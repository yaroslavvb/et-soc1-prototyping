#!/usr/bin/env python3
"""E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE REAL-PATH DESK TEST's cases (run by
desk/desktest_realpath_e196.sh inside its sandbox; never run it outside one). E192's form (tools/claims-v3/e192/desk/realpath_e192.py):
it builds a stand-in aifoundry3 tree in the scratch directory (E196's root R = <tree>/build/claims-v3/aifoundry3/e196 holding
boxfiles-e196.txt's files as the sync puts them; both hosts and the box's sampler as stand-ins at their real paths; today's build record),
then runs session_e196.sh's REAL path (DRY unset) case by case, with actions a person or the card could take mid-session (a stop by hand,
the card lock taken, a holder, a crash, a signal), and reads what it wrote. Nothing here opens a device; nothing is measured. Each case's
numbers are the stand-ins' (desk/standin_e196.py), never the card's. The cases are listed in main() and in the log.
    /usr/bin/python3 -I -B realpath_e196.py <repo top> <scratch dir>
SPDX-License-Identifier: Apache-2.0
"""
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

SRC, S = sys.argv[1], sys.argv[2]
E = "tools/claims-v3/e196"
STANDIN = os.path.join(SRC, E, "desk/standin_e196.py")
BOX = os.path.join(S, "box")
TREE = os.path.join(BOX, "aifoundry")
RR = "build/claims-v3/aifoundry3/e196"
R = os.path.join(TREE, RR)
SBIN = os.path.join(S, "sbin")
LOCK = "/run/lock/etsoc-shire0.lock"
ME = pwd.getpwuid(os.getuid()).pw_name
PY = "/usr/bin/python3"
TEXT = "8798e43c4869a124690bc652d574d5ab78d686faa70293cbcff658d24c30a399"
QUIET = os.environ.get("E196_QUIET_FLAG", "")   # the round's quiet-desk flag file, given by the caller (none: no wait)
npass = ncase = 0
fails = []
_last_t0 = [0]
results = {}


CURRENT = ["0"]


def ok(cond, label, detail=""):
    global npass, ncase
    ncase += 1
    results.setdefault(CURRENT[0], []).append(bool(cond))
    if cond:
        npass += 1
        print("-> PASS (%s)" % label, flush=True)
    else:
        fails.append(label)
        print("-> FAIL (%s%s)" % (label, (": " + str(detail)[:400]) if detail else ""), flush=True)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


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


def text(p):
    try:
        return open(p, errors="replace").read()
    except OSError:
        return ""


