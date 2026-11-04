#!/usr/bin/env python3
"""E161: post hoc readings (written after the data, Tue 3 Nov 2026 about 17:40 PST; NOT registered, no verdict uses them). They split the
registered errors into their parts with the frozen code, imported unchanged after reduce_e161.py's sha256 check:

  P1  G1Q's board: M8's prediction over the last 300 s against the measured, all samples, the samples inside work processes, and those at
      >= 790 MHz; the work share (samples inside processes); the fixed point recomputed with the switching part scaled by that share
      (the composition assumes continuous work; the harness's processes leave about 6% of the samples between them).
  P2  G2Q's clock: the share of samples at 600 / 700 / 800 MHz over the last 300 s, inside and between processes; the mean clock and board
      inside processes; the trip clock recomputed at the work share.
  P3  G2Q's first seconds: the clock, board and die from the first process's start to 60 s, and the governor's own first step down (the
      first sample below 790 MHz inside a kernel launch from a process's third on: a process opens at the idle state's 600 MHz and the
      governor raises the clock over its first launches, as E144b's D5 found).

    /usr/bin/python3 docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/posthoc_e161.py > .../posthoc.txt
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e161"))
import reduce_e161 as R  # noqa: E402  (checks the frozen inputs' sha256 on import)

PQ, SC, hm = R.PQ, R.SC, R.hm


def raw(step):
    d = os.path.join(HERE, step)
    tel = hm.load_tel(sorted(glob.glob(os.path.join(d, "tel", "HOLD-*.jsonl*"))), sensor="fw")
    procs = R.work_processes(d)
    t = tel["t"]
    inside = np.zeros(len(t), bool)
    for a, b in procs:
        inside |= (t >= a + 0.3) & (t <= b - 0.05)
    return tel, procs, inside


def fixed_point_share(c, T_rest, P_ref, share):
    """a2_plateau_800 with the switching part of the board scaled by the work share: board_s(T) = L(T) + share (board(800, c, T) - L(T)),
    L(T) = P_ref + 0.442 (T - T_rest) the idle board at die T (post hoc, not a frozen form)"""
    Rt = float(PQ.R2.sum())
    T = T_rest
    for _ in range(500):
        L = P_ref + PQ.K_A2 * (T - T_rest)
        T = T_rest + Rt * (L + share * (PQ.board(800, c, T) - L) - P_ref)
    return T


def main():
    res = json.load(open(os.path.join(HERE, "results.json")))
    out = {}
    # P1
    E = res["holds"]["G1Q"]["E_end_to_end"]
    tel, procs, inside = raw("G1Q")
    t1 = tel["t"][-1]
    k = tel["t"] >= t1 - 300
    hi = tel["mhz"] >= 790
    share = float((k & inside).sum() / k.sum())
    c = PQ.c_of(R.HOLDS["G1Q"])
    Ts = fixed_point_share(c, E["T_rest_C"], E["P_ref_W"], share)
    out["P1_G1Q_board"] = {
        "M8_board_predicted_last300s_W": E["board_predicted_W_last300s_simulated"],
        "measured_all_samples_W": round(float(tel["P"][k].mean()), 2),
        "measured_inside_processes_W": round(float(tel["P"][k & inside].mean()), 2),
        "measured_inside_and_ge790MHz_W": round(float(tel["P"][k & inside & hi].mean()), 2),
        "M8_board_at_the_measured_plateau_die_W": round(PQ.board(800, c, E["plateau_measured_C"]), 2),
        "work_share_samples_last300s": round(share, 4),
        "fixed_point_frozen_C": E["plateau_predicted_C"], "fixed_point_at_work_share_C": round(Ts, 3),
        "plateau_measured_C": E["plateau_measured_C"], "plateau_err_at_work_share_C": round(E["plateau_measured_C"] - Ts, 3)}
    # P2
    E2 = res["holds"]["G2Q"]["E_end_to_end"]
    tel2, procs2, inside2 = raw("G2Q")
    t12 = tel2["t"][-1]
    k2 = tel2["t"] >= t12 - 300
    f = tel2["mhz"]

    def shares(m):
        n = max(1, int(m.sum()))
        return {"600": round(float(((f <= 610) & m).sum() / n), 4), "700": round(float(((f > 610) & (f < 790) & m).sum() / n), 4),
                "800": round(float(((f >= 790) & m).sum() / n), 4)}
    share2 = float((k2 & inside2).sum() / k2.sum())
    c2 = PQ.c_of(R.HOLDS["G2Q"])
    # the trip clock at the work share: the held board is P_t = P_ref + (65.9 - T_rest) / R; inside work the board must be higher by the gaps'
    Rt = float(PQ.R2.sum())
    Pt = E2["P_ref_W"] + (PQ.TRIP_C - E2["T_rest_C"]) / Rt
    Lt = E2["P_ref_W"] + PQ.K_A2 * (PQ.TRIP_C - E2["T_rest_C"])
    Pt_work = Lt + (Pt - Lt) / share2
    lo, hi_ = 600.0, 800.0
    for _ in range(60):
        mid = 0.5 * (lo + hi_)
        if PQ.board(mid, c2, PQ.TRIP_C) < Pt_work:
            lo = mid
        else:
            hi_ = mid
    out["P2_G2Q_clock"] = {
        "clock_predicted_MHz": E2["clock_predicted_MHz"], "clock_measured_all_samples_MHz": E2["clock_mean_MHz_last300s"],
        "clock_measured_inside_processes_MHz": round(float(f[k2 & inside2].mean()), 1),
        "clock_measured_between_processes_MHz": round(float(f[k2 & ~inside2].mean()), 1) if (k2 & ~inside2).any() else None,
        "level_shares_all": shares(k2), "level_shares_inside": shares(k2 & inside2), "level_shares_between": shares(k2 & ~inside2),
        "board_measured_all_W": round(float(tel2["P"][k2].mean()), 2), "board_measured_inside_W": round(float(tel2["P"][k2 & inside2].mean()), 2),
        "board_at_trip_predicted_W": E2["board_at_trip_predicted_W"], "work_share_samples_last300s": round(share2, 4),
        "trip_clock_at_work_share_MHz": round(0.5 * (lo + hi_), 1)}
    # P3
    t0 = procs2[0][0]
    m = (tel2["t"] >= t0) & (tel2["t"] <= t0 + 60)
    rows = []
    for tt, P, T, F in zip(tel2["t"][m], tel2["P"][m], tel2["Tf"][m], f[m]):
        rows.append((round(float(tt - t0), 1), round(float(P), 1), int(T), int(F)))
    first800 = next((r for r in rows if r[3] >= 790), None)
    firstdown = None
    seen = False
    for r in rows:
        if r[3] >= 790:
            seen = True
        elif seen and r[3] <= 710:
            firstdown = r
            break
    # the governor's own first step down: the first sample below 790 MHz at least 1.0 s after a process's start and 0.3 s before its end
    # (a process opens the device at the idle state's 600 MHz, so the first in-process samples read 600 by construction: E144b's D5)
    # each process opens at the idle state's 600 MHz and the governor raises the clock over its first launches, so only the kernel
    # launches from each process's third on (its calibration launch and first measured launch skipped) count as steady work
    import gzip as _gz
    wins = []
    for x in (json.loads(y) for y in _gz.open(os.path.join(HERE, "G2Q", "launches.jsonl.gz"), "rt")):
        if x.get("role") == "work":
            wins += [(z["t_start_ms"] / 1000.0, z["t_end_ms"] / 1000.0) for z in (x.get("sparsity") or [])[2:]]
    gov = None
    for tt, P, T, F in zip(tel2["t"], tel2["P"], tel2["Tf"], f):
        if tt < t0 or F >= 790:
            continue
        if any(a <= tt <= b for a, b in wins):
            gov = (round(float(tt - t0), 1), round(float(P), 1), int(T), int(F))
            break
    out["P3_G2Q_governor_first_step_down"] = {"t_s_board_W_die_C_MHz": gov,
                                              "predicted_s": res["holds"]["G2Q"]["E_end_to_end"].get("first_step_down_s_frozen", 48.0)}
    out["P3_G2Q_first_60s"] = {"first_800MHz_sample": first800, "first_step_down_after_800": firstdown,
                               "samples_at_800_in_first_60s": sum(1 for r in rows if r[3] >= 790), "samples": len(rows),
                               "board_max_first_60s_W": max(r[1] for r in rows), "die_at_60s_C": rows[-1][2],
                               "every_second": [r for r in rows if abs(r[0] - round(r[0])) < 0.05][:61]}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
