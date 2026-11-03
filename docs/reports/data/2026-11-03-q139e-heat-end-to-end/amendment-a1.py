#!/usr/bin/env python3
"""Q139(e) amendment A1: corrections after verification, written before E154's and E161's claims (Tue 3 Nov 2026, desk only).

Nothing frozen changes. predict_q139e.py, predictions-q139e.json and predictions-q139e.txt stay as committed in 455c46c1, and
no registered rule, band, FAIL line or stop changes. This script imports the frozen code unchanged and:

  0. checks the sha256 of every input the frozen script reads, including those its own check_frozen() leaves out: E80's
     cells.json, E144b G1's telemetry, and the 85 reduction files its zeros-level glob read at 455c46c1 (listed with their
     sha256 in inputs-sidecar.json). It then rebuilds predictions-q139e.json from exactly those files and checks that the
     rebuild is byte-identical (sha256 60424edb...). The plain glob no longer reproduces it: E152's aifoundry3 files joined it.
  1. reads E154's PLAN with the registered arm E machinery (score_e144.py's s_on_grid, closed_on_grid and traj, unchanged)
     on planned dispatch records at their exact times, for M8's S (S_table_W), M7's and M6's. The frozen session table was
     simulated by heat_q138t.closed_loop, which rounds every piece to whole 0.2 s steps, so K_S's 3.456 s on / 0.914 s off ran
     as 3.4 / 1.0 s (share 0.773, not 0.791). This also re-solves K_S's duty period on the scorer's grid and re-reads K_S's
     band at the true share;
  2. G2q's trip clock under the heat path's own spread: the rise per board W later sessions measured on aifoundry2, and the
     trip plateau's +-0.60 C;
  3. E161's rest rule: the REST anchor G2q gets after G1q with and without E98's 15-minute no-launch rest (E144b's queue);
  4. T_REF's line against E80's sustained int8 -1s cell, a reading from another session;
  5. the facts behind the text corrections (H_L's tail, the plan's minutes);
  6. departure D4: the registered bands against the critic's scale, and the model gaps on the plan.

    python3 docs/reports/data/2026-11-03-q139e-heat-end-to-end/amendment-a1.py > .../amendment-a1.txt
writes amendment-a1.json beside itself (about 20 s). `--write-sidecar` rebuilds inputs-sidecar.json from git at 455c46c1
(the commit the frozen predictions were made at). numpy 1.26.4, Python 3.9.
"""
import fnmatch
import glob
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predict_q139e as pq  # noqa: E402  frozen, unchanged (importing it runs no main)

hm = pq.hm
import score_e144 as se  # noqa: E402  frozen, unchanged (pq put Q138(t)'s dir on the path; its sha256 is in pq.FROZEN)

ROOT, DATA = pq.ROOT, pq.DATA
FROZEN_REV = "455c46c1"
FROZEN_OUT = {
    os.path.join(HERE, "predict_q139e.py"): "0dad4370b5274f6bd85ab86c4065ac9bab8c414f68542d6552255b7891526314",
    os.path.join(HERE, "predictions-q139e.json"): "60424edb5ade86bc50986b9a8eb3368a4fdf28c10780f662361a518e225ed703",
    os.path.join(HERE, "predictions-q139e.txt"): "bcf51b0db6ec994d05010dfba465a6da9ae2bb9146c10e96f2c65bc6905e70a1",
}
SIDECAR = os.path.join(HERE, "inputs-sidecar.json")
GLOB_PAT = "docs/reports/data/2026-1*/e*.json"            # predict_q139e.zeros_spread_a3's glob, relative to ROOT
OTHER_INPUTS = ["docs/reports/data/2026-10-31-e80-kinds-speed/cells.json",
                "docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/G1/tel/HOLD-00-int8-neg_ones-hold-r1.jsonl.gz",
                "docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/G1/tel/REST-00-rest-r1.jsonl.gz",
                "docs/reports/data/2026-11-02-e144-heat-minutes/scored.json"]   # the last is read here only (H_L's facts)
KS = "fp32.real_smol_softmax_v_causal"
KQ = "int8.real_qwen_w8a8_v"
G2Q_ITEM = KS


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    return sha_bytes(open(p, "rb").read())


def zeros_values(blob):
    """the frozen zeros_spread_a3's reading of one file: {fmt: S mean} for an aifoundry3 file, else {}"""
    try:
        j = json.loads(blob)
    except (ValueError, UnicodeDecodeError):
        return {}
    if not isinstance(j, dict) or not str(j.get("card", "")).startswith("aifoundry3"):
        return {}
    out = {}
    for t in ("fp32", "fp16", "int8"):
        z = (j.get("items") or {}).get(f"{t}.zeros") if isinstance(j.get("items"), dict) else None
        if z and isinstance(z.get("S"), dict) and z["S"].get("mean") is not None:
            out[t] = float(z["S"]["mean"])
    return out


