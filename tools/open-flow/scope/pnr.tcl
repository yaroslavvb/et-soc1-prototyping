# Q129: place, route and extract the synthesized q129_scope_top on ASAP7, with OpenROAD.
# Derived from tools/open-flow/txfma/pnr.tcl - same floorplan, CTS and global-route recipe, so
# the lane's transport and the lane's arithmetic are extracted on identical terms.
# Everything open: ASAP7 (BSD-3-Clause), the ORFS asap7 platform (already at 1x), OpenROAD.
#   SCRATCH=... openroad -no_init -exit tools/open-flow/scope/pnr.tcl
set S [expr {[info exists ::env(SCRATCH)] ? $::env(SCRATCH) : "$::env(HOME)/scratch-q129-scope"}]
set W $S/work-scope
set P $S/orfs/flow/platforms/asap7
set NET [expr {[info exists ::env(NETLIST)] ? $::env(NETLIST) : "$W/syn/scope_mixed.v"}]
set UTIL [expr {[info exists ::env(UTIL)] ? $::env(UTIL) : 30}]
set DENS [expr {[info exists ::env(DENS)] ? $::env(DENS) : 0.55}]
set TOP q129_scope_top
set OUT [expr {[info exists ::env(PNROUT)] ? $::env(PNROUT) : "$W/pnr"}]
file mkdir $OUT

read_lef $P/lef/asap7_tech_1x_201209.lef
foreach f [glob $P/lef/asap7sc7p5t_28_{L,R,SL}_1x_*.lef] { read_lef $f }
foreach f [glob $W/lib/asap7sc7p5t_*.lib] { read_liberty $f }
read_verilog $NET
link_design $TOP

# ASAP7's liberty time unit is 1 ps, so the SDC period is in ps: 1250 ps = 800 MHz,
# the clock the governor-free cards start at. No IO delays: this block is extracted and
# powered, not closed against a parent.
create_clock -name core_clock -period 1250 [get_ports clock]
source $P/setRC.tcl

initialize_floorplan -utilization $UTIL -aspect_ratio 1 -core_space 2 -site asap7sc7p5t
source $P/openRoad/make_tracks.tcl
place_pins -hor_layers M4 -ver_layers M5

puts "=== global placement"
global_placement -density $DENS -pad_left 1 -pad_right 1
estimate_parasitics -placement
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
# Signal M2-M7, clock M4-M7. NOTE the detailed router below is given M2-M9, which is NOT the
# same range: holding both to M2-M7 only trades one failure for another, because the global
# route emits an M8 guide for an I/O net anyway and TritonRoute then stops with DRT-0155
# ("Guide in net in_data[48] uses layer M8 ... outside the allowed routing range"). Five
# configurations of this pair were tried; POWER.md § blockers has the table of ten.
set_routing_layers -signal M2-M7 -clock M4-M7
global_route -congestion_iterations 100
estimate_parasitics -global_routing
report_wns
report_tns
write_verilog $OUT/scope_pnr.v
write_def $OUT/scope_placed.def

# Per-net capacitance as OpenSTA holds it after the global-route estimate. This is the fallback
# the power model uses if detailed routing does not close (a Steiner estimate, no coupling);
# the SPEF below is the real thing. The accessor is a SWIG wrapper and its name has moved
# between OpenSTA versions, so every call is guarded.
proc dump_net_caps {path} {
  set corner [sta::cmd_corner]
  set mm ""
  foreach try {{sta::MinMax_max} {sta::parse_min_max_flags max}} {
    if {![catch {set mm [eval $try]}]} { break }
  }
  set fh [open $path w]
  puts $fh "# net wire_cap pin_cap"
  set n_ok 0
  foreach n [get_nets *] {
    set wc 0 ; set pc 0
    catch {set wc [sta::Net_wire_capacitance $n $corner $mm]}
    catch {set pc [sta::Net_pin_capacitance  $n $corner $mm]}
    puts $fh "[get_full_name $n] $wc $pc"
    incr n_ok
  }
  close $fh
  return $n_ok
}
if {[catch {set n [dump_net_caps $OUT/net_cap_globalroute.txt]} msg]} {
  puts "net cap dump failed: $msg"
} else {
  puts "=== wrote net_cap_globalroute.txt, $n nets"
}

puts "=== detailed route"
set drok 1
if {[catch {detailed_route -output_drc $OUT/route.drc -droute_end_iter 10 \
              -bottom_routing_layer M2 -top_routing_layer M9 -verbose 1} msg]} {
  puts "DETAILED ROUTE FAILED: $msg"
  set drok 0
}

if {$drok} {
  puts "=== extraction"
  define_process_corner -ext_model_index 0 X
  extract_parasitics -ext_model_file $P/rcx_patterns.rules -coupling_threshold 0.02
  write_spef $OUT/scope.spef
  write_def $OUT/scope_routed.def
  read_spef $OUT/scope.spef
  catch {dump_net_caps $OUT/net_cap_spef.txt}
}
catch {write_sdf -divider / -digits 4 $OUT/scope.sdf}
catch {report_checks -path_delay max -digits 4 > $OUT/timing.rpt}
catch {report_design_area}
catch {report_clock_skew > $OUT/skew.rpt}
catch {report_power > $OUT/power_default.rpt}
puts "=== done drok=$drok"
exit 0
