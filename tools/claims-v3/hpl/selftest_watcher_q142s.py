#!/usr/bin/env python3
"""Q142(s): the self-test of watcher_q142s.py. It forces a Watcher.follow() between the watcher's read of its path and its read of the
file, and shows that run_hpl.py's committed Watcher fails and the new one passes. Desk only: no device, no lock, no ssh; run_hpl.py
is imported unchanged (its --dry toy card drives the end-to-end cases). Every file it writes is under the scratch dir it is given.

    python3 -B tools/claims-v3/hpl/selftest_watcher_q142s.py <a new, empty scratch dir> > tools/claims-v3/hpl/selftest-watcher-q142s.txt

How the interleaving is forced, deterministically: the watcher's run() calls open() by its module's global name, so the test sets
<that module>.open to a hook for the length of a case. The hook passes every call through except the watcher thread's first binary
read of the followed (old) file after the case arms it, and at that call it does what the case names, in the watcher thread itself:
  path-read     follow(<new file>) after run() has read self.path and before it opens and reads the file (the race E165's D2 names);
  read-update   follow(<new file>) inside the file's read(), after the bytes are read and before run() applies its position.
In the end-to-end cases the session's own follow() (Session.start_sampler's, of the second run's file) first waits, at most 2 s,
until the watcher thread has read its path (still the first run's file) and sits in the hooked open(); the hook then waits, at most
10 s, until that follow() has returned, and only then opens and reads the file. So the session's real follow() lands between the
path read and the file read. (Without the handshake a dry session's follow() comes within the watcher's 50 ms sleep, because the
toy card's queries take no time; on a card they take seconds, and the race is a ~30 us window of each 50 ms loop.)

Cases (each run on the committed class OLD and on the new class NEW):
  W1  path-read, the old file fully read: a reading of the new file arrives within 2.5 s, and no old-file reading shows after follow().
      Expected: OLD fails (its position is left at the old file's length, and the old file's last line is stamped fresh); NEW passes.
  W2  read-update, with unread lines in the old file: the same two checks, and the position ends at the new file's end.
      Expected: OLD fails (the old chunk's length is added to the new file's position); NEW passes.
  W3  path-read, the old file's unread tail holding a sample at the die stop: the stop still fires (the fix keeps the old code's
      coverage of every line), and that sample is never the new file's reading. Expected: NEW passes; OLD fires but shows the old
      sample as the new file's reading.
  W4  the control: a follow() at a quiet moment, no hook. Expected: both pass (the harness alone fails neither).
  W5a end to end, a dry run_hpl Session of two runs, the second run's cool gate below the first run's last die: the session must run
      to "done". Expected: OLD ends error:telemetry_stale in the second run's cool gate, about 8 s into its sampler, before any launch
      (E165's signature, run 159); NEW runs to "done".
  W5b end to end, the second run's gate above the first run's last die: the gate must read the second run's own telemetry.
      Expected: OLD's gate admits the launch on the first run's last reading (the stops then blind for the launch); NEW reads its own.
  W6  install(): it replaces run_hpl's Watcher so a Session built after it holds the new class; it is idempotent; it refuses a
      run_hpl.py whose bytes differ from the committed file.
Exit 0 only if every expectation holds, the "OLD fails" ones included. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import builtins
import json
import os
import shutil
import sys
import threading
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hpl as H  # noqa: E402  (the committed file, imported, never edited)
import watcher_q142s as WQ  # noqa: E402

OLD = H.Watcher
NEW = WQ.make_watcher(H)
results = []


def check(ok, what):
    results.append(bool(ok))
    print(f"{'ok  ' if ok else 'FAIL'} {what}", flush=True)
    return bool(ok)


def tline(t_ms, die=50.0, w=30.0):
    return json.dumps({"t_ms": t_ms, "took_ms": 22, "board_w": w, "temp_c": {"minshire": [die, die - 3.0, die + 3.0]},
                       "mhz": {"minion": 600}}) + "\n"


class FakeSess:
    def __init__(self, d):
        self.proto = {"safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3}}
        self.stop_file = os.path.join(d, "STOP")
        self.marks = []

    def touch(self, p):
        with builtins.open(p, "a"):
            pass

    def mark(self, kind, detail="", **kw):
        self.marks.append((kind, detail))


class ReadThenFollow:
    def __init__(self, f, hook):
        self.f, self.h = f, hook

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.f.close()

    def seek(self, *a):
        return self.f.seek(*a)

    def read(self, *a):
        data = self.f.read(*a)
        self.h.w.follow(self.h.new)
        self.h.fired.set()
        return data


class Hook:
    """<module>.open for one case: the watcher thread's first binary read of `old` after arm() does `where`."""

    def __init__(self, cls, watcher, old, new, where, need_unread=False, wait_follow=None):
        self.mod = sys.modules[cls.run.__module__]
        self.w, self.old, self.new, self.where = watcher, old, new, where
        self.need_unread, self.wait_follow = need_unread, wait_follow
        self.armed, self.fired, self.inside = threading.Event(), threading.Event(), threading.Event()

    def __enter__(self):
        self.mod.open = self.open
        return self

    def __exit__(self, *a):
        self.mod.__dict__.pop("open", None)

    def open(self, path, mode="r", *a, **kw):
        if (self.armed.is_set() and threading.current_thread() is self.w and path == self.old and "b" in mode and "r" in mode
                and (not self.need_unread or os.path.getsize(path) > self.w.pos)):
            self.armed.clear()
            if self.where == "path-read":
                self.w.follow(self.new)
                self.fired.set()
                return builtins.open(path, mode, *a, **kw)
            if self.where == "session":          # the session's own follow() lands here, then the file is read
                self.inside.set()
                self.wait_follow.wait(10)
                self.fired.set()
                return builtins.open(path, mode, *a, **kw)
            return ReadThenFollow(builtins.open(path, mode, *a, **kw), self)
        return builtins.open(path, mode, *a, **kw)


