#!/usr/bin/env python3
"""E125: the scorer's self-test on synthetic passes with a known truth (no card data), and the rules' power.

Truths (card-1 watts; every rung at E113's value in E125's frame (e113-nodips/scored.json) over E82's card scale s unless named):
  replicate  E113's ladder / s; lq_h2 and lq_h4 at alq / 1.025 and / 1.059 (E113's cross-session A/B)
             -> expect Z REPLICATES, the X A rungs PASS, N1 SMALL-K EXCESS
  fraction   the same, but lq_h2 and lq_h4 at alq / 0.667 (one A/B fraction at every k)  -> expect N1 NO SMALL-K EXCESS
  dearer     every A rung (alq, als, nrd_a) x 1.25 over the replicate                    -> expect the X A rungs FAIL, X-c FAIL
Each writes a runs.csv in reduce_hl.py's format with 5 passes and 0.05 W of noise per run, then scores it. Then the power:
200 synthetic sessions of the replicate truth at n = 4 and n = 5 kept passes, each item's per-pass scatter set to E113's
in E125's frame (its SE x sqrt n), lq_h2 and lq_h4 at 0.15 W, the zeros at 0.05 W: how often each X rule and N1 read each verdict.
    python3 tools/claims-v3/e125/selftest_e125.py [<scratch dir>]
SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import json
import math
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e125 as S  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
pred113 = json.load(open(os.path.join(ROOT, "tools/claims-v3/e113/predictions-e113.json")))
pred = json.load(open(os.path.join(HERE, "predictions-e125.json")))
s113 = json.load(open(os.path.join(ROOT, pred["sources"]["E113_nodips_scored"])))   # the X rules' primary source
SC = pred["card_scale"]["s_fp32_aifoundry3_over_card1"]
ITEMS = ["anchor_pi", "aq_h0", "alq_h1", "alq_h2", "alq_h3", "alq_h4", "alq_h6", "alq_h8", "alq_h12", "alq_h16", "alq_h23",
         "als_h2", "als_h3", "als_h4", "als_h6", "als_h8", "als_h12", "als_h16", "lq_h0", "lq_h2", "lq_h4", "lq_h8", "ls_h8",
         "nrd_a", "nrd_b"]
COLS = ["card", "pass", "item", "pos", "attempt", "kind", "family", "start_c", "on_protocol", "p_raw", "p_raw14", "p80", "t_win",
        "rail", "mv", "mhz", "rate", "cycles_per_op", "fail"]


def truth(kind, item):
    if item in ("anchor_pi", "aq_h0", "lq_h0"):
        return 0.0
    if item == "lq_h2":
        return truth(kind, "alq_h2") / (1.025 if kind != "fraction" else 0.667)
    if item == "lq_h4":
        return truth(kind, "alq_h4") / (1.059 if kind != "fraction" else 0.667)
    v = s113["items"][item]["dW"] / SC
    if kind == "dearer" and (item.startswith("alq_") or item.startswith("als_") or item == "nrd_a"):
        v *= 1.25
    return v


def sd_of(item, realistic):
    if not realistic:
        return 0.05
    if item in ("anchor_pi", "aq_h0", "lq_h0"):
        return 0.05
    if item in ("lq_h2", "lq_h4"):
        return 0.15
    return s113["items"][item]["se"] * math.sqrt(s113["items"][item]["n_passes"])


def write(kind, path, rnd, n_passes, realistic=False):
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=COLS)
        wr.writeheader()
        for p in range(12501, 12501 + n_passes):
            off = rnd.gauss(0, 0.2)
            seq = ["anchor_pi"] + [i for i in ITEMS if i != "anchor_pi"] + ["anchor_pi"]
            for pos, it in enumerate(seq):
                v = 33.0 + off + truth(kind, it) + rnd.gauss(0, sd_of(it, realistic))
                wr.writerow({"card": "aifoundry1-c1", "pass": p, "item": it, "pos": pos, "attempt": 1, "kind": "fma",
                             "family": it.split("_")[0], "start_c": 58.0, "on_protocol": True, "p_raw": v, "p_raw14": v,
                             "p80": v, "t_win": 59.0, "rail": 15.0, "mv": 499.0, "mhz": "[600]", "rate": 1.1209e9,
                             "cycles_per_op": 546.0, "fail": "[]"})


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="e125-selftest-")
    os.makedirs(out, exist_ok=True)
    ok = True
    for kind, seed in (("replicate", 1), ("fraction", 2), ("dearer", 3)):
        path = os.path.join(out, f"selftest-{kind}.csv")
        write(kind, path, random.Random(seed), 5)
        R, E = S.score(S.S13.load_runs(path), pred113, pred)
        xa = E["x_A_rungs"]
        print(f"[{kind}] kept {R['passes_kept']}  Z {E['Z']['verdict']}  X A rungs {xa['verdict']} ({xa['n_pass']} PASS, "
              f"{xa['n_fail']} FAIL)  N1 {E['N1']['verdict']} ({E['N1']['N1']:.3f} +- {E['N1']['se']:.3f})  c {R['D2_A']['c_refit']:.4f}")
        print("   " + "  ".join(f"{x['id'][2:]}:{x['verdict'][:4]}" for x in E["x_rules"] if x["group"] != "A_rungs"))
        print("   " + "  ".join(f"{k}:{v['verdict'].split(' ')[0]}" for k, v in R["rules"].items()))
        xv = {x["id"]: x["verdict"] for x in E["x_rules"]}
        if kind == "replicate":
            ok &= E["Z"]["verdict"] == "REPLICATES" and xa["verdict"] == "PASS" and E["N1"]["verdict"] == "SMALL-K EXCESS"
            ok &= xv["X-c"] == "PASS" and xv["X-nrd"] == "PASS" and xv["X-D1_A8"] == "PASS"
        if kind == "fraction":
            ok &= E["N1"]["verdict"] == "NO SMALL-K EXCESS" and E["Z"]["verdict"] == "REPLICATES"
        if kind == "dearer":
            ok &= xa["verdict"] == "FAIL" and xv["X-c"] == "FAIL"
    print("SELFTEST", "PASS" if ok else "FAIL")
    # power of each rule under the replicate truth with E113's own per-pass scatter
    rnd = random.Random(125)
    for n in (4, 5):
        tally = collections.defaultdict(collections.Counter)
        for i in range(200):
            path = os.path.join(out, "power.csv")
            write("replicate", path, rnd, n, realistic=True)
            R, E = S.score(S.S13.load_runs(path), pred113, pred)
            for x in E["x_rules"]:
                tally[x["id"]][x["verdict"]] += 1
            tally["X A rungs"][E["x_A_rungs"]["verdict"]] += 1
            tally["N1"][E["N1"]["verdict"]] += 1
            tally["Z"][E["Z"]["verdict"]] += 1
        print(f"POWER n = {n} (200 sessions, replicate truth, E113's scatter):")
        for k, c in tally.items():
            print(f"  {k:14s} " + ", ".join(f"{v} {c[v] / 200:.2f}" for v in sorted(c)))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
