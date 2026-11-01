#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E108 (Q133): freeze the registration: predictions-e108.json, from e108/e108.json, the bench's counts and the files' hashes. Desk compute only. A port of
tools/claims-v3/kinds/make_predictions_e106.py with E108's tiles, quantities and rules.

    python3 tools/claims-v3/signloc/make_predictions_e108.py

M4 is not refitted: its coefficients, its card-1 scale and the interval's parts are recomputed here exactly as make_predictions_e104.py and _e106.py did and
checked against tools/claims-v3/kinds/e103/selection.json. The thresholds are here and in E108.md.
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
SL = "tools/claims-v3/signloc"
D = "docs/reports/data"
sys.path.insert(0, os.path.join(ROOT, D, "2026-11-01-q132-rtl-bench"))
from predict_m4 import fit, t975, x_float  # noqa: E402

DESK = f"{D}/2026-11-01-e108-sign-located/desk"
# the bench's counts, committed by the lanes that ran each tile on the same bench (rtl-sim/fma_toggle_v2); E108's new tiles in DESK
COUNTS = [f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json", f"{D}/2026-11-01-q132-rtl-bench/counts-e88.json", f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json",
          f"{D}/2026-11-01-e104-c-readback/desk/counts-e104.json", f"{D}/2026-11-01-e104-c-readback/desk/counts-e104b.json",
          f"{D}/2026-11-01-e106-held-signs/desk/counts-e106.json", f"{DESK}/counts-e108.json", f"{DESK}/counts-e108b.json"]
# E106's steps on this card (scored.json contrasts fp32.step, fp16.step): R2's references
E106_STEP = {"fp32": 4.792, "fp16": 4.716}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def x_of(m, z, rate):
    return np.array(x_float(m, z), float) * rate


def C(plus, minus, what):
    return {"form": "contrast", "plus": list(plus), "minus": list(minus), "what": what}


def Rt(a, b, what):
    return {"form": "ratio", "a": a, "b": b, "what": what}


def Df(a, b, what, k=1.0):
    return {"form": "diff", "a": a, "b": b, "k": k, "what": what}


