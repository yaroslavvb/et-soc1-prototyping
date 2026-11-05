#!/usr/bin/env python3
"""Q143(k)'s fix pass, Thu 5 Nov 2026: E176's passes that must carry a C log, and the check of C read against the launches their marks
record. Step 22 v2 (s22_collect_q143k_v2.sh) runs it after v3.1's ccdone_q142s.py, before it says "collected and scored".

Why it is needed (the verifier of Q143(k), its fault 2). collect_e176.sh (lab 03582d2f) skips a pass whose c-log.jsonl is empty or
missing, and checks the rest; ccdone_q142s.py reads only whether the check's --out file finished. So with the smoke's C log there and the
measured pass p17620's missing, the check read the smoke's 48 launches alone, ccdone passed, the scorer read rc 0, and step 22 printed
"E176 collected and scored". Its C rule was never applied to a measured hold.

The rules (E176's kit: the session runs the smoke p17601, then the measured pass p17620; run_e176.py writes one launch mark per host
process, with records = the C records it logged, and the C log holds one "c" line per record):
  1. p17620 is required. Its marks.jsonl must be there and show at least one launch (else MISSING-MARKS, or NO-LAUNCH: no hold ran, so
     nothing is scored), and its C log must have been collected (ccheck/c-log-p17620.jsonl or .gz, not empty; else MISSING-CLOG).
  2. p17601's marks.jsonl must be there: the session runs the smoke before the measured pass, so a measured pass without it is a lost
     record (MISSING-MARKS). p17601 is required when its marks show a launch; then its C log must have been collected (MISSING-CLOG).
     With no launch it is NOT-REQUIRED (reported).
  3. For each required pass, the check's rows for its log (ccheck-all.json's launches whose "log" is c-log-<pass>.jsonl) must match the
     marks one for one: every launch mark carries an integer "records" (else COUNT-UNREAD); the rows whose t_start_ms falls inside a mark's
     [t_start_ms, t_end_ms] number exactly its records; and no row falls outside every mark's window. Else COUNT-SHORT or COUNT-OVER
     (with the processes that differ) or ORPHAN. A match prints COUNT-OK.
  4. A row whose log is neither pass's is UNKNOWN-LOG: the collector checks only these two logs.
A C FAIL in a matched row is not stopped here: it reaches the registered C rule (CHECK-DONE prints the counts).

On E166's committed session (4 Nov 2026) the rule reads 493 processes and 6,644 launches for the measured pass and 6 and 48 for the smoke,
every process's records equal to its rows; on E154's (3 Nov) 474 and 6,288, 7 and 58 (the desk test, U1 and U2).

    python3 -B tools/claims-v3/q143k-runbook/cclaunch_q143k.py <E176's data dir>

Exit 0 when every rule holds; 4 when any does not; 2 on a usage error. Standard library only; it reads, and writes nothing. It prints
paths relative to the data directory. SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
SMOKE = ("p17601", os.path.join("aifoundry3", "e176-smoke", "p17601"))
MEASURED = ("p17620", os.path.join("aifoundry3", "e176", "p17620"))


def _open(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def first_there(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def launch_marks(d, rel):
    """the pass's launch marks, or (None, why)"""
    p = os.path.join(d, rel, "marks.jsonl")
    if not os.path.exists(p):
        return None, f"no {rel}/marks.jsonl"
    out = []
    try:
        with open(p) as f:
            for x in f:
                if x.strip():
                    m = json.loads(x)
                    if m.get("kind") == "launch":
                        out.append(m)
    except (OSError, ValueError) as e:
        return None, f"{rel}/marks.jsonl unreadable ({type(e).__name__})"
    return out, None


def clog_collected(d, name):
    """the collected C log of a pass (the collector copies it to ccheck/ and gzips it), and whether it has a line"""
    p = first_there(os.path.join(d, "ccheck", f"c-log-{name}.jsonl"), os.path.join(d, "ccheck", f"c-log-{name}.jsonl.gz"))
    if p is None:
        return None, False
    try:
        with _open(p) as f:
            for x in f:
                if x.strip():
                    return p, True
    except (OSError, EOFError):
        return p, False
    return p, False


def check_rows(d):
    p = first_there(os.path.join(d, "ccheck", "ccheck-all.json"), os.path.join(d, "ccheck", "ccheck-all.json.gz"))
    if p is None:
        return None, "no ccheck/ccheck-all.json (or .gz)"
    try:
        with _open(p) as f:
            j = json.load(f)
    except (OSError, EOFError, ValueError) as e:
        return None, f"{os.path.relpath(p, d)} unreadable ({type(e).__name__})"
    rows = j.get("launches") if isinstance(j, dict) else None
    if not isinstance(rows, list):
        return None, f"{os.path.relpath(p, d)} lists no launches"
    return rows, None


