#!/usr/bin/env python3
"""E185 (M11's session 3): the launch gate of step 22 (rb/s22_collect_e185.sh): E185's passes that must carry a C log, and the check of C read
against the launches their marks record. It is ../../q143k-runbook/cclaunch_q143k.py (6b013ad9, which stays as committed) with E185's passes
(the smoke p18501, the measured pass p18520) and three changes, each marked E185:
  1. --gates-only: before any check of C is read, the session's own gates from its marks. F0-STOPPED: there is no measured pass and the
     smoke's floor mark did not pass (A6-1: F0 above 53.9 C or unreadable; the session ended before the smoke's first launch). G0-REFUSED:
     the measured pass's start_gate mark did not pass (G0-A6 with A8-4). Either exits 5: nothing ran to score. Else GATES-PASSED, 0.
  2. Distinct t_start_ms (the Q143(k) code verifier's kit-v4 item): two launch marks of one pass with the same t_start_ms are COUNT-DUP, a
     problem, since the rows are matched to marks by their start times.
  3. The words of E176's runbook note 2, section 2 (the code verifier's fault 1, carried): no registered rule reads a C FAIL for M11's holds,
     so a C FAIL in a matched row stops nothing here and reaches no rule; the printout counts them, and a record says "computed correctly"
     only when the check's all_pass is True.
The rules, otherwise q143k's: p18520 is required (its marks there with a launch, else MISSING-MARKS or NO-LAUNCH; its C log collected, else
MISSING-CLOG); p18501's marks must be there and it is required when they show a launch; for each required pass the check's rows for its log
must match its launch marks one for one (COUNT-OK, else COUNT-SHORT, COUNT-OVER, ORPHAN, COUNT-UNREAD); a row of neither pass's log is
UNKNOWN-LOG.

    python3 -B tools/claims-v3/e185/rb/cclaunch_e185.py [--gates-only] <E185's data dir>

Exit 0 when every rule holds; 4 when any does not; 5 (--gates-only) when a gate of the session refused; 2 on a usage error. Standard library
only; it reads, and writes nothing. It prints paths relative to the data directory. SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
SMOKE = ("p18501", os.path.join("aifoundry3", "e185-smoke", "p18501"))
MEASURED = ("p18520", os.path.join("aifoundry3", "e185", "p18520"))


def _open(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def first_there(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def kind_marks(d, rel, kind):
    """E185 change 1: the pass's marks of one kind, or None when its marks.jsonl is not there"""
    p = os.path.join(d, rel, "marks.jsonl")
    if not os.path.exists(p):
        return None
    out = []
    with open(p) as f:
        for x in f:
            if x.strip():
                try:
                    m = json.loads(x)
                except ValueError:
                    continue
                if m.get("kind") == kind:
                    out.append(m)
    return out


def gates(d):
    """E185 change 1: the session's own gates, read before any check of C"""
    fl = kind_marks(d, SMOKE[1], "floor")
    sg = kind_marks(d, MEASURED[1], "start_gate")
    if sg is None:
        if fl and fl[-1].get("passed") is False:
            print(f"F0-STOPPED {SMOKE[0]}: A6-1's floor mark did not pass ({fl[-1].get('why')}): the session ended before the smoke's first "
                  "launch, and no measured pass ran: nothing to score")
            return 5
        print(f"GATES-UNREAD: no {MEASURED[1]}/marks.jsonl and no failed floor mark: the launch gate reads the record (MISSING-MARKS)")
        return 0
    if sg and sg[-1].get("passed") is False:
        print(f"G0-REFUSED {MEASURED[0]}: its start_gate mark did not pass ({sg[-1].get('why')}): no hold ran: nothing to score")
        return 5
    print(f"GATES-PASSED: the smoke's floor mark {fl[-1].get('passed') if fl else None}; {MEASURED[0]}'s start gate "
          f"{sg[-1].get('passed') if sg else None}")
    return 0


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
    only = bool(argv) and argv[0] == "--gates-only"
    argv = argv[1:] if only else argv
    if len(argv) != 1 or not os.path.isdir(argv[0]):
        print("usage: cclaunch_e185.py [--gates-only] <E185's data dir>")
        return 2
    d = argv[0]
    if only:
        return gates(d)
    problems = 0
    required = []
    for name, rel in (MEASURED, SMOKE):
        marks, why = launch_marks(d, rel)
        if marks is None:
            print(f"MISSING-MARKS {name}: {why} (E185's session runs the smoke, then the measured pass: the record is lost)")
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
                starts = [m["t_start_ms"] for m in marks]
                if len(set(starts)) != len(starts):                                           # E185 change 2
                    print(f"COUNT-DUP {name}: {len(starts) - len(set(starts))} launch mark(s) share a t_start_ms with another, so the rows "
                          "cannot be matched to them one for one")
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
                          f"(C FAIL rows {fails}: no registered rule reads them; 'computed correctly' only when all_pass is True)")
    print(f"cclaunch: {len(required)} pass(es) with a C log read against their marks; {problems} problem(s): {'OK' if problems == 0 else 'STOP'}")
    return 4 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
