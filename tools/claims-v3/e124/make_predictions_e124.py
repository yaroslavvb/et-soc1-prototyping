#!/usr/bin/env python3
"""E124 (Q134): write predictions-e124.json, E124's frozen numbers, from E109's frozen file and committed card-1 and E109 results.

    python3 tools/claims-v3/e124/make_predictions_e124.py        # writes predictions-e124.json and predictions-e124.txt beside it

E124 is E109's registration (tools/claims-v3/e109/E109.md) replicated on aifoundry1 card 1. Everything E109's scorer reads from its frozen file
(readings, arms, predicted quantities, R6's predicted cycles) is copied UNCHANGED from predictions-e109.json; only R10's tie cells are replaced by card 1's
references (E82's e82.json, the E78 design on this card, and E93's e93.json for the a_nz_b_randn tile), and E124's card, passes, budget, reduction,
set-aside rule and added rules (Y1, Y2, Z) are added. The sha256 of every reused file is frozen in `harness`. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E109 = os.path.join(ROOT, "tools/claims-v3/e109")
D109 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e109-int8-zeros")
E82J = os.path.join(ROOT, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json")
E93J = os.path.join(ROOT, "docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json")
CARD_SCALE = 0.970          # E82 result 1: card 1 switches about 0.970x aifoundry3 across kinds and formats (median ratio 1.031)


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    P = json.load(open(os.path.join(E109, "predictions-e109.json")))
    e82, e93 = json.load(open(E82J)), json.load(open(E93J))
    s3 = json.load(open(os.path.join(D109, "scored-3pass.json")))
    ph = json.load(open(os.path.join(D109, "posthoc.json")))["three_passes_gate_lifted"]

    def gap(d):
        v = [d["per_pass"][str(p)]["int8.zeros"]["S"] - d["per_pass"][str(p)]["fp32.zeros"]["S"] for p in d["passes"]]
        return sum(v) / len(v), v

    g82, g82v = gap(e82)
    it82 = e82["items"]
    cells = {
        "fp32.randn D": [it82["fp32.randn"]["D"]["mean"], 0.6],
        "fp16.randn D": [it82["fp16.randn"]["D"]["mean"], 0.6],
        "int8.full D": [it82["int8.full"]["D"]["mean"], 0.3],
        "anchor_pi D": [it82["anchor_pi"]["D"]["mean"], 0.5],
        "fp32.a_zeros_b_randn D": [it82["fp32.a_zeros_b_randn"]["D"]["mean"], 0.25],
        "gap G (S)": [g82, 0.2],
        "fp32.a_nz_b_randn D": [e93["items"]["fp32.a_nz_b_randn"]["D"]["mean"], 0.5],
    }
    out = dict(P)
    out["experiment"] = "E124"
    out["question"] = ("Q134, kinds page section 11 item 11 (int8 zeros' extra 0.61 W) as it reads at 90e02fa93e9c: 'a replicate that scores, which needs "
                       "4-5 passes or a rule for a set-aside pass registered in advance' - E109's registered test on a second card, with item 15's live-zero arm")
    out["card"] = {"name": "aifoundry1-c1", "host": "aifoundry1", "device": 1, "lock": "/run/lock/etsoc-shire1.lock", "clock_mhz": 600,
                   "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}},
                   "what": "aifoundry1 card 1, 600 MHz in every sample since 25 Sep, TDP 65 W / threshold 65 C (read, never set); tree ~/nekko"}
    out["sources"] = dict(P["sources"], e109_registration="tools/claims-v3/e109/E109.md (predictions-e109.json, unchanged in every key the scorer reads)",
                          e109_results="docs/reports/data/2026-11-01-e109-int8-zeros/ (scored-3pass.json, posthoc.json: labelled, post hoc)",
                          e82="docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json (E78's design on this card; R10's references)",
                          e93="docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json (fp32.a_nz_b_randn on this card; R10's added cell)",
                          card_scale="E82 README result 1: median D(aifoundry3)/D(card 1) 1.031 over 32 kinds, so card 1 = 0.970 x aifoundry3")
    r10 = dict(P["rules"]["R10_tie"])
    r10["what"] = ("the session against E78's design on THIS card: E82 (aifoundry1 card 1, 31 Oct, e82.json: five kept passes, leak auto = 0.2414 W/C, "
                   "dips kept) for E109's six cells, with E109's bands, and E93's fp32.a_nz_b_randn (the same tile, this card, 1 Nov, dips removed, 0.2414) "
                   "as a seventh cell, +-0.5 W. score_e109.py names the reference field 'e78' (unchanged code); here it holds card 1's reference")
    r10["cells"] = cells
    r10["e82_gap_per_pass_w"] = g82v
    out["rules"] = dict(P["rules"], R10_tie=r10)
    out["e78_gap_w_aifoundry3"] = P["e78_gap_w"]
    out["card1_gap_w_e82"] = g82
    out["passes"] = [12410, 12411, 12412, 12413, 12414]
    out["smoke_pass"] = 12401
    out["min_kept_passes"] = 3
    out["cap_card_minutes"] = 30
    out.pop("queue_deadline_min", None)
    out["budget"] = {"card_minutes": 30, "anchor": "the claim post's time T0 (epoch seconds, E124_T0)", "budget_s": 1800, "reserve_s": 150,
                     "rule": "a pass starts only if now + projected <= T0 + budget_s - reserve_s and now + projected <= the deadline (2026-11-01 23:15 PST); "
                             "projected = the first estimate until a pass ends, then the longest measured pass; a pass in flight is never cut",
                     "first_estimate_s": 360, "deadline_pst": "2026-11-01 23:15",
                     "card1_pass_times": "E86's 34-run pass on this card (E112(a)): 320-334 s; E93's 42-run pass: 361-386 s; E109's 34-run pass on aifoundry3: 334-387 s",
                     "expected_passes": "4 (a fifth only if the passes run <= ~310 s)"}
    out["primary_reduction"] = {
        "code": "tools/claims-v3/e124/reduce_e124.py: reduce_e78.py unchanged, E109's items (e109_common.install_for_reduce, as reduce_e109.py), card 1's "
                "config gate (a 65/65 read handed to E78's gate as the 0/65 it accepts, E82's substitution), card 1's board-meter dips removed (E82 A2: "
                "board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W; E88's, E91's and E93's primary on this card), leakage slope frozen at E82's own",
        "leak_w_per_c": 0.2414, "dips": "removed", "gates": "E78's, unchanged",
        "arms_reported": {"dips_kept": ["--keep-dips", "--leak", "0.2414"], "auto": ["--leak", "auto"]},
        "why_not_e109s_auto": "E109 on aifoundry3 used E78's 'auto'; on this card E91's per-session fit (0.422 W/C) moved fp32 random by -0.6 W and broke its tie, so "
                              "E93 froze E82's 0.2414 for this card; E124 follows E93 and reports 'auto' as an arm"}
    out["set_aside_rule"] = {
        "why": "E109 kept 2 of 3 passes and scored nothing: E78's random-anchor span gate (random_range_w 1.0 W) set aside a pass whose E109 statistics were "
               "intact (its zeros anchors spanned 0.053 and 0.054 W). The random anchors enter no E109 statistic except R10's two random cells. Card 1's "
               "meter dips set aside 2 of 7 E82 passes by the same gate.",
        "rule": "the primary reduction applies E78's pass gates unchanged and scores if it keeps >= 3 passes. If it keeps fewer, the rules are scored on "
                "reduce_e124.py --relax-random (GATES['random_range_w'] 1.0 -> 99 W, E109's posthoc_e109.py change, here registered in advance): a pass set "
                "aside ONLY by that gate is restored; a pass set aside by any other gate stays out. Verdicts so scored are registered and labelled 'scored "
                "under the set-aside rule'. Fewer than 3 passes after that: NOT SCORED. The relaxed reduction is always reported beside the primary. No "
                "pass is added after any reduction is read; no pass is chosen after the fact.",
        "relaxed_gate": {"random_range_w": 99.0}}
    y1_pred = ph["S_m0_gap"]["mean"] * CARD_SCALE
    out["e109_reference"] = {
        "what": "E109's labelled three-pass values (aifoundry3, post hoc: E78's random-anchor gate lifted), for the replication table; scored-3pass.json, posthoc.json",
        "card_scale": CARD_SCALE,
        "quantities": {
            "G": s3["gap"]["G"], "G_lane": s3["gap"]["G_lane"], "G_op": s3["gap"]["G_op"], "G_rest": s3["gap"]["G_rest"],
            "U_fp32": s3["quantities"]["fp32"]["U"], "U_int8": s3["quantities"]["int8"]["U"],
            "e_op_fp32_pj": s3["quantities"]["fp32"]["e_op_pj"], "e_op_int8_pj": s3["quantities"]["int8"]["e_op_pj"],
            "r_B_fp32_pj": s3["quantities"]["fp32"]["r_B_pj"], "R7": s3["item15"]["R7"], "R8": s3["item15"]["R8"], "T_minus": s3["item15"]["T_minus"],
            "S_m0_gap": ph["S_m0_gap"], "S_m0_fp32": ph["S_m0_fp32"], "S_m0_int8": ph["S_m0_int8"], "U_per_edge_fp32_fj": ph["U_per_edge_fp32_fj"],
            "U_per_edge_int8_fj": ph["U_per_edge_int8_fj"], "read_ceiling_fp32_pj": ph["read_ceiling_fp32_pj"],
            "read_ceiling_int8_pj": ph["read_ceiling_int8_pj"], "live_over_constant_w": ph["live_over_constant_w"]},
        "verdicts": {k: (v.get("verdict") if isinstance(v, dict) and "verdict" in v else None) for k, v in s3["rules"].items()},
        "r5": {f: s3["rules"]["R5_additive"][f]["verdict"] for f in ("fp32", "int8")}}
    out["expected_if_e109_carries"] = {
        "R0_answer": "PER-TIME", "R1_ops": "FAIL", "R2_lanes": "LANES-OPPOSE", "R3_per_time": "PASS", "R4_b_reads": "NOT-RESOLVED; CONSISTENT",
        "R5_additive": {"fp32": "INCONCLUSIVE", "int8": "PASS"}, "R6_cycles": "PASS x10", "R7_sign_unseen": "PASS", "R8_gated_transport": "FAIL",
        "R10_tie": "PASS x7", "Y1": "PASS", "Y2": "PASS", "Z": "REPLICATES",
        "numbers": {"G": round(g82, 3), "G_rest": round(s3["gap"]["G_rest"]["mean"] * CARD_SCALE, 3), "G_lane": round(s3["gap"]["G_lane"]["mean"] * CARD_SCALE, 3),
                    "S_m0_gap": round(y1_pred, 3), "U_fp32": round(s3["quantities"]["fp32"]["U"]["mean"] * CARD_SCALE, 3),
                    "U_int8": round(s3["quantities"]["int8"]["U"]["mean"] * CARD_SCALE, 3)},
        "note": "E109's labelled three-pass readings x card 1's 0.970 scale (G is E82's own on this card); these are expectations, not lines: the rules' lines are"
                " E109's, relative to this session's own G"}
    out["added_rules"] = {
        "Y1": {"what": "E109 result 3 as a registered test: with no micro-op issued (mask 0x0000), int8's TensorFMA loop costs more over idle than fp32's",
               "statistic": "N = S(m0.int8.zeros) - S(m0.fp32.zeros), per kept pass (posthoc_check_e109.reading's S_m0_gap on E124's reduction)",
               "predicted_w": y1_pred, "line_w": round(y1_pred / 2, 2),
               "verdict": "PASS if N's 95% lower bound >= line_w; FAIL if its upper bound < line_w; else INCONCLUSIVE"},
        "Y2": {"what": "E109 result 1 as a registered test: the ops reading's per-op price is excluded in both formats",
               "statistic": "e_op(fp32), e_op(int8) from score_e109.py (rule R1's e_op_pj)", "line_pj": P["readings"]["H_ops"]["e_pj_per_op"],
               "verdict": "PASS if both 95% upper bounds < line_pj; FAIL if either 95% lower bound >= line_pj; else INCONCLUSIVE"},
        "Z": {"what": "E109's labelled answer on a second card: the gap is per-time, not per-op work and not the lanes",
              "verdict": "REPLICATES if R0 PER-TIME and R1 FAIL and R2 LANES-OPPOSE and R3 PASS; CONTRADICTS if R0 names PER-OP or LANES, or R1 PASS, or R2 "
                         "LANES-CARRY, or R3 FAIL; else PARTIAL"},
        "reported": "posthoc_check_e109.reading() on E124's scored reduction (no verdict): S over idle of the no-issue loops, the per-read ceilings, U per "
                    "register-bit clock edge and per enabled bit with int8/fp32 paired by pass, item 15's live step over pi; each quantity beside e109_reference"}
    reuse = ["tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json",
             "tools/claims-v3/kinds/e93/e93.json", "tools/claims-v3/kinds/e93/tiles/fp32/a_nz_b_randn.bin", "tools/claims-v3/lib.sh",
             "tools/claims-v3/e109/e109_common.py", "tools/claims-v3/e109/run_e109.py", "tools/claims-v3/e109/block_e109.sh",
             "tools/claims-v3/e109/smoke_gate_e109.py", "tools/claims-v3/e109/score_e109.py", "tools/claims-v3/e109/posthoc_check_e109.py",
             "tools/claims-v3/e109/predictions-e109.json", "tools/claims-v3/e109/desk/bench-arms.json", "tools/claims-v3/e109/sp109/CMakeLists.txt",
             "tools/claims-v3/e109/sp109/sparsity_args.h", "tools/claims-v3/e109/sp109/kernel/sparsity.c", "tools/claims-v3/e109/sp109/host/main.cpp"]
    out["harness"] = {"reused_unchanged_sha256": {rel: sha(rel) for rel in reuse},
                      "what": "every file E124 runs or reads that it did not write, byte-identical to these hashes; check_e124.py refuses on any difference "
                              "(session_e124.sh runs it before any device opens; reduce_e124.py checks the same list)"}
    json.dump(out, open(os.path.join(HERE, "predictions-e124.json"), "w"), indent=1)
    L = ["E124 frozen numbers (make_predictions_e124.py)", "",
         f"R10's tie cells (card 1): " + "; ".join(f"{k} {v[0]:.4f} +- {v[1]}" for k, v in cells.items()),
         f"E82's gap per pass on this card: {', '.join(f'{x:.3f}' for x in g82v)} (mean {g82:.4f} W)",
         f"Y1 predicted N = {y1_pred:.3f} W (E109's {ph['S_m0_gap']['mean']:.3f} x {CARD_SCALE}); line {round(y1_pred / 2, 2)} W",
         f"Y2 line {P['readings']['H_ops']['e_pj_per_op']:.1f} pJ an op",
         f"passes {out['passes']}, smoke {out['smoke_pass']}, min kept {out['min_kept_passes']}, budget {out['budget']['budget_s']} s from the claim, reserve "
         f"{out['budget']['reserve_s']} s, first estimate {out['budget']['first_estimate_s']} s",
         "expected if E109's labelled readings carry: " + json.dumps({k: v for k, v in out["expected_if_e109_carries"].items() if k != "note"})]
    open(os.path.join(HERE, "predictions-e124.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
