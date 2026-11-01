#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E101 self-test: E101's reduction and scorer on SYNTHETIC passes with known answers, before any card data exist.

    /usr/bin/python3 tools/claims-v3/kinds/selftest_e101.py <scratch dir> [--passes 3] [--seed 1]

It writes fake passes with E78's own generator (selftest_e78.make_pass: the layout run_e78.py writes, 10 Hz telemetry, heaters, the quiet rule, integer die readings, a lagging rail, a drifting idle)
after installing E101's items and order, so every pass is E101's registered 78-run order, with every E101 cell at its frozen S and every E78 kind at E78's measured S. Then it runs reduce_e101.py and
score_e101.py and checks what they recover. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
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
import e101_common as e101  # noqa: E402
e101.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e101.json")))
    e78 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")))
    D = {}
    for n, v in e78["items"].items():
        D[n] = v["S"]["mean"] - st.ZERO_LEVEL[v["type"]]
    for n, c in reg["cells"].items():
        D[n] = c["S_w"] - st.ZERO_LEVEL[c["type"]]
    for t in ec.TYPES[:3]:
        for k in ("e37", "real"):
            D[f"res.{t}.{k}"] = reg["S_res"][t][k][0] - st.ZERO_LEVEL[t]
    for t in ec.TYPES[:3]:     # the cells with no frozen point
        D[f"gemm16.{t}.zeros"] = 4.0 - st.ZERO_LEVEL[t]
        D[f"gemm16.{t}.{e101.RANDOM_KIND[t]}"] = 14.0 - st.ZERO_LEVEL[t]
    D["mmp64.fp32.zeros"] = 6.0 - st.ZERO_LEVEL["fp32"]
    D["mmp64.fp32.randn"] = 6.0 + reg["dram"]["random_minus_zeros_w"] - st.ZERO_LEVEL["fp32"]
    D[ec.TIE] = e78["items"]["fp32.pi"]["S"]["mean"] - st.ZERO_LEVEL["fp32"]
    rng = np.random.default_rng(a.seed)
    items = ec.load_items()
    base = os.path.join(a.scratch, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    for i in range(a.passes):
        p = e101.FIRST_PASS + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        dirs.append(d)
    j = os.path.join(a.scratch, "e101.json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e101.py"), *dirs, "--out", j, "--no-refit", "--txt", os.path.join(a.scratch, "reduce.txt")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit("reduce_e101.py failed")
    e = json.load(open(j))
    want = {n: D[n] + st.ZERO_LEVEL[next(it["type"] for it in items if it["name"] == n)] for n in e["items"] if n in D}
    worst = max(abs(e["items"][n]["S"]["mean"] - want[n]) for n in want)
    worst_item = max(want, key=lambda n: abs(e["items"][n]["S"]["mean"] - want[n]))
    sc = os.path.join(a.scratch, "scored.json")
    r = subprocess.run([sys.executable, os.path.join(HERE, "score_e101.py"), "--e101", j, "--raw", *dirs, "--json", sc, "--md", os.path.join(a.scratch, "results.md")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit("score_e101.py failed")
    s = json.load(open(sc))
    v = s["verdicts"]
    checks = {
        "passes kept": (len(e["passes"]) == a.passes, len(e["passes"])),
        "runs kept, all": (e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "78 runs a pass": (e["runs"] == 78 * a.passes, e["runs"]),
        "S recovered within 0.25 W, every cell": (worst <= 0.25, (worst_item, round(worst, 4))),
        "every dumped tile passes the sha256 gate": (not any("tile dump" in " ".join(f[3]) for f in e["failed"]), len(e["failed"])),
        "experiment is E101": (e.get("experiment") == "E101", e.get("experiment")),
        "at the frozen S the model's rms is near 0": (s["rules"]["R3b_model"]["rms_w"]["mm16"] <= 0.3, s["rules"]["R3b_model"]["rms_w"]),
        "R1 passes at the frozen tie": (v["R1_tie_e37"] in ("PASS", "FAIL") and all(x["watts_ok"] for x in s["rules"]["R1_tie_e37"]["cells"].values()), v["R1_tie_e37"]),
        "R2 passes at E78's values": (v["R2_tie_e78"] == "PASS", v["R2_tie_e78"]),
        "R5 passes at the frozen prices": (v["R5_memory_data"] == "PASS", v["R5_memory_data"]),
        "R5b passes at frozen constants": (v["R5b_memory_constant"] in ("PASS", "INCONCLUSIVE"), v["R5b_memory_constant"]),
        "R6 passes": (v["R6_rank"] == "PASS", v["R6_rank"]),
        "R8 passes at the frozen order": (v["R8_coop"] == "PASS", v["R8_coop"]),
        "R11 passes at the frozen difference": (v["R11_dram"] in ("PASS",), v["R11_dram"]),
        "R12 passes": (v["R12_gemm16"] == "PASS", v["R12_gemm16"]),
        "R9 reports no check records": (v["R9_correct"] == "NOT SCORED", v["R9_correct"]),
    }
    ok = all(c[0] for c in checks.values())
    for k, (good, val) in checks.items():
        print(f"{'ok  ' if good else 'FAIL'} {k}: {val}")
    print("verdicts", json.dumps(v))
    print("SELFTEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
