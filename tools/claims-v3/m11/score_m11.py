#!/usr/bin/env python3
"""Q143(k): M11's scorer for heat over minutes (tools/claims-v3/m11/REGISTRATION.md section 13 step 1, as amended by A1, A2, A3 and A4),
desk only (the Intel). Nothing is fitted on a committed session and nothing is tuned: every registered list is checked by sha256 first,
each hold is read with the committed readers unchanged, and every rule is the committed design code's own function, imported unchanged:

  READING (section 1), aifoundry3: score_e166.records / classify / arm_a_error / read_one, unchanged, on the session's measured pass
    (arm A: fit_q138t.predict_session on the measured board, as score_e166.arms computes it; R = the measured plateau rise over the
    hold's anchor, e = arm A's plateau error, P = R - e; t0 = the hold's first process, b = its last process's end; the plateau over
    [b - 300 s, b)); a hold is scored if X1 reads it complete (b - t0 >= 570 s; the anchor and plateau windows at >= 5 lines a second).
    aifoundry2 (E177): no reader here. score_e167.read_hold is tied to E167's own holds and frozen predictions, so the aifoundry2 reader
    is E177's kit's own lane; a pass named aifoundry2 is refused.
  RULES, per card kind, over its M11 sessions, in the registered order:
    HM-LG    design_power_groups.lg_test(groups, min_tiles=4, min_span_w=6.0, min_df=3, detail=True), unchanged (section 3);
    A1-4     design_power_heat_v2.decide on the sessions HM-LG counts (HM-AG's three forms, the carried constants, S7-W, the arm's fate);
    HM-E144  |e(H_E)| / R(H_E) <= 1.5% in every session that ran H_E (section 3; A3-5);
    HM-HE    design_power_heat_a3.he_departs_exact (the exact t point, A3-7 (c)); N2 = it departs in every session that ran H_E;
    HM-CAL   design_power_heat_a3.cal_by_name per session (the pair H_E and Z by name, run first by the launch records; A3-6), pooled
             as design_power_heat_a2.hm_cal pools; A2-3's outcome by design_power_heat_a2.a2_entry at the exact t point (A2, A3);
    HM-CAL-I8 design_power_heat_a4.cal_i8_by_name / hm_cal_i8 (L1 and S by name, ended before L2's first launch, the span >= 3.0 C, L2
             inside it), E4' (design_power_heat_a4.int8_misses) and A4-3's route (design_power_heat_a4.i8_entry) (A4).
  REPORTED: per session the two-term fit with its intervals, the room's drift over R0, each hold's P, R, e, span, order and reason;
    RMS_c with its chi-square interval and the floor, for HM-CAL and HM-CAL-I8; the x1.032 arm's rms over the same holds; the blind
    precedence (every registration and amendment commit an ancestor of HEAD and older than the session's first launch record).

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11.py score --a3 <pass dir> [--a3 <pass dir>] [--json <out>] [--md <out>]
    /usr/bin/python3 -B tools/claims-v3/m11/score_m11.py --self-test [--json <out>]
Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import subprocess  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LISTS = ("SHA256SUMS", "SHA256SUMS-m11", "SHA256SUMS-a1", "SHA256SUMS-a2", "SHA256SUMS-a3", "SHA256SUMS-a4")
ALSO_LISTED = ("SHA256SUMS-h2-reader", "SHA256SUMS-h2-reader-v2", "SHA256SUMS-h2-refit")   # M11's other lists: checked and reported
PINNED = {   # the readers this scorer imports, as committed (frozen-e166-fix.sha256 pins score_e166.py; the rest are the M11 lists' entries)
    "tools/claims-v3/e166/score_e166.py": "752dc6b15d618d7d0b8d894628ee877532d357d62a231d9b8d09b81f8a95bba0",
}
REG_COMMITS = {"REGISTRATION": "3c31a91d", "A1": "f49b7ddd", "A2": "d3d97fe2", "A3": "ed24bc6e", "A4": "0b554d25"}
NAMES_A3 = ("H_E", "Z", "L1", "S", "L2")
MIN_SPAN_S = 570.0                      # section 1: E166's X1 for a 10-minute hold


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_lists():
    """every entry of M11's lists and the pinned readers, as listed; returns (counts, problems)"""
    counts, bad = {}, []
    for name in LISTS + ALSO_LISTED:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            bad.append(f"{name}: missing")
            continue
        n = 0
        for line in open(p):
            parts = line.split()
            if len(parts) != 2:
                continue
            n += 1
            q = os.path.join(TREE, parts[1])
            if not os.path.exists(q) or sha(q) != parts[0]:
                bad.append(f"{name}: {parts[1]} differs")
        counts[name] = n
    for rel, want in PINNED.items():
        if sha(os.path.join(TREE, rel)) != want:
            bad.append(f"{rel}: differs from its pin")
    return counts, bad


_COUNTS, _BAD = check_lists()
if _BAD:
    raise SystemExit("M11 scorer REFUSED: a registered file differs:\n  " + "\n  ".join(_BAD))

_saved = list(sys.argv)
sys.argv = [os.path.join(HERE, "design_power_heat_a4.py"), TREE]   # the design code reads argv[1] (the top directory) at import
sys.path.insert(0, HERE)
import design_power_heat_a4 as A4  # noqa: E402  (unchanged: it checks -m11, -a1, -a2, -a3 and imports A3, A2, v2, v1 unchanged)
sys.argv = _saved
A3, A2, V2, D, DPG = A4.A3, A4.A2, A4.V2, A4.D, A4.DPG
sys.path.insert(0, os.path.join(TREE, "tools", "claims-v3", "e166"))
import score_e166 as S166  # noqa: E402  (unchanged: it checks its frozen inputs and imports predict_q140e, which checks its 26)
import numpy as np  # noqa: E402

