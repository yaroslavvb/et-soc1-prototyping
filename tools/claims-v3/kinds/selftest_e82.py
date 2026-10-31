#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E82 self-test: the E82 reduction and scoring run on SYNTHETIC passes with known answers, before any card data.

    python3 tools/claims-v3/kinds/selftest_e82.py <scratch dir>  > tools/claims-v3/kinds/selftest_e82.txt

It uses selftest_e78.py's generator (the runner's exact layout) twice: six synthetic card-1 passes (8210-8215) whose
truth is Q130(c)'s prediction divided by 0.95 (card 1 switching 1/0.95 of aifoundry3), with card 1's configuration
reads (TDP 65, threshold 65, 499 mV), and six synthetic aifoundry3 passes (7810-7815) with the predictions
themselves, as a stand-in for E78's reduction. Then it checks:
  1. reduce_e78.py UNCHANGED sets every card-1 pass apart on its configuration (why reduce_e82.py exists);
  2. reduce_e82.py keeps all six and recovers the truth;
  3. a pass whose end read shows another TDP is still set apart by reduce_e82.py;
  4. score_e82.py scores E78's rules and the cross-card rules, and X3's median ratio recovers 0.95.
NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
"""
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

SCALE = 0.95          # synthetic D(aifoundry3) / D(card 1)


def make(base, first, truth, seed, card1):
    rng = np.random.default_rng(seed)
    items = ec.load_items()
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    for i in range(6):
        p = first + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, truth, rng, items)
        if card1:
            cf = json.load(open(os.path.join(d, "configs.json")))
            cf["card"] = "aifoundry1-c1"
            json.dump(cf, open(os.path.join(d, "configs.json"), "w"))
            for nm in ("config_start", "config_end"):
                json.dump({"tdp_w": 65, "temp_threshold_c": 65, "power_state": 1, "power_state_name": "managed_power",
                           "minion_mhz": 600, "minion_mv": 499}, open(os.path.join(d, nm + ".json"), "w"))
        dirs.append(d)
    return dirs


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-2500:])
        sys.exit(f"failed: {args[0]}")
    return r


def main():
    scr = sys.argv[1]
    os.makedirs(scr, exist_ok=True)
    truth = st.truth()
    t82 = {k: v / SCALE for k, v in truth.items()}
    d82 = make(os.path.join(scr, "e82", "kinds"), 8210, t82, 2, True)
    d78 = make(os.path.join(scr, "e78", "kinds"), 7810, truth, 3, False)
    j = lambda *a: os.path.join(scr, *a)  # noqa: E731
    # 1. the unchanged reduction on card-1 passes
    run([os.path.join(HERE, "reduce_e78.py"), *d82, "--out", j("plain-e78-on-c1.json"), "--no-refit"])
    plain = json.load(open(j("plain-e78-on-c1.json")))
    # 2. the wrapper, primary and arms
    run([os.path.join(HERE, "reduce_e82.py"), *d82, "--out", j("e82.json"), "--txt", j("e82-reduce.txt")])
    for k in ("0.545", "0.3803", "0"):
        run([os.path.join(HERE, "reduce_e82.py"), *d82, "--leak", k, "--no-refit", "--out", j(f"e82-leak{k}.json")])
    e = json.load(open(j("e82.json")))
    # 3. a pass whose end read shows another TDP
    bad = os.path.join(scr, "e82bad", "kinds")
    if os.path.isdir(bad):
        shutil.rmtree(bad)
    shutil.copytree(os.path.join(scr, "e82", "kinds"), bad)
    cfe = os.path.join(bad, "p8212", "config_end.json")
    c = json.load(open(cfe))
    c["tdp_w"] = 30
    json.dump(c, open(cfe, "w"))
    dbad = sorted(os.path.join(bad, x) for x in os.listdir(bad))
    run([os.path.join(HERE, "reduce_e82.py"), *dbad, "--out", j("e82-bad.json"), "--no-refit"])
    eb = json.load(open(j("e82-bad.json")))
    # the stand-in for E78's committed reduction (E78's collect writes e78.json and the two leakage arms)
    e78dir = j("e78-data")
    os.makedirs(e78dir, exist_ok=True)
    run([os.path.join(HERE, "reduce_e78.py"), *d78, "--out", os.path.join(e78dir, "e78.json"), "--no-refit"])
    for k in ("0.3803", "0"):
        run([os.path.join(HERE, "reduce_e78.py"), *d78, "--leak", k, "--no-refit",
             "--out", os.path.join(e78dir, f"e78-leak{k}.json")])
    run([os.path.join(HERE, "score_e78.py"), "--e78", os.path.join(e78dir, "e78.json"),
         "--json", os.path.join(e78dir, "scored.json"), "--md", os.path.join(e78dir, "results.md")])
    # 4. the E82 scorer with the cross-card rules
    run([os.path.join(HERE, "score_e82.py"), "--e82", j("e82.json"), "--e82-arm", f"leak0.545={j('e82-leak0.545.json')}",
         "--e82-arm", f"leak0.3803={j('e82-leak0.3803.json')}", "--e82-arm", f"leak0={j('e82-leak0.json')}",
         "--e78-dir", e78dir, "--json", j("e82-scored.json"), "--md", j("e82-results.md")])
    sc = json.load(open(j("e82-scored.json")))
    xc = sc["cross_card"]
    P = xc["primary"]
    worst = max(abs(e["items"][n]["D"]["mean"] - t82[n]) for n in e["items"] if n != ec.TIE)
    checks = {
        "plain_reduce_e78_sets_every_card1_pass_apart": (plain["passes"] == [] and len(plain["passes_config_flags"]) == 6,
                                                         (len(plain["passes"]), len(plain["passes_config_flags"]))),
        "reduce_e82_keeps_all_six": (e["passes"] == list(range(8210, 8216)) and e["experiment"] == "E82",
                                     (e["passes"], e["experiment"])),
        "reduce_e82_records_raw_reads": (all(v["config_start"]["tdp_w"] == 65 for v in e["reducer"]["config_reads_raw"].values()),
                                         len(e["reducer"]["config_reads_raw"])),
        "D_recovered_within_0.20W": (worst <= 0.20, round(worst, 4)),
        "a_changed_tdp_is_set_apart": ([x["pass"] for x in eb["passes_config_flags"]] == [8212] and 8212 not in eb["passes"],
                                       ([x["pass"] for x in eb["passes_config_flags"]], eb["passes"])),
        "cross_card_scored": (xc["status"] == "scored", xc["status"]),
        "X1_pass_all_types": (P["x1"]["verdict"] == "PASS",
                              {t: round(P["x1"][t]["rho"], 3) for t in ("fp32", "fp16", "int8")}),
        "X3_median_ratio_near_0.95": (abs(P["x3"]["median_ratio"] - SCALE) < 0.01 and P["x3"]["verdict"] == "PASS",
                                      round(P["x3"]["median_ratio"], 4)),
        "X2_fractions": (P["x2"]["X2a_verdict"] == "PASS" and P["x2"]["X2b_verdict"] == "PASS",
                         (P["x2"]["X2a_frac_point_inside"], P["x2"]["X2b_frac_interval_overlaps"])),
        "arms_scored": (len(xc["arms"]) == 3, sorted(xc["arms"])),
        "e78_rule_agreement_computed": (xc.get("e78_rule_verdict_agreement") is not None,
                                        (xc.get("e78_rule_verdict_agreement") or {}).get("compared")),
    }
    print("# selftest_e82.py on SYNTHETIC passes (6 card-1 passes, truth = Q130(c) / 0.95; 6 aifoundry3 passes): "
          "a check of the code, never data")
    for k, (ok, v) in checks.items():
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {v}")
    print("E78-rule tally on synthetic card-1 data (meaningless as a result):", sc["tally"])
    print("# exit", 0 if all(ok for ok, _ in checks.values()) else 1)
    sys.exit(0 if all(ok for ok, _ in checks.values()) else 1)


if __name__ == "__main__":
    main()
