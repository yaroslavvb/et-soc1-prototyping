#!/usr/bin/env python3
"""E168 (Q141(o)): the registered reduction. No card. It is E159's reduce_e159.py ported to E168: it scores E168's holds with Q140(q)'s
FROZEN scorer (docs/reports/data/2026-11-04-q140q-gemm-g4-stride/score_e168.py), unchanged, behind its hash checks, and adds what the
frozen rules name but the scorer does not compute (which holds are scored, sessions pooled, the checks of C, the safety record, card
time), and amendment A2's reported test (226249e1). Run on the Intel (the frozen scorer needs numpy):

    /usr/bin/python3 -B tools/claims-v3/e168/reduce_e168.py <RUNS dir: the queue's smoke/, stoptest-*/, s1/ (s2/ ...)> --out results.json \
        [--anchors <E165's zeros-anchor reads, predict_m9_a2.session_delta's layout>] > reduce.txt

  1. THE FREEZE. score_e168.check(): the 9 files of frozen-sha256-e168.json (e39d06da) equal their bytes; the 18-file sidecar
     frozen-sha256-e168-scorer.txt (1bfaa4e4): every line's sha256 recomputed (`shasum -a 256 -c`'s check); A2's
     predictions-e168-a2.json at its registered sha256. If any differs: exit 2, nothing is scored.
  2. WHICH HOLDS ARE SCORED (E159's rule, ported; Q140(q)'s A7: "a hold not run or cut by a stop is not scored"). A hold is a run whose
     label is one of the nine frozen cells or A2's, with processes >= 2. It is COMPLETE when all of its planned processes (12) have a
     work launch record with rc 0, every kernel record of it is ok and each process carries rgm136's check of C (a record with test
     "check", ok), and no safety_trip mark falls between its first process's start and its last process's end. Otherwise it is CUT:
     listed, not scored. The check-of-C clause is E168's (every E159 work launch carried one); a session whose e168.json says --dry
     (the toy card, which writes no check of C) is not held to it, and each of its holds says so.
  3. A7, THE REGISTERED SCORE. Each session directory is scored on its own by score_e168.score with predictions-e168.json as frozen (the
     scorer's default path), on a temporary copy of the session: the same tel/ (a link), the launch records gzipped as the scorer reads
     them, and runs.jsonl with every hold left out that is not a complete one of the nine (A2's hold is never passed here; the frozen
     file does not name it either). With --anchors, the scorer's own second arm G4_own_anchors (A6), here E165's reads of the same
     day, reported and labelled "E165's session". The rows of every session are pooled and the verdicts recomputed from the scorer's
     own rows with the scorer's own arithmetic: per quantity (measured - G4: the window clock within 15 MHz, the board within 2 W, the
     window die within 1 C) PASS when at least 8 of the 9 holds are inside (with fewer than 9 scored, all inside), else FAIL, with the
     count; the increment rule (int8 W8A8 real and int8 sparse50 at S2, minus int8 zeros at S2, window board, within the frozen band of
     1.328 W); every arm's rms and mean; G4's rms below G3's as frozen and below E136's law's. Printed over every scored hold (the
     primary) and over the registered subset (the six fp32 random holds). With one session, the recomputed verdicts must equal the
     scorer's own (a check of this file).
  4. A2, REPORTED (REGISTRATION-A2-cold-int8-zeros.md section 3). A2's hold, if complete, and the warm int8 zeros hold, scored by the
     same function with ppath = predictions-e168-a2.json, rows only; the warm row must equal its step-3 row (else the reading is
     labelled). The cold hold's measured - G4 against A7's lines, not counted. The start dependence: dW = the cold hold's window board -
     the warm one's, against dW_G4 (the same difference of the G4 rows), dW_G3, dW_E136 and the frozen nominal +1.334 W; the reading:
     h = dW_G4 / 2; SUPPORTED if dW >= +h, NO START DEPENDENCE if -h < dW < +h, OPPOSITE SIGN if dW <= -h; no reading if dW_G4 <= 0.2 W.
  5. R0, the checks of C: every kernel record ok in every work launch of every session (smoke, stop tests, holds), E159's count; beside
     it, every work launch without rgm136's check-of-C record, listed. A failure labels every verdict.
  6. THE SAFETY RECORD (E159's): per run the highest board sample, the highest die mean and hottest-sensor field, every safety_trip mark,
     every hold not admitted (skipped.jsonl) and every peak-lock mark; the stop-path tests' records (queue.jsonl stoptest_detail and
     stoptest_check); the TDP and threshold read after every run and in the queue's two snapshots; each hold's start gate (reached,
     waited, its reading); card time from the first card touch (snapshot-start) to the queue's end.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
G4DIR = os.path.join(ROOT, "docs/reports/data/2026-11-04-q140q-gemm-g4-stride")
sys.path.insert(0, G4DIR)
import score_e168 as SC  # noqa: E402  (Q140(q)'s frozen scorer: check(), score(), its RULE)

PRED_PATH = os.path.join(G4DIR, "predictions-e168.json")
A2_PATH = os.path.join(HERE, "predictions-e168-a2.json")
A2_SHA256 = "2afb290f62f7cc722c1f58837c18ab545f914863107a162653c38459c35fafe6"     # as committed in 226249e1
SIDECAR = os.path.join(G4DIR, "frozen-sha256-e168-scorer.txt")
PRED = json.load(open(PRED_PATH))
A2 = json.load(open(A2_PATH))
NINE = list(PRED["design"]["order"])
A2_LABEL = "S2-int8-zeros-cold"
WARM_ZEROS = "S2-int8-zeros-warm55"
SUBSET = [c for c in NINE if PRED["cells"][c]["type"] == "fp32" and PRED["cells"][c]["kind"] == "randn"]
ALL_HOLDS = NINE + [A2_LABEL]
N_PROC = int(PRED["design"]["hold"]["processes"])
RULE = dict(SC.RULE)
ARMS = ("G4", "G4_own_anchors", "G3_as_frozen", "E136_law", "chain_on_measured")
NO_POWER_W = 0.2


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def freeze_check():
    """[] if the 9 frozen files, the 18-file sidecar and A2's file are as registered, else what differs"""
    bad = []
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok9 = SC.check()
    if not ok9:
        bad.append("score_e168.check: " + buf.getvalue().strip())
    n = 0
    for ln in open(SIDECAR):
        ln = ln.strip()
        if not ln:
            continue
        want, rel = ln.split(None, 1)
        p = os.path.join(G4DIR, rel)
        got = sha(p) if os.path.isfile(p) else None
        n += 1
        if got != want:
            bad.append(f"sidecar: {rel} sha256 {got}, frozen {want}")
    if n != 18:
        bad.append(f"sidecar: {n} lines, not 18")
    got = sha(A2_PATH)
    if got != A2_SHA256:
        bad.append(f"A2: {os.path.relpath(A2_PATH, ROOT)} sha256 {got}, registered {A2_SHA256}")
    return bad, n


