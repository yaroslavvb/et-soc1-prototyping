#!/usr/bin/env python3
"""Q145(a), aifoundry3's idle-floor study, dated note 1: G0 and G0-A6 on EVERY committed November floor, settled or not, and what a short
rest leaves (post hoc; reads this study's committed floors.json and floor_analysis.json, Q138(t)'s model-q138t.json and the footing
law's footing-law.json; no telemetry).

  (1) every November 2026 session's first-sample floor, its rest since our last committed session on the card, and the two gates
      with A6-1's pre-smoke stop (F0 above 53.9 C ends the session before the smoke), R0's room modelled as in floor_analysis.py
      (the floor + the largest committed smoke residue, 0.43 C) where no R0 ran;
  (2) by rest, across 22 Sep - 5 Nov: each session's firmware floor against the lowest firmware floor of the settled sessions
      (rest at least 2 h) that started within 6 h of it on either side; the excess is what the shorter rest (or the hour) left;
  (3) M6's slowest pole (tau 1,500 s, weight 0.010, a 25 C plateau) at the same rests, the bound A6's Builds on quotes;
  (4) the loop gain g = R x k(T) at the five raw-code floors by E97's law (the 34-sensor mean, as A6 takes it) and by the footing
      law's FL1 (E44's and E71's dedicated cycles, the firmware reading: the floor less the study's mean offset, 0.94 C), with R
      from Q138(t)'s model-q138t.json > a3.
Labels: "est" floors are the firmware's whole degree + 0.94 C, as the study labels them.

    python3 -B floor_note1.py <lab repo top> <out.json>
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

TOP, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.join(TOP, "docs/reports/data/2026-11-05-q145a-a3-idle-floor")
fa = json.load(open(os.path.join(HERE, "floor_analysis.json")))
fl = json.load(open(os.path.join(HERE, "floors.json")))
RES = 0.43                     # floor_analysis.py's modelled smoke residue (the largest committed, E154's 0.428 C)
LINE_G0, LINE_A6, RESID_A6 = 53.0, 53.9, 0.50

rows = fa["rows"]
t_first = [s["t_first"] for s in fl["sessions"]]
assert len(t_first) == len(rows) and all(r["start_pst"] == s["start_pst"] for r, s in zip(rows, fl["sessions"]))


def gates(r):
    F0 = r["floor_c"]
    if F0 > LINE_A6:
        a6 = "STOP before the smoke (A6-1: F0 > 53.9 C)"
    else:
        room = F0 + RES
        a6 = "PASS" if (room <= LINE_A6 and room - F0 <= RESID_A6) else "REFUSE"
    g0 = "PASS" if F0 + RES <= LINE_G0 else "REFUSE"
    return g0, a6


nov = []
for r in rows:
    if " Nov " not in r["start_pst"]:
        continue
    g0, a6 = gates(r)
    nov.append({"session": r["start_pst"], "rest_h": r["rest_h"], "settled_1h": r["settled"], "floor_c": r["floor_c"],
                "kind": r["floor_kind"], "fw_c": r["fw_c"], "G0": g0, "G0_A6": a6})
cnt = lambda sel, key, val: sum(1 for x in sel if x[key].startswith(val))
summary = {"november_sessions": len(nov),
           "settled_1h": sum(x["settled_1h"] for x in nov),
           "G0_pass_all": cnt(nov, "G0", "PASS"), "G0_A6_pass_all": cnt(nov, "G0_A6", "PASS"),
           "G0_pass_settled": cnt([x for x in nov if x["settled_1h"]], "G0", "PASS"),
           "G0_A6_pass_settled": cnt([x for x in nov if x["settled_1h"]], "G0_A6", "PASS"),
           "stopped_by_A6_1": [x for x in nov if x["G0_A6"].startswith("STOP")],
           "refused_by_G0": [x["session"] for x in nov if x["G0"] == "REFUSE"]}

# (2) excess over nearby settled (rest >= 2 h) firmware floors, by rest bin
ref_idx = [i for i, r in enumerate(rows) if r["rest_h"] is not None and r["rest_h"] >= 2.0]
SIX_H = 6 * 3600 * 1000
by = []
for i, r in enumerate(rows):
    if r["rest_h"] is None:
        continue
    near = [rows[j]["fw_c"] for j in ref_idx if j != i and abs(t_first[j] - t_first[i]) <= SIX_H]
    if not near:
        continue
    by.append({"session": r["start_pst"], "rest_h": r["rest_h"], "fw_c": r["fw_c"], "ref_settled_fw_min": min(near), "n_ref": len(near),
               "excess_fw_c": r["fw_c"] - min(near)})
bins = [(0.0, 0.75), (0.75, 1.0), (1.0, 2.0), (2.0, 4.0), (4.0, 1e9)]
by_bin = {}
for lo, hi in bins:
    sel = [x for x in by if lo <= x["rest_h"] < hi]
    by_bin[f"{lo}-{hi if hi < 1e8 else 'inf'} h"] = {
        "n": len(sel), "excess_fw_max": max((x["excess_fw_c"] for x in sel), default=None),
        "n_excess_ge_2C": sum(1 for x in sel if x["excess_fw_c"] >= 2.0),
        "sessions_excess_ge_2C": [(x["session"], round(x["rest_h"], 2), x["fw_c"], x["ref_settled_fw_min"]) for x in sel if x["excess_fw_c"] >= 2.0]}
m6 = {f"{h} h": 0.010 * 25.0 * math.exp(-h * 3600 / 1500.0) for h in (0.67, 1.0, 2.0)}
# (4) the loop gain at the raw-code floors by E97's law (A6's) and by FL1 (E44's and E71's cycles), each in its own coordinate
R = json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json")))["a3"]["R_total"]
q1 = json.load(open(os.path.join(TOP, "tools/claims-v3/footing-law/footing-law.json")))["laws"]["aifoundry3"]["quad_w"]
E97 = (0.006175439291277969, -0.3665903970069978)
OFF = fa["offset_m34_minus_fw"]["mean"]
loop = []
for r in rows:
    if r["floor_kind"].startswith("34"):
        T34 = r["floor_c"]
        loop.append({"session": r["start_pst"], "floor_m34_c": T34, "g_E97": R * (2 * E97[0] * T34 + E97[1]),
                     "T_fw_equiv": T34 - OFF, "g_FL1": R * (2 * q1[0] * (T34 - OFF) + q1[1])})
res = {"what": "Q145(a) aifoundry3 idle-floor study, dated note 1: G0 and G0-A6 on every November floor; the excess after a short rest (post hoc)",
       "november": nov, "summary": summary, "excess_by_rest_bin": by_bin, "excess_rows": by, "m6_slowest_pole_tail_c": m6,
       "loop_gain_at_raw_code_floors": {"R_c_per_w": R, "offset_used_c": OFF, "rows": loop}}
json.dump(res, open(OUT, "w"), indent=1, sort_keys=True)
print("November:", summary["november_sessions"], "sessions,", summary["settled_1h"], "settled (rest >= 1 h)")
print("  G0 passes", summary["G0_pass_all"], "of all,", summary["G0_pass_settled"], "of settled; G0-A6 passes", summary["G0_A6_pass_all"],
      "of all,", summary["G0_A6_pass_settled"], "of settled")
for x in summary["stopped_by_A6_1"]:
    print("  stopped by A6-1:", x["session"], "rest %.2f h" % x["rest_h"], "floor %.3f (%s), firmware %.0f" % (x["floor_c"], x["kind"][:3], x["fw_c"]))
print("  refused by G0:", summary["refused_by_G0"])
for k, v in by_bin.items():
    print("excess by rest", k, "n", v["n"], "max", v["excess_fw_max"], ">=2C:", v["sessions_excess_ge_2C"])
print("M6 slowest-pole tail:", {k: round(v, 3) for k, v in m6.items()})
for x in loop:
    print("loop gain at %s floor %.3f C: E97 %.3f, FL1 at firmware %.2f C %.3f" % (x["session"], x["floor_m34_c"], x["g_E97"], x["T_fw_equiv"], x["g_FL1"]))
