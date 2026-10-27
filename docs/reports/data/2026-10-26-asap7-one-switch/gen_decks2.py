#!/usr/bin/env python3.12
"""Q126(d) fix-up decks: FAx1 energy with the CON load removed, and a probe of
what CON actually does while A toggles with B = CI = 0.

The committed FAx1 energy decks hang Ccout = 0.5 fF on the carry-out pin, which
`internal = rail - C_load*V^2` never subtracts, so any charge that reaches CON
is booked as FAx1's internal energy.  These decks measure the size of that.
"""
import os
import sys

HEAD = ".include 7nm_TT_osdi.pm\n.include cells_ng.cdl\n"
OSDI = "pre_osdi bsimcmg.osdi\n"
VDDS = {"0p517": 0.517, "0p700": 0.700}
LOADS = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]


def fa_energy(vddname, cl_fF, ccout_fF, tr_ps=5):
    vdd = VDDS[vddname]
    cl = f"{cl_fF}f" if cl_fF else "0.001f"
    cc = (f"Ccout cout 0 {ccout_fF}f\n" if ccout_fF else
          "Ccout cout 0 0.001f\n")
    return f"""* Q126(d) fix: FAx1 energy, VDD={vdd} V, Cload={cl_fF} fF, Ccout={ccout_fF} fF
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd  0
Vssm vs  0   0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 nin 0 0 cout out vd vs FAx1_ASAP7_75t_R
{cc}Cl out 0 {cl}
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
meas tran vo_lo FIND v(out) AT=2.9n
meas tran vo_hi FIND v(out) AT=4.9n
meas tran con_max MAX v(cout) FROM=0.95n TO=4.95n
meas tran con_min MIN v(cout) FROM=0.95n TO=4.95n
.endc
.end
"""


def fa_state(vddname, state, cl_fF=2.0, tr_ps=5):
    """FAx1 A->SN in each of the four (B, CI) hold states, so the per-state
    spread of a full adder's arc energy is measured, not assumed."""
    vdd = VDDS[vddname]
    b, ci = state
    bn = "vdd" if b else "0"
    cin = "vdd" if ci else "0"
    return f"""* Q126(d) fix: FAx1 A->SN with B={b} CI={ci}, VDD={vdd} V, Cload={cl_fF} fF
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd  0
Vssm vs  0   0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 nin {bn} {cin} cout out vd vs FAx1_ASAP7_75t_R
Ccout cout 0 0.001f
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
meas tran vo_lo FIND v(out) AT=2.9n
meas tran vo_hi FIND v(out) AT=4.9n
meas tran con_max MAX v(cout) FROM=0.95n TO=4.95n
meas tran con_min MIN v(cout) FROM=0.95n TO=4.95n
.endc
.end
"""


def nand_state(vddname, bval, cl_fF=2.0, tr_ps=5):
    """NAND2x1 A->Y with B high (the only state in which Y follows A)."""
    vdd = VDDS[vddname]
    bn = "vdd" if bval else "0"
    return f"""* Q126(d) fix: NAND2x1 A->Y with B={bval}, VDD={vdd} V, Cload={cl_fF} fF
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd  0
Vssm vs  0   0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 nin {bn} vd vs out NAND2x1_ASAP7_75t_R
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
meas tran vo_lo FIND v(out) AT=2.9n
meas tran vo_hi FIND v(out) AT=4.9n
.endc
.end
"""


def xor_deck(vddname, bval, cl_fF=2.0, tr_ps=5):
    """XOR2x1 A->Y in each B state: the cell whose when-averaging bug was
    worst among the hand-listed cells, measured both ways."""
    vdd = VDDS[vddname]
    bn = "vdd" if bval else "0"
    return f"""* Q126(d) fix: XOR2x1 A->Y with B={bval}, VDD={vdd} V, Cload={cl_fF} fF
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd  0
Vssm vs  0   0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 nin {bn} vd vs out XOR2x1_ASAP7_75t_R
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
meas tran vo_lo FIND v(out) AT=2.9n
meas tran vo_hi FIND v(out) AT=4.9n
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

    for v in VDDS:
        for cl in LOADS:
            tag = str(cl).replace(".", "p")
            w(f"fa_noc_{v}_{tag}.sp", fa_energy(v, cl, 0.0))
        # the committed deck's own configuration, re-run at the finer step so
        # the two are compared like for like
        w(f"fa_cc_{v}_2p0.sp", fa_energy(v, 2.0, 0.5))
        for b in (0, 1):
            for ci in (0, 1):
                w(f"fa_st_{v}_B{b}CI{ci}.sp", fa_state(v, (b, ci)))
        w(f"nand_B1_{v}.sp", nand_state(v, 1))
        for b in (0, 1):
            w(f"xor_B{b}_{v}.sp", xor_deck(v, b))

    with open(os.path.join(out, "runall2.sh"), "w") as fh:
        fh.write("cd ~/q126d/work/decks2\n")
        fh.write('NG="$HOME/q126d/ngspice/bin/ngspice"\n')
        fh.write("for f in " + " ".join(names) + "; do\n")
        fh.write('  echo "===DECK $f"\n')
        fh.write('  nice -n 15 "$NG" -b "$f" 2>&1\n')
        fh.write("done\n")
        fh.write('echo "===ALLDONE"\n')
    print(f"wrote {len(names)} decks to {out}")


if __name__ == "__main__":
    main()
