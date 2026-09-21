#!/usr/bin/env python3
"""Operand tiles for the FMA toggle bench, in the value patterns of workloads/sparsity's --values option.

    tiles.py <pattern> <out.hex> [--seed N] [--iters-before N] [--from-bin tiles.bin]

Writes 768 hex words: A[i][k], B[k][j], and the C the accumulators hold after --iters-before ops
(C = n * A.B computed in float32 the way the chip accumulates it, for small n; scaled for large n).
--from-bin takes the raw 2 x 1024-byte tiles dumped by sparsity_host --dump-tiles instead of drawing new ones.
"""
import argparse
import struct
import numpy as np

PATTERNS = ["zeros", "ones", "twos", "pi", "checker", "ternary", "onebit", "sparse75", "sparse50", "uniform", "randn",
            "signs", "pow2", "mant", "a_randn_b_ones", "a_ones_b_randn"]


def draw(pattern, rng):
    n = 512
    idx = np.arange(1, n + 1)
    if pattern == "zeros": v = np.zeros(n)
    elif pattern == "ones": v = np.ones(n)
    elif pattern == "twos": v = np.full(n, 2.0)
    elif pattern == "pi": v = np.full(n, 3.14159274)
    elif pattern == "checker": v = (idx & 1).astype(float)
    elif pattern == "ternary": v = rng.integers(0, 3, n) - 1.0
    elif pattern == "onebit": return np.full(n, 0x00800000, dtype=np.uint32)
    elif pattern == "uniform": v = rng.random(n)
    elif pattern == "randn": v = rng.standard_normal(n)
    elif pattern == "sparse75": v = np.where(rng.integers(0, 4, n) != 0, 0.0, rng.standard_normal(n))
    elif pattern == "sparse50": v = np.where(rng.integers(0, 2, n) != 0, 0.0, rng.standard_normal(n))
    elif pattern == "signs": v = np.where(rng.integers(0, 2, n) != 0, 1.0, -1.0)
    elif pattern == "pow2": v = 2.0 ** rng.integers(-8, 9, n)
    elif pattern == "mant": v = 1.0 + rng.random(n)
    elif pattern == "a_randn_b_ones": v = np.concatenate([rng.standard_normal(256), np.ones(256)])
    elif pattern == "a_ones_b_randn": v = np.concatenate([np.ones(256), rng.standard_normal(256)])
    else: raise SystemExit(f"unknown pattern {pattern}")
    return v.astype(np.float32).view(np.uint32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--iters-before", type=int, default=0)
    ap.add_argument("--from-bin")
    a = ap.parse_args()
    if a.from_bin:
        raw = np.frombuffer(open(a.from_bin, "rb").read(), dtype=np.uint32)
        words = raw[:512].copy()
    else:
        words = draw(a.pattern, np.random.default_rng(a.seed))
    A = words[:256].view(np.float32).reshape(16, 16).astype(np.float64)
    B = words[256:].view(np.float32).reshape(16, 16).astype(np.float64)
    with np.errstate(all="ignore"):
        C = ((A @ B) * a.iters_before).astype(np.float32)
    out = np.concatenate([words, C.reshape(-1).view(np.uint32)])
    open(a.out, "w").write("\n".join(f"{int(w):08x}" for w in out) + "\n")


if __name__ == "__main__":
    main()
