#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E86 self-test: E86's reduction and scoring run on SYNTHETIC passes with known answers, before any card data exist.

    python3 tools/claims-v3/kinds/selftest_e86.py <scratch dir> [--passes 6] [--seed 1]

It writes fake passes with E78's own generator (selftest_e78.make_pass: the exact layout run_e78.py writes, 10 Hz
telemetry, heaters, the quiet rule, integer die readings, a lagging rail, a drifting idle) after installing E86's
items and order, so every pass is E86's registered 32-run order. Two worlds:
  (a) "frozen": every real tile at Q130(n)'s frozen point, every E78 kind at E78's measured D;
  (b) "wrong":  real fp32 and fp16 tiles at 1.015 x their randn and real int8 at 0.95 x int8 full, so E86-R3 must
      FAIL in every format, while E86-R1 still finds them inside (the intervals are wide).
Then it runs reduce_e86.py (E78's reduction, unchanged) and score_e86.py on each and checks what they recover.
NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
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
import e86_common as e86  # noqa: E402

e86.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e86.json")))
    e78 = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e78_reduction"]["path"])))
    D = {n: v["D"]["mean"] for n, v in e78["items"].items()}
    for n, t in reg["tiles"].items():
        if world == "frozen":
            D[n] = t["D_frozen_w"]
        else:
            ref = D[t["ref"]]
            D[n] = ref * (1.015 if t["type"] in ("fp32", "fp16") else 0.95)
    return D, reg


def run_world(scratch, world, passes, seed):
    rng = np.random.default_rng(seed)
    items = ec.load_items()
    D, reg = truth(world)
    base = os.path.join(scratch, world, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    for i in range(passes):
        p = e86.FIRST_PASS + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        dirs.append(d)
    py = sys.executable
    j = os.path.join(scratch, f"{world}-e86.json")
    r = subprocess.run([py, os.path.join(HERE, "reduce_e86.py"), *dirs, "--out", j, "--no-refit",
                        "--txt", os.path.join(scratch, f"{world}-reduce.txt")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit(f"reduce_e86.py failed ({world})")
    s = os.path.join(scratch, f"{world}-scored.json")
    r2 = subprocess.run([py, os.path.join(HERE, "score_e86.py"), "--e86", j, "--json", s,
                         "--md", os.path.join(scratch, f"{world}-results.md")], capture_output=True, text=True)
    if r2.returncode:
        print(r2.stdout[-2000:], r2.stderr[-3000:])
        sys.exit(f"score_e86.py failed ({world})")
    return json.load(open(j)), json.load(open(s)), D, reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    e, sc, D, reg = run_world(a.scratch, "frozen", a.passes, a.seed)
    names = list(reg["tiles"]) + list(reg["e78_reference"])
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    R = sc["rules"]
    checks = {
        "frozen: passes_kept": (len(e["passes"]) == a.passes, len(e["passes"])),
        "frozen: runs_kept_all": (e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "frozen: 32 runs a pass": (e["runs"] == 32 * a.passes, e["runs"]),
        "frozen: D recovered within 0.15 W (real tiles and references)": (worst <= 0.15, round(worst, 4)),
        "frozen: every dumped tile passes the sha256 gate": (not any("tile dump" in " ".join(f[3]) for f in e["failed"]),
                                                             len(e["failed"])),
        "frozen: R1 PASS, 9 of 9 inside": (R["E86-R1"]["verdict"] == "PASS" and R["E86-R1"]["inside"] == 9,
                                           R["E86-R1"]["inside"]),
        "frozen: R2 PASS": (R["E86-R2"]["verdict"] == "PASS", R["E86-R2"]["verdict"]),
        "frozen: R3 PASS (rho below 1 / 1 / 0.9)": (R["E86-R3"]["verdict"] == "PASS",
                                                    {t: round(v["rho"]["mean"], 4) for t, v in R["E86-R3"]["by_type"].items()}),
        "frozen: R4 PASS": (R["E86-R4"]["verdict"] == "PASS", R["E86-R4"]["verdict"]),
        "frozen: R5 PASS": (R["E86-R5"]["verdict"] == "PASS", R["E86-R5"]["verdict"]),
        "frozen: S1 PASS": (R["E86-S1"]["verdict"] == "PASS", R["E86-S1"]["inside"]),
        "frozen: tie dump equals fp32.pi": (all(e["checks"]["tie_dump_equals_fp32_pi_tile"].values()), None),
    }
    e2, sc2, D2, _ = run_world(a.scratch, "wrong", a.passes, a.seed + 1)
    R2 = sc2["rules"]
    checks.update({
        "wrong: R3 FAIL in every format": (all(v["verdict"] == "FAIL" for v in R2["E86-R3"]["by_type"].values()),
                                           {t: (round(v["rho"]["mean"], 4), v["verdict"]) for t, v in R2["E86-R3"]["by_type"].items()}),
        "wrong: R1 still PASS (wide intervals)": (R2["E86-R1"]["verdict"] == "PASS", R2["E86-R1"]["inside"]),
        "wrong: real fp32 tiles read above randn per tile": (all(R2["E86-R3"]["by_type"]["fp32"]["per_tile"][n] == "FAIL"
                                                                for n in R2["E86-R3"]["by_type"]["fp32"]["per_tile"]), None),
    })
    ok_all = True
    for k, (ok, v) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {v}")
    print("tallies on synthetic data (meaningless as a result):", sc["tally"], sc2["tally"])
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
