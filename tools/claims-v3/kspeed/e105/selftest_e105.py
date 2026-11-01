#!/usr/bin/env python3
"""E105 (Q132): the scorer's self-test: every rule can fail. Made-up rows, no card, no data.

    python3 selftest_e105.py > selftest.txt
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e105 as RE  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e105.json")))
RULES, LAWS = P["rules"], P["laws"]


def rows(C, M, fs=(600, 650, 700, 750, 800)):
    return [(f, C / f + M) for f in fs for _ in range(4)]


def cells_for(Mc, Mv, Ma, fz=800.0, fx=620.0):
    def rate(C, M, f):
        return 1.0 / (C / f + M)
    out = {}
    for arm, C, M in (("gemmc1", 529.0, Mc), ("gemmv1", 344.3, Mv), ("gemm1", 344.3, Ma)):
        out[f"{arm}-fp32-zeros"] = {"sus_rate": rate(C, M, fz), "sus_mhz": fz, "burst_rate": rate(C, M, fz), "burst_mhz": fz}
        out[f"{arm}-fp32-sparse25"] = {"sus_rate": rate(C, M, fx), "sus_mhz": fx, "burst_rate": rate(C, M, 720.0), "burst_mhz": 720.0}
    out["gemmc1-int8-zeros"] = {"sus_rate": rate(280.5, Mc, fz), "sus_mhz": fz, "burst_rate": rate(280.5, Mc, fz), "burst_mhz": fz}
    out["gemmc1-int8-full"] = {"sus_rate": rate(280.5, Mc, 600.0), "sus_mhz": 600.0, "burst_rate": rate(280.5, Mc, 700.0), "burst_mhz": 700.0}
    return out


def case(name, Cc, Mc, Mv, Ma, want):
    fits = {"gemmc1.fp32": RE.fit(rows(Cc, Mc)), "gemmv1.fp32": RE.fit(rows(344.3, Mv)), "gemm1.fp32": RE.fit(rows(344.3, Ma))}
    t800 = {"gemmc1-fp32-zeros": Cc / 800 + Mc, "gemmv1-fp32-zeros": 344.3 / 800 + Mv, "gemm1-fp32-zeros": 344.3 / 800 + Ma, "gemmh1-fp32-zeros": 529.0 / 800 + Mc}
    V = RE.score(fits, cells_for(Mc, Mv, Ma), t800, RULES, LAWS)
    got = {"R1": V["R1"]["verdict"], "R2": V["R2"]["verdict"], "R3": V["R3"]["verdict"], "R4": V["R4"]["verdict"], "R5": V["R5"]["verdict"], "R6": V["R6"]["verdict"], "R7c": V["R7"]["cells"]["gemmc1"]["verdict"], "R9": V["R9"]["verdict"]}
    ok = all(got[k] == v for k, v in want.items())
    print(f"{name:34s} {'ok' if ok else 'WRONG'}  {json.dumps(got)}  R4 rate {V['R4']['rate']} clock {V['R4']['clock']}, R5 {V['R5']['rate']}, R6 {V['R6']['as_run']} {V['R6']['vendor']} {V['R6']['bycol']}")
    return ok


def admission_case():
    """run_e105's rule on made-up measures: a probe admits or refuses, no probe refuses, the 93 W lock holds."""
    import tempfile
    sys.path.insert(0, os.path.join(HERE, "..", "e101"))
    sys.path.insert(0, os.path.join(HERE, "..", "..", "kinds"))
    import run_e105 as RU
    proto = json.load(open(os.path.join(HERE, "protocol.json")))
    with tempfile.TemporaryDirectory() as d:
        adm = RU.Admission(proto, os.path.join(d, "s1"))
        oks = []

        def want(lab, admitted):
            why, est, how = adm.why_not(lab)
            ok = (why is None) == admitted
            oks.append(ok)
            print(f"  {lab:30s} est {est} ({how}) -> {why or 'admitted'}: {'ok' if ok else 'WRONG'}")
        print("admission rule, no probe measured yet:")
        want("gemmc1-fp32-zeros", True)
        want("gemmc1-fp32-sparse25", False)
        want("gemmc1-fp32-randn", False)
        want("no-such-cell", False)
        print("the probe reads rho 1.08, the model's by-column guess:")
        adm.state["rho"]["gemmc1-fp32-sparse50"] = 1.08
        want("gemmc1-fp32-sparse25", True)
        want("gemmc1-fp32-sparse25-rep2", True)
        want("gemmc1-fp32-randn", False)
        want("gemmc1-fp32-randn-half", True)
        print("the probe reads rho 0.75, misses still holding the rate down:")
        adm.state["rho"]["gemmc1-fp32-sparse50"] = 0.75
        want("gemmc1-fp32-randn", True)
        print("a run at 80 W read 93 W, so nothing at or above 80 W goes on:")
        adm.state["lock_est"] = 80.0
        want("gemmc1-fp32-randn", False)
        want("gemmc1-fp32-zeros", True)
    return all(oks)


def main():
    good = True
    good &= case("the desk model holds", 529.0, 0.0, 0.468, 0.838, {"R1": "PASS", "R2": "PASS", "R3": "PASS", "R4": "COMES BACK", "R5": "COMES BACK", "R6": "PASS", "R7c": "PASS", "R9": "PASS"})
    good &= case("by column changes nothing", 344.3, 0.838, 0.838, 0.838, {"R1": "FAIL", "R2": "FAIL", "R3": "PASS", "R7c": "FAIL", "R9": "FAIL"})
    good &= case("by column half way", 400.0, 0.30, 0.468, 0.838, {"R1": "PARTIAL", "R2": "PASS", "R7c": "FAIL"})
    good &= case("strides as good as by column", 529.0, 0.0, 0.02, 0.838, {"R1": "PASS", "R2": "FAIL", "R3": "PASS"})
    good &= case("the rebuilt arm is not the old one", 529.0, 0.0, 0.30, 0.60, {"R3": "FAIL"})
    f = RE.fit([(800.0, 0.661)] * 8)
    print("no span:", f, "->", RE.score({"gemmc1.fp32": f}, {}, {}, RULES, LAWS)["R1"]["verdict"])
    good &= RE.score({"gemmc1.fp32": f}, {}, {}, RULES, LAWS)["R1"]["verdict"] is None
    good &= admission_case()
    print("selftest", "PASS" if good else "FAIL")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
