#!/usr/bin/env python3
"""E210's runner (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum): the switch test's whole session on aifoundry3 card 0. E206's
runner for its arm A (tools/claims-v3/e206/run_e206.py, landed in 906699ea, which ran E206 arm A FULL on this card: 241 of 241 runs, data
d7e4f35e), as kit-e207 ported it for E207 on the same card (its local commit 4bd6e38c, under verification when this was written); E190's runner
v2 form behind it (one sampler, the stop lines live, the stop-path test, the identity gate and read, the host watch, the sampler's freshness,
the gates). Every behaviour below is E206's, line for line, but: E210's order (points-e210.json > runs: 171 runs, the warm-up ties, six passes
of chained A B B A blocks, the closing tie, each run's registered host_args); THE OPENING (60 s at rest; the smoke: random@S1, zeros@S1 and
random@S2, each read against E206's measured cycles an op at the shape; THE PROBE of maxalte@S2; then the stop-path test); the card-time rule (no
run after 85 card-minutes, the session ends at 95); one arm only; the files' names (build/e210rgm, build/e210/...).
  - NO SIGKILL ANYWHERE (W/out/orch/kill-rule.txt; AGENT.md "never kill -9"): every process this runner starts that can open a device is
    under a plain `timeout 10` and is never killed: a host (or the reader) still alive HANG_GRACE_S after its timeout's TERM is HUNG: the
    line "<time> HUNG: ..." in the session log, the host's stop file, nothing further started, no further card command (the closing config
    read is not sent), the session closed and the process LEFT (exit 8); et-who, the harness check and the preflight are waited on with a
    bound and, past it, left too (a failed read, never a kill);
  - THE HOST'S RECORDS read with e210_common.host_records (runtime lines dropped wherever they fell; every record parsed whole and checked
    against its own command line); the config read with config_json;
  - THE OPENING in E210.md section 6's order: 60 s at rest, one checked 2 s process each of random@S1, zeros@S1 and random@S2 (the smoke),
    THE PROBE (one checked 2 s process of maxalte@S2 under the die gate after a 10 s rest read: every board sample from its start to the end of
    its 4 s tail at or under 64 W and the die under 63 C, else maxalte leaves the session: its runs are not started, its case NO DATA; a
    registered rule, logged, never a stop), THEN the stop-path test on live samples (no launch); the identity read comes before the smoke (with
    the sampler running);
  - K1: a host whose stderr says "kernel did not finish" (a launch that did not finish: it may leave a hung hart) stops the session at once;
  - an operator's SIGTERM to this runner (never to a host or the sampler) is a registered stop: the stop file, nothing further starts;
  - a crash of this runner is named ("CRASH: <type>: <message>") and exits 1, its closing still run;
  - THE OPERATOR'S STOP FILE (CARD-LANE-BRIEF 2: `touch build/e210/T<T0>-A/STOP` on the box) is a registered stop, read before every start
    (stopped(): the run loop, may_start, every rest read; E202's form); a STOP file already there when the runner starts is a refusal before
    any device ("refused, no device opened"), never removed; a smoke or probe process the STOP file ended is named as the STOP's (verify-e207's
    finding V4, taken in before any datum);
  - a sampler that will not stop on SIGTERM (left running, never killed) still holds the management node: no second sampler is started, the
    session stops, and the closing config read is not sent while it lives;
  - a runtime line naming another card than card 0 ("Opening device N" on a host's, a config read's or the sampler's stdout) is an identity
    trip; the board line skips samples with no board reading, and the runtime-line parser runs until none is left (e210_common).
  (The fixes E206's verifier asked for before E206's land are kept, each marked "fix-e206" where it sits.)
Python's own modules only (the box's system python3). session_e210.sh starts it, detached.

    python3 -B tools/claims-v3/e210/run_e210.py session --arm A --t0 T0 --out build/e210/T<T0>-A [--deadline-epoch E]
    python3 -B tools/claims-v3/e210/run_e210.py session --dry --arm A --t0 T0 --out DIR [--sequence plan|short|two|ties|s2|pass12|cut]
        [--rest-s S --smoke-rest-s S --tail-s S --gate-wait-s S --rule-s S --cap-s S]   (the last six and --sequence in --dry only)

What a session does (E210.md section 6), from the box tree's root (aifoundry3 ~/aifoundry):
  1. checks the box and the build: the hostname is aifoundry3; build/e210rgm's record today's BUILT by build_e210.sh on this box, the kernel
     through THE KERNEL GATE now (check_e210.py --kernel), the host at the sha256 the build recorded, the reader at its pin, every tile (493)
     at its sha256, the harness (check_e210.py --box: HARNESS OK) and the preflight (preflight_e210.sh: dmcmd_audit_v2 GO); the device
     environment without ET_DEVICES; else no device is opened;
  2. takes the card's lock (flock -n /run/lock/etsoc-shire0.lock, held by this process to the end) and reads et-who and the processes (any
     holder line of another login, another user's device process, a CI job, any other device process of ours); an unreadable et-who is a
     holder; else no device opened;
  3. THE FIRST CARD COMMAND: `ettelem config` through the guard under `timeout 10`, its stderr kept: the start config as found (TDP 0 W /
     65 C / 600 MHz) and THE IDENTITY GATE (/dev/et0_mgmt, ID 0); else the gate, no launch. The card time counts from it;
  4. the sampler, `ettelem sample --every-ms 100` through the guard, ONE process for the session (restarted if it dies or goes silent, while
     a run could still start), every line to telemetry.jsonl and to THE STOP LINES as it arrives (board above 70 W on 3 samples in a row,
     die at or above 70 C; the die on the shires' mean, the latch only as it rises: e210_common.Stops). A trip touches the host's
     --stop-file at once (the host ends at its next ~0.5 s launch boundary) and nothing further starts;
  5. THE IDENTITY READ (the sampler running): et-who as counts by card and the sampler's own open files: card 0 only, else the gate;
  6. THE OPENING: 60 s at rest (the rest die and board: the die gate is formed from them), then the smoke: one 2 s process each of random@S1,
     zeros@S1 and random@S2 (`--seconds 2 --budget 3.5`), each rc 0 with every launch ok, its check of C exact or approx, its cycles an op (the
     check record's: the counter's mean) within 50-250% of E206's measured cycles an op at the shape, the board at least 2 W over the rest
     during its launches, the host on card 0; any failure: the smoke gate failed, no run; THEN THE PROBE (above); THEN the stop-path test (each
     line again with a test threshold every live sample crosses must trip within 5 s, touch its own test file and refuse a start; no launch);
  7. the runs, the registered sequence: each run the die gate (min(60, rest die + 4); at most 300 s, else that run NO DATA), the holders
     again, 10 s at rest, ONE host process `timeout 10 sparsity_host <the run's host_args> --kernel <ELF> --stop-file <STOP>`
     (`--seconds 6 --budget 7.5`), then 4 s read; a run of a case the probe took out is not started (NO DATA, the reason named); no run starts
     once the card time passes 85 minutes, nor within its longest length (RUN_MAX_S) + 90 s of the window's last end; a started run is cut only
     by a stop; two failed processes in a row stop the session (E190's E64 rule for one-process runs), and so does K1 or a HUNG host;
  8. the closing, bounded by the 95-minute cap: the sampler stopped (SIGTERM only), the closing `ettelem config` (not after a HUNG), "session
     end", the lock released, queue.json, MANIFEST.sha256 last.
Every device command is a READ: the host opens the ops node only; ettelem config and sample through the guard (it refuses --reset-ms and
anything else before the device opens). No set, no reset, no statistics reset, no power cycle, no firmware change.
--dry swaps every device-opening process for fake_card_e210.py's doubles, takes a lock file in the output directory, skips the box and
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
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e210_common as C  # noqa: E402
import e210_ident as N1  # noqa: E402

ROOT = C.REPO
CHECK_PY = "check_e210.py"
PREFLIGHT_SH = "preflight_e210.sh"
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
CI_COMM = re.compile(r"^Runner\.Worker$")
RC_HUNG = 8


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def pacific_day():
    """Today by the Pacific calendar (the day build_e210.sh writes with TZ=America/Los_Angeles)."""
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


def case_dir(case):
    """A case's folder name in the session (random@S1 -> random-S1)."""
    return case.replace("@", "-")


