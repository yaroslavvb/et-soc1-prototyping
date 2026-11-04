#!/usr/bin/env python3
"""E153: post hoc readings quoted in README.md, from this directory's committed files only (scored.json, runs.csv, e153.json, the
pass directories) and E141's committed runs.csv. Nothing here is a registered rule or verdict. Standard library only.

    python3 docs/reports/data/2026-11-03-e153-blind6-aifoundry3/posthoc_e153.py > docs/reports/data/2026-11-03-e153-blind6-aifoundry3/posthoc.txt
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
E141 = os.path.join(HERE, "..", "2026-11-02-e141-blind5-aifoundry3")


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


S = json.load(open(os.path.join(HERE, "scored.json")))
P = S["primary"]["primary"]
pw = {m: P["power_rows"][m] for m in ("M8", "M7", "M6")}
reg = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "e153", "predictions-e153.json")))
p1 = reg["sets"]["priority1_by_format"]
print("E153 post hoc readings (posthoc_e153.py; committed files only; none is a registered rule or verdict)\n")
e = [pw["M8"][t]["error"] for t in p1["fp32"]]
e2 = [pw["M8"][t]["error"] for t in p1["fp32"] if t != "fp32.b_onebit_b20_third"]
print(f"1. P1's fp32 rms over the 12 priority-1 kinds {rms(e):.3f} W; without fp32.b_onebit_b20_third (error "
      f"{pw['M8']['fp32.b_onebit_b20_third']['error']:+.3f} W) {rms(e2):.3f} W over 11 (P1's 97.5% line, 12 draws: "
      f"{P['rules']['E153-P1']['interval']['hi95']:.3f} W)")
b20, b12 = "fp32.b_onebit_b20_third", "fp32.b_onebit_b12_third"
gap = {m: pw[m][b20]["pred"] - pw[m][b12]["pred"] for m in ("M8", "M7", "M6")}
print(f"   bit 20 against bit 12 on the 1/3 base word (the same A, the same base word, one B bit flipping every cycle): measured "
      f"{pw['M8'][b20]['measured'] - pw['M8'][b12]['measured']:.3f} W apart; predicted M8 {gap['M8']:.3f}, M7 {gap['M7']:.3f}, "
      f"M6 {gap['M6']:.3f} W; bit 20's errors M8/M7/M6 {pw['M8'][b20]['error']:+.3f} / {pw['M7'][b20]['error']:+.3f} / "
      f"{pw['M6'][b20]['error']:+.3f} W")
print("\n2. int8, the tiles where M8's near-whole-byte B discount acts most (case L and Z; error = measured - model, W):")
for t in ("int8.b_line_55_aa", "int8.a_zeros_b_lineflip", "int8.b_line_zero_ff", "int8.b_line_zero_full", "int8.a_word_zero_one"):
    print(f"   {t:28s} measured {pw['M8'][t]['measured']:6.3f}  M8 {pw['M8'][t]['error']:+.3f}  M7 {pw['M7'][t]['error']:+.3f}  "
          f"M6 {pw['M6'][t]['error']:+.3f}  (priority {pw['M8'][t]['priority']})")
rest = [t for t in p1["int8"] if t not in ("int8.a_zeros_b_lineflip", "int8.b_line_zero_ff")]
for m in ("M8", "M7", "M6"):
    print(f"   {m}: priority-1 int8 rms {rms([pw[m][t]['error'] for t in p1['int8']]):.3f} W; without the two priority-1 tiles "
          f"above whose B bytes flip all 8 bits (a_zeros_b_lineflip, b_line_zero_ff) {rms([pw[m][t]['error'] for t in rest]):.3f} W over {len(rest)}")
print("\n3. exponent-heavy kinds (case E, all 10): measured - model, W")
E = [t for t in reg["sets"]["new_kinds"] if reg["tiles"][t]["case"].split()[0] == "E"]
for m in ("M8", "M7", "M6"):
    v = [pw[m][t]["error"] for t in E]
    print(f"   {m}: mean {statistics.mean(v):+.3f}, rms {rms(v):.3f}, {sum(1 for x in v if x > 0)} of {len(v)} above zero")
print("\n4. the C log's duty (E78's per-run duty, the reducer's runs.csv): this session against E141's on this card")
for name, path in (("E153", os.path.join(HERE, "runs.csv")), ("E141", os.path.join(E141, "runs.csv"))):
    d = [float(r["duty"]) for r in csv.DictReader(open(path)) if r["duty"] not in ("", "nan", "None")]
    print(f"   {name}: {len(d)} runs, duty median {statistics.median(d):.4f}, min {min(d):.4f}, max {max(d):.4f}")
k = S["primary"]["K1"]["tiles"]
diffs = [r["diff_w"] for r in k.values() if "diff_w" in r]
print(f"   K1's six D minus E141's on Q139(u)'s footing: mean {statistics.mean(diffs):+.4f} W, range {min(diffs):+.4f} to {max(diffs):+.4f}")
print(f"   K1's six D over their E141 D, mean ratio {statistics.mean([r['E153']['mean'] / r['E141']['mean'] for r in k.values() if 'diff_w' in r]):.4f}")
print("\n5. paired M8 - M6 rms over all 44 new kinds (the scorer's reported_priority2): "
      + json.dumps({x: (round(v, 4) if isinstance(v, float) else v) for x, v in P["reported_priority2"]["paired_M8_minus_M6_all_new_kinds"].items()}))
for m in ("M8", "M7", "M6"):
    v = [pw[m][t]["error"] for t in reg["sets"]["new_kinds"]]
    print(f"   {m}: all 44 new kinds rms {rms(v):.3f} W, bias {statistics.mean(v):+.3f} W, inside own band "
          f"{sum(1 for t in reg['sets']['new_kinds'] if pw[m][t]['inside'])} of 44")
