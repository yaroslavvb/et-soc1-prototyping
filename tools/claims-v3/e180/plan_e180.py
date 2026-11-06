#!/usr/bin/env python3
"""E180's run plan: the configurations every pass runs, the order of each pass from a stated seed, and the budget.

    python3 plan_e180.py --dir tools/claims-v3/e180            # writes cfgs-e180.json and plan-e180.json
    python3 plan_e180.py --dir tools/claims-v3/e180 --check    # re-makes both and compares byte for byte

A pass is every kind of kinds-e180.json once, plus two more runs of each of his pair (fadd.ps/f_4, fadd.ps/f_5) and one
more of fadd.ps/zeros and of fadd.pi/zeros (E180-H's couple, the footings of the ladder and of E180-I): 47 runs. Each run is one energy-catalogue configuration, its
arguments exactly as workloads/enercat/run_catalogue.py writes an instruction row (--pattern <op> --operands <fill> --harts
2), with E180's operand image as --operands file:<image>, run by E180's runner with the catalogue's timing (--burst 3
--gap 4.5, launches of --window 240000000 cycles = 0.4 s at 600 MHz, a 10 s lead). A repeat run of a kind is the same
configuration under the suffix @r2 / @r3 (one burst per (cfg, pass), as analyze_catalogue.bursts_of groups them).
Order: the runner's own per-pass shuffle, random.Random(seed).shuffle over this list, with seed = 18000 + pass number;
the plan writes each pass's order out so the block can check the runner's (catfull's form).
Passes: FULL 18010-18015 (six), TWO 18010-18011; the smoke 18001 (fadd.ps zeros, fadd.ps/f_5, fadd.ps.acc/f_5, fadd.pi
random, --burst 1, no lead), the stop-path test 18002 (no launch). Budget: the queue starts a pass only if its projected
end (the longest measured pass, first 420 s) fits the cap less a 60 s reserve and the deadline; FULL cap 50 card-minutes
(3,000 s from E180_T0), TWO cap 20 (1,200 s); a pass in flight is never cut, and a seventh is never planned.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import filecmp
import json
import os
import random
import sys
import tempfile

PASSES = {"FULL": [18010, 18011, 18012, 18013, 18014, 18015], "TWO": [18010, 18011]}
SMOKE = ["fadd.ps/zeros", "fadd.ps/f_5", "fadd.ps.acc/f_5", "fadd.pi/random"]
REPEAT = {"fadd.ps/f_4": 3, "fadd.ps/f_5": 3, "fadd.ps/zeros": 2, "fadd.pi/zeros": 2}   # runs a pass
CAP_S = {"FULL": 3000, "TWO": 1200}
RESERVE_S = 60
FIRST_PASS_ESTIMATE_S = 420
BURST, GAP, LEAD, WINDOW = 3.0, 4.5, 10.0, 240000000
HOST_BIN = "build/enercat-e180/host/enercat_host"


def cfg_of(k, suffix=""):
    ops = k["operands"]
    oper = f"file:tools/claims-v3/e180/{k['image']}" if ops == "file" else ops
    return {"cfg": f"e180/{k['name']}/h2{suffix}", "kind": k["name"], "mode": k["mode"],
            "args": ["--pattern", k["mode"], "--operands", oper, "--harts", "2"], "host_bin": HOST_BIN}


def build(d):
    kinds = json.load(open(os.path.join(d, "kinds-e180.json")))["kinds"]
    cfgs = [cfg_of(k) for k in kinds] + [cfg_of(k, f"@r{r}") for k in kinds for r in range(2, REPEAT.get(k["name"], 1) + 1)]
    names = [c["cfg"] for c in cfgs]
    assert len(names) == len(set(names)) == 47, len(names)   # E180's runner selects by exact name, never by prefix
    passes = {}
    for p in sorted(set(PASSES["FULL"]) | set(PASSES["TWO"])):
        order = list(range(len(cfgs)))
        random.Random(p).shuffle(order)
        passes[str(p)] = [names[i] for i in order]
    smoke = [cfg_of(next(k for k in kinds if k["name"] == s)) for s in SMOKE]
    plan = {"what": "E180's run plan (plan_e180.py)", "card": "aifoundry3 card 0, 600 MHz pinned (fallback aifoundry1 card 1)",
            "plans": PASSES, "cap_s": CAP_S, "reserve_s": RESERVE_S, "first_pass_estimate_s": FIRST_PASS_ESTIMATE_S,
            "timing": {"burst_s": BURST, "gap_s": GAP, "lead_s": LEAD, "window_cycles": WINDOW},
            "smoke": {"pass": 18001, "cfgs": [c["cfg"] for c in smoke], "burst_s": 1.0, "lead_s": 3.0},
            "stop_path_test": {"pass": 18002}, "seed_rule": "random.Random(pass).shuffle over cfgs-e180.json's order",
            "runs_per_pass": len(cfgs), "order": passes,
            "estimate": {"per_run_s": BURST + GAP + 0.6, "per_pass_s": round(len(cfgs) * (BURST + GAP + 0.6) + LEAD + 20),
                         "full_card_minutes": round((6 * (len(cfgs) * (BURST + GAP + 0.6) + LEAD + 20) + 120) / 60, 1)}}
    return {"what": "E180's configurations (plan_e180.py)", "host_bin": HOST_BIN, "cfgs": cfgs, "smoke": smoke}, plan


def write(d, out):
    cfgs, plan = build(d)
    json.dump(cfgs, open(os.path.join(out, "cfgs-e180.json"), "w"), indent=1)
    json.dump(plan, open(os.path.join(out, "plan-e180.json"), "w"), indent=1)
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check:
        plan = write(a.dir, a.dir)
        print(json.dumps(plan["estimate"]), plan["runs_per_pass"], "runs a pass")
        return
    with tempfile.TemporaryDirectory() as t:
        write(a.dir, t)
        bad = [f for f in ("cfgs-e180.json", "plan-e180.json")
               if not filecmp.cmp(os.path.join(t, f), os.path.join(a.dir, f), shallow=False)]
    print("CHECK FAIL: " + ", ".join(bad) if bad else "CHECK PASS: cfgs-e180.json and plan-e180.json byte for byte")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
