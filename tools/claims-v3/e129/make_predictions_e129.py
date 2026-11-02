#!/usr/bin/env python3
"""E129 (Q136): write predictions-e129.json and predictions-e129.txt, E129's frozen numbers, from committed files only (E109's frozen file, E124's
committed card-1 results, Q136(c)'s committed bench counts and prices). Standard library only.

    python3 tools/claims-v3/e129/make_predictions_e129.py           # writes both files beside this script

Every number below is read from the file named beside it in "sources"; nothing is typed in but the lines, bands, tolerances and the budget, which are the
registration's own choices (E129.md).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E109P = "tools/claims-v3/e109/predictions-e109.json"
E124D = "docs/reports/data/2026-11-01-e124-int8-zeros-replicate"
Q136C = "docs/reports/data/2026-11-02-q136c-tima-bench"
E124_EXP = "E124, aifoundry1 card 1 (registered, four passes)"

REUSED = [
    "tools/claims-v3/lib.sh",
    "tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json",
    "tools/claims-v3/kinds/tiles/fp32/zeros.bin", "tools/claims-v3/kinds/tiles/int8/zeros.bin",
    "tools/claims-v3/e128/ettelem_guard.sh",
    "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
    "tools/claims-v3/e109/sp109/CMakeLists.txt", "tools/claims-v3/e109/sp109/sparsity_args.h", "tools/claims-v3/e109/sp109/host/CMakeLists.txt",
    "tools/claims-v3/e109/sp109/host/Constants.h.in", "tools/claims-v3/e109/sp109/host/main.cpp", "tools/claims-v3/e109/sp109/kernel/CMakeLists.txt",
    "tools/claims-v3/e109/sp109/kernel/crt.S", "tools/claims-v3/e109/sp109/kernel/sections.ld", "tools/claims-v3/e109/sp109/kernel/sparsity.c",
    "workloads/sparsity/host/main.cpp",
]
# the binaries the run executes on aifoundry1, as E124's passes and E128's box record them
BOX_BINARIES = {
    "build/e109/host/sparsity_host": (f"{E124D}/aifoundry1-c1/e124/p12413/binaries.sha256", "build/e109/host/sparsity_host"),
    "build/e109/kernel/sparsity.elf": (f"{E124D}/aifoundry1-c1/e124/p12413/binaries.sha256", "build/e109/kernel/sparsity.elf"),
    "build/sparsity/host/sparsity_host": (f"{E124D}/aifoundry1-c1/e124/p12413/binaries.sha256", "build/sparsity/host/sparsity_host"),
    "build/sparsity/kernel/sparsity.elf": ("docs/reports/data/2026-11-02-e128-fp16-signs/aifoundry1-c1/e128/readback-p12802/binaries.sha256",
                                           "build/sparsity/kernel/sparsity.elf"),
    "build/ettelem/ettelem": ("docs/reports/data/2026-11-02-e128-fp16-signs/desk/box-binaries.txt", "build/ettelem/ettelem"),
}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def J(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def from_hashlist(rel, name):
    for ln in open(os.path.join(ROOT, rel)):
        f = ln.split()
        if len(f) == 2 and f[1] == name and len(f[0]) == 64:
            return f[0]
    raise SystemExit(f"{name} not in {rel}")


def main():
    p109 = J(E109P)
    e124 = J(f"{E124D}/e124.json")
    sc124 = J(f"{E124D}/scored.json")
    ex124 = J(f"{E124D}/extras.json")
    pr124 = J("tools/claims-v3/e124/predictions-e124.json")
    priced = J(f"{Q136C}/priced.json")
    counts = J(f"{Q136C}/counts.json")
    cc = J(f"{Q136C}/corrections-check.json")
    pe = priced["experiments"][E124_EXP]
    con = pe["contrasts"]
    k_r1_card = "desk-only arm: N with one A row, fp32 after an int8 run"
    k_r1_reset = "desk-only arm: N with one A row (TenC read at one address), from reset"
    k_n_card, k_n_reset = "N, fp32 after an int8 run (the card's order)", "N, from reset (the bench's own runs)"
    sums = lambda k: {m: v["sum"] for m, v in con[k]["priced_w"].items()}
    r1_card, r1_reset, n_card, n_reset = sums(k_r1_card), sums(k_r1_reset), sums(k_n_card), sums(k_n_reset)
    tima_issue = cc["experiments"][E124_EXP]["per_pass"]["desk-only arm: one A row, fp32 after an int8 run|A|tima_ctrl"]
    tima_issue_m0 = cc["experiments"][E124_EXP]["per_pass"].get("N, fp32 after an int8 run (the card's order)|A|tima_ctrl")
    # per-cycle ratios, r1 over m0, from the bench's counts a second (Q136(c) priced.json d_counts_per_s)
    tima_r1 = con[k_r1_reset]["d_counts_per_s"]["tima_ctrl"]["clocked"]
    tima_m0 = con[k_n_reset]["d_counts_per_s"]["tima_ctrl"]["clocked"]
    tenc_r1 = con[k_r1_reset]["d_counts_per_s"]["tenc"]["reads"]
    tenc_m0 = con[k_n_reset]["d_counts_per_s"]["tenc"]["reads"]
    st = {(s["set"], s["name"]): s["per_op"] for s in counts["streams"]}

    def op(setname, name):
        po = st[(setname, name)]
        a, x = po["arrays"], po["x"]
        return {"bench_cycles": po["cycles"], "scp_reads": po["scp_reads"], "scp_rd32": x["scp_rd32"], "scp_rd64": x["scp_rd64"], "scp_rd256": x["scp_rd256"],
                "tenc_reads": a["tenc"]["reads"], "tenc_reads_newaddr": a["tenc"]["reads_newaddr"], "tena_writes": a["tena"]["writes"],
                "tentmp_writes": a["tentmp"]["writes"], "tenb_writes": a["tenb"]["writes"], "ff_clocked_bits": po["ff_clocked_bits"]}

    delta = p109["rules"]["R6_cycles"]["delta_cycles"]
    arms = {
        "m0.fp32.zeros": op("design", "m0.fp32.zeros"), "m0.int8.zeros": op("design", "m0.int8.zeros"),
        "m0r1.fp32.zeros": op("arms_pace", "m0r1.fp32.zeros"), "m0r1.int8.zeros": op("arms_pace", "m0r1.int8.zeros"),
    }
    pred_cycles = {k: p109["rules"]["R6_cycles"]["predicted"][k] for k in ("m0.fp32.zeros", "m0.int8.zeros", "m0k8.fp32.zeros", "m0k8.int8.zeros")}
    for f in ("fp32", "int8"):
        pred_cycles[f"m0r1.{f}.zeros"] = st[("arms_pace", f"m0r1.{f}.zeros")]["cycles"] + delta[f]
    rate_r1 = {f: 600e6 * 1024 / pred_cycles[f"m0r1.{f}.zeros"] for f in ("fp32", "int8")}
    # E124's per-pass spreads, for the expected resolution at 6, 8 and 10 passes (E124 scored.json)
    T95 = {3: 3.182, 5: 2.571, 7: 2.365, 9: 2.262}
    def sd(v):
        m = sum(v) / len(v)
        return (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5
    gop = sc124["gap"]["G_op"]
    G124 = sc124["gap"]["G"]["mean"]
    N124 = ex124["added_rules"]["Y1"]["N"]
    sd_gop, sd_n = sd(gop["per_pass"]), sd(N124["per_pass"])
    reso = {str(n): {"G_op_half_w": T95[n - 1] * sd_gop / n ** 0.5, "N1_half_w_if_N_spread": T95[n - 1] * sd_n / n ** 0.5,
                     "R1_if_E124_mean": ("FAIL" if gop["mean"] + T95[n - 1] * sd_gop / n ** 0.5 < G124 / 2 else "INCONCLUSIVE")} for n in (6, 8, 10)}
    harness = {"reused_unchanged_sha256": {rel: sha(rel) for rel in REUSED},
               "box_binaries_sha256": {b: from_hashlist(src, nm) for b, (src, nm) in BOX_BINARIES.items()},
               "box_binaries_sources": {b: src for b, (src, _) in BOX_BINARIES.items()}}
    items = e124["items"]
    out = {
        "experiment": "E129",
        "question": "Q136, lane a1c1-e129-int8-noissue; the kinds page's section 11, item 11 ('int8 zeros' extra 0.61 W'); Q134's final critic, item 5",
        "card": {"name": "aifoundry1-c1", "host": "aifoundry1", "device": 1, "lock": "/run/lock/etsoc-shire1.lock", "clock_mhz": 600,
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}},
                 "what": "aifoundry1 card 1, firmware 1.2.0 (BL2 0.18.0), 600 MHz in every sample since 25 Sep, TDP 65 W / threshold 65 C (read, never set)"},
        "sources": {"e109_frozen": E109P, "e124_reduction": f"{E124D}/e124.json", "e124_scored": f"{E124D}/scored.json",
                    "e124_extras": f"{E124D}/extras.json", "e124_frozen": "tools/claims-v3/e124/predictions-e124.json",
                    "q136c_priced": f"{Q136C}/priced.json", "q136c_counts": f"{Q136C}/counts.json", "q136c_corrections": f"{Q136C}/corrections-check.json"},
        "items": ["m0.fp32.zeros", "m0k8.fp32.zeros", "m0r1.fp32.zeros", "m0.int8.zeros", "m0k8.int8.zeros", "m0r1.int8.zeros"],
        "anchors": ["fp32.zeros", "int8.zeros"],
        "runs_per_pass": 14, "burnin_runs_per_pass": 2,
        "arms_bench_per_op": arms,
        "one_row_rates_pred_ops_per_s": rate_r1,
        "passes": list(range(12910, 12920)), "smoke_pass": 12901,
        "min_kept_passes": {"every_rule": 3, "R1": 6},
        "budget": {"card_minutes": 35, "budget_s": 2100, "reserve_s": 150, "first_estimate_s": 300, "deadline": "2026-11-02 15:50 PST",
                   "anchor": "E129_T0 = the session's launch (date +%s in the launch command); card time counted from the session's first config read to its last",
                   "no_new_session_after": "2026-11-02 15:00 PST"},
        "primary_reduction": {"code": "tools/claims-v3/e129/reduce_e129.py (reduce_e78.py unchanged)", "leak_w_per_c": 0.2414, "dips": "removed (E82 A2)",
                              "gates": "E78's, unchanged; the four anchors E129 does not run (fp32/fp16 random, fp16 zeros, int8 full) have no runs to gate"},
        "set_aside_rule": {
            "why": "E129's statistics use only each format's zeros anchors and the six arms; pi enters none but its own R10 cell. On this card a pass whose "
                   "statistics are intact has been set aside by a gate on an anchor no statistic uses (E124's dips-kept arm: 12410 and 12412 by fp16 "
                   "random's span, 12412 also by pi's drift, +1.082 W). R1 needs six kept passes.",
            "rule": "The primary reduction (E78's pass gates as they apply to E129's pass: the zeros anchors' span <= 0.60 W and straight-line departure "
                    "<= 0.25 W, pi's drift <= 0.60 W, at most 2 failed runs, card 1's config gate) carries every verdict if it keeps at least 6 passes. "
                    "If it keeps fewer, the relaxed reduction (reduce_e129.py --relax-tie: GATES['tie_drift_w'] 0.60 -> 99 W) carries them if it keeps "
                    "more passes than the primary: a pass set aside ONLY by pi's drift is restored, a pass set aside by any other gate stays out, and the "
                    "verdicts are labelled 'scored under the set-aside rule'. R1 needs at least 6 kept passes in the reduction that carries the verdicts, "
                    "else it reads NOT-SCORED and G_op is reported with no verdict; every other rule needs at least 3. The relaxed reduction is always "
                    "reported. No pass is added after any reduction is read, and no pass is chosen after the fact.",
            "relaxed_gate": {"tie_drift_w": 99.0}},
        "rules": {
            "R0_R3": "E109's (predictions-e109.json › rules R0-R3), statistics and lines unchanged: shares of G with 95% lower bound >= G/2 carry it",
            "R1_ops": {"statistic": "G_op = e_op(int8) O(int8) - e_op(fp32) O(fp32)", "line": "G/2 (this session's G)",
                       "verdict": "PASS if lower >= G/2; FAIL if upper < G/2; else INCONCLUSIVE; NOT-SCORED with fewer than 6 kept passes"},
            "Y1": {"statistic": "N = S(m0.int8.zeros) - S(m0.fp32.zeros)", "line_w": pr124["added_rules"]["Y1"]["line_w"],
                   "predicted_w": N124["mean"], "verdict": "PASS if lower >= line_w; FAIL if upper < line_w; else INCONCLUSIVE"},
            "Y2": {"statistic": "e_op(fp32), e_op(int8)", "line_pj": pr124["added_rules"]["Y2"]["line_pj"],
                   "verdict": "PASS if both upper < line_pj; FAIL if either lower >= line_pj; else INCONCLUSIVE"},
            "R6_cycles": {"predicted": pred_cycles, "tolerance": 2.0,
                          "what": "the card's median cycles per op of each arm against the RTL's: the bench's own cycles + E109's 7.75 (E109's rule); m0 and m0k8 "
                                  "are E109's frozen values, m0r1 is Q136(c)'s bench (counts.json, set arms_pace) + 7.75"},
            "V0_equal_rate": {"statistic": "|cycles(m0r1.int8.zeros) - cycles(m0r1.fp32.zeros)| (medians)", "tolerance_cycles": 2.0,
                              "verdict": "EQUAL-RATE if <= 2 cycles, else RATES-DIFFER (V1 then carries that label)"},
            "V1_one_row": {"statistic": "N1 = S(m0r1.int8.zeros) - S(m0r1.fp32.zeros), per kept pass", "line_fraction_of_N": 0.5,
                           "verdict": "PER-ROW if N1's 95% upper bound < N/2 (N = this session's Y1 mean); PER-CYCLE if N1's 95% lower bound >= N/2; "
                                      "else INCONCLUSIVE"},
            "V2_readings": {"what": "which frozen reading N1's 95% interval agrees with: CONSISTENT if it overlaps the reading's range, else N1 BELOW / ABOVE",
                            "readings": {
                                "bench at its constants, the card's order (TenC read at one frozen address in fp32 too)": {
                                    "range_w": [min(r1_card.values()), max(r1_card.values())], "by_constant_set": r1_card},
                                "bench at its constants, from reset (TenC's reads int8's alone)": {
                                    "range_w": [min(r1_reset.values()), max(r1_reset.values())], "by_constant_set": r1_reset},
                                "the TIMA controls alone at the cards' issue price (17.2 fJ a clocked bit, Q136(c) result 5b), 95%": {
                                    "range_w": [tima_issue["lo"], tima_issue["hi"]], "mean_w": tima_issue["mean"]},
                                "all of N goes with work done every cycle (the r1/m0 ratio of the TIMA controls' or TenC's reads a second)": {
                                    "range_fraction_of_N": [tima_r1 / tima_m0, tenc_r1 / tenc_m0]},
                            }},
            "R10_tie": {"what": "the tie to E124 on this card (same frame for these cells); a failed cell labels every verdict and removes none",
                        "cells": {
                            "m0.fp32.zeros": {"what": "D", "ref": items["m0.fp32.zeros"]["D"]["mean"], "band": 0.3},
                            "m0.int8.zeros": {"what": "D", "ref": items["m0.int8.zeros"]["D"]["mean"], "band": 0.3},
                            "m0k8.fp32.zeros": {"what": "D", "ref": items["m0k8.fp32.zeros"]["D"]["mean"], "band": 0.3},
                            "m0k8.int8.zeros": {"what": "D", "ref": items["m0k8.int8.zeros"]["D"]["mean"], "band": 0.3},
                            "anchor_pi": {"what": "D", "ref": items["anchor_pi"]["D"]["mean"], "band": 0.5},
                            "gap G (S)": {"what": "G", "ref": G124, "band": 0.2},
                            "no-issue gap N (S)": {"what": "N", "ref": N124["mean"], "band": 0.5}}},
        },
        "predictions": {
            "if_e124_carries": {"R0": "PER-TIME", "R1": "INCONCLUSIVE at 6 kept passes, FAIL at 8 or more (E124's mean and per-pass spread)",
                                "R2": "LANES-OPPOSE", "R3": "PASS", "Y1": "PASS", "Y2": "PASS", "R6": "PASS x6", "V0": "EQUAL-RATE",
                                "numbers_w": {"G": G124, "G_lane": sc124["gap"]["G_lane"]["mean"], "G_op": gop["mean"], "G_rest": sc124["gap"]["G_rest"]["mean"],
                                              "N": N124["mean"]}},
            "resolution_from_e124_spread": reso,
            "V1": "No single expectation: at the bench's constants every reading puts N1 below N/2 (PER-ROW), 0.07-0.14 W in the card's order and "
                  "0.40-0.79 W from reset; at the cards' issue price the TIMA controls alone would put it near N/2 or above (0.98 +- 0.49 W), and "
                  "work done every cycle would keep 0.89-1.00 of N (PER-CYCLE).",
            "bench_N_16_rows_w": {"card_order": n_card, "from_reset": n_reset},
            "tima_issue_price_16_rows_w": tima_issue_m0,
        },
        "e124_reference": {"G": sc124["gap"]["G"], "G_op": gop, "N": N124, "e_op_pj": {f: sc124["quantities"][f]["e_op_pj"] for f in ("fp32", "int8")}},
        "harness": harness,
    }
    json.dump(out, open(os.path.join(HERE, "predictions-e129.json"), "w"), indent=1)
    L = ["E129 frozen numbers (predictions-e129.json, written by make_predictions_e129.py from committed files)", ""]
    L.append("R6 predicted cycles per op: " + ", ".join(f"{k} {v:.2f}" for k, v in pred_cycles.items()))
    L.append("one-row op rate predicted: " + ", ".join(f"{f} {v / 1e9:.3f} e9/s" for f, v in rate_r1.items()))
    L.append("V2 readings of N1 (W): " + "; ".join(f"{k}: {v.get('range_w') or v.get('range_fraction_of_N')}" for k, v in out["rules"]["V2_readings"]["readings"].items()))
    L.append(f"E124 on this card: G {G124:.4f} W, G_op {gop['mean']:+.4f} +- {gop['half']:.4f} W, N {N124['mean']:.4f} +- {N124['half']:.4f} W")
    L.append("expected resolution (E124's spreads): " + json.dumps(reso))
    L.append("R10 cells: " + ", ".join(f"{c} {s['ref']:+.3f} +- {s['band']}" for c, s in out["rules"]["R10_tie"]["cells"].items()))
    L.append(f"harness: {len(harness['reused_unchanged_sha256'])} reused files, {len(harness['box_binaries_sha256'])} box binaries")
    open(os.path.join(HERE, "predictions-e129.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
