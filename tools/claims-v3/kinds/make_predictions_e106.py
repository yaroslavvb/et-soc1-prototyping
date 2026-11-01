#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E106 (Q132): freeze the registration: predictions-e106.json, from e106/e106.json, the bench's counts and the files' hashes. Desk compute only.

    python3 tools/claims-v3/kinds/make_predictions_e106.py

M4 is not refitted: its coefficients, its card-1 scale and the interval's parts are recomputed here exactly as make_predictions_e104.py did and checked against e103/selection.json. The thresholds are here and in E106.md.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
D = "docs/reports/data"
sys.path.insert(0, os.path.join(ROOT, D, "2026-11-01-q132-rtl-bench"))
from predict_m4 import fit, t975, x_float  # noqa: E402

DESK = f"{D}/2026-11-01-e106-held-signs/desk"
# E92's dips-removed arm on aifoundry3 and the card-1 float scale E103 froze: the carried values E104 had to use, which E106 replaces with one card's
E92_STEP = {"fp32": 5.016, "fp16": 4.965}
READ_LENGTHS = (2, 1000, 199874, 541999)


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def x_of(m, z, rate):
    return np.array(x_float(m, z), float) * rate


def main():
    spec = load(f"{K}/e106/e106.json")
    # the read-back rule assumes the three readings coincide on every tile at every length: checked at the desk
    bad = [(t, n) for t, v in spec["tiles"].items() for n, r in v["read"].items() if r["words_rtl_vs_fl"] or r["words_rtl_vs_manual"]]
    assert not bad, bad
    e94 = load(f"{K}/predictions-e94.json")
    reused = e94["harness"]["reused_unchanged_sha256"]
    miss = [r for r, w in reused.items() if sha(r) != w]
    assert not miss, miss
    sel = load(f"{K}/e103/selection.json")
    zc = load(f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json")["rows"]
    e78 = load(f"{D}/2026-10-31-e78-kinds-energy-matrix/e78.json")["items"]
    e82 = load(f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")["items"]
    rate = {t: e78[f"{t}.randn"]["rate"]["mean"] for t in ("fp32", "fp16")}

    def rows(items):
        X, y = [], []
        for k, v in zc.items():
            t, name = v["type"], v["kind"]
            if t == "int8" or name == "zeros":
                continue
            it = items.get(k)
            if not it or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                continue
            r = it["rate"]["mean"] if isinstance(it.get("rate"), dict) else 600e6 / 546 * 1024 * 0.9963
            X.append(x_of(v["mean"], zc[t + ".zeros"]["mean"], r))
            y.append(it["D"]["mean"])
        return np.array(X, float), np.array(y, float)

    X, y = rows(e78)
    b = fit(X, y)
    jk = np.array([fit(np.delete(X, i, 0), np.delete(y, i)) for i in range(len(y))])
    d = jk - jk.mean(axis=0)
    C = d.T @ d * (len(y) - 1) / len(y)
    X82, y82 = rows(e82)
    p82 = X82 @ b
    s = float((p82 @ y82) / (p82 @ p82))
    js = [float((np.delete(p82, i) @ np.delete(y82, i)) / (np.delete(p82, i) @ np.delete(p82, i))) for i in range(len(y82))]
    se_s = math.sqrt(sum((v - sum(js) / len(js)) ** 2 for v in js) * (len(js) - 1) / len(js))
    fm = sel["models"]["float"]
    for nm, v in zip(["k_core", "k_bus", "k_rest", "a_clocked"], b):
        assert abs(v * 1e15 - fm["coef_fJ"][nm]) < 1e-6, nm
    assert abs(s - fm["card1_scale"]) < 1e-9 and abs(se_s - fm["card1_scale_se"]) < 1e-9
    pool, npool = fm["interval_pool"]["rms_w"], fm["interval_pool"]["n"]
    t_ = t975(npool - 2)

    counts = {}
    counts.update(zc)
    counts.update(load(f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json")["rows"])
    counts.update(load(f"{DESK}/counts-e106.json")["rows"])
    x_tile, m_tile, tiles = {}, {}, {}
    groups = {"ones": "the +1 side of the step", "signs": "the +-1 side of the step", "c_abs": "held baseline", "x_c": "held baseline", "s_abs": "held, both operands' signs moving", "z_ss": "held, both operands' signs moving", "x_s": "held, both operands' signs moving"}
    names = list(spec["power"]) + ["fp32.ones", "fp16.ones"]
    for name in names:
        t = name.split(".")[0]
        v = counts[name]
        z = zc[t + ".zeros"]["mean"]
        x = x_of(v["mean"], z, rate[t])
        p0 = float(x @ b)
        pts = [float(x_of(q, z, rate[t]) @ b) * s for q in v["points"]]
        m = float(np.std(pts, ddof=1) / math.sqrt(len(pts)))
        half = t_ * math.sqrt(pool ** 2 + s * s * float(x @ C @ x) + (p0 * se_s) ** 2 + m * m)
        x_tile[name], m_tile[name] = x, m
        kind = name.split(".")[1]
        tiles[name] = {"type": t, "kind": kind, "group": groups[kind], "pred": {"M": p0 * s, "lo95": max(p0 * s - half, 0.0), "hi95": p0 * s + half, "half95": half, "launch_points_w": pts, "terms_w": [float(c) * s for c in x * b]},
                       "check_mismatch_words": v["mean"]["check_mismatch"], "valid_slots": v["mean"]["valid_slots"], "cycles": v["mean"]["cycles"]}

    def cdef(plus, minus, what):
        xx = sum(x_tile[n] for n in plus) - sum(x_tile[n] for n in minus)
        p0 = float(xx @ b)
        var = (len(plus) + len(minus)) * pool ** 2 + s * s * float(xx @ C @ xx) + (p0 * se_s) ** 2 + sum(m_tile[n] ** 2 for n in list(plus) + list(minus))
        return {"plus": list(plus), "minus": list(minus), "what": what, "M": p0 * s, "half95": t_ * math.sqrt(var)}

    contrasts = {
        "fp32.step": cdef(["fp32.signs"], ["fp32.ones"], "the sign step on this card"),
        "fp16.step": cdef(["fp16.signs"], ["fp16.ones"], "the sign step on this card"),
        "fp32.held": cdef(["fp32.s_abs"], ["fp32.c_abs"], "random signs on both operands, absorbed: the sum holds"),
        "fp16.held_z": cdef(["fp16.z_ss"], ["fp16.c_abs"], "random signs on both operands, zero products: the sum holds, both eff_sub flip independently"),
        "fp16.held_x": cdef(["fp16.x_s"], ["fp16.x_c"], "random signs on both operands, products cancelling: the sum holds, nonzero aligned operands, eff_sub1 and eff_sub2 in opposite phase"),
        "fp32.rest": cdef(["fp32.signs", "fp32.c_abs"], ["fp32.ones", "fp32.s_abs"], "the step less the held part"),
        "fp16.rest_z": cdef(["fp16.signs", "fp16.c_abs"], ["fp16.ones", "fp16.z_ss"], "the step less the held part"),
    }
    Ms = {k: contrasts[k]["M"] for k in contrasts}
    shares = {"fp32.s_abs": {"held": "fp32.held", "step": "fp32.step", "M": Ms["fp32.held"] / Ms["fp32.step"], "what": "fp32's held share of the step, on one card"},
              "fp16.z_ss": {"held": "fp16.held_z", "step": "fp16.step", "M": Ms["fp16.held_z"] / Ms["fp16.step"], "what": "fp16's held share, zero products, independent eff_subs"},
              "fp16.x_s": {"held": "fp16.held_x", "step": "fp16.step", "M": Ms["fp16.held_x"] / Ms["fp16.step"], "what": "fp16's held share, cancelling products, eff_subs in opposite phase"}}
    files = [f"{K}/{f}" for f in ("e106_common.py", "run_e106.py", "block_e106.sh", "queue_e106.sh", "run_e106.sh", "reduce_e106.py", "score_e106.py", "collect_e106.sh", "readback_e106.py", "block_readback_e106.sh")]
    nod = e82
    reg = {
        "experiment": "E106",
        "title": "a random sign's ~5 W split on one card: signs and ones beside held tiles with both operands' signs moving, read back, aifoundry1 card 1 at 600 MHz",
        "request": "Q132: item 2's last line, E104's verifier's suggestion",
        "date": "2026-11-01",
        "registration": f"{K}/E106.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {
            "counts_e78": {"path": f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json", "sha256": sha(f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json")},
            "counts_e92": {"path": f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json", "sha256": sha(f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json")},
            "counts_e106": {"path": f"{DESK}/counts-e106.json", "sha256": sha(f"{DESK}/counts-e106.json")},
            "desk_check": {"path": f"{DESK}/desk-e106.txt", "sha256": sha(f"{DESK}/desk-e106.txt")},
            "selection_e103": {"path": f"{K}/e103/selection.json", "sha256": sha(f"{K}/e103/selection.json")},
        },
        "harness": {"reused_unchanged_sha256": reused, "e106_json_sha256": sha(f"{K}/e106/e106.json"), "e106_files_sha256": {f: sha(f) for f in files}},
        "plan": {"passes": [10610, 10611, 10612, 10613], "smoke": 10601, "readback": 10602, "runs_per_pass": 2 + 18 + len(names), "items_per_pass": f"the tie twice, E78's six anchors three times, E106's {len(spec['power'])} tiles and E78's two ones once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's)", "min_kept_passes_scored": 2, "min_tile_passes": 2},
        "card_budget": {"card_minutes_about": 20, "queue_budget_s": 1250, "first_pass_estimate_s": 310, "queue_deadline": "2026-11-01 10:30 PST"},
        "model": {"name": "M4", "coef_fJ": fm["coef_fJ"], "card1_scale": s, "card1_scale_se": se_s, "interval_pool": fm["interval_pool"]},
        "e92_step_on_aifoundry3_w": E92_STEP,
        "tiles": tiles,
        "contrasts": contrasts,
        "shares": shares,
        "session_tie": {"reference": f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json items.<cell>.D.mean (dips removed, as E106's primary)",
                        "cells": {c: {"ref_w": round(nod[c]["D"]["mean"], 4), "band_w": w} for c, w in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}},
        "rules": {
            "E106-R1": {"kind": "read", "what": "every tile, at every length, every word of all 1,024 minions: the three readings coincide on these tiles, so a miss means the tile is not what it is called, or a sum does not hold", "reads": {t: list(READ_LENGTHS) for t in spec["tiles"]}},
            "E106-R2": {"kind": "power", "what": "the step on one card: signs - ones in each format against E92's aifoundry3 value carried by the card scale", "carried_w": {t: E92_STEP[t] * s for t in E92_STEP}, "band_w": 1.0},
            "E106-R3": {"kind": "power", "what": "fp32's held share on one card: (s_abs - c_abs) / (signs - ones), per pass", "lo": 0.35, "hi": 0.65},
            "E106-R4": {"kind": "power", "what": "fp16's held share with both operands' signs moving: (z_ss - c_abs) / (signs - ones), per pass", "lo": 0.30, "hi": 0.70},
            "E106-R5": {"kind": "power", "what": "the same with nonzero aligned operands: (x_s - x_c) / (signs - ones), per pass", "lo": 0.30, "hi": 0.70},
            "E106-R6": {"kind": "power", "what": "the two formats' shares: fp16's z_ss share less fp32's s_abs share, per pass", "band": 0.15},
            "E106-R7": {"kind": "power", "what": "the bench's model on E106's tiles: rms(D - M4)", "pass_w": 0.60, "fail_w": 1.00},
            "E106-S1": {"kind": "power", "what": "the session tie against E82, dips removed: every cell inside its band"},
        },
        "not_scored_if": "fewer than 2 kept passes in the primary reduction: every power rule NOT SCORED. The read-back rule needs no pass.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e106.json"), "w"), indent=1)
    print("tiles", len(tiles), "runs per pass", reg["plan"]["runs_per_pass"])
    print(f"{'tile':14s} {'M4':>6s} [{'lo':>5s},{'hi':>6s}]  core   bus  rest clock  valid chk")
    for n, r in tiles.items():
        q = r["pred"]
        print(f"{n:14s} {q['M']:6.2f} [{q['lo95']:5.2f},{q['hi95']:6.2f}]  {' '.join(f'{v:5.2f}' for v in q['terms_w'])} {r['valid_slots']:6.0f} {r['check_mismatch_words']:3.0f}")
    for n, c in contrasts.items():
        print(f"{n:16s} M4 {c['M']:6.2f} ± {c['half95']:4.2f}")
    for n, c in shares.items():
        print(f"share {n:12s} M4 {c['M']:.3f}")
    print("carried", reg["rules"]["E106-R2"]["carried_w"])


if __name__ == "__main__":
    main()
