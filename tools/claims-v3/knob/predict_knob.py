#!/usr/bin/env python3
"""predict_knob.py: freeze E69's per-cell predictions from E64's registered governor model.

E64 (docs/reports/data/2026-10-23-e64-horace-power-limit/) fitted, on aifoundry2's card 0:
  (a) each operand pattern's board power at 600, 700 and 800 MHz;
  (b) the governor as a first-order average of the board's power, time constant 1.3 s, compared with the TDP
      level once per 0.24 s pass, one VMIN point up or down (mean clock after the ramp reproduced to 3.3 MHz
      rms over 26 cool-die runs);
  (c) a thermal line, die = 41.88 + 0.4696 C per W of board power, over the sustained runs' last 40 s.
Those three, and nothing measured in E69, produce every number this file writes.

Burst cells use E64's own `simulate()` with its default window, which is the call E64 validated against its
26 measured 6 s runs (`figures.json .check`, 3.3 MHz rms). The published cap table in E64's README used a
longer window (t_end 12 s, from 4 s), so its numbers differ by a few MHz from the ones here; E69 measures 6 s
bursts, so the 6 s window is the right predictor and the control cells check it against E64's own measurements.

Sustained cells use the clock ladder directly: the highest VMIN point whose own sustained board power is under
the cap AND whose die on the thermal line is at or under the threshold. Where the point above is excluded by a
thin margin the governor dithers between the two, as E64 measured for `ones`, and the prediction is the midpoint
with the pair as its band.

SAFETY FILTER (the archive's own incident record; see README "Why these cells and no others"): a cell is dropped
its 600 MHz board power is at least 2 W below 1.05 x TDP. At or above that line the power-down loop's exit test
can never be satisfied while the kernel runs - the mechanism that latched aifoundry3's governor at TDP 0 - and
Esperanto filed two of their own incidents against it (ids and details stay out of this public repo). No cell raises the cap above the card's own
65 W default: their service-processor hang was seen with card power pinned just above 75 W.

    python3 tools/claims-v3/knob/predict_knob.py \
        --figures docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json \
        --out tools/claims-v3/knob/predictions.json

Read-only: no card, no device node, no network.
"""
import argparse
import hashlib
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
from surface_hpl import rate_t, simulate  # noqa: E402

PTS = [600, 700, 800]
TAU = 1.3      # s, E64 figures.json .governor.tau_s
PASS_S = 0.24  # s, E64 .governor.pass_s
BAND = 25.0    # MHz, the registered half-width (7.5x the model's own 3.3 MHz rms, a quarter of a VMIN step)
EXIT_MARGIN_W = 2.0   # the safety filter's margin on the power loop's exit test
DITHER_C = 1.5        # C: the point above counts as "thinly excluded" on heat within this
DITHER_W = 2.0        # W: ditto on power

# The grid. TDP 65 W and threshold 65 C are the card's own defaults, so those cells are controls with nothing set.
BURST = [  # (tdp_w, type, values)
    (65, "fp32", "zeros"), (65, "fp32", "ones"), (65, "fp32", "a_ones_b_randn"), (65, "fp32", "randn"),
    (55, "fp32", "zeros"), (55, "fp32", "ones"), (55, "fp32", "a_ones_b_randn"), (55, "fp32", "randn"),
    (45, "fp32", "zeros"), (45, "fp32", "ones"), (45, "fp32", "a_ones_b_randn"),
    (35, "fp32", "zeros"), (35, "fp32", "ones"),
]
SUS = [  # (tdp_w, threshold_c, type, values)
    (65, 65, "fp32", "ones"), (65, 65, "fp32", "randn"),      # controls: must reproduce E64
    (65, 70, "fp32", "ones"), (65, 70, "fp32", "randn"),      # the threshold raised (the CONTEXT ceiling)
    (65, 62, "fp32", "ones"),                                 # the threshold lowered
    (50, 65, "fp32", "ones"),                                 # the cap lowered: a heat clamp becomes a power cap
]
THERM_A, THERM_K = 41.88, 0.4696  # E64 .thermal


