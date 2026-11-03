#!/usr/bin/env python3
"""E140's scorer on synthetic sessions (nothing here is a measurement). It builds a registration shaped as
predictions-e140.json (25 tiles of blind pool 4's types and priorities; power and heat predictions with 95% intervals; nested
reference errors), then sessions of 3 kept passes whose per-tile truth is the prediction plus an error drawn from the
reference errors times a factor f, plus pass noise; and counts each rule's verdicts over many sessions.

    python3 tools/claims-v3/e140/selftest_e140.py [--sessions 200] [--reg predictions-e140.json]

With --reg it uses the frozen registration's tiles, intervals and reference errors; without, made-up ones.
f = 1: the model as good as its nested score says (R1/R2 should PASS about 97.5% of the time, R3 PASS);
f = 2 and 3: the model twice / three times worse (R1/R2 should FAIL most of the time).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e140 as S  # noqa: E402
import e140_common as e140  # noqa: E402


def fake_reg(rng):
    ref = {"power": {"fp32": [rng.gauss(0, 0.20) for _ in range(150)], "fp16": [rng.gauss(0, 0.20) for _ in range(60)],
                     "int8": [rng.gauss(0, 0.26) for _ in range(78)]},
           "heat": {"fp32": [rng.gauss(0, 0.30) for _ in range(40)], "fp16": [rng.gauss(0, 0.30) for _ in range(20)],
                    "int8": [rng.gauss(0, 0.20) for _ in range(20)]}}
    tiles = {}
    for n in e140.E140_NAMES:
        ty = n.split(".")[0]
        d = rng.uniform(2, 25) if ty != "int8" else rng.uniform(1, 7)
        hp = 0.45 if ty != "int8" else 0.55
        tiles[n] = {"type": ty, "priority": e140.PRIORITY[n], "case": e140.OPEN_CASE[n],
                    "power": {"pred": d, "lo95": d - hp, "hi95": d + hp},
                    "heat": {"pred": d * 0.08, "lo95": d * 0.08 - 0.6, "hi95": d * 0.08 + 0.6}}
    return tiles, ref


def fam(unit, ref, q):
    return {"unit": unit, "reference_errors": ref,
            "families": {f"E140-{q}1": {"types": ["fp32", "fp16"], "min_tiles": 5},
                         f"E140-{q}2": {"types": ["int8"], "min_tiles": 4}},
            "coverage": {"rule": f"E140-{q}3", "min_tiles": 10}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=200)
    ap.add_argument("--reg")
    a = ap.parse_args()
    rng = random.Random(14099)
    if a.reg:
        reg = json.load(open(a.reg))
        tiles = reg["tiles"]
        ref = {k: reg["model"][k]["reference_errors"] for k in ("power", "heat") if reg["model"].get(k)}
    else:
        tiles, ref = fake_reg(rng)
        reg = {"plan": {"min_kept_passes_scored": 2, "min_tile_passes": 2, "bootstrap": {"draws": 4000, "seed": 14000}},
               "tiles": tiles, "anchors_predicted": None,
               "model": {"power": fam("W", ref["power"], "P"), "heat": fam("C", ref["heat"], "H"),
                         "heat_measure": {"e78_field": "dT_win"}}}
    reg["plan"]["bootstrap"] = {"draws": 4000, "seed": 14000}
    key = reg["model"].get("heat_measure", {}).get("e78_field", "dT_win")
    lines = []
    for f in (1.0, 2.0, 3.0):
        tally = {}
        for s in range(a.sessions):
            truth = {}
            for n, t in tiles.items():
                ty = t["type"]
                truth[n] = {"power": t["power"]["pred"] + f * rng.choice(ref["power"][ty])}
                if "heat" in ref and t.get("heat"):
                    truth[n]["heat"] = t["heat"]["pred"] + f * rng.choice(ref["heat"][ty])
            res = {"passes": [14010, 14011, 14012], "per_pass": {}}
            for p in res["passes"]:
                res["per_pass"][str(p)] = {n: {"D": v["power"] + rng.gauss(0, 0.05),
                                               key: (v.get("heat", 0.0) + rng.gauss(0, 0.05))} for n, v in truth.items()}
            v = S.verdicts(S.score(res, reg))
            for r, x in v.items():
                if "anchor" in r:
                    continue
                tally.setdefault(r, {}).setdefault(x, 0)
                tally[r][x] += 1
        lines.append(f"f = {f}: " + json.dumps({r: tally[r] for r in sorted(tally)}))
    lines.append("no kept pass: " + json.dumps(S.score({"passes": [14010], "per_pass": {}}, reg).get("NOT SCORED")))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
