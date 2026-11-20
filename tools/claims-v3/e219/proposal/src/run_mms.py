#!/usr/bin/env python3
"""1119-mmsweep5: one card's session on its box, from a schedule (E190's runner form: tools/claims-v3/e190/run_e190_v2.py in
the public lab repo, adapted to a schedule of arms, three cards and this kit's folder). Python's own modules only.

    python3 -B src/run_mms.py session --card a2c0|a1c1|a1c0 --sched src/sched/<card>-<S>.json --t0 T0 --out sessions/<sid>
        [--deadline-epoch E]                                           a real session (started detached by src/start_mms.sh)
    python3 -B src/run_mms.py session --dry --scale 0.02 --card ... --sched ... --t0 T0 --out <dir>
        [--only N] [--trip-arm ID --trip-w W] [--config-fail] [--wrong-card] [--wrong-config] [--stop-after N]
        [--host-hang ARM] [--sampler-stall N] [--host-fail-after N] [--config-hang start|end] [--holder-after N]
        [--closing-holder]                                              the doubles, no device; every device call printed

What a session does, from the kit's root (~/claude/work/ee-1119-mmsweep5 on the box; every path it writes is relative to it):
  1. the box lock run/box.lock, its first act (flock -n, held to the end): src/start_mms.sh takes it before its own checks and
     hands it to the session (MMS_BOX_LOCK_FD: the same open file, so the lock is never free between the start's checks and the
     session's end); src/build_mms.sh and src/dry_mms.sh hold it while they run: never two sessions of this kit on one box (so
     never two of ours on aifoundry1), and no session beside the kit's build or dry pass;
  2. the box and the build: the hostname is the card's box; build/BUILD-mms.json written today by src/build_mms.sh on this box
     (BUILT; on aifoundry1 the host and /opt/et's device layer carry ET_DEVICES); the kernel ELF at E136's pin, the host and the
     reader at the sha256 the build recorded, every src/ file at src/SRC-SHA256SUMS (src/check_mms.py --box), the device-command
     audit GO (src/preflight_mms.sh --audit-only); else no device is opened; the kit's STOP file run/STOP and the session's STOP
     absent;
  3. the card's lock (/run/lock/etsoc-shire<N>.lock: root's, opened read-only, never created; flock -n, held for the whole
     session: its one sampler holds the card's mgmt node throughout; one retry after 15 s), then 3 s, then the holders: et-who
     (counts by card; another login on the card, aifoundry2 any card; any line of ours) and ps (a CI job; another device process
     of ours; on aifoundry2 another user's device process): one retry after 5 s; else no device opened;
  4. THE FIRST CARD COMMAND: `ettelem config` through src/guard_ettelem.sh under `timeout 10` (one re-run after 5 s if it fails:
     another reader may have had the node); it must be the config the card's plan rests on, and THE IDENTITY GATE:
     its stderr names the card's mgmt node and physical device ID (aifoundry1: minion_mv below 510 on card 1, at or above on
     card 0); the card time counts from it. A start read that fails either gate ends the session with NO closing read. A
     config read still running at its bound (30 s; at the closing 12-30 s) gets SIGTERM to its `timeout` wrapper and 30 s more
     (never SIGKILL): anything of it still alive then is a LEFTOVER (below), and the session makes no other read of the node;
  5. ONE sampler for the session (`ettelem sample --every-ms 100` through the guard), every line to telemetry.jsonl and to THE
     STOP LINES as it arrives (mms_common.Stops: the card's board line on 3 samples in a row; the die at 80 C; a risen latch);
     a trip touches the hosts' stop file at once (a running host ends at its next ~0.5 s launch boundary), nothing further
     starts; SIGTERM only, ever; a sampler that is not live is restarted only once it has stopped: a sampler of ours that will
     not stop on SIGTERM is never joined by a second one (the session ends; a leftover, below);
  6. THE STOP-PATH TEST: each line with a test threshold every live sample crosses must trip within 5 s, touch its own file and
     refuse a start; THE IDENTITY READ (et-who and the sampler's own open files: the card's mgmt node, nothing of ours off it);
  7. the opening rest: 60 s at rest (the session's rest die and board; the cards of aifoundry1 form their gate from it);
  8. THE SMOKE: one 2 s process a type (fp32 zeros, fp16 ones, int8 rnd at 1 x 1 x 4): rc 0, every launch ok, the check of C
     exact or approx, cycles an op inside 200-4,000, the host on the card (stderr or held nodes) and the board 2 W over the rest;
  9. the runs, in the schedule's order (anchors first, between blocks and last): each run waits for the die gate (at most
     180 s, a live sample), reads ps and et-who (before every run, on every card: E190's runner form), then its form: `burst`
     10 s at rest, ONE process `timeout 10 sparsity_host ... --seconds 6
     --budget 7.5`, 5 s at rest; `sus3` 20 s at rest, three such processes back to back, 20 s at rest; `null` 20 s at rest, a
     6.5 s window with no process, 20 s at rest (no device opened). No run starts once the card time passes the schedule's rule,
     or if its planned length would pass the cap less the closing or the window's last end; a started run is cut only by a
     stop. Two failed processes in a row (rc not 0, or the check of C not ok) stop the session;
 10. `timeout 10` sends a host SIGTERM at 10 s; a host still alive 30 s after it started gets the runner's SIGTERM to its
     `timeout` wrapper (which ignores it once it has sent its own; never SIGKILL); alive 30 s later it is
     a LEFTOVER: the session ends at once, makes no closing read, and holds the card's lock until no device process of ours is
     left (at most 10 minutes), recording it in queue.json and status.json;
 11. the closing (bounded by the cap from the first card command, E190's form): the sampler stopped (SIGTERM only); et-who and
     ps read once more, the sampler stopped; the closing config read (not after an identity trip, a stop for another holder, a
     failed start read or a leftover, and not when that last read shows a holder of another login on the card, a line of ours
     other than the session's own card lock, or a device process), "session end", the locks released, queue.json,
     MANIFEST.sha256 last.
No child process of the runner is ever sent SIGKILL: every bounded wait (the config reads, et-who, the box check, the hosts)
ends with SIGTERM and a grace, and what outlives it is left and recorded.
Every device command is a READ: the host opens the ops node only; `ettelem config` and `ettelem sample` through the guard,
which refuses every other word. Nothing is set: no clock, voltage, limit, firmware or governor; no reset; no statistics reset.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import fcntl
import gzip
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
import mms_common as C  # noqa: E402
import mms_ident as N  # noqa: E402

ROOT = C.ROOT
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
CI_COMM = re.compile(r"^Runner\.Worker$")


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def pacific_day():
    try:
        from zoneinfo import ZoneInfo
        import datetime
        return datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    except Exception:  # noqa: BLE001
        return time.strftime("%Y-%m-%d", time.localtime())


def rel(p):
    return os.path.relpath(os.path.abspath(p), ROOT)


def alive(pid):
    """A process that still runs (it exists and is not a zombie)."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().split(")")[-1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def take_box_lock(path, handed=None):
    """(descriptor, how) or (None, why): the kit's box lock, flock -n, held to the session's end. `handed` is the descriptor
    src/start_mms.sh took the lock on before its own checks and passed to the session (MMS_BOX_LOCK_FD): it must be that same
    file; flock on it is the lock it already holds (one open file), so the lock is never free between the start's checks and
    this session. Without it the file is opened here (a session started by hand)."""
    if handed:
        try:
            fd = int(handed)
            st, sp = os.fstat(fd), os.stat(path)
        except (ValueError, OSError) as e:
            return None, f"the box lock handed over (MMS_BOX_LOCK_FD={handed}) cannot be read ({type(e).__name__})"
        if (st.st_dev, st.st_ino) != (sp.st_dev, sp.st_ino):
            return None, f"the descriptor handed over (MMS_BOX_LOCK_FD={handed}) is not the kit's box lock"
        how = "held since src/start_mms.sh took it (handed over)"
    else:
        try:
            fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        except OSError as e:
            return None, f"the box lock cannot be opened ({type(e).__name__})"
        how = "taken"
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        if not handed:
            os.close(fd)
        return None, "the box lock is held (a session, build or dry pass of this kit runs on this box)"
    return fd, how


