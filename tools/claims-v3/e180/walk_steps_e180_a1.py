#!/usr/bin/env python3
"""E180's dated note A1 (E180.md.dated-note-A1.md section 6, wording (d)): the step sizes of the accumulating 5s' float32 walk over a
whole launch, with walk_e180.py's own rounding (imported unchanged), to the registration's last launch point (9,325,000 steps).

    python3 -B tools/claims-v3/e180/walk_steps_e180_a1.py            # prints the table; writes nothing

E180.md section 3 says float32 "rounds each +5 to +4 or +8" above 2^24. This counts, by binade of the sum, every step's size for
v = 5 (and v = 4 and 1, the walks the registration calls alike). Standard library only; about 30 s on one core.
SPDX-License-Identifier: Apache-2.0
"""
import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import walk_e180 as wk  # noqa: E402

STEPS = 9325000


def main():
    for v in (5.0, 4.0, 1.0):
        c, hist = 0.0, {}
        vv = wk.f32(v)
        for _ in range(STEPS):
            n = wk.f32(c + vv)
            b = int(math.floor(math.log2(n))) if n > 0 else 0
            hist.setdefault(b, {}).setdefault(n - c, 0)
            hist[b][n - c] += 1
            c = n
        print(f"v = {v:g}: the sum after {STEPS:,} steps is {c:,.0f} (0x{wk.w(c):08x}), below 2^26 = {2 ** 26:,}: {c < 2 ** 26}")
        for b in sorted(hist):
            if b >= 22:
                print(f"   sums in [2^{b}, 2^{b + 1}): " + ", ".join(f"+{s:g} x {k:,}" for s, k in sorted(hist[b].items())))


if __name__ == "__main__":
    main()
