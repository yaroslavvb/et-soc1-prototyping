#!/usr/bin/env python3
"""E107, POST HOC (written after the data, labelled): board readings inside each run's power window, [t0+1 s, t0+3 s) (reduce_e78.py's), that sit more than
10 W below the window's median - a held or dropped PMIC sample at a launch boundary, as in pass 10712's c1.fp32.randn - and what that run's window mean
reads without them. It changes no registered number. Standard library.

    python3 tools/claims-v3/e107/glitch_e107.py <pass dir> [...] > glitches.txt
"""
import gzip
import json
import statistics as st
import sys

print("pass   pos item                    low samples (ms after t0: W)                          window mean  without  diff W")
n_runs = n_hit = 0
for d in sys.argv[1:]:
    tel = []
    for ln in gzip.open(f"{d}/telemetry.jsonl.gz", "rt"):
        if ln.startswith("{"):
            x = json.loads(ln)
            tel.append((x["t_ms"], x["board_w"]))
    runs = {}
    for ln in open(f"{d}/runs.jsonl"):
        r = json.loads(ln)
        if r.get("test") == "fma":
            k = (r["block"], r["pos"], r["item"])
            runs[k] = min(runs.get(k, 1e18), r["t_start_ms"])
    for (blk, pos, item), t0 in sorted(runs.items(), key=lambda kv: kv[1]):
        w = [(t, b) for t, b in tel if t0 + 1000 <= t < t0 + 3000]
        if len(w) < 5:
            continue
        n_runs += 1
        med = st.median(b for _, b in w)
        low = [(t - t0, b) for t, b in w if b < med - 10]
        if low:
            n_hit += 1
            keep = [b for _, b in w if b >= med - 10]
            print(f"{blk} {pos:4d} {item:22s} {str(low):55s} {st.mean(b for _, b in w):8.2f} {st.mean(keep):8.2f} {st.mean(keep) - st.mean(b for _, b in w):+6.2f}")
print(f"runs read {n_runs}, runs with a low sample {n_hit}")
