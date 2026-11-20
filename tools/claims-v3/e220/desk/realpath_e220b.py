#!/usr/bin/env python3
"""E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE REAL-PATH DESK TEST, E216's desk/realpath_e216.py (landed in
59f5288b; E209's form) for E220 arm B's schedule. The lesson
(round log sections 104, 109 and 116: E183's two lost days, E191's split JSON; E215's: through the smoke, the stop path and at least two points,
one of them a G point): a check that runs only on the REAL path is never exercised by a dry pass. This runs E220's session exactly as runbook
step 9 launches it - the box root's src/start_e220b.sh, then src/session_e220b.sh, then src/run_e220b.py (E208's runner src/run_mms.py UNCHANGED,
imported, with E220's lines and family G) on its REAL path (no --dry) - in a box root made by make_box_e220b.py sync, against stand-ins for
every device tool (desk/standin_e220b.py: the reader behind E208's guard, rgm136's host, RGM211'S HOST for family G, et-who; E208's own doubles
inside), the card's lock and the nodes. Standard library only.

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e220/desk/realpath_e220b.py <scratch> --elf <a built rgm136 sparsity.elf>
         --elf211 <a built rgm211 sparsity.elf> [case ...]

THE SANDBOX: it refuses unless it runs where no /dev/et* is a device node (inside W/nodev.sh), and then EVERY CASE runs in a bubblewrap of its
own: a private /dev holding two REGULAR FILES named /dev/et0_ops and /dev/et0_mgmt, a private /run/lock (the card's lock file etsoc-shire0.lock
made there, root's inside the case's user namespace: the runner refuses a lock that is not root's), a private PID namespace and /proc, the host
name aifoundry2. The stand-in box root holds the REAL built kernel ELFs (rgm136's at E136's pin: the runner's box check and THE IDENTITY GATE
PER PROCESS read it; rgm211's own, for the gate's refusal), stand-ins at build/ettelem/ettelem, build/rgm/host/sparsity_host and
build/e220brgm211/host/sparsity_host (each a script whose process name is the real tool's, so ps sees device-named processes), and build records of
today naming their sha256 (E208's BUILD-mms.json and E220's BUILD-e220b.json); everything else is the synced kit. Step 7's folder holds a desk
test's reboot-gate record (desk_test true), taken by start_e220b.sh only with E220B_DESKTEST=1, which marks the session DESKTEST (never collected).
THE CASES (each asserted from the session's own records; the time is the real pace, scale 1):
  MAIN       THE WHOLE REGISTERED SCHEDULE: the box check (both builds, the identity gate's check), the card's lock, the holders, the config and
             identity gates, the sampler, THE STOP-PATH TEST with E220's lines (70 W x 3, 70 C), the identity read, the 60 s opening rest, THE
             SMOKE (three processes, gated: E208's smoke arms, s01 by D1), all 103 runs in the registered order - the tie, pass 1, the tie,
             pass 2, the tie, then THE G BLOCK LAST: its smoke s03 and its 16 runs, 17 processes on rgm211's host's stand-in with rgm136's
             real ELF, each gated GATE OK and its walk 'mn' ok - every process under its sized plain timeout (xf04's `timeout 13`, every
             other `timeout 10`: E218's R0 lesson), the closing config read, the manifest; then E208's reducer UNCHANGED on the session and the
             frozen scorer score_e220.py (--b) on its output (arm B's R0 PASS, every registered point read, the runs named by their E220 ids,
             the clock in every sample)
  STEP       the governor steps p03b's clock DOWN to 600 MHz 2 s into its process (run 8, 2 shires: a run the toy card's 45 W burst cap
             never holds back, inside its busy window); the reducer and the frozen scorer FLAG it (STEP); then the operator's STOP as run 009
             begins (in MAIN the same run, unstepped, carries no STEP flag: the control)
  BOARD      the board 60 W over the toy card's lift in t01's process (run 1): THE BOARD STOP (E220's line: above 70 W on 3 samples)
  DIE        the die 25 C over in t01's process: THE DIE STOP (the shires' mean at or above 70 C)
  LATCH      the hottest-sensor latch rises from 60 to 75 C in t01's process and holds: THE LATCH STOP (at or above 70 C once it has risen)
  LATCHHI    the latch reads 85 C from the first sample and never rises (high from before the session): no latch stop; the operator's STOP at run 3
  RUNTIME    a runtime line splits t01's check record (E191's lesson): that process reads no check; the frozen scorer's R0 then FAILS
  HANG       t01's host ignores SIGTERM and lives 75 s past its end: a LEFTOVER, no closing read, the card's lock held until the host ends BY ITSELF
  QUIET      the sampler goes quiet after 1,000 samples and ignores SIGTERM for 25 s: not live; stopped by SIGTERM and started again
  HOLDER     another login's holder line from et-who's second read: the gate, no launch
  BUSYLOCK   another process holds the card's lock for 60 s: one retry after 15 s, then no device opened
  NOLOCK     no card lock file on the box: no device opened
  WRONGCFG   the config read names another card: the identity gate, no launch
  TWOFAIL    every host after the fourth fails its check: two failed processes in a row stop the session
  GWALK      s03's process (the G block's smoke, run 87, its own gate and stop path) prints walk_ok false: THE KERNEL STOP (the walk check);
             no G point starts; the 86 runs before stand; no SIGKILL
  GHANG      s03's G host ignores SIGTERM and lives 75 s past its end: a LEFTOVER after the G block's first process, the session ends at once,
             no closing read, the card's lock held until the host ends BY ITSELF; no SIGKILL
  GTRIP      the board 60 W over in every G process alone (MMS_FAKE_TRIP_ARM=nc): THE BOARD STOP in s03; nothing further; the 86 runs before stand
  GATE       rgm211's real ELF in rgm136's place before the start: the box check refuses it (E208's, first: the ELF not E136's pin; E220's
             gate per family would refuse it next): no device opened (runner rc 16)
  STALE220   E220's build record of yesterday: E220's box check refuses (rc 16), no device opened
  HOST216    rgm211's host not at the sha256 E220's build record names: E220's box check refuses (rc 16), no device opened
  R-OLD, R-NODIR, R-BOOT, R-DIFF, R-QUIET, R-HOST, R-NODESK, R-NOB216   start_e220b.sh's refusals: a first card command 200 s old; no step 7 folder;
             a reboot-gate record of another boot; one not EQUAL; THE QUIET DESK FLAG another's; the host name aifoundry3; a desk record without
             E220B_DESKTEST=1; no E220 build record: nothing started, no device opened
  R-REAL     the start's REAL path: a reboot-gate record that is not a desk test's (desk_test false), E220B_DESKTEST unset: STARTED with no
             DESKTEST mark; the case's box has no card lock file, so the runner ends at its card-lock gate before any card command
             (queue.json t_first_ms null, which the rest rule never counts)
Prints one line a case and DESKTEST-REALPATH-E220 <n> of <m> PASS (or FAIL) last.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"
STANDIN = """#!/usr/bin/python3 -IB
# E220's real-path desk test: a stand-in for the real tool at this path (desk/standin_e220b.py says what it does)
import os, runpy, sys
sys.argv = [os.environ["E220B_SI"], "{mode}"] + sys.argv[1:]
runpy.run_path(os.environ["E220B_SI"], run_name="__main__")
"""
ETWHO = """#!/bin/sh
# E220's real-path desk test: the stand-in for et-who (desk/standin_e220b.py etwho)
exec /usr/bin/python3 -I -B "$E220B_SI" etwho "$@"
"""
HOLDER = """import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(fd, fcntl.LOCK_EX)
open(sys.argv[2], "w").write("held")
time.sleep(float(sys.argv[3]))
"""
CASES = {
    "MAIN": {},
    "STEP": {"env": {"E220B_SI_STEP_S": "2.0", "E220B_SI_STEP_ARM": "1x4x17-fp32-rnd-s2"}, "stop_at": "run 009-"},
    "BOARD": {"env": {"MMS_FAKE_TRIP": "60", "MMS_FAKE_TRIP_ARM": "2x4x4-fp32-rnd"}},
    "DIE": {"env": {"E220B_SI_DIE_ADD": "25", "E220B_SI_DIE_ARM": "2x4x4-fp32-rnd"}},
    "LATCH": {"env": {"E220B_SI_LATCH_RISE": "15", "E220B_SI_LATCH_ARM": "2x4x4-fp32-rnd"}},
    "LATCHHI": {"env": {"E220B_SI_LATCH0": "85"}, "stop_at": "run 003-"},
    "RUNTIME": {"env": {"E220B_SI_RUNTIME": "split", "E220B_SI_RUNTIME_ARM": "2x4x4-fp32-rnd"}, "stop_at": "run 003-"},
    "HANG": {"env": {"E220B_SI_IGNORE_TERM_S": "75", "E220B_SI_HANG_ARM": "2x4x4-fp32-rnd"}},
    "QUIET": {"env": {"MMS_FAKE_SAMPLER_STALL": "1000"}, "stop_at": "run 004-"},
    "HOLDER": {"env": {"MMS_FAKE_HOLDER_AFTER": "1"}},
    "BUSYLOCK": {"hold_lock_s": 60},
    "NOLOCK": {"lockfile": False},
    "WRONGCFG": {"env": {"MMS_FAKE_WRONG_CONFIG": "1"}},
    "TWOFAIL": {"env": {"MMS_FAKE_HOST_FAIL_AFTER": "4"}},
    "GWALK": {"env": {"E220B_SI_WALK_FAIL_ARM": "nc6x5x10-fp32-rnd"}},
    "GHANG": {"env": {"E220B_SI_IGNORE_TERM_S": "75", "E220B_SI_HANG_ARM": "nc6x5x10-fp32-rnd"}},
    "GTRIP": {"env": {"MMS_FAKE_TRIP": "60", "MMS_FAKE_TRIP_ARM": "nc"}},
    "GATE": {"elf211_as_elf": True},
    "STALE220": {"build216_day": "2026-11-18"},
    "HOST216": {"build216_host_sha": "0" * 64},
    "R-OLD": {"first_age": 200, "refusal": True},
    "R-NODIR": {"firstdir": False, "refusal": True},
    "R-BOOT": {"record_boot_shift": -86400, "refusal": True},
    "R-DIFF": {"record_verdict": "DIFFERENT", "refusal": True},
    "R-QUIET": {"quiet_owner": "another-lane", "refusal": True},
    "R-HOST": {"hostname": "aifoundry3", "refusal": True},
    "R-NODESK": {"unset": ["E220B_DESKTEST"], "refusal": True},
    "R-NOB216": {"no_build216": True, "refusal": True},
    "R-REAL": {"unset": ["E220B_DESKTEST"], "record_desk": False, "lockfile": False},
}
SCHED = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "box", "a2c0-E220.json")))
G_ORDER = [r["arm"] for r in SCHED["runs"] if r.get("family") == "rgm136 gemmLnc"]      # s03, then the G block (xg08 ... n01)
G_FIRST = SCHED["runs"].index(next(r for r in SCHED["runs"] if r.get("family") == "rgm136 gemmLnc")) + 1     # 87: s03's place
N_RUNS = len(SCHED["runs"])                                                                                    # 103
N_G = len(G_ORDER)                                                                                             # 17


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def prepare(S, elf, elf211):
    base = os.path.join(S, "base")
    root = os.path.join(base, "root")
    os.makedirs(root)
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(E, "make_box_e220b.py"), "sync", root], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("the sync failed: " + r.stdout + r.stderr)
    for d in ("build/rgm/kernel", "build/rgm/host", "build/ettelem", "build/e220brgm211/host", "build/e220brgm211/kernel"):
        os.makedirs(os.path.join(root, d))
    shutil.copyfile(elf, os.path.join(root, "build", "rgm", "kernel", "sparsity.elf"))
    shutil.copyfile(elf211, os.path.join(root, "build", "e220brgm211", "kernel", "sparsity.elf"))
    if sha(os.path.join(root, "build", "rgm", "kernel", "sparsity.elf")) != PIN:
        raise SystemExit("the ELF given is not E136's pin")
    for p, mode in (("build/ettelem/ettelem", "reader"), ("build/rgm/host/sparsity_host", "host"),
                    ("build/e220brgm211/host/sparsity_host", "g-host")):
        open(os.path.join(root, p), "w").write(STANDIN.format(mode=mode))
        os.chmod(os.path.join(root, p), 0o755)
    os.makedirs(os.path.join(base, "bin"))
    open(os.path.join(base, "bin", "et-who"), "w").write(ETWHO)
    os.chmod(os.path.join(base, "bin", "et-who"), 0o755)
    import datetime
    try:
        from zoneinfo import ZoneInfo
        day = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    except Exception:  # noqa: BLE001
        day = time.strftime("%Y-%m-%d")
    rec = {"box": "aifoundry2", "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": PIN,
           "host_sha256": sha(os.path.join(root, "build/rgm/host/sparsity_host")), "ettelem_sha256": sha(os.path.join(root, "build/ettelem/ettelem")),
           "kernel_pin": PIN, "host_checks": ["desk-test stand-in"], "et_devices": "not a gate on aifoundry2 (one card)",
           "builder": "desk/realpath_e220b.py (a desk test's record: stand-ins for the host and the reader)"}
    json.dump(rec, open(os.path.join(root, "build", "BUILD-mms.json"), "w"), indent=1)
    rec2 = {"box": "aifoundry2", "day": day, "epoch": int(time.time()), "verdict": "BUILT",
            "host_sha256": sha(os.path.join(root, "build/e220brgm211/host/sparsity_host")), "host": "build/e220brgm211/host/sparsity_host",
            "host_checks": ["desk-test stand-in"], "family_g_gate": "GATE OK: a desk test's record (the runner's own gate reads the real ELF)",
            "builder": "desk/realpath_e220b.py (a desk test's record: a stand-in for rgm211's host)"}
    json.dump(rec2, open(os.path.join(root, "build", "BUILD-e220b.json"), "w"), indent=1)
    return base


def setup(S, base, name, cfg):
    d = os.path.join(S, name)
    shutil.copytree(base, d, symlinks=True)
    for n in ("et0_ops", "et0_mgmt"):
        open(os.path.join(d, n), "w").close()
    json.dump(cfg, open(os.path.join(d, "case.json"), "w"), indent=1)
    return d


def run_case(S, base, name, cfg):
    d = setup(S, base, name, cfg)
    args = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev", "--tmpfs", "/run/lock"]
    for n in ("et0_ops", "et0_mgmt"):
        args += ["--bind", os.path.join(d, n), "/dev/" + n]
    args += ["--unshare-user", "--uid", "0", "--gid", "0", "--unshare-pid", "--proc", "/proc", "--unshare-uts",
             "--hostname", cfg.get("hostname", "aifoundry2"), "--die-with-parent", "--",
             "/usr/bin/python3", "-I", "-B", os.path.abspath(__file__), "--inner", d]
    t0 = time.time()
    r = subprocess.run(args, capture_output=True, text=True)
    open(os.path.join(d, "inner.out"), "w").write(r.stdout + r.stderr)
    return d, time.time() - t0


def inner(d):
    cfg = json.load(open(os.path.join(d, "case.json")))
    root = os.path.join(d, "root")
    lock = "/run/lock/etsoc-shire0.lock"
    if cfg.get("lockfile", True):
        open(lock, "a").close()
    env = dict(os.environ)
    env.update(PATH=os.path.join(d, "bin") + ":" + env.get("PATH", "/usr/bin:/bin"), USER="root", MMS_FAKE_CARD="a2c0", MMS_FAKE_DIR="/dev",
               MMS_FAKE_SCALE="1", E220B_SI=os.path.join(HERE, "standin_e220b.py"), E220B_SI_SRC=os.path.join(root, "src"), E220B_DESKTEST="1",
               E220B_QUIET_FILE=os.path.join(d, "quiet-flag"), E220B_QUIET_LANE="card-e220b")
    env.update(cfg.get("env", {}))
    for k in cfg.get("unset", []):
        env.pop(k, None)
    if cfg.get("elf211_as_elf"):
        shutil.copyfile(os.path.join(root, "build", "e220brgm211", "kernel", "sparsity.elf"), os.path.join(root, "build", "rgm", "kernel", "sparsity.elf"))
    if cfg.get("no_build216"):
        os.remove(os.path.join(root, "build", "BUILD-e220b.json"))
    if cfg.get("build216_day") or cfg.get("build216_host_sha"):
        bp = os.path.join(root, "build", "BUILD-e220b.json")
        b = json.load(open(bp))
        b.update({k: v for k, v in (("day", cfg.get("build216_day")), ("host_sha256", cfg.get("build216_host_sha"))) if v})
        json.dump(b, open(bp, "w"), indent=1)
    open(os.path.join(d, "quiet-flag"), "w").write(f"{cfg.get('quiet_owner', 'card-e220b')} desk test\n")
    now = int(time.time())
    first = now - int(cfg.get("first_age", 10))
    if cfg.get("firstdir", True):
        fd = os.path.join(root, "first", str(first))
        os.makedirs(fd)
        bt = int([ln.split()[1] for ln in open("/proc/stat") if ln.startswith("btime ")][0]) + int(cfg.get("record_boot_shift", 0))
        bid = open("/proc/sys/kernel/random/boot_id").read().strip()
        json.dump({"schema": "fwgate-read/1", "box": "aifoundry2", "card": 0, "verdict": cfg.get("record_verdict", "EQUAL"), "boot_epoch": bt,
                   "boot_id": bid, "read_epoch": first, "desk_test": bool(cfg.get("record_desk", True)),
                   "ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl"},
                  open(os.path.join(fd, "fwgate-aifoundry2-c0-desktest.json"), "w"))
    holders = []
    if cfg.get("hold_lock_s"):
        hp = os.path.join(d, "holder.py")
        open(hp, "w").write(HOLDER)
        flag = os.path.join(d, "holder.flag")
        holders.append(subprocess.Popen(["/usr/bin/python3", "-I", "-B", hp, lock, flag, str(cfg["hold_lock_s"])]))
        t = time.time()
        while not os.path.exists(flag) and time.time() - t < 10:
            time.sleep(0.05)
    res = {"start": time.time(), "first": first}
    r = subprocess.run(["bash", os.path.join(root, "src", "start_e220b.sh"), str(now + 3 * 3600), str(first)], cwd=root, env=env,
                       capture_output=True, text=True, timeout=120)
    res["start_rc"], res["start_out"] = r.returncode, r.stdout + r.stderr
    sid = None
    for ln in r.stdout.splitlines():
        if ln.startswith("STARTED"):
            sid = ln.split()[2] if ln.split()[1] == "DESKTEST" else ln.split()[1]
    res["sid"] = sid
    if sid:
        sd = os.path.join(root, "sessions", sid)
        stopped = False
        t = time.time()
        while time.time() - t < 3000:
            if os.path.exists(os.path.join(sd, "runner.rc")):
                break
            if cfg.get("stop_at") and not stopped and os.path.exists(os.path.join(sd, "session.log")) and \
                    cfg["stop_at"] in open(os.path.join(sd, "session.log")).read():
                so = subprocess.run(["bash", os.path.join(root, "src", "stop_mms.sh"), "a2c0", sid], cwd=root, env=env, capture_output=True, text=True)
                res["stop_out"] = so.stdout
                stopped = True
            time.sleep(0.5)
        res["waited_s"] = round(time.time() - t, 1)
        st = subprocess.run(["bash", os.path.join(root, "src", "status_mms.sh"), "a2c0", sid], cwd=root, env=env, capture_output=True, text=True)
        res["status_rc"], res["status_out"] = st.returncode, st.stdout
        res["ps_after"] = subprocess.run(["ps", "-eo", "pid=,comm="], capture_output=True, text=True).stdout
    for h in holders:
        h.wait()
    res["end"] = time.time()
    json.dump(res, open(os.path.join(d, "result.json"), "w"), indent=1)


# ------------------------------------------------------------------------------------------------- the assertions
class Case:
    def __init__(self, d):
        self.d = d
        self.res = json.load(open(os.path.join(d, "result.json"))) if os.path.exists(os.path.join(d, "result.json")) else {}
        self.root = os.path.join(d, "root")
        self.sid = self.res.get("sid")
        self.sd = os.path.join(self.root, "sessions", self.sid) if self.sid else None
        self.log = open(os.path.join(self.sd, "session.log")).read() if self.sd and os.path.exists(os.path.join(self.sd, "session.log")) else ""
        self.q = json.load(open(os.path.join(self.sd, "queue.json"))) if self.sd and os.path.exists(os.path.join(self.sd, "queue.json")) else {}
        self.rc = open(os.path.join(self.sd, "runner.rc")).read().strip() if self.sd and os.path.exists(os.path.join(self.sd, "runner.rc")) else None

    def has(self, s):
        return s in self.log

    def run(self, i):
        for p in glob.glob(os.path.join(self.sd, "runs", f"{i:03d}-*", "run.json")):
            return json.load(open(p))
        return None

    def ran(self):
        return [x for x in self.q.get("queue", []) if x.get("ran")]

    def text_all(self):
        out = []
        for dp, _, fn in os.walk(self.sd or self.d):
            for n in fn:
                p = os.path.join(dp, n)
                try:
                    b = open(p, "rb").read()
                    if n.endswith(".gz"):
                        b = gzip.decompress(b)
                    out.append(b.decode("utf-8", "replace"))
                except OSError:
                    pass
        return "\n".join(out)

    def samples(self):
        p = os.path.join(self.sd, "telemetry.jsonl.gz")
        if not os.path.exists(p):
            return []
        return [json.loads(x) for x in gzip.open(p, "rt") if x.startswith("{")]


def nokill(c):
    """no kill: no process of the case ended by signal 9 (rc 137 or -9 in any run or smoke record), and no record says one was sent (the runner's
    own 'never kill -9' / 'no kill -9' words are its statements of the rule, not a kill)"""
    import re
    t = c.text_all() + c.res.get("start_out", "")
    t = re.sub(r"(never|no) (kill -9|SIGKILL|`?timeout -k`?)", "", t)
    rcs = []
    for p in glob.glob(os.path.join(c.sd or c.d, "runs", "*", "run.json")) + glob.glob(os.path.join(c.sd or c.d, "smoke", "*", "smoke.json")):
        j = json.load(open(p))
        rcs += [x.get("rc") for x in j.get("procs", [])] if "procs" in j else [j.get("rc")]
    return [("no SIGKILL, kill -9 or timeout -k in any record of the case", not any(w in t for w in ("SIGKILL", "kill -9", "timeout -k"))),
            ("no process ended by signal 9 (no rc 137 or -9)", not any(r in (137, -9) for r in rcs))]


def common_ok(c):
    return [("started (DESKTEST)", c.res.get("start_rc") == 0 and c.sid is not None and "STARTED DESKTEST" in c.res.get("start_out", "")),
            ("the session ended: runner.rc and MANIFEST.sha256", c.rc is not None and os.path.exists(os.path.join(c.sd, "MANIFEST.sha256"))),
            ("the session folder carries step 7's folder (first/) and the DESKTEST mark", os.path.isdir(os.path.join(c.sd, "first"))
             and os.path.exists(os.path.join(c.sd, "DESKTEST")))]


def sched_order():
    return [(r["i"], r["arm"]) for r in json.load(open(os.path.join(E, "box", "a2c0-E220.json")))["runs"]]


def gates_of(c):
    p = os.path.join(c.sd, "gates.jsonl")
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def a_main(c):
    sm = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(c.sd, "smoke", "*", "smoke.json")))]
    sp = json.load(open(os.path.join(c.sd, "stop-path.json"))) if os.path.exists(os.path.join(c.sd, "stop-path.json")) else {}
    S = c.samples()
    arms = [(x["i"], x["arm"]) for x in c.ran()]
    g = gates_of(c)
    gruns = [c.run(i) for i in range(G_FIRST, N_RUNS + 1)]
    gprocs = [r["procs"][0] for r in gruns if r and r.get("procs")]
    out = common_ok(c) + [
        ("runner rc 0", c.rc == "0"),
        ("the box and the build line (E208's box check: kernel pin, harness, audit GO)", c.has("the box and the build: the host, build/")),
        ("E220's box check passed: its lines named at the start (70 W x 3, 70 C; line 67 W; family G on rgm211's host)", c.has("E220's lines: board above 70 W on 3 samples") and c.has("line 67 W")),
        ("the identity gate's own check read CHECK PASS (ident-check.txt)", "CHECK PASS" in (open(os.path.join(c.sd, "ident-check.txt")).read() if os.path.exists(os.path.join(c.sd, "ident-check.txt")) else "")),
        ("the config and identity gates passed", c.has("config start: {") and c.has("physical device ID 0")),
        ("THE STOP-PATH TEST passed with E220's real lines (70 W x 3, 70 C)", sp.get("ok") is True and sp.get("real_lines") == {"board_cap_w": 70.0, "cap_consecutive": 3, "abs_stop_c": 70.0}),
        ("the identity read: the sampler on card 0 only", c.has("the identity read: et-who")),
        ("the 60 s opening rest", c.has("the opening rest: 60 s at rest")),
        ("THE SMOKE: three processes, each good", len(sm) == 3 and all(x.get("good") for x in sm) and c.has("smoke gate passed")),
        (f"ALL {N_RUNS} RUNS ran in the registered order with E220's names", arms == sched_order() and len(arms) == N_RUNS),
        (f"THE G BLOCK LAST: runs {G_FIRST}-{N_RUNS} are s03 then xg08 ... n01, each on rgm211's host (its stand-in) with rgm136's real ELF",
         [r["arm"] for r in gruns if r] == G_ORDER and len(gprocs) == N_G and all(p["argv"][0] == "build/e220brgm211/host/sparsity_host"
                                                                                and p["argv"][p["argv"].index("--kernel") + 1] == "build/rgm/kernel/sparsity.elf" for p in gprocs)),
        ("every G process gated GATE OK for 'rgm136 gemmLnc' and its walk 'mn' ok", all(p.get("family") == "rgm136 gemmLnc" and p["gate"]["ok"]
                                                                                       and p["walk"]["ok"] for p in gprocs)),
        (f"THE IDENTITY GATE PER PROCESS: {3 + N_RUNS} gates (3 smoke, {N_RUNS - N_G} 'rgm136 gemmL' runs, {N_G} 'rgm136 gemmLnc'), every one OK",
         len(g) == 3 + N_RUNS and all(x["ok"] for x in g) and sum(1 for x in g if x["family"] == "rgm136 gemmLnc") == N_G),
        ("THE SIZED PLAIN TIMEOUT: xf04's process under `timeout 13`, every other run's under `timeout 10`, none with -k",
         timeouts_seen(c) == {"13": ["xf04"], "10": sorted({r["arm"] for r in SCHED["runs"]} - {"xf04"})}),
        ("no stop: the session ran to its end", not c.q.get("stop")),
        ("the closing config read made (no identity trip, no foreign stop, no leftover)", c.has("config end: {")),
        ("no LEFTOVER", "LEFTOVER" not in c.log and c.q.get("leftover") is None),
        ("THE CLOCK IN EVERY SAMPLE (mhz.minion present in every telemetry line)", bool(S) and all((s.get("mhz") or {}).get("minion") is not None for s in S)),
        ("the clock moves 600 -> 800 MHz inside a process (the governed double)", {600, 800} <= {(s.get("mhz") or {}).get("minion") for s in S}),
    ]
    return out + nokill(c)


def timeouts_seen(c):
    """{"<T>": [the arms whose host ran under `timeout <T>`]}: each run's host stand-in names its parent's plain timeout on its stderr's first
    line (desk/standin_e220b.py: STANDIN-TIMEOUT <T>, read from /proc of its parent, the runner's `timeout` process)"""
    out = {}
    for p in sorted(glob.glob(os.path.join(c.sd, "runs", "*", "proc-*.err"))):
        arm = os.path.basename(os.path.dirname(p)).split("-", 1)[1]
        first = (open(p, errors="replace").readline().split() or ["", ""])
        if first[0] == "STANDIN-TIMEOUT" and len(first) > 1:
            out.setdefault(first[1], set()).add(arm)
        else:
            out.setdefault("unread", set()).add(arm)
    return {k: sorted(v) for k, v in out.items()}


def reduce_and_score(c, tag):
    """E208's reducer, UNCHANGED (the lab's committed copy), on the session; then the frozen scorer on its output as arm B's measured side"""
    red = os.path.join(REPO, "tools", "claims-v3", "e208", "proposal", "src", "reduce_mms.py")
    out = os.path.join(c.d, f"data-{tag}.json")
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", red, c.sd, "--out", out, "--txt", os.path.join(c.d, f"reduce-{tag}.txt")],
                       capture_output=True, text=True)
    sd = os.path.join(c.d, f"scored-{tag}")
    r2 = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(E, "score_e220.py"), "--b", out, "--out", sd], capture_output=True, text=True,
                        env=dict(os.environ, OMP_NUM_THREADS="1"))
    open(os.path.join(c.d, f"score-{tag}.out"), "w").write(r2.stdout + r2.stderr)
    data = json.load(open(out)) if r.returncode == 0 else {}
    sc = os.path.join(sd, "scores-e220.json")
    scored = json.load(open(sc)) if r2.returncode == 0 and os.path.exists(sc) else {}
    return r.returncode, r2.returncode, data, scored