def wait_for(cond, secs):
    t = time.time() + secs
    while time.time() < t:
        if cond():
            return True
        time.sleep(0.01)
    return cond()


def unit(cls, name, where, d, unread=0, hot=False):
    """One unit case; returns (new_seen, old_after, pos_ok, tripped)."""
    os.makedirs(d)
    old, new = os.path.join(d, "old.jsonl"), os.path.join(d, "new.jsonl")
    with builtins.open(old, "w") as f:
        for i in range(200):
            f.write(tline(1000 + i))
    with builtins.open(new, "w") as f:
        for i in range(5):
            f.write(tline(5000 + i, die=52.0))
    s = FakeSess(d)
    w = cls(s)
    w.follow(old)
    w.start()
    if not wait_for(lambda: (w.snapshot()[0] or (0,))[0] == 1199, 3):
        w.stop_flag.set()
        return None
    seen_new, old_after = False, False
    if where is None:                                      # W4, the control: a follow() at a quiet moment
        time.sleep(0.3)
        w.follow(new)
        fired = True
    else:
        with Hook(cls, w, old, new, where, need_unread=bool(unread)) as hk:
            hk.armed.set()
            if unread:                                     # one write, so the hook never fires on half of the tail
                tail = "".join(tline(1200 + i, die=(90.0 if hot and i == unread - 1 else 50.0)) for i in range(unread))
                fd = os.open(old, os.O_WRONLY | os.O_APPEND)
                try:
                    os.write(fd, tail.encode())
                finally:
                    os.close(fd)
            fired = hk.fired.wait(3)
            t_end = time.time() + 2.5
            while time.time() < t_end:
                last = w.snapshot()[0]
                if last is not None:
                    if last[0] >= 5000:
                        seen_new = True
                    else:
                        old_after = True
                time.sleep(0.01)
    if where is None:
        t_end = time.time() + 2.5
        while time.time() < t_end:
            last = w.snapshot()[0]
            if last is not None:
                if last[0] >= 5000:
                    seen_new = True
                else:
                    old_after = True
            time.sleep(0.01)
    pos_ok = w.pos == os.path.getsize(new)
    w.stop_flag.set()
    w.join(2)
    tripped = bool(w.trip) and os.path.exists(s.stop_file)
    return {"fired": bool(fired), "new_seen": seen_new, "old_after": old_after, "pos_ok": pos_ok, "tripped": tripped,
            "pos": w.pos, "new_size": os.path.getsize(new), "trip": w.trip}


PROTO = {
    "experiment": "Q142s-selftest", "order_seed": 1,
    "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3},
    "sampler": {"every_ms": 100},
    "blocks": [
        {"name": "LONG", "runs": [{"type": "fp32", "values": "randn", "launch": {"seconds": 6, "budget": 7.5, "processes": 2},
                                   "tail_s": 2, "start": {"mode": "cool", "max_c": 60, "max_wait_s": 30}}]},
        {"name": "NEXT", "runs": [{"type": "fp32", "values": "zeros", "launch": {"seconds": 1, "budget": 2.5, "processes": 1},
                                   "tail_s": 1, "start": {"mode": "cool", "max_c": None, "max_wait_s": 40}}]},
    ],
}


def first_t(path):
    with builtins.open(path) as f:
        for ln in f:
            if ln.startswith("{"):
                return json.loads(ln)["t_ms"]
    return None


