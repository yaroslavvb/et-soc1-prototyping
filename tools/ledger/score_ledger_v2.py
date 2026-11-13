#!/usr/bin/env python3
"""Score the load ledger v2's frozen predictions against the committed measurements (Q166, step 1).

Run only after docs/reports/data/2026-11-12-q166-ledger-v2/predictions-v2.json is committed with its SHA256SUMS-freeze
(it refuses otherwise). It never recomputes a frozen prediction. It writes scores-v2.json and chart-data-v2.json beside
it; chart_ledger_v2.py draws the chart from the second. The dated corrections of fix-q166 (Thu 12 Nov 2026), every one
post hoc, come from posthoc_ledger_v2.py's compute() and sit beside the frozen scores, never in place of them.

Scores, each labelled as it truly is:
  E39, E59        held out, not blind (measured in September; known before the freeze), beside v1's committed scores
  E37             held out, not blind, but its forecast depends on the awake rule, which was set during the build after
                  arithmetic beside E101's DRAM arm (the same benchmark streaming from DRAM): post hoc for that rule
  E101            beside: the 7 loop cells held out by price; the 2 DRAM-arm cells (mmp64) POST HOC for the awake rule;
                  the L2-streamed cells IN SAMPLE
  E136            beside: random minus zeros at 800 MHz, held out, not blind, differences only; a dated correction for
                  the L3 row (its share of the difference was not zero, as the frozen label said)
  E86, E95        beside: M10 held out by kind (M10 was fitted on their rows), each session's own anchors

    python3 -I -B tools/ledger/score_ledger_v2.py

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import posthoc_ledger_v2 as PH  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
D = os.path.join(REPO, "docs", "reports", "data", "2026-11-12-q166-ledger-v2")
DV3 = "docs/reports/data/2026-09-25-claims-v3/results"
SP = "workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy"
LM = "docs/reports/data/2026-10-26-load-model"


def rd(rel):
    return json.load(open(os.path.join(REPO, rel)))


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def check_freeze():
    lines = open(os.path.join(D, "SHA256SUMS-freeze")).read().split("\n")
    bad = []
    for ln in lines:
        if not ln.strip():
            continue
        h, p = ln.split(None, 1)
        if hashlib.sha256(open(os.path.join(REPO, p.strip()), "rb").read()).hexdigest() != h:
            bad.append(p)
    if bad:
        sys.exit("refused: frozen files differ from SHA256SUMS-freeze: " + ", ".join(bad))
    return [ln for ln in lines if ln.strip()]


def row(load, name, quantity, unit, measured, msrc, forecast, band, label, v1=None, seconds="given", extra=None):
    err = forecast - measured
    r = {"load": load, "name": name, "quantity": quantity, "unit": unit, "seconds": seconds,
         "measured": measured, "measured_source": msrc, "forecast": forecast, "forecast_band": band,
         "error": err, "error_pct": 100.0 * err / measured if measured else None,
         "inside_band": (band[0] <= measured <= band[1]) if band else None, "label": label}
    if v1 is not None:
        r["v1_forecast"] = v1
        r["v1_error"] = v1 - measured
        r["v1_error_pct"] = 100.0 * (v1 - measured) / measured if measured else None
    if extra:
        r.update(extra)
    return r


AWAKE_NOTE = ("its forecast depends on the awake rule (a hart's time priced once), which was set during the build after "
              "arithmetic that put v2 beside E101's DRAM arm, the same benchmark streaming from DRAM: post hoc for that rule")


def main():
    sums = check_freeze()
    P = json.load(open(os.path.join(D, "predictions-v2.json")))
    ph = PH.compute()
    no_rule = ph["awake_rule_e37"]["per_card"]
    v1 = rd(f"{LM}/scores.json")["loads"]
    by = {}
    for ld in P["loads"]:
        by.setdefault(ld["load"], []).append(ld)
    rows = []

    # ---------------- E39: three slopes and three intercepts (v1's six independent predictions)
    ab = rd(f"{DV3}/ablb.json")
    meas39 = {"line": {}, "ends": {}}
    for it in ab:
        pc = it.get("per_card", {})
        if it.get("item") == "ABLB-3c":
            for card, v in pc.items():
                f = v.get("fit_on_block_means") or v.get("vs_aifoundry2_values", {}).get("fit_on_block_means")
                s = v.get("slope") or v.get("vs_aifoundry2_values", {}).get("slope")
                meas39["line"][card] = {"slope": s["mean"], "slope_ci99": [s["lo"], s["hi"]], "intercept": f["intercept"]}
        if it.get("item") == "ABLB-3ab":
            for card, v in pc.items():
                d = v.get("dense_W") or v.get("vs_aifoundry2_values", {}).get("dense_W")
                z = v.get("zero_W") or v.get("vs_aifoundry2_values", {}).get("zero_W")
                if d and z:
                    meas39["ends"][card] = {"dense": d["mean"], "zero": z["mean"]}
    v1_39 = {r["card"]: r for r in v1["E39_gemv_sparsity_ladder"]["rows"]}
    e39_err, e39_err_v1, e39_ends = [], [], []
    for ld in by["E39"]:
        card = ld["name"].split(", ")[-1]
        pr = ld["predicted"]["line_w_over_idle_with_heat"]
        m = meas39["line"][card]
        src = f"{DV3}/ablb.json ABLB-3c per_card.{card}"
        lab = "held out, not blind"
        rows.append(row("E39", f"slope, {card}", "W over idle per unit of useful-slot fraction", "W", m["slope"], src,
                        pr["slope_w"], pr["slope_band_w"], lab, v1=v1_39[card]["predicted_slope_w"],
                        extra={"measured_ci99": m["slope_ci99"],
                               "inside_measured_ci99": m["slope_ci99"][0] <= pr["slope_w"] <= m["slope_ci99"][1]}))
        rows.append(row("E39", f"intercept, {card}", "W over idle at zero useful slots", "W", m["intercept"], src,
                        pr["intercept_w"], pr["intercept_band_w"], lab, v1=v1_39[card]["predicted_intercept_w"]))
        e39_err += [pr["slope_w"] - m["slope"], pr["intercept_w"] - m["intercept"]]
        e39_err_v1 += [v1_39[card]["predicted_slope_w"] - m["slope"], v1_39[card]["predicted_intercept_w"] - m["intercept"]]
        e = meas39["ends"].get(card)
        if e:
            dense = ld["predicted"]["fma-dense"]["w_over_idle_with_heat"]
            zero = ld["predicted"]["fma-zero"]["w_over_idle_with_heat"]
            e39_ends += [dense - e["dense"], zero - e["zero"]]

    # ---------------- E37: W over idle with the run's heating, and J per op, given and forecast seconds
    mm = rd(f"{DV3}/mmb.json")["items"]
    meas37 = {}
    for it in mm:
        if it.get("item") == "MMB-c":
            for card, v in it["per_card"].items():
                d = v["fp32-tensor-DRAM"]
                meas37[card] = {"w": d["mean"], "ci99": d["ci99"], "idle_before_w": d["idle_before_w"]}
    v1_37 = {r["card"]: r for r in v1["E37_mmbench_fp32_from_DRAM"]["rows"]}
    e37 = {"given": [], "forecast": [], "v1": []}
    e37_j = {"given": [], "forecast": [], "total_given": [], "total_forecast": []}
    for ld in by["E37"]:
        card = ld["variants"]["given_seconds"]["card"]
        m = meas37[card]
        c_meas = ld["inputs"]["cycles_per_op_measured"]
        ops_meas = 1024 * 600e6 / c_meas
        src = f"{DV3}/mmb.json MMB-c per_card.{card}['fp32-tensor-DRAM'].mean"
        for which in ("given", "forecast"):
            pr = ld["predicted"][f"{which}_seconds"]
            ops_f = pr["inputs_echo"]["work_units"]
            w = pr["w_over_idle_with_heat"]
            nr = no_rule[card][f"{which}_no_rule"]
            lab37 = (f"held out, not blind; {AWAKE_NOTE}; without the rule it reads {nr['w_error_pct']:+.1f}% "
                     f"(posthoc-v2.json awake_rule_e37)")
            rows.append(row("E37", f"{card}", "W over the pre-launch idle", "W", m["w"], src, w,
                            pr["w_over_idle_with_heat_band"], lab37,
                            v1=v1_37[card]["predicted_over_idle_w"] if which == "given" else None,
                            seconds=which, extra={"measured_ci99": m["ci99"], "label_frozen": "held out, not blind",
                                                  "without_awake_rule_w": nr["w_over_idle_with_heat"]}))
            e37[which].append(w - m["w"])
            jm = m["w"] / ops_meas
            jf = w / ops_f
            e37_j[which].append(100 * (jf - jm) / jm)
            jtm = (m["idle_before_w"] + m["w"]) / ops_meas
            jtf = (pr["rest"]["w"] + w) / ops_f
            e37_j[f"total_{which}"].append(100 * (jtf - jtm) / jtm)
            rows.append(row("E37", f"{card}, J an op", "J over idle per op", "nJ", jm * 1e9, src + " / measured rate",
                            jf * 1e9, [x / ops_f * 1e9 for x in pr["w_over_idle_with_heat_band"]],
                            f"held out, not blind; {AWAKE_NOTE}; without the rule it reads "
                            f"{nr['j_per_op_error_pct']:+.1f}% an op (posthoc-v2.json awake_rule_e37)", seconds=which,
                            extra={"j_total_measured_nj": jtm * 1e9, "j_total_forecast_nj": jtf * 1e9,
                                   "rest_w_forecast": pr["rest"]["w"], "rest_w_measured": m["idle_before_w"],
                                   "label_frozen": "held out, not blind",
                                   "j_total_error_pct_posthoc_t0_at_die_start":
                                       ph["e37_die_start"][f"j_total_per_op_error_pct_{which}"][card]}))
        e37["v1"].append(v1_37[card]["predicted_over_idle_w"] - m["w"])

    # ---------------- E59: W over idle (leak-corrected) and J a solve, given and forecast seconds; the total too
    names = {"L1 (512,4,0.3,448)": "aifoundry3-1136-l1", "L2 (512,4,0.4,1850)": "aifoundry3-1136-l2",
             "(256,5,0.4,1925) first half": "aifoundry3-1136-f5h0",
             "(256,5,0.4,1925) second half": "aifoundry3-1136-f5h1"}
    v1_59 = {r["size"]: r for r in v1["E59_sparse_parity"]["rows"]}
    e59 = {"w_given": [], "w_v1": [], "j_given": [], "j_forecast": [], "jt_given": [], "jt_forecast": []}
    for ld in by["E59"]:
        en = rd(f"{SP}/{names[ld['name']]}/energy.json")
        mw = en["board"]["catalogue"]["over_idle_w"]
        mj = en["board"]["j_per_solve"]
        mjt = en["board"]["j_per_solve_total"]
        src = f"{SP}/{names[ld['name']]}/energy.json board"
        g = ld["predicted"]["given_seconds"]
        f = ld["predicted"]["forecast_seconds"]
        rows.append(row("E59", ld["name"], "W over idle, leak-corrected", "W", mw, src + ".catalogue.over_idle_w",
                        g["w_over_idle"], g["w_over_idle_band"], "held out, not blind",
                        v1=v1_59[ld["name"]]["predicted_over_idle_w"]))
        e59["w_given"].append(g["w_over_idle"] - mw)
        e59["w_v1"].append(v1_59[ld["name"]]["predicted_over_idle_w"] - mw)
        for which, pr in (("given", g), ("forecast", f)):
            pu = pr["per_unit"]
            rows.append(row("E59", ld["name"], "J a solve over idle", "J", mj, src + ".j_per_solve",
                            pu["j_over_idle"], pu["j_over_idle_band"], "held out, not blind", seconds=which,
                            v1=v1_59[ld["name"]]["predicted_j_per_solve_over_idle"] if which == "given" else None))
            rows.append(row("E59", ld["name"], "J a solve with the card at rest", "J", mjt, src + ".j_per_solve_total",
                            pu["j_total"], pu["j_total_band"], "held out, not blind", seconds=which))
            e59[f"j_{which}"].append(100 * (pu["j_over_idle"] - mj) / mj)
            e59[f"jt_{which}"].append(100 * (pu["j_total"] - mjt) / mjt)

    # ---------------- E101: S per cell
    e101 = rd("docs/reports/data/2026-11-01-e101-real-matmul/e101.json")["items"]
    e101_err = {"loop": [], "dram post hoc": [], "in sample": [], "first nine": []}
    for ld in by["E101"]:
        it = e101[ld["item"]]
        pr = ld["predicted"]["given_seconds"]
        ins = ld["label"].startswith("in sample")   # the L2-streamed cells
        dram = ld["name"].startswith("mmp64")       # the DRAM arm: post hoc for the awake rule (fix-q166)
        lab, extra = ld["label"], {"measured_ci95": it["S"]["ci95"]}
        if dram:
            d = ph["awake_rule_e101_dram"]["cells"][ld["name"]]
            lab = ("post hoc for the awake rule (set during the build after arithmetic that put v2 beside this arm); "
                   f"without the rule {d['without_rule_error_pct']:+.1f}%; the catalogue's DRAM row held out "
                   "(posthoc-v2.json awake_rule_e101_dram)")
            extra.update(label_frozen=ld["label"], without_awake_rule_w=d["without_rule_w"])
        rows.append(row("E101", ld["name"], "S, W over idle", "W", it["S"]["mean"],
                        f"docs/reports/data/2026-11-01-e101-real-matmul/e101.json items.{ld['item']}.S",
                        pr["w_over_idle"], pr["w_over_idle_band"], lab, extra=extra))
        e = 100 * (pr["w_over_idle"] - it["S"]["mean"]) / it["S"]["mean"]
        e101_err["in sample" if ins else ("dram post hoc" if dram else "loop")].append(e)
        if not ins:
            e101_err["first nine"].append(e)

    # ---------------- E136: random minus zeros at 800 MHz
    cells = rd("docs/reports/data/2026-11-02-e136-large-gemm/results.json")["cells"]
    e136_err = []
    for ld in by["E136"]:
        fmt = ld["name"].split()[1].rstrip(",")
        rk = "full" if fmt == "int8" else "randn"
        mr = cells[f"g4k-{fmt}-{rk}"]["burst_p800_w_runs"][0]
        mz = cells[f"g4k-{fmt}-zeros"]["burst_p800_w_runs"][0]
        pr = ld["predicted"]
        cor = ph["e136_l3_correction"]["per_format"][fmt]
        lab = ("held out, not blind; differences only; aifoundry2's D carried from aifoundry3 by E38's card scale. "
               "DATED CORRECTION (fix-q166, Thu 12 Nov 2026, post hoc): the frozen label said the L3 row's share of "
               f"the difference is zero by construction; it is {cor['l3_share_w']:+.3f} W (its zeros column is "
               "aifoundry3's 13.5 pJ/B, its random column aifoundry2's 12.3); without it the forecast reads "
               f"{cor['corrected_w']:.3f} W, {cor['corrected_error_pct']:+.1f}% (posthoc-v2.json e136_l3_correction)")
        rows.append(row("E136", ld["name"], "W, random minus zeros, burst at 800 MHz", "W", mr - mz,
                        f"docs/reports/data/2026-11-02-e136-large-gemm/results.json cells.g4k-{fmt}-{rk} and "
                        f"g4k-{fmt}-zeros .burst_p800_w_runs (one run each)",
                        pr["difference_w"], pr["difference_band_w"], lab,
                        extra={"label_frozen": ld["label"], "corrected_w_posthoc": cor["corrected_w"],
                               "corrected_error_pct_posthoc": cor["corrected_error_pct"]}))
        e136_err.append(100 * (pr["difference_w"] - (mr - mz)) / (mr - mz))

    # ---------------- E86, E95: S per kind in the loop
    def item_of(exp, kind):
        fmt, k = kind.split(".", 1)
        if k.startswith("real2:"):
            return f"{fmt}.r2_{k[6:]}"
        if k.startswith("real:"):
            return f"{fmt}.real_{k[5:]}"
        return kind
    srcs = {"E86": "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json",
            "E95": "docs/reports/data/2026-11-01-e95-real-tensors-energy/e95.json"}
    meas_items = {ex: rd(p)["items"] for ex, p in srcs.items()}
    e8695 = {"E86": [], "E95": []}
    missing = []
    for ex in ("E86", "E95"):
        for ld in by.get(ex, []):
            key = item_of(ex, ld["name"])
            it = meas_items[ex].get(key)
            if not it:
                missing.append(f"{ex} {ld['name']} (no item {key})")
                continue
            pr = ld["predicted"]["given_seconds"]
            rows.append(row(ex, ld["name"], "S, W over idle", "W", it["S"]["mean"], f"{srcs[ex]} items.{key}.S",
                            pr["w_over_idle"], pr["w_over_idle_band"], ld["label"],
                            extra={"measured_ci95": it["S"]["ci95"]}))
            e8695[ex].append(pr["w_over_idle"] - it["S"]["mean"])

    summary = {
        "E39": {"rms_w_six": rms(e39_err), "bias_w_six": sum(e39_err) / len(e39_err),
                "v1_rms_w_six_recomputed": rms(e39_err_v1), "v1_rms_w_committed": v1["E39_gemv_sparsity_ladder"]["rms_w"],
                "endpoint_crosscheck_rms_w": rms(e39_ends),
                "slopes_inside_measured_ci99": sum(1 for r in rows if r["load"] == "E39" and r.get("inside_measured_ci99")),
                "label": "held out, not blind", "seconds": "the loop's 546 cycles an op, the same given or forecast"},
        "E37": {"depends_on_awake_rule": AWAKE_NOTE,
                "posthoc_without_awake_rule": {"rms_w_given": ph["awake_rule_e37"]["rms_w_given_no_rule"],
                                               "j_per_op_error_pct_given": ph["awake_rule_e37"]["j_per_op_error_pct_given_no_rule"],
                                               "source": "posthoc-v2.json awake_rule_e37"},
                "posthoc_j_total_per_op_error_pct_t0_at_die_start": ph["e37_die_start"]["j_total_per_op_error_pct_given"],
                "posthoc_bytes_per_op_zeroing_the_miss": ph["e37_bytes"]["bytes_per_op_zeroing_the_miss"],
                "rms_w_given": rms(e37["given"]), "bias_w_given": sum(e37["given"]) / 3,
                "rms_w_forecast": rms(e37["forecast"]), "bias_w_forecast": sum(e37["forecast"]) / 3,
                "v1_rms_w_committed": v1["E37_mmbench_fp32_from_DRAM"]["rms_w"], "v1_rms_w_recomputed": rms(e37["v1"]),
                "j_per_op_error_pct_given": e37_j["given"], "j_per_op_error_pct_forecast": e37_j["forecast"],
                "j_total_per_op_error_pct_given": e37_j["total_given"],
                "j_total_per_op_error_pct_forecast": e37_j["total_forecast"],
                "label": "held out, not blind; post hoc for the awake rule"},
        "E59": {"rms_w_given": rms(e59["w_given"]), "bias_w_given": sum(e59["w_given"]) / 4,
                "v1_rms_w_committed": v1["E59_sparse_parity"]["rms_w"], "v1_rms_w_recomputed": rms(e59["w_v1"]),
                "j_per_solve_error_pct_given": e59["j_given"], "j_per_solve_error_pct_forecast": e59["j_forecast"],
                "j_total_per_solve_error_pct_given": e59["jt_given"],
                "j_total_per_solve_error_pct_forecast": e59["jt_forecast"], "label": "held out, not blind",
                "reductions": "W is scored against each record's board.catalogue.over_idle_w (the energy catalogue's "
                              "cross-check) and J against its board.j_per_solve (the headline); for one run the two "
                              "differ by %.1f-%.1f%% (posthoc-v2.json e59_reductions)" % (
                                  min(abs(v["apart_pct"]) for v in ph["e59_reductions"]["per_run"].values()),
                                  max(abs(v["apart_pct"]) for v in ph["e59_reductions"]["per_run"].values())),
                "posthoc_op_cycles_priced_once": {
                    "j_per_solve_error_pct_given": [ph["e59_double_count"]["per_run"][n]["given"]["j_over_idle_error_pct_once"]
                                                    for n in ph["e59_double_count"]["per_run"]],
                    "double_count_share_pct_given": [ph["e59_double_count"]["per_run"][n]["given"]["double_count_share_pct"]
                                                     for n in ph["e59_double_count"]["per_run"]],
                    "source": "posthoc-v2.json e59_double_count"},
                "terms_v1_lacked_pct_given": ph["e59_terms_v1_lacked"]["pct"]},
        "E101": {"error_pct_loop_cells": e101_err["loop"], "rms_pct_loop_cells": rms(e101_err["loop"]),
                 "loop_cells_label": "held out by price: M10's kernel term on a session M10 never saw (7 cells)",
                 "error_pct_dram_arm": e101_err["dram post hoc"],
                 "dram_arm_label": "post hoc for the awake rule (2 cells, mmp64)",
                 "dram_arm_posthoc": ph["awake_rule_e101_dram"]["cells"],
                 "error_pct_in_sample_cells": e101_err["in sample"], "rms_pct_in_sample": rms(e101_err["in sample"]),
                 "first_reported_rms_pct_nine_cells_superseded": rms(e101_err["first nine"]),
                 "first_reported_note": "the first scorer pooled the loop's 7 cells with the DRAM arm's 2 as 'held out by "
                                        "price' (7.1% rms); the DRAM arm is post hoc for the awake rule (fix-q166)"},
        "E136": {"error_pct": e136_err, "label": "held out, not blind; differences only",
                 "posthoc_corrected_error_pct": {k: v["corrected_error_pct"]
                                                 for k, v in ph["e136_l3_correction"]["per_format"].items()},
                 "correction": "dated, post hoc: the L3 row's share of random minus zeros is not zero (posthoc-v2.json)"},
        "E86": {"rms_w": rms(e8695["E86"]), "n": len(e8695["E86"]),
                "label": "M10 held out by kind (M10 was fitted on these rows, each kind left out)"},
        "E95": {"rms_w": rms(e8695["E95"]), "n": len(e8695["E95"]),
                "label": "M10 held out by kind (M10 was fitted on these rows, each kind left out)"},
        "not_scored": missing,
    }
    out = {"what": "load ledger v2's frozen predictions scored against the committed measurements (Q166, calc-a)",
           "frozen_v2_sha256": P["frozen_v2_sha256"], "freeze_hashes": sums, "summary": summary, "rows": rows}
    with open(os.path.join(D, "scores-v2.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    chart = {"what": "forecast against measured, one row per scored number, each with its source and label "
                     "(tools/ledger/chart_ledger_v2.py draws chart-v2.html from it)",
             "rows": [{k: r.get(k) for k in ("load", "name", "quantity", "unit", "seconds", "measured", "measured_source",
                                             "forecast", "forecast_band", "error_pct", "label", "v1_forecast")}
                      for r in rows]}
    with open(os.path.join(D, "chart-data-v2.json"), "w") as f:
        json.dump(chart, f, indent=1)
        f.write("\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
