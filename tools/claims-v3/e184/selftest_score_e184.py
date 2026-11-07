#!/usr/bin/env python3
"""E184's scorer self-test (the kit): synthetic sessions with a stated truth through the box's file layout, the reducer and the scorer,
and the readers on the lab's committed card data. Desk only.

    /usr/bin/python3 -B tools/claims-v3/e184/selftest_score_e184.py <scratch dir> <repository top> > logs/selftest-score-e184.txt

Synthetic (fake_card_e184.py, then reduce_e184.py, then score_e184.py, each as a subprocess, so the test runs the box's own files):
  S1 the meter linear: N NULL, L LINEAR, J NONE SEEN, P LINEAR and METER EXCLUDED, C NONE SEEN, K inside its band;
  S2 small steps read at 0.8: L LOW, P LOW, P still METER EXCLUDED;
  S3 small steps read at E178's 0.29: P METER NOT EXCLUDED;
  S4 a one-code step (32.8 mW) where the true level passes 33.6 W: C SEEN, its break within 0.15 W of 33.6 W;
  S5 a 0.10 W jump from n = 48 on: J SEEN;
  B1 card 1's SRAM statistic two-phase (H-MIX): M SUPPORTED, T PASS (the SRAM rail's rise and fall), R near 0.77-0.80, X near 0.718,
     G within three of its binomial sd of the generator's 0.087%;
  B2 a normal SRAM rail: M REFUTED;  B3 two-phase ratios that move 0.12 across the loads: M REFUTED;  B4 an SRAM filter of 1.0 s: T OUTSIDE;
  N1 no arm-B file: every arm-B rule NOT SCORED; N2 the operating point's passes missing: E184-P NOT SCORED, the rest scored.
Committed card data:
  R1 the reset-window reader (e184_common.reset_window_ratios) on the version-3 TEL block's card-1 reset windows reproduces Q150's
     committed medians (docs/reports/data/2026-11-06-q150-meter-checks/reset_minmax_bylevel.json, idle and busy, n and both ratios);
  R2 dated amendment A1's step-response reader (tau_a1_e184.fit_burst) on E58's card-1 bursts at the 100 ms sampler
     (docs/reports/data/2026-09-29-tau-aifoundry1-c1/p1-p3): the SRAM rail on the SRAM-dominated D bursts within 0.04 s of E58's
     committed 0.525 s (by kind D), the minion rail on the H and M bursts within 0.10 s of its 1.08 s.
Identity: score_e184's delta_ratio is the text of power_e184.py's, and gives the same numbers.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402

S = os.path.abspath(sys.argv[1])
TOP = os.path.abspath(sys.argv[2])
PY = sys.executable
results = []


def check(name, ok, detail):
    results.append(ok)
    print("%-4s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def run(args):
    r = subprocess.run([PY, "-B"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("%s failed: %s" % (args[0], r.stderr[-500:]))
    return r.stdout


def session(name, arm, fake_args, drop=()):
    d = os.path.join(S, name)
    raw = os.path.join(d, "raw")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    run([os.path.join(HERE, "fake_card_e184.py"), raw, "--arm", arm] + fake_args)
    for p in drop:
        shutil.rmtree(os.path.join(raw, "aifoundry3", "e184", "p%d" % p))
    rf = os.path.join(d, "red-%s.json" % arm.lower())
    open(rf, "w").write(run([os.path.join(HERE, "reduce_e184.py"), raw, "--arm", arm]))
    return rf


def score(name, s=None, b=None):
    out = os.path.join(S, name, "scored")
    args = [os.path.join(HERE, "score_e184.py"), "--out", out]
    if s:
        args += ["--s", s]
    if b:
        args += ["--b", b]
    run(args)
    return json.load(open(os.path.join(out, "scored-e184.json")))


def v(sc, arm, rule):
    a = sc["arm_" + arm]
    return a[rule]["verdict"] if a and rule in a else None


# ---- synthetic, arm S ------------------------------------------------------------------------------------------------------------------
s1 = score("S1", s=session("S1", "S", ["--seed", "11"]))
a = s1["arm_S"]
check("S1 linear", v(s1, "S", "E184-N") == "NULL" and v(s1, "S", "E184-L") == "LINEAR" and v(s1, "S", "E184-J") == "NONE SEEN"
      and v(s1, "S", "E184-P") == "LINEAR" and a["E184-P"]["meter"] == "METER EXCLUDED" and v(s1, "S", "E184-C") == "NONE SEEN"
      and a["reported"]["E184-K"]["inside"],
      "N %s, L %s R %s %s, J %s, P %s %s R %s, C %s T %s, K %s mW" % (
          v(s1, "S", "E184-N"), v(s1, "S", "E184-L"), a["E184-L"]["R"], a["E184-L"]["ci95"], v(s1, "S", "E184-J"), v(s1, "S", "E184-P"),
          a["E184-P"]["meter"], a["E184-P"]["R"], v(s1, "S", "E184-C"), a["E184-C"]["max_abs_t"], a["reported"]["E184-K"]["b_large_mw_per_minion"]))
s2 = score("S2", s=session("S2", "S", ["--seed", "12", "--gain-small", "0.8"]))
check("S2 small steps at 0.8", v(s2, "S", "E184-L") == "LOW" and v(s2, "S", "E184-P") == "LOW" and s2["arm_S"]["E184-P"]["meter"] == "METER EXCLUDED",
      "L %s R %s, P %s R %s %s" % (v(s2, "S", "E184-L"), s2["arm_S"]["E184-L"]["R"], v(s2, "S", "E184-P"), s2["arm_S"]["E184-P"]["R"],
                                  s2["arm_S"]["E184-P"]["meter"]))
s3 = score("S3", s=session("S3", "S", ["--seed", "13", "--gain-small", "0.2865"]))
check("S3 small steps at E178's 0.29", s3["arm_S"]["E184-P"]["meter"] == "METER NOT EXCLUDED",
      "P %s R %s %s %s" % (v(s3, "S", "E184-P"), s3["arm_S"]["E184-P"]["R"], s3["arm_S"]["E184-P"]["ci95"], s3["arm_S"]["E184-P"]["meter"]))
s4 = score("S4", s=session("S4", "S", ["--seed", "14", "--carry-w", "33.6", "--carry-d", "0.0328"]))
cc = s4["arm_S"]["E184-C"]
check("S4 a one-code step at 33.6 W", cc["verdict"] == "SEEN" and abs(cc["best_break_board_w"] - 33.6) <= 0.15,
      "C %s T %s, break %.3f W, d %s W" % (cc["verdict"], cc["max_abs_t"], cc["best_break_board_w"], cc["best_d_w"]))
s5 = score("S5", s=session("S5", "S", ["--seed", "15", "--jump-n", "48", "--jump-w", "0.10"]))
jj = s5["arm_S"]["E184-J"]
check("S5 a 0.10 W jump from n = 48", jj["verdict"] == "SEEN", "J %s, max |z| %.2f" % (jj["verdict"], jj["max_abs_z"]))

# ---- synthetic, arm B ------------------------------------------------------------------------------------------------------------------
b1 = score("B1", b=session("B1", "B", ["--seed", "21"]))
bb = b1["arm_B"]
tv = [x["verdict"] for x in bb["E184-T"].values()]
g = bb["reported"]["E184-G"]
check("B1 two-phase", bb["E184-M"]["verdict"] == "SUPPORTED" and all(t == "PASS" for t in tv)
      and 0.72 <= bb["reported"]["E184-R"]["sram_w"]["median"] <= 0.82 and abs(bb["reported"]["E184-X"]["median"] - 0.718) < 0.03
      and abs(g["rate"] - 0.00087) <= 3 * (0.00087 / g["samples"]) ** 0.5,
      "M %s f %s, T %s, R %s, X %s, G %s" % (bb["E184-M"]["verdict"], bb["E184-M"]["f"], tv, bb["reported"]["E184-R"]["sram_w"]["median"],
                                             bb["reported"]["E184-X"]["median"], bb["reported"]["E184-G"]["rate"]))
b2 = score("B2", b=session("B2", "B", ["--seed", "22", "--normal"]))
check("B2 a normal SRAM rail", b2["arm_B"]["E184-M"]["verdict"] == "REFUTED",
      "M %s, pooled min/avg %s" % (b2["arm_B"]["E184-M"]["verdict"], b2["arm_B"]["E184-M"]["pooled_min_over_avg_ci95"]))
b3 = score("B3", b=session("B3", "B", ["--seed", "23", "--spread", "0.12"]))
check("B3 ratios moving 0.12 with the load", b3["arm_B"]["E184-M"]["verdict"] == "REFUTED",
      "M %s, spread %s" % (b3["arm_B"]["E184-M"]["verdict"], b3["arm_B"]["E184-M"]["spread_min_over_avg"]))
b4 = score("B4", b=session("B4", "B", ["--seed", "24", "--tau-sram", "1.0"]))
t4 = b4["arm_B"]["E184-T"]
check("B4 an SRAM filter of 1.0 s", t4["sram_w rise"]["verdict"] == "OUTSIDE" and t4["sram_w fall"]["verdict"] == "OUTSIDE",
      "rise %s %s, fall %s %s" % (t4["sram_w rise"]["verdict"], t4["sram_w rise"]["mean_s"], t4["sram_w fall"]["verdict"], t4["sram_w fall"]["mean_s"]))
n1 = score("N1", s=os.path.join(S, "S1", "red-s.json"))
check("N1 no arm-B file", n1["arm_B"] is None and n1["arm_S"]["E184-L"]["verdict"] == "LINEAR", "arm B %s" % n1["arm_B"])
n2 = score("N2", s=session("N2", "S", ["--seed", "11"], drop=(18414, 18415, 18416)))
check("N2 the operating point's passes missing", v(n2, "S", "E184-P") == "NOT SCORED" and v(n2, "S", "E184-L") == "LINEAR",
      "P %s, L %s" % (v(n2, "S", "E184-P"), v(n2, "S", "E184-L")))

# ---- the readers on committed card data ------------------------------------------------------------------------------------------------
q = json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-06-q150-meter-checks/reset_minmax_bylevel.json")))["aifoundry1-c1"]
bins = {"idle": [], "busy": []}
import glob  # noqa: E402
for f in sorted(glob.glob(os.path.join(TOP, "docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1/tel/p*/reset.jsonl.gz"))):
    ds = []
    for line in gzip.open(f, "rt"):
        try:
            ds.append(json.loads(line))
        except ValueError:
            continue
    for x in c.reset_window_ratios(ds):
        bins["idle" if x[3] < 40 else "busy"].append(x)
ok, det = True, []
for k in ("idle", "busy"):
    m, M = round(c.median([x[0] for x in bins[k]]), 4), round(c.median([x[1] for x in bins[k]]), 4)
    ok = ok and len(bins[k]) == q[k]["n"] and m == q[k]["min_over_avg"] and M == q[k]["max_over_avg"]
    det.append("%s n %d/%d min/avg %.4f/%.4f max/avg %.4f/%.4f" % (k, len(bins[k]), q[k]["n"], m, q[k]["min_over_avg"], M, q[k]["max_over_avg"]))
check("R1 the reset-window reader on September's card-1 windows", ok, "; ".join(det))
import tau_a1_e184 as tau  # noqa: E402
taus = {"sram_w": [], "minion_w": []}
for pdir in sorted(glob.glob(os.path.join(TOP, "docs/reports/data/2026-09-29-tau-aifoundry1-c1/p[0-9]"))):
    bl = [json.loads(line) for line in open(os.path.join(pdir, "bursts.jsonl"))]
    for i, b in enumerate(bl):
        if b.get("rate_ms") != 100 or b.get("status") != "ok":
            continue
        tel = [json.loads(line) for line in open(os.path.join(pdir, "tel-%02d.jsonl" % b["win"])) if line.startswith("{")]
        tp, ref = tau.passes(tel)
        for rail, kinds in (("sram_w", ("D",)), ("minion_w", ("H", "M"))):
            if b["kind"] in kinds:
                dd = json.load(open(os.path.join(TOP, "docs/reports/data/2026-09-29-tau-aifoundry1-c1/report.json")))[rail]["100"]["one_pass"]["d_s"]
                f = tau.fit_burst(tp, [d["sp"][rail][0] for d in ref], b["t_on_ms"] / 1000.0, b["t_off_ms"] / 1000.0, None, dd)
                if f:
                    taus[rail].append(f)
e58 = json.load(open(os.path.join(TOP, "docs/reports/data/2026-09-29-tau-aifoundry1-c1/report.json")))
sr = c.median([f["tau_shared"] for f in taus["sram_w"]])
mr = c.median([f["tau_shared"] for f in taus["minion_w"]])
srr, srf = c.median([f["tau_rise"] for f in taus["sram_w"]]), c.median([f["tau_fall"] for f in taus["sram_w"]])
check("R2 A1's step-response reader on E58's card-1 bursts (100 ms sampler)",
      abs(sr - e58["sram_w"]["100"]["by_kind_tau"]["D"]) <= 0.04 and abs(mr - e58["minion_w"]["100"]["one_pass"]["tau_s"]) <= 0.10,
      "SRAM on %d D bursts: median tau %.2f s (E58 by kind D %.3f, one pass %.2f), rise %.2f fall %.2f (E58 %s); minion on %d H and M "
      "bursts %.2f s (E58 %.2f)" % (len(taus["sram_w"]), sr, e58["sram_w"]["100"]["by_kind_tau"]["D"], e58["sram_w"]["100"]["one_pass"]["tau_s"],
                                    srr, srf, e58["sram_w"]["100"]["rise_fall_tau_s"], len(taus["minion_w"]), mr,
                                    e58["minion_w"]["100"]["one_pass"]["tau_s"]))

# ---- the registered statistic -------------------------------------------------------------------------------------------------------------
import ast  # noqa: E402
import score_e184 as sc  # noqa: E402
src = open(os.path.join(HERE, "power_e184.py")).read()
fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "delta_ratio"][0]
seg = ast.get_source_segment(src, fn)
lv = {0: [0.001, -0.002, 0.003], 3: [0.026, 0.021, 0.027], 19: [0.16, 0.15, 0.158], 121: [0.99, 1.01, 1.0]}
got = sc.delta_ratio(lv, [3, 19], [121])
check("ID the scorer's delta_ratio is power_e184.py's", got == sc.registered_delta_ratio()(lv, [3, 19], [121]) and len(seg) > 200,
      "source sha256 %s, R %.6f" % (hashlib.sha256(seg.encode()).hexdigest()[:16], got[0]))

print("SELFTEST-SCORE-E184: %d of %d PASS" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
