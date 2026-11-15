#!/usr/bin/env python3
"""E191's runner (Q178, the kit, Sat 14 Nov 2026, written after E189's data commit fa9098c4 and before any E191 datum): the blind day's
whole session on aifoundry1 card 1, in energy.sh's form, with the live stops. It is E189's runner (tools/claims-v3/e189/run_e189.py,
b42dc95c, unchanged beside it) with E191's dated note 1 (8c8f825f) carried in, and the defects E189's real day and its readiness check
showed, each fixed as kit mechanics (KIT.md section 1 names each). Python's own modules only (aifoundry1's system python3).
session_e191.sh starts it, detached.

    python3 -B tools/claims-v3/e191/run_e191.py session --t0 T0 --out build/e191/T<T0> --programs ledger,spp
        [--deadline-epoch E] [--rapl-allowed]
    python3 -B tools/claims-v3/e191/run_e191.py session --dry --double alt|base|inject --t0 T0 --out DIR [--sequence plan|short|e2e]
        [--idle-before S --idle-after S --anchor-s S --die-wait-s S --cap-pass-s S --cap-end-s S --host-bound-s S]   (--dry only)

What changes from E189's runner (note 1, section 1):
  - CARD 1 SELECTED FOR EVERY PROCESS (item 1): every process the runner starts carries ET_DEVICES=1 (and V3_DEVICE=1) in its
    environment: the guard's `ettelem config` (start and end), its `ettelem sample`, both hosts at every launch (the smoke's included),
    et-who; E189's two removals of them are gone. E191's guard refuses any box but aifoundry1 and any ET_DEVICES but 1;
  - CARD 1'S LOCK (item 2): /run/lock/etsoc-shire1.lock, flock -n, held by this process to the end; never card 0's;
  - THE BOX CHECK (real path; E190 arm B's form): the host is aifoundry1, the reader build/ettelem/ettelem at its pin, each program's
    build record written today by build_e191.sh with the host at its sha256 and the ET_DEVICES reading passed; else no device opened;
  - THE IDENTITY GATE (item 3; e191_ident.py): (a) the start config read keeps its stderr (config-start.err), which must name
    /dev/et1_mgmt and device ID 1, and its JSON TDP 65 W, threshold 65 C, minion 600 MHz (E191.md 2) and minion_mv below 510; (b) with
    the sampler running and before the smoke, et-who's lines of ours on card 1 only, one on /dev/et1_mgmt, none on card 0, and the
    sampler's own fds holding /dev/et1_mgmt and no card 0 node; either failing: the gate, no launch;
  - THE WATCH at every launch: each host's stderr block and held nodes; another card named or held stops the session after that process
    (it is set aside); in the smoke each device-opening process must have shown card 1, else the smoke gate fails;
  - THE HOLDER RULE before the first card command and before each pass: no other login's holder line on either card (E189's foreign()),
    no line of ours on card 0, none of ours on card 1's ops node while no host runs, no other user's device process, and (new) no device
    process of ours but the session's own sampler;
  - THE 30 s BOUND (ready-e189's finding 1): the runner's bound around `timeout 10 <host>` no longer kills the `timeout` wrapper and goes
    on: when it expires, nothing is killed, the line "BOUND:" is logged, and THE QUEUE STOPS (nothing further starts beside a host that
    may still hold the card); the closing reads follow once that host has ended ("AFTER A BOUND" below);
  - THE PASS'S READING IN WORDS (E189's real day: its log said "host rc 1, status FAIL" for every SHORT copy burst): each pass's line
    adds the adapter's reading, PASS, SHORT (k of K launches, the host's own budget: scored on its launches) or FAILED RUN;
  - THE DRY PASS RECORDS every device-opening command line the real path would run (commands.jsonl) and asserts note 1's item 4 on them
    (dry_check: ET_DEVICES=1 on each; none names etsoc-shire0, /dev/et0_ or ET_DEVICES=0; none unsets ET_DEVICES; no dev_mngt_service or
    et-powertop); its doubles print card 1's identity block and hold stand-in nodes, so the identity gate and the watch run in it too.
What changes after the kit's verifier (verify-e191k; fix-e191k, Sat 14 Nov 2026, before any E191 datum; kit mechanics and gates made
stricter for safety, KIT.md section 4 names each; no registered number changes):
  - THE SAMPLER'S FRESHNESS (finding 2; E190's kit note 1's rule): a pass's host process, a smoke process and the die gate each need a live
    sampler, alive with a sample received under SAMPLE_FRESH_S (2 s) ago; one that is alive but quiet is stopped (SIGTERM only) and
    restarted; a pass whose sampler is not live just before its host process starts no host (no data), and the sampler is restarted
    before the next pass, else the queue stops ("the sampler would not restart");
  - ET-WHO UNREADABLE (finding 3): an et-who that exits other than 0, or answers with neither a holder line nor its no-holder sentence, is
    unreadable: before the first card command that refuses (no device opened), before a pass it stops the session, in the identity read
    it fails the gate (e191_ident.etwho_unreadable);
  - AFTER A BOUND (finding 4): the runner keeps card 1's lock while the host past its bound still runs, and the sampler keeps reading:
    it polls the host's end every second (nothing is killed) until the end bound less the closing's share; the closing config read runs
    only once that host has ended (never beside it); queue.json records the host's end, or that it still ran when the lock was released;
  - THE EARLY STOP (finding 5): a file named STOP in the session's own directory, or a SIGTERM to the runner's own process, asks for an
    early stop: the queue ends after the running process (its idle after whole), then the closing runs as for a stop line (the closing
    config read, queue.json, "session end", the lock released, MANIFEST.sha256 last); before the first card command it refuses (16);
  - OUR DEVICE PROCESSES (nit 6): DEV_COMM also matches a name ps shows cut to 15 characters (sparseparity_host as 'sparseparity_ho'), and
    for our own processes the executable's own name (/proc/<pid>/exe) is read too.
What changes after the kit's second verifier (verify-e191k2: HOLDS WITH FIXES, 6 nits; fix-e191k2, Sun 15 Nov 2026, before any E191 datum;
kit mechanics, KIT.md section 4 names each; no registered number changes):
  - A LIVE SAMPLE (nit 1): only a sample that carries every reading THE STOP LINES read (board_w, minshire[0], the minion clock; each a
    number: e191_common.sample_live) keeps the sampler live, starts it ("sampler started") and passes the die gate; any other line is still
    written to the telemetry and fed to the stop lines, and counted (queue.json's sampler_lines_not_live). A reader whose power request
    fails while it still prints lines is therefore quiet: stopped (SIGTERM only) and restarted, as finding 2 says. The freshness ages are
    read on time.monotonic() (a step of the wall clock cannot age or freshen a sample);
  - THE SAMPLER DURING A PASS (nit 2): each pass's run.json records the last live sample's age at its host's start, at its host's end and at
    the pass's end, the live samples in the host's span, and the largest gap between live samples from the pass's start to its end (and
    in the host's span); a pass whose largest gap is SAMPLE_FRESH_S (2 s) or more carries the flag "the sampler was not live during this
    pass" in pass.json and on its log line, and is listed in queue.json (passes_sampler_not_live). A flag only: the reducer and the scorer
    read nothing of it, and the scoring stays as registered; the next pass's freshness rule restarts a quiet sampler as before. Each smoke
    process's smoke.json records the same age at its end and its gap (the smoke gate's verdict is unchanged);
  - AN EARLY STOP AT THE GATE (nit 3): the stop file or a SIGTERM read after the start config read is read again just before the stop-path
    test and just after it; either way the log says "an early stop was asked for (...) before / during the stop-path test: the gate, no
    launch" (16, step 10's GATE-STOPPED, the closing as before), never "stop-path test failed", and stop-path.json carries early_stop;
  - THE BOX CHECK READS THE KERNELS TOO (nit 5): each program's kernel must be at its build record's kernel_sha256 and the record must
    carry the kernel gate's own "KERNEL OK <prog>:" line (build_e191.sh writes both only after THE KERNEL GATE passed those bytes), so a
    kernel changed after its build is refused before card 1's lock, as a host changed after its build already was.
Everything else is E189's: the sequence (plan-e191.json, never re-drawn), THE STOP LINES (65 W, 70 C, the clock line in a pass), the
stop-path test, the ramped smoke, the anchors, the die gate (60 C, 10 minutes, never past the cap), the cap (108 / 110 card-minutes
from the first card command), the end bound, ONE sampler, the pass's files (E191.md 8.1), the closing, MANIFEST.sha256 last. The
counters arm is DROPPED (E189's kit section 5; E191.md 7 lets E191's kit keep it only if E189's kept it). Every device command is a
READ (dmcmd_audit GO). --dry swaps every device-opening process for fake_card_e191.py's doubles, takes a lock file in the output
directory, and marks every line DRY (the rest rule skips it). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
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
import e191_common as C  # noqa: E402
import e191_ident as I  # noqa: E402

ROOT = C.REPO
DEV_COMM = re.compile(r"_ho(st)?$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner\.Worker$")   # nit 6: _ho(st)?
RAPL_F = "/sys/class/powercap/intel-rapl:0/energy_uj"
FORBIDDEN = ("etsoc-shire0", "/dev/et0_", "ET_DEVICES=0", "dev_mngt_service", "et-powertop")


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def pacific_day():
    return subprocess.run(["date", "+%F"], env=dict(os.environ, TZ="America/Los_Angeles"), capture_output=True, text=True).stdout.strip()


def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def exe_name(pid):
    """The name of one of OUR processes' executable (/proc/<pid>/exe's last part), never cut to 15 characters as ps's comm is; '' if it
    cannot be read (nit 6)."""
    try:
        return os.path.basename(os.readlink(f"/proc/{pid}/exe")).replace(" (deleted)", "")
    except OSError:
        return ""


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
        self.samples = []
        self.last = None
        self.lock = threading.Lock()
        self.set_aside = {}
        self.sproc = None
        self.tel = open(os.path.join(self.out, "telemetry.jsonl"), "a")
        self.queue = []
        self.t_first = None
        self.device_opened = False
        self.sampler_t0 = None
        self.programs = [p for p in a.programs.split(",") if p]
        self.env = C.device_env()                       # ET_DEVICES=1 and V3_DEVICE=1 for every process (note 1, item 1)
        self.identity = {}
        self.bound = []                                 # host processes that outlived the runner's 30 s bound (never killed)
        self.bound_procs = {}                           # their Popen objects by pid (finding 4: their end is polled, the lock kept)
        self.last_rx = None                             # finding 2: when the last LIVE sample arrived (time.monotonic(); fix-e191k2)
        self.rx_mono = []                               # fix-e191k2 (nit 2): every live sample's arrival (time.monotonic()), in order
        self.n_not_live = 0                             # fix-e191k2 (nit 1): lines without a stop line's reading (never live), in all
        self.n_not_live_since = 0                       # ... and since the last live sample (the staleness words)
        self.not_live_passes = []                       # fix-e191k2 (nit 2): the passes during which the sampler was not live
        self.stop_file = os.path.join(self.out, C.STOP_FILE)    # finding 5: the early stop's file, in the session's own directory
        self.term_req = None                            # finding 5: when a SIGTERM asked for an early stop (set by the handler only)
        self.stop_req_why = None                        # the early stop's words, once it is taken as the session's stop
        self.cmd_log = open(os.path.join(self.out, "commands.jsonl"), "a")
        self.me = pwd.getpwuid(os.getuid()).pw_name     # our login, as et-who prints it (never written anywhere)
        self.dev_dir = None
        if self.dry:
            self.env["E191_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            open(self.env["E191_FAKE_SCHED"], "a").close()
            self.dev_dir = os.path.abspath(os.path.join(self.out, "dev"))   # the doubles' stand-in nodes (et1_mgmt, et1_ops)
            os.makedirs(self.dev_dir, exist_ok=True)
            self.env["E191_FAKE_DEVDIR"] = self.dev_dir
            self.env["E191_FAKE_LOCK"] = os.path.abspath(os.path.join(self.out, "dry.lock"))
            if a.double in ("alt", "base"):
                self.env["E191_FAKE_BASE"] = a.double
        self.watch_dir = self.dev_dir if self.dry else None

    # ------------------------------------------------------------------ the log, in the kits' form
    def say(self, words):
        w = ("DRY " + words) if self.dry and not words.startswith("session start") else words
        line = f"{stamp()} {w}"
        self.log_f.write(line + "\n")
        self.log_f.flush()
        print(line, flush=True)

    def record(self, kind, real_argv, used_argv, opens_device=True):
        """Every command the session starts, with the real path's command line and its ET_DEVICES (the dry check reads it)."""
        self.cmd_log.write(json.dumps({"kind": kind, "real": real_argv, "used": used_argv, "dry": self.dry,
                                       "et_devices": self.env.get("ET_DEVICES"), "opens_device": opens_device,
                                       "lock": C.LOCK}) + "\n")
        self.cmd_log.flush()

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def fake(self):
        return [sys.executable, "-B", os.path.join(HERE, "fake_card_e191.py")]

    def real_config(self):
        return ["timeout", str(C.HOST_TIMEOUT_S), "bash", C.GUARD, "config"]

    def cmd_config(self):
        c = self.fake() + ["config"] if self.dry else self.real_config()
        self.record("config", self.real_config(), c)
        return c

    def real_sampler(self, seconds):
        return ["bash", C.GUARD, "sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)]

    def cmd_sampler(self, seconds, rec=True):
        c = (self.fake() + ["sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)]) if self.dry else self.real_sampler(seconds)
        if rec:
            self.record("sampler", self.real_sampler(seconds), c)
        return c

    def cmd_etwho(self):
        c = self.fake() + ["etwho"] if self.dry else ["timeout", "20", "et-who"]
        self.record("et-who", ["timeout", "20", "et-who"], c, opens_device=False)
        return c

    def host_cmd(self, argv):
        real = ["timeout", str(C.HOST_TIMEOUT_S)] + argv
        if self.dry:
            c = self.fake() + ["host-ledger" if os.path.basename(argv[0]) == "ledger_host" else "host-spp"] + argv[1:]
        else:
            c = real
        self.record("host", real, c, opens_device="--selftest" not in argv)
        return c

    # ------------------------------------------------------------------ the box check (real path)
    def box_check(self):
        """'' when the box, the reader and today's builds are E191's (the module docstring); else why. Never in --dry."""
        why = []
        host = socket.gethostname().split(".")[0]
        if host != C.BOX:
            why.append(f"this host is {host!r}, not {C.BOX}")
        if self.env.get("ET_DEVICES") != C.ET_DEVICES:
            why.append("ET_DEVICES is not 1 in the session's environment")
        rp = os.path.join(ROOT, C.READER)
        if not os.path.exists(rp):
            why.append(f"no reader {C.READER}")
        elif sha256(rp) != C.READER_SHA256:
            why.append(f"the reader {C.READER} is not at its pin {C.READER_SHA256[:12]}")
        day = pacific_day()
        for prog in self.programs:
            rec_p = os.path.join(ROOT, C.BUILD_REC.get(prog, "/nonexistent"))
            host_p = os.path.join(ROOT, C.LEDGER_HOST if prog == "ledger" else C.SPP_HOST)
            elf_p = os.path.join(ROOT, C.LEDGER_ELF if prog == "ledger" else C.SPP_ELF)
            try:
                rec = json.load(open(rec_p))
            except (OSError, ValueError):
                why.append(f"no build record for {prog} ({C.BUILD_REC.get(prog)})")
                continue
            if rec.get("builder") != "build_e191.sh" or rec.get("verdict") != "BUILT" or rec.get("day") != day:
                why.append(f"{prog}'s build record is not build_e191.sh's BUILT of today ({rec.get('builder')}, {rec.get('verdict')}, {rec.get('day')})")
            elif not os.path.exists(host_p) or sha256(host_p) != rec.get("host_sha256"):
                why.append(f"{prog}'s host is not the one its build record names")
            elif not os.path.exists(elf_p) or sha256(elf_p) != rec.get("kernel_sha256"):      # fix-e191k2 (verify-e191k2's nit 5)
                why.append(f"{prog}'s kernel is not the one its build record names (THE KERNEL GATE passed that one at the build)")
            elif not str(rec.get("kernel_gate") or "").startswith(f"KERNEL OK {prog}: "):
                why.append(f"{prog}'s build record carries no passing kernel gate line ({str(rec.get('kernel_gate'))[:60]!r})")
            elif rec.get("et_devices") != "yes":
                why.append(f"{prog}'s build record has no passing ET_DEVICES reading ({rec.get('et_devices')})")
        return "; ".join(why)

    # ------------------------------------------------------------------ holders
    def our_device_procs(self):
        """Our own device processes (lib.sh's DEV_COMM, on ps's comm or, nit 6, on the executable's own name) but the session's sampler
        and its children: counts."""
        if self.dry:
            return 0
        skip = set(I.descendants(self.sproc.pid)) if self.sproc else set()
        ps = subprocess.run(["ps", "-eo", "uid=,pid=,comm="], capture_output=True, text=True).stdout.splitlines()
        n = 0
        for ln in ps:
            f = ln.split(None, 2)
            if len(f) == 3 and int(f[0]) == os.getuid() and int(f[1]) not in skip and (
                    DEV_COMM.search(f[2].strip()) or DEV_COMM.search(exe_name(int(f[1])))):
                n += 1
        return n

    def foreign(self):
        """et-who's lines (e191_ident.foreign_lines: another login's on either card, ours on card 0, ours on card 1's ops node), other
        users' device processes (energy.sh's foreign()) and our own device processes but the sampler; counts, never names."""
        try:
            w = subprocess.run(self.cmd_etwho(), cwd=ROOT, capture_output=True, text=True, timeout=30, env=self.env)
            lines = w.stdout.splitlines()
            rc = w.returncode
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"et-who unreadable ({type(e).__name__})"
        uw = I.etwho_unreadable(rc, lines)          # finding 3: rc not 0, or neither a holder line nor the no-holder sentence
        if uw:
            return uw
        why, _ = I.foreign_lines(lines, self.me)
        n = ours = 0
        if not self.dry:
            ps = subprocess.run(["ps", "-eo", "uid=,pid=,comm="], capture_output=True, text=True).stdout.splitlines()
            uid = os.getuid()
            for ln in ps:
                f = ln.split(None, 2)
                if len(f) == 3 and int(f[0]) != uid and DEV_COMM.search(f[2].strip()):
                    n += 1
            ours = self.our_device_procs()
        parts = [x for x in (why, f"{n} other users' device process(es)" if n else "",
                             f"{ours} device process(es) of ours besides the sampler" if ours else "") if x]
        return "; ".join(parts)

    # ------------------------------------------------------------------ the sampler and the live stops
    def _reader(self, proc):
        for raw in proc.stdout:
            if not raw.startswith("{"):
                continue
            try:
                s = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(s, dict):
                continue
            self.tel.write(raw if raw.endswith("\n") else raw + "\n")
            live = C.sample_live(s)                 # fix-e191k2 (nit 1): live only with every stop line's reading (board_w, minshire[0], clock)
            with self.lock:
                self.samples.append((s.get("t_ms", 0), raw.rstrip("\n")))
                if live:
                    self.last = s                   # the die gate reads the last LIVE sample
                    self.last_rx = time.monotonic()     # finding 2: when the last live sample ARRIVED (monotonic: fix-e191k2)
                    self.rx_mono.append(self.last_rx)
                    self.n_not_live_since = 0
                else:
                    self.n_not_live += 1
                    self.n_not_live_since += 1
                acts = self.stops.feed(s, self.in_pass)
                if self.test_stops is not None:
                    self.test_stops.feed(s, "the stop-path test")
                if "set-aside" in acts and self.in_pass and self.in_pass not in self.set_aside:
                    self.set_aside[self.in_pass] = f"a sample off {C.CLOCK_MHZ} MHz ({(s.get('mhz') or {}).get('minion')} MHz at t_ms {s.get('t_ms')})"
        self.tel.flush()

    def close_deadline(self):
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
            with self.lock:
                n0 = len(self.rx_mono)              # fix-e191k2 (nit 1): started once a LIVE sample has arrived from it
            th = threading.Thread(target=self._reader, args=(self.sproc,), daemon=True)
            th.start()
            t = time.time()
            while time.time() - t < 10:
                with self.lock:
                    got = len(self.rx_mono) > n0
                if got:
                    self.say(f"sampler started (attempt {attempt}, pid {self.sproc.pid}, every {C.EVERY_MS} ms)")
                    if self.identity.get("sampler_nodes") is not None:      # a restarted sampler is read again (the identity)
                        why = I.sampler_identity(I.proc_nodes(self.sproc.pid, self.watch_dir))
                        if why:
                            with self.lock:
                                self.stops.stop = self.stops.stop or f"identity: the restarted sampler: {why}"
                            self.say(f"STOP: identity: the restarted sampler: {why}")
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
        """SIGTERM only (never kill -9 a tool): 30 s, then once more and 60 s; each wait ends CLOSE_CONFIG_S before the end bound but
        lasts at least 2 s (E189's end bound, unchanged)."""
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

    # ------------------------------------------------------------------ finding 2: the sampler's freshness (E190's kit note 1's rule)
    def fresh(self):
        """The sampler is live: its process alive and a LIVE sample (e191_common.sample_live) received less than SAMPLE_FRESH_S ago."""
        with self.lock:
            rx = self.last_rx
        return self.sampler_alive() and rx is not None and (time.monotonic() - rx) < C.SAMPLE_FRESH_S

    def staleness(self):
        with self.lock:
            rx, nl = self.last_rx, self.n_not_live_since
        return (f"alive {self.sampler_alive()}, last live sample {'never' if rx is None else '%.1f s ago' % (time.monotonic() - rx)}"
                + (f", {nl} line(s) since without a stop line's reading" if nl else ""))

    def sample_age(self):
        """Seconds since the last live sample arrived (rounded to 0.01 s; None if none ever did): written beside each host process."""
        with self.lock:
            rx = self.last_rx
        return None if rx is None else round(time.monotonic() - rx, 2)

    def live_gap(self, m0, m1):
        """fix-e191k2 (verify-e191k2's nit 2): the longest stretch of [m0, m1] (time.monotonic()) with no live sample, in seconds: from the
        last live sample at or before m0 (else m0) to the first after it, between live samples, and from the last one to m1; and the number
        of live samples inside (m0, m1]. A stretch of SAMPLE_FRESH_S or more is time in which the sampler was not live."""
        with self.lock:
            i0 = bisect.bisect_right(self.rx_mono, m0)
            i1 = bisect.bisect_right(self.rx_mono, m1)
            prev = self.rx_mono[i0 - 1] if i0 > 0 else m0
            inside = self.rx_mono[i0:i1]
        pts = [prev] + inside + [m1]
        return round(max(b - a for a, b in zip(pts, pts[1:])), 2), len(inside)

    def ensure_fresh_sampler(self):
        """A live sampler, or a restart (one that is alive but quiet is stopped first, SIGTERM only); False when none can run."""
        if self.fresh():
            return True
        why = self.may_start(60) if self.t_first else ""
        if why:
            self.say(f"the sampler is not live ({self.staleness()}); not restarted: no pass can start ({why})")
            return False
        self.say(f"the sampler is not live ({self.staleness()}): restarting it")
        if self.sampler_alive():
            self.stop_sampler(self.close_deadline())
        return self.start_sampler()

    # ------------------------------------------------------------------ finding 5: the early stop (the stop file, or SIGTERM)
    def on_sigterm(self, signum, frame):
        """SIGTERM asks for the early stop: only a flag here (no lock is taken in a handler); may_start and nap take it as the stop."""
        self.term_req = self.term_req or time.time()

    def stop_requested(self):
        """True once an early stop has been asked for (a file named STOP in the session's directory, or a SIGTERM to this process); the
        first time, it becomes the session's stop: the queue ends after the running process, then the closing runs."""
        if self.stop_req_why is None:
            why = ""
            if self.term_req:
                why = "a SIGTERM to the runner"
            elif os.path.exists(self.stop_file):
                why = f"the stop file ({C.STOP_FILE} in the session's directory)"
            if not why:
                return False
            self.stop_req_why = f"an early stop was asked for ({why})"
            with self.lock:
                self.stops.stop = self.stops.stop or self.stop_req_why
            self.say(f"STOP asked: {self.stop_req_why}: no further process starts; the running one (if any) ends by itself, then the closing")
        return True

    def latest(self):
        with self.lock:
            return dict(self.last) if self.last else None

    def nap(self, seconds):
        end = time.time() + seconds
        while time.time() < end:
            if self.stops.stop or self.stop_requested():
                return False
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    def idle(self, seconds):
        """The idle AFTER a host process: it runs to its end whatever the stop lines say (E189's fault 2)."""
        end = time.time() + seconds
        while time.time() < end:
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    # ------------------------------------------------------------------ the gates
    def may_start(self, seconds):
        self.stop_requested()                       # finding 5: the stop file and SIGTERM are read before every start
        if self.stop_req_why and self.stops.stop == self.stop_req_why:
            return self.stop_req_why
        if self.stops.stop or (self.test_stops is not None and self.test_stops.stop):
            return "a stop line has tripped"
        el = time.time() - self.t_first
        if el > self.a.cap_pass_s or el + (seconds if seconds > 60 else 0) > self.a.cap_pass_s:
            return f"the cap: {el / 60:.1f} card-minutes since the first card command (no pass after {self.a.cap_pass_s / 60:g})"
        if self.a.deadline_epoch and time.time() + seconds + 90 > self.a.deadline_epoch:
            return "the window's last end is too close"
        return ""

    def die_gate(self):
        t = time.time()
        while True:
            s = self.latest() if self.fresh() else None      # finding 2: only a live sample passes the gate
            die = C.die_of(s) if s else None
            if die is not None and die <= C.DIE_GATE_C:
                return True, die, time.time() - t, ""
            why = self.may_start(60)
            if why:
                return False, die, time.time() - t, why
            if time.time() - t >= self.a.die_wait_s:
                return False, die, time.time() - t, ""
            if not self.ensure_fresh_sampler():
                return False, die, time.time() - t, "the sampler is not live"
            time.sleep(1.0)

    # ------------------------------------------------------------------ reads
    def config(self, name, bound_s=30):
        """The config read through the guard; its stderr is kept (config-<name>.err: the device layer's identity block)."""
        try:
            r = subprocess.run(self.cmd_config(), cwd=ROOT, capture_output=True, text=True, timeout=bound_s, env=self.env)
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, "", f"config read failed ({type(e).__name__})"
        j = C.last_json(r.stdout)
        with open(os.path.join(self.out, f"config-{name}.json"), "w") as f:
            f.write(json.dumps(j) + "\n")
        with open(os.path.join(self.out, f"config-{name}.err"), "w") as f:
            f.write(r.stderr)
        if r.returncode != 0 or not j:
            return None, r.stderr, f"config read rc {r.returncode}, no JSON line"
        return j, r.stderr, ""

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

    # ------------------------------------------------------------------ one host process, watched
    def run_host(self, argv, out_dir, stdout_name):
        """ONE host process under `timeout 10`, watched (e191_ident.HostWatch). The runner's own bound is HOST_BOUND_S (30 s): when it
        expires nothing is killed (a device process is never killed, nor the `timeout` wrapper that waits on it), the session logs
        BOUND and the queue stops (ready-e189's finding 1: E189's runner killed the wrapper and went on, so a host stuck in the driver
        could have been left running beside the next pass's). Returns (rc, t0, t1, cpu, text, watch result); rc None when bound."""
        os.makedirs(out_dir, exist_ok=True)
        u0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = now_ms()
        errp = os.path.join(out_dir, "host.err")
        with open(os.path.join(out_dir, stdout_name), "w") as so, open(errp, "w") as se:
            p = subprocess.Popen(self.host_cmd(argv), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=self.env)

            def wrong(why):
                with self.lock:
                    self.stops.stop = self.stops.stop or f"identity: {why}"
            w = I.HostWatch(p.pid, errp, self.watch_dir, on_wrong=wrong)
            w.start()
            try:
                rc = p.wait(timeout=self.a.host_bound_s)
            except subprocess.TimeoutExpired:
                rc = None
                why = (f"BOUND: the host process (pid {p.pid}) outlived the runner's {self.a.host_bound_s:g} s bound: `timeout "
                       f"{C.HOST_TIMEOUT_S}` did not end it; nothing is killed; the queue stops")
                self.bound.append({"argv": argv, "pid": p.pid, "t0_ms": t0})
                self.bound_procs[p.pid] = p     # finding 4: its end is polled with card 1's lock kept (wait_bound)
                with self.lock:
                    self.stops.stop = self.stops.stop or why
                self.say(why)
            w.finish()
        t1 = now_ms()
        u1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = [round(u1.ru_utime - u0.ru_utime, 3), round(u1.ru_stime - u0.ru_stime, 3)]
        with open(os.path.join(out_dir, stdout_name)) as f:
            text = f.read()
        return rc, t0, t1, cpu, text, w.result()

    # ------------------------------------------------------------------ finding 4: after a BOUND, the lock is kept while that host lives
    def bound_alive(self):
        return [pid for pid, p in self.bound_procs.items() if p.poll() is None]

    def wait_bound(self, deadline):
        """After a BOUND: this process keeps card 1's lock (and the sampler keeps reading) while the host process past the runner's bound
        still runs, polling its end every BOUND_POLL_S (nothing is killed), until the end bound less the closing's share. Each BOUND record
        gains ended_ms (when it was seen ended) or alive_at_close; the closing config read runs only when none is alive."""
        if not self.bound_procs:
            return
        until = (deadline - C.CLOSE_CONFIG_S - 5) if deadline else time.time() + 600
        alive = self.bound_alive()
        if alive:
            self.say(f"after the BOUND: card 1's lock stays held while our host (pid {', '.join(map(str, alive))}) runs; its end is polled "
                     f"every {C.BOUND_POLL_S:g} s, nothing is killed, at most until {time.strftime('%H:%M:%S %Z', time.localtime(until))}")
        t = time.time()
        while self.bound_alive() and time.time() < until:
            time.sleep(C.BOUND_POLL_S)
        for b in self.bound:
            p = self.bound_procs.get(b["pid"])
            if p is not None and p.poll() is not None:
                b["ended_ms"] = b.get("ended_ms") or now_ms()
                b["rc"] = p.returncode
                self.say(f"the host past the bound (pid {b['pid']}) has ended (rc {p.returncode}, {time.time() - t:.0f} s into the wait); "
                         f"card 1's lock was held until then")
            elif p is not None:
                b["alive_at_close"] = True
                self.say(f"the host past the bound (pid {b['pid']}) still runs at the end bound less the closing's share: card 1's lock "
                         f"is released with it running and the closing config read is not run beside it; reported (nothing killed)")

    # ------------------------------------------------------------------ the identity read (note 1, item 3(b))
    def identity_read(self):
        try:
            r = subprocess.run(self.cmd_etwho(), cwd=ROOT, capture_output=True, text=True, timeout=30, env=self.env)
            lines = r.stdout.splitlines()
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"et-who unreadable ({type(e).__name__})"
        uw = I.etwho_unreadable(r.returncode, lines)    # finding 3
        if uw:
            self.identity["etwho_with_sampler"] = {"counts": {}, "why": uw}
            return uw
        why, counts = I.etwho_identity(lines, self.me)
        nodes = I.proc_nodes(self.sproc.pid, self.watch_dir) if self.sproc else set()
        swhy = I.sampler_identity(nodes)
        self.identity["etwho_with_sampler"] = {"counts": counts, "why": why}
        self.identity["sampler_nodes"] = {"nodes": sorted(f"/dev/et{c}_{k}" for c, k in nodes), "why": swhy}
        with open(os.path.join(self.out, "etwho-identity.txt"), "w") as f:
            f.write(f"et-who with the sampler running, before the smoke (counts by card; no login): {json.dumps(counts, sort_keys=True)}; "
                    f"{why or 'ok'}\nthe sampler's own nodes: {self.identity['sampler_nodes']['nodes']}; {swhy or 'ok'}\n")
        return "; ".join(x for x in (why, swhy) if x)

    # ------------------------------------------------------------------ the stop-path test (E189's)
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
                                                                  "clock_mhz": C.CLOCK_MHZ},
                       # fix-e191k2 (nit 3): an early stop asked for during the test cuts it (its "refused" readings are the stop's): not read
                       "early_stop": self.stop_req_why}, f, indent=1)
        return ok, res

    # ------------------------------------------------------------------ the smoke (E189's, with the watch)
    def smoke(self):
        self.identity["smoke"] = {}
        for name, argv, kind in C.smoke_runs(self.programs):
            why = self.may_start(30)
            if why:
                return False, f"{name}: not started ({why})"
            ok, die, waited, gwhy = self.die_gate()
            if not ok:
                return False, f"{name}: the die gate ({die} C after {waited:.0f} s{'; ' + gwhy if gwhy else ''})"
            if kind != "selftest" and not self.fresh():         # finding 2: a live sampler before every device-opening process
                return False, f"{name}: not started (the sampler is not live: {self.staleness()})"
            age = self.sample_age()
            d = os.path.join(self.out, "smoke", name)
            m0 = time.monotonic()
            rc, t0, t1, cpu, text, wres = self.run_host(argv, d, "stdout.txt")
            age1 = self.sample_age()                            # fix-e191k2 (nit 2): recorded beside the process (the gate's verdict unchanged)
            gap, n_live = self.live_gap(m0, time.monotonic())
            self.device_opened = self.device_opened or kind != "selftest"
            self.identity["smoke"][name] = wres
            j = C.last_json(text)
            if kind == "selftest":
                good = rc == 0 and "SELFTEST PASS" in text
            elif kind == "ledger":
                good = rc == 0 and j.get("status") == "PASS"
            else:
                good = rc == 0 and j.get("status") == "PASS" and (j.get("result") or {}).get("solved") is not False
            card = "no device (the self-test)" if kind == "selftest" else (
                "card 1" if (wres["right"] and not wres["wrong"]) else ("ANOTHER CARD: " + "; ".join(wres["wrong"]) if wres["wrong"]
                                                                      else "not seen (no PCIe target line, no node held)"))
            with open(os.path.join(d, "smoke.json"), "w") as f:
                json.dump({"name": name, "argv": argv, "rc": rc, "t0_ms": t0, "t1_ms": t1, "status": j.get("status"),
                           "good": good, "identity": wres, "sample_age_s_at_start": age,
                           "sample_age_s_at_end": age1, "live_gap_s": gap, "live_samples": n_live}, f, indent=1)
            self.say(f"smoke {name}: rc {rc}, {'ok' if good else 'FAILED'} ({(t1 - t0) / 1000:.1f} s); the host's card: {card}")
            if not good:
                return False, f"{name}: rc {rc}, status {j.get('status')}"
            if kind != "selftest" and (wres["wrong"] or not wres["right"]):
                return False, f"{name}: the host's card: {card}"
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
            with self.lock:
                self.stops.stop = self.stops.stop or f"a holder or a foreign device process: {f}"
            self.say(f"STOP before pass {idx}: {f}")
            return {"pass": key, "ran": False, "why": f}
        os.makedirs(d, exist_ok=True)
        t_start = now_ms()
        m_start = time.monotonic()              # fix-e191k2 (nit 2): the pass's own span, on the clock the freshness ages are read on
        with self.lock:
            self.in_pass = key
        self.say(f"pass {idx}: {cfg} p{k} (K {K}; die {die} C{'; below the forecast band' if die is not None and die < C.DIE_LOW_C else ''})")
        clean = self.nap(self.a.idle_before)
        if not clean:
            with self.lock:
                self.in_pass = None
            self.say(f"pass {idx}: a stop tripped in its idle before: no host process started")
            return {"pass": key, "ran": False, "why": "stop: " + str(self.stops.stop)}
        if not self.fresh():                    # finding 2: a live sampler just before the host process, else no host (no data)
            with self.lock:
                self.in_pass = None
            st = self.staleness()
            self.say(f"pass {idx}: {cfg} p{k}: the sampler is not live just before its host process ({st}): no host process started, "
                     f"no data; the sampler is restarted before the next pass")
            return {"pass": key, "ran": False, "why": f"the sampler was not live before the host process ({st})"}
        age = self.sample_age()
        rapl, r0 = self.rapl()
        argv = C.host_argv(cfg, p, d)
        m_h0 = time.monotonic()
        rc, h0, h1, cpu, text, wres = self.run_host(argv, d, "host-raw.json" if C.PROGRAM[cfg] == "ledger" else "host.json")
        m_h1 = time.monotonic()
        age_h1 = self.sample_age()              # fix-e191k2 (nit 2): the last live sample's age at the host's end
        self.device_opened = True
        _, r1 = self.rapl()
        self.idle(self.a.idle_after)          # whole, even after a stop: the host ran, so its pass keeps its after window (E189's fault 2)
        t_end = now_ms()
        m_end = time.monotonic()
        age_end = self.sample_age()             # ... at the pass's end
        gap_host, n_live_host = self.live_gap(m_h0, m_h1)
        gap_pass, n_live_pass = self.live_gap(m_start, m_end)
        sampler_live = gap_pass < C.SAMPLE_FRESH_S
        with self.lock:
            self.in_pass = None
            sl = [ln for (t, ln) in self.samples if t_start - 1000 <= t <= t_end + 500]
            if wres["wrong"] and key not in self.set_aside:
                self.set_aside[key] = "identity: the host named or held another card (" + "; ".join(wres["wrong"]) + ")"
        with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as g:
            for ln in sl:
                g.write(ln + "\n")
        j = C.last_json(text)
        hj = j
        if C.PROGRAM[cfg] == "ledger":
            with open(os.path.join(d, "host-raw.json"), "w") as fo:
                fo.write((json.dumps(j) if j else "") + "\n")
            hj = C.adapt_ledger(j, K)
            with open(os.path.join(d, "host.json"), "w") as fo:
                fo.write(json.dumps(hj) + "\n")
        flags = []
        if self.stops.stop:
            flags.append(f"a stop line tripped during this pass: {self.stops.stop}")
        if die is not None and die < C.DIE_LOW_C:
            flags.append(f"T0 below the forecast band ({die} C < {C.DIE_LOW_C} C)")
        if not wres["right"] and not wres["wrong"]:
            flags.append("the host's card was not seen (no PCIe target line on its stderr, no card node held)")
        if rc is None:
            flags.append(f"BOUND: the host outlived the runner's {self.a.host_bound_s:g} s bound (nothing killed)")
        if not sampler_live:                    # fix-e191k2 (nit 2): a flag only; the scoring stays as registered
            flags.append(f"the sampler was not live during this pass: no live sample for {gap_pass:.2f} s between its start and its end "
                         f"({gap_host:.2f} s in the host's span, {n_live_host} live sample(s) in it): the live stop lines read nothing then "
                         f"(reported; the scoring stays as registered)")
            self.not_live_passes.append(key)
        run = {"preset": cfg, "card": "aifoundry1 card 1", "et_devices": self.env.get("ET_DEVICES"), "dry": self.dry,
               "lock": C.LOCK if not self.dry else "DRY",
               "build": os.path.dirname(os.path.dirname(argv[0])), "host_args": " ".join(argv[1:]), "reps_planned": K,
               "idle_before_s": self.a.idle_before, "idle_after_s": self.a.idle_after, "every_ms": C.EVERY_MS,
               "sampler": " ".join(self.real_sampler(C.CAP_S + 1200)), "sampler_t0_ms": self.sampler_t0, "host_t0_ms": h0,
               "host_t1_ms": h1, "end_ms": t_end, "host_rc": rc, "foreign": None, "rapl": rapl, "rapl_uj": [r0, r1],
               "host_cpu_ext_s": cpu, "identity": wres, "stub_card": self.a.double if self.dry else None,
               "sample_age_s_at_host_start": age,
               # fix-e191k2 (verify-e191k2's nit 2): the sampler during the pass (the last live sample's age at three moments; the
               # longest stretch with no live sample in the host's span and in the whole pass; the live samples in each)
               "sample_age_s_at_host_end": age_h1, "sample_age_s_at_pass_end": age_end,
               "live_gap_s_host": gap_host, "live_samples_host": n_live_host, "live_gap_s_pass": gap_pass,
               "live_samples_pass": n_live_pass, "sampler_live_during_pass": sampler_live}
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(run, fo, indent=1)
        with self.lock:
            sa = self.set_aside.get(key)
        rd = C.reading(cfg, hj) if rc is not None else "BOUND (no reading: the host did not end)"
        with open(os.path.join(d, "pass.json"), "w") as fo:
            json.dump({"config": cfg, "pass": k, "order_index": idx, "launches_requested": K, "set_aside": sa,
                       "die_start_c": die, "die_gate_wait_s": round(waited, 1), "flags": flags, "sampler_live": sampler_live,
                       "t_start_ms": t_start,
                       "t_end_ms": t_end, "host_rc": rc, "host_status": j.get("status"), "reading": rd, "dry": self.dry}, fo, indent=1)
        self.say(f"pass {idx}: {cfg} p{k} done: host rc {rc}, status {j.get('status')}, reading {rd}"
                 f"{', SET ASIDE: ' + sa if sa else ''}{', ' + '; '.join(flags) if flags else ''}")
        return {"pass": key, "ran": True, "rc": rc, "status": j.get("status"), "reading": rd, "set_aside": sa}

    # ------------------------------------------------------------------ the dry check (note 1, item 4)
    def dry_check(self):
        """Every device-opening command the real path would run: ET_DEVICES=1, nothing of card 0, no unset, no dev_mngt_service or
        et-powertop; the real lock is card 1's. ('' or why, n)."""
        bad, n = [], 0
        try:
            rows = [json.loads(ln) for ln in open(os.path.join(self.out, "commands.jsonl")) if ln.strip()]
        except (OSError, ValueError) as e:
            return f"commands.jsonl unreadable ({type(e).__name__})", 0
        for r in rows:
            words = " ".join(r.get("real") or [])
            if any(x in words for x in FORBIDDEN) or "unset" in words.split():
                bad.append(f"{r.get('kind')}: '{words[:80]}' names a forbidden word")
            if r.get("lock") != "/run/lock/etsoc-shire1.lock":
                bad.append(f"the real lock is {r.get('lock')}")
            if r.get("opens_device"):
                n += 1
                if r.get("et_devices") != "1":
                    bad.append(f"{r.get('kind')}: ET_DEVICES {r.get('et_devices')!r}, not '1'")
        if n == 0:
            bad.append("no device-opening command recorded")
        return "; ".join(sorted(set(bad))[:6]), n

    # ------------------------------------------------------------------ the whole session
    def run(self):
        a = self.a
        tag = " DRY" if self.dry else ""
        self.say(f"session start (T0 {a.t0} = {time.strftime('%H:%M:%S %Z', time.localtime(a.t0))}; plan FULL; programs "
                 f"{'+'.join(self.programs) or 'none'}; aifoundry1 card 1, ET_DEVICES=1; its files in {a.out}){tag}")
        lockf = None
        result = {"t0": a.t0, "dry": self.dry, "programs": self.programs, "queue": self.queue, "card": "aifoundry1 card 1"}
        prev_term = signal.signal(signal.SIGTERM, self.on_sigterm)     # finding 5: SIGTERM asks for the early stop; finally still runs
        try:
            if not self.programs:
                self.say("no program was built today: no device opened")
                return 16
            if not self.dry:
                why = self.box_check()
                if why:
                    self.say(f"the box check: {why}: no device opened")
                    return 16
                self.say("the box check: aifoundry1, ET_DEVICES=1, the reader at its pin, today's builds by build_e191.sh with the ET_DEVICES reading passed, "
                         "each host and kernel at its build record's sha256 with the kernel gate's OK")
            lockp = os.path.join(self.out, "dry.lock") if self.dry else C.LOCK
            try:
                lockf = open(lockp, "a+")
            except OSError as e:
                self.say(f"card 1's lock cannot be opened ({type(e).__name__}): no device opened")
                return 16
            try:
                fcntl.flock(lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.say("card 1's lock is held: no device opened")
                return 16
            f = self.foreign()
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((f or "no holder of another login; nothing of ours on card 0 or card 1's ops node; no device process of "
                              "another user or of ours") + "\n")
            if f:
                self.say(f"a holder or a foreign device process ({f}): no device opened")
                return 16
            if self.stop_requested():           # finding 5: an early stop asked for before the first card command
                self.say(f"{self.stop_req_why} before the first card command: no device opened")
                return 16
            self.t_first = time.time()
            cfg0, err0, why = self.config("start")
            self.device_opened = True
            idw = I.config_identity(cfg0 or {}, err0) if cfg0 else "no config read"
            targets, ids = I.parse_ident(err0)
            self.identity["config_start"] = {"targets": sorted({f"/dev/et{c}_{k}" for c, k in targets}), "ids": sorted(set(ids)),
                                             "minion_mv": (cfg0 or {}).get("minion_mv"), "why": idw}
            if not cfg0 or not C.config_ok(cfg0):
                self.say(f"config start: {why or json.dumps(cfg0)}: not TDP 65 W / 65 C / 600 MHz: the gate, no launch")
                return 16
            if idw:
                self.say(f"config start: {json.dumps(cfg0)}: IDENTITY GATE FAILED: {idw}: the gate, no launch")
                return 16
            self.say(f"config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv {cfg0.get('minion_mv')} (read, nothing set); "
                     f"identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510")
            if not self.start_sampler():
                self.say("the sampler would not start: no launch")
                return 16
            self.sampler_t0 = self.samples[0][0] if self.samples else now_ms()
            why = self.identity_read()
            if why:
                self.say(f"identity (b): IDENTITY GATE FAILED: {why}: the gate, no launch")
                return 16
            c = self.identity["etwho_with_sampler"]["counts"]
            self.say(f"identity (b): et-who with the sampler running: ours on card 1 {c['ours_on_card1']} (on /dev/et1_mgmt "
                     f"{c['ours_on_mgmt']}), ours on card 0 0, another login's 0; the sampler holds /dev/et1_mgmt only")
            if self.stop_requested():           # fix-e191k2 (nit 3): an early stop asked for after the start config read, before the test
                self.say(f"{self.stop_req_why} before the stop-path test: the gate, no launch")
                return 16
            ok, res = self.stop_path_test()
            if self.stop_req_why:               # ... or during it: the test is cut, its lines are not read (never "stop-path test failed")
                self.say(f"{self.stop_req_why} during the stop-path test (its lines not read): the gate, no launch")
                return 16
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
            elif a.sequence == "short":
                seq = [("anchor", 1)] + [("pass", c2, 1, i + 1) for i, c2 in enumerate(C.ORDER)] + [("anchor", 3)]
            else:
                seq = [("anchor", 1)] + [("pass", c2, k, 0) for k in (1, 2) for c2 in ("copy-zeros", "sha256", "sparse-parity")]
            anchors = []
            for it in seq:
                if self.stops.stop or self.stop_requested():        # finding 5: the stop file or a SIGTERM ends the queue here
                    break
                if it[0] == "anchor":
                    anchors.append(self.anchor(it[1]))
                    continue
                _, cfg, k, idx = it
                if C.PROGRAM[cfg] not in self.programs:
                    self.queue.append({"pass": f"{cfg}/p{k}", "ran": False, "why": "SKIPPED: its program was not built today"})
                    continue
                self.queue.append(self.one_pass(cfg, k, idx))
                if not self.fresh() and not self.may_start(60) and not self.ensure_fresh_sampler():     # finding 2: live, or restarted
                    with self.lock:
                        self.stops.stop = self.stops.stop or "the sampler would not restart"
            with open(os.path.join(self.out, "anchors.json"), "w") as fo:
                json.dump(anchors, fo, indent=1)
            self.say("the counters arm: DROPPED by E189's kit (its KIT.md section 5; E191.md 7): not run")
            if self.stops.stop:
                self.say(f"STOP: {self.stops.stop}: the queue ended after the running process")
            return 0
        finally:
            dl = self.close_deadline()
            self.wait_bound(dl)                 # finding 4: the lock stays held (and the sampler reads) while a host past the bound runs
            self.stop_sampler(dl)
            if self.device_opened and self.bound_alive():
                self.identity["config_end"] = {"why": "not run: a host of ours past the runner's bound still ran"}
                self.say(f"config end: NOT RUN: our host past the runner's bound (pid {', '.join(map(str, self.bound_alive()))}) still runs; "
                         f"nothing starts beside it (nothing killed)")
            elif self.device_opened:
                cfg1, err1, why = self.config("end", max(12.0, min(30.0, dl - time.time())) if dl else 30)
                t1, i1 = I.parse_ident(err1)
                self.identity["config_end"] = {"targets": sorted({f"/dev/et{c}_{k}" for c, k in t1}), "ids": sorted(set(i1)),
                                               "minion_mv": (cfg1 or {}).get("minion_mv"),
                                               "why": I.config_identity(cfg1 or {}, err1) if cfg1 else "no config read"}
                self.say("config end: " + (f"TDP {cfg1.get('tdp_w')} W, threshold {cfg1.get('temp_threshold_c')} C, minion "
                                           f"{cfg1.get('minion_mhz')} MHz, minion_mv {cfg1.get('minion_mv')}; its identity "
                                           f"{'card 1' if not self.identity['config_end']['why'] else 'NOT card 1: ' + self.identity['config_end']['why']}"
                                           if cfg1 else why))
            self.tel.close()
            if os.path.exists(os.path.join(self.out, "telemetry.jsonl")):
                with open(os.path.join(self.out, "telemetry.jsonl"), "rb") as fi, \
                        gzip.open(os.path.join(self.out, "telemetry.jsonl.gz"), "wb") as fo:
                    fo.write(fi.read())
                os.remove(os.path.join(self.out, "telemetry.jsonl"))
            with open(os.path.join(self.out, "identity.json"), "w") as fo:
                json.dump(self.identity, fo, indent=1, sort_keys=True)
            self.cmd_log.close()
            if self.dry and self.device_opened:
                why, n = self.dry_check()
                self.say(f"the device-command check: {n} device-opening command(s), " + (
                    "each with ET_DEVICES=1; none names card 0, unsets ET_DEVICES or calls dev_mngt_service or et-powertop; the lock "
                    "card 1's: ok" if not why else f"FAILED: {why}"))
                result["dry_check"] = {"ok": not why, "n": n, "why": why}
            result.update({"stop": self.stops.stop, "off_clock": self.stops.events, "set_aside": self.set_aside,
                           "bound": self.bound, "identity_ok": not any(
                               (v or {}).get("why") for k2, v in self.identity.items() if k2 in ("config_start", "etwho_with_sampler", "sampler_nodes")),
                           "t_first_ms": int(self.t_first * 1000) if self.t_first else None, "t_close_ms": now_ms(),
                           "end_bound_ms": int(self.close_deadline() * 1000) if self.t_first else None,
                           "early_stop": self.stop_req_why,                                   # finding 5
                           "lock_released_with_bound_host_alive": bool(self.bound_alive()),   # finding 4
                           "sampler_lines_not_live": self.n_not_live,                         # fix-e191k2 (nit 1)
                           "passes_sampler_not_live": self.not_live_passes})                  # fix-e191k2 (nit 2)
            with open(os.path.join(self.out, "queue.json"), "w") as fo:
                json.dump(result, fo, indent=1)
            self.say(f"session end (T0 {a.t0})")
            self.log_f.close()
            if lockf:
                lockf.close()
            write_manifest(self.out)
            signal.signal(signal.SIGTERM, prev_term)


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
    ap.add_argument("--host-bound-s", type=float, default=C.HOST_BOUND_S)
    a = ap.parse_args(argv)
    if not a.dry:
        changed = [n for n, v in (("--idle-before", a.idle_before != C.IDLE_BEFORE_S), ("--idle-after", a.idle_after != C.IDLE_AFTER_S),
                                  ("--anchor-s", a.anchor_s != C.ANCHOR_S), ("--die-wait-s", a.die_wait_s != C.DIE_GATE_WAIT_S),
                                  ("--cap-pass-s", a.cap_pass_s != C.CAP_PASS_START_S), ("--cap-end-s", a.cap_end_s != C.CAP_S),
                                  ("--host-bound-s", a.host_bound_s != C.HOST_BOUND_S), ("--sequence", a.sequence != "plan")) if v]
        if changed:
            print(f"refused: {', '.join(changed)} change the registered session and are read with --dry only")
            return 2
        if os.environ.get("V3_DRY"):
            print("refused: V3_DRY is set but --dry is not")
            return 2
    s = Session(a)
    return s.run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