def shim(path, role):
    """a stand-in at a real path: a POSIX sh script that execs the stand-in at once (its name is the real one only until that exec)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("#!/bin/sh\nexec %s -I -B %s %s \"$@\"\n" % (PY, STANDIN, role))
    os.chmod(path, 0o755)


def write_build_record():
    p = os.path.join(R, "build", "BUILD-E196.txt")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lh = sha(os.path.join(R, "build/sparsity-lab/host/sparsity_host"))
    xh = sha(os.path.join(R, "build/x14/host/x14_host"))
    with open(p, "w") as f:
        f.write("built %s on aifoundry3 (desk test stand-in record)\nlab_host_sha256 %s\nx14_host_sha256 %s\n"
                "kernel_elf_sha256_lab %s\nkernel_elf_sha256_x14 %s\nkernel_text_sha256_lab %s\nkernel_text_sha256_x14 %s\n"
                "E196-BUILT rc=0 lab %s x14 %s text %s\n" % (time.strftime("%F %T %Z"), lh, xh, "0" * 64, "0" * 64, TEXT, TEXT,
                                                           lh[:12], xh[:12], TEXT[:12]))


def setup():
    os.makedirs(R, exist_ok=True)
    files = [ln.strip() for ln in open(os.path.join(SRC, E, "boxfiles-e196.txt")) if ln.strip() and not ln.startswith("#")]
    for p in files:
        if p.endswith("SHA256SUMS-e196-kit") and not os.path.exists(os.path.join(SRC, p)):
            continue
        os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
        shutil.copy2(os.path.join(SRC, p), os.path.join(R, p))
    # the kit's list: a stand-in made here from R's copies (the real list holds this test's own log); the session reads its sha256
    kl = os.path.join(R, E, "SHA256SUMS-e196-kit")
    reg = {ln.split()[1] for ln in open(os.path.join(R, E, "SHA256SUMS-e196-registration")) if ln.strip()}
    rows = []
    for root, _, fs in os.walk(os.path.join(R, E)):
        for fn in fs:
            p = os.path.relpath(os.path.join(root, fn), R)
            if p in reg or p.endswith("SHA256SUMS-e196-kit") or p.endswith("SHA256SUMS-e196-registration"):
                continue
            rows.append("%s  %s" % (sha(os.path.join(R, p)), p))
    with open(kl, "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x.split("  ")[1])) + "\n")
    shim(os.path.join(TREE, "build/ettelem/ettelem"), "sampler")
    shim(os.path.join(R, "build/sparsity-lab/host/sparsity_host"), "lab")
    shim(os.path.join(R, "build/x14/host/x14_host"), "x14")
    write_build_record()
    shim(os.path.join(SBIN, "et-who"), "etwho")
    shim(os.path.join(SBIN, "ps"), "ps")
    for t in ("ssh", "rsync", "scp"):
        with open(os.path.join(SBIN, t), "w") as f:
            f.write("#!/bin/sh\necho \"%s $*\" >> %s/network-calls.log\necho 'STAND-IN: no network in this test' >&2\nexit 97\n" % (t, S))
        os.chmod(os.path.join(SBIN, t), 0o755)
    return sha(kl)


def new_t0():
    t = max(int(time.time()), _last_t0[0] + 1)
    _last_t0[0] = t
    return t


def base_env(sd, extra):
    env = {"PATH": SBIN + ":/usr/local/bin:/usr/bin:/bin", "HOME": BOX, "USER": ME, "LOGNAME": ME, "LANG": "C.UTF-8",
           "TZ": "America/Los_Angeles", "E196_STANDIN_DIR": sd, "E196_KITLIST_SHA256": KLS,
           "E196_DEADLINE_EPOCH": str(int(time.time()) + 7200)}
    for k, v in extra.items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    return env


class Run:
    pass


def wait_quiet():
    """the round's QUIET DESK FLAG: no stand-in host or sampler starts while a card session of ours runs on this box's own card"""
    t = time.time()
    while QUIET and os.path.exists(QUIET) and time.time() - t < 3600:
        time.sleep(15)


def run_case(name, scen=None, env=None, actions=(), timeout=400, dry=False, wrap=None, lock=True):
    print("\n== %s" % name, flush=True)
    CURRENT[0] = name.split("-")[0]
    wait_quiet()
    t0 = new_t0()
    sd = os.path.join(S, "sd", name)
    os.makedirs(sd, exist_ok=True)
    json.dump(scen or {}, open(os.path.join(sd, "scenario.json"), "w"))
    for fn in os.listdir(sd):
        if fn.startswith("count-"):
            os.unlink(os.path.join(sd, fn))
    if lock:
        open(LOCK, "a").close()
    elif os.path.exists(LOCK):
        os.unlink(LOCK)
    r = Run()
    r.name, r.t0, r.sd = name, t0, sd
    r.outd = os.path.join(TREE, "build/e196/T%d%s" % (t0, "-dry" if dry else ""))
    rundir = os.path.join(r.outd, "run")
    open(os.path.join(sd, "rundir"), "w").write(rundir + "\n")
    e = base_env(sd, dict(env or {}, E196_T0=str(t0)))
    cmd = ["bash", os.path.join(R, E, "session_e196.sh")] + (["--dry"] if dry else [])
    if wrap:
        cmd = wrap + cmd
    out = open(os.path.join(S, "case-%s.out" % name), "w")
    r.start = time.time()
    p = subprocess.Popen(cmd, cwd=S, env=e, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
    r.pid = p.pid
    pending = list(actions)
    timed_out = False
    while p.poll() is None:
        for a in list(pending):
            try:
                if a(r):
                    pending.remove(a)
            except Exception as ex:
                print("   (action %s: %s)" % (getattr(a, "__name__", "?"), ex), flush=True)
        if time.time() - r.start > timeout and not timed_out:
            timed_out = True
            print("   TIMEOUT at %d s: STOP written by the test" % timeout, flush=True)
            write_stop(r, "desk test: the case's own bound")
        if timed_out and time.time() - r.start > timeout + 90:
            os.killpg(p.pid, signal.SIGTERM)
        time.sleep(0.2)
    r.rc = p.returncode
    r.elapsed = time.time() - r.start
    r.timed_out = timed_out
    out.close()
    r.out = text(os.path.join(S, "case-%s.out" % name))
    r.log = text(os.path.join(r.outd, "session.log"))
    r.rlog = text(os.path.join(rundir, "session.log"))
    r.marks = jl(os.path.join(rundir, "marks.jsonl"))
    r.runs = jl(os.path.join(rundir, "runs.jsonl"))
    r.trecs = jl(os.path.join(rundir, "train.jsonl"))
    r.checks = jl(os.path.join(rundir, "checks.jsonl"))
    st = jl(os.path.join(rundir, "STOP"))
    r.stop = st[0] if st else None
    r.src = text(os.path.join(r.outd, "session.rc")).strip()
    r.calls = {}
    cd = os.path.join(sd, "calls")
    if os.path.isdir(cd):
        for fn in os.listdir(cd):
            r.calls[fn[:-4]] = jl(os.path.join(cd, fn))
    print("   rc %s (session.rc %s) in %.1f s; calls %s; stop %s" % (r.rc, r.src, r.elapsed, {k: len(v) for k, v in r.calls.items()},
          (r.stop or {}).get("why", "-")[:160]), flush=True)
    for ln in r.log.splitlines()[-7:]:
        print("   | " + ln[:230], flush=True)
    return r


def write_stop(r, why):
    rd = os.path.join(r.outd, "run")
    if os.path.isdir(rd) and not os.path.exists(os.path.join(rd, "STOP")):
        with open(os.path.join(rd, "STOP"), "w") as f:
            f.write(json.dumps({"by": "hand", "why": why, "t_ms": int(time.time() * 1000)}) + "\n")


def manifest_ok(r):
    mf = os.path.join(r.outd, "MANIFEST.sha256")
    if not os.path.exists(mf):
        return False, "no MANIFEST.sha256"
    listed = {}
    for ln in open(mf):
        h, p = ln.rstrip("\n").split("  ", 1)
        listed[os.path.normpath(p)] = h
    have = set()
    for root, _, fs in os.walk(r.outd):
        for fn in fs:
            rel = os.path.normpath(os.path.relpath(os.path.join(root, fn), r.outd))
            if rel in ("MANIFEST.sha256", "session.rc"):
                continue
            have.add(rel)
    bad = [p for p in listed if p not in have or sha(os.path.join(r.outd, p)) != listed[p]]
    extra = sorted(have - set(listed))
    return (not bad and not extra), "bad %s extra %s" % (bad[:3], extra[:3])


def block_after(r, b):
    return any(m.get("kind") == "idle" and m.get("label") == "after" and m.get("pass") == b
               for m in jl(os.path.join(r.outd, "run", "marks.jsonl")))


def smoke_gate_mark(r):
    return [m for m in jl(os.path.join(r.outd, "run", "marks.jsonl")) if m.get("kind") == "smoke_gate"]


def count(r, name):
    try:
        return int(open(os.path.join(r.sd, "count-" + name)).read().strip() or 0)
    except OSError:
        return 0


def order(fn):
    o = {}
    for ln in open(os.path.join(SRC, E, "desk", fn)):
        if ln.startswith("pass "):
            head, rest = ln.split(":", 1)
            o[int(head.split()[1])] = [w.split("(")[0] for w in rest.split()]
    return o


def runs_by_seq(r, p):
    seqs = {}
    for x in r.runs:
        if x.get("pass") == p:
            seqs.setdefault(x["seq"], []).append(x)
    return [seqs[k] for k in sorted(seqs)]


def device_calls(r, role):
    return [c for c in r.calls.get(role, []) if c.get("event") == "call"]


def no_device_after(r, t_ms):
    late = [c for role in ("lab", "x14") for c in device_calls(r, role) if c.get("t0", 0) * 1000 > t_ms + 50]
    return not late, late[:2]


def hold_lock(seconds):
    flag = os.path.join(S, "holder.flag")
    if os.path.exists(flag):
        os.unlink(flag)
    code = ("import fcntl, os, time\nfd = os.open(%r, os.O_RDONLY)\nfcntl.flock(fd, fcntl.LOCK_EX)\nopen(%r, 'w').write('held')\n"
            "time.sleep(%d)\n") % (LOCK, flag, seconds)
    f = os.path.join(S, "holder.py")
    open(f, "w").write(code)
    p = subprocess.Popen([PY, "-I", "-B", f], start_new_session=True)
    t = time.time()
    while not os.path.exists(flag) and time.time() - t < 10:
        time.sleep(0.05)
    return p


def end_hold(p):
    p.terminate()
    p.wait()
    flag = os.path.join(S, "holder.flag")
    if os.path.exists(flag):
        os.unlink(flag)


def s20_patterns():
    src = text(os.path.join(SRC, E, "rb/s20_wait_e196.sh"))
    g = re.search(r"grep -qE '([^']+)' \"\$L\" 2>/dev/null; then echo \"GATE-STOPPED", src)
    c = re.search(r"grep -qE '([^']+)' \"\$L\" 2>/dev/null; then echo \"MAIN-CRASHED", src)
    n = re.search(r"pgrep -u \"\$\(id -u\)\" -f '([^']+)'", src)
    return (g.group(1) if g else None, c.group(1) if c else None, n.group(1) if n else None)


def s20_reading(r):
    g, c, _ = s20_patterns()
    ended = ("session end (T0 %d)" % r.t0) in r.log
    if not ended:
        return "RUN-NOT-ENDED"
    if c and re.search(c, r.log):
        return "MAIN-CRASHED"
    if g and re.search(g, r.log):
        return "GATE-STOPPED"
    return "RUN-ENDED"


def rest_read(label):
    p = subprocess.run(["bash", os.path.join(SRC, E, "rb/rest_rule_e196.sh")], cwd=TREE,
                       env={"HOME": BOX, "PATH": "/usr/bin:/bin", "TZ": "America/Los_Angeles"}, capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip().replace("\n", " | ")
    print("   rest rule after %s: rc %d: %s" % (label, p.returncode, out[:300]), flush=True)
    return p.returncode, out


def nest(devnames):
    w = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev"]
    for d in devnames:
        f = os.path.join(S, "nest-%s.regular-file" % d)
        open(f, "a").close()
        w += ["--bind", f, "/dev/" + d]
    return w + ["--die-with-parent", "--"]


def pid_of(pattern):
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            cl = open("/proc/%s/cmdline" % d, "rb").read().replace(b"\0", b" ").decode(errors="ignore")
        except OSError:
            continue
        if pattern in cl:
            return int(d)
    return None


def stops_unit():
    """ST: stops_e196.py on synthetic telemetry files (no session): the rule's boundaries"""
    sp = os.path.join(R, E, "stops_e196.py")
    base = int(time.time() * 1000)
    CURRENT[0] = "ST"

    def case(name, ws, dies=None, end=None, done=False, pre_stop=False, wait=4.0):
        d = os.path.join(S, "st", name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "tel.jsonl"), "w") as f:
            for i, w in enumerate(ws):
                rec = {"t_ms": base + 100 * i, "board_w": w, "temp_c": {"minshire": [dies[i] if dies else 57]}}
                f.write(json.dumps(rec) + "\n")
        if pre_stop:
            open(os.path.join(d, "STOP"), "w").write('{"by": "hand", "why": "before", "t_ms": 1}\n')
        if done:
            open(os.path.join(d, "SESSION_DONE"), "w").close()
        args = [PY, "-B", sp, os.path.join(d, "tel.jsonl"), d] + (["--end-epoch", str(end)] if end else [])
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            p.wait(timeout=wait)
        except subprocess.TimeoutExpired:
            open(os.path.join(d, "SESSION_DONE"), "w").close()
            p.wait(timeout=5)
        stp = jl(os.path.join(d, "STOP"))
        return (stp[0] if stp else None)
    s = case("a-three-at-65", [40, 65.0, 65.0, 65.0, 40])
    ok(s and s["by"] == "stops_e196" and "at or above 65 W on 3 samples in a row" in s["why"], "ST1 three samples at exactly 65.0 W in a row: STOP (at or above)", s)
    s = case("b-broken-run", [65.5, 65.5, 64.9, 65.5, 65.5, 40])
    ok(s is None, "ST2 65.5, 65.5, 64.9, 65.5, 65.5: no stop (a sample below resets the run)", s)
    s = case("c-two-only", [66, 66, 30, 30])
    ok(s is None, "ST3 two samples at 66 W: no stop", s)
    s = case("d-die-69", [40] * 5, dies=[69] * 5)
    ok(s is None, "ST4 the die at 69 C: no stop", s)
    s = case("e-die-70", [40] * 5, dies=[57, 58, 70, 57, 57])
    ok(s and "die reading 70 C at or above 70 C" in s["why"], "ST5 a die reading of 70 C: STOP", s)
    s = case("f-end-epoch", [40] * 3, end=int(time.time()) + 2, wait=6)
    ok(s and "end-stop" in s["why"], "ST6 --end-epoch reached: the end-stop's STOP", s)
    s = case("g-done", [66] * 5, done=True)
    ok(s is None, "ST7 SESSION_DONE before anything: it exits, no STOP", s)
    s = case("h-first-writer", [66] * 5, pre_stop=True)
    ok(s and s["by"] == "hand", "ST8 a STOP already written by another: not overwritten (the first writer's reason stands)", s)


