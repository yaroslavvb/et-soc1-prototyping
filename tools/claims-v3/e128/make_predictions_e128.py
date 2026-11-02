#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E128 (Q136): freeze the registration: predictions-e128.json, from e128/e128.json, the bench's counts, the earlier sessions' committed values and the files'
hashes. Desk compute only. A port of tools/claims-v3/signloc/make_predictions_e108.py with E128's tiles, quantities and rules.

    python3 tools/claims-v3/e128/make_predictions_e128.py

M4 is not refitted: its coefficients, its card-1 scale and the interval's parts are recomputed here exactly as make_predictions_e104.py, _e106.py and _e108.py
did and checked against tools/claims-v3/kinds/e103/selection.json. The thresholds are here and in E128.md.
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
E = "tools/claims-v3/e128"
D = "docs/reports/data"
sys.path.insert(0, os.path.join(ROOT, D, "2026-11-01-q132-rtl-bench"))
from predict_m4 import fit, t975, x_float  # noqa: E402

DESK = f"{D}/2026-11-02-e128-fp16-signs/desk"
# the bench's counts, committed by the lanes that ran each tile on the same bench (rtl-sim/fma_toggle_v2); E128's new tiles in DESK (later files win)
COUNTS = [f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json", f"{D}/2026-11-01-q132-rtl-bench/counts-e88.json", f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json",
          f"{D}/2026-11-01-e104-c-readback/desk/counts-e104.json", f"{D}/2026-11-01-e104-c-readback/desk/counts-e104b.json",
          f"{D}/2026-11-01-e106-held-signs/desk/counts-e106.json", f"{D}/2026-11-01-e108-sign-located/desk/counts-e108.json",
          f"{D}/2026-11-01-e108-sign-located/desk/counts-e108b.json", f"{DESK}/counts-e128.json"]
# the earlier sessions this one is scored against (their committed scored.json: primary quantities, per pass)
E108_SCORED = f"{D}/2026-11-01-e108-sign-located/scored.json"
E122_SCORED = f"{D}/2026-11-01-e122-signs-replicate/scored.json"
E82_SCORED = f"{D}/2026-10-31-e82-kinds-aifoundry1/scored.json"
CARD1_PASSES_E108 = [10810, 10811, 10812, 10813]
# the binaries on aifoundry1's ~/nekko that the run executes (read on the box before this freeze: work/probe; E108's readback binaries.sha256 for three of them)
BINARIES = {
    "build/sparsity/host/sparsity_host": "e0fbecce35f252c546e6e8390f6a4694519674dc4d6dea359b0db9c4d1a3fbbe",
    "build/sparsity/kernel/sparsity.elf": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
    "build/e104/b/host/sparsity_host": "79bf5f2df92bcca13c8c77e394226cca4d53cff73b7f194d649adafa718086d7",
    "build/ettelem/ettelem": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",
}


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


