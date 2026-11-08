#!/usr/bin/env python3
"""E184 arm B (Q156, card day Sun 8 Nov 2026), POST HOC readings, written after the data and deciding nothing: three looks at arm B's
reduced file that help read its registered outcomes. Every verdict stays the scorer's (scored-e184-v3.json); nothing here is a rule.

  1. E184-M by level: each scored level's median SRAM min/avg and max/avg (the scorer's), their spread with and without the idle level,
     beside September's committed idle and busy medians (forecast-e184.json > forecasts > card1_sram > H-MIX > q150_committed).
  2. E184-X split in two: the registered statistic is (today's card-1 SRAM share of the board) / (September's aifoundry3 share), per B3
     configuration and pass. Post hoc it is the product of (today's card-1 share) / (September's card-1 share) and (September's card-1
     share) / (September's aifoundry3 share), each read from the energy catalogue's rows in inputs-e184.json > catalogue > sram_set.
  3. E184-T burst by burst: each B2 burst's SRAM tau on the rise and on the fall, and the fitted step size A (A1's reader's fits).

Usage (from the top of the lab repository):
  /usr/bin/python3 -B <this file> <data dir> > <data dir>/posthoc-armb-e184.json
Standard library only; reads the data directory's reduced and scored files and the registration's inputs and forecasts.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import statistics
import sys

d = sys.argv[1]
E = "tools/claims-v3/e184"
red = json.load(open(os.path.join(d, "reduced-e184b-v4.json")))
sc = json.load(open(os.path.join(d, "scored-e184-v3.json")))["arm_B"]
fc = json.load(open(os.path.join(E, "forecast-e184.json")))["forecasts"]["card1_sram"]
inp = json.load(open(os.path.join(E, "inputs-e184.json")))
out = {"what": "E184 arm B, post hoc readings (after the data; deciding nothing; every verdict is scored-e184-v3.json's)",
       "inputs": {"reduced": "reduced-e184b-v4.json", "scored": "scored-e184-v3.json",
                  "forecast": E + "/forecast-e184.json", "catalogue": E + "/inputs-e184.json > catalogue > sram_set"}}


def r6(x):
    return None if x is None else round(x, 6)


# 1. E184-M by level
M = sc["E184-M"]
mins, maxs = M["min_over_avg_by_level"], M["max_over_avg_by_level"]
lv = {x["cfg"] + "/m" + str(x["mask_m"]): x for x in red["passes"]["18441"]["levels"]}
rows = []
for k in sorted(mins):
    x = lv.get(k, {})
    rows.append({"level": k, "n_steady": (x.get("sram_w") or {}).get("n"), "board_w": x.get("board_w"),
                 "sram_avg_w": (x.get("avg_w") or {}).get("sram_w"), "min_over_avg": mins[k], "max_over_avg": maxs[k]})
loaded = [mins[k] for k in mins if not k.startswith("idle/")]
out["E184-M_by_level"] = {
    "rows": rows,
    "spread_min_over_avg_all_levels": r6(max(mins.values()) - min(mins.values())),
    "spread_min_over_avg_without_idle": r6(max(loaded) - min(loaded)),
    "registered_spread_max": fc["H-MIX"]["level_spread_max"],
    "loaded_levels_min_over_avg_range": [r6(min(loaded)), r6(max(loaded))],
    "september_committed": fc["H-MIX"]["q150_committed"],
}

# 2. E184-X split
cat = {x["cfg"]: x for x in inp["catalogue"]["sram_set"]}
per = []
for p in ("18443", "18444"):
    for x in red["passes"].get(p, {}).get("shares", []):
        c = cat.get(x["cfg"])
        if not c or not x.get("share"):
            continue
        a3 = c["a3_sram_w"] / c["a3_board_w"]
        c1 = c["c1_sram_w"] / c["c1_board_w"]
        per.append({"pass": p, "cfg": x["cfg"], "share_today_c1": r6(x["share"]), "share_sept_c1": r6(c1), "share_sept_a3": r6(a3),
                    "registered_ratio_today_c1_over_sept_a3": r6(x["share"] / a3),
                    "today_c1_over_sept_c1": r6(x["share"] / c1), "sept_c1_over_sept_a3": r6(c1 / a3),
                    "board_over_w_today": r6(x.get("board_over_w")), "board_over_w_sept_c1": r6(c["c1_board_w"]),
                    "sram_over_w_today": r6(x.get("sram_over_w")), "sram_over_w_sept_c1": r6(c["c1_sram_w"])})
med = statistics.median
out["E184-X_split"] = {
    "n": len(per),
    "median_registered_ratio": r6(med([y["registered_ratio_today_c1_over_sept_a3"] for y in per])) if per else None,
    "median_today_c1_over_sept_c1": r6(med([y["today_c1_over_sept_c1"] for y in per])) if per else None,
    "median_sept_c1_over_sept_a3": r6(med([y["sept_c1_over_sept_a3"] for y in per])) if per else None,
    "median_board_over_today_over_sept_c1": r6(med([y["board_over_w_today"] / y["board_over_w_sept_c1"] for y in per])) if per else None,
    "median_sram_over_today_over_sept_c1": r6(med([y["sram_over_w_today"] / y["sram_over_w_sept_c1"] for y in per])) if per else None,
    "rows": per,
}

# 3. E184-T burst by burst
fits = [x for x in red["passes"]["18442"]["fits"] if "reason" not in x]
out["E184-T_bursts"] = [{"seq": x.get("seq"), "burst_s": x.get("burst_s"),
                         "sram": {k: r6(x["sram_w"].get(k)) for k in ("tau_rise", "tau_fall", "tau_shared", "A", "rel_rms")},
                         "minion": {k: r6(x["minion_w"].get(k)) for k in ("tau_rise", "tau_fall", "A")},
                         "noc": {k: r6(x["noc_w"].get(k)) for k in ("tau_rise", "tau_fall", "A")}} for x in fits]
json.dump(out, sys.stdout, indent=1, sort_keys=True)
sys.stdout.write("\n")
