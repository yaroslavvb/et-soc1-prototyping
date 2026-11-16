#!/usr/bin/env python3
"""E202's runner (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): one pass over MNIST in int8, E202's whole session on
aifoundry3 card 0, in E189's runner form (energy.sh's: one sampler, live stops, a burst = rest, ONE host process, rest). Python's own
modules only (the box's system python3). session_e202.sh starts it, detached.

    python3 -B tools/claims-v3/e202/run_e202.py session --t0 T0 --out build/e202/T<T0> --deadline-epoch E
    python3 -B tools/claims-v3/e202/run_e202.py session --dry --double alt|base|inject --t0 T0 --out DIR [--sequence plan|short|e2e]
        [--idle-before S --idle-after S --anchor-s S --die-wait-s S --cap-burst-s S --cap-end-s S]   (the last six with --dry only)

What a session does (E202.md sections 8-10, plan-e202.json), from the box tree's root (~/aifoundry):
  0. REFUSALS BEFORE ANYTHING ("refused, no device opened: ...", exit 2): the host's name aifoundry3; exactly /dev/et0_mgmt and
     /dev/et0_ops; no desk-test variable; the synced files at harness-e202.json's sha256 (HARNESS OK); the preflight GO (dmcmd_audit_v2,
     every send site a READ); today's build record build/e202mnist/BUILD-E202.json with the kernel's .text at E202.md's pin and the host
     and ELF at the record's sha256; every input the host reads at its pin (build/e202files, PINS-SHA256SUMS: 18 files);
  1. card 0's lock (flock -n, held by this process to the end); et-who's holder lines of another login and other users' device
     processes (any: "refused, no device opened");
  2. THE FIRST CARD COMMAND, stamped as it starts: `ettelem config` through E128's guard under `timeout 10` (TDP 0 W, threshold 65 C,
     minion 600 MHz as found, else GATE-STOP before any launch); THE CAP COUNTS FROM IT (no burst after 33 card-minutes; the session's
     last card command by 35);
  3. ONE sampler for the session, `ettelem sample --every-ms 100` through the guard, every line written to telemetry.jsonl and fed to
     THE STOP LINES as it arrives, with its age; a watchdog stops the session when no line has come for 1 s (E202.md 9);
  4. THE STOP-PATH TEST: each of the four lines with a test threshold every live sample crosses (board 0 W, minshire[0] 0 C, a clock
     of -1 MHz, a line older than -1 s) must trip on the live sampler within 5 s and refuse a start; else GATE-STOP;
  5. idle anchor 1 (2 minutes);
  6. THE SMOKE (E202.md 8.2): T-scp, Z-scp, T-dram, Z-dram (R = 1, --debug-logits) and ACC (T-scp on the test split, --true-labels),
     each after the die gate and et-who, under `timeout 10`, its result read from its own --out file (smoke/<arm>/host-raw.json), the
     kernel's own label lines kept (--labels-out, 240 KB); THE GATE (E202-R0): the scp pair is scored when T-scp and Z-scp read core
     PASS, else the dram pair when T-dram and Z-dram do, else GATE-STOP (no burst: no data); THE R RULE per arm from its own smoke;
  7. THE BURSTS (E202.md 8.4-8.5): the scored pair T Z Z T T Z Z T, then (scp scored) the dram pair T Z Z T, REPORTED; each burst the
     die gate (60 C, at most 10 minutes, never past the cap), et-who, 8 s at rest, ONE host process (one launch of R passes, `timeout
     10`, never -k), 10 s at rest whatever a stop says; its files in bursts/<config>/b<k>/ (E202.md 7.1: host-raw.json = the host's own
     --out file, host.json = the adapter's, burst.json = the runner's marks, run.json, telemetry.jsonl.gz, stdout.txt, host.err);
  8. a stop (65 W, 70 C, a second sample off 600 MHz, a line older than 1 s, a holder or an unreadable et-who, K1, the operator's STOP
     file or SIGTERM) ends the queue after the running process
     (never killed); a failed burst (any host check) ends its arm; idle anchor 2 if it ends inside the cap; then THE CLOSING: the sampler
     stopped (SIGTERM only), et-who read, and the closing `ettelem config` ONLY while our sampler has stopped and et-who reads the card
     free of every other login (verify-e195's lesson), "session end", the lock released, MANIFEST.sha256 last. The closing's waits end
     CLOSE_S before 35 minutes.
Fixed before the land (fix-e202, verify-e202's findings): et-who is read only when it exits 0 with a holder line or its no-holder
sentence, anything else is a holder (1); a crash of the runner is named in its log ("CRASH: <type>: <message>", before the closing)
and in queue.json, and the runner exits non-zero (2); K1 also on a host that died (rc 125 or more) or left no --out record after its
device opened (5); the R rule's R is capped at the host's own launch timeout less 0.5 s, the time left read from the arm's own smoke
(7); the closing config read is not sent while our own sampler has not stopped (8).
Every device command is a READ: the host opens the ops node only; ettelem config and sample through E128's guard. No set, no reset, no
statistics reset. --dry swaps every device-opening process for fake_card_e202.py's doubles (or energy_stub.py's sampler with --double
alt|base), takes a lock file in its own directory, and marks every line DRY (the rest rule skips it). Exit 0 the queue ran (a stop or
not), 2 refused (no device opened), 3 GATE-STOP (the card opened, no burst ran), 1 a crash (named in the log; the closing still ran).
SPDX-License-Identifier: Apache-2.0
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
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e202_common as C  # noqa: E402

ROOT = C.REPO
DEV_COMM = re.compile(C.DEV_COMM)
OBJCOPY = "/opt/et/bin/riscv64-unknown-elf-objcopy"


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pacific_day(epoch):
    return subprocess.run(["date", "-d", "@%d" % int(epoch), "+%F"], capture_output=True, text=True,
                          env=dict(os.environ, TZ="America/Los_Angeles")).stdout.strip()


class Session:
    def __init__(self, a):
        self.a = a
        self.dry = a.dry
        self.out = a.out
        os.makedirs(self.out, exist_ok=True)
        self.log_f = open(os.path.join(self.out, "session.log"), "a")
        self.stops = C.Stops()
        self.test_stops = None
        self.in_burst = None
        self.samples = []              # (t_ms, line) of the whole session
        self.last = None
        self.last_arrival = None
        self.sampling = False
        self.lock = threading.Lock()
        self.set_aside = {}
        self.sproc = None
        self.tel = open(os.path.join(self.out, "telemetry.jsonl"), "a")
        self.smoke_res = {}
        self.bursts = []
        self.t_first = None
        self.device_opened = False
        self.sampler_t0 = None
        self.closing = "not reached"
        self.env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
        self.env.pop("V3_DEVICE", None)
        self.env.pop("ET_DEVICES", None)
        if self.dry:
            self.env["E202_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            open(self.env["E202_FAKE_SCHED"], "a").close()

    # ------------------------------------------------------------------ the log, in the kits' form
    def say(self, words):
        w = ("DRY " + words) if self.dry and not words.startswith("session start") else words
        line = f"{stamp()} {w}"
        self.log_f.write(line + "\n")
        self.log_f.flush()
        print(line, flush=True)

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def fake(self, *words):
        """A double's command line, from the tree's root (the runner's cwd), relative: no desk or box path enters a record."""
        return ["python3", "-B", os.path.relpath(os.path.join(HERE, "fake_card_e202.py"), ROOT)] + list(words)

    def cmd_config(self):
        if self.dry:
            return self.fake("config")
        return ["timeout", str(C.HOST_TIMEOUT_S), "bash", C.GUARD, "config"]

    def cmd_sampler(self, seconds):
        if self.dry and self.a.double in ("alt", "base"):
            return ["python3", "-B", "workloads/sparseparity/tools/energy_stub.py", "sample",
                    "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS), "--sched", self.env["E202_FAKE_SCHED"],
                    "--card", self.a.double]
        if self.dry:
            return self.fake("sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS))
        return ["bash", C.GUARD, "sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)]

    def cmd_etwho(self):
        if self.dry:
            return self.fake("etwho")
        return ["timeout", "20", "et-who"]

    def host_cmd(self, argv):
        if self.dry:
            return self.fake("host", *argv[1:])
        return ["timeout", str(C.HOST_TIMEOUT_S)] + argv

    # ------------------------------------------------------------------ refusals before anything (real runs)
    def refusals(self):
        """Step 0: the box, the pins, the build, the files and the preflight, before the lock and before any card command."""
        if self.a.refused:
            return self.a.refused
        if not self.dry:
            hn = socket.gethostname().split(".")[0]
            if hn != C.BOX:
                return f"the host's name is {hn!r}, not {C.BOX}"
            nodes = sorted(os.path.join("/dev", n) for n in os.listdir("/dev") if n.startswith("et"))
            if nodes != sorted(C.NODES):
                return f"the card nodes are {nodes}, not exactly {list(C.NODES)} (one card, card 0)"
        r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "check_e202.py"), "--box"], cwd=ROOT, capture_output=True,
                           text=True, timeout=120)
        if not r.stdout.startswith("HARNESS OK"):
            return "the synced files differ from harness-e202.json: " + (r.stdout.strip() or r.stderr.strip())[:200]
        r = subprocess.run(["bash", os.path.join(HERE, "preflight_e202.sh")], cwd=ROOT, capture_output=True, text=True,
                           timeout=180)
        verdict = [ln for ln in (r.stderr + "\n" + r.stdout).splitlines() if ln.startswith("dmcmd_audit: ")]
        if r.returncode != 0 or not verdict or not verdict[0].startswith("dmcmd_audit: GO"):
            return "the preflight is not GO (dmcmd_audit_v2): " + (verdict[0][:200] if verdict else f"rc {r.returncode}, no verdict line")
        if self.dry:
            return ""
        rec_p = os.path.join(ROOT, C.BUILD, "BUILD-E202.json")
        try:
            rec = json.load(open(rec_p))
        except (OSError, ValueError):
            return "no build record build/e202mnist/BUILD-E202.json (step 6)"
        if pacific_day(os.path.getmtime(rec_p)) != pacific_day(time.time()) or not rec.get("built"):
            return "the build record was not written today (Pacific) by a build that passed (step 6)"
        for what, p, key in (("host", C.HOST, "host_sha256"), ("kernel ELF", C.ELF, "elf_sha256")):
            if not os.path.exists(os.path.join(ROOT, p)):
                return f"no {what} at {p}"
            if sha(os.path.join(ROOT, p)) != rec.get(key):
                return f"the {what} differs from today's build record"
        oc = OBJCOPY if os.path.exists(OBJCOPY) else "objcopy"
        t = subprocess.run([oc, "-O", "binary", "-j", ".text", os.path.join(ROOT, C.ELF), "/dev/stdout"], capture_output=True,
                           timeout=60)
        th = hashlib.sha256(t.stdout).hexdigest() if t.returncode == 0 and t.stdout else None
        if th != C.TEXT_PIN or rec.get("text_sha256") != C.TEXT_PIN:
            return f"the kernel's .text is {th}, not E202.md's {C.TEXT_PIN[:16]}..."
        pins = os.path.join(ROOT, C.PINS)
        try:
            want = [ln.split() for ln in open(pins) if ln.strip()]
        except OSError:
            return "no pins file build/e202files/files/PINS-SHA256SUMS (step 6's files)"
        if sha(pins) != sha(os.path.join(ROOT, "workloads/mnistmlp/model/PINS-SHA256SUMS")):
            return "the box's pins file is not the program's PINS-SHA256SUMS"
        for h, n in want:
            d = C.MNIST if "idx" in n else C.WDIR
            p = os.path.join(ROOT, d, n)
            if not os.path.exists(p) or sha(p) != h:
                return f"the input {n} is not at its pin in {d}"
        return ""

    # ------------------------------------------------------------------ holders
    def foreign(self, bound_s=30.0):
        """et-who's holder lines of another login, and other users' device processes (counts, never names); '' when free. An et-who
        that cannot be read (fix-e202, verify-e202's finding 1: rc other than 0, or neither a holder line nor its no-holder sentence)
        is a holder: a refusal before the first card command, a stop before a start, the closing config read not sent."""
        try:
            w = subprocess.run(self.cmd_etwho(), cwd=ROOT, capture_output=True, text=True, timeout=bound_s, env=self.env)
            text, rc = w.stdout, w.returncode
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"et-who unreadable ({type(e).__name__})"
        uw = C.etwho_unreadable(rc, text)
        if uw:
            return uw
        me = pwd.getpwuid(os.getuid()).pw_name      # our login, as et-who prints it (never written anywhere)
        held = C.etwho_holders(text, me)
        n = 0
        if not self.dry:
            ps = subprocess.run(["ps", "-eo", "uid=,pid=,comm="], capture_output=True, text=True).stdout.splitlines()
            uid = os.getuid()
            for ln in ps:
                f = ln.split(None, 2)
                if len(f) == 3 and f[0].isdigit() and int(f[0]) != uid and DEV_COMM.search(f[2].strip()):
                    n += 1
        if held or n:
            return f"{held} holder line(s) of another login, {n} other users' device process(es)"
        return ""

    # ------------------------------------------------------------------ the sampler and the live stops
    def _reader(self, proc):
        for raw in proc.stdout:
            arrival = time.time()
            s = C.sample_line(raw)
            if s is None:
                continue
            self.tel.write(raw if raw.endswith("\n") else raw + "\n")
            with self.lock:
                self.samples.append((s.get("t_ms", 0), raw.rstrip("\n")))
                self.last = s
                self.last_arrival = arrival
                age = arrival - s["t_ms"] / 1000.0
                acts = self.stops.feed(s, self.in_burst, age)
                if self.test_stops is not None:
                    self.test_stops.feed(s, "the stop-path test", age)
                if "set-aside" in acts and self.in_burst and self.in_burst not in self.set_aside:
                    self.set_aside[self.in_burst] = f"a sample off {C.CLOCK_MHZ} MHz ({(s.get('mhz') or {}).get('minion')} MHz at t_ms {s.get('t_ms')})"
        self.tel.flush()

    def _watchdog(self):
        """THE STALE LINE's watchdog: while the session samples, no line for more than 1 s stops it (E202.md 9)."""
        while True:
            time.sleep(0.1)
            with self.lock:
                if not self.sampling:
                    if self.sproc is None and self.last_arrival is not None:
                        return
                    continue
                gap = time.time() - (self.last_arrival or time.time())
                if self.stops.stale(gap):
                    pass
                if self.test_stops is not None:
                    self.test_stops.stale(gap)

    def close_deadline(self):
        """The session's end bound: 35 card-minutes from the first card command (E202.md 8; --cap-end-s with --dry only)."""
        return self.t_first + self.a.cap_end_s if self.t_first else None

    def start_sampler(self):
        secs = C.CAP_S + 1200
        for attempt in range(1, 7):                     # lib.sh's six attempts, before the queue only
            err = open(os.path.join(self.out, "sampler.err"), "a")
            self.sproc = subprocess.Popen(self.cmd_sampler(secs), cwd=ROOT, stdout=subprocess.PIPE, stderr=err,
                                          stdin=subprocess.DEVNULL, text=True, env=self.env)
            n0 = len(self.samples)
            th = threading.Thread(target=self._reader, args=(self.sproc,), daemon=True)
            th.start()
            t = time.time()
            while time.time() - t < 10:
                if len(self.samples) > n0 + 2:
                    with self.lock:
                        self.sampling = True
                    threading.Thread(target=self._watchdog, daemon=True).start()
                    self.say(f"sampler started (attempt {attempt}, pid {self.sproc.pid}, every {C.EVERY_MS} ms)")
                    return True
                if self.sproc.poll() is not None:
                    break
                time.sleep(0.25)
            self.stop_sampler(self.close_deadline())
            time.sleep(2)
        return False

    def stop_sampler(self, deadline=None):
        """SIGTERM only (never kill -9 a tool): 30 s, then once more and 60 s; each wait ends CLOSE_S before the end bound (at least
        2 s), so the closing's et-who and config reads fit before 35 card-minutes. A sampler that will not stop is recorded."""
        p = self.sproc
        with self.lock:
            self.sampling = False
        if not p:
            return True
        waited = 0.0
        for n, wait_s in enumerate((30.0, 60.0)):
            if p.poll() is None:
                if deadline:
                    wait_s = min(wait_s, max(2.0, deadline - C.CLOSE_S - time.time()))
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

    def latest(self):
        with self.lock:
            return dict(self.last) if self.last else None

    def stopped(self):
        """A stop line has tripped, or the operator stopped the session: the STOP file in its directory (`touch
        build/e202/T<T0>/STOP` on the box) or SIGTERM / SIGINT to the runner. Either is a registered stop: the running process finishes
        (never killed), nothing further starts, the closing follows."""
        if not self.stops.stop and os.path.exists(os.path.join(self.out, "STOP")):
            self.stops.stop = "the operator's stop (the STOP file in the session's directory)"
        return self.stops.stop

    def on_signal(self, signum, _frame):
        if not self.stops.stop:
            self.stops.stop = f"the operator's stop (signal {signum} to the runner)"

    def nap(self, seconds):
        """Sleep, watching the stop lines; False at once when a stop trips (before a host process: a stop starts nothing)."""
        end = time.time() + seconds
        while time.time() < end:
            if self.stopped():
                return False
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stopped()

    def idle(self, seconds):
        """The rest AFTER a host process runs to its end whatever the stop lines say (E189 fault 2: no launch happens in it, only the
        sampler reads, so a burst whose host ran keeps its whole after window). False if a stop tripped by its end."""
        end = time.time() + seconds
        while time.time() < end:
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stopped()

    # ------------------------------------------------------------------ the gates
    def burst_worst(self):
        """A burst's longest possible span from its start check: et-who's bound (30 s), the rest before, the host process's bound
        (`timeout 10` inside a 30 s bound), the rest after."""
        return 30.0 + self.a.idle_before + C.HOST_TIMEOUT_S + 20.0 + self.a.idle_after

    def may_start(self, kind, seconds=0.0):
        """A burst, a smoke process or an anchor may start: no stop; inside the cap (no start after 33 card-minutes from the first
        card command); its longest span ending before the closing's share of the end bound (35 minutes less CLOSE_S: the session's
        last card command by 35, E202.md 8); an anchor's whole length inside the cap; 90 s to spare before the window's last end."""
        if self.stopped() or (self.test_stops is not None and self.test_stops.stop):
            return "a stop line has tripped"
        if self.t_first is None:
            return ""
        el = time.time() - self.t_first
        if el > self.a.cap_burst_s:
            return f"the cap: {el / 60:.1f} card-minutes since the first card command (no start after {self.a.cap_burst_s / 60:g})"
        if kind == "anchor" and el + seconds > self.a.cap_burst_s:
            return f"the cap: the anchor would end {(el + seconds) / 60:.1f} card-minutes after the first card command"
        span = self.burst_worst() if kind in ("burst", "smoke") else seconds
        if el + span > self.a.cap_end_s - C.CLOSE_S:
            return f"the end bound: {(el + span) / 60:.1f} card-minutes at its longest, past {(self.a.cap_end_s - C.CLOSE_S) / 60:.2f}"
        if self.a.deadline_epoch and time.time() + span + 90 > self.a.deadline_epoch:
            return "the window's last end is too close"
        return ""

    def die_gate(self):
        """minshire[0] at or below 60 C on the latest sample, waiting at most --die-wait-s, never past the cap, the window or a stop;
        (ok, die, waited_s, why), why naming what ended the wait when it was not the die nor the 10 minutes."""
        t = time.time()
        while True:
            s = self.latest()
            die = C.die_of(s) if s else None
            if die is not None and die <= C.DIE_GATE_C:
                return True, die, time.time() - t, ""
            why = self.may_start("burst")
            if why:
                return False, die, time.time() - t, why
            if time.time() - t >= self.a.die_wait_s:
                return False, die, time.time() - t, ""
            time.sleep(1.0)

    # ------------------------------------------------------------------ reads
    def config(self, name, bound_s=30):
        try:
            r = subprocess.run(self.cmd_config(), cwd=ROOT, capture_output=True, text=True, timeout=bound_s, env=self.env)
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, f"config read failed ({type(e).__name__})"
        j = C.config_line(r.stdout)
        with open(os.path.join(self.out, f"config-{name}.json"), "w") as f:
            f.write(json.dumps(j) + "\n")
        if r.returncode != 0 or not j:
            return None, f"config read rc {r.returncode}, no JSON line"
        return j, ""

    # ------------------------------------------------------------------ one host process
    def run_host(self, argv, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        u0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = now_ms()
        with open(os.path.join(out_dir, "stdout.txt"), "w") as so, open(os.path.join(out_dir, "host.err"), "w") as se:
            try:
                rc = subprocess.run(self.host_cmd(argv), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL,
                                    env=self.env, timeout=C.HOST_TIMEOUT_S + 20).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        t1 = now_ms()
        u1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = [round(u1.ru_utime - u0.ru_utime, 3), round(u1.ru_stime - u0.ru_stime, 3)]
        try:
            err = open(os.path.join(out_dir, "host.err"), errors="replace").read()
        except OSError:
            err = ""
        raw, why = C.read_result(os.path.join(out_dir, "host-raw.json"), device="card")
        self.device_opened = True
        return rc, t0, t1, cpu, raw, why, err

    def off_clock_in(self, t0, t1):
        with self.lock:
            return [e for e in self.stops.events if e.get("t_ms") is not None and t0 - 1000 <= e["t_ms"] <= t1 + 500]

    # ------------------------------------------------------------------ the stop-path test
    def stop_path_test(self):
        res = {}
        for line, kw in (("board", {"board_w": 0.0}), ("die", {"die_c": 0.0}), ("clock", {"clock_mhz": -1}),
                         ("stale", {"stale_s": -1.0})):
            with self.lock:
                self.test_stops = C.Stops(**kw)
            t = time.time()
            while time.time() - t < 5 and not self.test_stops.stop:
                time.sleep(0.1)
            tripped = bool(self.test_stops.stop)
            refused = bool(self.may_start("burst"))
            res[line] = {"tripped": tripped, "why": self.test_stops.stop, "refused_a_start": refused,
                         "s": round(time.time() - t, 2)}
            with self.lock:
                self.test_stops = None
        ok = all(v["tripped"] and v["refused_a_start"] for v in res.values()) and not self.stopped()
        with open(os.path.join(self.out, "stop-path.json"), "w") as f:
            json.dump({"ok": ok, "lines": res, "real_thresholds": {"board_w": C.STOP_BOARD_W, "minshire0_c": C.STOP_DIE_C,
                                                                  "clock_mhz": C.CLOCK_MHZ, "stale_s": C.STALE_S}}, f, indent=1)
        return ok, res

    # ------------------------------------------------------------------ an idle anchor
    def anchor(self, n):
        why = self.may_start("anchor", self.a.anchor_s)
        if why:
            self.say(f"idle anchor {n}: not started ({why})")
            return {"anchor": n, "ran": False, "why": why}
        t0 = now_ms()
        self.say(f"idle anchor {n}: {self.a.anchor_s:g} s, nothing running but the sampler")
        ok = self.nap(self.a.anchor_s)
        return {"anchor": n, "ran": True, "t0_ms": t0, "t1_ms": now_ms(), "whole": ok}

    # ------------------------------------------------------------------ the smoke
    def smoke(self):
        """The five R = 1 processes in the registered order; each its own arm (a failure ends that arm only). Returns
        (scored stage or None, why)."""
        pm = C.plan_module()
        for arm, w, st, sp, dbg, acc in C.SMOKE:
            why = self.may_start("smoke")
            if why:
                self.smoke_res[arm] = {"arm": arm, "ran": False, "why": why}
                self.say(f"smoke {arm}: not started ({why})")
                return None, f"{arm}: not started ({why})"
            ok, die, waited, gwhy = self.die_gate()
            if not ok:
                self.smoke_res[arm] = {"arm": arm, "ran": False, "why": f"the die gate ({die} C after {waited:.0f} s{'; ' + gwhy if gwhy else ''})"}
                self.say(f"smoke {arm}: not started: {self.smoke_res[arm]['why']}")
                return None, f"{arm}: {self.smoke_res[arm]['why']}"
            f = self.foreign()
            if f:
                self.stops.stop = self.stops.stop or f"a holder or a foreign device process: {f}"
                self.smoke_res[arm] = {"arm": arm, "ran": False, "why": f}
                self.say(f"STOP before smoke {arm}: {f}")
                return None, f"a holder before smoke {arm}: {f}"
            d = os.path.join(self.out, "smoke", arm)
            argv = C.smoke_argv(arm, os.path.relpath(os.path.join(d, "host-raw.json"), ROOT),
                                labels_out=os.path.relpath(os.path.join(d, "labels.bin"), ROOT))
            rc, t0, t1, cpu, raw, rwhy, err = self.run_host(argv, d)
            left = C.left_from_smoke(raw, t0)
            R, pred, why_r, rdet = C.r_for(raw, pm, left_s=left) if (arm != "ACC" and C.core_pass(raw)) else (None, {}, "", {})
            rec = {"arm": arm, "ran": True, "argv": argv, "rc": rc, "t0_ms": t0, "t1_ms": t1, "host_cpu_ext_s": cpu,
                   "die_start_c": die, "die_gate_wait_s": round(waited, 1), "result_read": rwhy or "the host's own --out file",
                   "status": (raw or {}).get("status"), "core_status": (raw or {}).get("core_status"),
                   "logits_status": (raw or {}).get("logits_status"), "tensor_error_or": (raw or {}).get("tensor_error_or"),
                   "first_mismatch": (raw or {}).get("first_mismatch"), "accuracy": (raw or {}).get("accuracy"),
                   "work_cycles_max": ((raw or {}).get("work_cycles") or {}).get("max"),
                   "copy_cycles_max": (raw or {}).get("copy_cycles_max"), "core_pass": C.core_pass(raw),
                   "R": R, "R_predicted_s": {str(k): round(v, 4) for k, v in pred.items()}, "R_why": why_r,
                   "R_registered_rule": rdet.get("R_registered_rule"), "R_host_cap": rdet.get("cap"), "budget_left_s": left,
                   "off_clock": self.off_clock_in(t0, t1), "did_not_finish": C.did_not_finish(raw, rc, err)}
            if C.core_pass(raw) and (raw or {}).get("logits_status") == "FAIL":
                rec["note"] = "a logits-only failure: a debug-path defect, recorded; the core checks passed (E202.md 7.2)"
            self.smoke_res[arm] = rec
            with open(os.path.join(d, "smoke.json"), "w") as fo:
                json.dump(rec, fo, indent=1)
            acc_s = ""
            if raw and raw.get("accuracy"):
                acc_s = ", accuracy %s of %s" % (raw["accuracy"].get("correct"), raw["accuracy"].get("scored"))
            self.say(f"smoke {arm}: rc {rc}, core {rec['core_status']}, logits {rec['logits_status']}, status {rec['status']}"
                     f"{acc_s} ({(t1 - t0) / 1000:.1f} s){'' if raw else '; no result: ' + rwhy}")
            if rec["did_not_finish"]:
                self.stops.stop = self.stops.stop or f"K1: smoke {arm}'s launch did not finish (rc {rc}{'' if raw else '; no record'})"
                return None, self.stops.stop
            if self.stopped():
                return None, f"a stop line tripped during smoke {arm}: {self.stopped()}"
        core = {a: self.smoke_res[a]["core_pass"] for a in self.smoke_res}
        if core.get("T-scp") and core.get("Z-scp"):
            return "scp", "T-scp and Z-scp read core PASS: the scp pair is scored"
        if core.get("T-dram") and core.get("Z-dram"):
            return "dram", "the scp pair's smoke failed and T-dram and Z-dram read core PASS: the registered fallback, the dram pair, is scored"
        return None, "no pair read core PASS (%s)" % ", ".join(f"{a} {self.smoke_res[a].get('core_status')}" for a in self.smoke_res)

    # ------------------------------------------------------------------ one burst
    def one_burst(self, key, k, idx, label, R):
        d = os.path.join(self.out, "bursts", key, f"b{k}")
        bk = f"{key}/b{k}"
        why = self.may_start("burst")
        if why:
            self.say(f"burst {idx}: {key} b{k} not started ({why}): no data")
            return {"burst": bk, "ran": False, "why": why}
        ok, die, waited, gwhy = self.die_gate()
        if not ok and gwhy:
            self.say(f"burst {idx}: {key} b{k} not started ({gwhy}; the die gate read {die} C after {waited:.0f} s): no data")
            return {"burst": bk, "ran": False, "why": f"{gwhy} (in the die gate's wait: {die} C after {waited:.0f} s)"}
        if not ok:
            self.say(f"burst {idx}: {key} b{k} skipped by the die gate (minshire[0] {die} C after {waited:.0f} s): no data")
            return {"burst": bk, "ran": False, "why": f"die gate: {die} C after {waited:.0f} s"}
        why = self.may_start("burst")
        if why:
            self.say(f"burst {idx}: {key} b{k} not started ({why}): no data")
            return {"burst": bk, "ran": False, "why": why}
        f = self.foreign()
        if f:
            self.stops.stop = self.stops.stop or f"a holder or a foreign device process: {f}"
            self.say(f"STOP before burst {idx}: {f}")
            return {"burst": bk, "ran": False, "why": f}
        os.makedirs(d, exist_ok=True)
        t_start = now_ms()
        with self.lock:
            self.in_burst = bk
        low = die is not None and die < C.DIE_LOW_C
        self.say(f"burst {idx}: {key} b{k} (R {R}; {label}; die {die} C{'; below the forecast band' if low else ''})")
        if not self.nap(self.a.idle_before):
            with self.lock:
                self.in_burst = None
            self.say(f"burst {idx}: a stop tripped in its rest before: no host process started")
            return {"burst": bk, "ran": False, "why": "stop: " + str(self.stopped())}
        w, st = key.split("-")
        argv = C.host_argv(w, st, "train", R, os.path.relpath(os.path.join(d, "host-raw.json"), ROOT))
        rc, h0, h1, cpu, raw, rwhy, err = self.run_host(argv, d)
        self.idle(self.a.idle_after)          # whole, even after a stop: the host ran, so its burst keeps its after window
        t_end = now_ms()
        with self.lock:
            self.in_burst = None
            sl = [ln for (t, ln) in self.samples if t_start - 1000 <= t <= t_end + 500]
        with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as g:
            for ln in sl:
                g.write(ln + "\n")
        with open(os.path.join(d, "host.json"), "w") as fo:
            fo.write(json.dumps(C.adapt(raw, rwhy)) + "\n")
        flags = []
        if self.stopped():
            flags.append(f"a stop line tripped during this burst: {self.stopped()}")
        if low:
            flags.append(f"T0 below the forecast band ({die} C < {C.DIE_LOW_C} C)")
        if not raw:
            flags.append(f"no host result: {rwhy}")
        run = {"preset": key, "card": C.BOX, "dry": self.dry, "lock": C.LOCK if not self.dry else "DRY", "build": C.BUILD,
               "host_args": " ".join(argv[1:]), "reps_planned": 1, "passes_R": R, "idle_before_s": self.a.idle_before,
               "idle_after_s": self.a.idle_after, "every_ms": C.EVERY_MS, "sampler": " ".join(self.cmd_sampler(C.CAP_S + 1200)),
               "sampler_t0_ms": self.sampler_t0, "host_t0_ms": h0, "host_t1_ms": h1, "end_ms": t_end, "host_rc": rc,
               "foreign": None, "rapl": "not read: the lab's default (E202.md 10)", "rapl_uj": [None, None],
               "host_cpu_ext_s": cpu, "stub_card": self.a.double if self.dry else None}
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(run, fo, indent=1)
        with self.lock:
            sa = self.set_aside.get(bk)
        good = C.burst_good(raw, R)
        with open(os.path.join(d, "burst.json"), "w") as fo:
            json.dump({"config": key, "burst": k, "order_index": idx, "R": R, "set_aside": sa, "label": label,
                       "die_start_c": die, "die_gate_wait_s": round(waited, 1), "flags": flags, "t_start_ms": t_start,
                       "t_end_ms": t_end, "host_rc": rc, "host_status": (raw or {}).get("status"),
                       "core_status": (raw or {}).get("core_status"), "host_checks_good": good,
                       "result_read": rwhy or "the host's own --out file", "dry": self.dry}, fo, indent=1)
        self.say(f"burst {idx}: {key} b{k} done: host rc {rc}, status {(raw or {}).get('status')}, core "
                 f"{(raw or {}).get('core_status')}{', SET ASIDE: ' + sa if sa else ''}{', ' + '; '.join(flags) if flags else ''}")
        out = {"burst": bk, "ran": True, "rc": rc, "status": (raw or {}).get("status"), "good": good, "set_aside": sa}
        if C.did_not_finish(raw, rc, err):
            self.stops.stop = self.stops.stop or f"K1: burst {idx} ({bk})'s launch did not finish (rc {rc}{'' if raw else '; no record'})"
            out["did_not_finish"] = True
        return out

    # ------------------------------------------------------------------ the whole session
    def run(self):
        a = self.a
        tag = " DRY" if self.dry else ""
        self.say(f"session start (T0 {a.t0} = {time.strftime('%H:%M:%S %Z', time.localtime(a.t0))}; plan FULL; its files in "
                 f"{a.out}){tag}")
        lockf = None
        result = {"t0": a.t0, "dry": self.dry, "smoke": self.smoke_res, "bursts": self.bursts}
        rc = 0
        crash = None
        try:
            why = self.refusals()
            if why:
                self.say(f"refused, no device opened: {why}")
                return 2
            lockp = os.path.join(self.out, "dry.lock") if self.dry else C.LOCK
            try:
                lockf = open(lockp, "a+")
            except OSError as e:
                self.say(f"refused, no device opened: card 0's lock cannot be opened ({type(e).__name__})")
                return 2
            try:
                fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.say("refused, no device opened: card 0's lock is held")
                return 2
            f = self.foreign()
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((f or "no holder of another login; no other user's device process") + "\n")
            if f:
                self.say(f"refused, no device opened: a holder or a foreign device process ({f})")
                return 2
            self.t_first = time.time()
            self.say("first card command: config start, stamped as it starts at %s.%03d (the cap counts from it)" % (
                time.strftime("%H:%M:%S", time.localtime(self.t_first)), int(self.t_first * 1000) % 1000))
            cfg0, why = self.config("start")
            self.device_opened = True
            if not cfg0 or not C.config_ok(cfg0):
                self.say(f"GATE-STOP: config start: {why or json.dumps(cfg0)}: not TDP 0 W / 65 C / 600 MHz as found: no launch")
                return 3
            self.say("config start: TDP 0 W, threshold 65 C, minion 600 MHz (read, nothing set)")
            if not self.start_sampler():
                self.say("GATE-STOP: the sampler would not start: no launch")
                return 3
            self.sampler_t0 = self.samples[0][0] if self.samples else now_ms()
            ok, res = self.stop_path_test()
            self.say(f"stop-path test {'passed' if ok else 'failed'}: " + "; ".join(
                f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, start {'refused' if v['refused_a_start'] else 'NOT refused'}"
                for k, v in res.items()))
            if not ok:
                self.say("GATE-STOP: the stop-path test failed: no launch")
                return 3
            result["anchor1"] = self.anchor(1)
            stage, why = self.smoke()
            result["scored_stage"] = stage
            result["smoke_gate"] = why
            if stage is None:
                self.say(f"GATE-STOP: the smoke gate: {why}: no burst (no data, never a failed forecast)")
                return 3
            self.say(f"smoke gate passed: {why}")
            Rs = {}
            for w in C.CONFIGS:
                for st in C.STAGES:
                    arm = ("T-" if w == "trained" else "Z-") + st
                    r = self.smoke_res.get(arm) or {}
                    Rs[C.cfg_key(w, st)] = r.get("R") if r.get("core_pass") else None
            result["R"] = Rs
            reg = {}
            for k in Rs:
                sm = self.smoke_res.get(("T-" if k.startswith("trained") else "Z-") + k.split("-")[1]) or {}
                reg[k] = sm.get("R_registered_rule")
            result["R_registered_rule"] = reg
            self.say("the R rule (each arm from its own R = 1 smoke; the host's timeout cap after it): " + "; ".join(
                f"{k} R {v if v else 'none (no burst for the arm)'}" + (f" (the registered rule's R {reg[k]}, capped)"
                                                                        if reg.get(k) and reg[k] != v else "")
                for k, v in Rs.items() if k.endswith(stage) or stage == "scp"))
            report = stage == "scp"
            if a.sequence == "plan":
                seq = C.burst_sequence(stage, report)
            elif a.sequence == "short":             # --dry only (step 8 on the box): one burst of each configuration the day runs
                seq = [x for x in C.burst_sequence(stage, report) if x[1] == 1]
            else:                                   # --dry only (e2e): two bursts of each scored configuration, for the scorer
                seq = [x for x in C.burst_sequence(stage, False) if x[1] <= 2]
            ended = {}
            for key, k, idx, label in seq:
                if self.stopped():
                    break
                R = Rs.get(key)
                if not R:
                    arm = ("T-" if key.startswith("trained") else "Z-") + key.split("-")[1]
                    sm = self.smoke_res.get(arm) or {}
                    why = ("its smoke did not read core PASS" if not sm.get("core_pass")
                           else "the R rule found no allowed R: " + (sm.get("R_why") or "no allowed R fits the 6 s ceiling"))
                    self.bursts.append({"burst": f"{key}/b{k}", "ran": False, "why": "no burst for the arm: " + why})
                    continue
                if key in ended:
                    self.bursts.append({"burst": f"{key}/b{k}", "ran": False, "why": f"the arm ended at {ended[key]}"})
                    continue
                b = self.one_burst(key, k, idx, label, R)
                self.bursts.append(b)
                if b.get("ran") and not b.get("good"):
                    ended[key] = b["burst"]
                    self.say(f"the arm {key} ends: {b['burst']}'s host checks did not pass (E202.md 9)")
            result["anchor2"] = self.anchor(2) if not self.stopped() else {"anchor": 2, "ran": False, "why": "a stop"}
            if self.stopped():
                self.say(f"STOP: {self.stopped()}: the queue ended after the running process")
            return 0
        except BaseException as e:        # fix-e202 (verify-e202's finding 2): a crash is named before the closing, never a clean end
            crash = f"{type(e).__name__}: {e}"
            self.stops.stop = self.stops.stop or f"a crash of the runner ({crash[:200]})"
            self.say(f"CRASH: {crash[:400]} (the runner's own fault: nothing further starts, the closing follows, the runner exits 1)")
            raise
        finally:
            dl = self.close_deadline()
            sampler_stopped = self.stop_sampler(dl)
            if self.device_opened and not sampler_stopped:   # fix-e202 (finding 8): our sampler may still hold the management node
                self.closing = "not read: our sampler did not stop on SIGTERM (it may still hold the single-open management node)"
                self.say(f"closing config read: {self.closing}")
            elif self.device_opened:
                f = self.foreign(min(30.0, max(5.0, dl - time.time() - 12.0)) if dl else 30.0)
                if f:
                    self.closing = f"not read: et-who does not read the card free ({f})"
                    self.say(f"closing config read: {self.closing}")
                else:
                    left = (dl - time.time()) if dl else 30
                    cfg1, why = self.config("end", max(10.0, min(30.0, left)))
                    self.closing = "read" if cfg1 else why
                    self.say("config end: " + (f"TDP {cfg1.get('tdp_w')} W, threshold {cfg1.get('temp_threshold_c')} C, minion "
                                               f"{cfg1.get('minion_mhz')} MHz" if cfg1 else why))
            self.tel.close()
            tp = os.path.join(self.out, "telemetry.jsonl")
            if os.path.exists(tp):
                with open(tp, "rb") as fi, gzip.open(tp + ".gz", "wb") as fo:
                    fo.write(fi.read())
                os.remove(tp)
            result.update({"stop": self.stops.stop, "off_clock": self.stops.events, "set_aside": self.set_aside,
                           "t_first_ms": int(self.t_first * 1000) if self.t_first else None, "t_close_ms": now_ms(),
                           "end_bound_ms": int(self.close_deadline() * 1000) if self.t_first else None,
                           "closing_config": self.closing, "crash": crash,
                           "bursts_ran": sum(1 for b in self.bursts if b.get("ran"))})
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
            rows.append(f"{sha(p)}  {rel}")
    with open(os.path.join(out, "MANIFEST.sha256"), "w") as f:
        f.write("\n".join(rows) + "\n")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("what", choices=["session"])
    ap.add_argument("--t0", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-epoch", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--double", choices=["alt", "base", "inject"], default="inject")
    ap.add_argument("--sequence", choices=["plan", "short", "e2e"], default="plan")
    ap.add_argument("--idle-before", type=float, default=C.IDLE_BEFORE_S)
    ap.add_argument("--idle-after", type=float, default=C.IDLE_AFTER_S)
    ap.add_argument("--anchor-s", type=float, default=C.ANCHOR_S)
    ap.add_argument("--die-wait-s", type=float, default=C.DIE_GATE_WAIT_S)
    ap.add_argument("--cap-burst-s", type=float, default=C.CAP_BURST_START_S)
    ap.add_argument("--cap-end-s", type=float, default=C.CAP_S)
    a = ap.parse_args(argv)
    a.refused = ""
    if not a.dry:
        changed = [n for n, v in (("--idle-before", a.idle_before != C.IDLE_BEFORE_S), ("--idle-after", a.idle_after != C.IDLE_AFTER_S),
                                  ("--anchor-s", a.anchor_s != C.ANCHOR_S), ("--die-wait-s", a.die_wait_s != C.DIE_GATE_WAIT_S),
                                  ("--cap-burst-s", a.cap_burst_s != C.CAP_BURST_START_S), ("--cap-end-s", a.cap_end_s != C.CAP_S),
                                  ("--sequence", a.sequence != "plan"), ("--double", a.double != "inject")) if v]
        desk = sorted(k for k in os.environ if k.startswith(C.DESK_VARS))
        if changed:
            a.refused = f"{', '.join(changed)} change the registered session and are read with --dry only"
        elif desk:
            a.refused = f"a desk-test variable is set ({', '.join(desk)}) but --dry is not"
        if a.refused:
            print(f"refused, no device opened: {a.refused}")      # also in the session's log (refusals(), first)
    s = Session(a)
    signal.signal(signal.SIGTERM, s.on_signal)      # an operator's stop, never a kill: the session ends itself
    signal.signal(signal.SIGINT, s.on_signal)
    return s.run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
