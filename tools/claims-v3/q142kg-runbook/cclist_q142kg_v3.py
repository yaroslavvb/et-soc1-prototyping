#!/usr/bin/env python3
"""Q142(v2) fix pass, Thu 5 Nov 2026: the sessions of a collected run that must carry a C log, v3 (E173.md.dated-note-2.md and
E174.md.dated-note-2.md, committed before this file and before any E173 or E174 data). cclist_q142kg_v2.py (lab 34436d68) and v1
(cclist_q142kg.py, 5a2a9ba0) stay as committed; v3 imports v2's functions unchanged and adds one rule.

Why v3. v2 reads the sessions the queue's record started (session_start lines) and every session directory in the runs dir; it never reads
the names in the queue's session_end lines (cclist_q142kg_v2.py line 107). The first verifier of v2 (verify-q142v2-code, Thu 5 Nov 2026,
its fault 3, case D3) built a session known only from its session_end (9.5 card-minutes), with its start line and its directory lost: v2's
gate passed it (rc 0). The queue writes a session's session_end only after its session_start (queue_e173.py and queue_e174.py, session()),
so a genuine record names no session in its session_end lines that it did not start: the rule below can only stop a record that lost lines.

  v3's rule 2b: the sessions read are also those the queue's record names in a session_end line. A session named there whose directory is not
  in the runs dir is required when v1 requires a started session with no directory (p8gov.required_c_logs: one of smoke, stoptest-board and
  s1, or a BURST session s<digits>), so it is listed REQUIRED, and with no C log (none can be there) MISSING-CLOG: the gate stops (14).
  Everything else is v2's, unchanged: v3 can only add sessions to v2's list, never remove one.

    python3 -B tools/claims-v3/q142kg-runbook/cclist_q142kg_v3.py <the queue's runs dir> <the dir the ccheck-<session>.json files go in>

It prints `REQUIRED <session> <ccheck path>` per required session (v1's form, which the runbook's gate reads), `MISSING-CLOG <session>` for one
with no C log, `V2-ADDED <session>: <why>` for each session v2's rule adds to v1's list, `V3-ADDED <session>: <why>` for each v3 adds to v2's,
then `cclist v3: <n> required (v2 <m>, v1 <k>), <j> without a C log`. Exit 0 when every required session has a C log; 4 when one has none or
the queue's record is missing; 2 on a usage error. Standard library, p8gov and cclist_q142kg_v2 (unchanged); it reads, and writes nothing.
SPDX-License-Identifier: Apache-2.0
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cclist_q142kg_v2 as V2  # noqa: E402  (34436d68, unchanged; it imports p8gov from ../e173)

G = V2.G


def ended_names(qp):
    """the names in the queue's record's session_end lines, in order"""
    out = []
    for r in G._read_jsonl(qp):
        if r.get("kind") == "session_end" and r.get("name"):
            out.append(r["name"])
    return list(dict.fromkeys(out))


def main(argv):
    if len(argv) != 2:
        print("usage: cclist_q142kg_v3.py <the queue's runs dir> <the ccheck dir>")
        return 2
    q, cdir = argv
    if not os.path.isdir(q):
        print(f"usage: {q} is not a directory")
        return 2
    qp, started, ends = V2.queue_record(q)
    if not qp:
        print(f"MISSING-QUEUE: {q} holds no queue.jsonl (or .gz): the queue's record is lost, so the sessions that must carry a C log cannot be read")
        print("cclist v3: 0 required (v2 and v1 not read), the queue's record missing")
        return 4
    v1, rep = G.required_c_logs(q, V2.LISTED)
    v1_names = set(started) | {n for n in V2.LISTED if os.path.isdir(os.path.join(q, n))}     # what v1 reads (p8gov.required_c_logs)
    on_disk = sorted(d for d in os.listdir(q) if V2.NAMED.match(d) and os.path.isdir(os.path.join(q, d)))
    # v2's list, as v2 computes it (cclist_q142kg_v2.main, lines 107-116)
    req = list(v1)
    added = {}
    for n in list(dict.fromkeys(started + on_disk)):
        if n in req:
            continue
        w = V2.why_v2(n, os.path.join(q, n), ends, n in v1_names)
        if w:
            req.append(n)
            added[n] = w
    n_v2 = len(req)
    # v3's rule 2b: the names only the queue's session_end lines give
    added3 = {}
    for n in ended_names(qp):
        if n in req or n in started or n in on_disk:
            continue
        if not os.path.isdir(os.path.join(q, n)) and (n in V2.LISTED or V2.burst(n)):
            end = ends.get(n) or {}
            req.append(n)
            added3[n] = (f"named only by the queue's session_end (reason {str(end.get('reason'))[:40]!r}, {end.get('card_min')} card-minutes), "
                         "its session_start line and its directory lost: v1's rule for a session with no directory")
    missing = 0
    for s in req:
        sd = os.path.join(q, s)
        has = any(os.path.exists(os.path.join(sd, x)) for x in ("c-log.jsonl", "c-log.jsonl.gz"))
        print(f"REQUIRED {s} {os.path.join(cdir, f'ccheck-{s}.json')}")
        if s in added:
            print(f"V2-ADDED {s}: {added[s]}")
        if s in added3:
            print(f"V3-ADDED {s}: {added3[s]}")
        if not has:
            print(f"MISSING-CLOG {s}: it must carry a C log ({added3.get(s) or added.get(s) or rep.get(s)}), and none was collected")
            missing += 1
    print(f"cclist v3: {len(req)} required (v2 {n_v2}, v1 {len(v1)}), {missing} without a C log")
    return 4 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