def a_main_scored(c):
    rr, rs, data, scored = reduce_and_score(c, "main")
    runs = {x["arm"]: x for x in data.get("runs", []) if x.get("ran")}
    r0 = (scored.get("verdicts") or {}).get("B:R0")
    pids = [p["id"] for p in json.load(open(os.path.join(E, "points-e220.json")))["points"]["B"]]
    B = (scored.get("arms") or {}).get("B") or {}
    read = [pid for pid in pids if pid in (B.get("measured") or {}) or pid in (B.get("route_m_REPORTED") or {})]
    g_read = [pid for pid in G_ORDER if pid in read]
    return [(f"E208's reducer, unchanged, reads the real-path session (rc 0) with every run ({N_RUNS})", rr == 0 and len(data.get("runs", [])) == N_RUNS),
            ("the control: p03b unstepped carries no STEP flag", not step_flagged(scored, "p03b")),
            ("the reducer's runs carry E220's ids, the G block's among them", set(pids) <= set(runs)),
            ("the frozen scorer reads the reducer's output (rc 0)", rs == 0),
            ("the scorer's R0 PASS on this session (every check exact or approx, the smoke good)", r0 == "PASS"),
            (f"the scorer reads every registered point ({len(read)} of {len(pids)}), the nine G points among them ({len(set(g_read))} distinct, "
             f"read in {len(g_read)} G-block runs)", len(read) == len(pids) and len(set(g_read)) == 9 and len(g_read) == N_G - 1)]


