#!/usr/bin/env python3
"""Q142(kg) fix pass, Thu 5 Nov 2026: the sessions of a collected run that must carry a C log, v2 (E173.md.dated-note-1.md and
E174.md.dated-note-1.md, section 3, committed before any E173 or E174 data). cclist_q142kg.py (v1, lab 5a2a9ba0) stays as committed.

Why v2. v1 reads the list from the queue's record (queue.jsonl's session_start) and each session's launches.jsonl (p8gov.required_c_logs, the
scorers' own rule). The kits' verifier found two gaps (its fault 7, probes V7 and V8): a copy with no queue.jsonl and no smoke directory drops
smoke from the list, and a session whose launches.jsonl is lost counts no work launch and drops out. Either way the gate passed and the step said
"collected and scored", though a session that ran carried no checked C log. v2 can only add sessions to v1's list, never remove one:

  1. the queue's record (queue.jsonl or queue.jsonl.gz) must be in the runs dir; without it the list cannot be read (MISSING-QUEUE, exit 4);
  2. the sessions read are those the queue's record started and every directory in the runs dir with a session's name (smoke, stoptest-board,
     stoptest-die, s<digits>), so a session whose session_start line was lost is still read;
  3. a session is required if v1 requires it; or, for a session directory v1 did not read (one the queue's record does not start, other than
     smoke, stoptest-board and s1, which v1 reads when they are there), if v1's own rule would require it (d): its launches.jsonl counts a work
     launch; or, for smoke, stoptest-board and every BURST session s1-s6 that is not a dry session, if any of these shows it ran a launch:
       (a) its runs.jsonl holds at least one run record (a run is made of work launches, whatever launches.jsonl says);
       (b) its launches.jsonl is missing and the queue's session_end for it gives more than 0 card-minutes;
       (c) it is stoptest-board and the queue's session_end for it gives the board stop ("safety:board ..."), which fires only inside its
           launch;
  4. stoptest-die keeps v1's rule (required only if it ran a work launch); a dry session (the toy card writes no C log) needs none.

    python3 -B tools/claims-v3/q142kg-runbook/cclist_q142kg_v2.py <the queue's runs dir> <the dir the ccheck-<session>.json files go in>

It prints `REQUIRED <session> <ccheck path>` per required session (v1's form, which the runbook's gate reads), `MISSING-CLOG <session>` for one
with no C log, `V2-ADDED <session>: <why>` for each session v2 adds to v1's list, then `cclist v2: <n> required (v1 <m>), <k> without a C log`.
Exit 0 when every required session has a C log; 4 when one has none or the queue's record is missing; 2 on a usage error. Standard library and
p8gov (unchanged); it reads, and writes nothing. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import p8gov as G  # noqa: E402

LISTED = ("smoke", "stoptest-board", "s1")          # v1's listed sessions (cclist_q142kg.py)
NAMED = re.compile(r"^(smoke|stoptest-board|stoptest-die|s[0-9]+)$")


def burst(n):
    return len(n) > 1 and n[0] == "s" and n[1:].isdigit()


def queue_record(q):
    """(the queue's record path, the names it started in order, {name: its last session_end's 'end' dict})"""
    qp = G._first(q, "queue.jsonl", "queue.jsonl.gz")
    started, ends = [], {}
    if not qp:
        return None, started, ends
    for r in G._read_jsonl(qp):
        if r.get("kind") == "session_start" and r.get("name"):
            started.append(r["name"])
        elif r.get("kind") == "session_end" and r.get("name"):
            ends[r["name"]] = r.get("end") or {}
    return qp, started, ends


def runs_records(sd):
    p = G._first(sd, "runs.jsonl", "runs.jsonl.gz")
    return sum(1 for _ in G._read_jsonl(p)) if p else 0


def why_v2(n, sd, ends, v1_read):
    """why v2 requires session n (its directory sd) beyond v1, or None; v1_read: v1 read this session (its names)"""
    if not os.path.isdir(sd) or G.is_dry(sd):
        return None
    if not v1_read and (n == "stoptest-die" or n in LISTED or burst(n)):
        wl = G.work_launches(sd)
        if wl > 0:
            return f"(d) launches.jsonl counts {wl} work launch(es), and the queue's record does not start it"
    if not (n in ("smoke", "stoptest-board") or burst(n)):
        return None
    nr = runs_records(sd)
    if nr > 0:
        return f"(a) runs.jsonl holds {nr} run record(s)"
    end = ends.get(n) or {}
    has_launches = bool(G._first(sd, "launches.jsonl", "launches.jsonl.gz"))
    try:
        cm = float(end.get("card_min") or 0)
    except (TypeError, ValueError):
        cm = 0.0
    if not has_launches and cm > 0:
        return f"(b) launches.jsonl is missing and the queue's session_end gives {cm} card-minutes"
    if n == "stoptest-board" and str(end.get("reason") or "").startswith("safety:board"):
        return f"(c) the queue's session_end gives the board stop ({str(end.get('reason'))[:60]}), which fires inside its launch"
    return None


def main(argv):
    if len(argv) != 2:
        print("usage: cclist_q142kg_v2.py <the queue's runs dir> <the ccheck dir>")
        return 2
    q, cdir = argv
    if not os.path.isdir(q):
        print(f"usage: {q} is not a directory")
        return 2
    qp, started, ends = queue_record(q)
    if not qp:
        print(f"MISSING-QUEUE: {q} holds no queue.jsonl (or .gz): the queue's record is lost, so the sessions that must carry a C log cannot be read")
        print("cclist v2: 0 required (v1 not read), the queue's record missing")
        return 4
    v1, rep = G.required_c_logs(q, LISTED)
    v1_names = set(started) | {n for n in LISTED if os.path.isdir(os.path.join(q, n))}     # what v1 reads (p8gov.required_c_logs)
    on_disk = sorted(d for d in os.listdir(q) if NAMED.match(d) and os.path.isdir(os.path.join(q, d)))
    names = list(dict.fromkeys(started + on_disk))
    req = list(v1)
    added = {}
    for n in names:
        if n in req:
            continue
        w = why_v2(n, os.path.join(q, n), ends, n in v1_names)
        if w:
            req.append(n)
            added[n] = w
    missing = 0
    for s in req:
        sd = os.path.join(q, s)
        has = any(os.path.exists(os.path.join(sd, x)) for x in ("c-log.jsonl", "c-log.jsonl.gz"))
        print(f"REQUIRED {s} {os.path.join(cdir, f'ccheck-{s}.json')}")
        if s in added:
            print(f"V2-ADDED {s}: {added[s]}")
        if not has:
            print(f"MISSING-CLOG {s}: it must carry a C log ({added.get(s) or rep.get(s)}), and none was collected")
            missing += 1
    print(f"cclist v2: {len(req)} required (v1 {len(v1)}), {missing} without a C log")
    return 4 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
