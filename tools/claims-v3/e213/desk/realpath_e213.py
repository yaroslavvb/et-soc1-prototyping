#!/usr/bin/env python3
"""E213's REAL-PATH desk test (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum; the round's lesson: a branch the dry path skips is
exercised by a desk test of the real path), E211's desk/realpath_e211.py (arm A, its two kernels and hosts; landed in 2b7f261f) with E206's arm B
cases (desk/realpath_e206.py, landed in 906699ea), for E213's two arms and four families. run_e213.py's session WITHOUT --dry, on a stand-in box
tree, as on the card day except for these stand-ins:
  - the hostname: the arm's box (aifoundry3 or aifoundry1), from a private UTS namespace (desk/realpath_e213.sh starts this driver under bubblewrap
    with --hostname, a private PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock);
  - the telemetry reader behind the REAL guard (ettelem_guard_e213.sh, with its hostname and ET_DEVICES rules): build/ettelem/ettelem is a script
    that runs fake_card_e213.py (config, sample); the runner's pin for it is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e213.py etwho, which reads who holds the stand-in nodes and the stand-in lock from /proc;
  - the two hosts: build/e213rgm/rgm136/host/sparsity_host and build/e213rgm/rgm211/host/sparsity_host are scripts (the names the runner checks)
    that run fake_card_e213.py host --as rgm136 and --as rgm211 (rgm211's with its walk fields); the build record carries their sha256; the two
    kernel ELFs are the REAL ones, built by the REAL build_e213.sh in arm A's stand-in tree (the kernel gates on this desk's toolchain), so THE
    IDENTITY GATE PER PROCESS reads real ELFs (arm B's tree gets the same real ELFs: this desk's riscv gcc prints "() 15.1.0", as aifoundry1's);
  - the card's lock: a writable stand-in file (the runner's lock path set to it in this process), and the card's nodes a stand-in directory
    (e213_ident.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, the device environment's ET_DEVICES rule, the build record, its day and arm and
on arm B its ET_DEVICES reading, each kernel through THE KERNEL GATE (check_e213.py --kernel rgm136|rgm211, arm B rgm136 --whole: the kit's gate,
the real objcopy), each host at its record, the reader at its pin, the tiles, check_e213.py --box and preflight_e213.sh (dmcmd_audit_v2), both
run), the lock (open, flock -n), the holders (et-who through `timeout 20` and the real `ps`), the start config through the real guard under the real
`timeout 10`, the card's identity gate, the sampler through the real guard, the identity read, the smoke (each process through the real identity
gate on its real ELF, its counter's mean in R0's band, the walk check) THEN the stop-path test, the runs with each host under the real `timeout
10`, each gated, the closing config, the manifest. Timing: the desk's short reads and the doubles at a twentieth of their time (the session's
fields are set here; run_e213.py's main() refuses them without --dry).

    python3 -B tools/claims-v3/e213/desk/realpath_e213.py <scratch dir> A|B      (desk/realpath_e213.sh runs it in its namespaces)

Arm A (hostname aifoundry3): RA0 the REAL build_e213.sh in the stand-in tree (RGM-BUILT; both kernels through their gates, rgm136's whole ELF
aace138c..., rgm211's 00402801...; both hosts' twelve refusals in the build's sandbox, before the device stage; ET_DEVICES not a gate); RA1 THE
WHOLE REAL PATH, the short sequence (t01, a039, a005): rc 0, the smoke s01-s04 (s04 by Amendment A1) each gated GATE OK on its real ELF with the walk read, the
stop-path test after it, three runs gated; RA1K THE FOUR FAMILIES ON THE REAL PATH: every run of rgm211's host in pass 1 (a084 a085 a086 a080 a081
a082 a077 a078 a079 a073 a074 a075 a087), each gated GATE OK by its loop on its real ELF ('rgm211 gemmL' on rgm211's), the walk nm for gemmLn and
mn for the others; RA2 the lock held: 16, no config read; RA3 A HOST HUNG PAST ITS TERM in run 002: the real `timeout 10` sends its TERM at 10 s,
the host ignores it, HUNG at 14 s, exit 8, no closing config read, NOTHING KILLS the host: it ends by itself (its marker); RA4 a device process of
ours (a stand-in named sys_emu): 16; RA5 the reader not at its pin: 16; RA6 rgm211's kernel with one byte of its .text changed: the box check's
kernel gate refuses it: 16; RA7 ET_DEVICES: (a) inherited, dropped; (b) a table setting it: 16; (c) the real guard with ET_DEVICES=1 and with
`sample --reset-ms`: 97; RA8 another login on card 0 at the start: 16; RA9 the other card three ways (config, sampler, host): 16; RA10 card 1's
runtime line on the first run's host: STOP (identity), rc 0; card 0's line inside records: dropped, rc 0; RA11 the sampler dies in a run: restarted,
rc 0; RA12 a build record without the builder: 16; RA13 the operator's STOP file touched in run 002: run 003 never starts, rc 0; RA14 THE NEW
FAMILY'S IDENTITY GATE ON REAL ELFS (the orchestrator's condition for keeping a074, a078, a081, a085): rgm136's real ELF copied over rgm211's once
the smoke has passed (s04, the family's own smoke by Amendment A1, good on its real gate before it): the first 'rgm211 gemmL' run's gate (a085) reads GATE FAILED (".text is rgm136's"), no process, the session stops, rc 0;
and in process, the gate on the real ELFs for all four families both ways (each family on its own ELF OK, on the other ELF FAILED) and THE WALK
ALONE CANNOT TELL: rgm211's host stand-in given rgm136's ELF for a gemmL arm reads walk mn, walk_ok true (only the gate refuses it); RA15 THE WALK
CHECK on the real path: walk_ok false on a085 ('rgm211 gemmL'): THE KERNEL STOPS, rc 0; RA16 AMENDMENT A1, THE FAMILY SMOKE'S OWN STOP PATH ON THE
REAL PATH: (a) the walk fails at s04 (its real gate passed on rgm211's real ELF): the family 'rgm211 gemmL' DROPPED, the stop-path test passes,
the gemmL211 sequence's four runs never start (no run folder; "Amendment A1" in queue.json), rc 0; (b) K1 at s04: the session stops at the smoke
(16), nothing dropped, no run.
Arm B (hostname aifoundry1): RB0 the REAL build on this desk's stock device layer (no ET_DEVICES in it): RGM-BUILD-FAILED "ET_DEVICES: a host has
no ET_DEVICES", and the runner then refuses the failed record: 16; RB1 THE WHOLE REAL PATH with a stand-in record (the ET_DEVICES reading) and the
REAL ELFs: ET_DEVICES=1 through the real guard, card 1's identity (499 mV), the smoke s11-s14 (s14 rgm136's ELF on rgm211's host, the walk mn), each
gated at rgm136's WHOLE ELF, the stop-path test, three runs (t02, k03, k18), rc 0; RB1K arm B's gemmLnc runs (k40, k37, k38, k39) on the real path,
each on rgm211's host with rgm136's real ELF at its whole ELF, the walk mn; RB2 the config naming card 0 (519 mV): 16 before the sampler; RB3 the
sampler holding card 0's node: 16; RB4 the host naming card 0: the watch trips, "stopping:", 16; RB5 A MISSING ET_DEVICES: (a) the runner's device
environment without it: 16; (b) the real guard with ET_DEVICES unset under aifoundry1: 97; RB6 (a) another login on card 0 at the start: 16; (b) a
process of ours holding card 0's node: 16; RB7 the sampler dies in a run: restarted, rc 0; RB8 aifoundry1's runtime line ("Opening device 1", its
own) at the host's start and inside its first record: dropped, rc 0; "Opening device 0" on the first run's host: STOP (identity), rc 0; RB9 THE
WHOLE ELF ON ARM B: an ELF whose loadable identity is rgm136's but whose whole bytes are not (a changed .comment, aifoundry3's form): arm A's gate
passes it, arm B's box check refuses it (KERNEL FAILED ... requires the whole ELF): 16; RB10 a host hung past its TERM: HUNG, rc 8, nothing killed;
RB11 THE IDENTITY GATE PER PROCESS on arm B: rgm211's real ELF copied over rgm136's once the smoke has passed: the next run's gate reads GATE FAILED,
no process, rc 0.
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
REL_E = "tools/claims-v3/e213"
READER = "build/ettelem/ettelem"
BOX = {"A": "aifoundry3", "B": "aifoundry1"}
CARD = {"A": "0", "B": "1"}
SHORT = {"A": ["001-tie-t01", "002-pass1-a039", "003-pass1-a005"], "B": ["001-tie-t02", "002-pass1-k03", "003-pass1-k18"]}


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
    files = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "check_e213.py"), "--list"], capture_output=True, text=True).stdout.split()
    for rel in files + [REL_E + "/harness-e213.json"]:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e213.py")
    for rel, words in ((READER, ""), ("build/e213rgm-standin/rgm136/sparsity_host", " host --as rgm136"),
                       ("build/e213rgm-standin/rgm211/sparsity_host", " host --as rgm211")):
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
    r = subprocess.run(["bash", os.path.join(tree, REL_E, "build_e213.sh")], cwd=tree, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def standin_record(tree, arm, day, builder=True, et_ok=True):
    ks = {}
    for k in ("rgm136", "rgm211"):
        host = os.path.join(tree, f"build/e213rgm/{k}/host/sparsity_host")
        os.makedirs(os.path.dirname(host), exist_ok=True)
        shutil.copy2(os.path.join(tree, f"build/e213rgm-standin/{k}/sparsity_host"), host)
        elf = os.path.join(tree, f"build/e213rgm/{k}/kernel/sparsity.elf")
        ks[k] = {"kernel_sha256": sha256(elf), "host_sha256": sha256(host), "kernel_gate": "KERNEL OK: (the real build's gate, RA0)"}
    rec = {"box": BOX[arm], "arm": arm, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernels": ks, "host_checks": ["stand-in"],
           "what": "the real-path desk test's stand-in record (stand-in hosts beside the two real kernel ELFs)"}
    if builder:
        rec["builder"] = "build_e213.sh"
        rec["et_devices"] = (("the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES" if et_ok else "no: a host has no ET_DEVICES")
                             if arm == "B" else "not a gate on aifoundry3 (one card)")
    with open(os.path.join(tree, "build/e213rgm/BUILD-e213.json"), "w") as f:
        json.dump(rec, f, indent=1)


REGISTERED_PIN = {}


def session(S, arm, tree, name, env=None, pin_ok=True, seq="short", touch_after=None, on_line=None):
    import run_e213 as R
    C, N1 = R.C, R.N1
    out = os.path.join(S, f"{arm}-{name}")
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E213_FAKE_")]:
        del os.environ[k]
    os.environ.update({"E213_FAKE_ARM": arm, "E213_FAKE_DEVDIR": N1.DEV_DIR, "E213_FAKE_LOCK": C.ARMS[arm]["lock"],
                       "E213_FAKE_SCHED": os.path.join(out, "sched.jsonl"), "E213_FAKE_SCALE": "0.05", "E213_FAKE_TAU_S": "0.5"})
    os.environ.update(env or {})
    open(os.environ["E213_FAKE_SCHED"], "a").close()
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


def comment_variant(src, dst):
    """An ELF whose loadable identity is the source's and whose whole bytes are not: one byte of its .comment section (never loaded) changed."""
    b = bytearray(open(src, "rb").read())
    k = b.find(b"GCC: (")
    if k < 0:
        return False
    b[k + 5] = ord("X") if b[k + 5] != ord("X") else ord("Y")
    open(dst, "wb").write(bytes(b))
    return True


