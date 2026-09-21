#!/usr/bin/env python3
"""Structured 16x16 operand tiles for the matmul heat experiments, as raw fp32 tile files.

    make_tiles.py <kind> <out.bin> [--seed N]        one tile pair (A then B, 1,024 bytes each)
    make_tiles.py --all <out-dir> [--seed N]         every kind, as <kind>.<seed>.bin
    make_tiles.py --list

The files load with `sparsity_host --values file:<out.bin>` and replay in `rtl-sim/fma_toggle` (tiles.py --from-bin).
Kinds (n = 16; "random" is standard normal):

  hadamard        Sylvester Hadamard matrix, entries +-1                 (A = B = H)
  hadamard_orth   the same scaled to be orthonormal, entries +-0.25
  dct             orthonormal DCT-II matrix                              (B is its transpose)
  fft_cos         real part of the DFT matrix, cos(2 pi j k / n)         (B is the imaginary part, sin)
  butterfly       one butterfly factor each: 2 random nonzeros per row at stride 2 (A) and stride 8 (B)
  kaleidoscope    dense products of all four butterfly factors, BB^T form (Dao et al., ICLR 2020)
  identity        the identity                                           (A = B = I)
  permutation     random permutation matrices
  diagonal        random diagonal matrices
  tridiagonal     random band of width 3
  block_diag      four random 4x4 blocks on the diagonal
  upper           random upper-triangular
  lowrank         rank-1: outer product of two random vectors
  circulant       random first row, shifted down the rows
  quant4          random normal rounded to 16 levels (4-bit weights)
  relu            A random normal, B random normal with negatives zeroed (weights times ReLU activations)
  negzero         every element -0.0: numerically zero, but not the bit pattern the chip's zero gating looks for
"""
import argparse
import os

import numpy as np

N = 16


def butterfly_factor(stride, rng):
    m = np.zeros((N, N))
    for i in range(N):
        m[i, i] = rng.standard_normal()
        m[i, i ^ stride] = rng.standard_normal()
    return m


def butterfly(rng):
    m = np.eye(N)
    for s in (1, 2, 4, 8):
        m = butterfly_factor(s, rng) @ m
    return m


def tiles(kind, rng):
    idx = np.arange(N)
    if kind in ("hadamard", "hadamard_orth"):
        h = np.array([[1.0]])
        while h.shape[0] < N:
            h = np.block([[h, h], [h, -h]])
        h = h / 4.0 if kind == "hadamard_orth" else h
        return h, h
    if kind == "dct":
        d = np.cos(np.pi * (idx[None, :] + 0.5) * idx[:, None] / N) * np.sqrt(2.0 / N)
        d[0] /= np.sqrt(2.0)
        return d, d.T
    if kind == "fft_cos":
        ang = 2 * np.pi * np.outer(idx, idx) / N
        c, s = np.cos(ang), np.sin(ang)
        c[np.abs(c) < 1e-12] = 0.0; s[np.abs(s) < 1e-12] = 0.0
        return c, s
    if kind == "butterfly":
        return butterfly_factor(2, rng), butterfly_factor(8, rng)
    if kind == "kaleidoscope":
        return butterfly(rng) @ butterfly(rng).T, butterfly(rng) @ butterfly(rng).T
    if kind == "identity":
        return np.eye(N), np.eye(N)
    if kind == "permutation":
        return np.eye(N)[rng.permutation(N)], np.eye(N)[rng.permutation(N)]
    if kind == "diagonal":
        return np.diag(rng.standard_normal(N)), np.diag(rng.standard_normal(N))
    if kind == "tridiagonal":
        band = np.abs(idx[:, None] - idx[None, :]) <= 1
        return rng.standard_normal((N, N)) * band, rng.standard_normal((N, N)) * band
    if kind == "block_diag":
        blk = (idx[:, None] // 4) == (idx[None, :] // 4)
        return rng.standard_normal((N, N)) * blk, rng.standard_normal((N, N)) * blk
    if kind == "upper":
        up = idx[:, None] <= idx[None, :]
        return rng.standard_normal((N, N)) * up, rng.standard_normal((N, N)) * up
    if kind == "lowrank":
        return np.outer(rng.standard_normal(N), rng.standard_normal(N)), np.outer(rng.standard_normal(N), rng.standard_normal(N))
    if kind == "circulant":
        r1, r2 = rng.standard_normal(N), rng.standard_normal(N)
        return np.array([np.roll(r1, i) for i in range(N)]), np.array([np.roll(r2, i) for i in range(N)])
    if kind == "quant4":
        q = lambda x: np.clip(np.round(x * 2.5), -8, 7) / 2.5
        return q(rng.standard_normal((N, N))), q(rng.standard_normal((N, N)))
    if kind == "relu":
        return rng.standard_normal((N, N)), np.maximum(rng.standard_normal((N, N)), 0.0)
    if kind == "negzero":
        return np.full((N, N), -0.0), np.full((N, N), -0.0)
    raise SystemExit(f"unknown kind {kind}")


KINDS = ["hadamard", "hadamard_orth", "dct", "fft_cos", "butterfly", "kaleidoscope", "identity", "permutation", "diagonal",
         "tridiagonal", "block_diag", "upper", "lowrank", "circulant", "quant4", "relu", "negzero"]


def write(kind, path, seed):
    a, b = tiles(kind, np.random.default_rng(seed))
    if kind != "negzero":
        a, b = a + 0.0, b + 0.0   # x * 0 leaves -0.0 for negative x, and the chip only gates the all-zero bit pattern
    with open(path, "wb") as f:
        f.write(a.astype("<f4").tobytes())   # row i of A is scratchpad line i: 16 floats
        f.write(b.astype("<f4").tobytes())   # row k of B likewise
    return a, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--all")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print(" ".join(KINDS)); return
    if a.all:
        os.makedirs(a.all, exist_ok=True)
        for k in KINDS:
            A, B = write(k, os.path.join(a.all, f"{k}.{a.seed}.bin"), a.seed)
            print(f"{k:14s} nonzero A {np.count_nonzero(A):3d}/256  B {np.count_nonzero(B):3d}/256  distinct |values| {len(np.unique(np.abs(np.concatenate([A.ravel(), B.ravel()]).astype('<f4'))))}")
        return
    write(a.kind, a.out, a.seed)


if __name__ == "__main__":
    main()
