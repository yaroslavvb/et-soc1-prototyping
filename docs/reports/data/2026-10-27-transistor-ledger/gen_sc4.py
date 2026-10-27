#!/usr/bin/env python3
"""Q128(d) amendment: bracket the short-circuit minimum at the minion rail.

The committed sweep (gen_decks3.py, 1..100 ps) is still falling at its slowest
edge at 0.517 V, so "at most 2.5%" was the spread over the sampled range and
not a bound.  This extends the sweep to 2 ns of input edge, on a window whose
LENGTH IS THE SAME FOR EVERY EDGE (0.95 ns -> 14.95 ns), and measures the
inverter's static leakage in both input states so the state-duration shift
that a slower edge causes can be subtracted instead of assumed small.

  gen_sc4.py <outdir>
"""
import os
import sys

HEAD = ".include 7nm_TT_osdi.pm\n.include cells_ng.cdl\n"
OSDI = "pre_osdi bsimcmg.osdi\n"
VDDS = {"0p517": 0.517, "0p700": 0.700}
CL_FF = 2.105          # the load the committed sweep used: an average toggling net
T0_NS = 0.95           # start of the measurement window
T1_NS = 14.95          # end of it -- the same for every deck
TD_NS = 1.0            # the rise starts here
PW_NS = 6.0            # time at VDD after the rise completes


def sc_deck(vddname, tr_ps):
    """INVx1 at a real net's load, one input pulse, fixed measurement window."""
    vdd = VDDS[vddname]
    t = tr_ps / 1000.0                      # ns
    fall_end = TD_NS + 2 * t + PW_NS
    assert fall_end < T1_NS - 1.0, (tr_ps, fall_end)
    return f"""* Q128(d) short circuit, VDD={vdd} V, Cload={CL_FF} fF, tr=tf={tr_ps} ps, fixed window
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
Vin  nin 0 PULSE(0 {vdd} {TD_NS}n {t}n {t}n {PW_NS}n 100n)
X1 nin vd vs out INVx1_ASAP7_75t_R
Cl out 0 {CL_FF}f
Fd 0 nqd Vdut 1
Cqd nqd 0 1
.ic v(nqd)=0
.control
{OSDI}tran 0.02p {T1_NS + 0.05}n
meas tran qd0 FIND v(nqd) AT={T0_NS}n
meas tran qdf FIND v(nqd) AT={fall_end - 0.01}n
meas tran qd2 FIND v(nqd) AT={T1_NS}n
.endc
.end
"""


def leak_deck(vddname, state):
    """The same inverter with its input held, over the same window: the static
    charge the rail delivers per nanosecond in each state."""
    vdd = VDDS[vddname]
    vin = 0.0 if state == "lo" else vdd
    return f"""* Q128(d) static leakage, VDD={vdd} V, Cload={CL_FF} fF, input held {state}
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vdut vdd vd 0
Vssm vs  0  0
Vin  nin 0 {vin}
X1 nin vd vs out INVx1_ASAP7_75t_R
Cl out 0 {CL_FF}f
Fd 0 nqd Vdut 1
Cqd nqd 0 1
.ic v(nqd)=0
.control
{OSDI}tran 0.02p {T1_NS + 0.05}n
meas tran qd0 FIND v(nqd) AT={T0_NS}n
meas tran qd2 FIND v(nqd) AT={T1_NS}n
.endc
.end
"""


EDGES_PS = (5, 50, 100, 200, 300, 500, 700, 1000, 1500, 2000)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    names = []

    def w(fn, text):
        open(os.path.join(out, fn), "w").write(text)
        names.append(fn)

    for v in VDDS:
        for tr in EDGES_PS:
            w(f"sc4_{v}_{tr}ps.sp", sc_deck(v, tr))
        for st in ("lo", "hi"):
            w(f"leak_{v}_{st}.sp", leak_deck(v, st))

    runall = "#!/bin/bash\nset -u\n" + "".join(
        f'echo "### {n}"; nice -n 19 "$NG" -b {n} 2>&1\n' for n in sorted(names))
    open(os.path.join(out, "runall.sh"), "w").write(runall)
    print(f"{len(names)} decks in {out}")


if __name__ == "__main__":
    main()
