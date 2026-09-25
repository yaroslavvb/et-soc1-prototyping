#!/usr/bin/env python3
"""Pre-registered tests for experiments anat-X1 and anat-X2 (memory anatomy, both cards). No card.

    crosscard_tests.py --a2 PASS_DIR [PASS_DIR ...] --a3 PASS_DIR [PASS_DIR ...] [--requesters 7,24,31] > tests.json

Each PASS_DIR is one independent pass: the memprobe_host outputs (<name>.u32 + the gen_ops <name>.json) of timer,
ladder, decomp, msmap, bits, refresh, refresh_jit, pagetimeout, l3map, and a subfolder req<S>/ for each requester S
of anat-X2 holding ladder and decomp run with --hart 64*S (the ladder gives that run its own L1 reference). A pass on aifoundry2 whose refresh period is not 2,325 +- 3 cycles, or
whose telemetry showed mhz.minion != 600, is dropped before this script (list the kept ones only).

Every latency is re-referenced to the pass's own timed L1 hit (--l1-ref), because the 22 Sep build read an L1 hit
7 cycles slower than the 19 Sep one. The DRAM model is the 19 Sep one, not refitted (--fixed-model).

Decision rule (written 25 Sep, before any run): for each prediction and each card, the pass-level values must have a
99% t-interval (df = passes - 1) inside the tolerance band, and for effects with a null of zero the interval must
exclude zero; for deterministic counts (msmap, the timer fix) every pass must satisfy the prediction exactly. The
prediction holds as PROVEN-BOTH only if it holds on both cards.
"""
import argparse
import json
import math
import os
import statistics as st
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169}


