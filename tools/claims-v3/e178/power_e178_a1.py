#!/usr/bin/env python3
"""E178 dated note A1 (Q146 fix pass): the rule power the verifier's faults touch, re-run before any kit or datum.

    python3 -B power_e178_a1.py --root <lab repo root>           # writes tools/claims-v3/e178/power-e178-a1.json and .txt
    python3 -B power_e178_a1.py --root <lab repo root> --check   # recomputes in memory, compares both files byte for byte

Reads only committed files: tools/claims-v3/e178/forecast-e178.json, power-e178.json and power_e178.py (imported: its spearman,
couple_rule, T975 and RHO_CRIT), and M10's held-out rows (docs/reports/data/2026-11-04-q142m-m10/rows-m10.json, read for the
post hoc block (F) only). No E178 datum exists; nothing is fitted. The noise model is E178.md section 6's, unchanged: sigma1
0.125 W (0.10 and 0.20 beside), the per-pass sd of a same-session difference of two one-number kinds' single reads; a kind's
single read sigma1/sqrt(2); a core couple's per-pass value sigma1/sqrt(3) with a 0.02 W couple term; a 0.041 W session term
per kind for kinds compared across a pass.

  (H0) harness: this file's couple_full and power_e178.couple_rule reproduce power-e178.json's E178-H-int8 and E178-U figures
       with their own seeds; (X)'s registered rows reproduce its E178-R-int8, E178-W-int8 and E178-E figures.
  (S)  E178-S-int8, registered by A1: x_p = D(int8.e178_v85) - D(int8.neg_ones) in each kept pass. Each kind is one single read
       a pass in the plan, so x_p = truth + (o_85 - o_neg) + N(0, sigma1), o ~ N(0, 0.041) per kind and session; t interval.
       Beside it, reported only: 127 - neg_ones.
  (A)  What R-int8, H-int8 and W-int8 read if the truth is an operand-bit model (the A and B words' 1-bits, or their 0-bits)
       instead of P, scaled to P's spread or to the committed bridge (neg_ones - ones).
  (B)  E178-H-int8 if the card prices the int8 bus flips at a fraction f of M10's bus price; one session and two.
  (D)  E178-H-int8 at n 4, 3, 2 and sigma1 0.10 / 0.125 / 0.20 (power-e178.json's figures, quoted), and with a larger couple term.
  (U)  E178-U: the shares of sessions whose interval holds dP, dF, both, or only the true one: F's SIZE coverage, which
       power_e178.py never counted (its line 89, `inF += (abs((truth) - dF) <= hw) if False else 0`, adds 0).
  (X)  R-int8, W-int8 and E178-E with each core kind's se as its three reads a pass give it (sigma1/sqrt(6), where
       power_e178.py used sigma1/sqrt(3)), fp32.ones and fp32.e178_v4 both core in E-fp32; the same seeds as the frozen rows.
  (G)  The equal-flip groups' spreads in (i) and in P.
  (F)  Post hoc: M10's held-out errors on the committed int8 one-number rows, and M10's bus term for them.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
DRAWS = 20000
SYS_KIND = 0.041
SYS_COUPLE = 0.02
PW = None
T975 = None


def couple_full(rng, delta_true, n, sigma1, sys_sd):
    """power_e178.couple_rule's draws, in its order, returning the mean and the half-width."""
    off = rng.gauss(0, sys_sd)
    xs = [delta_true + off + rng.gauss(0, sigma1 / math.sqrt(3)) for _ in range(n)]
    return statistics.mean(xs), T975[n - 1] * statistics.stdev(xs) / math.sqrt(n)


def couple_sessions(rng, delta_true, n_per, sessions, sigma1, sys_sd):
    """A couple read over sessions of n_per passes each, each session with its own couple term, as one interval."""
    xs = []
    for _ in range(sessions):
        off = rng.gauss(0, sys_sd)
        xs += [delta_true + off + rng.gauss(0, sigma1 / math.sqrt(3)) for _ in range(n_per)]
    n = len(xs)
    return statistics.mean(xs), T975[n - 1] * statistics.stdev(xs) / math.sqrt(n)