def session(cls, d, gate_c):
    """A dry run_hpl Session of two runs with `cls` as its watcher; the second run's follow() forced into the race."""
    os.makedirs(d)
    proto = json.loads(json.dumps(PROTO))
    proto["blocks"][1]["runs"][0]["start"]["max_c"] = gate_c
    pp = os.path.join(d, "protocol.json")
    json.dump(proto, builtins.open(pp, "w"))
    raw, runs, bad = H.load_protocol(pp)
    assert not bad, bad
    a = types.SimpleNamespace(dry=True, root=os.path.normpath(os.path.join(HERE, "..", "..", "..")), out=os.path.join(d, "run"),
                              max_card_min=3.0)
    saved = H.Watcher
    H.Watcher = cls
    try:
        s = H.Session(a, raw, runs)
    finally:
        H.Watcher = saved
    followed = threading.Event()
    stops = [0]
    gate_seen = {}
    orig_follow, orig_stop, orig_gate = s.watcher.follow, s.stop_sampler, s.gate
    hook = Hook(cls, s.watcher, None, None, "session", wait_follow=followed)

    def follow(path):
        # Session.start_sampler's follow() of the second run's file waits (at most 2 s; the watcher loops every 50 ms) until the
        # watcher thread has read its path, the first run's file, and sits in the hooked open(): so it lands between the two reads
        race = threading.current_thread() is not s.watcher and hook.old is not None and path != hook.old and not followed.is_set()
        if race:
            hook.inside.wait(2)
        orig_follow(path)
        if race:
            followed.set()

    def stop_sampler():
        orig_stop()
        stops[0] += 1
        if stops[0] == 1:                      # the first run's sampler has stopped: arm at its file
            hook.old = s.watcher.path
            hook.armed.set()

    def gate(r):
        g = orig_gate(r)
        gate_seen[r.name] = s.watcher.snapshot()[0]
        return g

    s.watcher.follow, s.stop_sampler, s.gate = follow, stop_sampler, gate
    out = open(os.path.join(d, "stdout.txt"), "w")
    so = sys.stdout
    sys.stdout = out
    t0 = time.time()
    try:
        with hook:
            code = s.run()
    finally:
        sys.stdout = so
        out.close()
    secs = time.time() - t0
    end = json.load(builtins.open(os.path.join(a.out, "end.json")))
    tels = sorted(os.listdir(os.path.join(a.out, "tel")))
    nxt = [t for t in tels if t.startswith("NEXT")]
    nxt_first = first_t(os.path.join(a.out, "tel", nxt[0])) if nxt else None
    g = gate_seen.get(runs[1].name)
    return {"code": code, "reason": end["reason"], "fired": hook.fired.is_set(), "secs": round(secs, 1),
            "into_sampler_s": round((end["t_end_ms"] - nxt_first) / 1000.0, 1) if nxt_first else None,
            "gate_t": g[0] if g else None, "next_first_t": nxt_first}


