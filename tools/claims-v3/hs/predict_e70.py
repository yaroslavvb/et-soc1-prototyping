#!/usr/bin/env python3
"""E70 (Q129) pre-registered predictions: the saturation ladder and the A-side multi-bit ladder.

    python3 tools/claims-v3/hs/predict_e70.py --out <predictions-e70.json> [--print]

Everything here is derived from already-published aifoundry3 numbers at 600 MHz / ~0.522 V, so the whole
prediction set is frozen before the first E70 launch and nothing in it depends on E70's own data:

  * E65  B-side single-bit prices, all 32 positions, quiet partner A = 1.0, against lq_h0
         docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json  -> cards.aifoundry3.bits
  * E67  A-side single-bit prices, all 32 positions, quiet partner B = 1.0, against aq_h0, and the
         interaction grid's mean excess (the shared turn-on T = -excess)
         docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json       -> cards.aifoundry3.a_bits, .ix
  * E60  the lq ladder on THIS card (h = 1, 2, 4, 8, 12, 16, 23)
         docs/reports/data/2026-10-20-bitflip-ladder/hl.json              -> cards.aifoundry3.lq.rungs

Three candidate laws for how h simultaneous flips add up (README.md states them and the decision rules):

  A  additive          dW(mask) = S(mask),  S = sum of the single-bit prices of the flipping positions
  H  "how many"        the deficit is set by the Hamming weight alone:
       H-strong        dW_ls(h) = dW_lq(h) at every h (layout does not matter)
       H-offset        dW(mask) = S(mask) - (h-1)*T, one shared turn-on T charged once instead of h times
  W  "which bits"      shared wires: dW is one saturating function of S, the same curve for both layouts,
                       dW = Winf * (1 - exp(-S/Winf)), Winf fitted on E60's lq ladder ALONE and then used to
                       predict every ls and alq rung with no further freedom.
"""
import argparse
import json
import math
import os

N_B_BITS = 4096        # designed B-bit flips per multiply-add per minion (B alternates every micro-op)
N_A_BITS = 2048        # designed A-bit flips per multiply-add (the issue order holds A for two micro-ops)
LQ_H = [1, 2, 3, 4, 6, 8, 12, 16, 23]   # the low layout. At h = 23 the spread mask IS the low mask, so the two
                                        # layouts coincide there by construction: a built-in tie and the ceiling anchor
LS_H = [2, 3, 4, 6, 8, 12, 16]
ALQ_K = [1, 2, 4, 8, 12, 16, 23]
RATE = 1.10e9          # measured multiply-adds per second per minion on this card (E67's pass means)


def low_mask_bits(h):
    return list(range(h))


def spread_mask_bits(h):
    """make_hl.py:spread_mask -- h bits spread evenly over the 23 mantissa positions."""
    if h == 0:
        return []
    bits = sorted({int(round(j * 23 / h)) for j in range(h)})
    assert len(bits) == h, (h, bits)
    return bits


def price_list(d):
    return {int(k): v for k, v in d.items() if v.get("dW") is not None}


def ssum(prices, bits):
    return sum(prices[b]["dW"] for b in bits)


def ssum_se(prices, bits):
    return math.sqrt(sum((prices[b]["se"] or 0.0) ** 2 for b in bits))