P166, SE, FT, PQ = S166.P, S166.SE, S166.FT, S166.PQ
_NZ = D.noise()                                              # design_power_heat.noise() on the committed files (SHA256SUMS)
SIGMA = {"aifoundry3": _NZ["a3"]["sigma_C"], "aifoundry2": _NZ["a2"]["sigma_C"]}   # section 7's sigma_c at the power code's precision
                                                             # (0.0884 and 0.2296 C to four decimals, the registered figures)
_S7 = json.load(open(os.path.join(TREE, "docs", "reports", "data", "2026-11-04-q142m-m10", "section7-m10.json")))["section7"]["d"]
GAMMA_ARM = _S7["variants"]["common"]["gamma_all_holds"]["all"]   # the x1.032 arm's gamma, as A2 reads it


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def chi2_interval(r, n):
    """RMS r over n holds: the 95% chi-square interval at n degrees of freedom (approximate)"""
    if r is None or n < 1:
        return None
    return [r4(r * math.sqrt(n / A4.chi2_ppf(0.975, n))), r4(r * math.sqrt(n / A4.chi2_ppf(0.025, n)))]


# ------------------------------------------------------------------------------------------------ section 1: one aifoundry3 session
def read_hold_a3(sess, recs, marks, tel_t, pred_a, name, b_override=None):
    """one hold with score_e166's readers, unchanged; b_override reads an earlier window end (the self-test's K_O_window only)"""
    by = {h["name"]: h for h in sess["holds"]}
    sh = by.get(name)
    if sh is None:
        return {"scored": False, "why": ["not run"]}
    hr = recs.get(name) or {}
    procs = hr.get("procs") or []
    t0 = procs[0][0] if procs else None
    b = b_override if b_override is not None else hr.get("b")
    cl = S166.classify(marks, name, sh["t0"], t0, b, MIN_SPAN_S, tel_t, sh["anchor_end"])
    row = {"item": sh.get("item"), "t0_first_process": t0, "b_last_process_end": b, "anchor_end": sh["anchor_end"],
           "first_launch_s": t0, "status": cl["status"], "why": cl["why_incomplete"], "heat_line_seen": cl["heat_line_seen"]}
    R = e = None
    if b is not None and t0 is not None and b > t0 + 60:
        w = (sh["launch_period_s"] or 7.0) if sh["share"] < 0.9 else 5.0
        err = S166.arm_a_error(sess, pred_a, sh["anchor_end"])
        rr = S166.read_one(sess, {}, err, t0, b, sh["anchor_end"], w, P166.CHECK_A3)
        R, e = rr["measured_rise_C"], rr["A_plateau_err_C"]
        row.update(R_C=R, e_C=e, P_C=None if R is None or e is None else round(R - e, 3), span_s=rr["span_s"], anchor_C=rr["anchor_C"])
    row["scored"] = cl["status"] == "complete" and R is not None and e is not None
    return row


def read_session_a3(pass_dir):
    """an M11 aifoundry3 session: every hold of section 5 by name, the launch order, the room and its drift over R0"""
    marks, recs, src = S166.records(pass_dir)
    gate = [m for m in marks if m.get("kind") == "start_gate"]
    sess = SE.a3_load([pass_dir])
    tel_t = S166.tel_times(pass_dir)
    pred_a = FT.predict_session(sess, PQ.TAU, PQ.R3)
    holds = {nm: read_hold_a3(sess, recs, marks, tel_t, pred_a, nm) for nm in NAMES_A3}
    g, T = sess["g"], sess["T"]
    r0 = sess["rests"][0] if sess["rests"] else None
    drift = None
    if r0 is not None:
        k = (g >= r0["t1"] - 240.0) & (g < r0["t1"])
        if k.sum() >= 10:
            drift = float(np.polyfit(g[k] - g[k][0], T[k], 1)[0]) * 600.0
    launches = [m["t_start_ms"] for m in marks if m.get("kind") == "launch"]
    return {"pass_dir": os.path.basename(os.path.normpath(pass_dir)), "card_kind": "aifoundry3", "records_from": src,
            "start_gate": gate[-1] if gate else None, "first_launch_ms": min(launches) if launches else None,
            "room_drift_over_R0_C_per_10min": r4(drift), "holds": holds, "order": launch_order(holds)}


def launch_order(holds):
    """A2-7 / A3-6: the pair H_E and Z are the session's first two holds by their first launches; A4-1: L1 and S ended before L2's first
    launch. Holds that never launched are left out of the order."""
    st = {nm: h for nm, h in holds.items() if h.get("first_launch_s") is not None}
    order = sorted(st, key=lambda nm: st[nm]["first_launch_s"])
    pair_first = order[:2] == ["H_E", "Z"]
    l2 = st.get("L2")
    i8_ok = bool(l2) and all(st.get(nm) and st[nm].get("b_last_process_end") is not None and
                             st[nm]["b_last_process_end"] <= l2["first_launch_s"] for nm in ("L1", "S"))
    return {"by_first_launch": order, "pair_first": pair_first, "L1_and_S_ended_before_L2": i8_ok}


