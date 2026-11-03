#!/usr/bin/env python3
"""E155, corrections after verification (Tue 3 Nov 2026; post hoc, deciding nothing): every number the dated corrections in README.md quote, each
printed with its inputs, from committed files only. It changes no frozen file and no registered verdict.

    python3 docs/reports/data/2026-11-03-e155-int8-floor-rows/corrections-numbers.py      # from anywhere; standard library only

Writes corrections-numbers.txt and corrections-numbers.json beside itself.

C2  F1's margins in every arm, unrounded and to three decimals: D31's 95% interval against each frozen band (the registered rule is overlap), and
    D31's point against the toggle count's band.
C1  The bands on the premise's own footing. The registration adds the shared per-op term E_op x (rate(int8) - rate(fp32)) at three rows (the
    premise: equal per-op energy in the two formats), but its readings Wn, Wt and T scale ALL of E148's sixteen-row N - N1, which under the same
    premise already holds E_op x (rate(m0.int8) - rate(m0.fp32)) (int8 318 cycles an op there, fp32 544; at one row both run 62, so N1 holds none).
    Here that term is removed from each E148 pass with that pass's own E_op (the registration's E_op construction) and the bands rebuilt (a) by the
    registration's interval rule and (b) paired per E148 pass; each reading's status, F1a and F1b by the registered scorer's logic, in every arm;
    the errors of D31 and N3 on that footing; F3's frozen allowance on that footing; and E148's own two-row check (its posthoc section 1) on the
    same footing.
C1  One-term prices on matched footings: E148's sixteen-row prices with its shared term removed (at its own E_op and at this session's) against
    E155's three-row prices (less the frozen and the session's shared term).
C3  Q31k: how much of it is B's add-back, its interval against the frozen walk parts, and those parts on the premise's footing.
C4  N3's and D31's out-of-sample errors with their intervals.
C5  R6's frozen cycles as the bench's plus E109's one constant.
SPDX-License-Identifier: Apache-2.0"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
E148D = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e148-int8-excess")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201}
ARMS = (("primary", "scored.json"), ("dips kept", "scored-dipskept.json"), ("leakage auto", "scored-auto.json"),
        ("relaxed", "scored-relaxed.json"))


def ci(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n}


def gap(alo, ahi, blo, bhi):
    """0 if [alo, ahi] and [blo, bhi] overlap, else the distance between their facing ends."""
    if blo > ahi:
        return blo - ahi
    if alo > bhi:
        return alo - bhi
    return 0.0


def f1(d, bands):
    """The registered scorer's F1a/F1b logic (tools/claims-v3/e155/score_e155.py, score()) on any set of bands."""
    cons = {k: ("CONSISTENT" if gap(d["lo"], d["hi"], b[0], b[1]) == 0.0 else "EXCLUDED") for k, b in bands.items()}
    walk = cons["Wn"] == "CONSISTENT" or cons["Wt"] == "CONSISTENT"
    if walk and cons["C"] == "EXCLUDED":
        a = "WALK"
    elif cons["C"] == "CONSISTENT" and not walk:
        a = "PER-CYCLE"
    elif not walk and cons["C"] == "EXCLUDED":
        a = "NEITHER"
    else:
        a = "INCONCLUSIVE"
    if cons["Wt"] == "CONSISTENT" and cons["Wn"] == "EXCLUDED":
        b = "TOGGLES"
    elif cons["Wn"] == "CONSISTENT" and cons["Wt"] == "EXCLUDED":
        b = "NEW-ADDRESS"
    elif cons["Wn"] == "EXCLUDED" and cons["Wt"] == "EXCLUDED":
        b = "NEITHER"
    else:
        b = "INCONCLUSIVE (both counts consistent)"
    return cons, a, b


