* Q126(d) FO4 delay, VDD=0.517 V (every stage loaded x4)
.include 7nm_TT_osdi.pm
.include cells_ng.cdl
.temp 25
Vdd vdd 0 0.517
Vin a 0 PULSE(0 0.517 1n 5p 5p 2n 4n)
Xd0 a   vdd 0 nd INVx1_ASAP7_75t_R
Xqd0 nd vdd 0 nqd0 INVx1_ASAP7_75t_R
Xqd1 nd vdd 0 nqd1 INVx1_ASAP7_75t_R
Xqd2 nd vdd 0 nqd2 INVx1_ASAP7_75t_R
Xd1 nd  vdd 0 ne INVx1_ASAP7_75t_R
Xqe0 ne vdd 0 nqe0 INVx1_ASAP7_75t_R
Xqe1 ne vdd 0 nqe1 INVx1_ASAP7_75t_R
Xqe2 ne vdd 0 nqe2 INVx1_ASAP7_75t_R
Xdut ne vdd 0 out INVx1_ASAP7_75t_R
Xl0 out vdd 0 nc0 INVx1_ASAP7_75t_R
Xl1 out vdd 0 nc1 INVx1_ASAP7_75t_R
Xl2 out vdd 0 nc2 INVx1_ASAP7_75t_R
Xl3 out vdd 0 nc3 INVx1_ASAP7_75t_R
.control
pre_osdi bsimcmg.osdi
tran 0.05p 5n
meas tran tin_f WHEN v(ne)=0.2585 FALL=1
meas tran tout_r WHEN v(out)=0.2585 RISE=1
meas tran tin_r WHEN v(ne)=0.2585 RISE=1
meas tran tout_f WHEN v(out)=0.2585 FALL=1
meas tran slew_r TRIG v(out) VAL=0.0517 RISE=1 TARG v(out) VAL=0.46530000000000005 RISE=1
meas tran slew_f TRIG v(out) VAL=0.46530000000000005 FALL=1 TARG v(out) VAL=0.0517 FALL=1
.endc
.end
