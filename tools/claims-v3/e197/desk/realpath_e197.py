#!/usr/bin/env python3
"""E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): THE REAL-PATH DESK TEST's cases (desktest_realpath_e197.sh is
its entry; read its header for the sandbox). Each case: a stand-in aifoundry3 tree (the kit's synced files copied from the lab clone at
their repository paths under build/claims-v3/aifoundry3/e197, the box's own copy of E128's guard among them; fake_card_e197.py copied
to the host's path, to build/ettelem/ettelem, and to et-who and ps first on PATH; today's build record naming the stand-in host), its
own bubblewrap (a private /dev with /dev/et0_ops and /dev/et0_mgmt as REGULAR FILES, a private /run/lock with the card's lock file, a
private PID namespace, the host name aifoundry3), and session_e197.sh launched exactly as step 9 launches it (DRY unset; E197_T0,
E197_SIT, E197_PLAN, E197_FIRST, E197_LAST_END_EPOCH, E197_HARNESS_SHA256), with actions made mid-session where a case needs them
(a stop by hand, a signal, the watch killed, the lock taken). Every watt, degree and rate is a stand-in's arbitrary test value, never a
forecast and never a measurement; nothing here opens a device.

  python3 -I -B realpath_e197.py SRC SCRATCH [case ...]         (from desktest_realpath_e197.sh, inside W/nodev.sh)
  python3 -I -B realpath_e197.py --inner CASE_DIR               (inside a case's sandbox: start, act, wait, report)

THE CASES (each row's assertions are in check_<case> below; the audit of the dry branches is desk/dry-branches-e197.tsv):
  D1 D2 D3   --dry, sitting 1 full and short, sitting 2 ext: LISTING SAME against the registration's listings (429, 331, 277 device
             calls), the -dry directory, the DRY lines, no stand-in called, the manifest exact
  P          THE REAL PATH, sitting 1 full, whole (the smoke and blocks A-D at a fast stand-in launch): the first card command from step 7
             (E197_FIRST), CAP_S; one sampler through E128's guard, `sample --seconds <CAP_S+600> --every-ms 100`, ended by SIGTERM once;
             the runner's smoke gate and the kit's smoke check passed; 429 host processes IN THE REGISTERED ORDER (the registration's
             listing desk/dry-e197-full.txt, call for call), each under timeout, with the card lock held, --window 240000000 and
             --stop-file run/STOP; SESSION_DONE the reference's own; the summary (4 blocks complete, stop none, SITTING-RESULT); the
             manifest exact; then the registered reducer on the session's own files (rc 0, every train with processes / 2 units) and
             the kit's checker (CHECKS READ)
  P2         sitting 2 (ext) whole: 277 host processes in the registered order; then THE POOLED REDUCTION of P's and P2's sessions
             (T1's units 67 + 115 = 182; T7 and T14 scored)
  SH         sitting 1, the short plan, whole: 331 host processes in the registered order
  S1         a stop by hand (an empty STOP) after block B's first train process: exit 8, no host process after it, the stop read as not
             naming the card, SITTING-RESULT card stop none
  K1         the kit's board stop at its own boundary: readings alternating 65.0 and 66.0 W (at or above 65 W, distinct; the
             proposal's stopwatch stops above 65 W only, so it never does here): the watch's STOP, naming the card
  K2, K2b    the kit's clock stop: 500 MHz on 30 samples (STOP), and on 2 samples only (no clock stop; ended by hand)
  K3, K4     a die reading of 70 C; a sampler gone quiet: a stop naming the card (the stopwatch's, the runner's or the watch's)
  G1, G2, G3 the smoke: an anchor with 1,023 participants and an anchor that exits 1 (the runner's gate passes both; the kit's smoke
             check stops the sitting before block A's first device process: GATE-STOP); a train launch with check_bad (the runner's
             own smoke gate, exit 7: GATE-STOP)
  SP1, SP2   RUNTIME LINES IN THE HOST'S OUTPUT, with E191's committed runtime bytes ("Opening device 1" and its newline, read from
             1a4bc1e3's smoke stdout): inside a smoke train's REGFILE line (the registered runner drops that launch: 25 of 26, the
             smoke gate fails, exit 7, GATE-STOP, no train runs: the safe side), and between two of its lines (harmless: the smoke
             passes; ended by hand)
  H1 H2 H3   a holder, another user's device process, the card lock held, at the start: exit 3, GATE-STOP "no device opened by the
             session", no sampler and no host started
  H4         a holder before block B: run_session.sh stops (exit 3) after block A; SITTING-RESULT card stop none
  L1         the card lock taken after the sampler started: the smoke's lock busy (75), GATE-STOP, the sampler ended by SIGTERM
  X1         a crash: a host prints "REGFILE 5" in block A (valid JSON, no object): the registered runner raises; "the trains ended
             without a registered stop", exit 9
  HG         A HUNG HOST (departure D1): a host process ignores its timeout's TERM and lives 14 s: the watch's HUNG line and STOP at
             about 12 s, NO KILL (the host logs the TERM and ends by itself), the session ends at its next check (exit 8)
  T1, W1     SIGTERM to the wrapper mid-block (its STOP, the session's own end); the kit's watch killed mid-block (the wrapper's STOP)
  C1         the cap from the first card command (E197_DESKTEST=1, E197_CAP_S=370): the runner's deadline skips the trains that cannot
             fit, the session ends inside the cap, rc 0
  WE         the watch's end-stop alone (first card command + cap - 30 s): its STOP, not naming the card, then SESSION_DONE ends it
  R1-R10     refusals before anything (exit 2, "no device opened by the session"): a desk-test variable without E197_DESKTEST=1; the
             harness's sha256; a synced registered file changed; the build record not today; the host not the recorded one; USER;
             the first card command too old (R7; R7b at 5 minutes: the bound is 120 s) and in the future; the cap past the last end; no lock file
  TWO NONE OPS R13  the node count (two cards; none; ops without mgmt) and another host's name: refused before anything
  Z          no process left in any case; nothing but the cases' own regular files at /dev/et*
SPDX-License-Identifier: Apache-2.0
"""
import concurrent.futures
import fcntl
import hashlib
import json
import os
import pwd
import re
import shutil
import signal
import subprocess
import sys
import time

E = "tools/claims-v3/e197"
WR = "build/claims-v3/aifoundry3/e197"
E191_STDOUT = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random/stdout.txt"
E191_SUMS = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/SHA256SUMS"


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def jl(p):
    out = []
    try:
        for ln in open(p, errors="replace"):
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


# =============================================== inside a case's sandbox ===============================================
HOLDER = """import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(fd, fcntl.LOCK_EX)
open(sys.argv[2], 'w').write('held')
time.sleep(float(sys.argv[3]))
"""


