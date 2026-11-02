#!/usr/bin/env python3
"""E128: what the README quotes beyond scored.json. Standard library only; run it in the data directory after collection. POST HOC: no rule of E128's
depends on it, and nothing here decides a verdict.

    python3 posthoc_e128.py > posthoc_e128.txt

A: every registered quantity on the board and on the minion rail (Drail, which the board meter's dips do not touch), per pass.
B: the arms, quantity by quantity (the headline ones).
C: the lane bits behind each contrast (the desk counts) and the board watts per 1,000 differing lane C-read + result bits, post hoc.
D: beside E108 (card 1) and E122 (aifoundry3): this session's card-1 watts against E108's, the ratio of the two sessions over every tile at 4 W or more.
E: the alternation counts: equal in each matched triple (desk), and what the unmatched contrasts carry.
F: every tile's D, its rail, and its M4 miss.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
P = json.load(open(os.path.join(HERE, "e128.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
REG = json.load(open(os.path.join(ROOT, "tools/claims-v3/e128/predictions-e128.json")))
SPEC = json.load(open(os.path.join(ROOT, "tools/claims-v3/e128/e128/e128.json")))
ARMS = {a: json.load(open(os.path.join(HERE, f"e128-{a}.json"))) for a in ("dipskept", "gatesoff", "auto", "leak0.1994", "leak0.3803", "leak0.545", "leak0")}
E108 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e108-sign-located/e108.json")))
Q = REG["quantities"]
RATE = P["items"]["fp32.randn"]["rate"]["mean"]


def mci(v):
    v = list(v)
    if len(v) < 2:
        return (v[0] if v else float("nan")), float("nan"), len(v)
    return sum(v) / len(v), T975.get(len(v) - 1, 2.0) * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def per_pass(res, name, key="D"):
    q = Q[name]
    if q["form"] == "contrast":
        out = {}
        for p, it in sorted(res["per_pass"].items()):
            if all(n in it and it[n].get(key) is not None for n in q["plus"] + q["minus"]):
                out[p] = sum(it[n][key] for n in q["plus"]) - sum(it[n][key] for n in q["minus"])
        return out
    a, b = per_pass(res, q["a"], key), per_pass(res, q["b"], key)
    if q["form"] == "ratio":
        return {p: a[p] / b[p] for p in a if p in b and b[p] != 0}
    return {p: a[p] - q.get("k", 1.0) * b[p] for p in a if p in b}


def f(m, c, n, d=3):
    return f"{m:.{d}f} ± {c:.{d}f} (n {n})"


print("E128 posthoc_e128 (labelled post hoc; no rule depends on it)")
print(f"passes kept {P['passes']}, set aside {P.get('passes_set_aside')}, leak {P['leak']}, rate {RATE:.4g} op/s")
print("\nA. every registered quantity, board and rail, per pass")
for name, q in Q.items():
    b, r = per_pass(P, name), per_pass(P, name, "Drail")
    mb, mr = mci(b.values()), mci(r.values())
    pb = ", ".join(f"{v:.3f}" for v in b.values())
    print(f"  {name:22s} board {f(*mb)}  rail {f(*mr)}  M4 {q['M']:.3f}  per pass [{pb}]")
print("\nB. the arms (board), headline quantities")
for name in ("fp32.share_het_m", "fp32.share_walk_m", "fp32.Bm_walk", "fp32.design_m", "fp32.share_het_z", "fp16.share_het_z", "fp16.share_het_m", "fp16.share_walk_m",
             "fp16.Bm_walk", "formats_m", "alt_walk_ratio", "fp32.alt_walk", "fp16.alt_walk"):
    row = [f"primary {f(*mci(per_pass(P, name).values()))}"]
    for a, res in ARMS.items():
        row.append(f"{a} {f(*mci(per_pass(res, name).values()))}")
    print(f"  {name:20s} " + " | ".join(row))
print("\nC. lane bits behind each contrast (desk counts, per op per minion) and board watts per 1,000 differing lane C-read + result bits, post hoc")
for name in ("fp32.Bm_het", "fp32.Bm_walk", "fp32.Bm_rest", "fp32.Bz_het", "fp32.Bz_walk", "fp32.Bz_rest", "fp32.held_alt", "fp32.walk_alt",
             "fp16.Bm_het", "fp16.Bm_walk", "fp16.Bm_rest", "fp16.Bz_het", "fp16.Bz_walk", "fp16.Bz_rest", "fp16.held_alt", "fp16.walk_alt"):
    q = Q[name]
    cnt = lambda n: SPEC["tiles"][n]["counts_real"]
    d = {k: sum(cnt(n)[k] for n in q["plus"]) - sum(cnt(n)[k] for n in q["minus"]) for k in ("alt1", "alt2", "cbus", "rbus", "store")}
    m, c, n = mci(per_pass(P, name).values())
    bits = d["cbus"] + d["rbus"]
    fj = (m / (bits * RATE) * 1e15) if bits else float("nan")
    print(f"  {name:16s} {f(m, c, n)} W | alternations {d['alt1']:+.0f} {d['alt2']:+.0f} | lane C-read {d['cbus']:+.0f} result {d['rbus']:+.0f} store {d['store']:+.0f} bits | "
          f"{fj:.1f} fJ per differing lane bit")
print("\nD. this session on card 1 against E108's, every tile both ran at 4 W or more: D(E128) / D(E108)")
rat = []
for n, it in P["items"].items():
    o = E108["items"].get(n)
    if not o or not it.get("D") or not o.get("D") or it["D"].get("mean") is None or o["D"].get("mean") is None:
        continue
    if o["D"]["mean"] >= 4.0:
        rat.append((it["D"]["mean"] / o["D"]["mean"], n))
rat.sort()
if rat:
    print(f"  {len(rat)} cells, median {statistics.median(r for r, _ in rat):.4f}, range {rat[0][0]:.4f} ({rat[0][1]}) .. {rat[-1][0]:.4f} ({rat[-1][1]})")
print("\nE. alternations an op (desk, e128.json counts_real alt1 + alt2)")
for t, trio in SPEC["matched"].items():
    print(f"  {t} matched: " + ", ".join(f"{n} {SPEC['tiles'][n]['counts_real']['alt1']:.0f}+{SPEC['tiles'][n]['counts_real']['alt2']:.0f}" for n in trio))
for n in ("fp32.b_B_z", "fp32.b_B_w", "fp16.b_B_z", "fp16.b_B_w"):
    c = SPEC["tiles"][n]["counts_real"]
    print(f"  {n}: {c['alt1']:.0f}+{c['alt2']:.0f}")
print("\nF. every tile: D, rail, M4, D - M4")
tab = SC["primary"]["table"]
for n in sorted(P["items"]):
    if n not in REG["tiles"]:
        continue
    it = P["items"][n]
    d, r = it.get("D", {}), it.get("Drail", {})
    m = REG["tiles"][n]["pred"]["M"]
    print(f"  {n:16s} D {d.get('mean', float('nan')):7.3f} ± {d.get('ci95') or float('nan'):.3f}  rail {r.get('mean', float('nan')) if isinstance(r, dict) else float('nan'):7.3f}  M4 {m:7.3f}  D-M4 {d.get('mean', float('nan')) - m:+.3f}")
