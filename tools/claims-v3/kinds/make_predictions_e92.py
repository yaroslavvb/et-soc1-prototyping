#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E92 (Q132): write predictions-e92.json, E92's freeze, from committed sources only. Every number is read from the
file it names, never retyped: E78's and E90's reductions and scores, E65's, E67's and E79's sign-bit prices, E88's score
and fit, E82's reduction (the card scale), e92/e92.json (the counts) and Q130(n)'s predictor (real/make_real.py).

    /usr/bin/python3 tools/claims-v3/kinds/make_predictions_e92.py      # writes predictions-e92.json

The models, all frozen here before any E92 data exist:
  bits       P_bits = dW_B x flips_B / item_flips_B + dW_A x flips_A / item_flips_A, E90's model unchanged
  alt        the adder-alternation reading: E88's frozen random-sign cost beyond its sign bits, per alternation of
             eff_sub, carried to aifoundry3 by the card scale and multiplied by a tile's alternations:
               p_alt = (M32s - P_bits(s_abs)) / N_alt(s_abs),   alt(contrast) = scale x p_alt x dN_alt
             fp16: the same price per lane-micro-op, times E90's fp16 step over its fp32 step, each beyond its bits
  e88        E88's frozen four-price fit on E82 (card 1): D = F live + a N_op + c N_prod + b N_res
  e88+flops  e88 plus one more price, f per flop-bit change on the adder's inputs and flops (make_e92.py's reading of
             txfma_f3.v and txfma_f4.v), calibrated on the same single datum: f = (M32s - e88(M32s)) / dflops(s_abs - c_abs);
             times the card scale
  q130n      Q130(n)'s predictor, fitted on E78's 51 kinds, unchanged
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(HERE, "real")]
import make_predictions_e90 as mp90  # noqa: E402

E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E82_JSON = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json"
E88_SCORED = "docs/reports/data/2026-10-31-e88-result-path/scored.json"
E88_FIT = "tools/claims-v3/rpath/e88.json"
E90_JSON = "docs/reports/data/2026-10-31-e90-signs-spread/e90.json"
E90_SCORED = "docs/reports/data/2026-10-31-e90-signs-spread/scored.json"
E65_HL = mp90.E65_HL
E67_HL = mp90.E67_HL
E79_README = mp90.E79_README
E92_JSON = "tools/claims-v3/kinds/e92/e92.json"
REUSED = ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json")
BOX_FILES = ("tools/claims-v3/kinds/e92_common.py", "tools/claims-v3/kinds/run_e92.py",
             "tools/claims-v3/kinds/reduce_e92.py", "tools/claims-v3/kinds/block_e92.sh",
             "tools/claims-v3/kinds/queue_e92.sh", "tools/claims-v3/kinds/run_e92.sh",
             "tools/claims-v3/kinds/make_e92.py")
