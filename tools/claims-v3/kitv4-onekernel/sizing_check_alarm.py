#!/usr/bin/env python3
"""Kit v4's one-kernel option, dated note 1 (README.md.dated-note-1.md): the one kernel's wall time when the clock is lower than
the governor's 600 MHz boot point, against the host's 6 s launch timeout, and its wall at the cap with a first in-kernel
heartbeat at 0 s. It imports onekernel.py unchanged (its sizing, CPO and HOST_TIMEOUT_S) and touches no card.

    python3 -I -B sizing_check_alarm.py > sizing-check-alarm.txt

The clocks below the boot point are card 0's PMIC alarm, as the lab measured it (docs/findings/14-card-behaviour.md lines 238
and 466, E84): a 300 MHz safe state; over a sustained run the work samples sat 31-32% at 300 MHz, 32-34% at 600, 25% at 700
and 10-11% at 800 (a sampled 551 MHz), and the kernel's own effective clock was 0.475-0.479 GHz.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import onekernel as OK  # noqa: E402

MIX = {300: (0.31, 0.32), 600: (0.32, 0.34), 700: (0.25, 0.25), 800: (0.10, 0.11)}   # findings 14 line 466


def main():
    out = {"host_timeout_s": OK.HOST_TIMEOUT_S, "floor_mhz_as_sized": OK.FLOOR_MHZ, "t600_s": OK.T600_S, "types": {}}
    mid = {f: 0.5 * (a + b) for f, (a, b) in MIX.items()}
    s = sum(mid.values())
    mix_mhz = sum(f * w for f, w in mid.items()) / s
    out["E84_sampled_mix_mhz"] = round(mix_mhz, 1)
    for typ in ("fp32", "fp16", "int8"):
        n = OK.iters_for(typ)
        cyc = n * OK.CPO[typ]
        rec = {"iters": n, "G_cycles": round(cyc / 1e9, 4),
               "wall_at_cap_s": {f"first_beat_{b:.1f}_s": round(OK.wall_at(typ, n, first_beat_s=b), 3) for b in (0.0, 0.5, 1.0)},
               "wall_at_fixed_clock_s": {}}
        for label, mhz in (("600 MHz, the boot point (the sizing's worst case)", 600.0),
                           ("E84's sampled mix under the alarm, 551 MHz", mix_mhz),
                           ("E84's kernel effective clock under the alarm, 0.479 GHz", 479.0),
                           ("E84's kernel effective clock under the alarm, 0.475 GHz", 475.0),
                           ("the alarm's 300 MHz safe state", 300.0)):
            w = cyc / (mhz * 1e6)
            rec["wall_at_fixed_clock_s"][label] = {"wall_s": round(w, 3), "over_host_timeout": w >= OK.HOST_TIMEOUT_S}
        out["types"][typ] = rec
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
