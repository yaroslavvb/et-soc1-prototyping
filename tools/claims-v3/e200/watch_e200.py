#!/usr/bin/env python3
"""E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE KIT'S WATCH, run by session_e200.sh beside E197's reference
session (run_session.sh, stopwatch.py and E200's runner: E197's lab runner with W1, all unchanged). E197's watch (watch_e197.py, unchanged
beside it) ported to aifoundry2 card 0 under its governor (E200.md 4, C3, and 9). It opens no device, sends no command and signals no
process: it reads the session's own files (telemetry.jsonl, marks.jsonl, runs.jsonl in OUT) and /proc, and it acts only through the
registered stop file OUT/STOP, which run_trains.py checks before every device process and in every idle, and the host before every launch
(E197.md 9 and E200.md 19: "The kit may add stops and gates that end a sitting early, named so; it never changes a train, a kind, a value,
the order, a window, a threshold, a cap, the reduction or the comparison"). Every STOP it writes is one JSON line {"by": "watch_e200",
"why", "t_ms", "card"} (the first writer's STOP stands: it never writes over another's). Its watches:

  1. THE KIT'S LIVE STOPS (E197.md 9, "the box's, the kit's"; E200.md 9), on the session's own telemetry: board power AT OR ABOVE 65 W on
     three distinct readings in a row (a sample that repeats the previous board value is the same reading of the meter: it neither counts
     nor resets the run, the stopwatch's rule); a die reading (temp_c.minshire[0]) at or above 70 C; and AIFOUNDRY2'S OWN LINES beside
     them (E194.md 11, E190 arm A's on this card): board strictly ABOVE 85 W on 3 samples in a row (a sample with no board reading starts
     the count again), or the shires' mean minshire[0] or the latch minshire[2] at or above 80 C. E189's lines bind first. E197's watch's
     third stop (a minion clock other than 600 MHz on three samples in a row) is GONE: under this card's governor the clock reads 600 MHz
     at rest and 800 MHz under load; C3 below replaces it (E200.md 4).
  2. C3, THE CLOCK LIVE (E200.md 4): each train process of a block of trains.tsv (its mark "train" and its REGFILE records in runs.jsonl,
     the smoke's apart) is judged once its 13 launch records are in and the telemetry has reached its last launch's end (E197's runner
     writes a process's mark BEFORE its records: a mark with fewer than 13 is read again each poll until all 13 are in, a later mark shows
     the runner past it, or 3 s pass; fix-e200, before any datum): its samples from its first launch's start + 1.5 s
     to its last launch's end must read 800 MHz within 1 MHz (mhz.minion; a sample with no clock field is not judged, as in C1). A process
     whose samples leave 800 MHz there is OFF; three OFF processes in a row end the sitting (STOP, naming the card: "the card is not
     holding the registered clock"). A process with no launch record or no sample in that window is not judged: it neither counts nor
     resets the run. (The reduction's C1, reduce_e200.py, sets each OFF process aside by its own count as well; nothing here re-runs one.)
  3. THE KIT'S SMOKE CHECK (E197's kit's, with the smoke's clock, E200.md 4 C3): once the smoke block's gate mark is written with ok true,
     every smoke launch record must read "ok" true, "check_bad" 0 and 1,024 participants, every smoke device process must have exited 0
     with at least two launches (a 1 s burst) or 13 (a train process), AND BOTH SMOKE TRAIN PROCESSES MUST HOLD THE CLOCK RULE: every
     sample from the first launch's start + 1.5 s to the last launch's end at 800 MHz within 1 MHz (at least one sample there), and the
     last launch at 780-810 MHz by its own count (cycles_max / wall_s; E200.md 15: a different overhead on this box's build shows here);
     else STOP within block A's first 10 s idle, before its first device process (a gate stop: no train, E200.md 13).
  4. THE END-STOP (E197.md 10): at the first card command + the cap - 30 s, if the session still runs, STOP (not naming the card).
  5. THE HANG WATCH (departure D1: every device process under a plain `timeout 10`, never a KILL): a host process of ours still alive 12 s
     after this watch first saw it has outlived its timeout's TERM: STOP (naming the card), a line "<time> HUNG: ..." appended to the
     session log, and NOTHING ELSE: no signal is sent, the card lock stays with the process's own descriptor. The lane reports it.
Every event goes to <log dir>/watch.jsonl and stdout; each judged train process is one "clock" event (its window, samples, off samples,
the verdict). It ends when OUT/SESSION_DONE appears (after a STOP it keeps only the hang watch).

    python3 -I -B watch_e200.py OUT --first EPOCH --cap S --host PATH --log-dir DIR --session-log FILE
            [--board-w 65] [--n 3] [--max-c 70] [--hi-w 85] [--hi-n 3] [--hi-c 80] [--mhz 800] [--tol-mhz 1] [--allow-ms 1500]
            [--own-lo 780] [--own-hi 810] [--c3-n 3] [--end-margin 30] [--hang-s 12] [--participants 1024]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import json
import os
import sys
import time

POLL_S = 0.25
TRAIN_BLOCKS = ("A", "B", "C", "D", "E")
LAUNCHES = 13


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


def own_mhz(r):
    """a launch's clock by its own count: its slowest hart's cycles over its wall seconds (reduce_e200.own_mhz's arithmetic)"""
    c, w = num(r, "cycles_max"), num(r, "wall_s")
    if c is None or w is None or c <= 0 or w <= 0:
        return None
    return c / w / 1e6


class Clock:
    """the session's telemetry clock samples, by time: (t_ms, mhz or None)"""

    def __init__(self):
        self.ts, self.mhz, self.latest = [], [], 0

    def add(self, s):
        t = num(s, "t_ms")
        if t is None:
            return
        m = num(s, "mhz", "minion")
        i = bisect.bisect_right(self.ts, t)
        self.ts.insert(i, t)
        self.mhz.insert(i, m)
        self.latest = max(self.latest, t)

    def window(self, t0, t1):
        i0, i1 = bisect.bisect_left(self.ts, t0), bisect.bisect_right(self.ts, t1)
        return [m for m in self.mhz[i0:i1] if m is not None]


def process_records(runs, block, train, proc):
    return sorted((r for r in runs if r.get("block") == block and r.get("train") == train and r.get("proc") == proc
                   and num(r, "t_start_ms") is not None and num(r, "t_end_ms") is not None),
                  key=lambda r: (num(r, "launch") if num(r, "launch") is not None else -1))


def clock_rule(clock, recs, mhz, tol, allow_ms):
    """(window, samples judged, off samples, off values) for one process's records under THE CLOCK RULE's sample clause"""
    lo = min(num(r, "t_start_ms") for r in recs)
    hi = max(num(r, "t_end_ms") for r in recs)
    vals = clock.window(lo + allow_ms, hi)
    off = [m for m in vals if abs(m - mhz) > tol]
    return (lo, hi), len(vals), len(off), sorted(set(off))


def smoke_verdict(marks, runs, participants, clock, a):
    """(ok, rows, reasons) over the smoke block's device processes and launch records, with the smoke trains' clock (C3)."""
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
        row = {"what": "%s %s" % key, "rc": m.get("rc"), "launches": len(recs), "ok": nok, "check_bad_lines": nbad,
               "participants": parts}
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
        if key[0] == "train" and recs:
            timed = [r for r in recs if num(r, "t_start_ms") is not None and num(r, "t_end_ms") is not None]
            if len(timed) != len(recs):
                why.append("a launch record without its span")
            else:
                (lo, hi), n, noff, offv = clock_rule(clock, timed, a.mhz, a.tol_mhz, a.allow_ms)
                last = max(timed, key=lambda r: num(r, "launch") if num(r, "launch") is not None else -1)
                f = own_mhz(last)
                row.update(clock_samples=n, clock_off=noff, clock_off_values=offv, last_launch_own_mhz=f)
                if n == 0:
                    why.append("the clock: no telemetry sample from its first launch + %.1f s to its last launch's end (C3)" % (a.allow_ms / 1000.0))
                elif noff:
                    why.append("the clock: %d of %d samples from its first launch + %.1f s read %s MHz, not %g (C3)"
                               % (noff, n, a.allow_ms / 1000.0, offv, a.mhz))
                if f is None or not (a.own_lo <= f <= a.own_hi):
                    why.append("the clock: its last launch ran at %s MHz by its own count, not %g-%g (C3)"
                               % ("none" if f is None else "%.1f" % f, a.own_lo, a.own_hi))
        rows.append(row)
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
    ap.add_argument("--hi-w", type=float, default=85.0)
    ap.add_argument("--hi-n", type=int, default=3)
    ap.add_argument("--hi-c", type=float, default=80.0)
    ap.add_argument("--mhz", type=float, default=800.0)
    ap.add_argument("--tol-mhz", type=float, default=1.0)
    ap.add_argument("--allow-ms", type=float, default=1500.0)
    ap.add_argument("--own-lo", type=float, default=780.0)
    ap.add_argument("--own-hi", type=float, default=810.0)
    ap.add_argument("--c3-n", type=int, default=3)
    ap.add_argument("--end-margin", type=float, default=30.0)
    ap.add_argument("--hang-s", type=float, default=12.0)
    ap.add_argument("--participants", type=int, default=1024)
    a = ap.parse_args()
    stop_file = os.path.join(a.out, "STOP")
    done_file = os.path.join(a.out, "SESSION_DONE")
    tt = Tail(os.path.join(a.out, "telemetry.jsonl"))
    tm, tr = Tail(os.path.join(a.out, "marks.jsonl")), Tail(os.path.join(a.out, "runs.jsonl"))
    marks, runs = [], []
    clock = Clock()
    me = os.getuid()
    state = {"stopped": False, "smoke": None, "smoke_due": None}
    over, last_w, hi_run = 0, None, 0
    c3_run = 0
    judged = 0                # train marks judged (or passed over) so far, in mark order
    pend_since = {}           # mark index -> when it was first seen waiting for its telemetry
    seen = {}                 # pid -> (first seen, argv)
    hung = set()
    end_at = a.first + a.cap - a.end_margin

    def event(kind, **kw):
        rec = dict(t_ms=int(time.time() * 1000), kind=kind, **kw)
        with open(os.path.join(a.log_dir, "watch.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print("watch_e200: " + json.dumps(rec), flush=True)

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
                f.write(json.dumps({"by": "watch_e200", "why": why, "t_ms": int(time.time() * 1000), "card": card}) + "\n")
            wrote = True
        except FileExistsError:
            pass
        state["stopped"] = True
        event("stop", why=why, card=card, wrote=wrote, **kw)

    event("start", first=a.first, cap_s=a.cap, end_stop_at=time.strftime("%H:%M:%S %Z", time.localtime(end_at)), host=a.host,
          board_w=a.board_w, n=a.n, max_c=a.max_c, hi_w=a.hi_w, hi_n=a.hi_n, hi_c=a.hi_c, mhz=a.mhz, tol_mhz=a.tol_mhz,
          allow_ms=a.allow_ms, own_lo=a.own_lo, own_hi=a.own_hi, c3_n=a.c3_n, hang_s=a.hang_s, participants=a.participants)
    while True:
        if os.path.exists(done_file):
            event("session_done", hung=sorted(hung), train_processes_judged=judged)
            return 0
        now = time.time()
        # 5. the hang watch: always, even after a STOP (our processes running the host: its path is argv[0], or the script an
        #    interpreter runs, argv[1] or argv[2], a stand-in's form; a `timeout` process that names it is not one)
        live = {}
        for d in os.listdir("/proc"):
            if not d.isdigit():
                continue
            try:
                if os.stat("/proc/" + d).st_uid != me:
                    continue
                with open("/proc/%s/cmdline" % d, "rb") as f:
                    argv = [x.decode(errors="ignore") for x in f.read().split(b"\0") if x]
            except OSError:
                continue
            if not argv or os.path.basename(argv[0]) == "timeout":
                continue
            if a.host in argv[:3]:
                live[int(d)] = argv
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
            # 1. the kit's live stops: E189's lines first, then aifoundry2's own
            for s in tt.read():
                clock.add(s)
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
                hi_run = hi_run + 1 if (w is not None and w > a.hi_w) else 0
                if hi_run >= a.hi_n:
                    stop("board %.2f W above %g W on %d samples in a row (aifoundry2's own line, E194.md 11)" % (w, a.hi_w, hi_run), True)
                    break
                latch = num(s, "temp_c", "minshire", 2)
                if (t is not None and t >= a.hi_c) or (latch is not None and latch >= a.hi_c):
                    stop("die reading minshire[0] %s C, the latch minshire[2] %s C: at or above %g C (aifoundry2's own line, E194.md 11)"
                         % (t, latch, a.hi_c), True)
                    break
        if not state["stopped"]:
            nm, nr = tm.read(), tr.read()
            marks += nm
            runs += nr
            # 2. C3: the train processes of the blocks of trains.tsv, in mark order, each once its records and its telemetry are in.
            #    E197's lab runner writes a process's mark BEFORE its REGFILE records (device(): the mark, then one line a record): a
            #    mark is judged only once its 13 records are in, or a later mark shows the runner past it, or 3 s on from when this
            #    watch first waited on it (fix-e200, before any datum: verify-e200's F2)
            tmarks = [(i, m) for i, m in enumerate(marks) if m.get("kind") == "train" and m.get("block") in TRAIN_BLOCKS]
            while judged < len(tmarks) and not state["stopped"]:
                mi, m = tmarks[judged]
                recs = process_records(runs, m.get("block"), m.get("train"), m.get("proc"))
                waited = now - pend_since.setdefault(judged, now)
                if len(recs) < LAUNCHES and len(marks) <= mi + 1 and waited < 3.0:
                    break   # its records are not all in yet: read again next poll (at most 3 s)
                if not recs:
                    event("clock", block=m.get("block"), train=m.get("train"), proc=m.get("proc"), verdict="not judged",
                          why="no launch record", run=c3_run)
                    judged += 1
                    continue
                hi = max(num(r, "t_end_ms") for r in recs)
                if clock.latest < hi and waited < 3.0:
                    break   # its telemetry is not in yet: read again next poll (at most 3 s)
                (lo, hi), n, noff, offv = clock_rule(clock, recs, a.mhz, a.tol_mhz, a.allow_ms)
                if n == 0:
                    verdict = "not judged"
                elif noff:
                    verdict = "OFF"
                    c3_run += 1
                else:
                    verdict = "800"
                    c3_run = 0
                event("clock", block=m.get("block"), train=m.get("train"), proc=m.get("proc"), window_ms=[lo + a.allow_ms, hi],
                      samples=n, off=noff, off_values=offv, launches=len(recs), verdict=verdict, run=c3_run, waited_s=round(waited, 2))
                judged += 1
                if c3_run >= a.c3_n:
                    say("C3: %d train processes in a row off %g MHz after their first %.1f s (the last: %s %s process %s, %s MHz): the "
                        "card is not holding the registered clock (E200.md 4): STOP" % (c3_run, a.mhz, a.allow_ms / 1000.0, m.get("block"),
                                                                                     m.get("train"), m.get("proc"), offv))
                    stop("the clock (C3): %d train processes in a row off %g MHz after their first %.1f s (the last: block %s %s "
                         "process %s read %s MHz)" % (c3_run, a.mhz, a.allow_ms / 1000.0, m.get("block"), m.get("train"),
                                                      m.get("proc"), offv), True)
            # 3. the kit's smoke check, with the smoke's clock
            if state["smoke"] is None and not state["stopped"]:
                g = [m for m in marks if m.get("kind") == "smoke_gate"]
                if g:
                    if g[0].get("ok") is not True:
                        state["smoke"] = False
                        event("smoke_gate_failed", gate=g[0])
                    else:
                        if state["smoke_due"] is None:
                            state["smoke_due"] = now + 0.5     # its records were written before the gate mark; read once more
                        else:
                            ends = [num(r, "t_end_ms") for r in runs if r.get("block") == "smoke" and r.get("train") == "smoke"
                                    and num(r, "t_end_ms") is not None]
                            tel_in = not ends or clock.latest >= max(ends) or now >= state["smoke_due"] + 3.0
                            if now >= state["smoke_due"] and tel_in:
                                ok, rows, bad = smoke_verdict(marks, runs, a.participants, clock, a)
                                state["smoke"] = ok
                                event("smoke_check", ok=ok, rows=rows, reasons=bad)
                                if ok:
                                    say("the kit's smoke check: passed (every smoke launch ok, check_bad 0, %d participants; every smoke "
                                        "device process exit 0; both smoke train processes at %g MHz from their first launch + %.1f s "
                                        "and their last launch at %g-%g MHz by its own count)" % (a.participants, a.mhz,
                                                                                               a.allow_ms / 1000.0, a.own_lo, a.own_hi))
                                else:
                                    say("the kit's smoke check: FAILED: " + "; ".join(bad))
                                    stop("the kit's smoke check failed: " + "; ".join(bad)[:400], True)
        if not state["stopped"] and now >= end_at:
            # 4. the end-stop
            stop("the end-stop: %.0f s before the cap (first card command + %.0f s); the launch in flight finishes" %
                 (a.end_margin, a.cap), False)
        time.sleep(POLL_S)


if __name__ == "__main__":
    sys.exit(main())
