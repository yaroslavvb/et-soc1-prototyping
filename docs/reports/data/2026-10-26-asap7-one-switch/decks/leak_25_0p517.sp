* Q126(d) leakage, INVx1 both states, 25 C, VDD=0.517 V
.include 7nm_TT_osdi.pm
.include cells_ng.cdl
.temp 25
Vdd vdd 0 0.517
VdA vdd vda 0
VdB vdd vdb 0
VinA a 0 0
VinB b 0 0.517
XA a vda 0 ya INVx1_ASAP7_75t_R
XB b vdb 0 yb INVx1_ASAP7_75t_R
* one fin of each device, for the per-device figure
Vdn dn 0 0.517
N1 dn 0 0 0 nmos_rvt l=20n nfin=1
Vsp sp 0 0.517
N2 0 sp sp sp pmos_rvt l=20n nfin=1
.control
pre_osdi bsimcmg.osdi
op
print i(VdA) i(VdB) i(Vdn) i(Vsp)
.endc
.end