class Session:
    def __init__(self, a):
        self.a = a
        self.card = a.card
        self.K = C.CARDS[a.card]
        self.dry = a.dry
        self.scale = a.scale if a.dry else 1.0
        self.sched = C.load_sched(a.sched)
        if self.sched["card"] != a.card:
            raise ValueError(f"the schedule is card {self.sched['card']}'s, not {a.card}'s")
        T = self.sched["timing"]
        self.forms = self.sched["forms"]
        self.open_rest_s = T["open_rest_s"]
        self.gate_wait_s, self.rule_s, self.cap_s = T["gate_wait_s"], T["rule_min"] * 60.0, T["cap_min"] * 60.0
        P = self.sched["process"]
        self.seconds, self.budget = P["seconds"], P["budget"]
        self.out = os.path.abspath(a.out)
        os.makedirs(self.out, exist_ok=True)
        self.stop_file = os.path.join(self.out, "STOP")
        self.kit_stop = os.path.join(self.out, "KITSTOP") if a.dry else os.path.join(ROOT, C.KIT_STOP)   # --dry: its own stand-in
        self.log_f = open(os.path.join(self.out, "session.log"), "a")
        self.stops = C.Stops(**self.K["stops"], trip_file=self.stop_file)
        self.test_stops = None
        self.samples = []
        self.last = None
        self.last_rx = None
        self.lock = threading.Lock()
        self.sproc = None
        self.tel = open(os.path.join(self.out, "telemetry.jsonl"), "a")
        self.queue = []
        self.t_first = None
        self.device_opened = False
        self.start_ident_ok = False        # the start config read passed the config and identity gates (the closing read needs it)
        self.identity_tripped = False
        self.foreign_stop = False          # a stop for another holder or another device process on the card (no closing read then)
        self.leftover = []                 # device processes of ours alive when they should not be (recorded; never kill -9)
        self.failed_in_a_row = 0
        self.rest_die = self.rest_board = None
        self.cfg_err = {}
        self.ident = {}
        self.ident_ok = False
        self.env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
        self.env.pop("ET_DEVICES", None)
        self.env.pop("V3_DEVICE", None)
        self.env.pop("MMS_BOX_LOCK_FD", None)            # the session's own; its children never see the box lock
        if self.K["et_devices"] is not None:
            self.env["ET_DEVICES"] = self.K["et_devices"]
        self.dev_dir = os.path.join(self.out, "fakedev") if self.dry else N.DEV_DIR
        if self.dry:
            os.makedirs(self.dev_dir, exist_ok=True)
            for k in ("ops", "mgmt"):
                for c in ("0", "1"):
                    open(os.path.join(self.dev_dir, f"et{c}_{k}"), "a").close()
            open(os.path.join(self.dev_dir, "card.lock"), "a").close()
            self.env.update(MMS_FAKE_CARD=a.card, MMS_FAKE_DIR=self.dev_dir, MMS_FAKE_SCALE=str(self.scale))
            if a.trip_arm:
                self.env.update(MMS_FAKE_TRIP=str(a.trip_w), MMS_FAKE_TRIP_ARM=a.trip_arm)
            if a.config_fail:
                self.env["MMS_FAKE_CONFIG_FAIL"] = "1"
            if a.wrong_card:
                self.env["MMS_FAKE_WRONG_CARD"] = "1"
            if a.host_hang:
                self.env["MMS_FAKE_HOST_HANG_ARM"] = a.host_hang
            if a.sampler_stall:
                self.env["MMS_FAKE_SAMPLER_STALL"] = str(a.sampler_stall)
            if a.wrong_config:
                self.env["MMS_FAKE_WRONG_CONFIG"] = "1"
            if a.host_fail_after:
                self.env["MMS_FAKE_HOST_FAIL_AFTER"] = str(a.host_fail_after)
            if a.config_hang:
                self.env["MMS_FAKE_CONFIG_HANG"] = a.config_hang
            if a.holder_after:
                self.env["MMS_FAKE_HOLDER_AFTER"] = str(a.holder_after)
            if a.closing_holder:
                self.env["MMS_FAKE_CLOSING_HOLDER"] = "1"
            self.calls = open(os.path.join(self.out, "device-calls.txt"), "a")
        for p in (self.stop_file,):
            if os.path.exists(p):
                os.remove(p)

    # ------------------------------------------------------------------ log and the device calls
    def say(self, words):
        line = f"{stamp()} {'DRY ' if self.dry and not words.startswith('session start') else ''}{words}"
        self.log_f.write(line + "\n")
        self.log_f.flush()
        print(line, flush=True)

    def device_call(self, real):
        """The command a real session runs (printed and kept under --dry); under --dry the double that replaces it."""
        if not self.dry:
            return real
        self.calls.write(" ".join(real) + "\n")
        self.calls.flush()
        print("DRY DEVICE CALL: " + " ".join(real), flush=True)
        fake = [sys.executable, "-B", os.path.join(HERE, "fake_card_mms.py")]
        if real[-1] == "config" and real[0] == "timeout":          # the same tree as the real read: `timeout 10` over the reader
            return ["timeout", str(C.HOST_TIMEOUT_S)] + fake + ["config"]
        if "sample" in real:
            return fake + ["sample"] + real[real.index("sample") + 1:]
        if real[0] == "timeout" and real[2] == C.HOST:
            return ["timeout", str(C.HOST_TIMEOUT_S)] + fake + ["host"] + real[3:]
        raise ValueError(f"no double for {real}")

    def wait(self, seconds):
        time.sleep(max(0.0, seconds * self.scale))

    def cmd_config(self):
        return self.device_call(["timeout", str(C.HOST_TIMEOUT_S), "bash", C.GUARD, self.card, "config"])

    def cmd_sampler(self, seconds):
        return self.device_call(["bash", C.GUARD, self.card, "sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)])

    def cmd_etwho(self):
        if self.dry:
            return [sys.executable, "-B", os.path.join(HERE, "fake_card_mms.py"), "etwho"]
        return ["timeout", "20", "et-who"]

    def host_cmd(self, argv):
        return self.device_call(["timeout", str(C.HOST_TIMEOUT_S)] + argv)

    # ------------------------------------------------------------------ a bounded child process (never SIGKILL)
    def bounded(self, cmd, bound_s, grace_s, env=None):
        """Run cmd from the kit's root (stdin /dev/null, stdout and stderr to pipes) and wait at most bound_s. Past the bound:
        SIGTERM to our direct child (a `timeout` wrapper ignores it once it has sent its own SIGTERM, at its limit, to the process
        under it) and grace_s more; whatever of the child's tree still runs then is LEFT: our ends of its pipes are closed and
        nothing else is done to it (never SIGKILL, never kill -9). -> (rc or None, stdout, stderr, the pids left running)."""
        try:
            p = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, errors="replace", env=env)
        except OSError as e:
            return None, "", type(e).__name__, []
        try:
            out, err = p.communicate(timeout=bound_s)
            return p.returncode, out or "", err or "", []
        except subprocess.TimeoutExpired:
            pass
        tree = N.descendants(p.pid)
        try:
            p.send_signal(signal.SIGTERM)
        except OSError:
            pass
        try:
            out, err = p.communicate(timeout=grace_s)
            return (p.returncode if p.returncode is not None else 124), out or "", err or "", [x for x in tree if alive(x)]
        except subprocess.TimeoutExpired:
            pass
        left = [x for x in tree if alive(x)]
        for fh in (p.stdout, p.stderr):
            try:
                fh.close()
            except OSError:
                pass
        return None, "", "", left

    # ------------------------------------------------------------------ holders (counts, never names)
    def etwho_lines(self):
        rc, out, _, left = self.bounded(self.cmd_etwho(), 30, C.ETWHO_GRACE_S, env=self.env)
        if left:
            self.mark("etwho_left", f"{len(left)} process(es) of an et-who read still running after its bound and SIGTERM "
                                    "(et-who never opens a card node; left, not killed)")
            self.say(f"an et-who read did not end within its bound and SIGTERM: {len(left)} process(es) left running (et-who "
                     "opens no card node; never killed)")
        if rc is None:
            return [], "et-who unreadable (TimeoutExpired)"
        if rc != 0:          # plain et-who exits 0 whenever it read the holders (sudo's own failure is 1, `timeout 20`'s 124)
            return [], f"et-who unreadable (rc {rc})"
        return out.splitlines(), ""

    def ps_block(self):
        """'' when no process blocks the card, else why (counts only): a CI job; another device process of ours (not this
        session's sampler or host); on aifoundry2 another user's device process."""
        if self.dry:
            return ""
        mine = {os.getpid()} | ({self.sproc.pid} if self.sproc is not None else set())
        uid = os.getuid()
        n_oth = n_ci = n_ours = 0
        out = subprocess.run(["ps", "-eo", "uid=,pid=,ppid=,state=,comm="], capture_output=True, text=True).stdout.splitlines()
        for ln in out:
            f = ln.split(None, 4)
            if len(f) != 5:
                continue
            try:
                u, pid, ppid = int(f[0]), int(f[1]), int(f[2])
            except ValueError:
                continue
            comm = f[4].strip()
            if f[3].upper().startswith("Z") or pid in mine or ppid in mine:
                continue
            if CI_COMM.search(comm):
                n_ci += 1
            elif DEV_COMM.search(comm) and u == uid:
                n_ours += 1
            elif DEV_COMM.search(comm) and C.OTHER_CARD_ON_BOX[self.card] is None:
                n_oth += 1
        why = [x for x, n in ((f"{n_ci} CI job(s)", n_ci), (f"{n_ours} other device process(es) of ours", n_ours),
                              (f"{n_oth} other users' device process(es)", n_oth)) if n]
        return "; ".join(why)

    def holders(self, with_etwho=True, form=None):
        """'' when nothing blocks, else why (counts only). form 'block' (no device of ours open: before the first card command,
        and right before the closing read once the sampler has stopped): N.etwho_block; form 'run' (the sampler running):
        N.etwho_identity. Default: 'block' before the first card command, 'run' after it."""
        me = pwd.getpwuid(os.getuid()).pw_name if not self.dry else (os.environ.get("USER") or str(os.getuid()))
        form = form or ("block" if self.t_first is None else "run")
        why = []
        if with_etwho:
            lines, err = self.etwho_lines()
            if err:
                return err
            b = N.etwho_block(self.card, lines, me) if form == "block" else self._etwho_during(lines, me)
            if b:
                why.append(b)
        p = self.ps_block()
        if p:
            why.append(p)
        return "; ".join(why)

    def _etwho_during(self, lines, me):
        why, _ = N.etwho_identity(self.card, lines, me)
        return why

    # ------------------------------------------------------------------ the sampler and the stop lines
    def _reader(self, proc):
        for raw in proc.stdout:
            if not raw.startswith("{"):
                continue
            try:
                s = json.loads(raw)
            except ValueError:
                continue
            self.tel.write(raw if raw.endswith("\n") else raw + "\n")
            self.tel.flush()
            with self.lock:
                self.samples.append((s.get("t_ms", 0), raw.rstrip("\n")))
                self.last = s
                self.last_rx = time.time()
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
        """The session's end bound (E190's): the cap from the first card command."""
        return self.t_first + self.cap_s * self.scale if self.t_first else None

    def start_sampler(self):
        secs = self.cap_s + 600
        for attempt in (1, 2, 3):
            if attempt > 1 and self.may_start(60):
                break
            if self.sampler_alive():
                self.say("a sampler of ours is still alive: no other sampler is started beside it")
                return False
            err = open(os.path.join(self.out, "sampler.err"), "a")
            self.sproc = subprocess.Popen(self.cmd_sampler(secs), cwd=ROOT, stdout=subprocess.PIPE, stderr=err,
                                          stdin=subprocess.DEVNULL, text=True, env=self.env)
            n0 = len(self.samples)
            threading.Thread(target=self._reader, args=(self.sproc,), daemon=True).start()
            t = time.time()
            while time.time() - t < 10:
                if len(self.samples) > n0:
                    self.say(f"sampler started (attempt {attempt}, pid {self.sproc.pid}, every {C.EVERY_MS} ms)")
                    if self.ident_ok:
                        nodes = N.proc_nodes(self.sproc.pid, self.dev_dir)
                        wrong = sorted(f"/dev/et{c}_{k}" for c, k in nodes if c != self.K["card"])
                        self.ident.setdefault("sampler_restarts", []).append(sorted(f"/dev/et{c}_{k}" for c, k in nodes))
                        if wrong:
                            self.identity_trip(f"the restarted sampler holds {wrong}")
                    return True
                if self.sproc.poll() is not None:
                    break
                time.sleep(0.1)
            if not self.stop_sampler(self.close_deadline()):
                self.note_leftover("sampler", "a sampler that sent no sample did not stop on SIGTERM")
                return False
            time.sleep(2)
        return False

    def sampler_alive(self):
        return self.sproc is not None and self.sproc.poll() is None

    def stop_sampler(self, deadline=None):
        """SIGTERM only (never kill -9 a tool): 30 s, then once more and 60 s, each wait ending CLOSE_S / 2 before the end bound
        but lasting at least 2 s (E190's form; scaled under --dry); a sampler that will not stop stays recorded in self.sproc_left
        and the session treats it as a leftover (no other sampler, no closing read beside it)."""
        p = self.sproc
        if not p:
            return True
        for n, w in enumerate((30.0, 60.0)):
            if p.poll() is None:
                w = w * self.scale if self.dry else w
                if deadline:
                    w = min(w, max(2.0 * (self.scale if self.dry else 1.0), deadline - C.CLOSE_S * self.scale / 2 - time.time()))
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=w)
                except subprocess.TimeoutExpired:
                    if n == 0:
                        self.say(f"the sampler did not stop within {w:.0f} s of SIGTERM: SIGTERM once more")
                    continue
            break
        ok = p.poll() is not None
        if not ok:
            self.say("the sampler did not stop on SIGTERM: left running, recorded (no kill -9)")
            self.sproc_left = p
        self.sproc = None
        return ok

    def fresh(self):
        """The sampler is live: alive, with a sample received less than 2 s ago (under --dry: 0.5 s or 2 s x the scale)."""
        with self.lock:
            rx = self.last_rx
        limit = C.SAMPLE_FRESH_S if not self.dry else max(0.5, C.SAMPLE_FRESH_S * self.scale)
        return self.sampler_alive() and rx is not None and (time.time() - rx) < limit

    def staleness(self):
        with self.lock:
            rx = self.last_rx
        return f"alive {self.sampler_alive()}, last sample {'never' if rx is None else '%.1f s ago' % (time.time() - rx)}"

    def ensure_fresh_sampler(self):
        if self.fresh():
            return True
        why = self.may_start(60)
        if why:
            self.say(f"the sampler is not live ({self.staleness()}); not restarted: no run can start ({why})")
            return False
        self.say(f"the sampler is not live ({self.staleness()}): restarting it")
        if self.sampler_alive() and not self.stop_sampler(self.close_deadline()):
            self.note_leftover("sampler", "a stale sampler did not stop on SIGTERM: no second sampler is started beside it")
            self.stops.stop = self.stops.stop or "a sampler of ours would not stop on SIGTERM: the session ends"
            return False
        return self.start_sampler()

    def note_leftover(self, what, why, pids=None):
        rec = {"t_ms": now_ms(), "what": what, "why": why, "pids": sorted(pids or [])}
        self.leftover.append(rec)
        self.mark("leftover", why, what=what)
        self.say(f"LEFTOVER: {why} (recorded; never kill -9; the card's lock stays held until no device process of ours is left)")

    def ours_alive(self):
        """Device processes of ours still alive: the leftover process trees this session started (by pid), and under a real
        session every process of our login whose name is a device tool's (ps), the session's own live sampler aside."""
        n = 0
        for rec in self.leftover:
            n += sum(1 for pid in rec["pids"] if alive(pid))
        sl = getattr(self, "sproc_left", None)
        if sl is not None and sl.poll() is None:
            n += 1
        if not self.dry:
            mine = {os.getpid()} | ({self.sproc.pid} if self.sproc is not None else set())
            out = subprocess.run(["ps", "-eo", "uid=,pid=,state=,comm="], capture_output=True, text=True).stdout.splitlines()
            for ln in out:
                f = ln.split(None, 3)
                if len(f) == 4 and f[0] == str(os.getuid()) and not f[2].upper().startswith("Z") and int(f[1]) not in mine \
                        and DEV_COMM.search(f[3].strip()):
                    n += 1
        return n

    def identity_trip(self, why):
        self.identity_tripped = True
        try:
            with open(self.stop_file, "a"):
                os.utime(self.stop_file, None)
        except OSError:
            pass
        self.stops.stop = self.stops.stop or f"identity: {why}"
        self.mark("identity_trip", why)

    def latest(self):
        with self.lock:
            return dict(self.last) if self.last else None

    def write_status(self, n_total, closing=None, leftover=None):
        """status.json, for src/status_mms.sh: the session's progress after each run, and its closing (replaced whole each time)."""
        s = self.latest() or {}
        st = {"t0": self.a.t0, "card": self.card, "card_min": round(self.card_time() / 60, 2), "runs_total": n_total,
              "runs_done": len(self.queue), "runs_ran": sum(1 for q in self.queue if q.get("ran")), "stop": self.stops.stop,
              "last_run": self.queue[-1] if self.queue else None, "rest_die_c": self.rest_die,
              "last_sample": {"board_w": s.get("board_w"), "die_c": C.die_of(s) if s else None,
                              "minion_mhz": (s.get("mhz") or {}).get("minion")},
              "closing": closing, "leftover": leftover if leftover is not None else (self.leftover or None)}
        tmp = os.path.join(self.out, "status.json.tmp")
        with open(tmp, "w") as f:
            json.dump(st, f, indent=1)
        os.replace(tmp, os.path.join(self.out, "status.json"))

    def window(self, t0_ms, t1_ms):
        with self.lock:
            return [json.loads(ln) for (t, ln) in self.samples if t0_ms <= t <= t1_ms]

    def stop_requested(self):
        """The operator's stop (run/STOP or the session's STOP) is the hosts' stop file: copied to the session's at once."""
        if os.path.exists(self.kit_stop) and not os.path.exists(self.stop_file):
            open(self.stop_file, "a").close()
        if os.path.exists(self.stop_file) and not self.stops.stop:
            self.stops.stop = "the operator's STOP file"
            self.mark("operator_stop", "STOP file present")
        return bool(self.stops.stop)

    def nap(self, seconds):
        """Sleep (scaled under --dry), watching the stops; False at once if one tripped (a process then does not start)."""
        end = time.time() + seconds * self.scale
        while time.time() < end:
            if self.stop_requested():
                return False
            time.sleep(min(0.2 * max(self.scale, 0.05), max(0.0, end - time.time())))
        return not self.stop_requested()

    def idle(self, seconds):
        """The read after a run's process: it runs to its end whatever the stop lines say (no launch happens in it)."""
        end = time.time() + seconds * self.scale
        while time.time() < end:
            time.sleep(min(0.2, max(0.0, end - time.time())))

    # ------------------------------------------------------------------ the rules
    def card_time(self):
        return (time.time() - self.t_first) / self.scale if self.t_first else 0.0

    def may_start(self, seconds):
        if self.stop_requested() or (self.test_stops is not None and self.test_stops.stop):
            return "a stop line has tripped or a STOP file is present"
        el = self.card_time()
        if el > self.rule_s:
            return f"the card-time rule: {el / 60:.1f} card-minutes (no run after {self.rule_s / 60:g})"
        if el + seconds > self.cap_s - C.CLOSE_S:
            return f"the cap: {el / 60:.1f} card-minutes + {seconds:.0f} s would pass {self.cap_s / 60:g} less the closing"
        if self.a.deadline_epoch and time.time() + seconds * self.scale + 90 * self.scale > self.a.deadline_epoch:
            return "the window's last end is too close"
        return ""

    def die_gate(self, gate, planned):
        t = time.time()
        while True:
            s = self.latest() if self.fresh() else None
            die = C.die_of(s) if s else None
            if die is not None and gate is not None and die <= gate:
                return True, die, (time.time() - t) / self.scale, ""
            why = self.may_start(planned)
            if why:
                return False, die, (time.time() - t) / self.scale, why
            if (time.time() - t) / self.scale >= self.gate_wait_s:
                return False, die, (time.time() - t) / self.scale, ""
            if not self.ensure_fresh_sampler():
                return False, die, (time.time() - t) / self.scale, "the sampler is not live"
            time.sleep(max(0.01, 0.5 * self.scale))

    # ------------------------------------------------------------------ reads
    def config(self, name, bound_s=30):
        """The config read (the guard under `timeout 10`), waited for at most bound_s, then SIGTERM to its wrapper and TERM_GRACE_S
        more (never SIGKILL). Anything of it still running then holds or may hold the card's mgmt node: a LEFTOVER, the session
        ends at once and reads the node no more (no re-run, no closing read), the card's lock held until it is gone."""
        rc, out, err, left = self.bounded(self.cmd_config(), bound_s, C.TERM_GRACE_S, env=self.env)
        j = C.last_json(out)
        with open(os.path.join(self.out, f"config-{name}.json"), "w") as f:
            f.write(json.dumps(j) + "\n")
        self.cfg_err[name] = err
        with open(os.path.join(self.out, f"config-{name}.err"), "w") as f:
            f.write(err)
        if left:
            self.note_leftover("config-read", f"the {name} config read outlived its {bound_s:.0f} s bound and then SIGTERM to its "
                                         f"wrapper by {C.TERM_GRACE_S:.0f} s", left)
            self.stops.stop = self.stops.stop or "a config read of ours outlived its bound: the session ends at once"
            try:
                with open(self.stop_file, "a"):
                    os.utime(self.stop_file, None)
            except OSError:
                pass
            return None, f"config read ({name}) left {len(left)} process(es) running past its bound (a leftover)"
        if rc is None:
            return None, "config read failed (TimeoutExpired)"
        if rc != 0 or not j:
            return None, f"config read rc {rc}, no JSON line"
        return j, ""

    def write_ident(self):
        with open(os.path.join(self.out, "identity.json"), "w") as f:
            json.dump(self.ident, f, indent=1, sort_keys=True)

    def identity_read(self):
        me = pwd.getpwuid(os.getuid()).pw_name if not self.dry else (os.environ.get("USER") or str(os.getuid()))
        lines, err = self.etwho_lines()
        why_e, counts = N.etwho_identity(self.card, lines, me) if not err else (err, {})
        nodes = N.proc_nodes(self.sproc.pid, self.dev_dir) if self.sproc is not None else set()
        c = self.K["card"]
        why_s = []
        if (c, "mgmt") not in nodes:
            why_s.append(f"the sampler does not hold {C.node(self.card, 'mgmt')}")
        off = sorted(f"/dev/et{x}_{k}" for x, k in nodes if x != c)
        if off:
            why_s.append(f"the sampler holds {off}")
        self.ident["etwho_with_sampler"] = {"counts": counts, "why": why_e}
        self.ident["sampler_nodes"] = {"nodes": sorted(f"/dev/et{x}_{k}" for x, k in nodes), "why": "; ".join(why_s)}
        with open(os.path.join(self.out, "etwho-identity.txt"), "w") as f:
            f.write(f"et-who with the sampler running (counts by card; no login): {json.dumps(counts, sort_keys=True)}; "
                    f"{why_e or 'ok'}\nthe sampler's own nodes: {self.ident['sampler_nodes']['nodes']}; {'; '.join(why_s) or 'ok'}\n")
        why = "; ".join(x for x in [why_e] + why_s if x)
        self.ident_ok = not why
        self.write_ident()
        return not why, why

    # ------------------------------------------------------------------ one host process
    def run_proc(self, argv, d, name):
        os.makedirs(d, exist_ok=True)
        errp = os.path.join(d, name + ".err")
        t0 = now_ms()
        with open(os.path.join(d, name + ".out"), "w") as so, open(errp, "w") as se:
            p = subprocess.Popen(self.host_cmd(argv), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=self.env)
            watch = N.HostWatch(self.card, p.pid, errp, self.dev_dir, on_wrong=self.identity_trip)
            watch.start()
            try:
                rc = p.wait(timeout=C.HOST_TIMEOUT_S + 20)
            except subprocess.TimeoutExpired:
                # alive 30 s after it started: `timeout 10` sent the host SIGTERM at 10 s; SIGTERM to our own `timeout` too (it
                # ignores it once it has sent its own), never SIGKILL; still alive 30 s later, the tree is a leftover and the
                # session ends at once
                tree = N.descendants(p.pid)
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    pass
                rc = 124
                alive = [x for x in tree if os.path.exists(f"/proc/{x}")]
                if alive or p.poll() is None:
                    self.note_leftover("host", f"a host process outlived `timeout {C.HOST_TIMEOUT_S}` by 20 s and then SIGTERM by 30 s",
                                       alive + ([p.pid] if p.poll() is None else []))
                    self.stops.stop = self.stops.stop or "a device process of ours outlived its timeout: the session ends at once"
                    try:
                        with open(self.stop_file, "a"):
                            os.utime(self.stop_file, None)
                    except OSError:
                        pass
            watch.finish()
        t1 = now_ms()
        self.device_opened = True
        text = open(os.path.join(d, name + ".out")).read()
        sp = C.parse_sparsity(text)
        chk = [x for x in sp if x.get("test") == "check"]
        fma = [x for x in sp if x.get("test") == "fma"]
        lw = [x for x in fma if x.get("t_start_ms") and x.get("t_end_ms") and (x.get("launch") or 0) >= 0]
        return {"name": name, "argv": argv, "rc": rc, "t0_ms": t0, "t1_ms": t1, "n_launch": len(fma),
                "launches_ok": bool(fma) and all(x.get("ok") for x in fma),
                "check": chk[-1].get("result") if chk else None, "check_ok": bool(chk) and bool(chk[-1].get("ok")),
                "check_cycles_per_op": chk[-1].get("cycles_per_op") if chk else None,
                "stopped_by_file": "stopping:" in open(errp).read(),
                "launch_window_ms": [min(x["t_start_ms"] for x in lw), max(x["t_end_ms"] for x in lw)] if lw else None,
                "ident": watch.result()}

    # ------------------------------------------------------------------ the stop-path test
    def stop_path_test(self):
        res = {}
        st = self.K["stops"]
        for line, kw in (("board", {"board_cap_w": 0.0, "cap_consecutive": st["cap_consecutive"], "abs_stop_c": 999.0}),
                         ("die", {"board_cap_w": 999.0, "cap_consecutive": st["cap_consecutive"], "abs_stop_c": 0.0})):
            tf = os.path.join(self.out, f"STOPTEST-{line}")
            self.test_stops = C.Stops(**kw, trip_file=tf)
            t = time.time()
            while time.time() - t < 5 and not self.test_stops.stop:
                time.sleep(0.05)
            tripped = bool(self.test_stops.stop)
            refused = bool(self.may_start(0))
            res[line] = {"tripped": tripped, "why": self.test_stops.stop, "test_file_touched": os.path.exists(tf),
                         "refused_a_start": refused, "s": round(time.time() - t, 2)}
            self.test_stops = None
        ok = all(v["tripped"] and v["refused_a_start"] and v["test_file_touched"] for v in res.values()) and not self.stops.stop \
            and not os.path.exists(self.stop_file)
        with open(os.path.join(self.out, "stop-path.json"), "w") as f:
            json.dump({"ok": ok, "lines": res, "real_lines": st}, f, indent=1)
        return ok, res

    # ------------------------------------------------------------------ the opening rest and the smoke
    def opening_rest(self):
        t0 = now_ms()
        self.say(f"the opening rest: {self.open_rest_s:g} s at rest (the card at rest; the session's rest die)")
        ok = self.nap(self.open_rest_s)
        win = self.window(t0, now_ms())
        dies = [C.die_of(s) for s in win if C.die_of(s) is not None]
        bws = [s.get("board_w") for s in win if s.get("board_w") is not None]
        self.rest_die = statistics.median(dies) if dies else None
        self.rest_board = statistics.median(bws) if bws else None
        rest = {"t0_ms": t0, "t1_ms": now_ms(), "samples": len(win), "board_w_median": self.rest_board,
                "die_median_c": self.rest_die, "gate_c": C.gate_c(self.card, self.rest_die)}
        with open(os.path.join(self.out, "rest.json"), "w") as f:
            json.dump(rest, f, indent=1)
        self.say(f"the opening rest: {len(win)} samples, board {self.rest_board} W, die {self.rest_die} C; gate {rest['gate_c']} C")
        if not ok:
            return False, f"a stop during the opening rest: {self.stops.stop}"
        if not win or self.rest_die is None or rest["gate_c"] is None:
            return False, "no live sample in the opening rest"
        return True, ""

    def smoke(self):
        d0 = os.path.join(self.out, "smoke")
        P = self.sched["process"]
        for r in self.sched["smoke"]:
            why = self.may_start(15)
            if why:
                return False, f"{r['arm']}: not started ({why})"
            if not self.fresh():
                return False, f"{r['arm']}: not started (the sampler is not live: {self.staleness()})"
            pre = now_ms()
            if not self.nap(5):
                return False, f"a stop before the smoke's {r['arm']}"
            pre_w = [s["board_w"] for s in self.window(pre, now_ms()) if s.get("board_w") is not None]
            rest_w = statistics.median(pre_w) if pre_w else self.rest_board
            argv = C.host_argv(r, P["smoke_seconds"], P["smoke_budget"], rel(self.stop_file))
            p = self.run_proc(argv, os.path.join(d0, r["arm"]), "proc")
            idn = p["ident"]
            id_ok = not idn["wrong"] and idn["right"]
            win = self.window(*p["launch_window_ms"]) if p["launch_window_ms"] else []
            rise_ok, rise, n_rise = N.board_rise(win, p["launch_window_ms"], rest_w)
            cpo = p["check_cycles_per_op"]
            good = p["rc"] == 0 and p["launches_ok"] and p["check"] in ("exact", "approx") and p["check_ok"] and \
                cpo is not None and C.CYC_LO <= cpo <= C.CYC_HI and id_ok and rise_ok
            with open(os.path.join(d0, r["arm"], "smoke.json"), "w") as fo:
                json.dump(dict(p, identity_ok=id_ok, board_rise={"ok": rise_ok, "rise_w": rise, "samples": n_rise, "rest_w": rest_w},
                               good=good), fo, indent=1)
            self.ident.setdefault("smoke", {})[r["arm"]] = {"host": idn, "board_rise_w": rise}
            self.write_ident()
            self.say(f"smoke {r['arm']}: rc {p['rc']}, {p['n_launch']} launches, check {p['check']}, cycles an op {cpo}; the host's "
                     f"card: {'its own' if id_ok else ('ANOTHER: ' + '; '.join(idn['wrong']) if idn['wrong'] else 'NOT SEEN')}; "
                     f"the board {rise} W over its rest on {n_rise} samples: {'ok' if good else 'FAILED'}")
            if not good:
                return False, f"{r['arm']}: rc {p['rc']}, check {p['check']}, cycles {cpo}, card {'ok' if id_ok else 'not seen or another'}, rise {rise}"
            if self.stops.stop:
                return False, f"a stop during the smoke: {self.stops.stop}"
        return True, ""

    # ------------------------------------------------------------------ one run
    def one_run(self, r):
        key = f"{r['i']:03d}-{r['arm']}"
        d = os.path.join(self.out, "runs", key)
        planned = r["est_s"]
        F = self.forms[r["form"]]
        base = {"i": r["i"], "block": r["block"], "role": r["role"], "arm": r["arm"], "run": key, "form": r["form"]}
        if r["est_peak_w"] > self.K["line_w"]:
            return dict(base, ran=False, why=f"its estimate {r['est_peak_w']} W is over the card's line {self.K['line_w']} W")
        why = self.may_start(planned)
        if why:
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        gate = C.gate_c(self.card, self.rest_die)
        ok, die, waited, gwhy = self.die_gate(gate, planned)
        if not ok:
            w = gwhy or f"the die gate: {die} C after {waited:.0f} s (gate {gate} C)"
            self.say(f"run {key}: not started ({w}): no data")
            return dict(base, ran=False, why=w, gate={"c": gate, "die": die, "waited_s": round(waited, 1)})
        why = self.may_start(planned)
        if why:
            self.say(f"run {key}: not started ({why}): no data")
            return dict(base, ran=False, why=why)
        # et-who and ps before every run, on every card (E190's runner form): another login on the card (aifoundry2: on any
        # card), a line of ours off the card, the sampler's line missing, or another device process stops the session
        h = self.holders(with_etwho=True)
        if h:
            self.stops.stop = self.stops.stop or f"a holder or a device process: {h}"
            self.foreign_stop = True
            self.say(f"STOP before run {key}: {h}")
            return dict(base, ran=False, why=h)
        if not self.fresh():
            self.say(f"run {key}: the sampler is not live ({self.staleness()}): no data")
            return dict(base, ran=False, why="the sampler is not live")
        os.makedirs(d, exist_ok=True)
        self.say(f"run {key}: {r['role']} {r['arm']} ({r['form']}; gate {gate} C, die {die} C after {waited:.0f} s)")
        r0 = now_ms()
        clean = self.nap(F["rest_s"])
        r1 = now_ms()
        rec = dict(base, sched=r, gate={"c": gate, "die": die, "waited_s": round(waited, 1)}, rest={"t0_ms": r0, "t1_ms": r1},
                   procs=[], flags=[])
        if not clean:
            rec.update(ran=False, why="stop: " + str(self.stops.stop))
        elif r["form"] == "null":
            # a null run: the same windows with no process (no device is opened); the reducer reads it as a run
            w0 = now_ms()
            self.idle(F["window_s"])
            w1 = now_ms()
            self.idle(F["tail_s"])
            rec.update(ran=True, null={"t0_ms": w0, "t1_ms": w1}, work={"t0_ms": w0, "t1_ms": w1}, tail={"t0_ms": w1, "t1_ms": now_ms()})
        else:
            argv = C.host_argv(r, self.seconds, self.budget, rel(self.stop_file))
            for n in range(F["nproc"]):
                if n and (self.stops.stop or self.stop_requested()):
                    rec["flags"].append(f"a stop after process {n} of {F['nproc']}: the rest not started")
                    break
                p = self.run_proc(argv, d, f"proc-{n:02d}")
                rec["procs"].append(p)
                if not p["ident"]["right"] and not p["ident"]["wrong"]:
                    rec["flags"].append(f"proc-{n:02d}: the host's card was not seen on its stderr or in its open files (reported)")
                if p["rc"] != 0:
                    rec["flags"].append(f"proc-{n:02d}: process rc {p['rc']}")
                failed = p["rc"] != 0 or p["check"] not in ("exact", "approx") or not p["check_ok"]
                self.failed_in_a_row = self.failed_in_a_row + 1 if failed else 0
                if self.failed_in_a_row >= C.FAILED_IN_A_ROW:
                    self.stops.stop = self.stops.stop or f"{C.FAILED_IN_A_ROW} failed processes in a row (rc not 0, or the check of C not ok)"
                if self.leftover:
                    break
            w1 = now_ms()
            if not self.leftover:
                self.idle(F["tail_s"])
            rec.update(ran=True, work={"t0_ms": rec["procs"][0]["t0_ms"], "t1_ms": w1}, tail={"t0_ms": w1, "t1_ms": now_ms()})
        if self.stops.stop:
            rec["flags"].append(f"a stop: {self.stops.stop}")
        with open(os.path.join(d, "run.json"), "w") as fo:
            json.dump(rec, fo, indent=1)
        pr = rec["procs"][-1] if rec["procs"] else {}
        self.say(f"run {key} done: {len(rec['procs'])} process(es), rc {pr.get('rc')}, {sum(p.get('n_launch') or 0 for p in rec['procs'])} "
                 f"launches, check {pr.get('check')}{', ' + '; '.join(rec['flags']) if rec['flags'] else ''}")
        return dict(base, ran=bool(rec.get("ran")), rc=pr.get("rc") if rec["procs"] else None,
                    rcs=[p["rc"] for p in rec["procs"]], check=pr.get("check"),
                    checks=[p["check"] for p in rec["procs"]], flags=rec["flags"])

    # ------------------------------------------------------------------ the box and the build (never under --dry)
    def box_check(self):
        host = socket.gethostname().split(".")[0]
        if host != self.K["box"]:
            return f"this host is {host!r}, not {self.card}'s {self.K['box']!r}"
        try:
            rec = C.load(os.path.join(ROOT, C.BUILD_REC))
        except (OSError, ValueError):
            return f"no build record {C.BUILD_REC}: run src/build_mms.sh first"
        bad = []
        if rec.get("day") != pacific_day() or rec.get("verdict") != "BUILT" or rec.get("box") != self.K["box"]:
            bad.append(f"the build record is not today's BUILT on {self.K['box']} ({rec.get('day')}, {rec.get('verdict')}, {rec.get('box')})")
        if self.K["et_devices"] is not None and rec.get("et_devices") != "the host, the reader and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES":
            bad.append(f"the build record does not say the host and the reader honour ET_DEVICES ({rec.get('et_devices')})")
        for relp, want in ((C.ELF, C.KERNEL_PIN), (C.HOST, rec.get("host_sha256")), (C.ETTELEM, rec.get("ettelem_sha256"))):
            p = os.path.join(ROOT, relp)
            got = C.sha256(p) if os.path.isfile(p) else None
            if got is None or got != want:
                bad.append(f"{relp}: sha256 {got}, want {want}")
        if bad:
            return "; ".join(bad)
        for name, cmd, want in (("harness", [sys.executable, "-B", os.path.join(HERE, "check_mms.py"), "--box"], "HARNESS OK"),
                                ("preflight", ["bash", os.path.join(HERE, "preflight_mms.sh"), self.card, "--audit-only"],
                                 "dmcmd_audit: GO")):
            rc, out, err, left = self.bounded(cmd, 120, C.ETWHO_GRACE_S)
            txt = out + err if rc is not None else "TimeoutExpired"
            if left:
                txt += f"\n{len(left)} process(es) of the {name} check still running after its bound and SIGTERM: left, not killed\n"
            with open(os.path.join(self.out, f"{name}.txt"), "w") as f:
                f.write(txt)
            if rc != 0 or left or not any(ln.startswith(want) for ln in txt.splitlines()):
                bad.append(f"the {name} did not read {want} (see {name}.txt)")
        return "; ".join(bad)

    def card_lock_path(self):
        return os.path.join(self.dev_dir, "card.lock") if self.dry else self.K["lock"]

    def take_card_lock(self):
        p = self.card_lock_path()
        if not self.dry:
            if not os.path.exists(p) or os.path.islink(p):
                return None, f"no card lock {p} on this box, or it is a link (it is never created here)"
            try:
                if os.stat(p).st_uid != 0:
                    return None, f"{p} is not root's"
            except OSError as e:
                return None, f"{p}: {type(e).__name__}"
        try:
            fd = os.open(p, os.O_RDONLY)
        except OSError as e:
            return None, f"the card's lock cannot be opened ({type(e).__name__})"
        for attempt in (1, 2):
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd, ""
            except OSError:
                if attempt == 1:
                    self.say("the card's lock is held: one retry in 15 s (another tool may hold it briefly)")
                    self.wait(15)
        os.close(fd)
        return None, "the card's lock is held"

    # ------------------------------------------------------------------ the whole session
    def run(self):
        a = self.a
        self.say(f"session start (T0 {a.t0}; card {self.card}, {self.K['box']} card {self.K['card']}; schedule "
                 f"{os.path.basename(a.sched)} sha256 {C.sha256(a.sched)[:16]}; {len(self.sched['runs'])} runs; files in "
                 f"{rel(self.out)}){' DRY scale ' + str(self.scale) if self.dry else ''}")
        boxfd = cardfd = None
        result = {"t0": a.t0, "card": self.card, "dry": self.dry, "scale": self.scale, "sched": os.path.basename(a.sched),
                  "sched_sha256": C.sha256(a.sched), "queue": self.queue}
        try:
            # the box lock first (under --dry a stand-in in the dry folder): held to the end; from src/start_mms.sh it is the
            # lock the start took before its own checks (MMS_BOX_LOCK_FD), so it is never free in between
            if not self.dry:
                os.makedirs(os.path.join(ROOT, C.RUN_DIR), exist_ok=True)
            boxp = os.path.join(self.out, "box.lock") if self.dry else os.path.join(ROOT, C.BOX_LOCK)
            boxfd, how = take_box_lock(boxp, None if self.dry else os.environ.get("MMS_BOX_LOCK_FD"))
            if boxfd is None:
                self.say(f"{how}: no device opened")
                return 16
            self.say(f"the box lock: {how}")
            if not self.dry:
                why = self.box_check()
                if why:
                    self.say(f"the box or the build is not the registered one ({why}): no device opened")
                    return 16
                self.say("the box and the build: the host, build/ (the kernel at E136's pin, the host and the reader as built "
                         "today), the harness, the device-command audit GO")
            if os.path.exists(self.kit_stop):
                self.say(f"{C.KIT_STOP} is present: no device opened (start_mms.sh moves it aside when no session runs)")
                return 16
            cardfd, why = self.take_card_lock()
            if cardfd is None:
                self.say(f"{why}: no device opened")
                return 16
            self.wait(3)
            h = self.holders()
            if h:
                self.say(f"a holder or a device process ({h}): one re-check in 5 s")
                self.wait(5)
                h = self.holders()
            with open(os.path.join(self.out, "etwho-before.txt"), "w") as fo:
                fo.write((h or "no holder that blocks; no device process that blocks") + "\n")
            if h:
                self.say(f"a holder or a device process ({h}): no device opened")
                return 16
            self.t_first = time.time()
            cfg0, why = self.config("start")
            self.device_opened = True
            if not cfg0 and not self.leftover:
                self.say(f"config start: {why}: one re-run in 5 s (another reader may have had the node)")
                self.wait(5)
                cfg0, why = self.config("start")
            if self.leftover:
                self.say(f"config start: {why}: no re-run, no launch, no closing read (a leftover holds or may hold the node)")
                return 16
            if not cfg0 or C.config_ok(self.card, cfg0):
                self.say(f"config start: {why or json.dumps(cfg0)}: {C.config_ok(self.card, cfg0) if cfg0 else ''}: the gate, no launch")
                return 16
            idw = N.config_identity(self.card, cfg0, self.cfg_err.get("start", ""))
            tg, ids = N.parse_ident(self.cfg_err.get("start", ""))
            self.ident["config_start"] = {"targets": sorted({f"/dev/et{c}_{k}" for c, k in tg}), "ids": sorted(set(ids)),
                                          "minion_mv": cfg0.get("minion_mv"), "why": idw}
            self.write_ident()
            if idw:
                self.say(f"config start: {json.dumps(cfg0)}: the card's identity: {idw}: the gate, no launch (and no closing read)")
                return 16
            self.start_ident_ok = True
            self.cfg0 = cfg0
            self.say(f"config start: {json.dumps(cfg0)} (read, nothing set); the card's identity: {C.node(self.card, 'mgmt')}, "
                     f"physical device ID {self.K['card']}" + (f", minion_mv {cfg0.get('minion_mv')}" if self.K["mv_rule"] else ""))
            if not self.start_sampler():
                self.say("the sampler would not start: no launch")
                return 16
            ok, res = self.stop_path_test()
            self.say("stop-path test " + ("passed" if ok else "failed") + ": " + "; ".join(
                f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, its file "
                f"{'touched' if v['test_file_touched'] else 'NOT touched'}, start {'refused' if v['refused_a_start'] else 'NOT refused'}"
                for k, v in res.items()))
            if not ok:
                return 16
            ok, why = self.identity_read()
            if not ok:
                self.say(f"the identity read (the sampler running): {why}: the gate, no launch")
                return 16
            self.say(f"the identity read: et-who {json.dumps(self.ident['etwho_with_sampler']['counts'], sort_keys=True)} (counts by "
                     f"card), the sampler holds {self.ident['sampler_nodes']['nodes']}: card {self.K['card']} only")
            ok, why = self.opening_rest()
            if not ok:
                self.say(f"the opening rest failed: {why}: the gate, no launch")
                return 16
            ok, why = self.smoke()
            if not ok:
                self.say(f"smoke gate failed: {why}")
                return 16
            self.say("smoke gate passed: the runs start")
            runs = self.sched["runs"][: a.only] if a.only else self.sched["runs"]
            for r in runs:
                if self.stops.stop:
                    self.queue.append({"i": r["i"], "arm": r["arm"], "ran": False, "why": "after a stop: nothing further starts"})
                    continue
                self.queue.append(self.one_run(r))
                self.write_status(len(runs))
                if self.dry and a.stop_after and len(self.queue) == a.stop_after:
                    open(self.stop_file, "a").close()      # --dry only: the operator's stop, as stop_mms.sh touches it
                if not self.leftover and not self.fresh() and not self.may_start(60) and not self.ensure_fresh_sampler():
                    self.stops.stop = self.stops.stop or "the sampler would not restart"
            if self.stops.stop:
                self.say(f"STOP: {self.stops.stop}: nothing further started")
            return 0
        finally:
            dl = self.close_deadline()
            if not self.stop_sampler(dl) and not any(x["what"] == "sampler" for x in self.leftover):
                self.note_leftover("sampler", "the session's sampler did not stop on SIGTERM at the closing")
            # the closing config read: only after a start read that passed the config and identity gates, never after an identity
            # trip or a stop for another holder, and never beside a device process of ours that should be gone
            why_no_close = ("the start read did not pass its gates" if not self.start_ident_ok else
                            "an identity trip" if self.identity_tripped else
                            "a stop for another holder or device process" if self.foreign_stop else
                            "a device process of ours is left" if self.leftover else "")
            if self.device_opened and self.t_first and not why_no_close:
                # the holders once more, right before the closing read opens the mgmt node again (the sampler has stopped, so the
                # form is the one before the first card command): another login on the card (aifoundry2: on any card), any node
                # line of ours, a lock line of ours off the card, or a device process skips the closing read
                h = self.holders(form="block")
                with open(os.path.join(self.out, "etwho-close.txt"), "w") as fo:
                    fo.write((h or "no holder that blocks; no device process that blocks") + "\n")
                if h:
                    why_no_close = f"a holder or a device process right before it ({h})"
                    self.mark("closing_holder", h)
            if self.device_opened and self.t_first and not why_no_close:
                cfg1, why = self.config("end", max(12.0, min(30.0, dl - time.time())) if dl else 30)
                self.say("config end: " + (json.dumps(cfg1) if cfg1 else why))
                tg, ids = N.parse_ident(self.cfg_err.get("end", ""))
                self.ident["config_end"] = {"targets": sorted({f"/dev/et{c}_{k}" for c, k in tg}), "ids": sorted(set(ids)),
                                            "minion_mv": (cfg1 or {}).get("minion_mv"),
                                            "why": N.config_identity(self.card, cfg1, self.cfg_err.get("end", "")) if cfg1 else why}
                if cfg1 and cfg0_saved(self) and cfg1.get("power_state") != cfg0_saved(self).get("power_state"):
                    self.say(f"the power state read {cfg0_saved(self).get('power_state')} at the start and {cfg1.get('power_state')} "
                             f"at the end (read, never set): recorded")
                self.write_ident()
            elif self.device_opened and self.t_first:
                self.say(f"no closing config read: {why_no_close}")
                self.ident["config_end"] = {"skipped": why_no_close}
                self.write_ident()
            left = None
            if self.leftover:
                # hold the card's lock until no device process of ours is left, at most LEFTOVER_WAIT_S (never kill -9)
                bound = C.LEFTOVER_WAIT_S * (max(self.scale, 0.1) if self.dry else 1.0)
                t = time.time()
                n = self.ours_alive()
                self.write_status(len(self.sched["runs"]), closing=f"holding the card's lock: {n} device process(es) of ours left")
                while n and time.time() - t < bound:
                    time.sleep(min(5.0, max(0.2, bound / 50)))
                    n = self.ours_alive()
                left = {"records": self.leftover, "still_alive_at_release": n, "waited_s": round(time.time() - t, 1),
                        "resolved": n == 0}
                self.say(f"LEFTOVER {'resolved' if n == 0 else 'NOT resolved'}: {n} device process(es) of ours alive after "
                         f"{left['waited_s']} s; " + ("the card's lock is released" if n == 0 else
                                                     "the card's lock is released at the bound: tell the owner (no kill -9)"))
            self.tel.close()
            tp = os.path.join(self.out, "telemetry.jsonl")
            if os.path.exists(tp):
                with open(tp, "rb") as fi, gzip.open(tp + ".gz", "wb") as fo:
                    fo.write(fi.read())
                os.remove(tp)
            result.update({"stop": self.stops.stop, "t_first_ms": int(self.t_first * 1000) if self.t_first else None,
                           "t_close_ms": now_ms(), "card_min": round(self.card_time() / 60, 2), "rest_die_c": self.rest_die,
                           "rest_board_w": self.rest_board, "identity_read_ok": self.ident_ok, "runner": "run_mms.py",
                           "n_ran": sum(1 for q in self.queue if q.get("ran")), "leftover": left,
                           "end_bound_ms": int(dl * 1000) if dl else None})
            if self.t_first:
                self.write_status(len(self.sched["runs"]), closing="ended", leftover=left)
            with open(os.path.join(self.out, "queue.json"), "w") as fo:
                json.dump(result, fo, indent=1)
            self.say(f"session end (T0 {a.t0}; {result['n_ran']} runs ran; {result['card_min']} card-minutes)")
            self.log_f.close()
            if self.dry:
                self.calls.close()
            if cardfd is not None:
                os.close(cardfd)
            if boxfd is not None:
                os.close(boxfd)
            write_manifest(self.out)


