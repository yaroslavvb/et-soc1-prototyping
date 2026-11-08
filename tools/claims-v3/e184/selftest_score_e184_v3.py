#!/usr/bin/env python3
"""E184's scorer self-test, v3 (kit note 2, KIT.md.dated-note-2.md section 5): what kit note 2 and dated amendment A3 change, and that
nothing else reads differently. Synthetic sessions with a stated truth (fake_card_e184_v2.py, unchanged), in the box's file layout, through
reduce_e184_v2.py + score_e184_v2.py and reduce_e184_v3.py + score_e184_v3.py, each run as a subprocess. Desk only.
selftest_score_e184.py (v1) and selftest_score_e184_v2.py (v2) stay as committed, with their committed logs.

    /usr/bin/python3 -B tools/claims-v3/e184/selftest_score_e184_v3.py <scratch dir> > tools/claims-v3/e184/logs/selftest-score-e184-v3.txt

  Q   v2's synthetic cases (V1-V13 of arm S, B1-B2 of arm B, each with v2's seeds and options), through both pipelines: every verdict,
      E184-P's meter and the session gate read the same under v3 as under v2 (one check per case).
  F1  (the verifier's fault 1) V7's session (+25 mW in every B block): E184-L's and E184-P's verdicts are the null-corrected R's, and v3 puts
      that reading at the top level (governing_R and governing_ci95 equal the null-corrected R and interval), E184-P's METER EXCLUDED is read
      on governing_ci95's lower end, the registered R and interval are labelled (and read HIGH), no bare "R" or "ci95" is written, and the
      md prints the governing interval on the verdict's line and the registered one on its own labelled line.
  F1b the branch where the interval decides the meter: +40 mW in every B block and small steps at E178's 0.29: part P's null reads OFFSET,
      the null-corrected R governs and reads METER NOT EXCLUDED, while the registered interval's lower end lies above 0.5 (alone it would
      have read EXCLUDED).
  F2  (fault 2; A3-4) V1's reduced file with 15 of the 24 scan levels besides the reference cut to 2 quads: v3 leaves them out and E184-C is
      NOT SCORED (9 levels), where v2 scored all 24;  F2b 3 levels cut to 3 quads: v3 scores 21 levels, names the 3 left out, and fits the
      quads of the 21 only.
  G0-G11 (fault 3; A3-3) the session gate on V1's arm-S session (and B1's arm-B session for G10), its logs copied and changed: G0 every read
      present, a step-7 read after the session reported, never used; G1 the end read empty, a step-7 read 2 minutes after its attempt:
      the gate holds with one departure naming it, and the arm scores as V1; G2 the same with no step-7 read: NOT SCORED; G3 the only
      step-7 read 40 minutes after (outside 30): NOT SCORED; G4 a step-7 read only before T0: NOT SCORED (never the end's); G5 the end read
      MOVED (TDP 65 W) beside a good step-7 read: NOT SCORED; G6 the end read empty, the step-7 read moved: NOT SCORED; G7 the start read
      empty, step-7 reads 120 and 20 minutes and 10 minutes before T0 (the first outside 90): the 10-minute one is used; G8 the end read
      absent with no record of its attempt: NOT SCORED; G9 a dry read in the session's end file: NOT SCORED; G10 arm B's end read empty and
      the step-7 read's TDP differs from the start read's: NOT SCORED, the same TDP: holds; G11 two step-7 reads after (2 minutes, good;
      10 minutes, moved): the oldest is used.
  ID  score_e184_v3's A2 statistics are score_e184_v2's, which are power_e184_a2.py's text.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import hashlib
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
    return out


def score(red, arm, ver, out):
    args = [os.path.join(HERE, "score_e184_%s.py" % ver), "--out", out, "--" + arm.lower(), red]
    run(args)
    return json.load(open(os.path.join(out, "scored-e184-%s.json" % ver))), open(os.path.join(out, "scored-e184-%s.md" % ver)).read()


def both(name, raw, arm):
    d = os.path.join(S, name)
    r2 = reduce(raw, arm, "v2", os.path.join(d, "red-v2.json"))
    r3 = reduce(raw, arm, "v3", os.path.join(d, "red-v3.json"))
    s2, _ = score(r2, arm, "v2", os.path.join(d, "scored-v2"))
    s3, m3 = score(r3, arm, "v3", os.path.join(d, "scored-v3"))
    return s2["arm_" + arm], s3["arm_" + arm], m3, r3


def verdicts(a):
    out = {}
    for k, v in sorted(a.items()):
        if isinstance(v, dict) and "verdict" in v:
            out[k] = v["verdict"] + ("/" + v["meter"] if "meter" in v else "")
        elif isinstance(v, dict) and k == "E184-T":
            for kk, vv in sorted(v.items()):
                out["%s %s" % (k, kk)] = vv["verdict"]
    out["gate"] = (a.get("session") or {}).get("gate_ok")
    return out


# ---- Q: v2's cases read the same under v3 -------------------------------------------------------------------------------------------------
CASES = [("V1", "S", ["--seed", "11"]), ("V2", "S", ["--seed", "12", "--gain-small", "0.8"]), ("V3", "S", ["--seed", "13", "--gain-small", "0.2865"]),
         ("V4", "S", ["--seed", "14", "--carry-w", "33.6", "--carry-d", "0.0328"]), ("V5", "S", ["--seed", "15", "--jump-n", "48", "--jump-w", "0.10"]),
         ("V6", "S", ["--seed", "16", "--dnl-w", "33.624", "--dnl-sign", "1"]), ("V7", "S", ["--seed", "17", "--offset-w", "0.025"]),
         ("V8", "S", ["--seed", "18", "--dip-rate", "0.003"]), ("V9", "S", ["--seed", "11", "--block-status", "18411:others"]),
         ("V10", "S", ["--seed", "11", "--mhz-off", "18414"]), ("V11", "S", ["--seed", "11", "--smoke-fail"]),
         ("V12", "S", ["--seed", "11", "--config-end-tdp", "65"]), ("V13", "S", ["--seed", "11", "--stale-log"]),
         ("B1", "B", ["--seed", "21"]), ("B2", "B", ["--seed", "21", "--config-end-tdp", "55"])]
keep = {}
for name, arm, fa in CASES:
    raw = fake(name, arm, fa)
    a2, a3, m3, r3 = both(name, raw, arm)
    keep[name] = (raw, a2, a3, m3, r3)
    v2v, v3v = verdicts(a2), verdicts(a3)
    check("Q %s reads the same under v3" % name, v2v == v3v, json.dumps(v3v, sort_keys=True)[:260])

# ---- F1: the governing reading at the top level (V7) -------------------------------------------------------------------------------------
_, a2, a3, m3, _ = keep["V7"]
L, P = a3["E184-L"], a3["E184-P"]
ncL, ncP = L["a2"]["null_corrected"], P["a2"]["null_corrected"]
line_p = [ln for ln in m3.splitlines() if ln.startswith("- **E184-P**")]
line_pr = [ln for ln in m3.splitlines() if ln.startswith("  - registered R (reported, A2-2)")]
ok = (L["governing_rule"].startswith("the null-corrected") and P["governing_rule"].startswith("the null-corrected")
      and L["governing_R"] == ncL["R"] and L["governing_ci95"] == ncL["ci95"] and P["governing_R"] == ncP["R"] and P["governing_ci95"] == ncP["ci95"]
      and P["meter"] == "METER EXCLUDED" and P["governing_ci95"][0] > 0.5 and "R" not in L and "ci95" not in L and "R" not in P and "ci95" not in P
      and L["registered_verdict"] == "HIGH" and P["registered_R"] == a2["E184-P"]["R"] and P["registered_ci95"] == a2["E184-P"]["ci95"]
      and len(line_p) == 1 and json.dumps(P["governing_ci95"]) in line_p[0] and json.dumps(P["registered_ci95"]) not in line_p[0]
      and any(json.dumps(P["registered_ci95"]) in ln for ln in line_pr))
check("F1 V7: the governing reading at the top level, METER read on it", ok,
      "L %s by %s, governing R %s %s (registered %s %s reads %s); P %s %s, governing R %s %s, registered %s %s; md: %s" % (
          L["verdict"], L["governing_rule"][:24], L["governing_R"], L["governing_ci95"], L["registered_R"], L["registered_ci95"],
          L["registered_verdict"], P["verdict"], P["meter"], P["governing_R"], P["governing_ci95"], P["registered_R"], P["registered_ci95"],
          (line_p[0] if line_p else "")[:150]))
raw = fake("F1b", "S", ["--seed", "19", "--offset-w", "0.040", "--gain-small", "0.2865"])
a2, a3, m3, _ = both("F1b", raw, "S")
P = a3["E184-P"]
check("F1b +40 mW and small steps at 0.29: the governing interval decides the meter",
      P["governing_rule"].startswith("the null-corrected") and P["meter"] == "METER NOT EXCLUDED" and P["registered_ci95"][0] > 0.5
      and P["governing_ci95"][0] <= 0.5 and a2["E184-P"]["meter"] == P["meter"],
      "part P's own null %s; governing %s %s -> %s; the registered interval %s (alone: %s); v2's meter %s" % (
          P["a2"]["own_null"], P["governing_R"], P["governing_ci95"], P["meter"], P["registered_ci95"],
          "EXCLUDED" if P["registered_ci95"][0] > 0.5 else "NOT EXCLUDED", a2["E184-P"]["meter"]))

# ---- F2: A2-4's level filter on E184-C (A3-4) ------------------------------------------------------------------------------------------
_, _, a3v1, _, r3v1 = keep["V1"]
red = json.load(open(r3v1))
ref = json.load(open(os.path.join(HERE, "plan-e184.json")))["design"]["C"]["ref"]
scan = sorted(set(q["n"] for p in ("18417", "18418") for q in red["passes"][p]["quads"] if q["part"] == "C" and q["n"] != ref))


def cut(red, levels, keep_n):
    out = json.loads(json.dumps(red))
    seen = {}
    for p in ("18417", "18418"):
        qs = []
        for q in out["passes"][p]["quads"]:
            if q["part"] == "C" and q["n"] in levels:
                seen[q["n"]] = seen.get(q["n"], 0) + 1
                if seen[q["n"]] > keep_n:
                    continue
            qs.append(q)
        out["passes"][p]["quads"] = qs
    return out


for name, lv, kn, want in (("F2", scan[:15], 2, 9), ("F2b", scan[3:6], 3, 21)):
    d = os.path.join(S, name)
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "red-cut.json")
    cr = cut(red, set(lv), kn)
    json.dump(cr, open(f, "w"))
    kept_q = sum(1 for p in ("18417", "18418") for q in cr["passes"][p]["quads"] if q["part"] == "C" and q["n"] != ref and q["n"] not in lv)
    s2c, _ = score(f, "S", "v2", os.path.join(d, "scored-v2"))
    s3c, _ = score(f, "S", "v3", os.path.join(d, "scored-v3"))
    c2, c3 = s2c["arm_S"]["E184-C"], s3c["arm_S"]["E184-C"]
    left = c3.get("levels_left_out", {})
    if name == "F2":
        ok = c3["verdict"] == "NOT SCORED" and len(left) == 15 and c2["verdict"] != "NOT SCORED" and c2["scan_levels"] == 24
        det = "v3 %s (%s); left out %d levels; v2 %s on %d levels" % (c3["verdict"], c3.get("why", "")[:80], len(left), c2["verdict"], c2["scan_levels"])
    else:
        ok = (c3["verdict"] != "NOT SCORED" and c3["scan_levels"] == want and sorted(left) == sorted(str(n) for n in lv)
              and c3["quads"] == kept_q and c2["scan_levels"] == 24)
        det = "v3 %s on %d levels, %d quads (the kept levels' %d; V1 %d), left out %s; v2 %s on %d levels" % (
            c3["verdict"], c3["scan_levels"], c3["quads"], kept_q, a3v1["E184-C"]["quads"], json.dumps(left, sort_keys=True), c2["verdict"],
            c2["scan_levels"])
    check("%s %d scan levels cut to %d quads" % (name, len(lv), kn), ok, det)

# ---- G: A3-3's session gate --------------------------------------------------------------------------------------------------------------
import reduce_e184_v3 as r3m  # noqa: E402


def iso(ep):
    return datetime.datetime.fromtimestamp(ep, PST).isoformat()


GOOD = {"S": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "synthetic": True},
        "B": {"tdp_w": 40, "temp_threshold_c": 70, "minion_mhz": 600, "synthetic": True}}
TIMES = {"S": (T0 + 40, T0 + 7800), "B": (T0 + 30, T0 + 1400)}


def gcase(name, arm, base_raw, edits):
    """a copy of base_raw's logs (the passes linked, not copied), changed by edits: [(op, *args)]"""
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
        if op[0] == "empty":
            open(os.path.join(logs, "config-%s-t%d-%s.json" % (arm, T0, op[1])), "w").close()
        elif op[0] == "absent":
            os.remove(os.path.join(logs, "config-%s-t%d-%s.json" % (arm, T0, op[1])))
            os.remove(os.path.join(logs, "config-%s-t%d-%s.json.time" % (arm, T0, op[1])))
        elif op[0] == "set":
            json.dump(op[2], open(os.path.join(logs, "config-%s-t%d-%s.json" % (arm, T0, op[1])), "w"))
        elif op[0] == "step7":
            json.dump(op[2], open(os.path.join(logs, "config-%s-step7-%d.json" % (arm, op[1])), "w"))
    return raw


