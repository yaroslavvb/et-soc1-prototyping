#!/usr/bin/env python3
"""E206's REAL-PATH desk test (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum; the round's lesson: a branch the dry path skips is
exercised by a desk test of the real path; E190's kit note 1's desk/realpath_e190_v2.py form). run_e206.py's session WITHOUT --dry, on one
arm's stand-in box tree, as on the card day except for these stand-ins:
  - the hostname: the arm's box (aifoundry3 or aifoundry1), from a private UTS namespace (desk/realpath_e206.sh starts this driver under
    bubblewrap with --hostname, a private PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock);
  - the telemetry reader behind the REAL guard (ettelem_guard_e206.sh, with its hostname and ET_DEVICES rules): build/ettelem/ettelem is a
    script that runs fake_card_e206.py (config, sample); the runner's pin for it is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e206.py etwho, which reads who holds the stand-in nodes and the stand-in lock from
    /proc, as et-who's fuser does;
  - the host: build/e206rgm/host/sparsity_host is a script (the name the runner checks) that runs fake_card_e206.py host; the build record
    carries its sha256; the kernel ELF is the REAL one, built by the REAL build_e206.sh in arm A's stand-in tree (the kernel gate on this
    desk's toolchain);
  - the card's lock: a writable stand-in file (the runner's lock path set to it in this process), and the card's nodes a stand-in directory
    (e206_ident.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, arm B's ET_DEVICES=1, the build record and its day, the kernel through THE
KERNEL GATE (check_e206.py --kernel, the real objcopy), the host at its record, the reader at its pin, the tiles, check_e206.py --box and
preflight_e206.sh (dmcmd_audit_v2), both run), the lock (open, flock -n), the holders (et-who through `timeout 20` and the real `ps`), the
start config through the real guard under the real `timeout 10`, the identity gate, the sampler through the real guard, the identity read,
the smoke (p001, p046, p021) THEN the stop-path test, the runs (the first tie and two points of pass 1) with each host under the real
`timeout 10`, the closing config, the manifest. Timing: the desk's short reads and the doubles at a twentieth of their time (the session's
fields are set here; run_e206.py's main() refuses them without --dry).

    python3 -B tools/claims-v3/e206/desk/realpath_e206.py <scratch dir> A|B      (desk/realpath_e206.sh runs both, in their namespaces)

Cases, arm A (hostname aifoundry3): RA0 the REAL build in the stand-in tree (BUILT; THE KERNEL GATE reads KERNEL OK on the registered ELF;
ET_DEVICES not a gate on aifoundry3); RA1 the whole real path: rc 0 (the smoke, the stop-path test after it, three runs); RA2 the lock held
by another process: 16, no config read; RA3 A HOST HUNG PAST ITS TERM in the tie: the real `timeout 10` sends its TERM at 10 s, the host
ignores it, the runner writes HUNG at 14 s and exits 8 with no closing config read, and NOTHING KILLS the host: it ends by itself at 16 s
(its marker file); RA4 a device process of ours (a stand-in named sys_emu): the real ps read refuses it: 16, no config read; RA5 the reader
not at its pin: 16, no lock taken; RA6 a kernel whose .text differs (one byte of the built ELF's .text changed): the box check's kernel gate
refuses it: 16, no device opened.
Arm B (hostname aifoundry1): RB0 the REAL build on this desk's stock device layer: RGM-BUILD-FAILED "ET_DEVICES: the host has no ET_DEVICES",
and the runner then refuses the failed record: 16; RB1 the whole real path (ET_DEVICES=1 through the real guard; card 1's identity, 499 mV;
the sampler on /dev/et1_mgmt; the smoke's hosts on /dev/et1_ops): rc 0; RB2 the reader's config names card 0 (519 mV): 16 before the
sampler; RB3 the sampler holds card 0's node: 16 before the smoke; RB4 the host names and holds card 0: the watch trips in the smoke's first
process, the stop file, "stopping:", 16; RB5 A MISSING ET_DEVICES: (a) the runner's device environment without it: the box check refuses
before any device: 16; (b) the REAL guard run with ET_DEVICES unset under aifoundry1: refused (97) before the reader opens; RB6 A SECOND
CARD'S HOLDER: (a) another login on card 0 at the start: 16 (the kit's start rule); (b) a process of ours holding card 0's stand-in node: 16;
RB7 the sampler dies in a run: the run ends flagged, the sampler restarts through the real guard, rc 0; RB8 aifoundry1's runtime line on the
host's stdout at its start AND inside its first record: dropped, every record read whole, rc 0; RB9 a build record without the builder: 16.
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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
REL_E = "tools/claims-v3/e206"
CARD = {"A": "0", "B": "1"}
BOX = {"A": "aifoundry3", "B": "aifoundry1"}
READER = "build/ettelem/ettelem"


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
    # the file list from the harness check run as its own process (importing it here would load the lab clone's e206_common first, and
    # the stand-in tree's runner would then read the clone's paths)
    files = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "check_e206.py"), "--list"], capture_output=True, text=True).stdout.split()
    for rel in files + [REL_E + "/harness-e206.json"]:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e206.py")
    for rel, words in ((READER, ""), ("build/e206rgm-standin/sparsity_host", " host")):
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
    r = subprocess.run(["bash", os.path.join(tree, REL_E, "build_e206.sh")], cwd=tree, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def standin_record(tree, arm, day, builder=True, et_ok=True):
    host = os.path.join(tree, "build/e206rgm/host/sparsity_host")
    os.makedirs(os.path.dirname(host), exist_ok=True)
    shutil.copy2(os.path.join(tree, "build/e206rgm-standin/sparsity_host"), host)
    elf = os.path.join(tree, "build/e206rgm/kernel/sparsity.elf")
    rec = {"box": BOX[arm], "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": sha256(elf),
           "host_sha256": sha256(host), "host_checks": ["stand-in"], "kernel_gate": "KERNEL OK: (the real build's gate, RA0)",
           "what": "the real-path desk test's stand-in record (a stand-in host beside the real kernel ELF)"}
    if builder:
        rec["builder"] = "build_e206.sh"
        rec["et_devices"] = ("the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES" if et_ok else "no: the host has no ET_DEVICES") \
            if arm == "B" else "not a gate on aifoundry3 (one card)"
    with open(os.path.join(tree, "build/e206rgm/BUILD-e206.json"), "w") as f:
        json.dump(rec, f, indent=1)


REGISTERED_PIN = {}


def session(S, arm, tree, name, env=None, pin_ok=True, seq="short"):
    import run_e206 as R
    C, N1 = R.C, R.N1
    out = os.path.join(S, f"{arm}-{name}")
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E206_FAKE_")]:
        del os.environ[k]
    os.environ.update({"E206_FAKE_ARM": arm, "E206_FAKE_DEVDIR": N1.DEV_DIR, "E206_FAKE_LOCK": C.ARMS[arm]["lock"],
                       "E206_FAKE_SCHED": os.path.join(out, "sched.jsonl"), "E206_FAKE_SCALE": "0.05", "E206_FAKE_TAU_S": "0.5"})
    os.environ.update(env or {})
    open(os.environ["E206_FAKE_SCHED"], "a").close()
    want = C.ARMS[arm]["ettelem_sha256"]
    if not pin_ok:
        C.ARMS[arm]["ettelem_sha256"] = REGISTERED_PIN[arm]
    a = argparse.Namespace(what="session", arm=arm, t0=int(time.time()), out=out, deadline_epoch=0, dry=False, sequence=seq,
                           rest_s=0.4, smoke_rest_s=1.5, tail_s=0.3, gate_wait_s=3.0, rule_s=C.CARD_RULE_S, cap_s=C.CAP_S)
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


def ran(d):
    q = json.load(open(os.path.join(d, "queue.json"))) if os.path.exists(os.path.join(d, "queue.json")) else {}
    return sum(1 for x in q.get("queue", []) if x.get("ran"))


def wait_marker(path, secs=40):
    t = time.time()
    while time.time() - t < secs:
        if os.path.exists(path):
            return open(path).read().strip()
        time.sleep(0.5)
    return ""


def arm_cases(t, S, arm):
    tree, b, dev, lock = make_tree(S, arm)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e206 as R
    C, N1 = R.C, R.N1
    host = socket.gethostname()
    print(f"realpath_e206 arm {arm}: hostname {host!r} (the namespace's), tree {os.path.relpath(tree, S)}, the runner and its common module the "
          f"tree's: {R.__file__ == os.path.join(tree, REL_E, 'run_e206.py') and C.__file__ == os.path.join(tree, REL_E, 'e206_common.py')}", flush=True)
    if C.REPO != tree:
        t.case(f"R{arm}-tree", False, f"the runner reads {C.REPO}, not the stand-in tree")
        return
    if host != BOX[arm]:
        t.case(f"R{arm}-host", False, f"the namespace's hostname is {host!r}, not {BOX[arm]!r}: run under desk/realpath_e206.sh")
        return
    REGISTERED_PIN[arm] = C.ARMS[arm]["ettelem_sha256"]
    C.ARMS[arm]["ettelem_sha256"] = sha256(os.path.join(tree, READER))
    C.ARMS[arm]["lock"] = lock
    N1.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    day = R.pacific_day()
    if arm == "A":
        rc, txt = real_build(tree)
        rec = json.load(open(os.path.join(tree, "build/e206rgm/BUILD-e206.json")))
        t.case("RA0", rc == 0 and "RGM-BUILT rc=0" in txt and rec.get("builder") == "build_e206.sh" and rec.get("kernel_sha256", "").startswith("aace138c")
               and rec.get("kernel_gate", "").startswith("KERNEL OK: ") and "not a gate on aifoundry3" in rec.get("et_devices", "") and rec.get("box") == "aifoundry3",
               f"rc {rc}; {[ln[:110] for ln in txt.splitlines() if ln.startswith(('KERNEL', 'ETDEVICES', 'RGM-', 'HOSTCHECK'))]}")
        standin_record(tree, arm, day)
        rc, log, d = session(S, arm, tree, "RA1")
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        boxtxt = "".join(open(os.path.join(d, f)).read() for f in ("kernel.txt", "kernel.err", "harness.txt", "harness.err", "preflight.txt",
                                                                    "preflight.err") if os.path.exists(os.path.join(d, f)))
        ls = log.splitlines()
        i_sm = max([i for i, x in enumerate(ls) if "smoke p021:" in x] or [-1])
        i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
        t.case("RA1", rc == 0 and "DRY" not in log and "the box and the build" in log and "KERNEL OK" in boxtxt and "HARNESS OK" in boxtxt
               and "dmcmd_audit: GO" in boxtxt and "smoke gate passed" in log and 0 <= i_sm < i_sp < 10 ** 6 and ran(d) == 3 and "config end: {" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and idn.get("config_start", {}).get("targets") == ["/dev/et0_mgmt"],
               f"rc {rc}; the box check {'passed' if 'the box and the build' in log else 'NOT passed'} (kernel gate, harness, preflight run); identity "
               f"{idn.get('config_start', {}).get('targets')} {idn.get('config_start', {}).get('ids')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}; "
               f"the smoke then the stop-path test (lines {i_sm} < {i_sp}); runs {ran(d)} of 3; real path (no DRY line) {'DRY' not in log}")
        holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)
        time.sleep(0.5)
        rc, log, d = session(S, arm, tree, "RA2")
        holder.terminate()
        holder.wait()
        t.case("RA2", rc == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
        t0 = time.time()
        rc, log, d = session(S, arm, tree, "RA3", {"E206_FAKE_HOST": "hang_term", "E206_FAKE_HOST_FROM_N": "21", "E206_FAKE_HOST_COUNT": "1",
                                                     "E206_FAKE_HANG_S": "16"})
        mk = wait_marker(os.path.join(d, "sched.jsonl.hang-ended"), 40)
        rj = os.path.join(d, "runs", "001-tie-p001", "run.json")
        rj = json.load(open(rj)) if os.path.exists(rj) else {}
        pr = (rj.get("procs") or [{}])[0]
        t.case("RA3", rc == 8 and " HUNG: a device process (the host of 001-tie-p001" in log and "config end: not read (a device process of ours is HUNG" in log
               and pr.get("hung") is True and pr.get("t1_ms", 0) - pr.get("t0_ms", 0) >= 13500 and ran(d) == 1 and "ended by itself after 16" in mk,
               f"rc {rc}; the tie's host left after {(pr.get('t1_ms', 0) - pr.get('t0_ms', 0)) / 1000:.1f} s (timeout's TERM at 10 s ignored); the hung stand-in: "
               f"'{mk[:90]}' ({time.time() - t0:.0f} s after the session began); nothing killed it")
        dp = subprocess.Popen([os.path.join(b, "sys_emu"), "30"], stdin=subprocess.DEVNULL)
        time.sleep(0.3)
        rc, log, d = session(S, arm, tree, "RA4")
        dp.terminate()
        dp.wait()
        t.case("RA4", rc == 16 and "other device process(es) of ours" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
        rc, log, d = session(S, arm, tree, "RA5", pin_ok=False)
        t.case("RA5", rc == 16 and "refused, no device opened" in log and READER in log and not os.path.exists(os.path.join(d, "config-start.json")),
               f"rc {rc}; '{[ln[24:170] for ln in log.splitlines() if 'no device opened' in ln][:1]}'")
        elf = os.path.join(tree, "build/e206rgm/kernel/sparsity.elf")
        keep = open(elf, "rb").read()
        oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
        tb = os.path.join(S, "text-A.bin")
        subprocess.run([oc, "-O", "binary", "-j", ".text", elf, tb], check=False)
        tx = open(tb, "rb").read() if os.path.exists(tb) else b""
        k = keep.find(tx[:64]) if tx else -1
        if k >= 0:
            bad = bytearray(keep)
            bad[k + 16] ^= 0x01
            open(elf, "wb").write(bytes(bad))
            standin_record(tree, arm, day)
            rc, log, d = session(S, arm, tree, "RA6")
            kt = open(os.path.join(d, "kernel.txt")).read() if os.path.exists(os.path.join(d, "kernel.txt")) else ""
            open(elf, "wb").write(keep)
            standin_record(tree, arm, day)
            t.case("RA6", rc == 16 and "the kernel check did not read KERNEL OK" in log and "KERNEL FAILED: .text sha256" in kt
                   and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{kt.strip()[:120]}'")
        else:
            t.case("RA6", False, "the .text bytes were not found in the ELF to change one")
        return
    # ---- arm B
    src_elf = os.path.join(S, "tree-A", "build/e206rgm/kernel/sparsity.elf")
    rc, txt = real_build(tree)
    rec = json.load(open(os.path.join(tree, "build/e206rgm/BUILD-e206.json"))) if os.path.exists(os.path.join(tree, "build/e206rgm/BUILD-e206.json")) else {}
    rc2, log2, d2 = session(S, arm, tree, "RB0")
    t.case("RB0", rc == 1 and "RGM-BUILD-FAILED: ET_DEVICES: the host has no ET_DEVICES" in txt and rec.get("verdict") == "BUILD-FAILED"
           and rc2 == 16 and "refused, no device opened" in log2,
           f"build rc {rc}; {[ln[:100] for ln in txt.splitlines() if ln.startswith(('ETDEVICES', 'RGM-', 'KERNEL'))]}; the runner then rc {rc2}")
    os.makedirs(os.path.join(tree, "build/e206rgm/kernel"), exist_ok=True)
    shutil.copy2(src_elf, os.path.join(tree, "build/e206rgm/kernel/sparsity.elf"))
    standin_record(tree, arm, day)
    rc, log, d = session(S, arm, tree, "RB1")
    idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
    t.case("RB1", rc == 0 and "DRY" not in log and "smoke gate passed" in log and ran(d) == 3 and idn.get("config_start", {}).get("targets") == ["/dev/et1_mgmt"]
           and idn.get("config_start", {}).get("minion_mv") == 499 and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et1_mgmt"]
           and all(v["host"]["stderr_targets"] == ["/dev/et1_ops"] and v["host"]["nodes_held"] == ["/dev/et1_ops"] for v in idn.get("smoke", {}).values())
           and len(idn.get("smoke", {})) == 3,
           f"rc {rc}; identity {idn.get('config_start')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}, the sampler "
           f"{idn.get('sampler_nodes', {}).get('nodes')}; smoke hosts {[(k, v['host']['stderr_targets'], v['host']['nodes_held']) for k, v in idn.get('smoke', {}).items()]}")
    rc, log, d = session(S, arm, tree, "RB2", {"E206_FAKE_CONFIG": "card0"})
    t.case("RB2", rc == 16 and "the card's identity" in log and "sampler started" not in log and not has_proc(d), f"rc {rc}")
    rc, log, d = session(S, arm, tree, "RB3", {"E206_FAKE_SAMPLER": "card0"})
    t.case("RB3", rc == 16 and "the identity read" in log and not has_proc(d), f"rc {rc}; '{[ln[24:200] for ln in log.splitlines() if 'identity read' in ln][:1]}'")
    rc, log, d = session(S, arm, tree, "RB4", {"E206_FAKE_HOST": "card0"})
    err = open(os.path.join(d, "smoke", "p001", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "p001", "proc.err")) else ""
    t.case("RB4", rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log
           and not os.path.isdir(os.path.join(d, "smoke", "p046")), f"rc {rc}; the host stopped by the file {'stopping:' in err}")
    C.ARMS["B"]["et_devices"] = None
    try:
        rc, log, d = session(S, arm, tree, "RB5a")
    finally:
        C.ARMS["B"]["et_devices"] = "1"
    e = {k: v for k, v in os.environ.items() if k != "ET_DEVICES"}
    g = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e206.sh"), "config"], cwd=tree, capture_output=True, text=True, env=e)
    t.case("RB5", rc == 16 and "lacks ET_DEVICES=1" in log and not os.path.exists(os.path.join(d, "config-start.json")) and g.returncode == 97
           and "ET_DEVICES is 'unset' on aifoundry1, not 1" in g.stderr and "PCIe target" not in g.stderr,
           f"(a) the runner rc {rc}: '{[ln[24:150] for ln in log.splitlines() if 'ET_DEVICES' in ln][:1]}'; (b) the real guard rc {g.returncode}: '{g.stderr.strip()[:120]}'")
    rc, log, d = session(S, arm, tree, "RB6a", {"E206_FAKE_ETWHO": "other0"})
    holder = subprocess.Popen(["/usr/bin/python3", "-c", f"import time; f = open('{os.path.join(dev, 'et0_ops')}', 'a'); time.sleep(30)"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc2, log2, d2 = session(S, arm, tree, "RB6b")
    holder.terminate()
    holder.wait()
    t.case("RB6", rc == 16 and "another login on card 0 (the kit's start rule" in log and rc2 == 16 and "of ours on card 0" in log2
           and not os.path.exists(os.path.join(d, "config-start.json")) and not os.path.exists(os.path.join(d2, "config-start.json")),
           f"(a) another login on card 0: rc {rc}; (b) a process of ours holding card 0's node: rc {rc2}: '{[ln[24:160] for ln in log2.splitlines() if 'refused' in ln][:1]}'")
    rc, log, d = session(S, arm, tree, "RB7", {"E206_FAKE_SAMPLER": "dies:24"})
    t.case("RB7", rc == 0 and "restarting it" in log and log.count("sampler started") >= 2 and ran(d) >= 2,
           f"rc {rc}; sampler starts {log.count('sampler started')}; runs {ran(d)}")
    rc, log, d = session(S, arm, tree, "RB8", {"E206_FAKE_HOST": "runtime"})
    sm = json.load(open(os.path.join(d, "smoke", "p001", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "p001", "smoke.json")) else {}
    rj = os.path.join(d, "runs", "001-tie-p001", "run.json")
    rj = json.load(open(rj)) if os.path.exists(rj) else {}
    pr = (rj.get("procs") or [{}])[0]
    t.case("RB8", rc == 0 and sm.get("records", {}).get("runtime_lines") == 2 and sm.get("records", {}).get("unparsed") == 0 and ran(d) == 3
           and pr.get("records", {}).get("runtime_lines") == 2 and pr.get("records", {}).get("unparsed") == 0 and pr.get("check") in ("approx", "exact"),
           f"rc {rc}; the smoke's p001 records {sm.get('records')}; the tie's {pr.get('records')}")
    standin_record(tree, arm, day, builder=False)
    rc, log, d = session(S, arm, tree, "RB9")
    t.case("RB9", rc == 16 and "not today's BUILT by build_e206.sh" in log and "refused, no device opened" in log, f"rc {rc}")
    standin_record(tree, arm, day)


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
    print(f"realpath_e206 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    arm_cases(t, S, argv[1])
    print(f"REALPATH-E206 arm {argv[1]}: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
