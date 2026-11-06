#!/usr/bin/env python3
"""The accumulating modes' sums c (c += v, eight chains a hart, c = 0 at a launch's start), word for word.

    python3 walk_e180.py --steps N1,N2,...      # prints the 32-bit word of c after each N steps, for each R5 kind

fadd.ps.acc: float32 addition, round to nearest even, every step (the txfma's own add, DAZ/FTZ irrelevant: no denormal
is reached); fadd.pi.acc: int32 addition mod 2^32. A step is one fadd of one chain; a hart's 64-op loop iteration
advances each of its 8 chains 8 steps.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import struct


def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


def w(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def walk_f32(v, steps):
    """c after each of the given step counts (sorted), float32 round-to-nearest-even each step."""
    out, c, k = {}, 0.0, 0
    vv = f32(v)
    for n in sorted(steps):
        while k < n:
            # exact float32 sum: a double holds c + v exactly for these magnitudes, then one rounding
            c = f32(c + vv)
            k += 1
        out[n] = c
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", required=True)
    a = ap.parse_args()
    steps = [int(x) for x in a.steps.split(",")]
    res = {}
    for name, v in (("fadd.ps.acc/f_4", 4.0), ("fadd.ps.acc/f_5", 5.0), ("fadd.ps.acc/const", 1.0)):
        cs = walk_f32(v, steps)
        res[name] = {str(n): f"0x{w(cs[n]):08x}" for n in steps}
    for name, v in (("fadd.pi.acc/i_4", 4), ("fadd.pi.acc/i_5", 5), ("fadd.pi.acc/i_1", 1)):
        res[name] = {str(n): f"0x{(v * n) & 0xFFFFFFFF:08x}" for n in steps}
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
