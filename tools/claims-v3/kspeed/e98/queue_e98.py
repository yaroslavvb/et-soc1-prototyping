#!/usr/bin/env python3
"""E98 (Q132): the night's queue, detached on aifoundry2. It takes no card lock between probes, so E100 and E96 can run in
their slots, and it depends on no ssh: once started it needs nothing from outside.

    setsid nohup python3 queue_e98.py --schedule schedule.json --runs build/e98/runs > build/e98/queue.out 2>&1 < /dev/null &

For each probe of schedule.json, in order, on epoch ms (02:00 PDT goes back tonight; no local time is ever compared):

  1. Wait for the probe's rest_read_ms. Skip the probe if RUNS/SKIP-<name> exists (a hand brake for the night's other
     experiments), or once latest_start_ms has passed. A probe that would run into a slot of schedule.json (E100, E96) waits for the slot's
     end, so the queue launches nothing inside a slot.
  2. The rest rule. The card must have carried no launch for the last 15 min: the box's own 5 s history
     (~/live/history/<UTC date>.jsonl, written by tools/lab/live/live-collector.py) must hold no row with a die over 55 C or a board
     reading over 26 W and no two rows running with the card held, and the previous probe must have ended at least 15 min ago. A busy row
     moves the probe's start to 15 min after that row. The card lock must be free and nobody else logged in (`who`, as the runner checks);
     otherwise it polls every 20 s. It never takes the lock to wait, and never launches inside another's hold.
  3. Records sensors -j, the zone, the load, and `ettelem config` (non-blocking lock, timeout 10), then runs run_e98.py, whose
     session holds the lock from the REST reading to the end of the HOLD, and records the same at the end.
  4. Exit codes: 0 next probe; 3 (the card was not ours) next probe, flagged; 1 (an error) next probe once, a second one
     halts; 2, 4, 5 halt (RUNS/QUEUE-HALT says why). A halt leaves the card alone; nothing is set, so nothing is restored.

The hard stop: at cutoff_ms - 120 s a running session's stop-file is touched (the launch loop ends at its next ~0.5 s launch
boundary), at cutoff_ms - 30 s it gets SIGTERM if still alive (its handler ends the session; a device process is never
signalled), and at cutoff_ms the queue exits. RUNS/QUEUE-STOP stops the queue at its next look, between probes.
Every record goes to RUNS/queue.jsonl; RUNS/status.json holds the current state.
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time

LOCK = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
REST_S = 15 * 60
IDLE_W_BAR = 26.0
IDLE_DIE_BAR = 55
POLL_S = 20


def now_ms():
    return int(time.time() * 1000)


def out(cmd, timeout=30, env=None, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env, cwd=cwd)
        return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "", str(e)


class Queue:
    def __init__(self, a):
        self.a = a
        self.root = os.path.abspath(a.root)
        self.runs = os.path.abspath(a.runs)
        self.sched = json.load(open(a.schedule))
        self.cutoff = self.sched["cutoff_ms"]
        self.last_end_ms = self.sched.get("rest_from_ms", 0)
        self.errors = 0
        self.rest_s = 5 if a.dry else REST_S
        os.makedirs(self.runs, exist_ok=True)
        self.ettelem = os.path.join(self.root, "build/ettelem-hpl/ettelem")

    def rec(self, kind, **kw):
        d = dict(t_ms=now_ms(), zone=time.strftime("%Z"), kind=kind, **kw)
        with open(os.path.join(self.runs, "queue.jsonl"), "a") as f:
            f.write(json.dumps(d) + "\n")
        print(time.strftime("%H:%M:%S %Z"), json.dumps(d), flush=True)

    def status(self, **kw):
        d = dict(t_ms=now_ms(), zone=time.strftime("%Z"), pid=os.getpid(), **kw)
        tmp = os.path.join(self.runs, "status.json.tmp")
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, os.path.join(self.runs, "status.json"))

    def stopped(self):
        return os.path.exists(os.path.join(self.runs, "QUEUE-STOP"))

    def slot_clash(self, t):
        """The slot a probe started at t would run into, or None."""
        span = self.sched.get("probe_min", 24) * 60000
        for sl in self.sched.get("slots", []):
            if t < sl["end_ms"] and t + span > sl["start_ms"]:
                return sl
        return None

    # -- the rest rule
    def last_busy_ms(self, now):
        """(the newest busy row's t in the last 16 min of the box's own history, or 0; how old the newest row is, s; rows read)."""
        if self.a.dry:
            return 0, 0.0, 0
        rows = []
        for t in (now - 17 * 60 * 1000, now):
            p = os.path.expanduser(time.strftime("~/live/history/%Y-%m-%d.jsonl", time.gmtime(t / 1000.0)))
            if p in [r[0] for r in rows]:
                continue
            try:
                with open(p, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    n = f.tell()
                    f.seek(max(0, n - 200000))
                    rows.append((p, f.read().decode(errors="replace").splitlines()))
            except OSError:
                pass
        busy, newest, seen = 0, 0, 0
        last_held = None
        for _, lines in rows:
            for ln in lines:
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                t = r.get("t", 0)
                if t < now - 16 * 60 * 1000:
                    continue
                seen += 1
                newest = max(newest, t)
                held = False
                for c in r.get("cards") or []:
                    w, die = c.get("w"), c.get("die")
                    held = held or bool(c.get("held"))
                    if (w is not None and w > IDLE_W_BAR) or (die is not None and die > IDLE_DIE_BAR):
                        busy = max(busy, t)
                # held on two rows running: a launch session holds it for many, a config read or a lock probe can show on one
                if held and last_held:
                    busy = max(busy, t)
                last_held = held
        return busy, (now - newest) / 1000.0 if newest else None, seen

    def lock_free(self):
        if self.a.dry:
            return True
        rc, _, _ = out(["flock", "-n", LOCK, "true"], timeout=5)
        return rc == 0

    def others(self):
        """How many other users `who` lists. A count: a login never goes in a record."""
        if self.a.dry:
            return 0
        me = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
        rc, so, _ = out(["who"], timeout=5)
        return len({ln.split()[0] for ln in so.splitlines() if ln.split() and ln.split()[0] != me})

    # -- one snapshot beside a probe
    def snapshot(self, pdir, tag):
        snap = {"tag": tag, "t_ms": now_ms(), "zone": time.strftime("%Z")}
        if self.a.dry:
            json.dump(snap, open(os.path.join(pdir, f"snapshot-{tag}.json"), "w"))
            return
        rc, so, _ = out(["sensors", "-j"], timeout=20)
        if rc == 0:
            open(os.path.join(pdir, f"sensors-{tag}.json"), "w").write(so)
        snap["sensors_rc"] = rc
        rc, so, _ = out(["uptime"], timeout=5)
        snap["uptime"] = so.strip()
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        for attempt in range(1, 6):
            rc, so, se = out(["flock", "-n", LOCK, "timeout", "10", self.ettelem, "config"], timeout=15, env=env, cwd=self.root)
            if rc == 0:
                break
            time.sleep(2)
        snap["config_rc"], snap["config_attempts"] = rc, attempt
        open(os.path.join(pdir, f"config-{tag}.txt"), "w").write(so + (("\nstderr: " + se[-300:]) if rc else ""))
        try:
            snap["config"] = json.loads(so.strip().splitlines()[-1])
        except (ValueError, IndexError):
            snap["config"] = None
        json.dump(snap, open(os.path.join(pdir, f"snapshot-{tag}.json"), "w"), indent=1)
        return snap

    # -- one probe
    def wait_for_probe(self, p):
        """True when it may go; False with the reason recorded when it is skipped."""
        name = p["name"]
        target = p["rest_read_ms"]
        waits = {}
        while True:
            now = now_ms()
            if now >= self.cutoff or self.stopped():
                self.rec("skip", probe=name, why="queue stop or the cutoff")
                return False
            if os.path.exists(os.path.join(self.runs, f"SKIP-{name}")):
                self.rec("skip", probe=name, why="SKIP file")
                return False
            if now >= p["latest_start_ms"]:
                self.rec("skip", probe=name, why="latest_start passed", waits=waits)
                return False
            clash = self.slot_clash(max(now, target))
            if clash is not None:
                # never inside another experiment's slot: a probe that would run into one waits for its end, then its latest start decides
                target = max(target, clash["end_ms"])
                waits["slot"] = waits.get("slot", 0) + 1
                self.status(state="slot", probe=name, slot=clash["name"], until_ms=target)
                time.sleep(POLL_S)
                continue
            if now < target:
                self.status(state="waiting", probe=name, until_ms=target)
                time.sleep(min(POLL_S, max(1.0, (target - now) / 1000.0)))
                continue
            busy, age, seen = self.last_busy_ms(now)
            ref = max(busy, self.last_end_ms)
            if ref and now - ref < self.rest_s * 1000:
                target = ref + self.rest_s * 1000
                waits["rest"] = waits.get("rest", 0) + 1
                self.status(state="resting", probe=name, until_ms=target, busy_ms=busy)
                continue
            if not self.lock_free():
                waits["lock"] = waits.get("lock", 0) + 1
                self.status(state="lock held", probe=name)
                time.sleep(POLL_S)
                continue
            n = self.others()
            if n:
                waits["others"] = waits.get("others", 0) + 1
                self.status(state="another user is logged in", probe=name, n=n)
                time.sleep(POLL_S)
                continue
            self.rest_seen = {"last_busy_ms": busy, "history_age_s": age, "history_rows_16min": seen,
                              "since_ref_min": round((now - ref) / 60000.0, 1) if ref else None, "waits": waits}
            return True

    def run_probe(self, p):
        name = p["name"]
        pdir = os.path.join(self.runs, name)
        os.makedirs(pdir, exist_ok=True)
        s0 = self.snapshot(pdir, "start")
        cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/kspeed/e98/run_e98.py"), "--protocol", self.a.protocol,
               "--out", pdir, "--max-card-min", str(self.sched.get("max_card_min", 30))]
        if self.a.dry:
            cmd.append("--dry")
        t0 = now_ms()
        self.rec("start", probe=name, rest_read_ms=p["rest_read_ms"], rest=self.rest_seen,
                 config=(s0 or {}).get("config") if isinstance(s0, dict) else None)
        self.status(state="running", probe=name, t0_ms=t0)
        with open(os.path.join(pdir, "run.out"), "ab") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=self.root,
                                    start_new_session=True)
        stopped, termed = False, False
        while proc.poll() is None:
            now = now_ms()
            if not stopped and now >= self.cutoff - 120000:
                open(os.path.join(pdir, "STOP"), "a").close()
                stopped = True
                self.rec("cutoff_stop", probe=name)
            if stopped and not termed and now >= self.cutoff - 30000:
                proc.terminate()
                termed = True
                self.rec("cutoff_term", probe=name)
            time.sleep(1.0)
        rc = proc.returncode
        self.last_end_ms = now_ms()
        try:
            end = json.load(open(os.path.join(pdir, "end.json")))
        except (OSError, ValueError):
            end = None
        s1 = self.snapshot(pdir, "end")
        self.rec("end", probe=name, rc=rc, end=end, cutoff_stopped=stopped, config=(s1 or {}).get("config") if isinstance(s1, dict) else None)
        return rc, stopped

    def run(self):
        self.rec("queue_start", cutoff_ms=self.cutoff, probes=[p["name"] for p in self.sched["probes"]], python=sys.version.split()[0],
                 sensors=bool(shutil.which("sensors")))
        why = "done"
        for p in self.sched["probes"]:
            if not self.wait_for_probe(p):
                if self.stopped() or now_ms() >= self.cutoff:
                    why = "stop or cutoff"
                    break
                continue
            rc, stopped = self.run_probe(p)
            if rc == 0 or rc == 3 or stopped:
                continue
            if rc == 1:
                self.errors += 1
                if self.errors == 1:
                    continue
            why = f"probe {p['name']} exit {rc}"
            open(os.path.join(self.runs, "QUEUE-HALT"), "a").write(json.dumps({"t_ms": now_ms(), "why": why}) + "\n")
            break
        self.rec("queue_end", why=why)
        self.status(state="ended", why=why)
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--protocol", default="tools/claims-v3/kspeed/e98/protocol.json")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    a.protocol = os.path.abspath(a.protocol) if os.path.exists(a.protocol) else os.path.join(os.path.abspath(a.root), a.protocol)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    return Queue(a).run()


if __name__ == "__main__":
    sys.exit(main())
