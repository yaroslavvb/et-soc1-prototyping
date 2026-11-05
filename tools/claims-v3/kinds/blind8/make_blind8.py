#!/usr/bin/env python3
"""Q142(d): blind pool 8's generator.  DESIGN.md beside this file is the design; this file is the code it describes.

    python3 -I make_blind8.py seed                              # the seed, its rule and its value
    python3 -I make_blind8.py fetch --dl DIR [--depth 6]        # network: the two public checkpoints' bytes, into DIR
    python3 -I make_blind8.py build --dl DIR --out POOL         # the pool, from DIR and the committed pools only
    python3 -I make_blind8.py build --dl DIR --test             # a dry run on a test seed: builds in memory, writes nothing
    python3 -I make_blind8.py check --out POOL                  # re-derive every label and class from the tile bytes

Run it with `python3 -I` (isolated: no user site, no script directory on sys.path), because `build` reads downloaded
bytes.  Downloaded bytes are parsed only as JSON (config.json, tokenizer.json, the safetensors header) and as raw
little-endian arrays; nothing is unpickled.  `build` never touches the network.

Tiles are made with tools/claims-v3/kinds/make_kinds.py (`encode`, `decode`, `words_of`, `from_words`, `tile_stats`),
loaded from its file.  Every tile is 2,048 bytes, the A tile then the B tile, in make_kinds' layout, for
`sparsity_host --test fma --type <fmt> --values file:<tile>`.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import struct
import subprocess
import sys
import time
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_DEFAULT = os.path.dirname(HERE)                  # tools/claims-v3/kinds

# ------------------------------------------------------------------ the seed: a value this design cannot choose
SEED_COMMIT = "c996d1357609c10009c80e59dd8e85bcc652343f"   # lab commit named by the round, before this design
SEED_RULE = "int(sha256(ascii of the 40-hex commit string).hexdigest()[:16], 16)"
SEED = int(hashlib.sha256(SEED_COMMIT.encode("ascii")).hexdigest()[:16], 16)
assert SEED == 0x1DA1FDE559D92805 == 2135266859847067653
TEST_SEED = int(hashlib.sha256(b"blind8 dry run, never the pool").hexdigest()[:16], 16)

EARLIER = ("blind3", "blind4", "blind5", "blind6", "blind7")   # the committed pools every tile is hashed against
RERUN_FROM = ("blind6", "blind7")
FORMATS = ("fp32", "fp16", "int8")
ONE = {"fp32": 0x3F800000, "fp16": 0x3C003C00}                # the 1.0 word
FP16_MAX = 60000.0

# ------------------------------------------------------------------ quotas (the round's) and this pool's plan
QUOTA = {
    "S": "at least 8 single high B bits at new bit positions and base words (fp32 and fp16)",
    "U": "at least 12 kinds from the generator aimed at no named class",
    "R": "at least 8 real tiles from two or more public models used in no earlier pool, int8 W8A8 outlier "
         "activations among them",
    "LH": "at least 6 int8 whole-line or held-B tiles",
    "0": "two random anchors per format plus a check anchor per format",
    "rerun": "about 12 re-runs of pool 6/7 float tiles under their own labels (scored apart), chosen by a rule "
             "from their bytes and the seed so that they span the range of the data term",
}
QUOTA_MIN = {"S": 8, "U": 12, "R": 8, "LH": 6, "0": 9, "rerun": 11}
S_STRATA = {   # (stratum, candidate bit positions, picks); positions used by any earlier single-bit tile are removed
    "fp32": [("mant_hi", list(range(16, 23)), 2), ("mant_mid", list(range(8, 16)), 2),
             ("mant_lo", list(range(0, 8)), 1), ("exp_sign", list(range(23, 29)) + [31], 1)],
    "fp16": [("mant_hi", [7, 8, 9], 1), ("mant_lo", list(range(0, 7)), 2), ("exp_sign", [10, 11, 12, 15], 1)],
}
S_BASE_EXP = {"fp32": (124, 130), "fp16": (13, 17)}           # the base word's biased exponent, drawn uniformly
S_WINDOW = {"fp32": (2.0 ** -40, 2.0 ** 40), "fp16": (2.0 ** -10, 2.0 ** 10)}   # |base| and |flipped| must lie in it
S_VARIANT = ("fp32", "mant_mid", 1)                            # this pick holds A at a seeded constant, not 1.0
U_FLOAT = ("tdist", "lognorm", "mixture", "uniform", "expo", "grid", "rowscale", "sparse", "ar_i", "ar_k",
           "bimodal", "cauchy")
U_INT8 = ("tq", "geom", "urange", "biased", "sparseq", "pm", "ar_k", "relu_tq")
U_COUNT = {"fp32": 5, "fp16": 4, "int8": 4}
RERUN_COUNT = {"fp32": 8, "fp16": 4}
DEPTH = 6                                                      # layers 0-5 run; cuts come from layers 1-5

CLASS_AIM = {
    "0": "Anchors. Two random anchors per format (pool 7's rules: standard normal floats, uniform -128..127 int8) for "
         "the session's own scale, a third draw of the same rule held out as the check anchor (role `check`), and the "
         "all-zero tile kept under pool 7's own label as the floor.",
    "S": "Single high B bits: A one constant word, B alternating every cycle between a base word (columns 0-7) and "
         "the same word with one bit flipped (columns 8-15), so each lane's B operand toggles that one bit and nothing "
         "else moves. New bit positions (mantissa high, middle and low, and one exponent-or-sign bit per format) and "
         "new base words, drawn by the seed.",
    "U": "Kinds aimed at no named class: whole-tile value distributions (heavy tails, log-normal magnitudes, mixtures, "
         "grids, per-row scales, sparsity, correlation along the stream, bimodal values), the families and their "
         "parameters drawn by the seed from a fixed menu.",
    "L": "int8 whole lines: A random over the full range, B built from two or three distinct 64-byte lines that "
         "change as a whole at k-group boundaries, in new patterns (k-bit flips per byte, a change every second "
         "boundary, a three-line cycle, half the words of a line changing).",
    "H": "int8 held B: A random over the full range, every B line identical, at held values and lines no earlier "
         "pool held.",
    "R": "Real tiles: operands cut from two public W8A8 checkpoints no earlier pool used, run on a public-domain text: "
         "int8 per-token-quantised activations (blocks holding the activation outliers) against the checkpoints' own "
         "int8 weights, and float attention, query-key and dequantised-weight operands.",
    "rerun": "Re-runs: pool 6 and pool 7 float tiles, byte for byte, under their own labels and classes, chosen from "
             "their bytes and the seed to span the range of the operand-toggle count; scored apart from the new tiles.",
}


# ------------------------------------------------------------------ small helpers
def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    with open(p, "rb") as f:
        return sha(f.read())


def rng(seed, *tag):
    """One independent stream per tag, from the one seed (make_kinds.rng_for's scheme)."""
    t = "blind8/" + "/".join(str(x) for x in tag)
    return np.random.default_rng([seed, int.from_bytes(hashlib.sha256(t.encode()).digest()[:8], "little")])


def rank(seed, *tag):
    """A seeded ordering key: sort by it to choose without a hand."""
    return hashlib.sha256((f"{seed}/" + "/".join(str(x) for x in tag)).encode()).hexdigest()


def load_make_kinds(kinds):
    p = os.path.join(kinds, "make_kinds.py")
    spec = importlib.util.spec_from_file_location("make_kinds", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, sha_file(p)


def read_manifest(path):
    rows = []
    with open(path) as f:
        for line in f:
            x = line.split()
            if len(x) < 8:
                continue
            rows.append({"sha": x[0], "file": x[1], "label": x[2], "fmt": x[3], "case": x[4].split("=", 1)[1],
                         "prio": x[5], "role": x[6], "flag": x[7]})
    return rows


def git(*args, cwd):
    r = subprocess.run(["git", "-C", cwd] + list(args), capture_output=True, text=True, timeout=60)
    return r.stdout.strip() if r.returncode == 0 else None


# ------------------------------------------------------------------ the committed pools (blind3-blind7)
def scan_earlier(kinds):
    """Every tile file of the committed pools, with its label (the pool's MANIFEST label where there is one, else
    `<fmt>.<file stem>`), its bytes and sha256; and each pool's SHA256SUMS agreement."""
    tiles, sums = [], {}
    for pool in EARLIER:
        man = {}
        mp = os.path.join(kinds, pool, "MANIFEST")
        if os.path.exists(mp):
            for row in read_manifest(mp):
                man[row["file"]] = row
        listed = {}
        sp = os.path.join(kinds, pool, "SHA256SUMS")
        if os.path.exists(sp):
            with open(sp) as f:
                for line in f:
                    x = line.split()
                    if len(x) == 2:
                        listed[x[1]] = x[0]
        agree = disagree = 0
        for fmt in FORMATS:
            d = os.path.join(kinds, pool, "tiles", fmt)
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".bin"):
                    continue
                rel = f"tiles/{fmt}/{fn}"
                with open(os.path.join(d, fn), "rb") as f:
                    raw = f.read()
                h = sha(raw)
                if rel in listed:
                    agree += listed[rel] == h
                    disagree += listed[rel] != h
                stem = fn[:-4]
                label = man[rel]["label"] if rel in man else (stem if stem.startswith(fmt + ".") else f"{fmt}.{stem}")
                if rel in man and man[rel]["sha"] != h:
                    raise SystemExit(f"{pool}/{rel}: MANIFEST sha256 differs from the file")
                tiles.append({"pool": pool, "fmt": fmt, "file": rel, "label": label, "sha": h, "raw": raw,
                              "manifest": man.get(rel)})
        sums[pool] = {"tiles": sum(1 for t in tiles if t["pool"] == pool), "sha256sums_agree": agree,
                      "sha256sums_disagree": disagree}
    return tiles, sums


# ------------------------------------------------------------------ structure read from the bytes
def one_bit(d, fmt):
    """The bit position if the XOR of two words is one bit (fp32) or the same one bit in both halves (fp16)."""
    if fmt == "fp32":
        return d.bit_length() - 1 if d and d & (d - 1) == 0 else None
    h, lo = d >> 16, d & 0xFFFF
    return lo.bit_length() - 1 if lo and h == lo and lo & (lo - 1) == 0 else None


def single_bit_b(raw, fmt, mk):
    """A single-high-B-bit tile: A one word everywhere; B columns 0-7 one word and columns 8-15 another, in every
    line, the two differing in one bit (per element).  Each lane then alternates between the two every cycle."""
    if fmt not in ONE:
        return None
    aw, bw = mk.words_of(raw)
    a = {int(x) for x in aw.ravel()}
    lo = {int(x) for x in bw[:, :8].ravel()}
    hi = {int(x) for x in bw[:, 8:].ravel()}
    if len(a) != 1 or len(lo) != 1 or len(hi) != 1:
        return None
    w0, w1 = lo.pop(), hi.pop()
    bit = one_bit(w0 ^ w1, fmt)
    if bit is None:
        return None
    return {"side": "B", "bit": bit, "base": w0, "flipped": w1, "a_word": a.pop()}


def single_bit_any(raw, fmt, mk):
    """single_bit_b, or its A-side mirror (B one word, A exactly two words differing in one bit): used only to list
    the bit positions and words earlier pools already used."""
    s = single_bit_b(raw, fmt, mk)
    if s or fmt not in ONE:
        return s
    aw, bw = mk.words_of(raw)
    b = {int(x) for x in bw.ravel()}
    a = sorted({int(x) for x in aw.ravel()})
    if len(b) == 1 and len(a) == 2:
        bit = one_bit(a[0] ^ a[1], fmt)
        if bit is not None:
            return {"side": "A", "bit": bit, "base": a[0], "flipped": a[1], "b_word": b.pop()}
    return None


def int8_lines(raw):
    """The B tile as 16 lines of 64 bytes (one line per k-group): distinct lines, the shortest period p with
    line[i] == line[i + p], the boundaries (cyclic, 16) where the line changes, and the one byte value if B is one."""
    B = raw[1024:]
    lines = [B[64 * p:64 * (p + 1)] for p in range(16)]
    period = next(p for p in range(1, 17) if all(lines[i] == lines[i + p] for i in range(16 - p)))
    vals = set(B)
    return {"distinct": len(set(lines)), "period": period,
            "changes": sum(1 for p in range(16) if lines[p] != lines[(p + 1) % 16]),
            "byte": next(iter(vals)) if len(vals) == 1 else None, "lines": lines}


def structure(raw, fmt, mk):
    """'S' single high B bit; 'H' int8 with every B line identical; 'L' int8 with two to four distinct B lines;
    'G' anything else."""
    if fmt in ONE:
        return "S" if single_bit_b(raw, fmt, mk) else "G"
    info = int8_lines(raw)
    if info["distinct"] == 1:
        return "H"
    if 2 <= info["distinct"] <= 4:
        return "L"
    return "G"


def byte_sig(raw, fmt, cls, mk):
    """The part of a label computed from the 2,048 bytes.  S: b<bit>_<base word hex>[_A<A word hex> when A is not
    1.0]; H: v<byte hex> when B is one byte value, else line<4 hex of sha256 of line 0>; L: d<distinct lines>
    p<period>c<changing boundaries>_<4 hex of the tile's sha256>; every other tile: 6 hex of the tile's sha256."""
    if cls == "S":
        s = single_bit_b(raw, fmt, mk)
        sig = f"b{s['bit']}_{s['base']:08x}"
        if s["a_word"] != ONE[fmt]:
            sig += f"_A{s['a_word']:08x}"
        return sig
    if cls == "H":
        i = int8_lines(raw)
        return f"v{i['byte']:02x}" if i["byte"] is not None else f"line{sha(i['lines'][0])[:4]}"
    if cls == "L":
        i = int8_lines(raw)
        return f"d{i['distinct']}p{i['period']}c{i['changes']}_{sha(raw)[:4]}"
    return sha(raw)[:6]


def class_check(raw, fmt, cls, role, mk):
    """A class claim the bytes must bear out: S, H and L need their structure; every other class needs none of the
    three; anchors and the check anchor need their rule's moments."""
    st = structure(raw, fmt, mk)
    want = {"S": "S", "H": "H", "L": "L"}.get(cls, "G")
    if st != want:
        return False, f"bytes read as {st}, class {cls} needs {want}"
    if role in ("anchor", "check"):
        a, b = mk.decode(raw, fmt)
        for side, v in (("A", a), ("B", b)):
            v = v.astype(np.float64)
            if fmt == "int8":
                ok = 65.0 <= v.std() <= 85.0 and v.min() <= -120 and v.max() >= 120
            else:
                ok = abs(v.mean()) < 0.3 and 0.8 <= v.std() <= 1.2
            if not ok:
                return False, f"{side} side's moments are not its rule's"
    return True, "ok"


def tile_refusal(raw, fmt, mk):
    """None if the tile is admissible: 2,048 bytes, no NaN or Inf, and make_kinds.encode accepts its decoded elements
    and gives back exactly these bytes."""
    if len(raw) != 2048:
        return "not 2,048 bytes"
    a, b = mk.decode(raw, fmt)
    if fmt != "int8":
        if not (np.isfinite(a.astype(np.float64)).all() and np.isfinite(b.astype(np.float64)).all()):
            return "NaN or Inf"
    try:
        again = mk.encode(a, b, fmt)
    except Exception as e:                                     # noqa: BLE001 - a refusal of any kind refuses the tile
        return f"make_kinds.encode refuses it: {e!r}"
    if again != raw:
        return "make_kinds.encode does not give back these bytes"
    return None


# ------------------------------------------------------------------ anchors and the floor
def make_anchors(seed, mk):
    out = []
    for fmt in FORMATS:
        K = mk.TYPES[fmt][3]
        for name, role in (("a", "anchor"), ("b", "anchor"), ("check", "check")):
            r = rng(seed, "anchor", fmt, name)
            if fmt == "int8":
                A = r.integers(-128, 128, (16, K)).astype(np.float64)
                B = r.integers(-128, 128, (K, 16)).astype(np.float64)
                slot = "anchor8_check_full" if name == "check" else f"anchor8_full_{name}"
                rule = "A and B uniform over -128..127 (pool 7's int8 anchor rule) on stream anchor/int8/" + name
            else:
                A, B = r.standard_normal((16, K)), r.standard_normal((K, 16))
                slot = "anchor8_check_randn" if name == "check" else f"anchor8_randn_{name}"
                rule = (f"A and B standard normal{', rounded to fp16' if fmt == 'fp16' else ''} (pool 7's float anchor "
                        f"rule) on stream anchor/{fmt}/{name}")
            out.append({"fmt": fmt, "cls": "0", "role": role, "slot": slot, "raw": mk.encode(A, B, fmt), "rule": rule,
                        "params": {"stream": ["anchor", fmt, name]}})
    return out


def floor_tiles(earlier):
    """The all-zero tile of each format, kept under pool 7's own label (its bytes are pool 6's and 7's zeros)."""
    out = []
    for fmt in FORMATS:
        t = next(t for t in earlier if t["pool"] == "blind7" and t["label"] == f"{fmt}.anchor7_zeros")
        assert t["raw"] == bytes(2048), t["label"]
        out.append({"fmt": fmt, "cls": "0", "role": "anchor", "slot": None, "label": t["label"], "raw": t["raw"],
                    "rule": "the all-zero floor, byte for byte pool 7's tile under pool 7's label",
                    "params": {"from_pool": "blind7", "from_label": t["label"]}, "rerun_of": "blind7"})
    return out


# ------------------------------------------------------------------ S: single high B bits
def half_value(h):
    return float(np.frombuffer(struct.pack("<H", h), dtype="<f2")[0])


def make_s(seed, mk, used_bits, used_words):
    out = []
    for fmt, strata in S_STRATA.items():
        picks = []
        for name, cand, n in strata:
            avail = [b for b in cand if b not in used_bits[fmt]]
            chosen = rng(seed, "S", fmt, "bits", name).choice(avail, size=n, replace=False)
            picks += [(name, i, int(b), avail) for i, b in enumerate(chosen)]
        for name, i, bit, avail in picks:
            r = rng(seed, "S", fmt, "base", bit)
            lo_e, hi_e = S_BASE_EXP[fmt]
            for attempt in range(1000):
                sign, e = int(r.integers(0, 2)), int(r.integers(lo_e, hi_e + 1))
                if fmt == "fp32":
                    w0 = (sign << 31) | (e << 23) | int(r.integers(0, 1 << 23))
                    w1 = w0 ^ (1 << bit)
                    elems = [w0, w1]
                    exps = [(w >> 23) & 0xFF for w in elems]
                    vals = [struct.unpack("<f", struct.pack("<I", w))[0] for w in elems]
                    normal = all(0 < x < 255 for x in exps)
                else:
                    h0 = (sign << 15) | (e << 10) | int(r.integers(0, 1 << 10))
                    h1 = h0 ^ (1 << bit)
                    w0, w1 = (h0 << 16) | h0, (h1 << 16) | h1
                    elems = [h0, h1]
                    vals = [half_value(h) for h in elems]
                    normal = all(0 < ((h >> 10) & 0x1F) < 31 for h in elems)
                lo_w, hi_w = S_WINDOW[fmt]
                if normal and all(lo_w <= abs(v) <= hi_w for v in vals) and not ({w0, w1} & used_words):
                    break
            else:
                raise SystemExit(f"S {fmt} bit {bit}: no admissible base word in 1,000 draws")
            used_words |= {w0, w1}
            a_word = ONE[fmt]
            if (fmt, name, i) == S_VARIANT:
                ra = rng(seed, "S", fmt, "a", bit)
                a_word = (int(ra.integers(126, 129)) << 23) | int(ra.integers(0, 1 << 23))
            aw = np.full((16, 16), a_word, dtype=np.uint64)
            bw = np.empty((16, 16), dtype=np.uint64)
            bw[:, :8], bw[:, 8:] = w0, w1
            out.append({"fmt": fmt, "cls": "S", "role": "kind", "slot": "s8_onebit", "raw": mk.from_words(aw, bw),
                        "rule": (f"A every word 0x{a_word:08x}; B columns 0-7 0x{w0:08x}, columns 8-15 0x{w1:08x} "
                                 f"(bit {bit} flipped{' in both halves' if fmt == 'fp16' else ''}), every line"),
                        "params": {"stratum": name, "candidates": avail, "bit": bit, "base": f"0x{w0:08x}",
                                   "flipped": f"0x{w1:08x}", "a_word": f"0x{a_word:08x}", "base_draws": attempt + 1,
                                   "values": vals}})
    return out


# ------------------------------------------------------------------ U: kinds aimed at no named class
def ar1(r, shape, rho, axis):
    x = r.standard_normal(shape)
    out = np.array(x)
    for t in range(1, shape[axis]):
        cur = [slice(None), slice(None)]
        prev = [slice(None), slice(None)]
        cur[axis], prev[axis] = t, t - 1
        out[tuple(cur)] = rho * out[tuple(prev)] + math.sqrt(1.0 - rho * rho) * x[tuple(cur)]
    return out


def u_float(fam, r, K):
    sa, sb = (16, K), (K, 16)
    if fam == "tdist":
        df, s = float(r.uniform(2.5, 8.0)), 2.0 ** int(r.integers(-4, 5))
        f = lambda sh: np.clip(s * r.standard_t(df, sh), -64 * s, 64 * s)          # noqa: E731
        return f(sa), f(sb), {"df": df, "scale": s, "clip": 64 * s}
    if fam == "lognorm":
        mu, sig, pneg = float(r.uniform(-2, 2)), float(r.uniform(0.5, 2.5)), float(r.uniform(0.2, 0.8))
        f = lambda sh: np.exp(mu + sig * r.standard_normal(sh)) * np.where(r.random(sh) < pneg, -1.0, 1.0)  # noqa: E731
        return f(sa), f(sb), {"mu": mu, "sigma": sig, "p_negative": pneg}
    if fam == "mixture":
        pw, ratio, s = float(r.uniform(0.01, 0.1)), float(2.0 ** r.uniform(3, 7)), 2.0 ** int(r.integers(-3, 4))
        f = lambda sh: s * r.standard_normal(sh) * np.where(r.random(sh) < pw, ratio, 1.0)  # noqa: E731
        return f(sa), f(sb), {"p_wide": pw, "wide_ratio": ratio, "scale": s}
    if fam == "uniform":
        a = float(2.0 ** r.uniform(-6, 6))
        return r.uniform(-a, a, sa), r.uniform(-a, a, sb), {"half_width": a}
    if fam == "expo":
        s_a, s_b = 2.0 ** int(r.integers(-3, 4)), 2.0 ** int(r.integers(-3, 4))
        return s_a * r.exponential(1.0, sa), s_b * r.standard_normal(sb), {"a_exponential_scale": s_a,
                                                                           "b_normal_scale": s_b}
    if fam == "grid":
        q, s = int(r.integers(1, 7)), 2.0 ** int(r.integers(-2, 3))
        f = lambda sh: s * np.clip(np.round(r.standard_normal(sh) * 2 ** q) / 2 ** q, -4, 4)  # noqa: E731
        return f(sa), f(sb), {"grid_bits": q, "scale": s, "clip_sigmas": 4}
    if fam == "rowscale":
        ga, gb = float(r.uniform(0.5, 2.0)), float(r.uniform(0.5, 2.0))
        A = r.standard_normal(sa) * np.exp(ga * r.standard_normal((16, 1)))
        B = r.standard_normal(sb) * np.exp(gb * r.standard_normal((1, 16)))
        return A, B, {"a_row_log_sd": ga, "b_column_log_sd": gb}
    if fam == "sparse":
        pa, pb = float(r.uniform(0.1, 0.8)), float(r.uniform(0.1, 0.8))
        A = np.where(r.random(sa) < pa, 0.0, r.standard_normal(sa))
        B = np.where(r.random(sb) < pb, 0.0, r.standard_normal(sb))
        return A, B, {"a_zero_p": pa, "b_zero_p": pb}
    if fam == "ar_i":
        rho = float(r.uniform(0.8, 0.99))
        return ar1(r, sa, rho, 0), ar1(r, sb, rho, 1), {"rho": rho, "along": "A rows i, B columns j"}
    if fam == "ar_k":
        rho = float(r.uniform(0.8, 0.99))
        return ar1(r, sa, rho, 1), ar1(r, sb, rho, 0), {"rho": rho, "along": "k on both sides"}
    if fam == "bimodal":
        m = float(2.0 ** r.uniform(-3, 3))
        sd = m * float(r.uniform(0.01, 0.3))
        f = lambda sh: m * np.where(r.random(sh) < 0.5, -1.0, 1.0) + sd * r.standard_normal(sh)  # noqa: E731
        return f(sa), f(sb), {"mode": m, "sd": sd}
    if fam == "cauchy":
        s = 2.0 ** int(r.integers(-3, 3))
        f = lambda sh: np.clip(s * r.standard_cauchy(sh), -1000 * s, 1000 * s)     # noqa: E731
        return f(sa), f(sb), {"scale": s, "clip": 1000 * s}
    raise KeyError(fam)


def u_int8(fam, r, K):
    sa, sb = (16, K), (K, 16)
    sgn = lambda sh: np.where(r.random(sh) < 0.5, -1.0, 1.0)                       # noqa: E731
    if fam == "tq":
        df, s = float(r.uniform(2.5, 8.0)), float(r.uniform(4, 40))
        f = lambda sh: np.clip(np.round(s * r.standard_t(df, sh)), -127, 127)        # noqa: E731
        return f(sa), f(sb), {"df": df, "scale": s}
    if fam == "geom":
        pg = float(r.uniform(0.05, 0.5))
        f = lambda sh: np.minimum(r.geometric(pg, sh) - 1, 127).astype(np.float64) * sgn(sh)  # noqa: E731
        return f(sa), f(sb), {"p": pg}
    if fam == "urange":
        rr = int(r.choice([2, 4, 16, 32, 64]))
        return (r.integers(-rr, rr, sa).astype(np.float64), r.integers(-rr, rr, sb).astype(np.float64),
                {"range": [-rr, rr - 1]})
    if fam == "biased":
        mu, sd = float(r.uniform(-80, 80)), float(r.uniform(5, 50))
        f = lambda sh: np.clip(np.round(mu + sd * r.standard_normal(sh)), -128, 127)  # noqa: E731
        return f(sa), f(sb), {"mean": mu, "sd": sd}
    if fam == "sparseq":
        pz, s = float(r.uniform(0.2, 0.7)), float(r.uniform(8, 32))
        f = lambda sh: np.where(r.random(sh) < pz, 0.0, np.clip(np.round(s * r.standard_normal(sh)), -127, 127))  # noqa: E731
        return f(sa), f(sb), {"zero_p": pz, "scale": s}
    if fam == "pm":
        m = int(r.integers(1, 128))
        return float(m) * sgn(sa), float(m) * sgn(sb), {"magnitude": m}
    if fam == "ar_k":
        rho, s = float(r.uniform(0.8, 0.99)), float(r.uniform(16, 48))
        return (np.clip(np.round(s * ar1(r, sa, rho, 1)), -127, 127), np.clip(np.round(s * ar1(r, sb, rho, 0)), -127, 127),
                {"rho": rho, "scale": s, "along": "k on both sides"})
    if fam == "relu_tq":
        s_a, df, s_b = float(r.uniform(8, 40)), float(r.uniform(2.5, 8.0)), float(r.uniform(4, 24))
        A = np.clip(np.round(s_a * np.maximum(r.standard_normal(sa), 0.0)), 0, 127)
        B = np.clip(np.round(s_b * r.standard_t(df, sb)), -127, 127)
        return A, B, {"a_relu_scale": s_a, "b_df": df, "b_scale": s_b}
    raise KeyError(fam)


def make_u(seed, mk):
    out = []
    for fmt in FORMATS:
        fams = U_INT8 if fmt == "int8" else U_FLOAT
        K = mk.TYPES[fmt][3]
        order = rng(seed, "U", fmt, "families").permutation(len(fams))
        for fam in [fams[int(i)] for i in order[:U_COUNT[fmt]]]:
            r = rng(seed, "U", fmt, fam)
            A, B, p = (u_int8 if fmt == "int8" else u_float)(fam, r, K)
            if fmt == "fp16":
                A, B = np.clip(A, -FP16_MAX, FP16_MAX), np.clip(B, -FP16_MAX, FP16_MAX)
            out.append({"fmt": fmt, "cls": "U", "role": "kind", "slot": f"u8_{fam}", "raw": mk.encode(A, B, fmt),
                        "rule": f"family {fam} on stream U/{fmt}/{fam}", "params": p})
    return out


# ------------------------------------------------------------------ L and H: int8 whole lines and held B
def int8_raw(A, lines):
    a = np.asarray(A, dtype=np.int64)
    assert a.shape == (16, 64) and a.min() >= -128 and a.max() <= 127
    assert len(lines) == 16 and all(len(x) == 64 for x in lines)
    return a.astype("<i1").tobytes() + b"".join(lines)


def make_lh(seed, held_used):
    out = []

    def full(r, n):
        return r.integers(-128, 128, n)

    def line(r):
        return r.integers(0, 256, 64).astype(np.uint8).tobytes()

    for name, pops, neg in (("v1", (3,), None), ("v2", (5, 6), True)):
        r = rng(seed, "H", name)
        cands = [v for v in range(256) if bin(v).count("1") in pops and v not in held_used and (neg is None or v >= 128)]
        v = int(r.choice(cands))
        held_used.add(v)
        A = full(r, (16, 64))
        out.append({"fmt": "int8", "cls": "H", "role": "kind", "slot": "h8_held", "raw": int8_raw(A, [bytes([v]) * 64] * 16),
                    "rule": f"A uniform -128..127; every B byte 0x{v:02x}", "params": {"held_byte": v, "candidates": cands}})
    r = rng(seed, "H", "line")
    ln = np.clip(np.round(12.0 * r.standard_normal(64)), -127, 127).astype(np.int64).astype("<i1").tobytes()
    A = full(r, (16, 64))
    out.append({"fmt": "int8", "cls": "H", "role": "kind", "slot": "h8_held", "raw": int8_raw(A, [ln] * 16),
                "rule": "A uniform -128..127; one B line of round(12*N(0,1)) bytes, held for all 16 k-groups",
                "params": {"line_scale": 12.0}})
    # whole lines
    r = rng(seed, "L", "flip")
    X = np.frombuffer(line(r), dtype=np.uint8)
    kb = int(r.choice([2, 3, 4, 5]))
    M = np.array([sum(1 << int(b) for b in r.choice(8, kb, replace=False)) for _ in range(64)], dtype=np.uint8)
    Y = (X ^ M).astype(np.uint8)
    A = full(r, (16, 64))
    out.append({"fmt": "int8", "cls": "L", "role": "kind", "slot": "l8_flip",
                "raw": int8_raw(A, [X.tobytes(), Y.tobytes()] * 8),
                "rule": f"A uniform -128..127; B lines alternate X, Y with Y = X xor a mask of {kb} bits in every byte",
                "params": {"bits_per_byte": kb}})
    r = rng(seed, "L", "period2")
    X, Y = line(r), line(r)
    A = full(r, (16, 64))
    out.append({"fmt": "int8", "cls": "L", "role": "kind", "slot": "l8_period2", "raw": int8_raw(A, [X, X, Y, Y] * 4),
                "rule": "A uniform -128..127; B lines X, X, Y, Y, ... (random lines; a change at every second boundary)",
                "params": {}})
    r = rng(seed, "L", "cycle3")
    X, Y, Z = line(r), line(r), line(r)
    A = full(r, (16, 64))
    out.append({"fmt": "int8", "cls": "L", "role": "kind", "slot": "l8_cycle3",
                "raw": int8_raw(A, [(X, Y, Z)[p % 3] for p in range(16)]),
                "rule": "A uniform -128..127; B lines cycle X, Y, Z (three random lines)", "params": {}})
    r = rng(seed, "L", "halfword")
    X = np.frombuffer(line(r), dtype=np.uint8)
    Y = X.copy()
    Y[32:] = ~Y[32:]
    A = full(r, (16, 64))
    out.append({"fmt": "int8", "cls": "L", "role": "kind", "slot": "l8_halfword",
                "raw": int8_raw(A, [X.tobytes(), Y.tobytes()] * 8),
                "rule": "A uniform -128..127; B lines alternate X, Y with Y = X with words 8-15 (columns 8-15) "
                        "complemented: half of each line's words change at every boundary", "params": {}})
    return out


# ------------------------------------------------------------------ re-runs
def pick_reruns(seed, mk, earlier):
    """Per float format: the candidates are pool 6's and pool 7's kind tiles (MANIFEST role `kind`), one per distinct
    sha256; the statistic is make_kinds.tile_stats' bus_bits_per_op (the operand bits the unit's input bus flips in
    one op, which every field's toggles sum to).  Sorted by (statistic, seeded key): the minimum, the maximum, and one
    tile from each of n-2 equal-count strata of the rest, the stratum's smallest seeded key."""
    cands = {f: [] for f in RERUN_COUNT}
    seen = set()
    for t in earlier:
        m = t["manifest"]
        if t["pool"] not in RERUN_FROM or t["fmt"] not in cands or not m or m["role"] != "kind" or t["sha"] in seen:
            continue
        seen.add(t["sha"])
        st = mk.tile_stats(t["raw"], t["fmt"])
        cands[t["fmt"]].append(dict(t, stat=int(st["bus_bits_per_op"]), stats=st))
    picks, table = [], {}
    for fmt, n in RERUN_COUNT.items():
        c = sorted(cands[fmt], key=lambda x: (x["stat"], rank(seed, "rerun", x["label"])))
        inner = c[1:-1]
        chosen = [("min", c[0])]
        for i, idx in enumerate(np.array_split(np.arange(len(inner)), n - 2)):
            chosen.append((f"stratum {i + 1} of {n - 2} (ranks {int(idx[0]) + 2}-{int(idx[-1]) + 2} of {len(c)})",
                           min((inner[int(j)] for j in idx), key=lambda x: rank(seed, "rerun", x["label"]))))
        chosen.append(("max", c[-1]))
        table[fmt] = [{"label": x["label"], "pool": x["pool"], "stat": x["stat"]} for x in c]
        for why, t in chosen:
            m = t["manifest"]
            picks.append({"fmt": fmt, "cls": m["case"], "role": "rerun", "slot": None, "label": t["label"],
                          "raw": t["raw"], "rerun_of": t["pool"],
                          "rule": f"re-run of {t['pool']} {t['label']} (case={m['case']}), byte for byte",
                          "params": {"from_pool": t["pool"], "from_label": t["label"], "from_case": m["case"],
                                     "bus_bits_per_op": t["stat"], "pick": why}})
    return picks, table


# ------------------------------------------------------------------ real tiles: two public W8A8 checkpoints
TEXT = ("You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have "
        "regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister "
        "of my welfare and increasing confidence in the success of my undertaking.")
TEXT_SOURCE = "Mary Shelley, Frankenstein (1818), Letter 1, its opening; public domain; ASCII, no digits"
T = 32
REAL_MODELS = {
    "granite": {"repo": "RedHatAI/granite-3.1-2b-instruct-quantized.w8a8", "rev": "ba87c9abf4e5ccd3e1255925eb490991809a89ab",
                "license": "apache-2.0", "base": "ibm-granite/granite-3.1-2b-instruct", "split": "gpt2",
                "expect": {"model_type": "granite", "hidden_size": 2048, "num_attention_heads": 32,
                           "num_key_value_heads": 8, "intermediate_size": 8192, "rms_norm_eps": 1e-05,
                           "rope_theta": 5000000.0, "embedding_multiplier": 12.0, "residual_multiplier": 0.22,
                           "attention_multiplier": 0.015625, "attention_bias": False, "rope_scaling": None}},
    "dsqwen": {"repo": "RedHatAI/DeepSeek-R1-Distill-Qwen-1.5B-quantized.w8a8", "rev": "eb5a917a789bcf9f76eee7b3f61a12d647e2d37a",
               "license": "mit", "base": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "split": "qwen2",
               "expect": {"model_type": "qwen2", "hidden_size": 1536, "num_attention_heads": 12,
                          "num_key_value_heads": 2, "intermediate_size": 8960, "rms_norm_eps": 1e-06,
                          "rope_theta": 10000, "rope_scaling": None, "use_sliding_window": False}},
}
REAL_KEYS = ("granite", "dsqwen")
QUANT_EXPECT = {"format": "int-quantized", "weights": {"num_bits": 8, "strategy": "channel", "symmetric": True,
                                                       "type": "int"},
                "input_activations": {"num_bits": 8, "strategy": "token", "symmetric": True, "dynamic": True,
                                      "type": "int"}}
SPLIT = {   # each tokenizer's pre-tokenizer split with \p{L} -> [A-Za-z], \p{N} -> [0-9]: exact on ASCII text
    "gpt2": r"'s|'t|'re|'ve|'m|'ll|'d| ?[A-Za-z]+| ?[0-9]+| ?[^\sA-Za-z0-9]+|\s+(?!\S)|\s+",
    "qwen2": r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\nA-Za-z0-9]?[A-Za-z]+|[0-9]| ?[^\sA-Za-z0-9]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+",
}
QWEN2_REGEX = ("(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\\r\\n\\p{L}\\p{N}]?\\p{L}+|\\p{N}| ?[^\\s\\p{L}\\p{N}]+[\\r\\n]*|"
               "\\s*[\\r\\n]+|\\s+(?!\\S)|\\s+")
