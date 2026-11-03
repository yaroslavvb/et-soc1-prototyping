#!/usr/bin/env python3
"""E144b (Q138): the evening's queue, detached on aifoundry2. It is E133's queue (queue_e133.py, E111's), its rules unchanged, with E144b's
steps, times and budget, and E143's stop-path tests (queue_e143.py's check, ported); it depends on no ssh: once started it needs nothing
from outside.

    setsid nohup python3 tools/claims-v3/e144b/queue_e144b.py --schedule <schedule.json> --runs build/e144b/runs \
        > build/e144b/queue.out 2>&1 < /dev/null &

The go gate: nothing touches the card until RUNS/GO exists (touched over ssh after the claim) or the marker tools/claims-v3/e144b/CLAIMED
is on origin/main of the public repository (committed on the Intel only after the #community-lab post names this card; the box reads it
with `git fetch` over https, so a lapsed Tailscale check cannot hold the run, and cannot start it either). At the go, every file the
queue runs must equal origin/main's byte for byte, or the queue halts. No go by the smoke's latest start: nothing runs.

Steps, in this order, on epoch ms (no local time is ever compared), each a run_e144b.py session of its protocol:

  SMOKE           E133's (E111's, E98's) smoke: protocol-smoke.json (20 s idle, three 2 s launches); anything but exit 0 ends the queue
  STOPTEST-DIE    the die stop's path: abs_stop_c 30 C. It passes only if it ended with exit 4 for "die" within 1.5 s of the first live
                  sampler line at or above 30 C, before any work launch. A failure ends the queue (QUEUE-HALT), nothing else runs
  STOPTEST-BOARD  the board stop's path: board_cap_w 30 W on 3 samples, one 6 s int8 -1s launch. It passes only if it ended with exit 4 for
                  "board", the watcher's safety_trip came inside the work launch and within 1.5 s of the third live line over 30 W, and
                  the launch ended within 3 s of the trip. A failure ends the queue (QUEUE-HALT), nothing else runs
  G1              Q138(t)'s G1: protocol-g1.json (E133's W1B: E98's REST, 120 s, then H-I8, 107 processes of int8 -1s behind the 57 C gate)
  END             G1's cool-down: protocol-end.json (E98's REST block, 120 s), right after G1
  G2              Q138(t)'s G2: protocol-g2.json (E98's REST, 120 s, then H-F32, 106 processes of fp32 randn from at once, governed)
  END2            G2's cool-down: protocol-end2.json, right after G2

Before G1 and G2, E98's rest rule (E111's, E133's): the card carried no launch for 15 minutes: the box's own 5 s history
(~/live/history/<UTC date>.jsonl) holds no row with a die over 55 C or a board reading over 26 W and no two rows running with the card
held, over the rest, and the previous step ended at least that long ago. END and END2 follow their holds at once: they are cool-down
readings, unscored (E144b.md, departure D1). The card lock must be free and nobody else active (E111's idle_logins_e111.py, the owner's
ruling of 1 November 2026: a user whose every session has been idle for at least 120 minutes and none of whose processes started under
120 minutes ago does not count); otherwise it polls every 20 s, never taking the lock to wait.

What stops a step from starting (each recorded): the smoke after smoke_latest_ms (then nothing runs); no start after no_start_after_ms;
the card-minute budget (the steps' card_min so far, plus the step's plan, over budget_card_min, 40); a step that could not end 3 minutes
before the cutoff; RUNS/SKIP-<step> or RUNS/QUEUE-STOP. Exit codes (E111's): 0 next step; 3 (the card was not ours) next step, flagged;
1 (an error) next step once, a second halts; 4 (a safety stop) in G1 or G2 runs END / END2 only (an idle read, no launch) and then
stops; 2 and 5 halt. A halt leaves the card alone; nothing is set, so nothing is restored.

The hard stop (E111's): at cutoff_ms - 120 s a running session's stop-file is touched, at cutoff_ms - 30 s it gets SIGTERM if still
alive (its handler ends the session; a device process is never signalled), and at cutoff_ms the queue exits (23:50 PST). Beside the
steps, the camera phone's /health is read once a minute (E111's descriptive room reading): RUNS/phone.jsonl.
"""
import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e111"))
import idle_logins_e111 as IL  # noqa: E402

