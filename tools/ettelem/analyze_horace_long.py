#!/usr/bin/env python3
"""Per-run summary of run_horace_long.sh: curves at 1 Hz, power and temperature at fixed times, FLOPs, end reason.

    analyze_horace_long.py <run-dir> --out long.json
"""
import argparse
import gzip
import json
import os

import numpy as np

MAC_PER_OP, FLOP_PER_MAC = 4096, 2
AT = [5, 10, 30, 60, 120, 300, 600]


def norm_values(v):
    """'file:/path/kind.seed.bin' (custom tiles) -> 'kind'."""
    return os.path.basename(v[5:]).split(".")[0] if isinstance(v, str) and v.startswith("file:") else v


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    out = []
    for line in (gzip.open(path, "rt") if path.endswith(".gz") else open(path)):
        try:
            rec = json.loads(line)
            if "values" in rec:
                rec["values"] = norm_values(rec["values"])
            out.append(rec)
        except Exception:
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tel = load_jsonl(f"{a.run_dir}/telemetry.jsonl")
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    P = np.array([s["board_w"] for s in tel])
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    rail = np.array([s["sp"]["minion_w"][0] for s in tel])
    starts = {s["run"]: s for s in load_jsonl(f"{a.run_dir}/starts.jsonl")}
    ends = {s["run"]: s for s in load_jsonl(f"{a.run_dir}/ends.jsonl")}
    launches = {}
    for r in load_jsonl(f"{a.run_dir}/runs.jsonl"):
        if r.get("block", -9) >= 0:
            launches.setdefault(r["block"], []).append(r)
    runs = []
    for k, ls in sorted(launches.items()):
        if k not in ends:
            continue  # still running
        t0, t1 = ls[0]["t_start_ms"] / 1000.0, ls[-1]["t_end_ms"] / 1000.0
        dur = t1 - t0
        ops = sum(r["iters"] for r in ls)
        win = lambda lo, hi, x: float(x[(t >= t0 + lo) & (t <= t0 + hi)].mean()) if ((t >= t0 + lo) & (t <= t0 + hi)).any() else None
        sec = np.arange(-10, int(dur) + 121)
        cT = [win(s - 0.5, s + 0.5, T) for s in sec]
        cP = [win(s - 0.5, s + 0.5, P) for s in sec]
        run_sel = (t >= t0 + 0.3) & (t <= t1)
        runs.append({
            "run": k, "values": ls[0]["values"], "minions": ls[0]["minions"], "per_shire": starts[k]["per_shire"], "seed": starts[k]["seed"],
            "t0_ms": ls[0]["t_start_ms"], "dur": dur, "reason": ends[k]["reason"], "approach_s": starts[k]["approach_ms"] / 1000.0,
            "reached_target": starts[k]["reached_target"], "start_reading": float(T[np.searchsorted(t, t0) - 1]),
            "tflops": ops * MAC_PER_OP * FLOP_PER_MAC * ls[0]["minions"] / dur / 1e12, "flops": ops * MAC_PER_OP * FLOP_PER_MAC * ls[0]["minions"],
            "p_before": win(-3.0, -0.5, P), "t_before": win(-3.0, -0.5, T), "p_mean": float(P[run_sel].mean()), "energy_j": float(P[run_sel].mean() * dur),
            "mhz": [int(mhz[run_sel].min()), int(mhz[run_sel].max())],
            "P_at": {str(s): win(s - 2, s + 2, P) for s in AT if s <= dur}, "T_at": {str(s): win(s - 2, s + 2, T) for s in AT if s <= dur},
            "rail_at": {str(s): win(s - 2, s + 2, rail) for s in AT if s <= dur},
            "t_max": float(T[run_sel].max()), "sec": [int(s) for s in sec], "curve_T": cT, "curve_P": cP,
        })
    json.dump({"runs": runs, "session_minutes": float((t[-1] - t[0]) / 60)}, open(a.out, "w"))
    print(f"{len(runs)} finished runs, session {float((t[-1] - t[0]) / 60):.0f} min so far")
    for r in runs:
        ta = " ".join(f"{s}s:{r['T_at'][str(s)]:.1f}" for s in AT if str(s) in r["T_at"])
        pa = " ".join(f"{s}s:{r['P_at'][str(s)]:.1f}" for s in AT if str(s) in r["P_at"])
        print(f"run {r['run']:2d} {r['values']:14s} {r['minions']:4d} minions  {r['dur']:6.1f} s ({r['reason']:5s}) start {r['t_before']:.1f} C {r['p_before']:.1f} W  {r['tflops']:.2f} TFLOPS\n"
              f"       T {ta}\n       P {pa}")


if __name__ == "__main__":
    main()
