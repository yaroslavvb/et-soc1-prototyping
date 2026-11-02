#!/usr/bin/env python3
"""E134 self-test (Q136): what the registered design can decide, before any data. It builds per-run tables on E134's real
block orders (e134_common.pass_order) and the registered sequence, with each item at a chosen truth over its own zero, and
scores them with score_e134.py's own Book and rules. Standard library only. Nothing here is a measurement.

    python3 tools/claims-v3/e134/selftest_e134.py [--sessions 40] > tools/claims-v3/e134/selftest.txt

Each simulated run: zero level + truth step + a warm-up curve (2 W amplitude, tau 45 s from the block's start, E102's float
trains, check_e102.txt [M]) + a random walk of 0.01 W a run + carry-over of 5% of the previous run's step (pessimistic: the
rail's is 7.8%, E102 A1) + white noise sigma. A train run is 4.86 s (E102's). Worlds:
  bench        every item at the bench's frozen step (predictions-e134.json items.*.pred_W.bench)
  position     A items at E67's list for their bit (the same on both words), B at the bench
  later        the bench, but B's swing starts two bits later (bits 8 and 9 at the balanced price x 4096/3968)
  earlier      the bench, but bit 7's all-in item carries 0.20 W of swing
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e134_common as ec  # noqa: E402
import score_e134 as sc  # noqa: E402

RUN_S = 4.86


def truths(reg, world):
    t = {}
    for name, it in reg["items"].items():
        b = it["pred_W"]["bench"]
        if world == "position" and it["side"] == "a":
            b = it["pred_W"]["position_only_e67"]
        t[name] = b
    if world == "later":
        for j in (8, 9):
            t[f"fp32.bj_{j}"] = t[f"fp32.bp_{j}"] * reg["design"]["balanced_to_allin_flip_scale_B"]
    if world == "earlier":
        t["fp32.bj_7"] = t["fp32.bp_7"] * reg["design"]["balanced_to_allin_flip_scale_B"] + 0.20
    return t


def session(reg, items, truth, sigma, rng, blocks):
    zl = {"fp32.aq": 41.00, "fp32.a67q": 41.04, "fp32.hq": 41.20}
    runs = []
    t0 = 0.0
    for p in blocks:
        order = ec.pass_order(items, "aifoundry3", p)
        walk = 0.0
        prev_step = 0.0
        tb = t0
        for r in order:
            name = r["item"]
            it = reg["items"].get(name)
            z = it["zero"] if it else name
            step = truth[name] if it else 0.0
            walk += rng.gauss(0, 0.01)
            warm = -2.0 * pow(2.718281828, -(t0 - tb) / 45.0)
            v = zl[z] + step + warm + walk + 0.05 * prev_step + rng.gauss(0, sigma)
            prev_step = step
            runs.append({"pass": p, "item": name, "segment": r["segment"], "t0": t0 * 1000.0, "p_raw": v, "p80": v,
                         "rail_raw": v, "rate": reg["design"]["rate_ops_per_s"], "fail": 0, "fail_reasons": "",
                         "t_win": None, "start_c": None, "mv": None, "pos": r["pos"]})
            t0 += RUN_S
        t0 += 25.0
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=40)
    a = ap.parse_args()
    reg = json.load(open(sc.REG))
    tiles = json.load(open(sc.TILES))["tiles"]
    items = ec.load_items()
    seq = reg["plan"]["sequence"]
    plans = {"A4 B5 (the budget's expectation)": seq[:9], "A4 B4": seq[:8], "A3 B3": seq[:6]}
    print("E134 self-test: verdicts over simulated sessions (counts out of the number of sessions); nothing here is a measurement")
    print(f"R2 contrast (bench) {reg['rules']['E134-R2']['bench_W']:+.3f} W, threshold {reg['rules']['E134-R2']['word_threshold_w']:.3f} W; "
          f"R4 bits {reg['rules']['E134-R4']['quiet_bit']}/{reg['rules']['E134-R4']['onset_bit']}; R5 bits {reg['rules']['E134-R5']['bits']}")
    for pname, blocks in plans.items():
        for world in ("bench", "position", "later", "earlier"):
            for sigma in (0.025, 0.035):
                rng = random.Random(f"E134-selftest|{pname}|{world}|{sigma}")
                tally = {}
                hw = {"R2": [], "R4q": [], "R4o": [], "R1_0": [], "R1_6": []}
                for _ in range(a.sessions):
                    runs = session(reg, items, truths(reg, world), sigma, rng, blocks)
                    res = sc.score(runs, {}, tiles, reg)
                    for r, v in res["rules"].items():
                        tally.setdefault(r, {}).setdefault(v["verdict"], 0)
                        tally[r][v["verdict"]] += 1
                    st = res["statistics"]
                    c = st["contrasts_W"]["A_word_allin_6"]
                    if c["ci95"] is not None:
                        hw["R2"].append(c["ci95"])
                    q = st["contrasts_W"][f"B_swing_{reg['rules']['E134-R4']['quiet_bit']}"]
                    o = st["contrasts_W"][f"B_swing_{reg['rules']['E134-R4']['onset_bit']}"]
                    if q["ci95"] is not None:
                        hw["R4q"].append(q["ci95"])
                        hw["R4o"].append(o["ci95"])
                    for j in (0, 6):
                        r_ = st["ratios_per_flip"][f"A_W79_allin_over_bal_{j}"]
                        if r_.get("hi") is not None:
                            hw[f"R1_{j}"].append((r_["hi"] - r_["lo"]) / 2)
                med = {k: (sorted(v)[len(v) // 2] if v else None) for k, v in hw.items()}
                print(f"\n[{pname}] world={world} sigma={sigma} W a run, {a.sessions} sessions")
                for r in sorted(tally):
                    print(f"  {r}: " + ", ".join(f"{k} {n}" for k, n in sorted(tally[r].items(), key=lambda x: -x[1])))
                print("  median 95% half-widths: " + ", ".join(f"{k} {v:.3f}" for k, v in med.items() if v is not None))


if __name__ == "__main__":
    main()
