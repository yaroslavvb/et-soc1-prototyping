#!/usr/bin/env python3
"""E72 frozen predictions: the same card's flip price at 600 MHz, from its own 800 MHz price.

    python3 tools/claims-v3/lq6/predict_e72.py --out tools/claims-v3/lq6/predictions.json

Everything here is derived from data already in the repo, so the file is reproducible and nothing is
typed in by hand:

  * E60 (`docs/reports/data/2026-10-20-bitflip-ladder/hl.json`), card `aifoundry2` at 800 MHz: this is
    THE SAME CARD E72 runs, so the V^2 test needs no card-to-card scale factor. E60 ran only lq_h0,
    lq_h2 and lq_h8 there (its departure D5: the higher rungs and the whole lb ladder pass the 65 W
    governor limit at 800 MHz), so its registered "slope" is the h2 -> h8 secant.
  * E60, card `aifoundry3` at 600 MHz: the SHAPE references - how much the full h >= 1 ladder slope
    exceeds the h2 -> h8 secant (the ladder is bent), and how much the busy ladder lb exceeds lq.
    Shapes travel across cards better than absolute watts; they are registered as ratios.

The law under test, per flipped B mantissa bit, is 1/2 C V^2: the ENERGY of a flip depends on the
voltage and not on the clock. The reducer divides the measured watts by the measured operation rate,
so the clock cancels and what is left must scale as V^2 alone:

    fJ_600 / fJ_800 = (V_600 / V_800) ^ 2                      (the registered hypothesis)

The alternative - the one E60's own decision rule named ("a ratio near 1.87 would mean the energy per
flip scaled with f too, i.e. it was not a flip") - predicts the ratio f*V^2 instead:

    fJ_600 / fJ_800 = (600/800) * (V_600 / V_800) ^ 2           (the alternative, to be refuted)

The two differ by exactly 600/800 = 0.75, which is far outside the band, so the cell discriminates.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E60 = os.path.join(ROOT, "docs/reports/data/2026-10-20-bitflip-ladder/hl.json")

# The voltage this card is expected to show at the 600 MHz vmin-LUT point, read fresh on 27 Oct 2026
# at 14:24 and 14:42 PDT by E69's `ettelem config` (minion_mv 519 at 600 MHz, idle). E60 read 521.775
# mV at the same nominal point on aifoundry3. The prediction is a FORMULA in V; this is the number it
# is evaluated at, and the reduction re-evaluates it at the voltage actually measured.
V600_EXPECTED = 0.519
V600_TOL = 0.003            # the reducer's own per-pass voltage gate is +-3 mV

BAND_FRAC = 0.10            # +-10% on the price predictions
BAND_SHAPE = 0.20           # +-0.20 absolute on the bend ratio
BAND_LB = 0.15              # +-0.15 absolute on the lb/lq ratio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--v600", type=float, default=V600_EXPECTED)
    a = ap.parse_args()

    hl = json.load(open(E60))
    a2 = hl["cards"]["aifoundry2"]
    a3 = hl["cards"]["aifoundry3"]

    v800 = a2["v_mean"]
    v600 = a.v600
    r_v2 = (v600 / v800) ** 2               # the registered law: energy per flip
    r_fv2 = (600.0 / 800.0) * r_v2          # the alternative: energy per flip scaled with f as well

    # --- this card's own 800 MHz price, board and rail (E60's registered estimator there) ----------
    lq800 = a2["lq"]["designed"]
    fJ800, fJ800_se = lq800["fJ"], lq800["se_J"] * 1e15
    rail800, rail800_se = lq800["rail_fJ"], lq800["rail_se_J"] * 1e15

    # --- the watts E60 measured on this card at 800 MHz, for the rung-by-rung predictions ----------
    w800 = {k: a2["items"][k]["d_p80"] for k in ("lq_h2", "lq_h8")}
    # the straight line through those two rungs, scaled to 600 MHz by f*V^2 (watts DO carry the clock)
    slope600 = (w800["lq_h8"] - w800["lq_h2"]) / 6.0 * r_fv2
    icept600 = w800["lq_h2"] * r_fv2 - 2 * slope600

    # --- shapes from E60's own 600 MHz card (aifoundry3) ------------------------------------------
    lq3_full = a3["lq"]["designed"]["fJ"]                       # full h >= 1 ladder slope
    lq3_sec = a3["lq_h2_h8_J"] * 1e15 if "lq_h2_h8_J" in a3 else hl["v2"]["aifoundry3"]["lq_h2_h8_J"] * 1e15
    bend3 = lq3_full / lq3_sec
    lb3_over_lq3 = a3["lb"]["designed"]["fJ"] / lq3_full
    turnon3 = a3["lb"]["first_flip_W"]["W"] / a3["lq"]["first_flip_W"]["W"]

    pred_sec = fJ800 * r_v2
    pred_full = pred_sec * bend3
    pred_lb = pred_full * lb3_over_lq3

    def band(x, frac=BAND_FRAC):
        return [round(x * (1 - frac), 4), round(x * (1 + frac), 4)]

    out = {
        "experiment": "E72",
        "what": "the same card's price per flipped B mantissa bit at 600 MHz (governor pinned by TDP 0)",
        "card": "aifoundry2 card 0",
        "frozen_utc": None,          # filled by the committer; the commit hash is the real freeze
        "reference": {
            "e60_hl_json": "docs/reports/data/2026-10-20-bitflip-ladder/hl.json",
            "e60_aifoundry2_800MHz": {
                "v_mean": v800, "clock_mhz": a2["clock_mhz"], "passes": len(a2["passes"]),
                "lq_fJ_per_designed_bit": fJ800, "lq_fJ_se": fJ800_se,
                "lq_rail_fJ_per_designed_bit": rail800, "lq_rail_fJ_se": rail800_se,
                "estimator": "h2 -> h8 secant (only lq_h0/h2/h8 were run there: E60 departure D5)",
                "leak_W_per_C_fitted_there": a2.get("leak_W_per_C"),
                "d_p80_W": w800,
            },
            "e60_aifoundry3_600MHz_shapes": {
                "lq_full_ladder_fJ": lq3_full, "lq_h2_h8_secant_fJ": lq3_sec,
                "bend_full_over_secant": bend3,
                "lb_over_lq_full_ladder": lb3_over_lq3,
                "lb_h1_over_lq_h1_turnon_W": turnon3,
            },
        },
        "voltages": {"v800_measured_e60": v800, "v600_expected": v600, "v600_tol": V600_TOL,
                     "ratio_v2": r_v2, "ratio_f_times_v2": r_fv2},
        "rules": {
            "V1": {
                "claim": "the price per flipped mantissa bit at 600 MHz equals this card's own 800 MHz "
                         "price times (V600/V800)^2 - the flip's energy follows the voltage, not the clock",
                "quantity": "lq h2 -> h8 secant, board, fJ per designed flipped bit",
                "predicted": round(pred_sec, 3), "band": band(pred_sec),
                "alternative_if_it_scaled_with_f_too": round(fJ800 * r_fv2, 3),
                "pass_if": "measured inside the band AND outside the alternative's own +-10% band",
            },
            "V2": {
                "claim": "the same on the minion rail",
                "quantity": "lq h2 -> h8 secant, minion rail, fJ per designed flipped bit",
                "predicted": round(rail800 * r_v2, 3), "band": band(rail800 * r_v2, 0.15),
                "pass_if": "measured inside the band",
            },
            "V3": {
                "claim": "the watts of each rung scale as f*V^2 (the clock is in the watts, not in the "
                         "energy): the line through this card's own 800 MHz lq_h2 and lq_h8",
                "quantity": "d_p80 (W over lq_h0) at 600 MHz",
                "predicted_W": {f"lq_h{h}": round(icept600 + slope600 * h, 4) for h in (1, 2, 4, 8)},
                "band_frac": BAND_FRAC,
                "pass_if": "lq_h2 and lq_h8 inside +-10%; h1 and h4 are reported, not scored "
                           "(E60 never ran them on this card, so their line is an interpolation)",
            },
            "V4": {
                "claim": "the ladder is bent the same way as on E60's 600 MHz card: the full h >= 1 "
                         "slope exceeds the h2 -> h8 secant",
                "quantity": "(full-ladder slope) / (h2 -> h8 secant), board",
                "predicted": round(bend3, 4), "band": [round(bend3 - BAND_SHAPE, 4), round(bend3 + BAND_SHAPE, 4)],
                "and_so_full_ladder_fJ": round(pred_full, 3), "full_ladder_band": band(pred_full, 0.15),
                "pass_if": "the ratio is inside the band",
            },
            "V5": {
                "claim": "the busy ladder lb - which this card cannot run at 800 MHz at all - costs more "
                         "per bit than lq, by the factor E60 measured at 600 MHz on the other card",
                "quantity": "lb full-ladder slope / lq full-ladder slope, board",
                "predicted": round(lb3_over_lq3, 4),
                "band": [round(lb3_over_lq3 - BAND_LB, 4), round(lb3_over_lq3 + BAND_LB, 4)],
                "and_so_lb_fJ": round(pred_lb, 3), "lb_band": band(pred_lb, 0.15),
                "pass_if": "the ratio is inside the band",
            },
            "V6": {
                "claim": "the turn-on (the first flipped bit, which wakes the multiplier tree) is dearer "
                         "with a busy partner, by about the factor E60 measured at 600 MHz",
                "quantity": "lb_h1 / lq_h1 in watts over their own zeros",
                "predicted": round(turnon3, 3), "band": [round(turnon3 * 0.6, 3), round(turnon3 * 1.4, 3)],
                "pass_if": "the ratio is inside the band",
            },
            "G1": {
                "claim": "the governor is pinned: TDP 0 means the power-down branch fires on any load and "
                         "the power-up branch can never fire, so the clock never leaves the vmin-LUT floor",
                "quantity": "every telemetry sample of every launch, and the governor's own log",
                "predicted": "600 MHz in 100% of samples; zero 'Power throttle up' lines while TDP 0 is set",
                "pass_if": "exactly that, with no sample at any other clock",
            },
            "G2": {
                "claim": "the voltage at the pinned point is the LUT's 600 MHz voltage",
                "predicted": v600, "band": [v600 - V600_TOL, v600 + V600_TOL],
                "pass_if": "the mean measured minion voltage is inside the band",
            },
            "G3": {
                "claim": "restore: both governor fields read back at their originals and the card steps "
                         "normally afterwards",
                "predicted": "TDP 65 W, software threshold 65 C, and a post-restore burst that reaches "
                             ">= 700 MHz with at least one 'Power throttle up' event",
                "pass_if": "exactly that",
            },
        },
        "leak_slopes_reported": {
            "registered": "auto (reduce_hl.py's own within-run fit, as E60 and E68 registered it)",
            "e66_measured": 0.2936,
            "e60_fitted_on_this_card": a2.get("leak_W_per_C"),
            "note": "the price is a difference between two rungs in the same pass, so the leakage slope "
                    "enters only through the small difference in within-run heating between rungs; all "
                    "three are reported and the registered one is the verdict",
        },
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
        f.write("\n")
    print(json.dumps({k: out["rules"][k].get("predicted") for k in out["rules"]}, indent=1))
    print(f"V800={v800:.6f} V600={v600:.3f} ratio_V2={r_v2:.5f} ratio_fV2={r_fv2:.5f}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
