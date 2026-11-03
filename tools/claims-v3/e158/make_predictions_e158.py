#!/usr/bin/env python3
"""E158 (Q139): the frozen predictions for a ladder of B-panel reuse distances under aifoundry2's own governor, written before any E158 data exists.
Writes predictions-e158.json; prints predictions-e158.txt. Standard library only.

    python3 tools/claims-v3/e158/make_predictions_e158.py > tools/claims-v3/e158/predictions-e158.txt

WHAT IS FROZEN, per shape and format (model_e158.py, MAB's frozen prices from E146; desk/reuse_e158.json for the lines and their distances):
  * STRICT-C: strict LRU at 32 MB with C's stores occupying the L3 (E146's MAB exactly: the "before");
  * STRICT-NOC: strict LRU at 32 MB with C taking none of it (w = 0);
  * PRIOR: a logistic retention curve fitted, through MAB's frozen prices, on E146's committed ladder cells with KB >= 2 (L2, L4, L8, D2, D4, D8 in three
    formats; T800 by least squares in relative error; never F6, and not the KB = 1 shapes, whose miss is A's L2 hits), so its F6 is out of sample;
  each with T600, T800, X, C and M of C/f + M, the cycles per op at 800 MHz, and the far-B share it implies.
  * the zeros' power: E136's law as frozen (make_predictions_e146.py's levels0, its lines the desk's strict lines), P0 at 600, 700 and 800 MHz, and the
    admission estimate p800 = B(800) + s(800) c600 (E119's rule; it over-read every E136 burst by 4-15 W), which is this run's predicted peak board power;
  * the rules R0-R8 and the stops.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e146"))
import model_e158 as M  # noqa: E402
import make_predictions_e146 as M146  # noqa: E402  (E146's module as frozen: E136's power law, E119's relation, MAB's prices)

DESK = M.load_desk()
AB, C1 = M.load_prices()
R146 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")))
TYPES = M.TYPES
LADDER = [s for s in DESK["shapes"] if s.startswith("K")]
E146_SHAPES = ("L1", "L2", "L4", "L8", "D1", "D2", "D4", "D8", "F6")
PRIOR_SET = ("L2", "L4", "L8", "D2", "D4", "D8")
RUN_E146 = ("D2", "D4", "F6")             # E146 shapes run again in this session (K4n2 is E146's L4)
LIMIT_W, LOCK_W = 82.0, 60.0
SAFETY = {"abs_stop_c": 80, "board_cap_w": 60, "cap_consecutive": 3}


def inject():
    """E146's power module reads each shape's strict lines from its own desk table; E158's shapes are added to it (E146's own entries unchanged)"""
    for s in LADDER:
        rec = DESK["shapes"][s]
        st = {}
        for cap in ("32MB", "24MB"):
            v = dict(rec["strict"][cap])
            v.update({"A_L2": rec["L2_hits"]["A_L2"], "B_L2": rec["L2_hits"]["B_L2"]})
            v["n_L3"] = v["A_L3"] + v["B_L3"]
            v["n_F"] = v["A_F"] + v["B_F"]
            v["n_miss"] = v["n_L3"] + v["n_F"]
            st[cap] = v
        M146.DESK["shapes"][s] = {"arm": rec["arm"], "store_every_ops": rec["store_every_ops"], "lines": st}


def fit_prior():
    """the logistic (x50, s, w) by least squares on E146's KB >= 2 ladder cells' measured T800, relative error, through MAB's frozen prices"""
    cells = [(s, t, R146["per_shape"][f"{s}.{t}"]["T800"]) for s in PRIOR_SET for t in TYPES]

    def sse(x50, s, w):
        r = M.curve_logistic(x50, s)
        return sum((M.T_model(DESK["shapes"][sh], r, w, AB, C1, t)["T800"] / T - 1) ** 2 for sh, t, T in cells)
    best = None
    for w in (0.0, 0.25, 0.5, 0.75, 1.0):
        for x50 in range(20, 72, 2):
            for s in (1, 2, 4, 8):
                e = sse(x50, s, w)
                if best is None or e < best[0]:
                    best = (e, float(x50), float(s), w)
    e, x50, s, w = best
    step = [2.0, 1.0, 0.125]
    for _ in range(40):
        imp = False
        for dx, ds, dw in ((step[0], 0, 0), (-step[0], 0, 0), (0, step[1], 0), (0, -step[1], 0), (0, 0, step[2]), (0, 0, -step[2])):
            nx, ns, nw = x50 + dx, s + ds, min(1.0, max(0.0, w + dw))
            if not (16 <= nx <= 72 and 0.5 <= ns <= 16):
                continue
            ne = sse(nx, ns, nw)
            if ne < e - 1e-14:
                e, x50, s, w, imp = ne, nx, ns, nw, True
        if not imp:
            step = [v / 2 for v in step]
            if step[0] < 0.02:
                break
    return {"x50_mb": round(x50, 3), "s_mb": round(s, 3), "w": round(w, 3), "rms_rel": round(math.sqrt(e / len(cells)), 5), "cells": [f"{a}.{b}" for a, b, _ in cells],
            "fitted_on": "docs/reports/data/2026-11-02-e146-gemm-stores/results.json per_shape.<s>.<t>.T800 (E146's KB >= 2 ladder; not F6, not L1, D1)"}


