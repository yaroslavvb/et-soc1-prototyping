#!/usr/bin/env python3
"""E202's bit-exact numpy model of the mnistmlp kernel's integer arithmetic, and the files the host reads.

The network: 784 -> 1792 -> 1792 -> 1792 -> 1792 -> 10 (ReLU, biases), K padded to 832 in layer 1 and N to 16 in layer
5 with zero weights. Per image, as the kernel computes (../kernel/mnistmlp.c):
    acc_j  = sum_k x_k * Q_kj          x uint8 (TensorIMA8A32 with UA = 1), Q int8, exact int32 accumulation
    hidden: y_j = sat_u8( ((acc_j + Bp_j) * M) >> 32 )   fadd.pi (32-bit wrap), fmulh.pi (floor), fsatu8.pi
    output: logit_j = acc_j + B_j (j < 10); label = the first index of the maximum (numpy's argmax rule)
    checksum of a group of 16 images = the sum of its 160 logits mod 2^32
Every product and partial sum is an integer below 2^53, so a float64 matrix product is exact (checked against int64).

Files (little-endian):
  MLPW  weights: 256 B header (b"MLPW0001", u32 layers = 5, per layer u32 Kpad, Npad, Kreal, Nreal, u32 M[4] at byte 92,
        a 32 B name at byte 108, zeros to 256), then each layer's int8 Q[Kpad][Npad], then each layer's int32 bias[Npad]
        (Bp for hidden layers: B + floor(2^31 / M), the rounding offset folded in; B for the output layer).
  MLPE  expected outputs: 64 B header (b"MLPE0001", u32 groups, u32 images), uint8 labels[groups*16], u32 checksum[groups].
  MLPL  expected raw layer-5 C tiles: 64 B header (b"MLPL0001", u32 groups), int32 [groups][16][16] (acc, no bias).
  MLPR  the host's --ref output: 64 B header (b"MLPR0001", u32 groups), per group 16 labels, u32 checksum, 12 zero
        bytes, int32 [16][16].

Commands (python3 -I -B mnist_model.py ...):
  expect --weights W --images IDX --out-expect E [--out-logits L]   the expected outputs of a whole split
  make-random --train-images IDX --out W                             the random-weights configuration
  compare-ref --ref R --weights W --images IDX                       the host's reference against this model
  info --weights W                                                   shape, multipliers and sha256 of a weights file
  dump-tiles --weights W --images IDX --groups N --out NPZ           the A and B tile pairs in issue order
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import struct
import sys

import numpy as np

H = 1792
DIMS = [784, H, H, H, H, 10]
KPAD = [832, H, H, H, H]
NPAD = [H, H, H, H, 16]
NGROUP = 16
RANDOM_SEED0 = 0xE202000000000000   # layer l (1..5) draws from seed RANDOM_SEED0 + l
RANDOM_PCT = 99.9                   # random config: this percentile of the positive accumulators maps to 255
CAL_IMAGES = 10000                  # calibration: the first 10,000 training images


# ------------------------------------------------------------------ files
def load_idx(path):
    raw = open(path, "rb").read()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    magic, = struct.unpack(">I", raw[:4])
    nd = magic & 0xFF
    dims = struct.unpack(">" + "I" * nd, raw[4:4 + 4 * nd])
    return np.frombuffer(raw, dtype=np.uint8, offset=4 + 4 * nd).reshape(dims)


def load_images(path):
    x = load_idx(path)
    assert x.ndim == 3 and x.shape[1:] == (28, 28), x.shape
    return x.reshape(-1, 784)


def write_mlpw(path, Q, B, M, name):
    assert len(Q) == 5 and len(B) == 5 and len(M) == 4
    hdr = bytearray(256)
    hdr[0:8] = b"MLPW0001"
    struct.pack_into("<I", hdr, 8, 5)
    for l in range(5):
        assert Q[l].dtype == np.int8 and Q[l].shape == (KPAD[l], NPAD[l]), (l, Q[l].dtype, Q[l].shape)
        assert not Q[l][DIMS[l]:, :].any() and not Q[l][:, DIMS[l + 1]:].any(), "nonzero padding"
        struct.pack_into("<IIII", hdr, 12 + 16 * l, KPAD[l], NPAD[l], DIMS[l], DIMS[l + 1])
    for i in range(4):
        assert 0 < int(M[i]) < 2 ** 31
        struct.pack_into("<I", hdr, 92 + 4 * i, int(M[i]))
    nb = name.encode()[:32]
    hdr[108:108 + len(nb)] = nb
    with open(path, "wb") as f:
        f.write(bytes(hdr))
        for l in range(5):
            f.write(np.ascontiguousarray(Q[l]).tobytes())
        for l in range(5):
            b = np.asarray(B[l], dtype=np.int64)
            assert b.shape == (NPAD[l],) and b.min() >= -2 ** 31 and b.max() < 2 ** 31
            f.write(b.astype("<i4").tobytes())


def read_mlpw(path):
    d = open(path, "rb").read()
    assert d[:8] == b"MLPW0001", "not an MLPW0001 file"
    assert struct.unpack_from("<I", d, 8)[0] == 5
    for l in range(5):
        assert struct.unpack_from("<IIII", d, 12 + 16 * l) == (KPAD[l], NPAD[l], DIMS[l], DIMS[l + 1]), l
    M = [struct.unpack_from("<I", d, 92 + 4 * i)[0] for i in range(4)]
    name = d[108:140].split(b"\0")[0].decode()
    off = 256
    Q, B = [], []
    for l in range(5):
        n = KPAD[l] * NPAD[l]
        Q.append(np.frombuffer(d, dtype=np.int8, count=n, offset=off).reshape(KPAD[l], NPAD[l]))
        off += n
    for l in range(5):
        B.append(np.frombuffer(d, dtype="<i4", count=NPAD[l], offset=off).astype(np.int64))
        off += 4 * NPAD[l]
    assert off == len(d), "MLPW size"
    return Q, B, M, name


def write_mlpe(path, labels, checksums, nimages):
    g = len(checksums)
    assert labels.shape == (g * NGROUP,)
    hdr = bytearray(64)
    hdr[0:8] = b"MLPE0001"
    struct.pack_into("<II", hdr, 8, g, nimages)
    with open(path, "wb") as f:
        f.write(bytes(hdr))
        f.write(labels.astype(np.uint8).tobytes())
        f.write(np.asarray(checksums, dtype="<u4").tobytes())


def write_mlpl(path, c5):
    g = c5.shape[0]
    assert c5.shape == (g, 16, 16)
    hdr = bytearray(64)
    hdr[0:8] = b"MLPL0001"
    struct.pack_into("<I", hdr, 8, g)
    with open(path, "wb") as f:
        f.write(bytes(hdr))
        f.write(c5.astype("<i4").tobytes())


def read_mlpr(path):
    d = open(path, "rb").read()
    assert d[:8] == b"MLPR0001", "not an MLPR0001 file"
    g = struct.unpack_from("<I", d, 8)[0]
    rec = 16 + 4 + 12 + 1024
    assert len(d) == 64 + g * rec, "MLPR size"
    labels = np.zeros((g, 16), dtype=np.uint8)
    sums = np.zeros(g, dtype=np.uint32)
    c5 = np.zeros((g, 16, 16), dtype=np.int32)
    for i in range(g):
        o = 64 + i * rec
        labels[i] = np.frombuffer(d, dtype=np.uint8, count=16, offset=o)
        sums[i] = struct.unpack_from("<I", d, o + 16)[0]
        c5[i] = np.frombuffer(d, dtype="<i4", count=256, offset=o + 32).reshape(16, 16)
    return labels, sums, c5


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# ------------------------------------------------------------------ splitmix64
def splitmix64_bytes(seed, nbytes):
    """Little-endian bytes of successive splitmix64 outputs (the scalar definition)."""
    m = (1 << 64) - 1
    out = bytearray()
    s = seed & m
    while len(out) < nbytes:
        s = (s + 0x9E3779B97F4A7C15) & m
        z = s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & m
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & m
        z = z ^ (z >> 31)
        out += z.to_bytes(8, "little")
    return bytes(out[:nbytes])


def splitmix64_int8(seed, shape):
    """Vectorised splitmix64: the same bytes as splitmix64_bytes, read as int8 of the given shape (row-major)."""
    n = int(np.prod(shape))
    nw = (n + 7) // 8
    with np.errstate(over="ignore"):
        i = np.arange(1, nw + 1, dtype=np.uint64)
        z = np.uint64(seed) + i * np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    b = z.astype("<u8").view(np.uint8)[:n]
    return b.view(np.int8).reshape(shape)


# ------------------------------------------------------------------ the kernel's arithmetic
def matmul_exact(h_u8, q_i8, exact_int=False):
    """acc = h @ q exactly: int64, or float64 (exact: every partial sum is an integer below 2^53)."""
    if exact_int:
        return h_u8.astype(np.int64) @ q_i8.astype(np.int64)
    a = h_u8.astype(np.float64) @ q_i8.astype(np.float64)
    acc = np.rint(a).astype(np.int64)
    assert np.array_equal(acc.astype(np.float64), a), "float64 product not integral"
    return acc


def requant(acc, Bp, M):
    """fadd.pi Bp (32-bit), fmulh.pi M (floor(p / 2^32) of the signed 64-bit product), fsatu8.pi."""
    s = acc + Bp
    assert s.min() >= -2 ** 31 and s.max() < 2 ** 31, "fadd.pi would wrap"
    return np.clip((s * np.int64(M)) >> 32, 0, 255).astype(np.uint8)


def forward(Q, B, M, x_u8, exact_int=False, collect=None):
    """The kernel's outputs for images x_u8 (n, 784): logits (n, 10) int64, labels (n,) uint8, c5 (n, 16) int64 raw."""
    n = x_u8.shape[0]
    h = np.zeros((n, KPAD[0]), dtype=np.uint8)
    h[:, :784] = x_u8
    for l in range(5):
        acc = matmul_exact(h, Q[l], exact_int)
        assert np.abs(acc).max() < 2 ** 31
        if collect is not None:
            collect.setdefault("acc_absmax", [0] * 5)
            collect["acc_absmax"][l] = max(collect["acc_absmax"][l], int(np.abs(acc).max()))
        if l < 4:
            h = requant(acc, B[l], M[l])
            if collect is not None:
                collect.setdefault("act_zero", [[] for _ in range(4)])[l].append(float((h == 0).mean()))
                collect.setdefault("act_sat", [[] for _ in range(4)])[l].append(float((h == 255).mean()))
        else:
            logits = acc[:, :10] + B[4][:10]
            assert logits.min() >= -2 ** 31 and logits.max() < 2 ** 31
            return logits, logits.argmax(axis=1).astype(np.uint8), acc


