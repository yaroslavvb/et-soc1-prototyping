#!/usr/bin/env python3
"""Q128(d) amendment, part 2: the fast end of the sweep on the same window,
plus the output edge this inverter actually produces into a real net -- which
is what says whether any part of the sweep describes this design.

  gen_sc5.py <outdir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_sc4 import HEAD, OSDI, VDDS, CL_FF, T0_NS, T1_NS, TD_NS, PW_NS, sc_deck  # noqa: E402

EDGES_PS = (1, 2, 10, 20)


def slew_deck(vddname, tr_ps=5):
    """The 20-80% output transition of an INVx1 into the 2.105 fF a real net
    carries: the input edge the NEXT gate sees."""
    vdd = VDDS[vddname]
    t = tr_ps / 1000.0
    lo, hi = 0.2 * vdd, 0.8 * vdd
    return f"""* Q128(d) output slew of INVx1 into {CL_FF} fF, VDD={vdd} V, input edge {tr_ps} ps
{HEAD}.temp 25
Vdd  vdd 0 {vdd}
Vssm vs  0  0
Vin  nin 0 PULSE(0 {vdd} {TD_NS}n {t}n {t}n {PW_NS}n 100n)
X1 nin vdd vs out INVx1_ASAP7_75t_R
Cl out 0 {CL_FF}f
.control
{OSDI}tran 0.02p {T1_NS + 0.05}n
meas tran tf80 WHEN v(out)={hi} FALL=1
meas tran tf20 WHEN v(out)={lo} FALL=1
meas tran tr20 WHEN v(out)={lo} RISE=1
meas tran tr80 WHEN v(out)={hi} RISE=1
.endc
.end
"""


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
        w(f"slew_{v}.sp", slew_deck(v))

    runall = "#!/bin/bash\nset -u\n" + "".join(
        f'echo "### {n}"; nice -n 19 "$NG" -b {n} 2>&1\n' for n in sorted(names))
    open(os.path.join(out, "runall5.sh"), "w").write(runall)
    print(f"{len(names)} decks in {out}")


if __name__ == "__main__":
    main()