LINEARS = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
           "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]
UA = {"User-Agent": "q142d-pool8/1.0"}


class Store:
    """One checkpoint's downloaded bytes: <dl>/<key>-config/config.json, <dl>/<key>-tokenizer/tokenizer.json and
    <dl>/<key>-safetensors/r_<lo>_<hi>.bin (byte ranges of model.safetensors).  online=True (fetch) creates the three
    directories new and empty and downloads into them; online=False (build) never touches the network."""

    def __init__(self, dl, key, online, budget):
        self.key, self.online, self.budget = key, online, budget
        self.dirs = {k: os.path.join(dl, f"{key}-{k}") for k in ("config", "tokenizer", "safetensors")}
        if online:
            for d in self.dirs.values():
                if os.path.exists(d):
                    raise SystemExit(f"{d} exists: each download goes in its own new empty directory")
                os.makedirs(d)
        m = REAL_MODELS[key]
        self.url = f"https://huggingface.co/{m['repo']}/resolve/{m['rev']}/"
        self.log = []

    def _get(self, url, lo=None, hi=None):
        if not self.online:
            raise SystemExit(f"{url} [{lo}, {hi}] was not fetched: run `fetch` first")
        n = (hi - lo + 1) if lo is not None else 0
        if self.budget["used"] + n > self.budget["cap"]:
            raise SystemExit(f"download cap {self.budget['cap']} bytes reached")
        h = dict(UA)
        if lo is not None:
            h["Range"] = f"bytes={lo}-{hi}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=300) as r:
            b = r.read()
        if lo is not None and len(b) != n:
            raise SystemExit(f"{url}: asked {n} bytes, got {len(b)}")
        self.budget["used"] += len(b)
        return b

    def file(self, name, kind):
        p = os.path.join(self.dirs[kind], name)
        if not os.path.exists(p):
            b = self._get(self.url + name)
            with open(p, "wb") as f:
                f.write(b)
        with open(p, "rb") as f:
            b = f.read()
        self.log.append({"file": name, "bytes": len(b), "sha256": sha(b)})
        return b

    def range(self, lo, hi, what):
        p = os.path.join(self.dirs["safetensors"], f"r_{lo}_{hi}.bin")
        if not os.path.exists(p):
            b = self._get(self.url + "model.safetensors", lo, hi)
            with open(p, "wb") as f:
                f.write(b)
        with open(p, "rb") as f:
            b = f.read()
        assert len(b) == hi - lo + 1, p
        self.log.append({"file": "model.safetensors", "what": what, "range": [lo, hi], "bytes": len(b), "sha256": sha(b)})
        return b


