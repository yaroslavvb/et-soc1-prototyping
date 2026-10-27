#!/usr/bin/env python3
"""E66 (Q128(b)): the fixed/leakage split of aifoundry2's idle power over 51-67 C, and L1-L4.

    python3 tools/claims-v3/idle/e66_split.py --data build/claims-v3/aifoundry2/idle \
        --passes 11,12,13,14,15 --out e66-split.json

L5 (IDLE-d) is scored by the stock reduction, not here:
    python3 tools/claims-v3/idle/reduce.py --data build/claims-v3 --out verdicts.json

Per cycle this fits P(T) = B + A80 * exp((T - 80) / T_L) to the cooling samples, binned to whole degrees of
`temp_c.minshire[0]` with at least 20 samples a bin, dropping every sample from 1 s before to 6 s after any
heater launch and the first 20 s of the pass (flip_thermal_model.py step 2a's rule, which IDLE-L registers),
and any sample off 600 MHz. The three parameters are fitted by least squares on the bin means, T_L on a grid
of 16-80 C with B and A80 solved linearly at each T_L, as step 2a does.

Then, for the band Q128(b) asks for, leakage share = A80 * exp((T - 80) / T_L) / P(T) at 51 C and at 67 C.
The published law (2026-09-21-horace-aifoundry2/model.json) is B = 12.6349 W, A80 = 23.2568 W, T_L = 36 C,
which gives 0.452 at 51 C and 0.562 at 67 C.
"""
import argparse
import glob
import gzip
import json
import os

import numpy as np

LAW = {"B_W": 12.6349, "A80_W": 23.2568, "T_L_C": 36.0}
BANDS = {"L1_T_L": (30.0, 45.0), "L1_T_L_ci_half_width_max": 8.0,
         "L2_A80": (19.0, 29.0), "L2_A80_ci_half_width_max": 3.0, "L2_B": (9.0, 16.0),
         "L3_share51": (0.38, 0.52), "L3_share67": (0.49, 0.63), "L3_rise": (0.06, 0.16),
         "L4_floor_c": 53.0}


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    for line in op(path, "rt"):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def cooling_bins(d):
    """Whole-degree bins of the cooling window: (temps, mean board W, n), and the lowest reading reached."""
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    if not tel:
        return None
    t = np.array([s["t_ms"] for s in tel], float)
    P = np.array([s["board_w"] for s in tel], float)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel], float)
    mhz = np.array([s["mhz"]["minion"] for s in tel], float)
    marks = {m.get("ev"): m for m in load_jsonl(os.path.join(d, "marks.jsonl"))}   # the idle block keys its marks "ev"
    if "cool_start" not in marks or "cool_end" not in marks:
        return None
    t0, t1 = marks["cool_start"]["t_ms"], marks["cool_end"]["t_ms"]
    keep = (t >= t0 + 20000) & (t <= t1) & (mhz == 600)
    for L in load_jsonl(os.path.join(d, "launches.jsonl")):
        keep &= ~((t >= L["t_start_ms"] - 4500) & (t <= L["t_end_ms"] + 4500))
    T, P = T[keep], P[keep]
    if len(T) < 200:
        return None
    xs, ys, ns = [], [], []
    for deg in range(int(T.min()), int(T.max()) + 1):
        m = (T >= deg) & (T < deg + 1)
        if m.sum() >= 20:
            xs.append(deg + 0.5)
            ys.append(float(P[m].mean()))
            ns.append(int(m.sum()))
    return (np.array(xs), np.array(ys), np.array(ns), float(T.min())) if len(xs) >= 4 else None


def fit_cycle(x, y):
    """Least squares on the bin means: T_L on a grid, B and A80 linear at each T_L (step 2a)."""
    best = None
    for T_L in np.arange(16.0, 80.01, 0.25):
        E = np.exp((x - 80.0) / T_L)
        M = np.vstack([np.ones_like(x), E]).T
        c, *_ = np.linalg.lstsq(M, y, rcond=None)
        r = float(np.sqrt(np.mean((y - M @ c) ** 2)))
        if best is None or r < best[0]:
            best = (r, float(T_L), float(c[0]), float(c[1]))
    return {"rms_W": best[0], "T_L_C": best[1], "B_W": best[2], "A80_W": best[3]}


def share(p, T):
    leak = p["A80_W"] * np.exp((T - 80.0) / p["T_L_C"])
    return float(leak / (p["B_W"] + leak))


