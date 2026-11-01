#!/usr/bin/env python3
"""E109: write the frozen numbers, predictions-e109.json and predictions-e109.txt, from committed inputs only. Run before the claim; never after the data.

    python3 tools/claims-v3/e109/make_predictions_e109.py          # from anywhere

Inputs (all committed before E109): Q132(b)'s two one-number readings of int8 zeros' extra 0.61 W, recomputed here as its zeros/zeros_check.py computes them
(E78's S and op rates on this card, the fixed bench's per-op counts in counts-v2.json); M4's clocked-bit constant (predictions-e103.json); E78's own cells on
this card (the session tie); and E109's desk run of every arm through the RTL bench (desk/bench-arms.json: cycles, issued micro-ops, scratchpad reads,
register bits clocked, per op on one minion).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
load = lambda p: json.load(open(p))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

E78 = load(os.path.join(DD, "2026-10-31-e78-kinds-energy-matrix", "e78.json"))["items"]
CNT = load(os.path.join(DD, "2026-11-01-q132-rtl-bench", "counts-v2.json"))["rows"]
M4 = load(os.path.join(ROOT, "tools", "claims-v3", "kinds", "predictions-e103.json"))["models"]
BENCH = load(os.path.join(HERE, "desk", "bench-arms.json"))
B = BENCH["per_op"]

CLOCK_HZ, MINIONS = 600e6, 1024
NOM = CLOCK_HZ * MINIONS                      # minion-cycles per second
FMT = ("fp32", "int8")
CARD_CPO = {"fp32": 546.0, "int8": 318.0}     # E78's measured cycles per op (546.001, 318.000)
# the card's per-op cycles beyond the bench's FSM-limited op: the core's loop and the CSR write (E78's card cycles minus the bench's +period=1 cycles)
DELTA = {f: CARD_CPO[f] - B[f"base.{f}.zeros"]["cycles"] for f in FMT}
DUTY = {f: E78[f"{f}.zeros"]["rate"]["mean"] / (NOM / CARD_CPO[f]) for f in FMT}   # launch gaps: the measured rate against the nominal

# ---- Q132(b) section 14's two readings, recomputed from its inputs (zeros/zeros_check.py) --------------------------------------------------------------
rate0 = {f: E78[f"{f}.zeros"]["rate"]["mean"] for f in FMT}
S0 = {f: E78[f"{f}.zeros"]["S"]["mean"] for f in FMT}
reads0 = {f: CNT[f"{f}.zeros"]["mean"]["scp_reads"] * rate0[f] for f in FMT}
clk0 = {f: CNT[f"{f}.zeros"]["mean"]["ff"]["all"]["clocked"] * rate0[f] for f in FMT}
det = clk0["fp32"] * reads0["int8"] - clk0["int8"] * reads0["fp32"]
C_READS = (S0["fp32"] * reads0["int8"] - S0["int8"] * reads0["fp32"]) / det       # W per clocked bit per second (Q132(b): 0.060 fJ)
R_READ = (clk0["fp32"] * S0["int8"] - clk0["int8"] * S0["fp32"]) / det           # W per scratchpad read per second (5.93 pJ)
E_OP = (S0["int8"] - S0["fp32"]) / (rate0["int8"] - rate0["fp32"])              # W per op per second (770 pJ)
C_OPS = S0["fp32"] - E_OP * rate0["fp32"]                                        # 1.123 W
A_CLK = M4["float"]["coef_fJ"]["a_clocked"] * 1e-15                              # M4's clocked-bit price, as Q132(b) applied it to both formats (1.066 fJ)
GAP_E78 = S0["int8"] - S0["fp32"]

# ---- every arm: the RTL's counts, the card cycles they predict, and each reading's D over the format's zeros -------------------------------------------
ARMS = {"fp32": ("base", "m0", "k8", "r8", "m0k8"), "int8": ("base", "m0", "k8", "r8", "m0k8")}
ITEM15 = ("base.fp32.a_zeros_b_randn", "m0.fp32.a_zeros_b_randn", "base.fp32.a_nz_b_randn", "m0.fp32.a_nz_b_randn")


def arm_row(key, f):
    b = B[key]
    cyc = b["cycles"] + DELTA[f]
    rate = DUTY[f] * NOM / cyc
    return {"bench_cycles": b["cycles"], "card_cycles_pred": round(cyc, 2), "rate_pred": rate, "uops_per_op": b["uops"], "scp_reads_per_op": b["scp_reads"],
            "clocked_bits_per_op": b["ff_clocked_bits"], "edges_per_op": b["ff_present_bits"], "lane_edges_per_op": b["txfma_present"] + b["tima_present"],
            "b_half_lines_per_op": 2 * (8 if key.split(".")[0] in ("k8", "m0k8") else 16), "a_reads_per_op": b["scp_reads"] - 2 * (8 if key.split(".")[0] in ("k8", "m0k8") else 16)}


rows = {}
for f in FMT:
    for a in ARMS[f]:
        rows[f"{a}.{f}.zeros"] = arm_row(f"{a}.{f}.zeros", f)
for k in ITEM15:
    rows[k] = arm_row(k, "fp32")


def model(h, r):
    """S (W over idle) under a reading, at the arm's predicted rate."""
    if h == "H_reads":
        return R_READ * r["scp_reads_per_op"] * r["rate_pred"] + C_READS * r["clocked_bits_per_op"] * r["rate_pred"]
    if h == "H_ops":
        return C_OPS + E_OP * r["rate_pred"]
    if h == "H_bench":
        return A_CLK * r["clocked_bits_per_op"] * r["rate_pred"]
    raise KeyError(h)