def inner(d):
    cfg = json.load(open(os.path.join(d, "case.json")))
    tree = os.path.join(d, "tree")
    lock = "/run/lock/etsoc-shire0.lock"
    if cfg.get("lockfile", True):
        open(lock, "a").close()
    holders = []

    def take_lock(seconds):
        hp = os.path.join(d, "holder.py")
        open(hp, "w").write(HOLDER)
        flag = os.path.join(d, "holder.flag")
        if os.path.exists(flag):
            os.unlink(flag)
        h = subprocess.Popen(["/usr/bin/python3", "-I", "-B", hp, lock, flag, str(seconds)], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        holders.append(h)
        t0 = time.time()
        while not os.path.exists(flag) and time.time() - t0 < 10:
            time.sleep(0.02)

    now = int(time.time())
    env = dict(os.environ)
    env["PATH"] = os.path.join(d, "bin") + ":" + env.get("PATH", "/usr/bin:/bin")
    env["E197_STANDIN_DIR"] = os.path.join(d, "sd")
    env["E197_STANDIN_TABLE"] = cfg["table"]
    env["USER"] = pwd.getpwuid(os.getuid()).pw_name
    for k, v in cfg.get("env", {}).items():
        if isinstance(v, str) and v.startswith("@NOW"):
            v = str(now + int(v[4:] or 0))
        env[k] = str(v)
    for k in cfg.get("unset", []):
        env.pop(k, None)
    if cfg.get("lock_at_start"):
        take_lock(cfg["lock_at_start"])
    res = {"t0": env.get("E197_T0"), "first": env.get("E197_FIRST"), "start": time.time(), "actions": []}
    out = open(os.path.join(d, "wrapper.out"), "w")
    if cfg.get("alone"):   # the registered run_session.sh alone (its own refusals), from a ref/ folder as the wrapper makes it
        ref = os.path.join(d, "ref")
        os.makedirs(ref, exist_ok=True)
        for f, q in (("run_session.sh", "proposal/src/run_session.sh"), ("stopwatch.py", "proposal/src/stopwatch.py"),
                     ("trains.tsv", "proposal/src/trains.tsv"), ("run_trains.py", "lab/run_trains.py")):
            shutil.copyfile(os.path.join(tree, WR, E, q), os.path.join(ref, f))
        env["H"] = WR + "/build/regfile/host/regfile_host"
        env["ETTELEM"] = WR + "/tools/claims-v3/e128/ettelem_guard.sh"
        env["LOCK"] = lock
        env["GAP"] = "30"
        sdir = os.path.join(d, "alone")
        run = os.path.join(sdir, "run")
        os.makedirs(sdir, exist_ok=True)
        p = subprocess.Popen(["bash", os.path.join(ref, "run_session.sh"), run, "full"], cwd=tree, env=env, stdout=out,
                             stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    else:
        wrapper = os.path.join(tree, WR, E, "session_e197.sh")
        p = subprocess.Popen(["bash", wrapper] + cfg.get("args", []), cwd=tree, env=env, stdout=out, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL)
        sdir = os.path.join(tree, "build/e197/T%s%s" % (env.get("E197_T0"), "-dry" if cfg.get("args") == ["--dry"] else ""))
        run = os.path.join(sdir, "run")
    deadline = time.time() + cfg.get("timeout", 900)
    for act in cfg.get("actions", []):
        w = act["when"]
        while p.poll() is None and time.time() < deadline:
            ok = False
            if "train_mark" in w:   # a train mark (the process ended) of this train label
                ok = any(m.get("kind") == "train" and m.get("train") == w["train_mark"] for m in jl(os.path.join(run, "marks.jsonl")))
            elif "block_train" in w:
                ok = any(m.get("kind") == "train" and m.get("block") == w["block_train"] for m in jl(os.path.join(run, "marks.jsonl")))
            elif "block_after" in w:   # a block's closing 10 s idle ended: the 30 s gap begins
                ok = any(m.get("kind") == "idle" and m.get("label") == "after" and m.get("block") == w["block_after"]
                         for m in jl(os.path.join(run, "marks.jsonl")))
            elif "sampler_s" in w:
                ss = [r for r in jl(os.path.join(d, "sd", "calls", "sampler.log")) if r.get("mode") == "sample"]
                ok = bool(ss) and time.time() * 1000 - ss[0]["t_ms"] >= w["sampler_s"] * 1000
            if ok:
                break
            time.sleep(0.1)
        if p.poll() is not None:
            break
        do = act["do"]
        t = time.time()
        if do == "touch_stop":
            open(os.path.join(run, "STOP"), "a").close()
        elif do == "term_wrapper":
            p.send_signal(signal.SIGTERM)
        elif do == "kill_watch":
            for q in os.listdir("/proc"):
                if q.isdigit():
                    try:
                        cl = open("/proc/%s/cmdline" % q, "rb").read().split(b"\0")
                    except OSError:
                        continue
                    if any(x.endswith(b"watch_e197.py") for x in cl):
                        os.kill(int(q), signal.SIGTERM)
        elif do == "term_run_session":
            for q in os.listdir("/proc"):
                if q.isdigit():
                    try:
                        cl = open("/proc/%s/cmdline" % q, "rb").read().split(b"\0")
                    except OSError:
                        continue
                    if len(cl) > 1 and cl[0] == b"bash" and cl[1].endswith(b"/ref/run_session.sh"):
                        os.kill(int(q), signal.SIGTERM)
        elif do == "take_lock":
            take_lock(act.get("seconds", 120))
        res["actions"].append({"do": do, "t_ms": int(t * 1000)})
    try:
        rc = p.wait(timeout=max(1, deadline - time.time()))
    except subprocess.TimeoutExpired:
        p.send_signal(signal.SIGTERM)       # the test's own bound on the wrapper (a bash script, never a device process)
        rc = p.wait(timeout=60)
        res["timed_out"] = True
    res["rc"] = rc
    res["end"] = time.time()
    for h in holders:
        h.terminate()
        h.wait(timeout=10)
    time.sleep(1.0)
    left = []
    for q in os.listdir("/proc"):
        if q.isdigit() and int(q) != os.getpid():
            try:
                cl = open("/proc/%s/cmdline" % q, "rb").read().replace(b"\0", b" ").decode(errors="replace")
            except OSError:
                continue
            if re.search(r"session_e197|run_session|run_trains|stopwatch|watch_e197|regfile_host|ettelem|holder\.py", cl):
                left.append(cl[:120])
    res["left"] = left
    json.dump(res, open(os.path.join(d, "result.json"), "w"), indent=1)
    return 0


# =============================================== the outer side: set up, run, check ===============================================
class Ctx:
    def __init__(self, src, s):
        self.src, self.s = src, s
        self.kit = os.path.join(src, E)
        self.table = os.path.join(self.kit, "desk", "host-list-e197.jsonl")
        self.hsha = sha(os.path.join(self.kit, "harness-e197.json"))
        r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(self.kit, "harness_e197.py"), "--list"], capture_output=True,
                           text=True, check=True)
        self.files = [p for p in r.stdout.split("\n") if p]


