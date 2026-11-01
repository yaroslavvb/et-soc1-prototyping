#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9,<3.13"
# dependencies = ["numpy==1.26.4"]
# ///
"""Q130(n) Amendment 1: the intervals E86, E87 and E91 score against, written Sat 31 Oct 2026 after verification and
before any card ran a real tile.

predictions-real.json is NOT changed. Its points and its frozen intervals stand as committed in 7d5b99af (sha256
bab33bee...), and this script refuses to run unless that file, real.json and make_real.py's frozen inputs have their
committed sha256. It computes, from committed files only:

  1. (a) The nested leave-one-kind-out (LOO) rms of make_real.py's whole procedure. In each fold the feature set is
     chosen again on the other kinds by make_real's own rule (lowest LOO rms to 4 decimals, ties to fewer non-zero
     terms) with make_real's own exact NNLS, then fitted on those kinds and scored on the held-out one. Choosing the
     best of 11 candidates by their LOO rms makes the winner's own LOO rms optimistic; the nested rms is not.
     Scoring half-width: t(0.975, n - p) x nested rms, as make_real.py builds its interval (p = the selected set's
     non-zero terms).
  2. (E91) The amended (a) interval divided by E82's per-type card scale. It leaves out the card-scale spread.
  3. (b) The clock at the two ends of the amended (a) interval through E83's own Rel (a D-propagated range), widened
     on each side, in quadrature, by 1.96 x E83's relation rms on measured power over the kinds below 800 MHz
     (10.6 MHz burst, 8.4 MHz sustained: E83's README, Results 1 and rule S1), and clamped to Rel's [600, 800] MHz.
     A burst whose whole range sits at the 800 MHz cap stays [800, 800]: E83's cells at the cap read 800.0.
  4. Like with like: each tile's D against the predictor's own fit for randn (fp32, fp16) or full (int8), and that
     ratio times E78's measured value.
  5. Informational, never scored: the runner-up feature set's predictions; every model column's range check, B
     included; the nearest E78 kind by both metrics the lane used; the 20-window band against both interval widths.
  6. With --hf-dir (the three files make_real.py takes): the int8 calibration sensitivity. The same windows, with the
     activations re-quantised four other common ways, pushed through the same predictor.

    uv run --python 3.11 tools/claims-v3/kinds/real/amend_real.py [--hf-dir <dir>] [--out <dir>]
"""
import argparse
import hashlib
import json
import os
import platform
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_real as MR  # noqa: E402

ROOT = MR.ROOT
MK = MR.MK
PRED = "tools/claims-v3/kinds/real/predictions-real.json"
SPEC = "tools/claims-v3/kinds/real/real.json"
FROZEN = {PRED: "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941",
          SPEC: "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0"}
REL_RMS_MHZ = {"burst": 10.6, "sustained": 8.4}
REF = {"fp32": "randn", "fp16": "randn", "int8": "full"}
NAMES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")


def loo_rms(X, y):
    r = []
    for i in range(len(y)):
        m = np.ones(len(y), bool)
        m[i] = False
        r.append(float(X[i] @ MR.nnls(X[m], y[m]) - y[i]))
    return round(float(np.sqrt(np.mean(np.square(r)))), 4)


def nested_loo(rows_t):
    y = np.array([r["D"] for r in rows_t])
    n = len(y)
    Xs = {name: np.array([[r["f"][c] for c in cols] for r in rows_t]) for name, cols in MR.CANDIDATES.items()}
    outer, chosen = [], []
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        table = {}
        for name, X in Xs.items():
            b = MR.nnls(X[m], y[m])
            table[name] = (loo_rms(X[m], y[m]), int(np.sum(b > 0)), b)
        sel = min(table, key=lambda k: (table[k][0], table[k][1]))
        outer.append(float(Xs[sel][i] @ table[sel][2] - y[i]))
        chosen.append(sel)
    return outer, chosen


