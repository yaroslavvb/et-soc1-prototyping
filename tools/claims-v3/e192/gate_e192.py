#!/usr/bin/env python3
"""E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE KIT'S GATE, run by session_e192.sh beside the proposal's
reference session (run_session.sh, unchanged). It opens no device and sends no command: it reads the session's own files (marks.jsonl,
runs.jsonl, written by run_block.py) and acts only through the registered stop file OUT/STOP, which run_block.py checks before every
device process and the host before every 0.4 s launch (E192.md sections 9 and 17.2: "the kit may add stops that end a session early; it
never changes an arm, a value, the order, a window, a threshold or the reduction"). Two gates, each a stop and nothing else:

  THE SMOKE GATE (E192.md 17.2: "a smoke gate that reads the smoke's INTBITS lines (the reference run_block.py reports a failed smoke run
  but does not stop on it)"). When the smoke block (pass -1) has recorded its three runs (nop, add.a.f2, add.cr.l31), each must have:
  its device process's exit 0; at least 3 INTBITS lines (2 s of 0.4 s launches); on every line "ok" true, "check_bad" 0 and 1,024
  participants (the reducer's run gates and registered check 1's count); and, with a heater, the heater check's own launch exit 0 (the
  reference reads its board level but not its exit: a heater that failed would pass the 70 W check on idle readings and leave every
  run's approach unable to preheat). Else STOP before any pass: the smoke ends in its 10 s 'after'
  idle, which checks the stop file, and run_session.sh runs no pass. Read 0.8 s after the third run's mark (its INTBITS lines follow
  the mark at once) and always before pass 0's first device process, which comes 10 s later at the earliest.

  THE CAP (E192.md section 10: "65 card-minutes from the session's first card command: no pass starts that could end after it ... never
  by killing a device process"). At the end of each block (its 'after' idle mark), the next pass p may start only if
  now + (the 30 s gap, for p > 0) + D <= first + cap, where D is the longest measured pass so far (from its 'before' idle's start to its
  'after' idle's end) plus 60 s, or, before any pass was measured, D0 (400 s: the proposal's 5.6 minutes a pass, section 9, and about a
  minute). Else STOP (run_session.sh checks it after the gap, or pass 0 in its first idle). And 30 s before the cap, if the session still
  runs, STOP: the launch in flight finishes and the block ends at its next check (never a kill).

    python3 -I -B gate_e192.py OUT --first EPOCH --cap 3900 [--d0 400] [--gap 30] [--passes 9]
Writes OUT/gate.jsonl (one event a line) and prints each event. Exits when OUT/SESSION_DONE appears, or after a STOP (its own or
anyone's). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys
import time

SMOKE_ARMS = ("nop", "add.a.f2", "add.cr.l31")
PARTICIPANTS = 1024
MIN_LAUNCHES = 3
MARGIN_S = 60.0
HARD_S = 30.0


class Tail:
    """New complete JSON lines of a file that grows."""

    def __init__(self, path):
        self.path, self.pos, self.buf = path, 0, ""

    def read(self):
        try:
            with open(self.path, "rb") as f:
                f.seek(self.pos)
                chunk = f.read()
                self.pos = f.tell()
        except OSError:
            return []
        self.buf += chunk.decode(errors="ignore")
        *lines, self.buf = self.buf.split("\n")
        out = []
        for ln in lines:
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
        return out


def smoke_verdict(marks, runs):
    """(ok, detail) for the smoke block's three runs."""
    rm = [m for m in marks if m.get("kind") == "run" and m.get("pass") == -1]
    bad, rows = [], []
    for m in rm:
        seq, arm = m.get("seq"), m.get("arm")
        lines = [r for r in runs if r.get("pass") == -1 and r.get("seq") == seq]
        n = len(lines)
        nok = sum(1 for r in lines if r.get("ok") is True)
        nbad = sum(1 for r in lines if r.get("check_bad", 1) != 0)
        parts = sorted({r.get("participants") for r in lines}, key=str)
        rows.append({"seq": seq, "arm": arm, "rc": m.get("rc"), "launches": n, "ok": nok, "check_bad_lines": nbad,
                     "participants": parts})
        why = []
        if m.get("rc") != 0:
            why.append("exit %s" % m.get("rc"))
        if n < MIN_LAUNCHES:
            why.append("%d INTBITS lines (< %d)" % (n, MIN_LAUNCHES))
        if nok != n:
            why.append("%d of %d lines not ok" % (n - nok, n))
        if nbad:
            why.append("check_bad on %d lines" % nbad)
        if parts != [PARTICIPANTS]:
            why.append("participants %s" % parts)
        if why:
            bad.append("%s: %s" % (arm, ", ".join(why)))
    hcm = [m for m in marks if m.get("kind") == "heater_check" and m.get("pass") == -1]
    for m in hcm:  # the kit's addition: the smoke's heater launch must itself have run (exit 0), or its level read nothing
        rows.append({"heater_check_rc": m.get("rc")})
        if m.get("rc") != 0:
            bad.append("the heater check's launch exited %s" % m.get("rc"))
    arms = [m.get("arm") for m in rm]
    if tuple(arms) != SMOKE_ARMS:
        bad.append("the smoke's arms were %s, not %s" % (arms, list(SMOKE_ARMS)))
    return (not bad), rows, "; ".join(bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--first", type=float, required=True, help="the session's first card command, epoch seconds")
    ap.add_argument("--cap", type=float, required=True)
    ap.add_argument("--d0", type=float, default=400.0)
    ap.add_argument("--gap", type=float, default=30.0)
    ap.add_argument("--passes", type=int, default=9)
    a = ap.parse_args()
    stop_file = os.path.join(a.out, "STOP")
    done_file = os.path.join(a.out, "SESSION_DONE")
    tm, tr = Tail(os.path.join(a.out, "marks.jsonl")), Tail(os.path.join(a.out, "runs.jsonl"))
    marks, runs = [], []
    smoke_done, smoke_due = False, None
    began = {}          # pass -> its 'before' idle's start (s)
    durs = {}           # pass -> measured duration (s)
    seen_after = set()

    def event(kind, **kw):
        rec = dict(t_ms=int(time.time() * 1000), kind=kind, **kw)
        with open(os.path.join(a.out, "gate.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print("gate_e192: " + json.dumps(rec), flush=True)

    def stop(why, **kw):
        if not os.path.exists(stop_file):
            with open(stop_file, "w") as f:
                f.write(json.dumps({"by": "gate_e192", "why": why, "t_ms": int(time.time() * 1000)}) + "\n")
        event("stop", why=why, **kw)
        sys.exit(0)

    event("start", first=a.first, cap_s=a.cap, d0_s=a.d0, gap_s=a.gap, passes=a.passes,
          cap_at=time.strftime("%H:%M:%S %Z", time.localtime(a.first + a.cap)))
    while True:
        if os.path.exists(done_file):
            event("session_done")
            return 0
        if os.path.exists(stop_file):
            try:
                why = open(stop_file).read().strip()[:300]
            except OSError:
                why = "?"
            event("stop_seen", stop=why)
            return 0
        now = time.time()
        new_m = tm.read()
        marks += new_m
        runs += tr.read()
        if not smoke_done:
            nrun = sum(1 for m in marks if m.get("kind") == "run" and m.get("pass") == -1)
            p0 = any(m.get("pass", -1) >= 0 for m in marks)
            if nrun >= len(SMOKE_ARMS) and smoke_due is None:
                smoke_due = now + 0.8
            if (smoke_due is not None and now >= smoke_due) or p0:
                runs += tr.read()
                ok, rows, why = smoke_verdict(marks, runs)
                smoke_done = True
                if not ok:
                    stop("smoke gate: " + why, runs=rows)
                event("smoke_gate", verdict="GO", runs=rows)
        for m in new_m:
            p = m.get("pass", -1)
            if m.get("kind") == "idle" and m.get("label") == "before" and p >= 0:
                began[p] = m.get("t0_ms", 0) / 1000.0
            if m.get("kind") == "idle" and m.get("label") == "after" and p not in seen_after:
                seen_after.add(p)
                if p >= 0 and p in began:
                    durs[p] = m.get("t1_ms", 0) / 1000.0 - began[p]
                if p == -1 and not smoke_done:
                    runs += tr.read()
                    ok, rows, why = smoke_verdict(marks, runs)
                    smoke_done = True
                    if not ok:
                        stop("smoke gate: " + why, runs=rows)
                    event("smoke_gate", verdict="GO", runs=rows)
                nxt = p + 1
                if nxt >= a.passes:
                    event("last_block_done", block=p)
                    continue
                d = (max(durs.values()) + MARGIN_S) if durs else a.d0
                need = (a.gap if nxt > 0 else 0.0) + d
                left = a.first + a.cap - time.time()
                if need > left:
                    stop("cap: pass %d could end after the cap (%.0f s needed: %s; %.0f s left of %.0f)" % (
                        nxt, need, "the longest pass so far %.0f s + %.0f s" % (max(durs.values()), MARGIN_S) if durs
                        else "D0 %.0f s" % a.d0, left, a.cap), next_pass=nxt, measured=durs)
                event("cap_ok", next_pass=nxt, need_s=round(need, 1), left_s=round(left, 1),
                      measured={str(k): round(v, 1) for k, v in durs.items()})
        if time.time() >= a.first + a.cap - HARD_S:
            stop("cap: %.0f s before the cap (%.0f s from the first card command): the run in flight finishes, no more" % (
                HARD_S, a.cap))
        time.sleep(0.25)


if __name__ == "__main__":
    sys.exit(main())
