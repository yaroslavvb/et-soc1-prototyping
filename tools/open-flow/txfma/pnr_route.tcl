# Q129(a): the same place-and-route as pnr.tcl, carried through DETAILED routing, OpenRCX
# extraction with coupling capacitance, SPEF and SDF. Run inside the ORFS container, whose
# OpenROAD is current; the 2022 conda OpenROAD pnr.tcl was written for stops at DRT-0255 on the
# top-level port nets (docs/reports/data/2026-10-26-open-netlist/POWER.md, ten configurations).
#
#   openroad -no_init -exit tools/open-flow/txfma/pnr_route.tcl
#
# Environment (all optional except NETLIST):
#   NETLIST   the synthesized netlist to route            (default $W/syn/txfma_mixed.v)
#   PLATFORM  the ORFS asap7 platform directory           (default the container's)
#   LIBDIR    uncompressed liberty for this corner        (default $W/lib)
#   PNROUT    output directory                            (default $W/pnr-route)
#   UTIL DENS core utilisation % and placement density    (default 30 / 0.55)
#   PINHOR PINVER   pin layers                            (default M4 / M5)
#   SIGLAYERS CLKLAYERS  routing ranges for GRT           (default M2-M7 / M4-M7)
#   DRT_BOT DRT_TOP      the detailed router's range      (default M2 / M9)
#   DRT_ITERS end iteration for the detailed router       (default 10)
#   COUPLING  OpenRCX coupling threshold, fF              (default 0.02)
#   CORE_SPACE core space in um                            (default 2)
#
# Everything the published run did is kept identical except the tool: same platform sha, same
# liberty, same SDC, same utilisation, same pin layers, same layer ranges. The whole flow is
# re-run end to end (floorplan -> placement -> CTS -> GRT -> DRT) in ONE tool, so the
# global-route estimate this script dumps is the right "before" for its own extraction; the
# 2022 run's estimate is in the Q126(e) directory for the cross-tool comparison.

proc env_or {name default} {
  if {[info exists ::env($name)] && $::env($name) ne ""} { return $::env($name) }
  return $default
}

set S [env_or SCRATCH "$::env(HOME)/scratch-q129-route"]
set W $S/work
set P [env_or PLATFORM /OpenROAD-flow-scripts/flow/platforms/asap7]
set LIBDIR [env_or LIBDIR $W/lib]
set NET [env_or NETLIST $W/syn/txfma_mixed.v]
set UTIL [env_or UTIL 30]
set DENS [env_or DENS 0.55]
set PINHOR [env_or PINHOR M4]
set PINVER [env_or PINVER M5]
set SIGLAYERS [env_or SIGLAYERS M2-M7]
set CLKLAYERS [env_or CLKLAYERS M4-M7]
set DRT_BOT [env_or DRT_BOT M2]
set DRT_TOP [env_or DRT_TOP M9]
set DRT_ITERS [env_or DRT_ITERS 10]
set COUPLING [env_or COUPLING 0.02]
set CORE_SPACE [env_or CORE_SPACE 2]
set TOP txfma_top
set OUT [env_or PNROUT $W/pnr-route]
file mkdir $OUT

puts "=== Q129(a) route: netlist $NET util $UTIL pins $PINHOR/$PINVER grt $SIGLAYERS/$CLKLAYERS drt $DRT_BOT-$DRT_TOP"
puts "=== openroad [exec openroad -version] platform $P"

read_lef $P/lef/asap7_tech_1x_201209.lef
foreach f [lsort [glob $P/lef/asap7sc7p5t_28_{L,R,SL}_1x_*.lef]] { read_lef $f }
foreach f [lsort [glob $LIBDIR/asap7sc7p5t_*.lib]] { read_liberty $f }
read_verilog $NET
link_design $TOP

# ASAP7's liberty time unit is 1 ps, so the SDC period is in ps: 1250 ps = 800 MHz. The placed
# design misses it by about 2x (POWER.md); nothing here tries to fix that, because the question
# is energy per toggle. The SDC is kept identical so the CTS answer is comparable.
create_clock -name core_clock -period 1250 [get_ports clock]
source $P/setRC.tcl

initialize_floorplan -utilization $UTIL -aspect_ratio 1 -core_space $CORE_SPACE -site asap7sc7p5t
source $P/openRoad/make_tracks.tcl
place_pins -hor_layers $PINHOR -ver_layers $PINVER

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

