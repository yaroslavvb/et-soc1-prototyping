#!/usr/bin/env python3
"""E130 self-test (Q136): synthetic per-run tables in the shape reduce_e130.py writes (runs.csv), built on E130's REAL block
orders (e130_common.pass_order) and the registered sequence, scored by score_e130.py, in worlds whose truth is a netlist's
frozen prediction. Nothing here is a measurement. Standard library only.

    python3 tools/claims-v3/e130/selftest_e130.py [--sessions 40] [--sigma 0.025] > tools/claims-v3/e130/selftest.txt

Each run reads its item's level plus a slow drift (a block-long curve of 0.3 W and a random walk of 0.01 W a run) plus white
noise sigma (planning value 0.025 W a run on the board: E102's int8 train read 0.019 W a run on aifoundry1 card 1's rail,
E79's repeated int8 zeros on this card about 0.03 W between passes). An item's level is its own zero's plus truth fJ x
designed flips x the rate. Worlds: `booth_tree`, `booth_swap`, `plain` (truth = that netlist's nets_map predictions), `e79`
(booth_tree's lists with B's odd-even scaled to E79's +40 board-fJ, the card's amplitude at E79's base words), `both`
(B as booth_tree, A as booth_swap: a multiplier none of the four is). Checks: each world's R1-R4 verdicts and their rates, the
separators' median half-widths, the train gate setting a block with a 0.4 W zero glitch aside, and R1 NOT SCORED with two B
blocks.
"""
import argparse
import csv
import io
import json
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e130_common as e130  # noqa: E402
import score_e130 as sc  # noqa: E402

REG = json.load(open(os.path.join(HERE, "predictions-e130.json")))
TILES = {"int8." + t["tile"]: t for t in json.load(open(os.path.join(HERE, "e130-items.json")))["tiles"]}
RATE = REG["source"]["rate_ops_per_s"]
ZLEVEL = {"hb1": 31.80, "hb2": 31.83, "hb1d": 32.40, "ha1": 32.90, "ha2": 33.05, "ha1d": 33.60}


def truth(world):
    if world in ("booth_tree", "booth_swap", "plain", "booth"):
        return {t: REG["netlists"][world]["items"][t]["fJ_map"] for t in REG["item_order"]}
    bt = {t: REG["netlists"]["booth_tree"]["items"][t]["fJ_map"] for t in REG["item_order"]}
    if world == "e79":
        odd = [bt[f"b1_{j}"] for j in (1, 3, 5)]
        even = [bt[f"b1_{j}"] for j in (0, 2, 4)]
        m_odd, m_even = sum(odd) / 3, sum(even) / 3
        s = 40.0 / (m_odd - m_even)
        for j in (1, 3, 5):
            bt[f"b1_{j}"] = m_even + (bt[f"b1_{j}"] - m_even) * s
        return bt
    if world == "both":
        sw = {t: REG["netlists"]["booth_swap"]["items"][t]["fJ_map"] for t in REG["item_order"]}
        return {t: (bt[t] if t.startswith("b") else sw[t]) for t in REG["item_order"]}
    raise SystemExit(world)


def session(world, rng, sigma, seq=None, glitch=None):
    tr = truth(world)
    items = e130.load_items()
    rows = []
    t = 1_793_600_000_000.0
    for p in (seq or REG["plan"]["sequence"]):
        order = e130.pass_order(items, "aifoundry3", p)
        n = len(order)
        walk = 0.0
        for k, r in enumerate(order):
            tile = TILES[r["item"]]
            z = tile["zero"] or tile["tile"]
            lvl = ZLEVEL[z]
            if tile["zero"] is not None:
                lvl += tr[tile["tile"]] * 1e-15 * tile["designed_flips_per_op"] * RATE
            walk += rng.gauss(0, 0.01)
            drift = 0.3 * (1 - (1 - k / max(n - 1, 1)) ** 2) + walk
            v = lvl + drift + rng.gauss(0, sigma)
            if glitch and glitch[0] == p and glitch[1] == k:
                v += glitch[2]
            rate = RATE * (1 + rng.gauss(0, 1e-4))
            rows.append({"pass": p, "item": r["item"], "segment": r["segment"], "t0_ms": t, "p_raw": v, "p80": v,
                         "rail_raw": 0.81 * v, "rate": rate, "fail": 0, "pos": r["pos"]})
            t += 4800.0
        t += 25_000.0
    return rows