# ------------------------------------------------------------------------------------------------ sections 3, 6, 7 and A2-A4: the rules
def decide_card_kind(sessions, kind):
    """every registered reading on one card kind's M11 sessions. sessions = {sid: {"holds": {name: {"P_C", "e_C", "R_C", "scored"}},
    "order": {"pair_first", "L1_and_S_ended_before_L2"}}}"""
    sigma_c = SIGMA[kind]
    names = A3.NAMES[kind]
    out = {"card_kind": kind, "sigma_c_C": sigma_c, "sessions": sorted(sessions)}
    named, groups = {}, {}
    for sid in sorted(sessions):
        hs = sessions[sid]["holds"]
        nm = {n: (hs[n]["P_C"], hs[n]["e_C"]) for n in names if hs.get(n, {}).get("scored")}
        named[sid] = nm
        groups[sid] = [nm[n] for n in names if n in nm]
    # HM-LG, on the sessions it counts (section 3)
    counted = {s: v for s, v in groups.items() if len(v) >= D.MIN_HOLDS and max(p for p, _ in v) - min(p for p, _ in v) >= D.MIN_SPAN_C}
    res = DPG.lg_test(groups, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF, detail=True)
    k = len(counted)
    n = sum(len(v) for v in counted.values())
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k) if k >= 2 and n - 2 * k >= 1 else None
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k) if k >= 2 and n - 2 * k >= 1 else None
    o, fate = V2.decide(counted, res, k, n, crit, crit_b, sigma_c)
    out["HM_LG"] = {"verdict": res["verdict"], "k": res["k"], "n": res["n"], "df": res["df"], "not_counted": res["not_counted"],
                    **{x: r4(res[x]) for x in ("F_slope", "F_level", "F_point", "F_null", "F_null_point") if x in res},
                    "null": res.get("null")}
    out["A1_4"] = {"outcome": o, "x1p032_arm": fate}
    if o in A2.COMMON_OUTCOMES and k >= 2:
        allp = [p for v in counted.values() for p in v]
        out["A1_4"]["constants"] = {"gain": [r4(x) for x in V2.fit_gain(allp)], "level": [r4(x) for x in V2.fit_level(allp)],
                                    "both": [[r4(x) for x in V2.fit_both(allp)[0]], [r4(x) for x in V2.fit_both(allp)[1]]]}
    if k >= 2:
        st = V2.ag_stats(counted, k, n)
        out["HM_AG"] = {"F_gain": r4(st["gain"]), "F_level": r4(st["level"]), "F_both": r4(st["both"]), "F_point": r4(crit),
                        "F_point_both": r4(crit_b)}
    # per session, reported (section 3)
    per = {}
    for sid, v in groups.items():
        row = {"n_scored": len(v), "span_P_C": r4(max(p for p, _ in v) - min(p for p, _ in v)) if v else None}
        if len(v) >= 3:
            (a, alo, ahi), (gg, glo, ghi) = V2.fit_both(v)
            row.update(a_C=[r4(a), r4(alo), r4(ahi)], g=[r4(gg), r4(glo), r4(ghi)],
                       level_alone_rms_C=r4(rms([e - V2.fit_level(v)[0] for _, e in v])),
                       gain_alone_rms_C=r4(rms([e - V2.fit_gain(v)[0] * p for p, e in v])))
        per[sid] = row
    out["per_session_fit"] = per
    he_on = kind == "aifoundry3"
    # HM-E144 and HM-HE (aifoundry3's H_E only)
    rep = None
    dep_all = False
    if he_on:
        ins, deps = {}, {}
        for sid, nm in named.items():
            if "H_E" in nm:
                p, e = nm["H_E"]
                ins[sid] = abs(e) / (p + e) <= A3.E144_LINE
                pts = [nm["H_E"]] + [nm[x] for x in names[1:] if x in nm]
                deps[sid] = A3.he_departs_exact(pts)
        rep = all(ins.values()) if ins else None
        dd = [x for x in deps.values() if x is not None]
        dep_all = bool(dd) and all(dd)
        out["HM_E144"] = {"per_session_inside_1p5pct": ins, "reading": "NOT SCORED" if rep is None else ("REPEATS" if rep else "DOES NOT REPEAT"),
                          "label": "A3-5's flag of section 0.1's case; condition E3 of A4's route"}
        out["HM_HE"] = {"per_session_departs": deps, "N2_departs_in_every_session": dep_all, "t_point_2df": r4(A3.T_EXACT[2])}
    # HM-CAL (A2), by name
    cal_per, eu, ec = {}, [], []
    for sid in sorted(sessions):
        r, why = A3.cal_by_name(named[sid], kind, "both", sigma_c, pair_first=sessions[sid]["order"]["pair_first"])
        cal_per[sid] = r if r is not None else {"not_scored": why}
        if r is not None:
            eu += r["eu"]
            ec += r["ec"]
    if eu:
        tau = sigma_c / math.sqrt(len(eu))
        dcal = rms(ec) - rms(eu)
        cal = {"verdict": "BETTER" if dcal <= -tau else "WORSE" if dcal >= tau else "NOT RESOLVED",
               "k": sum(1 for v in cal_per.values() if "not_scored" not in v), "n_L": len(eu), "tau": tau, "D": dcal,
               "rms_u": rms(eu), "rms_c": rms(ec), "N1": any(v.get("worse_alone") for v in cal_per.values() if "not_scored" not in v)}
    else:
        cal = {"verdict": "NOT SCORED", "k": 0, "N1": False}
    e2 = A2.a2_entry(o, cal, dep_all)
    later_pairs = []
    for sid in sorted(sessions):
        for x in A3.LATER[kind]:
            if x in named[sid] and "not_scored" not in cal_per[sid]:
                later_pairs.append(named[sid][x])
    out["HM_CAL"] = {"verdict": cal["verdict"], "n_L": cal.get("n_L"), "tau_C": r4(cal.get("tau")), "D_C": r4(cal.get("D")),
                     "RMS_u_C": r4(cal.get("rms_u")), "RMS_c_C": r4(cal.get("rms_c")),
                     "RMS_c_interval_C": chi2_interval(cal.get("rms_c"), cal.get("n_L") or 0), "N1": cal["N1"],
                     "per_session": {s: ({"a_C": r4(v["a"]), "g": r4(v["g"]), "n": v["n"], "rms_u_C": r4(v["rms_u"]), "rms_c_C": r4(v["rms_c"]),
                                          "d_C": r4(v["d"]), "worse_alone": v["worse_alone"]} if "not_scored" not in v else v)
                                     for s, v in cal_per.items()},
                     "x1p032_arm_rms_later_C": r4(rms([e - GAMMA_ARM * p for p, e in later_pairs])),
                     "floor_C": r4(floor_cal(named, kind, cal_per, sigma_c)),
                     "A2_3_outcome": e2,
                     "scope": "int8 holds on E97's natural chain within the pair's span of P (A3-4)" if he_on else "aifoundry2's later holds"}
    out["HM_CAL"]["arms"] = {}
    for form in ("gain", "level", "gain_HE"):
        eu2, ec2 = [], []
        for sid in sorted(sessions):
            r, _ = A3.cal_by_name(named[sid], kind, form, sigma_c, pair_first=sessions[sid]["order"]["pair_first"])
            if r is not None:
                eu2 += r["eu"]
                ec2 += r["ec"]
        out["HM_CAL"]["arms"][form] = {"RMS_c_C": r4(rms(ec2)), "RMS_u_C": r4(rms(eu2))} if eu2 else "NOT SCORED"
    # HM-CAL-I8 (A4), aifoundry3 only
    if he_on:
        i8 = A4.hm_cal_i8({sid: (named[sid], sessions[sid]["order"]["L1_and_S_ended_before_L2"]) for sid in sorted(sessions)}, sigma_c)
        x2, pt, miss = A4.int8_misses(i8, sigma_c) if i8["verdict"] != "NOT SCORED" else (None, None, False)
        oi = A4.i8_entry(o, e2, bool(rep), res, i8, sigma_c)
        l2 = [named[s]["L2"] for s, v in i8["per"].items() if "not_scored" not in v]
        fl = None
        rd = [v for v in i8["per"].values() if "not_scored" not in v]
        if rd:
            fl = sigma_c * math.sqrt(sum(1.0 + (1.0 - v["w"]) ** 2 + v["w"] ** 2 for v in rd) / len(rd))
        out["HM_CAL_I8"] = {"verdict": i8["verdict"], "n_L": i8.get("n_L"), "tau_C": r4(i8.get("tau")), "D_C": r4(i8.get("D")),
                            "RMS_u_C": r4(i8.get("rms_u")), "RMS_c_C": r4(i8.get("rms_c")),
                            "RMS_c_interval_C": chi2_interval(i8.get("rms_c"), i8.get("n_L") or 0), "N1_I8": bool(i8.get("N1")),
                            "E4p": {"X2": r4(x2), "chi2_95_point": r4(pt), "the_chain_misses_the_int8_holds": miss},
                            "per_session": {s: ({kk: r4(vv) if isinstance(vv, float) else vv for kk, vv in v.items()}) for s, v in i8["per"].items()},
                            "x1p032_arm_rms_L2_C": r4(rms([e - GAMMA_ARM * p for p, e in l2])) if l2 else None,
                            "floor_C": r4(fl), "A4_3_outcome": oi,
                            "scope": "int8 holds on E97's natural chain inside the session's L1-S span (A4-2)"}
    else:
        oi = None
    # what M11 carries for heat over minutes on this card kind
    if o in A2.COMMON_OUTCOMES:
        carries = f"A1-4's common term ({o})"
    elif e2 == A3.ENTERS:
        carries = "A2's in-session calibration (H_E and Z)"
    elif oi == A4.ENTERS_I8:
        carries = "A4's in-session calibration (L1 and S, read on L2)"
    elif o == "nothing: one session (a candidate)" or (len(sessions) < 2):
        carries = "nothing: one session (the readings are a candidate for the next session)"
    else:
        carries = "nothing: the chain unscaled stays M11's primary"
    out["M11_carries"] = carries
    return out


