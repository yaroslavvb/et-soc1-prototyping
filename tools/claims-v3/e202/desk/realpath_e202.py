#!/usr/bin/env python3
"""E202's REAL-PATH DESK TEST (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum), run inside desktest_realpath_e202.sh's
sandbox (host name aifoundry3; /dev/et0_ops and /dev/et0_mgmt as regular files; a private /run/lock and PID namespace).

    /usr/bin/python3 -I -B realpath_e202.py SRC SCRATCH BUILT

It builds a stand-in aifoundry3 tree in SCRATCH/tree holding harness-e202.json's files at their paths (what step 5's sync puts on the
box), the kernel BUILT by build_e202.sh today (its .text at E202.md's pin) and the 18 checked inputs, with stand-ins at the tools' real
paths (desk/standin_e202.py): build/ettelem/ettelem behind the box copy of E128's guard, build/e202mnist/host/mnistmlp_host (the build
record re-written with its sha256), and et-who on PATH. Then each case launches `bash tools/claims-v3/e202/session_e202.sh` EXACTLY as
step 9 does (E202_T0, E202_DEADLINE_EPOCH; DRY unset) and asserts on what the runner wrote and what it sent:
  P     the whole real path: refusals passed, the lock, et-who, the first card command, the sampler through the guard, the stop-path test,
        anchor 1, the five smoke processes, the gate, the R rule, the 12 bursts in THE ORDER, anchor 2, et-who, the closing read, the
        manifest; every host's stdout split by a runtime line inside its JSON line and every 25th sampler line too; the lock held and
        step 10's pattern matching the real wrapper (and no decoy) while it runs; then the collection, the unchanged reducer (each burst's
        J over idle against the energy the stand-in card injected), the frozen scorer, and the rest rule reading the session;
  R1-R9 the refusals before anything ("refused, no device opened", runner.rc 2, no card command sent);
  G1-G3 the gates after the card opened (GATE-STOP, runner.rc 3);
  S1, FB, K1, SG, T, SIG  stops and the fallback after data;
  fix-e202 (verify-e202's findings 1, 2, 5): W1 et-who's helper refused (rc 1, nothing on stdout) before the first card command:
        refused, no device opened; W2 et-who rc 0 with neither a holder line nor its no-holder sentence from its 9th read: STOP before
        burst 3, the closing config NOT sent; K1b a host that dies mid-launch in burst 1 (rc 134, no --out record): K1, nothing
        further; CR a crash of the runner in burst 1 (its folder cannot be made): "CRASH: ..." before the closing, runner.rc 1;
  AUDIT every line of run_e202.py and session_e202.sh that branches on DRY has a row in dry-branches-e202.tsv naming the cases here that
        run its real branch, and every such case passed in this run.
Prints each check PASS/FAIL and DESKTEST-REALPATH-E202 <n> of <m> PASS or FAIL last. SPDX-License-Identifier: Apache-2.0
"""
import csv
import fcntl
import glob
import hashlib
import json
import os
import pwd
import shutil
import signal
import subprocess
import sys
import time

SRC, S, BUILT = (os.path.abspath(x) for x in sys.argv[1:4])
E = "tools/claims-v3/e202"
T = os.path.join(S, "tree")
SD = os.path.join(T, ".standin")
BIN = os.path.join(S, "bin")
RES = []
PASSED = set()
TEXT_PIN = "ace7bcb04536329f1d75135446049c442b9f4b65f726083f7623b959b279d82d"
LOGIN = pwd.getpwuid(os.getuid()).pw_name


