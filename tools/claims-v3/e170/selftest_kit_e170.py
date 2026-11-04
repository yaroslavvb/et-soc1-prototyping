#!/usr/bin/env python3
"""E170 (Q141(w)): the kit's self-test at the desk. No card, no device, no ssh: every box tool is a shim in a temporary sandbox, and Q141(k)'s step
driver runs as a dry listing (RB_DRY=1), which prints its commands and runs none.

    python3 -B tools/claims-v3/e170/selftest_kit_e170.py > tools/claims-v3/e170/logs/selftest-kit.txt

  1. The state gate's helpers (queue_e170.py): continuity() passes E118's committed read (8,689 min at 14:50:39.729 PST on 1 Nov 2026: its change
     record's live gate) and refuses a shorter uptime and an unreadable one; holders_why() refuses card 0 held by anyone and anything of ours on
     either card, and lets another user's card 1 pass (et-who's whole-box wait covers that).
  2. E170's guard refuses, with exit 97 and before the reader starts, residency, threshold, loglevel, sample --reset-ms, any extra word and
     ET_DEVICES other than 0; config, uptime, sample --seconds/--every-ms and sptrace <file> pass the allow-list (the reader is absent here, so
     the exec then fails with another code).
  3. A1: every BURST run of protocol.json, protocol-subset.json and protocol-dry.json carries, at its index, the label of the registered order
     filtered to that protocol's passes; the committed score_e170.py main's mapping refuses the subset's first pass-4 run, A1's maps it.
  4. run_e170.protocol_why() passes the committed protocols and the stop tests, and refuses a looser board stop, a board stop on 3 samples, a die
     stop above 72 C, the reader named without the guard, a run of a tile left out by name and a looser admission line.
  5. Every shell script parses (bash -n).
  6. box/launch_e170.sh's refusals, in a sandbox laid out like ~/nekko with shims for date (GNU), sudo/et-holders and ps: no deadline (2), not a
     date (2), too little time for the full plan (4) and for the subset (4), card 0 held (3), ours on card 1 (3), ours a device process (3), a
     queue already run (5), and the harness check without the binaries (9). None reaches the launch.
  7. box/step_e170.sh lists every step's exact commands under RB_DRY=1 (look, sync, check, launch, wait, pull) and runs none of them.
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
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
os.environ["ET_DEVICES"] = "0"
os.environ["V3_DEVICE"] = "0"
import e170_common as C  # noqa: E402
import queue_e170 as Q  # noqa: E402
import run_e170 as RN  # noqa: E402
import score_e170 as SC  # noqa: E402
import score_e170_a1 as A1  # noqa: E402

fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def sh(cmd, env=None, stdin=None, cwd=None):
    r = subprocess.run(cmd, capture_output=True, env=env, stdin=stdin, cwd=cwd, timeout=60)
    return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")


print(f"E170 kit self-test: run_e170.py {C.sha256_file(RN.__file__)[:16]}..., queue_e170.py {C.sha256_file(Q.__file__)[:16]}..., "
      f"score_e170_a1.py {C.sha256_file(A1.__file__)[:16]}...")

# 1 ----------------------------------------------------------------------------------------------------------------------------------------------
t118 = dt.datetime(2026, 11, 1, 22, 50, 39, 729000, tzinfo=dt.timezone.utc).timestamp() * 1000      # 14:50:39.729 PST
good, why = Q.continuity({"t_ms": t118, "rc": 0, "day": 6, "hours": 0, "mins": 49})
short, why2 = Q.continuity({"t_ms": t118, "rc": 0, "day": 0, "hours": 3, "mins": 10})
unread, why3 = Q.continuity({"t_ms": t118, "rc": 1})
ok(good and not short and not unread, f"continuity: E118's gate read passes ({why}); a 3 h uptime is NO-GO; rc 1 is unreadable")
me = "owner"
fx = {"none": "No process holds an ET-SoC-1 device node or card lock.\n",
      "card0_other": "/dev/et0_mgmt   zq9login  4242 00:10 some command\n",
      "card0_lock_ours": "lock:etsoc-shire0.lock owner 77 00:01 flock\n",
      "card1_ours": "/dev/et1_ops    owner  999 00:05 sparsity_host\n",
      "card1_other": "lock:etsoc-shire1.lock zq9login 5 01:00 flock\n"}
res = {k: Q.holders_why(v, me) for k, v in fx.items()}
ok(res["none"] is None and res["card1_other"] is None and res["card0_other"] and res["card0_lock_ours"] and res["card1_ours"] and "zq9login" not in json.dumps(res),
   f"holders_why: {json.dumps({k: (v[:40] if v else None) for k, v in res.items()})} (no login returned)")

# 2 ----------------------------------------------------------------------------------------------------------------------------------------------
G = os.path.join(HERE, "ettelem_guard_e170.sh")
env0 = dict(os.environ, ET_DEVICES="0")
cases = {"residency 1 2 3": 97, "threshold set 70": 97, "loglevel debug": 97, "sample --reset-ms 1000": 97, "sample --seconds 9 --reset-ms 1": 97,
         "config extra": 97, "uptime 1": 97, "sptrace -x": 97, "sptrace": 97, "": 97, "profile": 97}
got = {k: sh(["bash", G] + k.split(), env=env0)[0] for k in cases}
ok(all(got[k] == 97 for k in cases), f"the guard refuses {len(cases)} forms with exit 97 before the reader starts: {got}")
rc1 = sh(["bash", G, "config"], env=dict(os.environ, ET_DEVICES="1"))[0]
passed = {k: sh(["bash", G] + k.split(), env=env0) for k in ("config", "uptime", "sample --seconds 9 --every-ms 100", "sptrace /dev/null")}
ok(rc1 == 97 and all(v[0] not in (0, 97) and "refused" not in v[2] for v in passed.values()),
   f"ET_DEVICES=1 is refused ({rc1}); config, uptime, sample and sptrace <file> pass the allow-list (exec of the absent reader: {[v[0] for v in passed.values()]})")

# 3 ----------------------------------------------------------------------------------------------------------------------------------------------
P = SC.load_pred()
mism = {}
for name, passes in A1.PROTOCOL_PASSES.items():
    pr = json.load(open(os.path.join(HERE, name)))
    runs = next(b for b in pr["blocks"] if b["name"] == "BURST")["runs"]
    order = A1.order_for(P, passes)
    mism[name] = (len(runs), len(order), sum(1 for i, r in enumerate(runs) if i >= len(order) or order[i]["label"] != r["label"]))
ok(all(a == b and m == 0 for a, b, m in mism.values()), f"each protocol's BURST runs are the registered order filtered to its passes: {mism}")
sub = A1.order_for(P, (1, 2, 4, 5))
i64 = next(i for i, o in enumerate(sub) if o["pass"] == 4)
r64 = {"run": "x", "idx": i64, "label": sub[i64]["label"]}
try:
    SC.pass_by_order(P)(r64)
    old = "mapped"
except SystemExit:
    old = "refused"
ok(old == "refused" and A1.pass_by_order(P, (1, 2, 4, 5))(r64) == 4, f"the subset's first pass-4 run (idx {i64}): score_e170.py's main {old} it, A1 maps it to pass 4")

# 4 ----------------------------------------------------------------------------------------------------------------------------------------------
base = json.load(open(os.path.join(HERE, "protocol.json")))
okp = {n: RN.protocol_why(json.load(open(os.path.join(HERE, n)))) for n in ("protocol.json", "protocol-subset.json", "protocol-dry.json",
                                                                             "protocol-stoptest-board.json", "protocol-stoptest-die.json")}


def bad(f):
    p = json.loads(json.dumps(base))
    f(p)
    return RN.protocol_why(p)


refusals = {"board 70 W": bad(lambda p: p["safety"].update(board_cap_w=70)), "board on 3 samples": bad(lambda p: p["safety"].update(cap_consecutive=3)),
            "die 76 C": bad(lambda p: p["safety"].update(abs_stop_c=76)), "reader without the guard": bad(lambda p: p["tools"].update(ettelem=C.ETTELEM_REL)),
            "a left-out tile": bad(lambda p: p["blocks"][1]["runs"].append({"type": "fp32", "values": "file:x", "label": "b7-fp32.uniform_pm1"})),
            "admission 82 W": bad(lambda p: p.update(limit_p800_w=82.0))}
ok(all(v is None for v in okp.values()) and all(refusals.values()), f"protocol_why: the five committed protocols pass; refused: {sorted(refusals)}")

# 5 ----------------------------------------------------------------------------------------------------------------------------------------------
shs = sorted([os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith(".sh")] + [os.path.join(HERE, "box", f) for f in os.listdir(os.path.join(HERE, "box")) if f.endswith(".sh")])
synt = {os.path.relpath(p, HERE): sh(["bash", "-n", p])[0] for p in shs}
ok(all(v == 0 for v in synt.values()), f"bash -n: {len(synt)} scripts parse ({sorted(synt)})")

# 6 ----------------------------------------------------------------------------------------------------------------------------------------------
L = os.path.join(HERE, "box", "launch_e170.sh")
with tempfile.TemporaryDirectory() as td:
    home = os.path.join(td, "home")
    nek = os.path.join(home, "nekko")
    shutil.copytree(HERE, os.path.join(nek, "tools", "claims-v3", "e170"), ignore=shutil.ignore_patterns("__pycache__", "logs"))
    shim = os.path.join(td, "shim")
    os.makedirs(shim)
    gd = shutil.which("gdate")
    open(os.path.join(shim, "date"), "w").write(f"#!/bin/sh\nexec {gd} \"$@\"\n")
    open(os.path.join(shim, "sudo"), "w").write("#!/bin/sh\n[ \"$1\" = -n ] && shift\ncat \"$HOLDERS_FIXTURE\"\n")
    open(os.path.join(shim, "ps"), "w").write("#!/bin/sh\ncat \"$PS_FIXTURE\"\n")
    for f in ("date", "sudo", "ps"):
        os.chmod(os.path.join(shim, f), 0o755)
    hf, pf = os.path.join(td, "holders.txt"), os.path.join(td, "ps.txt")
    uid = os.getuid()

    def launch(args, holders="No process holds an ET-SoC-1 device node or card lock.\n", ps=f"{uid} bash\n", pre=None):
        open(hf, "w").write(holders)
        open(pf, "w").write(ps)
        if pre:
            pre()
        env = dict(os.environ, HOME=home, PATH=shim + os.pathsep + os.environ["PATH"], HOLDERS_FIXTURE=hf, PS_FIXTURE=pf, USER="owner")
        return sh(["bash", "-s", "--"] + args, env=env, stdin=open(L, "rb"))

    def at(minutes):
        return subprocess.run([gd, "-d", f"@{int(dt.datetime.now().timestamp()) + int(minutes * 60)}", "+%F %T %Z"], capture_output=True, text=True).stdout.strip()
    far = at(120)
    r = {"no deadline": launch([]), "not a date": launch(["garbage", "words"]), "full, 30 min": launch(at(30).split()),
         "subset, 20 min": launch(at(20).split() + ["subset"]),
         "card 0 held": launch(far.split(), holders="/dev/et0_mgmt  zq9login 4242 00:10 x\n"),
         "ours on card 1": launch(far.split(), holders="lock:etsoc-shire1.lock owner 99 00:10 flock\n"),
         "ours a device process": launch(far.split(), ps=f"{uid} sparsity_host\n"),
         "a queue already ran": launch(far.split(), pre=lambda: (os.makedirs(os.path.join(nek, "build", "e170", "runs"), exist_ok=True),
                                                                 open(os.path.join(nek, "build", "e170", "runs", "queue.jsonl"), "w").close())),
         }
    shutil.rmtree(os.path.join(nek, "build", "e170"), ignore_errors=True)
    r["no binaries"] = launch(far.split())
    want = {"no deadline": 2, "not a date": 2, "full, 30 min": 4, "subset, 20 min": 4, "card 0 held": 3, "ours on card 1": 3, "ours a device process": 3,
            "a queue already ran": 5, "no binaries": 9}
    rcs = {k: v[0] for k, v in r.items()}
    launched = any("launched T0=" in v[1] for v in r.values()) or os.path.exists(os.path.join(nek, "build", "e170", "slot.txt"))
    ok(rcs == want and not launched, f"launch_e170.sh's refusals: {rcs}; nothing launched")
    ok("zq9login" not in "".join(v[1] + v[2] for v in r.values()), "the launch prints holder counts only, never a login (the fixture login zq9login never appears)")

# 7 ----------------------------------------------------------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    env = dict(os.environ, RB_DRY="1", RB_OUT=os.path.join(td, "out"), RB_LOCK=os.path.join(td, "lock.txt"))
    S7 = os.path.join(HERE, "box", "step_e170.sh")
    lst = {}
    for st in (["look"], ["sync"], ["check"], ["launch", "2026-11-04 19:00 PST"], ["launch", "2026-11-04 19:00 PST", "subset"], ["wait"], ["pull"]):
        rc, so, se = sh(["bash", S7] + st, env=env, cwd=ROOT)
        lst[" ".join(st)] = (rc, so)
    allz = all(v[0] == 0 for v in lst.values())
    no_ssh_ran = not os.path.exists(os.path.join(td, "out", "runbook.log")) or "cls=" not in open(os.path.join(td, "out", "runbook.log")).read()
    ok(allz and "rsync -a -c -R" in lst["sync"][1] and "bash -s -- '2026-11-04 19:00 PST' subset" in lst["launch 2026-11-04 19:00 PST subset"][1] and no_ssh_ran,
       f"step_e170.sh lists every step under RB_DRY=1 and runs nothing: {{{', '.join(f'{k}: rc {v[0]}' for k, v in lst.items())}}}")
    print("     the listing of `launch '2026-11-04 19:00 PST'`:")
    for ln in lst["launch 2026-11-04 19:00 PST"][1].splitlines()[:4]:
        print("       " + ln.replace(ROOT, "<lab clone>")[:220])

print()
print("ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
