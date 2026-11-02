#!/usr/bin/env python3
"""E127, post hoc and labelled (never a verdict): every number the README's post-hoc section quotes, from committed files.

    python3 docs/reports/data/2026-11-02-e127-b-gate/posthoc_e127.py > docs/reports/data/2026-11-02-e127-b-gate/posthoc_e127.txt

1. The miss split in two, at both data regimes. By construction Q1 = Q2 + Q3 and B1 = B3 - B2, for the measurement and for
   M5 alike, so their excesses add exactly; what is informative is that each part reads the same with the data still and
   with random data: the per-lane part (each lane's gate flipping, four live lanes in every micro-op: Q2 quiet, B3 random,
   F3 fp16 quiet) and the all-off part (micro-ops whose eight lanes are all off: Q3 quiet, -B2 random).
2. The per-lane part per gate flip: excess / (4,096 flips an op x the op rate), the op rate fit_m5's RATE (600 MHz / 546
   cycles x 1,024 minions x 0.9963 duty), so fJ per lane-gate flip beyond what M5 prices.
3. q_blk: its excess against the all-off part, and what the per-flip price would give at its 128 flips an op.
4. Where the per-tile miss sits: the quiet tiles against the random ones, D - M5 per tile.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sc = json.load(open(os.path.join(HERE, "scored.json")))["primary"]
C, T = sc["contrasts"], sc["table"]
RATE = 600e6 / 546 * 1024 * 0.9963          # ops a second, chip-wide (fit_m5.RATE["fp32"]; fp16 the same)
FLIPS = 4096                                 # gate flips an op in q_alt, q_chk, g_blanes_alt, g_blanes_chk (e127-tiles.json)


def c(k):
    return next(v for n, v in C.items() if n.startswith(k + ":"))


def line(name, x, lo, hi, unit="W"):
    print(f"  {name:58s} {x:+.3f} [{lo:+.3f}, {hi:+.3f}] {unit}")


print("1. The miss in two parts (excess = measured contrast - M5's frozen point; 95% over the five kept passes)")
for k, what in (("Q1", "quiet: all-off/all-live flipping vs steady (the whole miss)"), ("Q2", "quiet: per-lane flipping, 4 live a micro-op, vs steady"),
                ("Q3", "quiet: all-off/all-live vs 4 live a micro-op (equal flips)"), ("B1", "random: the whole miss (E115's pair)"),
                ("B3", "random: per-lane flipping, 4 live a micro-op, vs steady"), ("B2", "random: 4 live a micro-op vs all-off/all-live (equal bus)"),
                ("F1", "fp16 random: the whole miss"), ("F2", "fp16 quiet: the whole miss"), ("F3", "fp16 quiet: per-lane flipping vs steady")):
    v = c(k)
    line(f"{k} {what}", v["excess_w"], v["excess_lo95"], v["excess_hi95"])
q1, q2, q3, b1, b2, b3 = (c(k) for k in ("Q1", "Q2", "Q3", "B1", "B2", "B3"))
print(f"  identity checks: e(Q2) + e(Q3) - e(Q1) = {q2['excess_w'] + q3['excess_w'] - q1['excess_w']:+.2e} W; "
      f"e(B3) - e(B2) - e(B1) = {b3['excess_w'] - b2['excess_w'] - b1['excess_w']:+.2e} W")
print(f"  per-lane share of the whole miss: quiet {q2['excess_w'] / q1['excess_w']:.3f}, random {b3['excess_w'] / b1['excess_w']:.3f}")
print(f"  all-off part: quiet e(Q3) {q3['excess_w']:+.3f} W, random -e(B2) {-b2['excess_w']:+.3f} W")
print(f"  the all-off micro-ops' saving the card takes, measured / M5: quiet Q3 {q3['measured_w']:+.3f} / {q3['M5_w']:+.3f} = "
      f"{q3['measured_w'] / q3['M5_w']:.2f}; random B2 (sign reversed) {-b2['measured_w']:+.3f} / {-b2['M5_w']:+.3f} = {b2['measured_w'] / b2['M5_w']:.2f}")
print("\n2. The per-lane part per gate flip (fJ beyond M5's price; 4,096 flips an op; op rate %.4e /s)" % RATE)
for k in ("Q2", "B3", "F3"):
    v = c(k)
    f = lambda w: w / (FLIPS * RATE) * 1e15
    line(f"{k}", f(v["excess_w"]), f(v["excess_lo95"]), f(v["excess_hi95"]), "fJ per flip")
print("\n3. q_blk (128 flips an op, off and on in 32-cycle stretches)")
q4 = c("Q4")
line("e(Q4)", q4["excess_w"], q4["excess_lo95"], q4["excess_hi95"])
per_flip = q2["excess_w"] / FLIPS
print(f"  the per-lane price at 128 flips an op: {per_flip * 128:+.3f} W; e(Q4) - e(Q3) = {q4['excess_w'] - q3['excess_w']:+.3f} W "
      f"(the two contrasts share no tile pair, so their difference's interval is about sqrt(h4^2 + h3^2) = "
      f"{math.sqrt(q4['ci95_w'] ** 2 + q3['ci95_w'] ** 2):.3f} W)")
print("\n4. Where the per-tile miss sits (D - M5, W; M5's 95% half-width beside)")
for n in ("fp32.q_steady", "fp32.q_steady_hi", "fp32.q_blk", "fp32.q_chk", "fp32.q_alt", "fp16.q_steady", "fp16.q_chk", "fp16.q_alt",
          "fp32.g_blanes_steady", "fp32.g_blanes_chk", "fp32.g_blanes_alt", "fp16.g_blanes_steady", "fp16.g_blanes_alt"):
    r = T[n]
    print(f"  {n:22s} D {r['D']:6.3f}  M5 {r['M5']:6.3f}  D-M5 {r['err_M5']:+.3f}  (M5 +-{(r['hi95'] - r['lo95']) / 2:.2f}; {'inside' if r['inside_M5'] else 'OUTSIDE'})")