def jl(path):
    out = []
    op = gzip.open if path.endswith(".gz") else open
    try:
        with op(path, "rt") as f:
            for ln in f:
                ln = ln.strip()
                if ln.startswith("{"):
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def launches_path(sd):
    for n in ("launches.jsonl.gz", "launches.jsonl"):
        if os.path.exists(os.path.join(sd, n)):
            return os.path.join(sd, n)
    return None


def tel_rows(sd, run):
    for ext in (".jsonl.gz", ".jsonl"):
        p = os.path.join(sd, "tel", run + ext)
        if os.path.exists(p):
            rows = []
            for d in jl(p):
                ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                rows.append((d.get("t_ms"), d.get("board_w"), ms[0], ms[2] if len(ms) > 2 else None, (d.get("mhz") or {}).get("minion")))
            return rows
    return []


def sessions(runs_dir):
    """the queue's session directories in order (s1, s2, ...); a refused start (sN.refusedK) holds no run"""
    out, k = [], 1
    while os.path.isdir(os.path.join(runs_dir, f"s{k}")):
        out.append(os.path.join(runs_dir, f"s{k}"))
        k += 1
    return out


def has_check(p):
    return any(k.get("test") == "check" and k.get("ok") for k in p.get("sparsity", []))


def is_dry(sd):
    """True when the session's own run record (run_e168.py's e168.json) says --dry: the toy card writes no check of C"""
    try:
        return bool(json.load(open(os.path.join(sd, "e168.json"))).get("dry"))
    except (OSError, ValueError):
        return False