def step_flagged(scored, pid):
    """the frozen scorer's flag for a run of the point: '<pid> run <i>: [... 'STEP' ...]' (score_e220.read_b's form)"""
    fl = ((scored.get("arms") or {}).get("B") or {}).get("flags") or []
    return any(f.startswith(f"{pid} run ") and "'STEP'" in f for f in fl)


def a_step(c):
    rr, rs, data, scored = reduce_and_score(c, "step")
    r5 = [x for x in data.get("runs", []) if x.get("arm") == "p03b" and x.get("ran")]
    fr = r5[0].get("frac_800_after_step") if r5 else None
    S = c.samples()
    pr = c.run(8)
    return common_ok(c) + [("runner rc 0", c.rc == "0"), ("the reducer reads it (rc 0) and the scorer (rc 0)", rr == 0 and rs == 0),
                           (f"p03b's launches after its step leave the 800 MHz band (frac_800_after_step {fr})", fr is not None and fr < 1.0),
                           ("the sampler records the step: 600 MHz samples inside p03b's process", bool(pr) and any((s.get("mhz") or {}).get("minion") == 600
                             for s in S if pr["procs"][0]["t0_ms"] + 2500 <= s["t_ms"] <= pr["procs"][0]["t1_ms"] - 500)),
                           ("THE STEP IS FLAGGED by the frozen scorer for p03b (STEP)", step_flagged(scored, "p03b"))] + nokill(c)