def conv(b, dtype, shape):
    if dtype == "BF16":
        return (np.frombuffer(b, dtype="<u2").astype(np.uint32) << np.uint32(16)).view(np.float32).reshape(shape).copy()
    if dtype == "I8":
        return np.frombuffer(b, dtype=np.int8).reshape(shape).copy()
    if dtype == "F16":
        return np.frombuffer(b, dtype="<f2").astype(np.float32).reshape(shape)
    if dtype == "F32":
        return np.frombuffer(b, dtype="<f4").reshape(shape).copy()
    raise SystemExit(f"dtype {dtype}")


def bytes_to_unicode():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("\xa1"), ord("\xac") + 1)) + list(range(ord("\xae"), ord("\xff") + 1))
    cs, n = bs[:], 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


def check_pretokenizer(tok, split):
    pre = tok.get("pre_tokenizer") or {}
    if split == "gpt2":
        ok = pre == {"type": "ByteLevel", "add_prefix_space": False, "trim_offsets": True, "use_regex": True}
    else:
        ps = pre.get("pretokenizers", [])
        ok = (pre.get("type") == "Sequence" and len(ps) == 2 and ps[0].get("type") == "Split"
              and ps[0].get("pattern", {}).get("Regex") == QWEN2_REGEX and ps[1].get("type") == "ByteLevel"
              and ps[1].get("use_regex") is False)
    if not ok:
        raise SystemExit(f"tokenizer pre_tokenizer is not the expected {split} one: {json.dumps(pre)[:300]}")
    if tok["model"].get("type") != "BPE":
        raise SystemExit("tokenizer model is not BPE")


