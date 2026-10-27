* Q126(d) fix: NAND2x1 A->Y with B=1, VDD=0.7 V, Cload=2.0 fF
.include 7nm_TT_osdi.pm
.include cells_ng.cdl
.temp 25
Vdd  vdd 0 0.7
Vdut vdd vd  0
Vssm vs  0   0
Vin  nin 0 PULSE(0 0.7 1n 5p 5p 2n 4n)
X1 nin vdd vd vs out NAND2x1_ASAP7_75t_R
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
meas tran vo_lo FIND v(out) AT=2.9n
meas tran vo_hi FIND v(out) AT=4.9n
.endc
.end