def a_stopline(word):
    def f(c):
        r1 = c.run(1) or {}
        return common_ok(c) + [("runner rc 0", c.rc == "0"), (f"the {word} stop tripped during t01 (run 1)", word in str(c.q.get("stop"))),
                               ("nothing further started (every later run 'after a stop')", all(not x.get("ran") for x in c.q.get("queue", [])[1:])),
                               ("t01's host ended at its launch boundary by the stop file", any(p.get("stopped_by_file") for p in r1.get("procs", []))),
                               ("the marks record the safety trip", "safety_trip" in open(os.path.join(c.sd, "marks.jsonl")).read()
                                if os.path.exists(os.path.join(c.sd, "marks.jsonl")) else False)] + nokill(c)
    return f


def a_latchhi(c):
    S = c.samples()
    lat = {(s.get("temp_c") or {}).get("minshire", [None, None, None])[2] for s in S}
    return common_ok(c) + [("runner rc 0", c.rc == "0"), ("the latch read 85 C in every sample (high from before the session)", lat == {85}),
                           ("no latch stop: the session ran on (t01, n01t and more) until the operator's STOP", "latch" not in str(c.q.get("stop"))
                            and "operator" in str(c.q.get("stop")) and len(c.ran()) >= 2)] + nokill(c)


def a_runtime(c):
    r1 = c.run(1) or {}
    p = (r1.get("procs") or [{}])[0]
    out = open(os.path.join(c.sd, "runs", "001-t01", "proc-00.out")).read() if os.path.exists(
        os.path.join(c.sd, "runs", "001-t01", "proc-00.out")) else ""
    rr, rs, data, scored = reduce_and_score(c, "runtime")
    r0 = (scored.get("verdicts") or {}).get("B:R0")
    return common_ok(c) + [("the runtime line is inside the host's stdout", "[runtime] ET [DEVICE_LAYER]" in out),
                           ("that process reads NO check (None), never a wrong value", p.get("check") is None and p.get("launches_ok") is True),
                           ("the run is flagged and counted as a failed process (not a stop: one in a row)", "two failed" not in str(c.q.get("stop"))),
                           ("the reducer still reads t01's launches (rc 0)", rr == 0),
                           ("the frozen scorer's R0 FAILS (a process with no check printed)", r0 == "FAIL")] + nokill(c)