def fit_ceiling(points):
    """Least-squares Winf of dW = Winf*(1-exp(-S/Winf)) over (S, dW) points, by scan + bisection refine."""
    def err(w):
        return sum((w * (1 - math.exp(-s / w)) - y) ** 2 for s, y in points)
    best, lo, hi = None, 0.5, 400.0
    n = 4000
    for i in range(n + 1):
        w = lo * (hi / lo) ** (i / n)
        e = err(w)
        if best is None or e < best[1]:
            best = (w, e)
    return best[0], math.sqrt(best[1] / len(points))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    ap.add_argument("--out", required=True)
    ap.add_argument("--print", action="store_true")
    a = ap.parse_args()
    R = os.path.abspath(a.root)
    e65 = json.load(open(f"{R}/docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json"))["cards"]["aifoundry3"]
    e67 = json.load(open(f"{R}/docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json"))["cards"]["aifoundry3"]
    e60 = json.load(open(f"{R}/docs/reports/data/2026-10-20-bitflip-ladder/hl.json"))["cards"]["aifoundry3"]
    B = price_list(e65["bits"])              # B-side single-bit prices, W above lq_h0
    A = price_list(e67["a_bits"])            # A-side single-bit prices, W above aq_h0
    T = -e67["ix"]["excess_mean_W"]          # the shared turn-on the interaction grid measures
    T_se = e67["ix"]["excess_mean_se"]
    e60_lq = {int(v["h"]): v for v in e60["lq"]["rungs"].values() if v.get("dW") is not None}

    out = {"card": "aifoundry3", "clock_mhz": 600, "v_mean": e67["v_mean"], "rate_assumed": RATE,
           "sources": {"B_single_bit": "E65 cards.aifoundry3.bits", "A_single_bit": "E67 cards.aifoundry3.a_bits",
                       "turn_on_T_W": T, "turn_on_T_se_W": T_se, "lq_prior": "E60 cards.aifoundry3.lq.rungs"},
           "designed": {"B_bits_per_op_per_h": N_B_BITS, "A_bits_per_op_per_k": N_A_BITS}}

    # ---- Law W's single free parameter, fitted on E60's lq ladder alone (no E70 data, no ls, no A side)
    lq_prior = []
    for h, v in sorted(e60_lq.items()):
        s = ssum(B, low_mask_bits(h))
        lq_prior.append({"h": h, "S_additive_W": s, "measured_W": v["dW"], "se_W": v["se"],
                         "ratio_measured_over_additive": v["dW"] / s,
                         "T_implied_W": (s - v["dW"]) / (h - 1) if h > 1 else None})
    winf, rms = fit_ceiling([(p["S_additive_W"], p["measured_W"]) for p in lq_prior])
    out["law_W_fit"] = {"Winf_W": winf, "fit_rms_W": rms, "fitted_on": "E60 lq rungs h=1..23 on aifoundry3",
                        "n_points": len(lq_prior)}
    out["lq_prior_E60"] = lq_prior

    def rungs(kind, hs, prices, nbits, maskf, ceiling):
        rows = []
        for h in hs:
            bits = maskf(h)
            s = ssum(prices, bits)
            row = {"item": f"{kind}_h{h}", "h": h, "bits": bits, "designed_bits_per_op": nbits * h,
                   "S_additive_W": s, "S_additive_se_W": ssum_se(prices, bits),
                   "pred_law_A_W": s,
                   "pred_law_H_offset_W": s - (h - 1) * T,
                   "pred_law_W_W": ceiling * (1 - math.exp(-s / ceiling)),
                   "fJ_per_bit_if_law_A": 1e15 * s / (nbits * h * RATE),
                   "fJ_per_bit_if_law_W": 1e15 * ceiling * (1 - math.exp(-s / ceiling)) / (nbits * h * RATE)}
            if kind == "lq" and h in e60_lq:
                row["pred_replicate_E60_W"] = e60_lq[h]["dW"]
                row["pred_replicate_E60_se_W"] = e60_lq[h]["se"]
            rows.append(row)
        return rows

    out["lq"] = rungs("lq", LQ_H, B, N_B_BITS, low_mask_bits, winf)
    out["ls"] = rungs("ls", LS_H, B, N_B_BITS, spread_mask_bits, winf)
    out["alq"] = rungs("alq", ALQ_K, A, N_A_BITS, low_mask_bits, winf)
    # the A side's own ceiling if the ceiling scales with the operand's designed rate instead of being shared
    out["alq_half_ceiling"] = rungs("alq", ALQ_K, A, N_A_BITS, low_mask_bits, winf / 2)

    # ---- D1: the matched-h layout contrast, the experiment's sharpest discriminator
    d1 = []
    for h in LS_H:
        sl, sq = ssum(B, spread_mask_bits(h)), ssum(B, low_mask_bits(h))
        pw = winf * (1 - math.exp(-sl / winf)) - winf * (1 - math.exp(-sq / winf))
        d1.append({"h": h, "S_ls_W": sl, "S_lq_W": sq, "S_difference_W": sl - sq,
                   "pred_law_A_dW": sl - sq, "pred_law_H_offset_dW": sl - sq, "pred_law_H_strong_dW": 0.0,
                   "pred_law_W_dW": pw})
    out["D1_matched_h_layout_contrast"] = d1

    # ---- D3: is the implied turn-on constant across rungs? (E60's lq ladder already answers this for one layout)
    ts = [p["T_implied_W"] for p in lq_prior if p["T_implied_W"] is not None]
    out["D3_turn_on_spread_in_E60_lq"] = {"T_implied_W": ts, "min": min(ts), "max": max(ts),
                                          "grid_T_W": T, "grid_T_se_W": T_se}

    # ---- the carry-over between operands: single-bit vs multi-bit A/B, per flipped bit
    med = lambda xs: sorted(xs)[len(xs) // 2] if len(xs) % 2 else 0.5 * (sorted(xs)[len(xs) // 2 - 1] + sorted(xs)[len(xs) // 2])
    mant = [j for j in range(23) if j in A and j in B]
    raw = [A[j]["dW"] / B[j]["dW"] * (N_B_BITS / N_A_BITS) for j in mant]   # per flipped bit, not per item
    marg = []
    for j in mant:
        ea, eb = A[j]["dW"] - T, B[j]["dW"] - T
        if eb > 0 and ea > 0:
            marg.append(ea / eb * (N_B_BITS / N_A_BITS))
    out["carry_over_prior"] = {
        "single_bit_raw_per_bit_median": med(raw), "n_positions": len(mant),
        "single_bit_item_ratio_median": med([A[j]["dW"] / B[j]["dW"] for j in mant]),
        "single_bit_marginal_per_bit_median": med(marg) if marg else None,
        "n_marginal_usable": len(marg),
        "note": "the two defensible numbers Q128 had to choose between; E70's matched-h alq vs lq measures it"}
    out["D4_matched_h_A_over_B"] = [
        {"h": h, "pred_law_A_per_bit": (ssum(A, low_mask_bits(h)) / (N_A_BITS * h)) / (ssum(B, low_mask_bits(h)) / (N_B_BITS * h)),
         "pred_law_W_per_bit": ((winf * (1 - math.exp(-ssum(A, low_mask_bits(h)) / winf)) / (N_A_BITS * h))
                               / (winf * (1 - math.exp(-ssum(B, low_mask_bits(h)) / winf)) / (N_B_BITS * h)))}
        for h in [1, 2, 4, 8, 12, 16] if h in LQ_H]

    # ---- the random-word anchors the ladders extrapolate to (E67's own measurements, for the closure)
    anc = e67["anchors"]
    out["anchors_E67"] = {k: {"W": anc[k]["p80"], "se": anc[k]["se"], "dW_vs_zero": anc[k].get("dW_vs_zero")}
                          for k in ("nrd_a", "nrd_b", "anchor_randn", "anchor_zeros", "lq_h0", "aq_h0") if k in anc}
    json.dump(out, open(a.out, "w"), indent=1)
    if a.print:
        print(f"Law W ceiling Winf = {winf:.2f} W (fit rms {rms:.3f} W on E60's {len(lq_prior)} lq rungs)")
        print(f"shared turn-on T from E67's grid = {T:.3f} +- {T_se:.3f} W; implied T over E60's lq rungs "
              f"{min(ts):.2f}..{max(ts):.2f} W")
        print()
        for kind in ("lq", "ls", "alq"):
            print(f"-- {kind}")
            for r in out[kind]:
                rep = f"  E60 {r['pred_replicate_E60_W']:.3f}" if "pred_replicate_E60_W" in r else ""
                print(f"  {r['item']:9s} h={r['h']:2d} bits={str(r['bits'])[:34]:34s} S={r['S_additive_W']:7.3f} "
                      f"A={r['pred_law_A_W']:7.3f} Hoff={r['pred_law_H_offset_W']:7.3f} W={r['pred_law_W_W']:6.3f}{rep}")
        print("\n-- D1 matched-h layout contrast (ls - lq)")
        for r in d1:
            print(f"  h={r['h']:2d}  S_ls-S_lq={r['S_difference_W']:7.3f}  law A/H-offset={r['pred_law_A_dW']:7.3f}  "
                  f"H-strong=0.000  law W={r['pred_law_W_dW']:6.3f}")
        print("\n-- carry-over prior:", json.dumps(out["carry_over_prior"]))
        print("-- D4 matched-h A/B per flipped bit:", json.dumps(out["D4_matched_h_A_over_B"]))


if __name__ == "__main__":
    main()
