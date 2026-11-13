#!/usr/bin/env python3
"""E189's runner (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the blind day's whole session on aifoundry3 card 0, in
energy.sh's form, with the live stops. Python's own modules only (the box's system python3). session_e189.sh starts it, detached.

    python3 -B tools/claims-v3/e189/run_e189.py session --t0 T0 --out build/e189/T<T0> --programs ledger,spp
        [--deadline-epoch E] [--rapl-allowed]
    python3 -B tools/claims-v3/e189/run_e189.py session --dry --double alt|base|inject --t0 T0 --out DIR [--sequence plan|short|e2e]
        [--idle-before S --idle-after S --anchor-s S --die-wait-s S --cap-pass-s S --cap-end-s S]   (the last six in --dry only)

What a session does (E189.md sections 9-11, plan-e189.json), from the box tree's root (~/aifoundry):
  1. takes card 0's lock (flock -n on /run/lock/etsoc-shire0.lock, held by this process to the end), reads et-who and the other users'
     device processes (a holder or a foreign device process: no device opened, the session ends at the gate);
  2. THE FIRST CARD COMMAND: `ettelem config` through E128's guard under `timeout 10` (TDP 0 W, threshold 65 C, minion 600 MHz, else
     the session ends at the gate before any launch); the cap counts from it;
  3. the sampler, `ettelem sample --every-ms 100` through the guard, ONE process for the session (restarted as lib.sh does if it dies),
     every line written to telemetry.jsonl and fed to THE STOP LINES (e189_common.Stops) as it arrives;
  4. THE STOP-PATH TEST: the three stop lines, each with a test threshold every live sample crosses (board 0 W, minshire[0] 0 C, a clock
     of -1 MHz), must trip on the live sampler within 5 s, and the runner must then refuse to start a host; else no device process starts;
  5. THE RAMPED SMOKE (the programs built today): ledger --selftest, copy 64 MiB random and zeros, copy 1 GiB random, SHA-256 2 KiB x 1
     with --expect over 2,048 participants, the sort of 1 shuffled and sorted, sparse parity's instance once; every output checked; any
     failure ends the session at the gate (E189.md section 12);
  6. idle anchor 1 (2 min), rounds 1-2, idle anchor 2, rounds 3-4, idle anchor 3 (plan-e189.json > order, never re-drawn); the counters
     arm is DROPPED (KIT.md section 5: its desk test was not run);
     each pass: the die gate (minshire[0] at or below 60 C, at most 10 minutes and never past the cap, else that pass is skipped), 8 s
     of idle, ONE host process under `timeout 10`, 10 s of idle; its files in passes/<config>/p<k>/ (E189.md section 8.1):
     telemetry.jsonl.gz (the session's samples over the pass), host-raw.json + host.json (the adapter) or sparse parity's host.json,
     host.err, run.json (energy.sh's marks), pass.json; the reducer is NOT run here (the collection runs it at the desk, unchanged);
  7. a stop (65 W, 70 C, a second sample off 600 MHz in a pass) ends the queue after the running process (never killed); the pass that
     process belongs to still runs its 10 s of idle after the host (no launch happens in it; E189.md 9's pass form, 12's "the passes done
     are scored"), so its long window is whole; no pass starts after 108 card-minutes from the first card command, nor too close to the
     window's last end; then the sampler stops (SIGTERM only), the closing `ettelem config`, "session end", the lock released,
     MANIFEST.sha256 last. THE END BOUND (E189.md 10: "the session ends by 110"): the die gate stops waiting at the cap, the sampler is
     not restarted once no pass can start, and the closing's waits on the sampler end CLOSE_CONFIG_S (15 s) before 110 card-minutes (at
     least 2 s each), the closing config read having those 15 s (KIT.md section 4 gives the arithmetic).
Every device command is a READ: the two hosts open the ops node only; ettelem config and sample through E128's guard (it refuses
--reset-ms and anything else before the device opens). No set, no reset, no statistics reset, no firmware-revisions query. The host's
package counter is read only with --rapl-allowed (his go), and only if our user can read it.
--dry swaps every device-opening process for fake_card_e189.py's doubles (or energy_stub.py's sampler with --double alt|base), takes a
lock file in the output directory, and marks every line DRY (the rest rule skips it). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import fcntl
import gzip
import hashlib
import json
import os
import pwd
import re
import resource
import signal
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e189_common as C  # noqa: E402

ROOT = C.REPO
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner\.Worker$")
RAPL_F = "/sys/class/powercap/intel-rapl:0/energy_uj"


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


class Session:
    def __init__(self, a):
        self.a = a
        self.dry = a.dry
        self.out = a.out
        os.makedirs(self.out, exist_ok=True)
        self.log_f = open(os.path.join(self.out, "session.log"), "a")
        self.stops = C.Stops()
        self.test_stops = None
        self.in_pass = None
        self.samples = []              # (t_ms, line) of the whole session
        self.last = None
        self.lock = threading.Lock()
        self.set_aside = {}            # pass key -> why
        self.sproc = None
        self.tel = open(os.path.join(self.out, "telemetry.jsonl"), "a")
        self.queue = []
        self.t_first = None
        self.device_opened = False
        self.programs = [p for p in a.programs.split(",") if p]
        self.env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
        self.env.pop("V3_DEVICE", None)
        self.env.pop("ET_DEVICES", None)
        if self.dry:
            self.env["E189_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            open(self.env["E189_FAKE_SCHED"], "a").close()

    # ------------------------------------------------------------------ the log, in the kits' form
    def say(self, words):
        w = ("DRY " + words) if self.dry and not words.startswith("session start") else words
        line = f"{stamp()} {w}"
        self.log_f.write(line + "\n")
        self.log_f.flush()
        print(line, flush=True)

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def cmd_config(self):
        if self.dry:
            return [sys.executable, "-B", os.path.join(HERE, "fake_card_e189.py"), "config"]
        return ["timeout", str(C.HOST_TIMEOUT_S), "bash", C.GUARD, "config"]

    def cmd_sampler(self, seconds):
        if self.dry and self.a.double in ("alt", "base"):
            return [sys.executable, "-B", os.path.join(ROOT, "workloads/sparseparity/tools/energy_stub.py"), "sample",
                    "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS), "--sched", self.env["E189_FAKE_SCHED"],
                    "--card", self.a.double]
        if self.dry:
            return [sys.executable, "-B", os.path.join(HERE, "fake_card_e189.py"), "sample", "--seconds", str(int(seconds)),
                    "--every-ms", str(C.EVERY_MS)]
        return ["bash", C.GUARD, "sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)]

    def cmd_etwho(self):
        if self.dry:
            return [sys.executable, "-B", os.path.join(HERE, "fake_card_e189.py"), "etwho"]
        return ["timeout", "20", "et-who"]

    def host_cmd(self, argv):
        if self.dry:
            return [sys.executable, "-B", os.path.join(HERE, "fake_card_e189.py"),
                    "host-ledger" if os.path.basename(argv[0]) == "ledger_host" else "host-spp"] + argv[1:]
        return ["timeout", str(C.HOST_TIMEOUT_S)] + argv

    # ------------------------------------------------------------------ holders
    def foreign(self):
        """et-who's holder lines of another login, and other users' device processes (energy.sh's foreign()); counts, never names."""
        try:
            w = subprocess.run(self.cmd_etwho(), cwd=ROOT, capture_output=True, text=True, timeout=30, env=self.env)
            lines = w.stdout.splitlines()
            rc = w.returncode
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"et-who unreadable ({type(e).__name__})"
        me = pwd.getpwuid(os.getuid()).pw_name      # our login, as et-who prints it (never written anywhere)
        held = [ln for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1
                and ln.split()[1] != me]
        if rc not in (0, 1) and not lines:
            return f"et-who rc {rc}"
        n = 0
        if not self.dry:
            ps = subprocess.run(["ps", "-eo", "uid=,pid=,comm="], capture_output=True, text=True).stdout.splitlines()
            uid = os.getuid()
            for ln in ps:
                f = ln.split(None, 2)
                if len(f) == 3 and int(f[0]) != uid and DEV_COMM.search(f[2].strip()):
                    n += 1
        if held or n:
            return f"{len(held)} holder line(s) of another login, {n} other users' device process(es)"
        return ""

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
                acts = self.stops.feed(s, self.in_pass)
                if self.test_stops is not None:
                    # the stop-path test reads its samples as a pass's, so its clock line (two samples off a test clock in a pass)
                    # trips on live samples as the real line would in a pass (the clock line counts in-pass samples only)
                    self.test_stops.feed(s, "the stop-path test")
                if "set-aside" in acts and self.in_pass and self.in_pass not in self.set_aside:
                    self.set_aside[self.in_pass] = f"a sample off {C.CLOCK_MHZ} MHz ({(s.get('mhz') or {}).get('minion')} MHz at t_ms {s.get('t_ms')})"
        self.tel.flush()

    def close_deadline(self):
        """The session's end bound: 110 card-minutes from the first card command (E189.md 10; --cap-end-s in --dry only)."""
        return self.t_first + self.a.cap_end_s if self.t_first else None

    def start_sampler(self):
        secs = C.CAP_S + 1200
        for attempt in range(1, 7):
            if attempt > 1 and self.t_first and self.may_start(60):
                self.say(f"the sampler: no attempt {attempt} ({self.may_start(60)}): no pass can start")
                break
            err = open(os.path.join(self.out, "sampler.err"), "a")
            self.sproc = subprocess.Popen(self.cmd_sampler(secs), cwd=ROOT, stdout=subprocess.PIPE, stderr=err,
                                          stdin=subprocess.DEVNULL, text=True, env=self.env)
            n0 = len(self.samples)
            th = threading.Thread(target=self._reader, args=(self.sproc,), daemon=True)
            th.start()
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
        """SIGTERM only (never kill -9 a tool): 30 s, then once more and 60 s; a sampler that will not stop is recorded. With a deadline
        (the session's end bound), each wait ends CLOSE_CONFIG_S before it, but lasts at least 2 s: the closing config read still fits
        before 110 card-minutes (fixed Fri 13 Nov 2026, verify-e189's nit: 30 + 60 s here could end the session at about 110.8)."""
        p = self.sproc
        if not p:
            return True
        waited = 0.0
        for n, wait_s in enumerate((30.0, 60.0)):
            if p.poll() is None:
                if deadline:
                    wait_s = min(wait_s, max(2.0, deadline - C.CLOSE_CONFIG_S - time.time()))
                p.send_signal(signal.SIGTERM)
                t = time.time()
                try:
                    p.wait(timeout=wait_s)
                except subprocess.TimeoutExpired:
                    waited += time.time() - t
                    if n == 0:
                        self.say(f"the sampler did not stop within {wait_s:.0f} s of SIGTERM: SIGTERM once more")
                    continue
                waited += time.time() - t
            break
        ok = p.poll() is not None
        if not ok:
            self.say(f"the sampler did not stop on SIGTERM in {waited:.0f} s: left running, recorded (no kill -9)")
        self.sproc = None
        return ok

    def ensure_sampler(self):
        if self.sampler_alive():
            return True
        why = self.may_start(60) if self.t_first else ""
        if why:
            self.say(f"the sampler is not running; not restarted: no pass can start ({why})")
            return False
        self.say("the sampler is not running: restarting it")
        return self.start_sampler()

    def latest(self):
        with self.lock:
            return dict(self.last) if self.last else None

    def nap(self, seconds):
        """Sleep, watching the stop lines; returns False (at once) if a stop tripped meanwhile. Before a host process: a stop starts
        nothing."""
        end = time.time() + seconds
        while time.time() < end:
            if self.stops.stop:
                return False
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    def idle(self, seconds):
        """The idle AFTER a host process: it runs to its end whatever the stop lines say (no launch happens in it, only the sampler
        reads), so a pass whose host ran keeps its whole after window (verify-e189's fault 2: nap() returned at once on a stop, cutting
        the pass's telemetry about 0.5 s after its host and its J over idle short by the SP average's tail). Returns False if a stop
        tripped by its end."""
        end = time.time() + seconds
        while time.time() < end:
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    # ------------------------------------------------------------------ the gates
    def may_start(self, seconds):
        """A pass (or an anchor) may start: no stop, inside the cap from the first card command, before the window's end."""
        if self.stops.stop or (self.test_stops is not None and self.test_stops.stop):
            return "a stop line has tripped"
        el = time.time() - self.t_first
        if el > self.a.cap_pass_s or el + (seconds if seconds > 60 else 0) > self.a.cap_pass_s:
            return f"the cap: {el / 60:.1f} card-minutes since the first card command (no pass after {self.a.cap_pass_s / 60:g})"
        if self.a.deadline_epoch and time.time() + seconds + 90 > self.a.deadline_epoch:
            return "the window's last end is too close"
        return ""

    def die_gate(self):
        """minshire[0] at or below 60 C on the latest sample, waiting at most --die-wait-s, and never past the cap, the window or a stop
        (no pass could start then: fixed Fri 13 Nov 2026, the 10-minute wait could otherwise run past 110 card-minutes); returns
        (ok, die, waited_s, why), why naming what ended the wait when it was not the die nor the 10 minutes."""
        t = time.time()
        while True:
            s = self.latest()
            die = C.die_of(s) if s else None
            if die is not None and die <= C.DIE_GATE_C:
                return True, die, time.time() - t, ""
            why = self.may_start(60)
            if why:
                return False, die, time.time() - t, why
            if time.time() - t >= self.a.die_wait_s:
                return False, die, time.time() - t, ""
            if not self.ensure_sampler():
                return False, die, time.time() - t, "the sampler is not running"
            time.sleep(1.0)

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

    @staticmethod
    def config_ok(j):
        return j.get("tdp_w") == 0 and j.get("temp_threshold_c") == 65 and j.get("minion_mhz") == 600

    def rapl(self):
        if not self.a.rapl_allowed:
            return "not read: his go did not allow it", None
        try:
            with open(RAPL_F) as f:
                return "readable", int(f.read().strip())
        except PermissionError:
            return "root-only (not read: no root read in this kit)", None
        except OSError:
            return "absent", None

    # ------------------------------------------------------------------ one host process
    def run_host(self, argv, out_dir, stdout_name):
        os.makedirs(out_dir, exist_ok=True)
        u0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = now_ms()
        with open(os.path.join(out_dir, stdout_name), "w") as so, open(os.path.join(out_dir, "host.err"), "w") as se:
            try:
                rc = subprocess.run(self.host_cmd(argv), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL,
                                    env=self.env, timeout=C.HOST_TIMEOUT_S + 20).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        t1 = now_ms()
        u1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = [round(u1.ru_utime - u0.ru_utime, 3), round(u1.ru_stime - u0.ru_stime, 3)]
        with open(os.path.join(out_dir, stdout_name)) as f:
            text = f.read()
        return rc, t0, t1, cpu, text

    # ------------------------------------------------------------------ the stop-path test
    def stop_path_test(self):
        res = {}
        for line, kw in (("board", {"board_w": 0.0}), ("die", {"die_c": 0.0}), ("clock", {"clock_mhz": -1})):
            self.test_stops = C.Stops(**kw)
            t = time.time()
            while time.time() - t < 5 and not self.test_stops.stop:
                time.sleep(0.1)
            tripped = bool(self.test_stops.stop)
            refused = bool(self.may_start(0))
            res[line] = {"tripped": tripped, "why": self.test_stops.stop, "refused_a_start": refused,
                         "s": round(time.time() - t, 2)}
            self.test_stops = None
        ok = all(v["tripped"] and v["refused_a_start"] for v in res.values()) and not self.stops.stop
        with open(os.path.join(self.out, "stop-path.json"), "w") as f:
            json.dump({"ok": ok, "lines": res, "real_thresholds": {"board_w": C.STOP_BOARD_W, "minshire0_c": C.STOP_DIE_C,
                                                                  "clock_mhz": C.CLOCK_MHZ}}, f, indent=1)
        return ok, res

    # ------------------------------------------------------------------ the smoke
    def smoke(self):
        for name, argv, kind in C.smoke_runs(self.programs):
            why = self.may_start(30)
            if why:
                return False, f"{name}: not started ({why})"
            ok, die, waited, gwhy = self.die_gate()
            if not ok:
                return False, f"{name}: the die gate ({die} C after {waited:.0f} s{'; ' + gwhy if gwhy else ''})"
            d = os.path.join(self.out, "smoke", name)
            rc, t0, t1, cpu, text = self.run_host(argv, d, "stdout.txt")
            self.device_opened = self.device_opened or kind != "selftest"
            j = C.last_json(text)
            if kind == "selftest":
                good = rc == 0 and "SELFTEST PASS" in text
            elif kind == "ledger":
                good = rc == 0 and j.get("status") == "PASS"
            else:
                good = rc == 0 and j.get("status") == "PASS" and (j.get("result") or {}).get("solved") is not False
            with open(os.path.join(d, "smoke.json"), "w") as f:
                json.dump({"name": name, "argv": argv, "rc": rc, "t0_ms": t0, "t1_ms": t1, "status": j.get("status"),
                           "good": good}, f, indent=1)
            self.say(f"smoke {name}: rc {rc}, {'ok' if good else 'FAILED'} ({(t1 - t0) / 1000:.1f} s)")
            if not good:
                return False, f"{name}: rc {rc}, status {j.get('status')}"
            if self.stops.stop:
                return False, f"a stop line tripped during {name}: {self.stops.stop}"
        return True, ""

    # ------------------------------------------------------------------ an idle anchor
    def anchor(self, n):
        why = self.may_start(self.a.anchor_s)
        if why:
            self.say(f"idle anchor {n}: not started ({why})")
            return {"anchor": n, "ran": False, "why": why}
        t0 = now_ms()
        self.say(f"idle anchor {n}: {self.a.anchor_s:g} s, nothing running but the sampler")
        ok = self.nap(self.a.anchor_s)
        return {"anchor": n, "ran": True, "t0_ms": t0, "t1_ms": now_ms(), "whole": ok}

    # ------------------------------------------------------------------ one pass
    def one_pass(self, cfg, k, idx):
        p = C.plan()
        K = p["configs"][cfg]["launches_K"]
        d = os.path.join(self.out, "passes", cfg, f"p{k}")
        key = f"{cfg}/p{k}"
        why = self.may_start(60)
        if why:
            self.say(f"pass {idx}: {cfg} p{k} not started ({why}): no data")
            return {"pass": key, "ran": False, "why": why}
        ok, die, waited, gwhy = self.die_gate()
        if not ok and gwhy:
            self.say(f"pass {idx}: {cfg} p{k} not started ({gwhy}; the die gate read {die} C after {waited:.0f} s): no data")
            return {"pass": key, "ran": False, "why": f"{gwhy} (in the die gate's wait: {die} C after {waited:.0f} s)"}
        if not ok:
            self.say(f"pass {idx}: {cfg} p{k} skipped by the die gate (minshire[0] {die} C after {waited:.0f} s): no data")
            return {"pass": key, "ran": False, "why": f"die gate: {die} C after {waited:.0f} s"}
        why = self.may_start(60)
        if why:
            self.say(f"pass {idx}: {cfg} p{k} not started ({why}): no data")
            return {"pass": key, "ran": False, "why": why}
        f = self.foreign()
        if f:
            self.stops.stop = self.stops.stop or f"a holder or a foreign device process: {f}"
            self.say(f"STOP before pass {idx}: {f}")
            return {"pass": key, "ran": False, "why": f}
        os.makedirs(d, exist_ok=True)
        t_start = now_ms()
        with self.lock:
            self.in_pass = key
        self.say(f"pass {idx}: {cfg} p{k} (K {K}; die {die} C{'; below the forecast band' if die is not None and die < C.DIE_LOW_C else ''})")
        clean = self.nap(self.a.idle_before)
        if not clean:
            with self.lock:
                self.in_pass = None
            self.say(f"pass {idx}: a stop tripped in its idle before: no host process started")
            return {"pass": key, "ran": False, "why": "stop: " + str(self.stops.stop)}
        rapl, r0 = self.rapl()
        argv = C.host_argv(cfg, p, d)
        rc, h0, h1, cpu, text = self.run_host(argv, d, "host-raw.json" if C.PROGRAM[cfg] == "ledger" else "host.json")
        self.device_opened = True
        _, r1 = self.rapl()
        self.idle(self.a.idle_after)          # whole, even after a stop: the host ran, so its pass keeps its after window (fault 2)
        t_end = now_ms()
        with self.lock:
            self.in_pass = None
            sl = [ln for (t, ln) in self.samples if t_start - 1000 <= t <= t_end + 500]
        with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as g:
            for ln in sl:
                g.write(ln + "\n")
        j = C.last_json(text)
        if C.PROGRAM[cfg] == "ledger":
            with open(os.path.join(d, "host-raw.json"), "w") as fo:      # the host's own line, unchanged
                fo.write((json.dumps(j) if j else "") + "\n")
            with open(os.path.join(d, "host.json"), "w") as fo:
                fo.write(json.dumps(C.adapt_ledger(j, K)) + "\n")
        flags = []
        if self.stops.stop:
            flags.append(f"a stop line tripped during this pass: {self.stops.stop}")
        if die is not None and die < C.DIE_LOW_C:
            flags.append(f"T0 below the forecast band ({die} C < {C.DIE_LOW_C} C)")
        run = {"preset": cfg, "card": "aifoundry3", "dry": self.dry, "lock": C.LOCK if not self.dry else "DRY",
               "build": os.path.dirname(os.path.dirname(argv[0])), "host_args": " ".join(argv[1:]), "reps_planned": K,
               "idle_before_s": self.a.idle_before, "idle_after_s": self.a.idle_after, "every_ms": C.EVERY_MS,
               "sampler": " ".join(self.cmd_sampler(C.CAP_S + 1200)), "sampler_t0_ms": self.sampler_t0, "host_t0_ms": h0,
               "host_t1_ms": h1, "end_ms": t_end, "host_rc": rc, "foreign": None, "rapl": rapl, "rapl_uj": [r0, r1],
               "host_cpu_ext_s": cpu, "stub_card": self.a.double if self.dry else None}
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(run, fo, indent=1)
        with self.lock:
            sa = self.set_aside.get(key)
        with open(os.path.join(d, "pass.json"), "w") as fo:
            json.dump({"config": cfg, "pass": k, "order_index": idx, "launches_requested": K, "set_aside": sa,
                       "die_start_c": die, "die_gate_wait_s": round(waited, 1), "flags": flags, "t_start_ms": t_start,
                       "t_end_ms": t_end, "host_rc": rc, "host_status": j.get("status"), "dry": self.dry}, fo, indent=1)
        self.say(f"pass {idx}: {cfg} p{k} done: host rc {rc}, status {j.get('status')}"
                 f"{', SET ASIDE: ' + sa if sa else ''}{', ' + '; '.join(flags) if flags else ''}")
        return {"pass": key, "ran": True, "rc": rc, "status": j.get("status"), "set_aside": sa}

    # ------------------------------------------------------------------ the whole session
    def run(self):
        a = self.a
        tag = " DRY" if self.dry else ""
        self.say(f"session start (T0 {a.t0} = {time.strftime('%H:%M:%S %Z', time.localtime(a.t0))}; plan FULL; programs "
                 f"{'+'.join(self.programs) or 'none'}; its files in {a.out}){tag}")
        lockf = None
        result = {"t0": a.t0, "dry": self.dry, "programs": self.programs, "queue": self.queue}
        try:
            if not self.programs:
                self.say("no program was built today: no device opened")
                return 16
            lockp = os.path.join(self.out, "dry.lock") if self.dry else C.LOCK
            try:
                lockf = open(lockp, "a+")
            except OSError as e:
                self.say(f"card 0's lock cannot be opened ({type(e).__name__}): no device opened")
                return 16
            try:
                fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.say("card 0's lock is held: no device opened")
                return 16
            f = self.foreign()
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((f or "no holder of another login; no other user's device process") + "\n")
            if f:
                self.say(f"a holder or a foreign device process ({f}): no device opened")
                return 16
            self.t_first = time.time()
            cfg0, why = self.config("start")
            self.device_opened = True
            if not cfg0 or not self.config_ok(cfg0):
                self.say(f"config start: {why or json.dumps(cfg0)}: not TDP 0 W / 65 C / 600 MHz: the gate, no launch")
                return 16
            self.say("config start: TDP 0 W, threshold 65 C, minion 600 MHz (read, nothing set)")
            if not self.start_sampler():
                self.say("the sampler would not start: no launch")
                return 16
            self.sampler_t0 = self.samples[0][0] if self.samples else now_ms()
            ok, res = self.stop_path_test()
            self.say(f"stop-path test {'passed' if ok else 'failed'}: " + "; ".join(
                f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, start {'refused' if v['refused_a_start'] else 'NOT refused'}"
                for k, v in res.items()))
            if not ok:
                return 16
            ok, why = self.smoke()
            if not ok:
                self.say(f"smoke gate failed: {why}")
                return 16
            self.say("smoke gate passed: queue starts (plan FULL)")
            if a.sequence == "plan":
                seq = C.sequence()
            elif a.sequence == "short":           # --dry only: one pass of each configuration
                seq = [("anchor", 1)] + [("pass", c, 1, i + 1) for i, c in enumerate(C.ORDER)] + [("anchor", 3)]
            else:                                 # --dry only (e2e): two passes of three configurations, for the reducer and scorer
                seq = [("anchor", 1)] + [("pass", c, k, 0) for k in (1, 2) for c in ("copy-zeros", "sha256", "sparse-parity")]
            anchors = []
            for it in seq:
                if self.stops.stop:
                    break
                if it[0] == "anchor":
                    anchors.append(self.anchor(it[1]))
                    continue
                _, cfg, k, idx = it
                if C.PROGRAM[cfg] not in self.programs:
                    self.queue.append({"pass": f"{cfg}/p{k}", "ran": False, "why": "SKIPPED: its program was not built today"})
                    continue
                self.queue.append(self.one_pass(cfg, k, idx))
                if not self.sampler_alive() and not self.may_start(60) and not self.ensure_sampler():
                    # restarted only while a pass could still start (past the cap, the window or a stop it is not: the end bound)
                    self.stops.stop = self.stops.stop or "the sampler would not restart"
            with open(os.path.join(self.out, "anchors.json"), "w") as fo:
                json.dump(anchors, fo, indent=1)
            self.say("the counters arm: DROPPED by the kit (KIT.md section 5): not run")
            if self.stops.stop:
                self.say(f"STOP: {self.stops.stop}: the queue ended after the running process")
            return 0
        finally:
            dl = self.close_deadline()
            self.stop_sampler(dl)
            if self.device_opened:
                # the closing read: its own `timeout 10` inside, this process's bound at most what is left to the end bound (at least 12 s)
                cfg1, why = self.config("end", max(12.0, min(30.0, dl - time.time())) if dl else 30)
                self.say("config end: " + (f"TDP {cfg1.get('tdp_w')} W, threshold {cfg1.get('temp_threshold_c')} C, minion "
                                           f"{cfg1.get('minion_mhz')} MHz" if cfg1 else why))
            self.tel.close()
            if os.path.exists(os.path.join(self.out, "telemetry.jsonl")):
                with open(os.path.join(self.out, "telemetry.jsonl"), "rb") as fi, \
                        gzip.open(os.path.join(self.out, "telemetry.jsonl.gz"), "wb") as fo:
                    fo.write(fi.read())
                os.remove(os.path.join(self.out, "telemetry.jsonl"))
            result.update({"stop": self.stops.stop, "off_clock": self.stops.events, "set_aside": self.set_aside,
                           "t_first_ms": int(self.t_first * 1000) if self.t_first else None, "t_close_ms": now_ms(),
                           "end_bound_ms": int(self.close_deadline() * 1000) if self.t_first else None})
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
            if rel in ("MANIFEST.sha256", "dry.lock"):
                continue
            rows.append(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {rel}")
    with open(os.path.join(out, "MANIFEST.sha256"), "w") as f:
        f.write("\n".join(rows) + "\n")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=["session"])
    ap.add_argument("--t0", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--programs", default="ledger,spp")
    ap.add_argument("--deadline-epoch", type=int, default=0)
    ap.add_argument("--rapl-allowed", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--double", choices=["alt", "base", "inject"], default="inject")
    ap.add_argument("--sequence", choices=["plan", "short", "e2e"], default="plan")
    ap.add_argument("--idle-before", type=float, default=C.IDLE_BEFORE_S)
    ap.add_argument("--idle-after", type=float, default=C.IDLE_AFTER_S)
    ap.add_argument("--anchor-s", type=float, default=C.ANCHOR_S)
    ap.add_argument("--die-wait-s", type=float, default=C.DIE_GATE_WAIT_S)
    ap.add_argument("--cap-pass-s", type=float, default=C.CAP_PASS_START_S)
    ap.add_argument("--cap-end-s", type=float, default=C.CAP_S)
    a = ap.parse_args(argv)
    if not a.dry:
        changed = [n for n, v in (("--idle-before", a.idle_before != C.IDLE_BEFORE_S), ("--idle-after", a.idle_after != C.IDLE_AFTER_S),
                                  ("--anchor-s", a.anchor_s != C.ANCHOR_S), ("--die-wait-s", a.die_wait_s != C.DIE_GATE_WAIT_S),
                                  ("--cap-pass-s", a.cap_pass_s != C.CAP_PASS_START_S), ("--cap-end-s", a.cap_end_s != C.CAP_S),
                                  ("--sequence", a.sequence != "plan")) if v]
        if changed:
            print(f"refused: {', '.join(changed)} change the registered session and are read with --dry only")
            return 2
        if os.environ.get("V3_DRY"):
            print("refused: V3_DRY is set but --dry is not")
            return 2
    s = Session(a)
    s.sampler_t0 = None
    return s.run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