def quantities(spec):
    f = "fp32."
    h = "fp16."
    alt = {n: spec["tiles"][n]["counts_real"]["alt1"] for n in spec["tiles"]}
    rho = alt[f + "b_A_f"] / alt[f + "b_B_f"]
    q = {
        # the like for like (item 5's one-session test) and E106's held tiles, one session
        "fp32.step": C([f + "signs"], [f + "ones"], "the sign step, fp32"),
        "fp16.step": C([h + "signs"], [h + "ones"], "the sign step, fp16"),
        "fp32.held_z": C([f + "z_s"], [f + "c_abs"], "random B signs on zero products, the sum held (E104's z_s), fp32"),
        "fp16.held_z": C([h + "z_s"], [h + "c_abs"], "random B signs on zero products, the sum held (E104's z_s), fp16"),
        "fp32.held_abs": C([f + "s_abs"], [f + "c_abs"], "random signs on both sides, absorbed, the sum held (E88's s_abs), fp32"),
        "fp16.held_zss": C([h + "z_ss"], [h + "c_abs"], "random signs on both sides, zero products, the sum held (E106's z_ss), fp16"),
        "fp32.rest_vs_z": C([f + "signs", f + "c_abs"], [f + "ones", f + "z_s"], "the step less the zero-product held part, fp32"),
        "fp16.rest_vs_z": C([h + "signs", h + "c_abs"], [h + "ones", h + "z_s"], "the step less the zero-product held part, fp16"),
        "fp32.rest_vs_abs": C([f + "signs", f + "c_abs"], [f + "ones", f + "s_abs"], "the step less the absorbed held part (E106's rest), fp32"),
        # axis b: A against B sign, held and walking; s_abs and s_walk are both
        "fp32.A_held": C([f + "b_A_f"], [f + "c_abs"], "A's random signs, B +1, absorbed"),
        "fp32.B_held": C([f + "b_B_f"], [f + "c_abs"], "B's random signs, A +1, absorbed"),
        "fp32.A_step": C([f + "b_A_w"], [f + "ones"], "A's random signs, B +1, walking, over all +1"),
        "fp32.B_step": C([f + "b_B_w"], [f + "ones"], "B's random signs, A +1, walking, over all +1"),
        "fp32.AB_step": C([f + "s_walk"], [f + "ones"], "both sides' random signs (s_walk), walking, over all +1"),
        "fp32.A_rest": C([f + "b_A_w"], [f + "b_A_f"], "A's signs: walking less held"),
        "fp32.B_rest": C([f + "b_B_w"], [f + "b_B_f"], "B's signs: walking less held"),
        "fp32.rest": C([f + "s_walk"], [f + "s_abs"], "both: walking less held, the draws matched (E88's R32s)"),
        "fp32.A_on_B_held": C([f + "s_abs"], [f + "b_B_f"], "A's signs added to B's, held"),
        "fp32.A_on_B_walk": C([f + "s_walk"], [f + "b_B_w"], "A's signs added to B's, walking"),
        "fp32.abs_vs_zero": C([f + "b_B_f"], [f + "z_s"], "the same B stream and k = 0 slice: absorbed +-1 products against zero products"),
        "fp32.Bz_het": C([f + "b_B_z"], [f + "z_s"], "zero products, B's signs: held at b_B_w's sums over held at z_s's equal ones"),
        "fp32.Bz_walk": C([f + "b_B_w"], [f + "b_B_z"], "B's signs walking over held at the same sums at every op's end"),
        "fp32.Bz_rest": C([f + "b_B_w"], [f + "z_s"], "B's signs walking over held on zero products: the rest for B's signs, zero-product baseline"),
        # axis c: the accumulators exponent-aligned against misaligned, held (absorbed); s_walk is the walking end
        "fp32.het_sg": C([f + "c_sg_f"], [f + "s_abs"], "held accumulators that differ in sign, over s_abs's equal ones"),
        "fp32.het_ex": C([f + "c_ex_f"], [f + "s_abs"], "held accumulators that differ in sign and exponent"),
        "fp32.het_mx": C([f + "c_mx_f"], [f + "s_abs"], "held accumulators that differ as s_walk's do"),
        "fp32.ex_over_sg": C([f + "c_ex_f"], [f + "c_sg_f"], "the exponents misaligned, over sign only"),
        "fp32.mx_over_ex": C([f + "c_mx_f"], [f + "c_ex_f"], "the mantissas too, over sign and exponent"),
        "fp32.walk_given_het": C([f + "s_walk"], [f + "c_mx_f"], "the sums walking, over held accumulators that differ as s_walk's do"),
        # axis a: product-sign alternation against operand sign changes at a fixed product sign, held and walking
        "fp32.alt_held": C([f + "h_sub"], [f + "h_add"], "alternating against a fixed product sign, held (E92's pair)"),
        "fp32.alt_walk": C([f + "m_h_sub"], [f + "w_h_add"], "alternating against a fixed product sign, walking, the same magnitudes (E104's pair)"),
        "fp16.alt_walk": C([h + "m_h_sub"], [h + "w_h_add"], "alternating against a fixed product sign, walking (E104's pair)"),
        "fp32.walk_fixed": C([f + "w_h_add"], [f + "h_add"], "the sums walking at a fixed product sign, over held"),
    }
    q.update({
        "fp32.share_z": Rt("fp32.held_z", "fp32.step", "fp32's held share, zero products, one session"),
        "fp16.share_z": Rt("fp16.held_z", "fp16.step", "fp16's held share, zero products, one session"),
        "fp32.share_abs": Rt("fp32.held_abs", "fp32.step", "fp32's held share, absorbed products (E106's design)"),
        "fp16.share_zss": Rt("fp16.held_zss", "fp16.step", "fp16's held share, zero products with A's signs (E106's design)"),
        "fp32.share_het": Rt("fp32.het_mx", "fp32.rest", "how much of the rest held accumulators that differ as s_walk's do carry"),
        "fp32.share_het_z": Rt("fp32.Bz_het", "fp32.Bz_rest", "zero products: how much of B's rest held accumulators at b_B_w's own sums carry"),
        "fp32.alt_ratio": Rt("fp32.alt_walk", "fp32.alt_held", "the alternation's price walking over held, fp32"),
        "alt_walk_ratio": Rt("fp16.alt_walk", "fp32.alt_walk", "E104-R6: fp16 over fp32, walking"),
        "fp32.A_over_B_held": Rt("fp32.A_held", "fp32.B_held", "A's held cost over B's"),
        "formats_z": Df("fp16.share_z", "fp32.share_z", "the like for like: fp16's zero-product share less fp32's"),
        "design_fp32": Df("fp32.share_abs", "fp32.share_z", "fp32's held share, absorbed less zero products, one session"),
        "design_fp16": Df("fp16.share_zss", "fp16.share_z", "fp16's held share, A's sign bits moving on the zeros less still"),
        "A_vs_B_priced": Df("fp32.A_held", "fp32.B_held", f"A's held cost less B's scaled by their alternations ({rho:.4f})", k=rho),
    })
    return q, rho


