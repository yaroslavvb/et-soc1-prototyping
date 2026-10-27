#!/usr/bin/env python3
"""reduce_knob.py: E69 measured against the predictions frozen before the runs, and the six decision rules.

It does not re-reduce the telemetry: it reads the results of E64's own reducer (`reduce_hpl.py`), so every
measured number is produced by the same code that produced E64's, and computes the one metric that lives in
E64's surface tool rather than its reducer - `mhz_steady`, the mean clock from 1.5 s to the end of the work,
on the exact VMIN points - with the identical definition.

    python3 tools/claims-v3/hpl/reduce_hpl.py <session...> --out results_hpl.json > reduce_hpl.txt
    python3 tools/claims-v3/knob/reduce_knob.py results_hpl.json \
        --predictions tools/claims-v3/knob/predictions.json --out results.json > reduce.txt

E64's own rules R1-R4 in `results_hpl.json` were written for a card with nothing set and are NOT applicable
to E69's moved cells; this tool ignores them and says so in its output.
"""
import argparse
import json
import statistics as st
import sys

PTS = [600, 700, 800]
RAMP_S = 1.5
OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
CYC = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}


def rate_t(typ, mhz, minions=1024):
    return minions * OPS[typ] / CYC[typ] * mhz * 1e6 / 1e12


def mhz_steady(m):
    """E64's definition (surface_hpl.py:130): the clock from 1.5 s to the end of the work, VMIN points only."""
    tr = m.get("trace") or []
    xs = [x[3] for x in tr if x[0] is not None and RAMP_S <= x[0] <= (m.get("work_s") or 0) and x[3] in PTS]
    return round(st.mean(xs), 1) if xs else None


