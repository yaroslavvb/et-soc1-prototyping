#!/usr/bin/env python3
"""E182 (Q153): the frozen forecasts of E182's one-number kinds, and the held-bit split each forecast predicts (E182.md section 4).

    /usr/bin/python3 -B forecast_e182.py --root <lab repo root>            # writes forecast-e182.json and forecast-e182.txt beside it
    /usr/bin/python3 -B forecast_e182.py --root <lab repo root> --check    # recomputes into a temporary directory and compares both
                                                                           # files byte for byte: CHECK PASS or FAIL
Reads kinds-e182.json, the tiles, bench/counts-e182.json (the toggle bench on the mini, run_kinds.py unchanged) and committed files only:
  (i)   flips per op by class: E178's exact flip model, tools/claims-v3/e178/flipmodel_e178.c, compiled UNCHANGED against
        rtl-sim/fma_toggle_v2/accum.c (unchanged), at the bench's three launch points and as the launch mean at E178's measured launch
        size (m10acc.json N_e178: int8 913,813, fp32 539,132 ops; the C log's medians on 6 Nov);
  (ii)  nets per op by stage from the bench, above the format's zeros (M10's counts form);
  P     M10 frozen on (ii): docs/reports/data/2026-11-04-q142m-m10 fit_m10.chain_feats and predict_m10.d600 unchanged, s = 1, at E178's
        median measured rate per type (forecasts-e182-m10acc.json `rate`), aifoundry3 and card 1;
  ACC   M10-ACC's frozen term (Q153 lane m10acc; m10acc.json, registered b5586759, frozen d87bb417), by its own predictor's functions
        (tools/claims-v3/m10-acc/predict_m10acc.py build, trace and term_w, unchanged); the arm is P + ACC. The term did not enter M10
        (m10acc.json families.*.enters false): a reported arm;
  E     E178's measured price applied to the flips, a reported arm: the line E178-W-int8 read on 6 Nov (OLS of the 13 int8 kinds'
        measured D on (i)'s launch-mean flips, re-fitted here from E178's committed scored.json and checked to equal its committed slope,
        2.7812 fJ a flip), D_E = a + (b / R) x flips x rate; for fp32 the same OLS over E178's 14 fp32 kinds (its reported slope 0.352 fJ,
        se 1.15: an arm with almost no weight, recorded so the float pairs have one).
The held-bit split each arm predicts (E182.md section 4.3): beta_A and beta_B, W per held 1-bit a byte on A's side and on B's, read
from the arm's own D by the trains' formulas on the +-1 set (x_sign = D(-1,-1) - D(1,1) = 7 (beta_A + beta_B); x_swap = D(1,-1) -
D(-1,1) = 7 (beta_B - beta_A)) and by the quartet fit over Q1 and Q2's 16 kinds (one level per product, plus beta_A h_A + beta_B h_B,
h the popcount a byte). No card datum of E182 exists; the only measured inputs are E178's committed levels for arm E.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
CPO = {"fp32": 546, "fp16": 546, "int8": 318}
N_CALIB = 20000
CARDS = ("a3", "c1")
DD = "docs/reports/data"
M10D = f"{DD}/2026-11-04-q142m-m10"
ACCD = f"{DD}/2026-11-07-q153-m10acc"
E178D = f"{DD}/2026-11-06-e178-one-number-aifoundry3"
PAIRS = (  # the registered pairs (E182.md section 5): (id, first, second, what) - each read as D(first) - D(second)
    ("T1", "int8.e178_v5", "int8.e178_v4", "his pair: int8 5s against 4s (E178-H-int8 again)"),
    ("T2", "int8.e182_a1_bm1", "int8.e182_am1_b1", "the swap at product -1: A 1 / B -1 against A -1 / B 1 (x_swap)"),
    ("T3", "int8.neg_ones", "int8.ones", "the sign flip at product +1: -1s against 1s (x_sign)"),
    ("T4", "int8.e178_a4_b5", "int8.e178_a5_b4", "the crossed pair: A 4 / B 5 against A 5 / B 4 (a one-bit swap at product 20)"),
    ("T5", "fp32.e182_a1_b3fffffff", "fp32.e182_a3fffffff_b1", "the float swap: A 1.0 / B 0x3FFFFFFF against the reverse"),
    ("T6", "fp32.e178_v5", "fp32.e178_v4", "his pair in fp32: 5.0s against 4.0s (E178-H-fp32 again)"),
)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def launch_points(t):
    ops = 0.5 * 600e6 / CPO[t]
    return [int(ops * f) for f in (1 / 6, 1 / 2, 5 / 6)]


def run_flips(exe, t, aw, bw, n):
    pts = ",".join(str(p) for p in launch_points(t))
    out = subprocess.run([exe, t, aw, bw, str(n), pts, str(N_CALIB)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def ols(xs, ys):
    """score_e178.ols, copied (slope, se) plus the intercept"""
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((a - mx) ** 2 for a in xs)
    b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sxx
    resid = [c - (my + b * (a - mx)) for a, c in zip(xs, ys)]
    se = math.sqrt(sum(r * r for r in resid) / (len(xs) - 2) / sxx)
    return b, se, my - b * mx


def solve(A, y):
    """least squares by the normal equations (Gauss-Jordan; tiny, well-posed systems only)"""
    n = len(A[0])
    M = [[sum(A[r][i] * A[r][j] for r in range(len(A))) for j in range(n)] + [sum(A[r][i] * y[r] for r in range(len(A)))] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * z for x, z in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def quartet_design(kinds):
    """rows of the quartet fit: one indicator per product group, then h_A and h_B (popcount a byte)"""
    groups = sorted({k["product_group"] for k in kinds})
    X = []
    for k in kinds:
        X.append([1.0 if k["product_group"] == g else 0.0 for g in groups] + [k["popcount_a_word"] / 4.0, k["popcount_b_word"] / 4.0])
    return X, groups


def split_of(D, kinds_by_key, qkeys):
    """(beta_A, beta_B) of one arm: the +-1 set's trains formulas and the quartet fit (E182.md section 4.3)"""
    xs = D["int8.neg_ones"] - D["int8.ones"]
    xw = D["int8.e182_a1_bm1"] - D["int8.e182_am1_b1"]
    q = [kinds_by_key[k] for k in qkeys]
    X, _ = quartet_design(q)
    b = solve(X, [D[k] for k in qkeys])
    return {"x_sign_w": xs, "x_swap_w": xw, "beta_A_w_per_bit": (xs - xw) / 14, "beta_B_w_per_bit": (xs + xw) / 14,
            "quartet_fit": {"beta_A_w_per_bit": b[-2], "beta_B_w_per_bit": b[-1]}}