def holds_of(sd):
    """(complete, cut) holds of a session: each a dict with the run, the label, the gate and why it is cut. A --dry session (the toy
    card, no check of C) is not held to the check-of-C clause, and says so in each hold's record."""
    runs = jl(os.path.join(sd, "runs.jsonl"))
    L = jl(launches_path(sd) or os.path.join(sd, "launches.jsonl"))
    trips = [m for m in jl(os.path.join(sd, "marks.jsonl")) if m.get("kind") == "safety_trip"]
    dry = is_dry(sd)
    good, cut = [], []
    for r in runs:
        if r.get("label") not in ALL_HOLDS or r.get("processes", 1) < 2:
            continue
        ps = [p for p in L if p.get("run") == r["run"] and p.get("role") == "work"]
        why = []
        want = int(r.get("processes") or N_PROC)
        if len(ps) < want:
            why.append(f"{len(ps)} of {want} processes recorded")
        if any(p.get("rc") != 0 for p in ps):
            why.append("a process rc not 0")
        recs = [k for p in ps for k in p.get("sparsity", [])]
        if not recs or not all(k.get("ok") for k in recs):
            why.append(f"kernel records {len(recs)}, not all ok (the check of C)")
        nochk = sum(1 for p in ps if not has_check(p))
        if nochk and not dry:
            why.append(f"{nochk} process(es) without rgm136's check of C")
        if ps:
            a, b = min(p["t_start_ms"] for p in ps), max(p["t_end_ms"] for p in ps)
            if any(a <= m.get("t_ms", 0) <= b for m in trips):
                why.append("a safety stop fired inside the hold")
        h = {"run": r["run"], "label": r["label"], "processes": len(ps), "planned": want, "gate": r.get("gate")}
        if dry:
            h["dry"] = "a --dry session: the toy card writes no check of C, so the check-of-C clause is not applied"
        if why:
            h["why_cut"] = "; ".join(why)
            cut.append(h)
        else:
            good.append(h)
    return good, cut


def temp_session(sd, keep_runs, drop_labels):
    """a temporary copy of a session for the frozen scorer: tel/ linked, launches gzipped, runs.jsonl less the holds not kept"""
    tmp = tempfile.mkdtemp(prefix="e168-reduce-", dir=os.environ.get("TMPDIR"))
    os.symlink(os.path.abspath(os.path.join(sd, "tel")), os.path.join(tmp, "tel"))
    lp = launches_path(sd)
    if lp.endswith(".gz"):
        os.symlink(os.path.abspath(lp), os.path.join(tmp, "launches.jsonl.gz"))
    else:
        with open(lp, "rb") as fi, gzip.open(os.path.join(tmp, "launches.jsonl.gz"), "wb") as fo:
            shutil.copyfileobj(fi, fo)
    with open(os.path.join(tmp, "runs.jsonl"), "w") as f:
        for r in jl(os.path.join(sd, "runs.jsonl")):
            if r.get("label") in ALL_HOLDS and r.get("processes", 1) >= 2 and (r["run"] not in keep_runs or r.get("label") in drop_labels):
                continue
            f.write(json.dumps(r) + "\n")
    return tmp


def quiet_score(tmp, ppath=None, anchors=None):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = SC.score(tmp, ppath=ppath, anchors=anchors)
    return res, buf.getvalue()


