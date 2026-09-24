#!/usr/bin/env python3
"""Bit-toggle rate of the 'random' wire data, from the exact byte image the prefill leaves in each scratchpad.

Prefill (run_catalogue.py): enercat_host --pattern tstore --operands random --slice-bytes 32K --scp, on all 32 shires.
Kernel EC_TSTORE (hart 0 of every minion, hart id h = 64*shire + 2*minion): f0..f7 = the 8 x 32 B rows of this hart's
256 B source block, f8..f15 = fadd.ps f_i,f_i = 2*f_i; each tensor store writes rows f0..f15 (16 x 32 B = 512 B,
row n from register n: sys_emu tensors.cpp srcinc = STEP+1) and the 512 B block repeats 64 times through the 32 KB
slot at scratchpad offset 256K + minion*32K. The wire run reads slot m of the target shire, so the data are the
source block of hart 64*target + 2*m. Sources: exact C++ reproduction (gen_sources.cpp, libstdc++ of GCC 13.3,
seed 1), mt19937_64 + uniform_real_distribution<float>(0.5, 2).
"""
import json
import numpy as np

w = np.fromfile('sources_seed1.bin', dtype='<u4')
f = w.view('<f4')
SLICE = 32 * 1024
rng = np.random.default_rng(0)


def image(hart):
    blk = f[hart * 64:(hart + 1) * 64].astype(np.float32)          # 64 floats = 256 B = f0..f7
    dbl = (blk * np.float32(2)).astype(np.float32)                   # f8..f15 = 2*f0..2*f7 (exact)
    one = np.concatenate([blk, dbl]).view('<u4')                     # 512 B block, 128 words
    return np.tile(one, SLICE // 512)                                # 32 KB slot, 8192 words


harts = [64 * t + 2 * m for t in range(32) for m in range(32)]
imgs = np.stack([image(h) for h in harts])                          # (1024, 8192) u32
bits = np.unpackbits(imgs.view(np.uint8), axis=1, bitorder='little').reshape(1024, -1)   # (1024, 262144)
print("ones density of the image:", bits.mean().round(4))

def popcount32(x):
    return np.unpackbits(x.view(np.uint8), bitorder='little').reshape(x.shape + (32,)).sum(-1)

out = {"ones_density": float(bits.mean())}
# 1) one flow, chunks of W bytes in address order (cyclic through the slot)
for W in (16, 32, 64, 128, 256, 512):
    nw = W // 4
    ch = imgs.reshape(1024, -1, nw)                                   # (1024, nchunks, nw)
    nxt = np.roll(ch, -1, axis=1)
    x = np.bitwise_xor(ch, nxt)
    t = np.unpackbits(x.view(np.uint8), axis=-1).sum() / (x.size * 32)
    out[f"seq_W{W}"] = float(t)
    print(f"one flow, address order, {W:3d} B chunks: {t:.4f} toggles per bit between consecutive chunks")
# 2) consecutive chunks from two different flows (any interleaving of independent flows)
for W in (32, 64):
    nw = W // 4
    ch = imgs.reshape(1024, -1, nw)
    n = 200000
    a, b = rng.integers(0, 1024, n), rng.integers(0, 1024, n)
    keep = a != b
    a, b = a[keep], b[keep]
    ia, ib = rng.integers(0, ch.shape[1], len(a)), rng.integers(0, ch.shape[1], len(a))
    x = np.bitwise_xor(ch[a, ia], ch[b, ib])
    t = np.unpackbits(x.view(np.uint8), axis=-1).sum() / (x.size * 32)
    out[f"indep_W{W}"] = float(t)
    print(f"chunks from two different flows, {W} B: {t:.4f}")
# 3) per bit position within a 32-bit word, one flow, 32 B chunks
ch = imgs.reshape(1024, -1, 8)
x = np.bitwise_xor(ch, np.roll(ch, -1, axis=1)).reshape(-1)
per = np.array([((x >> b) & 1).mean() for b in range(32)])
print("per-bit toggle prob (32 B chunks, one flow): sign %.3f; exponent bits 30..23: %s; mantissa mean %.4f (min %.4f max %.4f)" % (
    per[31], np.round(per[30:22:-1], 3).tolist(), per[:23].mean(), per[:23].min(), per[:23].max()))
out["per_bit_W32"] = per.tolist()
ones = np.array([((imgs.reshape(-1) >> b) & 1).mean() for b in range(32)])
print("per-bit ones density: sign %.3f exponent %s mantissa mean %.3f" % (ones[31], np.round(ones[30:22:-1], 3).tolist(), ones[:23].mean()))
# 4) two in-flight 1 KB loads of the same minion interleaved line by line: A_k, B_k, A_k+1 ... with B = A + 1 KB
#    (the image has a 512 B period, so A_k == B_k)
ch = imgs.reshape(1024, -1, 16)   # 64 B lines, 512 lines per slot
A = ch[:, 0:16]; B = ch[:, 16:32]
seq = np.stack([A, B], axis=2).reshape(1024, 32, 16)
x = np.bitwise_xor(seq[:, :-1], seq[:, 1:])
t = np.unpackbits(x.view(np.uint8), axis=-1).sum() / (x.size * 32)
out["lockstep_pair_W64"] = float(t)
print(f"two loads of one minion interleaved line by line (64 B flits): {t:.4f}")
json.dump(out, open('toggles.json', 'w'), indent=1)
