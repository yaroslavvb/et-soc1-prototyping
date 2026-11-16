#!/usr/bin/env python3
"""Self-tests of E202's numpy model (mnist_model.py). CPU only, a few seconds, no data files needed.

  1. the float64 matrix product equals int64 on random uint8 x int8 operands at the network's largest K (exactness);
  2. the B-tile interleave (pack_b_tile) against a direct 16 x 64 x 16 product, as TensorIMA8A32 reads TenB;
  3. splitmix64: the vectorised form against the scalar definition, and the generator's published first output;
  4. the label rule on ties: numpy's argmax takes the first index of the maximum, as the kernel's strict '>' does;
  5. the requantization's floor and saturation: fmulh.pi is floor(p / 2^32) of the signed product (an arithmetic
     shift), fsatu8.pi clamps to 0..255;
  6. MLPW, MLPE and MLPL files round-trip;
  7. the group checksum is the sum of 160 logits mod 2^32 (negative logits wrap).
Usage: python3 -I -B selftest_model.py      prints one line per test and MODEL-SELFTEST PASS (exit 0) or FAIL (exit 1)
SPDX-License-Identifier: Apache-2.0
"""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mnist_model as mm  # noqa: E402

bad = 0


def check(name, ok):
    global bad
    print(f"MODEL-SELFTEST {name:56s} {'OK' if ok else 'MISMATCH'}")
    bad += not ok


rng = np.random.default_rng(1)
# 1
h = rng.integers(0, 256, size=(64, 1792), dtype=np.uint8)
q = rng.integers(-128, 128, size=(1792, 64), dtype=np.int64).astype(np.int8)
check("float64 product == int64 product (K 1792, extremes included)",
      np.array_equal(mm.matmul_exact(h, q), mm.matmul_exact(h, q, exact_int=True)))
hx = np.full((2, 1792), 255, dtype=np.uint8)
qx = np.full((1792, 2), -128, dtype=np.int8)
check("largest |acc| = 1792 x 255 x 128 is exact", int(mm.matmul_exact(hx, qx)[0, 0]) == -1792 * 255 * 128)
# 2
Q = [np.zeros((mm.KPAD[l], mm.NPAD[l]), dtype=np.int8) for l in range(5)]
Q[1][:, :] = rng.integers(-128, 128, size=(1792, 1792)).astype(np.int8)
A = rng.integers(0, 256, size=(16, 64), dtype=np.uint8)
c, t = 7, 3
Bt = mm.pack_b_tile(Q, 1, c, t)
direct = A.astype(np.int64) @ Q[1][64 * t:64 * (t + 1), 16 * c:16 * (c + 1)].astype(np.int64)
packed = np.zeros((16, 16), dtype=np.int64)
for p in range(16):
    for x in range(4):
        packed += np.outer(A[:, 4 * p + x].astype(np.int64), Bt[p, x::4].astype(np.int64))
check("B-tile interleave: line p, bytes 4j..4j+3 = Q[64t+4p+x, 16c+j]", np.array_equal(direct, packed))
# 3
check("splitmix64 vectorised == scalar (4 KiB, layer-1 seed)",
      mm.splitmix64_int8(mm.RANDOM_SEED0 + 1, (4096,)).view(np.uint8).tobytes() ==
      mm.splitmix64_bytes(mm.RANDOM_SEED0 + 1, 4096))
check("splitmix64(0) first output 0xE220A8397B1DCDAF",
      int.from_bytes(mm.splitmix64_bytes(0, 8), "little") == 0xE220A8397B1DCDAF)
# 4
lg = np.array([[3, 7, 7, 1, 0, 0, 0, 0, 0, 0], [-5] * 10, [0, 0, 0, 0, 0, 0, 0, 0, 0, 9]])
check("argmax takes the first maximum (7 at 1 and 2 -> 1; all equal -> 0)", lg.argmax(axis=1).tolist() == [1, 0, 9])
# 5
M = 4492549
acc = np.array([-1, 0, 955, 956, 957, 1 << 24, -(1 << 24)], dtype=np.int64)
y = mm.requant(acc, np.zeros_like(acc), M)
ref = [max(0, min(255, (int(a) * M) >> 32)) for a in acc]
check("requant: floor of the signed product, clamp 0..255", y.tolist() == ref and y.tolist()[0] == 0)
check("requant: -1 x M -> floor(-M / 2^32) = -1 -> 0", ((-1 * M) >> 32) == -1)
# 6
with tempfile.TemporaryDirectory() as d:
    Qw = [np.zeros((mm.KPAD[l], mm.NPAD[l]), dtype=np.int8) for l in range(5)]
    for l in range(5):
        Qw[l][:mm.DIMS[l], :mm.DIMS[l + 1]] = mm.splitmix64_int8(99 + l, (mm.DIMS[l], mm.DIMS[l + 1]))
    Bw = [rng.integers(-1000, 1000, size=mm.NPAD[l]) for l in range(5)]
    for l in range(5):
        Bw[l][mm.DIMS[l + 1]:] = 0
    Mw = [11, 22, 33, 44]
    mm.write_mlpw(os.path.join(d, "w.mlpw"), Qw, Bw, Mw, "selftest")
    Q2, B2, M2, n2 = mm.read_mlpw(os.path.join(d, "w.mlpw"))
    check("MLPW round trip", all(np.array_equal(Qw[l], Q2[l]) and np.array_equal(Bw[l], B2[l]) for l in range(5))
          and M2 == Mw and n2 == "selftest" and os.path.getsize(os.path.join(d, "w.mlpw")) == 11182400)
    lab = rng.integers(0, 10, size=32, dtype=np.uint8)
    mm.write_mlpe(os.path.join(d, "e.mlpe"), lab, np.array([1, 2], dtype=np.uint32), 32)
    raw = open(os.path.join(d, "e.mlpe"), "rb").read()
    check("MLPE layout (64 B header, labels, checksums)", raw[:8] == b"MLPE0001" and len(raw) == 64 + 32 + 8
          and raw[64:96] == lab.tobytes())
    c5 = rng.integers(-1000, 1000, size=(2, 16, 16)).astype(np.int32)
    mm.write_mlpl(os.path.join(d, "l.mlpl"), c5)
    raw = open(os.path.join(d, "l.mlpl"), "rb").read()
    check("MLPL layout (64 B header, int32 tiles)", raw[:8] == b"MLPL0001" and
          np.array_equal(np.frombuffer(raw, dtype="<i4", offset=64).reshape(2, 16, 16), c5))
# 7
lg = np.full((16, 10), -1, dtype=np.int64)
check("checksum wraps mod 2^32 (160 x -1 -> 2^32 - 160)", int(mm.group_checksums(lg)[0]) == (1 << 32) - 160)

print(f"MODEL-SELFTEST {'FAIL' if bad else 'PASS'}")
sys.exit(1 if bad else 0)
