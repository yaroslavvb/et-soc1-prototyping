#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E102 (Q132): write predictions-e102.json, E102's freeze, from committed sources only. Every number is read from the file it names, never retyped.

    /usr/bin/python3 tools/claims-v3/kinds/make_predictions_e102.py      # writes predictions-e102.json

For every tile, a predicted step over its own zero, in board watts on aifoundry1 card 1, from each of (all frozen here, before any E102 data exist):
  all_in_list       the published all-in step at that position: E65 (fp32 B), E67 (fp32 A), E79 (fp16 B and A), each over E82's card scale. All-in items only.
  ratio_hypothesis  what the kinds page implies: a balanced price is the published all-in price over E79's measured ratio at its one position (7.0 in fp32, 5.6 in fp16). Balanced items only.
  e79_measured      E79's own measured step where it ran this item, over the card scale. int8: at no temperature term (E79's runs.csv, p_raw minus h8q in each pass: E102.md says why), and a mask as the sum of its singles.
  bench_map         the RTL bench (Q132(b), core-et's vpu_top, -fno-dfg, counts committed beside E102's data): D = rate x (k x merged-net toggles + a x clocked register bits), with E92's frozen k and a, fitted
                    on E78's fp32 and fp16 kinds alone, nets_map (that file's primary), over the card scale. bench_hier2: the other merge.
  bench_int8fit     int8 only: the same form, k and a fitted on E78's int8 kinds, since the frozen pair was fitted on floats.
  e88               E88's frozen four prices on this card (rpath/e88.json).
  e88_flops         e88 plus E92's one price per flop-bit change on the adder (predictions-e92.json), fp32 and fp16, with C = fl((n-1) S), make_e88's and make_e92's own start, which those files say is exact for integer and absorbed designs.
  e88_flops_exact   the same two models from counts on the REAL accumulators (make_e102.exact_counts, accum.c): the C read, result bus, store and flops change; the operand and product counts do not.
