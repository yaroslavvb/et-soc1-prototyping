#!/usr/bin/env python3
"""Q142(s) v3.1: did each check of C a collection ran finish? s22_collect.sh runs it after every collector that checks C (e163, e164,
e165, e166) and after e167's own checks, before it says "collected" (v3.1/README.md, fault 1).

Why it is needed. Q139(k)'s ccheck.py (tools/claims-v3/ccheck/ccheck.py, unchanged) exits 1 both when it crashes and when a launch's C
is wrong (ccheck.py:732), so its exit status cannot tell the two apart; and it writes its --out file only when it runs to its end
(ccheck.py:729-731). The collectors print "ccheck rc=N" and go on (collect_e163.sh:62, collect_e166.sh:24, collect_e164.sh:84), and
collect_e165_bounded.sh:83 reads nothing; the scorers then score without the check. In v3's verifier's end-to-end run (a C check that
crashed), E163's scorer still wrote results.md: 17 of its 28 rules read NOT SCORED, and 5 C rules (K14-C, KC, KE, KEprime, KE-C) read
FAIL where the data passes them, and v2 said "E163 collected and scored". So the file is the reading: a check finished if, and only
if, its --out file is there, holds ccheck.py's summary, and was written by this collection.

    python3 -B ccdone_q142s.py [--since <epoch s>] <ccheck --out json> ...

For each file (or, when the file is not there, the same path with .gz, which a collector or a commit may leave), it prints one line:
  CCHECK-DONE     the summary: launches, PASS, ROUNDING, UNMODELLED, FAIL, all_pass. A C FAIL is a finished check: it is not
                  stopped here, and it reaches the registered C rules, as each run's registration says;
  CCHECK-MISSING  no file: the check never ran, or did not run to its end;
  CCHECK-STALE    written before --since (the step's own start, to the second): an earlier collection's file;
  CCHECK-UNREAD   not JSON, no summary, or a summary whose launch count is not the file's;
  CCHECK-EMPTY    a summary of 0 launches: the check read nothing.
It exits 0 when every file is CCHECK-DONE, 4 when any is not, 2 on a usage error. Standard library only; it reads, and never writes,
anything. It prints paths as given (the runbook gives repo-relative ones). SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import sys
import time

VERDICTS = ("PASS", "ROUNDING", "UNMODELLED", "FAIL")      # ccheck.py's VERDICTS, the summary's counts


def read_one(path, since):
    p = path
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        p = path + ".gz"
    if not os.path.exists(p):
        return False, f"CCHECK-MISSING {path}: no file (ccheck.py writes its --out only when the check runs to its end)"
    mt = os.stat(p).st_mtime
    if since is not None and mt < since:
        when = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(mt))
        return False, f"CCHECK-STALE {p}: written {when}, before this step began: an earlier collection's file, not this one's"
    try:
        if p.endswith(".gz"):
            with gzip.open(p, "rt") as f:
                d = json.load(f)
        else:
            with open(p) as f:
                d = json.load(f)
    except (OSError, EOFError, ValueError) as e:
        return False, f"CCHECK-UNREAD {p}: {type(e).__name__}"
    s = d.get("summary") if isinstance(d, dict) else None
    if not isinstance(s, dict) or not isinstance(s.get("launches"), int) or "all_pass" not in s:
        return False, f"CCHECK-UNREAD {p}: no ccheck.py summary in it"
    rows = d.get("launches")
    if not isinstance(rows, list) or len(rows) != s["launches"]:
        n = len(rows) if isinstance(rows, list) else "no"
        return False, f"CCHECK-UNREAD {p}: the summary counts {s['launches']} launches, the file lists {n}"
    if s["launches"] == 0:
        return False, f"CCHECK-EMPTY {p}: a summary of 0 launches (the check read nothing)"
    counts = ", ".join(f"{k} {s.get(k, 0)}" for k in VERDICTS)
    return True, f"CCHECK-DONE {p}: {s['launches']} launches, {counts}, all_pass {bool(s['all_pass'])}"


def main(argv):
    since, paths, i = None, [], 0
    while i < len(argv):
        if argv[i] == "--since" and i + 1 < len(argv):
            try:
                since = float(argv[i + 1])
            except ValueError:
                print(f"usage: --since takes epoch seconds, not {argv[i + 1]!r}")
                return 2
            i += 2
            continue
        paths.append(argv[i])
        i += 1
    if not paths:
        print("usage: ccdone_q142s.py [--since <epoch s>] <ccheck --out json> ...")
        return 2
    done = allpass = 0
    for p in paths:
        ok, line = read_one(p, since)
        print(line)
        done += ok
        allpass += ok and line.endswith("all_pass True")
    print(f"ccdone: {done} of {len(paths)} C checks finished ({allpass} of them all PASS): "
          f"{'FINISHED' if done == len(paths) else 'NOT FINISHED'}")
    return 0 if done == len(paths) else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
