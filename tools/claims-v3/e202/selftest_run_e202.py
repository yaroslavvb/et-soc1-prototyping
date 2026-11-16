#!/usr/bin/env python3
"""E202's runner desk test on the doubles (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): run_e202.py --dry, every gate,
stop and branch the doubles can drive, and END TO END through the collection (collect_e202.py), the reducer (energy_reduce.py,
unchanged) and the frozen scorer (score_e202.py, unchanged). The real path (DRY unset, stand-ins at the tools' real paths) is
desk/realpath_e202.py's; this is the dry path step 8 runs on the box, and the runner's logic at desk speed.

    /usr/bin/python3 -I -B tools/claims-v3/e202/selftest_run_e202.py <scratch dir outside the repo>      (inside W/nodev.sh and a slot)

Prints each case PASS/FAIL with its evidence, and SELFTEST-RUN-E202 <n> of <m> PASS (or FAIL) last. The watts and seconds are the
frozen forecast's points driven through toy cards: desk checks of code, not measurements. SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import os
import pwd
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PY = sys.executable
RUNNER = os.path.join(HERE, "run_e202.py")
RES = []


def check(name, ok, detail=""):
    RES.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)


def session(S, name, knobs=None, args=None, double="inject", timeout=420, env_extra=None, fast=True, prep=()):
    out = os.path.join(S, name)
    for p in prep:                      # fix-e202: a file where the runner makes a folder (its crash cases, verify-e202's A2/A3 form)
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, p), "w").close()
    env = {k: v for k, v in os.environ.items() if not k.startswith("E202_")}
    env["E202_FAKE_SCALE"] = "0.2" if fast else "1"
    for k, v in (knobs or {}).items():
        if isinstance(v, (list, dict)):
            p = os.path.join(S, f"{name}-{k.lower()}.json")
            json.dump(v, open(p, "w"))
            env["E202_FAKE_" + k] = p
        else:
            env["E202_FAKE_" + k] = str(v)
    env.update(env_extra or {})
    a = [PY, "-B", RUNNER, "session", "--dry", "--double", double, "--t0", str(int(time.time())), "--out", out]
    if fast:
        a += ["--idle-before", "1", "--idle-after", "1", "--anchor-s", "1", "--die-wait-s", "5"]
    a += args or []
    t = time.time()
    r = subprocess.run(a, cwd=REPO, env=env, capture_output=True, text=True, timeout=timeout)
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    try:
        q = json.load(open(os.path.join(out, "queue.json")))
    except (OSError, ValueError):
        q = {}
    return r.returncode, log, q, out, round(time.time() - t, 1)


def ran(q):
    return [b["burst"] for b in q.get("bursts", []) if b.get("ran")]


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    for d in os.listdir("/dev"):
        if d.startswith("et") and not os.path.isfile(os.path.join("/dev", d)):
            print(f"REFUSED: /dev/{d} is a device here: run this inside W/nodev.sh")
            return 2
    os.makedirs(S, exist_ok=True)
    print(f"selftest_run_e202: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}, {PY} {sys.version.split()[0]}, scratch <S>", flush=True)
    r = subprocess.run([PY, "-B", os.path.join(HERE, "check_e202.py"), "--box"], cwd=REPO, capture_output=True, text=True)
    check("H0 the harness reads OK before the cases", r.stdout.startswith("HARNESS OK"), r.stdout.strip())

    # D0: the dry pass as step 8 runs it (the alt card, the short sequence)
    rc, log, q, out, dt = session(S, "D0-step8", args=["--sequence", "short"], double="alt")
    check("D0 the dry pass in step 8's form", rc == 0 and "smoke gate passed: T-scp and Z-scp" in log and len(ran(q)) == 4
          and ran(q) == ["trained-scp/b1", "random-scp/b1", "trained-dram/b1", "random-dram/b1"] and "DRY session end" in log
          and os.path.exists(os.path.join(out, "MANIFEST.sha256")) and all(ln.split(" ", 3)[3].startswith(("DRY", "session start"))
                                                                          for ln in log.splitlines() if ln.strip()),
          f"rc {rc}, bursts {ran(q)}, {dt} s, every line DRY")

    # the full registered order on the doubles (fast)
    rc, log, q, out, dt = session(S, "D1-plan")
    order = ran(q)
    want = ["trained-scp/b1", "random-scp/b1", "random-scp/b2", "trained-scp/b2", "trained-scp/b3", "random-scp/b3", "random-scp/b4",
            "trained-scp/b4", "trained-dram/b1", "random-dram/b1", "random-dram/b2", "trained-dram/b2"]
    bj = [json.load(open(os.path.join(out, "bursts", *b.split("/"), "burst.json"))) for b in order]
    check("D1 THE ORDER: T Z Z T T Z Z T scored, then T Z Z T dram REPORTED, R 96, order indices 1-12", rc == 0 and order == want
          and [b["order_index"] for b in bj] == list(range(1, 13)) and all(b["R"] == 96 for b in bj)
          and [b["label"] for b in bj] == ["scored"] * 8 + ["REPORTED"] * 4, f"rc {rc}, {len(order)} bursts, {dt} s")
    hr = json.load(open(os.path.join(out, "bursts", "trained-scp", "b1", "host-raw.json")))
    hj = json.load(open(os.path.join(out, "bursts", "trained-scp", "b1", "host.json")))
    check("D1 the burst's files: host-raw.json is the host's own --out record; host.json the adapter's", hr.get("mnistmlp") == 1
          and hr.get("passes") == 96 and hj["reps_done"] == 1 and hj["launch_epoch_ms"] == hr["launch_epoch_ms"]
          and hj["launch_s"] == [hr["wall_s"]] and all(os.path.exists(os.path.join(out, "bursts", "trained-scp", "b1", f))
                                                      for f in ("run.json", "burst.json", "telemetry.jsonl.gz", "stdout.txt", "host.err")),
          f"passes {hr.get('passes')}, reps_done {hj['reps_done']}")
    sm = json.load(open(os.path.join(out, "smoke", "ACC", "smoke.json")))
    check("D1 the smoke: five processes in the registered order, labels kept, ACC's accuracy recorded",
          [ln.split("smoke ")[1].split(":")[0] for ln in log.splitlines() if " smoke " in ln and ": rc " in ln] ==
          ["T-scp", "Z-scp", "T-dram", "Z-dram", "ACC"] and sm.get("accuracy") == {"correct": 9849, "scored": 10000}
          and os.path.exists(os.path.join(out, "smoke", "T-scp", "labels.bin")) and "--debug-logits" in
          json.load(open(os.path.join(out, "smoke", "T-scp", "smoke.json")))["argv"], "")
    check("D1 the closing: et-who read, then the closing config read", "config end: TDP 0 W" in log and q.get("closing_config") == "read"
          and os.path.exists(os.path.join(out, "config-end.json")), q.get("closing_config", ""))

    # gates before any device
    lp = os.path.join(S, "G1-lock")
    os.makedirs(lp, exist_ok=True)
    lf = open(os.path.join(lp, "dry.lock"), "a+")       # held by this test process itself (no child inherits it)
    fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
    rc, log, q, out, dt = session(S, "G1-lock")
    lf.close()
    check("G1 the lock held: refused, no device opened", rc == 2 and "refused, no device opened: card 0's lock is held" in log
          and not os.path.exists(os.path.join(out, "config-start.json")), f"rc {rc}")
    rc, log, q, out, dt = session(S, "G2-holder", knobs={"ETWHO": "held"})
    check("G2 a holder of another login: refused, no device opened", rc == 2 and "refused, no device opened: a holder" in log
          and not os.path.exists(os.path.join(out, "config-start.json")), f"rc {rc}")
    rc, log, q, out, dt = session(S, "G3-tdp5", knobs={"CONFIG": "tdp5"})
    check("G3 the start config off TDP 0 W: GATE-STOP, no sampler", rc == 3 and "GATE-STOP: config start" in log
          and "sampler started" not in log, f"rc {rc}")
    rc, log, q, out, dt = session(S, "G4-cutconfig", knobs={"CONFIG": "cut"})
    check("G4 a runtime line inside the config line: no reading, GATE-STOP", rc == 3 and "no JSON line" in log, f"rc {rc}")
    rc, log, q, out, dt = session(S, "G5-dead", knobs={"SAMPLER": "dead"}, timeout=200)
    check("G5 a dead sampler: six attempts, GATE-STOP, no launch", rc == 3 and "the sampler would not start" in log
          and not os.path.isdir(os.path.join(out, "smoke")), f"rc {rc}, {dt} s")

    # stops on live samples
    rc, log, q, out, dt = session(S, "S1-board", knobs={"INJECT": [{"board_w": 66.0, "during": "burst", "count": 1}]})
    b1 = json.load(open(os.path.join(out, "bursts", "trained-scp", "b1", "burst.json")))
    rj = json.load(open(os.path.join(out, "bursts", "trained-scp", "b1", "run.json")))
    check("S1 board 66 W in burst 1: STOP, the host finishes, its rest after runs whole, no burst after, the closing read",
          rc == 0 and ran(q) == ["trained-scp/b1"] and "board 66.0 W at or above 65 W" in (q.get("stop") or "")
          and rj["end_ms"] - rj["host_t1_ms"] >= 900 and any("a stop line tripped" in f for f in b1["flags"])
          and q.get("closing_config") == "read", f"bursts {ran(q)}, rest after {rj['end_ms'] - rj['host_t1_ms']} ms")
    rc, log, q, out, dt = session(S, "S2-die-smoke", knobs={"INJECT": [{"die": 70, "during": "smoke", "count": 1}]})
    check("S2 minshire[0] 70 C in the smoke: GATE-STOP (a stop during the smoke), no burst", rc == 3 and not ran(q)
          and "a stop line tripped during smoke" in log and "70 C" in (q.get("stop") or ""), f"rc {rc}, stop {q.get('stop')}")
    rc, log, q, out, dt = session(S, "S3-clock", knobs={"INJECT": [{"mhz": 700, "during": "smoke", "count": 1},
                                                                   {"mhz": 800, "during": "burst", "after_launches": 3, "count": 1}]})
    sa = q.get("set_aside") or {}
    check("S3 THE CLOCK: one sample off in the smoke (outside a burst: nothing set aside), a second in burst 3: set aside, STOP",
          rc == 0 and ran(q) == ["trained-scp/b1", "random-scp/b1", "random-scp/b2"] and list(sa) == ["random-scp/b2"]
          and "second sample off 600 MHz" in (q.get("stop") or "") and len(q.get("off_clock") or []) == 2,
          f"bursts {ran(q)}, set aside {list(sa)}, stop {q.get('stop')}")
    rc, log, q, out, dt = session(S, "S3b-clock-one", knobs={"INJECT": [{"mhz": 800, "during": "burst", "after_launches": 2, "count": 1}]})
    sa = q.get("set_aside") or {}
    b2 = json.load(open(os.path.join(out, "bursts", "random-scp", "b1", "burst.json")))
    check("S3b one sample off in burst 2 only: burst 2 set aside (burst.json), the session goes on", rc == 0 and len(ran(q)) == 12
          and list(sa) == ["random-scp/b1"] and b2["set_aside"] and not q.get("stop"), f"set aside {list(sa)}")
    rc, log, q, out, dt = session(S, "S4-quiet", knobs={"SAMPLER": "quiet-from:12"})
    check("S4 the sampler goes quiet: no line for 1 s, STOP; the closing read", rc in (0, 3) and "no telemetry line for" in
          (q.get("stop") or "") and q.get("closing_config") == "read", f"rc {rc}, stop {q.get('stop')}, bursts {len(ran(q))}")
    rc, log, q, out, dt = session(S, "S5-old", knobs={"SAMPLER": "old-from:12"})
    check("S5 lines 1.5 s old at their arrival: STOP", rc in (0, 3) and "s old at its arrival" in (q.get("stop") or ""),
          f"rc {rc}, stop {q.get('stop')}")
    rc, log, q, out, dt = session(S, "S6-split", knobs={"SAMPLER": "split"}, args=["--sequence", "short"])
    check("S6 a runtime line inside every 25th sampler line: those lines lost, never misread; the session runs", rc == 0
          and len(ran(q)) == 4 and not q.get("stop"), f"rc {rc}, bursts {len(ran(q))}")
    rc, log, q, out, dt = session(S, "H1-holder-b3", knobs={"ETWHO": "held-from:9"})
    check("H1 a holder appears before burst 3: STOP before it; the closing config NOT read (et-who not free)",
          rc == 0 and ran(q) == ["trained-scp/b1", "random-scp/b1"] and "STOP before burst 3" in log
          and q.get("closing_config", "").startswith("not read: et-who") and not os.path.exists(os.path.join(out, "config-end.json")),
          f"bursts {ran(q)}, closing {q.get('closing_config')}")

    # fix-e202 (verify-e202's finding 1): an et-who that cannot be read is a holder, never "free"
    rc, log, q, out, dt = session(S, "W1-etwho-fail", knobs={"ETWHO": "fail"})
    check("W1 et-who's helper refused (rc 1, nothing on stdout) before the first card command: refused, no device opened",
          rc == 2 and "refused, no device opened: a holder or a foreign device process (et-who unreadable (rc 1, nothing on its stdout))"
          in log and not os.path.exists(os.path.join(out, "config-start.json")), f"rc {rc}")
    rc, log, q, out, dt = session(S, "W2-etwho-garbled", knobs={"ETWHO": "garbled"})
    check("W2 et-who rc 0 with neither a holder line nor its no-holder sentence: refused, no device opened", rc == 2
          and "et-who unreadable (rc 0, but neither a holder line nor its no-holder sentence)" in log
          and not os.path.exists(os.path.join(out, "config-start.json")), f"rc {rc}")
    rc, log, q, out, dt = session(S, "W3-etwho-text1-b3", knobs={"ETWHO": "text1-from:9"})
    check("W3 et-who rc 1 with a line of text from its 9th read (before burst 3): STOP before burst 3; the closing config NOT read",
          rc == 0 and ran(q) == ["trained-scp/b1", "random-scp/b1"] and "STOP before burst 3: et-who unreadable (rc 1)" in log
          and q.get("closing_config", "").startswith("not read: et-who does not read the card free (et-who unreadable")
          and not os.path.exists(os.path.join(out, "config-end.json")), f"bursts {ran(q)}, closing {q.get('closing_config')}")
    rc, log, q, out, dt = session(S, "W4-etwho-closing", knobs={"ETWHO": "fail-from:19"})
    check("W4 et-who unreadable at the closing only (its 19th read): every burst ran; the closing config NOT read", rc == 0
          and len(ran(q)) == 12 and q.get("closing_config", "").startswith("not read: et-who does not read the card free (et-who unreadable")
          and not os.path.exists(os.path.join(out, "config-end.json")), f"bursts {len(ran(q))}, closing {q.get('closing_config')}")

    # fix-e202 (finding 2): a crash of the runner is named before the closing and in queue.json; the runner exits 1, never 0
    rc, log, q, out, dt = session(S, "X1-crash-burst", args=["--sequence", "short"], prep=["bursts"])
    lines = log.splitlines()
    ci = [i for i, ln in enumerate(lines) if " CRASH: NotADirectoryError" in ln]
    ce = [i for i, ln in enumerate(lines) if "config end: TDP 0 W" in ln]
    check("X1 a crash inside burst 1 (its folder cannot be made): 'CRASH: <type>: <message>' before the closing, queue.json's crash, "
          "the closing read, session end and the manifest, rc 1", rc == 1 and ci and ce and ci[0] < ce[0]
          and (q.get("crash") or "").startswith("NotADirectoryError") and "DRY session end" in log and q.get("bursts_ran") == 0
          and os.path.exists(os.path.join(out, "MANIFEST.sha256")), f"rc {rc}, crash {str(q.get('crash')).split(':')[0]}")
    rc, log, q, out, dt = session(S, "X2-crash-smoke", args=["--sequence", "short"], prep=["smoke"])
    check("X2 a crash inside the smoke: CRASH named, no host process, the closing read, rc 1", rc == 1 and " CRASH: " in log
          and (q.get("crash") or "").startswith("NotADirectoryError") and q.get("closing_config") == "read" and not ran(q),
          f"rc {rc}, closing {q.get('closing_config')}")
    xcopy = os.path.join(S, "X1-copy")
    shutil.copytree(os.path.join(S, "X1-crash-burst"), xcopy)
    os.remove(os.path.join(xcopy, "dry.lock")) if os.path.exists(os.path.join(xcopy, "dry.lock")) else None
    with open(os.path.join(xcopy, "runner.rc"), "w") as f:     # as session_e202.sh writes it after the runner exits
        f.write("1\n")
    xdata = os.path.join(S, "e202-x1-crash-data")
    env0 = {k: v for k, v in os.environ.items() if not k.startswith("E202_")}
    r = subprocess.run([PY, "-B", os.path.join(HERE, "collect_e202.py"), xcopy, xdata, "--box-home", os.path.expanduser("~"),
                        "--box-login", pwd.getpwuid(os.getuid()).pw_name, "--data-outside"], cwd=REPO, env=dict(env0, RB_DESKTEST="1"),
                       capture_output=True, text=True, timeout=300)
    fx = json.load(open(os.path.join(xdata, "session-facts-e202.json"))) if os.path.exists(os.path.join(xdata, "session-facts-e202.json")) else {}
    check("X3 the crash's session collected: COPY-BACK EXACT, named a crash's record (never a gate stop's), the facts carry the crash "
          "and runner.rc 1", r.returncode == 0 and "a crash's record" in r.stdout and (fx.get("crash") or "").startswith("NotADirectoryError")
          and fx.get("runner_rc") == 1, (r.stdout.strip().splitlines() or [""])[-1][:160])   # the collector names the crash's type only

    # fix-e202 (finding 5): K1 also on a host that died, or that left no record after its device opened
    rc, log, q, out, dt = session(S, "K1b-hostcrash", knobs={"BURSTS": {"trained-scp/b1": "crash"}})
    check("K1b a host that dies mid-launch in burst 1 (rc 134, no --out record): K1, nothing further", rc == 0
          and ran(q) == ["trained-scp/b1"] and (q.get("stop") or "").startswith("K1: burst 1") and "rc 134" in (q.get("stop") or ""),
          f"stop {q.get('stop')}")
    rc, log, q, out, dt = session(S, "K1c-norecord", knobs={"SMOKE": {"T-scp": "nojson"}})
    check("K1c the first smoke process leaves no --out record after its device opened: K1, GATE-STOP, no burst", rc == 3
          and not ran(q) and (q.get("stop") or "").startswith("K1: smoke T-scp") and "no record" in (q.get("stop") or ""),
          f"rc {rc}, stop {q.get('stop')}")

    # fix-e202 (finding 8): the closing config read is not sent while our own sampler has not stopped
    rc, log, q, out, dt = session(S, "CL-deaf", knobs={"SAMPLER": "deaf:25"}, args=["--cap-end-s", "60"], timeout=200)
    check("CL our sampler ignores every SIGTERM: left running (no kill), the closing config NOT read", rc == 3
          and q.get("closing_config", "").startswith("not read: our sampler did not stop on SIGTERM")
          and "left running, recorded (no kill -9)" in log and not os.path.exists(os.path.join(out, "config-end.json")),
          f"rc {rc}, closing {q.get('closing_config')}")

    # the smoke gate and the arms
    rc, log, q, out, dt = session(S, "F1-scpfail", knobs={"SMOKE": {"T-scp": "core"}})
    check("F1 T-scp's smoke fails its core checks: the dram pair is scored (the fallback), T Z Z T T Z Z T, nothing REPORTED",
          rc == 0 and q.get("scored_stage") == "dram" and ran(q) == [b.replace("scp", "dram") for b in want[:8]], f"bursts {ran(q)}")
    rc, log, q, out, dt = session(S, "F2-allfail", knobs={"SMOKE": {"T-scp": "core", "Z-dram": "core"}})
    check("F2 no pair passes (T-scp and Z-dram core FAIL; a missing record is K1's since fix-e202, case K1c): GATE-STOP, no burst",
          rc == 3 and not ran(q) and "GATE-STOP: the smoke gate: no pair read core PASS" in log
          and q["smoke"]["Z-dram"]["core_status"] == "FAIL" and q["smoke"]["T-scp"]["core_status"] == "FAIL", f"rc {rc}")
    rc, log, q, out, dt = session(S, "F3-logits", knobs={"SMOKE": {"T-scp": "logits", "Z-scp": "logits"}}, args=["--sequence", "short"])
    check("F3 a logits-only failure in T-scp and Z-scp: the gate passes, scp scored, the failure recorded",
          rc == 0 and q.get("scored_stage") == "scp" and q["smoke"]["T-scp"]["logits_status"] == "FAIL"
          and "debug-path defect" in q["smoke"]["T-scp"].get("note", ""), f"stage {q.get('scored_stage')}")
    rc, log, q, out, dt = session(S, "F4-armend", knobs={"BURSTS": {"trained-scp/b2": "core"}})
    nb = [b for b in q.get("bursts", []) if not b.get("ran")]
    check("F4 trained-scp b2's host checks fail: that arm ends (b3, b4 not run), random-scp and the dram pair go on",
          rc == 0 and "trained-scp/b3" not in ran(q) and "random-scp/b4" in ran(q) and "trained-dram/b2" in ran(q)
          and any("the arm ended at trained-scp/b2" in b.get("why", "") for b in nb), f"{len(ran(q))} bursts")
    rc, log, q, out, dt = session(S, "K1-hang", knobs={"BURSTS": {"trained-scp/b1": "hang"}})
    check("K1 a launch that does not finish: STOP (the kit's K1), nothing further", rc == 0 and ran(q) == ["trained-scp/b1"]
          and (q.get("stop") or "").startswith("K1:"), f"stop {q.get('stop')}")
    rc, log, q, out, dt = session(S, "R1-slow", knobs={"SMOKE": {"Z-scp": "slow:2.2"}}, args=["--sequence", "short"])
    check("R1 THE R RULE per arm: Z-scp's smoke 2.2 x slower gives random-scp R 80, trained-scp keeps R 96",
          rc == 0 and q["R"]["random-scp"] == 80 and q["R"]["trained-scp"] == 96
          and json.load(open(os.path.join(out, "bursts", "random-scp", "b1", "burst.json")))["R"] == 80, f"R {q.get('R')}")
    rc, log, q, out, dt = session(S, "R2-noR", knobs={"SMOKE": {"T-scp": "slow:40"}}, args=["--sequence", "short"])
    check("R2 no allowed R under 6 s for trained-scp: its bursts not run (no burst for the arm), random-scp's run",
          rc == 0 and q["R"]["trained-scp"] is None and "trained-scp/b1" not in ran(q) and "random-scp/b1" in ran(q)
          and any("no allowed R" in b.get("why", "") for b in q["bursts"]), f"R {q.get('R')}")
    rc, log, q, out, dt = session(S, "R3-cap", knobs={"SMOKE": {"Z-scp": "slow:3.817"}}, args=["--sequence", "short"])
    zs = q.get("smoke", {}).get("Z-scp", {})
    check("R3 THE HOST'S TIMEOUT CAP (fix-e202, finding 7): Z-scp's 32.5 ms round gives the registered rule's R 48 at 5.72 s, past the "
          "host's 6 s timeout less 0.5 s: random-scp runs at R 16; trained-scp keeps R 96", rc == 0 and q["R"]["random-scp"] == 16
          and zs.get("R_registered_rule") == 48 and "the host's timeout cap" in zs.get("R_why", "") and q["R"]["trained-scp"] == 96
          and json.load(open(os.path.join(out, "bursts", "random-scp", "b1", "burst.json")))["R"] == 16
          and "(the registered rule's R 48, capped)" in log, f"R {q.get('R')}, rule {zs.get('R_registered_rule')}")
    rc, log, q, out, dt = session(S, "C1-cap", args=["--cap-burst-s", "25", "--cap-end-s", "200"])
    check("C1 THE CAP (25 s here): no burst starts after it", rc == 0 and 0 < len(ran(q)) < 12
          and any("the cap" in b.get("why", "") for b in q["bursts"]), f"{len(ran(q))} bursts before the cap")
    rc, log, q, out, dt = session(S, "C2-endbound", args=["--cap-burst-s", "600", "--cap-end-s", "120"])
    check("C2 THE END BOUND (35 minutes here 120 s): a burst whose longest span would pass it does not start",
          rc == 0 and len(ran(q)) < 12 and any("the end bound" in b.get("why", "") for b in q["bursts"]), f"{len(ran(q))} bursts")
    rc, log, q, out, dt = session(S, "C3-diegate", knobs={"INJECT": [{"die": 62, "after_launches": 1}]})
    check("C3 THE DIE GATE held at 62 C after burst 1: each later burst waits its 5 s (here), skipped, no data", rc == 0
          and ran(q) == ["trained-scp/b1"] and sum(1 for b in q["bursts"] if "die gate" in b.get("why", "")) == 11, f"bursts {ran(q)}")
    rc, log, q, out, dt = session(S, "W1-window", args=["--deadline-epoch", str(int(time.time()) + 100)])
    check("W1 the window's last end too close (its longest span and 90 s do not fit): the smoke does not start, GATE-STOP, no burst",
          rc == 3 and not ran(q) and "the window's last end is too close" in log, f"rc {rc}")

    # refusals without --dry
    env = {k: v for k, v in os.environ.items() if not k.startswith("E202_")}
    r = subprocess.run([PY, "-B", RUNNER, "session", "--t0", "1", "--out", os.path.join(S, "N1"), "--idle-before", "1"], cwd=REPO,
                       env=env, capture_output=True, text=True)
    check("N1 a desk-only argument without --dry: refused, no device opened", r.returncode == 2 and "refused, no device opened" in r.stdout,
          r.stdout.strip()[:120])
    r = subprocess.run([PY, "-B", RUNNER, "session", "--t0", "1", "--out", os.path.join(S, "N2")], cwd=REPO,
                       env=dict(env, E202_FAKE_SCALE="0.2"), capture_output=True, text=True)
    check("N2 a desk-test variable without --dry: refused, no device opened", r.returncode == 2 and "desk-test variable" in r.stdout,
          r.stdout.strip()[:120])
    r = subprocess.run([PY, "-B", RUNNER, "session", "--t0", "1", "--out", os.path.join(S, "N3")], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=120)
    lg = open(os.path.join(S, "N3", "session.log")).read() if os.path.exists(os.path.join(S, "N3", "session.log")) else ""
    check("N3 the REAL path on the desk: refused before anything (the host's name), no lock, no device", r.returncode == 2
          and "refused, no device opened: the host's name is" in lg and not os.path.exists(os.path.join(S, "N3", "config-start.json")),
          lg.splitlines()[1][20:140] if len(lg.splitlines()) > 1 else "")

    # END TO END on the alt card, the registered rests: collection, reducer, scorer
    rc, log, q, out, dt = session(S, "E2E", double="alt", args=["--sequence", "e2e", "--anchor-s", "2"], fast=False, timeout=900)
    check("E2E the session (alt card, registered rests, two bursts of each scored configuration)", rc == 0 and len(ran(q)) == 4,
          f"rc {rc}, {dt} s")
    copy = os.path.join(S, "E2E-copy")
    shutil.copytree(out, copy)
    os.remove(os.path.join(copy, "dry.lock")) if os.path.exists(os.path.join(copy, "dry.lock")) else None
    data = os.path.join(S, "e202-e2e-data")
    # the "box" of the dry E2E is this desk: its home and login are what the scrub must take out
    r = subprocess.run([PY, "-B", os.path.join(HERE, "collect_e202.py"), copy, data, "--box-home", os.path.expanduser("~"),
                        "--box-login", pwd.getpwuid(os.getuid()).pw_name, "--data-outside"], cwd=REPO, env=dict(env, RB_DESKTEST="1"),
                       capture_output=True, text=True, timeout=900)
    check("E2E the collection: COPY-BACK EXACT, every burst reduced by the unchanged reducer, SHA256SUMS", r.returncode == 0 and
          "COPY-BACK EXACT" in r.stdout and "COLLECTED" in r.stdout and "4 bursts reduced" in r.stdout, r.stdout.strip().splitlines()[-1][:160])
    sched = [json.loads(ln) for ln in open(os.path.join(out, "fake_sched.jsonl")) if ln.startswith("{")]
    errs = []
    for b in ran(q):
        cfg, k = b.split("/")
        en = json.load(open(os.path.join(data, "bursts", cfg, k, "energy.json")))
        hr = json.load(open(os.path.join(data, "bursts", cfg, k, "host-raw.json")))
        lo, hi = hr["launch_epoch_ms"]
        inj = [s for s in sched if s["tag"] == "burst" and abs(s["t0"] * 1000 - lo) < 50]
        e_inj = sum(s["dp"] * (s["t1"] - s["t0"]) for s in inj)
        t = (hi - lo) / 1000.0
        tol = 0.03 + 0.33 * (t + 7.0) / max(e_inj, 1e-9)
        e = en["board"]["j_per_solve"] / e_inj - 1.0
        errs.append((b, round(e, 4), round(tol, 4), en.get("ok")))
    check("E2E each burst's reduced J over idle against the energy the card injected, within TOL = 3% + 0.33 W/C x (t + 7 s) / J",
          all(ok and abs(e) <= tol for _, e, tol, ok in errs), "; ".join(f"{b} {e:+.2%} (tol {tol:.1%})" for b, e, tol, ok in errs))
    for d in ("bursts", "smoke"):
        if not os.path.isdir(os.path.join(data, d)):
            errs.append(d)
    sc = os.path.join(S, "scores-e2e.json")
    r = subprocess.run([PY, "-I", "-B", os.path.join(HERE, "score_e202.py"), data, "--out", sc], cwd=REPO, capture_output=True,
                       text=True, timeout=600)
    v = json.load(open(sc))["verdict_of_the_day"] if os.path.exists(sc) else {}
    check("E2E the frozen scorer on the collected data reads the gate and every rule (S1 and S3 PASS by construction: t_k is the point "
          "and the injected J over idle the forecast's)", r.returncode == 0 and v.get("E202-S1") == "PASS" and v.get("E202-S3") == "PASS"
          and all(x in ("PASS", "FAIL") for x in v.values()), json.dumps(v))
    v3o = os.path.join(S, "v3-scores-e2e.json")
    r3 = subprocess.run([PY, "-I", "-B", os.path.join(HERE, "v3note_e202.py"), "--score", data, "--out", v3o], cwd=REPO,
                        capture_output=True, text=True, timeout=600)
    s2 = json.load(open(sc)) if os.path.exists(sc) else {}
    s3 = json.load(open(v3o)) if os.path.exists(v3o) else {}
    eq = []
    for key in ("trained-scp", "random-scp"):
        c2, c3 = (s2.get("configs") or {}).get(key, {}), ((s3.get("configs") or {}).get(key) or {}).get("errors", {})
        for a, b in (("e_j_over", "S1-v3 (= v2's S1)"), ("e_j_total", "S1T-v3 (= v2's S1T)"), ("e_j_over_forecast", "S2-v3 (= v2's S2)")):
            eq.append(abs(c2.get(a, 9.0) - c3.get(b, -9.0)) <= 1e-5)
        eq.append(isinstance(c3.get("S2T-v3"), float) and isinstance(((s3.get("configs") or {}).get(key) or {}).get("S2T-v3 within 15%"), bool))
    check("E2E the ledger v3 note's REPORTED readings (v3note_e202.py --score, fix-e202 finding 3): S1, S1T and S2 through v3's route equal "
          "the frozen scorer's to 1e-5; S2T-v3 read", r3.returncode == 0 and len(eq) == 8 and all(eq),
          f"rc {r3.returncode}, " + "; ".join(f"{k} S2T-v3 {((s3.get('configs') or {}).get(k) or {}).get('errors', {}).get('S2T-v3')}"
                                              for k in ("trained-scp", "random-scp")))
    fx = json.load(open(os.path.join(data, "session-facts-e202.json")))
    check("E2E the session facts: the scored stage, R, the peaks and the clock count", fx["scored_stage"] == "scp" and fx["bursts_ran"] == 4
          and fx["telemetry_samples"] == fx["samples_at_600_mhz"] > 100 and fx["peak_board_w"] < 65, f"samples {fx['telemetry_samples']}, "
          f"peak {fx['peak_board_w']} W / {fx['peak_minshire0_c']} C, minutes {fx['card_minutes_first_command_to_close']}")
    gcopy = os.path.join(S, "G3-copy")
    shutil.copytree(os.path.join(S, "G3-tdp5"), gcopy)
    os.remove(os.path.join(gcopy, "dry.lock")) if os.path.exists(os.path.join(gcopy, "dry.lock")) else None
    r = subprocess.run([PY, "-B", os.path.join(HERE, "collect_e202.py"), gcopy, os.path.join(REPO, "docs/reports/data/2099-01-01-e202-x"),
                        "--box-home", "/home/nobody-e2e", "--box-login", "nobody-e2e"], cwd=REPO, env=env, capture_output=True, text=True)
    check("E2E a gate stop is refused under docs/reports/data/ (its record goes under docs/reports/gate-stops/)", r.returncode == 2
          and "gate-stops" in r.stdout and not os.path.exists(os.path.join(REPO, "docs/reports/data/2099-01-01-e202-x")), r.stdout.strip()[:140])
    n = sum(1 for _, ok in RES if ok)
    print(f"SELFTEST-RUN-E202 {n} of {len(RES)} {'PASS' if n == len(RES) else 'FAIL'}")
    return 0 if n == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
