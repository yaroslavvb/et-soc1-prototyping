#!/usr/bin/env python3
"""E93 (Q132): write predictions-e93.json, the frozen predictions and decision rules, from the committed sources it
names. Every number is copied or computed here from those files, never retyped; each source is recorded with its sha256.

    python3 tools/claims-v3/kinds/make_predictions_e93.py

Standard library only. The registration in words is tools/claims-v3/kinds/E93.md.
"""
import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
E82 = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json"
E88 = "docs/reports/data/2026-10-31-e88-result-path/e88.json"
P88 = "tools/claims-v3/rpath/predictions-e88.json"
E91L = "docs/reports/data/2026-10-31-e91-real-tensors-aifoundry1/e91-leak0.1994.json"
E93J = f"{K}/e93/e93.json"
T95 = {2: 4.303, 3: 3.182, 4: 2.776}
MINIONS = 1024
RATE = {"fp32": MINIONS * 600e6 / 546, "fp16": MINIONS * 600e6 / 546, "int8": MINIONS * 600e6 / 318}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def W(bits, fj, ty):
    """Bits per op at a price in fJ a bit -> watts at this type's op rate."""
    return bits * fj * 1e-15 * RATE[ty]


def main():
    e82 = load(E82)
    e88 = load(E88)
    p88 = load(P88)
    t93 = load(E93J)
    T = t93["tiles"]
    R = t93["reference_counts"]
    D82 = {n: v["D"]["mean"] for n, v in e82["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    CI82 = {n: v["D"]["ci95"] for n, v in e82["items"].items() if v.get("D")}
    D88 = {n: v["D"]["mean"] for n, v in e88["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    fit = p88["model"]["fit"]

    # ---- prices. F: E88's measured clocked lane on this card. a: E88's frozen fit, fJ per operand-bus bit.
    # pp: E88's measured operand-side multiplier less its bus share, per partial-product bit of the public Booth
    # generator on the same tile (make_e93.py). sign: E88's measured frozen-result sign cost (fp32; E90 found fp16's
    # sign step equal to fp32's within its interval, so the same number bounds fp16).
    F = {"fp32": D88["fp32.c_abs"], "fp16": D88["fp16.c_cancel"], "int8": D88["int8.c_cancel"]}
    A = {ty: fit[ty]["a_fj_per_bus_bit"] for ty in ("fp32", "fp16", "int8")}
    M = {"fp32": D88["fp32.r_abs"] - D88["fp32.c_abs"], "fp16": D88["fp16.r_cancel"] - D88["fp16.c_cancel"],
         "int8": D88["int8.r_cancel"] - D88["int8.c_cancel"]}
    Rp = {"int8": D88["int8.r_walk"] - D88["int8.r_cancel"]}
    SIGN = D88["fp32.s_abs"] - D88["fp32.c_abs"]
    PPJ = {}
    for ty, ref in (("fp32", "fp32.r_abs"), ("fp16", "fp16.r_cancel")):
        pp = R[ref]["booth_pp_bits_per_op"]
        PPJ[ty] = (M[ty] - W(R[ref]["bus_bits_per_op"], A[ty], ty)) / (pp * 1e-15 * RATE[ty])
    prices = {"F_w": F, "a_fj_per_bus_bit": A, "operand_side_M_w": M, "sign_frozen_w": SIGN,
              "pp_fj_per_booth_bit": PPJ, "op_rate_per_s": RATE,
              "what": "F = E88's D(constant operands, frozen result) on this card; a = E88's frozen fit; M = E88's "
                      "D(random operands, frozen) - F; sign = E88's D(s_abs) - D(c_abs); pp = (M - a x bus) / the "
                      "partial-product bits per op of r_abs (fp32) or r_cancel (fp16), make_e93.py's emulation"}

    def bus(n):
        return T[n]["stats"]["bus_bits_per_op"]

    def pp(n):
        return T[n]["booth_pp_bits_per_op"]

    pred = {}

    def put(name, low, high, band_lo, band_hi, reference, no_flush=None):
        v = T[name]
        s = v["stats"]
        pred[name] = {
            "type": v["type"], "kind": v["kind"], "rule": v["rule"], "sha256": v["sha256"],
            "gate_share_rtl": s["gated_lane_frac"], "gate_share_alt": s.get("gated_lane_frac_alt_grouping"),
            "live_share": round(1 - s["gated_lane_frac"], 6), "bus_bits_per_op": s["bus_bits_per_op"],
            "booth_pp_bits_per_op": v.get("booth_pp_bits_per_op"),
            "point_w": round((low + high) / 2, 3), "arm_low_w": round(low, 3), "arm_high_w": round(high, 3),
            "band": [round(band_lo, 3), round(band_hi, 3)], "reference": reference,
        }
        if no_flush is not None:
            pred[name]["if_not_flushed_w"] = round(no_flush, 3)

    # fp32 and fp16: live share 1.0 in every -0 and denormal tile
    for ty in ("fp32", "fp16"):
        const_ref = {"fp32": "E88 fp32.c_abs (E82 neg_ones %.2f, ones %.2f, pi %.2f)" % (D82["fp32.neg_ones"], D82["fp32.ones"], D82["fp32.pi"]),
                     "fp16": "E88 fp16.c_cancel (E82 neg_ones %.2f, ones %.2f)" % (D82["fp16.neg_ones"], D82["fp16.ones"])}[ty]
        put(f"{ty}.nz_both", F[ty], F[ty], F[ty] - 1.0, F[ty] + 1.0,
            f"live share 1 x a constant's cost, nothing moves and the result stays +0: {const_ref}, +-1.0 W (E88 H1's bound)")
        n = f"{ty}.a_nz_b_randn"
        lo = F[ty] + W(bus(n), A[ty], ty)
        put(n, lo, lo + SIGN, lo - 1.0, lo + SIGN + 1.0,
            "live share 1 x the constant, plus the B bits at E88's a; A = -0 holds every Booth digit at zero, so no "
            "partial product moves; high arm adds E88's frozen sign cost, the product's sign flips as often as in s_abs")
        n = f"{ty}.a_randn_b_nz"
        lo = F[ty] + W(bus(n), A[ty], ty) + W(pp(n), PPJ[ty], ty)
        put(n, lo, lo + SIGN / 2, lo - 2.0, lo + SIGN / 2 + 2.0,
            "live share 1 x the constant, plus the A bits at E88's a, plus the partial products: a negative Booth digit "
            "on multiplicand zero gives all ones (txfma_booth_ppg_32r4_norm.v), priced per bit from E88's M; high arm "
            "adds half the sign cost (A's sign changes every second micro-op)")
        n = f"{ty}.dnr_both"
        lo = F[ty] + W(bus(n), A[ty], ty)
        put(n, lo, lo, F[ty], lo + 1.5,
            "live share 1 x the constant, plus the raw denormal bits at E88's a: txfma_f0.v:375-377 clears the "
            "fraction, PRM 3.4 says input denormals become zero, so no partial product moves",
            no_flush=lo + W(T[n]["booth_pp_bits_per_op_no_flush"], PPJ[ty], ty))
        n = f"{ty}.a_dnr_b_randn"
        lo = F[ty] + W(bus(n), A[ty], ty)
        put(n, lo, lo + SIGN, lo - 1.0, lo + SIGN + 1.0,
            f"as {ty}.a_nz_b_randn, with A's raw denormal bits added at E88's a; flushed, so no partial product moves",
            no_flush=lo + W(T[n]["booth_pp_bits_per_op_no_flush"], PPJ[ty], ty))
    n = "fp32.dn1_both"
    put(n, F["fp32"], F["fp32"], F["fp32"] - 1.0, F["fp32"] + 1.0,
        "live share 1 x a constant's cost: E88 fp32.c_abs, +-1.0 W; 0x00000001 is raw nonzero and flushed inside")
    n = "fp32.a_randn_b_dnr"
    lo = F["fp32"] + W(bus(n), A["fp32"], "fp32") + W(pp(n), PPJ["fp32"], "fp32")
    put(n, lo, lo + SIGN / 2, lo - 2.0, lo + SIGN / 2 + 2.0,
        "as fp32.a_randn_b_nz with B's raw denormal bits added at E88's a: flushed, so the multiplicand is zero",
        no_flush=lo + W(T[n]["booth_pp_bits_per_op_no_flush"] - pp(n), PPJ["fp32"], "fp32"))
    # the masked sparse tile: E82's clean tile plus what the lost gating adds at the same prices
    n = "fp32.sparse50_mask"
    g0 = R["fp32.sparse50"]
    kinds = load(f"{K}/kinds.json")
    g_clean = kinds["kinds"]["fp32"]["sparse50"]["stats"]["gated_lane_frac"]
    gain = F["fp32"] * (g_clean - T[n]["stats"]["gated_lane_frac"]) + W(bus(n) - g0["bus_bits_per_op"], A["fp32"], "fp32") \
        + W(pp(n) - g0["booth_pp_bits_per_op"], PPJ["fp32"], "fp32")
    put(n, D82["fp32.sparse50"] + gain, D82["fp32.sparse50"] + gain, D82["fp32.sparse50"] + gain - 2.0,
        D82["fp32.sparse50"] + gain + 2.0,
        "E82 fp32.sparse50 (%.2f W) plus F x the lanes -0 keeps live, plus the extra bus and partial-product bits at "
        "the same prices; the result path of the lanes that compute is unchanged" % D82["fp32.sparse50"])
    # int8: the gate law on E82's full, under the RTL's reading
    full = D82["int8.full"]
    gated = (D82["int8.a_full_b_zeros"] + D82["int8.a_zeros_b_full"]) / 2
    L_low = F["int8"] + W(T["int8.b_unpaired"]["stats"]["a"]["bus_bits_per_op"], A["int8"], "int8")
    P = 0.5 * full + 0.5 * gated
    Q = 0.5 * full + 0.5 * L_low
    put("int8.b_pairs_rtl", P, P, P - 0.75, P + 0.75,
        "live share 0.5 x E82 int8.full (%.2f W) + 0.5 x E82's fully gated tiles (%.2f W), under the RTL's reading; "
        "under A4's it would read as int8.b_pairs_alt reads here" % (full, gated))
    for nm in ("int8.b_pairs_alt", "int8.b_unpaired"):
        put(nm, Q, 0.5 * full + 0.5 * full, Q - 0.75, full + 0.5,
            "under the RTL's reading every unit is live: 8 of 16 carry E82 int8.full's cost, 8 multiply A by a zero B "
            "word; low arm: those cost the clocked lane plus A's bits at E88's a (%.2f W for all 16), high arm: as much "
            "as random data, if the synthesized multiplier's recoding toggles on A with a zero multiplicand" % L_low)
    lo = F["int8"] + 0.25 * M["int8"]
    put("int8.a_3of4_b_full", lo, full, 2.0, full + 0.5,
        "live share 1: low arm E88's clocked lane + a quarter of its operand-side multiplier (one byte in four), high "
        "arm E82 int8.full; under a byte-wide A rule the tile would read like E82 int8.a_zeros_b_full (%.2f W)" %
        D82["int8.a_zeros_b_full"])

    def fixed(name):
        return {"e82": name, "value_w": round(D82[name], 4), "ci95_w": round(CI82[name], 4)}

    # ---- the rules. above: PASS if the interval's low end > pass, FAIL if its high end < fail, else INCONCLUSIVE.
    # below: PASS if high end < thr, FAIL if low end > thr. within: PASS if inside +-w, FAIL if wholly outside.
    th = {}

    def thr_flush(name, base):
        """Halfway between the flushed and the unflushed readings of a contrast."""
        flushed = pred[name]["arm_low_w"] - pred[base]["arm_low_w"]
        unflushed = pred[name]["if_not_flushed_w"] - pred[base]["arm_low_w"]
        th[name] = {"flushed_w": round(flushed, 3), "unflushed_w": round(unflushed, 3)}
        return round((flushed + unflushed) / 2, 2)

    rules = []

    def rule(rid, a, b=None, fx=None, test="above", what="", fails="", **kw):
        rules.append({"id": rid, "a": a, "b": b, "fixed": fixed(fx) if fx else None, "test": test, **kw,
                      "what": what, "failure_means": fails})

    gate_fail = "the compare is not a raw-word compare: the gate sees value zero, or the RTL here is not what runs"
    for rid, a, b, fx in (("R1-fp32-both", "fp32.nz_both", None, None),
                          ("R1-fp32-a", "fp32.a_nz_b_randn", "fp32.a_zeros_b_randn", None),
                          ("R1-fp32-b", "fp32.a_randn_b_nz", None, "fp32.a_randn_b_zeros"),
                          ("R1-fp16-both", "fp16.nz_both", None, None),
                          ("R1-fp16-a", "fp16.a_nz_b_randn", None, "fp16.a_zeros_b_randn"),
                          ("R1-fp16-b", "fp16.a_randn_b_nz", None, "fp16.a_randn_b_zeros")):
        rule(rid, a, b, fx, "above", **{"pass": 5.0, "fail": 2.0},
             what="negative zero leaves the lane on: the tile over its +0 twin", fails=gate_fail)
    rule("R2-fp32", "fp32.nz_both", "anchor_pi", None, "within", w=1.0,
         what="a live lane on -0 x -0 costs what a constant costs, same pass",
         fails="a live lane's cost depends on the operand being zero: the float unit saves clocks on a zero it detects")
    rule("R2-fp16", "fp16.nz_both", None, "fp16.neg_ones", "within", w=1.0,
         what="the same in fp16, against E82's constant on this card",
         fails="as R2-fp32, in the fp16 path")
    for rid, a, b, fx in (("R3-fp32-one", "fp32.dn1_both", None, None),
                          ("R3-fp32-both", "fp32.dnr_both", None, None),
                          ("R3-fp32-a", "fp32.a_dnr_b_randn", "fp32.a_zeros_b_randn", None),
                          ("R3-fp32-b", "fp32.a_randn_b_dnr", None, "fp32.a_randn_b_zeros"),
                          ("R3-fp16-both", "fp16.dnr_both", None, None),
                          ("R3-fp16-a", "fp16.a_dnr_b_randn", None, "fp16.a_zeros_b_randn")):
        rule(rid, a, b, fx, "above", **{"pass": 5.0, "fail": 2.0},
             what="a denormal word leaves the lane on: the gate does not act", fails=gate_fail)
    for rid, a, b in (("R4-fp32-both", "fp32.dnr_both", "fp32.dn1_both"),
                      ("R4-fp32-a", "fp32.a_dnr_b_randn", "fp32.a_nz_b_randn"),
                      ("R4-fp16-both", "fp16.dnr_both", "fp16.nz_both"),
                      ("R4-fp16-a", "fp16.a_dnr_b_randn", "fp16.a_nz_b_randn")):
        rule(rid, a, b, None, "below", thr=thr_flush(a, b),
             what="the float unit flushes a denormal: random denormal fractions never reach the multiplier",
             fails="the fractions reach the multiplier: PRM 3.4, the VPU specification 2.2.3.9 and txfma_f0.v:375-377 "
                   "do not describe what the silicon's multiplier sees")
    fa, fb = "fp32.a_randn_b_nz", "fp32.a_nz_b_randn"
    rule("R5-fp32", fa, fb, None, "above", **{"pass": 1.0, "fail": 1.0},
         what="the recoder is on A: a live zero costs more when it sits on B (partial products all-0 / all-1) than on A "
              "(every digit zero), though B moves twice as often",
         fails="the partial products do not swing as the public Booth generator says, or something keeps them from "
               "reaching the tree on a zero operand")
    rule("R6a", "int8.b_unpaired", "int8.b_pairs_rtl", None, "above", **{"pass": 0.30, "fail": 0.30},
         what="int8's eight-byte B rule: the same eight zero words a line cost less when they fill (l, l+8) pairs",
         fails="filling pairs saves nothing against one zero word in each pair: no eight-byte rule at this resolution")
    rule("R6b", "int8.b_pairs_alt", "int8.b_pairs_rtl", None, "above", **{"pass": 0.30, "fail": 0.30},
         what="int8's column pairing: zero words filling (l, l+8) cost less than the same words filling (2l, 2l+1)",
         fails="the RTL's pairing does not hold on silicon; if b_pairs_alt reads below b_pairs_rtl by more than the "
               "margin, A4's reading holds and every int8 gate figure on the page changes (kinds.json's "
               "gated_lane_frac_alt_grouping replaces gated_lane_frac)")
    rule("R6c", "int8.b_unpaired", "int8.b_pairs_alt", None, "within", w=0.60,
         what="the control: (2l, 2l+1) pairs gate nothing, so they cost what unpaired zero words cost",
         fails="the (2l, 2l+1) arrangement differs from unpaired: a pairing the two readings do not describe, or a "
               "lane-position effect")
    rule("R7", "int8.a_3of4_b_full", "int8.a_zeros_b_full", None, "above", **{"pass": 1.0, "fail": 1.0},
         what="int8's A rule: three of four bytes zero leaves the lane on; four of four gates it",
         fails="a word with one nonzero byte is gated, or costs next to nothing live: the A test is not the whole word")
    rule("R8", "fp32.sparse50_mask", "fp32.sparse50", None, "above", **{"pass": 1.0, "fail": 1.0},
         what="the same sparse numbers cost more when half their zeros are -0.0, as x * mask leaves them",
         fails="the zeros' sign does not matter: lanes on a -0 operand cost no more than gated ones in this mix")

    # ---- what the rules can say: P(verdict) by simulation, per-pass contrast sd from E82 and E88 (scatter in E93.md)
    def sim(test, truth, sd, n, rng, draws=20000, **k):
        out = {"PASS": 0, "FAIL": 0, "INCONCLUSIVE": 0}
        for _ in range(draws):
            v = [rng.gauss(truth, sd) for _ in range(n)]
            m = sum(v) / n
            h = T95[n - 1] * math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1) / n)
            lo, hi = m - h, m + h
            if test == "above":
                o = "PASS" if lo > k["pass_"] else "FAIL" if hi < k["fail"] else "INCONCLUSIVE"
            elif test == "below":
                o = "PASS" if hi < k["thr"] else "FAIL" if lo > k["thr"] else "INCONCLUSIVE"
            else:
                o = "PASS" if lo >= -k["w"] and hi <= k["w"] else "FAIL" if hi < -k["w"] or lo > k["w"] else "INCONCLUSIVE"
            out[o] += 1
        return {a_: round(b_ / draws, 3) for a_, b_ in out.items()}

    rng = random.Random(9310)
    d_low = Q - P                                 # the smaller effect the registration expects in int8
    d_high = pred["int8.b_unpaired"]["arm_high_w"] - P
    power = {"what": "P(verdict) over 20,000 simulated sessions, normal per-pass contrasts", "sd_w": {"int8": 0.23, "fp32": 0.30, "fp16": 0.16},
             "R6b_above_0.30": {}, "R6c_within_0.60": {}, "R1_above_5_fail_2": {}, "R2_within_1": {}, "R5_above_1": {}}
    for n in (3, 4, 5):
        power["R6b_above_0.30"][f"n{n}"] = {f"true {t:+.2f} W": sim("above", t, 0.23, n, rng, pass_=0.30, fail=0.30)
                                            for t in (-d_low, 0.0, 0.5, d_low, d_high)}
        power["R6c_within_0.60"][f"n{n}"] = {f"true {t:+.2f} W": sim("within", t, 0.23, n, rng, w=0.60)
                                             for t in (0.0, d_low)}
        power["R1_above_5_fail_2"][f"n{n}"] = {f"true {t:+.2f} W": sim("above", t, 0.30, n, rng, pass_=5.0, fail=2.0)
                                               for t in (F["fp32"], 0.6)}
        power["R2_within_1"][f"n{n}"] = {f"true {t:+.2f} W": sim("within", t, 0.30, n, rng, w=1.0) for t in (0.0, 2.0)}
        rb = pred[fa]["point_w"] - pred[fb]["point_w"]
        power["R5_above_1"][f"n{n}"] = {f"true {t:+.2f} W": sim("above", t, 0.30, n, rng, pass_=1.0, fail=1.0) for t in (rb, 0.0)}

    tie = {"fp32.randn": 0.50, "fp16.randn": 0.50, "anchor_pi": 0.50, "int8.full": 0.25,
           "fp32.a_zeros_b_randn": 0.25, "int8.a_zeros_b_full": 0.25, "fp32.sparse50": 0.75}
    e82_ref = {n: {"D_w": round(D82[n], 4), "ci95_w": round(CI82[n], 4), "band_w": b} for n, b in tie.items()}
    e91 = load(E91L)
    e91_ref = {n: {"D_w": round(e91["items"][n]["D"]["mean"], 4), "ci95_w": round(e91["items"][n]["D"]["ci95"], 4), "band_w": tie[n]}
               for n in ("fp32.randn", "fp16.randn", "anchor_pi", "int8.full")}

    harness_reused = {f"tools/claims-v3/{r}": sha(f"tools/claims-v3/{r}") for r in
                      ("lib.sh", "kinds/run_e78.py", "kinds/reduce_e78.py", "kinds/e78_common.py", "kinds/kinds.json")}
    e93_files = {f"{K}/{f}": sha(f"{K}/{f}") for f in ("e93_common.py", "run_e93.py", "block_e93.sh", "queue_e93.sh",
                                                       "run_e93.sh", "reduce_e93.py", "make_e93.py")}
    out = {
        "experiment": "E93", "registered": "2026-11-01", "registration": f"{K}/E93.md",
        "card": {"name": "aifoundry1-c1", "device": 1, "clock_mhz": 600,
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}}},
        "primary": {"reduction": "reduce_e93.py: reduce_e78.py unchanged, E93's items, card 1's config gate, dips "
                                 "removed (E82 A2), leakage slope frozen at E82's own on this card",
                    "leak_w_per_c": 0.2414,
                    "arms": {"dips_kept": ["--keep-dips", "--leak", "0.2414"], "auto": ["--leak", "auto"],
                             "leak0.1994": ["--leak", "0.1994"], "leak0.3803": ["--leak", "0.3803"],
                             "leak0.545": ["--leak", "0.545"], "leak0": ["--leak", "0"]},
                    "min_kept_passes": 3, "min_cell_passes": 3},
        "inputs_frozen": {"e82_reduction": {"path": E82, "sha256": sha(E82), "commit": "0a041356"},
                          "e88_reduction": {"path": E88, "sha256": sha(E88), "commit": "f1c7412e"},
                          "e88_predictions": {"path": P88, "sha256": sha(P88), "commit": "3dd99088"},
                          "e91_arm_0.1994": {"path": E91L, "sha256": sha(E91L), "commit": "7c0af0c1"},
                          "e93_tiles": {"path": E93J, "sha256": sha(E93J)}},
        "prices": prices, "tiles": pred, "flush_thresholds": th, "rules": rules, "e82_reference": e82_ref,
        "e91_reference": e91_ref, "power": power,
        "budget": {"card_minutes": 40, "passes_max": 5, "passes_min_planned": 4, "runs_per_pass": 40, "burnin": 2,
                   "smoke_runs": 8, "queue_budget_s": 2280, "queue_first_s": 450, "first_pass": 9310, "smoke_pass": 9301},
        "harness": {"reused_unchanged_sha256": harness_reused, "e93_json_sha256": sha(E93J), "e93_files_sha256": e93_files},
    }
    p = os.path.join(HERE, "predictions-e93.json")
    json.dump(out, open(p, "w"), indent=1, sort_keys=True)
    print("wrote", p)
    print("prices", json.dumps({k: v for k, v in prices.items() if k != "what"}, indent=0)[:900])
    for n, v in sorted(pred.items()):
        print(f"{n:24s} live {v['live_share']:.3f} point {v['point_w']:7.2f} arms [{v['arm_low_w']:6.2f}, {v['arm_high_w']:6.2f}] "
              f"band [{v['band'][0]:6.2f}, {v['band'][1]:6.2f}]" + (f" noflush {v['if_not_flushed_w']:6.2f}" if "if_not_flushed_w" in v else ""))
    for r in rules:
        print(r["id"], r["test"], {k: r[k] for k in ("pass", "fail", "thr", "w") if k in r}, r["a"], "-", r["b"] or (r["fixed"] and r["fixed"]["value_w"]))
    print("flush", th)
    print(json.dumps(power, indent=0)[:3000])


if __name__ == "__main__":
    main()
