#!/usr/bin/env python3
"""Q142(h2) fix pass: M11's HC1-B and I8P-B reader, v2, under README-h2-reader.md.dated-note-1.md (Thu 5 Nov 2026, written before any E171
or E172 data). It is read_hc1b_i8pb.py (lab 21666b23, 10:07:38 PST; it stays as committed and is not run on the card day) with four
changes, each marked "v2 (note 1, change N)" where it is made. The verifier of Q142(h2) found them:

  1. The runs table in reduce_e78's own form (its fault 1, major). v1 required runs.csv to hold exactly the reduction's kept runs, so it
     refused (exit 6) every session whose reduction set a pass aside or failed a run. reduce_e78.py, which reduce_e171.py and
     reduce_e172.py run unchanged, writes EVERY run of every pass it reduces to runs.csv, and counts 'kept' without the failed runs and
     without the runs of a set-aside or configuration-flagged pass. v2 checks the table as reduce_e78 writes it, all of:
       (a) its rows number the reduction's 'runs';
       (b) every kept pass (the reduction's 'passes') has rows in it;
       (c) the kept passes' rows without a fail number exactly the reduction's 'kept';
       (d) every other pass in it is named in 'passes_set_aside' or 'passes_config_flags', or every one of its runs failed (the
           complement of reduce_e78's kept set);
       (e) the runs it marks failed are, as (pass, item, position), the reduction's 'failed' list.
     Any of these false: refusal 6, nothing written. The run length stays fit_m6.heat_rows' rule over the whole table, every pass and
     run in it, as v1 applied it (the rule M10's heat rows were built with).
  2. The C-session check re-run (its fault 2). After the identity checks and before any table is read, ccsessions_p8.check(run, raw,
     ccheck), the committed scorer's own C gate, is called unchanged on the raw copy and the check of C given; not ok: refusal 4,
     nothing written. A C log deleted after scoring (a pass's or the smoke's) is now refused. A scored file that is missing while that
     check does not read ok (the scorer refuses with 4 and writes nothing when a C log is missing) now reads 4, not 2.
  3. Anchors with long runs (its third finding). An anchor whose run length exceeds 5.0 s (fit_m6.HEAT_TRUN_MAX) is named and left out
     of h (h1 on E172, the control h3 on E171, and the C-clean arm), as M10's heat_c1 reads a session's scale only from heat rows, which
     leave such runs out. h with them included is reported beside, never applied. v1 let them enter, unnamed. N1 tiles are unchanged:
     a tile longer than 5.0 s is named, never dropped (the registered set is N1).
  4. Committed files (its fourth finding). REGISTRATION.md sections 8 and 11 compute the readings from E171's and E172's committed files,
     after their own scoring. The reading records, per session, whether every file it read is committed and unchanged at HEAD, and
     the commit; if any is not, it records the departure beside its label.
Nothing else changes: the statistics, the sets, the seeds, the draws, the minimums, the C-gating, the precedence rule, the identity
checks and the other refusals are v1's, and v1's docstring states them (REGISTRATION.md sections 8, 9 and 11, lab 3c31a91d; A1, f49b7ddd,
changes none of them; A2, d3d97fe2, changes nothing of (c) or (d)).

  read  python3 -B read_hc1b_i8pb_v2.py read --e172-dir <E172's data dir> [--e171-dir <E171's data dir>] --json <out.json> [--md <out.md>]
        (or each file by name: --e172-scored, --e172-reduction, --e172-runs, --e172-raw, --e172-ccheck; the same for e171)

Refusals (nothing written): 9 a frozen input differs (v1's list, plus the C-session check's code: ccsessions_p8.py against
p8-600/SHA256SUMS, ccdone_q142s.py against k6/SHA256SUMS-drivers-v3, ccheck.py against its recorded sha256); 4 a C log is missing (the
scored file not scored through the C gate, no check of C beside it, or the C-session check re-run here not ok; also a missing scored file
when that check is not ok); 6 an identity check fails (v1's, and the runs table not in the form (a)-(e)); 5 an anchor list holds a check or
a zeros anchor; 2 a usage error. Python 3.9, standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P8D = os.path.join(TOP, "tools", "claims-v3", "p8-600")
M10D = os.path.join(TOP, "docs", "reports", "data", "2026-11-04-q142m-m10")
PREDD = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142p-pool8-predictor")
for _p in (P8D, M10D):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import score_p8_600 as SC  # noqa: E402  (the committed P8 scorer, a518aa11; importing it runs nothing; its sha256 is checked before use)
import score_p8_600_v2 as V2  # noqa: E402  (86d10a75; checked against SHA256SUMS-v2 before use)
import score_p8_600_v3 as V3  # noqa: E402  (e2b48f5a; checked against SHA256SUMS-v3 before use)

REG_COMMIT = "3c31a91d00f1de8354ff2da6c8862fc89600d3b9"     # M11's registration (REGISTRATION.md section 11's "this commit")
A1_COMMIT = "f49b7ddd"                                      # dated amendment A1 (no statistic, set, seed or verdict of HC1-B or I8P-B)
M11_LISTS = (("SHA256SUMS", 58), ("SHA256SUMS-m11", 6), ("SHA256SUMS-a1", 9))
RUN_CARD = {"E171": "aifoundry3", "E172": "aifoundry1c1"}
HEAT_CD = {"aifoundry3": "a3", "aifoundry1c1": "c1"}          # predict_m10's card keys
CARD_SUB = {"E171": "aifoundry3", "E172": "aifoundry1-c1"}    # the collectors' data-dir layout
CCHECK_NAMES = {"E171": ("ccheck/ccheck-all.json", "ccheck/ccheck-session.json"),
                "E172": ("ccheck/ccheck-session.json", "ccheck/ccheck-all.json")}
DRAWS = 20000
SEED_BASE = 80000
RULE_HC1B, RULE_I8PB = "M11-HC1-B", "M11-I8P-B"
# M10 REGISTRATION section 3a's random anchors (fit_m10.ANCHORS, the list heat_c1 reads); the self-test checks it equals fit_m10's
M10_ANCHORS = ("fp32.randn", "fp16.randn", "int8.full", "fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full",
               "fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp16.anchor7_randn_a", "fp16.anchor7_randn_b",
               "int8.anchor7_full_a", "int8.anchor7_full_b")
I8P_ANCHORS = ("int8.full", "int8.anchor8_full_a_4aac84", "int8.anchor8_full_b_935710")
I8P_CHECK = "int8.anchor8_check_full_d8b6c8"
E78_HEAT_ITEMS = ("fp32.randn", "fp16.randn", "int8.full")
HEAT_TRUN_MAX = 5.0   # fit_m6.HEAT_TRUN_MAX: M10's heat rows leave out longer runs; a longer N1 tile is named, never dropped
EXIT_FROZEN, EXIT_NO_C, EXIT_ID, EXIT_ANCHOR, EXIT_USAGE = 9, 4, 6, 5, 2
# v2 (note 1, change 2): the C-session check's code, each against its committed list; ccheck.py (Q139(k), unchanged since 4946a992 on
# 3 Nov 2026) against the sha256 E163's collection recorded for it (docs/reports/data/2026-11-04-e163-blind7-aifoundry3/code.sha256)
CS_LISTS = (("tools/claims-v3/p8-600/SHA256SUMS", "tools/claims-v3/p8-600/ccsessions_p8.py"),
            ("tools/claims-v3/q141k-runbook/k6/SHA256SUMS-drivers-v3", "tools/claims-v3/q141k-runbook/v3.1/ccdone_q142s.py"))
CCHECK_PY = ("tools/claims-v3/ccheck/ccheck.py", "2f806fe6080baeea33558ddd49fded16f2ebcb8c02f494217dfd32cc033c0a22")
NOTE = "tools/claims-v3/m11/README-h2-reader.md.dated-note-1.md"
sha = SC.sha
load = lambda p: json.load(open(p))  # noqa: E731
_M = {}


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, TOP) if a.startswith(TOP + os.sep) else os.path.basename(a)


def seed_of(rule):
    return SEED_BASE + sum(ord(c) for c in rule)


def rms(v):
    v = [float(x) for x in v]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v]
    return sum(v) / len(v) if v else None


def overcorrects(b0, b1):
    """the registration's words: the bias changes sign and grows in size"""
    return bool(b0 is not None and b1 is not None and b0 * b1 < 0 and abs(b1) > abs(b0))


