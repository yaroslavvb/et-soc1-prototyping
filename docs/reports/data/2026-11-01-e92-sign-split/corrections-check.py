#!/usr/bin/env python3
"""E92, the desk check behind README.md's "Corrections after verification" (C1-C13): every number those corrections cite, read from
committed files and recomputed here. No card touched, nothing re-run, and no frozen or data file changed. Standard library only; run it
from this directory:   python3 corrections-check.py > corrections-check.txt

Primary reduction: e92.json, scored.json. Registered dips-removed arm: dips-arm/. Bench: bench-prediction-de545f0c.json, the file as Q132(b)
froze it (git show de545f0c:docs/reports/data/2026-11-01-q132-rtl-bench/e92-bench-prediction.json). Counts: tools/claims-v3/kinds/e92/e92.json.
"Adder bits" are what E92.md and predictions-e92.json call flop bits (C4)."""
import json
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
e = json.load(open(os.path.join(HERE, "e92.json")))
n = json.load(open(os.path.join(HERE, "dips-arm", "e92-nodips.json")))
s = json.load(open(os.path.join(HERE, "scored.json")))
sn = json.load(open(os.path.join(HERE, "dips-arm", "scored-nodips.json")))
dips = json.load(open(os.path.join(HERE, "dips-arm", "dips.json")))
fit = json.load(open(os.path.join(HERE, "posthoc-fit.json")))
bench = json.load(open(os.path.join(HERE, "bench-prediction-de545f0c.json")))["variants"]["nets_hier2"]
spec = json.load(open(os.path.join(K, "e92", "e92.json")))
reg = json.load(open(os.path.join(K, "predictions-e92.json")))
T = spec["tiles"]
ARMS = (("primary", e, s), ("dips-removed", n, sn))
OPS = 600e6 / 546 * 1024


def mc(v):
    v = list(v)
    m = st.fmean(v)
    return m, (st.stdev(v) / math.sqrt(len(v)) * T95[len(v) - 1]) if len(v) > 1 else float("nan")


def perpass(res, name, key="D"):
    return [res["per_pass"][str(p)][name][key] for p in res["passes"]]


def diff(res, a, b, key="D"):
    return [x - y for x, y in zip(perpass(res, a, key), perpass(res, b, key))]


def pm(v, nd=3):
    m, c = mc(v)
    return f"{m:+.{nd}f} +- {c:.{nd}f}"


def rate(res, name):
    return res["items"][name]["rate"]["mean"]


def res_bits(name):
    t = T.get(name) or spec["references"][name]
    return t["stream"]["res_bits_per_op"]


def adder_bits(name):
    t = T.get(name) or spec["references"][name]
    return t["sign"]["flops"]


def both(a, b, key="D"):
    return f"primary {pm(diff(e, a, b, key))}; dips-removed {pm(diff(n, a, b, key))}"


print("# C1. fp16: the frozen share in each arm, and the dips in fp16.c_abs")
for nm, res, sc in ARMS:
    print(f"  {nm}: fp16.c_abs D per kept pass {[round(x, 3) for x in perpass(res, 'fp16.c_abs')]}, mean {pm(perpass(res, 'fp16.c_abs'))}")
    print(f"  {nm}: fp16.ones - c_abs {pm(diff(res, 'fp16.ones', 'fp16.c_abs'))}")
    b16, b32 = sc["budget"]["fp16"], sc["budget"]["fp32"]
    print(f"  {nm}: frozen share fp16 {b16['frozen_share']['mean']:.3f} +- {b16['frozen_share']['ci95']:.3f}; fp32 {b32['frozen_share']['mean']:.3f} +- {b32['frozen_share']['ci95']:.3f}")
    print(f"  {nm}: fp16 frozen s_abs - c_abs {pm(diff(res, 'fp16.s_abs', 'fp16.c_abs'))}; moving part {b16['moving_sum_part_w']['mean']:+.3f} +- {b16['moving_sum_part_w']['ci95']:.3f}; h_sub - c_abs {pm(diff(res, 'fp16.h_sub', 'fp16.c_abs'))}; gamma {sc['factorial']['fp16']['gamma_w']['mean']:.3f} W, {sc['factorial']['fp16']['gamma_fj_per_lane_alternation']:.0f} fJ")