def floor_cal(named, kind, cal_per, sigma_c):
    p_name, z_name = A3.PAIR[kind]
    f = []
    for sid, v in cal_per.items():
        if "not_scored" in v:
            continue
        p1, p2 = named[sid][p_name][0], named[sid][z_name][0]
        for x in A3.LATER[kind]:
            if x in named[sid]:
                w = (named[sid][x][0] - p2) / (p1 - p2)
                f.append(1.0 + (1.0 - w) ** 2 + w * w)
    return sigma_c * math.sqrt(sum(f) / len(f)) if f else None


# ------------------------------------------------------------------------------------------------ precedence (section 11, A2-8, A3-10, A4-9)
def git(*a):
    try:
        p = subprocess.run(["git", "-C", TREE] + list(a), capture_output=True, text=True, timeout=30)
        return p.returncode, p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 99, ""


def precedence(first_launch_ms):
    out = {}
    for k, c in REG_COMMITS.items():
        rc, t = git("log", "-1", "--format=%ct", c)
        rca, _ = git("merge-base", "--is-ancestor", c, "HEAD")
        ok = rc == 0 and rca == 0 and first_launch_ms is not None and int(t) * 1000 < first_launch_ms
        out[k] = {"commit": c, "commit_epoch_s": int(t) if rc == 0 and t else None, "ancestor_of_HEAD": rca == 0, "precedes_first_launch": ok}
    out["blind"] = all(v["precedes_first_launch"] for v in out.values() if isinstance(v, dict))
    return out


