#!/usr/bin/env python3
"""Per-configuration results of run_ablation.sh: power at the launch temperature, work rate, energy per unit of work.

    analyze_ablation.py <run-dir> --out ablation.json [--leak 0.68] [--launch-temp 80.9]
"""
import argparse
import collections
import gzip
import json
import os

import numpy as np

MAC_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    out = []
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
    ap.add_argument("--leak", type=float, default=0.68, help="W per C of idle power around 80 C")
    ap.add_argument("--launch-temp", type=float, default=80.9)
    a = ap.parse_args()
    tel = load_jsonl(f"{a.run_dir}/telemetry.jsonl")
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    P = np.array([s["board_w"] for s in tel])
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])
    mhz = np.array([s["mhz"]["minion"] for s in tel])
    mv = np.array([s["die_mv"]["minion"] for s in tel])
    rail = {k: np.array([s["sp"][k + "_w"][0] for s in tel]) for k in ("minion", "sram", "noc")}
    procs = collections.OrderedDict()
    for r in load_jsonl(f"{a.run_dir}/runs.jsonl"):
        if r.get("block", -9) >= 0:
            procs.setdefault((r["block"], r["config"]), []).append(r)
    runs = []
    for (block, cfg), ls in procs.items():
        t0, t1 = ls[0]["t_start_ms"] / 1000.0, ls[-1]["t_end_ms"] / 1000.0
        dur = t1 - t0
        sel = lambda lo, hi: (t >= t0 + lo) & (t <= t0 + hi)
        early = sel(1.0, 3.0)
        p_early, t_early = float(P[early].mean()), float(T[early].mean())
        body = ls[1:] if len(ls) > 1 else ls
        r0 = ls[0]
        work = {}
        if r0["test"] == "fma":
            ops = sum(r["iters"] for r in ls) * r0["minions"]
            work = {"unit": "MAC", "per_s": ops * MAC_PER_OP[r0["type"]] / dur, "cycles_per_op": float(np.mean([r["cycles_per_op"] for r in body])),
                    "type": r0["type"], "values": r0.get("values")}
        elif r0["test"] == "tload":
            work = {"unit": "byte", "per_s": sum(r["bytes_requested"] for r in ls) / dur, "where": r0["where"]}
        elif r0["test"] == "spin":
            work = {"unit": "instruction", "per_s": sum(r["iters"] for r in ls) * 5 * r0["minions"] / dur}
        runs.append({"block": block, "config": cfg, "minions": r0["minions"], "dur": dur, "p_before": float(P[sel(-2.0, -0.3)].mean()),
                     "p_early": p_early, "t_early": t_early, "p80": p_early - a.leak * (t_early - a.launch_temp),
                     "p_late": float(P[sel(dur - 2.0, dur)].mean()), "mhz": [int(mhz[sel(0.3, dur)].min()), int(mhz[sel(0.3, dur)].max())],
                     "mv": float(mv[sel(0.3, dur)].mean()), "rails_late": {k: float(v[sel(dur - 1.0, dur)].mean()) for k, v in rail.items()},
                     "t_end": float(T[sel(dur - 0.5, dur)].mean()), "work": work})
    cfgs = collections.OrderedDict()
    for cfg in sorted({r["config"] for r in runs}, key=lambda c: np.mean([r["p80"] for r in runs if r["config"] == c])):
        rs = [r for r in runs if r["config"] == cfg]
        p80 = float(np.mean([r["p80"] for r in rs])); idle = float(np.mean([r["p_before"] for r in rs]))
        w = rs[0]["work"]; per_s = float(np.mean([r["work"]["per_s"] for r in rs])) if w else 0.0
        cfgs[cfg] = {"n": len(rs), "minions": rs[0]["minions"], "p80": p80, "p80_sd": float(np.std([r["p80"] for r in rs])), "idle": idle, "dyn": p80 - idle,
                     "unit": w.get("unit"), "per_s": per_s, "pj_per_unit_dyn": (p80 - idle) / per_s * 1e12 if per_s else None,
                     "pj_per_unit_board": p80 / per_s * 1e12 if per_s else None, "cycles_per_op": w.get("cycles_per_op"),
                     "mw_per_minion": 1000.0 * (p80 - idle) / rs[0]["minions"], "rise": float(np.mean([r["t_end"] for r in rs])) - a.launch_temp,
                     "rails_late": {k: float(np.mean([r["rails_late"][k] for r in rs])) for k in ("minion", "sram", "noc")},
                     "mhz": [min(r["mhz"][0] for r in rs), max(r["mhz"][1] for r in rs)], "mv": float(np.mean([r["mv"] for r in rs]))}
    json.dump({"runs": runs, "configs": cfgs}, open(a.out, "w"))
    print(f"{'config':14s} n minions   W@80   sd   over idle  mW/minion   work/s        pJ per unit (over idle / board)   cycles/op")
    for c, v in cfgs.items():
        pj = f"{v['pj_per_unit_dyn']:8.3f} / {v['pj_per_unit_board']:8.3f} per {v['unit']}" if v["per_s"] else ""
        print(f"{c:14s} {v['n']} {v['minions']:5d}  {v['p80']:6.2f} {v['p80_sd']:5.2f}  {v['dyn']:7.2f}   {v['mw_per_minion']:7.2f}   {v['per_s']:.3e}   {pj}   {v['cycles_per_op'] or ''}")


if __name__ == "__main__":
    main()
