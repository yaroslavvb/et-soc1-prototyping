#!/usr/bin/env python3
"""E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): THE REAL-PATH DESK TEST. The lesson (round log sections 104, 109 and
116: E183's two lost days, E191's split JSON): a check that runs only on the REAL path is never exercised by a dry pass. This runs E209's
session exactly as runbook step 9 launches it - the box root's src/start_e209.sh, then src/session_e209.sh, then E208's runner
src/run_mms.py UNCHANGED on its REAL path (no --dry) - in a box root made by make_box_e209.py sync, against stand-ins for every device tool
(desk/standin_e209.py: the reader behind E208's guard, the host, et-who; E208's own doubles inside), the card's lock and the nodes. Standard
library only.

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e209/desk/realpath_e209.py <scratch> --elf <a built sparsity.elf>
         [case ...]

THE SANDBOX: it refuses unless it runs where no /dev/et* is a device node (inside W/nodev.sh), and then EVERY CASE runs in a bubblewrap of its
own: a private /dev holding two REGULAR FILES named /dev/et0_ops and /dev/et0_mgmt, a private /run/lock (the card's lock file etsoc-shire0.lock
made there, root's inside the case's user namespace: the runner refuses a lock that is not root's), a private PID namespace and /proc, the host
name aifoundry2. The stand-in box root holds the REAL built kernel ELF (E136's pin: the runner's box check reads it), stand-ins at
build/ettelem/ettelem and build/rgm/host/sparsity_host (each a script whose process name is the real tool's, so ps sees device-named processes),
and a build record of today naming their sha256; everything else is the synced kit. Step 7's folder holds a desk test's reboot-gate record
(desk_test true), taken by start_e209.sh only with E209_DESKTEST=1, which marks the session DESKTEST (never collected as data).
THE CASES (each asserted from the session's own records; the time is the real pace, scale 1):
  MAIN       the registered schedule: the box check, the card's lock, the holders, the config and identity gates, the sampler, THE STOP-PATH
             TEST, the identity read, the 60 s opening rest, THE SMOKE (three processes, its gates), A1, N1, e29, e30, e14, then the
             operator's STOP (stop_mms.sh, as the card lane would) touched as run 006 begins: the host ends at its launch boundary, nothing
             further starts, the closing config read, the manifest; then E208's reducer UNCHANGED on the session and the frozen scorer on its
             output (R0 read, the runs named by their E209 ids, the clock in every sample)
  STEP       the governor steps e30's clock DOWN to 600 MHz 2 s into its process (inside its busy window); the reducer and the frozen scorer
             FLAG it (STEP), as registered (E209.md section 7); in MAIN the same run, unstepped, carries no STEP flag (the control)
  BOARD      the board 60 W over the toy card's lift in A1's process: THE BOARD STOP (above 85 W on 3 samples): nothing further starts
  DIE        the die 40 C over in A1's process: THE DIE STOP (the shires' mean at or above 80 C)
  LATCH      the hottest-sensor latch rises from 70 to 85 C in A1's process and holds: THE LATCH STOP (at or above 80 C once it has risen)
  LATCHHI    the latch reads 85 C from the first sample and never rises (high from before the session): no latch stop; the session runs on
             until the operator's STOP as run 003 begins
  RUNTIME    a runtime line splits A1's check record (E191's lesson): that process reads no check (a failed process, never a wrong value);
             the scorer's R0 then FAILS (a process with no check printed)
  HANG       A1's host ignores SIGTERM and lives 75 s past its end: the runner's SIGTERM to its timeout wrapper, then a LEFTOVER recorded,
             the session ends at once with no closing read and holds the card's lock until the host has ended BY ITSELF (its marker
             file; its stderr's last line): NO SIGKILL anywhere
  QUIET      the sampler goes quiet after 1,000 samples and ignores SIGTERM for 25 s: not live; stopped by SIGTERM and started again
  HOLDER     another login's holder line on the card from et-who's second read (the identity read with the sampler): the gate, no launch
  BUSYLOCK   another process holds the card's lock for 60 s: one retry after 15 s, then no device opened
  NOLOCK     no card lock file on the box: no device opened
  WRONGCFG   the config read names another card: the identity gate, no launch
  TWOFAIL    every host after the fourth fails its check: two failed processes in a row stop the session
  R-OLD, R-NODIR, R-BOOT, R-DIFF, R-QUIET, R-HOST, R-NODESK   start_e209.sh's refusals: a first card command 200 s old; no step 7 folder;
             a reboot-gate record of another boot; one not EQUAL; THE QUIET DESK FLAG another's; the host name aifoundry3; a desk record
             without E209_DESKTEST=1: nothing started, no device opened
  R-REAL     the start's REAL path: a reboot-gate record that is not a desk test's (desk_test false), E209_DESKTEST unset: STARTED with no
             DESKTEST mark; the case's box has no card lock file, so E208's runner ends at its card-lock gate before any card command
             (queue.json t_first_ms null, which the rest rule never counts)
Prints one line a case and DESKTEST-REALPATH-E209 <n> of <m> PASS (or FAIL) last.
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
# E209's real-path desk test: a stand-in for the real tool at this path (desk/standin_e209.py says what it does)
import os, runpy, sys
sys.argv = [os.environ["E209_SI"], "{mode}"] + sys.argv[1:]
runpy.run_path(os.environ["E209_SI"], run_name="__main__")
"""
ETWHO = """#!/bin/sh
# E209's real-path desk test: the stand-in for et-who (desk/standin_e209.py etwho)
exec /usr/bin/python3 -I -B "$E209_SI" etwho "$@"
"""
HOLDER = """import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(fd, fcntl.LOCK_EX)
open(sys.argv[2], "w").write("held")
time.sleep(float(sys.argv[3]))
"""
CASES = {
    "MAIN": {"stop_at": "run 006-"},
    "STEP": {"env": {"E209_SI_STEP_S": "2.0", "E209_SI_STEP_ARM": "2x8x4-int8-rnd"}, "stop_at": "run 005-"},
    "BOARD": {"env": {"MMS_FAKE_TRIP": "60", "MMS_FAKE_TRIP_ARM": "4x8x8-int8-rnd"}},
    "DIE": {"env": {"E209_SI_DIE_ADD": "40", "E209_SI_DIE_ARM": "4x8x8-int8-rnd"}},
    "LATCH": {"env": {"E209_SI_LATCH_RISE": "15", "E209_SI_LATCH_ARM": "4x8x8-int8-rnd"}},
    "LATCHHI": {"env": {"E209_SI_LATCH0": "85"}, "stop_at": "run 003-"},
    "RUNTIME": {"env": {"E209_SI_RUNTIME": "split", "E209_SI_RUNTIME_ARM": "4x8x8-int8-rnd"}, "stop_at": "run 003-"},
    "HANG": {"env": {"E209_SI_IGNORE_TERM_S": "75", "E209_SI_HANG_ARM": "4x8x8-int8-rnd"}},
    "QUIET": {"env": {"MMS_FAKE_SAMPLER_STALL": "1000"}, "stop_at": "run 004-"},
    "HOLDER": {"env": {"MMS_FAKE_HOLDER_AFTER": "1"}},
    "BUSYLOCK": {"hold_lock_s": 60},
    "NOLOCK": {"lockfile": False},
    "WRONGCFG": {"env": {"MMS_FAKE_WRONG_CONFIG": "1"}},
    "TWOFAIL": {"env": {"MMS_FAKE_HOST_FAIL_AFTER": "4"}},
    "R-OLD": {"first_age": 200, "refusal": True},
    "R-NODIR": {"firstdir": False, "refusal": True},
    "R-BOOT": {"record_boot_shift": -86400, "refusal": True},
    "R-DIFF": {"record_verdict": "DIFFERENT", "refusal": True},
    "R-QUIET": {"quiet_owner": "another-lane", "refusal": True},
    "R-HOST": {"hostname": "aifoundry3", "refusal": True},
    "R-NODESK": {"unset": ["E209_DESKTEST"], "refusal": True},
    "R-REAL": {"unset": ["E209_DESKTEST"], "record_desk": False, "lockfile": False},
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def prepare(S, elf):
    base = os.path.join(S, "base")
    root = os.path.join(base, "root")
    os.makedirs(root)
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(E, "make_box_e209.py"), "sync", root], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("the sync failed: " + r.stdout + r.stderr)
    os.makedirs(os.path.join(root, "build", "rgm", "kernel"))
    os.makedirs(os.path.join(root, "build", "rgm", "host"))
    os.makedirs(os.path.join(root, "build", "ettelem"))
    shutil.copyfile(elf, os.path.join(root, "build", "rgm", "kernel", "sparsity.elf"))
    if sha(os.path.join(root, "build", "rgm", "kernel", "sparsity.elf")) != PIN:
        raise SystemExit("the ELF given is not E136's pin")
    for p, mode in (("build/ettelem/ettelem", "reader"), ("build/rgm/host/sparsity_host", "host")):
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
           "builder": "desk/realpath_e209.py (a desk test's record: stand-ins for the host and the reader)"}
    json.dump(rec, open(os.path.join(root, "build", "BUILD-mms.json"), "w"), indent=1)
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
               MMS_FAKE_SCALE="1", E209_SI=os.path.join(HERE, "standin_e209.py"), E209_SI_SRC=os.path.join(root, "src"), E209_DESKTEST="1",
               E209_QUIET_FILE=os.path.join(d, "quiet-flag"), E209_QUIET_LANE="card-e209")
    env.update(cfg.get("env", {}))
    for k in cfg.get("unset", []):
        env.pop(k, None)
    open(os.path.join(d, "quiet-flag"), "w").write(f"{cfg.get('quiet_owner', 'card-e209')} desk test\n")
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
    r = subprocess.run(["bash", os.path.join(root, "src", "start_e209.sh"), str(now + 3 * 3600), str(first)], cwd=root, env=env,
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
        while time.time() - t < 900:
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


def a_main(c):
    sm = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(c.sd, "smoke", "*", "smoke.json")))]
    sp = json.load(open(os.path.join(c.sd, "stop-path.json"))) if os.path.exists(os.path.join(c.sd, "stop-path.json")) else {}
    S = c.samples()
    arms = [(x["i"], x["arm"]) for x in c.ran()]
    out = common_ok(c) + [
        ("runner rc 0", c.rc == "0"),
        ("the box and the build line (the real box check: kernel pin, harness, audit GO)", c.has("the box and the build: the host, build/")),
        ("the config and identity gates passed", c.has("config start: {") and c.has("physical device ID 0")),
        ("THE STOP-PATH TEST passed (both lines tripped, files touched, starts refused)", sp.get("ok") is True),
        ("the identity read: the sampler on card 0 only", c.has("the identity read: et-who")),
        ("the 60 s opening rest", c.has("the opening rest: 60 s at rest")),
        ("THE SMOKE: three processes, each good", len(sm) == 3 and all(x.get("good") for x in sm) and c.has("smoke gate passed")),
        ("runs 1-5 ran in the registered order with E209's names", arms[:5] == [(1, "4x8x8-int8-rnd"), (2, "null-1"), (3, "e29"), (4, "e30"), (5, "e14")]),
        ("the operator's STOP: nothing further started", "operator" in str(c.q.get("stop")) and c.has("STOP: the operator's STOP file")),
        ("run 006 (e05) cut by the stop: ran false or its host stopped by the file", (lambda r: r is not None and (not r.get("ran") or
            any("stop" in f for f in r.get("flags", []))))(c.run(6))),
        ("the closing config read made (no identity trip, no foreign stop, no leftover)", c.has("config end: {")),
        ("no LEFTOVER", "LEFTOVER" not in c.log and c.q.get("leftover") is None),
        ("THE CLOCK IN EVERY SAMPLE (mhz.minion present in every telemetry line)", bool(S) and all((s.get("mhz") or {}).get("minion") is not None for s in S)),
        ("the clock moves 600 -> 800 MHz inside a process (the governed double)", {600, 800} <= {(s.get("mhz") or {}).get("minion") for s in S}),
    ]
    return out + nokill(c)


