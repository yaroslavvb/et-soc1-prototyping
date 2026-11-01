#!/usr/bin/env python3
"""E92, post hoc and labelled so: a crude, independent look at the raw telemetry, all four passes: the median board power in each
run's [t0+1 s, t0+3 s), with no gate, no interpolation of the zeros and no leakage correction, because a median does not see the
board meter's dips. Standard library only; run it from this directory: python3 crude-check.py > crude-check.txt"""
import gzip, json, os, statistics as st, math
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),"aifoundry3","kinds")
out={}
for p in ("p9210","p9211","p9212","p9213"):
    d=os.path.join(R,p)
    tel=[json.loads(l) for l in gzip.open(os.path.join(d,"telemetry.jsonl.gz"),"rt") if l.startswith("{")]
    tt=[(s["t_ms"],s["board_w"]) for s in tel]
    recs=[json.loads(l) for l in open(os.path.join(d,"runs.jsonl"))]
    t0={}
    for r in recs:
        k=(r["item"],r.get("pos"))
        t0[k]=min(t0.get(k,1e18),r["t_start_ms"])
    vals={}
    for (it,pos),t in t0.items():
        w=[b for (x,b) in tt if t+1000<=x<t+3000]
        if w: vals.setdefault(it,[]).append(st.median(w))
    out[p]={k:st.fmean(v) for k,v in vals.items()}
pairs=[("fp32.h_add","fp32.c_abs"),("fp32.h_sub","fp32.h_add"),("fp32.c_alt","fp32.c_abs"),("fp32.h_allsub","fp32.h_add"),("fp32.c_neg","fp32.c_abs"),("fp16.h_add","fp16.c_abs"),("fp16.h_sub","fp16.h_add"),("fp16.c_alt","fp16.c_abs"),("fp16.h_allsub","fp16.h_add"),("fp32.i_sub","fp32.i_add"),("fp32.r_h_sub","fp32.r_h_add"),("fp32.w_h_sub","fp32.w_h_add"),("fp32.wr_h_sub","fp32.wr_h_add"),("fp16.hh_sub","fp16.c_abs"),("fp16.hl_sub","fp16.c_abs"),("fp16.h_sub","fp16.c_abs"),("fp32.s_abs","fp32.c_abs"),("fp16.s_abs","fp16.c_abs"),("fp32.signs","fp32.ones"),("fp16.signs","fp16.ones")]
T={2:4.303,3:3.182}
for a,b in pairs:
    v=[out[p][a]-out[p][b] for p in out]
    m=st.fmean(v); ci=st.stdev(v)/math.sqrt(len(v))*3.182
    print(f"{a:16s}- {b:12s} {m:+7.3f} +- {ci:5.3f}  (4 passes, medians) {[round(x,2) for x in v]}")
