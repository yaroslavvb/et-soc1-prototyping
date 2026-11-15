#!/usr/bin/env python3
"""E193's REAL-PATH DESK TEST (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum).

    bash slot.sh bash nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e193/desk/desktest_realpath_e193.py <empty scratch dir> > log

THE LESSON (Fri 13 Nov 2026, both of E183's days): a check that runs only on the REAL path is never exercised by a dry pass. This test
runs SESSION_E193.SH'S REAL PATH, DRY UNSET, exactly as step 9 launches it (E193_T0, E193_LAST_END_EPOCH, E193_HARNESS_SHA256, the
sitting), and through it the proposal's runner as committed (run_x04.py, unchanged) with its real --sampler path through E128's guard
(unchanged), against stand-ins for every device tool (fake_card_e193.py: the sampler build/ettelem/ettelem and its config, et-who, the
host x04clock_host) and loggers in front of the system's timeout and flock. Each case runs in its OWN SANDBOX inside the no-device one
(bubblewrap: a private /dev holding only a plain scratch file at /dev/et0_ops, the runner's and the host's one-card rule; a private,
empty /run/lock, a scratch directory, so the card lock is a scratch file; a private PID namespace, so ps and et-who see only the
case's processes; the host name aifoundry3), and refuses to start if a character device /dev/et* is visible. Real timing throughout:
20 s of idle reference, 5 s gaps, 0.4 s launches, 30 s between passes.

Cases (each asserts the session's log, its exit status, the runner's files, the stand-ins' call log, the manifest, and that no
process of the case is left):
  PA   sitting A, its real path: the first card command, the one ops node, the start config (both config reads with ET_DEVICES=0), the
       smoke (10 calls) and SMOKE GO, the main run's passes 0
       and 1 whole (26 calls each), then the operator's stop file: "main run stopped" (rc 1), the closing config read, the manifest;
       the deadline is the first card command + 3,480 s; the runner's holder check exempts the sampler by its process id at every
       block; idle-down waits; each sampler stopped by SIGTERM; then the collection (collect_e193.py) and THE REGISTERED REDUCER and
       the kit's checker on what it collected;
  PB   sitting B, its real path WHOLE: the smoke, all 9 passes (15 calls each), "main run end: runner rc 0, every pass", rc 0; the
       runner's normal end; the collection, the reducer and the checker;
  K1-K7 THE RUNNER'S STOP LINES on live samples and device exits, in the smoke: the board above 65 W three samples in a row (K1), the
       die at 70 C (K2), the clock off 600 MHz three samples in a row (K3) and only twice (K3N: no stop), the sampler stalled (K4), a
       device process exit 1 (K5), three exits 3 (K6) and one (K6N: no stop), a short train (K6S: the gate reads it), a device process
       killed by `timeout -k 1 10` (K7): each a GATE-STOP after the smoke, nothing of the main run started;
  H1   a holder (another user's lock line) at the start: GATE-STOP before any device (no config read, no sampler, no host);
  H2   a holder appearing between the smoke's blocks: the runner waits ("card not free"), the operator's stop ends it; H3 the same
       holder left there: the runner's own stop after 10 minutes of 30 s polls ("card not free for 10 minutes");
  L1   the card lock held (by a process the case's et-who cannot see) at the start: the start config read cannot take it: GATE-STOP;
  L2   the card lock taken after the smoke (by a process the case's et-who cannot see): the main runner's flock fails at its first
       holder check ("card lock ... held"), the operator's stop ends it, the closing read finds the lock held;
  G1   the smoke gate reads a launch not ok (exit 3 on the smoke's first call): SMOKE NO-GO, GATE-STOP, no main run;
  G2   the start config at TDP 5 W: GATE-STOP before the smoke;
  N2, N0  two ops nodes, and none: THE SESSION'S OWN COUNT OF OPS NODES, after the holder check and before any card read, stops it:
       GATE-STOP (no device opened), no config read, no sampler, no smoke, no host call (fix-e193, verify-e193's finding 3: the kit's form
       made its start config read first and left the count to the smoke's runner);
  D1   THE DEADLINE, clipped by a window's last end 390 s away: the runner stops at it during the main run ("deadline"), rc 1;
  T1   SIGTERM to the main runner during a launch: the runner ends the device process, releases the lock, stops its sampler; rc 1;
  X1   A CRASH OF THE MAIN RUN: after the main run's second call the stand-in host prints a malformed X04 line once (exit 0); the runner
       raises (a traceback, no STOPPED), its sampler stopped by SIGTERM; the session writes "main run ended without a registered stop"
       (never "main run stopped"), makes the closing read and exits 4; the collector records session rc 4 (fix-e193, verify-e193's
       finding 5);
  O1   a device process of ours (named ettelem) running at the start: GATE-STOP, no device opened;
  B1-B4  the harness's sha256 not the launch's (B1), a synced file changed (B2), a host the build did not record (B3), the host's name
       not aifoundry3 (B4): each GATE-STOP, no device opened;
  S1   the operator's stop file in the session's directory before the smoke (the holder check made to wait 3 s): GATE-STOP; the cap's
       start (first-card-command.txt) stamped BEFORE that holder check began, not after its 3 s (fix-e193, verify-e193's finding 4); S1B the
       same file written during the smoke: the smoke runs whole (its own stop file is smoke/STOP), then GATE-STOP before the main run;
       S2 the runner's own stop file made before the main run starts: "main run stopped" at its first check, no main sampler;
  Y1   THE DRY PATH (DRY=1): rc 0, build/e193/T<T0>-dry, every line "DRY ", both listings equal to the registration's, no stand-in
       called; Y2 DRY=2 refused; Y3 no window's last end on the real path refused;
  AUDIT every branch of session_e193.sh and run_x04.py that a dry flag skips (desk/dry-branches-e193.tsv, read against the files' own
       lines) is run by a case above that passed.
EVERY WATT AND DEGREE HERE IS THE STAND-INS' ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT. Prints
DESKTEST-REALPATH-E193 <n> of <m> PASS (or FAIL). Exit 0 on PASS, 1 on FAIL, 2 on a usage or sandbox refusal.
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
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
FAKE = os.path.join(E, "fake_card_e193.py")
PY = "/usr/bin/python3"
RES = []
SKIP = False


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def put(path, text, mode=0o644):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, mode)


def rd(path):
    try:
        with open(path, errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def ok(name, cond, detail):
    if SKIP:
        return
    RES.append((name, bool(cond)))
    print(f"-> {'PASS' if cond else 'FAIL'} ({name}: {detail})", flush=True)


# ---------------------------------------------------------------------------------------------------------------- the inner side
def inner(argv):
    """Run inside the case's sandbox: optionally a decoy device process of ours, then the session; returns its exit status."""
    mode = argv[0]
    cmd = argv[argv.index("--") + 1:]
    decoy = None
    if mode == "decoy":
        d = os.path.join(os.environ["E193_FAKE_STATE"], "decoy")
        os.makedirs(d, exist_ok=True)
        shutil.copy2("/bin/sleep", os.path.join(d, "ettelem"))
        decoy = subprocess.Popen([os.path.join(d, "ettelem"), "120"])
        time.sleep(0.3)
    try:
        return subprocess.run(cmd).returncode
    finally:
        if decoy:
            decoy.kill()
            decoy.wait()