def score_rows(rows):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "runs.csv")
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        book = sc.Book(sc.load_runs(p), TILES, "p_raw", True, REG["plan"]["train_gate_w"], {"passes_set_aside": [], "passes_config_flags": []})
        return sc.score(book, REG), book


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=40)
    ap.add_argument("--sigma", type=float, default=0.025)
    a = ap.parse_args()
    out = io.StringIO()
    ok = []

    def check(name, cond):
        ok.append(bool(cond))
        print(f"  [{'pass' if cond else 'FAIL'}] {name}", file=out)
    print(f"E130 self-test: synthetic runs on the registered orders and sequence, sigma {a.sigma} W a run, "
          f"{a.sessions} sessions a world (nothing here is a measurement)", file=out)
    th = REG["thresholds"]
    print(f"thresholds: T_B {th['T_B']['value']:.2f}, T_A {th['T_A']['value']:.2f}, T_S {th['T_S']['value']:.2f} fJ", file=out)
    expect = {"booth_tree": "BOOTH ON B", "booth_swap": "BOOTH ON A", "plain": "NO BOOTH", "e79": "BOOTH ON B", "both": "NONE OF THE FOUR"}
    for world in ("booth_tree", "booth_swap", "plain", "e79", "both"):
        rng = random.Random(f"E130 selftest {world}")
        tally = {}
        hw = {k: [] for k in REG["separators"]}
        nets = {}
        for _ in range(a.sessions):
            res, _book = score_rows(session(world, rng, a.sigma))
            v = res["verdicts"]
            key = (v["E130-R1"], v["E130-R2"], v["E130-R3"], v["E130-R4"])
            tally[key] = tally.get(key, 0) + 1
            for k in hw:
                s = res["statistics"][k]
                if s.get("ci95") is not None:
                    hw[k].append(s["ci95"])
            for n, e in res["netlists"].items():
                nets.setdefault(n, {}).setdefault(e["verdict"], 0)
                nets[n][e["verdict"]] += 1
        print(f"world {world}:", file=out)
        for key, c in sorted(tally.items(), key=lambda kv: -kv[1]):
            print(f"    {c:3d}/{a.sessions}  R1 {key[0]}, R2 {key[1]}, R3 {key[2]} -> R4 {key[3]}", file=out)
        med = {k: sorted(v)[len(v) // 2] if v else None for k, v in hw.items()}
        print("    median 95% half-widths (fJ): " + ", ".join(f"{k} {m:.1f}" for k, m in med.items() if m is not None), file=out)
        print("    per netlist: " + "; ".join(f"{n} {d}" for n, d in nets.items()), file=out)
        right = sum(c for key, c in tally.items() if key[3] == expect[world])
        if world == "e79":       # a power reading, not a check: the card's amplitude at E79's base words sits 9 fJ above T_B
            print(f"    power (reported, not checked): R4 reads {expect[world]} in {right}/{a.sessions} sessions", file=out)
        else:
            check(f"{world}: R4 reads {expect[world]} in at least 80% of sessions ({right}/{a.sessions})", right >= 0.8 * a.sessions)
        wrong = sum(c for key, c in tally.items() if key[3] not in (expect[world],) and not key[3].startswith("INCONCLUSIVE")
                    and not key[3].startswith(expect[world]))
        check(f"{world}: R4 names a wrong group in at most 5% of sessions ({wrong}/{a.sessions})", wrong <= 0.05 * a.sessions)
    rng = random.Random("E130 selftest gates")
    rows = session("booth_tree", rng, a.sigma)
    order = e130.pass_order(e130.load_items(), "aifoundry3", 13011)
    k = next(i for i, r in enumerate(order) if r["item"] == "int8.hb1" and r["segment"] == 0 and i > 8)
    res, book = score_rows(session("booth_tree", random.Random("g"), a.sigma, glitch=(13011, k, 0.4)))
    check(f"a +0.4 W glitch on an interior hb1 read sets block 13011 aside ({book.set_aside})",
          any(x["pass"] == 13011 for x in book.set_aside) and 13011 not in book.blocks["B"])
    res, book = score_rows(session("booth_tree", random.Random("h"), a.sigma, seq=[13010, 13020, 13011, 13021, 13022]))
    check(f"two B blocks: R1 NOT SCORED, R4 NOT SCORED (R1 {res['verdicts']['E130-R1']}, R4 {res['verdicts']['E130-R4']})",
          res["verdicts"]["E130-R1"] == "NOT SCORED" and res["verdicts"]["E130-R4"] == "NOT SCORED")
    bad = []
    for p in list(e130.B_PASSES) + list(e130.A_PASSES):
        bad += e130.check_order(e130.load_items(), "aifoundry3", p)
    check(f"every block order (13010-13029): each item has its own zero on both sides; registered counts ({bad or 'no problem'})",
          not bad)
    print(f"self-test: {sum(ok)} of {len(ok)} checks pass", file=out)
    sys.stdout.write(out.getvalue())
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
