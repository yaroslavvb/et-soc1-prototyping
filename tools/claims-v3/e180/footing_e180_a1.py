#!/usr/bin/env python3
"""E180's dated note A1 (E180.md.dated-note-A1.md sections 1, 3 and 4): the footing E180's prices and D rest on, the prices re-made on the
current footing law, C's standard error restated, and the net-minion-rail arm's frozen forecast.

    python3 -B tools/claims-v3/e180/footing_e180_a1.py --dir tools/claims-v3/e180 --root .            # writes footing-e180-a1.json and .txt
    python3 -B tools/claims-v3/e180/footing_e180_a1.py --dir tools/claims-v3/e180 --root . --check    # re-makes both, byte for byte

Post hoc reads of committed data, after the registration and before any E180 datum; nothing is fitted to an E180 outcome.
  F1. The label. The catalogue's reduction (workloads/enercat/analyze_catalogue.py, unchanged) corrects each burst's board rise with the
      21 Sep law's slope, k21(T) = 23.257/36 exp((T - 80)/36) W/C, at the burst's mid die, times its rise (Tb - Ti). The registered
      footing law (tools/claims-v3/footing-law, c14e5f35, FL1) gives k_c(T) = 2 q0 T + q1 per card. Both laws at 52-66 C per card, and at
      the fadd rows' own mid temperatures.
  F2. The prices on three footings, from each catalogue burst's own over_idle_raw_w, die_c_busy and die_c_idle: the registered (k21;
      it must reproduce the catalogue's pj_per_op to its own rounding), FL1 (each card's own law), and E60's in-run slope on aifoundry3 (0.2026 W/C,
      docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt line 19, dfee3d7a; FOOTING-LAW.md: a diluted estimator, reported only).
      Then P (aifoundry3's random - zeros over the bench's N(random)), C (const - zeros pooled as forecast_e180.py pools it), and the
      forecasts that move with them on aifoundry3: his pair, const, R3max, the ladder slope, E180-A.
  F3. The reading's footing gain: E180's D are read on the registered footing; read on another, every D difference changes by
      (k_reg - k_alt) x (the burst's rise per watt), a gain on the slope. The rise per watt is the least-squares slope of (Tb - Ti) on
      over_idle_raw_w over aifoundry3's two-hart vector rows (the catalogue's bursts, the same 3 s protocol E180 runs).
  F4. C's standard error restated: the registered inverse-variance pooling of three 2-df per-card ses (aifoundry2's 3-pass se is the
      smallest by luck and takes most of the weight), against the same pooling with each card's se from its own pair noise
      (noise-e180.json's median, noise-e180-a1.json's debiased median and rms: se = sigma_d / sqrt 3, in pJ at the row's wall rate).
  F5. The net minion rail (CONTEXT section 48's vector-arm rules 1, 3 and 5, footing A): the anatomy's committed re-split
      (docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc-note1-q145a.json, 877e7476: the catalogue's rails_over net of their
      own heating by reduce_e78.py's c_rb rule, 0.81 of the law's slope on the rise through the card's rail filter, / 0.94) gives
      fadd.ps random - zeros on the board and on the minion rail per card; their ratio on aifoundry3 is the rail arm's share, frozen
      here, so the rail forecast of any kind is its board forecast times that share (the form E178's owed rail arm takes: CONTEXT
      section 50). Also reported: fadd.ps const - zeros on the minion rail (footing A) per card and pooled, as committed.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics as st
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import power_e180 as pw  # noqa: E402

CAT = "docs/reports/data/2026-09-23-energy-manual/catalogue.json"
LAW = "tools/claims-v3/footing-law/footing-law.json"
ANAT = "docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc-note1-q145a.json"
CARDS = ("aifoundry3", "aifoundry1-c1", "aifoundry2")
LAWKEY = {"aifoundry3": "aifoundry3", "aifoundry1-c1": "aifoundry1c1", "aifoundry2": "aifoundry2"}
E60_SLOPE = 0.2026
ROWS = ("fadd.ps/zeros/h2", "fadd.ps/const/h2", "fadd.ps/random/h2", "fadd.pi/zeros/h2", "fadd.pi/const/h2", "fadd.pi/random/h2")


def k21(T):
    return 23.257 / 36.0 * math.exp((T - 80.0) / 36.0)


def kfl(q, T):
    return 2 * q[0] * T + q[1]


def build(d, root):
    cat = json.load(open(os.path.join(root, CAT)))
    law = json.load(open(os.path.join(root, LAW)))["laws"]
    anat = json.load(open(os.path.join(root, ANAT)))
    fc = json.load(open(os.path.join(d, "forecast-e180.json")))
    nz = json.load(open(os.path.join(d, "noise", "noise-e180.json")))["cards"]
    nz1 = json.load(open(os.path.join(d, "noise", "noise-e180-a1.json")))["cards"]
    K = fc["kinds"]
    out = {"what": "E180 dated note A1: the footing, the prices on the current footing, C's se, the rail arm (footing_e180_a1.py)"}
    # ---- F1: the two laws
    f1 = {}
    for c in CARDS:
        q = law[LAWKEY[c]]["quad_w"]
        tab = {str(T): {"k21": k21(T), "kFL1": kfl(q, T), "diff": k21(T) - kfl(q, T)} for T in range(52, 67)}
        mids = [0.5 * (b["die_c_busy"] + b["die_c_idle"]) for b in cat["bursts"][c] if b["cfg"] in ROWS]
        f1[c] = {"law_quad_w": q, "by_degree": tab, "fadd_rows_mid_c": [min(mids), max(mids)],
                 "max_abs_diff_over_fadd_mids_w_per_c": max(abs(k21(T) - kfl(q, T)) for T in mids),
                 "max_abs_diff_55_62_w_per_c": max(abs(k21(T) - kfl(q, T)) for T in range(55, 63))}
    out["F1_laws"] = f1
    # ---- F2: the rows on three footings
    foot = {"registered_21sep": lambda c, T: k21(T), "FL1": lambda c, T: kfl(law[LAWKEY[c]]["quad_w"], T),
            "E60_inrun": lambda c, T: E60_SLOPE}
    rows, worst = {}, 0.0
    for c in CARDS:
        rows[c] = {}
        for cfg in ROWS:
            bs = sorted((b for b in cat["bursts"][c] if b["cfg"] == cfg), key=lambda b: b["pass"])
            rec = {"passes": [b["pass"] for b in bs], "wall_per_op_ps": [b["wall_s"] / b["ops"] * 1e12 for b in bs],
                   "rise_c": [b["die_c_busy"] - b["die_c_idle"] for b in bs]}
            for fn, kf in foot.items():
                if fn == "E60_inrun" and c != "aifoundry3":
                    continue
                pj = []
                for b in bs:
                    Tm = 0.5 * (b["die_c_busy"] + b["die_c_idle"])
                    over = b["over_idle_raw_w"] - kf(c, Tm) * (b["die_c_busy"] - b["die_c_idle"])
                    pj.append(over * b["wall_s"] / b["ops"] * 1e12)
                    if fn == "registered_21sep":
                        worst = max(worst, abs(pj[-1] - b["pj_per_op"]))
                rec[fn] = pj
            rows[c][cfg] = rec
    out["F2_reproduces_catalogue_pj_max_abs"] = worst

    def above(c, fn, a, z):
        x, y = rows[c][a][fn], rows[c][z][fn]
        return st.mean(x) - st.mean(y), math.sqrt(st.variance(x) / len(x) + st.variance(y) / len(y))

    Nr, Nc = K["fadd.ps/random"]["counts"]["N"], K["fadd.ps/const"]["counts"]["N"]
    rate = K["fadd.ps/f_4"]["W"]["aifoundry3"]["rate"]
    f2 = {}
    for fn in foot:
        e = {}
        rz, rz_se = above("aifoundry3", fn, "fadd.ps/random/h2", "fadd.ps/zeros/h2")
        pN = 1000 * rz / Nr
        e["P_random_minus_zeros_pj"], e["P_pN_fJ"] = rz, pN
        cz = {}
        for c in CARDS:
            if fn in rows[c]["fadd.ps/zeros/h2"]:
                cz[c] = dict(zip(("pj", "se_pj"), above(c, fn, "fadd.ps/const/h2", "fadd.ps/zeros/h2")))
        e["const_minus_zeros_per_card"] = cz
        if len(cz) == 3:
            w = {c: 1.0 / v["se_pj"] ** 2 for c, v in cz.items()}
            pooled = sum(w[c] * cz[c]["pj"] for c in cz) / sum(w.values())
            e["C_pooled_pj"], e["C_pooled_se_pj"], e["C_pN_fJ"] = pooled, 1 / math.sqrt(sum(w.values())), 1000 * pooled / Nc
            e["C_weights"] = {c: w[c] / sum(w.values()) for c in w}
        fW = {}
        for nm in ("fadd.ps/f_5", "fadd.ps/f_4", "fadd.ps/const", "fadd.ps/r3_max", "fadd.ps.acc/f_4"):
            fW[nm] = {"P": pN * K[nm]["counts"]["N"] * 1e-15 * rate}
            if "C_pN_fJ" in e:
                fW[nm]["C"] = e["C_pN_fJ"] * K[nm]["counts"]["N"] * 1e-15 * rate
        e["forecast_W"] = fW
        e["his_pair_W"] = {a: fW["fadd.ps/f_5"][a] - fW["fadd.ps/f_4"][a] for a in fW["fadd.ps/f_5"]}
        e["A_W"] = {a: fW["fadd.ps.acc/f_4"][a] - fW["fadd.ps/f_4"][a] for a in fW["fadd.ps/f_4"]}
        e["ladder_slope_P_W_per_bit"] = fc["ladder"]["slope_W_per_bit"]["P"] * pN / fc["prices"]["P@aifoundry3"]["pN_fJ"]
        f2[fn] = e
    out["F2_prices_by_footing"] = f2
    # ---- F3: the reading's footing gain
    vb = [b for b in cat["bursts"]["aifoundry3"] if b.get("unit") == "instruction" and b.get("harts") == 2
          and b["cfg"].split("/")[0].endswith((".ps", ".pi"))]
    xs = [b["over_idle_raw_w"] for b in vb]
    ys = [b["die_c_busy"] - b["die_c_idle"] for b in vb]
    g = pw.ols(xs, ys)
    Tm = st.median(0.5 * (b["die_c_busy"] + b["die_c_idle"]) for b in vb)
    q3 = law["aifoundry3"]["quad_w"]
    f3 = {"bursts": len(vb), "rise_per_raw_watt_c_per_w": g, "median_mid_die_c": Tm, "k21_at_mid": k21(Tm), "kFL1_at_mid": kfl(q3, Tm)}
    for name, kalt in (("FL1", kfl(q3, Tm)), ("E60_inrun", E60_SLOPE)):
        gain = 1 + (k21(Tm) - kalt) * g
        f3[name] = {"k_alt": kalt, "gain_on_D_differences": gain,
                    "L_slope_shift_W_per_bit": fc["ladder"]["slope_W_per_bit"]["P"] * (gain - 1),
                    "his_pair_shift_W": (K["fadd.ps/f_5"]["W"]["aifoundry3"]["P"] - K["fadd.ps/f_4"]["W"]["aifoundry3"]["P"]) * (gain - 1)}
    out["F3_reading_gain"] = f3
    # ---- F4: C's se restated
    f4 = {"registered": {"C_pj": fc["prices"]["C"]["const_minus_zeros_pj"], "se_pj": fc["prices"]["C"]["se_pj"],
                         "weights": {c: (1 / v["se_pj"] ** 2) / sum(1 / u["se_pj"] ** 2 for u in fc["prices"]["C"]["per_card"].values())
                                     for c, v in fc["prices"]["C"]["per_card"].items()}}}
    P_const_pj = fc["prices"]["P@aifoundry3"]["pN_fJ"] * Nc / 1000
    f4["P_const_pj"] = P_const_pj
    f4["registered"]["P_low_by_se"] = (f4["registered"]["C_pj"] - P_const_pj) / f4["registered"]["se_pj"]
    for lvl, src, key in (("median", nz, "sigma_d_vec_w"), ("debiased", nz1, "debiased_median_w"), ("rms", nz1, "rms_w")):
        per, w = {}, {}
        for c in CARDS:
            wpo = st.mean(rows[c]["fadd.ps/const/h2"]["wall_per_op_ps"] + rows[c]["fadd.ps/zeros/h2"]["wall_per_op_ps"])
            se = src[c][key] / math.sqrt(3) * wpo
            per[c] = {"se_pj": se, "pj": fc["prices"]["C"]["per_card"][c]["pj"]}
            w[c] = 1 / se ** 2
        pooled = sum(w[c] * per[c]["pj"] for c in CARDS) / sum(w.values())
        se = 1 / math.sqrt(sum(w.values()))
        f4[lvl] = {"per_card": per, "weights": {c: w[c] / sum(w.values()) for c in CARDS}, "C_pj": pooled, "se_pj": se,
                   "C_W_aifoundry3": pooled * 1e-12 * rate, "se_W_aifoundry3": se * 1e-12 * rate, "P_low_by_se": (pooled - P_const_pj) / se}
    out["F4_C_se"] = f4
    # ---- F5: the net minion rail
    pairs = {(p["op"] if "op" in p else p["board"]["op"], p["a"], p["b"]): p for p in anat["f1_vector_pairs_pooled"]}
    rz = pairs[("fadd.ps", "random", "zeros")]
    czp = pairs[("fadd.ps", "const", "zeros")]
    share = {c: rz["minion_A"]["per_card"][c]["mean"] / rz["board"]["per_card"][c]["mean"] for c in CARDS}
    s3 = share["aifoundry3"]
    f5 = {"random_minus_zeros_pj": {c: {"board": rz["board"]["per_card"][c]["mean"], "minion_A": rz["minion_A"]["per_card"][c]["mean"],
                                         "minion_raw": rz["minion_raw"]["per_card"][c]["mean"] if "minion_raw" in rz else None}
                                     for c in CARDS},
          "share_minion_A_of_board": share, "share_used_aifoundry3": s3,
          "const_minus_zeros_pj_committed": {k: {"mean": czp[k]["mean"], "ci95": czp[k]["ci95"],
                                                 "per_card": {c: czp[k]["per_card"][c]["mean"] for c in CARDS}}
                                             for k in ("board", "minion_A", "minion_Au") if k in czp},
          "rail_forecast_W": {}}
    for nm in ("fadd.ps/const", "fadd.ps/f_4", "fadd.ps/f_5", "fadd.ps/r3_max", "fadd.ps/random", "fadd.ps.acc/f_4"):
        f5["rail_forecast_W"][nm] = {a: K[nm]["W"]["aifoundry3"][a] * s3 for a in ("P", "C", "E", "F", "A")}
    f5["rail_his_pair_W"] = {a: (K["fadd.ps/f_5"]["W"]["aifoundry3"][a] - K["fadd.ps/f_4"]["W"]["aifoundry3"][a]) * s3
                             for a in ("P", "C", "E", "F", "A")}
    f5["rail_ladder_slope_W_per_bit"] = {a: fc["ladder"]["slope_W_per_bit"][a] * s3 for a in ("P", "C", "E", "F", "A")}
    f5["rail_A_W"] = {a: ((K["fadd.ps.acc/f_4"]["W"]["aifoundry3"][a] - K["fadd.ps.acc/zeros"]["W"]["aifoundry3"][a]) -
                          (K["fadd.ps/f_4"]["W"]["aifoundry3"][a] - K["fadd.ps/zeros"]["W"]["aifoundry3"][a])) * s3
                      for a in ("P", "C", "E", "F", "A")}
    out["F5_rail"] = f5
    return out


def text(o):
    L = ["E180 dated note A1: footing, prices, C's se and the rail arm (footing_e180_a1.py); post hoc reads of committed data."]
    L.append("F1. The 21 Sep law against FL1 (W/C):")
    for c, v in o["F1_laws"].items():
        L.append(f"   {c}: fadd rows' mid die {v['fadd_rows_mid_c'][0]:.2f}-{v['fadd_rows_mid_c'][1]:.2f} C; max |k21 - kFL1| there "
                 f"{v['max_abs_diff_over_fadd_mids_w_per_c']:.4f}, over 55-62 C {v['max_abs_diff_55_62_w_per_c']:.4f}; at 58 C "
                 f"{v['by_degree']['58']['k21']:.4f} against {v['by_degree']['58']['kFL1']:.4f}")
    L.append(f"F2. The registered footing reproduces the catalogue's pj_per_op to {o['F2_reproduces_catalogue_pj_max_abs']:.2e} pJ.")
    for fn, e in o["F2_prices_by_footing"].items():
        s = f"   {fn:16s}: P {e['P_pN_fJ']:.4f} fJ (random - zeros {e['P_random_minus_zeros_pj']:.4f} pJ)"
        if "C_pN_fJ" in e:
            s += f"; C {e['C_pN_fJ']:.4f} fJ (pooled {e['C_pooled_pj']:+.4f} +- {e['C_pooled_se_pj']:.4f} pJ)"
        s += "; his pair " + " / ".join(f"{a} {v:+.4f}" for a, v in e["his_pair_W"].items()) + " W"
        s += f"; ladder slope P {e['ladder_slope_P_W_per_bit']:.5f} W a bit; E180-A " + " / ".join(f"{a} {v:+.3f}" for a, v in e["A_W"].items()) + " W"
        L.append(s)
        L.append("      const - zeros by card (pJ): " + ", ".join(f"{c} {v['pj']:+.4f} +- {v['se_pj']:.4f}" for c, v in e["const_minus_zeros_per_card"].items()))
    f3 = o["F3_reading_gain"]
    L.append(f"F3. aifoundry3's vector rows: the burst's rise {f3['rise_per_raw_watt_c_per_w']:.4f} C per raw watt over {f3['bursts']} bursts; "
             f"median mid die {f3['median_mid_die_c']:.2f} C (k21 {f3['k21_at_mid']:.4f}, FL1 {f3['kFL1_at_mid']:.4f} W/C)")
    for name in ("FL1", "E60_inrun"):
        v = f3[name]
        L.append(f"   read on {name} (k {v['k_alt']:.4f}): every D difference x {v['gain_on_D_differences']:.5f}; L's slope moves "
                 f"{v['L_slope_shift_W_per_bit']:+.5f} W a bit, his pair {v['his_pair_shift_W']:+.5f} W")
    f4 = o["F4_C_se"]
    L.append(f"F4. C's pooled se. P's const - zeros {f4['P_const_pj']:.4f} pJ.")
    r = f4["registered"]
    L.append(f"   registered: {r['C_pj']:+.4f} +- {r['se_pj']:.4f} pJ, weights " + ", ".join(f"{c} {w:.3f}" for c, w in r["weights"].items())
             + f"; P low by {r['P_low_by_se']:.2f} se")
    for lvl in ("median", "debiased", "rms"):
        v = f4[lvl]
        L.append(f"   each card's own {lvl} pair noise: {v['C_pj']:+.4f} +- {v['se_pj']:.4f} pJ ({v['C_W_aifoundry3']:+.4f} +- "
                 f"{v['se_W_aifoundry3']:.4f} W on aifoundry3), weights " + ", ".join(f"{c} {w:.3f}" for c, w in v["weights"].items())
                 + f"; P low by {v['P_low_by_se']:.2f} se")
    f5 = o["F5_rail"]
    L.append("F5. Net minion rail (footing A): fadd.ps random - zeros, minion A over board: " +
             ", ".join(f"{c} {v:.4f}" for c, v in f5["share_minion_A_of_board"].items()) + f"; the share used (aifoundry3) {f5['share_used_aifoundry3']:.4f}")
    L.append("   rail forecasts (W, P / C / E / F / A): his pair " + " / ".join(f"{v:+.4f}" for v in f5["rail_his_pair_W"].values())
             + "; ladder slope " + " / ".join(f"{v:.5f}" for v in f5["rail_ladder_slope_W_per_bit"].values()) + " W a bit; E180-A "
             + " / ".join(f"{v:+.3f}" for v in f5["rail_A_W"].values()))
    L.append("   const: " + " / ".join(f"{v:+.4f}" for v in f5["rail_forecast_W"]["fadd.ps/const"].values()) + " W; R3max: "
             + " / ".join(f"{v:+.3f}" for v in f5["rail_forecast_W"]["fadd.ps/r3_max"].values()) + " W")
    for k, v in f5["const_minus_zeros_pj_committed"].items():
        L.append(f"   committed fadd.ps const - zeros, {k}: pooled {v['mean']:+.3f} +- {v['ci95']:.3f} pJ (95%); per card "
                 + ", ".join(f"{c} {x:+.3f}" for c, x in v["per_card"].items()))
    return "\n".join(L) + "\n"


def write(d, root, outdir):
    o = build(d, root)
    json.dump(pw.rnd(o), open(os.path.join(outdir, "footing-e180-a1.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(outdir, "footing-e180-a1.txt"), "w").write(text(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        write(a.dir, a.root, a.dir)
        print(open(os.path.join(a.dir, "footing-e180-a1.txt")).read())
        return
    with tempfile.TemporaryDirectory() as t:
        write(a.dir, a.root, t)
        bad = [f for f in ("footing-e180-a1.json", "footing-e180-a1.txt")
               if open(os.path.join(t, f)).read() != open(os.path.join(a.dir, f)).read()]
    print("CHECK FAIL: " + ", ".join(bad) if bad else "CHECK PASS: footing-e180-a1.json and footing-e180-a1.txt byte for byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