def forward_chunked(Q, B, M, x_u8, chunk=10000, collect=None):
    L, Y, C = [], [], []
    for i in range(0, x_u8.shape[0], chunk):
        lg, lb, c5 = forward(Q, B, M, x_u8[i:i + chunk], collect=collect)
        L.append(lg)
        Y.append(lb)
        C.append(c5)
    return np.concatenate(L), np.concatenate(Y), np.concatenate(C)


def group_checksums(logits):
    g = logits.shape[0] // NGROUP
    s = logits[:g * NGROUP].reshape(g, NGROUP * 10).astype(np.int64).sum(axis=1)
    return (s % (1 << 32)).astype(np.uint32)


def pack_b_tile(Q, l, c, t):
    """B tile (layer l, column block c, k tile t) as TensorIMA8A32 reads TenB: line p, bytes 4j..4j+3 = Q[64t+4p+x, 16c+j]."""
    blk = Q[l][64 * t:64 * (t + 1), 16 * c:16 * (c + 1)]             # (64 k, 16 n)
    return blk.reshape(16, 4, 16).transpose(0, 2, 1).reshape(16, 64)  # line p: n-major, 4 consecutive k each


# ------------------------------------------------------------------ commands
def cmd_expect(a):
    Q, B, M, name = read_mlpw(a["--weights"])
    x = load_images(a["--images"])
    assert x.shape[0] % NGROUP == 0
    col = {}
    logits, labels, c5 = forward_chunked(Q, B, M, x, collect=col)
    sums = group_checksums(logits)
    write_mlpe(a["--out-expect"], labels, sums, x.shape[0])
    out = {"weights": os.path.basename(a["--weights"]), "weights_sha256": sha256_file(a["--weights"]),
           "weights_name": name, "images": os.path.basename(a["--images"]), "images_sha256": sha256_file(a["--images"]),
           "groups": int(len(sums)), "expect": os.path.basename(a["--out-expect"]),
           "expect_sha256": sha256_file(a["--out-expect"]),
           "labels_sha256": hashlib.sha256(labels.tobytes()).hexdigest(),
           "label_histogram": np.bincount(labels, minlength=10).tolist(),
           "acc_absmax": col["acc_absmax"],
           "act_zero_share": [float(np.mean(v)) for v in col["act_zero"]],
           "act_sat255_share": [float(np.mean(v)) for v in col["act_sat"]]}
    if a.get("--out-logits"):
        g = x.shape[0] // NGROUP
        write_mlpl(a["--out-logits"], c5.reshape(g, NGROUP, 16))
        out["logits"] = os.path.basename(a["--out-logits"])
        out["logits_sha256"] = sha256_file(a["--out-logits"])
    if a.get("--true-labels"):
        y = load_idx(a["--true-labels"])
        out["accuracy"] = float((labels == y).mean())
    print(json.dumps(out))
    return 0