def match(marks, rows):
    """(per-mark row counts, orphan rows, marks without an integer records): rows by t_start_ms into the marks' windows"""
    ms = sorted(marks, key=lambda m: m["t_start_ms"])
    starts = [m["t_start_ms"] for m in ms]
    per = [0] * len(ms)
    orphans = 0
    for r in rows:
        t = r.get("t_start_ms")
        try:
            t = int(t)
        except (TypeError, ValueError):
            orphans += 1
            continue
        i = bisect.bisect_right(starts, t) - 1
        if i >= 0 and ms[i]["t_start_ms"] <= t <= ms[i]["t_end_ms"]:
            per[i] += 1
        else:
            orphans += 1
    unread = [i for i, m in enumerate(ms) if not isinstance(m.get("records"), int)]
    return ms, per, orphans, unread


def main(argv):
    if len(argv) != 1 or not os.path.isdir(argv[0]):
        print("usage: cclaunch_q143k.py <E176's data dir>")
        return 2
    d = argv[0]
    problems = 0
    required = []
    for name, rel in (MEASURED, SMOKE):
        marks, why = launch_marks(d, rel)
        if marks is None:
            print(f"MISSING-MARKS {name}: {why} (E176's session runs the smoke, then the measured pass: the record is lost)")
            problems += 1
            continue
        if name == MEASURED[0] and not marks:
            print(f"NO-LAUNCH {name}: its marks record no launch: no hold ran, so nothing is scored (read the session log: the start gate?)")
            problems += 1
            continue
        if not marks:
            print(f"NOT-REQUIRED {name}: its marks record no launch, so it carries no C log")
            continue
        p, has = clog_collected(d, name)
        print(f"REQUIRED {name}: {len(marks)} launch mark(s); C log {os.path.relpath(p, d) if p else 'none'}")
        if not has:
            print(f"MISSING-CLOG {name}: its marks record {len(marks)} launch(es) and no C log with a line was collected (ccheck/c-log-{name}.jsonl)")
            problems += 1
            continue
        required.append((name, marks))
    if required:
        rows, why = check_rows(d)
        if rows is None:
            print(f"CHECK-UNREAD: {why}")
            problems += 1
        else:
            logs = {f"c-log-{n}.jsonl": n for n, _ in (MEASURED, SMOKE)}
            unknown = sorted({str(r.get("log")) for r in rows if r.get("log") not in logs})
            for u in unknown:
                print(f"UNKNOWN-LOG {u}: the check read a log that is neither pass's")
                problems += 1
            for name, marks in required:
                mine = [r for r in rows if r.get("log") == f"c-log-{name}.jsonl"]
                untimed = [m for m in marks if not (isinstance(m.get("t_start_ms"), int) and isinstance(m.get("t_end_ms"), int))]
                if untimed:
                    print(f"COUNT-UNREAD {name}: {len(untimed)} launch mark(s) carry no integer t_start_ms and t_end_ms, so their windows are not known")
                    problems += 1
                    continue
                ms, per, orphans, unread = match(marks, mine)
                want = sum(m["records"] for m in ms if isinstance(m.get("records"), int))
                fails = sum(1 for r in mine if r.get("verdict") == "FAIL")
                if unread:
                    print(f"COUNT-UNREAD {name}: {len(unread)} launch mark(s) carry no integer records, so the launches they hold are not known")
                    problems += 1
                    continue
                diff = [(i, ms[i]["records"], per[i]) for i in range(len(ms)) if per[i] != ms[i]["records"]]
                if orphans:
                    print(f"ORPHAN {name}: {orphans} checked launch(es) fall outside every launch mark's window")
                    problems += 1
                if diff:
                    short = sum(1 for _, w, g in diff if g < w)
                    tag = "COUNT-SHORT" if short else "COUNT-OVER"
                    ex = "; ".join(f"process {i + 1} at t_start_ms {ms[i]['t_start_ms']}: records {w}, checked {g}" for i, w, g in diff[:3])
                    print(f"{tag} {name}: the check read {len(mine)} launch(es) in its log, the marks record {want} in {len(ms)} process(es); "
                          f"{len(diff)} process(es) differ ({ex})")
                    problems += 1
                if not orphans and not diff:
                    print(f"COUNT-OK {name}: {len(mine)} checked launches in {len(ms)} processes, each process's records equal to its rows "
                          f"(C FAIL rows {fails}: the registered C rule reads them)")
    print(f"cclaunch: {len(required)} pass(es) with a C log read against their marks; {problems} problem(s): {'OK' if problems == 0 else 'STOP'}")
    return 4 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
