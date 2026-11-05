#!/usr/bin/env python3
"""Q143(k)'s fix pass: M11's scorer v2 for heat over minutes (tools/claims-v3/m11/REGISTRATION.md section 13 step 1, as amended by A1-A5),
desk only (the Intel). score_m11.py (lab 03582d2f) stays as committed: v2 imports it unchanged, and every reading and decision v1 makes is
v2's too. What v2 adds or changes (the verifier of Q143(k), its faults 1, 3, 4 and 5; dated amendment A5, lab 9b084c66):

  A5   HM-CAL-AG and HM-I8-AG (design_power_heat_a5.lines_agree, unchanged) beside HM-CAL and HM-CAL-I8, and the form an entry is
       stated in (A5-3: "per session" only on the ENTERING calibration's own DIFFER, else "common to the sessions, or not separated").
       An entry made while HM-LG counted fewer than two sessions is labelled "HM-LG read one session" (A5-4).
  F3   A4-3's printed reason where HM-E144 or HM-CAL-I8 reads NOT SCORED (A5-4), read before design_power_heat_a4.i8_entry. The decision
       is v1's: v2 refuses (exit 1) if its A4-3 decision ever differs from v1's.
  F4   (a) the lines first: every session's A2 line (its pair H_E and Z) is written to the lines file before any later hold's e is read,
       and every session's A4 line (L1 and S) before any L2's e is read. That is three stages, each appended and fsync'd, with the
       reading order recorded in the output. (b) A2's calibrated miss on L2 alone, printed beside RMS_c(I8). (c) The self-test covers all
       ten of A4-8's read-rule cases (design-power-heat-a4.txt section 2). The lines file's values are checked against the decision's
       lines: on E154's committed pass under a second renaming (REN2, where A4's line is read), and on 4,000 synthetic sessions bit for
       bit (the fix pass's takeover, Thu 5 Nov 2026 about 14:40 PST: under the first renaming both lines are null on E154's pass, so
       the value check there never ran).
  F5   The self-test adds A1-4's BOTH paths that carry a term (both enter; gain, or level, enters refitted alone), on noise orthogonal to
       each session's own line (the verifier's cases A1o, A2o, A2p).

It checks SHA256SUMS-a5 and SHA256SUMS-score-m11 before it reads anything (v1, on import, checks SHA256SUMS, -m11, -a1 ... -a4, M11's other
lists and its pinned reader), and counts A5's commit in the blind precedence.

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v2.py score --a3 <pass dir> [--a3 <pass dir>] --lines <out.jsonl> [--json <out>] [--md <out>]
    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v2.py --self-test --workdir <a new scratch dir> [--json <out>]
Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import shutil  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
V2_LISTS = ("SHA256SUMS-a5", "SHA256SUMS-score-m11")
A5_COMMIT = "9b084c66"


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _check_v2_lists():
    counts, bad = {}, []
    for name in V2_LISTS:
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
            if not os.path.exists(q) or _sha(q) != parts[0]:
                bad.append(f"{name}: {parts[1]} differs")
        counts[name] = n
    return counts, bad


_V2_COUNTS, _V2_BAD = _check_v2_lists()
if _V2_BAD:
    raise SystemExit("M11 scorer v2 REFUSED: a registered file differs:\n  " + "\n  ".join(_V2_BAD))

sys.path.insert(0, HERE)
import score_m11 as V1  # noqa: E402  (03582d2f, unchanged: on import it checks M11's lists and its pinned reader, imports A4 and score_e166)

_saved = list(sys.argv)
sys.argv = [os.path.join(HERE, "design_power_heat_a5.py"), TREE]   # A5 reads argv[1] (the top directory) at import; its main() never runs
import design_power_heat_a5 as A5  # noqa: E402  (9b084c66, unchanged: it checks SHA256SUMS-a4 and imports A4 unchanged)
sys.argv = _saved

A4, A3, A2, VD2, D, DPG = V1.A4, V1.A3, V1.A2, V1.V2, V1.D, V1.DPG
np = V1.np
r4, rms = V1.r4, V1.rms
NAMES_A3 = V1.NAMES_A3
REG_COMMITS = dict(V1.REG_COMMITS)
REG_COMMITS["A5"] = A5_COMMIT
FORM_PER, FORM_COMMON = A5.FORM_PER, A5.FORM_COMMON
STATEMENT = {FORM_PER: "per session: the read sessions' pair lines differ (A5-3), so heat over minutes on aifoundry3 is set per session for "
                       "the holds in this calibration's scope, and each session's own pair reads it",
             FORM_COMMON: "common to the sessions, or not separated: the read sessions' pair lines read as one (A5-3); a common line or "
                          "per-session lines this design cannot separate. M11 does not say heat over minutes is set per session; the pooled "
                          "line is a candidate common term, never carried"}


# ------------------------------------------------------------------------------------------------ F4 (a): the staged reading
def _now():
    return {"wall": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "epoch_s": round(time.time(), 3)}


class LinesFile:
    """the lines file: one JSON line per stage, appended and fsync'd before the next stage reads anything"""

    def __init__(self, path):
        self.path = path
        with open(path, "w"):
            pass

    def write(self, rec):
        with open(self.path, "a") as f:
            f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())


def _context(pass_dir):
    """what v1's read_session_a3 loads for a pass before it reads any hold (records, the session, telemetry times, arm A's prediction)"""
    marks, recs, src = V1.S166.records(pass_dir)
    sess = V1.SE.a3_load([pass_dir])
    tel_t = V1.S166.tel_times(pass_dir)
    pred_a = V1.FT.predict_session(sess, V1.PQ.TAU, V1.PQ.R3)
    return {"pass_dir": pass_dir, "marks": marks, "recs": recs, "src": src, "sess": sess, "tel_t": tel_t, "pred_a": pred_a}


def _order_from_records(c):
    """the launch order from the process records alone, before any hold's e is read: v1's launch_order on the two fields it reads from
    read_hold_a3's rows (a hold's first launch and its last process's end), taken from the same records"""
    by = {h["name"] for h in c["sess"]["holds"]}
    stub = {}
    for nm in NAMES_A3:
        if nm not in by:
            stub[nm] = {"scored": False}
            continue
        hr = c["recs"].get(nm) or {}
        procs = hr.get("procs") or []
        stub[nm] = {"first_launch_s": procs[0][0] if procs else None, "b_last_process_end": hr.get("b")}
    return V1.launch_order(stub)


def _read(c, nm, sid, log):
    log.append(f"read {nm} of {sid}")
    return V1.read_hold_a3(c["sess"], c["recs"], c["marks"], c["tel_t"], c["pred_a"], nm)