def setup(ctx, name, cfg):
    d = os.path.join(ctx.s, name)
    tree = os.path.join(d, "tree")
    R = os.path.join(tree, WR)
    for p in ctx.files:
        q = os.path.join(R, p)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        shutil.copy2(os.path.join(ctx.src, p), q)
    fake = os.path.join(ctx.kit, "fake_card_e197.py")
    for q in (os.path.join(R, "build/regfile/host/regfile_host"), os.path.join(tree, "build/ettelem/ettelem"),
              os.path.join(d, "bin", "et-who"), os.path.join(d, "bin", "ps")):
        os.makedirs(os.path.dirname(q), exist_ok=True)
        shutil.copyfile(fake, q)
        os.chmod(q, 0o755)
    H = os.path.join(R, "build/regfile/host/regfile_host")
    built = os.path.join(R, "build/regfile-built.txt")
    with open(built, "w") as f:
        f.write("REGFILE-BUILT %s\nkernel %s\ntext %s\nhost %s\nsampler %s\nsignal host none| none\n" % (
            time.strftime("%F %T %Z"), "0" * 64, "0" * 64, sha(H) if not cfg.get("built_host_wrong") else "1" * 64,
            sha(os.path.join(tree, "build/ettelem/ettelem"))))
    if cfg.get("built_yesterday"):
        t = time.time() - 86400 * 1.5
        os.utime(built, (t, t))
    for p, extra in cfg.get("tamper", {}).items():
        with open(os.path.join(R, p), "ab") as f:
            f.write(extra.encode())
    os.makedirs(os.path.join(d, "sd"), exist_ok=True)
    json.dump(cfg.get("scenario", {}), open(os.path.join(d, "sd", "scenario.json"), "w"))
    for n in cfg.get("nodes", ["et0_ops", "et0_mgmt"]):
        open(os.path.join(d, n), "w").close()
    c = dict(cfg)
    c["table"] = ctx.table
    env = {"E197_T0": "@NOW", "E197_SIT": "1", "E197_PLAN": "full", "E197_FIRST": "@NOW-20", "E197_LAST_END_EPOCH": "@NOW+14400",
           "E197_HARNESS_SHA256": ctx.hsha}
    env.update(cfg.get("env", {}))
    c["env"] = env
    json.dump(c, open(os.path.join(d, "case.json"), "w"), indent=1)
    return d


def run(ctx, name, cfg):
    d = setup(ctx, name, cfg)
    args = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev", "--tmpfs", "/run/lock"]
    for n in cfg.get("nodes", ["et0_ops", "et0_mgmt"]):
        args += ["--bind", os.path.join(d, n), "/dev/" + n]
    args += ["--unshare-pid", "--proc", "/proc", "--unshare-uts", "--hostname", cfg.get("hostname", "aifoundry3"), "--die-with-parent",
             "--", "/usr/bin/python3", "-I", "-B", os.path.abspath(__file__), "--inner", d]
    t0 = time.time()
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        open(os.path.join(d, "inner.err"), "w").write(r.stdout + r.stderr)
    return name, d, time.time() - t0


# ------------------------------------------------- the reading helpers -------------------------------------------------
class Case:
    def __init__(self, d):
        self.d = d
        self.res = json.load(open(os.path.join(d, "result.json"))) if os.path.exists(os.path.join(d, "result.json")) else {}
        self.cfg = json.load(open(os.path.join(d, "case.json")))
        t0 = self.res.get("t0")
        dry = self.cfg.get("args") == ["--dry"]
        if self.cfg.get("alone"):
            self.sd = os.path.join(d, "alone")
            self.run = os.path.join(self.sd, "run")
            logp = os.path.join(self.run, "session.log")
        else:
            self.sd = os.path.join(d, "tree", "build/e197/T%s%s" % (t0, "-dry" if dry else ""))
            self.run = os.path.join(self.sd, "run")
            logp = os.path.join(self.sd, "session.log")
        try:
            self.log = open(logp, errors="replace").read()
        except OSError:
            self.log = ""
        self.marks = jl(os.path.join(self.run, "marks.jsonl"))
        self.runs = jl(os.path.join(self.run, "runs.jsonl"))
        self.hosts = [r for r in jl(os.path.join(d, "sd", "calls", "host.log")) if "argv" in r and not r.get("refused")]
        self.samplers = jl(os.path.join(d, "sd", "calls", "sampler.log"))
        self.stop = None
        sp = os.path.join(self.run, "STOP")
        if os.path.exists(sp):
            txt = open(sp).read()
            try:
                self.stop = json.loads(txt.splitlines()[0])
            except (ValueError, IndexError):
                self.stop = {"by": "by hand", "raw": txt}
        self.watch = jl(os.path.join(self.sd, "watch.jsonl"))

    def rc(self):
        return self.res.get("rc")

    def has(self, pat):
        return re.search(pat, self.log, re.M) is not None

    def manifest_ok(self):
        m = os.path.join(self.sd, "MANIFEST.sha256")
        if not os.path.exists(m):
            return False
        r = subprocess.run(["sha256sum", "-c", "--quiet", "MANIFEST.sha256"], cwd=self.sd, capture_output=True, text=True)
        return r.returncode == 0

    def wrapper_rc(self):
        try:
            return int(open(os.path.join(self.sd, "wrapper.rc")).read().strip())
        except (OSError, ValueError):
            return None


def listing_calls(ctx, plan, run_rel):
    out = []
    for ln in open(os.path.join(ctx.kit, "desk", "dry-e197-%s.txt" % plan)):
        ln = ln.rstrip("\n")
        if ln.startswith("DRY: timeout 10 build/host/regfile_host "):
            a = ln[len("DRY: timeout 10 build/host/regfile_host "):].split()
            out.append([x.replace("out-%s/STOP" % plan, run_rel + "/STOP") for x in a])
    return out


def order_ok(ctx, c, plan):
    run_rel = "build/e197/T%s/run" % c.res.get("t0")
    want = listing_calls(ctx, plan, run_rel)
    have = [r["argv"] for r in sorted(c.hosts, key=lambda r: r["proc"])]
    return have == want, len(have), len(want)


def reduce(ctx, outdir, runs, name):
    o = os.path.join(outdir, name + ".json")
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(ctx.kit, "proposal/src/reduce_regfile.py")] + runs + ["--out", o],
                       capture_output=True, text=True)
    open(os.path.join(outdir, name + ".txt"), "w").write(r.stdout + r.stderr)
    return r.returncode, (json.load(open(o)) if r.returncode == 0 and os.path.exists(o) else None)


# ------------------------------------------------- the checks, one function a case -------------------------------------------------
def gate_nodev(c, rc=3):
    return [("exit %d" % rc, c.rc() == rc), ("GATE-STOP ... (no device opened by the session)",
                                            c.has(r" GATE-STOP: .*\(no device opened by the session\)$")),
            ("no sampler, no host started", not [s for s in c.samplers if s.get("mode") == "sample"] and not c.hosts),
            ("session end and the manifest exact", c.has(r" session end \(T0 \d+\)$") and c.manifest_ok())]


