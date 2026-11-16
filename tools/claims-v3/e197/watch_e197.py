#!/usr/bin/env python3
"""E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): THE KIT'S WATCH, run by session_e197.sh beside the proposal's
reference session (run_session.sh, stopwatch.py and the lab's runner lab/run_trains.py, all unchanged). It opens no device, sends no
command and signals no process: it reads the session's own files (telemetry.jsonl, marks.jsonl, runs.jsonl in OUT) and /proc, and it
acts only through the registered stop file OUT/STOP, which run_trains.py checks before every device process and in every idle, and the
host before every 0.4 s launch (E197.md 9: "The kit may add stops that end a sitting early; it never changes a train, a kind, a value,
the order, a window, a threshold, a cap or the reduction"). Every STOP it writes is one JSON line {"by": "watch_e197", "why", "t_ms",
"card"} (the first writer's STOP stands: it never writes over another's). Its watches:

  1. THE KIT'S LIVE STOPS (E197.md 9, "the box's, the kit's"), on the session's own telemetry: board power AT OR ABOVE 65 W on three
     distinct readings in a row (a sample that repeats the previous board value is the same reading of the meter: it neither counts nor
     resets the run, the stopwatch's rule); a die reading (temp_c.minshire[0]) at or above 70 C; a minion clock (mhz.minion) other than
     600 MHz, or missing, on three samples in a row. (The proposal's stopwatch stops above 65 W, at 70 C and on a quiet sampler; the
     runner on 70 C and stale telemetry: these stay theirs.)
  2. THE KIT'S SMOKE CHECK. The runner's own smoke gate (registered: 26 train launches ok, letters as planned, rates within 3 %) reads
     neither the participants nor the smoke's anchors. Once the smoke block's gate mark is written with ok true, every smoke launch
     record (the three 1 s anchor bursts and the two train processes) must read "ok" true, "check_bad" 0 and 1,024 participants (the
     reducer's process gates), every smoke device process must have exited 0 with at least two launches (a 1 s burst of 0.4 s launches;
     a train process 13), else STOP. The smoke block and block A run back to back, and block A begins with a 10 s idle that reads the
     stop file every 0.25 s, so a STOP within 8 s of the gate mark ends the sitting before block A's first device process (the read
     comes within 0.5 s of the records). A failed check is a gate stop: no train runs ("no train block that sitting: no data",
     E197.md 11).
  3. THE END-STOP (E197.md 10: the cap counts from the sitting's first card command to its sampler's stop; "never by killing a device
     process"): at the first card command + the cap - 30 s, if the session still runs, STOP. The wrapper sets the runner's deadline at
     the first card command + the cap - 120 s, so the end-stop is reached only when a block that started just before that deadline
     would run its anchors past the cap (KIT.md 4).
  4. THE HANG WATCH (departure D1: the lab's runner gives every device process a plain `timeout 10`, never a KILL): a host process of
     ours (an argument of its command line is the host's path, the command not `timeout`) still alive 12 s after this watch first saw
     it has outlived its timeout's TERM: STOP ("a device process ... not ending": it names the card), a line "<time> HUNG: ..." appended
     to the session log, the event logged, and NOTHING ELSE: no signal is sent, the card lock stays with the process's own descriptor,
     and the watch keeps reading until the session ends. The lane reports it to the owner (CARD-LANE-BRIEF.md 3).
Every event goes to <log dir>/watch.jsonl and stdout. It ends when OUT/SESSION_DONE appears (after a STOP it keeps only the hang watch).

    python3 -I -B watch_e197.py OUT --first EPOCH --cap S --host PATH --log-dir DIR --session-log FILE
            [--board-w 65] [--n 3] [--max-c 70] [--mhz 600] [--end-margin 30] [--hang-s 12] [--participants 1024]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys
import time

POLL_S = 0.25


class Tail:
    """New complete JSON object lines of a file that grows (a line that is not one whole object is skipped)."""

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
                    v = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(v, dict):
                    out.append(v)
        return out


def num(d, *keys):
    for k in keys:
        try:
            d = d[k]
        except (KeyError, IndexError, TypeError):
            return None
    if isinstance(d, bool) or not isinstance(d, (int, float)):
        return None
    return float(d)


def host_procs(host, me):
    """{pid: argv} of our processes running the host: its path is the command (argv[0]), or the script an interpreter runs (argv[1]
    or argv[2], a stand-in's form); a `timeout` process that names it is not one."""
    found = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            if os.stat("/proc/" + d).st_uid != me:
                continue
            with open("/proc/%s/cmdline" % d, "rb") as f:
                argv = [a.decode(errors="ignore") for a in f.read().split(b"\0") if a]
        except OSError:
            continue
        if not argv or os.path.basename(argv[0]) == "timeout":
            continue
        if host in argv[:3]:
            found[int(d)] = argv
    return found


def smoke_verdict(marks, runs, participants):
    """(ok, rows, reasons) over the smoke block's device processes and launch records."""
    devs = [m for m in marks if m.get("block") == "smoke" and m.get("kind") in ("anchor", "train")]
    bad, rows = [], []
    for m in devs:
        if m.get("kind") == "anchor":
            key = ("anchor", m.get("kind_run"))
            recs = [r for r in runs if r.get("block") == "smoke" and r.get("role") == "smoke_anchor"
                    and r.get("kind_run") == m.get("kind_run")]
            need = 2
        else:
            key = ("train", m.get("proc"))
            recs = [r for r in runs if r.get("block") == "smoke" and r.get("train") == "smoke" and r.get("proc") == m.get("proc")]
            need = 13
        nok = sum(1 for r in recs if r.get("ok") is True)
        nbad = sum(1 for r in recs if r.get("check_bad") != 0)
        parts = sorted({r.get("participants") for r in recs}, key=str)
        rows.append({"what": "%s %s" % key, "rc": m.get("rc"), "launches": len(recs), "ok": nok, "check_bad_lines": nbad,
                     "participants": parts})
        why = []
        if m.get("rc") != 0:
            why.append("exit %s" % m.get("rc"))
        if len(recs) < need:
            why.append("%d launches (< %d)" % (len(recs), need))
        if nok != len(recs):
            why.append("%d of %d launches not ok" % (len(recs) - nok, len(recs)))
        if nbad:
            why.append("check_bad on %d launches" % nbad)
        if participants and parts != [participants]:
            why.append("participants %s" % parts)
        if why:
            bad.append("%s %s: %s" % (key[0], key[1], ", ".join(why)))
    kinds = [m.get("kind") for m in devs]
    if kinds.count("anchor") != 3 or kinds.count("train") != 2:
        bad.append("the smoke block recorded %d anchors and %d train processes, not 3 and 2" % (kinds.count("anchor"), kinds.count("train")))
    return (not bad), rows, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--first", type=float, required=True, help="the sitting's first card command, epoch seconds")
    ap.add_argument("--cap", type=float, required=True, help="the sitting's cap in seconds, from the first card command")
    ap.add_argument("--host", required=True, help="the host's path as the session runs it")
    ap.add_argument("--log-dir", required=True)
    ap.add_argument("--session-log", required=True)
    ap.add_argument("--board-w", type=float, default=65.0)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--max-c", type=float, default=70.0)
    ap.add_argument("--mhz", type=float, default=600.0)
    ap.add_argument("--end-margin", type=float, default=30.0)
    ap.add_argument("--hang-s", type=float, default=12.0)
    ap.add_argument("--participants", type=int, default=1024)
    a = ap.parse_args()
    stop_file = os.path.join(a.out, "STOP")
    done_file = os.path.join(a.out, "SESSION_DONE")
    tt = Tail(os.path.join(a.out, "telemetry.jsonl"))
    tm, tr = Tail(os.path.join(a.out, "marks.jsonl")), Tail(os.path.join(a.out, "runs.jsonl"))
    marks, runs = [], []
    me = os.getuid()
    state = {"stopped": False, "smoke": None, "smoke_due": None}
    over, last_w, offclk = 0, None, 0
    seen = {}            # pid -> (first seen, argv)
    hung = set()
    end_at = a.first + a.cap - a.end_margin

    def event(kind, **kw):
        rec = dict(t_ms=int(time.time() * 1000), kind=kind, **kw)
        with open(os.path.join(a.log_dir, "watch.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print("watch_e197: " + json.dumps(rec), flush=True)

    def say(line):
        try:
            fd = os.open(a.session_log, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
            try:
                os.write(fd, (time.strftime("%Y-%m-%d %H:%M:%S %Z") + " " + line + "\n").encode())
            finally:
                os.close(fd)
        except OSError:
            pass

    def stop(why, card, **kw):
        wrote = False
        try:
            with open(stop_file, "x") as f:   # never over another writer's STOP: the first reason and time stand
                f.write(json.dumps({"by": "watch_e197", "why": why, "t_ms": int(time.time() * 1000), "card": card}) + "\n")
            wrote = True
        except FileExistsError:
            pass
        state["stopped"] = True
        event("stop", why=why, card=card, wrote=wrote, **kw)

    event("start", first=a.first, cap_s=a.cap, end_stop_at=time.strftime("%H:%M:%S %Z", time.localtime(end_at)),
          host=a.host, board_w=a.board_w, n=a.n, max_c=a.max_c, mhz=a.mhz, hang_s=a.hang_s, participants=a.participants)
    while True:
        if os.path.exists(done_file):
            event("session_done", hung=sorted(hung))
            return 0
        now = time.time()
        # 4. the hang watch: always, even after a STOP
        live = host_procs(a.host, me)
        for pid, argv in live.items():
            if pid not in seen:
                seen[pid] = (now, argv)
        for pid in list(seen):
            if pid not in live:
                del seen[pid]
                continue
            t0, argv = seen[pid]
            if now - t0 > a.hang_s and pid not in hung:
                hung.add(pid)
                why = ("a device process (pid %d) still runs %.0f s after it was first seen: its timeout's TERM did not end it; "
                       "nothing kills it (E197 departure D1)" % (pid, now - t0))
                say("HUNG: " + why + "; the card lock stays with its own descriptor; report to the owner")
                stop(why, True, pid=pid, argv=argv[:12])
        if os.path.exists(stop_file) and not state["stopped"]:
            try:
                txt = open(stop_file).read().strip()[:300]
            except OSError:
                txt = "?"
            state["stopped"] = True
            event("stop_seen", stop=txt)
        if not state["stopped"]:
            # 1. the kit's live stops
            for s in tt.read():
                w = num(s, "board_w")
                if w is not None and w != last_w:
                    last_w = w
                    over = over + 1 if w >= a.board_w else 0
                    if over >= a.n:
                        stop("board %.2f W at or above %g W on %d distinct readings in a row (the kit's stop)" % (w, a.board_w, over), True)
                        break
                t = num(s, "temp_c", "minshire", 0)
                if t is not None and t >= a.max_c:
                    stop("die reading %g C at or above %g C (the kit's stop)" % (t, a.max_c), True)
                    break
                m = num(s, "mhz", "minion")
                offclk = offclk + 1 if (m is None or abs(m - a.mhz) > 0.5) else 0
                if offclk >= a.n:
                    stop("minion clock %s, not %g MHz, on %d samples in a row (the kit's stop)" % (m, a.mhz, offclk), True)
                    break
        if not state["stopped"]:
            # 2. the kit's smoke check
            nm, nr = tm.read(), tr.read()
            marks += nm
            runs += nr
            if state["smoke"] is None:
                g = [m for m in marks if m.get("kind") == "smoke_gate"]
                if g:
                    if g[0].get("ok") is not True:
                        state["smoke"] = False
                        event("smoke_gate_failed", gate=g[0])
                    else:
                        if state["smoke_due"] is None:
                            state["smoke_due"] = now + 0.5     # its records were written before the gate mark; read once more
                        elif now >= state["smoke_due"]:
                            ok, rows, bad = smoke_verdict(marks, runs, a.participants)
                            state["smoke"] = ok
                            event("smoke_check", ok=ok, rows=rows, reasons=bad)
                            if ok:
                                say("the kit's smoke check: passed (every smoke launch ok, check_bad 0, %d participants; every smoke "
                                    "device process exit 0)" % a.participants)
                            else:
                                say("the kit's smoke check: FAILED: " + "; ".join(bad))
                                stop("the kit's smoke check failed: " + "; ".join(bad)[:400], True)
        if not state["stopped"] and now >= end_at:
            # 3. the end-stop
            stop("the end-stop: %.0f s before the cap (first card command + %.0f s); the launch in flight finishes" %
                 (a.end_margin, a.cap), False)
        time.sleep(POLL_S)


if __name__ == "__main__":
    sys.exit(main())
