#!/usr/bin/env python3
"""E224, post hoc desk check for R0 (written Sat 21 Nov 2026 PST by the lab's fix lane after verify-e224d; DESK, POST HOC, REPORTED;
NOT TESTED on a card). Why the host's check of C read 'wrong' at E224's two fp16 pattern points p3a and p3b (gemmL1x1x25: K 25,600, so
800 k-tiles of 32 per C tile) while the same two tiles read 'approx' at gemmL1x1x1 (K 1,024, 32 k-tiles) in E212's and E217's sessions.

What it reads (all committed in this repository): the two tile files, and the check records the hosts printed (E224's eight p3a/p3b runs
on both arms; E212's and E217's five gemmL1x1x1 runs of the same tiles). What it does, with the host's own definitions (rgm136
host/main.cpp, sha256 f9b2279f..., the source E224 built on both arms):
  - decodes each tile as the host's Elems does for fp16 (A[i][k] at byte i*64 + 2k; B[k][j] at line k/2, half (2j + k%2); halfValue);
  - with one tile file every A tile and every B tile of the pools is that file's tile (the host's fill), so every C tile is the same
    16 x 16 partial product summed over the k-tiles, and the 64 sampled C tiles are equal: a count over 16,384 words is 64 times a count
    over 256 (12,160 = 190 x 64);
  - makes the host's reference: want and abs (the sum of |products|) in double, in the host's order (each k-tile, then k);
  - emulates candidate fp32 accumulations of the card (models, not the card's datapath, which is not documented here):
      fused-g<g>-<RNE|RZ>: the 32 products of a k-tile in groups of g consecutive k, each group summed exactly, then added to the fp32
        accumulator with one rounding, to nearest even (RNE) or toward zero (RZ), g in 1, 2, 4, 8, 16, 32;
      align-g<g>-guard<G>-<RNE|RZ>: an adder that truncates the smaller operand toward zero at alignment, keeping G guard bits below the
        larger operand's fp32 least significant bit (no sticky bit), then rounds the sum, g in 1, 2 and G in 0-3;
    every addition is formed exactly in 80-bit extended precision (asserted: every value is a multiple of 2^bottom below 2^top with
    top - bottom <= 63) and rounded once to fp32;
  - counts, per 256-word C tile, the words within the host's tolerance (|C - want| <= 1e-4 x abs) and the words exact (C == want), at
    800 and 32 k-tiles, against the measured counts.
Products of two halves are exact in fp32 and in double (22-bit significands); neither tile holds a zero, subnormal, Inf or NaN half.

Usage, from the top folder of the repository (or with --repo <that folder>): python3 <this file> [--repo <folder>] [--json <out.json>]
Needs Python 3 and numpy with an 80-bit long double (x86-64 Linux); single-threaded. It prints its lines and, with --json, writes them.
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys
from fractions import Fraction

import numpy as np

LD = np.longdouble
TILES = {
    "p3a": ("fld16_mant", "tools/claims-v3/e212/proposal/src/tiles/fp16/fld16_mant.bin",
            "a7d401d3e2f880f3693b59403e0bb423d068ddf8ba0a34f3281001a23e068c73"),
    "p3b": ("h_th_in", "tools/claims-v3/e217/proposal/src/tiles/fp16/h_th_in.bin",
            "c5da4e977eb0425709a485cc5a19fd419f0654eaed355dbbad27640d80cb3a67"),
}
D = "docs/reports/data/"
RECORDS = {  # (point, k-tiles): the committed check records of the tile (each prints words, exact, within, result)
    ("p3a", 800): [D + "2026-11-21-e224-blind-matmul-aifoundry1-c1/session/runs/035-pass1-p3a/proc-00.out",
                   D + "2026-11-21-e224-blind-matmul-aifoundry1-c1/session/runs/076-pass2-p3a/proc-00.out",
                   D + "2026-11-21-e224-blind-matmul-aifoundry2/session/runs/040-p3a/proc-00.out",
                   D + "2026-11-21-e224-blind-matmul-aifoundry2/session/runs/073-p3a/proc-00.out"],
    ("p3b", 800): [D + "2026-11-21-e224-blind-matmul-aifoundry1-c1/session/runs/008-pass1-p3b/proc-00.out",
                   D + "2026-11-21-e224-blind-matmul-aifoundry1-c1/session/runs/092-pass2-p3b/proc-00.out",
                   D + "2026-11-21-e224-blind-matmul-aifoundry2/session/runs/014-p3b/proc-00.out",
                   D + "2026-11-21-e224-blind-matmul-aifoundry2/session/runs/085-p3b/proc-00.out"],
    ("p3a", 32): [D + "2026-11-17-e212-mmsweep2-a1c1-S2/session/runs/068-1x1x1-fp16-fld16_mant/proc-00.out",
                  D + "2026-11-17-e212-mmsweep2-a1c1-S3/session/runs/060-1x1x1-fp16-fld16_mant/proc-00.out"],
    ("p3b", 32): [D + "2026-11-19-e217-mmsweep4-a1c1-S3/session/runs/079-1x1x1-fp16-h_th_in/proc-00.out",
                  D + "2026-11-19-e217-mmsweep4-a1c1-S4/session/runs/060-1x1x1-fp16-h_th_in/proc-00.out",
                  D + "2026-11-19-e217-mmsweep4-a1c0-S3/session/runs/084-1x1x1-fp16-h_th_in-s8/proc-00.out"],
}
ARM = {800: "gemmL1x1x25", 32: "gemmL1x1x1"}
TOL = 1e-4


def half(h):
    """the host's halfValue, exact"""
    e, m = (h >> 10) & 0x1F, h & 0x3FF
    v = m * 2.0 ** -24 if e == 0 else (0x400 + m) * 2.0 ** (e - 25)
    return -v if h & 0x8000 else v