def burst_powers(fig):
    """{(type, values): {f: W}} from E64's LAD runs' own powers - the inputs its `check` validated."""
    g = {}
    for m in fig["runs"]:
        if m["block"] == "LAD" and m.get("minions") == 1024 and m.get("p"):
            g.setdefault((m["type"], m["values"]), []).append(m)
    out, meas = {}, {}
    for k, ms in g.items():
        p = {}
        for f in PTS:
            xs = [m["p"][str(f)] for m in ms if m["p"].get(str(f)) is not None]
            p[f] = round(st.mean(xs), 2) if xs else None
        if all(p[f] is not None for f in PTS):
            out[k] = p
            meas[k] = [m["mhz_steady"] for m in ms if m.get("mhz_steady") is not None]
    return out, meas


def sus_powers(fig, lad):
    """{(type, values): ({f: W}, note)} - each clock's SUSTAINED board power.

    A sustained run visits only one or two VMIN points, and a dithering one spends most 2 s bins at fractional
    clocks, so per-clock sustained medians are not available. The rule, fixed here before any E69 run: take the
    pattern's own sustained mean board power and sustained mean clock from E64's reduction, read the pattern's
    cool-die LAD ladder at that same clock by linear interpolation, and scale the whole ladder by the ratio. The
    ratio is above 1 because a sustained die is hotter and leaks more; one ratio per pattern keeps the ladder's
    measured SHAPE and fixes only its level, which is what the thermal line needs."""
    out = {}
    for m in fig["runs"]:
        if m["block"] != "SUS" or m.get("sus_w_mean") is None or m.get("sus_mhz_mean") is None:
            continue
        k = (m["type"], m["values"])
        p_lad = lad.get(k)
        if not p_lad:
            continue
        f0 = max(600.0, min(800.0, m["sus_mhz_mean"]))
        lo = 600 if f0 <= 700 else 700
        hi = lo + 100
        frac = (f0 - lo) / 100.0
        lad_at = p_lad[lo] + frac * (p_lad[hi] - p_lad[lo])
        r = m["sus_w_mean"] / lad_at if lad_at else None
        if not r:
            continue
        out[k] = ({f: round(p_lad[f] * r, 2) for f in PTS},
                  {"sus_mhz_mean": m["sus_mhz_mean"], "sus_w_mean": m["sus_w_mean"],
                   "lad_interp_w": round(lad_at, 2), "ratio": round(r, 4)})
    return out