def cfg0_saved(sess):
    return getattr(sess, "cfg0", None)


def write_manifest(out):
    rows = []
    for dp, dn, fn in os.walk(out):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            r = os.path.relpath(p, out)
            if r in ("MANIFEST.sha256", "runner.rc", "runner.out", "box.lock") or r.startswith("fakedev"):
                continue
            rows.append(f"{C.sha256(p)}  {r}")
    with open(os.path.join(out, "MANIFEST.sha256"), "w") as f:
        f.write("\n".join(rows) + "\n")


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("what", choices=["session"])
    parser.add_argument("--card", choices=sorted(C.CARDS), required=True)
    parser.add_argument("--sched", required=True)
    parser.add_argument("--t0", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--deadline-epoch", type=int, default=0)
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--only", type=int, default=0)
    parser.add_argument("--trip-arm", default="")
    parser.add_argument("--trip-w", type=float, default=0.0)
    parser.add_argument("--config-fail", action="store_true")
    parser.add_argument("--wrong-card", action="store_true")
    parser.add_argument("--stop-after", type=int, default=0)
    parser.add_argument("--host-hang", default="")
    parser.add_argument("--sampler-stall", type=int, default=0)
    parser.add_argument("--wrong-config", action="store_true")
    parser.add_argument("--host-fail-after", type=int, default=0)
    parser.add_argument("--config-hang", choices=["", "start", "end"], default="")
    parser.add_argument("--holder-after", type=int, default=0)
    parser.add_argument("--closing-holder", action="store_true")
    a = parser.parse_args(argv)
    if not a.dry and (a.scale != 1.0 or a.only or a.trip_arm or a.config_fail or a.wrong_card or a.stop_after or a.host_hang
                      or a.sampler_stall or a.wrong_config or a.host_fail_after or a.config_hang or a.holder_after
                      or a.closing_holder):
        print("refused: --scale, --only, --trip-arm, --config-fail, --wrong-card, --stop-after, --host-hang, --sampler-stall, "
              "--wrong-config, --host-fail-after, --config-hang, --holder-after and --closing-holder are read with --dry only")
        return 2
    os.chdir(ROOT)
    return Session(a).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
