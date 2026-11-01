#!/usr/bin/env python3
"""E99 (V3-DM) reduction: the decision rules frozen in dm/predictions.json and dm/README.md, written and tested BEFORE
the first measured pass (selftest_dm.py: E81's committed passes relabelled, a pipeline test that means nothing).

    python3 tools/claims-v3/dm/reduce_dm.py <pass dir> [...] --gen <make_dm.py dir> --pred tools/claims-v3/dm/predictions.json
        --out dm.json [--csv runs.csv] [--leak auto|<W per C>]

E81's estimator and gates, unchanged (reduce_hl.runs_of_pass, reduce_mf.ec_fields, reduce_mf.took_ms_window, the same run
and pass gates, the warm-up rule). What is new is the contrast list, which may hold more than two items, the rail read
the way E81's post-hoc view read it (within-pass differences of the raw minion-rail power, no leakage correction), and
the registered rules R1-R13 at the end. Primary arm: the passes with the board meter's dip samples removed by E82 A2's
definition (dp/posthoc_dips.py, registered here, before any data); the same reducer on the unfiltered passes is reported
beside it.
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
sys.path.insert(0, os.path.join(HERE, "..", "dp"))
from reduce_hl import leak_slope, load_jsonl, runs_of_pass  # noqa: E402
from reduce_mf import ci, ec_fields, took_ms_window  # noqa: E402
from reduce_dp import classify  # noqa: E402

CONTRASTS = {
    # the session's tie to E81 (its dp.json headline: 1.636, 1.866, 3.501, 2.046 W)
    "tie_total": ({"dp_bern": 1, "dp_c2": -1}, "E81's whole step: random bits over its two-value image"),
    "tie_c2": ({"dp_c2": 1, "dp_zeros": -1}, "E81's two-value image over zeros"),
    "tie_bern": ({"dp_bern": 1, "dp_zeros": -1}, "E81's random bits over zeros"),
    "tie_c1": ({"dp_c1": 1, "dp_zeros": -1}, "E75's k0 image over zeros"),
    # the same ones, different pins driven high
    "hi_t0": ({"dm_u4": 1, "dm_l08": -1}, "w 256, no toggles, no line change: high 256 against 32"),
    "hi_ta": ({"dm_a35": 1, "dm_a08": -1}, "w 256, raw toggles 496 and encoded toggles 62 on both: high 224 against 32"),
    "hi_ta26": ({"dm_a26": 1, "dm_a08": -1}, "the same at high 160 against 32"),
    "hi_r": ({"dm_r44": 1, "dm_r08": -1}, "random bytes, w 256, k 256, half 128, raw 248: high 256 against 32 (encoded 248 against 31)"),
    "hi_r26": ({"dm_r26": 1, "dm_r08": -1}, "the same at high 160 against 32 (encoded 224.5 against 31)"),
    # toggles
    "t_enc": ({"dm_a44": 1, "dm_a35": -1}, "w 256, raw 496 on both: encoded toggles +434, high +32"),
    "t_raw": ({"dm_a08": 1, "dm_l08": -1}, "w 256, high 32 on both: raw toggles +496, encoded +62 (the DMI pin)"),
    "t_both": ({"dm_a44": 1, "dm_u4": -1}, "w 256, high 256 on both: raw and encoded toggles +496"),
    # the tent: the same pins driven high, different raw ones
    "tie27": ({"dm_u7": 1, "dm_u2": -1}, "128 high on both, no toggles: 448 ones against 128"),
    "tie45": ({"dm_u5": 1, "dm_u4": -1}, "256 high on both, no toggles: 320 ones against 256 (the rule's tie)"),
    "tie18": ({"dm_u8": 1, "dm_u1": -1}, "64 high on both, no toggles: 512 ones against 64"),
    "tent_S": ({"dm_u4": 1, "dm_u2": -1, "dm_u7": -1, "dm_u5": 1},
               "(u4 - u2) - (u7 - u5): two steps of +128 ones, one going up the tent, one down it; free of a linear price of ones"),
    "kink": ({"dm_u4": 1.5, "dm_u2": -0.5, "dm_u5": -1}, "(u4 - u2)/2 - (u5 - u4): the step per 64 ones below the tie, less the step across it"),
    "ones_u8": ({"dm_u8": 1, "dp_zeros": -1}, "all 0xFF over zeros: 512 raw ones, every data pin low, 64 DMI highs"),
    # half, floor
    "half": ({"dp_c1": 1, "dm_l08": -1}, "w 256, high 32: the line's 32 B halves differ in 256 bits against 0 (encoded toggles 2 against 0)"),
    "floor_w1": ({"dm_w1": 1, "dp_zeros": -1}, "one bit in every line over zeros"),
    "u1_over_w1": ({"dm_u1": 1, "dm_w1": -1}, "64 ones and 64 high against one"),
    # the arrangement again, on the session's own images
    "arr_L2": ({"dm_L2": 1, "dp_c2": -1}, "E81's arrangement: scattered 2-cycle over the two-value image (E81 dp_s2 - dp_c2 +0.996)"),
    "r08_vs_c2": ({"dm_r08": 1, "dp_c2": -1}, "whole bytes in random places, against whole bytes in runs: the same high pins, raw toggles 248 against 40"),
    "L2_vs_r08": ({"dm_L2": 1, "dm_r08": -1}, "scattered bits against scattered whole bytes: high 211 against 32"),
    # the period ladder
    "h1": ({"dm_L2": 1, "dm_L1": -1}, "period 2 against period 1 (k 256 against 0)"),
    "h3": ({"dm_L3": 1, "dm_L2": -1}, "period 3 over period 2: each channel sees 3 values"),
    "h4": ({"dm_L4": 1, "dm_L2": -1}, "period 4 over period 2: each channel sees 1"),
    "h8": ({"dm_L8": 1, "dm_L2": -1}, "period 8 over period 2: each channel sees 1"),
    "h16": ({"dm_L16": 1, "dm_L2": -1}, "period 16 over period 2: each channel sees 1, each 8-way path 2"),
    "h17": ({"dm_L17": 1, "dm_L2": -1}, "period 17 over period 2: each channel sees 17"),
    "h32": ({"dm_L32": 1, "dm_L2": -1}, "period 32 over period 2: each channel sees 2, each 128-way path 1"),
    "h256": ({"dm_L256": 1, "dm_L2": -1}, "period 256 over period 2: each channel sees 16, each 128-way path 2"),
    "D": ({"dm_L8192": 1, "dm_L2": -1}, "8,192 lines over period 2, the same byte distribution: E81's period (dp_bern - dp_s2 +0.640)"),
    "bern_vs_L8192": ({"dp_bern": 1, "dm_L8192": -1}, "E81's random bits against the fixed-distribution 8,192 lines"),
}


def value(row, spec):
    out = 0.0
    for it, c in spec.items():
        v = row.get(it)
        if v is None:
            return None
        out += c * v
    return out


def band_verdict(cls, mean, band):
    """PASS: present and inside the band. FAIL: absent. UNRESOLVED otherwise (an effect of another size stays visible)."""
    if mean is None:
        return "UNRESOLVED"
    if cls == "absent":
        return "FAIL"
    if cls == "present" and band[0] <= mean <= band[1]:
        return "PASS"
    return "UNRESOLVED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    ap.add_argument("--warmup", type=int, default=None)
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    D_ = pred["decision"]
    warmup = a.warmup if a.warmup is not None else D_["warmup_pass"]
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}

    R, card = [], None
    for d in a.dirs:
        rr, c = runs_of_pass(d, man)
        card = card or c
        ec = ec_fields(d)
        for r in rr:
            r.update(ec.get((r["pass"], r["item"], r["pos"], r["attempt"]), {}))
        by = {}
        for x in load_jsonl(os.path.join(d, "runs.jsonl")):
            key = (x["block"], x["item"], x.get("pos", 0), x.get("attempt", 1))
            by[key] = min(by.get(key, x["t_start_ms"]), x["t_start_ms"])
        for r in rr:
            r["_t0_ms"] = by.get((r["pass"], r["item"], r["pos"], r["attempt"]))
        took_ms_window(d, rr)
        R += rr
    if not R:
        raise SystemExit("no runs: is telemetry.jsonl(.gz) in the pass directories?")

    k_leak, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
    clocks = sorted({m for r in R for m in r["mhz"]})
    mv_med = {p: float(np.median([r["mv"] for r in R if r["pass"] == p])) for p in {r["pass"] for r in R}}
    for r in R:
        it = man.get(r["item"], {})
        r["p80"] = r["p_raw"] - k_leak * (r["t_win"] - r["start_c"])
        r["k"], r["w"] = it.get("k"), it.get("w")
        r["arm"] = "drift" if r["kind"] == "fma" else "dram"
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

    all_passes = sorted({r["pass"] for r in R})
    drift, set_aside = {}, {}
    for p in all_passes:
        anc = sorted([r for r in R if r["pass"] == p and r["kind"] == "fma"], key=lambda r: r["pos"])
        drift[p] = (anc[-1]["p80"] - anc[0]["p80"]) if len(anc) >= 2 else None
        if drift[p] is not None and abs(drift[p]) > 0.3:
            set_aside[p] = "anchor_pi drift %.3f W" % drift[p]
        at = [r for r in R if r["pass"] == p and r["arm"] == "dram"]
        nf = sum(1 for r in at if r["fails"])
        if at and nf > len(at) / 3.0:
            set_aside[p] = set_aside.get(p, "") + ("; " if p in set_aside else "") + \
                "%d of %d DRAM runs fail a gate" % (nf, len(at))
    healthy = [p for p in all_passes if p not in set_aside]
    headline = [p for p in healthy if p != warmup]
    G = [r for r in R if r["pass"] in healthy and not r["fails"]]

    def item_of(p, name, field):
        v = [r[field] for r in G if r["pass"] == p and r["item"] == name and r.get(field) is not None]
        return float(np.mean(v)) if v else None

    names = [n for n, it in man.items() if it["kind"] == "cmd"]
    per_pass = {}
    for p in healthy:
        board = {n: item_of(p, n, "p80") for n in names}
        rail = {n: item_of(p, n, "rail") for n in names}
        rate = [r["ops_per_s"] for r in G if r["pass"] == p and r["arm"] == "dram" and r.get("ops_per_s")]
        per_pass[p] = {"items_W": board, "rail_W": rail, "lines_per_s": float(np.mean(rate)) if rate else None,
                       "drift_W": drift.get(p),
                       "contrasts_W": {cn: value(board, s) for cn, (s, _) in CONTRASTS.items()},
                       "rail_contrasts_W": {cn: value(rail, s) for cn, (s, _) in CONTRASTS.items()}}

    def present(values):
        return [v for v in values if v is not None]

    def summarize(passes):
        out = {"passes": passes}
        lps = [per_pass[p]["lines_per_s"] for p in passes if per_pass[p]["lines_per_s"]]
        lr = float(np.mean(lps)) if lps else None
        out["lines_per_s"] = lr
        out["line_rate_by_item"] = {}
        for n in names:
            v = [r["ops_per_s"] for r in G if r["pass"] in passes and r["item"] == n and r.get("ops_per_s")]
            out["line_rate_by_item"][n] = float(np.mean(v)) if v else None
        out["items_W"] = {n: ci(present([per_pass[p]["items_W"][n] for p in passes])) for n in names}
        out["items_over_zeros_W"] = {}
        out["rail_over_zeros_W"] = {}
        for n in names:
            for key, fld in (("items_over_zeros_W", "items_W"), ("rail_over_zeros_W", "rail_W")):
                out[key][n] = ci([per_pass[p][fld][n] - per_pass[p][fld]["dp_zeros"] for p in passes
                                  if per_pass[p][fld].get(n) is not None and per_pass[p][fld].get("dp_zeros") is not None])
        out["contrasts_W"] = {}
        out["rail_contrasts_W"] = {}
        out["contrasts_pJ_per_line"] = {}
        for cn, (s, what) in CONTRASTS.items():
            c = ci(present([per_pass[p]["contrasts_W"][cn] for p in passes]))
            c["what"], c["items"] = what, s
            out["contrasts_W"][cn] = c
            out["rail_contrasts_W"][cn] = ci(present([per_pass[p]["rail_contrasts_W"][cn] for p in passes]))
            out["contrasts_pJ_per_line"][cn] = {k: ((c[k] / lr * 1e12) if (c.get(k) is not None and lr) else None)
                                                for k in ("mean", "se", "lo", "hi")}
        return out

    head = summarize(headline)
    every = summarize(healthy)
    C, CR = head["contrasts_W"], head["rail_contrasts_W"]
    pm, ah = D_["present_min_W"], D_["absent_half_W"]
    cls = {cn: classify(C[cn], pm, ah) for cn in C}
    enough = len(headline) >= D_["min_headline_passes"]
    if not enough:
        cls = {cn: "unresolved" for cn in C}
    B = pred["bands"]
    m = lambda cn: C[cn]["mean"]

    def in_band(cn, lohi):
        return None if m(cn) is None else bool(lohi[0] <= m(cn) <= lohi[1])

    V = {}
    # R1, the session tie
    V["R1_session_tie"] = {cn: {"E81_W": B["tie"][cn]["e81"], "mean_W": m(cn),
                                "verdict": ("UNRESOLVED" if m(cn) is None else
                                            "PASS" if abs(m(cn) - B["tie"][cn]["e81"]) <= B["tie"][cn]["within"] else "FAIL")}
                           for cn in B["tie"]}
    # R2, R3, R4: the same ones or a price-free step, different high pins
    for key, cn in (("R2_hi_no_toggles", "hi_t0"), ("R3_hi_same_toggles", "hi_ta"), ("R4_tent", "tent_S")):
        V[key] = {"contrast": cn, "mean_W": m(cn), "interval_W": [C[cn]["lo"], C[cn]["hi"]], "class": cls[cn],
                  "band_W": B[cn], "verdict": band_verdict(cls[cn], m(cn), B[cn])}
    # R5: whole bytes in random places behave as runs do, because their high pins are the same
    v5 = "UNRESOLVED"
    if cls["L2_vs_r08"] == "absent" or cls["r08_vs_c2"] == "present":
        v5 = "FAIL"
    if cls["r08_vs_c2"] == "absent" and cls["L2_vs_r08"] == "present":
        v5 = "PASS"
    V["R5_whole_byte_scatter"] = {"r08_vs_c2": {"mean_W": m("r08_vs_c2"), "interval_W": [C["r08_vs_c2"]["lo"], C["r08_vs_c2"]["hi"]],
                                                "class": cls["r08_vs_c2"]},
                                  "L2_vs_r08": {"mean_W": m("L2_vs_r08"), "interval_W": [C["L2_vs_r08"]["lo"], C["L2_vs_r08"]["hi"]],
                                                "class": cls["L2_vs_r08"]}, "verdict": v5}
    # R6: the same pins driven high, different ones
    pure = [cls[c] == "absent" for c in ("tie27", "tie18")]
    paid = [cls[c] == "present" for c in ("tie27", "tie18")]
    V["R6_ties"] = {"contrasts": {c: {"mean_W": m(c), "interval_W": [C[c]["lo"], C[c]["hi"]], "class": cls[c],
                                      "pJ_per_one": ((C[c]["mean"] / head["lines_per_s"] * 1e12 / B["tie_ones"][c])
                                                     if (m(c) is not None and head["lines_per_s"]) else None)}
                                  for c in ("tie27", "tie45", "tie18")},
                    "verdict": "pure DBI: ones cost nothing beyond the high pins" if all(pure) else
                               "ones cost beyond the pins, at the price above" if all(paid) else "UNRESOLVED"}
    # R7, R8: toggles. The registered expectation is that neither pays much: absent is PASS, present is FAIL.
    for key, cn in (("R7_encoded_toggles", "t_enc"), ("R8_raw_toggles", "t_raw")):
        V[key] = {"contrast": cn, "mean_W": m(cn), "interval_W": [C[cn]["lo"], C[cn]["hi"]], "class": cls[cn],
                  "verdict": {"absent": "PASS", "present": "FAIL"}.get(cls[cn], "UNRESOLVED")}
    # R9, R10: two-way, no expectation to pass or fail: what is measured is the answer
    V["R9_half"] = {"contrast": "half", "mean_W": m("half"), "interval_W": [C["half"]["lo"], C["half"]["hi"]], "class": cls["half"]}
    V["R10_floor"] = {"contrast": "floor_w1", "mean_W": m("floor_w1"), "interval_W": [C["floor_w1"]["lo"], C["floor_w1"]["hi"]],
                      "class": cls["floor_w1"]}
    # R11: the period ladder
    frac = {h: (m(h) / m("D")) if (m(h) is not None and m("D")) else None for h in ("h3", "h4", "h8", "h16", "h17", "h32", "h256")}
    v11 = "UNRESOLVED"
    reading = []
    if enough:
        flat = all(cls[h] == "absent" for h in ("h4", "h8", "h16"))
        steps = cls["h3"] == "present" and cls["h17"] == "present"
        h32ok = frac["h32"] is not None and B["h32_fraction"][0] <= frac["h32"] <= B["h32_fraction"][1]
        if cls["D"] == "present" and flat and steps and h32ok:
            v11 = "PASS"
        if cls["h8"] == "present" or cls["h16"] == "present" or cls["h3"] == "absent" or cls["h17"] == "absent":
            v11 = "FAIL"
        if cls["h16"] == "present" and cls["h8"] == "absent":
            reading.append("period 16 costs and period 8 does not: a path of the 8-way interleave pays")
        if cls["h32"] == "absent" and cls["h256"] == "present":
            reading.append("period 32 is free and period 256 is not: a path of about the 128-way (bank) interleave pays")
        if cls["h32"] == "absent" and cls["h256"] == "absent" and steps:
            reading.append("powers of two up to 256 are free and periods 3 and 17 are not: a path much deeper than the channels pays")
    V["R11_period_ladder"] = {"classes": {h: cls[h] for h in ("h1", "h3", "h4", "h8", "h16", "h17", "h32", "h256", "D")},
                              "fractions_of_D": frac, "verdict": v11, "reading": reading}
    # R12: closure, from the structured images' prices to the arrangement on random lines
    if all(m(c) is not None for c in ("hi_ta", "t_enc", "t_raw", "arr_L2")) and head["lines_per_s"]:
        p_h = m("hi_ta") / 192.0
        p_te = (m("t_enc") - 32 * p_h) / 434.0
        p_tr = (m("t_raw") - 62 * p_te) / 496.0
        pred_arr = 179 * p_h + 253 * p_te + 208 * p_tr
        lr = head["lines_per_s"]
        V["R12_closure"] = {"price_per_high_pin_pJ": p_h / lr * 1e12, "price_per_encoded_toggle_pJ": p_te / lr * 1e12,
                            "price_per_raw_toggle_pJ": p_tr / lr * 1e12, "predicted_arr_L2_W": pred_arr, "measured_arr_L2_W": m("arr_L2"),
                            "parts_W": {"high": 179 * p_h, "encoded": 253 * p_te, "raw": 208 * p_tr},
                            "verdict": "PASS" if abs(pred_arr - m("arr_L2")) <= B["closure_within_W"] else "FAIL"}
    else:
        V["R12_closure"] = {"verdict": "UNRESOLVED"}
    # R13: the compute rail
    r13 = {}
    for cn in ("hi_t0", "hi_ta", "D", "tie_total"):
        r13[cn] = {"rail_mean_W": CR[cn]["mean"], "rail_interval_W": [CR[cn]["lo"], CR[cn]["hi"]], "board_mean_W": m(cn),
                   "verdict": "UNRESOLVED" if CR[cn]["mean"] is None else
                   ("PASS" if abs(CR[cn]["mean"]) <= B["rail_within_W"] else "FAIL")}
    V["R13_rail"] = r13
    # the overall reading of the firmware's read DBI as the arrangement's mechanism
    a4 = [V[k]["verdict"] for k in ("R2_hi_no_toggles", "R3_hi_same_toggles", "R4_tent", "R5_whole_byte_scatter")]
    overall = "CONFIRMED" if all(x == "PASS" for x in a4) else \
        "REFUTED" if (V["R2_hi_no_toggles"]["verdict"] == "FAIL" and V["R3_hi_same_toggles"]["verdict"] == "FAIL") else "PARTIAL"
    if not enough:
        overall = "UNRESOLVED"
    V["overall_dbi"] = overall

    res = {"exp": "E99", "card": card, "dirs": a.dirs, "warmup_pass": warmup, "passes_all": all_passes,
           "passes_healthy": healthy, "passes_headline": headline, "passes_set_aside": set_aside,
           "anchor_drift_W": drift,
           "gates": {"runs": len(R), "kept": len(G), "clocks_mhz": clocks, "leak_W_per_C": k_leak, "leak_runs": nk,
                     "failures": dict(sorted(((f, sum(1 for r in R if f in r["fails"]))
                                              for f in {f for r in R for f in r["fails"]}))) or {},
                     "took_ms_med_max": max([r.get("took_ms_med") or 0 for r in R])},
           "headline": head, "with_warmup": every, "classes": cls, "verdicts": V, "per_pass": per_pass}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["card", "pass", "item", "arm", "k", "w", "pos", "attempt", "start_c", "t_win", "on_protocol",
                "p_raw", "p80", "rail", "mv", "ops_per_s", "bytes_per_s", "took_ms_med", "fails"]
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in sorted(R, key=lambda r: (r["pass"], r["pos"])):
                w.writerow([("|".join(r[c]) if c == "fails" else r.get(c)) for c in cols])

    print("E99 %s: %d runs, %d kept, healthy %s, headline %s, set aside %s, leak %.4f W/C (%d runs)"
          % (card, len(R), len(G), healthy, headline, set_aside, k_leak, nk))
    for cn, c in C.items():
        if c["mean"] is not None:
            print("  %-14s %+.3f W [%s, %s] n=%d  %-10s rail %+.3f" % (
                cn, c["mean"], "%+.3f" % c["lo"] if c["lo"] is not None else "n/a",
                "%+.3f" % c["hi"] if c["hi"] is not None else "n/a", c["n"], cls[cn],
                CR[cn]["mean"] if CR[cn]["mean"] is not None else float("nan")))
    for k_ in V:
        v = V[k_]
        if isinstance(v, str):
            txt = v
        elif "verdict" in v:
            txt = v["verdict"]
        elif "class" in v:
            txt = v["class"]
        else:
            txt = json.dumps({x: y.get("verdict") for x, y in v.items()})
        print("  %-24s %s" % (k_, txt))


if __name__ == "__main__":
    main()