def _a2_line(rows, order):
    """stage 1: A2-1's line through the session's pair H_E and Z (A3-6's names), from those two holds only"""
    he, z = rows["H_E"], rows["Z"]
    if not (he.get("scored") and z.get("scored")):
        return {"line": None, "why": "a pair hold (H_E or Z) is not scored"}
    if not order["pair_first"]:
        return {"line": None, "why": "its pair was not run first (a reordering, A2-7)"}
    (p1, e1), (p2, e2) = (he["P_C"], he["e_C"]), (z["P_C"], z["e_C"])
    if abs(p1 - p2) < A2.MIN_PAIR_SPAN_C:
        return {"line": None, "why": f"the pair spans under {A2.MIN_PAIR_SPAN_C} C of P"}
    a, g = A2.cal_line([(p1, e1), (p2, e2)], "both")
    return {"line": {"a_C": a, "g": g}, "pair": {"H_E": [p1, e1], "Z": [p2, e2]},
            "note": "the session is read only if at least 2 later holds are scored (known after stage 3)"}


def _a4_line(rows, order):
    """stage 2: A4-1's line through L1 and S, from those two holds only (L2's place in the span is read after stage 3)"""
    l1, s = rows["L1"], rows["S"]
    if not (l1.get("scored") and s.get("scored")):
        return {"line": None, "why": "L1 or S is not scored"}
    if not order["L1_and_S_ended_before_L2"]:
        return {"line": None, "why": "L1 and S did not both end before L2's first launch"}
    (p1, e1), (p2, e2) = (l1["P_C"], l1["e_C"]), (s["P_C"], s["e_C"])
    span = abs(p1 - p2)
    if span < A4.I8_MIN_SPAN_C:
        return {"line": None, "why": f"the pair spans {span:.3f} C of P, under {A4.I8_MIN_SPAN_C} C"}
    g = (e1 - e2) / (p1 - p2)
    return {"line": {"a_C": e2 - g * p2, "g": g}, "pair": {"L1": [p1, e1], "S": [p2, e2]}, "span_C": span,
            "note": "L2's P inside the pair's span is read after stage 3"}


def _session_dict(c, holds):
    """v1's read_session_a3 result, line for line, from the staged rows"""
    marks, sess = c["marks"], c["sess"]
    gate = [m for m in marks if m.get("kind") == "start_gate"]
    g, T = sess["g"], sess["T"]
    r0 = sess["rests"][0] if sess["rests"] else None
    drift = None
    if r0 is not None:
        k = (g >= r0["t1"] - 240.0) & (g < r0["t1"])
        if k.sum() >= 10:
            drift = float(np.polyfit(g[k] - g[k][0], T[k], 1)[0]) * 600.0
    launches = [m["t_start_ms"] for m in marks if m.get("kind") == "launch"]
    return {"pass_dir": os.path.basename(os.path.normpath(c["pass_dir"])), "card_kind": "aifoundry3", "records_from": c["src"],
            "start_gate": gate[-1] if gate else None, "first_launch_ms": min(launches) if launches else None,
            "room_drift_over_R0_C_per_10min": r4(drift), "holds": holds, "order": V1.launch_order(holds)}


def read_sessions_staged(a3_dirs, lines_path):
    """every session's holds in three stages; returns (sessions in v1's form keyed as v1 keys them, the reading order)"""
    log = []
    lf = LinesFile(lines_path)
    ctx = {}
    for i, d in enumerate(a3_dirs):
        ctx[f"S{i + 1}:{os.path.basename(os.path.normpath(d))}"] = _context(d)
    order = {sid: _order_from_records(c) for sid, c in ctx.items()}
    rows = {sid: {} for sid in ctx}
    st = {}
    for sid, c in ctx.items():
        for nm in ("H_E", "Z"):
            rows[sid][nm] = _read(c, nm, sid, log)
        st[sid] = _a2_line(rows[sid], order[sid])
    lf.write({"stage": 1, "what": "A2's line per session through its pair H_E and Z (A2-1, A3-6), written before any later hold's e is read",
              "t": _now(), "sessions": st, "order_from_records": order})
    log.append("stage 1 written: A2's lines")
    st = {}
    for sid, c in ctx.items():
        for nm in ("L1", "S"):
            rows[sid][nm] = _read(c, nm, sid, log)
        st[sid] = _a4_line(rows[sid], order[sid])
    lf.write({"stage": 2, "what": "A4's line per session through L1 and S (A4-1), written before any L2's e is read", "t": _now(), "sessions": st})
    log.append("stage 2 written: A4's lines")
    for sid, c in ctx.items():
        rows[sid]["L2"] = _read(c, "L2", sid, log)
    lf.write({"stage": 3, "what": "L2 read; every reading follows in the scorer's JSON", "t": _now(),
              "L2": {sid: {"scored": r["L2"].get("scored"), "P_C": r["L2"].get("P_C"), "e_C": r["L2"].get("e_C")} for sid, r in rows.items()}})
    log.append("stage 3 written: L2 read")
    sessions = {sid: _session_dict(c, {nm: rows[sid][nm] for nm in NAMES_A3}) for sid, c in ctx.items()}
    return sessions, log


# ------------------------------------------------------------------------------------------------ the rules: v1's, then A5 and F3/F4 (b)
def _ag_out(ag, lines, pair_names):
    o = {"pair": list(pair_names), "verdict": ag["verdict"], "k": ag["k"],
         "per_session_line": {s: {"a_C": r4(v[0]), "g": r4(v[1])} for s, v in sorted(lines.items())}}
    if ag["verdict"] != "NOT SCORED":
        o.update(X2=r4(ag["X2"]), df=ag["df"], chi2_95_point=r4(ag["point"]),
                 pooled_line={"a_C": r4(ag["pooled_a"]), "g": r4(ag["pooled_g"]), "cov": [[float(x) for x in row] for row in ag["pooled_cov"]]})
    return o


def entry_form(e2, oi, ag_cal, ag_i8):
    """A5-3: (which calibration enters, its stated form), or (None, None); design_power_heat_a5.entry_form's rule"""
    if e2 == A3.ENTERS:
        return "A2", FORM_PER if ag_cal["verdict"] == "DIFFER" else FORM_COMMON
    if oi == A4.ENTERS_I8:
        return "A4", FORM_PER if ag_i8["verdict"] == "DIFFER" else FORM_COMMON
    return None, None


def a4_outcome(o, e2, rep, res, i8, sigma_c):
    """A4-3's outcome with A5-4's reasons: E1, E2, E3 (HM-E144 NOT SCORED, then DOES NOT REPEAT), HM-CAL-I8 NOT SCORED, then
    design_power_heat_a4.i8_entry, which reads E3-E6 in A4-3's order and agrees with this wherever rep is read and HM-CAL-I8 is scored"""
    if o in A2.COMMON_OUTCOMES:
        return "A1-4's common term"
    if e2 == A3.ENTERS:
        return "A2's calibration"
    if rep is None:
        return "nothing from A4: HM-E144 NOT SCORED"
    if not rep:
        return "nothing from A4: HM-E144 DOES NOT REPEAT"
    if i8["verdict"] == "NOT SCORED":
        return "nothing from A4: HM-CAL-I8 NOT SCORED"
    return A4.i8_entry(o, e2, rep, res, i8, sigma_c)


