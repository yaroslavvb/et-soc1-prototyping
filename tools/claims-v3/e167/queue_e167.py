#!/usr/bin/env python3
"""E167 (Q141(h)): the session's queue, detached on aifoundry2, registered in E167.md (7ba987b3). It is E161's queue (queue_e161.py:
E144b's, E133's, E111's rules unchanged, E160's smoke check of the C log and its DMA rule), with E167's names and two changes (E167.md
D1, D3):
  * G1Q's start gate: a G1Q session that ends with exit 6 ("gate", run_e167.py: its REST anchor read above 49.0 C) is recorded as G1Q NOT
    RUN (the start gate); END is skipped (no hold ran) and the queue goes on to the 15-minute rest and G2Q. G1Q's plan is 19.6 card-minutes
    (E161: 15.6), for the REST's wait of at most 240 s; the budget stays 40.
  * under --dry the camera phone is not read (a desk dry pass makes no network call); a real session reads it once a minute, as E161's did.
It depends on no ssh: once started it needs nothing from outside.

    setsid nohup python3 tools/claims-v3/e167/queue_e167.py --schedule <schedule.json> --runs build/e167/runs \
        > build/e167/queue.out 2>&1 < /dev/null &

The go gate: nothing touches the card until RUNS/GO exists (touched over ssh after the claim) or the marker tools/claims-v3/e167/CLAIMED
is on origin/main of the public repository (committed on the Intel only after the #community-lab post names this card). At the go, every
file the queue runs must equal origin/main's byte for byte, or the queue halts. No go by the smoke's latest start: nothing runs.

Steps, in this order, on epoch ms, each a run_e167.py session of its protocol: SMOKE (E144b's smoke through the C-logging wrapper, its C log
and DMA rule checked), STOPTEST-DIE, STOPTEST-BOARD (the stop paths on live samples), G1Q (REST with its 49 C start gate, then 93 processes
of int8.b_line_zero_ff behind E98's 57 C gate), END (G1Q's cool-down), G2Q (REST, then 91 processes of fp32.real_smol_softmax_v_causal from at
once, governed), END2. Before G1Q and G2Q, E98's rest rule: 15 minutes with no launch, from the box's own 5 s history. What stops a step,
the exit codes, the hard stop and the budget are E161's (E161's queue's docstring holds the full text); exit 6 is G1Q's gate (above).
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
import statistics  # noqa: E402

LOCK = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
IDLE_W_BAR = 26.0
IDLE_DIE_BAR = 55
POLL_S = 20
STEPS = ("SMOKE", "STOPTEST-DIE", "STOPTEST-BOARD", "G1Q", "END", "G2Q", "END2")
PLAN_MIN = {"SMOKE": 1.0, "STOPTEST-DIE": 0.5, "STOPTEST-BOARD": 0.5, "G1Q": 19.6, "END": 2.1, "G2Q": 15.7, "END2": 2.1}
EXIT_GATE = 6                      # run_e167.py: G1Q's start gate
REST_MIN = {"SMOKE": 0, "STOPTEST-DIE": 0, "STOPTEST-BOARD": 0, "G1Q": 15, "END": 0, "G2Q": 15, "END2": 0}
CC_HOST_SHA256 = "eae32a152b8f0861bd2922c500eac217c931c9b464d3274a6bcf346cc986bfd2"   # e160_common.py CC_HOST_SHA256 (E160's host)
KERNEL_SHA256 = "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24"    # E80's build/sparsity_t2/kernel/sparsity.elf
ZERO_C_HEX = "0" * 2048
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


def health(dry=False):
    if dry:
        return {"dry": True, "note": "no camera read in a dry pass (E167.md D3)"}
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
            d = dict(t_ms=now_ms(), **health(self.dry))
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
        snap = {"tag": tag, "t_ms": now_ms(), "zone": time.strftime("%Z"), "phone": health(self.dry)}
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
        return os.path.join(self.root, "tools/claims-v3/e167", f"protocol-{name.lower()}{'-dry' if self.dry else ''}.json")

    def run_step(self, name):
        pdir = os.path.join(self.runs, name)
        os.makedirs(pdir, exist_ok=True)
        s0 = self.snapshot(pdir, "start")
        proto = self.proto_path(name)
        # the session's cap: its protocol's, never past what the budget leaves (minus 0.5 min for the queue's own reads)
        cap = min(float(json.load(open(proto))["caps"]["max_card_min"]), round(self.budget - self.card_min - 0.5, 1))
        cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/e167/run_e167.py"), "--protocol", proto, "--out", pdir,
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
        if self.dry:
            self.rec("smoke_ccheck", skipped="dry: the toy card runs no host and writes no C log")
            return None
        return self.check_smoke_clog(rd, launches)

    def check_smoke_clog(self, rd, launches):
        """E160's smoke check of the C log (queue_e160.py's check_smoke_clog, ported): the host records, a C record for every SPARSITY line
        (poison written, no mask, no stream, one group holding every minion), the fp32 zeros run's C = +0, and the DMA rule. None if both
        hold, else why not. Writes rd/smoke-ccheck.json."""
        p = os.path.join(rd, "c-log.jsonl")
        if not os.path.exists(p):
            return "smoke: no C log (c-log.jsonl)"
        recs = []
        for ln in open(p, errors="replace"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                recs.append(json.loads(ln))
            except ValueError:
                recs.append(None)
        if any(r is None for r in recs):
            return "smoke: a C log line is cut short or not JSON"
        hosts = [r for r in recs if r.get("kind") == "host"]
        crec = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in recs if r.get("kind") == "c"}
        work = [L for L in launches if L.get("role") == "work"]
        if len(hosts) < len(work):
            return f"smoke: {len(hosts)} host records in the C log for {len(work)} work processes"
        for h in hosts:
            if h.get("host_sha256") != CC_HOST_SHA256 or h.get("kernel_sha256") != KERNEL_SHA256 or h.get("kernel_from") != "runner":
                return (f"smoke: the C log's host record names {h.get('host_sha256')} / {h.get('kernel_sha256')} ({h.get('kernel_from')}), "
                        "not the pinned host and E80's kernel")
        n_lines, gaps, why = 0, [], None
        for L in work:
            sp = L.get("sparsity") or []
            gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(sp, sp[1:])]
            zeros = "fp32/zeros.bin" in str((L.get("cmd") or [])) or str(L.get("run", "")).endswith("fp32-zeros-r1")
            for s in sp:
                n_lines += 1
                r = crec.get((s.get("t_start_ms"), s.get("t_end_ms")))
                if r is None:
                    why = why or f"smoke: {L.get('run')} launch {s.get('launch')} has no C record"
                    continue
                g = r.get("groups") or []
                if not (r.get("ok") and r.get("poison") and r.get("use_mask") == 0 and r.get("b_stream") == 0):
                    why = why or (f"smoke: {L.get('run')} launch {s.get('launch')}: C record ok {r.get('ok')} poison {r.get('poison')} "
                                  f"mask {r.get('use_mask')} stream {r.get('b_stream')}")
                elif len(g) != 1 or g[0].get("count") != r.get("participants") or r.get("participants") != s.get("minions"):
                    why = why or (f"smoke: {L.get('run')} launch {s.get('launch')}: {len(g)} C groups, {[x.get('count') for x in g]} of "
                                  f"{r.get('participants')} minions")
                elif zeros and g[0].get("hex") != ZERO_C_HEX:
                    why = why or f"smoke: {L.get('run')} launch {s.get('launch')}: the zeros tile's C is not +0 (first bytes {str(g[0].get('hex'))[:24]})"
        dma = json.load(open(self.proto_path("SMOKE"))).get("dma") or {}
        res = {"c_records": len(crec), "sparsity_lines": n_lines, "host_records": len(hosts), "gaps_ms": gaps}
        if why is None and gaps:
            med = statistics.median(gaps)
            delta = med - float(dma["e144b_smoke_gap_ms_median"])
            proj = float(dma["e144b_hold_held_s_max"]) + int(dma["launches"]) * max(0.0, delta) / 1000.0
            res.update(gap_ms_median=med, delta_ms=round(delta, 3), projected_held_max_s=round(proj, 3), limit_s=dma["projected_held_max_s"])
            if proj > float(dma["projected_held_max_s"]):
                why = (f"smoke: the C log adds {delta:.1f} ms a launch; E144b's longest hold process would hold the device {proj:.2f} s, over "
                       f"{dma['projected_held_max_s']} s of the {dma['budget_s']} s budget")
        elif why is None:
            why = "smoke: no launch gap to time the C log's DMA"
        res["why"] = why
        json.dump(res, open(os.path.join(rd, "smoke-ccheck.json"), "w"), indent=1)
        self.rec("smoke_ccheck", **{k: v for k, v in res.items() if k != "gaps_ms"})
        return why

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

    # -- the go gate: nothing touches the card before the claim (the box may become unreachable from the Intel later in the day, so the go can come
    #    over ssh, RUNS/GO, or from the public repository: the marker tools/claims-v3/e167/CLAIMED, committed on the Intel only after
    #    the #community-lab post names this card). Either way the files the queue runs must equal origin/main's, byte for byte.
    CODE = ["tools/claims-v3/e167/run_e167.py", "tools/claims-v3/e167/queue_e167.py"] + \
        [f"tools/claims-v3/e167/protocol-{s.lower()}.json" for s in STEPS]

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
        rc, so, _ = out(["git", "-C", self.root, "show", "origin/main:tools/claims-v3/e167/CLAIMED"], timeout=30)
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
        gated = False
        for name in self.steps:
            if gated and name == "END":
                self.rec("skip", step=name, why="G1Q's hold did not run (the start gate): no cool-down to read")
                gated = False
                continue
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
            if name == "G1Q" and rc == EXIT_GATE:
                end = None
                try:
                    end = json.load(open(os.path.join(self.runs, "G1Q", "end.json")))
                except (OSError, ValueError):
                    pass
                self.rec("gate", step="G1Q", rc=rc, end=end, note="G1Q NOT RUN (the start gate, E167.md G1): END is skipped, G2Q follows")
                gated = True
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