def bpe_tokens(tok, split):
    """Byte-level BPE on ASCII TEXT: the pre-tokenizer's split, GPT-2's byte-to-unicode map, the merges by rank
    (every occurrence of the best pair, left to right, until none applies); no special token added."""
    assert all(ord(c) < 128 for c in TEXT) and not re.search(r"[0-9]", TEXT)
    vocab, rank_of = tok["model"]["vocab"], {}
    for r, m in enumerate(tok["model"]["merges"]):
        a, b = (m.split(" ", 1) if isinstance(m, str) else m)
        rank_of[(a, b)] = r
    b2u = bytes_to_unicode()
    ids, pieces = [], []
    for pre in re.findall(SPLIT[split], TEXT):
        word = [b2u[b] for b in pre.encode("utf-8")]
        while len(word) > 1:
            best = min(((rank_of.get((word[i], word[i + 1])), i) for i in range(len(word) - 1)),
                       key=lambda x: (x[0] is None, x[0] if x[0] is not None else 0, x[1]))
            if best[0] is None:
                break
            out, i = [], 0
            while i < len(word):
                if i < len(word) - 1 and rank_of.get((word[i], word[i + 1])) == best[0]:
                    out.append(word[i] + word[i + 1])
                    i += 2
                else:
                    out.append(word[i])
                    i += 1
            word = out
        for w in word:
            pieces.append(w)
            ids.append(int(vocab[w]))
        if len(ids) >= T:
            break
    assert len(ids) >= T, (len(ids), pieces)
    return ids[:T], pieces[:T]


