# Q126(e) step 3: place, route and extract the synthesized TXFMA on ASAP7 (ORFS 1x platform).
# Everything here is open: ASAP7 (BSD-3-Clause) and OpenROAD.
set S $::env(HOME)/scratch-q126-e
set W $S/work
set P $S/orfs/flow/platforms/asap7
set NET [expr {[info exists ::env(NETLIST)] ? $::env(NETLIST) : "$W/syn/txfma_keep.v"}]
set TOP txfma_top
set OUT $W/pnr
file mkdir $OUT

read_lef $P/lef/asap7_tech_1x_201209.lef
foreach f [glob $P/lef/asap7sc7p5t_28_{L,R,SL}_1x_*.lef] { read_lef $f }

foreach f [glob $W/lib/asap7sc7p5t_*.lib] { read_liberty $f }

read_verilog $NET
link_design $TOP

# ASAP7's liberty time unit is 1 ps, so the SDC period is in ps: 1250 ps = 800 MHz,
# the clock the governor-free cards start at.
create_clock -name core_clock -period 1250 [get_ports clock]
# No IO delays: this block is extracted and powered, not closed against a parent.

source $P/setRC.tcl

initialize_floorplan -utilization 40 -aspect_ratio 1 -core_space 2 -site asap7sc7p5t
source $P/openRoad/make_tracks.tcl
place_pins -hor_layers M4 -ver_layers M5

puts "=== global placement"
global_placement -density 0.70 -pad_left 1 -pad_right 1
estimate_parasitics -placement
puts "=== repair_design"
set_dont_use {}
repair_design
puts "=== detailed placement"
detailed_placement
check_placement -verbose

puts "=== CTS"
set bufs {}
foreach b {BUFx2_ASAP7_75t_R BUFx3_ASAP7_75t_R BUFx4_ASAP7_75t_R BUFx5_ASAP7_75t_R} {
  if {[llength [get_lib_cells -quiet $b]] > 0} { lappend bufs $b }
}
puts "cts bufs: $bufs"
clock_tree_synthesis -buf_list $bufs -root_buf [lindex $bufs end] -sink_clustering_enable
set_propagated_clock [all_clocks]
estimate_parasitics -placement
detailed_placement
check_placement -verbose

puts "=== global route"
global_route -allow_congestion -congestion_iterations 50
estimate_parasitics -global_routing
report_wns
report_tns

puts "=== detailed route"
detailed_route -output_drc $OUT/route.drc -droute_end_iter 5 -verbose 1

puts "=== extraction"
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $P/rcx_patterns.rules -coupling_threshold 0.02
write_spef $OUT/txfma.spef
write_def $OUT/txfma.def
write_verilog $OUT/txfma_pnr.v

read_spef $OUT/txfma.spef
report_checks -path_delay max -digits 4 > $OUT/timing.rpt
report_design_area > $OUT/area.rpt
report_clock_skew > $OUT/skew.rpt
puts "=== done"
exit 0
