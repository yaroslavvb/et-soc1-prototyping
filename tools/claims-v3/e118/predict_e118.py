#!/usr/bin/env python3
"""E118 frozen predictions: E72's two-clock price on a second card, aifoundry1 card 0, from its own 800 MHz price.

    python3 tools/claims-v3/e118/predict_e118.py --out tools/claims-v3/e118/predictions.json

Everything is derived from committed data; nothing is typed in by hand except the expected 600 MHz voltage and the
bands (E72's). E72 (27 Oct, aifoundry2) is the design: the same card at 600 MHz (static TDP 0, the vmin-LUT floor)
against its own 800 MHz rows, the same operand bytes and E60's reducer, so the card factor is 1 by construction.

  * The 800 MHz reference is card 0's own E60 rows (20 Oct; `docs/reports/data/2026-10-20-bitflip-ladder/`, card
    `aifoundry1-c0`, 10 passes, lq_h0 / lq_h2 / lq_h8 only, so its per-designed-bit slope IS the h2 -> h8 secant).
  * The no-PMIC-read profile moves the voltage source from `die_mv.minion` (PVT, from GET_ASIC_VOLTAGE, which reads
    PMIC registers) to `sp.minion_mv[0]` (SP statistics). This tool re-reduces E60's card-0 passes in BOTH sources and
    freezes the numbers in the sp source; it fails if the two disagree by more than 0.5 mV or keep different runs.
  * V600 expected: 0.519 V. Card 0 read 519 mV at 600 MHz on 31 Oct in both sources (E84: `ettelem config`
    minion_mv 519, PVT, ident/ident-154200.out; its sampler's sp.minion_mv avg 519 at 600 MHz, s1/tel). The
    prediction is a FORMULA in V; the scorer re-evaluates it at the voltage the pinned passes measure (E72 C2).
  * V1m, the primary form (E72's correction C2): the same V^2 test with BOTH sides reduced at the same leakage slope,
    on a fixed pass set, at the registered slope set {0, E60's own auto fit on this card}.
  * Shapes (V4-V6) come from the two cards already measured at 600 MHz with the same rungs: E72 (aifoundry2) and
    E60 (aifoundry3); the prediction is their mean, the bands E72's.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E60D = os.path.join(ROOT, "docs/reports/data/2026-10-20-bitflip-ladder")
E72D = os.path.join(ROOT, "docs/reports/data/2026-10-27-e72-600mhz")
CARD = "aifoundry1-c0"
V600_EXPECTED = 0.519
V600_TOL = 0.003
H2, H8 = 8192, 32768
BAND = 0.10
PY = sys.executable


def reduce(dirs, leak, src, tmp, tag):
    gen = os.path.join(tmp, "gen")
    os.makedirs(gen, exist_ok=True)
    shutil.copy(os.path.join(E60D, "manifest-a1.json"), os.path.join(gen, "manifest.json"))
    out = os.path.join(tmp, f"{tag}.json")
    csvp = os.path.join(tmp, f"{tag}.csv")
    if src == "sp":
        cmd = [PY, os.path.join(HERE, "reduce_e118.py"), *dirs, "--gen", gen, "--pred", os.path.join(E60D, "predictions.json"),
               "--out", out, "--csv", csvp, "--leak", str(leak), "--free"]
    else:
        cmd = [PY, os.path.join(ROOT, "tools/claims-v3/hl/reduce_hl.py"), *dirs, "--gen", gen, "--pred",
               os.path.join(E60D, "predictions.json"), "--out", out, "--csv", csvp, "--leak", str(leak)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"reduction {tag} failed: {r.stderr[-800:]}")
    return json.load(open(out)), csvp


def secant(c):
    it = c["items"]
    return (it["lq_h8"]["d_p80"] - it["lq_h2"]["d_p80"]) / ((H8 - H2) * it["lq_h8"]["rate"]) * 1e15


def kept_passes(res):
    return sorted(res["cards"][CARD]["passes"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    hl = json.load(open(os.path.join(E60D, "hl.json")))
    pub = hl["cards"][CARD]
    k_auto = hl["gates"][CARD]["leak_W_per_C"]
    passes = [os.path.join(E60D, CARD, "hl", f"p{p}") for p in range(1, 11)]
    tmp = tempfile.mkdtemp(prefix="e118-predict-")
    try:
        die_auto, _ = reduce(passes, "auto", "die", tmp, "die-auto")
        sp_auto, _ = reduce(passes, "auto", "sp", tmp, "sp-auto")
        cd, cs = die_auto["cards"][CARD], sp_auto["cards"][CARD]
        same_runs = die_auto["gates"][CARD]["kept"] == sp_auto["gates"][CARD]["kept"] and kept_passes(die_auto) == kept_passes(sp_auto)
        dv = abs(cd["v_mean"] - cs["v_mean"]) * 1000
        if dv > 0.5 or not same_runs:
            raise SystemExit(f"the two voltage sources disagree on E60's card-0 passes: {dv:.3f} mV, same runs {same_runs}")
        if abs(cs["lq"]["designed"]["fJ"] - pub["lq"]["designed"]["fJ"]) > 1e-6:
            raise SystemExit("the sp-source reduction does not reproduce E60's published card-0 price")
        v800 = cs["v_mean"]
        fJ800, se800 = cs["lq"]["designed"]["fJ"], cs["lq"]["designed"]["se_J"] * 1e15
        rail800 = cs["lq"]["designed"]["rail_fJ"]
        w800 = {k: cs["items"][k]["d_p80"] for k in ("lq_h2", "lq_h8")}
        sec800_auto = secant(cs)
        # V1m: E60's card-0 secant at each registered slope, on the passes kept at EVERY registered slope
        slopes = [0.0, round(k_auto, 6)]
        first = {k: reduce(passes, k, "sp", tmp, f"sp-k{k}")[0] for k in slopes}
        inter = sorted(set.intersection(*[set(kept_passes(first[k])) for k in slopes]))
        fixed = [os.path.join(E60D, CARD, "hl", f"p{p}") for p in inter]
        matched = {}
        for k in slopes:
            res, _ = reduce(fixed, k, "sp", tmp, f"sp-fixed-k{k}")
            matched[str(k)] = {"secant_fJ": secant(res["cards"][CARD]), "passes": kept_passes(res),
                               "designed_fJ": res["cards"][CARD]["lq"]["designed"]["fJ"],
                               "designed_se_fJ": res["cards"][CARD]["lq"]["designed"]["se_J"] * 1e15}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    v600 = V600_EXPECTED
    r_v2 = (v600 / v800) ** 2
    r_fv2 = 0.75 * r_v2
    e72 = json.load(open(os.path.join(E72D, "results.json")))["cards"]["aifoundry2"]
    e72v = json.load(open(os.path.join(E72D, "verdicts.json")))["rules"]
    a3 = hl["cards"]["aifoundry3"]
    bend = {"e72_aifoundry2": e72v["V4"]["measured"], "e60_aifoundry3": a3["lq"]["designed"]["fJ"] / (hl["v2"]["aifoundry3"]["lq_h2_h8_J"] * 1e15) if "v2" in hl and "lq_h2_h8_J" in hl["v2"].get("aifoundry3", {}) else e72v["V4"]["predicted"]}
    lbq = {"e72_aifoundry2": e72["lb"]["designed"]["fJ"] / e72["lq"]["designed"]["fJ"], "e60_aifoundry3": a3["lb"]["designed"]["fJ"] / a3["lq"]["designed"]["fJ"]}
    ton = {"e72_aifoundry2": e72["lb"]["first_flip_W"]["W"] / e72["lq"]["first_flip_W"]["W"],
           "e60_aifoundry3": a3["lb"]["first_flip_W"]["W"] / a3["lq"]["first_flip_W"]["W"]}
    mean = lambda d: sum(d.values()) / len(d)

    def band(x, f=BAND):
        return [round(x * (1 - f), 4), round(x * (1 + f), 4)]

    v1 = fJ800 * r_v2
    out = {
        "experiment": "E118",
        "what": "aifoundry1 card 0's price per flipped B mantissa bit at 600 MHz (static TDP 0) against its own 800 MHz",
        "card": "aifoundry1 card 0 (PCI 0000:01:00.0, /dev/et0_*)",
        "telemetry_profile": "no-PMIC-read: sampler and config without GET_ASIC_VOLTAGE / GET_MODULE_VOLTAGE; voltages from sp.minion_mv[0]",
        "reference": {
            "e60_card0_800MHz": {"data": "docs/reports/data/2026-10-20-bitflip-ladder/ (aifoundry1-c0, hl/p1-p10)",
                                 "v_mean_sp": v800, "v_mean_die": cd["v_mean"], "v_sources_differ_mV": dv,
                                 "runs_kept": sp_auto["gates"][CARD]["kept"], "passes": kept_passes(sp_auto),
                                 "lq_fJ_per_designed_bit": fJ800, "lq_fJ_se": se800, "lq_rail_fJ": rail800,
                                 "lq_h2_h8_secant_fJ": sec800_auto, "leak_auto_W_per_C": k_auto, "d_p80_W": w800,
                                 "note": "only lq_h0/h2/h8 ran on this card at 800 MHz, so the per-designed-bit slope is the h2 -> h8 secant"},
            "shapes_600MHz": {"bend_full_over_secant": bend, "lb_over_lq_full": lbq, "turnon_lb_h1_over_lq_h1": ton},
        },
        "voltages": {"v800_sp": v800, "v600_expected": v600, "v600_tol": V600_TOL, "ratio_v2": r_v2,
                     "ratio_f_times_v2": r_fv2, "source": "sp.minion_mv[0] on both sides"},
        "rules": {
            "V1": {"claim": "the 600 MHz price per flipped mantissa bit = card 0's own 800 MHz price x (V600/V800)^2: "
                            "the flip's energy follows the voltage, not the clock (E72's registered form)",
                   "quantity": "lq h2 -> h8 secant, board, fJ per designed flipped bit, registered leak auto",
                   "predicted": round(v1, 3), "band": band(v1),
                   "alternative": round(v1 * 0.75, 3), "alternative_band": band(v1 * 0.75),
                   "pass_if": "inside the band AND outside the alternative's band; inside both = INCONCLUSIVE"},
            "V1m": {"claim": "PRIMARY. The same test with both sides reduced at the same leakage slope on fixed pass sets "
                             "(E72 correction C2)",
                    "slopes_W_per_C": slopes, "e60_fixed_passes": inter, "e60_matched": matched,
                    "predicted": {str(k): round(matched[str(k)]["secant_fJ"] * r_v2, 3) for k in slopes},
                    "band": {str(k): band(matched[str(k)]["secant_fJ"] * r_v2) for k in slopes},
                    "pass_if": "E118's secant at each registered slope (on E118's passes kept at both) inside that "
                               "slope's band: PASS at both, PARTIAL at one, FAIL at neither; re-evaluated at the measured V600"},
            "V2": {"claim": "the same on the minion rail (uncorrected, E72's caveat)", "predicted": round(rail800 * r_v2, 3),
                   "band": band(rail800 * r_v2, 0.15), "pass_if": "inside"},
            "V3": {"claim": "the watts of a rung scale as f*V^2 (the clock is in the watts)",
                   "predicted_W": {"lq_h2": round(w800["lq_h2"] * r_fv2, 4), "lq_h8": round(w800["lq_h8"] * r_fv2, 4)},
                   "band_frac": BAND, "pass_if": "both inside +-10% (E72 missed lq_h2 by 12.2%)"},
            "V4": {"claim": "the ladder bends as on the two cards measured at 600 MHz", "predicted": round(mean(bend), 4),
                   "band": [round(mean(bend) - 0.20, 4), round(mean(bend) + 0.20, 4)],
                   "quantity": "full h >= 1 slope / h2 -> h8 secant, board", "pass_if": "inside"},
            "V5": {"claim": "the busy ladder costs more per bit than lq by the two cards' factor", "predicted": round(mean(lbq), 4),
                   "band": [round(mean(lbq) - 0.15, 4), round(mean(lbq) + 0.15, 4)], "quantity": "lb full slope / lq full slope",
                   "pass_if": "inside"},
            "V6": {"claim": "the turn-on is dearer with a busy partner", "predicted": round(mean(ton), 3),
                   "band": [round(mean(ton) * 0.6, 3), round(mean(ton) * 1.4, 3)], "quantity": "lb_h1 / lq_h1 in watts over their zeros",
                   "pass_if": "inside"},
            "C1": {"claim": "the same-session 800 MHz control agrees with E60's 20 Oct rows on this card",
                   "predicted_W": {"lq_h2": round(w800["lq_h2"], 4), "lq_h8": round(w800["lq_h8"], 4)}, "band_frac": BAND,
                   "pass_if": "both d_p80 inside +-10%; else V1 is also reported against today's control, said so"},
            "G1": {"claim": "the pin: TDP 0 holds the clock at the vmin-LUT floor",
                   "predicted": "600 MHz in 100% of samples of every pinned launch; zero 'Power throttle up' events in the SP ring between the dump before the pin and the dump after the last pinned pass",
                   "pass_if": "both halves; a ring that wrapped between the dumps leaves the log half UNMEASURED (not PASS)"},
            "G2": {"claim": "the pinned voltage is the LUT's 600 MHz point", "predicted": v600,
                   "band": [round(v600 - V600_TOL, 3), round(v600 + V600_TOL, 3)], "quantity": "mean sp.minion_mv[0] of the kept pinned runs",
                   "pass_if": "inside"},
            "G3": {"claim": "the restore", "predicted": "TDP 65 W and threshold 65 C read back; the return burst reaches >= 700 MHz; >= 1 'Power throttle up' event in the ring between the dump after the pinned passes and the dump after the return burst",
                   "pass_if": "all three halves"},
            "V1s": {"claim": "REPORTED, NOT SCORED: V1 against today's 800 MHz control instead of E60's rows",
                    "quantity": "E118 600 MHz secant / E118 800 MHz control secant vs (V600/V800_session)^2"},
        },
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"V800 sp {v800*1000:.3f} mV (die {cd['v_mean']*1000:.3f}); fJ800 {fJ800:.3f} +- {se800:.3f}; secant {sec800_auto:.3f}")
    print(f"V1 {v1:.3f} band {band(v1)}; alt {v1*0.75:.3f} {band(v1*0.75)}")
    print("V1m", out["rules"]["V1m"]["predicted"], "fixed passes", inter)
    print("V2", out["rules"]["V2"]["predicted"], "V3", out["rules"]["V3"]["predicted_W"], "V4", out["rules"]["V4"]["predicted"],
          "V5", out["rules"]["V5"]["predicted"], "V6", out["rules"]["V6"]["predicted"], "C1", out["rules"]["C1"]["predicted_W"])
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