# ---------------------------------------------------------------------------------------------------------------- the outer side
class Box:
    def __init__(self, S):
        self.S = S
        self.home = os.path.join(S, "home")
        self.tree = os.path.join(self.home, "aifoundry")
        self.root = os.path.join(self.tree, "build/claims-v3/aifoundry3/e193")
        self.bin = os.path.join(S, "bin")
        self.kit = os.path.join(self.root, "tools/claims-v3/e193")
        self.host = os.path.join(self.root, "build/x04clock/host/x04clock_host")
        self.kernel = os.path.join(self.root, "build/x04clock/kernel/x04clock.elf")
        self.built = os.path.join(self.root, "build/x04clock-built.txt")
        lst = subprocess.run([PY, "-I", "-B", os.path.join(E, "harness_e193.py"), "--list"], capture_output=True, text=True,
                             check=True).stdout.split()
        for p in lst:
            dst = os.path.join(self.root, p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(SRC, p), dst)
        self.nsync = len(lst)
        wrap = '#!/bin/bash\nexec %s -I -B %s %s "$@"\n'
        put(os.path.join(self.tree, "build/ettelem/ettelem"), wrap % (PY, FAKE, "ettelem"), 0o755)
        put(self.host, wrap % (PY, FAKE, "host"), 0o755)
        put(self.kernel, "stand-in kernel ELF for E193's real-path desk test (never loaded)\n")
        put(os.path.join(self.bin, "et-who"), wrap % (PY, FAKE, "etwho"), 0o755)
        for c, real in (("timeout", "/usr/bin/timeout"), ("flock", "/usr/bin/flock")):
            put(os.path.join(self.bin, c), '#!/bin/bash\necho "$(date +%%s.%%N) %s $*" >> "$E193_FAKE_STATE/calls.log"\nexec %s "$@"\n'
                % (c, real), 0o755)
        for c in ("ssh", "scp", "rsync", "sudo"):
            put(os.path.join(self.bin, c), '#!/bin/sh\necho "STAND-IN %s: refused (no network, no privilege at the desk)" >&2\nexit 97\n' % c,
                0o755)
        self.write_built()
        self.hsha = sha(os.path.join(self.kit, "harness-e193.json"))
        for n in (0, 1):
            put(os.path.join(S, f"node{n}"), "")

    def write_built(self, host_sha=None):
        put(self.built, "X04-BUILT %s (stand-in record of the desk test)\nkernel %s\ntext (stand-in)\nhost %s\nsampler %s\n" % (
            time.strftime("%F %T %Z"), sha(self.kernel), host_sha or sha(self.host), sha(os.path.join(self.tree, "build/ettelem/ettelem"))))


def procs_with(state):
    """Process ids (outer namespace) whose environment names this case's stand-in state."""
    out = []
    key = ("E193_FAKE_STATE=" + state).encode()
    for p in glob.glob("/proc/[0-9]*"):
        try:
            if key in open(p + "/environ", "rb").read().split(b"\0"):
                out.append(int(p.split("/")[2]))
        except OSError:
            continue
    return [p for p in out if p != os.getpid()]


def runner_pid(out_rel):
    """The runner whose output folder is out_rel (the session passes it relative to the box's tree: build/e193/T<T0>/x04)."""
    for p in glob.glob("/proc/[0-9]*"):
        try:
            cmd = open(p + "/cmdline", "rb").read().split(b"\0")
        except OSError:
            continue
        if any(c.endswith(b"run_x04.py") for c in cmd) and out_rel.encode() in cmd:
            return int(p.split("/")[2])
    return None