def make_random(train_x):
    Q, B, M = [], [], []
    h = np.zeros((CAL_IMAGES, KPAD[0]), dtype=np.uint8)
    h[:, :784] = train_x[:CAL_IMAGES]
    info = []
    for l in range(5):
        q = np.zeros((KPAD[l], NPAD[l]), dtype=np.int8)
        q[:DIMS[l], :DIMS[l + 1]] = splitmix64_int8(RANDOM_SEED0 + l + 1, (DIMS[l], DIMS[l + 1]))
        Q.append(q)
        acc = matmul_exact(h, q)
        if l < 4:
            p = float(np.percentile(acc[acc > 0], RANDOM_PCT))
            m = int(round(255.0 * 2 ** 32 / p))
            assert 0 < m < 2 ** 31
            M.append(m)
            bp = np.full(NPAD[l], (2 ** 31) // m, dtype=np.int64)   # biases 0, the rounding offset folded in
            B.append(bp)
            h = requant(acc, bp, m)
            info.append({"layer": l + 1, "p999_positive_acc": p, "M": m, "act_zero": float((h == 0).mean()),
                         "act_sat255": float((h == 255).mean())})
        else:
            B.append(np.zeros(NPAD[l], dtype=np.int64))
    return Q, B, M, info


def cmd_make_random(a):
    x = load_images(a["--train-images"])
    Q, B, M, info = make_random(x)
    write_mlpw(a["--out"], Q, B, M, "random-splitmix64-e202")
    print(json.dumps({"out": os.path.basename(a["--out"]), "sha256": sha256_file(a["--out"]), "M": M,
                      "requant": info}))
    return 0


def cmd_compare_ref(a):
    labels_r, sums_r, c5_r = read_mlpr(a["--ref"])
    Q, B, M, _ = read_mlpw(a["--weights"])
    x = load_images(a["--images"])
    g = labels_r.shape[0]
    logits, labels, c5 = forward(Q, B, M, x[:g * NGROUP], exact_int=True)
    sums = group_checksums(logits)
    res = {"groups": int(g), "images": int(g * NGROUP),
           "labels_equal": bool(np.array_equal(labels.reshape(g, 16), labels_r)),
           "checksums_equal": bool(np.array_equal(sums, sums_r)),
           "c5_equal": bool(np.array_equal(c5.reshape(g, 16, 16).astype(np.int64), c5_r.astype(np.int64))),
           "arithmetic": "int64 (exact_int)"}
    res["status"] = "EQUAL" if res["labels_equal"] and res["checksums_equal"] and res["c5_equal"] else "DIFFER"
    print(json.dumps(res))
    return 0 if res["status"] == "EQUAL" else 1


def cmd_info(a):
    Q, B, M, name = read_mlpw(a["--weights"])
    print(json.dumps({"name": name, "M": M, "sha256": sha256_file(a["--weights"]),
                      "q_sha256": [hashlib.sha256(np.ascontiguousarray(q).tobytes()).hexdigest() for q in Q],
                      "bias_absmax": [int(np.abs(b).max()) for b in B],
                      "zero_weight_share_real": [float((Q[l][:DIMS[l], :DIMS[l + 1]] == 0).mean()) for l in range(5)]}))
    return 0


def cmd_dump_tiles(a):
    """The operand tile pairs one minion issues for the first N groups, in issue order: A (16 x 64 uint8) and B
    (16 x 64 int8 as TenB holds it), for a tensor-data price computed from tile pairs (the registration's job)."""
    Q, B, M, _ = read_mlpw(a["--weights"])
    x = load_images(a["--images"])
    n = int(a["--groups"])
    A_t, B_t, meta = [], [], []
    for g in range(n):
        h = np.zeros((NGROUP, KPAD[0]), dtype=np.uint8)
        h[:, :784] = x[NGROUP * g:NGROUP * (g + 1)]
        for l in range(5):
            for c in range(NPAD[l] // 16):
                for t in range(KPAD[l] // 64):
                    A_t.append(h[:, 64 * t:64 * (t + 1)])
                    B_t.append(pack_b_tile(Q, l, c, t))
                    meta.append((g, l, c, t))
            acc = matmul_exact(h, Q[l], exact_int=True)
            if l < 4:
                h = requant(acc, B[l], M[l])
    np.savez_compressed(a["--out"], A=np.array(A_t, dtype=np.uint8), B=np.array(B_t, dtype=np.int8),
                        meta=np.array(meta, dtype=np.int32))
    print(json.dumps({"out": os.path.basename(a["--out"]), "pairs": len(meta), "groups": n}))
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] not in ("expect", "make-random", "compare-ref", "info", "dump-tiles"):
        print(__doc__)
        return 2
    a = {}
    i = 2
    while i < len(argv):
        if i + 1 >= len(argv):
            print("missing value for", argv[i])
            return 2
        a[argv[i]] = argv[i + 1]
        i += 2
    return {"expect": cmd_expect, "make-random": cmd_make_random, "compare-ref": cmd_compare_ref, "info": cmd_info,
            "dump-tiles": cmd_dump_tiles}[argv[1]](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