def a_hang(c):
    marker = os.path.exists(os.path.join(c.d, "root", "..", "hang-marker")) or False
    lo = c.q.get("leftover") or {}
    err = open(os.path.join(c.sd, "runs", "001-t01", "proc-00.err")).read() if os.path.exists(
        os.path.join(c.sd, "runs", "001-t01", "proc-00.err")) else ""
    return common_ok(c) + [("a LEFTOVER recorded (the host outlived timeout 10 by 20 s and the runner's SIGTERM by 30 s)", c.has("LEFTOVER: a host process outlived")),
                           ("the session ends at once: no run after t01", all(not x.get("ran") for x in c.q.get("queue", [])[1:])),
                           ("no closing config read beside a leftover", c.has("no closing config read: a device process of ours is left")),
                           ("the card's lock held until the host ended: LEFTOVER resolved", c.has("LEFTOVER resolved") and lo.get("resolved") is True),
                           ("the host ended BY ITSELF (its stderr's last line 'device held for'; no SIGKILL could have let it write it)",
                            "device held for" in err and "deaf to SIGTERM" in err)] + nokill(c)


def a_quiet(c):
    return common_ok(c) + [("the sampler found not live", c.has("the sampler is not live")),
                           ("stopped by SIGTERM and started again (attempt lines)", c.log.count("sampler started (attempt") >= 2),
                           ("runs went on after the restart", len(c.ran()) >= 2)] + nokill(c)