def write_sidecar():
    names = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", FROZEN_REV, "docs/reports/data/"],
                           capture_output=True, text=True, check=True).stdout.split("\n")
    globbed = sorted(n for n in names if n.count("/") == 4 and fnmatch.fnmatch(n, GLOB_PAT))
    contrib = []
    for n in globbed:
        b = subprocess.run(["git", "-C", ROOT, "show", f"{FROZEN_REV}:{n}"], capture_output=True, check=True).stdout
        v = zeros_values(b)
        if v:
            contrib.append({"path": n, "sha256": sha_bytes(b), **v})
    other = []
    for n in OTHER_INPUTS:
        b = subprocess.run(["git", "-C", ROOT, "show", f"{FROZEN_REV}:{n}"], capture_output=True, check=True).stdout
        other.append({"path": n, "sha256": sha_bytes(b)})
    sc = {"_note": "Q139(e) amendment A1: the inputs predict_q139e.py read at 455c46c1 that its check_frozen() does not hash. "
                   "zeros_spread_glob.contributing = every file its glob docs/reports/data/2026-1*/e*.json matched that carries an "
                   "aifoundry3 <fmt>.zeros S mean, in the glob's sorted order; amendment-a1.py checks each one's sha256 and rebuilds "
                   "the frozen predictions from exactly these.",
          "rev": FROZEN_REV, "zeros_spread_glob": {"pattern": GLOB_PAT, "globbed_n": len(globbed), "contributing_n": len(contrib),
                                                  "data_dirs_n": len({c["path"].split("/")[3] for c in contrib}),
                                                  "contributing": contrib},
          "other_unhashed_inputs": other}
    json.dump(sc, open(SIDECAR, "w"), indent=1)
    print(f"wrote {os.path.relpath(SIDECAR, ROOT)}: {len(contrib)} contributing of {len(globbed)} globbed; {len(other)} others")


def zeros_from_sidecar(sc):
    bad = [c["path"] for c in sc["zeros_spread_glob"]["contributing"] if sha(os.path.join(ROOT, c["path"])) != c["sha256"]]
    bad += [c["path"] for c in sc["other_unhashed_inputs"] if sha(os.path.join(ROOT, c["path"])) != c["sha256"]]
    if bad:
        sys.exit("sidecar inputs changed since 455c46c1: " + ", ".join(bad))
    out = {}
    for t in ("fp32", "fp16", "int8"):
        v = []
        for c in sc["zeros_spread_glob"]["contributing"]:
            vv = zeros_values(open(os.path.join(ROOT, c["path"]), "rb").read())
            if t in vv:
                v.append(vv[t])
        out[t] = {"n": len(v), "mean": round(statistics.mean(v), 4) if v else None,
                  "sd": round(statistics.stdev(v), 4) if len(v) > 1 else None}
    return out


def zeros_by_dir(sc):
    """post hoc: one value per data directory (its primary e<N>.json when it has one), the spread between sessions"""
    by = {}
    for c in sc["zeros_spread_glob"]["contributing"]:
        d, f = c["path"].split("/")[3], c["path"].split("/")[4]
        stem = f[:-5]
        if stem[1:].isdigit():
            by[d] = c
    out = {}
    for t in ("fp32", "fp16", "int8"):
        v = [c[t] for c in by.values() if t in c]
        out[t] = {"n": len(v), "sd": round(statistics.stdev(v), 4) if len(v) > 1 else None}
    return out, sorted(by)


def bands_by_zeros_spread(frozen, zdir):
    """post hoc: each aifoundry3 pool-6 hold's band_95_C with the zeros-level term as frozen (85 files), as one primary file
    per data directory, and left out, at the frozen G and M8's D band (the registered bands stay as committed)"""
    zs = frozen["zeros_level_spread_aifoundry3"]
    out = {}
    for h in frozen["aifoundry3"]["session"]["holds"]:
        if not h.get("end_to_end"):
            continue
        t = h["item"].split(".")[0]
        sz = zs[t]["sd"]
        sd2 = h["sigma_S_W"] ** 2 - sz ** 2
        G = h["dplateau_dS_C_per_W"]
        row = {}
        for lab, z in (("85 files (frozen)", sz), ("one per directory", zdir[t]["sd"]), ("none", 0.0)):
            row[lab] = round(1.96 * math.sqrt(pq.SIG_CHAIN_A3 ** 2 + G * G * (sd2 + z * z)), 3)
        row["frozen_band_95_C"] = h["band_95_C"]
        out[h["hold"]] = row
    return out


