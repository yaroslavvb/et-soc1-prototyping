#!/usr/bin/env python3
"""Desk-only checks for the E79 corrections: every number the corrected README quotes that is not already a
scored.json key, recomputed from the committed per-run data (runs.csv) the way reduce_hlp.py does it.
Usage: python3 -I corrections-check.py docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices
Output committed beside it as corrections-check.txt (the README cites it as [n], the section numbers below)."""
import csv
import json
import math
import os
import statistics as st
import sys
from collections import defaultdict

D = sys.argv[1]
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
man = {it["name"]: it for it in json.load(open(os.path.join(D, "manifest.json")))["items"]}
H = json.load(open(os.path.join(D, "hlp.json")))["cards"]["aifoundry3"]
HL = json.load(open(os.path.join(D, "hlp-leak0.3803.json")))["cards"]["aifoundry3"]
S = json.load(open(os.path.join(D, "scored.json")))
SET_ASIDE = {x["pass"] for x in H["passes_set_aside"]}


def mci(v):
    v = [x for x in v if x is not None]
    n = len(v)
    if n == 0:
        return None, None, 0
    m = st.mean(v)
    if n < 2:
        return m, None, n
    return m, T95.get(n - 1, 1.96) * st.stdev(v) / math.sqrt(n), n


def per_pass(csvname):
    per = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader(open(os.path.join(D, csvname))):
        if r["fail"] or int(r["pass"]) in SET_ASIDE:
            continue
        p = int(r["pass"])
        per[p][r["item"]].append({k: (float(r[k]) if r[k] not in ("", "None") else None)
                                  for k in ("p80", "rail", "rate")})
    out = {}
    for p, d in per.items():
        out[p] = {}
        for it, rr in d.items():
            out[p][it] = {k: (st.mean([x[k] for x in rr if x[k] is not None])
                              if any(x[k] is not None for x in rr) else None) for k in ("p80", "rail", "rate")}
    return out


PER = per_pass("runs.csv")
PERL = per_pass("runs-leak0.3803.csv")
passes = sorted(PER)
print("passes kept:", passes)


def price_pp(per, item, count=None, key="p80"):
    it = man[item]
    z = it["zero"]
    nb = count or it["flips"][f"{it['side']}_all"]
    v = {}
    for p in sorted(per):
        if item in per[p] and z in per[p] and per[p][item]["rate"]:
            v[p] = (per[p][item][key] - per[p][z][key]) / (nb * per[p][item]["rate"]) * 1e15
    return v


def dw_pp(per, item):
    z = man[item]["zero"]
    return {p: per[p][item]["p80"] - per[p][z]["p80"] for p in sorted(per) if item in per[p] and z in per[p]}


# 0. the reconstruction matches the committed reduction
for it in ("b16_9", "b32_22", "b16p_9", "b8k_6", "a8_7"):
    m, hw, n = mci(list(price_pp(PER, it).values()))
    print(f"check {it}: {m:.2f} +- {hw:.2f} (n {n}) vs hlp.json {H['items'][it]['e_fJ']:.2f} +- "
          f"{H['items'][it]['e_fJ_ci95']:.2f}")

# 1. b16p_9 per pass, board and rail
bp = price_pp(PER, "b16p_9")
br = price_pp(PER, "b16p_9", key="rail")
print("\n[1] b16p_9 per pass, board fJ:", {p: round(v, 1) for p, v in bp.items()})
print("    b16p_9 per pass, rail fJ: ", {p: round(v, 1) for p, v in br.items()})
others = [v for p, v in bp.items() if p != 7921]
m, hw, n = mci(others)
print(f"    without 7921: {m:.1f} +- {hw:.1f} (n {n}), range {min(others):.1f}-{max(others):.1f}")
m, hw, n = mci(list(br.values()))
print(f"    rail arm, all 8: {m:.1f} +- {hw:.1f}")

# 2. same-session paired dW ratio fp16 B bit 9 over fp32 B bit 22
a, b = dw_pp(PER, "b16_9"), dw_pp(PER, "b32_22")
rr = [a[p] / b[p] for p in a if p in b]
m, hw, n = mci(rr)
print(f"\n[2] dW(b16_9)/dW(b32_22) paired per pass: {m:.3f} +- {hw:.3f} (n {n}); "
      f"ratio of means {H['items']['b16_9']['d_p80'] / H['items']['b32_22']['d_p80']:.3f}")

# 3. aligned positions against E65 (README block A table, bits 13-22, lines 73-82)
E65 = {13: 1.777, 14: 2.157, 15: 2.544, 16: 2.794, 17: 2.838, 18: 3.152, 19: 3.717, 20: 3.973, 21: 4.161, 22: 4.627}
al = {j: S["prices"]["fp16_b"][str(j)]["dW"] / E65[j + 13] for j in range(10)}
print("\n[3] fp16 B dW bit j / E65 fp32 B dW bit j+13:", {j: round(v, 3) for j, v in al.items()})
print(f"    range {min(al.values()):.3f}-{max(al.values()):.3f}, mean {st.mean(al.values()):.3f}")
print("    width model predicts dW ratio 2 x 11/24 = %.3f; equal watts per word predicts 1.000" % (2 * 11 / 24))

