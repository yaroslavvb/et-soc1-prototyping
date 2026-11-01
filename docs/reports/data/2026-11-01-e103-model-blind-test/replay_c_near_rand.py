#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103, corrections after verification: fp32.c_near_rand was chosen as a near-cancelling tile. How near does it cancel, along a launch? A float32 replay of its stream. Every A word is 1, so all sixteen rows of C are the same.

    python3 replay_c_near_rand.py <tile.bin> > replay-c-near-rand.txt          # about a minute on the mini; the Intel's load makes it slow

SPDX-License-Identifier: Apache-2.0
"""
import sys

import numpy as np

w = np.frombuffer(open(sys.argv[1], "rb").read(), dtype="<f4")
A = w[:256].reshape(16, 16).astype(np.float64)
B = w[256:].reshape(16, 16).astype(np.float32)
print("A all 1:", bool(np.all(A == 1.0)))


def lost(C0, p):
    C1 = (C0 + p).astype(np.float32).astype(np.float64)
    big = np.maximum(np.abs(C0), np.abs(p))
    with np.errstate(divide="ignore"):
        drop = np.log2(big) - np.log2(np.abs(C1))
    drop = np.where(big == 0, 0.0, drop)
    drop = np.where((C1 == 0) & (big > 0), 99.0, drop)
    return C1, drop


marks = (0, 1000, 5000, 20000, 91575, 274725, 457875)
C32 = np.zeros(16, dtype=np.float32)
for n in range(max(marks) + 1):
    if n in marks:
        C = C32.astype(np.float64)
        c8 = c4 = 0
        for k in range(16):
            C, dr = lost(C, B[k].astype(np.float64))
            c8 += int((dr >= 8).sum())
            c4 += int((dr >= 4).sum())
        C32 = C.astype(np.float32)
        print(f"op {n:7d}: MACs losing >= 8 bits {c8 / 256:.1%}, >= 4 bits {c4 / 256:.1%}; median |C| {np.median(np.abs(C)):.4g}")
    else:
        for k in range(16):
            C32 = C32 + B[k]