def pair_full(rng, delta_true, n, sigma1, sys_kind):
    """E178-S-int8's draw: two kinds, one single read each a pass, each kind with its own session term."""
    off = rng.gauss(0, sys_kind) - rng.gauss(0, sys_kind)
    xs = [delta_true + off + rng.gauss(0, sigma1) for _ in range(n)]
    return statistics.mean(xs), T975[n - 1] * statistics.stdev(xs) / math.sqrt(n)


def interval_shares(draw, rng, dP, dF):
    pos = neg = inP = inF = both = 0
    hws = []
    for _ in range(DRAWS):
        m, hw = draw(rng)
        lo, hi = m - hw, m + hw
        pos += lo > 0
        neg += hi < 0
        a, b = lo <= dP <= hi, lo <= dF <= hi
        inP += a
        inF += b
        both += a and b
        hws.append(hw)
    return {"p_positive": pos / DRAWS, "p_negative": neg / DRAWS, "p_not_resolved": 1 - (pos + neg) / DRAWS,
            "p_dP_inside": inP / DRAWS, "p_dF_inside": inF / DRAWS, "p_both_inside": both / DRAWS,
            "median_halfwidth_w": statistics.median(hws)}


def meas_int8(rng, mu, i8, n, s1, model_sd, core_se):
    """One session's int8 D's in power_e178.py's R and W form (its draw order); core_se(s1) is a core kind's per-pass se."""
    out = []
    for k in i8:
        se = (core_se(s1) if k in ("int8.e178_v4", "int8.e178_v5") else s1 / math.sqrt(2)) / math.sqrt(n)
        out.append(mu[k] + rng.gauss(0, model_sd) + rng.gauss(0, SYS_KIND) + rng.gauss(0, se))
    return out


