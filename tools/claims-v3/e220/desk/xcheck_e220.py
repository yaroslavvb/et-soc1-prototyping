#!/usr/bin/env python3
"""E220 (Q233) desk: MM1-v3.2's arm A forecasts of family X against its frozen E218 forecasts of the same configurations (aifoundry3 card 0, both at
600 MHz): its time has no per-card term, so the time quantities must agree (to the 12-digit rounding of forecast-e220.json); its energy carries the
per-card terms, so W over idle differs by card (the ratio is printed). Standard library only.

    python3 -I -B tools/claims-v3/e220/desk/xcheck_e220.py     writes desk/xcheck-e220.json (exit 0 = the time agrees to 1e-9)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E218_FC = ("tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json", "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209")


def main():
    p = os.path.join(REPO, E218_FC[0])
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != E218_FC[1]:
        print("xcheck_e220: REFUSED, E218's frozen forecasts changed")
        sys.exit(4)
    L = json.load(open(p))["forecasts"]
    F = json.load(open(os.path.join(HERE, "..", "forecast-e220.json")))
    P = json.load(open(os.path.join(HERE, "..", "points-e220.json")))
    worst, ratio = {}, []
    n = 0
    for q in P["points"]["A"]:
        if q["family"] != "X":
            continue
        a = F["arms"]["A"]["points"][q["id"]]["clocks"]["600.0"]["MM1-v3.2"]
        b = L[q["e218_id"]]["MM1-v3.2"]
        for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "T_op_us"):
            worst[k] = max(worst.get(k, 0.0), abs(a[k] / b[k] - 1.0))
        ratio.append(a["W_over_idle"] / b["W_over_idle"])
        n += 1
    ok = n == 52 and all(v < 1e-9 for v in worst.values())
    rec = {"what": "MM1-v3.2's arm A X forecasts (aifoundry1 card 1, 600 MHz) against its frozen E218 forecasts (aifoundry3 card 0, 600 MHz)",
           "n_twins": n, "worst_relative_difference_time": worst, "W_over_idle_ratio_card1_over_a3": {"min": min(ratio), "max": max(ratio)},
           "verdict": "SAME TIME" if ok else "DIFFER"}
    json.dump(rec, open(os.path.join(HERE, "xcheck-e220.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(rec))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
