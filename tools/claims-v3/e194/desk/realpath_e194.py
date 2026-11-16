#!/usr/bin/env python3
"""E194's REAL-PATH desk test (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum; the lesson of CONTEXT
sections 104, 107, 109 and 116: a check that runs only on the real path is exercised by a desk test of the real path, never by the dry pass
alone). run_e194.py's session WITHOUT --dry (DRY unset), on a stand-in box tree (~/claude/et-soc1-prototyping's form), as on the card day
except for these stand-ins (E191's real-path test's form, tools/claims-v3/e191/desk/realpath_e191.py, unchanged beside it):
  - the hostname: aifoundry2, from a private UTS namespace (desk/realpath_e194.sh starts this driver under bubblewrap with --hostname
    aifoundry2, a private PID namespace and its own /proc; outside it, W/nodev.sh: no /dev/et*, an empty /run/lock); the second namespace,
    --hostname aifoundry1, is the wrong-box case;
  - the telemetry reader behind E194's REAL guard: build/ettelem-hpl/ettelem is a script that runs fake_card_e194.py (config, sample) under
    the name ettelem (so ps reads the sampler's comm as the real reader's and the per-pass count of our device processes must skip it by
    pid); the runner's pin for it is set to the stand-in's sha256 in this process;
  - et-who: a script first on PATH that runs fake_card_e194.py etwho, which reads who holds the stand-in nodes and lock from /proc;
  - the two hosts: build/e194ledger/host/ledger_host and build/e194spp/host/sparseparity_host are scripts (the names the runner runs) that run
    fake_card_e194.py host-ledger / host-spp; their build records (BUILD-e194.json, today's, builder build_e194.sh, box aifoundry2, the kernel
    gate's line) carry their sha256; the kernels are stand-in files the records name;
  - card 0's lock: a writable stand-in file (the runner's lock path set to it in this process); the card's nodes: a stand-in directory
    (e194_ident.DEV_DIR set to it in this process).
Everything else is the real path: the box check (the hostname, ET_DEVICES and V3_DEVICE unset, the reader at its pin, today's build records
and the hosts and kernels at their sha256), the lock (open, flock -n), the holders (et-who through `timeout 20`, the real `ps` read of other
users' and our own device processes, the start's re-read of a stray reader), the start config through E194's real guard under `timeout 10`
(its hostname and ET_DEVICES rules) with its stderr kept, THE IDENTITY GATE (a) and (b), the sampler through the real guard, the stop-path
test (four lines and the clock rule's read), the ramped smoke and the passes with each host under the real `timeout 10` and watched, THE
HOST'S LINE read from the whole stdout, THE CLOCK RULE after each pass with the REGISTERED climb (1.5 s), the runner's bound, the closing
config, the manifest. Timing: the short sequence with short idles; the doubles at half their time in the cases that read the clock (so each
burst outlasts the 1.5 s climb), a tenth elsewhere (the namespace's fields are set here; run_e194.py's main() refuses them without --dry).

    python3 -B tools/claims-v3/e194/desk/realpath_e194.py <scratch dir> aifoundry2|aifoundry1    (desk/realpath_e194.sh runs both)

Cases, hostname aifoundry2 (verdicts stated first):
  RP1  THE WHOLE REAL PATH: rc 0, no DRY line, the box check, identity (a) and (b) on card 0's forms, the stop-path test (four lines, the
       clock rule read), the smoke (every device-opening host on card 0), six passes reading PASS with THE CLOCK RULE ok on each (the
       registered 1.5 s climb), the closing config, the manifest; every command the real one with ET_DEVICES and V3_DEVICE unset; the
       sampler's process named ettelem, skipped by pid in every per-pass count;
  RP2  card 0's lock held by another process: 16, no config read;  RP3 a device process of ours already running (stray_host) that stays: the
       start's re-reads (3) still see it: 16, no config read;
  RP4  the reader not at its pin: 16, nothing started;  RP5 a build record not build_e194.sh's: 16;  RP6 a build record made on another box: 16;
  RP7  the reader's config names A SECOND CARD (card 1's block, through the real guard): IDENTITY GATE FAILED, 16, no sampler;
  RP8  THE GUARD: ET_DEVICES=0, ET_DEVICES=1 or V3_DEVICE=1 set: refused (97, the reader never started); unset: passes, card 0's block; a
       session whose environment carries ET_DEVICES=0, and one whose carries V3_DEVICE=1 (fix-e194, verify-e194's nit 5: the runner's
       own environment, no patched module): the box check, 16, nothing started;
  RP9  the sampler holds a second card's node: identity (b), 16, no host;
  RP10 another login on card 0: 16, no config read;  RP11 ours on a second card's node: 16, no config read;
  RP12 a host names and holds a second card in the smoke: the watch, the smoke gate fails at the first device-opening host, 16;
  RP13 a host that hangs (honouring SIGTERM) in pass 1: the real `timeout 10` ends it (rc 124 at about 10 s), FAILED RUN, the queue goes on;
  RP14 a host that ignores SIGTERM past the runner's bound (12 s here): BOUND, nothing killed, the queue stops; card 0's lock HELD while it
       runs, the closing read after its end;
  RP15 a quiet sampler: stopped and restarted through the guard; every host on a live sample;
  RP16 a process of ours holding a second card's ops node from pass 1 on: STOP before pass 2;  RP17 another login on card 0 from et-who's
       4th call: STOP before pass 2;  RP18 et-who refused before the first card command: no device opened;  RP19 et-who refused from its
       4th call: STOP before pass 2;  RP20 a stray sparseparity_host of ours (ps: 'sparseparity_ho') that stays: refused after the re-reads;
  RP21 the stop file written while pass 1's host runs: no further pass, the closing read, the manifest, rc 0;
  RP22 a kernel changed after its build record: 16;  RP23 a record without the kernel gate's line: 16;  RP24 the reader printing lines
       without board_w: restarted, the passes flagged by their gaps;  RP25 the stop file at the start config read: an early stop at the gate.
E194's own cases on the real path (KIT.md section 4):
  RC1  THE CLOCK RULE: a pass whose clock steps to 700 MHz after its climb is SET ASIDE ("the clock: ... [700] MHz, not 800"), the session
       goes on;  RC2 a second such pass, in another configuration: "STOP: a second pass off 800 MHz after its climb", the queue ends, the
       closing read, rc 0;  RC3 a governor that climbs late (2.0 s, past the 1.5 s allowance): set aside the same way;
  RH1  THE HOST'S LINE split by a runtime line ("Opening device 0" between the ledger host's two parts, as aifoundry1's runtime split E191's
       smoke) in the smoke and in a pass: the smoke reads ok and the pass PASS, each smoke.json / run.json "host_line" reassembled with the
       one span recorded, host-stdout.txt the raw bytes kept, host-raw.json the object as read;  RH2 split by a line no lab box printed:
       fix-e194 (verify-e194's finding 2): that pass reads 'none', a FAILED RUN, the span named, the raw bytes kept, the session goes on;  RH3 THE REAL BYTES (CONTEXT section 116's lesson): the smoke's
       device-opening host replays, verbatim, E191's committed smoke stdout from aifoundry1's card (1a4bc1e3,
       session/smoke/copy-64m-random/stdout.txt, at its SHA256SUMS sha256: the ledger host's line split by "Opening device 1"): the real
       path reads status PASS, the smoke gate passes, smoke.json's host_line 'reassembled' with the one span "Opening device 1" dropped as
       a runtime line seen before, the kept stdout.txt byte for byte the committed file, and the session runs its six passes;
  RT1  THE HOLDER RE-READ: et-who shows a stray reader of ours on /dev/et0_mgmt at the first read only: read again with the lock held, then
       the session runs, rc 0;  RT2 a stand-in `ettelem` of ours (our live collector's read in flight) that ends 1.5 s into the start: the
       re-read sees it gone, rc 0;  RT3 the stray reader stays: refused after 3 re-reads, 16, no config read.
Hostname aifoundry1 (the second namespace):
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
REL_E = "tools/claims-v3/e194"


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
    import check_e194 as H
    for rel in list(H.FILES) + [REL_E + "/harness-e194.json"]:
        dst = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, rel), dst)
    fake = os.path.join(tree, REL_E, "fake_card_e194.py")
    b = os.path.join(S, "bin")
    os.makedirs(b, exist_ok=True)
    os.symlink("/usr/bin/python3", os.path.join(b, "ettelem"))         # nit 7: the stand-in reader runs under the reader's own name
    for rel, words, interp in (("build/ettelem-hpl/ettelem", "", os.path.join(b, "ettelem")),
                               ("build/e194ledger/host/ledger_host", " host-ledger", "/usr/bin/python3"),
                               ("build/e194spp/host/sparseparity_host", " host-spp", "/usr/bin/python3")):
        p = os.path.join(tree, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(f'#!/bin/sh\n[ -n "$REALPATH_MARK" ] && echo "$0 $*" >> "$REALPATH_MARK"\nexec "{interp}" -B "{fake}"{words} "$@"\n')
        os.chmod(p, 0o755)
    for rel, text in (("build/e194ledger/kernel/ledger.elf", "E194 real-path stand-in kernel: ledger\n"),
                      ("build/e194spp/kernel/sparseparity.elf", "E194 real-path stand-in kernel: sparse parity\n")):
        os.makedirs(os.path.dirname(os.path.join(tree, rel)), exist_ok=True)
        open(os.path.join(tree, rel), "w").write(text)
    with open(os.path.join(b, "et-who"), "w") as f:
        f.write(f'#!/bin/sh\nexec /usr/bin/python3 -B "{fake}" etwho\n')
    os.chmod(os.path.join(b, "et-who"), 0o755)
    shutil.copy2("/usr/bin/sleep", os.path.join(b, "stray_host"))      # a stand-in device process of ours (its name ends _host)
    dev = os.path.join(S, "dev")
    os.makedirs(dev, exist_ok=True)
    lock = os.path.join(S, "lock", "etsoc-shire0.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    open(lock, "a").close()
    return tree, b, os.path.realpath(dev), lock


def records(tree, day, builder="build_e194.sh", box="aifoundry2", kgate=True):
    etd = "not a gate on aifoundry2 (E194 runs on aifoundry2's one card, ET_DEVICES unset): no: the host has no ET_DEVICES (the stand-in)"
    for prog, d, host, elf in (("ledger", "build/e194ledger", "host/ledger_host", "kernel/ledger.elf"),
                               ("spp", "build/e194spp", "host/sparseparity_host", "kernel/sparseparity.elf")):
        rec = {"builder": builder, "box": box, "day": day, "epoch": int(time.time()), "verdict": "BUILT", "why": "",
               "host": f"{d}/{host}", "host_sha256": sha256(os.path.join(tree, d, host)), "kernel": f"{d}/{elf}",
               "kernel_sha256": sha256(os.path.join(tree, d, elf)), "et_devices": etd,
               # build_e194.sh writes the kernel gate's own line; the box check reads it (E191's fix-e191k2, nit 5)
               "kernel_gate": (f"KERNEL OK {prog}: (the real-path desk test's stand-in record)" if kgate else "not read"),
               "what": "the real-path desk test's stand-in record (a stand-in host)"}
        with open(os.path.join(tree, d, "BUILD-e194.json"), "w") as f:
            json.dump(rec, f, indent=1)


def session(S, tree, name, env=None, seq="short", host_bound_s=None, scale="0.1"):
    """One real-path session in this process: returns (rc, log, out dir, queue). THE CLOCK RULE's climb is the registered 1.5 s."""
    import run_e194 as R
    C, I = R.C, R.I
    out = os.path.join(S, name)
    os.makedirs(out, exist_ok=True)
    for k in [k for k in os.environ if k.startswith("E194_FAKE_") or k == "REALPATH_MARK"]:
        del os.environ[k]
    os.environ.update({"E194_FAKE_DEVDIR": I.DEV_DIR, "E194_FAKE_LOCK": C.LOCK, "E194_FAKE_SCHED": os.path.join(out, "sched.jsonl"),
                       "E194_FAKE_SCALE": scale, "REALPATH_MARK": os.path.join(out, "started.txt")})
    os.environ.update(env or {})
    open(os.environ["E194_FAKE_SCHED"], "a").close()
    a = argparse.Namespace(what="session", t0=int(time.time()), out=out, programs="ledger,spp", deadline_epoch=0, rapl_allowed=False,
                           dry=False, double="inject", sequence=seq, idle_before=0.5, idle_after=0.5, anchor_s=0.5, die_wait_s=3.0,
                           cap_pass_s=C.CAP_PASS_START_S, cap_end_s=C.CAP_S, host_bound_s=host_bound_s or C.HOST_BOUND_S, climb_s=C.CLIMB_S)
    rc = R.Session(a).run()
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
    print(f"   [{name}] rc {rc}; " + " | ".join(ln[24:200] for ln in log.splitlines()
                                                 if any(w in ln for w in ("STOP", "gate", "no device opened", "BOUND", "box check",
                                                                          "IDENTITY", "smoke gate", "SET ASIDE", "stray"))), flush=True)
    return rc, log, out, q


