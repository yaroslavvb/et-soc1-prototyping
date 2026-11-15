#!/usr/bin/env python3
"""E191's REAL-PATH desk test (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum; CONTEXT
sections 104, 107 and 109's lesson: a check that runs only on the real path is exercised by a desk test of the real path, never by the
dry pass alone). run_e191.py's session WITHOUT --dry, on a stand-in box tree (~/nekko's form), as on the card day except for these
stand-ins (E190's kit note 1's real-path test's form, desk/realpath_e190_v2.py):
  - the hostname: aifoundry1, from a private UTS namespace (desk/realpath_e191.sh starts this driver under bubblewrap with --hostname
    aifoundry1, a private PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock); the second namespace,
    --hostname aifoundry2, is the wrong-box case;
  - the telemetry reader behind E191's REAL guard: build/ettelem/ettelem is a script that runs fake_card_e191.py (config, sample) under
    the name ettelem (fix-e191k, the verifier's nit 7: it execs the interpreter through a link named ettelem, so ps reads the sampler's
    comm as the real reader's and the per-pass count of our device processes meets it and must skip it by pid); the runner's pin for it
    is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e191.py etwho, which reads who holds the stand-in nodes and the stand-in lock from
    /proc, as et-who's fuser does;
  - the two hosts: build/e191ledger/host/ledger_host and build/e191spp/host/sparseparity_host are scripts (the names the runner runs) that
    run fake_card_e191.py host-ledger / host-spp; their build records (BUILD-e191.json, today's, builder build_e191.sh) carry their sha256;
  - card 1's lock: a writable stand-in file (the runner's lock path set to it in this process); the cards' nodes: a stand-in directory
    (e191_ident.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, ET_DEVICES, the reader at its pin, today's build records and the hosts at
their sha256), the lock (open, flock -n), the holders (et-who through `timeout 20`, the real `ps` read of other users' and our own device
processes), the start config through E191's real guard under `timeout 10` (its hostname and ET_DEVICES rules) with its stderr kept, THE
IDENTITY GATE (a) and (b) (the sampler's own fds read from /proc), the sampler through the real guard, the stop-path test, the ramped
smoke and the six passes of the short sequence with each host under the real `timeout 10` and watched (its stderr block and its held
nodes), the runner's bound around it, the closing config, the manifest. Timing: the short sequence with the desk's short idles and the
doubles at a tenth of their time (the namespace's fields are set here; run_e191.py's main() refuses them without --dry).

    python3 -B tools/claims-v3/e191/desk/realpath_e191.py <scratch dir> aifoundry1|aifoundry2    (desk/realpath_e191.sh runs both)

Cases, hostname aifoundry1 (verdicts stated first):
  RP1  the whole real path: rc 0, no DRY line, the box check, identity (a) and (b) on card 1's forms, the stop-path test, the smoke (every
       device-opening host on card 1), six passes reading PASS, the closing config, the manifest; the commands it ran are the real ones;
  RP2  card 1's lock held by another process: 16, no config read;
  RP3  a device process of ours already running (a stand-in named stray_host): the real ps read refuses it: 16, no config read;
  RP4  the reader not at its pin: the box check refuses: 16, no lock taken, no config read;
  RP5  a build record not build_e191.sh's (E189's form): 16;  RP6 a build record without the passing ET_DEVICES reading: 16;
  RP7  the reader's config names card 0 (through the real guard): IDENTITY GATE FAILED, 16, no sampler;
  RP8  ET_DEVICES: the real guard refuses a config read without ET_DEVICES, with ET_DEVICES=0 and with ET_DEVICES=1 off aifoundry1 (exit
       97, the reader never started), and passes it with ET_DEVICES=1 here; a session whose environment lacks ET_DEVICES: the box check, 16;
  RP9  the sampler holds card 0's node: identity (b), 16, no host;
  RP10 another login on card 0: 16, no config read;  RP11 ours on card 0 (another session of ours on aifoundry1): 16, no config read;
  RP12 a host names and holds card 0 in the smoke: the watch, the smoke gate fails at the first device-opening host, 16;
  RP13 a host that hangs (honouring SIGTERM) in pass 1: the real `timeout 10` ends it (rc 124 at about 10 s), FAILED RUN, the queue goes on;
  RP14 a host that ignores SIGTERM past `timeout 10` and the runner's bound (12 s here): BOUND, nothing killed, the queue stops; card 1's
       lock stays HELD while it runs (a flock -n from this test is refused: the verifier's X10, finding 4), the runner polls its end and
       the closing read runs after it, rc 0; the stand-in host has ended when the session returns.
The verifier's findings and nits on the real path (fix-e191k, Sat 14 Nov 2026, before any E191 datum; its X3-X6, X9, X11):
  RP1  also: the sampler's process is named ettelem (its /proc comm, read while it ran) and the six passes passed the holder rule beside
       it (the per-pass count skips it by pid: nit 7);
  RP15 a quiet sampler (alive, silent from the schedule's 9th launch, in pass 1): stopped (SIGTERM, through the guard's exec) and restarted;
       every host started on a sample under 2 s old; rc 0 (finding 2; the verifier's X9 ran five passes on no live sample);
  RP16 a process of ours holding card 0's ops node from pass 1 on: STOP before pass 2 (nit 8; X3);  RP17 another login on card 0 from
       et-who's 4th call (before pass 2): STOP before pass 2 (nit 8; X4);
  RP18 et-who refused (rc 1, nothing on stdout) before the first card command: unreadable, no device opened, no config read (finding 3;
       X6 had opened the device);  RP19 et-who refused from its 4th call: STOP before pass 2 (X5 ran passes 2-6 blind);
  RP20 a stray sparseparity_host of ours holding no node (ps shows 'sparseparity_ho'): refused, no device opened (nit 6; X11);
  RP21 the stop file written while pass 1's host runs: that host ends by itself, no further pass, the closing read, the manifest, rc 0
       (finding 5).
The second verifier's nits on the real path (fix-e191k2, Sun 15 Nov 2026, before any E191 datum; the stand-in records now carry the
kernel gate's line, as build_e191.sh's do):
  RP22 a kernel changed after its build record was written: the box check refuses (16, nothing started) (nit 5);  RP23 a build record
       without the kernel gate's OK line: refused (nit 5);
  RP24 the reader keeps printing without board_w from the schedule's 9th launch: those lines are not live, the sampler is restarted
       through the guard, every host starts on a live sample, each pass flagged exactly when its largest live-sample gap was 2 s or more
       (nits 1 and 2);
  RP25 the stop file written as the start config read is logged: "... before the stop-path test: the gate, no launch", 16, no smoke, the
       closing read, never "stop-path test failed" (nit 3).
Hostname aifoundry2 (the second namespace):
  RW1  the wrong box: the box check refuses (16, no device opened), and the real guard refuses its config read (97).
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
REL_E = "tools/claims-v3/e191"


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
    """The stand-in box tree: every file of the harness copied byte for byte, the stand-ins, the stand-in lock and node directory."""
    tree = os.path.join(S, "tree")
    sys.path.insert(0, E)
    import check_e191 as H
    for rel in list(H.FILES) + [REL_E + "/harness-e191.json"]:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e191.py")
    b = os.path.join(S, "bin")
    os.makedirs(b, exist_ok=True)
    os.symlink("/usr/bin/python3", os.path.join(b, "ettelem"))         # nit 7: the stand-in reader runs under the reader's own name
    for rel, words, interp in (("build/ettelem/ettelem", "", os.path.join(b, "ettelem")),
                               ("build/e191ledger/host/ledger_host", " host-ledger", "/usr/bin/python3"),
                               ("build/e191spp/host/sparseparity_host", " host-spp", "/usr/bin/python3")):
        p = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(f'#!/bin/sh\n[ -n "$REALPATH_MARK" ] && echo "$0 $*" >> "$REALPATH_MARK"\nexec "{interp}" -B "{fake}"{words} "$@"\n')
        os.chmod(p, 0o755)
    for rel, text in (("build/e191ledger/kernel/ledger.elf", "E191 real-path stand-in kernel: ledger\n"),
                      ("build/e191spp/kernel/sparseparity.elf", "E191 real-path stand-in kernel: sparse parity\n")):
        os.makedirs(os.path.dirname(os.path.join(tree, rel)), exist_ok=True)
        open(os.path.join(tree, rel), "w").write(text)
    with open(os.path.join(b, "et-who"), "w") as f:
        f.write(f'#!/bin/sh\nexec /usr/bin/python3 -B "{fake}" etwho\n')
    os.chmod(os.path.join(b, "et-who"), 0o755)
    shutil.copy2("/usr/bin/sleep", os.path.join(b, "stray_host"))      # a stand-in device process of ours (its name ends _host)
    dev = os.path.join(S, "dev")
    os.makedirs(dev, exist_ok=True)
    lock = os.path.join(S, "lock", "etsoc-shire1.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    open(lock, "a").close()
    return tree, b, os.path.realpath(dev), lock


def records(tree, day, builder="build_e191.sh", etd="yes", kgate=True):
    for prog, d, host, elf in (("ledger", "build/e191ledger", "host/ledger_host", "kernel/ledger.elf"),
                               ("spp", "build/e191spp", "host/sparseparity_host", "kernel/sparseparity.elf")):
        rec = {"builder": builder, "box": "aifoundry1", "day": day, "epoch": int(time.time()), "verdict": "BUILT", "why": "",
               "host": f"{d}/{host}", "host_sha256": sha256(os.path.join(tree, d, host)), "kernel": f"{d}/{elf}",
               "kernel_sha256": sha256(os.path.join(tree, d, elf)), "et_devices": etd,
               # fix-e191k2 (nit 5): build_e191.sh writes the kernel gate's own line; the box check now reads it
               "kernel_gate": (f"KERNEL OK {prog}: (the real-path desk test's stand-in record)" if kgate else "not read"),
               "what": "the real-path desk test's stand-in record (a stand-in host)"}
        with open(os.path.join(tree, d, "BUILD-e191.json"), "w") as f:
            json.dump(rec, f, indent=1)


def session(S, tree, name, env=None, seq="short", host_bound_s=None):
    """One real-path session in this process: returns (rc, log, out dir, queue)."""
    import run_e191 as R
    C, I = R.C, R.I
    out = os.path.join(S, name)
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E191_FAKE_") or k == "REALPATH_MARK"]:
        del os.environ[k]
    os.environ.update({"E191_FAKE_DEVDIR": I.DEV_DIR, "E191_FAKE_LOCK": C.LOCK, "E191_FAKE_SCHED": os.path.join(out, "sched.jsonl"),
                       "E191_FAKE_SCALE": "0.1", "REALPATH_MARK": os.path.join(out, "started.txt")})
    os.environ.update(env or {})
    open(os.environ["E191_FAKE_SCHED"], "a").close()
    a = argparse.Namespace(what="session", t0=int(time.time()), out=out, programs="ledger,spp", deadline_epoch=0, rapl_allowed=False,
                           dry=False, double="inject", sequence=seq, idle_before=0.5, idle_after=0.5, anchor_s=0.5, die_wait_s=3.0,
                           cap_pass_s=C.CAP_PASS_START_S, cap_end_s=C.CAP_S, host_bound_s=host_bound_s or C.HOST_BOUND_S)
    rc = R.Session(a).run()
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
    print(f"   [{name}] rc {rc}; " + " | ".join(ln[24:200] for ln in log.splitlines()
                                                 if any(w in ln for w in ("STOP", "gate", "no device opened", "BOUND", "box check",
                                                                          "IDENTITY", "smoke gate"))), flush=True)
    return rc, log, out, q


def started(out):
    """The stand-in reader's and hosts' starts in this session (each script appends its own command line)."""
    p = os.path.join(out, "started.txt")
    return open(p).read().splitlines() if os.path.exists(p) else []


def guard_call(tree, env_extra, unset=False):
    e = {k: v for k, v in os.environ.items() if not k.startswith("E191_FAKE_")}     # the doubles' plain modes (card 1's block)
    e.pop("ET_DEVICES", None)
    e.pop("V3_DEVICE", None)
    mark = os.path.join(tree, "..", "guard-mark.txt")
    if os.path.exists(mark):
        os.remove(mark)
    e["REALPATH_MARK"] = mark
    e.update(env_extra)
    r = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e191.sh"), "config"], cwd=tree, env=e,
                       capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout, r.stderr, os.path.exists(mark)


def run_cases(t, S, host_want):
    tree, b, dev, lock = make_tree(S)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e191 as R
    C, I = R.C, R.I
    host = socket.gethostname()
    print(f"realpath_e191: hostname {host!r} (the namespace's); the runner is the stand-in tree's: "
          f"{R.__file__ == os.path.join(tree, REL_E, 'run_e191.py')}", flush=True)
    if host != host_want:
        t.case(f"host-{host_want}", False, f"the namespace's hostname is {host!r}, not {host_want!r}: run under desk/realpath_e191.sh")
        return
    registered_pin = C.READER_SHA256
    C.READER_SHA256 = sha256(os.path.join(tree, C.READER))
    C.LOCK = lock
    I.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    day = R.pacific_day()
    records(tree, day)
    if host_want == "aifoundry2":
        rc, log, out, q = session(S, tree, "RW1")
        grc, gout, gerr, gm = guard_call(tree, {"ET_DEVICES": "1"})
        t.case("RW1", rc == 16 and "the box check: this host is 'aifoundry2', not aifoundry1" in log and "no device opened" in log
               and not os.path.exists(os.path.join(out, "config-start.json")) and grc == 97 and "box 'aifoundry2'" in gerr and not gm,
               f"rc {rc}; the guard rc {grc} ('{gerr.strip()[:90]}'), the reader started {gm}")
        return
    # ---- RP1: the whole real path (and, nit 7, the sampler's process name read while it runs)
    comms = {}

    def watch_comm(out):
        L = os.path.join(out, "session.log")
        t = time.time()
        while time.time() - t < 120 and not os.path.exists(os.path.join(out, "MANIFEST.sha256")):
            try:
                for ln in open(L):
                    if "sampler started (attempt" in ln:
                        pid = int(ln.split("pid ", 1)[1].split(",", 1)[0])
                        if pid not in comms:
                            comms[pid] = open(f"/proc/{pid}/comm").read().strip()
            except (OSError, ValueError, IndexError):
                pass
            time.sleep(0.1)
    th = threading.Thread(target=watch_comm, args=(os.path.join(S, "RP1"),), daemon=True)
    th.start()
    rc, log, out, q = session(S, tree, "RP1")
    th.join(timeout=10)
    print(f"   RP1: the sampler's process name(s) while it ran: {sorted(set(comms.values()))}")
    idn = json.load(open(os.path.join(out, "identity.json"))) if os.path.exists(os.path.join(out, "identity.json")) else {}
    cmds = [json.loads(ln) for ln in open(os.path.join(out, "commands.jsonl"))] if os.path.exists(os.path.join(out, "commands.jsonl")) else []
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP1", rc == 0 and "DRY" not in log and "the box check: aifoundry1, ET_DEVICES=1" in log
           and "identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510" in log and "identity (b): et-who with the sampler running" in log
           and "stop-path test passed" in log and "smoke gate passed" in log and len(ran) == 6 and all(x.get("reading") == "PASS" for x in ran)
           and q.get("identity_ok") is True and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et1_mgmt"]
           and all(v["right"] and not v["wrong"] for k, v in idn.get("smoke", {}).items() if k != "ledger-selftest")
           and "config end:" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
           and cmds and all(c["real"] == c["used"] and c["et_devices"] == "1" for c in cmds)
           and any(c["used"][:4] == ["timeout", "10", "bash", C.GUARD] for c in cmds)
           and comms and set(comms.values()) == {"ettelem"},
           f"rc {rc}; passes {[x.get('reading') for x in ran]}; identity {idn.get('config_start')}, et-who "
           f"{idn.get('etwho_with_sampler', {}).get('counts')}, the sampler {idn.get('sampler_nodes', {}).get('nodes')} named "
           f"{sorted(set(comms.values()))}; {len(cmds)} commands, each the real one, each ET_DEVICES=1")
    # ---- RP2: the lock held
    holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc, log, out, q = session(S, tree, "RP2")
    holder.terminate()
    holder.wait()
    t.case("RP2", rc == 16 and "card 1's lock is held: no device opened" in log and not os.path.exists(os.path.join(out, "config-start.json")),
           f"rc {rc}")
    # ---- RP3: a device process of ours
    dp = subprocess.Popen([os.path.join(b, "stray_host"), "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.3)
    rc, log, out, q = session(S, tree, "RP3")
    dp.terminate()
    dp.wait()
    t.case("RP3", rc == 16 and "device process(es) of ours besides the sampler" in log and "no device opened" in log
           and not os.path.exists(os.path.join(out, "config-start.json")), f"rc {rc}")
    # ---- RP4: the reader off its pin
    C.READER_SHA256 = registered_pin
    rc, log, out, q = session(S, tree, "RP4")
    C.READER_SHA256 = sha256(os.path.join(tree, C.READER))
    t.case("RP4", rc == 16 and "not at its pin" in log and "no device opened" in log and not started(out)
           and not os.path.exists(os.path.join(out, "etwho-before.txt")), f"rc {rc}; nothing started {not started(out)}")
    # ---- RP5, RP6: the build records
    records(tree, day, builder="build_e189.sh")
    rc5, log5, out5, _ = session(S, tree, "RP5")
    records(tree, day, etd="not a gate on aifoundry2 (E191 runs on aifoundry1): no: the host has no ET_DEVICES")
    rc6, log6, out6, _ = session(S, tree, "RP6")
    records(tree, day)
    t.case("RP5", rc5 == 16 and "build record is not build_e191.sh's BUILT of today" in log5 and not started(out5), f"rc {rc5}")
    t.case("RP6", rc6 == 16 and "has no passing ET_DEVICES reading" in log6 and not started(out6), f"rc {rc6}")
    # ---- RP7: the config names card 0
    rc, log, out, q = session(S, tree, "RP7", {"E191_FAKE_CONFIG": "card0"})
    st = started(out)
    t.case("RP7", rc == 16 and "IDENTITY GATE FAILED: PCIe target /dev/et0_mgmt, not /dev/et1_mgmt" in log and "sampler started" not in log
           and not any("host" in x for x in st) and os.path.exists(os.path.join(out, "config-start.err")),
           f"rc {rc}; started {[x.split()[0].rsplit('/', 1)[-1] + ' ' + x.split()[1] for x in st]}")
    # ---- RP8: ET_DEVICES and the real guard
    g_unset = guard_call(tree, {})
    g_zero = guard_call(tree, {"ET_DEVICES": "0"})
    g_one = guard_call(tree, {"ET_DEVICES": "1"})
    orig = C.device_env

    def no_etd(base=None):
        e = orig(base)
        e.pop("ET_DEVICES", None)
        return e
    C.device_env = no_etd
    rc, log, out, q = session(S, tree, "RP8")
    C.device_env = orig
    print(f"   the guard: unset rc {g_unset[0]} ('{g_unset[2].strip()[:80]}'), reader started {g_unset[3]}; 0 rc {g_zero[0]}, reader "
          f"started {g_zero[3]}; 1 rc {g_one[0]} ({'card 1' if '/dev/et1_mgmt' in g_one[2] else 'no card 1 block'}), reader started {g_one[3]}")
    t.case("RP8", g_unset[0] == 97 and "ET_DEVICES is 'unset'" in g_unset[2] and not g_unset[3] and g_zero[0] == 97 and not g_zero[3]
           and g_one[0] == 0 and "/dev/et1_mgmt" in g_one[2] and g_one[3]
           and rc == 16 and "ET_DEVICES is not 1 in the session's environment" in log and not started(out),
           f"the guard refused unset and 0 (97, no reader started), passed 1; the session without ET_DEVICES rc {rc}")
    # ---- RP9: the sampler on card 0
    rc, log, out, q = session(S, tree, "RP9", {"E191_FAKE_SAMPLER": "card0"})
    t.case("RP9", rc == 16 and "identity (b): IDENTITY GATE FAILED" in log and not any("host" in x for x in started(out)), f"rc {rc}")
    # ---- RP10, RP11: holders on card 0
    rc10, log10, out10, _ = session(S, tree, "RP10", {"E191_FAKE_ETWHO": "other0"})
    rc11, log11, out11, _ = session(S, tree, "RP11", {"E191_FAKE_ETWHO": "ours0"})
    t.case("RP10", rc10 == 16 and "holder line(s) of another login" in log10 and not os.path.exists(os.path.join(out10, "config-start.json")),
           f"rc {rc10}")
    t.case("RP11", rc11 == 16 and "holder line(s) of ours off card 1" in log11 and not os.path.exists(os.path.join(out11, "config-start.json")),
           f"rc {rc11}")
    # ---- RP12: a host on card 0 in the smoke
    rc, log, out, q = session(S, tree, "RP12", {"E191_FAKE_HOST": "card0"})
    sm = sorted(os.listdir(os.path.join(out, "smoke"))) if os.path.isdir(os.path.join(out, "smoke")) else []
    t.case("RP12", rc == 16 and "smoke gate failed: copy-64m-random: the host's card: ANOTHER CARD" in log and sm == ["copy-64m-random", "ledger-selftest"],
           f"rc {rc}; smoke processes {sm}")
    # ---- RP13: a host that hangs, honouring SIGTERM: the real timeout 10
    rc, log, out, q = session(S, tree, "RP13", {"E191_FAKE_HOST": "hang", "E191_FAKE_HOST_FROM": "8", "E191_FAKE_HOST_COUNT": "1",
                                                 "E191_FAKE_WEDGE_S": "25"})
    rj = os.path.join(out, "passes", "copy-zeros", "p1", "run.json")
    rj = json.load(open(rj)) if os.path.exists(rj) else {}
    dur = ((rj.get("host_t1_ms") or 0) - (rj.get("host_t0_ms") or 0)) / 1000.0
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP13", rc == 0 and rj.get("host_rc") == 124 and 9.5 <= dur <= 12.5 and len(ran) == 6 and ran[0].get("reading", "").startswith("FAILED RUN")
           and "BOUND" not in log, f"rc {rc}; pass 1's host rc {rj.get('host_rc')} after {dur:.2f} s (the real timeout 10); passes {len(ran)}")
    # ---- RP14: a host that ignores SIGTERM: the runner's bound; card 1's lock held while it runs (finding 4)
    t0 = time.time()
    held = {}

    def try_lock(out):
        L = os.path.join(out, "session.log")
        t = time.time()
        while time.time() - t < 120:
            if os.path.exists(L) and "BOUND: the host process" in open(L).read():
                time.sleep(0.5)
                alive_then = subprocess.run(["pgrep", "-f", "host-ledger"], capture_output=True, text=True).stdout.split()
                held["flock_rc"] = subprocess.run(["flock", "-n", lock, "true"]).returncode
                held["host_alive"] = bool(alive_then)
                return
            time.sleep(0.05)
    th = threading.Thread(target=try_lock, args=(os.path.join(S, "RP14"),), daemon=True)
    th.start()
    rc, log, out, q = session(S, tree, "RP14", {"E191_FAKE_HOST": "wedge", "E191_FAKE_HOST_FROM": "8", "E191_FAKE_HOST_COUNT": "1",
                                                 "E191_FAKE_WEDGE_S": "16"}, host_bound_s=12)
    th.join(timeout=10)
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    alive = subprocess.run(["pgrep", "-f", "host-ledger"], capture_output=True, text=True).stdout.split()
    bd = (q.get("bound") or [{}])[0]
    lines = log.splitlines()
    i_end = next((i for i, ln in enumerate(lines) if "the host past the bound" in ln and "has ended" in ln), None)
    i_cfg = next((i for i, ln in enumerate(lines) if "config end: TDP" in ln), None)
    t.case("RP14", rc == 0 and "BOUND: the host process" in log and "nothing is killed; the queue stops" in log and len(ran) == 1
           and len(q.get("bound") or []) == 1 and "config end:" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
           and held.get("flock_rc") == 1 and held.get("host_alive") is True and bd.get("ended_ms") and not alive
           and i_end is not None and i_cfg is not None and i_end < i_cfg,
           f"rc {rc} after {time.time() - t0:.1f} s; passes {len(ran)}; while the stuck host ran (alive {held.get('host_alive')}) a flock -n on "
           f"card 1's lock read rc {held.get('flock_rc')} (1 = held); its end polled, the closing read after it; alive when the session "
           f"returned: {bool(alive)}")
    # ---- fix-e191k: the verifier's real-path cases X3-X6, X9, X11, and the early stop
    rc, log, out, q = session(S, tree, "RP15", {"E191_FAKE_SAMPLER": "hangs:9"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    ages = [json.load(open(os.path.join(out, "passes", x["pass"], "run.json"))).get("sample_age_s_at_host_start") for x in ran]
    t.case("RP15", rc == 0 and "the sampler is not live (alive True" in log and "restarting it" in log and len(ran) >= 5
           and all(a is not None and a < 2.0 for a in ages), f"rc {rc}; passes {len(ran)}; the last sample's age at each host start {ages}")
    hold = {}

    def hold_card0(out):
        L = os.path.join(out, "session.log")
        t = time.time()
        while time.time() - t < 60:
            if os.path.exists(L) and "pass 1: copy-zeros p1 (K" in open(L).read():
                hold["p"] = subprocess.Popen(["/usr/bin/python3", "-I", "-B", "-c", f"import time; f = open({os.path.join(dev, 'et0_ops')!r}, 'a'); "
                                              "time.sleep(40)"], stdin=subprocess.DEVNULL)
                return
            time.sleep(0.05)
    th = threading.Thread(target=hold_card0, args=(os.path.join(S, "RP16"),), daemon=True)
    th.start()
    rc, log, out, q = session(S, tree, "RP16")
    th.join(timeout=10)
    if hold.get("p"):
        hold["p"].terminate()
        hold["p"].wait()
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP16", rc == 0 and len(ran) == 1 and "STOP before pass 2:" in log and "holder line(s) of ours off card 1" in log
           and "config end:" in log, f"rc {rc}; passes {len(ran)}")
    rc, log, out, q = session(S, tree, "RP17", {"E191_FAKE_ETWHO": "other0", "E191_FAKE_ETWHO_FROM": "4"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP17", rc == 0 and len(ran) == 1 and "STOP before pass 2:" in log and "holder line(s) of another login" in log,
           f"rc {rc}; passes {len(ran)}")
    rc, log, out, q = session(S, tree, "RP18", {"E191_FAKE_ETWHO": "fail"})
    t.case("RP18", rc == 16 and "et-who unreadable (rc 1, nothing on its stdout)" in log and "no device opened" in log
           and not os.path.exists(os.path.join(out, "config-start.json")) and not started(out), f"rc {rc}; nothing started {not started(out)}")
    rc, log, out, q = session(S, tree, "RP19", {"E191_FAKE_ETWHO": "fail", "E191_FAKE_ETWHO_FROM": "4"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP19", rc == 0 and len(ran) == 1 and "STOP before pass 2: et-who unreadable (rc 1" in log and "config end:" in log,
           f"rc {rc}; passes {len(ran)}")
    shutil.copy2("/usr/bin/sleep", os.path.join(b, "sparseparity_host"))
    dp = subprocess.Popen([os.path.join(b, "sparseparity_host"), "40"], stdin=subprocess.DEVNULL)
    time.sleep(0.3)
    comm = open(f"/proc/{dp.pid}/comm").read().strip()
    rc, log, out, q = session(S, tree, "RP20")
    dp.terminate()
    dp.wait()
    t.case("RP20", rc == 16 and comm == "sparseparity_ho" and "1 device process(es) of ours besides the sampler" in log and "no device opened" in log
           and not os.path.exists(os.path.join(out, "config-start.json")), f"its comm {comm!r}; rc {rc}")
    stopped = {}

    def stop_in_pass1(out):
        sched = os.path.join(out, "sched.jsonl")
        t = time.time()
        while time.time() - t < 60:
            if os.path.exists(sched) and sum(1 for ln in open(sched) if '"tag": "pass"' in ln) >= 1:
                open(os.path.join(out, "STOP"), "w").close()
                stopped["at"] = time.time()
                return
            time.sleep(0.01)
    th = threading.Thread(target=stop_in_pass1, args=(os.path.join(S, "RP21"),), daemon=True)
    th.start()
    rc, log, out, q = session(S, tree, "RP21")
    th.join(timeout=10)
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP21", rc == 0 and stopped and [x["pass"] for x in ran] == ["copy-zeros/p1"] and "STOP: an early stop was asked for (the stop file" in log
           and "config end: TDP" in log and (q.get("early_stop") or "").startswith("an early stop was asked for (the stop file")
           and os.path.exists(os.path.join(out, "MANIFEST.sha256")), f"rc {rc}; passes {[x['pass'] for x in ran]}; early_stop {q.get('early_stop')}")
    # ---- fix-e191k2: the second verifier's nits 5, 1 and 3 on the real path
    sk = os.path.join(tree, "build/e191spp/kernel/sparseparity.elf")
    keep = open(sk, "rb").read()
    with open(sk, "ab") as f:
        f.write(b"one byte more after the build\n")
    rc, log, out, q = session(S, tree, "RP22")
    with open(sk, "wb") as f:
        f.write(keep)
    t.case("RP22", rc == 16 and "spp's kernel is not the one its build record names" in log and "no device opened" in log and not started(out)
           and not os.path.exists(os.path.join(out, "etwho-before.txt")),
           f"rc {rc}; a kernel changed after its build record was written: refused at the box check, nothing started {not started(out)}")
    records(tree, day, kgate=False)
    rc, log, out, q = session(S, tree, "RP23")
    records(tree, day)
    t.case("RP23", rc == 16 and "build record carries no passing kernel gate line" in log and "no device opened" in log and not started(out),
           f"rc {rc}; a build record without the kernel gate's OK line: refused at the box check")
    rc, log, out, q = session(S, tree, "RP24", {"E191_FAKE_SAMPLER": "noboard:9"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    rows = []
    for x in ran:
        rjx = json.load(open(os.path.join(out, "passes", x["pass"], "run.json")))
        pjx = json.load(open(os.path.join(out, "passes", x["pass"], "pass.json")))
        fl = any(f.startswith("the sampler was not live during this pass") for f in pjx.get("flags") or [])
        rows.append((x["pass"], rjx.get("sample_age_s_at_host_start"), rjx.get("live_gap_s_pass"), fl, pjx.get("sampler_live")))
    cons = all(a is not None and a < 2.0 and g is not None and (g >= 2.0) == fl and sl is (not fl) for _, a, g, fl, sl in rows)
    t.case("RP24", rc == 0 and "line(s) since without a stop line's reading): restarting it" in log and len(ran) >= 5 and cons
           and (q.get("sampler_lines_not_live") or 0) > 0 and sorted(q.get("passes_sampler_not_live") or []) == sorted(k for k, _, _, fl, _ in rows if fl),
           f"rc {rc}; lines without board_w {q.get('sampler_lines_not_live')}: the sampler restarted through the guard; (pass, age at host start, "
           f"largest live-sample gap, flagged, sampler_live) {rows}")
    early = {}

    def stop_at_config(out):
        L = os.path.join(out, "session.log")
        t0 = time.time()
        while time.time() - t0 < 60:
            if os.path.exists(L) and "config start:" in open(L).read():
                open(os.path.join(out, "STOP"), "w").close()
                early["at"] = time.time()
                return
            time.sleep(0.002)
    th = threading.Thread(target=stop_at_config, args=(os.path.join(S, "RP25"),), daemon=True)
    th.start()
    rc, log, out, q = session(S, tree, "RP25")
    th.join(timeout=10)
    t.case("RP25", rc == 16 and early and "before the stop-path test: the gate, no launch" in log and "stop-path test failed" not in log
           and "config end: TDP" in log and not os.path.isdir(os.path.join(out, "smoke"))
           and (q.get("early_stop") or "").startswith("an early stop was asked for (the stop file") and os.path.exists(os.path.join(out, "MANIFEST.sha256")),
           f"rc {rc}; the stop file written as the start config read was logged: an early stop at the gate, never 'stop-path test failed'")
    time.sleep(2)


def main(argv):
    if len(argv) != 2 or argv[1] not in ("aifoundry1", "aifoundry2"):
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
    print(f"realpath_e191 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    run_cases(t, S, argv[1])
    print(f"REALPATH-E191 {argv[1]}: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
