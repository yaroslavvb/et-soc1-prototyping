#!/usr/bin/env python3
"""E130 self-test of R5 and R6 (amendment A3, Mon 2 Nov 2026, written before any E130 data): how often E130-R5 and
E130-R6 read FAILS when every netlist's shared prediction is true. It reuses selftest_e130.py's model unchanged
(session() and score_rows(): the registered block orders and sequence, a block-long drift curve of 0.3 W, a random walk
of 0.01 W a run, white noise sigma, scored by score_e130.py) in each netlist's world, whose truth is that netlist's
nets_map items, so its sign ratios a2_7 / a1_7 and b2_7 / b1_7 lie inside the shared bands by construction. Sigma 0.015,
0.025 and 0.035 W a run, 200 sessions each, two seed sets: the verification's ("verify r56 <world> <sigma>", three
worlds) and the fix pass's ("fix r56 <world> <sigma>", four). Nothing here is a measurement. Standard library only.

    python3 tools/claims-v3/e130/selftest_r56_e130.py > tools/claims-v3/e130/selftest-r56.txt

SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_e130 as st  # noqa: E402

SIGMAS = (0.015, 0.025, 0.035)
SETS = (("verify r56", ("booth_tree", "booth_swap", "plain")),
        ("fix r56", ("booth_tree", "booth", "booth_swap", "plain")))
N = 200


def fails(counter):
    return sum(c for k, c in counter.items() if k.startswith("FAILS"))


def main():
    print("E130 self-test of R5 and R6: FAILS with every shared prediction true "
          f"({N} sessions a world and sigma; synthetic, nothing here is a measurement)")
    print("shared bands:", json.dumps(st.REG["shared_bands"], sort_keys=True))
    tot = {"R5": [0, 0], "R6": [0, 0]}
    cells = {"R5": [], "R6": []}
    for seed, worlds in SETS:
        print(f"\nseed set '{seed} <world> <sigma>'")
        for world in worlds:
            tr = st.truth(world)
            print(f"  world {world}: truth a2_7/a1_7 {tr['a2_7'] / tr['a1_7']:.4f}, b2_7/b1_7 {tr['b2_7'] / tr['b1_7']:.4f}")
            for sigma in SIGMAS:
                rng = random.Random(f"{seed} {world} {sigma}")
                c5, c6 = collections.Counter(), collections.Counter()
                for _ in range(N):
                    res, _book = st.score_rows(st.session(world, rng, sigma))
                    v = res["verdicts"] if "verdicts" in res else res
                    c5[v["E130-R5"]] += 1
                    c6[v["E130-R6"]] += 1
                for rule, c in (("R5", c5), ("R6", c6)):
                    tot[rule][0] += fails(c)
                    tot[rule][1] += N
                    cells[rule].append(fails(c))
                print(f"    sigma {sigma}: R5 FAILS {fails(c5):3d}/{N} {dict(sorted(c5.items()))}; "
                      f"R6 FAILS {fails(c6):3d}/{N} {dict(sorted(c6.items()))}")
    print()
    for rule in ("R5", "R6"):
        f, n = tot[rule]
        print(f"E130-{rule}: FAILS in {f} of {n} sessions ({100.0 * f / n:.1f}%); by world and sigma "
              f"{100.0 * min(cells[rule]) / N:.1f}-{100.0 * max(cells[rule]) / N:.1f}%")


if __name__ == "__main__":
    main()
