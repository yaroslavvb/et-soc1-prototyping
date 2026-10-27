#!/usr/bin/env python3
"""The leakage slope this card actually shows, measured on E66 pass 11's cooling (Q128(b) correction pass).

The registered idle rule (reduce.py rule F / flip_thermal_model.py step 2a): no launch within 4.5 s, the first
20 s of the pass dropped, mhz.minion == 600. A straight line of board power against die temperature over a
band is what E68's correction term `p80 = p_raw - k*(t_win - t_launch)` needs.
"""
import gzip
import json
import os

import numpy as np

D = os.path.expanduser("~/claude/et-soc1-prototyping/build/claims-v3/aifoundry2/idle")


def load(p):
    cool = None
    mk = os.path.join(p, "marks.jsonl")
    if not os.path.exists(mk):
        return None
    for l in open(mk):
        m = json.loads(l)
        if m["ev"] == "cool_start":
            cool = m["t_ms"]
    if cool is None:
        return None
    # a finished pass is gzipped; a killed one left .jsonl; a running one is still writing .jsonl.raw
    op = None
    for name in ("telemetry.jsonl.gz", "telemetry.jsonl", "telemetry.jsonl.raw"):
        f = os.path.join(p, name)
        if os.path.exists(f):
            op = (lambda f=f: gzip.open(f, "rt")) if f.endswith(".gz") else (lambda f=f: open(f))
            break
    if op is None:
        return None
    rows = []
    with op() as fh:
        for l in fh:
            l = l.strip()
            if not l.startswith("{") or not l.endswith("}"):
                continue
            try:
                d = json.loads(l)
            except Exception:
                continue
            t = d.get("t_ms")
            # rule F: 4.5 s after the last burst (cool_start is the last burst's end) and 20 s of settling
            if t is None or t < cool + 20000:
                continue
            if d.get("mhz", {}).get("minion") != 600:
                continue
            rows.append((d["temp_c"]["minshire"][0], d["board_w"]))
    return np.array(rows) if rows else None


for name in sorted(os.listdir(D)):
    p = os.path.join(D, name)
    if not os.path.isdir(p) or not name.startswith("p"):
        continue
    a = load(p)
    if a is None or len(a) < 100:
        print(f"{name}: no usable cooling")
        continue
    T, W = a[:, 0], a[:, 1]
    print(f"\n=== {name}: {len(T)} idle samples at 600 MHz, {T.min():.0f}-{T.max():.0f} C ===")
    for lo, hi in ((51, 58), (51, 67), (49, 70), (51, 70)):
        m = (T >= lo) & (T <= hi)
        if m.sum() < 50 or len(set(T[m])) < 3:
            print(f"  {lo}-{hi} C: too few ({m.sum()})")
            continue
        k, b = np.polyfit(T[m], W[m], 1)
        r = W[m] - (k * T[m] + b)
        print(f"  {lo:2d}-{hi:2d} C: slope {k:7.4f} W/C   intercept {b:8.3f} W   "
              f"rms {np.sqrt(np.mean(r**2)):.4f} W   n {m.sum():6d}   spanC {T[m].max()-T[m].min():.0f}")
    # per-degree means, the shape the exponential law is fitted to
    print("   per-degree mean board W:",
          " ".join(f"{int(t)}:{W[T == t].mean():.2f}" for t in sorted(set(T), reverse=True)))
