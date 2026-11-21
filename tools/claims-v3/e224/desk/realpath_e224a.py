#!/usr/bin/env python3
"""E224 ARM A's REAL-PATH desk test (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; the round's lesson: a branch the dry path skips is
exercised by a desk test of the real path), E215 arm A's desk/realpath_e215.py (landed in 8bde0182) for E224's one arm, its two families, its
family smoke s03 in its place and the G block. run_e224a.py's session WITHOUT --dry, on a stand-in box tree, as on the card day except for these
stand-ins:
  - the hostname: aifoundry1, from a private UTS namespace (desk/realpath_e224a.sh starts this driver under bubblewrap with --hostname, a private
    PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock);
  - the telemetry reader behind the REAL guard (ettelem_guard_e224a.sh, with its hostname and ET_DEVICES rules): build/ettelem/ettelem is a script
    that runs fake_card_e224a.py (config, sample); the runner's pin for it is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e224a.py etwho, which reads who holds the stand-in nodes and the stand-in lock from /proc;
  - the two hosts: build/e224argm/rgm136/host/sparsity_host and build/e224argm/rgm211/host/sparsity_host are scripts (the names the runner checks)
    that run fake_card_e224a.py host --as rgm136 and --as rgm211 (rgm211's with its walk fields); the build record carries their sha256; the two
    kernel ELFs are the REAL ones, built by the REAL build_e224a.sh in the stand-in tree (the kernel gate on rgm136 and the tree gate on rgm211 on
    this desk's toolchain), so THE IDENTITY GATE PER PROCESS reads rgm136's real ELF;
  - the card's lock: a writable stand-in file (the runner's lock path set to it in this process), and the card's nodes a stand-in directory
    (e224a_ident.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, the device environment's ET_DEVICES rule, the build record, its day and arm,
rgm136 through THE KERNEL GATE and rgm211 through THE TREE GATE (check_e224a.py --kernel rgm136|rgm211, the real objcopy), each host at its record,
the reader at its pin, the tiles, check_e224a.py --box and preflight_e224a.sh (dmcmd_audit_v2), both run), the lock (open, flock -n), the holders
(et-who through `timeout 20` and the real `ps`), the start config through the real guard under the real `timeout 10`, the card's identity gate,
the sampler through the real guard, the identity read, the opening smoke s01 (through the real identity gate on rgm136's real ELF, its counter's
mean in R0's band) THEN the stop-path test, the runs with each host under the real `timeout 10`, each gated, the G smoke s03 in its place (on
rgm211's host with rgm136's real ELF, the walk check), the closing config, the manifest. Timing: the desk's short reads and the doubles at a
twentieth of their time (the session's fields are set here; run_e224a.py's main() refuses them without --dry).

    python3 -B tools/claims-v3/e224/desk/realpath_e224a.py <scratch dir> A      (desk/realpath_e224a.sh runs it in its namespaces)

ARM A IS AIFOUNDRY1 CARD 1 (E215 arm B's cases RB0-RB12, on E218's code as the kit ports it): RA0 the REAL build_e224a.sh in the stand-in tree on
this desk's stock device layer: both kernels built and through their gates (rgm136 at its WHOLE ELF aace138c..., rgm211's tree 00402801...),
the hosts' refusals, then THE ET_DEVICES GATE: RGM-BUILD-FAILED "ET_DEVICES: a host has no ET_DEVICES" (this desk's device layer carries no
ET_DEVICES; on aifoundry1 it does: E215 arm B's build there read it), and the runner refuses the failed record: 16 (if this desk's layer ever
carries it, RGM-BUILT is read instead and said); every later case runs on a stand-in record with the ET_DEVICES reading beside the REAL ELFs;
RA1 THE WHOLE REAL PATH, the short sequence (t01, d25, p1r): rc 0, ET_DEVICES=1 in the runner's device environment, card 1's identity
(/dev/et1_mgmt, /dev/et1_ops, physical ID 1, 499 mV), the opening smoke s01 gated GATE OK on rgm136's real ELF at its whole ELF, the stop-path
test after it, three runs gated; RA1G THE G BLOCK ON THE REAL PATH (the lnc2 sequence: the third tie, s03 in its place, d30, g03): s03 after its
own rest, gated GATE OK on rgm136's real ELF on rgm211's host, the walk mn, good, at its place; then d30 and g03 each gated, the walk mn; RA2 the
lock held: 16, no config read; RA3 A HOST HUNG PAST ITS TERM in run 002: the real `timeout 10` sends its TERM at 10 s, the host ignores it,
HUNG, exit 8, no closing config read, NOTHING KILLS the host: it ends by itself (its marker); RA4 a device process of ours (a stand-in named
sys_emu): 16; RA5 the reader not at its pin: 16; RA6 rgm136's kernel with one byte of its .text changed: the box check's kernel gate refuses it:
16; RA6T rgm211's tree ELF with one byte of its .text changed: the tree gate refuses it: 16; RA7 A MISSING ET_DEVICES: (a) the runner's device
environment without it: 16 before any device; (b) the real guard with ET_DEVICES unset under aifoundry1: 97; (c) the real guard with
`sample --reset-ms`: 97; RA8 THE TWO-CARD HOLDER RULE: (a) another login on card 1: 16; (b) another login on card 0 at the start: 16; (c) a process
of ours holding card 0's node: 16; RA9 the other card (card 0) three ways (config, sampler, host): 16, and (d) a card reading 519 mV (over arm
A's 510 mV identity bound): 16; RA10 card 0's runtime line ("Opening device 0") on the first run's host: STOP (identity), rc 0; card 1's own line
inside records (s01's and run 002's): dropped, rc 0; RA11 the sampler dies in a run: restarted, rc 0; RA12 a build record without the builder:
16; RA13 the operator's STOP file touched in run 002: run 003 never starts, rc 0; RA14 THE IDENTITY GATE PER PROCESS ON REAL ELFS: rgm211's
real ELF copied over rgm136's once the G smoke has passed (lnc2): d30's gate reads GATE FAILED, no process, the session stops, rc 0; and in
process, the gate on the real ELFs for both families both ways and THE WALK ALONE CANNOT TELL; RA15 THE WALK CHECK on the real path: walk_ok false
on d30: THE KERNEL STOPS, rc 0; RA16 THE G SMOKE'S OWN STOP PATH ON THE REAL PATH (s03): (a) the walk fails at s03: the family 'rgm136 gemmLnc'
DROPPED, d30 and g03 never start, rc 0; (b) K1 at s03: the session stops (nothing dropped, no G run).
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
REL_E = "tools/claims-v3/e224"
READER = "build/ettelem/ettelem"
BOX = {"A": "aifoundry1"}
CARD = {"A": "1"}
OTHER = {"A": "0"}
SHORT = {"A": ["001-tie-t01", "002-pass1-d25", "003-pass1-p1r"]}
ETDEV_YES = "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"      # e224a_common.ETDEV_YES (E215 arm B's build reading)


def lnc_keys(C, arm):
    seq = C.sequence(arm)
    ti = [i for i, r in enumerate(seq) if r["block"] == "tie"][-1]
    return [C.run_key(r) for r in seq[ti:]]


def sjson(d, pid):
    p = os.path.join(d, "smoke", pid, "smoke.json")
    return json.load(open(p)) if os.path.exists(p) else {}


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


def make_tree(S, arm):
    tree = os.path.join(S, f"tree-{arm}")
    files = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "check_e224a.py"), "--list"], capture_output=True, text=True).stdout.split()
    for rel in files + [REL_E + "/harness-e224a.json"]:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e224a.py")
    for rel, words in ((READER, ""), ("build/e224argm-standin/rgm136/sparsity_host", " host --as rgm136"),
                       ("build/e224argm-standin/rgm211/sparsity_host", " host --as rgm211")):
        p = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(f'#!/bin/sh\nexec /usr/bin/python3 -B "{fake}"{words} "$@"\n')
        os.chmod(p, 0o755)
    b = os.path.join(S, f"bin-{arm}")
    os.makedirs(b, exist_ok=True)
    with open(os.path.join(b, "et-who"), "w") as f:
        f.write(f'#!/bin/sh\nexec /usr/bin/python3 -B "{fake}" etwho\n')
    os.chmod(os.path.join(b, "et-who"), 0o755)
    shutil.copy2("/usr/bin/sleep", os.path.join(b, "sys_emu"))
    dev = os.path.join(S, f"dev-{arm}")
    os.makedirs(dev, exist_ok=True)
    lock = os.path.join(S, f"lock-{arm}", f"etsoc-shire{CARD[arm]}.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    open(lock, "a").close()
    return tree, b, os.path.realpath(dev), lock


def real_build(tree):
    r = subprocess.run(["bash", os.path.join(tree, REL_E, "build_e224a.sh")], cwd=tree, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def standin_record(tree, arm, day, builder=True):
    ks = {}
    for k in ("rgm136", "rgm211"):
        host = os.path.join(tree, f"build/e224argm/{k}/host/sparsity_host")
        os.makedirs(os.path.dirname(host), exist_ok=True)
        shutil.copy2(os.path.join(tree, f"build/e224argm-standin/{k}/sparsity_host"), host)
        elf = os.path.join(tree, f"build/e224argm/{k}/kernel/sparsity.elf")
        ks[k] = {"kernel_sha256": sha256(elf), "host_sha256": sha256(host), "kernel_gate": "KERNEL OK: (the real build's gate, RA0)"}
    rec = {"box": BOX[arm], "arm": arm, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernels": ks, "host_checks": ["stand-in"],
           "what": "the real-path desk test's stand-in record (stand-in hosts beside the two real kernel ELFs)"}
    if builder:
        rec["builder"] = "build_e224a.sh"
        rec["et_devices"] = ETDEV_YES
    with open(os.path.join(tree, "build/e224argm/BUILD-e224a.json"), "w") as f:
        json.dump(rec, f, indent=1)


REGISTERED_PIN = {}


def session(S, arm, tree, name, env=None, pin_ok=True, seq="short", touch_after=None, on_line=None):
    import run_e224a as R
    C, N1 = R.C, R.N1
    out = os.path.join(S, f"{arm}-{name}")
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E224A_FAKE_")]:
        del os.environ[k]
    os.environ.update({"E224A_FAKE_ARM": arm, "E224A_FAKE_DEVDIR": N1.DEV_DIR, "E224A_FAKE_LOCK": C.ARMS[arm]["lock"],
                       "E224A_FAKE_SCHED": os.path.join(out, "sched.jsonl"), "E224A_FAKE_SCALE": "0.05", "E224A_FAKE_TAU_S": "0.5"})
    os.environ.update(env or {})
    open(os.environ["E224A_FAKE_SCHED"], "a").close()
    want = C.ARMS[arm]["ettelem_sha256"]
    if not pin_ok:
        C.ARMS[arm]["ettelem_sha256"] = REGISTERED_PIN[arm]
    a = argparse.Namespace(what="session", arm=arm, t0=int(time.time()), out=out, deadline_epoch=0, dry=False, sequence=seq,
                           rest_s=0.4, smoke_rest_s=1.5, tail_s=0.3, gate_wait_s=3.0, rule_s=C.ARMS[arm]["rule_s"], cap_s=C.ARMS[arm]["cap_s"])
    hook = touch_after or on_line
    if hook:                     # once the log names hook[0]: touch the session's STOP file (the operator), or call on_line's function
        def watcher():
            t0 = time.time()
            while time.time() - t0 < 150:
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
        C.ARMS[arm]["ettelem_sha256"] = want
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


def runs_of(d):
    return [x.get("run") for x in qj(d).get("queue", [])]


def wait_marker(path, secs=40):
    t = time.time()
    while time.time() - t < secs:
        if os.path.exists(path):
            return open(path).read().strip()
        time.sleep(0.5)
    return ""


def first_line(log, word):
    return [ln[24:200] for ln in log.splitlines() if word in ln][:1]


def setup(t, S, arm):
    tree, b, dev, lock = make_tree(S, arm)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e224a as R
    C, N1 = R.C, R.N1
    host = socket.gethostname()
    print(f"realpath_e224a arm {arm}: hostname {host!r} (the namespace's), tree {os.path.relpath(tree, S)}, the runner, its common module and the "
          f"gate the tree's: {R.__file__ == os.path.join(tree, REL_E, 'run_e224a.py') and C.__file__ == os.path.join(tree, REL_E, 'e224a_common.py') and R.IG.__file__ == os.path.join(tree, REL_E, 'ident_e224a.py')}", flush=True)
    if C.REPO != tree:
        t.case(f"R{arm}-tree", False, f"the runner reads {C.REPO}, not the stand-in tree")
        return None
    if host != BOX[arm]:
        t.case(f"R{arm}-host", False, f"the namespace's hostname is {host!r}, not {BOX[arm]!r}: run under desk/realpath_e224a.sh")
        return None
    REGISTERED_PIN[arm] = C.ARMS[arm]["ettelem_sha256"]
    C.ARMS[arm]["ettelem_sha256"] = sha256(os.path.join(tree, READER))
    C.ARMS[arm]["lock"] = lock
    N1.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    return tree, b, dev, lock, R, C, N1


def text_flip(elf, keep, S, tag):
    """the ELF's bytes with one byte of its .text changed (the .text found by objcopy's own bytes), or None"""
    oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
    tb = os.path.join(S, f"text-{tag}.bin")
    subprocess.run([oc, "-O", "binary", "-j", ".text", elf, tb], check=False)
    tx = open(tb, "rb").read() if os.path.exists(tb) else b""
    k = keep.find(tx[:64]) if tx else -1
    if k < 0:
        return None
    bad = bytearray(keep)
    bad[k + 16] ^= 0x01
    return bytes(bad)


def arm_a(t, S):
    st = setup(t, S, "A")
    if not st:
        return
    tree, b, dev, lock, R, C, N1 = st
    arm = "A"
    day = R.pacific_day()
    rc, txt = real_build(tree)
    rec = json.load(open(os.path.join(tree, "build/e224argm/BUILD-e224a.json"))) if os.path.exists(os.path.join(tree, "build/e224argm/BUILD-e224a.json")) else {}
    ks = rec.get("kernels") or {}
    hc = rec.get("host_checks") or []
    kl = [ln for ln in txt.splitlines() if ln.startswith("KERNEL")]
    both_gated = (any(ln.startswith("KERNEL rgm136 aace138c") and "KERNEL OK: rgm136: rgm136 gemmL: rgm136, " in ln for ln in kl)
                  and any(ln.startswith("KERNEL rgm211 00402801") and "KERNEL OK: rgm211: rgm211's tree: its ELF 00402801" in ln for ln in kl))
    elves = all(os.path.exists(os.path.join(tree, f"build/e224argm/{k}/kernel/sparsity.elf")) for k in ("rgm136", "rgm211"))
    refused = rc != 0 and "RGM-BUILD-FAILED: ET_DEVICES: a host has no ET_DEVICES" in txt and rec.get("verdict") == "BUILD-FAILED"
    built = rc == 0 and "RGM-BUILT rc=0" in txt and rec.get("et_devices") == ETDEV_YES and len(hc) == 12 and all(x.endswith(":ok") for x in hc)
    rcf = None
    if refused:
        rcf, logf, df = session(S, arm, tree, "RA0-failed-record")
    t.case("RA0", both_gated and elves and ((refused and rcf == 16 and "refused, no device opened" in logf) or built),
           f"rc {rc}; {'REFUSED at the ET_DEVICES gate (this desk' + chr(39) + 's device layer carries none), the runner on that record rc ' + str(rcf) if refused else 'BUILT (this desk' + chr(39) + 's layer carries ET_DEVICES)' if built else 'neither'}; "
           f"{[ln[:120] for ln in txt.splitlines() if ln.startswith(('KERNEL', 'ETDEVICES', 'RGM-'))]}")
    if not (both_gated and elves):
        print(txt[-3000:])
        return
    real_elf = {k: os.path.join(tree, f"build/e224argm/{k}/kernel/sparsity.elf") for k in ("rgm136", "rgm211")}
    keep_elf = {k: open(p, "rb").read() for k, p in real_elf.items()}
    standin_record(tree, arm, day)
    # RA1: the whole real path, the short sequence
    rc, log, d = session(S, arm, tree, "RA1")
    idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
    boxtxt = "".join(open(os.path.join(d, f)).read() for f in ("kernel-rgm136.txt", "kernel-rgm211.txt", "kernel-rgm136.err", "kernel-rgm211.err",
                                                                "harness.txt", "harness.err", "preflight.txt", "preflight.err") if os.path.exists(os.path.join(d, f)))
    ls = log.splitlines()
    i_sm = max([i for i, x in enumerate(ls) if "smoke s01: the identity gate GATE OK; rc" in x] or [-1])
    i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
    sm = sjson(d, "s01")
    pr = [(rjson(d, k).get("procs") or [{}])[0] for k in SHORT[arm]]
    gates = [sm.get("gate", "")] + [p.get("gate", "") for p in pr]
    real_gate = all(g.startswith("GATE OK: rgm136 gemmL: rgm136, ") and "the whole ELF" in g and "(dry" not in g for g in gates)
    t.case("RA1", rc == 0 and "DRY" not in log and "the box and the builds" in log and boxtxt.count("KERNEL OK") == 2 and "TREE OK" not in boxtxt
           and "rgm211's tree: its ELF" in boxtxt and "HARNESS OK" in boxtxt
           and "dmcmd_audit: GO" in boxtxt and "smoke gate passed" in log and 0 <= i_sm < i_sp < 10 ** 6 and ran(d) == 3 and "config end: {" in log
           and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and idn.get("config_start", {}).get("targets") == ["/dev/et1_mgmt"]
           and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et1_mgmt"] and sm.get("good") is True and real_gate
           and sm.get("family") == "rgm136 gemmL" and sm.get("cycles_in_band") and not os.path.isdir(os.path.join(d, "smoke", "s03"))
           and all(v["host"]["stderr_targets"] == ["/dev/et1_ops"] and v["host"]["nodes_held"] == ["/dev/et1_ops"] for v in idn.get("smoke", {}).values())
           and runs_of(d) == SHORT[arm],
           f"rc {rc}; the box check {'passed' if 'the box and the builds' in log else 'NOT passed'} (the kernel and tree gates, harness, preflight run); identity "
           f"{idn.get('config_start', {}).get('targets')} {idn.get('config_start', {}).get('ids')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}, "
           f"the sampler {idn.get('sampler_nodes', {}).get('nodes')}; s01's counter mean {sm.get('counted_cycles_per_op')} (R0's band), then the stop-path "
           f"test (lines {i_sm} < {i_sp}); the real gate on every process {real_gate} ({gates[0][:110]!r}); runs {runs_of(d)}; real path (no DRY line) "
           f"{'DRY' not in log}")
    # RA1G: the G block on the real path (the lnc2 sequence)
    rc, log, d = session(S, arm, tree, "RA1G", seq="lnc2")
    lk = lnc_keys(R.C, arm)[:4]
    s3 = sjson(d, "s03")
    pr = [(rjson(d, k).get("procs") or [{}])[0] for k in lk if "-G-pass" in k]
    ok = (rc == 0 and runs_of(d) == lk and s3.get("good") is True and str(s3.get("gate", "")).startswith("GATE OK: rgm136 gemmLnc: rgm136, ")
          and "(dry" not in str(s3.get("gate", "")) and s3.get("host") == "rgm211" and s3.get("kernel") == "rgm136" and s3.get("sequence_n") == int(lk[1][:3])
          and s3.get("walk_ok") is True and (s3.get("walk") or {}).get("want") == "mn" and "/rgm211/host/" in str((s3.get("argv") or ["x"])[0])
          and len(pr) == 2 and all(str(p.get("gate", "")).startswith("GATE OK: rgm136 gemmLnc: rgm136, ") and p.get("walk_ok") is True
                                   and (p.get("walk") or {}).get("want") == "mn" and p.get("host") == "rgm211" and p.get("kernel") == "rgm136"
                                   and p.get("rc") == 0 and p.get("check") in ("exact", "approx") for p in pr) and "STOP" not in log)
    t.case("RA1G", ok, f"rc {rc}; s03's real gate {str(s3.get('gate'))[:80]!r}, good {s3.get('good')}, place {s3.get('sequence_n')}, walk "
           f"{(s3.get('walk') or {}).get('want')} ok {s3.get('walk_ok')}; then {[(p.get('family'), p.get('host'), p.get('kernel'), str(p.get('gate'))[:7], p.get('walk_ok')) for p in pr]}")
    # RA2: the lock held
    holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc, log, d = session(S, arm, tree, "RA2")
    holder.terminate()          # the stand-in holder (a sleep under flock, no device), by SIGTERM
    holder.wait()
    t.case("RA2", rc == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
    # RA3: a host hung past its TERM under the real timeout 10
    t0 = time.time()
    rc, log, d = session(S, arm, tree, "RA3", {"E224A_FAKE_HOST": "hang_term", "E224A_FAKE_HOST_POINTS": "d25", "E224A_FAKE_HANG_S": "16"})
    mk = wait_marker(os.path.join(d, "sched.jsonl.hang-ended"), 40)
    p0 = (rjson(d, SHORT[arm][1]).get("procs") or [{}])[0]
    t.case("RA3", rc == 8 and f" HUNG: a device process (the host of {SHORT[arm][1]}" in log and "config end: not read (a device process of ours is HUNG" in log
           and p0.get("hung") is True and p0.get("t1_ms", 0) - p0.get("t0_ms", 0) >= 13500 and ran(d) == 2 and "ended by itself after 16" in mk,
           f"rc {rc}; run 002's host left after {(p0.get('t1_ms', 0) - p0.get('t0_ms', 0)) / 1000:.1f} s (timeout's TERM at 10 s ignored); the hung stand-in: "
           f"'{mk[:90]}' ({time.time() - t0:.0f} s after the session began); nothing killed it")
    # RA4: a device process of ours
    dp = subprocess.Popen([os.path.join(b, "sys_emu"), "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.3)
    rc, log, d = session(S, arm, tree, "RA4")
    dp.terminate()              # the decoy (a copy of sleep named sys_emu, no device), by SIGTERM
    dp.wait()
    t.case("RA4", rc == 16 and "other device process(es) of ours" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
    # RA5: the reader not at its pin
    rc, log, d = session(S, arm, tree, "RA5", pin_ok=False)
    t.case("RA5", rc == 16 and "refused, no device opened" in log and READER in log and not os.path.exists(os.path.join(d, "config-start.json")),
           f"rc {rc}; '{first_line(log, 'no device opened')}'")
    # RA6 / RA6T: a changed .text in rgm136's ELF (the kernel gate) and in rgm211's tree ELF (the tree gate)
    for name, k, want in (("RA6", "rgm136", "KERNEL FAILED: rgm136: rgm136 gemmL needs rgm136's .text"),
                          ("RA6T", "rgm211", "KERNEL FAILED: rgm211: rgm211's tree: its ELF")):
        bad = text_flip(real_elf[k], keep_elf[k], S, k)
        if bad is None:
            t.case(name, False, "the .text bytes were not found in the ELF to change one")
            continue
        open(real_elf[k], "wb").write(bad)
        standin_record(tree, arm, day)
        rc, log, d = session(S, arm, tree, name)
        kt = open(os.path.join(d, f"kernel-{k}.txt")).read() if os.path.exists(os.path.join(d, f"kernel-{k}.txt")) else ""
        open(real_elf[k], "wb").write(keep_elf[k])
        standin_record(tree, arm, day)
        t.case(name, rc == 16 and f"the kernel-{k} check did not read KERNEL OK" in log and want in kt
               and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{kt.strip()[:150]}'")
    # RA7: A MISSING ET_DEVICES (aifoundry1: card 1 only through ET_DEVICES=1)
    C.ARMS[arm]["et_devices"] = None
    try:
        rc, log, d = session(S, arm, tree, "RA7a")
    finally:
        C.ARMS[arm]["et_devices"] = "1"
    genv = {k: v for k, v in os.environ.items() if k != "ET_DEVICES"}
    g = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e224a.sh"), "config"], cwd=tree, capture_output=True,
                       text=True, env=genv)
    g2 = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e224a.sh"), "sample", "--reset-ms", "1"], cwd=tree,
                        capture_output=True, text=True, env=dict(genv, ET_DEVICES="1"))
    t.case("RA7", rc == 16 and "lacks ET_DEVICES=1" in log and not os.path.exists(os.path.join(d, "config-start.json")) and g.returncode == 97
           and "ET_DEVICES is 'unset' on aifoundry1" in g.stderr and "PCIe target" not in g.stderr and g2.returncode == 97 and "PCIe target" not in g2.stderr,
           f"(a) the device environment without ET_DEVICES: the runner rc {rc}: '{first_line(log, 'ET_DEVICES')}'; (b) the real guard with ET_DEVICES "
           f"unset rc {g.returncode}: '{g.stderr.strip()[:110]}'; (c) sample --reset-ms rc {g2.returncode}")
    # RA8: THE TWO-CARD HOLDER RULE: another login on card 1; another login on card 0 at the start; a process of ours on card 0
    rca, loga, da = session(S, arm, tree, "RA8a", {"E224A_FAKE_ETWHO": "other"})
    rcb, logb, db = session(S, arm, tree, "RA8b", {"E224A_FAKE_ETWHO": "other1"})
    rcc, logc, dc = session(S, arm, tree, "RA8c", {"E224A_FAKE_ETWHO": "ours1"})
    t.case("RA8", rca == 16 and "holder line(s) of another login on card 1" in loga and not os.path.exists(os.path.join(da, "config-start.json"))
           and rcb == 16 and "of another login on card 0" in logb and not os.path.exists(os.path.join(db, "config-start.json"))
           and rcc == 16 and "of ours on card 0" in logc and not os.path.exists(os.path.join(dc, "config-start.json")),
           f"(a) card 1, another login: rc {rca} '{first_line(loga, 'refused')}'; (b) card 0, another login: rc {rcb} '{first_line(logb, 'refused')}'; "
           f"(c) card 0, ours: rc {rcc} '{first_line(logc, 'refused')}'")
    # RA9: the other card (card 0), three ways; and a card reading 519 mV
    rc1, log1, d1 = session(S, arm, tree, "RA9a", {"E224A_FAKE_CONFIG": "card1"})
    rc2, log2, d2 = session(S, arm, tree, "RA9b", {"E224A_FAKE_SAMPLER": "card1"})
    rc3, log3, d3 = session(S, arm, tree, "RA9c", {"E224A_FAKE_HOST": "card1"})
    err = open(os.path.join(d3, "smoke", "s01", "proc.err")).read() if os.path.exists(os.path.join(d3, "smoke", "s01", "proc.err")) else ""
    rc4, log4, d4 = session(S, arm, tree, "RA9d", {"E224A_FAKE_CONFIG": "mv519"})
    t.case("RA9", rc4 == 16 and "the card's identity" in log4 and "sampler started" not in log4 and not has_proc(d4)
           and rc1 == 16 and "the card's identity" in log1 and "/dev/et0_mgmt" in log1 and "sampler started" not in log1 and not has_proc(d1)
           and rc2 == 16 and "the identity read" in log2 and not has_proc(d2)
           and rc3 == 16 and os.path.exists(os.path.join(d3, "STOP")) and "stopping:" in err and "smoke gate failed" in log3 and ran(d3) == 0,
           f"(a) config naming card 0: rc {rc1}; (b) the sampler on card 0: rc {rc2}; (c) the host on card 0: rc {rc3}, stopped by the file {'stopping:' in err}; "
           f"(d) 519 mV: rc {rc4} '{first_line(log4, 'identity')}'")
    # RA10: card 0's runtime line in the first run (identity stop); card 1's own runtime line inside records (dropped)
    rc, log, d = session(S, arm, tree, "RA10a", {"E224A_FAKE_HOST": "runtime1", "E224A_FAKE_HOST_POINTS": "t01"})
    q = qj(d)
    rcb, logb, db = session(S, arm, tree, "RA10b", {"E224A_FAKE_HOST": "runtime"})
    smb = sjson(db, "s01")
    prb = (rjson(db, SHORT[arm][1]).get("procs") or [{}])[0]
    t.case("RA10", rc == 0 and ran(d) == 1 and "identity: the runtime named card(s) ['0']" in str(q.get("stop")) and "nothing further started" in log
           and rcb == 0 and ran(db) == 3 and smb.get("records", {}).get("runtime_lines") == 2 and smb.get("records", {}).get("unparsed") == 0
           and prb.get("records", {}).get("runtime_lines") == 2 and prb.get("records", {}).get("unparsed") == 0 and prb.get("check") in ("approx", "exact"),
           f"card 0's line: rc {rc}, the stop {str(q.get('stop'))[:90]!r}; card 1's own line: rc {rcb}, s01's records {smb.get('records')}, "
           f"run 002's {prb.get('records')}")
    # RA11: the sampler dies in a run (past the opening smoke's one process, about 7 launches, and the tie's)
    rc, log, d = session(S, arm, tree, "RA11", {"E224A_FAKE_SAMPLER": "dies:14"})
    t.case("RA11", rc == 0 and "restarting it" in log and log.count("sampler started") >= 2 and ran(d) >= 2,
           f"rc {rc}; sampler starts {log.count('sampler started')}; runs {ran(d)}")
    # RA12: a build record without the builder
    standin_record(tree, arm, day, builder=False)
    rc, log, d = session(S, arm, tree, "RA12")
    standin_record(tree, arm, day)
    t.case("RA12", rc == 16 and "not today's BUILT by build_e224a.sh" in log and "refused, no device opened" in log, f"rc {rc}")
    # RA13: the operator's STOP file touched in run 002
    rc, log, d = session(S, arm, tree, "RA13", touch_after=("run 002-", 0.4))
    q = qj(d)
    qq = q.get("queue", [])
    t.case("RA13", rc == 0 and len(qq) == 3 and not qq[-1].get("ran") and "the operator's STOP file" in str(q.get("stop"))
           and os.path.exists(os.path.join(d, "STOP")), f"rc {rc}; runs {[(x.get('run'), x.get('ran')) for x in qq]}; the stop {str(q.get('stop'))[:80]!r}")
    # RA14: THE IDENTITY GATE PER PROCESS on real ELFs: rgm211's ELF copied over rgm136's once the G smoke has passed
    def swap():
        open(real_elf["rgm136"], "wb").write(keep_elf["rgm211"])
    try:
        rc, log, d = session(S, arm, tree, "RA14", seq="lnc2", on_line=("smoke s03: rc 0", 0.0, swap))
    finally:
        open(real_elf["rgm136"], "wb").write(keep_elf["rgm136"])
    lk = lnc_keys(R.C, arm)[:4]
    r8 = rjson(d, lk[2])
    inproc = {}
    for fam in ("rgm136 gemmL", "rgm136 gemmLnc"):
        for k in ("rgm136", "rgm211"):
            good_, words = R.IG.gate(fam, os.path.join(S, f"real-{k}.elf") if os.path.exists(os.path.join(S, f"real-{k}.elf")) else real_elf[k])
            inproc[f"{fam} on {k}"] = good_
    want_ip = {f"{fam} on {k}": (k == "rgm136") for fam in R.IG.FAMILY_KERNEL for k in ("rgm136", "rgm211")}
    # the walk alone cannot tell: rgm211's host stand-in given rgm211's ELF for a gemmLnc arm reads walk mn and walk_ok true
    fake = os.path.join(tree, REL_E, "fake_card_e224a.py")
    argv = R.C.host_argv(tree, "d30", 2, 3.5, os.path.join(S, "nostop"))
    argv[argv.index("--kernel") + 1] = real_elf["rgm211"]
    wenv = {k: v for k, v in os.environ.items() if not k.startswith("E224A_FAKE_")}
    wenv.update({"E224A_FAKE_ARM": "A", "E224A_FAKE_SCALE": "0.05", "E224A_FAKE_POINT": "d30"})
    wo = subprocess.run(["/usr/bin/python3", "-B", fake, "host", "--as", "rgm211"] + argv[1:], capture_output=True, text=True, env=wenv)
    fma, chk, _ = R.C.host_records(wo.stdout, argv)
    wok, wwords, _ = R.C.walk_check("rgm136 gemmLnc", fma, chk)
    s3r = sjson(d, "s03")
    s3_ok = s3r.get("good") is True and str(s3r.get("gate", "")).startswith("GATE OK: ") and "(dry" not in str(s3r.get("gate", ""))
    t.case("RA14", rc == 0 and ran(d) == 2 and f"STOP before run {lk[2]}'s process: the identity gate failed" in log
           and "rgm211's" in str(r8.get("gate_words")) and not os.path.exists(os.path.join(d, "runs", lk[2], "proc-00.out"))
           and "nothing further started" in log and inproc == want_ip and wok and wo.returncode == 0 and s3_ok,
           f"rc {rc}; entries ran {ran(d)}; the G smoke s03 good on its real gate before the swap {s3_ok}; {lk[2]}'s gate {str(r8.get('gate_words'))[:150]!r}; "
           f"the gate in process on the real ELFs {sum(1 for v in inproc.values() if v)} OK of 4 as wanted {inproc == want_ip}; the walk alone with "
           f"rgm211's ELF for d30: walk_ok {wok} ({wwords[:60]}), host rc {wo.returncode}: only the gate refuses it")
    # RA15: THE WALK CHECK on the real path, a G run
    rc, log, d = session(S, arm, tree, "RA15", {"E224A_FAKE_HOST": "walkbad", "E224A_FAKE_HOST_POINTS": "d30"}, seq="lnc2")
    t.case("RA15", rc == 0 and ran(d) == 3 and f"STOP: the kernel stops in run {lk[2]} (rgm136 gemmLnc): " in log and "the walk check failed" in log
           and "nothing further started" in log and not os.path.isdir(os.path.join(d, "runs", lk[3])),
           f"rc {rc}; entries ran {ran(d)}; '{[x[24:200] for x in log.splitlines() if 'STOP:' in x][:1]}'")
    # RA16: the G smoke's own stop path on the real path (s03)
    rc, log, d = session(S, arm, tree, "RA16a", {"E224A_FAKE_HOST": "walkbad", "E224A_FAKE_HOST_POINTS": "s03"}, seq="lnc2")
    q = qj(d)
    s3 = sjson(d, "s03")
    qa = [x for x in q.get("queue", []) if "-G-pass" in x.get("run", "")]
    ok_a = (rc == 0 and "smoke s03: FAILED for its family alone (its own stop path, E224.md 3)" in log and str(s3.get("gate", "")).startswith("GATE OK: ")
            and "(dry" not in str(s3.get("gate", "")) and s3.get("walk_ok") is False and s3.get("a1_family_dropped") == "rgm136 gemmLnc" and len(qa) == 2
            and all(x.get("ran") is False and "was dropped by its smoke s03" in x.get("why", "") for x in qa)
            and not any(os.path.isdir(os.path.join(d, "runs", x.get("run", "-"))) for x in qa) and "rgm136 gemmLnc" in (q.get("families_dropped") or {})
            and "STOP" not in log)
    rc2, log2, d2 = session(S, arm, tree, "RA16b", {"E224A_FAKE_HOST": "k1", "E224A_FAKE_HOST_POINTS": "s03"}, seq="lnc2")
    s3b = sjson(d2, "s03")
    ok_b = (rc2 == 0 and "K1: a launch of the gemmLnc smoke s03 did not finish" in log2 and "nothing further started" in log2 and ran(d2) == 2
            and s3b.get("a1_family_dropped") is None and "K1" in str(s3b.get("a1_session_level")) and not qj(d2).get("families_dropped")
            and not any(os.path.isdir(os.path.join(d2, "runs", k)) for k in lk[2:]))
    t.case("RA16", ok_a and ok_b,
           f"(a) rc {rc}; s03's real gate {str(s3.get('gate'))[:60]!r}, walk_ok {s3.get('walk_ok')}, dropped {s3.get('a1_family_dropped')!r}; the "
           f"family's runs {[(x.get('run', '')[4:], x.get('ran')) for x in qa]}; (b) rc {rc2}; '{first_line(log2, 'STOP:')}'; s03's session-level "
           f"reading {s3b.get('a1_session_level')!r}")


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
    print(f"realpath_e224a ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    arm_a(t, S)
    print(f"REALPATH-E224A arm {argv[1]}: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
