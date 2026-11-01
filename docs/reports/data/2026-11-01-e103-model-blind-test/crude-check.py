#!/usr/bin/env python3
"""E103, post hoc and labelled so: a crude, independent look at the raw telemetry. The median board power in each run's [t0 + 1 s, t0 + 3 s), minus the same pass's median over that type's
three zeros, with no gate, no interpolation of the zeros and no leakage correction. A median does not see the board meter's dips, and this code shares nothing with the reduction. Standard library only.

    python3 crude-check.py > crude-check.txt
"""
import gzip
import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "aifoundry1-c1", "kinds")
reg = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "kinds", "predictions-e103.json")))
out = {}
for p in ("p10310", "p10311", "p10312"):
    d = os.path.join(R, p)
    tel = [json.loads(line) for line in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if line.startswith("{")]
    tt = [(s["t_ms"], s["board_w"]) for s in tel if s.get("board_w") is not None]
    t0 = {}
    for line in open(os.path.join(d, "runs.jsonl")):
        r = json.loads(line)
        k = (r["item"], r.get("pos"))
        t0[k] = min(t0.get(k, 1e18), r["t_start_ms"])
    vals = {}
    for (it, pos), t in t0.items():
        w = [b for (x, b) in tt if t + 1000 <= x < t + 3000]
        if w:
            vals.setdefault(it, []).append(st.median(w))
    out[p] = {k: st.fmean(v) for k, v in vals.items()}
print("# tile, crude D per pass, its mean, the reduction's D, M4 or I3")
red = json.load(open(os.path.join(HERE, "e103.json")))["items"]
rows = []
for k, t in sorted(reg["tiles"].items()):
    z = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}[t["type"]]
    v = [out[p][k] - out[p][z] for p in out if k in out[p] and z in out[p]]
    m = st.fmean(v)
    rows.append((k, t["type"], m, red[k]["D"]["mean"], t["pred"]["M"], t["pred"]["q130n"]))
    print(f"{k:26s} {[round(x, 2) for x in v]} crude {m:6.2f}  reduction {red[k]['D']['mean']:6.2f}  M {t['pred']['M']:6.2f}")


def rms(x):
    return math.sqrt(sum(a * a for a in x) / len(x))


for label, sel in (("floats", [r for r in rows if r[1] != "int8"]), ("fp32", [r for r in rows if r[1] == "fp32"]), ("fp16", [r for r in rows if r[1] == "fp16"]), ("int8", [r for r in rows if r[1] == "int8"])):
    print(f"{label:7s} n {len(sel):2d}: rms(crude - reduction) {rms([r[2] - r[3] for r in sel]):.3f} W; rms(crude - M) {rms([r[2] - r[4] for r in sel]):.3f} W; rms(crude - Q130(n)) {rms([r[2] - r[5] for r in sel]):.3f} W")
