* Q126(d) short circuit vs input edge: tr=10 ps, VDD=0.517 V
.include 7nm_TT_osdi.pm
.include cells_ng.cdl
.temp 25
Vdd  vdd 0 0.517
Vdut vdd vd 0
Vssm vs  0  0
Vin  nin 0 PULSE(0 0.517 1n 10p 10p 2n 4n)
X1 nin vd vs out INVx1_ASAP7_75t_R
Cl out 0 2.0f
Fqd 0 nqd Vdut 1
Cqd nqd 0 1
Fqs 0 nqs Vssm 1
Cqs nqs 0 1
.ic v(nqd)=0 v(nqs)=0
.control
pre_osdi bsimcmg.osdi
tran 0.02p 5n
meas tran qd0 FIND v(nqd) AT=0.95n
meas tran qd1 FIND v(nqd) AT=2.95n
meas tran qd2 FIND v(nqd) AT=4.95n
meas tran qs0 FIND v(nqs) AT=0.95n
meas tran qs1 FIND v(nqs) AT=2.95n
meas tran qs2 FIND v(nqs) AT=4.95n
.endc
.end
