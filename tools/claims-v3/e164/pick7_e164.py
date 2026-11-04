#!/usr/bin/env python3
"""Q141(b), E164: the 8 pool-6 tiles E164 re-runs on aifoundry1 card 1 for the Q139 critic's rank 7 (card 1's day-to-day
repeatability), picked mechanically from committed data before any E164 data exists. Standard library only.

    python3 -B tools/claims-v3/e164/pick7_e164.py [--json <out>]

Rule (written before any E164 launch, in Q139(k)'s pick6.py form): blind pool 6's non-anchor tiles measured in both E153's
(aifoundry3) and E157's (aifoundry1 card 1) registered primary reductions, with D at or above E157's X1 / X2 floors on both
cards (5 W for fp32 and fp16, 1 W for int8: the anchor scale of rank 7 is a ratio, so it must have watts to act on); per
format the tiles whose D was measured most tightly on both cards, smallest sqrt(ci95_E153^2 + ci95_E157^2) of the
reductions' own items.<tile>.D.ci95, ties by name: 2 fp32, 2 fp16 and 4 int8 (the critic's "4 int8, 4 float").
Sources: docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json and 2026-11-03-e157-blind6-card1/e157.json
(items.<tile>.D {mean, se, n, ci95}); tools/claims-v3/kinds/blind6/blind6.json. It also prints, per pick, the half-width
a same-card repeat with E157's own se and passes would get (pick6.welch), and the pool-6 random anchors' E157 readings
the per-session scale uses.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
E153 = "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json"
E157 = "docs/reports/data/2026-11-03-e157-blind6-card1/e157.json"
POOL = "tools/claims-v3/kinds/blind6/blind6.json"
PICK6 = "tools/claims-v3/ccheck/pick6.py"
COUNT = {"fp32": 2, "fp16": 2, "int8": 4}
FLOOR = {"fp32": 5.0, "fp16": 5.0, "int8": 1.0}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def welch():
    spec = importlib.util.spec_from_file_location("pick6", os.path.join(ROOT, PICK6))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.welch


def main():
    w = welch()
    a = json.load(open(os.path.join(ROOT, E153)))["items"]
    b = json.load(open(os.path.join(ROOT, E157)))["items"]
    pool = json.load(open(os.path.join(ROOT, POOL)))["tiles"]
    rows = []
    for t in pool:
        if t.get("anchor"):
            continue
        nm = t["name"]
        if nm not in a or nm not in b:
            continue
        da, db = a[nm]["D"], b[nm]["D"]
        if da["mean"] < FLOOR[t["type"]] or db["mean"] < FLOOR[t["type"]]:
            continue
        rows.append({"tile": nm, "type": t["type"], "case": t["case"], "priority": t["priority"],
                     "file": "tools/claims-v3/kinds/blind6/" + t["file"], "sha256": t["sha256"]["whole"],
                     "E153_D": da["mean"], "E153_ci95": da["ci95"], "E153_se": da["se"], "E153_n": da["n"],
                     "E157_D": db["mean"], "E157_ci95": db["ci95"], "E157_se": db["se"], "E157_n": db["n"],
                     "combined_ci95": math.hypot(da["ci95"], db["ci95"]),
                     "repeat_band_W_E157": w(0, db["se"], db["n"], 0, db["se"], db["n"])["half_width_W"]})
    pick = []
    for typ in ("fp32", "fp16", "int8"):
        pick += sorted((r for r in rows if r["type"] == typ), key=lambda r: (r["combined_ci95"], r["tile"]))[:COUNT[typ]]
    anchors = {}
    for n in ("fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full", "fp32.randn", "fp16.randn", "int8.full"):
        anchors[n] = {"E157_D": b[n]["D"]["mean"], "E157_se": b[n]["D"]["se"], "E157_n": b[n]["D"]["n"],
                      "E153_D": a[n]["D"]["mean"], "E153_se": a[n]["D"]["se"], "E153_n": a[n]["D"]["n"]}
    out = {"_rule": __doc__.split("Rule (", 1)[1].split("Sources:", 1)[0].strip(),
           "sources_sha256": {r: sha(r) for r in (E153, E157, POOL, PICK6)},
           "eligible": len(rows), "pick": pick, "pool6_and_E78_random_anchors_E157": anchors}
    for r in pick:
        print(f"{r['tile']:34s} {r['type']} case {r['case'][:1]} p{r['priority']}  E153 {r['E153_D']:7.3f} +-{r['E153_ci95']:.3f}  "
              f"E157 {r['E157_D']:7.3f} +-{r['E157_ci95']:.3f} (se {r['E157_se']:.4f}, n {r['E157_n']})  combined {r['combined_ci95']:.3f}"
              f"  same-card repeat band {r['repeat_band_W_E157']:.3f} W")
    print(f"eligible tiles: {len(rows)}; picked {len(pick)}")
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
