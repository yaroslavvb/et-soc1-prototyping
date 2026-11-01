#!/usr/bin/env python3
"""E108, post hoc and labelled so: a crude, independent look at the raw telemetry of every finished pass: the median board power in each run's
[t0 + 1 s, t0 + 3 s), with no gate, no interpolation of the zeros and no leakage correction, because a median does not see the board meter's dips
(E92's crude-check.py, ported). Standard library only; run it from this directory: python3 crude-check.py > crude-check.txt"""
import glob
import gzip
import json
import math
import os
import statistics as st

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aifoundry1-c1", "signloc")
T = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
out = {}
for d in sorted(glob.glob(os.path.join(R, "p108[1-9][0-9]"))):
    if not os.path.exists(os.path.join(d, "block.json")) or '"status":"ok"' not in open(os.path.join(d, "block.json")).read():
        continue
    tel = [json.loads(line) for line in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if line.startswith("{")]
    tt = [(s["t_ms"], s.get("board_w")) for s in tel if s.get("board_w") is not None]
    recs = [json.loads(line) for line in open(os.path.join(d, "runs.jsonl"))]
    t0 = {}
    for r in recs:
        if r.get("launch", 0) < 0:
            continue
        k = (r["item"], r.get("pos"))
        t0[k] = min(t0.get(k, 1e18), r["t_start_ms"])
    vals = {}
    for (it, pos), t in t0.items():
        w = [b for (x, b) in tt if t + 1000 <= x < t + 3000]
        if w:
            vals.setdefault(it, []).append(st.median(w))
    out[os.path.basename(d)] = {k: st.fmean(v) for k, v in vals.items()}
print("passes:", sorted(out))
pairs = [("fp32.signs", "fp32.ones"), ("fp16.signs", "fp16.ones"), ("fp32.z_s", "fp32.c_abs"), ("fp16.z_s", "fp16.c_abs"), ("fp32.s_abs", "fp32.c_abs"), ("fp16.z_ss", "fp16.c_abs"),
         ("fp32.s_walk", "fp32.s_abs"), ("fp32.c_mx_f", "fp32.s_abs"), ("fp32.c_ex_f", "fp32.s_abs"), ("fp32.c_sg_f", "fp32.s_abs"), ("fp32.s_walk", "fp32.c_mx_f"),
         ("fp32.b_B_w", "fp32.z_s"), ("fp32.b_B_z", "fp32.z_s"), ("fp32.b_B_w", "fp32.b_B_z"), ("fp32.b_A_f", "fp32.c_abs"), ("fp32.b_B_f", "fp32.c_abs"),
         ("fp32.b_A_w", "fp32.b_A_f"), ("fp32.b_B_w", "fp32.b_B_f"), ("fp32.s_abs", "fp32.b_B_f"), ("fp32.s_walk", "fp32.b_B_w"), ("fp32.h_sub", "fp32.h_add"),
         ("fp32.m_h_sub", "fp32.w_h_add"), ("fp16.m_h_sub", "fp16.w_h_add")]
for a, b in pairs:
    v = [out[p][a] - out[p][b] for p in out if a in out[p] and b in out[p]]
    if len(v) < 2:
        continue
    m = st.fmean(v)
    ci = st.stdev(v) / math.sqrt(len(v)) * T[len(v) - 1]
    print(f"{a:14s} - {b:12s} {m:+7.3f} +- {ci:5.3f}  ({len(v)} passes, medians) {[round(x, 2) for x in v]}")


def ratio(num, den):
    v = [(out[p][num[0]] - out[p][num[1]]) / (out[p][den[0]] - out[p][den[1]]) for p in out]
    m = st.fmean(v)
    return m, st.stdev(v) / math.sqrt(len(v)) * T[len(v) - 1], v


for nm, num, den in (("share_het (R7)", ("fp32.c_mx_f", "fp32.s_abs"), ("fp32.s_walk", "fp32.s_abs")), ("share_het_z (R12)", ("fp32.b_B_z", "fp32.z_s"), ("fp32.b_B_w", "fp32.z_s")),
                     ("fp32 share_z", ("fp32.z_s", "fp32.c_abs"), ("fp32.signs", "fp32.ones")), ("fp16 share_z", ("fp16.z_s", "fp16.c_abs"), ("fp16.signs", "fp16.ones")),
                     ("alt_ratio (R9)", ("fp32.m_h_sub", "fp32.w_h_add"), ("fp32.h_sub", "fp32.h_add")), ("alt_walk_ratio (R10)", ("fp16.m_h_sub", "fp16.w_h_add"), ("fp32.m_h_sub", "fp32.w_h_add"))):
    m, ci, v = ratio(num, den)
    print(f"{nm:22s} {m:.3f} +- {ci:.3f}  per pass {[round(x, 3) for x in v]}")