def gate(raw, arm):
    return r3m.session_gate(raw, arm, T0)


S_RAW, B_RAW = keep["V1"][0], keep["B1"][0]
end_s = TIMES["S"][1]
g = gate(gcase("G0", "S", S_RAW, [("step7", end_s + 120, GOOD["S"])]), "S")
check("G0 every read present: no departure; a step-7 read after is reported only", g["gate_ok"] and not g["departures"]
      and g["config_from"] == {"start": "the session's own read", "end": "the session's own read"}
      and (g.get("reported_step7_after_end") or {}).get("epoch") == end_s + 120,
      "gate %s, from %s, reported after-read %s" % (g["gate_ok"], json.dumps(g["config_from"], sort_keys=True), (g.get("reported_step7_after_end") or {}).get("file")))
raw = gcase("G1", "S", S_RAW, [("empty", "end"), ("step7", end_s + 120, GOOD["S"])])
g = gate(raw, "S")
d = os.path.join(S, "G", "G1")
s3g, m3g = score(reduce(raw, "S", "v3", os.path.join(d, "red-v3.json"), T0), "S", "v3", os.path.join(d, "scored-v3"))
r2g = reduce(raw, "S", "v2", os.path.join(d, "red-v2.json"), T0)
s2g, _ = score(r2g, "S", "v2", os.path.join(d, "scored-v2"))
same_as_v1 = {k: v for k, v in verdicts(s3g["arm_S"]).items()} == verdicts(keep["V1"][2])
check("G1 the end read empty, a step-7 read 2 minutes after its attempt: one departure, scored as V1",
      g["gate_ok"] and len(g["departures"]) == 1 and ("config-S-step7-%d.json" % (end_s + 120)) in g["departures"][0] and same_as_v1
      and "departure:" in m3g and verdicts(s2g["arm_S"])["E184-L"] == "NOT SCORED",
      "v3 gate %s, departure: %s; v3 verdicts as V1's: %s; v2 on the same session: L %s" % (
          g["gate_ok"], g["departures"][0][:150] if g["departures"] else None, same_as_v1, verdicts(s2g["arm_S"])["E184-L"]))