# Per-net capacitance as OpenSTA holds it. Called twice: once on the global-route Steiner
# estimate (the "before"), once on the SPEF (the "after"). The accessor is a SWIG wrapper whose
# name has moved between OpenSTA versions, so every call is guarded.
proc dump_net_caps {path} {
  # OpenSTA renamed the current-corner accessor: `sta::cmd_corner` in the 2022 build pnr.tcl
  # used, `sta::cmd_analysis_corner` in the current one. Try both, newest first.
  set corner ""
  foreach try {{sta::cmd_analysis_corner} {sta::cmd_corner}} {
    if {![catch {set corner [eval $try]}]} { break }
  }
  if {$corner eq ""} { error "no corner accessor (sta::cmd_analysis_corner/cmd_corner)" }
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

puts "=== global route"
set_routing_layers -signal $SIGLAYERS -clock $CLKLAYERS
global_route -congestion_iterations 100
# -spef_file writes the Steiner estimate itself as SPEF, which is the right "before" for the
# extraction below: the same parser (spef_caps.py) reads both, so ground-cap against ground-cap
# and the coupling column is the only thing that appears out of nowhere. The 2022 build pnr.tcl
# ran had no such flag, which is why that run only has an OpenSTA net-cap table.
if {[catch {estimate_parasitics -global_routing -spef_file $OUT/txfma_gr.spef} msg]} {
  puts "estimate_parasitics -spef_file failed ($msg); falling back to no SPEF"
  estimate_parasitics -global_routing
} else {
  puts "=== wrote txfma_gr.spef (global-route Steiner estimate)"
}
report_wns
report_tns
write_verilog $OUT/txfma_pnr.v
write_def $OUT/txfma_placed.def
if {[catch {set n [dump_net_caps $OUT/net_cap_globalroute.txt]} msg]} {
  puts "net cap dump (global route) failed: $msg"
} else {
  puts "=== wrote net_cap_globalroute.txt, $n nets"
}
if {[string match -nocase "grt*" [env_or STOP_AFTER ""]]} {
  puts "=== STOP_AFTER=grt, stopping before the detailed route"
  exit 0
}

puts "=== detailed route"
set drok 1
set drargs [list -output_drc $OUT/route.drc -droute_end_iter $DRT_ITERS -verbose 1]
# The detailed router gets its own, WIDER range: the published configuration gave GRT M2-M7 and
# DRT M2-M9 (POWER.md's table, row 10). Current OpenROAD rejects detailed_route's own
# -bottom/-top_routing_layer flags (DRT-0509 "deprecated. Use set_routing_layers"), so the
# range is set here instead; the clock range is left where CTS and GRT had it.
set_routing_layers -signal "$DRT_BOT-$DRT_TOP" -clock $CLKLAYERS
if {[catch {detailed_route {*}$drargs} msg]} {
  puts "DETAILED ROUTE FAILED: $msg"
  set drok 0
}
puts "=== detailed route drok=$drok"

if {$drok} {
  write_def $OUT/txfma_routed.def
  catch {write_verilog $OUT/txfma_routed.v}

  puts "=== extraction, coupling threshold $COUPLING fF"
  define_process_corner -ext_model_index 0 X
  extract_parasitics -ext_model_file $P/rcx_patterns.rules -coupling_threshold $COUPLING
  write_spef $OUT/txfma_coupled.spef
  puts "=== wrote txfma_coupled.spef"

  # Read it back so timing, the SDF and the net-cap table all stand on the extraction.
  read_spef $OUT/txfma_coupled.spef
  catch {dump_net_caps $OUT/net_cap_spef.txt}
  catch {report_wns}
  catch {report_tns}

  # The SDF for the glitch agent, at the one corner this flow reads: ASAP7 RVT TT, liberty
  # nominal 0.7 V / 25 C. The 0.517 V rail the ledger prices energy at is NOT a corner of this
  # liberty and the delays here are not transferable to it (POWER.md says the same of pnr.tcl's).
  # -include_typ fills the middle of every (min:typ:max) triple, which is what the help says
  # some Verilog simulators need; Icarus is the one waiting for this file.
  foreach try [list \
      [list write_sdf -divider / -digits 4 -include_typ $OUT/txfma_routed.sdf] \
      [list write_sdf -divider / -digits 4 $OUT/txfma_routed.sdf]] {
    if {![catch {eval $try} msg]} { puts "=== wrote txfma_routed.sdf"; break } \
    else { puts "write_sdf attempt failed: $msg" }
  }
} else {
  # Still leave an SDF on the global-route estimate, so a failed detailed route does not also
  # cost the glitch bench its input.
  catch {write_sdf -divider / -digits 4 $OUT/txfma_gr.sdf}
}

catch {report_checks -path_delay max -digits 4 > $OUT/timing.rpt}
catch {report_design_area}
catch {report_clock_skew > $OUT/skew.rpt}
catch {report_power > $OUT/power_default.rpt}
catch {report_wire_length > $OUT/wirelength.rpt}
puts "=== done drok=$drok"
exit 0