def reduce_and_score(c, tag):
    """E208's reducer, UNCHANGED (the lab's committed copy), on the session; then the frozen scorer on its output"""
    red = os.path.join(REPO, "tools", "claims-v3", "e208", "proposal", "src", "reduce_mms.py")
    out = os.path.join(c.d, f"data-{tag}.json")
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", red, c.sd, "--out", out, "--txt", os.path.join(c.d, f"reduce-{tag}.txt")],
                       capture_output=True, text=True)
    sc = os.path.join(c.d, f"scored-{tag}.json")
    r2 = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(E, "score_e209.py"), out, "--out", sc], capture_output=True, text=True,
                        env=dict(os.environ, OMP_NUM_THREADS="1"))
    open(os.path.join(c.d, f"score-{tag}.out"), "w").write(r2.stdout + r2.stderr)
    data = json.load(open(out)) if r.returncode == 0 else {}
    scored = json.load(open(sc)) if r2.returncode == 0 and os.path.exists(sc) else {}
    return r.returncode, r2.returncode, data, scored


def a_main_scored(c):
    rr, rs, data, scored = reduce_and_score(c, "main")
    runs = {x["arm"]: x for x in data.get("runs", []) if x.get("ran")}
    r0 = ((scored.get("rules") or {}).get("R0") or {}).get("verdict")
    return [("E208's reducer, unchanged, reads the real-path session (rc 0)", rr == 0),
            ("the control: e30 unstepped carries no STEP flag", not step_flagged(scored, "e30")),
            ("the reducer's runs carry E209's ids (e29, e30, e14)", {"e29", "e30", "e14"} <= set(runs)),
            ("the frozen scorer reads the reducer's output (rc 0)", rs == 0),
            ("the scorer's R0 PASS on this session (every check exact or approx, the smoke good)", r0 == "PASS")]


