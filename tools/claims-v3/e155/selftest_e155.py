#!/usr/bin/env python3
"""E155 self-test (desk, before the freeze; no card, no device). Standard library only.

    python3 tools/claims-v3/e155/selftest_e155.py > tools/claims-v3/e155/selftest.txt      # from the repo root

A. the bench's counts for m0 and m0r1 are identical to Q136(c)'s committed counts.json, and m0r3's to E148's post hoc ladder (desk/bench-e155.json >
   check_against_committed_counts);
B. the scorer on E148's committed reduction (its real m0r1 arms), with synthetic m0r3 and m0r3k8 items: m0r3.fp32 = m0r1.fp32 at m0r3's predicted
   rate, m0r3.int8 = m0r1.int8 with S shifted by a reading's point (Wn, Wt, C, T), and m0r3k8 D's set so that de3 equals the allowance's mid (F3
   BOUNDED) - each returns that reading's F1a/F1b verdicts; then de3 = mid + 60 pJ returns F3 EXCEEDS - synthetic inputs, never a result;
C. run_e155's line test: a 2.0 s old line stops at the registered 1.5 s, a fresh one does not, the stop test's 0.0 s stops any line, and the board and
   die stops fire at their lines.
SPDX-License-Identifier: Apache-2.0"""
import copy
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e155 as sc  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e155.json")))
B = json.load(open(os.path.join(HERE, "desk", "bench-e155.json")))
E = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e148-int8-excess", "e148.json")))
ok = True
a = all(v == "identical" for v in B["check_against_committed_counts"].values())
print(f"A bench m0/m0r1 identical to Q136(c)'s counts.json and m0r3 to E148's ladder: {'PASS' if a else 'FAIL'} {B['check_against_committed_counts']}")
ok &= a


def synth(point, de_extra_pj):
    o = copy.deepcopy(E)
    rp = P["rates_pred_ops_per_s"]
    e_f = 80e-12
    bm = P["f3_allowance"]["mid_pJ"] * 1e-12
    for p, e in o["per_pass"].items():
        f1, i1 = e["m0r1.fp32.zeros"], e["m0r1.int8.zeros"]
        f3 = copy.deepcopy(f1); f3["rate"] = rp["m0r3.fp32"]
        i3 = copy.deepcopy(i1); i3["rate"] = rp["m0r3.int8"]; i3["S"] = i1["S"] + point
        f3k = copy.deepcopy(f3); f3k["rate"] = rp["m0r3k8.fp32"]; f3k["D"] = f3["D"] + e_f * (rp["m0r3k8.fp32"] - rp["m0r3.fp32"])
        i3k = copy.deepcopy(i3); i3k["rate"] = rp["m0r3k8.int8"]
        i3k["D"] = i3["D"] + (e_f + bm + de_extra_pj * 1e-12) * (rp["m0r3k8.int8"] - rp["m0r3.int8"])
        e["m0r3.fp32.zeros"], e["m0r3.int8.zeros"], e["m0r3k8.fp32.zeros"], e["m0r3k8.int8.zeros"] = f3, i3, f3k, i3k
        for k in ("m0.fp32.zeros", "m0.int8.zeros", "m0r2.fp32.zeros", "m0r2.int8.zeros"):
            e.pop(k, None)
    for k, v in P["rules"]["R6"]["predicted"].items():
        arm, f = k.split(".")
        o["cycles_per_op"][f"{arm}:{f}"] = v
    return o


want = {"Wn": ("WALK", "NEW-ADDRESS"), "Wt": ("WALK", "TOGGLES"), "C": ("PER-CYCLE", "NEITHER"), "T": ("NEITHER", "NEITHER")}
for k, (va, vb) in want.items():
    r = sc.score(synth(P["readings"][k]["point"], 0.0), P)
    f1 = r["rules"]["F1"]
    r6 = all(x["verdict"] == "PASS" for x in r["rules"]["R6"].values())
    good = f1["F1a_walk_against_per_cycle"] == va and f1["F1b_toggles_against_new_address"] == vb and f1["consistent_set"] == [k] \
        and r["rules"]["F3"]["verdict"] == "BOUNDED" and r6
    print(f"B reading {k} at its point {P['readings'][k]['point']:+.3f} W: F1a {f1['F1a_walk_against_per_cycle']} (want {va}), F1b "
          f"{f1['F1b_toggles_against_new_address']} (want {vb}), consistent {f1['consistent_set']}; F3 {r['rules']['F3']['verdict']} "
          f"(de3c {r['rules']['F3']['de3c_pJ']['mean']:+.2f} pJ); R6 all PASS {r6}: {'PASS' if good else 'FAIL'}")
    ok &= good
r = sc.score(synth(P["readings"]["Wt"]["point"], 60.0), P)
g = r["rules"]["F3"]["verdict"] == "EXCEEDS"
print(f"B de3 = mid + 60 pJ: F3 {r['rules']['F3']['verdict']} (want EXCEEDS; de3c {r['rules']['F3']['de3c_pJ']['mean']:+.1f}): {'PASS' if g else 'FAIL'}")
ok &= g
os.environ["E155_DESK"] = "1"
import run_e155 as rr  # noqa: E402
now = time.time()
st = P["plan"]["stops"]
fresh = {"t_ms": now * 1000, "board_w": 40.0, "temp_c": {"minshire": [55.0, 56.0]}}
old = dict(fresh, t_ms=(now - 2.0) * 1000)
c1 = rr._check_line(old, st["board_w"], st["die_hottest_shire_c"], "T", "x", st["stale_line_s"])
c2 = rr._check_line(fresh, st["board_w"], st["die_hottest_shire_c"], "T", "x", st["stale_line_s"])
c3 = rr._check_line(dict(fresh, t_ms=(time.time() - 0.05) * 1000), st["board_w"], st["die_hottest_shire_c"], "T", "x", st["stoptest_stale_s"])
c4 = rr._check_line(dict(fresh, board_w=66.0), st["board_w"], st["die_hottest_shire_c"], "T", "x", st["stale_line_s"])
c5 = rr._check_line(dict(fresh, temp_c={"minshire": [55.0, 72.0]}), st["board_w"], st["die_hottest_shire_c"], "T", "x", st["stale_line_s"])
g = bool(c1 and "stale" in c1) and c2 is None and bool(c3 and "stale" in c3) and bool(c4 and "board" in c4) and bool(c5 and "die" in c5)
print(f"C line test: 2.0 s old -> {c1!r:.60}; fresh -> {c2!r}; stop test 0.0 s -> {c3!r:.50}; board 66 -> {c4!r:.40}; die 72 -> {c5!r:.40}: "
      f"{'PASS' if g else 'FAIL'}")
ok &= g
print("SELFTEST", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
