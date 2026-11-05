#!/usr/bin/env python3
"""E174 (Q142(kg)): the kit's self-test, at the desk, before any claim: no device, no lock, no ssh.

    python3 -B tools/claims-v3/e174/selftest_kit_e174.py > tools/claims-v3/e174/logs/selftest-kit.txt

  1  every protocol's BURST runs are its order entries, in order, and those are the registered order's (126 full, 84 subset) or the dry twin's (24)
  2  the order: each pass opens with the three zeros anchors; half A (passes 1-3) holds tier A, half B (passes 4-6) tier B in ascending estimate
  3  no tile left out by name in any protocol; every pool run's value and type are its tile's; every run's estimate is at most 60 W
  4  run_e174.protocol_why: None for the five protocols; refused for a looser die stop, board stop, sample count, admission or lock, other tools,
     a left-out tile, a tile not admitted
  5  the stop-path tests (die 30 C before any launch; board 25 W on one sample, the dry twin's 30 W) and the ramped smoke (rest,
     int8.anchor7_zeros, fp32.b_onebit_b20_one; cycles 318 / 546)
  6  the watcher fix: importing run_e174 installs watcher_q142s on run_hpl (the session's record carries it)
  7  check_e174.py --desk: HARNESS OK, and the harness names every file the box steps sync and run
  8  the queue's state-gate helpers on E170's committed state read: continuity() reads GO, holders_why() counts only
  9  launch_e174.sh's refusals in a sandbox HOME (stand-in date, sudo, ps, uptime; GNU date): no window (2), past the last start or a deadline
     after the last end (6), too little time (4), a queue already ran (5), the host booted after E84's read (3), card 0 held, ours on card 1, ours a
     device process, a run queue of ours (3), the harness not OK (9); nothing launched, no login printed
  10 bash -n on every shell file of the kit
SPDX-License-Identifier: Apache-2.0
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
os.environ.setdefault("ET_DEVICES", "0")
import e174_common as C  # noqa: E402

fails = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def sh(cmd, env=None, stdin=None, cwd=None):
    r = subprocess.run(cmd, env=env, stdin=stdin, cwd=cwd, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


P = json.load(open(os.path.join(HERE, "predictions-e174.json")))
PR = {n: json.load(open(os.path.join(HERE, n))) for n in ("protocol.json", "protocol-subset.json", "protocol-dry.json", "protocol-stoptest-board.json",
                                                           "protocol-stoptest-die.json", "protocol-stoptest-board-dry.json", "protocol-stoptest-die-dry.json")}

# 1
good = True
for n, want_src, want_n in (("protocol.json", "order", 126), ("protocol-subset.json", "order", 84), ("protocol-dry.json", "dry_order", 24)):
    p = PR[n]
    runs = p["blocks"][1]["runs"]
    reg = {o["idx"]: o for o in P[want_src]}
    e = p["order_entries"]
    good = good and p["order_source"] == want_src and len(runs) == len(e) == want_n and all(r["label"] == x["label"] for r, x in zip(runs, e)) \
        and all(reg[x["registered_idx"]]["label"] == x["label"] and reg[x["registered_idx"]]["pass"] == x["pass"] for x in e)
ok(good, "1  every protocol's runs are its order entries and the registered order's (126 full, 84 subset passes 1, 2, 4, 5) or the dry twin's (24)")
# 2
z = {C.label_of(n) for n in C.ZEROS_ANCHORS}
passes = {}
for o in P["order"]:
    passes.setdefault(o["pass"], []).append(o)
first3 = all({x["label"] for x in v[:3]} == z for v in passes.values())
tierA = all(P["tiles"][o["name"]]["tier"] == "A" for p in (1, 2, 3) for o in passes[p])
tierB = all(P["tiles"][o["name"]]["tier"] in ("A", "B") and (o["name"] in C.ZEROS_ANCHORS or P["tiles"][o["name"]]["tier"] == "B") for p in (4, 5, 6) for o in passes[p])
asc = all([P["tiles"][o["name"]]["est_card0_peak_w"] for o in passes[p][3:]] == sorted(P["tiles"][o["name"]]["est_card0_peak_w"] for o in passes[p][3:]) for p in (4, 5, 6))
ok(first3 and tierA and tierB and asc and len(passes[1]) == 29 and len(passes[4]) == 13,
   "2  each pass opens with the zeros anchors; half A tier A (29 a pass), half B tier B in ascending estimate (13 a pass), the hottest last")
# 3
lo = set(P["left_out"])
labs = [r["label"] for p in PR.values() for b in p["blocks"] for r in b["runs"]]
man = C.manifest()
vals = all(r["values"] == C.tile_value(man[C.name_of(r["label"])]) and r["type"] == man[C.name_of(r["label"])]["type"]
           for p in PR.values() for b in p["blocks"] for r in b["runs"] if C.name_of(r["label"]))
est = max(PR["protocol.json"]["admission"][r["label"]]["fixed_p800_w"] for r in PR["protocol.json"]["blocks"][1]["runs"])
ok(not any(C.name_of(x) in lo for x in labs) and vals and est <= C.ADMIT_LINE_W,
   f"3  no left-out tile in any protocol; every pool run's value and type are its tile's; the highest estimate that runs is {est} W (line {C.ADMIT_LINE_W:g})")
# 4
import run_e174 as RUN  # noqa: E402
none = all(RUN.protocol_why(PR[n]) is None for n in PR)
ref = {}
for what, f in (("die 73 C", lambda p: p["safety"].update(abs_stop_c=73)), ("board 66 W", lambda p: p["safety"].update(board_cap_w=66.0)),
                ("3 samples", lambda p: p["safety"].update(cap_consecutive=3)), ("admission 61 W", lambda p: p.update(limit_p800_w=61)),
                ("lock 63 W", lambda p: p.update(peak_lock_w=63)), ("other ettelem", lambda p: p["tools"].update(ettelem="build/ettelem-e84/ettelem")),
                ("a left-out tile", lambda p: p["blocks"][1]["runs"].append({"label": C.label_of(sorted(lo)[0])})),
                ("a tile not admitted", lambda p: p["blocks"][1]["runs"].append({"label": "b8-fp32.not_a_tile"}))):
    q = json.loads(json.dumps(PR["protocol.json"]))
    f(q)
    ref[what] = RUN.protocol_why(q) is not None
ok(none and all(ref.values()), f"4  protocol_why: None for the {len(PR)} protocols; refused: {ref}")
# 5
sb, sd, sbd = PR["protocol-stoptest-board.json"], PR["protocol-stoptest-die.json"], PR["protocol-stoptest-board-dry.json"]
smoke = [r["label"] for r in PR["protocol.json"]["blocks"][0]["runs"]]
ok(sb["safety"] == {"abs_stop_c": 72, "board_cap_w": 25, "cap_consecutive": 1} and sd["safety"]["abs_stop_c"] == 30 and sbd["safety"]["board_cap_w"] == 30
   and sb["blocks"][0]["runs"][0]["label"] == "b8-int8.anchor7_zeros" and smoke == ["rest", "b8-int8.anchor7_zeros", "b8-fp32.b_onebit_b20_one"]
   and PR["protocol.json"]["smoke_cycles"] == {"b8-int8.anchor7_zeros": 318, "b8-fp32.b_onebit_b20_one": 546} and PR["protocol.json"]["safety"] == C.SAFETY,
   f"5  the stop tests (board 25 W one sample on int8.anchor7_zeros, die 30 C; the dry board 30 W) and the ramped smoke {smoke}; the session's stops {C.SAFETY}")
# 6
ok(getattr(RUN.H.Watcher, "_q142s", False) and RUN.WATCHER and RUN.WATCHER["installed"] and RUN.WATCHER_WHY is None,
   f"6  importing run_e174 installed the watcher fix ({RUN.WATCHER and RUN.WATCHER['watcher']}, run_hpl {RUN.WATCHER and RUN.WATCHER['run_hpl_sha256'][:12]})")
# 7
rc, so, _ = sh([sys.executable, "-B", os.path.join(HERE, "check_e174.py"), "--desk"])
H = json.load(open(os.path.join(HERE, "harness-e174.json")))["files_sha256"]
need = ["tools/claims-v3/e174/run_e174.py", "tools/claims-v3/e174/queue_e174.py", "tools/claims-v3/e170/ettelem_guard_e170.sh", "tools/claims-v3/hpl/watcher_q142s.py",
        "tools/claims-v3/e174/box/launch_e174.sh", "tools/claims-v3/e174/protocol.json", "tools/claims-v3/kinds/blind8/blind8.json"]
ok(rc == 0 and so.startswith("HARNESS OK") and all(x in H for x in need), f"7  {so.strip()}; the harness names the runner, queue, guard, watcher, launcher, protocols and pool")
# 8
sys.path.insert(0, HERE)
import queue_e174 as Q  # noqa: E402
g = json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-04-e170-blind7-card0/aifoundry1-c0/state-gate.json")))
okc, msg = Q.continuity(g["uptime"])
hw = Q.holders_why("/dev/et1_mgmt   someone 4242 00:10 x\n", "owner")
hw0 = Q.holders_why("/dev/et0_ops   someone 4242 00:10 x\n", "owner")
ok(okc and hw is None and hw0 is not None and "someone" not in (hw0 or ""), f"8  continuity() on E170's committed read: {msg}; holders_why: card 1 another user's -> None, card 0 held -> refused, no login")
# 9
L = os.path.join(HERE, "box", "launch_e174.sh")
gd = shutil.which("gdate")
if not gd:
    ok(False, "9  no GNU date here (gdate): the launch sandbox cannot run")
else:
    with tempfile.TemporaryDirectory() as td:
        home = os.path.join(td, "home")
        nek = os.path.join(home, "nekko")
        shutil.copytree(HERE, os.path.join(nek, "tools", "claims-v3", "e174"), ignore=shutil.ignore_patterns("__pycache__", "logs"))
        shim = os.path.join(td, "shim")
        os.makedirs(shim)
        hf, pf, bf = os.path.join(td, "holders.txt"), os.path.join(td, "ps.txt"), os.path.join(td, "boot.txt")
        open(os.path.join(shim, "date"), "w").write(f"#!/bin/sh\nexec {gd} \"$@\"\n")
        open(os.path.join(shim, "sudo"), "w").write("#!/bin/sh\n[ \"$1\" = -n ] && shift\ncat \"$HOLDERS_FIXTURE\"\n")
        open(os.path.join(shim, "ps"), "w").write("#!/bin/sh\ncat \"$PS_FIXTURE\"\n")
        open(os.path.join(shim, "uptime"), "w").write("#!/bin/sh\ncat \"$BOOT_FIXTURE\"\n")
        for f in ("date", "sudo", "ps", "uptime"):
            os.chmod(os.path.join(shim, f), 0o755)
        uid = os.getuid()

        def at(minutes):
            return subprocess.run([gd, "-d", f"@{int(dt.datetime.now().timestamp()) + int(minutes * 60)}", "+%F %T %Z"], capture_output=True, text=True).stdout.strip()

        def launch(args, holders="No process holds an ET-SoC-1 device node or card lock.\n", ps=f"{uid} bash\n", boot="2026-10-26 15:02:04\n", pre=None):
            open(hf, "w").write(holders)
            open(pf, "w").write(ps)
            open(bf, "w").write(boot)
            if pre:
                pre()
            env = dict(os.environ, HOME=home, PATH=shim + os.pathsep + os.environ["PATH"], HOLDERS_FIXTURE=hf, PS_FIXTURE=pf, BOOT_FIXTURE=bf, USER="owner")
            return sh(["bash", "-s", "--"] + args, env=env, stdin=open(L, "rb"))
        LS, LE = at(600), at(900)
        far = at(120)
        r = {"no window": launch([]), "two times only": launch([far, LS]), "not a date": launch(["garbage", LS, LE]),
             "past the last start": launch([far, at(-5), LE]), "a deadline after the last end": launch([at(120), LS, at(60)]),
             "full, 30 min": launch([at(30), LS, LE]), "subset, 20 min": launch([at(20), LS, LE, "subset"]),
             "booted after E84's read": launch([far, LS, LE], boot="2026-11-05 01:00:00\n"),
             "card 0 held": launch([far, LS, LE], holders="/dev/et0_mgmt  zq9login 4242 00:10 x\n"),
             "ours on card 1": launch([far, LS, LE], holders="lock:etsoc-shire1.lock owner 99 00:10 flock\n"),
             "ours a device process": launch([far, LS, LE], ps=f"{uid} sparsity_host\n"),
             "ours a run queue (E172's)": launch([far, LS, LE], ps=f"{uid} python3 tools/claims-v3/e172/queue_e172.py --slots s\n"),
             "a queue already ran": launch([far, LS, LE], pre=lambda: (os.makedirs(os.path.join(nek, "build", "e174", "runs"), exist_ok=True),
                                                                        open(os.path.join(nek, "build", "e174", "runs", "queue.jsonl"), "w").close()))}
        shutil.rmtree(os.path.join(nek, "build", "e174"), ignore_errors=True)
        r["the harness not OK (no binaries)"] = launch([far, LS, LE])
        r["the harness not OK, subset"] = launch([far, LS, LE, "subset"])
        want = {"no window": 2, "two times only": 2, "not a date": 2, "past the last start": 6, "a deadline after the last end": 6, "full, 30 min": 4,
                "subset, 20 min": 4, "booted after E84's read": 3, "card 0 held": 3, "ours on card 1": 3, "ours a device process": 3,
                "ours a run queue (E172's)": 3, "a queue already ran": 5, "the harness not OK (no binaries)": 9, "the harness not OK, subset": 9}
        rcs = {k: v[0] for k, v in r.items()}
        launched = any("LAUNCHED e174" in v[1] for v in r.values()) or os.path.exists(os.path.join(nek, "build", "e174", "slot.txt"))
        ok(rcs == want and not launched, f"9  launch_e174.sh's refusals: {rcs}; nothing launched")
        ok("zq9login" not in "".join(v[1] + v[2] for v in r.values()), "9  the launch prints holder counts only, never a login (the fixture login never appears)")
        ok(any(ln.startswith("IDENTITY-STOP") for ln in r["booted after E84's read"][1].splitlines()), "9  a host booted after E84's read prints IDENTITY-STOP")
        slots = {k: ("slot 45 min" in r[k][1], "slot 30 min" in r[k][1]) for k in ("the harness not OK (no binaries)", "the harness not OK, subset")}
        ok(slots == {"the harness not OK (no binaries)": (True, False), "the harness not OK, subset": (False, True)}, f"9  the full plan's slot is 45 min, the subset's 30: {slots}")
# 10
shs = [os.path.join(HERE, x) for x in ("preflight_e174.sh", "collect_e174.sh", "drypass_intel_e174.sh")] + \
      [os.path.join(HERE, "box", x) for x in sorted(os.listdir(os.path.join(HERE, "box"))) if x.endswith(".sh")]
res = {os.path.relpath(f, HERE): sh(["bash", "-n", f])[0] for f in shs}
ok(all(v == 0 for v in res.values()), f"10 bash -n: {len(res)} scripts parse")
print()
print("ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
