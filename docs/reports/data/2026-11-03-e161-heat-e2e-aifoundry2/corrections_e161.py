#!/usr/bin/env python3
"""E161: corrections after verification (post hoc, written Tue 3 Nov 2026 about 18:15-18:45 PST, after the data, the post hoc readings
P1-P3 and the verifier's report; NOT registered, no verdict uses them, no registered number or verdict changes). It prints every number
the README's dated notes and its section "Corrections after verification" quote, from committed files only: each hold's HOLD telemetry and
launches.jsonl.gz, results.json and Q139(e)'s frozen predictions, with the frozen code imported unchanged after reduce_e161.py's sha256
check (posthoc_e161.py's own helpers, unchanged).

  C0  posthoc_e161.py's P1/P2 reproduced first (work share 0.9396 / 0.9390, fixed point 62.762 C, trip clock 682.3 MHz), so the
      alternatives below differ from it only in the definition of the share.
  C1  where the scoring window's samples fall ([t1 - 300, t1], t1 the HOLD file's last sample, as the reducer and P1 read it): after the
      hold's last process (the window's tail), in the ~10 ms gaps between processes, in a process's first 0.3 s (before its first kernel
      launch / in it), in kernel launches, in the post hoc's trimmed windows; board W and MHz in each part. The work share under each
      definition, and G1Q's fixed point and G2Q's trip clock at each with P1/P2's formulas; the hold's kernel duty from launches.jsonl
      alone (time in kernel launches over the hold's span, first process start to last process end); the window's tail's effect on the
      measured plateau and clock; the frozen trajectory's last-300 s mean against the fixed point (the finite hold); M8's 800 MHz level
      against the board inside kernel launches at >= 790 MHz.
  C2  the anchor: each hold's REST die and board, and the registered readings over the rest die's whole-degree +-0.5 C (results.json).
  C3  G1Q's registered band against the critic's scale (Q139(e)'s predictions-q139e.json).

    /usr/bin/python3 docs/reports/data/2026-11-03-e161-heat-e2e-aifoundry2/corrections_e161.py > .../corrections.txt
"""
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import posthoc_e161 as PH  # noqa: E402  (imports reduce_e161, which checks the frozen inputs' sha256 on import)

R, PQ, SC = PH.R, PH.PQ, PH.SC
RT = float(PQ.R2.sum())


def r3(x):
    return None if x is None else round(float(x), 3)


def launch_windows(step):
    L = [json.loads(x) for x in gzip.open(os.path.join(HERE, step, "launches.jsonl.gz"), "rt") if x.strip()]
    work = [x for x in L if x.get("role") == "work" and str(x.get("run", "")).startswith("HOLD")]
    pw = [(x["t_start_ms"] / 1000.0, x["t_end_ms"] / 1000.0) for x in work]
    lw = [(z["t_start_ms"] / 1000.0, z["t_end_ms"] / 1000.0) for x in work for z in (x.get("sparsity") or [])]
    first = [x["sparsity"][0]["t_start_ms"] / 1000.0 - x["t_start_ms"] / 1000.0 for x in work if x.get("sparsity")]
    return work, pw, lw, first


def mask(t, wins, lo=0.0, hi=0.0):
    m = np.zeros(len(t), bool)
    for a, b in wins:
        m |= (t >= a + lo) & (t <= b - hi)
    return m


def trip_clock_share(c, T_rest, P_ref, share, T_trip=None, dP=0.0):
    """P2's trip clock at a work share: the held board P_t = P_ref + (T_trip - T_rest) / R; inside the work the board must be
    L_t + (P_t - L_t) / share, L_t the idle board at the trip die (P_ref + 0.442 (T_trip - T_rest)); the clock where M8's board (less dP,
    a level offset read post hoc from the kernel launches) meets it"""
    T_trip = PQ.TRIP_C if T_trip is None else T_trip
    Pt = P_ref + (T_trip - T_rest) / RT
    Lt = P_ref + PQ.K_A2 * (T_trip - T_rest)
    Pw = Lt + (Pt - Lt) / share
    lo, hi = 600.0, 800.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if PQ.board(mid, c, T_trip) - dP < Pw:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def fixed_point_share_level(c, T_rest, P_ref, share, dP=0.0):
    """posthoc_e161.fixed_point_share with M8's 800 MHz board less dP (a level offset read post hoc from the kernel launches);
    at dP = 0 it is fixed_point_share"""
    T = T_rest
    for _ in range(500):
        L = P_ref + PQ.K_A2 * (T - T_rest)
        T = T_rest + RT * (L + share * (PQ.board(800, c, T) - dP - L) - P_ref)
    return T


