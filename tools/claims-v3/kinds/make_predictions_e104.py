#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E104 (Q132): freeze the registration: predictions-e104.json, from e104/e104.json, the bench's counts of E104's tiles and the files' hashes. Desk compute only.

    python3 tools/claims-v3/kinds/make_predictions_e104.py

THE READINGS, frozen before any E104 run.
  C, three: frozen (make_e88's fl(n S)), the manual's (PRM 9.3.3: the exact sum, then toward zero, manual_e104.c) and the RTL's (each aligned term truncated separately, accum.c, fp16_model.py, the fixed bench). Word for word in e104/e104.json.
  Watts, two. E92's frozen reading: fp16's h_sub and c_alt hold their sums, so their premium is the price of alternation; numbers: E92's dips-removed values on aifoundry3 times card 1's float scale, 0.9722 (E103's frame), and 14/15 of them on
  u_sub. The fault's reading: fp16's h_sub parts its halves and swings the result bus on every micro-op, u_sub does not; numbers: the bench's model M4 (frozen before E95, tested blind in E103), fitted on E78 alone, from counts the fixed RTL bench takes
  on the real sums.

M4 is not refitted: its coefficients, its card-1 scale and the interval's parts are recomputed here exactly as select_e103.py did and checked against e103/selection.json. The thresholds are here and in E104.md.
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

DESK = f"{D}/2026-11-01-e104-c-readback/desk"
SCALE_NOTE = "E103's card-1 float scale, E82 dips removed through the origin over E82's float kinds, model M4: the same number carries E92's aifoundry3 watts to card 1 only as an estimate"
# E92's dips-removed arm on aifoundry3 (docs/reports/data/2026-11-01-e92-sign-split/README.md, dips-arm), the frame nearest E104's primary
E92_DIPS = {"fp16.h_premium": 6.812, "fp16.c_alt - c_abs": 7.258, "fp16.s_abs - c_abs": 4.587, "fp16.signs - ones": 4.965, "fp32.h_premium": 4.396, "fp32.s_abs - c_abs": 2.520, "fp32.signs - ones": 5.016, "fp32.w_premium": 2.785}
E92_RATIO = 1.552


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def x_of(m, z, rate):
    return np.array(x_float(m, z), float) * rate


def main():
    spec = load(f"{K}/e104/e104.json")
    bad = [n for n, cs in spec["checks"].items() if not all(c["ok"] for c in cs)]
    assert not bad, bad
    # what the read-back rules assume, checked at the desk: where the two readings must differ, and where they must coincide
    r1 = ("fp16.h_sub", "fp16.c_alt", "fp16.h_allsub", "fp16.hh_sub", "fp16.hl_sub", "fp16.s_abs")
    r3 = ("fp16.r_abs", "fp16.r_walk", "fp16.u_sub", "fp32.pm_pi", "fp32.bj_6")
    gate = ("fp16.c_abs", "fp16.h_add", "fp32.c_abs", "fp32.h_add")
    same = gate + ("fp16.z_add", "fp16.z_sub", "fp16.z_s", "fp16.z_allsub", "fp16.z_hh", "fp16.z_hl", "fp16.x_add", "fp16.x_sub", "fp16.w_h_add", "fp16.w_h_sub", "fp16.w_c", "fp16.m_h_sub", "fp16.signs",
                   "fp32.h_sub", "fp32.u_sub", "fp32.c_alt", "fp32.h_allsub", "fp32.s_abs", "fp32.r_abs", "fp32.z_add", "fp32.z_sub", "fp32.z_s", "fp32.w_h_add", "fp32.w_h_sub", "fp32.w_c", "fp32.m_h_sub", "fp32.signs")
    for t in r1 + r3:
        assert all(v["words_rtl_vs_fl"] > 0 for v in spec["tiles"][t]["read"].values()), t
    for t in same:
        assert all(v["words_rtl_vs_fl"] == 0 and v["words_rtl_vs_manual"] == 0 for v in spec["tiles"][t]["read"].values()), t
    # the manual's and the RTL's readings part on these, at every length
    for t in ("fp16.hh_sub", "fp16.hl_sub", "fp16.s_abs", "fp16.r_abs"):
        assert all(v["words_rtl_vs_manual"] > 0 and v["words_fl_vs_manual"] >= 0 for v in spec["tiles"][t]["read"].values()), t
    # and the manual's reading holds these two where the RTL's walks: its sum is frozen, one word
    for t in ("fp16.hh_sub", "fp16.hl_sub"):
        assert all(v["words_fl_vs_manual"] == 0 and v["distinct"]["manual"] == 1 for v in spec["tiles"][t]["read"].values()), t
    # h_sub, c_alt and h_allsub cannot part the manual from the RTL
    for t in ("fp16.h_sub", "fp16.c_alt", "fp16.h_allsub"):
        assert all(v["words_rtl_vs_manual"] == 0 for v in spec["tiles"][t]["read"].values()), t
    e94 = load(f"{K}/predictions-e94.json")
    reused = e94["harness"]["reused_unchanged_sha256"]
    miss = [r for r, w in reused.items() if sha(r) != w]
    assert not miss, miss
    sel = load(f"{K}/e103/selection.json")
    zc = load(f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json")["rows"]
    e78 = load(f"{D}/2026-10-31-e78-kinds-energy-matrix/e78.json")["items"]
    e82 = load(f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")["items"]
    rate = {t: e78[f"{t}.randn"]["rate"]["mean"] for t in ("fp32", "fp16")}
    # M4, as select_e103.py computes it
    want = lambda t: t != "int8"

    def rows(items):
        X, y = [], []
        for k, v in zc.items():
            t, name = v["type"], v["kind"]
            if not want(t) or name == "zeros":
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
    names = ["k_core", "k_bus", "k_rest", "a_clocked"]
    for nm, v in zip(names, b):
        assert abs(v * 1e15 - fm["coef_fJ"][nm]) < 1e-6, (nm, v * 1e15, fm["coef_fJ"][nm])
    assert abs(s - fm["card1_scale"]) < 1e-9 and abs(se_s - fm["card1_scale_se"]) < 1e-9
    pool, npool = fm["interval_pool"]["rms_w"], fm["interval_pool"]["n"]
    t_ = t975(npool - 2)

    counts = {}
    counts.update(load(f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json")["rows"])
    counts.update(load(f"{DESK}/counts-e104.json")["rows"])
    counts.update(load(f"{DESK}/counts-e104b.json")["rows"])
    counts.update(load(f"{DESK}/counts-e104c.json")["rows"])
    # E88's and E92's fp32.w_* are in both files, from one tile and one bench: the later one is used, and they must agree
    x_tile, m_tile, tiles = {}, {}, {}
    groups = {"h_": "frozen, by E92's reading", "c_": "frozen, by E92's reading", "s_": "frozen, by E92's reading", "u_": "halves together", "z_": "truly frozen, zero products", "x_": "truly frozen, products cancel", "w_": "moving", "m_": "moving"}
    for name in spec["power"]:
        t = spec["tiles"][name]["type"]
        v = counts[name]
        z = zc[t + ".zeros"]["mean"]
        x = x_of(v["mean"], z, rate[t])
        p0 = float(x @ b)
        pts = [float(x_of(q, z, rate[t]) @ b) * s for q in v["points"]]
        m = float(np.std(pts, ddof=1) / math.sqrt(len(pts)))
        half = t_ * math.sqrt(pool ** 2 + s * s * float(x @ C @ x) + (p0 * se_s) ** 2 + m * m)
        x_tile[name], m_tile[name] = x, m
        kind = spec["tiles"][name]["kind"]
        tiles[name] = {"type": t, "kind": kind, "group": next(g for pre, g in groups.items() if kind.startswith(pre)),
                       "pred": {"M": p0 * s, "lo95": max(p0 * s - half, 0.0), "hi95": p0 * s + half, "half95": half, "launch_points_w": pts, "terms_w": [float(c) * s for c in x * b]},
                       "check_mismatch_words": v["mean"]["check_mismatch"], "valid_slots": v["mean"]["valid_slots"], "cycles": v["mean"]["cycles"], "unit_nets_map": v["mean"]["unit"]["nets_map"], "ff_toggles": v["mean"]["ff"]["all"]["toggles"]}

    def cdef(plus, minus, what, frozen=None):
        xx = sum(x_tile[n] for n in plus) - sum(x_tile[n] for n in minus)
        p0 = float(xx @ b)
        n_t = len(plus) + len(minus)
        var = n_t * pool ** 2 + s * s * float(xx @ C @ xx) + (p0 * se_s) ** 2 + sum(m_tile[n] ** 2 for n in list(plus) + list(minus))
        return {"plus": list(plus), "minus": list(minus), "what": what, "M": p0 * s, "half95": t_ * math.sqrt(var), "frozen_reading_w": frozen}

    sc = s
    e = {k: v * sc for k, v in E92_DIPS.items()}
    # the fp32 moving premium's m_ form has no E92 value of its own: the frozen reading's ratio applies to whichever is measured
    u = 14.0 / 15.0
    contrasts = {
        "fp16.h_premium": cdef(["fp16.h_sub"], ["fp16.h_add"], "E92's fp16 add/subtract premium", e["fp16.h_premium"]),
        "fp16.u_premium": cdef(["fp16.u_sub"], ["fp16.h_add"], "the same with the halves together: the adder swings, the result bus does not", u * e["fp16.h_premium"]),
        "fp16.z_premium": cdef(["fp16.z_sub"], ["fp16.z_add"], "the alternation on zero products: the sum truly holds and the adder's output does not swing", e["fp16.h_premium"]),
        "fp16.h_sub - u_sub": cdef(["fp16.h_sub"], ["fp16.u_sub"], "the two halves' swing on the result path, E104-R4", (1 - u) * e["fp16.h_premium"]),
        "fp16.u_premium - z_premium": cdef(["fp16.u_sub", "fp16.z_add"], ["fp16.h_add", "fp16.z_sub"], "what an absorbed operand adds over a zero one: the adder's output swinging"),
        "fp16.m_premium": cdef(["fp16.m_h_sub"], ["fp16.w_h_add"], "fp16's missing moving-sum pair: same magnitudes, adder alternating or not", E92_RATIO * e["fp32.w_premium"]),
        "fp16.c_alt - c_abs": cdef(["fp16.c_alt"], ["fp16.c_abs"], "E92's second fp16 contrast", e["fp16.c_alt - c_abs"]),
        "fp16.s_abs - c_abs": cdef(["fp16.s_abs"], ["fp16.c_abs"], "E92's frozen random signs on fp16: the 92%", e["fp16.s_abs - c_abs"]),
        "fp16.z_s - c_abs": cdef(["fp16.z_s"], ["fp16.c_abs"], "random signs in a sum that truly holds", e["fp16.s_abs - c_abs"]),
        "fp16.h_add - c_abs": cdef(["fp16.h_add"], ["fp16.c_abs"], "the operand and sum signs alone"),
        "fp16.z_add - c_abs": cdef(["fp16.z_add"], ["fp16.c_abs"], "the operand and sum signs on zero products"),
        "fp32.h_premium": cdef(["fp32.h_sub"], ["fp32.h_add"], "E92's fp32 premium, where nothing is in dispute", e["fp32.h_premium"]),
        "fp32.u_premium": cdef(["fp32.u_sub"], ["fp32.h_add"], "the same at 14/15 of the alternations", u * e["fp32.h_premium"]),
        "fp32.z_premium": cdef(["fp32.z_sub"], ["fp32.z_add"], "the alternation on zero products", e["fp32.h_premium"]),
        "fp32.h_sub - u_sub": cdef(["fp32.h_sub"], ["fp32.u_sub"], "the control on R4: both sums hold, only 1/15 of the alternations differ", (1 - u) * e["fp32.h_premium"]),
        "fp32.u_premium - z_premium": cdef(["fp32.u_sub", "fp32.z_add"], ["fp32.h_add", "fp32.z_sub"], "what an absorbed operand adds over a zero one, fp32"),
        "fp32.m_premium": cdef(["fp32.m_h_sub"], ["fp32.w_h_add"], "fp32's moving pair with w_h_add's magnitudes", e["fp32.w_premium"]),
        "fp32.z_s - c_abs": cdef(["fp32.z_s"], ["fp32.c_abs"], "random signs on zero products, fp32", e["fp32.s_abs - c_abs"]),
        "fp32.h_add - c_abs": cdef(["fp32.h_add"], ["fp32.c_abs"], "the operand and sum signs alone, fp32"),
    }
    files = [f"{K}/{f}" for f in ("e104_common.py", "run_e104.py", "block_e104.sh", "queue_e104.sh", "run_e104.sh", "reduce_e104.py", "score_e104.py", "collect_e104.sh", "readback_e104.py", "block_readback_e104.sh", "build_host_e104.sh", "patch_host_e104.py", "manual_e104.c")]
    nod = load(f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")["items"]
    reg = {
        "experiment": "E104",
        "title": "the accumulators read back, and fp16's add/subtract premium on sums that really do or do not move, on aifoundry1 card 1 at 600 MHz",
        "request": "Q132: the fault lane a1c1-e102-bits found in the lab's tools",
        "date": "2026-11-01",
        "registration": f"{K}/E104.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {
            "counts_e78": {"path": f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json", "sha256": sha(f"{D}/2026-11-01-q132-rtl-bench/counts-v2.json")},
            "counts_e92": {"path": f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json", "sha256": sha(f"{D}/2026-11-01-q132-rtl-bench/counts-e92.json")},
            "counts_e104": {"path": f"{DESK}/counts-e104.json", "sha256": sha(f"{DESK}/counts-e104.json")},
            "counts_e104b": {"path": f"{DESK}/counts-e104b.json", "sha256": sha(f"{DESK}/counts-e104b.json")},
            "counts_e104c": {"path": f"{DESK}/counts-e104c.json", "sha256": sha(f"{DESK}/counts-e104c.json")},
            "desk_check": {"path": f"{DESK}/desk-e104.txt", "sha256": sha(f"{DESK}/desk-e104.txt")},
            "selection_e103": {"path": f"{K}/e103/selection.json", "sha256": sha(f"{K}/e103/selection.json")},
        },
        "harness": {"reused_unchanged_sha256": reused, "e104_json_sha256": sha(f"{K}/e104/e104.json"), "e104_files_sha256": {f: sha(f) for f in files}},
        "plan": {"passes": [10410, 10411, 10412], "smoke": 10401, "readback": 10402, "runs_per_pass": 2 + 18 + len(tiles), "items_per_pass": f"the tie twice, E78's six anchors three times, E104's {len(tiles)} tiles once",
                 "reduction_primary": "dips removed, leak 0.2414 (E82's)", "min_kept_passes_scored": 2, "min_tile_passes": 2},
        "card_budget": {"card_minutes_about": 25, "queue_budget_s": 1300, "first_pass_estimate_s": 420, "queue_deadline": "2026-11-01 07:00 PST", "every_run_ends_by": "07:15 PST"},
        "model": {"name": "M4", "coef_fJ": fm["coef_fJ"], "card1_scale": s, "card1_scale_se": se_s, "interval_pool": fm["interval_pool"], "scale_note": SCALE_NOTE},
        "e92_dips_on_aifoundry3_w": E92_DIPS,
        "e92_ratio": E92_RATIO,
        "tiles": tiles,
        "contrasts": contrasts,
        "session_tie": {"reference": f"{D}/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json items.<cell>.D.mean (dips removed, as E104's primary)",
                        "cells": {c: {"ref_w": round(nod[c]["D"]["mean"], 4), "band_w": w} for c, w in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}},
        "rules": {
            "E104-R1": {"kind": "read", "what": "the accumulators of E92's fp16 'frozen' tiles, read back: every word of every minion against the three readings", "tiles": list(r1),
                        "verdicts": {"RTL": "every read of all six equals accum.c", "MANUAL": "every read of all six equals the exact sum truncated: h_sub walks, hh_sub and hl_sub hold one word", "FROZEN": "every read of all six equals fl(n S): h_sub holds one word", "NONE": "no reading fits: report the first mismatch and the rate", "UNREAD": "a read is missing or the minions disagree"}},
            "E104-R2": {"kind": "read", "what": "the controls, where the three readings coincide: the read path itself, and that the new designs do what they were built to. If a gate tile misses, the read-back is broken and R1 and R3 are not scored", "gate_tiles": list(gate), "tiles": list(same)},
            "E104-R3": {"kind": "read", "what": "the fault's other tiles, read back: E88's fp16.r_abs and r_walk, E104's fp16.u_sub (its halves meet each op), and fp32's near-identical bj_6 and pm_pi", "tiles": list(r3)},
            "E104-R4": {"kind": "power", "what": "where fp16's h_sub premium goes: h_sub - u_sub, the two halves' swing on the result path, 95% t over passes, with fp32's as the control", "frozen_band_w": 1.0, "M_w": contrasts["fp16.h_sub - u_sub"]["M"],
                        "verdicts": {"FROZEN-READING": "the interval lies inside +-1 W: E92's reading holds", "RESULT-PATH": "the interval lies above +1 W: the moving result pays that much of E92's premium", "INCONCLUSIVE": "else"}},
            "E104-R5": {"kind": "power", "what": "E92's 1.55x with the halves together: fp16 u premium over fp32 u premium, per pass", "e92_ratio": E92_RATIO, "equal_above": 1.2, "verdicts": {"1.55x HOLDS": "the interval holds 1.552 and lies above 1.2", "1.55x GOES": "the interval lies below 1.552", "INCONCLUSIVE": "else"}},
            "E104-R6": {"kind": "power", "what": "E92's 1.55x, moving regime: fp16 m premium over fp32 m premium, per pass", "e92_ratio": E92_RATIO, "equal_above": 1.2, "verdicts": {"1.55x HOLDS": "as R5", "1.55x GOES": "as R5", "INCONCLUSIVE": "else"}},
            "E104-R7": {"kind": "power", "what": "the bench's model on E104's float tiles: rms(D - M4)", "pass_w": 0.60, "fail_w": 1.00},
            "E104-R8": {"kind": "power", "what": "E92's fp16 watts stand: fp16 h_sub - h_add on this card against E92's dips-removed value carried by 0.9722", "e92_dips_w": E92_DIPS["fp16.h_premium"], "scale": s, "band_w": 1.0},
            "E104-S1": {"kind": "power", "what": "the session tie against E82, dips removed: every cell inside its band"},
        },
        "not_scored_if": "fewer than 2 kept passes in the primary reduction: every power rule NOT SCORED. The read-back rules need no pass; a gate tile that misses leaves R1 and R3 NOT SCORED.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e104.json"), "w"), indent=1)
    print("tiles", len(tiles), "runs per pass", reg["plan"]["runs_per_pass"])
    print(f"{'tile':14s} {'M4':>6s} [{'lo':>5s},{'hi':>6s}]  terms core bus rest clock    valid  cycles chk")
    for n, r in tiles.items():
        q = r["pred"]
        print(f"{n:14s} {q['M']:6.2f} [{q['lo95']:5.2f},{q['hi95']:6.2f}]  {' '.join(f'{v:5.2f}' for v in q['terms_w'])}  {r['valid_slots']:6.0f} {r['cycles']:6.1f} {r['check_mismatch_words']:3.0f}")
    print(f"{'contrast':34s} {'M4':>6s} {'±':>5s} {'frozen reading':>14s}")
    for n, c in contrasts.items():
        print(f"{n:34s} {c['M']:6.2f} {c['half95']:5.2f} {'' if c['frozen_reading_w'] is None else format(c['frozen_reading_w'], '14.2f')}")


if __name__ == "__main__":
    main()
