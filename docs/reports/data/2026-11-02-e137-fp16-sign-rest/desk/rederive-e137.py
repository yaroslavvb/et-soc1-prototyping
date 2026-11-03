#!/usr/bin/env python3
"""E137: the headline numbers re-derived from the committed files without E137's reducer or scorer (Mon 2 Nov 2026, after the results commit
df05d9f3): per-pass D from runs.csv (the primary's run rows), 13710 left out by its zeros-line departure recomputed from the same rows, the shares and
contrasts with t(0.975, n - 1), M4's frozen numbers from predictions-e137.json, the telemetry maxima, the card-minutes from the session's config
reads, the lane-bit price and the ratio to E128. Standard library only. POST HOC.

    python3 docs/reports/data/2026-11-02-e137-fp16-sign-rest/desk/rederive-e137.py docs/reports/data/2026-11-02-e137-fp16-sign-rest \
        tools/claims-v3/e137/predictions-e137.json docs/reports/data/2026-11-02-e128-fp16-signs/e128.json > .../desk/rederive-e137.txt
SPDX-License-Identifier: Apache-2.0
"""
import csv, json, math, statistics, sys, gzip, glob, os, datetime
D = sys.argv[1]
T = {5: 2.571, 4: 2.776, 6: 2.447, 1: 12.706}
rows = list(csv.DictReader(open(os.path.join(D, "runs.csv"))))
print("rows", len(rows), "fail nonempty", sum(1 for r in rows if r["fail"] not in ("", "0", "[]")))
# zeros-line departure, independently: per pass, per zeros anchor, 3 points (t0_ms, p80)
for p in sorted({r["pass"] for r in rows}):
    for a in ("fp32.zeros", "fp16.zeros", "int8.zeros"):
        pts = sorted((float(r["t0_ms"]), float(r["p80"])) for r in rows if r["pass"] == p and r["item"] == a)
        (t1, v1), (t2, v2), (t3, v3) = pts
        dep = v2 - (v1 + (v3 - v1) * (t2 - t1) / (t3 - t1))
        if abs(dep) > 0.2: print(" ", p, a, f"departure {dep:+.3f}")
keep = [p for p in sorted({r["pass"] for r in rows}) if p != "13710"]
by = {}
for r in rows:
    if r["pass"] in keep and r["D"] not in ("",):
        by.setdefault(r["pass"], {}).setdefault(r["item"], []).append(float(r["D"]))
pp = {p: {k: sum(v) / len(v) for k, v in d.items()} for p, d in by.items()}
def ci(v):
    m = sum(v) / len(v); return m, T[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)
def show(name, f):
    v = [f(pp[p]) for p in keep]; m, c, n = ci(v); print(f"  {name:22s} {m:+.4f} ± {c:.4f} (n {n})"); return m, c
g = lambda r, *t: r["fp16." + t[0]]
show("share_het_m", lambda r: (r["fp16.b_B_zm"] - r["fp16.z_s"]) / (r["fp16.b_B_wm"] - r["fp16.z_s"]))
show("share_walk_m", lambda r: (r["fp16.b_B_wm"] - r["fp16.b_B_zm"]) / (r["fp16.b_B_wm"] - r["fp16.z_s"]))
show("share_het_z", lambda r: (r["fp16.b_B_z"] - r["fp16.z_s"]) / (r["fp16.b_B_w"] - r["fp16.z_s"]))
show("design_m", lambda r: (r["fp16.b_B_zm"] - r["fp16.z_s"]) / (r["fp16.b_B_wm"] - r["fp16.z_s"]) - (r["fp16.b_B_z"] - r["fp16.z_s"]) / (r["fp16.b_B_w"] - r["fp16.z_s"]))
show("step", lambda r: r["fp16.signs"] - r["fp16.ones"])
show("Bm_het", lambda r: r["fp16.b_B_zm"] - r["fp16.z_s"])
show("Bm_walk", lambda r: r["fp16.b_B_wm"] - r["fp16.b_B_zm"])
show("Bm_rest", lambda r: r["fp16.b_B_wm"] - r["fp16.z_s"])
show("Bz_het", lambda r: r["fp16.b_B_z"] - r["fp16.z_s"])
show("Bz_rest", lambda r: r["fp16.b_B_w"] - r["fp16.z_s"])
# M4 sign contrasts rms (frozen M from predictions)
reg = json.load(open(sys.argv[2]))
Q = reg["quantities"]
errs = []
for q in reg["rules"]["E137-R7"]["legs"]:
    qq = Q[q]; v = [sum(pp[p][t] for t in qq["plus"]) - sum(pp[p][t] for t in qq["minus"]) for p in keep]
    m = sum(v) / len(v); errs.append(m - qq["M"]); print(f"  R7 {q:12s} {m:.4f} M4 {qq['M']:.4f} err {m-qq['M']:+.4f} inside {abs(m-qq['M'])<=qq['half95']}")
print("  R7 rms", math.sqrt(sum(e*e for e in errs)/len(errs)), "mean", sum(errs)/len(errs))
e6 = [sum(pp[p][t] for p in keep)/len(keep) - reg["tiles"][t]["pred"]["M"] for t in reg["tiles"]]
print("  R6 rms", math.sqrt(sum(e*e for e in e6)/len(e6)), "bias", sum(e6)/len(e6))
# tie cells from all kept passes (item mean of per-pass means)
for c in ("fp32.randn", "fp16.randn", "anchor_pi", "int8.full"):
    v = [pp[p][c] for p in keep if c in pp[p]]; print("  S1", c, sum(v)/len(v))
# telemetry max and sample count; mhz
n=0; bm=0; tm=0; mhz=set()
for f in glob.glob(os.path.join(D, "aifoundry1-c1/e137/*/telemetry.jsonl.gz")):
    for l in gzip.open(f, "rt"):
        if not l.startswith("{"): continue
        s=json.loads(l); n+=1; bm=max(bm, s.get("board_w") or 0); tm=max(tm, (s.get("temp_c") or {}).get("minshire",[0])[0]); mhz.add((s.get("mhz") or {}).get("minion"))
print("telemetry samples", n, "board max", bm, "minshire mean max", tm, "mhz", mhz)
a=open(os.path.join(D,"logs/config-session-start.json.time")).read().strip(); b=open(os.path.join(D,"logs/config-session-end.json.time")).read().strip()
ta=datetime.datetime.fromisoformat(a); tb=datetime.datetime.fromisoformat(b); print("card minutes", (tb-ta).total_seconds()/60, a, b)
rate = statistics.mean(float(r["rate"]) for r in rows if r["item"]=="fp32.randn" and r["pass"] in keep)
print("fJ/bit Bm_het", (sum((pp[p]["fp16.b_B_zm"]-pp[p]["fp16.z_s"]) for p in keep)/len(keep))/((45114+45562)*rate)*1e15, "rate", rate)
r128 = json.load(open(sys.argv[3]))
print("E137/E128 item ratios median", statistics.median(sum(pp[p][t] for p in keep)/len(keep)/r128["items"][t]["D"]["mean"] for t in reg["tiles"]))
