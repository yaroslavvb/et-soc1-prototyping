#!/usr/bin/env python3
"""Q140(c) check 4 (post hoc, desk only; nothing registered): the die's rise over pool 6's 4.5 s runs, predicted from the bits
(M7's heat law carried in M8, on each model's predicted power), against simple baselines that never see a bit.

    python3 -I -B check4_heat_constant.py <lab repo root> --out check4-heat-constant.json > check4-heat-constant.txt

Standard library only. Inputs (committed, read only): E154's scored.json (holds.*.E_end_to_end.plateau_err_C, for its session interval), E153's scored.json (aifoundry3, primary.primary.heat_rows and
power_rows) and E157's scored.json (card 1, primary.heat_rows and power_rows); the registered set is pool 6's 30 priority-1
new kinds (anchors out), as E153-H1..H3 and E157-H1..H3 score them.

Baselines, per card and format (each fitted on the very tiles it is scored on, so each is generous to itself):
  * a constant: the format's mean measured rise (its rms is the rises' sd);
  * the same constant left one tile out (each tile scored against the mean of the others);
  * a rise proportional to the tile's MEASURED D, one slope per format through the origin (a perfect power prediction
    with a fitted slope: what is left is the heat law's shape and the readout);
and the readout floor: the rms over tiles of each tile's sd over its passes / sqrt(n passes) (whole-degree die readings).
For int8 it also reports how many rises read exactly 1.00 C and each model's rms on those tiles against the constant 1.00,
and the two lowest-power tiles' errors.
"""
import argparse
import json
import math
import os

E153 = "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/scored.json"
E157 = "docs/reports/data/2026-11-03-e157-blind6-card1/scored.json"
E154 = "docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/scored.json"
MODELS = ("M8", "M7", "M6")
FORMATS = ("fp32", "fp16", "int8")


def rms(e):
    return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


def chi2_cdf_4df(x):
    """The chi-square CDF at 4 degrees of freedom, closed form."""
    return 1.0 - math.exp(-x / 2.0) * (1.0 + x / 2.0)


