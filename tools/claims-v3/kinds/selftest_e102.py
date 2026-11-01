#!/usr/bin/env python3
"""E102 (Q132): the scorer on synthetic passes, written before any pass exists. Each case builds a full set of blocks from e102_common's real orders, gives every item a known step over its own zero and
noise at the card's measured size, and checks that score_e102.py returns the verdict the truth implies. Standard library only.

    python3 tools/claims-v3/kinds/selftest_e102.py          # prints the cases; exit 1 on any miss
"""
import csv
import json
import math
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e102_common as e102   # noqa: E402
import score_e102 as sc      # noqa: E402

reg = json.load(open(os.path.join(HERE, "predictions-e102.json")))
tiles = json.load(open(os.path.join(HERE, "e102", "e102.json")))["tiles"]
RATE = reg["analysis"]["rate_ops_per_s"]
SEQ = reg["plan"]["sequence"]
ITEMS = e102.load_items()
FIELDS = ["pass", "item", "pos", "segment", "t0_ms", "p_raw", "p80", "rail_raw", "rate", "fail", "t_win", "start_c", "D", "mv", "fail_reasons"]


def rows_for(step, sig_b, sig_r, seed, settle_w=0.0, bad_pass=None):
    """step(name) -> board watts over the item's own zero. Rail = 0.81 x board step. A level per type, a slow drift per pass, white noise per run."""
    rng = random.Random(seed)
    out = []
    t0 = 1_000_000.0
    for p in SEQ:
        order = e102.pass_order(ITEMS, "aifoundry1-c1", p)
        drift = rng.uniform(-0.0007, 0.0007)      # W per s: anchor_pi drifts up to about 0.4 W in a 10 min pass
        for row in order:
            n = row["item"]
            ty = n.split(".")[0] if n != "anchor_pi" else "fp32"
            level = {"fp32": 44.0, "fp16": 44.0, "int8": 36.0}[ty]
            s = 0.0
            if n in tiles and tiles[n]["layout"] != "zero":
                s = step(n)
            tmin = (t0 - 1_000_000.0) / 1000.0
            b = level + s + drift * tmin + rng.gauss(0, sig_b)
            r = 0.45 * level + 0.81 * s + 0.8 * drift * tmin + rng.gauss(0, sig_r)
            if row["segment"] == -1:      # settling runs never count: make them far off
                b += settle_w
                r += settle_w
            if bad_pass == p and n == "int8.hq" and row["pos"] == 15:
                r += 1.0
            D = None
            out.append({"pass": p, "item": n, "pos": row["pos"], "segment": row["segment"], "t0_ms": t0, "p_raw": b, "p80": b, "rail_raw": r, "rate": RATE[ty], "fail": 0, "t_win": 58.0, "start_c": 58.0, "D": D, "mv": 499.0, "fail_reasons": ""})
            t0 += 4750.0 if p >= 10220 else 9700.0
        t0 += 60000.0
    return out


