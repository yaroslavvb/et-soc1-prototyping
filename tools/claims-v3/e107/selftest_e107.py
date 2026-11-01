#!/usr/bin/env python3
"""E107's self-test: score_e107.score() on made-up rows. The frozen world (every cell at its frozen number) must give the frozen verdicts, and each rule
must fail or flip on a world built to break it. Writes selftest.txt beside it. Standard library only.

    python3 tools/claims-v3/e107/selftest_e107.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e107_common as e7  # noqa: E402
import score_e107 as sc  # noqa: E402

PRED = json.load(open(os.path.join(HERE, "predictions-e107.json")))
P = PRED["predictions"]


def world(T=None, S_add=0.0, kind_T=None, droop=None):
    """Items and rails at the frozen numbers, with overrides: T {arm.type: us}, kind_T {item: factor}, droop {arm: mV}."""
    T = dict(P["T_us"], **(T or {}))
    items, rails = {}, {}
    dr = {"c1": 0.6, "c8s": 0.9, "c4s": 0.9, "c16": 2.6, **(droop or {})}
    for a in e7.ARMS:
        for ty in sc.TYPES:
            for k in e7.arm_kinds(a):
                kn = e7.kind_name(ty, k)
                name = f"{a}.{ty}.{kn}"
                t = T[f"{a}.{ty}"] * (kind_T or {}).get(name, 1.0)
                rate = 1024 / (t * 1e-6)
                s = P["S_w"].get(name, 10.0) + S_add
                eop = s / rate * 1e12
                items[name] = {"rate": {"mean": rate, "ci95": rate * 1e-3}, "S": {"mean": s}, "pj_op_S": {"mean": eop}, "pj_mac_S": {"mean": eop / 4096},
                               "cycles_per_op": t * 600}
                rails[name] = {"ddr_droop_mv": {"mean": dr.get(a, 1.5)}}
    return items, rails


def verdicts(items, rails):
    s = sc.score(items, rails, PRED)
    return {k: v["verdict"] for k, v in s["rules"].items()}


def main():
    L = []
    base = verdicts(*world())
    L.append(f"frozen world: {base}")
    want = {"R1_tie": "PASS", "R2_kind": "PASS", "R3_reuse": "REUSE IS THE VARIABLE", "R4b_resident": "PASS", "R4_walk": "DRAM SETS MOST OF IT",
            "R4c_dram_check": "PASS", "R5_c_in_l3": "C ALLOCATES", "R6_c_traffic": "PART OF THE LIMIT", "R7_power": "PASS", "R8_energy_order": "PASS"}
    bad = [k for k, v in want.items() if base[k] != v]
    t16 = {ty: P["T_us"][f"c16.{ty}"] for ty in sc.TYPES}
    cases = [
        ("R1 fails: c1 5% slow", dict(T={f"c1.{ty}": P["T_us"][f"c1.{ty}"] * 1.05 for ty in sc.TYPES}), "R1_tie", "FAIL"),
        ("R2 fails: random 2% slower than zeros in c8s fp32", dict(kind_T={"c8s.fp32.randn": 1.02}), "R2_kind", "FAIL"),
        ("R3: every repeat as slow as the cold walk", dict(T={f"{a}.{ty}": t16[ty] for a in ("c16r2", "c16r4", "c16r8", "c16r32") for ty in sc.TYPES}),
         "R3_reuse", "NOT THE VARIABLE"),
        ("R3: the law's shape off (R=4 at R=2's time)", dict(T={f"c16r4.{ty}": P["T_us"][f"c16r2.{ty}"] for ty in sc.TYPES}), "R3_reuse", "PARTIAL"),
        ("R4: the L3 walk as slow as DRAM's", dict(T={f"{a}.{ty}": t16[ty] * 0.97 for a in ("c8s", "c4s") for ty in sc.TYPES}), "R4_walk", "NOT DRAM"),
        ("R4: between", dict(T={f"{a}.{ty}": P["T_us"][f"c1.{ty}"] + 0.65 * (t16[ty] - P["T_us"][f"c1.{ty}"]) for a in ("c8s", "c4s") for ty in sc.TYPES}),
         "R4_walk", "SHARED"),
        ("R4b: 26 MB not resident (c8s at c16, c4s frozen)", dict(T={f"c8s.{ty}": t16[ty] for ty in sc.TYPES}), "R4b_resident", "FAIL"),
        ("R4c: c8s droops as c16 does", dict(droop={"c8s": 2.6}), "R4c_dram_check", "FAIL"),
        ("R5: c8 as fast as c8s", dict(T={f"c8.{ty}": P["T_us"][f"c8s.{ty}"] for ty in sc.TYPES}), "R5_c_in_l3", "C DOES NOT DISPLACE"),
        ("R6: c16s as slow as c16", dict(T={f"c16s.{ty}": t16[ty] for ty in sc.TYPES}), "R6_c_traffic", "NOT THE LIMIT"),
        ("R7: every S 3 W high", dict(S_add=3.0), "R7_power", "FAIL"),
    ]
    for label, kw, rule, expect in cases:
        v = verdicts(*world(**kw))
        ok = v[rule] == expect
        L.append(f"{'ok ' if ok else 'BAD'} {label}: {rule} -> {v[rule]} (want {expect})")
        if not ok:
            bad.append(label)
    e = world()
    items, rails = copy.deepcopy(e[0]), e[1]
    items["c16r4.fp32.randn"]["pj_op_S"]["mean"] = items["c16r2.fp32.randn"]["pj_op_S"]["mean"] * 1.01
    v = verdicts(items, rails)["R8_energy_order"]
    L.append(f"{'ok ' if v == 'FAIL' else 'BAD'} R8: c16r4 above c16r2: R8_energy_order -> {v} (want FAIL)")
    if v != "FAIL":
        bad.append("R8")
    L.append("ALL OK" if not bad else f"PROBLEMS: {bad}")
    open(os.path.join(HERE, "selftest.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