def summarize(rows, P):
    """the frozen scorer's summary, verdict, increment rule and rms comparisons, its own arithmetic, recomputed for any set of its rows"""
    summ = {}
    for a in ARMS:
        for q in RULE:
            e = [x["err"][a][q] for x in rows if a in x["err"] and q in x["err"][a]]
            if e:
                summ[f"{a}.{q}"] = {"n": len(e), "rms": round(math.sqrt(sum(v * v for v in e) / len(e)), 3), "mean": round(sum(e) / len(e), 3),
                                    "inside": int(sum(abs(v) <= RULE[q] for v in e))}
    n = len(rows)
    verdict = {q: ("PASS" if n and sum(x["inside_G4"][q] for x in rows) >= min(8, n) and (n >= 9 or all(x["inside_G4"][q] for x in rows)) else "FAIL")
               + f" ({sum(x['inside_G4'][q] for x in rows)} of {n}; the rule needs 8 of 9)" for q in RULE}
    inc = {}
    by = {x["cell"]: x for x in rows}
    z = by.get(WARM_ZEROS)
    for k in ("real_smol_w8a8_down", "sparse50"):
        h = by.get(f"S2-int8-{k}-warm55")
        if z and h:
            rule = P["cells"][f"S2-int8-{k}-warm55"]["increment_rule"]
            mi = h["meas"]["w"] - z["meas"]["w"]
            pi = h["pred"]["G4"]["w"] - z["pred"]["G4"]["w"]
            inc[k] = {"measured_increment_w": round(mi, 3), "G4_increment_w": round(pi, 3), "err_w": round(mi - pi, 3), "band_w": rule["band_w"],
                      "verdict": "PASS" if abs(mi - pi) <= rule["band_w"] else "FAIL"}
    below = {ref: {q: summ.get(f"G4.{q}", {}).get("rms", 1e9) < summ.get(f"{ref}.{q}", {}).get("rms", -1) for q in RULE} for ref in ("G3_as_frozen", "E136_law")}
    return {"summary": summ, "verdict_G4": verdict, "increment_rule": inc, "G4_rms_below": below, "holds": [x["cell"] for x in rows]}


def a2_reading(cold, warm):
    """A2's reported test of G4's start dependence (REGISTRATION-A2-cold-int8-zeros.md section 3) on the two rows"""
    def dq(arm, q):
        return cold["pred"][arm][q] - warm["pred"][arm][q]
    dW = cold["meas"]["w"] - warm["meas"]["w"]
    dG4 = dq("G4", "w")
    out = {"dW_meas_w": round(dW, 3), "dW_G4_w": round(dG4, 3), "dW_G3_as_frozen_w": round(dq("G3_as_frozen", "w"), 3), "dW_E136_law_w": round(dq("E136_law", "w"), 3),
           "dW_G4_nominal_frozen_w": A2["start_dependence"]["nominal_frozen"]["G4"]["w"], "dW_G3_nominal_frozen_w": A2["start_dependence"]["nominal_frozen"]["G3_as_frozen"]["w"],
           "dW_meas_minus_G4_w": round(dW - dG4, 3), "dW_meas_minus_G3_w": round(dW - dq("G3_as_frozen", "w"), 3),
           "dDie_meas_c": round(cold["meas"]["die"] - warm["meas"]["die"], 3), "dDie_G4_c": round(dq("G4", "die"), 3),
           "die_start_cold_c": round(cold["die_start"], 2), "die_start_warm_c": round(warm["die_start"], 2)}
    if "G4_own_anchors" in cold["pred"] and "G4_own_anchors" in warm["pred"]:
        out["dW_G4_own_anchors_w"] = round(dq("G4_own_anchors", "w"), 3)
    h = dG4 / 2.0
    out["h_w"] = round(h, 3)
    if dG4 <= NO_POWER_W:
        out["reading"] = f"NO READING: G4's mechanical difference {dG4:+.3f} W is {NO_POWER_W} W or less (the starts too close); the test has no power"
    elif dW >= h:
        out["reading"] = "G4's start dependence SUPPORTED"
    elif dW <= -h:
        out["reading"] = "OPPOSITE SIGN: the window board falls with the start (the direction of a leakage law in the absolute die)"
    else:
        out["reading"] = "NO START DEPENDENCE (E159's reading)"
    return out