class Case:
    def __init__(self, box, name, sit, nodes=(0,), host="aifoundry3", inner_mode="plain", last_end=4 * 3600, dry=False,
                 env=None, hsha=None, maxs=900):
        self.b, self.name, self.sit = box, name, sit
        self.state = os.path.join(box.S, "state-" + name)
        self.runlock = os.path.join(box.S, "runlock-" + name)
        os.makedirs(self.state)
        os.makedirs(self.runlock)
        t = int(time.time())
        while int(time.time()) == t:
            time.sleep(0.05)
        self.T0 = int(time.time())
        self.last_end = self.T0 + last_end if last_end else None
        self.sd = os.path.join(box.tree, "build/e193", "T%d%s" % (self.T0, "-dry" if dry else ""))
        self.nodes, self.hostname, self.inner_mode, self.dry, self.maxs = nodes, host, inner_mode, dry, maxs
        self.env = {"PATH": box.bin + ":/usr/bin:/bin", "HOME": box.home, "USER": "boxuser", "LOGNAME": "boxuser", "LC_ALL": "C",
                    "E193_FAKE_STATE": self.state, "E193_T0": str(self.T0), "E193_HARNESS_SHA256": hsha or box.hsha}
        if self.last_end:
            self.env["E193_LAST_END_EPOCH"] = str(self.last_end)
        if dry:
            self.env["DRY"] = "1" if dry is True else str(dry)
        self.env.update(env or {})
        self.done = set()

    def f(self, *p):
        return os.path.join(self.sd, *p)

    def has(self, rel, pat):
        return re.search(pat, rd(self.f(rel)), re.M) is not None

    def once(self, key, cond, act):
        if key not in self.done and cond():
            self.done.add(key)
            act()

    def touch(self, p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "a").close()

    def knob(self, name, text=""):
        put(os.path.join(self.state, name), text)

    only = None

    def run(self, watch=None):
        global SKIP
        self.skipped = Case.only is not None and self.name not in Case.only
        SKIP = self.skipped
        if self.skipped:
            self.rc, self.secs, self.left, self.log, self.calls = None, 0, [], "", ""
            return self
        cmd = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev"]
        for n in self.nodes:
            cmd += ["--bind", os.path.join(self.b.S, f"node{n}"), f"/dev/et{n}_ops"]
        cmd += ["--bind", self.runlock, "/run/lock", "--proc", "/proc", "--unshare-pid", "--unshare-uts", "--hostname",
                self.hostname, "--die-with-parent", "--chdir", self.b.tree, "--", PY, "-I", "-B", os.path.abspath(__file__),
                "--inner", self.inner_mode, "--", "bash", os.path.join(self.b.kit, "session_e193.sh"), self.sit]
        t0 = time.time()
        p = subprocess.Popen(cmd, env=self.env, stdout=open(os.path.join(self.state, "session.stdout"), "w"),
                             stderr=subprocess.STDOUT, start_new_session=True)
        killed = False
        while p.poll() is None:
            if watch:
                watch(self)
            if time.time() - t0 > self.maxs:
                os.killpg(p.pid, signal.SIGKILL)
                killed = True
            time.sleep(0.2)
        self.rc = p.returncode
        self.secs = time.time() - t0
        time.sleep(0.5)
        self.left = procs_with(self.state)
        self.log = rd(self.f("session.log"))
        self.calls = rd(os.path.join(self.state, "calls.log"))
        print(f"   [{self.name}] sitting {self.sit}: exit {self.rc} after {self.secs:.0f} s{' (KILLED at its bound)' if killed else ''}; "
              f"session dir {os.path.basename(self.sd)}", flush=True)
        for ln in self.log.splitlines():
            if re.search(r"GATE-STOP|main run|smoke (start|end)|SMOKE|first card|config read|deadline|session (start|end)", ln):
                print("     | " + ln[24:224], flush=True)
        return self

    def manifest_ok(self):
        m = self.f("MANIFEST.sha256")
        if not os.path.exists(m):
            return False
        r = subprocess.run(["sha256sum", "-c", "--quiet", "MANIFEST.sha256"], cwd=self.sd, capture_output=True, text=True)
        return r.returncode == 0

    def ncalls(self, word):
        return len(re.findall(r"^\S+ " + word, self.calls, re.M))

    def stop_of(self, rel):
        return subprocess.run([PY, "-I", "-B", os.path.join(E, "check_e193.py"), "stopreason", self.f(rel)], capture_output=True,
                              text=True).stdout.strip()

    def runlog_calls(self, rel):
        return re.findall(r"^pass (\d+) block (\S+) (\S+): (\d+) launches, exit (-?\d+)", rd(self.f(rel, "run.log")), re.M)

    def common(self, want_rc, gate=None, main=None):
        """The assertions every case shares: its exit, the gate line or none, the manifest, nothing left running."""
        ok(self.name + " exit", self.rc == want_rc, f"session exit {self.rc}, want {want_rc}")
        g = re.findall(r"GATE-STOP: (.*)", self.log)
        if gate is None:
            ok(self.name + " no gate", not g, f"no GATE-STOP line ({len(g)})")
        else:
            ok(self.name + " gate", g and re.search(gate, g[0]), f"GATE-STOP: {g[0][:150] if g else '(none)'}")
        ok(self.name + " end", "session end (T0 %d)" % self.T0 in self.log and self.manifest_ok() and rd(self.f("session.rc")).strip()
           == str(want_rc), f"'session end', MANIFEST.sha256 verifying ({sum(1 for _ in open(self.f('MANIFEST.sha256')))} files) and session.rc "
           f"{rd(self.f('session.rc')).strip()}" if os.path.exists(self.f("MANIFEST.sha256")) else "no MANIFEST.sha256")
        ok(self.name + " nothing left", not self.left, f"processes of the case left: {self.left}")


def smoke_first_call(c):
    return bool(c.runlog_calls("smoke"))


def main_started(c):
    return "main run start" in rd(c.f("session.log"))


