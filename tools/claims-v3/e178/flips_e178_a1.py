#!/usr/bin/env python3
"""E178 dated note A1 (Q146 fix pass): the flip model re-run where the verifier's faults touch it, before any kit or datum.

    python3 -B flips_e178_a1.py --root <lab repo root> [--cc cc]            # writes tools/claims-v3/e178/flips-e178-a1.json and .txt
    python3 -B flips_e178_a1.py --root <lab repo root> [--cc cc] --check    # recomputes, compares both files byte for byte

flipmodel_e178.c and rtl-sim/fma_toggle_v2/accum.c are built unchanged, as forecast_e178.py builds them (its build_model), in a
temporary directory. For each of the 40 kinds of kinds-e178.json:
  (0) the registered call (forecast_e178.N_LAUNCH, its three launch points, N_CALIB): must equal forecast-e178.json's flips_i
      (launch mean, points, points mean, run mean, end word) in every field, or the script stops (exit 3);
  (1) the launch size at the C log's median: E171's pass 17110 (docs/reports/data/2026-11-05-e171-blind8-aifoundry3/ccheck/
      c-log-p17110.jsonl.gz), the median of every timed launch's iters by format (the calibration launches of 20,000 left out),
      rounded half up; forecast_e178.N_LAUNCH is one run's iters, which this also shows;
  (2) the op the toggle bench counts: run_kinds.py seeds C at op n0, runs one warm op and counts op n0 + 1, where the registered
      call counts op n0. int8's F arm subtracts (i)'s points mean over the classes the bench files under lane_operand_bus; at
      n0 + 1 that subtraction moves F by the amounts printed (aifoundry3, and card 1 by M10's card-1 scale).
Also reported: each kind's launch events an op (flipmodel_e178.c prints them apart from the launch mean). Prices are m10.json's:
the float c_end coefficient and the int8 bus coefficient. Nothing is fitted, and no E178 datum exists.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True


def run(exe, t, aw, bw, n, pts, ncal):
    o = subprocess.run([exe, t, aw, bw, str(n), ",".join(str(p) for p in pts), str(ncal)], check=True, capture_output=True,
                       text=True).stdout
    return json.loads(o)


def clog_medians(path):
    """Median iters of the timed launches, by format, in one pass's C log; and the distinct iters of each run."""
    runs, cur = [], None
    for line in gzip.open(path, "rt"):
        r = json.loads(line)
        if r["kind"] == "tiles":
            cur = {"type": r["type"], "iters": [], "calib": []}
            runs.append(cur)
        elif r["kind"] == "c":
            (cur["calib"] if r["launch"] < 0 else cur["iters"]).append(r["iters"])
    res = {}
    for t in ("fp32", "fp16", "int8"):
        rs = [x for x in runs if x["type"] == t]
        allit = [i for x in rs for i in x["iters"]]
        res[t] = {"runs": len(rs), "timed_launches": len(allit), "median": statistics.median(allit), "min": min(allit), "max": max(allit),
                  "runs_with_one_size": sum(1 for x in rs if len(set(x["iters"])) == 1),
                  "calibration_iters": sorted(set(i for x in rs for i in x["calib"]))}
    return res, runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--cc", default="cc")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    D = os.path.join(root, "tools/claims-v3/e178")
    sys.path.insert(0, D)
    import forecast_e178 as FE  # noqa: E402  (N_LAUNCH, N_CALIB, RATE, launch_points, build_model, ACC_CLASSES_INT8; unchanged)
    kinds = json.load(open(os.path.join(D, "kinds-e178.json")))["kinds"]
    fc = json.load(open(os.path.join(D, "forecast-e178.json")))
    m10 = json.load(open(os.path.join(root, "docs/reports/data/2026-11-04-q142m-m10/m10.json")))
    ff, fi = m10["families"]["float"], m10["families"]["int8"]
    e_cend = ff["coef_J"][ff["terms"].index("c_end")]
    e_bus = fi["coef_J"][fi["terms"].index("bus")]
    clog = os.path.join(root, "docs/reports/data/2026-11-05-e171-blind8-aifoundry3/ccheck/c-log-p17110.jsonl.gz")
    med, runs = clog_medians(clog)
    n_med = {t: int(math.floor(med[t]["median"] + 0.5)) for t in med}
    for t in med:
        med[t]["forecast_N_LAUNCH"] = FE.N_LAUNCH[t]
        med[t]["runs_whose_every_launch_is_N_LAUNCH"] = sum(1 for x in runs if x["type"] == t and set(x["iters"]) == {FE.N_LAUNCH[t]})
        med[t]["median_rounded"] = n_med[t]
    out = {"_what": "E178 dated note A1: the flip model re-run (flips_e178_a1.py)", "clog_p17110": med, "prices_J": {"float_c_end": e_cend,
           "int8_bus": e_bus, "card1_scale_float": ff["card1_scale"], "card1_scale_int8": fi["card1_scale"]}, "kinds": {}}
    L = ["E178 dated note A1: the flip model re-run (flips_e178_a1.py; flipmodel_e178.c and accum.c unchanged; no E178 datum exists).", ""]
    L.append("E171's C log, pass 17110, timed launches (the 20,000-op calibration launches left out):")
    for t, v in med.items():
        L.append(f"  {t}: {v['timed_launches']} launches in {v['runs']} runs; median {v['median']:,} (min {v['min']:,}, max {v['max']:,}); "
                 f"{v['runs_with_one_size']} of {v['runs']} runs keep one size for all their launches; forecast_e178.N_LAUNCH {v['forecast_N_LAUNCH']:,} "
                 f"is every launch of {v['runs_whose_every_launch_is_N_LAUNCH']} run")
    L.append("")
    worst = {"rel_total": 0.0, "dF_float_w": 0.0, "dF_int8_med_w": 0.0, "dF_int8_n01_w": [None, None], "launch_events_max": 0.0}
    with tempfile.TemporaryDirectory() as td:
        exe = FE.build_model(root, a.cc, td)
        for k in kinds:
            t, key = k["type"], k["key"]
            reg = fc["kinds"][key]["flips_i"]
            pts = FE.launch_points(t)
            r0 = run(exe, t, k["a_word"], k["b_word"], FE.N_LAUNCH[t], pts, FE.N_CALIB)
            same = (r0["launch_mean"] == reg["launch_mean"] and r0["points_mean"] == reg["points_mean"] and r0["points"] == reg["points"]
                    and r0.get("run_mean") == reg["run_mean"] and r0["c_end"] == reg["c_end_word"])
            if not same:
                print(f"REGISTERED CALL DIFFERS for {key}", file=sys.stderr)
                return 3
            r1 = run(exe, t, k["a_word"], k["b_word"], n_med[t], pts, FE.N_CALIB)
            r2 = run(exe, t, k["a_word"], k["b_word"], FE.N_LAUNCH[t], [p + 1 for p in pts], FE.N_CALIB)
            lm0, lm1 = r0["launch_mean"], r1["launch_mean"]
            rel = (lm1["total"] - lm0["total"]) / lm0["total"] if lm0["total"] else 0.0
            row = {"registered_call_equal": True, "launch_events_per_op": r0["launch_events_per_op"],
                   "median_N": n_med[t], "launch_mean_total_registered": lm0["total"], "launch_mean_total_at_median": lm1["total"],
                   "rel_change_total": rel}
            if t == "int8":
                acc0 = sum(lm0[c] for c in FE.ACC_CLASSES_INT8)
                acc1 = sum(lm1[c] for c in FE.ACC_CLASSES_INT8)
                dF_med = FE.RATE[t] * e_bus * (acc1 - acc0)
                pm0 = sum(r0["points_mean"][c] for c in FE.ACC_CLASSES_INT8)
                pm2 = sum(r2["points_mean"][c] for c in FE.ACC_CLASSES_INT8)
                dF_n01 = -FE.RATE[t] * e_bus * (pm2 - pm0)
                row.update({"dF_w_a3_at_median": dF_med, "acc_points_mean_n0": pm0, "acc_points_mean_n0_plus_1": pm2,
                            "dF_w_a3_at_n0_plus_1": dF_n01, "dF_w_c1_at_n0_plus_1": dF_n01 * fi["card1_scale"],
                            "F_w_a3_at_n0_plus_1": fc["kinds"][key]["F_w"]["a3"] + dF_n01})
                worst["dF_int8_med_w"] = max(worst["dF_int8_med_w"], abs(dF_med))
                lo, hi = worst["dF_int8_n01_w"]
                worst["dF_int8_n01_w"] = [dF_n01 if lo is None else min(lo, dF_n01), dF_n01 if hi is None else max(hi, dF_n01)]
            else:
                dF_med = FE.RATE[t] * e_cend * (lm1["c_store"] - lm0["c_store"])
                row["dF_w_a3_at_median"] = dF_med
                worst["dF_float_w"] = max(worst["dF_float_w"], abs(dF_med))
            worst["rel_total"] = max(worst["rel_total"], abs(rel))
            worst["launch_events_max"] = max(worst["launch_events_max"], r0["launch_events_per_op"])
            out["kinds"][key] = row
    ks = out["kinds"]
    # both kinds move by the same 96 flips an op; flipmodel_e178 prints 4 decimals, so the raw difference is a few 1e-9 W of rounding
    d54 = round(ks["int8.e178_v5"]["dF_w_a3_at_n0_plus_1"] - ks["int8.e178_v4"]["dF_w_a3_at_n0_plus_1"], 6) + 0.0
    out["summary"] = {"max_abs_rel_change_launch_mean_total_at_median": worst["rel_total"], "max_abs_dF_float_w_at_median": worst["dF_float_w"],
                      "max_abs_dF_int8_w_at_median": worst["dF_int8_med_w"], "dF_int8_w_a3_at_n0_plus_1_range": worst["dF_int8_n01_w"],
                      "d_5s_minus_4s_F_int8_w_a3_at_n0_plus_1": d54, "max_launch_events_per_op": worst["launch_events_max"],
                      "registered_calls_equal": all(v["registered_call_equal"] for v in ks.values())}
    s = out["summary"]
    L.append(f"(0) The registered call reproduces forecast-e178.json's flips_i for all {len(ks)} kinds: {s['registered_calls_equal']}.")
    L.append(f"(1) At the C log's median launch size, (i)'s launch-mean total moves by at most {100 * s['max_abs_rel_change_launch_mean_total_at_median']:.4f}% "
             f"over the 40 kinds; F moves by at most {s['max_abs_dF_float_w_at_median']:.5f} W (floats) and {s['max_abs_dF_int8_w_at_median']:.5f} W (int8). "
             "P does not use the launch size.")
    L.append(f"(2) int8's F at op n0 + 1, where the bench counts: F moves by {s['dF_int8_w_a3_at_n0_plus_1_range'][0]:+.4f} to "
             f"{s['dF_int8_w_a3_at_n0_plus_1_range'][1]:+.4f} W a kind (aifoundry3); 5s - 4s by {s['d_5s_minus_4s_F_int8_w_a3_at_n0_plus_1']:+.4f} W.")
    L.append(f"    Launch events: at most {s['max_launch_events_per_op']:.4f} flips an op (flipmodel_e178.c prints them apart; line 33's comment says "
             "the launch mean includes them, and it does not).")
    L.append("")
    L.append("kind                     N median   (i) registered   (i) at median   rel      dF median W   F a3 at n0+1   dF n0+1 W")
    for key in sorted(ks):
        r = ks[key]
        extra = (f"   {r['F_w_a3_at_n0_plus_1']:.4f}       {r['dF_w_a3_at_n0_plus_1']:+.4f}" if "F_w_a3_at_n0_plus_1" in r else "")
        L.append(f"  {key:22s} {r['median_N']:9d}   {r['launch_mean_total_registered']:12.2f}   {r['launch_mean_total_at_median']:12.2f}   "
                 f"{100 * r['rel_change_total']:+.4f}%   {r['dF_w_a3_at_median']:+.6f}{extra}")
    js = json.dumps(out, indent=1, sort_keys=True) + "\n"
    txt = "\n".join(L) + "\n"
    pj, pt = os.path.join(D, "flips-e178-a1.json"), os.path.join(D, "flips-e178-a1.txt")
    if a.check:
        same = open(pj).read() == js and open(pt).read() == txt
        print("CHECK", "PASS" if same else "FAIL")
        return 0 if same else 1
    open(pj, "w").write(js)
    open(pt, "w").write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
