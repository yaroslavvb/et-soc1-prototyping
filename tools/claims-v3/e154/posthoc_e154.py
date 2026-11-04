#!/usr/bin/env python3
"""E154 (Q139): POST HOC readings of the measured pass, beside the registered verdicts (score_e154.py), never a verdict. Written on Tue 3 Nov
2026 during the pass (about 18:00 PST), before any hold's data was read. Desk only.

  1. the board over minutes: each hold's measured board rise over R0's P_ref, mean over its last 300 s, against the closed loop's board
     (p = S x on + L(T) - L(T_rest), the same loop arm E runs) for M8's S, E153's measured S, M7's and M6's;
  2. the S at work over minutes: over each hold's last 300 s, the measured board over P_ref less the leakage law's rise at the measured
     die (E97's pooled law, heat_q138t.law_a3), divided by the recorded on-share of those 300 s: the switching watts the tile drew while it
     ran, after minutes, against M8's S and E153's 4.5 s measurement;
  3. arm E anchored on each hold's own rest die (the closed loop restarted at the rest before the hold, from that rest's measured die, with
     no carried-in state): how much of arm E's error is the tail the loop carries from R0;
  4. the plateau's sensitivity to the room: arm E from R0's rest die +-0.25 C.

    python3 tools/claims-v3/e154/posthoc_e154.py <pass dir> [--json <out>]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e154 as sc  # noqa: E402  (checks the frozen inputs' sha256 on import)

se, hm = sc.se, sc.hm


def r3(x, n=3):
    return None if x is None or not np.isfinite(x) else round(float(x), n)


def closed_board(s, table, T_rest, k0):
    g = s["g"]
    S_t = se.s_on_grid(g, [(a, b, table[it]) for (a, b, it) in s["recs"]])
    T = np.full(len(g), np.nan)
    P = np.full(len(g), np.nan)
    T[k0], P[k0] = se.closed_on_grid(S_t[k0], se.TAU, se.R3, T_rest, hm.law_a3)
    return S_t, T, P


def main():
    args = sys.argv[1:]
    jout = None
    if "--json" in args:
        i = args.index("--json")
        jout = args[i + 1]
        args = args[:i] + args[i + 2:]
    pdir = args[0]
    s = se.a3_load([pdir])
    g, T, P = s["g"], s["T"], s["P"]
    r0 = s["rests"][0]
    T_rest = se.wmean(g, T, r0["t1"] - hm.ANCHOR_S, r0["t1"])
    Pref = s["Pref"]
    k0 = g >= r0["t0"]
    out = {"note": "POST HOC (written during the pass, before any hold's data was read); never a verdict", "T_rest_R0_C": r3(T_rest),
           "P_ref_W": r3(Pref), "holds": {}}
    arms = {m: closed_board(s, sc.s_table(m), T_rest, k0) for m in sc.MODELS}
    on_all = se.s_on_grid(g, [(a, b, 1.0) for (a, b, it) in s["recs"]])
    for h in s["holds"]:
        nm, it = h["name"], h.get("item")
        last = (g >= h["t1"] - 300) & (g < h["t1"])
        anc = (g >= h["anchor_end"] - hm.ANCHOR_S) & (g < h["anchor_end"])
        row = {"item": it, "measured_board_rise_last300s_W": r3(float(np.mean(P[last])) - Pref),
               "measured_die_last300s_C": r3(float(np.mean(T[last]))),
               "share_last300s": r3(float(np.mean(on_all[last])), 4)}
        for m, (S_t, Tm, Pm) in arms.items():
            row[f"board_rise_last300s_{m}_W"] = r3(float(np.nanmean(Pm[last])))
            row[f"board_err_{m}_W"] = r3(float(np.mean(P[last])) - Pref - float(np.nanmean(Pm[last])))
        leak = hm.law_a3(T) - hm.law_a3(T_rest)
        sh = float(np.mean(on_all[last]))
        S_obs = (float(np.mean(P[last] - Pref - leak[last])) / sh) if sh > 0.05 else None
        row["S_at_work_last300s_W"] = r3(S_obs)
        row["S_armE_W"] = sc.s_table("M8").get(it)
        row["S_E153_W"] = sc.E153_S.get(it)
        if S_obs is not None and it in sc.E153_S:
            row["S_at_work_minus_E153_W"] = r3(S_obs - sc.E153_S[it])
            row["S_at_work_minus_M8_W"] = r3(S_obs - sc.s_table("M8")[it])
        # 3. arm E restarted at the hold's own rest die, no carried state
        Tr = float(np.mean(T[anc]))
        kk = g >= h["anchor_end"] - hm.ANCHOR_S
        S_t = arms["M8"][0]
        Th = np.full(len(g), np.nan)
        Th[kk], _ = se.closed_on_grid(S_t[kk], se.TAU, se.R3, Tr, hm.law_a3)
        w = (h["launch_period_s"] or 7.0) if h["share"] < 0.9 else 5.0
        meas = se.traj(g, T, h, w)
        pr = se.traj(g, Th, h, w)
        row["E_from_own_rest_plateau_err_C"] = r3(meas["plateau_rise_C"] - pr["plateau_rise_C"])
        out["holds"][nm] = row
    sens = {}
    for d in (-0.25, 0.25):
        S_t = arms["M8"][0]
        Tm = np.full(len(g), np.nan)
        Tm[k0], _ = se.closed_on_grid(S_t[k0], se.TAU, se.R3, T_rest + d, hm.law_a3)
        sens[f"{d:+.2f}"] = {}
        for h in s["holds"]:
            w = (h["launch_period_s"] or 7.0) if h["share"] < 0.9 else 5.0
            sens[f"{d:+.2f}"][h["name"]] = r3(se.traj(g, T, h, w)["plateau_rise_C"] - se.traj(g, Tm, h, w)["plateau_rise_C"])
    out["E_plateau_err_by_room_offset_C"] = sens
    txt = json.dumps(out, indent=1)
    if jout:
        open(jout, "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