med = {}
for line in open(os.path.join(HERE, "crude-check.txt")):
    m = re.match(r"(\S+)\s+-\s+(\S+)\s+([+-][0-9.]+) \+- ([0-9.]+)", line)
    if m:
        med[(m.group(1), m.group(2))] = (float(m.group(3)), float(m.group(4)))
print(f"  raw medians (crude-check.txt): fp16 s_abs - c_abs {med[('fp16.s_abs', 'fp16.c_abs')][0]:.3f} / signs - ones {med[('fp16.signs', 'fp16.ones')][0]:.3f} = {med[('fp16.s_abs', 'fp16.c_abs')][0] / med[('fp16.signs', 'fp16.ones')][0]:.3f}; fp32 {med[('fp32.s_abs', 'fp32.c_abs')][0]:.3f} / {med[('fp32.signs', 'fp32.ones')][0]:.3f} = {med[('fp32.s_abs', 'fp32.c_abs')][0] / med[('fp32.signs', 'fp32.ones')][0]:.3f}")
print("  the moving-sum part per result bit: (signs - ones) - (s_abs - c_abs), over the result bits it adds, at each tile's measured rate")
price = {}
for nm, res, sc in ARMS:
    for ty in ("fp32", "fp16"):
        mv = [a - b for a, b in zip(diff(res, f"{ty}.signs", f"{ty}.ones"), diff(res, f"{ty}.s_abs", f"{ty}.c_abs"))]
        dres = (res_bits(f"{ty}.signs") - res_bits(f"{ty}.ones")) - (res_bits(f"{ty}.s_abs") - res_bits(f"{ty}.c_abs"))
        price[(nm, ty)] = 1e15 * mc(mv)[0] / (dres * rate(res, f"{ty}.signs"))
        print(f"    {nm} {ty}: {pm(mv)} W over {dres:,.0f} result bits: {price[(nm, ty)]:.1f} fJ a bit")
    wc = diff(res, "fp32.w_c", "fp32.c_abs")
    dr, df = res_bits("fp32.w_c") - res_bits("fp32.c_abs"), adder_bits("fp32.w_c") - adder_bits("fp32.c_abs")
    rt = rate(res, "fp32.w_c")
    print(f"    {nm} fp32 w_c - c_abs, no alternation: {pm(wc)} W over {dr:,.0f} result bits and {df:,.0f} adder bits: {1e15 * (mc(wc)[0] - df * rt * 7e-15) / (dr * rt):.1f} fJ a result bit after 7 fJ per adder bit")
ratio_w = mc(diff(n, "fp32.w_h_sub", "fp32.w_h_add"))[0] / mc(diff(n, "fp32.h_sub", "fp32.h_add"))[0]
rest = mc(diff(n, "fp16.s_abs", "fp16.c_abs"))[0] - reg["contrasts"]["fp16.s_abs-c_abs"]["bits_w"]
dres16 = res_bits("fp16.signs") - res_bits("fp16.ones")
print(f"  the verifier's post-hoc arithmetic, fp32's two prices on fp16 (dips-removed): bits {reg['contrasts']['fp16.signs-ones']['bits_w']:.3f} + {rest:.3f} x {ratio_w:.3f} = {rest * ratio_w:.3f} (the switch; a fall of {rest * (1 - ratio_w):.2f} W) + {dres16:,.0f} x 30 fJ x 1.121e9 = {dres16 * 30e-15 * 1.121e9:.3f} (the sums) = {reg['contrasts']['fp16.signs-ones']['bits_w'] + rest * ratio_w + dres16 * 30e-15 * 1.121e9:.2f} W; measured {pm(diff(n, 'fp16.signs', 'fp16.ones'))}")

print()
print("# C2. R2 at the registered level")
print("  primary", s["rules"]["E92-R2"]["verdict"], s["rules"]["E92-R2"]["contrasts"], "; leakage arms", s["rules"]["E92-R2"]["arms"], "; dips-removed", sn["rules"]["E92-R2"]["verdict"])
los = []
for k in s["rules"]["E92-R2"]["contrasts"]:
    d, pr = s["contrasts"][k]["D_w"], s["contrasts"][k]["pred_w"]
    lo, hi = d["mean"] - d["ci95"], d["mean"] + d["ci95"]
    los.append((lo, k))
    print(f"  {k}: {d['mean']:.3f} +- {d['ci95']:.3f}, [{lo:.2f}, {hi:.2f}]; confirmed inside [{0.5 * pr:.2f}, {2 * pr:.2f}], refuted below {0.25 * pr:.2f} or above {4 * pr:.2f}")
