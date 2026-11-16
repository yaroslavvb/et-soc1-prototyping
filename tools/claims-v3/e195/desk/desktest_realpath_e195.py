#!/usr/bin/env python3
"""E195's REAL-PATH DESK TEST (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum; Q191, lane fix-e195, the same day: H2-H4
assert that no closing config read is sent while another user holds the card, verify-e195's finding 1).

    bash slot.sh bash nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e195/desk/desktest_realpath_e195.py <empty scratch dir> > log

THE LESSONS (CONTEXT sections 104, 109 and 116): a check that runs only on the REAL path is never exercised by a dry pass, and a host's
stdout on a real box can carry runtime lines inside the host's own output. This test runs SESSION_E195.SH'S REAL PATH, DRY UNSET,
exactly as step 9 launches it (E195_T0, X9_LATEST_START, X9_DEADLINE, E195_HARNESS_SHA256), and through it the kit's blocks
(block_e195.sh with the registered lib_x09.sh and lib.sh, lib_e195.sh) and runner (runitems_e195.py), the registered watcher
(watch_x09.py) and smoke gate (smoke_gate_x09.py), E128's guard (unchanged), against stand-ins for every device tool (fake_card_e195.py:
the sampler build/ettelem/ettelem and its config, the heater and anchor build/sparsity/host/sparsity_host, the host x09mem_host printing
X09MEM lines with the real host's keys, et-who and the holder helper behind sudo) and loggers in front of the system's timeout and
flock. Each case runs in its OWN SANDBOX inside the no-device one (bubblewrap: a private /dev holding only plain scratch files at
/dev/et<n>_ops, a private /run/lock holding the case's own card lock file, a private PID namespace, the host name aifoundry3), and the
test refuses to start if a character device /dev/et* is visible. Fast timing (launches of 0.05 s, heater bursts of 0.2 s) in every case
but P, which runs the hosts' and the heater's real timing (0.4 s launches for 4 s, 2 s heater bursts) so that the registered reducer
can read its passes.

Cases (each asserts its exit, its gate line or none, the session's own lines, the stand-ins' call log, the manifest, nothing left):
  Y1   the dry path (--dry): exit 0, the -dry directory, every log line "DRY ", E195-DRY OK (288 calls), no stand-in device call;
  P    THE REAL PATH, real timing: the first card command (stamped), the one ops node, the start config read under the card lock, the
       watcher, the smoke (8 device calls) and both smoke gates, passes 910 and 911 whole (35 device calls each, in the registered order
       for aifoundry3, every host call with --no-ms and the card lock held), the operator's stop file in the gap: "stopping before
       p912", exit 1; every sampler stopped by SIGTERM only; the closing config read after its own et-who --check read the card free; the
       manifest; then THE REGISTERED REDUCER on the
       real path's two passes (--warmup 910) and the kit's leftover checker;
  F    the whole session (fast): the smoke and all 8 passes, "every pass", exit 0, each pass 35 calls in the registered order;
  SP, S2, SL  THE RUNTIME LINE (aifoundry1's, from the committed 1a4bc1e3 smoke stdout) INSIDE every X09MEM line (SP), two of them
       (S2), on its own line (SL): every record read whole (10 launches a run), run.log names the dropped lines, the smoke gates pass;
  X1   an unknown text inside a record during pass 910 (a garbled line): the runner fails the parse (a traceback, never a wrong datum),
       the block ends "runitems exit 1", the session writes "ended without a registered stop" and exits 4;
  G2   the same garble from the start: the smoke block fails, GATE-STOP, no pass;
  B1   the board at 75 W on the live telemetry during pass 910: the watcher (watch_x09.py, on the live .raw) writes the pass's STOP and
       build/x09-STOP, the runner ends the pass at its next item (exit 8), the session stops, exit 1;
  D1   the die at 71 C during pass 910: the runner's die stop (exit 6); T1 a stale sampler during pass 910: exit 7 after 20 s;
  K1   A SAMPLER THAT IGNORES SIGTERM at pass 910's end: lib_e195.sh waits 30 s, never kills it, writes SAMPLER-STUCK and the stop files;
       the session stops after p910 and skips its closing config read; no second sampler; the stand-in received SIGTERM, never SIGKILL;
  H1   another user's holder at the start: GATE-STOP (no device opened), no config read, no sampler, no host;
  H2   another user's holder appearing during pass 910: the runner's own holder check stops the pass (exit 3), the session stops, and
       its closing config read is NOT sent (et-who --check reads the card held: the registered cfg()'s rule; verify-e195's finding 1);
  H3   another user's holder on the management node appearing between passes: lib_x09.sh's other-user test refuses p911 before its
       block begins (exit 3), the session stops; no closing config read (as H2);
  H4   another user's holder appearing during the smoke: the runner's holder check stops it (exit 3), GATE-STOP, no pass; no closing
       config read (as H2; verify-e195's case VH0);
  L1   the card lock held at the start by a process the case's et-who cannot see: no start config read: GATE-STOP;
  N2, N0  two ops nodes, and none: GATE-STOP (no device opened) after the holder check, before any card read;
  C1   the start config at TDP 5 W: GATE-STOP before the watcher and the smoke;
  G65  the heater's bursts at 66 W in the smoke: THE KIT'S 65 W GATE stops (the registered gate alone passes): GATE-STOP;
  GP   a launch with 1,023 participants in the smoke: the registered smoke gate stops: GATE-STOP;
  SG   SIGTERM to the session during pass 910: the stop files written, the pass ends at its next item, the close, exit 1;
  BS   SIGTERM to the block while a host launches (the host at real timing): the block's signal path writes the pass's STOP and the
       session's stop file, the host stops after its launch in flight and ends by itself with the card lock still held (its own end
       reads it), runitems ends by itself (no SIGTERM to it: the registered one would end a running host at its next write by SIGPIPE),
       the block ends "signal"; the session stops, exit 1;
  DW   the watcher killed during pass 910: the session stops before pass 911;
  DL   a deadline that holds the smoke and pass 910 only: "deadline: p911 would end after ...", exit 0;
  R1-R9  refusals before anything (exit 8, no device opened, no stand-in call): another host name; USER another login; no window;
       the last start passed; a deadline too near for the smoke; a stop file left from before; the harness's sha256 not the launch's;
       a synced file changed; the host not the one the build record names;
  PF   a kit file changed so that the device-command preflight reads NO-GO (its harness re-made to match): exit 3, no device opened;
  AUDIT every branch of session_e195.sh, block_e195.sh, lib_e195.sh and runitems_e195.py that a dry flag skips (desk/dry-branches-e195.tsv,
       read against the files' own lines) is run by a case above that passed, or named as unreachable at the desk with why.
EVERY WATT AND DEGREE HERE IS THE STAND-INS' ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT. Prints
DESKTEST-REALPATH-E195 <n> of <m> PASS (or FAIL). Exit 0 on PASS, 1 on FAIL, 2 on a usage or sandbox refusal.
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
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
SRC = os.path.normpath(os.path.join(E, "..", "..", ".."))
FAKE = os.path.join(E, "fake_card_e195.py")
PY = "/usr/bin/python3"
LOGIN = subprocess.run(["id", "-un"], capture_output=True, text=True).stdout.strip()
REALBYTES = os.path.join(SRC, "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random/stdout.txt")
RES = []
BOXES = None
LOCK = threading.Lock()
ONLY = [x for x in os.environ.get("E195_DESKTEST_ONLY", "").split(",") if x]   # a development run of some cases; the logged run has none
SCRUB = []


def scrub(s):
    for a, b in SCRUB:
        s = s.replace(a, b)
    return s


def out(s):
    with LOCK:
        print(scrub(s), flush=True)


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
    with LOCK:
        RES.append((name, bool(cond)))
    out(f"-> {'PASS' if cond else 'FAIL'} ({name}: {detail})")


def order_of(p):
    """The registered order for pass p on a host named aifoundry3 (desk/order-e195-aifoundry3.txt), anchors included."""
    txt = rd(os.path.join(E, "desk", "order-e195-aifoundry3.txt"))
    m = re.search(r"^pass %s .*\n((?:  .*\n)+)" % p, txt, re.M)
    if not m:
        return None
    line = m.group(1).splitlines()[0]
    return [x.split(":", 1)[1] for x in line.split()]


# ---------------------------------------------------------------------------------------------------------------- the box
class Box:
    def __init__(self, S, name="box"):
        self.S = os.path.join(S, name)
        self.home = os.path.join(self.S, "home")
        self.tree = os.path.join(self.home, "aifoundry")
        self.root = os.path.join(self.tree, "build/claims-v3/aifoundry3/e195")
        self.bin = os.path.join(self.S, "bin")
        self.kit = os.path.join(self.root, "tools/claims-v3/e195")
        lst = subprocess.run([PY, "-I", "-B", os.path.join(E, "harness_e195.py"), "--list"], capture_output=True, text=True,
                             check=True).stdout.split()
        for p in lst:
            dst = os.path.join(self.root, p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(SRC, p), dst)
        shutil.copy2(FAKE, os.path.join(self.kit, "fake_card_e195.py"))   # the stand-ins read desk/arm-table-e195.* beside them
        self.fake = os.path.join(self.kit, "fake_card_e195.py")
        self.nsync = len(lst)
        wrap = '#!/bin/bash\n%sexec %s -I -B %s %s "$@"\n'
        self.kernel = os.path.join(self.root, "build/x09mem/kernel/x09mem.elf")
        put(os.path.join(self.tree, "build/ettelem/ettelem"), wrap % ("", PY, self.fake, "ettelem"), 0o755)
        put(os.path.join(self.tree, "build/sparsity/host/sparsity_host"), wrap % ("# stand-in of the heater and anchor; it takes --stop-file\n",
                                                                                 PY, self.fake, "sparsity"), 0o755)
        for t in ("ettelem/ettelem", "sparsity/host/sparsity_host"):
            os.makedirs(os.path.dirname(os.path.join(self.root, "build", t)), exist_ok=True)
            os.symlink(os.path.join(self.tree, "build", t), os.path.join(self.root, "build", t))
        self.host = os.path.join(self.root, "build/x09mem/host/x09mem_host")
        put(self.host, wrap % ("# stand-in host: it prints X09MEM {json} lines; it launches %s\n" % self.kernel, PY, self.fake, "host"), 0o755)
        put(self.kernel, "stand-in kernel ELF for E195's real-path desk test (never loaded)\n")
        put(os.path.join(self.bin, "et-who"), wrap % ("", PY, self.fake, "etwho"), 0o755)
        put(os.path.join(self.bin, "sudo"), '#!/bin/bash\nif [ "$1" = -n ] && [ "$2" = /usr/local/sbin/et-holders ] && [ $# -eq 2 ]; then exec %s -I -B %s holders; fi\n'
            'echo "STAND-IN sudo: refused ($*)" >&2\nexit 97\n' % (PY, self.fake), 0o755)
        put(os.path.join(self.bin, "et-lab-manifest"), '#!/bin/sh\necho "host stand-in (E195 real-path desk test)"\n', 0o755)
        for c, real in (("timeout", "/usr/bin/timeout"), ("flock", "/usr/bin/flock")):
            put(os.path.join(self.bin, c), '#!/bin/bash\necho "$(date +%%s.%%N) %s $*" >> "$E195_FAKE_STATE/calls.log"\nexec %s "$@"\n'
                % (c, real), 0o755)
        for c in ("ssh", "scp", "rsync"):
            put(os.path.join(self.bin, c), '#!/bin/sh\necho "STAND-IN %s: refused (no network at the desk)" >&2\nexit 97\n' % c, 0o755)
        self.write_built()
        # the sandbox's first process: the session, then a bounded wait (90 s) for the case's stand-ins to end by themselves, so the PID
        # namespace's teardown (which would SIGKILL whatever is left) never ends one: a stuck stand-in sampler ends 40 s after the SIGTERM
        # it ignored, as the real one would end at its own --seconds bound
        self.inner = os.path.join(self.S, "inner.sh")
        put(self.inner, '#!/bin/bash\nbash "$@"\nrc=$?\nfor i in $(seq 1 180); do\n  pgrep -f "fake_card_e195.py (ettelem|host|sparsity)" > /dev/null || break\n'
            '  sleep 0.5\ndone\nexit $rc\n', 0o755)
        self.hsha = sha(os.path.join(self.kit, "harness-e195.json"))
        for n in (0, 1):
            put(os.path.join(self.S, f"node{n}"), "")

    def write_built(self, host_sha=None):
        et = os.path.join(self.tree, "build/ettelem/ettelem")
        sp = os.path.join(self.tree, "build/sparsity/host/sparsity_host")
        put(os.path.join(self.root, "build/x09mem-built.txt"),
            "X09MEM-BUILT %s on aifoundry3 (stand-in record of the desk test)\nhost %s\nkernel %s\nettelem %s %s\nsparsity_host %s %s\n" % (
                time.strftime("%F %T %Z"), host_sha or sha(self.host), sha(self.kernel), sha(et), et, sha(sp), sp))


def procs_with(state):
    outp = []
    key = ("E195_FAKE_STATE=" + state).encode()
    for p in glob.glob("/proc/[0-9]*"):
        try:
            if key in open(p + "/environ", "rb").read().split(b"\0"):
                outp.append(int(p.split("/")[2]))
        except OSError:
            continue
    return [p for p in outp if p != os.getpid()]


def pid_of(state, pat):
    for p in procs_with(state):
        try:
            cmd = open(f"/proc/{p}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if re.search(pat, cmd):
            return p
    return None


class Case:
    def __init__(self, box, name, nodes=(0,), host="aifoundry3", fast=True, latest=3600, deadline=3 * 3600, dry=False, env=None,
                 hsha=None, maxs=900, knobs=None, user=None):
        if box is None or box == "own":   # each case in its own stand-in box: build/x09-STOP is per E195 root
            box = Box(BOXES, "box-" + name)
        self.b, self.name = box, name
        self.state = os.path.join(box.S, "state-" + name)
        self.runlock = os.path.join(box.S, "runlock-" + name)
        os.makedirs(self.state)
        os.makedirs(self.runlock)
        put(os.path.join(self.runlock, "etsoc-shire0.lock"), "")
        with LOCK:
            t = int(time.time())
            while int(time.time()) == t:
                time.sleep(0.05)
            self.T0 = int(time.time())
            time.sleep(1.05)
        self.sd = os.path.join(box.tree, "build/e195", "T%d%s" % (self.T0, "-dry" if dry else ""))
        self.data = os.path.join(box.root, "build/claims-v3-dry/aifoundry3" if dry else "build/claims-v3/aifoundry3", "x09-T%d" % self.T0)
        self.nodes, self.hostname, self.dry, self.maxs = nodes, host, dry, maxs
        self.env = {"PATH": box.bin + ":/usr/bin:/bin", "HOME": box.home, "USER": user or LOGIN, "LOGNAME": LOGIN, "LC_ALL": "C",
                    "E195_FAKE_STATE": self.state, "E195_FAKE_LOGIN": LOGIN, "E195_T0": str(self.T0),
                    "E195_HARNESS_SHA256": hsha or box.hsha}
        if latest is not None:
            self.env["X9_LATEST_START"] = "@%d" % (self.T0 + latest)
        if deadline is not None:
            self.env["X9_DEADLINE"] = "@%d" % (self.T0 + deadline)
        self.env.update(env or {})
        if fast:
            self.knob("fast")
        self.knob("realbytes", REALBYTES)
        for k, v in (knobs or {}).items():
            self.knob(k, v)
        self.done = set()

    def f(self, *p):
        return os.path.join(self.sd, *p)

    def knob(self, name, text=""):
        put(os.path.join(self.state, name), text)

    def once(self, key, cond, act):
        if key not in self.done and cond():
            self.done.add(key)
            act()

    def items_done(self, p):
        return len(re.findall(r"^\S+ \[aifoundry3\] block %s #\d+ " % p, rd(os.path.join(self.data, "p%s" % p, "run.log")), re.M))

    def run(self, watch=None, holdlock=False):
        cmd = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev"]
        for n in self.nodes:
            cmd += ["--bind", os.path.join(self.b.S, f"node{n}"), f"/dev/et{n}_ops"]
        cmd += ["--bind", self.runlock, "/run/lock", "--proc", "/proc", "--unshare-pid", "--unshare-uts", "--hostname", self.hostname,
                "--die-with-parent", "--chdir", self.b.tree, "--", "bash", self.b.inner, os.path.join(self.b.kit, "session_e195.sh")]
        if self.dry:
            cmd.append("--dry")
        lk = None
        if holdlock:   # the card lock held by a process outside the case's PID namespace: its et-who cannot see it
            import fcntl
            lk = open(os.path.join(self.runlock, "etsoc-shire0.lock"), "r+")
            fcntl.flock(lk, fcntl.LOCK_EX)
        t0 = time.time()
        p = subprocess.Popen(cmd, env=self.env, stdout=open(os.path.join(self.state, "session.stdout"), "w"), stderr=subprocess.STDOUT,
                             start_new_session=True)
        killed = False
        while p.poll() is None:
            if watch:
                try:
                    watch(self)
                except Exception as e:   # a watch error is the test's, reported and the case goes on
                    out(f"   [{self.name}] watch error: {e}")
            if time.time() - t0 > self.maxs:
                os.killpg(p.pid, signal.SIGKILL)   # the test's own bound on a stand-in sandbox (no real device anywhere)
                killed = True
            time.sleep(0.2)
        if lk:
            lk.close()
        self.rc = p.returncode
        self.secs = time.time() - t0
        for _ in range(60):   # a stuck stand-in sampler ends by itself; wait for every process of the case
            if not procs_with(self.state):
                break
            time.sleep(1)
        self.left = procs_with(self.state)
        self.log = rd(self.f("session.log"))
        self.calls = rd(os.path.join(self.state, "calls.log"))
        self.signals = rd(os.path.join(self.state, "signals.log"))
        out(f"   [{self.name}] exit {self.rc} after {self.secs:.0f} s{' (KILLED at its bound)' if killed else ''}; {os.path.basename(self.sd)}")
        for ln in self.log.splitlines():
            if re.search(r"GATE-STOP|refused|smoke|first card|config read|deadline|queue end|signal|session (start|end)|p9\d\d rc=", ln):
                out("     | " + ln[24:244])
        return self

    def manifest_ok(self):
        m = self.f("MANIFEST.sha256")
        if not os.path.exists(m):
            return False
        r = subprocess.run(["sha256sum", "-c", "--quiet", m], cwd=self.b.tree, capture_output=True, text=True)
        return r.returncode == 0

    def n(self, pat):
        return len(re.findall(pat, self.calls, re.M))

    def common(self, want_rc, gate=None):
        ok(self.name + " exit", self.rc == want_rc, f"session exit {self.rc}, want {want_rc}")
        g = re.findall(r"GATE-STOP: (.*)", self.log)
        if gate is None:
            ok(self.name + " no gate", not g, f"no GATE-STOP line ({len(g)})")
        else:
            ok(self.name + " gate", g and re.search(gate, g[0]), f"GATE-STOP: {g[0][:160] if g else '(none)'}")
        nm = sum(1 for _ in open(self.f("MANIFEST.sha256"))) if os.path.exists(self.f("MANIFEST.sha256")) else 0
        ok(self.name + " end", "session end (T0 %d)" % self.T0 in self.log and self.manifest_ok() and rd(self.f("session.rc")).strip() == str(want_rc),
           f"'session end', MANIFEST.sha256 verifying ({nm} files) and session.rc {rd(self.f('session.rc')).strip()}")
        ok(self.name + " nothing left", not self.left, f"processes of the case left: {self.left}")
        hs, he = self.n(r"^\S+ x09mem_host --item"), self.n(r"^\S+ x09mem_host-end ")
        ss, se = self.n(r"^\S+ ettelem sample"), self.n(r"^\S+ ettelem-end ")
        ps, pe = self.n(r"^\S+ sparsity_host --"), self.n(r"^\S+ sparsity_host-end ")
        ok(self.name + " nothing killed", (hs, ss, ps) == (he, se, pe),
           f"every device stand-in that started ended by itself (a killed one logs no end): host {hs}/{he}, sampler {ss}/{se}, heater and anchor {ps}/{pe}")

    def held_close(self):
        """verify-e195's finding 1: no closing config read while another user holds the card (the registered cfg()'s rule)."""
        cfgs = self.n(r"^\S+ flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config")
        chk = self.n(r"^\S+ et-who --check")
        ok(self.name + " no closing read while held", cfgs == 1 and chk == 2 and
           "closing config read: not read (et-who --check does not read the card free: exit 1" in self.log and
           not os.path.exists(self.f("config-session-end.json")) and os.path.exists(self.f("etwho-check-end.txt")),
           f"config reads {cfgs} (the start's only); et-who --check calls {chk} (the start's and the closing's); the closing line "
           f"'not read'; no config-session-end.json; etwho-check-end.txt kept")

    def nodev(self):
        dev = self.n(r"^\S+ (ettelem|x09mem_host|sparsity_host) ")
        ok(self.name + " no device", dev == 0 and "no device opened" in self.log, f"stand-in device calls {dev}; 'no device opened' in the log")

    def passes(self):
        return [p for p in range(910, 918) if os.path.exists(os.path.join(self.data, f"p{p}", "block.json"))]

    def pass_ok(self, p):
        b = rd(os.path.join(self.data, f"p{p}", "block.json"))
        runs = [json.loads(x) for x in rd(os.path.join(self.data, f"p{p}", "runs.jsonl")).splitlines() if x.startswith("{")]
        seq = []
        for r in runs:
            if r.get("block") == p and (not seq or seq[-1][0] != r["pos"]):
                seq.append((r["pos"], r["item"]))
        want = order_of(p)
        return '"status":"ok"' in b, [i for _, i in seq] == want, len(runs)


# ---------------------------------------------------------------------------------------------------------------- the cases
def at_items(c, p, k, act, key="a"):
    c.once(key, lambda: c.items_done(p) >= k, act)


def case_list(box, S):
    T = []

    def th(fn):
        if ONLY and fn.__name__ not in ONLY:
            return
        t = threading.Thread(target=fn)
        t.start()
        T.append(t)

    # ---- P: the real path at real timing, two whole passes, then the operator's stop in the gap
    def P():
        c = Case(None, "P", fast=False, maxs=1800)
        c.run(lambda c: c.once("stop", lambda: "p911 rc=0" in rd(c.f("session.log")), lambda: put(os.path.join(c.b.root, "build/x09-STOP"), "the operator, in the gap\n")))
        os.rename(os.path.join(c.b.root, "build/x09-STOP"), os.path.join(c.b.root, "build/x09-STOP.P")) if os.path.exists(os.path.join(c.b.root, "build/x09-STOP")) else None
        c.common(1)
        ok("P first card command", os.path.exists(c.f("first-card-command.txt")) and "the first card command (the holder check): free" in c.log,
           f"first-card-command.txt {rd(c.f('first-card-command.txt')).strip()}; the holder check line")
        ok("P config start", c.n(r"^\S+ flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config") == 2
           and "start config read: TDP 0 W, 65 C, minion 600 MHz as found" in c.log and "closing config read: TDP 0 W" in c.log
           and c.n(r"^\S+ et-who --check") == 2 and os.path.exists(c.f("etwho-check-end.txt")),
           "both config reads through the guard under the card lock (flock -n ... timeout 10), each after an et-who --check that read the card free (2 calls)")
        ok("P watcher", "the board-power watcher runs" in c.log and "watch: board stop 70.0 W on 3 samples" in rd(c.f("watch.log")), "watch_x09.py started on the data folder")
        smoke_calls = len([1 for x in rd(os.path.join(c.data, "p901", "marks.jsonl")).splitlines() if '"kind": "run"' in x or '"kind": "burnin"' in x])
        ok("P smoke", smoke_calls == 8 and "smoke gate PASS" in c.log and "SMOKE-PEAK PASS" in c.log and "smoke gate passed" in c.log,
           f"smoke device calls {smoke_calls} (2 burn-ins, the anchor, 4 arms, the anchor: 8), the registered gate PASS, the kit's 65 W / 65 C gate PASS")
        for p in (910, 911):
            st, order, nr = c.pass_ok(p)
            ok(f"P p{p}", st and order, f"block.json ok {st}; the 33 runs in the registered order for aifoundry3 {order}; {nr} records")
        hosts = re.findall(r"^\S+ x09mem_host (.*) \| lock=(\S+)$", c.calls, re.M)
        ok("P host calls", len(hosts) == 4 + 31 * 2 and all(a.endswith("--no-ms") for a, _ in hosts) and all(l == "held" for _, l in hosts),
           f"{len(hosts)} host calls (4 in the smoke, 31 a pass), every one --no-ms and under the block's card lock")
        ok("P stop", "queue end: " in c.log and re.search(r"build/x09-STOP exists: stopping before p912", c.log) and re.search(r"passes complete: 2 of 8", c.log),
           "the operator's stop before p912; passes complete 2 of 8")
        sig = re.findall(r"ettelem got signal (\d+)", c.signals)
        ok("P samplers by SIGTERM", sig and set(sig) == {"15"} and len(sig) == 3, f"signals the samplers received: {sig} (one SIGTERM for each of the 3 blocks)")
        # the registered reducer on the real path's files, then the kit's leftover checker
        red = os.path.join(E, "proposal", "src", "reduce_x09.py")
        r = subprocess.run([PY, "-I", "-B", red, os.path.join(c.data, "p910"), os.path.join(c.data, "p911"), "--gen", os.path.join(E, "gen-e195-noms"),
                            "--out", os.path.join(S, "P-x09.json"), "--warmup", "910"], capture_output=True, text=True)
        xj = json.load(open(os.path.join(S, "P-x09.json"))) if os.path.exists(os.path.join(S, "P-x09.json")) else {}
        ok("P reducer", r.returncode == 0 and xj.get("headline") == [911] and xj.get("warmup") == 910,
           f"the registered reducer rc {r.returncode}; headline {xj.get('headline')}, warm-up {xj.get('warmup')}; {r.stdout.splitlines()[0][:150] if r.stdout else r.stderr[-150:]}")
        lo = subprocess.run([PY, "-I", "-B", os.path.join(E, "check_e195.py"), "leftover", red, os.path.join(E, "gen-e195-noms"),
                             os.path.join(c.data, "p910"), os.path.join(c.data, "p911"), "--warmup", "910"], capture_output=True, text=True)
        ok("P leftover", lo.returncode == 0 and "LEFTOVER-E195: headline passes [911]" in lo.stdout and "rail minion: measured 0.5230 V" in lo.stdout,
           " / ".join(x[14:120] for x in lo.stdout.splitlines()[-3:]))
    th(P)

    # ---- F: the whole session, fast
    def F():
        c = Case(None, "F", maxs=1800)
        c.run()
        c.common(0)
        good = [p for p in range(910, 918) if all(c.pass_ok(p)[:2])]
        ok("F passes", good == list(range(910, 918)) and "queue end: every pass; passes complete: 8 of 8" in c.log,
           f"passes ok and in the registered order: {good}")
    th(F)

    # ---- the runtime line inside the host's output (aifoundry1's form, from the committed bytes)
    def runtime_case(name, mode):
        def fn():
            c = Case(None, name, knobs={"runtime": mode})
            c.run(lambda c: c.once("st2", lambda: "p910 rc=0" in rd(c.f("session.log")), lambda: put(os.path.join(c.b.root, "build/x09-STOP"), name + "\n")))
            stopf = os.path.join(c.b.root, "build/x09-STOP")
            if os.path.exists(stopf):
                os.rename(stopf, stopf + "." + name)
            c.common(1)
            runs = [json.loads(x) for x in rd(os.path.join(c.data, "p910", "runs.jsonl")).splitlines() if x.startswith("{")]
            x9 = [r for r in runs if r["item"].startswith("x9_")]
            dropped = len(re.findall(r"runtime line\(s\) dropped from the host's stdout: Opening device", rd(os.path.join(c.data, "p910", "run.log"))))
            ok(name + " records whole", len(x9) == 31 * 10 and all(r.get("participants") == 1024 and r.get("ok") for r in x9) and
               "smoke gate passed" in c.log and dropped == (31 if mode != "line" else 31),
               f"p910: {len(x9)} X09MEM records (31 runs x 10 launches), every one ok with 1,024 participants; run.log names the dropped runtime line in {dropped} runs")
        fn.__name__ = name
        return fn
    for nm, md in (("SP", "split"), ("S2", "twice"), ("SL", "line")):
        th(runtime_case(nm, md))

    # ---- the stop lines and gates, a few at a time
    def B1():
        c = Case(None, "B1")
        c.run(lambda c: at_items(c, 910, 3, lambda: c.knob("board_hot", "75@%d" % time.time())))
        stopf = os.path.join(c.b.root, "build/x09-STOP")
        moved = os.path.exists(stopf)
        if moved:
            os.rename(stopf, stopf + ".B1")
        c.common(1)
        ok("B1 board stop", re.search(r"STOP: p910 board 75\.00 W >= 70\.0 W on 3 samples in a row", rd(c.f("watch.log"))) and moved and
           os.path.exists(os.path.join(c.data, "p910", "STOP")) and re.search(r"stopping after p910 \(block rc 1, runitems exit 8\)", c.log),
           "the watcher on the live telemetry wrote p910/STOP and build/x09-STOP; the runner ended the pass (exit 8); the session stopped")

    def D1():
        c = Case(None, "D1")
        c.run(lambda c: at_items(c, 910, 3, lambda: c.knob("die_hot", "71@%d" % time.time())))
        c.common(1)
        ok("D1 die stop", re.search(r"STOP \(6\): die reading 71\.0 C", rd(os.path.join(c.data, "p910", "run.log"))) and
           re.search(r"stopping after p910 \(block rc 1, runitems exit 6\)", c.log), "the runner's 70 C stop (exit 6); the session stopped")

    def T1():
        c = Case(None, "T1")
        c.run(lambda c: at_items(c, 910, 3, lambda: c.knob("stale", "%d" % time.time())))
        c.common(1)
        ok("T1 stale", re.search(r"STOP \(7\): the newest telemetry line is", rd(os.path.join(c.data, "p910", "run.log"))) and
           re.search(r"runitems exit 7", c.log), "the runner's stale-sampler stop (exit 7); the session stopped")

    def K1():
        c = Case(None, "K1", maxs=1200)
        c.run(lambda c: at_items(c, 910, 30, lambda: c.knob("stuck", "")))
        c.common(1)
        sig = re.findall(r"ettelem got signal (\d+)", c.signals)
        late = [ln for ln in c.calls.splitlines() if " ettelem sample" in ln and float(ln.split()[0]) > (os.path.getmtime(os.path.join(c.data, "p910", "SAMPLER-STUCK")) if os.path.exists(os.path.join(c.data, "p910", "SAMPLER-STUCK")) else 9e12)]
        ok("K1 stuck sampler", os.path.exists(os.path.join(c.data, "p910", "SAMPLER-STUCK")) and "9" not in sig and "15" in sig and
           re.search(r"a sampler of p910 ignored SIGTERM", c.log) and "closing config read: SKIPPED" in c.log and not late and
           "NOT killed" in rd(c.f("passes.log")),
           f"SAMPLER-STUCK written; the sampler's signals {sig} (never 9); the session stopped after p910; the closing config read skipped; no sampler started after it ({len(late)})")
        os.path.exists(os.path.join(c.b.root, "build/x09-STOP")) and os.rename(os.path.join(c.b.root, "build/x09-STOP"), os.path.join(c.b.root, "build/x09-STOP.K1"))

    def H1():
        c = Case(None, "H1", knobs={"foreign": "lock:etsoc-shire0.lock otheruser 4244 00:03 someone-elses-block.sh"})
        c.run()
        c.common(3, r"the card is held: et-who --check lists 1 holder line")
        c.nodev()

    def H2():
        c = Case(None, "H2")
        c.run(lambda c: at_items(c, 910, 3, lambda: c.knob("foreign", "/dev/et0_ops   otheruser 4244 00:03 other_host")))
        c.common(1)
        ok("H2 holder mid-pass", re.search(r"STOP \(3\): block 910 .*another user on this card: otheruser", rd(os.path.join(c.data, "p910", "run.log")))
           and re.search(r"stopping after p910 \(block rc 3", c.log), "the runner's holder check stopped the pass (exit 3); the session stopped")
        c.held_close()

    def H3():
        c = Case(None, "H3")
        c.run(lambda c: c.once("h", lambda: "p910 rc=0" in rd(c.f("session.log")), lambda: c.knob("foreign", "/dev/et0_mgmt  otheruser 4244 00:03 other_tool")))
        c.common(1)
        ok("H3 holder at a block's start", re.search(r"others present: procs=\[\] holders=\[otheruser:4244", rd(c.f("passes.log"))) and
           re.search(r"stopping after p911 \(block rc 3\)", c.log) and not os.path.exists(os.path.join(c.data, "p911", "block.json")),
           "lib_x09.sh's other-user test refused p911 before its block began (exit 3); the session stopped")
        c.held_close()

    def H4():
        c = Case(None, "H4")
        c.run(lambda c: at_items(c, 901, 2, lambda: c.knob("foreign", "/dev/et0_ops   otheruser 4244 00:03 other_host")))
        c.common(3, r"the smoke gate failed or a stop is set")
        ok("H4 holder in the smoke", re.search(r"STOP \(3\): block 901 .*another user on this card: otheruser", rd(os.path.join(c.data, "p901", "run.log")))
           and not c.passes(), "the runner's holder check stopped the smoke (exit 3); GATE-STOP; no pass")
        c.held_close()

    def L2():
        c = Case(None, "L2")
        state = {}
        def w(c):
            if "lk" not in state and "smoke gate passed" in rd(c.f("session.log")):
                import fcntl
                state["lk"] = open(os.path.join(c.runlock, "etsoc-shire0.lock"), "r+")
                fcntl.flock(state["lk"], fcntl.LOCK_EX)
        c.run(w)
        if "lk" in state:
            state["lk"].close()
        c.common(1)
        ok("L2 lock at a block's start", re.search(r"card lock /run/lock/etsoc-shire0\.lock is held by another process: not starting", rd(c.f("passes.log"))) and
           re.search(r"stopping after p910 \(block rc 3", c.log) and "closing config read: none came back" in c.log,
           "lib.sh's block_begin found the card lock held (exit 3); the session stopped; the closing read found the lock held")

    def NR():
        c = Case(None, "NR")
        c.run(lambda c: at_items(c, 910, 3, lambda: put(os.path.join(c.b.root, "build/x09-STOP"), "by hand, the session's stop file alone\n")))
        stopf = os.path.join(c.b.root, "build/x09-STOP")
        had = os.path.exists(stopf)
        if had:
            os.rename(stopf, stopf + ".NR")
        c.common(1)
        rl = rd(os.path.join(c.data, "p910", "run.log"))
        ok("NR session stop file", had and len(re.findall(r"no launch record \(rc 0\): one retry", rl)) >= 20 and '"status":"ok"' in rd(os.path.join(c.data, "p910", "block.json"))
           and "build/x09-STOP exists: stopping before p911" in c.log,
           f"after build/x09-STOP every host launched nothing ({len(re.findall(r'no launch record', rl))} 'no launch record' lines, each item tried twice), p910 ended ok, the session stopped before p911")

    def L1():
        c = Case(None, "L1")
        c.run(holdlock=True)
        c.common(3, r"no start config read came back")
        ok("L1 no closing", "closing config read" not in c.log and c.n(r"^\S+ (x09mem_host|sparsity_host) ") == 0, "no closing read, no host, no heater")

    def N(name, nodes):
        def fn():
            c = Case(None, name, nodes=nodes)
            c.run()
            c.common(3, r"not exactly /dev/et0_ops")
            c.nodev()
        fn.__name__ = name
        return fn

    def C1():
        c = Case(None, "C1", knobs={"config": '{"tdp_w":5,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}'})
        c.run()
        c.common(3, r"the start config is not TDP 0 W / 65 C / 600 MHz")
        ok("C1 nothing after", c.n(r"^\S+ (x09mem_host|sparsity_host) ") == 0 and "watcher runs" not in c.log, "no watcher, no smoke")

    def G65():
        c = Case(None, "G65", knobs={"heater_w": "66"})
        c.run()
        c.common(3, r"the smoke gate failed .*the kit's 65 W / 65 C gate 1")
        ok("G65 gates", re.search(r"smoke gate PASS", c.log) and re.search(r"SMOKE-PEAK FAIL: highest board reading 66\.00 W", c.log)
           and "closing config read" in c.log and not c.passes(), "the registered gate PASS (it reads no peak); the kit's gate FAIL; no pass; the closing read")

    def GP():
        c = Case(None, "GP", knobs={"participants": "1023"})
        c.run()
        c.common(3, r"the smoke gate failed .*registered gate 1")
        ok("GP gate", re.search(r"smoke gate FAIL: .*a launch without 1,024 participants", c.log) and not c.passes(), "the registered gate FAIL; no pass")

    def G2():
        c = Case(None, "G2", knobs={"runtime": "garble"})
        c.run()
        c.common(3, r"the smoke gate failed .*block rc 1")
        ok("G2 no datum", re.search(r"JSONDecodeError|Traceback", rd(c.f("smoke.log"))) and not c.passes(), "the runner failed the parse in the smoke (a traceback): no pass")

    def X1():
        c = Case(None, "X1")
        c.run(lambda c: at_items(c, 910, 3, lambda: c.knob("runtime", "garble")))
        c.common(4)
        ok("X1 crash", re.search(r"p910 ended without a registered stop \(block rc 1, runitems exit 1", c.log) and
           re.search(r"JSONDecodeError", rd(c.f("passes.log"))), "a traceback in the runner (exit 1): 'ended without a registered stop', exit 4")

    def SG():
        c = Case(None, "SG")
        c.run(lambda c: at_items(c, 910, 3, lambda: os.kill(pid_of(c.state, r"^bash \S+session_e195\.sh"), signal.SIGTERM)))
        stopf = os.path.join(c.b.root, "build/x09-STOP")
        had = os.path.exists(stopf)
        if had:
            os.rename(stopf, stopf + ".SG")
        c.common(1)
        ok("SG signal", "signal: build/x09-STOP and the running pass's STOP written" in c.log and had and
           re.search(r"stopping after p910 \(block rc 1, runitems exit 8\)", c.log), "the stop files written; the pass ended at its next item; the close")

    def BS():
        c = Case(None, "BS", knobs={"slow_host": ""})
        def w(c):
            c.once("t", lambda: re.search(r"x09mem_host --item", rd(os.path.join(c.state, "calls.log"))) and c.items_done(910) >= 2 and
                   pid_of(c.state, r"x09mem_host") and pid_of(c.state, r"block_e195\.sh 910"),
                   lambda: (time.sleep(1.0), os.kill(pid_of(c.state, r"bash \S+block_e195\.sh 910"), signal.SIGTERM)))
        c.run(w)
        c.common(1)
        ends = re.findall(r"^\S+ x09mem_host-end (\S+) \| lock=(\S+)$", c.calls, re.M)
        last = ends[-1] if ends else None
        ok("BS lock kept", last and last[1] == "held" and "x09k: a signal to the block: this pass's STOP and the session's stop file written" in rd(c.f("passes.log"))
           and "SIGTERM to it" not in rd(c.f("passes.log")) and re.search(r"stopping after p910 \(block rc 1, signal\)", c.log),
           f"the stop files written first; the host in flight stopped after its launch and ended by itself with the card lock still held by the block ({last}); runitems ended by itself (no SIGTERM); the block ended 'signal'")
        stopf = os.path.join(c.b.root, "build/x09-STOP")
        os.path.exists(stopf) and os.rename(stopf, stopf + ".BS")

    def DW():
        c = Case(None, "DW")
        c.run(lambda c: at_items(c, 910, 3, lambda: os.kill(pid_of(c.state, r"watch_x09\.py"), signal.SIGTERM)))
        c.common(1)
        ok("DW watcher", "the board-power watcher is not running: stopping before p911" in c.log, "the session stopped before p911")

    def DL():
        c = Case(None, "DL", deadline=500)
        c.run()
        c.common(0)
        ok("DL deadline", re.search(r"deadline: p911 would end after", c.log) and c.passes() == [910], f"passes {c.passes()}; the deadline rule before p911")

    def Y1():
        c = Case(None, "Y1", dry=True)
        c.run()
        ok("Y1 exit", c.rc == 0, f"exit {c.rc}")
        lines = [ln for ln in c.log.splitlines() if ln.strip()]
        ok("Y1 dry", lines and all(ln[24:].startswith("DRY ") for ln in lines) and "E195-DRY OK: 288 device calls" in c.log and c.sd.endswith("-dry"),
           f"{len(lines)} lines, every one 'DRY '; {[x for x in lines if 'E195-DRY' in x][0][28:110] if any('E195-DRY' in x for x in lines) else 'no E195-DRY line'}")
        ok("Y1 no device", c.n(r"^\S+ (ettelem|x09mem_host|sparsity_host|et-who|flock|timeout) ") == 0, "no stand-in device tool, et-who, flock or timeout called")
        ok("Y1 end", c.manifest_ok() and rd(c.f("session.rc")).strip() == "0" and not c.left, "the -dry manifest and session.rc 0; nothing left")

    def refusal(name, why, **kw):
        def fn():
            setup = kw.pop("setup", None)
            bx = kw.pop("box", None)
            if setup:
                setup(bx)
            c = Case(bx, name, **kw)
            c.run()
            ok(name + " refused", c.rc == 8 and re.search("refused, no device opened: " + why, c.log), f"exit {c.rc}; {([x[24:180] for x in c.log.splitlines() if 'refused' in x] or ['no refusal line'])[0]}")
            ok(name + " nothing", c.n(r"^\S+ (ettelem|x09mem_host|sparsity_host|et-who|flock) ") == 0 and not c.left and "session end (T0" in c.log,
               "no stand-in device call, no et-who, no flock; session end; nothing left")
        fn.__name__ = name
        return fn

    def mkbox(nm, mutate):
        bx = Box(S, nm)
        mutate(bx)
        return bx

    batches = [
        [B1, D1, T1, K1],
        [H1, H2, H3, H4, L1, L2, N("N2", (0, 1)), N("N0", ()), C1],
        [G65, GP, G2, X1, SG],
        [BS, DW, DL, Y1, NR],
        [refusal("R1", "this is aifoundry2, not aifoundry3", host="aifoundry2"),
         refusal("R2", "USER is 'someone-else', not this login", user="someone-else"),
         refusal("R3", "X9_LATEST_START and X9_DEADLINE are required", latest=None),
         refusal("R4", "no session starts after", latest=-5),
         refusal("R5", r"the smoke \(150 s\) and the close would end after the deadline", deadline=100),
         refusal("R6", "build/claims-v3/aifoundry3/e195/build/x09-STOP exists", box=mkbox("box-r6", lambda b: put(os.path.join(b.root, "build/x09-STOP"), "left\n"))),
         refusal("R7", "harness-e195.json reads", hsha="0" * 64),
         refusal("R8", "the harness check failed: HARNESS FAIL: differs tools/claims-v3/e195/check_e195.py",
                 box=mkbox("box-r8", lambda b: open(os.path.join(b.kit, "check_e195.py"), "a").write("# one byte more\n"))),
         refusal("R9", "the host, the kernel, the sampler or the heater is not the one the build record names",
                 box=mkbox("box-r9", lambda b: b.write_built(host_sha="1" * 64)))],
    ]
    for b in batches:
        ts = [threading.Thread(target=fn) for fn in b if not ONLY or fn.__name__ in ONLY]
        for t in ts:
            t.start()
        for t in ts:
            t.join()

    # ---- PF: a kit file changed so the preflight reads NO-GO, its harness re-made to match (its own box)
    if ONLY and "PF" not in ONLY:
        for t in T:
            t.join()
        return
    pb = Box(S, "box-pf")
    with open(os.path.join(pb.kit, "check_e195.py"), "a") as f:
        f.write("# a statistics reset written into a scanned file, for the test only:\n# ettelem sample --seconds 1 --every-ms 100 --reset-ms 1000\n"
                "RESET = ['build/ettelem/ettelem', 'sample', '--reset-ms', '1000']\n")
    subprocess.run([PY, "-I", "-B", os.path.join(pb.kit, "harness_e195.py"), "--make"], capture_output=True, text=True, check=True)
    c = Case(pb, "PF", hsha=sha(os.path.join(pb.kit, "harness-e195.json")))
    c.run()
    ok("PF preflight", c.rc == 3 and re.search(r"device-command preflight rc=3: dmcmd_audit: NO-GO", c.log) and "no device opened" in c.log
       and c.n(r"^\S+ (ettelem|x09mem_host|sparsity_host|et-who|flock) ") == 0, f"exit {c.rc}; the preflight NO-GO; no device opened")
    for t in T:
        t.join()


def audit():
    """THE AUDIT: every line of the session's chain that reads a dry flag has a row naming the cases that ran its real branch."""
    rows = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(HERE, "dry-branches-e195.tsv")) if ln.strip() and not ln.startswith("#")]
    have = {(r[0], r[1]): r for r in rows}
    files = {"tools/claims-v3/e195/session_e195.sh": r"DRYF", "tools/claims-v3/e195/block_e195.sh": r"V3_DRY",
             "tools/claims-v3/e195/lib_e195.sh": r"V3_DRY", "tools/claims-v3/e195/runitems_e195.py": r"a\.dry|V3_DRY",
             "tools/claims-v3/lib.sh": r"V3_DRY", "tools/claims-v3/e195/proposal/src/lib_x09.sh": r"V3_DRY"}
    passed = {}
    for name, good in RES:
        k = name.split()[0]
        passed[k] = passed.get(k, True) and good
    bad = []
    n = 0
    for fn, pat in files.items():
        for i, ln in enumerate(open(os.path.join(SRC, fn)), 1):
            if re.search(pat, ln) and not ln.lstrip().startswith("#"):
                n += 1
                r = have.get((fn, str(i)))
                if not r:
                    bad.append(f"{fn}:{i} has no row")
                    continue
                if r[2].strip() != ln.strip()[:len(r[2].strip())]:
                    bad.append(f"{fn}:{i} the row's text differs")
                cs = [x for x in r[5].split(",") if x.strip()]
                if r[5].startswith("UNREACHABLE"):
                    continue
                for cname in cs:
                    if not passed.get(cname.strip()):
                        bad.append(f"{fn}:{i} case {cname} did not pass")
    ok("AUDIT dry branches", not bad, f"{n} lines that read a dry flag, each with a row whose cases passed" + (f"; {bad[:6]}" if bad else ""))


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if os.path.exists(S) and os.listdir(S):
        print(f"REFUSED: {S} is not empty")
        return 2
    os.makedirs(S, exist_ok=True)
    for p in glob.glob("/dev/et*"):
        if os.path.exists(p) and (os.stat(p).st_mode & 0o170000) == 0o020000:
            print(f"REFUSED: a character device {p} is visible: run inside nodev.sh")
            return 2
    hc = subprocess.run([PY, "-I", "-B", os.path.join(E, "harness_e195.py"), "--check"], capture_output=True, text=True)
    if hc.returncode != 0:
        print("REFUSED: the harness is not current: " + hc.stdout.strip())
        return 2
    SCRUB.extend([(S, "<scratch>"), (SRC, "<repo>"), (os.path.expanduser("~"), "<home>"), (LOGIN, "<login>")])
    out(f"E195 real-path desk test, {time.strftime('%F %T %Z')}; Python {sys.version.split()[0]} ({sys.executable}); bubblewrap "
        f"{subprocess.run(['/usr/bin/bwrap', '--version'], capture_output=True, text=True).stdout.strip()}; {hc.stdout.strip()}")
    global BOXES
    BOXES = S
    box = Box(S)
    out(f"stand-in boxes, one a case: {box.nsync} harness files synced into each E195 root; stand-ins for the sampler, heater/anchor, host, et-who, sudo et-holders")
    case_list(box, S)
    if not ONLY:
        audit()
    n = sum(1 for _, g in RES if g)
    out(f"DESKTEST-REALPATH-E195 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
