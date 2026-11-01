#!/usr/bin/env python3
"""E114 (Q133), POST HOC, labelled, never a verdict: written after the data, when E114-R3 read SLOWER where E84 had int8
zeros faster. For every sustained run of the five kinds in E114's session and in E84's, the climb at each 8 s process
start: seconds from the process's first kernel launch to its first 800 MHz sample, the gap since the previous process
ended, and how many of the process starts fall in the last 40 s (the window the rules read).

    python3 posthoc_climb.py > climb.txt        # in this directory
"""
import gzip
import json
import os
import statistics as st

D = os.path.dirname(os.path.abspath(__file__))
SESS = {"E114": os.path.join(D, "..", "s1"),
        "E84": os.path.join(D, "..", "..", "2026-10-31-e84-speed-aifoundry1-card0", "s1")}
KINDS = ["fp16/zeros", "fp16/ones", "fp16/randn", "int8/zeros", "int8/full"]


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        return [json.loads(l) for l in f if l.startswith("{")]


def kind_of(v):
    p = v[5:].split("/")
    return f"{p[-2]}/{p[-1][:-4]}"


out = {}
for name, rd in SESS.items():
    runs = jl(os.path.join(rd, "runs.jsonl"))
    lp = os.path.join(rd, "launches.jsonl.gz")
    launches = jl(lp if os.path.exists(lp) else os.path.join(rd, "launches.jsonl"))
    for r in runs:
        if r["block"] not in ("SUS", "SUS2"):
            continue
        k = kind_of(r["values"])
        if k not in KINDS:
            continue
        tp = os.path.join(rd, r["tel"])
        tel = jl(tp + ".gz" if os.path.exists(tp + ".gz") else tp)
        s = sorted((int(d["t_ms"]), (d.get("mhz") or {}).get("minion")) for d in tel if "t_ms" in d)
        procs = sorted([L for L in launches if L["run"] == r["run"] and L.get("role") == "work"], key=lambda L: L["proc"])
        t1 = max(L["t_end_ms"] for L in procs)
        tl = t1 - 40000
        climbs, gaps, kgaps, in_last = [], [], [], 0
        prev_end = prev_kend = None
        for L in procs:
            ks = [x for x in L.get("sparsity", []) if x.get("t_start_ms")]
            a = min(x["t_start_ms"] for x in ks) if ks else L["t_start_ms"]
            b = L["t_end_ms"]
            f800 = next((t for t, m in s if a <= t <= b and m == 800), None)
            climbs.append(round((f800 - a) / 1000.0, 2) if f800 else None)
            gaps.append(round((a - prev_end) / 1000.0, 2) if prev_end else None)
            kgaps.append(round((a - prev_kend) / 1000.0, 3) if prev_kend else None)
            prev_end = b
            prev_kend = max(x["t_end_ms"] for x in ks if x.get("t_end_ms")) if ks else b
            if a >= tl:
                in_last += 1
        rec = {"run": r["run"], "climb_s": climbs, "gap_s": gaps, "kernel_gap_s": kgaps, "starts_in_last_40s": in_last}
        out.setdefault(name, {}).setdefault(k, []).append(rec)

for name in SESS:
    print(f"== {name}")
    for k in KINDS:
        recs = out.get(name, {}).get(k, [])
        for rec in recs:
            cl = [c for c in rec["climb_s"] if c is not None]
            print(f"{k:11s} {rec['run']:26s} climb per process {rec['climb_s']} (mean {st.mean(cl):.2f} s); "
                  f"gap before each {rec['gap_s'][1:]}; process starts in the last 40 s: {rec['starts_in_last_40s']}")
print("== mean climb by kind, every process of every run")
for name in SESS:
    for k in KINDS:
        cl = [c for rec in out.get(name, {}).get(k, []) for c in rec["climb_s"] if c is not None]
        if cl:
            print(f"{name:4s} {k:11s} n {len(cl):3d} processes, climb mean {st.mean(cl):.3f} s, sd {st.stdev(cl):.3f}, "
                  f"min {min(cl):.2f}, max {max(cl):.2f}")
json.dump(out, open(os.path.join(D, "climb.json"), "w"), indent=1)
print("== long climbs (> 0.4 s) among the process starts inside the last 40 s, per run, and over every process start")
for name in SESS:
    tot = [0, 0]
    for k in KINDS:
        ls = []
        for rec in out.get(name, {}).get(k, []):
            n = rec["starts_in_last_40s"]
            ls.append(sum(1 for c in rec["climb_s"][-n:] if c is not None and c > 0.4))
            tot[0] += sum(1 for c in rec["climb_s"] if c is not None and c > 0.4)
            tot[1] += len(rec["climb_s"])
        print(f"{name:4s} {k:11s} {ls}")
    print(f"{name:4s} every process start: {tot[0]} of {tot[1]} long ({100 * tot[0] / tot[1]:.0f}%)")
print("== the climbs' distribution, and the idle time between processes (last kernel's end to the next process's first kernel)")
for name in SESS:
    cl = [c for k in KINDS for rec in out.get(name, {}).get(k, []) for c in rec["climb_s"] if c is not None]
    kg = [g for k in KINDS for rec in out.get(name, {}).get(k, []) for g in rec["kernel_gap_s"] if g is not None]
    edges = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 1.25, 1.5]
    hist = [sum(1 for c in cl if lo <= c < hi) for lo, hi in zip(edges, edges[1:])]
    print(f"{name:4s} climbs by bin {list(zip(edges, hist))}; short (<= 0.4 s) max {max(c for c in cl if c <= 0.4):.2f}, "
          f"long (> 0.4 s) min {min(c for c in cl if c > 0.4):.2f}, max {max(cl):.2f}")
    print(f"{name:4s} idle between processes: median {st.median(kg):.3f} s, min {min(kg):.3f}, max {max(kg):.3f} (n {len(kg)})")
print("== long climbs at the first process start of each run (it follows the sampler start, the gate and a 1 s pause) "
      "and at the eight after it (each follows a ~0.33 s idle gap)")
for name in SESS:
    first = [rec["climb_s"][0] for k in KINDS for rec in out.get(name, {}).get(k, [])]
    later = [c for k in KINDS for rec in out.get(name, {}).get(k, []) for c in rec["climb_s"][1:] if c is not None]
    nl = sum(1 for c in later if c > 0.4)
    print(f"{name:4s} first starts: {sum(1 for c in first if c is not None and c > 0.4)} of {len(first)} long "
          f"({min(first):.2f}-{max(first):.2f} s); later starts: {nl} of {len(later)} long ({100 * nl / len(later):.0f}%)")
