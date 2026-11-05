#!/usr/bin/env python3
"""Q142(k6): did every session that must carry a C log carry one, checked to its end? (E171.md and E172.md, "The sessions that must carry
a C log"; the Q142 critic's fault 3: v3.1's gate read each check of C that ran, never each session that had to carry one.)

THE LIST, by the registered rule, from the raw copy of the run's directories (never chosen after the fact):
  - <run>-smoke/p<NN01>, the smoke (E171: p17101; E172: p17201);
  - every pass directory <run>/p<prefix><NN> (E171: 17110-17129; E172: 17210-17219), never an .attempt-* copy, whose runs.jsonl holds a
    launch record (a JSON line with an "item" and a "launch" field), whatever its block status.
  The stop-path test <run>-stoptest/p<NN02> runs no launch: it must hold no launch record and no C record.
FOR EACH LISTED SESSION:
  1. its c-log.jsonl (or .jsonl.gz) is there, non-empty, and holds a host record ({"ccheck":1, "kind":"host"});
  2. the check's --out file finished: v3.1's ccdone_q142s.read_one (tools/claims-v3/q141k-runbook/v3.1/ccdone_q142s.py, imported
     unchanged): there, ccheck.py's summary, as many launches listed as it counts, at least one, written since --since;
  3. the check judged exactly as many launches from this session's log (the --out file's "log" field, which the collectors set to
     c-log-<session dir name>.jsonl) as ccheck.py's own reader (ccheck.load_clog, imported unchanged) finds in it, at least one.
A genuine C FAIL is a finished check: it is not a stop here; it reaches P8-KC, as registered.

    python3 -B tools/claims-v3/p8-600/ccsessions_p8.py --run E171|E172 --raw <raw copy> --ccheck <ccheck --out json> [--since <epoch s>]
        [--json <out>]

It prints one line per session (CCSESSION-OK, -MISSING, -NOHOST, -UNFINISHED, -UNCHECKED, -SHORT) and for the stop-path test
(STOPTEST-OK, STOPTEST-LAUNCHED), then "ccsessions: k of n listed sessions checked to the end: FINISHED | NOT FINISHED". Exit 0 when
every listed session is CCSESSION-OK and the stop-path test is clean, 4 when not, 2 on a usage error. It reads and never writes (except
--json). check(...) is what score_p8_600.py calls. Standard library only (ccheck.py's reader is too). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUNS = {"E171": {"dir": "e171", "smoke": "p17101", "stoptest": "p17102", "passes": re.compile(r"^p171[12][0-9]$")},
        "E172": {"dir": "e172", "smoke": "p17201", "stoptest": "p17202", "passes": re.compile(r"^p1721[0-9]$")},
        # the parents' committed layouts, for the self-test only (E163's kinds passes and E151 blocks; E164's passes)
        "E163": {"dir": "e163", "smoke": "p16301", "stoptest": "p16302", "passes": re.compile(r"^p163[0-9][0-9]$")},
        "E164": {"dir": "e164", "smoke": "p16401", "stoptest": "p16402", "passes": re.compile(r"^p164[0-9][0-9]$")}}
_M = {}


def _ccdone():
    if "d" not in _M:
        p = os.path.join(TOP, "tools", "claims-v3", "q141k-runbook", "v3.1")
        if p not in sys.path:
            sys.path.insert(0, p)
        import ccdone_q142s as d  # noqa: E402  (v3.1's, unchanged)
        _M["d"] = d
    return _M["d"]


def _ccheck():
    if "c" not in _M:
        p = os.path.join(TOP, "tools", "claims-v3", "ccheck")
        if p not in sys.path:
            sys.path.insert(0, p)
        import ccheck as c  # noqa: E402  (Q139(k)'s, unchanged; only its reader is called)
        _M["c"] = c
    return _M["c"]


def _lines(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    yield json.loads(line)
                except ValueError:
                    continue


def has_launch(runs_jsonl):
    if not os.path.exists(runs_jsonl):
        return False
    return any(isinstance(r, dict) and "item" in r and "launch" in r for r in _lines(runs_jsonl))


def clog_of(d):
    for nm in ("c-log.jsonl", "c-log.jsonl.gz"):
        p = os.path.join(d, nm)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None


def listed_sessions(run, raw):
    """the registered list: the smoke, then every pass with a launch record, sorted by name"""
    R = RUNS[run]
    out = [os.path.join(raw, f"{R['dir']}-smoke", R["smoke"])]
    pd = os.path.join(raw, R["dir"])
    if os.path.isdir(pd):
        for nm in sorted(os.listdir(pd)):
            if ".attempt-" in nm or not R["passes"].match(nm):
                continue
            d = os.path.join(pd, nm)
            if os.path.isdir(d) and has_launch(os.path.join(d, "runs.jsonl")):
                out.append(d)
    return out


def n_launches_in_log(path):
    """ccheck.py's own reader over one log: the number of launches the check reads from it (broken records included)"""
    C = _ccheck()
    if path.endswith(".gz"):
        tmp = tempfile.mkdtemp(prefix="ccsessions-")
        try:
            plain = os.path.join(tmp, os.path.basename(path)[:-3])
            with gzip.open(path, "rb") as a, open(plain, "wb") as b:
                shutil.copyfileobj(a, b)
            return len(C.load_clog([plain]))
        finally:
            shutil.rmtree(tmp)
    return len(C.load_clog([path]))


