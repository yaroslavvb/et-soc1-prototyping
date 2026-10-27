#!/usr/bin/env python3
"""Q129 rail ledger: where the board's watts go that the minion rail does not carry.

    python3 docs/reports/data/2026-10-27-q129-rail-ledger/rail_ledger.py <repo root> \
        --out docs/reports/data/2026-10-27-q129-rail-ledger/rail-ledger.json

Q128's waterfall takes one random fp32 multiply-add at 5.783 pJ at the board and puts 0.75 of it on the minion
rail (4.337 pJ), the 0.75 being E60's per-flipped-bit rail/board ratio carried across to a per-multiply-add
figure E38 measured.  Nothing had read the other three rails for the multiply-add itself.  This script does,
from committed telemetry only: no card was run for it.

Sources
-------
* E38/E39's own telemetry, `docs/reports/data/2026-09-25-claims-v3/raw/<card>/abla/p[1-4]/` - the runs behind
  the 5.783 pJ.  23 configurations x 4 passes x 3 cards, 7 s per run, every sample at 600 MHz, after the strict
  start (launch 80.9 C on aifoundry2 and aifoundry1-c1, 55.8 C on aifoundry3).
* the energy manual's catalogue, `docs/reports/data/2026-09-23-energy-manual/catalogue.json` - 1,176 bursts per
  card with `rails_over` and `over_idle_w`, for the load dependence of the off-rail remainder.
* `docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json` - the published attribution of that remainder.

What the rails are (docs/findings/14-card-behaviour.md, "The telemetry, and what each number really is"):
`sp.minion_w`, `sram_w`, `noc_w` are the PMIC's own first-order running average of each regulator's OUTPUT power,
published one service-processor pass late, tau 1.02-1.07 s on these cards.  `board_w` is the 12 V input, instant.
The other rails - DDR core, VDDQ, VDDQLP, PCIe logic, PCIe/PShire, IO shire, Maxion - have set points in the
PMIC and no telemetry at all, so board minus the three is the off-rail remainder plus every regulator's loss.

Two windows, both with board and rails read from the SAME samples, so no temperature correction stands between
them:

  LAUNCH   board over [t0+1, t0+3] s (the registered p_early with its dropout rule), rails deconvolved to the
           same window with `tools/ettelem/deconv.py` and each card's tau.  2.3-3.3 C above the launch reading.
  LATE     board and rails both over [t1-1, t1] s, raw.  6-7 s after the step the rails' filter has 0.3% of the
           step left, so no deconvolution is needed, and this is the published rail split's own kind of window.

Both are differences against the pre-launch idle bracket [t0-2, t0-0.3] s, the same bracket the registered
metric uses.  Per-rail watts become pJ per multiply-add by the run's own measured MAC rate.

THE FOOTING, and why the first version of this ledger was on the wrong one
-------------------------------------------------------------------------
A window delta `p_window - p_idle` carries the die heating that happened inside the window.  E38's REGISTERED
metric does not: it is `p_early - leak * (t_early - t_launch) - p_before`, with `leak` 0.81 W/C on aifoundry2
and 0.55 on aifoundry3.  The catalogue's `over_idle_w` carries the same correction (`leak_correction_w`, mean
0.352 W) while its `rails_over` does not, so the published off-rail fit is calibrated against a corrected
board.  Both references this ledger transfers onto are therefore on the CORRECTED footing.

The first version of this ledger (commit 68c50c37) reported uncorrected deltas and then multiplied every row
by 5.783 / 6.176 to land on Q128's board figure - treating an additive leakage term as a proportional scale.
That is wrong, and it is wrong in a direction that matters: the minion rail carries only 32-37% of the board's
within-run temperature rise (measured below), so a correction that is proportional to each row takes too much
off the minion rail and too little off the off-rail remainder.  Three footings are now computed for every row
and all three are published:

  uncorrected   the raw window delta (what 68c50c37 published).  LOWER BOUND on the rail's share.
  drift_split   the registered correction `leak * (t_window - t_launch)` subtracted from the board and
                distributed over minion / SRAM / NoC / off-rail by their OWN measured within-run drift
                slopes.  This is the central estimate: it is the only one that is consistent both with the
                registered metric and with the measured fact that the rails do not carry all of the rise.
  board_only    the correction taken off the board alone, rails left raw - literally what E38 does, because
                E38 has no rail numbers.  UPPER BOUND on the rail's share.

The SRAM and NoC rails do not survive this: their whole launch-window delta is the same size as their own
leakage rise inside the window (NoC 100% / 103%, SRAM 66% / 61%), so on the corrected footing they are
0.01 pJ and -0.02 pJ and are reported as "not separable from the window's own heating", not as per-MAC
switching energies.

The per-rail within-run temperature slope is each rail's deconvolved power regressed on the die reading over
[t0+2, t1-0.2] s for the runs that heat the die by at least 3 C, beside the board's own slope from the same
samples - which is how the board's leakage correction is split between the rails and the off-rail remainder.

Screens (declared here, applied below, every exclusion counted)
---------------------------------------------------------------
S1  every launch record printed ok, and mhz.minion == 600 over [t0-2, t1] - E38's own keep rule.
S2  the idle bracket's rails must be SETTLED: |minion over [t0-5, t0-3] minus minion over [t0-2, t0-0.3]| <=
    0.15 W, and the strict start's approach >= 6 s (six time constants).  A rail delta is a difference against
    that bracket, so a bracket still falling from the preheat makes the delta meaningless.  This screen removes
    aifoundry1-c1's whole E38 campaign, and the leg that fires is the SETTLING leg, not the approach: 72 of its
    92 runs fail settling alone, 20 fail both, and NONE fails the approach alone (its approach is 3.1 s at the
    tenth percentile and 2.3 s at the minimum, but 78% of its runs are above the 6 s bar).  Its preheat runs to
    within 2 s of the launch, so the minion rail enters the run far above its idle level - the far bracket sits
    20.5 W above the early window - and falls through it, which makes a rail delta negative on a pattern that
    draws power: its fp32_zeros minion delta reads -6.6 W raw and -6.9 W deconvolved (per pass -2.9 to -9.6),
    i.e. the filter, not the workload.  aifoundry2 (approach median 15.6 s, 38 runs lost to settling) and
    aifoundry3 (39.9 s, 1 run lost) pass it.  Every figure here is counted in `cards.*.screen_evidence`.
S3  the board's random 5-12 W meter drops (E62) are dropped from every board window by the registered rule:
    samples more than 2 W below that window's median.
"""
import argparse
import collections
import glob
import gzip
import json
import os
import sys

import numpy as np

CARDS = ["aifoundry2", "aifoundry3", "aifoundry1-c1"]
RAILS = ("minion", "sram", "noc")
# the registered reduction parameters of E38 (tools/claims-v3/abla/reduce.py PAR); aifoundry1-c1 takes aifoundry2's
PAR = {"aifoundry2": {"leak": 0.81, "launch": 80.9}, "aifoundry3": {"leak": 0.55, "launch": 55.8},
       "aifoundry1-c1": {"leak": 0.81, "launch": 80.9}}
MAC_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
# the configurations this ledger reports, in the order the README's table uses
WANT = ["fp32_zeros", "fp32_ones", "fp32_randn", "fp32_randn_16", "fp32_randn_8", "fp16_randn", "int8_randn", "spin"]


def load_jsonl(path):
    op = gzip.open if path.endswith(".gz") else open
    return [json.loads(l) for l in op(path, "rt") if l.lstrip().startswith("{")]


