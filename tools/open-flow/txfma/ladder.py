#!/usr/bin/env python3
"""Fit the open flow's ladder the way reduce_hl.py fits E60's: slope over h >= 1 with a free
intercept, against the designed operand-bit flips and against the counted bus bits."""
import json
import sys

OUT = sys.argv[1]
MULADDS = 512.0
BUS = {  # bench ACCT bus_toggles, whole run of 512 multiply-adds
    "lq_h0": 99, "lq_h1": 1123, "lq_h2": 2147, "lq_h4": 4617, "lq_h8": 6959,
    "lb_h0": 119, "lb_h1": 1565, "lb_h2": 2532, "lb_h4": 3891, "lb_h8": 6666,
    "randn": 17349, "ones": 31, "zeros": 0,
}


def fit(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return b, my - b * mx


def energy(tag):
    d = json.load(open(f"{OUT}/power_gr_{tag}.json"))
    return d["energy_J"] / MULADDS, d["internal_estimate"]["switching_plus_internal_J"] / MULADDS


print(f"{'fam':4} {'reg':9} {'slope fJ':>10} {'intercept fJ':>13}  (and with the cells' internal energy)")
rows = {}
for fam in ("lq", "lb"):
    z = f"{fam}_h0"
    ez, ezi = energy(z)
    hs = [1, 2, 4, 8]
    pts = [(h, *energy(f"{fam}_h{h}")) for h in hs]
    for reg in ("designed", "bus"):
        if reg == "designed":
            xs = [h for h, _, _ in pts]
        else:
            xs = [BUS[f"{fam}_h{h}"] / MULADDS - BUS[z] / MULADDS for h, _, _ in pts]
        ys = [(e - ez) * 1e15 for _, e, _ in pts]
        yi = [(e - ezi) * 1e15 for _, _, e in pts]
        s, c = fit(xs, ys)
        si, ci = fit(xs, yi)
        rows[(fam, reg)] = (s, c, si, ci)
        print(f"{fam:4} {reg:9} {s:10.2f} {c:13.2f}   {si:9.2f} {ci:12.2f}")
    # two-point, h8 against h0, for comparison with the first write-up
    e8 = dict((h, e) for h, e, _ in pts)[8]
    print(f"     two-point h8-h0: {(e8-ez)*1e12:.4f} pJ over 8 designed bits = "
          f"{(e8-ez)/8*1e15:.2f} fJ;  over {BUS[fam+'_h8']/MULADDS - BUS[z]/MULADDS:.2f} bus bits = "
          f"{(e8-ez)/(BUS[fam+'_h8']/MULADDS - BUS[z]/MULADDS)*1e15:.2f} fJ")

E60 = {("lq", "designed"): 116.746, ("lq", "bus"): 74.658,
       ("lb", "designed"): 129.918, ("lb", "bus"): 85.578}
print("\nagainst E60 (aifoundry3, 600 MHz, 521.8 mV, reduce.txt of 2026-10-20-bitflip-ladder):")
for k, v in E60.items():
    s, c, si, ci = rows[k]
    print(f"  {k[0]} per {k[1]:9} open {s:7.2f} fJ   board {v:7.3f} fJ   "
          f"{s / v * 100:5.1f} %   (with internal {si:6.2f} fJ -> {si / v * 100:5.1f} %)")
