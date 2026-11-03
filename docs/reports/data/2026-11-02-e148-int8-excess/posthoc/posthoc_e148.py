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
Standard library only. SPDX-License-Identifier: Apache-2.0"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
T95 = {9: 2.262}


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
    json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