def slope_hw(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    resid = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
    return b, PW.T975[11] * math.sqrt(sum(r * r for r in resid) / (len(xs) - 2) / sxx)


def e_rule(se, rng_null, rng_det, deltas):
    null = sorted(max(v) - min(v) for v in ([rng_null.gauss(0, math.sqrt(s * s + SYS_KIND ** 2)) for s in se] for _ in range(DRAWS)))
    crit = null[int(0.95 * DRAWS)]
    det = {}
    for delta in deltas:
        rng2 = rng_det()
        hit = 0
        for _ in range(DRAWS):
            v = [rng2.gauss(0, math.sqrt(s * s + SYS_KIND ** 2)) for s in se]
            v[0] += delta
            hit += (max(v) - min(v)) > crit
        det[f"p_detect_{delta}"] = hit / DRAWS
    return crit, det


def main():
    global PW, T975
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    D = os.path.join(root, "tools/claims-v3/e178")
    sys.path.insert(0, D)
    import power_e178  # noqa: E402  (the registered noise model's functions, unchanged)
    PW = power_e178
    T975 = dict(PW.T975)
    T975[7] = 2.365
    fc = json.load(open(os.path.join(D, "forecast-e178.json")))
    fz = json.load(open(os.path.join(D, "power-e178.json")))
    ks = fc["kinds"]
    rate8 = fc["rate"]["int8"]

    def Pa(k):
        return ks[k]["P_w"]["a3"]

    def Fa(k):
        return ks[k]["F_w"]["a3"]

    out = {"_what": "E178 dated note A1: the rule power the verifier's faults touch (power_e178_a1.py)", "draws": DRAWS}
    L = ["E178 dated note A1: the power the verifier's faults touch (power_e178_a1.py). 20,000 draws a case; E178.md section 6's",
         "noise model; aifoundry3's frozen forecasts; no E178 datum exists.", ""]

    # (H0) harness check against the frozen file
    chk = {}
    for rule, a_, b_, idx in (("E178-H-int8", "int8.e178_v5", "int8.e178_v4", 3), ("E178-U", "fp32.ones", "fp32.e178_uf", 4)):
        dP = Pa(a_) - Pa(b_)
        reg = [c for c in fz["rules"][rule]["cases"] if c["n"] == 4 and c["sigma1"] == 0.125 and c["truth"] == "P true"][0]
        rng = random.Random(17800 + idx)
        pos1 = sum(PW.couple_rule(rng, dP, dP, 4, 0.125, SYS_COUPLE)[0] for _ in range(DRAWS)) / DRAWS
        rng = random.Random(17800 + idx)
        hits = 0
        for _ in range(DRAWS):
            m, hw = couple_full(rng, dP, 4, 0.125, SYS_COUPLE)
            hits += m - hw > 0
        chk[rule] = {"frozen": reg["p_resolved_positive"], "couple_rule": pos1, "couple_full": hits / DRAWS,
                     "equal": reg["p_resolved_positive"] == pos1 == hits / DRAWS}
    out["H0_harness"] = chk
    L.append("(H0) Harness, P true, n 4, sigma1 0.125, POSITIVE: " + "; ".join(
        f"{r} frozen {v['frozen']:.4f}, couple_rule {v['couple_rule']:.4f}, couple_full {v['couple_full']:.4f} "
        f"({'EQUAL' if v['equal'] else 'DIFFER'})" for r, v in chk.items()))
    L.append("")

    # the int8 set and the operand-bit alternatives
    i8 = sorted(k for k in ks if ks[k]["type"] == "int8")
    P8 = [Pa(k) for k in i8]
    pcAB = {k: ks[k]["popcount_a_word"] + ks[k]["popcount_b_word"] for k in i8}
    zcAB = {k: 64 - pcAB[k] for k in i8}
    span_P = max(P8) - min(P8)
    beta = {"ones_span": span_P / (max(pcAB.values()) - min(pcAB.values())),
            "ones_bridge": (Pa("int8.neg_ones") - Pa("int8.ones")) / (pcAB["int8.neg_ones"] - pcAB["int8.ones"]),
            "zeros_span": span_P / (max(zcAB.values()) - min(zcAB.values()))}
    base = min(P8)
    T_ONES_SPAN = "1-bits of the A and B words, at P's spread"
    T_ONES_BRIDGE = "1-bits of the A and B words, at the bridge's size"
    T_ZEROS_SPAN = "0-bits of the A and B words, at P's spread"
    truths = {"P": {k: Pa(k) for k in i8},
              T_ONES_SPAN: {k: base + beta["ones_span"] * (pcAB[k] - min(pcAB.values())) for k in i8},
              T_ONES_BRIDGE: {k: base + beta["ones_bridge"] * (pcAB[k] - min(pcAB.values())) for k in i8},
              T_ZEROS_SPAN: {k: base + beta["zeros_span"] * (zcAB[k] - min(zcAB.values())) for k in i8},
              "flat": {k: 1.8 for k in i8}}
    fl8 = [ks[k]["flips_i"]["launch_mean"]["total"] for k in i8]
    out["operand_bits"] = {"kinds": i8, "popcount_a_plus_b_words": pcAB, "beta_w_per_bit": beta,
                           "spearman_P_vs_1bits": PW.spearman(P8, [pcAB[k] for k in i8]),
                           "spearman_flips_vs_1bits": PW.spearman(fl8, [pcAB[k] for k in i8]),
                           "spearman_P_vs_0bits": PW.spearman(P8, [zcAB[k] for k in i8])}
    ob = out["operand_bits"]
    L.append(f"Operand bits, int8 (the A word's and B word's 1-bits): Spearman against P {ob['spearman_P_vs_1bits']:+.3f}, against (i)'s "
             f"flips {ob['spearman_flips_vs_1bits']:+.3f}; the 0-bit count against P {ob['spearman_P_vs_0bits']:+.3f}.")
    L.append(f"A bit's price in each alternative truth: 1-bits at P's spread {beta['ones_span'] * 1e3:.3f} mW, 1-bits at the bridge's size "
             f"{beta['ones_bridge'] * 1e3:.3f} mW, 0-bits at P's spread {beta['zeros_span'] * 1e3:.3f} mW.")
    L.append("")

    # (S) E178-S-int8, and 127 - neg_ones beside it
    S = {}
    grid = [(4, 0.125), (3, 0.125), (2, 0.125), (4, 0.10), (4, 0.20)]
    for name, x, y in (("E178-S-int8", "int8.e178_v85", "int8.neg_ones"), ("beside: 127 - neg_ones", "int8.e178_v127", "int8.neg_ones")):
        dP, dF = Pa(x) - Pa(y), Fa(x) - Fa(y)
        dpc = pcAB[x] - pcAB[y]
        tr = {"P": dP, "F": dF, "null": 0.0}
        for tn in (T_ONES_SPAN, T_ONES_BRIDGE, T_ZEROS_SPAN):
            tr[tn] = truths[tn][x] - truths[tn][y]
        tr["P plus 1-bits at the bridge's size"] = dP + beta["ones_bridge"] * dpc
        tr["P plus 1-bits at P's spread"] = dP + beta["ones_span"] * dpc
        res = {"a": x, "b": y, "dP_w": dP, "dF_w": dF, "d_1bits_a_plus_b": dpc, "truths_w": tr, "cases": []}
        for tn, tv in tr.items():
            if tn.startswith("P plus"):
                pts = [(4, 0.125)]
            elif tn in ("P", "F", "null"):
                pts = grid
            else:
                pts = grid[:3]
            for n, s1 in pts:
                rng = random.Random(f"E178-A1|{name}|{tn}|{n}|{s1}")
                sh = interval_shares(lambda r: pair_full(r, tv, n, s1, SYS_KIND), rng, dP, dF)
                res["cases"].append({"truth": tn, "truth_w": tv, "n": n, "sigma1": s1, **sh})
        S[name] = res
        L.append(f"(S) {name}: {x} - {y}: dP {dP:+.4f} W, dF {dF:+.4f} W; the A and B words' 1-bits {dpc:+d}")
        for c in res["cases"]:
            L.append(f"    truth {c['truth']} ({c['truth_w']:+.4f} W), n {c['n']}, sigma1 {c['sigma1']}: POSITIVE {c['p_positive']:.3f}, "
                     f"NEGATIVE {c['p_negative']:.3f}, dP inside {c['p_dP_inside']:.3f}, dF inside {c['p_dF_inside']:.3f}, "
                     f"half-width {c['median_halfwidth_w']:.3f} W")
    out["S"] = S
    L.append("")

    # (A) R-int8, H-int8 and W-int8 under the alternatives (power_e178.py's se form, model error 0)
    mx = statistics.mean(fl8)
    sxx = sum((v - mx) ** 2 for v in fl8)
    bP = sum((v - mx) * (p - statistics.mean(P8)) for v, p in zip(fl8, P8)) / sxx
    dPh = Pa("int8.e178_v5") - Pa("int8.e178_v4")
    A = {"slope_P_w_per_flip": bP, "slope_P_fJ_per_flip": bP / rate8 * 1e15, "cases": []}
    for tn, tv in truths.items():
        for n in (4, 3):
            rng = random.Random(f"E178-A1|A|R|{tn}|{n}")
            rp = 0
            for _ in range(DRAWS):
                rp += PW.spearman(P8, meas_int8(rng, tv, i8, n, 0.125, 0.0, lambda s: s / math.sqrt(3))) >= PW.RHO_CRIT
            rng = random.Random(f"E178-A1|A|W|{tn}|{n}")
            wi = wl = wh = 0
            for _ in range(DRAWS):
                b, hw = slope_hw(fl8, meas_int8(rng, tv, i8, n, 0.125, 0.0, lambda s: s / math.sqrt(3)))
                wi += abs(b - bP) <= hw
                wl += b < bP - hw
                wh += b > bP + hw
            rng = random.Random(f"E178-A1|A|H|{tn}|{n}")
            dth = tv["int8.e178_v5"] - tv["int8.e178_v4"]
            hp = hn = hs = 0
            for _ in range(DRAWS):
                m, hw = couple_full(rng, dth, n, 0.125, SYS_COUPLE)
                hp += m - hw > 0
                hn += m + hw < 0
                hs += m - hw <= dPh <= m + hw
            A["cases"].append({"truth": tn, "n": n, "sigma1": 0.125, "R_int8_PASS": rp / DRAWS, "W_int8_PASS": wi / DRAWS,
                               "W_int8_FAIL_LOW": wl / DRAWS, "W_int8_FAIL_HIGH": wh / DRAWS, "H_int8_truth_w": dth,
                               "H_int8_POSITIVE": hp / DRAWS, "H_int8_NEGATIVE": hn / DRAWS, "H_int8_SIZE_PASS": hs / DRAWS})
    out["A_rules_under_alternatives"] = A
    L.append(f"(A) The int8 rules if the truth is not P (sigma1 0.125, model error 0, power_e178.py's se form). P's slope "
             f"{A['slope_P_fJ_per_flip']:.3f} fJ a flip; S-int8's shares under the same truths are in (S).")
    for c in A["cases"]:
        L.append(f"    {c['truth']}, n {c['n']}: R-int8 PASS {c['R_int8_PASS']:.3f}; H-int8 ({c['H_int8_truth_w']:+.4f} W) POSITIVE "
                 f"{c['H_int8_POSITIVE']:.3f}, NEGATIVE {c['H_int8_NEGATIVE']:.3f}, SIZE PASS {c['H_int8_SIZE_PASS']:.3f}; W-int8 PASS "
                 f"{c['W_int8_PASS']:.3f} (FAIL LOW {c['W_int8_FAIL_LOW']:.3f}, HIGH {c['W_int8_FAIL_HIGH']:.3f})")
    L.append("")

    # (B) H-int8 at a fraction f of M10's bus price
    t4, t5 = ks["int8.e178_v4"]["m10_terms_w_a3"], ks["int8.e178_v5"]["m10_terms_w_a3"]
    d_bus = t5["bus"] - t4["bus"]
    d_rest = sum(t5[q] - t4[q] for q in t5 if q != "bus")
    B = {"d_bus_w": d_bus, "d_other_terms_w": d_rest, "bus_share_of_dP": d_bus / dPh, "cases": []}
    for f in (1.0, 0.5, 0.25, 0.0):
        tv = d_rest + f * d_bus
        for sessions in (1, 2):
            rng = random.Random(f"E178-A1|B|{f}|{sessions}")
            pos = size = 0
            for _ in range(DRAWS):
                m, hw = couple_sessions(rng, tv, 4, sessions, 0.125, SYS_COUPLE)
                pos += m - hw > 0
                size += m - hw <= dPh <= m + hw
            B["cases"].append({"f": f, "truth_w": tv, "sessions_of_4": sessions, "p_positive": pos / DRAWS, "p_dP_inside": size / DRAWS})
    out["B_H_int8_at_a_lower_bus_price"] = B
    L.append(f"(B) E178-H-int8 if the card prices int8 bus flips at f x M10's price: M10's bus term is {d_bus:+.4f} W of dP {dPh:+.4f} W "
             f"({100 * d_bus / dPh:.1f}%); the other terms {d_rest:+.4f} W. One interval over all passes; each session its own couple term.")
    for c in B["cases"]:
        L.append(f"    f {c['f']:.2f} (truth {c['truth_w']:+.4f} W), {c['sessions_of_4']} session(s) of 4 passes: POSITIVE {c['p_positive']:.3f}, "
                 f"dP inside {c['p_dP_inside']:.3f}")
    L.append("")

    # (D) H-int8 at fewer passes and more noise
    Dd = {"frozen_P_true_positive": {}, "couple_term": []}
    for c in fz["rules"]["E178-H-int8"]["cases"]:
        if c["truth"] == "P true":
            Dd["frozen_P_true_positive"][f"n {c['n']}, sigma1 {c['sigma1']}"] = c["p_resolved_positive"]
    for st in (0.02, 0.041, 0.066):
        for n in (4, 3):
            rng = random.Random(f"E178-A1|D|{st}|{n}")
            pos = 0
            for _ in range(DRAWS):
                m, hw = couple_full(rng, dPh, n, 0.125, st)
                pos += m - hw > 0
            Dd["couple_term"].append({"couple_term_w": st, "n": n, "p_positive": pos / DRAWS})
    out["D_H_int8_passes_and_noise"] = Dd
    L.append("(D) E178-H-int8 POSITIVE if P is right (power-e178.json): " + "; ".join(f"{k} {v:.3f}" for k, v in Dd["frozen_P_true_positive"].items()))
    L.append("    with a larger couple term, sigma1 0.125: " + "; ".join(f"{c['couple_term_w']} W n {c['n']} {c['p_positive']:.3f}"
                                                                    for c in Dd["couple_term"]))
    L.append("")

    # (U) E178-U: P against F; F's SIZE coverage. At n 4 / sigma1 0.125 the frozen seed 17804, so P's shares equal power-e178.json's.
    dPu, dFu = Pa("fp32.ones") - Pa("fp32.e178_uf"), Fa("fp32.ones") - Fa("fp32.e178_uf")
    U = {"dP_w": dPu, "dF_w": dFu, "cases": []}
    for tn, tv in (("P true", dPu), ("F true", dFu), ("null", 0.0)):
        for n, s1 in grid:
            rng = random.Random(17804) if (n, s1) == (4, 0.125) else random.Random(f"E178-A1|U|{tn}|{n}|{s1}")
            sh = interval_shares(lambda r: couple_full(r, tv, n, s1, SYS_COUPLE), rng, dPu, dFu)
            true_in = sh["p_dP_inside"] if tn == "P true" else sh["p_dF_inside"] if tn == "F true" else None
            sh["p_only_the_true_one_inside"] = (true_in - sh["p_both_inside"]) if true_in is not None else None
            if (n, s1) == (4, 0.125):
                reg = [c for c in fz["rules"]["E178-U"]["cases"] if c["n"] == 4 and c["sigma1"] == 0.125 and c["truth"] == tn][0]
                sh["frozen_equal"] = (reg["p_resolved_positive"] == sh["p_positive"] and reg["p_dP_inside"] == sh["p_dP_inside"])
            U["cases"].append({"truth": tn, "n": n, "sigma1": s1, **sh})
    out["U"] = U
    L.append(f"(U) E178-U: dP {dPu:+.4f} W, dF {dFu:+.4f} W, |dF - dP| {abs(dFu - dPu):.4f} W")
    for c in U["cases"]:
        only = f", only the true one {c['p_only_the_true_one_inside']:.3f}" if c["p_only_the_true_one_inside"] is not None else ""
        fe = f" [power-e178.json's POSITIVE and dP-inside {'EQUAL' if c['frozen_equal'] else 'DIFFER'}]" if "frozen_equal" in c else ""
        L.append(f"    {c['truth']}, n {c['n']}, sigma1 {c['sigma1']}: POSITIVE {c['p_positive']:.3f}; dP inside {c['p_dP_inside']:.3f}, "
                 f"dF inside {c['p_dF_inside']:.3f}, both {c['p_both_inside']:.3f}{only}; half-width {c['median_halfwidth_w']:.3f} W{fe}")
    L.append("")

    # (X) the exact se of a core kind, with the frozen seeds (R 17805, W 17806, E 17807 / 17907)
    X = {"R": [], "W": [], "E": []}
    se_rules = (("registered", lambda s: s / math.sqrt(3)), ("exact", lambda s: s / math.sqrt(6)))
    for lab, rule in se_rules:
        for msd in (0.0, 0.03):
            rng = random.Random(17805)
            rp = 0
            for _ in range(DRAWS):
                rp += PW.spearman(P8, meas_int8(rng, truths["P"], i8, 4, 0.125, msd, rule)) >= PW.RHO_CRIT
            row = {"se": lab, "model_sd": msd, "n": 4, "R_int8_PASS": rp / DRAWS}
            if lab == "registered":
                reg = [c for c in fz["rules"]["E178-R-int8"]["cases"] if c["n"] == 4 and c["sigma1"] == 0.125 and c["model_sd"] == msd
                       and c["truth"] == "P"][0]
                row["frozen_equal"] = reg["p_pass"] == row["R_int8_PASS"]
            X["R"].append(row)
            rng = random.Random(17806)
            wi = 0
            hws = []
            for _ in range(DRAWS):
                b, hw = slope_hw(fl8, meas_int8(rng, truths["P"], i8, 4, 0.125, msd, rule))
                wi += abs(b - bP) <= hw
                hws.append(hw / rate8 * 1e15)
            row = {"se": lab, "model_sd": msd, "n": 4, "W_P_inside": wi / DRAWS, "W_median_halfwidth_fJ": statistics.median(hws)}
            if lab == "registered":
                reg = [c for c in fz["rules"]["E178-W-int8"]["cases"] if c["n"] == 4 and c["sigma1"] == 0.125 and c["model_sd"] == msd][0]
                row["frozen_equal"] = reg["p_P_slope_inside"] == row["W_P_inside"]
            X["W"].append(row)
    groups = fz["rules"]["E178-E"]["groups"]
    core_reg = {"int8.e178_v4", "int8.e178_v5", "fp32.e178_v4", "fp16.e178_v4"}
    core_all = {"int8.e178_v4", "int8.e178_v5", "fp32.e178_v4", "fp32.e178_v5", "fp16.e178_v4", "fp16.e178_v5", "fp32.ones", "fp32.e178_uf"}
    for g, mem in groups.items():
        for lab in ("registered", "exact"):
            s1, n = 0.125, 4
            if lab == "registered":
                se = [(s1 / math.sqrt(3) if m in core_reg else s1 / math.sqrt(2)) / math.sqrt(n) for m in mem]
            else:
                se = [(s1 / math.sqrt(6) if m in core_all else s1 / math.sqrt(2)) / math.sqrt(n) for m in mem]
            crit, det = e_rule(se, random.Random(17807), lambda: random.Random(17907), (0.05, 0.10))
            row = {"group": g, "se": lab, "n": n, "crit_spread_w": crit, **det}
            if lab == "registered":
                regs = [c for c in fz["rules"]["E178-E"]["cases"] if c["group"] == g and c["n"] == 4]
                row["frozen_equal"] = all(abs(c["crit_spread_w"] - crit) == 0 and c["p_detect"] == det[f"p_detect_{c['delta_w']}"] for c in regs)
            X["E"].append(row)
    out["X_exact_core_se"] = X
    L.append("(X) A core kind's se as three reads a pass give it (n 4, sigma1 0.125; the frozen seeds, so 'registered' rows reproduce "
             "power-e178.json):")
    for c in X["R"]:
        L.append(f"    E178-R-int8, {c['se']} se, model error {c['model_sd']}: PASS {c['R_int8_PASS']:.4f}"
                 + (f" [power-e178.json {'EQUAL' if c['frozen_equal'] else 'DIFFER'}]" if "frozen_equal" in c else ""))
    for c in X["W"]:
        L.append(f"    E178-W-int8, {c['se']} se, model error {c['model_sd']}: P's slope inside {c['W_P_inside']:.4f}, half-width "
                 f"{c['W_median_halfwidth_fJ']:.2f} fJ" + (f" [power-e178.json {'EQUAL' if c['frozen_equal'] else 'DIFFER'}]" if "frozen_equal" in c else ""))
    for c in X["E"]:
        L.append(f"    E178-E-{c['group']}, {c['se']} se: equal reads PASS below {c['crit_spread_w']:.3f} W; one kind 0.05 W off caught "
                 f"{c['p_detect_0.05']:.3f}, 0.10 W off {c['p_detect_0.1']:.3f}"
                 + (f" [power-e178.json {'EQUAL' if c['frozen_equal'] else 'DIFFER'}]" if "frozen_equal" in c else ""))
    L.append("")

    # (G) the equal-flip groups
    G = {}
    for g, mem in groups.items():
        tot = [ks[k]["flips_i"]["launch_mean"]["total"] for k in mem]
        cst = [ks[k]["flips_i"]["launch_mean"]["c_store"] for k in mem]
        pw = [Pa(k) for k in mem]
        G[g] = {"members": mem, "flips_total_min": min(tot), "flips_total_max": max(tot), "flips_spread_rel": (max(tot) - min(tot)) / max(tot),
                "c_store_min": min(cst), "c_store_max": max(cst), "P_spread_w": max(pw) - min(pw),
                "popcount_a_word": [ks[k]["popcount_a_word"] for k in mem]}
    out["G_equal_flip_groups"] = G
    L.append("(G) E178-E's groups: " + "; ".join(
        f"{g}: (i) {v['flips_total_min']:,.0f}-{v['flips_total_max']:,.0f} flips an op ({100 * v['flips_spread_rel']:.2f}% apart), "
        f"accumulator storage {v['c_store_min']:,.0f}-{v['c_store_max']:,.0f}, P spread {v['P_spread_w']:.4f} W" for g, v in G.items()))
    L.append("")

    # (F) post hoc: M10's held-out errors on the committed int8 one-number rows, and its bus term for them
    rows = json.load(open(os.path.join(root, "docs/reports/data/2026-11-04-q142m-m10/rows-m10.json")))
    Fp = {"label": "post hoc: read after M10's fit and before any E178 datum; never a verdict", "rows": [], "bus_term_w_a3": {}}
    for r in rows:
        if r["type"] == "int8" and r["key"] in ("int8.ones", "int8.neg_ones"):
            Fp["rows"].append({"exp": r["exp"], "card": r["card"], "key": r["key"], "D_w": r["D"], "err_w_B": r["err_w"]["B"]})
    Fp["rows"].sort(key=lambda r: (r["key"], r["exp"]))
    for k in ("int8.ones", "int8.neg_ones", "int8.e178_v4", "int8.e178_v5"):
        Fp["bus_term_w_a3"][k] = ks[k]["m10_terms_w_a3"]["bus"]
    out["F_posthoc_m10_int8_one_number"] = Fp
    L.append("(F) Post hoc: M10's held-out error (measured - predicted, rows-m10.json err_w B) on the committed int8 one-number rows: "
             + "; ".join(f"{r['key']} {r['exp']} ({r['card']}) {r['err_w_B']:+.3f} W" for r in Fp["rows"]))
    L.append("    M10's bus term at aifoundry3's rate: " + "; ".join(f"{k} {v:.4f} W" for k, v in Fp["bus_term_w_a3"].items()))

    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    txt = "\n".join(L) + "\n"
    pj, pt = os.path.join(D, "power-e178-a1.json"), os.path.join(D, "power-e178-a1.txt")
    if a.check:
        same = open(pj).read() == js and open(pt).read() == txt
        print("CHECK", "PASS" if same else "FAIL")
        return 0 if same else 1
    open(pj, "w").write(js)
    open(pt, "w").write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