# ------------------------------------------------------------------------------------------------ the score
def score(a3_dirs):
    out = {"scorer": "tools/claims-v3/m11/score_m11.py", "lists_checked": _COUNTS, "registration_commits": REG_COMMITS}
    sessions = {}
    for i, d in enumerate(a3_dirs):
        s = read_session_a3(d)
        sid = f"S{i + 1}:{s['pass_dir']}"
        gate = s["start_gate"]
        s["precedence"] = precedence(s["first_launch_ms"])
        if not gate or not gate.get("passed"):
            s["excluded"] = "the start gate (G0) did not pass: no hold ran"
        sessions[sid] = s
    out["sessions"] = sessions
    use = {sid: s for sid, s in sessions.items() if "excluded" not in s}
    out["aifoundry3"] = decide_card_kind(use, "aifoundry3") if use else {"verdict": "NOT SCORED: no session passed its start gate"}
    out["blind"] = all(s["precedence"]["blind"] for s in use.values()) if use else None
    out["label"] = ("blind: every registration and amendment commit precedes every session's first launch record" if out["blind"]
                    else "post hoc: a registration or amendment commit does not precede a session's first launch record")
    return out


def md_summary(res):
    a = res.get("aifoundry3", {})
    L = [f"# M11 on aifoundry3 ({len(res.get('sessions', {}))} session(s)), score_m11.py", "", f"- {res.get('label')}"]
    for sid, s in res.get("sessions", {}).items():
        L.append(f"- {sid}: " + "; ".join(f"{n} P {h.get('P_C')} e {h.get('e_C')} {'scored' if h.get('scored') else 'NOT SCORED ' + str(h.get('why'))}"
                                          for n, h in s["holds"].items()))
    if "HM_LG" in a:
        L += [f"- HM-LG: {a['HM_LG']['verdict']}; A1-4: {a['A1_4']['outcome']} (arm {a['A1_4']['x1p032_arm']})",
              f"- HM-E144: {a['HM_E144']['reading']}; N2 {a['HM_HE']['N2_departs_in_every_session']}",
              f"- HM-CAL: {a['HM_CAL']['verdict']} (D {a['HM_CAL']['D_C']}, tau {a['HM_CAL']['tau_C']}); A2-3: {a['HM_CAL']['A2_3_outcome']}",
              f"- HM-CAL-I8: {a['HM_CAL_I8']['verdict']} (D {a['HM_CAL_I8']['D_C']}, tau {a['HM_CAL_I8']['tau_C']}); A4-3: {a['HM_CAL_I8']['A4_3_outcome']}",
              f"- M11 carries: {a['M11_carries']}"]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ self-test
def synth(P_list, e_list, scored=None, pair_first=True, i8_ok=True, kind="aifoundry3"):
    names = A3.NAMES[kind]
    hs = {}
    for i, nm in enumerate(names):
        ok = True if scored is None else (nm in scored)
        hs[nm] = {"P_C": P_list[i], "e_C": e_list[i], "R_C": P_list[i] + e_list[i], "scored": ok}
    return {"holds": hs, "order": {"pair_first": pair_first, "L1_and_S_ended_before_L2": i8_ok}}


