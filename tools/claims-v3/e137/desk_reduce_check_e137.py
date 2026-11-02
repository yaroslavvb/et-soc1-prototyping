#!/usr/bin/env python3
"""E137 desk check (before the freeze, no card): copy E128's two committed raw passes, keeping only the run records of E137's items (E78's anchors,
the tie, E128's seven fp16 sign tiles and fp16.ones), reduce the copies with reduce_e137.py at the primary's options, and compare every fp16 item's
per-pass D with E128's committed primary reduction (docs/reports/data/2026-11-02-e128-fp16-signs/e128.json). With leakage frozen, a run's D depends on
its own run and its type's zeros line only, so they must agree exactly. Marks (heats, launches) are kept whole: the reduction finds a run's window
from its own record. Standard library + the reducer's numpy.

    /usr/bin/python3 tools/claims-v3/e137/desk_reduce_check_e137.py <scratch dir>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e137_common as e137  # noqa: E402

SRC = os.path.join(ROOT, "docs/reports/data/2026-11-02-e128-fp16-signs")
keep = set(e137.E137_NAMES) | set(e137.COMPARE) | set(e137.ec.ANCHORS) | {e137.ec.TIE}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    dirs = []
    for p in ("p12810", "p12811"):
        s, d = os.path.join(SRC, "aifoundry1-c1/e128", p), os.path.join(out, p)
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)
        rows = [l for l in open(os.path.join(s, "runs.jsonl")) if l.strip() and json.loads(l)["item"] in keep]
        open(os.path.join(d, "runs.jsonl"), "w").writelines(rows)
        dirs.append(d)
    rc = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e137.py"), *dirs, "--leak", "0.2414", "--out", os.path.join(out, "e137.json")],
                        capture_output=True, text=True)
    if rc.returncode:
        print(rc.stdout[-2000:], rc.stderr[-2000:])
        sys.exit(1)
    a = json.load(open(os.path.join(out, "e137.json")))
    b = json.load(open(os.path.join(SRC, "e128.json")))
    n, worst = 0, 0.0
    for p in b["per_pass"]:
        for it in sorted(keep):
            if it.startswith("fp16.") and it in b["per_pass"][p] and it in a["per_pass"].get(p, {}):
                d = abs(a["per_pass"][p][it]["D"] - b["per_pass"][p][it]["D"])
                worst = max(worst, d)
                n += 1
                print(f"{p} {it:14s} E137 reducer {a['per_pass'][p][it]['D']:.6f}  E128 {b['per_pass'][p][it]['D']:.6f}  diff {d:.2e}")
    print(f"DESK-REDUCE-CHECK: {n} fp16 per-pass D values compared, max |diff| {worst:.3e} W; passes kept {a['passes']}; set aside "
          f"{a['passes_set_aside']}")
    sys.exit(0 if n >= 14 and worst < 1e-9 else 1)


if __name__ == "__main__":
    main()
