#!/usr/bin/env python3
"""E111 (Q133): the afternoon's queue, detached on aifoundry2. It depends on no ssh: once started it needs nothing from outside.

    setsid nohup python3 tools/claims-v3/e111/queue_e111.py --schedule <schedule.json> --runs build/e111/runs \
        > build/e111/queue.out 2>&1 < /dev/null &

Steps, in this order, on epoch ms (no local time is ever compared):

  SMOKE  E98's smoke: run_e111.py protocol-smoke.json (20 s idle, three 2 s launches); not before w1_not_before_ms - 25 min, not after
         w1_latest_ms - 15 min; anything but exit 0 ends the queue (nothing else runs)
  W1   warm probe 1: run_e111.py protocol-w1.json (E98's REST, SUS and HOLD, the hold extended to H-I8)
  W2   warm probe 2: run_e111.py protocol-w2.json (E98's REST, SUS and HOLD, then H-F32)
  END  the idle after H-F32: run_e111.py protocol-end.json (E98's REST block)
  CAM  the camera at 0.005 Hz: run_hlc.py protocol-cam.json from the staged copy build/e111/cam (E63's runner, as E73 ran it),
       straight after END; then the registered camera reduction (reduce_hm.py, fpa_trace.py, lockin_hlf.py, dips_hlc.py) at nice 10

Before each of W1, W2 and END, E98's rest rule: the card carried no launch for the step's rest (W1 15 min, W2 20 min, END 15
min): the box's own 5 s history (~/live/history/<UTC date>.jsonl) holds no row with a die over 55 C or a board reading over 26 W
and no two rows running with the card held, over the rest, and the previous step ended at least that long ago. The card lock must
be free and nobody else logged in (`who`); otherwise it polls every 20 s, never taking the lock to wait. CAM needs only the lock free,
nobody else logged in and the camera's /health reading ok and streaming.

What stops a step from starting (each recorded): its latest start has passed (W1: schedule w1_latest_ms; every step: no start after
no_start_after_ms, 18:00 PST); the card-minute budget (the steps' card_min so far, plus the step's plan, over budget_card_min, 120);
RUNS/SKIP-<step> or RUNS/QUEUE-STOP. Exit codes: 0 next step; 3 (the card was not ours) next step, flagged; 1 (an error) next step
once, a second halts; 4 (a safety stop) runs END only (an idle read, no launch) and then stops; 2 and 5 halt. A halt leaves the card
alone; nothing is set, so nothing is restored.

The hard stop: at cutoff_ms - 120 s a running session's stop-file is touched (the launch loop ends at its next ~0.5 s launch
boundary), at cutoff_ms - 30 s it gets SIGTERM if still alive (its handler ends the session; a device process is never signalled), and
at cutoff_ms the queue exits. Beside the steps, from start to end, the camera phone's /health is read once a minute and its
batteryTempC, batteryCharging and streaming go to RUNS/phone.jsonl: a descriptive room reading, never a verdict (the phone charges).
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

LOCK = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
IDLE_W_BAR = 26.0
IDLE_DIE_BAR = 55
POLL_S = 20
PLAN_MIN = {"SMOKE": 1.5, "W1": 44.5, "W2": 50.0, "END": 2.5, "CAM": 22.0}
REST_MIN = {"SMOKE": 0, "W1": 15, "W2": 20, "END": 15, "CAM": 0}
STEPS = ("SMOKE", "W1", "W2", "END", "CAM")
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
        self.budget = float(self.sched.get("budget_card_min", 120.0)) - float(self.sched.get("card_min_before", 0.0))
        self.last_end_ms = self.sched.get("rest_from_ms", 0)
        self.errors = 0
        self.card_min = 0.0
        self.dry = a.dry
        os.makedirs(self.runs, exist_ok=True)
        self.ettelem = os.path.join(self.root, "build/ettelem-hpl/ettelem")
        self.cam_code = os.path.join(self.root, "build/e111/cam")
        self.stop_phone = threading.Event()

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
        """How many other users `who` lists. A count: a login never goes in a record."""
        if self.dry:
            return 0
        me = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
        rc, so, _ = out(["who"], timeout=5)
        return len({ln.split()[0] for ln in so.splitlines() if ln.split() and ln.split()[0] != me})

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
        if name == "W1" and now >= self.sched["w1_latest_ms"]:
            return "W1's latest start passed"
        if name == "SMOKE" and now >= self.sched["w1_latest_ms"] - 15 * 60000:
            return "the smoke's latest start (W1's latest - 15 min) passed"
        if self.card_min + PLAN_MIN[name] > self.budget:
            return f"card budget: {self.card_min:.1f} used + {PLAN_MIN[name]} planned > {self.budget:.1f}"
        if now + PLAN_MIN[name] * 60000 > self.cutoff - 180000:
            return "it could not end before the cutoff"
        return None

    def wait_for(self, name):
        target = {"W1": self.sched.get("w1_not_before_ms", 0),
                  "SMOKE": self.sched.get("w1_not_before_ms", 0) - 25 * 60000}.get(name, 0)
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
            if name == "CAM":
                h = health()
                if not (h.get("ok") and h.get("streaming")):
                    self.rec("skip", step=name, why="the camera's /health is not ok and streaming", health=h)
                    return False
            self.rest_seen = {"last_busy_ms": busy, "history_age_s": age, "history_rows": seen,
                              "since_ref_min": round((now - ref) / 60000.0, 1) if ref else None, "waits": waits}
            return True

    def run_step(self, name):
        pdir = os.path.join(self.runs, name)
        os.makedirs(pdir, exist_ok=True)
        s0 = self.snapshot(pdir, "start")
        if name == "CAM":
            proto = "protocol-cam-dry.json" if self.dry else "protocol-cam.json"
            cmd = [sys.executable, os.path.join(self.cam_code, "run_hlc.py"), "--protocol", os.path.join(self.cam_code, proto),
                   "--out", pdir, "--root", self.root, "--force"]
            cwd = self.cam_code
        else:
            proto = os.path.join(self.root, "tools/claims-v3/e111", f"protocol-{name.lower()}{'-dry' if self.dry else ''}.json")
            cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/e111/run_e111.py"), "--protocol", proto, "--out", pdir,
                   "--max-card-min", str(json.load(open(proto))["caps"]["max_card_min"])]
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

    def reduce_cam(self):
        """The registered camera reduction, E85's and E73's chain on the staged copy, at nice 10, after the card is done."""
        pdir = os.path.join(self.runs, "CAM")
        red, ana = pdir + "-RED", pdir + "-ANA"
        c = self.cam_code
        proto = os.path.join(c, "protocol-cam-dry.json" if self.dry else "protocol-cam.json")
        steps = [["nice", "-n", "10", sys.executable, os.path.join(c, "reduce_hm.py"), pdir, "--out", red],
                 ["nice", "-n", "10", sys.executable, os.path.join(c, "fpa_trace.py"), pdir, "--out", os.path.join(red, "fpa.npz")],
                 ["nice", "-n", "10", sys.executable, os.path.join(c, "lockin_hlf.py"), red, "--protocol", proto,
                  "--template", os.path.join(c, "prereg/e62_bloom_dt.npy"), "--scene-ref", os.path.join(c, "prereg/e62_scene.npy"),
                  "--fpa", os.path.join(red, "fpa.npz"), "--out", ana, "--seed", "111"],
                 ["nice", "-n", "10", sys.executable, os.path.join(c, "dips_hlc.py"), red, "--out", os.path.join(ana, "dips.json")]]
        os.makedirs(ana, exist_ok=True)
        for s in steps:
            rc, so, se = out(s, timeout=3600, cwd=c)
            self.rec("reduce_cam", cmd=[os.path.basename(x) for x in s[3:5]], rc=rc, tail=(so[-600:] + se[-400:]))
            with open(os.path.join(ana, "reduce.log"), "a") as f:
                f.write(" ".join(s) + f"\nrc={rc}\n" + so + se + "\n")
            if rc != 0:
                return rc
        return 0

    def run(self):
        self.rec("queue_start", cutoff_ms=self.cutoff, no_start_after_ms=self.no_start_after, budget_card_min=self.budget,
                 steps=list(STEPS), python=sys.version.split()[0], sensors=bool(shutil.which("sensors")), dry=self.dry)
        th = threading.Thread(target=self.phone_loop, daemon=True)
        th.start()
        why = "done"
        safety = False
        for name in STEPS:
            if safety and name != "END":
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
            if name == "CAM" and rc == 0:
                self.reduce_cam()
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
    a = ap.parse_args()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    return Queue(a).run()


if __name__ == "__main__":
    sys.exit(main())
