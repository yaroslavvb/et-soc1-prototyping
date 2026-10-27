#!/usr/bin/env python3.12
"""Q126(d) part 2: generate the ngspice decks for one switch in ASAP7 SPICE.

Writes a set of self-contained decks into <outdir>.  Each deck loads the
BSIM-CMG OSDI library, includes ASAP7's converted model card and the kit's
own CDL cell netlists, and prints its measurements with `meas`.

Usage: python3.12 -I gen_decks.py <outdir>
"""
import os
import sys

HEAD = """.include 7nm_TT_osdi.pm
.include cells_ng.cdl
"""
OSDI = "pre_osdi bsimcmg.osdi\n"

VDDS = {"0p517": 0.517, "0p700": 0.700}
LOADS_fF = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
EDGES_ps = [1, 2, 5, 10, 20, 50, 100, 200]
TEMPS = [25, 80]

# cell -> (subckt, port order, input pin, output pin, how to tie the rest,
#          extra netlist lines)
CELLS = {
    "INVx1": ("INVx1_ASAP7_75t_R", "A VDD VSS Y", "A", "Y", {}, ""),
    "NAND2x1": ("NAND2x1_ASAP7_75t_R", "A B VDD VSS Y", "A", "Y",
                {"B": "vdd"}, ""),
    # A toggles with B = CI = 0, so SN follows A and CON stays low.
    "FAx1": ("FAx1_ASAP7_75t_R", "A B CI CON SN VDD VSS", "A", "SN",
             {"B": "0", "CI": "0", "CON": "cout"}, "Ccout cout 0 0.5f\n"),
}


def ports(order, mapping):
    return " ".join(mapping[p] for p in order.split())


def energy_deck(cell, vddname, cl_fF, tr_ps=5):
    sub, order, ipin, opin, ties, extra = CELLS[cell]
    vdd = VDDS[vddname]
    # the DUT's rails go through 0 V ammeters so its charge can be integrated
    m = {"VDD": "vd", "VSS": "vs"}
    for p in order.split():
        if p in ("VDD", "VSS"):
            continue
        m[p] = "nin" if p == ipin else "out" if p == opin else ties[p]
    cl = f"{cl_fF}f" if cl_fF else "0.001f"
    return f"""* Q126(d) energy per edge: {cell}, VDD={vdd} V, Cload={cl_fF} fF, tr={tr_ps} ps
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd  0
Vssm vs  0   0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 {ports(order, m)} {sub}
{extra}Cl out 0 {cl}
Fqd 0 nqd Vdut 1
Cqd nqd 0 1
Fqs 0 nqs Vssm 1
Cqs nqs 0 1
.ic v(nqd)=0 v(nqs)=0
.control
{OSDI}tran 0.05p 5n
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
"""


def delay_deck(vddname, tr_ps=5, fanout=4):
    """FO4: a chain in which EVERY stage carries a fanout-of-4 load, so the
    DUT sees the input slew a real FO4 chain settles at, not a fast edge."""
    vdd = VDDS[vddname]
    # each driving stage also carries fanout-1 dummy copies, so its output
    # slew is the FO4 slew
    def dummies(node, tag):
        return "\n".join(f"Xq{tag}{i} {node} vdd 0 nq{tag}{i} "
                         f"INVx1_ASAP7_75t_R" for i in range(fanout - 1))
    loads = "\n".join(
        f"Xl{i} out vdd 0 nc{i} INVx1_ASAP7_75t_R" for i in range(fanout))
    return f"""* Q126(d) FO{fanout} delay, VDD={vdd} V (every stage loaded x{fanout})
{HEAD}.temp 25
Vdd vdd 0 {vdd}
Vin a 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
Xd0 a   vdd 0 nd INVx1_ASAP7_75t_R
{dummies("nd", "d")}
Xd1 nd  vdd 0 ne INVx1_ASAP7_75t_R
{dummies("ne", "e")}
Xdut ne vdd 0 out INVx1_ASAP7_75t_R
{loads}
.control
{OSDI}tran 0.05p 5n
meas tran tin_f WHEN v(ne)={vdd/2} FALL=1
meas tran tout_r WHEN v(out)={vdd/2} RISE=1
meas tran tin_r WHEN v(ne)={vdd/2} RISE=1
meas tran tout_f WHEN v(out)={vdd/2} FALL=1
meas tran slew_r TRIG v(out) VAL={0.1*vdd} RISE=1 TARG v(out) VAL={0.9*vdd} RISE=1
meas tran slew_f TRIG v(out) VAL={0.9*vdd} FALL=1 TARG v(out) VAL={0.1*vdd} FALL=1
.endc
.end
"""


