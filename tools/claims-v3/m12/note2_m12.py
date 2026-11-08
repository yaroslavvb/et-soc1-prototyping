#!/usr/bin/env python3
"""M12 (Q158a, fix-m12): the re-runs behind REFIT.md.dated-note-2.md, POST HOC, from committed files only. Nothing of M12 is refitted
or changed: with M12's own functions (m12_common.py) and its committed outputs (m12.json, heldout-m12.json, candidates-m12.json), it
re-derives each figure the dated note quotes for the verifier's faults of Sun 8 Nov 2026 (verify-m12), section by section:

  f1  his pair is E182's T1: the same kinds and words, T1's leverage in the int8 fit, k_walk from T1 alone, M12's pair against T1
  f2  E178's 40 held-out kinds split into the 32 new to E182 and the 8 E182 also fitted, by word, with heldout_m12.py's own bootstrap
  f3  each candidate train's power and separation at E182's registered train noise and at its measured train noise
  f4  fp16's held-bit level on E178's fp16 kinds as a fraction of fp32's (a regression through 0), and H16 at that fraction
  f5  the int8 session level: E178's D minus E182's D on the six int8 kinds both sessions ran
  f7  the code nits: the flip model on all 24 of E182's kinds, the reference tile's bench row, M10's int8 rate, the two power forms,
      sigma_K's denominator, the one-base-word scope of pool 8's class S tiles
  f8  the records nits that a number can settle: the build record's hashes, the placement term on E178's fp32 kinds

    /usr/bin/python3 -B tools/claims-v3/m12/note2_m12.py --root .           # writes note2-m12.json and logs/note2-m12.txt beside it
    /usr/bin/python3 -B tools/claims-v3/m12/note2_m12.py --root . --check   # recomputes in memory, compares both files byte for byte

Needs a C compiler (E178's flip model, compiled unchanged) and numpy (M10's feature chain, unchanged), as candidates_m12.py does.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m12_common as C  # noqa: E402

HW_TRAIN = 0.0051            # candidates_m12.py's HW_TRAIN: E182's registered train half-width at 32 units
BUILD_RECORD = "docs/reports/data/2026-11-04-q141t-s7-recount/step243/build-record-mini.json"
E182_COUNTS = "tools/claims-v3/e182/bench/counts-e182.json"
E178_COUNTS = "tools/claims-v3/e178/bench/counts-e178.json"


def ncdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def power(d, hw, sig):
    """candidates_m12.py's form: the chance a train's 95% interval (half-width hw) excludes 0 if the true difference is d"""
    return ncdf((d - hw) / sig) + ncdf((-d - hw) / sig)


def through0(x, e):
    """least squares of e on x through 0: slope, its se (residual variance on n - 1)"""
    sxx = sum(a * a for a in x)
    f = sum(a * b for a, b in zip(x, e)) / sxx
    s2 = sum((b - f * a) ** 2 for a, b in zip(x, e)) / (len(x) - 1)
    return f, math.sqrt(s2 / sxx)


def joint_fit_denom(kind_rows, kind_y, train_rows, train_y, train_se, denom, tol=1e-12, it_max=200):
    """m12_common.joint_fit with sigma_K^2's denominator fixed (denom), in place of n_K minus the kinds rows' leverages"""
    nk = len(kind_rows)
    b0, _ = C.wls(kind_rows, kind_y, [1.0] * nk)
    s2 = sum((yy - C.dot(r, b0)) ** 2 for yy, r in zip(kind_y, kind_rows)) / denom
    for _ in range(it_max):
        var = [s2] * nk + [s * s for s in train_se]
        b, cov = C.wls(kind_rows + train_rows, kind_y + train_y, var)
        new = sum((yy - C.dot(r, b)) ** 2 for yy, r in zip(kind_y, kind_rows)) / denom
        if abs(new - s2) <= tol * max(s2, 1e-30):
            s2 = new
            break
        s2 = new
    var = [s2] * nk + [s * s for s in train_se]
    b, cov = C.wls(kind_rows + train_rows, kind_y + train_y, var)
    return b, cov, math.sqrt(s2)


def build(root):
    m = json.load(open(os.path.join(HERE, "m12.json")))
    ho = json.load(open(os.path.join(HERE, "heldout-m12.json")))
    cj = json.load(open(os.path.join(HERE, "candidates-m12.json")))
    sc = C.load(root, f"{C.E182D}/scored.json")
    tr = C.load(root, f"{C.E182D}/trains-e182.json")["trains"]
    f182 = C.load(root, C.E182F)
    fc = f182["kinds"]
    f8 = C.load(root, C.E178F)["kinds"]
    s8 = C.load(root, f"{C.E178D}/scored.json")
    K, K8 = sc["reported"]["kinds"], s8["primary"]["reported"]["kinds"]
    inputs = ["tools/claims-v3/m12/m12.json", "tools/claims-v3/m12/heldout-m12.json", "tools/claims-v3/m12/candidates-m12.json",
              "tools/claims-v3/m12/kinds-m12.json", "tools/claims-v3/m12/bench/counts-m12.json", "tools/claims-v3/m12/m12_common.py",
              f"{C.E182D}/scored.json", f"{C.E182D}/trains-e182.json", C.E182F, f"{C.E178D}/scored.json", C.E178F, E182_COUNTS,
              E178_COUNTS, BUILD_RECORD, f"{C.E171D}/scored.json", f"{C.B8}/MANIFEST", f"{C.M10D}/m10.json",
              "tools/claims-v3/e178/flipmodel_e178.c", "rtl-sim/fma_toggle_v2/accum.c"]
    out = {"_what": "M12's dated note 2 re-runs (note2_m12.py): figures for the verifier's faults, re-derived from committed files; "
                    "nothing of M12 is refitted or changed", "label": "post hoc throughout (M12 is post hoc); each figure's label is in "
                    "REFIT.md.dated-note-2.md", "inputs_sha256": {p: C.sha(os.path.join(root, p)) for p in inputs}}
    b8, cov8 = m["int8"]["b"], m["int8"]["cov"]
    bf = m["float"]["b"]
    rows = ho["rows"]

    # ---------------------------------------------------------------- f1: his pair is E182's T1
    i8 = sorted(k for k in K if k.startswith("int8."))
    Rm = m["int8"]["mean_rate_per_s"]
    lm = {k: fc[k]["flips_i"]["launch_mean"] for k in i8}
    pa = {k: fc[k]["popcount_a_word"] for k in i8}
    pb = {k: fc[k]["popcount_b_word"] for k in i8}
    krow = [C.int8_row(K[k]["rate_per_s"], lm[k], pa[k], pb[k]) for k in i8]
    ky = [K[k]["D_w"] for k in i8]
    trow, ty, tse = [], [], []
    for t, (a, b) in C.TRAINS8.items():
        ra, rb = C.int8_row(Rm, lm[a], pa[a], pb[a]), C.int8_row(Rm, lm[b], pa[b], pb[b])
        trow.append([x - y for x, y in zip(ra, rb)])
        ty.append(tr[t]["estimate"]["mean"])
        tse.append(tr[t]["estimate"]["se"])
    sK = m["int8"]["sigma_K_w"]
    var = [sK * sK] * len(krow) + [s * s for s in tse]
    b_re, cov_re = C.wls(krow + trow, ky + ty, var)
    assert max(abs(x - y) for x, y in zip(b_re, b8)) < 1e-9, (b_re, b8)
    lev = C.hat_diag(krow + trow, var, cov_re)
    t1a, t1b = C.TRAINS8["T1"]
    hp = ho["his_pair_E178"]
    h178 = s8["primary"]["rules"]["E178-H-int8"]
    T1 = tr["T1"]["estimate"]
    d1 = trow[0]
    rest = sum(b8[i] * d1[i] for i in (0, 2, 3, 4))
    out["f1_his_pair"] = {
        "T1_kinds": [t1a, t1b], "T1_words": {k: [fc[k]["a_word"], fc[k]["b_word"]] for k in (t1a, t1b)},
        "E178_H_int8_kinds": [h178["a"], h178["b"]], "E178_H_int8_words": {k: [f8[k]["a_word"], f8[k]["b_word"]] for k in (h178["a"], h178["b"])},
        "same_kinds_and_words": [t1a, t1b] == [h178["a"], h178["b"]] and all(
            [fc[k]["a_word"], fc[k]["b_word"]] == [f8[k]["a_word"], f8[k]["b_word"]] for k in (t1a, t1b)),
        "E182_T1_w": {"mean": T1["mean"], "lo95": T1["lo"], "hi95": T1["hi"], "se": T1["se"], "n": T1["n"]},
        "E182_HT_committed": {k: sc["rules"]["E182-HT"][k] for k in ("verdict", "sign", "repeat", "size_P", "size_E", "size_PACC")},
        "E178_H_int8_w": {"mean": h178["mean_w"], "lo95": h178["lo95_w"], "hi95": h178["hi95_w"], "M10_dP": h178["dP_w"]},
        "M12_pair_on_E178_w": hp["M12_w"], "M12_pair_se_w": hp["M12_se_w"], "M12_pair_minus_T1_w": hp["M12_w"] - T1["mean"],
        "M12_T1_fit_w": m["int8"]["in_sample"]["trains"]["T1"]["fit_w"], "M12_T1_z": m["int8"]["in_sample"]["trains"]["T1"]["z"],
        "trains_leverage": {t: lev[len(krow) + i] for i, t in enumerate(C.TRAINS8)},
        "k_walk_fitted_fJ": b8[1], "k_walk_se_fJ": math.sqrt(cov8[1][1]),
        "k_walk_from_T1_alone_fJ": (T1["mean"] - rest) / d1[1],
        "k_walk_from_T1_alone_at_E182_betas_fJ": (T1["mean"] - sc["rules"]["E182-A"]["beta_A"]["mean"] * d1[3]
                                                  - sc["rules"]["E182-B"]["beta_B"]["mean"] * d1[4] - b8[2] * d1[2]) / d1[1],
        "T1_design_row": d1}

    # ---------------------------------------------------------------- f2: E178's 40 kinds, new to E182 or fitted by E182 (by word)
    e182w = {(k.split(".")[0], fc[k]["a_word"], fc[k]["b_word"]) for k in fc}
    e178 = sorted(r for r in rows if r.startswith("E178:"))
    shared = [r for r in e178 if (rows[r]["type"], rows[r]["a_word"], rows[r]["b_word"]) in e182w]
    grp = {
        "E178 all (40)": e178,
        "E178 new to E182 (32)": [r for r in e178 if r not in shared],
        "E178 E182 also fitted (8)": shared,
        "E178 int8 new to E182": [r for r in e178 if r not in shared and rows[r]["type"] == "int8"],
        "E178 int8 E182 also fitted": [r for r in shared if rows[r]["type"] == "int8"],
        "E178 fp32 new to E182": [r for r in e178 if r not in shared and rows[r]["type"] == "fp32"],
        "E178 fp32 E182 also fitted": [r for r in shared if rows[r]["type"] == "fp32"],
        "E178 fp16 (all new to E182)": [r for r in e178 if rows[r]["type"] == "fp16"]}
    f2 = {}
    for g, ks in grp.items():
        e12 = [rows[k]["models"]["M12"]["e_w"] for k in ks]
        e10 = [rows[k]["models"]["M10"]["e_w"] for k in ks]
        f2[g] = {"rows": [k.split(":", 1)[1] for k in ks], "n": len(ks), "M10": C.group_stats(e10), "M12": C.group_stats(e12),
                 "zero_inside_M10": sum(1 for k in ks if rows[k]["models"]["M10"]["zero_inside"]),
                 "zero_inside_M12": sum(1 for k in ks if rows[k]["models"]["M12"]["zero_inside"]),
                 "M12_vs_M10": C.boot_rms_diff(e12, e10)}
    ref = ho["groups"]["E178 all (40)"]["models"]["M12"]["vs_M10"]
    assert all(abs(f2["E178 all (40)"]["M12_vs_M10"][k] - ref[k]) < 1e-15 for k in ("diff", "lo95", "hi95")), "bootstrap differs"
    out["f2_shared_kinds"] = {"groups": f2, "bootstrap_reproduces_heldout_all40": True}

    # ---------------------------------------------------------------- f3 (and f7d): power and separation at both train noises
    se_reg = HW_TRAIN / C.t975(31)
    assert abs(se_reg - cj["train_noise"]["se_w"]) < 1e-15
    se_m = {"int8": statistics.median(tr[t]["estimate"]["se"] for t in C.TRAINS8),
            "fp32": statistics.mean(tr[t]["estimate"]["se"] for t in C.TRAINS32)}
    df_m = {"int8": 31, "fp32": 37}
    f3 = {"se_registered_w": se_reg, "halfwidth_registered_w": HW_TRAIN,
          "se_measured_w": {"int8 (median of T1-T4)": se_m["int8"], "fp32 (mean of T5, T6)": se_m["fp32"],
                            "fp16": "none measured (E182 ran no fp16 train): fp32's measured se and df 37 stand in"},
          "se_measured_each_w": {t: tr[t]["estimate"]["se"] for t in list(C.TRAINS8) + list(C.TRAINS32)}, "trains": {}}
    for tid, v in cj["trains"].items():
        t = v["first"].split(".")[0]
        fam = "int8" if t == "int8" else "fp32"
        d12, s12, d10 = v["M12_w"], v["M12_se_w"], v["M10_w"]
        sig_r = math.sqrt(se_reg ** 2 + s12 ** 2)
        p_r, sep_r = power(d12, HW_TRAIN, sig_r), abs(d12 - d10) / sig_r
        assert abs(p_r - v["power_excludes_0_if_M12"]) < 1e-12 and abs(sep_r - v["separation_M12_M10_in_se"]) < 1e-9, tid
        sm = se_m[fam]
        hw_m = sm * C.t975(df_m[fam])
        sig_m = math.sqrt(sm ** 2 + s12 ** 2)
        f3["trains"][tid] = {
            "format": t, "M12_w": d12, "M12_se_w": s12, "M10_w": d10,
            "registered": {"power_if_M12": p_r, "separation": sep_r, "power_if_M10": power(d10, HW_TRAIN, se_reg)},
            "measured": {"se_w": sm, "halfwidth_w": hw_m, "power_if_M12": power(d12, hw_m, sig_m), "separation": abs(d12 - d10) / sig_m,
                         "power_if_M10": power(d10, hw_m, sm)},
            "REFIT_letter_train_se_alone": {"registered": {"power_if_M12": power(d12, HW_TRAIN, se_reg), "separation": abs(d12 - d10) / se_reg},
                                            "measured": {"power_if_M12": power(d12, hw_m, sm), "separation": abs(d12 - d10) / sm}}}
    out["f3_train_noise"] = f3

    # ---------------------------------------------------------------- f4: fp16's held-bit level, and H16 at that fraction
    cf = bf[0]
    r16 = [r for r in e178 if rows[r]["type"] == "fp16"]
    x16 = [rows[r]["models"]["M12"]["pred_w"] - rows[r]["models"]["F16-NOHB"]["pred_w"] for r in r16]
    e16 = [rows[r]["D_w"] - rows[r]["models"]["F16-NOHB"]["pred_w"] for r in r16]
    r32 = [r for r in e178 if rows[r]["type"] == "fp32"]
    x32 = [rows[r]["models"]["M12"]["pred_w"] - rows[r]["P10_w"] - cf for r in r32]
    e32 = [rows[r]["D_w"] - rows[r]["P10_w"] - cf for r in r32]
    fr16, se16 = through0(x16, e16)
    fr32, se32 = through0(x32, e32)
    H = cj["trains"]["H16"]
    h_at = fr16 * H["M12_w"]
    s_at = se16 * H["M12_w"]
    sm = se_m["fp32"]
    hw_m16 = sm * C.t975(37)
    out["f4_fp16"] = {
        "rule": "e = D - (P10 + c_f) regressed through 0 on M12's held-bit increment x = gamma_A pc_A + gamma_B pc_B, E178's rows; "
                "slope 1 = F16-SAME's level per bit, 0 = no held-bit term",
        "fp16_13_kinds": {"slope": fr16, "se": se16, "n": len(r16)}, "fp32_14_kinds": {"slope": fr32, "se": se32, "n": len(r32)},
        "H16_M12_F16_SAME_w": H["M12_w"], "H16_M12_se_w": H["M12_se_w"], "H16_M10_w": H["M10_w"],
        "H16_at_fp16_slope_w": h_at, "H16_at_fp16_slope_se_w": s_at,
        "H16_at_fp16_slope_95_w": [(fr16 - 1.96 * se16) * H["M12_w"], (fr16 + 1.96 * se16) * H["M12_w"]],
        "assumes": "the placement (gamma_B - gamma_A) scales with fp16's level per bit; E178's fp16 rows measure mostly the level "
                   "(gamma_A + gamma_B), since 11 of 13 hold equal A and B words",
        "at_measured_fp32_noise": {
            "separation_scaled_vs_M10": abs(h_at - H["M10_w"]) / math.sqrt(sm ** 2 + s_at ** 2),
            "separation_scaled_vs_F16_SAME": abs(H["M12_w"] - h_at) / math.sqrt(sm ** 2 + s_at ** 2 + H["M12_se_w"] ** 2),
            "power_if_scaled": power(h_at, hw_m16, math.sqrt(sm ** 2 + s_at ** 2))},
        "fp16_rows_equal_words": sum(1 for r in r16 if rows[r]["a_word"] == rows[r]["b_word"])}

    # ---------------------------------------------------------------- f5: the int8 session level, E178 against E182
    both = sorted(k for k in K8 if k.startswith("int8.") and k in fc and [f8[k]["a_word"], f8[k]["b_word"]] == [fc[k]["a_word"], fc[k]["b_word"]])
    dd = {k: K8[k]["D_w"] - K[k]["D_w"] for k in both}
    out["f5_int8_session"] = {
        "kinds_both_sessions": both, "E178_minus_E182_D_w": dd, "min_w": min(dd.values()), "max_w": max(dd.values()),
        "mean_w": statistics.mean(dd.values()),
        "M12_bias_E178_int8_w": ho["groups"]["E178 int8 (13)"]["models"]["M12"]["bias"],
        "M12_S1_shift_w": ho["arm_S1_shift_w"], "c8_w": b8[0], "c8_se_w": math.sqrt(cov8[0][0])}

    # ---------------------------------------------------------------- f7: the code nits
    f7 = {}
    N = f182["N_launch"]
    sys.path.insert(0, os.path.join(root, "tools/claims-v3/e182"))
    sys.path.insert(0, os.path.join(root, C.M10D))
    import forecast_e182 as FE  # noqa: E402  (run_flips only)
    import fit_m10 as FM        # noqa: E402  (the feature chain only)
    import predict_m10 as PM    # noqa: E402
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "flipmodel_e178")
        subprocess.run(["cc", "-O2", "-std=gnu11", f'-DACCUM_C="{os.path.join(root, "rtl-sim/fma_toggle_v2/accum.c")}"', "-o", exe,
                        os.path.join(root, "tools/claims-v3/e178/flipmodel_e178.c"), "-lm"], check=True)
        fl = {}
        for key in sorted(fc):
            t = key.split(".")[0]
            got = FE.run_flips(exe, t, fc[key]["a_word"], fc[key]["b_word"], N[t])["launch_mean"]
            fl[key] = got == fc[key]["flips_i"]["launch_mean"]
    f7["a_flip_model_all_E182_kinds"] = {"kinds": len(fl), "equal": sum(fl.values()), "unequal": sorted(k for k, v in fl.items() if not v)}
    cm = json.load(open(os.path.join(HERE, "bench", "counts-m12.json")))["rows"]
    c182 = C.load(root, E182_COUNTS)["rows"]
    c178 = C.load(root, E178_COUNTS)["rows"]
    ref_rows = {}
    for key, src, name in (("fp32.e182_a1_b3fffffff", c182, "E182"), ("fp32.ones", c178, "E178"), ("int8.zeros", c178, "E178"),
                           ("fp32.zeros", c178, "E178"), ("fp16.zeros", c178, "E178")):
        ref_rows[key] = {"against": name, "mean_equal": cm[key]["mean"] == src[key]["mean"], "points_equal": cm[key]["points"] == src[key]["points"],
                         "n_points": len(cm[key]["points"])}
    f7["b_reference_rows"] = ref_rows
    # M10's int8 column at E182's median int8 rate, against the mean the code used
    rmed = statistics.median(K[k]["rate_per_s"] for k in i8)
    m10 = PM.load_m10()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    kj = json.load(open(os.path.join(HERE, "kinds-m12.json")))["kinds"]
    p_mean, p_med = {}, {}
    for k in kj:
        if k["type"] != "int8":
            continue
        f = FM.chain_feats(cm[k["key"]], os.path.join(root, k["tile"]), "int8", zeros, zr)
        p_mean[k["key"]] = PM.d600(f, "int8", Rm, "a3", m10, 1.0)
        p_med[k["key"]] = PM.d600(f, "int8", rmed, "a3", m10, 1.0)
        assert abs(p_mean[k["key"]] - cj["kinds"][k["key"]]["P10_w"]) < 1e-12, k["key"]
    dtr = {tid: (p_med[v["first"]] - p_med[v["second"]]) - (p_mean[v["first"]] - p_mean[v["second"]])
           for tid, v in cj["trains"].items() if v["first"].startswith("int8.")}
    f7["c_M10_int8_rate"] = {"mean_rate_used": Rm, "median_rate": rmed, "registered_rates": f182["rate"],
                             "median_over_mean_minus_1": rmed / Rm - 1.0,
                             "max_abs_kind_change_w": max(abs(p_med[k] - p_mean[k]) for k in p_mean),
                             "max_abs_train_change_w": max(abs(x) for x in dtr.values()),
                             "rates_used_vs_registered": {t: cj["rates_per_s"][t] / f182["rate"][t] - 1.0 for t in cj["rates_per_s"]}}
    # sigma_K's denominator: the code's effective dof, against n - p and n - 1
    nk, p = len(krow), len(krow[0])
    den = {}
    for lab, dnm in (("n_K - p", nk - p), ("n_K - 1", nk - 1), ("n_K", nk)):
        bb, cc, ss = joint_fit_denom(krow, ky, trow, ty, tse, dnm)
        den[lab] = {"denominator": dnm, "sigma_K_w": ss, "k_walk_fJ": bb[1], "k_scp_fJ": bb[2], "beta_A_w": bb[3], "beta_B_w": bb[4],
                    "c8_w": bb[0], "d_k_walk_fJ": bb[1] - b8[1], "d_k_scp_fJ": bb[2] - b8[2], "d_beta_A_w": bb[3] - b8[3],
                    "d_beta_B_w": bb[4] - b8[4], "d_c8_w": bb[0] - b8[0]}
    f7["e_sigma_K_denominator"] = {"code": {"rule": "n_K minus the kinds rows' leverages (m12_common.joint_fit), iterated",
                                            "dof_K": m["int8"]["dof_K"], "sigma_K_w": sK}, "alternatives": den}
    # the one-base-word scope of pool 8's class S tiles (E171's rows)
    man = {}
    for ln in open(os.path.join(root, C.B8, "MANIFEST")):
        fs = ln.split()
        if len(fs) >= 3:
            man[fs[2]] = fs[1]
    s171 = C.load(root, f"{C.E171D}/scored.json")["primary"]["rows"]
    scope = {}
    for k, v in sorted(s171.items()):
        if v.get("case") != "S":
            continue
        raw = open(os.path.join(root, C.B8, man[k]), "rb").read()
        aw = sorted(set(struct.unpack("<256I", raw[:1024])))
        bw = sorted(set(struct.unpack("<256I", raw[1024:])))
        one, two = (aw, bw) if len(aw) == 1 else (bw, aw)
        row = {"type": v["type"], "distinct_a": len(aw), "distinct_b": len(bw)}
        if len(one) == 1 and len(two) == 2:
            x = two[0] ^ two[1]
            row["xor_popcount"] = C.popcount(x)
            row["xor_popcount_halves"] = [C.popcount(x & 0xFFFF), C.popcount(x >> 16)]
            row["one_base_word"] = (C.popcount(x) == 1) if v["type"] == "fp32" else (row["xor_popcount_halves"] in ([1, 1], [1, 0], [0, 1]))
        else:
            row["one_base_word"] = False
        scope[k] = row
    f7["f_one_base_word_scope"] = {"tiles": len(scope), "in_scope": sum(1 for r in scope.values() if r["one_base_word"]), "rows": scope}
    out["f7_code_nits"] = f7

    # ---------------------------------------------------------------- f8: the records nits a number settles
    br = C.load(root, BUILD_RECORD)
    out["f8_records"] = {
        "build_record": {"path": BUILD_RECORD, "binaries_sha256": br["binaries"], "run_kinds.py": br["inputs"]["run_kinds.py"]},
        "placement_on_E178_fp32": {}}
    gA, gB = bf[1], bf[2]
    pl = {}
    for r in r32:
        a_, b_ = rows[r]["pc_a"], rows[r]["pc_b"]
        pl[r.split(":", 1)[1]] = {"pc_a": a_, "pc_b": b_, "placement_part_w": (gB - gA) * (b_ - a_) / 2.0,
                                  "level_part_w": (gA + gB) * (a_ + b_) / 2.0}
    out["f8_records"]["placement_on_E178_fp32"] = {
        "split": "gamma_A pc_A + gamma_B pc_B = (gamma_A + gamma_B)(pc_A + pc_B)/2 + (gamma_B - gamma_A)(pc_B - pc_A)/2",
        "rows": pl, "rows_with_equal_popcounts": sum(1 for v in pl.values() if v["pc_a"] == v["pc_b"]),
        "max_abs_placement_part_w": max(abs(v["placement_part_w"]) for v in pl.values()),
        "level_part_range_w": [min(v["level_part_w"] for v in pl.values()), max(v["level_part_w"] for v in pl.values())]}
    return out


def fmt(x, n=4):
    return f"{x:+.{n}f}"


def text(o):
    L = ["M12, dated note 2's re-runs (note2_m12.py), POST HOC, from committed files only; nothing of M12 is refitted or changed.", ""]
    a = o["f1_his_pair"]
    L += ["f1 his pair is E182's T1 (in-sample by construction):",
          f"  T1's kinds {a['T1_kinds']} = E178-H-int8's {a['E178_H_int8_kinds']}, same words: {a['same_kinds_and_words']} ({a['T1_words']})",
          f"  E182 T1 (blind, registered) {fmt(a['E182_T1_w']['mean'])} [{fmt(a['E182_T1_w']['lo95'])}, {fmt(a['E182_T1_w']['hi95'])}] W, se "
          f"{a['E182_T1_w']['se']:.4f}; E182-HT {a['E182_HT_committed']}",
          f"  E178-H-int8 (blind, registered) {fmt(a['E178_H_int8_w']['mean'])} [{fmt(a['E178_H_int8_w']['lo95'])}, {fmt(a['E178_H_int8_w']['hi95'])}]; "
          f"M10 {fmt(a['E178_H_int8_w']['M10_dP'])}",
          f"  M12 on E178's pair {fmt(a['M12_pair_on_E178_w'], 6)} (se {a['M12_pair_se_w']:.4f}); minus T1 {fmt(a['M12_pair_minus_T1_w'], 6)}; "
          f"M12's in-sample T1 {fmt(a['M12_T1_fit_w'], 6)} (z {a['M12_T1_z']:+.3f})",
          "  leverage of each train in the int8 fit: " + ", ".join(f"{t} {v:.4f}" for t, v in a["trains_leverage"].items()),
          f"  k_walk fitted {a['k_walk_fitted_fJ']:.5f} fJ (se {a['k_walk_se_fJ']:.4f}); from T1 alone at the fitted betas and k_scp "
          f"{a['k_walk_from_T1_alone_fJ']:.5f} fJ, at E182-A's and E182-B's betas {a['k_walk_from_T1_alone_at_E182_betas_fJ']:.5f} fJ; "
          f"T1's design row {[round(x, 6) for x in a['T1_design_row']]}", ""]
    L.append("f2 E178's held-out kinds, new to E182 or also fitted by E182 (by word); rms M10 -> M12 (bias), centred, 0 inside, "
             "rms(M12) - rms(M10) [95%, heldout_m12.py's bootstrap]:")
    for g, v in o["f2_shared_kinds"]["groups"].items():
        d = v["M12_vs_M10"]
        L.append(f"  {g:30s} n {v['n']:2d}: {v['M10']['rms']:.4f} ({fmt(v['M10']['bias'])}) -> {v['M12']['rms']:.4f} ({fmt(v['M12']['bias'])}); "
                 f"centred {v['M10']['centred_rms']:.4f} -> {v['M12']['centred_rms']:.4f}; inside {v['zero_inside_M10']} -> {v['zero_inside_M12']}; "
                 f"{fmt(d['diff'])} [{fmt(d['lo95'])}, {fmt(d['hi95'])}]")
    L.append("  the 8 E182 also fitted: " + ", ".join(o["f2_shared_kinds"]["groups"]["E178 E182 also fitted (8)"]["rows"]))
    L.append("")
    f3 = o["f3_train_noise"]
    L += [f"f3 train noise: registered se {f3['se_registered_w']:.5f} W (half-width {f3['halfwidth_registered_w']} at 32 units); measured "
          f"int8 {f3['se_measured_w']['int8 (median of T1-T4)']:.5f}, fp32 {f3['se_measured_w']['fp32 (mean of T5, T6)']:.5f}; fp16: "
          f"{f3['se_measured_w']['fp16']}",
          "  each: " + ", ".join(f"{t} {v:.5f}" for t, v in f3["se_measured_each_w"].items()),
          "  train: M12 (se), M10 | registered: power if M12, separation | measured: power if M12, separation | REFIT's letter (train se "
          "alone): separation registered, measured"]
    for tid, v in f3["trains"].items():
        r, mm, lt = v["registered"], v["measured"], v["REFIT_letter_train_se_alone"]
        L.append(f"  {tid:9s} {fmt(v['M12_w'])} ({v['M12_se_w']:.4f}), {fmt(v['M10_w'])} | {r['power_if_M12']:.3f}, {r['separation']:.2f} | "
                 f"{mm['power_if_M12']:.3f}, {mm['separation']:.2f} | {lt['registered']['separation']:.2f}, {lt['measured']['separation']:.2f}")
    L.append("")
    f4 = o["f4_fp16"]
    L += ["f4 fp16's held-bit level as a fraction of F16-SAME's (" + f4["rule"] + "):",
          f"  fp16, 13 E178 kinds: {f4['fp16_13_kinds']['slope']:.3f} (se {f4['fp16_13_kinds']['se']:.3f}); fp32, 14 kinds: "
          f"{f4['fp32_14_kinds']['slope']:.3f} (se {f4['fp32_14_kinds']['se']:.3f}); fp16 rows with equal A and B words: {f4['fp16_rows_equal_words']}",
          f"  H16: F16-SAME {fmt(f4['H16_M12_F16_SAME_w'])} (se {f4['H16_M12_se_w']:.4f}), M10 {fmt(f4['H16_M10_w'])}; at fp16's fraction "
          f"{fmt(f4['H16_at_fp16_slope_w'])} (se {f4['H16_at_fp16_slope_se_w']:.4f}) [{fmt(f4['H16_at_fp16_slope_95_w'][0])}, "
          f"{fmt(f4['H16_at_fp16_slope_95_w'][1])}] W",
          f"  at fp32's measured train noise (each arm's own se combined): the scaled value is "
          f"{f4['at_measured_fp32_noise']['separation_scaled_vs_M10']:.1f} se from M10 and "
          f"{f4['at_measured_fp32_noise']['separation_scaled_vs_F16_SAME']:.1f} se from F16-SAME; power if it is true "
          f"{f4['at_measured_fp32_noise']['power_if_scaled']:.3f}", ""]
    f5 = o["f5_int8_session"]
    L += ["f5 int8 session level, E178's D minus E182's on the kinds both ran: " + ", ".join(f"{k} {fmt(v)}" for k, v in f5["E178_minus_E182_D_w"].items()),
          f"  range {fmt(f5['min_w'])} to {fmt(f5['max_w'])} W, mean {fmt(f5['mean_w'])}; M12's bias on E178's 13 int8 kinds {fmt(f5['M12_bias_E178_int8_w'])}; "
          f"M12-S1's shift {fmt(f5['M12_S1_shift_w'])}; c8 {f5['c8_w']:.4f} (se {f5['c8_se_w']:.4f})", ""]
    f7 = o["f7_code_nits"]
    fa = f7["a_flip_model_all_E182_kinds"]
    L += [f"f7a flip model (E178's, compiled unchanged) on E182's kinds: {fa['equal']} of {fa['kinds']} equal to forecast-e182.json's launch means; "
          f"unequal {fa['unequal']}",
          "f7b reference rows, counts-m12.json against the committed counts: " + "; ".join(
              f"{k} vs {v['against']}: mean {v['mean_equal']}, {v['n_points']} points {v['points_equal']}" for k, v in f7["b_reference_rows"].items())]
    c = f7["c_M10_int8_rate"]
    L += [f"f7c M10's int8 rate: the mean used {c['mean_rate_used']:.6e} /s, the median {c['median_rate']:.6e} ({c['median_over_mean_minus_1'] * 100:+.4f}%); "
          f"M10's int8 kinds move at most {c['max_abs_kind_change_w']:.2e} W and its int8 trains {c['max_abs_train_change_w']:.2e} W; the rates "
          "used against E182's registered: " + ", ".join(f"{t} {v * 100:+.4f}%" for t, v in c["rates_used_vs_registered"].items()),
          "f7d the two power forms: in f3 (committed = registered, train se combined with M12's; REFIT's letter = the train's se alone)"]
    e = f7["e_sigma_K_denominator"]
    L.append(f"f7e sigma_K: the code's denominator {e['code']['dof_K']:.3f} effective dof (sigma_K {e['code']['sigma_K_w']:.5f} W); " + "; ".join(
        f"{lab} ({v['denominator']}): sigma_K {v['sigma_K_w']:.5f}, d k_walk {v['d_k_walk_fJ']:+.2e} fJ, d k_scp {v['d_k_scp_fJ']:+.2e} fJ, d beta_A "
        f"{v['d_beta_A_w']:+.1e}, d beta_B {v['d_beta_B_w']:+.1e}, d c8 {v['d_c8_w']:+.1e} W" for lab, v in e["alternatives"].items()))
    s = f7["f_one_base_word_scope"]
    L.append(f"f7f pool 8's class S tiles (E171): {s['in_scope']} of {s['tiles']} hold one word on one side and two words one bit apart on "
             "the other (fp16: at most one bit a half)")
    for k, v in s["rows"].items():
        L.append(f"     {k}: {v['type']}, distinct A {v['distinct_a']}, B {v['distinct_b']}, xor popcount {v.get('xor_popcount')}, "
                 f"halves {v.get('xor_popcount_halves')}")
    L.append("")
    f8 = o["f8_records"]
    L += ["f8 the committed build record (" + f8["build_record"]["path"] + "): " + ", ".join(
        f"{k} {v}" for k, v in f8["build_record"]["binaries_sha256"].items()) + f", run_kinds.py {f8['build_record']['run_kinds.py']}"]
    p = f8["placement_on_E178_fp32"]
    L.append(f"f8 placement on E178's 14 fp32 kinds ({p['split']}): {p['rows_with_equal_popcounts']} of 14 with pc_A = pc_B; the placement part "
             f"at most {p['max_abs_placement_part_w']:.4f} W; the level part {p['level_part_range_w'][0]:.4f} to {p['level_part_range_w'][1]:.4f} W")
    for k, v in p["rows"].items():
        if v["pc_a"] != v["pc_b"]:
            L.append(f"     {k}: pc {v['pc_a']}/{v['pc_b']}, placement part {fmt(v['placement_part_w'])}, level part {v['level_part_w']:.4f}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    o = build(root)
    js = json.dumps(o, indent=1, sort_keys=True) + "\n"
    tx = text(o)
    pj, pt = os.path.join(HERE, "note2-m12.json"), os.path.join(HERE, "logs", "note2-m12.txt")
    if a.check:
        ok = open(pj).read() == js and open(pt).read() == tx
        print("CHECK PASS" if ok else "CHECK FAIL")
        return 0 if ok else 1
    open(pj, "w").write(js)
    open(pt, "w").write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
