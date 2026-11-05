#!/usr/bin/env python3
"""E164, post hoc readings at the desk (Wed 4 Nov 2026, after the registered score; never a verdict, nothing rescored), from scored.json:

1. E164-U1's 12 unaimed tiles split by family: M9's and M6's mean error (measured - predicted) and rms on the float and the int8 tiles.
2. The runs E78's launch rule skipped ("launch reading not reached ... skipped"), from each pass's run.log.

    python3 -B docs/reports/data/2026-11-04-e164-blind7-card1/posthoc/readings_e164.py > .../posthoc/readings_e164.txt
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.dirname(HERE)
s = json.load(open(os.path.join(DD, "scored.json")))
p = s["primary"]
U = p["rules"]["E164-U1"]["tiles"]
print("1. E164-U1's 12 unaimed tiles by family (W; measured - predicted)")
for m in ("M9", "M8", "M7", "M6"):
    rows = p["power_rows"][m]
    for fam, test in (("floats", lambda t: not t.startswith("int8.")), ("int8", lambda t: t.startswith("int8."))):
        e = [rows[t]["measured"] - rows[t]["pred"] for t in U if test(t)]
        print(f"  {m} {fam:6s} n {len(e)}: mean {sum(e) / len(e):+.3f}, rms {(sum(x * x for x in e) / len(e)) ** 0.5:.3f}")
print("2. Runs skipped by E78's launch rule")
pat = re.compile(r"pass (\d+) #(\d+) (\S+): launch reading not reached .*: skipped")
n = 0
for f in sorted(glob.glob(os.path.join(DD, "aifoundry1-c1", "e164", "p164*", "run.log"))):
    for line in open(f):
        m = pat.search(line)
        if m:
            n += 1
            print(f"  pass {m.group(1)} run #{m.group(2)} {m.group(3)}")
print(f"  {n} runs skipped")
