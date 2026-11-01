#!/usr/bin/env python3
"""E108: every number the README's corrections after verification cite (Sun 1 Nov 2026). Standard library only, from committed files;
run it in this directory. POST HOC: no rule of E108's depends on it, and nothing here changes a frozen file, a data file or a verdict.

    python3 corrections-check.py > corrections-check.txt

C1: R7 with M4's bus term: what the term is (the bench's lane_operand_bus stage), and R7 with it taken off both sides or as c_mx_f's excess only.
C2: R12 and the tile contrast b_B_w - b_B_z with the alternation counts priced: one rate; R9's held and walking prices; E104's ranges; z_s's cap.
C3: E106's fp16 held share on cancelling products, which item 5's line keeps.
C4: the arms that move R3, R4, R5, R7 and R9: which passes they keep, and how far their means move.
C5: watts per lane C-read and result bit, all six contrasts.
C6: M4 on the 8 new tiles against the 17 reused ones.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}


def load(*p):
    return json.load(open(os.path.join(*p)))


P = load(HERE, "e108.json")
REG = load(ROOT, "tools/claims-v3/signloc/predictions-e108.json")
SPEC = load(ROOT, "tools/claims-v3/signloc/e108/e108.json")
SC = load(HERE, "scored.json")
ARMS = {a: load(HERE, f"e108-{a}.json") for a in ("dipskept", "leak0")}
Q = REG["quantities"]
RATE = P["items"]["fp32.randn"]["rate"]["mean"]
CNT = {n: SPEC["tiles"][n]["counts_real"] for n in SPEC["tiles"]}


def mci(v):
    v = list(v)
    return sum(v) / len(v), T975[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def f(m, c, n, d=3):
    return f"{m:.{d}f} ± {c:.{d}f} (n {n})"


def per_pass(res, name, key="D"):
    q = Q[name]
    if q["form"] == "contrast":
        return {p: sum(it[n][key] for n in q["plus"]) - sum(it[n][key] for n in q["minus"]) for p, it in sorted(res["per_pass"].items())
                if all(n in it and it[n].get(key) is not None for n in q["plus"] + q["minus"])}
    a, b = per_pass(res, q["a"], key), per_pass(res, q["b"], key)
    if q["form"] == "ratio":
        return {p: a[p] / b[p] for p in a if p in b and b[p] != 0}
    return {p: a[p] - q.get("k", 1.0) * b[p] for p in a if p in b}


def D(p, t):
    return P["per_pass"][p][t]["D"]


PS = sorted(P["per_pass"])
print("E108 corrections-check (labelled post hoc; no rule depends on it)")
print(f"passes {P['passes']}, leak {P['leak']['mode']}, rate {RATE:.4g} op/s (fp32.randn)")

# ---------------------------------------------------------------- C1
print("\nC1. R7 and M4's bus term")
STAGE_FILES = {"fp32.s_abs": "docs/reports/data/2026-11-01-q132-rtl-bench/counts-e92.json",
               "fp32.s_walk": "docs/reports/data/2026-11-01-q132-rtl-bench/counts-e88.json",
               "fp32.zeros": "docs/reports/data/2026-11-01-q132-rtl-bench/counts-e88.json",
               "fp32.c_mx_f": "docs/reports/data/2026-11-01-e108-sign-located/desk/counts-e108.json",
               "fp32.b_B_w": "docs/reports/data/2026-11-01-e108-sign-located/desk/counts-e108.json",
               "fp32.b_B_z": "docs/reports/data/2026-11-01-e108-sign-located/desk/counts-e108b.json",
               "fp32.z_s": "docs/reports/data/2026-11-01-e104-c-readback/desk/counts-e104b.json"}
stage = {t: load(ROOT, p)["rows"][t]["mean"]["vpu"]["by_stage"]["lane_operand_bus"] for t, p in STAGE_FILES.items()}
bus = {t: REG["tiles"][t]["pred"]["terms_w"][1] for t in STAGE_FILES if t != "fp32.zeros"}
kb = REG["model"]["coef_fJ"]["k_bus"]
print(f"  M4's bus term is k_bus ({kb:.3f} fJ) x the bench's lane_operand_bus stage over zeros (predict_m4.py x_float; settle_count.cpp stage_of:"
      " .lane.bypass, .lane.txfma_trans_top, .lane_tima.* and other .lane.* nets, not .lane.rf)")
print("  tile          M4 bus W   lane_operand_bus toggles an op   over zeros   W per 1,000 over zeros   designed bus bits an op")
for t in ("fp32.s_abs", "fp32.s_walk", "fp32.c_mx_f", "fp32.z_s", "fp32.b_B_z", "fp32.b_B_w"):
    over = stage[t] - stage["fp32.zeros"]
    print(f"  {t:13s} {bus[t]:8.3f}   {stage[t]:31,.0f}   {over:10,.0f}   {1000 * bus[t] / over:22.5f}   {SPEC['tiles'][t]['stats']['bus_bits_per_op']:23,d}")
wpt = bus["fp32.c_mx_f"] / (stage["fp32.c_mx_f"] - stage["fp32.zeros"])
bb = {t: SPEC["tiles"][t]["stats"]["bus_bits_per_op"] for t in ("fp32.s_abs", "fp32.s_walk", "fp32.c_mx_f")}
print(f"  over s_abs: c_mx_f's bus term {bus['fp32.c_mx_f'] - bus['fp32.s_abs']:.3f} W on {stage['fp32.c_mx_f'] - stage['fp32.s_abs']:,.0f} stage toggles, "
      f"s_walk's {bus['fp32.s_walk'] - bus['fp32.s_abs']:.3f} W on {stage['fp32.s_walk'] - stage['fp32.s_abs']:,.0f}; designed bus bits "
      f"c_mx_f {bb['fp32.c_mx_f'] - bb['fp32.s_abs']:+,d}, s_walk {bb['fp32.s_walk'] - bb['fp32.s_abs']:+,d}")
print(f"  c_mx_f's own extra designed bus bits over s_abs ({bb['fp32.c_mx_f'] - bb['fp32.s_abs']:,d} an op) at the same price per toggle: "
      f"{(bb['fp32.c_mx_f'] - bb['fp32.s_abs']) * wpt:.4f} W")
num = [D(p, "fp32.c_mx_f") - D(p, "fp32.s_abs") for p in PS]
den = [D(p, "fp32.s_walk") - D(p, "fp32.s_abs") for p in PS]
bn = bus["fp32.c_mx_f"] - bus["fp32.s_abs"]
bd = bus["fp32.s_walk"] - bus["fp32.s_abs"]
print(f"  R7 as scored, (c_mx_f - s_abs) / (s_walk - s_abs): {f(*mci(a / b for a, b in zip(num, den)))}")
print(f"  withdrawn: the term off the numerator only ({bn:.3f} W): {f(*mci((a - bn) / b for a, b in zip(num, den)))}")
print(f"  the term off both sides ({bn:.3f} / {bd:.3f} W): {f(*mci((a - bn) / (b - bd) for a, b in zip(num, den)))}")
print(f"  only c_mx_f's excess over s_walk off ({bn - bd:.3f} W): {f(*mci((a - (bn - bd)) / b for a, b in zip(num, den)))}")

# ---------------------------------------------------------------- C2
print("\nC2. R12, the tile contrast b_B_w - b_B_z, and the alternation counts")
alt = {t: CNT[t]["alt1"] for t in ("fp32.z_s", "fp32.b_B_z", "fp32.b_B_w", "fp32.h_sub", "fp32.h_add", "fp32.m_h_sub", "fp32.w_h_add")}
print("  eff_sub alternations an op: " + ", ".join(f"{t.split('.')[1]} {v:,.0f}" for t, v in alt.items()))
n12 = [D(p, "fp32.b_B_z") - D(p, "fp32.z_s") for p in PS]
d12 = [D(p, "fp32.b_B_w") - D(p, "fp32.z_s") for p in PS]
print(f"  R12 as scored: {f(*mci(a / b for a, b in zip(n12, d12)))}; b_B_w - b_B_z {f(*mci(b - a for a, b in zip(n12, d12)))} W (M4 "
      f"{REG['quantities']['fp32.Bz_walk']['M']:.3f})")
hz = [D(p, "fp32.z_s") - D(p, "fp32.c_abs") for p in PS]
m, c, _ = mci(hz)
cap = m / (alt["fp32.z_s"] * RATE) * 1e15
print(f"  z_s's cap: z_s - c_abs = {f(*mci(hz))} W over {alt['fp32.z_s']:,.0f} alternations an op: at most {cap:.0f} fJ an alternation on zero products "
      f"({(m + c) / (alt['fp32.z_s'] * RATE) * 1e15:.0f} at the interval's top), even if B's sign bits cost nothing")
ah = [D(p, "fp32.h_sub") - D(p, "fp32.h_add") for p in PS]
aw = [D(p, "fp32.m_h_sub") - D(p, "fp32.w_h_add") for p in PS]
ph9 = mci(ah)[0] / ((alt["fp32.h_sub"] - alt["fp32.h_add"]) * RATE) * 1e15
pw9 = mci(aw)[0] / ((alt["fp32.m_h_sub"] - alt["fp32.w_h_add"]) * RATE) * 1e15
print(f"  R9's prices: held (h_sub - h_add) {ph9:.0f} fJ, walking (m_h_sub - w_h_add) {pw9:.0f} fJ an alternation; E104: about 900-1,050 fJ for absorbed products"
      " on a sum that does not part, 488-756 fJ on moving sums at magnitude 1, 257 fJ for E92's random magnitudes")


def priced(pz, pzb, pw):
    """each tile's alternations removed at its own price (fJ): z_s at pz, b_B_z at pzb, b_B_w at pw -> share, walk (per pass)"""
    k = 1e-15 * RATE
    h = [a - alt["fp32.b_B_z"] * pzb * k + alt["fp32.z_s"] * pz * k for a in n12]
    w = [b - alt["fp32.b_B_w"] * pw * k + alt["fp32.z_s"] * pz * k for b in d12]
    return mci(x / y for x, y in zip(h, w)), mci(y - x for x, y in zip(h, w))


