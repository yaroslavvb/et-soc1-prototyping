#!/usr/bin/env python3
"""The effective price of a flipped bit IN COMPANY, for every multi-bit stimulus on
aifoundry3 at 600 MHz that has both a measured board power and an exact flip count."""
import json, os, sys
D = sys.argv[1] + "/docs/reports/data"
L = lambda p: json.load(open(os.path.join(D, p)))
E65 = L("2026-10-26-e65-bit-prices-hart-ladder/hl.json")["cards"]["aifoundry3"]
E60 = L("2026-10-20-bitflip-ladder/hl.json")["cards"]["aifoundry3"]
E67H = L("2026-10-27-e67-a-side-bit-prices/hl.json")["cards"]["aifoundry3"]
E67C = L("2026-10-27-e67-a-side-bit-prices/closure.json")
M60 = {i["name"]: i for i in L("2026-10-20-bitflip-ladder/manifest.json")["items"]}
M67 = {i["name"]: i for i in L("2026-10-27-e67-a-side-bit-prices/manifest.json")["items"]}
B_PRES, A_PRES = 4096, 2048
pB = {int(k): v["J_per_alternating_bit"] * 1e15 for k, v in E65["bits"].items()}
pA = {int(k): v["J_per_alternating_bit"] * 1e15 for k, v in E67H["a_bits"].items()}
rate60 = E60["items"]["lq_h0"]["rate"]

rows = []
# E60's lq ladder: contiguous LOW mantissa bits of B, quiet partner
for _, r in sorted(E60["lq"]["rungs"].items(), key=lambda kv: kv[1]["h"]):
    h = r["h"]
    if h == 0 or r["dW"] is None:
        continue
    flips = M60["lq_h%d" % h]["flips"]["b_all"]
    naive = sum(pB[j] for j in range(h)) * flips / h
    rows.append(dict(item="lq_h%d" % h, exp="E60", side="B", partner="A=1.0",
                     where="mantissa bits 0..%d, contiguous" % (h - 1), m=h, flips=flips,
                     W=r["dW"], rate=rate60, eff_fJ=r["dW"] / rate60 / flips * 1e15,
                     naive_fJ=naive / flips, naive_W=naive * 1e-15 * rate60))
# E67's whole-operand random items
for nm, hist, pl, pres in (("nrd_a", "A_hist", pA, A_PRES), ("nrd_b", "B_hist", pB, B_PRES)):
    it = E67C["items"][nm]
    h = it[hist]
    flips = sum(h)
    naive = sum(h[j] * pl[j] for j in range(32))
    rows.append(dict(item=nm, exp="E67", side=nm[-1].upper(),
                     partner="B=1.0" if nm == "nrd_a" else "A=1.0",
                     where="random normal fp32, all 32 positions", m=flips / pres, flips=flips,
                     W=it["measured_W"], rate=it["rate_ops_s"],
                     eff_fJ=it["measured_W"] / it["rate_ops_s"] / flips * 1e15,
                     naive_fJ=naive / flips, naive_W=naive * 1e-15 * it["rate_ops_s"]))
# the grid's 16 two-bit cells, pooled (one A bit + one B bit)
cells = E67H["ix"]["cells"]
rate67 = E67H["anchors"]["anchor_zeros"]["rate"]
tot_W = sum(c["cell_dW"] for c in cells.values()) / len(cells)
tot_naive = sum(c["sum_dW"] for c in cells.values()) / len(cells)
flips_cell = A_PRES + B_PRES
rows.append(dict(item="ix grid (16 cells, mean)", exp="E67", side="A+B", partner="both busy",
                 where="one A bit + one B bit, bits 0/8/16/22", m=2, flips=flips_cell, W=tot_W,
                 rate=rate67, eff_fJ=tot_W / rate67 / flips_cell * 1e15,
                 naive_fJ=tot_naive / flips_cell / rate67 * 1e15 * 1e15 / 1e15, naive_W=tot_naive))
rows[-1]["naive_fJ"] = tot_naive / rate67 / flips_cell * 1e15

print("The effective price of ONE flipped operand bit, by how much company it has")
print("(aifoundry3, 600 MHz, 0.522 V; every row is a measured board power over its own zero)")
print()
print(" item                      side  m bits   flips/op   measured W   effective fJ   price-list fJ   eff/list")
print(" ------------------------- ----  ------   --------   ----------   ------------   -------------   --------")
for r in sorted(rows, key=lambda r: r["m"]):
    print(" %-25s %-4s  %6.2f   %8d   %10.3f   %12.1f   %13.1f   %.2f"
          % (r["item"], r["side"], r["m"], r["flips"], r["W"], r["eff_fJ"], r["naive_fJ"],
             r["eff_fJ"] / r["naive_fJ"]))
sb = [r for r in rows if r["side"] == "B" and r["item"].startswith("lq")]
print()
print(" single-bit price list, for comparison:  B side %.0f-%.0f fJ (span %.1fx), A side %.0f-%.0f fJ (span %.1fx)"
      % (min(pB.values()), max(pB.values()), max(pB.values()) / min(pB.values()),
         min(pA.values()), max(pA.values()), max(pA.values()) / min(pA.values())))
eff = [r["eff_fJ"] for r in rows if r["m"] > 1]
print(" effective prices with m>1:  %.0f-%.0f fJ, span %.1fx" % (min(eff), max(eff), max(eff) / min(eff)))
json.dump({"rows": rows,
           "single_bit_span": {"B": [min(pB.values()), max(pB.values())], "A": [min(pA.values()), max(pA.values())]},
           "in_company_span_fJ": [min(eff), max(eff)], "in_company_span_ratio": max(eff) / min(eff)},
          open(sys.argv[2] + "/effective.json", "w"), indent=1)