def sus_predict(p, tdp, thr):
    """The sustained mean clock under both limits, from the scaled power ladder and E64's thermal line.

    A clock f is REACHABLE when its own sustained board power is at or under the cap; it is COOL when its die on
    the thermal line is at or under the threshold. The governor climbs while the average power is under the cap,
    so the top reachable point is where it tries to sit; the thermal branch then walks it down and, on exit,
    drops it to the boot point, from which the power branch climbs straight back. The time-average therefore
    lands BETWEEN the highest cool-and-reachable point f_lo and the point above it f_hi, and how far up depends
    on where the threshold sits inside the two points' die span:

        w = (thr - die(f_lo)) / (die(f_hi) - die(f_lo)),  clipped to [0, 1];  mean = f_lo + w (f_hi - f_lo)

    with w = 0 when f_hi is unreachable on power (the governor cannot dwell there at all) and w = 0.5 when f_hi
    is excluded on power by less than DITHER_W (it dwells there on alternate passes: the no-hysteresis dither).
    When no point is cool the card sits at the boot point, which is where the thermal loop's exit puts it.
    This rule reproduces E64's own nine sustained runs; `selfcheck_sus` in the output reports by how much."""
    reach = [f for f in PTS if p.get(f) is not None and p[f] <= tdp]
    cool = [f for f in reach if (THERM_A + THERM_K * p[f]) <= thr]
    if not cool:
        return 600.0, 600, None, 0.0, "no point is cool: the boot point", None, None
    f_lo = max(cool)
    above = [x for x in PTS if x > f_lo and p.get(x) is not None]
    if not above:
        return float(f_lo), f_lo, None, 1.0, "top point, cool and under the cap", None, None
    f_hi = above[0]
    d_c = round((THERM_A + THERM_K * p[f_hi]) - thr, 2)
    d_w = round(p[f_hi] - tdp, 2)
    if d_w > DITHER_W:
        w, shape = 0.0, f"held at {f_lo}: {f_hi} is over the cap by {d_w} W"
    elif d_w > 0:
        w, shape = 0.5, f"dither {f_lo}-{f_hi}: {f_hi} is over the cap by only {d_w} W"
    else:
        die_lo = THERM_A + THERM_K * p[f_lo]
        die_hi = THERM_A + THERM_K * p[f_hi]
        w = 0.0 if die_hi <= die_lo else max(0.0, min(1.0, (thr - die_lo) / (die_hi - die_lo)))
        shape = f"heat clamp between {f_lo} and {f_hi}: duty {round(w, 3)}"
    return round(f_lo + w * (f_hi - f_lo), 1), f_lo, f_hi, w, shape, d_c, d_w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figures", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fig = json.load(open(a.figures))
    bp, bmeas = burst_powers(fig)
    sp = sus_powers(fig, bp)

    out = {"experiment": "E69", "request": "Q129", "card": "aifoundry2 card 0",
           "source": {"figures": "docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json",
                      "governor": fig["governor"], "thermal": {"a_c": THERM_A, "k_c_per_w": THERM_K},
                      "note": "E64's fit extrapolated; no E69 measurement enters any number here"},
           "model": {"tau_s": TAU, "pass_s": PASS_S, "band_mhz": BAND,
                     "exit_margin_w": EXIT_MARGIN_W, "dither_c": DITHER_C, "dither_w": DITHER_W},
           "burst": [], "sustained": [], "dropped": [], "controls_from_e64": {}}

    for k, v in sorted(bmeas.items()):
        out["controls_from_e64"][f"burst-{k[0]}-{k[1]}"] = v
    for k, m in sorted({(r["type"], r["values"]): r for r in fig["runs"]
                        if r["block"] == "SUS"}.items()):
        if m.get("sus_mhz_mean") is not None:
            out["controls_from_e64"][f"sus-{k[0]}-{k[1]}"] = {
                "mhz": m["sus_mhz_mean"], "die_c": m.get("sus_die_mean"), "board_w": m.get("sus_w_mean")}

    for tdp, t, v in BURST:
        p = bp.get((t, v))
        if p is None:
            out["dropped"].append({"cell": f"B-tdp{tdp}-{t}-{v}", "why": "no E64 power ladder for this pattern"})
            continue
        if p[600] > 1.05 * tdp - EXIT_MARGIN_W:
            out["dropped"].append({"cell": f"B-tdp{tdp}-{t}-{v}", "why": "power-loop exit unreachable",
                                   "p600_w": p[600], "limit_w": round(1.05 * tdp - EXIT_MARGIN_W, 2)})
            continue
        mhz = round(simulate(p, float(tdp), TAU, PASS_S), 1)
        lo, hi = (775.0, 800.0) if mhz >= 799 else ((600.0, 625.0) if mhz <= 601 else (mhz - BAND, mhz + BAND))
        out["burst"].append({"cell": f"B-tdp{tdp}-{t}-{v}", "block": "BURST", "tdp_w": tdp, "threshold_c": 65,
                             "type": t, "values": v, "control": tdp == 65, "p_w": p,
                             "pred_mhz_mean": mhz, "band_mhz": [round(lo, 1), round(hi, 1)],
                             "pred_tflops": round(rate_t(t, mhz), 2), "pred_throttles": mhz < 799.0,
                             "e64_measured_mhz": bmeas.get((t, v)) if tdp == 65 else None})

    for tdp, thr, t, v in SUS:
        got = sp.get((t, v))
        if got is None:
            out["dropped"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}", "why": "no E64 sustained power ladder"})
            continue
        p, pnote = got
        if p[600] > 1.05 * tdp - EXIT_MARGIN_W:
            out["dropped"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}", "why": "power-loop exit unreachable",
                                   "p600_w": p[600], "limit_w": round(1.05 * tdp - EXIT_MARGIN_W, 2)})
            continue
        # The thermal loop spins while the die at the bottom point is over the threshold. At the card's own
        # default threshold that is its everyday condition (E64 measured it for `randn`), so it is a baseline,
        # not a new hazard; a LOWERED threshold that creates it is a new hazard and the cell is dropped.
        if thr < 65 and (THERM_A + THERM_K * p[600]) > thr:
            out["dropped"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}",
                                   "why": "a lowered threshold would put the thermal loop's exit out of reach",
                                   "die600_c": round(THERM_A + THERM_K * p[600], 1), "threshold_c": thr})
            continue
        mhz, f_lo, f_hi, w, shape, d_c, d_w = sus_predict(p, tdp, thr)
        if mhz >= 799:
            lo, hi = 775.0, 800.0
        elif mhz <= 601:
            lo, hi = 600.0, 625.0
        elif f_hi is not None and 0 < w < 1:
            lo, hi = float(f_lo), float(f_hi)          # a duty cycle: the band is the pair it moves between
        else:
            lo, hi = mhz - BAND, mhz + BAND
        out["sustained"].append({"cell": f"S-tdp{tdp}-thr{thr}-{t}-{v}", "block": "SUS", "tdp_w": tdp,
                                 "threshold_c": thr, "type": t, "values": v,
                                 "control": tdp == 65 and thr == 65, "p_w": p, "p_w_note": pnote,
                                 "pred_mhz_mean": mhz, "band_mhz": [round(lo, 1), round(hi, 1)],
                                 "shape": shape, "point": f_lo, "point_above": f_hi, "duty_at_above": round(w, 3),
                                 "excluded_above_by_c": d_c, "excluded_above_by_w": d_w,
                                 "pred_die_c": round(THERM_A + THERM_K * p[f_lo], 1), "pred_board_w": p[f_lo],
                                 "pred_tflops": round(rate_t(t, mhz), 2)})

    # self-check: the same sustained rule on E64's own nine sustained runs, at its own TDP 65 / threshold 65
    out["selfcheck_sus"] = []
    for m in fig["runs"]:
        if m["block"] != "SUS" or m.get("sus_mhz_mean") is None:
            continue
        got = sp.get((m["type"], m["values"]))
        if not got:
            continue
        pp, _ = got
        pred = sus_predict(pp, 65, 65)[0]
        out["selfcheck_sus"].append({"run": m["run"], "type": m["type"], "values": m["values"],
                                     "pred_mhz": pred, "meas_mhz": m["sus_mhz_mean"],
                                     "err_mhz": round(pred - m["sus_mhz_mean"], 1)})
    errs = [abs(c["err_mhz"]) for c in out["selfcheck_sus"]]
    out["selfcheck_sus_rms_mhz"] = round((sum(e * e for e in errs) / len(errs)) ** 0.5, 1) if errs else None

    blob = json.dumps(out, indent=1, sort_keys=True)
    open(a.out, "w").write(blob + "\n")
    print(f"sha256 {hashlib.sha256(blob.encode()).hexdigest()}  {a.out}")
    print(f"\nBURST ({len(out['burst'])} cells; cool die, one 6 s launch, mean MHz from 1.5 s)")
    for c in out["burst"]:
        e = f"  E64 measured {c['e64_measured_mhz']}" if c["e64_measured_mhz"] else ""
        print(f"  {c['cell']:30s} pred {c['pred_mhz_mean']:6.1f} band {c['band_mhz']} "
              f"{c['pred_tflops']:6.2f} TF  p600/700/800 {c['p_w'][600]}/{c['p_w'][700]}/{c['p_w'][800]} W{e}")
    print(f"\nSUSTAINED ({len(out['sustained'])} cells; nine 8 s launches, last 40 s)")
    for c in out["sustained"]:
        print(f"  {c['cell']:30s} pred {c['pred_mhz_mean']:6.1f} band {c['band_mhz']}  "
              f"die {c['pred_die_c']} C  board {c['pred_board_w']} W  -- {c['shape']}")
    print(f"\nsustained rule on E64's own nine runs: rms {out['selfcheck_sus_rms_mhz']} MHz")
    for c in out["selfcheck_sus"]:
        print(f"  {c['run']:28s} pred {c['pred_mhz']:6.1f}  meas {c['meas_mhz']:6.1f}  err {c['err_mhz']:+6.1f}")
    print(f"\nDROPPED by the safety filter ({len(out['dropped'])})")
    for d in out["dropped"]:
        print(f"  {d['cell']:30s} {d['why']}  {({k: v for k, v in d.items() if k not in ('cell', 'why')})}")
    print("\nE64 controls to reproduce:", json.dumps(out["controls_from_e64"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