print(f"  the lowest lower bound of the four: {min(los)[0]:.2f} W ({min(los)[1]})")
for arm, sc in s["arms_contrasts"].items():
    print(f"  {arm}: h_sub - h_add verdicts fp32 {sc['fp32.h_sub-h_add']['verdict']}, fp16 {sc['fp16.h_sub-h_add']['verdict']}; c_alt fp16 {sc['fp16.c_alt-c_abs']['verdict']} {sc['fp16.c_alt-c_abs']['D_w']['mean']:.3f} +- {sc['fp16.c_alt-c_abs']['D_w']['ci95']:.3f}")

print()
print("# C3. the fp32 split: what is measured, what is modelled")
sw = T["fp32.signs"]["sign"]["N_alt1"] / T["fp32.w_h_sub"]["sign"]["N_alt1"]
ss = T["fp32.s_abs"]["sign"]["N_alt1"] / T["fp32.h_sub"]["sign"]["N_alt1"]
bs, bg = reg["contrasts"]["fp32.s_abs-c_abs"]["bits_w"], reg["contrasts"]["fp32.signs-ones"]["bits_w"]
for nm, res, sc in ARMS:
    tot, froz = diff(res, "fp32.signs", "fp32.ones"), diff(res, "fp32.s_abs", "fp32.c_abs")
    fm, fc = mc(froz)
    wp = mc(diff(res, "fp32.w_h_sub", "fp32.w_h_add"))[0]
    g = sc["factorial"]["fp32"]["gamma_w"]["mean"]
    print(f"  {nm}: measured signs - ones {pm(tot)}, s_abs - c_abs {pm(froz)}; bits (price list x flips, modelled) {bs:.3f} (s_abs), {bg:.3f} (signs)")
    print(f"    upper: all of s_abs - c_abs beyond its bits {fm - bs:.3f}, [{fm - fc - bs:.2f}, {fm + fc - bs:.2f}]; gamma x s_abs' rate {ss:.4f} = {g * ss:.2f} W overshoots it")
    print(f"    lower: the w premium {wp:.3f} x signs' rate {sw:.4f} = {wp * sw:.3f} W; the residual (moving part) {sc['budget']['fp32']['moving_sum_part_w']['mean']:.3f} +- {sc['budget']['fp32']['moving_sum_part_w']['ci95']:.3f}")
    dr = res_bits("fp32.signs") - res_bits("fp32.ones")
    wc, ddr, ddf = mc(diff(res, "fp32.w_c", "fp32.c_abs"))[0], res_bits("fp32.w_c") - res_bits("fp32.c_abs"), adder_bits("fp32.w_c") - adder_bits("fp32.c_abs")
    rt = rate(res, "fp32.w_c")
    pz = (wc - ddf * rt * 7e-15) / (ddr * rt)
    sums = pz * dr * rate(res, "fp32.signs")
    print(f"    at w_c's price {pz * 1e15:.1f} fJ a result bit, signs' {dr:,.0f} result bits are {sums:.3f} W: bits {bg:.3f} + switch {wp * sw:.3f} + sums {sums:.3f} = {bg + wp * sw + sums:.3f} W against {mc(tot)[0]:.3f}, {mc(tot)[0] - (bg + wp * sw + sums):.2f} W unaccounted")

print()
print("# C4. the premium over the adder bits, with the model's e88 part: (premium - e88) / d adder bits, at the tile's measured rate")
scale = reg["models"]["card_scale"]["fp32"]
print(f"  registered f {reg['models']['f_fj_per_flop_bit']:.2f} fJ (card 1); card scale {scale:.4f}. Column 'scaled' divides the premium by the scale first.")
for label, hi, lo in (("frozen, magnitude 1", "fp32.h_sub", "fp32.h_add"), ("frozen, random magnitudes", "fp32.r_h_sub", "fp32.r_h_add"),
                      ("moving sums, magnitude 1", "fp32.w_h_sub", "fp32.w_h_add"), ("moving sums, random magnitudes", "fp32.wr_h_sub", "fp32.wr_h_add")):
    c = reg["contrasts"][f"fp32.{hi.split('.')[1]}-{lo.split('.')[1]}"]
    dbits = adder_bits(hi) - adder_bits(lo)
    for nm, res, sc in ARMS:
        m, ci = mc(diff(res, hi, lo))
        rt = rate(res, hi)
        print(f"  {label:32s} {nm:13s} premium {m:+.3f} +- {ci:.3f}; e88 {c['e88']['mu']:+.3f}; d adder bits {dbits:,.0f}; premium / bits {1e15 * m / dbits / rt:5.2f}; (premium - e88) / bits {1e15 * (m - c['e88']['mu']) / dbits / rt:5.2f} +- {1e15 * ci / dbits / rt:5.2f} fJ; scaled {1e15 * (m / scale - c['e88']['mu']) / dbits / rt:5.2f}")