def run_case(step, sig_b, sig_r, seed, **kw):
    with tempfile.TemporaryDirectory() as d:
        rows = rows_for(step, sig_b, sig_r, seed, **kw)
        with open(os.path.join(d, "runs.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        json.dump({"passes_set_aside": [], "passes_config_flags": [], "runs": len(rows), "kept": len(rows), "failed": [], "leak": {"k_w_per_c": 0.2414}, "clock_mhz": 600, "v_mean": 0.499}, open(os.path.join(d, "e102.json"), "w"))
        return sc.run_one(os.path.join(d, "runs.csv"), os.path.join(d, "e102.json"), tiles, reg)


def bench_step(n):
    return reg["positions"][n]["pred_w"]["bench_map"]


def ratio_step(n):
    """The page's implication: every balanced price is the all-in price over 7 (fp32) or 5.6 (fp16). Sign and exponent too. int8: E79's list."""
    p = reg["positions"][n]["pred_w"]
    if "ratio_hypothesis" in p:
        return p["ratio_hypothesis"]
    if "all_in_list" in p:
        return p["all_in_list"]
    return p["e79_measured"]


def check(name, res, want):
    bad = []
    for k, v in want.items():
        got = res["rules"][k]["verdict"]
        ok = got in v if isinstance(v, (list, tuple)) else got == v
        if not ok:
            bad.append(f"{k}: {got}, wanted {v}")
    print(f"{name}: " + ("ok" if not bad else "MISS " + "; ".join(bad)))
    print("   " + "; ".join(f"{k.split('-')[1]} {v['verdict']}" for k, v in res["rules"].items()))
    return bad


def main():
    bad = []
    # 0. the arithmetic
    r = sc.fieller({1: 2.0, 2: 2.2, 3: 1.8}, {1: 1.0, 2: 1.1, 3: 0.9})
    assert abs(r["ratio"] - 2.0) < 1e-9 and r["paired"] and r["lo"] == r["lo"]
    r = sc.fieller({1: 2.0, 2: 2.0, 3: 2.0}, {4: 1.0, 5: 1.0, 6: 1.0})
    assert r["paired"] is False and abs(r["ratio"] - 2.0) < 1e-9
    r = sc.fieller({1: 1.0, 2: 1.0, 3: 1.0}, {1: 0.1, 2: -0.1, 3: 0.2})
    assert r["lo"] is None, "a denominator whose interval contains zero leaves the ratio unbounded"
    assert abs(sc.interp([(0.0, 0.0), (10.0, 10.0)], 5.0) - 5.0) < 1e-9 and sc.interp([(0.0, 1.0), (10.0, 3.0)], 20.0) == 3.0
    m = sc.mean_ci([1.0, 2.0, 3.0])
    assert abs(m["ci95"] - 4.303 * 1.0 / math.sqrt(3)) < 1e-3
    print("arithmetic: ok")
    # 1. truth = the bench, noiseless: every rule that reads the truth returns what the registration's table says
    res = run_case(bench_step, 1e-4, 1e-4, 1)
    bad += check("bench truth, no noise", res, {"E102-R1": "POSITION", "E102-R2": "POSITION", "E102-R3": "INVERTED", "E102-R4": "CONFIRMED", "E102-R6": "CONFIRMED", "E102-R7": "CONFIRMED",
                                                "E102-R8": "BENCH-LEVEL", "E102-R9": "FLAT", "E102-R10": "RISE", "E102-R11": "CONFIRMED"})
    for j in (0, 22):
        c = res["rules"]["E102-R1"]["board_arm"]["cells"][str(j)]
        want_ratio = (bench_step(f"fp32.bj_{j}") / 4096) / (bench_step(f"fp32.bp_{j}") / 3968)
        assert abs(c["ratio"] - want_ratio) < 0.01, (j, c["ratio"], want_ratio)
    f = res["prices"]["fp32.bp_22@T"]["board"]["fJ"]["mean"]
    want_f = bench_step("fp32.bp_22") / (3968 * RATE["fp32"]) * 1e15
    assert abs(f - want_f) < 2.0, (f, want_f)     # drift past a zero's last read is flat by the registered rule
    # 2. truth = the bench, at the card's noise: the design must decide its registered rules. Report how often, over seeds.
    tallies = {}
    for s in range(20):
        res = run_case(bench_step, reg["analysis"]["noise_from_e93_w"]["p_raw"], reg["analysis"]["noise_from_e93_w"]["rail_raw"], 100 + s)
        for k, v in res["rules"].items():
            if k == "E102-S1":
                continue
            tallies.setdefault(k, {}).setdefault(v["verdict"], 0)
            tallies[k][v["verdict"]] += 1
    print("bench truth, E93's noise, 20 seeds (the design's power):", json.dumps(tallies))
    if tallies["E102-R1"].get("POSITION", 0) < 14:
        bad.append("R1 decides POSITION in fewer than 14 of 20 at the card's noise")
    # 3. truth = the page's implication (a constant ratio): R1 must say CONSTANT, not POSITION
    res = run_case(ratio_step, 1e-4, 1e-4, 2)
    bad += check("constant-ratio truth, no noise", res, {"E102-R1": "CONSTANT", "E102-R2": "CONSTANT", "E102-R3": "COMPOSITE"})
    # 4. truth = E79's int8 list: R8 and R9 turn
    def e79_int8(n):
        return reg["positions"][n]["pred_w"].get("e79_measured", bench_step(n))
    res = run_case(lambda n: e79_int8(n) if n.startswith("int8") else bench_step(n), 1e-4, 1e-4, 3)
    bad += check("E79's int8 truth, no noise", res, {"E102-R8": "E79-LEVEL", "E102-R9": "SHAPE", "E102-R10": "FLAT"})
    # 5. a settling run far off moves nothing; a zero's jump sets that train aside by the trains' own gate
    a = run_case(bench_step, 1e-4, 1e-4, 4, settle_w=3.0)
    assert abs(a["prices"]["fp32.bp_6@T"]["rail"]["W"]["mean"] - 0.81 * bench_step("fp32.bp_6")) < 0.01
    a = run_case(bench_step, 1e-4, 1e-4, 5, bad_pass=10230)
    assert any(x["pass"] == 10230 for x in a["passes_set_aside_by_own_gate"]) and a["passes_kept"]["I"] == [10231, 10232, 10233, 10234], a["passes_set_aside_by_own_gate"]
    print("settling runs and the trains' gate: ok")
    print("selftest:", "ALL OK" if not bad else f"{len(bad)} MISSES: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