def refused(c):
    return [("exit 2", c.rc() == 2), ("refused ... (no device opened by the session)",
                                     c.has(r" GATE-STOP: refused: .*\(no device opened by the session\)$")),
            ("no et-who, no sampler, no host called", not os.path.exists(os.path.join(c.d, "sd", "calls", "etwho.log"))
             and not c.samplers and not c.hosts), ("the manifest exact", c.manifest_ok())]


def common_real(c):
    s = [r for r in c.samplers if r.get("mode") == "sample"]
    e = [r for r in c.samplers if r.get("mode") == "end"]
    return [("one sampler through the guard, ended by SIGTERM", len(s) == 1 and len(e) == 1 and e[0].get("how") == "SIGTERM"),
            ("every host process (%d) under timeout with the card lock held" % len(c.hosts), all(
                h.get("parent") == "timeout" and h.get("lock_held") is True for h in c.hosts)),
            ("session end and the manifest exact", c.has(r" session end \(T0 \d+\)$") and c.manifest_ok()),
            ("no process left", not c.res.get("left"))]


def stopped_by(c, by, pat, card):
    return [("STOP by %s: %s" % (by, pat), bool(c.stop) and c.stop.get("by") == by and re.search(pat, str(c.stop)) is not None),
            ("the summary reads it %s the card" % ("as naming" if card else "as not naming"),
             c.has(r" stop: .*\((names the card)\)$") if card else c.has(r" stop: .*\(does not name the card\)$"))]


def after_stop_none(c):
    """no host process began after the STOP's time (the in-flight one excepted)"""
    if not c.stop:
        return False
    try:
        t = c.stop.get("t_ms") or int(os.stat(os.path.join(c.run, "STOP")).st_mtime * 1000)
    except OSError:
        return False
    late = [m for m in c.marks if m.get("kind") in ("train", "anchor") and m.get("t0_ms", 0) > t + 50]
    return not late


CHECKS = {}


def check(name):
    def deco(fn):
        CHECKS[name] = fn
        return fn
    return deco


def dry(c, plan, calls):
    return [("exit 0", c.rc() == 0), ("LISTING SAME %s, %d device calls" % (plan, calls),
                                     c.has(r"DRY mode: rc 0; LISTING SAME %s: \d+ lines, %d device calls" % (plan, calls))),
            ("the -dry directory and DRY lines", c.sd.endswith("-dry") and c.has(r" DRY session start")),
            ("no stand-in called", not os.path.exists(os.path.join(c.d, "sd", "calls"))), ("the manifest exact", c.manifest_ok())]


check("D1")(lambda ctx, c: dry(c, "full", 429))
check("D2")(lambda ctx, c: dry(c, "short", 331))
check("D3")(lambda ctx, c: dry(c, "ext", 277))


@check("P")
def _p(ctx, c):
    ok, n, m = order_ok(ctx, c, "full")
    s = [r for r in c.samplers if r.get("mode") == "sample"]
    caps = re.search(r"CAP_S (\d+) s", c.log)
    want_secs = str(int(caps.group(1)) + 600) if caps else "?"
    rcode, red = reduce(ctx, c.d, [c.run], "reduce-P")
    units = {t: x.get("units") for t, x in (red or {}).get("trains", {}).items()}
    want_units = {"T2": 9, "T1": 67, "T3": 9, "T5": 26, "T6": 9, "T4": 9, "T8": 9, "T10": 9, "T9": 13, "T11": 9, "T13": 13,
                  "T12": 9, "T15": 9, "T7": 0, "T14": 0}
    ck = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(ctx.kit, "check_e197.py"), "checks", os.path.join(c.d, "reduce-P.json"),
                         "--out", os.path.join(c.d, "checks-P.json")], capture_output=True, text=True)
    return [("exit 0", c.rc() == 0), ("the first card command from step 7 and CAP_S", c.has(r"the first card command at .* \(step 7's"
                                                                                             r" config read") and caps is not None),
            ("the sampler: sample --seconds CAP_S+600 --every-ms 100", bool(s) and s[0]["argv"] == ["sample", "--seconds", want_secs,
                                                                                                    "--every-ms", "100"]),
            ("the runner's smoke gate passed and the kit's smoke check passed", c.has(r"the runner's smoke gate: passed") and
             c.has(r"the kit's smoke check: passed")),
            ("429 host processes in the registered order (desk/dry-e197-full.txt, call for call)", ok and n == 429, (n, m)),
            ("--window 240000000 and --stop-file run/STOP on every host call", all("240000000" in h["argv"] and h["argv"][-1].endswith(
                "/run/STOP") for h in c.hosts)),
            ("SESSION_DONE the reference's own (empty)", os.path.getsize(os.path.join(c.run, "SESSION_DONE")) == 0),
            ("4 blocks complete, stop none, SITTING-RESULT", c.has(r"train blocks started: 4 of 4 \(A B C D\); complete: 4 \(A B C D\)")
             and c.has(r" stop: none$") and c.has(r"SITTING-RESULT: smoke passed; train blocks complete 4 \(A B C D\); card stop none")),
            ("no STOP file", c.stop is None), ("card time logged", c.has(r"card time \d+ s from the first card command \(cap 3000 s\)")),
            ("the registered reducer on the session's files: rc 0, every train's units = processes / 2", rcode == 0 and units == want_units,
             units),
            ("the kit's checker: CHECKS READ", ck.returncode == 0 and "CHECKS READ: " in ck.stdout)] + common_real(c)


@check("P2")
def _p2(ctx, c):
    ok, n, m = order_ok(ctx, c, "ext")
    pd = os.path.join(ctx.s, "P", "tree", "build/e197")
    p1 = [os.path.join(pd, x, "run") for x in sorted(os.listdir(pd)) if not x.endswith("-dry")] if os.path.isdir(pd) else []
    res = []
    if p1:
        rcode, red = reduce(ctx, c.d, [p1[0], c.run], "reduce-pooled")
        tr = (red or {}).get("trains", {})
        res = [("THE POOLED REDUCTION of P and P2: rc 0, T1 67 + 115 = 182 units, T7 and T14 9 units each", rcode == 0 and
                tr.get("T1", {}).get("units") == 182 and tr.get("T7", {}).get("units") == 9 and tr.get("T14", {}).get("units") == 9,
                {t: tr.get(t, {}).get("units") for t in ("T1", "T7", "T14")})]
    else:
        res = [("THE POOLED REDUCTION of P and P2 (P's session present)", False)]
    return [("exit 0", c.rc() == 0), ("277 host processes in the registered order (desk/dry-e197-ext.txt)", ok and n == 277, (n, m)),
            ("block E complete, SITTING-RESULT", c.has(r"train blocks started: 1 of 1 \(E\); complete: 1 \(E\)") and
             c.has(r"SITTING-RESULT: smoke passed; train blocks complete 1 \(E\); card stop none"))] + res + common_real(c)


