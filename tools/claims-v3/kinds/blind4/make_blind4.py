#!/usr/bin/env python3
"""Q137(m) blind pool 4: 25 operand tile pairs (11 fp32, 7 fp16, 7 int8) for the ET-SoC-1 power experiment.

    python3 tools/claims-v3/kinds/blind4/make_blind4.py            # write tiles/, blind4.json, SHA256SUMS
    python3 tools/claims-v3/kinds/blind4/make_blind4.py --check    # rebuild in memory, compare with disk

Every tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), packed by `make_kinds.encode` (or
`make_kinds.from_words` for tiles defined on the 32-bit lane-operand words), and described by
`make_kinds.tile_stats`.  The layout, stream order and gate rule are the ones in `../README.md`.

Deterministic: one fixed seed, derived per tile by sha256 of its name, so any tile can be rebuilt alone.
The real-model tiles read only the small 16x16-word cuts committed in `real/` (float32 .npy, exact copies of
the source fp16 / bf16 values) and `real/provenance.json`; the model files themselves are not in the repo.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import make_kinds as mk  # noqa: E402

SEED = 20261102
N = 16
TILES = []   # (name, type, case, priority, rule, builder)


def tile(name, type_name, case, priority, rule):
    def deco(fn):
        TILES.append((name, type_name, case, priority, rule, fn))
        return fn
    return deco


def seed_tag(name):
    return int.from_bytes(hashlib.sha256(f"blind4/{name}".encode()).digest()[:8], "little")


def rng_for(name):
    return np.random.default_rng([SEED, seed_tag(name)])


def f32_from_bits(bits):
    return np.asarray(bits, dtype=np.uint32).view(np.float32)


def wide_exp_f32(rng, shape, lo=-120, hi=120):
    """Random sign, exponent uniform over 2^lo..2^hi, random 23-bit mantissa: every exponent field busy."""
    sign = rng.integers(0, 2, shape).astype(np.uint32) << np.uint32(31)
    exp = (rng.integers(lo, hi + 1, shape) + 127).astype(np.uint32) << np.uint32(23)
    mant = rng.integers(0, 1 << 23, shape).astype(np.uint32)
    return f32_from_bits(sign | exp | mant)


def real(name):
    return np.load(os.path.join(HERE, "real", f"{name}.npy"))


PROV = None


def prov():
    global PROV
    if PROV is None:
        with open(os.path.join(HERE, "real", "provenance.json")) as f:
            PROV = json.load(f)
    return PROV


def quant_sym(x, max_abs):
    """Symmetric int8 quantisation: scale = max_abs / 127, q = clip(round_half_even(x / scale), -127, 127)."""
    scale = max_abs / 127.0
    return np.clip(np.round(np.asarray(x, dtype=np.float64) / scale), -127, 127), scale


# ====================================================================== fp32 (K = 16)
@tile("fp32.cancel_pairs", "fp32", "1 signs on moving sums", 1,
      "randn; A[i][2m+1] = A[i][2m] and B[2m+1][j] = -B[2m][j], so every k-pair adds exactly zero to C")
def _(rng):
    a = rng.standard_normal((N, 8))
    b = rng.standard_normal((8, N))
    A = np.repeat(a, 2, axis=1)
    B = np.empty((N, N))
    B[0::2], B[1::2] = b, -b
    return A, B


@tile("fp32.sign_drift", "fp32", "1 signs on moving sums", 1,
      "abs(randn) with one random sign s_k per k shared by A column k and B line k: every product positive, C only grows")
def _(rng):
    s = np.where(rng.integers(0, 2, N) == 1, 1.0, -1.0)
    A = np.abs(rng.standard_normal((N, N))) * s[None, :]
    B = np.abs(rng.standard_normal((N, N))) * s[:, None]
    return A, B


@tile("fp32.wideexp_bgate_alt", "fp32", "2 spread exponents under a gate", 1,
      "random sign, exponent 2^-120..2^120, random mantissa; B columns 8-15 all +0.0, so every lane alternates "
      "a wide-exponent word with zero each cycle (half the slots gated)")
def _(rng):
    A = wide_exp_f32(rng, (N, N))
    B = wide_exp_f32(rng, (N, N))
    B[:, 8:] = 0.0
    return A, B


@tile("fp32.wideexp_agate_rows", "fp32", "2 spread exponents under a gate", 2,
      "wide-exponent words (2^-120..2^120) both sides; A rows 2,5,8,11,14 all zero (whole micro-ops gated) and "
      "20% of B words zero at random")
def _(rng):
    A = wide_exp_f32(rng, (N, N))
    B = wide_exp_f32(rng, (N, N))
    A[[2, 5, 8, 11, 14], :] = 0.0
    B[rng.random((N, N)) < 0.2] = 0.0
    return A, B


@tile("fp32.denormals_only", "fp32", "own choice (surprise)", 1,
      "every word an fp32 subnormal: exponent field 0, random nonzero 23-bit mantissa, random sign; no word is "
      "zero so nothing gates, but a flush-to-zero datapath sees only zeros")
def _(rng):
    def sub(shape):
        sign = rng.integers(0, 2, shape).astype(np.uint32) << np.uint32(31)
        mant = rng.integers(1, 1 << 23, shape).astype(np.uint32)
        return f32_from_bits(sign | mant)
    return sub((N, N)), sub((N, N))


@tile("fp32.a_const_b_busy", "fp32", "3 A with a busy partner", 1,
      "A every element 1.5 (0x3FC00000, A never changes), B standard normal")
def _(rng):
    return np.full((N, N), 1.5), rng.standard_normal((N, N))


@tile("fp32.a_exp_busy_b_const", "fp32", "3 A with a busy partner", 2,
      "A = random sign * 2^U{-60..60}, mantissa 0 (only sign and exponent fields move); B every element 0.75")
def _(rng):
    A = np.where(rng.integers(0, 2, (N, N)) == 1, 1.0, -1.0) * 2.0 ** rng.integers(-60, 61, (N, N))
    return A, np.full((N, N), 0.75)


@tile("fp32.b_3of8_k", "fp32", "4 partial sparsity", 1,
      "A randn dense; B randn with N:M sparsity 3:8 along k: in each column, 3 of every 8 k-lines nonzero "
      "(62.5% of B words zero)")
def _(rng):
    A = rng.standard_normal((N, N))
    B = rng.standard_normal((N, N))
    for j in range(N):
        for g in range(2):
            keep = rng.permutation(8)[:3]
            m = np.ones(8, bool)
            m[keep] = False
            B[g * 8:(g + 1) * 8, j][m] = 0.0
    return A, B


@tile("fp32.rowcol_sparse", "fp32", "4 partial sparsity", 2,
      "randn; A rows 1,4,7,10,13 zero (31.25%); B columns 2 and 10 zero (lane 2 gated on both half-passes) "
      "and column 5 zero (its partner 13 is not)")
def _(rng):
    A = rng.standard_normal((N, N))
    B = rng.standard_normal((N, N))
    A[[1, 4, 7, 10, 13], :] = 0.0
    B[:, [2, 10, 5]] = 0.0
    return A, B


@tile("fp32.real_pythia_embed_qkv", "fp32", "5 real model", 1,
      "pythia-70m: A = token embeddings (rows 100-115, dims 0-15), B = layer-2 query_key_value weight "
      "W[0:16, 0:16] transposed (head 0's query rows); fp16 source values, exact in fp32")
def _(rng):
    return real("pythia_embed_r100_c0_16x16"), real("pythia_qkv_r0_c0_16x16T")


@tile("fp32.real_qwen_q_down", "fp32", "5 real model", 1,
      "Qwen2.5-0.5B: A = layer-12 q_proj weight rows 128-143, cols 0-15; B = layer-0 mlp.down_proj "
      "W[0:16, 2048:2064] transposed; bf16 source values, exact in fp32 (low 16 mantissa bits zero)")
def _(rng):
    return real("qwen_qproj_r128_c0_16x16"), real("qwen_down_r0_c2048_16x16T")


# ====================================================================== fp16 (K = 32)
@tile("fp16.pair_cancel", "fp16", "1 signs on moving sums", 1,
      "randn; both halves of every A word equal (a1 = a2) and B[2w+1][j] = -B[2w][j]: every two-term update "
      "a1*b1 + a2*b2 is exactly zero, yet no lane gates and no update is dropped")
def _(rng):
    a = rng.standard_normal((N, 16))
    b = rng.standard_normal((16, N))
    A = np.repeat(a, 2, axis=1)
    B = np.empty((32, N))
    B[0::2], B[1::2] = b, -b
    return A, B


@tile("fp16.wideexp_gate30", "fp16", "2 spread exponents under a gate", 1,
      "fp16 bit patterns: random sign, exponent field uniform 1..30 (2^-14..2^15) with 10% subnormals, random "
      "mantissa; 30% of the 32-bit words zeroed on each side")
def _(rng):
    def side():
        sh = (N, N, 2)
        sign = rng.integers(0, 2, sh).astype(np.uint32) << np.uint32(15)
        exp = rng.integers(1, 31, sh).astype(np.uint32)
        exp[rng.random(sh) < 0.1] = 0
        mant = rng.integers(1, 1 << 10, sh).astype(np.uint32)
        h = sign | (exp << np.uint32(10)) | mant
        w = h[..., 0] | (h[..., 1] << np.uint32(16))           # element 0 in the low half
        w[rng.random((N, N)) < 0.3] = 0
        return w.astype(np.uint64)
    return ("words", side(), side())


@tile("fp16.a_hi_busy_lo_const", "fp16", "3 A with a busy partner", 1,
      "A: even k (the low half of each word) = 1.0, odd k (the high half) randn; B randn")
def _(rng):
    A = rng.standard_normal((N, 32))
    A[:, 0::2] = 1.0
    return A, rng.standard_normal((32, N))


@tile("fp16.block_sparse_37", "fp16", "4 partial sparsity", 1,
      "randn; the 16x16 word grid in 4x4-word blocks: 6 of B's 16 blocks zero (37.5%), 3 of A's (18.75%)")
def _(rng):
    A = rng.standard_normal((N, 32))
    B = rng.standard_normal((32, N))
    for blk in rng.permutation(16)[:3]:
        bi, bw = divmod(int(blk), 4)
        A[bi * 4:(bi + 1) * 4, bw * 8:(bw + 1) * 8] = 0.0     # 4 words = 8 elements along k
    for blk in rng.permutation(16)[:6]:
        bp, bj = divmod(int(blk), 4)
        B[bp * 8:(bp + 1) * 8, bj * 4:(bj + 1) * 4] = 0.0     # 4 lines = 8 k, 4 columns
    return A, B


@tile("fp16.band_local", "fp16", "4 partial sparsity", 2,
      "randn; A word (i, w) nonzero only where abs(i - w) <= 1 (46 of 256), B word (p, j) only where abs(p - j) <= 3 "
      "(100 of 256): local-attention bands on both sides")
def _(rng):
    A = rng.standard_normal((N, 32))
    B = rng.standard_normal((32, N))
    for i in range(N):
        for w in range(N):
            if abs(i - w) > 1:
                A[i, 2 * w:2 * w + 2] = 0.0
    for p in range(N):
        for j in range(N):
            if abs(p - j) > 3:
                B[2 * p:2 * p + 2, j] = 0.0
    return A, B


@tile("fp16.real_pythia_embed_qkv", "fp16", "5 real model", 1,
      "pythia-70m: A = token embeddings rows 200-215, dims 64-95; B = layer-2 query_key_value W[512:528, 64:96] "
      "transposed (GPT-NeoX interleaves q,k,v per head: these are head 2's value rows); fp16 source values, "
      "stored exactly")
def _(rng):
    return real("pythia_embed_r200_c64_16x32"), real("pythia_qkv_r512_c64_16x32T")


@tile("fp16.real_qwen_ln_down", "fp16", "5 real model", 1,
      "Qwen2.5-0.5B: A = layer-12 input_layernorm gains 0-511 laid out 16x32 (values near 1, a few up to 6.7); "
      "B = layer-0 mlp.down_proj W[400:416, 300:332] transposed; bf16 rounded to fp16 (nearest-even)")
def _(rng):
    return real("qwen_ln12_0_512_as16x32"), real("qwen_down_r400_c300_16x32T")


# ====================================================================== int8 (K = 64)
@tile("int8.sign_runs_i", "int8", "1 signs on moving sums", 1,
      "magnitudes 1..20 (abs(round(6*randn)), zeros bumped to 1); A sign constant down each A column for runs of 8 "
      "rows (i 0-7, 8-15), random per run and k; B uniform -128..127")
def _(rng):
    mag = np.maximum(np.abs(np.round(6.0 * rng.standard_normal((N, 64)))), 1.0)
    mag = np.minimum(mag, 20.0)
    s = np.where(rng.integers(0, 2, (2, 64)) == 1, 1.0, -1.0)
    sign = np.repeat(s, 8, axis=0)
    return mag * sign, rng.integers(-128, 128, (64, N)).astype(np.float64)


@tile("int8.a_full_b_const", "int8", "3 A with a busy partner", 1,
      "A uniform -128..127; B every byte 0x5A (+90): B nonzero and never changing")
def _(rng):
    return rng.integers(-128, 128, (N, 64)).astype(np.float64), np.full((64, N), 90.0)


@tile("int8.pair_gate_37", "int8", "4 partial sparsity", 1,
      "A uniform -128..127 dense; B uniform with column pairs (1,9), (4,12), (6,14) all zero (exactly 3/8 of "
      "int8's gate decisions off) and column 3 zero alone (its partner 11 live, so it never gates)")
def _(rng):
    A = rng.integers(-128, 128, (N, 64)).astype(np.float64)
    B = rng.integers(-128, 128, (64, N)).astype(np.float64)
    B[:, [1, 9, 4, 12, 6, 14, 3]] = 0.0
    return A, B


@tile("int8.band_a", "int8", "4 partial sparsity", 2,
      "A uniform -128..127 only in words (i, w) with abs(i - w) <= 2 (74 of 256), else zero; B 2:4 byte sparsity "
      "(two random bytes of every 4-byte word zero), which never gates in int8")
def _(rng):
    A = rng.integers(-128, 128, (N, 64)).astype(np.float64)
    for i in range(N):
        for w in range(N):
            if abs(i - w) > 2:
                A[i, 4 * w:4 * w + 4] = 0.0
    B = rng.integers(-128, 128, (64, N)).astype(np.float64)
    B[B == 0] = 1.0
    for p in range(N):
        for j in range(N):
            z = rng.permutation(4)[:2]
            B[4 * p + z, j] = 0.0
    return A, B


@tile("int8.b_line_flipflop", "int8", "own choice (surprise)", 1,
      "A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0xFF = -1 "
      "(odd k-groups): at every line boundary all 512 B bits flip at once")
def _(rng):
    A = rng.integers(-128, 128, (N, 64)).astype(np.float64)
    B = np.zeros((64, N))
    for p in range(1, N, 2):
        B[4 * p:4 * p + 4, :] = -1.0
    return A, B


@tile("int8.real_pythia_embed_mlpout", "int8", "5 real model", 1,
      "pythia-70m: A = token embeddings rows 40-55, dims 128-191, symmetric int8 with a per-cut scale "
      "max(abs(cut))/127; B = layer-4 mlp.dense_4h_to_h W[32:48, 1000:1064] transposed, symmetric per-tensor "
      "(scale max(abs(W))/127 over the whole tensor)")
def _(rng):
    a = real("pythia_embed_r40_c128_16x64")
    qa, _ = quant_sym(a, float(np.max(np.abs(a))))
    mx = prov()["cuts"]["pythia_mlpout_r32_c1000_16x64T"]["per_tensor_max_abs"]
    qb, _ = quant_sym(real("pythia_mlpout_r32_c1000_16x64T"), mx)
    return qa, qb


@tile("int8.real_qwen_q_down", "int8", "5 real model", 1,
      "Qwen2.5-0.5B: A = layer-12 q_proj rows 700-715, cols 64-127; B = layer-0 mlp.down_proj W[100:116, "
      "4000:4064] transposed; each symmetric per-tensor int8 (scale max(abs(W))/127 over its whole tensor)")
def _(rng):
    c = prov()["cuts"]
    qa, _ = quant_sym(real("qwen_qproj_r700_c64_16x64"), c["qwen_qproj_r700_c64_16x64"]["per_tensor_max_abs"])
    qb, _ = quant_sym(real("qwen_down_r100_c4000_16x64T"), c["qwen_down_r100_c4000_16x64T"]["per_tensor_max_abs"])
    return qa, qb


# ====================================================================== build
REAL_CUTS = {
    "fp32.real_pythia_embed_qkv": ["pythia_embed_r100_c0_16x16", "pythia_qkv_r0_c0_16x16T"],
    "fp32.real_qwen_q_down": ["qwen_qproj_r128_c0_16x16", "qwen_down_r0_c2048_16x16T"],
    "fp16.real_pythia_embed_qkv": ["pythia_embed_r200_c64_16x32", "pythia_qkv_r512_c64_16x32T"],
    "fp16.real_qwen_ln_down": ["qwen_ln12_0_512_as16x32", "qwen_down_r400_c300_16x32T"],
    "int8.real_pythia_embed_mlpout": ["pythia_embed_r40_c128_16x64", "pythia_mlpout_r32_c1000_16x64T"],
    "int8.real_qwen_q_down": ["qwen_qproj_r700_c64_16x64", "qwen_down_r100_c4000_16x64T"],
}


def build_one(name, type_name, fn):
    out = fn(rng_for(name))
    if isinstance(out, tuple) and len(out) == 3 and out[0] == "words":
        raw = mk.from_words(out[1], out[2])
        return raw, None
    A, B = out
    E, size, dtype, K = mk.TYPES[type_name]
    raw = mk.encode(A, B, type_name)
    # the tile must decode back to the intended elements (after the type's own rounding)
    da, db = mk.decode(raw, type_name)
    ia = np.asarray(A).astype(dtype)
    ib = np.asarray(B).astype(dtype)
    assert ia.tobytes() == da.tobytes() and ib.tobytes() == db.tobytes(), name
    if type_name == "int8":
        assert np.all(np.asarray(A) == np.round(A)) and np.all(np.abs(A) <= 128), name
    return raw, (A, B)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build_all():
    files, entries = {}, []
    for name, type_name, case, prio, rule, fn in TILES:
        raw, _ = build_one(name, type_name, fn)
        assert len(raw) == 2048
        path = f"tiles/{type_name}/{name}.bin"
        files[path] = raw
        st = mk.tile_stats(raw, type_name)
        e = {"name": name, "file": path, "type": type_name, "case": case, "rule": rule,
             "seed": {"base": SEED, "tag": seed_tag(name),
                      "rng": "numpy default_rng([base, tag]), tag = first 8 bytes (LE) of sha256('blind4/<name>')"},
             "sha256": {"whole": sha(raw), "a": sha(raw[:1024]), "b": sha(raw[1024:])},
             "priority": prio, "stats": st}
        if name in REAL_CUTS:
            e["real_cuts"] = REAL_CUTS[name]
            e["seed"]["used"] = False
        entries.append(e)
    names = [e["name"] for e in entries]
    assert len(set(names)) == len(names)
    counts = {t: sum(1 for e in entries if e["type"] == t) for t in ("fp32", "fp16", "int8")}
    doc = {
        "title": "Q137(m) blind pool 4",
        "date": "2026-11-02",
        "written_by": "an independent designer who never saw the model",
        "format": "2,048 bytes a tile: raw A (1,024 B) then raw B (1,024 B), in the type's layout "
                  "(make_kinds.encode); stats from make_kinds.tile_stats",
        "generator": "make_blind4.py",
        "counts": {"tiles": len(entries), **counts,
                   "priority1": sum(1 for e in entries if e["priority"] == 1),
                   "priority2": sum(1 for e in entries if e["priority"] == 2)},
        "real_provenance": "real/provenance.json",
        "tiles": entries,
    }
    files["blind4.json"] = (json.dumps(doc, indent=1, sort_keys=False) + "\n").encode()
    return files, doc


def sums_text(file_bytes):
    lines = [f"{sha(b)}  {p}" for p, b in sorted(file_bytes.items())]
    return ("\n".join(lines) + "\n").encode()


def disk_files_for_sums(built):
    """Every file in blind4/ except SHA256SUMS: the built ones from memory, the rest (README, generator,
    real/) from disk."""
    out = dict(built)
    for root, dirs, fnames in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fnames:
            rel = os.path.relpath(os.path.join(root, f), HERE)
            if rel == "SHA256SUMS" or rel in out or f.endswith(".pyc"):
                continue
            with open(os.path.join(root, f), "rb") as fh:
                out[rel] = fh.read()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    built, doc = build_all()
    if args.check:
        bad = 0
        for p, b in built.items():
            fp = os.path.join(HERE, p)
            ok = os.path.exists(fp) and open(fp, "rb").read() == b
            if not ok:
                print("MISMATCH", p); bad += 1
        on_disk = set()
        for root, dirs, fnames in os.walk(os.path.join(HERE, "tiles")):
            for f in fnames:
                on_disk.add(os.path.relpath(os.path.join(root, f), HERE))
        extra = on_disk - set(built)
        for p in sorted(extra):
            print("EXTRA", p); bad += 1
        want = sums_text(disk_files_for_sums(built))
        have = open(os.path.join(HERE, "SHA256SUMS"), "rb").read() if os.path.exists(
            os.path.join(HERE, "SHA256SUMS")) else b""
        if want != have:
            print("MISMATCH SHA256SUMS"); bad += 1
        print(f"check: {len(built)} built files, {bad} problems")
        sys.exit(1 if bad else 0)
    for p, b in built.items():
        fp = os.path.join(HERE, p)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(b)
    with open(os.path.join(HERE, "SHA256SUMS"), "wb") as f:
        f.write(sums_text(disk_files_for_sums(built)))
    for e in doc["tiles"]:
        s = e["stats"]
        print(f"{e['name']:32s} p{e['priority']} gated {100 * s['gated_lane_frac']:6.2f}%  "
              f"bus/op {s['bus_bits_per_op']:7d}  {e['sha256']['whole'][:12]}")
    print(doc["counts"])


if __name__ == "__main__":
    main()
