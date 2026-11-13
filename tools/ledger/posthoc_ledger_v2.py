#!/usr/bin/env python3
"""The load ledger v2's dated corrections, all POST HOC (Q166, fix-q166, Thu 12 Nov 2026).

Written after the scores, on a verifier's findings (Q166's verify-calc). It changes no frozen file and no frozen
prediction: it re-runs the frozen model (ledger_v2.py, loads_ledger_v2.py, frozen-v2.json) on variants of the frozen
loads, reads the same committed measurements score_ledger_v2.py reads, and writes posthoc-v2.json. Every number in it
is labelled post hoc: each variant was chosen after the measurements and the frozen scores were seen.

  1. awake_rule_e37: E37 with every waiting cycle priced as awake (without the awake rule, which was set during the
     build after arithmetic beside E101's DRAM arm, the same benchmark streaming from DRAM).
  2. awake_rule_e101_dram: E101's two DRAM-arm cells (mmp64), with and without the rule.
  3. e136_l3_correction: E136's random minus zeros without the L3 row, whose zeros and random columns come from two
     cards (13.5 pJ/B of aifoundry3 against 12.3 of aifoundry2), so it added about -0.12 W to every difference.
  4. e59_double_count: sparse parity with the op's awake cycles priced once: each op's cycles sit inside the tensor
     price (the loop's cycles an op) and inside the scratchpad-load price (2 KB at the probe's 4 B a minion-cycle)
     while hart 0 spends only C_OP_str (1 + KAPPA_T U) on it, so the excess was priced twice.
  5. e59_terms_v1_lacked: the share of each run's joules over idle (given its seconds) in the terms v1 had none of.
  6. e59_reductions: which reduction of each E59 run the scores use (watts: the catalogue cross-check; joules: the
     headline) and how far apart the two are.
  7. e37_die_start: E37 with the run's starting die (die_c_start) as T0, where the frozen load used the run's mean die.
  8. e37_bytes: the byte count that would zero E37's miss on each card, and the bytes a measured op moved at 76 GB/s.
  9. nits: aifoundry3's rest law at its footing band's lower edge; E136's unpriced L2-side path.

    python3 -I -B tools/ledger/posthoc_ledger_v2.py        # writes docs/reports/data/2026-11-12-q166-ledger-v2/posthoc-v2.json

Desk only. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ledger_v2 as LV  # noqa: E402
import loads_ledger_v2 as LL  # noqa: E402

REPO = LV.REPO
D = os.path.join(REPO, "docs", "reports", "data", "2026-11-12-q166-ledger-v2")
DV3 = "docs/reports/data/2026-09-25-claims-v3/results"
SP = "workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy"
NAMES = {"L1 (512,4,0.3,448)": "aifoundry3-1136-l1", "L2 (512,4,0.4,1850)": "aifoundry3-1136-l2",
         "(256,5,0.4,1925) first half": "aifoundry3-1136-f5h0", "(256,5,0.4,1925) second half": "aifoundry3-1136-f5h1"}
LABEL = "post hoc (fix-q166, Thu 12 Nov 2026): a variant chosen after the frozen scores were seen"


def rd(rel):
    return json.load(open(os.path.join(REPO, rel)))


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def pct(f, m):
    return 100.0 * (f - m) / m


def mmb_meas():
    out = {}
    for it in rd(f"{DV3}/mmb.json")["items"]:
        if it.get("item") == "MMB-c":
            for card, v in it["per_card"].items():
                d = v["fp32-tensor-DRAM"]
                out[card] = {"w": d["mean"], "idle_before_w": d["idle_before_w"], "die_c_mean": d["die_c_mean"],
                             "die_c_start": d["die_c_start"]}
    return out


def e37_variant(ld, which, F, awake="rule", die=None, bytes_per_op=None):
    v = copy.deepcopy(ld["variants"][f"{which}_seconds"])
    c = v["_note"]["cycles_per_op"]
    ops = v["work_units"]
    b = 2048.0 if bytes_per_op is None else bytes_per_op
    if bytes_per_op is not None:
        v["bytes"][0]["bytes"] = b * ops
    if awake == "rule":
        v["awake_hart_cycles"] = max(0.0, c - 546.0 - b / F["probe_rates_b_per_minion_cycle"]["dram_load"]) * ops
    else:                                   # every waiting cycle priced as awake
        v["awake_hart_cycles"] = max(0.0, c - 546.0) * ops
    if die is not None:
        v["die_start_c"] = die
    return LV.predict(v, F), ops


def compute():
    """Every correction, as the dict posthoc-v2.json holds (score_ledger_v2.py reads it too)."""
    F = LV.load_frozen()
    P = json.load(open(os.path.join(D, "predictions-v2.json")))
    by = {}
    for ld in P["loads"]:
        by.setdefault(ld["load"], []).append(ld)
    out = {"what": "the load ledger v2's dated corrections, every one post hoc (tools/ledger/posthoc_ledger_v2.py)",
           "label": LABEL, "frozen_v2_sha256": P["frozen_v2_sha256"]}

    # ---- 1 and 7, 8: E37
    meas = mmb_meas()
    e37 = {}
    for ld in LL.e37_loads(F):
        card = ld["variants"]["given_seconds"]["card"]
        m = meas[card]
        c_meas = ld["inputs"]["cycles_per_op_measured"]
        ops_meas = 1024 * 600e6 / c_meas
        jm = m["w"] / ops_meas
        jtm = (m["idle_before_w"] + m["w"]) / ops_meas
        row = {"measured_w": m["w"], "cycles_per_op_measured": c_meas}
        for which in ("given", "forecast"):
            for aw in ("rule", "no_rule"):
                pr, ops = e37_variant(ld, which, F, awake=aw)
                w = pr["w_over_idle_with_heat"]
                row[f"{which}_{aw}"] = {"w_over_idle_with_heat": w, "w_error_pct": pct(w, m["w"]),
                                        "j_per_op_error_pct": pct(w / ops, jm),
                                        "j_total_per_op_error_pct": pct((pr["rest"]["w"] + w) / ops, jtm)}
            pr, ops = e37_variant(ld, which, F, die=m["die_c_start"])
            w = pr["w_over_idle_with_heat"]
            row[f"{which}_die_start"] = {"die_start_c": m["die_c_start"], "die_mean_c_frozen": m["die_c_mean"],
                                         "rest_w": pr["rest"]["w"], "w_over_idle_with_heat": w,
                                         "j_total_per_op_error_pct": pct((pr["rest"]["w"] + w) / ops, jtm)}
        # 8: the bytes an op that would zero the given-seconds miss (the awake rule as frozen), by bisection
        lo, hi = 256.0, 2048.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            pr, _ops = e37_variant(ld, "given", F, bytes_per_op=mid)
            if pr["w_over_idle_with_heat"] > m["w"]:
                hi = mid
            else:
                lo = mid
        row["bytes_per_op_zeroing_the_miss"] = 0.5 * (lo + hi)
        bw = LV._c(F, "dram_bandwidth_gb_s") * 1e9
        row["bytes_per_op_at_76_gb_s_in_the_measured_cycles"] = c_meas * bw / (1024 * 600e6)
        row["gb_s_if_2048_b_an_op"] = 2048.0 * 1024 * 600e6 / c_meas / 1e9
        e37[card] = row
    out["awake_rule_e37"] = {
        "what": "E37 (mmbench fp32 from DRAM) with and without the awake rule; the rule prices none of a hart's wait "
                "inside its own DRAM loads (2,048 B at the probe's 0.124 B a minion-cycle), so only c - 546 - 16,556 "
                "cycles an op, none on these runs, are priced as awake; without it all c - 546 are",
        "label": LABEL, "per_card": {k: {kk: vv for kk, vv in v.items() if kk.startswith(("given_", "forecast_"))
                                         and not kk.endswith("die_start")} for k, v in e37.items()},
        "j_per_op_error_pct_given_rule": [e37[c]["given_rule"]["j_per_op_error_pct"] for c in e37],
        "j_per_op_error_pct_given_no_rule": [e37[c]["given_no_rule"]["j_per_op_error_pct"] for c in e37],
        "rms_w_given_rule": rms([e37[c]["given_rule"]["w_over_idle_with_heat"] - e37[c]["measured_w"] for c in e37]),
        "rms_w_given_no_rule": rms([e37[c]["given_no_rule"]["w_over_idle_with_heat"] - e37[c]["measured_w"] for c in e37]),
        "cards": list(e37)}
    out["e37_die_start"] = {
        "what": "E37's frozen T0 is the run's mean die (die_c_mean), itself raised by the run, and the ledger adds the "
                "forecast rise on top; here T0 is the run's starting die (die_c_start)",
        "label": LABEL,
        "j_total_per_op_error_pct_given": {c: e37[c]["given_die_start"]["j_total_per_op_error_pct"] for c in e37},
        "j_total_per_op_error_pct_forecast": {c: e37[c]["forecast_die_start"]["j_total_per_op_error_pct"] for c in e37},
        "die_c": {c: [e37[c]["given_die_start"]["die_start_c"], e37[c]["given_die_start"]["die_mean_c_frozen"]] for c in e37}}
    out["e37_bytes"] = {
        "what": "E37's residual (+13-14% an op) is the DRAM row's price OR the byte count: 2,048 B an op is assumed "
                "(bracket 1,024-2,048); the measured cycles move fewer bytes at 76 GB/s, and this many bytes an op "
                "would zero the given-seconds miss with every other input frozen",
        "label": LABEL,
        "bytes_per_op_zeroing_the_miss": {c: e37[c]["bytes_per_op_zeroing_the_miss"] for c in e37},
        "bytes_per_op_at_76_gb_s": {c: e37[c]["bytes_per_op_at_76_gb_s_in_the_measured_cycles"] for c in e37},
        "gb_s_if_2048_b_an_op": {c: e37[c]["gb_s_if_2048_b_an_op"] for c in e37}}

    # ---- 2: E101's DRAM arm with and without the awake rule
    e101 = rd("docs/reports/data/2026-11-01-e101-real-matmul/e101.json")
    loop = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
    dram = {}
    for ld in LL.e101_loads(F):
        if not ld["name"].startswith("mmp64"):
            continue
        v = ld["variants"]["given_seconds"]
        c = ld["inputs"]["cycles_per_op"]
        fmt = ld["name"].split()[1]
        meas_s = e101["items"][ld["item"]]["S"]["mean"]
        rule = LV.predict(v, F)["w_over_idle"]
        v2 = copy.deepcopy(v)
        v2["awake_hart_cycles"] = max(0.0, c - loop[fmt]) * v2["work_units"]
        norule = LV.predict(v2, F)["w_over_idle"]
        dram[ld["name"]] = {"measured_w": meas_s, "with_rule_w": rule, "with_rule_error_pct": pct(rule, meas_s),
                            "without_rule_w": norule, "without_rule_error_pct": pct(norule, meas_s)}
    out["awake_rule_e101_dram"] = {
        "what": "E101's DRAM arm (mmp64, the benchmark streaming from DRAM): the awake rule was set during the build "
                "after arithmetic that put v2 beside these two cells, so they are post hoc for it",
        "label": LABEL, "cells": dram}

    # ---- 3: E136 without the L3 row's spurious share
    cells = rd("docs/reports/data/2026-11-02-e136-large-gemm/results.json")["cells"]
    e136 = {}
    for ld in by["E136"]:
        fmt = ld["name"].split()[1].rstrip(",")
        rk = "full" if fmt == "int8" else "randn"
        mr = cells[f"g4k-{fmt}-{rk}"]["burst_p800_w_runs"][0]
        mz = cells[f"g4k-{fmt}-zeros"]["burst_p800_w_runs"][0]
        pr = ld["predicted"]
        l3 = lambda d: sum(t["j"] for k, t in pr[d]["terms"].items() if k.startswith("bytes:l3_load"))  # noqa: E731
        spurious = (l3("random") - l3("zeros")) / pr["random"]["seconds"]
        corr = pr["difference_w"] - spurious
        e136[fmt] = {"measured_w": mr - mz, "frozen_w": pr["difference_w"], "frozen_error_pct": pct(pr["difference_w"], mr - mz),
                     "l3_share_w": spurious, "corrected_w": corr, "corrected_error_pct": pct(corr, mr - mz)}
    out["e136_l3_correction"] = {
        "what": "the frozen label said the L3 row's share of random minus zeros is zero by construction; it is not: "
                "its zeros column is aifoundry3's 13.5 pJ/B and aifoundry2's random column 12.3, so every difference "
                "carries a spurious l3_share_w; corrected = frozen minus it",
        "label": LABEL, "per_format": e136}

    # ---- 4, 5, 6: E59
    cy = F["cycle_model"]["FITTED"]
    awake_pj = LV._c(F, "awake_pj_per_hart_cycle")
    loop_int8 = 1024 * 600e6 / F["zeros_anchor"]["int8"]["a3"]["rate_ops_per_s"]
    scp_cyc = 2048.0 / F["probe_rates_b_per_minion_cycle"]["scp_load"]
    e59, lacked, red = {}, {}, {}
    for ld in by["E59"]:
        en = rd(f"{SP}/{NAMES[ld['name']]}/energy.json")
        mj, mjt = en["board"]["j_per_solve"], en["board"]["j_per_solve_total"]
        ops, U = ld["inputs"]["counts"]["ops"], ld["inputs"]["U_planner"]
        over = max(0.0, loop_int8 + scp_cyc - cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U))
        row = {"overlap_cycles_per_op": over, "loop_cycles_per_op": loop_int8, "scp_load_cycles_per_op": scp_cyc,
               "hart0_cycles_per_op": cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U)}
        for which in ("given", "forecast"):
            v = copy.deepcopy(ld["variants"][f"{which}_seconds"])
            frozen = ld["predicted"][f"{which}_seconds"]
            v["awake_hart_cycles"] = max(0.0, v["awake_hart_cycles"] - over * ops)
            pr = LV.predict(v, F)
            row[which] = {"double_count_j": frozen["j_over_idle"] - pr["j_over_idle"],
                          "double_count_share_pct": 100.0 * (frozen["j_over_idle"] - pr["j_over_idle"]) / frozen["j_over_idle"],
                          "j_over_idle_error_pct_frozen": pct(frozen["per_unit"]["j_over_idle"], mj),
                          "j_over_idle_error_pct_once": pct(pr["per_unit"]["j_over_idle"], mj),
                          "j_total_error_pct_frozen": pct(frozen["per_unit"]["j_total"], mjt),
                          "j_total_error_pct_once": pct(pr["per_unit"]["j_total"], mjt)}
        e59[ld["name"]] = row
        g = ld["predicted"]["given_seconds"]
        lk = sum(t["j"] for k, t in g["terms"].items() if k.startswith("instr:") or k == "awake")
        lacked[ld["name"]] = 100.0 * lk / g["j_over_idle"]
        cat = en["board"]["catalogue"]
        t = 1.0 / en["solves_per_s"]
        red[ld["name"]] = {"w_scored_against": "board.catalogue.over_idle_w (the energy catalogue's cross-check)",
                           "j_scored_against": "board.j_per_solve (the run's headline)",
                           "catalogue_w_times_t_j": cat["over_idle_w"] * t, "catalogue_j_per_solve": cat["j_per_solve"],
                           "headline_j": mj, "apart_pct": pct(cat["over_idle_w"] * t, mj),
                           "catalogue_j_apart_pct": pct(cat["j_per_solve"], mj)}
    out["e59_double_count"] = {
        "what": "each sparse-parity op's cycles are inside the tensor price (the int8 loop's cycles an op) and inside "
                "the scratchpad-load price (2 KB at the probe's 4 B a minion-cycle), while hart 0 spends only "
                "C_OP_str (1 + KAPPA_T U) on the op: the excess was priced twice; here it is priced once",
        "label": LABEL, "awake_pj_per_hart_cycle": awake_pj, "per_run": e59}
    out["e59_terms_v1_lacked"] = {
        "what": "the share of each run's joules over idle, given its seconds, in hart 1's generation, the epilogue and "
                "set-up and the awake time (the terms v1 had none of); desk arithmetic of the frozen ledger",
        "label": "desk arithmetic of the frozen predictions", "pct": lacked,
        "range_pct": [min(lacked.values()), max(lacked.values())]}
    out["e59_reductions"] = {
        "what": "E59's watts are scored against the record's catalogue cross-check and its joules against the record's "
                "headline; the two reductions of one run are this far apart, so W and J errors of one forecast differ",
        "label": "reported (the records' own two reductions)", "per_run": red}

    # ---- 9: nits
    lo_c = F["idle_laws"]["aifoundry3"]["quad_band_c"][0]
    q = F["idle_laws"]["aifoundry3"]["quad"]
    quad = q["a"] * lo_c * lo_c + q["b"] * lo_c + q["c"]
    e = F["idle_laws"]["aifoundry3"]["exp"]
    expv = e["B"] + e["A80"] * math.exp((lo_c - 80.0) / e["T_L"])
    l2 = F["mem_paths"]["l2_stream"]
    q51 = q["a"] * 51.0 * 51.0 + q["b"] * 51.0 + q["c"]
    e51 = e["B"] + e["A80"] * math.exp((51.0 - 80.0) / e["T_L"])
    nits = {"aifoundry3_rest_law_step_at_band_edge_w": {"edge_c": lo_c, "footing_law_w": quad, "exponential_law_w": expv,
                                                         "step_w": quad - expv,
                                                         "at_51_c_the_e59_l1_l2_start": {"footing_law_extended_w": q51,
                                                                                         "exponential_law_used_w": e51,
                                                                                         "difference_w": q51 - e51}},
            "e136_l2_side_path_if_priced_w": {}}
    for ld in by["E136"]:
        fmt = ld["name"].split()[1].rstrip(",")
        ops = ld["pair"]["random"]["work_units"]
        v2f = LV.v2_factor(F, "aifoundry2", 800.0)
        nits["e136_l2_side_path_if_priced_w"][fmt] = 384.0 * ops * (l2["random_pj"]["a2"] - l2["zeros_pj"]) * 1e-12 * v2f
    out["nits"] = nits
    return out


def main():
    out = compute()
    dram, e136, e59 = out["awake_rule_e101_dram"]["cells"], out["e136_l3_correction"]["per_format"], out["e59_double_count"]["per_run"]
    lacked = out["e59_terms_v1_lacked"]["pct"]
    with open(os.path.join(D, "posthoc-v2.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    short = {"E37 J/op given, rule": [round(x, 1) for x in out["awake_rule_e37"]["j_per_op_error_pct_given_rule"]],
             "E37 J/op given, no rule": [round(x, 1) for x in out["awake_rule_e37"]["j_per_op_error_pct_given_no_rule"]],
             "E101 DRAM": {k: [round(v["with_rule_error_pct"], 1), round(v["without_rule_error_pct"], 1)] for k, v in dram.items()},
             "E136 corrected": {k: round(v["corrected_error_pct"], 1) for k, v in e136.items()},
             "E59 J over idle given, once": [round(e59[n]["given"]["j_over_idle_error_pct_once"], 1) for n in e59],
             "E59 double count share": [round(e59[n]["given"]["double_count_share_pct"], 1) for n in e59],
             "E59 terms v1 lacked": [round(lacked[n], 1) for n in lacked],
             "E37 J total given at die start": {c: round(v, 2) for c, v in out["e37_die_start"]["j_total_per_op_error_pct_given"].items()},
             "E37 bytes zeroing": {c: round(v) for c, v in out["e37_bytes"]["bytes_per_op_zeroing_the_miss"].items()},
             "E37 bytes at 76 GB/s": {c: round(v) for c, v in out["e37_bytes"]["bytes_per_op_at_76_gb_s"].items()}}
    print(json.dumps(short, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