ITEM_FLIPS = mp90.ITEM_FLIPS
OPS_PER_S = 600e6 / 546.0 * 1024        # whole chip at duty 1 (fp32, fp16)
FACTOR_BITS = 2.0                       # R1: E90-R1's factor
ZERO_BAND = 0.50                        # R3, R9: E86-R5 / E90-R4's session band for fp32 and fp16 cells
LO_FRACTION, HI_FACTOR = 0.5, 2.0       # R2, R8: "confirmed" inside [0.5, 2] x the prediction
LO_REFUTE, HI_REFUTE = 0.25, 4.0        # "refuted" wholly below 0.25 x or wholly above 4 x the prediction
LINEAR_FRACTION = 0.20                  # R4-R7: a difference that would move a price per alternation by a fifth


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def main():
    e78, e82, e88s, e88f, e90j, e90s, spec = (load(x) for x in (E78_JSON, E82_JSON, E88_SCORED, E88_FIT, E90_JSON, E90_SCORED, E92_JSON))
    tiles, refs = spec["tiles"], spec["references"]
    D78 = {n: v["D"]["mean"] for n, v in e78["items"].items()}
    D90 = {n: v["D"]["mean"] for n, v in e90j["items"].items() if v.get("D")}
    it65 = load(E65_HL)["cards"]["aifoundry3"]["items"]["bit_31"]
    it67 = load(E67_HL)["cards"]["aifoundry3"]["items"]["abit_31"]
    txt79 = open(os.path.join(ROOT, E79_README)).read()
    b16 = mp90.e79_sign_row(txt79, "### fp16, B side (A = 1.0), jg layout")
    a16 = mp90.e79_sign_row(txt79, "### fp16, A side (B = 1.0)")
    price = {"fp32": {"B": it65["d_p80"], "A": it67["d_p80"]}, "fp16": {"B": b16["dW"], "A": a16["dW"]}}
    price_src = {"fp32.B": f"{E65_HL} cards.aifoundry3.items.bit_31.d_p80", "fp32.A": f"{E67_HL} cards.aifoundry3.items.abit_31.d_p80",
                 "fp16.B": f"{E79_README} table '{b16['table']}' row 15 (a bound)", "fp16.A": f"{E79_README} table '{a16['table']}' row 15"}

    def get(n):
        return tiles.get(n) or refs[n]

    def flips(n):
        t = get(n)
        st = t.get("stats", t)
        return st["sign_flips_per_op_a"], st["sign_flips_per_op_b"]

    def p_bits(n, lo=None):
        ty = n.split(".")[0]
        fa, fb = flips(n)
        if lo:
            la, lb = flips(lo)
            fa, fb = fa - la, fb - lb
        return price[ty]["B"] * fb / ITEM_FLIPS[ty]["B"] + price[ty]["A"] * fa / ITEM_FLIPS[ty]["A"]

    def n_alt(n):
        s = get(n)["sign"]
        return s["N_alt1"] + s["N_alt2"]

    def x_of(n):
        t = get(n)
        bus = t["stats"]["bus_bits_per_op"] if "stats" in t else t["bus_bits_per_op"]
        s = t["stream"]
        return np.array([s["live_frac"], bus, s["prod"], s["res_bits_per_op"]], float)

    def flops(n):
        return get(n)["sign"]["flops"]

    fit = e88f["fit"]
    coef = {t: np.array(fit[t]["coef"]) for t in ("fp32", "fp16")}
    cov = {t: np.array(fit[t]["cov"]) for t in ("fp32", "fp16")}
    rms = {t: fit[t]["rms_w"] for t in ("fp32", "fp16")}

    def e88_d(n):
        return float(x_of(n) @ coef[n.split(".")[0]])

    def e88_delta(hi, lo):
        t = hi.split(".")[0]
        dx = x_of(hi) - x_of(lo)
        mu = float(dx @ coef[t])
        se = float(np.sqrt(dx @ cov[t] @ dx))
        tol = 2.0 * float(np.sqrt(se ** 2 + 2.0 * rms[t] ** 2))
        return {"mu": round(mu, 3), "lo": round(mu - tol, 3), "hi": round(mu + tol, 3)}

    # ---- the card scale: E78's random tile on aifoundry3 against E82's on aifoundry1 card 1, the card E88 ran on
    scale = {t: D78[f"{t}.randn"] / e82["items"][f"{t}.randn"]["D"]["mean"] for t in ("fp32", "fp16")}
    # ---- the adder-alternation reading, from E88's M32s and E90's steps
    M32s = e88s["primary"]["contrasts"]["M32s"]["D"]["mean"]
    R32s = e88s["primary"]["contrasts"]["R32s"]["D"]["mean"]
    Pb_sabs = p_bits("fp32.s_abs")
    p_alt = (M32s - Pb_sabs) / n_alt("fp32.s_abs")                 # W per alternation/op, card 1
    st90 = e90s["steps"]
    S32 = st90["fp32.signs-fp32.ones"]
    S16 = st90["fp16.signs-fp16.ones"]
    ratio16 = (S16["step_w"]["mean"] - S16["P_bits_w"]) / (S32["step_w"]["mean"] - S32["P_bits_w"])
    # fp16 counts two eff_sub per lane-micro-op; its price is per lane-micro-op alternation, so use eff_sub1's count
    alt_pred = {"fp32": scale["fp32"] * p_alt * n_alt("fp32.h_sub"),
                "fp16": scale["fp16"] * p_alt * ratio16 * tiles["fp16.h_sub"]["sign"]["N_alt1"]}
    pa_fj = p_alt / OPS_PER_S * 1e15
    # ---- e88+flops
    d88 = e88_delta("fp32.s_abs", "fp32.c_abs")
    f_w = (M32s - d88["mu"]) / (flops("fp32.s_abs") - flops("fp32.c_abs"))       # W per flop-bit change/op
    f_fj = f_w / OPS_PER_S * 1e15

    def m2(hi, lo):
        t = hi.split(".")[0]
        return scale[t] * (float((x_of(hi) - x_of(lo)) @ coef[t]) + f_w * (flops(hi) - flops(lo)))

    def alt_of(hi, lo):
        t = hi.split(".")[0]
        if t == "fp32":
            return scale[t] * p_alt * (n_alt(hi) - n_alt(lo))
        # fp16: (N_alt1 + N_alt2) / 2 is the lane-micro-op count when both alternate together; a one-aligner tile counts half
        return scale[t] * p_alt * ratio16 * (n_alt(hi) - n_alt(lo)) / 2.0

    def contrast(name, hi, lo, rule, what, **extra):
        out = {"hi": hi, "lo": lo, "rule": rule, "what": what,
               "bits_w": round(p_bits(hi, lo), 4), "alt_w": round(alt_of(hi, lo), 3),
               "e88": e88_delta(hi, lo), "e88_flops_w": round(m2(hi, lo), 3),
               "dN_alt": round(n_alt(hi) - n_alt(lo), 1), "dflops": round(flops(hi) - flops(lo), 1)}
        out.update(extra)
        return name, out

    C = dict([
        contrast("fp32.h_add-c_abs", "fp32.h_add", "fp32.c_abs", "E92-R1", "the sign bits: every B, product and C sign moves, the adder always adds"),
        contrast("fp16.h_add-c_abs", "fp16.h_add", "fp16.c_abs", "E92-R1", "the same in fp16"),
        contrast("fp32.h_sub-h_add", "fp32.h_sub", "fp32.h_add", "E92-R2", "the same operands: alternate add, subtract, against always add"),
        contrast("fp16.h_sub-h_add", "fp16.h_sub", "fp16.h_add", "E92-R2", "the same in fp16"),
        contrast("fp32.c_alt-c_abs", "fp32.c_alt", "fp32.c_abs", "E92-R2", "no operand or product sign moves at k >= 1: only the sign the sum holds, so the adder alternates"),
        contrast("fp16.c_alt-c_abs", "fp16.c_alt", "fp16.c_abs", "E92-R2", "the same in fp16"),
        contrast("fp32.h_allsub-h_add", "fp32.h_allsub", "fp32.h_add", "E92-R3", "the same operands: always subtract, against always add"),
        contrast("fp16.h_allsub-h_add", "fp16.h_allsub", "fp16.h_add", "E92-R3", "the same in fp16"),
        contrast("fp32.c_neg-c_abs", "fp32.c_neg", "fp32.c_abs", "E92-R3", "nothing moves at k >= 1: always subtract, against always add"),
        contrast("fp32.i_sub-i_add", "fp32.i_sub", "fp32.i_add", "E92-R4", "the A-side twin: alternation every two micro-ops"),
        contrast("fp32.h_sub2-c_abs", "fp32.h_sub2", "fp32.c_abs", "E92-R5", "2 of 8 lanes alternate"),
        contrast("fp32.h_sub4-c_abs", "fp32.h_sub4", "fp32.c_abs", "E92-R5", "4 of 8 lanes alternate"),
        contrast("fp32.h_sub6-c_abs", "fp32.h_sub6", "fp32.c_abs", "E92-R5", "6 of 8 lanes alternate"),
        contrast("fp32.h_sub-c_abs", "fp32.h_sub", "fp32.c_abs", "E92-R5", "8 of 8 lanes alternate"),
        contrast("fp32.s_abs-c_abs", "fp32.s_abs", "fp32.c_abs", "E92-R6", "random signs, frozen: E88's M32s on this card"),
        contrast("fp16.s_abs-c_abs", "fp16.s_abs", "fp16.c_abs", "E92-R6", "random signs, frozen, in fp16"),
        contrast("fp16.h_sub-c_abs", "fp16.h_sub", "fp16.c_abs", "E92-R6", "both products alternate"),
        contrast("fp32.r_h_sub-r_h_add", "fp32.r_h_sub", "fp32.r_h_add", "E92-R7", "the core contrast on random positive magnitudes, frozen"),
        contrast("fp32.w_h_sub-w_h_add", "fp32.w_h_sub", "fp32.w_h_add", "E92-R8", "the core contrast with a moving sum, magnitude 1"),
        contrast("fp32.wr_h_sub-wr_h_add", "fp32.wr_h_sub", "fp32.wr_h_add", "E92-R8", "the core contrast with moving sums on random positive magnitudes"),
        contrast("fp32.k_only-c_abs", "fp32.k_only", "fp32.c_abs", "E92-R9", "the kinds page's design: operand signs flip at k boundaries only, every product +"),
        contrast("fp16.hh_sub-hl_sub", "fp16.hh_sub", "fp16.hl_sub", "E92-R10", "aligner 1 against aligner 2"),
        # reported, no verdict
        contrast("fp16.hh_sub-c_abs", "fp16.hh_sub", "fp16.c_abs", None, "only the high product alternates"),
        contrast("fp16.hl_sub-c_abs", "fp16.hl_sub", "fp16.c_abs", None, "only the low product alternates"),
        contrast("fp32.w_h_add-w_c", "fp32.w_h_add", "fp32.w_c", None, "the sign bits with a moving sum (E65's bit_31 layout)"),
        contrast("fp32.w_h_sub-w_c", "fp32.w_h_sub", "fp32.w_c", None, "signs and alternation with a moving sum"),
        contrast("fp32.r_h_add-r_abs", "fp32.r_h_add", "fp32.r_abs", None, "the sign bits on random magnitudes, frozen"),
        contrast("fp32.r_h_sub-r_abs", "fp32.r_h_sub", "fp32.r_abs", None, "signs and alternation on random magnitudes, frozen"),
        contrast("fp32.wr_h_add-r_walk", "fp32.wr_h_add", "fp32.r_walk", None, "the sign bits on random magnitudes, moving sums"),
        contrast("fp32.signs-ones", "fp32.signs", "fp32.ones", None, "E90's headline step, this session"),
        contrast("fp16.signs-ones", "fp16.signs", "fp16.ones", None, "E90's headline step in fp16, this session"),
        contrast("fp32.ones-c_abs", "fp32.ones", "fp32.c_abs", None, "E88's W32 on this card"),
        contrast("fp16.ones-c_abs", "fp16.ones", "fp16.c_abs", None, "the same in fp16"),
        contrast("fp32.r_walk-r_abs", "fp32.r_walk", "fp32.r_abs", None, "E88's R32 on this card"),
        contrast("fp32.r_abs-c_abs", "fp32.r_abs", "fp32.c_abs", None, "E88's M32 on this card"),
    ])
    # the alternation contrasts' frozen prediction: the alt model; the moving-sum ones: e88+flops (make_e92's counts say why)
    thresholds = {}
    for k, c in C.items():
        if c["rule"] == "E92-R1":
            c["threshold_w"] = round(FACTOR_BITS * c["bits_w"], 4)
        if c["rule"] == "E92-R2":
            ty = k.split(".")[0]
            c["pred_w"] = round(alt_pred[ty], 3)
        if c["rule"] == "E92-R8":
            c["pred_w"] = c["e88_flops_w"]
        if c["rule"] in ("E92-R3", "E92-R9"):
            c["band_w"] = ZERO_BAND
        if c["rule"] == "E92-R10":
            c["pred_w"] = c["e88_flops_w"]
    linear_band = {t: round(LINEAR_FRACTION * alt_pred[t], 3) for t in alt_pred}
    # ---- E90's measured step on random magnitudes, read as linear in alternation: an alternative to e88+flops for wr
    randn_step = st90["fp32.randn-fp32.abs_randn"]
    alt_wr_linear = (randn_step["step_w"]["mean"] - randn_step["P_bits_w"]) * n_alt("fp32.wr_h_sub") / n_alt("fp32.randn")
    C["fp32.wr_h_sub-wr_h_add"]["e90_linear_w"] = round(alt_wr_linear, 3)
    C["fp32.wr_h_sub-wr_h_add"]["e90_linear_source"] = (f"(E90 randn - abs_randn {randn_step['step_w']['mean']:.3f} W, minus its bits "
                                                        f"{randn_step['P_bits_w']:.3f} W) x N_alt(wr_h_sub) / N_alt(randn)")
    # ---- back-test on data that already exist (reported; E90's and E88's measured steps against the frozen models)
    bt = {}
    for nm, hi, lo, measured, src in (
            ("E90 fp32 signs - ones", "fp32.signs", "fp32.ones", S32["step_w"]["mean"], E90_SCORED),
            ("E90 fp16 signs - ones", "fp16.signs", "fp16.ones", S16["step_w"]["mean"], E90_SCORED),
            ("E90 fp32 randn - abs_randn", "fp32.randn", "fp32.abs_randn", randn_step["step_w"]["mean"], E90_SCORED),
            ("E90 fp16 randn - abs_randn", "fp16.randn", "fp16.abs_randn", st90["fp16.randn-fp16.abs_randn"]["step_w"]["mean"], E90_SCORED)):
        bt[nm] = {"measured_w": round(measured, 3), "e88_w": e88_delta(hi, lo)["mu"], "e88_flops_w": round(m2(hi, lo), 3),
                  "bits_w": round(p_bits(hi, lo), 3), "source": src}
    t = "fp32"
    dx = x_of("fp32.s_walk") - x_of("fp32.s_abs")
    bt["E88 R32s s_walk - s_abs (card 1, no scale)"] = {"measured_w": round(R32s, 3), "e88_w": round(float(dx @ coef[t]), 3),
                                                        "e88_flops_w": round(float(dx @ coef[t]) + f_w * (flops("fp32.s_walk") - flops("fp32.s_abs")), 3),
                                                        "bits_w": None, "source": E88_SCORED}
    # ---- Q130(n)'s predictor
    import make_real as mr  # noqa: E402
    P, rows = mr.fit_predictor(e78, ROOT)
    out_tiles = {}
    for name, e in tiles.items():
        ty = e["type"]
        raw = open(os.path.join(HERE, "e92", e["file"]), "rb").read()
        r = mr.predict_D(P, ty, mr.features(raw, ty), rows[ty])
        d_pred = scale[ty] * (e88_d(name) + f_w * flops(name))
        if e["kind"] == "signs":
            d_pred = D90[name]
        out_tiles[name] = {"type": ty, "group": e["group"], "sha256": e["sha256"],
                           "stats": e["stats"], "stream": e["stream"], "sign": e["sign"],
                           "e88_D_w": round(e88_d(name), 3), "D_pred_w": round(d_pred, 3),
                           "D_pred_source": "E90's measured D" if e["kind"] == "signs" else "scale x (e88 + f flops)",
                           "q130n_predictor": {"point_w": r["point_w"], "pi95_w": r["pi95_w"], "model": r["model"],
                                               "features_outside_e78_range": r["features_outside_e78_range"]}}
    reg = {
        "experiment": "E92", "title": "where a random sign's cost goes (aifoundry3 card 0, 600 MHz)",
        "request": "Q132, item 2 of the kinds page's section 11", "date": "2026-11-01",
        "registration": "tools/claims-v3/kinds/E92.md", "card": "aifoundry3 card 0",
        "inputs_frozen": {
            "e78_reduction": {"path": E78_JSON, "sha256": sha(E78_JSON)},
            "e82_reduction": {"path": E82_JSON, "sha256": sha(E82_JSON)},
            "e88_scored": {"path": E88_SCORED, "sha256": sha(E88_SCORED)},
            "e88_fit": {"path": E88_FIT, "sha256": sha(E88_FIT)},
            "e90_reduction": {"path": E90_JSON, "sha256": sha(E90_JSON)},
            "e90_scored": {"path": E90_SCORED, "sha256": sha(E90_SCORED)},
            "e65_hl": {"path": E65_HL, "sha256": sha(E65_HL)},
            "e67_hl": {"path": E67_HL, "sha256": sha(E67_HL)},
            "e79_readme": {"path": E79_README, "sha256": sha(E79_README)},
            "make_real": {"path": "tools/claims-v3/kinds/real/make_real.py", "sha256": sha("tools/claims-v3/kinds/real/make_real.py")},
            "e92_json": {"path": E92_JSON, "sha256": sha(E92_JSON)},
        },
        "harness": {"reused_unchanged_sha256": {r: sha(r) for r in REUSED},
                    "e92_files_sha256": {r: sha(r) for r in BOX_FILES},
                    "e92_json_sha256": sha(E92_JSON)},
        "plan": {"passes": [9210, 9211, 9212, 9213], "smoke": 9201, "runs_per_pass": 54, "min_passes": 3,
                 "items_per_pass": "the tie twice, E78's six anchors three times, E92's 32 tiles and fp32.ones, fp16.ones once"},
        "card_budget": {"card_minutes_max": 45, "queue_budget_min": 41, "queue_deadline": "2026-11-01 06:45 PST",
                        "every_run_ends_by": "07:15 PST"},
        "models": {
            "sign_bit_prices_w": price, "sign_bit_price_sources": price_src, "item_flips": ITEM_FLIPS,
            "card_scale": {t: round(scale[t], 4) for t in scale},
            "card_scale_source": f"{E78_JSON} items.<t>.randn.D.mean over {E82_JSON} items.<t>.randn.D.mean",
            "M32s_w": round(M32s, 4), "R32s_w": round(R32s, 4), "M32s_source": f"{E88_SCORED} primary.contrasts.M32s.D.mean",
            "P_bits_s_abs_w": round(Pb_sabs, 4), "N_alt_s_abs": n_alt("fp32.s_abs"),
            "p_alt_w_per_alternation_per_op": p_alt, "p_alt_fj_per_alternation": round(pa_fj, 1),
            "ratio_fp16_over_fp32_beyond_bits": round(ratio16, 4),
            "alt_pred_h_sub_w": {t: round(alt_pred[t], 3) for t in alt_pred},
            "e88_d_s_abs_minus_c_abs_w": d88["mu"], "f_w_per_flop_bit_per_op": f_w, "f_fj_per_flop_bit": round(f_fj, 2),
            "linear_band_w": linear_band,
        },
        "contrasts": C,
        "tiles": out_tiles,
        "back_test": bt,
        "e78_reference": {n: {"D_w": round(D78[n], 4)} for n in ("fp32.randn", "fp16.randn", "int8.full", "fp32.ones", "fp16.ones", "anchor_pi")},
        "e90_reference": {n: {"D_w": round(D90[n], 4)} for n in ("fp32.randn", "fp16.randn", "int8.full", "fp32.ones", "fp16.ones", "anchor_pi", "fp32.signs", "fp16.signs")},
        "e88_reference": {"M32s_w": round(M32s, 4), "F32_w": round(e88s["primary"]["contrasts"]["F32"]["D"]["mean"], 4),
                          "M32_w": round(e88s["primary"]["contrasts"]["M32"]["D"]["mean"], 4),
                          "R32_w": round(e88s["primary"]["contrasts"]["R32"]["D"]["mean"], 4)},
        "rules": {
            "E92-R1": {"what": "the sign bits' price holds for h_add - c_abs (every operand, product and C sign moves; the adder always adds)",
                       "contrasts": ["fp32.h_add-c_abs", "fp16.h_add-c_abs"], "factor": FACTOR_BITS,
                       "per_contrast": "CONFIRMED if the 95% upper bound <= 2 x P_bits, REFUTED if the 95% lower bound > 2 x P_bits, else INCONCLUSIVE"},
            "E92-R2": {"what": "the adder-alternation reading: same operands, or none moving; only the effective operation differs",
                       "contrasts": ["fp32.h_sub-h_add", "fp16.h_sub-h_add", "fp32.c_alt-c_abs", "fp16.c_alt-c_abs"],
                       "per_contrast": "CONFIRMED if the 95% interval lies inside [0.5, 2] x pred_w, REFUTED if it lies wholly below 0.25 x pred_w or wholly above 4 x pred_w, else INCONCLUSIVE"},
            "E92-R3": {"what": "subtraction itself is not dear: a steady effective subtract costs what a steady add costs",
                       "contrasts": ["fp32.h_allsub-h_add", "fp16.h_allsub-h_add", "fp32.c_neg-c_abs"], "band_w": ZERO_BAND,
                       "per_contrast": "CONFIRMED if the 95% interval lies inside +-0.50 W, REFUTED if wholly outside, else INCONCLUSIVE"},
            "E92-R4": {"what": "the A-side twin: alternation every two micro-ops costs half (N_alt ratio from e92.json)",
                       "statistic": "(i_sub - i_add) - (N_alt(i_sub) / N_alt(h_sub)) x (h_sub - h_add), paired per pass",
                       "band_w": linear_band["fp32"], "per_contrast": "CONFIRMED if the 95% interval lies inside +-band, REFUTED if wholly outside, else INCONCLUSIVE"},
            "E92-R5": {"what": "linear in the number of lanes alternating",
                       "statistic": "for m = 2, 4, 6: (h_sub<m> - c_abs) - (m / 8) x (h_sub - c_abs), paired per pass",
                       "band_w": linear_band["fp32"], "per_contrast": "each rung as R4; CONFIRMED if all three are, REFUTED if any is, else INCONCLUSIVE"},
            "E92-R6": {"what": "random signs at about 50% alternation are the same price per alternation as structured signs at 100%",
                       "statistic": "(s_abs - c_abs - P_bits(s_abs)) - (N_alt(s_abs) / N_alt(h_sub)) x (h_sub - c_abs - P_bits(h_sub)), paired per pass; fp32, fp16",
                       "band_w": linear_band, "per_contrast": "as R4"},
            "E92-R7": {"what": "with the product absorbed its magnitude does not matter",
                       "statistic": "(r_h_sub - r_h_add) - (h_sub - h_add), paired per pass",
                       "band_w": linear_band["fp32"], "per_contrast": "as R4"},
            "E92-R8": {"what": "with moving sums the alternation's price follows the adder's flops (e88+flops)",
                       "contrasts": ["fp32.w_h_sub-w_h_add", "fp32.wr_h_sub-wr_h_add"], "per_contrast": "as R2, with pred_w = e88_flops_w"},
            "E92-R9": {"what": "a few hundred operand sign flips an op, every product positive: nothing to measure",
                       "contrasts": ["fp32.k_only-c_abs"], "band_w": ZERO_BAND, "per_contrast": "as R3"},
            "E92-R10": {"what": "fp16's two aligners: the 52-bit one costs more than the 29-bit one",
                        "contrasts": ["fp16.hh_sub-hl_sub"],
                        "per_contrast": "CONFIRMED if the 95% lower bound >= 0.5 x pred_w, REFUTED if the 95% upper bound < 0, else INCONCLUSIVE"},
            "E92-S1": {"what": "the session tie to E78 and to E90 (reported; a failure means the session moved)",
                       "cells": {"fp32.randn": 0.5, "fp16.randn": 0.5, "fp32.ones": 0.5, "fp16.ones": 0.5, "anchor_pi": 0.5, "int8.full": 0.25},
                       "cells_e90_only": {"fp32.signs": 0.5, "fp16.signs": 0.5},
                       "rule": "each cell's D within its band of E78's and of E90's; E90's own tiles of E90's"},
            "E92-S2": {"what": "the frozen models, out of sample (reported)",
                       "rule": "for every contrast: inside E88's band or not; rms of e88+flops over the contrasts with a rule; Q130(n)'s count of tiles inside its 95% interval"},
            "E92-S3": {"what": "the tie to E88, across cards (reported)",
                       "rule": "s_abs - c_abs within +-0.75 W of scale x M32s; c_abs - zeros within +-1.0 W of scale x F32"},
        },
        "not_scored_if": "fewer than 3 kept passes in the primary reduction: then every rule is scored on the registered dips-removed arm "
                         "(E86's posthoc_dips method), labelled as that arm; fewer than 3 there too: NOT SCORED.",
    }
    json.dump(reg, open(os.path.join(HERE, "predictions-e92.json"), "w"), indent=1)
    print(f"scale {scale}; p_alt {pa_fj:.0f} fJ per alternation; f {f_fj:.2f} fJ per flop bit; alt pred {alt_pred}; linear band {linear_band}")
    for k, c in C.items():
        print(f"{k:28s} {str(c['rule']):8s} bits {c['bits_w']:+.3f} alt {c['alt_w']:+.3f} e88 {c['e88']['mu']:+.3f} [{c['e88']['lo']:+.3f}, {c['e88']['hi']:+.3f}] "
              f"e88+flops {c['e88_flops_w']:+.3f} pred {c.get('pred_w')} thr {c.get('threshold_w')}")
    for k, v in bt.items():
        print(k, v)
    for n, v in out_tiles.items():
        q = v["q130n_predictor"]
        print(f"{n:16s} D_pred {v['D_pred_w']:7.3f} e88 {v['e88_D_w']:7.3f} q130n {q['point_w']:7.3f} {q['pi95_w']}")
    print("sha256 predictions-e92.json", hashlib.sha256(open(os.path.join(HERE, "predictions-e92.json"), "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