# ------------------------------------------------------------------------------------------------- frozen inputs
def read_list(path):
    out = []
    for line in open(path):
        if line.strip():
            h, p = line.split(None, 1)
            out.append((h, p.strip().lstrip("*")))
    return out


def check_m11_lists():
    """REGISTRATION.md.dated-note-1.md A1-8: an M11 scorer checks SHA256SUMS, SHA256SUMS-m11 and SHA256SUMS-a1 before it reads anything"""
    got, bad = {}, []
    for name, n in M11_LISTS:
        lines = read_list(os.path.join(HERE, name))
        if len(lines) != n:
            bad.append(f"{name}: {len(lines)} lines, not {n}")
        for h, p in lines:
            q = os.path.join(TOP, p)
            if not os.path.isfile(q) or sha(q) != h:
                bad.append(f"{name}: {p}")
        got[name] = len(lines)
    if bad:
        raise Refuse(EXIT_FROZEN, "M11's frozen inputs differ: " + "; ".join(bad[:6]))
    return got


def frozen_code():
    """the committed scorer, v2 and v3 (each against its own list); the predictor's pin of pool8-registration.json; m10.json and
    predict_m10.py (pinned by M11's SHA256SUMS, checked first); v2 (note 1, change 2): the C-session check's three files"""
    if "P10" in _M:
        return _M
    try:
        _M["scorer"] = V2.committed_scorer_sha()
        _M["v2"] = V3.committed_v2_sha()
    except SC.Refuse as e:
        raise Refuse(EXIT_FROZEN, str(e))
    want = None
    for h, p in read_list(os.path.join(P8D, "SHA256SUMS-v3")):
        if p == "tools/claims-v3/p8-600/score_p8_600_v3.py":
            want = h
    if want is None or sha(os.path.abspath(V3.__file__)) != want:
        raise Refuse(EXIT_FROZEN, "tools/claims-v3/p8-600/score_p8_600_v3.py is not its committed file (p8-600/SHA256SUMS-v3)")
    _M["v3"] = want
    cs = SC.CS()
    loaded = {"tools/claims-v3/p8-600/ccsessions_p8.py": cs.__file__,
              "tools/claims-v3/q141k-runbook/v3.1/ccdone_q142s.py": cs._ccdone().__file__,
              CCHECK_PY[0]: cs._ccheck().__file__}
    for p, f in loaded.items():
        if os.path.abspath(f) != os.path.join(TOP, p):
            raise Refuse(EXIT_FROZEN, f"the C-session check loaded {rel(f)}, not {p}")
    _M["c_session_code"] = {}
    for lst, p in CS_LISTS:
        w = dict((q, h) for h, q in read_list(os.path.join(TOP, lst))).get(p)
        if w is None or sha(os.path.join(TOP, p)) != w:
            raise Refuse(EXIT_FROZEN, f"{p} is not its committed file ({lst})")
        _M["c_session_code"][p] = w
    if sha(os.path.join(TOP, CCHECK_PY[0])) != CCHECK_PY[1]:
        raise Refuse(EXIT_FROZEN, f"{CCHECK_PY[0]} is not the file E163's collection recorded ({CCHECK_PY[1][:12]})")
    _M["c_session_code"][CCHECK_PY[0]] = CCHECK_PY[1]
    regp = os.path.join(TOP, "tools", "claims-v3", "m10", "pool8-registration.json")
    pin = dict((p, h) for h, p in read_list(os.path.join(PREDD, "SHA256SUMS")))
    if pin.get("tools/claims-v3/m10/pool8-registration.json") != sha(regp):
        raise Refuse(EXIT_FROZEN, "tools/claims-v3/m10/pool8-registration.json is not the predictor's pinned file")
    mins = load(regp)["scoring"]["minimum_tiles"]
    _M["min"] = {"N1": int(mins["M1"]), "I1": int(mins["M1i"])}
    import predict_m10 as P10  # noqa: E402  (M10's frozen predictor, pinned by M11's SHA256SUMS; standard library only)
    _M["P10"] = P10
    _M["m10"] = P10.load_m10(os.path.join(M10D, "m10.json"))
    return _M


def law(S, T, card):
    """M10's 4.5 s window rise at measured S and run length: predict_m10.rise_4p5s with m10.json's per-card coefficients, no refit"""
    g = frozen_code()
    return g["P10"].rise_4p5s(float(S), float(T), HEAT_CD[card], g["m10"])


# ------------------------------------------------------------------------------------------------- one session's table
def run_lengths(runs_csv):
    """fit_m6.heat_rows' rule, copied: per item, the median over its runs of (the next run's prev_end_ms - its t0_ms) / 1000, consecutive
    runs within a pass, the table sorted by (pass, t0_ms); over the whole table (every pass and run reduce_e78 wrote, as fit_m6 reads it)"""
    runs = list(csv.DictReader(open(runs_csv)))
    runs.sort(key=lambda r: (r["pass"], float(r["t0_ms"] or 0)))
    dur = {}
    for a, b in zip(runs, runs[1:]):
        if a["pass"] == b["pass"]:
            try:
                dur.setdefault(a["item"], []).append((float(b["prev_end_ms"]) - float(a["t0_ms"])) / 1000)
            except (TypeError, ValueError):
                pass
    return {k: float(statistics.median(v)) for k, v in dur.items()}, runs


def _nfail(row):
    """reduce_e78 writes a run's fail column as the number of its fail reasons (0 when it passed every per-run gate)"""
    v = row.get("fail")
    if v in (None, ""):
        return 0
    return int(float(v))


