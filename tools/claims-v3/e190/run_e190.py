#!/usr/bin/env python3
"""E190's runner (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): one arm's whole session, in E189's runner form (one sampler for
the session, the stop lines fed live, the stop-path test, the gates, the closing bound), running E136's rgm136 (built today into build/e190rgm)
in the registered order. Python's own modules only (the box's system python3). session_e190.sh starts it, detached.

    python3 -B tools/claims-v3/e190/run_e190.py session --arm A|B --t0 T0 --out build/e190/T<T0>-<arm> [--deadline-epoch E]
    python3 -B tools/claims-v3/e190/run_e190.py session --dry --arm A|B --t0 T0 --out DIR [--sequence plan|short|bursts|e2e]
        [--rest-s S --smoke-rest-s S --tail-s S --gate-wait-s S --rule-s S --cap-s S]   (the last six and --sequence in --dry only)

What a session does (E190.md sections 3, 6-8; plan-e190.json), from the box tree's root (aifoundry2 ~/claude/et-soc1-prototyping, arm A;
aifoundry1 ~/nekko, arm B):
  1. checks the box and the build: the hostname is the arm's; build/e190rgm's kernel ELF at the registration's pin, its host at the sha256
     build_e190.sh recorded today (BUILD-e190.json, written today, every behaviour check passed), the arm's telemetry reader at its pin, the
     three tiles at kinds.json's sha256; else no device is opened;
  2. takes the arm's card lock (flock -n: /run/lock/etsoc-shire0.lock, arm A; etsoc-shire1.lock, arm B; held by this process to the end),
     reads et-who and the processes (a holder of another login on the arm's card, another user's device process on aifoundry2, a CI job, or
     any other device process of ours, or anything of ours on aifoundry1's card 0: no device opened);
  3. THE FIRST CARD COMMAND: `ettelem config` through the guard under `timeout 10` (arm A 65 W / 65 C; arm B 65 W / 65 C / 600 MHz, the
     clock its 70 W line is reckoned at; else the session ends at the gate, no launch); the card time counts from it (E190.md 7);
  4. the sampler, `ettelem sample --every-ms 100` through the guard, ONE process for the session (restarted as lib.sh does if it dies,
     while a run could still start), every line written to telemetry.jsonl and fed to THE STOP LINES (e190_common.Stops) as it arrives:
     arm A board above 85 W on 3 samples in a row, arm B above 75 W on 3; the die (the shires' mean or the hottest sensor) at or above 80 C
     on one sample. A trip touches the hosts' --stop-file at once (a running host ends at its next ~0.5 s launch boundary; no process is
     ever killed) and nothing further starts;
  5. THE STOP-PATH TEST (E190.md 7: "the stop tests on live samples first"): each line again with a test threshold every live sample
     crosses (board 0 W on 3 samples; 0 C) must trip on the live sampler within 5 s, touch its own test file and refuse a start; else no
     process starts;
  6. THE SMOKE: 30 s at rest (the session's rest reading: arm B's gates are formed from its die), then one 2 s process per format (fp32,
     fp16, int8 random), each rc 0 with every launch ok, its check of C exact or approx, its cycles an op within 50-250% of the frozen point
     at the arm's clock (R0's tie); any failure ends the session at the gate;
  7. the runs, plan-e190.json's order (P1, S1, P2, S2, P3, S3, P4, S4, S5, S6): each run the die gate (arm A 55 C / 57 C; arm B min(63, rest
     die + 3) / min(64, rest die + 4); at most 300 s, else skipped: NO DATA), the holders again, 10 s at rest, ONE process (a burst) or
     TWELVE back to back (a sustained run), each `timeout 10 sparsity_host ... --seconds 6 --budget 7.5`, then 4 s read (the kit's tail);
     no run starts once the card time passes 35 minutes or within its planned length of the window's last end; a started run is cut only
     by a stop;
  8. the closing, bounded by the 40-minute cap: the sampler stopped (SIGTERM only), the closing `ettelem config`, "session end", the lock
     released, queue.json, MANIFEST.sha256 last.
Every device command is a READ: the host opens the ops node only; ettelem config and sample through the guard (it refuses --reset-ms and
anything else before the device opens). No set, no reset, no statistics reset, no firmware-revisions query, no residency read.
--dry swaps every device-opening process for fake_card_e190.py's doubles, takes a lock file in the output directory, skips the box and
build checks, and marks every line DRY. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import fcntl
import gzip
import hashlib
import json
import os
import pwd
import re
import signal
import socket
import statistics
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e190_common as C  # noqa: E402

ROOT = C.REPO
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
CI_COMM = re.compile(r"^Runner\.Worker$")


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def pacific_day():
    """Today by the Pacific calendar (the day build_e190.sh writes with TZ=America/Los_Angeles)."""
    try:
        from zoneinfo import ZoneInfo
        import datetime
        return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    except Exception:  # noqa: BLE001 -- no tz database: the box's own calendar
        return time.strftime("%Y-%m-%d", time.localtime())


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Session:
    def __init__(self, a):
        self.a = a
        self.arm = a.arm
        self.A = C.ARMS[a.arm]
        self.dry = a.dry
        self.out = os.path.abspath(a.out)
        os.makedirs(self.out, exist_ok=True)
        self.stop_file = os.path.join(self.out, "STOP")
        self.log_f = open(os.path.join(self.out, "session.log"), "a")
        self.stops = C.Stops(**C.stops_of(a.arm), trip_file=self.stop_file)
        self.test_stops = None
        self.samples = []              # (t_ms, line) of the whole session
        self.last = None
        self.lock = threading.Lock()
        self.sproc = None
        self.sampler_t0 = None
        self.tel = open(os.path.join(self.out, "telemetry.jsonl"), "a")
        self.queue = []
        self.t_first = None
        self.device_opened = False
        self.rest_die = None
        self.env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
        self.env.pop("V3_DEVICE", None)
        self.env.pop("ET_DEVICES", None)
        if self.A["et_devices"] is not None:
            self.env["ET_DEVICES"] = self.A["et_devices"]
        if self.dry:
            self.env["E190_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            self.env["E190_FAKE_ARM"] = self.arm
            open(self.env["E190_FAKE_SCHED"], "a").close()
        if os.path.exists(self.stop_file):
            os.remove(self.stop_file)

    # ------------------------------------------------------------------ the log, in the kits' form
    def say(self, words):
        w = ("DRY " + words) if self.dry and not words.startswith("session start") else words
        line = f"{stamp()} {w}"
        self.log_f.write(line + "\n")
        self.log_f.flush()
        print(line, flush=True)

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def fake(self, *words):
        return [sys.executable, "-B", os.path.join(HERE, "fake_card_e190.py")] + list(words)

    def cmd_config(self):
        return self.fake("config") if self.dry else ["timeout", str(C.HOST_TIMEOUT_S), "bash", C.GUARD, "config"]

    def cmd_sampler(self, seconds):
        w = ["sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)]
        return self.fake(*w) if self.dry else ["bash", C.GUARD] + w

    def cmd_etwho(self):
        return self.fake("etwho") if self.dry else ["timeout", "20", "et-who"]

    def host_cmd(self, argv):
        if self.dry:
            return ["timeout", str(C.HOST_TIMEOUT_S)] + self.fake("host") + argv[1:]
        return ["timeout", str(C.HOST_TIMEOUT_S)] + argv

    # ------------------------------------------------------------------ holders (counts, never names)
    def foreign(self, with_etwho=True):
        """'' when nothing blocks the arm's card, else why (counts only). Arm A (aifoundry2, one card): any holder line of another login,
        another user's device process, a CI job, another device process of ours. Arm B (aifoundry1, two cards): a holder line of another
        login on card 1's nodes or lock, ANY holder line of ours on card 0 (never two of our sessions on aifoundry1), a CI job, another
        device process of ours; another login on card 0 does not block (k6's holder rule there)."""
        me = pwd.getpwuid(os.getuid()).pw_name      # our login, as et-who prints it (never written anywhere)
        why = []
        if with_etwho:
            try:
                w = subprocess.run(self.cmd_etwho(), cwd=ROOT, capture_output=True, text=True, timeout=30, env=self.env)
                lines = w.stdout.splitlines()
            except (OSError, subprocess.TimeoutExpired) as e:
                return f"et-who unreadable ({type(e).__name__})"
            card = "1" if self.arm == "B" else "0"
            hold = [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]
            def on_card(f, c):
                return f[0].startswith(f"/dev/et{c}_") or f[0] == f"lock:etsoc-shire{c}.lock"
            if self.arm == "A":
                n_other = sum(1 for f in hold if f[1] != me)
                n_ours0 = 0
            else:
                n_other = sum(1 for f in hold if f[1] != me and on_card(f, card))
                n_ours0 = sum(1 for f in hold if f[1] == me and on_card(f, "0"))
            if n_other:
                why.append(f"{n_other} holder line(s) of another login on the card")
            if n_ours0:
                why.append(f"{n_ours0} holder line(s) of ours on card 0 (never two of our sessions on aifoundry1)")
        if not self.dry:
            mine = {os.getpid()}
            if self.sproc is not None:
                mine.add(self.sproc.pid)
            uid = os.getuid()
            n_oth = n_ci = n_ours = 0
            ps = subprocess.run(["ps", "-eo", "uid=,pid=,state=,comm="], capture_output=True, text=True).stdout.splitlines()
            for ln in ps:
                f = ln.split(None, 3)
                if len(f) != 4:
                    continue
                try:
                    u, pid = int(f[0]), int(f[1])
                except ValueError:
                    continue
                comm = f[3].strip()
                if f[2].upper().startswith("Z") or pid in mine:
                    continue
                if CI_COMM.search(comm):
                    n_ci += 1
                elif u != uid and DEV_COMM.search(comm) and self.arm == "A":
                    n_oth += 1
                elif u == uid and DEV_COMM.search(comm):
                    n_ours += 1
            if n_oth:
                why.append(f"{n_oth} other users' device process(es)")
            if n_ci:
                why.append(f"{n_ci} CI job(s)")
            if n_ours:
                why.append(f"{n_ours} other device process(es) of ours")
        elif os.environ.get("E190_FAKE_PS") in ("other", "ours", "ci"):
            why.append({"other": "1 other users' device process(es)", "ours": "1 other device process(es) of ours",
                        "ci": "1 CI job(s)"}[os.environ["E190_FAKE_PS"]])
        return "; ".join(why)

    # ------------------------------------------------------------------ the sampler and the live stops
    def _reader(self, proc):
        for raw in proc.stdout:
            if not raw.startswith("{"):
                continue
            try:
                s = json.loads(raw)
            except ValueError:
                continue
            self.tel.write(raw if raw.endswith("\n") else raw + "\n")
            with self.lock:
                self.samples.append((s.get("t_ms", 0), raw.rstrip("\n")))
                self.last = s
            if "stop" in self.stops.feed(s):
                self.mark("safety_trip", self.stops.stop, t_sample_ms=s.get("t_ms"))
            ts = self.test_stops
            if ts is not None:
                ts.feed(s)
        self.tel.flush()

    def mark(self, kind, detail, **kw):
        with open(os.path.join(self.out, "marks.jsonl"), "a") as f:
            f.write(json.dumps(dict(t_ms=now_ms(), kind=kind, detail=detail, **kw)) + "\n")

    def close_deadline(self):
        """The session's end bound: the cap (40 card-minutes) from the first card command."""
        return self.t_first + self.a.cap_s if self.t_first else None

    def start_sampler(self):
        secs = C.CAP_S + 600
        for attempt in range(1, 7):
            if attempt > 1 and self.t_first and self.may_start(60):
                self.say(f"the sampler: no attempt {attempt} ({self.may_start(60)}): no run can start")
                break
            err = open(os.path.join(self.out, "sampler.err"), "a")
            self.sproc = subprocess.Popen(self.cmd_sampler(secs), cwd=ROOT, stdout=subprocess.PIPE, stderr=err,
                                          stdin=subprocess.DEVNULL, text=True, env=self.env)
            n0 = len(self.samples)
            threading.Thread(target=self._reader, args=(self.sproc,), daemon=True).start()
            t = time.time()
            while time.time() - t < 10:
                if len(self.samples) > n0:
                    self.say(f"sampler started (attempt {attempt}, pid {self.sproc.pid}, every {C.EVERY_MS} ms)")
                    return True
                if self.sproc.poll() is not None:
                    break
                time.sleep(0.25)
            self.stop_sampler(self.close_deadline())
            time.sleep(2)
        return False

    def sampler_alive(self):
        return self.sproc is not None and self.sproc.poll() is None

    def stop_sampler(self, deadline=None):
        """SIGTERM only (never kill -9 a tool): 30 s, then once more and 60 s; each wait ends C.CLOSE_S / 2 before the end bound but lasts
        at least 2 s; a sampler that will not stop is recorded."""
        p = self.sproc
        if not p:
            return True
        for n, wait_s in enumerate((30.0, 60.0)):
            if p.poll() is None:
                if deadline:
                    wait_s = min(wait_s, max(2.0, deadline - C.CLOSE_S / 2 - time.time()))
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=wait_s)
                except subprocess.TimeoutExpired:
                    if n == 0:
                        self.say(f"the sampler did not stop within {wait_s:.0f} s of SIGTERM: SIGTERM once more")
                    continue
            break
        ok = p.poll() is not None
        if not ok:
            self.say("the sampler did not stop on SIGTERM: left running, recorded (no kill -9)")
        self.sproc = None
        return ok

    def ensure_sampler(self):
        if self.sampler_alive():
            return True
        why = self.may_start(60) if self.t_first else ""
        if why:
            self.say(f"the sampler is not running; not restarted: no run can start ({why})")
            return False
        self.say("the sampler is not running: restarting it")
        return self.start_sampler()

    def latest(self):
        with self.lock:
            return dict(self.last) if self.last else None

    def window(self, t0_ms, t1_ms):
        with self.lock:
            return [json.loads(ln) for (t, ln) in self.samples if t0_ms <= t <= t1_ms]

    def nap(self, seconds):
        """Sleep, watching the stop lines; False (at once) if a stop tripped meanwhile: before a process, a stop starts nothing."""
        end = time.time() + seconds
        while time.time() < end:
            if self.stops.stop:
                return False
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    def idle(self, seconds):
        """The read AFTER a run's last process: it runs to its end whatever the stop lines say (no launch happens in it)."""
        end = time.time() + seconds
        while time.time() < end:
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    # ------------------------------------------------------------------ the gates
    def may_start(self, seconds):
        """A run (or the smoke's next process) may start: no stop; the card time under the 35-minute rule; its planned length inside the
        cap less the closing; before the window's last end."""
        if self.stops.stop or (self.test_stops is not None and self.test_stops.stop):
            return "a stop line has tripped"
        el = time.time() - self.t_first
        if el > self.a.rule_s:
            return f"the card-time rule: {el / 60:.1f} card-minutes since the first card command (no run after {self.a.rule_s / 60:g})"
        if el + seconds > self.a.cap_s - C.CLOSE_S:
            return f"the cap: {el / 60:.1f} card-minutes + {seconds:.0f} s would pass {self.a.cap_s / 60:g} less the closing"
        if self.a.deadline_epoch and time.time() + seconds + 90 > self.a.deadline_epoch:
            return "the window's last end is too close"
        return ""

    def die_gate(self, gate, planned):
        """The latest live sample's shires' mean at or below the gate, waiting at most --gate-wait-s and never past the card-time rule, the
        window or a stop; returns (ok, die, waited_s, why), why naming what ended the wait when it was not the die nor the 300 s."""
        t = time.time()
        while True:
            s = self.latest()
            die = C.die_of(s) if s else None
            if die is not None and gate is not None and die <= gate:
                return True, die, time.time() - t, ""
            why = self.may_start(planned)
            if why:
                return False, die, time.time() - t, why
            if time.time() - t >= self.a.gate_wait_s:
                return False, die, time.time() - t, ""
            if not self.ensure_sampler():
                return False, die, time.time() - t, "the sampler is not running"
            time.sleep(0.5)

    # ------------------------------------------------------------------ reads
    def config(self, name, bound_s=30):
        try:
            r = subprocess.run(self.cmd_config(), cwd=ROOT, capture_output=True, text=True, timeout=bound_s, env=self.env)
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, f"config read failed ({type(e).__name__})"
        j = C.last_json(r.stdout)
        with open(os.path.join(self.out, f"config-{name}.json"), "w") as f:
            f.write(json.dumps(j) + "\n")
        if r.returncode != 0 or not j:
            return None, f"config read rc {r.returncode}, no JSON line"
        return j, ""

    # ------------------------------------------------------------------ one host process
    def run_proc(self, argv, d, name, kind):
        os.makedirs(d, exist_ok=True)
        env = dict(self.env, E190_FAKE_KIND=kind) if self.dry else self.env     # the doubles' watts by the run's kind (--dry only)
        t0 = now_ms()
        with open(os.path.join(d, name + ".out"), "w") as so, open(os.path.join(d, name + ".err"), "w") as se:
            try:
                rc = subprocess.run(self.host_cmd(argv), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=env,
                                    timeout=C.HOST_TIMEOUT_S + 20).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        t1 = now_ms()
        self.device_opened = True
        with open(os.path.join(d, name + ".out")) as f:
            text = f.read()
        sp = C.parse_sparsity(text)
        chk = [x for x in sp if x.get("test") == "check"]
        fma = [x for x in sp if x.get("test") == "fma"]
        return {"name": name, "argv": argv, "rc": rc, "t0_ms": t0, "t1_ms": t1, "n_launch": len(fma),
                "launches_ok": bool(fma) and all(x.get("ok") for x in fma),
                "check": chk[-1].get("result") if chk else None, "check_ok": bool(chk) and bool(chk[-1].get("ok")),
                "check_cycles_per_op": chk[-1].get("cycles_per_op") if chk else None,
                "stopped_by_file": "stopping:" in open(os.path.join(d, name + ".err")).read()}

    # ------------------------------------------------------------------ the stop-path test
    def stop_path_test(self):
        res = {}
        st = C.stops_of(self.arm)
        for line, kw in (("board", {"board_cap_w": 0.0, "cap_consecutive": st["cap_consecutive"], "abs_stop_c": 999.0}),
                         ("die", {"board_cap_w": 999.0, "cap_consecutive": st["cap_consecutive"], "abs_stop_c": 0.0})):
            tf = os.path.join(self.out, f"STOPTEST-{line}")
            self.test_stops = C.Stops(**kw, trip_file=tf)
            t = time.time()
            while time.time() - t < 5 and not self.test_stops.stop:
                time.sleep(0.1)
            tripped = bool(self.test_stops.stop)
            refused = bool(self.may_start(0))
            res[line] = {"tripped": tripped, "why": self.test_stops.stop, "test_file_touched": os.path.exists(tf),
                         "refused_a_start": refused, "s": round(time.time() - t, 2), "t_trip_ms": self.test_stops.t_trip}
            self.test_stops = None
        ok = all(v["tripped"] and v["refused_a_start"] and v["test_file_touched"] for v in res.values()) and not self.stops.stop \
            and not os.path.exists(self.stop_file)
        with open(os.path.join(self.out, "stop-path.json"), "w") as f:
            json.dump({"ok": ok, "lines": res, "real_lines": st}, f, indent=1)
        return ok, res

    # ------------------------------------------------------------------ the smoke
    def smoke(self):
        d0 = os.path.join(self.out, "smoke")
        os.makedirs(d0, exist_ok=True)
        t0 = now_ms()
        self.say(f"smoke: {self.a.smoke_rest_s:g} s at rest (the session's rest reading)")
        ok = self.nap(self.a.smoke_rest_s)
        t1 = now_ms()
        win = self.window(t0, t1)
        dies = [C.die_of(s) for s in win if C.die_of(s) is not None]
        bws = [s.get("board_w") for s in win if s.get("board_w") is not None]
        self.rest_die = statistics.median(dies) if dies else None
        rest = {"t0_ms": t0, "t1_ms": t1, "samples": len(win), "board_w_median": statistics.median(bws) if bws else None,
                "die_median_c": self.rest_die, "gates": {k: C.gate_c(self.arm, k, self.rest_die) for k in C.KINDS}}
        with open(os.path.join(d0, "rest.json"), "w") as f:
            json.dump(rest, f, indent=1)
        self.say(f"smoke rest: {len(win)} samples, board {rest['board_w_median']} W, die {self.rest_die} C; gates {rest['gates']}")
        if not ok:
            return False, f"a stop during the rest reading: {self.stops.stop}"
        if not win or self.rest_die is None:
            return False, "no live sample in the rest reading"
        fc = C.forecast()
        f = C.ARMS[self.arm]["clock_mhz"]
        sec, bud, _ = C.proc_form("smoke")
        for fmt in C.FMTS:
            why = self.may_start(15)
            if why:
                return False, f"{fmt}: not started ({why})"
            argv = C.host_argv(ROOT, fmt, sec, bud, self.stop_file)
            p = self.run_proc(argv, os.path.join(d0, fmt), "proc", "burst")
            pt = fc["speed"][fmt][f"T{f}_us"]["point"] * f
            cpo = p["check_cycles_per_op"]
            ratio = cpo / pt if cpo else None
            good = p["rc"] == 0 and p["launches_ok"] and p["check"] in ("exact", "approx") and p["check_ok"] and \
                ratio is not None and C.CYC_LO <= ratio <= C.CYC_HI
            with open(os.path.join(d0, fmt, "smoke.json"), "w") as fo:
                json.dump(dict(p, cycles_point=pt, cycles_ratio=ratio, good=good), fo, indent=1)
            self.say(f"smoke {fmt}: rc {p['rc']}, {p['n_launch']} launches, check {p['check']}, cycles an op {cpo} "
                     f"({'%.2f' % ratio if ratio else '-'} of the point): {'ok' if good else 'FAILED'}")
            if not good:
                return False, f"{fmt}: rc {p['rc']}, check {p['check']}, cycles ratio {ratio}"
            if self.stops.stop:
                return False, f"a stop line tripped during the smoke's {fmt}: {self.stops.stop}"
        return True, ""

    # ------------------------------------------------------------------ one run
    def one_run(self, i, blk, kind, fmt, rep):
        key = f"{i:02d}-{blk}-{kind}-{fmt}"
        d = os.path.join(self.out, "runs", key)
        planned = C.run_plan_s(kind, fmt)
        base = {"i": i, "block": blk, "kind": kind, "format": fmt, "rep": rep, "cell": f"{fmt}.{kind}", "arm": self.arm, "run": key}
        why = self.may_start(planned)
        if why:
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        gate = C.gate_c(self.arm, kind, self.rest_die)
        ok, die, waited, gwhy = self.die_gate(gate, planned)
        if not ok:
            w = gwhy or f"the die gate: {die} C after {waited:.0f} s (gate {gate} C)"
            self.say(f"run {key}: not started ({w}): no data")
            return dict(base, ran=False, why=w, gate={"c": gate, "die": die, "waited_s": round(waited, 1)})
        why = self.may_start(planned)
        if why:
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        f = self.foreign()
        if f:
            self.stops.stop = self.stops.stop or f"a holder or a device process: {f}"
            self.say(f"STOP before run {key}: {f}")
            return dict(base, ran=False, why=f)
        os.makedirs(d, exist_ok=True)
        sec, bud, nproc = C.proc_form(kind)
        self.say(f"run {key}: {nproc} x {sec:g} s {fmt} (gate {gate} C, die {die} C after {waited:.0f} s)")
        r0 = now_ms()
        clean = self.nap(self.a.rest_s)
        r1 = now_ms()
        rec = dict(base, gate={"c": gate, "die": die, "waited_s": round(waited, 1)}, rest={"t0_ms": r0, "t1_ms": r1}, procs=[],
                   flags=[])
        if not clean:
            self.say(f"run {key}: a stop tripped in its rest read: no process started")
            rec.update(ran=False, why="stop: " + str(self.stops.stop))
            with open(os.path.join(d, "run.json"), "w") as fo:
                json.dump(rec, fo, indent=1)
            return rec
        argv = C.host_argv(ROOT, fmt, sec, bud, self.stop_file)
        fails = 0
        for k in range(nproc):
            if k > 0:
                if self.stops.stop:
                    rec["flags"].append(f"a stop after process {k - 1}: {self.stops.stop}")
                    break
                f = self.foreign(with_etwho=False)
                if f:
                    self.stops.stop = self.stops.stop or f"a device process: {f}"
                    rec["flags"].append(f"a device process before process {k}: {f}")
                    break
            p = self.run_proc(argv, d, f"proc-{k:02d}", kind)
            rec["procs"].append(p)
            if p["rc"] != 0:
                fails += 1
                rec["flags"].append(f"process {k} rc {p['rc']}")
                if fails >= 2:
                    self.stops.stop = self.stops.stop or f"two processes of run {key} failed"
                    break
        w1 = now_ms()
        self.idle(self.a.tail_s)
        rec.update(ran=True, work={"t0_ms": rec["procs"][0]["t0_ms"] if rec["procs"] else r1, "t1_ms": w1}, tail_end_ms=now_ms(),
                   stop=self.stops.stop)
        if self.stops.stop:
            rec["flags"].append(f"a stop line tripped during this run: {self.stops.stop}")
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(rec, fo, indent=1)
        self.say(f"run {key} done: {len(rec['procs'])} process(es), rc {[p['rc'] for p in rec['procs']]}, checks "
                 f"{sorted({str(p['check']) for p in rec['procs']})}{', ' + '; '.join(rec['flags']) if rec['flags'] else ''}")
        return dict(base, ran=True, n_procs=len(rec["procs"]), rcs=[p["rc"] for p in rec["procs"]], flags=rec["flags"])

    # ------------------------------------------------------------------ the box and the build (never under --dry)
    def box_check(self):
        """'' when the box, the build and the readers are the registered ones, else why (no device is opened)."""
        host = socket.gethostname().split(".")[0]
        if host != self.A["box"]:
            return f"this host is {host!r}, not arm {self.arm}'s {self.A['box']!r}"
        bad = []
        try:
            rec = C.load(os.path.join(ROOT, C.BUILD_REC))
        except (OSError, ValueError):
            return f"no build record {C.BUILD_REC}: run build_e190.sh (the runbook's build step) first"
        today = pacific_day()
        if rec.get("day") != today or rec.get("verdict") != "BUILT" or rec.get("box") != self.A["box"]:
            bad.append(f"the build record is not today's BUILT on {self.A['box']} ({rec.get('day')}, {rec.get('verdict')}, {rec.get('box')})")
        for rel, want in ((C.ELF, C.KERNEL_PIN), (C.HOST, rec.get("host_sha256")), (self.A["ettelem"], self.A["ettelem_sha256"])):
            p = os.path.join(ROOT, rel)
            got = sha256(p) if os.path.isfile(p) else None
            if got is None or got != want:
                bad.append(f"{rel}: sha256 {got}, want {want}")
        for fmt, (rel, want) in C.TILES.items():
            p = os.path.join(ROOT, rel)
            if not os.path.isfile(p) or sha256(p) != want:
                bad.append(f"{rel} is not kinds.json's {want[:12]}")
        if bad:
            return "; ".join(bad)
        # the harness (every file the session runs or reads, at its sha256) and the device-command preflight, before the first device
        # access (E190.md section 8: dmcmd_audit GO with every send site READ)
        for name, cmd, want in (("harness", [sys.executable, "-B", os.path.join(HERE, "check_e190.py"), "--box"], "HARNESS OK: "),
                                ("preflight", ["bash", os.path.join(HERE, "preflight_e190.sh")], "dmcmd_audit: GO")):
            try:
                r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
                txt = r.stdout + r.stderr
            except (OSError, subprocess.TimeoutExpired) as e:
                txt, r = f"{type(e).__name__}", None
            with open(os.path.join(self.out, f"{name}.txt"), "w") as f:
                f.write(txt)
            if r is None or r.returncode != 0 or not any(ln.startswith(want) for ln in txt.splitlines()):
                bad.append(f"the {name} did not read {want.strip()} (rc {None if r is None else r.returncode}; {name}.txt)")
        return "; ".join(bad)

    # ------------------------------------------------------------------ the whole session
    def run(self):
        a = self.a
        tag = " DRY" if self.dry else ""
        self.say(f"session start (T0 {a.t0} = {time.strftime('%H:%M:%S %Z', time.localtime(a.t0))}; arm {self.arm}, {self.A['card']}; "
                 f"its files in {os.path.basename(self.out)}){tag}")
        lockf = None
        result = {"t0": a.t0, "arm": self.arm, "dry": self.dry, "queue": self.queue}
        try:
            if not self.dry:
                why = self.box_check()
                if why:
                    self.say(f"the box or the build is not the registered one ({why}): no device opened")
                    return 16
                self.say("the box and the build: the host, build/e190rgm (the kernel at the registration's pin, the host as built today), "
                         "the reader at its pin, the tiles")
            lockp = os.path.join(self.out, "dry.lock") if self.dry else self.A["lock"]
            if not self.dry and not os.path.exists(lockp):
                self.say(f"no card lock {lockp} on this box (it is never created here): no device opened")
                return 16
            try:
                lockf = open(lockp, "a+")
            except OSError as e:
                self.say(f"the card's lock cannot be opened ({type(e).__name__}): no device opened")
                return 16
            try:
                fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.say("the card's lock is held: no device opened")
                return 16
            f = self.foreign()
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((f or "no holder that blocks; no device process that blocks") + "\n")
            if f:
                self.say(f"a holder or a device process ({f}): no device opened")
                return 16
            self.t_first = time.time()
            cfg0, why = self.config("start")
            self.device_opened = True
            if not cfg0 or not C.config_ok(self.arm, cfg0):
                self.say(f"config start: {why or json.dumps(cfg0)}: not {self.A['config']}: the gate, no launch")
                return 16
            self.say(f"config start: {json.dumps(cfg0)} (read, nothing set)")
            if not self.start_sampler():
                self.say("the sampler would not start: no launch")
                return 16
            self.sampler_t0 = self.samples[0][0] if self.samples else now_ms()
            ok, res = self.stop_path_test()
            self.say("stop-path test " + ("passed" if ok else "failed") + ": " + "; ".join(
                f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, its file {'touched' if v['test_file_touched'] else 'NOT touched'}, "
                f"start {'refused' if v['refused_a_start'] else 'NOT refused'}" for k, v in res.items()))
            if not ok:
                return 16
            ok, why = self.smoke()
            if not ok:
                self.say(f"smoke gate failed: {why}")
                return 16
            self.say("smoke gate passed: the runs start")
            seq = C.sequence()
            if a.sequence == "short":          # --dry only: one burst of each format and one sustained run of fp32
                seq = [s for s in seq if s[1] == "P1"] + [s for s in seq if s[1] == "S1"]
            elif a.sequence == "bursts":       # --dry only: the four bursts of each format (the end-to-end case)
                seq = [s for s in seq if s[2] == "burst"]
            elif a.sequence == "e2e":          # --dry only: P1 and one sustained run of each format
                seq = [s for s in seq if s[1] in ("P1", "S1", "S2", "S3")]
            for it in seq:
                if self.stops.stop:
                    self.queue.append({"run": f"{it[0]:02d}-{it[1]}-{it[2]}-{it[3]}", "ran": False, "why": "after a stop: nothing further starts"})
                    continue
                self.queue.append(self.one_run(*it))
                if not self.sampler_alive() and not self.may_start(60) and not self.ensure_sampler():
                    self.stops.stop = self.stops.stop or "the sampler would not restart"
            if self.stops.stop:
                self.say(f"STOP: {self.stops.stop}: nothing further started")
            return 0
        finally:
            dl = self.close_deadline()
            self.stop_sampler(dl)
            if self.device_opened and self.t_first:
                cfg1, why = self.config("end", max(12.0, min(30.0, dl - time.time())) if dl else 30)
                self.say("config end: " + (json.dumps(cfg1) if cfg1 else why))
            self.tel.close()
            tp = os.path.join(self.out, "telemetry.jsonl")
            if os.path.exists(tp):
                with open(tp, "rb") as fi, gzip.open(tp + ".gz", "wb") as fo:
                    fo.write(fi.read())
                os.remove(tp)
            result.update({"stop": self.stops.stop, "t_first_ms": int(self.t_first * 1000) if self.t_first else None,
                           "t_close_ms": now_ms(), "end_bound_ms": int(self.close_deadline() * 1000) if self.t_first else None,
                           "rest_die_c": self.rest_die, "card_min": round((time.time() - self.t_first) / 60, 2) if self.t_first else 0})
            with open(os.path.join(self.out, "queue.json"), "w") as fo:
                json.dump(result, fo, indent=1)
            self.say(f"session end (T0 {a.t0})")
            self.log_f.close()
            if lockf:
                lockf.close()
            write_manifest(self.out)


