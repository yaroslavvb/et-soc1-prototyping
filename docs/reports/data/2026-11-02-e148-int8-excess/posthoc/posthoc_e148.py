#!/usr/bin/env python3
"""E148 post hoc (written after the scored results were read, Mon 2 Nov 2026 ~22:55 PST; it decides nothing and changes no registered verdict).

    python3 docs/reports/data/2026-11-02-e148-int8-excess/posthoc/posthoc_e148.py > docs/reports/data/2026-11-02-e148-int8-excess/posthoc/posthoc.txt

1. Each single-carrier reading of D21 = N2 - N1 rescaled to THIS session's own N - N1 (and N1), paired inside every pass: the residual
   D21 - f x (N - N1), mean and 95% t interval over the ten passes, for the registered walk count (TenC reads at a new address, f = 0.4225), the
   A path (TenTMP's 64-bit A reads, f = -0.6069), and - NEW, chosen after the data were seen - the walk counted in TenC read-address BIT
   TOGGLES (the bench's raddr_tog, f = 512 x rate(r2) / (7,680 x rate(r16)) = 0.2254); and per cycle, D21 - 0.0506 x N1.
2. The one-term prices each walk count implies: (N - N1) over the count a second at sixteen rows (fJ a new-address read; fJ an address-bit toggle).
3. What a third row count would show (a design note for a later registered test): for R = 3, 5, 6, 8 A rows (posthoc/bench-ladder.json, the bench's
   counts), each walk count a second relative to sixteen rows'.

Added after verification (Mon 2 Nov 2026, about 23:40 PST, lane fix-a1c1-e148-int8-excess; desk only, deciding nothing either). Sections 1-3 print
exactly what they printed at 22:49; sections 4-6 are new and are printed after them:
4. The premise allowance: E129's per-op difference between the formats (one_row.e_op_diff_at_r1_rate_w per pass, over E129's one-row int8 rate,
   the frozen 9.8645e9 a second at 62.0 cycles) times int8's op-rate change from one row to two (the frozen rates), D21 net of it, and that against
   W2's line (0) and T's frozen range.
5. The registered two-term solve's shares (scored.json > reported.two_term per pass, times predictions-e148.json > two_term_design): how much of
   N - N1 it gives the walk and the A path, and one row's A staging inside N1.
6. The out-of-sample errors like for like: on D21 (what was frozen for each reading) and on N2 from what was frozen before the run (E129's N1 plus a
   frozen D21), beside the null predictors and the bench's own N2.
Standard library only. SPDX-License-Identifier: Apache-2.0"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
T95 = {2: 4.303, 9: 2.262}     # 2 df added after verification, for E129's three passes (section 4)


def ci(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95.get(n - 1, 2.262) * sd / math.sqrt(n)
    return m, h


def main():
    sc = json.load(open(os.path.join(D, "scored.json")))
    P = json.load(open(os.path.join(ROOT, "tools/claims-v3/e148/predictions-e148.json")))
    B = json.load(open(os.path.join(ROOT, "tools/claims-v3/e148/desk/bench-e148.json")))
    L = json.load(open(os.path.join(HERE, "bench-ladder.json")))["rows"]
    st = sc["stats"]
    d21, dn, n1 = st["D21"]["per_pass"], st["N_minus_N1"]["per_pass"], st["N1"]["per_pass"]
    rate = P["rates_pred_ops_per_s"]
    tog16 = B["streams"]["m0.int8.zeros"]["candidates"]["tenc"]["raddr_tog"] * rate["m0.int8"]
    tog2 = B["streams"]["m0r2.int8.zeros"]["candidates"]["tenc"]["raddr_tog"] * rate["m0r2.int8"]
    new16 = P["bench_per_s_card_order"]["m0"]["tenc_newaddr"]
    f_tog = tog2 / tog16
    out = {"note": "post hoc, deciding nothing", "passes": sc["passes"]}
    print("E148 post hoc (deciding nothing); primary reduction, 10 passes; residuals paired inside each pass, mean +- 95% t (9 df)")
    for name, f, base in (("W, new-address reads (registered count)", P["readings"]["W"]["factor"], dn),
                          ("T, 64-bit A reads into TenTMP (registered count)", P["readings"]["T"]["factor"], dn),
                          ("walk in address-bit toggles (count chosen after the data)", f_tog, dn),
                          ("C, per cycle (registered count)", P["readings"]["C"]["factor"], n1)):
        r = [a - f * b for a, b in zip(d21, base)]
        m, h = ci(r)
        pred = [f * b for b in base]
        pm, ph = ci(pred)
        out[name] = {"factor": f, "predicted_D21_this_session": [pm, ph], "residual": [m, h], "residual_excludes_0": abs(m) > h}
        print(f"  {name}: factor {f:+.4f}; predicts D21 {pm:+.3f} +- {ph:.3f} W from this session; D21 - prediction {m:+.3f} +- {h:.3f} W"
              f" -> {'EXCLUDED' if abs(m) > h else 'consistent'}")
    p_new = [x / new16 * 1e15 for x in dn]
    p_tog = [x / tog16 * 1e15 for x in dn]
    m1, h1 = ci(p_new)
    m2, h2 = ci(p_tog)
    out["one_term_prices_fJ"] = {"per_new_address_read": [m1, h1], "per_address_bit_toggle": [m2, h2],
                                 "counts_per_s_16_rows": {"new_address_reads": new16, "address_bit_toggles": tog16}}
    print(f"  one-term prices from N - N1 at sixteen rows: {m1:.1f} +- {h1:.1f} fJ a TenC read at a new address (7.88e12 a second), or "
          f"{m2:.1f} +- {h2:.1f} fJ an address-bit toggle (1.48e13 a second)")
    print("  design note, the bench's counts a second relative to sixteen rows' (int8 at the card's cycles; fp32 reads TenC at one address):")
    lad = {}
    r16 = L["16"]
    for R in ("2", "3", "5", "6", "8"):
        x = L[R]
        fn = (x["tenc_newaddr"] / x["card_cycles"]["int8"]) / (r16["tenc_newaddr"] / r16["card_cycles"]["int8"])
        ft = (x["tenc_raddr_tog"] / x["card_cycles"]["int8"]) / (r16["tenc_raddr_tog"] / r16["card_cycles"]["int8"])
        lad[R] = {"new_address_reads": fn, "address_bit_toggles": ft, "int8_cycles": x["card_cycles"]["int8"], "fp32_cycles": x["card_cycles"]["fp32"]}
        print(f"    R {R}: new-address reads {fn:.3f}, address-bit toggles {ft:.3f}; cycles int8 {x['card_cycles']['int8']}, fp32 {x['card_cycles']['fp32']}")
    out["ladder_ratios"] = lad
    out["after_verification"] = after_verification(sc, P, st, rate, out)
    json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)


def after_verification(sc, P, st, rate, out):
    """Sections 4-6, added after verification (Mon 2 Nov 2026): the numbers the README's corrections C1, C2, C3, C5 and C6 quote."""
    E129 = json.load(open(os.path.join(os.path.dirname(D), "2026-11-02-e129-int8-noissue", "scored.json")))
    R, d21, n1 = P["readings"], st["D21"], st["N1"]
    res = {}
    print("after verification (Mon 2 Nov 2026; deciding nothing):")
    # 4. the premise allowance
    r1, r2 = rate["m0r1.int8"], rate["m0r2.int8"]
    de = [w / r1 * 1e12 for w in E129["one_row"]["e_op_diff_at_r1_rate_w"]["per_pass"]]
    dem, deh = ci(de)
    dr = r2 - r1
    sm, sh = dr * dem * 1e-12, abs(dr) * deh * 1e-12
    nm, nh = d21["mean"] - sm, math.hypot(d21["half"], sh)
    res["premise"] = {"e_op_diff_pJ": [dem, deh], "e_op_diff_pJ_per_pass": de, "int8_rate_change_per_s": dr, "D21_share_w": [sm, sh],
                      "D21_net_w": [nm, nh], "D21_net_interval_w": [nm - nh, nm + nh], "T_range_top_w": R["T"]["hi"]}
    print(f"  4. premise: E129's per-op difference int8 - fp32 {dem:+.1f} +- {deh:.1f} pJ an op (3 passes, t 4.303); int8's op rate two rows"
          f" against one {dr:+.4e} a second; so a per-op difference puts {sm:+.3f} +- {sh:.3f} W into D21; D21 net of it (half-widths in"
          f" quadrature) {nm:+.3f} +- {nh:.3f} W = [{nm - nh:+.3f}, {nm + nh:+.3f}]: against W2's line 0 -> "
          f"{'still above' if nm - nh > 0 else 'not resolved from zero'}; against T's frozen range (top {R['T']['hi']:+.3f}) -> "
          f"{'T still excluded' if nm - nh > R['T']['hi'] else 'T not excluded'}")
    # 5. the two-term solve's shares
    tt, A = sc["reported"]["two_term"], P["two_term_design"]
    t1 = P["bench_per_s_card_order"]["m0r1"]["tentmp_64bit"]
    pw, pt = tt["pw_fJ_per_newaddr_read"]["per_pass"], tt["pt_pJ_per_64bit_A_read"]["per_pass"]
    shares = {"walk_of_N_minus_N1": [x * 1e-15 * A["a11"] for x in pw], "A_path_of_N_minus_N1": [x * 1e-12 * A["a12"] for x in pt],
              "A_path_one_row_level_in_N1": [x * 1e-12 * t1 for x in pt],
              "walk_in_D21": [x * 1e-15 * A["a21"] for x in pw], "A_path_in_D21": [x * 1e-12 * A["a22"] for x in pt]}
    res["two_term_shares_w"] = {k: list(ci(v)) for k, v in shares.items()}
    res["two_term_pt_pJ"] = [tt["pt_pJ_per_64bit_A_read"][k] for k in ("mean", "half", "lo", "hi")]
    g = {k: ci(v) for k, v in shares.items()}
    print(f"  5. two-term solve (registered, reported): p_t {tt['pt_pJ_per_64bit_A_read']['mean']:.2f} +- {tt['pt_pJ_per_64bit_A_read']['half']:.2f} pJ"
          f" a 64-bit A read (95% {tt['pt_pJ_per_64bit_A_read']['lo']:.2f} to {tt['pt_pJ_per_64bit_A_read']['hi']:.2f}); of N - N1 at sixteen rows"
          f" the walk {g['walk_of_N_minus_N1'][0]:.3f} +- {g['walk_of_N_minus_N1'][1]:.3f} W and the A path {g['A_path_of_N_minus_N1'][0]:.3f} +-"
          f" {g['A_path_of_N_minus_N1'][1]:.3f} W; one row's A staging inside N1 {g['A_path_one_row_level_in_N1'][0]:.3f} +-"
          f" {g['A_path_one_row_level_in_N1'][1]:.3f} W; in D21 the walk {g['walk_in_D21'][0]:+.3f} and the A path {g['A_path_in_D21'][0]:+.3f} W")
    # 6. out-of-sample errors like for like
    bc = P["bench_constants"]["card_order"]
    models = [k for k in bc if k != "range_D21"]
    b_d21 = (bc["range_D21"]["lo"], bc["range_D21"]["hi"])
    e129n1 = P["e129_reference"]["N1"]["mean"]
    n2m = st["N2"]["mean"]
    own_w = out["W, new-address reads (registered count)"]
    own_tog = out["walk in address-bit toggles (count chosen after the data)"]
    rows_d21 = [("null: a second row changes nothing", 0.0, 0.0),
                ("the bench at its constants, card order (frozen)", b_d21[0], b_d21[1]),
                ("C, per cycle (frozen)", R["C"]["point"], R["C"]["point"]),
                ("W, the walk at E129's N - N1 (frozen)", R["W"]["point"], R["W"]["point"]),
                ("T, the A path (frozen)", R["T"]["point"], R["T"]["point"]),
                ("post hoc: W's count at this session's N - N1", own_w["predicted_D21_this_session"][0], own_w["predicted_D21_this_session"][0]),
                ("post hoc: address-bit toggles at this session's N - N1", own_tog["predicted_D21_this_session"][0],
                 own_tog["predicted_D21_this_session"][0])]
    print(f"  6a. D21 measured {d21['mean']:+.3f} +- {d21['half']:.3f} W; error = measured - predicted (each carries the measurement's"
          f" +-{d21['half']:.3f}; the post hoc rows' paired residuals are in section 1):")
    res["errors_D21_w"] = {}
    for name, lo, hi in rows_d21:
        e1, e2 = d21["mean"] - hi, d21["mean"] - lo
        res["errors_D21_w"][name] = {"predicted": [lo, hi], "error": [e1, e2]}
        p = f"{lo:+.3f}" if lo == hi else f"{lo:+.3f} to {hi:+.3f}"
        e = f"{e1:+.3f}" if lo == hi else f"{e1:+.3f} to {e2:+.3f}"
        print(f"      {name}: predicted {p}, error {e}")
    rows_n2 = [("E129's N1 alone (no change from one row)", e129n1, e129n1),
               ("E129's N1 + the bench's frozen D21", e129n1 + b_d21[0], e129n1 + b_d21[1]),
               ("E129's N1 + C's frozen D21", e129n1 + R["C"]["point"], e129n1 + R["C"]["point"]),
               ("E129's N1 + W's frozen D21", e129n1 + R["W"]["point"], e129n1 + R["W"]["point"]),
               ("E129's N1 + T's frozen D21", e129n1 + R["T"]["point"], e129n1 + R["T"]["point"]),
               ("the bench at its own constants, all of N2", min(bc[k]["N2"] for k in models), max(bc[k]["N2"] for k in models))]
    print(f"  6b. N2 measured {n2m:+.3f} +- {st['N2']['half']:.3f} W, from what was frozen before the run (E129's N1 {e129n1:.4f}):")
    res["errors_N2_frozen_w"] = {}
    for name, lo, hi in rows_n2:
        e1, e2 = n2m - hi, n2m - lo
        res["errors_N2_frozen_w"][name] = {"predicted": [lo, hi], "error": [e1, e2]}
        p = f"{lo:.3f}" if lo == hi else f"{lo:.3f} to {hi:.3f}"
        e = f"{e1:+.3f}" if lo == hi else f"{e1:+.3f} to {e2:+.3f}"
        print(f"      {name}: predicted {p}, error {e}")
    bn1 = (min(bc[k]["N1"] for k in models), max(bc[k]["N1"] for k in models))
    res["bench_N1_w"] = {"predicted": list(bn1), "measured": n1["mean"]}
    print(f"      the bench's own N1 at its constants {bn1[0]:.3f} to {bn1[1]:.3f} W against N1 measured {n1['mean']:.3f}: its N2 miss is its N1 miss")
    o2 = sc["reported"]["N2_out_of_sample"]
    same = all(abs(o2[k]["error_w"] - (d21["mean"] - R[k]["point"])) < 1e-9 for k in ("W", "T", "C"))
    res["registered_N2_errors_equal_D21_errors"] = same
    print(f"  6c. the registered N2 errors (this session's N1 + a frozen D21; scored.json > reported.N2_out_of_sample) equal the D21 errors: {same}")
    wn2 = n1["mean"] + own_w["predicted_D21_this_session"][0]
    res["post_hoc_W_count_at_own_scale_N2"] = {"predicted": wn2, "error": n2m - wn2, "null_error": n2m - n1["mean"]}
    print(f"  6d. post hoc: W's count priced at this session's N - N1 ({out['one_term_prices_fJ']['per_new_address_read'][0]:.1f} fJ a new-address"
          f" read) predicts N2 {wn2:.3f} W, error {n2m - wn2:+.3f}, against the null's (N2 = N1) {n2m - n1['mean']:+.3f}")
    return res


if __name__ == "__main__":
    main()
