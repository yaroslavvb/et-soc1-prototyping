#!/usr/bin/env python3
"""Q138(m): self-test of predict_blind5.py on blind pool 4 (the only pool with committed counts), all three cards, written to a
scratch directory given as the argument. Checks that M6 and M5 through predict_blind5.py reproduce Q137(m)'s frozen
predictions-blind4.json (D and its 95% interval, M6's die rise) exactly, and that every card runs. Pool 4 is IN M7's fit, so
M7's numbers here are in sample and are not a test of M7.

    python3 selftest_predict_blind5.py <scratch_dir> > selftest-predict-blind5.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
POOL = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind4")
CNT = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q137m-model", "counts-blind4.json")
out = os.path.abspath(sys.argv[1])
ok = True
for card in ("aifoundry3", "aifoundry1c1", "aifoundry2"):
    r = subprocess.run([sys.executable, os.path.join(HERE, "predict_blind5.py"), POOL, card, "--counts", CNT, "--out", out], capture_output=True, text=True)
    print(f"{card}: exit {r.returncode}, {len(r.stdout.splitlines())} lines")
    ok &= r.returncode == 0
ref = json.load(open(os.path.join(POOL, "predictions-blind4.json")))["tiles"]
got = json.load(open(os.path.join(out, "predictions-aifoundry3.json")))["tiles"]
worst = {"M6_D": 0.0, "M5_D": 0.0, "M6_D95": 0.0, "M5_D95": 0.0, "M6_dT": 0.0, "M6_dT95": 0.0}
for n, v in ref.items():
    g = got[n]
    worst["M6_D"] = max(worst["M6_D"], abs(g["M6"]["D_w"] - v["M6_D_w"]))
    worst["M5_D"] = max(worst["M5_D"], abs(g["M5"]["D_w"] - v["M5_D_w"]))
    worst["M6_D95"] = max(worst["M6_D95"], max(abs(a - b) for a, b in zip(g["M6"]["D_95"], v["M6_D_95"])))
    worst["M5_D95"] = max(worst["M5_D95"], max(abs(a - b) for a, b in zip(g["M5"]["D_95"], v["M5_D_95"])))
    worst["M6_dT"] = max(worst["M6_dT"], abs(g["M6"]["dT_win_c"] - v["M6_dT_win_c"]))
    worst["M6_dT95"] = max(worst["M6_dT95"], max(abs(a - b) for a, b in zip(g["M6"]["dT_win_95"], v["M6_dT_win_95"])))
print("largest |predict_blind5 - predictions-blind4.json| over the 25 tiles (rounding is 1e-4 W, 1e-3 C):", {k: round(x, 5) for k, x in worst.items()})
ok &= all(x <= 2e-3 for x in worst.values())
print("SELFTEST", "PASS" if ok else "FAIL")