def main():
    global KLS
    print("E196 real-path desk test (kit-e196), %s; Python %s; the scratch %s" % (time.strftime("%F %T %Z"), sys.version.split()[0],
                                                                                  "<scratch>"), flush=True)
    KLS = setup()
    ORD = order("order-e196-aifoundry3.txt")
    DESK = {"E196_DESKTEST": "1"}
    # ---- 0 ----
    print("\n== 0 the sandbox and the stand-in box", flush=True)
    import socket
    ok(socket.gethostname() == "aifoundry3", "0a the host's name is aifoundry3 in the sandbox")
    devs = sorted(d for d in os.listdir("/dev") if d.startswith("et"))
    ok(devs == ["et0_mgmt", "et0_ops"] and all(os.path.isfile("/dev/" + d) for d in devs), "0b /dev holds only et0_ops and et0_mgmt, regular files", devs)
    ok(len([d for d in os.listdir("/proc") if d.isdigit()]) < 40, "0c a private PID namespace")
    pf = subprocess.run(["bash", os.path.join(R, E, "preflight_e196.sh")], capture_output=True, text=True, cwd=S)
    ok(pf.returncode == 0 and "E196-PREFLIGHT: GO" in pf.stdout, "0d the box copy's preflight: GO, every send site READ", pf.stdout[-300:])
    stops_unit()
    # ---- D: the dry path ----
    r = run_case("D-dry", dry=True, timeout=120)
    ok(r.rc == 0 and "E196-DRY OK: 255 device calls (237 with the cut order)" in r.log, "D1 --dry: rc 0; the listing 255 device calls (237 cut), line for line the registered commands", r.log[-500:])
    ok(r.outd.endswith("-dry") and "; DRY)" in r.log.splitlines()[0] and all(" DRY " in ln for ln in r.log.splitlines()),
       "D2 the dry log: T<T0>-dry, 'session start (...; DRY)', every line DRY (every rest rule skips it)")
    ok(not any(r.calls.get(k) for k in ("sampler", "lab", "x14", "etwho")), "D3 no stand-in tool called (nothing opened)", {k: len(v) for k, v in r.calls.items()})
    ok(manifest_ok(r)[0] and r.src == "0", "D4 MANIFEST.sha256 exact; session.rc 0", manifest_ok(r)[1])

    if os.environ.get("E196_RP_QUICK") != "1":
        long_cases(ORD)
    refusal_cases()
    print("\nfailed: %s" % (fails or "none"), flush=True)
    print("DESKTEST-REALPATH-E196 %d of %d %s%s" % (npass, ncase, "PASS" if npass == ncase else "FAIL",
          " (QUICK: a development subset, never a logged result)" if os.environ.get("E196_RP_QUICK") == "1" else ""), flush=True)
    return 0 if npass == ncase else 1


