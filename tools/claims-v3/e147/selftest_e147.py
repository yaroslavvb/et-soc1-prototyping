#!/usr/bin/env python3
"""E147 self-test (Q138): what the registered design can decide, before any data. It builds per-run tables on E147's real
block orders (e147_common.pass_order) and the registered sequence, with each item at a chosen truth over its own zero, and
scores them with score_e147.py's own Book and rules. Standard library only. Nothing here is a measurement. A port of
tools/claims-v3/e134/selftest_e134.py (the same simulated run).

    python3 tools/claims-v3/e147/selftest_e147.py [--sessions 40] > tools/claims-v3/e147/selftest.txt

Each simulated run: zero level + truth step + a warm-up curve (2 W amplitude, tau 45 s from the block's start, E102's float
trains) + a random walk of 0.01 W a run + carry-over of 5% of the previous run's step (pessimistic: the rail's is 7.8%,
E102 A1) + white noise sigma. A train run is 4.86 s (E102's). Worlds:
  bench        every item at the bench's frozen step (predictions-e147.json items.*.pred_W.bench)
  m6           every item at M6's frozen step (items.*.pred_W.m6)
  position     A items at E67's list for their bit (the same on both words), B at the bench (the word does nothing)
  scaled       the bench, every A word difference at 0.67 of the bench's (E134's measured-over-bench factor) and every B
               swing 1.15 x the bench's (E134's, post hoc)
  reading      the bench, but bit 19's two W67 items at their W79 twins' steps (E134's digit reading: the same digit changes,
               the same price), the world in which R5 should hold
  bench_c3     the bench world with a 3% carry-over instead of 5%: E134's board read 2.8% +- 0.8% per W of the preceding
               step in its zero reads, post hoc (carry_e134.py); E147's B blocks hold steps of 3-4.5 W, so the carry-over is
               the noise that matters most here
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e147_common as ec  # noqa: E402
import score_e147 as sc  # noqa: E402

RUN_S = 4.86


def truths(reg, world):
    t = {}
    for name, it in reg["items"].items():
        b = it["pred_W"]["m6" if world == "m6" else "bench"]          # bench_c3: the bench's truths
        if world == "position" and it["side"] == "a":
            b = it["pred_W"]["position_only"]
        t[name] = b
    if world == "reading":
        t["fp32.a67j_19"], t["fp32.a67p_19"] = t["fp32.aj_19"], t["fp32.ap_19"]
    if world == "scaled":
        for j in sc.A67_BITS:
            for a, b in ((f"fp32.a67j_{j}", f"fp32.aj_{j}"), (f"fp32.a67p_{j}", f"fp32.ap_{j}")):
                t[a] = t[b] + 0.67 * (t[a] - t[b])
        s = reg["design"]["balanced_to_allin_flip_scale_B"]
        for j in sc.B_BITS + sc.B_LINK:
            sw = t[f"fp32.bj_{j}"] - s * t[f"fp32.bp_{j}"]
            t[f"fp32.bj_{j}"] += 0.15 * sw
    return t


def session(reg, items, truth, sigma, rng, blocks, carry=0.05):
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
            v = zl[z] + step + warm + walk + carry * prev_step + rng.gauss(0, sigma)
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
    plans = {"A4 B4 (the budget's expectation)": seq[:8], "A3 B3": seq[:6]}
    print("E147 self-test: verdicts over simulated sessions (counts out of the number of sessions); nothing here is a measurement")
    print(f"R4 bits {reg['rules']['E147-R4']['bits']}; R5 signed {reg['rules']['E147-R5']['signed_bits']}, same "
          f"{reg['rules']['E147-R5']['same_bit']}; M1 line {reg['rules']['E147-M1']['rms_line_w']} W")
    for pname, blocks in plans.items():
        for world in ("bench", "m6", "position", "scaled", "reading", "bench_c3"):
            for sigma in (0.025, 0.035):
                rng = random.Random(f"E147-selftest|{pname}|{world}|{sigma}")
                tally = {}
                hw = {"word": [], "Bswing_low": [], "Bswing_hi": [], "Aitem": [], "Bitem": [], "m6_rms": []}
                for _ in range(a.sessions):
                    runs = session(reg, items, truths(reg, world), sigma, rng, blocks, 0.03 if world == "bench_c3" else 0.05)
                    res = sc.score(runs, {}, tiles, reg)
                    for r, v in res["rules"].items():
                        tally.setdefault(r, {}).setdefault(v["verdict"], 0)
                        tally[r][v["verdict"]] += 1
                    st = res["statistics"]["contrasts_W"]
                    for j in sc.A67_BITS:
                        if st[f"A_word_allin_{j}"]["ci95"] is not None:
                            hw["word"].append(st[f"A_word_allin_{j}"]["ci95"])
                    for j in (1, 2, 3, 4, 5):
                        if st[f"B_swing_{j}"]["ci95"] is not None:
                            hw["Bswing_low"].append(st[f"B_swing_{j}"]["ci95"])
                    for j in (17, 18, 19, 21):
                        if st[f"B_swing_{j}"]["ci95"] is not None:
                            hw["Bswing_hi"].append(st[f"B_swing_{j}"]["ci95"])
                    for k, pr in res["prices"].items():
                        if pr["W"]["ci95"] is not None:
                            hw["Aitem" if k.startswith("a") else "Bitem"].append(pr["W"]["ci95"])
                    d = res["rules"]["E147-M1"]["detail"]
                    if d.get("rms_w") is not None:
                        hw["m6_rms"].append(d["rms_w"])
                med = {k: (sorted(v)[len(v) // 2] if v else None) for k, v in hw.items()}
                print(f"\n[{pname}] world={world} sigma={sigma} W a run, {a.sessions} sessions")
                for r in sorted(tally):
                    print(f"  {r}: " + ", ".join(f"{k} {n}" for k, n in sorted(tally[r].items(), key=lambda x: -x[1])))
                print("  medians (95% half-widths, W; m6_rms = M1's rms of measured minus M6): " +
                      ", ".join(f"{k} {v:.3f}" for k, v in med.items() if v is not None))


if __name__ == "__main__":
    main()