def cases(box):
    global SKIP
    # ---- the two long cases run in threads beside the others, each in its own sandbox: PB (sitting B whole) and H3 (the 10-minute wait)
    pb = Case(box, "PB", "B", maxs=3000)
    pbt = threading.Thread(target=pb.run)
    pbt.start()
    h3 = Case(box, "H3", "A", maxs=1000)
    h3t = threading.Thread(target=h3.run, args=(lambda c: c.once("f", lambda: len(c.runlog_calls("smoke")) >= 1, lambda: c.knob(
        "foreign", "lock:etsoc-shire0.lock otheruser 4244 00:03 someone-elses-block.sh\n")),))
    h3t.start()
    # ---- PA: sitting A's real path, two whole passes, then the operator's stop
    seen = {}

    def wpa(c):
        c.once("seen", lambda: len(c.runlog_calls("x04")) >= 1, lambda: seen.setdefault("n", len(procs_with(c.state))))
        c.once("stop", lambda: c.has("x04/run.log", r"^pass 1 done"), lambda: c.touch(c.f("x04", "STOP")))
    c = Case(box, "PA", "A", maxs=1500).run(wpa)
    c.common(1)
    ok("PA control", seen.get("n", 0) >= 2, f"while the main run ran, the driver's scan saw {seen.get('n', 0)} processes of the case (the "
       f"session, the runner, its sampler ...): its later empty scans mean the case's processes ended, not a blind scan")
    first = int(rd(c.f("first-card-command.txt")) or 0)
    dl = re.search(r"\(epoch (\d+): the first card command \+ 3600 s - 120 s", c.log)
    ok("PA deadline", dl and int(dl.group(1)) == first + 3480, f"deadline {dl.group(1) if dl else '?'} = first card command {first} + 3,480 s")
    ok("PA order", all(s in c.log for s in ("HARNESS OK: ", "preflight: dmcmd_audit: GO", "binaries: host", "the first card command (the "
                                             "holder check): free", "start config read: TDP 0 W, 65 C, minion 600 MHz", "SMOKE GO: 10 of 10",
                                             "main run start", "main run stopped: runner rc 1; stop: stop file", "closing config read: TDP 0 W")),
       "harness, preflight, binaries, first card command, start config, SMOKE GO, main run, its stop, closing config: all in the log")
    sm = c.runlog_calls("smoke")
    mn = c.runlog_calls("x04")
    per = {p: sum(1 for x in mn if x[0] == p) for p in ("0", "1", "2")}
    ok("PA passes", len(sm) == 10 and per["0"] == 26 and per["1"] == 26 and per["2"] == 0 and all(x[4] == "0" for x in sm + mn),
       f"smoke {len(sm)} calls; main pass 0 {per['0']}, pass 1 {per['1']}, pass 2 {per['2']} calls; every exit 0")
    runs = [json.loads(x) for x in rd(c.f("x04/runs.jsonl")).splitlines() if x.strip()]
    ok("PA records", runs and all(r["ok"] and r["rc"] == 0 for r in runs) and {r["host"] for r in runs} == {"aifoundry3"},
       f"{len(runs)} launch records, every one ok with rc 0, host aifoundry3")
    ev = [json.loads(x) for x in rd(c.f("x04/events.jsonl")).splitlines() if x.strip()]
    kinds = [e["kind"] for e in ev]
    ok("PA idle", "idle_ref" in kinds and kinds.count("idle_down") >= 1 and "card_busy" not in kinds,
       f"idle_ref once, idle_down waits {kinds.count('idle_down')}, card_busy {kinds.count('card_busy')} (the sampler exempt by its pid)")
    nw, ns, nh, nc = c.ncalls("et-who --check"), c.ncalls("ettelem sample --seconds"), c.ncalls("host "), c.ncalls("ettelem config")
    ok("PA calls", nw >= 1 + 5 + 8 and ns == 2 and nh == 62 and nc == 2 and c.calls.count("ended (SIGTERM)") == 2 and
       c.ncalls("timeout -k 1 10 ") == 62 and len(re.findall(r"^\S+ flock -n /run/lock/etsoc-shire0.lock timeout 10 ", c.calls, re.M)) == 2,
       f"et-who --check {nw} (the session's 1, then before each block), samplers {ns} (each ended by SIGTERM), host calls {nh} under "
       f"timeout -k 1 10, config reads {nc} under flock -n and timeout 10")
    ok("PA card 0", len(re.findall(r"^\S+ ettelem config ET_DEVICES=0$", c.calls, re.M)) == 2 and
       "the one ops node /dev/et0_ops" in c.log, "both config reads ran with ET_DEVICES=0; the session counted one ops node, /dev/et0_ops, "
       "before its first card read")
    yield c
    # ---- K1-K7: the stop lines, in the smoke
    for name, knob, want in (("K1", ("board66", ""), r"board above 65 W on three samples in a row"),
                             ("K2", ("die70", ""), r"die reading 70 C"),
                             ("K3", ("mhz500", "3"), r"minion clock 500(\.0)?, not 600 MHz, on three samples in a row"),
                             ("K4", ("stall", ""), r"telemetry not growing for 5 s"),
                             ("K5", ("host-mode", "rc1 1\n"), r"device process exit 1 \(a launch that did not finish"),
                             ("K6", ("host-mode", "rc3 3\n"), r"three device processes returned an incomplete launch"),
                             ("K7", ("host-mode", "hang 1\n"), r"device process killed by timeout")):
        c = Case(box, name, "A", maxs=400).run(lambda c, k=knob: c.once("k", lambda: smoke_first_call(c), lambda: c.knob(*k)))
        c.common(3, gate="the smoke gate failed")
        ok(name + " stop line", re.search(want, c.stop_of("smoke")) and not os.path.exists(c.f("x04")),
           f"{c.stop_of('smoke')[:120]}; no main run")
        yield c
    for name, knob, nexp in (("K3N", ("mhz500", "2"), "clock"), ("K6N", ("host-mode", "rc3 1\n"), "incomplete")):
        def wn(c, k=knob):
            c.once("k", lambda: smoke_first_call(c), lambda: c.knob(*k))
            c.once("stop", lambda: len(c.runlog_calls("smoke")) >= 4, lambda: c.touch(c.f("smoke", "STOP")))
        c = Case(box, name, "A", maxs=400).run(wn)
        c.common(3, gate="the smoke gate failed")
        ev = [json.loads(x) for x in rd(c.f("smoke/events.jsonl")).splitlines() if x.strip()]
        ok(name + " no stop", c.stop_of("smoke") == "stop: stop file" and (name != "K6N" or sum(e["kind"] == "incomplete" for e in ev) == 1),
           f"{c.stop_of('smoke')} (not the {nexp} line); incomplete events {sum(e['kind'] == 'incomplete' for e in ev)}")
        yield c
    c = Case(box, "K6S", "A", maxs=400).run(lambda c: c.once("k", lambda: smoke_first_call(c), lambda: c.knob("host-mode", "short 1\n")))
    c.common(3, gate=r"the smoke gate failed: SMOKE NO-GO: .*tr_tk_spin1")
    ev = [json.loads(x) for x in rd(c.f("smoke/events.jsonl")).splitlines() if x.strip()]
    ok("K6S short train", any(e["kind"] == "short_train" for e in ev) and "(short train: dropped)" in rd(c.f("smoke/run.log")),
       "the runner's short_train event and its '(short train: dropped)'; the gate names the train")
    yield c
    # ---- H1, H2: holders
    c = Case(box, "H1", "A", maxs=120)
    c.knob("foreign", "lock:etsoc-shire0.lock otheruser 4242 00:01 bash someone-elses-run.sh\n")
    c.run()
    c.common(3, gate=r"the card is held: et-who --check lists 1 holder line\(s\) \(no device opened\)")
    ok("H1 nothing opened", c.ncalls("ettelem") == 0 and c.ncalls("host ") == 0, "no config read, no sampler, no host call")
    yield c

    def wh2(c):
        c.once("f", lambda: len(c.runlog_calls("smoke")) >= 1,
               lambda: c.knob("foreign", "/dev/et0_ops otheruser 4243 00:02 someone_host\n"))
        c.once("stop", lambda: c.has("smoke/run.log", r"card not free \(pass 0 block [A-Z]\)"), lambda: c.touch(c.f("smoke", "STOP")))
    c = Case(box, "H2", "A", maxs=400).run(wh2)
    c.common(3, gate="the smoke gate failed")
    ok("H2 holder read", c.has("smoke/run.log", r"card not free \(pass 0 block [A-Z]\): /dev/et0_ops otheruser 4243") and
       c.stop_of("smoke") == "stop: stop file", "the runner read the other holder's line at its next block, waited, then the stop file")
    yield c
    # ---- L1, L2: the card lock held by a process the case's et-who cannot see
    c = Case(box, "L1", "A", maxs=120)
    fd = os.open(os.path.join(c.runlock, "etsoc-shire0.lock"), os.O_RDONLY | os.O_CREAT, 0o666)
    fcntl.flock(fd, fcntl.LOCK_EX)
    c.run()
    os.close(fd)
    c.common(3, gate=r"no start config read came back \(the card lock held")
    ok("L1 no smoke", not os.path.exists(c.f("smoke")) and c.ncalls("host ") == 0, "no smoke, no host call")
    yield c
    held = {}

    def wl2(c):
        def grab():
            fd = os.open(os.path.join(c.runlock, "etsoc-shire0.lock"), os.O_RDONLY | os.O_CREAT, 0o666)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                held["fd"] = fd
            except OSError:
                os.close(fd)
        c.once("sleep", lambda: c.has("smoke/run.log", r"^pass 0 block C spin2:"), lambda: c.knob("etwho-sleep", "4"))
        if "fd" not in held and "SMOKE GO" in rd(c.f("session.log")):
            grab()
        c.once("stop", lambda: c.has("x04/run.log", r"card lock /run/lock/etsoc-shire0.lock held"), lambda: c.touch(c.f("x04", "STOP")))
    c = Case(box, "L2", "A", maxs=400).run(wl2)
    took = "fd" in held
    if took:
        os.close(held.pop("fd"))
    c.common(1)
    ok("L2 lock read", took and c.has("x04/run.log", r"card not free \(session start\): card lock /run/lock/etsoc-shire0.lock held") and
       c.stop_of("x04") == "stop: stop file" and "closing config read: none came back" in c.log,
       "the main runner's flock failed at its first holder check (et-who saw no holder: the lock's holder is outside the case's "
       "namespace), it waited, the operator's stop ended it; the closing read found the lock held, reported")
    yield c
    # ---- G1, G2: the smoke gate and the config gate
    c = Case(box, "G1", "A", maxs=400)
    c.knob("host-mode", "notok 1\n")
    c.run()
    c.common(3, gate=r"the smoke gate failed: SMOKE NO-GO: spin2 \(block S\) exited 3")
    ok("G1 no main", not os.path.exists(c.f("x04")) and "closing config read: TDP 0 W" in c.log,
       "no main run; the closing config read after the gate stop")
    yield c
    c = Case(box, "G2", "A", maxs=120)
    c.knob("config.json", '{"tdp_w":5,"temp_threshold_c":65,"power_state":"managed_power","minion_mhz":600}\n')
    c.run()
    c.common(3, gate=r"the start config is not TDP 0 W / 65 C / 600 MHz as found")
    ok("G2 no smoke", not os.path.exists(c.f("smoke")), "no smoke")
    yield c
    # ---- N2, N0: the one-card rule
    for name, nodes in (("N2", (0, 1)), ("N0", ())):
        c = Case(box, name, "A", nodes=nodes, maxs=200).run()
        seen = "/dev/et0_ops /dev/et1_ops" if nodes else "none"
        c.common(3, gate=r"the host shows ops node\(s\) \[%s\], not exactly /dev/et0_ops: .*\(no device opened\)" % seen)
        ok(name + " one card", c.ncalls("et-who --check") == 1 and c.ncalls("ettelem") == 0 and c.ncalls("host ") == 0 and
           not os.path.exists(c.f("smoke")) and not os.path.exists(c.f("config-start.json")),
           "the holder check ran, then the session's own count of ops nodes stopped it: no config read, no sampler, no smoke, no host call")
        yield c
    # ---- D1: the deadline, clipped by a window's last end
    c = Case(box, "D1", "A", last_end=390, maxs=600).run()
    c.common(1)
    dl = re.search(r"\(epoch (\d+): ", c.log)
    ok("D1 deadline", dl and int(dl.group(1)) == c.last_end - 180 and "main run stopped: runner rc 1; stop: deadline" in c.log and
       len(c.runlog_calls("x04")) >= 1, f"deadline {dl.group(1) if dl else '?'} = the last end - 180 s; the main run stopped at it after "
       f"{len(c.runlog_calls('x04'))} calls")
    yield c

    # ---- T1: SIGTERM to the main runner during a launch
    sent = {}

    def wt1(c):
        if "pid" in sent or not (main_started(c) and len(c.runlog_calls("x04")) >= 1 and os.path.exists(os.path.join(c.state, "burst.json"))):
            return
        p = runner_pid("build/e193/T%d/x04" % c.T0)
        if p:
            os.kill(p, signal.SIGTERM)
            sent["pid"] = p
    c = Case(box, "T1", "A", maxs=600).run(wt1)
    c.common(1)
    ok("T1 sent", "pid" in sent, f"SIGTERM sent to the main runner (pid {sent.get('pid')}) while a launch ran")
    ok("T1 signal", "main run stopped: runner rc 143; stop: signal 15" in c.log and c.has("x04/run.log", r"ending the running device process")
       and c.calls.count("ended (SIGTERM)") == 2, "rc 143, 'signal 15'; the runner ended the device process, then its sampler (SIGTERM)")
    yield c
    # ---- X1: a crash of the main run (a malformed X04 line from the stand-in host, which then exits 0)
    c = Case(box, "X1", "A", maxs=600).run(lambda c: c.once("k", lambda: len(c.runlog_calls("x04")) >= 2,
                                                            lambda: c.knob("host-mode", "garble 1\n")))
    c.common(4)
    rout = rd(c.f("runner.out"))
    ok("X1 crash read", "main run ended without a registered stop: runner rc 1; no stop recorded (the runner's log does not end 'done')"
       in c.log and "main run stopped" not in c.log and "Traceback" in rout and not os.path.exists(c.f("x04", "STOPPED")) and
       "closing config read: TDP 0 W" in c.log and c.calls.count("ended (SIGTERM)") == 2,
       "the runner raised on the malformed X04 line (a traceback in runner.out, no STOPPED), its sampler ended by SIGTERM; the session "
       "wrote 'main run ended without a registered stop', never 'main run stopped', made the closing read, exit 4")
    raw = os.path.join(box.S, "raw-X1")
    shutil.copytree(c.sd, raw)
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "collect_e193.py"), raw, os.path.join(box.S, "data-X1"), "--box-home", box.home,
                        "--sitting", "A", "--login", "boxuser"], capture_output=True, text=True)
    fx = json.load(open(os.path.join(box.S, "data-X1", "facts-e193-a.json"))) if r.returncode == 0 else {}
    ok("X1 collected", r.returncode == 0 and fx.get("session_rc") == "4" and any("without a registered stop" in x for x in
                                                                                fx.get("session_lines", [])),
       f"the collector on the crash: rc {r.returncode}; facts session_rc {fx.get('session_rc')}, its crash line kept")
    yield c
    # ---- O1: a device process of ours at the start
    c = Case(box, "O1", "A", inner_mode="decoy", maxs=120).run()
    c.common(3, gate=r"a device process of ours is running \(1\) \(no device opened\)")
    yield c
    # ---- B1-B4: the pins and the box
    c = Case(box, "B1", "A", hsha="0" * 64, maxs=60).run()
    c.common(3, gate=r"harness-e193.json reads .*, not the launch's 0000.* \(no device opened\)")
    yield c
    victim = os.path.join(box.kit, "check_e193.py")
    keep = open(victim, "rb").read()
    open(victim, "ab").write(b"# one line more\n")
    c = Case(box, "B2", "A", maxs=60).run()
    open(victim, "wb").write(keep)
    c.common(3, gate=r"the harness check failed: HARNESS FAIL: differs tools/claims-v3/e193/check_e193.py \(no device opened\)")
    yield c
    box.write_built(host_sha="f" * 64)
    c = Case(box, "B3", "A", maxs=60).run()
    box.write_built()
    c.common(3, gate=r"the host or the kernel is not the one today's build recorded")
    yield c
    c = Case(box, "B4", "A", host="aifoundry2", maxs=60).run()
    c.common(3, gate=r"this is aifoundry2, not aifoundry3")
    yield c
    # ---- S1, S2: the operator's stop
    c = Case(box, "S1", "A", maxs=120)
    c.knob("etwho-sleep", "3")          # the holder check waits 3 s, so the stop file lands before the smoke's check, not in a race
    c.run(lambda c: c.once("s", lambda: os.path.exists(c.f("session.log")), lambda: c.touch(c.f("STOP"))))
    c.common(3, gate=r"the operator's stop file .* is present before the smoke")
    ok("S1 no smoke", not os.path.exists(c.f("smoke")), "no smoke")
    first = int(rd(c.f("first-card-command.txt")) or 0)
    ew = [float(x.split()[0]) for x in c.calls.splitlines() if x.split()[1:3] == ["et-who", "--check"]]
    ok("S1 cap start", first > 0 and ew and first <= ew[0] < first + 2,
       f"first-card-command.txt {first} stamped before the holder check began ({ew[0] if ew else '?'}: et-who then waited 3 s)")
    yield c
    c = Case(box, "S1B", "A", maxs=400).run(lambda c: c.once("s", lambda: len(c.runlog_calls("smoke")) >= 2, lambda: c.touch(c.f("STOP"))))
    c.common(3, gate=r"the operator's stop file .* is present before the main run")
    ok("S1B smoke whole", len(c.runlog_calls("smoke")) == 10 and not os.path.exists(c.f("x04")),
       "the session's stop file does not stop the running smoke (its own is smoke/STOP): the smoke ran its 10 calls, no main run")
    yield c
    # the runner's own stop file, made before the main runner starts (during the smoke's last block), so the runner meets it at its
    # first check, before its holder check and its sampler (run_x04.py's start: one card, then the stop file and the deadline)
    c = Case(box, "S2", "A", maxs=400).run(lambda c: c.once("s", lambda: c.has("smoke/run.log", r"^pass 0 block C spin2:"),
                                                           lambda: c.touch(c.f("x04", "STOP"))))
    c.common(1)
    ok("S2 runner's stop", "main run stopped: runner rc 1; stop: stop file" in c.log and c.ncalls("ettelem sample --seconds") == 1 and
       not c.runlog_calls("x04"), "the main runner stopped before its sampler and any call")
    yield c
    # ---- Y1-Y3: the dry path and two refusals
    c = Case(box, "Y1", "A", dry=True, last_end=None, maxs=120).run()
    lines = [x for x in c.log.splitlines() if x.strip()]
    ok("Y1 dry", c.rc == 0 and lines and all(re.match(r"^\S+ \S+ \S+ DRY ", x) for x in lines) and c.manifest_ok() and
       c.calls.strip() == "", f"exit {c.rc}, {len(lines)} log lines all 'DRY ', the manifest, no stand-in called")
    host_rel = os.path.relpath(box.host, box.tree)
    a = subprocess.run([PY, "-I", "-B", os.path.join(E, "check_e193.py"), "drycmp", c.f("smoke-runner.out"),
                        os.path.join(E, "desk/dry-e193-smoke-all.txt"), "--host", host_rel], capture_output=True, text=True)
    b = subprocess.run([PY, "-I", "-B", os.path.join(E, "check_e193.py"), "drycmp", c.f("runner.out"), os.path.join(E, "desk/dry-e193-A.txt"),
                        "--host", host_rel], capture_output=True, text=True)
    ok("Y1 listings", a.returncode == 0 and b.returncode == 0, a.stdout.strip()[:90] + " / " + b.stdout.strip()[:90])
    yield c
    for name, kw, pat in (("Y2", {"dry": "2"}, r"DRY must be 1 or unset"), ("Y3", {"last_end": None}, r"E193_LAST_END_EPOCH must be")):
        c = Case(box, name, "A", maxs=30, **kw).run()
        out = rd(os.path.join(c.state, "session.stdout"))
        ok(name + " refused", c.rc == 2 and re.search(pat, out) and not os.path.exists(c.sd), f"exit {c.rc}: {out.strip()[:100]}")
        yield c
    h3t.join()
    c = h3
    SKIP = c.skipped
    c.common(3, gate="the smoke gate failed")
    ok("H3 ten minutes", re.search(r"stop: card not free for 10 minutes \(pass 0 block [A-Z]\): lock:etsoc-shire0.lock otheruser 4244",
                                   c.stop_of("smoke")) and rd(c.f("smoke/run.log")).count("; waiting") >= 19,
       f"{c.stop_of('smoke')[:120]} (polled every 30 s: {rd(c.f('smoke/run.log')).count('; waiting')} waits)")
    yield c
    # ---- PB: sitting B whole (its run began in a thread before PA; its assertions here)
    pbt.join()
    c = pb
    SKIP = c.skipped
    c.common(0)
    first = int(rd(c.f("first-card-command.txt")) or 0)
    dl = re.search(r"\(epoch (\d+): the first card command \+ 3000 s - 120 s", c.log)
    ok("PB deadline", dl and int(dl.group(1)) == first + 2880, f"deadline = first card command + 2,880 s")
    mn = c.runlog_calls("x04")
    per = [sum(1 for x in mn if x[0] == str(p)) for p in range(9)]
    ok("PB passes", per == [15] * 9 and "main run end: runner rc 0, every pass (no stop: done)" in c.log and
       rd(c.f("x04/run.log")).rstrip().endswith("done"), f"calls a pass {per}; 'main run end: runner rc 0, every pass'; the runner's 'done'")
    ok("PB pass gaps", rd(c.f("x04/run.log")).count("30 s with the lock released, nothing launched") == 8, "8 pass gaps of 30 s, lock released")
    yield c


