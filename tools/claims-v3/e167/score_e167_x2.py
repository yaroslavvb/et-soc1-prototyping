#!/usr/bin/env python3
"""E167 (Q141(h), the fix pass): X2, E167's incomplete-window rule in E166's X1 form, and RK3-c's reading when G1Q did not run or is
incomplete, registered in E167.md.dated-note-2.md (Wed 4 Nov 2026, before any E167 data, claim or launch). Desk only (the Intel).

It wraps the registered scorer score_e167.py, imported UNCHANGED (its own checks run on import: predict_q140e's 26 inputs, reduce_e161's 13,
E167.md and e167-registration.json as committed in 7ba987b3), and changes nothing score_e167.py reads or computes. It reads, per hold, whether
the hold's window is complete, and applies X2 to the verdicts. From the amendment on, E167's registered verdicts are this script's `verdicts`;
score_e167.py's own are kept beside them as `verdicts_score_e167`.

  COMPLETE: the hold's step ended "done" (end.json reason exactly "done"); no safety_trip mark; at least the registered protocol's HOLD work
    processes (G1Q 93, G2Q 91: protocol-g1q.json, protocol-g2q.json); a span b - t0 of at least the frozen plan span less 30 s (G1Q
    782.97 - 30 = 752.97 s, G2Q 770.97 - 30 = 740.97 s: predictions-q140e.json E167.plan_span_s); and at least 5 telemetry lines a second
    (half the 10 Hz sampler's) in the anchor window (the REST file's last 120 s, read as reduce_e161.rest_reading reads it: 600 lines) and
    in the plateau window [b - 300 s, b) (1,500 lines). One failed process (rc != 0) is the harness's own tolerance and is reported.
  ENDED BY A SAFETY LINE: the step's end reason starts "safety:" or its marks hold a safety_trip (run_hpl.py's watcher: the die line at
    72 C on the shires' mean or on the hottest-sensor field, or the board line over 80 W on 3 consecutive samples), after the hold's first
    work process started. It counts against: RK3-b FAIL, outside for RK3-c, every carried verdict FAIL. The field that reached the line
    first is read from the step's telemetry and reported.
  EXCLUDED: anything else (the queue's cutoff STOP file, a signal, the protocol's card-minute cap, an error, another user, no end.json,
    thin telemetry): NOT SCORED (incomplete window: <why>); its readings are reported as post hoc.
  NOT RUN: no HOLD work process (the start gate G1, or a stop before the hold): excluded.
  THE RULES WITH X2: RK3-b as registered on a complete G1Q (its regime precondition first, unchanged); FAIL if G1Q ended by a safety line;
    NOT SCORED (incomplete window) if excluded; unchanged when the hold did not run. RK3-c in X1's form: FAIL if any hold rising 10 C or
    more is outside +-1.5%, or ended by a safety line; with nothing excluded, R4 as registered; otherwise PASS only if both expected large
    rises (G1Q and G2Q) are complete and inside, else NOT SCORED (incomplete windows) - a gated G1Q included. An exclusion never turns a
    decided outcome into another. The session figures are over the complete holds, their number stated.

    /usr/bin/python3 tools/claims-v3/e167/score_e167_x2.py <data dir> [--e165-anchors <json>] [--json <out>]
    /usr/bin/python3 tools/claims-v3/e167/score_e167_x2.py --self-test [--json <out>]
numpy 1.26.4, Python 3.9 (the Intel's /usr/bin/python3).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import copy  # noqa: E402
import glob  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FROZEN_X2 = {
    # the registered scorer and the files X2 reads its plan from, as committed in 7ba987b3 / f830b9e2 / 4f4e7620
    "tools/claims-v3/e167/score_e167.py": "9106a5b92c3a6ca7ac63e57dac6fc36a1ebc2f26467e6635d8fb3f5a5fe56a38",
    "tools/claims-v3/e167/protocol-g1q.json": "7cc81b26d42a2c69bd141c3ab6005818af7ba83d29af9a6f8b4a4ab3f59aa6af",
    "tools/claims-v3/e167/protocol-g2q.json": "17a71baa518e99542098f2eea734a73e5f3bf45a50609245fcb09c04b04295a9",
    # the amendment that registers X2 (this fix pass)
    "tools/claims-v3/e167/E167.md.dated-note-2.md": "93caadeb9506827a06e73adef1cb0968dc87ec4b651b0333132adbb6fd4fd739",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


_bad = [f"{rel}: {(sha(os.path.join(TREE, rel)) if os.path.exists(os.path.join(TREE, rel)) else 'missing')[:16]} != {h[:16]}"
        for rel, h in FROZEN_X2.items() if not os.path.exists(os.path.join(TREE, rel)) or sha(os.path.join(TREE, rel)) != h]
if _bad:
    raise SystemExit("E167 X2 scorer REFUSED: a frozen input differs:\n  " + "\n  ".join(_bad))
sys.path.insert(0, HERE)
import score_e167 as S7  # noqa: E402  the registered scorer, unchanged (checks its own frozen inputs on import)

P, R, hm, np = S7.P, S7.R, S7.hm, S7.np
HOLDS = S7.HOLDS
RK3C_FRAC, LARGE_RISE_C = S7.RK3C_FRAC, S7.LARGE_RISE_C
PROTO = {st: json.load(open(os.path.join(HERE, f"protocol-{st.lower()}.json"))) for st in HOLDS}
PLAN_PROCS = {st: int([b for b in PROTO[st]["blocks"] if b["name"] == "HOLD"][0]["launch"]["processes"]) for st in HOLDS}
PLAN_SPAN_S = {st: float(S7.PRED["E167"]["plan_span_s"][st]) for st in HOLDS}
SPAN_SLACK_S = 30.0
MIN_RATE_HZ = 5.0
PLATEAU_S = 300.0
ANCHOR_S = float(hm.ANCHOR_S)
STOP_C = {st: float(PROTO[st]["safety"]["abs_stop_c"]) for st in HOLDS}
CAP_W = {st: float(PROTO[st]["safety"]["board_cap_w"]) for st in HOLDS}
CAP_N = {st: int(PROTO[st]["safety"]["cap_consecutive"]) for st in HOLDS}
EXPECTED_LARGE = tuple(S7.REG["rules"]["RK3_c"].get("expected_large") or ("G1Q", "G2Q"))
CLASS_COMPLETE, CLASS_SAFETY, CLASS_EXCL, CLASS_NOTRUN = "complete", "ended by a safety line", "excluded", "not run"


def r3(x, n=3):
    return S7.r3(x, n)


# ------------------------------------------------------------------------------------------------ reading a step
def read_marks(step_dir):
    p = os.path.join(step_dir, "marks.jsonl")
    out = []
    if os.path.exists(p):
        for ln in open(p):
            if ln.strip():
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel_t(step_dir, prefix):
    fs = sorted(glob.glob(os.path.join(step_dir, "tel", f"{prefix}-*.jsonl*")))
    return hm.load_tel(fs, sensor="fw")["t"] if fs else np.array([])


def first_line_crossing(step_dir, st, t_from):
    """which of run_hpl.py's lines a step's telemetry reached first at or after t_from: the die line on minshire[0] (the shires' mean) or
    on minshire[2] (the hottest-sensor field, the shires' high latch), or the board line on CAP_N consecutive samples"""
    rows = []
    for f in sorted(glob.glob(os.path.join(step_dir, "tel", "*.jsonl*"))):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            for ln in fh:
                if not ln.startswith("{"):
                    continue
                try:
                    d = json.loads(ln)
                    ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
                    rows.append((int(d["t_ms"]) / 1e3, ms[0], ms[2] if len(ms) > 2 else None, d.get("board_w")))
                except (ValueError, KeyError, TypeError):
                    pass
    rows.sort()
    over = 0
    for t, m0, m2, w in rows:
        if t < t_from - 1e-6:
            continue
        hit = []
        if m0 is not None and m0 >= STOP_C[st]:
            hit.append(f"the shires' mean (minshire[0] {m0} C)")
        if m2 is not None and m2 >= STOP_C[st]:
            hit.append(f"the hottest-sensor field (minshire[2] {m2} C, the shires' high latch)")
        if hit:
            return {"t_s": t, "line": "die", "field": " and ".join(hit)}
        if w is not None and w > CAP_W[st]:
            over += 1
            if over >= CAP_N[st]:
                return {"t_s": t, "line": "board", "field": f"board {w} W > {CAP_W[st]:g} W on {CAP_N[st]} samples"}
        else:
            over = 0
    return None


def classify(st, step_dir):
    """X2 for one hold: complete, ended by a safety line, excluded, or not run; and why"""
    ej = S7.end_json(step_dir)
    reason = None if ej is None else str(ej.get("reason", ""))
    work = S7.work_entries(step_dir) if os.path.isdir(step_dir) else []
    n_work = len(work)
    n_failed = sum(1 for x in work if x.get("rc") not in (0, None))
    smk = [m for m in read_marks(step_dir) if m.get("kind") == "safety_trip"]
    why = []
    row = {"end_reason": reason, "end_exit": None if ej is None else ej.get("exit"), "work_processes": n_work,
           "planned_processes": PLAN_PROCS[st], "failed_processes": n_failed, "safety_trip_marks": [m.get("detail") for m in smk]}
    if not os.path.isdir(step_dir):
        return {**row, "status": CLASS_NOTRUN, "why_incomplete": ["no step directory"]}
    if n_work == 0:
        w = ["no HOLD work process"]
        if reason is not None and reason != "done":
            w.append(f"the step ended: {reason}")
        return {**row, "status": CLASS_NOTRUN, "why_incomplete": w}
    t0, b = work[0]["t_start_ms"] / 1e3, work[-1]["t_end_ms"] / 1e3
    span = b - t0
    need = PLAN_SPAN_S[st] - SPAN_SLACK_S
    row.update(t0_s=t0, b_s=b, span_s=r3(span, 2), span_needed_s=r3(need, 2))
    safety = bool(smk) or (reason or "").startswith("safety:")
    if ej is None:
        why.append("no end.json")
    elif reason != "done":
        why.append(f"the step ended: {reason}")
    if n_work < PLAN_PROCS[st]:
        why.append(f"{n_work} of {PLAN_PROCS[st]} work processes")
    if span < need:
        why.append(f"span {span:.2f} s < {need:.2f} s")
    tr = tel_t(step_dir, "REST")
    n_anchor = int((tr >= tr[-1] - ANCHOR_S).sum()) if tr.size else 0
    th = tel_t(step_dir, "HOLD")
    n_plateau = int(((th >= b - PLATEAU_S) & (th < b)).sum()) if th.size else 0
    row.update(anchor_lines=n_anchor, anchor_lines_needed=int(MIN_RATE_HZ * ANCHOR_S), plateau_lines=n_plateau,
               plateau_lines_needed=int(MIN_RATE_HZ * PLATEAU_S))
    if n_anchor < MIN_RATE_HZ * ANCHOR_S:
        why.append(f"anchor window {n_anchor} lines (< {MIN_RATE_HZ * ANCHOR_S:.0f})")
    if n_plateau < MIN_RATE_HZ * PLATEAU_S:
        why.append(f"plateau window {n_plateau} lines (< {MIN_RATE_HZ * PLATEAU_S:.0f})")
    if safety:
        row["safety_line"] = {"detail": smk[0].get("detail") if smk else (reason or "")[len("safety:"):],
                              "from": "a safety_trip mark" if smk else "end.json's reason",
                              "first_crossing_in_telemetry": first_line_crossing(step_dir, st, t0)}
        if not any(w.startswith("the step ended") for w in why):
            why.insert(0, "a safety line fired")
        return {**row, "status": CLASS_SAFETY, "why_incomplete": why}
    return {**row, "status": CLASS_COMPLETE if not why else CLASS_EXCL, "why_incomplete": why}


# ------------------------------------------------------------------------------------------------ the rules with X2
def rk3b_x2(v, cls):
    """v: score_e167's RK3-b verdict; cls: G1Q's X2 class"""
    if cls["status"] == CLASS_NOTRUN or v.startswith("not scored"):
        return v
    if cls["status"] == CLASS_COMPLETE:
        return v
    if cls["status"] == CLASS_SAFETY:
        return "FAIL (ended by a safety line)"
    return "NOT SCORED (incomplete window: " + "; ".join(cls["why_incomplete"]) + ")"


def rk3c_x2(cstat):
    """cstat: hold -> (status, measured rise), status 'inside' | 'outside' | 'small' (complete, under 10 C) | 'excluded'; X1's form"""
    if any(v[0] == "outside" for v in cstat.values()):
        return "FAIL"
    excluded = [k for k, v in cstat.items() if v[0] == "excluded"] + [k for k in EXPECTED_LARGE if k not in cstat]
    if not excluded:
        return "PASS" if any(v[0] == "inside" for v in cstat.values()) else "NOT SCORED (no rise of 10 C or more)"
    if all(cstat.get(k, ("excluded", None))[0] == "inside" for k in EXPECTED_LARGE):
        return "PASS"
    return "NOT SCORED (incomplete windows)"


def apply_x2(out, data):
    """X2 on score_e167.score's output for the session in data"""
    cls = {st: classify(st, os.path.join(data, st)) for st in HOLDS}
    rows = {st: out["holds"][st] for st in HOLDS if isinstance(out["holds"].get(st), dict) and "primary_M9a_at_own_d" in out["holds"][st]}
    cstat = {}
    for st in HOLDS:
        c = cls[st]["status"]
        row = rows.get(st)
        if c == CLASS_COMPLETE and row is not None:
            rise, fr = row.get("measured_rise_C"), row.get("A_frac_of_rise")
            if rise is not None and rise >= LARGE_RISE_C:
                cstat[st] = ("inside" if (fr is not None and abs(fr) <= RK3C_FRAC) else "outside", rise)
            else:
                cstat[st] = ("small", rise)
        elif c == CLASS_SAFETY:
            rise = None if row is None else row.get("measured_rise_C")
            cstat[st] = ("outside", rise) if st in EXPECTED_LARGE else ("small", rise)
        else:
            cstat[st] = ("excluded", None)
    v_b = rk3b_x2(out["rules"]["RK3_b"]["verdict"], cls["G1Q"])
    v_c = rk3c_x2(cstat)
    v = {"RK3_b": v_b, "RK3_c_aifoundry2": v_c}
    for st in HOLDS:
        row = rows.get(st)
        c = cls[st]["status"]
        if row is not None:
            if c == CLASS_COMPLETE:
                v[f"{st} carried"] = row["carried"]["verdict"]
                v[f"{st} carried clock"] = row["carried"]["clock_verdict"]
            elif c == CLASS_SAFETY:
                v[f"{st} carried"] = v[f"{st} carried clock"] = "FAIL (ended by a safety line)"
            else:
                v[f"{st} carried"] = v[f"{st} carried clock"] = "NOT SCORED (incomplete window)"
        else:
            v[st] = out["holds"][st].get("status") if isinstance(out["holds"].get(st), dict) else "NOT RUN"
        if c != CLASS_COMPLETE:
            v[f"{st} X2"] = c + (": " + "; ".join(cls[st]["why_incomplete"]) if cls[st]["why_incomplete"] else "")
    comp = [st for st in HOLDS if cls[st]["status"] == CLASS_COMPLETE and st in rows]
    sf = {"n_complete_holds": len(comp),
          "G1Q_plateau_err_from_the_bits_C": rows["G1Q"]["primary_M9a_at_own_d"]["plateau_err_C"] if "G1Q" in comp else None,
          "G2Q_clock_err_from_the_bits_MHz": rows["G2Q"]["primary_M9a_at_own_d"].get("clock_err_MHz") if "G2Q" in comp else None,
          "note": "over the complete holds only (X2); an incomplete hold's readings stay in holds as post hoc"}
    out["x2"] = {"holds": cls, "RK3_c_status": {k: {"status": a, "measured_rise_C": r} for k, (a, r) in cstat.items()},
                 "amendment": "E167.md.dated-note-2.md", "plan": {"processes": PLAN_PROCS, "span_s": PLAN_SPAN_S, "slack_s": SPAN_SLACK_S,
                                                                 "min_lines_per_s": MIN_RATE_HZ, "stops": {"die_C": STOP_C, "board_W": CAP_W,
                                                                                                           "board_consecutive": CAP_N}}}
    out["rules"]["RK3_b_x2"] = v_b
    out["rules"]["RK3_c_aifoundry2_x2"] = v_c
    out["session_figures_x2"] = sf
    out["verdicts_score_e167"] = out["verdicts"]
    out["verdicts"] = v
    out["registration"] = "7ba987b3 + E167.md.dated-note-2.md (X2)"
    return out


def score(data, e165=None):
    data = os.path.abspath(data)
    return apply_x2(S7.score(data, e165), data)


# ------------------------------------------------------------------------------------------------ self-test
E161D = S7.E161D


def _rewrite_gz(src, dst, keep):
    with gzip.open(src, "rt") as fi, gzip.open(dst, "wt") as fo:
        i = 0
        for ln in fi:
            if ln.startswith("{"):
                try:
                    t = json.loads(ln)["t_ms"] / 1e3
                except (ValueError, KeyError):
                    fo.write(ln)
                    continue
                if keep(t, i):
                    fo.write(ln)
                i += 1
            else:
                fo.write(ln)


def build_step(dst, st, spec):
    """one step directory from E161's committed one: spec None = copied whole; {"gate": True} = score_e167's gated layout; else any of
    cut (keep the first n HOLD work processes, telemetry to 1 s after the n-th's end), reason/exit (end.json), safety_mark (a safety_trip
    mark's detail at the cut), thin_plateau / thin_anchor (keep 2 lines of every 5 there), no_end_json, fail_one (rc 1 on process 40)"""
    src = os.path.join(E161D, st)
    if spec == "absent":
        return
    if spec and spec.get("latch_rest"):
        # the REST's telemetry with the hottest-sensor field at 72 C on every line; no HOLD; run_hpl's watcher ends the step (exit 4)
        os.makedirs(os.path.join(dst, "tel"))
        for f in os.listdir(os.path.join(src, "tel")):
            if f.startswith("REST"):
                with gzip.open(os.path.join(src, "tel", f), "rt") as fi, gzip.open(os.path.join(dst, "tel", f), "wt") as fo:
                    for ln in fi:
                        if ln.startswith("{"):
                            d = json.loads(ln)
                            d["temp_c"]["minshire"][2] = 72
                            ln = json.dumps(d) + "\n"
                        fo.write(ln)
        with gzip.open(os.path.join(dst, "launches.jsonl.gz"), "wt"):
            pass
        shutil.copy(os.path.join(src, "marks.jsonl"), os.path.join(dst, "marks.jsonl"))
        with open(os.path.join(dst, "marks.jsonl"), "a") as fo:
            fo.write(json.dumps({"t_ms": 0, "kind": "safety_trip", "detail": SAFE_DIE}) + "\n")
        json.dump({"t_end_ms": 0, "exit": 4, "reason": "safety:" + SAFE_DIE, "card_min": 0.1}, open(os.path.join(dst, "end.json"), "w"))
        return
    if spec and spec.get("gate"):
        os.makedirs(os.path.join(dst, "tel"))
        for f in os.listdir(os.path.join(src, "tel")):
            if f.startswith("REST"):
                shutil.copy(os.path.join(src, "tel", f), os.path.join(dst, "tel", f))
        with gzip.open(os.path.join(dst, "launches.jsonl.gz"), "wt"):
            pass
        shutil.copy(os.path.join(src, "marks.jsonl"), os.path.join(dst, "marks.jsonl"))
        json.dump({"t_end_ms": 0, "exit": 6, "reason": "gate:G1Q's REST anchor 49.4 C > 49.0 C", "card_min": 2.1},
                  open(os.path.join(dst, "end.json"), "w"))
        return
    shutil.copytree(src, dst)
    if not spec:
        return
    L = [json.loads(x) for x in gzip.open(os.path.join(src, "launches.jsonl.gz"), "rt") if x.strip()]
    work = [x for x in L if x.get("role") == "work" and str(x.get("run", "")).startswith("HOLD")]
    b_all = work[-1]["t_end_ms"] / 1e3
    cut_b = work[spec["cut"] - 1]["t_end_ms"] / 1e3 if spec.get("cut") else None
    if spec.get("cut") or spec.get("fail_one"):
        keep_ids = set(id(x) for x in work[:spec["cut"]]) if spec.get("cut") else set(id(x) for x in work)
        with gzip.open(os.path.join(dst, "launches.jsonl.gz"), "wt") as fo:
            for x in L:
                if x.get("role") == "work" and str(x.get("run", "")).startswith("HOLD") and id(x) not in keep_ids:
                    continue
                y = copy.deepcopy(x)
                if spec.get("fail_one") and x.get("proc") == 40:
                    y["rc"] = 1
                fo.write(json.dumps(y) + "\n")
    hold_f = sorted(glob.glob(os.path.join(dst, "tel", "HOLD-*.jsonl.gz")))[0]
    rest_f = sorted(glob.glob(os.path.join(dst, "tel", "REST-*.jsonl.gz")))[0]
    if cut_b is not None:
        tmp = hold_f + ".tmp.gz"
        _rewrite_gz(hold_f, tmp, lambda t, i: t <= cut_b + 1.0)
        os.replace(tmp, hold_f)
    if spec.get("latch_at_cut"):
        tmp = hold_f + ".tmp.gz"
        with gzip.open(hold_f, "rt") as fi, gzip.open(tmp, "wt") as fo:
            for ln in fi:
                if ln.startswith("{"):
                    d = json.loads(ln)
                    if d["t_ms"] / 1e3 >= cut_b - 2.0:
                        d["temp_c"]["minshire"][2] = 72
                        ln = json.dumps(d) + "\n"
                fo.write(ln)
        os.replace(tmp, hold_f)
    if spec.get("thin_plateau"):
        bb = cut_b if cut_b is not None else b_all
        tmp = hold_f + ".tmp.gz"
        _rewrite_gz(hold_f, tmp, lambda t, i: not (bb - PLATEAU_S <= t < bb) or (i % 5) < 2)
        os.replace(tmp, hold_f)
    if spec.get("thin_anchor"):
        tr = hm.load_tel([rest_f], sensor="fw")["t"]
        tl = float(tr[-1])
        tmp = rest_f + ".tmp.gz"
        _rewrite_gz(rest_f, tmp, lambda t, i: not (t >= tl - ANCHOR_S - 0.05) or (i % 5) < 2 or t >= tl - 1e-6)
        os.replace(tmp, rest_f)
    if spec.get("safety_mark"):
        with open(os.path.join(dst, "marks.jsonl"), "a") as fo:
            fo.write(json.dumps({"t_ms": int((cut_b or b_all) * 1e3), "kind": "safety_trip", "detail": spec["safety_mark"]}) + "\n")
    if spec.get("no_end_json"):
        os.remove(os.path.join(dst, "end.json"))
    elif "reason" in spec:
        json.dump({"t_end_ms": int(((cut_b or b_all) + 1.0) * 1e3), "exit": spec.get("exit", 0), "reason": spec["reason"], "card_min": 9.9},
                  open(os.path.join(dst, "end.json"), "w"))


def session_case(name, g1q=None, g2q=None):
    td = tempfile.mkdtemp(prefix="e167-x2-")
    try:
        build_step(os.path.join(td, "G1Q"), "G1Q", g1q)
        build_step(os.path.join(td, "G2Q"), "G2Q", g2q)
        res = score(td)
        return {"name": name, "verdicts": res["verdicts"], "x2_status": {st: res["x2"]["holds"][st]["status"] for st in HOLDS},
                "x2_why": {st: res["x2"]["holds"][st]["why_incomplete"] for st in HOLDS},
                "safety_line": {st: res["x2"]["holds"][st].get("safety_line") for st in HOLDS if res["x2"]["holds"][st].get("safety_line")},
                "verdicts_score_e167": res["verdicts_score_e167"], "n_complete": res["session_figures_x2"]["n_complete_holds"]}
    finally:
        shutil.rmtree(td, ignore_errors=True)


SAFE_DIE = "die 72 C >= 72 C"
FAIL_SAFE = "FAIL (ended by a safety line)"
NS_C = "NOT SCORED (incomplete windows)"
NS_W = "NOT SCORED (incomplete window)"


def session_cases():
    """X2 on sessions built from E161's committed G1Q and G2Q (each case: what changed -> the registered verdicts it must read)"""
    want = {
        "E161 as committed (both complete)": ({}, {"RK3_b": "PASS", "RK3_c_aifoundry2": "FAIL", "G1Q carried": "PASS", "G1Q carried clock": "PASS",
                                                   "G2Q carried": "PASS", "G2Q carried clock": "PASS"}),
        "G1Q cut after 60 processes by the die line (safety mark and reason)": (
            {"g1q": {"cut": 60, "exit": 4, "reason": "safety:" + SAFE_DIE, "safety_mark": SAFE_DIE}},
            {"RK3_b": FAIL_SAFE, "RK3_c_aifoundry2": "FAIL", "G1Q carried": FAIL_SAFE, "G1Q carried clock": FAIL_SAFE, "G2Q carried": "PASS"}),
        "G1Q cut after 60 by the die line on the hottest-sensor field (the latch at 72 C, the mean at 63 C)": (
            {"g1q": {"cut": 60, "exit": 4, "reason": "safety:" + SAFE_DIE, "safety_mark": SAFE_DIE, "latch_at_cut": True}},
            {"RK3_b": FAIL_SAFE, "RK3_c_aifoundry2": "FAIL", "G1Q carried": FAIL_SAFE, "G1Q carried clock": FAIL_SAFE}),
        "G1Q cut after 60 by the board line": (
            {"g1q": {"cut": 60, "exit": 4, "reason": "safety:board 81.2 W > 80 W on 3 samples", "safety_mark": "board 81.2 W > 80 W on 3 samples"}},
            {"RK3_b": FAIL_SAFE, "RK3_c_aifoundry2": "FAIL", "G1Q carried": FAIL_SAFE}),
        "G1Q cut after 60 by the queue's cutoff STOP file": (
            {"g1q": {"cut": 60, "exit": 4, "reason": "stop_file"}},
            {"RK3_b": "NOT SCORED (incomplete window: the step ended: stop_file; 60 of 93 work processes; span 504.88 s < 752.97 s)",
             "RK3_c_aifoundry2": NS_C, "G1Q carried": NS_W, "G1Q carried clock": NS_W, "G2Q carried": "PASS", "G2Q carried clock": "PASS"}),
        "G1Q cut after 60, STOP file read before the watcher's trip (a safety_trip mark, reason stop_file)": (
            {"g1q": {"cut": 60, "exit": 4, "reason": "stop_file", "safety_mark": SAFE_DIE}},
            {"RK3_b": FAIL_SAFE, "RK3_c_aifoundry2": "FAIL", "G1Q carried": FAIL_SAFE}),
        "G1Q cut after 80 by the protocol's cap (done:max_card_min)": (
            {"g1q": {"cut": 80, "exit": 0, "reason": "done:max_card_min"}},
            {"RK3_c_aifoundry2": NS_C, "G1Q carried": NS_W}),
        "G2Q cut after 50 by SIGTERM (G1Q complete, outside)": (
            {"g2q": {"cut": 50, "exit": 5, "reason": "signal:15"}},
            {"RK3_b": "PASS", "RK3_c_aifoundry2": "FAIL", "G1Q carried": "PASS", "G2Q carried": NS_W, "G2Q carried clock": NS_W}),
        "G2Q with no end.json": ({"g2q": {"no_end_json": True}}, {"RK3_c_aifoundry2": "FAIL", "G2Q carried": NS_W}),
        "G1Q's plateau window thinned to 2 lines a second": ({"g1q": {"thin_plateau": True}},
                                                             {"RK3_c_aifoundry2": NS_C, "G1Q carried": NS_W, "G2Q carried": "PASS"}),
        "G1Q's anchor window thinned to 2 lines a second": ({"g1q": {"thin_anchor": True}}, {"RK3_c_aifoundry2": NS_C, "G1Q carried": NS_W}),
        "G1Q one process long, ended done (the desk dry queue's shape)": (
            {"g1q": {"cut": 1, "exit": 0, "reason": "done"}},
            {"RK3_c_aifoundry2": NS_C, "G1Q carried": NS_W, "G1Q carried clock": NS_W}),
        "G1Q with one failed process (rc 1), ended done": ({"g1q": {"fail_one": True}},
                                                           {"RK3_b": "PASS", "RK3_c_aifoundry2": "FAIL", "G1Q carried": "PASS"}),
        "G1Q stopped at the start gate (exit 6), G2Q as committed (inside)": (
            {"g1q": {"gate": True}}, {"RK3_b": "not scored: the start gate", "RK3_c_aifoundry2": NS_C, "G1Q": "NOT RUN (the start gate)",
                                      "G2Q carried": "PASS", "G2Q carried clock": "PASS"}),
        "G2Q not run (no step directory: the registered subset)": ({"g2q": "absent"}, {"RK3_b": "PASS", "RK3_c_aifoundry2": "FAIL"}),
        "the latch at 72 C at idle: G1Q's REST stopped by the die line before any work, the queue ended (no G2Q)": (
            {"g1q": {"latch_rest": True}, "g2q": "absent"},
            {"RK3_b": "not scored: G1Q's hold did not run", "RK3_c_aifoundry2": NS_C, "G1Q": "NOT RUN (no HOLD work process)",
             "G2Q": "not run (no step directory)"}),
    }
    out, probs = [], []
    for name, (spec, w) in want.items():
        r = session_case(name, spec.get("g1q"), spec.get("g2q"))
        r["want"] = w
        bad = {k: (r["verdicts"].get(k), x) for k, x in w.items() if r["verdicts"].get(k) != x}
        r["ok"] = not bad
        if bad:
            probs.append(f"{name}: {bad}")
        out.append(r)
    # the gated session: score_e167 alone read RK3-c PASS on G2Q (fault 2 of the verifier); X2 reads it NOT SCORED
    g = [r for r in out if r["name"].startswith("G1Q stopped at the start gate")][0]
    if g["verdicts_score_e167"].get("RK3_c_aifoundry2") != "PASS":
        probs.append(f"the gated case under score_e167 alone read {g['verdicts_score_e167'].get('RK3_c_aifoundry2')}, not PASS")
    # the die-line cases name the field from the telemetry: E161's cut G1Q never reached 72 C on either field, so there the crossing is
    # none (the mark decides); with the latch raised to 72 C at the cut, the hottest-sensor field is named
    for r in out:
        sl = (r.get("safety_line") or {}).get("G1Q") or {}
        fc = sl.get("first_crossing_in_telemetry")
        if r["name"].startswith("G1Q cut after 60 by the die line on the hottest-sensor field"):
            if not fc or "minshire[2]" not in fc.get("field", "") or "minshire[0]" in fc.get("field", ""):
                probs.append(f"{r['name']}: the crossing read {fc}, not the hottest-sensor field alone")
        elif r["name"].startswith("G1Q cut after 60 by the die line (safety"):
            if fc is not None:
                probs.append(f"{r['name']}: a crossing read {fc} on E161's own telemetry")
    return out, probs


def rule_cases():
    """the decision functions on their edges"""
    probs, out = [], []
    I, O, S, X = "inside", "outside", "small", "excluded"

    def want(name, got, w):
        out.append({"case": name, "got": got, "want": w, "ok": got == w})
        if got != w:
            probs.append(f"{name}: {got} != {w}")
    want("RK3-c both complete and inside", rk3c_x2({"G1Q": (I, 16.0), "G2Q": (I, 18.0)}), "PASS")
    want("RK3-c both complete, G1Q outside", rk3c_x2({"G1Q": (O, 16.0), "G2Q": (I, 18.0)}), "FAIL")
    want("RK3-c G1Q under 10 C, G2Q inside (R4 as registered)", rk3c_x2({"G1Q": (S, 9.5), "G2Q": (I, 18.0)}), "PASS")
    want("RK3-c both under 10 C", rk3c_x2({"G1Q": (S, 9.5), "G2Q": (S, 9.0)}), "NOT SCORED (no rise of 10 C or more)")
    want("RK3-c G1Q excluded, G2Q inside", rk3c_x2({"G1Q": (X, None), "G2Q": (I, 18.0)}), NS_C)
    want("RK3-c G1Q excluded, G2Q outside", rk3c_x2({"G1Q": (X, None), "G2Q": (O, 18.0)}), "FAIL")
    want("RK3-c G1Q missing (not in the table), G2Q inside", rk3c_x2({"G2Q": (I, 18.0)}), NS_C)
    want("RK3-c both excluded", rk3c_x2({"G1Q": (X, None), "G2Q": (X, None)}), NS_C)
    want("RK3-c G1Q excluded, G2Q under 10 C", rk3c_x2({"G1Q": (X, None), "G2Q": (S, 9.0)}), NS_C)
    c = {"status": CLASS_COMPLETE, "why_incomplete": []}
    sft = {"status": CLASS_SAFETY, "why_incomplete": ["the step ended: safety:die 72 C >= 72 C"]}
    exc = {"status": CLASS_EXCL, "why_incomplete": ["the step ended: stop_file"]}
    nr = {"status": CLASS_NOTRUN, "why_incomplete": ["no HOLD work process"]}
    want("RK3-b complete PASS", rk3b_x2("PASS", c), "PASS")
    want("RK3-b complete FAIL", rk3b_x2("FAIL", c), "FAIL")
    want("RK3-b safety line", rk3b_x2("PASS", sft), FAIL_SAFE)
    want("RK3-b safety line, the trip regime", rk3b_x2("not scored: the trip regime", sft), "not scored: the trip regime")
    want("RK3-b excluded", rk3b_x2("PASS", exc), "NOT SCORED (incomplete window: the step ended: stop_file)")
    want("RK3-b excluded, a FAIL as read", rk3b_x2("FAIL", exc), "NOT SCORED (incomplete window: the step ended: stop_file)")
    want("RK3-b not run (gate)", rk3b_x2("not scored: the start gate", nr), "not scored: the start gate")
    want("RK3-b the trip edge inside the readout, complete", rk3b_x2("not scored: the trip edge inside the readout", c),
         "not scored: the trip edge inside the readout")
    return out, probs


def plan_problems():
    probs = []
    if PLAN_PROCS != {"G1Q": 93, "G2Q": 91}:
        probs.append(f"planned processes {PLAN_PROCS}")
    if PLAN_SPAN_S != {"G1Q": 782.97, "G2Q": 770.97}:
        probs.append(f"plan spans {PLAN_SPAN_S}")
    if STOP_C != {"G1Q": 72.0, "G2Q": 72.0} or CAP_W != {"G1Q": 80.0, "G2Q": 80.0} or CAP_N != {"G1Q": 3, "G2Q": 3}:
        probs.append("the stops differ from E161's")
    if set(EXPECTED_LARGE) != {"G1Q", "G2Q"}:
        probs.append(f"expected large rises {EXPECTED_LARGE}")
    return probs


def self_test():
    res = {"note": "E167's X2 scorer self-test (desk, before any E167 data): (1) score_e167.py's own self-test, re-run unchanged, passes "
                   "(E161's posthoc.json figures, C3, the frozen arms byte for byte, the gate, RA1.2, E2, the constants, and reduce_e161's six "
                   "registered verdicts on E161); (2) on E161's committed data X2 reads both holds complete and changes no verdict; (3) X2 "
                   "on sessions built from E161's committed holds, cut, thinned or stopped, against the verdicts the amendment registers; "
                   "(4) the decision functions on their edges; (5) the plan X2 reads, against the registered protocols and predictions"}
    base = S7.self_test()
    res["score_e167_self_test_ok"] = base["self_test_ok"]
    res["score_e167_self_test_problems"] = base["problems"]
    probs = [f"score_e167 self-test: {p}" for p in base["problems"]]
    e161 = score(E161D)
    res["E161"] = {"x2_status": {st: e161["x2"]["holds"][st]["status"] for st in HOLDS},
                   "x2_holds": {st: {k: e161["x2"]["holds"][st].get(k) for k in ("work_processes", "planned_processes", "span_s", "span_needed_s",
                                                                                   "anchor_lines", "plateau_lines", "end_reason", "failed_processes")}
                                for st in HOLDS},
                   "verdicts": e161["verdicts"], "verdicts_score_e167": e161["verdicts_score_e167"],
                   "session_figures_x2": e161["session_figures_x2"]}
    if any(e161["x2"]["holds"][st]["status"] != CLASS_COMPLETE for st in HOLDS):
        probs.append("E161: a hold is not complete under X2")
    if e161["verdicts"] != e161["verdicts_score_e167"]:
        probs.append("E161: X2 changed a verdict")
    if e161["verdicts"] != base["E161_reproduction"]["verdicts"]:
        probs.append("E161: verdicts differ from score_e167's self-test")
    sc, p2 = session_cases()
    res["session_cases"] = sc
    res["session_cases_passed"] = f"{sum(1 for r in sc if r['ok'])} of {len(sc)}"
    rc, p3 = rule_cases()
    res["rule_cases"] = rc
    res["rule_cases_passed"] = f"{sum(1 for r in rc if r['ok'])} of {len(rc)}"
    p4 = plan_problems()
    res["plan"] = {"processes": PLAN_PROCS, "span_s": PLAN_SPAN_S, "slack_s": SPAN_SLACK_S, "min_lines_per_s": MIN_RATE_HZ,
                   "stops": {"die_C": STOP_C, "board_W": CAP_W, "consecutive": CAP_N}, "expected_large": list(EXPECTED_LARGE)}
    probs += p2 + p3 + p4
    res["problems"] = probs
    res["self_test_ok"] = not probs
    return res


def main():
    args = sys.argv[1:]
    jout, e165 = None, None
    for flag in ("--json", "--e165-anchors"):
        if flag in args:
            i = args.index(flag)
            if flag == "--json":
                jout = args[i + 1]
            else:
                e165 = args[i + 1]
            args = args[:i] + args[i + 2:]
    if not args:
        raise SystemExit(__doc__)
    res = self_test() if args[0] == "--self-test" else score(args[0], e165)
    txt = S7._json(res)
    if jout:
        open(jout, "w").write(txt + "\n")
    print(txt)
    if args[0] == "--self-test" and not res["self_test_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
