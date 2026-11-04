#!/usr/bin/env python3
"""Q141(t2): the self-test of the 243-point step's code, run before any 243-point count existed.

    /usr/bin/python3 -B selftest_step243.py > selftest-step243.txt

T0  run_recount_rule_243.py --selfcheck: main() on the committed 9-, 27- and 81-point counts alone rewrites step81/recount-rule.json
    and .txt byte for byte (so the wrapper adds nothing to the registered rule).
T1  bench_243.py's point sets: N = 81's points are exactly every third point of N = 243; the two parts are 81 points each, disjoint,
    and together the 162 points N = 81 does not hold; the step's check point (n0 272464, j = 120) is in part 1.
T2  the summary's three outcomes (REGISTRATION-step243.md section 3), on synthetic 243-point levels added to step81's committed
    recount-rule.json, never on counts: (a) all eight tiles meet the bound at 243 -> N* = 243, no F1, F2 not needed; (b)
    fp32.cal_third_b21 is above the bound at 243 -> N* "not reached by uniform points at the cap (243)", F1 on that tile with its
    243-point mean and e(243), F2 "not run here"; (c) one tile counted only to 81 -> N* "not yet determined: the step is incomplete",
    and that tile is named, never given F1.
T3  readings_243.py on world (b): G1's z, G2's ratio and G3 against the synthetic levels; G4's k243 = s x (3pt - 243) and u243
    = s x e(243) per card from arm-s7.json's card scale; G5 copied.
Every synthetic file is written in a temporary directory; nothing is written beside this file. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bench_243 as B  # noqa: E402
import run_recount_rule_243 as W  # noqa: E402

FAIL = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f": {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


# T0
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "run_recount_rule_243.py"), "--selfcheck", td],
                       capture_output=True, text=True)
    check("T0 the wrapper on the committed counts alone rewrites step81's output byte for byte", r.returncode == 0,
          r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:])

# T1
part = B.step_points()
p243, p81 = B.points(243), B.points(81)
check("T1 N = 81's points are every third point of N = 243 (j = 1 mod 3)", p243[1::3] == p81)
check("T1 the two parts: 81 + 81 points, disjoint, = the 162 points N = 81 does not hold",
      len(part[1]) == 81 and len(part[2]) == 81 and not set(part[1]) & set(part[2])
      and sorted(part[1] + part[2]) == sorted(set(p243) - set(p81)))
check("T1 the check point n0 272464 is j = 120 of N = 243, in part 1", p243[120] == 272464 and 272464 in part[1])

# T2
base = json.load(open(os.path.join(D, "step81", "recount-rule.json")))
RAT = {"fp32.cal_third_b21": 1.70, "fp32.cal_pi_b21": 1.75, "fp32.cal_third_b20": 1.80, "fp32.cal_w67_b21": 1.72,
       "fp32.cal_w79_b21": 1.74, "fp32.cal_w67_b20": 1.73, "fp32.cal_w79_b20": 1.76, "fp32.cal_pi_b20": 1.71}


def world(kind):
    r = copy.deepcopy(base)
    first = {}
    for n, t in r["tiles"].items():
        if t["first_N_meeting_bound"]:
            first[n] = t["first_N_meeting_bound"]
    for n, rat in RAT.items():
        t = r["tiles"][n]
        if kind == "c" and n == "fp32.cal_pi_b20":
            continue          # counted only to 81: the step cut short
        b81 = t["by_N"]["81"]
        e = b81["e_w"] / rat
        if kind == "a":
            e = min(e, 0.099)
        if kind in ("b", "c") and n == "fp32.cal_third_b21":
            e = 0.128
        if kind in ("b", "c") and n != "fp32.cal_third_b21":
            e = min(e, 0.099)
        lvl = {"mean_w": b81["mean_w"] + 0.01, "se_sample_w": e, "se_interleaved_w": e * 0.9, "e_w": e,
               "subrule_means_w": [b81["mean_w"]] * 3, "three_point_minus_N_w": b81["three_point_minus_N_w"] - 0.01,
               "met": e <= 0.10}
        t["by_N"]["243"] = lvl
        t["N_counted"] = 243
        if lvl["met"]:
            t["first_N_meeting_bound"] = 243
            first[n] = 243
            t["projected_N_by_inverse_sqrt_law"] = None
        else:
            t["first_N_meeting_bound"] = None
            t["projected_N_by_inverse_sqrt_law"] = int(math.ceil(243 * (e / 0.10) ** 2))
    unmet = [n for n in r["tiles"] if n not in first]
    r["N_star"] = max(first.values()) if not unmet else None
    r["tiles_not_yet_meeting_bound"] = unmet
    return r


def summarize(r):
    td = tempfile.mkdtemp()
    json.dump(r, open(os.path.join(td, "recount-rule.json"), "w"))
    json.dump({"exit": 0, "points": 81, "jobs": 4, "wall_s": 160.0, "machine": {"arch": "arm64", "system": "Darwin"}},
              open(os.path.join(td, "counts-cal243-third_b21-p1-run.json"), "w"))
    W.HERE = td
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        W.summary()
    s = json.load(open(os.path.join(td, "summary243.json")))
    return td, s


tda, sa = summarize(world("a"))
check("T2a all eight meet at 243 -> N* = 243, no F1, F2 not needed",
      sa["N_star"] == 243 and not sa["F1_applies_to"] and sa["F2"] == "not needed for the calibration set"
      and all(sa["tiles"][n]["outcome"] == "met at 243" for n in RAT), f"N* {sa['N_star']}")
tdb, sb = summarize(world("b"))
f1 = sb["tiles"]["fp32.cal_third_b21"].get("F1_known_counting_error", {})
check("T2b cal_third_b21 above the bound at 243 -> N* not reached at the cap, F1 on it alone, F2 not run here",
      sb["N_star"] == "not reached by uniform points at the cap (243)" and sb["F1_applies_to"] == ["fp32.cal_third_b21"]
      and abs(f1.get("e_w", 0) - 0.128) < 1e-12 and sb["F2"].startswith("not run here") and sb["recount_cap_N"] == 243,
      f"N* {sb['N_star']!r}; F1 {sb['F1_applies_to']}")
tdc, sc = summarize(world("c"))
check("T2c one tile counted only to 81 -> N* not yet determined (incomplete), that tile named and never given F1",
      sc["N_star"] == "not yet determined: the step is incomplete" and sc["tiles_not_counted_to_cap"] == ["fp32.cal_pi_b20"]
      and "fp32.cal_pi_b20" not in sc["F1_applies_to"], f"N* {sc['N_star']!r}; short {sc['tiles_not_counted_to_cap']}")

# T3
with tempfile.TemporaryDirectory() as td:
    os.makedirs(os.path.join(td, "step243"))
    shutil.copy(os.path.join(HERE, "readings_243.py"), os.path.join(td, "step243"))
    shutil.copy(os.path.join(D, "arm-s7.json"), td)
    shutil.copy(os.path.join(tdb, "recount-rule.json"), os.path.join(td, "step243"))
    r = subprocess.run([sys.executable, "-B", os.path.join(td, "step243", "readings_243.py")], capture_output=True, text=True)
    g = json.load(open(os.path.join(td, "step243", "readings-243.json"))) if r.returncode == 0 else {}
rb = world("b")
arm = json.load(open(os.path.join(D, "arm-s7.json")))
ok = r.returncode == 0
if ok:
    t = rb["tiles"]["fp32.cal_third_b21"]["by_N"]
    z = (t["81"]["mean_w"] - t["243"]["mean_w"]) / math.sqrt(t["81"]["e_w"] ** 2 - t["243"]["e_w"] ** 2)
    ok &= abs(g["G1_move_81_to_243"]["fp32.cal_third_b21"]["z"] - z) < 1e-12
    ok &= abs(g["G2_ratio"]["fp32.cal_third_b21"] - t["81"]["e_w"] / t["243"]["e_w"]) < 1e-12
    pb = rb["tiles"]["fp32.cal_pi_b20"]["by_N"]["243"]
    for card in ("aifoundry3", "aifoundry1c1"):
        s = 1.0 if card == "aifoundry3" else arm["cards"]["aifoundry1c1"]["fp32.b_onebit_b20_pi"]["card_scale"]
        a = arm["cards"][card]["fp32.b_onebit_b20_pi"]
        ok &= abs(g["G4_arm_b20_pi"][card]["k243_w"] - round(s * pb["three_point_minus_N_w"], 4)) < 1e-12
        ok &= abs(g["G4_arm_b20_pi"][card]["u243_w"] - round(s * pb["e_w"], 4)) < 1e-12
        ok &= abs(g["G4_arm_b20_pi"][card]["P243_w"] - round(a["P3_w"] - s * pb["three_point_minus_N_w"], 4)) < 1e-12
    ok &= g["G5_pool6_twins"] == rb.get("posthoc_pool6_twins")
check("T3 readings_243.py: G1 z, G2 ratio, G4 k243/u243/P243 on both cards and G5, against independent sums", ok,
      "" if r.returncode == 0 else r.stderr[-200:])
for d in (tda, tdb, tdc):
    shutil.rmtree(d, ignore_errors=True)
print(f"\nSELFTEST {'PASS' if not FAIL else 'FAIL: ' + ', '.join(FAIL)} ({sys.executable.rsplit('/', 1)[-1]} "
      f"{sys.version.split()[0]})")
sys.exit(1 if FAIL else 0)
