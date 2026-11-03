#!/usr/bin/env python3
"""Q139(c): the committed numbers behind the corrections of Q138's final critic's minor and moderate faults that checks (a)-(c)
do not compute (desk only, Tue 3 Nov 2026; nothing here is new data, every value is read from a committed file and printed).

  fault 2  E141 corrections-numbers.txt C1: B1 at M7's training footings, the meter's dips kept and removed
  fault 4  E141 / E142 scored.json heat_rows (M7, priority-1 tiles): the spread of the measured 4.5 s rises per format (the rms
           error a constant per format would make) against M7's rms
  fault 6  E146 results.json rules.R5: the burst-power rule on PS and the time-per-op point rule on the fresh shape F6
  fault 7  Q138(m) posthoc-m7.json aifoundry2_split: M7's end-to-end score on the bursts the governor acts on (its C1)
  fault 9  E141 / E142 raw launches: the result field of every fma launch on pool 5's file tiles
Standard library only.  Usage: python3 fault_support.py [--txt out.txt]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")


def walk_results(path, counts):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="replace") as f:
        for ln in f:
            if '"result"' not in ln or not ln.startswith("{"):
                continue
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            for k in d.get("sparsity", []) if isinstance(d.get("sparsity"), list) else [d]:
                if isinstance(k, dict) and k.get("test") == "fma" and "result" in k:
                    counts[k["result"]] = counts.get(k["result"], 0) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--txt")
    a = ap.parse_args()
    L = []
    pr = L.append
    pr("Q139(c): the committed numbers behind the corrections (read, not computed anew)")
    c1 = open(os.path.join(DATA, "2026-11-02-e141-blind5-aifoundry3", "corrections-numbers.txt")).read().splitlines()
    pr("")
    pr("fault 2: E141 corrections-numbers.txt C1 (B1 is the floats' bias, measured - predicted; its line -0.117 W):")
    for ln in c1:
        if "post hoc" in ln and ("dips kept" in ln or "dips removed" in ln) and "leak 0.2" in ln:
            pr("  " + ln.strip())
    pr("")
    pr("fault 4: the measured 4.5 s rise per format against M7's heat rms (priority-1 tiles; spread = rms about the mean, "
       "the error of a constant per format):")
    for nm, d in (("aifoundry3 (E141)", "2026-11-02-e141-blind5-aifoundry3"), ("card 1 (E142)", "2026-11-02-e142-blind5-card1")):
        hr = json.load(open(os.path.join(DATA, d, "scored.json")))["primary"]["heat_rows"]["M7"]
        for f in ("fp32", "fp16", "int8"):
            rows = [v for v in hr.values() if v.get("type") == f and v.get("priority") == 1 and v.get("measured") is not None]
            m = [v["measured"] for v in rows]
            e = [v["error"] for v in rows if v.get("error") is not None]
            mu = sum(m) / len(m)
            pr(f"  {nm:18s} {f}: n {len(m)}  rises {min(m):.3f}-{max(m):.3f} C ({len(set(round(x, 3) for x in m))} distinct)  "
               f"constant {math.sqrt(sum((x - mu) ** 2 for x in m) / len(m)):.3f} C  M7 {math.sqrt(sum(x * x for x in e) / len(e)):.3f} C")
    r5 = json.load(open(os.path.join(DATA, "2026-11-02-e146-gemm-stores", "results.json")))["rules"]["R5"]
    pr("")
    pr("fault 6: E146 results.json rules.R5 on the fresh shape F6:")
    for f, v in r5["T"].items():
        pr(f"  time per op {f}: T800 {v['T800']} us, MS {v['MS']['pred']} ({100 * v['MS']['rel']:+.2f}%), point {v['point']}")
    for c, v in sorted(r5["power"].items()):
        pr(f"  burst power {c}: measured {v['p800_w']} W, PS {v['PS_w']} W, P0 {v['P0_w']} W, err on PS {v['err_S']:+.2f} W {v['verdict']}")
    for c, v in r5["sus"].items():
        pr(f"  sustained {c}: {v['sus_mhz']} MHz (G2 {v['pred_mhz_G2']}, {v['clock']}), {v['sus_w']} W (G2 {v['pred_w_G2']}, "
           f"{v['power']}), die {v['sus_die']} (law on G2's W {v['pred_die']}, {v['die']})")
    sp = json.load(open(os.path.join(DATA, "2026-11-02-q138m-model", "posthoc-m7.json")))["aifoundry2_split"]["frozen_cap"]
    pr("")
    pr("fault 7: Q138(m) posthoc-m7.json aifoundry2_split.frozen_cap (M7 end to end from the tile's bytes, its C1):")
    for k in ("all", "governed"):
        v = sp[k]
        pr(f"  {k}: n {v['n']}  clock {v['rms_mhz']:.2f} MHz rms  board {v['rms_board_w']:.3f} W rms")
    pr("")
    pr("fault 9: the result field of every fma launch in pool 5's sessions (sparsity_host --values file:):")
    for nm, d in (("E141 aifoundry3", "2026-11-02-e141-blind5-aifoundry3"), ("E142 card 1", "2026-11-02-e142-blind5-card1"),
                  ("E143 aifoundry2", "2026-11-02-e143-blind5-aifoundry2")):
        counts = {}
        for dp, _, fs in os.walk(os.path.join(DATA, d)):
            for fn in fs:
                if fn.startswith(("launches", "runs")) and (fn.endswith(".jsonl") or fn.endswith(".jsonl.gz")):
                    walk_results(os.path.join(dp, fn), counts)
        pr(f"  {nm}: {counts}")
    txt = "\n".join(L) + "\n"
    if a.txt:
        open(a.txt, "w").write(txt)
    sys.stdout.write(txt)


if __name__ == "__main__":
    main()
