#!/usr/bin/env python3
"""heat-q145a, Part 1: E97's pooled idle law re-derived by independent code from E97's committed Part B pass (post hoc).

E97's method, as its README and e97.json state it: the pass's rests (marks of kind "rest": R0, R1, R2), samples from 20 s after each rest's
start to its end at the 600 MHz clock, the die read as the 34-sensor mean of the raw codes (E97's code_to_c, as smoke_gate_e176.py has it);
bins of 0.5 C of that mean, each bin with at least 20 samples one point (its mean T, its mean board W); a quadratic through the points.
Compared with e97.json > holds.idle_law_pooled and with heat_q138t.py's constants; its slope at 51-66 C.

    python3 -B rederive_e97.py <lab repo top> <out.json>
"""
import gzip
import json
import os
import sys

import numpy as np

G_TS, H_TS, CAL5 = 57400, 249400, 4096


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def main():
    top, outp = sys.argv[1], sys.argv[2]
    d = os.path.join(top, "docs/reports/data/2026-11-01-e97-heat-low-power-steady/aifoundry3/e97/p9720")
    rests = [json.loads(x) for x in open(os.path.join(d, "marks.jsonl")) if x.startswith("{") and '"rest"' in x]
    rests = [r for r in rests if r.get("kind") == "rest"]
    xs, ys = [], []
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                s = json.loads(line)
            except ValueError:
                continue
            t = s.get("t_ms")
            if t is None or (s.get("mhz") or {}).get("minion") != 600:
                continue
            if not any(r["t_start_ms"] + 20000 <= t < r["t_end_ms"] for r in rests):
                continue
            pv = s.get("pvt") or {}
            cs = pv.get("c") or []
            if pv.get("st") != 0 or pv.get("f") or len(cs) != 34:
                continue
            xs.append(sum(code_to_c(c) for c in cs) / 34.0)
            ys.append(float(s["board_w"]))
    x, y = np.array(xs), np.array(ys)
    b = np.floor(x / 0.5).astype(int)
    bx, by = [], []
    for i in np.unique(b):
        q = b == i
        if q.sum() >= 20:
            bx.append(float(x[q].mean()))
            by.append(float(y[q].mean()))
    bx, by = np.array(bx), np.array(by)
    c = np.polyfit(bx, by, 2)
    com = json.load(open(os.path.join(top, "docs/reports/data/2026-11-01-e97-heat-low-power-steady/e97.json")))["holds"]["idle_law_pooled"]
    out = {"rests": [r["name"] for r in rests], "samples": int(len(x)), "bins": int(len(bx)), "T_range": [float(bx.min()), float(bx.max())],
           "poly_rederived": [float(v) for v in c], "poly_committed": com["poly"], "samples_committed": com["samples"], "bins_committed": com["bins"],
           "max_abs_poly_diff": float(max(abs(a - b_) for a, b_ in zip(c, com["poly"]))),
           "slope_rederived": {str(T): float(2 * c[0] * T + c[1]) for T in (51, 55, 58, 60, 62, 66)},
           "slope_committed": {str(T): float(2 * com["poly"][0] * T + com["poly"][1]) for T in (51, 55, 58, 60, 62, 66)}}
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("slope_rederived", "slope_committed")}))
    print("slope re-derived", {k: round(v, 4) for k, v in out["slope_rederived"].items()})
    print("slope committed ", {k: round(v, 4) for k, v in out["slope_committed"].items()})


if __name__ == "__main__":
    main()
