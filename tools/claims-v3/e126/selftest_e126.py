#!/usr/bin/env python3
"""E126 (Q136): every rule of reduce_e126.score() shown passing on made-up rows at the frozen values and failing when one number moves, plus
run_e126.preflight() refusing a binary that is not E119's. No card, no E126 data.

    python3 tools/claims-v3/e126/selftest_e126.py > tools/claims-v3/e126/selftest.txt
"""
import copy
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e126 as RD  # noqa: E402
import run_e126 as RN  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e126.json")))
TYPES = ("fp32", "fp16", "int8")


def frozen_rows():
    """per, cells, t800 at the frozen values: every new arm's X as frozen (c4s like c8s, the DRAM arms at their share model), the replicate at E119's."""
    per, cells, t800 = {}, {}, {}
    for t in TYPES:
        L = P["laws"][f"c4s.{t}"]
        per[f"c4s.{t}"] = {"X": L["X_like_c8s"], "T600": P["rules"]["R0_ties"]["e107_T600"][f"c4s.{t}"] * 0.997, "n600": 3, "fit": None}
        for a in P["dram_arms"]:
            L = P["laws"][f"{a}.{t}"]
            per[f"{a}.{t}"] = {"X": L["X_S"], "T600": P["rules"]["R0_ties"]["e107_T600"][f"{a}.{t}"] * 0.997, "n600": 3, "fit": None}
    for a, ref in P["replicate"].items():
        per[f"{a}.fp32"] = {"X": ref["X"], "T600": None, "n600": 0, "fit": None, "how": "launch means"}
        cells[f"{a}-fp32-randn"] = {"sus_mhz": ref["randn_sus_mhz"], "sus_rate": ref["randn_sus_rate"]}
        cells[f"{a}-fp32-zeros"] = {"sus_mhz": ref["zeros_sus_mhz"], "sus_rate": ref["zeros_sus_rate"]}
        t800[f"{a}-fp32-zeros"] = ref["T800_zeros_us"]
        t800[f"{a}-fp32-randn"] = ref["T800_zeros_us"] * 1.002
    r6 = P["rules"]["R6_new_sus"]
    cells["c4s-fp32-randn"] = {"sus_mhz": r6["c4s_mhz"], "sus_rate": 6.10, "burst_p800_w_runs": [70.0]}
    cells["c4s-fp32-zeros"] = {"sus_mhz": 789.0, "sus_rate": 6.10 * r6["c4s_gap"]}
    for a in P["dram_arms"]:
        cells[f"{a}-fp32-randn"] = {"sus_mhz": 790.0, "sus_rate": 3.50, "burst_p800_w_runs": [55.0]}
        cells[f"{a}-fp32-zeros"] = {"sus_mhz": 795.0, "sus_rate": 3.52}
    t800["c4s-fp32-zeros"] = 1.2654
    return per, cells, t800


def show(tag, V):
    out = {
        "R0": V["R0"]["verdict"],
        "R1": f"{V['R1']['verdict']} / {V['R1']['share_verdict']}",
        "R2": {k: f"{v['verdict_a']} / {v['verdict_b']}" for k, v in V["R2"]["cells"].items() if k.endswith("fp32")},
        "R3": V["R3"]["verdict"], "R4": {"cells": {k: v["verdict"] for k, v in V["R4"]["cells"].items()}, "order": V["R4"]["order"], "c8s_below": V["R4"]["c8s_below"]},
        "R5": {k: v["verdict"] for k, v in V["R5"]["cells"].items()}, "R6": {k: v["verdict"] for k, v in V["R6"]["cells"].items()},
        "R7": V["R7"]["verdict"], "R8": V["R8"]["verdict"]}
    print(f"{tag}: {json.dumps(out)}")


