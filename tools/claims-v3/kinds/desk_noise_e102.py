#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E102 (Q132): the desk evidence behind E102's choices, from committed data of other experiments only (no E102 data exist when this is written). Run from the repo's root; its output is desk_noise_e102.txt.

  [1] E79's int8 B `kg` list, per pass, at no temperature term, at its fitted slope, and at E71's. The reading is in whole degrees, and at int8's low power a run's window sits on a step's edge (58.0 to 59.0), so the correction
      adds up to k x 1 C to one run and nothing to the next. So the slope arm's bounds come from the reading, not from the card.
  [2] Card 1's run-to-run noise on the low-power anchors: E93's and E82's three reads per pass (the middle read off the straight line through the other two), board against rail.
"""
import csv
import math
import statistics as st
import numpy as np

BASE = "docs/reports/data/"
R = list(csv.DictReader(open(BASE + "2026-10-31-e79-fp16-int8-bit-prices/runs.csv")))
B = [r for r in R if r["pass"] in ("7920", "7921", "7922", "7923")]
print("[1] E79's int8 B kg steps over h8q, watts, per pass 7920-7923, aifoundry3, 1,024 flips per op per bit (1 W is 507 fJ)")
for k, name in ((0.0, "no temperature term"), (0.0834, "E79's fitted 0.0834"), (0.3803, "E71's 0.3803")):
    print(f"  {name}")
    means = []
    for j in range(8):
        d = []
        for p in ("7920", "7921", "7922", "7923"):
            x = [r for r in B if r["pass"] == p and r["item"] == f"b8k_{j}"][0]
            z = [r for r in B if r["pass"] == p and r["item"] == "h8q"][0]
            c = lambda r: float(r["p_raw"]) - k * (float(r["t_win"]) - float(r["start_c"]))
            d.append(c(x) - c(z))
        means.append(st.mean(d))
        print(f"    bit {j}: " + " ".join(f"{v:+.3f}" for v in d) + f"   mean {st.mean(d):+.3f}  sd {st.stdev(d):.3f}")
    odd, even = [means[i] for i in (1, 3, 5)], [means[i] for i in (0, 2, 4)]
    print(f"    bits 1,3,5 mean {st.mean(odd):+.3f}; bits 0,2,4 mean {st.mean(even):+.3f}; all eight mean {st.mean(means):+.3f}")
tw = sorted({round(float(r["t_win"]), 2) for r in B if r["item"] == "h8q" or r["item"].startswith("b8k")})
print(f"  the window's mean reading across those runs: {tw[:14]} ...; launch reading 58.0")
print()
print("[2] the run-to-run noise on low-power anchors, watts per run: the middle of a pass's three reads off the line through the other two, over sqrt(1.5)")
for name, path in (("E93", "2026-11-01-e93-zero-gate-silicon/runs.csv"), ("E82", "2026-10-31-e82-kinds-aifoundry1/runs.csv")):
    rows = list(csv.DictReader(open(BASE + path)))
    for it in ("fp32.zeros", "fp16.zeros", "int8.zeros"):
        out = {}
        for key in ("p_raw", "rail_raw"):
            res = []
            for p in sorted({r["pass"] for r in rows}):
                rr = sorted([r for r in rows if r["pass"] == p and r["item"] == it and float(r.get("fail") or 0) == 0], key=lambda r: float(r["t0_ms"]))
                if len(rr) == 3:
                    t = [float(r["t0_ms"]) for r in rr]
                    y = [float(r[key]) for r in rr]
                    res.append((y[1] - (y[0] + (y[2] - y[0]) * (t[1] - t[0]) / (t[2] - t[0]))) / math.sqrt(1.5))
            out[key] = (round(float(np.sqrt(np.mean(np.square(res)))), 3), len(res))
        print(f"  {name} {it:11s} board {out['p_raw'][0]:.3f} W, rail {out['rail_raw'][0]:.3f} W, {out['p_raw'][1]} passes")