def main():
    res = json.load(open(os.path.join(HERE, "results.json")))
    steps, sess = R.load(HERE)
    out = {"note": "post hoc, after verification; no registered number, rule, prediction or verdict changes", "C0": {}, "C1": {}}
    for st, s in zip(steps, sess):
        E = res["holds"][st]["E_end_to_end"]
        h = s["holds"][0]
        t1 = h["t1"]
        c = PQ.c_of(R.HOLDS[st])
        T_rest, P_ref = E["T_rest_C"], E["P_ref_W"]
        # the registered readings, unrounded (the reducer's own windows)
        kr = (s["t_raw"] >= t1 - 300.0) & (s["t_raw"] <= t1)
        plat = SC.wmean(s["g"], s["T"], t1 - 300.0, t1)
        f_meas = float(np.mean(s["mhz_raw"][kr]))
        # P1/P2's samples and share, reproduced
        tel, procs, inside = PH.raw(st)
        t, P, F = tel["t"], tel["P"], tel["mhz"]
        k = t >= t[-1] - 300.0
        n = int(k.sum())
        share_posthoc = float((k & inside).sum() / n)
        work, pw, lw, first = launch_windows(st)
        assert pw == procs, "launches.jsonl's processes differ from reduce_e161.work_processes"
        a_first, b_last = pw[0][0], pw[-1][1]
        gaps = [(pw[i][1], pw[i + 1][0]) for i in range(len(pw) - 1)]
        m_proc, m_launch = mask(t, pw), mask(t, lw)
        m_tail = t > b_last
        m_gap = np.zeros(len(t), bool)
        for a, b in gaps:
            m_gap |= (t > a) & (t < b)
        m_first = mask(t, [(a, a + 0.3) for a, _ in pw])
        m_last = mask(t, [(b - 0.05, b) for _, b in pw])

        def part(m):
            mm = m & k
            q = int(mm.sum())
            return {"samples": q, "share": round(q / n, 4), "board_W": round(float(P[mm].mean()), 2) if q else None,
                    "MHz": round(float(F[mm].mean()), 1) if q else None}
        span = b_last - a_first
        KD = "launches.jsonl alone: kernel-launch time over the hold's span (the hold's kernel duty)"
        shares = {
            "continuous (as registered)": 1.0,
            "launches.jsonl alone: process time over the hold's span": sum(b - a for a, b in pw) / span,
            KD: sum(b - a for a, b in lw) / span,
            "window samples in process windows (the verifier's 'process windows')": float((k & m_proc).sum() / n),
            "window samples in kernel launches (the verifier's 'kernel launches')": float((k & m_launch).sum() / n),
            "window samples in the post hoc's trimmed windows (P1/P2)": share_posthoc,
        }
        # the window's tail: the measured readings with the window ended at the last process's end
        plat_notail = SC.wmean(s["g"], s["T"], t1 - 300.0, b_last)
        kr2 = (s["t_raw"] >= t1 - 300.0) & (s["t_raw"] <= b_last)
        f_notail = float(np.mean(s["mhz_raw"][kr2]))
        # the finite hold: the frozen trajectory's mean over the window against the fixed point (G1Q)
        gp, Tp, Pp, Fp = PQ.a2_closed(c, T_rest, P_ref, t1 - pw[0][0])
        m300 = gp >= gp[-1] - 300.0
        o = {
            "window": {"t1_minus_last_process_end_s": r3(t1 - b_last), "samples": n, "processes": len(pw), "launches": len(lw),
                       "gap_between_processes_s_median_max": [round(float(np.median([b - a for a, b in gaps])), 4),
                                                              round(float(max(b - a for a, b in gaps)), 4)],
                       "first_launch_after_process_start_s_min_median_max": [r3(min(first)), r3(np.median(first)), r3(max(first))]},
            "where_the_window_samples_fall": {
                "after the hold's last process (the window's tail)": part(m_tail),
                "in the gaps between processes": part(m_gap),
                "in a process's first 0.3 s": part(m_first),
                "  of which before its first kernel launch": part(m_first & ~m_launch),
                "  of which in a kernel launch": part(m_first & m_launch),
                "in a process's last 0.05 s": part(m_last),
                "in kernel launches": part(m_launch),
                "in kernel launches at >= 790 MHz": part(m_launch & (F >= 790)),
                "in process windows": part(m_proc),
                "in process windows, not in a kernel launch": part(m_proc & ~m_launch),
                "in the post hoc's trimmed windows": part(inside),
                "in the post hoc's trimmed windows at >= 790 MHz": part(inside & (F >= 790)),
            },
            "work_share_by_definition": {kk: round(v, 4) for kk, v in shares.items()},
            "registered_readings_unrounded": {"plateau_measured_C": round(plat, 4), "clock_measured_MHz": round(f_meas, 3)},
            "window_tail_effect": {"plateau_window_ended_at_last_process_C": round(plat_notail, 4),
                                   "plateau_tail_effect_C": round(plat - plat_notail, 4),
                                   "clock_window_ended_at_last_process_MHz": round(f_notail, 3),
                                   "clock_tail_effect_MHz": round(f_meas - f_notail, 3)},
        }
        if st == "G1Q":
            T800 = PQ.a2_plateau_800(c, T_rest, P_ref)
            per = {}
            for nm, sh in shares.items():
                T = PH.fixed_point_share(c, T_rest, P_ref, sh)
                per[nm] = {"share": round(sh, 4), "fixed_point_C": round(T, 3), "plateau_err_C": round(plat - T, 3),
                           "plateau_err_window_ended_at_last_process_C": round(plat_notail - T, 3)}
            o["G1Q_plateau_at_each_share"] = per
            o["finite_hold"] = {"fixed_point_C": round(T800, 3), "frozen_trajectory_mean_last300s_C": round(float(Tp[m300].mean()), 3),
                                "difference_C": round(float(Tp[m300].mean()) - T800, 3)}
            o["M8_level"] = {"M8_board_800MHz_at_the_measured_plateau_die_W": round(PQ.board(800, c, plat), 2),
                             "board_in_kernel_launches_ge790MHz_W": part(m_launch & (F >= 790))["board_W"],
                             "board_in_trimmed_windows_ge790MHz_W": part(inside & (F >= 790))["board_W"],
                             "M8_minus_kernel_launches_ge790_W": round(PQ.board(800, c, plat) - part(m_launch & (F >= 790))["board_W"], 2),
                             "board_predicted_last300s_W": E["board_predicted_W_last300s_simulated"],
                             "board_measured_last300s_all_samples_W": part(np.ones(len(t), bool))["board_W"]}
            # the decomposition (post hoc): M8's level inside the work, read from the kernel launches at >= 790 MHz sample by sample
            mm = k & m_launch & (F >= 790)
            dP1 = float(np.mean([PQ.board(800, c, T_) for T_ in tel["Tf"][mm]]) - P[mm].mean())
            A = res["holds"][st]["A_given_watts"]
            dec = {}
            for nm, sh, dp in (("as registered: continuous work, M8's level", 1.0, 0.0), ("the kernel duty alone", shares[KD], 0.0),
                               ("M8's level alone (set to the kernel launches' at >= 790 MHz)", 1.0, dP1),
                               ("both", shares[KD], dP1)):
                T = fixed_point_share_level(c, T_rest, P_ref, sh, dp)
                dec[nm] = {"share": round(sh, 4), "level_offset_W": round(dp, 3), "fixed_point_C": round(T, 3), "plateau_err_C": round(plat - T, 3)}
            o["decomposition_posthoc"] = {"M8_level_offset_in_kernel_launches_ge790MHz_W": round(dP1, 3), "fixed_points": dec,
                                          "arm_A_plateau_err_C_given_the_watts": round(A["plateau_err_C"], 3),
                                          "E_minus_A_plateau_C": res["holds"][st]["E_minus_A_plateau_C"]}
            out["C0"]["P1"] = {"share": round(share_posthoc, 4), "fixed_point_C": round(PH.fixed_point_share(c, T_rest, P_ref, share_posthoc), 3),
                               "plateau_err_C": round(plat - PH.fixed_point_share(c, T_rest, P_ref, share_posthoc), 3)}
        else:
            per = {}
            for nm, sh in shares.items():
                f = trip_clock_share(c, T_rest, P_ref, sh)
                per[nm] = {"share": round(sh, 4), "trip_clock_MHz": round(f, 3), "clock_err_MHz": round(f_meas - f, 2),
                           "clock_err_window_ended_at_last_process_MHz": round(f_notail - f, 2)}
            o["G2Q_clock_at_each_share"] = per
            f0, _ = PQ.a2_trip_clock(c, T_rest, P_ref)
            o["frozen_trip_clock_check_MHz"] = round(f0, 3)
            # the decomposition (post hoc): M8's level inside the work at the clocks the card ran, sample by sample in the kernel launches
            mm = k & m_launch
            dP2 = float(np.mean([PQ.board(f_, c, T_) for f_, T_ in zip(F[mm], tel["Tf"][mm])]) - P[mm].mean())
            A = res["holds"][st]["A_given_watts"]
            dec = {}
            for nm, sh, dp, Tt in (("as registered: continuous work, M8's level", 1.0, 0.0, PQ.TRIP_C),
                                   ("the kernel duty alone", shares[KD], 0.0, PQ.TRIP_C),
                                   ("M8's level alone (set to the kernel launches')", 1.0, dP2, PQ.TRIP_C),
                                   ("both", shares[KD], dP2, PQ.TRIP_C),
                                   ("M8's level, with the measured held die for the rule's 65.9 C", 1.0, dP2, plat),
                                   ("both, with the measured held die", shares[KD], dP2, plat)):
                f = trip_clock_share(c, T_rest, P_ref, sh, T_trip=Tt, dP=dp)
                dec[nm] = {"share": round(sh, 4), "level_offset_W": round(dp, 3), "held_die_C": round(Tt, 3), "trip_clock_MHz": round(f, 2),
                           "clock_err_MHz": round(f_meas - f, 2)}
            o["decomposition_posthoc"] = {"M8_level_offset_in_kernel_launches_W": round(dP2, 3), "trip_clocks": dec,
                                          "arm_A_plateau_err_C_given_the_watts": round(A["plateau_err_C"], 3)}
            out["C0"]["P2"] = {"share": round(share_posthoc, 4), "trip_clock_MHz": round(trip_clock_share(c, T_rest, P_ref, share_posthoc), 3),
                               "clock_err_MHz": round(f_meas - trip_clock_share(c, T_rest, P_ref, share_posthoc), 3)}
        out["C1"][st] = o
    # C2: the anchor
    out["C2"] = {st: {"T_rest_C": res["holds"][st]["E_end_to_end"]["T_rest_C"], "P_ref_W": res["holds"][st]["E_end_to_end"]["P_ref_W"],
                      "rest_samples": res["holds"][st]["E_end_to_end"].get("rest_samples"),
                      "over_rest_die_pm0p5": {kk: {x: v.get(x) for x in ("plateau_err_C", "clock_err_MHz")}
                                              for kk, v in res["holds"][st]["posthoc_rest_quantization"].items()}}
                 for st in ("G1Q", "G2Q")}
    # C3: G1Q's registered band against the critic's scale
    fh = R.FROZEN_HOLD[R.HOLDS["G1Q"]]
    b95, cs = fh["band_95_C"], fh.get("critic_scale_C")
    out["C3"] = {"G1Q_band_95_C": b95, "G1Q_fail_beyond_C": fh["fail_beyond_C"], "critic_scale_C": cs,
                 "band_over_critic_scale_1p0_and_critic_scale": [round(b95 / 1.0, 2), round(b95 / cs, 2) if cs else None],
                 "G1Q_plateau_err_C": res["holds"]["G1Q"]["E_end_to_end"]["plateau_err_C"],
                 "G1Q_M7_plateau_err_C": res["holds"]["G1Q"]["M7_through_the_same_composition"]["plateau_err_C"],
                 "G1Q_checkpoints_rms_C": res["holds"]["G1Q"]["E_end_to_end"]["checkpoints_rms_C"]}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
