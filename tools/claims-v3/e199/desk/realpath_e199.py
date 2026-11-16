#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE REAL-PATH DESK TEST's cases (run by
desk/desktest_realpath_e199.sh inside its sandbox; never run it outside one). E192's real-path test (tools/claims-v3/e192/desk/
realpath_e192.py, a6fe5c20, unchanged beside it) made aifoundry1 card 1's: it builds a stand-in aifoundry1 tree in the scratch directory
(~/nekko's shape: E199's root R = <tree>/build/claims-v3/aifoundry1-c1/e199 holding boxfiles-e199.txt's files as the sync puts them; the
box's reader, heater and the host as stand-ins, desk/standin_e199.py), then runs session_e199.sh's REAL path (DRY unset) case by case in
a private /dev holding aifoundry1's four node names (each a bind of /dev/null: character nodes that are no card), card 1's and card 0's
lock files, a private PID namespace and the host name aifoundry1: the dry path; the real path through the identity gates, the smoke,
two passes and a stop by hand (THE STOP PATH); the plain sampler; holders on either card; THE IDENTITY GATE (a) and (b) both ways (card
1's forms pass; card 0's, a missing ET_DEVICES and a second card's holder refused); THE WATCH on every host; card 1's live stop lines;
the smoke gate, the cap, the gate's death, a signal; aifoundry1's runtime line inside a host line; run_session.sh's free check after
the first card command; eight refusals; the node counts; run_session.sh's own selection refusals (its line 65 among them, which E192's
kit could not run without a character node). Nothing here opens a card; nothing is measured. THE QUIET DESK FLAG: no case starts while
E199_QUIET_FLAG names a file that exists (the round's flag while card-e194 uses aifoundry2's card): since fix-e199 (verify-e199 F7)
a flag found before or between cases ends the run at once, the remaining cases NOT RUN (exit 5); the test never waits inside its sandbox.
    /usr/bin/python3 -I -B realpath_e199.py <repo top> <scratch dir>
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
E = "tools/claims-v3/e199"
E2 = "tools/claims-v3/e192"
STANDIN = os.path.join(SRC, E, "desk/standin_e199.py")
TABLE = os.path.join(SRC, E2, "desk/arm-table-e192.jsonl")
BOX = os.path.join(S, "box")
TREE = os.path.join(BOX, "nekko")
RR = "build/claims-v3/aifoundry1-c1/e199"
R = os.path.join(TREE, RR)
SBIN = os.path.join(S, "sbin")
LOCK = "/run/lock/etsoc-shire1.lock"
LOCK0 = "/run/lock/etsoc-shire0.lock"
ME = pwd.getpwuid(os.getuid()).pw_name
PY = "/usr/bin/python3"
npass = ncase = 0
fails = []
_last_t0 = [0]


def ok(cond, label, detail=""):
    global npass, ncase
    ncase += 1
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


def shim(path, role, selection=True):
    """A stand-in tool; with selection, its text carries the word ET_DEVICES (run_session.sh's and the wrapper's grep reads a binary's
    linked device layer for it; a stand-in has none, so the word is written here, as a real binary built against /opt/et carries it)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("#!/bin/bash\n%sexec -a \"$0\" %s -I -B %s %s \"$@\"\n" % ("# stand-in: honours ET_DEVICES\n" if selection else "", PY, STANDIN, role))
    os.chmod(path, 0o755)


def setup():
    os.makedirs(R, exist_ok=True)
    files = [ln.strip() for ln in open(os.path.join(SRC, E, "boxfiles-e199.txt")) if ln.strip() and not ln.startswith("#")]
    for p in files:
        if p.endswith("SHA256SUMS-e199-kit") and not os.path.exists(os.path.join(SRC, p)):
            continue
        os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
        shutil.copy2(os.path.join(SRC, p), os.path.join(R, p))
    # the kit's list: a stand-in made here from R's copies (the real list holds this test's log); the session reads its sha256
    kl = os.path.join(R, E, "SHA256SUMS-e199-kit")
    reg = {ln.split()[1] for ln in open(os.path.join(R, E, "SHA256SUMS-e199-registration")) if ln.strip()}
    rows = []
    for root, _, fs in os.walk(os.path.join(R, E)):
        for fn in fs:
            p = os.path.relpath(os.path.join(root, fn), R)
            if p in reg or p.endswith("SHA256SUMS-e199-kit") or p.endswith("SHA256SUMS-e199-registration") or "/build/" in p:
                continue
            rows.append("%s  %s" % (sha(os.path.join(R, p)), p))
    with open(kl, "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x.split("  ")[1])) + "\n")
    shim(os.path.join(TREE, "build/ettelem/ettelem"), "sampler")
    shim(os.path.join(TREE, "build/sparsity/host/sparsity_host"), "heater")
    shim(os.path.join(R, "build/intbits/host/intbits_host"), "host")
    open(os.path.join(R, "build/intbits/kernel.standin"), "w").write("not a kernel\n")
    shim(os.path.join(SBIN, "et-who"), "etwho")
    shim(os.path.join(SBIN, "ps"), "ps")
    for t in ("ssh", "rsync", "scp"):
        with open(os.path.join(SBIN, t), "w") as f:
            f.write("#!/bin/bash\necho \"%s $*\" >> %s/network-calls.log\necho 'STAND-IN: no network in this test' >&2\nexit 97\n" % (t, S))
        os.chmod(os.path.join(SBIN, t), 0o755)
    os.makedirs(os.path.join(S, "standin"), exist_ok=True)
    pvt = os.path.join(S, "standin", "pvt_standin.py")
    with open(pvt, "w") as f:
        f.write("import runpy, sys\nsys.argv[0:1] = [%r, 'pvt']\nrunpy.run_path(%r, run_name='__main__')\n" % (STANDIN, STANDIN))
    for lk in (LOCK, LOCK0):
        open(lk, "a").close()
    return sha(kl), pvt, sha(pvt), sha(os.path.join(TREE, "build/ettelem/ettelem"))


def new_t0():
    t = max(int(time.time()), _last_t0[0] + 1)
    _last_t0[0] = t
    return t


def base_env(sd, extra):
    env = {"PATH": SBIN + ":/usr/local/bin:/usr/bin:/bin", "HOME": BOX, "USER": ME, "LOGNAME": ME, "LANG": "C.UTF-8",
           "TZ": "America/Los_Angeles", "E199_STANDIN_DIR": sd, "E199_STANDIN_TABLE": TABLE,
           "E199_KITLIST_SHA256": KLS, "E199_DEADLINE_EPOCH": str(int(time.time()) + 7200),
           "E199_DESKTEST": "1", "E199_READER_SHA256": RDS}
    env.update({k: v for k, v in extra.items() if v is not None})
    for k, v in extra.items():
        if v is None:
            env.pop(k, None)
    return env


class Run:
    pass


def run_case(name, scen=None, env=None, actions=(), timeout=300, dry=False, direct=False, wrap=None, lock=True):
    print("\n== %s" % name, flush=True)
    t0 = new_t0()
    sd = os.path.join(S, "sd", name)
    os.makedirs(sd, exist_ok=True)
    json.dump(scen or {}, open(os.path.join(sd, "scenario.json"), "w"))
    shutil.copy2(TABLE, os.path.join(sd, "arm-table.jsonl"))
    for fn in os.listdir(os.path.join(sd)):
        if fn.startswith("count-"):
            os.unlink(os.path.join(sd, fn))
    if lock:
        open(LOCK, "a").close()
    elif os.path.exists(LOCK):
        os.unlink(LOCK)
    r = Run()
    r.name, r.t0, r.sd = name, t0, sd
    r.outd = os.path.join(TREE, "build/e199/T%d%s" % (t0, "-dry" if dry else ""))
    if direct:
        r.outd = os.path.join(S, "direct", name)
        os.makedirs(r.outd, exist_ok=True)
    rundir = os.path.join(r.outd, "run") if not direct else os.path.join(r.outd, "run")
    open(os.path.join(sd, "rundir"), "w").write(rundir + "\n")
    e = base_env(sd, dict(env or {}, E199_T0=str(t0)))
    if direct:
        e.update({"SAMPLER": "ettelem", "ETTELEM": os.path.join(TREE, "build/ettelem/ettelem"),
                  "HEATER": os.path.join(TREE, "build/sparsity/host/sparsity_host"),
                  "H": (env or {}).get("H") or os.path.join(R, "build/intbits/host/intbits_host")})
        cmd = ["bash", os.path.join(R, E2, "proposal/src/run_session.sh"), rundir, "9"]
    else:
        cmd = ["bash", os.path.join(R, E, "session_e199.sh")] + (["--dry"] if dry else [])
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
            except Exception as ex:          # an action that cannot read yet tries again
                print("   (action %s: %s)" % (getattr(a, "__name__", "?"), ex), flush=True)
        if time.time() - r.start > timeout and not timed_out:
            timed_out = True
            print("   TIMEOUT at %d s: STOP written by the test" % timeout, flush=True)
            write_stop(r, "desk test: the case's own bound")
        if timed_out and time.time() - r.start > timeout + 60:
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
    r.gate = jl(os.path.join(rundir, "gate.jsonl"))
    st = jl(os.path.join(rundir, "STOP"))
    r.stop = st[0] if st else None
    r.calls = {}
    cd = os.path.join(sd, "calls")
    if os.path.isdir(cd):
        for fn in os.listdir(cd):
            r.calls[fn[:-4]] = jl(os.path.join(cd, fn))
    print("   rc %s in %.1f s; outd %s; calls %s; stop %s" % (r.rc, r.elapsed, os.path.relpath(r.outd, S),
          {k: len(v) for k, v in r.calls.items()}, (r.stop or {}).get("why", "-")[:160]), flush=True)
    for ln in r.log.splitlines()[-6:]:
        print("   | " + ln[:220], flush=True)
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
            if rel in ("MANIFEST.sha256", "wrapper.rc"):
                continue
            have.add(rel)
    bad = [p for p in listed if p not in have or sha(os.path.join(r.outd, p)) != listed[p]]
    extra = sorted(have - set(listed))
    return (not bad and not extra), "bad %s extra %s" % (bad[:3], extra[:3])


def marks_after(r, p):
    return any(m.get("kind") == "idle" and m.get("label") == "after" and m.get("pass") == p for m in jl(os.path.join(r.outd, "run", "marks.jsonl")))


def gate_ev(r, kind):
    return [g for g in jl(os.path.join(r.outd, "run", "gate.jsonl")) if g.get("kind") == kind]


def count(r, name):
    try:
        return int(open(os.path.join(r.sd, "count-" + name)).read().strip() or 0)
    except OSError:
        return 0


def order():
    o = {}
    for ln in open(os.path.join(SRC, E, "order-e199-aifoundry1.txt")):
        if ln.startswith("pass "):
            head, rest = ln.split(":", 1)
            o[int(head.split()[1])] = [w.split(":")[-1] for w in rest.split()]
    return o


def by_seq(r, p):
    seqs = {}
    for x in r.runs:
        if x.get("pass") == p:
            seqs.setdefault(x["seq"], []).append(x)
    return [seqs[k] for k in sorted(seqs)]


def no_device_after(r, t_ms):
    """No heater or host process started after t_ms (with 50 ms of slack for a process already being started)."""
    late = [c for role in ("heater", "host") for c in r.calls.get(role, []) if c.get("event") == "call" and c.get("t0", 0) * 1000 > t_ms + 50]
    return not late, late[:2]


def hold_lock(seconds):
    code = ("import fcntl, os, time\nfd = os.open(%r, os.O_RDONLY)\nfcntl.flock(fd, fcntl.LOCK_EX)\nopen(%r, 'w').write('held')\n"
            "time.sleep(%d)\n") % (LOCK, os.path.join(S, "holder.flag"), seconds)
    f = os.path.join(S, "holder.py")
    open(f, "w").write(code)
    return subprocess.Popen([PY, "-I", "-B", f], start_new_session=True)


# ---- fix-e192's helpers -------------------------------------------------------------------------------------------------------------
def s20_reading(r):
    """step 10's reading of the wrapper's log, with the gate-stop pattern read from rb/s20_wait_e199.sh itself: (reading, pattern)."""
    src = text(os.path.join(SRC, E, "rb/s20_wait_e199.sh"))
    m = re.search(r"if grep -qE '([^']+)' \"\$L\" 2>/dev/null; then echo \"GATE-STOPPED", src)
    pat = m.group(1) if m else None
    ended = ("session end (T0 %d)" % r.t0) in r.log
    gate = bool(pat) and bool(re.search(pat, r.log))
    return ("RUN-ENDED" if ended else "RUN-NOT-ENDED") + (" GATE-STOPPED(16)" if gate else " (0)"), pat


def rest_read(label):
    """the kit's rest rule (rb/rest_rule_e199.sh) as step 9 sends it, run from the stand-in box's tree."""
    p = subprocess.run(["bash", os.path.join(SRC, E, "rb/rest_rule_e199.sh")], cwd=TREE,
                       env={"HOME": BOX, "PATH": "/usr/bin:/bin", "TZ": "America/Los_Angeles"}, capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip().replace("\n", " | ")
    print("   rest rule after %s: rc %d: %s" % (label, p.returncode, out[:300]), flush=True)
    return p.returncode, out


def nest(devnames, files=()):
    """a nested sandbox for one case: a fresh private /dev holding only the named stand-in nodes (each a bind of /dev/null: a character
    node that is no card) and the named regular files; all else as here."""
    w = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev"]
    for d in devnames:
        w += ["--dev-bind", "/dev/null", "/dev/" + d]
    for d in files:
        f = os.path.join(S, "nest-%s.regular-file" % d)
        open(f, "a").close()
        w += ["--bind", f, "/dev/" + d]
    return w + ["--die-with-parent", "--"]


def lock_free():
    try:
        fd = os.open(LOCK, os.O_RDONLY)
    except OSError:
        return True
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return True
    except BlockingIOError:
        return False
    finally:
        os.close(fd)


def end_holder(r):
    """end a case's stand-in lock holder (SIGTERM), if the stand-ins started one, and wait for the lock to come free."""
    pf = os.path.join(r.sd, "holder.pid")
    if os.path.exists(pf):
        try:
            os.kill(int(open(pf).read().strip()), signal.SIGTERM)
        except (OSError, ValueError):
            pass
        os.unlink(pf)
    t = time.time()
    while not lock_free() and time.time() - t < 10:
        time.sleep(0.1)
    return lock_free()


def main():
    global KLS, RDS
    print("E199 real-path desk test (kit-e199), %s; Python %s; the scratch %s" % (
        time.strftime("%F %T %Z"), sys.version.split()[0], "<scratch>"), flush=True)
    KLS, pvt, pvt_sha, RDS = setup()
    PVT = {"E199_PVT_SAMPLE": pvt, "E199_PVT_SHA256": pvt_sha}
    ORD = order()
    QF = os.environ.get("E199_QUIET_FLAG", "")

    def quiet_wait():
        """THE QUIET DESK FLAG (the round's rule): no new case starts while card-e194's flag exists on this box. The test never waits
        inside its sandbox (fix-e199, verify-e199 F7: a paused run here held a card lane's pre-launch check): it ends, NOT RUN."""
        if QF and os.path.exists(QF):
            print("QUIET-FLAG: the quiet-desk flag exists: the remaining cases NOT RUN (the test never waits inside its sandbox)", flush=True)
            sys.exit(5)
    _rc = run_case

    def run_case2(*a, **k):
        quiet_wait()
        return _rc(*a, **k)
    globals()["run_case"] = run_case2

    def stop_after_go(r):
        if gate_ev(r, "smoke_gate"):
            write_stop(r, "desk test: by hand after the smoke gate")
            return True
        return False

    def stop_after_identity(r):
        if "identity (a): IDENT-A OK" in text(os.path.join(r.outd, "session.log")):
            write_stop(r, "desk test: by hand after the identity gate (a)")
            return True
        return False

    def nodev_calls(r):
        return not any(r.calls.get(k) for k in ("heater", "host"))

    # ---- 0: the sandbox and the stand-in box ----
    print("\n== 0 the sandbox and the stand-in aifoundry1", flush=True)
    import socket
    import stat as st_
    ok(socket.gethostname() == "aifoundry1", "0a the host's name is aifoundry1 in the sandbox")
    devs = sorted(d for d in os.listdir("/dev") if d.startswith("et"))
    ok(devs == ["et0_mgmt", "et0_ops", "et1_mgmt", "et1_ops"] and all(
        st_.S_ISCHR(os.stat("/dev/" + d).st_mode) and os.stat("/dev/" + d).st_rdev == os.stat("/dev/null").st_rdev for d in devs),
       "0b the private /dev holds aifoundry1's four node names, each a bind of /dev/null (a character node that is no card)", devs)
    ok(len([d for d in os.listdir("/proc") if d.isdigit()]) < 40, "0c a private PID namespace (few processes visible)")
    pf = subprocess.run(["bash", os.path.join(R, E, "preflight_e199.sh")], capture_output=True, text=True, cwd=S)
    ok(pf.returncode == 0 and "PLAIN-CHAIN: GO" in pf.stdout and "PVT-CHAIN: GO" in pf.stdout,
       "0d the box copy's preflight: the plain chain GO (the stock table), the per-sensor chain GO (E144's table)", pf.stdout[-300:])
    ic = subprocess.run([PY, "-I", "-B", os.path.join(R, E, "ident_e199.py"), "selfcheck"], capture_output=True, text=True)
    ok(ic.returncode == 0 and "IDENT-E199 SELF-CHECK PASS" in ic.stdout, "0e the box copy's identity module self-check: card 1's forms pass, card 0's refused", ic.stdout[-300:])
    g = subprocess.run(["bash", os.path.join(R, E, "ettelem_guard_e199.sh"), "config"], capture_output=True, text=True,
                       env={"PATH": SBIN + ":/usr/bin:/bin", "E199_STANDIN_DIR": os.path.join(S, "sd-guard"), "ET_DEVICES": ""})
    g0 = subprocess.run(["bash", os.path.join(R, E, "ettelem_guard_e199.sh"), "config"], capture_output=True, text=True,
                        env={"PATH": SBIN + ":/usr/bin:/bin", "E199_STANDIN_DIR": os.path.join(S, "sd-guard"), "ET_DEVICES": "0"})
    gs = subprocess.run(["bash", os.path.join(R, E, "ettelem_guard_e199.sh"), "sample", "--seconds", "1"], capture_output=True, text=True,
                        env={"PATH": SBIN + ":/usr/bin:/bin", "E199_STANDIN_DIR": os.path.join(S, "sd-guard"), "ET_DEVICES": "1"})
    ok(g.returncode == 97 and g0.returncode == 97 and gs.returncode == 97 and not os.path.exists(os.path.join(S, "sd-guard", "calls")),
       "0f IA0: the guard refuses a missing ET_DEVICES, ET_DEVICES=0 and any word but config (exit 97), the reader never started",
       (g.returncode, g0.returncode, gs.returncode, g.stderr[-160:]))
    os.makedirs(os.path.join(S, "sd-guard"), exist_ok=True)
    ga = subprocess.run(["bash", os.path.join(R, E, "ettelem_guard_e199.sh"), "config"], capture_output=True, text=True,
                        env={"PATH": SBIN + ":/usr/bin:/bin", "E199_STANDIN_DIR": os.path.join(S, "sd-guard"), "ET_DEVICES": "1"})
    open(os.path.join(S, "ga.out"), "w").write(ga.stdout)
    open(os.path.join(S, "ga.err"), "w").write(ga.stderr)
    ia = subprocess.run([PY, "-I", "-B", os.path.join(R, E, "ident_e199.py"), "config", os.path.join(S, "ga.out"), os.path.join(S, "ga.err")],
                        capture_output=True, text=True)
    ok(ga.returncode == 0 and ga.stdout.startswith("Opening device 1\n") and ia.returncode == 0 and "IDENT-A OK: /dev/et1_mgmt" in ia.stdout,
       "0g the guard with ET_DEVICES=1 runs the reader's config (the runtime line first, card 1's block on stderr): IDENT-A OK", ia.stdout[-200:])

    # ---- D: the dry path ----
    r = run_case("D-dry", dry=True, timeout=120)
    ok(r.rc == 0 and "E199-DRY OK: 328 device calls" in r.log, "D1 --dry: rc 0, the dry listing 328 device calls in the registered order for aifoundry1", r.log[-400:])
    ok(r.outd.endswith("-dry") and "; DRY)" in r.log.splitlines()[0] and all(" DRY " in ln for ln in r.log.splitlines()),
       "D2 the dry log: the T<T0>-dry directory, 'session start (...; DRY)', every line DRY (every rest rule skips it)")
    ok(not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host", "etwho", "ps")), "D3 no stand-in tool was called (nothing opened)", {k: len(v) for k, v in r.calls.items()})
    m = manifest_ok(r)
    ok(m[0], "D4 MANIFEST.sha256 written last and exact", m[1])

    # ---- P: the real path, the per-sensor sampler, two passes, a stop by hand in the gap after pass 1 ----
    def stop_after_pass1(r):
        if marks_after(r, 1):
            write_stop(r, "desk test: by hand, in the gap after pass 1")
            return True
        return False
    r = run_case("P-realpath", scen={"scale": 0.5}, env=PVT, actions=[stop_after_pass1], timeout=1500)
    P = r
    ok(r.rc == 0 and not r.timed_out, "P1 rc 0 (a stop by hand between passes ends the session normally)", r.rc)
    cfg = [c for c in r.calls.get("sampler", []) if c.get("event") == "config"]
    ok(len(cfg) == 2 and cfg[0].get("lock_held") is True and cfg[0].get("et_devices") == "1" and cfg[0].get("card") == 1 and
       "identity (a): IDENT-A OK: /dev/et1_mgmt, physical device ID 1, minion_mv 499" in r.log,
       "P2 THE FIRST CARD COMMAND is the start config read under card 1's lock with ET_DEVICES=1: THE IDENTITY GATE (a) OK; the end read too", cfg[:1])
    probe = [c for c in r.calls.get("pvt", []) if c.get("event") == "probe_end"]
    pstart = [c for c in r.calls.get("pvt", []) if c.get("event") == "start"]
    ok("sampler: pvt (its probe answered" in r.log and len(probe) == 1 and len(pstart) == 2 and pstart[0].get("lock_held") is True and
       "--probe" in pstart[0].get("argv", []) and all(c.get("card") == 1 and c.get("held") for c in pstart),
       "P3 the per-sensor probe under card 1's lock answered (SAMPLER=pvt); then ONE sampler, both on card 1, each holding /dev/et1_mgmt", pstart)
    ok(pstart[-1].get("argv") == ["--seconds", "6000", "--every-ms", "100"] and pstart[-1].get("et_devices") == "1",
       "P4 the session's sampler: --seconds 6000 --every-ms 100, ET_DEVICES=1", pstart[-1])
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") in ("exit_on_sigterm", "exit_at_seconds")]
    ok(len(ends) == 1 and ends[0]["event"] == "exit_on_sigterm", "P5 the sampler stopped by SIGTERM (never killed), once", ends)
    ib = gate_ev(r, "identity_b")
    ok(len(ib) == 1 and ib[0].get("counts", {}).get("ours_on_mgmt", 0) >= 1 and ib[0]["counts"].get("ours_on_card0") == 0 and
       ib[0].get("sampler_nodes") == ["/dev/et1_mgmt"] and ib[0].get("decided_s_after_first_sample", 99) < 8,
       "P6 THE IDENTITY GATE (b): with the sampler running and before the smoke's first launch, our holder lines on card 1 only, the sampler holding /dev/et1_mgmt", ib)
    sg = gate_ev(r, "smoke_gate")
    idrow = [x for x in (sg[0]["runs"] if sg else []) if "identity_blocks" in x]
    ok(len(sg) == 1 and sg[0].get("verdict") == "GO" and [x["arm"] for x in sg[0]["runs"] if "arm" in x] == ["nop", "add.a.f2", "add.cr.l31"]
       and idrow and idrow[0]["card1_blocks"] == 4 and idrow[0]["smoke_device_processes"] == 4,
       "P7 the kit's smoke gate GO: the three runs' INTBITS lines, and each of the smoke's 4 device processes showed card 1's identity block", sg)
    hc = [m for m in r.marks if m.get("kind") == "heater_level"]
    hcr = [m for m in r.marks if m.get("kind") == "heater_check"]
    ok(len(hc) == 1 and hc[0].get("board_max_w") is not None and 45 < hc[0]["board_max_w"] < 65 and hcr and hcr[0].get("rc") == 0,
       "P8 the smoke's heater check: the heater ran (exit 0, its board level read) and stayed below card 1's 65 W line", (hc, hcr))
    for p in (0, 1):
        runs = by_seq(r, p)
        arms = [x[0]["arm"] for x in runs]
        ok(arms == ORD[p], "P9.%d pass %d: 36 runs in the registered order for aifoundry1 (order-e199-aifoundry1.txt)" % (p, p), (len(arms), arms[:5]))
        nl = [len(x) for x in runs]
        ok(bool(nl) and min(nl) >= 8 and all(all(y["ok"] and y["check_bad"] == 0 and y["participants"] == 1024 for y in x) for x in runs),
           "P10.%d pass %d: every run 8 or more INTBITS lines, every launch ok" % (p, p), (min(nl) if nl else 0, max(nl) if nl else 0))
    hcalls = [c for c in r.calls.get("host", []) if c.get("event") == "call"]
    ok(len(hcalls) == 3 + 36 * 2 and all(c.get("lock_held") is True and c.get("et_devices") == "1" for c in hcalls),
       "P11 75 host processes (smoke 3, passes 36 each), every one with card 1's lock held and ET_DEVICES=1", len(hcalls))
    launches = sum(c.get("launches", 0) for c in r.calls.get("host", []) if "launches" in c)
    ok(launches == len(r.runs) and launches > 0, "P12 AIFOUNDRY1'S RUNTIME LINE ('Opening device 1' on each host's stdout before its first INTBITS line): every launch printed is a record (none lost, none broken)", (launches, len(r.runs)))
    heats = [c for c in r.calls.get("heater", []) if c.get("event") == "call"]
    ok(len(heats) >= 2 and all(c.get("lock_held") is True and c.get("et_devices") == "1" for c in heats), "P13 the heater ran under card 1's lock with ET_DEVICES=1 (the check and the approach)", len(heats))
    ok(r.stop and r.stop.get("by") == "hand" and "STOP:" in r.rlog and "passes complete: 2 of 9" in r.log, "P14 THE STOP PATH: the stop by hand was honoured after the gap: 2 passes complete", r.log[-500:])
    cn = [g.get("next_pass") for g in gate_ev(r, "cap_ok")]
    ok(cn[:2] == [0, 1] and len(cn) <= 3, "P15 the cap read before passes 0 and 1, each within it", cn)
    ok("the end config read: exit 0; IDENT-A OK: /dev/et1_mgmt" in r.log and os.path.exists(os.path.join(r.outd, "config-end.err")),
       "P16 the end config read kept its stderr and named card 1 (recorded, not a gate)", r.log[-600:])
    m = manifest_ok(r)
    ok(m[0] and text(os.path.join(r.outd, "wrapper.rc")).strip() == "0" and "session end (T0 %d)" % r.t0 in r.log, "P17 session end, MANIFEST exact, wrapper.rc 0", m[1])
    w0 = [c for c in r.calls.get("etwho", []) if c.get("call") == 1]
    ok(w0 and w0[0].get("holders") == 0 and gate_ev(r, "session_done") == [] and gate_ev(r, "stop_seen"),
       "P18 et-who before anything read no holder on either card; the gate ended at the stop", w0)
    pre = subprocess.run([PY, "-I", "-B", os.path.join(SRC, E, "prefilter_e199.py"), os.path.join(r.outd, "run"), os.path.join(S, "P-filtered")],
                         capture_output=True, text=True)
    red = subprocess.run([PY, "-I", "-B", os.path.join(SRC, E2, "proposal/src/reduce_intbits.py"), os.path.join(S, "P-filtered"),
                          "--out", os.path.join(S, "P-intbits.json")], capture_output=True, text=True)
    ok(pre.returncode == 0 and red.returncode == 0 and os.path.exists(os.path.join(S, "P-intbits.json")),
       "P19 E199's pipeline reads the real path's files (stand-in numbers): E151's rail filter (prefilter_e199.py), then E192's reducer, rc 0",
       (pre.stdout[-200:], pre.stderr[-200:], red.stderr[-200:]))
    rr = rest_read("P")
    ok(rr[0] == 3 and "REFUSED" in rr[1], "P20 the rest rule on the stand-in box right after P: REFUSED (E199's own session log counted)", rr[1][:200])

    # ---- FE: the plain sampler by the go ----
    r = run_case("FE-plain-by-go", env=dict(PVT, E199_SAMPLER="ettelem"), actions=[stop_after_go], timeout=240)
    st0 = [c for c in r.calls.get("sampler", []) if c.get("event") == "start"]
    ok("the go named the plain sampler" in r.log and not r.calls.get("pvt") and st0 and st0[0].get("argv") == ["sample", "--seconds", "6000", "--every-ms", "100"]
       and st0[0].get("card") == 1 and st0[0].get("held"), "FE E199_SAMPLER=ettelem: no probe; the plain sampler on card 1 holding /dev/et1_mgmt", st0)
    ok(gate_ev(r, "identity_b") and r.rc == 8 and count(r, "host") == 3, "FEb identity (b) OK with the plain sampler; the stop by hand after the smoke: rc 8, 3 host runs", (r.rc, count(r, "host")))

    # ---- the free check and the holders: either card blocks ----
    r = run_case("H1-holder-card1-at-start", scen={"etwho_lines": ["/dev/et1_ops otheruser 4242 foo_host"]}, env=PVT, timeout=60)
    ok(r.rc == 3 and "no device opened" in r.log and not r.calls.get("sampler") and not r.calls.get("pvt") and nodev_calls(r),
       "H1 a holder on card 1 at the start: exit 3, nothing opened (no config read)", (r.rc, list(r.calls)))
    r = run_case("H1b-holder-card0-at-start", scen={"etwho_lines": ["/dev/et0_ops otheruser 4242 foo_host"]}, env=PVT, timeout=60)
    ok(r.rc == 3 and "card 0 1" in text(os.path.join(r.outd, "etwho-before.txt")) and not r.calls.get("sampler") and nodev_calls(r),
       "H1b a second card's holder (another login on card 0) at the start: exit 3, nothing opened (either card blocks)", (r.rc, text(os.path.join(r.outd, "etwho-before.txt"))))
    r = run_case("H2-foreign-process", scen={"foreign_proc": True}, env=PVT, timeout=60)
    ok(r.rc == 3 and "device process(es) of another user" in r.log and not r.calls.get("sampler") and nodev_calls(r), "H2 another user's device process: exit 3, nothing opened", r.rc)
    hp = hold_lock(25)
    t_w = time.time()
    while not os.path.exists(os.path.join(S, "holder.flag")) and time.time() - t_w < 10:
        time.sleep(0.1)
    r = run_case("H3-card1-lock-held", env=PVT, timeout=60)
    hp.terminate(); hp.wait()
    os.unlink(os.path.join(S, "holder.flag"))
    ok(r.rc == 3 and "card 1's lock is held" in r.log and not r.calls.get("sampler") and nodev_calls(r), "H3 card 1's lock held at the start: exit 3, nothing opened", r.rc)

    # ---- THE IDENTITY GATE (a), both ways ----
    r = run_case("IA1-config-names-card0", scen={"config_card": 0}, env=PVT, timeout=60)
    ok(r.rc == 16 and "THE IDENTITY GATE (a) FAILED" in r.log and "stopped before any pass completed" in r.log and "/dev/et0_mgmt" in r.log
       and not r.calls.get("pvt") and nodev_calls(r) and manifest_ok(r)[0], "IA1 the start config read names /dev/et0_mgmt and ID 0 (card 0's form): exit 16, no probe, no sampler, no launch", r.log[-400:])
    ok(s20_reading(r)[0] == "RUN-ENDED GATE-STOPPED(16)", "IA1b step 10 reads it ended and stopped before any pass (16), with s20's own pattern", s20_reading(r))
    r = run_case("IA2-minion-mv-519", scen={"config_mv": 519}, env=PVT, timeout=60)
    ok(r.rc == 16 and "minion_mv 519, not below 510" in r.log and nodev_calls(r), "IA2 card 1's block but minion_mv 519 (card 0's): exit 16, no launch", r.log[-300:])
    r = run_case("IA3-config-split", scen={"config_split": True}, env=PVT, actions=[stop_after_identity], timeout=120)
    ok("identity (a): IDENT-A OK" in r.log and "runtime lines dropped 1" in r.log, "IA3 the runtime line INSIDE the config's JSON line: dropped, the identity read OK", r.log[:900])
    r = run_case("IA4-config-busy-once", scen={"config_fail_on_call": 1}, env=PVT, actions=[stop_after_identity], timeout=120)
    ok("one more read in 3 s" in r.log and "identity (a): IDENT-A OK" in r.log and os.path.exists(os.path.join(r.outd, "config-start-try1.err")),
       "IA4 no config came back once (a busy node): ONE more read, then the identity read OK", r.log[:900])
    r = run_case("IA5-config-busy-twice", scen={"config_fail_on_call": [1, 2]}, env=PVT, timeout=60)
    ok(r.rc == 16 and "THE IDENTITY GATE (a) FAILED" in r.log and nodev_calls(r) and not r.calls.get("pvt"), "IA5 no config twice: exit 16, no launch", r.log[-300:])
    rr = rest_read("IA5")
    ok(rr[0] == 3, "IA5b the rest rule counts a session ended at the identity gate (a card command was sent)", rr[1][:200])

    # ---- THE IDENTITY GATE (b), both ways ----
    r = run_case("IB1-ours-on-card0", scen={"etwho_lines_on_call": {"3": ["/dev/et0_mgmt {me} 31337 ettelem"]}}, env=PVT, timeout=120)
    ok(r.stop and r.stop.get("by") == "gate_e199" and "identity gate (b)" in r.stop.get("why", "") and "card 0" in r.stop.get("why", "")
       and nodev_calls(r), "IB1 a holder line of ours on card 0 with the sampler running: the gate (b) STOPs before any launch", (r.rc, r.stop))
    r = run_case("IB2-second-card-holder", scen={"etwho_lines_on_call": {"3": ["/dev/et0_ops otheruser 4242 foo_host"]}}, env=PVT, timeout=120)
    ok(r.stop and "identity gate (b)" in r.stop.get("why", "") and "another login" in r.stop.get("why", "") and nodev_calls(r),
       "IB2 a second card's holder (another login on card 0) with the sampler running: the gate (b) STOPs before any launch", (r.rc, r.stop))
    r = run_case("IB3-sampler-holds-nothing", scen={"sampler_no_hold": True}, env=PVT, timeout=120)
    ok(r.stop and "identity gate (b)" in r.stop.get("why", "") and "/dev/et1_mgmt" in r.stop.get("why", "") and nodev_calls(r) and r.rc == 8,
       "IB3 no holder line of ours on /dev/et1_mgmt (the sampler holds nothing): the gate (b) STOPs, exit 8, no launch", (r.rc, r.stop))
    ok(s20_reading(r)[0] == "RUN-ENDED GATE-STOPPED(16)", "IB3b step 10 reads it stopped before any pass (16)", s20_reading(r))

    # ---- THE WATCH on every host ----
    r = run_case("W1-host-names-card0", scen={"host_card_from": {"n": 5, "card": 0}}, env=PVT, timeout=300)
    ok(r.stop and r.stop.get("by") == "gate_e199" and "the watch" in r.stop.get("why", "") and "/dev/et0_ops" in r.stop.get("why", "")
       and count(r, "host") == 5 and r.rc == 8, "W1 the 5th host process names card 0 on its stderr: the watch STOPs; no 6th host process; exit 8", (r.rc, count(r, "host"), r.stop))
    r = run_case("W2-host-holds-card0", scen={"host_hold_from": {"n": 5, "node": "/dev/et0_ops"}}, env=PVT, timeout=300)
    ok(r.stop and "the watch" in r.stop.get("why", "") and "holds /dev/et0_ops" in r.stop.get("why", "") and count(r, "host") == 5,
       "W2 the 5th host process holds /dev/et0_ops: the watch STOPs; no 6th host process", (r.rc, count(r, "host"), r.stop))
    r = run_case("W3-smoke-heater-names-card0", scen={"heater_card": 0}, env=PVT, timeout=120)
    ok(r.stop and "the watch" in r.stop.get("why", "") and count(r, "host") == 0 and "stopped before any pass completed" in r.log,
       "W3 the smoke's heater check names card 0: the watch STOPs before any host run", (r.rc, count(r, "host"), r.stop))

    # ---- card 1's live stop lines ----
    r = run_case("LS1-board-65", scen={"host_w_from": {"n": 4, "w": 66.0}}, env=PVT, timeout=300)
    st_t = (r.stop or {}).get("t_ms", 0)
    nd = no_device_after(r, st_t)
    ok(r.stop and r.stop.get("by") == "gate_e199" and "card 1's live stop: board" in r.stop.get("why", "") and nd[0] and r.rc == 8,
       "LS1 a board reading at or above 65 W (below stopwatch's 80 W): card 1's live stop; no device process after it; exit 8", (r.rc, r.stop, nd[1]))
    r = run_case("LS2-die-70", scen={"host_tss_from": {"n": 4, "tss": 76.0}}, env=PVT, timeout=300)
    st_t = (r.stop or {}).get("t_ms", 0)
    ok(r.stop and "70" in r.stop.get("why", "") and no_device_after(r, st_t)[0] and r.rc in (6, 8),
       "LS2 minshire[0] at or above 70 C: a stop (card 1's line, stopwatch's or the block's), no device process after it", (r.rc, r.stop))

    r = run_case("S3-sampler-quiet", scen={"stall_after_s": 45}, env=PVT, timeout=300)
    ok(r.stop and ("old" in r.stop.get("why", "") or "telemetry" in r.stop.get("why", "")) and r.rc in (4, 8),
       "S3 the sampler gone quiet: a stale-telemetry stop (the block's 5 s or stopwatch's 10 s), no device process after it", (r.rc, r.stop))
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(len(ends) == 1, "S3b the quiet sampler still ended by SIGTERM", ends)
    r = run_case("HC-heater-above-65", scen={"heater_w": 66.0}, env=PVT, timeout=120)
    ok(r.stop and "card 1's live stop: board" in r.stop.get("why", "") and count(r, "host") == 0 and r.rc == 8,
       "HC the smoke's heater check reading 66 W (under the registered 70 W ceiling): card 1's 65 W live stop first, no host run (on card 1 the 65 W line binds before the 70 W ceiling)", (r.rc, r.stop))

    # ---- the smoke gate, the cap, the gate's death, a signal, a runtime line inside a host line ----
    r = run_case("G1-smoke-gate", scen={"check_bad_arm": "add.a.f2", "check_bad_upto": 3}, env=PVT, timeout=180)
    ok(r.stop and r.stop.get("by") == "gate_e199" and "smoke gate: add.a.f2" in r.stop.get("why", "") and r.rc == 8 and count(r, "host") == 3,
       "G1 a smoke run with check_bad: the kit's smoke gate writes STOP, exit 8, no pass-0 device process", (r.rc, r.stop))
    r = run_case("G2a-cap-before-pass0", env=dict(PVT, E199_CAP_S="300"), timeout=180)
    ok(r.stop and "cap: pass 0 could end after the cap" in r.stop.get("why", "") and count(r, "host") == 3 and r.rc == 8,
       "G2a the cap read before pass 0 (D0 400 s, cap 300 s): STOP, no pass-0 device process", (r.rc, r.stop))

    def kill_gate(r):
        if gate_ev(r, "smoke_gate"):
            for ln in text(os.path.join(r.outd, "session.log")).splitlines():
                if "gate_e199.py (pid " in ln:
                    os.kill(int(ln.split("gate_e199.py (pid ")[1].split(")")[0]), signal.SIGKILL)
                    return True
        return False
    r = run_case("G4-gate-dies", env=PVT, actions=[kill_gate], timeout=180)
    ok(r.stop and r.stop.get("by") == "session_e199" and "gate watcher is gone" in r.stop.get("why", "") and r.rc == 8,
       "G4 the gate watcher killed: the wrapper writes STOP, exit 8", (r.rc, r.stop))

    def term_wrapper(r):
        if count(r, "host") >= 5:
            os.kill(r.pid, signal.SIGTERM)
            return True
        return False
    r = run_case("T-signal", env=PVT, actions=[term_wrapper], timeout=240)
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(r.stop and "a signal to the wrapper" in r.stop.get("why", "") and r.rc == 8 and "session end (T0" in r.log and ends and manifest_ok(r)[0],
       "T SIGTERM to the wrapper: STOP, the run in flight finishes, the end read, session end, manifest, the sampler by SIGTERM", (r.rc, r.stop))
    r = run_case("RT1-runtime-line-inside", scen={"runtime_inside": {"n": 4, "offset": 20}}, env=PVT, timeout=240)
    rs_out = text(os.path.join(r.outd, "run_session.out"))
    ok(r.rc == 1 and "JSONDecodeError" in rs_out and len(r.runs) == sum(c.get("launches", 0) for c in r.calls.get("host", []) if c.get("n", 0) <= 3)
       and all(x.get("pass") == -1 for x in r.runs), "RT1 the runtime line INSIDE a host's first INTBITS line: run_block.py raises, the block and the session stop (rc 1); no record of that run, no wrong record", (r.rc, len(r.runs), rs_out[-200:]))
    r = run_case("B7-holder-at-run-session-check", scen={"etwho_lines_on_call": {"2": ["/dev/et1_ops otheruser 4242 foo_host"]}}, env=PVT, timeout=120)
    sd_ = text(os.path.join(r.outd, "run", "SESSION_DONE"))
    ok(r.rc == 3 and '"by": "session_e199"' in sd_ and r.elapsed < 60 and not [c for c in r.calls.get("pvt", []) if c.get("event") == "start" and "--probe" not in c.get("argv", [])],
       "B7 run_session.sh's own free check refuses after the first card command: the wrapper writes SESSION_DONE, the session ends at once", (r.rc, sd_[:120], r.elapsed))

    # ---- refusals before anything (exit 2, no device opened) ----
    def refused(r, what):
        return r.rc == 2 and "no device opened" in r.log and what in r.log and not r.calls.get("sampler") and not r.calls.get("pvt") and nodev_calls(r)
    nested = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--unshare-uts", "--hostname", "aifoundry3", "--die-with-parent", "--"]
    r = run_case("R1-hostname", env=PVT, wrap=nested, timeout=60)
    ok(refused(r, "not aifoundry1"), "R1 another host's name (aifoundry3): refused before anything", r.log[-300:])
    r = run_case("R2-desk-variable", env={"E199_DESKTEST": None, "E199_CAP_S": "100"}, timeout=60)
    ok(refused(r, "desk-test variable"), "R2 a desk-test variable without E199_DESKTEST=1: refused", r.log[-300:])
    r = run_case("R3-kitlist", env=dict(PVT, E199_KITLIST_SHA256="0" * 64), timeout=60)
    ok(refused(r, "the kit's list is not at the sha256"), "R3 the kit's list off the sha256 the runbook passed: refused", r.log[-300:])
    rb = os.path.join(R, E2, "proposal/src/run_block.py")
    keep = open(rb, "rb").read()
    open(rb, "ab").write(b"\n")
    r = run_case("R4-registered-file", env=PVT, timeout=60)
    open(rb, "wb").write(keep)
    ok(refused(r, "registered session file of E192's is off its sha256"), "R4 E192's run_block.py one byte longer: refused", r.log[-300:])
    r = run_case("R5-reader-pin", env=dict(PVT, E199_READER_SHA256="1" * 64), timeout=60)
    ok(refused(r, "is not at E191's pin"), "R5 the reader off its pin: refused", r.log[-300:])
    hp_ = os.path.join(TREE, "build/sparsity/host/sparsity_host")
    shim(hp_, "heater", selection=False)
    r = run_case("R6-heater-no-selection", env=PVT, timeout=60)
    shim(hp_, "heater")
    ok(refused(r, "does not carry ET_DEVICES"), "R6 the heater without ET_DEVICES: refused before anything (never after a card command)", r.log[-300:])
    r = run_case("R7-no-card1-lock-file", env=PVT, lock=False, timeout=60)
    ok(refused(r, "no card lock file /run/lock/etsoc-shire1.lock"), "R7 no card 1 lock file: refused", r.log[-300:])
    r = run_case("R8-no-deadline", env=dict(PVT, E199_DEADLINE_EPOCH=None), timeout=60)
    ok(refused(r, "no E199_DEADLINE_EPOCH"), "R8 no deadline: refused", r.log[-300:])
    r = run_case("N1-card1-nodes-only", env=PVT, wrap=nest(["et1_ops", "et1_mgmt"]), timeout=60)
    ok(refused(r, "not exactly aifoundry1's two cards"), "N1 only card 1's two node names (a private /dev on the box): refused at the node count", r.log[-300:])
    r = run_case("N2-three-nodes", env=PVT, wrap=nest(["et0_mgmt", "et1_ops", "et1_mgmt"]), timeout=60)
    ok(refused(r, "not exactly aifoundry1's two cards"), "N2 three node names (no /dev/et0_ops): refused at the node count", r.log[-300:])
    # run_session.sh alone (E192's, as committed): its own selection refusals, now runnable at the desk (character stand-in nodes)
    r = run_case("N3-run-session-no-selection", env={"ET_DEVICES": None}, direct=True, timeout=60)
    ok(r.rc == 2 and "2 cards on this host and ET_DEVICES unset" in r.rlog and nodev_calls(r) and not r.calls.get("sampler"),
       "N3 run_session.sh alone, two cards, ET_DEVICES unset: its own refusal (exit 2), nothing opened", r.rlog[-200:])
    noh = os.path.join(S, "nohonour", "intbits_host")
    shim(noh, "host", selection=False)
    r = run_case("N4-run-session-host-ignores", env={"ET_DEVICES": "1", "H": noh}, direct=True, timeout=60)
    ok(r.rc == 2 and "does not honour ET_DEVICES" in r.rlog and nodev_calls(r), "N4 run_session.sh alone, ET_DEVICES=1, a host binary without the selection: its refusal (line 65; E192's kit could not run it)", r.rlog[-200:])
    r = run_case("N5-run-session-et1-not-a-node", env={"ET_DEVICES": "1"}, direct=True, wrap=nest(["et0_ops", "et0_mgmt", "et1_mgmt"], files=["et1_ops"]), timeout=60)
    ok(r.rc == 2 and "no /dev/et1_ops" in r.rlog and nodev_calls(r), "N5 run_session.sh alone, ET_DEVICES=1 with /dev/et1_ops not a character node: its refusal", r.rlog[-200:])

    # ---- Z ----
    time.sleep(2)
    left = [d for d in os.listdir("/proc") if d.isdigit() and int(d) not in (1, os.getpid()) and
            any(w.endswith("standin_e199.py") or w.endswith("session_e199.sh") or w.endswith("gate_e199.py")
                for w in [x.decode(errors="ignore") for x in open("/proc/%s/cmdline" % d, "rb").read().split(b"\0")])]
    ok(not left and not os.path.exists(os.path.join(S, "network-calls.log")), "Z no process of the test left; no network call", left)
    print("\nDESKTEST-REALPATH-E199 %d of %d PASS%s" % (npass, ncase, "" if not fails else "; FAILED: " + ", ".join(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