def quantities():
    q = {}
    for t in ("fp32", "fp16"):
        p = t + "."
        q.update({
            p + "step": C([p + "signs"], [p + "ones"], f"the sign step, {t}"),
            p + "held_z": C([p + "z_s"], [p + "c_abs"], f"random B signs on zero products, the sum held (E104's z_s), {t}"),
            p + "rest_vs_z": C([p + "signs", p + "c_abs"], [p + "ones", p + "z_s"], f"the step less the zero-product held part (the step's rest), {t}"),
            # E108's design (fp32: E108's own tiles, a third session on card 1; fp16: the port)
            p + "Bz_het": C([p + "b_B_z"], [p + "z_s"], f"E108's design, {t}: held at b_B_w's sums over held at z_s's equal ones"),
            p + "Bz_walk": C([p + "b_B_w"], [p + "b_B_z"], f"E108's design, {t}: walking over held at the same sums at every op's end (alternations differ)"),
            p + "Bz_rest": C([p + "b_B_w"], [p + "z_s"], f"E108's design, {t}: B's rest on zero products"),
            # the matched triple: z_s, b_B_zm, b_B_wm alternate exactly as often
            p + "Bm_het": C([p + "b_B_zm"], [p + "z_s"], f"matched, {t}: the accumulators differing (held at b_B_wm's sums over z_s's equal ones)"),
            p + "Bm_walk": C([p + "b_B_wm"], [p + "b_B_zm"], f"matched, {t}: the sums changing (walking over held at the same op-end sums, the same alternations)"),
            p + "Bm_rest": C([p + "b_B_wm"], [p + "z_s"], f"matched, {t}: B's rest on zero products"),
            p + "held_alt": C([p + "b_B_z"], [p + "b_B_zm"], f"two held tiles with differing accumulators, {t}: E108's design over the matched one (other alternation counts and other C words)"),
            p + "walk_alt": C([p + "b_B_w"], [p + "b_B_wm"], f"two walking tiles, {t}: E108's design over the matched one (other alternation counts, A's sign, other sums)"),
            p + "alt_walk": C([p + "m_h_sub"], [p + "w_h_add"], f"alternating against a fixed product sign, walking, the same magnitudes (E104's pair), {t}"),
        })
    for t in ("fp32", "fp16"):
        p = t + "."
        q.update({
            p + "share_z": Rt(p + "held_z", p + "step", f"{t}'s held share, zero products, one session"),
            p + "share_het_z": Rt(p + "Bz_het", p + "Bz_rest", f"E108's design, {t}: how much of B's rest held accumulators at b_B_w's sums carry (E108-R12's form)"),
            p + "share_het_m": Rt(p + "Bm_het", p + "Bm_rest", f"matched, {t}: how much of B's rest goes with the accumulators differing"),
            p + "share_walk_m": Rt(p + "Bm_walk", p + "Bm_rest", f"matched, {t}: how much of B's rest goes with the sums changing"),
            p + "rest_ratio_m": Rt(p + "Bm_rest", p + "rest_vs_z", f"{t}: B's rest on zero products (matched) over the step's rest"),
        })
    q.update({
        "fp32.design_m": Df("fp32.share_het_m", "fp32.share_het_z", "fp32: the matched share less E108's design's share, one session"),
        "fp16.design_m": Df("fp16.share_het_m", "fp16.share_het_z", "fp16: the matched share less E108's design's share, one session"),
        "formats_m": Df("fp16.share_het_m", "fp32.share_het_m", "the location's like for like: fp16's matched share less fp32's"),
        "formats_z": Df("fp16.share_z", "fp32.share_z", "the held share's like for like (E108-R3's quantity), one session"),
        "alt_walk_ratio": Rt("fp16.alt_walk", "fp32.alt_walk", "E104-R6 / E108-R10: fp16 over fp32, walking"),
    })
    return q