k1 = 1e-15 * RATE
for fj in (913.0, 1056.0):
    one = [(a + (alt["fp32.z_s"] - alt["fp32.b_B_z"]) * fj * k1) / b for a, b in zip(n12, d12)]
    print(f"  withdrawn: b_B_z's 468 missing alternations priced at {fj:.0f} fJ in the numerator only: {f(*mci(one))}")
print("  one rate for every alternation (fJ):")
for p in (0.0, 257.0, 465.0, cap, 913.0, 1056.0):
    (s, w) = priced(p, p, p)
    print(f"    {p:6.0f}  R12 {f(*s)}  walk net of alternations {f(*w)} W")
print("  a held price on z_s and a walking price on b_B_w, with b_B_z at either (fJ):")
rows = []
for ph in (cap, round(ph9), 913.0, 1056.0):
    for pw in (257.0, round(pw9), 488.0, 756.0):
        for lab, pzb in (("held", ph), ("walking", pw)):
            (s, w) = priced(ph, pzb, pw)
            rows.append((ph, pw, lab, s, w))
            print(f"    z_s {ph:5.0f}  b_B_w {pw:4.0f}  b_B_z at the {lab:7s} price  R12 {f(*s)}  walk {f(*w)} W")
allp = [(s[0], s[1], w[0]) for _, _, _, s, w in rows] + [(priced(p, p, p)[0][0], priced(p, p, p)[0][1], priced(p, p, p)[1][0]) for p in (0.0, cap, 913.0, 1056.0)]
capped = [(s[0], s[1], w[0]) for ph, _, _, s, w in rows if ph <= cap + 1e-9] + [(priced(p, p, p)[0][0], priced(p, p, p)[0][1], priced(p, p, p)[1][0]) for p in (0.0, cap)]
for lab, xs in (("every pricing above", allp), ("pricings within z_s's cap", capped)):
    lo = min(xs, key=lambda r: r[0])
    print(f"  {lab}: R12 {min(r[0] for r in xs):.3f} to {max(r[0] for r in xs):.3f} (lowest {lo[0]:.3f} ± {lo[1]:.3f}, so its interval's foot "
          f"{lo[0] - lo[1]:.3f} > 0.65: MOST); walk {min(r[2] for r in xs):+.3f} to {max(r[2] for r in xs):+.3f} W")

