#!/usr/bin/env python3
"""E129 amendment A1, part 2 (E129.md § Amendments): R1p, R1 pooled with E124 on the same card. R1's statistic G_op and its line G/2, each computed per
pass by score_e129.per_pass_stats (E109's formulas), over E124's four kept passes (its committed primary reduction) and the kept passes of the E129
reduction that carries E129's verdicts (score_e129.choose), each pass one unit; mean and 95% interval with t at n - 1; the line at the pooled passes'
mean G over 2. PASS if the lower bound >= the line, FAIL if the upper bound < it, else INCONCLUSIVE; NOT-SCORED with fewer than 6 pooled passes.

    python3 tools/claims-v3/e129/pool_r1_e129.py --primary e129.json --relaxed e129-relaxed.json --out r1p.json

Registered by amendment A1 after E124's data were published (its G_op, +0.060 +- 0.370 W, was known) and before any E129 power data were read.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e129 as sc  # noqa: E402

E124 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e124-int8-zeros-replicate/e124.json")
MIN_POOLED = 6


def rows(d, tag):
    st = sc.per_pass_stats(d)
    out = []
    for p in [str(x) for x in d["passes"]]:
        g = (st.get(p) or {}).get("gap")
        if g is not None:
            out.append({"session": tag, "pass": p, "G": g["G"], "G_op": g["G_op"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--relaxed")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e129.json"))
    a = ap.parse_args()
    P = json.load(open(a.pred))
    which, d = sc.choose(json.load(open(a.primary)), json.load(open(a.relaxed)) if a.relaxed else None, P)
    R = rows(json.load(open(E124)), "E124") + rows(d, "E129")
    gop = sc.ci([r["G_op"] for r in R])
    G = sc.ci([r["G"] for r in R])
    line = None if G["mean"] is None else G["mean"] / 2
    n = len(R)
    v = f"NOT-SCORED (fewer than {MIN_POOLED} pooled passes)" if n < MIN_POOLED or line is None else sc.above(gop, line)
    out = {"rule": "R1p (E129 amendment A1): R1 pooled with E124 on aifoundry1 card 1", "e129_reduction": which, "passes": R, "n": n,
           "G_op": gop, "G": G, "line_w": line, "verdict": v,
           "by_session": {s: {"G_op": sc.ci([r["G_op"] for r in R if r["session"] == s]), "G": sc.ci([r["G"] for r in R if r["session"] == s])}
                          for s in ("E124", "E129")},
           "label": "pooled with E124 (two sessions, one card; registered by amendment A1 after E124's data were published and before E129's power data "
                    "were read)"}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({"n": n, "G_op": [gop.get("mean"), gop.get("half")], "line_w": line, "verdict": v}))


if __name__ == "__main__":
    main()
