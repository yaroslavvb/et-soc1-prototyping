#!/usr/bin/env python3
"""Q139(q), POST HOC: G3's two open constants, chosen on the four GEMM-pattern sessions, nested leave one session out.

G3's chain (Q138(t) a2), P0's levels, the burst cap and the schedule are frozen. Two constants of the power and trip path are not frozen by any
earlier lane for a GEMM: the leakage slope on P0 above the run's start die (Q138(t)'s 0.442 W per C was fitted on idle rests) and the die the
governor holds a GEMM at (Q138(t)'s 65.9 C came from the kinds loop's E133 holds; E136's law used 65.5 C). Each is chosen on a grid by the
critic's three rules as one loss, sum over runs of (clock err / 15 MHz)^2 + (board err / 2 W)^2 + (die err / 1 C)^2:
  * nested: for each session held out, the grid point best on the other three, scored on the held-out one (out of sample by session);
  * final: the grid point best on all four (the constants frozen for E159; in sample on these runs).
Reads posthoc-g3-inputs.json (written by posthoc_g3.py). Writes fit-g3.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g3_model as G  # noqa: E402

K_GRID = (0.0, 0.1, 0.2, 0.3, 0.442)
TRIP_GRID = (65.1, 65.3, 65.5, 65.7, 65.9)
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
INP = json.load(open(os.path.join(HERE, "posthoc-g3-inputs.json")))
SESS = ("E119", "E126", "E136", "E146")


def run_all(k, trip):
    res = []
    for c in INP:
        lev = {int(f): v for f, v in c["lev"].items()}
        on = np.array(c["on"], bool)
        gg = c["gg0"] + np.arange(len(on)) * G.DT
        T, P, F = G.simulate(lev, on, np.array(c["x0"]), c["anc"], T_start=c["T_start"], trip=trip, k_leak=k)
        p = G.window_means(gg, on, T, P, F, c["t1"])
        res.append({"session": c["session"], "cell": c["cell"], "err": {q: c["meas"][q] - p[q] for q in RULE}, "pred": p})
    return res


def loss(rows):
    return float(sum(sum((r["err"][q] / RULE[q]) ** 2 for q in RULE) for r in rows))


def summary(rows):
    out = {}
    for q in RULE:
        e = np.array([r["err"][q] for r in rows])
        out[q] = {"rms": round(float(np.sqrt(np.mean(e ** 2))), 3), "mean": round(float(np.mean(e)), 3),
                  "within": int(np.sum(np.abs(e) <= RULE[q])), "n": int(len(e))}
    return out


def main():
    grid = {}
    for k in K_GRID:
        for tr in TRIP_GRID:
            grid[(k, tr)] = run_all(k, tr)
            print(f"k {k:5.3f} trip {tr:4.1f}: loss {loss(grid[(k, tr)]):8.2f}  {summary(grid[(k, tr)])}", flush=True)
    nested = {}
    held_rows = []
    for s in SESS:
        best = min(grid, key=lambda kt: loss([r for r in grid[kt] if r["session"] != s]))
        rows = [r for r in grid[best] if r["session"] == s]
        nested[s] = {"chosen_on_others": {"k_leak": best[0], "trip_C": best[1]}, "held_out": summary(rows)}
        held_rows += rows
        print(f"held out {s}: chosen k {best[0]}, trip {best[1]} -> {summary(rows)}")
    final = min(grid, key=lambda kt: loss(grid[kt]))
    out = {"what": "Q139(q) post hoc: G3's leakage slope and held die, nested leave one session out, then on all four sessions",
           "grid": {"k_leak": K_GRID, "trip_C": TRIP_GRID}, "rule_scale": RULE,
           "grid_scores": {f"{k}|{t}": {"loss": round(loss(v), 3), "summary": summary(v)} for (k, t), v in grid.items()},
           "nested": nested, "nested_pooled": summary(held_rows),
           "final": {"k_leak": final[0], "trip_C": final[1], "in_sample": summary(grid[final]),
                     "by_session": {s: summary([r for r in grid[final] if r["session"] == s]) for s in SESS}},
           "as_first_written": {"k_leak": 0.442, "trip_C": 65.9, "summary": summary(grid[(0.442, 65.9)])}}
    print(f"nested, pooled over the four held-out sessions: {out['nested_pooled']}")
    print(f"final (all four): k {final[0]}, trip {final[1]}: {out['final']['in_sample']}")
    json.dump(out, open(os.path.join(HERE, "fit-g3.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