def reproduce(sc):
    """predict_q139e.main()'s object, built from the sidecar's files; it must equal the committed JSON byte for byte"""
    frozen = pq.check_frozen()
    bad = [os.path.relpath(p, ROOT) for p, h in FROZEN_OUT.items() if sha(p) != h]
    if bad:
        sys.exit("frozen outputs changed: " + ", ".join(bad))
    zs = zeros_from_sidecar(sc)
    a3 = pq.a3_predictions(zs)
    tref = pq.tref_check()
    a2 = pq.a2_predictions()
    bc = pq.a2_backcheck()
    res = {"_note": "Q139(e): heat over minutes from the bits, frozen before E154/E161; desk only, nothing refitted",
           "frozen_inputs_sha256": frozen, "gate_commit_pool6_predictions": "d98d2e34",
           "chain_terms_1sigma_C": {"aifoundry3": pq.SIG_CHAIN_A3, "aifoundry2": pq.SIG_CHAIN_A2},
           "zeros_level_spread_aifoundry3": zs, "aifoundry3": a3,
           "aifoundry2": {"T_REF_A2_C": pq.T_REF_A2, "T_REF_check": tref, "K_A2_W_per_C": pq.K_A2, "W0_W": pq.W0,
                          "trip_C": pq.TRIP_C, "backcheck_E144b_G1_posthoc": bc, **a2}}
    res["rules"] = pq.RULES
    txt = json.dumps(res, indent=1, sort_keys=False)
    ok = sha_bytes(txt.encode()) == FROZEN_OUT[os.path.join(HERE, "predictions-q139e.json")]
    if not ok:
        sys.exit("the rebuild from the sidecar does not reproduce predictions-q139e.json")
    # what the plain glob reads at this tree (the reason for the sidecar)
    now = pq.zeros_spread_a3()
    return res, {"rebuild_sha256": sha_bytes(txt.encode()), "byte_identical": ok, "zeros_from_sidecar": zs,
                 "plain_glob_at_this_tree": now, "plain_glob_reproduces": now == zs,
                 "frozen_inputs_checked": len(frozen) + len(FROZEN_OUT) + len(sc["zeros_spread_glob"]["contributing"])
                 + len(sc["other_unhashed_inputs"])}


