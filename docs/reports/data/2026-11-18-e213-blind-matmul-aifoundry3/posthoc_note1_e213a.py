#!/usr/bin/env python3
"""E213 arm A, dated note 1 (post hoc): the figures of its sections 2 and 3, printed from this directory's measured records and E213's
frozen files (Wed 18 Nov 2026, the fix lane fix-e213d, Q216, after the data verifier verify-e213d). Python's own modules only; reads only.

    /usr/bin/python3 -I -B posthoc_note1_e213a.py [--json <a new path>] [--top <the lab's top>]

Run from this directory (the lab's top is then ../../../..). It prints posthoc-note1-e213a.txt byte for byte and, with --json, writes the
JSON that posthoc-note1-e213a.json holds. Inputs, each checked at its registered sha256 (plan-e213.json's inputs_sha256):
tools/claims-v3/e213/points-e213.json and tools/matmul/mm1/v3/out/mm1_v3_e213.csv (MM1-v3's frozen arm A forecasts, at its land b1493082);
from this directory, data-e213.json (the reducer's p_work and p_rest), session/runs/<run>/run.json (each run's process window) and
session/telemetry.jsonl.gz (the board readings), and session/smoke/<s>/smoke.json (the smoke's command lines).
Section 2: the smoke's --seconds and --budget, as points-e213.json lists them and as the session ran them.
Section 3: each point and reference run's board peak (the highest board reading inside its process window) against MM1-v3's planning
peak (E213.md section 6, plan_e213.py's form: the point's W over idle + its rest law + 2 W); the gemmLnc points beside their gemmL twins.
Labels: the board readings are measured; the planning peaks, the line and the stops are registered; the differences are desk arithmetic,
post hoc and REPORTED; no rule reads them. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import csv
import datetime
import gzip
import hashlib
import json
import os
import statistics
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--json")
ap.add_argument("--top", default=os.path.normpath(os.path.join(HERE, "..", "..", "..", "..")))
ap.add_argument("--dir", default=HERE)
a = ap.parse_args()
TOP, D = a.top, a.dir
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
PINS = {"tools/claims-v3/e213/points-e213.json": "f122b62500ce7d0f5e924f7454adb074d9ca673c328fe3c98c64a9b906d65d15",
        "tools/matmul/mm1/v3/out/mm1_v3_e213.csv": "01a2fdaef0b506b218fad1975dacf397a2c728010a595c8b4dadcbf569c07a49"}
for rel, pin in PINS.items():
    got = hashlib.sha256(open(os.path.join(TOP,rel), "rb").read()).hexdigest()
    if got != pin:
        sys.exit(f"REFUSE: {rel} reads {got[:12]}, not its registered {pin[:12]}")
P = json.load(open(os.path.join(TOP,"tools/claims-v3/e213/points-e213.json")))
V3 = {r["id"]: r for r in csv.DictReader(open(os.path.join(TOP,"tools/matmul/mm1/v3/out/mm1_v3_e213.csv"), newline=""))}
DA = json.load(open(os.path.join(D, "data-e213.json")))["arms"]["A"]
pts = {p["id"]: p for p in P["arms"]["A"]["points"]}
out = {"inputs_sha256_checked": PINS}
print("E213 arm A, dated note 1 (post hoc): the figures of sections 2 and 3 (posthoc_note1_e213a.py)")
print("inputs at their registered sha256: points-e213.json f122b625..., mm1_v3_e213.csv 01a2fdae...")
print()
print("SECTION 2. The smoke's --seconds and --budget")


def arg(v, k):
    return v[v.index(k) + 1] if k in v else None


sm = []
for s in P["arms"]["A"]["smoke"] + P["arms"]["B"]["smoke"]:
    sm.append({"id": s["id"], "arm_tag": s["arm_tag"], "points_file": [arg(s["host_args"], "--seconds"), arg(s["host_args"], "--budget")]})
for s in sm:
    if s["arm_tag"] == "A":
        sj = json.load(open(os.path.join(D, "session/smoke", s["id"], "smoke.json")))
        s["ran"] = [arg(sj["argv"], "--seconds"), arg(sj["argv"], "--budget")]
for s in sm:
    print(f"  {s['id']} (arm {s['arm_tag']}): points-e213.json host_args --seconds {s['points_file'][0]} --budget {s['points_file'][1]}"
          + (f"; this session's command line --seconds {s['ran'][0]} --budget {s['ran'][1]} (session/smoke/{s['id']}/smoke.json)" if "ran" in s
             else "; arm B: not run"))
out["smoke"] = sm
print()
print("SECTION 3. The board's peak in each point and reference run against MM1-v3's planning peak (W over idle + rest law + 2 W)")
tel = []
with gzip.open(os.path.join(D, "session/telemetry.jsonl.gz"), "rt") as f:
    for ln in f:
        o = json.loads(ln)
        if o.get("board_w") is not None:
            tel.append((o["t_ms"], o["board_w"]))
tel.sort()
times = [t for t, _ in tel]


def pst(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, TZ).strftime("%H:%M:%S.%f")[:-3]


rows = []
for pid, rec in sorted(DA["points"].items()):
    if pid not in pts:
        continue
    p, v = pts[pid], V3[pid]
    for r in rec["runs"]:
        key = r["detail"]["run"]
        pr = json.load(open(os.path.join(D, "session/runs", key, "run.json")))["procs"][0]
        i, j = bisect.bisect_left(times, pr["t0_ms"]), bisect.bisect_right(times, pr["t1_ms"])
        tm, bm = max(tel[i:j], key=lambda x: x[1])
        plan = float(v["W_over_idle"]) + float(v["P_rest_W_REPORTED"]) + 2.0
        rows.append({"id": pid, "run": key, "loop": p["loop"], "arm": p["arm"], "format": p["format"], "kind": p["kind"],
                     "mask": p["shire_mask"], "p_work_w": r["p_work_w"], "p_rest_w": r["p_rest_w"], "board_peak_w": bm,
                     "board_peak_pst": pst(tm), "n_samples": j - i, "planning_peak_w": round(plan, 2),
                     "peak_minus_plan_w": round(bm - plan, 2)})
over = [r for r in rows if r["board_peak_w"] > r["planning_peak_w"]]
rest = [r["peak_minus_plan_w"] for r in rows if r not in over]
print(f"  point and reference runs: {len(rows)} (the three tie runs and the smoke apart); board readings read: {len(tel)}")
print(f"  board peak above the planning peak: {len(over)} runs, all of them 'rgm136 gemmLnc': "
      f"{all(r['loop'] == 'rgm136 gemmLnc' for r in over)}; every 'rgm136 gemmLnc' run among them: "
      f"{len(over) == sum(1 for r in rows if r['loop'] == 'rgm136 gemmLnc')}")
print(f"  the other {len(rest)} runs: board peak minus planning peak, median {statistics.median(rest):+.2f} W, highest {max(rest):+.2f} W")
twins = {}
for r in rows:
    if r["loop"] == "rgm136 gemmL":
        twins.setdefault((r["arm"], r["format"], r["kind"], r["mask"]), []).append(r)
print("  run | point | configuration | p_work W | board peak W (PST) | planning peak W | peak - plan W | under the 65 W line by W"
      " | the gemmL twin: run, board peak W, planning peak W, peak - plan W")
lnc = []
for r in sorted(over, key=lambda r: r["run"]):
    tw = twins.get((r["arm"].replace("gemmLnc", "gemmL"), r["format"], r["kind"], r["mask"]), [])
    tws = "; ".join(f"{t['run']}, {t['board_peak_w']:.2f}, {t['planning_peak_w']:.2f}, {t['peak_minus_plan_w']:+.2f}" for t in tw) or "none"
    print(f"  {r['run']} | {r['id']} | {r['arm']} {r['format']} {r['kind']} {r['mask']} | {r['p_work_w']:.2f} | {r['board_peak_w']:.2f} "
          f"({r['board_peak_pst']}) | {r['planning_peak_w']:.2f} | {r['peak_minus_plan_w']:+.2f} | {65.0 - r['board_peak_w']:.2f} | {tws}")
    lnc.append(dict(r, twins=[{k: t[k] for k in ("run", "id", "board_peak_w", "planning_peak_w", "peak_minus_plan_w")} for t in tw]))
twr = {t["run"]: t["peak_minus_plan_w"] for r in lnc for t in r["twins"]}
twd = list(twr.values())
print(f"  the twins' board peak minus planning peak: {min(twd):+.2f} to {max(twd):+.2f} W ({len(twd)} twin runs of {len({r['id'] for r in lnc})} gemmLnc points)")
top = max(rows, key=lambda r: r["board_peak_w"])
print(f"  the session's highest board reading in a run: {top['board_peak_w']:.2f} W at {top['board_peak_pst']} PST ({top['run']}); "
      f"the arm's highest planning peak: {max(r['planning_peak_w'] for r in rows):.2f} W "
      f"({max(rows, key=lambda r: r['planning_peak_w'])['id']})")
out["section3"] = {"runs": len(rows), "board_readings": len(tel), "over_plan": lnc,
                   "others_median_peak_minus_plan_w": round(statistics.median(rest), 2), "others_highest_peak_minus_plan_w": round(max(rest), 2),
                   "twins_peak_minus_plan_w": [min(twd), max(twd)], "highest": {k: top[k] for k in ("run", "board_peak_w", "board_peak_pst")}}
if a.json:
    json.dump(out, open(a.json, "w"), indent=1, sort_keys=True)
    print()
    print("JSON written")
