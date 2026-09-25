#!/usr/bin/env python3
"""Data for the DVFS / leakage report: governor transitions, the wake-up probe, and the long-idle check.

    analyze_dvfs.py --cold <cold1-dir> <cold2-dir> --wakeup <dir> --idle <idle.jsonl[.gz]> \
                    --since <runs.jsonl[.gz] of the last workload before the idle sample> \
                    --model model.json --ablation ablation.json [--sptrace sptrace-aifoundry3.bin] \
                    [--cool-passes <dir>...] [--idle-sessions <root>...] [--tl-range 30 45] --out dvfs.json

The page's data, from the repo root:

    D=docs/reports/data; H=$D/2026-09-21-horace-aifoundry2; R2=$D/2026-09-23-reruns-aifoundry2
    python3 tools/ettelem/analyze_dvfs.py --cold $H/cold1 $H/cold2 \
        --wakeup $D/2026-09-22-dvfs-aifoundry2/wakeup --idle $D/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz \
        --since $H/long2/runs.jsonl.gz --model $H/model.json \
        --ablation $H/ablation.json --sptrace $D/2026-09-22-cards/sptrace-aifoundry3.bin \
        --cool-passes $R2/hotline-pass2 $R2/hotline-pass3 $R2/hotline-pass4 $R2/relay-pass1 $R2/relay-pass2 $R2/relay-pass4 \
        --idle-sessions $H $D/2026-09-2[234]-* \
        --out $D/2026-09-22-dvfs-aifoundry2/dvfs.json

--cool-passes adds the governor's timing on a second day (governor_days); --idle-sessions tests the idle law on
every session under those directories that it was not fitted on, on both cards (idle_sessions); leak_split gives
the law's split into fixed and leakage power at the two ends of --tl-range (added 25 September 2026, version 3 of
the claims check, docs/reports/data/2026-09-25-claims-v3).

then build_cards_data.py ... --merge $D/2026-09-22-dvfs-aifoundry2/dvfs.json (tools/ettelem/finish_horace.sh runs it).

Fits nothing. Every number is either read from telemetry or computed from it. The three-machine block
("cards") is merged in afterwards by build_cards_data.py --merge dvfs.json; when --out already holds one, it is
carried over, so rerunning this script alone does not drop it.

A down-step is attributed to the thermal test if the die reading was above 65 °C, to the power test if board
power was above 65 W, to both if both; any other down-step is "unattributed": neither test fired on the values
we sampled at 10 Hz. "why" reads the first sample that shows the new clock, "why_prev" the last sample before
it; the board meter lags the clock by about 0.3 s (0-0.5 s, governor_days.meter_lag_s), so the two can differ. (Launches run back to back every
0.37–0.49 s, so every instant is within 0.25 s of a kernel boundary; distance to a boundary is kept in the data
but explains nothing.)

The operating points' voltages are the median on-die minion reading (die_mv.minion) while a kernel runs, in
the cool-start sessions, over samples whose clock equals the previous sample's.
"""
import argparse
import collections
import gzip
import json
import os
import re
import statistics as st
import struct

import numpy as np

TDP_W = 65.0        # POWER_THRESHOLD_SW_MANAGED, thermal_pwr_mgmt.h
T_THRESHOLD_C = 65  # TEMP_THRESHOLD_SW_MANAGED
CLOCK_HZ = 600e6    # the wake-up probe ran at the lowest operating point
UNATTRIBUTED = "unattributed (reading ≤65 °C)"


def jsonl(path):
    op = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    out = []
    for line in op:
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def cause(T, P):
    return ("thermal+power" if (T > T_THRESHOLD_C and P > TDP_W) else
            "thermal" if T > T_THRESHOLD_C else
            "power" if P > TDP_W else
            UNATTRIBUTED)


def volts(cold_dirs):
    """Median on-die minion voltage per clock while a kernel runs: samples inside a launch whose clock equals
    the previous sample's (so not the sample at a step), in volts, rounded to 1 mV."""
    byf = collections.defaultdict(list)
    for d in cold_dirs:
        tel = jsonl(os.path.join(d, "telemetry.jsonl.gz"))
        t = np.array([s["t_ms"] for s in tel]) / 1000.0
        f = np.array([s["mhz"]["minion"] for s in tel])
        mv = np.array([s["die_mv"]["minion"] for s in tel])
        inside = np.zeros(len(t), bool)
        for r in jsonl(os.path.join(d, "runs.jsonl")):
            inside |= (t >= r["t_start_ms"] / 1000.0) & (t <= r["t_end_ms"] / 1000.0)
        for i in range(1, len(t)):
            if inside[i] and f[i] == f[i - 1]:
                byf[int(f[i])].append(int(mv[i]))
    return {f: round(float(np.median(v)) / 1000.0, 3) for f, v in sorted(byf.items())}, {f: len(v) for f, v in sorted(byf.items())}


