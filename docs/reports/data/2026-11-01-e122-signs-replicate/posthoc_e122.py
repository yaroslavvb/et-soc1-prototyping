#!/usr/bin/env python3
"""E122: what the README quotes beyond scored.json. Standard library only; run it in this directory after collection.
POST HOC: no rule of E122's depends on it; it decides nothing.

    python3 posthoc_e122.py > posthoc_e122.txt

A: every registered quantity on the board and on the minion rail (Drail, which the board meter's dips do not touch), per
   pass, beside E108's on card 1 and the ratio of the two.
B: this session's card scale: D of the random anchors, the constant and every tile at 4 W or more over E108's D.
C: the arms, for the quantities behind R3, R4, R7, R12, R9 and R10.
D: watts per lane C-read and result bit that differ, for the location's contrasts, as E108's posthoc-check C did
   (counts: tools/claims-v3/signloc/e108/e108.json > tiles > <t> > counts_real > cbus + rbus).
E: every tile's D, rail, M4 here and its miss, and D over E108's D.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
P = json.load(open(os.path.join(HERE, "e122.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
REG108 = json.load(open(os.path.join(ROOT, "tools/claims-v3/signloc/predictions-e108.json")))
REG = json.load(open(os.path.join(ROOT, "tools/claims-v3/e122/predictions-e122.json")))
SPEC = json.load(open(os.path.join(ROOT, "tools/claims-v3/signloc/e108/e108.json")))
D108 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e108-sign-located")
P108 = json.load(open(os.path.join(D108, "e108.json")))
S108 = json.load(open(os.path.join(D108, "scored.json")))
ARMS = {}
for a in ("dipskept", "gatesoff", "auto", "leak0.2414", "leak0.3803", "leak0.545", "leak0"):
    p = os.path.join(HERE, f"e122-{a}.json")
    if os.path.exists(p):
        ARMS[a] = json.load(open(p))
Q = REG108["quantities"]
QM = REG["substitutions"]["quantities.M"]
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


print("E122 posthoc_e122 (labelled post hoc; no rule depends on it)")
print(f"passes kept {P['passes']}, set aside {P.get('passes_set_aside')}, leak {P['leak']}, rate {RATE:.4g} op/s")
print("\nA. every registered quantity, board and rail, per pass; E108 on card 1 (board); E122 / E108")
for name in Q:
    b, r = per_pass(P, name), per_pass(P, name, "Drail")
    mb, mr = mci(b.values()), mci(r.values())
    q108 = S108["primary"]["quantities"][name]
    ratio = mb[0] / q108["mean"] if q108["mean"] else float("nan")
    pb = ", ".join(f"{v:.3f}" for v in b.values())
    print(f"  {name:20s} board {f(*mb)}  rail {f(*mr)}  M4 {QM[name]['M']:.3f}  E108 {q108['mean']:.3f} ± {q108['ci95']:.3f}  "
          f"ratio {ratio:.3f}  per pass [{pb}]")

print("\nB. this session's card scale: D here over E108's D on card 1 (E82's per-type medians: "
      f"{REG['card_scale']['per_type']})")
rat = []
for n, it in sorted(P["items"].items()):
    d = it.get("D") if isinstance(it.get("D"), dict) else None
    i8 = P108["items"].get(n)
    d8 = i8.get("D") if i8 and isinstance(i8.get("D"), dict) else None
    if not d or not d8 or d.get("mean") is None or d8.get("mean") is None:
        continue
    if n in ("fp32.randn", "fp16.randn", "int8.full", "anchor_pi"):
        print(f"  {n:16s} {d['mean']:.3f} over {d8['mean']:.3f} = {d['mean'] / d8['mean']:.4f}")
    if d8["mean"] >= 4.0:
        rat.append((d["mean"] / d8["mean"], n))
rat.sort()
if rat:
    v = [x for x, _ in rat]
    print(f"  every cell at 4 W or more on card 1 ({len(v)}): median {statistics.median(v):.4f}, range {v[0]:.4f} "
          f"({rat[0][1]}) to {v[-1]:.4f} ({rat[-1][1]})")

print("\nC. the arms (board), for the quantities behind R3, R4, R7, R12, R9, R10")
for name in ("formats_z", "design_fp32", "fp32.share_het", "fp32.share_het_z", "fp32.alt_ratio", "alt_walk_ratio"):
    row = [f"primary {f(*mci(per_pass(P, name).values()))}"]
    for a, res in ARMS.items():
        row.append(f"{a} {f(*mci(per_pass(res, name).values()))} kept {res['passes']}")
    print(f"  {name}: " + "; ".join(row))

print("\nD. watts per differing lane C-read + result bit (fJ), post hoc, as E108's posthoc-check C")
bits = {t: v["counts_real"]["cbus"] + v["counts_real"]["rbus"] for t, v in SPEC["tiles"].items() if "counts_real" in v}
for name, plus, minus in (("fp32.Bz_het", "fp32.b_B_z", "fp32.z_s"), ("fp32.Bz_rest", "fp32.b_B_w", "fp32.z_s"),
                          ("fp32.het_mx", "fp32.c_mx_f", "fp32.s_abs"), ("fp32.rest", "fp32.s_walk", "fp32.s_abs"),
                          ("fp32.het_sg", "fp32.c_sg_f", "fp32.s_abs"), ("fp32.het_ex", "fp32.c_ex_f", "fp32.s_abs")):
    m, c, n = mci(per_pass(P, name).values())
    db = bits[plus] - bits[minus]
    fj = m / (db * RATE) * 1e15
    q108 = S108["primary"]["quantities"][name]["mean"]
    print(f"  {name:14s} {m:.3f} ± {c:.3f} W over {db:,.0f} bits an op = {fj:.1f} fJ a bit (E108 {q108 / (db * RATE) * 1e15:.1f} at its own W and this rate)")

print("\nE. every tile: D, rail, M4 here [95%], D - M4, D over E108's D")
for n, it in sorted(P["items"].items()):
    if n not in REG108["tiles"]:
        continue
    d = it["D"]
    m4 = REG["substitutions"]["tiles.pred"][n]
    d8 = P108["items"][n]["D"]["mean"]
    rail = it.get("Drail", {}).get("mean") if isinstance(it.get("Drail"), dict) else None
    rs = "—" if rail is None else f"{rail:.3f}"
    print(f"  {n:16s} D {d['mean']:.3f} ± {d['ci95'] or 0:.3f}  rail {rs}  M4 {m4['M']:.3f} [{m4['lo95']:.3f}, {m4['hi95']:.3f}]  "
          f"D - M4 {d['mean'] - m4['M']:+.3f}  D / E108 {d['mean'] / d8:.4f}")