def main():
    T = sys.argv[1] if len(sys.argv) > 1 else None
    if not T:
        sys.exit("usage: selftest_watcher_q142s.py <a new, empty scratch dir>")
    if os.path.isdir(T) and os.listdir(T):
        sys.exit(f"refused: {T} is not empty")
    os.makedirs(T, exist_ok=True)
    print("# Q142(s) watcher self-test: watcher_q142s.py against run_hpl.py's committed Watcher, desk only (no device, no ssh)")
    print(f"# run_hpl.py sha256 {WQ.sha256_of(H.__file__)} (committed {WQ.RUN_HPL_SHA256 == WQ.sha256_of(H.__file__)}); "
          f"watcher_q142s.py sha256 {WQ.sha256_of(WQ.__file__)}")
    t_all = time.time()
    exp = {}
    for label, cls in (("OLD", OLD), ("NEW", NEW)):
        print(f"\n== {label}: {cls.__module__}.{cls.__qualname__}")
        r1 = unit(cls, "W1", "path-read", os.path.join(T, f"w1-{label}"))
        r2 = unit(cls, "W2", "read-update", os.path.join(T, f"w2-{label}"), unread=10)
        r3 = unit(cls, "W3", "path-read", os.path.join(T, f"w3-{label}"), unread=10, hot=True)
        r4 = unit(cls, "W4", None, os.path.join(T, f"w4-{label}"))
        for nm, r in (("W1", r1), ("W2", r2), ("W3", r3), ("W4", r4)):
            print(f"   {nm}: {json.dumps(r)}")
        good1 = bool(r1 and r1["fired"] and r1["new_seen"] and not r1["old_after"])
        good2 = bool(r2 and r2["fired"] and r2["new_seen"] and not r2["old_after"] and r2["pos_ok"])
        good3 = bool(r3 and r3["fired"] and r3["tripped"] and not r3["old_after"])
        good4 = bool(r4 and r4["new_seen"] and not r4["old_after"] and r4["pos_ok"])
        s5a = session(cls, os.path.join(T, f"w5a-{label}"), 55)
        s5b = session(cls, os.path.join(T, f"w5b-{label}"), 79)
        print(f"   W5a: {json.dumps(s5a)}")
        print(f"   W5b: {json.dumps(s5b)}")
        good5a = s5a["fired"] and s5a["code"] == 0 and s5a["reason"] == "done"
        good5b = bool(s5b["fired"] and s5b["code"] == 0 and s5b["gate_t"] is not None and s5b["next_first_t"] is not None
                      and s5b["gate_t"] >= s5b["next_first_t"])
        exp[label] = {"W1": good1, "W2": good2, "W3": good3, "W4": good4, "W5a": good5a, "W5b": good5b, "r3": r3, "s5a": s5a, "s5b": s5b}
    print("\n== the expectations")
    o, n = exp["OLD"], exp["NEW"]
    check(not o["W1"], "W1 OLD fails: a follow() between the path read and the file read leaves the committed watcher off the new file")
    check(n["W1"], "W1 NEW passes: the new file's reading arrives and no old-file reading shows after follow()")
    check(not o["W2"], "W2 OLD fails: a follow() between the file read and the position update moves the new file's position")
    check(n["W2"], "W2 NEW passes: the chunk read across follow() is discarded; the position ends at the new file's end")
    check(n["W3"], "W3 NEW passes: an unread old sample at the die stop still fires the stop, and is never the new file's reading")
    check(o["r3"] is not None and o["r3"]["tripped"], "W3 OLD fires the stop too (the old code re-reads the old file from 0)")
    check(o["W4"] and n["W4"], "W4 the control: a follow() at a quiet moment passes on both (the harness alone fails neither)")
    s = o["s5a"]
    check(s["fired"] and s["code"] == 1 and s["reason"].startswith("error:telemetry_stale:NEXT-") and s["reason"].endswith("cool gate"),
          f"W5a OLD ends as E165's s1 did: {s['reason']!r}, {s['into_sampler_s']} s into the second run's sampler, before any launch")
    check(n["W5a"], f"W5a NEW runs to the end: {n['s5a']['reason']!r} (the gate waits on live readings and the run completes)")
    s = o["s5b"]
    check(s["fired"] and s["gate_t"] is not None and s["next_first_t"] is not None and s["gate_t"] < s["next_first_t"],
          "W5b OLD's gate admits the second run's launch on the first run's last reading (the stops blind for that launch)")
    check(n["W5b"], "W5b NEW's gate reads the second run's own telemetry")
    # W6: install()
    d6 = os.path.join(T, "w6")
    os.makedirs(d6)
    saved = H.Watcher
    try:
        rec = WQ.install(H)
        rec2 = WQ.install(H)
        a = types.SimpleNamespace(dry=True, root=os.path.normpath(os.path.join(HERE, "..", "..", "..")), out=os.path.join(d6, "run"),
                                  max_card_min=1.0)
        raw, runs, _ = H.load_protocol(os.path.join(T, "w5a-NEW", "protocol.json"))
        sess = H.Session(a, raw, runs)
        check(rec["installed"] and getattr(sess.watcher, "_q142s", False) and rec2 == rec and issubclass(H.Watcher, OLD),
              "W6 install(): a Session built after it holds the new watcher; a second install() changes nothing")
        check(rec["run_hpl_sha256"] == WQ.RUN_HPL_SHA256 and rec["watcher"] == WQ.THIS,
              f"W6 install()'s record names the watcher file and run_hpl.py's committed hash ({rec['run_hpl_sha256'][:12]})")
    finally:
        H.Watcher = saved
    fake_dir = os.path.join(d6, "fake")
    os.makedirs(fake_dir)
    fp = os.path.join(fake_dir, "run_hpl.py")
    shutil.copyfile(H.__file__, fp)
    with builtins.open(fp, "a") as f:
        f.write("# one more line\n")
    fake = types.SimpleNamespace(**{k: getattr(H, k) for k in ("Session", "Watcher", "parse_tel", "num", "now_ms")})
    fake.__file__, fake.__name__ = fp, H.__name__
    try:
        WQ.install(fake)
        refused = False
    except RuntimeError as e:
        refused = "not the committed run_hpl.py" in str(e)
    check(refused and fake.Watcher is OLD, "W6 install() refuses a run_hpl.py whose bytes differ from the committed file, and installs nothing")
    check(H.Watcher is OLD, "after the test, run_hpl's Watcher is its own again")
    n_ok = sum(results)
    print(f"\n{n_ok} of {len(results)} expectations hold, in {time.time() - t_all:.0f} s")
    if n_ok == len(results):
        print("SELFTEST OK: the forced follow() fails run_hpl.py's committed watcher (W1, W2, W5a, W5b) and passes watcher_q142s.py's")
        return 0
    print("SELFTEST FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