def runs_table_check(res, runs, runs_csv):
    """v2 (note 1, change 1): the runs table as reduce_e78.py writes it (every run of every pass it reduced) against the reduction's own
    counts, (a)-(e) in the docstring; returns the record, or raises refusal 6 naming every check that fails"""
    bad = []
    n_runs, kept = res.get("runs"), res.get("kept")
    if not isinstance(n_runs, int) or not isinstance(kept, int):
        raise Refuse(EXIT_ID, f"the reduction is not in reduce_e78's form: 'runs' {n_runs!r} and 'kept' {kept!r} must be counts")
    try:
        nf = [_nfail(r) for r in runs]
    except ValueError:
        raise Refuse(EXIT_ID, f"{rel(runs_csv)}: a fail value reduce_e78 never writes (it writes the number of fail reasons)")
    kept_p = [str(p) for p in res.get("passes", [])]
    sa = sorted({str(x.get("pass")) for x in (res.get("passes_set_aside") or [])})
    cf = sorted({str(x.get("pass")) for x in (res.get("passes_config_flags") or [])})
    by = collections.defaultdict(list)
    for r, f in zip(runs, nf):
        by[str(r["pass"])].append(f)
    if len(runs) != n_runs:                                                                      # (a)
        bad.append(f"(a) {rel(runs_csv)} holds {len(runs)} runs where the reduction read {n_runs}")
    miss = [p for p in kept_p if p not in by]                                                     # (b)
    if miss:
        bad.append(f"(b) kept passes {miss} have no run in {rel(runs_csv)}")
    good = sum(1 for r, f in zip(runs, nf) if str(r["pass"]) in kept_p and f == 0)               # (c)
    if good != kept:
        bad.append(f"(c) the kept passes' runs without a fail number {good} where the reduction kept {kept}")
    other = sorted(p for p in by if p not in kept_p)                                              # (d)
    unexpl = [p for p in other if p not in sa and p not in cf and not all(f > 0 for f in by[p])]
    if unexpl:
        bad.append(f"(d) passes {unexpl} are in {rel(runs_csv)} but neither kept, set aside, configuration-flagged nor wholly failed")
    failed = res.get("failed")                                                                    # (e)
    fc = collections.Counter((str(r["pass"]), str(r.get("item")), str(r.get("pos") or "")) for r, f in zip(runs, nf) if f > 0)
    if failed is not None:
        fj = collections.Counter((str(x[0]), str(x[1]), "" if x[2] is None else str(x[2])) for x in failed)
        if fc != fj:
            bad.append(f"(e) the runs {rel(runs_csv)} marks failed ({sum(fc.values())}) are not the reduction's failed list "
                       f"({sum(fj.values())})")
    if bad:
        raise Refuse(EXIT_ID, "the runs table is not this reduction's (reduce_e78's form, read_hc1b_i8pb_v2 change 1): " + "; ".join(bad))
    return {"rows": len(runs), "reduction_runs": n_runs, "reduction_kept": kept, "kept_passes": kept_p,
            "kept_pass_rows_without_fail": good, "passes_set_aside": sa, "passes_config_flags": cf,
            "other_passes": {p: {"rows": len(by[p]), "why": ("set aside" if p in sa else "configuration-flagged" if p in cf
                                                             else "every run failed")} for p in other},
            "failed_runs": sum(fc.values()), "failed_list": None if failed is None else len(failed)}


def session_table(red_path, runs_csv, names):
    """per item: D, dT_win and S as the mean over the kept passes (the committed scorer's `measured`, at least 2 passes), the rate (the
    reduction's item mean, as predict_pool8.primary reads it) and the run length; plus the checks that bind the runs table to the
    reduction (v2, note 1, change 1: reduce_e78's own form)"""
    res = load(red_path)
    T, runs = run_lengths(runs_csv)
    chk = runs_table_check(res, runs, runs_csv)
    mD, _ = SC.measured(res, names, "D", 2)
    mT, _ = SC.measured(res, names, "dT_win", 2)
    mS, _ = SC.measured(res, names, "S", 2)
    items = res.get("items", {})
    out, worst = {}, {"dT_win": 0.0, "S": 0.0, "D": 0.0}
    for n in names:
        it = items.get(n) or {}
        rate = (it.get("rate") or {}).get("mean") if isinstance(it.get("rate"), dict) else None
        rec = {"D": (mD.get(n) or {}).get("mean"), "dT": (mT.get(n) or {}).get("mean"), "S": (mS.get(n) or {}).get("mean"),
               "rate": rate, "T_run": T.get(n), "n_passes": (mT.get(n) or mD.get(n) or {}).get("n")}
        for key, m in (("dT_win", mT), ("S", mS), ("D", mD)):
            v = (it.get(key) or {}).get("mean") if isinstance(it.get(key), dict) else None
            if v is not None and n in m:
                worst[key] = max(worst[key], abs(float(v) - m[n]["mean"]))
        out[n] = rec
    return out, {"kept_passes": res.get("passes", []), "runs_in_table": len(runs), "reduction_kept": res.get("kept"),
                 "runs_table": chk, "kept_pass_mean_vs_item_mean_max_abs": worst}


# ------------------------------------------------------------------------------------------------- one session's identity and C
def paths_of(run, a):
    """the session's files: each given by name, or from the data dir's layout"""
    lc = run.lower()
    d = getattr(a, f"{lc}_dir")
    f = {k: getattr(a, f"{lc}_{k}") for k in ("scored", "reduction", "runs", "raw", "ccheck")}
    if d:
        f["scored"] = f["scored"] or os.path.join(d, "scored.json")
        f["reduction"] = f["reduction"] or os.path.join(d, f"{lc}.json")
        f["runs"] = f["runs"] or os.path.join(d, "runs.csv")
        f["raw"] = f["raw"] or os.path.join(d, CARD_SUB[run])
        if not f["ccheck"]:
            for c in CCHECK_NAMES[run]:
                for q in (os.path.join(d, c), os.path.join(d, c) + ".gz"):
                    if os.path.exists(q) and not f["ccheck"]:
                        f["ccheck"] = q
    return f


def identity_one(path, run):
    """score_p8_600_v3's per-file checks, for one file: run and card, the freeze's predictions, the committed scorer, the C gate, and its
    rows its own card's (or the committed scorer's own NOT SCORED session)"""
    card = RUN_CARD[run]
    o = V2.load_json(path, "scored.json")
    fz = SC.freeze_sums()
    bad = []
    if o.get("run") != run or o.get("card") != card:
        bad.append(f"run {o.get('run')} on {o.get('card')}, not {run} on {card}")
    relp = f"tools/claims-v3/kinds/blind8/predictions-pool8-{card}.json"
    if o.get("predictions") != relp or o.get("predictions_sha256") != fz.get(relp):
        bad.append(f"predictions {o.get('predictions')} ({str(o.get('predictions_sha256'))[:12]}) are not the freeze's {relp}")
    if o.get("scorer_sha256") != frozen_code()["scorer"]:
        bad.append(f"scorer_sha256 {str(o.get('scorer_sha256'))[:12]} is not the committed scorer's")
    if not isinstance(o.get("primary"), dict) or "scale" not in o["primary"]:
        bad.append("no primary block")
    if bad:
        raise Refuse(EXIT_ID, f"{rel(path)} is not {run}'s scored session (HC1-B and I8P-B read E172 on aifoundry1c1 and E171 on "
                              f"aifoundry3 only): " + "; ".join(bad))
    if not (o.get("c_sessions") or {}).get("ok"):
        raise Refuse(EXIT_NO_C, f"{rel(path)} was not scored through the C gate (no c_sessions.ok): a session that must carry a C log "
                                f"has no finished check of C (E171.md / E172.md), so nothing is read")
    _, pred = SC.load_pred(card)
    ns, why = V3.not_scored_session(o)
    if ns is False:
        raise Refuse(EXIT_ID, f"{rel(path)}: a NOT SCORED mark in a form the committed scorer never writes ({why})")
    if ns is None:
        n, rb = V2.card_rows(o, pred)
        if n == 0 or rb:
            raise Refuse(EXIT_ID, f"{rel(path)}: its rows are not {card}'s ({n} checked; " + "; ".join(rb[:3]) + ")")
    return o, pred, (why if ns else None)


