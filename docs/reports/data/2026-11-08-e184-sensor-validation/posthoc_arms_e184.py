#!/usr/bin/env python3
"""E184 arm S (Q156), post hoc: the smoke pass that stopped the session, read at the desk. Written after the data; it decides nothing.

The session of Sun 8 Nov 2026 (T0 1794133299, 02:21:39 PST) ran the stop-path test (18402) and the smoke (18401), and the smoke gate
(check_e184_v2.py smoke, kit note 1 section 1) read NO-GO on the 16-shire n = 19 quad alone, so no pass ran (E184.md.dated-note-A3.md,
A3-1: "E184 arm S not run"). This reader prints what the smoke's four quads read, with the kit's own readers imported unchanged:
  - the gate's reading: check_e184.quads (v1's reader, the one check_e184_v2.smoke gates on);
  - the reducer's reading: reduce_e184_v2.read_process_a2 (v1's reader with A2-5's refresh rule), board and minion rail;
  - each quad's four blocks (label, mean board W, kept refreshes), its base (the A blocks' mean), its instruction rates;
  - the size registered for each step (E184.md section 5.1: 8.256 mW a minion on the board; 2.55 mW a minion on the rail in a quad)
    and the reading over it;
  - the smoke's peak board power, its highest minshire[0] temperature and its busy samples' clock (the stops: 65 W, 70 C).
Usage (from the top of the lab repository): /usr/bin/python3 -B posthoc_arms_e184.py <smoke pass dir> > posthoc-arms-e184.json
It prints JSON only, with no path but the pass's name."""
import json
import math
import os
import sys

pdir = sys.argv[1]
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e184"))
import e184_common as c  # noqa: E402
import check_e184 as v1  # noqa: E402
import reduce_e184_v2 as r2  # noqa: E402

STEP_BOARD_W = 0.008256      # E184.md section 5.1: one minion switched, on the board (E180's fadd.ps random less zeros)
STEP_RAIL_QUAD_W = 0.00255   # E184.md section 5.1: the minion rail keeps 0.380 of a step across a quad's blocks: 2.55 mW a minion
BANDS = {(32, 0): (-0.15, 0.15), (32, 121): (0.70, 1.30), (32, 1024): (7.6, 9.3), (16, 19): (-0.15, 0.30)}   # kit note 1 section 1

qs, tel, runs = v1.quads(pdir)
by = {}
for r in runs:
    by.setdefault(r["seq"], []).append(r)
out = {"pass": os.path.basename(os.path.normpath(pdir)), "label": "post hoc (written after the data; deciding nothing)",
       "readers": "check_e184.quads (the gate's) and reduce_e184_v2.read_process_a2 (the reducer's, A2-5), imported unchanged",
       "quads": []}
for q in qs:
    lns = by[q["seq"]]
    rd = c.read_process(tel, lns)
    a2 = r2.read_process_a2(tel, lns)
    exp_b = q["n"] * STEP_BOARD_W
    exp_r = q["n"] * STEP_RAIL_QUAD_W
    y_a2 = base_a2 = y_rail = None
    if a2["reason"] is None:
        y_a2, base_a2 = c.quad_contrast(a2["board"])
        y_rail, _ = c.quad_contrast(a2["rail"])
    lo, hi = BANDS[(q["mask_m"], q["n"])]
    # each block's kept refreshes (after E82 A2's dip rule and the 0.35 s discard, as both readers keep them), and those A2-5 sets aside
    segs = {}
    for ln in lns:
        s = segs.setdefault(ln["seg"], {"label": ln["label"], "t0": ln["t_start_ms"], "t1": ln["t_end_ms"]})
        s["t0"] = min(s["t0"], ln["t_start_ms"])
        s["t1"] = max(s["t1"], ln["t_end_ms"])
    order = sorted(segs)
    ref = c.refreshes([d for d in tel if segs[order[0]]["t0"] - 1000 <= d.get("t_ms", -1) <= segs[order[-1]]["t1"] + 1000])
    xs = [d["board_w"] for d in ref]
    kept = set(c.dip_keep(xs))
    blocks_refreshes = []
    for k in order[1:]:
        g = segs[k]
        vals = [xs[i] for i in range(len(ref)) if i in kept and g["t0"] + c.DISCARD_S * 1000.0 <= ref[i]["t_ms"] <= g["t1"]]
        m = c.median(vals) if vals else None
        blocks_refreshes.append({"label": g["label"], "refreshes_w": [round(v, 3) for v in vals],
                                 "a2_5_set_aside_w": [round(v, 3) for v in vals if m is not None and abs(v - m) > r2.ROBUST_W],
                                 "median_w": None if m is None else round(m, 3)})
    out["quads"].append({
        "blocks_refreshes": blocks_refreshes,
        "seq": q["seq"], "mask_m": q["mask_m"], "n": q["n"], "ref": q["ref"], "orient": lns[0].get("orient"),
        "blocks_board": [[b[0], round(b[1], 5), b[2]] for b in rd["blocks"]],
        "y_gate_w": None if q["y"] is None else round(q["y"], 5), "base_w": None if q["base"] is None else round(q["base"], 4),
        "y_a2_5_w": None if y_a2 is None else round(y_a2, 5), "a2_5_set_aside": a2["a2_5"],
        "y_rail_w": None if y_rail is None else round(y_rail, 5),
        "band_w": [lo, hi], "in_band": None if q["y"] is None else (lo <= q["y"] <= hi),
        "registered_step_board_w": round(exp_b, 5), "reading_over_step": None if (q["y"] is None or exp_b == 0) else round(q["y"] / exp_b, 4),
        "registered_step_rail_w": round(exp_r, 5),
        "rail_over_step": None if (y_rail is None or exp_r == 0) else round(y_rail / exp_r, 4),
        "rates": q["rate"], "reason": q["reason"]})
board = [d["board_w"] for d in tel if "board_w" in d]
temps = [d["temp_c"]["minshire"][0] for d in tel if isinstance(d.get("temp_c"), dict) and d["temp_c"].get("minshire")]
m_ok, nb = v1.mhz_ok(tel)
rates = [r for q in qs for r in q["rate"]]
med = c.median(rates) if rates else None
out["telemetry"] = {"samples": len(tel), "peak_board_w": max(board) if board else None,
                    "max_minshire0_c": max(temps) if temps else None, "busy_samples": nb, "busy_all_600_mhz": m_ok,
                    "rate_median": med, "rate_max_off_median": None if not med else round(max(abs(r / med - 1) for r in rates), 5)}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
sys.stdout.write("\n")