def safety(runs_dir):
    out = {"runs": [], "trips": [], "not_admitted": [], "peak_lock": [], "end": {}, "stoptests": [], "config": [], "gates": []}
    names = [n for n in ("smoke", "stoptest-board", "stoptest-die") if os.path.isdir(os.path.join(runs_dir, n))] + [os.path.basename(s) for s in sessions(runs_dir)]
    for n in names:
        sd = os.path.join(runs_dir, n)
        try:
            out["end"][n] = json.load(open(os.path.join(sd, "end.json")))
        except (OSError, ValueError):
            out["end"][n] = None
        for m in jl(os.path.join(sd, "marks.jsonl")):
            if m.get("kind") == "safety_trip":
                out["trips"].append({"session": n, **m})
            if m.get("kind") == "e105_peak_lock":
                out["peak_lock"].append({"session": n, **m})
        for s in jl(os.path.join(sd, "skipped.jsonl")):
            out["not_admitted"].append({"session": n, **s})
        for r in jl(os.path.join(sd, "runs.jsonl")):
            rows = tel_rows(sd, r["run"])
            ws = [w for _, w, _, _, _ in rows if w is not None]
            dm = [d for _, _, d, _, _ in rows if d is not None]
            hs = [h for _, _, _, h, _ in rows if h is not None]
            c = (r.get("queries") or {}).get("config") or {}
            out["runs"].append({"session": n, "run": r["run"], "label": r.get("label"), "processes": r.get("processes"), "samples": len(rows),
                                "board_max_w": max(ws) if ws else None, "die_mean_max_c": max(dm) if dm else None, "hottest_field_max_c": max(hs) if hs else None,
                                "hottest_field_min_c": min(hs) if hs else None})
            out["config"].append({"session": n, "run": r["run"], "tdp_w": c.get("tdp_w"), "temp_threshold_c": c.get("temp_threshold_c"),
                                  "power_state_name": c.get("power_state_name"), "minion_mhz": c.get("minion_mhz")})
            if r.get("label") in ALL_HOLDS:
                out["gates"].append({"session": n, "run": r["run"], "label": r.get("label"), "gate": r.get("gate")})
    q = jl(os.path.join(runs_dir, "queue.jsonl"))
    out["stoptests"] = [x for x in q if x.get("kind") in ("stoptest_detail", "stoptest_check", "smoke_check", "queue_halt")]
    snaps = {}
    for tag in ("start", "end"):
        try:
            snaps[tag] = json.load(open(os.path.join(runs_dir, f"snapshot-{tag}.json")))
        except (OSError, ValueError):
            snaps[tag] = None
    out["snapshots"] = {k: (None if v is None else {"t_ms": v.get("t_ms"), "config": v.get("config")}) for k, v in snaps.items()}
    qe = [x for x in q if x.get("kind") == "queue_end"]
    t0 = (snaps.get("start") or {}).get("t_ms")
    t1 = qe[-1].get("card_free_ms") if qe else None
    out["card_time"] = {"first_touch_ms": t0, "card_free_ms": t1, "minutes": None if (t0 is None or t1 is None) else round((t1 - t0) / 60000.0, 2)}
    ws = [r["board_max_w"] for r in out["runs"] if r["board_max_w"] is not None]
    dm = [r["die_mean_max_c"] for r in out["runs"] if r["die_mean_max_c"] is not None]
    hs = [r["hottest_field_max_c"] for r in out["runs"] if r["hottest_field_max_c"] is not None]
    out["peaks"] = {"board_max_w": max(ws) if ws else None, "die_mean_max_c": max(dm) if dm else None, "hottest_field_max_c": max(hs) if hs else None}
    out["config_read"] = sorted({(c["tdp_w"], c["temp_threshold_c"]) for c in out["config"] if c["tdp_w"] is not None})
    return out


def checks_of_c(runs_dir):
    """R0: every kernel record ok in every work launch of every session (E159's count); beside it, the work launches with no check of C"""
    n, bad, nochk, launches = 0, [], [], 0
    names = [x for x in ("smoke", "stoptest-board", "stoptest-die") if os.path.isdir(os.path.join(runs_dir, x))] + [os.path.basename(s) for s in sessions(runs_dir)]
    for s in names:
        sd = os.path.join(runs_dir, s)
        for p in jl(launches_path(sd) or os.path.join(sd, "launches.jsonl")):
            if p.get("role") != "work":
                continue
            launches += 1
            if not has_check(p):
                nochk.append({"session": s, "run": p.get("run"), "proc": p.get("proc")})
            for k in p.get("sparsity", []):
                n += 1
                if not k.get("ok"):
                    bad.append({"session": s, "run": p.get("run"), "result": k.get("result"), "test": k.get("test")})
    return {"kernel_records": n, "work_launches": launches, "not_ok": bad, "launches_without_check_of_C": nochk,
            "verdict": "PASS" if n and not bad else ("FAIL" if bad else "NO RECORDS")}


def jdefault(o):
    return o.tolist() if hasattr(o, "tolist") else (bool(o) if isinstance(o, (bool,)) else str(o))