def main():
    inject()
    prior = fit_prior()
    curves = {"STRICT-C": (M.curve_strict(32.0), 1.0), "STRICT-NOC": (M.curve_strict(32.0), 0.0),
              "PRIOR": (M.curve_logistic(prior["x50_mb"], prior["s_mb"]), prior["w"])}
    laws, cells, adm = {}, {}, {}
    check = {}
    for s in list(LADDER) + list(E146_SHAPES):
        rec = DESK["shapes"][s]
        xf1, nfar = M.far_x(rec, 1.0)
        xf0, _ = M.far_x(rec, 0.0)
        for t in TYPES:
            L = {"arm": rec["arm"], "blocks": rec["blocks"], "store_every_ops": rec["store_every_ops"], "footprint_MB": rec["footprint_MB"],
                 "far_B": {"lines_per_op": round(nfar, 3), "x_w1_mb": None if xf1 is None else round(xf1, 3), "x_w0_mb": None if xf0 is None else round(xf0, 3)},
                 "share_axis_800": None}
            if nfar:
                tf, tl, n = M.share_axis(rec, AB, C1, t)
                L["share_axis_800"] = {"T_allF": round(tf, 5), "T_allL3": round(tl, 5), "n_far": round(n, 3)}
            for name, (r, w) in curves.items():
                m = M.T_model(rec, r, w, AB, C1, t)
                sh = None if not nfar else M.share_of(m["T800"], rec, AB, C1, t)
                L[name] = {"T600_us": round(m["T600"], 5), "T800_us": round(m["T800"], 5), "X": round(m["X"], 4), "C_cycles": round(m["C"], 1), "M_us": round(m["M"], 5),
                           "cyc800": round(m["T800"] * 800, 1), "share": None if sh is None else round(sh, 4),
                           "lines": {k: round(v, 3) for k, v in m["lines"].items()}}
            if s in E146_SHAPES:
                ref = M146.TAB(s, t, 800)
                check[f"{s}.{t}"] = {"E146_MAB_T800": round(ref, 5), "here_STRICT_C": L["STRICT-C"]["T800_us"], "diff": round(L["STRICT-C"]["T800_us"] - ref, 5)}
                L["E146_measured_T800"] = R146["per_shape"][f"{s}.{t}"]["T800"]
            laws[f"{s}.{t}"] = L
            if s in LADDER or s in RUN_E146:
                lab = f"{s}-{t}-zeros"
                P0 = M146.levels0(s, t, "zeros")
                c6 = M146.c600(s, t, "zeros")
                est = M146.B[800] + M146.SF[800] * c6
                cells[lab] = {"c600_w": round(c6, 3), "P0_w": {str(f): round(v, 2) for f, v in P0.items()}, "p800_estimate_w": round(est, 1),
                              "admitted": est <= LIMIT_W, "predicted_peak_w": round(est, 1)}
                adm[lab] = {"c_ref_w": round(c6, 3), "fixed_p800_w": round(est, 1)}
    adm["rest"] = {"fixed_p800_w": 30.0}
    top = max(v["p800_estimate_w"] for v in cells.values())
    rules = {
        "limit_p800_w": LIMIT_W, "peak_lock_w": LOCK_W, "safety": dict(SAFETY),
        "R2_clock_buys": {"text": "E119's clock_x unchanged (reduce_e158.py imports it through E126's collect): T600 the mean T of launches whose kernel clock is in [590, 610] MHz, T800 of those at or above 790 MHz; at least 2 launches at 600 and 5 at 800, else from the fit T = C/f + M over 590-810 MHz.",
                          "lo_mhz": [590, 610], "hi_mhz": 790, "min_lo": 2, "min_hi": 5},
        "R0_ties": {"text": "every check of C (the host's reference over the whole K) exact or approx, in the smoke and every run (a FAIL labels every other verdict); the smoke's cycles per op at the launch's own clock within 50-250% of STRICT-C's at 800 MHz (the queue's check); the shapes E146 ran, run again here (K4n2 = E146's L4, D2, D4, F6), T800 within 2% of E146's measured T800 per format run (a second session).", "replicate_rel": 0.02},
        "R1_shape": {"text": "the far-B share of every ladder rung (fp32 zeros, every pass pooled), inferred through MAB's frozen prices from T800 (model_e158.share_of): CONSISTENT if every rung's share lies in [-0.10, 1.10] (MAB's prices can carry the rung), else INCONSISTENT, naming the rungs. Against STRICT-C (share 1 below 32 MB, C counted, 0 above): STRICT if every rung is within 0.15 of it, else SOFT; the same against STRICT-NOC printed.", "range": [-0.10, 1.10], "band": 0.15},
        "R2_c_weight": {"text": "C's occupancy w, from ISO (model_e158.fit_iso on the ladder's fp32 shares, the rungs weighted by passes), read on its near-best interval of w (every grid value whose residual is within max(0.01, 0.25 x the least) of the least): C OCCUPIES THE L3 if the interval holds w = 1, not w = 0, and starts at or above 0.5; C TAKES NONE OF IT if it holds w = 0, not w = 1, and ends at or below 0.5; PARTIAL if it holds neither end; UNRESOLVED otherwise. NO SINGLE CURVE, whatever w, if ISO's least rms exceeds 0.06 in share (the three families do not fall on one curve at any w). LOGI's (x50, s, w) printed beside it.", "mid": 0.5, "near_abs": 0.01, "near_rel": 0.25, "single_curve_max_rms": 0.06},
        "R3_F6": {"text": "THE RULE (the critic's rank 7): the fitted retention curve, ISO at its w (primary), with MAB's frozen prices and F6's lines from the desk, predicts F6's T800 (gemmL3x4x6, measured in this session, zeros) within 3%, per format; fp32 primary. LOGI's prediction gets the same verdict, printed. Both also printed against E146's measured F6 (a second session). STRICT-C (E146's MAB) and PRIOR are the befores.", "point_rel": 0.03, "primary": "fp32"},
        "R4_out_of_sample": {"text": "ISO's T800 for every shape no fit saw, against STRICT-C's and PRIOR's: E146's committed 24 ladder cells (and without the KB = 1 shapes L1, D1), and D2 and D4 in this session; rms relative error per model; BETTER if ISO's rms on E146's KB >= 2 cells (L2, L4, L8, D2, D4, D8) is lower than STRICT-C's by at least 2 points. (PRIOR was fitted on those 18 cells: its row there is in sample.)", "better_by": 0.02},
        "R5_formats": {"text": "ISO, fitted on fp32, with each format's own MAB prices, predicts the K4 rungs' T800 in fp16 and int8 within 3% each; the count of PASSes.", "point_rel": 0.03},
        "R6_passes": {"text": "the unit of replication is the pass (A and B = pass 1, C = pass 2, F = pass 3; E, the formats, pass 1): each rung's share per pass; ISO refitted on each pass alone, its w and its F6 prediction per pass; a verdict that holds in one pass and not another is reported so (one session: no interval between sessions).", "scored": False},
        "R7_power": {"text": "the zeros' burst board power at 800 MHz (p800, the first second's median) against P0 (E136's law with the desk's strict lines) and P0 with ISO's lines: rms of each; within 4 W of P0, the count; reported, a secondary reading (zeros draw 34-38 W).", "band_w": 4.0, "scored": False},
        "R8_cycles": {"text": "cycles per op from the measured clock: per shape and format, the fit T = C/f + M over the launches' own clocks (E119's clock_x), and T800 x f at the launches at or above 790 MHz; printed.", "scored": False},
    }
    out = {"experiment": "E158", "request": "Q139", "date": "2026-11-03", "what": "frozen before the claim and the first launch of E158; nothing of E158 exists",
           "ladder": LADDER, "run_e146": list(RUN_E146), "fresh": "F6", "e146_shapes": list(E146_SHAPES), "types": list(TYPES), "kind": "zeros",
           "desk": "tools/claims-v3/e158/desk/reuse_e158.json", "prices": "tools/claims-v3/e146/predictions-e146.json fitted.<t>.ab; docs/reports/data/2026-11-01-e119-gemm-speed/results.json per_arm.c1.<t>.fit",
           "prior": prior, "laws": laws, "cells": cells, "admission": adm, "check_against_e146_mab": check, "rules": rules,
           "relation": {"B": M146.B, "s800": M146.SF[800], "s_f": M146.SF}, "highest_estimate_w": top}
    json.dump(out, open(os.path.join(HERE, "predictions-e158.json"), "w"), indent=1)
    print("E158 frozen predictions (no E158 data exists): aifoundry2 under its own governor, zeros in every cell; time per op by MAB's frozen prices (E146)")
    print("with the lines a retention curve leaves: STRICT-C (E146's MAB), STRICT-NOC (C takes no L3), PRIOR (a logistic fitted on E146's KB >= 2 ladder, not F6).")
    print(f"PRIOR: x50 {prior['x50_mb']} MB, s {prior['s_mb']} MB, w {prior['w']}; rms {100 * prior['rms_rel']:.2f}% over its 18 cells")
    worst = max(abs(v["diff"]) for v in check.values())
    print(f"check: STRICT-C reproduces E146's MAB T800 on E146's nine shapes within {worst:.5f} us")
    print(f"{'shape.fmt':10s} {'arm':12s} {'far':>5s} {'x(w1)':>6s} {'x(w0)':>6s} | {'STRICT-C':>8s} {'sh':>5s} | {'NOC':>8s} {'sh':>5s} | {'PRIOR':>8s} {'sh':>5s} | X(C)   cyc800(C)")
    for k, v in laws.items():
        def g(n):
            return f"{v[n]['T800_us']:8.4f} {'' if v[n]['share'] is None else format(v[n]['share'], '5.2f'):>5s}"
        fb = v["far_B"]
        print(f"{k:10s} {v['arm']:12s} {fb['lines_per_op']:5.1f} {fb['x_w1_mb'] or 0:6.2f} {fb['x_w0_mb'] or 0:6.2f} | {g('STRICT-C')} | {g('STRICT-NOC')} | {g('PRIOR')} | "
              f"{v['STRICT-C']['X']:.4f} {v['STRICT-C']['cyc800']:7.1f}" + (f"   E146 measured {v['E146_measured_T800']:.4f}" if "E146_measured_T800" in v else ""))
    print(f"cells (zeros): admission estimate = predicted peak board W, limit {LIMIT_W} W; highest {top} W")
    for k, v in cells.items():
        print(f"  {k:16s} est {v['p800_estimate_w']:5.1f} W  P0(800) {v['P0_w']['800']:6.2f} W  admitted {v['admitted']}")


if __name__ == "__main__":
    main()
