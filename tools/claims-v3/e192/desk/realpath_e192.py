#!/usr/bin/env python3
"""E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE REAL-PATH DESK TEST's cases (run by
desk/desktest_realpath_e192.sh inside its sandbox; never run it outside one). It builds a stand-in aifoundry3 tree in the scratch
directory (E192's root R = <tree>/build/claims-v3/aifoundry3/e192 holding boxfiles-e192.txt's files as the sync puts them; the box's
sampler, heater and the host as stand-ins), then runs session_e192.sh's REAL path (DRY unset) case by case, with actions a person or the
card could take mid-session (a stop by hand, the card lock taken, a holder, a dead gate, a signal), and reads what it wrote. Nothing here
opens a device; nothing is measured. Each case's numbers are the stand-ins' (desk/standin_e192.py), never the card's.
fix-e192 (Q176, Sat 14 Nov 2026 evening, before the land) added the cases after R8: verify-e192's break cases (B1-B11, W1-W2, F0) with
its stand-in knobs, the wrapper's two fixes (the node count before the probe; SESSION_DONE when run_session.sh exits before its EXIT trap),
run_session.sh's own refusals run alone, the gate's smoke-order condition, the heater check with no board reading, the probe's lock taken,
the per-sensor sampler off its pin and the per-sensor chain NO-GO, and no deadline variable.
    /usr/bin/python3 -I -B realpath_e192.py <repo top> <scratch dir>
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
E = "tools/claims-v3/e192"
STANDIN = os.path.join(SRC, E, "desk/standin_e192.py")
TABLE = os.path.join(SRC, E, "desk/arm-table-e192.jsonl")
BOX = os.path.join(S, "box")
TREE = os.path.join(BOX, "aifoundry")
RR = "build/claims-v3/aifoundry3/e192"
R = os.path.join(TREE, RR)
SBIN = os.path.join(S, "sbin")
LOCK = "/run/lock/etsoc-shire0.lock"
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


def shim(path, role):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("#!/bin/bash\nexec %s -I -B %s %s \"$@\"\n" % (PY, STANDIN, role))
    os.chmod(path, 0o755)


def setup():
    os.makedirs(R, exist_ok=True)
    files = [ln.strip() for ln in open(os.path.join(SRC, E, "boxfiles-e192.txt")) if ln.strip() and not ln.startswith("#")]
    for p in files:
        if p.endswith("SHA256SUMS-e192-kit") and not os.path.exists(os.path.join(SRC, p)):
            continue
        os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
        shutil.copy2(os.path.join(SRC, p), os.path.join(R, p))
    # the kit's list: a stand-in made here from R's copies (the real list holds this test's log); the session reads its sha256
    kl = os.path.join(R, E, "SHA256SUMS-e192-kit")
    reg = {ln.split()[1] for ln in open(os.path.join(R, E, "SHA256SUMS-e192-registration")) if ln.strip()}
    rows = []
    for root, _, fs in os.walk(os.path.join(R, E)):
        for fn in fs:
            p = os.path.relpath(os.path.join(root, fn), R)
            if p in reg or p.endswith("SHA256SUMS-e192-kit") or p.endswith("SHA256SUMS-e192-registration"):
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
    return sha(kl), pvt, sha(pvt)


def new_t0():
    t = max(int(time.time()), _last_t0[0] + 1)
    _last_t0[0] = t
    return t


def base_env(sd, extra):
    env = {"PATH": SBIN + ":/usr/local/bin:/usr/bin:/bin", "HOME": BOX, "USER": ME, "LOGNAME": ME, "LANG": "C.UTF-8",
           "TZ": "America/Los_Angeles", "E192_STANDIN_DIR": sd, "E192_STANDIN_TABLE": TABLE,
           "E192_KITLIST_SHA256": KLS, "E192_DEADLINE_EPOCH": str(int(time.time()) + 7200)}
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
    r.outd = os.path.join(TREE, "build/e192/T%d%s" % (t0, "-dry" if dry else ""))
    if direct:
        r.outd = os.path.join(S, "direct", name)
        os.makedirs(r.outd, exist_ok=True)
    rundir = os.path.join(r.outd, "run") if not direct else os.path.join(r.outd, "run")
    open(os.path.join(sd, "rundir"), "w").write(rundir + "\n")
    e = base_env(sd, dict(env or {}, E192_T0=str(t0)))
    if direct:
        e.update({"SAMPLER": "ettelem", "ETTELEM": os.path.join(TREE, "build/ettelem/ettelem"),
                  "HEATER": os.path.join(TREE, "build/sparsity/host/sparsity_host"),
                  "H": os.path.join(R, "build/intbits/host/intbits_host")})
        cmd = ["bash", os.path.join(R, E, "proposal/src/run_session.sh"), rundir, "9"]
    else:
        cmd = ["bash", os.path.join(R, E, "session_e192.sh")] + (["--dry"] if dry else [])
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
    for ln in open(os.path.join(SRC, E, "desk/order-e192-aifoundry3.txt")):
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
    """step 10's reading of the wrapper's log, with the gate-stop pattern read from rb/s20_wait_e192.sh itself: (reading, pattern)."""
    src = text(os.path.join(SRC, E, "rb/s20_wait_e192.sh"))
    m = re.search(r"if grep -qE '([^']+)' \"\$L\" 2>/dev/null; then echo \"GATE-STOPPED", src)
    pat = m.group(1) if m else None
    ended = ("session end (T0 %d)" % r.t0) in r.log
    gate = bool(pat) and bool(re.search(pat, r.log))
    return ("RUN-ENDED" if ended else "RUN-NOT-ENDED") + (" GATE-STOPPED(16)" if gate else " (0)"), pat


def rest_read(label):
    """the kit's rest rule (rb/rest_rule_e192.sh) as step 9 sends it, run from the stand-in box's tree."""
    p = subprocess.run(["bash", os.path.join(SRC, E, "rb/rest_rule_e192.sh")], cwd=TREE,
                       env={"HOME": BOX, "PATH": "/usr/bin:/bin", "TZ": "America/Los_Angeles"}, capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip().replace("\n", " | ")
    print("   rest rule after %s: rc %d: %s" % (label, p.returncode, out[:300]), flush=True)
    return p.returncode, out


def nest(devnames):
    """a nested sandbox for one case: a fresh private /dev holding only the named regular files (no device node); all else as here."""
    w = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev"]
    for d in devnames:
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
    global KLS
    print("E192 real-path desk test (kit-e192), %s; Python %s; the scratch %s" % (
        time.strftime("%F %T %Z"), sys.version.split()[0], "<scratch>"), flush=True)
    KLS, pvt, pvt_sha = setup()
    PVT = {"E192_DESKTEST": "1", "E192_PVT_SAMPLE": pvt, "E192_PVT_SHA256": pvt_sha}
    ORD = order()
    # ---- 0: the sandbox and the stand-in box ----
    print("\n== 0 the sandbox and the stand-in box", flush=True)
    import socket
    ok(socket.gethostname() == "aifoundry3", "0a the host's name is aifoundry3 in the sandbox")
    devs = sorted(d for d in os.listdir("/dev") if d.startswith("et"))
    ok(devs == ["et0_mgmt", "et0_ops"] and all(os.path.isfile("/dev/" + d) and not __import__("stat").S_ISCHR(os.stat("/dev/" + d).st_mode) for d in devs),
       "0b /dev holds only et0_ops and et0_mgmt, each a regular file (no device node)", devs)
    ok(len([d for d in os.listdir("/proc") if d.isdigit()]) < 40, "0c a private PID namespace (few processes visible)")
    pf = subprocess.run(["bash", os.path.join(R, E, "preflight_e192.sh")], capture_output=True, text=True, cwd=S)
    ok(pf.returncode == 0 and "PLAIN-CHAIN: GO" in pf.stdout and "PVT-CHAIN: GO" in pf.stdout,
       "0d the box copy's preflight: the plain chain GO (the stock table), the per-sensor chain GO (E144's table)", pf.stdout[-300:])
    # ---- D: the dry path ----
    r = run_case("D-dry", dry=True, timeout=120)
    ok(r.rc == 0 and "E192-DRY OK: 328 device calls" in r.log, "D1 --dry: rc 0, the dry listing 328 device calls in the registered order", r.log[-400:])
    ok(r.outd.endswith("-dry") and "; DRY)" in r.log.splitlines()[0] and all(" DRY " in ln for ln in r.log.splitlines()),
       "D2 the dry log: the T<T0>-dry directory, 'session start (...; DRY)', every line DRY (every rest rule skips it)")
    ok(not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host", "etwho", "ps")), "D3 no stand-in tool was called (nothing opened)", {k: len(v) for k, v in r.calls.items()})
    m = manifest_ok(r)
    ok(m[0], "D4 MANIFEST.sha256 written last and exact", m[1])

    # ---- P: the real path, the per-sensor sampler, a stop by hand in the gap after pass 1 ----
    def stop_after_pass1(r):
        if marks_after(r, 1):
            write_stop(r, "desk test: by hand, in the gap after pass 1")
            return True
        return False
    r = run_case("P-realpath", env=PVT, actions=[stop_after_pass1], timeout=1500)
    P = r
    ok(r.rc == 0 and not r.timed_out, "P1 rc 0 (a stop by hand between passes ends the session normally)", r.rc)
    ok("sampler: pvt (its probe answered" in r.log, "P2 the per-sensor probe answered: SAMPLER=pvt", r.log[:600])
    probe = [c for c in r.calls.get("pvt", []) if c.get("event") == "probe_end"]
    pstart = [c for c in r.calls.get("pvt", []) if c.get("event") == "start"]
    ok(len(probe) == 1 and len(pstart) == 2 and pstart[0].get("lock_held") is True and "--probe" in pstart[0].get("argv", []),
       "P3 the first card command is the probe, under the card lock; then ONE sampler for the session", pstart)
    ok(pstart[-1].get("argv") == ["--seconds", "6000", "--every-ms", "100"], "P4 the session's sampler: --seconds 6000 --every-ms 100", pstart[-1].get("argv"))
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") in ("exit_on_sigterm", "exit_at_seconds")]
    ok(len(ends) == 1 and ends[0]["event"] == "exit_on_sigterm", "P5 the sampler stopped by SIGTERM (never killed), once", ends)
    sg = gate_ev(r, "smoke_gate")
    ok(len(sg) == 1 and sg[0].get("verdict") == "GO" and [x["arm"] for x in sg[0]["runs"] if "arm" in x] == ["nop", "add.a.f2", "add.cr.l31"],
       "P6 the kit's smoke gate read the smoke's three runs' INTBITS lines: GO", sg)
    hc = [m for m in r.marks if m.get("kind") == "heater_level"]
    hcr = [m for m in r.marks if m.get("kind") == "heater_check"]
    ok(len(hc) == 1 and hc[0].get("board_max_w") is not None and 45 < hc[0]["board_max_w"] < 70 and hcr and hcr[0].get("rc") == 0,
       "P7 the smoke's heater check: the heater ran (exit 0, its board level read) and stayed below 70 W", (hc, hcr))
    for p in (0, 1):
        runs = by_seq(r, p)
        arms = [x[0]["arm"] for x in runs]
        ok(arms == ORD[p], "P8.%d pass %d: 36 runs in the registered order for aifoundry3" % (p, p), (len(arms), arms[:5]))
        nl = [len(x) for x in runs]
        ok(bool(nl) and min(nl) >= 8 and all(all(y["ok"] and y["check_bad"] == 0 and y["participants"] == 1024 for y in x) for x in runs),
           "P9.%d pass %d: every run 8 or more INTBITS lines (4 s of 0.4 s launches), every launch ok" % (p, p), (min(nl) if nl else 0, max(nl) if nl else 0))
    ap_on = sum(1 for x in r.runs if x.get("pass", -1) >= 0 and x.get("approach", {}).get("on_protocol"))
    ok(ap_on > 0.8 * len([x for x in r.runs if x.get("pass", -1) >= 0]), "P10 the approach ran (heater launches, the wait, the quiet): most launches on protocol", ap_on)
    hcalls = [c for c in r.calls.get("host", []) if c.get("event") == "call"]
    ok(len(hcalls) == 3 + 36 * 2 and all(c.get("lock_held") is True for c in hcalls), "P11 75 host processes (smoke 3, passes 36 each), every one with the card lock held", len(hcalls))
    ok(all(c["argv"][c["argv"].index("--window") + 1] == "240000000" and c["argv"][-2] == "--stop-file" for c in hcalls)
       and sorted({c["argv"][c["argv"].index("--seconds") + 1] for c in hcalls}) == ["2", "4"], "P12 every host run --window 240000000, --seconds 2 (smoke) or 4, --stop-file")
    heats = [c for c in r.calls.get("heater", []) if c.get("event") == "call"]
    ok(len(heats) >= 2 and all(c.get("lock_held") is True for c in heats), "P13 the heater ran under the card lock (the check and the approach)", len(heats))
    ok(r.stop and r.stop.get("by") == "hand" and "STOP:" in r.rlog and "passes complete: 2 of 9" in r.log, "P14 the stop by hand was honoured after the gap: 2 passes complete", r.log[-500:])
    cn = [g.get("next_pass") for g in gate_ev(r, "cap_ok")]
    ok(cn[:2] == [0, 1] and len(cn) <= 3 and gate_ev(r, "stop_seen"), "P15 the cap read before passes 0 and 1, each within it (pass 2's read is moot once the stop by hand exists: the gate sees it and ends)", cn)
    m = manifest_ok(r)
    ok(m[0] and text(os.path.join(r.outd, "wrapper.rc")).strip() == "0" and "session end (T0 %d)" % r.t0 in r.log, "P16 session end, MANIFEST exact, wrapper.rc 0", m[1])
    ew = [c for c in r.calls.get("etwho", [])]
    ok(len(ew) >= 5 and ew[0].get("holders") == 0 and any(c.get("holders") == 1 for c in ew), "P17 et-who before anything (no holder) and with the sampler (our own holder only)", [c.get("holders") for c in ew])
    red = subprocess.run([PY, "-I", "-B", os.path.join(SRC, E, "proposal/src/reduce_intbits.py"), os.path.join(r.outd, "run"),
                          "--out", os.path.join(S, "P-intbits.json")], capture_output=True, text=True)
    rj = json.load(open(os.path.join(S, "P-intbits.json"))) if red.returncode == 0 else {}
    ok(red.returncode == 0 and rj, "P18 the registered reducer reads the real path's files (stand-in numbers): rc 0", red.stderr[-300:])
    chk = os.path.join(SRC, E, "check_e192.py")
    if os.path.exists(chk):
        c = subprocess.run([PY, "-I", "-B", chk, os.path.join(r.outd, "run"), os.path.join(S, "P-intbits.json"), "--out",
                            os.path.join(S, "P-checks.json")], capture_output=True, text=True)
        ok(c.returncode == 0 and "CHECKS-E192" in c.stdout, "P19 the section 7 checker reads them: rc 0", c.stdout[-300:] + c.stderr[-300:])

    # ---- FB / FE: the fallbacks ----
    def stop_after_go(r):
        if gate_ev(r, "smoke_gate"):
            write_stop(r, "desk test: by hand after the smoke gate")
            return True
        return False
    r = run_case("FB-real-pvt-sample", actions=[stop_after_go], timeout=240)
    ok("sampler: ettelem (the fallback: the per-sensor probe exited" in r.log and any(c.get("event") == "start" for c in r.calls.get("sampler", [])),
       "FB1 the real pvt_sample.py's probe cannot open a card here: the plain sampler, the fallback", r.log[:700])
    ok([c["argv"] for c in r.calls.get("sampler", []) if c.get("event") == "start"] == [["sample", "--seconds", "6000", "--every-ms", "100"]],
       "FB2 the plain sampler: ettelem sample --seconds 6000 --every-ms 100, no statistics reset")
    ok("stopped before any pass completed" in r.log and r.rc == 8 and count(r, "host") == 3, "FB3 the stop by hand after the smoke: rc 8, no pass ran, 3 host runs", (r.rc, count(r, "host")))
    r = run_case("FE-plain-by-go", env=dict(PVT, E192_SAMPLER="ettelem"), actions=[stop_after_go], timeout=240)
    ok("his go named the plain sampler" in r.log and not r.calls.get("pvt") and r.calls.get("sampler"), "FE1 E192_SAMPLER=ettelem: no probe, the plain sampler", r.log[:600])

    # ---- the free check and the holders ----
    r = run_case("H1-holder-at-start", scen={"etwho": "foreign"}, env=PVT, timeout=60)
    ok(r.rc == 3 and "no device opened" in r.log and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host")),
       "H1 a holder at the start: exit 3, nothing opened", (r.rc, list(r.calls)))
    r = run_case("H2-foreign-process", scen={"foreign_proc": True}, env=PVT, timeout=60)
    ok(r.rc == 3 and "device process(es) of another user" in r.log and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host")),
       "H2 another user's device process: exit 3, nothing opened", r.rc)
    hp = hold_lock(25)
    t_w = time.time()
    while not os.path.exists(os.path.join(S, "holder.flag")) and time.time() - t_w < 10:
        time.sleep(0.1)
    r = run_case("H3-lock-held-at-start", env=PVT, timeout=60)
    hp.terminate(); hp.wait()
    os.unlink(os.path.join(S, "holder.flag"))
    ok(r.rc == 3 and "the card lock is held" in r.log and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host")),
       "H3 the card lock held at the start: exit 3, nothing opened", r.rc)
    r = run_case("H4-holder-between-passes", scen={"etwho": "foreign_after_pass0", "scale": 0.25}, env=PVT, timeout=700)
    ok(r.rc == 3 and "pass 1: the card is not free, stopping" in r.rlog and "passes complete: 1 of 9" in r.log, "H4 a holder between passes: the session stops before pass 1 (exit 3)", r.rlog[-300:])
    t_end0 = max((m["t1_ms"] for m in r.marks if m.get("pass") == 0 and m.get("label") == "after"), default=0)
    nd = no_device_after(r, t_end0)
    ok(nd[0], "H4b no device process after pass 0's end", nd[1])

    def take_lock_when_tel(r):
        if os.path.exists(os.path.join(r.outd, "run", "telemetry.jsonl")):
            r.holder = hold_lock(40)
            return True
        return False
    r = run_case("L-lock-taken-after-sampler", env=PVT, actions=[take_lock_when_tel], timeout=120)
    if getattr(r, "holder", None):
        r.holder.terminate(); r.holder.wait()
    if os.path.exists(os.path.join(S, "holder.flag")):
        os.unlink(os.path.join(S, "holder.flag"))
    ok(r.rc == 75 and "smoke: exit 75 (card lock busy), no pass runs" in r.rlog and count(r, "host") == 0 and count(r, "heater") == 0,
       "L the card lock taken after the sampler started: the smoke's lock busy, exit 75, nothing run", (r.rc, r.rlog[-200:]))
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(len(ends) == 1, "Lb the sampler still stopped by SIGTERM", ends)

    # ---- the live stops ----
    r = run_case("S1-board-stop", scen={"host_w_from": {"n": 6, "w": 85.0}}, env=PVT, timeout=300)
    st_t = (r.stop or {}).get("t_ms", 0)
    ok(r.stop and r.stop.get("by") == "stopwatch" and "above 80 W on 3 distinct readings" in r.stop.get("why", ""), "S1 board above 80 W on 3 distinct readings: stopwatch writes STOP", r.stop)
    h6 = [c for c in r.calls.get("host", []) if c.get("n", 0) >= 6 and "launches" in c]
    lastl = max((x["t_start_ms"] for x in r.runs), default=0)
    ok(r.rc == 8 and h6 and h6[0].get("stop_at_end") is True and lastl <= st_t + 50, "S1b the host saw the stop file and launched nothing after it; the block exits 8", (r.rc, lastl - st_t))
    nd = no_device_after(r, st_t)
    ok(nd[0] and "stopped before any pass completed" in r.log, "S1c no device process after the stop; no pass complete", nd[1])
    r = run_case("S2-die-stop", scen={"host_tss_from": {"n": 6, "tss": 76.0}}, env=PVT, timeout=300)
    ok(r.stop and ("at or above 70 C" in r.stop.get("why", "") or "70 C" in r.stop.get("why", "")) and r.rc in (6, 8), "S2 a die reading at or above 70 C stops the session (stopwatch or the block)", (r.rc, r.stop))
    r = run_case("S3-sampler-quiet", scen={"stall_after_s": 45}, env=PVT, timeout=300)
    ok(r.stop and ("old" in r.stop.get("why", "")) and r.rc in (4, 8), "S3 the sampler gone quiet: a stale-telemetry stop (the block's 5 s or stopwatch's 10 s)", (r.rc, r.stop))
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(len(ends) == 1, "S3b the quiet sampler still ended by SIGTERM", ends)
    r = run_case("HC-heater-check", scen={"heater_w": 72.0}, env=PVT, timeout=120)
    ok(r.rc == 9 and "heater board reading" in (r.stop or {}).get("why", "") and count(r, "host") == 0, "HC the smoke's heater check above 70 W: exit 9, no host run", (r.rc, r.stop))

    # ---- the kit's gates ----
    r = run_case("G1-smoke-gate", scen={"check_bad_arm": "add.a.f2", "check_bad_upto": 3}, env=PVT, timeout=180)
    ok(r.stop and r.stop.get("by") == "gate_e192" and "smoke gate: add.a.f2" in r.stop.get("why", "") and r.rc == 8,
       "G1 a smoke run with check_bad: the kit's smoke gate writes STOP, exit 8", (r.rc, r.stop))
    ok(count(r, "host") == 3 and count(r, "heater") == 1 and "stopped before any pass completed" in r.log, "G1b no pass-0 device process (3 smoke runs, the heater check only)", (count(r, "host"), count(r, "heater")))

    def stop_when_pass0_starts(r):
        if count(r, "host") >= 4 or count(r, "heater") >= 2:
            write_stop(r, "desk test: the negative control is stopped by hand once pass 0 has begun")
            return True
        return False
    r = run_case("N1-reference-alone", scen={"check_bad_arm": "add.a.f2", "check_bad_upto": 3}, actions=[stop_when_pass0_starts], timeout=240, direct=True)
    ok(count(r, "host") >= 4 or count(r, "heater") >= 2, "N1 THE NEGATIVE CONTROL: the reference session alone runs into pass 0 after the same failed smoke run", (count(r, "host"), count(r, "heater")))
    r = run_case("G2a-cap-before-pass0", env=dict(PVT, E192_CAP_S="300"), timeout=180)
    ok(r.stop and r.stop.get("by") == "gate_e192" and "cap: pass 0 could end after the cap" in r.stop.get("why", "") and count(r, "host") == 3 and r.rc == 8,
       "G2a the cap read before pass 0 (D0 400 s, cap 300 s): STOP, no pass-0 device process", (r.rc, r.stop))
    r = run_case("G2b-cap-hard", env=dict(PVT, E192_CAP_S="100", E192_D0_S="10"), timeout=240)
    first = int(text(os.path.join(r.outd, "first-card-command.txt")).strip() or 0)
    mtime = os.path.getmtime(os.path.join(r.outd, "MANIFEST.sha256")) if os.path.exists(os.path.join(r.outd, "MANIFEST.sha256")) else 0
    ok(r.stop and "s before the cap" in r.stop.get("why", "") and r.rc == 8, "G2b 30 s before the cap mid-pass: STOP, the run in flight finishes, exit 8", (r.rc, r.stop))
    ok(first and mtime - first <= 100 + 5, "G2c the session ended inside its cap (first card command to the manifest)", mtime - first)
    r = run_case("G2d-cap-between-passes", scen={"scale": 0.25}, env=dict(PVT, E192_CAP_S="330", E192_D0_S="10"), timeout=600)
    ok(r.stop and "cap: pass 1 could end after the cap" in r.stop.get("why", "") and "the longest pass so far" in r.stop.get("why", "")
       and "passes complete: 1 of 9" in r.log, "G2d the cap before pass 1 from the measured pass: STOP in the gap, 1 pass complete", (r.rc, r.stop))

    def kill_gate(r):
        if gate_ev(r, "smoke_gate"):
            for ln in text(os.path.join(r.outd, "session.log")).splitlines():
                if "gate_e192.py (pid " in ln:
                    os.kill(int(ln.split("gate_e192.py (pid ")[1].split(")")[0]), signal.SIGKILL)
                    return True
        return False
    r = run_case("G4-gate-dies", env=PVT, actions=[kill_gate], timeout=180)
    ok(r.stop and r.stop.get("by") == "session_e192" and "gate watcher is gone" in r.stop.get("why", "") and r.rc == 8,
       "G4 the gate watcher killed: the wrapper writes STOP, exit 8", (r.rc, r.stop))

    def term_wrapper(r):
        if count(r, "host") >= 5:
            os.kill(r.pid, signal.SIGTERM)
            return True
        return False
    r = run_case("T-signal", env=PVT, actions=[term_wrapper], timeout=240)
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(r.stop and "a signal to the wrapper" in r.stop.get("why", "") and r.rc == 8 and "session end (T0" in r.log and ends and manifest_ok(r)[0],
       "T SIGTERM to the wrapper: STOP, the run in flight finishes, session end, manifest, the sampler by SIGTERM", (r.rc, r.stop))

    # ---- refusals before anything ----
    def refused(r, what):
        return r.rc == 2 and "no device opened" in r.log and what in r.log and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host"))
    nested = ["/usr/bin/bwrap", "--dev-bind", "/", "/", "--unshare-uts", "--hostname", "aifoundry9", "--die-with-parent", "--"]
    r = run_case("R1-hostname", env=PVT, wrap=nested, timeout=60)
    ok(refused(r, "not aifoundry3"), "R1 another host's name: refused before anything", r.log[-300:])
    r = run_case("R2-user", env=dict(PVT, USER="nobody"), timeout=60)
    ok(refused(r, "USER is not this login"), "R2 USER not the login: refused", r.log[-200:])
    r = run_case("R3-desk-variable", env={"E192_CAP_S": "60"}, timeout=60)
    ok(refused(r, "desk-test variable"), "R3 a desk-test variable without E192_DESKTEST=1: refused", r.log[-200:])
    rb = os.path.join(R, E, "proposal/src/run_block.py")
    keep = open(rb, "rb").read()
    open(rb, "ab").write(b"\n")
    r = run_case("R4-pin", env=PVT, timeout=60)
    open(rb, "wb").write(keep)
    ok(refused(r, "off its sha256"), "R4 a registered session file one byte longer: refused", r.log[-200:])
    r = run_case("R5-kitlist", env=dict(PVT, E192_KITLIST_SHA256="0" * 64), timeout=60)
    ok(refused(r, "the kit's list is not at the sha256"), "R5 the kit's list off the runbook's sha256: refused", r.log[-200:])
    r = run_case("R6-deadline", env=dict(PVT, E192_DEADLINE_EPOCH=str(int(time.time()) + 600)), timeout=60)
    ok(refused(r, "would not start"), "R6 the cap passes the window's last end: refused", r.log[-200:])
    r = run_case("R7-no-lock-file", env=PVT, timeout=60, lock=False)
    ok(refused(r, "no card lock file"), "R7 no card lock file (never created by the session): refused", r.log[-200:])
    open(LOCK, "a").close()
    r = run_case("R8-sampler-word", env=dict(PVT, E192_SAMPLER="pvt"), timeout=60)
    ok(refused(r, "E192_SAMPLER may only be"), "R8 E192_SAMPLER other than ettelem: refused", r.log[-200:])

    # ==== fix-e192 (Q176, Sat 14 Nov 2026 evening, before the land): what verify-e192 found unrun, and the wrapper's two fixes ====
    r = run_case("R9-no-deadline", env=dict(PVT, E192_DEADLINE_EPOCH=None), timeout=60)
    ok(refused(r, "no E192_DEADLINE_EPOCH"), "R9 no deadline variable (the window's last end): refused before anything", r.log[-200:])

    # ---- the wrapper's node count, before the free check and the probe (verify-e192 finding 2): nested sandboxes ----
    for nm, devs, ex, what in (("W1-two-cards-pvt", ["et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt"], {}, "two cards, the per-sensor path"),
                               ("W2-two-cards-plain", ["et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt"], {"E192_SAMPLER": "ettelem"}, "two cards, the plain sampler by the go"),
                               ("F0-no-card-node", [], {}, "no card node"),
                               ("FM-no-mgmt-node", ["et0_ops"], {}, "et0_ops without et0_mgmt")):
        r = run_case(nm, env=dict(PVT, **ex), wrap=nest(devs), timeout=60)
        ok(refused(r, "not exactly /dev/et0_ops and /dev/et0_mgmt") and not r.calls.get("etwho") and not r.calls.get("ps") and r.elapsed < 30,
           "%s %s: the wrapper refuses at its node count (exit 2), before the free check and before any card command" % (nm.split("-")[0], what),
           (r.rc, r.log[-300:], list(r.calls)))

    # ---- run_session.sh's own refusals (lines 52-68), now behind the wrapper's checks, run alone (as N1 runs it) ----
    for nm, devs, ex, want in (("F0d-alone-no-node", [], {}, "refused: no /dev/et*_ops node on this host"),
                               ("W1d-alone-two-cards", ["et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt"], {}, "refused: 2 cards on this host and ET_DEVICES unset"),
                               ("WXd-alone-devices-word", None, {"ET_DEVICES": "x"}, "refused: ET_DEVICES must be one card index"),
                               ("W5d-alone-devices-1", ["et0_ops", "et0_mgmt", "et1_ops", "et1_mgmt"], {"ET_DEVICES": "1"}, "refused: no /dev/et1_ops")):
        r = run_case(nm, env=ex, wrap=(nest(devs) if devs is not None else None), timeout=60, direct=True)
        ok(r.rc == 2 and want in r.rlog and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host", "etwho", "ps")),
           "%s the reference session alone: '%s' (exit 2), before its free check, nothing opened" % (nm.split("-")[0], want), (r.rc, r.rlog[-200:], list(r.calls)))
    r = run_case("NLd-alone-no-lock-file", timeout=60, direct=True, lock=False)
    ok(r.rc == 2 and "refused: no card lock file" in r.rlog and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host", "etwho", "ps")),
       "NLd the reference session alone with no lock file: refused (exit 2), nothing opened", (r.rc, r.rlog[-200:]))
    open(LOCK, "a").close()

    # ---- run_session.sh exits before its EXIT trap, after the wrapper's probe (verify-e192 finding 1; its B7) ----
    def early(r, want, cid, what):
        pr = [c for c in r.calls.get("pvt", []) if c.get("event") == "start" and "--probe" in c.get("argv", [])]
        smp = [c for c in r.calls.get("pvt", []) + r.calls.get("sampler", []) if c.get("event") == "start" and "--probe" not in c.get("argv", [])]
        sdone = jl(os.path.join(r.outd, "run", "SESSION_DONE"))
        ge = [g.get("kind") for g in r.gate]
        card = re.findall(r"card time (\d+) s from the first card command", r.log)
        ok(r.rc == 3 and want in r.rlog and "the card is not free: nothing opened" in r.rlog and len(pr) == 1 and not smp
           and not r.calls.get("host") and not r.calls.get("heater"),
           "%s %s: run_session.sh's own free check refuses (exit 3) after the wrapper's probe; no sampler, heater or host" % (cid, what),
           (r.rc, r.rlog[-240:], len(pr), len(smp)))
        ok(not r.timed_out and r.elapsed < 45 and not r.stop and sdone and sdone[0].get("by") == "session_e192"
           and "the wrapper wrote run/SESSION_DONE" in r.log and ge[-1:] == ["session_done"] and card and int(card[0]) <= 15,
           "%sb THE FIX: the wrapper writes run/SESSION_DONE, the gate ends at it, the session ends at once (%.0f s; card time %s s; no STOP)" % (
               cid, r.elapsed, card[0] if card else "?"),
           "elapsed %.0f s, timed out %s, STOP %s, SESSION_DONE %s, gate %s" % (r.elapsed, r.timed_out, (r.stop or {}).get("by"), sdone, ge))
        ok("stopped before any pass completed" in r.log and s20_reading(r)[0] == "RUN-ENDED GATE-STOPPED(16)" and manifest_ok(r)[0],
           "%sc 'stopped before any pass completed'; step 10 reads it ended and stopped (16: still collected); the manifest exact" % cid,
           (s20_reading(r)[0], manifest_ok(r)[1]))
    r = run_case("B7-holder-after-probe", scen={"etwho_foreign_on_call": 2}, env=PVT, timeout=120)
    early(r, "held: /dev/et0_ops otheruser", "B7", "a holder after the wrapper's free check and probe")
    r = run_case("B7e-etwho-fails-after-probe", scen={"etwho_fail_on_call": 2}, env=PVT, timeout=120)
    early(r, "et-who --check failed (exit 2)", "B7e", "et-who failing at run_session.sh's check")
    r = run_case("B7p-foreign-process-after-probe", scen={"foreign_proc_on_call": 2}, env=PVT, timeout=120)
    early(r, "another user's device process", "B7p", "another user's device process at run_session.sh's check")
    r = run_case("B7l-lock-taken-after-probe", scen={"etwho_takes_lock_on_call": 2, "lock_hold_s": 20}, env=PVT, timeout=120)
    freed = end_holder(r)
    early(r, "held by another process (probe exit 75)", "B7l", "the card lock taken between run_session.sh's et-who and its lock probe")
    ok(freed and any(c.get("event") == "lock_taken_by_holder" and c.get("held") for c in r.calls.get("etwho", [])),
       "B7ld the stand-in's holder held the lock for the case and is ended after it", freed)

    # ---- the probe's lock taken (the wrapper's own line: flock exit 75 at the probe) ----
    shimd = os.path.join(S, "sbin-sha256sum")
    shim(os.path.join(shimd, "sha256sum"), "sha256sum")
    r = run_case("H5-lock-before-probe", scen={"lock_on_sha256_of": "pvt_standin.py", "lock_hold_s": 20},
                 env=dict(PVT, PATH=shimd + ":" + SBIN + ":/usr/local/bin:/usr/bin:/bin"), timeout=60)
    freed = end_holder(r)
    ok(r.rc == 3 and "the card lock was taken before the probe (flock exit 75)" in r.log and "no device opened" in r.log
       and not any(r.calls.get(k) for k in ("sampler", "pvt", "heater", "host")) and freed
       and any(c.get("event") == "lock_taken_by_holder" and c.get("held") for c in r.calls.get("sha256sum", []))
       and not os.path.exists(os.path.join(r.outd, "first-card-command.txt")),
       "H5 the card lock taken between the wrapper's own lock probe and its probe's flock: exit 3, the probe never ran, no first card command", (r.rc, r.log[-300:]))

    # ---- the per-sensor sampler's choice: off its pin; its chain NO-GO ----
    r = run_case("FP-pvt-off-its-pin", env=dict(PVT, E192_PVT_SHA256="0" * 64), actions=[stop_after_go], timeout=240)
    ok("is not at the audit table's reviewed sha256 (no probe sent)" in r.log and not r.calls.get("pvt")
       and any(c.get("event") == "start" for c in r.calls.get("sampler", [])) and r.rc == 8,
       "FP the per-sensor sampler off its reviewed sha256: no probe, the plain sampler (the fallback)", (r.rc, r.log[:700]))
    t144 = os.path.join(R, "tools/claims-v3/e144/dmcmd_table_e144.json")
    keep144 = open(t144, "rb").read()
    shutil.copy2(os.path.join(R, "tools/claims-v3/dmcmd_table.json"), t144)
    r = run_case("FN-pvt-chain-no-go", env=PVT, actions=[stop_after_go], timeout=240)
    open(t144, "wb").write(keep144)
    ok("the per-sensor chain is not GO by the audit (no probe sent)" in r.log and "the per-sensor chain NO-GO" in r.log
       and not r.calls.get("pvt") and any(c.get("event") == "start" for c in r.calls.get("sampler", [])) and r.rc == 8
       and sha(t144) == hashlib.sha256(keep144).hexdigest(),
       "FN the per-sensor chain NO-GO (the box copy of E144's table replaced by the stock table, then restored): no probe, the plain sampler", (r.rc, r.log[:700]))

    # ---- the gate's smoke conditions that G1 does not reach (verify-e192's B1-B4), and the smoke's arm order (the gate alone) ----
    r = run_case("B1-heater-check-exit", scen={"heater_rc": 1, "heater_rc_n": 1}, env=PVT, timeout=180)
    hcr = [m.get("rc") for m in r.marks if m.get("kind") == "heater_check"]
    ok(r.stop and r.stop.get("by") == "gate_e192" and "heater check's launch exited 1" in r.stop.get("why", "") and r.rc == 8
       and count(r, "host") == 3 and hcr == [1],
       "B1 the smoke's heater launch exits 1 (its level read on idle, under 70 W): the kit's gate stops, no pass", (r.rc, r.stop, count(r, "host"), hcr))
    ok("stopped before any pass completed" in r.log and s20_reading(r)[0] == "RUN-ENDED GATE-STOPPED(16)",
       "B1b step 10 reads it ended and stopped before any pass (16: still collected)", s20_reading(r)[0])
    r = run_case("B2-smoke-participants", scen={"participants_bad": 1023, "participants_upto": 3}, env=PVT, timeout=180)
    ok(r.stop and r.stop.get("by") == "gate_e192" and "participants [1023]" in r.stop.get("why", "") and count(r, "host") == 3 and r.rc == 8,
       "B2 the smoke's launches with 1,023 participants: the gate stops, no pass", (r.rc, r.stop))
    r = run_case("B3-smoke-host-exit", scen={"host_rc": 1, "host_rc_upto": 1}, env=PVT, timeout=180)
    ok(r.stop and r.stop.get("by") == "gate_e192" and "nop: exit 1" in r.stop.get("why", "") and count(r, "host") == 3 and r.rc == 8,
       "B3 the smoke's first host process exits 1 (its lines all ok): the gate stops, no pass", (r.rc, r.stop))
    r = run_case("B4-smoke-two-lines", scen={"host_lines_max": 2, "host_lines_upto": 3}, env=PVT, timeout=180)
    ok(r.stop and r.stop.get("by") == "gate_e192" and "2 INTBITS lines (< 3)" in r.stop.get("why", "") and count(r, "host") == 3 and r.rc == 8,
       "B4 the smoke's runs with 2 INTBITS lines each: the gate stops, no pass", (r.rc, r.stop))

    def gate_alone(name, arms):
        gd = os.path.join(S, "gate-alone", name)
        os.makedirs(gd)
        t = int(time.time() * 1000) - 30000
        with open(os.path.join(gd, "marks.jsonl"), "w") as f:
            f.write(json.dumps({"kind": "heater_check", "pass": -1, "rc": 0, "t0_ms": t, "t1_ms": t + 2000}) + "\n")
            for i, a in enumerate(arms):
                f.write(json.dumps({"kind": "run", "pass": -1, "seq": i, "arm": a, "role": "smoke", "rc": 0,
                                    "t0_ms": t + 3000 * (i + 1), "t1_ms": t + 3000 * (i + 1) + 2000}) + "\n")
        with open(os.path.join(gd, "runs.jsonl"), "w") as f:
            for i, a in enumerate(arms):
                for _ in range(5):
                    f.write(json.dumps({"arm": a, "pass": -1, "seq": i, "ok": True, "check_bad": 0, "participants": 1024}) + "\n")
        p = subprocess.Popen([PY, "-I", "-B", os.path.join(R, E, "gate_e192.py"), gd, "--first", str(time.time()), "--cap", "3900"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        t0 = time.time()
        while p.poll() is None and time.time() - t0 < 4:
            time.sleep(0.1)
        if p.poll() is None:
            open(os.path.join(gd, "SESSION_DONE"), "w").close()
        p.communicate(timeout=20)
        st = jl(os.path.join(gd, "STOP"))
        return p.returncode, (st[0] if st else None), [g.get("kind") for g in jl(os.path.join(gd, "gate.jsonl"))]
    print("\n== G5 the gate alone on a smoke written in another order, and its control", flush=True)
    g5 = gate_alone("G5-order", ["add.a.f2", "nop", "add.cr.l31"])
    ok(g5[1] and g5[1].get("by") == "gate_e192" and "the smoke's arms were" in g5[1].get("why", "") and g5[2][-1:] == ["stop"],
       "G5 the gate alone, the smoke's three runs in another order: STOP", g5)
    g5b = gate_alone("G5b-order-control", ["nop", "add.a.f2", "add.cr.l31"])
    ok(g5b[1] is None and "smoke_gate" in g5b[2] and g5b[2][-1:] == ["session_done"],
       "G5b its control, the registered order: GO, no STOP, the gate ends at SESSION_DONE", g5b)

    # ---- the block's own stops and crashes that the first cases do not reach (verify-e192's B5, B8-B11), and the heater check ----
    r = run_case("HB-heater-check-no-board", scen={"board_w_absent": True}, env=PVT, timeout=180)
    ok(r.rc == 4 and r.stop and r.stop.get("by") == "run_block" and "no board reading during the heater check" in r.stop.get("why", "")
       and count(r, "host") == 0 and count(r, "heater") == 1,
       "HB the smoke's heater check with no board reading in the telemetry: the block's stale stop (exit 4), no host run", (r.rc, r.stop))
    r = run_case("B8-holder-after-sampler", scen={"etwho_foreign_on_call": 3}, env=PVT, timeout=120)
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(r.rc == 3 and "the card is not free after the sampler started: no block runs" in r.rlog and not r.calls.get("host") and ends
       and os.path.exists(os.path.join(r.outd, "run", "SESSION_DONE")) and not jl(os.path.join(r.outd, "run", "SESSION_DONE"))
       and "the wrapper wrote run/SESSION_DONE" not in r.log,
       "B8 a holder right after the sampler starts: no block runs (exit 3), the sampler by SIGTERM, SESSION_DONE the reference's own (its EXIT trap)", (r.rc, r.rlog[-200:]))
    r = run_case("B9-sampler-silent", scen={"stall_after_s": 0}, env=PVT, timeout=120)
    ok(r.rc == 4 and r.stop and "no telemetry line" in r.stop.get("why", "") and not r.calls.get("host"),
       "B9 a sampler that never writes: the smoke's first reading stops (exit 4), no host run", (r.rc, r.stop))
    r = run_case("B5-block-crash", scen={"bad_json_at": 6, "scale": 0.25}, env=PVT, timeout=300)
    ends = [c for c in r.calls.get("pvt", []) if c.get("event") == "exit_on_sigterm"]
    ok(r.rc == 1 and "pass 0: exit 1 (block stopped), stopping" in r.rlog and ends and manifest_ok(r)[0]
       and "Traceback" in text(os.path.join(r.outd, "run_session.out")),
       "B5 a malformed INTBITS line in pass 0 (run_block.py raises): the block ends (exit 1), the session stops, the sampler by SIGTERM, the manifest exact", (r.rc, r.rlog[-200:]))
    nd = no_device_after(r, max((m.get("t1_ms", 0) for m in r.marks), default=0))
    ok(nd[0] and "stopped before any pass completed" in r.log, "B5b no device process after the crash; 'stopped before any pass completed'", nd[1])
    rc5, out5 = rest_read("B5")
    ok(rc5 == 3 and "since E192's session end" in out5, "B5c the rest rule counts the crashed session (its probe and sampler ran): REFUSED", out5[:200])

    def stop_when_pass0_started(r):
        if count(r, "host") >= 5:
            write_stop(r, "desk test: by hand, inside pass 0")
            return True
        return False
    r = run_case("B11-stop-inside-pass0", scen={"scale": 0.25}, env=PVT, actions=[stop_when_pass0_started], timeout=300)
    ok(r.rc == 8 and "passes complete: 0 of 9" in r.log and s20_reading(r)[0] == "RUN-ENDED GATE-STOPPED(16)",
       "B11 a stop by hand inside pass 0: exit 8, 0 passes complete, step 10 reads 16 (still collected)", (r.rc, s20_reading(r)[0]))
    r = run_case("B10-foreign-process-between-passes", scen={"foreign_proc_after_pass0": True, "scale": 0.25}, env=PVT, timeout=700)
    ok(r.rc == 3 and "pass 1: the card is not free, stopping" in r.rlog and "another user's device process" in r.rlog
       and "passes complete: 1 of 9" in r.log and s20_reading(r)[0] == "RUN-ENDED (0)",
       "B10 another user's device process after pass 0: the session stops before pass 1 (exit 3); step 10 reads it ended (0)", (r.rc, r.rlog[-300:], s20_reading(r)[0]))

    # ---- Z ----
    print("\n== Z", flush=True)
    left = []
    for d in os.listdir("/proc"):
        if d.isdigit() and int(d) != os.getpid():
            try:
                cl = open("/proc/%s/cmdline" % d, "rb").read().replace(b"\0", b" ").decode(errors="ignore")
            except OSError:
                continue
            if any(k in cl for k in ("standin_e192", "session_e192", "run_session.sh", "gate_e192", "stopwatch.py", "run_block.py", "holder.py")):
                left.append(cl[:120])
    ok(not left, "Z1 no process of the test left", left)
    ok(not os.path.exists(os.path.join(S, "network-calls.log")), "Z2 no network call (ssh, rsync, scp)")
    ok(sorted(d for d in os.listdir("/dev") if d.startswith("et")) == ["et0_mgmt", "et0_ops"], "Z3 no /dev/et* but the test's own two regular files, through the run")
    print("\nDESKTEST-REALPATH-E192 %d of %d %s%s" % (npass, ncase, "PASS" if npass == ncase else "FAIL",
          "" if npass == ncase else " (failed: %s)" % ", ".join(fails)), flush=True)
    return 0 if npass == ncase else 1


if __name__ == "__main__":
    sys.exit(main())
