#!/usr/bin/env python3
"""E113: the scorer's self-test on synthetic passes with a known truth (no card data). Three truths:
  mirror  every A rung = 0.65 x E70's B rung of the same mask  -> expect P1 PASS, P3 PASS, P4 'which bits', c ~ 0.65
  howmany als_h<k> = alq_h<k> (E70's low-layout A values)        -> expect P1 FAIL (how many), P4 'how many'
  curve   every A rung = 6.0 (1 - exp(-S_A/6.0))                 -> expect P2 ACCEPTED, W refit ~ 6.0
Each writes a runs.csv in reduce_hl.py's format with 6 passes and 0.05 W of noise per run, then scores it.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e113 as S  # noqa: E402

pred = json.load(open(os.path.join(HERE, "predictions-e113.json")))
rung = {r["item"]: r for r in pred["rungs"]}
ITEMS = (["anchor_pi", "aq_h0", "lq_h0", "lq_h8", "ls_h8", "nrd_a", "nrd_b"] + [f"alq_h{k}" for k in S.ALQ_K] +
         [f"als_h{k}" for k in S.ALS_K])
E70LQ = {r["k"]: r["B_same_mask_E70_W"] for r in pred["rungs"] if r["layout"] == "low"}


def truth(kind, item):
    if item in ("anchor_pi", "aq_h0", "lq_h0"):
        return 0.0
    if item == "lq_h8":
        return pred["E70_B_ties"]["lq_h8"]["W"]
    if item == "ls_h8":
        return pred["E70_B_ties"]["ls_h8"]["W"]
    if item == "nrd_b":
        return 10.8
    if item == "nrd_a":
        return 0.65 * 10.8
    r = rung[item]
    if kind == "mirror":
        return 0.65 * r["B_same_mask_E70_W"]
    if kind == "howmany":
        return 0.65 * E70LQ[r["k"]]
    if kind == "curve":
        return S.cov(r["S_A_W"], 6.0)
    raise ValueError(kind)


def write(kind, path, seed):
    rnd = random.Random(seed)
    cols = ["card", "pass", "item", "pos", "attempt", "kind", "family", "start_c", "on_protocol", "p_raw", "p_raw14",
            "p80", "t_win", "rail", "mv", "mhz", "rate", "cycles_per_op", "fail"]
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        for p in range(1131, 1137):
            off = rnd.gauss(0, 0.2)
            seq = ["anchor_pi"] + [i for i in ITEMS if i != "anchor_pi"] + ["anchor_pi"]
            for pos, it in enumerate(seq):
                v = 36.4 + off + truth(kind, it) + rnd.gauss(0, 0.05)
                wr.writerow({"card": "aifoundry3", "pass": p, "item": it, "pos": pos, "attempt": 1, "kind": "fma",
                             "family": it.split("_")[0], "start_c": 58.0, "on_protocol": True, "p_raw": v, "p_raw14": v,
                             "p80": v, "t_win": 59.0, "rail": 17.0, "mv": 522.0, "mhz": "[600]", "rate": 1.1209e9,
                             "cycles_per_op": 546.0, "fail": "[]"})


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    ok = True
    for kind, seed in (("mirror", 1), ("howmany", 2), ("curve", 3)):
        path = os.path.join(out, f"selftest-{kind}.csv")
        write(kind, path, seed)
        R = S.score(S.load_runs(path), pred)
        r, D2 = R["rules"], R["D2_A"]
        print(f"[{kind}] kept {R['passes_kept']}  D1_A(8) {[d for d in R['D1_A'] if d['k'] == 8][0]['dW_spread_minus_low']:.3f}  "
              f"R_k {D2['R_k_W']:.3f}  R_SA {D2['R_SA_refit_W']:.3f} (W {D2['WA_refit_W']:.2f})  R_M0 {D2['R_M_frozen_W']:.3f}  "
              f"R_M {D2['R_M_refit_W']:.3f} (c {D2['c_refit']:.4f})  rho8 {R['rho8']['low']['rho']:.3f}/{R['rho8']['spread']['rho']:.3f}")
        print("   " + "  ".join(f"{k}:{v['verdict']}" for k, v in r.items()))
        if kind == "mirror":
            ok &= r["P1"]["verdict"] == "PASS" and r["P3"]["verdict"] == "PASS" and r["P4"]["verdict"].startswith("which bits")
            ok &= abs(D2["c_refit"] - 0.65) < 0.01 and r["P5"]["verdict"] == "PASS" and r["P7"]["verdict"] == "PASS"
        if kind == "howmany":
            ok &= r["P1"]["verdict"].startswith("FAIL") and r["P4"]["verdict"].startswith("how many")
        if kind == "curve":
            ok &= r["P2"]["verdict"] == "ACCEPTED" and abs(D2["WA_refit_W"] - 6.0) < 0.15
    print("SELFTEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