def write_manifest(out):
    rows = []
    for dp, dn, fn in os.walk(out):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            rel = os.path.relpath(p, out)
            if rel in ("MANIFEST.sha256", "dry.lock", "runner.rc", "runner.out"):
                continue
            rows.append(f"{sha256(p)}  {rel}")
    with open(os.path.join(out, "MANIFEST.sha256"), "w") as f:
        f.write("\n".join(rows) + "\n")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=["session"])
    ap.add_argument("--arm", choices=["A", "B"], required=True)
    ap.add_argument("--t0", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-epoch", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--sequence", choices=["plan", "short", "bursts", "e2e"], default="plan")
    ap.add_argument("--rest-s", type=float, default=C.REST_READ_S)
    ap.add_argument("--smoke-rest-s", type=float, default=C.SMOKE_REST_S)
    ap.add_argument("--tail-s", type=float, default=C.TAIL_S)
    ap.add_argument("--gate-wait-s", type=float, default=C.GATE_WAIT_S)
    ap.add_argument("--rule-s", type=float, default=C.CARD_RULE_S)
    ap.add_argument("--cap-s", type=float, default=C.CAP_S)
    a = ap.parse_args(argv)
    if not a.dry:
        changed = [n for n, v in (("--rest-s", a.rest_s != C.REST_READ_S), ("--smoke-rest-s", a.smoke_rest_s != C.SMOKE_REST_S),
                                  ("--tail-s", a.tail_s != C.TAIL_S), ("--gate-wait-s", a.gate_wait_s != C.GATE_WAIT_S),
                                  ("--rule-s", a.rule_s != C.CARD_RULE_S), ("--cap-s", a.cap_s != C.CAP_S),
                                  ("--sequence", a.sequence != "plan")) if v]
        if changed:
            print(f"refused: {', '.join(changed)} change the registered session and are read with --dry only")
            return 2
        if os.environ.get("V3_DRY"):
            print("refused: V3_DRY is set but --dry is not")
            return 2
    return Session(a).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