HYP = ("H_reads", "H_ops", "H_bench")
pred_D = {}
for k, r in rows.items():
    f = k.split(".")[1]
    base = rows[f"base.{f}.zeros"]
    pred_D[k] = {h: model(h, r) - model(h, base) for h in HYP}

# ---- the registered quantities, each reading's frozen value ---------------------------------------------------------------------------------------------
def q(h):
    D = {k: pred_D[k][h] for k in pred_D}
    out = {}
    for f in FMT:
        rb, m0, k8, r8, mk = (rows[f"{a}.{f}.zeros"] for a in ARMS[f])
        U = -D[f"m0.{f}.zeros"]
        P = D[f"m0k8.{f}.zeros"] - D[f"m0.{f}.zeros"]
        dO = mk["rate_pred"] - m0["rate_pred"]
        e_op = P / dO
        R = D[f"r8.{f}.zeros"] - D[f"k8.{f}.zeros"]
        dB = r8["b_half_lines_per_op"] * r8["rate_pred"] - k8["b_half_lines_per_op"] * k8["rate_pred"]
        r_B = (R + e_op * (k8["rate_pred"] - r8["rate_pred"])) / dB
        U8 = D[f"k8.{f}.zeros"] - D[f"m0k8.{f}.zeros"]
        out[f] = {"U_w": U, "P_w": P, "e_op_pj": e_op * 1e12, "Q_w": D[f"k8.{f}.zeros"], "R_w": R, "r_B_pj": r_B * 1e12, "U8_w": U8,
                  "U8_minus_U_scaled_w": U8 - U * (k8["uops_per_op"] * k8["rate_pred"]) / (rb["uops_per_op"] * rb["rate_pred"])}
    G = model(h, rows["base.int8.zeros"]) - model(h, rows["base.fp32.zeros"]) + (C_OPS * 0 if h != "H_ops" else 0)
    O = {f: rows[f"base.{f}.zeros"]["rate_pred"] for f in FMT}
    G_lane = out["int8"]["U_w"] - out["fp32"]["U_w"]
    G_op = out["int8"]["e_op_pj"] * 1e-12 * O["int8"] - out["fp32"]["e_op_pj"] * 1e-12 * O["fp32"]
    out["gap"] = {"G_w": G, "G_lane_w": G_lane, "G_op_w": G_op, "G_rest_w": G - G_lane - G_op}
    t_plus = D["m0.fp32.a_zeros_b_randn"] - D["m0.fp32.zeros"]
    out["item15"] = {"R7_w": D["m0.fp32.a_nz_b_randn"] - D["m0.fp32.a_zeros_b_randn"], "T_plus_w": t_plus, "R8_w": D["base.fp32.a_zeros_b_randn"] - t_plus}
    return out


