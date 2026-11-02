#!/usr/bin/env python3
"""E123 (Q134): the numbers behind the README's "Corrections after verification", printed from committed files. Written at
the desk on Sun 1 Nov 2026, after Q134's verifier read E123; post hoc and labelled so. Standard library only (with E94's
t975 and incomplete gamma, imported as score_e123 imports them); it reads scored.json and the frozen predictions-e123.json
and changes nothing. No registered verdict comes from here.

    python3 docs/reports/data/2026-11-01-e123-tile-spread-rest/corrections-check.py > docs/reports/data/2026-11-01-e123-tile-spread-rest/corrections-check.txt

C1  the class pooling: each rule's own SD of the adjusted draws against its class's, the offset on the rule's own SD (the
    scorer's formula with only s' swapped), and whether the adjusted draws' SDs are equal inside each class
C2  what the committed tiles' gate-share gaps predict at D(random) per unit, against the measured offsets
C3  fp16 50% zeros in the page's frame, and its committed tile against E78 in this session
C4  the bridge draws' spread on both cards, and what sets fp32 ReLU's tau on aifoundry3
C5  what the gate share leaves, per kind in class G and pooled
C6  the table cells: each kind's D, S, nJ per op and pJ per MAC with their 95% half-widths (the registered primary)
C7  E94's form (the secondary column of README result 1), rounded once
"""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "kinds"))
import score_e94 as s94  # noqa: E402  (standard library only; its main() does not run on import)

sc = json.load(open(os.path.join(HERE, "scored.json")))
reg = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e123", "predictions-e123.json")))
P = sc["primary"]
RN = reg["rules_of_number"]
RO = P["rules_of_number"]
CL = P["primary_by_class"]
NPASS = len(P["passes"])