def decide_card_kind(sessions, kind):
    """v1's decide_card_kind, unchanged, then A5's readings and form, A4-3's reasons (A5-4) and A2's line on L2"""
    out = V1.decide_card_kind(sessions, kind)
    sigma_c = V1.SIGMA[kind]
    names = A3.NAMES[kind]
    named, groups = {}, {}
    for sid in sorted(sessions):
        hs = sessions[sid]["holds"]
        nm = {n: (hs[n]["P_C"], hs[n]["e_C"]) for n in names if hs.get(n, {}).get("scored")}
        named[sid] = nm
        groups[sid] = [nm[n] for n in names if n in nm]
    res = DPG.lg_test(groups, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF, detail=True)
    o, e2 = out["A1_4"]["outcome"], out["HM_CAL"]["A2_3_outcome"]
    cal_read = {}
    for sid in sorted(sessions):
        r, _ = A3.cal_by_name(named[sid], kind, "both", sigma_c, pair_first=sessions[sid]["order"]["pair_first"])
        if r is not None:
            cal_read[sid] = r
    p_name, z_name = A3.PAIR[kind]
    ag_cal = A5.lines_agree({sid: (named[sid][p_name], named[sid][z_name]) for sid in cal_read}, sigma_c)
    out["HM_CAL_AG"] = _ag_out(ag_cal, {s: (r["a"], r["g"]) for s, r in cal_read.items()}, (p_name, z_name))
    he_on = kind == "aifoundry3"
    oi = None
    ag_i8 = {"verdict": "NOT SCORED", "k": 0}
    if he_on:
        i8 = A4.hm_cal_i8({sid: (named[sid], sessions[sid]["order"]["L1_and_S_ended_before_L2"]) for sid in sorted(sessions)}, sigma_c)
        i8_read = {sid: v for sid, v in i8["per"].items() if "not_scored" not in v}
        ag_i8 = A5.lines_agree({sid: (named[sid]["L1"], named[sid]["S"]) for sid in i8_read}, sigma_c)
        out["HM_I8_AG"] = _ag_out(ag_i8, {s: (v["a"], v["g"]) for s, v in i8_read.items()}, ("L1", "S"))
        rr = out["HM_E144"]["reading"]
        rep = None if rr == "NOT SCORED" else rr == "REPEATS"
        oi = a4_outcome(o, e2, rep, res, i8, sigma_c)
        v1_oi = out["HM_CAL_I8"]["A4_3_outcome"]
        if (oi == A4.ENTERS_I8) != (v1_oi == A4.ENTERS_I8):
            raise SystemExit(f"M11 scorer v2 REFUSED: its A4-3 decision ({oi}) differs from score_m11.py's ({v1_oi})")
        out["HM_CAL_I8"]["A4_3_outcome_as_score_m11_printed"] = v1_oi
        out["HM_CAL_I8"]["A4_3_outcome"] = oi
        a2l2 = {sid: named[sid]["L2"][1] - r["a"] - r["g"] * named[sid]["L2"][0] for sid, r in cal_read.items() if "L2" in named[sid]}
        out["HM_CAL_I8"]["A2_line_on_L2"] = {"per_session_e_c_C": {s: r4(v) for s, v in sorted(a2l2.items())}, "n": len(a2l2),
                                             "rms_C": r4(rms(list(a2l2.values()))),
                                             "note": "A2's line (H_E and Z) read on L2 alone, beside RMS_c(I8) (A4-2, A4-8)"}
    who, form = entry_form(e2, oi, ag_cal, ag_i8)
    out["M11_form"] = {"entering": who, "form": form,
                       "statement": STATEMENT[form] if form else None,
                       "read_from": ({"A2": "HM-CAL-AG", "A4": "HM-I8-AG"}[who] if who else None),
                       "HM_LG_read_one_session": bool(who) and (out["HM_LG"].get("k") or 0) < 2,
                       "rule": "A5-3: an entry is stated per session only on the entering calibration's own DIFFER; the entry and what M11 "
                               "carries are A2-3's and A4-3's, unchanged (one way only)"}
    return out


# ------------------------------------------------------------------------------------------------ precedence (v1's, with A5)
def precedence(first_launch_ms):
    out = {}
    for k, c in REG_COMMITS.items():
        rc, t = V1.git("log", "-1", "--format=%ct", c)
        rca, _ = V1.git("merge-base", "--is-ancestor", c, "HEAD")
        ok = rc == 0 and rca == 0 and first_launch_ms is not None and int(t) * 1000 < first_launch_ms
        out[k] = {"commit": c, "commit_epoch_s": int(t) if rc == 0 and t else None, "ancestor_of_HEAD": rca == 0, "precedes_first_launch": ok}
    out["blind"] = all(v["precedes_first_launch"] for v in out.values() if isinstance(v, dict))
    return out


# ------------------------------------------------------------------------------------------------ the score
def score(a3_dirs, lines_path):
    out = {"scorer": "tools/claims-v3/m11/score_m11_v2.py", "imports_unchanged": "tools/claims-v3/m11/score_m11.py",
           "lists_checked": dict(V1._COUNTS, **_V2_COUNTS), "registration_commits": REG_COMMITS}
    sessions, log = read_sessions_staged(a3_dirs, lines_path)
    out["reading_order"] = log
    out["lines_file"] = os.path.basename(lines_path)
    for sid, s in sessions.items():
        s["precedence"] = precedence(s["first_launch_ms"])
        gate = s["start_gate"]
        if not gate or not gate.get("passed"):
            s["excluded"] = "the start gate (G0) did not pass: no hold ran"
    out["sessions"] = sessions
    use = {sid: s for sid, s in sessions.items() if "excluded" not in s}
    out["aifoundry3"] = decide_card_kind(use, "aifoundry3") if use else {"verdict": "NOT SCORED: no session passed its start gate"}
    out["blind"] = all(s["precedence"]["blind"] for s in use.values()) if use else None
    out["label"] = ("blind: every registration and amendment commit (A1-A5) precedes every session's first launch record" if out["blind"]
                    else "post hoc: a registration or amendment commit does not precede a session's first launch record")
    return out