def started(out):
    """The stand-in reader's and hosts' starts in this session (each script appends its own command line)."""
    p = os.path.join(out, "started.txt")
    return open(p).read().splitlines() if os.path.exists(p) else []


def guard_call(tree, env_extra, unset=False):
    e = {k: v for k, v in os.environ.items() if not k.startswith("E194_FAKE_")}     # the doubles' plain modes (card 0's block)
    e.pop("ET_DEVICES", None)
    e.pop("V3_DEVICE", None)
    mark = os.path.join(tree, "..", "guard-mark.txt")
    if os.path.exists(mark):
        os.remove(mark)
    e["REALPATH_MARK"] = mark
    e.update(env_extra)
    r = subprocess.run(["timeout", "10", "bash", os.path.join(tree, REL_E, "ettelem_guard_e194.sh"), "config"], cwd=tree, env=e,
                       capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout, r.stderr, os.path.exists(mark)


def run_cases(t, S, host_want):
    tree, b, dev, lock = make_tree(S)
    sys.path.insert(0, os.path.join(tree, REL_E))
    import run_e194 as R
    C, I = R.C, R.I
    host = socket.gethostname()
    print(f"realpath_e194: hostname {host!r} (the namespace's); the runner is the stand-in tree's: "
          f"{R.__file__ == os.path.join(tree, REL_E, 'run_e194.py')}", flush=True)
    if host != host_want:
        t.case(f"host-{host_want}", False, f"the namespace's hostname is {host!r}, not {host_want!r}: run under desk/realpath_e194.sh")
        return
    registered_pin = C.READER_SHA256
    C.READER_SHA256 = sha256(os.path.join(tree, C.READER))
    C.LOCK = lock
    I.DEV_DIR = dev
    os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    day = R.pacific_day()
    records(tree, day)
    if host_want == "aifoundry1":
        rc, log, out, q = session(S, tree, "RW1")
        grc, gout, gerr, gm = guard_call(tree, {})
        t.case("RW1", rc == 16 and "the box check: this host is 'aifoundry1', not aifoundry2" in log and "no device opened" in log
               and not os.path.exists(os.path.join(out, "config-start.json")) and grc == 97 and "box 'aifoundry1'" in gerr and not gm,
               f"rc {rc}; the guard rc {grc} ('{gerr.strip()[:90]}'), the reader started {gm}")
        return
    # ---- RP1: the whole real path (the sampler's process name read while it runs; THE CLOCK RULE on each pass, the registered climb)
    comms = {}

    def watch_comm(out):
        L = os.path.join(out, "session.log")
        t = time.time()
        while time.time() - t < 180 and not os.path.exists(os.path.join(out, "MANIFEST.sha256")):
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
    rc, log, out, q = session(S, tree, "RP1", scale="0.5")
    th.join(timeout=10)
    print(f"   RP1: the sampler's process name(s) while it ran: {sorted(set(comms.values()))}")
    idn = json.load(open(os.path.join(out, "identity.json"))) if os.path.exists(os.path.join(out, "identity.json")) else {}
    cmds = [json.loads(ln) for ln in open(os.path.join(out, "commands.jsonl"))] if os.path.exists(os.path.join(out, "commands.jsonl")) else []
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    clk = [json.load(open(os.path.join(out, "passes", x["pass"], "run.json"))).get("clock_rule", {}) for x in ran]
    t.case("RP1", rc == 0 and "DRY" not in log and "the box check: aifoundry2, ET_DEVICES and V3_DEVICE unset" in log
           and "identity (a): /dev/et0_mgmt, device ID 0, minion_mv between 450 and 600" in log and "identity (b): et-who with the sampler running" in log
           and "stop-path test passed" in log and "the clock rule read the live samples" in log and "smoke gate passed" in log and len(ran) == 6
           and all(x.get("reading") == "PASS" and x.get("clock") == "ok" for x in ran) and all(c.get("n", 0) >= 1 and c.get("climb_s") == 1.5 for c in clk)
           and q.get("identity_ok") is True and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et0_mgmt"]
           and all(v["right"] and not v["wrong"] for k, v in idn.get("smoke", {}).items() if k != "ledger-selftest")
           and "config end:" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
           and cmds and all(c["real"] == c["used"] and c["et_devices"] is None and c.get("v3_device") is None for c in cmds)
           and any(c["used"][:4] == ["timeout", "10", "bash", C.GUARD] for c in cmds)
           and comms and set(comms.values()) == {"ettelem"},
           f"rc {rc}; passes {[(x.get('reading'), x.get('clock')) for x in ran]}; clock samples read {[c.get('n') for c in clk]} (climb "
           f"{clk[0].get('climb_s') if clk else None} s); identity {idn.get('config_start')}, the sampler "
           f"{idn.get('sampler_nodes', {}).get('nodes')} named {sorted(set(comms.values()))}; {len(cmds)} commands, each the real one, "
           f"ET_DEVICES and V3_DEVICE unset")
    # ---- RP2: the lock held
    holder = subprocess.Popen(["flock", "-o", lock, "sleep", "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.5)
    rc, log, out, q = session(S, tree, "RP2")
    holder.terminate()
    holder.wait()
    t.case("RP2", rc == 16 and "card 0's lock is held: no device opened" in log and not os.path.exists(os.path.join(out, "config-start.json")),
           f"rc {rc}")
    # ---- RP3: a device process of ours that stays (the re-reads still see it)
    dp = subprocess.Popen([os.path.join(b, "stray_host"), "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.3)
    rc, log, out, q = session(S, tree, "RP3")
    dp.terminate()
    dp.wait()
    rr = q.get("holder_reads_at_start") or []
    t.case("RP3", rc == 16 and "device process(es) of ours besides the sampler" in log and "no device opened" in log and len(rr) == 4
           and not os.path.exists(os.path.join(out, "config-start.json")), f"rc {rc}; the holder rule read {len(rr)} times with the lock held")
    # ---- RP4: the reader off its pin
    C.READER_SHA256 = registered_pin
    rc, log, out, q = session(S, tree, "RP4")
    C.READER_SHA256 = sha256(os.path.join(tree, C.READER))
    t.case("RP4", rc == 16 and "not at its pin" in log and "no device opened" in log and not started(out)
           and not os.path.exists(os.path.join(out, "etwho-before.txt")), f"rc {rc}; nothing started {not started(out)}")
    # ---- RP5, RP6: the build records
    records(tree, day, builder="build_e191.sh")
    rc5, log5, out5, _ = session(S, tree, "RP5")
    records(tree, day, box="aifoundry1")
    rc6, log6, out6, _ = session(S, tree, "RP6")
    records(tree, day)
    t.case("RP5", rc5 == 16 and "build record is not build_e194.sh's BUILT of today" in log5 and not started(out5), f"rc {rc5}")
    t.case("RP6", rc6 == 16 and "build record was not made on aifoundry2" in log6 and not started(out6), f"rc {rc6}")
    # ---- RP7: the config names a second card
    rc, log, out, q = session(S, tree, "RP7", {"E194_FAKE_CONFIG": "card1"})
    st = started(out)
    t.case("RP7", rc == 16 and "IDENTITY GATE FAILED: PCIe target /dev/et1_mgmt, not /dev/et0_mgmt alone" in log and "sampler started" not in log
           and not any("host" in x for x in st) and os.path.exists(os.path.join(out, "config-start.err")),
           f"rc {rc}; started {[x.split()[0].rsplit('/', 1)[-1] + ' ' + x.split()[1] for x in st]}")
    # ---- RP8: ET_DEVICES, V3_DEVICE and the real guard
    g_zero = guard_call(tree, {"ET_DEVICES": "0"})
    g_one = guard_call(tree, {"ET_DEVICES": "1"})
    g_v3 = guard_call(tree, {"V3_DEVICE": "1"})
    g_unset = guard_call(tree, {})
    rc, log, out, q = session(S, tree, "RP8", {"ET_DEVICES": "0"})     # fix-e194 (nit 5): the runner's own environment, no patch
    os.environ.pop("ET_DEVICES", None)
    rcv, logv, outv, _ = session(S, tree, "RP8v", {"V3_DEVICE": "1"})
    os.environ.pop("V3_DEVICE", None)
    print(f"   the guard: ET_DEVICES=0 rc {g_zero[0]} ('{g_zero[2].strip()[:80]}'), reader started {g_zero[3]}; =1 rc {g_one[0]}, started "
          f"{g_one[3]}; V3_DEVICE=1 rc {g_v3[0]}, started {g_v3[3]}; unset rc {g_unset[0]} ({'card 0' if '/dev/et0_mgmt' in g_unset[2] else 'no card 0 block'}), "
          f"started {g_unset[3]}")
    t.case("RP8", g_zero[0] == 97 and "ET_DEVICES is set" in g_zero[2] and not g_zero[3] and g_one[0] == 97 and not g_one[3]
           and g_v3[0] == 97 and "V3_DEVICE is set" in g_v3[2] and not g_v3[3] and g_unset[0] == 0 and "/dev/et0_mgmt" in g_unset[2] and g_unset[3]
           and rc == 16 and "ET_DEVICES or V3_DEVICE is set in the session's environment" in log and not started(out)
           and rcv == 16 and "ET_DEVICES or V3_DEVICE is set in the session's environment" in logv and not started(outv),
           f"the guard refused ET_DEVICES=0, =1 and V3_DEVICE=1 (97, no reader started), passed unset; the session with ET_DEVICES=0 in "
           f"the runner's environment rc {rc}, with V3_DEVICE=1 rc {rcv}, nothing started")
    # ---- RP9: the sampler on a second card
    rc, log, out, q = session(S, tree, "RP9", {"E194_FAKE_SAMPLER": "card1"})
    t.case("RP9", rc == 16 and "identity (b): IDENTITY GATE FAILED" in log and not any("host" in x for x in started(out)), f"rc {rc}")
    # ---- RP10, RP11: holders
    rc10, log10, out10, _ = session(S, tree, "RP10", {"E194_FAKE_ETWHO": "other"})
    rc11, log11, out11, _ = session(S, tree, "RP11", {"E194_FAKE_ETWHO": "ours1"})
    t.case("RP10", rc10 == 16 and "holder line(s) of another login" in log10 and not os.path.exists(os.path.join(out10, "config-start.json")),
           f"rc {rc10}")
    t.case("RP11", rc11 == 16 and "holder line(s) of ours off card 0" in log11 and not os.path.exists(os.path.join(out11, "config-start.json")),
           f"rc {rc11}")
    # ---- RP12: a host on a second card in the smoke
    rc, log, out, q = session(S, tree, "RP12", {"E194_FAKE_HOST": "card1"})
    sm = sorted(os.listdir(os.path.join(out, "smoke"))) if os.path.isdir(os.path.join(out, "smoke")) else []
    t.case("RP12", rc == 16 and "smoke gate failed: copy-64m-random: the host's card: ANOTHER CARD" in log and sm == ["copy-64m-random", "ledger-selftest"],
           f"rc {rc}; smoke processes {sm}")
    # ---- RP13: a host that hangs, honouring SIGTERM: the real timeout 10
    rc, log, out, q = session(S, tree, "RP13", {"E194_FAKE_HOST": "hang", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1",
                                                 "E194_FAKE_WEDGE_S": "25"})
    rjp = os.path.join(out, "passes", "copy-zeros", "p1", "run.json")
    rjd = json.load(open(rjp)) if os.path.exists(rjp) else {}
    dur = ((rjd.get("host_t1_ms") or 0) - (rjd.get("host_t0_ms") or 0)) / 1000.0
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP13", rc == 0 and rjd.get("host_rc") == 124 and 9.5 <= dur <= 12.5 and len(ran) == 6 and ran[0].get("reading", "").startswith("FAILED RUN")
           and "BOUND" not in log, f"rc {rc}; pass 1's host rc {rjd.get('host_rc')} after {dur:.2f} s (the real timeout 10); passes {len(ran)}")
    # ---- RP14: a host that ignores SIGTERM: the runner's bound; card 0's lock held while it runs
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
    rc, log, out, q = session(S, tree, "RP14", {"E194_FAKE_HOST": "wedge", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1",
                                                 "E194_FAKE_WEDGE_S": "16"}, host_bound_s=12)
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
           f"card 0's lock read rc {held.get('flock_rc')} (1 = held); the closing read after its end; alive when the session returned: {bool(alive)}")
    # ---- RP15-RP21: E191's verifier's cases on this card
    rc, log, out, q = session(S, tree, "RP15", {"E194_FAKE_SAMPLER": "hangs:9"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    ages = [json.load(open(os.path.join(out, "passes", x["pass"], "run.json"))).get("sample_age_s_at_host_start") for x in ran]
    t.case("RP15", rc == 0 and "the sampler is not live (alive True" in log and "restarting it" in log and len(ran) >= 5
           and all(a is not None and a < 2.0 for a in ages), f"rc {rc}; passes {len(ran)}; the last sample's age at each host start {ages}")
    hold = {}

    def hold_card1(out):
        L = os.path.join(out, "session.log")
        t = time.time()
        while time.time() - t < 60:
            if os.path.exists(L) and "pass 1: copy-zeros p1 (K" in open(L).read():
                hold["p"] = subprocess.Popen(["/usr/bin/python3", "-I", "-B", "-c", f"import time; f = open({os.path.join(dev, 'et1_ops')!r}, 'a'); "
                                              "time.sleep(40)"], stdin=subprocess.DEVNULL)
                return
            time.sleep(0.05)
    th = threading.Thread(target=hold_card1, args=(os.path.join(S, "RP16"),), daemon=True)
    th.start()
    rc, log, out, q = session(S, tree, "RP16")
    th.join(timeout=10)
    if hold.get("p"):
        hold["p"].terminate()
        hold["p"].wait()
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP16", rc == 0 and len(ran) == 1 and "STOP before pass 2:" in log and "holder line(s) of ours off card 0" in log
           and "config end:" in log, f"rc {rc}; passes {len(ran)}")
    rc, log, out, q = session(S, tree, "RP17", {"E194_FAKE_ETWHO": "other", "E194_FAKE_ETWHO_FROM": "4"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    t.case("RP17", rc == 0 and len(ran) == 1 and "STOP before pass 2:" in log and "holder line(s) of another login" in log,
           f"rc {rc}; passes {len(ran)}")
    rc, log, out, q = session(S, tree, "RP18", {"E194_FAKE_ETWHO": "fail"})
    t.case("RP18", rc == 16 and "et-who unreadable (rc 1, nothing on its stdout)" in log and "no device opened" in log
           and not os.path.exists(os.path.join(out, "config-start.json")) and not started(out), f"rc {rc}; nothing started {not started(out)}")
    rc, log, out, q = session(S, tree, "RP19", {"E194_FAKE_ETWHO": "fail", "E194_FAKE_ETWHO_FROM": "4"})
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
    # ---- RP22-RP25: E191's second verifier's cases on this card
    sk = os.path.join(tree, "build/e194spp/kernel/sparseparity.elf")
    keep = open(sk, "rb").read()
    with open(sk, "ab") as f:
        f.write(b"one byte more after the build\n")
    rc, log, out, q = session(S, tree, "RP22")
    with open(sk, "wb") as f:
        f.write(keep)
    t.case("RP22", rc == 16 and "spp's kernel is not the one its build record names" in log and "no device opened" in log and not started(out)
           and not os.path.exists(os.path.join(out, "etwho-before.txt")), f"rc {rc}; nothing started {not started(out)}")
    records(tree, day, kgate=False)
    rc, log, out, q = session(S, tree, "RP23")
    records(tree, day)
    t.case("RP23", rc == 16 and "build record carries no passing kernel gate line" in log and "no device opened" in log and not started(out), f"rc {rc}")
    rc, log, out, q = session(S, tree, "RP24", {"E194_FAKE_SAMPLER": "noboard:9"})
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
           f"rc {rc}; lines without board_w {q.get('sampler_lines_not_live')}; (pass, age, largest gap, flagged, sampler_live) {rows}")
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
           f"rc {rc}; an early stop at the gate, never 'stop-path test failed'")
    # ---- RC1-RC3: THE CLOCK RULE on the real path (the registered 1.5 s climb; the doubles at half their time)
    inj = os.path.join(S, "inject-rc1.json")
    json.dump([{"during": "busy", "burst_after_s": 1.7, "mhz": 700, "count": 3}], open(inj, "w"))
    rc, log, out, q = session(S, tree, "RC1", {"E194_FAKE_INJECT": inj}, scale="0.5")
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    sa = [x for x in ran if str(x.get("set_aside") or "").startswith("the clock:")]
    t.case("RC1", rc == 0 and len(ran) == 6 and len(sa) == 1 and "[700] MHz, not 800" in (sa[0].get("set_aside") or "") and "STOP" not in log
           and q.get("off_clock_passes") == [sa[0]["pass"]], f"rc {rc}; passes {len(ran)}; set aside by the clock {[(x['pass'], x['set_aside'][:80]) for x in sa]}")
    inj2 = os.path.join(S, "inject-rc2.json")
    json.dump([{"during": "busy", "burst_after_s": 1.7, "mhz": 700, "count": 40}], open(inj2, "w"))
    rc, log, out, q = session(S, tree, "RC2", {"E194_FAKE_INJECT": inj2}, scale="0.5")
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    sa = [x for x in ran if str(x.get("set_aside") or "").startswith("the clock:")]
    t.case("RC2", rc == 0 and len(sa) == 2 and len(ran) == 2 and "STOP: a second pass off 800 MHz after its climb" in log and "config end: TDP" in log
           and os.path.exists(os.path.join(out, "MANIFEST.sha256")), f"rc {rc}; passes {[x['pass'] for x in ran]}, both set aside by the clock; the queue stopped")
    rc, log, out, q = session(S, tree, "RC3", {"E194_FAKE_CLIMB_S": "2.0"}, scale="0.5")
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    sa = [x for x in ran if str(x.get("set_aside") or "").startswith("the clock:")]
    t.case("RC3", rc == 0 and len(sa) == 2 and "STOP: a second pass off 800 MHz after its climb" in log and "600" in (sa[0].get("set_aside") or ""),
           f"rc {rc}; a governor climbing at 2.0 s: {[(x['pass'], x['set_aside'][:70]) for x in sa]}")
    # ---- RH1, RH2: THE HOST'S LINE split by a runtime line, in the smoke and in a pass
    rc, log, out, q = session(S, tree, "RH1", {"E194_FAKE_HOST": "split"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    sj = json.load(open(os.path.join(out, "smoke", "copy-64m-random", "smoke.json"))) if os.path.exists(os.path.join(out, "smoke", "copy-64m-random", "smoke.json")) else {}
    rjc = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "run.json"))) if ran else {}
    raw = open(os.path.join(out, "passes", "copy-zeros", "p1", "host-stdout.txt")).read() if ran else ""
    hr = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "host-raw.json"))) if ran else {}
    t.case("RH1", rc == 0 and "smoke gate passed" in log and (sj.get("host_line") or {}).get("dropped") == ["Opening device 0"] and sj.get("good") is True
           and len(ran) == 6 and all(x.get("reading") == "PASS" for x in ran) and (rjc.get("host_line") or {}).get("method") == "reassembled"
           and "Opening device 0\n" in raw and hr.get("status") == "PASS" and hr.get("launches") == 8,
           f"rc {rc}; the smoke's line {sj.get('host_line')}; pass 1's {rjc.get('host_line')}; the raw stdout kept ({len(raw)} B); host-raw.json "
           f"status {hr.get('status')}, launches {hr.get('launches')}")
    rc, log, out, q = session(S, tree, "RH2", {"E194_FAKE_HOST": "splitjunk", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    hl2 = (json.load(open(os.path.join(out, "passes", ran[0]["pass"], "run.json"))).get("host_line") or {}) if ran else {}
    raw2 = open(os.path.join(out, "passes", ran[0]["pass"], "host-stdout.txt")).read() if ran else ""
    t.case("RH2", rc == 0 and len(ran) == 6 and ran[0].get("reading") == "FAILED RUN (not a datum)" and hl2.get("method") == "none"
           and "not a whole known runtime line" in (hl2.get("why") or "") and "a runtime line no lab box printed\n" in raw2
           and all(x.get("reading") == "PASS" for x in ran[1:]),
           f"rc {rc}; pass 1 read {ran[0].get('reading') if ran else None} ({hl2.get('method')}: {str(hl2.get('why'))[:90]}); the raw stdout kept; "
           f"the other passes {[x.get('reading') for x in ran[1:]]}")
    # ---- RH3: THE REAL BYTES: E191's committed smoke stdout (aifoundry1's card; its runtime split the ledger host's line), replayed
    rel = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1"
    real = os.path.join(REPO, rel, "session", "smoke", "copy-64m-random", "stdout.txt")
    listed = [ln.split("  ", 1)[0] for ln in open(os.path.join(REPO, rel, "SHA256SUMS"))
              if ln.rstrip("\n").endswith("  session/smoke/copy-64m-random/stdout.txt")]
    rb = open(real, "rb").read()
    at_sum = listed == [hashlib.sha256(rb).hexdigest()]
    rc, log, out, q = session(S, tree, "RH3", {"E194_FAKE_HOST": "replay", "E194_FAKE_HOST_FILE": real, "E194_FAKE_HOST_FROM": "1",
                                               "E194_FAKE_HOST_COUNT": "1"})
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    sp = os.path.join(out, "smoke", "copy-64m-random")
    sj = json.load(open(os.path.join(sp, "smoke.json"))) if os.path.exists(os.path.join(sp, "smoke.json")) else {}
    kept = open(os.path.join(sp, "stdout.txt"), "rb").read() if os.path.exists(os.path.join(sp, "stdout.txt")) else b""
    hl = sj.get("host_line") or {}
    t.case("RH3", at_sum and b"Opening device 1\n" in rb and rc == 0 and "smoke gate passed" in log and sj.get("good") is True
           and sj.get("status") == "PASS" and hl.get("method") == "reassembled" and hl.get("dropped") == ["Opening device 1"]
           and hl.get("runtime") == [True] and kept == rb and len(ran) == 6 and all(x.get("reading") == "PASS" for x in ran),
           f"rc {rc}; the committed bytes ({len(rb)} B) at their SHA256SUMS sha256: {at_sum}; the smoke read status {sj.get('status')}, "
           f"good {sj.get('good')}; its host_line {hl}; stdout.txt kept byte for byte: {kept == rb}; passes {len(ran)}")
    # ---- RT1-RT3: THE HOLDER RE-READ at the start (the lock held)
    rc, log, out, q = session(S, tree, "RT1", {"E194_FAKE_ETWHO": "mgmt", "E194_FAKE_ETWHO_UNTIL": "2"})
    rr = q.get("holder_reads_at_start") or []
    t.case("RT1", rc == 0 and len(rr) == 2 and rr[0].get("transient") is True and not rr[1].get("why") and "read again in 2 s (1 of 3)" in log
           and "smoke gate passed" in log, f"rc {rc}; the start's reads {[(x.get('why') or 'clear')[:60] for x in rr]}")
    os.makedirs(os.path.join(S, "collector"), exist_ok=True)
    shutil.copy2("/usr/bin/sleep", os.path.join(S, "collector", "ettelem"))
    dp = subprocess.Popen([os.path.join(S, "collector", "ettelem"), "1.5"], stdin=subprocess.DEVNULL)
    reaper = threading.Thread(target=dp.wait, daemon=True)     # reaped at once, as our live collector reaps its reads (never a zombie)
    reaper.start()
    time.sleep(0.1)
    rc, log, out, q = session(S, tree, "RT2")
    reaper.join(timeout=10)
    rr = q.get("holder_reads_at_start") or []
    t.case("RT2", rc == 0 and len(rr) >= 2 and "device process(es) of ours besides the sampler" in (rr[0].get("why") or "") and not rr[-1].get("why")
           and "smoke gate passed" in log, f"rc {rc}; a stand-in ettelem of ours (1.5 s): the start's reads {[(x.get('why') or 'clear')[:60] for x in rr]}")
    rc, log, out, q = session(S, tree, "RT3", {"E194_FAKE_ETWHO": "mgmt"})
    rr = q.get("holder_reads_at_start") or []
    t.case("RT3", rc == 16 and len(rr) == 4 and "no device opened" in log and not os.path.exists(os.path.join(out, "config-start.json")),
           f"rc {rc}; the stray reader stayed: {len(rr)} reads, then refused")
    time.sleep(2)


def main(argv):
    if len(argv) != 2 or argv[1] not in ("aifoundry2", "aifoundry1"):
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
    print(f"realpath_e194 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}; processes visible: "
          f"{sum(1 for x in os.listdir('/proc') if x.isdigit())}", flush=True)
    run_cases(t, S, argv[1])
    print(f"REALPATH-E194 {argv[1]}: {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
