#!/usr/bin/env python3
"""E181's kit fix (fix-e181, Fri 6 Nov 2026): M11's scorer v4 for heat over minutes (tools/claims-v3/m11/REGISTRATION.md section 13 step 1,
as amended by A1-A9), desk only (the Intel). score_m11.py (03582d2f), score_m11_v2.py (ebdbb35c) and score_m11_v3.py (33cdccf6) stay as
committed: v4 imports v3 unchanged (v3 imports v2, v2 imports v1), and every registered reading and decision v3 makes is v4's, unchanged.
What v4 adds, from the E181 kit verifier's faults (verify-e181, Fri 6 Nov 2026) and M11's amendment A9:

  W   nothing written before the gates (the verifier's fault 4: v3 called v2's staged reader, which writes the lines file, before its own
      check of the start_gate marks, so a refused score left scored-m11-lines.jsonl behind). v4 reads every pass's start_gate mark with
      v3's gate_reading BEFORE anything is read or written, and refuses (exit 1, no file written) when a mark disagrees with its own numbers.
      The lines file is then written under a staging name beside it (<lines>.staging: v2's three stages, each appended and fsync'd before
      the next stage reads anything, as A4-8 asks; then the arm's three) and renamed to its own name only after the whole score has
      succeeded. Any refusal or error after the staging began removes the staging file, so a refused score leaves no scored file.
  A9  the reported arm of M11's amendment A9 (a9_posthoc.two_pass, imported unchanged): each session that passed its start gate and names
      its smoke pass (--smoke after its --a3) is read again with the registered chain run over the smoke pass and the measured pass
      together. Per hold e_2p and its shift from the registered e (R is the registered R exactly, or the arm refuses itself); then the
      registered decision code, unchanged (score_m11_v2.decide_card_kind), on the arm's points, so HM-E144, HM-HE and HM-CAL (and the rest)
      are printed under the arm's own heading. The arm's lines are staged too (its A2 line, then its A4 line, then L2). REPORTED: never a
      verdict, an entry or what M11 carries (A9-3); a failure of the arm makes the arm NOT SCORED and changes nothing else.
  H   A6-5's host readings (the verifier's fault 3): the host windows E181's step 12 writes on the box (build/e181/host-start.out and
      host-end.out, collected into the data directory's logs/) read and reported: the NVMe composite (nvme temp1) and the mean of coretemp
      temp2-temp9 at the session's start and end, and their change. Reported, never a gate; a missing window reads "not read".
  E   A6-3's pattern beside A6-2's room line (the verifier's fault 8): run_e181.py reads the room line with a 1e-9 C tolerance and H_E's
      pattern without it, so a room in (53.9, 53.9 + 1e-9] C passes the gate with no H_E pattern (H_E then runs as a rest). v4 flags a
      session whose start gate passed while its room mark carries no pattern (A6_3_pattern_edge), so a record names it. No reading changes.
  P   the blind precedence counts A9 beside the registration and A1-A8.

It checks SHA256SUMS-a9 and SHA256SUMS-score-m11-v3 (repo paths) before it imports anything; v3, v2 and v1 check theirs on import.

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v4.py score --a3 <pass dir> [--smoke <smoke pass dir>] [--host <logs dir>]
        [--a3 <pass dir> [--smoke ...] [--host ...]] --lines <out.jsonl> [--json <out>] [--md <out>]
    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v4.py --self-test --workdir <a new scratch dir> [--json <out>]
--smoke and --host belong to the --a3 just before them. Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site,
so never -I). SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
V4_LISTS = ("SHA256SUMS-a9", "SHA256SUMS-score-m11-v3")
A9_COMMIT = "cd5bed77"
HOST_KEYS = ("nvme:temp1_input",) + tuple(f"coretemp:temp{i}_input" for i in range(2, 10))
ARM_LABEL = "reported (A9): the chain over the smoke and the measured pass; never a verdict, an entry or what M11 carries"


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _check_v4_lists():
    counts, bad = {}, []
    for name in V4_LISTS:
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


_V4_COUNTS, _V4_BAD = _check_v4_lists()
if _V4_BAD:
    raise SystemExit("M11 scorer v4 REFUSED: a registered file differs:\n  " + "\n  ".join(_V4_BAD))

sys.path.insert(0, HERE)
import score_m11_v3 as V3  # noqa: E402  (33cdccf6, unchanged: it checks A6-A8's lists and the footing law's, and imports v2 unchanged)
import a9_posthoc as A9P  # noqa: E402  (A9's arm, unchanged: two_pass() builds the session over both passes from the registered modules)

V2, V1 = V3.V2, V3.V1
np = V2.np
r4 = V2.r4
REG_COMMITS = dict(V3.REG_COMMITS, A9=A9_COMMIT)


# ------------------------------------------------------------------------------------------------ P: the precedence, with A9
def precedence(first_launch_ms):
    out = {}
    for k, c in REG_COMMITS.items():
        rc, t = V1.git("log", "-1", "--format=%ct", c)
        rca, _ = V1.git("merge-base", "--is-ancestor", c, "HEAD")
        ok = rc == 0 and rca == 0 and first_launch_ms is not None and int(t) * 1000 < first_launch_ms
        out[k] = {"commit": c, "commit_epoch_s": int(t) if rc == 0 and t else None, "ancestor_of_HEAD": rca == 0, "precedes_first_launch": ok}
    out["blind"] = all(v["precedes_first_launch"] for v in out.values() if isinstance(v, dict))
    return out


# ------------------------------------------------------------------------------------------------ W: the gates before any write
def pregate(a3_dirs):
    """every pass's start_gate mark, read by v3's gate_reading before anything is read or written; returns the problems"""
    probs = []
    for i, d in enumerate(a3_dirs):
        marks, _, _ = V1.S166.records(d)
        gate = [m for m in marks if m.get("kind") == "start_gate"]
        g = V3.gate_reading(gate[-1] if gate else None)
        if not g["agrees"] and g["form"] != "none":
            probs.append(f"S{i + 1}:{os.path.basename(os.path.normpath(d))}: the start_gate mark's passed={g['passed']} disagrees with "
                         f"its own numbers ({g})")
    return probs


def _append(path, rec):
    """v2's LinesFile.write: one JSON line, appended and fsync'd (the staging file is not truncated: it already holds v2's stages)"""
    with open(path, "a") as f:
        f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _remove(p):
    try:
        os.remove(p)
        return True
    except FileNotFoundError:
        return False


# ------------------------------------------------------------------------------------------------ E: A6-3's pattern beside the gate
def pattern_edge(pass_dir):
    marks, _, _ = V1.S166.records(pass_dir)
    room = [m for m in marks if m.get("kind") == "room"]
    gate = [m for m in marks if m.get("kind") == "start_gate"]
    edge = bool(room and gate and gate[-1].get("passed") is True and "he_seconds" in room[-1] and room[-1]["he_seconds"] is None)
    return {"flag": edge, "room_c": room[-1].get("mean34_c") if room else None,
            "note": ("the start gate passed while the room mark carries no H_E pattern (A6-3 read without the gate's 1e-9 C tolerance): "
                     "H_E ran as a rest; name it in the records" if edge else "the gate and A6-3's pattern agree")}


# ------------------------------------------------------------------------------------------------ H: A6-5's host windows
def host_window(path):
    if not path or not os.path.exists(path):
        return {"read": False, "why": "no host window file (E181's step 12 was not run, or its file was not collected)"}
    lines = [x.rstrip("\n") for x in open(path, errors="replace")]
    vals = {}
    for x in lines:
        p = x.split()
        if len(p) >= 9 and p[1] == "mean" and p[3] == "min" and p[5] == "max" and p[7] == "n":
            try:
                vals[p[0]] = {"mean": float(p[2]), "min": float(p[4]), "max": float(p[6]), "n": int(p[8])}
            except ValueError:
                continue
    core = [vals[k]["mean"] for k in HOST_KEYS[1:] if k in vals]
    return {"read": bool(vals), "first_line": lines[0] if lines else None, "sensors": vals,
            "nvme_temp1_mean_C": vals.get("nvme:temp1_input", {}).get("mean"),
            "coretemp_2_9_mean_C": (sum(core) / len(core)) if core else None, "coretemp_2_9_n": len(core)}


def host_readings(logs_dir):
    if not logs_dir:
        return {"read": False, "why": "no --host named for this session", "note": "A6-5: reported, never a gate"}
    st = host_window(os.path.join(logs_dir, "host-start.out"))
    en = host_window(os.path.join(logs_dir, "host-end.out"))
    out = {"start": st, "end": en, "note": "A6-5: the host's NVMe composite and coretemp at the session's start and end; reported, never a gate"}
    if st.get("read") and en.get("read"):
        d = {}
        for k in ("nvme_temp1_mean_C", "coretemp_2_9_mean_C"):
            if st.get(k) is not None and en.get(k) is not None:
                d[k] = en[k] - st[k]
        out["end_less_start"] = d
    return out


# ------------------------------------------------------------------------------------------------ A9: the reported arm
def arm_contexts(sessions_in, out):
    """A9-1's session for every session that passed its start gate and names its smoke: {sid: context} and {sid: why not}"""
    ctx, why = {}, {}
    for i, s in enumerate(sessions_in):
        sid = f"S{i + 1}:{os.path.basename(os.path.normpath(s['a3']))}"
        reg = out["sessions"][sid]
        if "excluded" in reg:
            why[sid] = "the session did not pass its start gate"
            continue
        if not s.get("smoke"):
            why[sid] = "no smoke pass named (--smoke)"
            continue
        try:
            s2, info = A9P.two_pass(s["a3"], s["smoke"])
        except (OSError, ValueError, KeyError, IndexError, TypeError, EOFError) as e:
            why[sid] = f"the arm's session could not be built ({type(e).__name__}: {e})"
            continue
        if s2 is None:
            why[sid] = info.get("why")
            continue
        marks, recs, src = V1.S166.records(s["a3"])
        tel_t = V1.S166.tel_times(s["a3"])
        pred2 = V1.FT.predict_session(s2, V1.PQ.TAU, V1.PQ.R3)
        ctx[sid] = {"pass_dir": s["a3"], "marks": marks, "recs": recs, "src": src, "sess": s2, "tel_t": tel_t, "pred_a": pred2, "info": info}
    return ctx, why


def arm_read(ctx, staging):
    """v2's staged reading on the arm's sessions: H_E and Z, the arm's A2 lines written; L1 and S, its A4 lines written; then L2"""
    log, rows = [], {sid: {} for sid in ctx}
    order = {sid: V2._order_from_records(c) for sid, c in ctx.items()}
    st = {}
    for sid, c in ctx.items():
        for nm in ("H_E", "Z"):
            rows[sid][nm] = V2._read(c, nm, sid, log)
        st[sid] = V2._a2_line(rows[sid], order[sid])
    _append(staging, {"stage": 4, "what": "A9's arm: A2's line per session through its pair H_E and Z on the chain over both passes, written "
                                          "before any later hold's arm e is read", "t": V2._now(), "sessions": st})
    log.append("stage 4 written: the arm's A2 lines")
    st = {}
    for sid, c in ctx.items():
        for nm in ("L1", "S"):
            rows[sid][nm] = V2._read(c, nm, sid, log)
        st[sid] = V2._a4_line(rows[sid], order[sid])
    _append(staging, {"stage": 5, "what": "A9's arm: A4's line per session through L1 and S, written before any L2's arm e is read",
                      "t": V2._now(), "sessions": st})
    log.append("stage 5 written: the arm's A4 lines")
    for sid, c in ctx.items():
        rows[sid]["L2"] = V2._read(c, "L2", sid, log)
    _append(staging, {"stage": 6, "what": "A9's arm: L2 read; every arm reading follows in the scorer's JSON", "t": V2._now(),
                      "L2": {sid: {"scored": r["L2"].get("scored"), "P_C": r["L2"].get("P_C"), "e_C": r["L2"].get("e_C")} for sid, r in rows.items()}})
    log.append("stage 6 written: the arm's L2 read")
    return rows, log


def arm(sessions_in, out, staging):
    ctx, why = arm_contexts(sessions_in, out)
    res = {"label": ARM_LABEL, "rule": "M11's amendment A9 (A9-1 to A9-4); the arm is a9_posthoc.two_pass, imported unchanged",
           "not_read": why, "sessions": {}}
    if not ctx:
        res["reads"] = "NOT SCORED: no session with its smoke pass named passed its start gate"
        return res
    rows, log = arm_read(ctx, staging)
    res["reading_order"] = log
    arm_sessions = {}
    for sid, c in ctx.items():
        reg = out["sessions"][sid]["holds"]
        per, bad = {}, []
        for nm in V1.NAMES_A3:
            a, r = rows[sid].get(nm, {}), reg.get(nm, {})
            if a.get("R_C") != r.get("R_C"):
                bad.append(f"{nm}: R {a.get('R_C')} against the registered {r.get('R_C')}")
            de = (a["e_C"] - r["e_C"]) if (a.get("e_C") is not None and r.get("e_C") is not None) else None
            per[nm] = {"scored": a.get("scored"), "R_C": a.get("R_C"), "e_2p_C": a.get("e_C"), "P_2p_C": a.get("P_C"),
                       "e_registered_C": r.get("e_C"), "delta_e_C": None if de is None else round(de, 3)}
        sres = {"info": {k: (r4(v) if isinstance(v, float) else v) for k, v in c["info"].items()}, "holds": per}
        if bad:
            sres["reads"] = "NOT SCORED: the arm's R differs from the registered R (" + "; ".join(bad) + ")"
        else:
            sres["reads"] = "SCORED"
            arm_sessions[sid] = V2._session_dict(c, {nm: rows[sid][nm] for nm in V1.NAMES_A3})
        res["sessions"][sid] = sres
    if not arm_sessions:
        res["reads"] = "NOT SCORED: no session's arm read its holds"
        return res
    try:
        dec = V2.decide_card_kind(arm_sessions, "aifoundry3")
    except SystemExit as e:
        res["reads"] = f"NOT SCORED: the registered decision code refused on the arm's points ({str(e)[:300]})"
        return res
    res["reads"] = "SCORED (reported)"
    res["HM_E144"] = dec.get("HM_E144")
    res["HM_HE"] = dec.get("HM_HE")
    res["HM_CAL"] = {k: dec["HM_CAL"].get(k) for k in ("verdict", "n_L", "tau_C", "D_C", "RMS_u_C", "RMS_c_C", "per_session")} if dec.get("HM_CAL") else None
    res["all_readings_on_the_arm"] = dec
    res["note"] = "every reading here is reported beside the registered one; the registered reading decides (A9-3)"
    return res


# ------------------------------------------------------------------------------------------------ the score
def score(sessions_in, lines_path, _fail_after_stages=False):
    """sessions_in: [{"a3": dir, "smoke": dir or None, "host": dir or None}]"""
    a3_dirs = [s["a3"] for s in sessions_in]
    probs = pregate(a3_dirs)
    if probs:
        raise SystemExit("M11 scorer v4 REFUSED before any file was written: " + "; ".join(probs))
    staging = lines_path + ".staging"
    _remove(staging)
    try:
        out = V3.score(a3_dirs, staging)
        if _fail_after_stages:
            raise SystemExit("M11 scorer v4 REFUSED: the self-test's refusal after the staged stages")
        out["scorer"] = "tools/claims-v3/m11/score_m11_v4.py"
        out["imports_unchanged"] = ["tools/claims-v3/m11/score_m11_v3.py", "tools/claims-v3/m11/score_m11_v2.py", "tools/claims-v3/m11/score_m11.py",
                                    "tools/claims-v3/m11/a9_posthoc.py"]
        out["lists_checked"] = dict(out.get("lists_checked", {}), **_V4_COUNTS)
        out["registration_commits"] = REG_COMMITS
        for i, s in enumerate(sessions_in):
            sid = f"S{i + 1}:{os.path.basename(os.path.normpath(s['a3']))}"
            so = out["sessions"][sid]
            so["precedence"] = precedence(so["first_launch_ms"])
            so["A6_3_pattern_edge"] = pattern_edge(s["a3"])
            so["A6_5_host"] = host_readings(s.get("host"))
            so["smoke_pass_named"] = os.path.basename(os.path.normpath(s["smoke"])) if s.get("smoke") else None
        out["arm_A9"] = arm(sessions_in, out, staging)
        use = {sid: s for sid, s in out["sessions"].items() if "excluded" not in s}
        out["blind"] = all(s["precedence"]["blind"] for s in use.values()) if use else None
        out["label"] = ("blind: every registration and amendment commit (A1-A9) precedes every session's first launch record" if out["blind"]
                        else "post hoc: a registration or amendment commit does not precede a session's first launch record")
    except BaseException:
        _remove(staging)
        raise
    os.replace(staging, lines_path)
    out["lines_file"] = os.path.basename(lines_path)
    out["lines_staged_as"] = os.path.basename(staging) + ", renamed to the lines file only after the whole score succeeded (v4 W)"
    return out


def md_summary(res):
    L = [V3.md_summary(res).rstrip("\n").replace("score_m11_v3.py", "score_m11_v4.py")]
    for sid, s in res.get("sessions", {}).items():
        e = s.get("A6_3_pattern_edge", {})
        if e.get("flag"):
            L.append(f"- {sid} A6-3 PATTERN EDGE: {e['note']} (room {r4(e.get('room_c'))} C)")
        h = s.get("A6_5_host", {})
        if h.get("start") or h.get("end"):
            st, en = h.get("start", {}), h.get("end", {})
            L.append(f"- {sid} A6-5 host, reported: NVMe composite {r4(st.get('nvme_temp1_mean_C'))} -> {r4(en.get('nvme_temp1_mean_C'))} C, "
                     f"coretemp 2-9 {r4(st.get('coretemp_2_9_mean_C'))} -> {r4(en.get('coretemp_2_9_mean_C'))} C"
                     + ("" if st.get("read") and en.get("read") else f" ({st.get('why') or en.get('why')})"))
    a = res.get("arm_A9", {})
    L.append(f"- A9's arm (the chain over the smoke and the measured pass), {a.get('reads')}; " + ARM_LABEL)
    for sid, s in a.get("sessions", {}).items():
        L.append(f"  - {sid}: " + ", ".join(f"{nm} delta e {v.get('delta_e_C')}" for nm, v in s.get("holds", {}).items())
                 + f"; gap {s.get('info', {}).get('gap_s')} s ({s.get('reads')})")
    if a.get("HM_E144"):
        L.append(f"  - on the arm: HM-E144 {a['HM_E144'].get('reading')}; HM-HE N2 {a.get('HM_HE', {}).get('N2_departs_in_every_session')}; "
                 f"HM-CAL {(a.get('HM_CAL') or {}).get('verdict')} (RMS_c {(a.get('HM_CAL') or {}).get('RMS_c_C')}, RMS_u {(a.get('HM_CAL') or {}).get('RMS_u_C')})")
    for sid, w in a.get("not_read", {}).items():
        L.append(f"  - {sid}: the arm not read ({w})")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ self-test
def _registered_view(res):
    """the registered readings of a v3 or v4 result: what A9-3 says the arm never changes"""
    ss = {}
    for sid, s in res["sessions"].items():
        ss[sid] = {k: s.get(k) for k in ("holds", "order", "start_gate", "start_gate_reading", "FL5c", "excluded", "room_drift_over_R0_C_per_10min",
                                         "first_launch_ms", "records_from")}
    return json.loads(json.dumps({"sessions": ss, "aifoundry3": res.get("aifoundry3"), "reading_order": res.get("reading_order")},
                                 sort_keys=True, default=str))


def self_test(workdir):
    if os.path.exists(workdir):
        raise SystemExit(f"--workdir {workdir} exists: name a new one")
    os.makedirs(workdir)
    T = {"lists_checked": dict(_V4_COUNTS), "cases": {}}
    probs = []

    def case(name, ok, got):
        T["cases"][name] = {"pass": bool(ok), "got": got}
        if not ok:
            probs.append(f"{name}: {got}")

    e154 = V1.P166.E154P
    smoke154 = os.path.join(os.path.dirname(os.path.dirname(e154)), "e154-smoke", "p15401")
    room154 = [json.loads(x) for x in open(os.path.join(e154, "marks.jsonl")) if '"room"' in x]
    room154 = [m for m in room154 if m.get("kind") == "room"][0]["mean34_c"]
    f0 = 50.98740804036458                                         # E154's F0 (residue-a8.json > sessions > E154 > F0_C), as v3's self-test

    def mk(nm, **kw):
        d = os.path.join(workdir, nm, "p18120")
        os.makedirs(os.path.dirname(d))
        V2._renamed_e154(d)
        V3._rewrite_gate(d, **kw)
        return d

    def files(nm):
        return sorted(x for x in os.listdir(os.path.join(workdir, nm)) if x.startswith("lines"))

    # W1: a lying start_gate mark refuses BEFORE any file is written (the verifier's fault 4, on v3's own S-LIE pass)
    d = mk("W-LIE", floor=room154 - 0.414 - 0.6, passed_override=True)
    try:
        score([{"a3": d, "smoke": smoke154}], os.path.join(workdir, "W-LIE", "lines.jsonl"))
        lie = "not refused"
    except SystemExit as e:
        lie = str(e)[:120]
    case("W1 a start_gate mark that disagrees with its numbers: REFUSED before any file is written (no lines file, no staging file)",
         lie.startswith("M11 scorer v4 REFUSED before any file was written") and files("W-LIE") == [], {"refusal": lie, "files": files("W-LIE")})
    # W2: a refusal after the staged stages removes the staging file and writes no lines file
    d = mk("W-LATE", floor=f0)
    try:
        score([{"a3": d, "smoke": smoke154}], os.path.join(workdir, "W-LATE", "lines.jsonl"), _fail_after_stages=True)
        late = "not refused"
    except SystemExit as e:
        late = str(e)[:100]
    case("W2 a refusal after v2's stages: the staging file removed, no lines file left", late.startswith("M11 scorer v4 REFUSED")
         and files("W-LATE") == [], {"refusal": late, "files": files("W-LATE")})
    # W3, A1-A4: a passing session with its smoke (E154's committed p15401); v3 on the same pass beside it
    d = mk("S-PASS", floor=f0)
    host = os.path.join(workdir, "S-PASS", "logs")
    os.makedirs(host)
    for nm_, nv, cv in (("host-start.out", 38.85, 33.1), ("host-end.out", 39.85, 34.6)):
        with open(os.path.join(host, nm_), "w") as f:
            f.write("2026-11-06 09:00:00 PST\n" + f"{'nvme:temp1_input':22s} mean {nv:.3f}  min {nv:.2f}  max {nv:.2f}  n 13\n"
                    + "".join(f"{'coretemp:temp%d_input' % i:22s} mean {cv:.3f}  min {cv - 1:.2f}  max {cv + 1:.2f}  n 13\n" for i in range(1, 10)))
    lines4 = os.path.join(workdir, "S-PASS", "lines.jsonl")
    r4_ = score([{"a3": d, "smoke": smoke154, "host": host}], lines4)
    r3_ = V3.score([d], os.path.join(workdir, "S-PASS", "lines-v3.jsonl"))
    st4 = [json.loads(x)["stage"] for x in open(lines4) if x.strip()]
    case("W3 a passing session: the lines file under its own name, stages 1-6 in order, no staging file left",
         st4 == [1, 2, 3, 4, 5, 6] and not os.path.exists(lines4 + ".staging") and r4_["lines_file"] == "lines.jsonl", {"stages": st4})
    same = _registered_view(r4_) == _registered_view(r3_)
    case("A1 every registered reading is v3's, unchanged, with the arm beside it (A9-3)", same,
         {"same": same, "HM_LG": r4_["aifoundry3"]["HM_LG"]["verdict"], "HM_E144": r4_["aifoundry3"]["HM_E144"]["reading"],
          "HM_CAL": r4_["aifoundry3"]["HM_CAL"]["verdict"]})
    a = r4_["arm_A9"]
    sa = list(a["sessions"].values())[0]
    post = json.load(open(os.path.join(HERE, "a9-posthoc.json")))["sessions"]["E154"]["holds"]["H_M"]["delta_e_C"]
    de_he = sa["holds"]["H_E"]["delta_e_C"]
    later = [abs(sa["holds"][n]["delta_e_C"]) for n in ("Z", "L1", "S", "L2")]
    rs_same = all(sa["holds"][n]["R_C"] == r4_["sessions"][list(r4_["sessions"])[0]]["holds"][n]["R_C"] for n in V1.NAMES_A3)
    case("A2 the arm on E154's pass with its smoke: SCORED; R the registered R for all 5 holds; H_E's delta e within 0.005 C of A9's post hoc "
         "H_M (fit_q138t.score_hold); the later holds' within 0.001 C", a["reads"].startswith("SCORED") and sa["reads"] == "SCORED" and rs_same
         and de_he is not None and abs(de_he - post) <= 0.005 and max(later) <= 0.001 and a.get("HM_E144", {}).get("reading") in ("REPEATS", "DOES NOT REPEAT")
         and (a.get("HM_CAL") or {}).get("verdict") is not None and "HM_HE" in a,
         {"reads": a["reads"], "delta_e_H_E": de_he, "posthoc_H_M": post, "later_max": max(later), "R_same": rs_same,
          "arm_HM_E144": a.get("HM_E144", {}).get("reading"), "arm_HM_CAL": (a.get("HM_CAL") or {}).get("verdict"), "gap_s": sa["info"].get("gap_s")})
    h = list(r4_["sessions"].values())[0]["A6_5_host"]
    case("H1 A6-5's host windows read: the NVMe composite and coretemp 2-9 at the start and end, and their change",
         h["start"]["read"] and h["end"]["read"] and abs(h["end_less_start"]["nvme_temp1_mean_C"] - 1.0) < 1e-9
         and abs(h["end_less_start"]["coretemp_2_9_mean_C"] - 1.5) < 1e-9 and h["start"]["coretemp_2_9_n"] == 8,
         {"start": [h["start"]["nvme_temp1_mean_C"], h["start"]["coretemp_2_9_mean_C"]], "change": h.get("end_less_start")})
    # A3: no smoke named, and a smoke a day away (E144's beside E154's measured pass): the arm NOT SCORED, the registered readings unchanged
    d = mk("S-NOSMOKE", floor=f0)
    r_ns = score([{"a3": d}], os.path.join(workdir, "S-NOSMOKE", "lines.jsonl"))
    e144s = os.path.join(TREE, "docs/reports/data/2026-11-02-e144-heat-minutes/aifoundry3/e144-smoke/p14401")
    d = mk("S-FARSMOKE", floor=f0)
    r_fs = score([{"a3": d, "smoke": e144s}], os.path.join(workdir, "S-FARSMOKE", "lines.jsonl"))
    ns_why = list(r_ns["arm_A9"]["not_read"].values())
    fs_why = list(r_fs["arm_A9"]["not_read"].values())
    case("A3 no smoke named, or a smoke a day before the pass: the arm NOT SCORED with its reason; the registered readings v3's",
         r_ns["arm_A9"]["reads"].startswith("NOT SCORED") and r_fs["arm_A9"]["reads"].startswith("NOT SCORED")
         and ns_why and "no smoke pass named" in ns_why[0] and fs_why and "gap between the passes" in fs_why[0]
         and _registered_view(r_ns)["aifoundry3"] == _registered_view(r3_)["aifoundry3"]
         and _registered_view(r_fs)["aifoundry3"] == _registered_view(r3_)["aifoundry3"],
         {"no_smoke": ns_why, "far_smoke": fs_why})
    # A4: E176's committed pass beside the passing one: excluded with its own G0's reason; the arm read on the passing session only
    e176 = os.path.join(TREE, "docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620")
    e176s = os.path.join(TREE, "docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176-smoke/p17601")
    d2 = os.path.join(workdir, "S-PASS", "p18120")
    r_two = score([{"a3": e176, "smoke": e176s}, {"a3": d2, "smoke": smoke154}], os.path.join(workdir, "lines-two.jsonl"))
    s1, s2_ = list(r_two["sessions"].values())
    case("A4 E176's committed pass beside it: excluded (its own G0); the arm not read there, read on the passing session",
         "excluded" in s1 and "excluded" not in s2_ and list(r_two["arm_A9"]["not_read"].values()) == ["the session did not pass its start gate"]
         and len(r_two["arm_A9"]["sessions"]) == 1, {"E176": s1.get("excluded"), "arm_not_read": r_two["arm_A9"]["not_read"],
                                                      "arm_sessions": list(r_two["arm_A9"]["sessions"])})
    # E1: A6-3's pattern edge flagged (a passed gate, the room mark's pattern null); a pattern, or a refused gate, not flagged
    def room_pattern(nm, secs, period, **kw):
        dd = mk(nm, **kw)
        mp = os.path.join(dd, "marks.jsonl")
        ms = [json.loads(x) for x in open(mp) if x.strip()]
        for m in ms:
            if m.get("kind") == "room":
                m["he_seconds"], m["he_period_s"] = secs, period
        with open(mp, "w") as f:
            for m in ms:
                f.write(json.dumps(m) + "\n")
        return pattern_edge(dd)["flag"]
    fe = room_pattern("S-EDGE", None, None, floor=f0)
    fp = room_pattern("S-PAT", 3.20, 7.56, floor=f0)
    fr = room_pattern("S-EDGE-REFUSED", None, None, floor=f0, room=54.0)
    case("E1 A6-3's pattern edge: a passed gate with no H_E pattern flagged; a pattern, or a refused gate, not flagged",
         fe and not fp and not fr, {"edge": fe, "with_pattern": fp, "refused_gate": fr})
    # P1: the precedence with A9: a launch now reads blind; one second before A9's commit, post hoc
    rc, t9 = V1.git("log", "-1", "--format=%ct", A9_COMMIT)
    pn = precedence(int(time.time() * 1000))
    pb = precedence((int(t9) - 1) * 1000) if rc == 0 and t9 else {"blind": None}
    case("P1 the precedence counts A9: now blind, one second before A9's commit post hoc", pn["blind"] is True and pb["blind"] is False,
         {"now": pn["blind"], "before_A9": pb["blind"], "commits": list(REG_COMMITS)})
    case("L1 v4's lists read before any import: SHA256SUMS-a9 and SHA256SUMS-score-m11-v3", _V4_COUNTS.get("SHA256SUMS-a9", 0) >= 4
         and _V4_COUNTS.get("SHA256SUMS-score-m11-v3", 0) >= 4, _V4_COUNTS)
    T["problems"] = probs
    T["pass"] = not probs
    return T


def _parse(args):
    sessions, cur = [], None
    i = 1
    while i < len(args):
        x = args[i]
        if x == "--a3":
            cur = {"a3": args[i + 1], "smoke": None, "host": None}
            sessions.append(cur)
            i += 2
            continue
        if x in ("--smoke", "--host"):
            if cur is None:
                raise SystemExit(f"M11 scorer v4: {x} belongs to the --a3 before it")
            cur[x[2:]] = args[i + 1]
            i += 2
            continue
        i += 2 if x in ("--lines", "--json", "--md") else 1
    return sessions


def main():
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else None
    mp = args[args.index("--md") + 1] if "--md" in args else None
    if "--self-test" in args:
        if "--workdir" not in args:
            raise SystemExit("M11 scorer v4: --self-test needs --workdir <a new scratch dir>")
        T = self_test(args[args.index("--workdir") + 1])
        print("M11 scorer v4 self-test: lists " + ", ".join(f"{k} {v}" for k, v in T["lists_checked"].items()))
        for k, x in T["cases"].items():
            print(f"  {k:100s} {'PASS' if x['pass'] else 'FAIL'}  {json.dumps(x['got'], default=str)[:300]}")
        print("SELF-TEST " + ("PASS" if T["pass"] else "FAIL: " + "; ".join(T["problems"])))
        if jp:
            json.dump(T, open(jp, "w"), indent=1, sort_keys=True, default=str)
        sys.exit(0 if T["pass"] else 1)
    if not args or args[0] != "score":
        raise SystemExit(__doc__)
    if any(x == "--a2" for x in args):
        raise SystemExit("M11 scorer v4: no aifoundry2 reader here (E177 is not built); refused")
    sessions = _parse(args)
    if not sessions:
        raise SystemExit("M11 scorer v4: name at least one aifoundry3 pass with --a3")
    if "--lines" not in args:
        raise SystemExit("M11 scorer v4: name the lines file with --lines (A4-8: the lines are written before the later holds are read)")
    res = score(sessions, args[args.index("--lines") + 1])
    if jp:
        json.dump(res, open(jp, "w"), indent=1, sort_keys=True, default=str)
    if mp:
        open(mp, "w").write(md_summary(res))
    print(md_summary(res))


if __name__ == "__main__":
    main()