quant = {h: q(h) for h in HYP}

# ---- the registered rules -------------------------------------------------------------------------------------------------------------------------------
rules = {
    "R0_answer": {"what": "item 11's answer: which share of this session's gap G = S(int8.zeros) - S(fp32.zeros) carries at least half of it",
                  "shares": {"per_op": "G_op = e_op(int8) x O(int8) - e_op(fp32) x O(fp32), O = each format's op rate on zeros, e_op from rule R1",
                             "lanes": "G_lane = U(int8) - U(fp32), U = S(zeros) - S(m0.zeros): what issuing the micro-ops costs on zeros",
                             "per_time": "G_rest = G - G_op - G_lane: what neither moves - the A-word stream and B's reads of the scratchpad, the FSM's busy clocks, the rest"},
                  "line": "a share carries the gap if its 95% lower bound >= G/2 (G = this session's mean gap); if none does, MIXED; if two do (impossible unless one is negative), both are named",
                  "verdicts": ["PER-OP", "LANES", "PER-TIME", "MIXED"]},
    "R1_ops": {"what": "Q132(b)'s second reading, S = c + e x ops: per-op work makes the gap",
               "statistic": "e_op(f) = [D(m0k8.f.zeros) - D(m0.f.zeros)] / [rate(m0k8) - rate(m0)], per pass; G_op as in R0",
               "line": "PASS if G_op's 95% lower bound >= G/2; FAIL if its upper bound < G/2; else INCONCLUSIVE", "reading_e_op_pj": E_OP * 1e12},
    "R2_lanes": {"what": "the lanes (register clocking, the issued micro-op, int8's TenC read port): U(f) = -D(m0.f.zeros)",
                 "line": "LANES-CARRY if G_lane's 95% lower bound >= G/2; LANES-OPPOSE if its upper bound < 0 (the RTL count's direction: fp32's lanes clock more); else LANES-NEITHER",
                 "rtl_count_prediction": "H_bench: U(fp32) = %.3f W, U(int8) = %.3f W, G_lane = %.3f W (M4's a on the bench's clocked bits, the extrapolation Q132(b) made)" % (
                     quant["H_bench"]["fp32"]["U_w"], quant["H_bench"]["int8"]["U_w"], quant["H_bench"]["gap"]["G_lane_w"])},
    "R3_per_time": {"what": "the per-time side, where the A-word stream and B's reads are (Q132(b)'s first reading puts the gap here)",
                    "line": "PASS if G_rest's 95% lower bound >= G/2; FAIL if its upper bound < G/2; else INCONCLUSIVE"},
    "R4_b_reads": {"what": "B-line reuse: r8 against k8 in fp32, the same op rate within 3% and twice B's half-line reads per op",
                   "statistic": "r_B = {[D(r8) - D(k8)] + e_op x [rate(k8) - rate(r8)]} / [B/s(r8) - B/s(k8)], per pass, fp32",
                   "line": "PRICED if the 95% interval of r_B excludes 0 from above; NOT-RESOLVED if it includes 0; H_reads' value of this same statistic (its 5.93 pJ a read less the 3% of A reads a second r8 loses against k8, predicted_quantities.H_reads.fp32.r_B_pj) is named CONSISTENT if inside the interval, else INCONSISTENT",
                   "int8": "reported only: in int8 the RTL's count has r8 read A 13% less often a second than k8 (190 against 166 cycles at the same 96 A reads), so its contrast mixes A and B reads"},
    "R5_additive": {"what": "the lane side at K = 8 against K = 16: U8(f) = D(k8) - D(m0k8) against U(f) x the issued micro-ops' rate ratio",
                    "line": "PASS per format if the 95% interval of U8 - U x ratio lies inside [-0.15, +0.15] W; FAIL if it lies outside; else INCONCLUSIVE"},
    "R6_cycles": {"what": "the card's cycles per op for each arm against the RTL's: bench cycles (+period=1) + each format's DELTA (E78's card cycles minus the bench's base)",
                  "line": "PASS per arm if |median measured cycles per op - predicted| <= 2.0; else FAIL", "delta_cycles": DELTA,
                  "predicted": {k: r["card_cycles_pred"] for k, r in rows.items() if not k.startswith("base.")},
                  "check_on_committed_data": "the September fma-rowmask runs (row mask 0x00FF, 16 x 16, fp32) read 544.001 cycles on this card (docs/reports/data/2026-09-18-sparsity-aifoundry3/energy-*/results.json); the bench gives 536.2 + 7.8 = 544.0 for that mask (desk/bench-arms.txt does not list it; bench_arms_e109.py's run() with mask 0xff reproduces it)"},
    "R7_sign_unseen": {"what": "item 15: with no micro-op issued, A = -0 and A = +0 (both constant words; the B bytes identical) cost the same",
                       "statistic": "D(m0.fp32.a_nz_b_randn) - D(m0.fp32.a_zeros_b_randn)",
                       "line": "PASS if its 95% interval lies inside [-0.25, +0.25] W; FAIL if it lies outside; else INCONCLUSIVE"},
    "R8_gated_transport": {"what": "item 15: a gated lane's moving B costs only its transport (the RTL: on a gated slot B's random bytes change no counted register; desk/bench-arms.txt: a_zeros_b_randn's counts equal zeros' to the bit, issued and masked)",
                           "statistic": "D(fp32.a_zeros_b_randn) - T_plus, T_plus = D(m0.fp32.a_zeros_b_randn) - D(m0.fp32.zeros)",
                           "line": "PASS if its 95% interval lies inside [-0.25, +0.25] W; FAIL if it lies outside; else INCONCLUSIVE"},
    "R9_live_split": {"what": "item 15, reported (no verdict): where a live -0 lane with random B spends its watts on this card",
                      "statistics": {"T_minus": "D(m0.fp32.a_nz_b_randn) - D(m0.fp32.zeros): B's random bytes moving to the register files, no micro-op",
                                     "L_live": "D(fp32.a_nz_b_randn) - D(m0.fp32.a_nz_b_randn): the live lanes",
                                     "X": "L_live - D(anchor_pi): what B's random bytes cost inside a live lane beyond a constant lane (pi x pi)"},
                      "e93_context": "E93 priced a_nz_b_randn on aifoundry1 card 1 at 10.40 W (E88's constant lane 7.92 W + B's bus bits at E88's a + half E88's sign) and read 12.11 W: +1.72 W (E93 R5). E109 runs on another card, so it splits the tile, it does not re-price it"},
    "R10_tie": {"what": "the session against E78 on this card (one card, 600 MHz pinned, the same tiles and reduction)",
                "cells": {"fp32.randn D": [E78["fp32.randn"]["D"]["mean"], 0.6], "fp16.randn D": [E78["fp16.randn"]["D"]["mean"], 0.6],
                          "int8.full D": [E78["int8.full"]["D"]["mean"], 0.3], "anchor_pi D": [E78["anchor_pi"]["D"]["mean"], 0.5],
                          "fp32.a_zeros_b_randn D": [E78["fp32.a_zeros_b_randn"]["D"]["mean"], 0.25], "gap G (S)": [GAP_E78, 0.2]},
                "line": "PASS per cell if |this session's mean - E78's| <= its band; a failed cell labels every verdict, it removes none"},
}

