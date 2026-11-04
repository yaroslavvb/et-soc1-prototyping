#!/usr/bin/env python3
"""Q141(t), REGISTRATION.md section 4: the convergence rule's 81-point step, scored by Q140(m)'s recount_rule.py main(), unchanged,
with its output directory pointed here (its module-level HERE), on the committed nine- and 27-point counts and this step's counts:

    /usr/bin/python3 -B run_recount_rule.py      # writes recount-rule.json and recount-rule.txt here, then summary81.json / .txt

Inputs: ../../2026-11-04-q140m-m9/bench-check/counts-cal.json, ../../2026-11-04-q140m-m9/recount-rule/counts-pilot27.json and
counts-cal81-<n>.json beside this file. main() stops on a point counted twice with different nets or a C mismatch. Its cost lines
read a pilot-run.json beside its output, which this directory does not have, so summary81 adds this step's own bench time.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
M9D = os.path.abspath(os.path.join(HERE, "..", "..", "2026-11-04-q140m-m9"))
RRD = os.path.join(M9D, "recount-rule")
sys.path.insert(0, RRD)
import recount_rule as RR  # noqa: E402

files = [os.path.join(M9D, "bench-check", "counts-cal.json"), os.path.join(RRD, "counts-pilot27.json")] + sorted(
    glob.glob(os.path.join(HERE, "counts-cal81-[0-9].json")))
RR.HERE = HERE
sys.argv = [os.path.join(RRD, "recount_rule.py")] + files
RR.main()

# summary81: e(9), e(27), e(81) per tile, the measured ratio e(27)/e(81) beside the 1/sqrt(N) law's sqrt(3), and the bench time
r = json.load(open(os.path.join(HERE, "recount-rule.json")))
runs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(HERE, "counts-cal81-[0-9]-run.json")))]
pts = sum(x["points"] for x in runs if x.get("exit") == 0)
core_s = sum(x["wall_s"] * x["jobs"] for x in runs if x.get("exit") == 0)
sec = core_s / pts if pts else None
S = {"_note": "Q141(t) step 3: the convergence rule's 81-point step (REGISTRATION.md section 4), from recount-rule.json beside this file",
     "bound_w": r["bound_w"], "N_star": r["N_star"], "tiles_not_yet_meeting_bound": r["tiles_not_yet_meeting_bound"],
     "next_step": r["next_step"], "tiles": {}, "bench": {"runs": len(runs), "points": pts, "core_seconds": core_s,
                                                          "seconds_per_point_one_core": sec,
                                                          "wall_s": sum(x["wall_s"] for x in runs)}}
L = ["Q141(t) step 3: the convergence rule's 81-point step, by recount_rule.py's main() (recount-rule.json, .txt beside this file)", "",
     f"{'tile':20s} {'e(9)':>6s} {'e(27)':>6s} {'e(81)':>6s} {'e27/e81':>7s}  first N met   projected N (1/sqrt N, planning)"]
for name, t in r["tiles"].items():
    e = {n: t["by_N"][n]["e_w"] for n in t["by_N"]}
    rat = (e["27"] / e["81"]) if ("27" in e and "81" in e) else None
    S["tiles"][name] = {"e_w": e, "N_counted": t["N_counted"], "first_N_meeting_bound": t["first_N_meeting_bound"],
                        "e27_over_e81": rat, "projected_N_by_inverse_sqrt_law": t["projected_N_by_inverse_sqrt_law"]}
    cells = " ".join(f"{e[n]:6.3f}" if n in e else f"{'-':>6s}" for n in ("9", "27", "81"))
    rs = f"{rat:7.2f}" if rat else f"{'-':>7s}"
    L.append(f"{name:20s} {cells} {rs}  {str(t['first_N_meeting_bound'] or 'not yet'):>11s}   "
             f"{t['projected_N_by_inverse_sqrt_law'] or '-'}")
rats = [v["e27_over_e81"] for v in S["tiles"].values() if v["e27_over_e81"]]
if rats:
    S["e27_over_e81_range"] = [min(rats), max(rats)]
    S["e27_over_e81_median"] = sorted(rats)[len(rats) // 2]
if sec:
    unmet = r["tiles_not_yet_meeting_bound"]
    S["cost_243_step_bench_hours_at_4_jobs"] = len(unmet) * (243 - 81) * sec / 4 / 3600
L += ["", f"N* = {r['N_star'] or 'not yet determined'}; tiles above the bound: {len(r['tiles_not_yet_meeting_bound'])} of 16"]
if rats:
    L.append(f"e(27)/e(81) over the tiles counted at 81: {min(rats):.2f}-{max(rats):.2f} (median {S['e27_over_e81_median']:.2f}; "
             f"the 1/sqrt(N) law gives {math.sqrt(3):.2f})")
if sec:
    L.append(f"bench: {pts} points in {S['bench']['wall_s']:.0f} s of wall time over {len(runs)} runs, {sec:.1f} s a point on one core; "
             f"the 243-point step for the tiles still above the bound: {S['cost_243_step_bench_hours_at_4_jobs']:.2f} bench-hours at 4 jobs")
json.dump(S, open(os.path.join(HERE, "summary81.json"), "w"), indent=1, sort_keys=True)
open(os.path.join(HERE, "summary81.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
