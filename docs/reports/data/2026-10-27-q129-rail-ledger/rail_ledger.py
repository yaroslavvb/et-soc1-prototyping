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

The per-rail within-run temperature slope is each rail's deconvolved power regressed on the die reading over
[t0+2, t1-0.2] s for the runs that heat the die by at least 3 C, beside the board's own slope from the same
samples - which is how the board's leakage correction is split between the rails and the off-rail remainder.

Screens (declared here, applied below, every exclusion counted)
---------------------------------------------------------------
S1  every launch record printed ok, and mhz.minion == 600 over [t0-2, t1] - E38's own keep rule.
S2  the idle bracket's rails must be SETTLED: |minion over [t0-5, t0-3] minus minion over [t0-2, t0-0.3]| <=
    0.15 W, and the strict start's approach >= 6 s (six time constants).  A rail delta is a difference against
    that bracket, so a bracket still falling from the preheat makes the delta meaningless.  This screen removes
    aifoundry1-c1's whole E38 campaign: its approach was 2.3 s at the tenth percentile, and its preheat runs up
    to 2 s before the launch, so the minion rail enters the run 10-20 W above its idle level and falls through
    it (its fp32_zeros rail delta reads -1.5 W, i.e. the filter, not the workload).  aifoundry2 (approach
    median 15.6 s) and aifoundry3 (39.9 s) pass it.
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


def pass_runs(d, card, deconv, drops):
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
        if abs(settle) > SETTLE_W or app is None or app / 1e3 < APPROACH_S:
            drops["S2_rails_not_settled"] += 1
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
        out["rails"] = {"mean": sum(out[k]["mean"] for k in RAILS), "n": out["board"]["n"]}
        out["offrail"] = {"mean": out["board"]["mean"] - out["rails"]["mean"], "n": out["board"]["n"]}
        out["offrail_share_of_board_drift"] = out["offrail"]["mean"] / out["board"]["mean"]
        # same thing per run, so the share gets an interval of its own
        sh = [(r["drift_board_w_per_c"] - sum(r[f"drift_{k}_w_per_c"] for k in RAILS)) / r["drift_board_w_per_c"]
              for r in runs if "drift_board_w_per_c" in r and abs(r["drift_board_w_per_c"]) > 0.1]
        if sh:
            m, se, n = mean_se(sh)
            out["offrail_share_per_run"] = {"mean": m, "se": se, "n": n}
        out["rise_c"] = mean_se([r["drift_rise_c"] for r in runs if "drift_rise_c" in r])[0]
        out["configs"] = sorted({r["config"] for r in runs if "drift_board_w_per_c" in r})
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
        runs, drops = [], collections.Counter()
        for d in sorted(glob.glob(os.path.join(D, "2026-09-25-claims-v3/raw", card, "abla", "p[0-9]*"))):
            if os.path.exists(os.path.join(d, "telemetry.jsonl.gz")):
                runs += pass_runs(d, card, deconv, drops)
        per_cfg = ledger_rows(runs, card)
        cd = card_drift(runs)
        for cfg, rec in per_cfg.items():
            rec["card_drift"] = cd
            for win in ("launch", "late"):
                rec[win]["offrail_split"] = offrail_split(rec, card, fit, win)
            del rec["card_drift"]
        out["cards"][card] = {"kept_runs": len(runs), "screened_out": dict(drops), "par": PAR[card],
                              "card_drift_w_per_c": cd, "per_config": per_cfg}
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

    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    lines.append(f"wrote {a.out}")

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
    lines.append("== within-run drift against the die reading, W per C (pooled over the card's heating runs) ==")
    for card in ok:
        dr = out["cards"][card]["card_drift_w_per_c"]
        lines.append(f"{card:14s}" + "  ".join(
            f"{k} {v['mean']:+.3f}" + (f"+-{v['se']:.3f}" if v.get("se") is not None else "")
            for k, v in dr.items() if isinstance(v, dict) and "mean" in v))
        sh = dr.get("offrail_share_per_run", {})
        lines.append(f"              off-rail share of the board's drift {dr['offrail_share_of_board_drift']:.2f} "
                     f"(per run {sh.get('mean', float('nan')):.2f}+-{sh.get('se', float('nan')):.2f}, "
                     f"n {dr['board']['n']}, mean rise {dr['rise_c']:.1f} C, {len(dr['configs'])} configurations)")
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