# ---------------------------------------------------------------- C3
print("\nC3. E106's fp16 held share on cancelling products (x_s), the low end item 5's line keeps")
r5 = load(ROOT, "docs/reports/data/2026-11-01-e106-held-signs/scored.json")["primary"]["rules"]["E106-R5"]
print(f"  E106 scored.json primary.rules.E106-R5: share {r5['share']:.3f} ± {r5['ci95']:.3f} (n {r5['n']}), held {r5['held_w']:.3f} ± {r5['held_ci95_w']:.3f} W, "
      f"verdict {r5['verdict']}; E108 did not rerun x_s")

# ---------------------------------------------------------------- C4
print("\nC4. the arms that move R3, R4, R5, R7 and R9")
for a, res in ARMS.items():
    print(f"  {a}: keeps passes {res['passes']}, sets aside {[(x['pass'], '; '.join(x['why'])) for x in res['passes_set_aside']]}; "
          f"t(0.975, {len(res['passes']) - 1}) = {T975[len(res['passes']) - 1]}")
print(f"  primary: keeps {P['passes']}; t(0.975, {len(P['passes']) - 1}) = {T975[len(P['passes']) - 1]}")
verd = {r: SC["primary"]["rules"][r] for r in SC["primary"]["rules"]}
for rule, qn in (("E108-R3", "formats_z"), ("E108-R4", "design_fp32"), ("E108-R5", "A_vs_B_priced"), ("E108-R7", "fp32.share_het"), ("E108-R9", "fp32.alt_ratio")):
    m0, c0, n0 = mci(per_pass(P, qn).values())
    out = [f"primary {m0:.3f} ± {c0:.3f}"]
    for a, res in ARMS.items():
        m1, c1, n1 = mci(per_pass(res, qn).values())
        out.append(f"{a} {m1:.3f} ± {c1:.3f} (n {n1}; mean moves {m1 - m0:+.3f}; interval x{c1 / c0:.1f})")
    print(f"  {rule} {qn:15s} " + "; ".join(out))