def self_test():
    T = {"lists_checked": _COUNTS}
    probs = []
    POST154 = json.load(open(os.path.join(TREE, "docs", "reports", "data", "2026-11-04-q140e-heat-replicates", "posthoc.json")))["E154"]["holds"]
    # (1) M10's committed per-hold R and e for E154's five and E166's four fitted holds, within 0.001 C, through this scorer's reader
    hl = json.load(open(os.path.join(TREE, "docs", "reports", "data", "2026-11-04-q142m-m10", "heldout-m10.json")))["heat_d_chain_gain"]["holds"]
    want = {(x["session"], x["hold"]): x for x in hl if x["session"] in ("E154", "E166") and x.get("fitted")}
    rep = {}
    for sid, pdir in (("E154", P166.E154P),
                      ("E166", os.path.join(TREE, "docs", "reports", "data", "2026-11-04-e166-heat-replicate-aifoundry3", "aifoundry3", "e166", "p16620"))):
        marks, recs, _ = S166.records(pdir)
        sess = SE.a3_load([pdir])
        tel_t = S166.tel_times(pdir)
        pred_a = FT.predict_session(sess, PQ.TAU, PQ.R3)
        for (ss, hold), w in sorted(want.items()):
            if ss != sid:
                continue
            if hold == "K_O_window":
                hr = recs["K_OL"]
                b10 = P166.window_10min({"procs": hr["procs"], "t0": hr["procs"][0][0]})
                row = read_hold_a3(sess, recs, marks, tel_t, pred_a, "K_OL", b_override=b10)
            else:
                row = read_hold_a3(sess, recs, marks, tel_t, pred_a, hold)
            dR, de = abs(row["R_C"] - w["R_C"]), abs(row["e_C"] - w["e_C"])
            ok = dR <= 0.001 and de <= 0.001
            why = None
            if not ok and sid == "E154" and de <= 0.001:
                # M10 took E154's R from E154's registered scored.json window; section 1 registers R3's window (b = the last process's
                # end). posthoc.json records both for E154: accept only where M10's R is the registered window's and this reader's R is
                # the convention window's, exactly
                ph = POST154[hold]
                if (abs(ph["registered_window"]["measured_rise_C"] - w["R_C"]) <= 0.001
                        and abs(ph["convention_window"]["measured_rise_C"] - row["R_C"]) <= 0.001):
                    ok = True
                    why = (f"R3's window (section 1) reads {row['R_C']}, posthoc.json's convention_window exactly; M10's {round(w['R_C'], 4)} is "
                           f"E154's registered window (posthoc.json registered_window), whose end moved {ph.get('window_end_moved_s')} s")
            rep[f"{sid}|{hold}"] = {"R_C": row["R_C"], "e_C": row["e_C"], "M10_R_C": round(w["R_C"], 4), "M10_e_C": round(w["e_C"], 4),
                                    "dR": round(dR, 6), "de": round(de, 6), "within_0p001": dR <= 0.001 and de <= 0.001,
                                    "accepted": ok, "window_note": why}
            if not ok:
                probs.append(f"{sid} {hold}: R {row['R_C']} vs {w['R_C']}, e {row['e_C']} vs {w['e_C']}")
    T["m10_holds_reproduced"] = {"n": len(rep), "e_all_within_0p001_C": all(v["de"] <= 0.001 for v in rep.values()),
                                 "R_within_0p001_C": sum(1 for v in rep.values() if v["dR"] <= 0.001),
                                 "all_accepted": all(v["accepted"] for v in rep.values()), "holds": rep}
    if len(rep) != 9:
        probs.append(f"{len(rep)} of E154's five and E166's four fitted holds read")
    # (2) post hoc: HM-LG on E154 and E166 as two sessions (their fitted holds; not a registered result)
    gr = {s: [(w["P_C"], w["e_C"]) for (ss, _), w in sorted(want.items()) if ss == s] for s in ("E154", "E166")}
    ph = DPG.lg_test(gr, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF, detail=True)
    T["posthoc_HM_LG_E154_E166"] = {"label": "post hoc: E154 and E166 ran other kinds in another order; no rule reads them",
                                    "verdict": ph["verdict"], "k": ph["k"], "n": ph["n"], "null": ph.get("null"),
                                    "F_slope": r4(ph.get("F_slope")), "F_level": r4(ph.get("F_level")), "F_point": r4(ph.get("F_point"))}
    # (3) synthetic sessions with known answers (A1-4's paths, A2-A4's paths, the reading rules)
    PS = [14.517, 0.695, 9.670, 3.459, 8.354]
    PW = [11.723, 0.986, 9.778, 3.471, 8.439]
    nz1 = [0.02, -0.03, 0.01, 0.02, -0.02]
    nz2 = [-0.01, 0.02, -0.02, 0.01, 0.01]

    def line(a, g, ps, nz):
        return [a + g * p + x for p, x in zip(ps, nz)]
    cases = {
        "a common 3.2% gain in both sessions": ({"S1": synth(PS, line(0.0, 0.032, PS, nz1)), "S2": synth(PW, line(0.0, 0.032, PW, nz2))},
                                                {"HM_LG": "GAIN", "A1_4": "gain enters", "arm": "replaced", "carries": "A1-4's common term (gain enters)"}),
        "a common 0.27 C level in both sessions": ({"S1": synth(PS, line(0.27, 0.0, PS, nz1)), "S2": synth(PW, line(0.27, 0.0, PW, nz2))},
                                                   {"HM_LG": "LEVEL", "A1_4": "level enters", "arm": "retired", "carries": "A1-4's common term (level enters)"}),
        "E154's line, then E166's (the premise holds)": (
            {"S1": synth(PS, line(-0.229, 0.0572, PS, nz1)), "S2": synth(PW, line(0.395, -0.0143, PW, nz2))},
            {"HM_LG": "BOTH", "A1_4": "nothing: the sessions differ", "HM_CAL": "BETTER", "A2_3": A3.ENTERS, "HM_E144": "DOES NOT REPEAT",
             "carries": "A2's in-session calibration (H_E and Z)"}),
        "E154's line, then E166's, H_E read by the chain (section 0.1's case)": (
            {"S1": synth(PS, [0.02] + line(-0.229, 0.0572, PS, nz1)[1:]), "S2": synth(PW, [-0.01] + line(0.395, -0.0143, PW, nz2)[1:])},
            {"HM_E144": "REPEATS", "HM_CAL_I8": "BETTER", "A4_3": A4.ENTERS_I8, "carries": "A4's in-session calibration (L1 and S, read on L2)"}),
        "no effect (noise only)": ({"S1": synth(PS, nz1), "S2": synth(PW, nz2)},
                                   {"HM_LG": "NOT SEPARATED", "A1_4": "nothing: NOT SEPARATED", "arm": "retired",
                                    "carries": "nothing: the chain unscaled stays M11's primary"}),
        "one session (E154's line)": ({"S1": synth(PS, line(-0.229, 0.0572, PS, nz1))},
                                      {"A1_4": "nothing: one session (a candidate)",
                                       "carries": "nothing: one session (the readings are a candidate for the next session)"}),
        "H_E not scored in S1 (HM-CAL reads S2 only; HM-CAL-I8 reads both)": (
            {"S1": synth(PS, line(-0.229, 0.0572, PS, nz1), scored=("Z", "L1", "S", "L2")), "S2": synth(PW, line(0.395, -0.0143, PW, nz2))},
            {"HM_CAL_S1": "NOT SCORED", "HM_CAL_k": 1, "HM_CAL_I8_k": 2}),
        "the pair run in the other order in both sessions": (
            {"S1": synth(PS, line(-0.229, 0.0572, PS, nz1), pair_first=False), "S2": synth(PW, line(0.395, -0.0143, PW, nz2), pair_first=False)},
            {"HM_CAL": "NOT SCORED", "A2_3": "nothing from A2: NOT SCORED"}),
        "L2 not scored in both sessions": (
            {"S1": synth(PS, line(-0.229, 0.0572, PS, nz1), scored=("H_E", "Z", "L1", "S")),
             "S2": synth(PW, line(0.395, -0.0143, PW, nz2), scored=("H_E", "Z", "L1", "S"))},
            {"HM_CAL_I8": "NOT SCORED"}),
        "L2 run before S ended in both sessions": (
            {"S1": synth(PS, line(-0.229, 0.0572, PS, nz1), i8_ok=False), "S2": synth(PW, line(0.395, -0.0143, PW, nz2), i8_ok=False)},
            {"HM_CAL_I8": "NOT SCORED"}),
        "three holds scored in S1 (HM-LG counts S2 only)": (
            {"S1": synth(PS, line(0.0, 0.032, PS, nz1), scored=("H_E", "Z", "L1")), "S2": synth(PW, line(0.0, 0.032, PW, nz2))},
            {"HM_LG_k": 1}),
    }
    syn = {}
    for name, (ss, exp) in cases.items():
        r = decide_card_kind(ss, "aifoundry3")
        got = {"HM_LG": r["HM_LG"]["verdict"], "A1_4": r["A1_4"]["outcome"], "arm": r["A1_4"]["x1p032_arm"], "HM_CAL": r["HM_CAL"]["verdict"],
               "A2_3": r["HM_CAL"]["A2_3_outcome"], "HM_E144": r["HM_E144"]["reading"], "HM_CAL_I8": r["HM_CAL_I8"]["verdict"],
               "A4_3": r["HM_CAL_I8"]["A4_3_outcome"], "carries": r["M11_carries"], "HM_LG_k": r["HM_LG"]["k"],
               "HM_CAL_S1": "NOT SCORED" if "not_scored" in r["HM_CAL"]["per_session"].get("S1", {}) else "read",
               "HM_CAL_k": sum(1 for v in r["HM_CAL"]["per_session"].values() if "not_scored" not in v),
               "HM_CAL_I8_k": sum(1 for v in r["HM_CAL_I8"]["per_session"].values() if "not_scored" not in v)}
        ok = all(got[k] == v for k, v in exp.items())
        syn[name] = {"expected": exp, "got": {k: got[k] for k in exp}, "pass": ok}
        if not ok:
            probs.append(f"synthetic '{name}': expected {exp}, got { {k: got[k] for k in exp} }")
    T["synthetic"] = syn
    # (4) one committed cell each of A2, A3 and A4, from v2's committed draws, through decide_card_kind
    a2c = json.load(open(os.path.join(TREE, A3.A2_OUT_REL)))
    a3c = json.load(open(os.path.join(TREE, A4.A3_OUT_REL)))
    a4c = json.load(open(os.path.join(HERE, "design-power-heat-a4.json")))
    des = a4c["plan_P_C"][A4.A3X2]
    tr = dict(V2.truths_as_committed())
    mx = A4.MIXED
    cells = {}
    for tag, extra in (("premise holds", None), ("H_E read by the chain", A4.he_chain_extra(des, tr[mx]))):
        rng = random.Random(f"M11-HM-LG|{A4.A3X2}|{0.0884:.4f}|{mx}")
        cnt = {"HM_CAL_BETTER": 0, "HM_CAL_NOT_RESOLVED": 0, "HM_CAL_WORSE": 0, "A2_enters": 0, "REPEATS": 0, "I8_BETTER": 0, "I8_enters": 0,
               "per_session_calibration": 0}
        N = A4.DRAWS
        for _ in range(N):
            groups = D.sim_sessions(des, tr[mx], SIGMA["aifoundry3"], rng)
            if extra is not None:
                groups = {i: [(p, e + x) for (p, e), x in zip(pts, extra[i])] for i, pts in groups.items()}
            ss = {f"S{i}": synth([p for p, _ in pts], [e for _, e in pts]) for i, pts in groups.items()}
            r = decide_card_kind(ss, "aifoundry3")
            v = r["HM_CAL"]["verdict"]
            cnt["HM_CAL_BETTER"] += v == "BETTER"
            cnt["HM_CAL_NOT_RESOLVED"] += v == "NOT RESOLVED"
            cnt["HM_CAL_WORSE"] += v == "WORSE"
            cnt["A2_enters"] += r["HM_CAL"]["A2_3_outcome"] == A3.ENTERS
            cnt["REPEATS"] += r["HM_E144"]["reading"] == "REPEATS"
            cnt["I8_BETTER"] += r["HM_CAL_I8"]["verdict"] == "BETTER"
            cnt["I8_enters"] += r["HM_CAL_I8"]["A4_3_outcome"] == A4.ENTERS_I8
            cnt["per_session_calibration"] += r["HM_CAL"]["A2_3_outcome"] == A3.ENTERS or r["HM_CAL_I8"]["A4_3_outcome"] == A4.ENTERS_I8
        cells[tag] = {k: round(100.0 * v / N, 1) for k, v in cnt.items()}
    c = cells
    com = {
        "A2 (design-power-heat-a2.json plan|0.0884|mixed: HM-CAL B/NR/W, enters)":
            ((c["premise holds"]["HM_CAL_BETTER"], c["premise holds"]["HM_CAL_NOT_RESOLVED"], c["premise holds"]["HM_CAL_WORSE"],
              c["premise holds"]["A2_enters"]),
             (a2c["plan"]["0.0884"][mx]["HM_CAL"]["both"]["BETTER"], a2c["plan"]["0.0884"][mx]["HM_CAL"]["both"]["NOT RESOLVED"],
              a2c["plan"]["0.0884"][mx]["HM_CAL"]["both"]["WORSE"],
              a3c["a2_cells"][f"plan|0.0884|{mx}"]["a3"]["exact_t"]["with_A2_M11_carries"].get(A3.ENTERS, 0.0))),
        "A3 (design-power-heat-a3.json premise_a3, section 0.1's case: HM-CAL BETTER, enters, REPEATS)":
            ((c["H_E read by the chain"]["HM_CAL_BETTER"], c["H_E read by the chain"]["A2_enters"], c["H_E read by the chain"]["REPEATS"]),
             (a3c["premise_a3"][f"{mx}|{A4.HE_CHAIN}"]["a2_form"]["HM_CAL"]["both"]["BETTER"],
              a3c["premise_a3"][f"{mx}|{A4.HE_CHAIN}"]["a3"]["exact_t"]["with_A2_M11_carries"].get(A3.ENTERS, 0.0),
              a3c["premise_a3"][f"{mx}|{A4.HE_CHAIN}"]["a3"]["HM_E144"]["repeats_in_every_session"])),
        "A4 (design-power-heat-a4.json, section 0.1's case: I8 BETTER, I8 enters, a per-session calibration)":
            ((c["H_E read by the chain"]["I8_BETTER"], c["H_E read by the chain"]["I8_enters"], c["H_E read by the chain"]["per_session_calibration"]),
             (a4c["plan"]["0.0884"][A4.HE_CHAIN][mx]["HM_CAL_I8"]["BETTER"],
              a4c["plan"]["0.0884"][A4.HE_CHAIN][mx]["with_A4_M11_carries"].get(A4.ENTERS_I8, 0.0),
              a4c["plan"]["0.0884"][A4.HE_CHAIN][mx]["a_per_session_calibration_enters"])),
    }
    T["committed_cells"] = {k: {"this_scorer": list(v[0]), "committed": list(v[1]), "equal": list(v[0]) == list(v[1])} for k, v in com.items()}
    for k, v in T["committed_cells"].items():
        if not v["equal"]:
            probs.append(f"{k}: {v['this_scorer']} != {v['committed']}")
    # (5) the precedence check on two synthetic first-launch times: now (every commit precedes it) and one second before A4's commit
    import time
    rc, t4 = git("log", "-1", "--format=%ct", REG_COMMITS["A4"])
    pn = precedence(int(time.time() * 1000))
    pb = precedence((int(t4) - 1) * 1000) if rc == 0 and t4 else {"blind": None}
    T["precedence_synthetic"] = {"now": pn["blind"], "one_second_before_A4": pb["blind"],
                                 "ancestors": {k: v["ancestor_of_HEAD"] for k, v in pn.items() if isinstance(v, dict)}}
    if pn["blind"] is not True or pb["blind"] is not False:
        probs.append(f"precedence: now {pn['blind']}, one second before A4 {pb['blind']} (want True, False)")
    T["problems"] = probs
    T["pass"] = not probs
    return T