def shortcircuit_deck(vddname, tr_ps, cl_fF=2.0):
    """INVx1 driven by an ideal edge of a stated length; the VSS charge during
    the OUTPUT RISE is short-circuit charge (the pull-down should be off)."""
    vdd = VDDS[vddname]
    return f"""* Q126(d) short circuit vs input edge: tr={tr_ps} ps, VDD={vdd} V
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 nin vd vs out INVx1_ASAP7_75t_R
Cl out 0 {cl_fF}f
Fqd 0 nqd Vdut 1
Cqd nqd 0 1
Fqs 0 nqs Vssm 1
Cqs nqs 0 1
.ic v(nqd)=0 v(nqs)=0
.control
{OSDI}tran 0.02p 5n
meas tran qd0 FIND v(nqd) AT=0.95n
meas tran qd1 FIND v(nqd) AT=2.95n
meas tran qd2 FIND v(nqd) AT=4.95n
meas tran qs0 FIND v(nqs) AT=0.95n
meas tran qs1 FIND v(nqs) AT=2.95n
meas tran qs2 FIND v(nqs) AT=4.95n
.endc
.end
"""


def device_deck(temp):
    """Id-Vg for one fin of each RVT device: Idsat, Ioff, SS and DIBL,
    against the ASAP7 paper's Tables 3 and 4."""
    return f"""* Q126(d) device check at {temp} C, RVT, one fin
{HEAD}.temp {temp}
Vdn dn 0 0.7
Vgn gn 0 0
N1 dn gn 0 0 nmos_rvt l=20n nfin=1
Vdnl dnl 0 0.05
N2 dnl gn 0 0 nmos_rvt l=20n nfin=1
Vsp sp 0 0.7
Vgp gp 0 0.7
N3 0 gp sp sp pmos_rvt l=20n nfin=1
.control
{OSDI}dc Vgn 0 0.7 0.005
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
"""


def leak_deck(temp, vddname):
    """Whole-cell leakage for INVx1 in both states, against the liberty's
    51.2 pW (state-averaged, VDD, 0.7 V, 25 C)."""
    vdd = VDDS[vddname]
    return f"""* Q126(d) leakage, INVx1 both states, {temp} C, VDD={vdd} V
{HEAD}.temp {temp}
Vdd vdd 0 {vdd}
VdA vdd vda 0
VdB vdd vdb 0
VinA a 0 0
VinB b 0 {vdd}
XA a vda 0 ya INVx1_ASAP7_75t_R
XB b vdb 0 yb INVx1_ASAP7_75t_R
* one fin of each device, for the per-device figure
Vdn dn 0 {vdd}
N1 dn 0 0 0 nmos_rvt l=20n nfin=1
Vsp sp 0 {vdd}
N2 0 sp sp sp pmos_rvt l=20n nfin=1
.control
{OSDI}op
print i(VdA) i(VdB) i(Vdn) i(Vsp)
.endc
.end
"""


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    names = []

    def w(name, text):
        with open(os.path.join(out, name), "w") as fh:
            fh.write(text)
        names.append(name)

    for t in TEMPS:
        w(f"dev_{t}.sp", device_deck(t))
    for v in VDDS:
        w(f"fo4_{v}.sp", delay_deck(v))
        for t in TEMPS:
            w(f"leak_{t}_{v}.sp", leak_deck(t, v))
        for cell in CELLS:
            for cl in LOADS_fF:
                w(f"en_{cell}_{v}_{str(cl).replace('.', 'p')}.sp",
                  energy_deck(cell, v, cl))
        for tr in EDGES_ps:
            w(f"sc_{v}_{tr}.sp", shortcircuit_deck(v, tr))

    with open(os.path.join(out, "runall.sh"), "w") as fh:
        fh.write("cd ~/q126d/work/decks\n")
        fh.write('NG="$HOME/q126d/ngspice/bin/ngspice"\n')
        fh.write("for f in " + " ".join(names) + "; do\n")
        fh.write('  echo "===DECK $f"\n')
        fh.write('  nice -n 15 "$NG" -b "$f" 2>&1\n')
        fh.write("done\n")
        fh.write('echo "===ALLDONE"\n')
    print(f"wrote {len(names)} decks to {out}")


if __name__ == "__main__":
    main()
