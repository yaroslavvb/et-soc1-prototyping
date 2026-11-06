#!/usr/bin/env python3
"""The dip term's scorer, v3 (REGISTRATION.md.dated-note-2.md): v2 unchanged, plus one REPORTED arm, "seq-gc". It is the seq arm
with every governed pass's expected clock and board deficits multiplied by the catch-up factor K_GC. A governed pass is a counted
pass of a tile in the run's own governed set (results.json > score.reported.tiles > group or set, as the run's registered rules read
it). Every other pass is the seq arm's, unchanged. The
registered arms and every verdict on them are v2's. dipterm.py is unchanged.

    python3 score_dipterm_v3.py <the same arguments as score_dipterm.py> [--arms none,count,seq,seq-gc]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dipterm as DT  # noqa: E402
import score_dipterm_v2 as V2  # noqa: E402

K_GC = 0.67          # dated note 2: E175's three governed falls, measured cost over the term's (0.749, 0.579, 0.687), post hoc


def score(a):
    arms = a.arms.split(",")
    want_gc = "seq-gc" in arms
    base = [x for x in arms if x != "seq-gc"]
    if want_gc and "seq" not in base:
        base.append("seq")
    a2 = argparse.Namespace(**dict(vars(a), arms=",".join(base)))
    R = json.load(open(a.results))
    tiles = R["score"]["reported"]["tiles"]
    gov = {r["run"] for r in R["run_rows"] if V2.S1.group_of(tiles.get(V2.S1.tile_of(r["label"]), {}) or {"group": "none"}) == "governed"}
    orig = DT.predict
    keep = {}

    def predict(procs, card, f_ref, dP=None, arm="seq", draws=DT.MC_DRAWS, seed=DT.SEED):
        out = orig(procs, card, f_ref, dP, arm, draws, seed)
        if arm == "seq":
            g = copy.deepcopy(out)
            g["arm"] = "seq-gc"
            for p in g["processes"]:
                if p["run"] in gov:
                    p["clock_deficit_mhz"] *= K_GC
                    p["board_deficit_w"] *= K_GC
            keep["seq-gc"] = g
        return out

    DT.predict = predict
    try:
        out = V2.score(a2)
    finally:
        DT.predict = orig
    if want_gc:
        # score the seq-gc arm with v2's own code path: substitute the stored predictions for one more pass
        def predict_gc(procs, card, f_ref, dP=None, arm="seq", draws=DT.MC_DRAWS, seed=DT.SEED):
            return keep["seq-gc"] if arm == "seq" else orig(procs, card, f_ref, dP, arm, draws, seed)
        DT.predict = predict_gc
        try:
            o2 = V2.score(argparse.Namespace(**dict(vars(a), arms="none,seq")))
        finally:
            DT.predict = orig
        res = o2["arms"]["seq"]
        res["label"] = f"seq-gc (dated note 2): REPORTED, never a verdict; governed passes' deficits x {K_GC}"
        out["arms"]["seq-gc"] = res
    out["scorer"] = "score_dipterm_v3.py"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--card", required=True, choices=sorted(DT.PERIOD_PRIOR_MS))
    ap.add_argument("--clock-rule")
    ap.add_argument("--clock-set", default="pinned")
    ap.add_argument("--board-rule")
    ap.add_argument("--board-set", default="pinned")
    ap.add_argument("--predictions")
    ap.add_argument("--relation")
    ap.add_argument("--arms", default="none,count,seq,seq-gc")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = score(a)
    s = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(s + "\n")
    print(json.dumps({arm: {k: ({kk: v[kk] for kk in ("n", "rms", "mean", "verdict")} if isinstance(v, dict) and "rms" in v else None)
                            for k, v in res.items() if k.startswith("DT-")} for arm, res in out["arms"].items()}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
