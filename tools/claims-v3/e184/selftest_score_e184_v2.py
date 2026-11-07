#!/usr/bin/env python3
"""E184's scorer self-test, v2 (kit note 1, KIT.md.dated-note-1.md section 6): synthetic sessions with a stated truth, in the box's file
layout, through fake_card_e184_v2.py, reduce_e184_v2.py and score_e184_v2.py, each run as a subprocess. Desk only. selftest_score_e184.py
(v1, which stays as committed, with its committed log) still tests v1's readers on the lab's committed card data; this file tests what
dated amendment A2 and kit note 1 change, and that the rest reads as v1 read it.

    /usr/bin/python3 -B tools/claims-v3/e184/selftest_score_e184_v2.py <scratch dir> > tools/claims-v3/e184/logs/selftest-score-e184-v2.txt

  E0 fake_card_e184_v2.py with no new option writes v1's telemetry and runs, record for record (seed 11, both arms);
  V1 linear: N NULL, L LINEAR (the registered R governs), J NONE SEEN, P LINEAR and METER EXCLUDED, C (A2-1) NONE SEEN, K inside, the
     session gate holds, no pass set aside;  V2 small steps at 0.8: L and P LOW, P EXCLUDED, and A2-3's words follow the rail's own R
     (the synthetic rail is linear in the minions but filtered over 1.06 s between processes, so its R is not resolved and the words read
     "not separated");  V3 small steps at E178's 0.29: P METER NOT EXCLUDED, and the smoke gate holds (kit note 1's band; v1's gate read
     this session NO-GO);  V4 a one-code step where the true level passes 33.6 W: C SEEN, its break within 0.15 W, "near code 1024";
  V5 a 0.10 W jump from n = 48: J SEEN;  V6 one missing code at 33.624 W, the scan's reference position (the registration's dither model):
     A2-1 NONE SEEN, beside the registered statistic's reading of the same session;  V7 a protocol offset of +25 mW in every B block:
     E184-N OFFSET, so the null-corrected R governs E184-L (A2-2), and the registered R reads HIGH;
  V8 partial dips at 0.3% of refreshes: A2-5 sets aside about the number planted, and N, L read as V1;
  V9 pass 18411's block.json says "others": the pass is set aside, L is scored on 18410 and 18412;  V10 a busy sample of 18414 at
     800 MHz: 18414 set aside;  V11 the session's smoke gate failed: every arm-S rule NOT SCORED;  V12 the end config read moved
     (TDP 65 W): NOT SCORED;  V13 a stale session log (an earlier T0, its smoke failed) beside the real one: the newest is read, and
     --t0 names it;
  B1 card 1 two-phase: M SUPPORTED, T PASS; E184-G's count equals the generator's own glitches, counted again here from the raw files;
  B2 card 1's end config read moved: arm B NOT SCORED;
  ID score_e184_v2's scan_fit_a2 and delta_ratio_nc are power_e184_a2.py's text, and give its numbers.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import gzip
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
results = []


def check(name, ok, detail):
    results.append(bool(ok))
    print("%-4s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def run(args):
    r = subprocess.run([PY, "-B"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("%s failed: %s" % (args[0], r.stderr[-800:]))
    return r.stdout


def session(name, arm, fake_args, red_args=(), v1=False):
    d = os.path.join(S, name)
    raw = os.path.join(d, "raw")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    run([os.path.join(HERE, "fake_card_e184.py" if v1 else "fake_card_e184_v2.py"), raw, "--arm", arm] + fake_args)
    if v1:
        return raw
    rf = os.path.join(d, "red-%s.json" % arm.lower())
    open(rf, "w").write(run([os.path.join(HERE, "reduce_e184_v2.py"), raw, "--arm", arm] + list(red_args)))
    return rf


def score(name, s=None, b=None):
    out = os.path.join(S, name, "scored")
    args = [os.path.join(HERE, "score_e184_v2.py"), "--out", out]
    if s:
        args += ["--s", s]
    if b:
        args += ["--b", b]
    run(args)
    return json.load(open(os.path.join(out, "scored-e184-v2.json")))


def v(sc, arm, rule):
    a = sc["arm_" + arm]
    return a[rule]["verdict"] if a and rule in a else None


def rows(path):
    with gzip.open(path, "rt") as f:
        return f.read()


# ---- E0 ---------------------------------------------------------------------------------------------------------------------------------
same, nfiles = True, 0
for arm, seed in (("S", "11"), ("B", "21")):
    r1 = session("E0v1" + arm, arm, ["--seed", seed], v1=True)
    session("E0v2" + arm, arm, ["--seed", seed])
    r2 = os.path.join(S, "E0v2" + arm, "raw")
    for top, _, files in os.walk(r1):
        for f in files:
            p1 = os.path.join(top, f)
            p2 = os.path.join(r2, os.path.relpath(p1, r1))
            nfiles += 1
            a = rows(p1) if f.endswith(".gz") else open(p1).read()
            b = rows(p2) if f.endswith(".gz") else open(p2).read()
            same = same and a == b
check("E0 v2's generator writes v1's files with no new option", same and nfiles > 50, "%d files compared (gz by content), same %s" % (nfiles, same))

# ---- arm S ------------------------------------------------------------------------------------------------------------------------------
s1 = score("V1", s=session("V1", "S", ["--seed", "11"]))
a = s1["arm_S"]
check("V1 linear", v(s1, "S", "E184-N") == "NULL" and v(s1, "S", "E184-L") == "LINEAR" and v(s1, "S", "E184-J") == "NONE SEEN"
      and v(s1, "S", "E184-P") == "LINEAR" and a["E184-P"]["meter"] == "METER EXCLUDED" and v(s1, "S", "E184-C") == "NONE SEEN"
      and a["reported"]["E184-K"]["inside"] and a["session"]["gate_ok"] and not a["set_aside_passes"]
      and a["E184-L"]["a2"]["governing_rule"] == "the registered R",
      "N %s, L %s (%s; nc %s), J %s, P %s %s, C %s T %s (t* %s), K %s mW, gate %s" % (
          v(s1, "S", "E184-N"), v(s1, "S", "E184-L"), a["E184-L"]["a2"]["governing_rule"], a["E184-L"]["a2"]["null_corrected"]["verdict"],
          v(s1, "S", "E184-J"), v(s1, "S", "E184-P"), a["E184-P"]["meter"], v(s1, "S", "E184-C"), a["E184-C"]["max_abs_t"], a["E184-C"]["t_crit"],
          a["reported"]["E184-K"]["b_large_mw_per_minion"], a["session"]["gate_ok"]))
s2 = score("V2", s=session("V2", "S", ["--seed", "12", "--gain-small", "0.8"]))
w2 = s2["arm_S"]["E184-L"]["a2"]["words"]
rv2 = (s2["arm_S"]["E184-L"]["a2"].get("rail_R") or {}).get("verdict")
want2 = "the meter" if rv2 == "LINEAR" else ("the power" if rv2 == "LOW" else "not separated")
check("V2 small steps at 0.8", v(s2, "S", "E184-L") == "LOW" and v(s2, "S", "E184-P") == "LOW" and s2["arm_S"]["E184-P"]["meter"] == "METER EXCLUDED"
      and w2.startswith(want2), "L %s, P %s %s; the rail's own R %s, so A2-3's words must begin '%s': %s" % (
          v(s2, "S", "E184-L"), v(s2, "S", "E184-P"), s2["arm_S"]["E184-P"]["meter"], s2["arm_S"]["E184-L"]["a2"].get("rail_R"), want2, w2))
s3 = score("V3", s=session("V3", "S", ["--seed", "13", "--gain-small", "0.2865"]))
r3 = json.load(open(os.path.join(S, "V3", "red-s.json")))
check("V3 small steps at E178's 0.29", s3["arm_S"]["E184-P"]["meter"] == "METER NOT EXCLUDED" and r3["session"]["gate_ok"]
      and r3["session"]["desk_smoke"].startswith("SMOKE GO"),
      "P %s %s; the smoke at the desk: %s" % (v(s3, "S", "E184-P"), s3["arm_S"]["E184-P"]["meter"], r3["session"]["desk_smoke"][:60]))
s4 = score("V4", s=session("V4", "S", ["--seed", "14", "--carry-w", "33.6", "--carry-d", "0.0328"]))
cc = s4["arm_S"]["E184-C"]
check("V4 a one-code step at 33.6 W", cc["verdict"] == "SEEN" and abs(cc["best_break_board_w"] - 33.6) <= 0.15 and cc["reading"] == "a step near code 1024",
      "C %s T %s (t* %s), break %s W, d %s W, %s" % (cc["verdict"], cc["max_abs_t"], cc["t_crit"], cc["best_break_board_w"], cc["best_d_w"], cc["reading"]))
s5 = score("V5", s=session("V5", "S", ["--seed", "15", "--jump-n", "48", "--jump-w", "0.10"]))
check("V5 a 0.10 W jump from n = 48", v(s5, "S", "E184-J") == "SEEN", "J %s, max |z| %.2f" % (v(s5, "S", "E184-J"), s5["arm_S"]["E184-J"]["max_abs_z"]))
s6 = score("V6", s=session("V6", "S", ["--seed", "16", "--dnl-w", "33.624", "--dnl-sign", "1"]))
c6 = s6["arm_S"]["E184-C"]
check("V6 one missing code at the reference's position", c6["verdict"] == "NONE SEEN",
      "A2-1 %s T %s (t* %s); the registered statistic, reported: %s T %s; the reference's own null %s" % (
          c6["verdict"], c6["max_abs_t"], c6["t_crit"], c6["reported_registered_statistic"]["verdict"],
          c6["reported_registered_statistic"]["max_abs_t"], c6["reference_null"]))
s7 = score("V7", s=session("V7", "S", ["--seed", "17", "--offset-w", "0.025"]))
a7 = s7["arm_S"]["E184-L"]["a2"]
check("V7 a +25 mW protocol offset", v(s7, "S", "E184-N") == "OFFSET" and a7["governing_rule"].startswith("the null-corrected")
      and a7["registered_R_verdict"] == "HIGH" and v(s7, "S", "E184-L") == a7["null_corrected"]["verdict"],
      "N %s %s; registered R %s %s; governing: %s -> %s (nc R %s)" % (v(s7, "S", "E184-N"), s7["arm_S"]["E184-N"]["mean_w"], a7["registered_R_verdict"],
                                                                     a7["registered_R"], a7["governing_rule"], v(s7, "S", "E184-L"), a7["null_corrected"]["R"]))
red8 = session("V8", "S", ["--seed", "18", "--dip-rate", "0.003"])
s8 = score("V8", s=red8)
r8 = json.load(open(red8))
check("V8 partial dips at 0.3% of refreshes", r8["a2_5_set_aside"] > 0 and v(s8, "S", "E184-N") == "NULL" and v(s8, "S", "E184-L") == "LINEAR",
      "A2-5 set aside %d refreshes; N %s, L %s, P %s" % (r8["a2_5_set_aside"], v(s8, "S", "E184-N"), v(s8, "S", "E184-L"), v(s8, "S", "E184-P")))
red9 = session("V9", "S", ["--seed", "11", "--block-status", "18411:others"])
s9 = score("V9", s=red9)
r9 = json.load(open(red9))
check("V9 a pass another user's process stopped", "18411" in r9["set_aside_passes"] and "18411" not in r9["passes"]
      and s9["arm_S"]["E184-L"]["quads"] < s1["arm_S"]["E184-L"]["quads"],
      "set aside %s; L %s on %d quads (V1 %d)" % (json.dumps(r9["set_aside_passes"]), v(s9, "S", "E184-L"), s9["arm_S"]["E184-L"]["quads"],
                                                  s1["arm_S"]["E184-L"]["quads"]))
red10 = session("V10", "S", ["--seed", "11", "--mhz-off", "18414"])
r10 = json.load(open(red10))
check("V10 a busy sample at 800 MHz", "18414" in r10["set_aside_passes"] and "800" not in json.dumps(r10["passes"].get("18414", {})),
      "set aside %s" % json.dumps({p: x["why"] for p, x in r10["set_aside_passes"].items()}))
s11 = score("V11", s=session("V11", "S", ["--seed", "11", "--smoke-fail"]))
check("V11 the smoke gate failed in the session's log", all(v(s11, "S", r) == "NOT SCORED" for r in ("E184-N", "E184-L", "E184-J", "E184-P", "E184-C")),
      "every rule %s: %s" % (v(s11, "S", "E184-L"), s11["arm_S"]["E184-L"]["why"][:120]))
s12 = score("V12", s=session("V12", "S", ["--seed", "11", "--config-end-tdp", "65"]))
check("V12 the end config read moved", v(s12, "S", "E184-L") == "NOT SCORED" and "end config" in s12["arm_S"]["E184-L"]["why"],
      s12["arm_S"]["E184-L"]["why"][:160])
red13 = session("V13", "S", ["--seed", "11", "--stale-log"])
r13 = json.load(open(red13))
red13b = os.path.join(S, "V13", "red-s-t0.json")
open(red13b, "w").write(run([os.path.join(HERE, "reduce_e184_v2.py"), os.path.join(S, "V13", "raw"), "--arm", "S", "--t0", "1794500000"]))
r13b = json.load(open(red13b))
red13c = os.path.join(S, "V13", "red-s-stale.json")
open(red13c, "w").write(run([os.path.join(HERE, "reduce_e184_v2.py"), os.path.join(S, "V13", "raw"), "--arm", "S", "--t0", "1794496400"]))
r13c = json.load(open(red13c))
check("V13 a stale session log beside the real one", r13["session"]["t0"] == 1794500000 and r13["session"]["gate_ok"] and r13b["session"]["gate_ok"]
      and not r13c["session"]["gate_ok"],
      "logs %s; newest read T0 %s gate %s; --t0 the real one: gate %s; --t0 the stale one: gate %s (%s)" % (
          r13["session"]["session_logs_found"], r13["session"]["t0"], r13["session"]["gate_ok"], r13b["session"]["gate_ok"],
          r13c["session"]["gate_ok"], "; ".join(r13c["session"]["reasons"])[:100]))

# ---- arm B ------------------------------------------------------------------------------------------------------------------------------
redb = session("B1", "B", ["--seed", "21"])
b1 = score("B1", b=redb)
bb = b1["arm_B"]
own = 0
nsamp = 0
for top, _, files in os.walk(os.path.join(S, "B1", "raw", "aifoundry1-c1")):
    if os.path.basename(top) == "p18441" or "stoptest" in top:
        continue
    if "telemetry.jsonl.gz" in files:
        for line in gzip.open(os.path.join(top, "telemetry.jsonl.gz"), "rt"):
            d = json.loads(line)
            mw = d["sp"]["minion_w"]
            nsamp += 1
            own += 1 if mw[0] == mw[2] else 0
g = bb["reported"]["E184-G"]
check("B1 two-phase, and E184-G's count", bb["E184-M"]["verdict"] == "SUPPORTED" and all(x["verdict"] == "PASS" for x in bb["E184-T"].values())
      and round(own / nsamp, 6) == round(g["rate"], 6) and nsamp == g["samples"],
      "M %s, T %s; G %s of %d samples: the generator's own count %d of %d (a draw of %.3f%% against its 0.087%%)" % (
          bb["E184-M"]["verdict"], [x["verdict"] for x in bb["E184-T"].values()], g["rate"], g["samples"], own, nsamp, 100.0 * own / nsamp))
b2 = score("B2", b=session("B2", "B", ["--seed", "21", "--config-end-tdp", "55"]))
check("B2 card 1's end config read moved", v(b2, "B", "E184-M") == "NOT SCORED", b2["arm_B"]["E184-M"]["why"][:160])

# ---- the amended statistics are power_e184_a2.py's ----------------------------------------------------------------------------------------
import score_e184_v2 as sc  # noqa: E402
src = open(os.path.join(HERE, "power_e184_a2.py")).read()
segs = {n.name: ast.get_source_segment(src, n) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name in ("scan_fit_a2", "delta_ratio_nc")}
qs = [{"n": n, "y": 0.008256 * (n - 144) + ((-1) ** k) * 0.003} for n in range(0, 289, 12) for k in range(4)]
fa = sc.A2["scan_fit_a2"](qs, 144)
lv = {0: [0.001, -0.002, 0.003], 3: [0.026, 0.021, 0.027], 19: [0.16, 0.15, 0.158], 121: [0.99, 1.01, 1.0]}
dn = sc.A2["delta_ratio_nc"](lv, [3, 19], [121])
p2 = json.load(open(os.path.join(HERE, "power-e184-a2.json")))
check("ID the scorer's A2 statistics are power_e184_a2.py's", len(segs) == 2 and sc.T_A2 == p2["C"]["t_crit_a2"] and fa["best"] is not None and dn[0] > 0,
      "sources sha256 %s; t*_A2 %s; a test scan T %.4f; a test nc R %.6f" % (
          hashlib.sha256((segs.get("scan_fit_a2", "") + segs.get("delta_ratio_nc", "")).encode()).hexdigest()[:16], sc.T_A2, fa["max_abs_t"], dn[0]))

print("SELFTEST-SCORE-E184-V2: %d of %d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
