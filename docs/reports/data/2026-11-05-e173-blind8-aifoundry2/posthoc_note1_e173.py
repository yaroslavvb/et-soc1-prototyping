#!/usr/bin/env python3
"""E173's dated note 1 (README.md.dated-note-1.md, Thu 5 Nov 2026, week 45, PST): the figures of its sections 3, 4 and 5, recomputed from the
committed results.json beside this file and the look's uptime line, with no scorer import. Written in the E173 card lane's fix pass, after the
data commit (ed8b5761) and the README fix (571d0482). Post hoc: no rule, line, verdict or prediction changes, and nothing here is a re-score.

    python3 -I docs/reports/data/2026-11-05-e173-blind8-aifoundry2/posthoc_note1_e173.py [<results.json>]

  [4] each scored pinned tile with a counted pass under 800 MHz: its board error against M10 carried (the mean of its counted passes less
      M10 carried's burst_board_w, as score.reported.tiles gives both), the error of its 800 MHz passes alone, and the share the dipped
      passes take; the pinned clock rms with and without those tiles (P8-A2-F2's form);
  [5] M1's paired difference, what it is made of: d = M10 carried - M9's part per scored tile, on the board; rms(a)^2 - rms(b)^2 with
      a = measured - M10 carried, b = measured - M9's part (so a = b - d), and the part a constant offset at d's mean would give;
  [3] the boot time from the look's uptime line (11:36:02 PST, 'up 9 days, 21:22') and uptime -s's 2026-10-26 15:13:03, read in PDT.
It prints no path. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import datetime as dt
import json
import math
import os
import sys

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
r = json.load(open(path))
S = r["score"]
T = S["reported"]["tiles"]
scored = set(S["governed"]) | set(S["pinned"])
assert len(scored) == S["tiles_scored"], (len(scored), S["tiles_scored"])
by = {}
for x in r["run_rows"]:
    if not x.get("counted"):
        continue
    lab = x["label"][3:] if x["label"].startswith("b8-") else x["label"]
    if lab in scored:
        by.setdefault(lab, []).append(x)


def rms(v):
    return math.sqrt(sum(e * e for e in v) / len(v))


def mean(v):
    return sum(v) / len(v)


print("E173 dated note 1, post hoc figures from results.json (no scorer import)")
print(f"scored tiles {len(scored)}: governed {len(S['governed'])}, pinned {len(S['pinned'])}; counted passes on them {sum(len(v) for v in by.values())}")

print("\n[4] pinned tiles with a counted pass under 800 MHz (board error = mean of the counted passes - M10 carried's burst_board_w):")
dipped = []
for t in sorted(S["pinned"]):
    xs = sorted(by[t], key=lambda z: z["pass"])
    if min(x["burst_mhz"] for x in xs) >= 800:
        continue
    pred = T[t]["M10"]["burst_board_w"]
    e_all = mean([x["burst_w"] for x in xs]) - pred
    e800 = mean([x["burst_w"] for x in xs if x["burst_mhz"] >= 800]) - pred
    dipped.append(t)
    print(f"  {t}: passes (pass, MHz, W) {[(x['pass'], x['burst_mhz'], x['burst_w']) for x in xs]}; M10 carried {pred:.3f} W; "
          f"error {e_all:+.3f} W (the tile's mean in results.json: {T[t]['burst_w'] - pred:+.3f}); its 800 MHz passes alone {e800:+.3f} W; "
          f"the dipped passes' share {e_all - e800:+.3f} W")
ce = [T[t]["burst_mhz"] - T[t]["M10"]["burst_mhz"] for t in S["pinned"]]
ce_rest = [T[t]["burst_mhz"] - T[t]["M10"]["burst_mhz"] for t in S["pinned"] if t not in dipped]
print(f"  the pinned clock rms over {len(ce)} tiles: {rms(ce):.4f} MHz; over the {len(ce_rest)} with no dipped pass: {rms(ce_rest):.4f} MHz")

print("\n[5] M1's paired difference: d = M10 carried - M9's part, board prediction per scored tile:")
for grp in ("governed", "pinned", "all"):
    ts = sorted(scored) if grp == "all" else sorted(S[grp])
    d = [T[t]["M10"]["burst_board_w"] - T[t]["M9"]["burst_board_w"] for t in ts]
    a = [T[t]["burst_w"] - T[t]["M10"]["burst_board_w"] for t in ts]
    b = [T[t]["burst_w"] - T[t]["M9"]["burst_board_w"] for t in ts]
    sd = math.sqrt(sum((x - mean(d)) ** 2 for x in d) / (len(d) - 1))
    print(f"  {grp:8s} n {len(ts):2d}: d mean {mean(d):+.4f} W, sd {sd:.4f}, min {min(d):+.4f}, max {max(d):+.4f}; "
          f"{sum(1 for x in d if x < 0)} negative, {sum(1 for x in d if x > 0)} positive; error mean M10 {mean(a):+.4f} W, M9 {mean(b):+.4f} W; "
          f"rms M10 {rms(a):.4f}, M9 {rms(b):.4f}")
ts = sorted(scored)
d = {t: T[t]["M10"]["burst_board_w"] - T[t]["M9"]["burst_board_w"] for t in ts}
order = sorted(ts, key=lambda t: d[t])
print("  the five lowest d: " + ", ".join(f"{t} {d[t]:+.3f}" for t in order[:5]))
print("  the five highest d: " + ", ".join(f"{t} {d[t]:+.3f}" for t in order[-5:]))
cases = {}
for t in ts:
    cases.setdefault(str(T[t].get("case")), []).append(d[t])
print("  d by case: " + "; ".join(f"{c} n {len(v)} mean {mean(v):+.3f} (|d| largest {max(abs(x) for x in v):.3f})" for c, v in sorted(cases.items())))
a = [T[t]["burst_w"] - T[t]["M10"]["burst_board_w"] for t in ts]
b = [T[t]["burst_w"] - T[t]["M9"]["burst_board_w"] for t in ts]
lhs = rms(a) ** 2 - rms(b) ** 2
rhs = mean([-d[t] * (2 * bb - d[t]) for t, bb in zip(ts, b)])
cm = mean([d[t] for t in ts])
lvl = mean([-cm * (2 * bb - cm) for bb in b])
print(f"  rms(a)^2 - rms(b)^2 = {lhs:+.5f} W^2 (the identity mean(-d (2b - d)): {rhs:+.5f}); with every d set to its mean {cm:+.4f} W: "
      f"{lvl:+.5f} W^2 (what a constant offset gives through the session's mean error, {mean(b):+.4f} W); rms(a) - rms(b) = {rms(a) - rms(b):+.4f} W")

print("\n[3] the boot time:")
pst = dt.timezone(dt.timedelta(hours=-8), "PST")
pdt = dt.timezone(dt.timedelta(hours=-7), "PDT")
look = dt.datetime(2026, 11, 5, 11, 36, 2, tzinfo=pst)
boot = look - dt.timedelta(days=9, hours=21, minutes=22)
print(f"  11:36:02 PST less 'up 9 days, 21:22' = {boot.astimezone(dt.timezone.utc):%Y-%m-%d %H:%M} UTC = {boot.astimezone(pdt):%H:%M} PDT "
      f"= {boot.astimezone(pst):%H:%M} PST (to uptime's minute)")
b2 = dt.datetime(2026, 10, 26, 15, 13, 3, tzinfo=pdt)
fw = dt.datetime(2026, 10, 27, 13, 56, 26, tzinfo=pdt)
print(f"  uptime -s's 2026-10-26 15:13:03 in PDT = {b2.astimezone(pst):%H:%M:%S} PST = {b2.astimezone(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC; "
      f"E69's firmware read (2026-10-27 13:56:26 PDT) is {(fw - b2).total_seconds() / 3600:.2f} h after it "
      f"({(fw - b2.replace(tzinfo=pst)).total_seconds() / 3600:.2f} h if the boot were read as PST)")
