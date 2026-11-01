#!/usr/bin/env python3
"""E111 amendment A3 (the owner's ruling of 1 November 2026, about 15:00 PST): the first queue's W2 and END run under code loaded
before the ruling (A1: a session idle under 120 minutes blocks; device processes, the use count and the lock as run_hpl.py). This
watcher, started on aifoundry2 while W2 ran, applies A3's whole rule (idle_logins_e111.decide: a non-idle terminal, or a process
of a logged-in other user started under 120 minutes ago) to those steps: every 10 s, if a user blocks while one of them runs, it
touches that step's RUNDIR/STOP, our own file (run_hpl.py ends the session at its next check, exit 4), once per step, and records
it. It reads `who -u` and `ps` only: it never signals a process and never touches another user's session. Records are counts only.

    setsid nohup python3 watch_activity_e111.py --runs build/e111/runs --steps W2,END --until-ms <epoch ms> > <log> 2>&1 < /dev/null &
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idle_logins_e111 as IL  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--steps", default="W2,END")
    ap.add_argument("--until-ms", type=int, required=True)
    a = ap.parse_args()
    steps = set(a.steps.split(","))
    log = os.path.join(a.runs, "activity_watch.jsonl")

    def rec(**kw):
        with open(log, "a") as f:
            f.write(json.dumps(dict(t_ms=int(time.time() * 1000), zone=time.strftime("%Z"), **kw)) + "\n")

    touched, last_hb, last_state = set(), 0, None
    blocking, r = IL.decide()
    rec(kind="watch_start", steps=sorted(steps), blocking_users=len(blocking), decision=r)
    while time.time() * 1000 < a.until_ms and not os.path.exists(os.path.join(a.runs, "WATCH-STOP")):
        try:
            st = json.load(open(os.path.join(a.runs, "status.json")))
        except (OSError, ValueError):
            st = {}
        blocking, r = IL.decide()
        step = st.get("step")
        running = st.get("state") == "running" and step in steps
        state = (st.get("state"), step, len(blocking))
        if state != last_state:
            rec(kind="state", queue_state=st.get("state"), step=step, blocking_users=len(blocking), decision=r)
            last_state = state
        if running and blocking and step not in touched:
            p = os.path.join(a.runs, step, "STOP")
            open(p, "a").close()
            touched.add(step)
            rec(kind="touched_stop", step=step, blocking_users=len(blocking), decision=r)
        if time.time() - last_hb > 300:
            rec(kind="heartbeat", queue_state=st.get("state"), step=step, blocking_users=len(blocking), decision=r)
            last_hb = time.time()
        time.sleep(10)
    rec(kind="watch_end")
    return 0


if __name__ == "__main__":
    sys.exit(main())
