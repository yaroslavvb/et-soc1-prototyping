#!/usr/bin/env python3
"""Which bits, at a fixed number of bits: the one clean contrast in the committed data.

E60 ran `lq_h2` (the two LOWEST mantissa bits) and `ls_h2` (two bits SPREAD across the mantissa)
on aifoundry2, same pass set, same clock, same zero. Both flip m = 2 bits of B per transition.
If company erased the position premium, the two would cost the same.
"""
import json, os, sys
D = sys.argv[1] + "/docs/reports/data"
L = lambda p: json.load(open(os.path.join(D, p)))
E60 = L("2026-10-20-bitflip-ladder/hl.json")["cards"]
E65 = L("2026-10-26-e65-bit-prices-hart-ladder/hl.json")["cards"]["aifoundry3"]
MAN = {i["name"]: i for i in L("2026-10-20-bitflip-ladder/manifest.json")["items"]}
pB = {int(k): v["dW"] for k, v in E65["bits"].items()}


def mask_bits(h):
    return sorted(j for j in range(32) if int(MAN["ls_h%d" % h]["mask"], 16) >> j & 1)


a2 = E60["aifoundry2"]["items"]
lq, ls = a2["lq_h2"], a2["ls_h2"]
ls_bits, lq_bits = mask_bits(2), [0, 1]
r_meas = ls["d_p80"] / lq["d_p80"]
se_r = r_meas * ((ls["d_p80_se"] / ls["d_p80"]) ** 2 + (lq["d_p80_se"] / lq["d_p80"]) ** 2) ** 0.5
r_pred = sum(pB[j] for j in ls_bits) / sum(pB[j] for j in lq_bits)

print("WHICH BITS, AT A FIXED NUMBER OF BITS  (aifoundry2, 800 MHz, 9 passes each, zero lq_h0)")
print()
print("  item     m   bit positions   measured dW (W)    SE")
print("  lq_h2    2   %-13s   %7.3f        %.3f" % (lq_bits, lq["d_p80"], lq["d_p80_se"]))
print("  ls_h2    2   %-13s   %7.3f        %.3f" % (ls_bits, ls["d_p80"], ls["d_p80_se"]))
print()
print("  measured ls/lq ratio                 %.3f +- %.3f" % (r_meas, se_r))
print("  the single-bit price list predicts   %.3f   (aifoundry3's 32-position list, 600 MHz)" % r_pred)
print("  measured / predicted                 %.3f" % (r_meas / r_pred))
print()
print("  So at m = 2 the position premium is paid IN FULL: swapping bit 1 for bit %d more than" % ls_bits[1])
print("  doubles the cost of the same two flips. Compare the far end of the lq ladder, where")
print("  bits 16-22 are added in company:")
a3 = E60["aifoundry3"]
r16, r23 = a3["lq"]["rungs"]["lq_h16"], a3["lq"]["rungs"]["lq_h23"]
marg = (r23["dW"] - r16["dW"]) / 7
alone = sum(pB[j] for j in range(16, 23)) / 7
print("    lq_h16 -> lq_h23 adds 7 bits (16..22) for %.3f W, i.e. %.3f W each;" % (r23["dW"] - r16["dW"], marg))
print("    the same seven bits cost %.3f W each on their own (E65, same card and clock)." % alone)
print("    a %.1fx discount." % (alone / marg))
print()
print("  >>> the position premium is paid in full at m = 2 and is %.0f%% gone by m = 23." % (100 * (1 - marg / alone)))
print("      That is the compression, and it is a function of m. Only ONE spread rung has ever run")
print("      (ls_h2, on one card); make_hl.py already builds ls_h4, ls_h8, ls_h12 and ls_h16.")
json.dump({"card": "aifoundry2", "clock_mhz": 800,
           "lq_h2": {"bits": lq_bits, "dW": lq["d_p80"], "se": lq["d_p80_se"], "n": lq["n"]},
           "ls_h2": {"bits": ls_bits, "dW": ls["d_p80"], "se": ls["d_p80_se"], "n": ls["n"],
                     "mask": MAN["ls_h2"]["mask"]},
           "ratio_measured": r_meas, "ratio_measured_se": se_r,
           "ratio_predicted_from_price_list": r_pred, "measured_over_predicted": r_meas / r_pred,
           "marginal_high_bits_in_company_W": marg, "same_bits_alone_W": alone,
           "discount": alone / marg,
           "ls_rungs_ever_run": ["ls_h2 (aifoundry2 only)"],
           "ls_rungs_built_but_never_run": ["ls_h4", "ls_h8", "ls_h12", "ls_h16"]},
          open(sys.argv[2] + "/position.json", "w"), indent=1)