def a_gate16(words, launched=False):
    def f(c):
        procs = glob.glob(os.path.join(c.sd, "runs", "*", "proc-*.out")) + glob.glob(os.path.join(c.sd, "smoke", "*", "proc.out"))
        return common_ok(c) + [("runner rc 16 (a gate refused)", c.rc == "16"), (f"the log says: {words}", c.has(words)),
                               ("no host process launched", launched or not procs)] + nokill(c)
    return f


def a_twofail(c):
    return common_ok(c) + [("two failed processes in a row stop the session", "2 failed processes in a row" in str(c.q.get("stop")))] + nokill(c)


def a_refusal(words):
    def f(c):
        return [("start_e220b.sh refused (exit 3), nothing started", c.res.get("start_rc") == 3 and c.sid is None),
                (f"its words: {words}", words in c.res.get("start_out", "")),
                ("no session folder was made", not glob.glob(os.path.join(c.root, "sessions", "*-a2c0-E220")))]
    return f


def a_real(c):
    """the start's REAL path: a reboot-gate record that is not a desk test's, E220B_DESKTEST unset: STARTED with no DESKTEST mark; the box has no
    card lock file, so the runner ends at its card-lock gate before any card command (t_first_ms null: the rest rule never counts it)"""
    procs = glob.glob(os.path.join(c.sd or c.d, "runs", "*", "proc-*.out")) + glob.glob(os.path.join(c.sd or c.d, "smoke", "*", "proc.out"))
    out = c.res.get("start_out", "")
    return [("start_e220b.sh took the real record (exit 0): 'STARTED <sid>' with no DESKTEST word", c.res.get("start_rc") == 0 and c.sid is not None
             and "STARTED DESKTEST" not in out and ("STARTED " + str(c.sid)) in out),
            ("the session folder carries step 7's folder (first/) and NO DESKTEST mark", c.sd is not None and os.path.isdir(os.path.join(c.sd, "first"))
             and not os.path.exists(os.path.join(c.sd, "DESKTEST"))),
            ("the session ended: runner.rc and MANIFEST.sha256", c.rc is not None and os.path.exists(os.path.join(c.sd, "MANIFEST.sha256"))),
            ("runner rc 16 at the card-lock gate: no card lock /run/lock/etsoc-shire0.lock on this box", c.rc == "16"
             and c.has("no card lock /run/lock/etsoc-shire0.lock on this box")),
            ("queue.json: not dry, t_first_ms null (no card command: the rest rule lists it and never counts it)",
             c.q.get("dry") is False and "t_first_ms" in c.q and c.q.get("t_first_ms") is None),
            ("no host process launched", not procs)] + nokill(c)