def _cs_lines_not_ok(g):
    return [ln for ln in g.get("lines", []) if not ln.startswith(("CCSESSION-OK", "STOPTEST-OK", "CCHECK-DONE"))]


def c_sessions(run, f, o=None):
    """v2 (note 1, change 2): the committed scorer's C gate, ccsessions_p8.check, called unchanged on the raw copy and the check of C
    given (no --since: the collectors call the scorer without one). Not ok: refusal 4, nothing written. Beside it, reported and never
    a refusal: whether each session it lists has the same record in the scored file's c_sessions block (a data dir renames a pass that
    is not ok to notok-<pass>, so it can list fewer sessions than the scorer did on the raw copy)"""
    if not f.get("ccheck") or not os.path.exists(f["ccheck"]):
        raise Refuse(EXIT_NO_C, f"{run}: no check of C beside the scored file ({f.get('ccheck')}): the C status cannot be read")
    g = SC.CS().check(run, f["raw"], f["ccheck"], None)
    g = json.loads(json.dumps(g).replace(TOP + os.sep, ""))
    if not g.get("ok"):
        raise Refuse(EXIT_NO_C, f"{run}: the C-session check (ccsessions_p8.check, the committed scorer's C gate, re-run on the raw copy "
                                f"given) does not read ok, so nothing is read: " + " | ".join(_cs_lines_not_ok(g)[:6]))
    rec = {"ok": True, "listed": g.get("listed"), "stoptest": g.get("stoptest"), "ccdone": (g.get("ccdone") or {}).get("finished"),
           "code": "tools/claims-v3/p8-600/ccsessions_p8.py check (unchanged), no --since"}
    if o is not None:
        at = {s.get("session"): s for s in ((o.get("c_sessions") or {}).get("sessions") or [])}
        same, differ = 0, []
        for s in g.get("sessions", []):
            t = at.get(s.get("session"))
            if t and all(t.get(k) == s.get(k) for k in ("status", "launches_in_log", "launches_judged")):
                same += 1
            else:
                differ.append(s.get("session"))
        rec.update(listed_at_scoring=len(at), same_record_as_scored=same, differ_from_scored=differ)
    return rec


def c_check(run, o, pred, f, names):
    """the C status of every item read here, by P8-KC's rule (the committed c_status), from the check of C and the session's runs; the
    P8-KC block it gives must be the scored file's (else this is not the check the session was scored with)"""
    if not f["ccheck"] or not os.path.exists(f["ccheck"]):
        raise Refuse(EXIT_NO_C, f"{run}: no check of C beside the scored file ({f['ccheck']}): the C status cannot be read, so nothing is")
    if not f["raw"] or not os.path.isdir(os.path.join(f["raw"], SC.CS().RUNS[run]["dir"])):
        raise Refuse(EXIT_NO_C, f"{run}: no session directory {SC.CS().RUNS[run]['dir']}/ under {f['raw']}: the launch records behind "
                                f"the C status are missing")
    res = load(f["reduction"])
    passes_dir = os.path.join(f["raw"], SC.CS().RUNS[run]["dir"])
    want = list(pred["tiles"])
    cstat = SC.c_status(want, res, [f["ccheck"]], passes_dir)
    kc, ok = V2.kc_of(cstat, want)
    kc_file = ((o.get("primary") or {}).get("rules") or {}).get("P8-KC") or {}
    if any(kc.get(k) != kc_file.get(k) for k in ("verdict", "c_excluded", "not_measured", "launches", "PASS")):
        raise Refuse(EXIT_ID, f"{run}: the check of C given ({rel(f['ccheck'])}) does not give the scored file's P8-KC block (recomputed "
                              f"{kc['verdict']}, {kc['launches']} launches; the file's {kc_file.get('verdict')}, {kc_file.get('launches')})")
    cx = SC.c_status(list(dict.fromkeys(list(names))), res, [f["ccheck"]], passes_dir)
    return {n: V2.status_rec(cx.get(n)) for n in names}, set(kc["c_excluded"]), kc


def first_launch_ms(raw, run):
    """the earliest t_start_ms of every launch record under the session's directories (the smoke, the passes, any copy kept beside)"""
    best, n = None, 0
    if not raw or not os.path.isdir(raw):
        return None, 0
    d = SC.CS().RUNS[run]["dir"]
    for walked, _, files in os.walk(raw):
        top = os.path.relpath(walked, raw).split(os.sep)[0]
        if top not in (d, f"{d}-smoke"):
            continue
        if "runs.jsonl" not in files:
            continue
        for line in open(os.path.join(walked, "runs.jsonl")):
            if not line.startswith("{"):
                continue
            try:
                t = json.loads(line).get("t_start_ms")
            except ValueError:
                continue
            if isinstance(t, (int, float)):
                n += 1
                best = t if best is None or t < best else best
    return best, n