# 4. balanced fp16 over balanced fp32 (jgp), paired over the passes with both, and ratio of means
a, b = price_pp(PER, "b16p_9"), price_pp(PER, "b32p_22")
rr = [a[p] / b[p] for p in a if p in b]
m, hw, n = mci(rr)
f16, f32 = S["prices"]["fp16_b_jgp"]["9"], S["prices"]["fp32_b_jgp"]["22"]
r = f16["fJ"] / f32["fJ"]
rel = math.hypot(f16["fJ_ci95"] / f16["fJ"], f32["fJ_ci95"] / f32["fJ"])
print(f"\n[4] fJ(b16p_9)/fJ(b32p_22): paired over {n} block-B passes {m:.3f} +- {hw:.3f}; "
      f"ratio of means {r:.3f} [{r * (1 - rel):.2f}, {r * (1 + rel):.2f}] (first-order propagation)")
print("    per pass pairs:", {p: (round(a[p], 1), round(b[p], 1)) for p in a if p in b})

# 5. int8 jgp at the 1,024 count the int8 structure implies (A4/A6)
for lbl, per in (("fitted slope", PER), ("E71 slope", PERL)):
    v = price_pp(per, "b8p_6", count=1024)
    m, hw, n = mci(list(v.values()))
    k = price_pp(per, "b8k_6")
    mk, hwk, nk = mci(list(k.values()))
    print(f"\n[5] {lbl}: b8p_6 at 1,024: {m:.1f} +- {hw:.1f} fJ [{m - hw:.0f}, {m + hw:.0f}] (n {n}); "
          f"b8k_6 {mk:.1f} +- {hwk:.1f} (n {nk})")

# 6. int8 A on a per-unit footing (each A read feeds both TIMA units): every price halves
ia = S["prices"]["int8_a"]
mag = [ia[str(j)]["fJ"] for j in range(7)]
print(f"\n[6] int8 A per lane: MSB {ia['7']['fJ']:.1f}, magnitude {min(mag):.1f}-{max(mag):.1f}, mean {st.mean(mag):.2f}; "
      f"MSB/mean {ia['7']['fJ'] / st.mean(mag):.3f}")
print(f"    per unit (/2): MSB {ia['7']['fJ'] / 2:.1f} [{ia['7']['fJ_lo'] / 2:.0f}, {ia['7']['fJ_hi'] / 2:.0f}], "
      f"magnitude {min(mag) / 2:.1f}-{max(mag) / 2:.1f}")

# 7. what zeros save, per op and per MAC
for fmt, h0, macs in (("fp16", "h16q", 16 * 16 * 32), ("int8", "h8q", 16 * 16 * 64)):
    sw = S["switching"][fmt]
    rate = H["items"][h0]["rate"]
    nj = -sw["zeros_minus_h0_W"] / rate * 1e9
    print(f"\n[7] {fmt}: zeros - h0 {sw['zeros_minus_h0_W']:.3f} W at {rate:.4g} ops/s -> {nj:.3f} nJ per op, "
          f"{nj * 1e3 / macs:.4f} pJ per MAC ({macs} MACs an op)")
z16 = -S["switching"]["fp16"]["zeros_minus_h0_W"] / H["items"]["h16q"]["rate"]
z8 = -S["switching"]["int8"]["zeros_minus_h0_W"] / H["items"]["h8q"]["rate"]
print(f"    ratios: W {S['switching']['fp16']['zeros_minus_h0_W'] / S['switching']['int8']['zeros_minus_h0_W']:.2f}, "
      f"per op {z16 / z8:.2f}, per MAC {(z16 / 8192) / (z8 / 16384):.2f}")

# 8. rail arm over board arm, item by item
rows = []
for nm, it in H["items"].items():
    if it.get("e_fJ") and it.get("e_rail_fJ") is not None and it.get("d_p80") is not None:
        rows.append((nm, it["e_rail_fJ"] / it["e_fJ"], it["d_p80"], it["e_fJ_lo"] > 0))
res = [x for x in rows if x[3]]
big = [x for x in rows if abs(x[2]) >= 1.0]
print(f"\n[8] rail/board: {len(rows)} priced items; resolved {len(res)}: "
      f"{min(x[1] for x in res):.3f}-{max(x[1] for x in res):.3f} (median {st.median(x[1] for x in res):.3f}); "
      f"steps >= 1 W {len(big)}: {min(x[1] for x in big):.3f}-{max(x[1] for x in big):.3f} "
      f"(median {st.median(x[1] for x in big):.3f})")
