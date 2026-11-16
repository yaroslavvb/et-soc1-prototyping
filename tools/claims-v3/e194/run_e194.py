#!/usr/bin/env python3
"""E194's runner (Q183, the kit, Sun 15 Nov 2026, written after E194's registration 0d8e3de0 and before any E194 datum): the blind day's
whole session on aifoundry2's own card 0, under its governor as found, in energy.sh's form, with the live stops. It is E191's runner
(tools/claims-v3/e191/run_e191.py, eb1ac923, unchanged beside it: E189's runner with E191's dated note 1 and both of its verifiers' fixes,
fix-e191k and fix-e191k2) ported back to a card on the orchestrating box, with E194's registered changes and the parser lesson of E191's
stop record (1a4bc1e3). Python's own modules only (/usr/bin/python3 3.12.3 on aifoundry2). session_e194.sh starts it, detached.

    python3 -B tools/claims-v3/e194/run_e194.py session --t0 T0 --out build/e194/T<T0> --programs ledger,spp
        [--deadline-epoch E] [--rapl-allowed]
    python3 -B tools/claims-v3/e194/run_e194.py session --dry --double alt|base|inject --t0 T0 --out DIR [--sequence plan|short|e2e]
        [--idle-before S --idle-after S --anchor-s S --die-wait-s S --cap-pass-s S --cap-end-s S --host-bound-s S --climb-s S]  (--dry only)

What changes from E191's runner (KIT.md section 1 names each):
  - THE CARD: aifoundry2 card 0, the box's only card; every process the runner starts runs with ET_DEVICES and V3_DEVICE UNSET (E190 arm
    A's form on this card: aifoundry2's device layer carries no ET_DEVICES, and its guard refused any setting); card 0's lock
    /run/lock/etsoc-shire0.lock, flock -n, held to the end; the reader build/ettelem-hpl/ettelem at its pin, through E194's guard, which
    refuses any box but aifoundry2 and any ET_DEVICES setting;
  - THE BOX CHECK (real path): the host is aifoundry2, ET_DEVICES and V3_DEVICE unset, the reader at its pin, each program's build record
    written today on aifoundry2 by build_e194.sh with the host and kernel at its sha256 and the kernel gate's OK line;
  - THE IDENTITY GATE (e194_ident.py): (a) the start config read's stderr names /dev/et0_mgmt and device ID 0 alone, minion_mv a number
    between 450 and 600, and its JSON TDP 65 W, threshold 65 C, minion 600 MHz at rest (E194.md 2); (b) with the sampler running and
    before the smoke, et-who's lines of ours on card 0 only, one on /dev/et0_mgmt, nothing of another login, and the sampler's own fds
    holding /dev/et0_mgmt and no other card's node; either failing: the gate, no launch; THE WATCH at every launch (another card named or
    held stops the session after that process; in the smoke each device-opening process must have shown card 0);
  - THE STOP LINES (E194.md 11): E189's 65 W / 70 C first, then aifoundry2's own kept beside them (board above 85 W on 3 samples in a row;
    minshire[0] or the latch minshire[2] at or above 80 C); E189's per-sample clock line is gone (at 800 MHz under load and 600 MHz at
    rest it would trip in every pass), and the stop-path test trips each of the four lines and reads THE CLOCK RULE on live samples;
  - THE CLOCK RULE, live (E194.md 11): after each pass's host process, its live samples from the burst's first launch's start + 1.5 s to
    its last launch's end (the host's own launch_epoch_ms) must read 800 MHz; the first pass with one off it is SET ASIDE ("the clock:
    ..."), a second such pass, in any configuration, stops the session (the card is not at the forecast's clock); a window with no live
    sample is flagged (the scorer's rule reads the pass's telemetry, which the pass keeps);
  - THE DIE GATE at 57 C (E194.md 11; a die below 46 C does not block, the pass is labelled);
  - THE HOST'S LINE (E191's stop record 1a4bc1e3; CONTEXT section 116's lesson): every host's and the reader's JSON is read from its WHOLE
    stdout by e194_common.host_json, which reassembles an object a runtime print split and records each dropped span (run.json and
    smoke.json "host_line"; the session log names them); each host's raw stdout is kept beside it (host-stdout.txt in a pass,
    stdout.txt in the smoke), and host-raw.json / host.json hold the object as read;
  - THE HOLDER RULE AT THE START, re-read (kit mechanics, KIT.md section 4): with card 0's lock held (so our own live collector, which reads
    the card only while `et-who --check` finds nothing held, starts no new read), a refusal whose every reason is a device process of
    ours besides the sampler or a line of ours on /dev/et0_mgmt is read again, at most HOLDER_REREAD_N times HOLDER_REREAD_S apart, and the
    first card command comes only after a clear read; any other reason refuses at once, and before each pass the rule is E191's, unchanged;
  - THE DRY CHECK (E191's item 4, for this box): every device-opening command the real path would run carries no ET_DEVICES and no
    V3_DEVICE; none names etsoc-shire1, /dev/et1_, an ET_DEVICES= or V3_DEVICE= setting, dev_mngt_service or et-powertop; the real lock
    is card 0's.
fix-e194 (Q183, after E194's verifier, before any E194 datum; kit mechanics, KIT.md section 11): every host's line and the config read are
read by e194_common.host_result (the last object with the host's key, no foreign newline inside it, every dropped span a whole known
runtime line, the line checked against its own command line: else 'none', a FAILED RUN or a failed gate; verify-e194's finding 2); the
box check reads ET_DEVICES and V3_DEVICE in the runner's own environment (nit 5); the sampler's reader thread survives a line of any shape,
counting it not live (nit 7). session_e194.sh writes runner.rc after the runner exits, and step 10 reads it (finding 3).
Everything else is E191's, unchanged: THE 30 s BOUND (nothing killed, the queue stops, the lock kept while that host lives), THE SAMPLER'S
FRESHNESS and a LIVE sample, the per-pass sampler flag, ET-WHO UNREADABLE, THE EARLY STOP (the stop file or a SIGTERM to the runner), an
early stop at the gate, our device processes by comm and executable, the box check reading the kernels, the pass's reading in words, the
sequence (plan-e194.json, never re-drawn), the ramped smoke, the anchors, the cap (108 / 110 card-minutes from the first card command),
the end bound, ONE sampler, the pass's files (E194.md 8.1), the closing, MANIFEST.sha256 last. The counters arm is DROPPED (E194.md 7).
Every device command is a READ (dmcmd_audit GO). --dry swaps every device-opening process for fake_card_e194.py's doubles, takes a lock
file in the output directory, and marks every line DRY (the rest rule skips it). SPDX-License-Identifier: Apache-2.0
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
import e194_common as C  # noqa: E402
import e194_ident as I  # noqa: E402

ROOT = C.REPO
DEV_COMM = re.compile(r"_ho(st)?$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner\.Worker$")   # nit 6: _ho(st)?
RAPL_F = "/sys/class/powercap/intel-rapl:0/energy_uj"
FORBIDDEN = ("etsoc-shire1", "/dev/et1_", "ET_DEVICES=", "V3_DEVICE=", "dev_mngt_service", "et-powertop")


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
        self.env = C.device_env()                       # ET_DEVICES and V3_DEVICE UNSET for every process (E190 arm A's form)
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
        self.live_clock = []                            # E194: every LIVE sample's (t_ms, minion MHz), in order (THE CLOCK RULE reads it)
        self.off_clock_passes = []                      # E194: the passes THE CLOCK RULE set aside (a second one stops the session)
        self.unread_clock_passes = []                   # E194: the passes whose clock window held no live sample (flagged)
        self.holder_reads = []                          # E194: the holder rule's reads at the start, with the lock held (KIT.md 4)
        self.n_reader_errors = 0                        # fix-e194 (nit 7): sampler lines whose reading raised (counted, never fatal)
        self.reader_errors = []                         # ... the first three, in words
        self.dev_dir = None
        if self.dry:
            self.env["E194_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            open(self.env["E194_FAKE_SCHED"], "a").close()
            self.dev_dir = os.path.abspath(os.path.join(self.out, "dev"))   # the doubles' stand-in nodes (et0_mgmt, et0_ops)
            os.makedirs(self.dev_dir, exist_ok=True)
            self.env["E194_FAKE_DEVDIR"] = self.dev_dir
            self.env["E194_FAKE_LOCK"] = os.path.abspath(os.path.join(self.out, "dry.lock"))
            if a.double in ("alt", "base"):
                self.env["E194_FAKE_BASE"] = a.double
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
                                       "et_devices": self.env.get("ET_DEVICES"), "v3_device": self.env.get("V3_DEVICE"),
                                       "opens_device": opens_device,
                                       "lock": C.LOCK}) + "\n")
        self.cmd_log.flush()

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def fake(self):
        return [sys.executable, "-B", os.path.join(HERE, "fake_card_e194.py")]

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
        """'' when the box, the reader and today's builds are E194's (the module docstring); else why. Never in --dry."""
        why = []
        host = socket.gethostname().split(".")[0]
        if host != C.BOX:
            why.append(f"this host is {host!r}, not {C.BOX}")
        if "ET_DEVICES" in os.environ or "V3_DEVICE" in os.environ:     # fix-e194 (verify-e194's nit 5): the runner's own environment
            why.append("ET_DEVICES or V3_DEVICE is set in the session's environment (aifoundry2's one card is opened with both unset)")
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
            if rec.get("builder") != "build_e194.sh" or rec.get("verdict") != "BUILT" or rec.get("day") != day:
                why.append(f"{prog}'s build record is not build_e194.sh's BUILT of today ({rec.get('builder')}, {rec.get('verdict')}, {rec.get('day')})")
            elif not os.path.exists(host_p) or sha256(host_p) != rec.get("host_sha256"):
                why.append(f"{prog}'s host is not the one its build record names")
            elif not os.path.exists(elf_p) or sha256(elf_p) != rec.get("kernel_sha256"):      # fix-e191k2 (verify-e191k2's nit 5)
                why.append(f"{prog}'s kernel is not the one its build record names (THE KERNEL GATE passed that one at the build)")
            elif not str(rec.get("kernel_gate") or "").startswith(f"KERNEL OK {prog}: "):
                why.append(f"{prog}'s build record carries no passing kernel gate line ({str(rec.get('kernel_gate'))[:60]!r})")
            elif rec.get("box") != C.BOX:
                why.append(f"{prog}'s build record was not made on {C.BOX} ({rec.get('box')})")
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

    def foreign_read(self):
        """et-who's lines (e194_ident.foreign_lines: another login's anywhere, ours off card 0, ours on /dev/et0_ops while no host of ours
        runs, ours on /dev/et0_mgmt while no sampler of ours runs), other users' device processes (energy.sh's foreign()) and our own
        device processes but the sampler; counts, never names. Returns (why, transient): transient is True when every reason is a device
        process of ours besides the sampler or a line of ours on /dev/et0_mgmt (a stray reader, such as our live collector's read in
        flight), which the start re-reads with the lock held (KIT.md section 4); False for anything else."""
        try:
            w = subprocess.run(self.cmd_etwho(), cwd=ROOT, capture_output=True, text=True, timeout=30, env=self.env)
            lines = w.stdout.splitlines()
            rc = w.returncode
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"et-who unreadable ({type(e).__name__})", False
        uw = I.etwho_unreadable(rc, lines)          # finding 3: rc not 0, or neither a holder line nor the no-holder sentence
        if uw:
            return uw, False
        why, _, transient = I.foreign_lines(lines, self.me, sampler_running=self.sampler_alive())
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
        trans = bool(parts) and not n and (transient or not why)
        return "; ".join(parts), trans

    def foreign(self):
        return self.foreign_read()[0]

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
            try:                                    # fix-e194 (verify-e194's nit 7): a line of any shape never ends this thread
                self._read_line(s, raw)
            except Exception as e:                  # noqa: BLE001 - counted as not live, and the reader goes on
                with self.lock:
                    self.n_not_live += 1
                    self.n_not_live_since += 1
                    self.n_reader_errors += 1
                    if self.n_reader_errors <= 3:
                        self.reader_errors.append(f"{type(e).__name__}: {str(e)[:80]}")
        self.tel.flush()

    def _read_line(self, s, raw):
        """One sampler line (a dict): kept, read for liveness, fed to THE STOP LINES. fix-e194 (nit 7): a t_ms that is not a number makes
        the line not live and keeps it out of every pass's window (t 0), so no comparison downstream can meet a string."""
        t = s.get("t_ms", 0)
        t = t if C._num(t) else 0
        live = C.sample_live(s) and t > 0       # fix-e191k2 (nit 1): live only with every stop line's reading (board_w, minshire[0], clock)
        with self.lock:
            self.samples.append((t, raw.rstrip("\n")))
            if live:
                self.last = s                   # the die gate reads the last LIVE sample
                self.last_rx = time.monotonic()     # finding 2: when the last live sample ARRIVED (monotonic: fix-e191k2)
                self.rx_mono.append(self.last_rx)
                self.n_not_live_since = 0
                self.live_clock.append((t, s["mhz"]["minion"]))     # E194: THE CLOCK RULE reads these, per pass
            else:
                self.n_not_live += 1
                self.n_not_live_since += 1
            self.stops.feed(s, self.in_pass)    # E194.md 11's lines (no per-sample clock line: THE CLOCK RULE is per pass)
            if self.test_stops is not None:
                self.test_stops.feed(s, "the stop-path test")

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
        """The sampler is live: its process alive and a LIVE sample (e194_common.sample_live) received less than SAMPLE_FRESH_S ago."""
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
        j, prec = C.host_result(r.stdout, "config")         # E194: read from the whole stdout; fix-e194: verified (host_result)
        self.identity.setdefault("config_parse", {})[name] = prec
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
        """ONE host process under `timeout 10`, watched (e194_ident.HostWatch). The runner's own bound is HOST_BOUND_S (30 s): when it
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
                self.bound_procs[p.pid] = p     # finding 4: its end is polled with card 0's lock kept (wait_bound)
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
        """After a BOUND: this process keeps card 0's lock (and the sampler keeps reading) while the host process past the runner's bound
        still runs, polling its end every BOUND_POLL_S (nothing is killed), until the end bound less the closing's share. Each BOUND record
        gains ended_ms (when it was seen ended) or alive_at_close; the closing config read runs only when none is alive."""
        if not self.bound_procs:
            return
        until = (deadline - C.CLOSE_CONFIG_S - 5) if deadline else time.time() + 600
        alive = self.bound_alive()
        if alive:
            self.say(f"after the BOUND: card 0's lock stays held while our host (pid {', '.join(map(str, alive))}) runs; its end is polled "
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
                         f"card 0's lock was held until then")
            elif p is not None:
                b["alive_at_close"] = True
                self.say(f"the host past the bound (pid {b['pid']}) still runs at the end bound less the closing's share: card 0's lock "
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
        """E189's stop-path test on E194's four live lines (E194.md 11), each at a test threshold every live sample crosses, the other
        lines out of reach: E189's board and die lines, aifoundry2's board line (above -1 W on 3 samples in a row) and its 80 C line (on
        minshire[0] or the latch minshire[2], at 0 C); each must trip and refuse a start. Then THE CLOCK RULE is read on the live samples of
        the last 3 s as if they were a burst's window (the card at rest: its idle point, 600 MHz): the rule must read them (verdict 'off'
        at rest, or 'ok'); a rule that reads nothing ('unread') fails the test. Nothing here touches the card."""
        res = {}
        far = {"board_w": 1e9, "die_c": 1e9, "a2_board_w": 1e9, "a2_die_c": 1e9}
        for line, kw in (("board", dict(far, board_w=0.0)), ("die", dict(far, die_c=0.0)),
                         ("board-85x3", dict(far, a2_board_w=-1.0)), ("die-80-or-latch", dict(far, a2_die_c=0.0))):
            self.test_stops = C.Stops(**kw)
            t = time.time()
            while time.time() - t < 5 and not self.test_stops.stop:
                time.sleep(0.1)
            tripped = bool(self.test_stops.stop)
            refused = bool(self.may_start(0))
            res[line] = {"tripped": tripped, "why": self.test_stops.stop, "refused_a_start": refused,
                         "s": round(time.time() - t, 2)}
            self.test_stops = None
        now = now_ms()
        with self.lock:
            lc = list(self.live_clock)
        v, words, n = C.clock_pass(lc, now - 3000, now, climb_s=0.0)
        clock = {"verdict": v, "words": words, "n": n, "read": v in ("off", "ok")}
        ok = all(x["tripped"] and x["refused_a_start"] for x in res.values()) and clock["read"] and not self.stops.stop
        with open(os.path.join(self.out, "stop-path.json"), "w") as f:
            json.dump({"ok": ok, "lines": res, "clock_rule": clock,
                       "real_thresholds": {"board_w": C.STOP_BOARD_W, "minshire0_c": C.STOP_DIE_C, "a2_board_w_above": C.A2_BOARD_W,
                                           "a2_board_n": C.A2_BOARD_N, "a2_die_c": C.A2_DIE_C, "clock_mhz": C.CLOCK_MHZ,
                                           "climb_s": self.a.climb_s},
                       # fix-e191k2 (nit 3): an early stop asked for during the test cuts it (its "refused" readings are the stop's): not read
                       "early_stop": self.stop_req_why}, f, indent=1)
        res["clock-rule"] = {"tripped": clock["read"], "refused_a_start": clock["read"], "s": 0.0, "why": words}
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
            if kind == "selftest":
                j, prec = {}, {"method": "the self-test's lines (no JSON)", "dropped": [], "runtime": []}
                good = rc == 0 and "SELFTEST PASS" in text
            else:                                               # E194: the host's line read from its whole stdout; fix-e194: verified
                j, prec = C.host_result(text, kind, argv)       # against this command's line (host_result; verify-e194's finding 2)
                if kind == "ledger":
                    good = rc == 0 and j.get("status") == "PASS"
                else:
                    good = rc == 0 and j.get("status") == "PASS" and (j.get("result") or {}).get("solved") is not False
            card = "no device (the self-test)" if kind == "selftest" else (
                "card 0" if (wres["right"] and not wres["wrong"]) else ("ANOTHER CARD: " + "; ".join(wres["wrong"]) if wres["wrong"]
                                                                      else "not seen (no PCIe target line, no node held)"))
            with open(os.path.join(d, "smoke.json"), "w") as f:
                json.dump({"name": name, "argv": argv, "rc": rc, "t0_ms": t0, "t1_ms": t1, "status": j.get("status"),
                           "good": good, "identity": wres, "host_line": prec, "sample_age_s_at_start": age,
                           "sample_age_s_at_end": age1, "live_gap_s": gap, "live_samples": n_live}, f, indent=1)
            pw = C.host_json_words(prec) if kind != "selftest" else ""
            self.say(f"smoke {name}: rc {rc}, {'ok' if good else 'FAILED'} ({(t1 - t0) / 1000:.1f} s); the host's card: {card}"
                     f"{'; ' + pw if pw else ''}")
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
        rc, h0, h1, cpu, text, wres = self.run_host(argv, d, "host-stdout.txt")     # E194: the host's raw stdout kept as it came
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
        j, prec = C.host_result(text, C.PROGRAM[cfg], argv)     # E194: the host's line, whole stdout; fix-e194: verified (finding 2)
        hj = j
        if C.PROGRAM[cfg] == "ledger":
            with open(os.path.join(d, "host-raw.json"), "w") as fo:
                fo.write((json.dumps(j) if j else "") + "\n")
            hj = C.adapt_ledger(j, K)
            with open(os.path.join(d, "host.json"), "w") as fo:
                fo.write(json.dumps(hj) + "\n")
        else:
            with open(os.path.join(d, "host.json"), "w") as fo:
                fo.write((json.dumps(j) if j else "") + "\n")
        # E194: THE CLOCK RULE, live (E194.md 11), on the burst's own window (its first launch's start, its last launch's end)
        win = C.burst_window(hj) if rc is not None else None
        if win:
            with self.lock:
                lc = [x for x in self.live_clock if win[0] - 1000 <= x[0] <= win[1] + 1000]
            cv, cwords, cn = C.clock_pass(lc, win[0], win[1], self.a.climb_s)
        else:
            cv, cwords, cn = "unread", "the clock: no burst window in the host's line (no launch read)", 0
        clock = {"verdict": cv, "words": cwords, "n": cn, "lo_ms": win[0] if win else None, "hi_ms": win[1] if win else None,
                 "climb_s": self.a.climb_s, "clock_mhz": C.CLOCK_MHZ}
        flags = []
        if cv == "off":
            self.off_clock_passes.append(key)
            with self.lock:
                if key not in self.set_aside:
                    self.set_aside[key] = cwords
                if len(self.off_clock_passes) >= 2 and not self.stops.stop:
                    self.stops.stop = (f"a second pass off {C.CLOCK_MHZ} MHz after its climb ({', '.join(self.off_clock_passes)}): the card is "
                                       f"not at the forecast's clock (E194.md 11)")
        elif cv == "unread" and rc is not None and j:
            flags.append(f"{cwords} (reported; the scorer's clock rule reads the pass's telemetry)")
            self.unread_clock_passes.append(key)
        pw = C.host_json_words(prec)
        if pw:
            flags.append(pw)
        if self.stops.stop and not str(self.stops.stop).startswith("a second pass off"):
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
        run = {"preset": cfg, "card": "aifoundry2 card 0", "et_devices": self.env.get("ET_DEVICES"), "dry": self.dry,
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
               "live_samples_pass": n_live_pass, "sampler_live_during_pass": sampler_live,
               "host_line": prec, "clock_rule": clock}                      # E194: how the host's line was read; THE CLOCK RULE's reading
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(run, fo, indent=1)
        with self.lock:
            sa = self.set_aside.get(key)
        rd = C.reading(cfg, hj) if rc is not None else "BOUND (no reading: the host did not end)"
        with open(os.path.join(d, "pass.json"), "w") as fo:
            json.dump({"config": cfg, "pass": k, "order_index": idx, "launches_requested": K, "set_aside": sa,
                       "die_start_c": die, "die_gate_wait_s": round(waited, 1), "flags": flags, "sampler_live": sampler_live,
                       "t_start_ms": t_start,
                       "t_end_ms": t_end, "host_rc": rc, "host_status": j.get("status"), "reading": rd, "clock_rule": cv,
                       "dry": self.dry}, fo, indent=1)
        self.say(f"pass {idx}: {cfg} p{k} done: host rc {rc}, status {j.get('status')}, reading {rd}, the clock {cv} ({cn} samples)"
                 f"{', SET ASIDE: ' + sa if sa else ''}{', ' + '; '.join(flags) if flags else ''}")
        if cv == "off" and len(self.off_clock_passes) >= 2:
            self.say(f"STOP: {self.stops.stop}")
        return {"pass": key, "ran": True, "rc": rc, "status": j.get("status"), "reading": rd, "set_aside": sa, "clock": cv}

    # ------------------------------------------------------------------ the dry check (note 1, item 4)
    def dry_check(self):
        """Every device-opening command the real path would run: no ET_DEVICES and no V3_DEVICE in its environment, nothing naming another
        card (etsoc-shire1, /dev/et1_) or an ET_DEVICES= / V3_DEVICE= setting, no dev_mngt_service or et-powertop; the real lock is card
        0's. ('' or why, n)."""
        bad, n = [], 0
        try:
            rows = [json.loads(ln) for ln in open(os.path.join(self.out, "commands.jsonl")) if ln.strip()]
        except (OSError, ValueError) as e:
            return f"commands.jsonl unreadable ({type(e).__name__})", 0
        for r in rows:
            words = " ".join(r.get("real") or [])
            if any(x in words for x in FORBIDDEN):
                bad.append(f"{r.get('kind')}: '{words[:80]}' names a forbidden word")
            if r.get("lock") != "/run/lock/etsoc-shire0.lock":
                bad.append(f"the real lock is {r.get('lock')}")
            if r.get("opens_device"):
                n += 1
                if r.get("et_devices") is not None or r.get("v3_device") is not None:
                    bad.append(f"{r.get('kind')}: ET_DEVICES {r.get('et_devices')!r} or V3_DEVICE {r.get('v3_device')!r} set (both must be unset on aifoundry2)")
        if n == 0:
            bad.append("no device-opening command recorded")
        return "; ".join(sorted(set(bad))[:6]), n

    # ------------------------------------------------------------------ the whole session
    def run(self):
        a = self.a
        tag = " DRY" if self.dry else ""
        self.say(f"session start (T0 {a.t0} = {time.strftime('%H:%M:%S %Z', time.localtime(a.t0))}; plan FULL; programs "
                 f"{'+'.join(self.programs) or 'none'}; aifoundry2 card 0, ET_DEVICES unset; its files in {a.out}){tag}")
        lockf = None
        result = {"t0": a.t0, "dry": self.dry, "programs": self.programs, "queue": self.queue, "card": "aifoundry2 card 0"}
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
                self.say("the box check: aifoundry2, ET_DEVICES and V3_DEVICE unset, the reader at its pin, today's builds on aifoundry2 by "
                         "build_e194.sh, each host and kernel at its build record's sha256 with the kernel gate's OK")
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
            # E194 (KIT.md section 4): the holder rule with card 0's lock held, re-read only while every reason is a stray reader of ours
            # (our live collector reads the card only while `et-who --check` finds nothing held, so it starts no read once the lock is
            # held); the first card command comes only after a clear read
            f, trans = self.foreign_read()
            self.holder_reads.append({"t_ms": now_ms(), "why": f, "transient": trans})
            n_re = 0
            while f and trans and n_re < C.HOLDER_REREAD_N and not self.stop_requested():
                n_re += 1
                self.say(f"the holder rule read a stray reader of ours ({f}) with card 0's lock held: read again in "
                         f"{C.HOLDER_REREAD_S:g} s ({n_re} of {C.HOLDER_REREAD_N})")
                time.sleep(C.HOLDER_REREAD_S)
                f, trans = self.foreign_read()
                self.holder_reads.append({"t_ms": now_ms(), "why": f, "transient": trans})
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((f or "no holder of another login; nothing of ours off card 0, on its ops node or on its management node; no "
                              "device process of another user or of ours") + "\n")
                if len(self.holder_reads) > 1:
                    fo.write(f"read {len(self.holder_reads)} times with the lock held (the stray-reader re-read): "
                             + "; ".join(x["why"] or "clear" for x in self.holder_reads) + "\n")
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
                     f"identity (a): /dev/et0_mgmt, device ID 0, minion_mv between {C.MV_ABOVE} and {C.MV_BELOW}")
            if not self.start_sampler():
                self.say("the sampler would not start: no launch")
                return 16
            self.sampler_t0 = self.samples[0][0] if self.samples else now_ms()
            why = self.identity_read()
            if why:
                self.say(f"identity (b): IDENTITY GATE FAILED: {why}: the gate, no launch")
                return 16
            c = self.identity["etwho_with_sampler"]["counts"]
            self.say(f"identity (b): et-who with the sampler running: ours on card 0 {c['ours_on_card0']} (on /dev/et0_mgmt "
                     f"{c['ours_on_mgmt']}), ours off card 0 0, another login's 0; the sampler holds /dev/et0_mgmt only")
            if self.stop_requested():           # fix-e191k2 (nit 3): an early stop asked for after the start config read, before the test
                self.say(f"{self.stop_req_why} before the stop-path test: the gate, no launch")
                return 16
            ok, res = self.stop_path_test()
            if self.stop_req_why:               # ... or during it: the test is cut, its lines are not read (never "stop-path test failed")
                self.say(f"{self.stop_req_why} during the stop-path test (its lines not read): the gate, no launch")
                return 16
            self.say(f"stop-path test {'passed' if ok else 'failed'}: " + "; ".join(
                (f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, start {'refused' if v['refused_a_start'] else 'NOT refused'}"
                 if k != "clock-rule" else f"the clock rule {'read' if v['tripped'] else 'did NOT read'} the live samples ({v['why']})")
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
            self.say("the counters arm: DROPPED by E189's kit (its KIT.md section 5; E194.md 7): not run")
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
                                           f"{'card 0' if not self.identity['config_end']['why'] else 'NOT card 0: ' + self.identity['config_end']['why']}"
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
                    "each with ET_DEVICES and V3_DEVICE unset; none names another card or an ET_DEVICES setting, or calls "
                    "dev_mngt_service or et-powertop; the lock card 0's: ok" if not why else f"FAILED: {why}"))
                result["dry_check"] = {"ok": not why, "n": n, "why": why}
            result.update({"stop": self.stops.stop, "stop_events": self.stops.events, "set_aside": self.set_aside,
                           "off_clock_passes": self.off_clock_passes, "unread_clock_passes": self.unread_clock_passes,   # E194
                           "holder_reads_at_start": self.holder_reads, "climb_s": self.a.climb_s,                    # E194
                           "bound": self.bound, "identity_ok": not any(
                               (v or {}).get("why") for k2, v in self.identity.items() if k2 in ("config_start", "etwho_with_sampler", "sampler_nodes")),
                           "t_first_ms": int(self.t_first * 1000) if self.t_first else None, "t_close_ms": now_ms(),
                           "end_bound_ms": int(self.close_deadline() * 1000) if self.t_first else None,
                           "early_stop": self.stop_req_why,                                   # finding 5
                           "lock_released_with_bound_host_alive": bool(self.bound_alive()),   # finding 4
                           "sampler_lines_not_live": self.n_not_live,                         # fix-e191k2 (nit 1)
                           "sampler_lines_unreadable": self.n_reader_errors,                  # fix-e194 (nit 7)
                           "sampler_line_errors": self.reader_errors,                         # fix-e194 (nit 7)
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
    ap.add_argument("--climb-s", type=float, default=C.CLIMB_S)      # E194: THE CLOCK RULE's climb (the desk's time scale, --dry only)
    a = ap.parse_args(argv)
    if not a.dry:
        changed = [n for n, v in (("--idle-before", a.idle_before != C.IDLE_BEFORE_S), ("--idle-after", a.idle_after != C.IDLE_AFTER_S),
                                  ("--anchor-s", a.anchor_s != C.ANCHOR_S), ("--die-wait-s", a.die_wait_s != C.DIE_GATE_WAIT_S),
                                  ("--cap-pass-s", a.cap_pass_s != C.CAP_PASS_START_S), ("--cap-end-s", a.cap_end_s != C.CAP_S),
                                  ("--host-bound-s", a.host_bound_s != C.HOST_BOUND_S), ("--sequence", a.sequence != "plan"),
                                  ("--climb-s", a.climb_s != C.CLIMB_S)) if v]
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
