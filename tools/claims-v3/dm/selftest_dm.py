#!/usr/bin/env python3
"""E99: a pipeline test of reduce_dm.py, before any E99 pass exists. E81's committed passes are relabelled onto E99's item
names, so the numbers mean nothing as E99 results, but the reducer must return exactly what E81's reducer returned for the same
runs: its contrast tie_total on the relabelled passes equals E81's pattern_total pass by pass.

    python3 tools/claims-v3/dm/selftest_dm.py <E81 data dir> <gen dir> <scratch dir>
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {"dp_s1": "dm_u4", "dp_c4": "dm_l08", "dp_s2": "dm_a35", "dp_s4": "dm_a08", "dp_c2r": "dm_L2", "dp_random": "dm_L8192",
       "dp_s2r": "dm_L8"}


def main():
    e81, gen, work = sys.argv[1:4]
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    dirs = []
    for p in ("p8111", "p8112", "p8113", "p8114"):
        s, d = os.path.join(e81, "passes", p), os.path.join(work, p)
        shutil.copytree(s, d)
        for fn in ("runs.jsonl", "marks.jsonl"):
            t = open(os.path.join(d, fn)).read()
            for a, b in MAP.items():
                t = t.replace('"item": "%s"' % a, '"item": "%s"' % b)
            open(os.path.join(d, fn), "w").write(t)
        dirs.append(d)
    out = os.path.join(work, "dm.json")
    subprocess.run([sys.executable, os.path.join(HERE, "reduce_dm.py")] + dirs + ["--gen", gen, "--pred", os.path.join(HERE, "predictions.json"),
                    "--out", out, "--warmup", "8110", "--csv", os.path.join(work, "runs.csv")], check=True)
    r = json.load(open(out))
    e = json.load(open(os.path.join(e81, "dp.json")))
    bad = 0
    # the auto leakage slope is fitted over the runs given, so compare on the raw-power contrasts through a fixed slope
    for p in ("8111", "8112", "8113", "8114"):
        mine = r["per_pass"][p]["contrasts_W"]["tie_total"]
        theirs = e["per_pass"][p]["items_W"]["dp_bern"] - e["per_pass"][p]["items_W"]["dp_c2"]
        ok = abs(mine - theirs) < 0.02
        print("%s pass %s tie_total %+.4f W, E81's dp_bern - dp_c2 %+.4f W" % ("ok " if ok else "BAD", p, mine, theirs))
        bad += 0 if ok else 1
    c = r["headline"]["contrasts_W"]
    for cn, a_, b_ in (("hi_t0", "dm_u4", "dm_l08"), ("hi_ta", "dm_a35", "dm_a08"), ("D", "dm_L8192", "dm_L2")):
        v = [r["per_pass"][p]["items_W"][a_] - r["per_pass"][p]["items_W"][b_] for p in ("8111", "8112", "8113", "8114")]
        ok = abs(sum(v) / 4 - c[cn]["mean"]) < 1e-9
        print("%s %s = the mean of its per-pass differences (%+.4f W)" % ("ok " if ok else "BAD", cn, c[cn]["mean"]))
        bad += 0 if ok else 1
    print("verdict keys:", sorted(r["verdicts"]))
    print("selftest: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