@check("SH")
def _sh(ctx, c):
    ok, n, m = order_ok(ctx, c, "short")
    return [("exit 0", c.rc() == 0), ("331 host processes in the registered order (desk/dry-e197-short.txt)", ok and n == 331, (n, m)),
            ("4 blocks complete", c.has(r"complete: 4 \(A B C D\)"))] + common_real(c)


@check("S1")
def _s1(ctx, c):
    return [("exit 8", c.rc() == 8), ("blocks: A complete, B begun", c.has(r"train blocks started: 2 of 4 \(A B\); complete: 1 \(A\)")),
            ("no device process began after the STOP", after_stop_none(c)),
            ("SITTING-RESULT card stop none", c.has(r"SITTING-RESULT: smoke passed; train blocks complete 1 \(A\); card stop none"))] + \
        stopped_by(c, "by hand", r".", False) + common_real(c)


@check("K1")
def _k1(ctx, c):
    return [("exit 8", c.rc() == 8), ("the stopwatch did not stop (it stops above 65 W only)", c.stop is not None and c.stop.get("by") != "stopwatch"),
            ("no device process began after the STOP", after_stop_none(c))] + stopped_by(c, "watch_e197", r"board 6[56]\.00 W at or above 65 W", True) + common_real(c)


@check("K2")
def _k2(ctx, c):
    return [("exit 8", c.rc() == 8), ("no device process began after the STOP", after_stop_none(c))] + \
        stopped_by(c, "watch_e197", r"minion clock 500", True) + common_real(c)


@check("K2b")
def _k2b(ctx, c):
    return [("exit 8", c.rc() == 8), ("no clock stop (500 MHz on 2 samples only): the stop is by hand", c.stop is not None and
                                     c.stop.get("by") == "by hand" and not any(e.get("kind") == "stop" and "clock" in str(e.get("why"))
                                                                               for e in c.watch))] + common_real(c)


@check("K3")
def _k3(ctx, c):
    return [("exit 6 or 8", c.rc() in (6, 8)), ("a STOP naming the die", bool(c.stop) and "die reading 70" in str(c.stop.get("why"))),
            ("the summary: names the card", c.has(r" stop: .*\(names the card\)$")), ("SITTING-RESULT card stop yes",
                                                                                     c.has(r"SITTING-RESULT: .*card stop yes"))] + common_real(c)


@check("K4")
def _k4(ctx, c):
    return [("exit 4 or 8", c.rc() in (4, 8)), ("a STOP naming the telemetry", bool(c.stop) and re.search(r"telemetry|sample", str(c.stop.get("why")))),
            ("the summary: names the card", c.has(r" stop: .*\(names the card\)$"))] + common_real(c)


def smoke_gate_stop(c, by_watch):
    blkA = [h for h in c.hosts if h["proc"] > 5]
    r = [("GATE-STOP (no block began), with a device opened", c.has(r" GATE-STOP: no block of trains\.tsv began") and
          not c.has(r"no device opened by the session")), ("no host process after the smoke's five", not blkA),
         ("SITTING-RESULT smoke failed", c.has(r"SITTING-RESULT: smoke failed; train blocks complete 0"))]
    if by_watch:
        r += [("exit 8", c.rc() == 8), ("the runner's smoke gate passed", c.has(r"the runner's smoke gate: passed")),
              ("the kit's smoke check FAILED", c.has(r"the kit's smoke check: FAILED"))] + stopped_by(c, "watch_e197", r"smoke check", True)
    else:
        r += [("exit 7", c.rc() == 7), ("the runner's smoke gate failed", c.has(r"the runner's smoke gate: failed"))]
    return r + common_real(c)


check("G1")(lambda ctx, c: smoke_gate_stop(c, True) + [("the reason: participants [1023]", "participants [1023]" in c.log)])
check("G2")(lambda ctx, c: smoke_gate_stop(c, True) + [("the reason: an anchor's exit 1", "exit 1" in c.log)])
check("G3")(lambda ctx, c: smoke_gate_stop(c, False))
check("SP1")(lambda ctx, c: smoke_gate_stop(c, False) + [
    ("the split launch dropped: 25 of the smoke's 26 train launches recorded",
     sum(1 for r in c.runs if r.get("train") == "smoke") == 25 and '"launches": 25' in open(os.path.join(c.run, "marks.jsonl")).read())])


@check("SP2")
def _sp2(ctx, c):
    return [("the smoke passed with a runtime line between two host lines: 26 train launches", c.has(r"the runner's smoke gate: passed \(26 launches")
             and sum(1 for r in c.runs if r.get("train") == "smoke") == 26), ("the kit's smoke check passed", c.has(r"the kit's smoke check: passed")),
            ("ended by hand: exit 8", c.rc() == 8)] + common_real(c)


check("H1")(lambda ctx, c: gate_nodev(c) + [("the reason: et-who", c.has(r"the card is not free: et-who --check exit 1"))])
check("H2")(lambda ctx, c: gate_nodev(c) + [("the reason: another user's process", c.has(r"device process\(es\) of another user"))])
check("H3")(lambda ctx, c: gate_nodev(c) + [("the reason: the lock", c.has(r"the card lock is held"))])


@check("H4")
def _h4(ctx, c):
    return [("exit 3", c.rc() == 3), ("block A complete, B not begun", c.has(r"train blocks started: 1 of 4 \(A\); complete: 1 \(A\)")),
            ("run_session.sh: block B not free", "block B: the card is not free, stopping" in open(os.path.join(c.run, "session.log")).read()),
            ("SITTING-RESULT card stop none", c.has(r"SITTING-RESULT: smoke passed; train blocks complete 1 \(A\); card stop none"))] + common_real(c)


@check("L1")
def _l1(ctx, c):
    s = [r for r in c.samplers if r.get("mode") == "end"]
    return [("exit 75", c.rc() == 75), ("GATE-STOP with a device opened", c.has(r" GATE-STOP: no block") and not c.has(r"no device opened")),
            ("no host started", not c.hosts), ("the sampler ended by SIGTERM", bool(s) and s[0].get("how") == "SIGTERM"),
            ("no process left", not c.res.get("left")), ("the manifest exact", c.manifest_ok())]


@check("X1")
def _x1(ctx, c):
    return [("exit 9", c.rc() == 9), ("the trains ended without a registered stop", c.has(r" the trains ended without a registered stop: run_session.sh rc 1")),
            ("block A began", c.has(r"train blocks started: 1 of 4 \(A\)")), ("no STOP file", c.stop is None)] + common_real(c)


@check("HG")
def _hg(ctx, c):
    hung = [h for h in jl(os.path.join(c.d, "sd", "calls", "host.log")) if h.get("signal") == 15]
    ended = [h for h in c.hosts if h.get("proc") == 6]
    return [("exit 8", c.rc() == 8), ("the HUNG line in the session log", c.has(r" HUNG: a device process \(pid \d+\) still runs")),
            ("the host was sent TERM by its timeout, logged it, and ended by itself (no KILL)", bool(hung) and bool(ended) and
             ended[0].get("rc") == 0),
            ("the watch's hang event", any(e.get("kind") == "stop" and "still runs" in str(e.get("why")) for e in c.watch))] + \
        stopped_by(c, "watch_e197", r"still runs", True) + common_real(c)


