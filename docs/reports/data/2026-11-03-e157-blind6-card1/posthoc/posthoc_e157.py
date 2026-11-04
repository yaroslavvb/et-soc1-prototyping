#!/usr/bin/env python3
"""E157, post hoc and reported only (written after the registered scoring; no rule, verdict, prediction or reduction changes). Standard
library only. From the committed reductions and scored.json in the data directory:
  (a) heat at the measured run length with E142's rule (M7's heat rows' HEAT_TRUN_MAX, 5.0 s): items whose median run length exceeds 5.0 s
      are left out (their run length is read across the heater's pass, not their own run), as E142's README C-note did;
  (b) E78's three random anchors (fp32.randn, fp16.randn, int8.full) and K1's six tiles against E142's, each footing like for like;
  (c) the errors by the pool's case, rms per model (priority 1 and 2, non-anchor);
  (d) the per-format errors of the 44 non-anchor tiles, each model.
    python3 posthoc/posthoc_e157.py <data dir>      # prints posthoc.txt's content
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

D = sys.argv[1]
ROOT = os.path.abspath(D)
while not os.path.isdir(os.path.join(ROOT, "tools", "claims-v3")) and ROOT != "/":
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e157"))
import score_e157 as S  # noqa: E402

reg = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e157", "predictions-e157.json")))
sc = json.load(open(os.path.join(D, "scored.json")))
prim = json.load(open(os.path.join(D, "e157.json")))
e142f = json.load(open(os.path.join(D, "e157-e142footing.json")))
E142 = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e142-blind5-card1", "e142.json")))
E142U = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-q139u-footing", "reduced", "e142-footing.json")))


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


print("E157 post hoc (reported only; nothing here is a verdict)")
# (a)
tr = S.run_lengths(os.path.join(D, "runs.csv"))
names = sorted(reg["tiles"])
mT, _ = S.measured(prim, names, "dT_win", 2)
p1 = reg["sets"]["priority1_by_format"]
long_ = sorted(t for t in names if tr.get(t, 0) > 5.0)
rows = S.rows_for(reg, mT, "heat", "M8", [t for t in names if t not in long_], tr)
print("\n(a) heat at the measured run length, items with a median run length > 5.0 s left out (E142's rule):", len(long_), "left out:", long_)
for f in ("fp32", "fp16", "int8"):
    e = [rows[t]["error"] for t in p1[f] if t in rows and rows[t]["error"] is not None]
    print(f"  {f}: rms {rms(e):.3f} C over {len(e)} priority-1 tiles (frozen 4.5 s: {sc['primary']['reported']['M8']['heat'][f]['rms']:.3f} C over "
          f"{sc['primary']['reported']['M8']['heat'][f]['n']})")
cov = S.coverage(rows, [t for t in reg["sets"]["priority1_all"] if t in rows])
print("  coverage:", cov.get("inside"), "of", cov.get("n"), "outside", cov.get("outside"))
# (b)
print("\n(b) the same tiles against E142 (D, W; mean over kept passes, E142's 5 passes): E157 - E142")
for frame, mine, theirs in (("Q139(u)'s footing", prim, E142U), ("E142's own footing (0.2414)", e142f, E142)):
    print(" ", frame)
    for t in ("fp32.randn", "fp16.randn", "int8.full", "fp32.zeros", "fp16.zeros", "int8.zeros") + tuple(reg["sets"]["k1"]):
        m, _ = S.measured(mine, [t], "D", 2)
        o = theirs["items"].get(t, {}).get("D")
        if t in m and o:
            print(f"    {t}: {m[t]['mean']:.3f} - {o['mean']:.3f} = {m[t]['mean'] - o['mean']:+.3f}")
    for t in ("fp32.randn", "fp16.randn", "int8.full"):
        m, _ = S.measured(mine, [t], "S", 2)
        o = theirs["items"].get(t, {}).get("S")
        if t in m and o:
            print(f"    S {t}: {m[t]['mean']:.3f} - {o['mean']:.3f} = {m[t]['mean'] - o['mean']:+.3f}")
    print(f"    idle level: {mine.get('idle_level')} vs {theirs.get('idle_level')}")
# (c)
pw = sc["primary"]["power_rows"]
cases = {}
for t, r in pw["M8"].items():
    if r["pool_anchor"] or r["error"] is None:
        continue
    c = r["case"].split(" ")[0]
    cases.setdefault(c, []).append(t)
print("\n(c) by case, non-anchor tiles, rms (bias) of measured - model, W")
for c, ts in sorted(cases.items()):
    s = []
    for m in ("M8", "M7", "M6"):
        e = [pw[m][t]["error"] for t in ts]
        s.append(f"{m} {rms(e):.3f} ({sum(e) / len(e):+.3f})")
    print(f"  {c} ({len(ts)}): " + "; ".join(s) + "  | " + ", ".join(f"{t} {pw['M8'][t]['error']:+.2f}" for t in sorted(ts)))
# (d)
print("\n(d) the 44 non-anchor tiles by format, rms (bias), W")
for f in ("fp32", "fp16", "int8"):
    ts = [t for t, r in pw["M8"].items() if not r["pool_anchor"] and r["type"] == f]
    s = []
    for m in ("M8", "M7", "M6"):
        e = [pw[m][t]["error"] for t in ts]
        s.append(f"{m} {rms(e):.3f} ({sum(e) / len(e):+.3f})")
    print(f"  {f} ({len(ts)}): " + "; ".join(s))