print("    extremes among resolved:", sorted(res, key=lambda x: x[1])[:2], sorted(res, key=lambda x: x[1])[-2:])
pool = sum(H["items"][x[0]]["d_rail"] for x in big) / sum(x[2] for x in big)
print(f"    pooled d_rail/d_p80 over the >= 1 W steps: {pool:.3f}")

# 9. sensitivity ranges per list at E71's slope
print("\n[9] E71-slope change per list (positions whose fitted-slope interval excludes zero):")
for key in sorted(S["prices"]):
    ch = []
    for b, x in S["prices"][key].items():
        y = HL["prices"].get(key, {}).get(b)
        if x and y and x.get("fJ") and y.get("fJ") is not None and x["fJ_lo"] > 0:
            ch.append(100 * (y["fJ"] / x["fJ"] - 1))
    if ch:
        print(f"    {key}: {min(ch):+.1f}% to {max(ch):+.1f}% over {len(ch)} resolved positions")
    else:
        print(f"    {key}: no resolved position at the fitted slope")
print("    int8_b_kg at E71's slope:", {b: f"{y['fJ']:.0f} [{y['fJ_lo']:.0f}, {y['fJ_hi']:.0f}]"
                                         for b, y in sorted(HL['prices']['int8_b_kg'].items(), key=lambda t: int(t[0]))})
nres = sum(1 for y in HL["prices"]["int8_b_kg"].values() if y["fJ_lo"] > 0)
print(f"    int8_b_kg positions still resolved at E71's slope: {nres} of 8")
print("    int8_b_jgp at E71's slope:", {b: f"{y['fJ']:.1f} [{y['fJ_lo']:.1f}, {y['fJ_hi']:.1f}]"
                                          for b, y in HL['prices']['int8_b_jgp'].items()})

# 10. jg over jgp per bit, kg as a fraction of jg
for fmt, jg, jgp, kg in (("fp32", ("fp32_b", "22"), ("fp32_b_jgp", "22"), ("fp32_b_kg", "22")),
                         ("fp16", ("fp16_b", "9"), ("fp16_b_jgp", "9"), ("fp16_b_kg", "9"))):
    g, gp, k = S["prices"][jg[0]][jg[1]], S["prices"][jgp[0]][jgp[1]], S["prices"][kg[0]][kg[1]]
    print(f"\n[10] {fmt}: jg/jgp per bit {g['fJ'] / gp['fJ']:.2f}; kg {k['fJ']:.0f} [{k['fJ_lo']:.0f}, {k['fJ_hi']:.0f}]"
          f" = [{k['fJ_lo'] / g['fJ']:.2f}, {k['fJ_hi'] / g['fJ']:.2f}] of jg's per-bit price; "
          f"jgp {gp['fJ']:.0f} inside kg's interval: {k['fJ_lo'] <= gp['fJ'] <= k['fJ_hi']}")

# 11. the marginal against the single-bit rungs of the bits it adds
mg = S["marginal"]["fp16"]
b6, b7, b9 = (S["prices"]["fp16_b"][s]["fJ"] for s in ("6", "7", "9"))
print(f"\n[11] marginal {mg['fJ']:.1f} +- {mg['fJ_ci95']:.1f}; bits it adds 6, 7: {b6:.0f}, {b7:.0f} "
      f"(mean {(b6 + b7) / 2:.0f}, {((b6 + b7) / 2) / mg['fJ']:.2f}x); bit 9 {b9:.0f} ({b9 / mg['fJ']:.2f}x)")

# 12. MAC rates
r16, r8 = H["items"]["h16q"]["rate"], H["items"]["h8q"]["rate"]
print(f"\n[12] ops/s fp16 {r16:.4g}, int8 {r8:.4g}: ops ratio {r8 / r16:.3f}; MACs/s ratio "
      f"{(16384 * r8) / (8192 * r16):.3f}; cycles {S['cycles_per_op']}")

# 13. int8 jg dW range
d = [S["prices"]["int8_b"][str(j)]["dW"] for j in range(8)]
print(f"\n[13] int8 jg dW: {min(d):+.3f} to {max(d):+.3f} W; bit 6 {S['prices']['int8_b']['6']['dW']:.3f}")
print("     fp16 jg bit 9 dW %.3f, fp32 jg bit 22 dW %.3f" % (S["prices"]["fp16_b"]["9"]["dW"],
                                                           S["prices"]["fp32_b"]["22"]["dW"]))
print("     fp16 B list:", [round(S["prices"]["fp16_b"][str(j)]["fJ"]) for j in range(10)])

# 14. int8 B kg odd/even (4b) at both slopes
for lbl, P_ in (("fitted", S["prices"]), ("E71", HL["prices"])):
    kg = P_["int8_b_kg"]
    odd = st.mean(kg[str(j)]["fJ"] for j in (1, 3, 5))
    even = st.mean(kg[str(j)]["fJ"] for j in (0, 2, 4, 6))
    print(f"\n[14] {lbl}: int8 B kg odd mean {odd:.1f}, even mean {even:.1f}, ratio {odd / even:.2f}")
