#!/usr/bin/env python3
"""Data for the DVFS / leakage report: governor transitions, the wake-up probe, and the long-idle check.

    analyze_dvfs.py --cold <cold1-dir> <cold2-dir> --wakeup <dir> --idle <idle.jsonl[.gz]> \
                    --since <runs.jsonl[.gz] of the last workload before the idle sample> \
                    --model model.json --ablation ablation.json [--sptrace sptrace-aifoundry3.bin] --out dvfs.json

The page's data, from the repo root:

    D=docs/reports/data
    python3 tools/ettelem/analyze_dvfs.py --cold $D/2026-09-21-horace-aifoundry2/cold1 $D/2026-09-21-horace-aifoundry2/cold2 \
        --wakeup $D/2026-09-22-dvfs-aifoundry2/wakeup --idle $D/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz \
        --since $D/2026-09-21-horace-aifoundry2/long2/runs.jsonl.gz --model $D/2026-09-21-horace-aifoundry2/model.json \
        --ablation $D/2026-09-21-horace-aifoundry2/ablation.json --sptrace $D/2026-09-22-cards/sptrace-aifoundry3.bin \
        --out $D/2026-09-22-dvfs-aifoundry2/dvfs.json

then build_cards_data.py ... --merge $D/2026-09-22-dvfs-aifoundry2/dvfs.json (tools/ettelem/finish_horace.sh runs it).

Fits nothing. Every number is either read from telemetry or computed from it. The three-machine block
("cards") is merged in afterwards by build_cards_data.py --merge dvfs.json; when --out already holds one, it is
carried over, so rerunning this script alone does not drop it.

A down-step is attributed to the thermal test if the die reading was above 65 °C, to the power test if board
power was above 65 W, to both if both; any other down-step is "unattributed": neither test fired on the values
we sampled at 10 Hz. "why" reads the first sample that shows the new clock, "why_prev" the last sample before
it; the board meter lags the clock by 0.1-0.3 s, so the two can differ. (Launches run back to back every
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
    print(f"idle after {ic['hours_idle']} h: {ic['board_w']:.2f} W at {ic['die_c']:.1f} C, model {ic['model_pred_w']:.2f} W, error {ic['error_w']:+.2f} W")


if __name__ == "__main__":
    main()