d = sn["contrasts"]["fp32.wr_h_sub-wr_h_add"]["D_w"]
pred = reg["contrasts"]["fp32.wr_h_sub-wr_h_add"]["pred_w"]
print(f"  wr, dips-removed: [{d['mean'] - d['ci95']:.3f}, {d['mean'] + d['ci95']:.3f}] against e88+flops {pred:.3f} and E90 read as linear {reg['contrasts']['fp32.wr_h_sub-wr_h_add']['e90_linear_w']:.2f}: the model misses by {d['mean'] - pred:.2f} W, {d['mean'] / pred:.2f}x")
hs = T["fp32.h_sub"]["sign"]
print(f"  the count on fp32.h_sub, per op: csa_in3 {hs['csa3']:,.0f} (combinational: txfma_f3.v:430, no flop), comb_s {hs['comb_s']:,.0f}, comb_c {hs['comb_c']:,.0f}, comb_add {hs['comb_add']:,.0f}; total {hs['flops']:,.0f}")
v = e["v_mean"]
print(f"  7 fJ per bit at {v:.4f} V is {7e-15 / v ** 2 * 1e15:.1f} fF (E = C V^2): a proxy for everything downstream of those bits, not a flop's price")
print("  fp16's premium with the model's e88 part, fJ per adder bit:")
for label, hi, lo in (("both", "fp16.h_sub", "fp16.h_add"), ("sum signs only", "fp16.c_alt", "fp16.c_abs"), ("high product", "fp16.hh_sub", "fp16.c_abs"), ("low product", "fp16.hl_sub", "fp16.c_abs"), ("random signs", "fp16.s_abs", "fp16.c_abs")):
    c = reg["contrasts"][f"fp16.{hi.split('.')[1]}-{lo.split('.')[1]}"]
    dbits = adder_bits(hi) - adder_bits(lo)
    print(f"    {label:16s} " + "; ".join(f"{nm} {1e15 * (mc(diff(res, hi, lo))[0] - c['e88']['mu']) / dbits / rate(res, hi):5.2f}" for nm, res, sc in ARMS))


def solve(Atr, b):
    """Gaussian elimination with partial pivoting on a small square system."""
    m = len(b)
    M = [list(Atr[i]) + [b[i]] for i in range(m)]
    for c in range(m):
        p = max(range(c, m), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, m):
            f = M[r][c] / M[c][c]
            for j in range(c, m + 1):
                M[r][j] -= f * M[c][j]
    x = [0.0] * m
    for c in range(m - 1, -1, -1):
        x[c] = (M[c][m] - sum(M[c][j] * x[j] for j in range(c + 1, m))) / M[c][c]
    return x


def lsq(rows, feats):
    sc_ = [max(abs(r[f]) for r in rows) or 1.0 for f in feats]
    X = [[r[f] / a for f, a in zip(feats, sc_)] for r in rows]
    y = [r["D"] for r in rows]
    k = len(feats)
    A = [[sum(x[i] * x[j] for x in X) for j in range(k)] for i in range(k)]
    b = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(k)]
    c = solve(A, b)
    return {f: cc / a for f, cc, a in zip(feats, c, sc_)}


def rms(rows, co):
    return math.sqrt(st.fmean((r["D"] - sum(co[f] * r[f] for f in co)) ** 2 for r in rows))


def fj(co, f):
    return co[f] * 1e15 / OPS