def check(case, name, ok, detail=""):
    RES.append((case, name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'} {case} {name}{': ' + str(detail) if detail != '' else ''}", flush=True)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sh(path, body):
    with open(path, "w") as f:
        f.write(body)
    os.chmod(path, 0o755)


def build_tree():
    files = subprocess.run(["/usr/bin/python3", "-B", os.path.join(SRC, E, "check_e202.py"), "--list"], capture_output=True,
                           text=True).stdout.split()
    files += [E + "/harness-e202.json", E + "/desk/standin_e202.py", E + "/rb/rest_rule_e202.sh"]
    for p in files:
        os.makedirs(os.path.dirname(os.path.join(T, p)), exist_ok=True)
        shutil.copy2(os.path.join(SRC, p), os.path.join(T, p))
    os.makedirs(os.path.join(T, "build", "e202mnist", "kernel"))
    os.makedirs(os.path.join(T, "build", "e202mnist", "host"))
    shutil.copy2(os.path.join(BUILT, "build/e202mnist/kernel/mnistmlp.elf"), os.path.join(T, "build/e202mnist/kernel/mnistmlp.elf"))
    shutil.copytree(os.path.join(BUILT, "build/e202files"), os.path.join(T, "build/e202files"))
    os.makedirs(os.path.join(T, "build", "ettelem"))
    os.makedirs(SD)
    os.makedirs(BIN)
    si = os.path.join(T, E, "desk", "standin_e202.py")
    sh(os.path.join(T, "build/ettelem/ettelem"), f'#!/bin/bash\nexec /usr/bin/python3 -B "{si}" ettelem "$@"\n')
    sh(os.path.join(T, "build/e202mnist/host/mnistmlp_host"), f'#!/bin/bash\nexec /usr/bin/python3 -B "{si}" host "$@"\n')
    sh(os.path.join(BIN, "et-who"), f'#!/bin/bash\nexec /usr/bin/python3 -B "{si}" etwho "$@"\n')
    write_record()


def write_record():
    json.dump({"built": True, "written": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "host": "build/e202mnist/host/mnistmlp_host",
               "host_sha256": sha(os.path.join(T, "build/e202mnist/host/mnistmlp_host")),
               "elf_sha256": sha(os.path.join(T, "build/e202mnist/kernel/mnistmlp.elf")), "text_sha256": TEXT_PIN,
               "files": "E202-FILES OK (the desk build's)", "host_behaviour": "a stand-in host (the real-path desk test)"},
              open(os.path.join(T, "build/e202mnist/BUILD-E202.json"), "w"), indent=1)


def launch(case, knobs, deadline=None, wrap=None, env_extra=None, during=None, timeout=1500, pre=None):
    json.dump(knobs, open(os.path.join(SD, "case.json"), "w"))
    for f in ("sched.jsonl", "calls.jsonl", "etwho-calls"):
        p = os.path.join(SD, f)
        if os.path.exists(p):
            os.remove(p)
    t0 = int(time.time())
    while os.path.exists(os.path.join(T, "build", "e202", f"T{t0}")):
        time.sleep(1)
        t0 = int(time.time())
    if pre:                                   # fix-e202: a case's own preparation of the session's folder (CR)
        pre(t0)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("E202_", "V3_", "RB_"))}
    env["PATH"] = BIN + ":" + env.get("PATH", "/usr/bin:/bin")
    env["E202_T0"] = str(t0)
    env["E202_DEADLINE_EPOCH"] = str(deadline or t0 + 3 * 3600)
    env.update(env_extra or {})
    p = subprocess.Popen((wrap or []) + ["bash", f"{E}/session_e202.sh"], cwd=T, env=env, start_new_session=True,
                         stdout=open(os.path.join(S, f"{case}.wrapper.out"), "w"), stderr=subprocess.STDOUT)
    extra = during(p, t0) if during else None
    p.wait(timeout=timeout)
    out = os.path.join(T, "build", "e202", f"T{t0}")
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    try:
        q = json.load(open(os.path.join(out, "queue.json")))
    except (OSError, ValueError):
        q = {}
    rc = open(os.path.join(out, "runner.rc")).read().strip() if os.path.exists(os.path.join(out, "runner.rc")) else None
    calls = [json.loads(ln) for ln in open(os.path.join(SD, "calls.jsonl"))] if os.path.exists(os.path.join(SD, "calls.jsonl")) else []
    return {"out": out, "log": log, "q": q, "rc": rc, "calls": calls, "t0": t0, "extra": extra}


def ran(q):
    return [b["burst"] for b in q.get("bursts", []) if b.get("ran")]


def card_calls(c):
    return [x for x in c["calls"] if x["tool"] in ("ettelem", "host")]


def wait_log(t0, words, limit):
    """Wait for words in the session's log, at most limit seconds, and never past its "session end"."""
    end = time.time() + limit
    p = os.path.join(T, "build", "e202", f"T{t0}", "session.log")
    while time.time() < end:
        body = open(p).read() if os.path.exists(p) else ""
        if words in body:
            return True
        if "session end" in body:
            return False
        time.sleep(0.5)
    return False


def rb_pattern():
    for ln in open(os.path.join(SRC, E, "rb", "rb_e202.sh")):
        if ln.startswith("E202_SESSION_PAT="):
            return ln.split("=", 1)[1].strip().strip("'")
    return None