def step_flagged(scored, pid):
    return any(fl.startswith("STEP") for run in ((scored.get("flags") or {}).get(pid) or {}).get("runs", []) for fl in run.get("flags", []))


def a_step(c):
    rr, rs, data, scored = reduce_and_score(c, "step")
    r30 = [x for x in data.get("runs", []) if x.get("arm") == "e30" and x.get("ran")]
    fr = r30[0].get("frac_800_after_step") if r30 else None
    S = c.samples()
    w = (r30[0].get("procs") or [{}]) if r30 else []
    return common_ok(c) + [("runner rc 0", c.rc == "0"), ("the reducer reads it (rc 0) and the scorer (rc 0)", rr == 0 and rs == 0),
                           (f"e30's launches after its step leave the 800 MHz band (frac_800_after_step {fr})", fr is not None and fr < 1.0),
                           ("the sampler records the step: 600 MHz samples inside e30's process", any((s.get("mhz") or {}).get("minion") == 600
                             for s in S if r30 and c.run(4) and c.run(4)["procs"][0]["t0_ms"] + 2500 <= s["t_ms"] <= c.run(4)["procs"][0]["t1_ms"] - 500)),
                           ("THE STEP IS FLAGGED by the frozen scorer for e30 (STEP)", step_flagged(scored, "e30"))] + nokill(c)