"""
import csv
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
DATA = "docs/reports/data/2026-11-01-e102-balanced-bit-prices"
E102_JSON = f"{K}/e102/e102.json"
BENCH = f"{DATA}/bench/counts-e102.json"
BACKTEST = f"{DATA}/bench/backtest-hl-hlp.json"
BENCH_PRED = "docs/reports/data/2026-11-01-q132-rtl-bench/e92-bench-prediction.json"
BENCH_KINDS = "docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json"
E65_HL = "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json"
E67_HL = "docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json"
E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E79_JSON = "docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/hlp.json"
E79_RUNS = "docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/runs.csv"
E82_JSON = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json"
E82_NODIPS = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json"
E82_SCORED = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json"
E88_FIT = "tools/claims-v3/rpath/e88.json"
E92_PRED = f"{K}/predictions-e92.json"
E93_RUNS = "docs/reports/data/2026-11-01-e93-zero-gate-silicon/runs.csv"
REUSED = ("tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json")
BOX_FILES = tuple(f"{K}/{f}" for f in ("e102_common.py", "run_e102.py", "reduce_e102.py", "block_e102.sh", "queue_e102.sh", "run_e102.sh", "make_e102.py"))
DESK_FILES = tuple(f"{K}/{f}" for f in ("score_e102.py", "collect_e102.sh", "selftest_e102.py"))
RATIO = {"fp32": 7.0, "fp16": 5.6}       # E79 result 5's measured per-bit ratios (its README, scored.json's order probe), at fp32 bit 22 and fp16 bit 9


def rp(p):
    return os.path.join(ROOT, p)


def sha(p):
    return hashlib.sha256(open(rp(p), "rb").read()).hexdigest()


def load(p):
    return json.load(open(rp(p)))


def e79_int8_raw():
    """E79's int8 B `kg` steps with no temperature term: p_raw minus h8q in each kept pass of block B (7920-7923), mean over passes. E79's committed runs.csv."""
    rows = list(csv.DictReader(open(rp(E79_RUNS))))
    out = {}
    for j in range(8):
        d = []
        for p in ("7920", "7921", "7922", "7923"):
            x = [float(r["p_raw"]) for r in rows if r["pass"] == p and r["item"] == f"b8k_{j}"]
            z = [float(r["p_raw"]) for r in rows if r["pass"] == p and r["item"] == "h8q"]
            if x and z:
                d.append(x[0] - z[0])
        out[j] = {"dW": float(np.mean(d)), "per_pass": [round(v, 4) for v in d]}
    return out


def noise_from_e93():
    """What a run of a low-power tile reads from run to run on this card: E93's three reads of each type's zeros per pass, the middle read off the straight line through the other two (over sqrt(1.5)). Committed."""
    rows = [r for r in csv.DictReader(open(rp(E93_RUNS))) if r["item"] in ("fp32.zeros", "fp16.zeros", "int8.zeros") and float(r.get("fail") or 0) == 0]
    res = {"p_raw": [], "rail_raw": []}
    for key in res:
        for it in ("fp32.zeros", "fp16.zeros", "int8.zeros"):
            for p in sorted({r["pass"] for r in rows}):
                rr = sorted((r for r in rows if r["pass"] == p and r["item"] == it), key=lambda r: float(r["t0_ms"]))
                if len(rr) != 3:
                    continue
                t = [float(r["t0_ms"]) for r in rr]
                y = [float(r[key]) for r in rr]
                res[key].append((y[1] - (y[0] + (y[2] - y[0]) * (t[1] - t[0]) / (t[2] - t[0]))) / 1.5 ** 0.5)
    return {k: round(float(np.sqrt(np.mean(np.square(v)))), 4) for k, v in res.items()}


def half_width(sigma, n, zeros_each, t):
    return t * sigma * (1 + 1.0 / zeros_each) ** 0.5 / n ** 0.5


def main():
    tiles = load(E102_JSON)["tiles"]
    bench = load(BENCH)["rows"]
    bp = load(BENCH_PRED)["variants"]
    kinds = load(BENCH_KINDS)["rows"]
    e78 = load(E78_JSON)["items"]
    e82 = load(E82_JSON)["items"]
    e82n = load(E82_NODIPS)["items"]
    e88 = load(E88_FIT)["fit"]
    e92 = load(E92_PRED)["models"]
    e65 = load(E65_HL)["cards"]["aifoundry3"]
    e67 = load(E67_HL)["cards"]["aifoundry3"]
    e79 = load(E79_JSON)["cards"]["aifoundry3"]
    scale = load(E82_SCORED)["cross_card"]["primary"]["x3"]["per_type_median"]
    rate = {t: e82[f"{t}.randn" if t != "int8" else "int8.full"]["rate"]["mean"] for t in ("fp32", "fp16", "int8")}
    f_w = e92["f_w_per_flop_bit_per_op"]
    i8raw = e79_int8_raw()
    noise = noise_from_e93()

    # the int8 fit: the same form on E78's int8 kinds, rate x (k nets_map + a clocked)
    X, y = [], []
    z = kinds["int8.zeros"]["mean"]
    for name, v in kinds.items():
        if v["type"] != "int8" or v["kind"] == "zeros":
            continue
        m = v["mean"]
        r = e78[name]["rate"]["mean"]
        X.append([(m["vpu"]["nets_map"] - z["vpu"]["nets_map"]) * r, (m["ff"]["all"]["clocked"] - z["ff"]["all"]["clocked"]) * r])
        y.append(e78[name]["D"]["mean"])
    X, y = np.array(X), np.array(y)
    sc = X.max(axis=0)
    b8 = np.linalg.lstsq(X / sc, y, rcond=None)[0] / sc
    int8fit = {"k_fJ_per_net_toggle": float(b8[0]) * 1e15, "a_fJ_per_clocked_bit": float(b8[1]) * 1e15, "fit_rms_w_on_e78": float(np.sqrt(((y - X @ b8) ** 2).mean())), "n_fit": len(y)}

    def bench_w(name, var):
        v = bp[var]
        m = bench[name]["mean"]
        return (m["vpu"][var] * v["k_fJ_per_net_toggle"] + m["ff"]["all"]["clocked"] * v["a_fJ_per_clocked_bit"]) * 1e-15 * rate[tiles[name]["type"]] / scale[tiles[name]["type"]]

    def x88(name):
        e = tiles[name]
        s = e["stream"]
        return np.array([s["live_frac"], e["stats"]["bus_bits_per_op"], s["prod"], s["res_bits_per_op"]], float)

    def x88_exact(name):
        e = tiles[name]
        s_ = e["stream"]
        return np.array([s_["live_frac"], e["stats"]["bus_bits_per_op"], s_["prod"], e["exact"]["res_bits_per_op"]], float)

    positions = {}
    for name, e in tiles.items():
        ty, lay = e["type"], e["layout"]
        pos = {"block": e["block"], "layout": lay, "side": e["side"], "bit": e["bit"], "mask": e["mask"], "zero": e["zero"], "designed_flips_per_op": e["designed_flips_per_op"],
               "flops": e.get("exact", {}).get("flops"), "flops_from_fl_nS": e.get("sign", {}).get("flops"), "alt": e.get("exact", {}).get("N_alt1"), "stream": e["stream"], "exact": e.get("exact"), "vpu_nets_map": bench[name]["mean"]["vpu"]["nets_map"],
               "by_stage_vpu_map": bench[name]["mean"]["vpu"].get("by_stage")}
        if lay != "zero":
            zn = e["zero"]
            p = {}
            j = e["bit"]
            flips = e["designed_flips_per_op"]
            p["bench_map"] = bench_w(name, "nets_map") - bench_w(zn, "nets_map")
            p["bench_hier2"] = bench_w(name, "nets_hier2") - bench_w(zn, "nets_hier2")
            if ty == "int8":
                m, mz = bench[name]["mean"], bench[zn]["mean"]
                p["bench_int8fit"] = ((m["vpu"]["nets_map"] - mz["vpu"]["nets_map"]) * b8[0] + (m["ff"]["all"]["clocked"] - mz["ff"]["all"]["clocked"]) * b8[1]) * rate["int8"] / scale["int8"]
            p["e88"] = float((x88(name) - x88(zn)) @ np.array(e88[ty]["coef"]))
            if ty != "int8":
                p["e88_flops"] = p["e88"] + f_w * (e["sign"]["flops"] - tiles[zn]["sign"]["flops"])
                p["e88_flops_exact"] = float((x88_exact(name) - x88_exact(zn)) @ np.array(e88[ty]["coef"])) + f_w * (e["exact"]["flops"] - tiles[zn]["exact"]["flops"])
            s = scale[ty]
            if ty == "fp32":
                ref65 = e65["bits"][str(j)]["dW"]
                ref67 = e67["a_bits"][str(j)]["dW"]
                if lay == "bj":
                    p["all_in_list"] = ref65 / s
                if lay == "aj":
                    p["all_in_list"] = ref67 / s
                if lay == "bp":
                    p["ratio_hypothesis"] = ref65 / s * (flips / 4096.0) / RATIO["fp32"]
                if lay == "ap":
                    p["ratio_hypothesis"] = ref67 / s * (flips / 2048.0) / RATIO["fp32"]
                if name in ("fp32.bj_22", "fp32.bp_22"):
                    k79 = "fp32_b" if lay == "bj" else "fp32_b_jgp"
                    p["e79_measured"] = e79["prices"][k79]["22"]["dW"] / s
            if ty == "fp16":
                b79 = e79["prices"]["fp16_b"][str(j)]["dW"]
                a79 = e79["prices"]["fp16_a"][str(j)]["dW"]
                if lay == "bj":
                    p["all_in_list"] = b79 / s
                    p["e79_measured"] = b79 / s
                if lay == "aj":
                    p["all_in_list"] = a79 / s
                    p["e79_measured"] = a79 / s
                if lay == "bp":
                    p["ratio_hypothesis"] = b79 / s * (flips / 8192.0) / RATIO["fp16"]
                    if j == 9:
                        p["e79_measured"] = e79["prices"]["fp16_b_jgp"]["9"]["dW"] / s
                if lay == "ap":
                    p["ratio_hypothesis"] = a79 / s * (flips / 4096.0) / RATIO["fp16"]
            if ty == "int8":
                bits = [i for i in range(8) if int(e["mask"], 16) >> i & 1]
                p["e79_measured"] = sum(i8raw[i]["dW"] for i in bits) / s
            pos["pred_w"] = {k: round(float(v), 4) for k, v in p.items()}
            pos["pred_fJ"] = {k: round(float(v) / (flips * rate[ty]) * 1e15, 1) for k, v in p.items()}
        positions[name] = pos

    # ---- the resolution this design can reach, per block and arm, from E93's noise on this card
    sig_board, sig_rail = noise["p_raw"], noise["rail_raw"]
    T95 = {3: 4.303, 4: 3.182, 5: 2.776}
    res = {}
    for block, n, nz in (("G", 3, 2), ("T", 4, 3), ("I", 5, 4)):
        for arm, sg in (("board", sig_board), ("rail", sig_rail)):
            res[f"{block}.{arm}"] = {"passes": n, "own_zero_reads": nz, "sigma_w": sg, "half_width_w": round(half_width(sg, n, nz, T95[n]), 3)}
    flips_s = {"fp32 B": 3968 * rate["fp32"], "fp32 A": 1920 * rate["fp32"], "int8 single": 1024 * rate["int8"], "int8 ff": 8192 * rate["int8"], "int8 4 bits": 4096 * rate["int8"], "int8 3 bits": 3072 * rate["int8"]}
    resf = {"fp32 B balanced (T)": {a: round(res[f"T.{a}"]["half_width_w"] / flips_s["fp32 B"] * 1e15, 1) for a in ("board", "rail")},
            "fp32 A balanced (T)": {a: round(res[f"T.{a}"]["half_width_w"] / flips_s["fp32 A"] * 1e15, 1) for a in ("board", "rail")},
            "int8 single bit (I)": {a: round(res[f"I.{a}"]["half_width_w"] / flips_s["int8 single"] * 1e15, 1) for a in ("board", "rail")},
            "int8 3-bit mask, per bit (I)": {a: round(res[f"I.{a}"]["half_width_w"] / flips_s["int8 3 bits"] * 1e15, 1) for a in ("board", "rail")},
            "int8 4-bit mask, per bit (I)": {a: round(res[f"I.{a}"]["half_width_w"] / flips_s["int8 4 bits"] * 1e15, 1) for a in ("board", "rail")},
            "int8 ff, per bit (I)": {a: round(res[f"I.{a}"]["half_width_w"] / flips_s["int8 ff"] * 1e15, 1) for a in ("board", "rail")}}

    # ---- the ties to E79 (board), carried to this card
    s32, s16 = scale["fp32"], scale["fp16"]
    b22 = e79["prices"]["fp32_b"]["22"]["fJ"] / s32
    p22 = e79["prices"]["fp32_b_jgp"]["22"]["fJ"] / s32
    b9 = e79["prices"]["fp16_b"]["9"]["fJ"] / s16
    p9 = e79["prices"]["fp16_b_jgp"]["9"]["fJ"] / s16

    reg = {
        "experiment": "E102", "title": "single-bit prices in a balanced layout, the A side, and int8's B side (aifoundry1 card 1, 600 MHz)",
        "request": "Q132, the first half of item 12 of the kinds page's section 11", "date": "2026-11-01", "registration": f"{K}/E102.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600, "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "inputs_frozen": {k: {"path": v, "sha256": sha(v)} for k, v in (("e102_json", E102_JSON), ("bench_counts", BENCH), ("bench_backtest", BACKTEST), ("bench_prediction", BENCH_PRED), ("bench_kinds", BENCH_KINDS),
                                                                         ("e65", E65_HL), ("e67", E67_HL), ("e78", E78_JSON), ("e79", E79_JSON), ("e79_runs", E79_RUNS), ("e82", E82_JSON), ("e82_nodips", E82_NODIPS),
                                                                         ("e82_scored", E82_SCORED), ("e88_fit", E88_FIT), ("e92_predictions", E92_PRED), ("e93_runs", E93_RUNS))},
        "harness": {"reused_unchanged_sha256": {r: sha(r) for r in REUSED}, "e102_files_sha256": {r: sha(r) for r in BOX_FILES},
                    "desk_files_sha256": {r: sha(r) for r in DESK_FILES if os.path.exists(rp(r))}, "e102_json_sha256": sha(E102_JSON)},
        "plan": {"smoke": 10201, "sequence": [10210, 10220, 10221, 10230, 10211, 10222, 10231, 10212, 10223, 10232, 10233, 10234],
                 "blocks": {"G": "E78's protocol, launch 58 C after 59 C, 2 s quiet, 41 runs", "T": "a float train, no heater, 0.2 s between runs, 56 runs", "I": "an int8 train, 25 runs"},
                 "passes_planned": {"G": 3, "T": 4, "I": 5}, "reduction_primary": "dips removed (E82 A2), leak 0.2414 (E82's) in block G; no temperature term in the trains"},
        "card_budget": {"card_minutes_about": 57, "queue_budget_s": 3400, "queue_deadline": "2026-11-01 07:00 PST", "every_run_ends_by": "07:15 PST",
                        "first_estimates_s": {"G": 440, "T": 320, "I": 150}},
        "analysis": {"primary_arm_float": "rail", "primary_arm_int8": "rail", "min_passes": 3, "fp32_mantissa_positions": [0, 6, 11, 16, 20, 22],
                     "rate_ops_per_s": rate, "rail_over_board": 0.81, "rail_over_board_source": "E79 result 2, median over its steps of 1 W or more",
                     "gates": {"train_zero_mid_departure_rail_w": 0.25}, "card_scale": {"per_type": scale, "source": f"{E82_SCORED} cross_card.primary.x3.per_type_median"},
                     "noise_from_e93_w": noise, "resolution_half_width_w": res, "resolution_half_width_fJ": resf},
        "bench": {"source": "rtl-sim/fma_toggle_v2, core-et@b38a1a31, -fno-dfg, the Q132(b) bench", "variants": {k: {x: bp[k][x] for x in ("k_fJ_per_net_toggle", "a_fJ_per_clocked_bit", "fit_rms_w_on_e78")} for k in ("nets_map", "nets_hier2")},
                  "int8_fit": int8fit, "functional_check_mismatches": max(v["mean"]["check_mismatch"] for v in bench.values())},
        "positions": positions,
        "session_tie": {"reference": f"{E82_NODIPS} items.<cell>.D.mean (dips removed, as E102's primary)",
                        "cells": {c: {"ref_w": round(e82n[c]["D"]["mean"], 4), "band_w": b} for c, b in (("fp32.randn", 0.5), ("fp16.randn", 0.5), ("anchor_pi", 0.5), ("int8.full", 0.25))}},
        "rules": {
            "E102-R1": {"what": "fp32 B: does the per-bit ratio all-in / balanced stay near 5-7x across the mantissa?", "expected": "POSITION",
                        "constant_low_lower_bound_at_least": 4.0, "position_low_upper_bound_below": 4.0, "position_top_lower_bound_at_least": 4.0,
                        "rule": "CONSTANT if the ratio's lower bound is >= 4 at bits 0 and 6; POSITION if its upper bound is < 4 at both and its lower bound >= 4 at bit 22; else INCONCLUSIVE"},
            "E102-R2": {"what": "fp32 A: the same on the A side", "expected": "POSITION", "constant_low_lower_bound_at_least": 4.0, "position_low_upper_bound_below": 4.0, "position_top_lower_bound_at_least": 1.2,
                        "rule": "CONSTANT if the ratio's lower bound is >= 4 at bits 0 and 6; POSITION if its upper bound is < 4 at both and its lower bound >= 1.2 at bit 22; else INCONCLUSIVE"},
            "E102-R3": {"what": "fp32 exponent: which layout is dearer (E79 result 1b's open question)", "expected": "INVERTED", "positions": [23, 27], "composite_ratio_lower_bound_at_least": 3.0,
                        "rule": "on the B side: INVERTED if balanced - all-in has a lower bound > 0 W at both bits; COMPOSITE if the ratio's lower bound is >= 3 at both; else INCONCLUSIVE. The A side is reported beside it."},
            "E102-R4": {"what": "the sign: the balanced layout makes the adder alternate (E92), so it is the dear one", "expected": "CONFIRMED", "min_w": {"fp32 B": 1.0, "fp32 A": 0.5, "fp16 B": 1.0}, "refuted_below_w": 0.3,
                        "rule": "per list: CONFIRMED if balanced - all-in has a lower bound >= its floor; REFUTED if its upper bound is < 0.3 W; else INCONCLUSIVE. All three CONFIRMED confirms the rule; any REFUTED refutes it."},
            "E102-R5": {"what": "the ties to E79's numbers, board arm, gate protocol, carried by E82's scale",
                        "cells": {"fp32 bj_22": {"kind": "price", "block": "G", "item": "fp32.bj_22", "value_e79_scaled": round(b22, 1), "band": [round(b22 * 0.75, 1), round(b22 * 1.25, 1)]},
                                  "fp32 bp_22": {"kind": "price", "block": "G", "item": "fp32.bp_22", "value_e79_scaled": round(p22, 1), "band": [round(p22 * 0.5, 1), round(p22 * 1.5, 1)]},
                                  "fp16 bj_9": {"kind": "price", "block": "G", "item": "fp16.bj_9", "value_e79_scaled": round(b9, 1), "band": [round(b9 * 0.75, 1), round(b9 * 1.25, 1)]},
                                  "fp16 bp_9": {"kind": "price", "block": "G", "item": "fp16.bp_9", "value_e79_scaled": round(p9, 1), "band": [round(p9 * 0.5, 1), round(p9 * 1.5, 1)]},
                                  "fp32 ratio at 22": {"kind": "ratio", "block": "G", "top": "fp32.bj_22", "bot": "fp32.bp_22", "value_e79": 7.0, "band": [3.5, 14.0]},
                                  "fp16 ratio at 9": {"kind": "ratio", "block": "G", "top": "fp16.bj_9", "bot": "fp16.bp_9", "value_e79": 5.6, "band": [2.8, 11.2]}},
                        "rule": "per cell: CONFIRMED if the interval lies inside the band, REFUTED if wholly outside, else INCONCLUSIVE; any REFUTED refutes the rule"},
            "E102-R6": {"what": "the train reads what the gate reads: four items in both protocols, pooled per pass", "items": ["fp32.bp_22", "fp32.ap_22", "fp16.bp_9", "fp16.ap_9"], "band_w": {"board": 0.30, "rail": 0.15},
                        "rule": "the four items' mean step in the trains minus the same in the gate, inside +-0.15 W on the rail: CONFIRMED; wholly outside: REFUTED, and every train price carries that caveat; else INCONCLUSIVE. Item by item is reported beside it."},
            "E102-R7": {"what": "what a composite is: at E92's frozen price per flop bit, the adder's flops carry a share of the all-in excess", "expected": "CONFIRMED", "positions": [16, 20, 22], "fJ_per_flop_bit": e92["f_fj_per_flop_bit"], "share_band": [0.15, 0.50],
                        "rule": "excess = step(bj) - (flips bj / flips bp) step(bp), board arm; share = (the same difference of the flop count, make_e92's reading on the real accumulators) x 6.68 fJ x rate / excess. CONFIRMED if the share is in [0.15, 0.50] at all three, REFUTED if outside at all three, else INCONCLUSIVE"},
            "E102-R8": {"what": "int8 B's level: bk_ff, all eight bits, per flipped bit", "expected": "open: E79's list with no temperature term says E79-LEVEL (55 fJ board), the bench says BENCH-LEVEL (16 at the float coefficients, 31 at its int8 fit)",
                        "e79_level_lower_bound_at_least_fJ": {"rail": 35, "board": 43}, "bench_level_upper_bound_below_fJ": {"rail": 35, "board": 43},
                        "rule": "BOUND if the interval contains zero (below this design's resolution, and that is the result); E79-LEVEL if the lower bound is >= 35 rail-fJ (43 board); BENCH-LEVEL if the upper bound is < 35 (43); else RESOLVED-BETWEEN"},
            "E102-R9": {"what": "int8 B's odd/even shape (E79 result 4b): the odd magnitude bits 1,3,5 against the even 0,2,4 (three bits each)", "expected": "open: E79's list with no temperature term says SHAPE (+0.25 W on the rail), the bench says FLAT (0.00 W)", "band_w": {"rail": 0.10, "board": 0.12},
                        "rule": "bk_2a - bk_15, watts, paired: SHAPE if the lower bound is >= +0.10 W (rail); FLAT if the interval lies inside +-0.10 W; else INCONCLUSIVE"},
            "E102-R10": {"what": "int8 B's rise toward the high bits: the high nibble against the low (four bits each)", "expected": "open: the bench says RISE (+0.06 W on the rail, all of it the MSB), E79's list says FLAT (-0.01 W)", "band_w": {"rail": 0.10, "board": 0.12},
                         "rule": "bk_f0 - bk_0f, watts, paired: RISE if the lower bound is > 0; FLAT if the interval lies inside +-0.10 W; else INCONCLUSIVE"},
            "E102-R11": {"what": "int8 B's additivity at line boundaries: ff against 0f + f0", "band_w": {"rail": 0.15, "board": 0.20}, "rule": "bk_ff - (bk_0f + bk_f0), watts, paired: CONFIRMED if the interval lies inside +-0.15 W (rail), REFUTED if wholly outside, else INCONCLUSIVE. ff against its eight singles is reported beside it."},
            "E102-R12": {"what": "the int8 single-bit list: what this design resolved, against what it said it could", "registered_half_width_fJ": resf["int8 single bit (I)"], "rule": "reported: positions whose interval excludes zero, and the median half-width"},
            "E102-S1": {"what": "the session tie (a check on the session): E82's anchors in block G", "rule": "each cell's D within its band of E82's dips-removed value; a failure means the session moved"},
        },
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e102.json"), "w"), indent=1)
    print(json.dumps({"int8_fit": int8fit, "resolution_fJ": resf, "noise": noise, "scale": scale, "rate": rate, "ties": {"b22": b22, "p22": p22, "b9": b9, "p9": p9},
                      "e79_int8_raw_W": {k: round(v["dW"], 3) for k, v in i8raw.items()}}, indent=0))


if __name__ == "__main__":
    main()
