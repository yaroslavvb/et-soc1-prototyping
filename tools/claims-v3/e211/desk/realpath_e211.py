#!/usr/bin/env python3
"""E211's REAL-PATH desk test (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum; the round's lesson: a branch the dry path skips is
exercised by a desk test of the real path; E206's desk/realpath_e206.py form, arm A, as E207's kit ported it (Q199), for E211's two kernels and
two hosts). run_e211.py's session WITHOUT --dry, on a stand-in aifoundry3 box tree, as on the card day except for these stand-ins:
  - the hostname: aifoundry3, from a private UTS namespace (desk/realpath_e211.sh starts this driver under bubblewrap with --hostname, a private
    PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock);
  - the telemetry reader behind the REAL guard (ettelem_guard_e211.sh, with its hostname and ET_DEVICES rules): build/ettelem/ettelem is a
    script that runs fake_card_e211.py (config, sample); the runner's pin for it is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e211.py etwho, which reads who holds the stand-in nodes and the stand-in lock from
    /proc, as et-who's fuser does;
  - the two hosts: build/e211rgm/rgm136/host/sparsity_host and build/e211rgm/rgm211/host/sparsity_host are scripts (the names the runner checks)
    that run fake_card_e211.py host --as rgm136 and --as rgm211 (rgm211's with its walk fields); the build record carries their sha256; the two
    kernel ELFs are the REAL ones, built by the REAL build_e211.sh in the stand-in tree (the kernel gates on this desk's toolchain), so THE
    IDENTITY GATE PER PROCESS reads real ELFs;
  - the card's lock: a writable stand-in file (the runner's lock path set to it in this process), and the card's nodes a stand-in directory
    (e211_ident.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, the device environment without ET_DEVICES, the build record and its day, each
kernel through THE KERNEL GATE (check_e211.py --kernel rgm136|rgm211: the registration's gate, the real objcopy), each host at its record, the
reader at its pin, the tiles, check_e211.py --box (the registration's points, plan, forecast, kernel record and gate among its files) and
preflight_e211.sh (dmcmd_audit_v2), both run), the lock (open, flock -n), the holders (et-who through `timeout 20` and the real `ps`), the start
config through the real guard under the real `timeout 10`, the card's identity gate, the sampler through the real guard, the identity read, the
smoke (s01, s02, s03, each through the real identity gate on its real ELF, against MM1's counter-mean forecast, the walk check) THEN the
stop-path test, the runs (x01n, x01m, x02n) with each host under the real `timeout 10`, each gated, the closing config, the manifest. Timing: the
desk's short reads and the doubles at a twentieth of their time (the session's fields are set here; run_e211.py's main() refuses them without
--dry).

    python3 -B tools/claims-v3/e211/desk/realpath_e211.py <scratch dir> A      (desk/realpath_e211.sh runs it in its namespaces)

Cases (hostname aifoundry3): RA0 the REAL build in the stand-in tree (RGM-BUILT; both kernels through their gates on the desk build, rgm136's
whole ELF aace138c..., rgm211's 00402801...; both hosts' refusals in the build's sandbox, before the device stage; ET_DEVICES not a gate); RA1
THE WHOLE REAL PATH: rc 0 (the box check, the lock, et-who and ps, the card's identity gate and read, the smoke with every process gated GATE
OK on its real ELF and the walk read, the stop-path test after it, three runs gated); RA2 the lock held by another process: 16, no config read;
RA3 A HOST HUNG PAST ITS TERM in run 004: the real `timeout 10` sends its TERM at 10 s, the host ignores it, the runner writes HUNG at 14 s and
exits 8 with no closing config read, and NOTHING KILLS the host: it ends by itself at 16 s (its marker file); RA4 a device process of ours (a
stand-in named sys_emu): the real ps read refuses it: 16, no config read; RA5 the reader not at its pin: 16, no device opened; RA6 rgm211's
kernel with one byte of its .text changed: the box check's kernel gate refuses it: 16, no device opened; RA7 ET_DEVICES: (a) inherited by the
runner, it is dropped from the device environment; (b) a table that would set it: the box check refuses before any device: 16; (c) the REAL
guard run with ET_DEVICES=1, and with `sample --reset-ms`: refused (97) before the reader opens; RA8 another login on card 0 at the start: 16,
no config read; RA9 THE IDENTITY, the other card: (a) the reader's config naming card 1: 16 before the sampler; (b) the sampler holding card 1's
node: 16 before the smoke; (c) the host naming and holding card 1: the watch trips in the smoke's first process, the stop file, "stopping:",
16; RA10 a runtime line naming card 1 on the first run's host: STOP (identity), nothing further, rc 0; card 0's runtime line at the host's start
AND inside its first record: dropped, every record read whole, rc 0; RA11 the sampler dies in a run: the run ends flagged, the sampler restarts
through the real guard, rc 0; RA12 a build record without the builder: 16; RA13 the operator's STOP file touched in run 005 (the real path): run
006 never starts, rc 0; RA14 THE IDENTITY GATE PER PROCESS on real ELFs: rgm136's real ELF copied over rgm211's once the smoke has passed (after
the box check): run 004's gate (gemmLn) reads GATE FAILED (".text is rgm136's"), no process starts, the session stops, rc 0, no run; and in
process, the gate on the real ELFs both ways (gemmL and gemmLnc on rgm136's OK, gemmLn on rgm211's OK, gemmLn on rgm136's and gemmLnc on
rgm211's FAILED); RA15 THE WALK CHECK on the real path: rgm211's host stand-in printing walk_ok false in run 004: THE KERNEL STOPS, nothing
further, rc 0.
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
REL_E = "tools/claims-v3/e211"
READER = "build/ettelem/ettelem"
SHORT = ["004-X-x01n", "005-X-x01m", "006-X-x02n"]


def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class T:
    def __init__(self):
        self.n = self.ok = 0

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)


def make_tree(S):
    tree = os.path.join(S, "tree-A")
    # the file list from the harness check run as its own process (importing it here would load the lab clone's e211_common first, and the
    # stand-in tree's runner would then read the clone's paths)
    files = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "check_e211.py"), "--list"], capture_output=True, text=True).stdout.split()
    for rel in files + [REL_E + "/harness-e211.json"]:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e211.py")
    for rel, words in ((READER, ""), ("build/e211rgm-standin/rgm136/sparsity_host", " host --as rgm136"),
                       ("build/e211rgm-standin/rgm211/sparsity_host", " host --as rgm211")):
        p = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(f'#!/bin/sh\nexec /usr/bin/python3 -B "{fake}"{words} "$@"\n')
        os.chmod(p, 0o755)
    b = os.path.join(S, "bin-A")
    os.makedirs(b, exist_ok=True)
    with open(os.path.join(b, "et-who"), "w") as f:
        f.write(f'#!/bin/sh\nexec /usr/bin/python3 -B "{fake}" etwho\n')
    os.chmod(os.path.join(b, "et-who"), 0o755)
    shutil.copy2("/usr/bin/sleep", os.path.join(b, "sys_emu"))
    dev = os.path.join(S, "dev-A")
    os.makedirs(dev, exist_ok=True)
    lock = os.path.join(S, "lock-A", "etsoc-shire0.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    open(lock, "a").close()
    return tree, b, os.path.realpath(dev), lock


def real_build(tree):
    r = subprocess.run(["bash", os.path.join(tree, REL_E, "build_e211.sh")], cwd=tree, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def standin_record(tree, day, builder=True):
    ks = {}
    for k in ("rgm136", "rgm211"):
        host = os.path.join(tree, f"build/e211rgm/{k}/host/sparsity_host")
        os.makedirs(os.path.dirname(host), exist_ok=True)
        shutil.copy2(os.path.join(tree, f"build/e211rgm-standin/{k}/sparsity_host"), host)
        elf = os.path.join(tree, f"build/e211rgm/{k}/kernel/sparsity.elf")
        ks[k] = {"kernel_sha256": sha256(elf), "host_sha256": sha256(host), "kernel_gate": "KERNEL OK: (the real build's gate, RA0)"}
    rec = {"box": "aifoundry3", "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernels": ks, "host_checks": ["stand-in"],
           "what": "the real-path desk test's stand-in record (stand-in hosts beside the two real kernel ELFs)"}
    if builder:
        rec["builder"] = "build_e211.sh"
        rec["et_devices"] = "not a gate on aifoundry3 (one card)"
    with open(os.path.join(tree, "build/e211rgm/BUILD-e211.json"), "w") as f:
        json.dump(rec, f, indent=1)


REGISTERED_PIN = {}


def session(S, tree, name, env=None, pin_ok=True, seq="short", touch_after=None, on_line=None):
    import run_e211 as R
    C, N1 = R.C, R.N1
    out = os.path.join(S, f"A-{name}")
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E211_FAKE_")]:
        del os.environ[k]
    os.environ.update({"E211_FAKE_ARM": "A", "E211_FAKE_DEVDIR": N1.DEV_DIR, "E211_FAKE_LOCK": C.ARMS["A"]["lock"],
                       "E211_FAKE_SCHED": os.path.join(out, "sched.jsonl"), "E211_FAKE_SCALE": "0.05", "E211_FAKE_TAU_S": "0.5"})
    os.environ.update(env or {})
    open(os.environ["E211_FAKE_SCHED"], "a").close()
    want = C.ARMS["A"]["ettelem_sha256"]
    if not pin_ok:
        C.ARMS["A"]["ettelem_sha256"] = REGISTERED_PIN["A"]
    a = argparse.Namespace(what="session", arm="A", t0=int(time.time()), out=out, deadline_epoch=0, dry=False, sequence=seq,
                           rest_s=0.4, smoke_rest_s=1.5, tail_s=0.3, gate_wait_s=3.0, rule_s=C.CARD_RULE_S, cap_s=C.CAP_S)
    hook = touch_after or on_line
    if hook:                     # once the log names hook[0]: touch the session's STOP file (the operator), or call on_line's function
        def watcher():
            t0 = time.time()
            while time.time() - t0 < 120:
                lp = os.path.join(out, "session.log")
                if os.path.exists(lp) and hook[0] in open(lp).read():
                    time.sleep(hook[1])
                    if touch_after:
                        open(os.path.join(out, "STOP"), "a").close()
                    else:
                        hook[2]()
                    return
                time.sleep(0.05)
        threading.Thread(target=watcher, daemon=True).start()
    try:
        rc = R.Session(a).run()
    finally:
        C.ARMS["A"]["ettelem_sha256"] = want
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    return rc, log, out


def has_proc(d):
    for dp, dn, fn in os.walk(d):
        if any(n.startswith("proc") and n.endswith(".out") for n in fn):
            return True
    return False


def qj(d):
    return json.load(open(os.path.join(d, "queue.json"))) if os.path.exists(os.path.join(d, "queue.json")) else {}


def ran(d):
    return sum(1 for x in qj(d).get("queue", []) if x.get("ran"))


def rjson(d, key):
    p = os.path.join(d, "runs", key, "run.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def wait_marker(path, secs=40):
    t = time.time()
    while time.time() - t < secs:
        if os.path.exists(path):
            return open(path).read().strip()
        time.sleep(0.5)
    return ""


def cases(t, S):
    tree, b, dev, lock = make_tree(S)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e211 as R
    C, N1 = R.C, R.N1
    host = socket.gethostname()
    print(f"realpath_e211 arm A: hostname {host!r} (the namespace's), tree {os.path.relpath(tree, S)}, the runner, its common module and the gate "
          f"the tree's: {R.__file__ == os.path.join(tree, REL_E, 'run_e211.py') and C.__file__ == os.path.join(tree, REL_E, 'e211_common.py') and R.IG.__file__ == os.path.join(tree, REL_E, 'ident_e211.py')}", flush=True)
    if C.REPO != tree:
        t.case("RA-tree", False, f"the runner reads {C.REPO}, not the stand-in tree")
        return
    if host != "aifoundry3":
        t.case("RA-host", False, f"the namespace's hostname is {host!r}, not 'aifoundry3': run under desk/realpath_e211.sh")
        return
    REGISTERED_PIN["A"] = C.ARMS["A"]["ettelem_sha256"]
    C.ARMS["A"]["ettelem_sha256"] = sha256(os.path.join(tree, READER))
    C.ARMS["A"]["lock"] = lock
    N1.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    day = R.pacific_day()
    rc, txt = real_build(tree)
    rec = json.load(open(os.path.join(tree, "build/e211rgm/BUILD-e211.json"))) if os.path.exists(os.path.join(tree, "build/e211rgm/BUILD-e211.json")) else {}
    ks = rec.get("kernels") or {}
    hc = rec.get("host_checks") or []
    t.case("RA0", rc == 0 and "RGM-BUILT rc=0" in txt and rec.get("builder") == "build_e211.sh"
           and (ks.get("rgm136") or {}).get("kernel_sha256", "").startswith("aace138c") and (ks.get("rgm211") or {}).get("kernel_sha256", "").startswith("00402801")
           and all((ks.get(k) or {}).get("kernel_gate", "").startswith(f"KERNEL OK: {k}: ") for k in ("rgm136", "rgm211"))
           and len(hc) == 12 and all(x.endswith(":ok") for x in hc) and "not a gate on aifoundry3" in rec.get("et_devices", "") and rec.get("box") == "aifoundry3",
           f"rc {rc}; {[ln[:120] for ln in txt.splitlines() if ln.startswith(('KERNEL', 'ETDEVICES', 'RGM-'))]}; host checks {len(hc)} ({sum(1 for x in hc if x.endswith(':ok'))} ok)")
    if rc != 0:
        print(txt[-3000:])
        return
    real_elf = {k: os.path.join(tree, f"build/e211rgm/{k}/kernel/sparsity.elf") for k in ("rgm136", "rgm211")}
    keep_elf = {k: open(p, "rb").read() for k, p in real_elf.items()}
    standin_record(tree, day)
    # RA1: the whole real path
    rc, log, d = session(S, tree, "RA1")
    idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
    boxtxt = "".join(open(os.path.join(d, f)).read() for f in ("kernel-rgm136.txt", "kernel-rgm211.txt", "kernel-rgm136.err", "kernel-rgm211.err",
                                                                "harness.txt", "harness.err", "preflight.txt", "preflight.err") if os.path.exists(os.path.join(d, f)))
    ls = log.splitlines()
    i_sm = max([i for i, x in enumerate(ls) if "smoke s03: rc" in x] or [-1])
    i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
    sm = [json.load(open(os.path.join(d, "smoke", p, "smoke.json"))) for p in C.SMOKE_PIDS if os.path.exists(os.path.join(d, "smoke", p, "smoke.json"))]
    pr = [(rjson(d, k).get("procs") or [{}])[0] for k in SHORT]
    gates = [x.get("gate", "") for x in sm] + [p.get("gate", "") for p in pr]
    real_gate = all(g.startswith("GATE OK: ") and "the whole ELF" in g and "(dry" not in g for g in gates)
    q = qj(d)
    t.case("RA1", rc == 0 and "DRY" not in log and "the box and the builds" in log and boxtxt.count("KERNEL OK") == 2 and "HARNESS OK" in boxtxt
           and "dmcmd_audit: GO" in boxtxt and "smoke gate passed" in log and 0 <= i_sm < i_sp < 10 ** 6 and ran(d) == 3 and "config end: {" in log
           and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and idn.get("config_start", {}).get("targets") == ["/dev/et0_mgmt"]
           and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et0_mgmt"] and len(sm) == 3 and all(x["good"] for x in sm) and real_gate
           and [x.get("walk_ok") for x in sm] == [True, True, True] and [p.get("walk", {}).get("want") for p in pr] == ["nm", None, "nm"]
           and all(v["host"]["stderr_targets"] == ["/dev/et0_ops"] and v["host"]["nodes_held"] == ["/dev/et0_ops"] for v in idn.get("smoke", {}).values())
           and [x["run"] for x in q.get("queue", [])] == SHORT,
           f"rc {rc}; the box check {'passed' if 'the box and the builds' in log else 'NOT passed'} (both kernel gates, harness, preflight run); identity "
           f"{idn.get('config_start', {}).get('targets')} {idn.get('config_start', {}).get('ids')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}, "
           f"the sampler {idn.get('sampler_nodes', {}).get('nodes')}; the smoke {[round(x['cycles_ratio'], 3) for x in sm]} of MM1's counter mean, "
           f"then the stop-path test (lines {i_sm} < {i_sp}); the real gate on every process {real_gate} ({gates[1][:110]!r}); runs "
           f"{[x['run'] for x in q.get('queue', [])]}; real path (no DRY line) {'DRY' not in log}")
    # RA2: the lock held
    holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc, log, d = session(S, tree, "RA2")
    holder.terminate()          # the stand-in holder (a sleep under flock, no device), by SIGTERM
    holder.wait()
    t.case("RA2", rc == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
    # RA3: a host hung past its TERM under the real timeout 10
    t0 = time.time()
    rc, log, d = session(S, tree, "RA3", {"E211_FAKE_HOST": "hang_term", "E211_FAKE_HOST_POINTS": "x01n", "E211_FAKE_HANG_S": "16"})
    mk = wait_marker(os.path.join(d, "sched.jsonl.hang-ended"), 40)
    p0 = (rjson(d, "004-X-x01n").get("procs") or [{}])[0]
    t.case("RA3", rc == 8 and " HUNG: a device process (the host of 004-X-x01n" in log and "config end: not read (a device process of ours is HUNG" in log
           and p0.get("hung") is True and p0.get("t1_ms", 0) - p0.get("t0_ms", 0) >= 13500 and ran(d) == 1 and "ended by itself after 16" in mk,
           f"rc {rc}; run 004's host left after {(p0.get('t1_ms', 0) - p0.get('t0_ms', 0)) / 1000:.1f} s (timeout's TERM at 10 s ignored); the hung stand-in: "
           f"'{mk[:90]}' ({time.time() - t0:.0f} s after the session began); nothing killed it")
    # RA4: a device process of ours
    dp = subprocess.Popen([os.path.join(b, "sys_emu"), "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.3)
    rc, log, d = session(S, tree, "RA4")
    dp.terminate()              # the decoy (a copy of sleep named sys_emu, no device), by SIGTERM
    dp.wait()
    t.case("RA4", rc == 16 and "other device process(es) of ours" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
    # RA5: the reader not at its pin
    rc, log, d = session(S, tree, "RA5", pin_ok=False)
    t.case("RA5", rc == 16 and "refused, no device opened" in log and READER in log and not os.path.exists(os.path.join(d, "config-start.json")),
           f"rc {rc}; '{[ln[24:170] for ln in log.splitlines() if 'no device opened' in ln][:1]}'")
    # RA6: rgm211's kernel with a changed .text
    elf = real_elf["rgm211"]
    oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
    tb = os.path.join(S, "text-A.bin")
    subprocess.run([oc, "-O", "binary", "-j", ".text", elf, tb], check=False)
    tx = open(tb, "rb").read() if os.path.exists(tb) else b""
    keep = keep_elf["rgm211"]
    k = keep.find(tx[:64]) if tx else -1
    if k >= 0:
        bad = bytearray(keep)
        bad[k + 16] ^= 0x01
        open(elf, "wb").write(bytes(bad))
        standin_record(tree, day)
        rc, log, d = session(S, tree, "RA6")
        kt = open(os.path.join(d, "kernel-rgm211.txt")).read() if os.path.exists(os.path.join(d, "kernel-rgm211.txt")) else ""
        open(elf, "wb").write(keep)
        standin_record(tree, day)
        t.case("RA6", rc == 16 and "the kernel-rgm211 check did not read KERNEL OK" in log and "KERNEL FAILED: rgm211: gemmLn needs rgm211's .text" in kt
               and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{kt.strip()[:140]}'")
    else:
        t.case("RA6", False, "the .text bytes were not found in the ELF to change one")
    # RA7: ET_DEVICES
    os.environ["ET_DEVICES"] = "1"
    try:
        ns = argparse.Namespace(what="session", arm="A", t0=int(time.time()), out=os.path.join(S, "A-RA7-env"), deadline_epoch=0, dry=False,
                                sequence="short", rest_s=0.4, smoke_rest_s=1.5, tail_s=0.3, gate_wait_s=3.0, rule_s=C.CARD_RULE_S, cap_s=C.CAP_S)
        env_clean = "ET_DEVICES" not in R.Session(ns).env
    finally:
        del os.environ["ET_DEVICES"]
    C.ARMS["A"]["et_devices"] = "1"
    try:
        rc, log, d = session(S, tree, "RA7a")
    finally:
        C.ARMS["A"]["et_devices"] = None
    g = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e211.sh"), "config"], cwd=tree, capture_output=True,
                       text=True, env=dict(os.environ, ET_DEVICES="1"))
    g2 = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e211.sh"), "sample", "--reset-ms", "1"], cwd=tree,
                        capture_output=True, text=True)
    t.case("RA7", env_clean and rc == 16 and "carries ET_DEVICES" in log and not os.path.exists(os.path.join(d, "config-start.json")) and g.returncode == 97
           and "ET_DEVICES is '1' on aifoundry3" in g.stderr and "PCIe target" not in g.stderr and g2.returncode == 97 and "PCIe target" not in g2.stderr,
           f"(a) inherited ET_DEVICES dropped from the device environment: {env_clean}; (b) a table setting it: the runner rc {rc}: "
           f"'{[ln[24:150] for ln in log.splitlines() if 'ET_DEVICES' in ln][:1]}'; (c) the real guard rc {g.returncode}: "
           f"'{g.stderr.strip()[:110]}'; sample --reset-ms rc {g2.returncode}")
    # RA8: another login on card 0 at the start
    rc, log, d = session(S, tree, "RA8", {"E211_FAKE_ETWHO": "other"})
    t.case("RA8", rc == 16 and "holder line(s) of another login" in log and not os.path.exists(os.path.join(d, "config-start.json")),
           f"rc {rc}; '{[ln[24:160] for ln in log.splitlines() if 'refused' in ln][:1]}'")
    # RA9: the other card, three ways
    rc1, log1, d1 = session(S, tree, "RA9a", {"E211_FAKE_CONFIG": "card1"})
    rc2, log2, d2 = session(S, tree, "RA9b", {"E211_FAKE_SAMPLER": "card1"})
    rc3, log3, d3 = session(S, tree, "RA9c", {"E211_FAKE_HOST": "card1"})
    err = open(os.path.join(d3, "smoke", "s01", "proc.err")).read() if os.path.exists(os.path.join(d3, "smoke", "s01", "proc.err")) else ""
    t.case("RA9", rc1 == 16 and "the card's identity" in log1 and "/dev/et1_mgmt" in log1 and "sampler started" not in log1 and not has_proc(d1)
           and rc2 == 16 and "the identity read" in log2 and not has_proc(d2)
           and rc3 == 16 and os.path.exists(os.path.join(d3, "STOP")) and "stopping:" in err and "smoke gate failed" in log3
           and not os.path.isdir(os.path.join(d3, "smoke", "s02")),
           f"(a) config naming card 1: rc {rc1}; (b) the sampler on card 1: rc {rc2}; (c) the host on card 1: rc {rc3}, stopped by the file {'stopping:' in err}")
    # RA10: card 1's runtime line in the first run (identity stop); card 0's runtime line inside records (dropped)
    rc, log, d = session(S, tree, "RA10a", {"E211_FAKE_HOST": "runtime1", "E211_FAKE_HOST_POINTS": "x01n"})
    q = qj(d)
    rcb, logb, db = session(S, tree, "RA10b", {"E211_FAKE_HOST": "runtime"})
    smb = json.load(open(os.path.join(db, "smoke", "s02", "smoke.json"))) if os.path.exists(os.path.join(db, "smoke", "s02", "smoke.json")) else {}
    prb = (rjson(db, "004-X-x01n").get("procs") or [{}])[0]
    t.case("RA10", rc == 0 and ran(d) == 1 and "identity: the runtime named card(s) ['1']" in str(q.get("stop")) and "nothing further started" in log
           and rcb == 0 and ran(db) == 3 and smb.get("records", {}).get("runtime_lines") == 2 and smb.get("records", {}).get("unparsed") == 0
           and prb.get("records", {}).get("runtime_lines") == 2 and prb.get("records", {}).get("unparsed") == 0 and prb.get("check") in ("approx", "exact")
           and prb.get("walk_ok") is True,
           f"card 1's line: rc {rc}, the stop {str(q.get('stop'))[:90]!r}; card 0's line: rc {rcb}, the smoke's s02 records {smb.get('records')}, "
           f"run 004's {prb.get('records')} (walk ok {prb.get('walk_ok')})")
    # RA11: the sampler dies in a run
    rc, log, d = session(S, tree, "RA11", {"E211_FAKE_SAMPLER": "dies:24"})
    t.case("RA11", rc == 0 and "restarting it" in log and log.count("sampler started") >= 2 and ran(d) >= 2,
           f"rc {rc}; sampler starts {log.count('sampler started')}; runs {ran(d)}")
    # RA12: a build record without the builder
    standin_record(tree, day, builder=False)
    rc, log, d = session(S, tree, "RA12")
    standin_record(tree, day)
    t.case("RA12", rc == 16 and "not today's BUILT by build_e211.sh" in log and "refused, no device opened" in log, f"rc {rc}")
    # RA13: the operator's STOP file touched in run 005
    rc, log, d = session(S, tree, "RA13", touch_after=("run 005-", 0.4))
    q = qj(d)
    qq = q.get("queue", [])
    t.case("RA13", rc == 0 and len(qq) == 3 and not qq[-1].get("ran") and "the operator's STOP file" in str(q.get("stop"))
           and os.path.exists(os.path.join(d, "STOP")), f"rc {rc}; runs {[(x.get('run'), x.get('ran')) for x in qq]}; the stop {str(q.get('stop'))[:80]!r}")
    # RA14: THE IDENTITY GATE PER PROCESS on real ELFs: rgm136's ELF copied over rgm211's once the smoke has passed (the box check long done)
    def swap():
        open(real_elf["rgm211"], "wb").write(keep_elf["rgm136"])
    try:
        rc, log, d = session(S, tree, "RA14", on_line=("smoke gate passed", 0.0, swap))
    finally:
        open(real_elf["rgm211"], "wb").write(keep_elf["rgm211"])
    r4 = rjson(d, "004-X-x01n")
    inproc = {}
    for fam, k in (("gemmL", "rgm136"), ("gemmLnc", "rgm136"), ("gemmLn", "rgm211"), ("gemmLn", "rgm136"), ("gemmLnc", "rgm211"), ("gemmL", "rgm211")):
        good, words = R.IG.gate(fam, real_elf[k])
        inproc[f"{fam} on {k}"] = good
    want_ip = {"gemmL on rgm136": True, "gemmLnc on rgm136": True, "gemmLn on rgm211": True, "gemmLn on rgm136": False, "gemmLnc on rgm211": False,
               "gemmL on rgm211": False}
    t.case("RA14", rc == 0 and ran(d) == 0 and "smoke gate passed" in log and "STOP before run 004-X-x01n's process: the identity gate failed" in log
           and "rgm136's" in str(r4.get("gate_words")) and not os.path.exists(os.path.join(d, "runs", "004-X-x01n", "proc-00.out"))
           and "nothing further started" in log and inproc == want_ip,
           f"rc {rc}; runs {ran(d)}; run 004's gate {str(r4.get('gate_words'))[:150]!r}; the gate in process on the real ELFs {inproc}")
    # RA15: THE WALK CHECK on the real path
    rc, log, d = session(S, tree, "RA15", {"E211_FAKE_HOST": "walkbad", "E211_FAKE_HOST_POINTS": "x01n"})
    t.case("RA15", rc == 0 and ran(d) == 1 and "STOP: the kernel stops in run 004-X-x01n (gemmLn): " in log and "the walk check failed" in log
           and "nothing further started" in log, f"rc {rc}; runs {ran(d)}; '{[x[24:200] for x in log.splitlines() if 'STOP:' in x][:1]}'")


def main(argv):
    if len(argv) != 2 or argv[1] != "A":
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    if [x for x in os.listdir("/dev") if x.startswith("et")]:
        print("REFUSED: a /dev/et* node is visible: run this inside the sandbox (no /dev/et*, an empty /run/lock)")
        return 3
    os.makedirs(S, exist_ok=True)
    t = T()
    print(f"realpath_e211 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    cases(t, S)
    print(f"REALPATH-E211 arm A: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