def md_summary(res):
    a = res.get("aifoundry3", {})
    L = [f"# M11 on aifoundry3 ({len(res.get('sessions', {}))} session(s)), score_m11_v2.py", "", f"- {res.get('label')}"]
    for sid, s in res.get("sessions", {}).items():
        L.append(f"- {sid}: " + "; ".join(f"{n} P {h.get('P_C')} e {h.get('e_C')} {'scored' if h.get('scored') else 'NOT SCORED ' + str(h.get('why'))}"
                                          for n, h in s["holds"].items()))
    if "HM_LG" in a:
        f = a["M11_form"]
        L += [f"- HM-LG: {a['HM_LG']['verdict']} (k {a['HM_LG']['k']}); A1-4: {a['A1_4']['outcome']} (arm {a['A1_4']['x1p032_arm']})",
              f"- HM-E144: {a['HM_E144']['reading']}; N2 {a['HM_HE']['N2_departs_in_every_session']}",
              f"- HM-CAL: {a['HM_CAL']['verdict']} (D {a['HM_CAL']['D_C']}, tau {a['HM_CAL']['tau_C']}); A2-3: {a['HM_CAL']['A2_3_outcome']}; "
              f"HM-CAL-AG: {a['HM_CAL_AG']['verdict']} (X2 {a['HM_CAL_AG'].get('X2')}, point {a['HM_CAL_AG'].get('chi2_95_point')})",
              f"- HM-CAL-I8: {a['HM_CAL_I8']['verdict']} (D {a['HM_CAL_I8']['D_C']}, tau {a['HM_CAL_I8']['tau_C']}); A4-3: "
              f"{a['HM_CAL_I8']['A4_3_outcome']}; HM-I8-AG: {a['HM_I8_AG']['verdict']} (X2 {a['HM_I8_AG'].get('X2')}, point "
              f"{a['HM_I8_AG'].get('chi2_95_point')}); A2's line on L2: rms {a['HM_CAL_I8']['A2_line_on_L2']['rms_C']} C over "
              f"{a['HM_CAL_I8']['A2_line_on_L2']['n']}",
              f"- M11 carries: {a['M11_carries']}" + (f"; stated: {f['form']} (read from {f['read_from']}"
                                                      + ("; HM-LG read one session" if f["HM_LG_read_one_session"] else "") + ")" if f["form"] else "")]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ self-test
def _orth(v, ps):
    X = np.vstack([np.ones(len(ps)), np.array(ps)]).T
    v = np.array(v, float)
    return [float(x) for x in (v - X @ np.linalg.lstsq(X, v, rcond=None)[0])]


REN = {"H_M": "H_E", "K_S": "Z", "K_Q": "L1", "K_L": "S", "K_O": "L2"}
# the takeover's second renaming (Thu 5 Nov 2026, about 14:40 PST): under REN both staged lines are null on E154's pass (its first two holds
# span 0.511 C, under A2's 6.0 C; K_Q and K_L 1.717 C, under A4's 3.0 C), so the lines file's values were never compared there. Under REN2
# L1 = K_S and S = K_Q span 5.699 C with L2 = K_O inside, so A4's stage-2 line is read on a committed pass and compared with the decision's
# (A2's line stays null: its pair H_M, K_L is not run first, a reordering).
REN2 = {"H_M": "H_E", "K_S": "L1", "K_Q": "S", "K_L": "Z", "K_O": "L2"}