def model_bytes(store, key, depth):
    """Everything the forward pass reads: config, tokenizer, the safetensors header, the text's embedding rows and
    every tensor of layers 0..depth-1.  The same calls fetch (online) and read back (offline)."""
    m = REAL_MODELS[key]
    cfg = json.loads(store.file("config.json", "config"))
    for k, v in m["expect"].items():
        if cfg.get(k) != v:
            raise SystemExit(f"{key} config.json {k} = {cfg.get(k)!r}, expected {v!r}")
    q = cfg.get("quantization_config", {})
    g = q.get("config_groups", {}).get("group_0", {})
    for part in ("weights", "input_activations"):
        for k, v in QUANT_EXPECT[part].items():
            if g.get(part, {}).get(k) != v:
                raise SystemExit(f"{key} quantization {part}.{k} = {g.get(part, {}).get(k)!r}, expected {v!r}")
    if q.get("format") != QUANT_EXPECT["format"]:
        raise SystemExit(f"{key} quantization format {q.get('format')}")
    tok_bytes = store.file("tokenizer.json", "tokenizer")
    tok = json.loads(tok_bytes)
    check_pretokenizer(tok, m["split"])
    ids, pieces = bpe_tokens(tok, m["split"])
    n = struct.unpack("<Q", store.range(0, 7, "header length"))[0]
    hdr = json.loads(store.range(8, 8 + n - 1, "header"))
    base = 8 + n

    def tensor(name):
        t = hdr[name]
        lo, hi = t["data_offsets"]
        return conv(store.range(base + lo, base + hi - 1, name), t["dtype"], t["shape"])

    t = hdr["model.embed_tokens.weight"]
    esz = {"BF16": 2, "F16": 2, "F32": 4}[t["dtype"]]
    rb = t["shape"][1] * esz
    rows = {}
    for r in sorted(set(ids)):
        lo = base + t["data_offsets"][0] + r * rb
        rows[r] = conv(store.range(lo, lo + rb - 1, f"model.embed_tokens.weight row {r}"), t["dtype"], [t["shape"][1]])
    E = np.stack([rows[i] for i in ids]).astype(np.float32)
    layers = []
    for li in range(depth):
        L = f"model.layers.{li}."
        d = {"ln1": tensor(L + "input_layernorm.weight"), "ln2": tensor(L + "post_attention_layernorm.weight")}
        for p in LINEARS:
            d[p] = (tensor(L + p + ".weight"), tensor(L + p + ".weight_scale"))
        for p in ("q_proj", "k_proj", "v_proj"):
            d[p + ".bias"] = tensor(L + f"self_attn.{p}.bias") if (L + f"self_attn.{p}.bias") in hdr else None
        layers.append(d)
    return {"cfg": cfg, "ids": ids, "pieces": pieces, "E": E, "layers": layers, "tok_sha": sha(tok_bytes),
            "n_header_tensors": len([k for k in hdr if k != "__metadata__"])}


def rmsnorm(x, w, eps):
    r = np.sqrt((x.astype(np.float64) ** 2).mean(-1, keepdims=True) + eps)
    return (x.astype(np.float64) / r * w.astype(np.float64)).astype(np.float32)


def q_tok(x):
    """Dynamic per-token symmetric int8: scale = the token's max |x| over its whole row / 127, round half to even,
    clip to +-127 (pool 7's reading of the checkpoints' scheme)."""
    s = np.abs(x.astype(np.float64)).max(-1, keepdims=True) / 127.0
    s = np.where(s == 0, 1.0, s)
    return np.clip(np.round(x.astype(np.float64) / s), -127, 127), s[:, 0]


def w8a8(x, Wq, ws, bias=None):
    xq, xs = q_tok(x)
    acc = xq @ Wq.astype(np.float64).T                          # int8 x int8 sums, exact in float64
    y = acc * xs[:, None] * ws.reshape(1, -1).astype(np.float64)
    if bias is not None:
        y = y + bias.reshape(1, -1).astype(np.float64)
    return y.astype(np.float32)


def rotary(x, theta):
    hs = x.shape[-1]
    inv = 1.0 / (theta ** (np.arange(0, hs, 2, dtype=np.float64) / hs))
    fr = np.outer(np.arange(x.shape[0], dtype=np.float64), inv)
    emb = np.concatenate([fr, fr], axis=-1)
    cos, sin = np.cos(emb)[:, None, :], np.sin(emb)[:, None, :]
    half = hs // 2
    rot = np.concatenate([-x[..., half:], x[..., :half]], axis=-1).astype(np.float64)
    return (x.astype(np.float64) * cos + rot * sin).astype(np.float32)


def silu(x):
    return (x.astype(np.float64) / (1.0 + np.exp(-x.astype(np.float64)))).astype(np.float32)


