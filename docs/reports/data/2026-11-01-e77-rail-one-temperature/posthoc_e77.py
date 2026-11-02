"""E77 post hoc (labelled so; no verdict; written after the run, Sun 1 Nov 2026): the arms' minion-rail law against harts, the operating-point step, and the
conduction fit with an arm-B offset. Reads results.json (the registered reduction's rung means).
    /usr/bin/python3 posthoc_e77.py results.json > posthoc.json"""
import json, math, sys
import numpy as np
R = json.load(open(sys.argv[1]))
rm = R["footings"]["drift_split"]["rung_means"]
H = {"A": {1: 1024, 2: 768, 3: 544, 4: 288}, "B": {1: 544, 2: 416, 3: 288, 4: 160}}
T995 = {1: 63.657, 2: 9.925, 3: 5.841}
out = {}
for arm in ("A", "B"):
    xs, ys, ss, vs = [], [], [], []
    for k, v in rm.items():
        if k[0] == arm:
            g = int(k.split("-g")[1]); xs.append(H[arm][g]); ys.append(v["minion"]); ss.append(v["sram"]); vs.append(v["V"])
    sl, ic = np.polyfit(xs, ys, 1)
    res = np.array(ys) - (sl * np.array(xs) + ic)
    out[arm] = {"mW_per_hart": 1000 * sl, "intercept_w": ic, "rms_w": float(np.sqrt(np.mean(res ** 2))),
                "sram_mean_w": float(np.mean(ss)), "V_mean": float(np.mean(vs)), "n": len(xs)}
out["per_hart_ratio_B_over_A"] = out["B"]["mW_per_hart"] / out["A"]["mW_per_hart"]
out["fV2_measured"] = (800 / 600) * (out["B"]["V_mean"] / out["A"]["V_mean"]) ** 2
out["op_step_minion_w"] = out["B"]["intercept_w"] - out["A"]["intercept_w"]
out["op_step_sram_w"] = out["B"]["sram_mean_w"] - out["A"]["sram_mean_w"]
# conduction fit with an arm-B offset, per pass: offrail = a_m dm + c_B [B] + R ((m0+dm)/V)^2 - (m0/V0)^2
def fitp(pts, with_R=True, small=False):
    m = np.array([p["minion"] for p in pts]); V = np.array([p["V"] for p in pts]); V0 = np.array([p["V0"] for p in pts])
    m0 = np.array([p["m0"] for p in pts]); y = np.array([p["offrail"] for p in pts]); b = np.array([p["B"] for p in pts])
    cols = [m, b]
    if small:
        cols += [np.array([p["sram"] for p in pts]), np.array([p["noc"] for p in pts])]
    if with_R:
        cols.append(((m0 + m) / V) ** 2 - (m0 / V0) ** 2)
    X = np.vstack(cols).T
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ c
    return c, float(np.sqrt(np.mean(r ** 2))), float(np.linalg.cond(X))
for label, small in (("offset", False), ("offset_plus_small_rails", True)):
    Rs, per = [], {}
    for p in ("1", "2", "3"):
        pts = [dict(v, B=1.0 if k[0] == "B" else 0.0) for k, v in rm.items() if k[1] == p]
        c, rms, cond = fitp(pts, small=small)
        Rs.append(c[-1]); per[p] = {"R_mohm": 1000 * c[-1], "a_m": c[0], "c_B_w": c[1], "rms": rms, "cond": cond}
    m, sd = float(np.mean(Rs)), float(np.std(Rs, ddof=1))
    lo, hi = m - T995[2] * sd / math.sqrt(3), m + T995[2] * sd / math.sqrt(3)
    allp = [dict(v, B=1.0 if k[0] == "B" else 0.0) for k, v in rm.items()]
    cw, rw, _ = fitp(allp, small=small); cwo, rwo, _ = fitp(allp, with_R=False, small=small)
    I = 21.0 / out["A"]["V_mean"]
    out[f"fit_{label}"] = {"per_pass": per, "R_mean_mohm": 1000 * m, "R_ci99_mohm": [1000 * lo, 1000 * hi],
                           "rms_improvement": 1 - rw / rwo, "pooled_R_mohm": 1000 * cw[-1],
                           "loss_at_21W_ci99_w": [lo * I * I, hi * I * I],
                           "pJ_of_0875_ci99": [0.875 * lo * I * I / (0.18789 * 21), 0.875 * hi * I * I / (0.18789 * 21)]}
print(json.dumps(out, indent=1))