def collect_and_reduce(box, c, sit):
    """The collection, the registered reducer and the kit's checker on a real-path session (desk work: no device)."""
    raw = os.path.join(box.S, "raw-" + c.name)
    shutil.copytree(c.sd, raw)
    data = os.path.join(box.S, "data-" + c.name)
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "collect_e193.py"), raw, data, "--box-home", box.home, "--sitting", sit, "--login",
                        "boxuser"], capture_output=True, text=True)
    ok(c.name + " collected", r.returncode == 0 and "COPY-BACK EXACT" in r.stdout and "COLLECTED" in r.stdout,
       r.stdout.strip().splitlines()[-1][:160] if r.stdout.strip() else r.stderr[-200:])
    red = os.path.join(box.S, "reduce-" + c.name, "x04")
    os.makedirs(red)
    shutil.copy2(os.path.join(data, "x04/runs.jsonl"), red)
    with gzip.open(os.path.join(data, "x04/telemetry.jsonl.gz"), "rb") as g, open(os.path.join(red, "telemetry.jsonl"), "wb") as f:
        f.write(g.read())
    man = rd(os.path.join(data, "session/MANIFEST.sha256"))
    same = all(re.search(r"^%s  x04/%s$" % (sha(os.path.join(red, p)), p), man, re.M) for p in ("runs.jsonl", "telemetry.jsonl"))
    ok(c.name + " box bytes", same, "the collected runs.jsonl and the unpacked telemetry equal the box's manifest")
    xj = os.path.join(box.S, "x04-" + c.name + ".json")
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "proposal/src/reduce_x04.py"), red, "--out", xj], capture_output=True, text=True)
    x = json.load(open(xj)) if r.returncode == 0 else {}
    want = {"A": (16, 6), "B": (14, 0)}[sit]          # arms with the anchor, and trains, of the sitting's blocks (arms.tsv)
    nwant = {"A": 1, "B": 8}[sit]                       # measured passes (pass 0 set aside): PA ran passes 0-1, PB 0-8
    nanc = {"A": 5, "B": 2}[sit] * nwant                # the anchor spin2 runs at each block's start and once more at a pass's end
    arms = x.get("arms", {})
    trains = x.get("trains", {})
    ns_ = {a["n"] for k, a in arms.items() if k != "spin2"} | {t["n"] for t in trains.values()}
    ok(c.name + " reduced", r.returncode == 0 and (len(arms), len(trains)) == want and ns_ == {nwant} and
       arms.get("spin2", {}).get("n") == nanc and
       sha(os.path.join(E, "proposal/src/reduce_x04.py")) == "98bbc174db714667748c8d27436c7205e7d52be9d83f2614b4346aafc9630511",
       f"the registered reducer (98bbc174...) rc {r.returncode}: {len(arms)} arms and {len(trains)} trains reduced (want {want[0]} and "
       f"{want[1]}), each with {sorted(ns_)} measured passes (want {nwant}), the anchor spin2 {arms.get('spin2', {}).get('n')} runs "
       f"(want {nanc})")
    r2 = subprocess.run([PY, "-I", "-B", os.path.join(E, "check_e193.py"), "checks", xj, red, "--out", os.path.join(box.S, "checks-" + c.name
                                                                                                                    + ".json")],
                        capture_output=True, text=True)
    ok(c.name + " checks", r2.returncode == 0 and "CHECKS READ" in r2.stdout and "8 dip rule: REPORTED" in r2.stdout.replace("check ", ""),
       r2.stdout.strip().splitlines()[-1][:180] if r2.stdout.strip() else r2.stderr[-200:])
    print("   reducer's table (stand-in watts, not a measurement):\n" + "\n".join("     | " + x for x in r.stdout.splitlines()[:40]), flush=True)