for a in ("dips_kept", "leak0"):
    try:
        print(f"  scored.json arm {a}: " + ", ".join(f"{r} {SC['arms'][a]['rules'][r]['verdict']}" for r in ("E108-R3", "E108-R4", "E108-R5", "E108-R7", "E108-R9", "E108-R12")))
    except (KeyError, TypeError):
        pass

# ---------------------------------------------------------------- C5
print("\nC5. watts per lane C-read and result bit (board watts / (bits x op rate)), all six contrasts")
bits = {n: CNT[n]["cbus"] + CNT[n]["rbus"] for n in CNT}
fj = []
for base, tiles in (("fp32.s_abs", ("fp32.c_sg_f", "fp32.c_ex_f", "fp32.c_mx_f", "fp32.s_walk")), ("fp32.z_s", ("fp32.b_B_z", "fp32.b_B_w"))):
    for t in tiles:
        m, c, n = mci(D(p, t) - D(p, base) for p in PS)
        db = bits[t] - bits[base]
        fj.append(m / (db * RATE) * 1e15)
        print(f"  {t:13s} - {base:10s} {f(m, c, n)} W on {db:8,.0f} bits an op: {fj[-1]:5.1f} fJ a bit")
print(f"  range {min(fj):.1f}-{max(fj):.1f} fJ; the two smallest differences (c_sg_f, c_ex_f) give {fj[0]:.1f} and {fj[1]:.1f}")

# ---------------------------------------------------------------- C6
print("\nC6. M4 on the new tiles and the reused ones (D - M4, W)")
groups = {"new": [], "reused": []}
for t, s in sorted(SPEC["tiles"].items()):
    if t not in REG["tiles"] or not P["items"].get(t, {}).get("D"):
        continue
    d = P["items"][t]["D"]["mean"] - REG["tiles"][t]["pred"]["M"]
    inside = REG["tiles"][t]["pred"]["lo95"] <= P["items"][t]["D"]["mean"] <= REG["tiles"][t]["pred"]["hi95"]
    groups[s["how"]].append((t, d, inside))
for g in ("new", "reused"):
    xs = groups[g]
    print(f"  {g:6s} {len(xs):2d} tiles: rms {math.sqrt(sum(d * d for _, d, _ in xs) / len(xs)):.4f} W, mean {sum(d for _, d, _ in xs) / len(xs):+.4f} W, "
          f"M4 high on {sum(d < 0 for _, d, _ in xs)}, inside the frozen 95% interval {sum(i for _, _, i in xs)}")
    if g == "new":
        print("         " + ", ".join(f"{t.split('.')[1]} {d:+.3f}" for t, d, _ in xs))
xs = groups["new"] + groups["reused"]
print(f"  all    {len(xs):2d} tiles: rms {math.sqrt(sum(d * d for _, d, _ in xs) / len(xs)):.4f} W, mean {sum(d for _, d, _ in xs) / len(xs):+.4f} W")