def main():
    P = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e155", "predictions-e155.json")))
    B = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e155", "desk", "bench-e155.json")))
    SC = {arm: json.load(open(os.path.join(HERE, fn))) for arm, fn in ARMS}
    PH = json.load(open(os.path.join(HERE, "posthoc", "posthoc.json")))
    E = json.load(open(os.path.join(E148D, "e148.json")))
    out, L = {}, ["E155 corrections after verification (post hoc, deciding nothing; Tue 3 Nov 2026). Inputs: predictions-e155.json (frozen at "
                  "82b5af8d), scored*.json, posthoc/posthoc.json, E148's e148.json (primary, 10 passes)."]
    R = P["readings"]
    reg = {k: (R[k]["lo"], R[k]["hi"]) for k in R}
    s = SC["primary"]["stats"]

    # ---- C2: F1's margins as registered, every arm
    L.append("")
    L.append("C2. F1 as registered (bands frozen in predictions-e155.json > readings; the rule is overlap of D31's 95% interval with a band)")
    out["C2"] = {}
    for arm, _ in ARMS:
        d = SC[arm]["rules"]["F1"]["D31"]
        cons, a, b = f1(d, reg)
        g = {k: gap(d["lo"], d["hi"], *reg[k]) for k in reg}
        out["C2"][arm] = {"D31": d, "gaps_w": g, "F1a": a, "F1b": b, "Wt_band_lo_minus_D31_point_w": reg["Wt"][0] - d["mean"]}
        L.append(f"  {arm:12s}: D31 {d['mean']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}] (n {d['n']}); "
                 + "; ".join(f"{k} [{reg[k][0]:.4f}, {reg[k][1]:.4f}] {cons[k]}" + (f" by {g[k]:.4f} = {g[k]:.3f} W" if g[k] else "")
                             for k in ("Wn", "Wt", "T", "C"))
                 + f" -> F1a {a}; F1b {b}; D31's point lies {reg['Wt'][0] - d['mean']:+.4f} W below Wt's band")

    # ---- C1: the premise's own footing
    pp = E["per_pass"]
    ks = sorted(pp, key=int)
    S = lambda k, it: pp[k][it]["S"]
    r = lambda k, it: pp[k][it]["rate"]
    N16 = [S(k, "m0.int8.zeros") - S(k, "m0.fp32.zeros") for k in ks]
    N1 = [S(k, "m0r1.int8.zeros") - S(k, "m0r1.fp32.zeros") for k in ks]
    dN = [a - b for a, b in zip(N16, N1)]
    Eop = [(S(k, "m0r1.fp32.zeros") - S(k, "m0r2.fp32.zeros")) / (r(k, "m0r1.fp32.zeros") - r(k, "m0r2.fp32.zeros")) for k in ks]
    dr16 = [r(k, "m0.int8.zeros") - r(k, "m0.fp32.zeros") for k in ks]
    dr1 = [r(k, "m0r1.int8.zeros") - r(k, "m0r1.fp32.zeros") for k in ks]
    sh16 = [e * g for e, g in zip(Eop, dr16)]
    w16 = [a - b for a, b in zip(dN, sh16)]
    cdN, cE, csh, cw, cN1 = ci(dN), ci(Eop), ci(sh16), ci(w16), ci(N1)
    ref = P["e148_reference"]
    chk = max(abs(cdN["mean"] - ref["N_minus_N1"]["mean"]), abs(cdN["lo"] - ref["N_minus_N1"]["lo"]), abs(cE["mean"] * 1e12 - ref["E_op_fp32_pJ"]["mean"]),
              abs(cN1["mean"] - ref["N1"]["mean"]))
    rp = P["rates_pred_ops_per_s"]
    gap16_frozen = rp["m0.int8"] - rp["m0.fp32"]
    dr3 = P["shared_per_op_term"]["delta_rate_per_s"]
    sh3 = P["shared_per_op_term"]
    L.append("")
    L.append("C1. The bands on the premise's own footing (post hoc)")
    L.append(f"  E148 reproduced from e148.json: N - N1 {cdN['mean']:+.4f} [{cdN['lo']:+.4f}, {cdN['hi']:+.4f}] W, E_op {cE['mean'] * 1e12:.2f} pJ, "
             f"N1 {cN1['mean']:+.4f} W (largest difference from the frozen e148_reference: {chk:.1e})")
    L.append(f"  op-rate gap int8 - fp32: sixteen rows measured {sum(dr16) / len(dr16) / 1e9:.4f}e9/s (frozen prediction {gap16_frozen / 1e9:.4f}e9), "
             f"one row {sum(dr1) / len(dr1) / 1e9:+.5f}e9/s, three rows (frozen) {dr3 / 1e9:.4f}e9/s")
    L.append(f"  the shared per-op term inside E148's N - N1 (E_op x the sixteen-row gap, per pass): {csh['mean']:+.4f} ± {csh['half']:.4f} W "
             f"[{csh['lo']:+.4f}, {csh['hi']:+.4f}]; at the frozen gap {cE['mean'] * gap16_frozen:+.4f} W; three rows' frozen term {sh3['point']:+.4f} W")
    L.append(f"  E148's N - N1 less it: {cw['mean']:+.4f} ± {cw['half']:.4f} W [{cw['lo']:+.4f}, {cw['hi']:+.4f}]")
    fac = {k: R[k]["factor"] for k in ("Wn", "Wt", "T")}
    cons_bands, paired_bands, pts = {}, {}, {}
    for k, f in fac.items():
        pts[k] = f * cw["mean"] + sh3["point"]
        cons_bands[k] = (f * cw["lo"] + sh3["lo"], f * cw["hi"] + sh3["hi"])
        pv = ci([f * w + e * dr3 for w, e in zip(w16, Eop)])
        paired_bands[k] = (pv["lo"], pv["hi"])
    cons_bands["C"] = paired_bands["C"] = reg["C"]
    pts["C"] = R["C"]["point"]
    out["C1"] = {"E148_N_minus_N1": cdN, "E148_shared_16_rows_w": csh, "E148_walk_16_rows_w": cw, "gap16_measured_per_s": sum(dr16) / len(dr16),
                 "points": pts, "bands_interval_rule": cons_bands, "bands_paired": paired_bands, "arms": {}}
    for k in ("Wn", "Wt", "T"):
        L.append(f"  {k}: factor {fac[k]:.4f}; point {pts[k]:.4f} (registered {R[k]['point']:.4f}, {pts[k] - R[k]['point']:+.4f}); band by the "
                 f"registration's interval rule [{cons_bands[k][0]:.4f}, {cons_bands[k][1]:.4f}] (registered [{reg[k][0]:.4f}, {reg[k][1]:.4f}]); "
                 f"paired per E148 pass [{paired_bands[k][0]:.4f}, {paired_bands[k][1]:.4f}]")
    L.append(f"  C: unchanged, built on N1 (no rate gap at one row): [{reg['C'][0]:.4f}, {reg['C'][1]:.4f}]")
    for arm, _ in ARMS:
        d = SC[arm]["rules"]["F1"]["D31"]
        c1, a1, b1 = f1(d, cons_bands)
        c2, a2, b2 = f1(d, paired_bands)
        out["C1"]["arms"][arm] = {"interval_rule": {"cons": c1, "F1a": a1, "F1b": b1}, "paired": {"cons": c2, "F1a": a2, "F1b": b2}}
        L.append(f"  {arm:12s}: D31 [{d['lo']:.4f}, {d['hi']:.4f}] -> interval rule: Wn {c1['Wn']}, Wt {c1['Wt']}, T {c1['T']}, C {c1['C']}: "
                 f"F1a {a1}; F1b {b1} | paired: Wn {c2['Wn']}, Wt {c2['Wt']}: F1b {b2}")
    n3, dm = s["N3"], s["D31"]
    n1ref = ref["N1"]["mean"]
    errs = {}
    for k in ("Wn", "Wt", "T", "C"):
        errs[k] = {"registered": {"D31": dm["mean"] - R[k]["point"], "N3": n3["mean"] - (n1ref + R[k]["point"])},
                   "premise_footing": {"D31": dm["mean"] - pts[k], "N3": n3["mean"] - (n1ref + pts[k])}}
        L.append(f"  errors (measured - predicted), {k}: registered D31 {errs[k]['registered']['D31']:+.4f}, N3 {errs[k]['registered']['N3']:+.4f} W; "
                 f"on the premise's footing D31 {errs[k]['premise_footing']['D31']:+.4f}, N3 {errs[k]['premise_footing']['N3']:+.4f} W")
    out["C1"]["errors_w"] = errs
    L.append(f"  registered Wn margin {gap(dm['lo'], dm['hi'], *reg['Wn']):.4f} W against the construction's shift of Wn's point "
             f"{R['Wn']['point'] - pts['Wn']:.4f} W")
    # the same footing on E148's own two-row rise (E148's post hoc check, posthoc_e148.py section 1, factors from its posthoc.json)
    PH148 = json.load(open(os.path.join(E148D, "posthoc", "posthoc.json")))
    two = {}
    for lab, key in (("new-address", "W, new-address reads (registered count)"), ("toggles", "walk in address-bit toggles (count chosen after the data)")):
        f2 = PH148[key]["factor"]
        reg2, foot2 = [], []
        for i, k in enumerate(ks):
            d21 = (S(k, "m0r2.int8.zeros") - S(k, "m0r2.fp32.zeros")) - N1[i]
            g2 = r(k, "m0r2.int8.zeros") - r(k, "m0r2.fp32.zeros")
            reg2.append(d21 - f2 * dN[i])
            foot2.append(d21 - (f2 * w16[i] + Eop[i] * g2))
        two[lab] = {"factor": f2, "residual_as_E148": ci(reg2), "residual_premise_footing": ci(foot2)}
        a, b = ci(reg2), ci(foot2)
        L.append(f"  E148's two rows (post hoc there), {lab} (factor {f2:.4f}): D21 - prediction as E148 computed it {a['mean']:+.4f} ± {a['half']:.4f} "
                 f"[{a['lo']:+.4f}, {a['hi']:+.4f}]; on the premise's footing (E148's shared term out at sixteen rows, its own at two rows in) "
                 f"{b['mean']:+.4f} ± {b['half']:.4f} [{b['lo']:+.4f}, {b['hi']:+.4f}] W -> {'consistent' if b['lo'] <= 0 <= b['hi'] else 'excluded'}")
    out["C1"]["E148_two_rows"] = two

    # F3's allowance on the premise's footing
    A = P["f3_allowance"]
    I8 = P["bench_per_s_int8"]
    cnt = A["int8_counts_partner_minus_arm_per_s"]
    dri = A["rate_change_int8_per_s"]
    b2 = dict(A["by_reading_pJ"])
    b2["Wn"] = cw["mean"] / I8["m0"]["newaddr"] * cnt["newaddr"] / dri * 1e12
    b2["Wt"] = cw["mean"] / I8["m0"]["tog"] * cnt["tog"] / dri * 1e12
    blo, bhi = min(b2.values()), max(b2.values())
    mid, half = (blo + bhi) / 2, (bhi - blo) / 2
    raw = SC["primary"]["rules"]["F3"]["raw_de3_pJ"]
    x = raw["mean"] - mid
    H = math.sqrt(raw["half"] ** 2 + half ** 2)
    v3 = "BOUNDED" if (x - H > -30 and x + H < 30) else ("EXCEEDS" if (x - H > 30 or x + H < -30) else "INCONCLUSIVE")
    out["C1"]["F3_allowance_premise_footing"] = {"by_reading_pJ": b2, "mid_pJ": mid, "half_pJ": half, "de3c_pJ": x, "H_pJ": H, "interval_pJ": [x - H, x + H],
                                                 "verdict": v3}
    L.append(f"  F3's allowance with Wn's and Wt's prices taken from N - N1 less the term (C and the two-term solve as frozen): Wn {b2['Wn']:+.2f}, "
             f"Wt {b2['Wt']:+.2f} pJ (frozen {A['by_reading_pJ']['Wn']:+.2f}, {A['by_reading_pJ']['Wt']:+.2f}); mid {mid:+.2f} ± {half:.2f} (frozen "
             f"{A['mid_pJ']:+.2f} ± {A['half_pJ']:.2f}); de3c {x:+.2f}, interval [{x - H:+.2f}, {x + H:+.2f}] pJ -> {v3}")

    # ---- C1: one-term prices on matched footings
    Q = P["bench_per_s_card_order"]
    eses = s["E_op_session_pJ"]["mean"] * 1e-12
    p148 = {}
    for lab, y in (("as committed (N - N1)", dN), ("less its shared term at E148's E_op", w16),
                   ("less its shared term at this session's E_op", [a - eses * g for a, g in zip(dN, dr16)])):
        p148[lab] = {"toggle_fJ": ci([v / Q["m0"]["tog"] * 1e15 for v in y]), "newaddr_fJ": ci([v / Q["m0"]["newaddr"] * 1e15 for v in y])}
    p155 = {"less the session's shared term (session E_op)": {"toggle_fJ": SC["primary"]["reported"]["one_term_prices_on_D31_less_session_shared"]["fJ_per_addr_bit_toggle"],
                                                              "newaddr_fJ": SC["primary"]["reported"]["one_term_prices_on_D31_less_session_shared"]["fJ_per_newaddr_read"]},
            "less the frozen shared term (E148's E_op)": {"toggle_fJ": PH["one_term"]["frozen shared"]["fJ_toggle"],
                                                          "newaddr_fJ": PH["one_term"]["frozen shared"]["fJ_newaddr"]}}
    L.append("")
    L.append(f"C1. One-term prices (post hoc), fJ; E155's at three rows (counts {Q['m0r3']['tog']:.4g} toggles and {Q['m0r3']['newaddr']:.4g} new-address "
             f"reads a second), E148's at sixteen ({Q['m0']['tog']:.4g} and {Q['m0']['newaddr']:.4g}); this session's E_op {eses * 1e12:.1f} pJ")
    for lab, v in p148.items():
        L.append(f"  E148 {lab}: toggle {v['toggle_fJ']['mean']:.1f} ± {v['toggle_fJ']['half']:.1f} [{v['toggle_fJ']['lo']:.1f}, {v['toggle_fJ']['hi']:.1f}]; "
                 f"new-address {v['newaddr_fJ']['mean']:.1f} ± {v['newaddr_fJ']['half']:.1f} [{v['newaddr_fJ']['lo']:.1f}, {v['newaddr_fJ']['hi']:.1f}]")
    for lab, v in p155.items():
        L.append(f"  E155 {lab}: toggle {v['toggle_fJ']['mean']:.1f} ± {v['toggle_fJ']['half']:.1f} [{v['toggle_fJ']['lo']:.1f}, {v['toggle_fJ']['hi']:.1f}]; "
                 f"new-address {v['newaddr_fJ']['mean']:.1f} ± {v['newaddr_fJ']['half']:.1f} [{v['newaddr_fJ']['lo']:.1f}, {v['newaddr_fJ']['hi']:.1f}]")
    pairs = (("as committed (each session's own construction)", "as committed (N - N1)", "less the session's shared term (session E_op)"),
             ("mixed: E148 at its E_op, E155 at the session's", "less its shared term at E148's E_op", "less the session's shared term (session E_op)"),
             ("matched: E148's E_op at both", "less its shared term at E148's E_op", "less the frozen shared term (E148's E_op)"),
             ("matched: the session's E_op at both", "less its shared term at this session's E_op", "less the session's shared term (session E_op)"))
    out["C1"]["prices"] = {"E148": p148, "E155": p155, "comparisons": {}}
    for lab, a, b in pairs:
        row = {}
        for c in ("toggle_fJ", "newaddr_fJ"):
            g = gap(p148[a][c]["lo"], p148[a][c]["hi"], p155[b][c]["lo"], p155[b][c]["hi"])
            row[c] = g
        out["C1"]["prices"]["comparisons"][lab] = row
        L.append(f"  {lab}: toggle {'overlap' if row['toggle_fJ'] == 0 else 'miss by %.2f' % row['toggle_fJ']}; new-address "
                 f"{'overlap' if row['newaddr_fJ'] == 0 else 'miss by %.2f' % row['newaddr_fJ']} fJ")

    # ---- C3: Q31k
    qr = s["Q31k"]
    qb = PH["Q31k"]["B_added_back"]
    qk = P["q31k_reported"]
    scale = cw["mean"] / cdN["mean"]
    wpf = {}
    for k, cname in (("Wn", "newaddr"), ("Wt", "tog")):
        wpf[k] = {"point": cw["mean"] / I8["m0"][cname] * I8["m0r3k8"][cname], "lo": cw["lo"] / I8["m0"][cname] * I8["m0r3k8"][cname],
                  "hi": cw["hi"] / I8["m0"][cname] * I8["m0r3k8"][cname]}
    out["C3"] = {"raw": qr, "B_added_back": qb, "B_part_w": qb["mean"] - qr["mean"], "walk_frozen": {"Wn": qk["walk_Wn"], "Wt": qk["walk_Wt"]},
                 "walk_premise_footing": wpf}
    L.append("")
    L.append(f"C3. Q31k = S(m0r3k8.int8) - S(m0r1.int8) (post hoc): raw {qr['mean']:+.4f} ± {qr['half']:.4f} W; with B's halving added back at fp32's "
             f"three-arm price per TenB write {qb['mean']:+.4f} ± {qb['half']:.4f} [{qb['lo']:+.4f}, {qb['hi']:+.4f}] W, of which the add-back is "
             f"{qb['mean'] - qr['mean']:+.4f} W ({(qb['mean'] - qr['mean']) / qb['mean'] * 100:.0f}%)")
    for k in ("Wn", "Wt"):
        fz = qk[f"walk_{k}"]
        L.append(f"  {k}'s walk part, frozen {fz['point']:.4f} [{fz['lo']:.4f}, {fz['hi']:.4f}]: "
                 f"{'overlaps' if gap(qb['lo'], qb['hi'], fz['lo'], fz['hi']) == 0 else 'excluded by %.4f' % gap(qb['lo'], qb['hi'], fz['lo'], fz['hi'])}"
                 f" Q31k's interval, residual {qb['mean'] - fz['point']:+.4f} W; on the premise's footing {wpf[k]['point']:.4f} "
                 f"[{wpf[k]['lo']:.4f}, {wpf[k]['hi']:.4f}], residual {qb['mean'] - wpf[k]['point']:+.4f} W")

    # ---- C4: the out-of-sample errors with their intervals
    n3e = SC["primary"]["reported"]["N3_out_of_sample"]["Wt"]
    out["C4"] = {"N3_error_w": n3e["error_w_from_frozen"], "N3_half_w": n3["half"], "D31_error_w": n3e["D31_error_w"], "D31_half_w": dm["half"],
                 "session_N1_minus_E148_N1_w": s["N1"]["mean"] - n1ref}
    L.append("")
    L.append(f"C4. The toggle count's out-of-sample errors (measured - frozen prediction): N3 {n3e['error_w_from_frozen']:+.4f} ± {n3['half']:.4f} W; "
             f"D31 {n3e['D31_error_w']:+.4f} ± {dm['half']:.4f} W; this session's N1 sits {s['N1']['mean'] - n1ref:+.4f} W above E148's, which "
             f"offsets the rise's error in N3")

    # ---- C5: R6's predictions
    bc, cc = B["bench_cycles"], B["card_cycles_predicted"]
    r6 = SC["primary"]["rules"]["R6"]
    out["C5"] = {k: {"bench": bc[k], "offset": cc[k] - bc[k], "predicted": cc[k], "measured": r6[k]["measured"]} for k in r6}
    L.append("")
    L.append("C5. R6: the frozen cycles are the bench's plus one constant (E109's, fitted on the ordinary op): "
             + "; ".join(f"{k} {bc[k]} + {cc[k] - bc[k]} = {cc[k]} (measured {r6[k]['measured']})" for k in r6))
    json.dump(out, open(os.path.join(HERE, "corrections-numbers.json"), "w"), indent=1)
    open(os.path.join(HERE, "corrections-numbers.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
