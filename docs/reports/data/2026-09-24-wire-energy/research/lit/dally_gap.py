#!/usr/bin/env python3
"""Which process is Dally's ~100 fJ/b-mm for, and is a 2x gap expected? The arithmetic behind research/DALLY-NODES.md
and the heat-per-mm page's section 7b (the owner's question of 28 September 2026, Q63).

    python3 docs/reports/data/2026-09-24-wire-energy/research/lit/dally_gap.py [report.json]

Reads the page's data (report.json, built by tools/ettelem/build_wire_report.py, whose LIT holds Dally's figures with
their process, voltage and definition) and prints: each figure per random bit per mm, the switched capacitance per mm
it implies, and what it predicts for the ET-SoC-1 mesh at 0.485 V; the voltage the ~100 can have been made at; the
three readings of "the 2x"; and the size of each explanation. Conventions: a random bit switches its wire half the
time and each transition dissipates 1/2 C V^2, so E = C V^2 / 4 per random bit per mm and C = 4 E / V^2; energies
move between voltages as V^2 at constant C (full-swing CMOS). Nothing here is measured; the measured values are the
page's (report.json "headline")."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "report.json")))
V0 = R["inputs"]["noc_v"]["value"]
H = R["headline"]
sq = lambda v: (V0 / v) ** 2
ceff = lambda e, v: 4 * e / v ** 2

meas = {k: (H[k]["random_bit_data"]["mean"], H[k]["random_bit_total"]["mean"])
        for k in ("uncontended/noc_rail", "loaded/noc_rail", "uncontended/board", "loaded/board")}
print(f"Measured at {V0} V, fJ per random bit per mm (data-dependent, everything) and the C they imply (fF/mm):")
for k, (d, t) in meas.items():
    print(f"  {k:22s} {d:5.1f} {t:5.1f}   C {ceff(d, V0):4.0f} {ceff(t, V0):4.0f}")

L = sorted([l for l in R["literature"] if l.get("dally")], key=lambda l: (l["year"], -(l["v"] or 0)))
print("\nDally's figures: fJ per bit per mm as given; at their own voltage, the C they imply; predicted at", V0, "V")
for l in L:
    e = l["fj_bit_mm"]
    if l.get("c_rep_ff_mm"):
        pr = (f"{l['c_ff_mm'] * V0 ** 2 / 4:5.1f}-{l['c_rep_ff_mm'] * V0 ** 2 / 4:.1f} (C V^2/4 with its own {l['c_ff_mm']} fF/mm of wire, "
              f"{l['c_rep_ff_mm']} with repeaters; as it counts, C V^2 at its {l['v']} V: {l['c_ff_mm'] * l['v'] ** 2:.0f})")
    elif l.get("c_ff_mm"):
        pr = f"{l['c_ff_mm'] * V0 ** 2 / 4:5.1f} (C V^2/4 with its own {l['c_ff_mm']} fF/mm)"
    elif l.get("counting") and l["v"]:
        pr = f"{e * sq(l['v']) / 4:5.1f} (a quarter of its full charge per bit, from {l['v']} V; {e * sq(l['v']):.0f} as it counts)"
    elif l["v"]:
        pr = f"{e * sq(l['v']):5.1f} (from {l['v']} V; C {ceff(e, l['v']):.0f} fF/mm)"
    else:
        pr = " / ".join(f"{e * sq(v):5.1f}" for v in (0.9, 0.7, 0.5)) + " if made at 0.9 / 0.7 / 0.5 V"
    rng = f"{l['range'][0]}-{l['range'][1]}" if l.get("range") else f"{e:g}"
    print(f"  {l['year']}{'*' if l.get('table') is False else ' '}{l['label'][:52]:52s} {l['node']:12s} {rng:>6s} -> {pr}")

dated = [l for l in L if l["v"] and not l.get("c_ff_mm") and not l.get("counting") and 2011 <= l["year"] <= 2014]   # the 2011-14 tables
pd = [l["fj_bit_mm"] * sq(l["v"]) for l in dated]
kek = next(l for l in dated if l["node"] == "40 nm")
c40 = ceff(kek["fj_bit_mm"], kek["v"])
c10 = [ceff(l["fj_bit_mm"], l["v"]) for l in dated if l["node"] == "10 nm"]
vl = next(l for l in L if l.get("c_ff_mm") and l.get("range"))   # VLSI 2018
print("(Rows the page's table leaves out, table: False, are marked * above.)")
cw = vl["c_ff_mm"]
print(f"\nThe 2011-14 tables ({min(l['v'] for l in dated)}-{max(l['v'] for l in dated)} V) predict {min(pd):.1f}-{max(pd):.1f} "
      f"fJ per random bit.mm at {V0} V")
print(f"C implied: {c40:.0f} fF/mm at 40 nm, {min(c10):.0f}-{max(c10):.0f} at 10 nm: x{min(c10) / c40:.2f}-{max(c10) / c40:.2f}")
print(f"The 100 as a voltage, with C from {cw} (VLSI 2018) to {c40:.0f} fF/mm (40 nm table): per random bit "
      f"{math.sqrt(400 / c40):.2f}-{math.sqrt(400 / cw):.2f} V; per transition {math.sqrt(200 / c40):.2f}-{math.sqrt(200 / cw):.2f} V")
print(f"At 0.5 V the 100 needs {200 / 0.25:.0f} fF/mm per transition, {400 / 0.25:.0f} per random bit: "
      f"{200 / 0.25 / cw:.0f}-{400 / 0.25 / cw:.0f} times {cw}")
print(f"VLSI 2018's {vl['range'][0]}-{vl['range'][1]} as C V^2/4 with {cw} fF/mm: "
      f"{math.sqrt(4 * vl['range'][0] / cw):.2f}-{math.sqrt(4 * vl['range'][1] / cw):.2f} V")

# Dally's group's node scaling (Villa et al., SC14, Table II): a fixed length of wire, 28 -> 7 nm and 14 -> 7 nm
WS = R["wire_scaling"]
e = lambda n: WS["ewire"][WS["nodes"].index(n)]
vn = lambda n: WS["v_nominal"][WS["nodes"].index(n)]
s287, v287 = e("7nm") / e("28nm"), (vn("7nm") / vn("28nm")) ** 2
s147, v147 = e("7nm") / e("14nm"), (vn("7nm") / vn("14nm")) ** 2
print(f"\nSC14: wire energy 28 -> 7 nm x{s287:.2f} = voltage x{v287:.3f} ({vn('28nm')} -> {vn('7nm')} V) * the rest x{s287 / v287:.2f}; "
      f"14 -> 7 nm x{s147:.3f} = x{v147:.3f} * x{s147 / v147:.3f}")
r28, r14 = 100 * s287 * sq(vn("7nm")), 100 * s147 * sq(vn("7nm"))
print(f"  100 fJ at 28 nm -> {100 * s287:.0f} at 7 nm ({vn('7nm')} V) -> {r28:.1f} at {V0} V; 100 at 14 nm -> {100 * s147:.0f} -> {r14:.1f}")

# two other meshes measured on silicon with the data's switching controlled
pit = next(l for l in R["literature"] if l.get("mesh") and l.get("pj_flit_hop"))
raw = next(l for l in R["literature"] if l.get("mesh") and l.get("pj_word_hop_full_toggle"))
pdat = [(pit["pj_flit_hop"]["half"] - pit["pj_flit_hop"]["none"]) / pit["flit_bits"] * 1000 / h for h in pit["hop_mm"][::-1]]
pfix = [pit["pj_flit_hop"]["none"] / pit["flit_bits"] * 1000 / h for h in pit["hop_mm"][::-1]]
rdat = raw["pj_word_hop_full_toggle"] / raw["word_bits"] * 1000 / 2 / raw["hop_mm"][0]
print(f"Piton ({pit['node']}, {pit['v']} V): data {pdat[0]:.1f}-{pdat[1]:.1f}, none {pfix[0]:.1f}-{pfix[1]:.1f} fJ per bit.mm; "
      f"C {ceff(pdat[0], pit['v']):.0f}-{ceff(pdat[1], pit['v']):.0f} fF/mm; at {V0} V data {pdat[0] * sq(pit['v']):.1f}-{pdat[1] * sq(pit['v']):.1f}, "
      f"none {pfix[0] * sq(pit['v']):.1f}-{pfix[1] * sq(pit['v']):.1f}; routers (no switching) {pit['pj_flit_hop']['none'] / pit['pj_flit_hop']['half']:.2f} of a hop")
print(f"Raw ({raw['node']}, {raw['v']} V): {rdat:.0f} fJ per random bit.mm (half a full toggle); C {ceff(rdat, raw['v']):.0f} fF/mm; "
      f"at {V0} V {rdat * sq(raw['v']):.1f}")

ud, ut = meas["uncontended/noc_rail"]
hd, ht = meas["loaded/noc_rail"]
s09 = (0.9 / V0) ** 2
print("\nThe three readings of 'the 2x':")
print(f"  (a) as measured, mesh rail: {ut:.1f}-{ht:.1f} = {ut / 100:.2f}-{ht / 100:.2f} of 100; board "
      f"{meas['uncontended/board'][1]:.1f}-{meas['loaded/board'][1]:.1f}")
print(f"  (b) everything at 0.9 V: {ut * s09:.0f}-{ht * s09:.0f} = x{ut * s09 / 100:.2f}-{ht * s09 / 100:.2f}; data only {ud * s09:.0f}-{hd * s09:.0f}")
print(f"  (c) Dally's own: {vl['range'][0]}-{vl['range'][1]} (2018) and 30 (2022) against 100: x{100 / vl['range'][1]:.1f}-{100 / vl['range'][0]:.1f}")
print(f"  a 100 made at 0.5 V would leave the mesh {100 * sq(0.5) / ht:.1f}-{100 * sq(0.5) / ut:.1f} x below it in all")

W = R["first_principles"]["at_0485"]["per_random_bit_fj_mm"]
dn = R["wire"]["disjoint_flows"]["noc_pj_per_byte"]
cont = [dn["wu"]["random_fj_per_bit_hop"]["per_card"][h]["mean"] / dn["wsep_d1_4"]["random_fj_per_bit_hop"]["per_card"][h]["mean"] - 1
        for h in dn["wu"]["random_fj_per_bit_hop"]["per_card"] if h in dn["wsep_d1_4"]["random_fj_per_bit_hop"]["per_card"]]
mn = H["v2/noc_rail"]
a, b = mn["per_transition"]["mean"], mn["per_one"]["mean"]
ones = [c["mean"] for c in R["check_v3"]["items"]["P6a"]["per_card"].values()]
dv = [l["v"] for l in L if l["v"]]
print("\nExplanations, sizes:")
print(f"  voltage: x{1 / sq(min(dv)):.2f}-{1 / sq(max(dv)):.2f} from {min(dv)}-{max(dv)} V; x{1 / sq(0.7):.2f}-{1 / sq(0.9):.2f} from 0.7-0.9 V; "
      f"a 0.6 V step x{(0.6 / V0) ** 2:.2f}")
print(f"  what a hop counts: everything / data x{ut / ud:.2f}-{ht / hd:.2f}; data / plain 7 nm wire ({W[0]:.1f}-{W[2]:.1f}) "
      f"x{ud / W[2]:.2f}-{hd / W[0]:.2f}")
print(f"  contention (loaded / free, 1-4 hops, mesh rail, per card): +{100 * min(cont):.0f}-{100 * max(cont):.0f}%")
print(f"  per bit or per transition: Keckler x{kek['per_transition'] / kek['fj_bit_mm']:.2f}; here (a+b)/2/a = {(a + b) / 2 / a:.2f} "
      f"(a {a:.1f}, b {b:.1f} fJ/mm)")
print(f"  meter: board / mesh rail x{meas['uncontended/board'][1] / ut:.2f}-{meas['loaded/board'][1] / ht:.2f}")
print(f"  ones: per-one share of a random bit's data cost {b / (a + b):.2f}; all ones over random +{100 * min(ones):.0f}-{100 * max(ones):.0f}%")
print(f"  node: C x{min(c10) / c40:.2f}-{max(c10) / c40:.2f} from 40 to 10 nm; x{s287 / v287:.2f} from 28 to 7 nm (SC14, the voltage taken out)")
uf, hf = H["uncontended/noc_rail"]["fixed_per_bit"]["mean"], H["loaded/noc_rail"]["fixed_per_bit"]["mean"]
print(f"  the data-independent part: {100 * uf / ut:.0f}-{100 * hf / ht:.0f}% of a hop here")
print(f"\nThe scaled rule at {V0} V: {r28:.1f}-{r14:.1f}; measured in all x{ut / max(r28, r14):.2f}-{ht / min(r28, r14):.2f} of it, data x{ud / max(r28, r14):.2f}-{hd / min(r28, r14):.2f}")