def main():
    print(f"realpath_e202: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}, /usr/bin/python3 {sys.version.split()[0]}", flush=True)
    for d in os.listdir("/dev"):
        if d.startswith("et") and not os.path.isfile(os.path.join("/dev", d)):
            print(f"REFUSED: /dev/{d} is not a regular file in the sandbox")
            return 2
    build_tree()
    vis = [p for p in os.listdir("/proc") if p.isdigit()]
    check("ST", "the sandbox: host name aifoundry3, exactly two regular files /dev/et0_mgmt and /dev/et0_ops, a private PID namespace",
          os.uname().nodename == "aifoundry3" and sorted(d for d in os.listdir("/dev") if d.startswith("et")) == ["et0_mgmt", "et0_ops"]
          and len(vis) < 15, f"{len(vis)} processes visible")
    r = subprocess.run(["/usr/bin/python3", "-B", f"{E}/check_e202.py", "--box", "--built"], cwd=T, capture_output=True, text=True)
    check("ST", "the stand-in tree's harness with the built kernel", r.stdout.startswith("HARNESS OK: 33"), r.stdout.strip())

    # ---------------------------------------------------------------- D: the dry pass as step 8's job runs it
    t0 = int(time.time())
    env = {k: v for k, v in os.environ.items() if not k.startswith(("E202_", "V3_", "RB_"))}
    r = subprocess.run(["python3", "-B", f"{E}/run_e202.py", "session", "--dry", "--double", "alt", "--t0", str(t0), "--out",
                        f"build/e202/T{t0}-dry", "--sequence", "short", "--idle-before", "1", "--idle-after", "1", "--anchor-s", "1",
                        "--die-wait-s", "5"], cwd=T, env=dict(env, E202_FAKE_SCALE="0.2", PATH=BIN + ":" + env["PATH"]),
                       capture_output=True, text=True, timeout=600)
    dlog = open(os.path.join(T, f"build/e202/T{t0}-dry/session.log")).read()
    check("D", "the dry pass in step 8's form: smoke gate passed, 4 bursts done PASS, every line DRY, no stand-in called", r.returncode == 0
          and dlog.count("done: host rc 0, status PASS") == 4 and "smoke gate passed" in dlog
          and not os.path.exists(os.path.join(SD, "calls.jsonl")), f"rc {r.returncode}")

    # ---------------------------------------------------------------- P: the whole real path
    pat = rb_pattern()
    held = {}

    def during_p(p, t0):
        ok = wait_log(t0, "burst 1: trained-scp b1 (", 600)
        lk = subprocess.run(["flock", "-n", "/run/lock/etsoc-shire0.lock", "true"]).returncode
        decoy = subprocess.Popen(["s11_a3_session_e202.sh", "20"], executable="/usr/bin/sleep")
        decoy2 = subprocess.Popen(["bash", "-c", "sleep 20", "x"], cwd=T)
        time.sleep(0.5)
        m = subprocess.run(["pgrep", "-u", str(os.getuid()), "-f", pat], capture_output=True, text=True).stdout.split()
        cmd = [open(f"/proc/{x}/cmdline").read().replace("\0", " ").strip() for x in m if os.path.exists(f"/proc/{x}/cmdline")]
        k6 = subprocess.run(["pgrep", "-u", str(os.getuid()), "-f", r"(queue|session)_e[0-9]+[a-z0-9_]*\.(py|sh)"], capture_output=True,
                            text=True).stdout.split()
        decoy.terminate()
        decoy2.terminate()
        decoy.wait()
        decoy2.wait()
        held.update(reached=ok, lock_rc=lk, matches=cmd, k6=len(k6))
        return held

    knobs_p = {"BASE": "alt", "SPLIT": True, "SAMPLER": "split", "SCALE": "1"}
    c = launch("P", knobs_p, during=during_p)
    log, q, out = c["log"], c["q"], c["out"]
    check("P", "the session ran whole: runner.rc 0, no stop, 12 bursts", c["rc"] == "0" and not q.get("stop") and len(ran(q)) == 12,
          f"rc {c['rc']}, stop {q.get('stop')}")
    order = ["trained-scp/b1", "random-scp/b1", "random-scp/b2", "trained-scp/b2", "trained-scp/b3", "random-scp/b3", "random-scp/b4",
             "trained-scp/b4", "trained-dram/b1", "random-dram/b1", "random-dram/b2", "trained-dram/b2"]
    check("P", "THE ORDER as registered, R 96 each, the dram pair REPORTED", ran(q) == order and q.get("R", {}).get("trained-scp") == 96
          and all(json.load(open(os.path.join(out, "bursts", *b.split("/"), "burst.json")))["R"] == 96 for b in order), "")
    steps = ["first card command: config start, stamped as it starts", "config start: TDP 0 W, threshold 65 C, minion 600 MHz",
             "sampler started", "stop-path test passed", "idle anchor 1: 120 s", "smoke gate passed: T-scp and Z-scp read core PASS",
             "idle anchor 2: 120 s", "config end: TDP 0 W", "session end (T0"]
    pos = [log.find(s) for s in steps]
    check("P", "the session's steps in order, in the kits' log form", all(x >= 0 for x in pos) and pos == sorted(pos),
          f"{sum(1 for x in pos if x >= 0)} of {len(steps)}")
    lines = [ln for ln in log.splitlines()]
    check("P", "no line marked DRY on the real path", not any(" DRY " in ln[:40] for ln in lines), "")
    cc = card_calls(c)
    cfgs = [x for x in cc if x["tool"] == "ettelem" and x["args"] == ["config"]]
    smp = [x for x in cc if x["tool"] == "ettelem" and x["args"][:1] == ["sample"]]
    hosts = [x for x in cc if x["tool"] == "host"]
    whos = [x for x in c["calls"] if x["tool"] == "etwho"]
    check("P", "what reached the card's tools: config twice (start, end), ONE sampler (sample --seconds 3300 --every-ms 100), 17 host "
          "processes (5 smoke + 12 bursts), nothing else", len(cfgs) == 2 and len(smp) == 1 and smp[0]["args"] == ["sample", "--seconds",
                                                                                                                     "3300", "--every-ms", "100"]
          and len(hosts) == 17 and len(cc) == 20, f"config {len(cfgs)}, sampler {len(smp)}, host {len(hosts)}")
    check("P", "et-who read before the first card command, before each of the 17 host processes and before the closing read (19)",
          len(whos) == 19, f"{len(whos)} et-who calls")
    sm = [h["args"] for h in hosts[:5]]
    want_sm = [("trained", "scp", "train"), ("random", "scp", "train"), ("trained", "dram", "train"), ("random", "dram", "train"),
               ("trained", "scp", "test")]
    ok = all("--card" in a and a[a.index("--passes") + 1] == "1" and a[a.index("--stage") + 1] == st and a[a.index("--split") + 1] == sp
             and f"mnist-int8-{w}.mlpw" in a[a.index("--weights") + 1] and a[a.index("--pins") + 1] == "build/e202files/files/PINS-SHA256SUMS"
             for a, (w, st, sp) in zip(sm, want_sm))
    ok = ok and all("--debug-logits" in a for a in sm[:4]) and "--true-labels" in sm[4] and "--debug-logits" not in sm[4]
    bh = [h["args"] for h in hosts[5:]]
    ok2 = all(a[a.index("--passes") + 1] == "96" and "--debug-logits" not in a and "--labels-out" not in a for a in bh)
    check("P", "every host argv the registered one (smoke: R 1, the four with --debug-logits, ACC on the test split with --true-labels; "
          "bursts: R 96, no debug), every input pinned", ok and ok2, "")
    split = 0
    for b in order:
        so = open(os.path.join(out, "bursts", *b.split("/"), "stdout.txt")).read()
        hr = json.load(open(os.path.join(out, "bursts", *b.split("/"), "host-raw.json")))
        split += ("Opening device 0" in so and so.startswith("{") and hr.get("status") == "PASS")
    check("P", "THE HOST'S RESULT read from its own --out file: every burst's stdout holds its JSON line split by a runtime line, every "
          "host-raw.json whole and PASS", split == 12, f"{split} of 12")
    tel = os.path.join(out, "telemetry.jsonl.gz")
    check("P", "the sampler's split lines lost, never misread; the session's telemetry and the manifest", os.path.exists(tel)
          and os.path.exists(os.path.join(out, "MANIFEST.sha256")) and not q.get("off_clock"), "")
    h = c["extra"] or {}
    check("P", "while it ran: card 0's lock held (flock -n refused), step 10's pattern matched the real wrapper and no decoy, k6's "
          "ours_live counted it", h.get("reached") and h.get("lock_rc") == 1 and len(h.get("matches", [])) == 1
          and h["matches"][0].endswith(f"{E}/session_e202.sh") and h.get("k6", 0) >= 1, f"pattern {pat!r}: {h.get('matches')}")
    copy = os.path.join(S, "P-copy")
    shutil.copytree(out, copy)
    data = os.path.join(S, "e202-P-data")
    r = subprocess.run(["/usr/bin/python3", "-B", os.path.join(SRC, E, "collect_e202.py"), copy, data, "--box-home",
                        os.path.expanduser("~"), "--box-login", LOGIN, "--data-outside"], cwd=SRC,
                       env=dict(env, RB_DESKTEST="1"), capture_output=True, text=True, timeout=1200)
    check("P", "the collection on the real path's files: COPY-BACK EXACT, 12 bursts reduced (the unchanged reducer), the scrub clean",
          r.returncode == 0 and "COPY-BACK EXACT" in r.stdout and "12 bursts reduced" in r.stdout, (r.stdout.strip().splitlines() or [""])[-1][:150])
    sched = [json.loads(ln) for ln in open(os.path.join(SD, "sched.jsonl"))] if os.path.exists(os.path.join(SD, "sched.jsonl")) else []
    errs = []
    for b in order:
        en = json.load(open(os.path.join(data, "bursts", *b.split("/"), "energy.json")))
        hr = json.load(open(os.path.join(data, "bursts", *b.split("/"), "host-raw.json")))
        lo, hi = hr["launch_epoch_ms"]
        inj = [s for s in sched if s["tag"] == "burst" and abs(s["t0"] * 1000 - lo) < 50]
        e_inj = sum(s["dp"] * (s["t1"] - s["t0"]) for s in inj)
        tol = 0.03 + 0.33 * ((hi - lo) / 1000.0 + 7.0) / max(e_inj, 1e-9)
        errs.append((b, en["board"]["j_per_solve"] / e_inj - 1.0 if e_inj else 9.9, tol, en.get("ok")))
    check("P", "each burst's reduced J over idle against the energy the stand-in card injected (within 3% + 0.33 W/C x (t + 7 s) / J)",
          all(ok and abs(e) <= tol for _, e, tol, ok in errs), "; ".join(f"{b.split('/')[0][:9]}/{b.split('/')[1]} {e:+.1%}" for b, e, _, _ in errs))
    sc = os.path.join(S, "P-scores.json")
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(SRC, E, "score_e202.py"), data, "--out", sc], cwd=SRC,
                       capture_output=True, text=True, timeout=600)
    v = json.load(open(sc))["verdict_of_the_day"] if os.path.exists(sc) else {}
    rep = json.load(open(sc))["reported"] if os.path.exists(sc) else {}
    check("P", "the frozen scorer on the collected real-path data: the gate (scp), every rule a word, the dram pair REPORTED",
          r.returncode == 0 and set(v) == {"E202-S1", "E202-S1T", "E202-S2", "E202-S2T", "E202-S3"} and all(x in ("PASS", "FAIL") for x in v.values())
          and set(rep) == {"trained-dram", "random-dram"}, json.dumps(v))
    rw = os.path.join(S, "rest-wrap.sh")
    sh(rw, "set -u\ncd " + T + " || exit 1\n" + open(os.path.join(T, E, "rb", "rest_rule_e202.sh")).read())
    r = subprocess.run(["bash", rw], capture_output=True, text=True, timeout=120)
    check("P", "the rest rule reads the real session's log (40 minutes not yet passed: refused)", r.returncode == 3
          and r.stdout.startswith("REFUSED: ") and "E202's session end" in r.stdout, r.stdout.strip()[:140])
    PASSED.update(["P"] if all(ok for cs, _, ok in RES if cs == "P") else [])

    # ---------------------------------------------------------------- R: refusals before anything
    def refused(case, c, words):
        ok = c["rc"] == "2" and f"refused, no device opened: {words}" in c["log"] and not card_calls(c) and "first card command" not in c["log"]
        check(case, f"refused before any card command ({words})", ok, f"rc {c['rc']}, card calls {len(card_calls(c))}")
        if ok:
            PASSED.add(case)
    base = {"BASE": "alt", "SCALE": "1"}
    refused("R1", launch("R1", base, wrap=["/usr/bin/bwrap", "--dev-bind", "/", "/", "--unshare-uts", "--hostname", "aifoundry2", "--"]),
            "the host's name is 'aifoundry2'")
    open(os.path.join(S, "et1_ops.regular-file"), "w").close()
    # a nested sandbox with its OWN /dev (three regular files), so the outer sandbox's /dev keeps its two (a bind into the shared /dev
    # would leave the mount point there for every later case)
    refused("R2", launch("R2", base, wrap=["/usr/bin/bwrap", "--dev-bind", "/", "/", "--dev", "/dev",
                                           "--bind", os.path.join(S, "et0_ops.regular-file"), "/dev/et0_ops",
                                           "--bind", os.path.join(S, "et0_mgmt.regular-file"), "/dev/et0_mgmt",
                                           "--bind", os.path.join(S, "et1_ops.regular-file"), "/dev/et1_ops", "--"]), "the card nodes are")
    if sorted(d for d in os.listdir("/dev") if d.startswith("et")) != ["et0_mgmt", "et0_ops"]:
        print("ABORT: the outer sandbox's /dev changed after R2: " + str(sorted(d for d in os.listdir("/dev") if d.startswith("et"))))
        return 2
    fk = os.path.join(T, E, "fake_card_e202.py")
    keep = open(fk, "rb").read()
    open(fk, "ab").write(b"\n")
    refused("R3", launch("R3", base), "the synced files differ from harness-e202.json")
    open(fk, "wb").write(keep)
    rec = os.path.join(T, "build/e202mnist/BUILD-E202.json")
    st = os.stat(rec)
    os.utime(rec, (st.st_atime, time.time() - 2 * 86400))
    refused("R4", launch("R4", base), "the build record was not written today")
    os.utime(rec, (st.st_atime, time.time()))
    hp = os.path.join(T, "build/e202mnist/host/mnistmlp_host")
    keep = open(hp, "rb").read()
    open(hp, "ab").write(b"# changed\n")
    refused("R5", launch("R5", base), "the host differs from today's build record")
    open(hp, "wb").write(keep)
    ep = os.path.join(T, "build/e202files/files/expect-trained-test.mlpe")
    keep = open(ep, "rb").read()
    open(ep, "ab").write(b"\0")
    refused("R6", launch("R6", base), "the input expect-trained-test.mlpe is not at its pin")
    open(ep, "wb").write(keep)
    lf = open("/run/lock/etsoc-shire0.lock", "a+")      # held by this test process itself, released at once after (no child inherits it)
    fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
    refused("R7", launch("R7", base), "card 0's lock is held")
    lf.close()
    refused("R8", launch("R8", dict(base, ETWHO="held")), "a holder or a foreign device process")
    c = launch("R9", base, env_extra={"E202_FAKE_SCALE": "0.2"})
    ok = c["rc"] == "2" and not card_calls(c) and "desk-test variable" in open(os.path.join(c["out"], "runner.out")).read()
    check("R9", "a desk-test variable in the environment: refused, no device opened (the runner's own refusal)", ok, f"rc {c['rc']}")
    PASSED.update(["R9"] if ok else [])

    # ---------------------------------------------------------------- G: gates after the card opened
    c = launch("G1", dict(base, CONFIG="tdp5"))
    ok = c["rc"] == "3" and "GATE-STOP: config start" in c["log"] and not [x for x in card_calls(c) if x["args"][:1] == ["sample"]] \
        and not [x for x in card_calls(c) if x["tool"] == "host"]
    check("G1", "the start config at TDP 5 W: GATE-STOP, no sampler, no host process", ok, f"rc {c['rc']}")
    PASSED.update(["G1"] if ok else [])
    c = launch("G2", dict(base, SAMPLER="dead"))
    ok = c["rc"] == "3" and "GATE-STOP: the sampler would not start" in c["log"] and len([x for x in card_calls(c) if x["args"][:1] == ["sample"]]) == 6
    check("G2", "a dead sampler: six attempts through the guard, GATE-STOP, no host process", ok and not [x for x in card_calls(c) if x["tool"] == "host"],
          f"rc {c['rc']}")
    PASSED.update(["G2"] if ok else [])
    c = launch("G3", dict(base, SAMPLER="quiet-from:9"))
    ok = c["rc"] == "3" and "no telemetry line for" in (c["q"].get("stop") or "") and not [x for x in card_calls(c) if x["tool"] == "host"] \
        and c["q"].get("closing_config") == "read"
    check("G3", "the sampler quiet in anchor 1: THE STALE LINE stops it, no host process, GATE-STOP, the closing read", ok,
          f"rc {c['rc']}, stop {c['q'].get('stop')}")
    PASSED.update(["G3"] if ok else [])

    # ---------------------------------------------------------------- S: stops and the fallback after data
    c = launch("S1", dict(base, INJECT=[{"board_w": 66.0, "during": "burst", "count": 1}]))
    rj = json.load(open(os.path.join(c["out"], "bursts/trained-scp/b1/run.json"))) if ran(c["q"]) else {}
    ok = c["rc"] == "0" and ran(c["q"]) == ["trained-scp/b1"] and "board 66.0 W" in (c["q"].get("stop") or "") \
        and rj.get("end_ms", 0) - rj.get("host_t1_ms", 0) >= 9500 and c["q"].get("closing_config") == "read"
    check("S1", "board 66 W in burst 1: STOP; the host finishes; its 10 s rest after whole; nothing after; the closing read", ok,
          f"bursts {ran(c['q'])}, rest after {rj.get('end_ms', 0) - rj.get('host_t1_ms', 0)} ms")
    PASSED.update(["S1"] if ok else [])
    c = launch("FB", dict(base, SMOKE={"T-scp": "core"}, ETWHO="held-from:9"))
    ok = c["rc"] == "0" and c["q"].get("scored_stage") == "dram" and ran(c["q"]) == ["trained-dram/b1", "random-dram/b1"] \
        and "STOP before burst 3" in c["log"] and c["q"].get("closing_config", "").startswith("not read: et-who") \
        and not os.path.exists(os.path.join(c["out"], "config-end.json")) and len([x for x in card_calls(c) if x["args"] == ["config"]]) == 1
    check("FB", "T-scp's smoke fails: the dram pair scored; a holder before burst 3: STOP; the closing config NOT sent (et-who not free)",
          ok, f"stage {c['q'].get('scored_stage')}, bursts {ran(c['q'])}, closing {c['q'].get('closing_config')}")
    PASSED.update(["FB"] if ok else [])
    c = launch("K1", dict(base, BURSTS={"trained-scp/b1": "hang"}))
    ok = c["rc"] == "0" and ran(c["q"]) == ["trained-scp/b1"] and (c["q"].get("stop") or "").startswith("K1:")
    check("K1", "a launch that does not finish (the host's own line): STOP, nothing further", ok, f"stop {c['q'].get('stop')}")
    PASSED.update(["K1"] if ok else [])
    c = launch("SG", dict(base, SMOKE={"T-scp": "core", "T-dram": "core"}))
    ok = c["rc"] == "3" and not ran(c["q"]) and "GATE-STOP: the smoke gate: no pair read core PASS" in c["log"] \
        and c["q"]["smoke"]["T-dram"]["core_status"] == "FAIL" and c["q"].get("closing_config") == "read"
    check("SG", "no pair passes the smoke (T-scp and T-dram core FAIL; a host that crashes is K1's since fix-e202, case K1b): GATE-STOP, "
          "no burst, the closing read", ok, f"rc {c['rc']}")
    PASSED.update(["SG"] if ok else [])

    # ---------------------------------------------------------------- fix-e202: et-who unreadable, a host that dies, the runner's crash
    refused("W1", launch("W1", dict(base, ETWHO="fail")),
            "a holder or a foreign device process (et-who unreadable (rc 1, nothing on its stdout))")
    c = launch("W2", dict(base, ETWHO="garbled-from:9"))
    ok = c["rc"] == "0" and ran(c["q"]) == ["trained-scp/b1", "random-scp/b1"] \
        and "STOP before burst 3: et-who unreadable (rc 0, but neither a holder line nor its no-holder sentence)" in c["log"] \
        and c["q"].get("closing_config", "").startswith("not read: et-who does not read the card free (et-who unreadable") \
        and not os.path.exists(os.path.join(c["out"], "config-end.json")) and len([x for x in card_calls(c) if x["args"] == ["config"]]) == 1
    check("W2", "et-who rc 0 with neither a holder line nor its no-holder sentence from its 9th read: STOP before burst 3; the closing "
          "config NOT sent", ok, f"bursts {ran(c['q'])}, closing {c['q'].get('closing_config')}")
    PASSED.update(["W2"] if ok else [])
    c = launch("K1b", dict(base, BURSTS={"trained-scp/b1": "crash"}))
    ok = c["rc"] == "0" and ran(c["q"]) == ["trained-scp/b1"] and (c["q"].get("stop") or "").startswith("K1: burst 1") \
        and "rc 134" in (c["q"].get("stop") or "") and len([x for x in card_calls(c) if x["tool"] == "host"]) == 6
    check("K1b", "a host that dies mid-launch in burst 1 (rc 134, no --out record): K1, nothing further", ok, f"stop {c['q'].get('stop')}")
    PASSED.update(["K1b"] if ok else [])

    def pre_cr(t0):
        d = os.path.join(T, "build", "e202", f"T{t0}")
        os.makedirs(d)
        open(os.path.join(d, "bursts"), "w").close()      # a file where the runner makes burst 1's folder: the runner crashes there
    c = launch("CR", base, pre=pre_cr)
    lines = c["log"].splitlines()
    ci = [i for i, ln in enumerate(lines) if " CRASH: NotADirectoryError" in ln]
    ce = [i for i, ln in enumerate(lines) if "config end: TDP 0 W" in ln]
    ok = c["rc"] == "1" and ci and ce and ci[0] < ce[0] and (c["q"].get("crash") or "").startswith("NotADirectoryError") \
        and "session end (T0" in c["log"] and os.path.exists(os.path.join(c["out"], "MANIFEST.sha256")) and not ran(c["q"]) \
        and len([x for x in card_calls(c) if x["tool"] == "host"]) == 5
    check("CR", "a crash of the runner in burst 1: 'CRASH: <type>: <message>' before the closing, queue.json's crash, the closing read, "
          "session end, the manifest, runner.rc 1 (never 0)", ok, f"rc {c['rc']}, crash {str(c['q'].get('crash')).split(':')[0]}")
    PASSED.update(["CR"] if ok else [])

    def during_t(p, t0):
        wait_log(t0, "burst 2: random-scp b1 (", 600)
        open(os.path.join(T, "build", "e202", f"T{t0}", "STOP"), "w").close()
        return True
    c = launch("T", base, during=during_t)
    b2 = [b for b in c["q"].get("bursts", []) if b.get("burst") == "random-scp/b1"]
    ok = c["rc"] == "0" and ran(c["q"]) == ["trained-scp/b1"] and "the operator's stop (the STOP file" in (c["q"].get("stop") or "") \
        and c["q"].get("closing_config") == "read" and b2 and not b2[0].get("ran") and b2[0].get("why", "").startswith("stop:") \
        and len([x for x in card_calls(c) if x["tool"] == "host"]) == 6        # the five smoke processes and burst 1's, no more
    check("T", "the operator's STOP file in burst 2's rest before its host: no host process for it (a stop starts nothing), nothing "
          "further, the closing read", ok, f"bursts {ran(c['q'])}, burst 2: {b2[0].get('why') if b2 else None}, stop {c['q'].get('stop')}")
    PASSED.update(["T"] if ok else [])

    def during_sig(p, t0):
        wait_log(t0, "idle anchor 1:", 120)
        time.sleep(2)
        rp = subprocess.run(["pgrep", "-u", str(os.getuid()), "-f", f"run_e202.py session --t0 {t0}"], capture_output=True, text=True).stdout.split()
        for x in rp:
            os.kill(int(x), signal.SIGTERM)
        return rp
    c = launch("SIG", base, during=during_sig)
    ok = c["rc"] == "3" and "the operator's stop (signal 15" in (c["q"].get("stop") or "") and not ran(c["q"]) \
        and not [x for x in card_calls(c) if x["tool"] == "host"] and os.path.exists(os.path.join(c["out"], "MANIFEST.sha256"))
    check("SIG", "SIGTERM to the runner in anchor 1: a registered stop, never a kill: no host process, the closing, the manifest", ok,
          f"rc {c['rc']}, stop {c['q'].get('stop')}")
    PASSED.update(["SIG"] if ok else [])

    # ---------------------------------------------------------------- the end: nothing left
    left = [p for p in os.listdir("/proc") if p.isdigit() and int(p) != os.getpid()]
    names = [open(f"/proc/{p}/comm").read().strip() for p in left if os.path.exists(f"/proc/{p}/comm")]
    ok = not [n for n in names if n not in ("bash", "bwrap", "python3", "sed", "tee")]
    check("Z", "no stand-in, sampler or session process left in the sandbox", ok and not any("ettelem" in n or "_host" in n for n in names),
          ", ".join(names))
    PASSED.update(["Z"] if ok else [])

    # ---------------------------------------------------------------- AUDIT: every dry branch has its real cases
    rows = list(csv.DictReader(open(os.path.join(SRC, E, "desk", "dry-branches-e202.tsv")), delimiter="\t", quoting=csv.QUOTE_NONE))
    want = []
    for f in (f"{E}/run_e202.py", f"{E}/session_e202.sh"):
        for i, ln in enumerate(open(os.path.join(SRC, f)), 1):
            s = ln.strip()
            if ("self.dry" in s or "a.dry" in s or "args.dry" in s) and not s.startswith("#"):
                want.append((f, s))
    have = {(r["file"], r["line"]) for r in rows}
    missing = [w for w in want if w not in have]
    stale = [h for h in have if h not in set(want)]
    bad_cases = [(r["line"][:50], c) for r in rows for c in r["real_cases"].split(",") if c.strip() and c.strip() not in PASSED]
    check("AUDIT", f"every DRY branch ({len(want)} lines) has a row naming its real-path cases, every row's line is the file's own, every "
          "named case passed in this run", not missing and not stale and not bad_cases and len(rows) == len(want),
          f"missing {missing[:3]}, stale {stale[:3]}, cases not passed {bad_cases[:3]}")
    n = sum(1 for _, _, ok in RES if ok)
    print(f"DESKTEST-REALPATH-E202 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
