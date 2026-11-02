#!/usr/bin/env python3
"""E131, derived after verification (Mon 2 Nov 2026): E131-X4's statistic at each reduction arm.

X4 (predictions-e131.json > cross_card.X4) is the median, over its 24 eligible tiles, of D(aifoundry3) / D(card 1): E95's
registered dips-removed arm (docs/reports/data/2026-11-01-e95-real-tensors-energy/dips-arm/e95-nodips.json) over this
card's reduction, each tile's D its mean over the kept passes. The scorer prints it for the carrying reading only
(scored.json > cross_card.carrying.x4.median_ratio) and the arms' verdicts (cross_card.at_arms); this prints each arm's
median beside its verdict's band. It decides nothing. Run from the repo root:

    python3 docs/reports/data/2026-11-02-e131-real-tiles-card1/x4-arms-e131.py > docs/reports/data/2026-11-02-e131-real-tiles-card1/x4-arms-e131.txt

SPDX-License-Identifier: Apache-2.0
"""
import json
import statistics

D131 = "docs/reports/data/2026-11-02-e131-real-tiles-card1/"
A3 = "docs/reports/data/2026-11-01-e95-real-tensors-energy/dips-arm/e95-nodips.json"
reg = json.load(open("tools/claims-v3/e131/predictions-e131.json"))["cross_card"]["X4"]
eligible, band = reg["eligible"], reg["band"]
a3 = json.load(open(A3))


def mean_d(res, name):
    v = [res["per_pass"][str(p)].get(name, {}).get("D") for p in res["passes"]]
    v = [x for x in v if x is not None]
    return statistics.fmean(v)


print(f"E131-X4 at each arm: median of D(aifoundry3, E95 dips removed) / D(card 1) over {len(eligible)} eligible tiles; "
      f"band [{band[0]}, {band[1]}] ({reg['band_source']})")
for name, label in (("e131.json", "primary (frozen 0.2414 W/C, dips removed)"), ("e131-auto.json", "auto (the session's fitted slope)"),
                    ("e131-leak0.1994.json", "leak 0.1994"), ("e131-leak0.3803.json", "leak 0.3803"),
                    ("e131-leak0.545.json", "leak 0.545"), ("e131-dipskept.json", "dips kept")):
    c1 = json.load(open(D131 + name))
    m = statistics.median(mean_d(a3, n) / mean_d(c1, n) for n in eligible)
    inside = band[0] <= m <= band[1]
    print(f"   {label}: slope {c1['leak']['k_w_per_c']:.4f} W/C, passes {c1['passes']}, median {m:.4f}, "
          f"{'inside' if inside else 'outside'} the band")
