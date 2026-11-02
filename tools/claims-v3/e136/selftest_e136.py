#!/usr/bin/env python3
"""E136 (Q137): the self-test. Every rule of reduce_e136.score() on made-up rows, once passing and once failing, and run_e136.preflight refusing a
protocol whose binaries are not the registered ones. No card, no data.

    python3 tools/claims-v3/e136/selftest_e136.py > tools/claims-v3/e136/selftest.txt
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e136 as RD  # noqa: E402
import run_e136 as RUN  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e136.json")))
TYPES = ("fp32", "fp16", "int8")


def made_up(good):
    """per, cells, t800 that sit on the frozen numbers (good) or far off them (not good)"""
    per, cells, t800 = {}, {}, {}
    k = 1.0 if good else 1.6
    for g in ("g4k", "g2k"):
        for t in TYPES:
            lw = P["laws"][f"{g}.{t}"]["P1"]
            per[f"{g}.{t}"] = {"T600": lw["T600_us"] * k, "n600": 3, "T800": lw["T800_us"] * k, "n800": 20, "X": lw["X"] if good else lw["X"] + 0.2, "how": "launch means", "fit": {}}
    for lab, c in P["cells"].items():
        g, t, kind = lab.split("-", 2)
        dk = 0.0 if good else 12.0
        cells[lab] = {"burst_p800_w_runs": [c["P_w"]["800"] + dk], "burst_rate": c["burst_rate"] * (1 if good else 0.8), "burst_mhz": c["burst_mhz"],
                      "sus_mhz": c["sus_mhz_G1"] - (0 if good else 90), "sus_w": c["sus_w_G1"] + dk, "sus_rate": c["sus_rate_G1"] * (1 if good else 0.8),
                      "burst_die_max": [round(52 + P["heat"]["k_burst_c_per_w"] * (c["burst_w"] - 21.5) + (0 if good else 8), 1)], "burst_die_start": [52],
                      "sus_die": round(RD.die_sus(P, lab, 55.0, "G1") + (0 if good else 7), 2), "sus_die_start": [55.0]}
        if kind == "zeros":
            cells[lab]["burst_rate"] = c["burst_rate"]
            cells[lab]["sus_rate"] = c["sus_rate_G1"]
        t800[lab] = P["laws"][f"{g}.{t}"]["P1"]["T800_us"] * (1 if (good or kind == "zeros") else 1.05)
    return per, cells, t800


def summary(V):
    return {"R0": V["R0"]["verdict"], "R1": V["R1"]["verdict"], "R1_point": V["R1"]["point"],
            "R2": [V["R2"]["per_format"][t]["point"] for t in TYPES], "R3_pass": f"{V['R3']['pass']}/{V['R3']['n']}",
            "R4_pass": V["R4"]["pass"], "R5_fail": sum(1 for c in V["R5"]["cells"].values() for x in c.values() if x["verdict"] == "FAIL"),
            "R6_fail": sum(1 for c in V["R6"]["cells"].values() for x in ([c["sus"]] if "sus" in c else []) + c.get("burst", []) if x["verdict"] == "FAIL"),
            "R7": V["R7"]["verdict"], "R8_fail": sum(1 for c in V["R8"]["cells"].values() for x in c.values() if x["verdict"] == "FAIL")}


def main():
    for good in (True, False):
        per, cells, t800 = made_up(good)
        V, E = RD.score(per, cells, t800, P, checks_ok=good)
        print(("ON THE FROZEN NUMBERS" if good else "FAR OFF THEM") + ":", json.dumps(summary(V)))
    # R1's placement: a T800 halfway between P1 and P2, then at P2
    per, cells, t800 = made_up(True)
    for name, f in (("halfway", 0.5), ("at P2", 0.0), ("past P2", -1.0)):
        p1, p2 = P["laws"]["g4k.fp32"]["P1"]["T800_us"], P["laws"]["g4k.fp32"]["P2"]["T800_us"]
        per["g4k.fp32"]["T800"] = p2 + f * (p1 - p2)
        V, _ = RD.score(per, cells, t800, P)
        print(f"R1 with T800 {name}: {V['R1']['per_format']['fp32']['verdict']} (h {V['R1']['per_format']['fp32']['h']})")
    # the preflight refuses other binaries
    with tempfile.TemporaryDirectory() as d:
        for rel in ("build/e136/host/sparsity_host", "build/e136/kernel/sparsity.elf", "build/ettelem-hpl/ettelem"):
            os.makedirs(os.path.join(d, os.path.dirname(rel)), exist_ok=True)
            open(os.path.join(d, rel), "wb").write(b"not the registered binary")
        why = RUN.preflight(json.load(open(os.path.join(HERE, "protocol.json"))), d)
        print("preflight on other binaries:", "REFUSED" if why else "accepted (WRONG)", "-", (why or "")[:120])
        why = RUN.preflight({"tools": {"heater": "build/e119/host/sparsity_host"}}, d)
        print("preflight on E119's heater path:", "REFUSED" if why else "accepted (WRONG)")


if __name__ == "__main__":
    main()
