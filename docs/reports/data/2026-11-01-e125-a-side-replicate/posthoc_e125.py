#!/usr/bin/env python3
"""E125: the numbers the README labels POST HOC (none is a registered verdict), from committed files only. Standard library.

    python3 docs/reports/data/2026-11-01-e125-a-side-replicate/posthoc_e125.py   # writes posthoc.json beside this script

  b_small_k   card 1's B rungs at k = 2, 4, 8 (this session, over lq_h0) times E82's card scale, against E70's on aifoundry3
  rho_k       per designed bit, A over B in the low layout at k = 2, 4, 8 within card 1's passes: 2 x N1's r_k
  top_rung    alq_h23 out of every fit, against the refitted mirror, the frozen mirror and the refitted S_A curve, on both cards
  rho8_layout the spread layout's rho(8) minus the low layout's, on card 1 (registered reduction) and on E113's passes in the
              same frame (the desk reduction committed with E125's registration)
  dips        card 1's dips in this session against aifoundry3's in E113's passes (E82 A2's test on both)
  x_registered  how the X rules read against E113's registered (dips-kept) numbers
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
s = json.load(open(os.path.join(HERE, "scored.json")))
p125 = json.load(open(os.path.join(HERE, "predictions-e125.json")))
p113 = json.load(open(os.path.join(HERE, "predictions-e113.json")))
nod = json.load(open(os.path.join(ROOT, "tools/claims-v3/e125/e113-nodips/scored.json")))
reg = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e113-a-side-saturation/scored.json")))
dips113 = json.load(open(os.path.join(ROOT, "tools/claims-v3/e125/e113-nodips/dips.json")))
dips125 = json.load(open(os.path.join(HERE, "dips", "dips.json")))
SC = p125["card_scale"]["s_fp32_aifoundry3_over_card1"]
E = s["e125"]
out = {"note": "post hoc: computed after the data, no verdict"}
lq70 = {r["k"]: (r["B_same_mask_E70_W"], r["B_same_mask_E70_se_W"]) for r in p113["rungs"] if r["layout"] == "low"}
bk = {}
for k in (2, 4, 8):
    e = s["items"][f"lq_h{k}"]
    b70, se70 = lq70[k]
    d = e["dW"] * SC - b70
    bk[k] = {"card1_W": e["dW"], "card1_se": e["se"], "card1_x_s_W": e["dW"] * SC, "E70_W": b70, "E70_se": se70,
             "diff_W": d, "diff_sigma": d / math.hypot(e["se"] * SC, se70)}
out["b_small_k"] = bk
r = E["N1"]["r"]
out["rho_k"] = {k: {"rho": 2 * v["mean"], "se": 2 * v["se"]} for k, v in r.items()}
top = {}
for name, src in (("E125 card 1", s), ("E113 same frame", nod), ("E113 registered", reg)):
    o = src["D2_A"]["out_of_sample_alq_h23"]
    top[name] = {k: o[k] for k in ("dW", "se", "res_M_refit", "res_M_frozen", "res_SA_refit", "above_WA_refit_by_W")}
    top[name]["c_refit"] = src["D2_A"]["c_refit"]
out["top_rung"] = top
out["rho8_layout"] = {name: src["rho8"]["spread_minus_low"] | {"low": src["rho8"]["low"]["rho"], "spread": src["rho8"]["spread"]["rho"]}
                      for name, src in (("E125 card 1", s), ("E113 same frame", nod), ("E113 registered", reg))}
out["dips"] = {"card1_E125": dips125["totals"], "aifoundry3_E113": dips113["totals"]}
xr = E["x_rules_registered"]
out["x_registered"] = {"tally": {v: sum(1 for x in xr if x["verdict"] == v) for v in sorted({x["verdict"] for x in xr})},
                       "not_pass": [(x["id"], x["verdict"], round(x["d"], 3), round(x["h"], 3)) for x in xr if x["verdict"] != "PASS"]}
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