def stop_after_gate(r):
    if smoke_gate_mark(r):
        write_stop(r, "desk test: by hand, after the smoke gate")
        return True
    return False


def long_cases(ORD):
    # ---- P: the real path through the smoke, both trains and two passes; a stop by hand in the gap after pass 1 ----
    def stop_after_pass1(r):
        if block_after(r, 1):
            write_stop(r, "desk test: by hand, in the gap after pass 1")
            return True
        return False
    r = run_case("P-realpath", scen={"runtime_every": 7, "bad_line_values": "fb0.bin", "bad_line_nth": 1}, actions=[stop_after_pass1], timeout=2400)
    P = r
    ok(r.rc == 0 and r.src == "0" and not r.timed_out, "P1 rc 0 (a stop by hand between blocks ends the session normally)", (r.rc, r.src))
    ok("the cut order: M = 60 minutes: M >= 53: every arm, passes 0-5 and pass 6 if it fits" in r.log and "the first card command at" in r.log,
       "P2 the first card command stamped; the cut order read at the start: M = 60, every arm", r.log[:900])
    cfg = [c for c in r.calls.get("sampler", []) if c.get("event") == "config"]
    cs = json.loads(text(os.path.join(r.outd, "run", "config-start.json")) or "{}")
    ok(len(cfg) == 2 and all(c.get("lock_held") is True for c in cfg) and cs.get("tdp_w") == 0 and cs.get("minion_mhz") == 600,
       "P3 the opening and closing configuration reads through E128's guard, each under the card lock; the opening reads TDP 0 W, 600 MHz", cfg)
    starts = [c for c in r.calls.get("sampler", []) if c.get("event") == "start"]
    ends = [c for c in r.calls.get("sampler", []) if c.get("event") in ("exit_on_sigterm", "exit_at_seconds")]
    ok(len(starts) == 1 and starts[0]["argv"][:2] == ["sample", "--seconds"] and starts[0]["argv"][3:] == ["--every-ms", "100"]
       and len(ends) == 1 and ends[0]["event"] == "exit_on_sigterm", "P4 one sampler, sample --seconds N --every-ms 100, stopped by SIGTERM once", (starts, ends))
    hl = [m for m in r.marks if m.get("kind") == "heater_level"]
    sg = [m for m in r.marks if m.get("kind") == "smoke_gate"]
    sm = [x for x in r.runs if x.get("role") == "smoke"]
    ok(len(hl) == 1 and hl[0].get("ok") and hl[0].get("board_max_w") and hl[0]["board_max_w"] < 70 and len(sg) == 1 and sg[0].get("ok"),
       "P5 the smoke: the heater check on the lab's host (exit 0, below 70 W); SMOKE-GATE PASS", (hl, sg))
    lab_set = sorted({x["arm"] for x in sm if x.get("set") == "lab" and x.get("binary") == "sparsity_host" and x.get("readback") == "none"})
    pre_set = sorted({x["arm"] for x in sm if x.get("set") == "premise" and x.get("binary") == "x14_host" and "readback" not in x})
    pchk = [c for c in r.checks if c.get("pass") == -1 and c.get("set") == "premise"]
    ok(lab_set == pre_set == sorted(["I.H.m00FF", "I.R.m00FF", "Z.a0", "I.R.full"]) and len(pchk) == 8 and all(c["ok"] for c in pchk),
       "P6 the smoke's two sets: the four arms on the lab's host (readback none) and on the request's host (8 read-backs, all ok)", (lab_set, pre_set, len(pchk)))
    smt = [x for x in r.trecs if x.get("role") == "smoke"]
    ok(sorted({(x["process"], x["order"]) for x in smt}) == [(0, "SFFS"), (1, "FSSF")] and len(smt) == 28,
       "P7 the smoke's T1 processes: SFFS then FSSF, 14 launch records each", len(smt))
    ok_tr = True
    why = []
    for t, blk in (("T1", 101), ("T2", 102)):
        tr = [x for x in r.trecs if x.get("train") == t and x.get("role") == "train"]
        procs = {}
        for x in tr:
            procs.setdefault(x["process"], []).append(x)
        for k, rs in procs.items():
            rs.sort(key=lambda z: z["launch"])
            o = "SFFS" if k % 2 == 0 else "FSSF"
            want = [o[0], o[0]] + [o[(n - 1) % 4] for n in range(1, len(rs) - 1)]
            if [z["kind"] for z in rs] != want or len(rs) != 14 or rs[0]["order"] != o:
                ok_tr = False; why.append((t, k))
        anc = [x for x in r.runs if x.get("pass") == blk and x.get("role") in ("train_anchor_first", "train_anchor_last")]
        if len(procs) != 24 or {x["role"] for x in anc} != {"train_anchor_first", "train_anchor_last"} or \
                not all(x.get("binary") == "sparsity_host" and x.get("readback") == "none" and x["arm"] == "K.pi" for x in anc):
            ok_tr = False; why.append((t, len(procs), len(anc)))
    tchk = [c for c in r.checks if c.get("role") == "train"]
    ok(ok_tr and len(tchk) == 96 and all(c["ok"] for c in tchk), "P8 both trains: K.pi on the lab's host (readback none), 24 processes alternating SFFS and FSSF on the request's host, 14 launches each, 96 read-backs ok", why[:3])
    for p in (0, 1):
        seqs = runs_by_seq(r, p)
        arms = [x[0]["arm"] for x in seqs]
        want = list(ORD[p])
        if p == 0:
            want.remove("F.B0")
        rec_ok = all(all(y.get("binary") == "sparsity_host" and y.get("readback") == "none" and y["ops"] == y["iters"] * y["minions"]
                         and y["minions"] == 1024 for y in x) for x in seqs)
        ok(arms == want and rec_ok, "P9.%d pass %d: the registered order for aifoundry3%s, every run on the lab's host, ops = iters x minions, readback none" %
           (p, p, " (F.B0's unreadable run written as nothing)" if p == 0 else ""), (len(arms), arms[:6]))
    un = [m for m in r.marks if m.get("kind") == "host_lines" and m.get("written") is False]
    rt = [m for m in r.marks if m.get("kind") == "host_lines" and m.get("runtime_lines")]
    ok(len(un) == 1 and "F.B0" in un[0].get("what", "") and un[0].get("pass") == 0 and "Opening device" not in json.dumps(un[0].get("unreadable")),
       "P10 the one unreadable host output (F.B0, pass 0: unknown text inside a line): no record written, a mark names it", un)
    nsplit = sum(len(m["runtime_lines"]) for m in rt)
    ok(len(rt) >= 10 and all(m.get("written", True) is not False or "F.B0" in m.get("what", "") for m in rt),
       "P11 runtime lines INSIDE host lines (every 7th process of each host): %d dropped over %d processes, every one of those processes' records written" % (nsplit, len(rt)))
    lab = device_calls(r, "lab")
    x14 = device_calls(r, "x14")
    ok(lab and x14 and all(c.get("lock_held") is True for c in lab + x14) and all(c["argv"][-2] == "--stop-file" for c in lab + x14),
       "P12 every host process with the card lock held, --stop-file last (%d lab-host processes, %d request-host processes)" % (len(lab), len(x14)))
    ok(r.stop and r.stop.get("by") == "hand" and "trains complete: 2 of 2; passes complete: 2 of 7" in r.log, "P13 the stop by hand honoured in the gap: trains 2 of 2, passes 2 of 7", r.log[-500:])
    ce = json.loads(text(os.path.join(r.outd, "run", "config-end.json")) or "{}")
    ok(ce.get("tdp_w") == 0, "P14 the closing configuration read made after the holder check", ce)
    m = manifest_ok(r)
    ok(m[0] and "session end (T0 %d)" % r.t0 in r.log and s20_reading(r) == "RUN-ENDED", "P15 session end; MANIFEST exact; step 10 reads RUN-ENDED", (m[1], s20_reading(r)))
    red = subprocess.run([PY, "-I", "-B", os.path.join(SRC, E, "reduce_e196.py"), os.path.join(r.outd, "run"), "--readback-none-ok",
                          "--json", os.path.join(S, "P-x14.json")], capture_output=True, text=True)
    rj = json.load(open(os.path.join(S, "P-x14.json"))) if red.returncode == 0 else {}
    ex = (rj.get("readback_gate") or {}).get("exempt_runs")
    ok(red.returncode == 0 and ex is not None and ex >= 60 and rj.get("trains", {}).get("T1", {}).get("units") == 12,
       "P16 the registered reduction reads the real path's files (stand-in numbers): rc 0; readback_gate %s runs exempted; T1 12 units" % ex, red.stderr[-300:])
    c = subprocess.run([PY, "-I", "-B", os.path.join(SRC, E, "check_e196.py"), os.path.join(r.outd, "run"), os.path.join(S, "P-x14.json"),
                        "--out", os.path.join(S, "P-checks.json")], capture_output=True, text=True)
    ok(c.returncode == 0 and "CHECKS-E196: " in c.stdout and "4 PASS (108 of 108" in c.stdout, "P17 the section 8 checker reads them: rc 0; check 4 PASS 108 of 108", c.stdout[-400:])
    rc_, ro = rest_read("P")
    ok(rc_ == 3 and "E196" in ro and "REFUSED" in ro, "P18 the rest rule counts P's session (REFUSED: within 40 minutes of E196's session end)", ro)

    # ---- the holders and the lock ----
    r = run_case("H1-holder-at-start", scen={"etwho": "foreign"}, timeout=60)
    ok(r.rc == 3 and "no device opened" in r.log and not any(r.calls.get(k) for k in ("sampler", "lab", "x14")), "H1 a holder at the start: exit 3, nothing opened", (r.rc, list(r.calls)))
    rc_, ro = rest_read("H1")
    ok("E196" in ro and rc_ == 3, "H1b the rest rule skips H1's refusal (no device opened) and still reads P's end", ro)
    r = run_case("H2-foreign-process", scen={"foreign_proc": True}, timeout=60)
    ok(r.rc == 3 and "device process(es) of another user" in r.log and not any(r.calls.get(k) for k in ("sampler", "lab", "x14")), "H2 another user's device process: exit 3, nothing opened", r.rc)
    hp = hold_lock(25)
    r = run_case("H3-lock-held-at-start", timeout=60)
    end_hold(hp)
    ok(r.rc == 3 and "the card lock is held" in r.log and not any(r.calls.get(k) for k in ("sampler", "lab", "x14")), "H3 the card lock held at the start: exit 3, nothing opened", r.rc)
    r = run_case("H4-holder-between-blocks", scen={"etwho": "foreign_after_block", "after_block": 101, "x14_scale": 0.25}, timeout=700)
    ok(r.rc == 1 and "train T2: the card is not free, stopping" in r.rlog and "trains complete: 1 of 2" in r.log and "session stopped" in r.log,
       "H4 a holder after train T1: the session stops before T2 (run_session rc 3); session.rc 1, T1's blocks stand", (r.rc, r.rlog[-300:]))
    t_end = max((mk["t1_ms"] for mk in r.marks if mk.get("pass") == 101 and mk.get("label") == "after"), default=0)
    nd = no_device_after(r, t_end)
    ok(nd[0], "H4b no device process after T1's end", nd[1])
    # ---- the opening configuration gate ----
    r = run_case("CFG-config-gate", scen={"config_tdp": 65}, timeout=90)
    ok(r.rc == 3 and "GATE-STOP: the opening configuration read is not TDP 0 W and 600 MHz" in r.rlog and "GATE-STOP:" in r.log
       and not [c for c in r.calls.get("sampler", []) if c.get("event") == "start"] and not device_calls(r, "lab"),
       "CFG the opening configuration read at TDP 65 W: GATE-STOP (rc 12 in the port), no sampler, no block, session.rc 3", (r.rc, r.rlog[-300:]))
    ok(s20_reading(r) == "GATE-STOPPED", "CFGb step 10 reads it GATE-STOPPED", s20_reading(r))

    def take_lock_when_tel(r):
        if os.path.exists(os.path.join(r.outd, "run", "telemetry.jsonl")) and os.path.getsize(os.path.join(r.outd, "run", "telemetry.jsonl")) > 0:
            r.holder = hold_lock(40)
            return True
        return False
    r = run_case("L-lock-after-sampler", actions=[take_lock_when_tel], timeout=150)
    if getattr(r, "holder", None):
        end_hold(r.holder)
    ok(r.rc == 3 and "smoke: the card lock was busy, nothing more runs" in r.rlog and not device_calls(r, "lab") and "GATE-STOP:" in r.log,
       "L the card lock taken after the sampler started: the smoke's lock busy (75), nothing run, GATE-STOP", (r.rc, r.rlog[-200:]))
    ends = [c for c in r.calls.get("sampler", []) if c.get("event") == "exit_on_sigterm"]
    ok(len(ends) == 1, "Lb the sampler still stopped by SIGTERM", ends)
    # ---- L2 (Q191, lane fix-e196, verify-e196's finding 6): the card lock taken in the gap after pass 0, after data: the port's
    # exit 75 at pass 1, which the wrapper reads as a registered stop ("session stopped", session.rc 1; the blocks done stand) ----
    def take_lock_after_pass0(r):
        if block_after(r, 0):
            r.holder = hold_lock(120)
            return True
        return False
    r = run_case("L2-lock-after-pass0", scen={"x14_scale": 0.25}, actions=[take_lock_after_pass0], timeout=1500)
    if getattr(r, "holder", None):
        end_hold(r.holder)
    ok(r.rc == 1 and r.src == "1" and "pass 1: exit 75 (card lock busy), stopping" in r.rlog
       and "session stopped: run_session_e196.sh rc 75" in r.log and "trains complete: 2 of 2; passes complete: 1 of 7" in r.log,
       "L2 the card lock taken in the gap after pass 0 (data written): pass 1's lock busy (75); session.rc 1, 'session stopped', the trains and pass 0 stand", (r.rc, r.src, r.rlog[-300:], r.log[-300:]))
    t_end = max((mk["t1_ms"] for mk in r.marks if mk.get("pass") == 0 and mk.get("label") == "after"), default=0)
    nd = no_device_after(r, t_end)
    m = manifest_ok(r)
    ok(t_end > 0 and nd[0] and m[0] and s20_reading(r) == "RUN-ENDED",
       "L2b no device process after pass 0's end; MANIFEST exact; step 10 reads RUN-ENDED (the blocks done stand)", (t_end, nd[1], m[1], s20_reading(r)))
    # ---- the smoke ----
    r = run_case("HC-heater-ceiling", scen={"heater_w": 72.0}, timeout=150)
    hlm = [m for m in r.marks if m.get("kind") == "heater_level"]
    ok(r.rc == 3 and len(device_calls(r, "lab")) == 1 and not device_calls(r, "x14") and hlm and hlm[0].get("board_max_w", 0) > 70
       and "smoke: exit 9" in r.rlog and "at or above 65 W" in (r.stop or {}).get("why", ""),
       "HC the smoke's heater at 72 W: the lab's 65 W stop writes STOP first and the heater check's 70 W ceiling ends the block (exit 9): no smoke arm, GATE-STOP", (r.rc, r.stop, r.rlog[-200:]))
    r = run_case("HF-heater-fails", scen={"heater_rc_at": 1}, timeout=150)
    ok(r.rc == 3 and any("heater check" in p for m in r.marks if m.get("kind") == "smoke_gate" for p in m.get("problems", [])),
       "HF the heater check's launch fails (exit 1): the smoke gate fails at once, GATE-STOP", (r.rc, r.rlog[-200:]))
    r = run_case("G1-premise-readback", scen={"check_bad_arm": "I.R.m00FF"}, timeout=200)
    sgm = smoke_gate_mark(r)
    ok(r.rc == 3 and sgm and not sgm[0]["ok"] and any("I.R.m00FF: C read-back" in p for p in sgm[0]["problems"]) and
       len(device_calls(r, "x14")) == 6, "G1 a premise run's read-back not ok: SMOKE-GATE FAIL, no train, GATE-STOP", (r.rc, sgm))
    r = run_case("G2-mask-not-acting", scen={"lab_cycles_546_arm": "h.bin"}, timeout=200)
    sgm = smoke_gate_mark(r)
    ok(r.rc == 3 and sgm and any("kit stop K1: I.H.m00FF (sparsity_host) cycles per op 546.015, not within 0.5 of 544" in p for p in sgm[0]["problems"])
       and not any("(sparsity_host): cycles per op" in p for p in sgm[0]["problems"]),
       "G2 a lab-host smoke run of a masked arm at 546 cycles: the registered 0.5 %% gate passes it (2.7 cycles wide), the kit's stop K1 (0.5 cycles) fails the smoke", sgm)
    r = run_case("G3-tensor-error", scen={"tensor_err_arm": "lab_a_zeros"}, timeout=200)
    sgm = smoke_gate_mark(r)
    ok(r.rc == 3 and sgm and any("Z.a0 (sparsity_host) launch" in p for p in sgm[0]["problems"]), "G3 a lab-host smoke launch with a tensor error: SMOKE-GATE FAIL", sgm)
    r = run_case("U1-unreadable-smoke", scen={"bad_line_values": "h.bin", "bad_line_nth": 1}, timeout=200)
    sgm = smoke_gate_mark(r)
    ok(r.rc == 3 and sgm and any("host output unreadable" in p for p in sgm[0]["problems"]) and
       not [x for x in r.runs if x.get("arm") == "I.H.m00FF" and x.get("set") == "lab"], "U1 an unreadable lab-host smoke run: no record, SMOKE-GATE FAIL by name, GATE-STOP", sgm)
    r = run_case("U2-split-every-line", scen={"runtime_every": 1}, actions=[stop_after_gate], timeout=200)
    sgm = smoke_gate_mark(r)
    rtn = sum(len(m.get("runtime_lines") or []) for m in r.marks if m.get("kind") == "host_lines")
    ok(sgm and sgm[0]["ok"] and len([x for x in r.runs if x.get("role") == "smoke"]) >= 16 and rtn >= 11,
       "U2 the runtime line inside a line of EVERY host process: every record read, SMOKE-GATE PASS (%d runtime lines dropped)" % rtn, sgm)
    ok(r.rc == 3 and "GATE-STOP: run_session_e196.sh rc 0 before any train or pass block" in r.log, "U2b a stop by hand after the smoke gate: no train or pass ran, GATE-STOP (no data)", r.log[-300:])
    # ---- the live stops ----
    r = run_case("S1-lab-65W", scen={"host_w_from": {"n": 10, "w": 66.0, "role": "x14"}, "x14_scale": 0.25}, timeout=400)
    ok(r.stop and r.stop.get("by") == "stops_e196" and "at or above 65 W on 3 samples in a row" in r.stop.get("why", "") and r.rc == 1,
       "S1 board at 66 W in train T1: the lab's 65 W stop (stops_e196.py) writes STOP before stopwatch's 80 W; session.rc 1", (r.rc, r.stop))
    st_t = (r.stop or {}).get("t_ms", 0)
    late = [z for z in r.trecs if z["t_start_ms"] > st_t + 50]
    nd = no_device_after(r, st_t + 1000)
    ok(not late and nd[0], "S1b no launch started after the stop (the host reads STOP before every launch); no device process after", (len(late), nd[1]))
    r = run_case("S2-die-70", scen={"host_tss_from": {"n": 10, "tss": 74.0, "role": "x14"}, "x14_scale": 0.25}, timeout=400)
    ok(r.stop and "70 C" in r.stop.get("why", "") and r.rc == 1, "S2 a die reading at or above 70 C stops the session (the lab's stop, stopwatch or the block)", (r.rc, r.stop))
    r = run_case("S3-sampler-quiet", scen={"stall_after_s": 45, "x14_scale": 0.25}, timeout=400)
    ok(r.stop and "old" in r.stop.get("why", "") and r.rc in (1, 3), "S3 the sampler gone quiet: a stale-telemetry stop", (r.rc, r.stop))
    ends = [c for c in r.calls.get("sampler", []) if c.get("event") == "exit_on_sigterm"]
    ok(len(ends) == 1, "S3b the quiet sampler still ended by SIGTERM", ends)

    # ---- a crash, a signal ----
    def kill_block(r):
        if len(jl(os.path.join(r.outd, "run", "train.jsonl"))) >= 60:
            p = pid_of("run_block_e196.py")
            if p:
                os.kill(p, signal.SIGKILL)
                return True
        return False
    r = run_case("X1-crash", scen={"x14_scale": 0.25}, actions=[kill_block], timeout=400)
    ok(r.rc == 4 and "session ended without a registered stop" in r.log and s20_reading(r) == "MAIN-CRASHED" and manifest_ok(r)[0],
       "X1 the block killed from outside mid-train (no stop recorded): 'ended without a registered stop', session.rc 4, step 10 MAIN-CRASHED", (r.rc, r.log[-300:]))
    ends = [c for c in r.calls.get("sampler", []) if c.get("event") == "exit_on_sigterm"]
    ok(len(ends) == 1, "X1b the sampler stopped by SIGTERM by the port's own trap", ends)

    def term_wrapper(r):
        if count(r, "x14") >= 10:
            os.kill(r.pid, signal.SIGTERM)
            return True
        return False
    r = run_case("T-signal", scen={"x14_scale": 0.25}, actions=[term_wrapper], timeout=400)
    ends = [c for c in r.calls.get("sampler", []) if c.get("event") == "exit_on_sigterm"]
    ok(r.stop and "a signal to the wrapper" in r.stop.get("why", "") and r.rc == 1 and "session end (T0" in r.log and ends and manifest_ok(r)[0],
       "T SIGTERM to the wrapper mid-train: STOP, the run in flight finishes, the blocks done stand, session end, the sampler by SIGTERM", (r.rc, r.stop))
    # ---- the cut order ----
    r = run_case("M41-cut-order", env={"E196_DEADLINE_EPOCH": str(int(time.time()) + 41 * 60 + 30)}, actions=[stop_after_gate], timeout=200)
    ok("40 <= M < 43: DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF" in r.log and "PLAN runs=29 arms=25 dropped=F.Ae,Z.b50,I.H.mFFFF" in r.rlog,
       "M41 M = 41: the cut order, the three arms dropped from every pass (the port's plan line)", r.rlog[:400])
    r = run_case("M45-five-passes", env={"E196_DEADLINE_EPOCH": str(int(time.time()) + 45 * 60 + 30)}, actions=[stop_after_gate], timeout=200)
    dl = re.search(r"DEADLINE (\d\d:\d\d:\d\d)", r.log)
    ok("43 <= M < 53: every arm, the passes that fit" in r.log and "PLAN runs=32 arms=28" in r.rlog and dl,
       "M45 M = 45: every arm, the passes that fit; DEADLINE = the last end - 2 minutes", r.log[-600:])
    r = run_case("M39-no-session", env={"E196_DEADLINE_EPOCH": str(int(time.time()) + 39 * 60 + 30)}, timeout=60)
    ok(r.rc == 2 and "M < 40, no session" in r.log and "no device opened" in r.log and not r.calls.get("sampler"), "M39 M = 39: no session, no device opened", r.log[-300:])


