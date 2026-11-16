#!/usr/bin/env python3
"""E198's REAL-PATH DESK TEST AFTER DATED AMENDMENT A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum).

    bash slot.sh bash nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e198/desk/desktest_realpath_e198a1.py <empty scratch dir> > log

It is desktest_realpath_e198.py (kit-e198, Q191; unchanged beside it) run on A1's files, with A1's cases added. It runs SESSION_E198A1.SH'S
REAL PATH, DRY UNSET, exactly as step 9 (A1) launches it, and through it THE LAB'S RUNNER COPY (run_x04_e198a1.py: E193's runner with the
kill path changed: every device process under a plain `timeout 10`, one still running 25 s after it started reported at once and left
running, end_device() sending SIGTERM and waiting, never a KILL) in the kit's private /dev, with every stand-in, sandbox and real byte of
the v1 test (fake_card_e198a1.py is fake_card_e198.py with two A1 knobs). What A1 changes in the test itself: the A1 harness, session,
runner, listing check (check_e198a1.py) and build record ("a1 build_e198a1.sh"); this file sends NO KILL to anything: a stand-in holder is
ended with SIGTERM, and a case past its bound gets SIGTERM, never v1's SIGKILL. v1's cases, each as v1 states it (below), on A1's files:
PB2, K1, X1, W1, NWI, NWL (the lab's copy run directly, without the guard), IA0, IB0, H0, NOC1, NOM1, B4, GE, Y1, Y1B (the listings SAME
through check_e198a1.py's six mappings), AUDIT (every dry-flag line of session_e198a1.sh and run_x04_e198a1.py). A1's cases:
  HG   THE HOST THAT HANGS PAST ITS TERM (sitting B, the smoke's first device process; it catches TERM and ends by itself 140 s after it
       started): the runner copy reports it at 25 s ("device process still running 25 s ... device process not ended: tell the lab
       admin", event device_not_ended), stops the smoke ("device process not ended 25 s after it started ... (nothing killed: tell the lab
       admin)" in STOPPED), and its clean-up's end_device() sends SIGTERM to the timeout and waits 15 s and 60 s, reporting each, then leaves
       it ("device process not ended: the card lock goes only when this runner exits"); the session says "A DEVICE PROCESS DID NOT END",
       ends at the smoke gate (GATE-STOP, rc 3) and skips its closing config read. THE STRACE-FREE PROOF THAT NO KILL WAS SENT: the
       stand-in host is ALIVE when the session has ended (its process ID still there), and so are its `timeout` and the host wrapper
       (a KILL aimed at the timeout would have ended both), its signal log holds TERMs only, and it writes its own end line ("ended by
       itself at 140 s"), which a process killed by a KILL could never write. K9 (the dated fix): the runner's clean-up stops its sampler
       with SIGTERM all the same ("E198 A1: the sampler is stopped all the same"; the stand-in sampler's "ended (SIGTERM)"), so the sampler
       is gone when the session ends, the end knob finds none, and the smoke's telemetry is at its manifest sha256; nothing of the case is
       left;
  HGE  the same host in the main run's first device process, ending by itself 60 s after it started, inside end_device()'s 60 s wait: the
       stop as HG ("main run stopped", rc 1), then end_device() reads it ended ("device_ended"), the clean-up releases the lock and stops
       the sampler with SIGTERM; the host's own end line; nothing left when the session ends;
  HG2  a host that ends 1.5 s after its TERM (v1's `timeout -k 1 10` would have killed it at 11 s): it ends by itself at 11.5 s, the
       runner reads exit 124 and makes the registered stop "killed by timeout (tell the lab admin)", as registered; no DEVICE line;
  KILLWORDS  the runner copy, the session and every file this test drives name no SIGKILL, `kill -9` or `timeout -k` (a grep of their
       code lines; the kit-wide audit is desk/killaudit_e198a1.py).
Dated fix (Q196, lane fix-a1e198, Mon 16 Nov 2026, before the land and before any E198 datum), answering verify-a1e198's findings 1 and 6:
HG now asserts K9 (the sampler stopped by the clean-up, gone at the session's end, the smoke's telemetry final before the manifest) and
that the host's `timeout` and wrapper are alive at the session's end.
EVERY WATT AND DEGREE HERE IS THE STAND-INS' ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT. Prints
DESKTEST-REALPATH-E198-A1 <n> of <m> PASS (or FAIL). Exit 0 on PASS, 1 on FAIL, 2 on a usage or sandbox refusal.

v1's docstring, for its cases (read with A1's file names):
E198's REAL-PATH DESK TEST (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum).

    bash slot.sh bash nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e198/desk/desktest_realpath_e198.py <empty scratch dir> > log

It runs SESSION_E198.SH'S REAL PATH, DRY UNSET, exactly as step 9 launches it (E198_T0, E198_LAST_END_EPOCH, E198_HARNESS_SHA256, the
sitting), and through it E193's runner as committed (unchanged) IN THE KIT'S PRIVATE /dev (privdev_e198.sh: bubblewrap, nested), its real
--sampler path through the guard shim and E191's guard (both unchanged as the box runs them), its real --holder-check (holdercheck_e198.sh)
answered by the real warden outside the private /dev, and its real --host (x04host_e198.sh, the runtime-line guard), against stand-ins for
every device tool (fake_card_e198.py: the reader build/ettelem/ettelem and its config read, et-who, the host x04clock_host). Each case runs
in its OWN SANDBOX inside the no-device one (W/nodev.sh): a TWO-CARD BOX made of /dev/null bound at /dev/et0_ops, /dev/et0_mgmt,
/dev/et1_ops and /dev/et1_mgmt (character devices, as on aifoundry1; opening them opens /dev/null), a scratch /run/lock, a private PID
namespace with its own /proc (et-who reads only the case's processes), the host name aifoundry1, and a stand-in /etc/passwd naming our
uid 'boxuser' (so no login of the lab reaches a log). The stand-ins print aifoundry1's REAL runtime line (its bytes from 1a4bc1e3) and the
config read's REAL card-1 stderr (7156ac15's config-start.err). It refuses to start if a real character device /dev/et* is visible.
Real timing throughout: 20 s of idle reference, 5 s gaps, 0.4 s launches, 30 s between passes.

Cases (each asserts the session's log, its exit status, the runner's files, the stand-ins' call log, the manifest, and that no process of
the case is left):
  PB2  sitting B, its REAL PATH: the first card command (et-who --check, free), the two-card box, THE PRIVATE /dev SHOWN (card 1's two
       nodes inside, nothing else), the start config read inside it (IDENTITY (a) OK on the real card-1 stderr), the warden, IDENTITY (b)
       (the identity sampler inside; et-who outside; the holder check from inside lists the sampler by its process ID), the smoke (10 calls,
       SMOKE GO), the main run's passes 0 and 1 whole (15 calls each); A CARD-0 HOLDER OUTSIDE THE PRIVATE /dev during pass 0's gap: the
       runner's holder check INSIDE (through the warden) sees it and waits ("card_wait", pass 1 block C); THE RUNTIME LINE INSIDE AN X04
       LINE in one host call of pass 1: the guard drops it, the runner reads every record; then the operator's stop file (x04/STOP) at
       pass 2's first call: "main run stopped" (rc 1), the closing config read, the warden's summary (the watch: hosts on /dev/et1_ops,
       samplers on /dev/et1_mgmt, no card-0 node, no hit), the manifest; then THE COLLECTION (collect_e198.py), THE REGISTERED REDUCER,
       E193's checker and THE TRANSPORT SCORER (score_e198.py score) on what was collected;
  K1   the board above 65 W on three samples in a row during the main run: "main run stopped" (a registered stop), rc 1, the closing read;
  X1   a crash of the main run (a malformed X04 line from the host, passed through the guard unchanged): "main run ended without a
       registered stop", rc 4;
  W1   THE WATCH: a process carrying this sitting's E198_SESSION_T0 holding /dev/et0_mgmt during the smoke: WATCH-STOP, the runner's own
       stop files touched, the smoke stops, GATE-STOP naming the watch;
  NWI, NWL  the negative controls: the unchanged runner run directly in the private /dev WITHOUT the guard, the stand-in host printing the
       runtime line inside its first X04 line (NWI: the runner raises, "no stop recorded") or at the line's start (NWL: read, rc 0);
  IA0  IDENTITY (a) refused: the config read's stderr names /dev/et0_mgmt and device ID 0 (the real bytes made card 0's): GATE-STOP;
  IB0  IDENTITY (b) refused: another login's card-0 holder line appears after the start config read: GATE-STOP;
  H0   another login's card-0 holder at the start: the first card command refuses, GATE-STOP (no device opened);
  NOC1 card 1 absent (only card 0's nodes): the two-card check, GATE-STOP (no device opened); NOM1 card 1's management node absent: the
       private /dev refuses to bind it, GATE-STOP (no device opened);
  B4   the host name aifoundry2: GATE-STOP (no device opened);
  GE   the components with a missing or wrong ET_DEVICES: E191's guard through the shim refuses (97) with ET_DEVICES unset or 0, and runs the
       reader with 1; the stand-in host in the private /dev refuses with ET_DEVICES unset (it wants /dev/et0_ops, which is not there);
  Y1, Y1B  THE DRY PATH (DRY=1), sittings A and B: rc 0, build/e198/T<T0>-dry, every line "DRY ", the private /dev listed, the listings
       equal to E193's registered ones through check_e198.py's five mappings, no stand-in device tool called;
  AUDIT every line of session_e198.sh and run_x04.py that a dry flag skips (desk/dry-branches-e198.tsv, written here and read against the
       files' own lines) is run by a case above that passed.
EVERY WATT AND DEGREE HERE IS THE STAND-INS' ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT. Prints
DESKTEST-REALPATH-E198 <n> of <m> PASS (or FAIL). Exit 0 on PASS, 1 on FAIL, 2 on a usage or sandbox refusal.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
SRC = os.path.normpath(os.path.join(E, "..", "..", ".."))
FAKE = os.path.join(E, "fake_card_e198a1.py")
PY = "/usr/bin/python3"
RES = []
LOCK = threading.Lock()
ALLNODES = ("et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def put(path, text, mode=0o644):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if isinstance(text, bytes) else "w") as f:
        f.write(text)
    os.chmod(path, mode)


def rd(path):
    try:
        with open(path, errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def ok(name, cond, detail):
    with LOCK:
        RES.append((name, bool(cond)))
        print(f"-> {'PASS' if cond else 'FAIL'} ({name}: {detail})", flush=True)


# ---------------------------------------------------------------------------------------------------------------- the inner side
def inner(argv):
    """Inside the case's sandbox: helpers on the case's knobs (a card-0 holder; a decoy of the sitting), then the command."""
    cmd = argv[argv.index("--") + 1:]
    state = os.environ["E198_FAKE_STATE"]
    stop = threading.Event()

    def helper():
        h0 = dec = None
        while not stop.is_set():
            if os.path.exists(os.path.join(state, "holder0-on")) and h0 is None and not os.path.exists(os.path.join(state, "holder0-off")):
                h0 = subprocess.Popen(["/usr/bin/sleep", "300"], stdin=open("/dev/et0_mgmt"))
            if os.path.exists(os.path.join(state, "holder0-off")) and h0 is not None:
                h0.terminate(); h0.wait(); h0 = None
            if os.path.exists(os.path.join(state, "decoy-sitting")) and dec is None:
                env = dict(os.environ, E198_SESSION_T0=rd(os.path.join(state, "decoy-sitting")).strip())
                dec = subprocess.Popen(["/usr/bin/sleep", "300"], stdin=open("/dev/et0_mgmt"), env=env)
            time.sleep(0.2)
        for p in (h0, dec):
            if p is not None:
                p.terminate(); p.wait()
    th = threading.Thread(target=helper, daemon=True)
    th.start()
    try:
        return subprocess.run(cmd).returncode
    finally:
        stop.set()
        th.join(3)


# ---------------------------------------------------------------------------------------------------------------- the outer side
class Box:
    def __init__(self, S):
        self.S = S
        self.home = os.path.join(S, "home")
        self.tree = os.path.join(self.home, "nekko")
        self.root = os.path.join(self.tree, "build/claims-v3/aifoundry1/e198")
        self.bin = os.path.join(S, "bin")
        self.kit = os.path.join(self.root, "tools/claims-v3/e198")
        self.host = os.path.join(self.root, "build/x04clock/host/x04clock_host")
        self.kernel = os.path.join(self.root, "build/x04clock/kernel/x04clock.elf")
        self.built = os.path.join(self.root, "build/x04clock-built.txt")
        lst = subprocess.run([PY, "-I", "-B", os.path.join(E, "harness_e198a1.py"), "--list"], capture_output=True, text=True,
                             check=True).stdout.split()
        for p in lst:
            dst = os.path.join(self.root, p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(SRC, p), dst)
        shutil.copy2(os.path.join(SRC, "tools/claims-v3/e193/fake_card_e193.py"), os.path.join(self.root, "tools/claims-v3/e193/fake_card_e193.py"))
        g = os.path.join(self.tree, "tools/claims-v3/e191/ettelem_guard_e191.sh")
        os.makedirs(os.path.dirname(g), exist_ok=True)
        shutil.copy2(os.path.join(SRC, "tools/claims-v3/e191/ettelem_guard_e191.sh"), g)
        wrap = '#!/bin/bash\nexec %s -I -B %s %s "$@"\n'
        self.reader = os.path.join(self.tree, "build/ettelem/ettelem")
        put(self.reader, wrap % (PY, FAKE, "ettelem"), 0o755)
        put(self.host, wrap % (PY, FAKE, "host"), 0o755)
        put(self.kernel, "stand-in kernel ELF for E198's real-path desk test (never loaded)\n")
        put(os.path.join(self.bin, "et-who"), wrap % (PY, FAKE, "etwho"), 0o755)
        for c, real in (("timeout", "/usr/bin/timeout"), ("flock", "/usr/bin/flock")):
            put(os.path.join(self.bin, c), '#!/bin/bash\necho "$(date +%%s.%%N) %s $*" >> "$E198_FAKE_STATE/calls.log"\nexec %s "$@"\n'
                % (c, real), 0o755)
        for c in ("ssh", "scp", "rsync", "sudo"):
            put(os.path.join(self.bin, c), '#!/bin/sh\necho "STAND-IN %s: refused (no network, no privilege at the desk)" >&2\nexit 97\n' % c, 0o755)
        put(self.built, "X04-BUILT %s (stand-in record of the desk test)\nkernel %s\ntext (stand-in)\nhost %s\nreader %s\na1 build_e198a1.sh\n" % (
            time.strftime("%F %T %Z"), sha(self.kernel), sha(self.host), sha(self.reader)))
        hj = os.path.join(self.kit, "harness-e198-a1.json")
        h = json.load(open(hj))
        h["tree"]["build/ettelem/ettelem"] = sha(self.reader)          # the stand-in reader's pin, in this test's own copy only
        put(hj, json.dumps(h, indent=1, sort_keys=True) + "\n")
        self.hsha = sha(hj)
        uid = os.getuid()
        pw = [ln for ln in open("/etc/passwd") if not ln.split(":")[2:3] == [str(uid)]]
        pw.append(f"boxuser:x:{uid}:{os.getgid()}:stand-in:{self.home}:/bin/bash\n")
        self.passwd = os.path.join(S, "accounts")
        put(self.passwd, "".join(pw))
        self.rtfile = os.path.join(S, "runtime-line.bin")
        b = subprocess.run(["git", "-C", SRC, "show", "1a4bc1e3:docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/"
                            "copy-64m-random/stdout.txt"], capture_output=True, check=True).stdout
        put(self.rtfile, re.search(rb"Opening device [0-9]+\n", b).group(0))
        self.cfgerr = os.path.join(S, "config-card1.err")
        put(self.cfgerr, subprocess.run(["git", "-C", SRC, "show", "7156ac15:docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/"
                                         "session/config-start.err"], capture_output=True, check=True).stdout)


def procs_with(state):
    out = []
    key = ("E198_FAKE_STATE=" + state).encode()
    for p in glob.glob("/proc/[0-9]*"):
        try:
            if key in open(p + "/environ", "rb").read().split(b"\0"):
                out.append(int(p.split("/")[2]))
        except OSError:
            continue
    return [p for p in out if p != os.getpid()]


class Case:
    def __init__(self, box, name, sit, nodes=ALLNODES, host="aifoundry1", last_end=4 * 3600, dry=False, env=None, maxs=900, cmd=None):
        self.b, self.name, self.sit = box, name, sit
        self.state = os.path.join(box.S, "state-" + name)
        self.runlock = os.path.join(box.S, "runlock-" + name)
        os.makedirs(self.state)
        os.makedirs(self.runlock)
        with LOCK:
            t = int(time.time())
            while int(time.time()) == t:
                time.sleep(0.05)
            self.T0 = int(time.time())
            time.sleep(1.05)
        self.sd = os.path.join(box.tree, "build/e198", "T%d%s" % (self.T0, "-dry" if dry else ""))
        self.nodes, self.hostname, self.dry, self.maxs, self.cmd = nodes, host, dry, maxs, cmd
        self.env = {"PATH": box.bin + ":/usr/bin:/bin", "HOME": box.home, "USER": "boxuser", "LOGNAME": "boxuser", "LC_ALL": "C",
                    "E198_FAKE_STATE": self.state, "E198_FAKE_RTFILE": box.rtfile, "E198_FAKE_CFGERR": box.cfgerr,
                    "E198_T0": str(self.T0), "E198_HARNESS_SHA256": box.hsha, "E198_LAST_END_EPOCH": str(self.T0 + last_end)}
        if dry:
            self.env["DRY"] = "1"
        self.env.update(env or {})
        self.done = set()

    def f(self, *p):
        return os.path.join(self.sd, *p)

    def once(self, key, cond, act):
        if key not in self.done and cond():
            self.done.add(key)
            act()

    def knob(self, name, text=""):
        put(os.path.join(self.state, name), text)

    def run(self, watch=None):
        cmd = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev"]
        for n in self.nodes:
            cmd += ["--dev-bind", "/dev/null", "/dev/" + n]
        cmd += ["--bind", self.runlock, "/run/lock", "--bind", self.b.passwd, "/etc/passwd", "--proc", "/proc", "--unshare-pid",
                "--unshare-uts", "--hostname", self.hostname, "--die-with-parent", "--chdir", self.b.tree, "--", PY, "-I", "-B",
                os.path.abspath(__file__), "--inner", "--"]
        cmd += self.cmd or ["bash", os.path.join(self.b.kit, "session_e198a1.sh"), self.sit]
        t0 = time.time()
        p = subprocess.Popen(cmd, env=self.env, stdout=open(os.path.join(self.state, "session.stdout"), "w"),
                             stderr=subprocess.STDOUT, start_new_session=True)
        killed = False
        while p.poll() is None:
            if watch:
                watch(self)
            if time.time() - t0 > self.maxs:
                if not killed:
                    os.killpg(p.pid, signal.SIGTERM)     # A1: a case past its bound gets a TERM, never a KILL
                killed = True
            time.sleep(0.2)
        self.rc = p.returncode
        self.secs = time.time() - t0
        time.sleep(0.5)
        self.left = procs_with(self.state)
        self.log = rd(self.f("session.log"))
        self.calls = rd(os.path.join(self.state, "calls.log"))
        with LOCK:
            print(f"   [{self.name}] exit {self.rc} after {self.secs:.0f} s{' (TERM at its bound)' if killed else ''}", flush=True)
            for ln in self.log.splitlines():
                if re.search(r"GATE-STOP|main run|smoke (start|end)|SMOKE|first card|config read|identity|private /dev|warden|watch|session (start|end)", ln):
                    print(f"     | [{self.name}] " + ln[24:250], flush=True)
        return self

    def manifest_ok(self):
        if not os.path.exists(self.f("MANIFEST.sha256")):
            return False
        return subprocess.run(["sha256sum", "-c", "--quiet", "MANIFEST.sha256"], cwd=self.sd, capture_output=True).returncode == 0

    def ncalls(self, word):
        return len(re.findall(r"^\S+ " + word, self.calls, re.M))

    def stop_of(self, rel):
        return subprocess.run([PY, "-I", "-B", os.path.join(SRC, "tools/claims-v3/e193/check_e193.py"), "stopreason", self.f(rel)],
                              capture_output=True, text=True).stdout.strip()

    def runlog_calls(self, rel):
        return re.findall(r"^pass (\d+) block (\S+) (\S+): (\d+) launches, exit (-?\d+)", rd(self.f(rel, "run.log")), re.M)

    def common(self, want_rc, gate=None):
        ok(self.name + " exit", self.rc == want_rc, f"session exit {self.rc}, want {want_rc}")
        g = re.findall(r"GATE-STOP: (.*)", self.log)
        if gate is None:
            ok(self.name + " no gate", not g, f"no GATE-STOP line ({len(g)})")
        else:
            ok(self.name + " gate", g and re.search(gate, g[0]), f"GATE-STOP: {g[0][:170] if g else '(none)'}")
        ok(self.name + " end", "session end (T0 %d)" % self.T0 in self.log and self.manifest_ok() and rd(self.f("session.rc")).strip()
           == str(want_rc), "'session end', MANIFEST.sha256 verifying, session.rc " + rd(self.f("session.rc")).strip())
        ok(self.name + " nothing left", not self.left, f"processes of the case left: {self.left}")


def pb2(box):
    c = Case(box, "PB2", "B", maxs=1500)
    seen = {}

    def watch(c):
        calls = c.runlog_calls("x04")
        rl = rd(c.f("x04", "run.log"))
        c.once("h0on", lambda: "pass 0 done" in rl, lambda: (c.knob("holder0-on"), seen.__setitem__("h0on", time.time())))
        c.once("h0off", lambda: "h0on" in seen and time.time() - seen["h0on"] > 40, lambda: c.knob("holder0-off"))
        c.once("inside", lambda: any(x[0] == "1" for x in calls),
               lambda: c.knob("runtime", "inside %d\n" % (int(rd(os.path.join(c.state, "host-calls")).strip() or 0) + 2)))
        c.once("stop", lambda: any(x[0] == "2" for x in calls), lambda: open(c.f("x04", "STOP"), "a").close())
    c.run(watch)
    c.common(1)
    ok("PB2 the first card command and the box", "the first card command (the holder check): free on both cards" in c.log and
       "the host's ops nodes /dev/et0_ops /dev/et1_ops" in c.log, "free on both cards; the two-card box read")
    ok("PB2 THE PRIVATE /dev shown", "card nodes inside [et1_mgmt et1_ops]" in c.log, re.findall(r"the private /dev \(.*", c.log)[0][:150]
       if "the private /dev (" in c.log else "no line")
    ok("PB2 IDENTITY (a) on the real card-1 stderr", "start config read (inside the private /dev): IDENT-A OK" in c.log,
       (re.findall(r"start config read.*", c.log) or ["none"])[0][:160])
    ok("PB2 IDENTITY (b) and the holder check from inside", "IDENT-B OK" in c.log and '"inside_same_as_outside": true' in c.log,
       (re.findall(r"identity read with the sampler running: (.*)", c.log) or ["none"])[0][:220])
    sm = c.runlog_calls("smoke")
    ok("PB2 smoke", len(sm) == 10 and "SMOKE GO" in c.log, f"{len(sm)} smoke calls; {(re.findall(r'SMOKE GO[^;]*', c.log) or ['no SMOKE GO'])[0][:100]}")
    calls = c.runlog_calls("x04")
    per = {p: sum(1 for x in calls if x[0] == p) for p in ("0", "1")}
    ok("PB2 two whole passes", per == {"0": 15, "1": 15} and all(x[4] == "0" for x in calls), f"calls a pass {per}; exits {sorted({x[4] for x in calls})}")
    ok("PB2 the operator's stop", "main run stopped: runner rc 1; stop: stop file" in c.log, c.stop_of("x04"))
    ev = [json.loads(x) for x in rd(c.f("x04", "events.jsonl")).splitlines() if x.startswith("{")]
    cw = [e for e in ev if e.get("kind") == "card_wait"]
    ok("PB2 THE HOLDER CHECK INSIDE SEES CARD 0", cw and cw[0].get("why") == "pass 1 block C" and cw[0].get("seconds", 0) >= 25,
       f"card_wait events {cw}: a card-0 holder outside the private /dev, seen through the warden")
    runs = [json.loads(x) for x in rd(c.f("x04", "runs.jsonl")).splitlines() if x.startswith("{")]
    nl = sum(int(x[3]) for x in calls)
    facts = json.loads(subprocess.run([PY, "-I", "-B", os.path.join(E, "dropruntime_e198.py"), "facts", c.f("x04-hostraw", "index.jsonl")],
                                      capture_output=True, text=True).stdout or "{}")
    raw_inside = sum(1 for p in glob.glob(c.f("x04-hostraw", "*.stdout")) if b'"cls":Opening device 1\n' in open(p, "rb").read())
    ok("PB2 THE RUNTIME LINE GUARDED", len(runs) == nl and facts.get("runtime_lines_dropped") == facts.get("device_processes") == len(calls)
       and facts.get("x04_not_at_start") == 0 and facts.get("opening_text_left") == 0 and raw_inside == 1,
       f"{len(runs)} records for {nl} launches; {facts}; raw files with the runtime line inside an X04 line: {raw_inside}")
    wsum = json.loads(rd(c.f("holderd", "summary.json")) or "{}")
    served = [json.loads(x) for x in rd(c.f("holderd", "served.jsonl")).splitlines() if x.startswith("{")]
    ok("PB2 the warden and the watch", wsum.get("watch_hits") == [] and set(wsum.get("nodes_seen", [])) == {"/dev/et1_mgmt", "/dev/et1_ops"}
       and wsum.get("held_ops", 0) >= 10 and len(served) >= 4 and any(s["rc"] == 1 and s["holder_lines"] >= 2 for s in served),
       f"summary {json.dumps({k: wsum.get(k) for k in ('requests_served', 'statuses', 'held_ops', 'held_mgmt', 'nodes_seen', 'watch_hits')})}")
    ok("PB2 the closing read", "closing config read: IDENT-A OK" in c.log, (re.findall(r"closing config read.*", c.log) or ["none"])[0][:120])
    starts = [x for x in c.calls.splitlines() if re.search(r"^\S+ ettelem (config|sample --)", x)]
    ok("PB2 ET_DEVICES=1 for every device tool", len(starts) >= 4 and all("ET_DEVICES=1" in x for x in starts),
       f"{len(starts)} reader starts (config reads and samplers), each with ET_DEVICES=1")
    # ---- the collection, the registered reducer, E193's checker, the transport scorer
    data = os.path.join(box.S, "data-PB2")
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "collect_e198.py"), c.sd, data, "--box-home", box.home, "--sitting", "B",
                        "--login", "boxuser"], capture_output=True, text=True)
    ok("PB2 the collection", r.returncode == 0 and "COLLECTED" in r.stdout and os.path.exists(os.path.join(data, "x04", "hostraw.txt.gz")),
       (r.stdout.strip().splitlines() or [r.stderr[-200:]])[-1][:200])
    X = os.path.join(box.S, "reduce-PB2", "x04")
    os.makedirs(X)
    shutil.copy2(os.path.join(data, "x04", "runs.jsonl"), os.path.join(X, "runs.jsonl"))
    put(os.path.join(X, "telemetry.jsonl"), gzip.decompress(open(os.path.join(data, "x04", "telemetry.jsonl.gz"), "rb").read()))
    xj = os.path.join(box.S, "reduce-PB2", "x04-e198-B.json")
    r1 = subprocess.run([PY, "-I", "-B", os.path.join(SRC, "tools/claims-v3/e193/proposal/src/reduce_x04.py"), X, "--out", xj],
                        capture_output=True, text=True)
    r2 = subprocess.run([PY, "-I", "-B", os.path.join(SRC, "tools/claims-v3/e193/check_e193.py"), "checks", xj, X, "--out",
                         os.path.join(box.S, "reduce-PB2", "checks.json")], capture_output=True, text=True)
    r3 = subprocess.run([PY, "-I", "-B", os.path.join(E, "score_e198.py"), "score", "--b", xj, "--out", os.path.join(box.S, "reduce-PB2",
                         "scores.json")], capture_output=True, text=True)
    ok("PB2 the reducer, the checker, the scorer", r1.returncode == 0 and os.path.exists(xj) and "CHECKS READ" in r2.stdout and r3.returncode == 0,
       f"reducer rc {r1.returncode}; checker: {(re.findall(r'CHECKS READ.*', r2.stdout) or [r2.stderr[-120:]])[0][:100]}; scorer rc "
       f"{r3.returncode}: {(r3.stdout.strip().splitlines() or [r3.stderr[-160:]])[-1][:160]}")
    return c


def k1(box):
    c = Case(box, "K1", "B", maxs=900)
    c.run(lambda c: c.once("hot", lambda: len(c.runlog_calls("x04")) >= 1, lambda: c.knob("board66")))
    c.common(1)
    ok("K1 a registered stop", "main run stopped: runner rc 1; stop: board above 65 W on three samples in a row" in c.log, c.stop_of("x04"))


def x1(box):
    c = Case(box, "X1", "B", maxs=900)
    c.run(lambda c: c.once("garble", lambda: len(c.runlog_calls("x04")) >= 1, lambda: c.knob("host-mode", "garble 1\n")))
    c.common(4)
    ok("X1 a crash, not a registered stop", "main run ended without a registered stop: runner rc 1" in c.log and "main run stopped" not in c.log,
       c.stop_of("x04"))


def main_cases(box):
    th = [threading.Thread(target=f, args=(box,)) for f in (pb2, k1, x1, hg, hge, hg2)]
    for t in th:
        t.start()
    # ---- W1: the watch
    c = Case(box, "W1", "B", maxs=600)
    c.run(lambda c: c.once("decoy", lambda: len(c.runlog_calls("smoke")) >= 1, lambda: c.knob("decoy-sitting", str(c.T0))))
    c.common(3, gate=r"the watch saw a card node other than card 1's: .*WATCH-HIT.*/dev/et0_mgmt")
    ok("W1 the runner stopped by the watch's stop file", c.stop_of("smoke").startswith("stop: stop file") and os.path.exists(c.f("x04", "STOP")),
       c.stop_of("smoke"))
    # ---- NWI, NWL: the unchanged runner without the guard
    for name, mode, want in (("NWI", "inside 1", 1), ("NWL", "line", 0)):
        out = f"build/e198-nw/{name}"
        c = Case(box, name, "B", maxs=300, cmd=["env", "ET_DEVICES=1", "bash", os.path.join(box.kit, "privdev_e198.sh"), PY, "-I", "-B",
                 os.path.join(box.kit, "run_x04_e198a1.py"), out, "--arms", os.path.join(box.root, "tools/claims-v3/e193/proposal/src/arms.tsv"),
                 "--host", box.host, "--sampler",
                 os.path.join(box.kit, "ettelem_guard_e198.sh"), "--device", "1", "--holder-check", "/bin/true", "--smoke", "--blocks", "S"])
        c.knob("runtime", mode + "\n")
        c.run()
        lg = rd(os.path.join(box.tree, out, "run.log"))
        so = rd(os.path.join(c.state, "session.stdout"))
        recs = len([x for x in rd(os.path.join(box.tree, out, "runs.jsonl")).splitlines() if x.strip()])
        if name == "NWI":
            ok("NWI the runner raises without the guard", c.rc == 1 and "JSONDecodeError" in so and not os.path.exists(os.path.join(box.tree,
               out, "STOPPED")), f"rc {c.rc}; a traceback ({'JSONDecodeError' in so}); no STOPPED: the inside form reaches json.loads unguarded")
        else:
            ok("NWL the runtime line at a line's start is skipped", c.rc == 0 and lg.rstrip().endswith("done") and recs > 0,
               f"rc {c.rc}; {recs} records; run.log ends 'done'")
        ok(name + " nothing left", not c.left, f"processes left: {c.left}")
    # ---- the gates
    c = Case(box, "IA0", "B")
    err = rd(box.cfgerr).replace("/dev/et1_mgmt", "/dev/et0_mgmt")
    err = re.sub(r"(Physical device ID:\s+)1(\s+)\(0x1\)", r"\g<1>0\g<2>(0x0)", err)
    c.knob("config-err", err)
    c.run()
    c.common(3, gate=r"THE IDENTITY GATE \(a\): IDENT-A FAIL: PCIe target /dev/et0_mgmt, not /dev/et1_mgmt; Physical device ID \[0\]")
    ok("IA0 no sampler, no host", c.ncalls("ettelem sample") == 0 and c.ncalls("host") == 0, "no sampler or host call")
    c = Case(box, "IB0", "B")
    c.run(lambda c: c.once("foreign", lambda: os.path.exists(c.f("ident-a.txt")), lambda: c.knob(
        "foreign", "/dev/et0_ops   otheruser          777       01:00 someone-elses_host\n")))
    c.common(3, gate=r"THE IDENTITY GATE \(b\): IDENT-B FAIL: .*another login")
    ok("IB0 no smoke, no host", c.ncalls("host") == 0 and not os.path.exists(c.f("smoke")), "the identity sampler only; no host call")
    c = Case(box, "H0", "B")
    c.knob("foreign", "/dev/et0_mgmt  otheruser          778       01:00 someone-elses-reader\n")
    c.run()
    c.common(3, gate=r"a card is held: et-who --check lists 1 holder line.*\(no device opened\)")
    ok("H0 nothing opened", c.ncalls("ettelem") == 0 and c.ncalls("host") == 0, "no reader or host call")
    for name, nodes, gate in (("NOC1", ("et0_ops", "et0_mgmt"), r"not /dev/et0_ops /dev/et1_ops.*\(no device opened\)"),
                              ("NOM1", ("et0_ops", "et0_mgmt", "et1_ops"), r"the private /dev is not card 1's two nodes only.*PRIVDEV-REFUSED: /dev/et1_mgmt.*\(no device opened\)")):
        c = Case(box, name, "B", nodes=nodes)
        c.run()
        c.common(3, gate=gate)
        ok(name + " nothing opened", c.ncalls("ettelem") == 0 and c.ncalls("host") == 0, "no reader or host call")
    c = Case(box, "B4", "B", host="aifoundry2")
    c.run()
    c.common(3, gate=r"this is aifoundry2, not aifoundry1.*\(no device opened\)")
    # ---- GE: the components with a missing or wrong ET_DEVICES
    probe = os.path.join(box.S, "ge.sh")
    put(probe, "#!/bin/bash\nK=%s\nfor v in unset 0 1; do\n  if [ $v = unset ]; then unset ET_DEVICES; else export ET_DEVICES=$v; fi\n"
        "  \"$K/ettelem_guard_e198.sh\" config > $E198_FAKE_STATE/ge-out 2> $E198_FAKE_STATE/ge-err; echo \"GUARD ET_DEVICES=$v rc $? $(grep -c '^{' $E198_FAKE_STATE/ge-out) json; $(head -c 120 $E198_FAKE_STATE/ge-err | tr '\\n' ' ')\"\n"
        "done\nunset ET_DEVICES\nbash \"$K/privdev_e198.sh\" %s --label spin2 --arm spin --t1 same > $E198_FAKE_STATE/ge-out 2> $E198_FAKE_STATE/ge-err; echo \"HOST ET_DEVICES=unset rc $? $(head -c 160 $E198_FAKE_STATE/ge-err | tr '\\n' ' ')\"\n"
        % (box.kit, box.host), 0o755)
    c = Case(box, "GE", "B", cmd=["bash", probe])
    c.run()
    so = rd(os.path.join(c.state, "session.stdout"))
    ok("GE E191's guard: ET_DEVICES unset and 0 refused, 1 runs the reader",
       re.search(r"GUARD ET_DEVICES=unset rc 97 0 json;.*ET_DEVICES is 'unset', not 1", so) and re.search(r"GUARD ET_DEVICES=0 rc 97 0 json", so)
       and re.search(r"GUARD ET_DEVICES=1 rc 0 1 json", so), " | ".join(x[:110] for x in so.splitlines() if x.startswith("GUARD")))
    ok("GE the host refuses with ET_DEVICES unset in the private /dev", re.search(r"HOST ET_DEVICES=unset rc 1 FAIL: found 1 ops node\(s\); need exactly /dev/et0_ops", so),
       (re.findall(r"HOST .*", so) or ["none"])[0][:160])
    # ---- Y1, Y1B: the dry path
    for name, sit, reg in (("Y1", "A", "dry-e193-A.txt"), ("Y1B", "B", "dry-e193-B.txt")):
        c = Case(box, name, sit, dry=True)
        c.run()
        lines = [x for x in c.log.splitlines() if x.strip()]
        k = os.path.join(box.kit, "check_e198a1.py")
        wrap = "build/claims-v3/aifoundry1/e198/tools/claims-v3/e198/x04host_e198.sh"
        hc = "build/claims-v3/aifoundry1/e198/tools/claims-v3/e198/holdercheck_e198.sh"
        cmp = [subprocess.run([PY, "-I", "-B", k, "drycmp", c.f(o), os.path.join(SRC, "tools/claims-v3/e193/desk", r), "--host", wrap,
                               "--holder-check", hc], capture_output=True, text=True).stdout.strip()
               for o, r in (("smoke-runner.out", "dry-e193-smoke-all.txt"), ("runner.out", reg))]
        ok(name + " the dry path", c.rc == 0 and lines and all(" DRY " in x[:30] for x in lines) and "card nodes inside [et1_mgmt et1_ops]" in c.log
           and all(x.startswith("LISTING SAME") for x in cmp) and c.ncalls("ettelem") == 0 and c.ncalls("host") == 0 and c.ncalls("et-who") == 0,
           f"rc {c.rc}; {len(lines)} lines all DRY; {cmp}; stand-in device calls {c.ncalls('ettelem')}+{c.ncalls('host')}+{c.ncalls('et-who')}")
        for o, dst in (("smoke-runner.out", "dry-e198a1-smoke.txt"), ("runner.out", f"dry-e198a1-{sit}.txt")):
            if os.path.exists(c.f(o)):
                shutil.copyfile(c.f(o), os.path.join(box.S, dst))
        ok(name + " nothing left", not c.left, f"processes left: {c.left}")
    for t in th:
        t.join()


# ---------------------------------------------------------------------------------------------------------------- A1's cases
def hgwrap(argv):
    """Inside a case's sandbox (A1's HG cases): run the command (the session), then read which of the case's stand-ins are still alive
    (the session has ended: a stand-in host the runner left running must be ALIVE, so no KILL reached it), then make the end knob (a
    stand-in sampler still running would end by itself on it; after K9 the runner's clean-up has stopped it already), and wait, bounded,
    until every stand-in has ended BY ITSELF (the host at its own life). Nothing is signalled here: the PID namespace would end what is
    left with a KILL when this returns, so it returns only after nothing is left (or after its bound, said so)."""
    cmd = argv[argv.index("--") + 1:]
    state = os.environ["E198_FAKE_STATE"]
    rc = subprocess.run(cmd).returncode

    mine, q = set(), os.getpid()
    while q > 0 and q not in mine:                       # this process and its ancestors (the inner side, the namespace's init)
        mine.add(q)
        try:
            q = int(re.search(r"^PPid:\s+(\d+)", open(f"/proc/{q}/status").read(), re.M).group(1))
        except (OSError, AttributeError, ValueError):
            break

    def alive():
        out = []
        for p in glob.glob("/proc/[0-9]*"):
            try:
                pid = int(p.split("/")[2])
                if pid in mine or ("E198_FAKE_STATE=" + state).encode() not in open(p + "/environ", "rb").read().split(b"\0"):
                    continue
                if re.search(r"^State:\s+Z", open(p + "/status").read(), re.M):
                    continue                             # a zombie has ended; its parent has not reaped it yet
                out.append((pid, open(p + "/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")[:160]))
            except (OSError, ValueError):
                continue
        return out
    hp = rd(os.path.join(state, "a1-host.pid")).strip()
    left = alive()
    with open(os.path.join(state, "a1-left-at-session-end.txt"), "w") as f:
        st_ = (re.findall(r"^State:\s+(\S)", rd("/proc/%s/status" % hp), re.M) or ["gone"])[0] if hp else "gone"
        f.write("session rc %d at %.3f; the stand-in host pid %s alive: %s (state %s)\n" % (rc, time.time(), hp or "-", st_ not in ("gone", "Z"), st_))
        for pid, cl in left:
            f.write("%d %s\n" % (pid, re.sub(r"\S*/", "", cl)))
    open(os.path.join(state, "a1-sampler-end"), "w").close()
    t0 = time.time()
    while alive() and time.time() - t0 < 300:
        time.sleep(0.5)
    with open(os.path.join(state, "a1-left-at-end.txt"), "w") as f:
        f.write("after %.1f s: %d left\n" % (time.time() - t0, len(alive())))
    return rc


def hglog(c):
    return rd(os.path.join(c.state, "a1-host.log")), rd(os.path.join(c.state, "a1-host-signals.log"))


def hg(box):
    """HG: the smoke's first device process hangs past its TERM (life 140 s)."""
    c = Case(box, "HG", "B", maxs=900, cmd=[PY, "-I", "-B", os.path.abspath(__file__), "--hgwrap", "--", "bash",
                                           os.path.join(box.kit, "session_e198a1.sh"), "B"])
    c.knob("a1-hang", "1 140\n")
    c.run()
    ok("HG exit", c.rc == 3, f"session exit {c.rc}, want 3")
    g = re.findall(r"GATE-STOP: (.*)", c.log)
    ok("HG gate", g and g[0].startswith("the smoke gate failed"), f"GATE-STOP: {g[0][:150] if g else '(none)'}")
    chk = subprocess.run(["sha256sum", "-c", "MANIFEST.sha256"], cwd=c.sd, capture_output=True, text=True).stdout
    moved = sorted(x.rsplit(":", 1)[0] for x in chk.splitlines() if not x.endswith(": OK"))
    ok("HG end: the manifest; only the host wrapper's files may move after it (K9: the telemetry is final)", "session end (T0 %d)" % c.T0 in c.log
       and rd(c.f("session.rc")).strip() == "3" and set(moved) <= {"smoke/device-stdout.txt", "smoke-hostraw/index.jsonl"}
       and "smoke/telemetry.jsonl: OK" in chk,
       f"'session end', session.rc {rd(c.f('session.rc')).strip()}; files not at the manifest's sha256 (written after it by the processes the runner "
       f"left: the host's wrapper): {moved}; smoke/telemetry.jsonl {'OK' if 'smoke/telemetry.jsonl: OK' in chk else 'NOT OK'}")
    ok("HG nothing left", not c.left, f"processes of the case left: {c.left}")
    rl = rd(c.f("smoke", "run.log"))
    ev = [json.loads(x) for x in rd(c.f("smoke", "events.jsonl")).splitlines() if x.startswith("{")]
    dne = [e for e in ev if e.get("kind") == "device_not_ended"]
    ok("HG the runner copy reports the device process at 25 s", "device process still running 25 s after it started (its timeout's TERM came at 10 s; "
       "nothing is killed): device process not ended: tell the lab admin" in rl and dne and dne[0].get("seconds") == 25 and dne[0].get("arm") == "spin2",
       f"run.log line {'present' if 'device process not ended: tell the lab admin' in rl else 'MISSING'}; device_not_ended events {dne[:3]}")
    ok("HG the registered stop, in A1's form", c.stop_of("smoke").startswith("stop: spin2: device process not ended 25 s after it started, its "
       "timeout's TERM at 10 s (nothing killed: tell the lab admin)"), c.stop_of("smoke")[:200])
    ok("HG end_device(): SIGTERM and waits, reported, then left", "ending the running device process: SIGTERM to its timeout, then waiting" in rl
       and "device process still running 15 s after SIGTERM: tell the lab admin" in rl and "device process still running 60 s after SIGTERM: tell the lab admin"
       in rl and "device process not ended: the card lock goes only when this runner exits" in rl and [e.get("seconds") for e in dne] == [25, 15, 60],
       f"end_device's lines in run.log; device_not_ended seconds {[e.get('seconds') for e in dne]}")
    ok("HG the session says it and sends nothing else to the card", "A DEVICE PROCESS DID NOT END in the smoke run" in c.log and
       "closing config read: skipped: a device process of this sitting did not end" in c.log and "main run start" not in c.log,
       (re.findall(r"A DEVICE PROCESS DID NOT END.{0,120}", c.log) or ["no line"])[0])
    hl, sig = hglog(c)
    left0 = rd(os.path.join(c.state, "a1-left-at-session-end.txt"))
    hp = rd(os.path.join(c.state, "a1-host.pid")).strip()
    ok("HG NO KILL: the host alive when the session ended", hp and f"the stand-in host pid {hp} alive: True" in left0,
       "at the session's end: " + left0.splitlines()[0][:160] if left0 else "no record")
    terms = [ln for ln in sig.splitlines() if ln.strip()]
    ok("HG NO KILL: TERMs only, and its own end line", terms and all(" TERM " in ln for ln in terms) and
       re.search(r"A1-HOST ended by itself at 14\d\.\d+ s \(its life of 140 s\): \d+ TERM\(s\) received, exit 0", hl),
       f"{len(terms)} TERM line(s) ({'; '.join(x.split(' ', 1)[1] for x in terms)[:120]}); {(re.findall(r'A1-HOST ended.*', hl) or ['NO END LINE'])[0][:120]}")
    alive0 = left0.splitlines()[1:]
    tmo = [ln for ln in alive0 if re.search(r"^\d+ timeout 10 x04host_e198\.sh ", ln)]
    wrp = [ln for ln in alive0 if re.search(r"^\d+ bash x04host_e198\.sh ", ln)]
    ok("HG NO KILL: the host's timeout and its wrapper alive when the session ended (finding 6)", len(tmo) == 1 and len(wrp) == 1,
       f"alive at the session's end: timeout {len(tmo)}, wrapper {len(wrp)} ({'; '.join(x[:60] for x in tmo + wrp)})")
    spid = (rd(os.path.join(c.state, "sampler.pid")).split() or ["none"])[-1]
    smp = [ln for ln in alive0 if ln.split(" ", 1)[0] == spid or "ettelem" in ln]
    ok("HG K9: the clean-up stopped the sampler with SIGTERM though the device process did not end",
       "E198 A1: the sampler is stopped all the same (SIGTERM), so it does not hold the management node" in rl
       and f"ettelem sample pid {spid} ended (SIGTERM)" in c.calls and not smp
       and "A1-SAMPLER" not in rd(os.path.join(c.state, "a1-sampler.log")),
       f"run.log's K9 line {'present' if 'the sampler is stopped all the same' in rl else 'MISSING'}; the smoke's stand-in sampler (pid {spid}) "
       f"{'ended (SIGTERM)' if f'ettelem sample pid {spid} ended (SIGTERM)' in c.calls else 'NOT seen ending on SIGTERM'}; samplers alive at the "
       f"session's end: {len(smp)}; the end knob {'NOT needed' if 'A1-SAMPLER' not in rd(os.path.join(c.state, 'a1-sampler.log')) else 'ENDED A SAMPLER'}")
    ok("HG nothing left at the end", rd(os.path.join(c.state, "a1-left-at-end.txt")).strip().endswith(": 0 left"),
       rd(os.path.join(c.state, "a1-left-at-end.txt")).strip()[:100])


def hge(box):
    """HGE: the main run's first device process hangs past its TERM and ends by itself at 60 s, inside end_device()'s 60 s wait."""
    c = Case(box, "HGE", "B", maxs=900, cmd=[PY, "-I", "-B", os.path.abspath(__file__), "--hgwrap", "--", "bash",
                                            os.path.join(box.kit, "session_e198a1.sh"), "B"])
    c.knob("a1-hang", "11 60\n")              # the smoke has 10 device processes: call 11 is the main run's first
    c.run()
    c.common(1)
    rl = rd(c.f("x04", "run.log"))
    ev = [json.loads(x) for x in rd(c.f("x04", "events.jsonl")).splitlines() if x.startswith("{")]
    ended = [e for e in ev if e.get("kind") == "device_ended"]
    ok("HGE the stop, then end_device() reads it ended", c.stop_of("x04").startswith("stop: spin2: device process not ended 25 s after it started")
       and "device process still running 15 s after SIGTERM: tell the lab admin" in rl and ended and ended[0].get("rc") == 124
       and "device process not ended: the card lock goes only when this runner exits" not in rl,
       f"{c.stop_of('x04')[:90]}; device_ended {ended}")
    spid = (rd(os.path.join(c.state, "sampler.pid")).split() or ["none"])[-1]
    ok("HGE the clean-up goes on: the sampler stopped with SIGTERM", f"ettelem sample pid {spid} ended (SIGTERM)" in c.calls and "main run stopped: runner rc 1; stop: spin2: device "
       "process not ended" in c.log and "A DEVICE PROCESS DID NOT END in the x04 run" in c.log and "closing config read: skipped" in c.log,
       f"the main run's stand-in sampler (pid {spid}) 'ended (SIGTERM)'; the session's lines")
    hl, sig = hglog(c)
    ok("HGE NO KILL: its own end line at 60 s, TERMs only", re.search(r"A1-HOST ended by itself at 6\d\.\d+ s \(its life of 60 s\)", hl) and
       all(" TERM " in ln for ln in sig.splitlines() if ln.strip()), (re.findall(r"A1-HOST ended.*", hl) or ["NO END LINE"])[0][:140])


def hg2(box):
    """HG2: a host that ends 1.5 s after its TERM: the runner's timeout stop (124), as registered; no KILL at 11 s."""
    c = Case(box, "HG2", "B", maxs=900)
    c.knob("a1-hang", "11 40 1.5\n")
    c.run()
    c.common(1)
    rl = rd(c.f("x04", "run.log"))
    hl, sig = hglog(c)
    ok("HG2 the registered timeout stop, exit 124", c.stop_of("x04") == "stop: spin2: device process killed by timeout (tell the lab admin)" and
       re.search(r"pass 0 block C spin2: 0 launches, exit 124", rl) and "device process not ended" not in rl and "A DEVICE PROCESS" not in c.log,
       f"{c.stop_of('x04')}; {(re.findall(r'pass 0 block C spin2.*', rl) or ['no line'])[0]}")
    ok("HG2 NO KILL at 11 s: it ended by itself 1.5 s after its TERM", re.search(r"A1-HOST ended by itself at 11\.\d+ s \(1\.5 s after its first TERM\): 1 TERM", hl)
       and len([x for x in sig.splitlines() if x.strip()]) == 1, (re.findall(r"A1-HOST ended.*", hl) or ["NO END LINE"])[0][:140])


def killwords():
    """No code line of the runner copy, the A1 session, the host wrapper, the private /dev, the warden, the holder check, the guard shim, the
    identity reads or the A1 stand-ins names SIGKILL, signal 9, `kill -9`, `kill -KILL`, `timeout -k` or `--kill-after`, or calls .kill()."""
    pat = re.compile(r"SIGKILL|signal\.SIGKILL|\bkill\s+-(9|KILL|s\s*KILL|SIGKILL)\b|timeout\s+-k|--kill-after|\.kill\(\)|\"-k\"")
    hits = []
    for f in ("run_x04_e198a1.py", "session_e198a1.sh", "x04host_e198.sh", "privdev_e198.sh", "warden_e198.py", "holdercheck_e198.sh",
              "ettelem_guard_e198.sh", "ident_inner_e198.sh", "ident_e198.py", "dropruntime_e198.py", "fake_card_e198a1.py", "build_e198a1.sh"):
        for i, ln in enumerate(rd(os.path.join(E, f)).splitlines(), 1):
            code = ln.split("#", 1)[0] if f.endswith(".sh") else ln
            if pat.search(code):
                hits.append(f"{f}:{i}: {ln.strip()[:100]}")
    ok("KILLWORDS no kill word in a code line of the A1 session's files", not hits, f"{len(hits)} hit(s) {hits[:3]}")


AUDIT = [  # (file, line text start, dry path, real path, cases): v1's rows on A1's files, and A1's one dry-flag line more
    ("session_e198.sh", 'DRYF=', "the dry flag's default", "unset: the real path", "PB2,Y1"),
    ("session_e198.sh", 'case "${DRY-}" in', "DRY=1 sets the dry path", "DRY unset: the real path; any other value refused", "PB2,Y1"),
    ("session_e198.sh", 'if [ -z "$DRYF" ]; then', "no window's last end needed", "the window's last end required", "PB2"),
    ("session_e198.sh", 'SD=build/e198/T$T0; [ -n "$DRYF" ]', "the folder T<T0>-dry", "the folder T<T0>", "PB2,Y1"),
    ("session_e198.sh", 'say() {', "every line 'DRY '", "the plain line", "PB2,Y1"),
    ("session_e198.sh", '  if [ -n "$DRYF" ]; then\n    say "ET_DEVICES=1 privdev_e198.sh flock', "the closing read printed", "the closing config read inside the private /dev, identity (a) reported", "PB2,K1,X1"),
    ("session_e198.sh", '  [ -z "$DRYF" ] || return 0', "dne_check reads nothing", "A1: the runner's \'device process not ended\' line read; the session says so and skips its closing read", "HG,HGE,PB2"),
    ("session_e198.sh", 'say "session start', "'; DRY' in the start line", "the start line", "PB2,Y1"),
    ("session_e198.sh", 'if [ -n "$DRYF" ]; then\n  say "lib.sh', "the holder rules and the two-card box printed", "ps rules, et-who --check, the two-card box", "PB2,H0,NOC1"),
    ("session_e198.sh", 'if [ -n "$DRYF" ]; then\n  say "ET_DEVICES=1 privdev', "the start config read printed", "the start config read inside the private /dev, identity (a)", "PB2,IA0"),
    ("session_e198.sh", 'if [ -n "$DRYF" ]; then\n  say "warden', "the warden and identity (b) printed", "the warden started; the identity sampler; identity (b)", "PB2,IB0"),
    ("session_e198.sh", 'if [ -z "$DRYF" ] && [ $((LAST_END', "no clip", "the deadline clipped by the last end - 180 s", "PB2"),
    ("session_e198.sh", '[ -n "$DRYF" ] && COMMON+=(--dry)', "the runner's --dry", "the runner's real path", "PB2,Y1"),
    ("session_e198.sh", 'if [ -n "$DRYF" ]; then\n  say "check_e193.py smoke', "the smoke gate printed", "the watch, then E193's smoke gate", "PB2,W1"),
    ("session_e198.sh", 'if [ -n "$DRYF" ]; then\n  say "main run end', "the listing counted", "rc 0, a registered stop, or a crash", "PB2,K1,X1"),
    ("session_e198.sh", '[ -z "$DRYF" ] && [ -e "$SD/holderd/WATCH-STOP" ]', "skipped", "the watch's line, if any", "PB2,W1"),
    ("session_e198.sh", '[ -z "$DRYF" ] && say "the host', "skipped", "the host's runtime lines counted", "PB2"),
    ("session_e198.sh", 'rc=0; [ -z "$DRYF" ]', "rc 0", "rc 1 after a stop, 4 after a crash", "PB2,K1,X1"),
    ("run_x04.py", '    if not a.dry and bool(a.sampler)', "the sampler argument rule skipped", "exactly one of --sampler and --telemetry: the session passes --sampler", "PB2"),
    ("run_x04.py", '    if not a.dry and a.telemetry and', "skipped", "NOT ON THE SESSION'S PATH: --telemetry is never passed", "NOT-ON-PATH,PB2"),
    ("run_x04.py", '        if a.dry:\n            print(msg)', "say() also prints", "say() writes run.log only", "PB2,Y1"),
    ("run_x04.py", '        if a.dry:\n            print(f"DRY ET_DEVICES', "the device call printed", "the host wrapper under a plain timeout 10 (A1), its output to files, its exit read, at most 25 s waited", "PB2,K1,X1,NWI,NWL,HG,HGE,HG2"),
    ("run_x04.py", '        if a.dry:\n            return ""', "check_live returns nothing", "the live stops on new samples", "PB2,K1"),
    ("run_x04.py", '        if a.dry:\n            print(f"DRY {a.holder_check}', "the holder check printed", "the holder check through the warden, then the lock; a holder: wait and poll", "PB2"),
    ("run_x04.py", '        if a.dry or state["idle_ref"]', "idle-down skipped", "idle-down to the idle reference + 2 C", "PB2"),
    ("run_x04.py", '        if a.dry:\n            print(f"DRY count', "the one-card rule printed", "one_card() in the private /dev: one ops node, card 1's", "PB2,NWL"),
    ("run_x04.py", '        if not a.dry:\n            if a.sampler:', "no sampler", "the sampler through the shim and E191's guard, 20 s of idle, the reference", "PB2,K1"),
    ("run_x04.py", '                        if not a.dry:\n                            time.sleep(a.gap)', "no gap", "the 5 s gap", "PB2"),
    ("run_x04.py", '                if a.dry:\n                    print(f"DRY pass gap', "the pass gap printed", "30 s between passes, the lock closed", "PB2"),
    ("run_x04.py", '        if not a.dry:\n            time.sleep(a.gap + 3)', "no closing idle", "gap + 3 s after the last run", "NWL"),
]


def audit(box):
    files = {"session_e198.sh": rd(os.path.join(E, "session_e198a1.sh")), "run_x04.py": rd(os.path.join(E, "run_x04_e198a1.py"))}
    rows, bad = [], []
    for f, pat, dry, real, cs in AUDIT:
        i = files[f].find(pat)
        if i < 0:
            bad.append(f"{f}: no line '{pat[:40]}'")
            continue
        ln = files[f].count("\n", 0, i) + 1
        rows.append((f, ln, files[f].splitlines()[ln - 1].strip()[:90], dry, real, cs))
    want = {("session_e198.sh", n + 1) for n, x in enumerate(files["session_e198.sh"].splitlines()) if "DRYF" in x} | \
           {("run_x04.py", n + 1) for n, x in enumerate(files["run_x04.py"].splitlines()) if "a.dry" in x}
    have = {(f, ln) for f, ln, *_ in rows}
    passed = {n.split()[0] for n, c in RES if c}
    failed = {n.split()[0] for n, c in RES if not c}
    for f, ln, _t, _d, _r, cs in rows:
        for x in cs.split(","):
            if x != "NOT-ON-PATH" and (x not in passed or x in failed):
                bad.append(f"{f}:{ln}: case {x} did not pass")
    missing = sorted(want - have)
    with open(os.path.join(E, "desk", "dry-branches-e198a1.tsv"), "w") as o:
        o.write("# E198's dry-branch audit after amendment A1 (Q196, lane a1-e198): every line of session_e198a1.sh (named session_e198.sh in\n"
                "# the rows) and of the lab's runner copy run_x04_e198a1.py (named run_x04.py in the rows) that branches on a dry flag (DRYF;\n"
                "# a.dry), what the dry path does there, what the real path does, and the real-path desk test's cases that run it\n"
                "# (desk/desktest_realpath_e198a1.py, which writes this file and fails if a dry-flag line has no row or a named case failed).\n"
                "# file\tline\ttext\tdry path\treal path\tcases\n")
        for r in sorted(rows, key=lambda r: (r[0], r[1])):
            o.write("\t".join(str(x) for x in r) + "\n")
    ok("AUDIT every dry-flag line has a row and its cases passed", not missing and not bad,
       f"{len(rows)} rows ({sum(1 for r in rows if r[0] == 'session_e198.sh')} session, {sum(1 for r in rows if r[0] == 'run_x04.py')} runner); "
       f"lines without a row {missing}; {bad[:4]}")


def main(argv):
    if argv[:1] == ["--inner"]:
        return inner(argv[1:])
    if argv[:1] == ["--hgwrap"]:
        return hgwrap(argv[1:])
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if os.path.exists(S) and os.listdir(S):
        print(f"REFUSED: {S} is not an empty scratch folder")
        return 2
    real = [p for p in glob.glob("/dev/et*") if stat.S_ISCHR(os.stat(p).st_mode)]
    if real:
        print(f"REFUSED: character device(s) {real} visible: run inside W/nodev.sh")
        return 2
    os.makedirs(S, exist_ok=True)
    print(f"DESKTEST-REALPATH-E198-A1 on {os.uname().nodename}, {time.strftime('%F %T %Z')}, python {sys.version.split()[0]}, "
          f"bubblewrap {subprocess.run(['/usr/bin/bwrap', '--version'], capture_output=True, text=True).stdout.strip()}", flush=True)
    box = Box(S)
    print(f"   the stand-in box: {box.tree} (tree), E198's root, harness-e198-a1.json copy {box.hsha[:16]} (the stand-in reader's pin)", flush=True)
    main_cases(box)
    killwords()
    audit(box)
    for src, dst in (("dry-e198a1-smoke.txt", "dry-e198a1-smoke.txt"), ("dry-e198a1-A.txt", "dry-e198a1-A.txt"), ("dry-e198a1-B.txt", "dry-e198a1-B.txt")):
        if os.path.exists(os.path.join(S, src)):
            shutil.copyfile(os.path.join(S, src), os.path.join(E, "desk", dst))
    n = sum(1 for _, c in RES if c)
    print(f"DESKTEST-REALPATH-E198-A1 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}", flush=True)
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