def comb(pt, lo, hi, rms):
    """Half-widths of a D-propagated range and 1.96 x the relation rms, in quadrature on each side, in [600, 800]."""
    if lo >= 799.95:
        return [800.0, 800.0]
    e = 1.96 * rms
    return [round(max(600.0, pt - ((pt - lo) ** 2 + e ** 2) ** 0.5), 1),
            round(min(800.0, pt + ((hi - pt) ** 2 + e ** 2) ** 0.5), 1)]


def calibration(hf_dir, spec, P, e78rows, fit_full, meas_full):
    mpath = os.path.join(hf_dir, "model.safetensors")
    if MR.sha_file(mpath) != MR.MODEL["sha256"]:
        sys.exit("refused: model.safetensors sha256 differs from the frozen one")
    for fn, rec in MR.TOKENIZER.items():
        if fn.endswith((".json", ".txt")) and MR.sha_file(os.path.join(hf_dir, fn)) != rec["sha256"]:
            sys.exit(f"refused: {fn} sha256 differs from the frozen one")
    vocab = json.load(open(os.path.join(hf_dir, "vocab.json"), encoding="utf-8"))
    merges = [ln for ln in open(os.path.join(hf_dir, "merges.txt"), encoding="utf-8").read().split("\n")[1:] if ln]
    ids = MR.bpe_encode(MR.TEXT, vocab, merges)[:MR.T_TOKENS]
    names = ["wte.weight", "wpe.weight", "ln_f.weight", "ln_f.bias"]
    for L in range(MR.N_LAYER):
        for s in ("ln_1.weight", "ln_1.bias", "attn.c_attn.weight", "attn.c_attn.bias", "attn.c_proj.weight",
                  "attn.c_proj.bias", "ln_2.weight", "ln_2.bias", "mlp.c_fc.weight", "mlp.c_fc.bias",
                  "mlp.c_proj.weight", "mlp.c_proj.bias"):
            names.append(f"h.{L}.{s}")
    W, _ = MR.read_safetensors(mpath, names)
    keep, _ = MR.forward(W, ids)
    full = {"l0_mlp_up": (keep["l0_ln2"], W["h.0.mlp.c_fc.weight"], True),
            "l6_mlp_down": (keep["l6_gelu"], W["h.6.mlp.c_proj.weight"], True),
            "l6_attn_qk": (keep["l6_q"], keep["l6_k"].T.copy(), False)}

    def q(x, s):
        return np.clip(np.rint(x.astype(np.float64) / s), -127, 127).astype(np.int8)

    def variants(x, tok_axis):
        a = np.abs(x.astype(np.float64))
        rest = a[1:] if tok_axis == 0 else a[:, 1:]
        return {
            "per-tensor max-abs (committed)": q(x, float(a.max()) / 127.0),
            "per-tensor max-abs, token 0 left out": q(x, float(rest.max()) / 127.0),
            "per-token max-abs (vector-wise)": q(x, a.max(axis=1 - tok_axis, keepdims=True) / 127.0),
            "per-tensor 99.99th percentile clip": q(x, float(np.quantile(a, 0.9999)) / 127.0),
            "per-tensor 99.9th percentile clip": q(x, float(np.quantile(a, 0.999)) / 127.0),
        }

    out = {"note": ("int8 only: the committed window of each product, the activations re-quantised; weights stay per "
                    "output channel; for l6_attn_qk both q and k change (both are activations). D from the committed "
                    "predictor. Informational, never scored."),
           "activation_max_abs": {}, "products": {}}
    for name, (Af, Bf, b_is_weight) in full.items():
        a_abs = np.abs(Af.astype(np.float64))
        tok_max = a_abs.max(axis=1)
        out["activation_max_abs"][name] = {
            "max": round(float(tok_max.max()), 4), "token": int(np.argmax(tok_max)),
            "dim": int(np.argmax(a_abs[int(np.argmax(tok_max))])),
            "max_over_tokens_1_to_127": round(float(tok_max[1:].max()), 4),
            "p99.9": round(float(np.quantile(a_abs, 0.999)), 4)}
        w = spec["tiles"]["int8"][name]["window"]
        r0, k0, j0 = w["rows"][0], w["k"][0], w["cols"][0]
        K = MK.TYPES["int8"][3]
        Bq_w = MR.quant_per_out_channel(Bf)[0] if b_is_weight else None
        Av = variants(Af, 0)
        Bv = None if b_is_weight else variants(Bf, 1)
        res = {}
        for vn, Aq in Av.items():
            Bq = Bq_w if b_is_weight else Bv[vn]
            Aw, Bw = MR.cut(Aq, Bq, r0, k0, j0, K)
            raw = MK.encode(Aw, Bw, "int8")
            st = MK.tile_stats(raw, "int8")
            pd = MR.predict_D(P, "int8", MR.features(raw, "int8"), e78rows["int8"])
            res[vn] = {"D_w": pd["point_w"], "x_full_measured": round(pd["point_w"] / meas_full, 3),
                       "x_full_model_fit": round(pd["point_w"] / fit_full, 3),
                       "bus_bits_per_op": st["bus_bits_per_op"], "gated_lane_frac": st["gated_lane_frac"],
                       "window_A_sd_steps": round(float(np.asarray(Aw, dtype=np.float64).std()), 2),
                       "window_A_zero_byte_frac": round(float(np.mean(np.asarray(Aw) == 0)), 4),
                       "whole_A_sd_steps": round(float(Aq.astype(np.float64).std()), 2),
                       "features_outside_e78_range": pd["features_outside_e78_range"]}
            if vn.endswith("(committed)"):
                res[vn]["reproduces_committed_tile"] = (MR.sha_bytes(raw) ==
                                                        spec["tiles"]["int8"][name]["sha256"])
        out["products"][name] = res
    Ds = [v["D_w"] for p in out["products"].values() for v in p.values()]
    xs = [v["x_full_measured"] for p in out["products"].values() for v in p.values()]
    out["range"] = {"D_w": [min(Ds), max(Ds)], "x_full_measured": [min(xs), max(xs)]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf-dir", default=None)
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()

    for p, want in list(FROZEN.items()) + list(MR.FROZEN_SHA.items()):
        got = MR.sha_file(os.path.join(ROOT, p))
        if got != want:
            sys.exit(f"refused: {p} sha256 {got} is not the committed {want}")
    PR = json.load(open(os.path.join(ROOT, PRED)))
    spec = json.load(open(os.path.join(ROOT, SPEC)))
    E78 = json.load(open(os.path.join(ROOT, MR.E78J)))

    # the predictor again, checked against the frozen one
    P, rows = MR.fit_predictor(E78, ROOT)
    for t in MR.TYPES:
        fz = PR["predictor"]["per_type"][t]
        if (P[t]["selected"], P[t]["beta"], P[t]["rms_loo_w"]) != (fz["selected"], fz["beta"], fz["rms_loo_w"]):
            sys.exit(f"refused: the predictor for {t} does not reproduce the frozen one")

    # 1. nested LOO
    nested = {}
    for t in MR.TYPES:
        outer, chosen = nested_loo(rows[t])
        n, p = len(outer), P[t]["terms_nonzero"]
        rms = float(np.sqrt(np.mean(np.square(outer))))
        tq = MR.T975[n - p - 1]
        cand = PR["predictor"]["per_type"][t]["candidates"]
        order = sorted(cand, key=lambda k: (cand[k]["rms_loo_w"], cand[k]["terms_nonzero"]))
        nested[t] = {
            "n_kinds": n, "selected": P[t]["selected"], "terms_nonzero": p, "t975": tq,
            "loo_rms_w_frozen": P[t]["rms_loo_w"], "pi95_halfwidth_w_frozen": P[t]["pi95_halfwidth_w"],
            "nested_loo_rms_w": round(rms, 4), "nested_pi95_halfwidth_w": round(tq * rms, 4),
            "widening": round(rms / P[t]["rms_loo_w"], 3),
            "nested_max_abs_w": round(float(np.max(np.abs(outer))), 4),
            "chosen_per_fold": {k: chosen.count(k) for k in sorted(set(chosen), key=lambda k: -chosen.count(k))},
            "nested_residual_w": {rows[t][i]["kind"]: round(outer[i], 3) for i in range(n)},
            "candidates_by_loo": [[k, cand[k]["rms_loo_w"]] for k in order],
            "runner_up": order[1],
        }

    # relation, scale, conversion: exactly as make_real.py
    sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "kspeed", "e83"))
    import predict_e83 as P83  # noqa: E402
    E83 = json.load(open(os.path.join(ROOT, MR.E83P)))
    F64 = json.load(open(os.path.join(ROOT, MR.E64F)))
    Q = json.load(open(os.path.join(ROOT, MR.Q130C)))["predictions"]
    rel = P83.Rel({int(k): v for k, v in F64["fit"]["B"].items()})
    Wb, sb = E83["relation"]["burst"]["W_star_w"], E83["relation"]["burst"]["sigma_w"]
    Ws, ss = E83["relation"]["sustained"]["W_star_w"], E83["relation"]["sustained"]["sigma_w"]
    c0 = {t: Q[f"{t}/zeros"]["c_w_a2_600mhz"] for t in MR.TYPES}
    scale82 = json.load(open(os.path.join(ROOT, MR.E82S)))["cross_card"]["primary"]["x3"]["per_type_median"]

    def clk(t, D):
        c = c0[t] + D / P83.XFER
        return rel.f(c, Wb, sb)[0], rel.f(c, Ws, ss)[0]

    ref_fit, ref_meas, terms = {}, {}, {}
    for t in MR.TYPES:
        pts = {e["kind"]: e for e in PR["predictor"]["per_type"][t]["e78_points"]}
        ref_fit[t], ref_meas[t] = pts[REF[t]]["fit_w"], pts[REF[t]]["D_w"]
        fz = PR["predictor"]["per_type"][t]
        terms[t] = {}
        for kind in (REF[t], "randn_sorted" if t != "int8" else "sorted"):
            r = next(r for r in rows[t] if r["kind"] == kind)
            terms[t][kind] = {"measured_w": round(r["D"], 3),
                              "fit_w": round(float(sum(b * r["f"][c] for c, b in zip(fz["cols"], fz["beta"]))), 3),
                              "terms_w": {c: round(b * r["f"][c], 3) for c, b in zip(fz["cols"], fz["beta"])}}

    tiles = {}
    for t in MR.TYPES:
        fz = PR["predictor"]["per_type"][t]
        cols, beta = fz["cols"], fz["beta"]
        used = [c for c, b in zip(cols, beta) if b > 0]
        X = np.array([[r["f"][c] for c in cols] for r in rows[t]])
        mu, sd = X.mean(axis=0), X.std(axis=0)
        sd = np.where(sd > 0, sd, 1.0)
        ru = nested[t]["runner_up"]
        for name in NAMES:
            key = f"{t}/{name}"
            fp = PR["tiles"][key]
            f = spec["tiles"][t][name]["features"]
            A_ = fp["a_aifoundry3_600mhz"]
            D, hw = A_["D_w"], nested[t]["nested_pi95_halfwidth_w"]
            lo, hi = round(max(D - hw, 0.0), 3), round(D + hw, 3)
            b_pt, s_pt = clk(t, D)
            b_lo, s_lo = clk(t, hi)
            b_hi, s_hi = clk(t, lo)
            B_ = fp["b_aifoundry2_governor"]
            band = A_["D_band_over_20_windows_w"]
            # every column of the model, B included (the check of the first run with real tiles)
            outside = {}
            for c in cols:
                rlo, rhi = fz["feature_range_e78"][c]
                if not (rlo - 1e-9 <= f[c] <= rhi + 1e-9):
                    outside[c] = {"tile": f[c], "e78_range": [rlo, rhi],
                                  "beyond_pct": round(100.0 * (f[c] - rhi) / rhi, 2) if f[c] > rhi else None,
                                  "beta": beta[cols.index(c)]}

            def nearest(cs):
                idx = [cols.index(c) for c in cs]
                z = np.array([(f[c] - mu[j]) / sd[j] for c, j in zip(cs, idx)])
                d = [float(np.sum(((X[i, idx] - mu[idx]) / sd[idx] - z) ** 2)) for i in range(len(rows[t]))]
                return rows[t][int(np.argmin(d))]["kind"]

            rb = PR["predictor"]["per_type"][t]["candidates"][ru]
            tiles[key] = {
                "a_aifoundry3_600mhz": {
                    "D_w": D, "frozen_pi95_w": A_["D_pi95_w"], "scoring_interval_w": [lo, hi],
                    "scoring_halfwidth_w": hw,
                    "D_band_over_20_windows_w": [band["min"], band["max"]],
                    "band_share_of_width": {"frozen": round((band["max"] - band["min"]) /
                                                            (A_["D_pi95_w"][1] - A_["D_pi95_w"][0]), 3),
                                            "amended": round((band["max"] - band["min"]) / (hi - lo), 3)}},
                "e91_aifoundry1_card1_600mhz": {
                    "D_w": fp["e91_aifoundry1_card1_600mhz"]["D_w"],
                    "frozen_pi95_w": fp["e91_aifoundry1_card1_600mhz"]["D_pi95_w"],
                    "scoring_interval_w": [round(lo / scale82[t], 3), round(hi / scale82[t], 3)],
                    "card_scale_e82": round(scale82[t], 4),
                    "excludes": "the card-scale spread (E82's per-kind ratios: IQR 1.025-1.034 over 32 kinds; X3 FAIL)"},
                "b_aifoundry2_governor": {
                    "burst_mhz": B_["burst_mhz"], "burst_limit": B_["burst_limit"],
                    "burst_D_propagated_range_frozen_mhz": B_["burst_mhz_pi95"],
                    "burst_D_propagated_range_amended_mhz": [round(b_lo, 1), round(b_hi, 1)],
                    "burst_scoring_interval_mhz": comb(b_pt, b_lo, b_hi, REL_RMS_MHZ["burst"]),
                    "sus_mhz": B_["sus_mhz"], "sus_limit": B_["sus_limit"],
                    "sus_D_propagated_range_frozen_mhz": B_["sus_mhz_pi95"],
                    "sus_D_propagated_range_amended_mhz": [round(s_lo, 1), round(s_hi, 1)],
                    "sus_scoring_interval_mhz": comb(s_pt, s_lo, s_hi, REL_RMS_MHZ["sustained"]),
                    "check_point_reproduces_frozen": [round(b_pt, 1), round(s_pt, 1)] == [B_["burst_mhz"],
                                                                                          B_["sus_mhz"]]},
                "like_with_like": {
                    "ref_kind": REF[t], "ref_model_fit_w": ref_fit[t], "ref_measured_w": ref_meas[t],
                    "ratio_to_ref_model_fit": round(D / ref_fit[t], 4),
                    "ratio_to_ref_measured": round(D / ref_meas[t], 4),
                    "anchored_on_measured_ref_w": round(ref_meas[t] * D / ref_fit[t], 3)},
                "runner_up_informational": {
                    "model": ru, "loo_rms_w": rb["rms_loo_w"],
                    "D_w": round(float(sum(b * f[c] for c, b in zip(rb["cols"], rb["beta"]))), 3)},
                "model_columns_outside_e78_range": outside,
                "nearest_e78_kind": {"used_terms_z (committed metric)": nearest(used),
                                     "all_model_columns_z": nearest(cols)},
            }

    out = {
        "experiment": "Q130(n)", "amendment": 1,
        "written": "Sat 31 Oct 2026, after verification and before any card ran a real tile",
        "amends": {"file": PRED, "sha256": FROZEN[PRED],
                   "unchanged": "its points, its frozen intervals and its bytes stay as committed in 7d5b99af"},
        "real_json_sha256": FROZEN[SPEC],
        "generator": "tools/claims-v3/kinds/real/amend_real.py",
        "build": {"python": platform.python_version(), "numpy": np.__version__},
        "D_scope": ("D is board power (the board meter, as E78 measured it; rail D is 0.80-0.87 of it) over the "
                    "type's own zeros, at E78's primary leakage slope (auto, 0.1994 W/C). E78's registered leakage "
                    "arms move random data's D by about +-0.6 W. E86 computes D the same way."),
        "scoring": ("E86 scores (a) against tiles.<key>.a_aifoundry3_600mhz.scoring_interval_w; E91 against "
                    "tiles.<key>.e91_aifoundry1_card1_600mhz.scoring_interval_w; E87 against "
                    "tiles.<key>.b_aifoundry2_governor.{burst,sus}_scoring_interval_mhz. Each also reports how its "
                    "data falls against the frozen intervals in predictions-real.json."),
        "why": {
            "a": ("the feature set was the lowest-LOO of 11 candidates (after 5 OLS models tried on E78 in the "
                  "lane's scratch), so its own LOO rms is biased low; the nested LOO redoes the choice in each fold"),
            "b": ("burst_mhz_pi95 and sus_mhz_pi95 in predictions-real.json are D-propagated ranges (the clock at "
                  "the two ends of (a)'s frozen interval), not 95% prediction intervals: they leave out the "
                  "relation's own error, which E83 measured"),
            "e91": "E82's single per-type scale is approximate (X3 FAIL); its spread is not in the interval",
        },
        "relation_error_mhz": {"burst": REL_RMS_MHZ["burst"], "sustained": REL_RMS_MHZ["sustained"],
                               "what": ("E83's relation rms on each kind's measured power, over the kinds it puts "
                                        "below 800 MHz (9 bursts, 18 sustained cells), post hoc; over all 33 kinds "
                                        "7.9 / 7.5 MHz"),
                               "source": "docs/reports/data/2026-10-31-e83-kinds-speed-rest/README.md, Results 1 "
                                         "and rule E83-S1"},
        "nested_loo": nested,
        "model_terms_on_reference_kinds": {
            "what": ("beta x feature for each term of the selected model, on E78's random reference kind and its "
                     "sorted twin. A post-hoc fit's split, not a mechanism: beta_B = 0 in all three types, while E65 "
                     "measured flipped B bits on silicon at 83-1,008 fJ each (docs/findings/05-claims.md, E65)"),
            "per_type": terms},
        "tiles": tiles,
    }
    if a.hf_dir:
        out["calibration_sensitivity"] = calibration(a.hf_dir, spec, P, rows, ref_fit["int8"], ref_meas["int8"])
    path = os.path.join(a.out, "amendment-1.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")

    for t, v in nested.items():
        print(f"{t}: LOO {v['loo_rms_w_frozen']} -> nested {v['nested_loo_rms_w']} (x{v['widening']}); "
              f"+-{v['pi95_halfwidth_w_frozen']} -> +-{v['nested_pi95_halfwidth_w']} W; folds {v['chosen_per_fold']}")
    for k, v in tiles.items():
        A_, B_, L_ = v["a_aifoundry3_600mhz"], v["b_aifoundry2_governor"], v["like_with_like"]
        print(f"{k:18s} D {A_['D_w']:6.3f} {A_['scoring_interval_w']} E91 {v['e91_aifoundry1_card1_600mhz']['scoring_interval_w']} "
              f"burst {B_['burst_mhz']} {B_['burst_scoring_interval_mhz']} sus {B_['sus_mhz']} {B_['sus_scoring_interval_mhz']} "
              f"ratio {L_['ratio_to_ref_model_fit']} anchored {L_['anchored_on_measured_ref_w']} "
              f"runner-up {v['runner_up_informational']['D_w']} out {list(v['model_columns_outside_e78_range'])} "
              f"near {v['nearest_e78_kind']}")
    if a.hf_dir:
        cs = out["calibration_sensitivity"]
        print("calibration range", cs["range"], json.dumps(cs["activation_max_abs"]))
        for n_, p_ in cs["products"].items():
            print(" ", n_, {k: (v["D_w"], v["x_full_measured"]) for k, v in p_.items()})
    print(f"amendment-1.json sha256 {MR.sha_file(path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