def ci99(v):
    v = [x for x in v if x is not None]
    if len(v) < 2:
        return (float(np.mean(v)) if v else None), None, None, len(v)
    m, s = float(np.mean(v)), float(np.std(v, ddof=1) / np.sqrt(len(v)))
    # two-sided 99% t, small-n table
    tt = {2: 63.657, 3: 9.925, 4: 5.841, 5: 4.604, 6: 4.032, 7: 3.707, 8: 3.499, 9: 3.355, 10: 3.250}
    t = tt.get(len(v), 3.0)
    return m, m - t * s, m + t * s, len(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="$DATA_ROOT/idle")
    ap.add_argument("--passes", default="", help="comma-separated pass numbers; default every p1[1-9]")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.passes:
        dirs = [os.path.join(a.data, f"p{p.strip()}") for p in a.passes.split(",")]
    else:
        dirs = sorted(glob.glob(os.path.join(a.data, "p1[1-9]")))
    cycles, floors, dropped = [], [], []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        # A pass is kept when its block.json says ok; older idle passes carry no block.json, and for those a
        # recorded cool_end is the completion marker (an aborted cycle never writes one).
        bj = os.path.join(d, "block.json")
        if os.path.exists(bj):
            if '"status":"ok"' not in open(bj).read().replace(" ", ""):
                dropped.append((os.path.basename(d), "block.json not ok"))
                continue
        elif not any(m.get("ev") == "cool_end" for m in load_jsonl(os.path.join(d, "marks.jsonl"))):
            dropped.append((os.path.basename(d), "no block.json and no cool_end mark"))
            continue
        b = cooling_bins(d)
        if b is None:
            dropped.append((os.path.basename(d), "too few cooling bins"))
            continue
        x, y, n, lo = b
        p = fit_cycle(x, y)
        p.update({"pass": os.path.basename(d), "bins": len(x), "lowest_C": lo,
                  "share51": share(p, 51.0), "share67": share(p, 67.0)})
        p["rise"] = p["share67"] - p["share51"]
        cycles.append(p)
        floors.append(lo)
        print(f"{p['pass']:6s} bins {len(x):3d}  T_L {p['T_L_C']:6.2f} C  B {p['B_W']:6.2f} W  "
              f"A80 {p['A80_W']:6.2f} W  rms {p['rms_W']:.3f}  floor {lo:.1f} C  "
              f"share 51C {p['share51']:.3f} / 67C {p['share67']:.3f}")
    if not cycles:
        print("no kept cycles")
        json.dump({"cycles": [], "dropped": dropped}, open(a.out, "w"), indent=1)
        return
    V = {}
    for key, field, band in (("L1", "T_L_C", BANDS["L1_T_L"]), ("L2a", "A80_W", BANDS["L2_A80"]),
                             ("L2b", "B_W", BANDS["L2_B"]), ("L3a", "share51", BANDS["L3_share51"]),
                             ("L3b", "share67", BANDS["L3_share67"]), ("L3c", "rise", BANDS["L3_rise"])):
        m, lo, hi, n = ci99([c[field] for c in cycles])
        if n < 3:
            V[key] = {"outcome": "UNDECIDED", "reading": f"{field} {m} over {n} cycles (needs 3)"}
            continue
        inside = band[0] <= lo and hi <= band[1]
        straddle = (lo < band[0] <= hi) or (lo <= band[1] < hi)
        V[key] = {"outcome": "PASS" if inside else ("UNDECIDED" if straddle else "FAIL"),
                  "reading": f"{field} {m:.3f} [{lo:.3f}, {hi:.3f}] over {n} cycles, band {band}",
                  "mean": m, "ci99": [lo, hi], "band": list(band)}
    # L1's and L2's identification tests
    _, lo, hi, n = ci99([c["T_L_C"] for c in cycles])
    if n >= 3:
        V["L1_identified"] = {"outcome": "PASS" if (hi - lo) / 2 <= BANDS["L1_T_L_ci_half_width_max"] else "FAIL",
                              "reading": f"T_L 99% half-width {(hi - lo) / 2:.2f} C (needs <= 8)"}
    _, lo, hi, n = ci99([c["A80_W"] for c in cycles])
    if n >= 3:
        V["L2_identified"] = {"outcome": "PASS" if (hi - lo) / 2 <= BANDS["L2_A80_ci_half_width_max"] else "FAIL",
                              "reading": f"A80 99% half-width {(hi - lo) / 2:.2f} W (needs <= 3)"}
    V["L4"] = {"outcome": "PASS" if min(floors) <= BANDS["L4_floor_c"] else "FAIL",
               "reading": f"lowest reading reached {min(floors):.1f} C (needs <= {BANDS['L4_floor_c']})"}
    law_51, law_67 = share(LAW, 51.0), share(LAW, 67.0)
    json.dump({"cycles": cycles, "dropped": dropped, "verdicts": V,
               "published_law": dict(LAW, share51=law_51, share67=law_67)}, open(a.out, "w"), indent=1)
    print(f"\npublished law: B {LAW['B_W']} W, A80 {LAW['A80_W']} W, T_L {LAW['T_L_C']} C "
          f"-> leakage share {law_51:.3f} at 51 C, {law_67:.3f} at 67 C")
    for k, v in V.items():
        print(f"{k:14s} {v['outcome']:10s} {v['reading']}")


if __name__ == "__main__":
    main()