def mean_se(xs):
    """Mean and standard error of the mean over passes (n small: se = sd / sqrt(n), sd with ddof 1)."""
    a = np.asarray([x for x in xs if x is not None], float)
    if not len(a):
        return None, None, 0
    return float(a.mean()), (float(a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0), len(a)


SETTLE_W = 0.15          # S2: the idle bracket's minion rail must not move this much between its two brackets
APPROACH_S = 6.0         # S2: the strict start's approach, in time constants of the rails' filter
BODY_STARTS = (1.5, 2.5, 3.5)   # the drift window's start, as a sensitivity (the reported one is 1.5 s)
# E66 measured aifoundry2's real IDLE leakage slope at 0.294 W/C over 51-58 C; E38's registered estimator read
# 1.508 W/C on a busy transient and its reduction uses 0.81 / 0.55.  Published as a labelled sensitivity.
E66_IDLE_SLOPE = {"aifoundry2": 0.294}


def pass_runs(d, card, deconv, drops, screened=None):
    """Every kept run of one E38 pass directory, with board and rail windows."""
    tel = sorted(load_jsonl(os.path.join(d, "telemetry.jsonl.gz")), key=lambda s: s["t_ms"])
    t = np.array([s["t_ms"] for s in tel], float) / 1e3
    P = np.array([s["board_w"] for s in tel], float)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
    mhz = np.array([float(s["mhz"]["minion"]) for s in tel])
    rail = {k: np.array([s["sp"][k + "_w"][0] for s in tel], float) for k in RAILS}
    mv = {k: np.array([s["sp"][k + "_mv"][0] for s in tel], float) for k in RAILS}
    tc, ch = deconv.load(os.path.join(d, "telemetry.jsonl.gz"))
    dec = {k: deconv.deconvolve(tc, ch[k + "_w"], ch, k + "_w", card=card) for k in RAILS}
    dec_board = deconv.deconvolve(tc, ch["board_avg_w"], ch, "board_avg_w", card=card)

    starts = {(s.get("block"), s.get("config")): s for s in load_jsonl(os.path.join(d, "starts.jsonl"))}
    groups = collections.OrderedDict()
    for r in load_jsonl(os.path.join(d, "runs.jsonl")):
        if r.get("block", -9) >= 0 and "config" in r:
            groups.setdefault((r["block"], r["config"]), []).append(r)

    def clean(x):
        """S3: a board window's mean after the registered dropout rule."""
        return float(x[x >= float(np.median(x)) - 2.0].mean())

    out = []
    for (block, cfg), ls in groups.items():
        if not all(bool(x.get("ok")) for x in ls):
            drops["S1_not_ok"] += 1
            continue
        t0, t1 = ls[0]["t_start_ms"] / 1e3, ls[-1]["t_end_ms"] / 1e3
        dur = t1 - t0
        sel = lambda lo, hi: (t >= lo) & (t <= hi)                                      # noqa: E731
        idle, early, late = sel(t0 - 2.0, t0 - 0.3), sel(t0 + 1.0, t0 + 3.0), sel(t1 - 1.0, t1)
        far, clock = sel(t0 - 5.0, t0 - 3.0), sel(t0 - 2.0, t1)
        if idle.sum() < 3 or early.sum() < 5 or late.sum() < 5 or far.sum() < 3:
            drops["S1_telemetry_gap"] += 1
            continue
        mz = mhz[clock][~np.isnan(mhz[clock])]
        if not len(mz) or mz.min() != 600 or mz.max() != 600:
            drops["S1_clock"] += 1                                                      # E38's own keep rule
            continue
        st = starts.get((block, cfg), {})
        app = st.get("approach_ms")
        settle = float(rail["minion"][far].mean() - rail["minion"][idle].mean())
        bad_settle, bad_app = abs(settle) > SETTLE_W, (app is None or app / 1e3 < APPROACH_S)
        if screened is not None:
            # every run that reaches the S2 test, kept or not, so the screen itself can be audited
            mi, mf = float(rail["minion"][idle].mean()), float(rail["minion"][far].mean())
            gm, xm = dec["minion"]
            screened.append({
                "config": cfg, "approach_s": None if app is None else app / 1e3, "idle_settle_w": settle,
                "kept": not (bad_settle or bad_app),
                "leg": ("ok" if not (bad_settle or bad_app) else
                        "both" if bad_settle and bad_app else "settle" if bad_settle else "approach"),
                "minion_idle_w": mi, "minion_far_w": mf,
                "minion_early_raw_d": float(rail["minion"][early].mean()) - mi,
                "minion_early_dec_d": float(xm[(gm >= t0 + 1.0) & (gm <= t0 + 3.0)].mean()) - mi,
                "minion_late_raw_d": float(rail["minion"][late].mean()) - mi,
                "far_above_early_w": mf - float(rail["minion"][early].mean()),
                "board_early_d": float(P[early].mean()) - float(P[idle].mean())})
        if bad_settle or bad_app:
            drops["S2_rails_not_settled"] += 1
            drops["S2_leg_settle_only" if bad_settle and not bad_app else
                  "S2_leg_both" if bad_settle else "S2_leg_approach_only"] += 1
            continue
        r0 = ls[0]
        g = lambda arr_t, arr_x, lo, hi: float(arr_x[(arr_t >= lo) & (arr_t <= hi)].mean())  # noqa: E731
        row = {"card": card, "block": block, "config": cfg, "dur": dur, "test": r0.get("test"),
               "type": r0.get("type"), "values": r0.get("values"), "minions": r0.get("minions"),
               "approach_s": app / 1e3, "idle_settle_w": settle,
               "t_launch": float(T[idle][-1]), "t_early": float(T[early].mean()), "t_late": float(T[late].mean()),
               "board_idle": clean(P[idle]), "board_early": float(P[early].mean()),
               "board_early_d": clean(P[early]), "board_late": clean(P[late]),
               "mv": {k: float(mv[k][late].mean()) for k in RAILS}}
        for k in RAILS:
            gr, xr = dec[k]
            row[f"{k}_idle"] = float(rail[k][idle].mean())
            row[f"{k}_idle_far"] = float(rail[k][far].mean())
            row[f"{k}_early_dec"] = g(gr, xr, t0 + 1.0, t0 + 3.0)
            row[f"{k}_late"] = float(rail[k][late].mean())
            row[f"{k}_late_dec"] = g(gr, xr, t1 - 1.5, t1)
            # E60's own rail window, raw: [t0+2, t0+4) s of a 4 s run.  Its ratio to the settled late delta is
            # the attenuation E60's rail/board ratio carries (the board meter is instantaneous, the rails are not).
            row[f"{k}_e60win"] = g(t, rail[k], t0 + 2.0, t0 + 4.0)
        # a closure check on the deconvolution: the board's own filtered copy, deconvolved, against board_w
        row["board_early_dec_check"] = g(dec_board[0], dec_board[1], t0 + 1.0, t0 + 3.0)
        # work rate
        if r0.get("test") == "fma" and r0.get("type") in MAC_PER_OP:
            row["per_s"] = sum(x["iters"] for x in ls) * r0["minions"] * MAC_PER_OP[r0["type"]] / dur
            row["unit"] = "MAC"
        elif r0.get("test") == "spin":
            row["per_s"] = sum(x["iters"] for x in ls) * 5 * r0["minions"] / dur
            row["unit"] = "instruction"
        else:
            row["per_s"], row["unit"] = None, None
        # within-run drift against the die reading, board and each rail from the same body window.  The window
        # starts at t0+1.5 s, past the rails' deconvolved rise (10-90% in 0.3-0.4 s at sigma 0.1), and a run
        # qualifies when its reading rises at least 2.5 C inside it.
        body = sel(t0 + 1.5, t1 - 0.2)
        if body.sum() >= 10 and np.nanmax(T[body]) - np.nanmin(T[body]) >= 2.5:
            row["drift_board_w_per_c"] = float(np.polyfit(T[body], P[body], 1)[0])
            row["drift_rise_c"] = float(np.nanmax(T[body]) - np.nanmin(T[body]))
            for k in RAILS:
                gr, xr = dec[k]
                # the deconvolved rail sampled at the body's own times, against the same temperatures
                j = np.clip(np.searchsorted(gr, t[body]), 0, len(xr) - 1)
                row[f"drift_{k}_w_per_c"] = float(np.polyfit(T[body], xr[j], 1)[0])
                row[f"drift_{k}_raw_w_per_c"] = float(np.polyfit(T[body], rail[k][body], 1)[0])
        # the same split over other defensible body windows, as a declared sensitivity: start at t0+1.5, 2.5 or
        # 3.5 s with a >= 1.0 C rise (a looser rise bar, so each variant keeps many more runs), deconvolved and
        # raw side by side.  The raw rails are NOT an alternative reading in these windows - 24% of a 22 W step
        # is still unsettled at t0+1.5 s - they are here to show how much of the split the deconvolution carries.
        var = {}
        for s0 in BODY_STARTS:
            bw = sel(t0 + s0, t1 - 0.2)
            if bw.sum() < 10:
                continue
            rise = float(np.nanmax(T[bw]) - np.nanmin(T[bw]))
            if rise < 1.0:
                continue
            e = {"rise_c": rise, "board": float(np.polyfit(T[bw], P[bw], 1)[0])}
            for k in RAILS:
                gr, xr = dec[k]
                j = np.clip(np.searchsorted(gr, t[bw]), 0, len(xr) - 1)
                e[f"dec_{k}"] = float(np.polyfit(T[bw], xr[j], 1)[0])
                e[f"raw_{k}"] = float(np.polyfit(T[bw], rail[k][bw], 1)[0])
            var[f"t0+{s0:.1f}"] = e
        if var:
            row["drift_variants"] = var
        out.append(row)
    return out


def ledger_rows(runs, card):
    """Per configuration: board and per-rail deltas, pJ per unit, at both windows, averaged over passes."""
    by = collections.defaultdict(list)
    for r in runs:
        by[r["config"]].append(r)
    out = collections.OrderedDict()
    for cfg in [c for c in WANT if c in by] + sorted(set(by) - set(WANT)):
        rs = by[cfg]
        per_s, _, _ = mean_se([r["per_s"] for r in rs])
        rec = {"n_passes": len(rs), "unit": rs[0]["unit"], "per_s": per_s, "minions": rs[0]["minions"],
               "t_launch": mean_se([r["t_launch"] for r in rs])[0],
               "t_early": mean_se([r["t_early"] for r in rs])[0], "t_late": mean_se([r["t_late"] for r in rs])[0],
               "mv": {k: mean_se([r["mv"][k] for r in rs])[0] for k in RAILS}}
        for win, bkey, rkey in (("launch", "board_early_d", "{}_early_dec"), ("late", "board_late", "{}_late")):
            d = {}
            bd = [r[bkey] - r["board_idle"] for r in rs]
            d["board_w"], d["board_se_w"], _ = mean_se(bd)
            tot = np.zeros(len(rs))
            for k in RAILS:
                v = [r[rkey.format(k)] - r[f"{k}_idle"] for r in rs]
                d[f"{k}_w"], d[f"{k}_se_w"], _ = mean_se(v)
                tot = tot + np.array(v)
            d["rails_w"], d["rails_se_w"], _ = mean_se(tot.tolist())
            res = [b - s for b, s in zip(bd, tot.tolist())]
            d["offrail_w"], d["offrail_se_w"], _ = mean_se(res)
            d["minion_over_board"] = d["minion_w"] / d["board_w"] if d["board_w"] else None
            d["rails_over_board"] = d["rails_w"] / d["board_w"] if d["board_w"] else None
            d["offrail_share"] = d["offrail_w"] / d["board_w"] if d["board_w"] else None
            if per_s:
                for k in ("board", "minion", "sram", "noc", "rails", "offrail"):
                    d[f"{k}_pJ"] = d[f"{k}_w"] / per_s * 1e12
                    d[f"{k}_se_pJ"] = d[f"{k}_se_w"] / per_s * 1e12
            rec[win] = d
        for k in ["board"] + list(RAILS):
            vals = [r.get(f"drift_{k}_w_per_c") for r in rs if r.get(f"drift_{k}_w_per_c") is not None]
            if vals:
                m, se, n = mean_se(vals)
                rec.setdefault("drift_w_per_c", {})[k] = {"mean": m, "se": se, "n": n}
        if "drift_w_per_c" in rec and set(rec["drift_w_per_c"]) >= {"board", "minion", "sram", "noc"}:
            dr = rec["drift_w_per_c"]
            dr["rails"] = {"mean": sum(dr[k]["mean"] for k in RAILS), "se": None, "n": dr["board"]["n"]}
            dr["offrail"] = {"mean": dr["board"]["mean"] - dr["rails"]["mean"], "se": None, "n": dr["board"]["n"]}
            dr["offrail_share_of_board_drift"] = dr["offrail"]["mean"] / dr["board"]["mean"] if dr["board"]["mean"] else None
        rec["idle_w"] = {"board": mean_se([r["board_idle"] for r in rs])[0],
                         **{k: mean_se([r[f"{k}_idle"] for r in rs])[0] for k in RAILS}}
        rec["idle_w"]["rails"] = sum(rec["idle_w"][k] for k in RAILS)
        rec["idle_w"]["offrail"] = rec["idle_w"]["board"] - rec["idle_w"]["rails"]
        rec["idle_w"]["offrail_share"] = rec["idle_w"]["offrail"] / rec["idle_w"]["board"]
        rec["idle_settled_check_w"] = {k: mean_se([(r[f"{k}_idle_far"] - r[f"{k}_idle"]) for r in rs])[0]
                                       for k in RAILS}
        # absolute watts, so the deconvolution's closure check is checkable from this file: at the launch window
        # the deconvolved rail of a quiet pattern must equal its own settled late reading.
        rec["abs_w"] = {k: {"launch_dec": mean_se([r[f"{k}_early_dec"] for r in rs])[0],
                            "late_raw": mean_se([r[f"{k}_late"] for r in rs])[0]} for k in RAILS}
        for k in RAILS:
            a = rec["abs_w"][k]
            a["closure_w"] = a["launch_dec"] - a["late_raw"]
        # the attenuation E60's rail window applies: its raw delta over the settled late delta, run by run
        att = {}
        for k in RAILS:
            rat = [(r[f"{k}_e60win"] - r[f"{k}_idle"]) / (r[f"{k}_late"] - r[f"{k}_idle"]) for r in rs
                   if abs(r[f"{k}_late"] - r[f"{k}_idle"]) > 0.5]
            if len(rat):
                m, se, n = mean_se(rat)
                att[k] = {"mean": m, "se": se, "n": n}
        rec["e60_window_attenuation"] = att
        out[cfg] = rec
    return out


def card_drift(runs):
    """Each rail's within-run drift against the die reading, pooled over every screened run of one card that
    heats at least 2.5 C in its body window.  Leakage is a property of the die, not of the pattern, so pooling
    is what gives this an interval; per configuration it is in each configuration's own block."""
    out = {}
    for k in ["board"] + list(RAILS):
        vals = [r[f"drift_{k}_w_per_c"] for r in runs if f"drift_{k}_w_per_c" in r]
        if vals:
            m, se, n = mean_se(vals)
            out[k] = {"mean": m, "se": se, "n": n}
    if set(out) >= {"board", "minion", "sram", "noc"}:
        # the sum of the three rails and the off-rail remainder, with the standard errors PROPAGATED (the first
        # version of this script left these null, which is how a share with a +-0.34 interval was called firm)
        se_rails = float(np.sqrt(sum(out[k]["se"] ** 2 for k in RAILS)))
        out["rails"] = {"mean": sum(out[k]["mean"] for k in RAILS), "se": se_rails, "n": out["board"]["n"]}
        se_off = float(np.sqrt(out["board"]["se"] ** 2 + se_rails ** 2))
        out["offrail"] = {"mean": out["board"]["mean"] - out["rails"]["mean"], "se": se_off,
                          "n": out["board"]["n"]}
        sh = out["offrail"]["mean"] / out["board"]["mean"]
        out["offrail_share_of_board_drift"] = sh
        out["offrail_share_se"] = float(abs(sh) * np.sqrt((se_off / out["offrail"]["mean"]) ** 2
                                                          + (out["board"]["se"] / out["board"]["mean"]) ** 2))
        # same thing per run, so the share gets a second, independent interval
        shs = [(r["drift_board_w_per_c"] - sum(r[f"drift_{k}_w_per_c"] for k in RAILS)) / r["drift_board_w_per_c"]
               for r in runs if "drift_board_w_per_c" in r and abs(r["drift_board_w_per_c"]) > 0.1]
        if shs:
            m, se, n = mean_se(shs)
            out["offrail_share_per_run"] = {"mean": m, "se": se, "n": n}
        out["rise_c"] = mean_se([r["drift_rise_c"] for r in runs if "drift_rise_c" in r])[0]
        out["configs"] = sorted({r["config"] for r in runs if "drift_board_w_per_c" in r})
        # the RAW rails over the same window, pooled: the number this reading depends on the deconvolution for
        raw = {}
        for k in RAILS:
            v = [r[f"drift_{k}_raw_w_per_c"] for r in runs if f"drift_{k}_raw_w_per_c" in r]
            if v:
                m, se, n = mean_se(v)
                raw[k] = {"mean": m, "se": se, "n": n}
        if len(raw) == 3:
            rr = sum(raw[k]["mean"] for k in RAILS)
            raw["rails"] = {"mean": rr, "se": float(np.sqrt(sum(raw[k]["se"] ** 2 for k in RAILS)))}
            raw["offrail"] = {"mean": out["board"]["mean"] - rr}
            raw["offrail_share_of_board_drift"] = raw["offrail"]["mean"] / out["board"]["mean"]
            raw["note"] = ("the raw rails still carry the launch step's own settling ramp in this window (24% "
                           "of a 22 W step is unsettled at t0+1.5 s), which is ~6x the leakage signal, so this "
                           "share goes NEGATIVE; it bounds how much of the split the deconvolution carries")
            out["raw_rails"] = raw
        # the same split over the other body windows, pooled per variant
        var = {}
        for key in [f"t0+{s:.1f}" for s in BODY_STARTS]:
            rs = [r["drift_variants"][key] for r in runs if key in r.get("drift_variants", {})]
            if len(rs) < 3:
                continue
            b = mean_se([r["board"] for r in rs])
            e = {"n": len(rs), "rise_c": float(np.mean([r["rise_c"] for r in rs])),
                 "board": {"mean": b[0], "se": b[1]}}
            for tag in ("dec", "raw"):
                tot = np.zeros(len(rs))
                for k in RAILS:
                    tot = tot + np.array([r[f"{tag}_{k}"] for r in rs])
                rm, rse, _ = mean_se(tot.tolist())
                off = [r["board"] - x for r, x in zip(rs, tot.tolist())]
                om, ose, _ = mean_se(off)
                e[tag] = {"rails": {"mean": rm, "se": rse}, "offrail": {"mean": om, "se": ose},
                          "offrail_share_of_board_drift": om / b[0] if b[0] else None}
            var[key] = e
        if var:
            out["body_window_variants"] = var
            out["offrail_share_over_windows"] = {k: v["dec"]["offrail_share_of_board_drift"]
                                                 for k, v in var.items()}
    return out


def offrail_split(rec, card, fit, win):
    """Attribute a configuration's off-rail watts.  Two independent views, never summed:

    'fit'  the published catalogue attribution (unmetered_fit.json): a share of each rail's watts - the
           regulators' delivery loss plus whatever unmetered logic works in step with that rail - leaving an
           unattributed off-rail remainder.
    'temperature'  what the run's own heating puts off the rails: the off-rail within-run drift (the board's
           drift less the three rails') times the rise from the launch reading to the window.
    """
    d = rec[win]
    c = fit[card]["coef"]
    per_s = rec["per_s"]
    pj = lambda w: (w / per_s * 1e12) if per_s else None                               # noqa: E731
    pred = sum(c[k] * d[f"{k}_w"] for k in RAILS)
    out = {"offrail_w": d["offrail_w"], "offrail_pJ": d.get("offrail_pJ"),
           "fit": {"delivery_and_instep_w": pred, "delivery_and_instep_pJ": pj(pred),
                   "per_rail_w": {k: c[k] * d[f"{k}_w"] for k in RAILS},
                   "unattributed_w": d["offrail_w"] - pred, "unattributed_pJ": pj(d["offrail_w"] - pred),
                   "coef": {k: c[k] for k in RAILS}}}
    dr = rec.get("card_drift", {})
    if "offrail" in dr:
        rise = (rec["t_early"] if win == "launch" else rec["t_late"]) - rec["t_launch"]
        heat = dr["offrail"]["mean"] * rise
        out["temperature"] = {"rise_c": rise, "offrail_drift_w_per_c": dr["offrail"]["mean"],
                              "offrail_heating_w": heat, "offrail_heating_pJ": pj(heat),
                              "share_of_offrail": heat / d["offrail_w"] if d["offrail_w"] else None}
    return out


def catalogue_loaddep(cat, card):
    """Is the off-rail remainder's dependence on the rails linear or quadratic?  Over the catalogue's non-DRAM
    bursts: unmetered = a.minion + b.sram + c.noc, then the same with a (sum of rails)^2 term added."""
    bs = [b for b in cat["bursts"][card] if not ("dram" in b["cfg"] and "stride8K" not in b["cfg"])]
    by = collections.defaultdict(list)
    for b in bs:
        by[b["cfg"]].append(b)
    rows = []
    for cfg, v in by.items():
        m = {k: float(np.mean([x[k] for x in v])) for k in ("rail_minion_w", "rail_sram_w", "rail_noc_w", "over_idle_w")}
        m["cfg"] = cfg
        m["sum_w"] = m["rail_minion_w"] + m["rail_sram_w"] + m["rail_noc_w"]
        m["unmetered_w"] = m["over_idle_w"] - m["sum_w"]
        rows.append(m)
    X1 = np.array([[r["rail_minion_w"], r["rail_sram_w"], r["rail_noc_w"]] for r in rows])
    X2 = np.hstack([X1, np.array([[r["sum_w"] ** 2] for r in rows])])
    y = np.array([r["unmetered_w"] for r in rows])
    out = {"n_configs": len(rows), "max_sum_w": float(max(r["sum_w"] for r in rows))}
    for name, X in (("linear", X1), ("with_square", X2)):
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ c
        rms = float(np.sqrt(np.mean(res ** 2)))
        se = rms * np.sqrt(np.diag(np.linalg.inv(X.T @ X)))
        names = ["minion", "sram", "noc"] + (["sum_squared_per_w"] if X.shape[1] == 4 else [])
        out[name] = {"coef": dict(zip(names, map(float, c))), "se": dict(zip(names, map(float, se))), "rms_w": rms}
    q = out["with_square"]
    out["square_t"] = q["coef"]["sum_squared_per_w"] / q["se"]["sum_squared_per_w"]
    out["rms_improvement_w"] = out["linear"]["rms_w"] - q["rms_w"]
    return out


def e64_sustained(root):
    """E64's sustained runs on aifoundry2: the off-rail share of a 60-120 s burst, by the clock the governor held.
    Each telemetry file is one run; its first 2 s are the pre-launch idle.  A phase is a contiguous stretch of at
    least 40 samples (4 s) at one clock with the board at least 5 W over that file's idle, and only its samples
    from 3 s in are used, so the rails' filter has settled (3 s is three time constants)."""
    out = []
    for sess in ("s1", "s2"):
        for f in sorted(glob.glob(os.path.join(root, "docs/reports/data/2026-10-23-e64-horace-power-limit",
                                               sess, "tel", "*.jsonl.gz"))):
            tel = sorted(load_jsonl(f), key=lambda s: s["t_ms"])
            if len(tel) < 200:
                continue
            t = np.array([s["t_ms"] for s in tel], float) / 1e3
            t -= t[0]
            P = np.array([s["board_w"] for s in tel], float)
            mz = np.array([s["mhz"]["minion"] for s in tel], float)
            T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
            R = {k: np.array([s["sp"][k + "_w"][0] for s in tel], float) for k in RAILS}
            V = np.array([s["sp"]["minion_mv"][0] for s in tel], float)
            pre = t <= 2.0
            idle = {"board": float(np.median(P[pre])), **{k: float(np.median(R[k][pre])) for k in RAILS}}
            busy = P > idle["board"] + 5.0
            cut = np.flatnonzero(np.diff(mz) != 0) + 1
            for lo, hi in zip(np.r_[0, cut].tolist(), np.r_[cut, len(mz)].tolist()):
                if hi - lo < 40 or busy[lo:hi].mean() < 0.9:
                    continue
                w = np.zeros(len(t), bool)
                w[lo:hi] = True
                w &= t >= t[lo] + 3.0                              # three time constants after the clock changed
                if w.sum() < 20:
                    continue
                Pw = P[w]
                b = float(Pw[Pw >= np.median(Pw) - 2.0].mean()) - idle["board"]
                r = {k: float(R[k][w].mean()) - idle[k] for k in RAILS}
                tot = sum(r.values())
                out.append({"run": os.path.basename(f).replace(".jsonl.gz", ""), "session": sess,
                            "mhz": int(mz[lo]), "n": int(w.sum()), "secs": float(t[hi - 1] - t[lo]),
                            "minion_mv": float(V[w].mean()), "die_c": float(T[w].mean()),
                            "board_w": b, **{f"{k}_w": r[k] for k in RAILS}, "rails_w": tot,
                            "offrail_w": b - tot, "minion_over_board": r["minion"] / b if b else None,
                            "offrail_share": (b - tot) / b if b else None,
                            "idle_board_w": idle["board"], "idle_offrail_w": idle["board"] - sum(
                                idle[k] for k in RAILS)})
    return out


def apply_footing(rec, win, dr, leak, coef, variant):
    """One configuration's rows on one footing.  See "THE FOOTING" in the module docstring.

    variant 'uncorrected'  the raw window delta (no leakage correction at all)
            'drift_split'  the registered correction taken off the board and distributed over the four rows by
                           their own measured within-run drift slopes  <- the central estimate
            'board_only'   the correction taken off the board alone, rails left raw (E38's literal reduction)
    """
    d, per_s = rec[win], rec["per_s"]
    rise = (rec["t_early"] if win == "launch" else rec["t_late"]) - rec["t_launch"]
    C = 0.0 if variant == "uncorrected" else leak * rise
    w = {k: d[f"{k}_w"] for k in RAILS}
    board = d["board_w"] - C
    if variant == "drift_split":
        for k in RAILS:
            w[k] -= C * (dr[k]["mean"] / dr["board"]["mean"])
    rails = sum(w.values())
    offrail = board - rails
    deliv = sum(coef[k] * w[k] for k in RAILS)
    row = {"board": board, **w, "rails": rails, "offrail": offrail,
           "delivery_and_instep": deliv, "unattributed": offrail - deliv}
    out = {"variant": variant, "leak_w_per_c": leak, "rise_c": rise, "correction_w": C,
           "w": row, "minion_over_board": row["minion"] / board if board else None,
           "rails_over_board": rails / board if board else None}
    if per_s:
        out["pJ"] = {k: v / per_s * 1e12 for k, v in row.items()}
    return out


FOOTINGS = ("uncorrected", "drift_split", "board_only")


def screen_summary(screened):
    """What S2 actually did on one card: which leg fired, the approach distribution, and - for the card whose
    whole campaign it removes - the rail deltas that show why.  Written out so the screen is auditable."""
    if not screened:
        return {}
    app = np.array([s["approach_s"] for s in screened if s["approach_s"] is not None], float)
    legs = collections.Counter(s["leg"] for s in screened)
    out = {"runs_reaching_S2": len(screened), "legs": dict(legs),
           "kept": sum(1 for s in screened if s["kept"]),
           "approach_s": {"p10": float(np.percentile(app, 10)), "median": float(np.median(app)),
                          "min": float(app.min()), "max": float(app.max()),
                          "frac_below_6s": float((app < APPROACH_S).mean())} if len(app) else None,
           "idle_settle_w_abs_median": float(np.median([abs(s["idle_settle_w"]) for s in screened])),
           "far_above_early_w_mean": float(np.mean([s["far_above_early_w"] for s in screened]))}
    ev = {}
    for cfg in ("fp32_zeros", "fp32_randn", "fp32_ones"):
        v = [s for s in screened if s["config"] == cfg]
        if not v:
            continue
        ev[cfg] = {"n": len(v),
                   "minion_early_raw_d_w": float(np.mean([s["minion_early_raw_d"] for s in v])),
                   "minion_early_dec_d_w": float(np.mean([s["minion_early_dec_d"] for s in v])),
                   "minion_early_raw_d_per_pass_w": [s["minion_early_raw_d"] for s in v],
                   "board_early_d_w": float(np.mean([s["board_early_d"] for s in v]))}
    out["rail_deltas_against_the_idle_bracket"] = ev
    out["reading"] = ("a minion-rail delta that is NEGATIVE while the board's is positive (or near zero on a "
                      "pattern that draws nothing) is the filter falling through the window, not the workload")
    return out


def footing_table(out, ok, fit, q128_board_pJ, cfg="fp32_randn"):
    """The headline configuration on all three footings, per card and as the two-card mean, and the two-card
    ratio transferred onto Q128's three-card board figure.  This replaces the first version's single row."""
    res = {"what": "one random fp32 multiply-add on three leakage footings; see THE FOOTING in rail_ledger.py",
           "config": cfg, "q128_board_pJ": q128_board_pJ, "footings": list(FOOTINGS),
           "denominator_note": ("the 5.783 pJ board figure is a THREE-card registered mean (a2 5.920, a3 5.369, "
                                "aifoundry1-c1 6.058); every rail ratio here is a TWO-card measurement, because "
                                "aifoundry1-c1 has no usable E38 rail data (S2 removes all 92 of its runs)"),
           "per_card": {}, "two_card_mean": {}}
    for card in ok:
        rec = out["cards"][card]["per_config"][cfg]
        dr = out["cards"][card]["card_drift_w_per_c"]
        leak = out["cards"][card]["par"]["leak"]
        res["per_card"][card] = {win: {v: apply_footing(rec, win, dr, leak, fit[card]["coef"], v)
                                       for v in FOOTINGS} for win in ("launch", "late")}
    for win in ("launch", "late"):
        res["two_card_mean"][win] = {}
        for v in FOOTINGS:
            per = [res["per_card"][c][win][v] for c in ok]
            m = {k: float(np.mean([p["pJ"][k] for p in per])) for k in per[0]["pJ"]}
            ratio = m["minion"] / m["board"]
            scale = q128_board_pJ / m["board"]
            res["two_card_mean"][win][v] = {
                "pJ": m, "minion_over_board": ratio, "rails_over_board": m["rails"] / m["board"],
                "q128_scale": scale, "on_q128_board_pJ": {k: x * scale for k, x in m.items()},
                "per_card_minion_over_board": {c: res["per_card"][c][win][v]["minion_over_board"] for c in ok},
                "per_card_minion_pJ_on_q128_board": {
                    c: res["per_card"][c][win][v]["minion_over_board"] * q128_board_pJ for c in ok}}
    # the headline band: the three footings at the launch window
    lw = res["two_card_mean"]["launch"]
    mins = {v: lw[v]["on_q128_board_pJ"]["minion"] for v in FOOTINGS}
    res["minion_pJ_band"] = {
        "central_drift_split": mins["drift_split"], "lo_uncorrected": mins["uncorrected"],
        "hi_board_only": mins["board_only"], "q128_carried": 4.33725,
        "per_card_on_central_footing": lw["drift_split"]["per_card_minion_pJ_on_q128_board"],
        "what_the_band_is": ("the leakage treatment, which is the largest single uncertainty: the lower edge "
                             "is no correction at all and the upper edge is the correction taken off the board "
                             "alone.  The two cards on the central footing span a comparable width.")}
    # the third card is assumed, not measured: what its ratio does to the transferred figure
    a2 = lw["drift_split"]["per_card_minion_over_board"].get("aifoundry2")
    rs = list(lw["drift_split"]["per_card_minion_over_board"].values())
    if a2 is not None and len(rs) == 2:
        r3 = (sum(rs) + a2) / 3.0
        res["third_card_sensitivity"] = {
            "two_card_mean_ratio": float(np.mean(rs)),
            "if_a1c1_ratio_equalled_aifoundry2": r3, "minion_pJ_then": r3 * q128_board_pJ,
            "shift_pJ": r3 * q128_board_pJ - float(np.mean(rs)) * q128_board_pJ,
            "why": ("aifoundry1-c1 contributes 6.058 pJ of the three-card 5.783 and launches as hot as "
                    "aifoundry2, whose ratio is the lower of the two measured; assuming its ratio equals "
                    "aifoundry2's is the conservative direction")}
    # the leakage slope itself as a labelled sensitivity (CONTEXT section 2 item 3)
    sens = {}
    for name in ("registered", "measured_within_run", "e66_idle"):
        per = []
        for card in ok:
            rec = out["cards"][card]["per_config"][cfg]
            dr = out["cards"][card]["card_drift_w_per_c"]
            if name == "registered":
                leak = out["cards"][card]["par"]["leak"]
            elif name == "measured_within_run":
                leak = dr["board"]["mean"]
            else:
                leak = E66_IDLE_SLOPE.get(card)
                if leak is None:                       # aifoundry3's idle slope was never measured
                    leak = out["cards"][card]["par"]["leak"]
            per.append((card, leak, apply_footing(rec, "launch", dr, leak, fit[card]["coef"], "drift_split")))
        mb = float(np.mean([p[2]["pJ"]["board"] for p in per]))
        mm = float(np.mean([p[2]["pJ"]["minion"] for p in per]))
        sens[name] = {"leak_w_per_c": {c: l for c, l, _ in per}, "minion_over_board": mm / mb,
                      "minion_pJ_on_q128_board": mm / mb * q128_board_pJ}
    sens["note"] = ("E38's registered reduction uses 0.81 / 0.55 W/C; this ledger's own within-run board slope "
                    "is 0.725 +- 0.019 / 0.358 +- 0.093; E66 measured aifoundry2's IDLE slope at 0.294 W/C over "
                    "51-58 C and aifoundry3's idle slope has never been measured, so that row keeps 0.55 for "
                    "aifoundry3 and is a one-card sensitivity")
    res["leak_slope_sensitivity"] = sens
    return res


def residual_spread(out, ok, fit, cfg_board_min_pJ=1.0):
    """The off-rail fit's residual - the quantity the first version called 'on no meter and attributed to
    nothing' - across every configuration, on the uncorrected and the central footing, with the script's own
    temperature view beside it.  An energy that is really unmetered cannot be negative; this one is, often."""
    res = {"what": ("the off-rail remainder MINUS the published fit's prediction: a FIT RESIDUAL, not a "
                    "measured unmetered energy.  Reported per configuration because it changes sign across "
                    "sibling configurations of the same pattern on the same card."),
           "per_card": {}}
    for card in ok:
        dr = out["cards"][card]["card_drift_w_per_c"]
        leak = out["cards"][card]["par"]["leak"]
        rows = {}
        for cfg, rec in out["cards"][card]["per_config"].items():
            # MAC-unit configurations only: `spin` is per instruction, so its pJ is not comparable
            if not rec["per_s"] or rec["unit"] != "MAC":
                continue
            e = {"minions": rec["minions"], "n_passes": rec["n_passes"],
                 "board_pJ": rec["launch"]["board_pJ"]}
            for v in ("uncorrected", "drift_split"):
                f = apply_footing(rec, "launch", dr, leak, fit[card]["coef"], v)
                e[v] = f["pJ"]["unattributed"]
            t = rec["launch"]["offrail_split"].get("temperature", {})
            e["offrail_heating_pJ"] = t.get("offrail_heating_pJ")
            e["heating_share_of_residual"] = (
                t["offrail_heating_pJ"] / e["uncorrected"] if t.get("offrail_heating_pJ") is not None
                and e["uncorrected"] else None)
            rows[cfg] = e
        # the range is taken over configurations that actually draw power (a residual share is meaningless on a
        # 0.1 pJ board delta); the sign count is taken over every MAC configuration
        big = {c: r for c, r in rows.items() if r["board_pJ"] >= cfg_board_min_pJ}
        v = [r["uncorrected"] for r in big.values()]
        res["per_card"][card] = {
            "per_config_pJ": rows, "n_configs_all": len(rows), "n_configs_over_1pJ": len(v),
            "board_min_pJ_for_the_range": cfg_board_min_pJ,
            "uncorrected_range_pJ": [min(v), max(v)],
            "uncorrected_range_configs": [min(big, key=lambda c: big[c]["uncorrected"]),
                                          max(big, key=lambda c: big[c]["uncorrected"])],
            "n_negative_over_1pJ": sum(1 for x in v if x < 0),
            "n_negative_all": sum(1 for r in rows.values() if r["uncorrected"] < 0),
            "drift_split_range_pJ": [min(r["drift_split"] for r in big.values()),
                                     max(r["drift_split"] for r in big.values())],
            "n_negative_drift_split_over_1pJ": sum(1 for r in big.values() if r["drift_split"] < 0)}
    return res


def hart_law(out, ok, cfg_harts=(("fp32_randn", 1024), ("fp32_randn_16", 512), ("fp32_randn_8", 256))):
    """The minion rail's watts against active harts at 600 MHz, measured here, on each card.  This is the law
    E77 needs to match its two arms' rail power, and it replaces E62-CAL's 800 MHz BOARD law (whose 5.80 W
    offset E65 refuted) in E77-PLAN.md.  The board law is given beside it as a cross-check against E62-CAL."""
    res = {"what": "minion-rail and board watts over idle against active harts, 600 MHz, from this ledger",
           "per_card": {}}
    for card in ok:
        pc = out["cards"][card]["per_config"]
        rungs = [(h, pc[c]) for c, h in cfg_harts if c in pc and pc[c]["per_s"]]
        if len(rungs) < 3:
            continue
        H = np.array([h for h, _ in rungs], float)
        e = {"rungs": [{"harts": h, "minions": r["minions"], "n_passes": r["n_passes"],
                        "minion_w": r["launch"]["minion_w"], "minion_se_w": r["launch"]["minion_se_w"],
                        "board_w": r["launch"]["board_w"], "minion_mv": r["mv"]["minion"]}
                       for h, r in rungs]}
        for tag, key in (("minion", "minion_w"), ("board", "board_w")):
            W = np.array([r["launch"][key] for _, r in rungs], float)
            A = np.vstack([H, np.ones(len(H))]).T
            (sl, off), *_ = np.linalg.lstsq(A, W, rcond=None)
            e[tag] = {"offset_w": float(off), "mw_per_hart": float(sl * 1e3),
                      "mw_per_hart_through_zero": float((H * W).sum() / (H * H).sum() * 1e3)}
        e["note"] = ("the offset is within half a watt of zero on both cards and both quantities, which is "
                     "E65's reading (-0.51 +- 0.03 W + 27.1 mW/hart at the board on aifoundry3) and not "
                     "E62-CAL's 5.80 W")
        res["per_card"][card] = e
    # the f.V^2 transfer to 800 MHz, and E62-CAL as an independent check of it
    a2 = res["per_card"].get("aifoundry2")
    if a2:
        v600 = a2["rungs"][0]["minion_mv"]
        V800, F = 618.0, 800.0 / 600.0
        k = F * (V800 / v600) ** 2
        res["to_800mhz"] = {
            "minion_mv_600": v600, "minion_mv_800": V800, "f_ratio": F,
            "v2_ratio": (V800 / v600) ** 2, "per_hart_ratio_800_over_600": k,
            "arm_b_harts_per_arm_a_hart": 1.0 / k,
            "minion_mw_per_hart_800_predicted": a2["minion"]["mw_per_hart"] * k,
            "board_mw_per_hart_800_predicted": a2["board"]["mw_per_hart"] * k,
            "board_mw_per_hart_800_measured_e62cal": 55.8,
            "board_check": ("E62-CAL measured 5.80 +- 0.30 W + 55.8 +- 1.0 mW per hart at the BOARD at "
                            "800 MHz on this card; scaling this ledger's measured 600 MHz board slope by "
                            "f.V^2 predicts that slope, which is what licenses the same transfer on the "
                            "minion rail")}
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", help="also write the printed table here")
    a = ap.parse_args()
    root = a.root
    sys.path.insert(0, os.path.join(root, "tools", "ettelem"))
    import deconv                                                            # noqa: E402

    D = os.path.join(root, "docs/reports/data")
    out = {"what": "per-rail ledger of one random fp32 multiply-add, from committed E38 telemetry; no card was run",
           "sources": {
               "e38": "docs/reports/data/2026-09-25-claims-v3/raw/<card>/abla/p[1-4] (E38/E39, 25-26 Sep 2026)",
               "catalogue": "docs/reports/data/2026-09-23-energy-manual/catalogue.json (E46 full catalogue)",
               "published_fit": "docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json",
               "rail_meaning": "docs/findings/14-card-behaviour.md, 'The telemetry, and what each number really is'"},
           "windows": {"idle": "[t0-2.0, t0-0.3] s", "launch": "[t0+1, t0+3] s (board p_early with the registered "
                       "dropout rule; rails deconvolved to the same window)", "late": "[t1-1.0, t1] s, both raw"},
           "cards": {}}
    lines = []
    fit = json.load(open(os.path.join(D, "2026-09-23-energy-manual/unmetered_fit.json")))
    out["published_fit_coef"] = {c: fit[c]["coef"] for c in CARDS}
    for card in CARDS:
        runs, drops, screened = [], collections.Counter(), []
        for d in sorted(glob.glob(os.path.join(D, "2026-09-25-claims-v3/raw", card, "abla", "p[0-9]*"))):
            if os.path.exists(os.path.join(d, "telemetry.jsonl.gz")):
                runs += pass_runs(d, card, deconv, drops, screened)
        per_cfg = ledger_rows(runs, card)
        cd = card_drift(runs)
        for cfg, rec in per_cfg.items():
            rec["card_drift"] = cd
            for win in ("launch", "late"):
                rec[win]["offrail_split"] = offrail_split(rec, card, fit, win)
            del rec["card_drift"]
        out["cards"][card] = {"kept_runs": len(runs), "screened_out": dict(drops), "par": PAR[card],
                              "card_drift_w_per_c": cd, "screen_evidence": screen_summary(screened),
                              "per_config": per_cfg}
        lines.append(f"{card}: {len(runs)} runs kept, screened out {dict(drops)}")
    ok = [c for c in CARDS if out["cards"][c]["kept_runs"] >= 8 and "fp32_randn" in out["cards"][c]["per_config"]]
    out["cards_in_the_ledger"] = ok
    out["cards_excluded"] = {c: "S2: the idle bracket's rails never settled in this campaign (preheat up to 2 s "
                                "before the launch, approach 2.3 s at the tenth percentile), so a rail delta "
                                "against it is the filter, not the workload" for c in CARDS if c not in ok}

    cat = json.load(open(os.path.join(D, "2026-09-23-energy-manual/catalogue.json")))
    out["load_dependence"] = {c: catalogue_loaddep(cat, c) for c in CARDS if c in cat["bursts"]}
    out["e64_sustained"] = e64_sustained(root)

    # ---- the headline: one random fp32 multiply-add, the mean of the cards that pass the screens ------------
    head = {}
    for win in ("launch", "late"):
        per_card = {c: out["cards"][c]["per_config"]["fp32_randn"][win] for c in ok}
        head[win] = {k: float(np.mean([per_card[c][f"{k}_pJ"] for c in ok])) for k in
                     ("board", "minion", "sram", "noc", "rails", "offrail")}
        head[win]["per_card_pJ"] = {c: {k: per_card[c][f"{k}_pJ"] for k in
                                        ("board", "minion", "sram", "noc", "rails", "offrail")} for c in ok}
        head[win]["per_card_minion_over_board"] = {c: per_card[c]["minion_over_board"] for c in ok}
        head[win]["minion_over_board"] = float(np.mean([per_card[c]["minion_over_board"] for c in ok]))
        head[win]["rails_over_board"] = float(np.mean([per_card[c]["rails_over_board"] for c in ok]))
        head[win]["fit_delivery_pJ"] = float(np.mean([per_card[c]["offrail_split"]["fit"]["delivery_and_instep_pJ"]
                                                      for c in ok]))
        head[win]["fit_unattributed_pJ"] = float(np.mean([per_card[c]["offrail_split"]["fit"]["unattributed_pJ"]
                                                          for c in ok]))
    head["footing"] = ("UNCORRECTED window deltas.  This block is the raw measurement; it is NOT on the same "
                       "footing as Q128's registered board figure or the catalogue's published fit, both of "
                       "which have the window's own die heating removed.  Use `footings` for any number that "
                       "is transferred onto either of them.")
    out["random_fp32_mac"] = head

    # scale the ledger's shares onto Q128's registered 5.783 pJ board figure, which is what the waterfall uses
    Q128_BOARD_PJ = 5.783
    for win in ("launch", "late"):
        h = head[win]
        s = Q128_BOARD_PJ / h["board"]
        h["on_q128_board_pJ"] = {k: h[k] * s for k in ("board", "minion", "sram", "noc", "rails", "offrail",
                                                       "fit_delivery_pJ", "fit_unattributed_pJ")}
        h["q128_scale"] = s
        h["q128_minion_rail_pJ_was"] = 4.33725
        h["q129_minion_rail_pJ_is"] = h["minion"] * s
        h["scale_caveat"] = ("a proportional scale, which is the wrong operation for an additive leakage term; "
                             "see `footings`")

    # ---- the three footings, the fit residual's spread, and the 600 MHz hart law E77 needs ------------------
    out["footings"] = footing_table(out, ok, fit, Q128_BOARD_PJ)
    out["fit_residual_spread"] = residual_spread(out, ok, fit)
    out["hart_law_600mhz"] = hart_law(out, ok)

    # E60's own card is aifoundry3 (transistor-ledger.json: "aifoundry3 at 600 MHz and 521.9 mV"), so E60's
    # window attenuation must be read off aifoundry3, not aifoundry2.  And the correction is one-sided.
    E60_CARD, E60_RATIOS = "aifoundry3", (0.7455, 0.7497)
    att3 = out["cards"][E60_CARD]["per_config"]["fp32_randn"]["e60_window_attenuation"]["minion"]["mean"]
    out["e60_inference"] = {
        "card": E60_CARD, "attenuation": att3, "e60_ratios": list(E60_RATIOS),
        "upper_bound": [r / att3 for r in E60_RATIOS],
        "with_aifoundry2_attenuation_instead": [
            r / out["cards"]["aifoundry2"]["per_config"]["fp32_randn"]["e60_window_attenuation"]["minion"]["mean"]
            for r in E60_RATIOS],
        "noc_attenuation_aifoundry2": out["cards"]["aifoundry2"]["per_config"]["fp32_randn"][
            "e60_window_attenuation"].get("noc", {}).get("mean"),
        "why_upper_bound": ("two further biases in E60's own reduction push the same way and are NOT removed "
                            "here: its board is the leakage-corrected p80 while its rail is raw, and its rail "
                            "window sits 1 s later and hotter than its board window.  Both raise E60's measured "
                            "ratio, so dividing by the window attenuation alone over-corrects"),
        "status": ("an inference about E60's reduction, not a re-reduction of it; it must be confirmed against "
                   "E60's own harness before any published number of E60's is restated")}

    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    # name the output relative to the repo root when it is inside it, so this text file never carries a
    # machine's absolute path into a public repository however the script was invoked
    try:
        shown = os.path.relpath(os.path.abspath(a.out), os.path.abspath(root))
    except ValueError:
        shown = os.path.basename(a.out)
    lines.append(f"wrote {shown if not shown.startswith('..') else os.path.basename(a.out)}")

    # ---- printed table -------------------------------------------------------------------------------------
    def fm(v, k=3):
        return "    -  " if v is None else f"{v:7.{k}f}"

    for win in ("launch", "late"):
        lines.append("")
        lines.append(f"== {win} window: pJ per unit, per rail, per card ==")
        lines.append(f"{'config':15s}{'card':12s}{'unit':6s}{'board':>8s}{'minion':>8s}{'sram':>8s}{'noc':>8s}"
                     f"{'rails':>8s}{'offrail':>8s}{'min/bd':>8s}{'off%':>7s}{'deliv':>8s}{'unattr':>8s}")
        for cfg in WANT:
            for card in ok:
                r = out["cards"][card]["per_config"].get(cfg)
                if not r or "board_pJ" not in r[win]:
                    continue
                d = r[win]
                sp = d["offrail_split"]["fit"]
                lines.append(f"{cfg:15s}{card:12s}{r['unit'] or '':6s}{fm(d['board_pJ'])}{fm(d['minion_pJ'])}"
                             f"{fm(d['sram_pJ'])}{fm(d['noc_pJ'])}{fm(d['rails_pJ'])}{fm(d['offrail_pJ'])}"
                             f"{fm(d['minion_over_board'])}{100 * d['offrail_share']:7.1f}"
                             f"{fm(sp['delivery_and_instep_pJ'])}{fm(sp['unattributed_pJ'])}")
    lines.append("")
    lines.append(f"== one random fp32 multiply-add, mean over {', '.join(ok)} (pJ) ==")
    for win in ("launch", "late"):
        h = head[win]
        lines.append(f"{win:7s} board {h['board']:.3f}  minion {h['minion']:.3f}  sram {h['sram']:.3f}  "
                     f"noc {h['noc']:.3f}  rails {h['rails']:.3f}  off-rail {h['offrail']:.3f}  "
                     f"minion/board {h['minion_over_board']:.3f}  rails/board {h['rails_over_board']:.3f}")
        lines.append(f"        off-rail splits as delivery+in-step {h['fit_delivery_pJ']:.3f} + "
                     f"unattributed {h['fit_unattributed_pJ']:.3f}")
        q = h["on_q128_board_pJ"]
        lines.append(f"        on Q128's 5.783 pJ board: minion {q['minion']:.3f} (Q128 carried 4.337)  "
                     f"sram {q['sram']:.3f}  noc {q['noc']:.3f}  off-rail {q['offrail']:.3f} "
                     f"(delivery {q['fit_delivery_pJ']:.3f} + unattributed {q['fit_unattributed_pJ']:.3f})"
                     f"  [scale {h['q128_scale']:.4f}]")
    lines.append("")
    lines.append("== ONE RANDOM FP32 MULTIPLY-ADD ON THREE LEAKAGE FOOTINGS (launch window, pJ) ==")
    ft = out["footings"]
    lines.append(f"{'footing':14s}{'board':>8s}{'minion':>8s}{'sram':>8s}{'noc':>8s}{'offrail':>9s}"
                 f"{'deliv':>8s}{'resid':>8s}{'min/bd':>8s}   on Q128's 5.783 pJ board: minion")
    for v in FOOTINGS:
        m = ft["two_card_mean"]["launch"][v]
        p = m["pJ"]
        lines.append(f"{v:14s}{p['board']:8.3f}{p['minion']:8.3f}{p['sram']:8.3f}{p['noc']:8.3f}"
                     f"{p['offrail']:9.3f}{p['delivery_and_instep']:8.3f}{p['unattributed']:8.3f}"
                     f"{m['minion_over_board']:8.3f}   {m['on_q128_board_pJ']['minion']:.3f} pJ  "
                     f"(per card " + " / ".join(f"{x:.3f}" for x in
                                                m['per_card_minion_pJ_on_q128_board'].values()) + ")")
    bd = ft["minion_pJ_band"]
    lines.append(f"  >> the minion rail is {bd['central_drift_split']:.2f} pJ, band "
                 f"{bd['lo_uncorrected']:.2f}-{bd['hi_board_only']:.2f} over the leakage treatment; "
                 f"Q128 carries {bd['q128_carried']:.3f}")
    t3 = ft.get("third_card_sensitivity", {})
    if t3:
        lines.append(f"  >> the board denominator is a THREE-card mean and the ratio a TWO-card one: if "
                     f"aifoundry1-c1's ratio equalled aifoundry2's, {t3['minion_pJ_then']:.3f} pJ "
                     f"({t3['shift_pJ']:+.3f})")
    ls = ft["leak_slope_sensitivity"]
    for name in ("registered", "measured_within_run", "e66_idle"):
        s = ls[name]
        lines.append(f"  leak slope {name:20s} " + " ".join(f"{c} {l:.3f}" for c, l in s['leak_w_per_c'].items())
                     + f"  -> minion {s['minion_pJ_on_q128_board']:.3f} pJ (ratio {s['minion_over_board']:.3f})")
    lines.append("")
    lines.append("== the off-rail fit's RESIDUAL across configurations (launch, pJ per unit) ==")
    lines.append("   (the quantity the first version of this ledger called 'on no meter and attributed to "
                 "nothing')")
    for card in ok:
        r = out["fit_residual_spread"]["per_card"][card]
        lines.append(f"{card:14s}{r['n_configs_over_1pJ']:2d} configurations over 1 pJ: uncorrected "
                     f"{r['uncorrected_range_pJ'][0]:+.3f} ({r['uncorrected_range_configs'][0]}) to "
                     f"{r['uncorrected_range_pJ'][1]:+.3f} ({r['uncorrected_range_configs'][1]}) pJ, NEGATIVE "
                     f"in {r['n_negative_over_1pJ']} of them and {r['n_negative_all']} of all "
                     f"{r['n_configs_all']}; on the central footing {r['drift_split_range_pJ'][0]:+.3f} to "
                     f"{r['drift_split_range_pJ'][1]:+.3f} (negative in "
                     f"{r['n_negative_drift_split_over_1pJ']})")
        for cfg in ("fp32_randn", "fp32_randn_16", "fp32_randn_8"):
            e = r["per_config_pJ"].get(cfg)
            if e:
                hs = e["heating_share_of_residual"]
                lines.append(f"              {cfg:15s} {e['minions']:5d} harts  residual "
                             f"{e['uncorrected']:+.3f} pJ (corrected {e['drift_split']:+.3f}); the window's own "
                             f"off-rail heating is {e['offrail_heating_pJ']:+.3f} pJ"
                             + (f" = {100*hs:.0f}% of it" if hs else ""))
    lines.append("")
    lines.append("== the minion rail against active harts at 600 MHz, measured here (what E77 matches on) ==")
    for card, e in out["hart_law_600mhz"]["per_card"].items():
        lines.append(f"{card:14s}" + "  ".join(f"{r['harts']}h {r['minion_w']:.2f} W" for r in e["rungs"])
                     + f"   -> minion rail {e['minion']['offset_w']:+.3f} W + "
                       f"{e['minion']['mw_per_hart']:.2f} mW/hart  (board "
                       f"{e['board']['offset_w']:+.3f} W + {e['board']['mw_per_hart']:.2f} mW/hart)")
    t8 = out["hart_law_600mhz"].get("to_800mhz")
    if t8:
        lines.append(f"  f.V^2 to 800 MHz: x{t8['per_hart_ratio_800_over_600']:.3f} per hart, so an 800 MHz arm "
                     f"needs {t8['arm_b_harts_per_arm_a_hart']:.3f} x the harts for the same rail watts")
        lines.append(f"  check: that transfer predicts {t8['board_mw_per_hart_800_predicted']:.1f} mW/hart at "
                     f"the board at 800 MHz; E62-CAL measured {t8['board_mw_per_hart_800_measured_e62cal']} "
                     f"+- 1.0")
    lines.append("")
    lines.append("== the deconvolution's closure check: a quiet pattern's deconvolved launch vs its settled "
                 "late reading (absolute W) ==")
    for card in ok:
        aw = out["cards"][card]["per_config"]["fp32_zeros"]["abs_w"]["minion"]
        lines.append(f"{card:14s}launch deconvolved {aw['launch_dec']:.3f} W  vs  late raw "
                     f"{aw['late_raw']:.3f} W   -> {1000*aw['closure_w']:+.0f} mW")
    lines.append("")
    lines.append("== within-run drift against the die reading, W per C (pooled over the card's heating runs) ==")
    for card in ok:
        dr = out["cards"][card]["card_drift_w_per_c"]
        lines.append(f"{card:14s}" + "  ".join(
            f"{k} {v['mean']:+.3f}" + (f"+-{v['se']:.3f}" if v.get("se") is not None else "")
            for k, v in dr.items() if isinstance(v, dict) and "mean" in v))
        sh = dr.get("offrail_share_per_run", {})
        lines.append(f"              off-rail share of the board's drift "
                     f"{dr['offrail_share_of_board_drift']:.2f}+-{dr['offrail_share_se']:.2f} "
                     f"(per run {sh.get('mean', float('nan')):.2f}+-{sh.get('se', float('nan')):.2f}, "
                     f"n {dr['board']['n']}, mean rise {dr['rise_c']:.1f} C, {len(dr['configs'])} configurations)")
        wv = dr.get("offrail_share_over_windows", {})
        if wv:
            lines.append("              over body windows " + ", ".join(f"{k} {v:.2f}" for k, v in wv.items())
                         + f"   |  RAW rails (no deconvolution): share "
                           f"{dr['raw_rails']['offrail_share_of_board_drift']:+.2f} "
                           f"(rails {dr['raw_rails']['rails']['mean']:+.3f} W/C) - the launch step is still "
                           f"settling here, so this is a bound on the deconvolution, not a reading")
    lines.append("")
    lines.append("== idle split, W (fp32_randn's own pre-launch brackets) ==")
    for card in ok:
        iw = out["cards"][card]["per_config"]["fp32_randn"]["idle_w"]
        lines.append(f"{card:14s}board {iw['board']:6.2f}  minion {iw['minion']:6.2f}  sram {iw['sram']:5.2f}  "
                     f"noc {iw['noc']:5.2f}  rails {iw['rails']:6.2f}  off-rail {iw['offrail']:6.2f} "
                     f"({100 * iw['offrail_share']:.0f}%)")
    lines.append("")
    lines.append("== E60's rail window, measured: its raw delta over the settled delta (fp32_randn) ==")
    for card in ok:
        att = out["cards"][card]["per_config"]["fp32_randn"]["e60_window_attenuation"]
        lines.append(f"{card:14s}" + "  ".join(f"{k} {v['mean']:.3f}+-{v['se']:.3f} (n{v['n']})"
                                               for k, v in att.items()))
    ei = out["e60_inference"]
    lines.append(f"  E60 ran on {ei['card']}, so its own attenuation is {ei['attenuation']:.4f}: its "
                 f"{ei['e60_ratios']} would become {' / '.join(f'{x:.3f}' for x in ei['upper_bound'])}, an "
                 f"UPPER BOUND - {ei['why_upper_bound']}")
    lines.append(f"  and one tau does not explain every rail: the NoC returns "
                 f"{ei['noc_attenuation_aifoundry2']:.3f} on the same runs and the same window, so the "
                 f"single-time-constant picture is incomplete")
    lines.append("")
    lines.append("== E64 sustained on aifoundry2: off-rail share by the clock the governor held ==")
    lines.append(f"{'run':34s}{'MHz':>5s}{'mV':>5s}{'die C':>7s}{'board W':>9s}{'minion W':>9s}"
                 f"{'off W':>8s}{'min/bd':>8s}{'off%':>7s}{'s':>6s}")
    for r in sorted(out["e64_sustained"], key=lambda x: (-x["board_w"])):
        if r["board_w"] < 4:
            continue
        lines.append(f"{r['run'][:34]:34s}{r['mhz']:5d}{r['minion_mv']:5.0f}{r['die_c']:7.1f}{r['board_w']:9.2f}"
                     f"{r['minion_w']:9.2f}{r['offrail_w']:8.2f}{r['minion_over_board']:8.3f}"
                     f"{100 * r['offrail_share']:7.1f}{r['secs']:6.1f}")
    lines.append("")
    lines.append("== off-rail remainder: linear in the rails, or quadratic? (catalogue, non-DRAM) ==")
    for card, v in out["load_dependence"].items():
        lin, sq = v["linear"], v["with_square"]
        lines.append(f"{card:14s}n {v['n_configs']:3d}  max sum of rails {v['max_sum_w']:.1f} W")
        lines.append(f"              linear: {lin['coef']['minion']:.4f} minion + {lin['coef']['sram']:.4f} sram "
                     f"+ {lin['coef']['noc']:.4f} noc, rms {lin['rms_w']:.4f} W")
        lines.append(f"              +square: {sq['coef']['minion']:.4f} / {sq['coef']['sram']:.4f} / "
                     f"{sq['coef']['noc']:.4f} + {sq['coef']['sum_squared_per_w']:.5f}+-"
                     f"{sq['se']['sum_squared_per_w']:.5f} per W^2, rms {sq['rms_w']:.4f} W, t {v['square_t']:+.2f}")
    text = "\n".join(lines)
    print(text)
    if a.text:
        with open(a.text, "w") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()
