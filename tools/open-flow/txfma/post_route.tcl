# Q129(a): everything that stands on a FINISHED detailed route, without re-routing — read the
# routed DEF back, annotate a SPEF, write the SDF the glitch bench needs and the per-net
# capacitance table OpenSTA holds under that annotation.
#
#   DEF=.../txfma_routed.def SPEF=.../txfma_coupled.spef PNROUT=... \
#     openroad -no_init -exit tools/open-flow/txfma/post_route.tcl
#
# Detailed routing is three minutes of eight cores; this is seconds, so the SDF corner, the
# digits and the annotation can be changed without paying for the route again. It also makes
# the SDF reproducible on its own: the routed DEF and the SPEF are the only inputs.
proc env_or {name default} {
  if {[info exists ::env($name)] && $::env($name) ne ""} { return $::env($name) }
  return $default
}
set S [env_or SCRATCH "$::env(HOME)/scratch-q129-route"]
set W $S/work
set P [env_or PLATFORM /OpenROAD-flow-scripts/flow/platforms/asap7]
set LIBDIR [env_or LIBDIR $W/lib]
set OUT [env_or PNROUT $W/pnr-route]
set DEF [env_or DEF $OUT/txfma_routed.def]
set SPEF [env_or SPEF $OUT/txfma_coupled.spef]
set TOP txfma_top
file mkdir $OUT

read_lef $P/lef/asap7_tech_1x_201209.lef
foreach f [lsort [glob $P/lef/asap7sc7p5t_28_{L,R,SL}_1x_*.lef]] { read_lef $f }
foreach f [lsort [glob $LIBDIR/asap7sc7p5t_*.lib]] { read_liberty $f }
read_def $DEF
create_clock -name core_clock -period 1250 [get_ports clock]
set_propagated_clock [all_clocks]
source $P/setRC.tcl

proc dump_net_caps {path} {
  set corner ""
  foreach try {{sta::cmd_analysis_corner} {sta::cmd_corner}} {
    if {![catch {set corner [eval $try]}]} { break }
  }
  if {$corner eq ""} { error "no corner accessor" }
  set mm ""
  foreach try {{sta::MinMax_max} {sta::parse_min_max_flags max}} {
    if {![catch {set mm [eval $try]}]} { break }
  }
  set fh [open $path w]
  puts $fh "# net wire_cap pin_cap"
  set n 0
  foreach nn [get_nets *] {
    set wc 0 ; set pc 0
    catch {set wc [sta::Net_wire_capacitance $nn $corner $mm]}
    catch {set pc [sta::Net_pin_capacitance  $nn $corner $mm]}
    puts $fh "[get_full_name $nn] $wc $pc"
    incr n
  }
  close $fh
  return $n
}

read_spef $SPEF
puts "=== read $SPEF"
report_wns
report_tns
if {[catch {set n [dump_net_caps $OUT/net_cap_spef.txt]} msg]} {
  puts "net cap dump (spef) failed: $msg"
} else {
  puts "=== wrote net_cap_spef.txt, $n nets"
}

# ASAP7 RVT TT, liberty nominal 0.7 V / 25 C — the one corner this whole flow reads, and the
# corner the Q128 ledger's capacitances come from. The ledger prices ENERGY at the 0.517 V
# minion rail because capacitance is geometry; these DELAYS are 0.7 V delays and do not carry
# to 0.517 V. -include_typ fills the middle of each (min:typ:max) triple for Icarus.
foreach try [list \
    [list write_sdf -divider / -digits 4 -include_typ $OUT/txfma_routed.sdf] \
    [list write_sdf -divider / -digits 4 $OUT/txfma_routed.sdf]] {
  if {![catch {eval $try} msg]} { puts "=== wrote txfma_routed.sdf"; break } \
  else { puts "write_sdf attempt failed: $msg" }
}
catch {report_checks -path_delay max -digits 4 > $OUT/timing.rpt}
catch {report_clock_skew > $OUT/skew.rpt}
catch {report_power > $OUT/power_default.rpt}
catch {report_design_area}
puts "=== done"
exit 0
