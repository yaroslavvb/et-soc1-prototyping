#!/usr/bin/env python3
"""Cool-start runs (run_horace_cold.sh): clock, FLOPS, power and temperature per run.

    analyze_horace_cold.py <run-dir> --out cold.json
"""
import argparse
import gzip
import os
import json

import numpy as np

MINIONS, MAC_PER_OP, FLOP_PER_MAC = 1024, 4096, 2


def load_jsonl(path):
    out = []
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    for line in (gzip.open(path, "rt") if path.endswith(".gz") else open(path)):
        try:
            out.append(json.loads(line))
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
    procs = []
    for r in load_jsonl(f"{a.run_dir}/runs.jsonl"):
        if r["launch"] == -1:
            procs.append([])
        procs[-1].append(r)
    runs = []
    for proc in procs:
        t0, t1 = proc[0]["t_start_ms"] / 1000.0, proc[-1]["t_end_ms"] / 1000.0
        ops = sum(r["iters"] for r in proc)
        sel = [s for s, ts in zip(tel, t) if t0 - 1.0 <= ts <= t1 + 1.5]
        launches = [{"t": round((r["t_start_ms"] + r["t_end_ms"]) / 2000.0 - t0, 3), "ghz": r["ghz"]} for r in proc[1:]]
        inrun = [s for s, ts in zip(tel, t) if t0 + 0.3 <= ts <= t1]
        runs.append({
            "run": proc[0]["run"], "values": proc[0]["values"], "dur": t1 - t0, "ops": ops,
            "tflops": ops * MAC_PER_OP * FLOP_PER_MAC * MINIONS / (t1 - t0) / 1e12,
            "start_temp": sel[0]["temp_c"]["minshire"][0], "end_temp": max(s["temp_c"]["minshire"][0] for s in inrun),
            "p_mean": float(np.mean([s["board_w"] for s in inrun])), "p_max": max(s["board_w"] for s in inrun),
            "s_at_800": round(sum(0.1 for s in inrun if s["mhz"]["minion"] == 800), 1),
            "launches": launches,
            "trace": [{"t": round(s["t_ms"] / 1000.0 - t0, 2), "T": s["temp_c"]["minshire"][0], "P": s["board_w"],
                       "mhz": s["mhz"]["minion"], "mv": s["die_mv"]["minion"]} for s in sel],
        })
    json.dump({"runs": runs}, open(a.out, "w"))
    for r in runs:
        print(f"run {r['run']} {r['values']:8s} start {r['start_temp']} C end {r['end_temp']} C  {r['tflops']:5.2f} TFLOPS  "
              f"{r['s_at_800']:.1f} s at 800 MHz  mean {r['p_mean']:.1f} W max {r['p_max']:.1f} W  "
              f"clock by launch: {' '.join(f'{l['ghz']*1000:.0f}' for l in r['launches'])}")


if __name__ == "__main__":
    main()