def main():
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else None
    mp = args[args.index("--md") + 1] if "--md" in args else None
    if "--self-test" in args:
        T = self_test()
        print(f"M11 scorer self-test: lists " + ", ".join(f"{k} {v}" for k, v in T["lists_checked"].items()))
        mh = T["m10_holds_reproduced"]
        print(f"  M10's per-hold R and e ({mh['n']} holds): e within 0.001 C in {'all' if mh['e_all_within_0p001_C'] else 'NOT all'}, R within "
              f"0.001 C in {mh['R_within_0p001_C']}; {'every hold accepted' if mh['all_accepted'] else 'NOT every hold accepted'}")
        for k, v in mh["holds"].items():
            print(f"    {k:18s} R {v['R_C']:.3f} (M10 {v['M10_R_C']:.4f})  e {v['e_C']:+.3f} (M10 {v['M10_e_C']:+.4f})  "
                  + ("ok" if v["within_0p001"] else ("accepted: " + v["window_note"] if v["accepted"] else "DIFFERS")))
        ph = T["posthoc_HM_LG_E154_E166"]
        print(f"  post hoc (not a registered result): HM-LG on E154 and E166 as two sessions reads {ph['verdict']} (k {ph['k']}, n {ph['n']}; "
              f"F_slope {ph['F_slope']}, F_level {ph['F_level']}, point {ph['F_point']}; {ph['null']})")
        for k, v in T["synthetic"].items():
            print(f"  synthetic: {k:70s} {'PASS' if v['pass'] else 'FAIL'}  {json.dumps(v['got'])}")
        for k, v in T["committed_cells"].items():
            print(f"  committed cell: {k}: {v['this_scorer']} against {v['committed']}: {'equal' if v['equal'] else 'DIFFERS'}")
        print(f"  precedence (git): a first launch now reads blind {T['precedence_synthetic']['now']}; one second before A4's commit "
              f"{T['precedence_synthetic']['one_second_before_A4']}; every registration commit an ancestor of HEAD: "
              f"{all(T['precedence_synthetic']['ancestors'].values())}")
        print("SELF-TEST " + ("PASS" if T["pass"] else "FAIL: " + "; ".join(T["problems"])))
        if jp:
            json.dump(T, open(jp, "w"), indent=1, sort_keys=True)
        sys.exit(0 if T["pass"] else 1)
    if not args or args[0] != "score":
        raise SystemExit(__doc__)
    a3 = [args[i + 1] for i, x in enumerate(args) if x == "--a3"]
    if any(x == "--a2" for x in args):
        raise SystemExit("M11 scorer: no aifoundry2 reader here (E177's kit is its own lane); refused")
    if not a3:
        raise SystemExit("M11 scorer: name at least one aifoundry3 pass with --a3")
    res = score(a3)
    if jp:
        json.dump(res, open(jp, "w"), indent=1, sort_keys=True, default=str)
    if mp:
        open(mp, "w").write(md_summary(res))
    print(md_summary(res))


if __name__ == "__main__":
    main()
