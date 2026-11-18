#!/usr/bin/env python3
"""v31-trace (Q217): the walk's level model (minion_levels: the desk L2 model, the active shires' strict LRU L3 at 32 MB; no fitted constant)
for every traced working hart of the planned runs: per hart the counts of the (A level, B level) op classes, and the run's totals. These are
the model's levels for exactly the address streams the traces confirmed; no simulator can check the levels themselves. Desk.

    python3 -I -B levels_runs_v31.py --plan ../traces/plan.json --runs t1-...,t2-... --out levels_runs_v31.json
"""
import argparse
import collections
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walk_v31 as W  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    plan = {r["name"]: r for r in json.load(open(a.plan))["runs"]}
    out = {"what": "the walk's levels (model, strict LRU 32 MB L3 + the lab's desk L2) for the traced working harts", "python": sys.version.split()[0],
           "runs": {}}
    for name in a.runs.split(","):
        r = plan[name]
        MB, NB, KB = W.parse_shape(r["shape"])
        sh = set(W.mask_shires(r["mask"]))
        cache = {}
        tot = collections.Counter()
        harts = {}
        for sel in r["log_sel"]:
            s, m = sel.split(",")
            s, m = int(s), int(m, 16)
            if s not in sh:
                continue
            for t in range(0, 64, 2):
                if not (m >> t) & 1:
                    continue
                mn = t // 2
                lv = W.minion_levels(r["kernel"], MB, NB, KB, r["mask"], s, mn, _cache=cache)
                c = collections.Counter("%s/%s" % (x[1], x[5]) for x in lv)
                tot.update(c)
                harts[str(64 * s + t)] = {"coords": W.coords(s, mn), "classes_A_B": dict(c),
                                          "first_8_ops": [x[:9] for x in lv[:8]]}
        n = sum(tot.values())
        out["runs"][name] = {"kernel": r["kernel"], "shape": r["shape"], "mask": r["mask"], "traced_working_harts": len(harts),
                             "classes_A_B_share": {k: round(v / n, 6) for k, v in sorted(tot.items())}, "harts": harts}
        print(name, {k: round(v / n, 4) for k, v in sorted(tot.items())}, flush=True)
    json.dump(out, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
