#!/usr/bin/env python3
"""E190's REAL-PATH desk test v2 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum; the verifier's
finding 2 and CONTEXT section 104's lesson: a branch the dry path skips is exercised by a desk test of the real path). run_e190_v2.py's
session WITHOUT --dry, on one arm's stand-in box tree, as on the card day except for these stand-ins:
  - the hostname: the arm's box, from a private UTS namespace (desk/realpath_e190_v2.sh starts this driver under bubblewrap with
    --hostname aifoundry2 or aifoundry1, a private PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock);
  - the telemetry reader behind the guard: build/ettelem-hpl/ettelem (arm A) or build/ettelem/ettelem (arm B) is a script that runs
    fake_card_e190_v2.py (config, sample); the runner's pin for it is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e190_v2.py etwho, which reads who holds the stand-in nodes and the stand-in lock from
    /proc, as et-who's fuser does;
  - the host: build/e190rgm/host/sparsity_host is a script (the name the runner checks) that runs fake_card_e190_v2.py host; the build
    record carries its sha256; the kernel ELF is the REAL one at the registration's pin, built by build_e190_v2.sh in arm A's tree;
  - the card's lock: a writable stand-in file (the runner's lock path set to it in this process), and the card's nodes a stand-in directory
    (e190_note1.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, the build record v2 and its day, the kernel at the pin, the host at its
record, the reader at its pin, the tiles, check_e190_v2.py --box and preflight_e190_v2.sh, both run), the lock (open, flock -n), the
holders (et-who through `timeout 20` and the real `ps` read), the start config through the real guard under `timeout 10` (its hostname and
ET_DEVICES rules), the identity gate, the sampler through the real guard, the stop-path test, the identity read, the smoke, the runs with
each host under the real `timeout 10`, the closing config, the manifest. Timing: the short sequence with the desk's short reads and the
doubles at a tenth of their time (the namespace's fields are set here; run_e190_v2.py's main() refuses them without --dry).

    python3 -B tools/claims-v3/e190/desk/realpath_e190_v2.py <scratch dir> A|B      (desk/realpath_e190_v2.sh runs both, in their namespaces)

Cases, arm A (hostname aifoundry2): RA0 the real build v2 in the stand-in tree (BUILT; ET_DEVICES not a gate here); RA1 the whole real
path: rc 0; RA2 the lock held by another process: 16, no config read; RA3 a host that hangs in P1 fp32: the real `timeout 10` ends it
(rc 124), flagged, the session goes on; RA4 a device process of ours (a stand-in named sys_emu): the real ps read refuses it: 16, no config
read; RA5 the reader not at its pin: the box check refuses it: 16, no lock taken.
Arm B (hostname aifoundry1): RB0 the real build v2 on this desk's stock device layer: RGM-BUILD-FAILED, "the host has no ET_DEVICES", and
the runner then refuses the failed record: 16; RB1 the whole real path (ET_DEVICES=1 through the real guard; card 1's identity): rc 0; RB2
the reader's config names card 0: 16 before the sampler; RB3 the sampler holds card 0's node: 16 before the smoke; RB4 the host names and
holds card 0: the watch trips in the smoke's first process, the stop file, "stopping:", 16; RB5 a v1 build record (no builder, no
ET_DEVICES reading): 16; RB6 the sampler dies in S1: S1 ends flagged, the sampler restarts through the real guard, rc 0.
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import fcntl
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
REL_E = "tools/claims-v3/e190"
CARD = {"A": "0", "B": "1"}
BOX = {"A": "aifoundry2", "B": "aifoundry1"}
READER = {"A": "build/ettelem-hpl/ettelem", "B": "build/ettelem/ettelem"}


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
    """The stand-in box tree: every file of the v2 harness copied byte for byte, the stand-ins, the stand-in lock and node directory."""
    tree = os.path.join(S, f"tree-{arm}")
    sys.path.insert(0, E)
    import check_e190_v2 as H
    files = list(H.FILES) + [REL_E + "/harness-e190-v2.json"]
    for rel in files:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e190_v2.py")
    for rel, words in ((READER[arm], ""), ("build/e190rgm/host/sparsity_host.standin", " host")):
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
    shutil.copy2("/usr/bin/sleep", os.path.join(b, "sys_emu"))          # a stand-in device process of ours, for RA4
    dev = os.path.join(S, f"dev-{arm}")
    os.makedirs(dev, exist_ok=True)
    lock = os.path.join(S, f"lock-{arm}", f"etsoc-shire{CARD[arm]}.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    open(lock, "a").close()
    return tree, b, os.path.realpath(dev), lock


def real_build(tree):
    r = subprocess.run(["bash", os.path.join(tree, REL_E, "build_e190_v2.sh")], cwd=tree, capture_output=True, text=True, timeout=900)
    return r.returncode, r.stdout + r.stderr


def standin_record(tree, arm, day, builder=True):
    """build/e190rgm/BUILD-e190.json for the stand-in host (the real kernel ELF beside it)."""
    host = os.path.join(tree, "build/e190rgm/host/sparsity_host")
    shutil.copy2(host + ".standin", host)
    rec = {"box": BOX[arm], "day": day, "epoch": int(time.time()), "verdict": "BUILT", "kernel_sha256": sha256(os.path.join(tree, "build/e190rgm/kernel/sparsity.elf")),
           "host_sha256": sha256(host), "host_checks": ["stand-in"], "what": "the real-path desk test's stand-in record (a stand-in host)"}
    if builder:
        rec.update(builder="build_e190_v2.sh",
                   et_devices="the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES" if arm == "B" else "not a gate on aifoundry2 (one card)")
    with open(os.path.join(tree, "build/e190rgm/BUILD-e190.json"), "w") as f:
        json.dump(rec, f, indent=1)


def session(S, arm, tree, name, env=None, pin_ok=True, seq="short"):
    """One real-path session in this process: returns (rc, log, out dir)."""
    import run_e190_v2 as R
    C, N1 = R.C, R.N1
    out = os.path.join(S, f"{arm}-{name}")
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E190_FAKE_")]:
        del os.environ[k]
    os.environ.update({"E190_FAKE_ARM": arm, "E190_FAKE_DEVDIR": N1.DEV_DIR, "E190_FAKE_LOCK": C.ARMS[arm]["lock"],
                       "E190_FAKE_SCHED": os.path.join(out, "sched.jsonl"), "E190_FAKE_SCALE": "0.1", "E190_FAKE_TAU_S": "0.5"})
    os.environ.update(env or {})
    open(os.environ["E190_FAKE_SCHED"], "a").close()
    want = C.ARMS[arm]["ettelem_sha256"]
    if not pin_ok:
        C.ARMS[arm]["ettelem_sha256"] = REGISTERED_PIN[arm]
    a = argparse.Namespace(what="session", arm=arm, t0=int(time.time()), out=out, deadline_epoch=0, dry=False, sequence=seq,
                           rest_s=0.5, smoke_rest_s=1.5, tail_s=0.3, gate_wait_s=3.0, rule_s=C.CARD_RULE_S, cap_s=C.CAP_S)
    try:
        rc = R.Session(a).run()
    finally:
        C.ARMS[arm]["ettelem_sha256"] = want
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    return rc, log, out


REGISTERED_PIN = {}


def has_proc(d):
    for dp, dn, fn in os.walk(d):
        if any(n.startswith("proc") and n.endswith(".out") for n in fn):
            return True
    return False


def arm_cases(t, S, arm):
    tree, b, dev, lock = make_tree(S, arm)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e190_v2 as R
    C, N1 = R.C, R.N1
    host = socket.gethostname()
    print(f"realpath_e190_v2 arm {arm}: hostname {host!r} (the namespace's), tree {os.path.relpath(tree, S)}, the runner {R.__file__ == os.path.join(tree, REL_E, 'run_e190_v2.py')}", flush=True)
    if host != BOX[arm]:
        t.case(f"R{arm}-host", False, f"the namespace's hostname is {host!r}, not {BOX[arm]!r}: run under desk/realpath_e190_v2.sh")
        return
    REGISTERED_PIN[arm] = C.ARMS[arm]["ettelem_sha256"]
    C.ARMS[arm]["ettelem_sha256"] = sha256(os.path.join(tree, READER[arm]))      # the stand-in reader's
    C.ARMS[arm]["lock"] = lock
    N1.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    day = R.pacific_day()
    if arm == "A":
        rc, txt = real_build(tree)
        rec = json.load(open(os.path.join(tree, "build/e190rgm/BUILD-e190.json")))
        t.case("RA0", rc == 0 and "RGM-BUILT rc=0" in txt and rec.get("builder") == "build_e190_v2.sh" and rec.get("kernel_sha256", "").startswith("aace138c")
               and "not a gate on aifoundry2" in rec.get("et_devices", ""),
               f"rc {rc}; {[ln for ln in txt.splitlines() if ln.startswith(('KERNEL', 'ETDEVICES', 'RGM-'))]}")
        standin_record(tree, arm, day)
        rc, log, d = session(S, arm, tree, "RA1")
        q = json.load(open(os.path.join(d, "queue.json"))) if os.path.exists(os.path.join(d, "queue.json")) else {}
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        boxtxt = open(os.path.join(d, "harness.txt")).read() + open(os.path.join(d, "preflight.txt")).read() if os.path.exists(os.path.join(d, "harness.txt")) else ""
        t.case("RA1", rc == 0 and "DRY" not in log and "the box and the build" in log and "HARNESS OK" in boxtxt and "dmcmd_audit: GO" in boxtxt
               and "smoke gate passed" in log and q.get("identity_read_ok") is True and all(x.get("ran") for x in q.get("queue", []))
               and len(q.get("queue", [])) == 4 and "config end" in log and os.path.exists(os.path.join(d, "MANIFEST.sha256"))
               and idn.get("config_start", {}).get("targets") == ["/dev/et0_mgmt"],
               f"rc {rc}; the box check {'passed' if 'the box and the build' in log else 'NOT passed'} (harness and preflight run); identity "
               f"{idn.get('config_start', {}).get('targets')} {idn.get('config_start', {}).get('ids')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}; "
               f"runs {sum(1 for x in q.get('queue', []) if x.get('ran'))} of {len(q.get('queue', []))}; real path (no DRY line) {'DRY' not in log}")
        holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)   # -o: flock holds it, its child not
        time.sleep(0.5)
        rc, log, d = session(S, arm, tree, "RA2")
        holder.terminate()
        holder.wait()
        t.case("RA2", rc == 16 and "the card's lock is held" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
        rc, log, d = session(S, arm, tree, "RA3", {"E190_FAKE_HOST": "hang", "E190_FAKE_HOST_FROM_N": "22", "E190_FAKE_HOST_COUNT": "1"})
        rj = os.path.join(d, "runs", "01-P1-burst-fp32", "run.json")
        rj = json.load(open(rj)) if os.path.exists(rj) else {}
        q = json.load(open(os.path.join(d, "queue.json"))) if os.path.exists(os.path.join(d, "queue.json")) else {}
        t.case("RA3", rc == 0 and [p["rc"] for p in rj.get("procs", [])] == [124] and any("rc 124" in f for f in rj.get("flags", []))
               and sum(1 for x in q.get("queue", []) if x.get("ran")) == 4,
               f"rc {rc}; P1 fp32's process rc {[p['rc'] for p in rj.get('procs', [])]} ({[p['t1_ms'] - p['t0_ms'] for p in rj.get('procs', [])]} ms); the queue went on")
        dp = subprocess.Popen([os.path.join(b, "sys_emu"), "30"], stdin=subprocess.DEVNULL)
        time.sleep(0.3)
        rc, log, d = session(S, arm, tree, "RA4")
        dp.terminate()
        dp.wait()
        t.case("RA4", rc == 16 and "other device process(es) of ours" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
        rc, log, d = session(S, arm, tree, "RA5", pin_ok=False)
        t.case("RA5", rc == 16 and "no device opened" in log and READER[arm] in log and not os.path.exists(os.path.join(d, "config-start.json")),
               f"rc {rc}; '{[ln[24:180] for ln in log.splitlines() if 'no device opened' in ln][:1]}'")
        return
    # ---- arm B
    src_elf = os.path.join(S, "tree-A", "build/e190rgm/kernel/sparsity.elf")
    rc, txt = real_build(tree)
    rec = json.load(open(os.path.join(tree, "build/e190rgm/BUILD-e190.json"))) if os.path.exists(os.path.join(tree, "build/e190rgm/BUILD-e190.json")) else {}
    rc2, log2, d2 = session(S, arm, tree, "RB0")
    t.case("RB0", rc == 1 and "RGM-BUILD-FAILED: ET_DEVICES: the host has no ET_DEVICES" in txt and rec.get("verdict") == "BUILD-FAILED"
           and rc2 == 16 and "no device opened" in log2,
           f"build rc {rc}; {[ln for ln in txt.splitlines() if ln.startswith(('ETDEVICES', 'RGM-'))]}; the runner then rc {rc2}")
    os.makedirs(os.path.join(tree, "build/e190rgm/kernel"), exist_ok=True)
    shutil.copy2(src_elf, os.path.join(tree, "build/e190rgm/kernel/sparsity.elf"))
    standin_record(tree, arm, day)
    rc, log, d = session(S, arm, tree, "RB1")
    q = json.load(open(os.path.join(d, "queue.json"))) if os.path.exists(os.path.join(d, "queue.json")) else {}
    idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
    t.case("RB1", rc == 0 and "DRY" not in log and "smoke gate passed" in log and q.get("identity_read_ok") is True and len(q.get("queue", [])) == 4
           and all(x.get("ran") for x in q.get("queue", [])) and idn.get("config_start", {}).get("targets") == ["/dev/et1_mgmt"]
           and idn.get("config_start", {}).get("minion_mv") == 499 and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et1_mgmt"],
           f"rc {rc}; identity {idn.get('config_start')}; the read {idn.get('etwho_with_sampler', {}).get('counts')}, the sampler "
           f"{idn.get('sampler_nodes', {}).get('nodes')}; smoke hosts {[(k, v['host']['stderr_targets'], v['host']['nodes_held']) for k, v in idn.get('smoke', {}).items()]}")
    rc, log, d = session(S, arm, tree, "RB2", {"E190_FAKE_CONFIG": "card0"})
    t.case("RB2", rc == 16 and "the card's identity" in log and "sampler started" not in log and not has_proc(d), f"rc {rc}")
    rc, log, d = session(S, arm, tree, "RB3", {"E190_FAKE_SAMPLER": "card0"})
    t.case("RB3", rc == 16 and "the identity read" in log and not has_proc(d), f"rc {rc}; '{[ln[24:200] for ln in log.splitlines() if 'identity read' in ln][:1]}'")
    rc, log, d = session(S, arm, tree, "RB4", {"E190_FAKE_HOST": "card0"})
    err = open(os.path.join(d, "smoke", "fp32", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "fp32", "proc.err")) else ""
    t.case("RB4", rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log
           and not os.path.isdir(os.path.join(d, "smoke", "fp16")),
           f"rc {rc}; the host stopped by the file {'stopping:' in err}; smoke processes {sorted(os.listdir(os.path.join(d, 'smoke'))) if os.path.isdir(os.path.join(d, 'smoke')) else []}")
    standin_record(tree, arm, day, builder=False)
    rc, log, d = session(S, arm, tree, "RB5")
    t.case("RB5", rc == 16 and "not build_e190_v2.sh's" in log and "no device opened" in log, f"rc {rc}")
    standin_record(tree, arm, day)
    rc, log, d = session(S, arm, tree, "RB6", {"E190_FAKE_SAMPLER": "dies:90"})
    rj = os.path.join(d, "runs", "04-S1-sus-fp32", "run.json")
    rj = json.load(open(rj)) if os.path.exists(rj) else {}
    t.case("RB6", rc == 0 and any("the sampler was not live before process" in f for f in rj.get("flags", [])) and "restarting it" in log
           and log.count("sampler started") >= 2,
           f"rc {rc}; S1's processes {len(rj.get('procs', []))} of 12; flags {[f[:90] for f in rj.get('flags', [])]}; sampler starts {log.count('sampler started')}")


def main(argv):
    if len(argv) != 2 or argv[1] not in ("A", "B"):
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    devs = [x for x in os.listdir("/dev") if x.startswith("et")]
    if devs:
        print("REFUSED: a /dev/et* node is visible: run this inside the sandbox (no /dev/et*, an empty /run/lock)")
        return 3
    os.makedirs(S, exist_ok=True)
    t = T()
    print(f"realpath_e190_v2 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    arm_cases(t, S, argv[1])
    print(f"REALPATH-E190-V2 arm {argv[1]}: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
