#!/usr/bin/env python3
"""Data for the DVFS / leakage report: governor transitions, the wake-up probe, and the long-idle check.

    analyze_dvfs.py --cold <cold1-dir> <cold2-dir> --wakeup <dir> --idle <idle.jsonl[.gz]> \
                    --since <runs.jsonl[.gz] of the last workload before the idle sample> \
                    --model model.json --ablation ablation.json --out dvfs.json

Fits nothing. Every number is either read from telemetry or computed from it. The three-machine block
("cards") is merged in afterwards by build_cards_data.py --merge dvfs.json.

A down-step is attributed to the thermal test if the die reading was above 65 °C, to the power test if board
power was above 65 W, to both if both; any other down-step is "unattributed": neither test fired on the values
we sampled at 10 Hz. (Launches run back to back every 0.37–0.49 s, so every instant is within 0.25 s of a
kernel boundary; distance to a boundary is kept in the data but explains nothing.)
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
VOLTS = {600: 0.517, 700: 0.568, 800: 0.618}   # measured on-die, die_mv.minion
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
        for proc in procs:
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
                why = ("thermal+power" if (TT[i] > T_THRESHOLD_C and PP[i] > TDP_W) else
                       "thermal" if TT[i] > T_THRESHOLD_C else
                       "power" if PP[i] > TDP_W else
                       UNATTRIBUTED)
                rows.append({"session": os.path.basename(d), "values": proc[0]["values"], "t": round(tt[i] - t0, 2),
                             "dir": "up" if up else "down", "f0": int(ff[i - 1]), "f1": int(ff[i]),
                             "mv0": int(vv[i - 1]), "mv1": int(vv[i]), "T": int(TT[i]), "P": round(float(PP[i]), 1),
                             "gap_to_boundary_ms": round(near * 1000), "why": None if up else why})
                changes.append(tt[i] - t0)
            # step-up latency and oscillation period within the run
            ups = [r for r in rows if r["session"] == os.path.basename(d) and r["dir"] == "up"]
            if changes:
                osc.append({"session": os.path.basename(d), "values": proc[0]["values"],
                            "first_change_s": round(changes[0], 2), "n_changes": len(changes),
                            "span_s": round(changes[-1] - changes[0], 2)})
    return rows, osc


def traces(cold_dirs, want):
    """10 Hz clock, temperature and power for a few named runs, for the limit-cycle figure."""
    out = []
    for d in cold_dirs:
        tel = jsonl(os.path.join(d, "telemetry.jsonl.gz"))
        t = np.array([s["t_ms"] for s in tel]) / 1000.0
        P = np.array([s["board_w"] for s in tel])
        T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
        f = np.array([s["mhz"]["minion"] for s in tel])
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
                        "P": [round(float(x), 1) for x in P[sel]]})
    return out


def wakeup(d):
    labels = json.load(open(os.path.join(d, "wakeup.json")))["labels"]
    raw = open(os.path.join(d, "wakeup.u32"), "rb").read()
    v = list(struct.unpack("<%dI" % (len(raw) // 4), raw))
    fix = lambda x: x + 128 if (x & 0x7F) < 11 else x     # hpmcounter3 late carry
    by, per = collections.defaultdict(list), collections.defaultdict(dict)
    for l, x in zip(labels, v):
        if l and l[0] == "wake":
            by[(l[1], l[2])].append(fix(x))
            per[(l[1], l[3])][l[2]] = fix(x)
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
                    "paired_iqr": round(float(np.percentile(paired, 75) - np.percentile(paired, 25)), 1)})
    return {"idle_cycles": delays, "idle_ms": [round(d_ / 600e3, 3) for d_ in delays], "levels": out}


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
        "operating_points": [{"mhz": f, "volts": v} for f, v in sorted(VOLTS.items())],
        "transitions": rows,
        "transition_summary": {
            "total": len(rows), "up": sum(1 for r in rows if r["dir"] == "up"),
            "down": sum(1 for r in rows if r["dir"] == "down"),
            "by_cause": dict(collections.Counter(r["why"] for r in rows if r["dir"] == "down")),
            "first_change_s": [o["first_change_s"] for o in osc],
            "voltage_tracks_frequency": all((r["f1"] > r["f0"]) == (r["mv1"] >= r["mv0"]) for r in rows),
        },
        "oscillation": osc,
        "traces": traces(a.cold, {("cold1", "ones", 2), ("cold1", "zeros", 0), ("cold1", "randn", 1)}),
        "leak_model": {"P_fix": pw["P_fix"], "A_at_80": pw["A_leak_at_80"], "T_L": pw["T_L"]},
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
    json.dump(out, open(a.out, "w"), indent=1)
    s = out["transition_summary"]
    print(f"{s['total']} clock transitions ({s['up']} up, {s['down']} down); causes of down-steps: {s['by_cause']}")
    print(f"first change after launch: {sorted(s['first_change_s'])}")
    print(f"wake-up paired deltas: " + ", ".join(f"{l['level']} {l['paired_delta_cycles']:+g}" for l in out["wakeup"]["levels"]))
    ic = out["idle_check"]
    if "sptrace_events" in out:
        print(f"aifoundry3 governor log: {out['sptrace_events']}")
    print(f"idle after {ic['hours_idle']} h: {ic['board_w']:.2f} W at {ic['die_c']:.1f} C, model {ic['model_pred_w']:.2f} W, error {ic['error_w']:+.2f} W")


if __name__ == "__main__":
    main()
