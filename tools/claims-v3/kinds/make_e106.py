#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E106 (Q132): a random sign's ~5 W split on ONE card: `signs` and `ones` beside held tiles with the signs moving, read back. The tiles and the expected accumulators. Desk compute only; the registration is E106.md.

    python3 tools/claims-v3/kinds/make_e106.py            # writes e106/tiles/<type>/<kind>.bin and e106/e106.json
    python3 tools/claims-v3/kinds/make_e106.py --check

THE GAP (E104's verifier). The ±1 step never ran on card 1: E104's shares carried it from aifoundry3 by 0.9722. And fp16 had no held tile with both operands' signs moving: `z_s` keeps A's signs still.

THE NEW fp16 TILES. All hold C on the RTL, the manual and fl(n S) alike, so the read-back can fail them. k-group-0 is the seed; the rest moves only signs.
  x_c    A words (1, 1), B words (lo, hi) = (1, -1), k-group-0 (2, 2) x (4, 4): each micro-op's products cancel exactly, C = +16 n, no sign moves: the held baseline for x_s
  x_s    x_c with each A word's sign and each B word's sign drawn at random at k-group >= 1 (A s (1, 1), B t (1, -1)): the products still cancel inside each micro-op, so C = +16 n, on nonzero aligned operands. eff_sub1 and eff_sub2 flip together, in opposite phase
  z_ss   E92's fp16.s_abs's B words (+-1 in each half, at random), A words at random among the raw-nonzero zeros (-0, -0), (+0, -0), (-0, +0) at k-group >= 1, the seed of c_abs: products zero, C = n 2^31, both eff_sub flip independently and A's sign bits move. Its baseline is c_abs. (+0, +0) would close the gate
fp32 has one product and needs neither: E88's fp32.s_abs (random +-1 both sides, absorbed) already holds with both operands' signs moving, read back in E104, and fp32's zero words cannot carry A's signs.
Reused byte for byte: E78's fp32.ones, fp16.ones; E92's fp32.signs, fp16.signs, fp32.c_abs, fp16.c_abs, fp32.s_abs.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_e104 as e  # noqa: E402

me, m92, m90, mk = e.me, e.m92, e.m90, e.mk
OUT = os.path.join(HERE, "e106")
ROOT = e.ROOT
SEED = 10600
READS = (2, 1000, 199874, 541999)
POWER = ("fp16.c_abs", "fp16.signs", "fp16.x_c", "fp16.x_s", "fp16.z_ss", "fp32.c_abs", "fp32.signs", "fp32.s_abs")   # beside them, once a pass: E78's fp32.ones, fp16.ones (e106_common.COMPARE)
SMOKE = ("anchor_pi", "fp16.x_s", "fp16.z_ss", "fp16.signs", "fp16.zeros", "fp32.signs", "fp32.zeros", "fp32.randn")
REUSED = {"fp16.ones": "tools/claims-v3/kinds/tiles/", "fp32.ones": "tools/claims-v3/kinds/tiles/", "fp16.signs": "tools/claims-v3/kinds/e92/tiles/", "fp32.signs": "tools/claims-v3/kinds/e92/tiles/",
          "fp16.c_abs": "tools/claims-v3/kinds/e92/tiles/", "fp32.c_abs": "tools/claims-v3/kinds/e92/tiles/", "fp32.s_abs": "tools/claims-v3/kinds/e92/tiles/"}


def new_designs():
    w16, t16 = m92.w16, m92.t16
    rng = np.random.default_rng(SEED)
    p = w16(1.0, 1.0)
    seed, b4 = w16(2.0, 2.0), w16(4.0, 4.0)
    aw1 = np.full((16, 16), p, np.uint32)
    bx = np.full((16, 16), w16(1.0, -1.0), np.uint32)
    out = {}
    out["fp16.x_c"] = (*t16(seed, b4, aw1, bx), "A words (1, 1), B words (lo, hi) (1, -1), k-group-0 (2, 2) x (4, 4): each micro-op's products cancel, C = +16 n, no sign moves")
    s = rng.random((16, 16)) < 0.5
    t = rng.random((16, 16)) < 0.5
    ax = np.where(s, w16(-1.0, -1.0), p).astype(np.uint32)
    bxs = np.where(t, w16(-1.0, 1.0), w16(1.0, -1.0)).astype(np.uint32)
    out["fp16.x_s"] = (*t16(seed, b4, ax, bxs), f"x_c with A s (1, 1), B t (1, -1), s and t random at k-group>=1 (default_rng({SEED})): the products cancel inside each micro-op, C = +16 n, nonzero aligned operands, both operands' signs moving")
    aw_s, bw_s = me.words_from_tile(open(os.path.join(HERE, "e92", "tiles", "fp16", "s_abs.bin"), "rb").read())
    pick = rng.integers(0, 3, (16, 16))
    zeros = np.array([w16(-0.0, -0.0), w16(0.0, -0.0), w16(-0.0, 0.0)], np.uint32)
    az = np.array(aw_s)
    az[:, 1:] = zeros[pick][:, 1:]
    assert (az != 0).all()
    out["fp16.z_ss"] = (az, np.array(bw_s), f"E92's fp16.s_abs's B, A at k-group>=1 at random among (-0, -0), (+0, -0), (-0, +0) (default_rng({SEED})), the seed of c_abs: zero products, C = n 2^31, both operands' signs moving, both eff_sub flipping independently")
    return out


def build():
    accum = e.accum_binary()
    spec = {"experiment": "E106", "date": "2026-11-01", "generator": "tools/claims-v3/kinds/make_e106.py", "power": list(POWER), "smoke": list(SMOKE), "readback": {}, "tiles": {}, "reused_from": {}}
    new = new_designs()
    names = [(n, "new") for n in new] + [(n, "reused") for n in REUSED]
    raws, rules = {}, {}
    for name, how in names:
        ty, kind = name.split(".")
        if how == "new":
            aw, bw, rule = new[name]
            raws[name] = me.tile_from_words(aw, bw)
        else:
            raws[name] = open(os.path.join(ROOT, REUSED[name], ty, kind + ".bin"), "rb").read()
            rule = f"{REUSED[name]}{ty}/{kind}.bin, byte for byte"
            spec["reused_from"][name] = REUSED[name] + f"{ty}/{kind}.bin"
        rules[name] = rule
    with ThreadPoolExecutor(int(os.environ.get("E104_JOBS", "6"))) as ex:
        list(ex.map(lambda nh: e.real_c(nh[0].split(".")[0], raws[nh[0]], tuple(READS) + tuple(n - 1 for n in e.DP_NS), accum), names))
        list(ex.map(lambda nh: e.manual_c(nh[0].split(".")[0], raws[nh[0]], READS, accum), names))
    problems = []
    for name, how in names:
        ty, kind = name.split(".")
        raw = raws[name]
        st = mk.tile_stats(raw, ty)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        real = e.real_c(ty, raw, READS, accum)
        man = e.manual_c(ty, raw, READS, accum)
        cnt = e.dp_counts(ty, raw, accum, list(e.DP_NS))
        spec["readback"][name] = list(READS)
        ent = {"type": ty, "kind": kind, "how": how, "rule": rules[name], "file": f"tiles/{ty}/{kind}.bin", "bytes": len(raw), "sha256": e.sha(raw), "sha256_a": e.sha(raw[:1024]), "sha256_b": e.sha(raw[1024:]),
               "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"], "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb}, "counts_real": cnt, "read": {}}
        for n, v in real.items():
            f = e.fl_c(ty, raw, n)
            mv = man[n]
            ent["read"][str(n)] = {"rtl_hex": v.tobytes().hex(), "fl_hex": f.tobytes().hex(), "manual_hex": mv.tobytes().hex(), "words_rtl_vs_fl": int((v != f).sum()), "words_rtl_vs_manual": int((v != mv).sum()), "words_fl_vs_manual": int((f != mv).sum()),
                                   "distinct": {"rtl": len(set(v.tolist())), "fl": len(set(f.tolist())), "manual": len(set(mv.tolist()))},
                                   "c00": {"rtl": f"{int(v[0]):08x}", "fl": f"{int(f[0]):08x}", "manual": f"{int(mv[0]):08x}"}, "c08": {"rtl": f"{int(v[8]):08x}", "fl": f"{int(f[8]):08x}", "manual": f"{int(mv[8]):08x}"}}
            if int((v != f).sum()) or int((v != mv).sum()):
                problems.append(f"{name} n={n}: rtl!=fl {int((v != f).sum())}, rtl!=manual {int((v != mv).sum())}")
        spec["tiles"][name] = ent
        r = ent["read"]["199874"]
        print(f"{name:12s} {how:6s} bus {st['bus_bits_per_op']:6d} signflips A {fa:5d} B {fb:5d} alt {cnt['alt1']:6.0f} {cnt['alt2']:6.0f} sub {cnt['sub1']:.3f} {cnt['sub2']:.3f} res {cnt['cbus'] + cnt['rbus'] + cnt['store']:8.0f} chg {cnt['chg']:.3f} words {r['distinct']['rtl']} rtl!=fl {r['words_rtl_vs_fl']} C00 {r['c00']['rtl']}", flush=True)
    return spec, raws, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    spec, raws, problems = build()
    if a.check:
        bad = [n for n, r in raws.items() if open(os.path.join(OUT, spec["tiles"][n]["file"]), "rb").read() != r]
        print(json.dumps({"tiles": len(raws), "problems": bad, "readings_differ": problems}))
        sys.exit(1 if bad else 0)
    for name, raw in raws.items():
        p = os.path.join(OUT, spec["tiles"][name]["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(raw)
    json.dump(spec, open(os.path.join(OUT, "e106.json"), "w"), indent=1)
    print(json.dumps({"tiles": len(raws), "readings_differ": problems}))


if __name__ == "__main__":
    main()