def rest_before(d):
    """The card at rest before a session's first launch: for cold1, after an overnight idle (the idle law's
    overnight point, flip_thermal_model.py's --anchor)."""
    tel = jsonl(os.path.join(d, "telemetry.jsonl.gz"))
    first = min(r["t_start_ms"] for r in jsonl(os.path.join(d, "runs.jsonl")) if "t_start_ms" in r)
    pre = [s for s in tel if s["t_ms"] < first]
    P = np.array([s["board_w"] for s in pre])
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in pre])
    return {"session": os.path.basename(os.path.normpath(d)), "samples": len(pre),
            "seconds": round((first - pre[0]["t_ms"]) / 1000.0, 1) if pre else 0.0,
            "board_w": float(P.mean()), "board_sd": float(P.std()), "die_c": float(T.mean()),
            "die_c_range": [int(T.min()), int(T.max())], "mhz": sorted({int(s["mhz"]["minion"]) for s in pre})}


def transitions(cold_dirs):
    """Every minion-clock change in the cool-start runs, with the state that explains it."""
    rows, osc = [], []
    for d in cold_dirs:
        tel = jsonl(os.path.join(d, "telemetry.jsonl.gz"))
        t = np.array([s["t_ms"] for s in tel]) / 1000.0
        P = np.array([s["board_w"] for s in tel])
        T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
        f = np.array([s["mhz"]["minion"] for s in tel])
        mv = np.array([s["die_mv"]["minion"] for s in tel])
        procs = []
        for r in jsonl(os.path.join(d, "runs.jsonl")):
            if r["launch"] == -1:
                procs.append([])
            procs[-1].append(r)
        for k, proc in enumerate(procs):
            t0, t1 = proc[0]["t_start_ms"] / 1000.0, proc[-1]["t_end_ms"] / 1000.0
            bounds = [l["t_end_ms"] / 1000.0 for l in proc] + [l["t_start_ms"] / 1000.0 for l in proc]
            sel = (t >= t0 - 0.5) & (t <= t1 + 0.5)
            tt, ff, TT, PP, vv = t[sel], f[sel], T[sel], P[sel], mv[sel]
            changes = []
            for i in range(1, len(ff)):
                if ff[i] == ff[i - 1]:
                    continue
                near = min(abs(tt[i] - b) for b in bounds)
                up = ff[i] > ff[i - 1]
                why = cause(TT[i], PP[i])
                rows.append({"session": os.path.basename(d), "values": proc[0]["values"], "t": round(tt[i] - t0, 2),
                             "dir": "up" if up else "down", "f0": int(ff[i - 1]), "f1": int(ff[i]),
                             "mv0": int(vv[i - 1]), "mv1": int(vv[i]), "T": int(TT[i]), "P": round(float(PP[i]), 1),
                             "gap_to_boundary_ms": round(near * 1000), "why": None if up else why,
                             "proc": k, "T_prev": int(TT[i - 1]), "P_prev": round(float(PP[i - 1]), 1),
                             "why_prev": None if up else cause(TT[i - 1], PP[i - 1])})
                changes.append(tt[i] - t0)
            # step-up latency and oscillation period within the run
            ups = [r for r in rows if r["session"] == os.path.basename(d) and r["dir"] == "up"]
            if changes:
                osc.append({"session": os.path.basename(d), "values": proc[0]["values"], "proc": k,
                            "first_change_s": round(changes[0], 2), "n_changes": len(changes),
                            "span_s": round(changes[-1] - changes[0], 2)})
    return rows, osc


def traces(cold_dirs, want):
    """10 Hz clock, temperature, power and minion voltage for the named runs, for the governor figure."""
    out = []
    for d in cold_dirs:
        tel = jsonl(os.path.join(d, "telemetry.jsonl.gz"))
        t = np.array([s["t_ms"] for s in tel]) / 1000.0
        P = np.array([s["board_w"] for s in tel])
        T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
        f = np.array([s["mhz"]["minion"] for s in tel])
        mv = np.array([s["die_mv"]["minion"] for s in tel])
        procs = []
        for r in jsonl(os.path.join(d, "runs.jsonl")):
            if r["launch"] == -1:
                procs.append([])
            procs[-1].append(r)
        for k, proc in enumerate(procs):
            key = (os.path.basename(d), proc[0]["values"], k)
            if key not in want:
                continue
            t0, t1 = proc[0]["t_start_ms"] / 1000.0, proc[-1]["t_end_ms"] / 1000.0
            sel = (t >= t0 - 0.5) & (t <= t1 + 1.0)
            out.append({"session": key[0], "values": key[1], "dur": round(t1 - t0, 2),
                        "t": [round(x, 2) for x in (t[sel] - t0)],
                        "mhz": [int(x) for x in f[sel]], "T": [float(x) for x in T[sel]],
                        "P": [round(float(x), 1) for x in P[sel]], "proc": k, "mv": [int(x) for x in mv[sel]]})
    return out