print()
print("# C5. the post-hoc refit: in-sample, and across families (posthoc-fit.json's rows, E92's designs = its tiles less .signs)")
F4 = ("live", "bus", "prod", "res")
F5 = F4 + ("flops",)
FA = F4 + ("alt",)
for ty, rows in fit["tiles"].items():
    des = [r for r in rows if r["name"] in T and not r["name"].endswith(".signs")]
    oth = [r for r in rows if r not in des]
    print(f"  {ty}: {len(rows)} tiles, {len(des)} E92 designs, {len(oth)} others")
    for lab, fe in (("four prices", F4), ("+ adder bits", F5), ("+ alternations", FA)):
        ca = lsq(rows, fe)
        co = lsq(oth, fe)
        cd = lsq(des, fe)
        extra = fe[-1] if fe is not F4 else None
        line = f"    {lab:15s} in-sample, all tiles: rms {rms(rows, ca):.3f} W. Fit on the others, predict E92's designs: rms {rms(des, co):.3f} W. Fit on the designs, predict the others: rms {rms(oth, cd):.3f} W."
        if extra:
            line += f" Its price {fj(ca, extra):.1f} fJ (all), {fj(co, extra):.1f} (others), {fj(cd, extra):.1f} (designs)."
        line += f" Result-bit price {fj(ca, 'res'):.1f} (all), {fj(co, 'res'):.1f} (others), {fj(cd, 'res'):.1f} (designs)."
        print(line)
    co = lsq(oth, F5)
    by = {r["name"]: r for r in rows}
    for a, b in (("h_sub", "h_add"),):
        A, B = by[f"{ty}.{a}"], by[f"{ty}.{b}"]
        print(f"    {a} - {b}: measured {A['D'] - B['D']:+.2f}; the fit on the others alone says {sum(co[f] * (A[f] - B[f]) for f in F5):+.2f} W")
for k, m in fit["models"].items():
    print(f"  posthoc-fit.json {k}: rms {m['rms_w']:.3f}, leave-one-out {m['loo_rms_w']:.3f}, E86 held out {m['held_out_rms_w']:.3f} W")

print()
print("# C6. fp16's alternation over fp32's")
for nm, res, sc in ARMS:
    r = [a / b for a, b in zip(diff(res, "fp16.h_sub", "fp16.h_add"), diff(res, "fp32.h_sub", "fp32.h_add"))]
    print(f"  {nm}: per-pass ratio {pm(r)} {[round(x, 3) for x in r]}")
tb = bench["tiles_D_over_zeros_w"]
print(f"  the bench, frozen (de545f0c, nets_hier2): {tb['fp16.h_sub'] - tb['fp16.h_add']:.2f} / {tb['fp32.h_sub'] - tb['fp32.h_add']:.2f} = {(tb['fp16.h_sub'] - tb['fp16.h_add']) / (tb['fp32.h_sub'] - tb['fp32.h_add']):.2f}")
print(f"  fp32 h_sub - h_add: bench / measured {(tb['fp32.h_sub'] - tb['fp32.h_add']) / s['contrasts']['fp32.h_sub-h_add']['D_w']['mean']:.3f} (primary)")

print()
print("# C7. the pin: this directory's copy of the bench's frozen file")
import hashlib  # noqa: E402
raw = open(os.path.join(HERE, "bench-prediction-de545f0c.json"), "rb").read()
fz = json.loads(raw)
print(f"  sha256 {hashlib.sha256(raw).hexdigest()[:16]}, variants {list(fz['variants'])}; nets_hier2 carries d_unit_hier2_by_stage_per_op: {'d_unit_hier2_by_stage_per_op' in fz['variants']['nets_hier2']['contrasts_w'][0]}")

print()
print("# C8. a lane alternation against a sign flip, by regime")
for nm, res, sc in ARMS:
    f_ = sc["factorial"]["fp32"]
    rt = f_["rate_ops_per_s"]
    a0 = 1e15 * mc(diff(res, "fp32.h_add", "fp32.c_abs"))[0] / 4096 / rt
    print(f"  {nm}: gamma {f_['gamma_fj_per_lane_alternation']:.0f} fJ per lane alternation; h_add - c_abs (all four sign paths moving, the adder only adds) {a0:.0f} fJ per lane-micro-op; alpha (B and product) {1e15 * f_['alpha_w']['mean'] / 4096 / rt:.0f} fJ; beta (C and result) {1e15 * f_['beta_w']['mean'] / 4096 / rt:.0f} fJ")
    for label, hi, lo in (("frozen, magnitude 1", "fp32.h_sub", "fp32.h_add"), ("moving sums, magnitude 1", "fp32.w_h_sub", "fp32.w_h_add"), ("moving sums, random", "fp32.wr_h_sub", "fp32.wr_h_add")):
        p = 1e15 * mc(diff(res, hi, lo))[0] / 3840 / rate(res, hi)
        print(f"    {label:26s} premium per alternation {p:6.0f} fJ, {p / a0:.1f}x the {a0:.0f} fJ")