def git(*args):
    try:
        r = subprocess.run(["git", "-C", TOP, *args], capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except Exception as e:  # noqa: BLE001
        return 99, f"{type(e).__name__}"


def precedence(firsts):
    """REGISTRATION.md section 11: blind only if the registration's commit precedes the first launch record of every session read"""
    rc, ct = git("show", "-s", "--format=%ct", REG_COMMIT)
    anc = git("merge-base", "--is-ancestor", REG_COMMIT, "HEAD")[0] == 0
    reg_t = int(ct) if rc == 0 and ct.isdigit() else None
    rc2, out = git("log", "--diff-filter=A", "--format=%H %ct", "--", rel(os.path.abspath(__file__)))
    mine = out.splitlines()[-1].split() if rc2 == 0 and out else None
    out = {"registration_commit": REG_COMMIT[:8], "registration_time_s": reg_t, "in_history": anc,
           "first_launch_ms": {r: v for r, v in firsts.items()}}
    known = reg_t is not None and anc and all(v is not None for v in firsts.values())
    out["blind"] = bool(known and all(reg_t * 1000 < v for v in firsts.values()))
    out["label"] = "blind" if out["blind"] else "post hoc"
    out["why"] = ("the registration precedes every first launch record" if out["blind"] else
                  ("not established (a launch record or the registration's commit not found)" if not known
                   else "a session's first launch record precedes the registration's commit"))
    if mine:
        out["reader_first_commit"] = mine[0][:8]
        out["reader_frozen_before_the_data"] = bool(all(v is not None and int(mine[1]) * 1000 < v for v in firsts.values()))
    else:
        out["reader_first_commit"] = None
        out["reader_frozen_before_the_data"] = False
    return out


def committed_state(f):
    """v2 (note 1, change 4): is every file this reading reads committed, and unchanged, at HEAD? (REGISTRATION.md sections 8 and 11
    compute the readings from E171's and E172's committed files, after their own scoring)"""
    rec, ok, last = {}, True, None
    for k in ("scored", "reduction", "runs", "ccheck", "raw"):
        p = f.get(k)
        if not p or not os.path.exists(p):
            rec[k] = {"committed": False, "why": "not given or not found"}
            ok = False
            continue
        a = os.path.abspath(p)
        if not a.startswith(TOP + os.sep):
            rec[k] = {"committed": False, "why": "outside this repository"}
            ok = False
            continue
        r = os.path.relpath(a, TOP)
        rc1, tracked = git("ls-files", "--", r)
        rc2, dirty = git("status", "--porcelain", "--untracked-files=all", "--", r)
        rc3, lg = git("log", "-1", "--format=%H %ct", "--", r)
        c = bool(rc1 == 0 and tracked and rc2 == 0 and not dirty and rc3 == 0 and lg)
        e = {"path": r, "committed": c}
        if lg and rc3 == 0:
            h, t = lg.split()[:2]
            e.update(commit=h[:8], commit_time_s=int(t))
            if last is None or int(t) > last[1]:
                last = (h[:8], int(t))
        if not c:
            e["why"] = "not tracked" if not tracked else ("changed or untracked files under it" if dirty else "no commit")
            ok = False
        rec[k] = e
    return {"all_committed": ok, "latest_commit": last[0] if (ok and last) else None, "files": rec}


# ------------------------------------------------------------------------------------------------- the two readings (pure functions)
def paired(ea, eb, sel, rule, draws=DRAWS):
    """the P8 scorer's paired form (score_p8_600.paired, E163's compare_rule), unchanged, with the registered draws and seed"""
    return SC.paired(ea, eb, sorted(sel), rule, draws=draws, seed=seed_of(rule))


def h_scale(anchors, card, names, max_trun=HEAT_TRUN_MAX):
    """h = median over the anchors of dT / law (law > 0); 1 if none (M10's rule). v2 (note 1, change 3): an anchor whose run length
    exceeds max_trun (fit_m6.HEAT_TRUN_MAX, 5.0 s) is left out, as M10's heat_c1 reads h from heat rows only; None keeps every anchor"""
    rat = {}
    for n in names:
        a = anchors.get(n)
        if not a or a.get("dT") is None or a.get("S") is None or a.get("T_run") is None:
            continue
        if max_trun is not None and float(a["T_run"]) > max_trun:
            continue
        L = law(a["S"], a["T_run"], card)
        if L > 0:
            rat[n] = a["dT"] / L
    return (statistics.median(rat.values()) if rat else 1.0), rat


def long_anchors(anchors, names, max_trun=HEAT_TRUN_MAX):
    """v2 (note 1, change 3): the anchors measured with a run length over max_trun, named"""
    return sorted(n for n in names if (anchors.get(n) or {}).get("dT") is not None and (anchors.get(n) or {}).get("S") is not None
                  and (anchors.get(n) or {}).get("T_run") is not None and float(anchors[n]["T_run"]) > max_trun)


def hc1b_core(tiles, anchors, card, anchor_names, minimum, lawP=None, checks=None, rule=RULE_HC1B, draws=DRAWS, c_clean_names=None):
    """tiles: {name: {dT, S, T_run}} (the C-gated set); anchors: {name: {dT, S, T_run}}"""
    h, ratios = h_scale(anchors, card, anchor_names)
    out = {"h": h, "anchor_ratios": ratios, "anchors_used": sorted(ratios), "card": card}
    lg = long_anchors(anchors, anchor_names)                       # v2 (note 1, change 3)
    out["anchors_long_runs_left_out"] = lg
    out["anchor_run_length_max_s"] = HEAT_TRUN_MAX
    if lg:
        hx, rx = h_scale(anchors, card, anchor_names, max_trun=None)
        out["h_with_long_anchors"] = hx
        out["long_anchor_ratios"] = {n: rx[n] for n in lg if n in rx}
        out["h_with_long_anchors_note"] = "reported beside, never applied (M10's heat_c1 reads h from heat rows, runs of 5.0 s or less)"
    if c_clean_names is not None:
        hc, rc = h_scale(anchors, card, c_clean_names)
        out["h_c_clean"] = hc
        out["c_clean_anchors"] = sorted(rc)
    sel = sorted(t for t, r in tiles.items() if r.get("dT") is not None and r.get("S") is not None and r.get("T_run") is not None)
    out["left_out_no_measure"] = sorted(t for t in tiles if t not in sel)
    out["n"] = len(sel)
    out["long_runs_named"] = sorted(t for t in sel if tiles[t]["T_run"] > HEAT_TRUN_MAX)
    if not ratios:
        why = "no random anchor measured: h = 1 (M10's rule), nothing to test"
        if lg:
            why = (f"no random anchor measured within M10's heat rows' run lengths ({len(lg)} measured over {HEAT_TRUN_MAX} s, left out): "
                   f"h = 1 (M10's rule), nothing to test")
        out.update(verdict="NOT SCORED", why=why)
        return out
    if len(sel) < minimum:
        out.update(verdict="NOT SCORED", why=f"{len(sel)} tiles, fewer than {minimum}")
        return out
    L = {t: law(tiles[t]["S"], tiles[t]["T_run"], card) for t in sel}
    e0 = {t: tiles[t]["dT"] - L[t] for t in sel}
    e1 = {t: tiles[t]["dT"] - h * L[t] for t in sel}
    p = paired(e1, e0, sel, rule, draws)
    out.update(verdict=p["verdict"], d_rms_c=p["d_rms"], lo95=p["lo95"], hi95=p["hi95"], draws=p["draws"], seed=p["seed"],
               rms_without_c=rms(e0.values()), rms_with_c=rms(e1.values()),
               bias_without_c=mean(e0.values()), bias_with_c=mean(e1.values()))
    out["overcorrects"] = overcorrects(out["bias_without_c"], out["bias_with_c"])
    by = {}
    for t in sel:
        by.setdefault(t.split(".")[0], []).append(t)
    out["by_format"] = {f: {"n": len(v), "rms_without_c": rms([e0[t] for t in v]), "rms_with_c": rms([e1[t] for t in v])}
                        for f, v in sorted(by.items())}
    out["tiles"] = {t: {"dT_c": tiles[t]["dT"], "S_w": tiles[t]["S"], "T_run_s": tiles[t]["T_run"], "law_c": L[t],
                        "e_without_c": e0[t], "e_with_c": e1[t]} for t in sel}
    if lawP:
        sp = [t for t in sel if lawP.get(t) is not None]
        f0 = {t: tiles[t]["dT"] - lawP[t] for t in sp}
        f1 = {t: tiles[t]["dT"] - h * lawP[t] for t in sp}
        if len(sp) >= minimum:
            q = paired(f1, f0, sp, rule, draws)
            out["at_M10_primary_D"] = {"reading": q["verdict"], "d_rms_c": q["d_rms"], "lo95": q["lo95"], "hi95": q["hi95"], "n": len(sp),
                                       "rms_without_c": rms(f0.values()), "rms_with_c": rms(f1.values()),
                                       "note": "reported beside, never a verdict: the law at M10's primary D (the scorer's M10_heat_c)"}
        else:
            out["at_M10_primary_D"] = {"reading": "NOT SCORED", "n": len(sp)}
    if checks is not None:
        ch = {}
        for n, a in checks.items():
            if a and a.get("dT") is not None and a.get("S") is not None and a.get("T_run") is not None:
                Ln = law(a["S"], a["T_run"], card)
                ch[n] = {"e_without_c": a["dT"] - Ln, "e_with_c": a["dT"] - h * Ln, "smaller_with": abs(a["dT"] - h * Ln) < abs(a["dT"] - Ln)}
        out["check_anchors"] = ch
    return out


def i8p_k(anch_s, anch_r, names):
    """k = median over the anchors measured in both sessions of [D_s / Dhat_s] / [D_r / Dhat_r]; None if no anchor"""
    q = {}
    for n in names:
        a, b = anch_s.get(n), anch_r.get(n)
        if not a or not b or None in (a.get("D"), a.get("Dhat"), b.get("D"), b.get("Dhat")):
            continue
        if a["Dhat"] > 0 and b["Dhat"] > 0 and b["D"] != 0:
            q[n] = (a["D"] / a["Dhat"]) / (b["D"] / b["Dhat"])
    return (statistics.median(q.values()) if q else None), q


def i8pb_core(anch_s, anch_r, tiles, names, minimum, check=None, rule=RULE_I8PB, draws=DRAWS):
    """anch_*: {name: {D, Dhat}} (C-clean in both sessions); tiles: {name: {D, M10, M10_95}} (I1, C-gated)"""
    k, q = i8p_k(anch_s, anch_r, names)
    out = {"k": k, "anchor_ratios": q, "anchors_used": sorted(q)}
    sel = sorted(t for t, r in tiles.items() if r.get("D") is not None and r.get("M10") is not None)
    out["n"] = len(sel)
    if k is None:
        out.update(verdict="NOT SCORED", why="no int8 random anchor measured and C all PASS in both sessions: k cannot be read")
        return out
    if len(sel) < minimum:
        out.update(verdict="NOT SCORED", why=f"{len(sel)} tiles, fewer than {minimum}")
        return out
    e0 = {t: tiles[t]["D"] - tiles[t]["M10"] for t in sel}
    e1 = {t: tiles[t]["D"] - k * tiles[t]["M10"] for t in sel}
    p = paired(e1, e0, sel, rule, draws)
    out.update(verdict=p["verdict"], d_rms_w=p["d_rms"], lo95=p["lo95"], hi95=p["hi95"], draws=p["draws"], seed=p["seed"],
               rms_without_w=rms(e0.values()), rms_with_w=rms(e1.values()),
               bias_without_w=mean(e0.values()), bias_with_w=mean(e1.values()))
    out["I1_bias_overcorrects"] = overcorrects(out["bias_without_w"], out["bias_with_w"])
    out["tiles"] = {t: {"D_w": tiles[t]["D"], "M10_w": tiles[t]["M10"], "e_without_w": e0[t], "e_with_w": e1[t]} for t in sel}
    if check is not None:
        if check.get("D") is not None and check.get("M10") is not None:
            lo, hi = check.get("M10_95") or (None, None)
            hw = 0.5 * (hi - lo) if lo is not None else None
            ew, e = check["D"] - k * check["M10"], check["D"] - check["M10"]
            inside = (abs(ew) <= hw) if hw is not None else None
            out["check_anchor"] = {"abs_e_without_w": abs(e), "abs_e_with_w": abs(ew), "inside_M10_band_with": inside,
                                   "better": bool(abs(ew) < abs(e) and inside), "band_half_width_w": hw,
                                   "rule": "better if |e| is smaller with k and the measured D lies inside M10's int8 95% band about k x M10"}
        else:
            out["check_anchor"] = {"why": "not measured or not C all PASS"}
    return out


# ------------------------------------------------------------------------------------------------- the sessions
def load_session(run, f, o, pred, mark, cs):
    roles = pred.get("roles") or {}
    scale6 = sorted(n for n, r in roles.items() if (r or {}).get("role") == "scale")
    checks = sorted(n for n, r in roles.items() if (r or {}).get("role") == "check")
    zeros = set(pred["sets"]["zeros_anchors"]) | {n for n, r in roles.items() if (r or {}).get("role") == "zeros"}
    heat_anchors = [n for n in M10_ANCHORS] + scale6
    bad = [n for n in heat_anchors if n in zeros or n in checks or n in pred["sets"]["KA"]]
    bad += [n for n in I8P_ANCHORS if n in zeros or n in checks or n in pred["sets"]["KA"] or n == I8P_CHECK]
    if len(scale6) != 6 or bad:
        raise Refuse(EXIT_ANCHOR, f"{run}: an anchor list holds a check or a zeros anchor, or pool 8's scale anchors are not six "
                                  f"({len(scale6)}; {bad}): 'never a check anchor or a zeros anchor' (REGISTRATION.md sections 8-9)")
    if sha(f["reduction"]) != (o.get("primary") or {}).get("reduction_sha256"):
        raise Refuse(EXIT_ID, f"{run}: {rel(f['reduction'])} is not the reduction the scored file was scored on (reduction_sha256)")
    names = sorted(set(pred["tiles"]) | set(heat_anchors) | set(E78_HEAT_ITEMS))
    tab, tchk = session_table(f["reduction"], f["runs"], names)
    cst, cexcl, kc = c_check(run, o, pred, f, names)
    first, nrec = first_launch_ms(f["raw"], run)
    rows = (o.get("primary") or {}).get("rows") or {}
    # the scorer's dT_w and D_w are the same `measured` over the same reduction: identical, or the table is not this session's
    worst = 0.0
    for t, r in rows.items():
        for k_, kk in (("dT_w", "dT"), ("D_w", "D")):
            if r.get(k_) is not None and tab.get(t, {}).get(kk) is not None:
                worst = max(worst, abs(float(r[k_]) - float(tab[t][kk])))
    if worst > 1e-12:
        raise Refuse(EXIT_ID, f"{run}: the reduction's kept-pass means differ from the scored file's rows by {worst:.3g}")
    return {"run": run, "card": RUN_CARD[run], "o": o, "pred": pred, "tab": tab, "tab_checks": tchk, "c": cst, "c_excluded": cexcl,
            "kc": kc, "first_launch_ms": first, "launch_records": nrec, "not_scored": mark, "rows": rows, "scale6": scale6,
            "checks": checks, "heat_anchors": heat_anchors, "c_sessions": cs, "committed": committed_state(f),
            "files": {k: (rel(v) if v else None) for k, v in f.items()},
            "sha256": {k: (sha(v) if v and os.path.isfile(v) else None) for k, v in f.items()}}


def hc1b_of(s, rule=RULE_HC1B):
    """HC1-B on a card-1 session (or, with the aifoundry3 law, the control h3 on E171)"""
    g = frozen_code()
    if s["not_scored"]:
        return {"verdict": "NOT SCORED", "why": s["not_scored"] + " (the registrations' rule: every rule NOT SCORED)"}
    pred, tab = s["pred"], s["tab"]
    n1 = [t for t in pred["sets"]["N1"] if t not in s["c_excluded"]]
    tiles = {t: {"dT": tab[t]["dT"], "S": tab[t]["S"], "T_run": tab[t]["T_run"]} for t in n1}
    anchors = {n: tab[n] for n in s["heat_anchors"] if n in tab}
    present = [n for n in s["heat_anchors"] if tab.get(n, {}).get("dT") is not None]
    clean = [n for n in present if (s["c"].get(n) or {}).get("all_pass")]
    lawP = {t: s["rows"][t].get("M10_heat_c") for t in n1 if t in s["rows"]}
    checks = {n: tab.get(n) for n in s["checks"] if n not in s["c_excluded"]}
    out = hc1b_core(tiles, anchors, s["card"], s["heat_anchors"], g["min"]["N1"], lawP=lawP, checks=checks, rule=rule, c_clean_names=clean)
    out["set"] = {"N1": len(pred["sets"]["N1"]), "c_excluded": sorted(set(pred["sets"]["N1"]) & s["c_excluded"]), "minimum": g["min"]["N1"]}
    out["anchors_C"] = {n: {"all_pass": (s["c"].get(n) or {}).get("all_pass"), "launches": (s["c"].get(n) or {}).get("launches")}
                        for n in present}
    out["anchors_not_C_clean"] = sorted(set(present) - set(clean))
    return out


def i8pb_of(s1, s3):
    g = frozen_code()
    for s in (s1, s3):
        if s["not_scored"]:
            return {"verdict": "NOT SCORED", "why": f"{s['run']}: " + s["not_scored"] + " (the registrations' rule: every rule NOT SCORED)"}
    anch = {}
    named = {}
    for s in (s1, s3):
        pred, tab = s["pred"], s["tab"]
        d = {}
        for n in I8P_ANCHORS:
            k1 = (pred["m10_anchors"].get(n) or {}).get("k_J_per_op") if n in pred["m10_anchors"] else pred["tiles"][n]["M10"]["k_J_per_op"]
            r = tab.get(n) or {}
            c_ok = bool((s["c"].get(n) or {}).get("all_pass"))
            named[f"{s['run']}:{n}"] = {"D_w": r.get("D"), "rate_per_s": r.get("rate"), "C_all_pass": c_ok,
                                        "Dhat_w": (r["rate"] * k1) if r.get("rate") is not None and k1 is not None else None}
            if c_ok and r.get("D") is not None and r.get("rate") is not None and k1 is not None:
                d[n] = {"D": r["D"], "Dhat": r["rate"] * k1}
        anch[s["run"]] = d
    pred1, rows1 = s1["pred"], s1["rows"]
    i1 = [t for t in pred1["sets"]["I1"] if t not in s1["c_excluded"]]
    tiles = {t: {"D": (rows1.get(t) or {}).get("D_w"), "M10": (rows1.get(t) or {}).get("M10_primary_w"),
                 "M10_95": (rows1.get(t) or {}).get("M10_primary_95")} for t in i1}
    chk = None
    if I8P_CHECK not in s1["c_excluded"] and I8P_CHECK in rows1:
        r = rows1[I8P_CHECK]
        chk = {"D": r.get("D_w"), "M10": r.get("M10_primary_w"), "M10_95": r.get("M10_primary_95")}
    out = i8pb_core(anch["E172"], anch["E171"], tiles, I8P_ANCHORS, g["min"]["I1"], check=chk if chk is not None else {})
    out["anchors"] = named
    out["anchors_left_out"] = sorted(n for n in I8P_ANCHORS if n not in out.get("anchor_ratios", {}))
    out["set"] = {"I1": len(pred1["sets"]["I1"]), "c_excluded": sorted(set(pred1["sets"]["I1"]) & s1["c_excluded"]), "minimum": g["min"]["I1"]}
    out["card_term_card1"] = pred1["tiles"][I8P_ANCHORS[1]]["M10"]["card_term"]
    return out


def departure_of(sessions):
    """v2 (note 1, change 4): the departure, if any file read is not committed and unchanged at HEAD"""
    off = {s["run"]: sorted(k for k, v in s["committed"]["files"].items() if not v.get("committed")) for s in sessions}
    off = {r: v for r, v in off.items() if v}
    if not off:
        return None
    return ("read from files not committed and unchanged at HEAD (" + "; ".join(f"{r}: {', '.join(v)}" for r, v in sorted(off.items()))
            + "): REGISTRATION.md sections 8 and 11 compute these readings from E171's and E172's committed files, after their own "
              "scoring, so this reading departs from that")


def read(a):
    lists = check_m11_lists()
    g = frozen_code()
    f2 = paths_of("E172", a)
    f1 = paths_of("E171", a) if (a.e171_dir or a.e171_scored) else None
    for run, f in (("E172", f2), ("E171", f1)):
        if f is None:
            continue
        miss = [k for k in ("scored", "reduction", "runs", "raw") if not f.get(k) or not os.path.exists(f[k])]
        if miss:
            # v2 (note 1, change 2): the scorer writes no scored file when a session's C log is missing (its exit 4); that reads 4
            if miss == ["scored"] and os.path.isdir(f["raw"]):
                if not f.get("ccheck") or not os.path.exists(f["ccheck"]):
                    raise Refuse(EXIT_NO_C, f"{run}: no scored file and no check of C beside it ({f.get('ccheck')}): the scorer writes "
                                            f"nothing when a session that must carry a C log has no finished check")
                cg = SC.CS().check(run, f["raw"], f["ccheck"], None)
                if not cg.get("ok"):
                    raise Refuse(EXIT_NO_C, f"{run}: no scored file, and the C-session check (ccsessions_p8.check, re-run on the raw copy "
                                            f"given) does not read ok, so the scorer refused (its exit 4): "
                                            + " | ".join(_cs_lines_not_ok(json.loads(json.dumps(cg).replace(TOP + os.sep, "")))[:6]))
            raise Refuse(EXIT_USAGE, f"{run}: missing {', '.join(miss)} ({', '.join(str(f.get(k)) for k in miss)})")
    # a C log missing comes first (the registrations: the scorer refuses with 4 before it reads anything else)
    for run, f in (("E172", f2), ("E171", f1)):
        if f is None:
            continue
        o = V2.load_json(f["scored"], "scored.json")
        if not (o.get("c_sessions") or {}).get("ok"):
            raise Refuse(EXIT_NO_C, f"{run}: {rel(f['scored'])} was not scored through the C gate (no c_sessions.ok): a session that must "
                                    f"carry a C log has no finished check of C (E171.md / E172.md), so nothing is read")
        if not f["ccheck"] or not os.path.exists(f["ccheck"]):
            raise Refuse(EXIT_NO_C, f"{run}: no check of C beside the scored file ({f['ccheck']}): the C status cannot be read")
    pair = None
    if f1 is not None:
        try:
            objs, info, dchk = V3.pair_check([f1["scored"], f2["scored"]])
        except SC.Refuse as e:
            raise Refuse(e.code, str(e))
        pair = {"checks": "score_p8_600_v3.pair_check (1)-(7), unchanged", "pair": info, "measured_D": dchk}
    o2, pred2, m2 = identity_one(f2["scored"], "E172")
    o1 = pred1 = m1 = None
    if f1 is not None:
        o1, pred1, m1 = identity_one(f1["scored"], "E171")
    # v2 (note 1, change 2): the committed scorer's C gate re-run on the raw copies given, before any table is read
    cs2 = c_sessions("E172", f2, o2)
    cs1 = c_sessions("E171", f1, o1) if f1 is not None else None
    s2 = load_session("E172", f2, o2, pred2, m2, cs2)
    s1 = load_session("E171", f1, o1, pred1, m1, cs1) if f1 is not None else None
    sess = [s for s in (s2, s1) if s]
    dep = departure_of(sess)
    out = {"_note": "Q142(h2) fix pass read_hc1b_i8pb_v2.py: M11's HC1-B and I8P-B, the readings REGISTRATION.md sections 8, 9 and 11 "
                    "register (3c31a91d, amended by A1 f49b7ddd, which changes neither), read by v1's code with the four changes of "
                    "README-h2-reader.md.dated-note-1.md", "reader": "tools/claims-v3/m11/read_hc1b_i8pb_v2.py", "dated_note": NOTE,
           "reader_sha256": sha(os.path.abspath(__file__)),
           "m11_lists": lists, "scorer_sha256": g["scorer"], "v2_sha256": g["v2"], "v3_sha256": g["v3"],
           "c_session_code_sha256": g["c_session_code"],
           "m10_json_sha256": sha(os.path.join(M10D, "m10.json")), "minimum_tiles": g["min"], "draws": DRAWS,
           "seeds": {RULE_HC1B: seed_of(RULE_HC1B), RULE_I8PB: seed_of(RULE_I8PB)}, "pair_identity": pair,
           "committed_files": {s["run"]: s["committed"] for s in sess}, "departure": dep}
    out["sessions"] = {s["run"]: {"files": s["files"], "sha256": s["sha256"], "kept_passes": s["tab_checks"]["kept_passes"],
                                  "table_checks": s["tab_checks"], "P8-KC": {k: s["kc"].get(k) for k in ("verdict", "launches", "PASS", "c_excluded")},
                                  "c_sessions_rerun": s["c_sessions"], "first_launch_ms": s["first_launch_ms"],
                                  "launch_records": s["launch_records"], "not_scored": s["not_scored"]} for s in sess}
    h = hc1b_of(s2)
    prec_h = precedence({"E172": s2["first_launch_ms"]})
    h["label"] = prec_h["label"]
    h["precedence"] = prec_h
    h["departure"] = departure_of([s2])
    if h.get("verdict") in ("BETTER", "WORSE", "NOT RESOLVED"):
        h["not_wanted"] = {"HC1-B reads WORSE": h["verdict"] == "WORSE", "h1 over-corrects on E172's N1": h["overcorrects"]}
        h["not_wanted"]["met"] = any(h["not_wanted"].values())
    if s1 is not None:
        c3 = hc1b_of(s1)
        h["control_h3_E171"] = {"h3": c3.get("h"), "anchor_ratios": c3.get("anchor_ratios"), "applied": False,
                                "anchors_long_runs_left_out": c3.get("anchors_long_runs_left_out"),
                                "would_read": c3.get("verdict"), "d_rms_c": c3.get("d_rms_c"), "lo95": c3.get("lo95"), "hi95": c3.get("hi95"),
                                "note": "a control, computed the same way on aifoundry3 and not applied (REGISTRATION.md section 8)"}
    else:
        h["control_h3_E171"] = {"why": "E171 not given"}
    out["HC1-B"] = h
    if s1 is None:
        out["I8P-B"] = {"verdict": "NOT SCORED", "why": "E171 not given: I8P-B pairs E172 with E171", "label": "post hoc"}
    else:
        i = i8pb_of(s2, s1)
        prec_i = precedence({"E172": s2["first_launch_ms"], "E171": s1["first_launch_ms"]})
        i["label"] = prec_i["label"]
        i["precedence"] = prec_i
        i["departure"] = dep
        if i.get("verdict") in ("BETTER", "WORSE", "NOT RESOLVED"):
            i["not_wanted"] = {"I8P-B reads WORSE": i["verdict"] == "WORSE"}
        out["I8P-B"] = i
    return out


def markdown(o):
    h, i = o["HC1-B"], o["I8P-B"]
    L = ["# M11's HC1-B and I8P-B (read_hc1b_i8pb_v2.py)", "",
         f"Reader `{o['reader_sha256'][:12]}` (v2, {o['dated_note']}); M11's lists {o['m11_lists']}; seeds {o['seeds']}; {o['draws']} draws.",
         "", "| reading | label | verdict | d | 95% interval | n | scale |", "|---|---|---|---:|---|---:|---:|"]
    for nm, r, unit, sk in (("HC1-B", h, "c", "h"), ("I8P-B", i, "w", "k")):
        d = r.get(f"d_rms_{unit}")
        ds = f"{d:+.4f}" if isinstance(d, float) else ""
        iv = f"[{r['lo95']:+.4f}, {r['hi95']:+.4f}]" if isinstance(r.get("lo95"), float) else ""
        sc = r.get(sk)
        scs = f"{sc:.5f}" if isinstance(sc, float) else ("" if sc is None else str(sc))
        L.append(f"| {nm} | {r.get('label')} | {r.get('verdict')} | {ds} | {iv} | {r.get('n', '')} | {scs} |")
    for nm, r in (("HC1-B", h), ("I8P-B", i)):
        if r.get("why"):
            L.append(f"\n{nm}: {r['why']}")
    if h.get("anchors_long_runs_left_out"):
        L.append(f"\nAnchors over {HEAT_TRUN_MAX} s, left out of h1: {h['anchors_long_runs_left_out']}; h1 with them "
                 f"{h.get('h_with_long_anchors')} (reported beside, never applied).")
    if h.get("not_wanted"):
        L.append(f"\nHC1's not-wanted clauses on E172: {h['not_wanted']}")
    if i.get("not_wanted"):
        L.append(f"\nI8P's not-wanted clause on E172: {i['not_wanted']}")
    L.append(f"\nPrecedence: HC1-B {h.get('precedence', {}).get('why')}; I8P-B {(i.get('precedence') or {}).get('why')}.")
    cf = o.get("committed_files") or {}
    L.append("\nFiles read: " + "; ".join(f"{r} {'committed at ' + str(v.get('latest_commit')) if v.get('all_committed') else 'NOT all committed'}"
                                          for r, v in sorted(cf.items())) + ".")
    if o.get("departure"):
        L.append(f"\nDEPARTURE: {o['departure']}.")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    for run in ("e172", "e171"):
        r.add_argument(f"--{run}-dir")
        for k in ("scored", "reduction", "runs", "raw", "ccheck"):
            r.add_argument(f"--{run}-{k}")
    r.add_argument("--json", required=True)
    r.add_argument("--md")
    a = ap.parse_args(argv)
    if not (a.e172_dir or a.e172_scored):
        print("REFUSED (exit 2): give --e172-dir (or E172's files by name)")
        return EXIT_USAGE
    try:
        o = read(a)
    except Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code
    except SC.Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code
    txt = json.dumps(o, indent=1, sort_keys=True, default=str).replace(TOP + os.sep, "")
    open(a.json, "w").write(txt + "\n")
    if a.md:
        open(a.md, "w").write(markdown(o))
    print(json.dumps({"HC1-B": [o["HC1-B"].get("verdict"), o["HC1-B"].get("label")],
                      "I8P-B": [o["I8P-B"].get("verdict"), o["I8P-B"].get("label")],
                      "files": "committed" if not o.get("departure") else "DEPARTURE: not all committed"}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
