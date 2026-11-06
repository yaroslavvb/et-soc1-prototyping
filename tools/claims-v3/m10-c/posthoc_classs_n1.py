#!/usr/bin/env python3
"""Q148(c), POST HOC (pool 8 is measured; written after termc.py's fit output; it decides nothing): pool 8's class S, the 8 N1 tiles a
card (blind8.json role 'kind', case 'S', priority 1, the set the card day critic's class-S figures read), with the frozen one-word level
of termc-fit.json added at each tile's measured rate, inside the session's scale and card term. First it reproduces the committed
class-S figures from E171's and E172's scored rows (M10 0.273 W rms, bias +0.195, on aifoundry3; 0.238 / +0.138 on card 1).

    python3 -B posthoc_classs_n1.py > posthoc-classs-n1.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B8 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind8")
load = lambda p: json.load(open(p))  # noqa: E731
fit = load(os.path.join(HERE, "termc-fit.json"))
man = {t["name"]: t for t in load(os.path.join(B8, "blind8.json"))["tiles"]}
N1S = {n for n, t in man.items() if t.get("role") == "kind" and t.get("case") == "S" and t.get("priority") == 1}
REF = {"a3": (0.273, 0.195), "c1": (0.238, 0.138)}
ok = True
print("POST HOC: pool 8's class S (8 N1 tiles a card) with the frozen one-word level added (termc-fit.json, primary K)")
for cd in ("a3", "c1"):
    rows = [r for r in fit["posthoc_single_bit"]["pool8_list"] if r["card"] == cd and r["key"] in N1S]
    e = [r["e"] for r in rows]
    ep = [r["e_prime"] for r in rows]
    rm = lambda v: math.sqrt(sum(x * x for x in v) / len(v))  # noqa: E731
    mn = lambda v: sum(v) / len(v)  # noqa: E731
    good = len(rows) == 8 and abs(rm(e) - REF[cd][0]) < 0.0005 and abs(mn(e) - REF[cd][1]) < 0.0005
    ok &= good
    print(f"  {cd}: {len(rows)} tiles; M10 {rm(e):.3f} W rms (bias {mn(e):+.3f}) [the committed {REF[cd][0]:.3f} / {REF[cd][1]:+.3f}: "
          f"{'reproduced' if good else 'NOT REPRODUCED'}] -> M10 + the level {rm(ep):.3f} W rms (bias {mn(ep):+.3f}); level added "
          f"{min(r['add_w'] for r in rows):+.4f} to {max(r['add_w'] for r in rows):+.4f} W")
    for r in sorted(rows, key=lambda x: x["key"]):
        print(f"      {r['key']:40s} e {r['e']:+.3f} -> {r['e_prime']:+.3f}")
print("CHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