print()
print("# C9. the rail per pass, primary")
print("  i_sub - i_add", [round(x, 3) for x in diff(e, "fp32.i_sub", "fp32.i_add", "Drail")], pm(diff(e, "fp32.i_sub", "fp32.i_add", "Drail")))
print("  i_sub - i_add over h_sub - h_add on the rail:", round(mc(diff(e, "fp32.i_sub", "fp32.i_add", "Drail"))[0] / mc(diff(e, "fp32.h_sub", "fp32.h_add", "Drail"))[0], 3))
print("  wr_h_sub - wr_h_add", [round(x, 3) for x in diff(e, "fp32.wr_h_sub", "fp32.wr_h_add", "Drail")], "board", [round(x, 3) for x in diff(e, "fp32.wr_h_sub", "fp32.wr_h_add")])

print()
print("# C10. wording: the counts and times behind it")
print(f"  fp32.c_alt: B sign flips {T['fp32.c_alt']['stats']['sign_flips_per_op_b']}, product sign flips {T['fp32.c_alt']['sign']['P_sign']:.0f}, all from the k = 0 row; beta {s['factorial']['fp32']['beta_w']['mean']:.3f} W")
print(f"  rail: fp32 h_sub - h_add {pm(diff(e, 'fp32.h_sub', 'fp32.h_add', 'Drail'))}; fp16 {pm(diff(e, 'fp16.h_sub', 'fp16.h_add', 'Drail'))}")
d = s["contrasts"]["fp16.h_allsub-h_add"]["D_w"]
print(f"  fp16 h_allsub - h_add high end {d['mean'] + d['ci95']:.3f} W against 0.50 W: {s['contrasts']['fp16.h_allsub-h_add']['verdict']}")
for line in open(os.path.join(HERE, "logs", "e92-queue.log")):
    if re.search(r"p92\d\d (starts|rc=)", line):
        print("  queue:", line.strip()[:60])
print("  the bench's file was committed at 00:43:14 PDT (de545f0c): 9210 and 9211 had finished and 9212 was running; no pass was pulled before 00:55:57")

print()
print("# C11. registered reported items: each against E65's 0.563 W, and E88's contrasts on this card")
for a, b in (("fp32.h_add", "fp32.c_abs"), ("fp32.w_h_add", "fp32.w_c"), ("fp32.r_h_add", "fp32.r_abs"), ("fp32.wr_h_add", "fp32.r_walk"), ("fp32.i_add", "fp32.c_abs")):
    print(f"  {a} - {b}: {both(a, b)}; result bits {res_bits(a):,.0f} against {res_bits(b):,.0f}")
e88 = json.load(open(os.path.join(HERE, "..", "2026-10-31-e88-result-path", "scored.json")))["primary"]["contrasts"]
for label, a, b in (("M32", "fp32.r_abs", "fp32.c_abs"), ("R32", "fp32.r_walk", "fp32.r_abs"), ("W32", "fp32.ones", "fp32.c_abs")):
    print(f"  E88's {label} on this card: {both(a, b)}; E88 on card 1: {e88[label]['D']['mean']:.3f} +- {e88[label]['D']['ci95']:.3f}")