def a_gblock(kind):
    def f(c):
        q = c.q.get("queue", [])
        before = q[:G_FIRST - 1]
        g7 = c.run(G_FIRST) or {}
        p7 = (g7.get("procs") or [{}])[0]
        out = common_ok(c) + [("runner rc 0", c.rc == "0"),
                              (f"the {G_FIRST - 1} runs before the G block ran (they stand as measured)", len(before) == G_FIRST - 1 and all(x.get("ran") for x in before)),
                              (f"s03 (run {G_FIRST}, the G block's smoke, its first process) ran on rgm211's host's stand-in, gated GATE OK", g7.get("arm") == "s03"
                               and p7.get("argv", [""])[0] == "build/e220brgm211/host/sparsity_host" and (p7.get("gate") or {}).get("ok") is True),
                              ("no G point started (xg08 ... n01)", all(not x.get("ran") for x in q[G_FIRST:]) and len(q) == N_RUNS)]
        if kind == "walk":
            out += [("THE KERNEL STOP by the walk check", "KERNEL STOP" in str(c.q.get("stop")) and "the walk check" in str(c.q.get("stop"))),
                    ("s03's process records the walk failure (walk_ok not true)", (p7.get("walk") or {}).get("ok") is False),
                    ("the closing config read made (a kernel stop is not a foreign stop)", c.has("config end: {"))]
        elif kind == "hang":
            lo = c.q.get("leftover") or {}
            gk = f"{G_FIRST:03d}-s03"
            err = open(os.path.join(c.sd, "runs", gk, "proc-00.err")).read() if os.path.exists(os.path.join(c.sd, "runs", gk, "proc-00.err")) else ""
            out += [("a LEFTOVER recorded after s03 (the G host outlived its timeout by 20 s and the runner's SIGTERM by 30 s)", c.has("LEFTOVER: a host process outlived")),
                    ("no closing config read beside a leftover", c.has("no closing config read: a device process of ours is left")),
                    ("the card's lock held until the host ended: LEFTOVER resolved", c.has("LEFTOVER resolved") and lo.get("resolved") is True),
                    ("the G host ended BY ITSELF (its stderr's last line 'device held for')", "device held for" in err and "deaf to SIGTERM" in err)]
        elif kind == "trip":
            out += [("THE BOARD STOP in s03 (above 70 W on 3 samples)", "board" in str(c.q.get("stop")) and "70 W" in str(c.q.get("stop"))),
                    ("s03's host ended at its launch boundary by the stop file", bool(p7.get("stopped_by_file")))]
        return out + nokill(c)
    return f


