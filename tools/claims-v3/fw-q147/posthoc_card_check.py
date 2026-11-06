#!/usr/bin/env python3
"""fw-q147, post hoc desk check (no card; Thu 5 Nov 2026): do aifoundry3 (E171) and aifoundry1 card 1 (E172) do the same
work per op on pool 8, and how far apart are their minion rails after each card's own V^2?

Reads two committed reductions only (E171's and E172's), the same 71 items on both cards. For each item it compares the
cycles a step (`cycles_per_op`), the measured op rate (`rate`, launch records prorated over the window) and the switching
power above the zeros anchor on the minion rail (`Drail`) and on the board (`D`). Power ratios are card 1 over aifoundry3,
divided by (v_card1 / v_aifoundry3)^2 with each session's own mean minion voltage (`v_mean`), and use only items whose
aifoundry3 figure exceeds 1 W. Everything here is POST HOC: read after the data, never a prediction or a verdict.

Usage (from the top of the lab repository):
  python3 -I tools/claims-v3/fw-q147/posthoc_card_check.py . tools/claims-v3/fw-q147/posthoc-card-check.json
"""
import json
import statistics
import sys

repo, out = sys.argv[1], sys.argv[2]
IN_A = "docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json"
IN_B = "docs/reports/data/2026-11-05-e172-blind8-card1/e172.json"
a = json.load(open(f"{repo}/{IN_A}"))
b = json.load(open(f"{repo}/{IN_B}"))
va, vb = a["v_mean"], b["v_mean"]
v2 = (vb / va) ** 2
res = {"inputs": [IN_A, IN_B],
       "v_mean_aifoundry3": va, "v_mean_card1": vb, "v2_ratio_card1_over_a3": v2,
       "cycles_per_op_aifoundry3": a["cycles_per_op"], "cycles_per_op_card1": b["cycles_per_op"]}


def mean(item, field):
    v = item.get(field)
    return v.get("mean") if isinstance(v, dict) else v


rows = []
for k in sorted(set(a["items"]) & set(b["items"])):
    ia, ib = a["items"][k], b["items"][k]
    ra, rb = mean(ia, "rate"), mean(ib, "rate")
    rows.append({"item": k, "type": ia.get("type"),
                 "rate_ratio": (rb / ra) if ra and rb else None,
                 "cpo_a3": ia.get("cycles_per_op"), "cpo_c1": ib.get("cycles_per_op"),
                 "Drail_a3": mean(ia, "Drail"), "Drail_c1": mean(ib, "Drail"),
                 "D_a3": mean(ia, "D"), "D_c1": mean(ib, "D")})
res["n_common_items"] = len(rows)


def ratios(rs, key_a, key_b, scale):
    got = []
    for r in rs:
        x, y = r[key_a], r[key_b]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and x > 1.0:
            got.append((y / x) / scale)
    return got


groups = (("floats", [r for r in rows if r["type"] in ("fp32", "fp16")]),
          ("int8", [r for r in rows if r["type"] == "int8"]),
          ("all", rows))
for name, rs in groups:
    rr = ratios(rs, "Drail_a3", "Drail_c1", v2)
    bd = ratios(rs, "D_a3", "D_c1", v2)
    rt = [r["rate_ratio"] for r in rs if r["rate_ratio"]]
    res[name] = {"n": len(rs),
                 "minion_rail_D_ratio_c1_over_a3_after_V2_median": statistics.median(rr) if rr else None,
                 "n_rail": len(rr),
                 "board_D_ratio_c1_over_a3_after_V2_median": statistics.median(bd) if bd else None,
                 "n_board": len(bd),
                 "op_rate_ratio_c1_over_a3_median": statistics.median(rt) if rt else None,
                 "op_rate_ratio_min": min(rt) if rt else None,
                 "op_rate_ratio_max": max(rt) if rt else None}
res["cycles_per_op_identical_every_common_item"] = all(
    r["cpo_a3"] == r["cpo_c1"] for r in rows if r["cpo_a3"] is not None and r["cpo_c1"] is not None)
res["label"] = "post hoc: read after the data from committed reductions; not a prediction"
with open(out, "w") as f:
    json.dump(res, f, indent=1)
    f.write("\n")
for k in ("v2_ratio_card1_over_a3", "n_common_items", "cycles_per_op_identical_every_common_item"):
    print(k, res[k])
for name, _ in groups:
    print(name, res[name])