def chi2_q_4df(p):
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if chi2_cdf_4df(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    src = {"aifoundry3": json.load(open(os.path.join(root, E153)))["primary"]["primary"],
           "aifoundry1c1": json.load(open(os.path.join(root, E157)))["primary"]}
    out = {"_note": "Q140(c) check 4: post hoc desk check, nothing registered. Pool 6's 4.5 s die rises (priority 1, anchors out) from the bits against baselines.",
           "inputs": {"aifoundry3": E153 + " primary.primary.heat_rows, power_rows", "aifoundry1c1": E157 + " primary.heat_rows, power_rows"}}
    L = ["CHECK 4. THE 4.5 s RISE FROM THE BITS AGAINST BASELINES THAT NEVER SEE A BIT (post hoc; C rms of measured - predicted)"]
    for card, X in src.items():
        H, P = X["heat_rows"], X["power_rows"]["M8"]
        res = {}
        L.append("")
        L.append(f"  {card}:")
        for t in FORMATS:
            ns = sorted((n for n, v in H["M8"].items() if v["priority"] == 1 and not v["pool_anchor"] and v["type"] == t), key=lambda n: P[n]["measured"])
            y = [H["M8"][n]["measured"] for n in ns]
            D = [P[n]["measured"] for n in ns]
            k = len(ns)
            mu = sum(y) / k
            const = rms([v - mu for v in y])
            loo = rms([y[i] - (sum(y) - y[i]) / (k - 1) for i in range(k)])
            slope = sum(d * v for d, v in zip(D, y)) / sum(d * d for d in D)
            prop = rms([v - slope * d for d, v in zip(D, y)])
            floor = rms([H["M8"][n]["sd"] / math.sqrt(H["M8"][n]["n_passes"]) for n in ns])
            mod = {m: rms([H[m][n]["measured"] - H[m][n]["pred"] for n in ns]) for m in MODELS}
            r = {"n": k, "tiles_by_power": ns, "measured_rise_c": y, "measured_D_w": D, "model_rms_c": mod, "constant_rms_c": const,
                 "constant_value_c": mu, "constant_loo_rms_c": loo, "proportional_to_measured_D_rms_c": prop,
                 "proportional_slope_c_per_w": slope, "readout_floor_c": floor}
            line = (f"    {t} ({k}): M8 / M7 / M6 {mod['M8']:.3f} / {mod['M7']:.3f} / {mod['M6']:.3f}; constant {const:.3f} (LOO {loo:.3f}); "
                    f"proportional to measured D {prop:.3f} ({slope:.4f} C/W); readout floor {floor:.3f}")
            if t == "int8":
                ones = [n for n, v in zip(ns, y) if abs(v - 1.0) < 1e-9]
                low2 = ns[:2]
                r["n_exactly_1C"] = len(ones)
                r["tiles_exactly_1C"] = ones
                r["model_rms_on_exactly_1C_tiles_c"] = {m: rms([H[m][n]["measured"] - H[m][n]["pred"] for n in ones]) for m in MODELS} if ones else None
                r["constant_1C_rms_on_those_c"] = 0.0 if ones else None
                r["two_lowest_power"] = {n: {"D_w": P[n]["measured"], "rise_c": H["M8"][n]["measured"],
                                             **{f"{m}_err_c": H[m][n]["measured"] - H[m][n]["pred"] for m in MODELS},
                                             "constant_err_c": H["M8"][n]["measured"] - mu} for n in low2}
                rest = [n for n in ns if n not in low2]
                r["without_two_lowest"] = {"n": len(rest), "model_rms_c": {m: rms([H[m][n]["measured"] - H[m][n]["pred"] for n in rest]) for m in MODELS},
                                           "constant_rms_c": rms([H["M8"][n]["measured"] - sum(H["M8"][q]["measured"] for q in rest) / len(rest) for n in rest])}
                line += (f"\n        {len(ones)} of {k} read exactly 1.00 C; on those, M8 / M7 / M6 "
                         + (" / ".join(f"{r['model_rms_on_exactly_1C_tiles_c'][m]:.3f}" for m in MODELS) if ones else "n/a")
                         + " against the constant 1.00's 0.000"
                         + f"\n        without the two lowest-power tiles ({', '.join(low2)}): M8 / M7 / M6 "
                         + " / ".join(f"{r['without_two_lowest']['model_rms_c'][m]:.3f}" for m in MODELS)
                         + f" against a constant's {r['without_two_lowest']['constant_rms_c']:.3f}"
                         + "\n        the two: " + "; ".join(f"{n} D {v['D_w']:.2f} W rise {v['rise_c']:.3f} C, M8 {v['M8_err_c']:+.3f}, constant {v['constant_err_c']:+.3f}" for n, v in r["two_lowest_power"].items()))
            res[t] = r
            L.append(line)
        out[card] = res
    # E154's session figure: four plateau errors, an interval on the sigma (chi-square at 4 df, zero-mean errors assumed)
    S = json.load(open(os.path.join(root, E154)))
    errs = {h: v["E_end_to_end"]["plateau_err_C"] for h, v in S["holds"].items() if (v.get("E_end_to_end") or {}).get("plateau_err_C") is not None}
    r = rms(list(errs.values()))
    k = len(errs)
    assert k == 4
    lo, hi = r * math.sqrt(k / chi2_q_4df(0.975)), r * math.sqrt(k / chi2_q_4df(0.025))
    out["E154_session"] = {"plateau_err_C": errs, "rms_c": r, "committed_rms_c": S["session_figure"]["rms_plateau_err_C"]["E_M8"],
                           "sigma_95_chi2_4df_c": [lo, hi]}
    L.append("")
    L.append(f"  E154 (heat over minutes, aifoundry3, four pool-6 holds): plateau errors {', '.join(f'{h} {v:+.3f}' for h, v in errs.items())} C; rms {r:.3f} C "
             f"(committed {S['session_figure']['rms_plateau_err_C']['E_M8']}); 95% interval on the sigma at 4 df [{lo:.2f}, {hi:.2f}] C")
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    print("\n".join(L))


if __name__ == "__main__":
    main()