def betainc(a, b, x):
    """The regularized incomplete beta function I_x(a, b) (continued fraction, modified Lentz)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x)
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - betainc(b, a, 1.0 - x)
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((a + m2 - 1.0) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1.0))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return math.exp(lbt) * h / a


def t_cdf(t, df):
    p = 0.5 * betainc(df / 2.0, 0.5, df / (df + t * t))
    return 1.0 - p if t >= 0 else p


def t975_exact(df):
    """t(0.975, df) at a fractional df, by bisection (the scorer's own t975 floors df, the conservative convention)."""
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < 0.975:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def chi2_sf(x, df):
    return 1.0 - s94.gammainc_p(df / 2.0, x / 2.0)


def f_sf(x, d1, d2):
    return betainc(d2 / 2.0, d1 / 2.0, d2 / (d2 + d1 * x)) if x > 0 else 1.0


def bartlett(groups):
    k = len(groups)
    n = [len(g) for g in groups]
    s2 = [statistics.variance(g) for g in groups]
    N = sum(n)
    sp2 = sum((ni - 1) * v for ni, v in zip(n, s2)) / (N - k)
    num = (N - k) * math.log(sp2) - sum((ni - 1) * math.log(v) for ni, v in zip(n, s2))
    den = 1.0 + (sum(1.0 / (ni - 1) for ni in n) - 1.0 / (N - k)) / (3.0 * (k - 1))
    T = num / den
    return T, k - 1, chi2_sf(T, k - 1)


def brown_forsythe(groups):
    """Levene's test centred on each group's median (Brown-Forsythe), as scipy.stats.levene(center='median')."""
    z = [[abs(v - statistics.median(g)) for v in g] for g in groups]
    k = len(z)
    N = sum(len(g) for g in z)
    zm = [statistics.fmean(g) for g in z]
    zall = statistics.fmean([v for g in z for v in g])
    num = (N - k) * sum(len(g) * (m - zall) ** 2 for g, m in zip(z, zm))
    den = (k - 1) * sum((v - m) ** 2 for g, m in zip(z, zm) for v in g)
    W = num / den
    return W, k - 1, N - k, f_sf(W, k - 1, N - k)


def verdict(off, hw, band):
    return ("NO CORRECTION" if abs(off) + hw <= band else
            ("CORRECTION" if (abs(off) - hw > 0 and abs(off) >= band) else "UNRESOLVED"))


def offset_interval(o, r, s2, dfs):
    """score_e123.cv_class's offset interval for one rule, with s'^2 and its df given (the class N^2 kept, its df the rule's
    own two-way residual df, the gate-share term in the variance and not in the df, t floored as score_e94.t975)."""
    k = o["k"]
    df_res = k * (NPASS - 1)                      # (k draws + the committed tile - 1) x (passes - 1)
    N2 = CL[o["class"]]["N_w"] ** 2
    kn = (o["slope_w_per_unit"] * r["rule_gate_share"]["se_of_mean"]) ** 2
    a, b = s2 / k, N2
    dfo = (a + b) ** 2 / (a * a / dfs + b * b / df_res)
    se = math.sqrt(a + b + kn)
    kind_hw = s94.t975(dfs) * math.sqrt(a + kn)
    return {"hw": s94.t975(dfo) * se, "hw_exact_t": t975_exact(dfo) * se, "df": dfo, "kind_hw": kind_hw}


print("E123 corrections after verification: numbers from scored.json and predictions-e123.json (post hoc, labelled)\n")

print("[C1] the class pooling: each rule's own SD of the adjusted draws (rule_s_w) against its class's pooled s'")
print("     registered = score_e123's interval (recomputed here as a check of the formula); own SD = the same formula with the")
print("     rule's own s' and k - 1 df in place of the class's; t floored as the scorer's t975, and at the exact fractional df")
for c, o in RO.items():
    r = RN[c]
    k = o["k"]
    cls = o["class"]
    reg_iv = offset_interval(o, r, CL[cls]["s_w"] ** 2, CL[cls]["df_s"])
    own_iv = offset_interval(o, r, o["rule_s_w"] ** 2, k - 1)
    chk = abs(reg_iv["hw"] - o["offset_halfwidth_w"]) < 1e-9 and abs(reg_iv["df"] - o["offset_df"]) < 1e-9 \
        and abs(reg_iv["kind_hw"] - o["kind_mean_halfwidth_w"]) < 1e-9
    off = o["offset_w"]
    print(f"  {c:15s} {cls:2s} k {k}  s' own {o['rule_s_w']:.3f} vs class {CL[cls]['s_w']:.3f} ({CL[cls]['df_s']} df) | offset {off:+.3f}")
    print(f"      registered: +- {o['offset_halfwidth_w']:.3f} ({o['offset_df']:.1f} df) {o['R2']}; formula check {'ok' if chk else 'MISMATCH'}")
    print(f"      own SD:     +- {own_iv['hw']:.3f} ({own_iv['df']:.1f} df, t floored) [{off - own_iv['hw']:+.3f}, {off + own_iv['hw']:+.3f}] "
          f"{verdict(off, own_iv['hw'], r['band_w'])}; exact t: +- {own_iv['hw_exact_t']:.3f} [{off - own_iv['hw_exact_t']:+.3f}, "
          f"{off + own_iv['hw_exact_t']:+.3f}] {verdict(off, own_iv['hw_exact_t'], r['band_w'])}; kind's D {o['kind_mean_w']:.3f} +- "
          f"{own_iv['kind_hw']:.3f} (own SD) against +- {o['kind_mean_halfwidth_w']:.3f} (registered)")
    print(f"      |offset| + half-width - band ({r['band_w']:.2f}): registered {abs(off) + o['offset_halfwidth_w'] - r['band_w']:+.4f}; "
          f"own SD {abs(off) + own_iv['hw'] - r['band_w']:+.4f} (t floored), {abs(off) + own_iv['hw_exact_t'] - r['band_w']:+.4f} (exact t)")
fz = RN["fp16.sparse50"]["desk_table_e94"]
print(f"  fp16.sparse50's frozen offsets (E94's desk table): gate law {fz['gate_law_offset_w']:+.3f}, Q130(n) {fz['q130n_offset_w']:+.3f} W")
print("  are the adjusted draws' SDs equal inside each class? (scored.json adjusted_w)")
for cls in ("G", "LF", "LI"):
    groups = [list(o["adjusted_w"].values()) for o in RO.values() if o["class"] == cls]
    T, dfb, pb = bartlett(groups)
    W, d1, d2, pw = brown_forsythe(groups)
    print(f"    {cls:2s}: Bartlett {T:.2f} on {dfb} df, p {pb:.4f}; Brown-Forsythe F({d1}, {d2}) = {W:.3f}, p {pw:.4f}")

print("\n[C2] the committed tiles' gate-share gaps at D(random) per unit: beta x (rule mean - committed gate share)")
gaps = []
for c, o in RO.items():
    r = RN[c]
    gap = r["rule_gate_share"]["mean"] - r["committed_gate_share"]
    pred = r["cv_slope_w_per_unit"] * gap
    gaps.append((c, gap, pred, o["offset_w"]))
    print(f"  {c:15s} gap {gap:+.4f} x {r['cv_slope_w_per_unit']:.2f} = {pred:+.3f} W; measured offset {o['offset_w']:+.3f} W")
print(f"  |gap| range {min(abs(g) for _, g, _, _ in gaps):.4f} to {max(abs(g) for _, g, _, _ in gaps):.4f}")
rest = [p for c, _, p, _ in gaps if c != "fp16.sparse50"]
rest2 = [p for c, _, p, _ in gaps if c not in ("fp16.sparse50", "fp16.wsparse50", "fp32.nn_like")]
print(f"  largest |prediction| without fp16.sparse50: {max(abs(p) for p in rest):.3f} W; "
      f"without fp16.sparse50, fp16.wsparse50 and fp32.nn_like: {max(abs(p) for p in rest2):.3f} W")

print("\n[C3] fp16 50% zeros in the page's frame (E78's S, the page's cell, less the measured offset)")
o = RO["fp16.sparse50"]
r = RN["fp16.sparse50"]
own_iv = offset_interval(o, r, o["rule_s_w"] ** 2, o["k"] - 1)
s78 = r["e78_a3"]["S_w"]
print(f"  page's S {s78:.2f} - offset {o['offset_w']:+.3f} = {s78 - o['offset_w']:.2f} W, +- {o['offset_halfwidth_w']:.2f} (registered) "
      f"or +- {own_iv['hw']:.2f} (own SD); this session's frame: committed S {o['committed_S_w']['mean']:.2f}, kind's S "
      f"{o['kind_S_w']['mean_w']:.2f} +- {o['kind_S_w']['halfwidth_w']:.2f} W")
s1 = P["rules"]["E123-S1"]["cells"]["fp16.sparse50"]
print(f"  this session's committed D {s1['D_w']:.3f} against E78's {s1['ref_w']:.3f}: {s1['minus_ref_w']:+.3f} W (S1 band {s1['band_w']})")
others = [abs((RN[c]["e78_a3"]["S_w"] - x["offset_w"]) - x["kind_S_w"]["mean_w"]) for c, x in RO.items() if c != "fp16.sparse50"]
print(f"  the two frames on the other eleven rows differ by {max(others):.3f} W at most; fp16.sparse50's by "
      f"{abs((s78 - o['offset_w']) - o['kind_S_w']['mean_w']):.3f} W")

print("\n[C4] the bridge: E94's draws of fp32 ReLU x small weights read on both cards (D(draw) - D(committed); E123-R8 draws)")
br = P["rules"]["E123-R8"]["draws"]
a3 = [v["aifoundry3_w"] for v in br.values()]
c1 = [v["card1_w"] for v in br.values()]
c1s = [v["card1_scaled_w"] for v in br.values()]
print(f"  {len(a3)} draws: SD {statistics.stdev(a3):.3f} W on aifoundry3; {statistics.stdev(c1):.3f} W on card 1, "
      f"{statistics.stdev(c1s):.3f} W at E82's fp32 scale ({reg['bridge']['card_scale_fp32']:.4f})")
nn = {d: v for d, v in P["draws"].items() if v["rule_of"] == "fp32.nn_like"}
comm = RO["fp32.nn_like"]["committed_D_w"]
plain = {d: comm + v["minus_committed_w"] for d, v in nn.items()}
print("  fp32.nn_like's draws on aifoundry3 (plain means, W): " + ", ".join(f"{d.split('_')[-1]} {x:.2f}" for d, x in plain.items()))
print(f"  plain SD over its {len(plain)} draws {statistics.stdev(plain.values()):.3f} W (tau {RO['fp32.nn_like']['plain_spread']['tau_w']:.3f}); "
      f"without e123d1 {statistics.stdev([x for d, x in plain.items() if not d.endswith('e123d1')]):.3f} W; "
      f"the five bridge draws alone {statistics.stdev([plain[d] for d in br]):.3f} W")
print("  E94 on card 1 (posthoc_e123.txt [D]): fp32.sparse50 0.493, fp16.nn_like 0.565, fp32.nn_like 0.552 W; only fp32.nn_like is a rule of both")

print("\n[C5] what the gate share leaves: the SD of the adjusted draws (each with its tile's own noise in it)")
for cls in ("G", "LF", "LI"):
    per = ", ".join(f"{c} {o['rule_s_w']:.3f}" for c, o in RO.items() if o["class"] == cls)
    print(f"  {cls:2s}: pooled {CL[cls]['s_w']:.3f} W ({CL[cls]['df_s']} df); per rule {per}")

print("\n[C6] table cells (the registered primary; aifoundry3 card 0, 600 MHz, passes 12310 and 12311): value +- 95% half-width")
print("     D over the type's zeros (kind_mean_w +- kind_mean_halfwidth_w); S over idle (kind_S_w); nJ per op and pJ per MAC from S,")
print("     the half-widths scaled with S (score_e123: 1e9 S / rate, / MACs per op)")
for c, o in RO.items():
    ks = o["kind_S_w"]
    q = o["kind_nj_op_S"] / ks["mean_w"]
    qc = o["committed_nj_op_S"] / o["committed_S_w"]["mean"]
    m = o["kind_pj_mac_S"] / ks["mean_w"]
    print(f"  {c:15s} D {o['kind_mean_w']:7.3f} +- {o['kind_mean_halfwidth_w']:.3f} | S {ks['mean_w']:7.3f} +- {ks['halfwidth_w']:.3f} | "
          f"nJ/op {o['kind_nj_op_S']:7.3f} +- {ks['halfwidth_w'] * q:.3f} | pJ/MAC {o['kind_pj_mac_S']:.4f} +- {ks['halfwidth_w'] * m:.4f} | "
          f"R2 {o['R2']}; linear in S: {'ok' if abs(q - qc) < 1e-9 else 'MISMATCH'}")

print("\n[C7] E94's form (plain mean over draws, the rule's own s; secondary): offset +- half-width, W")
for c, o in RO.items():
    e = o.get("e94_form")
    if not e:
        print(f"  {c:15s} -  (two draws)")
        continue
    print(f"  {c:15s} {e['R2']:14s} {e['offset_w']:+.4f} +- {e['offset_halfwidth_w']:.4f}  ->  ({e['offset_w']:+.2f} +- {e['offset_halfwidth_w']:.2f})")