pred = {
    "experiment": "E109", "question": "Q133, kinds page section 11 item 11 (int8 zeros' extra 0.61 W), with an arm for item 15 (a live zero on A)",
    "card": "aifoundry3 card 0, 600 MHz pinned (boot-time TDP 0), E78's frame",
    "sources": {"q132b_section14": "docs/reports/data/2026-11-01-q132-rtl-bench/README.md section 14; zeros/zeros_check.py",
                "e78": "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json", "m4": "tools/claims-v3/kinds/predictions-e103.json models.float.coef_fJ.a_clocked",
                "bench": "tools/claims-v3/e109/desk/bench-arms.json (bench_e109.sh, bench_arms_e109.py)"},
    "readings": {"H_reads": {"what": "Q132(b)'s first: S = c x clocked + r x reads", "r_pj_per_read": R_READ * 1e12, "c_fj_per_clocked_bit": C_READS * 1e15},
                 "H_ops": {"what": "Q132(b)'s second: S = c + e x ops", "e_pj_per_op": E_OP * 1e12, "c_w": C_OPS},
                 "H_bench": {"what": "the RTL count at M4's clocked-bit price, Q132(b)'s extrapolation (which says int8 - fp32 = -0.51 W at E78's cells)", "a_fj": A_CLK * 1e15}},
    "e78_gap_w": GAP_E78, "duty": DUTY, "delta_cycles": DELTA,
    "arms": rows, "predicted_D_w": pred_D, "predicted_quantities": quant, "rules": rules,
    "passes": [10910, 10911, 10912, 10913], "smoke_pass": 10901, "min_kept_passes": 3, "cap_card_minutes": 25, "queue_deadline_min": 23,
    "harness": {"reused_unchanged_sha256": {rel: sha(os.path.join(ROOT, rel)) for rel in (
        "tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json",
        "tools/claims-v3/kinds/e93/e93.json", "tools/claims-v3/kinds/e93/tiles/fp32/a_nz_b_randn.bin", "tools/claims-v3/lib.sh")}},
}
json.dump(pred, open(os.path.join(HERE, "predictions-e109.json"), "w"), indent=1)

