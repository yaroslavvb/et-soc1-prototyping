#!/usr/bin/env python3
"""Pin the operand-bus price to E60/E61's measured read-port bit and refit. Q128(e), 26 Oct 2026.

    /usr/local/bin/python3.12 pin_bus_fit.py            # writes pin_bus.json beside scores.json

Recap item 10 ("transport carries most of a flipped bit's energy and is the least pinned term") ends in one
step: *pin the bus term to E60's measured read-port price instead of letting it float, and see whether the
per-card spread collapses.* Q126 shipped `--pin-bus` in `load_model.flip_w()` and `predict_load.py`, but no
scored fit ever used it. This runs the fit.

WHAT IS PINNED. `K.e_readport` = 20.83 fJ, E60's measured register-file read-port bit (E61's separate build
reads 20.70). In the free fit the `bus` column is a free parameter; here its contribution is subtracted into
the per-pattern target and only `ffclk`, `mult` and `rest` are fitted. Three parameters, not four.

TWO BASES. The design matrix has four (or three) flip-rate columns and NO constant column, so the per-kernel
offset c0 put into `base` is NOT absorbed -- see `load_model.refit_prices`. Both bases are reported: c0 = 0
(what the published 21 Sep prices were fitted on) and c0 = -1.18 W (the joined model's offset).

TWO POPULATIONS.
  * `fp32_14`  -- the 21 Sep board table on aifoundry2 (`score_load_predictions.MEAS14`), the one committed
                  set of 14 measured fp32 patterns. This is the headline fit, and the free arm reproduces
                  scores.json's `fp32_14_patterns` exactly (asserted below).
  * `per_card` -- the version-3 check of 26 Sep (`2026-09-25-claims-v3/results/abla.runs.json`), the only
                  committed set of board powers measured on more than one card: aifoundry2, aifoundry3 and
                  aifoundry1's card 1, each over ABL-R's own 14 rows (8 fp32 patterns + 6 structured
                  matrices, `tools/claims-v3/abla/reduce.py:FLIP_ROWS`), 4 kept busy runs each, 1,024 minions
                  at 600 MHz, counts from `toggles_all.json` as ABL-R reads them. Each card is fitted on its
                  own measured idle (`p_before`) and its own measured rail (`busy_mv`), so the prices are
                  referred to 0.517 V and the per-card spread is the card's own, not the rail's.

  The published per-card fit, ABL-R `refit_p80` in `abla.json`, is carried alongside for context. It is a
  DIFFERENT fit -- non-negative least squares with a FREE constant, so its bus price cannot go below zero and
  its constant absorbs the idle -- and its bus term is the 30.56 / 28.03 / 32.79 fJ the recap calls loose.
  The arms here keep load_model's convention instead (fixed base, no constant column, signed prices), which
  is what the headline 14-pattern fit uses and what `--pin-bus` plugs into.

  🛑 The three cards launched at different die temperatures (80.9 / 55.8 / 80.9 C registered). Switching is
  measured against each card's own idle at the same temperature, so each card's fit is internally matched, but
  the across-card comparison still carries that difference. It carries it IDENTICALLY in the free and the
  pinned arm, so the question this file answers -- does pinning collapse the spread -- is unaffected.

WHAT COMES OUT. For each population and base: the fitted prices, in-sample rms and bias, leave-one-out rms and
bias (E38's protocol: refit without one pattern, predict it), and for `per_card` the min/max/ratio of every
price across the three cards, free against pinned.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load_model as LM                      # noqa: E402
import score_load_predictions as SLP         # noqa: E402

OUT = os.path.join(LM.DATA, "2026-10-26-load-model", "pin_bus.json")
BASES = [0.0, LM.STATIC["c0_w"]]             # 0.0 and -1.18
E_BUS_PINNED = LM.K.e_readport * 1e15        # 20.83 fJ
CLASSES = list(LM.CLASSES)                   # ffclk, mult, rest, bus

# ABL-R's own 14 rows: 8 fp32 patterns + 6 structured matrices (tools/claims-v3/abla/reduce.py:FLIP_ROWS),
# the only rows the version-3 check measured on all three cards AND the 21 Sep bench counted.
V3_ROWS = [("fp32_zeros", "zeros"), ("fp32_ones", "ones"), ("fp32_randn", "randn"), ("fp32_signs", "signs"),
           ("fp32_pow2", "pow2"), ("fp32_mant", "mant"), ("fp32_arb1", "a_randn_b_ones"),
           ("fp32_a1br", "a_ones_b_randn"), ("m_negzero", "negzero"), ("m_fft_cos", "fft_cos"),
           ("m_butterfly", "butterfly"), ("m_hadamard", "hadamard"), ("m_relu", "relu"),
           ("m_kaleidoscope", "kaleidoscope")]
TOG_ALL = json.load(open(os.path.join(LM.D21, "toggles_all.json")))


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else float("nan")


def design_row(pattern, volts, active=1024, f_mhz=600.0, tog=None):
    """The four flip-rate columns, in the same currency load_model.refit_prices uses (fJ -> W)."""
    f = LM.flips_from_toggles(SLP.TOG if tog is None else tog, pattern)
    r = LM.F_OP * (f_mhz / 600.0) * active * (volts / LM.V_REF) ** 2 / 1e15
    return [f[c] * r for c in CLASSES]


def fit(patterns, measured_w, idle_w, c0, volts, pin_bus, tog=None):
    """One fit. `pin_bus` fixes the bus price at E60's read-port bit and fits the other three.

    With the bus pinned, its column is moved out of the design matrix and into the target, which is the only
    honest way to hold a price fixed in a model with no constant column: a pinned term is a known watt per
    pattern, not a prior on a free one.
    """
    A4 = [design_row(p, volts, tog=tog) for p in patterns]
    base = c0 + LM.K.p_sm + idle_w
    ib = CLASSES.index("bus")
    free = [i for i in range(len(CLASSES)) if not (pin_bus and i == ib)]

    def target(i):
        t = measured_w[patterns[i]] - base
        return t - (A4[i][ib] * E_BUS_PINNED if pin_bus else 0.0)

    A = [[A4[i][j] for j in free] for i in range(len(patterns))]
    b = [target(i) for i in range(len(patterns))]

    def prices(coeffs):
        e = dict(zip([CLASSES[j] for j in free], coeffs))
        if pin_bus:
            e["bus"] = E_BUS_PINNED
        return {c: e[c] for c in CLASSES}

    def predict(i, coeffs):
        return sum(A[i][k] * coeffs[k] for k in range(len(free))) + \
            (A4[i][ib] * E_BUS_PINNED if pin_bus else 0.0) + base

    e = LM._lsq(A, b)
    ins = [predict(i, e) - measured_w[patterns[i]] for i in range(len(patterns))]
    loo = []
    for i in range(len(patterns)):
        ei = LM._lsq([A[j] for j in range(len(patterns)) if j != i],
                     [b[j] for j in range(len(patterns)) if j != i])
        loo.append(predict(i, ei) - measured_w[patterns[i]])
    worst = max(range(len(loo)), key=lambda i: abs(loo[i]))
    return {"pin_bus": pin_bus, "kernel_offset_w": c0, "base_w": base, "volts": volts,
            "n_patterns": len(patterns), "n_free_parameters": len(free),
            "prices_fJ": prices(e),
            "in_sample_rms_w": rms(ins), "in_sample_bias_w": sum(ins) / len(ins),
            "leave_one_out_rms_w": rms(loo), "leave_one_out_bias_w": sum(loo) / len(loo),
            "leave_one_out_worst": {"pattern": patterns[worst], "err_w": loo[worst]},
            "residuals_w": dict(zip(patterns, ins))}


# ------------------------------------------------------------------ the 14 fp32 patterns, aifoundry2, 21 Sep
def fp32_14():
    pats = list(SLP.MEAS14)
    out = {"source": "docs/findings/10-data-dependent-power.md table (E17/21 Sep, aifoundry2, 600 MHz, "
                     "1,024 minions); idle 36.29 W, the measured idle just before each launch",
           "patterns": pats, "idle_w": SLP.IDLE21, "arms": {}}
    for pin in (False, True):
        for c0 in BASES:
            out["arms"][f"{'pinned' if pin else 'free'}_c0_{c0:g}"] = fit(
                pats, SLP.MEAS14, SLP.IDLE21, c0, LM.V_REF, pin)
    return out


# ------------------------------------------------------------------ three cards, the version-3 check, 26 Sep
def abl_r_published():
    """The committed per-card fit, read not recomputed: abla.json item ABL-R, refit_p80."""
    d = json.load(open(os.path.join(LM.DV3, "abla.json")))
    R = next(x for x in d if x["item"] == "ABL-R")["per_card"]
    vals = {c: R[c]["refit_p80"]["fJ_per_event"]["bus"] for c in R}
    lo, hi = min(vals.values()), max(vals.values())
    return {"how": "non-negative least squares, constant free, 14 rows, from abla.json ABL-R.refit_p80",
            "prices_fJ": {c: R[c]["refit_p80"]["fJ_per_event"] for c in R},
            "constant_w": {c: R[c]["refit_p80"]["constant_W"] for c in R},
            "rms_w": {c: R[c]["refit_p80"]["rms"] for c in R},
            "leave_one_out_rms_w": {c: R[c]["refit_p80"]["loo_rms"] for c in R},
            "bus_spread": {"min_fJ": lo, "max_fJ": hi, "ratio_max_over_min": hi / lo, "by_card": vals}}


def per_card():
    runs = json.load(open(os.path.join(LM.DV3, "abla.runs.json")))
    cards = [c for c in runs["cards_all"] if c in runs["runs"]]
    pats = [p for _, p in V3_ROWS]
    out = {"source": "docs/reports/data/2026-09-25-claims-v3/results/abla.runs.json, kept_busy runs of "
                     "ABL-R's 14 rows (8 fp32 + 6 structured); board power is the mean p80_d over the kept "
                     "runs (the registered dropout rule), idle the mean p_before, the rail each card's own "
                     "measured busy_mv; counts from 2026-09-21-horace-aifoundry2/toggles_all.json",
           "patterns": pats, "cards": {}, "arms": {},
           "published_abl_r_refit_p80": abl_r_published(),
           "arms_vs_published": "ABL-R is non-negative least squares with a free constant on the same 14 "
                                "rows; the arms here are signed least squares on load_model's fixed base, "
                                "which is the convention --pin-bus lives in. The two are not the same fit.",
           "temperature_caveat": "the registered launch temperatures differ (80.9 / 55.8 / 80.9 C); each "
                                 "card's switching is measured against its own idle at its own temperature, "
                                 "so each fit is internally matched and the across-card comparison carries "
                                 "the difference identically in both arms"}
    meas, idles, volts, nruns, tlaunch = {}, {}, {}, {}, {}
    for card in cards:
        kept = {}
        for r in runs["runs"][card]:
            if r.get("kept_busy"):
                kept.setdefault(r["config"], []).append(r)
        meas[card] = {p: sum(x["p80_d"] for x in kept[cfg]) / len(kept[cfg]) for cfg, p in V3_ROWS}
        allr = [x for cfg, _ in V3_ROWS for x in kept[cfg]]
        idles[card] = sum(x["p_before"] for x in allr) / len(allr)
        volts[card] = runs["idle_by_card"][card]["busy_mv"] / 1000.0
        nruns[card] = sorted({len(kept[cfg]) for cfg, _ in V3_ROWS})
        tlaunch[card] = sum(x["t_launch"] for x in allr) / len(allr)
        out["cards"][card] = {"idle_w": idles[card], "volts": volts[card], "runs_per_pattern": nruns[card],
                              "mean_launch_temp_c": tlaunch[card], "board_w": meas[card]}
    for pin in (False, True):
        for c0 in BASES:
            key = f"{'pinned' if pin else 'free'}_c0_{c0:g}"
            per = {card: fit(pats, meas[card], idles[card], c0, volts[card], pin, tog=TOG_ALL)
                   for card in cards}
            spread = {}
            for cls in CLASSES:
                vals = [per[c]["prices_fJ"][cls] for c in cards]
                lo, hi = min(vals), max(vals)
                spread[cls] = {"min_fJ": lo, "max_fJ": hi, "range_fJ": hi - lo,
                               "ratio_max_over_min": (hi / lo) if lo not in (0.0,) else None,
                               "by_card": {c: per[c]["prices_fJ"][cls] for c in cards}}
            out["arms"][key] = {
                "per_card": per, "price_spread": spread,
                "rms_w": {c: per[c]["in_sample_rms_w"] for c in cards},
                "leave_one_out_rms_w": {c: per[c]["leave_one_out_rms_w"] for c in cards}}
    return out


def main():
    a = fp32_14()
    c = per_card()

    # ---- the free arm must reproduce what is already committed, or this file is not comparable to it
    sc = json.load(open(os.path.join(LM.DATA, "2026-10-26-load-model", "scores.json")))["fp32_14_patterns"]
    checks = []
    for arm, ref in (("free_c0_0", "at_c0_zero"), ("free_c0_-1.18", "at_joined_c0")):
        mine, theirs = a["arms"][arm], sc[ref]
        for field in ("in_sample_rms_w", "leave_one_out_rms_w"):
            d = abs(mine[field] - theirs[field])
            checks.append({"arm": arm, "against": f"scores.json fp32_14_patterns.{ref}.{field}",
                           "mine": mine[field], "committed": theirs[field], "abs_diff": d, "ok": d < 1e-9})
        for cls in CLASSES:
            d = abs(mine["prices_fJ"][cls] - theirs["refit_prices_fJ"][cls])
            checks.append({"arm": arm, "against": f"scores.json ...{ref}.refit_prices_fJ.{cls}",
                           "mine": mine["prices_fJ"][cls], "committed": theirs["refit_prices_fJ"][cls],
                           "abs_diff": d, "ok": d < 1e-9})
    bad = [c_ for c_ in checks if not c_["ok"]]

    out = {
        "what": "the 14-pattern fit and the three-card fit with the operand-bus price PINNED to E60/E61's "
                "measured read-port bit, beside the free fit, at both per-kernel offsets. Recap item 10.",
        "request": "Q128(e)",
        "pinned_bus_fJ": E_BUS_PINNED,
        "pinned_bus_source": "load_model.Coefficients.e_readport -- E60/E61's measured register-file "
                             "read-port bit, 20.83 fJ at the board (E61's separate build reads 20.70)",
        "bases_w": BASES,
        "method": "the bus column is moved out of the design matrix and into the target, so the pinned arm "
                  "fits three free prices against the same measurements; leave-one-out refits without one "
                  "pattern and predicts it, as E38 does",
        "fp32_14": a,
        "per_card": c,
        "reproduction_check": {"ok": not bad, "n": len(checks), "failures": bad,
                               "note": "the free arms must equal scores.json's fp32_14_patterns to the last "
                                       "float digit; they are the same fit by a different route"},
    }
    out["reading"] = reading(a, c)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(json.dumps(out["reading"], indent=1))
    print(f"\nreproduction check: {'OK' if not bad else 'FAILED'} ({len(checks)} comparisons)")
    print(f"wrote {OUT}")


def reading(a, c):
    """The sentences the README quotes, built from the numbers above so the two cannot drift apart."""
    f0, p0 = a["arms"]["free_c0_0"], a["arms"]["pinned_c0_0"]
    fc, pc = a["arms"]["free_c0_-1.18"], a["arms"]["pinned_c0_-1.18"]
    sf0, sp0 = c["arms"]["free_c0_0"]["price_spread"], c["arms"]["pinned_c0_0"]["price_spread"]
    sfc, spc = c["arms"]["free_c0_-1.18"]["price_spread"], c["arms"]["pinned_c0_-1.18"]["price_spread"]
    return {
        "fp32_14_c0_zero": {
            "free": {"bus_fJ": f0["prices_fJ"]["bus"], "in_sample_rms_w": f0["in_sample_rms_w"],
                     "leave_one_out_rms_w": f0["leave_one_out_rms_w"]},
            "pinned": {"bus_fJ": p0["prices_fJ"]["bus"], "in_sample_rms_w": p0["in_sample_rms_w"],
                       "leave_one_out_rms_w": p0["leave_one_out_rms_w"]},
            "loo_cost_of_pinning_pct": 100 * (p0["leave_one_out_rms_w"] / f0["leave_one_out_rms_w"] - 1.0)},
        "fp32_14_c0_joined": {
            "free": {"bus_fJ": fc["prices_fJ"]["bus"], "in_sample_rms_w": fc["in_sample_rms_w"],
                     "leave_one_out_rms_w": fc["leave_one_out_rms_w"]},
            "pinned": {"bus_fJ": pc["prices_fJ"]["bus"], "in_sample_rms_w": pc["in_sample_rms_w"],
                       "leave_one_out_rms_w": pc["leave_one_out_rms_w"]},
            "loo_cost_of_pinning_pct": 100 * (pc["leave_one_out_rms_w"] / fc["leave_one_out_rms_w"] - 1.0)},
        "per_card_bus_spread": {
            "free_c0_zero": sf0["bus"], "pinned_c0_zero": sp0["bus"],
            "free_c0_joined": sfc["bus"], "pinned_c0_joined": spc["bus"]},
        "per_card_where_the_spread_goes": {
            "free_c0_zero": {k: sf0[k]["ratio_max_over_min"] for k in CLASSES},
            "pinned_c0_zero": {k: sp0[k]["ratio_max_over_min"] for k in CLASSES},
            "free_c0_joined": {k: sfc[k]["ratio_max_over_min"] for k in CLASSES},
            "pinned_c0_joined": {k: spc[k]["ratio_max_over_min"] for k in CLASSES}},
        "per_card_loo_w": {
            "free_c0_zero": c["arms"]["free_c0_0"]["leave_one_out_rms_w"],
            "pinned_c0_zero": c["arms"]["pinned_c0_0"]["leave_one_out_rms_w"],
            "free_c0_joined": c["arms"]["free_c0_-1.18"]["leave_one_out_rms_w"],
            "pinned_c0_joined": c["arms"]["pinned_c0_-1.18"]["leave_one_out_rms_w"]},
    }


if __name__ == "__main__":
    main()