def session_runs(d):
    """Every launch in a session's runs file, by start time."""
    R = []
    for p in (os.path.join(d, "runs.jsonl"), os.path.join(d, "runs.jsonl.gz")):
        if os.path.exists(p):
            R += [r for r in jsonl(p) if "t_start_ms" in r and "t_end_ms" in r]
    return sorted(R, key=lambda r: r["t_start_ms"])


def session_tel(d):
    p = os.path.join(d, "telemetry.jsonl.gz")
    return sorted(jsonl(p if os.path.exists(p) else os.path.join(d, "telemetry.jsonl")), key=lambda s: s["t_ms"])


DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "reports", "data")


def rel_data(d):
    """A session's name: its path under docs/reports/data."""
    return os.path.relpath(os.path.abspath(d), os.path.abspath(DATA))


def day_of(d):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.abspath(d))
    return m.group(1) if m else "?"


def governor_days(dirs):
    """The governor's timing in every aifoundry2 session whose clock moved: the cool-start runs of 21 September
    (--cold) and the cool passes of 23 September (--cool-passes: E29's discarded first attempt). A block is a run
    of launches with gaps of 2 s or less.
      sessions        per session: day, clock changes (up, down), direct 600 -> 800 up-steps
      up_T            per day: the whole-degree die readings on the samples either side of every up-step
      first_change_s  per block start, the time to the first clock change within [start, end + 0.5 s]
      change_gap_s    per day: the time between consecutive clock changes of a session less than 3 s apart
      reset           per block end (a launch followed by 2 s or more with no launch): the clock over the next
                      2.5 s, whether it was above 600 MHz, whether the loop stepped up after the end, and when it
                      settled at 600 MHz for good
      boundaries      per day and gap: consecutive launches 2 s apart or less, crossed with the clock above
                      600 MHz on the last sample of the first launch, and how many of them saw an 800 -> 600 MHz
                      drop from there to 0.2 s after the next launch started (the boot-point reset); "sessions" is
                      how many sessions those boundaries come from
      meter_lag_s     at every 600 -> 700/800 MHz up-step, the time from the first sample at the new clock to
                      the first sample whose board power is 3 W above the last sample before the step (within
                      six samples, while the clock holds)
    Descriptive counts of one card on two days; the session, not the launch, is the unit of replication."""
    import bisect
    ses, first, gaps, reset, lag = [], [], collections.defaultdict(list), [], []
    upT = collections.defaultdict(list)
    bnd = collections.defaultdict(lambda: [0, 0, set()])
    volt_ok, n_all = 0, 0
    for d in dirs:
        day, S, R = day_of(d), session_tel(d), session_runs(d)
        ts = [s["t_ms"] for s in S]
        f = [int(s["mhz"]["minion"]) for s in S]
        T = [int(s["temp_c"]["minshire"][0]) for s in S]
        P = [float(s["board_w"]) for s in S]
        mv = [int(s["die_mv"]["minion"]) for s in S]
        ch = [i for i in range(1, len(S)) if f[i] != f[i - 1]]
        n_all += len(ch)
        volt_ok += sum(1 for i in ch if (f[i] > f[i - 1]) == (mv[i] > mv[i - 1]) and mv[i] != mv[i - 1])
        ups = [i for i in ch if f[i] > f[i - 1]]
        for i in ups:
            upT[day].append([T[i - 1], T[i]])
        ses.append({"session": rel_data(d),
                    "day": day, "changes": len(ch), "up": len(ups), "down": len(ch) - len(ups),
                    "direct_600_800": sum(1 for i in ups if f[i - 1] == 600 and f[i] == 800),
                    "direct_800_600": sum(1 for i in ch if f[i - 1] == 800 and f[i] == 600)})
        blocks = []
        for r in R:
            if blocks and r["t_start_ms"] - blocks[-1][1] <= 2000:
                blocks[-1][1] = max(blocks[-1][1], r["t_end_ms"])
            else:
                blocks.append([r["t_start_ms"], r["t_end_ms"]])
        for a, b in blocks:
            c = [ts[i] for i in ch if a <= ts[i] <= b + 500]
            if c:
                first.append({"day": day, "s": round((c[0] - a) / 1000.0, 2)})
        gaps[day] += [round((ts[j] - ts[i]) / 1000.0, 2) for i, j in zip(ch, ch[1:]) if ts[j] - ts[i] < 3000]
        for a, b in zip(R, R[1:] + [None]):
            if b is not None and b["t_start_ms"] - a["t_end_ms"] < 2000:
                continue
            e = a["t_end_ms"]
            i, j = bisect.bisect_right(ts, e), bisect.bisect_right(ts, e + 2500)
            if i == 0 or i >= j:
                continue
            above = any(x != 600 for x in f[i:j])
            settle = None
            if above:
                k = max(k for k in range(i, j) if f[k] != 600)
                settle = round((ts[k + 1] - e) / 1000.0, 2) if k + 1 < len(ts) else None
            reset.append({"day": day, "above_600": above, "up_after_end": any(f[k] > f[k - 1] for k in range(i, j)),
                          "settle_s": settle})
        for a, b in zip(R, R[1:]):
            gap = (b["t_start_ms"] - a["t_end_ms"]) / 1000.0
            if gap < 0 or gap > 2:
                continue
            i = bisect.bisect_right(ts, a["t_end_ms"]) - 1
            if i < 0 or f[i] <= 600:
                continue
            j = bisect.bisect_right(ts, b["t_start_ms"] + 200)
            seq = f[i:j]
            cls = "<=10ms" if gap <= 0.01 else "10-100ms" if gap <= 0.1 else "100-300ms" if gap <= 0.3 else ">300ms"
            key = day + " " + cls
            bnd[key][0] += 1
            bnd[key][1] += any(x == 800 and y == 600 for x, y in zip(seq, seq[1:]))
            bnd[key][2].add(d)
        for i in range(1, len(S) - 6):
            if f[i] > f[i - 1] == 600:
                for j in range(i, min(i + 6, len(S))):
                    if f[j] < f[i]:
                        break
                    if P[j] > P[i - 1] + 3:
                        lag.append({"day": day, "s": round((ts[j] - ts[i]) / 1000.0, 2)})
                        break
    days = sorted({s["day"] for s in ses})
    spread = lambda v: {"n": len(v), "median": float(np.median(v)), "min": min(v), "max": max(v)} if v else {"n": 0}
    fs = [x["s"] for x in first]
    allgaps = [g for d_ in days for g in gaps[d_]]
    settles = [r["settle_s"] for r in reset if r["settle_s"] is not None]
    lags = [x["s"] for x in lag]
    return {
        "sessions": ses, "days": days, "changes": n_all, "voltage_tracks_strictly": volt_ok,
        "up_T": {d_: {"n": len(v), "max": max(max(p) for p in v), "min": min(min(p) for p in v),
                      "above_65_both": sum(1 for p in v if p[0] > T_THRESHOLD_C and p[1] > T_THRESHOLD_C)}
                 for d_, v in upT.items()},
        "first_change_s": spread(fs) | {"by_day": {d_: sorted(x["s"] for x in first if x["day"] == d_) for d_ in days}},
        "change_gap_s": {"n": len(allgaps), "median": float(np.median(allgaps)),
                         "p10": float(np.percentile(allgaps, 10)), "p90": float(np.percentile(allgaps, 90)),
                         "by_day": {d_: {"n": len(gaps[d_]), "median": float(np.median(gaps[d_]))} for d_ in days}},
        "reset": {"block_ends": len(reset), "above_600": sum(r["above_600"] for r in reset),
                  "up_after_end": sum(r["up_after_end"] for r in reset),
                  "settle_s": spread(settles)},
        "boundaries": {k: {"n": v[0], "drop_800_600": v[1], "sessions": len(v[2])} for k, v in sorted(bnd.items())},
        "meter_lag_s": spread(lags),
    }