def setup(t, S, arm):
    tree, b, dev, lock = make_tree(S, arm)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e213 as R
    C, N1 = R.C, R.N1
    host = socket.gethostname()
    print(f"realpath_e213 arm {arm}: hostname {host!r} (the namespace's), tree {os.path.relpath(tree, S)}, the runner, its common module and the "
          f"gate the tree's: {R.__file__ == os.path.join(tree, REL_E, 'run_e213.py') and C.__file__ == os.path.join(tree, REL_E, 'e213_common.py') and R.IG.__file__ == os.path.join(tree, REL_E, 'ident_e213.py')}", flush=True)
    if C.REPO != tree:
        t.case(f"R{arm}-tree", False, f"the runner reads {C.REPO}, not the stand-in tree")
        return None
    if host != BOX[arm]:
        t.case(f"R{arm}-host", False, f"the namespace's hostname is {host!r}, not {BOX[arm]!r}: run under desk/realpath_e213.sh")
        return None
    REGISTERED_PIN[arm] = C.ARMS[arm]["ettelem_sha256"]
    C.ARMS[arm]["ettelem_sha256"] = sha256(os.path.join(tree, READER))
    C.ARMS[arm]["lock"] = lock
    N1.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    return tree, b, dev, lock, R, C, N1


def arm_a(t, S):
    st = setup(t, S, "A")
    if not st:
        return
    tree, b, dev, lock, R, C, N1 = st
    arm = "A"
    day = R.pacific_day()
    rc, txt = real_build(tree)
    rec = json.load(open(os.path.join(tree, "build/e213rgm/BUILD-e213.json"))) if os.path.exists(os.path.join(tree, "build/e213rgm/BUILD-e213.json")) else {}
    ks = rec.get("kernels") or {}
    hc = rec.get("host_checks") or []
    t.case("RA0", rc == 0 and "RGM-BUILT rc=0" in txt and rec.get("builder") == "build_e213.sh" and rec.get("arm") == "A"
           and (ks.get("rgm136") or {}).get("kernel_sha256", "").startswith("aace138c") and (ks.get("rgm211") or {}).get("kernel_sha256", "").startswith("00402801")
           and all((ks.get(k) or {}).get("kernel_gate", "").startswith(f"KERNEL OK: {k}: ") for k in ("rgm136", "rgm211"))
           and len(hc) == 12 and all(x.endswith(":ok") for x in hc) and "not a gate on aifoundry3" in rec.get("et_devices", "") and rec.get("box") == "aifoundry3",
           f"rc {rc}; {[ln[:120] for ln in txt.splitlines() if ln.startswith(('KERNEL', 'ETDEVICES', 'RGM-'))]}; host checks {len(hc)} ({sum(1 for x in hc if x.endswith(':ok'))} ok)")
    if rc != 0:
        print(txt[-3000:])
        return
    real_elf = {k: os.path.join(tree, f"build/e213rgm/{k}/kernel/sparsity.elf") for k in ("rgm136", "rgm211")}
    keep_elf = {k: open(p, "rb").read() for k, p in real_elf.items()}
    for k in ("rgm136", "rgm211"):          # the real ELFs, kept for arm B's tree
        shutil.copy2(real_elf[k], os.path.join(S, f"real-{k}.elf"))
    standin_record(tree, arm, day)
    # RA1: the whole real path
    rc, log, d = session(S, arm, tree, "RA1")
    idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
    boxtxt = "".join(open(os.path.join(d, f)).read() for f in ("kernel-rgm136.txt", "kernel-rgm211.txt", "kernel-rgm136.err", "kernel-rgm211.err",
                                                                "harness.txt", "harness.err", "preflight.txt", "preflight.err") if os.path.exists(os.path.join(d, f)))
    ls = log.splitlines()
    i_sm = max([i for i, x in enumerate(ls) if "smoke s04: the identity gate GATE OK; rc" in x] or [-1])
    i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
    sm = [json.load(open(os.path.join(d, "smoke", p, "smoke.json"))) for p in C.ARMS[arm]["smoke"] if os.path.exists(os.path.join(d, "smoke", p, "smoke.json"))]
    pr = [(rjson(d, k).get("procs") or [{}])[0] for k in SHORT[arm]]
    gates = [x.get("gate", "") for x in sm] + [p.get("gate", "") for p in pr]
    real_gate = all(g.startswith("GATE OK: ") and "the whole ELF" in g and "(dry" not in g for g in gates)
    q = qj(d)
    t.case("RA1", rc == 0 and "DRY" not in log and "the box and the builds" in log and boxtxt.count("KERNEL OK") == 2 and "HARNESS OK" in boxtxt
           and "dmcmd_audit: GO" in boxtxt and "smoke gate passed" in log and 0 <= i_sm < i_sp < 10 ** 6 and ran(d) == 3 and "config end: {" in log
           and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and idn.get("config_start", {}).get("targets") == ["/dev/et0_mgmt"]
           and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et0_mgmt"] and len(sm) == 4 and all(x["good"] for x in sm) and real_gate
           and [x.get("walk_ok") for x in sm] == [True] * 4 and [x.get("walk", {}).get("want") for x in sm] == [None, "nm", "mn", "mn"]
           and [x.get("family") for x in sm] == ["rgm136 gemmL", "rgm211 gemmLn", "rgm136 gemmLnc", "rgm211 gemmL"]
           and all(x.get("cycles_in_band") for x in sm)
           and all(v["host"]["stderr_targets"] == ["/dev/et0_ops"] and v["host"]["nodes_held"] == ["/dev/et0_ops"] for v in idn.get("smoke", {}).values())
           and runs_of(d) == SHORT[arm],
           f"rc {rc}; the box check {'passed' if 'the box and the builds' in log else 'NOT passed'} (both kernel gates, harness, preflight run); identity "
           f"{idn.get('config_start', {}).get('targets')} {idn.get('config_start', {}).get('ids')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}, "
           f"the sampler {idn.get('sampler_nodes', {}).get('nodes')}; the smoke's counter means {[x.get('counted_cycles_per_op') for x in sm]} (R0's band), "
           f"then the stop-path test (lines {i_sm} < {i_sp}); the real gate on every process {real_gate} ({gates[1][:110]!r}); runs {runs_of(d)}; real path "
           f"(no DRY line) {'DRY' not in log}")
    # RA1K: the four families on the real path
    rc, log, d = session(S, arm, tree, "RA1K", seq="kernels")
    want_runs = [R.C.run_key(r) for r in R.C.sequence(arm) if r["block"] == "pass1" and R.C.rgm211_host(r["id"])]
    good = []
    for k in want_runs:
        rj = rjson(d, k)
        p = (rj.get("procs") or [{}])[0]
        fam = R.C.family(rj.get("id", "a000")) if rj else None
        want_walk = R.C.LOOPS[fam]["walk"] if fam else None
        ok = (p.get("gate", "").startswith("GATE OK: ") and "(dry" not in p.get("gate", "") and p.get("walk_ok") is True
              and (p.get("walk") or {}).get("want") == want_walk and p.get("rc") == 0 and p.get("check") in ("approx", "exact")
              and p.get("family") == fam and p.get("kernel") == R.C.fam_elf(fam) and p.get("host") == "rgm211")
        good.append((k, fam, ok))
    t.case("RA1K", rc == 0 and runs_of(d) == want_runs and len(want_runs) == 13 and all(x[2] for x in good)
           and sum(1 for x in good if x[1] == "rgm211 gemmL") == 4,
           f"rc {rc}; {len(want_runs)} runs of rgm211's host in pass 1, each gated on its real ELF by its loop with its walk: "
           f"{[(x[0][10:], x[1].split()[1] + '@' + x[1].split()[0][3:], x[2]) for x in good]}")
    # RA2: the lock held
    holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc, log, d = session(S, arm, tree, "RA2")
    holder.terminate()          # the stand-in holder (a sleep under flock, no device), by SIGTERM
    holder.wait()
    t.case("RA2", rc == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
    # RA3: a host hung past its TERM under the real timeout 10
    t0 = time.time()
    rc, log, d = session(S, arm, tree, "RA3", {"E213_FAKE_HOST": "hang_term", "E213_FAKE_HOST_POINTS": "a039", "E213_FAKE_HANG_S": "16"})
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
        standin_record(tree, arm, day)
        rc, log, d = session(S, arm, tree, "RA6")
        kt = open(os.path.join(d, "kernel-rgm211.txt")).read() if os.path.exists(os.path.join(d, "kernel-rgm211.txt")) else ""
        open(elf, "wb").write(keep)
        standin_record(tree, arm, day)
        t.case("RA6", rc == 16 and "the kernel-rgm211 check did not read KERNEL OK" in log and "KERNEL FAILED: rgm211: rgm211 gemmLn needs rgm211's .text" in kt
               and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{kt.strip()[:140]}'")
    else:
        t.case("RA6", False, "the .text bytes were not found in the ELF to change one")
    # RA7: ET_DEVICES
    os.environ["ET_DEVICES"] = "1"
    try:
        ns = argparse.Namespace(what="session", arm=arm, t0=int(time.time()), out=os.path.join(S, "A-RA7-env"), deadline_epoch=0, dry=False,
                                sequence="short", rest_s=0.4, smoke_rest_s=1.5, tail_s=0.3, gate_wait_s=3.0, rule_s=C.ARMS[arm]["rule_s"], cap_s=C.ARMS[arm]["cap_s"])
        env_clean = "ET_DEVICES" not in R.Session(ns).env
    finally:
        del os.environ["ET_DEVICES"]
    C.ARMS[arm]["et_devices"] = "1"
    try:
        rc, log, d = session(S, arm, tree, "RA7a")
    finally:
        C.ARMS[arm]["et_devices"] = None
    g = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e213.sh"), "config"], cwd=tree, capture_output=True,
                       text=True, env=dict(os.environ, ET_DEVICES="1"))
    g2 = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e213.sh"), "sample", "--reset-ms", "1"], cwd=tree,
                        capture_output=True, text=True)
    t.case("RA7", env_clean and rc == 16 and "carries ET_DEVICES" in log and not os.path.exists(os.path.join(d, "config-start.json")) and g.returncode == 97
           and "ET_DEVICES is '1' on aifoundry3" in g.stderr and "PCIe target" not in g.stderr and g2.returncode == 97 and "PCIe target" not in g2.stderr,
           f"(a) inherited ET_DEVICES dropped from the device environment: {env_clean}; (b) a table setting it: the runner rc {rc}: "
           f"'{first_line(log, 'ET_DEVICES')}'; (c) the real guard rc {g.returncode}: '{g.stderr.strip()[:110]}'; sample --reset-ms rc {g2.returncode}")
    # RA8: another login on card 0 at the start
    rc, log, d = session(S, arm, tree, "RA8", {"E213_FAKE_ETWHO": "other"})
    t.case("RA8", rc == 16 and "holder line(s) of another login" in log and not os.path.exists(os.path.join(d, "config-start.json")),
           f"rc {rc}; '{first_line(log, 'refused')}'")
    # RA9: the other card, three ways
    rc1, log1, d1 = session(S, arm, tree, "RA9a", {"E213_FAKE_CONFIG": "card1"})
    rc2, log2, d2 = session(S, arm, tree, "RA9b", {"E213_FAKE_SAMPLER": "card1"})
    rc3, log3, d3 = session(S, arm, tree, "RA9c", {"E213_FAKE_HOST": "card1"})
    err = open(os.path.join(d3, "smoke", "s01", "proc.err")).read() if os.path.exists(os.path.join(d3, "smoke", "s01", "proc.err")) else ""
    t.case("RA9", rc1 == 16 and "the card's identity" in log1 and "/dev/et1_mgmt" in log1 and "sampler started" not in log1 and not has_proc(d1)
           and rc2 == 16 and "the identity read" in log2 and not has_proc(d2)
           and rc3 == 16 and os.path.exists(os.path.join(d3, "STOP")) and "stopping:" in err and "smoke gate failed" in log3
           and not os.path.isdir(os.path.join(d3, "smoke", "s02")),
           f"(a) config naming card 1: rc {rc1}; (b) the sampler on card 1: rc {rc2}; (c) the host on card 1: rc {rc3}, stopped by the file {'stopping:' in err}")
    # RA10: card 1's runtime line in the first run (identity stop); card 0's runtime line inside records (dropped)
    rc, log, d = session(S, arm, tree, "RA10a", {"E213_FAKE_HOST": "runtime1", "E213_FAKE_HOST_POINTS": "t01"})
    q = qj(d)
    rcb, logb, db = session(S, arm, tree, "RA10b", {"E213_FAKE_HOST": "runtime"})
    smb = json.load(open(os.path.join(db, "smoke", "s02", "smoke.json"))) if os.path.exists(os.path.join(db, "smoke", "s02", "smoke.json")) else {}
    prb = (rjson(db, SHORT[arm][1]).get("procs") or [{}])[0]
    t.case("RA10", rc == 0 and ran(d) == 1 and "identity: the runtime named card(s) ['1']" in str(q.get("stop")) and "nothing further started" in log
           and rcb == 0 and ran(db) == 3 and smb.get("records", {}).get("runtime_lines") == 2 and smb.get("records", {}).get("unparsed") == 0
           and prb.get("records", {}).get("runtime_lines") == 2 and prb.get("records", {}).get("unparsed") == 0 and prb.get("check") in ("approx", "exact"),
           f"card 1's line: rc {rc}, the stop {str(q.get('stop'))[:90]!r}; card 0's line: rc {rcb}, the smoke's s02 records {smb.get('records')}, "
           f"run 002's {prb.get('records')}")
    # RA11: the sampler dies in a run
    rc, log, d = session(S, arm, tree, "RA11", {"E213_FAKE_SAMPLER": "dies:36"})      # past the smoke's four processes (about 28 launches; s04 by A1)
    t.case("RA11", rc == 0 and "restarting it" in log and log.count("sampler started") >= 2 and ran(d) >= 2,
           f"rc {rc}; sampler starts {log.count('sampler started')}; runs {ran(d)}")
    # RA12: a build record without the builder
    standin_record(tree, arm, day, builder=False)
    rc, log, d = session(S, arm, tree, "RA12")
    standin_record(tree, arm, day)
    t.case("RA12", rc == 16 and "not today's BUILT by build_e213.sh" in log and "refused, no device opened" in log, f"rc {rc}")
    # RA13: the operator's STOP file touched in run 002
    rc, log, d = session(S, arm, tree, "RA13", touch_after=("run 002-", 0.4))
    q = qj(d)
    qq = q.get("queue", [])
    t.case("RA13", rc == 0 and len(qq) == 3 and not qq[-1].get("ran") and "the operator's STOP file" in str(q.get("stop"))
           and os.path.exists(os.path.join(d, "STOP")), f"rc {rc}; runs {[(x.get('run'), x.get('ran')) for x in qq]}; the stop {str(q.get('stop'))[:80]!r}")
    # RA14: THE NEW FAMILY'S IDENTITY GATE on real ELFs: rgm136's ELF copied over rgm211's once the smoke has passed
    def swap():
        open(real_elf["rgm211"], "wb").write(keep_elf["rgm136"])
    try:
        rc, log, d = session(S, arm, tree, "RA14", seq="gemmL211", on_line=("smoke gate passed", 0.0, swap))
    finally:
        open(real_elf["rgm211"], "wb").write(keep_elf["rgm211"])
    k85 = [R.C.run_key(r) for r in R.C.sequence(arm) if r["block"] == "pass1" and R.C.family(r["id"]) == "rgm211 gemmL"]
    r5 = rjson(d, k85[0]) if k85 else {}
    inproc = {}
    for fam in ("rgm136 gemmL", "rgm136 gemmLnc", "rgm211 gemmLn", "rgm211 gemmL"):
        for k in ("rgm136", "rgm211"):
            good_, words = R.IG.gate(fam, real_elf[k])
            inproc[f"{fam} on {k}"] = good_
    want_ip = {f"{fam} on {k}": (R.IG.FAMILY_KERNEL[fam] == k) for fam in R.IG.FAMILY_KERNEL for k in ("rgm136", "rgm211")}
    # the walk alone cannot tell: rgm211's host stand-in given rgm136's ELF for a gemmL arm reads walk mn and walk_ok true
    fake = os.path.join(tree, REL_E, "fake_card_e213.py")
    argv = R.C.host_argv(tree, "a085", 2, 3.5, os.path.join(S, "nostop"))
    argv[argv.index("--kernel") + 1] = real_elf["rgm136"]
    wenv = {k: v for k, v in os.environ.items() if not k.startswith("E213_FAKE_")}
    wenv.update({"E213_FAKE_ARM": "A", "E213_FAKE_SCALE": "0.05", "E213_FAKE_POINT": "a085"})
    wo = subprocess.run(["/usr/bin/python3", "-B", fake, "host", "--as", "rgm211"] + argv[1:], capture_output=True, text=True, env=wenv)
    fma, chk, _ = R.C.host_records(wo.stdout, argv)
    wok, wwords, _ = R.C.walk_check("rgm211 gemmL", fma, chk)
    s4r = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
    s4_ok = s4r.get("good") is True and str(s4r.get("gate", "")).startswith("GATE OK: ") and "(dry" not in str(s4r.get("gate", ""))
    t.case("RA14", rc == 0 and ran(d) == 0 and "smoke gate passed" in log and f"STOP before run {k85[0]}'s process: the identity gate failed" in log
           and "rgm136's" in str(r5.get("gate_words")) and not os.path.exists(os.path.join(d, "runs", k85[0], "proc-00.out"))
           and "nothing further started" in log and inproc == want_ip and wok and wo.returncode == 0 and len(k85) == 4 and s4_ok,
           f"rc {rc}; runs {ran(d)}; the family's smoke s04 (Amendment A1) good on its real gate before the swap {s4_ok}; the new family's runs "
           f"{[x[10:] for x in k85]}; {k85[0]}'s gate {str(r5.get('gate_words'))[:150]!r}; the gate in process on "
           f"the real ELFs {sum(1 for v in inproc.values() if v)} OK of 8 as wanted {inproc == want_ip}; the walk alone with rgm136's ELF for a085: "
           f"walk_ok {wok} ({wwords[:60]}), host rc {wo.returncode}: only the gate refuses it")
    # RA15: THE WALK CHECK on the real path, the new family
    rc, log, d = session(S, arm, tree, "RA15", {"E213_FAKE_HOST": "walkbad", "E213_FAKE_HOST_POINTS": "a085"}, seq="gemmL211")
    t.case("RA15", rc == 0 and ran(d) == 1 and f"STOP: the kernel stops in run {k85[0]} (rgm211 gemmL): " in log and "the walk check failed" in log
           and "nothing further started" in log, f"rc {rc}; runs {ran(d)}; '{[x[24:200] for x in log.splitlines() if 'STOP:' in x][:1]}'")
    # RA16: Amendment A1, the family smoke's own stop path on the real path
    rc, log, d = session(S, arm, tree, "RA16a", {"E213_FAKE_HOST": "walkbad", "E213_FAKE_HOST_POINTS": "s04"}, seq="gemmL211")
    q = qj(d)
    s4 = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
    qa = q.get("queue", [])
    ok_a = (rc == 0 and "smoke s04: FAILED for its family alone (Amendment A1: its own stop path)" in log and "stop-path test passed" in log
            and "smoke gate failed" not in log and str(s4.get("gate", "")).startswith("GATE OK: ") and "(dry" not in str(s4.get("gate", ""))
            and s4.get("walk_ok") is False and s4.get("a1_family_dropped") == "rgm211 gemmL" and ran(d) == 0 and len(qa) == 4
            and all(x.get("ran") is False and "Amendment A1" in x.get("why", "") for x in qa)
            and not any(os.path.isdir(os.path.join(d, "runs", x.get("run", "-"))) for x in qa) and "rgm211 gemmL" in (q.get("families_dropped") or {}))
    rc2, log2, d2 = session(S, arm, tree, "RA16b", {"E213_FAKE_HOST": "k1", "E213_FAKE_HOST_POINTS": "s04"}, seq="gemmL211")
    s4b = json.load(open(os.path.join(d2, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d2, "smoke", "s04", "smoke.json")) else {}
    ok_b = (rc2 == 16 and "smoke gate failed: a stop during the smoke's s04: K1: a launch of the smoke's s04 did not finish" in log2 and ran(d2) == 0
            and s4b.get("a1_family_dropped") is None and "K1" in str(s4b.get("a1_session_level")) and not qj(d2).get("families_dropped"))
    t.case("RA16", ok_a and ok_b,
           f"(a) rc {rc}; s04's real gate {str(s4.get('gate'))[:60]!r}, walk_ok {s4.get('walk_ok')}, dropped {s4.get('a1_family_dropped')!r}; the "
           f"family's runs {[(x.get('run', '')[10:], x.get('ran')) for x in qa]}; (b) rc {rc2}; '{first_line(log2, 'smoke gate failed')}'; s04's "
           f"session-level reading {s4b.get('a1_session_level')!r}")


def arm_b(t, S):
    st = setup(t, S, "B")
    if not st:
        return
    tree, b, dev, lock, R, C, N1 = st
    arm = "B"
    day = R.pacific_day()
    rc, txt = real_build(tree)
    rec = json.load(open(os.path.join(tree, "build/e213rgm/BUILD-e213.json"))) if os.path.exists(os.path.join(tree, "build/e213rgm/BUILD-e213.json")) else {}
    rc2, log2, d2 = session(S, arm, tree, "RB0")
    t.case("RB0", rc == 1 and "RGM-BUILD-FAILED: ET_DEVICES: a host has no ET_DEVICES" in txt and rec.get("verdict") == "BUILD-FAILED"
           and rc2 == 16 and "refused, no device opened" in log2 and "KERNEL OK: rgm136: rgm136 gemmL: rgm136, .text" in txt and "the whole ELF" in txt,
           f"build rc {rc}; {[ln[:110] for ln in txt.splitlines() if ln.startswith(('ETDEVICES', 'RGM-', 'KERNEL'))]}; the runner then rc {rc2}")
    for k in ("rgm136", "rgm211"):          # the real ELFs from arm A's real build (this desk's toolchain, aifoundry1's form)
        dst = os.path.join(tree, f"build/e213rgm/{k}/kernel/sparsity.elf")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(S, f"real-{k}.elf"), dst)
    real_elf = {k: os.path.join(tree, f"build/e213rgm/{k}/kernel/sparsity.elf") for k in ("rgm136", "rgm211")}
    keep_elf = {k: open(p, "rb").read() for k, p in real_elf.items()}
    standin_record(tree, arm, day)
    rc, log, d = session(S, arm, tree, "RB1")
    idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
    boxtxt = "".join(open(os.path.join(d, f)).read() for f in ("kernel-rgm136.txt", "kernel-rgm211.txt") if os.path.exists(os.path.join(d, f)))
    sm = [json.load(open(os.path.join(d, "smoke", p, "smoke.json"))) for p in C.ARMS[arm]["smoke"] if os.path.exists(os.path.join(d, "smoke", p, "smoke.json"))]
    pr = [(rjson(d, k).get("procs") or [{}])[0] for k in SHORT[arm]]
    gates = [x.get("gate", "") for x in sm] + [p.get("gate", "") for p in pr]
    t.case("RB1", rc == 0 and "DRY" not in log and "smoke gate passed" in log and ran(d) == 3 and runs_of(d) == SHORT[arm]
           and idn.get("config_start", {}).get("targets") == ["/dev/et1_mgmt"] and idn.get("config_start", {}).get("minion_mv") == 499
           and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et1_mgmt"] and "ET_DEVICES=1 on every device process" in log
           and all(v["host"]["stderr_targets"] == ["/dev/et1_ops"] and v["host"]["nodes_held"] == ["/dev/et1_ops"] for v in idn.get("smoke", {}).values())
           and len(sm) == 4 and all(x["good"] for x in sm) and [x.get("walk", {}).get("want") for x in sm] == [None, None, None, "mn"]
           and all(g.startswith("GATE OK: ") and "the whole ELF" in g for g in gates) and "rgm136, .text" in boxtxt and "the whole ELF" in boxtxt,
           f"rc {rc}; identity {idn.get('config_start', {}).get('targets')} {idn.get('config_start', {}).get('minion_mv')} mV; the sampler "
           f"{idn.get('sampler_nodes', {}).get('nodes')}; the smoke {[(x.get('family'), x.get('walk_words', '')[:12]) for x in sm]}; every process gated at the "
           f"whole ELF {all('the whole ELF' in g for g in gates)}; runs {runs_of(d)}")
    # RB1K: arm B's gemmLnc runs on the real path
    rc, log, d = session(S, arm, tree, "RB1K", seq="kernels")
    want_runs = [R.C.run_key(r) for r in R.C.sequence(arm) if r["block"] == "pass1" and R.C.rgm211_host(r["id"])]
    pk = [(rjson(d, k).get("procs") or [{}])[0] for k in want_runs]
    t.case("RB1K", rc == 0 and runs_of(d) == want_runs and len(want_runs) == 4
           and all(p.get("host") == "rgm211" and p.get("kernel") == "rgm136" and p.get("walk_ok") is True and (p.get("walk") or {}).get("want") == "mn"
                   and p.get("gate", "").startswith("GATE OK: rgm136 gemmLnc: rgm136, ") and "the whole ELF" in p.get("gate", "") for p in pk),
           f"rc {rc}; runs {[k[10:] for k in want_runs]}; each on rgm211's host with rgm136's real ELF at its whole ELF, the walk mn: "
           f"{[(p.get('host'), p.get('kernel'), p.get('walk_ok')) for p in pk]}")
    rc, log, d = session(S, arm, tree, "RB2", {"E213_FAKE_CONFIG": "card1"})
    t.case("RB2", rc == 16 and "the card's identity" in log and "/dev/et0_mgmt" in log and "sampler started" not in log and not has_proc(d), f"rc {rc}")
    rc, log, d = session(S, arm, tree, "RB3", {"E213_FAKE_SAMPLER": "card1"})
    t.case("RB3", rc == 16 and "the identity read" in log and not has_proc(d), f"rc {rc}; '{first_line(log, 'identity read')}'")
    rc, log, d = session(S, arm, tree, "RB4", {"E213_FAKE_HOST": "card1"})
    err = open(os.path.join(d, "smoke", "s11", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "s11", "proc.err")) else ""
    t.case("RB4", rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log
           and not os.path.isdir(os.path.join(d, "smoke", "s12")), f"rc {rc}; the host stopped by the file {'stopping:' in err}")
    C.ARMS[arm]["et_devices"] = None
    try:
        rc, log, d = session(S, arm, tree, "RB5a")
    finally:
        C.ARMS[arm]["et_devices"] = "1"
    e = {k: v for k, v in os.environ.items() if k != "ET_DEVICES"}
    g = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e213.sh"), "config"], cwd=tree, capture_output=True, text=True, env=e)
    t.case("RB5", rc == 16 and "lacks ET_DEVICES=1" in log and not os.path.exists(os.path.join(d, "config-start.json")) and g.returncode == 97
           and "ET_DEVICES is 'unset' on aifoundry1, not 1" in g.stderr and "PCIe target" not in g.stderr,
           f"(a) the runner rc {rc}: '{first_line(log, 'ET_DEVICES')}'; (b) the real guard rc {g.returncode}: '{g.stderr.strip()[:120]}'")
    rc, log, d = session(S, arm, tree, "RB6a", {"E213_FAKE_ETWHO": "other1"})
    holder = subprocess.Popen(["/usr/bin/python3", "-c", f"import time; f = open('{os.path.join(dev, 'et0_ops')}', 'a'); time.sleep(30)"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc2, log2, d2 = session(S, arm, tree, "RB6b")
    holder.terminate()          # the stand-in (a python sleep holding a stand-in node file, no device), by SIGTERM
    holder.wait()
    t.case("RB6", rc == 16 and "another login on card 0 (the kit's start rule" in log and rc2 == 16 and "of ours on card 0" in log2
           and not os.path.exists(os.path.join(d, "config-start.json")) and not os.path.exists(os.path.join(d2, "config-start.json")),
           f"(a) another login on card 0: rc {rc}; (b) a process of ours holding card 0's node: rc {rc2}: '{first_line(log2, 'refused')}'")
    rc, log, d = session(S, arm, tree, "RB7", {"E213_FAKE_SAMPLER": "dies:36"})      # past the smoke's four processes (about 28 launches)
    t.case("RB7", rc == 0 and "restarting it" in log and log.count("sampler started") >= 2 and ran(d) >= 2,
           f"rc {rc}; sampler starts {log.count('sampler started')}; runs {ran(d)}")
    rc, log, d = session(S, arm, tree, "RB8a", {"E213_FAKE_HOST": "runtime"})
    smr = json.load(open(os.path.join(d, "smoke", "s11", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s11", "smoke.json")) else {}
    pr = (rjson(d, SHORT[arm][0]).get("procs") or [{}])[0]
    rc2, log2, d2 = session(S, arm, tree, "RB8b", {"E213_FAKE_HOST": "runtime1", "E213_FAKE_HOST_POINTS": "t02"})
    q2 = qj(d2)
    t.case("RB8", rc == 0 and smr.get("records", {}).get("runtime_lines") == 2 and smr.get("records", {}).get("unparsed") == 0 and ran(d) == 3
           and pr.get("records", {}).get("runtime_lines") == 2 and pr.get("records", {}).get("unparsed") == 0 and pr.get("check") in ("approx", "exact")
           and rc2 == 0 and ran(d2) == 1 and "identity: the runtime named card(s) ['0']" in str(q2.get("stop")),
           f"card 1's own line: rc {rc}, the smoke's s11 records {smr.get('records')}, the tie's {pr.get('records')}; card 0's line on the tie's host: "
           f"rc {rc2}, the stop {str(q2.get('stop'))[:80]!r}")
    # RB9: THE WHOLE ELF ON ARM B
    var = os.path.join(S, "rgm136-comment-variant.elf")
    made = comment_variant(real_elf["rgm136"], var)
    ga, wa = R.IG.gate("rgm136 gemmL", var)
    gb, wb = R.IG.gate("rgm136 gemmL", var, whole=True)
    if made:
        open(real_elf["rgm136"], "wb").write(open(var, "rb").read())
        standin_record(tree, arm, day)
        rc, log, d = session(S, arm, tree, "RB9")
        kt = open(os.path.join(d, "kernel-rgm136.txt")).read() if os.path.exists(os.path.join(d, "kernel-rgm136.txt")) else ""
        open(real_elf["rgm136"], "wb").write(keep_elf["rgm136"])
        standin_record(tree, arm, day)
    t.case("RB9", made and ga and not gb and "loadable identity" in wa and "requires the whole ELF" in wb and rc == 16
           and "the kernel-rgm136 check did not read KERNEL OK" in log and "requires the whole ELF" in kt and not os.path.exists(os.path.join(d, "config-start.json")),
           f"an identity-equal ELF with a changed .comment: arm A's gate {ga}, arm B's (whole) {gb}; the box check rc {rc}: '{kt.strip()[:150]}'")
    # RB10: a host hung past its TERM
    t0 = time.time()
    rc, log, d = session(S, arm, tree, "RB10", {"E213_FAKE_HOST": "hang_term", "E213_FAKE_HOST_POINTS": "k03", "E213_FAKE_HANG_S": "16"})
    mk = wait_marker(os.path.join(d, "sched.jsonl.hang-ended"), 40)
    p0 = (rjson(d, SHORT[arm][1]).get("procs") or [{}])[0]
    t.case("RB10", rc == 8 and f" HUNG: a device process (the host of {SHORT[arm][1]}" in log and "config end: not read" in log and p0.get("hung") is True
           and "ended by itself after 16" in mk, f"rc {rc}; the hung stand-in: '{mk[:90]}' ({time.time() - t0:.0f} s); nothing killed it")
    # RB11: THE IDENTITY GATE PER PROCESS on arm B: rgm211's ELF copied over rgm136's once the smoke has passed
    def swap():
        open(real_elf["rgm136"], "wb").write(keep_elf["rgm211"])
    try:
        rc, log, d = session(S, arm, tree, "RB11", on_line=("smoke gate passed", 0.0, swap))
    finally:
        open(real_elf["rgm136"], "wb").write(keep_elf["rgm136"])
    r1 = rjson(d, SHORT[arm][0])
    t.case("RB11", rc == 0 and ran(d) == 0 and f"STOP before run {SHORT[arm][0]}'s process: the identity gate failed" in log
           and "rgm211's" in str(r1.get("gate_words")) and not os.path.exists(os.path.join(d, "runs", SHORT[arm][0], "proc-00.out")),
           f"rc {rc}; runs {ran(d)}; the tie's gate {str(r1.get('gate_words'))[:150]!r}")


def main(argv):
    if len(argv) != 2 or argv[1] not in ("A", "B"):
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
    print(f"realpath_e213 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    (arm_a if argv[1] == "A" else arm_b)(t, S)
    print(f"REALPATH-E213 arm {argv[1]}: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