def knob_of(m):
    """(tdp_w, threshold_c) as the run itself recorded them: the configuration its own end query read back."""
    q = m.get("queries") or {}
    cfg = q.get("config") or {}
    if cfg.get("tdp_w") is not None:
        return int(cfg["tdp_w"]), int(cfg["temp_threshold_c"])
    # the label is the fallback, and only the label the protocol wrote
    lab = m.get("label") or ""
    tdp = thr = None
    for part in lab.split("-"):
        if part.startswith("tdp") and part[3:].isdigit():
            tdp = int(part[3:])
        if part.startswith("thr") and part[3:].isdigit():
            thr = int(part[3:])
    return tdp, (thr if thr is not None else 65)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_hpl")
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--end", nargs="*", default=[],
                    help="each session's end.json, for K6's restore read-back")
    a = ap.parse_args()
    res = json.load(open(a.results_hpl))
    pred = json.load(open(a.predictions))
    runs = res["metrics"] if "metrics" in res else res.get("runs", [])

    pb = {(c["tdp_w"], c["threshold_c"], c["type"], c["values"]): c for c in pred["burst"]}
    ps = {(c["tdp_w"], c["threshold_c"], c["type"], c["values"]): c for c in pred["sustained"]}

    out = {"experiment": "E69", "request": "Q129", "card": "aifoundry2 card 0",
           "predictions_source": a.predictions, "cells": [], "rules": {}, "unmatched": [],
           "note": "E64's rules R1-R4 in the input file were written for an unmoved governor and do not "
                   "apply to E69; they are ignored here."}

    for m in runs:
        tdp, thr = knob_of(m)
        key = (tdp, thr, m.get("type"), m.get("values"))
        blk = m.get("block")
        if blk == "BURST":
            c = pb.get(key)
            meas = mhz_steady(m)
        elif blk == "SUS":
            c = ps.get(key)
            meas = m.get("sus_mhz_mean")
        else:
            continue
        if c is None:
            out["unmatched"].append({"run": m.get("run"), "block": blk, "knob": [tdp, thr],
                                     "type": m.get("type"), "values": m.get("values")})
            continue
        ev = m.get("events") or {}
        rec = {"run": m.get("run"), "cell": c["cell"], "block": blk, "tdp_w": tdp, "threshold_c": thr,
               "type": m.get("type"), "values": m.get("values"), "rep": m.get("rep"),
               "control": c.get("control"),
               "pred_mhz": c["pred_mhz_mean"], "band_mhz": c["band_mhz"], "meas_mhz": meas,
               "err_mhz": (round(meas - c["pred_mhz_mean"], 1) if meas is not None else None),
               "in_band": (meas is not None and c["band_mhz"][0] <= meas <= c["band_mhz"][1]),
               "pred_tflops": c["pred_tflops"],
               "meas_tflops": (round(rate_t(m["type"], meas), 2) if meas else None),
               "die_start": m.get("die_start"), "die_max": m.get("die_max"), "p800_w": m.get("p800_w"),
               "power_down": ev.get("power_down", 0), "thermal_down": ev.get("thermal_down", 0),
               "power_up": ev.get("power_up", 0), "first_down_kind": m.get("first_down_kind"),
               "n_work_power_down": len(m.get("work_power_down") or []),
               "n_work_thermal_down": len(m.get("work_thermal_down") or [])}
        if blk == "SUS":
            rec.update({"pred_die_c": c.get("pred_die_c"), "pred_board_w": c.get("pred_board_w"),
                        "meas_die_c": m.get("sus_die_mean"), "meas_board_w": m.get("sus_w_mean"),
                        "shape": c.get("shape"), "sus_last": m.get("sus_last")})
        out["cells"].append(rec)

    B = [c for c in out["cells"] if c["block"] == "BURST"]
    S = [c for c in out["cells"] if c["block"] == "SUS"]

    def cellmean(rows, key=lambda c: (c["tdp_w"], c["values"])):
        g = {}
        for c in rows:
            g.setdefault(key(c), []).append(c)
        return g

    # K1: within each pattern, the mean clock is non-decreasing in the cap, and strictly up wherever the
    # model separates two caps by more than 25 MHz
    k1 = {"patterns": {}, "pass": True}
    for vals in sorted({c["values"] for c in B}):
        pts = []
        for (tdp, v), cs in sorted(cellmean(B).items()):
            if v != vals:
                continue
            ms = [c["meas_mhz"] for c in cs if c["meas_mhz"] is not None]
            if ms:
                pts.append((tdp, round(st.mean(ms), 1), round(st.mean([c["pred_mhz"] for c in cs]), 1)))
        pts.sort()
        ok, why = True, []
        for (t1, m1, p1), (t2, m2, p2) in zip(pts, pts[1:]):
            if m2 < m1 - 5:
                ok = False
                why.append(f"{vals}: {t2} W gives {m2} < {t1} W's {m1}")
            if p2 - p1 > 25 and not (m2 > m1 + 5):
                ok = False
                why.append(f"{vals}: model separates {t1}->{t2} W by {round(p2 - p1, 1)} MHz, measured "
                           f"{m1}->{m2}")
        k1["patterns"][vals] = {"points_tdp_meas_pred": pts, "pass": ok, "why": why}
        if len(pts) > 1 and not ok:
            k1["pass"] = False
    out["rules"]["K1"] = k1

    # K2: ones at 45 W throttles where at 65 W it did not
    o65 = [c for c in B if c["values"] == "ones" and c["tdp_w"] == 65]
    o45 = [c for c in B if c["values"] == "ones" and c["tdp_w"] == 45]
    out["rules"]["K2"] = {
        "tdp65": {"mhz": [c["meas_mhz"] for c in o65], "power_down": [c["n_work_power_down"] for c in o65]},
        "tdp45": {"mhz": [c["meas_mhz"] for c in o45], "power_down": [c["n_work_power_down"] for c in o45]},
        "pass": bool(o65) and bool(o45)
        and all(c["meas_mhz"] is not None and c["meas_mhz"] >= 775 for c in o65)
        and all(c["n_work_power_down"] == 0 for c in o65)
        and all(c["meas_mhz"] is not None and c["meas_mhz"] < 775 for c in o45)
        and any(c["n_work_power_down"] > 0 for c in o45)}

    # K3: the cap table - at least 10 of 12 cells in band, rms of the signed error at most 25 MHz
    errs = [c["err_mhz"] for c in B if c["err_mhz"] is not None]
    inb = sum(1 for c in B if c["in_band"])
    rms = round((sum(e * e for e in errs) / len(errs)) ** 0.5, 1) if errs else None
    out["rules"]["K3"] = {"cells": len(B), "in_band": inb, "rms_mhz": rms,
                          "pass": bool(errs) and inb >= 10 and rms is not None and rms <= 25}

    # K4: the sustained clamp is thermal - ones at threshold 70 reaches 775 MHz or more
    s70 = [c for c in S if c["values"] == "ones" and c["threshold_c"] == 70]
    s65 = [c for c in S if c["values"] == "ones" and c["threshold_c"] == 65 and c["tdp_w"] == 65]
    out["rules"]["K4"] = {"thr70_ones": [c["meas_mhz"] for c in s70],
                          "thr65_ones": [c["meas_mhz"] for c in s65],
                          "pass": bool(s70) and all(c["meas_mhz"] is not None and c["meas_mhz"] >= 775
                                                    for c in s70)}

    # K5: the cause can be switched
    r70 = [c for c in S if c["values"] == "randn" and c["threshold_c"] == 70]
    r65 = [c for c in S if c["values"] == "randn" and c["threshold_c"] == 65]
    o50 = [c for c in S if c["values"] == "ones" and c["tdp_w"] == 50]
    half_a = bool(r70) and all(c["meas_mhz"] is not None and abs(c["meas_mhz"] - 600) <= 25
                               and c["n_work_thermal_down"] == 0 and c["n_work_power_down"] > 0 for c in r70)
    half_b = bool(o50) and all(c["meas_mhz"] is not None and 675 <= c["meas_mhz"] <= 725
                               and c["n_work_power_down"] > 0 for c in o50)
    out["rules"]["K5"] = {
        "randn_thr70": [{"mhz": c["meas_mhz"], "thermal_down": c["n_work_thermal_down"],
                         "power_down": c["n_work_power_down"]} for c in r70],
        "randn_thr65": [{"mhz": c["meas_mhz"], "thermal_down": c["n_work_thermal_down"],
                         "power_down": c["n_work_power_down"]} for c in r65],
        "ones_tdp50": [{"mhz": c["meas_mhz"], "thermal_down": c["n_work_thermal_down"],
                        "power_down": c["n_work_power_down"]} for c in o50],
        "half_a_pass": half_a, "half_b_pass": half_b, "pass": half_a and half_b}

    # K6: restore - read straight out of the session's end.json by the caller and passed in res
    ends = []
    for f in a.end:
        d = json.load(open(f))
        orig, rest = d.get("governor_original") or {}, d.get("governor_restore") or {}
        af = rest.get("after") or {}
        ends.append({"file": f, "exit": d.get("exit"), "reason": d.get("reason"),
                     "card_min": d.get("card_min"),
                     "original": {"tdp_w": orig.get("tdp_w"), "temp_threshold_c": orig.get("temp_threshold_c")},
                     "after": {"tdp_w": af.get("tdp_w"), "temp_threshold_c": af.get("temp_threshold_c")},
                     "restore_ok": bool(rest.get("ok")),
                     "equal_to_original": (af.get("tdp_w") == orig.get("tdp_w")
                                           and af.get("temp_threshold_c") == orig.get("temp_threshold_c"))})
    out["rules"]["K6"] = {"sessions": ends,
                          "pass": bool(ends) and all(e["restore_ok"] and e["equal_to_original"] for e in ends)}

    json.dump(out, open(a.out, "w"), indent=1)

    print(f"E69 cells: {len(B)} burst, {len(S)} sustained; {len(out['unmatched'])} unmatched")
    print("\nBURST  cell                           pred   meas    err  band            in  pdn tdn first")
    for c in sorted(B, key=lambda c: (-c["tdp_w"], c["values"], c["rep"] or 0)):
        print(f"  {c['cell']:30s} {c['pred_mhz']:6.1f} {str(c['meas_mhz']):>6s} "
              f"{str(c['err_mhz']):>6s}  {str(c['band_mhz']):15s} {'Y' if c['in_band'] else 'n':2s} "
              f"{c['n_work_power_down']:3d} {c['n_work_thermal_down']:3d} {str(c['first_down_kind'])}")
    print("\nSUS    cell                           pred   meas    err  band            in  pdn tdn  die   W")
    for c in sorted(S, key=lambda c: (c["threshold_c"], -c["tdp_w"], c["values"])):
        print(f"  {c['cell']:30s} {c['pred_mhz']:6.1f} {str(c['meas_mhz']):>6s} "
              f"{str(c['err_mhz']):>6s}  {str(c['band_mhz']):15s} {'Y' if c['in_band'] else 'n':2s} "
              f"{c['n_work_power_down']:3d} {c['n_work_thermal_down']:3d} "
              f"{str(c.get('meas_die_c')):>5s} {str(c.get('meas_board_w')):>5s}")
    print("\nRULES")
    for k in ("K1", "K2", "K3", "K4", "K5", "K6"):
        v = out["rules"][k]
        print(f"  {k}: {'PASS' if v.get('pass') else 'FAIL'}  "
              f"{json.dumps({kk: vv for kk, vv in v.items() if kk != 'pass'})[:260]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
