#!/usr/bin/env python3
"""E175 (Q143(g)): the kit's self-test, at the desk, before any claim: no device, no lock, no ssh. E173's selftest_kit_e173.py (lab 5a2a9ba0)
with E175's names, counts and tiles.

    python3 -B tools/claims-v3/e175/selftest_kit_e175.py > tools/claims-v3/e175/logs/selftest-kit.txt

  1  every protocol's BURST runs are its order entries, in order, and those are the registered order's (145 full, 87 subset) or the dry twin's (22)
  2  the order: each pass opens with the three zeros anchors, then the 24 kept tiles and E80's two replicates (29 a pass, 5 passes)
  3  no tile left out by name in any protocol; every pool run's value and type are its tile's; every run's estimate is at most 82 W; the sets
     are 16 governed and 8 pinned, each tile's group the frozen file's
  4  run_e175.protocol_why: None for the protocols; refused for a board stop over 85 W, a die stop over 76 C, an admission or lock over 82 W, other
     tools, a missing stop key, a left-out tile (on a copy whose left_out names one)
  5  the stop-path tests (board 30 W on three samples, die 30 C; fp32.anchor7_zeros) and the smoke (rest and the three zeros anchors; 546 / 546 / 318)
  6  the watcher fix: importing run_e175 installs watcher_q142s on run_hpl; a run_hpl with other bytes is refused by install()
  7  check_e175.py --desk: HARNESS OK, and the harness names the runner, queue, scorer, watcher, protocols and pool
  8  bash -n on every shell file of the kit
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e175_common as C  # noqa: E402

fails = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout, r.stderr


P = json.load(open(os.path.join(HERE, "predictions-e175.json")))
PR = {n: json.load(open(os.path.join(HERE, n))) for n in ("protocol.json", "protocol-subset.json", "protocol-dry.json", "protocol-stoptest-board.json",
                                                           "protocol-stoptest-die.json", "protocol-stoptest-board-dry.json", "protocol-stoptest-die-dry.json")}
good = True
for n, src, want in (("protocol.json", "order", 145), ("protocol-subset.json", "order", 87), ("protocol-dry.json", "dry_order", 22)):
    p = PR[n]
    runs, e = p["blocks"][1]["runs"], p["order_entries"]
    reg = {o["idx"]: o for o in P[src]}
    good = good and p["order_source"] == src and len(runs) == len(e) == want and all(r["label"] == x["label"] for r, x in zip(runs, e)) \
        and all(reg[x["registered_idx"]]["label"] == x["label"] and reg[x["registered_idx"]]["pass"] == x["pass"] for x in e)
ok(good, "1  every protocol's runs are its order entries and the registered order's (145 full, 87 subset passes 1-3) or the dry twin's (22)")
z = {C.label_of(n) for n in C.ZEROS_ANCHORS}
passes = {}
for o in P["order"]:
    passes.setdefault(o["pass"], []).append(o)
reps = all(sum(1 for o in v if o["label"] in C.REPLICATES) == 2 for v in passes.values())
ok(all({x["label"] for x in v[:3]} == z and len(v) == 29 for v in passes.values()) and reps and len(passes) == 5,
   "2  each of the 5 passes opens with the three zeros anchors and holds 29 runs, E80's two replicates among them")
lo = set(P["left_out"])
man = C.manifest()
labs = [r["label"] for p in PR.values() for b in p["blocks"] for r in b["runs"]]
vals = all(r["values"] == C.tile_value(man[C.name_of(r["label"])]) and r["type"] == man[C.name_of(r["label"])]["type"]
           for p in PR.values() for b in p["blocks"] for r in b["runs"] if C.name_of(r["label"]))
est = max(PR["protocol.json"]["admission"][r["label"]]["fixed_p800_w"] for r in PR["protocol.json"]["blocks"][1]["runs"])
sets_ok = (len(P["sets"]["governed"]) == 16 and len(P["sets"]["pinned"]) == 8 and not lo
           and all(P["tiles"][n]["group"] == "governed" for n in P["sets"]["governed"]) and all(P["tiles"][n]["group"] == "pinned" for n in P["sets"]["pinned"]))
ok(not any(C.name_of(x) in lo for x in labs) and vals and est <= C.LIMIT_W and sets_ok,
   f"3  no left-out tile in any protocol; every pool run's value and type are its tile's; the highest estimate that runs is {est} W (line {C.LIMIT_W:g}); "
   f"16 governed and 8 pinned, each the frozen file's group")
import run_e175 as RUN  # noqa: E402
none = all(RUN.protocol_why(PR[n], TOP) is None for n in PR)
ref = {}
for what, f in (("board 86 W", lambda p: p["safety"].update(board_cap_w=86)), ("die 77 C", lambda p: p["safety"].update(abs_stop_c=77)),
                ("admission 83 W", lambda p: p.update(limit_p800_w=83)), ("lock 83 W", lambda p: p.update(peak_lock_w=83)),
                ("other ettelem", lambda p: p["tools"].update(ettelem="build/ettelem-e84/ettelem")), ("no cap_consecutive", lambda p: p["safety"].pop("cap_consecutive")),
                ("a left-out tile", None)):
    q = json.loads(json.dumps(PR["protocol.json"]))
    if f is None:
        keep = RUN._P
        RUN._P = dict(RUN.pred(), left_out=[P["sets"]["pinned"][0]])
        try:
            ref[what] = RUN.protocol_why(q, TOP) is not None
        finally:
            RUN._P = keep
        continue
    f(q)
    ref[what] = RUN.protocol_why(q, TOP) is not None
ok(none and all(ref.values()), f"4  protocol_why: None for the {len(PR)} protocols; refused: {ref}")
sb, sd = PR["protocol-stoptest-board.json"], PR["protocol-stoptest-die.json"]
smoke = [r["label"] for r in PR["protocol.json"]["blocks"][0]["runs"]]
ok(sb["safety"] == {"abs_stop_c": 76, "board_cap_w": 30, "cap_consecutive": 3} and sd["safety"] == {"abs_stop_c": 30, "board_cap_w": 85, "cap_consecutive": 3}
   and sb["blocks"][0]["runs"][0]["label"] == "e5-fp32.anchor7_zeros" and smoke == ["rest"] + [C.label_of(n) for n in C.ZEROS_ANCHORS]
   and PR["protocol.json"]["safety"] == C.STOPS and sorted(PR["protocol.json"]["smoke_cycles"].values()) == [318, 546, 546],
   f"5  the stop tests (board 30 W on 3 samples on fp32.anchor7_zeros, die 30 C), the smoke {smoke}; the session's stops {C.STOPS}")
okw = getattr(RUN.H.Watcher, "_q142s", False) and RUN.WATCHER and RUN.WATCHER["installed"] and RUN.WATCHER_WHY is None
sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "hpl"))
import watcher_q142s as W  # noqa: E402
with tempfile.TemporaryDirectory() as td:
    fake = os.path.join(td, "run_hpl.py")
    shutil.copyfile(os.path.join(TOP, C.RUN_HPL_REL), fake)
    with open(fake, "a") as f:
        f.write("\n# one more line\n")
    mod = types.SimpleNamespace(__file__=fake, Watcher=type("Watcher", (), {}), __name__="fake")
    try:
        W.install(mod)
        refused = False
    except RuntimeError:
        refused = True
ok(okw and refused, f"6  importing run_e175 installed the watcher fix ({RUN.WATCHER and RUN.WATCHER['watcher']}); install() refuses a run_hpl.py with other bytes")
rc, so, _ = sh([sys.executable, "-B", os.path.join(HERE, "check_e175.py"), "--desk"])
H = json.load(open(os.path.join(HERE, "harness-e175.json")))["files_sha256"]
need = ["tools/claims-v3/e175/run_e175.py", "tools/claims-v3/e175/queue_e175.py", "tools/claims-v3/e175/score_e175.py", "tools/claims-v3/hpl/watcher_q142s.py",
        "tools/claims-v3/e175/protocol.json", "tools/claims-v3/e175/pool/e175.json", "tools/claims-v3/e165/score_e165.py", "tools/claims-v3/e173/p8gov.py"]
ok(rc == 0 and so.startswith("HARNESS OK") and all(x in H for x in need), f"7  {so.strip()}; the harness names the runner, queue, scorer, watcher, protocols and pool")
shs = [os.path.join(HERE, x) for x in ("preflight_e175.sh", "collect_e175_bounded.sh", "drypass_intel_e175.sh")] + \
      [os.path.join(HERE, "box", x) for x in sorted(os.listdir(os.path.join(HERE, "box"))) if x.endswith(".sh")]
res = {os.path.relpath(f, HERE): sh(["bash", "-n", f])[0] for f in shs}
ok(all(v == 0 for v in res.values()), f"8  bash -n: {len(res)} scripts parse")
print()
print("ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