def refusal_cases():
    # ---- refusals before anything ----
    def refused(r, what):
        return r.rc == 2 and "no device opened" in r.log and what in r.log and not any(r.calls.get(k) for k in ("sampler", "lab", "x14"))
    r = run_case("R1-hostname", wrap=["/usr/bin/bwrap", "--dev-bind", "/", "/", "--unshare-uts", "--hostname", "aifoundry9", "--die-with-parent", "--"], timeout=60)
    ok(refused(r, "not aifoundry3"), "R1 another host's name: refused before anything", r.log[-300:])
    r = run_case("R2-user", env={"USER": "nobody"}, timeout=60)
    ok(refused(r, "USER is not this login"), "R2 USER not the login: refused", r.log[-200:])
    r = run_case("R3-desktest-var", env={"E196_CAP_S": "300"}, timeout=60)
    ok(refused(r, "is a desk-test variable"), "R3 a desk-test variable without E196_DESKTEST=1: refused", r.log[-200:])
    mk = os.path.join(R, E, "proposal/src/make_x14.py")
    keep = open(mk, "rb").read()
    open(mk, "ab").write(b"\n")
    r = run_case("R4-registered-file", timeout=60)
    open(mk, "wb").write(keep)
    ok(refused(r, "a registered session file is off its sha256"), "R4 a registered file one byte longer: refused", r.log[-200:])
    r = run_case("R5-kit-list", env={"E196_KITLIST_SHA256": "0" * 64}, timeout=60)
    ok(refused(r, "the kit's list is not at the sha256"), "R5 the kit's list off the runbook's sha256: refused", r.log[-200:])
    r = run_case("R6-no-deadline", env={"E196_DEADLINE_EPOCH": None}, timeout=60)
    ok(refused(r, "no E196_DEADLINE_EPOCH"), "R6 no window last end: refused", r.log[-200:])
    br = os.path.join(R, "build", "BUILD-E196.txt")
    os.utime(br, (time.time() - 86400 * 2, time.time() - 86400 * 2))
    r = run_case("R7-build-record-old", timeout=60)
    write_build_record()
    ok(refused(r, "no build record written today"), "R7 the build record not from today: refused", r.log[-200:])
    xh = os.path.join(R, "build/x14/host/x14_host")
    keep = open(xh, "rb").read()
    open(xh, "ab").write(b"# changed\n")
    r = run_case("R8-host-not-recorded", timeout=60)
    open(xh, "wb").write(keep)
    os.chmod(xh, 0o755)
    ok(refused(r, "is not the binary today's build recorded"), "R8 a host that is not today's recorded build: refused", r.log[-200:])
    rec = text(br)
    open(br, "w").write(rec.replace("kernel_text_sha256_x14 " + TEXT, "kernel_text_sha256_x14 " + "1" * 64))
    r = run_case("R9-text-not-registered", timeout=60)
    write_build_record()
    ok(refused(r, "both kernels' .text at 8798e43c"), "R9 a kernel .text other than 8798e43c... in today's record: refused (E196.md section 11)", r.log[-200:])
    for name, devs, what in (("W1-two-cards", ["et0_ops", "et1_ops", "et0_mgmt", "et1_mgmt"], "not exactly /dev/et0_ops"),
                             ("W2-no-card", [], "not exactly /dev/et0_ops"), ("W3-no-mgmt", ["et0_ops"], "not exactly /dev/et0_ops")):
        r = run_case(name, wrap=nest(devs), timeout=60)
        ok(refused(r, what), "%s the node count (%s): refused before anything" % (name.split("-")[0], ",".join(devs) or "none"), r.log[-200:])
    # ---- step 10's patterns on the real script ----
    CURRENT[0] = "W10"
    g, c, n = s20_patterns()
    ok(g and c and n and re.search(n, os.path.join(R, E, "session_e196.sh")) and not re.search(n, os.path.join(R, E, "run_session_e196.sh")),
       "W10 step 10's patterns read from rb/s20_wait_e196.sh: the session found by its real script's name (session_e196.sh), never the port's", (g, c, n))
    # ---- Z ----
    CURRENT[0] = "Z"
    left = []
    for d in os.listdir("/proc"):
        if d.isdigit() and int(d) != os.getpid():
            try:
                cl = open("/proc/%s/cmdline" % d, "rb").read().replace(b"\0", b" ").decode(errors="ignore")
            except OSError:
                continue
            if any(k in cl for k in ("standin_e196", "session_e196", "run_session_e196", "run_block_e196", "stopwatch.py", "stops_e196", "holder.py")):
                left.append(cl[:120])
    ok(not left, "Z1 no process of the test left", left[:3])
    ok(not os.path.exists(os.path.join(S, "network-calls.log")), "Z2 no network call (ssh, rsync, scp stand-ins never called)")
    ok(sorted(d for d in os.listdir("/dev") if d.startswith("et")) == ["et0_mgmt", "et0_ops"], "Z3 no /dev/et* but the test's two regular files")
    # ---- the audit of the dry branches ----
    if os.environ.get("E196_RP_QUICK") != "1":
        audit()


