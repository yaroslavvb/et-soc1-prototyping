#!/usr/bin/env python3
"""E130 post hoc (Mon 2 Nov 2026, after the data; nothing here is registered and no verdict moves). Standard library only,
committed files only: scored.json (score_e130.py's output on the registered primary and arms) and the registration's
predictions-e130.json. Prints:
  1. the three separators block by block on the primary, and B's odd - even with each B block left out in turn;
  2. B's list next to E79's B list on this card (the registration's card_precision_e79), and each list's odd/even ratio;
  3. the separators on the minion-rail arm beside the board's, with the rail-to-board ratio of the A list's levels.
    python3 docs/reports/data/2026-11-02-e130-int8-netlists/posthoc_e130.py > docs/reports/data/2026-11-02-e130-int8-netlists/posthoc_e130.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
S = json.load(open(os.path.join(HERE, "scored.json")))
REG = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e130", "predictions-e130.json")))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}
T_B = REG["thresholds"]["T_B"]
if isinstance(T_B, dict):
    T_B = T_B.get("value", T_B)


def ci(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return m, m - h, m + h


prim = S["primary"]["statistics"]
print("## 1. The separators block by block (primary: board p_raw over each item's own zero, dips removed; fJ per flipped bit)")
for name in ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ"):
    pb = prim[name]["per_block"]
    print(f"{name}: " + ", ".join(f"{k} {v:+.1f}" for k, v in sorted(pb.items())) +
          f"; all: {prim[name]['mean']:+.1f} [{prim[name]['lo']:+.1f}, {prim[name]['hi']:+.1f}]")
pb = prim["B_odd_minus_even_fJ"]["per_block"]
print(f"B odd - even with one B block left out (T_B = {T_B:.2f} fJ):")
for k in sorted(pb):
    m, lo, hi = ci([v for j, v in pb.items() if j != k])
    side = "above" if lo >= T_B else "below" if hi <= T_B else "straddles"
    print(f"  without {k}: {m:+.1f} [{lo:+.1f}, {hi:+.1f}] ({side} T_B)")

print("\n## 2. B's list against E79's on this card (board fJ per flipped bit; E79 at its own base words, 4 passes)")
e79 = REG["card_precision_e79"]["b_list_board_fJ"]
pr = S["primary"]["prices"]
mine = [pr[f"b1_{i}"]["fJ"]["mean"] for i in range(8)]
print("bit:   " + " ".join(f"{i:>7d}" for i in range(8)))
print("E130:  " + " ".join(f"{x:+7.1f}" for x in mine))
print("E79:   " + " ".join(f"{x:+7.1f}" for x in e79))
for lab, xs in (("E130", mine), ("E79", e79)):
    odd = sum(xs[i] for i in (1, 3, 5)) / 3
    even = sum(xs[i] for i in (0, 2, 4)) / 3
    print(f"{lab}: odd (1, 3, 5) {odd:+.1f}, even (0, 2, 4) {even:+.1f}, odd - even {odd - even:+.1f}, odd/even {odd / even:.2f}")

print("\n## 3. The minion rail (an arm) beside the board (the primary)")
rail = S["arms"]["rail"]["statistics"]
for name in ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ", "B_mean_bits0to6_fJ",
             "A_mean_bits0to6_fJ"):
    b, r = prim[name], rail[name]
    print(f"{name}: board {b['mean']:+.1f} [{b['lo']:+.1f}, {b['hi']:+.1f}]; rail {r['mean']:+.1f} [{r['lo']:+.1f}, {r['hi']:+.1f}]")
for name in ("B_odd_over_even", "A_odd_over_even", "A_sign_dense_over_one", "B_sign_w2_over_w1", "A_sign_w2_over_w1"):
    b, r = prim[name], rail[name]
    f = lambda v: "unbounded" if v is None else f"{v:.2f}"  # noqa: E731
    print(f"{name}: board {f(b['ratio'])} [{f(b['lo'])}, {f(b['hi'])}]; rail {f(r['ratio'])} [{f(r['lo'])}, {f(r['hi'])}]")
rb = rail["A_mean_bits0to6_fJ"]["mean"] / prim["A_mean_bits0to6_fJ"]["mean"]
print(f"rail / board on A's bits 0-6 (a level, post hoc): {rb:.2f}")
print(f"zeros' scatter about their neighbours' line: board {S['primary']['zero_residual_sd_W']:.4f} W, "
      f"rail {S['arms']['rail']['zero_residual_sd_W']:.4f} W ({S['primary']['zero_residual_n']} interior reads)")