LOCK = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
IDLE_W_BAR = 26.0
IDLE_DIE_BAR = 55
POLL_S = 20
STEPS = ("SMOKE", "STOPTEST-DIE", "STOPTEST-BOARD", "G1", "END", "G2", "END2")
PLAN_MIN = {"SMOKE": 1.0, "STOPTEST-DIE": 0.5, "STOPTEST-BOARD": 0.5, "G1": 17.3, "END": 2.1, "G2": 17.4, "END2": 2.1}
REST_MIN = {"SMOKE": 0, "STOPTEST-DIE": 0, "STOPTEST-BOARD": 0, "G1": 15, "END": 0, "G2": 15, "END2": 0}
STOPTESTS = {"STOPTEST-DIE": "die", "STOPTEST-BOARD": "board"}
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
        self.budget = float(self.sched.get("budget_card_min", 40.0))
        self.last_end_ms = self.sched.get("rest_from_ms", 0)
        self.errors = 0
        self.card_min = 0.0
        self.dry = a.dry
        self.steps = tuple(x for x in (a.steps or ",".join(STEPS)).split(",") if x)
        assert all(x in PLAN_MIN for x in self.steps), self.steps
        os.makedirs(self.runs, exist_ok=True)
        self.ettelem = os.path.join(self.root, "build/ettelem-hpl/ettelem")
        self.stop_phone = threading.Event()
        self.rest_seen = {}
        os.environ["E111_IDLE_LOG"] = os.path.join(self.runs, "idle_logins.jsonl")   # the idle-login decisions, counts only

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

    # -- the rest rule (E98's queue, with the rest as a parameter; queue_e133.py's code)
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
        """How many other users block, by E111's rule (idle_logins_e111.py). A count: a login never goes in a record."""
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
        if name == "SMOKE" and now >= self.sched["smoke_latest_ms"]:
            return "the smoke's latest start passed"
        if now >= self.no_start_after:
            return "no step starts after no_start_after_ms"
        if self.card_min + PLAN_MIN[name] > self.budget:
            return f"card budget: {self.card_min:.1f} used + {PLAN_MIN[name]} planned > {self.budget:.1f}"
        if now + PLAN_MIN[name] * 60000 > self.cutoff - 180000:
            return "it could not end before the cutoff"
        return None

    def wait_for(self, name):
        target = {"SMOKE": self.sched.get("smoke_not_before_ms", 0)}.get(name, 0)
        rest_s = (5 if (self.dry and REST_MIN[name]) else REST_MIN[name] * 60)
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
            self.rest_seen = {"last_busy_ms": busy, "history_age_s": age, "history_rows": seen,
                              "since_ref_min": round((now - ref) / 60000.0, 1) if ref else None, "waits": waits}
            return True

    def proto_path(self, name):
        return os.path.join(self.root, "tools/claims-v3/e144b", f"protocol-{name.lower()}{'-dry' if self.dry else ''}.json")

    def run_step(self, name):
        pdir = os.path.join(self.runs, name)
        os.makedirs(pdir, exist_ok=True)
        s0 = self.snapshot(pdir, "start")
        proto = self.proto_path(name)
        # the session's cap: its protocol's, never past what the budget leaves (minus 0.5 min for the queue's own reads)
        cap = min(float(json.load(open(proto))["caps"]["max_card_min"]), round(self.budget - self.card_min - 0.5, 1))
        cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/e144b/run_e144b.py"), "--protocol", proto, "--out", pdir,
               "--max-card-min", f"{cap:g}"]
        if self.dry:
            cmd.append("--dry")
        t0 = now_ms()
        self.rec("start", step=name, cmd=cmd[1:], rest=self.rest_seen, config=(s0 or {}).get("config"))
        self.status(state="running", step=name, t0_ms=t0)
        with open(os.path.join(pdir, "run.out"), "ab") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=self.root, start_new_session=True)
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
        try:
            end = json.load(open(os.path.join(pdir, "end.json")))
        except (OSError, ValueError):
            pass
        s1 = self.snapshot(pdir, "end")
        self.rec("end", step=name, rc=rc, end=end, cutoff_stopped=stopped, step_card_min=round((self.last_end_ms - t0) / 60000.0, 2),
                 card_min_total=round(self.card_min, 2), config=(s1 or {}).get("config"))
        return rc, stopped

    def check_smoke(self, rc):
        """None if the smoke is sound (exit 0, every launch rc 0, the config 65 W / 65 C at its end), else why not."""
        if rc != 0:
            return f"the smoke failed (exit {rc})"
        rd = os.path.join(self.runs, "SMOKE")
        try:
            launches = [json.loads(x) for x in open(os.path.join(rd, "launches.jsonl"))]
        except (OSError, ValueError) as e:
            return f"smoke records unreadable: {e}"
        work = [L for L in launches if L.get("role") == "work"]
        if len(work) != 3 or any(L.get("rc") != 0 for L in work):
            return f"smoke: {len(work)} work launches, rcs {[L.get('rc') for L in work]} (want 3, every rc 0)"
        if not self.dry:
            try:
                c = json.load(open(os.path.join(rd, "snapshot-end.json"))).get("config") or {}
            except (OSError, ValueError):
                c = {}
            if c.get("tdp_w") != 65 or c.get("temp_threshold_c") != 65:
                return f"smoke: config at its end {c}"
        return None

    def check_stoptest(self, name, kind):
        """None if the stop fired on live samples as registered, else why not (queue_e143.py's check_stoptest, ported)."""
        rd = os.path.join(self.runs, name)
        try:
            end = json.load(open(os.path.join(rd, "end.json")))
            marks = [json.loads(x) for x in open(os.path.join(rd, "marks.jsonl"))]
        except (OSError, ValueError) as e:
            return f"{name}: records unreadable: {e}"
        if end.get("exit") != 4 or not str(end.get("reason", "")).startswith(f"safety:{'board' if kind == 'board' else 'die'}"):
            return f"{name}: exit {end.get('exit')} ({end.get('reason')}), not a {kind} safety stop"
        trips = [m for m in marks if m.get("kind") == "safety_trip"]
        if not trips:
            return f"{name}: no safety_trip mark"
        t_trip = trips[0]["t_ms"]
        tel = []
        for p in sorted(os.listdir(os.path.join(rd, "tel"))):
            for ln in open(os.path.join(rd, "tel", p), errors="replace"):
                if ln.startswith("{"):
                    try:
                        d = json.loads(ln)
                    except ValueError:
                        continue
                    ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                    tel.append((d.get("t_ms"), d.get("board_w"), ms[0], ms[2] if len(ms) > 2 else None))
        tel = [x for x in tel if x[0] is not None]
        if not tel:
            return f"{name}: no sampler line"
        work = []
        try:
            work = [json.loads(x) for x in open(os.path.join(rd, "launches.jsonl")) if '"role": "work"' in x]
        except OSError:
            pass
        safety = json.load(open(self.proto_path(name))).get("safety", {})
        if kind == "board":
            cap, need = float(safety["board_cap_w"]), int(safety["cap_consecutive"])
            run, t_third = 0, None
            for t, w, _, _ in tel:
                run = run + 1 if (w is not None and w > cap) else 0
                if run >= need:
                    t_third = t
                    break
            if t_third is None:
                return f"{name}: no {need} sampler lines over {cap:g} W"
            if not -200 <= t_trip - t_third <= 1500:
                return f"{name}: the trip at {t_trip} is {t_trip - t_third} ms from the third live line over {cap:g} W"
            if not work:
                return f"{name}: no work launch recorded"
            L = work[0]
            if not (L["t_start_ms"] <= t_trip <= L["t_start_ms"] + 6500):
                return f"{name}: the trip at {t_trip} is not inside the work launch {L['t_start_ms']}-{L['t_end_ms']}"
            if L["t_end_ms"] - t_trip > 3000:
                return f"{name}: the launch ended {L['t_end_ms'] - t_trip} ms after the trip"
            self.rec("stoptest_detail", name=name, stop=kind, t_trip_ms=t_trip, t_third_line_ms=t_third, launch=[L["t_start_ms"], L["t_end_ms"]],
                     trip_after_line_ms=t_trip - t_third, launch_end_after_trip_ms=L["t_end_ms"] - t_trip, lines=len(tel))
            return None
        stop_c = float(safety["abs_stop_c"])
        first = next(((t, d, h) for t, _, d, h in tel if (d is not None and d >= stop_c) or (h is not None and h >= stop_c)), None)
        if first is None:
            return f"{name}: no sampler line at or above {stop_c:g} C"
        if not -200 <= t_trip - first[0] <= 1500:
            return f"{name}: the trip at {t_trip} is {t_trip - first[0]} ms from the first live line at or above {stop_c:g} C"
        if work:
            return f"{name}: a work launch ran before the die stop"
        self.rec("stoptest_detail", name=name, stop=kind, t_trip_ms=t_trip, t_first_line_ms=first[0], trip_after_line_ms=t_trip - first[0], lines=len(tel))
        return None

    def halt(self, why):
        open(os.path.join(self.runs, "QUEUE-HALT"), "a").write(json.dumps({"t_ms": now_ms(), "why": why}) + "\n")

    # -- the go gate: nothing touches the card before the claim (the Tailscale check may lapse at about 22:00 PST, so the go can come
    #    over ssh, RUNS/GO, or from the public repository: the marker tools/claims-v3/e144b/CLAIMED, committed on the Intel only after
    #    the #community-lab post names this card). Either way the files the queue runs must equal origin/main's, byte for byte.
    CODE = ["tools/claims-v3/e144b/run_e144b.py", "tools/claims-v3/e144b/queue_e144b.py"] + \
        [f"tools/claims-v3/e144b/protocol-{s.lower()}.json" for s in STEPS]

    def code_vs_origin(self):
        """(fetched, [paths that differ from origin/main]) after a `git fetch` of the public repository (https; no device, no ssh)."""
        rc, _, se = out(["git", "-C", self.root, "fetch", "-q", "origin", "main"], timeout=90)
        if rc != 0:
            return False, [f"fetch rc {rc}: {se.strip()[-160:]}"]
        bad = []
        for rel in self.CODE:
            try:
                r = subprocess.run(["git", "-C", self.root, "show", f"origin/main:{rel}"], capture_output=True, timeout=30,
                                   stdin=subprocess.DEVNULL)
                mine = open(os.path.join(self.root, rel), "rb").read()
                if r.returncode != 0 or hashlib.sha256(r.stdout).digest() != hashlib.sha256(mine).digest():
                    bad.append(rel)
            except (OSError, subprocess.SubprocessError):
                bad.append(rel)
        return True, bad

    def marker(self):
        rc, so, _ = out(["git", "-C", self.root, "show", "origin/main:tools/claims-v3/e144b/CLAIMED"], timeout=30)
        return so.strip() if rc == 0 else None

    def wait_go(self):
        if self.dry:
            return True
        gofile = os.path.join(self.runs, "GO")
        polls = 0
        while not self.stopped():
            if now_ms() >= self.sched["smoke_latest_ms"]:
                self.rec("no_go", why="no go by the smoke's latest start", polls=polls)
                return False
            polls += 1
            fetched, bad = self.code_vs_origin()
            mk = self.marker() if fetched else None
            go = os.path.exists(gofile)
            if go or mk:
                if fetched and bad:
                    self.rec("go_refused", why="the box's files differ from origin/main's", differ=bad, via="GO" if go else "CLAIMED")
                    self.halt("the box's files differ from origin/main's")
                    return False
                # (mk is only read after a fetch; a GO touched over ssh stands alone if the fetch failed, and says so)
                self.rec("go", via="GO" if go else "CLAIMED", marker=mk, code_checked=fetched, fetch_note=None if fetched else bad, polls=polls)
                return True
            self.status(state="waiting for the go (RUNS/GO or the CLAIMED marker on origin/main)", polls=polls, fetched=fetched)
            time.sleep(45)
        self.rec("no_go", why="QUEUE-STOP", polls=polls)
        return False

    def run(self):
        self.rec("queue_start", cutoff_ms=self.cutoff, no_start_after_ms=self.no_start_after, budget_card_min=self.budget,
                 steps=list(self.steps), python=sys.version.split()[0], sensors=bool(shutil.which("sensors")), dry=self.dry)
        th = threading.Thread(target=self.phone_loop, daemon=True)
        th.start()
        why = "done"
        safety = False
        if not self.wait_go():
            self.stop_phone.set()
            self.rec("queue_end", why="no go: nothing touched the card", card_min_total=0.0)
            self.status(state="ended", why="no go")
            return 0
        for name in self.steps:
            if safety and name not in ("END", "END2"):
                self.rec("skip", step=name, why="after a safety stop only END / END2 run")
                continue
            if not self.wait_for(name):
                if self.stopped() or now_ms() >= self.cutoff:
                    why = "stop or cutoff"
                    break
                if name in ("SMOKE",) + tuple(STOPTESTS):
                    why = f"no {name}: nothing else runs"
                    break
                continue
            rc, stopped = self.run_step(name)
            if name == "SMOKE":
                bad = self.check_smoke(rc)
                self.rec("smoke_check", rc=rc, bad=bad)
                if bad:
                    why = f"{bad}: nothing else runs"
                    self.halt(why)
                    break
                continue
            if name in STOPTESTS:
                bad = self.check_stoptest(name, STOPTESTS[name])
                self.rec("stoptest_check", name=name, rc=rc, bad=bad)
                if bad:
                    why = f"stop-path test failed: {bad}: nothing else runs"
                    self.halt(why)
                    break
                continue
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
            self.halt(why)
            break
        self.stop_phone.set()
        self.rec("queue_end", why=why, card_min_total=round(self.card_min, 2))
        self.status(state="ended", why=why)
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--root", default=os.path.join(HERE, "..", "..", ".."))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--steps", default=None, help="a comma list of steps (default " + ",".join(STEPS) + ")")
    a = ap.parse_args()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    return Queue(a).run()


if __name__ == "__main__":
    sys.exit(main())
