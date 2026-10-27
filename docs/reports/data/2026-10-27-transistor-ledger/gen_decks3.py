#!/usr/bin/env python3
"""Q128(d) decks: the gate charge of one minimum device, and how much of a
switch is the transistor and how much is the wire.

Q126(d) measured the energy of a whole cell per edge, by load.  It never
measured the piece underneath: how much charge a single minimum-size device's
gate takes, which is what "one transistor switching" means, and which part of
a real net's energy is that gate against the pin's own and the wire's.

Written to run in the same directory as Q126(d)'s decks (7nm_TT_osdi.pm,
bsimcmg.osdi, cells_ng.cdl must be beside the decks).

  gen_decks3.py <outdir> [extra_load_fF ...]
"""
import os
import sys

HEAD = ".include 7nm_TT_osdi.pm\n.include cells_ng.cdl\n"
OSDI = "pre_osdi bsimcmg.osdi\n"
VDDS = {"0p517": 0.517, "0p700": 0.700}

# A charge integrator: F copies the ammeter's current into a 1 F cap, so
# v(nq) is the coulombs that have passed.  Same device Q126(d) used.
def integ(name, vsrc):
    return f"F{name} 0 nq{name} {vsrc} 1\nCq{name} nq{name} 0 1\n"


def gate_charge(dev, vddname, drain, nfin=1):
    """Q_g of ONE FIN, driven 0 -> VDD by an ideal source through an ammeter.

    drain: 'gnd' (the device's drain held at 0) or 'vdd' (held at VDD).  The
    two bracket what a gate pin costs in a real cell, because the Miller term
    depends on where the drain sits when the gate moves.
    """
    vdd = VDDS[vddname]
    if dev == "n":
        # source and bulk at 0
        dnode = "0" if drain == "gnd" else "ndr"
        extra = "" if drain == "gnd" else f"Vdr ndr 0 {vdd}\n"
        inst = f"N1 {dnode} ng 0 0 nmos_rvt l=20n nfin={nfin}\n"
        drive = f"Vg ngs 0 PULSE(0 {vdd} 1n 5p 5p 2n 4n)\n"
    else:
        # source and bulk at VDD
        dnode = "0" if drain == "gnd" else "ndr"
        extra = f"Vsp nsp 0 {vdd}\n" + ("" if drain == "gnd" else f"Vdr ndr 0 {vdd}\n")
        inst = f"N1 {dnode} ng nsp nsp pmos_rvt l=20n nfin={nfin}\n"
        drive = f"Vg ngs 0 PULSE(0 {vdd} 1n 5p 5p 2n 4n)\n"
    return f"""* Q128(d) gate charge, {dev}mos RVT, {nfin} fin, drain={drain}, VDD={vdd} V
{HEAD}.temp 25
{drive}Vgm ngs ng 0
{extra}{inst}{integ('g', 'Vgm')}.ic v(nqg)=0
.control
{OSDI}tran 0.02p 5n
meas tran qg_lo FIND v(nqg) AT=0.95n
meas tran qg_hi FIND v(nqg) AT=2.95n
meas tran qg_end FIND v(nqg) AT=4.95n
.endc
.end
"""


CELL_PORTS = {            # .SUBCKT order, read from cells_ng.cdl
    "INVx1":   "{a} vd vs out",
    "NAND2x1": "{a} vdd vd vs out",
    "BUFx2":   "{a} vd vs out",
}


def inv_pin_charge(vddname, cell="INVx1"):
    """The charge a cell's INPUT PIN takes when it is driven 0 -> VDD, with the
    cell's own output unloaded.  This is what one unit of fanout costs the net
    that drives it, measured rather than taken from the liberty."""
    vdd = VDDS[vddname]
    ports = CELL_PORTS[cell].format(a="ng")
    return f"""* Q128(d) input-pin charge of {cell}, VDD={vdd} V, output unloaded
{HEAD}.temp 25
Vin  nin 0 PULSE(0 {vdd} 1n 5p 5p 2n 4n)
Vinm nin ng 0
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
X1 {ports} {cell}_ASAP7_75t_R
Cl out 0 0.001f
{integ('i', 'Vinm')}{integ('d', 'Vdut')}.ic v(nqi)=0 v(nqd)=0
.control
{OSDI}tran 0.02p 5n
meas tran qi_lo FIND v(nqi) AT=0.95n
meas tran qi_hi FIND v(nqi) AT=2.95n
meas tran qi_end FIND v(nqi) AT=4.95n
meas tran qd_lo FIND v(nqd) AT=0.95n
meas tran qd_hi FIND v(nqd) AT=2.95n
meas tran qd_end FIND v(nqd) AT=4.95n
.endc
.end
"""