def find_sessions(roots, exclude):
    """Every session directory under the roots (a telemetry file with a runs file beside it), less the excluded."""
    ex = {os.path.abspath(e) for e in exclude}
    out = set()
    for root in roots:
        for dp, _, fn in os.walk(root):
            if {"telemetry.jsonl.gz", "telemetry.jsonl"} & set(fn) and {"runs.jsonl", "runs.jsonl.gz"} & set(fn):
                if os.path.abspath(dp) not in ex:
                    out.add(os.path.normpath(dp))
    return sorted(out)


def idle_sessions(dirs, pw, idle_sample=None):
    """The aifoundry2 idle law against every session it was not fitted on, on both cards. Per session, with
    transfer_cards.py's published idle rule (10 Hz samples at 600 MHz outside [launch start - 1 s, launch end +
    6 s] of every launch, whole-degree bins of the minion-shire reading with 20 samples or more): the bins, and
    the session's offset from the law, measured minus law, over its idle samples (the bins weighted by samples).
    The 20.6-hour idle sample (--idle, no launches) is one more aifoundry2 session, every sample idle. The card
    comes from the directory name. The session is the unit: the summary is over sessions, per card."""
    L = lambda T: pw["P_fix"] + pw["A_leak_at_80"] * float(np.exp((T - 80) / pw["T_L"]))

    def one(name, card, samples, R):
        import bisect
        win = []                                   # the launch windows, merged
        for a, b in sorted((r["t_start_ms"] - 1000, r["t_end_ms"] + 6000) for r in R):
            if win and a <= win[-1][1]:
                win[-1][1] = max(win[-1][1], b)
            else:
                win.append([a, b])
        starts = [w[0] for w in win]
        bins = collections.defaultdict(list)
        for s in samples:
            if int(s["mhz"]["minion"]) != 600:
                continue
            k = bisect.bisect_right(starts, s["t_ms"]) - 1
            if k >= 0 and s["t_ms"] <= win[k][1]:
                continue
            bins[int(s["temp_c"]["minshire"][0])].append(float(s["board_w"]))
        rows = [{"T": k, "W": float(np.mean(v)), "law_W": L(k), "n": len(v)} for k, v in sorted(bins.items()) if len(v) >= 20]
        if not rows:
            return None
        n = sum(r["n"] for r in rows)
        return {"session": name, "card": card, "day": day_of(name),
                "T": [rows[0]["T"], rows[-1]["T"]], "n": n,
                "offset_W": sum((r["W"] - r["law_W"]) * r["n"] for r in rows) / n,
                "offset_W_bins": float(np.mean([r["W"] - r["law_W"] for r in rows])), "bins": rows}
    out = []
    for d in dirs:
        rel = rel_data(d)
        card = "aifoundry3" if "aifoundry3" in rel else "aifoundry2" if "aifoundry2" in rel else "?"
        r = one(rel, card, session_tel(d), session_runs(d))
        if r:
            out.append(r)
    if idle_sample:
        r = one(rel_data(idle_sample), "aifoundry2", jsonl(idle_sample), [])
        if r:
            out.append(r)
    summ = {}
    for card in sorted({r["card"] for r in out}):
        o = [r["offset_W"] for r in out if r["card"] == card]
        summ[card] = {"sessions": len(o), "mean_W": float(np.mean(o)), "sd_W": float(np.std(o, ddof=1)) if len(o) > 1 else None,
                      "min_W": min(o), "max_W": max(o), "max_abs_W": max(abs(x) for x in o),
                      "T": [min(r["T"][0] for r in out if r["card"] == card), max(r["T"][1] for r in out if r["card"] == card)],
                      "days": sorted({r["day"] for r in out if r["card"] == card})}
    return {"rule": "600 MHz samples outside [launch start - 1 s, launch end + 6 s], whole-degree bins with n >= 20; "
                    "offset_W = measured - law over the session's binned idle samples", "sessions": out, "summary": summ}


