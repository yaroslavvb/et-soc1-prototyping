#!/usr/bin/env python3
"""E102 amendment A1: its scorer on synthetic blocks through the real orders, written before any A1 data. Standard library only.

    python3 tools/claims-v3/kinds/selftest_e102a1.py      # prints the cases and the rule's power at the noise A1 expects; exit 1 on a miss
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e102a1_common as a1   # noqa: E402
import score_e102 as sc      # noqa: E402
import score_e102a1 as sa    # noqa: E402

reg = json.load(open(sc.REG))
tiles = json.load(open(sc.TILES))["tiles"]
RATE = reg["analysis"]["rate_ops_per_s"]["fp32"]
STUB = {"primary": {"rules": {"E102-R2": {"rail_arm": {"cells": {"22": {"ratio": 2.2, "lo": 1.8, "hi": 3.0, "n": 4}}}, "board_arm": {"cells": {"22": {"ratio": 2.2, "lo": 1.8, "hi": 3.0, "n": 4}}}}}}}


def runs(step, sigma, seed, curve=(0.7, 30.0), jump=None, passes=(10240, 10241, 10242, 10243)):
    rng = random.Random(seed)
    out = []
    t = 0.0
    for p in passes:
        for pos, it in enumerate(a1.order(p)):
            s = step(it) if it != a1.Z else 0.0
            w = -curve[0] * 2.71828 ** (-t / 1000 / curve[1])
            b = 44.0 + s + w + rng.gauss(0, sigma)
            r = 20.0 + 0.81 * s + 0.8 * w + rng.gauss(0, sigma)
            if jump and jump[0] == p and pos == jump[1]:
                r += jump[2]
            out.append({"pass": p, "item": it, "pos": pos, "segment": 0, "t0": t, "p_raw": b, "p80": b, "rail": r, "rate": RATE, "fail": 0, "t_win": 60.0, "start_c": 60.0, "D": None, "mv": 499.0})
            t += 4800.0
        t += 18000.0
    return out


def main():
    bad = []
    p = reg["positions"]
    bench = lambda it: p[it]["pred_w"]["bench_map"]                           # noqa: E731
    gate = reg["analysis"]["gates"]["train_zero_mid_departure_rail_w"]
    # the design's arithmetic
    for q in (10240, 10241):
        o = a1.order(q)
        assert o.count("fp32.aj_6") == 2 and o.count("fp32.ap_0") == 2 and len(o) == (18 if q == 10240 else 13), o
        pairs = [o[i:i + 2] for i in range((5 if q == 10240 else 0) + 1, len(o), 3)]
        assert all(a1.Z not in x for x in pairs), pairs
    assert a1.order(10214)[0] == "anchor_pi" and a1.order(10214)[1] == "fp32.hq" and sorted(a1.order(10214)[2:8]) == sorted(a1.SHORT_G_ITEMS)
    # truth: the bench, no noise
    r = sa.score(runs(bench, 1e-4, 1), reg, tiles, STUB, gate)
    print("bench truth, no noise:", r["verdict"], r["arms"]["board"]["verdict"], {j: round(r["arms"]["rail"]["cells"][j]["ratio"], 3) for j in ("0", "6")})
    if r["verdict"] != "POSITION":
        bad.append("bench truth should read POSITION")
    want = (bench("fp32.aj_6") / 2048) / (bench("fp32.ap_6") / 1920)
    if abs(r["arms"]["rail"]["cells"]["6"]["ratio"] - want) > 0.02:
        bad.append(f"bit 6 ratio {r['arms']['rail']['cells']['6']['ratio']} against {want}")
    # truth: a constant 7x
    r = sa.score(runs(lambda it: bench(it) if "aj" in it else bench(it.replace("ap_", "aj_")) / 7.0 * 1920 / 2048, 1e-4, 2), reg, tiles, STUB, gate)
    print("7x truth, no noise:", r["verdict"], {j: round(r["arms"]["rail"]["cells"][j]["ratio"], 3) for j in ("0", "6")})
    if r["verdict"] != "CONSTANT":
        bad.append("7x truth should read CONSTANT")
    # the settling reads never count, and a jump on an interior zero sets the block aside; the warm-up alone does not
    r = sa.score(runs(bench, 1e-4, 3, jump=(10241, 3, 1.0)), reg, tiles, STUB, gate)
    print("a 1 W jump on a zero:", r["set_aside"], r["passes_kept"])
    if not any(x["pass"] == 10241 for x in r["set_aside"]):
        bad.append("a 1 W jump should set the block aside")
    # power, at the neighbour noise the desk measured, truth from E102's own T steps on the rail
    steps = {"fp32.aj_0": 0.31 / 0.81, "fp32.ap_0": 0.259 / 0.81, "fp32.aj_6": 0.181 / 0.81, "fp32.ap_6": 0.167 / 0.81}
    for sigma in (0.044, 0.06):
        for ps in ((10240, 10241, 10242, 10243), (10240, 10241, 10242)):
            tally = {}
            hw = []
            for s in range(200):
                r = sa.score(runs(steps.get, sigma, 100 + s, passes=ps), reg, tiles, STUB, gate)
                tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
                hw.append(r["arms"]["rail"]["cells"]["6"]["fp32.ap_6"]["W"]["ci95"])
            print(f"sigma {sigma} W a run, {len(ps)} blocks, truth at E102's T steps: {tally} of 200; median half-width on ap_6 {sorted(hw)[100]:.3f} W")
    print("selftest:", "ALL OK" if not bad else f"MISSES {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
