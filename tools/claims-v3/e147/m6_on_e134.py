#!/usr/bin/env python3
"""E147 (Q138): M6 on E134's single bits, post hoc - the "before" for M1. Standard library only; committed files only.

    python3 tools/claims-v3/e147/predict_m6_e147.py --tiles tools/claims-v3/e134/e134/e134-tiles.json \
        --tile-dir tools/claims-v3/e134/e134 --counts docs/reports/data/2026-11-02-e134-bit-prices-more/bench/counts-e134.json \
        --out docs/reports/data/2026-11-02-e147-bit-prices-rest/bench/m6-e134-posthoc.json
    python3 tools/claims-v3/e147/m6_on_e134.py > docs/reports/data/2026-11-02-e147-bit-prices-rest/bench/m6-e134-posthoc.txt

M6 (Q137(m), frozen 15:56 PST on 2 Nov 2026) was fitted after E134's data was public (12:32 PST), but its fit left out
E134's rows (Q137(m) README, "How it was done"): so its error on E134's steps is out of its sample, though not blind.
It is printed beside M5's and the bench's (E134's own frozen model, E92's coefficients) over E134's 54 items, board W,
E134's primary (scored.json > primary > prices).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
M = os.path.join(ROOT, "docs/reports/data/2026-11-02-e147-bit-prices-rest/bench/m6-e134-posthoc.json")
SC = os.path.join(ROOT, "docs/reports/data/2026-11-02-e134-bit-prices-more/scored.json")
PR = os.path.join(ROOT, "tools/claims-v3/e134/predictions-e134.json")


def main():
    m = json.load(open(M))["items"]
    sc = json.load(open(SC))["primary"]["prices"]
    pr = json.load(open(PR))["items"]
    groups = {"A all-in": ("aj_", "a67j_"), "A balanced": ("ap_", "a67p_"), "B all-in": ("bj_",), "B balanced": ("bp_",),
              "all": None}
    print("M6 on E134's single-bit steps, post hoc (board W, E134's primary): measured minus model")
    for g, pre in groups.items():
        d = {"M6": [], "M5": [], "bench": []}
        for n, it in m.items():
            k = n[5:]
            if (pre and not k.startswith(pre)) or k not in sc or sc[k]["W"]["mean"] is None:
                continue
            y = sc[k]["W"]["mean"]
            d["M6"].append(y - it["M6_step_w"])
            d["M5"].append(y - it["M5_step_w"])
            d["bench"].append(y - pr[n]["pred_W"]["bench"])
        row = []
        for lab, v in d.items():
            rms = math.sqrt(sum(x * x for x in v) / len(v))
            row.append(f"{lab} rms {rms:.3f} bias {sum(v) / len(v):+.3f}")
        print(f"  {g:11s} n={len(d['M6']):2d}: " + "; ".join(row))
    print("per item: measured W, M6 W, M6 fJ a flip, measured fJ a flip")
    for n, it in sorted(m.items()):
        k = n[5:]
        if k in sc and sc[k]["W"]["mean"] is not None:
            print(f"  {k:8s} {sc[k]['W']['mean']:+.3f} {it['M6_step_w']:+.3f} {it['M6_fJ_per_flip']:7.1f} {sc[k]['fJ']['mean']:7.1f}")


if __name__ == "__main__":
    main()