def bounded(cmd, bound_s, cwd, env, out_path, err_path):
    """Run cmd with its stdout and stderr in files, waiting at most bound_s. (rc or None, stdout, stderr, the Popen). Past the bound the
    process is LEFT running: nothing here ever kills a process (the caller reports it)."""
    with open(out_path, "w") as so, open(err_path, "w") as se:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=env)
        try:
            rc = p.wait(timeout=bound_s)
        except subprocess.TimeoutExpired:
            rc = None
    with open(out_path, errors="replace") as f:
        out = f.read()
    with open(err_path, errors="replace") as f:
        err = f.read()
    return rc, out, err, p


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
        self.tel = open(os.path.join(self.out, "telemetry.jsonl"), "a")
        self.queue = []
        self.t_first = None
        self.device_opened = False
        self.rest_die = None
        self.rest_board = None
        self.last_rx = None
        self.cfg_err = {}
        self.ident = {}
        self.ident_ok = False
        self.hung = []                 # every process left running past its TERM (HUNG): pid, what
        self.left_samplers = []        # every sampler that would not stop on SIGTERM (left running, never killed): fix-e206
        self.cfg_runtime = {}          # the cards the runtime lines of each config read name (fix-e206)
        self.fails_in_row = 0
        self.manifest_written = False
        self.tel_closed = False
        self.lockf = None
        self.probe = None              # THE PROBE's record (E210.md 6)
        self.dropped = {}              # the cases the probe took out of the session: case -> why (their runs are not started)
        self.env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
        self.env.pop("V3_DEVICE", None)
        self.env.pop("ET_DEVICES", None)
        if self.A["et_devices"] is not None:
            self.env["ET_DEVICES"] = self.A["et_devices"]
        self.dev_dir = os.path.realpath(os.path.join(self.out, "fakedev")) if self.dry else N1.DEV_DIR
        if self.dry:
            self.env["E210_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            self.env["E210_FAKE_ARM"] = self.arm
            self.env["E210_FAKE_DEVDIR"] = self.dev_dir
            self.env["E210_FAKE_LOCK"] = os.path.join(self.out, "dry.lock")
            os.makedirs(self.dev_dir, exist_ok=True)
            open(self.env["E210_FAKE_SCHED"], "a").close()
        # fix-e206 (the verifier's finding 1): a STOP file already in the session's folder (each launch has its own T0 folder, so only the
        # operator's touch can have made it) is never removed: the session refuses before any device (body()).
        self.stop_file_at_start = os.path.exists(self.stop_file)

    # ------------------------------------------------------------------ the log, in the kits' form
    def say(self, words):
        w = ("DRY " + words) if self.dry and not words.startswith("session start") else words
        line = f"{stamp()} {w}"
        if not self.manifest_written:
            self.log_f.write(line + "\n")
            self.log_f.flush()
        print(line, flush=True)

    def mark(self, kind, detail, **kw):
        if self.manifest_written:
            return
        with open(os.path.join(self.out, "marks.jsonl"), "a") as f:
            f.write(json.dumps(dict(t_ms=now_ms(), kind=kind, detail=detail, **kw)) + "\n")

    def touch_stop(self):
        try:
            with open(self.stop_file, "a"):
                os.utime(self.stop_file, None)
        except OSError:
            pass

    def on_signal(self, signum, frame):
        """An operator's stop (SIGTERM to this runner): the hosts' stop file, nothing further starts; the session ends itself."""
        self.stops.stop = self.stops.stop or f"the operator's signal {signum} (a registered stop)"
        self.touch_stop()

    def stopped(self):
        """The session's stop, if any: a stop line, a holder, K1, HUNG, two failures, the operator's SIGTERM - or THE OPERATOR'S STOP FILE
        (CARD-LANE-BRIEF 2: `touch build/e210/T<T0>-<arm>/STOP` on the box), read here before every start (E202's form; fix-e206, the
        verifier's finding 1). Every stop of the runner's own names itself before it touches that file, so the first reason is kept."""
        if not self.stops.stop and os.path.exists(self.stop_file):
            self.stops.stop = "the operator's STOP file (a registered stop: nothing further starts)"
            self.mark("stop_file", self.stops.stop)
        return self.stops.stop

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def fake(self, *words):
        return [sys.executable, "-B", os.path.join(HERE, "fake_card_e210.py")] + list(words)

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

    def etwho_lines(self, tag):
        """et-who's holder lines, or (None, why) when it cannot be read (an unreadable et-who is a holder: E202's fix)."""
        d = os.path.join(self.out, "reads")
        os.makedirs(d, exist_ok=True)
        rc, out, err, p = bounded(self.cmd_etwho(), 24, ROOT, self.env, os.path.join(d, f"etwho-{tag}.out"), os.path.join(d, f"etwho-{tag}.err"))
        if rc is None:
            return None, f"et-who unreadable (still running after 24 s; left, nothing killed: pid {p.pid})"
        if rc != 0:
            return None, f"et-who unreadable (rc {rc})"
        return out.splitlines(), ""

    # ------------------------------------------------------------------ holders (counts, never names)
    def foreign(self, with_etwho=True, start=False, tag="run"):
        """'' when nothing blocks the card, else why (counts only). Arm A (aifoundry3, one card; E206 arm A's rule): any holder line of another
        login, another user's device process, a CI job, another device process of ours. An unreadable et-who is a holder (E202's fix)."""
        me = pwd.getpwuid(os.getuid()).pw_name      # our login, as et-who prints it (never written anywhere)
        why, note = [], []
        if with_etwho:
            lines, w = self.etwho_lines(tag)
            if lines is None:
                return w, ""
            hold = [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]
            n_other = sum(1 for f in hold if f[1] != me)
            if n_other:
                why.append(f"{n_other} holder line(s) of another login")
        if not self.dry:
            mine = {os.getpid()}
            if self.sproc is not None:
                mine.add(self.sproc.pid)
            uid = os.getuid()
            n_oth = n_ci = n_ours = 0
            try:
                ps = subprocess.run(["ps", "-eo", "uid=,pid=,state=,comm="], capture_output=True, text=True).stdout.splitlines()
            except OSError:
                return "ps unreadable", ""
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
                elif u != uid and DEV_COMM.search(comm):
                    n_oth += 1
                elif u == uid and DEV_COMM.search(comm):
                    n_ours += 1
            if n_oth:
                why.append(f"{n_oth} other users' device process(es)")
            if n_ci:
                why.append(f"{n_ci} CI job(s)")
            if n_ours:
                why.append(f"{n_ours} other device process(es) of ours")
        elif os.environ.get("E210_FAKE_PS") in ("other", "ours", "ci"):
            why.append({"other": "1 other users' device process(es)", "ours": "1 other device process(es) of ours",
                        "ci": "1 CI job(s)"}[os.environ["E210_FAKE_PS"]])
        return "; ".join(why), "; ".join(note)

    # ------------------------------------------------------------------ the sampler and the live stops
    def _reader(self, proc):
        for raw in proc.stdout:
            if not raw.startswith("{"):
                other = [c for c in C.runtime_cards([raw]) if c != N1.IDENT[self.arm]["card"]]
                if other:                   # fix-e206 (the verifier's finding 10): the sampler's runtime opened another card
                    self.identity_trip(f"the sampler's stdout names card(s) {sorted(set(other))} ({raw.strip()[:40]!r})")
                continue
            try:
                s = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(s, dict):
                continue
            if not self.tel_closed:
                try:
                    self.tel.write(raw if raw.endswith("\n") else raw + "\n")
                except ValueError:          # the closing closed the file meanwhile (a sampler that would not stop)
                    pass
            with self.lock:
                self.samples.append((s.get("t_ms", 0), raw.rstrip("\n")))
                self.last = s
                self.last_rx = time.time()
            if "stop" in self.stops.feed(s):
                self.mark("safety_trip", self.stops.stop, t_sample_ms=s.get("t_ms"))
            ts = self.test_stops
            if ts is not None:
                ts.feed(s)
        if not self.tel_closed:
            try:
                self.tel.flush()
            except ValueError:
                pass

    def close_deadline(self):
        return self.t_first + self.a.cap_s if self.t_first else None

    def start_sampler(self):
        secs = C.CAP_S + 600
        if any(q.poll() is None for q in self.left_samplers):     # fix-e206: never a second reader beside one that would not stop
            self.sampler_would_not_stop()
            return False
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
                    if self.ident_ok:      # a restarted sampler must hold the arm's mgmt node too (its own open files)
                        nodes = N1.proc_nodes(self.sproc.pid, self.dev_dir)
                        wrong = sorted(f"/dev/et{c}_{k}" for c, k in nodes if c != N1.IDENT[self.arm]["card"])
                        self.ident.setdefault("sampler_restarts", []).append({"pid": self.sproc.pid, "nodes": sorted(f"/dev/et{c}_{k}" for c, k in nodes)})
                        if wrong:
                            self.identity_trip(f"the restarted sampler holds {wrong}")
                    return True
                if self.sproc.poll() is not None:
                    break
                time.sleep(0.25)
            if not self.stop_sampler(self.close_deadline()):     # fix-e206: a silent sampler that will not stop: no further attempt
                self.sampler_would_not_stop()
                return False
            time.sleep(2)
        return False

    def sampler_alive(self):
        return self.sproc is not None and self.sproc.poll() is None

    def stop_sampler(self, deadline=None):
        """SIGTERM only (never kill -9 a tool): 30 s, then once more and 60 s; each wait ends CLOSE_S / 2 before the end bound but lasts
        at least 2 s; a sampler that will not stop is recorded and left."""
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
            self.left_samplers.append(p)
        self.sproc = None
        return ok

    def sampler_would_not_stop(self):
        """fix-e206 (the verifier's finding 4): a sampler left running after SIGTERM still holds the management node, which is single-open
        (telemetry clients do not coexist there): no second sampler is started; the session stops (nothing further starts); the closing
        config read is not sent while it lives. Nothing is killed."""
        pids = [q.pid for q in self.left_samplers if q.poll() is None]
        self.stops.stop = self.stops.stop or (f"the sampler would not stop on SIGTERM (pid(s) {pids}, left running, never killed): no second "
                                              f"reader of the management node is started")
        self.touch_stop()
        self.mark("sampler_left", self.stops.stop, pids=pids)

    def fresh(self):
        with self.lock:
            rx = self.last_rx
        return N1.fresh(self.sampler_alive(), rx)

    def staleness(self):
        with self.lock:
            rx = self.last_rx
        return f"alive {self.sampler_alive()}, last sample {'never' if rx is None else '%.1f s ago' % (time.time() - rx)}"

    def ensure_fresh_sampler(self):
        if self.fresh():
            return True
        why = self.may_start(60) if self.t_first else ""
        if why:
            self.say(f"the sampler is not live ({self.staleness()}); not restarted: no run can start ({why})")
            return False
        self.say(f"the sampler is not live ({self.staleness()}): restarting it")
        if self.sampler_alive() and not self.stop_sampler(self.close_deadline()):
            self.sampler_would_not_stop()          # fix-e206: never a second reader beside a sampler that would not stop
            return False
        return self.start_sampler()

    def identity_trip(self, why):
        """Another card named or held: the hosts' stop file at once (a running host ends at its next launch boundary), nothing further."""
        self.stops.stop = self.stops.stop or f"identity: {why}"
        self.touch_stop()
        self.mark("identity_trip", why)

    def latest(self):
        with self.lock:
            return dict(self.last) if self.last else None

    def window(self, t0_ms, t1_ms):
        with self.lock:
            return [json.loads(ln) for (t, ln) in self.samples if t0_ms <= t <= t1_ms]

    def nap(self, seconds):
        """Wait at rest, watching every stop and the operator's STOP file (fix-e206); False at once when one trips."""
        end = time.time() + seconds
        while time.time() < end:
            if self.stopped():
                return False
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stopped()

    def idle(self, seconds):
        end = time.time() + seconds
        while time.time() < end:
            time.sleep(min(0.2, max(0.0, end - time.time())))
        return not self.stops.stop

    # ------------------------------------------------------------------ the gates
    def may_start(self, seconds):
        """A run (or the opening's next process) may start: no stop (the operator's STOP file included: fix-e206); the card time under the
        85-minute rule (E210.md 6); its planned length inside the 95-minute cap less the closing; before the window's last end."""
        if self.stopped() or (self.test_stops is not None and self.test_stops.stop):
            return "a stop line has tripped"
        el = time.time() - self.t_first
        if el > self.a.rule_s:
            return f"the card-time rule: {el / 60:.1f} card-minutes since the first card command (no run after {self.a.rule_s / 60:g})"
        if el + seconds > self.a.cap_s - C.CLOSE_S:
            return f"the cap: {el / 60:.1f} card-minutes + {seconds:.0f} s would pass {self.a.cap_s / 60:g} less the closing"
        if self.a.deadline_epoch and time.time() + seconds + C.WINDOW_MARGIN_S > self.a.deadline_epoch:
            return "the window's last end is too close"
        return ""

    def die_gate(self, gate, planned):
        t = time.time()
        while True:
            s = self.latest() if self.fresh() else None
            die = C.die_of(s) if s else None
            if die is not None and gate is not None and die <= gate:
                return True, die, time.time() - t, ""
            why = self.may_start(planned)
            if why:
                return False, die, time.time() - t, why
            if time.time() - t >= self.a.gate_wait_s:
                return False, die, time.time() - t, ""
            if not self.ensure_fresh_sampler():
                return False, die, time.time() - t, "the sampler is not live"
            time.sleep(0.5)

    # ------------------------------------------------------------------ reads
    def config(self, name, bound_s=C.HOST_TIMEOUT_S + C.HANG_GRACE_S):
        rc, out, err, p = bounded(self.cmd_config(), bound_s, ROOT, self.env, os.path.join(self.out, f"config-{name}.out"),
                                  os.path.join(self.out, f"config-{name}.err"))
        if rc is None:
            self.on_hung(p.pid, f"the {name} config read (`timeout {C.HOST_TIMEOUT_S}` and the reader)")
            return None, "the config read did not end after its timeout's TERM (HUNG)"
        j = C.config_json(out)
        with open(os.path.join(self.out, f"config-{name}.json"), "w") as f:
            f.write(json.dumps(j) + "\n")
        self.cfg_err[name] = err or ""
        self.cfg_runtime[name] = C.runtime_cards(C.drop_runtime(out)[1])     # fix-e206: the cards its runtime lines open
        if rc != 0 or not j:
            return None, f"config read rc {rc}, no JSON line"
        return j, ""

    def write_ident(self):
        if self.manifest_written:
            return
        with open(os.path.join(self.out, "identity.json"), "w") as f:
            json.dump(self.ident, f, indent=1, sort_keys=True)

    def identity_read(self):
        me = pwd.getpwuid(os.getuid()).pw_name
        lines, why_w = self.etwho_lines("identity")
        why_e, counts = N1.etwho_identity(self.arm, lines or [], me) if lines is not None else (why_w, {})
        nodes = N1.proc_nodes(self.sproc.pid, self.dev_dir) if self.sproc is not None else set()
        c = N1.IDENT[self.arm]["card"]
        why_s = []
        if (c, "mgmt") not in nodes:
            why_s.append(f"the sampler (pid {self.sproc.pid if self.sproc else None}) does not hold {N1.IDENT[self.arm]['mgmt']}")
        off = sorted(f"/dev/et{x}_{k}" for x, k in nodes if x != c)
        if off:
            why_s.append(f"the sampler holds {off}")
        self.ident["etwho_with_sampler"] = {"counts": counts, "why": why_e}
        self.ident["sampler_nodes"] = {"nodes": sorted(f"/dev/et{x}_{k}" for x, k in nodes), "why": "; ".join(why_s)}
        with open(os.path.join(self.out, "etwho-identity.txt"), "w") as f:
            f.write(f"et-who with the sampler running, before the smoke (counts by card; no login): {json.dumps(counts, sort_keys=True)}; "
                    f"{why_e or 'ok'}\nthe sampler's own nodes: {self.ident['sampler_nodes']['nodes']}; {'; '.join(why_s) or 'ok'}\n")
        why = "; ".join(x for x in [why_e] + why_s if x)
        self.ident_ok = not why
        self.write_ident()
        return not why, why

    # ------------------------------------------------------------------ a HUNG process (no kill, ever)
    def on_hung(self, pid, what):
        self.hung.append({"pid": pid, "what": what, "t_ms": now_ms()})
        self.stops.stop = self.stops.stop or f"HUNG: {what}"
        self.touch_stop()
        self.say(f"HUNG: a device process ({what}; its `timeout` pid {pid}) still runs {C.HANG_GRACE_S:g} s after its timeout's TERM "
                 f"at {C.HOST_TIMEOUT_S} s: nothing kills it (no SIGKILL, ever); the stop file is touched, nothing further starts and no "
                 f"further card command is sent; report it to the owner at once (the card may hold a hung hart: never reset it)")
        self.mark("hung", what, pid=pid)

    # ------------------------------------------------------------------ one host process
    def run_proc(self, argv, d, name, case, kind):
        os.makedirs(d, exist_ok=True)
        env = dict(self.env, E210_FAKE_KIND=kind, E210_FAKE_CASE=case) if self.dry else self.env
        outp, errp = os.path.join(d, name + ".out"), os.path.join(d, name + ".err")
        t0 = now_ms()
        hung = False
        with open(outp, "w") as so, open(errp, "w") as se:
            p = subprocess.Popen(self.host_cmd(argv), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=env)
            watch = N1.HostWatch(self.arm, p.pid, errp, self.dev_dir, on_wrong=self.identity_trip)
            watch.start()
            try:
                rc = p.wait(timeout=C.HOST_TIMEOUT_S + C.HANG_GRACE_S)
            except subprocess.TimeoutExpired:          # past its TERM: HUNG, reported and LEFT (never killed)
                rc, hung = None, True
            watch.finish()
        t1 = now_ms()
        self.device_opened = True
        if hung:
            self.on_hung(p.pid, f"the host of {os.path.basename(d)} ({name})")
        with open(outp, errors="replace") as f:
            text = f.read()
        with open(errp, errors="replace") as f:
            etext = f.read()
        fma, chk, info = C.host_records(text, argv)
        lw = [x for x in fma if x.get("t_start_ms") and x.get("t_end_ms")]
        k1 = "kernel did not finish" in etext
        rt_other = sorted({c for c in C.runtime_cards(info["runtime_lines"]) if c != N1.IDENT[self.arm]["card"]})
        if rt_other:            # fix-e206 (the verifier's finding 10): the host's runtime opened another card than the arm's
            self.identity_trip(f"the runtime named card(s) {rt_other} on the host's stdout of {os.path.basename(d)} ('Opening device N')")
        return {"name": name, "argv": argv, "rc": rc, "hung": hung, "t0_ms": t0, "t1_ms": t1, "n_launch": len(fma), "runtime_other_cards": rt_other,
                "launches_ok": bool(fma) and all(x.get("ok") for x in fma),
                "check": chk[-1].get("result") if chk else None, "check_ok": bool(chk) and bool(chk[-1].get("ok")),
                "checks": [x.get("result") for x in chk],
                "check_cycles_per_op": chk[-1].get("cycles_per_op") if chk else None,
                "stopped_by_file": "stopping:" in etext and "exists" in etext, "k1": k1,
                "records": {"runtime_lines": len(info["runtime_lines"]), "unparsed": info["unparsed"], "mismatched": len(info["mismatched"]),
                            "other": info["other"]},
                "launch_window_ms": [min(x["t_start_ms"] for x in lw), max(x["t_end_ms"] for x in lw)] if lw else None,
                "ident": watch.result()}

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

    # ------------------------------------------------------------------ the opening: the rest, the smoke, the probe, the stop-path test
    def stop_words(self, what):
        """verify-e207's finding V4: a process the operator's STOP file (or another stop) ended is named as that stop's, first."""
        s = self.stopped()
        return f"{what}: a stop during it: {s}" if s else ""

    def opening(self):
        d0 = os.path.join(self.out, "smoke")
        os.makedirs(d0, exist_ok=True)
        t0 = now_ms()
        self.say(f"the opening: {self.a.smoke_rest_s:g} s at rest (the session's rest reading)")
        ok = self.nap(self.a.smoke_rest_s)
        t1 = now_ms()
        win = self.window(t0, t1)
        dies = [C.die_of(s) for s in win if C.die_of(s) is not None]
        bws = [s.get("board_w") for s in win if s.get("board_w") is not None]
        self.rest_die = statistics.median(dies) if dies else None
        self.rest_board = statistics.median(bws) if bws else None
        rest = {"t0_ms": t0, "t1_ms": t1, "samples": len(win), "board_w_median": self.rest_board, "die_median_c": self.rest_die,
                "gate_c": C.gate_c(self.arm, self.rest_die), "latch_c": sorted({C.latch_of(s) for s in win if C.latch_of(s) is not None})}
        with open(os.path.join(d0, "rest.json"), "w") as f:
            json.dump(rest, f, indent=1)
        self.say(f"the opening's rest: {len(win)} samples, board {rest['board_w_median']} W, die {self.rest_die} C (the latch {rest['latch_c']}); "
                 f"the die gate {rest['gate_c']} C")
        if not ok:
            return False, f"a stop during the rest reading: {self.stops.stop}"
        if not win or self.rest_die is None:
            return False, "no live sample in the rest reading"
        for case in C.SMOKE_CASES:
            why = self.may_start(C.HOST_TIMEOUT_S + C.HANG_GRACE_S + 5)
            if why:
                return False, f"{case}: not started ({self.stopped() or why})"
            if not self.fresh():
                return False, f"{case}: not started (the sampler is not live: {self.staleness()})"
            argv = C.host_argv(ROOT, C.case_args(case), C.SMOKE_SECONDS, C.SMOKE_BUDGET, self.stop_file)
            dd = os.path.join(d0, case_dir(case))
            p = self.run_proc(argv, dd, "proc", case, "smoke")
            ref, ref_pt = C.smoke_ref(case)
            cpo = p["check_cycles_per_op"]
            ratio = cpo / ref if cpo else None
            idn = p["ident"]
            id_ok = not idn["wrong"] and idn["right"] and not p["runtime_other_cards"]     # fix-e206: a runtime line naming another card
            win = self.window(*p["launch_window_ms"]) if p["launch_window_ms"] else []
            rise_ok, rise, n_rise = N1.board_rise(win, p["launch_window_ms"], self.rest_board)
            good = p["rc"] == 0 and p["launches_ok"] and p["check"] in ("exact", "approx") and p["check_ok"] and \
                ratio is not None and C.CYC_LO <= ratio <= C.CYC_HI and id_ok and rise_ok and not p["k1"] and not p["hung"]
            with open(os.path.join(dd, "smoke.json"), "w") as fo:
                json.dump(dict(p, case=case, cycles_ref=ref, cycles_ref_is=f"E206's measured cycles an op at the shape ({ref_pt}; E210.md 6)",
                               cycles_ratio=ratio, identity_ok=id_ok,
                               board_rise={"ok": rise_ok, "rise_w": rise, "samples": n_rise, "rest_w": self.rest_board,
                                           "min_w": N1.RISE_MIN_W}, good=good), fo, indent=1)
            self.ident.setdefault("smoke", {})[case] = {"host": idn, "board_rise_w": rise, "rise_samples": n_rise}
            self.write_ident()
            self.say(f"smoke {case}: rc {p['rc']}, {p['n_launch']} launches, check {p['check']}, cycles an op {cpo} "
                     f"({'%.3f' % ratio if ratio else '-'} of E206's {ref:.2f} at {ref_pt}); records: {p['records']['runtime_lines']} runtime line(s) dropped, "
                     f"{p['records']['unparsed']} unparsed, {p['records']['mismatched']} not its command's; the host's card: "
                     f"{'its own' if id_ok else ('ANOTHER: ' + '; '.join(idn['wrong']) if idn['wrong'] else ('ANOTHER by its runtime line: card(s) ' + str(p['runtime_other_cards']) if p['runtime_other_cards'] else 'NOT SEEN'))} "
                     f"(stderr {idn['stderr_targets']} {idn['stderr_ids']}, held {idn['nodes_held']}); the board {rise} W over the rest "
                     f"on {n_rise} samples (at least {N1.RISE_MIN_W:g} W): {'ok' if good else 'FAILED'}")
            if p["k1"]:
                self.stops.stop = self.stops.stop or f"K1: a launch of the smoke's {case} did not finish (the host's words): it may leave a hung hart"
                self.touch_stop()
                self.say(self.stops.stop)
            if not good:
                sw = self.stop_words(f"{case}")
                return False, sw or (f"{case}: rc {p['rc']}, check {p['check']}, cycles ratio {ratio}, the host's card "
                                     f"{'ok' if id_ok else 'NOT the arm' + chr(39) + 's'}, the board's rise {rise} W on {n_rise} samples"
                                     f"{', K1' if p['k1'] else ''}{', HUNG' if p['hung'] else ''}")
            if self.stopped():
                return False, f"a stop line tripped during the smoke's {case}: {self.stops.stop}"
        ok, why = self.probe_run()
        if not ok:
            return False, why
        ok, res = self.stop_path_test()
        self.say("stop-path test " + ("passed" if ok else "failed") + ": " + "; ".join(
            f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, its file {'touched' if v['test_file_touched'] else 'NOT touched'}, "
            f"start {'refused' if v['refused_a_start'] else 'NOT refused'}" for k, v in res.items()))
        if not ok:
            return False, "the stop-path test failed"
        return True, ""

    def probe_run(self):
        """THE PROBE (E210.md 6): one checked 2 s process of maxalte@S2, under the die gate and after a 10 s rest read (the run form's; the
        kit's reading), its window from the process's start to the end of a 4 s tail: every board sample at or under 64 W and the die under
        63 C (e210_common.probe_verdict), else maxalte leaves the session (its runs not started, its case NO DATA: a registered rule, logged;
        not a stop). A probe process that ends badly (rc not 0, no launch, a check of C not exact or approx) also leaves maxalte out (the line
        could not be shown), and counts as a failed process. K1, HUNG and an identity trip stop the session as anywhere. (ok, why): not ok only
        when the session must stop."""
        case = C.PROBE_CASE
        d = os.path.join(self.out, "probe", case_dir(case))
        os.makedirs(d, exist_ok=True)
        rec = {"case": case, "rule": f"every board sample at or under {C.PROBE_BOARD_MAX_W:g} W and the die under {C.PROBE_DIE_BELOW_C:g} C "
                                      f"from the process's start to the end of its {self.a.tail_s:g} s tail (E210.md 6)"}
        planned = C.RUN_MAX_S
        why = self.may_start(planned)
        if why:
            return False, f"the probe: not started ({self.stopped() or why})"
        gate = C.gate_c(self.arm, self.rest_die)
        ok, die, waited, gwhy = self.die_gate(gate, planned)
        rec["gate"] = {"c": gate, "die": die, "waited_s": round(waited, 1)}
        if not ok:
            if gwhy:
                return False, f"the probe: not started ({self.stopped() or gwhy})"
            rec.update(verdict="OUT", why=f"the die gate: {die} C after {waited:.0f} s (gate {gate} C): no probe process")
            return self._probe_done(rec, d)
        f, note = self.foreign(tag="probe")
        if f:
            self.stops.stop = self.stops.stop or f"a holder or a device process: {f}"
            self.touch_stop()
            return False, f"STOP before the probe: {f}"
        self.say(f"the probe {case}: one {C.PROBE_SECONDS:g} s process (gate {gate} C, die {die} C after {waited:.0f} s)")
        r0 = now_ms()
        clean = self.nap(self.a.rest_s)
        rec["rest"] = {"t0_ms": r0, "t1_ms": now_ms()}
        if not clean:
            return False, f"the probe: a stop in its rest read ({self.stops.stop})"
        if not self.fresh():
            rec.update(verdict="OUT", why=f"the sampler was not live before the probe's process ({self.staleness()})")
            return self._probe_done(rec, d)
        with self.lock:
            latch_low = self.stops.latch_low
        argv = C.host_argv(ROOT, C.case_args(case), C.PROBE_SECONDS, C.PROBE_BUDGET, self.stop_file)
        p = self.run_proc(argv, d, "proc", case, "probe")
        rec["proc"] = p
        if not self.hung:
            self.idle(self.a.tail_s)
        w1 = now_ms()
        win = self.window(p["t0_ms"], w1)
        verdict, bmax, dmax, vwhy = C.probe_verdict(win, latch_low)
        rec.update(window_ms=[p["t0_ms"], w1], samples=len(win), board_max_w=bmax, die_max_c=dmax, latch_low_c=latch_low)
        bad_proc = []
        if p["rc"] != 0:
            bad_proc.append(f"the process rc {p['rc']}")
        if not p["n_launch"] or not p["launches_ok"]:
            bad_proc.append("no launch, or a launch not ok")
        if p["check"] not in ("exact", "approx"):
            bad_proc.append(f"the check of C {p['check']}")
        if p["rc"] != 0:
            self.fails_in_row += 1
        else:
            self.fails_in_row = 0
        if p["k1"]:
            self.stops.stop = self.stops.stop or f"K1: a launch of the probe {case} did not finish (the host's words): it may leave a hung hart"
            self.touch_stop()
        if self.stopped():
            rec.update(verdict="OUT", why=f"a stop during the probe: {self.stops.stop}")
            self._probe_done(rec, d)
            return False, f"a stop during the probe {case}: {self.stops.stop}"
        if bad_proc:
            verdict, vwhy = "OUT", "; ".join(bad_proc + ([vwhy] if vwhy else []))
        rec.update(verdict=verdict, why=vwhy)
        return self._probe_done(rec, d)

    def _probe_done(self, rec, d):
        case = rec["case"]
        if rec["verdict"] != "IN":
            self.dropped[case] = f"{case} left the session at its probe ({rec['why']}): E210.md 6's registered rule, not a stop"
        self.probe = {k: v for k, v in rec.items() if k != "proc"}
        if "proc" in rec:
            self.probe["proc"] = {k: rec["proc"].get(k) for k in ("rc", "n_launch", "check", "checks", "hung", "k1", "t0_ms", "t1_ms",
                                                                  "launch_window_ms", "records", "runtime_other_cards", "stopped_by_file")}
        with open(os.path.join(d, "probe.json"), "w") as fo:
            json.dump(rec, fo, indent=1)
        self.say(f"the probe {case}: {rec['verdict']} (board max {rec.get('board_max_w')} W, die max {rec.get('die_max_c')} C on "
                 f"{rec.get('samples', 0)} samples{'; ' + rec['why'] if rec.get('why') else ''})"
                 + (f": {case} leaves the session (its runs are not started; its case NO DATA)" if rec["verdict"] != "IN" else ": it stays in the session"))
        if self.fails_in_row >= 2:
            self.stops.stop = self.stops.stop or "two failed processes in a row (the last the probe's)"
            self.touch_stop()
        return True, ""

    # ------------------------------------------------------------------ one run
    def one_run(self, r):
        key = C.run_key(r)
        d = os.path.join(self.out, "runs", key)
        base = {"n": r["n"], "run": key, "case": r["case"], "role": r["role"], "pass": r["pass"], "arm": self.arm}
        if r["case"] in self.dropped:
            why = self.dropped[r["case"]]
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        planned = C.RUN_MAX_S
        why = self.may_start(planned)
        if why:
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        gate = C.gate_c(self.arm, self.rest_die)
        ok, die, waited, gwhy = self.die_gate(gate, planned)
        if not ok:
            w = gwhy or f"the die gate: {die} C after {waited:.0f} s (gate {gate} C)"
            self.say(f"run {key}: not started ({w}): no data")
            return dict(base, ran=False, why=w, gate={"c": gate, "die": die, "waited_s": round(waited, 1)})
        why = self.may_start(planned)
        if why:
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        f, note = self.foreign(tag=key)
        if f:
            self.stops.stop = self.stops.stop or f"a holder or a device process: {f}"
            self.touch_stop()
            self.say(f"STOP before run {key}: {f}")
            return dict(base, ran=False, why=f)
        os.makedirs(d, exist_ok=True)
        self.say(f"run {key}: {r['case']} ({r['role']}), one {C.RUN_SECONDS:g} s process (gate {gate} C, die {die} C after {waited:.0f} s)"
                 + (f"; {note}" if note else ""))
        r0 = now_ms()
        clean = self.nap(self.a.rest_s)
        r1 = now_ms()
        rec = dict(base, gate={"c": gate, "die": die, "waited_s": round(waited, 1)}, rest={"t0_ms": r0, "t1_ms": r1}, procs=[], flags=[])
        if note:
            rec["flags"].append(note)
        if not clean:
            self.say(f"run {key}: a stop tripped in its rest read: no process started")
            rec.update(ran=False, why="stop: " + str(self.stops.stop))
            with open(os.path.join(d, "run.json"), "w") as fo:
                json.dump(rec, fo, indent=1)
            return rec
        if not self.fresh():
            rec["flags"].append(f"the sampler was not live before the process ({self.staleness()}): no process started")
            self.say(f"run {key}: the sampler is not live before its process ({self.staleness()}): no process, flagged")
        else:
            argv = C.host_argv(ROOT, r["host_args"], C.RUN_SECONDS, C.RUN_BUDGET, self.stop_file)
            p = self.run_proc(argv, d, "proc-00", r["case"], "run")
            rec["procs"].append(p)
            if not p["ident"]["right"] and not p["ident"]["wrong"]:
                rec["flags"].append("the host's card was not seen on its stderr or in its open files (reported)")
            if p["records"]["unparsed"] or p["records"]["mismatched"]:
                rec["flags"].append(f"{p['records']['unparsed']} record(s) unparsed, {p['records']['mismatched']} not its command's: not read")
            if p["runtime_other_cards"]:
                rec["flags"].append(f"the host's runtime named card(s) {p['runtime_other_cards']}: an identity trip (fix-e206)")
            if p["k1"]:
                self.stops.stop = self.stops.stop or f"K1: a launch of run {key} did not finish (the host's words): it may leave a hung hart"
                self.touch_stop()
                rec["flags"].append("K1: a launch did not finish")
            if p["rc"] != 0:
                self.fails_in_row += 1
                rec["flags"].append(f"the process rc {p['rc']}")
                if self.fails_in_row >= 2:
                    self.stops.stop = self.stops.stop or f"two failed processes in a row (the last in run {key})"
                    self.touch_stop()
            else:
                self.fails_in_row = 0
        w1 = now_ms()
        if not self.hung:
            self.idle(self.a.tail_s)
        ran = bool(rec["procs"])
        rec.update(ran=ran, work={"t0_ms": rec["procs"][0]["t0_ms"] if rec["procs"] else r1, "t1_ms": w1}, tail_end_ms=now_ms(),
                   stop=self.stops.stop)
        if not ran:
            rec["why"] = "; ".join(rec["flags"]) or "no process started"
        if self.stopped():
            rec["flags"].append(f"a stop tripped during this run: {self.stops.stop}")
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(rec, fo, indent=1)
        self.say(f"run {key} done: {len(rec['procs'])} process(es), rc {[p['rc'] for p in rec['procs']]}, checks "
                 f"{sorted({str(p['check']) for p in rec['procs']})}{', ' + '; '.join(rec['flags']) if rec['flags'] else ''}")
        out = dict(base, ran=ran, n_procs=len(rec["procs"]), rcs=[p["rc"] for p in rec["procs"]], flags=rec["flags"])
        if not ran:
            out["why"] = rec["why"]
        return out

    # ------------------------------------------------------------------ the box and the build (never under --dry)
    def box_check(self):
        """'' when the box, the build and the readers are the registered ones, else why (no device is opened)."""
        host = socket.gethostname().split(".")[0]
        if host != self.A["box"]:
            return f"this host is {host!r}, not arm {self.arm}'s {self.A['box']!r}"
        if "ET_DEVICES" in self.env:
            return "arm A's device environment carries ET_DEVICES (aifoundry3's one card is opened with it unset)"
        bad = []
        try:
            rec = C.load(os.path.join(ROOT, C.BUILD_REC))
        except (OSError, ValueError):
            return f"no build record {C.BUILD_REC}: run build_e210.sh (the runbook's build step) first"
        today = pacific_day()
        if rec.get("day") != today or rec.get("verdict") != "BUILT" or rec.get("box") != self.A["box"] or rec.get("builder") != C.BUILDER:
            bad.append(f"the build record is not today's BUILT by {C.BUILDER} on {self.A['box']} ({rec.get('day')}, {rec.get('verdict')}, "
                       f"{rec.get('box')}, {rec.get('builder')})")
        for rel, want in ((C.ELF, rec.get("kernel_sha256")), (C.HOST, rec.get("host_sha256")), (self.A["ettelem"], self.A["ettelem_sha256"])):
            p = os.path.join(ROOT, rel)
            got = sha256(p) if os.path.isfile(p) else None
            if got is None or got != want:
                bad.append(f"{rel}: sha256 {got}, want {want}")
        try:
            tl = C.tiles()
        except OSError as e:
            return f"the tiles' list could not be read ({type(e).__name__})"
        nbad = [rel for rel, want in sorted(tl.items()) if not os.path.isfile(os.path.join(ROOT, rel)) or sha256(os.path.join(ROOT, rel)) != want]
        if nbad:
            bad.append(f"{len(nbad)} of {len(tl)} tile file(s) not at their sha256 (the first {nbad[0]})")
        if bad:
            return "; ".join(bad)
        for name, cmd, want in (("kernel", [sys.executable, "-B", os.path.join(HERE, CHECK_PY), "--kernel", os.path.join(ROOT, C.ELF)], "KERNEL OK"),
                                ("harness", [sys.executable, "-B", os.path.join(HERE, CHECK_PY), "--box"], "HARNESS OK: "),
                                ("preflight", ["bash", os.path.join(HERE, PREFLIGHT_SH)], "dmcmd_audit: GO")):
            rc, out, err, p = bounded(cmd, 180, ROOT, dict(os.environ), os.path.join(self.out, f"{name}.txt"), os.path.join(self.out, f"{name}.err"))
            txt = out + err
            if rc is None or rc != 0 or not any(ln.startswith(want) for ln in txt.splitlines()):
                bad.append(f"the {name} check did not read {want.strip()} (rc {rc}; {name}.txt{'; still running, left' if rc is None else ''})")
        return "; ".join(bad)

    # ------------------------------------------------------------------ the whole session
    def run(self):
        """The session, then the closing (always); the exit: 0 ended (a stop in the runs included), 16 a gate, 8 HUNG, 1 a crash."""
        a = self.a
        tag = " DRY" if self.dry else ""
        self.say(f"session start (T0 {a.t0} = {time.strftime('%H:%M:%S %Z', time.localtime(a.t0))}; arm {self.arm}, {self.A['card']}; "
                 f"its files in {os.path.basename(self.out)}){tag}")
        self.lockf = None
        rc = 1
        try:
            rc = self.body()
        finally:
            rc = self.closing(rc)
        return rc

    def select(self, seq):
        """--dry and the desk's real-path test only: a subset of the registered order (main() refuses --sequence without --dry)."""
        by = {r["run"]: r for r in seq}
        s = self.a.sequence
        if s == "short":       # the first warm-up tie and two runs of pass 1: the host's own draws (sparse50) and a pattern of 61 tile files
            return [by["001-open-random-S1"], by["004-pass1-sparse50-S1"], by["007-pass1-bhalfeq-S1"]]
        if s == "two":         # the first tie, then one R and one P (the first block's head)
            return [by["001-open-random-S1"], by["003-pass1-random-S1"], by["004-pass1-sparse50-S1"]]
        if s == "ties":        # the three ties
            return [r for r in seq if r["role"] == "tie"]
        if s == "s2":          # pass 2's first three blocks (S2: highmant8, hd4, maxalte: the probe's case among them)
            return [r for r in seq if r["pass"] == "pass2"][:10]
        if s == "pass12":      # the warm-up ties and passes 1 and 2
            return [r for r in seq if r["pass"] in ("open", "pass1", "pass2")]
        if s == "cut":         # the registered subset if cut (E210.md 6: "the opening and passes 1-4"): the warm-up ties and passes 1-4
            return [r for r in seq if r["pass"] in ("open", "pass1", "pass2", "pass3", "pass4")]
        return seq

    def body(self):
        a = self.a
        rc = 1
        try:
            if self.stop_file_at_start:      # fix-e206 (the verifier's finding 1): the operator's stop before the start; the file is kept
                self.stops.stop = "the operator's STOP file was in the session's folder before it started (a registered stop)"
                self.say("refused, no device opened: the operator's STOP file is already in the session's folder (a registered stop; the "
                         "file is kept, never removed)")
                rc = 16
                return rc
            if not self.dry:
                why = self.box_check()
                if why:
                    self.say(f"refused, no device opened: the box or the build is not the registered one ({why})")
                    rc = 16
                    return rc
                self.say("the box and the build: the host, build/e210rgm (the kernel through THE KERNEL GATE, the host as built today), "
                         "the reader at its pin, the 493 tiles, the harness (the registration's frozen points and forecasts among it) and the "
                         "preflight (dmcmd_audit_v2 GO)")
            lockp = os.path.join(self.out, "dry.lock") if self.dry else self.A["lock"]
            if not self.dry and not os.path.exists(lockp):
                self.say(f"refused, no device opened: no card lock {lockp} on this box (it is never created here)")
                rc = 16
                return rc
            try:
                self.lockf = open(lockp, "a+")
            except OSError as e:
                self.say(f"refused, no device opened: the card's lock cannot be opened ({type(e).__name__})")
                rc = 16
                return rc
            try:
                fcntl.flock(self.lockf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                self.say("refused, no device opened: the card's lock is held")
                rc = 16
                return rc
            f, note = self.foreign(start=True, tag="before")
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((f or "no holder that blocks; no device process that blocks") + (f"; {note}" if note else "") + "\n")
            if f:
                self.say(f"refused, no device opened: a holder or a device process ({f})")
                rc = 16
                return rc
            self.t_first = time.time()
            self.say("the first card command: the start config read through the guard")
            cfg0, why = self.config("start")
            self.device_opened = True
            if self.hung:
                rc = RC_HUNG
                return rc
            if not cfg0 or not C.config_ok(self.arm, cfg0):
                self.say(f"config start: {why or json.dumps(cfg0)}: not {self.A['config']}: the gate, no launch")
                rc = 16
                return rc
            tg, ids = N1.parse_ident(self.cfg_err.get("start", ""))
            idw = N1.config_identity(self.arm, cfg0, self.cfg_err.get("start", ""))
            rt0 = sorted({c for c in self.cfg_runtime.get("start", []) if c != N1.IDENT[self.arm]["card"]})
            if rt0:              # fix-e206 (the verifier's finding 10): the reader's runtime opened another card
                idw = "; ".join(x for x in (idw, f"its stdout's runtime line(s) name card(s) {rt0}") if x)
            self.ident["config_start"] = {"targets": sorted({f"/dev/et{c}_{k}" for c, k in tg}), "ids": sorted(set(ids)),
                                          "minion_mv": cfg0.get("minion_mv"), "runtime_cards": self.cfg_runtime.get("start", []), "why": idw}
            self.write_ident()
            if idw:
                self.say(f"config start: {json.dumps(cfg0)}: the card's identity: {idw}: the gate, no launch")
                rc = 16
                return rc
            self.say(f"config start: {json.dumps(cfg0)} (read, nothing set); the card's identity: PCIe target "
                     f"{N1.IDENT[self.arm]['mgmt']}, physical device ID {N1.IDENT[self.arm]['phys_id']}"
                     + (f", minion_mv {cfg0.get('minion_mv')} below {N1.IDENT[self.arm]['mv_below']}" if N1.IDENT[self.arm]["mv_below"] else ""))
            if not self.start_sampler():
                self.say("the sampler would not start: no launch")
                rc = 16
                return rc
            ok, why = self.identity_read()
            if not ok:
                self.say(f"the identity read (the sampler running, before the smoke): {why}: the gate, no launch")
                rc = 16
                return rc
            self.say(f"the identity read: et-who {json.dumps(self.ident['etwho_with_sampler']['counts'], sort_keys=True)} (counts by card), "
                     f"the sampler holds {self.ident['sampler_nodes']['nodes']}: card {N1.IDENT[self.arm]['card']} only")
            ok, why = self.opening()
            if self.hung:
                self.say(f"smoke gate failed: {why}")
                rc = RC_HUNG
                return rc
            if not ok:
                self.say(f"smoke gate failed: {why}")
                rc = 16
                return rc
            self.say("smoke gate passed: the runs start" + (f" (without {', '.join(sorted(self.dropped))}: the probe)" if self.dropped else ""))
            seq = self.select(C.sequence(self.arm))
            for r in seq:
                if self.stopped():           # the operator's STOP file read before every start too (fix-e206)
                    self.queue.append({"n": r["n"], "run": C.run_key(r), "case": r["case"], "ran": False, "why": "after a stop: nothing further starts"})
                    continue
                self.queue.append(self.one_run(r))
                if not self.stopped() and not self.fresh() and not self.may_start(60) and not self.ensure_fresh_sampler():
                    self.stops.stop = self.stops.stop or "the sampler would not restart"
            if self.stopped():
                self.say(f"STOP: {self.stops.stop}: nothing further started")
            rc = RC_HUNG if self.hung else 0
            return rc
        except Exception as e:  # noqa: BLE001 -- a crash is named, then the closing runs (E202's fix)
            self.stops.stop = self.stops.stop or f"a crash of the runner ({type(e).__name__})"
            self.touch_stop()
            self.say(f"CRASH: {type(e).__name__}: {str(e)[:300]}")
            with open(os.path.join(self.out, "crash.txt"), "w") as f:
                f.write(traceback.format_exc())
            rc = 1
            return rc

    def closing(self, rc):
        """THE CLOSING, always: the sampler stopped (SIGTERM only), the closing config read (never after a HUNG, nor while the sampler
        would not stop), queue.json, "session end", the lock released, MANIFEST.sha256 last. Returns the session's exit."""
        a = self.a
        try:
            dl = self.close_deadline()
            stopped = self.stop_sampler(dl)
            # fix-e206 (the verifier's finding 4): a sampler left running earlier still holds the management node: no closing read then
            stopped = stopped and not any(q.poll() is None for q in self.left_samplers)
            if self.device_opened and self.t_first and not self.hung and stopped:
                cfg1, why = self.config("end", C.HOST_TIMEOUT_S + C.HANG_GRACE_S)
                self.say("config end: " + (json.dumps(cfg1) if cfg1 else why))
                if not self.hung:
                    tg, ids = N1.parse_ident(self.cfg_err.get("end", ""))
                    self.ident["config_end"] = {"targets": sorted({f"/dev/et{c}_{k}" for c, k in tg}), "ids": sorted(set(ids)),
                                                "minion_mv": (cfg1 or {}).get("minion_mv"), "runtime_cards": self.cfg_runtime.get("end", []),
                                                "why": N1.config_identity(self.arm, cfg1, self.cfg_err.get("end", "")) if cfg1 else why}
                    self.write_ident()
            elif self.hung:
                self.say("config end: not read (a device process of ours is HUNG: no further card command)")
            elif self.device_opened and not stopped:
                self.say("config end: not read (the sampler did not stop on SIGTERM: it still holds the management node)")
        except Exception as e:  # noqa: BLE001 -- the closing goes on to the manifest
            self.say(f"CRASH in the closing: {type(e).__name__}: {str(e)[:200]}")
            rc = 1 if rc in (0, 16) else rc
        if self.hung:
            rc = RC_HUNG
        self.tel_closed = True
        self.tel.close()
        tp = os.path.join(self.out, "telemetry.jsonl")
        if os.path.exists(tp):
            with open(tp, "rb") as fi, gzip.open(tp + ".gz", "wb") as fo:
                fo.write(fi.read())
            os.remove(tp)
        result = {"t0": a.t0, "arm": self.arm, "dry": self.dry, "queue": self.queue, "stop": self.stops.stop,
                  "t_first_ms": int(self.t_first * 1000) if self.t_first else None, "t_close_ms": now_ms(),
                  "end_bound_ms": int(self.close_deadline() * 1000) if self.t_first else None, "rest_die_c": self.rest_die,
                  "rest_board_w": self.rest_board, "card_min": round((time.time() - self.t_first) / 60, 2) if self.t_first else 0,
                  "runner": "run_e210.py", "identity_read_ok": self.ident_ok, "hung": self.hung, "rc": rc,
                  "samplers_left": [q.pid for q in self.left_samplers], "probe": self.probe, "dropped": self.dropped,
                  "sequence": self.a.sequence}
        with open(os.path.join(self.out, "queue.json"), "w") as fo:
            json.dump(result, fo, indent=1)
        self.say(f"session end (T0 {a.t0})")
        self.log_f.close()
        if self.lockf:
            self.lockf.close()
        write_manifest(self.out)
        self.manifest_written = True
        return rc


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
    ap.add_argument("--arm", choices=["A"], required=True)
    ap.add_argument("--t0", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--deadline-epoch", type=int, default=0)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--sequence", choices=["plan", "short", "two", "ties", "s2", "pass12", "cut"], default="plan")
    ap.add_argument("--rest-s", type=float, default=C.REST_READ_S)
    ap.add_argument("--smoke-rest-s", type=float, default=C.OPEN_REST_S)
    ap.add_argument("--tail-s", type=float, default=C.TAIL_S)
    ap.add_argument("--gate-wait-s", type=float, default=C.GATE_WAIT_S)
    ap.add_argument("--rule-s", type=float, default=C.CARD_RULE_S)
    ap.add_argument("--cap-s", type=float, default=C.CAP_S)
    a = ap.parse_args(argv)
    if not a.dry:
        changed = [n for n, v in (("--rest-s", a.rest_s != C.REST_READ_S), ("--smoke-rest-s", a.smoke_rest_s != C.OPEN_REST_S),
                                  ("--tail-s", a.tail_s != C.TAIL_S), ("--gate-wait-s", a.gate_wait_s != C.GATE_WAIT_S),
                                  ("--rule-s", a.rule_s != C.CARD_RULE_S), ("--cap-s", a.cap_s != C.CAP_S),
                                  ("--sequence", a.sequence != "plan")) if v]
        if changed:
            print(f"refused: {', '.join(changed)} change the registered session and are read with --dry only")
            return 2
        if os.environ.get("V3_DRY"):
            print("refused: V3_DRY is set but --dry is not")
            return 2
    s = Session(a)
    signal.signal(signal.SIGTERM, s.on_signal)
    return s.run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