def inv_energy(vddname, cl_fF, tr_ps=5, tag=""):
    """INVx1 rail energy per cycle at an arbitrary load -- the same deck shape
    Q126(d) used, re-run at the loads a real net in this design actually has."""
    vdd = VDDS[vddname]
    cl = f"{cl_fF:g}f" if cl_fF else "0.001f"
    return f"""* Q128(d) INVx1 energy, VDD={vdd} V, Cload={cl_fF:g} fF{tag}
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
Vin  nin 0 PULSE(0 {vdd} 1n {tr_ps}p {tr_ps}p 2n 4n)
X1 nin vd vs out INVx1_ASAP7_75t_R
Cl out 0 {cl}
{integ('d', 'Vdut')}{integ('s', 'Vssm')}.ic v(nqd)=0 v(nqs)=0
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


def inv_sc_sweep(vddname, cl_fF, tr_ps):
    """Short-circuit: the same inverter at one load, swept over input edge
    time, so the short-circuit share of a REAL net's energy can be read off
    rather than quoted from the 2 fF case."""
    return inv_energy(vddname, cl_fF, tr_ps, tag=f", tr={tr_ps} ps")


def fanout_chain(vddname, fo, wire_fF):
    """An INVx1 driving `fo` INVx1 loads plus a lumped wire capacitance: the
    real shape of a net in this design.  Splits the energy three ways -- the
    driver's own internal, the driven gates, the wire."""
    vdd = VDDS[vddname]
    # The driven cells hang off the IDEAL supply, not the ammetered one, so
    # Vdut sees the driver's own internal energy plus exactly the charge that
    # leaves it into the net -- the wire and the load gate pins -- and not the
    # load cells' own switching.
    loads = "".join(
        f"X{2+i} out vdd 0 o{i} INVx1_ASAP7_75t_R\nCo{i} o{i} 0 0.001f\n"
        for i in range(fo))
    return f"""* Q128(d) one net as built: INVx1 driving {fo} INVx1 pins + {wire_fF:g} fF of wire, VDD={vdd} V
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
Vin  nin 0 PULSE(0 {vdd} 1n 5p 5p 2n 4n)
X1 nin vd vs out INVx1_ASAP7_75t_R
Cw out 0 {wire_fF:g}f
{loads}{integ('d', 'Vdut')}.ic v(nqd)=0
.control
{OSDI}tran 0.02p 6n
meas tran qd0 FIND v(nqd) AT=0.95n
meas tran qd1 FIND v(nqd) AT=2.95n
meas tran qd2 FIND v(nqd) AT=4.95n
meas tran vo_lo FIND v(out) AT=2.9n
meas tran vo_hi FIND v(out) AT=4.9n
.endc
.end
"""


def main():
    out = sys.argv[1]
    wirec = float(sys.argv[2])          # the mean wire capacitance of a toggling net
    extra = [float(x) for x in sys.argv[3:]]
    os.makedirs(out, exist_ok=True)
    names = []

    def w(fn, text):
        open(os.path.join(out, fn), "w").write(text)
        names.append(fn)

    for v in VDDS:
        for dev in ("n", "p"):
            for drain in ("gnd", "vdd"):
                w(f"gq_{dev}_{drain}_{v}.sp", gate_charge(dev, v, drain))
        # a 3-fin device, to show the charge is per fin
        w(f"gq_n3_gnd_{v}.sp", gate_charge("n", v, "gnd", nfin=3))
        for cell in ("INVx1", "NAND2x1", "BUFx2"):
            w(f"pinq_{cell}_{v}.sp", inv_pin_charge(v, cell))

    # the loads a real net in this design has, measured in part 2
    for v in VDDS:
        for c in extra:
            w(f"en_INVx1_{v}_{str(c).replace('.', 'p')}.sp", inv_energy(v, c))

    # short-circuit share at a real net's load, by input edge time
    for v in VDDS:
        for tr in (1, 2, 5, 10, 20, 50, 100):
            c = extra[0] if extra else 2.0
            w(f"sc_INVx1_{v}_{tr}ps.sp", inv_sc_sweep(v, c, tr))

    # the net as built: driver + N gate pins + wire
    for v in VDDS:
        for fo in (0, 1, 2, 3, 4):
            w(f"net_{v}_fo{fo}.sp", fanout_chain(v, fo, wirec))

    runall = "#!/bin/bash\nset -u\n" + "".join(
        f'echo "### {n}"; ngspice -b {n} 2>&1\n' for n in sorted(names))
    open(os.path.join(out, "runall.sh"), "w").write(runall)
    print(f"{len(names)} decks in {out}")


if __name__ == "__main__":
    main()
