#!/usr/bin/env python3
"""E151, POST HOC (written after E151's data were reduced and scored; no rule reads it, never a verdict): the per-block B odd - even and
each B item's per-block rail price in the kept blocks' session order, the first four kept blocks against the last four, with the two
set-aside blocks (gates-off arm) beside them, and the same split of E138's and E145's (filtered) blocks for comparison. It uses the
registered scorer's Book (score_e151 -> score_e145 -> score_e130, unchanged) on the committed per-run tables. Standard library only.

    python3 docs/reports/data/2026-11-03-e151-int8-b-aifoundry3/posthoc/halves_e151.py > .../posthoc/halves.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e151"))
import score_e151 as S151  # noqa: E402

S145, S = S151.S145, S151.S
reg = json.load(open(os.path.join(ROOT, "tools/claims-v3/e151/predictions-e151.json")))
tiles = {"int8." + t["tile"]: t for t in json.load(open(os.path.join(ROOT, "tools/claims-v3/e151/e130-items.json")))["tiles"]}
D = os.path.join(ROOT, "docs/reports/data")
E = os.path.join(D, "2026-11-03-e151-int8-b-aifoundry3")


def welch(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
    return mb - ma, se, (mb - ma) / se if se else None


def show(name, csvp, redp, num, gate=True):
    b = S145.make_book(csvp, redp, "rail_raw", gate, reg, tiles, num)
    combo = S.combos()["B_odd_minus_even_fJ"]
    pb = S.per_block_stat(b, combo)
    keys = sorted(pb)
    print(f"== {name}: {len(keys)} B blocks, B odd - even per block (rail fJ, session order): " +
          ", ".join(f"{k} {pb[k]:+.1f}" for k in keys))
    if len(keys) >= 6:
        h = len(keys) // 2
        a, c = [pb[k] for k in keys[:h]], [pb[k] for k in keys[-h:]]
        d, se, t = welch(a, c)
        print(f"   first {h}: mean {statistics.mean(a):+.2f} (sd {statistics.stdev(a):.2f}); last {h}: mean {statistics.mean(c):+.2f} "
              f"(sd {statistics.stdev(c):.2f}); difference {d:+.2f} +- {se:.2f} (Welch t {t:+.2f})")
        for it in ("b1_0", "b1_1", "b1_2", "b1_3", "b1_4", "b1_5", "b1_6", "b1_7"):
            s = b.series(it)
            ka = [s[k] for k in keys[:h] if k in s]
            kc = [s[k] for k in keys[-h:] if k in s]
            print(f"   {it}: first {statistics.mean(ka):6.1f}  last {statistics.mean(kc):6.1f}  shift {statistics.mean(kc) - statistics.mean(ka):+6.1f} rail fJ")
    return pb


show("E151 primary (8 kept)", f"{E}/runs.csv", f"{E}/e151.json", "e151")
show("E151 gates off (all 10)", f"{E}/runs-gatesoff.csv", f"{E}/e151-gatesoff.json", "e151", gate=False)
show("E138 (aifoundry3, 2 Nov)", f"{D}/2026-11-02-e138-int8-b-rail/runs.csv", f"{D}/2026-11-02-e138-int8-b-rail/e138.json", "e138")
show("E145 under E151's filter (card 1)", f"{ROOT}/tools/claims-v3/e151/e145-filtered/runs.csv",
     f"{ROOT}/tools/claims-v3/e151/e145-filtered/e145-filtered.json", "e145")