def a_boxcheck(words):
    def f(c):
        procs = glob.glob(os.path.join(c.sd, "runs", "*", "proc-*.out")) + glob.glob(os.path.join(c.sd, "smoke", "*", "proc.out"))
        return common_ok(c) + [("runner rc 16 (the box check refused)", c.rc == "16"), (f"its words: {words}", c.has(words)),
                               ("no device opened: no config read, no host process", not c.has("config start:") and not procs
                                and c.has("no device opened"))] + nokill(c)
    return f


ASSERT = {
    "MAIN": lambda c: a_main(c) + a_main_scored(c),
    "STEP": a_step,
    "BOARD": a_stopline("board"),
    "DIE": a_stopline("mean"),
    "LATCH": a_stopline("latch"),
    "LATCHHI": a_latchhi,
    "RUNTIME": a_runtime,
    "HANG": a_hang,
    "QUIET": a_quiet,
    "HOLDER": a_gate16("the identity read (the sampler running)"),
    "BUSYLOCK": a_gate16("the card's lock is held: no device opened"),
    "NOLOCK": a_gate16("no card lock /run/lock/etsoc-shire0.lock on this box"),
    "WRONGCFG": a_gate16("the gate, no launch"),
    "TWOFAIL": a_twofail,
    "GWALK": a_gblock("walk"),
    "GHANG": a_gblock("hang"),
    "GTRIP": a_gblock("trip"),
    "GATE": a_boxcheck("build/rgm/kernel/sparsity.elf: sha256 00402801"),
    "STALE220": a_boxcheck("build/BUILD-e220b.json is not today's BUILT on aifoundry2"),
    "HOST216": a_boxcheck("build/e220brgm211/host/sparsity_host: sha256"),
    "R-OLD": a_refusal("REFUSED: the first card command was"),
    "R-NODIR": a_refusal("REFUSED: no step 7 folder"),
    "R-BOOT": a_refusal("not this boot"),
    "R-DIFF": a_refusal("verdict DIFFERENT"),
    "R-QUIET": a_refusal("REFUSED: THE QUIET DESK FLAG is not this lane's"),
    "R-HOST": a_refusal("REFUSED: this is aifoundry3"),
    "R-NODESK": a_refusal("a desk test's record"),
    "R-NOB216": a_refusal("REFUSED: no E220 build record (rgm211's host)"),
    "R-REAL": a_real,
}


def main(argv):
    if argv[:1] == ["--inner"]:
        inner(argv[1])
        return 0
    if len(argv) < 5 or argv[1] != "--elf" or argv[3] != "--elf211":
        print(__doc__)
        return 2
    S, elf, elf211 = os.path.abspath(argv[0]), os.path.abspath(argv[2]), os.path.abspath(argv[4])
    names = argv[5:] or list(CASES)
    if os.path.realpath(S).startswith(os.path.realpath(REPO) + os.sep):
        print("the scratch folder must be outside the repository")
        return 2
    for p in glob.glob("/dev/et*"):
        if not os.path.isfile(p):
            print(f"REFUSED: {p} is a device node here: run this inside W/nodev.sh")
            return 2
    os.makedirs(S, exist_ok=True)
    if os.listdir(S):
        print("give an empty scratch folder")
        return 2
    print(f"E220 REAL-PATH DESK TEST {time.strftime('%Y-%m-%d %H:%M:%S %Z')}: {len(names)} cases at the real pace, each in its own sandbox")
    base = prepare(S, elf, elf211)
    results = {}
    th = []

    def go(n):
        results[n] = run_case(S, base, n, CASES[n])
    for n in names:
        t = threading.Thread(target=go, args=(n,))
        t.start()
        th.append(t)
        time.sleep(1.0)
    for t in th:
        t.join()
    n_ok = n_all = 0
    for n in names:
        d, secs = results[n]
        c = Case(d)
        try:
            checks = ASSERT[n](c)
        except Exception as e:  # noqa: BLE001
            checks = [(f"the case's records could be read ({type(e).__name__}: {e})", False)]
        ok = all(v for _, v in checks)
        n_all += 1
        n_ok += ok
        print(f"{'PASS' if ok else 'FAIL'} {n} ({secs:.0f} s; runner rc {c.rc}; start rc {c.res.get('start_rc')}; stop {str(c.q.get('stop'))[:70]})")
        for w, v in checks:
            print(f"    {'ok  ' if v else 'FAIL'} {w}")
        if not ok:
            print("    the log's last lines: " + " | ".join(c.log.strip().splitlines()[-6:])[:1500])
            print("    start: " + c.res.get("start_out", "")[-600:].replace("\n", " | "))
    print(f"DESKTEST-REALPATH-E220B {n_ok} of {n_all} {'PASS' if n_ok == n_all else 'FAIL'}")
    return 0 if n_ok == n_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
