#!/usr/bin/env python3
"""E120 post hoc (labelled so; no verdict; written after the registered reduction, Sun 1 Nov 2026 ~21:25 PST).
How late arm B reached 800 MHz in each launch, and the registered offset fit with late-stepping launches left out
(the service processor's rails are the PMIC's running average, tau about 1.06 s, while the board reading is not, so a
launch that reaches 800 MHz late reads its minion rail low in the window and its off-rail high).

    /usr/bin/python3 docs/reports/data/2026-11-01-e120-rail-redesign/posthoc_e120.py > .../posthoc.txt
"""
import collections, importlib.util, json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
spec = importlib.util.spec_from_file_location("r120", os.path.join(ROOT, "tools/claims-v3/e120/reduce_e120.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
drops = collections.Counter()
rows, tels = m.launch_rows(os.path.join(HERE, "raw"), drops)
dr = m.block_drift(rows); sr = m.settling_ratio(rows, tels, dr)
B = [r for r in rows if r.get("kept") and r["role"] == "work" and r["arm"] == "B"]
f8 = sorted(r["first_800_s"] for r in B)
print("arm B kept launches:", len(B), "; first 800 MHz sample, s after launch: min %.2f median %.2f max %.2f" % (f8[0], np.median(f8), f8[-1]))
print("  over 1.26 s (E77's latest):", [(r["name"], round(r["first_800_s"], 2)) for r in B if r["first_800_s"] > 1.26])
mA = [r for r in rows if r.get("kept") and r["role"] == "work" and r["arm"] == "A"]
for cut in (None, 1.5, 1.26):
    keep = [r for r in rows if not (r.get("kept") and r["role"] == "work" and r["arm"] == "B" and cut is not None and r["first_800_s"] > cut)]
    c = m.with_arm(m.rung_means(keep, "drift_split", dr, sr))
    v = m.verdict_v(c, "offset")
    a = [x for k, x in c.items() if k[0] == "A"]
    b = m.bound(v, float(np.mean([x["m0"] for x in a])), float(np.mean([x["V"] for x in a])))
    lab = "registered (all kept)" if cut is None else f"arm B launches stepping later than {cut} s left out"
    print(f"{lab}: per pass mOhm", {k: round(1000 * f['R_eff_ohm'], 3) for k, f in v["per_pass"].items()},
          "mean %.3f, 99%% [%.3f, %.3f], rms improvement %.3f, %s; upper edge %.2f W = %.3f pJ total-current" % (
          1000 * v["R_mean_ohm"], 1000 * v["R_ci99_ohm"][0], 1000 * v["R_ci99_ohm"][1], v["rms_improvement"], v["verdict"],
          b["at_ci_high"]["total_current_w"], b["at_ci_high"]["total_current_pJ"]))
# all five registered per-pass values positive: a sign count (post hoc)
c = m.with_arm(m.rung_means(rows, "drift_split", dr, sr))
v = m.verdict_v(c, "offset")
pos = sum(1 for f in v["per_pass"].values() if f["R_eff_ohm"] > 0)
print(f"registered per-pass R_eff positive in {pos} of {len(v['per_pass'])} passes (one-sided sign test p = {0.5 ** len(v['per_pass']):.3f} if all, post hoc)")
tq95 = {4: 2.776}[len(v["per_pass"]) - 1]
h = tq95 * v["R_sd_ohm"] / np.sqrt(len(v["per_pass"]))
print("the same five passes at 95%% (not the registered level): [%.3f, %.3f] mOhm" % (1000 * (v["R_mean_ohm"] - h), 1000 * (v["R_mean_ohm"] + h)))