# ---------------------------------------------------------------- 1. E154's plan through the registered arm E machinery
def plan_records(S_of, period):
    """E154's design as dispatch records at exact times: rests at their lengths, natural-chain holds 5.6 s on / 0.2 s off
    (predict_q139e's LAUNCH_S, GAP_S), K_S 3.456 s on once every `period` s from its first launch; a hold ends with its last
    whole cycle, as in the frozen design"""
    recs, holds, t = [], [], 0.0
    on_ks = pq.K_S_DUTY["recorded_s"]
    for kind, name, item, minutes, pat in pq.A3_DESIGN:
        dur = minutes * 60.0
        if kind == "rest":
            t += dur
            continue
        t0 = t
        cyc, on = (period, on_ks) if pat == "duty" else (pq.LAUNCH_S + pq.GAP_S, pq.LAUNCH_S)
        n = int(dur // cyc)
        recs += [(t0 + i * cyc, t0 + i * cyc + on, S_of[item]) for i in range(n)]
        t = t0 + n * cyc
        holds.append({"name": name, "item": item, "t0": t0, "t1": t, "anchor_end": t0, "launch_period_s": cyc,
                      "duty": pat == "duty"})
    return recs, holds, t


def arm_e_on_plan(S_of, room, period):
    recs, holds, total = plan_records(S_of, period)
    g = np.arange(int(round(total / hm.DT))) * hm.DT
    S_t = se.s_on_grid(g, recs)
    T, Pr = se.closed_on_grid(S_t, pq.TAU, pq.R3, room, hm.law_a3)
    out = {}
    for h in holds:
        w = h["launch_period_s"] if h["duty"] else 5.0          # score_e144's window: one cycle on a duty-cycled hold
        tr = se.traj(g, T, h, w)
        k = (g >= h["t0"]) & (g < h["t1"])
        r = {"share": round(float(S_t[k].mean() / S_of[h["item"]]), 4), "carried_in_C": round(tr["base_C"] - room, 3),
             "plateau_rise_C": round(tr["plateau_rise_C"], 3),
             "plateau_C_abs": round(se.wmean(g, T, h["t1"] - 300, h["t1"]), 2), "peak_C_abs": round(float(T[k].max()), 2),
             "rise_C_by_s": {kk: round(v, 3) for kk, v in tr["rise_C_by_s"].items()}, "start_s": round(h["t0"], 2),
             "end_s": round(h["t1"], 2)}
        if h["t1"] - h["t0"] >= 630:
            a0 = h["anchor_end"] - hm.ANCHOR_S
            dT6 = se.wmean(g, T, h["t0"] + 570, h["t0"] + 630) - tr["base_C"]
            dP6 = se.wmean(g, Pr, h["t0"] + 570, h["t0"] + 630) - se.wmean(g, Pr, a0, h["anchor_end"])
            r["at_600s_per_board_W"] = round(dT6 / dP6, 4)
            r["replicate_ratio_vs_E97_H1_0.898"] = round(dT6 / dP6 / 0.898, 4)
        out[h["name"]] = r
    return out, round(total / 60.0, 2)


def s_tables(frozen):
    m8 = dict(frozen["aifoundry3"]["S_table_W"])
    tabs = {"M8": m8}
    for mname in ("M7", "M6"):
        t = dict(m8)
        for it in pq.CANDIDATES:
            t[it] = pq.P3["tiles"][it][mname]["S_w"]
        tabs[mname] = t
    return tabs


def solve_on_grid(S, T_rest, line=pq.PEAK_LINE_C):
    """predict_q139e.solve_duty_period's question (the shortest period at 7 dispatches whose in-launch peak, from a die rested
    at T_rest with a 120 s lead-in, stays at or under the line over a 10-minute hold) on the scorer's grid, 0.01 s steps"""
    on = pq.K_S_DUTY["recorded_s"]
    for p100 in range(int(on * 100) + 30, 1200):
        cyc = p100 / 100.0
        n = int(600.0 // cyc)
        recs = [(120.0 + i * cyc, 120.0 + i * cyc + on, S) for i in range(n)]
        g = np.arange(int(round((120.0 + n * cyc) / hm.DT))) * hm.DT
        T, _ = se.closed_on_grid(se.s_on_grid(g, recs), pq.TAU, pq.R3, T_rest, hm.law_a3)
        if float(T.max()) <= line:
            return {"period_s": cyc, "share": round(on / cyc, 4), "peak_C": round(float(T.max()), 3)}
    return None


def rested_peak_on_grid(S, T_rest, cyc):
    on = pq.K_S_DUTY["recorded_s"]
    n = int(600.0 // cyc)
    recs = [(120.0 + i * cyc, 120.0 + i * cyc + on, S) for i in range(n)]
    g = np.arange(int(round((120.0 + n * cyc) / hm.DT))) * hm.DT
    T, _ = se.closed_on_grid(se.s_on_grid(g, recs), pq.TAU, pq.R3, T_rest, hm.law_a3)
    return round(float(T.max()), 3)


def part1(frozen):
    tabs = s_tables(frozen)
    duty = frozen["aifoundry3"]["K_S_duty"]
    p_plan, p_warm = duty["plan (room <= 51.5 C)"]["period_s"], duty["warm room (51.5-53.0 C)"]["period_s"]
    cases = [("51.2", 51.2, p_plan), ("51.5", 51.5, p_plan), ("53.0", 53.0, p_warm)]
    on_plan = {}
    total_min = None
    for label, room, per in cases:
        on_plan[f"room {label} C, K_S period {per} s"] = {}
        for mname, tab in tabs.items():
            r, total_min = arm_e_on_plan(tab, room, per)
            on_plan[f"room {label} C, K_S period {per} s"][mname] = r
    fz = {h["hold"]: h for h in frozen["aifoundry3"]["session"]["holds"]}
    nominal = on_plan[f"room 51.2 C, K_S period {p_plan} s"]
    cmp = {}
    for name, h in fz.items():
        e = nominal["M8"][name]
        cmp[name] = {"frozen_share_stated": h["share"], "simulated_share_frozen": None, "armE_share": e["share"],
                     "frozen_plateau_rise_C": h["plateau_rise_C"], "armE_plateau_rise_C": e["plateau_rise_C"],
                     "frozen_carried_in_C": h["carried_in_C"], "armE_carried_in_C": e["carried_in_C"],
                     "frozen_plateau_C_abs": h["plateau_C_abs"], "armE_plateau_C_abs": e["plateau_C_abs"],
                     "frozen_peak_C_abs": h["peak_C_abs"], "armE_peak_C_abs": e["peak_C_abs"],
                     "frozen_M7_rise_C": h["M7_S_through_the_chain"]["plateau_rise_C"],
                     "armE_M7_rise_C": nominal["M7"][name]["plateau_rise_C"],
                     "frozen_M6_rise_C": h["M6_S_through_the_chain"]["plateau_rise_C"],
                     "armE_M6_rise_C": nominal["M6"][name]["plateau_rise_C"],
                     "d_rise_C": round(e["plateau_rise_C"] - h["plateau_rise_C"], 3)}
    # the frozen pattern as simulated: closed_loop rounds every piece to whole 0.2 s steps
    on_s = pq.K_S_DUTY["recorded_s"]
    on_steps, off_steps = int(round(on_s / hm.DT)), int(round((p_plan - on_s) / hm.DT))
    simulated = {"on_s": round(on_steps * hm.DT, 3), "off_s": round(off_steps * hm.DT, 3),
                 "cycle_s": round((on_steps + off_steps) * hm.DT, 3),
                 "share": round(on_steps / (on_steps + off_steps), 4),
                 "S_eff_W": round(frozen["aifoundry3"]["S_table_W"][KS] * on_steps / (on_steps + off_steps), 3),
                 "stated_S_eff_W": fz["K_S"]["S_eff_W"],
                 "frozen_K_S_span_s": [fz["K_S"]["start_s"], fz["K_S"]["end_s"]],
                 "n_cycles": int(600.0 // p_plan)}
    cmp["K_S"]["simulated_share_frozen"] = simulated["share"]
    # the duty solve on the scorer's grid, and the rested peak at the registered periods
    S = tabs["M8"][KS]
    solve = {"51.5": solve_on_grid(S, 51.5), "53.0": solve_on_grid(S, 53.0),
             "rested_peak_at_registered_period_C": {"51.5 C, 4.37 s": rested_peak_on_grid(S, 51.5, p_plan),
                                                    "53.0 C, 4.97 s": rested_peak_on_grid(S, 53.0, p_warm)},
             "frozen_solve": {"51.5": duty["plan (room <= 51.5 C)"], "53.0": duty["warm room (51.5-53.0 C)"]}}
    # every hold's in-session peak at each room, against the 67.5 C design line
    peaks = {lab: {n: r["peak_C_abs"] for n, r in v["M8"].items()} for lab, v in on_plan.items()}
    worst = max((pk, lab, n) for lab, v in peaks.items() for n, pk in v.items())
    # K_S's and K_Q's band at the true pattern (the frozen G came from the rounded one); sigma_S as frozen
    bands = {}
    for name, it in (("K_S", KS), ("K_Q", KQ)):
        rr = []
        for sgn in (+1, -1):
            t2 = dict(tabs["M8"])
            t2[it] = tabs["M8"][it] + sgn * 0.25
            rr.append(arm_e_on_plan(t2, 51.2, p_plan)[0][name]["plateau_rise_C"])
        G = (rr[0] - rr[1]) / 0.5
        sg = fz[name]["sigma_S_W"]
        b1 = math.sqrt(pq.SIG_CHAIN_A3 ** 2 + (G * sg) ** 2)
        bands[name] = {"frozen_dplateau_dS": fz[name]["dplateau_dS_C_per_W"], "armE_dplateau_dS": round(G, 4),
                       "frozen_band_95_C": fz[name]["band_95_C"], "band_95_C_at_true_pattern": round(1.96 * b1, 3),
                       "frozen_fail_beyond_C": fz[name]["fail_beyond_C"],
                       "fail_beyond_C_at_true_pattern": round(max(2 * 1.96 * b1, 1.30), 3)}
    return {"on_plan": on_plan, "frozen_vs_armE_at_51.2C": cmp, "frozen_simulated_K_S_pattern": simulated,
            "duty_solve": solve, "in_session_peaks_C": peaks,
            "worst_in_session_peak": {"peak_C": worst[0], "case": worst[1], "hold": worst[2],
                                      "margin_to_67.5_C": round(pq.PEAK_LINE_C - worst[0], 2)},
            "bands_at_true_pattern": bands, "total_min_exact_times": total_min,
            "nominal_minutes": sum(m for _, _, _, m, _ in pq.A3_DESIGN)}


# ---------------------------------------------------------------- 2. G2q's trip clock and the heat path's R
def trip_clock(c, T_rest, P_ref, R, T_hold=pq.TRIP_C):
    """predict_q139e.a2_trip_clock with the chain's total R and the held die as parameters (equal to it at R2.sum(), 65.9 C)"""
    Pt = P_ref + (T_hold - T_rest) / R
    lo, hi = 600.0, 800.0
    if pq.board(600, c, T_hold) >= Pt:
        return 600.0, Pt
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if pq.board(mid, c, T_hold) < Pt:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), Pt


def part2(frozen):
    c = pq.c_of(G2Q_ITEM)
    T_rest = 46.0
    P_ref, _ = pq.p_ref_a2(T_rest)
    R0 = float(pq.R2.sum())
    f0, Pt0 = pq.a2_trip_clock(c, T_rest, P_ref)
    f0b, _ = trip_clock(c, T_rest, P_ref, R0)
    assert abs(f0 - f0b) < 1e-9
    byR = {}
    for label, R in (("0.663 (frozen, model-q138t a2)", R0), ("0.685", 0.685), ("0.689", 0.689), ("0.707", 0.707),
                     ("0.711 (E144b's (c))", 0.711)):
        f, Pt = trip_clock(c, T_rest, P_ref, R)
        byR[label] = {"clock_MHz": round(f, 1), "board_W": round(Pt, 2), "d_MHz": round(f - f0, 1)}
    byT = {}
    for Th in (pq.TRIP_C - 0.60, pq.TRIP_C + 0.60):
        f, Pt = trip_clock(c, T_rest, P_ref, R0, Th)
        byT[f"held at {Th:.1f} C"] = {"clock_MHz": round(f, 1), "d_MHz": round(f - f0, 1)}
    slope = (pq.board(f0 + 1, c, pq.TRIP_C) - pq.board(f0 - 1, c, pq.TRIP_C)) / 2.0
    sigP = frozen["aifoundry2"]["holds"][1]["sigma_P_W"]
    return {"item": G2Q_ITEM, "rest_C": T_rest, "P_ref_W": round(P_ref, 3), "frozen_clock_rule_MHz": round(f0, 1),
            "board_W_per_MHz_at_the_trip_clock": round(slope, 4),
            "power_path_band_95_MHz": round(1.96 * sigP / slope, 1), "registered_band_MHz": 35.0,
            "clock_by_R": byR, "clock_by_held_die": byT}


# ---------------------------------------------------------------- 3. E161's rest rule (the REST anchor G2q gets after G1q)
def a2_closed_x(c, T_rest, P_ref, dur_s, x0, dt=hm.DT, period_s=1.0):
    """predict_q139e.a2_closed with the chain's states carried in (x0); equal to it at x0 = 0. T_rest is the room."""
    n = int(round(dur_s / dt))
    tau, R = np.asarray(pq.TAU, float), np.asarray(pq.R2, float)
    a = np.exp(-dt / tau)
    x = np.array(x0, float)
    levels = [600, 700, 800]
    ci = 2
    Tk = T_rest + float((R * x).sum())
    T, P, F = np.empty(n), np.empty(n), np.empty(n)
    nxt = 0.0
    for k in range(n):
        if k * dt >= nxt:
            nxt = k * dt + period_s
            rd = math.floor(Tk)
            pb = pq.board(levels[ci], c, Tk)
            if rd > 65 or pb > pq.W0:
                ci = max(0, ci - 1)
            elif rd < 65 and ci < 2 and pq.board(levels[ci + 1], c, Tk) <= pq.W0:
                ci += 1
        pb = pq.board(levels[ci], c, Tk)
        x = a * x + (1 - a) * (pb - P_ref)
        Tk = T_rest + float((R * x).sum())
        T[k], P[k], F[k] = Tk, pb, levels[ci]
    return np.arange(n) * dt, T, P, F, x


def a2_idle_x(T_rest, dur_s, x0, dt=hm.DT):
    """no launch: the board is the rest board moved by the leakage law (law_a2, 0.442 W/C), so the chain's input is
    0.442 (T - T_rest) (Q138(t)'s closed_loop at S = 0)"""
    n = int(round(dur_s / dt))
    tau, R = np.asarray(pq.TAU, float), np.asarray(pq.R2, float)
    a = np.exp(-dt / tau)
    x = np.array(x0, float)
    Tk = T_rest + float((R * x).sum())
    T = np.empty(n)
    for k in range(n):
        p = hm.law_a2(Tk) - hm.law_a2(T_rest)
        x = a * x + (1 - a) * p
        Tk = T_rest + float((R * x).sum())
        T[k] = Tk
    return np.arange(n) * dt, T, x


def part3(frozen):
    room = 46.0
    P_ref, _ = pq.p_ref_a2(room)
    c1, c2 = pq.c_of("int8.b_line_zero_ff"), pq.c_of(G2Q_ITEM)
    x0 = np.zeros(len(pq.TAU))
    # the check: a2_closed_x at x0 = 0 is the frozen a2_closed
    g, T, P, F = pq.a2_closed(c1, room, P_ref, 13 * 60.0)
    g_, T_, P_, F_, x1 = a2_closed_x(c1, room, P_ref, 13 * 60.0, x0)
    assert np.array_equal(T, T_) and np.array_equal(F, F_)
    out = {"room_C": room, "P_ref_W": round(P_ref, 3), "G1q_end_C": round(float(T[-1]), 2)}
    for label, idle_min in (("no rest rule: END 2 + REST 2 min", 4.0), ("E98's rest rule: END 2 + 15 min + REST 2 min", 19.0)):
        gi, Ti, xi = a2_idle_x(room, idle_min * 60.0, x1)
        anchor = float(np.mean(Ti[gi >= gi[-1] - hm.ANCHOR_S + 1e-9]))
        dT = anchor - room
        # the rule as registered, recomputed at the measured REST die and board (the board carries the leakage law)
        P_meas = P_ref + pq.K_A2 * dT
        f_rule, _ = pq.a2_trip_clock(c2, anchor, P_meas)
        f_line, _ = pq.a2_trip_clock(c2, anchor, pq.p_ref_a2(anchor)[0])
        # what the chain says when carried on from G1q (the room is still 46.0)
        g2, T2, P2_, F2, _ = a2_closed_x(c2, room, P_ref, 13 * 60.0, xi)
        m = g2 >= g2[-1] - 300
        out[label] = {"anchor_C": round(anchor, 2), "anchor_minus_room_C": round(dT, 2),
                      "rule_clock_at_the_anchor_MHz": round(f_rule, 1),
                      "rule_clock_at_the_anchor_P_ref_line_MHz": round(f_line, 1),
                      "G2q_carried_chain_plateau_C": round(float(T2[m].mean()), 3),
                      "G2q_carried_chain_clock_last300_MHz": round(float(F2[m].mean()), 1)}
    gr, Tr, Pr, Fr = pq.a2_closed(c2, room, P_ref, 13 * 60.0)
    mr = gr >= gr[-1] - 300
    f_room, _ = pq.a2_trip_clock(c2, room, P_ref)
    out["G2q_from_rest (frozen)"] = {"plateau_C": round(float(Tr[mr].mean()), 3), "clock_last300_MHz": round(float(Fr[mr].mean()), 1),
                                     "rule_clock_MHz": round(f_room, 1)}
    out["wall_min_with_the_rest_rule"] = 15 + 2 + 13 + 2 + 15 + 2 + 13 + 2
    out["card_min_by_E144b_count"] = 2 + 13 + 2 + 2 + 13 + 2
    return out


# ---------------------------------------------------------------- 4. T_REF's line against E80's sustained cell
def part4():
    tel = hm.load_tel(sorted(glob.glob(os.path.join(pq.E144B, "G1", "tel", "HOLD-*.jsonl.gz"))), sensor="fw")
    t = tel["t"] - tel["t"][0]
    k = (tel["mhz"] >= 790) & (t > 5)
    A = np.vstack([np.ones(k.sum()), tel["Tf"][k]]).T
    b0, b1 = np.linalg.lstsq(A, tel["P"][k], rcond=None)[0]
    cells = json.load(open(os.path.join(DATA, "2026-10-31-e80-kinds-speed", "cells.json")))

    def cell(q):
        return [c for c in cells if c.get("format") == "int8" and c.get("kind") == "neg_ones" and c.get("quantity") == q]
    sus_w = [c for c in cell("board_W") if "sustained" in c.get("conditions", "")][0]
    sus_die = [c for c in cell("die_C") if "sustained" in c.get("conditions", "")][0]
    sus_mhz = cell("sustained_MHz")[0]
    burst = cell("board_W_at_800MHz")[0]
    Tdie, W = float(sus_die["value"]), float(sus_w["value"])
    return {"G1_line": {"b0_W": round(float(b0), 3), "slope_W_per_C": round(float(b1), 4), "n": int(k.sum())},
            "E80_burst_P800_W": float(burst["value"]), "T_REF_on_the_line_C": round((float(burst["value"]) - b0) / b1, 2),
            "E80_sustained": {"board_W": W, "die_C": Tdie, "clock_MHz": float(sus_mhz["value"]),
                              "line_at_its_die_W": round(float(b0 + b1 * Tdie), 2), "minus_measured_W": round(float(b0 + b1 * Tdie) - W, 2),
                              "die_on_the_line_C": round((W - b0) / b1, 2)},
            "note": "E80 (31 Oct) is another session than E144b (2 Nov); its sustained cell is nine back-to-back 8 s processes, last 40 s"}


# ---------------------------------------------------------------- 5. facts behind the text corrections
def part5(frozen):
    s = json.load(open(os.path.join(DATA, "2026-11-02-e144-heat-minutes", "scored.json")))
    r0 = s["session"]["rest_die_R0_C"]
    hl = [h for h in s["holds"] if h["hold"] == "H_L"][0]
    return {"E144_H_L": {"rest_die_C": round(hl["rest_die_C"], 3), "R0_rest_die_C": round(r0, 3),
                         "carried_in_C": round(hl["rest_die_C"] - r0, 2), "arm_a_rms_C": round(hl["a"]["rms_C"], 3),
                         "arm_b_plateau_err_C": hl["b"]["plateau_err_C"]},
            "tails_here_C": {h["hold"]: h["carried_in_C"] for h in frozen["aifoundry3"]["session"]["holds"]},
            "plan_minutes": {"nominal": sum(m for _, _, _, m, _ in pq.A3_DESIGN), "frozen_total_min": frozen["aifoundry3"]["session"]["total_min"],
                             "rules_text_said": 72.9, "subset": frozen["aifoundry3"]["subset"]["minutes"]},
            "git": {"gate_commit": "455c46c1", "committed_PST": "2026-11-03 06:00:48"}}


# ---------------------------------------------------------------- 6. D4: the registered bands against the critic's scale
def part6(frozen, p1):
    nominal = p1["on_plan"][[k for k in p1["on_plan"] if k.startswith("room 51.2")][0]]
    rows = {}
    for h in frozen["aifoundry3"]["session"]["holds"]:
        n = h["hold"]
        if n == "H_M":
            continue
        e8, e7, e6 = (nominal[m][n]["plateau_rise_C"] for m in ("M8", "M7", "M6"))
        rows[n] = {"band_95_C": h["band_95_C"], "critic_form_C": h["critic_scale_C"],
                   "ratio_to_critic_form": round(h["band_95_C"] / h["critic_scale_C"], 2),
                   "ratio_to_critic_0.35": round(h["band_95_C"] / 0.35, 2),
                   "M8_minus_M7_C": round(e8 - e7, 3), "M8_minus_M6_C": round(e8 - e6, 3),
                   "largest_gap_over_band": round(max(abs(e8 - e7), abs(e8 - e6)) / h["band_95_C"], 2)}
    g1 = frozen["aifoundry2"]["holds"][0]
    rows["G1q"] = {"band_95_C": g1["band_95_C"], "critic_form_C": g1["critic_scale_C"],
                   "ratio_to_critic_form": round(g1["band_95_C"] / g1["critic_scale_C"], 2),
                   "ratio_to_critic_1.0-1.3": [round(g1["band_95_C"] / 1.3, 2), round(g1["band_95_C"] / 1.0, 2)]}
    return {"holds": rows, "E97_between_session_plateau_moves_C": [0.3, 0.8]}


def main():
    if "--write-sidecar" in sys.argv:
        write_sidecar()
        return
    sc = json.load(open(SIDECAR))
    frozen, rep = reproduce(sc)
    zdir, dirs = zeros_by_dir(sc)
    p1 = part1(frozen)
    res = {"_note": "Q139(e) amendment A1 (Tue 3 Nov 2026, before E154's and E161's claims): corrections after verification, "
                    "desk only, post hoc on the design; no frozen file, rule, band, FAIL line or stop changes",
           "A0_reproduction": rep,
           "C3_zeros_spread_inputs": {"globbed_at_455c46c1": sc["zeros_spread_glob"]["globbed_n"],
                                      "contributing_files": sc["zeros_spread_glob"]["contributing_n"],
                                      "data_dirs": sc["zeros_spread_glob"]["data_dirs_n"],
                                      "distinct_value_triples": len({(c.get("fp32"), c.get("fp16"), c.get("int8"))
                                                                     for c in sc["zeros_spread_glob"]["contributing"]}),
                                      "one_primary_file_per_dir_posthoc": zdir, "dirs_with_a_primary_file": len(dirs),
                                      "band_95_C_by_zeros_term_posthoc": bands_by_zeros_spread(frozen, zdir)},
           "C1_E154_plan_on_the_registered_machinery": p1,
           "C2_G2q_clock_and_the_heat_path": part2(frozen),
           "C4_E161_rest_rule": part3(frozen),
           "C5_T_REF_line_vs_E80_sustained": part4(),
           "C6_text_facts": part5(frozen),
           "D4_bands_vs_the_critic_scale": part6(frozen, p1)}
    json.dump(res, open(os.path.join(HERE, "amendment-a1.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