for name, edits, why in (("G2", [("empty", "end")], "no step-7 read"),
                         ("G3", [("empty", "end"), ("step7", end_s + 2400, GOOD["S"])], "the only step-7 read 40 minutes after (outside 30)"),
                         ("G4", [("empty", "end"), ("step7", T0 - 300, GOOD["S"])], "a step-7 read before T0 only"),
                         ("G5", [("set", "end", dict(GOOD["S"], tdp_w=65)), ("step7", end_s + 120, GOOD["S"])], "the end read moved, a good step-7 read after"),
                         ("G6", [("empty", "end"), ("step7", end_s + 120, dict(GOOD["S"], tdp_w=65))], "the step-7 read itself moved"),
                         ("G8", [("absent", "end")], "the end read absent, no record of its attempt"),
                         ("G9", [("set", "end", {"dry": True}), ("step7", end_s + 120, GOOD["S"])], "a dry read in the session's end file")):
    g = gate(gcase(name, "S", S_RAW, edits), "S")
    # G6 replaces the empty read and then fails the replacement's check: one departure is recorded, and the arm is still NOT SCORED
    want_dep = 1 if name == "G6" else 0
    check("%s %s: NOT SCORED" % (name, why), not g["gate_ok"] and len(g["departures"]) == want_dep,
          "%s%s" % ("; ".join(g["reasons"])[:200], (" [departure recorded: %s]" % g["departures"][0][:80]) if g["departures"] else ""))