def audit():
    """THE AUDIT (desk/dry-branches-e196.tsv): every line of the session's path that branches on DRY or a dry flag has a row; each row's
    text is the file's own line; each case it names passed in this run."""
    print("\n== AUDIT the dry branches (desk/dry-branches-e196.tsv)", flush=True)
    CURRENT[0] = "AUDIT"
    rows = []
    for ln in open(os.path.join(SRC, E, "desk/dry-branches-e196.tsv")):
        if ln.startswith("#") or not ln.strip():
            continue
        f, lineno, frag, dry, real, cases = ln.rstrip("\n").split("\t")
        rows.append((f, int(lineno), frag, cases))
    want = {}
    for f, pat in (("session_e196.sh", r"\$\{?DRY|\[ -n \"\$DRY\" \]"), ("run_session_e196.sh", r"\$\{DRY:-\}"), ("run_block_e196.py", r"a\.dry")):
        for i, l in enumerate(open(os.path.join(SRC, E, f)), 1):
            if re.search(pat, l) and not l.lstrip().startswith("#"):
                want[(f, i)] = l.strip()
    have = {(f, n): (frag, cases) for f, n, frag, cases in rows}
    missing = [k for k in want if k not in have]
    wrong = [k for k, (frag, _) in have.items() if k not in want or frag not in want[k]]
    ok(not missing and not wrong, "AUDIT1 every dry branch has a row (%d lines in the three files), each row's text the file's own line" % len(want), (missing[:3], wrong[:3]))
    unrun = []
    for k, (frag, cases) in have.items():
        for cname in [c.strip() for c in cases.split(",") if c.strip() and c.strip() != "-"]:
            if cname not in results or not all(results[cname]):
                unrun.append((k, cname))
    ok(not unrun, "AUDIT2 every case a row names ran and passed in this run", unrun[:5])


if __name__ == "__main__":
    sys.exit(main())