def a_stopline(word):
    def f(c):
        r1 = c.run(1) or {}
        return common_ok(c) + [("runner rc 0", c.rc == "0"), (f"the {word} stop tripped during A1", word in str(c.q.get("stop"))),
                               ("nothing further started (every later run 'after a stop')", all(not x.get("ran") for x in c.q.get("queue", [])[1:])),
                               ("A1's host ended at its launch boundary by the stop file", any(p.get("stopped_by_file") for p in r1.get("procs", []))),
                               ("the marks record the safety trip", "safety_trip" in open(os.path.join(c.sd, "marks.jsonl")).read()
                                if os.path.exists(os.path.join(c.sd, "marks.jsonl")) else False)] + nokill(c)
    return f


def a_latchhi(c):
    S = c.samples()
    lat = {(s.get("temp_c") or {}).get("minshire", [None, None, None])[2] for s in S}
    return common_ok(c) + [("runner rc 0", c.rc == "0"), ("the latch read 85 C in every sample (high from before the session)", lat == {85}),
                           ("no latch stop: the session ran on (A1, N1 and more) until the operator's STOP", "latch" not in str(c.q.get("stop"))
                            and "operator" in str(c.q.get("stop")) and len(c.ran()) >= 2)] + nokill(c)


def a_runtime(c):
    r1 = c.run(1) or {}
    p = (r1.get("procs") or [{}])[0]
    out = open(os.path.join(c.sd, "runs", "001-4x8x8-int8-rnd", "proc-00.out")).read() if os.path.exists(
        os.path.join(c.sd, "runs", "001-4x8x8-int8-rnd", "proc-00.out")) else ""
    rr, rs, data, scored = reduce_and_score(c, "runtime")
    r0 = ((scored.get("rules") or {}).get("R0") or {}).get("verdict")
    return common_ok(c) + [("the runtime line is inside the host's stdout", "[runtime] ET [DEVICE_LAYER]" in out),
                           ("that process reads NO check (None), never a wrong value", p.get("check") is None and p.get("launches_ok") is True),
                           ("the run is flagged and counted as a failed process (not a stop: one in a row)", "two failed" not in str(c.q.get("stop"))),
                           ("the reducer still reads A1's launches (rc 0)", rr == 0),
                           ("the frozen scorer's R0 FAILS (a process with no check printed)", r0 == "FAIL")] + nokill(c)


