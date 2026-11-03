#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u), corrections after verification (post hoc), C1's example: one governed E143 burst, its board reading by the SP's
own clock and voltage reading (sp.minion_mhz[0], sp.minion_mv[0], refreshed with board_w), A2's dips against the samples
A2 keeps, over the governed span (the first sample off the idle reading to the last above 45 W). Committed telemetry only.

    python3 fix_trace.py [trace name] > fix-trace.txt
"""
import gzip
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_footing as RF  # noqa: E402

TEL = os.path.join(RF.DD, "2026-11-02-e143-blind5-aifoundry2", "aifoundry2", "s1", "tel")
name = sys.argv[1] if len(sys.argv) > 1 else "BURST-11-b5-fp32.anchor_randn-r1.jsonl.gz"
recs = [json.loads(ln) for ln in gzip.open(os.path.join(TEL, name), "rt") if ln.startswith("{")]
B = [r["board_w"] for r in recs]
bad = set(RF.drop_dips(recs)[1])
first = next(i for i, r in enumerate(recs) if r["sp"]["minion_mhz"][0] != 600 or r["board_w"] > 40)
last = max(i for i, r in enumerate(recs) if r["board_w"] > 45)
print(f"E143 s1 {name}: governed span samples {first}-{last} of {len(recs)}; A2 dips at {sorted(bad)}")
acc = {}
for i in range(first, last + 1):
    k = (recs[i]["sp"]["minion_mhz"][0], recs[i]["sp"]["minion_mv"][0])
    acc.setdefault(k, {"dip": [], "kept": []})["dip" if i in bad else "kept"].append(B[i])
print("SP clock MHz, SP mV | A2 dips: n, min, median, max board W | kept: n, min, median, max board W")
for k, v in sorted(acc.items()):
    cell = lambda x: f"{len(x)}, {min(x):.2f}, {st.median(x):.2f}, {max(x):.2f}" if x else "0"
    print(f"{k[0]}, {k[1]} | {cell(v['dip'])} | {cell(v['kept'])}")