def leak_split(pw, tl_range, busy80):
    """How far the idle readings pin down the law's split into fixed and leakage power. flip_thermal_model.py picks
    the leakage temperature scale T_L from a grid by rms; here P_fix and A are refitted on the law's own idle bins
    (model.json power.idle_curve, least squares weighted by samples) at each end of tl_range, the range of scales
    that fit those readings about as well as the best (PLAN3 D3, docs/reports/data/2026-09-25-claims-v3). The
    law's total and its slope at 80 C barely move across the range; the split does."""
    bins = pw["idle_curve"]
    T = np.array([b["T"] for b in bins], float)
    Pw = np.array([b["P"] for b in bins], float)
    w = np.sqrt(np.array([b["n"] for b in bins], float))
    ends = []
    for T_L in list(tl_range) + [pw["T_L"]]:
        X = np.column_stack([np.ones(len(T)), np.exp((T - 80) / T_L)])
        c, *_ = np.linalg.lstsq(X * w[:, None], Pw * w, rcond=None)
        res = Pw - X @ c
        ends.append({"T_L": float(T_L), "P_fix": float(c[0]), "A_at_80": float(c[1]),
                     "rms_W": float(np.sqrt(np.sum(w ** 2 * res ** 2) / np.sum(w ** 2))),
                     "slope_80": float(c[1] / T_L), "idle_share_80": float(c[1] / (c[0] + c[1])),
                     "busy_share_80": float(c[1] / busy80)})
    return {"T_L": [float(x) for x in tl_range], "ends": ends[:2], "central_refit": ends[2],
            "rule": "P_fix and A refitted on model.json power.idle_curve (weighted by samples) at each T_L; "
                    "the page's central law is model.json's own fit"}