def _renamed_e154(dst, ren=None):
    """E154's committed pass with its five holds renamed to M11's names and a start_gate mark added (the verifier's Part B pass)"""
    ren = REN if ren is None else ren
    src = V1.P166.E154P
    os.makedirs(dst)
    marks = []
    for x in open(os.path.join(src, "marks.jsonl")):
        if not x.strip():
            continue
        m = json.loads(x)
        for key in ("name", "hold", "block"):
            if m.get(key) in ren:
                m[key] = ren[m[key]]
        marks.append(m)
        if m.get("kind") == "room":
            marks.append({"kind": "start_gate", "t_ms": m["t_ms"], "room_c": m["mean34_c"], "max_c": 53.0, "passed": True,
                          "why": "self-test: added to E154's pass (E154 predates G0)"})
    with open(os.path.join(dst, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    with open(os.path.join(src, "runs.jsonl")) as fi, open(os.path.join(dst, "runs.jsonl"), "w") as fo:
        for x in fi:
            if not x.strip():
                continue
            r = json.loads(x)
            if r.get("block") in ren:
                r["block"] = ren[r["block"]]
            fo.write(json.dumps(r) + "\n")
    for fn in ("configs.json", "block.json", "sampler.json", "manifest.txt", "telemetry.jsonl.gz"):
        if os.path.exists(os.path.join(src, fn)):
            shutil.copy2(os.path.join(src, fn), dst)


def _staged_lines_unit(n=4000, seed="M11-v2-selftest|the staged lines against the decision's lines"):
    """the takeover's check of the lines file's values on synthetic sessions: stage 1's _a2_line and stage 2's _a4_line against the frozen
    code the decision reads (design_power_heat_a3.cal_by_name, design_power_heat_a4.cal_i8_by_name), on the same rounded P and e. Where the
    decision reads a session, the stage line is there and equal, bit for bit; where the stage line is null, the decision reads NOT SCORED; a
    stage line the decision does not read is allowed only for a reason known after stage 3 (A2: fewer than 2 later holds scored; A4: L2 not
    scored, or L2's P outside the pair's span). A quarter of the draws sit on a registered line (A2's 6.0 C span, A4's 3.0 C span, L2 at an
    end of the span), within 0.02 C."""
    rr = random.Random(seed)
    sig = V1.SIGMA["aifoundry3"]
    later_names = A3.LATER["aifoundry3"]
    c = {"draws": n, "A2 read, line equal": 0, "A2 line, unread after stage 3": 0, "A2 null, NOT SCORED": 0,
         "A4 read, line equal": 0, "A4 line, unread after stage 3": 0, "A4 null, NOT SCORED": 0}
    bad = []
    for i in range(n):
        P = {nm: rr.uniform(0.3, 16.0) for nm in NAMES_A3}
        edge = rr.random()
        if edge < 0.10:
            P["Z"] = P["H_E"] + rr.choice((-1.0, 1.0)) * (A2.MIN_PAIR_SPAN_C + rr.uniform(-0.02, 0.02))
        elif edge < 0.20:
            P["S"] = P["L1"] + rr.choice((-1.0, 1.0)) * (A4.I8_MIN_SPAN_C + rr.uniform(-0.02, 0.02))
        elif edge < 0.25:
            P["L2"] = rr.choice((P["L1"], P["S"])) + rr.uniform(-0.02, 0.02)
        rows = {nm: {"scored": rr.random() < 0.85, "P_C": round(P[nm], 3), "e_C": round(rr.gauss(0.0, 0.3), 3)} for nm in NAMES_A3}
        order = {"pair_first": rr.random() < 0.85, "L1_and_S_ended_before_L2": rr.random() < 0.85}
        named = {nm: (r["P_C"], r["e_C"]) for nm, r in rows.items() if r["scored"]}
        s1 = _a2_line(rows, order)["line"]
        d2, _ = A3.cal_by_name(named, "aifoundry3", "both", sig, pair_first=order["pair_first"])
        if d2 is not None:
            if s1 is not None and s1["a_C"] == d2["a"] and s1["g"] == d2["g"]:
                c["A2 read, line equal"] += 1
            else:
                bad.append(f"draw {i}: A2 reads the session, stage 1 wrote {s1}, the decision's line ({d2['a']}, {d2['g']})")
        elif s1 is not None:
            if sum(1 for nm in later_names if nm in named) < A2.MIN_LATER:
                c["A2 line, unread after stage 3"] += 1
            else:
                bad.append(f"draw {i}: stage 1 wrote a line the decision does not read, with {A2.MIN_LATER} or more later holds scored")
        else:
            c["A2 null, NOT SCORED"] += 1
        s2 = _a4_line(rows, order)["line"]
        d4, _ = A4.cal_i8_by_name(named, sig, order["L1_and_S_ended_before_L2"])
        if d4 is not None:
            if s2 is not None and s2["a_C"] == d4["a"] and s2["g"] == d4["g"]:
                c["A4 read, line equal"] += 1
            else:
                bad.append(f"draw {i}: A4 reads the session, stage 2 wrote {s2}, the decision's line ({d4['a']}, {d4['g']})")
        elif s2 is not None:
            lo, hi = sorted((named["L1"][0], named["S"][0]))
            if "L2" not in named or not lo <= named["L2"][0] <= hi:
                c["A4 line, unread after stage 3"] += 1
            else:
                bad.append(f"draw {i}: stage 2 wrote a line the decision does not read, with L2 scored inside the span")
        else:
            c["A4 null, NOT SCORED"] += 1
    return c, bad


def self_test(workdir):
    T = {"lists_checked": dict(V1._COUNTS, **_V2_COUNTS)}
    probs = []
    # (0) v1's self-test, unchanged
    t1 = V1.self_test()
    T["v1_self_test"] = {"pass": t1["pass"], "problems": t1["problems"], "synthetic": {k: v["pass"] for k, v in t1["synthetic"].items()},
                         "committed_cells": {k: v["equal"] for k, v in t1["committed_cells"].items()},
                         "m10_holds": {k: t1["m10_holds_reproduced"][k] for k in ("n", "e_all_within_0p001_C", "R_within_0p001_C", "all_accepted")}}
    if not t1["pass"]:
        probs.append("score_m11.py's own self-test fails: " + "; ".join(t1["problems"]))
    syn = V1.synth
    PS = [14.517, 0.695, 9.670, 3.459, 8.354]
    PW = [11.723, 0.986, 9.778, 3.471, 8.439]

    def line(a, g, ps, nz):
        return [a + g * p + x for p, x in zip(ps, nz)]

    def rd(r, which, sid="S1"):
        v = r[which]["per_session"].get(sid, {})
        return ("NOT SCORED: " + v["not_scored"]) if "not_scored" in v else "read"

    # (1) A4-8's ten read-rule cases (design-power-heat-a4.txt section 2), S1 the case and S2 every hold scored, through v2's rules
    le = lambda p: -0.229 + 0.0572 * p  # noqa: E731
    base2 = syn(PW, [le(p) for p in PW])
    cases = [("every hold scored", None, True, {}, "read"),
             ("H_E not scored (A2 reads NOT SCORED; A4 still reads)", ("Z", "L1", "S", "L2"), True, {}, "read"),
             ("L2 not scored", ("H_E", "Z", "L1", "S"), True, {}, "NOT SCORED: L2 is not scored"),
             ("S not scored", ("H_E", "Z", "L1", "L2"), True, {}, "NOT SCORED: S is not scored"),
             ("L1 not scored", ("H_E", "Z", "S", "L2"), True, {}, "NOT SCORED: L1 is not scored"),
             ("L2 run before S ended (a reordering)", None, False, {}, "NOT SCORED: L1 and S did not both end before L2's first launch"),
             ("the pair spans 2.9 C", None, True, {3: PS[2] - 2.9, 4: PS[2] - 1.0}, "NOT SCORED: the pair spans"),
             ("L2's P above L1's (w > 1)", None, True, {4: PS[2] + 0.4}, "NOT SCORED: L2's P"),
             ("L2's P below S's (w < 0)", None, True, {4: PS[3] - 0.4}, "NOT SCORED: L2's P"),
             ("the pair spans exactly 3.0 C, L2 at its middle", None, True, {3: PS[2] - 3.0, 4: PS[2] - 1.5}, "read")]
    rr_ = {}
    for name, scored, ok, moved, want in cases:
        ps = [moved.get(i, p) for i, p in enumerate(PS)]
        r = decide_card_kind({"S1": syn(ps, [le(p) for p in ps], scored=scored, i8_ok=ok), "S2": base2}, "aifoundry3")
        got = rd(r, "HM_CAL_I8")
        good = got.startswith(want)
        rr_[name] = {"want": want, "got": got, "pass": good}
        if not good:
            probs.append(f"read rule '{name}': want {want}, got {got}")
    T["read_rule_cases"] = rr_
    # (2) fault 3's two printed reasons (A5-4), section 0.1's case; the decision is v1's
    nzA = [0.015, -0.02, 0.025, -0.01, 0.005]
    nzB = [-0.02, 0.01, -0.015, 0.02, -0.005]
    s01 = [0.02] + line(-0.229, 0.0572, PS, nzA)[1:]
    s02 = [-0.01] + line(0.395, -0.0143, PW, nzB)[1:]
    reasons = {
        "both sessions' first holds not scored (HM-E144 NOT SCORED)": (
            {"S1": syn(PS, s01, scored=("L1", "S", "L2")), "S2": syn(PW, s02, scored=("L1", "S", "L2"))},
            "nothing from A4: HM-E144 NOT SCORED", "nothing from A4: HM-E144 DOES NOT REPEAT"),
        "L2 launched before S ended in both (HM-CAL-I8 NOT SCORED)": (
            {"S1": syn(PS, s01, i8_ok=False), "S2": syn(PW, s02, i8_ok=False)},
            "nothing from A4: HM-CAL-I8 NOT SCORED", "nothing from A4: the int8 holds' misses read as noise (E4')")}
    T["reasons"] = {}
    for name, (ss, want, v1_was) in reasons.items():
        r = decide_card_kind(ss, "aifoundry3")
        got, v1g = r["HM_CAL_I8"]["A4_3_outcome"], r["HM_CAL_I8"]["A4_3_outcome_as_score_m11_printed"]
        good = got == want and v1g == v1_was and r["M11_carries"] == "nothing: the chain unscaled stays M11's primary"
        T["reasons"][name] = {"want": want, "got": got, "score_m11_printed": v1g, "pass": good}
        if not good:
            probs.append(f"reason '{name}': want {want} (v1 {v1_was}), got {got} (v1 {v1g})")
    # (3) fault 5: A1-4's BOTH paths that carry a term, noise orthogonal to each session's own line (the verifier's A1o, A2o, A2p)
    oA, oB = _orth(nzA, PS), _orth(nzB, PW)
    both = {"a common 0.25 C + 2.5% (A1o)": ((0.25, 0.025), "both enter", "replaced"),
            "a common 0.06 C + 3.0% (A2o)": ((0.06, 0.030), "gain enters (BOTH, refitted alone)", "replaced"),
            "a common 0.30 C + 0.5% (A2p)": ((0.30, 0.005), "level enters (BOTH, refitted alone)", "reported")}
    T["both_paths"] = {}
    for name, ((a, g), want, arm) in both.items():
        r = decide_card_kind({"S1": syn(PS, line(a, g, PS, oA)), "S2": syn(PW, line(a, g, PW, oB))}, "aifoundry3")
        got = (r["HM_LG"]["verdict"], r["A1_4"]["outcome"], r["A1_4"]["x1p032_arm"], r["M11_carries"], r["M11_form"]["form"])
        good = got == ("BOTH", want, arm, f"A1-4's common term ({want})", None)
        T["both_paths"][name] = {"want": ["BOTH", want, arm], "got": list(got), "pass": good}
        if not good:
            probs.append(f"BOTH path '{name}': want BOTH, {want}, {arm}; got {got}")
    # (4) A5: the agreement readings and the form, on synthetic sessions
    a5c = {
        "section 0.1's case, E154's line then E166's (A4 enters; the lines differ)": (
            {"S1": syn(PS, s01), "S2": syn(PW, s02)}, ("A4", FORM_PER, "DIFFER", False)),
        "section 0.1's case, E154's line in both sessions (A4 enters; one line)": (
            {"S1": syn(PS, s01), "S2": syn(PW, [-0.01] + line(-0.229, 0.0572, PW, nzB)[1:])}, ("A4", FORM_COMMON, "AGREE", False)),
        "the premise holds, E154's line then E166's (A2 enters; the lines differ; score_m11.py's own case and noise)": (
            {"S1": syn(PS, line(-0.229, 0.0572, PS, [0.02, -0.03, 0.01, 0.02, -0.02])),
             "S2": syn(PW, line(0.395, -0.0143, PW, [-0.01, 0.02, -0.02, 0.01, 0.01]))}, ("A2", FORM_PER, "DIFFER", False)),
        "section 0.1's case, S1's H_E and Z not scored (HM-LG counts S2; A4 enters on two)": (
            {"S1": syn(PS, s01, scored=("L1", "S", "L2")), "S2": syn(PW, s02)}, ("A4", FORM_PER, "DIFFER", True)),
        "one session (nothing enters; both readings NOT SCORED)": ({"S1": syn(PS, s01)}, (None, None, "NOT SCORED", False))}
    T["a5_cases"] = {}
    for name, (ss, (who, form, agv, one)) in a5c.items():
        r = decide_card_kind(ss, "aifoundry3")
        f = r["M11_form"]
        agr = r["HM_I8_AG"]["verdict"] if who != "A2" else r["HM_CAL_AG"]["verdict"]
        got = (f["entering"], f["form"], agr, f["HM_LG_read_one_session"])
        good = got == (who, form, agv, one)
        if who is None:
            good = good and r["HM_CAL_AG"]["verdict"] == "NOT SCORED"
        T["a5_cases"][name] = {"want": [who, form, agv, one], "got": list(got), "X2": r["HM_I8_AG"].get("X2") if who != "A2" else r["HM_CAL_AG"].get("X2"),
                               "carries": r["M11_carries"], "pass": good}
        if not good:
            probs.append(f"A5 case '{name}': want {(who, form, agv, one)}, got {got}")
    rr = random.Random("M11-v2-selftest|the two forms of X2_AG")
    worst = 0.0
    for _ in range(200):
        prs = {s: ((rr.uniform(3.0, 15.0), rr.gauss(0, 0.2)), (rr.uniform(0.3, 2.9), rr.gauss(0, 0.2))) for s in (0, 1)}
        worst = max(worst, abs(A5.lines_agree(prs, V1.SIGMA["aifoundry3"])["X2"] - A5.lines_agree_cov_form(prs, V1.SIGMA["aifoundry3"])))
    T["a5_two_forms_worst_abs"] = worst
    if worst > 1e-9:
        probs.append(f"the two forms of X2_AG differ by {worst}")
    # (5) A5's committed cell through v2's rules: section 0.1's case on the likeliest pattern, v2's committed draws
    a5j = json.load(open(os.path.join(HERE, "design-power-heat-a5.json")))
    des = a5j["plan_P_C"][A4.A3X2]
    tr = dict(VD2.truths_as_committed())
    mx = A4.MIXED
    extra = A4.he_chain_extra(des, tr[mx])
    rng = random.Random(f"M11-HM-LG|{A4.A3X2}|{0.0884:.4f}|{mx}")
    cnt = {f: 0 for f in A5.FORMS}
    first = {}
    N = A5.DRAWS
    for i in range(N):
        groups = D.sim_sessions(des, tr[mx], V1.SIGMA["aifoundry3"], rng)
        groups = {j: [(p, e + x) for (p, e), x in zip(pts, extra[j])] for j, pts in groups.items()}
        r = decide_card_kind({f"S{j}": syn([p for p, _ in pts], [e for _, e in pts]) for j, pts in groups.items()}, "aifoundry3")
        f = r["M11_form"]
        if f["entering"]:
            key = f"{f['entering']} enters, " + ("per session" if f["form"] == FORM_PER else "common or not separated")
            cnt[key] += 1
            first.setdefault(key, i)
    mine = {k: round(100.0 * v / N, 1) for k, v in cnt.items()}
    com = a5j["plan"]["0.0884"][A4.HE_CHAIN][mx]["entries_by_form"]
    T["a5_committed_cell"] = {"this_scorer": mine, "committed": com, "equal": mine == com, "first_draw_of_each_form": first}
    if mine != com:
        probs.append(f"A5's committed cell: {mine} != {com}")
    if len(first) != 4:
        probs.append(f"not every form was exercised in the cell: {sorted(first)}")
    # (6) the staged reading on E154's committed pass renamed to M11's holds: v2's reading equals v1's, and the lines come first
    if os.path.exists(workdir) and os.listdir(workdir):
        probs.append(f"--workdir {workdir} is not empty")
    else:
        pdir = os.path.join(workdir, "m11-from-e154")
        _renamed_e154(pdir)
        lp = os.path.join(workdir, "lines.jsonl")
        r2 = score([pdir], lp)
        r1 = V1.score([pdir])
        s1, s2 = list(r1["sessions"].values())[0], list(r2["sessions"].values())[0]
        holds_eq = all(all(s1["holds"][n].get(k) == s2["holds"][n].get(k) for k in ("scored", "R_C", "e_C", "P_C", "why", "status"))
                       for n in NAMES_A3)
        a1, a2_ = r1["aifoundry3"], r2["aifoundry3"]
        dec_eq = all(a1[k] == a2_[k] for k in ("HM_LG", "A1_4", "HM_E144", "HM_HE", "M11_carries")) and \
            a1["HM_CAL"]["verdict"] == a2_["HM_CAL"]["verdict"] and a1["HM_CAL_I8"]["verdict"] == a2_["HM_CAL_I8"]["verdict"]
        log = r2["reading_order"]
        i1, i2 = log.index("stage 1 written: A2's lines"), log.index("stage 2 written: A4's lines")
        later_first = min(i for i, x in enumerate(log) if x.split(" of ")[0] in ("read L1", "read S", "read L2"))
        l2_first = min(i for i, x in enumerate(log) if x.startswith("read L2"))
        order_ok = i1 < later_first and i2 < l2_first
        st = [json.loads(x) for x in open(lp)]
        lines_ok = [x["stage"] for x in st] == [1, 2, 3]
        sid = list(r2["sessions"])[0]
        l4 = st[1]["sessions"][sid].get("line")
        pi8 = a2_["HM_CAL_I8"]["per_session"].get(sid, {})
        if l4 and "a" in pi8:
            lines_ok = lines_ok and abs(l4["a_C"] - pi8["a"]) < 1e-3 and abs(l4["g"] - pi8["g"]) < 1e-3
        l2_ = st[0]["sessions"][sid].get("line")
        pc = a2_["HM_CAL"]["per_session"].get(sid, {})
        if l2_ and "a_C" in pc:
            lines_ok = lines_ok and abs(l2_["a_C"] - pc["a_C"]) < 1e-3 and abs(l2_["g"] - pc["g"]) < 1e-3
        T["staged_reading"] = {"pass_dir": "E154's committed pass p15420, its holds renamed H_M->H_E, K_S->Z, K_Q->L1, K_L->S, K_O->L2",
                               "holds_equal_v1": holds_eq, "decisions_equal_v1": dec_eq, "reading_order": log,
                               "lines_before_later_holds": order_ok, "lines_file_stages_and_values": lines_ok,
                               "holds": {n: {k: s2["holds"][n].get(k) for k in ("scored", "R_C", "e_C", "P_C")} for n in NAMES_A3},
                               "label": r2["label"], "blind": r2["blind"]}
        if not (holds_eq and dec_eq and order_ok and lines_ok):
            probs.append(f"staged reading: holds equal {holds_eq}, decisions equal {dec_eq}, lines first {order_ok}, lines file {lines_ok}")
        if r2["blind"] is not False:
            probs.append("staged reading: a session launched on 3 Nov must read post hoc")
        # the takeover's additions (about 14:40 PST): under REN both stage lines are null, so the value checks above never ran there.
        # (6a) a null stage line goes with a NOT SCORED decision, and the order read from the records alone equals the final order
        null_ok = ((l2_ is not None) or ("not_scored" in pc)) and ((l4 is not None) or ("not_scored" in pi8))
        ord_ok = st[0]["order_from_records"][sid] == r2["sessions"][sid]["order"]
        T["staged_reading"].update(lines_null_where_not_scored=null_ok, order_from_records_equals_final=ord_ok,
                                   stage_lines={"A2": l2_, "A4": l4, "why": [st[0]["sessions"][sid].get("why"), st[1]["sessions"][sid].get("why")]})
        if not (null_ok and ord_ok):
            probs.append(f"staged reading: a null line with a read decision ({not null_ok}), or the records' order differs ({not ord_ok})")
        # (6b) E154's pass under REN2: A4's stage-2 line is read on a committed pass, so its value is compared (r4 is the output's rounding)
        pdb = os.path.join(workdir, "m11-from-e154-i8")
        _renamed_e154(pdb, REN2)
        lpb = os.path.join(workdir, "lines-i8.jsonl")
        r2b = score([pdb], lpb)
        r1b = V1.score([pdb])
        s1b, s2b = list(r1b["sessions"].values())[0], list(r2b["sessions"].values())[0]
        holds_eq_b = all(all(s1b["holds"][n].get(k) == s2b["holds"][n].get(k) for k in ("scored", "R_C", "e_C", "P_C", "why", "status"))
                         for n in NAMES_A3)
        a1b, a2b = r1b["aifoundry3"], r2b["aifoundry3"]
        dec_eq_b = all(a1b[k] == a2b[k] for k in ("HM_LG", "A1_4", "HM_E144", "HM_HE", "M11_carries")) and \
            a1b["HM_CAL"]["verdict"] == a2b["HM_CAL"]["verdict"] and a1b["HM_CAL_I8"]["verdict"] == a2b["HM_CAL_I8"]["verdict"] and \
            a1b["HM_CAL_I8"]["per_session"] == a2b["HM_CAL_I8"]["per_session"]
        logb = r2b["reading_order"]
        order_ok_b = logb.index("stage 1 written: A2's lines") < min(i for i, x in enumerate(logb) if x.split(" of ")[0] in ("read L1", "read S", "read L2")) \
            and logb.index("stage 2 written: A4's lines") < min(i for i, x in enumerate(logb) if x.startswith("read L2"))
        stb = [json.loads(x) for x in open(lpb)]
        sidb = list(r2b["sessions"])[0]
        l4b, l2b = stb[1]["sessions"][sidb].get("line"), stb[0]["sessions"][sidb].get("line")
        pi8b, pcb = a2b["HM_CAL_I8"]["per_session"].get(sidb, {}), a2b["HM_CAL"]["per_session"].get(sidb, {})
        i8_read_b = "not_scored" not in pi8b and "a" in pi8b
        i8_equal_b = bool(l4b) and i8_read_b and r4(l4b["a_C"]) == pi8b["a"] and r4(l4b["g"]) == pi8b["g"]
        a2_null_b = l2b is None and "not_scored" in pcb
        ord_ok_b = stb[0]["order_from_records"][sidb] == r2b["sessions"][sidb]["order"]
        T["staged_reading_i8"] = {"pass_dir": "E154's committed pass p15420, its holds renamed H_M->H_E, K_S->L1, K_Q->S, K_L->Z, K_O->L2",
                                  "holds_equal_v1": holds_eq_b, "decisions_equal_v1": dec_eq_b, "lines_before_later_holds": order_ok_b,
                                  "A4_line_read_by_the_decision": i8_read_b, "A4_stage2_line_equals_the_decisions": i8_equal_b,
                                  "A2_line_null_and_not_scored": a2_null_b, "order_from_records_equals_final": ord_ok_b,
                                  "stage2_line": l4b, "decision_line": {k: pi8b.get(k) for k in ("a", "g", "w", "span")},
                                  "A2_why": [stb[0]["sessions"][sidb].get("why"), pcb.get("not_scored")], "reading_order": logb,
                                  "label": r2b["label"]}
        if not (holds_eq_b and dec_eq_b and order_ok_b and i8_equal_b and a2_null_b and ord_ok_b):
            probs.append(f"staged reading under REN2: holds equal {holds_eq_b}, decisions equal {dec_eq_b}, lines first {order_ok_b}, "
                         f"A4 line read and equal {i8_equal_b}, A2 null and NOT SCORED {a2_null_b}, order {ord_ok_b}")
    # (6c) the stage lines against the decision's lines on synthetic sessions (the takeover's)
    cu, bu = _staged_lines_unit()
    T["staged_lines_unit"] = {"counts": cu, "problems": bu[:10], "n_problems": len(bu)}
    if bu or cu["A2 read, line equal"] < 100 or cu["A4 read, line equal"] < 100:
        probs.append(f"the stage lines against the decision's: {len(bu)} problem(s) {bu[:3]}; counts {cu}")
    # (7) the precedence with A5's commit
    rc, t5 = V1.git("log", "-1", "--format=%ct", A5_COMMIT)
    pn = precedence(int(time.time() * 1000))
    pb = precedence((int(t5) - 1) * 1000) if rc == 0 and t5 else {"blind": None}
    T["precedence_synthetic"] = {"now": pn["blind"], "one_second_before_A5": pb["blind"],
                                 "ancestors": {k: v["ancestor_of_HEAD"] for k, v in pn.items() if isinstance(v, dict)}}
    if pn["blind"] is not True or pb["blind"] is not False:
        probs.append(f"precedence: now {pn['blind']}, one second before A5 {pb['blind']} (want True, False)")
    T["problems"] = probs
    T["pass"] = not probs
    return T


def main():
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else None
    mp = args[args.index("--md") + 1] if "--md" in args else None
    if "--self-test" in args:
        if "--workdir" not in args:
            raise SystemExit("M11 scorer v2: --self-test needs --workdir <a new scratch dir> (it writes a renamed copy of E154's pass there)")
        wd = args[args.index("--workdir") + 1]
        T = self_test(wd)
        print("M11 scorer v2 self-test: lists " + ", ".join(f"{k} {v}" for k, v in T["lists_checked"].items()))
        v = T["v1_self_test"]
        print(f"  score_m11.py's own self-test, unchanged: {'PASS' if v['pass'] else 'FAIL'} (M10's holds: {v['m10_holds']}; "
              f"{sum(v['synthetic'].values())} of {len(v['synthetic'])} synthetic; committed cells {v['committed_cells']})")
        for k, x in T["read_rule_cases"].items():
            print(f"  A4-8 read rule: {k:52s} {'PASS' if x['pass'] else 'FAIL'}  {x['got']}")
        for k, x in T["reasons"].items():
            print(f"  A5-4 reason: {k:62s} {'PASS' if x['pass'] else 'FAIL'}  v2 '{x['got']}' (score_m11.py printed '{x['score_m11_printed']}')")
        for k, x in T["both_paths"].items():
            print(f"  A1-4 BOTH path: {k:34s} {'PASS' if x['pass'] else 'FAIL'}  {x['got']}")
        for k, x in T["a5_cases"].items():
            print(f"  A5: {k:80s} {'PASS' if x['pass'] else 'FAIL'}  {x['got']} X2 {x['X2']}")
        print(f"  A5: the two forms of X2_AG on 200 random pairs agree to {T['a5_two_forms_worst_abs']:.1e}")
        c = T["a5_committed_cell"]
        print(f"  A5's committed cell (section 0.1's case, likeliest): {c['this_scorer']} against {c['committed']}: "
              f"{'equal' if c['equal'] else 'DIFFERS'}; first draw of each form {c['first_draw_of_each_form']}")
        s = T.get("staged_reading")
        if s:
            print(f"  staged reading (E154's pass renamed): holds equal v1's {s['holds_equal_v1']}; decisions equal {s['decisions_equal_v1']}; "
                  f"lines written before the later holds {s['lines_before_later_holds']}; lines file {s['lines_file_stages_and_values']}; {s['label']}")
            print("    order: " + " | ".join(s["reading_order"]))
            print(f"    both stage lines null there ({s['stage_lines']['why']}); a null line goes with a NOT SCORED decision "
                  f"{s['lines_null_where_not_scored']}; the order read from the records equals the final order {s['order_from_records_equals_final']}")
        s = T.get("staged_reading_i8")
        if s:
            print(f"  staged reading (E154's pass under REN2): holds equal v1's {s['holds_equal_v1']}; decisions equal {s['decisions_equal_v1']}; "
                  f"lines first {s['lines_before_later_holds']}; A4's stage-2 line {s['stage2_line']} read by the decision "
                  f"{s['A4_line_read_by_the_decision']} and equal to its {s['decision_line']} {s['A4_stage2_line_equals_the_decisions']}; "
                  f"A2 null and NOT SCORED {s['A2_line_null_and_not_scored']} ({s['A2_why'][0]}); order {s['order_from_records_equals_final']}")
        u = T["staged_lines_unit"]
        print(f"  the stage lines against the decision's on {u['counts']['draws']} synthetic sessions: {u['counts']}; problems {u['n_problems']}")
        p = T["precedence_synthetic"]
        print(f"  precedence (git, with A5): a first launch now reads blind {p['now']}; one second before A5's commit {p['one_second_before_A5']}; "
              f"every commit an ancestor of HEAD: {all(p['ancestors'].values())}")
        print("SELF-TEST " + ("PASS" if T["pass"] else "FAIL: " + "; ".join(T["problems"])))
        if jp:
            json.dump(T, open(jp, "w"), indent=1, sort_keys=True, default=str)
        sys.exit(0 if T["pass"] else 1)
    if not args or args[0] != "score":
        raise SystemExit(__doc__)
    if any(x == "--a2" for x in args):
        raise SystemExit("M11 scorer v2: no aifoundry2 reader here (E177's kit is its own lane); refused")
    a3 = [args[i + 1] for i, x in enumerate(args) if x == "--a3"]
    if not a3:
        raise SystemExit("M11 scorer v2: name at least one aifoundry3 pass with --a3")
    if "--lines" not in args:
        raise SystemExit("M11 scorer v2: name the lines file with --lines (A4-8: the lines are written before the later holds are read)")
    res = score(a3, args[args.index("--lines") + 1])
    if jp:
        json.dump(res, open(jp, "w"), indent=1, sort_keys=True, default=str)
    if mp:
        open(mp, "w").write(md_summary(res))
    print(md_summary(res))


if __name__ == "__main__":
    main()