def decode(raw):
    A = np.empty((16, 32))
    B = np.empty((32, 16))
    hs = []
    for i in range(16):
        for k in range(32):
            h = struct.unpack_from("<H", raw, i * 64 + 2 * k)[0]
            A[i, k] = half(h)
            hs.append(h)
    for k in range(32):
        for j in range(16):
            h = struct.unpack_from("<H", raw, 1024 + (k // 2) * 64 + (2 * j + k % 2) * 2)[0]
            B[k, j] = half(h)
            hs.append(h)
    return A, B, hs


def halves_stats(hs):
    ex = {}
    for h in hs:
        e = (h >> 10) & 0x1F
        ex[e] = ex.get(e, 0) + 1
    return {"halves": len(hs), "negative": sum(1 for h in hs if h & 0x8000), "zero": sum(1 for h in hs if (h & 0x7FFF) == 0),
            "subnormal": sum(1 for h in hs if (h >> 10) & 0x1F == 0 and h & 0x3FF), "exp31": sum(1 for h in hs if (h >> 10) & 0x1F == 31),
            "exponent_fields": {str(k): ex[k] for k in sorted(ex)}}


def rnd(x, mode):
    """x: exact values (long double array) -> fp32, rounded once: to nearest even, or toward zero"""
    f = x.astype(np.float32)
    if mode == "RZ":
        over = np.abs(f.astype(LD)) > np.abs(x)
        f[over] = np.nextafter(f[over], np.float32(0))
    return f


def host_ref(P, nt):
    want = np.zeros((16, 16))
    ab = np.zeros((16, 16))
    for _ in range(nt):
        for k in range(32):
            want += P[:, k, :]
            ab += np.abs(P[:, k, :])
    return want, ab


def fused(P, nt, g, mode):
    groups = [P[:, s:s + g, :].astype(LD).sum(axis=1) for s in range(0, 32, g)]
    acc = np.zeros((16, 16), dtype=np.float32)
    for _ in range(nt):
        for G in groups:
            acc = rnd(acc.astype(LD) + G, mode)
    return acc


def add_align(acc, b, guard, mode):
    a = acc.astype(LD)
    first = np.abs(a) >= np.abs(b)
    big = np.where(first, a, b)
    small = np.where(first, b, a)
    _, e = np.frexp(big)                           # big = m 2^e, 0.5 <= |m| < 1: its fp32 lsb is 2^(e - 24)
    q = np.ldexp(np.ones_like(big), e - 24 - guard)
    return rnd(big + np.trunc(small / q) * q, mode)


def align(P, nt, g, guard, mode):
    groups = [P[:, s:s + g, :].astype(LD).sum(axis=1) for s in range(0, 32, g)]
    acc = np.zeros((16, 16), dtype=np.float32)
    for _ in range(nt):
        for G in groups:
            acc = add_align(acc, G, guard, mode)
    return acc


def lowbit_exp(x):
    """exponent of the lowest set bit of a nonzero double"""
    fr = Fraction(x)
    n, d = abs(fr.numerator), fr.denominator
    e = -(d.bit_length() - 1)
    while n % 2 == 0:
        n //= 2
        e += 1
    return e


def self_tests():
    out = []
    assert np.finfo(LD).nmant >= 63, "needs an 80-bit long double"
    assert half(0x3C00) == 1.0 and half(0xC000) == -2.0 and half(0x0001) == 2.0 ** -24 and half(0x7BFF) == 65504.0
    x = np.array([LD(1) + LD(2) ** -24 + LD(2) ** -60, -(LD(1) + LD(2) ** -24 + LD(2) ** -60), LD(1) + LD(2) ** -24], dtype=LD)
    r, z = rnd(x.copy(), "RNE"), rnd(x.copy(), "RZ")
    assert r[0] == np.float32(1 + 2.0 ** -23) and r[1] == np.float32(-(1 + 2.0 ** -23)) and r[2] == np.float32(1.0), r
    assert z[0] == np.float32(1.0) and z[1] == np.float32(-1.0) and z[2] == np.float32(1.0), z
    out.append("self-test: halfValue 4/4; one rounding to fp32 from 80 bits (RNE above a tie, RNE at a tie to even, RZ) 6/6: OK")
    return out


def read_record(top, rel):
    s = open(os.path.join(top, rel), encoding="utf-8").read()
    m = re.search(r'\{"test":"check"[^\n]*\}', s)
    d = json.loads(m.group(0))
    return {"record": rel, "arm": d["arm"], "type": d["type"], "words": d["words"], "exact": d["exact"], "within": d["within"],
            "result": d["result"]}


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(here, "..", "..", "..", "..")))
    ap.add_argument("--json")
    a = ap.parse_args()
    lines = self_tests()
    res = {"what": "E224 post hoc desk check for R0 (DESK, POST HOC, REPORTED; NOT TESTED on a card)", "tolerance": TOL,
           "measured": {}, "tiles": {}, "models": {}}
    measured = {}
    for (pt, nt), recs in RECORDS.items():
        rows = [read_record(a.repo, r) for r in recs]
        for r in rows:
            assert r["arm"] == ARM[nt] and r["type"] == "fp16" and r["words"] == 16384, r
            assert r["within"] % 64 == 0 and r["exact"] % 64 == 0, r
        within = sorted({r["within"] for r in rows})
        exact = sorted({r["exact"] for r in rows})
        assert len(within) == 1 and len(exact) == 1, rows
        measured[(pt, nt)] = (within[0] // 64, exact[0] // 64)
        res["measured"][f"{pt} {nt}"] = {"records": rows, "per_256_word_tile": {"within": within[0] // 64, "exact": exact[0] // 64}}
        lines.append(f"measured {pt} at {nt} k-tiles ({ARM[nt]}): {len(rows)} records, each words 16384, within {within[0]}, exact {exact[0]}, "
                     f"result {sorted({r['result'] for r in rows})[0]}: per 256-word tile within {within[0] // 64}, exact {exact[0] // 64}")
    models = [(f"fused-g{g}-{m}", ("fused", g, None, m)) for m in ("RNE", "RZ") for g in (1, 2, 4, 8, 16, 32)]
    models += [(f"align-g{g}-guard{G}-{m}", ("align", g, G, m)) for g in (1, 2) for G in (0, 1, 2, 3) for m in ("RNE", "RZ")]
    for pt, (name, rel, sha) in TILES.items():
        raw = open(os.path.join(a.repo, rel), "rb").read()
        got = hashlib.sha256(raw).hexdigest()
        assert got == sha and len(raw) == 2048, (rel, got, len(raw))
        A, B, hs = decode(raw)
        st = halves_stats(hs)
        P = A[:, :, None] * B[None, :, :]                         # exact: two 11-bit significands
        bottom = min(lowbit_exp(float(v)) for v in P.ravel() if v != 0)
        top = int(np.ceil(np.log2(800 * np.abs(P).sum(axis=1).max()))) + 1
        assert top - bottom <= 63, (pt, top, bottom)
        part = P.sum(axis=1)
        absp = np.abs(P).sum(axis=1)
        canc = float(np.median(np.abs(part) / absp))
        res["tiles"][pt] = {"tile": name, "file": rel, "sha256": got, "halves": st, "products_exact_bits": {"top": top, "bottom": bottom},
                            "partial_product_min": float(part.min()), "partial_product_max": float(part.max()),
                            "partial_negative_words": int((part < 0).sum()), "median_abs_sum_over_sum_abs": canc}
        lines.append(f"{pt} = {name} ({rel}, sha256 {got[:16]}...): {st['halves']} halves, {st['negative']} negative, {st['zero']} zero, "
                     f"{st['subnormal']} subnormal, {st['exp31']} Inf/NaN; exponent fields {st['exponent_fields']}; one k-tile's partial "
                     f"product {part.min():.6g} to {part.max():.6g}, {int((part < 0).sum())} of 256 words negative, median |sum| / sum|p| {canc:.4f}; "
                     f"exact span 2^{bottom} .. 2^{top}")
        refs = {nt: host_ref(P, nt) for nt in (800, 32)}
        for mname, (kind, g, G, mode) in models:
            row = {}
            for nt in (800, 32):
                want, ab = refs[nt]
                c = (fused(P, nt, g, mode) if kind == "fused" else align(P, nt, g, G, mode)).astype(np.float64)
                err = np.abs(c - want)
                rel_err = err / ab
                row[str(nt)] = {"within": int((err <= TOL * ab).sum()), "exact": int((c == want).sum()),
                                "rel_err_median": float(np.median(rel_err)), "rel_err_max": float(rel_err.max())}
            res["models"].setdefault(mname, {})[pt] = row
    # the reading
    lines.append("models: per 256-word tile, within / exact at 800 k-tiles; at 32 k-tiles; the median |C - want| / abs at 800 (p3a, p3b)")
    for mname in res["models"]:
        r = res["models"][mname]
        lines.append(f"  {mname:22s} p3a 800 {r['p3a']['800']['within']:3d}/{r['p3a']['800']['exact']:<3d} 32 {r['p3a']['32']['within']:3d}/{r['p3a']['32']['exact']:<3d}"
                     f" | p3b 800 {r['p3b']['800']['within']:3d}/{r['p3b']['800']['exact']:<3d} 32 {r['p3b']['32']['within']:3d}/{r['p3b']['32']['exact']:<3d}"
                     f" | rel err {r['p3a']['800']['rel_err_median']:.2e}, {r['p3b']['800']['rel_err_median']:.2e}")
    ma = {(pt, nt): measured[(pt, nt)] for pt in ("p3a", "p3b") for nt in (800, 32)}

    def fits(r, pt, nt):
        return (r[pt][str(nt)]["within"], r[pt][str(nt)]["exact"]) == ma[(pt, nt)]
    fit_a = [m for m, r in res["models"].items() if fits(r, "p3a", 800) and fits(r, "p3a", 32)]
    fit_b32 = [m for m in fit_a if fits(res["models"][m], "p3b", 32)]
    b800 = sorted({res["models"][m]["p3b"]["800"]["within"] for m in fit_b32})
    fit_all = [m for m in fit_b32 if fits(res["models"][m], "p3b", 800)]
    rne_a800 = sorted({r["p3a"]["800"]["within"] for m, r in res["models"].items() if m.startswith("fused") and m.endswith("RNE")})
    rne_a32x = sorted({r["p3a"]["32"]["exact"] for m, r in res["models"].items() if m.startswith("fused") and m.endswith("RNE")})
    res["reading"] = {"fit_p3a_both_depths": fit_a, "of_those_fit_p3b_at_32": fit_b32, "their_p3b_within_at_800": b800,
                      "fit_all_four_counts": fit_all, "fused_RNE_p3a_within_at_800": rne_a800, "fused_RNE_p3a_exact_at_32": rne_a32x,
                      "estimate_rz_loss_relative": {"800": 800 * 32 * 2.0 ** -25, "32": 32 * 32 * 2.0 ** -25}}
    lines.append(f"models giving p3a's measured counts at both depths (800: 0/0, 32: 256/0): {len(fit_a)}: {', '.join(fit_a)}")
    lines.append(f"  of those, also p3b's at 32 k-tiles (256/0): {len(fit_b32)}; their p3b within at 800 k-tiles: {b800} (measured 190)")
    lines.append(f"  models giving all four measured counts: {len(fit_all)}{': ' + ', '.join(fit_all) if fit_all else ''}")
    lines.append(f"fused round-to-nearest models: p3a within at 800 k-tiles {rne_a800}; p3a exact words at 32 k-tiles {rne_a32x} (measured 0)")
    lines.append(f"the loss of an accumulator that truncates, about K x 2^-25 of an all-positive sum: {800 * 32 * 2.0 ** -25:.2e} at K 25,600, "
                 f"{32 * 32 * 2.0 ** -25:.2e} at K 1,024, against the tolerance {TOL:g}")
    res["lines"] = lines
    print("\n".join(lines))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, sort_keys=True)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
