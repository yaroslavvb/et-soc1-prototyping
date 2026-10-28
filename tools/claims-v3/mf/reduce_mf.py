#!/usr/bin/env python3
"""E75 (V3-MF) reduction, exactly the decision rules frozen in mf/predictions.json and mf/README.md.

    python3 tools/claims-v3/mf/reduce_mf.py <pass dir> [<pass dir> ...] --gen <make_mf.py dir>
        --pred tools/claims-v3/mf/predictions.json --out mf.json [--csv runs.csv] [--leak auto|<W per C>]

Written on the day of the run (departure D-M1, 28 Oct 2026): the registration left E75's reducer to the running
agent and named the rules it had to implement. It reuses reduce_hl.py's per-run machinery unchanged — runs_of_pass
(the [t0+1 s, t0+3 s) board window, the rail window, the leakage correction's inputs), leak_slope, fit_line and
mean_se — and adds only the registered estimator:

  rule 1  per level, within-pass least squares of leakage-corrected board power on changed bits per transfer over
          the k-arm; the mean over passes with a two-sided t interval on the between-pass scatter (df = n - 1);
          the slope converted with each run's OWN measured rate, never an assumed one. The w-arm the same way.
          Implementation note (amendment 28 Oct 2026, departure D-M5): the W-per-bit slope is converted to pJ
          with the MEAN of the level's own measured rates (mean over the pass's runs, then over passes), not run
          by run, because the slope itself is a per-pass quantity. No rate is ever assumed. Measured size of the
          difference: the within-level spread of ops_per_s is 1e-5 to 2e-3 relative (L2 9.8e-6, L1 3.6e-4,
          DRAM 1.3e-4, L3 2.1e-3), so it moves no published digit.
  rule 2  saturation = the signed departure of the top rung from the line through the two lowest rungs, with its
          own interval, as a number.
  rule 3  burst gate: a run whose telemetry median took_ms in its window exceeds 60 ms is dropped; a level losing
          more than a third of its runs in a pass is reported unresolved at that level, not averaged.
  rule 4  temperature: the approach gates, plus slopes with and without a die-temperature covariate.

A "transfer" is one element: a 32 B `flw.ps` at L1, a 64 B line at L2/L3/DRAM (stride 64 fetches one line per
load). The transfer rate is therefore the device record's own `ops_per_s` (loads per second), and `bytes_per_s`
is carried beside it for the per-byte figures and for P7's rate bands.
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hl"))
from reduce_hl import fit_line, leak_slope, load_jsonl, mean_se, runs_of_pass  # noqa: E402

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
LEVELS = ["l1", "l2", "l3", "dram"]
CHORD = {"l1": 0.0502, "dram": 12.73}          # published zeros-vs-random chord slopes, pJ per changed bit
RANDOM_K = {256: 95.6, 512: 191.1}             # the random law's changes per element
RANDOM_W = {256: 145.3, 512: 290.7}            # and its ones per element


def t975(df):
    return T975.get(df, 1.96)


def ci(values):
    m, se, n = mean_se(values)
    if m is None:
        return {"mean": None, "se": None, "n": 0, "lo": None, "hi": None}
    half = t975(n - 1) * se if (se is not None and n > 1) else None
    return {"mean": m, "se": se, "n": n, "lo": (m - half) if half is not None else None,
            "hi": (m + half) if half is not None else None}


def ec_fields(d):
    out = {}
    for r in load_jsonl(os.path.join(d, "runs.jsonl")):
        if r.get("kind") == "fma":
            continue
        out.setdefault((r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1)), []).append(r)
    agg = {}
    for key, rr in out.items():
        agg[key] = {"ops_per_s": float(np.mean([x["ops_per_s"] for x in rr])),
                    "bytes_per_s": float(np.mean([x["bytes_per_s"] for x in rr])),
                    "wall_s": float(np.mean([x["wall_s"] for x in rr])),
                    "launches": len(rr), "ok": all(x.get("ok", False) for x in rr)}
    return agg


def took_ms_window(d, runs):
    """rule 3: the median telemetry took_ms inside each run's own power window."""
    path = os.path.join(d, "telemetry.jsonl")
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return
    op = gzip.open if path.endswith(".gz") else open
    tel = []
    for line in op(path, "rt"):
        if line.startswith("{"):
            try:
                s = json.loads(line)
                tel.append((s["t_ms"], s.get("took_ms")))
            except (ValueError, KeyError):
                pass
    for r in runs:
        lo = r["_t0_ms"]
        v = [tk for (t, tk) in tel if tk is not None and lo <= t < lo + 4000]
        r["took_ms_med"] = float(np.median(v)) if v else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    a = ap.parse_args()

    pred = json.load(open(a.pred))
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}

    R, card = [], None
    for d in a.dirs:
        rr, c = runs_of_pass(d, man)
        card = card or c
        ec = ec_fields(d)
        for r in rr:
            r.update(ec.get((r["pass"], r["item"], r["pos"], r["attempt"]), {}))
            r["_t0_ms"] = None
        # t0 per run, for the took_ms window
        by = {}
        for x in load_jsonl(os.path.join(d, "runs.jsonl")):
            key = (x["block"], x["item"], x.get("pos", 0), x.get("attempt", 1))
            by[key] = min(by.get(key, x["t_start_ms"]), x["t_start_ms"])
        for r in rr:
            r["_t0_ms"] = by.get((r["pass"], r["item"], r["pos"], r["attempt"]))
        took_ms_window(d, rr)
        R += rr
    if not R:
        raise SystemExit("no runs: is telemetry.jsonl in the pass directories?")

    k_leak, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
    clocks = sorted({m for r in R for m in r["mhz"]})
    mv_med = {p: float(np.median([r["mv"] for r in R if r["pass"] == p])) for p in {r["pass"] for r in R}}
    for r in R:
        it = man.get(r["item"], {})
        r["p80"] = r["p_raw"] - k_leak * (r["t_win"] - r["start_c"])
        r["level"] = it.get("level")
        r["k"] = it.get("k")
        r["w"] = it.get("w")
        r["elem_bits"] = it.get("elem_bits")
        r["arm"] = ("k" if (it.get("family") or "").endswith("_k") else
                    "w" if (it.get("family") or "").endswith("_w") else
                    "anchor" if (it.get("family") or "").endswith("_anchor") else "drift")
        fails = []
        if len(r["mhz"]) != 1 or r["mhz"][0] != (clocks[0] if clocks else None):
            fails.append("clock")
        if abs(r["mv"] - mv_med[r["pass"]]) > 3:
            fails.append("voltage")
        if not r["on_protocol"] or (r["target"] is not None and abs(r["start_c"] - r["target"]) > 0.5):
            fails.append("approach")
        if r["arm"] != "drift":
            if r.get("took_ms_med") is not None and r["took_ms_med"] > 60:
                fails.append("burst")
            if not r.get("ok", True) or not r.get("launches"):
                fails.append("record")
        r["fails"] = fails

    # pass gates: the drift anchor, and rule 3's per-level loss
    drift, set_aside, unresolved = {}, {}, {}
    for p in sorted({r["pass"] for r in R}):
        anc = sorted([r for r in R if r["pass"] == p and r["kind"] == "fma"], key=lambda r: r["pos"])
        drift[p] = (anc[-1]["p80"] - anc[0]["p80"]) if len(anc) >= 2 else 0.0
        if abs(drift[p]) > 0.3:
            set_aside[p] = "anchor_pi drift %.3f W" % drift[p]
        for lvl in LEVELS:
            at = [r for r in R if r["pass"] == p and r["level"] == lvl]
            if at and sum(1 for r in at if r["fails"]) > len(at) / 3.0:
                unresolved.setdefault(lvl, []).append(p)

    passes = [p for p in sorted({r["pass"] for r in R}) if p not in set_aside]
    G = [r for r in R if r["pass"] in passes and not r["fails"]]

    def item_mean(p, name, key="p80"):
        v = [r[key] for r in G if r["pass"] == p and r["item"] == name and r.get(key) is not None]
        return float(np.mean(v)) if v else None

    res_levels = {}
    for lvl in LEVELS:
        names_k = sorted([n for n, it in man.items() if it.get("level") == lvl
                          and (it.get("family") or "").endswith("_k")], key=lambda n: man[n]["k"])
        names_w = sorted([n for n, it in man.items() if it.get("level") == lvl
                          and (it.get("family") or "").endswith("_w")], key=lambda n: man[n]["w"])
        elem = man[names_k[0]]["elem_bits"] if names_k else None
        per_pass = []
        for p in passes:
            row = {"pass": p}
            for arm, names, xkey in (("k", names_k, "k"), ("w", names_w, "w")):
                xs = [man[n][xkey] for n in names if item_mean(p, n) is not None]
                ys = [item_mean(p, n) for n in names if item_mean(p, n) is not None]
                f = fit_line(xs, ys) if len(xs) >= 2 else None
                row[arm] = {"n_rungs": len(xs), "x": xs, "p80_W": ys,
                            "slope_W_per_bit": f[1] if f else None, "intercept_W": f[0] if f else None,
                            "resid_rms_W": f[2] if f else None}
                if arm == "k" and len(xs) >= 3:   # rule 2: the top rung against the line through the two lowest
                    f2 = fit_line(xs[:2], ys[:2])
                    row["saturation_W"] = ys[-1] - (f2[0] + f2[1] * xs[-1]) if f2 else None
                    row["saturation_pct"] = (100.0 * row["saturation_W"] / (f2[0] + f2[1] * xs[-1] - f2[0])
                                             if (f2 and f2[1] != 0) else None)
            ops = [r["ops_per_s"] for r in G if r["pass"] == p and r["level"] == lvl and r.get("ops_per_s")]
            byt = [r["bytes_per_s"] for r in G if r["pass"] == p and r["level"] == lvl and r.get("bytes_per_s")]
            row["ops_per_s"] = float(np.mean(ops)) if ops else None
            row["bytes_per_s"] = float(np.mean(byt)) if byt else None
            row["zeros_W"] = item_mean(p, "mf_%s_zeros" % lvl)
            row["random_W"] = item_mean(p, "mf_%s_random" % lvl)
            per_pass.append(row)

        tr = float(np.mean([r["ops_per_s"] for r in per_pass if r["ops_per_s"]])) if per_pass else None
        bps = float(np.mean([r["bytes_per_s"] for r in per_pass if r["bytes_per_s"]])) if per_pass else None

        def to_pJ(c_):
            out = {k_: ((c_[k_] / tr * 1e12) if (c_[k_] is not None and tr) else None)
                   for k_ in ("mean", "se", "lo", "hi")}
            out["n"] = c_["n"]
            return out

        sk = ci([r["k"]["slope_W_per_bit"] for r in per_pass])
        sw = ci([r["w"]["slope_W_per_bit"] for r in per_pass])
        # the small-k slope, the registered P1/P2 quantity: the two lowest rungs only
        small = []
        for r in per_pass:
            xs, ys = r["k"]["x"], r["k"]["p80_W"]
            if len(xs) >= 2 and xs[1] != xs[0]:
                small.append((ys[1] - ys[0]) / (xs[1] - xs[0]))
        ssmall = ci(small)
        sat = ci([r.get("saturation_W") for r in per_pass])
        chord = ci([(r["random_W"] - r["zeros_W"]) for r in per_pass
                    if r["random_W"] is not None and r["zeros_W"] is not None])
        e_flip, e_one, e_small = to_pJ(sk), to_pJ(sw), to_pJ(ssmall)
        # P4, as registered: "the random anchor lands within +-15 % of the ladder interpolated to the
        # random-equivalent k AND THE MATCHING W". Both arms are needed, so fit the design's own additive model
        # P = a + b.k + c.w on the two arms only (never on the anchors), then predict the anchors from it. The
        # comparison is made on the chord ABOVE the zeros anchor, not on absolute board power: 15 % of 34 W is
        # 5 W, which would pass anything, while the whole chord is ~3 W.
        p4, two_term = None, []
        rel, rel_anchor = [], []
        for p, r in zip(passes, per_pass):
            pts = []
            for n in names_k + names_w:
                y = item_mean(p, n)
                if y is not None:
                    pts.append((man[n]["k"], man[n]["w"], y))
            if len(pts) < 4 or len({q[1] for q in pts}) < 2:
                continue
            A = np.array([[1.0, q[0], q[1]] for q in pts])
            c3, *_ = np.linalg.lstsq(A, np.array([q[2] for q in pts]), rcond=None)
            row = {"pass": p, "a_W": float(c3[0]), "b_W_per_changed_bit": float(c3[1]),
                   "c_W_per_one": float(c3[2]), "n_points": len(pts)}
            kr, wr = RANDOM_K.get(elem), RANDOM_W.get(elem)
            if kr and r["zeros_W"] is not None and r["random_W"] is not None:
                pred_zero = c3[0]
                pred_rand = c3[0] + c3[1] * kr + c3[2] * wr
                obs_chord = r["random_W"] - r["zeros_W"]
                pred_chord = pred_rand - pred_zero
                row.update({"pred_chord_W": float(pred_chord), "obs_chord_W": float(obs_chord),
                            "chord_accounted_pct": float(100.0 * pred_chord / obs_chord) if obs_chord else None,
                            "zeros_residual_W": float(r["zeros_W"] - pred_zero),
                            # P4 on the REGISTERED basis (amendment 28 Oct 2026, departure D-M3): the registered
                            # wording is a percent of the random anchor itself, i.e. of absolute board power at
                            # the random-equivalent k and the matching W. Both bases are now reported.
                            "pred_random_W": float(pred_rand), "obs_random_W": float(r["random_W"]),
                            "random_anchor_pct_error": float(100.0 * (pred_rand - r["random_W"]) / r["random_W"])})
                if obs_chord:
                    rel.append(100.0 * (pred_chord - obs_chord) / obs_chord)
                rel_anchor.append(row["random_anchor_pct_error"])
            two_term.append(row)
        if rel:
            p4 = ci(rel)
        res_levels[lvl] = {
            "unit": man[names_k[0]]["unit"] if names_k else None, "elem_bits": elem,
            "transfers_per_s": tr, "bytes_per_s": bps, "per_pass": per_pass,
            "slope_W_per_bit": sk, "e_flip_pJ_per_bit": e_flip,
            "e_flip_small_k_pJ_per_bit": e_small, "slope_small_k_W_per_bit": ssmall,
            "slope_w_W_per_bit": sw, "e_one_pJ_per_bit": e_one,
            "saturation_W": sat,
            "saturation_pct_below_line": ci([r.get("saturation_pct") for r in per_pass]),
            "chord_W_random_minus_zeros": chord,
            "chord_vs_two_term_model_pct": p4, "two_term_model": two_term,
            "random_anchor_vs_two_term_model_pct": (ci(rel_anchor) if rel_anchor else None),
            # whether the k-arm is monotone in every kept pass. Where it is not, the whole-arm slope is a shape,
            # not a measured per-changed-bit coefficient (amendment 28 Oct 2026).
            "k_arm_monotone": all(all(b >= a for a, b in zip(r["k"]["p80_W"], r["k"]["p80_W"][1:]))
                                  for r in per_pass if r["k"]["p80_W"]),
            "unresolved_in_passes": unresolved.get(lvl, []),
            "pJ_per_B": {"zeros": None, "random": None},
        }
        for nm, key in (("zeros", "zeros_W"), ("random", "random_W")):
            v = [r[key] for r in per_pass if r.get(key) is not None]
            if v and bps:
                res_levels[lvl]["pJ_per_B"][nm] = float(np.mean(v)) / bps * 1e12

    P = pred["predictions"]
    l1, dr = res_levels.get("l1", {}), res_levels.get("dram", {})

    def inrange(v, lohi):
        return None if v is None else bool(lohi[0] <= v <= lohi[1])

    e_flip_dram = (dr.get("e_flip_pJ_per_bit") or {}).get("mean")
    e_one_dram = (dr.get("e_one_pJ_per_bit") or {}).get("mean")
    closure = (191.1 * e_flip_dram + 290.7 * e_one_dram) if (e_flip_dram and e_one_dram) else None
    order = [(res_levels[l] or {}).get("e_flip_pJ_per_bit", {}).get("mean") for l in LEVELS]
    mono = all(order[i] is not None and order[i + 1] is not None and order[i] < order[i + 1]
               for i in range(len(order) - 1))
    # which pairs of the ordering are actually resolved at 95 %, not merely ordered on point estimates
    resolved_pairs = {}
    for i in range(len(LEVELS)):
        for j in range(i + 1, len(LEVELS)):
            a_ = (res_levels[LEVELS[i]].get("e_flip_pJ_per_bit") or {})
            b_ = (res_levels[LEVELS[j]].get("e_flip_pJ_per_bit") or {})
            resolved_pairs["%s<%s" % (LEVELS[i], LEVELS[j])] = (
                None if (a_.get("hi") is None or b_.get("lo") is None) else bool(a_["hi"] < b_["lo"]))
    scored = {
        "P1_l1_small_k_slope_pJ_per_bit": {"registered": P["P1_l1_small_k_slope_pJ_per_bit"],
                                           "measured": (l1.get("e_flip_small_k_pJ_per_bit") or {}).get("mean"),
                                           "interval": [(l1.get("e_flip_small_k_pJ_per_bit") or {}).get("lo"),
                                                        (l1.get("e_flip_small_k_pJ_per_bit") or {}).get("hi")],
                                           "pass": inrange((l1.get("e_flip_small_k_pJ_per_bit") or {}).get("mean"),
                                                           P["P1_l1_small_k_slope_pJ_per_bit"])},
        "P2_dram_small_k_slope_pJ_per_bit": {"registered": P["P2_dram_small_k_slope_pJ_per_bit"],
                                             "measured": (dr.get("e_flip_small_k_pJ_per_bit") or {}).get("mean"),
                                             "interval": [(dr.get("e_flip_small_k_pJ_per_bit") or {}).get("lo"),
                                                          (dr.get("e_flip_small_k_pJ_per_bit") or {}).get("hi")],
                                             "pass": inrange((dr.get("e_flip_small_k_pJ_per_bit") or {}).get("mean"),
                                                             P["P2_dram_small_k_slope_pJ_per_bit"])},
        "P3_dram_saturation_percent_below_line_at_k512": {
            "registered": P["P3_dram_saturation_percent_below_line_at_k512"],
            "measured_pct": (dr.get("saturation_pct_below_line") or {}).get("mean"),
            "measured_W": (dr.get("saturation_W") or {}).get("mean"),
            "k_arm_monotone": dr.get("k_arm_monotone"),
            "pass": inrange((dr.get("saturation_pct_below_line") or {}).get("mean"),
                            P["P3_dram_saturation_percent_below_line_at_k512"]),
            "note": "not resolved rather than merely failed: the DRAM k-arm is not monotone in any kept pass, so "
                    "the top rung sits above the line through the two lowest and the registered small-k slope is "
                    "negative"},
        "P4_random_anchor_within_percent": {
            "registered": P["P4_random_anchor_within_percent"],
            "registered_basis": "a percent of the random anchor itself: 'the random anchor lands within +-15 % of "
                                "the ladder interpolated to the random-equivalent k and the matching W'",
            "rule": "the two-arm additive model P = a + b.k + c.w is fitted on the k- and w-arms only (never on "
                    "the anchors) and used to predict the random anchor. Both bases are reported: the registered "
                    "one (percent of the anchor's absolute board power) and the chord one (percent of the "
                    "zeros-to-random difference), which is the stricter test and the informative number",
            "l1_pct_error": (l1.get("chord_vs_two_term_model_pct") or {}).get("mean"),
            "l1_interval": [(l1.get("chord_vs_two_term_model_pct") or {}).get("lo"),
                            (l1.get("chord_vs_two_term_model_pct") or {}).get("hi")],
            "dram_pct_error": (dr.get("chord_vs_two_term_model_pct") or {}).get("mean"),
            "dram_interval": [(dr.get("chord_vs_two_term_model_pct") or {}).get("lo"),
                              (dr.get("chord_vs_two_term_model_pct") or {}).get("hi")],
            "l1_pct_error_anchor_basis": (l1.get("random_anchor_vs_two_term_model_pct") or {}).get("mean"),
            "l1_interval_anchor_basis": [(l1.get("random_anchor_vs_two_term_model_pct") or {}).get("lo"),
                                         (l1.get("random_anchor_vs_two_term_model_pct") or {}).get("hi")],
            "dram_pct_error_anchor_basis": (dr.get("random_anchor_vs_two_term_model_pct") or {}).get("mean"),
            "dram_interval_anchor_basis": [(dr.get("random_anchor_vs_two_term_model_pct") or {}).get("lo"),
                                           (dr.get("random_anchor_vs_two_term_model_pct") or {}).get("hi")],
            "pass_l1": None if (l1.get("chord_vs_two_term_model_pct") or {}).get("mean") is None else
            bool(abs(l1["chord_vs_two_term_model_pct"]["mean"]) <= P["P4_random_anchor_within_percent"]),
            "pass_dram": None if (dr.get("chord_vs_two_term_model_pct") or {}).get("mean") is None else
            bool(abs(dr["chord_vs_two_term_model_pct"]["mean"]) <= P["P4_random_anchor_within_percent"]),
            "pass_l1_anchor_basis": None if (l1.get("random_anchor_vs_two_term_model_pct") or {}).get("mean")
            is None else bool(abs(l1["random_anchor_vs_two_term_model_pct"]["mean"])
                              <= P["P4_random_anchor_within_percent"]),
            "pass_dram_anchor_basis": None if (dr.get("random_anchor_vs_two_term_model_pct") or {}).get("mean")
            is None else bool(abs(dr["random_anchor_vs_two_term_model_pct"]["mean"])
                              <= P["P4_random_anchor_within_percent"])},
        "P5_closure_pJ_per_line_dram": {"registered": P["P5_closure_pJ_per_line_dram"], "measured": closure,
                                        "pass": None if closure is None else
                                        bool(abs(closure - P["P5_closure_pJ_per_line_dram"]["target"])
                                             <= P["P5_closure_pJ_per_line_dram"]["tolerance"])},
        "P6_ordering": {"registered": P["P6_ordering"], "e_flip_by_level": dict(zip(LEVELS, order)),
                        "monotone": mono,
                        "span": (order[-1] / order[0]) if (order[0] and order[-1]) else None,
                        "intervals_by_level": {l_: [(res_levels[l_]["e_flip_pJ_per_bit"] or {}).get("lo"),
                                                    (res_levels[l_]["e_flip_pJ_per_bit"] or {}).get("hi")]
                                               for l_ in LEVELS},
                        # monotone on point estimates is not the same as an ordering resolved at 95 %: a pair is
                        # resolved only when the lower level's interval sits entirely below the higher one's
                        # (amendment 28 Oct 2026).
                        "resolved_pairs_at_95": resolved_pairs,
                        "pass_order_points": mono,
                        "pass_order_resolved_at_95": all(resolved_pairs.values()),
                        "pass_l1_below_rest_at_95": all(v for k_, v in resolved_pairs.items()
                                                        if k_.startswith("l1<")),
                        "pass_span": (None if not (order[0] and order[-1]) else
                                      bool(order[-1] / order[0] >= 100.0)),
                        "note": "PASS on the order only as L1 < {L2, L3, DRAM}; the upper three are unresolved at "
                                "95 % (their intervals overlap almost completely). FAIL on the span"},
        "P7_rates": {"registered": P["P7_rates"],
                     "l1_bytes_per_s": l1.get("bytes_per_s"), "dram_bytes_per_s": dr.get("bytes_per_s"),
                     # the registered DRAM band is a LINE rate; bytes_per_s counts the 32 B each load asks for,
                     # half the 64 B line the stride-64 access actually fetches (amendment 28 Oct 2026).
                     "dram_line_bytes_per_s": (2.0 * dr["bytes_per_s"]) if dr.get("bytes_per_s") else None,
                     "basis": "l1_bytes_per_s is compared directly; the DRAM band [57, 95] GB/s is the line rate, "
                              "so dram_line_bytes_per_s = 2 x dram_bytes_per_s (32 B requested per 64 B line) is "
                              "the quantity scored",
                     "took_ms_med_max": max([r.get("took_ms_med") or 0 for r in R]) if R else None,
                     "pass_l1": inrange((l1.get("bytes_per_s") or 0) / 1e12, P["P7_rates"]["l1_TB_per_s"]),
                     "pass_dram": inrange((2.0 * dr["bytes_per_s"] / 1e9) if dr.get("bytes_per_s") else None,
                                          P["P7_rates"]["dram_GB_per_s"]),
                     "pass_took_ms": bool((max([r.get("took_ms_med") or 0 for r in R]) if R else 0)
                                          <= P["P7_rates"]["took_ms_drop_above"]),
                     "pass": bool(inrange((l1.get("bytes_per_s") or 0) / 1e12, P["P7_rates"]["l1_TB_per_s"])
                                  and inrange((2.0 * dr["bytes_per_s"] / 1e9) if dr.get("bytes_per_s") else None,
                                              P["P7_rates"]["dram_GB_per_s"])
                                  and (max([r.get("took_ms_med") or 0 for r in R]) if R else 0)
                                  <= P["P7_rates"]["took_ms_drop_above"])},
    }

    res = {"exp": "E75", "card": card, "dirs": a.dirs, "passes_used": passes, "passes_set_aside": set_aside,
           "anchor_drift_W": drift, "chord_reference_pJ_per_bit": CHORD,
           "gates": {"runs": len(R), "kept": len(G), "clocks_mhz": clocks, "leak_W_per_C": k_leak,
                     "leak_runs": nk,
                     "failures": dict(sorted(((f, sum(1 for r in R if f in r["fails"]))
                                              for f in {f for r in R for f in r["fails"]}))) or {},
                     "levels_unresolved": unresolved},
           "levels": res_levels, "scored": scored}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["card", "pass", "item", "level", "arm", "k", "w", "pos", "attempt", "start_c", "t_win",
                "on_protocol", "p_raw", "p80", "rail", "mv", "ops_per_s", "bytes_per_s", "took_ms_med", "fails"]
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in sorted(R, key=lambda r: (r["pass"], r["pos"])):
                w.writerow([("|".join(r[c]) if c == "fails" else r.get(c)) for c in cols])

    print("E75 %s: %d runs, %d kept, passes %s, leak %.3f W/C" % (card, len(R), len(G), passes, k_leak))
    for lvl in LEVELS:
        L = res_levels[lvl]
        print("  %-5s e_flip %s pJ/bit (small-k %s)  e_one %s  rate %.3g B/s  unresolved %s" % (
            lvl,
            "%.4g" % L["e_flip_pJ_per_bit"]["mean"] if L["e_flip_pJ_per_bit"]["mean"] is not None else "-",
            "%.4g" % L["e_flip_small_k_pJ_per_bit"]["mean"]
            if L["e_flip_small_k_pJ_per_bit"]["mean"] is not None else "-",
            "%.4g" % L["e_one_pJ_per_bit"]["mean"] if L["e_one_pJ_per_bit"]["mean"] is not None else "-",
            L["bytes_per_s"] or 0, L["unresolved_in_passes"]))
    for k_, v in scored.items():
        print("  %-34s %s" % (k_, v.get("pass", v.get("monotone", v.get("measured_pct", "")))))


if __name__ == "__main__":
    main()