g = gate(gcase("G7", "S", S_RAW, [("empty", "start"), ("step7", T0 - 7200, GOOD["S"]), ("step7", T0 - 1200, GOOD["S"]),
                                  ("step7", T0 - 600, GOOD["S"])]), "S")
check("G7 the start read empty: the newest step-7 read in the 90 minutes before T0", g["gate_ok"] and len(g["departures"]) == 1
      and ("config-S-step7-%d.json" % (T0 - 600)) in g["config_from"]["start"],
      "gate %s, start from %s" % (g["gate_ok"], g["config_from"]["start"]))
end_b = TIMES["B"][1]
g1 = gate(gcase("G10a", "B", B_RAW, [("empty", "end"), ("step7", end_b + 90, dict(GOOD["B"], tdp_w=41))]), "B")
g2 = gate(gcase("G10b", "B", B_RAW, [("empty", "end"), ("step7", end_b + 90, GOOD["B"])]), "B")
check("G10 arm B: a step-7 read whose TDP differs from the start read's NOT SCORED; the same TDP holds",
      not g1["gate_ok"] and g2["gate_ok"] and len(g2["departures"]) == 1,
      "different TDP: %s; the same: gate %s (%s)" % ("; ".join(g1["reasons"])[:120], g2["gate_ok"], g2["config_from"]["end"]))
g = gate(gcase("G11", "S", S_RAW, [("empty", "end"), ("step7", end_s + 120, GOOD["S"]), ("step7", end_s + 600, dict(GOOD["S"], tdp_w=65))]), "S")
check("G11 two step-7 reads after: the oldest is used", g["gate_ok"] and ("config-S-step7-%d.json" % (end_s + 120)) in g["config_from"]["end"],
      "gate %s, end from %s" % (g["gate_ok"], g["config_from"]["end"]))

# ---- ID ----------------------------------------------------------------------------------------------------------------------------------
import score_e184_v2 as sc2  # noqa: E402
import score_e184_v3 as sc3  # noqa: E402
src = open(os.path.join(HERE, "power_e184_a2.py")).read()
check("ID score_e184_v3's A2 statistics are score_e184_v2's (power_e184_a2.py's text)",
      sc3.A2 is sc2.A2 and sc3.T_A2 == json.load(open(os.path.join(HERE, "power-e184-a2.json")))["C"]["t_crit_a2"],
      "t*_A2 %s; power_e184_a2.py sha256 %s" % (sc3.T_A2, hashlib.sha256(src.encode()).hexdigest()[:16]))

print("SELFTEST-SCORE-E184-V3: %d of %d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
