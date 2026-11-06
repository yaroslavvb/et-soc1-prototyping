#!/usr/bin/env python3
"""E178 (Q146): the frozen forecasts of the one-number kinds - flips by the exact model, nets by the toggle bench, watts by M10.

    python3 -B forecast_e178.py --root <lab repo root> --dir tools/claims-v3/e178 [--cc cc]
        reads   <dir>/kinds-e178.json, <dir>/tiles/, <dir>/bench/counts-e178.json (the bench on the mini, run_kinds.py unchanged)
        builds  flipmodel_e178.c against rtl-sim/fma_toggle_v2/accum.c (unchanged), in a temporary directory
        writes  <dir>/forecast-e178.json and <dir>/forecast-e178.txt
    python3 -B forecast_e178.py --root <lab repo root> --check     # recomputes into a temporary directory and compares both files
                                                                    # byte for byte with the committed ones: CHECK PASS or FAIL

(i)  flips per op by class, from flipmodel_e178 (E178.md section 3): at the bench's three launch points and as the mean over a
     launch of E171's size (the C log's medians: fp32 539,295, fp16 539,149, int8 912,355 ops; the run mean adds the 20,000-op
     calibration launch);
(ii) nets per op by stage, from the bench, above the format's zeros (the committed zeros counts M10 uses);
(iii) watts: P, M10 frozen on (ii) (m10.json; fit_m10.chain_feats and predict_m10.d600 unchanged, s = 1, E171's measured zeros
     rates); F, P with its accumulator term replaced by (i)'s launch mean at M10's own price for it (floats: c_end's 6.0818 fJ
     per RF flip in place of M10's c_end, which samples one op at 2^19; int8: the bus price 7.9813 fJ on (i)'s launch mean in
     place of (ii)'s three points, for the classes (ii) files under lane_operand_bus). Uncertainty of a difference: M10's
     coefficient covariance (cov_J2) on the feature difference, and the scale band (x0.5 to x2) the registration states.
No card datum, no measured error and no file outside the lab repo is read. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import itertools
import json
import math
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

N_LAUNCH = {"fp32": 539295, "fp16": 539149, "int8": 912355}      # E171 C log (pass 17110) medians, 600 MHz, aifoundry3
N_CALIB = 20000
CPO = {"fp32": 546, "fp16": 546, "int8": 318}
RATE = {"fp32": 1117226099.79, "fp16": 1117107920.06, "int8": 1920872384.99}   # E171 e171.json items.<type>.zeros: 1024 x f / CPO x duty
CARDS = ("a3", "c1")
ACC_CLASSES_INT8 = ("c_store", "c_in", "c_out", "tenb_rz")       # (i)'s classes that (ii) files under lane_operand_bus


def launch_points(t):
    ops = 0.5 * 600e6 / CPO[t]
    return [int(ops * f) for f in (1 / 6, 1 / 2, 5 / 6)]


def build_model(root, cc, d):
    exe = os.path.join(d, "flipmodel_e178")
    src = os.path.join(root, "tools/claims-v3/e178/flipmodel_e178.c")
    acc = os.path.join(root, "rtl-sim/fma_toggle_v2/accum.c")
    subprocess.run([cc, "-O2", "-std=gnu11", f'-DACCUM_C="{acc}"', "-o", exe, src, "-lm"], check=True)
    return exe


def run_model(exe, t, aw, bw):
    pts = ",".join(str(p) for p in launch_points(t))
    out = subprocess.run([exe, t, aw, bw, str(N_LAUNCH[t]), pts, str(N_CALIB)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--dir", default="tools/claims-v3/e178")
    ap.add_argument("--cc", default="cc")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    D = os.path.join(root, a.dir)
    m10d = os.path.join(root, "docs/reports/data/2026-11-04-q142m-m10")
    sys.path.insert(0, m10d)
    import fit_m10 as FM      # noqa: E402  (the feature chain only; nothing is fitted)
    import predict_m10 as PM  # noqa: E402
    m10 = PM.load_m10()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    kinds = json.load(open(os.path.join(D, "kinds-e178.json")))["kinds"]
    bench = json.load(open(os.path.join(D, "bench/counts-e178.json")))["rows"]
    out = {"_what": "E178's frozen forecasts (forecast_e178.py)", "N_launch": N_LAUNCH, "N_calib": N_CALIB, "rate": RATE,
           "launch_points": {t: launch_points(t) for t in RATE}, "kinds": {}, "bench_check": {}}
    # the bench check: the mini's build against the committed (Intel) counts M10 uses, on the zeros and ones tiles
    for t in ("fp32", "fp16", "int8"):
        z_mini = bench[f"{t}.zeros"]["mean"]["vpu"]["nets_map"]
        z_comm = zeros[t]["vpu"]["nets_map"] if "vpu" in zeros[t] else None
        out["bench_check"][t] = {"zeros_nets_map_mini": z_mini, "zeros_nets_map_committed": z_comm}
    with tempfile.TemporaryDirectory() as td:
        exe = build_model(root, a.cc, td)
        for k in kinds:
            t, key = k["type"], k["key"]
            fl = run_model(exe, t, k["a_word"], k["b_word"])
            row = bench[key]
            tile = os.path.join(D, "tiles", t, k["name"] + ".bin")
            f = FM.chain_feats(row, tile, t, zeros, zr)
            fam = "int8" if t == "int8" else "float"
            fm = m10["families"][fam]
            feats = {q: float(f[q]) for q in fm["terms"]}
            P = {c: PM.d600(f, t, RATE[t], c, m10, 1.0) for c in CARDS}
            terms_w = {q: feats[q] * cj * RATE[t] for q, cj in zip(fm["terms"], fm["coef_J"])}
            lm, pm = fl["launch_mean"], fl["points_mean"]
            if fam == "float":
                e = fm["coef_J"][fm["terms"].index("c_end")]
                corr = RATE[t] * e * (lm["c_store"] - feats["c_end"])
            else:
                e = fm["coef_J"][fm["terms"].index("bus")]
                corr = RATE[t] * e * (sum(lm[c] for c in ACC_CLASSES_INT8) - sum(pm[c] for c in ACC_CLASSES_INT8))
            Fw = {c: P[c] + corr * (fm["card1_scale"] if c == "c1" else 1.0) for c in CARDS}
            zb = zeros[t]["vpu"]["by_stage"] if "vpu" in zeros[t] else None
            bst = row["mean"]["vpu"]["by_stage"]
            out["kinds"][key] = {
                "type": t, "name": k["name"], "v": k["v"], "w": k["w"], "a_word": k["a_word"], "b_word": k["b_word"],
                "popcount_a_word": k["popcount_a_word"], "popcount_b_word": k["popcount_b_word"], "rule": k["rule"], "role": k["role"],
                "flips_i": {"launch_mean": lm, "points_mean": pm, "run_mean": fl.get("run_mean"), "points": fl["points"],
                            "c_end_word": fl["c_end"], "c_store_fields": fl.get("c_store_fields")},
                "bench_ii": {"vpu_nets_map": row["mean"]["vpu"]["nets_map"], "unit_nets_map": row["mean"]["unit"]["nets_map"],
                             "by_stage": bst, "by_stage_above_zeros": {q: bst[q] - zb[q] for q in bst} if zb else None,
                             "check_mismatch": [p["check_mismatch"] for p in row["points"]]},
                "m10_features": feats, "m10_terms_w_a3": terms_w,
                "P_w": P, "F_w": Fw, "F_minus_P_w_a3": corr}
    ks = out["kinds"]

    def dfeat(k1, k2):
        return {q: ks[k1]["m10_features"][q] - ks[k2]["m10_features"][q] for q in ks[k1]["m10_features"]}

    def fit_sd(k1, k2):
        t = ks[k1]["type"]
        fm = m10["families"]["int8" if t == "int8" else "float"]
        dv = [dfeat(k1, k2)[q] for q in fm["terms"]]
        cov = fm["cov_J2"]
        var = sum(dv[i] * cov[i][j] * dv[j] for i in range(len(dv)) for j in range(len(dv)))
        return RATE[t] * math.sqrt(max(var, 0.0))

    def pair(k1, k2, why):
        x, y = ks[k1], ks[k2]
        tot = lambda r: r["flips_i"]["launch_mean"]["total"]  # noqa: E731
        dP = x["P_w"]["a3"] - y["P_w"]["a3"]
        dF = x["F_w"]["a3"] - y["F_w"]["a3"]
        return {"a": k1, "b": k2, "why": why, "d_flips_i_launch_mean": tot(x) - tot(y),
                "ratio_flips_i": tot(x) / tot(y) if tot(y) else None,
                "d_nets_ii": x["bench_ii"]["vpu_nets_map"] - y["bench_ii"]["vpu_nets_map"],
                "d_popcount_a_word": x["popcount_a_word"] - y["popcount_a_word"],
                "dP_w_a3": dP, "dP_w_c1": x["P_w"]["c1"] - y["P_w"]["c1"], "dF_w_a3": dF, "dF_w_c1": x["F_w"]["c1"] - y["F_w"]["c1"],
                "fit_sd_w_a3": fit_sd(k1, k2), "scale_band_w_a3": sorted([dP / 2, dP * 2])}
    pairs = {"his_4_5": [], "crossed": [], "equal_popcount_different_flips": [], "equal_flips_different_values": [], "bridge": []}
    for t in ("fp32", "fp16", "int8"):
        pairs["his_4_5"].append(pair(f"{t}.e178_v5", f"{t}.e178_v4", "his example: a matrix of 5s against a matrix of 4s"))
        pairs["crossed"].append(pair(f"{t}.e178_a4_b5", f"{t}.e178_a5_b4", "the same products and accumulator, A and B swapped"))
        pairs["crossed"].append(pair(f"{t}.e178_a4_b5", f"{t}.e178_v4", "B 5 against B 4 under A 4"))
        pairs["bridge"].append(pair(f"{t}.neg_ones", f"{t}.ones", "the committed one-number pair (E78, E82)"))
        grid = [k for k in ks if ks[k]["type"] == t and ks[k]["v"] == ks[k]["w"] and ks[k]["role"] in ("grid", "core", "low", "bridge")]
        for k1, k2 in itertools.combinations(sorted(grid), 2):
            x, y = ks[k1], ks[k2]
            fx, fy = x["flips_i"]["launch_mean"]["total"], y["flips_i"]["launch_mean"]["total"]
            if x["popcount_a_word"] == y["popcount_a_word"] and abs(fx - fy) >= 0.10 * max(fx, fy):
                pairs["equal_popcount_different_flips"].append(pair(*sorted((k1, k2), key=lambda q: -ks[q]["flips_i"]["launch_mean"]["total"]),
                                                                    "equal popcount of the operand word, flips differ by 10% or more"))
            if x["v"] != y["v"] and abs(fx - fy) <= 0.01 * max(fx, fy) and abs(abs(x["v"]) - abs(y["v"])) > 0:
                pairs["equal_flips_different_values"].append(pair(k1, k2, "different values, launch-mean flips within 1%"))
    out["pairs"] = pairs
    # the ranking and the extremes, per format, over the one-number kinds (v = w and the crosses)
    rank, extremes = {}, {}
    for t in ("fp32", "fp16", "int8"):
        kk = [k for k in ks if ks[k]["type"] == t]
        rank[t] = {"by_P_a3": sorted(kk, key=lambda q: ks[q]["P_w"]["a3"]),
                   "by_F_a3": sorted(kk, key=lambda q: ks[q]["F_w"]["a3"]),
                   "by_flips_i": sorted(kk, key=lambda q: ks[q]["flips_i"]["launch_mean"]["total"]),
                   "by_nets_ii": sorted(kk, key=lambda q: ks[q]["bench_ii"]["vpu_nets_map"])}
        ps = [(abs(ks[x]["P_w"]["a3"] - ks[y]["P_w"]["a3"]), x, y) for x, y in itertools.combinations(kk, 2)]
        ps.sort()
        lo = [p for p in ps if ks[p[1]]["v"] != ks[p[2]]["v"] or ks[p[1]]["w"] != ks[p[2]]["w"]]
        extremes[t] = {"largest": pair(*sorted(ps[-1][1:], key=lambda q: -ks[q]["P_w"]["a3"]), "largest |dP| in the format"),
                       "smallest": pair(lo[0][1], lo[0][2], "smallest |dP| between different kinds in the format")}
    out["ranking"], out["extremes"] = rank, extremes
    W = tempfile.mkdtemp() if a.check else D
    json.dump(out, open(os.path.join(W, "forecast-e178.json"), "w"), indent=1, sort_keys=True)
    # the readable table
    L = []
    L.append("E178 forecasts, frozen before any card datum (forecast_e178.py). Per TensorFMA op on one minion; W at 600 MHz, s = 1.")
    L.append("(i) flips: the exact model's launch mean; (ii) nets: the bench's vpu nets_map above zeros (3 launch points);")
    L.append("P: M10 frozen on (ii); F: P with the accumulator at (i)'s launch mean. D is board W over the format's zeros.")
    for t in ("fp32", "fp16", "int8"):
        L.append("")
        L.append(f"{t}: kind              A word      pc   (i) flips  c_store  buses+rz   (ii) nets   P a3 W   F a3 W   P c1 W   F c1 W")
        zn = bench[f"{t}.zeros"]["mean"]["vpu"]["nets_map"]
        for k in rank[t]["by_P_a3"]:
            r = ks[k]
            lm = r["flips_i"]["launch_mean"]
            L.append(f"  {r['name']:20s} {r['a_word']}/{r['b_word'][6:]} {r['popcount_a_word']:3d} {lm['total']:10.0f} {lm['c_store']:8.0f} "
                     f"{lm['total'] - lm['c_store']:9.0f} {r['bench_ii']['vpu_nets_map'] - zn:10.0f} {r['P_w']['a3']:8.4f} {r['F_w']['a3']:8.4f} "
                     f"{r['P_w']['c1']:8.4f} {r['F_w']['c1']:8.4f}")
    L.append("")
    for grp, lst in pairs.items():
        L.append(f"pairs: {grp}")
        for p in lst:
            L.append(f"  {p['a']:22s} - {p['b']:22s} d(i) {p['d_flips_i_launch_mean']:+9.0f} (x{p['ratio_flips_i'] or 0:.3f})  d(ii) {p['d_nets_ii']:+8.0f}  "
                     f"dpc {p['d_popcount_a_word']:+3d}  dP {p['dP_w_a3']:+.4f} W  dF {p['dF_w_a3']:+.4f} W  fit sd {p['fit_sd_w_a3']:.4f}")
    L.append("")
    for t in ("fp32", "fp16", "int8"):
        e = extremes[t]
        L.append(f"{t}: largest pair {e['largest']['a']} - {e['largest']['b']} dP {e['largest']['dP_w_a3']:+.4f} W (dF {e['largest']['dF_w_a3']:+.4f}); "
                 f"smallest {e['smallest']['a']} - {e['smallest']['b']} dP {e['smallest']['dP_w_a3']:+.5f} W (dF {e['smallest']['dF_w_a3']:+.5f})")
    open(os.path.join(W, "forecast-e178.txt"), "w").write("\n".join(L) + "\n")
    if a.check:
        same = all(open(os.path.join(W, f), "rb").read() == open(os.path.join(D, f), "rb").read()
                   for f in ("forecast-e178.json", "forecast-e178.txt"))
        print("CHECK", "PASS" if same else "FAIL")
        return 0 if same else 1
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