L = ["E109 frozen numbers (make_predictions_e109.py)", "",
     f"Q132(b)'s readings, recomputed: r = {R_READ * 1e12:.3f} pJ a read with c = {C_READS * 1e15:.4f} fJ a clocked bit; e = {E_OP * 1e12:.1f} pJ an op with c = {C_OPS:.3f} W; "
     f"M4's a = {A_CLK * 1e15:.4f} fJ. E78's gap {GAP_E78:.3f} W. DELTA (card - bench cycles) {DELTA}; duty {DUTY}", "",
     f"{'arm':28s} {'bench':>7s} {'card':>7s} {'rate/1e9':>9s} {'uops':>5s} {'reads':>6s} {'clocked':>9s} | predicted D (W): H_reads   H_ops   H_bench"]
for k, r in rows.items():
    p = pred_D[k]
    L.append(f"{k:28s} {r['bench_cycles']:7.1f} {r['card_cycles_pred']:7.1f} {r['rate_pred'] / 1e9:9.4f} {r['uops_per_op']:5.0f} {r['scp_reads_per_op']:6.0f} "
             f"{r['clocked_bits_per_op']:9.0f} |                  {p['H_reads']:+.3f}  {p['H_ops']:+.3f}  {p['H_bench']:+.3f}")
L.append("")
for h in HYP:
    Q = quant[h]
    L.append(f"{h}: " + "; ".join(f"{f}: U {Q[f]['U_w']:+.3f} W, P {Q[f]['P_w']:+.3f} W, e_op {Q[f]['e_op_pj']:.0f} pJ, R {Q[f]['R_w']:+.3f} W, r_B {Q[f]['r_B_pj']:.2f} pJ, "
                                  f"U8-U' {Q[f]['U8_minus_U_scaled_w']:+.3f}" for f in FMT)
             + f"; gap G {Q['gap']['G_w']:+.3f} = lane {Q['gap']['G_lane_w']:+.3f} + op {Q['gap']['G_op_w']:+.3f} + rest {Q['gap']['G_rest_w']:+.3f}; "
             f"R7 {Q['item15']['R7_w']:+.3f}, R8 {Q['item15']['R8_w']:+.3f}")
open(os.path.join(HERE, "predictions-e109.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
