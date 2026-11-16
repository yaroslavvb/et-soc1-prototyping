#!/usr/bin/env python3
"""E202's stand-ins for THE REAL-PATH DESK TEST (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): what stands at the box
tools' REAL paths in a stand-in aifoundry3 tree, so that run_e202.py runs its real path (DRY unset) end to end on the desk:

    <tree>/build/ettelem/ettelem          -> standin_e202.py ettelem config | sample ...   (behind the box copy of E128's guard)
    <PATH>/et-who                         -> standin_e202.py etwho
    <tree>/build/e202mnist/host/mnistmlp_host -> standin_e202.py host <the host's arguments>

Each is a two-line shell script that execs this file at once (so for its first milliseconds its process name is the tool's: the desk
tests wait for THE QUIET DESK FLAG to be absent). The behaviour is fake_card_e202.py's (imported, unchanged), with its knobs read from
the CASE FILE <tree>/.standin/case.json, never from the environment (the runner refuses desk-test variables on its real path), and the
launch schedule in <tree>/.standin/sched.jsonl. Knobs as fake_card_e202.py names them: CONFIG, ETWHO, SAMPLER, BASE, SPLIT, SCALE,
INJECT, SMOKE, BURSTS. Every call is appended to <tree>/.standin/calls.jsonl (the tool, its arguments, the time), so a case can assert
what the runner sent. Nothing here opens a device. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fake_card_e202 as F  # noqa: E402


def tree():
    """The stand-in tree: the runner's cwd (its root), or this file's tree, whichever holds .standin/case.json."""
    for base in (os.getcwd(), os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))):
        if os.path.exists(os.path.join(base, ".standin", "case.json")):
            return base
    return os.getcwd()


def main(argv):
    t = tree()
    sd = os.path.join(t, ".standin")
    try:
        knobs = json.load(open(os.path.join(sd, "case.json")))
    except (OSError, ValueError):
        knobs = {}
    knobs["SCHED"] = os.path.join(sd, "sched.jsonl")
    with open(os.path.join(sd, "calls.jsonl"), "a") as f:
        f.write(json.dumps({"t": round(time.time(), 3), "tool": argv[0] if argv else "", "args": argv[1:]}) + "\n")
    if not argv:
        return 2
    w = argv[0]
    if w == "ettelem":
        sub = argv[1:2]
        if sub == ["config"]:
            return F.main(["config"], knobs)
        if sub == ["sample"]:
            return F.main(["sample"] + argv[2:], knobs)
        print(f"ettelem stand-in: refused {argv[1:]}", file=sys.stderr)
        return 97
    if w == "etwho":
        return F.main(["etwho"], knobs, counter_file=os.path.join(sd, "etwho-calls"))
    if w == "host":
        return F.main(["host"] + argv[1:], knobs)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
