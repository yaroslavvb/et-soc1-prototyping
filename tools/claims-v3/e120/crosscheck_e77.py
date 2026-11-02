#!/usr/bin/env python3
"""E120's reduction code run on E77's committed raw data, with E77's hart counts, against E77's committed numbers.
Written before E120's claim: it checks the new fit code (the offset form, the bound, the arms' lines and steps, E77's
registered form) reproduces what E77 committed, so the registered reading is the post hoc one it says it is.

    /usr/bin/python3 tools/claims-v3/e120/crosscheck_e77.py > tools/claims-v3/e120/crosscheck_e77.txt
"""
import collections
import importlib.util
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E77 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e77-rail-one-temperature")
spec = importlib.util.spec_from_file_location("r120", os.path.join(HERE, "reduce_e120.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.HARTS = {("A", 1): 1024, ("A", 2): 768, ("A", 3): 544, ("A", 4): 288,
           ("B", 1): 544, ("B", 2): 416, ("B", 3): 288, ("B", 4): 160}
drops = collections.Counter()
rows, tels = m.launch_rows(os.path.join(E77, "raw"), drops)
dr = m.block_drift(rows)
sr = m.settling_ratio(rows, tels, dr)
c = m.with_arm(m.rung_means(rows, "drift_split", dr, sr))
ph = json.load(open(os.path.join(E77, "posthoc.json")))
res = json.load(open(os.path.join(E77, "results.json")))
ok = True


def check(label, got, want, tol):
    global ok
    good = abs(got - want) <= tol
    ok &= good
    print(f"{'MATCH' if good else 'DIFFERS'}  {label}: E120 code {got:.4f}, E77 committed {want:.4f} (tolerance {tol})")


v = m.verdict_v(c, "offset")
for k in ("1", "2", "3"):
    check(f"offset form, pass {k} R_eff mOhm", 1000 * v["per_pass"][k]["R_eff_ohm"], ph["fit_offset"]["per_pass"][k]["R_mohm"], 1e-6)
check("offset form, 99% low mOhm", 1000 * v["R_ci99_ohm"][0], ph["fit_offset"]["R_ci99_mohm"][0], 1e-6)
check("offset form, 99% high mOhm", 1000 * v["R_ci99_ohm"][1], ph["fit_offset"]["R_ci99_mohm"][1], 1e-6)
check("offset form, rms improvement", v["rms_improvement"], ph["fit_offset"]["rms_improvement"], 1e-9)
mA = [x for k, x in c.items() if k[0] == "A"]
b = m.bound(v, float(np.mean([x["m0"] for x in mA])), float(np.mean([x["V"] for x in mA])))
check("bound at the 99% high edge, total-current W (corrections-check.txt C: 1.37)", b["at_ci_high"]["total_current_w"], 1.37, 0.005)
check("bound at the 99% high edge, total-current pJ (corrections-check.txt C: 0.30)", b["at_ci_high"]["total_current_pJ"], 0.30, 0.005)
check("bound at the 99% high edge, literal pJ (corrections-check.txt C: 0.18)", b["at_ci_high"]["literal_pJ"], 0.18, 0.005)
e = m.verdict_for_e77(c)
check("E77's registered form, 99% low mOhm", 1000 * e["R_ci99_ohm"][0], 1000 * res["footings"]["drift_split"]["fit"]["R_ci99_ohm"][0], 1e-6)
check("E77's registered form, 99% high mOhm", 1000 * e["R_ci99_ohm"][1], 1000 * res["footings"]["drift_split"]["fit"]["R_ci99_ohm"][1], 1e-6)
L = m.arm_lines(c)
ratios = [L[("B", p)]["mw_per_hart"] / L[("A", p)]["mw_per_hart"] for p in (1, 2, 3)]
steps = [L[("B", p)]["intercept_w"] - L[("A", p)]["intercept_w"] for p in (1, 2, 3)]
srams = [L[("B", p)]["sram_mean_w"] - L[("A", p)]["sram_mean_w"] for p in (1, 2, 3)]
print("per pass: slope ratio", [round(x, 4) for x in ratios], "minion step W", [round(x, 3) for x in steps],
      "SRAM step W", [round(x, 3) for x in srams])
check("per-hart ratio, mean of passes (posthoc.json pools the rung means: 1.9235)", float(np.mean(ratios)), ph["per_hart_ratio_B_over_A"], 0.005)
check("minion step W, mean of passes (posthoc.json: 4.0950)", float(np.mean(steps)), ph["op_step_minion_w"], 0.005)
check("SRAM step W, mean of passes (posthoc.json: 1.7347)", float(np.mean(srams)), ph["op_step_sram_w"], 0.005)
print("ALL MATCH" if ok else "SOME DIFFER")
