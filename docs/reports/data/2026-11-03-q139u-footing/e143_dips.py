#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u) F4, post hoc: E143's registered reduction (tools/claims-v3/e143/reduce_e143.py, unchanged) re-run on a copy of the
session directory whose sampler traces (tel/*.jsonl.gz) have E82 A2's dips removed, beside the committed results.json.

    python3 e143_dips.py <scratch dir>      (writes e143-nodips.json here: both runs' rules and reported sets side by side)
"""
import gzip
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
D = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e143-blind5-aifoundry2")
sys.path.insert(0, HERE)
import reduce_footing as RF  # noqa: E402


def main():
    scratch = os.path.abspath(sys.argv[1])
    src = os.path.join(D, "aifoundry2", "s1")
    dst = os.path.join(scratch, "e143-nodips", "s1")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    dropped = {}
    for f in sorted(os.listdir(os.path.join(dst, "tel"))):
        p = os.path.join(dst, "tel", f)
        op = gzip.open if f.endswith(".gz") else open
        lines = [ln for ln in op(p, "rt") if ln.startswith("{")]
        recs = []
        for ln in lines:
            try:
                recs.append(json.loads(ln))
            except ValueError:
                recs.append({})
        _, bad = RF.drop_dips(recs)
        if bad:
            dropped[f] = len(bad)
        bad = set(bad)
        with op(p, "wt") as g:
            for i, ln in enumerate(lines):
                if i not in bad:
                    g.write(ln if ln.endswith("\n") else ln + "\n")
    out = os.path.join(scratch, "e143-nodips", "results-nodips.json")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "claims-v3", "e143", "reduce_e143.py"), dst, "--out", out],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    old = json.load(open(os.path.join(D, "results.json")))
    new = json.load(open(out))
    keep = ("verdict", "rms", "mean_err", "n", "inside", "share", "range_2.5_97.5")
    rules = {k: {"committed": {x: v.get(x) for x in keep if x in v},
                 "a2_removed": {x: new["score"]["rules"].get(k, {}).get(x) for x in keep if x in new["score"]["rules"].get(k, {})}}
             for k, v in old["score"]["rules"].items() if isinstance(v, dict)}
    cells = {}
    for lab, c in old.get("cells", {}).items():
        n = new.get("cells", {}).get(lab)
        if n and c.get("burst_w") is not None and n.get("burst_w") is not None:
            cells[lab] = {"burst_w": [c["burst_w"], n["burst_w"]], "D_w": [c.get("D_w"), n.get("D_w")],
                          "burst_mhz": [c.get("burst_mhz"), n.get("burst_mhz")]}
    dw = [v["burst_w"][1] - v["burst_w"][0] for v in cells.values()]
    dd = [v["D_w"][1] - v["D_w"][0] for v in cells.values() if None not in v["D_w"]]
    res = {"what": "E143 re-scored with E82 A2's dips removed from its sampler traces (F4); the reduction and rules unchanged",
           "files_with_dips": len(dropped), "samples_dropped": sum(dropped.values()), "rules": rules,
           "cells_changed": {"n": len(cells), "burst_w_shift_mean_w": sum(dw) / len(dw) if dw else None,
                             "burst_w_shift_range_w": [min(dw), max(dw)] if dw else None,
                             "D_shift_mean_w": sum(dd) / len(dd) if dd else None, "D_shift_range_w": [min(dd), max(dd)] if dd else None}}
    json.dump(res, open(os.path.join(HERE, "e143-nodips.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "rules"}))
    for k, v in rules.items():
        print(k, v["committed"].get("verdict"), v["committed"].get("rms"), v["committed"].get("mean_err"), "->",
              v["a2_removed"].get("verdict"), v["a2_removed"].get("rms"), v["a2_removed"].get("mean_err"))


if __name__ == "__main__":
    main()
