# Blind pool 3: the contrasts' 95% intervals (Q133(b), a dated addendum for E115)

Written by `docs/reports/data/2026-11-01-q133b-power-model/contrasts_blind3.py` on Sun 1 Nov 2026, after verification: after `predictions-blind3.json` was frozen (`64b4124e`) and before any card ran a pool tile. D in W over the type's own zeros at 600 MHz. Each point is the difference of the two tiles' frozen predictions. On a3 and c1 each interval is the two tiles' frozen 95% half-widths in quadrature (the errors treated as independent). On a new card it is a3's interval widened by one card's step on the contrast, t × |1 − s| × D, the rule the tiles' own `new` footing uses; the two tiles' `new` half-widths in quadrature, which count the step on each tile's whole D, are in `contrasts-blind3.json` as the most conservative figure. The last column is a check, not the interval: the tiles' own formula on the difference, with the constants' share cancelling.

| contrast | what it isolates | **M5, a3 [95%]** | M5, c1 [95%] | M5, new card [95%] | M4, a3 [95%] | M5 a3 ± if constants shared |
|---|---|---:|---:|---:|---:|---:|
| `fp32.g_blanes_alt - fp32.g_blanes_steady` | gate switching every cycle against a steady gate, same gated fraction | **+0.78** [+0.23, +1.34] | +0.76 [+0.09, +1.43] | +0.78 [+0.23, +1.34] | +0.73 [+0.21, +1.24] | ±0.55 |
| `fp32.a_lo8_b_randn - fp32.a_lo8_b_pi` | the same A side with a busy and a quiet partner | **+11.55** [+10.97, +12.12] | +11.21 [+10.52, +11.90] | +11.55 [+10.67, +12.42] | +11.36 [+10.80, +11.92] | ±0.57 |
| `fp32.m_blines_eq - fp32.m_bpair_eq` | B alternating in-lane with no line changes, against lines changing with no in-lane alternation | **+8.38** [+7.82, +8.94] | +8.14 [+7.46, +8.82] | +8.38 [+7.64, +9.12] | +8.31 [+7.76, +8.86] | ±0.54 |
| `fp32.s_drift12 - fp32.s_pair0` | a sum that drifts up against one that returns to 0 | **+0.06** [-0.50, +0.63] | +0.06 [-0.63, +0.75] | +0.06 [-0.50, +0.63] | +0.08 [-0.48, +0.65] | ±0.54 |
| `fp32.s_bridge - fp32.s_pair0` | a sum that climbs and walks back against one that returns every step | **+0.68** [+0.12, +1.24] | +0.66 [-0.02, +1.34] | +0.68 [+0.12, +1.24] | +0.65 [+0.11, +1.19] | ±0.53 |
| `fp32.x_logu_s50 - fp32.x_logu_bsteady` | exponents spread: a random 50% word gate against a steady lane gate | **-5.61** [-6.16, -5.06] | -5.45 [-6.12, -4.78] | -5.61 [-6.25, -4.97] | -5.62 [-6.12, -5.12] | ±0.55 |
| `fp16.s_wpair0 - fp16.s_inword0` | fp16: cancelling across k-groups against inside the two-term update | **+4.76** [+4.26, +5.26] | +4.62 [+4.04, +5.21] | +4.76 [+4.19, +5.33] | +4.68 [+4.15, +5.20] | ±0.49 |

**Each contrast split by M5's terms** (W, a3):

| contrast | mult | add32 | add16 | bus | rest | clk |
|---|---:|---:|---:|---:|---:|---:|
| `fp32.g_blanes_alt - fp32.g_blanes_steady` | +0.27 | -0.00 | +0.00 | +0.69 | +0.68 | -0.86 |
| `fp32.a_lo8_b_randn - fp32.a_lo8_b_pi` | +2.76 | +3.79 | +0.00 | +1.06 | +3.94 | +0.00 |
| `fp32.m_blines_eq - fp32.m_bpair_eq` | +2.99 | +2.05 | +0.00 | +0.74 | +2.61 | +0.00 |
| `fp32.s_drift12 - fp32.s_pair0` | +0.03 | +0.33 | +0.00 | -0.04 | -0.26 | +0.00 |
| `fp32.s_bridge - fp32.s_pair0` | -0.05 | +0.34 | +0.00 | -0.01 | +0.41 | +0.00 |
| `fp32.x_logu_s50 - fp32.x_logu_bsteady` | -1.52 | -1.01 | +0.00 | +0.42 | -1.10 | -2.40 |
| `fp16.s_wpair0 - fp16.s_inword0` | +0.15 | +0.00 | +1.53 | +0.33 | +2.75 | +0.00 |

**The memory-path pair, by what a path would carry** (bits an op, `make_kinds.tile_stats` in `blind3.json`): B line to line 0 (`m_blines_eq`) against 3,552 (`m_bpair_eq`); B half-line to half-line 3,680 against 1,776; A line to line 3,504 against 3,530. The bench has no memory path, so its +8.38 W is all compute and the operand bus. A card reading below the interval would fit a cost for B lines that change (only `m_bpair_eq`'s do), one above it a cost for half-lines that change (`m_blines_eq`'s change about twice as often); either could instead be compute the bench misprices.