def main():
    spec = load(f"{E}/e128/e128.json")
    bad = [(t, n) for t, v in spec["tiles"].items() for n, r in v["read"].items() if r["words_rtl_vs_fl"] or r["words_rtl_vs_manual"]]
    assert not bad, bad
    for ty, alts in spec["matched_alternations"].items():
        assert len({tuple(a) for a in alts.values()}) == 1, (ty, alts)
    assert all(len(v) == 64 for v in BINARIES.values())
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
    # the bench check: two reused tiles counted again on the build E128 used, against their committed counts
    chk = {}
    for mine, theirs, rel in (("fp32.chk_b_B_z", "fp32.b_B_z", f"{D}/2026-11-01-e108-sign-located/desk/counts-e108b.json"),
                              ("fp16.chk_z_s", "fp16.z_s", f"{D}/2026-11-01-e104-c-readback/desk/counts-e104b.json")):
        a_, b_ = counts[mine]["mean"], load(rel)["rows"][theirs]["mean"]
        same = json.dumps(a_, sort_keys=True) == json.dumps(b_, sort_keys=True)
        chk[theirs] = {"equal_word_for_word": same, "committed": rel}
        assert same, (mine, theirs)
    names = sorted(spec["tiles"])
    x_tile, m_tile, tiles = {}, {}, {}
    for name in names:
        t = name.split(".")[0]
        v = counts[name]
        z = zc[t + ".zeros"]["mean"]
        x = x_of(v["mean"], z, rate[t])
        p0 = float(x @ b)
        pts = [float(x_of(qq, z, rate[t]) @ b) * s for qq in v["points"]]
        m = float(np.std(pts, ddof=1) / math.sqrt(len(pts)))
        half = t_ * math.sqrt(pool ** 2 + s * s * float(x @ Cv @ x) + (p0 * se_s) ** 2 + m * m)
        x_tile[name], m_tile[name] = x, m
        tiles[name] = {"type": t, "kind": name.split(".")[1], "group": spec["tiles"][name]["group"], "how": spec["tiles"][name]["how"], "counts_from": src[name],
                       "alternations_per_op": [spec["tiles"][name]["counts_real"]["alt1"], spec["tiles"][name]["counts_real"]["alt2"]],
                       "pred": {"M": p0 * s, "lo95": max(p0 * s - half, 0.0), "hi95": p0 * s + half, "half95": half, "launch_points_w": pts, "terms_w": [float(c) * s for c in x * b]},
                       "check_mismatch_words": v["mean"]["check_mismatch"], "valid_slots": v["mean"]["valid_slots"], "cycles": v["mean"]["cycles"]}

    Q = quantities()
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

    # the earlier sessions: card 1 (E108) and aifoundry3 (E122), and E82's per-type card scale between them
    s108 = load(E108_SCORED)["primary"]["quantities"]
    s122 = load(E122_SCORED)["primary"]["quantities"]
    sc = load(E82_SCORED)["cross_card"]["primary"]["x3"]["per_type_median"]
    scale = {"fp32": sc["fp32"], "fp16": sc["fp16"]}

    def ref(sq, name):
        c = sq[name]
        return {"mean": c["mean"], "ci95": c["ci95"], "n": c["n"], "per_pass": c["per_pass"]}

    x_rules = []
    for of, unit, w, s_ in (("alt_walk_ratio", "ratio", 0.60, 1.0), ("fp32.alt_walk", "W", 0.75, scale["fp32"]), ("fp16.alt_walk", "W", 0.75, scale["fp16"]),
                            ("fp32.share_het_z", "ratio", 0.15, 1.0), ("fp32.Bz_het", "W", 0.75, scale["fp32"]), ("fp32.Bz_rest", "W", 0.75, scale["fp32"]),
                            ("fp32.step", "W", 0.75, scale["fp32"]), ("fp16.step", "W", 0.75, scale["fp16"])):
        x_rules.append({"id": f"X108-{of}", "of": of, "against": "E108 (aifoundry1 card 1, this card)", "ref": ref(s108, of), "scale": 1.0, "w": w, "unit": unit})
        x_rules.append({"id": f"X122-{of}", "of": of, "against": "E122 (aifoundry3 card 0), divided by E82's per-type card scale", "ref": ref(s122, of),
                        "scale": 1.0 / s_ if unit == "W" else 1.0, "w": w, "unit": unit})
    pooled_ref = {"E108": {p: v for p, v in s108["alt_walk_ratio"]["per_pass"].items()}, "E122": {p: v for p, v in s122["alt_walk_ratio"]["per_pass"].items()}}

    files = [f"{E}/{f}" for f in ("e128_common.py", "run_e128.py", "block_e128.sh", "queue_e128.sh", "run_e128.sh", "reduce_e128.py", "score_e128.py", "collect_e128.sh",
                                    "readback_e128.py", "block_readback_e128.sh", "ettelem_guard.sh")]
    nod = e82
    reg = {
        "experiment": "E128",
        "title": "a random sign's rest in fp16, and the part that goes with the sums changing: E108's held-tile designs ported to fp16, a held/walking triple matched in alternation counts in both formats, and the fp16/fp32 moving-sum ratio scored against both cards' sessions, aifoundry1 card 1 at 600 MHz",
        "request": "Q136 (the owner's 'continue the experiments', Mon 2 Nov 2026), from Q134's final critic, item 4; the kinds page's section 11 item 5",
        "date": "2026-11-02",
        "registration": f"{E}/E128.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {**{f"counts_{i}": {"path": rel, "sha256": sha(rel)} for i, rel in enumerate(COUNTS)},
                          "selection_e103": {"path": f"{K}/e103/selection.json", "sha256": sha(f"{K}/e103/selection.json")},
                          "e108_scored": {"path": E108_SCORED, "sha256": sha(E108_SCORED)}, "e122_scored": {"path": E122_SCORED, "sha256": sha(E122_SCORED)},
                          "e82_scored": {"path": E82_SCORED, "sha256": sha(E82_SCORED)}},
        "harness": {"reused_unchanged_sha256": reused, "e128_json_sha256": sha(f"{E}/e128/e128.json"), "e128_files_sha256": {f: sha(f) for f in files},
                    "binaries_sha256": BINARIES},
        "bench_check": chk,
        "plan": {"passes": [12810, 12811, 12812, 12813, 12814], "smoke": 12801, "readback": 12802, "runs_per_pass": 2 + 18 + len(spec["power"]) + len(spec["compare"]),
                 "items_per_pass": f"the tie twice, E78's six anchors three times, E128's {len(spec['power'])} tiles and E78's two ones once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's)", "min_kept_passes_scored": 2, "min_tile_passes": 2},
        "card_budget": {"card_minutes_at_most": 40, "queue_budget_s": 2040, "first_pass_estimate_s": 420, "queue_deadline": "2026-11-02 15:50 PST"},
        "model": {"name": "M4", "coef_fJ": fm["coef_fJ"], "card1_scale": s, "card1_scale_se": se_s, "interval_pool": fm["interval_pool"]},
        "matched_alternations": spec["matched_alternations"],
        "tiles": tiles,
        "quantities": Q,
        "session_tie": {"reference": f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json items.<cell>.D.mean (dips removed, as E128's primary)",
                        "cells": {c: {"ref_w": round(nod[c]["D"]["mean"], 4), "band_w": w} for c, w in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}},
        "cross_session": {"scale_e82_aifoundry3_over_card1": scale, "rule": "d = Q128 - s Qref; h = sqrt(h128^2 + (s href)^2); PASS if |d| + h <= w, FAIL if |d| - h > w, else INCONCLUSIVE (E122's X form); s = 1 against E108 (this card) and for a ratio, 1 / E82's per-type scale for a W contrast against E122",
                          "rules": x_rules, "aggregate": "PASS if no X rule FAILs and at least 8 of the 16 PASS; FAIL if 3 or more FAIL; else INCONCLUSIVE"},
        "pooled": {"of": "alt_walk_ratio", "ref_per_pass": pooled_ref, "rule": "every kept pass of the three sessions (E108's 4 on card 1, E122's 4 on aifoundry3, this session's) is one replicate of the ratio; mean +- t(0.975, n - 1) sd / sqrt(n); E104-R6's bands",
                   "arm": "inverse-variance weighted mean of the three sessions' means (each session's se = its ci95 / t(0.975, n - 1)), +- 1.96 se, labelled"},
        "rules": {
            "E128-R1": {"kind": "read", "what": "every tile, at every length, every word of all 1,024 minions: the three readings coincide on these tiles, so a miss means the tile is not what it is called", "reads": {t: spec["readback"][t] for t in spec["tiles"]}},
            "E128-R2": {"kind": "power", "form": "step_band", "what": "the step on this card, a third session: signs - ones in each format against E108's", "e108_w": {"fp32": s108["fp32.step"]["mean"], "fp16": s108["fp16.step"]["mean"]}, "band_w": 1.0},
            "E128-R3": {"kind": "power", "form": "bands", "legs": ["fp32.share_het_m"], "lo": 0.35, "hi": 0.65, "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "fp32, matched: the share of B's rest (b_B_wm - z_s) that the accumulators differing carry (b_B_zm - z_s), with the alternations equal"},
            "E128-R4": {"kind": "power", "form": "band_then_sign", "legs": ["fp32.share_walk_m"], "band": 0.10, "names": {"inside": "ALMOST NONE", "above": "SOME", "below": "NEGATIVE"},
                        "what": "fp32, matched: the share of B's rest that goes with the sums changing (b_B_wm - b_B_zm), with the alternations equal"},
            "E128-R5": {"kind": "power", "form": "sign_then_band", "legs": ["fp32.design_m"], "band": 0.10, "names": {"above": "MATCHED HIGHER", "below": "MATCHED LOWER", "inside": "ALIKE"},
                        "what": "fp32: the matched share less E108's design's share, one session: did E108's unequal alternation counts move R12"},
            "E128-R6": {"kind": "power", "form": "bands", "legs": ["fp32.share_het_z"], "lo": 0.35, "hi": 0.65, "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "fp32, E108's design (E108-R12 again, a third session on card 1)"},
            "E128-R7": {"kind": "power", "form": "bands", "legs": ["fp16.share_het_z"], "lo": 0.35, "hi": 0.65, "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "fp16, E108's design ported: the share of B's rest that b_B_z, held at b_B_w's sums, carries"},
            "E128-R8": {"kind": "power", "form": "bands", "legs": ["fp16.share_het_m"], "lo": 0.35, "hi": 0.65, "names": {"inside": "ABOUT HALF", "above": "MOST", "below": "LITTLE"},
                        "what": "fp16, matched: the share of B's rest that the accumulators differing carry, with the alternations equal"},
            "E128-R9": {"kind": "power", "form": "band_then_sign", "legs": ["fp16.share_walk_m"], "band": 0.10, "names": {"inside": "ALMOST NONE", "above": "SOME", "below": "NEGATIVE"},
                        "what": "fp16, matched: the share of B's rest that goes with the sums changing, with the alternations equal"},
            "E128-R10": {"kind": "power", "form": "ratio_e104", "legs": ["alt_walk_ratio"], "ratio": 1.552, "equal_above": 1.2, "what": "E104-R6 / E108-R10 in this session: fp16 over fp32, walking"},
            "E128-R12": {"kind": "power", "form": "sign_then_band", "legs": ["formats_m"], "band": 0.10, "names": {"above": "FP16 HIGHER", "below": "FP16 LOWER", "inside": "ALIKE"},
                         "what": "the location's like for like: fp16's matched share less fp32's, one session"},
            "E128-R11": {"kind": "power", "form": "rms", "what": "the bench's model on E128's tiles: rms(D - M4); and on the six new ones alone (reported)", "pass_w": 0.60, "fail_w": 1.00},
            "E128-S1": {"kind": "power", "form": "tie", "what": "the session tie against E82, dips removed: every cell inside its band"},
            "E128-X": {"kind": "cross", "what": "this session against E108 (card 1) and E122 (aifoundry3) at E82's per-type card scale: R10's ratio and its two legs, E108-R12's share and legs, the steps"},
            "E128-P": {"kind": "pooled", "form": "ratio_e104", "ratio": 1.552, "equal_above": 1.2, "what": "the moving-sum ratio over the three sessions' kept passes (E108, E122, E128)"},
        },
        "not_scored_if": "fewer than 2 kept passes in the primary reduction: every power, cross and pooled rule NOT SCORED. The read-back rule needs no pass.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e128.json"), "w"), indent=1)
    print("tiles", len(tiles), "runs per pass", reg["plan"]["runs_per_pass"], "bench check", chk)
    print(f"{'tile':16s} {'M4':>6s} [{'lo':>5s},{'hi':>6s}]  core   bus  rest clock  valid chk  alt  counts")
    for n, r in tiles.items():
        q = r["pred"]
        print(f"{n:16s} {q['M']:6.2f} [{q['lo95']:5.2f},{q['hi95']:6.2f}]  {' '.join(f'{v:5.2f}' for v in q['terms_w'])} {r['valid_slots']:6.0f} {r['check_mismatch_words']:3.0f} "
              f"{r['alternations_per_op'][0]:6.0f}+{r['alternations_per_op'][1]:<6.0f} {r['counts_from'].split('/')[-1]}")
    for n, q in Q.items():
        print(f"{n:22s} {q['form']:8s} M4 {q['M']:7.3f}" + ("" if q["half95"] is None else f" ± {q['half95']:4.2f}"))


if __name__ == "__main__":
    main()