@check("T1")
def _t1(ctx, c):
    return [("exit 8", c.rc() == 8), ("the wrapper logged the signal", c.has(r" signal: STOP written; waiting for the session to end"))] + \
        stopped_by(c, "session_e197", r"a signal to the wrapper", False) + common_real(c)


@check("W1")
def _w1(ctx, c):
    return [("exit 8", c.rc() == 8), ("the wrapper logged the watch gone", c.has(r"the kit's watch is gone: STOP written"))] + \
        stopped_by(c, "session_e197", r"the kit's watch is gone", False) + common_real(c)


@check("C1")
def _c1(ctx, c):
    first = int(c.res.get("first") or 0)
    e = [r for r in c.samplers if r.get("mode") == "end"]
    rs = open(os.path.join(c.run, "session.log")).read() if os.path.exists(os.path.join(c.run, "session.log")) else ""
    return [("exit 0", c.rc() == 0), ("trains skipped by the deadline", any(m.get("kind") == "skipped" for m in c.marks)),
            ("the cap reached before a later block", "cap reached before block" in rs),
            ("the sampler stopped inside the cap (first card command + 370 s)", bool(e) and e[0]["t_ms"] / 1000.0 <= first + 370),
            ("a train ran before the deadline (T2)", any(m.get("kind") == "train" and m.get("train") == "T2" for m in c.marks)),
            ("no STOP", c.stop is None)] + common_real(c)


def rs_log(c):
    try:
        return open(os.path.join(c.run, "session.log")).read()
    except OSError:
        return ""


def wrapper_done(c):
    try:
        j = json.loads(open(os.path.join(c.run, "SESSION_DONE")).read())
        return j.get("by") == "session_e197"
    except (OSError, ValueError):
        return False


@check("B7")
def _b7(ctx, c):
    return gate_nodev(c) + [("run_session.sh's own free check: not free, nothing opened", "the card is not free: nothing opened" in rs_log(c)),
                            ("SESSION_DONE written by the wrapper (run_session.sh exited before its EXIT trap)", wrapper_done(c))]


@check("B7p")
def _b7p(ctx, c):
    return gate_nodev(c) + [("run_session.sh's own free check: another user's device process", "another user's device process" in rs_log(c)),
                            ("SESSION_DONE written by the wrapper", wrapper_done(c))]


@check("B7l")
def _b7l(ctx, c):
    return gate_nodev(c) + [("run_session.sh's own lock probe: held", "held by another process" in rs_log(c)),
                            ("SESSION_DONE written by the wrapper", wrapper_done(c))]


@check("B8")
def _b8(ctx, c):
    s = [r for r in c.samplers if r.get("mode") == "end"]
    return [("exit 3", c.rc() == 3), ("free_with_sampler: not free after the sampler started", "the card is not free after the sampler started" in rs_log(c)),
            ("GATE-STOP with a device opened", c.has(r" GATE-STOP: no block") and not c.has(r"no device opened")), ("no host started", not c.hosts),
            ("the sampler ended by SIGTERM", bool(s) and s[0].get("how") == "SIGTERM"), ("no process left", not c.res.get("left")),
            ("the manifest exact", c.manifest_ok())]


def tel_stop(c, rc, pat):
    return [("exit %d" % rc, c.rc() == rc), ("STOP by run_trains: %s" % pat, bool(c.stop) and c.stop.get("by") == "run_trains" and pat in str(c.stop.get("why"))),
            ("the summary: names the card", c.has(r" stop: .*\(names the card\)$"))] + common_real(c)


check("B9")(lambda ctx, c: tel_stop(c, 4, "no telemetry line") + [("GATE-STOP (no block began)", c.has(r" GATE-STOP: no block"))])
check("NT")(lambda ctx, c: tel_stop(c, 4, "without temp_c.minshire"))


@check("T2")
def _t2(ctx, c):
    return [("exit 143 (run_session.sh's own signal trap)", c.rc() == 143), ("a registered end, not a crash", not c.has(r"without a registered stop"))] + \
        stopped_by(c, "run_session", r"signal 15", False) + common_real(c)


@check("S2")
def _s2(ctx, c):
    return [("exit 8", c.rc() == 8), ("block A complete, B not begun", c.has(r"train blocks started: 1 of 4 \(A\); complete: 1 \(A\)")),
            ("run_session.sh read the STOP after the gap", "STOP: " in rs_log(c))] + stopped_by(c, "by hand", r".", False) + common_real(c)


@check("HG2")
def _hg2(ctx, c):
    sig = [h for h in jl(os.path.join(c.d, "sd", "calls", "host.log")) if h.get("signal") == 15]
    return [("exit 5", c.rc() == 5), ("the host got its timeout's TERM, logged it, and ended by itself", bool(sig)),
            ("no HUNG line (it ended before 12 s)", not c.has(r" HUNG: "))] + stopped_by(c, "run_trains", r"killed by its timeout", True) + common_real(c)


check("F2")(lambda ctx, c: [("exit 5", c.rc() == 5)] + stopped_by(c, "run_trains", r"two failed device processes in a row", True) + common_real(c))
check("G4")(lambda ctx, c: smoke_gate_stop(c, False) + [("the gate's rates: rate_max over rate_min above 1.03", any(
    m.get("kind") == "smoke_gate" and m.get("rate_max") and m["rate_max"] / m["rate_min"] > 1.03 for m in c.marks))])
check("G5")(lambda ctx, c: smoke_gate_stop(c, False))
check("K5")(lambda ctx, c: [("exit 8", c.rc() == 8), ("a board STOP by the stopwatch or the watch", bool(c.stop) and c.stop.get("by") in (
    "stopwatch", "watch_e197") and "board" in str(c.stop.get("why"))), ("the summary: names the card", c.has(r" stop: .*\(names the card\)$"))] + common_real(c))


def alone(c, text):
    return [("run_session.sh alone: exit 2", c.rc() == 2), ("its refusal: %s" % text, text in c.log),
            ("no et-who, no sampler, no host called", not os.path.exists(os.path.join(c.d, "sd", "calls")))]


check("A0")(lambda ctx, c: alone(c, "refused: no /dev/et*_ops node on this host"))
check("A1")(lambda ctx, c: alone(c, "refused: ET_DEVICES must be one card index"))
check("A2")(lambda ctx, c: alone(c, "refused: no /dev/et1_ops"))
check("A3")(lambda ctx, c: alone(c, "refused: 2 cards on this host and ET_DEVICES unset"))
check("A4")(lambda ctx, c: alone(c, "refused: no card lock file"))


for _n in ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "TWO", "NONE", "OPS", "R13"):
    check(_n)(lambda ctx, c: refused(c))