def forward(md):
    """Layers 0..depth-1 in float32 with W8A8 linears: (Granite: embeddings x embedding_multiplier) -> RMSNorm ->
    q/k/v (+ bias where the checkpoint has one) -> rotary over the whole head -> scores q.k x scale (Granite:
    attention_multiplier; else 1/sqrt(head dim)) with grouped KV heads -> causal softmax -> P V -> o_proj ->
    residual (Granite: x residual_multiplier) -> RMSNorm -> gate, up -> SiLU(gate) * up -> down_proj -> residual."""
    cfg = md["cfg"]
    hid, H, KV = cfg["hidden_size"], cfg["num_attention_heads"], cfg["num_key_value_heads"]
    hs, grp = hid // H, H // KV
    eps, theta = float(cfg["rms_norm_eps"]), float(cfg["rope_theta"])
    emb, res = float(cfg.get("embedding_multiplier", 1.0)), float(cfg.get("residual_multiplier", 1.0))
    scale = float(cfg["attention_multiplier"]) if "attention_multiplier" in cfg else 1.0 / math.sqrt(hs)
    h = (md["E"].astype(np.float64) * emb).astype(np.float32)
    mask = np.triu(np.ones((T, T), bool), 1)
    out = []
    for Ly in md["layers"]:
        x1 = rmsnorm(h, Ly["ln1"], eps)
        q = w8a8(x1, *Ly["self_attn.q_proj"], Ly["q_proj.bias"]).reshape(T, H, hs)
        k = w8a8(x1, *Ly["self_attn.k_proj"], Ly["k_proj.bias"]).reshape(T, KV, hs)
        v = w8a8(x1, *Ly["self_attn.v_proj"], Ly["v_proj.bias"]).reshape(T, KV, hs)
        qr, kr = rotary(q, theta), rotary(k, theta)
        P = np.empty((H, T, T), np.float32)
        att = np.empty((T, H, hs), np.float32)
        for hh in range(H):
            s = (qr[:, hh, :].astype(np.float64) @ kr[:, hh // grp, :].astype(np.float64).T) * scale
            s = np.where(mask, -np.inf, s)
            p = np.exp(s - s.max(-1, keepdims=True))
            P[hh] = (p / p.sum(-1, keepdims=True)).astype(np.float32)
            att[:, hh, :] = (P[hh].astype(np.float64) @ v[:, hh // grp, :].astype(np.float64)).astype(np.float32)
        attf = att.reshape(T, H * hs)
        hmid = (h.astype(np.float64) + res * w8a8(attf, *Ly["self_attn.o_proj"]).astype(np.float64)).astype(np.float32)
        x2 = rmsnorm(hmid, Ly["ln2"], eps)
        act = (silu(w8a8(x2, *Ly["mlp.gate_proj"])).astype(np.float64)
               * w8a8(x2, *Ly["mlp.up_proj"]).astype(np.float64)).astype(np.float32)
        h = (hmid.astype(np.float64) + res * w8a8(act, *Ly["mlp.down_proj"]).astype(np.float64)).astype(np.float32)
        out.append({"x1": x1, "q": qr, "k": kr, "v": v, "P": P, "att": attf, "x2": x2, "act": act})
        assert all(np.isfinite(a).all() for a in out[-1].values())
    return out, {"grp": grp, "hs": hs, "H": H, "KV": KV, "hid": hid, "ff": cfg["intermediate_size"],
                 "softmax_row_sum_max_err": float(max(np.abs(o["P"].sum(-1) - 1).max() for o in out))}


def real_plan(seed, key, geo, depth):
    """Every seeded choice of one model's cuts, drawn in this order on stream real/<key>."""
    r = rng(seed, "real", key)
    hid, H, hs, ff, KV = geo["hid"], geo["H"], geo["hs"], geo["ff"], geo["KV"]
    p = {"L8": int(r.integers(1, depth)), "Lf": int(r.integers(1, depth))}
    p["win_x1"] = int(r.integers(0, 2))
    p["proj"] = ["q", "k", "v"][int(r.integers(0, 3))]
    p["rows_x1"] = 16 * int(r.integers(0, (hid if p["proj"] == "q" else KV * hs) // 16))
    p["win_act"] = int(r.integers(0, 2))
    p["rows_down"] = 16 * int(r.integers(0, hid // 16))
    p["win_pv"], p["head_pv"], p["dblk_pv"] = int(r.integers(0, 2)), int(r.integers(0, H)), 16 * int(r.integers(0, hs // 16))
    p["win_qk"], p["head_qk"], p["dblk_qk"] = int(r.integers(0, 2)), int(r.integers(0, H)), 16 * int(r.integers(0, hs // 16))
    p["win_dq"] = int(r.integers(0, 2))
    p["gu"] = ["gate", "up"][int(r.integers(0, 2))]
    p["rows_gu"] = 16 * int(r.integers(0, ff // 16))
    p["dblk_dq_draw"] = int(r.integers(0, 1 << 30))
    return p


def mode_argmax(x):
    """The commonest per-token argmax of |x| (ties to the smaller index)."""
    am = np.abs(x).argmax(-1)
    return int(np.bincount(am).argmax())


def block(i, width):
    s = (int(i) // width) * width
    return slice(s, s + width)


def win(i):
    return slice(16 * i, 16 * i + 16)


def outlier_stats(full_rows):
    a = np.abs(full_rows.astype(np.float64))
    mx, med = a.max(-1), np.median(a, -1)
    q, _ = q_tok(full_rows)
    return {"row_max_abs": [round(float(v), 5) for v in mx],
            "row_max_over_median": [round(float(v), 2) for v in mx / np.maximum(med, 1e-30)],
            "row_argmax": [int(v) for v in a.argmax(-1)],
            "row_int8_small_share": [round(float(v), 4) for v in (np.abs(q) <= 1).mean(-1)]}


def real_cuts(seed, md_all, depth):
    """Five cuts a model: two int8 W8A8 (the q/k/v input block holding the commonest outlier dim against that
    projection's int8 weights; the down_proj input block holding the most outlying token's top unit against
    down_proj's int8 weights), P x V in fp16, Q x K^T in fp32, and post-attention-norm activations against a
    dequantised gate or up block (fp16 for one model, fp32 for the other, by the seed)."""
    deq16 = REAL_KEYS[int(rng(seed, "real", "dequant-format").integers(0, 2))]
    cuts, plans, picks = [], {}, {}
    for key in REAL_KEYS:
        md = md_all[key]
        lay, geo = forward(md)
        md["geo"] = geo
        p = real_plan(seed, key, geo, depth)
        plans[key] = p
        Wt = md["layers"]
        # int8 1: the proj input
        L = p["L8"]
        X = lay[L]["x1"]
        w = win(p["win_x1"])
        dstar = mode_argmax(X[w])
        b64 = block(dstar, 64)
        Wq8, _ = Wt[L][f"self_attn.{p['proj']}_proj"]
        A_f = X[w, b64]
        Aq, _ = q_tok(X[w])
        cuts.append({"key": key, "fmt": "int8", "cut": f"x1{p['proj']}", "layer": L,
                     "A_float": A_f, "A": Aq[:, b64], "B": Wq8[p["rows_x1"]:p["rows_x1"] + 16, b64].T.astype(np.float64),
                     "what_A": f"layer {L} input_layernorm output (the {p['proj']}_proj input), tokens {w.start}-{w.stop - 1}, "
                               f"dims {b64.start}-{b64.stop - 1}, quantised per token over all {X.shape[1]} dims; the block "
                               f"holds dim {dstar}, the commonest per-token argmax of |x| over those tokens",
                     "what_B": f"layer {L} {p['proj']}_proj int8 weight rows {p['rows_x1']}-{p['rows_x1'] + 15} x input dims "
                               f"{b64.start}-{b64.stop - 1}, transposed",
                     "outliers": outlier_stats(X[w]), "pick": {"outlier_dim": dstar}})
        # int8 2: the down_proj input
        Xa = lay[L]["act"]
        w = win(p["win_act"])
        st = outlier_stats(Xa[w])
        tstar = int(np.argmax(st["row_max_over_median"]))
        ustar = int(np.abs(Xa[w][tstar]).argmax())
        b64 = block(ustar, 64)
        Wd8, _ = Wt[L]["mlp.down_proj"]
        Aq, _ = q_tok(Xa[w])
        cuts.append({"key": key, "fmt": "int8", "cut": "actdown", "layer": L,
                     "A_float": Xa[w, b64], "A": Aq[:, b64],
                     "B": Wd8[p["rows_down"]:p["rows_down"] + 16, b64].T.astype(np.float64),
                     "what_A": f"layer {L} SiLU(gate) * up (the down_proj input), tokens {w.start}-{w.stop - 1}, units "
                               f"{b64.start}-{b64.stop - 1}, quantised per token over all {Xa.shape[1]} units; the block "
                               f"holds unit {ustar}, the top unit of token {w.start + tstar}, the window's most outlying "
                               f"token (largest max/median of |x|)",
                     "what_B": f"layer {L} down_proj int8 weight rows {p['rows_down']}-{p['rows_down'] + 15} x units "
                               f"{b64.start}-{b64.stop - 1}, transposed",
                     "outliers": st, "pick": {"outlier_token": w.start + tstar, "outlier_unit": ustar}})
        # fp16: P x V
        L = p["Lf"]
        hh, kv = p["head_pv"], p["head_pv"] // geo["grp"]
        w = win(p["win_pv"])
        d0 = p["dblk_pv"]
        Pc = lay[L]["P"][hh][w, 0:32]
        Vc = lay[L]["v"][0:32, kv, d0:d0 + 16]
        cuts.append({"key": key, "fmt": "fp16", "cut": "pv", "layer": L, "A_float": Pc, "A": Pc, "B": Vc,
                     "what_A": f"layer {L} head {hh}: causal softmax, query tokens {w.start}-{w.stop - 1} x key tokens 0-31",
                     "what_B": f"layer {L} KV head {kv}: values of tokens 0-31, head dims {d0}-{d0 + 15}", "pick": {}})
        # fp32: Q x K^T
        hh, kv = p["head_qk"], p["head_qk"] // geo["grp"]
        w = win(p["win_qk"])
        d0 = p["dblk_qk"]
        Qc = lay[L]["q"][w, hh, d0:d0 + 16]
        Kc = lay[L]["k"][0:16, kv, d0:d0 + 16].T
        cuts.append({"key": key, "fmt": "fp32", "cut": "qk", "layer": L, "A_float": Qc, "A": Qc, "B": Kc,
                     "what_A": f"layer {L} head {hh}: rotary queries, tokens {w.start}-{w.stop - 1}, head dims {d0}-{d0 + 15}",
                     "what_B": f"layer {L} KV head {kv}: rotary keys of tokens 0-15, head dims {d0}-{d0 + 15}, transposed",
                     "pick": {}})
        # fp16 or fp32: activations x dequantised weights
        fmt = "fp16" if key == deq16 else "fp32"
        Kd = 32 if fmt == "fp16" else 16
        bd = block(Kd * (p["dblk_dq_draw"] % (geo["hid"] // Kd)), Kd)
        w = win(p["win_dq"])
        W8, ws = Wt[L][f"mlp.{p['gu']}_proj"]
        rows = slice(p["rows_gu"], p["rows_gu"] + 16)
        Wdq = (W8[rows, bd].astype(np.float32) * ws.reshape(-1)[rows].astype(np.float32)[:, None]).T
        X2 = lay[L]["x2"][w, bd]
        cuts.append({"key": key, "fmt": fmt, "cut": f"x2{p['gu']}", "layer": L, "A_float": X2, "A": X2, "B": Wdq,
                     "what_A": f"layer {L} post_attention_layernorm output, tokens {w.start}-{w.stop - 1}, dims "
                               f"{bd.start}-{bd.stop - 1}",
                     "what_B": f"layer {L} {p['gu']}_proj weight dequantised (int8 x its channel's bf16 scale, exact in "
                               f"float32) rows {rows.start}-{rows.stop - 1} x dims {bd.start}-{bd.stop - 1}, transposed",
                     "pick": {}})
        picks[key] = {"geometry": geo, "tokens": md["ids"], "pieces": md["pieces"]}
    return cuts, plans, picks, deq16


def make_real(seed, mk, dl, depth_expected=None):
    budget = {"used": 0, "cap": 0}
    md_all, logs = {}, {}
    for key in REAL_KEYS:
        st = Store(dl, key, online=False, budget=budget)
        md_all[key] = model_bytes_auto(st, key)
        logs[key] = st
    depth = min(len(md_all[k]["layers"]) for k in REAL_KEYS)
    if depth_expected is not None and depth != depth_expected:
        raise SystemExit(f"fetched depth {depth}, the pool needs {depth_expected}")
    cuts, plans, picks, deq16 = real_cuts(seed, md_all, depth)
    out = []
    for c in cuts:
        A, B = np.asarray(c["A"], dtype=np.float64), np.asarray(c["B"], dtype=np.float64)
        if c["fmt"] == "fp16" and (np.abs(A).max() > 65504 or np.abs(B).max() > 65504):
            raise SystemExit(f"{c['key']} {c['cut']}: beyond fp16's range")
        raw = mk.encode(A, B, c["fmt"])
        out.append({"fmt": c["fmt"], "cls": "R", "role": "kind", "slot": f"r8_{c['key']}_l{c['layer']}_{c['cut']}",
                    "raw": raw, "rule": f"{REAL_MODELS[c['key']]['repo']}: A = {c['what_A']}; B = {c['what_B']}",
                    "params": {"model": c["key"], "layer": c["layer"], "cut": c["cut"], "what_A": c["what_A"],
                               "what_B": c["what_B"], "pick": c["pick"], "outliers": c.get("outliers")},
                    "arrays": {"A": np.asarray(c["A_float"], dtype=np.float32), "B": np.asarray(c["B"], dtype=np.float32)}})
    meta = {"depth": depth, "plans": plans, "picks": picks, "dequant_fp16_model": deq16,
            "logs": {k: v.log for k, v in logs.items()},
            "models": {k: {"repo": REAL_MODELS[k]["repo"], "revision": REAL_MODELS[k]["rev"],
                           "license": REAL_MODELS[k]["license"], "base_model": REAL_MODELS[k]["base"],
                           "license_source": "the Hugging Face model API's cardData.license for that repo, read 4 Nov 2026",
                           "tokenizer_sha256": md_all[k]["tok_sha"], "header_tensors": md_all[k]["n_header_tensors"],
                           "fetched_bytes_read": int(sum(x["bytes"] for x in logs[k].log)),
                           "softmax_row_sum_max_err": md_all[k]["geo"]["softmax_row_sum_max_err"]}
                       for k in REAL_KEYS}}
    return out, meta


def model_bytes_auto(store, key):
    """Offline: read back as many layers as were fetched (fetch writes <key>-safetensors/DEPTH)."""
    with open(os.path.join(store.dirs["safetensors"], "DEPTH")) as f:
        depth = int(f.read().strip())
    return model_bytes(store, key, depth)


# ------------------------------------------------------------------ assembling the pool
def priorities(seed, tiles):
    """Anchors and the check anchor: p2, as pool 7's anchors.  Every other group (S, U, L+H, R, re-runs): sorted by
    a seeded key, the last round(n/4) (at least one) p2, the rest p1."""
    groups = {}
    for t in tiles:
        if t["role"] in ("anchor", "check"):
            t["prio"] = "p2"
            continue
        g = "rerun" if t["role"] == "rerun" else ("LH" if t["cls"] in ("L", "H") else t["cls"])
        groups.setdefault(g, []).append(t)
    for g, ts in groups.items():
        ts.sort(key=lambda t: rank(seed, "prio", t["label"]))
        n2 = max(1, round(len(ts) / 4))
        for i, t in enumerate(ts):
            t["prio"] = "p2" if i >= len(ts) - n2 else "p1"


ORDER = {"0": 0, "S": 1, "U": 2, "L": 3, "H": 4, "R": 5}


def assemble(seed, mk, kinds, dl, depth_expected):
    earlier, sums = scan_earlier(kinds)
    by_sha = {}
    for t in earlier:
        by_sha.setdefault(t["sha"], []).append((t["pool"], t["label"]))
    used_bits, used_words, sb_earlier, held_used = {"fp32": set(), "fp16": set()}, set(), [], set()
    for t in earlier:
        s = single_bit_any(t["raw"], t["fmt"], mk)
        if s:
            used_bits[t["fmt"]].add(s["bit"])
            used_words |= {s["base"], s["flipped"]}
            if t["fmt"] == "fp16":
                used_words |= {(s["base"] & 0xFFFF) * 0x10001, (s["flipped"] & 0xFFFF) * 0x10001}
            sb_earlier.append({"pool": t["pool"], "label": t["label"], "side": s["side"], "bit": s["bit"],
                               "base": f"0x{s['base']:08x}"})
        if t["fmt"] == "int8":
            i = int8_lines(t["raw"])
            if i["distinct"] == 1 and i["byte"] is not None:
                held_used.add(i["byte"])
    held_earlier, words_earlier = sorted(held_used), len(used_words)
    new = make_anchors(seed, mk) + make_s(seed, mk, used_bits, used_words) + make_u(seed, mk) + make_lh(seed, held_used)
    real, real_meta = make_real(seed, mk, dl, depth_expected)
    new += real
    reruns, rerun_table = pick_reruns(seed, mk, earlier)
    floors = floor_tiles(earlier)
    tiles, refused = [], []
    for t in new:
        sig = byte_sig(t["raw"], t["fmt"], t["cls"], mk)
        t["label"] = f"{t['fmt']}.{t['slot']}_{sig}"
        t["byte_sig"] = sig
        t["sha"] = sha(t["raw"])
        why = tile_refusal(t["raw"], t["fmt"], mk)
        ok, cwhy = class_check(t["raw"], t["fmt"], t["cls"], t["role"], mk)
        if why or not ok:
            refused.append({"label": t["label"], "why": why or cwhy})
            continue
        if t["sha"] in by_sha:
            refused.append({"label": t["label"], "why": f"byte twin of {by_sha[t['sha']]} under a new label"})
            continue
        t["flag"] = "-"
        tiles.append(t)
    for t in floors + reruns:
        t["sha"] = sha(t["raw"])
        if (t["rerun_of"], t["label"]) not in by_sha.get(t["sha"], []):
            raise SystemExit(f"{t['label']}: not byte for byte its own earlier tile")
        why = tile_refusal(t["raw"], t["fmt"], mk)
        if why:
            raise SystemExit(f"{t['label']}: {why}")
        t["flag"] = f"rerun:{t['rerun_of']}"
        tiles.append(t)
    seen = {}
    for t in tiles:
        if t["sha"] in seen and not (t["role"] == "anchor" and t["sha"] == sha(bytes(2048))):
            raise SystemExit(f"{t['label']} has the bytes of {seen[t['sha']]} in this pool")
        seen.setdefault(t["sha"], t["label"])
        assert t["label"] not in [x["label"] for x in tiles if x is not t], t["label"]
    priorities(seed, tiles)
    half_a, half_b = {}, {}
    for e in earlier:
        half_a.setdefault(sha(e["raw"][:1024]), set()).add(e["label"])
        half_b.setdefault(sha(e["raw"][1024:]), set()).add(e["label"])
    for t in tiles:
        t["file"] = f"tiles/{t['fmt']}/{t['label']}.bin"
        st = mk.tile_stats(t["raw"], t["fmt"])
        t["stats"] = {"bus_bits_per_op": int(st["bus_bits_per_op"]), "gated_lane_frac": st["gated_lane_frac"],
                      "a_hamming": st["a"]["hamming"], "b_hamming": st["b"]["hamming"],
                      "a_zero_word_frac": st["a"]["zero_word_frac"], "b_zero_word_frac": st["b"]["zero_word_frac"]}
        # half-twins: information only (a constant A, say, is many earlier tiles' A)
        t["half_twins"] = {"A": sorted(half_a.get(sha(t["raw"][:1024]), set()))[:6],
                           "B": sorted(half_b.get(sha(t["raw"][1024:]), set()))[:6]}
    tiles.sort(key=lambda t: (1 if t["role"] == "rerun" else 0, ORDER[t["cls"]] if t["role"] != "rerun" else 0,
                              FORMATS.index(t["fmt"]), 0 if t["flag"].startswith("rerun") else 1,
                              {"anchor": 0, "check": 1}.get(t["role"], 2), t["label"]))
    return tiles, refused, {"earlier": sums, "single_bit_earlier": sb_earlier, "used_bits": {k: sorted(v) for k, v in used_bits.items()},
                            "held_bytes_earlier": held_earlier, "single_bit_words_earlier": words_earlier,
                            "rerun_candidates": rerun_table, "real": real_meta, "n_earlier_tiles": len(earlier)}


def counts(tiles):
    c = {"S": 0, "U": 0, "R": 0, "LH": 0, "0": 0, "rerun": 0, "floor": 0}
    for t in tiles:
        if t["role"] == "rerun":
            c["rerun"] += 1
        elif t["flag"].startswith("rerun"):
            c["floor"] += 1
        elif t["cls"] in ("L", "H"):
            c["LH"] += 1
        else:
            c[t["cls"]] += 1
    c["int8_w8a8_outlier"] = sum(1 for t in tiles if t["cls"] == "R" and t["role"] == "kind" and t["fmt"] == "int8")
    c["real_models"] = len({t["params"]["model"] for t in tiles if t["cls"] == "R" and t["role"] == "kind"})
    c["total"] = len(tiles)
    return c


def quota_ok(c):
    return {k: c[k] >= QUOTA_MIN[k] for k in QUOTA_MIN} | {"real_models>=2": c["real_models"] >= 2,
                                                           "int8_w8a8>=1": c["int8_w8a8_outlier"] >= 1}


def generator_identity():
    me = os.path.abspath(__file__)
    d = os.path.dirname(me)
    blob = git("hash-object", me, cwd=d)
    head_blob = git("rev-parse", f"HEAD:./{os.path.basename(me)}", cwd=d)
    return {"file": os.path.basename(me), "sha256": sha_file(me), "git_blob": blob, "git_head_blob": head_blob,
            "git_head": git("rev-parse", "HEAD", cwd=d), "committed": blob is not None and blob == head_blob,
            "design_md_blob": git("rev-parse", "HEAD:./DESIGN.md", cwd=d)}


def write_pool(out, tiles, refused, info, seed, mk_sha, gen):
    if os.path.exists(out) and os.listdir(out):
        raise SystemExit(f"{out} is not empty")
    os.makedirs(out, exist_ok=True)
    for t in tiles:
        p = os.path.join(out, t["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(t["raw"])
    os.makedirs(os.path.join(out, "real"), exist_ok=True)
    real_cuts_meta = {}
    for t in tiles:
        if t["cls"] == "R" and t["role"] == "kind":
            for side in ("A", "B"):
                a = t["arrays"][side]
                fn = f"{t['label'].split('.', 1)[1]}_{side}_{a.shape[0]}x{a.shape[1]}.npy"
                np.save(os.path.join(out, "real", fn), a)
                real_cuts_meta[fn] = {"tile": t["label"], "side": side, "shape": list(a.shape),
                                      "sha256": sha_file(os.path.join(out, "real", fn)),
                                      "min": float(a.min()), "max": float(a.max()), "exact_zeros": int((a == 0).sum())}
    rm = info["real"]
    with open(os.path.join(out, "real", "provenance.json"), "w") as f:
        json.dump({"text": TEXT, "text_source": TEXT_SOURCE, "tokens_kept": T, "models": rm["models"],
                   "layers_run": rm["depth"], "plans": rm["plans"], "picks": rm["picks"],
                   "dequant_fp16_model": rm["dequant_fp16_model"], "fetched": rm["logs"], "cuts": real_cuts_meta,
                   "quantisation": "int8 A: q = clip(round_half_even(x / s), -127, 127), s = the token's max |x| over its "
                                   "whole row / 127 (the checkpoints' dynamic per-token symmetric int8, read as pool 7 "
                                   "read it); int8 B: the checkpoints' own int8 weights; fp16: round to nearest even",
                   "tiles": {t["label"]: t["params"] for t in tiles if t["cls"] == "R" and t["role"] == "kind"}},
                  f, indent=1)
        f.write("\n")
    with open(os.path.join(out, "MANIFEST"), "w") as f:
        for t in tiles:
            f.write(f"{t['sha']}  {t['file']}  {t['label']}  {t['fmt']}  case={t['cls']}  {t['prio']}  {t['role']}  "
                    f"{t['flag']}\n")
    with open(os.path.join(out, "RERUNS"), "w") as f:
        for t in tiles:
            if t["flag"].startswith("rerun"):
                p = t["params"]
                f.write(f"{t['label']}  {t['fmt']}  case={t['cls']}  role={t['role']}  from={p['from_pool']}  "
                        f"bus_bits_per_op={t['stats']['bus_bits_per_op']}  pick={p.get('pick', 'floor').replace(' ', '_')}\n")
    c = counts(tiles)
    prov = {"pool": "blind8", "made_by": gen, "seed": {"commit": SEED_COMMIT, "rule": SEED_RULE, "value": seed,
                                                       "hex": f"0x{seed:016x}"},
            "make_kinds_sha256": mk_sha, "python": sys.version.split()[0], "numpy": np.__version__,
            "made_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "counts": c, "quota": QUOTA, "quota_ok": quota_ok(c),
            "refused": refused, "inputs": {k: v for k, v in info.items() if k != "real"},
            "tiles": [{k: t[k] for k in ("label", "fmt", "cls", "role", "prio", "flag", "sha", "file", "rule", "params",
                                         "stats", "half_twins") if k in t} | {"byte_sig": t.get("byte_sig"),
                                                                                "slot": t.get("slot")}
                      for t in tiles]}
    with open(os.path.join(out, "provenance-blind8.json"), "w") as f:
        json.dump(prov, f, indent=1, default=str)
        f.write("\n")
    with open(os.path.join(out, "README.md"), "w") as f:
        f.write(readme(tiles, c, seed))
    lines = []
    for root, _, files in os.walk(out):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), out)
            if rel != "SHA256SUMS":
                lines.append(f"{sha_file(os.path.join(root, fn))}  {rel}")
    with open(os.path.join(out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(lines, key=lambda s: s.split("  ", 1)[1])) + "\n")
    return c


def readme(tiles, c, seed):
    rows = [("0", "Anchors (random a, b per format; the check anchor per format)", c["0"], QUOTA["0"]),
            ("S", "Single high B bits (fp32 and fp16)", c["S"], QUOTA["S"]),
            ("U", "Kinds aimed at no named class", c["U"], QUOTA["U"]),
            ("L+H", "int8 whole lines and held B", c["LH"], QUOTA["LH"]),
            ("R", f"Real tiles ({c['real_models']} models; {c['int8_w8a8_outlier']} int8 W8A8)", c["R"], QUOTA["R"]),
            ("rerun", "Re-runs of pool 6/7 float tiles, under their own labels", c["rerun"], QUOTA["rerun"]),
            ("floor", "The zero floor, pool 7's label, per format", c["floor"], "(kept as in every earlier pool)")]
    by = {}
    for t in tiles:
        by.setdefault((t["fmt"], "rerun" if t["role"] == "rerun" else t["cls"]), []).append(t)
    s = ["# Blind pool 8 (Q142(d))", "",
         f"Made by `make_blind8.py build` (the committed generator; DESIGN.md beside it is the design) from seed "
         f"`0x{seed:016x}`, the first 16 hex digits of sha256 of lab commit `{SEED_COMMIT}`. {c['total']} tiles of "
         f"2,048 bytes (A then B, make_kinds' layout) for `sparsity_host --test fma --type <fmt> --values file:<tile>`.",
         "", "Files: `MANIFEST` (pool 7's fields: sha256, file, label, format, case, priority, role, flag), `tiles/<fmt>/`, "
         "`RERUNS` (every tile whose bytes are an earlier pool's, under that pool's label), `provenance-blind8.json` (every "
         "tile's rule, seed stream, parameters, statistics and twin check), `real/` (the real cuts as float32 arrays and "
         "their provenance), `SHA256SUMS`.", "",
         "Roles: `anchor` (the random anchors a and b, and the floor), `check` (the check anchor: a third draw of the "
         "anchors' rule, held out to check the scale the two give), `kind` (new tiles), `rerun` (scored apart). "
         "Priorities: anchors p2 as in pool 7; in each other group a seeded quarter is p2.", "",
         "## What each class aims at", ""]
    for k in ("0", "S", "U", "L", "H", "R", "rerun"):
        s.append(f"- **{k}**: {CLASS_AIM[k]}")
    s += ["", "## Quotas", "", "| Class | What | Count | Quota |", "|---|---|---|---|"]
    for k, what, n, q in rows:
        s.append(f"| {k} | {what} | {n} | {q} |")
    s += [f"| all | | {c['total']} | |", "", "## Tiles by format and class", "", "| Format | Class | Tiles |", "|---|---|---|"]
    for (fmt, cl), ts in sorted(by.items(), key=lambda kv: (FORMATS.index(kv[0][0]), kv[0][1])):
        s.append(f"| {fmt} | {cl} | {len(ts)} |")
    s += ["", "## Checking it", "",
          "`python3 -I make_blind8.py check --out <this directory>` re-reads every tile, re-derives its label's byte part "
          "and its class structure from the bytes, re-checks make_kinds.encode, NaN/Inf, the byte twins against blind3-"
          "blind7, MANIFEST and SHA256SUMS. Re-running `build` from the same downloads reproduces every byte.", ""]
    return "\n".join(s)


# ------------------------------------------------------------------ check
def check_pool(out, kinds):
    mk, _ = load_make_kinds(kinds)
    earlier, _ = scan_earlier(kinds)
    by_sha = {}
    for t in earlier:
        by_sha.setdefault(t["sha"], set()).add(t["label"])
    with open(os.path.join(out, "provenance-blind8.json")) as f:
        prov = json.load(f)
    slots = {t["label"]: t for t in prov["tiles"]}
    problems, n = [], 0
    for row in read_manifest(os.path.join(out, "MANIFEST")):
        n += 1
        with open(os.path.join(out, row["file"]), "rb") as f:
            raw = f.read()
        if sha(raw) != row["sha"]:
            problems.append(f"{row['label']}: sha256 differs from MANIFEST")
        why = tile_refusal(raw, row["fmt"], mk)
        if why:
            problems.append(f"{row['label']}: {why}")
        p = slots.get(row["label"])
        if p is None:
            problems.append(f"{row['label']}: not in provenance")
            continue
        if row["flag"].startswith("rerun"):
            if row["label"] not in by_sha.get(row["sha"], set()):
                problems.append(f"{row['label']}: a re-run that is not byte for byte its own earlier tile")
            continue
        if row["sha"] in by_sha:
            problems.append(f"{row['label']}: byte twin of {sorted(by_sha[row['sha']])}")
        want = f"{row['fmt']}.{p['slot']}_{byte_sig(raw, row['fmt'], row['case'], mk)}"
        if want != row["label"]:
            problems.append(f"{row['label']}: the bytes give the label {want}")
        ok, cwhy = class_check(raw, row["fmt"], row["case"], row["role"], mk)
        if not ok:
            problems.append(f"{row['label']}: {cwhy}")
    with open(os.path.join(out, "SHA256SUMS")) as f:
        for line in f:
            h, rel = line.rstrip("\n").split("  ", 1)
            if sha_file(os.path.join(out, rel)) != h:
                problems.append(f"SHA256SUMS: {rel} differs")
    print(f"checked {n} tiles: {len(problems)} problems")
    for x in problems:
        print("  " + x)
    return 1 if problems else 0


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    f = sub.add_parser("fetch")
    f.add_argument("--dl", required=True)
    f.add_argument("--depth", type=int, default=DEPTH)
    f.add_argument("--cap-bytes", type=int, default=1_500_000_000)
    b = sub.add_parser("build")
    b.add_argument("--dl", required=True)
    b.add_argument("--out")
    b.add_argument("--test", action="store_true",
                   help="the test seed: build in memory and write nothing, or with --out a directory named TEST")
    b.add_argument("--summary", help="with --test: write the dry run's summary JSON here")
    b.add_argument("--kinds", default=KINDS_DEFAULT)
    c = sub.add_parser("check")
    c.add_argument("--out", required=True)
    c.add_argument("--kinds", default=KINDS_DEFAULT)
    a = ap.parse_args()
    if a.cmd == "seed":
        print(json.dumps({"commit": SEED_COMMIT, "rule": SEED_RULE, "value": SEED, "hex": f"0x{SEED:016x}"}))
        return 0
    if a.cmd == "fetch":
        budget = {"used": 0, "cap": a.cap_bytes}
        for key in REAL_KEYS:
            st = Store(a.dl, key, online=True, budget=budget)
            md = model_bytes(st, key, a.depth)
            with open(os.path.join(st.dirs["safetensors"], "DEPTH"), "w") as fh:
                fh.write(f"{a.depth}\n")
            with open(os.path.join(st.dirs["safetensors"], "FETCHED.json"), "w") as fh:
                json.dump({"repo": REAL_MODELS[key]["repo"], "revision": REAL_MODELS[key]["rev"], "depth": a.depth,
                           "tokens": md["ids"], "log": st.log}, fh, indent=1)
            print(f"{key}: {len(md['layers'])} layers, tokens {md['ids'][:8]}..., downloaded so far {budget['used']} bytes")
        print(f"fetched {budget['used']} bytes in all")
        return 0
    if a.cmd == "check":
        return check_pool(a.out, a.kinds)
    mk, mk_sha = load_make_kinds(a.kinds)
    gen = generator_identity()
    if a.test:
        tiles, refused, info = assemble(TEST_SEED, mk, a.kinds, a.dl, None)
        c = counts(tiles)
        summ = {"seed": "TEST", "counts": c, "quota_ok": quota_ok(c), "refused": refused,
                "tiles": [[t["label"], t["fmt"], t["cls"], t["prio"], t["role"], t["flag"], t["stats"]["bus_bits_per_op"]]
                          for t in tiles],
                "used_bits": info["used_bits"], "held_bytes_earlier": info["held_bytes_earlier"],
                "single_bit_earlier": info["single_bit_earlier"], "earlier": info["earlier"],
                "real_plans": info["real"]["plans"], "real_models": info["real"]["models"]}
        if a.summary:
            with open(a.summary, "w") as fh:
                json.dump(summ, fh, indent=1, default=str)
        if a.out:                                              # a test pool, on the test seed, to exercise write and check
            if os.path.basename(os.path.normpath(a.out)) == "pool" or "TEST" not in os.path.basename(os.path.normpath(a.out)):
                raise SystemExit("a --test pool goes in a directory whose name says TEST, never in pool/")
            write_pool(a.out, tiles, refused, info, TEST_SEED, mk_sha, gen)
        print(json.dumps({"counts": c, "quota_ok": quota_ok(c), "refused": refused}, default=str))
        for t in tiles:
            print(f"  {t['label']:52s} {t['fmt']} case={t['cls']} {t['prio']} {t['role']:6s} {t['flag']:13s} "
                  f"bus {t['stats']['bus_bits_per_op']:6d} gated {t['stats']['gated_lane_frac']:.3f}")
        return 0
    if not a.out:
        ap.error("build needs --out (or --test)")
    if not gen["committed"]:
        raise SystemExit(f"the generator differs from the committed one ({gen}): commit it (or a dated amendment) first")
    tiles, refused, info = assemble(SEED, mk, a.kinds, a.dl, DEPTH)
    c = write_pool(a.out, tiles, refused, info, SEED, mk_sha, gen)
    print(json.dumps({"counts": c, "quota_ok": quota_ok(c), "refused": refused}, default=str))
    for t in tiles:
        print(f"  {t['label']:52s} {t['fmt']} case={t['cls']} {t['prio']} {t['role']:6s} {t['flag']:13s} "
              f"bus {t['stats']['bus_bits_per_op']:6d} gated {t['stats']['gated_lane_frac']:.3f}")
    if not all(quota_ok(c).values()):
        print("QUOTA NOT MET", quota_ok(c), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
