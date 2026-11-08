#!/usr/bin/env python3
"""M12 (Q157): the refit, POST HOC, on E182's committed rows only (REFIT.md section 3). M10 stays frozen; nothing of E178 or pool 8
is read here.

    /usr/bin/python3 -B tools/claims-v3/m12/fit_m12.py --root .            # writes m12.json and fit-m12.txt beside this file
    /usr/bin/python3 -B tools/claims-v3/m12/fit_m12.py --root . --check    # recomputes into memory and compares both files byte for byte

Reads: E182's trains-e182.json and scored.json (kinds passes: D, sd, n, rate and M10's scored P; the trains' committed P lines),
tools/claims-v3/e182/forecast-e182.json (words, popcounts, flips by class), e182.json (the int8 random anchor's D, for arm M12-S1),
M10's m10.json (its float card term, asserted) and E184 arm B's scored file (the SRAM factor, carried as a reported candidate only).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m12_common as C  # noqa: E402

PARAMS8 = ["c8_w", "k_walk_fJ", "k_scp_fJ", "beta_A_w", "beta_B_w"]
PARAMS8_1K = ["c8_w", "k_fJ", "beta_A_w", "beta_B_w"]
PARAMS_F = ["c_f_w", "gamma_A_w", "gamma_B_w"]
PARAMS_G = ["g_f", "gamma_A_w", "gamma_B_w"]


def named(names, b, cov):
    return {n: {"value": b[i], "se": math.sqrt(cov[i][i])} for i, n in enumerate(names)}


def build(root):
    sc = C.load(root, f"{C.E182D}/scored.json")
    tr = C.load(root, f"{C.E182D}/trains-e182.json")["trains"]
    fc = C.load(root, C.E182F)["kinds"]
    red = C.load(root, f"{C.E182D}/e182.json")
    m10 = C.load(root, f"{C.M10D}/m10.json")
    e184 = C.load(root, C.E184S)
    assert abs(m10["families"]["float"]["card1_scale"] - C.CARD1_FLOAT) < 1e-15
    K = sc["reported"]["kinds"]
    inputs = [f"{C.E182D}/scored.json", f"{C.E182D}/trains-e182.json", f"{C.E182D}/e182.json", C.E182F, f"{C.M10D}/m10.json", C.E184S]
    out = {"_model": "M12 (Q157): M10 refitted POST HOC on E182's committed rows for held-word tiles (tools/claims-v3/m12/REFIT.md)",
           "label": "post hoc", "card": "aifoundry3", "inputs_sha256": {p: C.sha(os.path.join(root, p)) for p in inputs},
           "equations": {"int8": "D8 = c8 + R (k_walk F_walk + k_scp F_scp) 1e-15 + beta_A h_A + beta_B h_B; F_walk = c_store + c_in + c_out, "
                                 "F_scp = scp (flips an op, E178's flip model, launch mean); h = word popcount / 4",
                         "float": "Df = P10 + c_f + gamma_A pc_A + gamma_B pc_B; P10 = M10 frozen at the session's s and the measured rate; "
                                  "pc the 32-bit lane words' popcounts (a one-base-word side: the mean); fp16 takes fp32's terms (F16-SAME)",
                         "card1": "the float increment Df - P10 times M10's float card term %.8f; reported only" % C.CARD1_FLOAT}}
    # ---- the check: E182-A and E182-B from the trains by E182.md section 5.1's formulas
    bA = (tr["T3"]["estimate"]["mean"] - tr["T2"]["estimate"]["mean"]) / 14
    bB = (tr["T3"]["estimate"]["mean"] + tr["T2"]["estimate"]["mean"]) / 14
    assert abs(bA - sc["rules"]["E182-A"]["beta_A"]["mean"]) < 1e-12 and abs(bB - sc["rules"]["E182-B"]["beta_B"]["mean"]) < 1e-12
    out["check_trains_betas"] = {"beta_A_w": bA, "beta_B_w": bB, "equal_to_scored_to_1e-12": True}
    # ---- int8
    i8 = sorted(k for k in K if k.startswith("int8."))
    assert len(i8) == 20
    Rm = sum(K[k]["rate_per_s"] for k in i8) / len(i8)
    assert abs(Rm - sc["rules"]["E182-W-int8"]["mean_rate_per_s"]) < 1e-3
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
    J = C.joint_fit(krow, ky, trow, ty, tse)
    out["int8"] = {"form": "primary: two flip prices, joint WLS of 20 kinds-pass means (common sigma_K, iterated) and trains T1-T4 (own se)",
                   "params": named(PARAMS8, J["b"], J["cov"]), "names": PARAMS8, "b": J["b"], "cov": J["cov"],
                   "sigma_K_w": J["sigma_K"], "dof_K": J["dof_K"], "iterations": J["iterations"], "mean_rate_per_s": Rm,
                   "in_sample": {"kinds": {k: {"D_w": K[k]["D_w"], "fit_w": C.dot(r, J["b"]), "resid_w": e, "P10_w": K[k]["P_w"]}
                                           for k, r, e in zip(i8, krow, J["kinds_resid"])},
                                 "trains": {t: {"measured_w": y, "se_w": s, "fit_w": C.dot(r, J["b"]), "z": z}
                                            for t, r, y, s, z in zip(C.TRAINS8, trow, ty, tse, J["trains_z"])}}}
    # arm M12-1K: one price, the same joint fit
    krow1 = [C.int8_row_1k(K[k]["rate_per_s"], lm[k], pa[k], pb[k]) for k in i8]
    trow1 = []
    for t, (a, b) in C.TRAINS8.items():
        ra, rb = C.int8_row_1k(Rm, lm[a], pa[a], pb[a]), C.int8_row_1k(Rm, lm[b], pa[b], pb[b])
        trow1.append([x - y for x, y in zip(ra, rb)])
    J1 = C.joint_fit(krow1, ky, trow1, ty, tse)
    out["arm_1K"] = {"form": "one price for F_walk + F_scp, the same joint fit", "params": named(PARAMS8_1K, J1["b"], J1["cov"]),
                     "names": PARAMS8_1K, "b": J1["b"], "cov": J1["cov"], "sigma_K_w": J1["sigma_K"],
                     "trains_z": dict(zip(C.TRAINS8, J1["trains_z"]))}
    # arm M12-KO: one price on the kinds alone, betas fixed at E182-A and E182-B
    yko = [y - bA * r[2] - bB * r[3] for y, r in zip(ky, krow1)]
    Xko = [[r[0], r[1]] for r in krow1]
    bko, covu = C.wls(Xko, yko, [1.0] * len(Xko))
    rko = [y - C.dot(x, bko) for y, x in zip(yko, Xko)]
    s2ko = sum(e * e for e in rko) / (len(rko) - 2)
    covko = [[c * s2ko for c in row] for row in covu]
    out["arm_KO"] = {"form": "one price on the 20 kinds alone (OLS), beta_A and beta_B fixed at E182-A and E182-B",
                     "params": {"c8_w": {"value": bko[0], "se": math.sqrt(covko[0][0])}, "k_fJ": {"value": bko[1], "se": math.sqrt(covko[1][1])},
                                "beta_A_w": {"value": bA, "se": sc["rules"]["E182-A"]["beta_A"]["se"]},
                                "beta_B_w": {"value": bB, "se": sc["rules"]["E182-B"]["beta_B"]["se"]}},
                     "b": [bko[0], bko[1], bA, bB], "cov": [[covko[0][0], covko[0][1], 0, 0], [covko[1][0], covko[1][1], 0, 0],
                                                            [0, 0, sc["rules"]["E182-A"]["beta_A"]["se"] ** 2, 0], [0, 0, 0, sc["rules"]["E182-B"]["beta_B"]["se"] ** 2]],
                     "names": PARAMS8_1K, "resid_sd_w": math.sqrt(s2ko),
                     "T1_w": C.dot(trow1[0], [bko[0], bko[1], bA, bB])}
    # ---- fp32
    f32 = sorted(k for k in K if k.startswith("fp32."))
    assert len(f32) == 4
    frow = [C.float_row(fc[k]["popcount_a_word"], fc[k]["popcount_b_word"]) for k in f32]
    fy = [K[k]["D_w"] - K[k]["P_w"] for k in f32]
    fvar = [K[k]["sd_w"] ** 2 / K[k]["n"] for k in f32]
    trf, tyf, tvf = [], [], []
    for t, (a, b) in C.TRAINS32.items():
        trf.append([0.0, fc[a]["popcount_a_word"] - fc[b]["popcount_a_word"], fc[a]["popcount_b_word"] - fc[b]["popcount_b_word"]])
        line = 0.0 if t == "T5" else sc["rules"]["E182-H32T"]["lines_w"]["P"]
        assert t != "T5" or sc["rules"]["E182-F"]["forecast_every_arm"] == 0.0
        tyf.append(tr[t]["estimate"]["mean"] - line)
        tvf.append(tr[t]["estimate"]["se"] ** 2)
    bf, covf = C.wls(frow + trf, fy + tyf, fvar + tvf)
    out["float"] = {"form": "primary: c_f, gamma_A, gamma_B by WLS of the 4 fp32 kinds' D - P10 (each its pass sd^2 / n) and T5, T6 (minus "
                            "their committed P lines; own se^2)", "params": named(PARAMS_F, bf, covf), "names": PARAMS_F, "b": bf, "cov": covf,
                    "s_float_e182": sc["scale"]["s_float"],
                    "in_sample": {"kinds": {k: {"r_w": y, "fit_w": C.dot(r, bf), "resid_w": y - C.dot(r, bf)} for k, r, y in zip(f32, frow, fy)},
                                  "trains": {t: {"target_w": y, "se_w": math.sqrt(v), "fit_w": C.dot(r, bf), "z": (y - C.dot(r, bf)) / math.sqrt(v)}
                                             for t, r, y, v in zip(C.TRAINS32, trf, tyf, tvf)}},
                    "placement_w_per_bit": {"value": bf[2] - bf[1], "se": math.sqrt(covf[1][1] + covf[2][2] - 2 * covf[1][2])}}
    # arm M12-G: the float level as a gain on P10 (g_f in place of c_f)
    grow = [[K[k]["P_w"], fc[k]["popcount_a_word"], fc[k]["popcount_b_word"]] for k in f32]
    gy = [K[k]["D_w"] for k in f32]
    gtr = []
    for t, (a, b) in C.TRAINS32.items():
        line = 0.0 if t == "T5" else sc["rules"]["E182-H32T"]["lines_w"]["P"]
        gtr.append([line, fc[a]["popcount_a_word"] - fc[b]["popcount_a_word"], fc[a]["popcount_b_word"] - fc[b]["popcount_b_word"]])
    gty = [tr[t]["estimate"]["mean"] for t in C.TRAINS32]
    bg, covg = C.wls(grow + gtr, gy + gty, fvar + tvf)
    out["arm_G"] = {"form": "fp32 Df = g_f P10 + gamma_A pc_A + gamma_B pc_B, the same rows", "params": named(PARAMS_G, bg, covg),
                    "names": PARAMS_G, "b": bg, "cov": covg}
    # ---- M10-O and M10-G: M10's own levels with an offset or a gain, per format, on E182's kinds
    m10og = {}
    for fam, ks in (("int8", i8), ("fp32", f32)):
        d = [K[k]["D_w"] for k in ks]
        p = [K[k]["P_w"] for k in ks]
        m10og[fam] = {"c_w": sum(x - y for x, y in zip(d, p)) / len(ks), "g": sum(x * y for x, y in zip(d, p)) / sum(y * y for y in p), "n": len(ks)}
    m10og["fp16"] = {"from": "fp32"}
    out["arm_M10_OG"] = m10og
    # ---- arm M12-S1's E182 anchor (the int8 random anchor's D)
    out["arm_S1"] = {"form": "c8 moved by D(int8.full, session) - D(int8.full, E182); chosen after a look (REFIT.md section 6), reported only",
                     "D_int8_full_e182_w": red["items"]["int8.full"]["D"]["mean"]}
    # ---- carried, never applied
    eM = e184["arm_B"]["E184-M"]
    out["reported_candidate_not_applied"] = {
        "card1_sram_rail_over_reading": eM["implied_rail_over_reading"], "E184-M_f": eM["f"], "E184-M_verdict": eM["verdict"],
        "note": "E184 arm B's pooled factor, load-dependent (E184-M NOT RESOLVED); a candidate for card 1's SRAM rows, never applied by M12"}
    return out


def text(m):
    p8, pf = m["int8"]["params"], m["float"]["params"]
    L = ["M12 (Q157), fitted POST HOC on E182's committed rows only (fit_m12.py; REFIT.md section 3). aifoundry3, W over each format's zeros.",
         "",
         "int8 one-number tiles: D8 = c8 + R (k_walk F_walk + k_scp F_scp) + beta_A h_A + beta_B h_B   (joint WLS: 20 kinds + trains T1-T4)"]
    for n in m["int8"]["names"]:
        L.append(f"  {n:12s} {p8[n]['value']:+.6f}  (se {p8[n]['se']:.6f})")
    L.append(f"  sigma_K {m['int8']['sigma_K_w']:.4f} W on {m['int8']['dof_K']:.2f} effective dof, {m['int8']['iterations']} iterations; mean int8 rate "
             f"{m['int8']['mean_rate_per_s']:.6e} /s")
    L.append("  trains (measured, fit, z): " + "; ".join(f"{t} {v['measured_w']:+.4f} {v['fit_w']:+.4f} {v['z']:+.2f}" for t, v in m["int8"]["in_sample"]["trains"].items()))
    L.append("  kinds (D, fit, resid, M10's P):")
    for k, v in m["int8"]["in_sample"]["kinds"].items():
        L.append(f"    {k:22s} {v['D_w']:.4f} {v['fit_w']:.4f} {v['resid_w']:+.4f}   P10 {v['P10_w']:.4f}")
    a1 = m["arm_1K"]["params"]
    L.append("arm M12-1K (one price, joint): " + ", ".join(f"{n} {a1[n]['value']:+.6f} ({a1[n]['se']:.6f})" for n in m["arm_1K"]["names"])
             + "; trains z " + ", ".join(f"{t} {z:+.2f}" for t, z in m["arm_1K"]["trains_z"].items()))
    ak = m["arm_KO"]["params"]
    L.append(f"arm M12-KO (one price, kinds alone, betas fixed): c8 {ak['c8_w']['value']:+.4f} ({ak['c8_w']['se']:.4f}), k {ak['k_fJ']['value']:.3f} fJ "
             f"({ak['k_fJ']['se']:.3f}), resid sd {m['arm_KO']['resid_sd_w']:.4f} W; its T1 {m['arm_KO']['T1_w']:+.4f} W")
    L.append("")
    L.append("float held-word tiles: Df = P10 + c_f + gamma_A pc_A + gamma_B pc_B   (WLS: 4 fp32 kinds + T5, T6)")
    for n in m["float"]["names"]:
        L.append(f"  {n:12s} {pf[n]['value']:+.6f}  (se {pf[n]['se']:.6f})")
    pl = m["float"]["placement_w_per_bit"]
    L.append(f"  placement gamma_B - gamma_A {pl['value']:+.6f} W a held bit (se {pl['se']:.6f})")
    L.append("  kinds (D - P10, fit, resid): " + "; ".join(f"{k} {v['r_w']:+.4f} {v['fit_w']:+.4f} {v['resid_w']:+.4f}" for k, v in m["float"]["in_sample"]["kinds"].items()))
    L.append("  trains (target, fit, z): " + "; ".join(f"{t} {v['target_w']:+.4f} {v['fit_w']:+.4f} {v['z']:+.2f}" for t, v in m["float"]["in_sample"]["trains"].items()))
    ag = m["arm_G"]["params"]
    L.append("arm M12-G (gain): " + ", ".join(f"{n} {ag[n]['value']:+.6f} ({ag[n]['se']:.6f})" for n in m["arm_G"]["names"]))
    L.append("arms M10-O / M10-G on E182's kinds: " + "; ".join(f"{f} c {v['c_w']:+.4f} W, g {v['g']:.5f} (n {v['n']})" for f, v in m["arm_M10_OG"].items() if "c_w" in v))
    L.append(f"arm M12-S1: E182's D(int8.full) {m['arm_S1']['D_int8_full_e182_w']:.4f} W")
    r = m["reported_candidate_not_applied"]
    L.append(f"reported candidate, never applied: card 1's SRAM rail carries {r['card1_sram_rail_over_reading']} x its reading (E184-M {r['E184-M_verdict']}, f {r['E184-M_f']})")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    here = os.path.join(root, "tools/claims-v3/m12")
    m = build(root)
    js = json.dumps(m, indent=1, sort_keys=True) + "\n"
    tx = text(m)
    if a.check:
        ok = open(os.path.join(here, "m12.json")).read() == js and open(os.path.join(here, "fit-m12.txt")).read() == tx
        print("CHECK PASS" if ok else "CHECK FAIL")
        return 0 if ok else 1
    open(os.path.join(here, "m12.json"), "w").write(js)
    open(os.path.join(here, "fit-m12.txt"), "w").write(tx)
    print(tx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
