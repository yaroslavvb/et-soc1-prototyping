#!/usr/bin/env python3
"""Q142(kg): the sessions of a collected run that must carry a C log (the Q142 critic's fault 3: v3.1's cc_gate stopped a collection whose check of
C did not finish, but did not require a check for every session that should carry one; in e165 and e167 a session with no C log was skipped).

    python3 -B tools/claims-v3/q142kg-runbook/cclist_q142kg.py <the queue's runs dir> <the dir the ccheck-<session>.json files go in>

The list is E173.md's and E174.md's: smoke, stoptest-board and every BURST session s1-s6 the queue started that ran a work launch (read from the
queue's own queue.jsonl session_start records and each session's launches.jsonl work launches; tools/claims-v3/e173/p8gov.required_c_logs, the
scorers' own rule); stoptest-die runs no launch and carries none; a dry session (the toy card writes no C log) needs none. It prints, per required
session, `REQUIRED <session> <ccheck path>`, and `MISSING-CLOG <session>` for one that has no C log at all; then `cclist: <n> required, <m> without
a C log`. Exit 0 when every required session has a C log, 4 when one has none, 2 on a usage error. The step then runs ccdone_q142s.py on the
REQUIRED paths (v3.1's cc_gate): every one must be a finished check written by this collection. Standard library; it reads, and writes nothing.
SPDX-License-Identifier: Apache-2.0
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import p8gov as G  # noqa: E402

LISTED = ("smoke", "stoptest-board", "s1")


def main(argv):
    if len(argv) != 2:
        print("usage: cclist_q142kg.py <the queue's runs dir> <the ccheck dir>")
        return 2
    q, cdir = argv
    if not os.path.isdir(q):
        print(f"usage: {q} is not a directory")
        return 2
    req, rep = G.required_c_logs(q, LISTED)
    missing = 0
    for s in req:
        sd = os.path.join(q, s)
        has = any(os.path.exists(os.path.join(sd, n)) for n in ("c-log.jsonl", "c-log.jsonl.gz"))
        print(f"REQUIRED {s} {os.path.join(cdir, f'ccheck-{s}.json')}")
        if not has:
            print(f"MISSING-CLOG {s}: the registration requires a C log of it ({rep.get(s)}), and none was collected")
            missing += 1
    print(f"cclist: {len(req)} required, {missing} without a C log")
    return 4 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
