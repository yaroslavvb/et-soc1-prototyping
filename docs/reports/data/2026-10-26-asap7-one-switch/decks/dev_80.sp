* Q126(d) device check at 80 C, RVT, one fin
.include 7nm_TT_osdi.pm
.include cells_ng.cdl
.temp 80
Vdn dn 0 0.7
Vgn gn 0 0
N1 dn gn 0 0 nmos_rvt l=20n nfin=1
Vdnl dnl 0 0.05
N2 dnl gn 0 0 nmos_rvt l=20n nfin=1
Vsp sp 0 0.7
Vgp gp 0 0.7
N3 0 gp sp sp pmos_rvt l=20n nfin=1
.control
pre_osdi bsimcmg.osdi
dc Vgn 0 0.7 0.005
meas dc idsat_n FIND i(Vdn) AT=0.7
meas dc ioff_n  FIND i(Vdn) AT=0
meas dc idlin_n FIND i(Vdnl) AT=0.7
let ln = log10(abs(i(Vdn))+1e-18)
meas dc vg_1n  WHEN ln=-9 RISE=1
meas dc vg_10n WHEN ln=-8 RISE=1
dc Vgp 0.7 0 -0.005
meas dc idsat_p FIND i(Vsp) AT=0
meas dc ioff_p  FIND i(Vsp) AT=0.7
.endc
.end