def main():
    per, cells, t800 = frozen_rows()
    show("frozen values", RD.score(per, cells, t800, P, True))
    cases = []
    p2 = copy.deepcopy(per)
    p2["c4s.fp32"]["T600"] *= 1.03
    cases.append(("R0 FAIL: c4s's T at 600 MHz 3% off E107's", p2, cells, t800, True))
    cases.append(("R0 FAIL: a check of C wrong", per, cells, t800, False))
    p2 = copy.deepcopy(per)
    p2["c4s.fp32"]["X"] = P["laws"]["c4s.fp32"]["X_like_c8s"] + 0.03
    cases.append(("R1 NOT LIKE IT: c4s's X 0.03 over c8s's", p2, cells, t800, True))
    p2 = copy.deepcopy(per)
    p2["c4s.fp32"]["X"] = P["laws"]["c4s.fp32"]["X_M2"]
    cases.append(("R1 FOLLOWS THE CLOCK: c4s at M2", p2, cells, t800, True))
    p2 = copy.deepcopy(per)
    p2["c16s.fp32"]["X"] = P["laws"]["c16s.fp32"]["X_W"]
    cases.append(("R2 THE COLD WALK'S WAIT: c16s at W", p2, cells, t800, True))
    p2 = copy.deepcopy(per)
    p2["c16s.fp32"]["X"] = 1.11
    cases.append(("R2 NOT A DRAM WALK: c16s buys x1.11", p2, cells, t800, True))
    c2 = copy.deepcopy(cells)
    c2["c16r4-fp32-randn"]["sus_mhz"] += 40
    cases.append(("R3 NOT: c16r4 random 40 MHz faster", per, c2, t800, True))
    c2 = copy.deepcopy(cells)
    c2["c16r8-fp32-randn"]["sus_rate"] *= 1.08
    cases.append(("R4 FAIL and order: c16r8 random 8% faster", per, c2, t800, True))
    c2 = copy.deepcopy(cells)
    c2["c8s-fp32-randn"]["sus_rate"] /= 1.06
    cases.append(("R4 c8s not below 1.118: its gap x1.14", per, c2, t800, True))
    p2 = copy.deepcopy(per)
    p2["c16r2.fp32"]["X"] += 0.015
    cases.append(("R5 FAIL: c16r2's X 0.015 high", p2, cells, t800, True))
    c2 = copy.deepcopy(cells)
    c2["c8-fp32-randn"]["sus_mhz"] = 700.0
    c2["c4s-fp32-randn"]["sus_mhz"] = 720.0
    cases.append(("R6 FAIL: c8 random held to 700 MHz, c4s at 720", per, c2, t800, True))
    t2 = dict(t800)
    t2["c16r8-fp32-randn"] = t800["c16r8-fp32-zeros"] * 1.02
    cases.append(("R7 FAIL: c16r8 random's T 2% over zeros'", per, cells, t2, True))
    c2 = copy.deepcopy(cells)
    c2["c4s-fp32-randn"]["burst_p800_w_runs"] = [P["admission"]["c4s-fp32-randn"]["fixed_p800_w"] + 1.5]
    cases.append(("R8 FAIL: c4s random 1.5 W over its estimate", per, c2, t800, True))
    for tag, a, b, c, ok in cases:
        show(tag, RD.score(a, b, c, P, ok))
    d = tempfile.mkdtemp()
    proto = {"tools": {"heater": "build/e119/host/sparsity_host", "kernel": "build/e119/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"}}
    for rel in proto["tools"].values():
        os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
        open(os.path.join(d, rel), "wb").write(b"not E119's binary")
    why = RN.preflight(proto, d)
    print("preflight on binaries that are not E119's:", "REFUSED" if why else "passed (WRONG)", "|", (why or "")[:160])
    print("preflight on a protocol naming another sampler:", "REFUSED" if RN.preflight({"tools": dict(proto["tools"], ettelem="build/ettelem/ettelem")}, d) else "passed (WRONG)")
    print("run_e119.fits (E119's cap cut, unchanged): 40 min used + 2 min planned in 44 ->", RN.R119.fits(2400, 120, 2640), "; 43 + 2 ->", RN.R119.fits(2580, 120, 2640))


if __name__ == "__main__":
    main()