check("R10")(lambda ctx, c: refused(c) + [("the reason: no card lock file", c.has(r"no card lock file"))])
check("R7b")(lambda ctx, c: refused(c) + [("the reason: the first card command more than 120 s back", c.has(r"more than 120 s"))])


def we_case(ctx):
    """the watch's end-stop alone, on a scratch OUT (no session): its STOP, then SESSION_DONE ends it"""
    d = os.path.join(ctx.s, "WE")
    out = os.path.join(d, "out")
    os.makedirs(out)
    now = time.time()
    p = subprocess.Popen(["/usr/bin/python3", "-I", "-B", os.path.join(ctx.kit, "watch_e197.py"), out, "--first", str(int(now) - 200),
                          "--cap", "220", "--host", "build/none/regfile_host", "--log-dir", d, "--session-log", os.path.join(d, "s.log")],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = time.time()
    while not os.path.exists(os.path.join(out, "STOP")) and time.time() - t < 5:
        time.sleep(0.05)
    dt = time.time() - t
    st = json.loads(open(os.path.join(out, "STOP")).read()) if os.path.exists(os.path.join(out, "STOP")) else {}
    open(os.path.join(out, "SESSION_DONE"), "w").close()
    try:
        rc = p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.terminate()
        rc = None
    return [("the end-stop's STOP within 2 s", dt < 2.0 and st.get("by") == "watch_e197" and "the end-stop" in st.get("why", ""), round(dt, 2)),
            ("not naming the card", st.get("card") is False), ("SESSION_DONE ends the watch (rc 0)", rc == 0)]


AUDIT_FILES = {"session_e197.sh": (E + "/session_e197.sh", r"DRYRUN|DRY=1"), "proposal/src/run_session.sh":
               (E + "/proposal/src/run_session.sh", r"DRY"), "lab/run_trains.py": (E + "/lab/run_trains.py", r"a\.dry")}


def audit(ctx, results, complete):
    """THE AUDIT: desk/dry-branches-e197.tsv against the files' own lines; every case it names passed in this run."""
    rows = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(ctx.kit, "desk", "dry-branches-e197.tsv"))][1:]
    out, bad = [], []
    have = {}
    for r in rows:
        if len(r) != 6:
            bad.append("a row of %d fields" % len(r))
            continue
        f, n, txt, _dry, _real, cs = r
        lines = open(os.path.join(ctx.src, AUDIT_FILES[f][0])).read().split("\n")
        if lines[int(n) - 1].strip() != txt:
            bad.append("%s:%s's text differs from the row" % (f, n))
        have[(f, int(n))] = cs.split()
    for f, (path, pat) in AUDIT_FILES.items():
        for i, ln in enumerate(open(os.path.join(ctx.src, path)).read().split("\n"), 1):
            if re.search(pat, ln) and not ln.strip().startswith("#") and (f, i) not in have:
                bad.append("%s:%d branches on the dry mode and has no row" % (f, i))
    named = sorted({c for cs in have.values() for c in cs})
    if complete:
        notok = [c for c in named if results.get(c) is not True]
        if notok:
            bad.append("named cases that did not pass in this run: " + " ".join(notok))
    out.append(("the audit table's %d rows read the files' own lines, and every dry-branching line has a row" % len(rows),
                not [b for b in bad if "named cases" not in b], bad[:6]))
    out.append(("every case the audit names (%d) passed in this run" % len(named), complete and not [b for b in bad if "named cases" in b],
                "a subset run: not checked" if not complete else bad[-1:]))
    return out


def cases(ctx):
    raw = open(os.path.join(ctx.src, E191_STDOUT), "rb").read()
    i = raw.index(b"Opening device")
    j = raw.index(b"\n", i) + 1
    runtime = raw[i:j].decode()
    fast = {"launch_s": 0.02}
    C = {
        "P": {"scenario": fast, "timeout": 1500},
        "P2": {"scenario": fast, "env": {"E197_SIT": "2", "E197_PLAN": "ext"}, "timeout": 900},
        "SH": {"scenario": fast, "env": {"E197_PLAN": "short"}, "timeout": 1200},
        "D1": {"args": ["--dry"], "env": {}},
        "D2": {"args": ["--dry"], "env": {"E197_PLAN": "short"}},
        "D3": {"args": ["--dry"], "env": {"E197_SIT": "2", "E197_PLAN": "ext"}},
        "S1": {"scenario": fast, "actions": [{"when": {"train_mark": "T3"}, "do": "touch_stop"}]},
        "K1": {"scenario": dict(fast, board_w_from={"t": 50, "w": [65.0, 66.0]})},
        "K2": {"scenario": dict(fast, mhz_from={"t": 50, "mhz": 500, "n": 30})},
        "K2b": {"scenario": dict(fast, mhz_from={"t": 50, "mhz": 500, "n": 2}), "actions": [{"when": {"train_mark": "T1"}, "do": "touch_stop"}]},
        "K3": {"scenario": dict(fast, die_from={"t": 50, "c": 70})},
        "K4": {"scenario": dict(fast, quiet_after_s=50)},
        "G1": {"scenario": dict(fast, participants_bad={"proc": 1, "value": 1023})},
        "G2": {"scenario": dict(fast, host_rc={"proc": 2, "rc": 1})},
        "G3": {"scenario": dict(fast, check_bad_proc=4)},
        "SP1": {"scenario": dict(fast, split_proc={"proc": 4, "launch": 5, "runtime": runtime, "at": 200})},
        "SP2": {"scenario": dict(fast, between_proc={"proc": 4, "runtime": runtime}),
                "actions": [{"when": {"block_train": "A"}, "do": "touch_stop"}]},
        "H1": {"scenario": dict(fast, foreign_holder={"from_call": 1})},
        "H2": {"scenario": dict(fast, foreign_proc={"from_call": 1})},
        "H3": {"scenario": fast, "lock_at_start": 120},
        "H4": {"scenario": dict(fast, foreign_holder={"from_call": 5})},
        "L1": {"scenario": fast, "actions": [{"when": {"sampler_s": 3}, "do": "take_lock", "seconds": 120}]},
        "X1": {"scenario": dict(fast, notdict_proc=7)},
        "HG": {"scenario": dict(fast, hang_proc={"proc": 6, "live_s": 14})},
        "T1": {"scenario": fast, "actions": [{"when": {"block_train": "A"}, "do": "term_wrapper"}]},
        "W1": {"scenario": fast, "actions": [{"when": {"block_train": "A"}, "do": "kill_watch"}]},
        "C1": {"scenario": fast, "env": {"E197_DESKTEST": "1", "E197_CAP_S": "370", "E197_FIRST": "@NOW-5"}},
        "R1": {"scenario": fast, "env": {"E197_CAP_S": "300"}},
        "R2": {"scenario": fast, "env": {"E197_HARNESS_SHA256": "0" * 64}},
        "R3": {"scenario": fast, "tamper": {E + "/proposal/src/run_session.sh": "\n"}},
        "R4": {"scenario": fast, "built_yesterday": True},
        "R5": {"scenario": fast, "built_host_wrong": True},
        "R6": {"scenario": fast, "env": {"USER": "nobody-else"}},
        "R7": {"scenario": fast, "env": {"E197_FIRST": "@NOW-700"}},
        "R7b": {"scenario": fast, "env": {"E197_FIRST": "@NOW-300"}},
        "R8": {"scenario": fast, "env": {"E197_FIRST": "@NOW+100"}},
        "R9": {"scenario": fast, "env": {"E197_LAST_END_EPOCH": "@NOW+600"}},
        "R10": {"scenario": fast, "lockfile": False},
        "TWO": {"scenario": fast, "nodes": ["et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt"]},
        "NONE": {"scenario": fast, "nodes": ["et0_mgmt"]},
        "OPS": {"scenario": fast, "nodes": ["et0_ops"]},
        "R13": {"scenario": fast, "hostname": "aifoundry1"},
        "B7": {"scenario": dict(fast, foreign_holder={"from_call": 2})},
        "B7p": {"scenario": dict(fast, foreign_proc={"from_call": 2})},
        "B7l": {"scenario": dict(fast, lock_on_etwho_call=2)},
        "B8": {"scenario": dict(fast, foreign_holder={"from_call": 3})},
        "B9": {"scenario": dict(fast, quiet_after_s=0)},
        "NT": {"scenario": dict(fast, no_temp_after_s=50)},
        "T2": {"scenario": fast, "actions": [{"when": {"block_train": "A"}, "do": "term_run_session"}]},
        "S2": {"scenario": fast, "actions": [{"when": {"block_after": "A"}, "do": "touch_stop"}]},
        "HG2": {"scenario": dict(fast, hang_proc={"proc": 6, "live_s": 11.5})},
        "F2": {"scenario": dict(fast, host_rc={"procs": [6, 7], "rc": 1})},
        "G4": {"scenario": dict(fast, rate_jitter={"proc": 5, "factor": 1.05})},
        "G5": {"scenario": dict(fast, bad_letters_proc=4)},
        "K5": {"scenario": dict(fast, board_w_from={"t": 50, "w": [66.0, 67.0]})},
        "A0": {"alone": True, "scenario": fast, "nodes": ["et0_mgmt"]},
        "A1": {"alone": True, "scenario": fast, "env": {"ET_DEVICES": "x"}},
        "A2": {"alone": True, "scenario": fast, "env": {"ET_DEVICES": "1"}},
        "A3": {"alone": True, "scenario": fast, "nodes": ["et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt"]},
        "A4": {"alone": True, "scenario": fast, "lockfile": False},
    }
    return C


