#!/usr/bin/env python3
"""E210 (Q202) desk: the fp32 TensorFMA arithmetic and operand stream of one op, in PRM 9.4's order as the RTL bench (rtl-sim/fma_toggle_v2,
vpu_tensorfma.v) models it, with the bench's zero gate and first pass. The fp32 part of sw-design-a's hd_model.py (round Q202), unchanged in
its arithmetic (sw-design-a checked it word for word against the bench's accum.c: fp32 3 gated ops on a sparse50 tile, 256 of 256), with its
paths made relative to this file and its fp16 part left out (E210 is fp32 only).

Inside an op: for k in 0..15, for i in 0..15, two micro-ops h = 0, 1; lane l (0..7) computes C[i][8h+l] = A[i][k] * B[k][8h+l] + C[i][8h+l];
a lane is gated (no valid) on an accumulate pass when its A or B WORD is zero (+0.0 exactly; -0.0 is not zero). The first op of an accumulation
is a MUL pass (no gate, C not read). Arithmetic: FMADD round-to-nearest-even with denormal operands read as zero and denormal results flushed
(accum.c's rules), computed as float64 a*b (exact) + c rounded to float32.
SPDX-License-Identifier: Apache-2.0
"""
import numpy as np

POP = np.array([bin(x).count('1') for x in range(1 << 16)], dtype=np.int64)


def pc(x):
    x = np.asarray(x, dtype=np.uint32)
    return POP[x & 0xFFFF] + POP[x >> 16]


def load(path):
    w = np.fromfile(path, dtype='<u4')
    assert w.size == 512, path
    return w[:256].reshape(16, 16).copy(), w[256:].reshape(16, 16).copy()


def daz(u):
    u = np.asarray(u, dtype=np.uint32)
    return np.where((u & 0x7F800000) == 0, u & 0x80000000, u).astype(np.uint32)


def ftz(u):
    u = np.asarray(u, dtype=np.uint32)
    return np.where((u & 0x7F800000) == 0, u & 0x80000000, u).astype(np.uint32)


def f32(u):
    return np.asarray(u, dtype=np.uint32).view(np.float32).astype(np.float64)


def op_stream_fp32(A, B, C, first):
    """one op: returns per-micro-op arrays a (512,), b (512,8), c_in (512,8), r (512,8), valid (512,8); updates C in place"""
    a_s = np.empty(512, np.uint32)
    b_s = np.empty((512, 8), np.uint32)
    c_s = np.empty((512, 8), np.uint32)
    r_s = np.zeros((512, 8), np.uint32)
    v_s = np.zeros((512, 8), bool)
    Af, Bf = f32(daz(A)), f32(daz(B))
    for k in range(16):
        a_col = A[:, k]
        b_row = B[k, :]
        if first and k == 0:
            valid = np.ones((16, 16), bool)
            r = ftz((Af[:, k][:, None] * Bf[k, :][None, :]).astype(np.float32).view(np.uint32))
        else:
            valid = (a_col[:, None] != 0) & (b_row[None, :] != 0)
            r = ftz((Af[:, k][:, None] * Bf[k, :][None, :] + f32(C)).astype(np.float32).view(np.uint32))
        cin = C.copy()
        Cn = np.where(valid, r, C)
        t0 = 32 * k
        for i in range(16):
            for h in range(2):
                t = t0 + 2 * i + h
                a_s[t] = a_col[i]
                b_s[t] = b_row[8 * h:8 * h + 8]
                c_s[t] = cin[i, 8 * h:8 * h + 8]
                r_s[t] = r[i, 8 * h:8 * h + 8]
                v_s[t] = valid[i, 8 * h:8 * h + 8]
        C[:] = Cn
    return a_s, b_s, c_s, r_s, v_s


def c_after(seq, c0=None, first_first=True):
    """C after the ops of `seq` (a list of (A, B)), from c0 (zeros if None); the first op a MUL pass if first_first"""
    C = np.zeros((16, 16), np.uint32) if c0 is None else c0.copy()
    for n, (A, B) in enumerate(seq):
        op_stream_fp32(A, B, C, first_first and n == 0)
    return C
