#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E92, POST HOC and labelled so: written after the registration and run after the data; no rule depends on it. Does one
more price, per bit change on the adder's inputs and flops, make a model for every fp32 and fp16 tile measured on this card?

    /usr/bin/python3 tools/claims-v3/kinds/posthoc_fit_e92.py <e92 reduction json> <out json> [--txt <out txt>]

On aifoundry3 card 0 at 600 MHz: E78's committed reduction (its 18 fp32 and 17 fp16 kinds, the zeros included), E90's (its
sign and redraw tiles) and E92's (its 32 tiles). Where a tile ran in more than one session, the latest session's D. Per
type, least squares over the tiles, with every count from one exact-stream model (make_e88.simulate: live fraction, operand
bus, products, C read + result bus + register write) and make_e92's flop-level reading of the adder (dp_fp32, dp_fp16, with
the zero gate honoured here: a gated lane-micro-op moves nothing):
    D = F live + a N_op + c N_prod + b N_res                (E88's four prices, refitted on this card)
    D = F live + a N_op + c N_prod + b N_res + f N_flops    (one more price)
    D = F live + a N_op + c N_prod + b N_res + g N_alt      (the same, with the alternation count instead)
It reports each model's rms over the tiles and its leave-one-out rms (each tile predicted by a fit without it). A
leave-one-out rms is an in-family test, not a test on a new card or a new kind of data. E86's six float tiles of real GPT-2
weights (the same card and clock, never in the fit) are predicted as a held-out set.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools", "claims-v3", "rpath")]
import make_e88 as me    # noqa: E402
import make_e92 as m92   # noqa: E402

E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E90_JSON = "docs/reports/data/2026-10-31-e90-signs-spread/e90.json"
E86_JSON = "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json"
LAUNCH = m92.LAUNCH_OPS
SAMPLES = 4


def gated_counts(ty, aw, bw):
    """make_e92.sign_counts with the zero gate honoured: (N_alt, flops) per op, a zero word's lane-micro-op moves nothing."""
    A, B = me.elements(ty, aw, bw)
    S = me.per_op_sum(ty, A, B)
    seq = me.stream(ty)
    dp = m92.dp_fp32 if ty == "fp32" else m92.dp_fp16
    alt = bits = 0.0
    other = 0
    for s in range(SAMPLES):
        n = max(2, int((s + 0.5) / SAMPLES * LAUNCH))
        C = me.fl(ty, (n - 1) * S)
        prev = [None] * 8
        for op in (0, 1):
            for (k, i, cols) in seq:
                live = me.gate_live(ty, aw, bw, k, i, cols)
                for lane, j in enumerate(cols):
                    if not live[lane]:
                        continue
                    cw = m92.f32_words(C[i, j])
                    e1, e2, csa3, csa2, cs, cc, ca, oth = dp(cw, aw[i, k], bw[k, j])
                    p = float(A[i, k]) * float(B[k, j]) if ty == "fp32" else float((A[i, k] * B[k, j]).sum())
                    C[i, j] = np.float32(float(C[i, j]) + p)
                    if op == 1 and prev[lane] is not None:
                        q = prev[lane]
                        alt += (e1 != q[0]) + (e2 != q[1])
                        bits += sum(bin(x ^ y).count("1") for x, y in zip((csa3, csa2, cs, cc, ca), q[2:]))
                        other += oth
                    prev[lane] = (e1, e2, csa3, csa2, cs, cc, ca)
    return alt / SAMPLES, bits / SAMPLES, other / SAMPLES / 4096.0


def counts_of(ty, raw):
    aw, bw = me.words_from_tile(raw)
    sim = me.simulate(ty, aw, bw, launch_ops=LAUNCH)
    bus, _, _ = me.bus_bits(ty, aw, bw)
    alt, flops, other = gated_counts(ty, aw, bw)
    return {"live": sim["live_frac"], "bus": bus, "prod": sim["prod"], "res": sim["res_bits_per_op"], "alt": alt, "flops": flops, "other_frac": other}


def fit(rows, feats):
    X = np.array([[r[f] for f in feats] for r in rows], float)
    y = np.array([r["D"] for r in rows], float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    loo = []
    for i in range(len(y)):
        keep = np.arange(len(y)) != i
        c, *_ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
        loo.append(y[i] - X[i] @ c)
    return coef, res, np.array(loo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("e92")
    ap.add_argument("out")
    ap.add_argument("--txt")
    ap.add_argument("--cache", help="a json file of counts by tile sha256, read and extended (desk speed only)")
    a = ap.parse_args()
    cache = json.load(open(a.cache)) if a.cache and os.path.exists(a.cache) else {}
    e92r = json.load(open(a.e92))
    e78 = json.load(open(os.path.join(ROOT, E78_JSON)))
    e90 = json.load(open(os.path.join(ROOT, E90_JSON)))
    k = json.load(open(os.path.join(HERE, "kinds.json")))
    e90s = json.load(open(os.path.join(HERE, "e90", "e90.json")))
    e92s = json.load(open(os.path.join(HERE, "e92", "e92.json")))
    tiles = {}
    for ty in ("fp32", "fp16"):
        for kind, v in k["kinds"][ty].items():
            name = f"{ty}.{kind}"
            if name in e78["items"] and e78["items"][name]["D"]["mean"] is not None:
                tiles[name] = {"type": ty, "path": os.path.join(HERE, v["file"]), "D": e78["items"][name]["D"]["mean"], "session": "E78"}
    for name, v in e90s["tiles"].items():
        if v["type"] in ("fp32", "fp16") and name in e90["items"] and e90["items"][name]["D"]["mean"] is not None:
            tiles[name] = {"type": v["type"], "path": os.path.join(HERE, "e90", v["file"]), "D": e90["items"][name]["D"]["mean"], "session": "E90"}
    for name in list(tiles):
        if name in e90["items"] and e90["items"][name].get("D") and e90["items"][name]["D"]["mean"] is not None:
            tiles[name]["D"], tiles[name]["session"] = e90["items"][name]["D"]["mean"], "E90"
    for name, v in e92s["tiles"].items():
        tiles[name] = {"type": v["type"], "path": os.path.join(HERE, "e92", v["file"]), "D": e92r["items"][name]["D"]["mean"], "session": "E92"}
    for name in list(tiles):
        if name in e92r["items"] and e92r["items"][name].get("D") and e92r["items"][name]["D"]["mean"] is not None:
            tiles[name]["D"], tiles[name]["session"] = e92r["items"][name]["D"]["mean"], "E92"
    rows = {"fp32": [], "fp16": []}
    for name, t in tiles.items():
        raw = open(t["path"], "rb").read()
        key = f"{t['type']}:" + hashlib.sha256(raw).hexdigest()
        if key not in cache:
            cache[key] = counts_of(t["type"], raw)
            if a.cache:
                json.dump(cache, open(a.cache, "w"))
        c = dict(cache[key])
        c.update({"name": name, "D": t["D"], "session": t["session"]})
        rows[t["type"]].append(c)
        print(f"{name:26s} {t['session']} D {t['D']:7.3f} live {c['live']:.3f} bus {c['bus']:7.0f} prod {c['prod']:8.0f} res {c['res']:8.0f} alt {c['alt']:6.0f} flops {c['flops']:8.0f} other {c['other_frac']:.3f}", flush=True)
    # E86's real tiles: the held-out set
    e86 = json.load(open(os.path.join(ROOT, E86_JSON)))
    held = {"fp32": [], "fp16": []}
    for name, it in e86["items"].items():
        if "." not in name:
            continue
        ty, kind = name.split(".", 1)
        if ty not in held or not kind.startswith("real_"):
            continue
        raw = open(os.path.join(HERE, "real", "tiles", ty, kind[len("real_"):] + ".bin"), "rb").read()
        key = f"{ty}:" + hashlib.sha256(raw).hexdigest()
        if key not in cache:
            cache[key] = counts_of(ty, raw)
            if a.cache:
                json.dump(cache, open(a.cache, "w"))
        c = dict(cache[key])
        c.update({"name": name, "D": it["D"]["mean"], "D_ci95": it["D"]["ci95"], "session": "E86"})
        held[ty].append(c)
    out = {"experiment": "E92 post hoc", "label": "post hoc, exploratory; no rule depends on it; every tile measured on aifoundry3 card 0 at 600 MHz",
           "ops_per_s": 600e6 / 546.0 * 1024, "models": {}, "tiles": rows}
    lines = []
    for ty, rr in rows.items():
        for label, feats in (("four prices", ("live", "bus", "prod", "res")),
                             ("four prices + flops", ("live", "bus", "prod", "res", "flops")),
                             ("four prices + alternations", ("live", "bus", "prod", "res", "alt"))):
            coef, res, loo = fit(rr, feats)
            scale = 1e15 / out["ops_per_s"]
            names = [r["name"] for r in rr]
            worst = np.argsort(-np.abs(loo))[:5]
            m = {"features": list(feats), "F_w": float(coef[0]), "prices_fj": {f: float(c) * scale for f, c in zip(feats[1:], coef[1:])},
                 "rms_w": float(np.sqrt(np.mean(res ** 2))), "loo_rms_w": float(np.sqrt(np.mean(loo ** 2))), "n": len(rr),
                 "worst_loo": {names[i]: round(float(loo[i]), 3) for i in worst}, "residuals": {n: round(float(x), 3) for n, x in zip(names, res)}}
            hx = np.array([[r[f] for f in feats] for r in held[ty]], float)
            hy = np.array([r["D"] for r in held[ty]], float)
            herr = hy - hx @ coef
            m["held_out_e86"] = {r["name"]: {"measured_w": round(r["D"], 3), "predicted_w": round(float(p), 3), "error_w": round(float(e), 3)}
                                 for r, p, e in zip(held[ty], hx @ coef, herr)}
            m["held_out_rms_w"] = float(np.sqrt(np.mean(herr ** 2)))
            out["models"][f"{ty}: {label}"] = m
            lines.append(f"{ty:5s} {label:28s} n {len(rr):3d} rms {m['rms_w']:.3f} W, leave-one-out {m['loo_rms_w']:.3f} W; F {m['F_w']:.2f} W; prices (fJ) " +
                         ", ".join(f"{f} {c:.1f}" for f, c in m["prices_fj"].items()) + "; worst " + ", ".join(f"{n} {x:+.2f}" for n, x in m["worst_loo"].items()) +
                         f"; held-out E86 rms {m['held_out_rms_w']:.3f} W (" + ", ".join(f"{n.split('.', 1)[1]} {v['error_w']:+.2f}" for n, v in m["held_out_e86"].items()) + ")")
    json.dump(out, open(a.out, "w"), indent=1)
    text = "E92 post hoc (exploratory; no rule depends on it)\n" + "\n".join(lines) + "\n"
    print(text)
    if a.txt:
        open(a.txt, "w").write(text)


if __name__ == "__main__":
    main()