def main(argv):
    if argv[:1] == ["--inner"]:
        return inner(argv[1])
    src, s = argv[0], argv[1]
    only = argv[2:]
    ctx = Ctx(src, s)
    print("E197 real-path desk test, %s; the lab clone %s at HEAD %s; python %s" % (
        time.strftime("%F %T %Z"), "<lab clone>", subprocess.run(["git", "-C", src, "rev-parse", "--short=12", "HEAD"], capture_output=True,
                                                                text=True).stdout.strip(), sys.version.split()[0]), flush=True)
    s191 = sha(os.path.join(src, E191_STDOUT))
    pin = [ln.split()[0] for ln in open(os.path.join(src, E191_SUMS)) if ln.rstrip().endswith("session/smoke/copy-64m-random/stdout.txt")]
    print("E191's committed smoke stdout (1a4bc1e3): sha256 %s, %s its data directory's SHA256SUMS" % (
        s191[:16], "AT" if pin and pin[0] == s191 else "NOT AT"), flush=True)
    C = cases(ctx)
    names = [n for n in C if not only or n in only]
    if "WE" in only or not only:
        names_we = True
    else:
        names_we = False
    # the order: the long whole sittings first, then the rest; P2's pooled reduction reads P's session (P2 waits for P)
    first = [n for n in ("P", "SH") if n in names]
    rest = [n for n in names if n not in ("P", "SH", "P2")]
    total = passed = 0
    lines = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run, ctx, n, C[n]): n for n in first + rest}
        pfut = None
        done = {}
        for f in concurrent.futures.as_completed(list(futs)):
            n, d, dt = f.result()
            done[n] = (d, dt)
            if n == "P" and "P2" in names:
                pfut = ex.submit(run, ctx, "P2", C["P2"])
        if "P2" in names and pfut is None:
            pfut = ex.submit(run, ctx, "P2", C["P2"])
        if pfut:
            n, d, dt = pfut.result()
            done[n] = (d, dt)
    results = {}
    for n in names:
        d, dt = done[n]
        c = Case(d)
        try:
            rows = CHECKS[n](ctx, c)
        except Exception as e:  # a check that cannot read its case fails, never passes
            rows = [("the case's files could be read (%s)" % type(e).__name__, False, str(e)[:200])]
        ok = all(r[1] for r in rows)
        results[n] = ok
        print("\n== %s (%.0f s, wrapper exit %s): %s" % (n, dt, c.rc(), "PASS" if ok else "FAIL"), flush=True)
        for r in rows:
            total += 1
            passed += 1 if r[1] else 0
            print("   %s %s%s" % ("ok  " if r[1] else "FAIL", r[0], ("  " + json.dumps(r[2])[:300]) if len(r) > 2 and not r[1] else ""))
        for ln in re.findall(r"^\S+ \S+ \S+ (?:GATE-STOP|stop|SITTING-RESULT|HUNG|the trains ended|refused).*$", c.log, re.M)[:4]:
            print("   | " + ln[:220])
    if names_we:
        rows = we_case(ctx)
        ok = all(r[1] for r in rows)
        print("\n== WE (the watch's end-stop alone): %s" % ("PASS" if ok else "FAIL"))
        for r in rows:
            total += 1
            passed += 1 if r[1] else 0
            print("   %s %s%s" % ("ok  " if r[1] else "FAIL", r[0], ("  " + json.dumps(r[2])) if len(r) > 2 and not r[1] else ""))
    rows = audit(ctx, results, not only)
    print("\n== AUDIT (desk/dry-branches-e197.tsv): %s" % ("PASS" if all(r[1] for r in rows) else "FAIL"))
    for r in rows:
        total += 1
        passed += 1 if r[1] else 0
        print("   %s %s%s" % ("ok  " if r[1] else "FAIL", r[0], ("  " + json.dumps(r[2])[:400]) if not r[1] else ""))
    devs = [x for x in os.listdir("/dev") if x.startswith("et")]
    total += 1
    zok = not devs
    passed += 1 if zok else 0
    print("\n== Z: outside the cases, /dev/et* holds %d entries; %s" % (len(devs), "ok" if zok else "FAIL"))
    print("\nDESKTEST-REALPATH-E197 %d of %d %s" % (passed, total, "PASS" if passed == total else "FAIL"))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