def run(script, *args):
    out = subprocess.run([sys.executable, os.path.join(HERE, script), *args], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def pass_values(d, requesters):
    """The pass-level numbers each prediction uses."""
    L = run("recompute_latency.py", "--data", d, "--l1-ref", "--fixed-model")
    T = run("timer_window.py", d)
    b = L["bits_summary"]
    lm = L["ladder_model"]
    lad = L["ladder"]
    modes = L["refresh"]["open_closed_modes"]
    closed = max((k for k in modes if float(k) >= 220), key=lambda k: modes[k])
    opened = max((k for k in modes if float(k) < 220), key=lambda k: modes[k])
    l2rep = L["l2"]["by_rep"]
    v = {
        "P1_l3_within4_frac": L["l3"]["within4"] / L["l3"]["lines"],
        "P1_l3_slope": L["l3"]["fit"]["slope"],
        "P1_l3_intercept": L["l3"]["fit"]["intercept"],
        "P2_dram_within3_frac": L["model"]["within3"] / L["model"]["lines"],
        "P2_dram_median_resid": st.median(float(k) for k, n in L["model"]["hist"].items() for _ in range(n)),
        "P3_msmap_match": L["msmap"]["match"],
        "P3_msmap_lines": L["msmap"]["lines"],
        "P4_row_conflict_extra": b["row_conflict_extra"],
        "P4_seq_col": b["seq_col_bits13_17"],
        "P4_seq_row": b["seq_row_bits18_29"],
        "P4_seq_bank": st.median(b["seq_bank_bits6_12"].values()),
        "P5_refresh_period": L["refresh"]["best_period"],
        "P5_closed_minus_open": float(closed) - float(opened),
        "P5_max_extra": L["refresh"]["max_minus_226"],
        "P5_locked_slow_frac": L["refresh_locked"]["frac_ge_220"],
        "P5_locked_max": L["refresh_locked"]["max"],
        "P6_hit_no_refresh": L["rowlife"]["no_refresh"][0] / L["rowlife"]["no_refresh"][1],
        "P6_hit_refresh": L["rowlife"]["refresh"][0] / L["rowlife"]["refresh"][1],
        "P7_pagetimeout_z": L["pagetimeout"]["pooled_z"],
        "P7_late_hits": L["pagetimeout"]["late_hits"][0],
        "P8_ladder_L2": lad["ladder:1"]["med"], "P8_ladder_L3": lad["ladder:2"]["med"], "P8_ladder_MEM": lad["ladder:3"]["med"],
        "P8_ladder_MEM_within6": lm["ladder"]["within6"],
        "P8_nofence_resid": lm["nofence"]["resid_med"],
        "P8_nodelay_fast": lm["nodelay"]["fast_le-6"],
        "P8_nodelay_ms7_resid": lm["nodelay"]["by_ms"]["7"]["resid_med"],
        "P9_l2_rep0_48_frac": l2rep["0"].get("48", 0) / sum(l2rep["0"].values()),
        "P9_l2_rep12_37_frac": (l2rep["1"].get("37", 0) + l2rep["2"].get("37", 0)) / (sum(l2rep["1"].values()) + sum(l2rep["2"].values())),
        "P10_raw_fixed_all10": L["timer"]["fixed_window_11"].get("10", 0) == L["timer"]["pairs"],
        "P10_raw_off_frac": 1 - L["timer"]["raw"].get("10", 0) / L["timer"]["pairs"],
        "P10_stamps_at_11_short": T["stamps_at_11_not_clean"],
        "P10_kernel_misses": T["tnop_misses"],
    }
    for s in requesters:
        dd = os.path.join(d, f"req{s}")
        if os.path.isdir(dd):
            R = run("recompute_latency.py", "--data", dd, "--l1-ref", "--fixed-model", "--requester", str(s))
            v[f"X2_s{s}_l3_within4_frac"] = R["l3"]["within4"] / R["l3"]["lines"]
            v[f"X2_s{s}_dram_within3_frac"] = R["model"]["within3"] / R["model"]["lines"]
    return v


# (key, low, high, null) : the tolerance band each card's 99% interval must fall inside; null = value to exclude
BANDS = {
    "P1_l3_within4_frac": (0.97, 1.0, None), "P1_l3_slope": (11.5, 12.5, 0.0), "P1_l3_intercept": (107, 113, None),
    "P2_dram_within3_frac": (0.85, 1.0, None), "P2_dram_median_resid": (-3, 3, None),
    "P4_row_conflict_extra": (32, 48, 0.0), "P4_seq_col": (-15, -9, 0.0), "P4_seq_row": (6, 12, 0.0), "P4_seq_bank": (-2, 2, None),
    "P5_refresh_period": (2322, 2328, None), "P5_closed_minus_open": (10, 12, 0.0), "P5_max_extra": (170, 250, None),
    "P5_locked_slow_frac": (0.22, 0.28, None), "P6_hit_no_refresh": (0.90, 1.0, None), "P6_hit_refresh": (0.0, 0.10, None),
    "P7_pagetimeout_z": (-3, 3, None), "P8_ladder_L2": (46, 50, None), "P8_ladder_L3": (167, 175, None),
    "P8_ladder_MEM": (303, 315, None), "P8_nofence_resid": (30, 90, 0.0), "P8_nodelay_ms7_resid": (6, 50, 0.0),
    "P9_l2_rep0_48_frac": (0.90, 1.0, None), "P9_l2_rep12_37_frac": (0.90, 1.0, None),
    "P10_raw_off_frac": (0.140, 0.172, None),
}
EXACT = {"P3_msmap_match": lambda v, p: v == p["P3_msmap_lines"], "P10_raw_fixed_all10": lambda v, p: v is True,
         "P10_stamps_at_11_short": lambda v, p: v == 0, "P7_late_hits": lambda v, p: v <= 3, "P5_locked_max": lambda v, p: v < 250}


def interval(x):
    n = len(x)
    m = st.mean(x)
    if n < 2:
        return m, None, None
    h = T995.get(n - 1, 2.6) * st.stdev(x) / math.sqrt(n)
    return m, m - h, m + h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a2", nargs="+", default=[])
    ap.add_argument("--a3", nargs="+", default=[])
    ap.add_argument("--requesters", default="7,24,31")
    a = ap.parse_args()
    reqs = [int(s) for s in a.requesters.split(",") if s]
    cards = {"a2": [pass_values(d, reqs) for d in a.a2], "a3": [pass_values(d, reqs) for d in a.a3]}
    res = {}
    keys = sorted({k for c in cards.values() for p in c for k in p})
    for k in keys:
        per = {}
        for c, passes in cards.items():
            vals = [p[k] for p in passes if k in p]
            if not vals:
                per[c] = {"n": 0, "holds": None}
                continue
            if k in EXACT:
                per[c] = {"n": len(vals), "values": vals, "holds": all(EXACT[k](p[k], p) for p in passes if k in p)}
            elif k in BANDS or k.startswith("X2_"):
                lo, hi, null = BANDS.get(k, (0.97 if "l3" in k else 0.85, 1.0, None))
                m, l, h = interval([float(x) for x in vals])
                ok = l is not None and lo <= l and h <= hi and (null is None or not (l <= null <= h))
                per[c] = {"n": len(vals), "values": vals, "mean": m, "ci99": [l, h], "band": [lo, hi], "holds": ok if len(vals) >= 3 else None}
            else:
                per[c] = {"n": len(vals), "values": vals, "holds": None}
        both = [per[c]["holds"] for c in ("a2", "a3")]
        res[k] = {"cards": per, "verdict": ("PROVEN-BOTH" if all(x is True for x in both) else
                                            "FAILS" if any(x is False for x in both) else "NOT DECIDED (fewer than 3 passes on a card)")}
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
