#!/usr/bin/env python3
"""E98, amendment A1 (Q132): writes amendment-1.json, the amended night, and what five probes do to the frozen power estimate. predictions.json is not touched:
its targets, gates and noise stand, and the scorer reads them as they were. Standard library plus reduce_e98's verdict functions. Seeded, no card.

    python3 make_amendment1_e98.py > amendment-1.txt
"""
import json
import math
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e98 as X  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions.json")))
TG, N, T975, W_PER_C = P["targets"], P["noise_planning"], P["t975"], P["constants"]["rest_w_per_c"]
KEEP = ["P1", "P2", "P3", "P6", "P7"]
E101 = {"start_utc": "2026-11-01T12:20:00Z", "end_utc": "2026-11-01T13:35:00Z", "start_epoch": 1793535600, "end_epoch": 1793540100,
        "what": "a real matmul, kind by kind, under this card's own governor"}
x_all = [P["expected_rest"][k]["rest_w"] / W_PER_C for k in KEEP]


def scaled(xs, fall):
    a, b = xs[0], xs[-1]
    return [(x - b) / (a - b) * fall for x in xs]


def half_width(xs, sigma):
    m = st.mean(xs)
    return T975[str(len(xs) - 2)] * sigma / math.sqrt(sum((x - m) ** 2 for x in xs))


def simulate(beta, xs, sigma, verdict, n=20000, seed=98):
    rng = random.Random(seed)
    m = st.mean(xs)
    sxx = sum((x - m) ** 2 for x in xs)
    tq = T975[str(len(xs) - 2)]
    out = {}
    for _ in range(n):
        ys = [beta * (x - m) + rng.gauss(0, sigma) for x in xs]
        my = st.mean(ys)
        b = sum((x - m) * (y - my) for x, y in zip(xs, ys)) / sxx
        res = [y - my - b * (x - m) for x, y in zip(xs, ys)]
        se = math.sqrt(sum(r * r for r in res) / (len(xs) - 2) / sxx)
        v = verdict({"lo": b - tq * se, "hi": b + tq * se})
        out[v] = out.get(v, 0) + 1
    return {k: round(v / n, 3) for k, v in sorted(out.items())}


vl = lambda f: X.verdict_target(f, TG["line_slope"])                          # noqa: E731
vh = lambda f: X.verdict_band(f, TG["hold_band"], TG["hold_floor"])           # noqa: E731
power = {}
for fall in (2.0, 1.5, 1.0):
    xs = scaled(x_all, fall)
    power[f"fall_{fall:g}_C"] = {
        "line_half_width": round(half_width(xs, N["line_c"]), 2),
        "line_verdicts_if_slope_0.25": simulate(TG["line_slope"], xs, N["line_c"], vl),
        "line_verdicts_if_slope_0": simulate(0.0, xs, N["line_c"], vl),
        "hold_half_width": round(half_width(xs, N["hold_die_c"]), 2),
        "hold_verdicts_if_slope_room": simulate(TG["hold_slope_room"], xs, N["hold_die_c"], vh),
        "hold_verdicts_if_slope_0.25": simulate(TG["line_slope"], xs, N["hold_die_c"], vh),
        "fine_line_half_width_w_per_w": round(half_width([x * W_PER_C for x in xs], N["fine_line_w"]), 2),
        "hold_w_half_width_w_per_w": round(half_width([x * W_PER_C for x in xs], N["hold_w"]), 2),
    }
A = {"amendment": "A1", "probes_kept": KEEP, "probes_dropped": ["P4", "P5"], "slot_E101": E101, "p3_latest_start_utc": "2026-11-01T11:56:00Z",
     "p3_latest_start_epoch": 1793534160, "power_five_probes": power, "power_seven_probes_frozen": {k: {kk: v[kk] for kk in ("line_half_width", "hold_half_width")} for k, v in P["power"].items()}}
json.dump(A, open(os.path.join(HERE, "amendment-1.json"), "w"), indent=1, sort_keys=True)
for k, v in power.items():
    print(k, json.dumps(v))
print("seven probes, frozen:", json.dumps(A["power_seven_probes_frozen"]))
