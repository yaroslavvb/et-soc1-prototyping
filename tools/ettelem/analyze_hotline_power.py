#!/usr/bin/env python3
"""Board power and rails while one global atomic line is contended, against the same work spread over 32.

    analyze_hotline_power.py <run-dir> --out power.json

Idle is every 10 Hz sample at least a second away from any launch. A run's power is the mean over the samples
inside its three back-to-back launches, less the first 0.4 s of the first one; the per-rail numbers are the
service processor's ~2 s moving averages, which is why the launches are repeated.
"""
import argparse
import gzip
import json
import os

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tp = os.path.join(a.dir, "telemetry.jsonl")
    op = gzip.open if os.path.exists(tp + ".gz") else open
    tel = [json.loads(l) for l in op(tp + ".gz" if os.path.exists(tp + ".gz") else tp, "rt") if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(a.dir, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    f = {k: np.array([(s[p][k][0] if p else s[k]) for s in tel])   # rails are [avg, min, max]
         for k, p in (("board_w", None), ("minion_w", "sp"), ("sram_w", "sp"), ("noc_w", "sp"))}
    die = np.array([s["temp_c"]["minshire"][0] for s in tel])
    busy = np.zeros(len(t), bool)
    for r in runs:
        busy |= (t >= r["t_start_ms"] / 1000.0 - 1.0) & (t <= r["t_end_ms"] / 1000.0 + 1.0)
    idle = ~busy
    out = {"idle": {k: float(v[idle].mean()) for k, v in f.items()} | {"die_c": float(die[idle].mean()),
                                                                       "n": int(idle.sum())}, "runs": []}
    labels = []
    for r in runs:
        if r["label"] not in labels:
            labels.append(r["label"])
    print(f"idle: board {out['idle']['board_w']:.2f} W at {out['idle']['die_c']:.1f} C  "
          f"minion {out['idle']['minion_w']:.2f} sram {out['idle']['sram_w']:.2f} noc {out['idle']['noc_w']:.2f}")
    print(f"\n{'run':14s}{'home':12s}{'ops/s':>13s}{'cyc/op':>8s}{'board W':>9s}{'+idle':>7s}"
          f"{'minion':>8s}{'sram':>7s}{'noc':>6s}{'nJ/op':>8s}")
    for lab in labels:
        rs = [r for r in runs if r["label"] == lab]
        m = np.zeros(len(t), bool)
        for i, r in enumerate(rs):
            m |= (t >= r["t_start_ms"] / 1000.0 + (0.4 if not i else 0)) & (t <= r["t_end_ms"] / 1000.0 - 0.1)
        if m.sum() < 3:
            continue
        rate = sum(r["total_ops"] for r in rs) / sum(r["wall_s"] for r in rs)
        over = float(f["board_w"][m].mean() - out["idle"]["board_w"])
        row = {"label": lab, "home": rs[0]["home"], "ops_per_s": rate, "cycles_per_op": rs[0]["cycles_per_op"],
               "over_idle_w": over, "nj_per_op": over / rate * 1e9 if rate else 0,
               "die_c": float(die[m].mean()), "n": int(m.sum()),
               **{k: float(v[m].mean()) for k, v in f.items()}}
        out["runs"].append(row)
        print(f"{lab:14s}{rs[0]['home']:12s}{rate:13.3e}{row['cycles_per_op']:8.2f}{row['board_w']:9.2f}"
              f"{over:7.2f}{row['minion_w']:8.2f}{row['sram_w']:7.2f}{row['noc_w']:6.2f}{row['nj_per_op']:8.1f}")
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