clean = json.load(open(os.path.join(K, "predictions-e90.json")))["sign_bit_prices"]["fp32"]["A_clean_arm"]["dW"]
print(f"  E65 bit_31 {reg['models']['sign_bit_prices_w']['fp32']['B']:.4f} W; E67 abit_31 {reg['models']['sign_bit_prices_w']['fp32']['A']:.4f} W; its post-hoc clean price {clean:.4f} W (predictions-e90.json)")
print(f"  rest of the registered budget: gamma at signs' rate fp32 {s['budget']['fp32']['alternation_at_signs_rate_w']['mean']:.3f} +- {s['budget']['fp32']['alternation_at_signs_rate_w']['ci95']:.3f} ({sn['budget']['fp32']['alternation_at_signs_rate_w']['mean']:.3f} +- {sn['budget']['fp32']['alternation_at_signs_rate_w']['ci95']:.3f}), fp16 {s['budget']['fp16']['alternation_at_signs_rate_w']['mean']:.3f} +- {s['budget']['fp16']['alternation_at_signs_rate_w']['ci95']:.3f} ({sn['budget']['fp16']['alternation_at_signs_rate_w']['mean']:.3f} +- {sn['budget']['fp16']['alternation_at_signs_rate_w']['ci95']:.3f})")
print(f"  frozen left after bits and gamma at s_abs' rate: fp32 {s['budget']['fp32']['frozen_left_after_bits_and_alternation_w']['mean']:+.3f} +- {s['budget']['fp32']['frozen_left_after_bits_and_alternation_w']['ci95']:.3f} ({sn['budget']['fp32']['frozen_left_after_bits_and_alternation_w']['mean']:+.3f} +- {sn['budget']['fp32']['frozen_left_after_bits_and_alternation_w']['ci95']:.3f}), fp16 {s['budget']['fp16']['frozen_left_after_bits_and_alternation_w']['mean']:+.3f} +- {s['budget']['fp16']['frozen_left_after_bits_and_alternation_w']['ci95']:.3f} ({sn['budget']['fp16']['frozen_left_after_bits_and_alternation_w']['mean']:+.3f} +- {sn['budget']['fp16']['frozen_left_after_bits_and_alternation_w']['ci95']:.3f})")

print()
print("# C12. the dips: E92.md's words and posthoc_dips_e92.py's rule")
rows = [r for v in dips["passes"].values() for r in v["rows"]]
depth = [min(r["neighbours_w"]) - r["board_w"] for r in rows]
print(f"  {dips['definition']}")
print(f"  {len(rows)} dips, depth below the lower neighbour {min(depth):.2f}-{max(depth):.2f} W")
pw = [r for r in rows if r["in_power_window"]]
print(f"  {len(pw)} in power windows, depth {min(min(r['neighbours_w']) - r['board_w'] for r in pw):.2f}-{max(min(r['neighbours_w']) - r['board_w'] for r in pw):.2f} W, {min(r['ms_after_launch_boundary'] for r in pw)}-{max(r['ms_after_launch_boundary'] for r in pw)} ms after a launch boundary")
inr = [r for r in rows if r["where"].startswith("run")]
print(f"  {len(inr)} in runs, {max(r['ms_after_launch_boundary'] for r in inr)} ms at most after a launch boundary")
print("  contrasts whose mean moves by 0.25 W or more between the primary and the dips-removed arm:")
for k, c in s["contrasts"].items():
    a, b = c["D_w"]["mean"], sn["contrasts"][k]["D_w"]["mean"]
    if abs(a - b) >= 0.25:
        print(f"    {k:26s} {a:+.3f} -> {b:+.3f}")
d = s["contrasts"]["fp32.wr_h_sub-wr_h_add"]["D_w"]["mean"], sn["contrasts"]["fp32.wr_h_sub-wr_h_add"]["D_w"]["mean"]
print(f"  fp32 wr_h_sub - wr_h_add {d[0]:.3f} -> {d[1]:.3f}; raw median {med[('fp32.wr_h_sub', 'fp32.wr_h_add')][0]:.3f} +- {med[('fp32.wr_h_sub', 'fp32.wr_h_add')][1]:.3f}")

print()
print("# C13. the carried dip in the table cells")
for nm, res, sc in ARMS:
    it = res["items"]["fp16.c_abs"]
    print(f"  {nm}: fp16.c_abs D {it['D']['mean']:.3f} +- {it['D']['ci95']:.3f}; S {it['S']['mean']:.3f} +- {it['S']['ci95']:.3f}; pJ/MAC by S {it['pj_mac_S']['mean']:.4f} +- {it['pj_mac_S']['ci95']:.4f}")
print()
print("# Frozen files: no change. Their sha256, for the record")
for f in ("e92.json", "scored.json", "results.md", "dips-arm/e92-nodips.json", "dips-arm/scored-nodips.json", "runs.csv"):
    print(f"  {hashlib.sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest()[:16]}  {f}")
for f in ("E92.md", "predictions-e92.json", "e92/e92.json"):
    print(f"  {hashlib.sha256(open(os.path.join(K, f), 'rb').read()).hexdigest()[:16]}  tools/claims-v3/kinds/{f}")
