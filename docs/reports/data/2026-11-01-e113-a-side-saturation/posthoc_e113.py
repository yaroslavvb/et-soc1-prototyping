#!/usr/bin/env python3
"""E113: the post hoc numbers the README quotes as post hoc (none is a registered verdict). Run from the repo root:
    python3 docs/reports/data/2026-11-01-e113-a-side-saturation/posthoc_e113.py
Writes posthoc.json beside this file:
  sb_law      the 15 A rungs against c x E70's B-side law in the B list's additive sum over the same positions
              (W = 10.52 W frozen; c fitted through the origin), and the same with W free;
  mirror_res  each A rung's residual under the frozen mirror (c = 0.643 x E70's B rung of the same mask);
  bench_vs_card  A over B at the same low mask: Q132(b)'s bench net toggles (counts-hl.json unit.nets_hier over each
              ladder's zero) against the card's watts (E113's alq rungs over E70's lq rungs).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
s = json.load(open(os.path.join(HERE, "scored.json")))
p = json.load(open(os.path.join(HERE, "predictions-e113.json")))
e70 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-27-e70-saturation-ladder/scored.json")))
bench = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-q132-rtl-bench/counts-hl.json")))["rows"]
cov = lambda x, w: w * (1 - math.exp(-x / w))
WB = p["constants"]["WB_refit_W"]
rung = {r["item"]: r for r in p["rungs"]}
pts = [(n, s["items"][n]["dW"], rung[n]["S_B_W"], rung[n]["B_same_mask_E70_W"]) for n in s["D2_A"]["fit_set"]]
xs = [cov(sb, WB) for _, _, sb, _ in pts]
ys = [y for _, y, _, _ in pts]
c = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
out = {"sb_law": {"WB_W": WB, "c": c, "rms_W": math.sqrt(sum((y - c * x) ** 2 for x, y in zip(xs, ys)) / len(xs)),
                  "n_rungs": len(xs)}}
best = None
for i in range(4000):
    w = 1 + i * 0.025
    xw = [cov(sb, w) for _, _, sb, _ in pts]
    cw = sum(x * y for x, y in zip(xw, ys)) / sum(x * x for x in xw)
    e = math.sqrt(sum((y - cw * x) ** 2 for x, y in zip(xw, ys)) / len(xw))
    if best is None or e < best[0]:
        best = (e, w, cw)
out["sb_law_W_free"] = {"rms_W": best[0], "W_W": best[1], "c": best[2]}
c0 = p["constants"]["mirror_c"]
out["mirror_res"] = {n: y - c0 * b for n, y, _, b in pts}
lq = {r["h"]: r["dW"] for r in e70["lq"]}
nets = lambda k: bench["fp32." + k]["mean"]["unit"]["nets_hier"]
za, zb = nets("aq_h0"), nets("lq_h0")
bc = {}
for k in (2, 4, 8, 12, 16, 23):
    b_ratio = (nets(f"alq_h{k}") - za) / (nets(f"lq_h{k}") - zb)
    c_ratio = s["items"][f"alq_h{k}"]["dW"] / lq[k]
    bc[k] = {"bench_A_over_B_nets": b_ratio, "card_A_over_B_W": c_ratio, "bench_over_card": b_ratio / c_ratio}
out["bench_vs_card"] = bc
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
