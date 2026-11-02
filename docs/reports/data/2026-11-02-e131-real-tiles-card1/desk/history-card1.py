#!/usr/bin/env python3
"""E131 desk (before the registration): how often E78's anchor pass gates fire on aifoundry1 card 1 and on aifoundry3, over every committed
registered PRIMARY reduction of an E78-frame pass (one reduction per experiment: the data directory's own e<NN>*.json, never an arm, a
post-hoc or a relaxed re-reduction). Reads only committed files; prints per card the zeros lines' straight-line departures and spans and the
random anchors' spans against E78's limits (0.25, 0.60 and 1.0 W), and the passes each primary set aside and why.

    python3 docs/reports/data/2026-11-02-e131-real-tiles-card1/desk/history-card1.py > .../desk/history-card1.txt
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", ".."))
ARM = re.compile(r"(dipskept|leak|auto|gatesoff|scored|predictions|relax|posthoc|nodips|noa1|extras|counts|readback|pool|r1p)", re.I)
rows, sets = [], []
for f in sorted(glob.glob(R + "/*/e*.json") + glob.glob(R + "/*/[ab]-*/e*.json")):
    rel = os.path.relpath(f, R)
    if ARM.search(os.path.basename(f)) or "2026-11-02-e131" in rel:
        continue
    if not re.match(r"^e\d+[a-z]?\.json$", os.path.basename(f)):
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if not isinstance(d, dict) or "anchors" not in d or "passes_set_aside" not in d:
        continue
    card = d.get("card")
    nps = len(d["anchors"])
    sets.append((card, rel, nps, d["passes_set_aside"], (d.get("leak") or {}).get("k_w_per_c")))
    for p, an in d["anchors"].items():
        for name, e in an.items():
            rows.append((card, rel, p, name, e.get("mid_departure_w"), e.get("range_w")))
for c in sorted({r[0] for r in rows}):
    rr = [r for r in rows if r[0] == c]
    ss = [s for s in sets if s[0] == c]
    print(f"== {c}: {len(ss)} primary reductions, {sum(s[2] for s in ss)} passes")
    for nm in ("fp32.zeros", "fp16.zeros", "int8.zeros"):
        dep = sorted(abs(r[4]) for r in rr if r[3] == nm and r[4] is not None)
        sp = sorted(r[5] for r in rr if r[3] == nm and r[5] is not None)
        if dep:
            print(f"  {nm}: {len(dep)} reads; |straight-line departure| median {dep[len(dep) // 2]:.3f}, max {dep[-1]:.3f} W, "
                  f"> 0.25 W: {sum(1 for x in dep if x > 0.25)}; span max {sp[-1]:.3f} W, > 0.60 W: {sum(1 for x in sp if x > 0.60)}")
    for nm in ("fp32.randn", "fp16.randn", "int8.full"):
        sp = sorted(r[5] for r in rr if r[3] == nm and r[5] is not None)
        if sp:
            print(f"  {nm}: {len(sp)} reads; span median {sp[len(sp) // 2]:.3f}, max {sp[-1]:.3f} W, > 1.0 W: {sum(1 for x in sp if x > 1.0)}")
    print("  set aside by the primaries:")
    for card, rel, nps, sa, k in ss:
        for x in sa:
            print(f"    {rel} (leak {k}): pass {x['pass']}: {'; '.join(x['why'])}")
    print("  reductions read:", ", ".join(f"{s[1]} ({s[2]})" for s in ss))