def main():
    spec = load(f"{SL}/e108/e108.json")
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
    Cv = d.T @ d * (len(y) - 1) / len(y)
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

    counts, src = {}, {}
    for rel in COUNTS:
        for k, v in load(rel)["rows"].items():
            counts[k] = v
            src[k] = rel
    names = sorted(spec["tiles"])
    x_tile, m_tile, tiles = {}, {}, {}
    for name in names:
        t = name.split(".")[0]
        v = counts[name]
        z = zc[t + ".zeros"]["mean"]
        x = x_of(v["mean"], z, rate[t])
        p0 = float(x @ b)
        pts = [float(x_of(q, z, rate[t]) @ b) * s for q in v["points"]]
        m = float(np.std(pts, ddof=1) / math.sqrt(len(pts)))
        half = t_ * math.sqrt(pool ** 2 + s * s * float(x @ Cv @ x) + (p0 * se_s) ** 2 + m * m)
        x_tile[name], m_tile[name] = x, m
        tiles[name] = {"type": t, "kind": name.split(".")[1], "group": spec["tiles"][name]["group"], "counts_from": src[name],
                       "pred": {"M": p0 * s, "lo95": max(p0 * s - half, 0.0), "hi95": p0 * s + half, "half95": half, "launch_points_w": pts, "terms_w": [float(c) * s for c in x * b]},
                       "check_mismatch_words": v["mean"]["check_mismatch"], "valid_slots": v["mean"]["valid_slots"], "cycles": v["mean"]["cycles"]}

    Q, rho = quantities(spec)
    M = {}

    def m_of(name):
        if name in M:
            return M[name]
        q = Q[name]
        if q["form"] == "contrast":
            xx = sum(x_tile[n] for n in q["plus"]) - sum(x_tile[n] for n in q["minus"])
            p0 = float(xx @ b)
            var = (len(q["plus"]) + len(q["minus"])) * pool ** 2 + s * s * float(xx @ Cv @ xx) + (p0 * se_s) ** 2 + sum(m_tile[n] ** 2 for n in list(q["plus"]) + list(q["minus"]))
            q["M"], q["half95"] = p0 * s, t_ * math.sqrt(var)
        elif q["form"] == "ratio":
            q["M"], q["half95"] = m_of(q["a"]) / m_of(q["b"]), None
        else:
            q["M"], q["half95"] = m_of(q["a"]) - q["k"] * m_of(q["b"]), None
        M[name] = q["M"]
        return q["M"]

    for n in Q:
        m_of(n)
    files = [f"{SL}/{f}" for f in ("e108_common.py", "run_e108.py", "block_e108.sh", "queue_e108.sh", "run_e108.sh", "reduce_e108.py", "score_e108.py", "collect_e108.sh", "readback_e108.py", "block_readback_e108.sh")]
    nod = e82
    reg = {
        "experiment": "E108",
        "title": "a random sign's ~5 W located further: the like for like on zero products, and the rest by axis (alternation, A against B, the accumulators' exponents), aifoundry1 card 1 at 600 MHz",
        "request": "Q133: the kinds page's section 11 item 5, as of 1fe8377a18af",
        "date": "2026-11-01",
        "registration": f"{SL}/E108.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {**{f"counts_{i}": {"path": rel, "sha256": sha(rel)} for i, rel in enumerate(COUNTS)},
                          "selection_e103": {"path": f"{K}/e103/selection.json", "sha256": sha(f"{K}/e103/selection.json")}},
        "harness": {"reused_unchanged_sha256": reused, "e108_json_sha256": sha(f"{SL}/e108/e108.json"), "e108_files_sha256": {f: sha(f) for f in files}},
        "plan": {"passes": [10810, 10811, 10812, 10813], "smoke": 10801, "readback": 10802, "runs_per_pass": 2 + 18 + len(spec["power"]) + len(spec["compare"]),
                 "items_per_pass": f"the tie twice, E78's six anchors three times, E108's {len(spec['power'])} tiles and E78's two ones once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's)", "min_kept_passes_scored": 2, "min_tile_passes": 2},
        "card_budget": {"card_minutes_at_most": 40, "queue_budget_s": 1900, "first_pass_estimate_s": 450, "queue_deadline": "2026-11-01 18:45 PST"},
        "model": {"name": "M4", "coef_fJ": fm["coef_fJ"], "card1_scale": s, "card1_scale_se": se_s, "interval_pool": fm["interval_pool"]},
        "alternations_rho_A_over_B_held": rho,
        "tiles": tiles,
        "quantities": Q,
        "session_tie": {"reference": f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json items.<cell>.D.mean (dips removed, as E108's primary)",
                        "cells": {c: {"ref_w": round(nod[c]["D"]["mean"], 4), "band_w": w} for c, w in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}},
        "rules": {
            "E108-R1": {"kind": "read", "what": "every tile, at every length, every word of all 1,024 minions: the three readings coincide on these tiles, so a miss means the tile is not what it is called", "reads": {t: spec["readback"][t] for t in spec["tiles"]}},
            "E108-R2": {"kind": "power", "form": "step_band", "what": "the step on this card, another session: signs - ones in each format against E106's", "e106_w": E106_STEP, "band_w": 1.0},
            "E108-R3": {"kind": "power", "form": "sign_then_band", "legs": ["formats_z"], "band": 0.10, "names": {"above": "FP16 HIGHER", "below": "FP16 LOWER", "inside": "ALIKE"},
                        "what": "the like for like item 5 names: fp16's zero-product share less fp32's, one session"},
            "E108-R4": {"kind": "power", "form": "sign_then_band", "legs": ["design_fp32"], "band": 0.10, "names": {"above": "ABSORBED HIGHER", "below": "ZERO HIGHER", "inside": "ALIKE"},
                        "what": "fp32's held share, absorbed less zero products, one session"},
            "E108-R5": {"kind": "power", "form": "band_then_sign", "legs": ["A_vs_B_priced"], "band": 0.5, "names": {"inside": "PRICED ALIKE", "above": "A DEARER", "below": "A CHEAPER"},
                        "what": "A's signs against B's, held: A's cost less B's scaled by their alternation counts"},
            "E108-R6": {"kind": "power", "form": "band_then_sign", "legs": ["fp32.A_on_B_held", "fp32.A_on_B_walk"], "band": 0.5, "names": {"inside": "NOTHING MEASURABLE", "above": "ADDS", "below": "SUBTRACTS"},
                        "what": "A's signs on top of B's, held and walking"},
            "E108-R7": {"kind": "power", "form": "bands", "legs": ["fp32.share_het"], "lo": 0.35, "hi": 0.65, "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "where the rest goes: the share of s_walk - s_abs that held accumulators differing as s_walk's do carry"},
            "E108-R12": {"kind": "power", "form": "bands", "legs": ["fp32.share_het_z"], "lo": 0.35, "hi": 0.65, "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                         "what": "the same on zero products, B's signs: the share of b_B_w - z_s that b_B_z, held at b_B_w's sums, carries"},
            "E108-R8": {"kind": "power", "form": "sign_then_band", "legs": ["fp32.ex_over_sg", "fp32.mx_over_ex"], "band": 0.25, "names": {"above": "RISES", "below": "FALLS", "inside": "ALIKE"},
                        "what": "the ladder: each step of the accumulators' difference (exponent, then mantissa) against the one before"},
            "E108-R9": {"kind": "power", "form": "bands", "legs": ["fp32.alt_ratio"], "lo": 0.85, "hi": 1.15, "names": {"inside": "HOLDS", "above": "RISES", "below": "FALLS"},
                        "what": "the alternation's price when the sums walk, over held, fp32"},
            "E108-R10": {"kind": "power", "form": "ratio_e104", "legs": ["alt_walk_ratio"], "ratio": 1.552, "equal_above": 1.2, "what": "E104-R6 replicated: fp16 over fp32, walking"},
            "E108-R11": {"kind": "power", "form": "rms", "what": "the bench's model on E108's float tiles: rms(D - M4)", "pass_w": 0.60, "fail_w": 1.00},
            "E108-S1": {"kind": "power", "form": "tie", "what": "the session tie against E82, dips removed: every cell inside its band"},
        },
        "not_scored_if": "fewer than 2 kept passes in the primary reduction: every power rule NOT SCORED. The read-back rule needs no pass.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e108.json"), "w"), indent=1)
    print("tiles", len(tiles), "runs per pass", reg["plan"]["runs_per_pass"], "rho", round(rho, 4))
    print(f"{'tile':16s} {'M4':>6s} [{'lo':>5s},{'hi':>6s}]  core   bus  rest clock  valid chk  counts")
    for n, r in tiles.items():
        q = r["pred"]
        print(f"{n:16s} {q['M']:6.2f} [{q['lo95']:5.2f},{q['hi95']:6.2f}]  {' '.join(f'{v:5.2f}' for v in q['terms_w'])} {r['valid_slots']:6.0f} {r['check_mismatch_words']:3.0f}  {r['counts_from'].split('/')[-1]}")
    for n, q in Q.items():
        print(f"{n:22s} {q['form']:8s} M4 {q['M']:7.3f}" + ("" if q["half95"] is None else f" ± {q['half95']:4.2f}"))


if __name__ == "__main__":
    main()
