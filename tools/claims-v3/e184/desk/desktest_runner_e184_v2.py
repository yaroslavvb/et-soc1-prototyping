#!/usr/bin/env python3
"""E184 (Q153), kit v2 (KIT.md.dated-note-1.md section 4): desktest_runner_e184.py (v1, which stays as committed) on run_e184_v2.py, with one
case added, U5: arm B's B1 pass (18440) on a scratch copy of the plan whose holds are shortened to 1.5 s (three processes of 0.6 s each; the
gaps 0.2 s), so every process of every hold must come after a "gate" mark that names it (D1, the stall check and the live stop before EVERY
process: the verifier's fault 9). Only the scratch tree's plan is shortened; the committed plan is read for nothing here.

E184 (Q153, the kit): the desk test of the runner's real path (not --dry) on the Intel: run_e184.py --desk drives the desk build of the
patched host (desktest_host_e184.sh's, a mock runtime: no card) while a thread here writes a stand-in sampler file at 10 Hz.

    /usr/bin/python3 -B tools/claims-v3/e184/desk/desktest_runner_e184_v2.py <scratch dir> <desk host binary>

  U1 the smoke (18401): four quads, every one 18 launches with its segments S A B B A or B A A B as planned, its schedule file written, its
     images made and equal to the frozen list, marks for every process, rc 0;
  U2 a stop mid-pass (18410): the sampler file turns to 70 W about 3 s after the pass.s 10 s lead: the runner writes STOP and stop.json, ends rc 5, and runs
     fewer than the pass's 108 quads;
  U3 arm B's step-response pass (18442) on card 1's stops: six bursts of 2 and 4 s with 7 s of idle before each, item and process marks, rc 0;
  U4 refusals before any process: a pass of the other arm's card (rc 2), a pass the plan does not have (rc 2), parts P and C without
     cal.json (rc 2).
The runner's D1 other-user test is the box's (et-holders): --desk skips it, and is refused on a lab box (the runner checks the hostname).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
S = os.path.abspath(sys.argv[1])
HOST = os.path.abspath(sys.argv[2])
TREE = os.path.join(S, "tree")
res = []


def check(name, ok, detail):
    res.append(ok)
    print("%-4s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def writer(path, stop_evt, hot_after=None, card_temp=50):
    t0 = time.time()
    with open(path, "a") as f:
        while not stop_evt.is_set():
            hot = hot_after is not None and time.time() - t0 > hot_after
            d = {"t_ms": int(time.time() * 1000), "since_reset_ms": -1, "board_w": 70.0 if hot else 34.0,
                 "sp": {"board_avg_w": 34.0, "minion_w": [10.0, 9.0, 11.0], "sram_w": [2.0, 1.9, 2.1], "noc_w": [2.0, 1.9, 2.1]},
                 "temp_c": {"pmic": card_temp, "minshire": [card_temp, card_temp - 2, card_temp + 5]}, "mhz": {"minion": 600}}
            f.write(json.dumps(d) + "\n")
            f.flush()
            time.sleep(0.1)


def runner(out, p, card, hot_after=None, extra=()):
    tel = os.path.join(S, "tel-%d-%s.jsonl.raw" % (p, card))
    ev = threading.Event()
    th = threading.Thread(target=writer, args=(tel, ev, hot_after), daemon=True)
    th.start()
    time.sleep(0.3)
    kern = os.path.join(S, "kernel.elf")
    open(kern, "w").write("desk stand-in kernel: the mock runtime never reads it\n")
    env = dict(os.environ, E184_DESK_HOST=HOST, E184_DESK_KERNEL=kern, E184_MOCK_LAUNCH_MS="5")
    r = subprocess.run([sys.executable, "-B", os.path.join(TREE, "tools/claims-v3/e184/run_e184_v2.py"), out, "--root", TREE, "--pass", str(p),
                        "--card", card, "--tel-live", tel, "--desk"] + list(extra), env=env, capture_output=True, text=True, timeout=600)
    ev.set()
    th.join(timeout=2)
    return r


if os.path.exists(TREE):
    shutil.rmtree(TREE)
os.makedirs(os.path.join(TREE, "tools/claims-v3"))
shutil.copytree(KIT, os.path.join(TREE, "tools/claims-v3/e184"), ignore=shutil.ignore_patterns("__pycache__"))

out = os.path.join(S, "u1")
r = runner(out, 18401, "aifoundry3")
runs = [json.loads(l) for l in open(os.path.join(out, "runs.jsonl"))] if os.path.exists(os.path.join(out, "runs.jsonl")) else []
marks = [json.loads(l) for l in open(os.path.join(out, "marks.jsonl"))] if os.path.exists(os.path.join(out, "marks.jsonl")) else []
plan = json.load(open(os.path.join(KIT, "plan-e184.json")))
items = [q for q in plan["arm_S"]["passes"] if q["pass"] == 18401][0]["items"]
ok = r.returncode == 0 and len(runs) == 4 * 18
for it in items:
    ls = [x for x in runs if x["seq"] == it["seq"]]
    want = ["S", "S"] + [l for l in {"ABBA": "AAAABBBBBBBBAAAA", "BAAB": "BBBBAAAAAAAABBBB"}[it["orient"]]]
    ok = ok and [x["label"] for x in ls] == want and all(x["ok"] for x in ls) and ls[0]["n"] == it["n"]
    ok = ok and os.path.exists(os.path.join(out, "sched", "q%04d.txt" % it["seq"]))
frozen = dict(reversed(l.split()) for l in open(os.path.join(KIT, "images-e184.sha256")))
import hashlib  # noqa: E402
imgs = sorted(os.listdir(os.path.join(TREE, "build/e184/images")))
ok = ok and all(hashlib.sha256(open(os.path.join(TREE, "build/e184/images", f), "rb").read()).hexdigest() == frozen[f] for f in imgs)
ok = ok and sum(1 for m in marks if m["event"] == "proc_end" and m["rc"] == 0) == 4
check("U1 the smoke", ok, "rc %d, %d launches, images %s, procs %d" % (r.returncode, len(runs), imgs,
                                                                     sum(1 for m in marks if m["event"] == "proc_end")))
out = os.path.join(S, "u2")
r = runner(out, 18410, "aifoundry3", hot_after=13.0)
nq = len(set(json.loads(l)["seq"] for l in open(os.path.join(out, "runs.jsonl")))) if os.path.exists(os.path.join(out, "runs.jsonl")) else 0
sj = json.load(open(os.path.join(out, "stop.json"))) if os.path.exists(os.path.join(out, "stop.json")) else {}
check("U2 a stop mid-pass", r.returncode == 5 and os.path.exists(os.path.join(out, "STOP")) and 0 < nq < 108 and "65" in sj.get("why", ""),
      "rc %d, %d quads ran, stop: %s" % (r.returncode, nq, sj.get("why")))
out = os.path.join(S, "u3")
t0 = time.time()
r = runner(out, 18442, "aifoundry1-c1")
runs = [json.loads(l) for l in open(os.path.join(out, "runs.jsonl"))] if os.path.exists(os.path.join(out, "runs.jsonl")) else []
marks = [json.loads(l) for l in open(os.path.join(out, "marks.jsonl"))] if os.path.exists(os.path.join(out, "marks.jsonl")) else []
seqs = sorted(set(x["seq"] for x in runs))
check("U3 arm B's bursts", r.returncode == 0 and seqs == list(range(6)) and sum(1 for m in marks if m["event"] == "item_end") == 6,
      "rc %d, %d launches over items %s, %d item marks, %.0f s" % (r.returncode, len(runs), seqs,
                                                                  sum(1 for m in marks if m["event"] == "item_end"), time.time() - t0))
r1 = runner(os.path.join(S, "u4a"), 18442, "aifoundry3")
r2 = runner(os.path.join(S, "u4b"), 18499, "aifoundry3")
calp = os.path.join(TREE, "build/e184/cal.json")
if os.path.exists(calp):
    os.remove(calp)
r3 = runner(os.path.join(S, "u4c"), 18414, "aifoundry3")
check("U4 refusals", r1.returncode == 2 and r2.returncode == 2 and r3.returncode == 2 and not os.path.exists(os.path.join(S, "u4c", "runs.jsonl"))
      or (r3.returncode == 2 and os.path.getsize(os.path.join(S, "u4c", "runs.jsonl")) == 0),
      "other card rc %d, unplanned rc %d, P without cal.json rc %d" % (r1.returncode, r2.returncode, r3.returncode))
tp = os.path.join(TREE, "tools/claims-v3/e184/plan-e184.json")
pl = json.load(open(tp))
for q in pl["arm_B"]["passes"]:
    if q["pass"] == 18440:
        for it in q["items"]:
            it["gap_s"] = 0.2
            if it.get("hold_s"):
                it["hold_s"], it["proc_s"] = 1.5, 0.6
        q["est_s"] = 60
json.dump(pl, open(tp, "w"))
out = os.path.join(S, "u5")
r = runner(out, 18440, "aifoundry1-c1")
marks = [json.loads(l) for l in open(os.path.join(out, "marks.jsonl"))] if os.path.exists(os.path.join(out, "marks.jsonl")) else []
procs = [m for m in marks if m["event"] == "proc_start"]
gated, last_gate = 0, None
for m in marks:
    if m["event"] == "gate":
        last_gate = m["where"]
    elif m["event"] == "proc_start":
        gated += 1 if last_gate == m["where"] else 0
        last_gate = None
nhold = sum(1 for m in procs if " proc " in m["where"])
check("U5 every process of a hold gated", r.returncode == 0 and nhold == 27 and gated == len(procs),
      "rc %d, %d processes (%d of them in holds), %d preceded by a gate mark naming them, %d gate marks in all" % (
          r.returncode, len(procs), nhold, gated, sum(1 for m in marks if m["event"] == "gate")))
print("DESKTEST-RUNNER-E184-V2: %d of %d PASS" % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