def audit(passed):
    """Every dry-flag branch of the session and the runner, read from the files' own lines, has a row in dry-branches-e193.tsv whose
    cases all passed."""
    rows = [x.split("\t") for x in rd(os.path.join(HERE, "dry-branches-e193.tsv")).splitlines() if x and not x.startswith("#")]
    table = {(r[0], r[1]): r for r in rows}
    found = []
    for rel, pat in (("session_e193.sh", r"DRYF"), ("proposal/src/run_x04.py", r"\ba\.dry\b")):
        for i, ln in enumerate(open(os.path.join(E, rel)), 1):
            if re.search(pat, ln) and not ln.lstrip().startswith("#"):
                found.append((rel, str(i), ln.strip()))
    bad = []
    for rel, i, text in found:
        r = table.get((rel, i))
        if not r:
            bad.append(f"{rel}:{i} has no row ({text[:60]})")
            continue
        if r[2] != text:
            bad.append(f"{rel}:{i}: the row's text differs from the file's")
        for k in [x.strip() for x in r[5].split(",") if x.strip()]:
            if k == "NOT-ON-PATH":
                continue
            if not passed.get(k):
                bad.append(f"{rel}:{i}: its case {k} did not pass")
    extra = [k for k in table if (k[0], k[1]) not in {(a, b) for a, b, _ in found}]
    if extra:
        bad.append("rows for no dry branch: " + ", ".join(":".join(k) for k in extra))
    ok("AUDIT", not bad, f"{len(found)} dry-flag branches in the session and the runner, each with a row whose cases passed" if not bad
       else "; ".join(bad[:6]))


