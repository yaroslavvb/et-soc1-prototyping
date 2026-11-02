#!/usr/bin/env python3
"""E113 (Q133): the frozen predictions for the A side's two layouts, from published aifoundry3 numbers only.

    python3 tools/claims-v3/e113/predict_e113.py --out tools/claims-v3/e113/predictions-e113.json [--print]

Sources (all aifoundry3 card 0, 600 MHz, ~0.522 V, E67's protocol; read from their committed files, never retyped):
  E65  B single-bit prices          docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json  cards.aifoundry3.bits
  E67  A single-bit prices          docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json       cards.aifoundry3.a_bits
  E70  the measured ladders         docs/reports/data/2026-10-27-e70-saturation-ladder/scored.json   lq, ls, alq, D1,
                                    ceilings, A_ceiling, D5 (six passes, the registered reduction)

The laws for one A rung (mask m, k flipping bits; S_A(m) = the sum of E67's A prices over m; S_B(m) the same over E65's B
prices), each frozen here with every constant fixed before E113 runs:
  A    additive                        dW = S_A(m)
  H    "how many"                      dW(als_h<k>) = dW(alq_h<k>): the layout contrast D1_A(k) = 0
  WA   E70's A-side coverage curve     dW = WA (1 - exp(-S_A/WA)), WA = E70's pooled A fit (6.37 W), the form E70 rejected
  WB   the B side's curve on A's sum   dW = WB (1 - exp(-S_A/WB)), WB = E70's B refit (10.52 W)
  M    the mirror: an A mask costs a fixed fraction of the same mask flipped on B
                                       dW = c * dW_B,E70(m), dW_B,E70 = E70's measured B rung with the SAME mask (lq_h<k> for
                                       alq_h<k>, ls_h<k> for als_h<k>), c fitted through the origin on E70's seven alq rungs
                                       against its lq rungs (k = 1, 2, 4, 8, 12, 16, 23). Why it is a candidate: with the partner
                                       held at 1.0 the PRODUCT is the flipping operand, so everything after the multiplier sees
                                       the same bit pattern whichever side flips (A at half the rate), and Q132(b)'s bench puts
                                       most of a bit's position dependence after the multiplier (20x against 2.1x inside it).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
N_B, N_A = 4096, 2048
ALQ_K = [1, 2, 3, 4, 6, 8, 12, 16, 23]
ALS_K = [2, 3, 4, 6, 8, 12, 16]


def low_bits(k):
    return list(range(k))


def spread_bits(k):
    bits = sorted({int(round(j * 23 / k)) for j in range(k)})
    assert len(bits) == k
    return bits


def cov(s, w):
    return w * (1 - math.exp(-s / w))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--print", action="store_true")
    a = ap.parse_args()
    src = {"E65": "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json",
           "E67": "docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json",
           "E70": "docs/reports/data/2026-10-27-e70-saturation-ladder/scored.json"}
    e65 = json.load(open(os.path.join(ROOT, src["E65"])))["cards"]["aifoundry3"]
    e67 = json.load(open(os.path.join(ROOT, src["E67"])))["cards"]["aifoundry3"]
    e70 = json.load(open(os.path.join(ROOT, src["E70"])))
    B = {int(j): v for j, v in e65["bits"].items() if v.get("dW") is not None}
    A = {int(j): v for j, v in e67["a_bits"].items() if v.get("dW") is not None}
    SA = lambda bits: sum(A[b]["dW"] for b in bits)
    SA_se = lambda bits: math.sqrt(sum((A[b]["se"] or 0.0) ** 2 for b in bits))
    SB = lambda bits: sum(B[b]["dW"] for b in bits)
    lq = {r["h"]: r for r in e70["lq"]}
    ls = {r["h"]: r for r in e70["ls"]}
    alq = {r["h"]: r for r in e70["alq"]}
    WA = e70["A_ceiling"]["Winf_A_W"]
    WB = e70["ceilings"]["B_pooled_W"]
    # the mirror constant, through the origin, on E70's seven alq rungs against its lq rungs at the same k
    ks = sorted(k for k in alq if k in lq)
    c = sum(alq[k]["dW"] * lq[k]["dW"] for k in ks) / sum(lq[k]["dW"] ** 2 for k in ks)
    c_rms = math.sqrt(sum((alq[k]["dW"] - c * lq[k]["dW"]) ** 2 for k in ks) / len(ks))
    wa_rms = e70["A_ceiling"]["fit_rms_W"]
    out = {"experiment": "E113", "card": "aifoundry3", "clock_mhz": 600, "sources": src,
           "designed": {"A_bits_per_op_per_k": N_A, "B_bits_per_op_per_h": N_B},
           "constants": {"WA_W": WA, "WA_fit_rms_on_E70_alq_W": wa_rms, "WB_refit_W": WB,
                         "mirror_c": c, "mirror_c_fit_rms_on_E70_alq_W": c_rms, "mirror_c_fitted_on_k": ks,
                         "mirror_c_note": "least squares through the origin, E70 alq_h<k> on lq_h<k>; 2c is the per-bit "
                                          "A/B ratio rho a mirror law implies at every k and layout"}}
    rows = []
    for lay, kk, bitsf, bref in (("alq", ALQ_K, low_bits, lq), ("als", ALS_K, spread_bits, ls)):
        for k in kk:
            bits = bitsf(k)
            s_a, s_b = SA(bits), SB(bits)
            bmeas = bref.get(k)
            if lay == "als" and bmeas is None:
                bmeas = None
            r = {"item": f"{lay}_h{k}", "layout": "low" if lay == "alq" else "spread", "k": k, "bits": bits,
                 "designed_A_bits_per_op": N_A * k, "S_A_W": s_a, "S_A_se_W": SA_se(bits), "S_B_W": s_b,
                 "pred_A_W": s_a, "pred_WA_W": cov(s_a, WA), "pred_WB_on_SA_W": cov(s_a, WB),
                 "B_same_mask_E70_W": bmeas["dW"] if bmeas else None,
                 "B_same_mask_E70_se_W": bmeas["se"] if bmeas else None,
                 "B_same_mask_item": (("lq" if lay == "alq" else "ls") + f"_h{k}") if bmeas else None,
                 "pred_M_W": c * bmeas["dW"] if bmeas else None}
            if lay == "alq" and k in alq:
                r["E70_measured_W"] = alq[k]["dW"]
                r["E70_se_W"] = alq[k]["se"]
            rows.append(r)
    out["rungs"] = rows
    byk = {(r["layout"], r["k"]): r for r in rows}
    d1 = []
    for k in ALS_K:
        s, q = byk[("spread", k)], byk[("low", k)]
        d1.append({"k": k, "S_A_spread_minus_low_W": s["S_A_W"] - q["S_A_W"],
                   "pred_A": s["pred_A_W"] - q["pred_A_W"], "pred_H": 0.0,
                   "pred_WA": s["pred_WA_W"] - q["pred_WA_W"], "pred_WB_on_SA": s["pred_WB_on_SA_W"] - q["pred_WB_on_SA_W"],
                   "pred_M": c * (ls[k]["dW"] - lq[k]["dW"]),
                   "B_side_D1_E70_W": ls[k]["dW"] - lq[k]["dW"]})
    out["D1_A_layout_contrast"] = d1
    # per-bit A/B ratio at k = 8 in each layout (the B ties lq_h8, ls_h8 run in E113's own passes)
    out["rho8"] = {"low_E70": 2 * alq[8]["dW"] / lq[8]["dW"],
                   "pred_M_low": 2 * c, "pred_M_spread": 2 * c,
                   "pred_WA_spread": 2 * byk[("spread", 8)]["pred_WA_W"] / ls[8]["dW"],
                   "pred_A_spread": 2 * byk[("spread", 8)]["pred_A_W"] / ls[8]["dW"],
                   "pred_H_spread": 2 * alq[8]["dW"] / ls[8]["dW"],
                   "note": "rho = [dW_A/(2048 k)] / [dW_B/(4096 k)] = 2 dW_A/dW_B at matched mask; a broadcast A word "
                           "counted once per word (not per lane slot) would put rho near 8x a per-slot B bit's price"}
    out["E70_replicate"] = {f"alq_h{k}": {"W": alq[k]["dW"], "se": alq[k]["se"]} for k in sorted(alq)}
    out["E70_B_ties"] = {"lq_h8": {"W": lq[8]["dW"], "se": lq[8]["se"]}, "ls_h8": {"W": ls[8]["dW"], "se": ls[8]["se"]},
                         "D1_B_h8": {"W": [d for d in e70["D1"] if d["h"] == 8][0]["dW_ls_minus_lq"],
                                     "se": [d for d in e70["D1"] if d["h"] == 8][0]["se"]}}
    out["nrd_a_E70"] = {"W": e70["D5"]["nrd_a"]["measured_W"], "se": e70["D5"]["nrd_a"]["se"],
                        "S_additive_W": e70["D5"]["nrd_a"]["S_additive_W"]}
    json.dump(out, open(a.out, "w"), indent=1)
    if a.print:
        print(f"WA {WA:.3f} W (E70 rms {wa_rms:.3f}), WB {WB:.3f} W, mirror c {c:.4f} (rms on E70 alq {c_rms:.3f} W)")
        print(f"{'item':9s} {'k':>2s} {'S_A':>7s} {'A':>7s} {'WA':>6s} {'WB':>6s} {'M':>6s} {'E70':>6s}  bits")
        for r in rows:
            e = r.get("E70_measured_W")
            m = r["pred_M_W"]
            print(f"{r['item']:9s} {r['k']:2d} {r['S_A_W']:7.3f} {r['pred_A_W']:7.3f} {r['pred_WA_W']:6.3f} "
                  f"{r['pred_WB_on_SA_W']:6.3f} {('%6.3f' % m) if m is not None else '     -'} "
                  f"{('%6.3f' % e) if e is not None else '     -'}  {r['bits']}")
        print("D1_A (spread - low):")
        for d in d1:
            print(f"  k={d['k']:2d}  A {d['pred_A']:7.3f}  WA {d['pred_WA']:6.3f}  WB {d['pred_WB_on_SA']:6.3f}  "
                  f"M {d['pred_M']:6.3f}  H 0   (B side E70 {d['B_side_D1_E70_W']:.3f})")
        print("rho8:", json.dumps(out["rho8"]))


if __name__ == "__main__":
    main()