def reduce(runs_dir, outp=None, check=True, anchors=None):
    if check:
        bad, n = freeze_check()
        if bad:
            print("FREEZE CHECK FAILED: " + "; ".join(bad))
            raise SystemExit(2)
        print(f"FREEZE OK: score_e168.check 9 files; the sidecar {n} of 18 OK; A2's predictions-e168-a2.json {A2_SHA256[:12]}... as registered")
    rows, cut, complete, a2rows, per_session, consistency = [], [], [], [], {}, []
    for sd in sessions(runs_dir):
        name = os.path.basename(sd)
        good, badh = holds_of(sd)
        cut += [{"session": name, **h} for h in badh]
        complete += [{"session": name, **h} for h in good]
        keep = {h["run"] for h in good}
        nine_runs = {h["run"] for h in good if h["label"] in NINE}
        if nine_runs:
            tmp = temp_session(sd, nine_runs, {A2_LABEL})
            try:
                res, _ = quiet_score(tmp, anchors=anchors)
            finally:
                shutil.rmtree(tmp)
            per_session[name] = {"verdict_G4": res["verdict_G4"], "increment_rule": res["increment_rule"], "G4_rms_below": res["G4_rms_below"], "n": len(res["rows"])}
            for x in res["rows"]:
                x["session"] = name
                rows.append(x)
        if any(h["label"] == A2_LABEL for h in good):
            tmp = temp_session(sd, keep, set())
            try:
                res2, _ = quiet_score(tmp, ppath=A2_PATH, anchors=anchors)
            finally:
                shutil.rmtree(tmp)
            for x in res2["rows"]:
                x["session"] = name
                a2rows.append(x)
    order = {c: i for i, c in enumerate(NINE)}
    rows.sort(key=lambda x: order.get(x["cell"], 99))
    allv = summarize(rows, PRED)
    subv = summarize([x for x in rows if x["cell"] in SUBSET], PRED)
    subv["complete"] = all(c in subv["holds"] for c in SUBSET)
    if len(per_session) == 1:
        only = next(iter(per_session.values()))
        consistency.append({"check": "the recomputed verdicts equal the frozen scorer's own (one session)",
                            "ok": only["verdict_G4"] == allv["verdict_G4"] and only["increment_rule"] == allv["increment_rule"]})
    a2 = {"label": A2_LABEL, "run": any(h["label"] == A2_LABEL for h in complete), "cut": [c for c in cut if c["label"] == A2_LABEL]}
    cold = next((x for x in a2rows if x["cell"] == A2_LABEL), None)
    warm2 = next((x for x in a2rows if x["cell"] == WARM_ZEROS), None)
    warm = next((x for x in rows if x["cell"] == WARM_ZEROS), None)
    if cold is not None:
        a2["cold_row"] = cold
        a2["cold_inside_A7_lines"] = cold["inside_G4"]
        a2["cold_err_G4"] = cold["err"]["G4"]
        a2["frozen_nominal_cold"] = A2["cells"][A2_LABEL]["G4"]
        if warm is not None and warm2 is not None:
            same = all(abs(warm2["pred"]["G4"][q] - warm["pred"]["G4"][q]) < 1e-9 and abs(warm2["meas"][q] - warm["meas"][q]) < 1e-9 for q in RULE)
            consistency.append({"check": "the warm zeros hold's row in A2's call equals its A7 row", "ok": same})
            a2["start_dependence"] = a2_reading(cold, warm)
            if not same:
                a2["start_dependence"]["reading"] += " (LABELLED: the warm row differs between the two calls)"
        else:
            a2["start_dependence"] = {"reading": "NO READING: the warm int8 zeros hold was not scored"}
    else:
        a2["start_dependence"] = {"reading": "NOT RUN or CUT: A2's hold was not scored" + (f" ({a2['cut'][0]['why_cut']})" if a2["cut"] else "")}
    r0 = checks_of_c(runs_dir)
    sf = safety(runs_dir)
    out = {"experiment": "E168", "request": "Q141", "freeze": {"registration": "49575094", "predictions_and_scorer": "e39d06da", "A1_and_sidecar": "1bfaa4e4",
                                                            "A2": "226249e1", "predictions_sha256": sha(PRED_PATH), "a2_sha256": sha(A2_PATH)},
           "anchors": None if not anchors else {"path": anchors, "label": "E165's session, not E168's (A2 section 3): G4_own_anchors is reported only"},
           "rule": RULE, "rows": rows, "cut": cut, "complete": complete, "all_scored": allv, "registered_subset": subv, "per_session": per_session,
           "A2_reported": a2, "consistency": consistency, "R0_checks_of_C": r0, "labelled": r0["verdict"] != "PASS", "safety": sf}
    print()
    print("E168 reduction (registered): Q140(q)'s frozen scorer behind its hash checks, cut holds left out, A7's verdicts, A2's reported test, R0, the safety record")
    print(f"complete holds: {[(c['session'], c['label']) for c in complete]}; cut: {[(c['label'], c['why_cut']) for c in cut]}")
    print(f"{'hold':36s} {'measured MHz/W/C':>22s} | {'G4':>20s} | {'G4 err':>18s} | in  | {'G3 as frozen':>20s} | {'E136 law':>20s} | chain die | start")
    for x in rows + ([cold] if cold is not None else []):
        m, g, e, g3, lw = x["meas"], x["pred"]["G4"], x["err"]["G4"], x["pred"]["G3_as_frozen"], x["pred"]["E136_law"]
        ins = "".join("y" if x["inside_G4"][q] else "n" for q in ("mhz", "w", "die"))
        tag = " (A2, reported)" if x is cold else ""
        print(f"{x['cell']:36s} {m['mhz']:6.1f} {m['w']:6.2f} {m['die']:6.2f} | {g['mhz']:6.1f} {g['w']:6.2f} {g['die']:6.2f} | {e['mhz']:+6.1f} {e['w']:+5.2f} {e['die']:+5.2f} | "
              f"{ins} | {g3['mhz']:6.1f} {g3['w']:6.2f} {g3['die']:6.2f} | {lw['mhz']:6.1f} {lw['w']:6.2f} {lw['die']:6.2f} | {x['pred']['chain_on_measured']['die']:9.2f} | "
              f"{x['die_start']:5.1f}{tag}")
    for tag, v in (("A7, ALL SCORED HOLDS (the primary)", allv), ("THE REGISTERED SUBSET (the six fp32 random holds)", subv)):
        print(f"{tag}: G4 {json.dumps(v['verdict_G4'])}; increment rule {json.dumps(v['increment_rule'])}; G4 rms below {json.dumps(v['G4_rms_below'])}")
        for a in ARMS:
            s = "; ".join(f"{q} {v['summary'][f'{a}.{q}']['rms']} rms ({v['summary'][f'{a}.{q}']['mean']:+} mean, {v['summary'][f'{a}.{q}']['inside']} of {v['summary'][f'{a}.{q}']['n']} inside)"
                          for q in RULE if f"{a}.{q}" in v["summary"])
            if s:
                print(f"   {a:20s} {s}")
    print(f"A2 (reported, not in A7): {json.dumps(a2['start_dependence'])}")
    if cold is not None:
        print(f"   the cold hold's measured - G4 {json.dumps({q: round(v, 3) for q, v in cold['err']['G4'].items()})}; inside A7's lines {json.dumps(cold['inside_G4'])} (not counted)")
    print(f"consistency: {json.dumps(consistency)}")
    print(f"R0 (checks of C): {r0['verdict']} ({r0['kernel_records']} kernel records in {r0['work_launches']} work launches, {len(r0['not_ok'])} not ok; "
          f"{len(r0['launches_without_check_of_C'])} work launches without a check-of-C record){' -- EVERY VERDICT LABELLED' if out['labelled'] else ''}")
    print(f"safety: peaks {sf['peaks']}; trips {[(t['session'], t.get('detail')) for t in sf['trips']]}; not admitted {[(s['label'], s['why']) for s in sf['not_admitted']]}; "
          f"peak locks {len(sf['peak_lock'])}; config read (TDP W, threshold C) {sf['config_read']}; card time {sf['card_time']}")
    print("gates: " + "; ".join(f"{g['label']} {((g['gate'] or {}).get('max_c'))} C reached {((g['gate'] or {}).get('reached'))} after {((g['gate'] or {}).get('held_s'))} s "
                               f"at {((g['gate'] or {}).get('reading') or [None])[0]} C" for g in sf["gates"]))
    if outp:
        json.dump(out, open(outp, "w"), indent=1, default=jdefault)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    outp = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    anc = sys.argv[sys.argv.index("--anchors") + 1] if "--anchors" in sys.argv else None
    reduce(os.path.abspath(sys.argv[1]), outp, check="--no-check" not in sys.argv, anchors=anc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
