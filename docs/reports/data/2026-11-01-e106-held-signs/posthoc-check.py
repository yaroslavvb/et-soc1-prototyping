#!/usr/bin/env python3
"""E106: what the README quotes beyond scored.json. Standard library only; run it in this directory after collection. POST HOC: no rule of E106's depends on it.

    python3 posthoc-check.py > posthoc-check.txt

A: every contrast and share on the board, per pass. B: the same on the minion rail, which the board meter's dips do not touch (Drail carries E78's rail term, 0.81 k). C: the arms. D: fp16's z_ss against E104's z_s, what A's signs add. E: the sign bits by E92's price list, modelled. F: the rest, read two ways. G: how near each held tile is to signs. H: the read-back.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T975 = {1: 12.706, 2: 4.303, 3: 3.182}
P = json.load(open(os.path.join(HERE, "e106.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
REG = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/predictions-e106.json")))
SPEC = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/e106/e106.json")))
E104 = json.load(open(os.path.join(HERE, "..", "2026-11-01-e104-c-readback", "e104.json")))
E104G = json.load(open(os.path.join(HERE, "..", "2026-11-01-e104-c-readback", "e104-gatesoff.json")))
RATE = P["items"]["fp16.randn"]["rate"]["mean"]


def mci(v):
    v = list(v)
    if len(v) < 2:
        return (v[0] if v else float("nan")), float("nan"), len(v)
    return sum(v) / len(v), T975[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def pp(res, plus, minus, key="D"):
    out = {}
    for p, it in sorted(res["per_pass"].items()):
        if all(n in it and it[n].get(key) is not None for n in list(plus) + list(minus)):
            out[p] = sum(it[n][key] for n in plus) - sum(it[n][key] for n in minus)
    return out


C = REG["contrasts"]
print("A. The board, primary, per pass")
for n, c in C.items():
    v = pp(P, c["plus"], c["minus"])
    m, h, k = mci(v.values())
    print(f"  {n:14s} {m:6.3f} ± {h:5.3f} (n={k}) M4 {c['M']:5.2f} ± {c['half95']:4.2f} | {' '.join(f'{p[-2:]}:{x:.3f}' for p, x in v.items())}")
for n, s in REG["shares"].items():
    a, b = pp(P, C[s["held"]]["plus"], C[s["held"]]["minus"]), pp(P, C[s["step"]]["plus"], C[s["step"]]["minus"])
    m, h, k = mci([a[p] / b[p] for p in a])
    print(f"  share {n:10s} {m:.3f} ± {h:.3f} (n={k}) M4 {s['M']:.3f} | of means {sum(a.values()) / sum(b.values()):.3f}")
print("B. The rail, primary, per pass")
for n, c in C.items():
    v = pp(P, c["plus"], c["minus"], "Drail")
    m, h, k = mci(v.values())
    print(f"  {n:14s} {m:6.3f} ± {h:5.3f} (n={k}) | {' '.join(f'{p[-2:]}:{x:.3f}' for p, x in v.items())}")
for n, s in REG["shares"].items():
    a, b = pp(P, C[s["held"]]["plus"], C[s["held"]]["minus"], "Drail"), pp(P, C[s["step"]]["plus"], C[s["step"]]["minus"], "Drail")
    m, h, k = mci([a[p] / b[p] for p in a])
    print(f"  share {n:10s} {m:.3f} ± {h:.3f} (n={k})")
a, b = pp(P, C["fp16.held_z"]["plus"], C["fp16.held_z"]["minus"], "Drail"), pp(P, C["fp16.step"]["plus"], C["fp16.step"]["minus"], "Drail")
c, d = pp(P, C["fp32.held"]["plus"], C["fp32.held"]["minus"], "Drail"), pp(P, C["fp32.step"]["plus"], C["fp32.step"]["minus"], "Drail")
m, h, k = mci([a[p] / b[p] - c[p] / d[p] for p in a])
print(f"  fp16's z_ss share less fp32's, rail: {m:+.3f} ± {h:.3f} (n={k})")
print("C. The arms: R3, R4, R5 and R6's numbers")
for a_, v in SC["arms"].items():
    r = v["rules"]
    print(f"  {a_:11s} passes {[p for p in v['passes']]}: fp32 {r['E106-R3']['share']:.3f} ± {r['E106-R3']['ci95']:.3f} {r['E106-R3']['verdict']}; z_ss {r['E106-R4']['share']:.3f} ± {r['E106-R4']['ci95']:.3f} {r['E106-R4']['verdict']}; x_s {r['E106-R5']['share']:.3f} ± {r['E106-R5']['ci95']:.3f} {r['E106-R5']['verdict']}; difference {r['E106-R6']['difference']:+.3f} ± {r['E106-R6']['ci95']:.3f} {r['E106-R6']['verdict']}")
print("D. fp16: z_ss (A's signs moving, this session) against E104's z_s (A's signs still, same B), each over c_abs in its own session")
m, h, k = mci(pp(P, ["fp16.z_ss"], ["fp16.c_abs"]).values())
print(f"  z_ss - c_abs here {m:.3f} ± {h:.3f} (n={k})")
m, h, k = mci(pp(E104, ["fp16.z_s"], ["fp16.c_abs"]).values())
print(f"  z_s - c_abs, E104 primary {m:.3f} ± {h:.3f} (n={k})")
m, h, k = mci(pp(E104G, ["fp16.z_s"], ["fp16.c_abs"]).values())
print(f"  z_s - c_abs, E104 all three {m:.3f} ± {h:.3f} (n={k})")
print("E. The carry E104 used, against this session: E92's dips-removed step x 0.9722, and E88's held part on this card")
for t, v in REG["rules"]["E106-R2"]["carried_w"].items():
    m, h, k = mci(pp(P, C[f"{t}.step"]["plus"], C[f"{t}.step"]["minus"]).values())
    print(f"  {t} step: carried {v:.3f}, here {m:.3f} ± {h:.3f}, here/carried {m / v:.3f}")
m, h, k = mci(pp(P, ["fp32.s_abs"], ["fp32.c_abs"]).values())
print(f"  fp32 s_abs - c_abs: here {m:.3f} ± {h:.3f}; E88 on this card 2.524 ± 0.185; E92 on aifoundry3 2.520 ± 0.171 x 0.9722 = {2.520 * 0.9722:.3f}")
print("F. Sign flips an op, alternations, and result bits on the sums the card holds: how near each held tile is to signs (make_e106's counts at two op indices)")
for n in ("fp16.signs", "fp16.z_ss", "fp16.x_s", "fp16.c_abs", "fp16.x_c", "fp16.ones", "fp32.signs", "fp32.s_abs", "fp32.c_abs", "fp32.ones"):
    t = SPEC["tiles"][n]
    k_ = t["counts_real"]
    print(f"  {n:11s} A flips {t['stats']['sign_flips_per_op_a']:5d} B flips {t['stats']['sign_flips_per_op_b']:5d} bus {t['stats']['bus_bits_per_op']:5d} alternations {k_['alt1']:5.0f} {k_['alt2']:5.0f} result bits {k_['cbus'] + k_['rbus'] + k_['store']:7.0f}")
print("G. Modelled, not measured: the sign bits by E92's price list x s_abs' flips, fp32 0.569, fp16 0.297 W, x 0.9722; what is left of the held part")
for t, bits, held in (("fp32", 0.569, "fp32.held"), ("fp16", 0.297, "fp16.held_z")):
    m, h, k = mci(pp(P, C[held]["plus"], C[held]["minus"]).values())
    print(f"  {t}: sign bits {bits * 0.9722:.2f} W; the held part less them {m - bits * 0.9722:.2f} W")
print("H. A second reading of the rest. The alternation's price falls on moving sums, so part of the rest may be the adder alternating at its moving price: E104's m premium (all-three means) x signs' alternation rate. Modelled, and not additive with the held part")
for t, prem, alt in (("fp32", 2.099, SPEC["tiles"]["fp32.signs"]["counts_real"]["alt1"]), ("fp16", 3.253, SPEC["tiles"]["fp16.signs"]["counts_real"]["alt1"])):
    m, h, k = mci(pp(P, C[f"{t}.step"]["plus"], C[f"{t}.step"]["minus"]).values())
    sw = prem * alt / 3840
    bits = {"fp32": 0.569, "fp16": 0.297}[t] * 0.9722
    print(f"  {t}: step {m:.2f} W = sign bits {bits:.2f} + the switch at its moving price {sw:.2f} (premium {prem}, {alt:.0f} of 3,840 alternations) + what is left {m - bits - sw:.2f}")
print("I. The read-back")
rows = SC["readback"]["rows"]
for t in sorted({r["tile"] for r in rows}):
    x = [r for r in rows if r["tile"] == t]
    print(f"  {t:11s} n {','.join(str(r['n']) for r in x):22s} minions {min(r['minions'] for r in x)} equals {','.join(SC['readback']['tiles'][t])} | at the last n: C00 {x[-1]['card_c00']} C08 {x[-1]['card_c08']}, {x[-1]['card_distinct_words']} words")
print(f"  {len(rows)} reads; all 1,024 minions on one C in {sum(1 for r in rows if r.get('all_minions_agree'))}")
