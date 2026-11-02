#!/usr/bin/env python3
"""E133 (Q136): the morning's queue, detached on aifoundry2. It is E111's queue (queue_e111.py), its rules unchanged, with E133's steps,
times and budget; it depends on no ssh: once started it needs nothing from outside.

    setsid nohup python3 tools/claims-v3/e133/queue_e133.py --schedule <schedule.json> --runs build/e133/runs \
        > build/e133/queue.out 2>&1 < /dev/null &

Steps, in this order, on epoch ms (no local time is ever compared), each a run_e133.py session of its protocol:

  SMOKE  E111's (E98's) smoke: protocol-smoke.json (20 s idle, three 2 s launches); anything but exit 0 ends the queue
  W2     E111's W2: protocol-w2.json (E98's probe -- REST, SUS, HOLD of 39 -- then H-F32, 190 processes of fp32 randn)
  END    the idle after H-F32: protocol-end.json (E98's REST block)
  W1B    E111's W1B: protocol-w1b.json (E98's REST block, then H-I8 from rest, 190 processes of int8 neg_ones)
  END2   the idle after H-I8: protocol-end2.json (E98's REST block)
  W3     the optional afternoon probe: protocol-w3.json (E98's probe, REST, SUS, HOLD of 39), not before w3_not_before_ms and only
         once RUNS/GO-W3 exists (touched on the Intel after the #community-lab post names this card again); else skipped

Before each of W2, END, W1B, END2 and W3, E98's rest rule (E111's): the card carried no launch for the step's rest (W2 20 min, END,
W1B, END2 and W3 15 min): the box's own 5 s history (~/live/history/<UTC date>.jsonl) holds no row with a die over 55 C or a board
reading over 26 W and no two rows running with the card held, over the rest, and the previous step ended at least that long ago.
The card lock must be free and nobody else active (E111's idle_logins_e111.py, the owner's ruling of 1 November 2026: a user whose
every session has been idle for at least 120 minutes and none of whose processes started under 120 minutes ago does not count);
otherwise it polls every 20 s, never taking the lock to wait.

What stops a step from starting (each recorded): no start after no_start_after_ms (15:00 PST); the card-minute budget (the steps'
card_min so far, plus the step's plan, over budget_card_min, 110); a step that could not end by the cutoff; RUNS/SKIP-<step> or
RUNS/QUEUE-STOP; W3 without RUNS/GO-W3 by w3_latest_ms. Exit codes (E111's): 0 next step; 3 (the card was not ours) next step,
flagged; 1 (an error) next step once, a second halts; 4 (a safety stop) runs END or END2 only (an idle read, no launch) and then
stops; 2 and 5 halt. A halt leaves the card alone; nothing is set, so nothing is restored.

The hard stop (E111's): at cutoff_ms - 120 s a running session's stop-file is touched, at cutoff_ms - 30 s it gets SIGTERM if still
alive (its handler ends the session; a device process is never signalled), and at cutoff_ms the queue exits (16:00 PST). Beside the
steps, the camera phone's /health is read once a minute (E111's descriptive room reading; the phone charges): RUNS/phone.jsonl.
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "e111"))
import idle_logins_e111 as IL  # noqa: E402

LOCK = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
IDLE_W_BAR = 26.0
IDLE_DIE_BAR = 55
POLL_S = 20
PLAN_MIN = {"SMOKE": 1.5, "W2": 50.0, "END": 2.5, "W1B": 30.0, "END2": 2.5, "W3": 24.0}
REST_MIN = {"SMOKE": 0, "W2": 20, "END": 15, "W1B": 15, "END2": 15, "W3": 15}
STEPS = ("SMOKE", "W2", "END", "W1B", "END2", "W3")
HEALTH = "http://p3-phone:8080/health"


def now_ms():
    return int(time.time() * 1000)


def out(cmd, timeout=30, env=None, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env, cwd=cwd)
        return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "", str(e)


def health():
    try:
        with urllib.request.urlopen(HEALTH, timeout=6) as r:
            d = json.loads(r.read().decode(errors="replace"))
        return {k: d.get(k) for k in ("ok", "streaming", "connected", "pictureHealthy", "fps", "batteryTempC", "batteryCharging",
                                      "batteryPct", "externalPower", "preset")}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:200]}


class Queue:
    def __init__(self, a):
        self.a = a
        self.root = os.path.abspath(a.root)
        self.runs = os.path.abspath(a.runs)
        self.sched = json.load(open(a.schedule))
        self.cutoff = self.sched["cutoff_ms"]
        self.no_start_after = self.sched["no_start_after_ms"]
        self.budget = float(self.sched.get("budget_card_min", 110.0)) - float(self.sched.get("card_min_before", 0.0))
        self.last_end_ms = self.sched.get("rest_from_ms", 0)
        self.errors = 0
        self.card_min = 0.0
        self.dry = a.dry
        self.steps = tuple(x for x in (a.steps or ",".join(STEPS)).split(",") if x)
        assert all(x in PLAN_MIN for x in self.steps), self.steps
        os.makedirs(self.runs, exist_ok=True)
        self.ettelem = os.path.join(self.root, "build/ettelem-hpl/ettelem")
        self.stop_phone = threading.Event()
        os.environ["E111_IDLE_LOG"] = os.path.join(self.runs, "idle_logins.jsonl")   # the idle-login decisions, counts only, for every check

    def rec(self, kind, **kw):
        d = dict(t_ms=now_ms(), zone=time.strftime("%Z"), kind=kind, **kw)
        with open(os.path.join(self.runs, "queue.jsonl"), "a") as f:
            f.write(json.dumps(d) + "\n")
        print(time.strftime("%H:%M:%S %Z"), json.dumps(d), flush=True)

    def status(self, **kw):
        d = dict(t_ms=now_ms(), zone=time.strftime("%Z"), pid=os.getpid(), card_min=round(self.card_min, 2), **kw)
        tmp = os.path.join(self.runs, "status.json.tmp")
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, os.path.join(self.runs, "status.json"))

    def stopped(self):
        return os.path.exists(os.path.join(self.runs, "QUEUE-STOP"))

    def phone_loop(self):
        while not self.stop_phone.is_set():
            d = dict(t_ms=now_ms(), **health())
            with open(os.path.join(self.runs, "phone.jsonl"), "a") as f:
                f.write(json.dumps(d) + "\n")
            self.stop_phone.wait(60)

    # -- the rest rule (E98's queue, with the rest as a parameter)
    def last_busy_ms(self, now, rest_min):
        if self.dry:
            return 0, 0.0, 0
        rows = []
        span = (rest_min + 1) * 60 * 1000
        for t in (now - span - 60000, now):
            p = os.path.expanduser(time.strftime("~/live/history/%Y-%m-%d.jsonl", time.gmtime(t / 1000.0)))
            if p in [r[0] for r in rows]:
                continue
            try:
                with open(p, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    n = f.tell()
                    f.seek(max(0, n - 300000))
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
                if t < now - span:
                    continue
                seen += 1
                newest = max(newest, t)
                held = False
                for c in r.get("cards") or []:
                    w, die = c.get("w"), c.get("die")
                    held = held or bool(c.get("held"))
                    if (w is not None and w > IDLE_W_BAR) or (die is not None and die > IDLE_DIE_BAR):
                        busy = max(busy, t)
                if held and last_held:
                    busy = max(busy, t)
                last_held = held
        return busy, (now - newest) / 1000.0 if newest else None, seen

    def lock_free(self):
        if self.dry:
            return True
        rc, _, _ = out(["flock", "-n", LOCK, "true"], timeout=5)
        return rc == 0

    def others(self):
        """How many other users block, by amendment A1's rule (idle_logins_e111.py: a user whose every session has been idle for at
        least 120 minutes does not). A count: a login never goes in a record."""
        if self.dry:
            return 0
        return IL.others_count()

    def snapshot(self, pdir, tag):
        snap = {"tag": tag, "t_ms": now_ms(), "zone": time.strftime("%Z"), "phone": health()}
        if self.dry:
            json.dump(snap, open(os.path.join(pdir, f"snapshot-{tag}.json"), "w"))
            return snap
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

    def may_start(self, name):
        now = now_ms()
        if now >= self.cutoff or self.stopped():
            return "queue stop or the cutoff"
        if os.path.exists(os.path.join(self.runs, f"SKIP-{name}")):
            return "SKIP file"
        if now >= self.no_start_after:
            return "no step starts after no_start_after_ms"
        if name == "SMOKE" and now >= self.sched["smoke_latest_ms"]:
            return "the smoke's latest start passed"
        if name == "W3" and now >= self.sched["w3_latest_ms"]:
            return "W3's latest start passed (no GO-W3 by then, or the card not free)"
        if self.card_min + PLAN_MIN[name] > self.budget:
            return f"card budget: {self.card_min:.1f} used + {PLAN_MIN[name]} planned > {self.budget:.1f}"
        if now + PLAN_MIN[name] * 60000 > self.cutoff - 180000:
            return "it could not end before the cutoff"
        return None

    def wait_for(self, name):
        target = {"W3": self.sched.get("w3_not_before_ms", 0), "SMOKE": self.sched.get("smoke_not_before_ms", 0)}.get(name, 0)
        rest_s = (5 if self.dry else REST_MIN[name] * 60)
        waits = {}
        while True:
            why = self.may_start(name)
            if why:
                self.rec("skip", step=name, why=why, waits=waits)
                return False
            now = now_ms()
            if now < target:
                self.status(state="waiting", step=name, until_ms=target)
                time.sleep(min(POLL_S, max(1.0, (target - now) / 1000.0)))
                continue
            if rest_s:
                busy, age, seen = self.last_busy_ms(now, REST_MIN[name])
                ref = max(busy, self.last_end_ms)
                if ref and now - ref < rest_s * 1000:
                    target = ref + rest_s * 1000
                    waits["rest"] = waits.get("rest", 0) + 1
                    self.status(state="resting", step=name, until_ms=target, busy_ms=busy)
                    continue
            else:
                busy, age, seen, ref = 0, None, 0, self.last_end_ms
            if name == "W3" and not os.path.exists(os.path.join(self.runs, "GO-W3")):
                waits["go"] = waits.get("go", 0) + 1
                self.status(state="waiting for GO-W3 (the post first)", step=name)
                time.sleep(POLL_S)
                continue
            if not self.lock_free():
                waits["lock"] = waits.get("lock", 0) + 1
                self.status(state="lock held", step=name)
                time.sleep(POLL_S)
                continue
            n = self.others()
            if n:
                waits["others"] = waits.get("others", 0) + 1
                self.status(state="another user is logged in", step=name, n=n)
                time.sleep(POLL_S)
                continue
            self.rest_seen = {"last_busy_ms": busy, "history_age_s": age, "history_rows": seen,
                              "since_ref_min": round((now - ref) / 60000.0, 1) if ref else None, "waits": waits}
            return True

    def run_step(self, name):
        pdir = os.path.join(self.runs, name)
        os.makedirs(pdir, exist_ok=True)
        s0 = self.snapshot(pdir, "start")
        proto = os.path.join(self.root, "tools/claims-v3/e133", f"protocol-{name.lower()}{'-dry' if self.dry else ''}.json")
        # the session's cap: its protocol's, never past what the budget leaves (minus 0.5 min for the queue's own reads), so the
        # card minutes stay within budget_card_min even if a step overruns its plan (run_hpl.py ends a session at its cap, exit 0)
        cap = min(float(json.load(open(proto))["caps"]["max_card_min"]), round(self.budget - self.card_min - 0.5, 1))
        cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/e133/run_e133.py"), "--protocol", proto, "--out", pdir,
               "--max-card-min", f"{cap:g}"]
        cwd = self.root
        if self.dry:
            cmd.append("--dry")
        t0 = now_ms()
        self.rec("start", step=name, cmd=cmd[1:], rest=self.rest_seen, config=(s0 or {}).get("config"))
        self.status(state="running", step=name, t0_ms=t0)
        with open(os.path.join(pdir, "run.out"), "ab") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=cwd, start_new_session=True)
        stopped, termed = False, False
        while proc.poll() is None:
            now = now_ms()
            if not stopped and now >= self.cutoff - 120000:
                open(os.path.join(pdir, "STOP"), "a").close()
                stopped = True
                self.rec("cutoff_stop", step=name)
            if stopped and not termed and now >= self.cutoff - 30000:
                proc.terminate()
                termed = True
                self.rec("cutoff_term", step=name)
            time.sleep(1.0)
        rc = proc.returncode
        self.last_end_ms = now_ms()
        self.card_min += (self.last_end_ms - t0) / 60000.0
        end = None
        for fn in ("end.json", "session-end.json"):
            try:
                end = json.load(open(os.path.join(pdir, fn)))
                break
            except (OSError, ValueError):
                pass
        s1 = self.snapshot(pdir, "end")
        self.rec("end", step=name, rc=rc, end=end, cutoff_stopped=stopped, step_card_min=round((self.last_end_ms - t0) / 60000.0, 2),
                 card_min_total=round(self.card_min, 2), config=(s1 or {}).get("config"))
        return rc, stopped

    def run(self):
        self.rec("queue_start", cutoff_ms=self.cutoff, no_start_after_ms=self.no_start_after, budget_card_min=self.budget,
                 steps=list(self.steps), python=sys.version.split()[0], sensors=bool(shutil.which("sensors")), dry=self.dry)
        th = threading.Thread(target=self.phone_loop, daemon=True)
        th.start()
        why = "done"
        safety = False
        for name in self.steps:
            if safety and name not in ("END", "END2"):
                self.rec("skip", step=name, why="after a safety stop only END runs")
                continue
            if not self.wait_for(name):
                if self.stopped() or now_ms() >= self.cutoff:
                    why = "stop or cutoff"
                    break
                if name == "SMOKE":
                    why = "no smoke: nothing else runs"
                    break
                continue
            rc, stopped = self.run_step(name)
            if name == "SMOKE" and rc != 0:
                why = f"the smoke failed (exit {rc}): nothing else runs"
                open(os.path.join(self.runs, "QUEUE-HALT"), "a").write(json.dumps({"t_ms": now_ms(), "why": why}) + "\n")
                break
            if rc == 0 or rc == 3 or stopped:
                continue
            if rc == 4:
                safety = True
                continue
            if rc == 1:
                self.errors += 1
                if self.errors == 1:
                    continue
            why = f"step {name} exit {rc}"
            open(os.path.join(self.runs, "QUEUE-HALT"), "a").write(json.dumps({"t_ms": now_ms(), "why": why}) + "\n")
            break
        self.stop_phone.set()
        self.rec("queue_end", why=why, card_min_total=round(self.card_min, 2))
        self.status(state="ended", why=why)
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--steps", default=None, help="a comma list of steps (default SMOKE,W2,END,W1B,END2,W3)")
    a = ap.parse_args()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    return Queue(a).run()


if __name__ == "__main__":
    sys.exit(main())
