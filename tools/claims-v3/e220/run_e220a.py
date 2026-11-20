#!/usr/bin/env python3
"""E220's runner, ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): ARM A's whole session on aifoundry1 card 1 - E218's
runner (tools/claims-v3/e218/run_e218.py, landed in 5582edfc, which ran E218 FULL on aifoundry3 card 0: 107 of 107 runs, the opening smoke s01,
the stop-path test and the G block's smoke s03 in its place, data b445b0f5), every behaviour of it line for line (E215 arm A's runner, E213's with
E206's form: one sampler, the stop lines live, the stop-path test, the identity gate and read, the host watch, the sampler's freshness, the
gates, THE ARM FAMILIES, THE IDENTITY GATE PER PROCESS, THE WALK CHECK AND THE KERNEL STOPS, the family smoke's own stop path, the family smoke
inside the sequence), with E215 ARM B'S CARD RULES for aifoundry1 card 1 (tools/claims-v3/e215/run_e215.py's arm B, landed in 8bde0182, which ran
E215 arm B FULL on this card: 71 of 71 runs, data 4f648f24), and:
  - E220 arm A's order (plan-e220.json > arms > A > runs): the OPENING SMOKE s01 ('rgm136 gemmL', the session's gate), then the stop-path test,
    then the registered sequence: the tie, pass 1 (65 runs), the tie, pass 2 (18), the tie, then THE G BLOCK, LAST - its family smoke s03 ('rgm136
    gemmLnc' gemmLnc2x1x37, D1's; block "G-smoke") and its 26 runs (blocks G-pass1, G-pass2) (E220.md 6): 112 runs and the smoke s03;
  - ON AIFOUNDRY1 CARD 1 (E215 arm B's): ET_DEVICES=1 on every device process (the box check refuses an environment without it), card 1's lock
    (/run/lock/etsoc-shire1.lock), the start config TDP 65 W / 65 C / 600 MHz with /dev/et1_mgmt, physical device ID 1 and minion_mv below 510,
    the sampler on card 1's node only, every host on card 1 only (a runtime line naming another card is an identity trip); THE KERNEL GATE AT
    THE WHOLE ELF (E215 arm B's gate words on aifoundry1: "the whole ELF and its .text, the pinned ones"), the build record's ET_DEVICES reading
    (the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES); the TWO-CARD HOLDER RULE (a holder line of another login on card 1, ANY holder
    line of ours on card 0 - never two of our sessions on aifoundry1, nothing of ours on card 0 -, at the session's start any holder line on card
    0 of any login: the runtime's creation reaches every card its device layer enumerates and ET_DEVICES=1 is proven only by this session's own
    identity reads; later, another login's line on card 0 is reported, never a stop);
  - THE SIZED PLAIN TIMEOUT (E220.md 6, E218's R0 lesson: f04 run 77): each host process under `timeout <T>` with T from desk/timeouts-e220.json
    (e220a_common.timeout_of: 10 s for every process but xf04, 13 s there; never -k), its HUNG grace counted from its own T;
  - THE G SMOKE IN THE SEQUENCE (lnc_smoke, E215's reading), THE FAMILY SMOKE and the session's gate as E218's runner has them;
  - the card-time rule and cap (no run after 60 card-minutes, the session ends at 70); the files' names (build/e220argm/rgm136,
    build/e220argm/rgm211, build/e220a/T<T0>-A).
  E211's, E206's, E213's, E215's and E218's fixes are all kept (each "fix-e206" where it sits): the operator's STOP file read before every start
  and a STOP file present at the start a refusal before any device; a sampler that will not stop on SIGTERM left, never a second reader, the
  closing config read not sent while it lives; a runtime line naming another card than card 1 ("Opening device N") an identity trip; the board
  line skipping samples with no board reading; an unreadable et-who a holder; a crash named ("CRASH: <type>: <message>") and exit 1, its
  closing still run.
NO SIGKILL ANYWHERE (W/out/orch/kill-rule.txt; AGENT.md "never kill -9"): every device process runs under a plain `timeout 10`; a host whose
`timeout` has not returned HANG_GRACE_S (4 s) after its TERM is HUNG: the line "<time> HUNG: ..." in the session log, the host's stop file,
nothing further started, no further card command (the closing config read is not sent), the session closed and THE PROCESS LEFT (exit 8). et-who,
the box's checks and the config reads are waited on with a bound and left past it; the sampler is stopped by SIGTERM only.

    python3 -B tools/claims-v3/e220/run_e220a.py session --arm A --t0 T0 --out build/e220a/T<T0>-A [--deadline-epoch E]
    python3 -B tools/claims-v3/e220/run_e220a.py session --dry --arm A --t0 T0 --out DIR [--sequence plan|short|two|ties|lnc|lnc2|e2e]

What a session does (E220.md sections 3, 6 and 7; plan-e220.json > arms > A), from the box tree's root (aifoundry1 ~/nekko):
  1. checks the box and the builds: the hostname is aifoundry1; build/e220argm's record today's BUILT by build_e220a.sh on this box for arm A,
     rgm136's ELF through THE KERNEL GATE now and rgm211's through THE TREE GATE (check_e220a.py --kernel rgm136|rgm211), each host at the sha256
     the build recorded, the reader at its pin, every tile at its sha256, the harness (check_e220a.py --box: HARNESS OK, the registration's points,
     plan, kernel record and forecasts among it) and the preflight (preflight_e220a.sh: dmcmd_audit_v2 GO); the device environment without
     ET_DEVICES; else no device is opened;
  2. takes the card's lock (flock -n: /run/lock/etsoc-shire0.lock, held by this process to the end) and reads et-who and the processes (any
     holder line of another login, another user's device process, a CI job, any other device process of ours); an unreadable et-who is a holder;
     else no device opened;
  3. THE FIRST CARD COMMAND: `ettelem config` through the guard under `timeout 10`, its stderr kept: the start config as found (TDP 0 W / 65 C /
     600 MHz) and THE IDENTITY GATE of the card (/dev/et0_mgmt, ID 0); else the gate, no launch. The card time counts from it;
  4. ONE sampler (`ettelem sample --every-ms 100` through the guard, for the cap and 10 minutes; restarted only while a run could still start),
     every line to telemetry.jsonl and to THE STOP LINES as it arrives (the board above 70 W on 3 samples in a row, the die at or above 70 C; the
     die on the shires' mean, the latch only as it rises: e220a_common.Stops). A trip touches the host's --stop-file at once (the host ends at its
     next ~0.5 s launch boundary) and nothing further starts;
  5. THE IDENTITY READ (the sampler running): et-who as counts by card and the sampler's own open files: card 0 only, else the gate;
  6. THE SMOKE: 30 s at rest (the rest die and board: the die gate is formed from them), then one 2 s process of s01 (`--seconds 2 --budget
     3.5`), gated by its family first, rc 0 with every launch ok, its check of C exact or approx, no kernel stop, its counter's mean within
     200-4,000 cycles an op, the board at least 2 W over the rest during its launches, the host on card 0; THEN the stop-path test (each line again
     with a test threshold every live sample crosses must trip within 5 s, touch its own test file and refuse a start; no launch); any failure:
     the smoke gate failed, no run;
  7. the runs, the registered sequence: each run the die gate (min(60, rest die + 4); at most 300 s, else that run NO DATA), the holders again,
     10 s at rest, the identity gate of its process, ONE host process `timeout 10 <its host> <the point's host_args> --kernel <rgm136's ELF>
     --stop-file <STOP>` (`--seconds 6 --budget 7.5`), then 4 s read; no run starts once the card time passes 60 minutes, nor within its longest
     length (RUN_MAX_S) + 90 s of the window's last end; a started run is cut only by a stop; a kernel stop (a process of rgm211's host: family G),
     two failed 'rgm136 gemmL' processes in a row, K1 or a HUNG host stop the session; the G smoke s03 in its place, right before the G block;
  8. the closing, bounded by the cap (70 minutes): the sampler stopped (SIGTERM only), the closing `ettelem config` (not after a HUNG),
     "session end", the lock released, MANIFEST.sha256 last.
Every device command is a READ: the hosts open the ops node only; ettelem config and sample through the guard (it refuses --reset-ms and every
other word); dmcmd_audit_v2 GO is a box check. Nothing is set. --dry runs the same code against the doubles (fake_card_e220a.py), skips the box and
build checks, gates each process by its ELF's path (E220A_FAKE_GATE=fail:<point> refuses one point; the real gate is the real path's), and marks
every line DRY. SPDX-License-Identifier: Apache-2.0
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
import e220a_common as C  # noqa: E402
import e220a_ident as N1  # noqa: E402
import ident_e220a as IG  # noqa: E402  (the kit's identity gate per arm family, E211's keyed by E220's two loops; it pins E206's check_e206.py by sha256)

ROOT = C.REPO
CHECK_PY = "check_e220a.py"
PREFLIGHT_SH = "preflight_e220a.sh"
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
CI_COMM = re.compile(r"^Runner\.Worker$")
RC_HUNG = 8


def now_ms():
    return int(time.time() * 1000)


def stamp():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def pacific_day():
    """Today by the Pacific calendar (the day build_e220a.sh writes with TZ=America/Los_Angeles)."""
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
        self.dropped = {}              # the family smokes (E220.md 3): family -> {"smoke", "why", "t_ms"}: a family dropped by its own smoke (its runs never start)
        self.manifest_written = False
        self.tel_closed = False
        self.lockf = None
        self.env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
        self.env.pop("V3_DEVICE", None)
        self.env.pop("ET_DEVICES", None)
        if self.A["et_devices"] is not None:
            self.env["ET_DEVICES"] = self.A["et_devices"]
        self.dev_dir = os.path.realpath(os.path.join(self.out, "fakedev")) if self.dry else N1.DEV_DIR
        if self.dry:
            self.env["E220A_FAKE_SCHED"] = os.path.join(self.out, "fake_sched.jsonl")
            self.env["E220A_FAKE_ARM"] = self.arm
            self.env["E220A_FAKE_DEVDIR"] = self.dev_dir
            self.env["E220A_FAKE_LOCK"] = os.path.join(self.out, "dry.lock")
            os.makedirs(self.dev_dir, exist_ok=True)
            open(self.env["E220A_FAKE_SCHED"], "a").close()
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
        (CARD-LANE-BRIEF 2: `touch build/e220a/T<T0>-<arm>/STOP` on the box), read here before every start (E202's form; fix-e206, the
        verifier's finding 1). Every stop of the runner's own names itself before it touches that file, so the first reason is kept."""
        if not self.stops.stop and os.path.exists(self.stop_file):
            self.stops.stop = "the operator's STOP file (a registered stop: nothing further starts)"
            self.mark("stop_file", self.stops.stop)
        return self.stops.stop

    # ------------------------------------------------------------------ the doubles, or the box's commands
    def fake(self, *words):
        return [sys.executable, "-B", os.path.join(HERE, "fake_card_e220a.py")] + list(words)

    def cmd_config(self):
        return self.fake("config") if self.dry else ["timeout", str(C.HOST_TIMEOUT_S), "bash", C.GUARD, "config"]

    def cmd_sampler(self, seconds):
        w = ["sample", "--seconds", str(int(seconds)), "--every-ms", str(C.EVERY_MS)]
        return self.fake(*w) if self.dry else ["bash", C.GUARD] + w

    def cmd_etwho(self):
        return self.fake("etwho") if self.dry else ["timeout", "20", "et-who"]

    def host_cmd(self, argv, kind, to=C.HOST_TIMEOUT_S):
        """`timeout <to>` (plain, never -k) over one host process; to is the point's sized timeout (e220a_common.timeout_of)."""
        if self.dry:
            return ["timeout", str(to)] + self.fake("host", "--as", kind) + argv[1:]
        return ["timeout", str(to)] + argv

    def gate_of(self, pid, argv):
        """THE IDENTITY GATE PER PROCESS (E220.md 2; KIT.md 4): (ok, words) for the process's --kernel by its point's family (its loop), with the
        kit's gate (ident_e220a.gate: rgm136's .text and its whole ELF or its loadable identity). --dry gates by the ELF's path (the doubles have no
        ELF): the family's kernel folder, or E220A_FAKE_GATE=fail:<point> refusing that point (the real gate on real ELFs is the real-path test's)."""
        fam = C.family(pid)
        elf = C.arg_of(argv, "--kernel") or ""
        if self.dry:
            want = "/" + C.KERNELS[C.fam_elf(fam)]["dir"] + "/kernel/"
            forced = os.environ.get("E220A_FAKE_GATE", "") == f"fail:{pid}"
            if want in elf and not forced:
                return True, f"GATE OK: (dry, by path) {fam}: {C.fam_elf(fam)}'s kernel folder"
            return False, f"GATE FAILED: (dry, by path) {fam} needs {C.fam_elf(fam)}'s ELF; --kernel {os.path.relpath(elf, ROOT) if elf else None}" + (" (forced)" if forced else "")
        try:
            good, words = IG.gate(fam, elf, whole=True)        # aifoundry1: the whole ELF (E215 arm B's gate words)
        except Exception as e:  # noqa: BLE001 -- a gate that cannot be read is a failed gate
            good, words = False, f"the gate could not be read ({type(e).__name__}: {str(e)[:120]})"
        return good, ("GATE OK: " if good else "GATE FAILED: ") + words

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
        """'' when nothing blocks the arm's card, else why (counts only; E215 arm B's rule for aifoundry1, two cards): a holder line of another
        login on card 1's nodes or lock, ANY holder line of ours on card 0 (never two of our sessions on aifoundry1; nothing of ours on card 0),
        a CI job, another device process of ours; at the session's START also any holder line on card 0 of any login (the kit's start rule: the
        runtime's creation reaches every card its device layer enumerates, and ET_DEVICES=1 is proven only by this session's own identity
        reads); later, another login's line on card 0 is reported in the run (never a stop). An unreadable et-who is a holder (E202's fix)."""
        me = pwd.getpwuid(os.getuid()).pw_name      # our login, as et-who prints it (never written anywhere)
        why, note = [], []
        if with_etwho:
            lines, w = self.etwho_lines(tag)
            if lines is None:
                return w, ""
            hold = [ln.split() for ln in lines if (ln.startswith("/dev/et") or ln.startswith("lock:")) and len(ln.split()) > 1]
            c = N1.IDENT[self.arm]["card"]
            n_other1 = sum(1 for f in hold if f[1] != me and N1.holder_card(f[0]) == c)
            n_ours0 = sum(1 for f in hold if f[1] == me and N1.holder_card(f[0]) != c)
            n_other0 = sum(1 for f in hold if f[1] != me and N1.holder_card(f[0]) != c)
            if n_other1:
                why.append(f"{n_other1} holder line(s) of another login on card {c}")
            if n_ours0:
                why.append(f"{n_ours0} holder line(s) of ours on card 0 (never two of our sessions on aifoundry1; nothing of ours on card 0)")
            if n_other0 and start:
                why.append(f"{n_other0} holder line(s) of another login on card 0 (the kit's start rule for aifoundry1)")
            elif n_other0:
                note.append(f"{n_other0} holder line(s) of another login on card 0 (reported, not a stop once the session's identity is shown)")
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
        elif os.environ.get("E220A_FAKE_PS") in ("other", "ours", "ci"):
            why.append({"other": "1 other users' device process(es)", "ours": "1 other device process(es) of ours",
                        "ci": "1 CI job(s)"}[os.environ["E220A_FAKE_PS"]])
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
        secs = self.a.cap_s + 600
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
        """A run (or the smoke's next process) may start: no stop (the operator's STOP file included: fix-e206); the card time under the
        rule (E220.md 6: no run after 60 card-minutes); its planned length inside the cap (70 minutes) less the closing; before the window's
        last end."""
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
    def on_hung(self, pid, what, to=C.HOST_TIMEOUT_S):
        self.hung.append({"pid": pid, "what": what, "t_ms": now_ms()})
        self.stops.stop = self.stops.stop or f"HUNG: {what}"
        self.touch_stop()
        self.say(f"HUNG: a device process ({what}; its `timeout` pid {pid}) still runs {C.HANG_GRACE_S:g} s after its timeout's TERM "
                 f"at {to} s: nothing kills it (no SIGKILL, ever); the stop file is touched, nothing further starts and no "
                 f"further card command is sent; report it to the owner at once (the card may hold a hung hart: never reset it)")
        self.mark("hung", what, pid=pid)

    # ------------------------------------------------------------------ one host process
    def run_proc(self, argv, d, name, pid_point, kind, gate_words):
        os.makedirs(d, exist_ok=True)
        env = dict(self.env, E220A_FAKE_KIND=kind, E220A_FAKE_POINT=pid_point) if self.dry else self.env
        outp, errp = os.path.join(d, name + ".out"), os.path.join(d, name + ".err")
        fam = C.family(pid_point)
        to = C.timeout_of(pid_point)              # the sized plain timeout (desk/timeouts-e220.json: xf04 13 s, every other 10 s)
        t0 = now_ms()
        hung = False
        with open(outp, "w") as so, open(errp, "w") as se:
            p = subprocess.Popen(self.host_cmd(argv, C.fam_host(fam), to), cwd=ROOT, stdout=so, stderr=se, stdin=subprocess.DEVNULL, env=env)
            watch = N1.HostWatch(self.arm, p.pid, errp, self.dev_dir, on_wrong=self.identity_trip)
            watch.start()
            try:
                rc = p.wait(timeout=to + C.HANG_GRACE_S)
            except subprocess.TimeoutExpired:          # past its TERM: HUNG, reported and LEFT (never killed)
                rc, hung = None, True
            watch.finish()
        t1 = now_ms()
        self.device_opened = True
        if hung:
            self.on_hung(p.pid, f"the host of {os.path.basename(d)} ({name})", to)
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
        wok, wwords, wdet = C.walk_check(fam, fma, chk)
        return {"name": name, "argv": argv, "timeout_s": to, "rc": rc, "hung": hung, "t0_ms": t0, "t1_ms": t1, "n_launch": len(fma), "runtime_other_cards": rt_other,
                "family": fam, "host": C.fam_host(fam), "kernel": C.fam_elf(fam), "gate": gate_words,
                "walk_ok": wok, "walk_words": wwords, "walk": wdet, "tensor_errors": sum(int(x.get("tensor_errors") or 0) for x in fma),
                "launches_ok": bool(fma) and all(x.get("ok") for x in fma),
                "check": chk[-1].get("result") if chk else None, "check_ok": bool(chk) and bool(chk[-1].get("ok")),
                "check_cycles_per_op": chk[-1].get("cycles_per_op") if chk else None,
                "counted_cycles_per_op": (statistics.median([x["cycles_per_op"] for x in fma if C.counted(x) and x.get("cycles_per_op") is not None])
                                          if any(C.counted(x) and x.get("cycles_per_op") is not None for x in fma) else None),
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
        self.rest_board = statistics.median(bws) if bws else None
        rest = {"t0_ms": t0, "t1_ms": t1, "samples": len(win), "board_w_median": self.rest_board, "die_median_c": self.rest_die,
                "gate_c": C.gate_c(self.arm, self.rest_die), "latch_c": sorted({C.latch_of(s) for s in win if C.latch_of(s) is not None})}
        with open(os.path.join(d0, "rest.json"), "w") as f:
            json.dump(rest, f, indent=1)
        self.say(f"smoke rest: {len(win)} samples, board {rest['board_w_median']} W, die {self.rest_die} C (the latch {rest['latch_c']}); "
                 f"the die gate {rest['gate_c']} C")
        if not ok:
            return False, f"a stop during the rest reading: {self.stops.stop}"
        if not win or self.rest_die is None:
            return False, "no live sample in the rest reading"
        for pid in self.A["opening"]:
            why = self.may_start(C.HOST_TIMEOUT_S + C.HANG_GRACE_S + 5)
            if why:
                return False, f"{pid}: not started ({why})"
            if not self.fresh():
                return False, f"{pid}: not started (the sampler is not live: {self.staleness()})"
            argv = C.host_argv(ROOT, pid, C.SMOKE_SECONDS, C.SMOKE_BUDGET, self.stop_file)
            gok, gwords = self.gate_of(pid, argv)
            self.say(f"smoke {pid}: the identity gate ({C.family(pid)}): {gwords}")
            fam_smoke = C.FAMILY_SMOKE.get(pid)
            if not gok and fam_smoke and not self.stopped():     # the family smoke's own stop path (E220.md 3)
                os.makedirs(os.path.join(d0, pid), exist_ok=True)
                with open(os.path.join(d0, pid, "smoke.json"), "w") as fo:
                    json.dump({"argv": argv, "gate": gwords, "good": False, "ran": False, "a1_family_dropped": fam_smoke,
                               "a1_session_level": ""}, fo, indent=1)
                self.drop_family(fam_smoke, pid, f"the identity gate failed, no process started ({gwords})")
                continue
            if not gok:
                os.makedirs(os.path.join(d0, pid), exist_ok=True)
                with open(os.path.join(d0, pid, "smoke.json"), "w") as fo:
                    json.dump({"argv": argv, "gate": gwords, "good": False, "ran": False}, fo, indent=1)
                self.stops.stop = self.stops.stop or f"the identity gate failed for the smoke's {pid}: {gwords}"
                self.touch_stop()
                return False, f"{pid}: the identity gate failed, no process started ({gwords})"
            p = self.run_proc(argv, os.path.join(d0, pid), "proc", pid, "smoke", gwords)
            cpo = p["counted_cycles_per_op"]          # R0's reading: the median over the process's counted launches (E220.md 7)
            in_band = cpo is not None and C.SMOKE_CYC[0] <= cpo <= C.SMOKE_CYC[1]
            idn = p["ident"]
            id_ok = not idn["wrong"] and idn["right"] and not p["runtime_other_cards"]     # fix-e206: a runtime line naming another card
            win = self.window(*p["launch_window_ms"]) if p["launch_window_ms"] else []
            rise_ok, rise, n_rise = N1.board_rise(win, p["launch_window_ms"], self.rest_board)
            ks = C.kernel_stop(p["family"], p)
            good = p["rc"] == 0 and p["launches_ok"] and p["check"] in ("exact", "approx") and p["check_ok"] and p["walk_ok"] and \
                not p["tensor_errors"] and not ks and \
                in_band and id_ok and rise_ok and not p["k1"] and not p["hung"]
            sl = C.a1_session_level(p, id_ok, self.fresh()) if fam_smoke else ""
            drop = bool(fam_smoke) and not good and not sl and not self.stopped()     # the family smoke: the family's alone
            with open(os.path.join(d0, pid, "smoke.json"), "w") as fo:
                json.dump(dict(p, cycles_band=list(C.SMOKE_CYC), cycles_band_is="R0's: the smoke's counter mean 200-4,000 cycles an op (E220.md 7), "
                               "read on the median over the process's counted launches (the scorer's reading)", cycles_in_band=in_band,
                               identity_ok=id_ok, kernel_stop=ks,
                               board_rise={"ok": rise_ok, "rise_w": rise, "samples": n_rise, "rest_w": self.rest_board,
                                           "min_w": N1.RISE_MIN_W}, good=good,
                               a1_family_dropped=(fam_smoke if drop else None), a1_session_level=sl), fo, indent=1)
            self.ident.setdefault("smoke", {})[pid] = {"host": idn, "board_rise_w": rise, "rise_samples": n_rise}
            self.write_ident()
            self.say(f"smoke {pid}: the identity gate {gwords[:7]}; rc {p['rc']}, {p['n_launch']} launches, check {p['check']}, {p['walk_words']}, "
                     f"the counter's mean {cpo} cycles an op (R0's band {C.SMOKE_CYC[0]:g}-{C.SMOKE_CYC[1]:g}: {'in' if in_band else 'OUT'}; the check "
                     f"record's {p['check_cycles_per_op']}); records: {p['records']['runtime_lines']} runtime line(s) dropped, "
                     f"{p['records']['unparsed']} unparsed, {p['records']['mismatched']} not its command's; the host's card: "
                     f"{'its own' if id_ok else ('ANOTHER: ' + '; '.join(idn['wrong']) if idn['wrong'] else ('ANOTHER by its runtime line: card(s) ' + str(p['runtime_other_cards']) if p['runtime_other_cards'] else 'NOT SEEN'))} "
                     f"(stderr {idn['stderr_targets']} {idn['stderr_ids']}, held {idn['nodes_held']}); the board {rise} W over the rest "
                     f"on {n_rise} samples (at least {N1.RISE_MIN_W:g} W): {'ok' if good else 'FAILED'}")
            if p["k1"]:
                self.stops.stop = self.stops.stop or f"K1: a launch of the smoke's {pid} did not finish (the host's words): it may leave a hung hart"
                self.touch_stop()
                self.say(self.stops.stop)
            if ks and not drop:
                self.stops.stop = self.stops.stop or f"the kernel stops in the smoke's {pid} ({p['family']}): {ks}"
                self.touch_stop()
                self.say(self.stops.stop)
            if drop:                             # the family smoke's own stop path: the family dropped, the session goes on
                self.drop_family(fam_smoke, pid, "; ".join(x for x in (
                    f"rc {p['rc']}" if p["rc"] != 0 else "", "a launch not ok" if not p["launches_ok"] else "",
                    f"the check of C {p['check']} (ok {p['check_ok']})" if not (p["check"] in ("exact", "approx") and p["check_ok"]) else "",
                    f"walk FAILED: {p['walk_words']}" if not p["walk_ok"] else "", f"{p['tensor_errors']} tensor error(s)" if p["tensor_errors"] else "",
                    f"the counter's mean {cpo} outside R0's band" if not in_band else "", f"the board's rise {rise} W on {n_rise} samples" if not rise_ok else "")
                    if x))
                continue
            if self.stopped() and not good:      # a stop during the process (the operator's STOP file, a line, an identity trip, K1, the
                return False, f"a stop during the smoke's {pid}: {self.stops.stop}"     # kernel stops): named first (verify-e207's V4)
            if not good:
                return False, (f"{pid}: rc {p['rc']}, check {p['check']}, walk {'ok' if p['walk_ok'] else 'FAILED: ' + p['walk_words']}, the counter's mean {cpo} "
                               f"({'in' if in_band else 'outside'} R0's band), the host's card "
                               f"{'ok' if id_ok else 'NOT the arm' + chr(39) + 's'}, the board's rise {rise} W on {n_rise} samples"
                               f"{', K1' if p['k1'] else ''}{', HUNG' if p['hung'] else ''}")
            if self.stopped():
                return False, f"a stop during the smoke's {pid}: {self.stops.stop}"
        ok, res = self.stop_path_test()
        self.say("stop-path test " + ("passed" if ok else "failed") + ": " + "; ".join(
            f"{k} {'tripped' if v['tripped'] else 'did NOT trip'} in {v['s']} s, its file {'touched' if v['test_file_touched'] else 'NOT touched'}, "
            f"start {'refused' if v['refused_a_start'] else 'NOT refused'}" for k, v in res.items()))
        if not ok:
            return False, "the stop-path test failed"
        return True, ""

    def drop_family(self, fam, pid, why):
        """THE FAMILY SMOKE'S OWN STOP PATH (E220.md 3, E213's Amendment A1 form): the family is dropped (its runs never start: NO DATA, no card
        time); the session goes on. Never called for a failure that is the session's (e220a_common.a1_session_level) or after any stop."""
        members = sorted(q["id"] for q in self.A_points() if q["loop"] == fam)
        self.dropped[fam] = {"smoke": pid, "why": why, "t_ms": now_ms(), "points": members}
        self.say(f"smoke {pid}: FAILED for its family alone (its own stop path, E220.md 3): {why}: the family '{fam}' is DROPPED - "
                 f"{', '.join(members)} never start (NO DATA); the session goes on")
        self.mark("a1_family_dropped", f"{fam}: {why}", smoke=pid, points=members)

    def lnc_smoke(self, r):
        """THE GEMMLNC FAMILY'S SMOKE (family G's s03), the sequence's own entry right before its block (E220.md 3: "s03 (`gemmLnc2x2x2` fp32,
        rgm211's host with rgm136's ELF: family G's own smoke and stop path) right before the G block"; E215 arm A's reading, KIT.md 4 item 3): a
        run's start rules (the card-time rule and the window, the die gate, the holders), a run's 10 s at rest (its last 5 s are the board's rest
        for the rise and the reducer's p_rest: the opening rest is about 40 minutes back on a warm card), then ONE checked 2 s process gated by its
        family (`--seconds 2 --budget 3.5`) read by the opening smoke's checks, then a run's 4 s
        tail. ITS FAMILY'S OWN STOP PATH: a failure that is the family's alone drops the family (its runs never start, NO DATA) and the session
        goes on; a failure that is the session's (e220a_common.a1_session_level) or any stop raised during it stops the session. A smoke that
        cannot start for the die gate (300 s) or a sampler not live before it drops the family too: no family runs past a smoke that did not pass.
        Its files are a smoke's (smoke/<id>/smoke.json and proc.*), with its place in the sequence, so the reducer hands the scorer a smoke RUN."""
        pid = r["id"]
        fam = C.FAMILY_SMOKE.get(pid) or C.family(pid)
        key = C.run_key(r)
        base = {"n": r["n"], "block": r["block"], "id": pid, "name": r["name"], "arm": self.arm, "run": key, "smoke": True}
        if fam in self.dropped:
            return dict(base, ran=False, why=f"the family '{fam}' was already dropped")
        planned = C.run_max_s(pid)
        why = self.may_start(planned)
        if why:
            self.say(f"smoke {pid} (the gemmLnc block's): not started ({why}): its family's runs do not start either")
            return dict(base, ran=False, why=why)
        gate = C.gate_c(self.arm, self.rest_die)
        ok, die, waited, gwhy = self.die_gate(gate, planned)
        if not ok:
            w = gwhy or f"the die gate: {die} C after {waited:.0f} s (gate {gate} C)"
            if self.stopped():
                self.say(f"smoke {pid} (the gemmLnc block's): not started ({w})")
                return dict(base, ran=False, why=w)
            self.drop_family(fam, pid, f"its smoke did not start ({w})")
            return dict(base, ran=False, why=w, gate={"c": gate, "die": die, "waited_s": round(waited, 1)})
        why = self.may_start(planned)
        if why:
            self.say(f"smoke {pid} (the gemmLnc block's): not started ({why}): its family's runs do not start either")
            return dict(base, ran=False, why=why)
        f, note = self.foreign(tag=key)
        if f:
            self.stops.stop = self.stops.stop or f"a holder or a device process: {f}"
            self.touch_stop()
            self.say(f"STOP before the gemmLnc smoke {pid}: {f}")
            return dict(base, ran=False, why=f)
        d = os.path.join(self.out, "smoke", pid)
        os.makedirs(d, exist_ok=True)
        self.say(f"smoke {pid} (the gemmLnc block's, place {r['n']}): {r['name']} ({fam}: {C.fam_host(fam)}'s host, {C.fam_elf(fam)}'s ELF), a run's "
                 f"{self.a.rest_s:g} s at rest, then one {C.SMOKE_SECONDS:g} s process (gate {gate} C, die {die} C after {waited:.0f} s)"
                 + (f"; {note}" if note else ""))
        r0 = now_ms()
        clean = self.nap(self.a.rest_s)
        r1 = now_ms()
        rwin = self.window(max(r0, r1 - int(C.REST_WINDOW_S * 1000)), r1)     # inside its own rest read: its last 5 s (the reducer's p_rest)
        rbw = [s.get("board_w") for s in rwin if s.get("board_w") is not None]
        rest_w = statistics.median(rbw) if rbw else None
        rest = {"t0_ms": r0, "t1_ms": r1, "samples": len(rwin), "board_w_median_last5s": rest_w}
        meta = {"sequence_n": r["n"], "sequence_block": r["block"], "run": key, "rest": rest,
                "gate_die": {"c": gate, "die": die, "waited_s": round(waited, 1)}}
        if not clean:
            self.say(f"smoke {pid}: a stop tripped in its rest read: no process started")
            return dict(base, ran=False, why="stop: " + str(self.stops.stop))
        if not self.fresh() and not self.ensure_fresh_sampler():
            self.stops.stop = self.stops.stop or f"the sampler is not live before the gemmLnc smoke {pid} ({self.staleness()})"
            self.touch_stop()
            self.say(f"STOP: {self.stops.stop}")
            return dict(base, ran=False, why=self.stops.stop)
        argv = C.host_argv(ROOT, pid, C.SMOKE_SECONDS, C.SMOKE_BUDGET, self.stop_file)
        gok, gwords = self.gate_of(pid, argv)
        self.say(f"smoke {pid}: the identity gate ({fam}): {gwords}")
        if not gok:
            with open(os.path.join(d, "smoke.json"), "w") as fo:
                json.dump(dict(meta, argv=argv, gate=gwords, good=False, ran=False, a1_family_dropped=fam, a1_session_level=""), fo, indent=1)
            if self.stopped():
                return dict(base, ran=False, why=f"a stop: {self.stops.stop}")
            self.drop_family(fam, pid, f"the identity gate failed, no process started ({gwords})")
            return dict(base, ran=False, why="the identity gate failed: " + gwords, gate_words=gwords)
        p = self.run_proc(argv, d, "proc", pid, "smoke", gwords)
        cpo = p["counted_cycles_per_op"]
        in_band = cpo is not None and C.SMOKE_CYC[0] <= cpo <= C.SMOKE_CYC[1]
        idn = p["ident"]
        id_ok = not idn["wrong"] and idn["right"] and not p["runtime_other_cards"]
        win = self.window(*p["launch_window_ms"]) if p["launch_window_ms"] else []
        rise_ok, rise, n_rise = N1.board_rise(win, p["launch_window_ms"], rest_w)
        ks = C.kernel_stop(p["family"], p)
        good = p["rc"] == 0 and p["launches_ok"] and p["check"] in ("exact", "approx") and p["check_ok"] and p["walk_ok"] and \
            not p["tensor_errors"] and not ks and in_band and id_ok and rise_ok and not p["k1"] and not p["hung"]
        sl = C.a1_session_level(p, id_ok, self.fresh())
        drop = not good and not sl and not self.stopped()
        with open(os.path.join(d, "smoke.json"), "w") as fo:
            json.dump(dict(p, **meta, cycles_band=list(C.SMOKE_CYC), cycles_band_is="R0's: the smoke's counter mean 200-4,000 cycles an op (E220.md 7), "
                           "read on the median over the process's counted launches (the scorer's reading)", cycles_in_band=in_band,
                           identity_ok=id_ok, kernel_stop=ks,
                           board_rise={"ok": rise_ok, "rise_w": rise, "samples": n_rise, "rest_w": rest_w, "rest_is": "this smoke's own 10 s rest, its last 5 s",
                                       "min_w": N1.RISE_MIN_W}, good=good, a1_family_dropped=(fam if drop else None), a1_session_level=sl), fo, indent=1)
        self.ident.setdefault("smoke", {})[pid] = {"host": idn, "board_rise_w": rise, "rise_samples": n_rise}
        self.write_ident()
        self.say(f"smoke {pid}: rc {p['rc']}, {p['n_launch']} launches, check {p['check']}, {p['walk_words']}, the counter's mean {cpo} cycles an op "
                 f"(R0's band {C.SMOKE_CYC[0]:g}-{C.SMOKE_CYC[1]:g}: {'in' if in_band else 'OUT'}); the host's card {'its own' if id_ok else 'NOT the arm' + chr(39) + 's'}; "
                 f"the board {rise} W over its own rest {rest_w} W on {n_rise} samples (at least {N1.RISE_MIN_W:g} W): {'ok' if good else 'FAILED'}")
        if p["k1"]:
            self.stops.stop = self.stops.stop or f"K1: a launch of the gemmLnc smoke {pid} did not finish (the host's words): it may leave a hung hart"
            self.touch_stop()
            self.say(self.stops.stop)
        if ks and not drop:
            self.stops.stop = self.stops.stop or f"the kernel stops in the gemmLnc smoke {pid} ({p['family']}): {ks}"
            self.touch_stop()
            self.say(self.stops.stop)
        if drop:
            self.drop_family(fam, pid, "; ".join(x for x in (
                f"rc {p['rc']}" if p["rc"] != 0 else "", "a launch not ok" if not p["launches_ok"] else "",
                f"the check of C {p['check']} (ok {p['check_ok']})" if not (p["check"] in ("exact", "approx") and p["check_ok"]) else "",
                f"walk FAILED: {p['walk_words']}" if not p["walk_ok"] else "", f"{p['tensor_errors']} tensor error(s)" if p["tensor_errors"] else "",
                f"the counter's mean {cpo} outside R0's band" if not in_band else "", f"the board's rise {rise} W on {n_rise} samples" if not rise_ok else "")
                if x))
        elif not good:
            self.stops.stop = self.stops.stop or f"the gemmLnc smoke {pid} failed at the session's level: {sl or 'a stop during it'}"
            self.touch_stop()
            self.say(f"STOP: {self.stops.stop}")
        if not self.hung:
            self.idle(self.a.tail_s)
        return dict(base, ran=True, good=good, family_dropped=(fam if drop else None), rc=p["rc"], session_level=sl)

    def A_points(self):
        return C.points()["arms"][self.arm]["points"]

    # ------------------------------------------------------------------ one run
    def one_run(self, r):
        key = C.run_key(r)
        d = os.path.join(self.out, "runs", key)
        base = {"n": r["n"], "block": r["block"], "id": r["id"], "name": r["name"], "pair": r.get("pair"), "arm": self.arm, "run": key}
        planned = C.run_max_s(r["id"])
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
        self.say(f"run {key}: {r['name']} ({C.family(r['id'])}: {C.fam_host(C.family(r['id']))}'s host, {C.fam_elf(C.family(r['id']))}'s ELF), one {C.RUN_SECONDS:g} s process (gate {gate} C, die {die} C after {waited:.0f} s)"
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
            argv = C.host_argv(ROOT, r["id"], C.RUN_SECONDS, C.RUN_BUDGET, self.stop_file)
            gok, gwords = self.gate_of(r["id"], argv)
            rec["gate_words"] = gwords
            if not gok:
                self.stops.stop = self.stops.stop or f"the identity gate failed before run {key} ({C.family(r['id'])}): {gwords}"
                self.touch_stop()
                rec["flags"].append(f"the identity gate failed: no process started ({gwords})")
                self.say(f"STOP before run {key}'s process: the identity gate failed ({gwords}): nothing more today")
                rec.update(ran=False, why="the identity gate failed: " + gwords, stop=self.stops.stop)
                with open(os.path.join(d, "run.json"), "w") as fo:
                    json.dump(rec, fo, indent=1)
                return dict(base, ran=False, why=rec["why"])
            p = self.run_proc(argv, d, "proc-00", r["id"], "run", gwords)
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
            ks = C.kernel_stop(p["family"], p)
            if ks:              # a process of rgm211's host (E211's kernel stops, the kit's reading): nothing more that day
                self.stops.stop = self.stops.stop or f"the kernel stops in run {key} ({p['family']}): {ks}"
                self.touch_stop()
                rec["flags"].append(f"the kernel stops: {ks}")
            elif C.LOOPS[p["family"]]["walk"] is None and not p["walk_ok"]:
                rec["flags"].append(f"walk: {p['walk_words']}")
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
                 f"{sorted({str(p['check']) for p in rec['procs']})}, gate {[p['gate'][:7] for p in rec['procs']]}, walk "
                 f"{[p['walk_words'] if C.LOOPS[p['family']]['walk'] else 'none' for p in rec['procs']]}{', ' + '; '.join(rec['flags']) if rec['flags'] else ''}")
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
        if self.env.get("ET_DEVICES") != self.A["et_devices"] or self.A["et_devices"] != "1":
            return "arm A's device environment lacks ET_DEVICES=1 (card 1 only): refused before any device"
        bad = []
        try:
            rec = C.load(os.path.join(ROOT, C.BUILD_REC))
        except (OSError, ValueError):
            return f"no build record {C.BUILD_REC}: run build_e220a.sh (the runbook's build step) first"
        today = pacific_day()
        if rec.get("day") != today or rec.get("verdict") != "BUILT" or rec.get("box") != self.A["box"] or rec.get("builder") != C.BUILDER:
            bad.append(f"the build record is not today's BUILT by {C.BUILDER} on {self.A['box']} ({rec.get('day')}, {rec.get('verdict')}, "
                       f"{rec.get('box')}, {rec.get('builder')})")
        if rec.get("arm") != self.arm:
            bad.append(f"the build record is arm {rec.get('arm')}'s, not arm {self.arm}'s")
        if rec.get("et_devices") != C.ETDEV_YES:
            bad.append(f"the build record does not say the hosts honour ET_DEVICES ({rec.get('et_devices')})")
        ks = rec.get("kernels") or {}
        pairs = [(self.A["ettelem"], self.A["ettelem_sha256"])]
        for k in C.KERNELS:
            pairs += [(C.elf_rel(k), (ks.get(k) or {}).get("kernel_sha256")), (C.host_rel(k), (ks.get(k) or {}).get("host_sha256"))]
        for rel, want in pairs:
            p = os.path.join(ROOT, rel)
            got = sha256(p) if os.path.isfile(p) else None
            if got is None or got != want:
                bad.append(f"{rel}: sha256 {got}, want {want}")
        for rel, want in C.TILES.items():
            p = os.path.join(ROOT, rel)
            if not os.path.isfile(p) or sha256(p) != want:
                bad.append(f"{rel} is not its manifest's {want[:12]}")
        if bad:
            return "; ".join(bad)
        whole = ["--whole"]                   # aifoundry1: both kernels at the whole ELF (E213 arm B's and E215 arm B's builds there read the pins)
        for name, cmd, want in (("kernel-rgm136", [sys.executable, "-B", os.path.join(HERE, CHECK_PY), "--kernel", "rgm136", os.path.join(ROOT, C.elf_rel("rgm136"))] + whole, "KERNEL OK"),
                                ("kernel-rgm211", [sys.executable, "-B", os.path.join(HERE, CHECK_PY), "--kernel", "rgm211", os.path.join(ROOT, C.elf_rel("rgm211"))] + whole, "KERNEL OK"),
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
                self.say(f"the box and the builds: the host {self.A['box']}, build/e220argm (rgm136 through THE KERNEL GATE at its whole ELF and "
                         "rgm211 through THE TREE GATE at its whole ELF, each host as built today, the hosts and /opt/et/lib/libdeviceLayer.a carrying "
                         "ET_DEVICES), the reader at its pin, the tiles, the harness (the registration's points, plan, kernel record and forecasts "
                         "and the kit's timeouts among it) and the preflight (dmcmd_audit_v2 GO); ET_DEVICES=1 on every device process")
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
            ok, why = self.smoke()
            if self.hung:
                self.say(f"smoke gate failed: {why}")
                rc = RC_HUNG
                return rc
            if not ok:
                self.say(f"smoke gate failed: {why}")
                rc = 16
                return rc
            self.say("smoke gate passed: the runs start" + (" (the family smokes: " + "; ".join(
                f"the family '{f}' dropped by its smoke {v['smoke']}: {', '.join(v['points'])} never start" for f, v in self.dropped.items()) + ")"
                if self.dropped else ""))
            seq = C.sequence(self.arm)
            if a.sequence == "short":          # --dry and the desk's real-path test only: the first tie and the first two points of pass 1
                seq = seq[:3]
            elif a.sequence == "two":          # --dry only: one run of each block form (tie, pass 1, tie)
                seq = [seq[0], seq[1], [r for r in seq if r["block"] == "tie"][1]]
            elif a.sequence == "ties":         # --dry only: the three ties
                seq = [r for r in seq if r["block"] == "tie"]
            elif a.sequence == "lnc":          # --dry and the real-path test: the third tie, then THE G BLOCK (its smoke s03 and its 24 runs)
                ti = [i for i, r in enumerate(seq) if r["block"] == "tie"][-1]
                seq = seq[ti:]
            elif a.sequence == "lnc2":         # --dry and the real-path test: the third tie, the G smoke s03 and the G block's first two runs
                ti = [i for i, r in enumerate(seq) if r["block"] == "tie"][-1]
                seq = seq[ti:ti + 4]
            elif a.sequence == "e2e":          # --dry only: the whole registered order (the end-to-end case)
                seq = list(seq)
            for r in seq:
                if self.stopped():           # the operator's STOP file read before every start too (fix-e206)
                    self.queue.append({"n": r["n"], "id": r["id"], "run": C.run_key(r), "ran": False, "why": "after a stop: nothing further starts"})
                    continue
                if C.is_lnc_smoke(r):        # THE GEMMLNC FAMILY'S SMOKE, right before its block (E220.md 3)
                    self.queue.append(self.lnc_smoke(r))
                    if not self.stopped() and not self.fresh() and not self.may_start(60) and not self.ensure_fresh_sampler():
                        self.stops.stop = self.stops.stop or "the sampler would not restart"
                    continue
                fam = C.family(r["id"])
                if fam in self.dropped:      # the family smoke's own stop path: a dropped family's run never starts (NO DATA, no card time)
                    w = (f"the family '{fam}' was dropped by its smoke {self.dropped[fam]['smoke']} "
                         f"({self.dropped[fam]['why'][:160]}): never started, NO DATA")
                    self.say(f"run {C.run_key(r)}: not started ({w})")
                    self.queue.append({"n": r["n"], "id": r["id"], "run": C.run_key(r), "ran": False, "why": w, "a1_family_dropped": fam})
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
                  "runner": "run_e220a.py", "identity_read_ok": self.ident_ok, "hung": self.hung, "rc": rc,
                  "samplers_left": [q.pid for q in self.left_samplers], "families_dropped": self.dropped}
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
    ap.add_argument("--sequence", choices=["plan", "short", "two", "ties", "lnc", "lnc2", "e2e"], default="plan")
    ap.add_argument("--rest-s", type=float, default=C.REST_READ_S)
    ap.add_argument("--smoke-rest-s", type=float, default=C.SMOKE_REST_S)
    ap.add_argument("--tail-s", type=float, default=C.TAIL_S)
    ap.add_argument("--gate-wait-s", type=float, default=C.GATE_WAIT_S)
    ap.add_argument("--rule-s", type=float, default=None)
    ap.add_argument("--cap-s", type=float, default=None)
    a = ap.parse_args(argv)
    rule0, cap0 = C.ARMS[a.arm]["rule_s"], C.ARMS[a.arm]["cap_s"]       # the registered rule and cap (plan-e220.json: 60 and 70 card-minutes)
    changed_rule, changed_cap = a.rule_s is not None and a.rule_s != rule0, a.cap_s is not None and a.cap_s != cap0
    a.rule_s = rule0 if a.rule_s is None else a.rule_s
    a.cap_s = cap0 if a.cap_s is None else a.cap_s
    if not a.dry:
        changed = [n for n, v in (("--rest-s", a.rest_s != C.REST_READ_S), ("--smoke-rest-s", a.smoke_rest_s != C.SMOKE_REST_S),
                                  ("--tail-s", a.tail_s != C.TAIL_S), ("--gate-wait-s", a.gate_wait_s != C.GATE_WAIT_S),
                                  ("--rule-s", changed_rule), ("--cap-s", changed_cap),
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
