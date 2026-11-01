#!/usr/bin/env python3
"""E108: what the README quotes beyond scored.json. Standard library only; run it in this directory after collection. POST HOC: no rule of E108's depends on it.

    python3 posthoc-check.py > posthoc-check.txt

A: every registered quantity on the board and on the minion rail (Drail, which the board meter's dips do not touch), per pass.
B: the arms, quantity by quantity. C: the rest located: the split, and watts per 1,000 bits the lane's C and result words toggle, along the ladder.
D: beside earlier sessions on this card (E88, E104, E106) and aifoundry3 (E92). E: the alternation counts and a priced adjustment of R12. F: every tile's D, rail, S and M4 miss.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
P = json.load(open(os.path.join(HERE, "e108.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
REG = json.load(open(os.path.join(ROOT, "tools/claims-v3/signloc/predictions-e108.json")))
SPEC = json.load(open(os.path.join(ROOT, "tools/claims-v3/signloc/e108/e108.json")))
ARMS = {a: json.load(open(os.path.join(HERE, f"e108-{a}.json"))) for a in ("dipskept", "gatesoff", "auto", "leak0.1994", "leak0.3803", "leak0.545", "leak0")}
RATE = P["items"]["fp32.randn"]["rate"]["mean"]
Q = REG["quantities"]


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


print("E108 posthoc-check (labelled post hoc; no rule depends on it)")
print(f"passes kept {P['passes']}, set aside {P.get('passes_set_aside')}, leak {P['leak']}, rate {RATE:.4g} op/s")
print("\nA. every registered quantity, board and rail, per pass")
for name, q in Q.items():
    b, r = per_pass(P, name), per_pass(P, name, "Drail")
    mb, mr = mci(b.values()), mci(r.values())
    pb = ", ".join(f"{v:.3f}" for v in b.values())
    print(f"  {name:20s} board {f(*mb)}  rail {f(*mr)}  M4 {q['M']:.3f}  per pass [{pb}]")
print("\nB. the arms (board), quantity by quantity")
for name in Q:
    row = []
    for a, res in ARMS.items():
        m, c, n = mci(per_pass(res, name).values())
        row.append(f"{a} {m:.3f}±{c:.3f}")
    print(f"  {name:20s} " + "; ".join(row))
print("\nC. the rest located")
cnt = {n: SPEC["tiles"][n]["counts_real"] for n in SPEC["tiles"]}
bits = {n: cnt[n]["cbus"] + cnt[n]["rbus"] for n in cnt}
for base, tiles in (("fp32.s_abs", ("fp32.c_sg_f", "fp32.c_ex_f", "fp32.c_mx_f", "fp32.s_walk")), ("fp32.z_s", ("fp32.b_B_z", "fp32.b_B_w"))):
    for t in tiles:
        v = {p: P["per_pass"][p][t]["D"] - P["per_pass"][p][base]["D"] for p in P["per_pass"] if t in P["per_pass"][p] and base in P["per_pass"][p]}
        m, c, n = mci(v.values())
        db = bits[t] - bits[base]
        print(f"  {t:14s} - {base:11s} {f(m, c, n)} W; lane C + result bits an op {db:,.0f}; {1000 * m / db if db else float('nan'):.4f} W per 1,000 bits an op; "
              f"{m / (db * RATE) * 1e15 if db else float('nan'):.1f} fJ per bit")
for name in ("fp32.share_het", "fp32.share_het_z"):
    m, c, n = mci(per_pass(P, name).values())
    mr, cr, nr = mci(per_pass(P, name, "Drail").values())
    print(f"  {name}: board {f(m, c, n)}; rail {f(mr, cr, nr)}")
for name in ("fp32.walk_given_het", "fp32.Bz_walk", "fp32.rest", "fp32.Bz_rest"):
    m, c, n = mci(per_pass(P, name).values())
    print(f"  {name}: {f(m, c, n)} W")
# M4's bus term over s_abs. Corrected after verification (Sun 1 Nov 2026, README C1): the term is the bench's lane_operand_bus stage, which in
# c_mx_f and s_walk is mostly the lane's nets carrying the differing C words, not c_mx_f's k = 0 bus bits; so it comes off both sides, or only
# c_mx_f's excess over s_walk does. The withdrawn numerator-only figure is in corrections-check.txt C1.
tb = REG["tiles"]
bus = tb["fp32.c_mx_f"]["pred"]["terms_w"][1] - tb["fp32.s_abs"]["pred"]["terms_w"][1]
busw = tb["fp32.s_walk"]["pred"]["terms_w"][1] - tb["fp32.s_abs"]["pred"]["terms_w"][1]
print(f"  M4's bus term over s_abs: c_mx_f {bus:.3f} W, s_walk {busw:.3f} W (the lane's operand-bus nets, mostly carrying the differing C words)")
pp = P["per_pass"]
v = {p: (pp[p]["fp32.c_mx_f"]["D"] - pp[p]["fp32.s_abs"]["D"] - bus) / (pp[p]["fp32.s_walk"]["D"] - pp[p]["fp32.s_abs"]["D"] - busw) for p in pp}
print(f"  share_het with the term off both sides: {f(*mci(v.values()))}")
v = {p: (pp[p]["fp32.c_mx_f"]["D"] - pp[p]["fp32.s_abs"]["D"] - (bus - busw)) / (pp[p]["fp32.s_walk"]["D"] - pp[p]["fp32.s_abs"]["D"]) for p in pp}
print(f"  share_het with only c_mx_f's excess over s_walk ({bus - busw:.3f} W) off: {f(*mci(v.values()))}")
print("\nD. beside earlier sessions")
E106 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e106-held-signs/scored.json")))["primary"]["contrasts"]
E104 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e104-c-readback/scored.json")))["primary"]["contrasts"]
E88 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e88-result-path/scored.json")))["primary"]["contrasts"]


def mc(c):
    c = c.get("D", c)
    return c.get("mean"), c.get("ci95")


for mine, theirs, src in (("fp32.step", E106["fp32.step"], "E106"), ("fp16.step", E106["fp16.step"], "E106"), ("fp32.held_abs", E106["fp32.held"], "E106"),
                          ("fp16.held_zss", E106["fp16.held_z"], "E106"), ("fp32.held_z", E104["fp32.z_s - c_abs"], "E104 (two kept passes)"),
                          ("fp16.held_z", E104["fp16.z_s - c_abs"], "E104 (two kept passes)"), ("fp32.alt_held", E104["fp32.h_premium"], "E104"),
                          ("fp32.alt_walk", E104["fp32.m_premium"], "E104"), ("fp16.alt_walk", E104["fp16.m_premium"], "E104"),
                          ("fp32.rest", E88["R32s"], "E88 R32s"), ("fp32.held_abs", E88["M32s"], "E88 M32s")):
    m, c, n = mci(per_pass(P, mine).values())
    tm, tc = mc(theirs)
    print(f"  {mine:16s} here {f(m, c, n)}  {src} {tm if tm is None else round(tm, 3)} ± {tc if tc is None else round(tc, 3)}")
print("\nE. alternations an op, and R12 priced at a per-alternation figure (post hoc)")
for n in ("fp32.z_s", "fp32.b_B_z", "fp32.b_B_w", "fp32.s_abs", "fp32.c_mx_f", "fp32.s_walk", "fp32.b_B_f"):
    print(f"  {n:14s} alt {cnt[n]['alt1']:6.0f}  store {cnt[n]['store']:7.0f}  C {cnt[n]['cbus']:7.0f}  result {cnt[n]['rbus']:7.0f}")
# Corrected after verification (Sun 1 Nov 2026, README C2): both sides' counts are priced, at one rate here; z_s's own held part caps that rate on
# zero products at about 781 fJ. Two-price forms (R9's held and walking prices, E104's ranges) and the withdrawn one-sided figures are in
# corrections-check.txt C2.
for fj in (0.0, 465.0, 781.0):
    adj, walk = {}, {}
    for p, it in P["per_pass"].items():
        k = fj * 1e-15 * it["fp32.b_B_z"]["rate"]
        het = it["fp32.b_B_z"]["D"] - it["fp32.z_s"]["D"] + (cnt["fp32.z_s"]["alt1"] - cnt["fp32.b_B_z"]["alt1"]) * k
        rest = it["fp32.b_B_w"]["D"] - it["fp32.z_s"]["D"] + (cnt["fp32.z_s"]["alt1"] - cnt["fp32.b_B_w"]["alt1"]) * k
        adj[p], walk[p] = het / rest, rest - het
    print(f"  share_het_z with every tile's alternations priced at one rate, {fj:.0f} fJ: {f(*mci(adj.values()))}; b_B_w - b_B_z net of them {f(*mci(walk.values()))} W")
print("\nF. every tile: D, rail, S, M4 miss")
for n in sorted(REG["tiles"]):
    it = P["items"].get(n)
    if not it or not it.get("D"):
        continue
    d, r = it["D"], it["Drail"]
    print(f"  {n:14s} D {d['mean']:7.3f} ± {d.get('ci95') or 0:5.3f}  rail {r['mean']:7.3f} ± {r.get('ci95') or 0:5.3f}  S {it['S']['mean']:7.3f}  M4 {REG['tiles'][n]['pred']['M']:6.2f}  D-M4 {d['mean'] - REG['tiles'][n]['pred']['M']:+.3f}")
