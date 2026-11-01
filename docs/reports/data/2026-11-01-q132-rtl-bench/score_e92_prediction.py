#!/usr/bin/env python3
"""The bench's frozen E92 prediction against E92's own paired contrasts.

    score_e92_prediction.py <e92-bench-prediction.json> <E92's scored.json> <E92's e92.json> <out.json>

Order of events: nets_hier2 frozen in de545f0c at 00:43:14 PDT, before E92's first data commit (4e8eb836, 01:06:51 PDT). nets_map and nets_hier
were computed at 01:09 and committed in e7cb1f21 at 01:10:16 PDT, after that data reached main and before it was read, so by the clock only
nets_hier2 is a prediction.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import sys

p = json.load(open(sys.argv[1]))
s = json.load(open(sys.argv[2]))
e = json.load(open(sys.argv[3]))["items"]
out = {"order_of_events": __doc__.split("Order of events: ")[1].split("SPDX")[0].strip().replace("\n", " "), "variants": {}}
meas = {}
c = s["contrasts"]
for k, v in c.items():
    meas[k] = v
for var, P in p["variants"].items():
    rows = []
    for x in P["contrasts_w"]:
        name = x["contrast"]
        m = None
        for key in (name, name.replace("(", "").replace(")", "")):
            if key in meas:
                m = meas[key]
        if m is None:
            continue
        rows.append({"rule": x["rule"], "contrast": name, "measured_w": m["D_w"]["mean"], "ci95": m["D_w"]["ci95"], "predicted_w": x["pred_w"]})
    ys = [r["measured_w"] for r in rows]
    ps = [r["predicted_w"] for r in rows]
    T = P["tiles_D_over_zeros_w"]
    ty, tp = [], []
    for k, v in T.items():
        if k in e and isinstance(e[k].get("D"), dict):
            ty.append(e[k]["D"]["mean"])
            tp.append(v)
    def stat(a, b):
        n = len(a)
        my, mp = sum(a) / n, sum(b) / n
        r = sum((x - my) * (y - mp) for x, y in zip(a, b)) / math.sqrt(sum((x - my) ** 2 for x in a) * sum((y - mp) ** 2 for y in b))
        return {"n": n, "rms_w": math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / n), "bias_w": sum(y - x for x, y in zip(a, b)) / n, "r": r}
    out["variants"][var] = {"tiles": stat(ty, tp), "contrasts": stat(ys, ps) if rows else None, "rows": rows}
json.dump(out, open(sys.argv[4], "w"), indent=1)
for var, o in out["variants"].items():
    print(var, "tiles", {k: round(v, 3) for k, v in o["tiles"].items()}, "contrasts", {k: round(v, 3) for k, v in (o["contrasts"] or {}).items()})
    for r in o["rows"]:
        ci = r["ci95"]
        print(f"   {r['rule']:4s} {r['contrast']:30s} measured {r['measured_w']:6.2f} ±{(ci if ci is not None else 0):5.2f}  predicted {r['predicted_w']:6.2f}")
