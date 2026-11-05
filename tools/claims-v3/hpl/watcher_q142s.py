#!/usr/bin/env python3
"""Q142(s): run_hpl.py's telemetry watcher without the follow() race. A new kit file beside run_hpl.py, which stays as committed
(1a899d8f, 23 Oct 2026; sha256 68493295...f227) and is never edited. The dated amendment is run_hpl.py.dated-note.md beside this file.

THE RACE (E165's D2, docs/reports/data/2026-11-04-e165-blind7-aifoundry2/README.md). run_hpl.py's Watcher.run() reads self.path and
self.pos outside its lock, while Watcher.follow(), called by Session.start_sampler at every run boundary, resets both under the lock.
A follow() that lands after run() has read the old path and before it has read the old file leaves run() reading the OLD file from
the NEW position 0: it re-reads the whole old file, adds its length to the new file's position, and stamps the old file's last line
as a fresh reading. The watcher then reads nothing from the new file until that file grows past the old one's length; for up to
3 s the gates see the previous run's last reading as live, and run_hpl.py's guard ends the session with error:telemetry_stale 8 s
into the sampler (fail-safe: the stops are blind for at most about 5-8 s, or a whole launch if the gate passes on the stale reading).
A follow() that lands between the file read and the position update instead moves the new file's position by the old chunk's length.

THE FIX. One rule: what an iteration of run() reads is applied only if no follow() came after the iteration took its snapshot.
run() takes (path, pos, generation, over) under the lock, reads the file at that position outside it, and then, under the lock
again, applies the new position and the readings only if the generation is unchanged; follow() bumps the generation under the
lock. A chunk read across a follow() is never a reading of the new file and never moves its position, but its lines still go
through the same safety checks (they are the old run's genuinely unread lines, read from the old position: the old code's
coverage of every line is kept). Nothing else changes: the same parse (run_hpl.parse_tel), the same stops (safety.abs_stop_c on
the die mean or the hottest sensor on one sample; board_w over safety.board_cap_w on cap_consecutive samples), the same fire()
(the stop-file and a safety_trip mark), the same 50 ms loop, follow() still reads a new file from its start, snapshot() and
reading() unchanged. It sends no device command and opens no device: it reads the sampler's file (dmcmd_audit: 0 send sites).

USE (a run registered after the amendment; no past run changes):

    sys.path.insert(0, os.path.join(<tools/claims-v3>, "hpl"))
    import watcher_q142s
    rec = watcher_q142s.install(H)      # H = the imported run_hpl module (R119.H, RE.H, R84.H ...), before any Session is built
    # record rec in the session's own record (e.g. its eNNN.json); list this file in the run's frozen hashes and its dmcmd_audit set

install() refuses (RuntimeError, before anything opens a device) a run_hpl module whose file is not the committed run_hpl.py, or
whose Watcher is not run_hpl's, and is idempotent. Session.__init__ builds `Watcher(self)` from run_hpl's module namespace, so
replacing H.Watcher there is what every later Session uses. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import time

RUN_HPL_SHA256 = "68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227"   # tools/claims-v3/hpl/run_hpl.py at 1a899d8f
AMENDMENT = "tools/claims-v3/hpl/run_hpl.py.dated-note.md"
THIS = "tools/claims-v3/hpl/watcher_q142s.py"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_watcher(H):
    """The fixed watcher class for an imported run_hpl module H: a subclass of H's own Watcher, with follow() and run() replaced."""
    base = H.Watcher

    class Watcher(base):
        """run_hpl.py's Watcher, with the generation rule of watcher_q142s.py (Q142(s)): see the module docstring."""
        _q142s = True

        def __init__(self, sess):
            super().__init__(sess)
            self.gen = 0

        def follow(self, path):
            with self.lock:
                self.gen += 1
                self.path, self.pos, self.over = path, 0, 0
                self.last, self.last_host_ms = None, 0

        def run(self):
            sf = self.s.proto.get("safety", {})
            stop_c = H.num(sf.get("abs_stop_c", 85))
            cap_w = H.num(sf.get("board_cap_w", 97))
            need = int(sf.get("cap_consecutive", 3))
            while not self.stop_flag.is_set():
                with self.lock:
                    path, pos, gen, over = self.path, self.pos, self.gen, self.over
                try:
                    chunk = b""
                    if path and os.path.exists(path):
                        with open(path, "rb") as f:
                            f.seek(pos)
                            chunk = f.read()
                    nl = chunk.rfind(b"\n")
                    if nl >= 0:
                        parsed = []
                        for ln in chunk[:nl].splitlines():
                            if not ln.startswith(b"{"):
                                continue
                            t = H.parse_tel(ln)
                            if t is not None:
                                parsed.append(t)
                        why = None
                        with self.lock:
                            current = self.gen == gen          # no follow() since the snapshot: this chunk is the followed file's
                            o = self.over if current else over
                            for t in parsed:
                                _, die, high, w, _ = t
                                hot = [x for x in (die, high) if x is not None and x >= stop_c]
                                if hot and why is None:
                                    why = f"die {max(hot):.0f} C >= {stop_c:g} C"
                                if w is not None and w > cap_w:
                                    o += 1
                                    if o >= need and why is None:
                                        why = f"board {w:.1f} W > {cap_w:g} W on {need} samples"
                                else:
                                    o = 0
                                if current:
                                    self.last, self.last_host_ms = t, H.now_ms()
                            if current:
                                self.pos = pos + nl + 1
                                self.over = o
                        if why is not None and not self.trip:
                            self.fire(why)
                except OSError:
                    pass
                time.sleep(0.05)

    Watcher.__qualname__ = "Watcher"
    return Watcher


def record(H):
    """What a runner writes into its own session record: which watcher ran, by file and hash."""
    here = os.path.abspath(__file__)
    return {"watcher": THIS, "watcher_sha256": sha256_of(here), "amendment": AMENDMENT,
            "run_hpl_sha256": sha256_of(H.__file__), "installed": bool(getattr(H.Watcher, "_q142s", False))}


def install(H):
    """Replace H.Watcher with the fixed class. Refuses a run_hpl module that is not the committed file. Idempotent."""
    if getattr(H.Watcher, "_q142s", False):
        return record(H)
    got = sha256_of(H.__file__)
    if got != RUN_HPL_SHA256:
        raise RuntimeError(f"watcher_q142s: {H.__file__} is not the committed run_hpl.py (sha256 {got[:12]}, want {RUN_HPL_SHA256[:12]}): "
                           "the fix is written and tested against that file only; nothing installed")
    for name in ("Session", "Watcher", "parse_tel", "num", "now_ms"):
        if not hasattr(H, name):
            raise RuntimeError(f"watcher_q142s: the module has no {name}: not run_hpl; nothing installed")
    if H.Watcher.__module__ != H.__name__:
        raise RuntimeError("watcher_q142s: the module's Watcher is not its own (another patch came first): nothing installed")
    H.Watcher = make_watcher(H)
    return record(H)


if __name__ == "__main__":
    print(__doc__)
