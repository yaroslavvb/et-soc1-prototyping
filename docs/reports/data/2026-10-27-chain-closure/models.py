#!/usr/bin/env python3
"""Which law fits E60's lq ladder: position-weighted with compression, or flat per bit?"""
import json, math, os, sys
D = sys.argv[1] + "/docs/reports/data"
L = lambda p: json.load(open(os.path.join(D, p)))
E65 = L("2026-10-26-e65-bit-prices-hart-ladder/hl.json")["cards"]["aifoundry3"]
E60 = L("2026-10-20-bitflip-ladder/hl.json")["cards"]["aifoundry3"]
E67C = L("2026-10-27-e67-a-side-bit-prices/closure.json")
E67H = L("2026-10-27-e67-a-side-bit-prices/hl.json")["cards"]["aifoundry3"]
B_PRES, A_PRES = 4096, 2048
pB = {int(k): v["J_per_alternating_bit"] * 1e15 for k, v in E65["bits"].items()}
pA = {int(k): v["J_per_alternating_bit"] * 1e15 for k, v in E67H["a_bits"].items()}
rate60 = E60["items"]["lq_h0"]["rate"]

rows = []
for _, r in sorted(E60["lq"]["rungs"].items(), key=lambda kv: kv[1]["h"]):
    h = r["h"]
    if h == 0 or r["dW"] is None:
        continue
    meas_fJ_per_bit = r["dW"] / rate60 / (h * B_PRES) * 1e15
    naive_fJ_per_bit = sum(pB[j] for j in range(h)) / h
    rows.append((h, r["dW"], r["se"], meas_fJ_per_bit, naive_fJ_per_bit))

print(" m   dW (W)     SE     measured fJ/bit   naive fJ/bit   meas/naive")
for h, dw, se, m_, n_ in rows:
    print(" %2d  %7.3f  %6.3f      %7.1f         %7.1f        %.3f" % (h, dw, se, m_, n_, m_ / n_))

# model A: flat per flipped bit, position ignored
c = sum(dw / rate60 for h, dw, _, _, _ in rows) / sum(h * B_PRES for h, *_ in rows) * 1e15
predA = [c * h * B_PRES * 1e-15 * rate60 for h, *_ in rows]
# model B: position-weighted naive sum x m^(alpha-1), alpha fitted
pts = [(math.log(h), math.log((dw / rate60) / (sum(pB[j] for j in range(h)) * 1e-15 * B_PRES)))
       for h, dw, _, _, _ in rows if h > 1]
sl = sum(x * y for x, y in pts) / sum(x * x for x, _ in pts)
alpha = 1 + sl
predB = [sum(pB[j] for j in range(h)) * 1e-15 * B_PRES * h ** (alpha - 1) * rate60 for h, *_ in rows]
# model C: flat per bit with a free power,  dW = c2 * h^beta
xs = [math.log(h) for h, *_ in rows]; ys = [math.log(dw) for _, dw, *_ in rows]
n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
beta = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
c2 = math.exp(my - beta * mx)
predC = [c2 * h ** beta for h, *_ in rows]

print("\n m    measured   A: flat/bit   B: pos x m^(a-1)   C: c*m^beta")
for i, (h, dw, *_rest) in enumerate(rows):
    print(" %2d   %8.3f   %8.3f      %8.3f           %8.3f" % (h, dw, predA[i], predB[i], predC[i]))


def err(p):
    rel = [(q - dw) / dw for q, (h, dw, *_r) in zip(p, rows)]
    return math.sqrt(sum(e * e for e in rel) / len(rel)) * 100, max(abs(e) for e in rel) * 100


for nm, p, extra in (("A  flat per flipped bit, %.1f fJ" % c, predA, ""),
                     ("B  position-weighted x m^(a-1), a=%.3f" % alpha, predB, ""),
                     ("C  c*m^beta, c=%.3f W beta=%.3f" % (c2, beta), predC, "")):
    r, m_ = err(p)
    print("  %-46s rms %5.1f%%  worst %5.1f%%" % (nm, r, m_))

# does the flat law predict the random-operand items?
na, nb = E67C["items"]["nrd_a"], E67C["items"]["nrd_b"]
print("\nflat law carried to random operands (B side, same stimulus family):")
pred_nrd_b = c * sum(nb["B_hist"]) * 1e-15 * nb["rate_ops_s"]
print("  nrd_b  flat %.1f fJ x %d flips x rate = %.3f W   measured %.3f W   pred/meas %.2f"
      % (c, sum(nb["B_hist"]), pred_nrd_b, nb["measured_W"], pred_nrd_b / nb["measured_W"]))
# A side has no multi-bit ladder of its own; use the A/B single-bit price ratio to transfer
ratio_AB = sum(pA[j] for j in range(32)) / sum(pB[j] for j in range(32))
cA = c * ratio_AB
pred_nrd_a = cA * sum(na["A_hist"]) * 1e-15 * na["rate_ops_s"]
print("  nrd_a  A side has no ladder; scale the flat price by the A/B single-bit ratio %.2f -> %.1f fJ"
      % (ratio_AB, cA))
print("         %.3f W   measured %.3f W   pred/meas %.2f" % (pred_nrd_a, na["measured_W"], pred_nrd_a / na["measured_W"]))
kap = 0.8809539603800310
both = kap * (pred_nrd_a + pred_nrd_b)
meas_both = 16.184565813207264
print("  both random  %.3f x (%.3f + %.3f) = %.3f W   measured %.3f W   pred/meas %.2f"
      % (kap, pred_nrd_a, pred_nrd_b, both, meas_both, both / meas_both))
json.dump({"flat_fJ_per_bit_B": c, "flat_fJ_per_bit_A_scaled": cA, "A_over_B_single_bit_ratio": ratio_AB,
           "alpha": alpha, "beta": beta, "c2_W": c2,
           "rms_pct": {"flat": err(predA)[0], "pos_compressed": err(predB)[0], "power": err(predC)[0]},
           "worst_pct": {"flat": err(predA)[1], "pos_compressed": err(predB)[1], "power": err(predC)[1]},
           "rungs": [{"m": h, "dW": dw, "se": se, "meas_fJ_per_bit": m_, "naive_fJ_per_bit": n_,
                      "pred_flat_W": predA[i], "pred_pos_W": predB[i], "pred_power_W": predC[i]}
                     for i, (h, dw, se, m_, n_) in enumerate(rows)],
           "nrd": {"nrd_b_pred_W": pred_nrd_b, "nrd_b_meas_W": nb["measured_W"],
                   "nrd_a_pred_W": pred_nrd_a, "nrd_a_meas_W": na["measured_W"],
                   "both_pred_W": both, "both_meas_W": meas_both}},
          open(sys.argv[2] + "/models.json", "w"), indent=1)