def a_hang(c):
    marker = os.path.exists(os.path.join(c.d, "root", "..", "hang-marker")) or False
    lo = c.q.get("leftover") or {}
    err = open(os.path.join(c.sd, "runs", "001-4x8x8-int8-rnd", "proc-00.err")).read() if os.path.exists(
        os.path.join(c.sd, "runs", "001-4x8x8-int8-rnd", "proc-00.err")) else ""
    return common_ok(c) + [("a LEFTOVER recorded (the host outlived timeout 10 by 20 s and the runner's SIGTERM by 30 s)", c.has("LEFTOVER: a host process outlived")),
                           ("the session ends at once: no run after A1", all(not x.get("ran") for x in c.q.get("queue", [])[1:])),
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
        return [("start_e209.sh refused (exit 3), nothing started", c.res.get("start_rc") == 3 and c.sid is None),
                (f"its words: {words}", words in c.res.get("start_out", "")),
                ("no session folder was made", not glob.glob(os.path.join(c.root, "sessions", "*-a2c0-E209")))]
    return f


def a_real(c):
    """the start's REAL path: a reboot-gate record that is not a desk test's, E209_DESKTEST unset: STARTED with no DESKTEST mark; the box has no
    card lock file, so the runner ends at its card-lock gate before any card command (t_first_ms null: the rest rule never counts it)"""
    procs = glob.glob(os.path.join(c.sd or c.d, "runs", "*", "proc-*.out")) + glob.glob(os.path.join(c.sd or c.d, "smoke", "*", "proc.out"))
    out = c.res.get("start_out", "")
    return [("start_e209.sh took the real record (exit 0): 'STARTED <sid>' with no DESKTEST word", c.res.get("start_rc") == 0 and c.sid is not None
             and "STARTED DESKTEST" not in out and ("STARTED " + str(c.sid)) in out),
            ("the session folder carries step 7's folder (first/) and NO DESKTEST mark", c.sd is not None and os.path.isdir(os.path.join(c.sd, "first"))
             and not os.path.exists(os.path.join(c.sd, "DESKTEST"))),
            ("the session ended: runner.rc and MANIFEST.sha256", c.rc is not None and os.path.exists(os.path.join(c.sd, "MANIFEST.sha256"))),
            ("runner rc 16 at the card-lock gate: no card lock /run/lock/etsoc-shire0.lock on this box", c.rc == "16"
             and c.has("no card lock /run/lock/etsoc-shire0.lock on this box")),
            ("queue.json: not dry, t_first_ms null (no card command: the rest rule lists it and never counts it)",
             c.q.get("dry") is False and "t_first_ms" in c.q and c.q.get("t_first_ms") is None),
            ("no host process launched", not procs)] + nokill(c)


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
    "R-OLD": a_refusal("REFUSED: the first card command was"),
    "R-NODIR": a_refusal("REFUSED: no step 7 folder"),
    "R-BOOT": a_refusal("not this boot"),
    "R-DIFF": a_refusal("verdict DIFFERENT"),
    "R-QUIET": a_refusal("REFUSED: THE QUIET DESK FLAG is not this lane's"),
    "R-HOST": a_refusal("REFUSED: this is aifoundry3"),
    "R-NODESK": a_refusal("a desk test's record"),
    "R-REAL": a_real,
}


def main(argv):
    if argv[:1] == ["--inner"]:
        inner(argv[1])
        return 0
    if len(argv) < 3 or argv[1] != "--elf":
        print(__doc__)
        return 2
    S, elf = os.path.abspath(argv[0]), os.path.abspath(argv[2])
    names = argv[3:] or list(CASES)
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
    print(f"E209 REAL-PATH DESK TEST {time.strftime('%Y-%m-%d %H:%M:%S %Z')}: {len(names)} cases at the real pace, each in its own sandbox")
    base = prepare(S, elf)
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
    print(f"DESKTEST-REALPATH-E209 {n_ok} of {n_all} {'PASS' if n_ok == n_all else 'FAIL'}")
    return 0 if n_ok == n_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
