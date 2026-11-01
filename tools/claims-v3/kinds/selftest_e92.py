#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E92 self-test: E92's reduction on SYNTHETIC passes with known answers, before any card data exist.

    /usr/bin/python3 tools/claims-v3/kinds/selftest_e92.py <scratch dir> [--passes 3] [--seed 1]

It writes fake passes with E78's own generator (selftest_e78.make_pass: the layout run_e78.py writes, 10 Hz telemetry,
heaters, the quiet rule, integer die readings, a lagging rail, a drifting idle) after installing E92's items and
order, so every pass is E92's registered 54-run order, with every E92 tile at its frozen prediction (predictions-e92.json
`tiles.*.D_pred_w`) and every E78 kind at E78's measured D. Then it runs reduce_e92.py (E78's reduction, unchanged) and checks what it recovers. NOTHING HERE
IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e92_common as e92  # noqa: E402
e92.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e92.json")))
    e78 = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e78_reduction"]["path"])))
    D = {n: v["D"]["mean"] for n, v in e78["items"].items()}
    for n, t in reg["tiles"].items():
        D[n] = t["D_pred_w"] if t.get("D_pred_w") is not None else t["q130n_predictor"]["point_w"]
    rng = np.random.default_rng(a.seed)
    items = ec.load_items()
    base = os.path.join(a.scratch, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    for i in range(a.passes):
        p = e92.FIRST_PASS + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        dirs.append(d)
    j = os.path.join(a.scratch, "e92.json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e92.py"), *dirs, "--out", j, "--no-refit",
                        "--txt", os.path.join(a.scratch, "reduce.txt")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit("reduce_e92.py failed")
    e = json.load(open(j))
    names = list(reg["tiles"]) + [n for n in reg["e78_reference"] if n in e["items"]]
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    checks = {
        "passes kept": (len(e["passes"]) == a.passes, len(e["passes"])),
        "runs kept, all": (e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "54 runs a pass": (e["runs"] == 54 * a.passes, e["runs"]),
        "D recovered within 0.15 W (E92 tiles and references)": (worst <= 0.15, round(worst, 4)),
        "every dumped tile passes the sha256 gate": (not any("tile dump" in " ".join(f[3]) for f in e["failed"]),
                                                     len(e["failed"])),
        "experiment is E92": (e.get("experiment") == "E92", e.get("experiment")),
    }
    ok = all(v[0] for v in checks.values())
    for k, (good, val) in checks.items():
        print(f"{'ok  ' if good else 'FAIL'} {k}: {val}")
    print("SELFTEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
