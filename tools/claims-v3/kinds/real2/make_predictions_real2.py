#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9,<3.13"
# dependencies = ["numpy==1.26.4"]
# ///
"""Q132(r), stage 3 of 3: the FROZEN predictions and claims for the real2 tiles, before any card runs them. From committed
files only, each refused unless its sha256 is the one here; nothing is retyped.

    uv run --python 3.11 tools/claims-v3/kinds/real2/make_predictions_real2.py [--out <dir>] [--repo <root>]

Per tile:
  (a) D, switching W over the type's own zeros at 600 MHz on aifoundry3 (the E95 lane), from Q130(n)'s frozen predictor,
      unchanged (its frozen beta on make_real.features of the tile). The interval is NOT the predictor's own: it is fitted
      on the predictor's KNOWN OUT-OF-SAMPLE MISSES, measured - frozen point, as the E90 correction asks:
        float, ungated  every ungated tile of the format in E86 and E90 (fp32 n = 7, fp16 n = 9)
        float, gated    E90's six re-draws of the two zero-bearing rules, pooled over fp32 and fp16 (n = 6)
        int8, ungated   E86's three tiles and E90's int8 +-1 (n = 4)
        int8, gated     no E86 or E90 tile exists: E78's nested-LOO residuals on its six gated int8 kinds (n = 6; the one
                        place E78 enters, out of fold, and flagged)
      half-width = t(0.975, n) x the rms of those misses about zero, so a bias widens it. Beside it, labelled: the E86-only
      arm (t(0.975, 3) x the rms of E86's three tiles of the format), the class's mean miss as a bias arm, Amendment 1's
      half-width, and E78's random kind anchored by the predictor's own like-with-like ratio.
  (a') for a tile with a measured or same-pass partner: the predictor's OFFSET from that partner. E90-R5 is where the
      predictor earned its keep (0.28 W rms). Interval: t(0.975, 9) x 0.2765 W.
  (b) burst and sustained MHz on aifoundry2 under its own governor (the E96 lane), E83's relation applied to (a) through
      E83's conversion, the interval built as Amendment 1 builds it: the clock at the two ends of the (a) interval, widened
      in quadrature by 1.96 x E83's relation rms (10.6 / 8.4 MHz), clamped to [600, 800].
  (c) gated tiles only, stated separately from (a): the gate law. D = g * G + (1 - g) * L, with g the tile's own computed
      gated_lane_frac, L E78's measured D of the format's random kind (the cost of a fully live lane share) and G the mean of
      E78's two one-sided kinds (every lane gated, one operand's bus moving). No parameter is fitted. Its interval is
      t(0.975, n) x the rms of the law's misses on E78's gated random-magnitude kinds and E90's gated re-draws, per format.
  CLAIMS: what E95 and E96 test, each with thresholds and a way to fail.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=HERE)
ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..", "..", "..", "..")))
ap.add_argument("--real2", default=None, help="the directory holding real2.json and tiles/ (default --out)")
ARGS = ap.parse_args()
ROOT = ARGS.repo
R2 = ARGS.real2 or ARGS.out
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kinds/real"))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kspeed/e83"))
import make_real as MR  # noqa: E402
import predict_e83 as P83  # noqa: E402

MK = MR.MK
TYPES = MR.TYPES
PRED = "tools/claims-v3/kinds/real/predictions-real.json"
AMEND = "tools/claims-v3/kinds/real/amendment-1.json"
REALJ = "tools/claims-v3/kinds/real/real.json"
E86S = "docs/reports/data/2026-10-31-e86-real-tensors-energy/scored.json"
E90J = "docs/reports/data/2026-10-31-e90-signs-spread/e90.json"
E90S = "docs/reports/data/2026-10-31-e90-signs-spread/scored.json"
P90 = "tools/claims-v3/kinds/predictions-e90.json"
E91S = "docs/reports/data/2026-10-31-e91-real-tensors-aifoundry1/scored.json"
E87R = "docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json"
FROZEN = {PRED: "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941",
          AMEND: "f32e8a9087a9cf3bf60f29ff623c1a375537b43696df0dca24972ba220bc0d9e",
          REALJ: "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0",
          **MR.FROZEN_SHA}
READ_SHA = (E86S, E90J, E90S, P90, E91S, E87R)
REF = {"fp32": "randn", "fp16": "randn", "int8": "full"}
REL_RMS_MHZ = {"burst": 10.6, "sustained": 8.4}
GATED_MIN = 0.02
T975 = MR.T975


def tq(df):
    return T975[df - 1]


def rms(v):
    return float(np.sqrt(np.mean(np.square(v))))


def comb(pt, lo, hi, r):
    if lo >= 799.95:
        return [800.0, 800.0]
    e = 1.96 * r
    return [round(max(600.0, pt - ((pt - lo) ** 2 + e ** 2) ** 0.5), 1), round(min(800.0, pt + ((hi - pt) ** 2 + e ** 2) ** 0.5), 1)]


def main():
    shas = {}
    for p, want in FROZEN.items():
        got = MR.sha_file(os.path.join(ROOT, p))
        if got != want:
            sys.exit(f"refused: {p} sha256 {got} is not the frozen {want}")
        shas[p] = got
    for p in READ_SHA:
        shas[p] = MR.sha_file(os.path.join(ROOT, p))
    real2_path = os.path.join(R2, "real2.json")
    real2_sha = MR.sha_file(real2_path)
    spec = json.load(open(real2_path))
    PR = json.load(open(os.path.join(ROOT, PRED)))
    A1 = json.load(open(os.path.join(ROOT, AMEND)))
    E78 = json.load(open(os.path.join(ROOT, MR.E78J)))
    e86 = json.load(open(os.path.join(ROOT, E86S)))
    e90 = json.load(open(os.path.join(ROOT, E90J)))
    s90 = json.load(open(os.path.join(ROOT, E90S)))
    p90 = json.load(open(os.path.join(ROOT, P90)))
    D78 = {k: v["D"]["mean"] for k, v in E78["items"].items() if "D" in v}
    FZ = PR["predictor"]["per_type"]
    P, rows = MR.fit_predictor(E78, ROOT)
    for t in TYPES:
        if P[t]["selected"] != FZ[t]["selected"] or np.max(np.abs(np.array(P[t]["beta"]) - np.array(FZ[t]["beta"]))) > 1e-4:
            sys.exit(f"refused: the predictor for {t} does not reproduce the frozen one")
        P[t]["beta"] = FZ[t]["beta"]

    # ---------------------------------------------------------------- the known misses of Q130(n)'s points
    miss = {}
    for k, v in e86["tiles"].items():
        t = k.split(".")[0]
        miss[k] = {"type": t, "gated": 0.0, "miss_w": round(v["err_w"], 4), "source": f"{E86S} tiles.{k}.err_w"}
    for k, v in p90["tiles"].items():
        t = v["type"]
        miss[k] = {"type": t, "gated": v["stats"]["gated_lane_frac"], "miss_w": round(e90["items"][k]["D"]["mean"] - v["q130n_predictor"]["point_w"], 4),
                   "source": f"{E90J} items.{k}.D.mean - {P90} tiles.{k}.q130n_predictor.point_w"}
    int8_gated_nested = {}
    for kind in ("sparse50", "sparse90", "wsparse50", "wsparse90", "a_full_b_zeros", "a_zeros_b_full"):
        int8_gated_nested[kind] = round(-A1["nested_loo"]["int8"]["nested_residual_w"][kind], 4)   # residual is fit - measured
    classes = {
        "float_ungated/fp32": [k for k, v in miss.items() if v["type"] == "fp32" and v["gated"] < GATED_MIN],
        "float_ungated/fp16": [k for k, v in miss.items() if v["type"] == "fp16" and v["gated"] < GATED_MIN],
        "float_gated": [k for k, v in miss.items() if v["type"] in ("fp32", "fp16") and v["gated"] >= GATED_MIN],
        "int8_ungated": [k for k, v in miss.items() if v["type"] == "int8"],
    }
    cls = {}
    for c, ks in classes.items():
        vals = [miss[k]["miss_w"] for k in ks]
        cls[c] = {"tiles": {k: miss[k]["miss_w"] for k in ks}, "n": len(vals), "rms_w": round(rms(vals), 4), "mean_miss_w": round(float(np.mean(vals)), 4),
                  "t975": tq(len(vals)), "halfwidth_w": round(tq(len(vals)) * rms(vals), 3)}
    vals = list(int8_gated_nested.values())
    cls["int8_gated"] = {"tiles": {f"e78.int8.{k}": v for k, v in int8_gated_nested.items()}, "n": len(vals), "rms_w": round(rms(vals), 4), "mean_miss_w": round(float(np.mean(vals)), 4),
                         "t975": tq(len(vals)), "halfwidth_w": round(tq(len(vals)) * rms(vals), 3),
                         "note": f"no E86 or E90 tile gates in int8, so this class uses E78's nested-LOO out-of-fold residuals ({AMEND} nested_loo.int8.nested_residual_w), measured minus predicted; flagged as the one class not fitted on E86/E90"}
    e86only = {}
    for t in TYPES:
        vals = [miss[f"{t}.real_{m}"]["miss_w"] for m in ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")]
        e86only[t] = {"n": 3, "rms_w": round(rms(vals), 4), "t975": tq(3), "halfwidth_w": round(tq(3) * rms(vals), 3)}
    r5 = s90["rules"]["E90-R5"]["rms_w"]
    off_hw = round(tq(9) * r5, 3)

    # ---------------------------------------------------------------- the gate law, from E78's own anchors
    GL = {}
    for t in TYPES:
        L = D78[f"{t}.{REF[t]}"]
        if t == "int8":
            one = ["int8.a_full_b_zeros", "int8.a_zeros_b_full"]
        else:
            one = [f"{t}.a_randn_b_zeros", f"{t}.a_zeros_b_randn"]
        G = float(np.mean([D78[k] for k in one]))
        GL[t] = {"L_w": round(L, 4), "L_source": f"{MR.E78J} items.{t}.{REF[t]}.D.mean", "G_w": round(G, 4), "G_source": f"mean of {MR.E78J} items.{one[0]}.D.mean and items.{one[1]}.D.mean"}
    kinds = json.load(open(os.path.join(ROOT, MR.KINDSJ)))["kinds"]
    law = lambda t, g: g * GL[t]["G_w"] + (1.0 - g) * GL[t]["L_w"]
    law_known = {"fp32": {}, "fp16": {}, "int8": {}}
    gated_kinds = {"fp32": ("sparse50", "sparse90", "nn_like"), "fp16": ("sparse50", "sparse90", "wsparse50", "wsparse90", "nn_like"), "int8": ("wsparse50", "sparse90", "wsparse90")}
    for t, ks in gated_kinds.items():
        for k in ks:
            g = kinds[t][k]["stats"]["gated_lane_frac"]
            law_known[t][f"e78.{t}.{k}"] = {"g": g, "D_w": round(D78[f"{t}.{k}"], 4), "law_w": round(law(t, g), 4), "miss_w": round(D78[f"{t}.{k}"] - law(t, g), 4)}
    for k, v in p90["tiles"].items():
        g = v["stats"]["gated_lane_frac"]
        if g >= GATED_MIN:
            t = v["type"]
            law_known[t][f"e90.{k}"] = {"g": g, "D_w": round(e90["items"][k]["D"]["mean"], 4), "law_w": round(law(t, g), 4), "miss_w": round(e90["items"][k]["D"]["mean"] - law(t, g), 4)}
    for t in TYPES:
        vals = [v["miss_w"] for v in law_known[t].values()]
        GL[t].update({"known_misses": law_known[t], "n": len(vals), "rms_w": round(rms(vals), 4), "mean_miss_w": round(float(np.mean(vals)), 4), "t975": tq(len(vals)),
                      "halfwidth_w": round(tq(len(vals)) * rms(vals), 3),
                      "ratio_measured_over_law_range": [round(min(v["D_w"] / v["law_w"] for v in law_known[t].values()), 3), round(max(v["D_w"] / v["law_w"] for v in law_known[t].values()), 3)]})
        pts = list(law_known[t].values())
        GL[t]["known_slope_of_D_on_live_share_over_L"] = round(float(np.polyfit([1.0 - v["g"] for v in pts], [v["D_w"] for v in pts], 1)[0]) / GL[t]["L_w"], 3)
    e86_real_mean = {t: float(np.mean([e86["tiles"][f"{t}.real_{m}"]["D"]["mean"] for m in ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")])) for t in TYPES}

    # ---------------------------------------------------------------- E83's relation, E82's scale, as make_real.py
    E83 = json.load(open(os.path.join(ROOT, MR.E83P)))
    F64 = json.load(open(os.path.join(ROOT, MR.E64F)))
    Q = json.load(open(os.path.join(ROOT, MR.Q130C)))["predictions"]
    rel = P83.Rel({int(k): v for k, v in F64["fit"]["B"].items()})
    Wb, sb = E83["relation"]["burst"]["W_star_w"], E83["relation"]["burst"]["sigma_w"]
    Ws, ss = E83["relation"]["sustained"]["W_star_w"], E83["relation"]["sustained"]["sigma_w"]
    c0 = {t: Q[f"{t}/zeros"]["c_w_a2_600mhz"] for t in TYPES}

    def clk(t, D):
        c = c0[t] + D / P83.XFER
        (b, b8), (s, s8) = rel.f(c, Wb, sb), rel.f(c, Ws, ss)
        return c, b, b8, s, s8

    ref_fit, ref_meas = {}, {}
    for t in TYPES:
        pts = {e["kind"]: e for e in FZ[t]["e78_points"]}
        ref_fit[t], ref_meas[t] = pts[REF[t]]["fit_w"], pts[REF[t]]["D_w"]
    ref_clk = {t: {"burst_mhz": round(clk(t, ref_meas[t])[1], 1), "sus_mhz": round(clk(t, ref_meas[t])[3], 1)} for t in TYPES}

    # ---------------------------------------------------------------- per tile
    def predict(t, name, raw, f, stats, zero, group, tier, partner=None):
        beta = dict(zip(FZ[t]["cols"], FZ[t]["beta"]))
        pt = round(max(float(sum(b * f[c] for c, b in beta.items())), 0.0), 3)
        g = stats["gated_lane_frac"]
        klass = ("float_" if t != "int8" else "int8_") + ("gated" if g >= GATED_MIN else "ungated")
        ck = klass + (f"/{t}" if klass == "float_ungated" else "")
        hw = cls[ck]["halfwidth_w"]
        lo, hi = round(max(pt - hw, 0.0), 3), round(pt + hw, 3)
        c, b, b8, s, s8 = clk(t, pt)
        _, b_lo, _, s_lo, _ = clk(t, hi)
        _, b_hi, _, s_hi, _ = clk(t, lo)
        pd = MR.predict_D(P, t, f, rows[t])
        cols_out = {cc: {"tile": f[cc], "e78_range": FZ[t]["feature_range_e78"][cc], "beta": beta[cc]} for cc in FZ[t]["cols"]
                    if not (FZ[t]["feature_range_e78"][cc][0] - 1e-9 <= f[cc] <= FZ[t]["feature_range_e78"][cc][1] + 1e-9)}
        rec = {
            "tile": f"tools/claims-v3/kinds/real2/tiles/{t}/{name}.bin", "tile_sha256": hashlib.sha256(raw).hexdigest(), "group": group, "tier": tier,
            "gated_lane_frac": g, "bus_bits_per_op": stats["bus_bits_per_op"],
            "a_zero_word_frac": stats["a"]["zero_word_frac"], "a_zero_elem_frac": stats["a"]["zero_elem_frac"], "b_zero_word_frac": stats["b"]["zero_word_frac"],
            "a_aifoundry3_600mhz": {
                "D_w": pt, "class": ck, "scoring_interval_w": [lo, hi], "scoring_halfwidth_w": hw,
                "e86_only_arm_w": [round(max(pt - e86only[t]["halfwidth_w"], 0.0), 3), round(pt + e86only[t]["halfwidth_w"], 3)],
                "bias_arm_w": round(pt + cls[ck]["mean_miss_w"], 3), "amendment1_halfwidth_w": A1["nested_loo"][t]["nested_pi95_halfwidth_w"],
                "model": FZ[t]["selected"], "terms_w": {cc: round(bb * f[cc], 3) for cc, bb in beta.items()},
                "features_outside_e78_range": cols_out, "nearest_e78_kind": pd["nearest_e78_kind"], "nearest_e78_kind_D_w": pd["nearest_e78_kind_D_w"],
                "ratio_to_ref_measured_e78": round(pt / ref_meas[t], 4), "ratio_to_ref_model_fit": round(pt / ref_fit[t], 4), "ref_kind": REF[t]},
            "b_aifoundry2_governor": {
                "c_w": round(c, 3), "burst_mhz": round(b, 1), "burst_share800": round(b8, 3), "burst_limit": "none" if b8 >= P83.NONE_SHARE else "power", "burst_rate": round(P83.SH.rate_t(t, b), 3),
                "burst_scoring_interval_mhz": comb(b, b_lo, b_hi, REL_RMS_MHZ["burst"]), "burst_D_propagated_range_mhz": [round(b_lo, 1), round(b_hi, 1)],
                "sus_mhz": round(s, 1), "sus_share800": round(s8, 3), "sus_limit": "none" if s8 >= P83.NONE_SHARE else "thermal", "sus_rate": round(P83.SH.rate_t(t, s), 3),
                "sus_scoring_interval_mhz": comb(s, s_lo, s_hi, REL_RMS_MHZ["sustained"]), "sus_D_propagated_range_mhz": [round(s_lo, 1), round(s_hi, 1)],
                "rate_unit": "TOPS" if t == "int8" else "TFLOPS"},
        }
        if g >= GATED_MIN:
            d = law(t, g)
            rec["c_gate_law"] = {"g": g, "live_share": round(1 - g, 6), "D_w": round(d, 3), "scoring_interval_w": [round(max(d - GL[t]["halfwidth_w"], 0.0), 3), round(d + GL[t]["halfwidth_w"], 3)], "halfwidth_w": GL[t]["halfwidth_w"],
                                 "D_w_with_L_from_e86_real_tiles": round(g * GL[t]["G_w"] + (1 - g) * e86_real_mean[t], 3),
                                 "burst_mhz": round(clk(t, d)[1], 1), "sus_mhz": round(clk(t, d)[3], 1)}
        gnum = zero.get("gated_if_gate_took_numeric_zero") if zero else None
        if zero and gnum is not None and gnum >= GATED_MIN and g < GATED_MIN:
            d = law(t, gnum)
            rec["c_if_gate_took_numeric_zero"] = {"g_numeric": gnum, "D_w": round(d, 3), "scoring_interval_w": [round(max(d - GL[t]["halfwidth_w"], 0.0), 3), round(d + GL[t]["halfwidth_w"], 3)], "note": "the gate as built tests word == 0, so -0.0 passes; this is what the law says if it did not"}
        return rec

    preds = {}
    for t in TYPES:
        for name, e in spec["tiles"].get(t, {}).items():
            raw = open(os.path.join(R2, e["file"]), "rb").read()
            if MR.sha_bytes(raw) != e["sha256"]:
                sys.exit(f"refused: {t}/{name} differs from real2.json")
            f = MR.features(raw, t)
            if f != e["features"]:
                sys.exit(f"refused: {t}/{name} features differ from real2.json")
            preds[f"{t}/{name}"] = predict(t, name, raw, f, e["stats"], e.get("zero"), e["group"], e["tier"])
    # the E86 tiles run again beside them: Q130(n)'s frozen points and E86's measurement
    e86_pairs = {}
    for r in spec["e86_tiles_rerun_with_them"]:
        t, m = r["type"], r["matrix"]
        fzr = PR["tiles"][f"{t}/{m}"]
        e86_pairs[f"{t}.real_{m}"] = {"file": r["file"], "sha256": r["sha256"], "frozen_point_w": fzr["a_aifoundry3_600mhz"]["D_w"], "e86_measured_D_w": round(e86["tiles"][f"{t}.real_{m}"]["D"]["mean"], 3),
                                      "e86_measured_ci95_w": round(e86["tiles"][f"{t}.real_{m}"]["D"]["ci95"], 3), "e86_ratio_to_ref": round(e86["tiles"][f"{t}.real_{m}"]["ratio_to_ref"]["mean"], 4),
                                      "b_aifoundry2_governor": {kk: fzr["b_aifoundry2_governor"][kk] for kk in ("c_w", "burst_mhz", "sus_mhz", "burst_limit", "sus_limit")}}
    # (a') offsets from a partner
    partners = {"fp16/gpt2_l6_mlp_down_fp16fwd": "fp16.real_l6_mlp_down", "fp16/gpt2_l6_attn_qk_fp16fwd": "fp16.real_l6_attn_qk",
                "int8/gpt2_l6_down_per_token": "int8.real_l6_mlp_down", "int8/gpt2_l6_down_p9999": "int8.real_l6_mlp_down", "int8/gpt2_l6_down_p999": "int8.real_l6_mlp_down",
                "int8/gpt2_l11_down_p999": "int8/gpt2_l11_down_maxabs", "int8/gpt2_l11_down_asym": "int8/gpt2_l11_down_maxabs", "int8/vgg16_fc2_asym": "int8/vgg16_fc2"}
    for k, p in partners.items():
        if "." in p:
            t_, m_ = p.split(".real_")
            pp = PR["tiles"][f"{t_}/{m_}"]["a_aifoundry3_600mhz"]["D_w"]
            meas = round(e86["tiles"][p]["D"]["mean"], 3)
        else:
            pp, meas = preds[p]["a_aifoundry3_600mhz"]["D_w"], None
        off = round(preds[k]["a_aifoundry3_600mhz"]["D_w"] - pp, 3)
        preds[k]["a_prime_offset"] = {"partner": p, "offset_w": off, "interval_w": [round(off - off_hw, 3), round(off + off_hw, 3)], "halfwidth_w": off_hw, "halfwidth_rule": f"t(0.975, 9) x E90-R5's rms {round(r5, 4)} W",
                                      **({"anchored_on_e86_measured_partner_w": round(meas + off, 3)} if meas is not None else {})}

    def names(group, t=None, tier=1):
        return [k for k, v in preds.items() if v["group"] == group and (t is None or k.startswith(t + "/")) and (tier is None or v["tier"] == tier)]

    def predicted_ratio(ks):
        return round(float(np.mean([preds[k]["a_aifoundry3_600mhz"]["ratio_to_ref_measured_e78"] for k in ks])), 4)

    cells_e1 = {"gpt2/fp32": ["fp32/gpt2_l3_mlp_down", "fp32/gpt2_l9_attn_qk"], "gpt2/fp16": ["fp16/gpt2_l9_attn_qk"], "bert/fp32": ["fp32/bert_l6_up"], "bert/fp16": ["fp16/bert_l6_up"], "vit/fp32": ["fp32/vit_l5_down"], "vit/fp16": ["fp16/vit_l5_down"]}
    gated_float = {t: [k for k, v in preds.items() if k.startswith(t + "/") and v["group"] == "Z" and v["tier"] == 1] for t in ("fp32", "fp16")}

    claims = {
        "conventions": ("All energy claims are on D, each tile's board power over its own type's all-zeros level, at the E95 lane's primary leakage slope, on aifoundry3 at 600 MHz. r(x) = per pass D(x) / D(ref), ref the "
                        "same pass's fp32.randn, fp16.randn or int8.full (its three runs' mean). Intervals are t(0.975, n - 1) x SE over kept passes; a difference is paired within the pass. PASS, FAIL or INCONCLUSIVE as "
                        "each claim says. Fewer than 3 kept passes: NOT SCORED. A lane that drops a tile says so, and a claim short of its population is UNDER-RESOLVED, never PASS."),
        "E95": {
            "C1_within_2pct": {
                "claim": "Real fp32 and fp16 tiles with no exact zeros cost within 2% of random data of their format over its zeros, in every model",
                "cells": cells_e1, "band": [0.98, 1.02],
                "rule": "per cell, mean r over its tiles per pass, its 95% interval over passes: cell PASS if inside the band, FAIL if entirely outside, else INCONCLUSIVE. Claim PASS if every cell passes, FAIL if any fails, else INCONCLUSIVE",
                "predicted_ratio_per_cell_to_e78_ref": {c: predicted_ratio(k) for c, k in cells_e1.items()},
                "predicted_ratio_per_cell_to_ref_model_fit": {c: round(float(np.mean([preds[x]["a_aifoundry3_600mhz"]["ratio_to_ref_model_fit"] for x in k])), 4) for c, k in cells_e1.items()},
                "how_it_can_fail": "an attention tile in fp16 already read 0.971 and 0.966 (E86, E91), below the band; a model whose numbers sit further from random fails it"},
            "C2_below_random": {
                "claim": "On average real fp32 and fp16 tiles with no exact zeros sit below random data of their format",
                "tiles": {t: names("N", t) for t in ("fp32", "fp16")},
                "rule": "per format, mean r over its N tiles per pass: PASS if the 95% upper bound < 1, FAIL if the lower bound > 1, else INCONCLUSIVE (E86-R3's form). Both formats must pass",
                "predicted_ratio_to_e78_ref": {t: predicted_ratio(names("N", t)) for t in ("fp32", "fp16")}},
            "C3a_live_share_tiles": {
                "claim": "A ReLU tile's power follows its live share: each fp32 and fp16 ReLU tile lies inside the gate law's interval",
                "tiles": gated_float,
                "rule": "count of tiles whose D lies inside c_gate_law.scoring_interval_w: PASS if all, FAIL if two or more lie outside, else INCONCLUSIVE",
                "law": "D = g G + (1 - g) L, gate_law.<type>"},
            "C3b_live_share_slope": {
                "claim": "Across the ReLU tiles of a format, D rises with the live share at about the random kind's full cost",
                "tiles": gated_float, "band_slope_over_L": [0.85, 1.25],
                "rule": "per format, the least-squares slope of D on (1 - g) over its tiles, divided by E78's L: PASS if both formats lie inside the band, FAIL if either lies outside",
                "known_slope_over_L": {t: GL[t]["known_slope_of_D_on_live_share_over_L"] for t in ("fp32", "fp16")},
                "known": "the same slope over E78's gated kinds and E90's gated re-draws: gate_law.<type>.known_misses",
                "predicted_slope_over_L_from_a": {t: round(float(np.polyfit([1.0 - preds[k]["gated_lane_frac"] for k in gated_float[t]], [preds[k]["a_aifoundry3_600mhz"]["D_w"] for k in gated_float[t]], 1)[0]) / GL[t]["L_w"], 3) for t in ("fp32", "fp16")}},
            "C4_word_grouping": {
                "claim": "The same numbers cost more in fp16 than in fp32 because a zero must fill the whole 32-bit word",
                "pairs": {"vgg16_fc2": ["fp16/vgg16_fc2", "fp32/vgg16_fc2"], "resnet18_l3c1": ["fp16/resnet18_l3c1", "fp32/resnet18_l3c1"], "t5small_l0_down": ["fp16/t5small_l0_down", "fp32/t5small_l0_down"]},
                "rule": "per pair, r(fp16) - r(fp32), paired: PASS if the 95% lower bound > 0, FAIL if the upper bound < 0, else INCONCLUSIVE. Claim PASS if all three pass, FAIL if any fails",
                "predicted": {p: {"g_fp32": preds[f"fp32/{p}"]["gated_lane_frac"], "g_fp16": preds[f"fp16/{p}"]["gated_lane_frac"], "r_fp32": preds[f"fp32/{p}"]["a_aifoundry3_600mhz"]["ratio_to_ref_measured_e78"], "r_fp16": preds[f"fp16/{p}"]["a_aifoundry3_600mhz"]["ratio_to_ref_measured_e78"]} for p in ("vgg16_fc2", "resnet18_l3c1", "t5small_l0_down")}},
            "C5_int8_bits_or_gate": {
                "claim": "In int8 a real ReLU tile's power follows its operand bits more than its live share: the predictor (a) lies nearer the measurement than the gate law (c)",
                "tiles": ["int8/resnet18_l3c1", "int8/vgg16_fc2"],
                "rule": "per tile, |D - (a)| against |D - (c)|: PASS if (a) is nearer on both tiles, FAIL if (c) is nearer on both, else INCONCLUSIVE",
                "predicted": {k: {"a_w": preds[k]["a_aifoundry3_600mhz"]["D_w"], "c_w": preds[k]["c_gate_law"]["D_w"]} for k in ("int8/resnet18_l3c1", "int8/vgg16_fc2")},
                "why_this_side": "E78's int8 sparse50 gates 7% of its lane-cycles and its saving follows its bits; E86's real int8 tiles cost 0.78-0.89 of full with no gate at all"},
            "C6_calibration_lever": {
                "claim": "On a GELU layer with one huge activation the calibration is a lever several times larger than any data effect: 99.9th percentile clip against max-abs",
                "pair": ["int8/gpt2_l11_down_p999", "int8/gpt2_l11_down_maxabs"], "threshold_w": 2.0,
                "predicted_w": preds["int8/gpt2_l11_down_p999"]["a_prime_offset"]["offset_w"],
                "rule": "paired D difference: PASS if the 95% lower bound >= 2.0 W, FAIL if the upper bound < 2.0 W, else INCONCLUSIVE"},
            "C7_calibration_rank": {
                "claim": "On E86's window the calibrations rank committed < per-token < 99.9th percentile by power; the 99.99th percentile clip sits beside committed",
                "reference": "int8.real_l6_mlp_down",
                "predicted_offsets_w": {k: preds[k]["a_prime_offset"]["offset_w"] for k in ("int8/gpt2_l6_down_p9999", "int8/gpt2_l6_down_per_token", "int8/gpt2_l6_down_p999")},
                "rule": "paired differences against the reference: PASS if per-token's and 99.9th's lower bounds > 0 and p9999's interval lies inside +-0.40 W; FAIL if per-token's or 99.9th's upper bound < 0, or p9999's interval lies entirely outside +-0.40 W; else INCONCLUSIVE",
                "note": "the predicted steps are 0.04-0.24 W, at the size of E86's paired noise, so INCONCLUSIVE is the likely outcome; beside the verdict report Spearman over the four and each tile's r"},
            "C8_asym_turns_the_gate_off": {
                "claim": "TFLite-style asymmetric activations show the gate nothing on a ReLU tile, so the same numbers cost more than the symmetric tile",
                "pair": ["int8/vgg16_fc2_asym", "int8/vgg16_fc2"], "predicted_w": preds["int8/vgg16_fc2_asym"]["a_prime_offset"]["offset_w"],
                "rule": "paired D difference: PASS if the 95% lower bound > 0.5 W, FAIL if the upper bound < 0, else INCONCLUSIVE"},
            "C9_negative_zero": {
                "claim": "The gate tests word == 0, so -0.0 passes it: a tile whose A is {:.0%} -0.0 (the layer: {:.0%}) costs more than the gate law allows if the gate took numeric zeros".format(spec["tiles"]["fp32"]["vit_l11_down"]["zero"]["a"]["neg_zero_elem_frac"], json.load(open(os.path.join(R2, "capture.json")))["products"]["vit_l11_ff_down"]["stats"]["A"]["neg_zero_frac"]),
                "tile": "fp32/vit_l11_down", "prediction_gate_blind_w": preds["fp32/vit_l11_down"]["a_aifoundry3_600mhz"]["D_w"], "prediction_if_gate_took_numeric_zero": preds["fp32/vit_l11_down"].get("c_if_gate_took_numeric_zero"),
                "rule": "PASS if D's 95% lower bound > the upper end of c_if_gate_took_numeric_zero.scoring_interval_w, FAIL if D's 95% upper bound <= that end, else INCONCLUSIVE. Reported beside: r, which says what a live lane multiplying -0.0 costs"},
            "C10_bf16_weights": {
                "claim": "T5's weights sit on the bf16 grid (all low 16 mantissa bits zero), so a no-zero T5 tile costs clearly less than random fp32, unlike E86's full-mantissa tiles",
                "tile": "fp32/t5small_l0_up", "threshold_r": 0.97, "predicted_r": preds["fp32/t5small_l0_up"]["a_aifoundry3_600mhz"]["ratio_to_ref_measured_e78"],
                "rule": "r: PASS if the 95% upper bound < 0.97, FAIL if the lower bound >= 0.97, else INCONCLUSIVE"},
            "C11_fp16_forward": {
                "claim": "An fp16 forward pass costs what rounding the fp32 activations costs",
                "pair": ["fp16/gpt2_l6_mlp_down_fp16fwd", "fp16.real_l6_mlp_down"], "band_w": 0.5, "predicted_w": preds["fp16/gpt2_l6_mlp_down_fp16fwd"]["a_prime_offset"]["offset_w"],
                "rule": "paired D difference: PASS if the 95% interval lies inside +-0.50 W, FAIL if entirely outside, else INCONCLUSIVE"},
            "C12_intervals": {
                "claim": "The frozen (a) intervals hold",
                "population": "the 25 new tier-1 tiles, and any tier-2 tile run, counted apart",
                "rule": "count of new tier-1 tiles with D inside a_aifoundry3_600mhz.scoring_interval_w: PASS if >= 20 of 25, FAIL if < 18, else INCONCLUSIVE. Beside it, labelled: the count inside the E86-only arm; rms per class against the class's known rms; for the ungated float tiles the no-model baseline 'each tile costs E78's random kind'"},
        },
        "E96": {
            "S1_intervals": {"claim": "E83's relation fed (a) holds the clocks", "rule": "bursts: count inside b_aifoundry2_governor.burst_scoring_interval_mhz, sustained: count inside sus_scoring_interval_mhz; each PASS if >= 80% of the tiles run, FAIL if < 60%, else INCONCLUSIVE"},
            "S2_gate_buys_speed": {
                "claim": "A gated float tile whose (a) is under 15 W bursts well above same-session random data of its format",
                "tiles": [k for k in preds if preds[k]["group"] == "Z" and k.split("/")[0] in ("fp32", "fp16") and preds[k]["a_aifoundry3_600mhz"]["D_w"] < 15.0],
                "predicted_burst_mhz": {k: preds[k]["b_aifoundry2_governor"]["burst_mhz"] for k in preds if preds[k]["group"] == "Z" and k.split("/")[0] in ("fp32", "fp16") and preds[k]["a_aifoundry3_600mhz"]["D_w"] < 15.0},
                "rule": "per tile, burst minus the same session's randn burst of its format: PASS if every tile >= +40 MHz, FAIL if any tile < +15 MHz, else INCONCLUSIVE"},
            "S2b_gate_buys_sustained_clock": {
                "claim": "The same tiles also sustain well above same-session random data of their format",
                "tiles": [k for k in preds if preds[k]["group"] == "Z" and k.split("/")[0] in ("fp32", "fp16") and preds[k]["a_aifoundry3_600mhz"]["D_w"] < 15.0],
                "predicted_sus_mhz": {k: preds[k]["b_aifoundry2_governor"]["sus_mhz"] for k in preds if preds[k]["group"] == "Z" and k.split("/")[0] in ("fp32", "fp16") and preds[k]["a_aifoundry3_600mhz"]["D_w"] < 15.0},
                "rule": "per tile, sustained minus the same session's randn sustained of its format: PASS if every tile >= +50 MHz, FAIL if any tile < +15 MHz, else INCONCLUSIVE. One sustained run's 1 sigma is +-15.6 MHz on the slope (E83 C3)"},
            "S3_no_zero_runs_at_random_speed": {"claim": "Real fp32 and fp16 tiles with no exact zeros burst within 15 MHz of same-session randn (E87-S2's form)", "tiles": {t: names("N", t) for t in ("fp32", "fp16")},
                                                "rule": "per format, the tiles' mean burst minus randn's: PASS if |difference| <= 15 MHz in both formats, FAIL otherwise"},
            "S4_limits": {"claim": "The sustained limit is called right", "rule": "count of sus_limit right: PASS if >= 80% of the tiles run, FAIL if < 60%, else INCONCLUSIVE"},
            "S5_relation_on_measured_power": {"claim": "E83's relation on each tile's measured c gives its clocks (E87-S1's form)", "rule": "burst and sustained rms each <= 15 MHz: PASS; either > 25 MHz: FAIL; else INCONCLUSIVE"},
        },
    }

    # E96: what is worth a sustained run
    e96_burst_all = [k for k in preds if preds[k]["tier"] == 1]
    e96_sustained = ["fp32/resnet18_l2c1", "fp32/resnet18_l3c1", "fp16/resnet18_l3c1", "fp32/vgg16_fc2", "fp16/vgg16_fc2", "fp32/t5small_l0_down", "fp16/t5small_l0_down", "fp32/t5small_l0_up", "fp32/vit_l11_down",
                     "fp32/bert_l6_up", "fp16/vit_l5_down", "int8/vgg16_fc2", "int8/vgg16_fc2_asym", "int8/gpt2_l11_down_maxabs", "int8/gpt2_l11_down_p999"]

    out = {
        "experiment": "Q132(r)", "date": "2026-11-01",
        "what": ("FROZEN predictions and claims for the real2 tiles, made before any card ran them: (a) D at 600 MHz on aifoundry3 (E95) from Q130(n)'s frozen predictor with an interval fitted on its known out-of-sample misses; "
                 "(a') its offset from a partner tile; (b) the burst and sustained clock under aifoundry2's own governor (E96) from E83's relation; (c) the gate law for gated tiles, separately; and the claims E95 and E96 test."),
        "inputs_sha256": shas, "real2_json_sha256": real2_sha,
        "predictor": {"source": PRED, "per_type": {t: {"selected": FZ[t]["selected"], "cols": FZ[t]["cols"], "beta": FZ[t]["beta"]} for t in TYPES},
                      "note": "unchanged. E90's correction binds: it tracks a re-draw's offset from a measured tile (0.28 W rms) and misses absolute prices by 0.6-2.0 W; the intervals below say so, and it is a post-hoc fit, not a mechanism"},
        "known_misses": {"definition": "measured D minus Q130(n)'s frozen point, W, tiles the predictor was not fitted on", "classes": cls, "e86_only_arm": e86only},
        "offset_rule": {"e90_r5_rms_w": round(r5, 4), "source": f"{E90S} rules.E90-R5.rms_w", "t975_df9": tq(9), "halfwidth_w": off_hw},
        "gate_law": {"form": "D = g G + (1 - g) L; g = the tile's computed gated_lane_frac (make_kinds.tile_stats); no fitted parameter", "per_type": GL, "e86_real_tile_mean_D_w": {t: round(v, 3) for t, v in e86_real_mean.items()}, "gated_min": GATED_MIN},
        "relation_e83": {"source": MR.E83P, "burst": {"W_star_w": Wb, "sigma_w": sb}, "sustained": {"W_star_w": Ws, "sigma_w": ss}, "c_zeros_w": c0, "xfer": P83.XFER, "none_share_800": P83.NONE_SHARE,
                         "relation_rms_mhz": REL_RMS_MHZ, "interval": "the clock at the ends of the (a) scoring interval, widened in quadrature by 1.96 x relation rms, clamped to [600, 800]; a range wholly at the cap stays [800, 800] (Amendment 1's rule)",
                         "e87_note": "E87 read this relation on real tiles: 10.7 / 6.1 MHz rms frozen; its session's heat path ran 0.5 C warmer than E80's, and single int8 sustained runs land either side of the 65 C trip whatever the data",
                         "random_kind_from_relation_mhz": ref_clk},
        "references_e78": {t: {"kind": REF[t], "D_measured_w": ref_meas[t], "D_model_fit_w": ref_fit[t]} for t in TYPES},
        "e86_tiles_rerun": e86_pairs,
        "e95_suggested": {"items": "the 25 new tier-1 tiles as <type>.r2_<name>, E86's fp16.real_l6_mlp_down and int8.real_l6_mlp_down, E78's six anchors three times a pass, the anchor_pi tie twice: 47 runs and 2 burn-ins a pass",
                          "tier1": [k for k in preds if preds[k]["tier"] == 1], "tier2": [k for k in preds if preds[k]["tier"] == 2],
                          "smoke": ["fp32/vgg16_fc2", "fp16/t5small_l0_down", "int8/gpt2_l11_down_maxabs"],
                          "estimate": "E86 ran 32 runs and 2 burn-ins in 6.0-6.7 min, about 12 s a run, so 49 runs is about 10 min a pass and four passes about 40 card-minutes, with the smoke inside the 45; tier 2 adds 5 runs, about 1 min a pass"},
        "e96_suggested": {"bursts": "every tier-1 tile and E87's six anchors, two passes", "sustained_first": e96_sustained,
                          "why": "27 tiles in E87's full shape is about 75 card-minutes (E87: 13 s a burst, 100 s a sustained run). The ungated float tiles are predicted at random data's clock, so their sustained runs say least"},
        "tiles": preds,
        "claims": claims,
    }
    pjson = json.dumps(out, indent=1) + "\n"
    with open(os.path.join(ARGS.out, "predictions-real2.json"), "w") as fh:
        fh.write(pjson)

    lines = []
    lines.append("known misses (measured - frozen point): " + "; ".join(f"{c}: n {v['n']} rms {v['rms_w']} mean {v['mean_miss_w']} +-{v['halfwidth_w']}" for c, v in cls.items()))
    lines.append("E86-only arm: " + "; ".join(f"{t} rms {v['rms_w']} +-{v['halfwidth_w']}" for t, v in e86only.items()))
    lines.append(f"offset rule: E90-R5 rms {round(r5, 4)} +-{off_hw}")
    for t in TYPES:
        g_ = GL[t]
        lines.append(f"gate law {t}: L {g_['L_w']} G {g_['G_w']} known n {g_['n']} rms {g_['rms_w']} mean {g_['mean_miss_w']} +-{g_['halfwidth_w']} ratio {g_['ratio_measured_over_law_range']}")
    lines.append(f"{'tile':34s} t g     Azw   Aze   bus    (a)D   [scoring]        r_e78  (c)law [scoring]       burst [score]        sus [score]         lim")
    for k, v in preds.items():
        a_, b_ = v["a_aifoundry3_600mhz"], v["b_aifoundry2_governor"]
        c_ = v.get("c_gate_law")
        lines.append(f"{k:34s} {v['tier']} {v['gated_lane_frac']:.3f} {v['a_zero_word_frac']:.3f} {v['a_zero_elem_frac']:.3f} {v['bus_bits_per_op']:6d} {a_['D_w']:6.2f} [{a_['scoring_interval_w'][0]:5.2f},{a_['scoring_interval_w'][1]:5.2f}] {a_['ratio_to_ref_measured_e78']:.3f} "
                     + (f"{c_['D_w']:6.2f} [{c_['scoring_interval_w'][0]:5.2f},{c_['scoring_interval_w'][1]:5.2f}]" if c_ else " " * 21)
                     + f" {b_['burst_mhz']:6.1f} [{b_['burst_scoring_interval_mhz'][0]:.0f},{b_['burst_scoring_interval_mhz'][1]:.0f}] {b_['sus_mhz']:6.1f} [{b_['sus_scoring_interval_mhz'][0]:.0f},{b_['sus_scoring_interval_mhz'][1]:.0f}] {b_['sus_limit']}"
                     + (f" OUT {list(a_['features_outside_e78_range'])}" if a_["features_outside_e78_range"] else "") + (f" off {v['a_prime_offset']['offset_w']:+.3f}" if "a_prime_offset" in v else ""))
    lines.append(f"predictions-real2.json sha256 {hashlib.sha256(pjson.encode()).hexdigest()}")
    txt = "\n".join(lines) + "\n"
    print(txt)
    with open(os.path.join(ARGS.out, "predictions-real2.txt"), "w") as fh:
        fh.write(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