def main(argv):
    if argv[:1] == ["--inner"]:
        return inner(argv[1:])
    only = set(argv[2].split(",")) if len(argv) == 3 and argv[1] == "--only" else None    # a development run of some cases (never logged)
    if len(argv) != 1 and only is None:
        print(__doc__)
        return 2
    for p in glob.glob("/dev/et*"):
        if stat.S_ISCHR(os.stat(p).st_mode):
            print(f"REFUSED: {p} is a character device here: run this test inside the no-device sandbox (nodev.sh)")
            return 2
    S = os.path.abspath(argv[0])
    if os.path.exists(S) and os.listdir(S):
        print("REFUSED: give an empty scratch directory")
        return 2
    if S.startswith(SRC + os.sep):
        print("REFUSED: the scratch directory must be outside the repository")
        return 2
    os.makedirs(S, exist_ok=True)
    print(f"E193 real-path desk test, {time.strftime('%F %T %Z')}, {sys.executable} {sys.version.split()[0]}; the stand-in box's root holds "
          f"the harness's files copied from the clone; the session, the runner, E128's guard, the checker and the collector are the "
          f"kit's own files at their sha256", flush=True)
    box = Box(S)
    print(f"   {box.nsync} synced files; harness-e193.json {box.hsha[:16]}...; session_e193.sh {sha(os.path.join(box.kit, 'session_e193.sh'))[:16]}...; "
          f"run_x04.py {sha(os.path.join(box.kit, 'proposal/src/run_x04.py'))[:16]}...", flush=True)
    done = {}
    Case.only = only
    for c in cases(box):
        done[c.name] = c
        if c.name in ("PA", "PB") and not c.skipped:
            collect_and_reduce(box, c, c.sit)
    if only is not None:
        print("(a development run of some cases, " + ",".join(sorted(only)) + ": never a logged result)")
    passed = {}
    for name, good in RES:
        k = name.split()[0]
        passed[k] = passed.get(k, True) and good
    audit(passed)
    n = sum(1 for _, g in RES if g)
    print(f"\nDESKTEST-REALPATH-E193 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