def wakeup(d):
    wj = json.load(open(os.path.join(d, "wakeup.json")))
    labels = wj["labels"]
    raw = open(os.path.join(d, "wakeup.u32"), "rb").read()
    # memprobe.c stores (uint32_t)(fixcyc(t1) - fixcyc(t0)), a signed difference cut to 32 bits: read it back as
    # int32, so a load that reads short is negative, not 4.29e9. The hpmcounter3 late-carry fix is already applied
    # on the card; do not correct again. Three loads still carry the kernel's own misfire, exactly 128 off: one
    # L1 repeat's no-idle load (+128), and one load each at L1 left in place and L2 (-128). They are kept as read.
    v = list(struct.unpack("<%di" % (len(raw) // 4), raw))
    by, per = collections.defaultdict(list), collections.defaultdict(dict)
    for l, x in zip(labels, v):
        if l and l[0] == "wake":
            by[(l[1], l[2])].append(x)
            per[(l[1], l[3])][l[2]] = x
    names = {-1: "L1 (line left in place)", 0: "L1", 1: "L2", 2: "L3", 3: "DRAM"}
    delays = sorted({k[1] for k in by})
    out = []
    for lev in sorted({k[0] for k in by}):
        med = [st.median(by[(lev, d_)]) for d_ in delays]
        paired = [per[k][delays[-1]] - per[k][delays[0]] for k in per
                  if k[0] == lev and delays[-1] in per[k] and delays[0] in per[k]]
        # Each repeat uses its own line (its own address, so its own distance), so compare each repeat with
        # itself: the median over repeats of (latency after idle d) - (latency with no idle), for every d.
        by_idle = [st.median([per[k][d_] - per[k][delays[0]] for k in per
                              if k[0] == lev and d_ in per[k] and delays[0] in per[k]]) for d_ in delays]
        out.append({"level": names.get(lev, str(lev)), "median_cycles": med, "paired_median_by_idle": by_idle,
                    "paired_delta_cycles": st.median(paired), "paired_n": len(paired),
                    "paired_iqr": round(float(np.percentile(paired, 75) - np.percentile(paired, 25)), 1),
                    # every repeat (its own line) against its own no-idle load, at each idle: [repeat][idle]
                    "paired_by_repeat": [[per[k][d_] - per[k][delays[0]] for d_ in delays]
                                         for k in sorted(per) if k[0] == lev and all(d_ in per[k] for d_ in delays)]})
    meta = wj.get("meta", {})
    # the idle the probe programs: every delay, once per repeat and per level, at 600 MHz (the loads add little)
    probe_s = (sum(meta["delays"]) * meta["reps"] * len(out) / CLOCK_HZ) if "delays" in meta and "reps" in meta else None
    return {"idle_cycles": delays, "idle_ms": [round(d_ / 600e3, 3) for d_ in delays], "levels": out,
            "reps": meta.get("reps"), "probe_idle_s": round(probe_s, 2) if probe_s is not None else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cold", nargs="+", required=True)
    ap.add_argument("--wakeup", required=True)
    ap.add_argument("--idle", required=True)
    ap.add_argument("--since", required=True,
                    help="runs.jsonl[.gz] of the last workload before the idle sample; its last launch end starts the idle")
    ap.add_argument("--model", required=True)
    ap.add_argument("--ablation", required=True)
    ap.add_argument("--sptrace", help="aifoundry3's service-processor trace buffer (sptrace-aifoundry3.bin), "
                                      "to count the governor's log events")
    ap.add_argument("--cool-passes", nargs="*", default=[],
                    help="more aifoundry2 sessions whose clock moved (the 23 September cool passes), for the governor's "
                         "timing on a second day (governor_days); the --cold sessions are always included")
    ap.add_argument("--idle-sessions", nargs="*", default=[],
                    help="directories to search for sessions (telemetry and runs files) to test the idle law on, on "
                         "either card (idle_sessions); the sessions the law was fitted on (--cold and model.json's "
                         "sessions) are left out, and the --idle sample is added as one more aifoundry2 session")
    ap.add_argument("--tl-range", nargs=2, type=float, default=[30.0, 45.0],
                    help="leakage temperature scales that fit the law's idle readings about as well as the best "
                         "(leak_split; default 30 45, PLAN3 D3)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows, osc = transitions(a.cold)
    VOLTS, volts_n = volts(a.cold)
    idle = jsonl(a.idle)
    P = np.array([r["board_w"] for r in idle])
    T = np.array([float(r["temp_c"]["minshire"][0]) for r in idle])
    rails = {k: float(np.mean([r["sp"][k + "_w"][0] for r in idle])) for k in ("minion", "sram", "noc")}
    pw = json.load(open(a.model))["power"]
    leak = pw["A_leak_at_80"] * float(np.exp((T.mean() - 80) / pw["T_L"]))
    pred = pw["P_fix"] + leak
    ab = json.load(open(a.ablation))["configs"]
    # How long the card had been idle: from the end of the last launch before the sample to the first sample.
    last_end_ms = max(r["t_end_ms"] for r in jsonl(a.since) if "t_end_ms" in r)
    idle_start_ms = min(r["t_ms"] for r in idle)
    hours_idle = round((idle_start_ms - last_end_ms) / 3.6e6, 1)

    out = {
        # dm_task_delay_ms is only the sleep at the end of each device-management pass; the pass itself,
        # and so the governor, runs about every 133 ms.
        "thresholds": {"tdp_w": TDP_W, "temp_c": T_THRESHOLD_C, "dm_task_delay_ms": 10,
                       "hw_catastrophic_c": 75, "hw_catastrophic_w": 75},
        "operating_points": [{"mhz": f, "volts": v, "samples": volts_n[f],
                              "source": "median die_mv.minion while a kernel runs (cold1+cold2)"} for f, v in sorted(VOLTS.items())],
        "transitions": rows,
        "transition_summary": {
            "total": len(rows), "up": sum(1 for r in rows if r["dir"] == "up"),
            "down": sum(1 for r in rows if r["dir"] == "down"),
            "by_cause": dict(collections.Counter(r["why"] for r in rows if r["dir"] == "down")),
            "by_cause_prev": dict(collections.Counter(r["why_prev"] for r in rows if r["dir"] == "down")),
            "first_change_s": [o["first_change_s"] for o in osc],
            "voltage_tracks_frequency": all((r["f1"] > r["f0"]) == (r["mv1"] >= r["mv0"]) for r in rows),
        },
        "oscillation": osc,
        "traces": traces(a.cold, {(o["session"], o["values"], o["proc"]) for o in osc}),
        "leak_model": {"P_fix": pw["P_fix"], "A_at_80": pw["A_leak_at_80"], "T_L": pw["T_L"],
                       "idle_curve": pw.get("idle_curve")},
        # the overnight rest before the cool starts (21 September), with the idle law's watts at its temperature
        "overnight_idle": (lambda r: r | {"law_w": pw["P_fix"] + pw["A_leak_at_80"] * float(np.exp((r["die_c"] - 80) / pw["T_L"]))})(rest_before(a.cold[0])),
        "busy_randn_80c": ab["fp32_randn"]["p80"], "idle_80c": ab["fp32_zeros"]["idle"],
        "wakeup": wakeup(a.wakeup),
        "idle_check": {
            "hours_idle": hours_idle, "last_workload_end_ms": last_end_ms, "sample_start_ms": idle_start_ms,
            "samples": len(idle), "board_w": float(P.mean()), "board_sd": float(P.std()),
            "die_c": float(T.mean()), "rails": rails, "board_minus_rails": float(P.mean() - sum(rails.values())),
            "model_pred_w": pred, "error_w": float(P.mean() - pred),
            "temp_dependent_w": leak, "temp_dependent_frac": leak / float(P.mean()),
        },
        "leak_fraction": {
            "idle_80c": (pw["A_leak_at_80"]) / ab["fp32_zeros"]["idle"],
            "idle_80c_law": pw["A_leak_at_80"] / (pw["P_fix"] + pw["A_leak_at_80"]),
            "busy_randn_80c": pw["A_leak_at_80"] / ab["fp32_randn"]["p80"],
            "kanter_range": [0.05, 0.30],
        },
        "activity_term": {
            "mw_per_minion": {k: ab[k]["mw_per_minion"] for k in ("fp32_randn_8", "fp32_randn_16", "fp32_randn_24", "fp32_randn")},
            "minions": {k: ab[k]["minions"] for k in ("fp32_randn_8", "fp32_randn_16", "fp32_randn_24", "fp32_randn")},
        },
    }
    if a.cool_passes:
        out["governor_days"] = governor_days(list(a.cold) + list(a.cool_passes))
    if a.idle_sessions:
        fitted = list(a.cold) + [os.path.join(DATA, "..", "..", "..", m["dir"]) for m in json.load(open(a.model)).get("sessions", [])]
        out["idle_sessions"] = idle_sessions(find_sessions(a.idle_sessions, fitted), pw, a.idle)
    out["leak_split"] = leak_split(pw, a.tl_range, ab["fp32_randn"]["p80"])
    if a.sptrace:
        # The governor's own log lines, in buffer order. Their format ("Power idle state event, current pwr N
        # tdp level N") exists only in et-platform before commit 60b40c10f, so it also dates the firmware.
        buf = open(a.sptrace, "rb").read().decode("latin-1")
        ev = [("idle" if m.group(1) else "down" if m.group(2) else "up")
              for m in re.finditer(r"Power (idle state event, current pwr)|Power (throttle down event)|"
                                   r"Power throttle up event", buf)]
        out["sptrace_events"] = {
            "idle": ev.count("idle"), "down": ev.count("down"), "up": ev.count("up"),
            "consecutive_idle_pairs": sum(1 for x, y in zip(ev, ev[1:]) if x == y == "idle"),
            "consecutive_down_pairs": sum(1 for x, y in zip(ev, ev[1:]) if x == y == "down"),
        }
    if os.path.exists(a.out):
        try:
            prev = json.load(open(a.out))
        except Exception:
            prev = {}
        if prev.get("cards") is not None:
            out["cards"] = prev["cards"]   # the three-machine block that build_cards_data.py --merge added
    json.dump(out, open(a.out, "w"), indent=1)
    s = out["transition_summary"]
    print(f"{s['total']} clock transitions ({s['up']} up, {s['down']} down); causes of down-steps: {s['by_cause']}; "
          f"on the sample before the step: {s['by_cause_prev']}")
    print("operating points: " + ", ".join(f"{o['mhz']} MHz {o['volts']:.3f} V (n={o['samples']})" for o in out["operating_points"]))
    print(f"wake-up probe: {out['wakeup']['probe_idle_s']} s of programmed idle ({out['wakeup']['reps']} repeats)")
    print(f"first change after launch: {sorted(s['first_change_s'])}")
    print(f"wake-up paired deltas: " + ", ".join(f"{l['level']} {l['paired_delta_cycles']:+g}" for l in out["wakeup"]["levels"]))
    ic = out["idle_check"]
    if "sptrace_events" in out:
        print(f"aifoundry3 governor log: {out['sptrace_events']}")
    if "governor_days" in out:
        g = out["governor_days"]
        print(f"governor on {len(g['sessions'])} sessions ({', '.join(g['days'])}): {g['changes']} clock changes; first change "
              f"median {g['first_change_s']['median']:.2f} s ({g['first_change_s']['min']}-{g['first_change_s']['max']}, n={g['first_change_s']['n']}); "
              f"change gaps median {g['change_gap_s']['median']:.2f} s (p10-p90 {g['change_gap_s']['p10']:.2f}-{g['change_gap_s']['p90']:.2f}); "
              f"reset {g['reset']['settle_s']['median']:.2f} s ({g['reset']['settle_s']['min']}-{g['reset']['settle_s']['max']}) over "
              f"{g['reset']['above_600']} of {g['reset']['block_ends']} block ends, up after end {g['reset']['up_after_end']}; "
              f"meter lag median {g['meter_lag_s']['median']:.2f} s ({g['meter_lag_s']['min']}-{g['meter_lag_s']['max']}, n={g['meter_lag_s']['n']}); "
              f"boundaries {g['boundaries']}; up-step readings {g['up_T']}")
    if "idle_sessions" in out:
        for c, v in out["idle_sessions"]["summary"].items():
            print(f"idle law on {c}: {v['sessions']} sessions {v['days']}, offset mean {v['mean_W']:+.2f} W (sd {v['sd_W']:.2f}), "
                  f"{v['min_W']:+.2f} to {v['max_W']:+.2f} W, die {v['T'][0]}-{v['T'][1]} C")
    ls = out["leak_split"]
    print("leakage split: " + "; ".join(f"T_L {e['T_L']:.0f} C: fixed {e['P_fix']:.1f} W, leakage {e['A_at_80']:.1f} W at 80 C "
                                         f"(idle {e['idle_share_80']:.0%}, busy {e['busy_share_80']:.0%}, slope {e['slope_80']:.3f} W/C, rms {e['rms_W']:.3f} W)"
                                         for e in ls["ends"] + [ls["central_refit"]]))
    print(f"idle after {ic['hours_idle']} h: {ic['board_w']:.2f} W at {ic['die_c']:.1f} C, model {ic['model_pred_w']:.2f} W, error {ic['error_w']:+.2f} W")


if __name__ == "__main__":
    main()