def check(run, raw, ccheck_out, since=None):
    """the reading: {"sessions": [...], "stoptest": ..., "ccdone": ..., "ok": bool, "lines": [...]}"""
    R = RUNS[run]
    lines, res = [], {"run": run, "sessions": []}
    done, why = _ccdone().read_one(ccheck_out, since)
    res["ccdone"] = {"finished": bool(done), "line": why}
    lines.append(why)
    judged = {}
    if done:
        p = ccheck_out if os.path.exists(ccheck_out) else ccheck_out + ".gz"
        op = gzip.open if p.endswith(".gz") else open
        with op(p, "rt") as f:
            for v in json.load(f).get("launches", []):
                judged[v.get("log")] = judged.get(v.get("log"), 0) + 1
    ok_all = bool(done)
    sess = listed_sessions(run, raw)
    for d in sess:
        name = os.path.relpath(d, raw)
        rec = {"session": name, "log_name": f"c-log-{os.path.basename(d)}.jsonl"}
        cl = clog_of(d)
        if not os.path.isdir(d):
            rec["status"], msg = "MISSING", f"CCSESSION-MISSING {name}: the session's directory is not in the raw copy"
        elif cl is None:
            rec["status"], msg = "MISSING", f"CCSESSION-MISSING {name}: no C log (c-log.jsonl), though the session must carry one"
        elif not any(r.get("ccheck") == 1 and r.get("kind") == "host" for r in _lines(cl)):
            rec["status"], msg = "NOHOST", f"CCSESSION-NOHOST {name}: its C log holds no host record (the wrapper did not run)"
        elif not done:
            rec["status"], msg = "UNFINISHED", f"CCSESSION-UNFINISHED {name}: the check of C did not finish ({why.split(':')[0]})"
        else:
            n_log = n_launches_in_log(cl)
            n_j = judged.get(rec["log_name"], 0)
            rec.update(c_log=os.path.relpath(cl, raw), launches_in_log=n_log, launches_judged=n_j)
            if n_j == 0:
                rec["status"], msg = "UNCHECKED", f"CCSESSION-UNCHECKED {name}: the check judged no launch from {rec['log_name']}"
            elif n_j != n_log or n_log < 1:
                rec["status"], msg = "SHORT", f"CCSESSION-SHORT {name}: the check judged {n_j} launches of the {n_log} its log holds"
            else:
                rec["status"], msg = "OK", f"CCSESSION-OK {name}: {n_log} launches in its C log, {n_j} judged"
        ok_all = ok_all and rec["status"] == "OK"
        res["sessions"].append(rec)
        lines.append(msg)
    st = os.path.join(raw, f"{R['dir']}-stoptest", R["stoptest"])
    st_runs = has_launch(os.path.join(st, "runs.jsonl"))
    st_cl = clog_of(st)
    st_c = sum(1 for r in _lines(st_cl) if r.get("ccheck") == 1 and r.get("kind") == "c") if st_cl else 0
    if st_runs or st_c:
        res["stoptest"] = "LAUNCHED"
        lines.append(f"STOPTEST-LAUNCHED {os.path.relpath(st, raw)}: {int(st_runs)} launch file(s) with records and {st_c} C records (want none)")
        ok_all = False
    else:
        res["stoptest"] = "OK"
        lines.append(f"STOPTEST-OK {os.path.relpath(st, raw)}: no launch record and no C record")
    k = sum(1 for s in res["sessions"] if s["status"] == "OK")
    res["listed"] = len(res["sessions"])
    res["ok"] = bool(ok_all and res["listed"] >= 1)
    lines.append(f"ccsessions: {k} of {res['listed']} listed sessions checked to the end: {'FINISHED' if res['ok'] else 'NOT FINISHED'}")
    res["lines"] = lines
    return res


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, choices=sorted(RUNS))
    ap.add_argument("--raw", required=True)
    ap.add_argument("--ccheck", required=True)
    ap.add_argument("--since", type=float)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.raw):
        print(f"usage: --raw {a.raw} is not a directory")
        return 2
    res = check(a.run, a.raw, a.ccheck, a.since)
    for ln in res["lines"]:
        print(ln)
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1)
    return 0 if res["ok"] else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
