#!/usr/bin/env python3
"""E184's reducer self-test, v4 (dated amendment A4; kit note 3, KIT.md.dated-note-3.md section 4): A4's session gate in reduce_e184_v4.py
against v3's (reduce_e184_v3.py, unchanged), on synthetic sessions with a stated truth (fake_card_e184_v2.py, unchanged) in the box's file
layout, their logs copied and changed. Desk only; nothing opens a card or reaches a network.

    /usr/bin/python3 -B tools/claims-v3/e184/selftest_reduce_e184_v4.py <scratch dir> > tools/claims-v3/e184/logs/selftest-reduce-e184-v4.txt

  Q1-Q5  whole sessions where A4 changes nothing (V1 arm S seed 11; B1 arm B seed 21; V1 with its end read MOVED to TDP 65 W; B1 with its
         end TDP 41 W; V1 with the smoke gate failed and an earlier session's files beside it): reduce v4's output is v3's, key for key, but
         for the reducer's name, the gate's name, the new config_status and step7_reads' status fields, and the reasons' words (as many
         reasons, the same gate).
  G0-G11 A3-3's twelve gate cases (selftest_score_e184_v3.py's, the same edits; G10 as G10a and G10b): each reads the same under v4 as
         under v3 (the gate, the departures' count, and each edge's read from the same file; v4's label adds "A4").
  K1-K20 A4's cases (critic-q154's nit 1 and verify-q154k's fault 2, whose case names H3-H16 are given beside), v4 against v3:
         K1 a partial start read (tdp_w null, a failed GET) beside a complete step-7 read: v4 MISSING and replaced, holds (one departure);
            v3 read it as moved (NOT SCORED). K2 the same with minion_mhz absent (a failed clock GET).
         K3 an empty {} start read, no step-7 read (H3): v4 NOT SCORED (missing, not replaced); v3 held it unchecked.
            K3b the same with a complete step-7 read: v4 replaces it (one departure).
         K4 (H4) start {} and the end read MOVED (TDP 65 W): v4 NOT SCORED (the moved end read is checked on its own); v3 held.
         K5 (H5) the start read MOVED (TDP 25 W) and the end {}: v4 NOT SCORED; v3 held.
         K6 (H6) arm B, TDP and threshold null at both ends, no step-7 read: v4 NOT SCORED; v3 held (null == null).
            K6b the same with a complete step-7 read in each window: v4 holds with two departures. K6c the start's replacement TDP 40 W,
            the end's own TDP 41 W: NOT SCORED.
         K15 (H15) the end read empty, the only step-7 file in its window an empty {}: v4 NOT SCORED; v3 held (one departure).
         K16 (H16) the start read empty; two step-7 files in the window, the older complete, the newer partial: v4 takes the older, holds;
            v3 took the newer (NOT SCORED).
         K17 a partial start read with no record of its attempt: NOT SCORED under both (v4: never replaced).
         K18 the start read's tdp_w is JSON false: v4 NOT SCORED (false is not the number 0); v3 held (Python reads False == 0).
         K19 a partial end read, the only step-7 file in its window partial too: NOT SCORED under both.
         K20 a partial end read, the step-7 read in its window complete and MOVED: NOT SCORED under both (v4: one departure recorded).
  KF     K4 end to end: reduce v4 + score_e184_v3.py: every rule NOT SCORED; reduce v3 + score v3 on the same raw tree scores the arm.
  K1F    K1 end to end: reduce v4 + score v3: the arm scores as V1 (the same verdicts), and the md names the departure.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
S = os.path.abspath(sys.argv[1])
PY = sys.executable
T0 = 1794500000
PST = datetime.timezone(datetime.timedelta(hours=-8))
results = []

import reduce_e184_v3 as r3m  # noqa: E402
import reduce_e184_v4 as r4m  # noqa: E402


def check(name, ok, detail):
    results.append(bool(ok))
    print("%-4s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def run(args):
    r = subprocess.run([PY, "-B"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("%s failed: %s" % (args[0], r.stderr[-800:]))
    return r.stdout


def fake(name, arm, fake_args):
    d = os.path.join(S, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    raw = os.path.join(d, "raw")
    run([os.path.join(HERE, "fake_card_e184_v2.py"), raw, "--arm", arm] + fake_args)
    return raw


def reduce(raw, arm, ver, out, t0=None):
    args = [os.path.join(HERE, "reduce_e184_%s.py" % ver), raw, "--arm", arm] + (["--t0", str(t0)] if t0 else [])
    open(out, "w").write(run(args))
    return json.load(open(out))


def score(red_file, arm, out):
    run([os.path.join(HERE, "score_e184_v3.py"), "--out", out, "--" + arm.lower(), red_file])
    return json.load(open(os.path.join(out, "scored-e184-v3.json")))["arm_" + arm], open(os.path.join(out, "scored-e184-v3.md")).read()


def verdicts(a):
    out = {}
    for k, v in sorted(a.items()):
        if isinstance(v, dict) and "verdict" in v:
            out[k] = v["verdict"] + ("/" + v["meter"] if "meter" in v else "")
        elif isinstance(v, dict) and k == "E184-T":
            for kk, vv in sorted(v.items()):
                out["%s %s" % (k, kk)] = vv["verdict"]
    return out


def iso(ep):
    return datetime.datetime.fromtimestamp(ep, PST).isoformat()


GOOD = {"S": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "synthetic": True},
        "B": {"tdp_w": 40, "temp_threshold_c": 70, "minion_mhz": 600, "synthetic": True}}
TIMES = {"S": (T0 + 40, T0 + 7800), "B": (T0 + 30, T0 + 1400)}


def gcase(name, arm, base_raw, edits):
    """a copy of base_raw's logs (the passes linked, not copied), each read's attempt recorded, changed by edits: [(op, *args)]"""
    card = "aifoundry3" if arm == "S" else "aifoundry1-c1"
    d = os.path.join(S, "G", name)
    if os.path.exists(d):
        shutil.rmtree(d)
    raw = os.path.join(d, "raw")
    os.makedirs(os.path.join(raw, card))
    for sub in ("e184", "e184-smoke", "e184-stoptest"):
        if os.path.isdir(os.path.join(base_raw, card, sub)):
            os.symlink(os.path.join(base_raw, card, sub), os.path.join(raw, card, sub))
    logs = os.path.join(raw, card, "logs")
    shutil.copytree(os.path.join(base_raw, card, "logs"), logs)
    for edge, ep in zip(("start", "end"), TIMES[arm]):
        open(os.path.join(logs, "config-%s-t%d-%s.json.time" % (arm, T0, edge)), "w").write(iso(ep) + "\n")
    for op in edits:
        f = os.path.join(logs, "config-%s-t%d-%s.json" % (arm, T0, op[1])) if op[0] in ("empty", "absent", "set", "notime") else None
        if op[0] == "empty":
            open(f, "w").close()
        elif op[0] == "absent":
            os.remove(f)
            os.remove(f + ".time")
        elif op[0] == "notime":
            os.remove(f + ".time")
        elif op[0] == "set":
            json.dump(op[2], open(f, "w"))
        elif op[0] == "step7":
            json.dump(op[2], open(os.path.join(logs, "config-%s-step7-%d.json" % (arm, op[1])), "w"))
    return raw


def both(raw, arm):
    return r3m.session_gate(raw, arm, T0), r4m.session_gate(raw, arm, T0)


def brief(g):
    return "gate %s, %d departure(s), from %s%s" % (g["gate_ok"], len(g["departures"]), json.dumps(g["config_from"], sort_keys=True),
                                                    ("; " + "; ".join(g["reasons"])[:230]) if g["reasons"] else "")


# ---- Q: whole sessions where A4 changes nothing ----------------------------------------------------------------------------------------
NEWKEYS = {"config_status"}


def strip(red):
    out = json.loads(json.dumps(red))
    out.pop("reducer", None)
    s = out.get("session", {})
    s.pop("gate", None)
    for k in NEWKEYS:
        s.pop(k, None)
    for x in s.get("step7_reads") or []:
        x.pop("status", None)
    n = len(s.get("reasons") or [])
    s["reasons"] = n
    return out


raws = {}
for name, arm, fa, want_gate in (("Q1-V1", "S", ["--seed", "11"], True), ("Q2-B1", "B", ["--seed", "21"], True),
                                 ("Q3-V1-end-moved", "S", ["--seed", "11", "--config-end-tdp", "65"], False),
                                 ("Q4-B1-end-41", "B", ["--seed", "21", "--config-end-tdp", "41"], False),
                                 ("Q5-V1-smoke-stale", "S", ["--seed", "11", "--smoke-fail", "--stale-log"], False)):
    raw = fake(name, arm, fa)
    raws[name] = raw
    d = os.path.join(S, name)
    red3 = reduce(raw, arm, "v3", os.path.join(d, "red-v3.json"))
    red4 = reduce(raw, arm, "v4", os.path.join(d, "red-v4.json"))
    same = strip(red3) == strip(red4)
    g3, g4 = red3["session"], red4["session"]
    check("%s v4's output is v3's (but the names, the new status fields and the reasons' words), the gate %s" % (
        name, "holds" if want_gate else "does not hold"),
        same and g3["gate_ok"] == g4["gate_ok"] == want_gate and len(g3["reasons"]) == len(g4["reasons"]),
        "same %s; v3 %s; v4 %s" % (same, brief(g3), brief(g4)))
S_RAW, B_RAW = raws["Q1-V1"], raws["Q2-B1"]
end_s, end_b = TIMES["S"][1], TIMES["B"][1]
G, GB = GOOD["S"], GOOD["B"]

# ---- G: A3-3's own cases, read the same under v4 ---------------------------------------------------------------------------------------
for name, arm, edits, want in (
        ("G0", "S", [("step7", end_s + 120, G)], (True, 0)),
        ("G1", "S", [("empty", "end"), ("step7", end_s + 120, G)], (True, 1)),
        ("G2", "S", [("empty", "end")], (False, 0)),
        ("G3", "S", [("empty", "end"), ("step7", end_s + 2400, G)], (False, 0)),
        ("G4", "S", [("empty", "end"), ("step7", T0 - 300, G)], (False, 0)),
        ("G5", "S", [("set", "end", dict(G, tdp_w=65)), ("step7", end_s + 120, G)], (False, 0)),
        ("G6", "S", [("empty", "end"), ("step7", end_s + 120, dict(G, tdp_w=65))], (False, 1)),
        ("G7", "S", [("empty", "start"), ("step7", T0 - 7200, G), ("step7", T0 - 1200, G), ("step7", T0 - 600, G)], (True, 1)),
        ("G8", "S", [("absent", "end")], (False, 0)),
        ("G9", "S", [("set", "end", {"dry": True}), ("step7", end_s + 120, G)], (False, 0)),
        ("G10a", "B", [("empty", "end"), ("step7", end_b + 90, dict(GB, tdp_w=41))], (False, 1)),
        ("G10b", "B", [("empty", "end"), ("step7", end_b + 90, GB)], (True, 1)),
        ("G11", "S", [("empty", "end"), ("step7", end_s + 120, G), ("step7", end_s + 600, dict(G, tdp_w=65))], (True, 1))):
    g3, g4 = both(gcase(name, arm, S_RAW if arm == "S" else B_RAW, edits), arm)
    frm4 = {e: (v or "").replace(" (A3-3, A4)", " (A3-3)") or None for e, v in g4["config_from"].items()}   # v4 adds A4 to the label
    same = (g3["gate_ok"], len(g3["departures"]), g3["config_from"]) == (g4["gate_ok"], len(g4["departures"]), frm4)
    check("%s A3-3's case reads the same under v4 (gate %s, %d departure(s), each edge's read from the same file)" % (name, want[0], want[1]),
          same and (g4["gate_ok"], len(g4["departures"])) == want, "v4 %s" % brief(g4))

# ---- K: A4's cases ---------------------------------------------------------------------------------------------------------------------
K = [
    ("K1", "S", [("set", "start", dict(G, tdp_w=None)), ("step7", T0 - 600, G)], (True, 1), (False, 0),
     "a partial start read (tdp_w null) beside a complete step-7 read: MISSING, replaced"),
    ("K2", "S", [("set", "start", {"tdp_w": 0, "temp_threshold_c": 65, "synthetic": True}), ("step7", T0 - 600, G)], (True, 1), (False, 0),
     "a start read without minion_mhz (a failed clock GET) beside a complete step-7 read: MISSING, replaced"),
    ("K3", "S", [("set", "start", {})], (False, 0), (True, 0), "(H3) an empty {} start read, no step-7 read: MISSING, not replaced"),
    ("K3b", "S", [("set", "start", {}), ("step7", T0 - 600, G)], (True, 1), (True, 0),
     "an empty {} start read beside a complete step-7 read: MISSING, replaced"),
    ("K4", "S", [("set", "start", {}), ("set", "end", dict(G, tdp_w=65))], (False, 0), (True, 0),
     "(H4) start {} and the end read MOVED (TDP 65 W): the moved read is fatal"),
    ("K5", "S", [("set", "start", dict(G, tdp_w=25)), ("set", "end", {})], (False, 0), (True, 0),
     "(H5) the start read MOVED (TDP 25 W) and the end {}: the moved read is fatal"),
    ("K6", "B", [("set", "start", dict(GB, tdp_w=None, temp_threshold_c=None)), ("set", "end", dict(GB, tdp_w=None, temp_threshold_c=None))],
     (False, 0), (True, 0), "(H6) arm B, TDP and threshold null at both ends, no step-7 read: both MISSING, not replaced"),
    ("K6b", "B", [("set", "start", dict(GB, tdp_w=None, temp_threshold_c=None)), ("set", "end", dict(GB, tdp_w=None, temp_threshold_c=None)),
                  ("step7", T0 - 300, GB), ("step7", end_b + 90, GB)], (True, 2), (True, 0),
     "arm B, both reads null, a complete step-7 read in each window: both replaced, the same TDP and threshold"),
    ("K6c", "B", [("set", "start", dict(GB, tdp_w=None)), ("step7", T0 - 300, GB), ("set", "end", dict(GB, tdp_w=41))], (False, 1), (False, 0),
     "arm B, the start read's replacement TDP 40 W, the end's own TDP 41 W: not the same"),
    ("K15", "S", [("empty", "end"), ("step7", end_s + 120, {})], (False, 0), (True, 1),
     "(H15) the end read empty, the only step-7 file in its window {}: not a read, not replaced"),
    ("K16", "S", [("empty", "start"), ("step7", T0 - 1200, G), ("step7", T0 - 600, dict(G, tdp_w=None))], (True, 1), (False, 1),
     "(H16) the start read empty; the older step-7 read complete, the newer partial: the newest COMPLETE one is used"),
    ("K17", "S", [("set", "start", dict(G, tdp_w=None)), ("notime", "start"), ("step7", T0 - 600, G)], (False, 0), (False, 0),
     "a partial start read with no record of its attempt: never replaced"),
    ("K18", "S", [("set", "start", dict(G, tdp_w=False))], (False, 0), (True, 0),
     "the start read's tdp_w is JSON false: not the number 0, so not as registered (moved)"),
    ("K19", "S", [("set", "end", dict(G, temp_threshold_c=None)), ("step7", end_s + 120, dict(G, minion_mhz=None))], (False, 0), (False, 0),
     "a partial end read, the only step-7 file in its window partial too: not replaced"),
    ("K20", "S", [("set", "end", dict(G, temp_threshold_c=None)), ("step7", end_s + 120, dict(G, tdp_w=65))], (False, 1), (False, 0),
     "a partial end read, its window's step-7 read complete and MOVED: replaced, then fatal"),
]
for name, arm, edits, w4, w3, why in K:
    g3, g4 = both(gcase(name, arm, S_RAW if arm == "S" else B_RAW, edits), arm)
    got4, got3 = (g4["gate_ok"], len(g4["departures"])), (g3["gate_ok"], len(g3["departures"]))
    check("%s %s: v4 gate %s with %d departure(s); v3 gate %s with %d" % (name, why, w4[0], w4[1], w3[0], w3[1]),
          got4 == w4 and got3 == w3, "v4 %s | v3 %s" % (brief(g4), brief(g3)))
    if name == "K16":
        check("K16b the step-7 read v4 used is the older, complete one",
              ("config-S-step7-%d.json" % (T0 - 1200)) in (g4["config_from"]["start"] or ""), "start from %s" % g4["config_from"]["start"])
    if name == "K1":
        st = g4.get("config_status", {})
        check("K1b config_status names the failed read", st.get("start", "").startswith("failed (no value for tdp_w)") and st.get("end") == "complete",
              json.dumps(st, sort_keys=True))

# ---- end to end through score v3 -------------------------------------------------------------------------------------------------------
v1d = os.path.join(S, "Q1-V1")
s_v1, _ = score(os.path.join(v1d, "red-v4.json"), "S", os.path.join(v1d, "scored-v4"))
raw = gcase("KF", "S", S_RAW, [("set", "start", {}), ("set", "end", dict(G, tdp_w=65))])
d = os.path.join(S, "G", "KF")
reduce(raw, "S", "v4", os.path.join(d, "red-v4.json"), T0)
reduce(raw, "S", "v3", os.path.join(d, "red-v3.json"), T0)
a4, m4 = score(os.path.join(d, "red-v4.json"), "S", os.path.join(d, "scored-v4"))
a3, _ = score(os.path.join(d, "red-v3.json"), "S", os.path.join(d, "scored-v3"))
v4v, v3v = verdicts(a4), verdicts(a3)
check("KF K4 end to end: reduce v4 + score v3 reads every rule NOT SCORED; reduce v3 + score v3 scores the arm (the fault)",
      all(v == "NOT SCORED" for v in v4v.values()) and v3v.get("E184-L") != "NOT SCORED" and "DOES NOT HOLD" in m4,
      "v4: %s | v3: L %s, P %s" % (json.dumps(sorted(set(v4v.values()))), v3v.get("E184-L"), v3v.get("E184-P")))
raw = gcase("K1F", "S", S_RAW, [("set", "start", dict(G, tdp_w=None)), ("step7", T0 - 600, G)])
d = os.path.join(S, "G", "K1F")
reduce(raw, "S", "v4", os.path.join(d, "red-v4.json"), T0)
a1, m1 = score(os.path.join(d, "red-v4.json"), "S", os.path.join(d, "scored-v4"))
check("K1F K1 end to end: reduce v4 + score v3 scores the arm as V1 (the same verdicts) and the md names the departure",
      verdicts(a1) == verdicts(s_v1) and "departure:" in m1 and "A4" in m1,
      "L %s, P %s, C %s; V1's L %s" % (verdicts(a1).get("E184-L"), verdicts(a1).get("E184-P"), verdicts(a1).get("E184-C"),
                                        verdicts(s_v1).get("E184-L")))

print("SELFTEST-REDUCE-E184-V4: %d of %d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
