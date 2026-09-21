#!/usr/bin/env python3
"""Out-of-sample test of a frozen flips-to-temperature model (flip_thermal_model.py output).

    validate_flip_model.py --model model.json --toggles toggles_all.json [--after SECONDS] <run-dir>...

Nothing is fitted here. For every long run in the given sessions (optionally only runs launched after --after
seconds, for a time split of the session the model was trained on), the thermal state at launch is estimated
causally: the network runs on the measured board power from the start of the session, and an observer nudges its
slow stages toward the sensor reading, using telemetry up to the launch instant only. From launch on, the network
is driven by the power line of the model (flip rates of the run, leakage at the simulated temperature) and
nothing measured. Reports predicted against measured time to the cap and end temperature.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flip_thermal_model as ftm  # noqa: E402

DT = ftm.DT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="+")
    ap.add_argument("--model", required=True)
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--after", type=float, default=0.0, help="only evaluate runs launched this many seconds into the session or later")
    ap.add_argument("--observer-tau", type=float, default=30.0, help="seconds over which the observer pulls the slow stages to the sensor")
    ap.add_argument("--cap", type=float, default=89.5)
    ap.add_argument("--out")
    a = ap.parse_args()
    m = json.load(open(a.model))
    tog = json.load(open(a.toggles))
    taus, R, pw = m["taus"], np.array(m["R"]), m["power"]
    T_amb = m["sessions"][0]["T_amb"] if "sessions" in m else m["T_amb"]
    e = np.array([pw["e_fJ"][c] for c in ftm.CLASSES])
    alphas = np.array([1.0 - math.exp(-DT / tau) for tau in taus])
    slow = np.array([tau >= 60 for tau in taus])
    w = np.where(slow, R, 0.0)
    w = w / w.sum()
    rows = []
    for d in a.run_dirs:
        s = ftm.load_session(d, tog)
        n = len(s["t"])
        # start: fast stages settled at the first power sample, the rest of the first reading held by the slow stages
        x = R * s["P"][0]
        x[slow] = 0.0
        x = x + w * (s["T"][0] - T_amb - x.sum())
        launches = {int(np.searchsorted(s["t"], b["t0"])) + 2: b for b in s["blocks"] if b["t1"] < s["t"][-1] - 1.0}
        states = {}
        gain = DT / a.observer_tau
        for i in range(n):
            if i in launches:
                states[i] = x.copy()
            x = x + alphas * (R * s["P"][i] - x)
            x = x + gain * w * (s["T"][i] - (T_amb + x.sum()))       # assimilate the reading (past data only, for later launches)
        for i0, b in launches.items():
            dur = b["t1"] - b["t0"]
            if dur < 15 or b["values"] not in tog or s["t"][i0] - s["t"][0] < max(a.after, 180.0):
                continue
            j = int(np.searchsorted(s["t"], b["t1"]))
            if j >= n - 1:
                continue
            rate = s["F"][:, i0] * s["act"][i0] * ftm.F_OP / 1e15
            pdyn = pw["p_sm_full_chip"] * s["act"][i0] / 1024.0 + float(e @ rate)
            xs = states[i0].copy()
            Tc = T_amb + xs.sum()
            T0, t_cap, T_end = Tc, None, None
            for k in range(int(max(dur, 600) / DT)):
                p = pw["P_fix"] + pw["A_leak_at_80"] * math.exp((min(Tc, 100.0) - 80.0) / pw["T_L"]) + pdyn
                xs = xs + alphas * (R * p - xs)
                Tc = T_amb + xs.sum()
                if t_cap is None and Tc >= a.cap:
                    t_cap = (k + 1) * DT
                if k == int(dur / DT) - 1:
                    T_end = Tc
                if Tc >= 95:
                    T_end = Tc if T_end is None else T_end
                    break
            T_meas_end = float(s["T"][max(i0, j - 20):j].mean())
            rows.append({"session": d, "values": b["values"], "active": int(s["act"][i0]), "t0": float(s["t"][i0] - s["t"][0]), "dur": dur,
                         "p_flips": pdyn, "T_launch_est": float(T0), "T_launch_read": float(s["T"][i0 - 3]),
                         "capped": bool(T_meas_end >= 88.5), "t_cap_pred": t_cap, "T_end_meas": T_meas_end, "T_end_pred": float(T_end)})
    capped = [r for r in rows if r["capped"]]
    hit = [r for r in capped if r["t_cap_pred"]]
    ratios = np.array([r["t_cap_pred"] / r["dur"] for r in hit]) if hit else np.array([1.0])
    unc = [r for r in rows if not r["capped"]]
    summary = {"runs": len(rows), "capped": len(capped), "capped_predicted_to_cap": len(hit),
               "median_abs_pct": float(np.median(np.abs(ratios - 1)) * 100), "worst_pct": float(np.max(np.abs(ratios - 1)) * 100),
               "within_20pct": int(np.sum(np.abs(ratios - 1) <= 0.20)),
               "uncapped": len(unc), "uncapped_end_T_rms": float(np.sqrt(np.mean([(r["T_end_pred"] - r["T_end_meas"]) ** 2 for r in unc]))) if unc else None,
               "uncapped_falsely_capped": int(sum(1 for r in unc if r["t_cap_pred"] and r["t_cap_pred"] < r["dur"]))}
    for r in rows:
        tag = f"90 C after {r['dur']:6.1f} s, predicted {r['t_cap_pred'] if r['t_cap_pred'] else 'never'}" if r["capped"] else \
              f"ran {r['dur']:5.0f} s to {r['T_end_meas']:.1f} C, predicted {r['T_end_pred']:.1f} C" + (f" (cap predicted at {r['t_cap_pred']:.0f} s)" if r["t_cap_pred"] and r["t_cap_pred"] < r["dur"] else "")
        print(f"  {os.path.basename(r['session'].split('@')[0]):6s} {r['t0']:7.0f} s  {r['values']:14s} {r['active']:4d}  flips {r['p_flips']:5.1f} W  launch est {r['T_launch_est']:.1f} (read {r['T_launch_read']:.0f})  {tag}")
    print("summary", summary)
    if a.out:
        json.dump({"rows": rows, "summary": summary, "model": a.model, "after": a.after}, open(a.out, "w"))


if __name__ == "__main__":
    main()
