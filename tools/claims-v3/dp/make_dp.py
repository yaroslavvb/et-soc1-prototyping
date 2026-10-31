#!/usr/bin/env python3
"""V3-DP (E81, the DRAM pattern question): the operand images, the per-item commands, and every count.

    python3 tools/claims-v3/dp/make_dp.py <out-dir>                      # srcs/, manifest.json
    python3 tools/claims-v3/dp/make_dp.py <out-dir> --check              # re-derive every count from the bytes
    python3 tools/claims-v3/dp/make_dp.py <out-dir> --check --builtins <dir with random.bin bern50.bin>
                                                                         # + the built-in operands' realized counts
    python3 tools/claims-v3/dp/make_dp.py <out-dir> --check --e75-gen <E75 mf-gen dir>
                                                                         # + byte identity with E75's two rungs

## The question

E75 split DRAM's zeros-to-random chord into a price per changed bit and a price per carried one, using images
built from two values alternating (a 2-cycle, a b a b ...), and found that those two designed counts explain only
36.6 % of the chord (95 % [30.0, 43.3]); a random image costs about 1.1-1.2 W more than the two-term model says it
should. Its registration named the risk in advance: a two-value alternating image is maximally correlated, and if
the DRAM path compresses it in any way random data is not, the ladder measures the 2-cycle and not the general
case. The Horace hub's Status item 6 asks for the test: a third image at the same changed-bit and carried-one
counts, but a longer period.

Two properties of E75's images differ from random data at once, and E81 separates them:

  * the PERIOD (how many distinct lines the stream cycles through): E75's images repeat every 2 lines (k > 0) or
    every line (k = 0); `--operands random` fills a 512 KB source, 8,192 distinct lines, so every hart's 2,048-line
    region holds distinct lines. A path that sees repeated values (a channel that only ever gets the even lines,
    an encoding with memory, anything that compresses repetition) pays less for a short period.
  * the ARRANGEMENT inside a line: E75's two_values() puts the toggling group and the static ones in contiguous
    runs (bits 0..k-1, then k..k+s-1), so a 64 B line is a few long runs of ones and zeros. Random data has its
    ones scattered. Any path narrower than a line (a 16-bit DQ bus that moves a line as 32 beats, a 32 B burst)
    toggles between the pieces of ONE line, and contiguous runs barely toggle it.

## The images (DRAM only; E75's exact command: flw_pat, --stride 64, 128 KB per hart, --harts 1)

Every file image is 256 B = four 512-bit lines, repeated by the host through every slice (E75's construction).
The scattered images are the contiguous ones with ONE fixed permutation pi of the 512 bit positions applied to
every line, so a contiguous image and its scattered twin carry exactly the same counts and differ only in where
the bits sit. All counts below are exact for the file images and re-derived from the bytes by --check.

| item | period (lines) | arrangement | k changed bits between consecutive lines | w ones per line |
|---|---|---|---|---|
| dp_c1   | 1 | contiguous (= E75's mf_dram_k0 bytes)    | 0   | 256 |
| dp_s1   | 1 | scattered, pi(c1)                         | 0   | 256 |
| dp_c2   | 2 | contiguous (= E75's mf_dram_k256 bytes)  | 256 | 256 |
| dp_s2   | 2 | scattered, pi(c2)                         | 256 | 256 |
| dp_c4   | 4 | contiguous 64-bit blocks, Hadamard rows   | 256 | 256 (every pair of distinct lines differs in 256) |
| dp_s4   | 4 | scattered, pi(c4)                         | 256 | 256 (every pair of distinct lines differs in 256) |
| dp_bern | 2,048 per hart (8,192 in the source) | Bernoulli(0.5) bits (`--operands bern:0.5`) | 256 expected | 256 expected |
| dp_c2r  | 2 | contiguous, two_values(512, 4, 192, 290)  | 192 | 290 (random's own counts, rounded) |
| dp_s2r  | 2 | scattered, pi(c2r)                        | 192 | 290 |
| dp_zeros, dp_random | E75's two anchors, unchanged (`--operands zeros`, `--operands random`) | | 0 / 191 | 0 / 291 |

The Hadamard 4-cycle: the eight 64-bit blocks of a line take the rows 01010101, 00110011, 01100110, 00001111 of
an order-8 Hadamard design (block j all ones where the row has a 1), so each line has 256 ones and any two of the
four lines differ in exactly 256 bits — like random data, whatever order a path sees them in. In E75's 2-cycle
the two values also differ in 256 bits; in a period-1 image every line is the same.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
from make_mf import WINDOW, args_for, image, two_values  # noqa: E402  (E75's construction, unchanged)

ELEM, N = 512, 4                      # bits per line, lines per 256 B image
PERM_SEED = 0xE81                     # the one permutation of the 512 bit positions
HADAMARD = ["01010101", "00110011", "01100110", "00001111"]
SLICE = 131072                        # E75's DRAM working set per hart, and its --region
SLICE_STRIDE = SLICE + 8192           # the host adds 8 KB of bank-spread slack per slice (flw_pat)
SRC_BYTES = 2048 * 256                # sources(): EC_MAX_HARTS x 256 B, the period of a built-in fill
ACTIVE_HARTS = list(range(0, 2048, 2))   # --harts 1: thread 0 of each of 1,024 minions
BUS_BITS = (16, 32, 64, 256)          # the narrower paths a line might cross, for the derived toggle counts


def splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return x, z ^ (z >> 31)


def permutation(n=ELEM, seed=PERM_SEED):
    """Fisher-Yates over 0..n-1 driven by splitmix64: portable, so any machine rebuilds the same pi."""
    p = list(range(n))
    s = seed
    for i in range(n - 1, 0, -1):
        s, r = splitmix64(s)
        j = r % (i + 1)
        p[i], p[j] = p[j], p[i]
    return p


def permute(v, pi):
    """Bit i of v moves to position pi[i]."""
    out = 0
    for i in range(ELEM):
        if (v >> i) & 1:
            out |= 1 << pi[i]
    return out


def hadamard_line(row):
    v = 0
    for j, c in enumerate(row):
        if c == "1":
            v |= ((1 << 64) - 1) << (64 * j)
    return v


def lines_image(lines):
    out = b"".join(x.to_bytes(ELEM // 8, "little") for x in lines)
    if len(out) != 256:
        raise ValueError("an image is 256 B")
    return out


def build_images():
    pi = permutation()
    a2, b2 = two_values(ELEM, N, 256, 256)            # E75's mf_dram_k256
    a1, b1 = two_values(ELEM, N, 0, 256)              # E75's mf_dram_k0 (a1 == b1)
    ar, br = two_values(ELEM, N, 192, 290)            # random's own counts, E75's construction
    h = [hadamard_line(r) for r in HADAMARD]
    imgs = {
        "dp_c1": [a1, b1, a1, b1],
        "dp_s1": [permute(x, pi) for x in (a1, b1, a1, b1)],
        "dp_c2": [a2, b2, a2, b2],
        "dp_s2": [permute(x, pi) for x in (a2, b2, a2, b2)],
        "dp_c4": h,
        "dp_s4": [permute(x, pi) for x in h],
        "dp_c2r": [ar, br, ar, br],
        "dp_s2r": [permute(x, pi) for x in (ar, br, ar, br)],
    }
    return imgs, pi


# ---- counting, on the bytes as each hart's region holds them -------------------------------------------------
def to_bits(blob):
    """bytes -> (n_lines, 512) uint8 bit matrix, bit i of a line = bit i of its little-endian integer."""
    a = np.frombuffer(blob, dtype=np.uint8).reshape(-1, 64)
    return np.unpackbits(a, axis=1, bitorder="little")


def region_lines(src_bits, h):
    """The 2,048 lines hart h's flw_pat region holds, as row indices into the source's line matrix."""
    base = h * SLICE_STRIDE + ((h >> 1) & 7) * 1024
    n_src = src_bits.shape[0]
    first = (base % (n_src * 64)) // 64
    return (first + np.arange(SLICE // 64)) % n_src


def stream_counts(src_bits, harts=ACTIVE_HARTS):
    """Per-line means over every active hart's region, in the order flw_pat reads it (the lap wraps to line 0).
    A 256 B image starts every region at its own line 0 (slice strides and bank offsets are multiples of 1 KB), so
    one hart stands for all of them; a built-in 512 KB source is counted over all 1,024 regions."""
    if (src_bits.shape[0] * 64) <= 1024 and 1024 % (src_bits.shape[0] * 64) == 0 \
            and SLICE_STRIDE % (src_bits.shape[0] * 64) == 0:
        harts = harts[:1]
    acc = {"k": [], "w": [], "half": []}
    for b in BUS_BITS:
        acc["beat%d" % b] = []
    distinct = set()
    n_src = src_bits.shape[0]
    for h in harts:
        idx = region_lines(src_bits, h)
        L = src_bits[idx]                                   # (2048, 512)
        nxt = np.roll(L, -1, axis=0)
        acc["k"].append((L != nxt).sum(axis=1).mean())
        acc["w"].append(L.sum(axis=1).mean())
        acc["half"].append((L[:, :256] != L[:, 256:]).sum(axis=1).mean())
        for b in BUS_BITS:
            # consecutive b-bit pieces of a line, in order, then the last piece of a line against the first of
            # the next line (a hypothetical in-order mapping onto a b-bit path, for the derived reading only)
            P = L.reshape(L.shape[0], ELEM // b, b)
            inside = (P[:, 1:, :] != P[:, :-1, :]).sum(axis=(1, 2))
            across = (P[:, -1, :] != np.roll(P, -1, axis=0)[:, 0, :]).sum(axis=1)
            acc["beat%d" % b].append((inside + across).mean())
        distinct.update(np.unique(idx).tolist())
    out = {k: float(np.mean(v)) for k, v in acc.items()}
    out["distinct_lines_in_all_regions"] = len(distinct)
    out["distinct_lines_per_hart_region"] = int(len(np.unique(region_lines(src_bits, harts[0]))))
    # how far apart two lines of the alphabet are, whatever order a shared path interleaves them in
    U = np.unique(src_bits[sorted(distinct)], axis=0) if len(distinct) <= 4096 else None
    if U is not None and len(U) > 1:
        d = [(U[i] != U[j]).sum() for i in range(len(U)) for j in range(i + 1, len(U))]
        out["alphabet_size"] = int(len(U))
        out["alphabet_pairwise_distance_mean"] = float(np.mean(d))
    elif U is not None:
        out["alphabet_size"] = 1
        out["alphabet_pairwise_distance_mean"] = 0.0
    else:
        rng = np.random.default_rng(0)
        ii = rng.integers(0, src_bits.shape[0], 4000)
        jj = rng.integers(0, src_bits.shape[0], 4000)
        out["alphabet_size"] = int(np.unique(src_bits, axis=0).shape[0])
        out["alphabet_pairwise_distance_mean"] = float((src_bits[ii] != src_bits[jj]).sum(axis=1).mean())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--builtins", help="a directory with dp-replica's random.bin and bern50.bin (512 KB each)")
    ap.add_argument("--e75-gen", help="E75's make_mf.py output, to check dp_c1 / dp_c2 are its k0 / k256 bytes")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "srcs"), exist_ok=True)
    imgs, pi = build_images()
    designed = {"dp_c1": (0, 256), "dp_s1": (0, 256), "dp_c2": (256, 256), "dp_s2": (256, 256),
                "dp_c4": (256, 256), "dp_s4": (256, 256), "dp_c2r": (192, 290), "dp_s2r": (192, 290)}
    period = {"dp_c1": 1, "dp_s1": 1, "dp_c2": 2, "dp_s2": 2, "dp_c4": 4, "dp_s4": 4, "dp_c2r": 2, "dp_s2r": 2}
    arr = {n: ("scattered" if n.startswith("dp_s") else "contiguous") for n in designed}
    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"}]
    for name, lines in imgs.items():
        blob = lines_image(lines)
        open(os.path.join(a.out, "srcs", name + ".bin"), "wb").write(blob)
        k, w = designed[name]
        items.append({"name": name, "kind": "cmd", "tool": "main", "family": "dp_file", "level": "dram",
                      "src": "%GEN%/srcs/" + name + ".bin", "src_bytes": 256, "k": k, "w": w,
                      "period_lines": period[name], "arrangement": arr[name], "elem_bits": ELEM, "n_elem": N,
                      "unit": "DRAM, 128 MB in all", "tag": "ENERCAT {",
                      "args": args_for("dram", name),
                      "designed": "%d bits change between consecutive lines, %d ones in each; period %d; %s"
                                  % (k, w, period[name], arr[name])})
    # the built-in operands, E75's anchor commands verbatim, plus Bernoulli(0.5) through the same command shape
    bern_args = [x if x != "random" else "bern:0.5" for x in args_for("dram", "random")]
    for name, args, k, w, desc in (
            ("dp_zeros", args_for("dram", None), 0, 0, "E75's zeros anchor: no ones, no changes"),
            ("dp_random", args_for("dram", "random"), 191, 291,
             "E75's random anchor: floats in [0.5, 2); 8,192 distinct lines in the 512 KB source"),
            ("dp_bern", bern_args, 256, 256,
             "Bernoulli(0.5) bits: 256 changes and 256 ones per line expected; 8,192 distinct lines")):
        items.append({"name": name, "kind": "cmd", "tool": "main", "family": "dp_builtin", "level": "dram",
                      "k": k, "w": w, "period_lines": 8192, "arrangement": "random",
                      "elem_bits": ELEM, "n_elem": N, "unit": "DRAM, 128 MB in all", "tag": "ENERCAT {",
                      "args": args, "designed": desc})
    man = {"exp": "E81", "elem_bits": ELEM, "lines_per_image": N, "perm_seed": PERM_SEED, "perm": pi,
           "hadamard_rows": HADAMARD, "window": WINDOW, "slice_bytes": SLICE, "slice_stride": SLICE_STRIDE,
           "items": items}
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print("%d items -> %s" % (len(items), a.out))

    if not a.check:
        return
    bad = 0
    counts = {}
    for it in items:
        if it.get("src"):
            blob = open(it["src"].replace("%GEN%", a.out), "rb").read()
            c = stream_counts(to_bits(blob))
            exact_k = c["k"] == it["k"]
            exact_w = c["w"] == it["w"]
            per = c["alphabet_size"] == it["period_lines"]
            ok = len(blob) == 256 and exact_k and exact_w and per
            if it["name"] in ("dp_c4", "dp_s4"):
                ok = ok and c["alphabet_pairwise_distance_mean"] == 256.0
            counts[it["name"]] = c
            print("%s %-9s k=%-7.2f w=%-7.2f alphabet=%d pairwise=%-6.1f beat16=%-6.1f beat32=%-6.1f half=%-6.1f"
                  % ("ok " if ok else "BAD", it["name"], c["k"], c["w"], c["alphabet_size"],
                     c["alphabet_pairwise_distance_mean"], c["beat16"], c["beat32"], c["half"]))
            bad += 0 if ok else 1
    # the scattered twin of every contiguous image holds the same multiset of counts by construction; check pi
    if sorted(pi) != list(range(ELEM)):
        print("BAD pi is not a permutation")
        bad += 1
    if a.e75_gen:
        for mine, theirs in (("dp_c1", "mf_dram_k0"), ("dp_c2", "mf_dram_k256")):
            x = open(os.path.join(a.out, "srcs", mine + ".bin"), "rb").read()
            y = open(os.path.join(a.e75_gen, "srcs", theirs + ".bin"), "rb").read()
            same = hashlib.sha256(x).hexdigest() == hashlib.sha256(y).hexdigest()
            print("%s %s == E75 %s (sha256 %s)" % ("ok " if same else "BAD", mine, theirs,
                                                     hashlib.sha256(x).hexdigest()[:16]))
            bad += 0 if same else 1
    if a.builtins:
        for name, fn in (("dp_random", "random.bin"), ("dp_bern", "bern50.bin")):
            p = os.path.join(a.builtins, fn)
            blob = open(p, "rb").read()
            if len(blob) != SRC_BYTES:
                print("BAD %s is %d bytes, not %d" % (p, len(blob), SRC_BYTES))
                bad += 1
                continue
            c = stream_counts(to_bits(blob))
            c["sha256"] = hashlib.sha256(blob).hexdigest()
            counts[name] = c
            print("ok  %-9s k=%-7.2f w=%-7.2f lines=%d pairwise=%-6.1f beat16=%-6.1f beat32=%-6.1f half=%-6.1f"
                  % (name, c["k"], c["w"], c["alphabet_size"], c["alphabet_pairwise_distance_mean"],
                     c["beat16"], c["beat32"], c["half"]))
        zero = stream_counts(np.zeros((4, ELEM), dtype=np.uint8))
        counts["dp_zeros"] = zero
    json.dump(counts, open(os.path.join(a.out, "counts.json"), "w"), indent=1)
    print("check: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