def build(root, out_dir):
    sys.path.insert(0, os.path.join(root, M10D))
    sys.path.insert(0, os.path.join(root, "tools/claims-v3/m10-acc"))
    import fit_m10 as FM      # noqa: E402  (the feature chain only)
    import predict_m10 as PM  # noqa: E402
    import predict_m10acc as PA  # noqa: E402  (build, trace and term_w only)
    D = os.path.join(root, "tools/claims-v3/e182")
    m10 = PM.load_m10()
    acc = json.load(open(os.path.join(root, ACCD, "m10acc.json")))
    grid = json.load(open(os.path.join(root, ACCD, "forecasts-e182-m10acc.json")))
    N, RATE = acc["N_e178"], grid["rate"]
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    kinds = json.load(open(os.path.join(D, "kinds-e182.json")))["kinds"]
    kb = {k["key"]: k for k in kinds}
    bench = json.load(open(os.path.join(D, "bench/counts-e182.json")))["rows"]
    sc = json.load(open(os.path.join(root, E178D, "scored.json")))
    sk = sc["primary"]["reported"]["kinds"]
    out = {"_what": "E182's frozen forecasts (forecast_e182.py): flips (i), nets (ii), P (M10 frozen), P + ACC (M10-ACC's term), "
                    "E (E178's measured price), and the held-bit split each predicts",
           "N_launch": N, "N_calib": N_CALIB, "rate": RATE, "launch_points": {t: launch_points(t) for t in ("fp32", "int8")},
           "inputs_sha256": {p: sha(os.path.join(root, p)) for p in (
               f"{M10D}/m10.json", f"{ACCD}/m10acc.json", f"{ACCD}/forecasts-e182-m10acc.json", f"{E178D}/scored.json",
               "tools/claims-v3/e178/flipmodel_e178.c", "rtl-sim/fma_toggle_v2/accum.c", "tools/claims-v3/m10-acc/predict_m10acc.py",
               "tools/claims-v3/m10-acc/acctrace_m10acc.c", "tools/claims-v3/e182/kinds-e182.json", "tools/claims-v3/e182/bench/counts-e182.json")},
           "kinds": {}, "bench_check": {}}
    # the bench check: this run's zeros and E178's eight reused tiles against E178's committed counts (the same recorded build)
    e178c = json.load(open(os.path.join(root, "tools/claims-v3/e178/bench/counts-e178.json")))["rows"]
    for key in [f"{t}.zeros" for t in ("fp32", "fp16", "int8")] + [k["key"] for k in kinds if k["rule"] == "Q3"] + ["int8.ones", "int8.neg_ones"]:
        out["bench_check"][key] = {"vpu_nets_map_e182": bench[key]["mean"]["vpu"]["nets_map"],
                                   "vpu_nets_map_e178": e178c[key]["mean"]["vpu"]["nets_map"],
                                   "equal": bench[key]["mean"] == e178c[key]["mean"]}
    # arm E's lines, re-fitted from E178's committed levels
    eline = {}
    for t, nkinds in (("int8", 13), ("fp32", 14)):
        ks = sorted(k for k in sk if k.startswith(t + "."))
        assert len(ks) == nkinds, (t, len(ks))
        b, se, a0 = ols([sk[k]["flips_launch_mean"] for k in ks], [sk[k]["D_w"] for k in ks])
        R = statistics.mean(sk[k]["rate_per_s"] for k in ks)
        eline[t] = {"kinds": ks, "n": len(ks), "slope_w_per_flip": b, "intercept_w": a0, "mean_rate_per_s": R,
                    "price_fJ_per_flip": b / R * 1e15, "se_fJ": se / R * 1e15}
    w8 = sc["primary"]["rules"]["E178-W-int8"]["slope_fJ_per_flip"]
    assert abs(eline["int8"]["price_fJ_per_flip"] - w8) < 1e-9, (eline["int8"]["price_fJ_per_flip"], w8)
    f32 = sc["primary"]["reported"]["floats_ranking_and_slope"]["fp32"]["slope_fJ_per_flip"]
    assert abs(eline["fp32"]["price_fJ_per_flip"] - f32) < 1e-9, (eline["fp32"]["price_fJ_per_flip"], f32)
    eline["int8"]["e178_rule_95_fJ"] = [sc["primary"]["rules"]["E178-W-int8"]["lo95_fJ"], sc["primary"]["rules"]["E178-W-int8"]["hi95_fJ"]]
    out["arm_E_lines"] = eline
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "flipmodel_e178")
        subprocess.run(["cc", "-O2", "-std=gnu11", f'-DACCUM_C="{os.path.join(root, "rtl-sim/fma_toggle_v2/accum.c")}"', "-o", exe,
                        os.path.join(root, "tools/claims-v3/e178/flipmodel_e178.c"), "-lm"], check=True)
        aexe = PA.build(td)
        for k in kinds:
            t, key = k["type"], k["key"]
            fl = run_flips(exe, t, k["a_word"], k["b_word"], N[t])
            row = bench[key]
            tile = os.path.join(D, "tiles", t, k["name"] + ".bin") if k["tile"] == "new" else os.path.join(root, k["tile"].split(":", 1)[1])
            raw = open(tile, "rb").read()
            assert hashlib.sha256(raw).hexdigest() == k["sha256"]
            f = FM.chain_feats(row, tile, t, zeros, zr)
            fam = "int8" if t == "int8" else "float"
            fm = m10["families"][fam]
            feats = {q: float(f[q]) for q in fm["terms"]}
            P = {c: PM.d600(f, t, RATE[t], c, m10, 1.0) for c in CARDS}
            tr = PA.trace(aexe, t, raw, [N[t]], td)
            xa, xb = tr["x_acc"][str(N[t])]["total"], tr["x_bth_per_op"]
            ACC = {}
            for c in CARDS:
                w, ends, entered = PA.term_w(acc, t, xa, xb, RATE[t], c, 1.0)
                ACC[c] = {"term_w": w, "term_w_95": ends, "entered_M10": entered}
            lm = fl["launch_mean"]
            el = eline[t]
            E = {c: (el["intercept_w"] + el["price_fJ_per_flip"] * 1e-15 * lm["total"] * RATE[t]) *
                 (acc["card1_scale"][fam] if c == "c1" else 1.0) for c in CARDS}
            zb = zeros[t]["vpu"]["by_stage"] if "vpu" in zeros[t] else None
            bst = row["mean"]["vpu"]["by_stage"]
            out["kinds"][key] = {
                "type": t, "name": k["name"], "a": k["a"], "b": k["b"], "a_word": k["a_word"], "b_word": k["b_word"],
                "popcount_a_word": k["popcount_a_word"], "popcount_b_word": k["popcount_b_word"],
                "hamming_a_b_word": k["hamming_a_b_word"], "product": k["product"], "product_group": k["product_group"],
                "rule": k["rule"], "role": k["role"],
                "flips_i": {"launch_mean": lm, "points_mean": fl["points_mean"], "run_mean": fl.get("run_mean")},
                "bench_ii": {"vpu_nets_map": row["mean"]["vpu"]["nets_map"], "by_stage_above_zeros": {q: bst[q] - zb[q] for q in bst} if zb else None,
                             "check_mismatch": [p["check_mismatch"] for p in row["points"]]},
                "m10_features": feats, "P_w": P, "ACC": ACC, "PACC_w": {c: P[c] + ACC[c]["term_w"] for c in CARDS},
                "x_acc_per_op": xa, "x_bth_per_op": xb, "E_w": E}
    ks = out["kinds"]
    # the checks against earlier frozen forecasts of the same quantity (the Builds-on rule's item 2)
    e178f = json.load(open(os.path.join(root, "tools/claims-v3/e178/forecast-e178.json")))
    out["inputs_sha256"]["tools/claims-v3/e178/forecast-e178.json"] = sha(os.path.join(root, "tools/claims-v3/e178/forecast-e178.json"))
    r171 = e178f["rate"]
    out["check_P_against_e178"] = {k: {"P_a3_e182": ks[k]["P_w"]["a3"], "P_a3_e178_at_this_rate": e178f["kinds"][k]["P_w"]["a3"] * RATE[ks[k]["type"]] / r171[ks[k]["type"]],
                                       "abs_diff": abs(ks[k]["P_w"]["a3"] - e178f["kinds"][k]["P_w"]["a3"] * RATE[ks[k]["type"]] / r171[ks[k]["type"]])}
                                   for k in ks if k in e178f["kinds"]}
    gk = {(x["type"], x["a_word"], x["b_word"]): x for x in grid["kinds"]}
    byprod = {}
    for x in grid["kinds"]:
        if x["type"] == "int8":
            a_, b_ = (int(x[w][-2:], 16) for w in ("a_word", "b_word"))
            byprod.setdefault((a_ - 256 if a_ > 127 else a_) * (b_ - 256 if b_ > 127 else b_), x)
    chk = {}
    for k, v in ks.items():
        g = gk.get((v["type"], v["a_word"], v["b_word"]))
        how = "the grid's own kind"
        if g is None and v["type"] == "int8":
            g, how = byprod.get(v["product"]), "the grid's kind of the same product (the int8 term depends only on the product)"
        chk[k] = {"against": how if g else "not in the grid: the predictor's own trace", "abs_diff_w_a3": abs(v["ACC"]["a3"]["term_w"] - g["term_w_a3"]) if g else None}
    out["check_ACC_against_grid"] = chk

    def fit_sd(k1, k2):
        t = ks[k1]["type"]
        fm = m10["families"]["int8" if t == "int8" else "float"]
        dv = [ks[k1]["m10_features"][q] - ks[k2]["m10_features"][q] for q in fm["terms"]]
        cov = fm["cov_J2"]
        var = sum(dv[i] * cov[i][j] * dv[j] for i in range(len(dv)) for j in range(len(dv)))
        return RATE[t] * math.sqrt(max(var, 0.0))
    pairs = {}
    for pid, x, y, what in PAIRS:
        X, Y = ks[x], ks[y]
        tot = lambda r: r["flips_i"]["launch_mean"]["total"]  # noqa: E731
        p = {"first": x, "second": y, "what": what, "d_flips_i": tot(X) - tot(Y),
             "d_flips_by_class": {c: X["flips_i"]["launch_mean"][c] - Y["flips_i"]["launch_mean"][c] for c in X["flips_i"]["launch_mean"]},
             "d_nets_ii": X["bench_ii"]["vpu_nets_map"] - Y["bench_ii"]["vpu_nets_map"],
             "d_popcount_a_word": X["popcount_a_word"] - Y["popcount_a_word"], "d_popcount_b_word": X["popcount_b_word"] - Y["popcount_b_word"],
             "fit_sd_w_a3": fit_sd(x, y)}
        for arm, fld in (("P", "P_w"), ("PACC", "PACC_w"), ("E", "E_w")):
            for c in CARDS:
                p[f"d{arm}_w_{c}"] = X[fld][c] - Y[fld][c]
        p["dACC_term_w_a3"] = X["ACC"]["a3"]["term_w"] - Y["ACC"]["a3"]["term_w"]
        pairs[pid] = p
    out["pairs"] = pairs
    qkeys = [k["key"] for k in kinds if k["rule"] in ("Q1", "Q2")]
    out["quartet_keys"] = qkeys
    out["held_bit_split"] = {}
    for arm, fld in (("P", "P_w"), ("PACC", "PACC_w"), ("E", "E_w")):
        for c in CARDS:
            out["held_bit_split"][f"{arm}_{c}"] = split_of({k: ks[k][fld][c] for k in ks}, kb, qkeys)
    out["held_bit_hypotheses"] = {
        "_what": "the four splits the rules tell apart (E182.md section 4.3), in W per held 1-bit a byte at aifoundry3; the sizes are set "
                 "by arm E's B-side price, so each hypothesis is a re-placement of the same total, not a forecast",
        "B-ONLY (every arm)": {"beta_A": 0.0, "beta_B": out["held_bit_split"]["E_a3"]["beta_B_w_per_bit"]},
        "A+B, equal a bit": {"beta_A": out["held_bit_split"]["E_a3"]["beta_B_w_per_bit"] / 2, "beta_B": out["held_bit_split"]["E_a3"]["beta_B_w_per_bit"] / 2},
        "A-ONLY": {"beta_A": out["held_bit_split"]["E_a3"]["beta_B_w_per_bit"], "beta_B": 0.0},
        "NONE": {"beta_A": 0.0, "beta_B": 0.0}}
    # the ranking (int8 kinds by each arm) and the per-flip slope each arm implies over E182's int8 kinds
    i8 = sorted(k for k in ks if ks[k]["type"] == "int8")
    out["ranking_int8"] = {arm: sorted(i8, key=lambda q: (ks[q][fld]["a3"], q)) for arm, fld in (("P", "P_w"), ("PACC", "PACC_w"), ("E", "E_w"))}
    R8 = RATE["int8"]
    out["slope_int8_fJ_per_flip"] = {arm: ols([ks[q]["flips_i"]["launch_mean"]["total"] for q in i8], [ks[q][fld]["a3"] for q in i8])[0] / R8 * 1e15
                                     for arm, fld in (("P", "P_w"), ("PACC", "PACC_w"), ("E", "E_w"))}
    json.dump(out, open(os.path.join(out_dir, "forecast-e182.json"), "w"), indent=1, sort_keys=True)
    L = ["E182 forecasts, frozen before any card datum (forecast_e182.py). Per TensorFMA op on one minion; W at 600 MHz, s = 1, aifoundry3.",
         "(i) flips: E178's exact model, launch mean at E178's N; (ii) nets: the bench's vpu nets_map above zeros; P: M10 frozen on (ii);",
         "P+ACC: P plus M10-ACC's frozen term (it did not enter M10); E: E178's measured line (int8 2.781 fJ a flip; fp32 0.352 fJ). D = W over zeros.",
         ""]
    for t in ("int8", "fp32"):
        L.append(f"{t}: kind                     A word     B word     pcA pcB  hd  (i) flips  c_store  tenb_rz     scp  (ii) nets    P W  P+ACC W     E W")
        zn = bench[f"{t}.zeros"]["mean"]["vpu"]["nets_map"]
        for q in sorted((k for k in ks if ks[k]["type"] == t), key=lambda q: (ks[q]["product_group"], q)):
            r = ks[q]
            lm = r["flips_i"]["launch_mean"]
            L.append(f"  {r['name']:24s} {r['a_word']} {r['b_word']} {r['popcount_a_word']:3d} {r['popcount_b_word']:3d} {r['hamming_a_b_word']:3d} "
                     f"{lm['total']:10.0f} {lm['c_store']:8.0f} {lm['tenb_rz']:8.0f} {lm['scp']:7.0f} {r['bench_ii']['vpu_nets_map'] - zn:10.0f} "
                     f"{r['P_w']['a3']:7.4f} {r['PACC_w']['a3']:8.4f} {r['E_w']['a3']:7.4f}")
        L.append("")
    L.append("the registered pairs, D(first) - D(second), W at aifoundry3 (card 1 in forecast-e182.json):")
    for pid, p in pairs.items():
        L.append(f"  {pid} {p['first']:24s} - {p['second']:24s} d(i) {p['d_flips_i']:+8.0f}  d(ii) {p['d_nets_ii']:+8.0f}  "
                 f"dP {p['dP_w_a3']:+.4f}  dP+ACC {p['dPACC_w_a3']:+.4f}  dE {p['dE_w_a3']:+.4f}  fit sd {p['fit_sd_w_a3']:.4f}")
    L.append("")
    L.append("the held-bit split each arm predicts (W per held 1-bit a byte; +-1 set by the trains' formulas / the quartet fit):")
    for kk, v in out["held_bit_split"].items():
        L.append(f"  {kk:8s} beta_A {v['beta_A_w_per_bit']:+.5f} / {v['quartet_fit']['beta_A_w_per_bit']:+.5f}   "
                 f"beta_B {v['beta_B_w_per_bit']:+.5f} / {v['quartet_fit']['beta_B_w_per_bit']:+.5f}   (x_sign {v['x_sign_w']:+.4f}, x_swap {v['x_swap_w']:+.4f})")
    L.append("")
    L.append("arm E's lines (re-fitted from E178's committed scored.json): " + "; ".join(
        f"{t} {v['price_fJ_per_flip']:.4f} fJ a flip (se {v['se_fJ']:.3f}), intercept {v['intercept_w']:+.4f} W, n {v['n']}" for t, v in eline.items()))
    L.append("per-flip slope over E182's 20 int8 kinds, by arm (fJ a flip): " + ", ".join(f"{a} {v:.3f}" for a, v in out["slope_int8_fJ_per_flip"].items()))
    L.append("check: P against E178's frozen P at this rate, largest |diff| %.1e W over %d kinds; M10-ACC's term against its frozen grid, largest |diff| %.1e W over %d kinds"
             % (max(v["abs_diff"] for v in out["check_P_against_e178"].values()), len(out["check_P_against_e178"]),
                max(v["abs_diff_w_a3"] for v in out["check_ACC_against_grid"].values() if v["abs_diff_w_a3"] is not None),
                sum(1 for v in out["check_ACC_against_grid"].values() if v["abs_diff_w_a3"] is not None)))
    L.append("bench check (vpu nets_map, this run against E178's committed counts): " + ", ".join(
        f"{k} {'equal' if v['equal'] else 'DIFFERS'}" for k, v in out["bench_check"].items()))
    open(os.path.join(out_dir, "forecast-e182.txt"), "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    D = os.path.join(root, "tools/claims-v3/e182")
    if not a.check:
        build(root, D)
        print("wrote forecast-e182.json and forecast-e182.txt")
        return 0
    with tempfile.TemporaryDirectory() as td:
        build(root, td)
        ok = all(open(os.path.join(td, f), "rb").read() == open(os.path.join(D, f), "rb").read() for f in ("forecast-e182.json", "forecast-e182.txt"))
    print("CHECK PASS" if ok else "CHECK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
