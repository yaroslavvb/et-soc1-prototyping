Card aifoundry3, 600 MHz, 521.8 mV. Passes kept [750, 751, 752, 753, 770, 774, 775]; runs kept 277 of 277; leakage 0.168 W/°C (272 runs). Passes set aside: none.

### Block 1 — the A side at all 32 positions (B = 1.0)

| bit | field | ΔW above the constant-A zero | SE (W) | fJ per flipped A bit | E65's B side (fJ) | A / B |
|---|---|---|---|---|---|---|
| 0 | mantissa | 0.325 | 0.030 | 141 ± 13 | 136 | 1.04 |
| 1 | mantissa | 0.781 | 0.018 | 340 ± 8 | 112 | 3.05 |
| 2 | mantissa | 0.394 | 0.009 | 172 ± 4 | 88 | 1.94 |
| 3 | mantissa | 0.799 | 0.015 | 348 ± 6 | 105 | 3.32 |
| 4 | mantissa | 0.298 | 0.012 | 130 ± 5 | 105 | 1.23 |
| 5 | mantissa | 0.648 | 0.074 | 282 ± 32 | 100 | 2.81 |
| 6 | mantissa | 0.658 | 0.008 | 287 ± 3 | 83 | 3.46 |
| 7 | mantissa | 0.313 | 0.015 | 136 ± 7 | 116 | 1.17 |
| 8 | mantissa | 0.199 | 0.098 | 87 ± 43 | 114 | 0.76 |
| 9 | mantissa | 0.605 | 0.003 | 264 ± 1 | 132 | 2.00 |
| 10 | mantissa | 0.469 | 0.130 | 204 ± 57 | 210 | 0.97 |
| 11 | mantissa | 0.975 | 0.047 | 425 ± 20 | 239 | 1.78 |
| 12 | mantissa | 0.727 | 0.122 | 317 ± 53 | 341 | 0.93 |
| 13 | mantissa | 1.748 | 0.015 | 762 ± 7 | 387 | 1.97 |
| 14 | mantissa | 1.037 | 0.201 | 452 ± 87 | 470 | 0.96 |
| 15 | mantissa | 2.030 | 0.066 | 885 ± 29 | 554 | 1.60 |
| 16 | mantissa | 1.941 | 0.007 | 846 ± 3 | 609 | 1.39 |
| 17 | mantissa | 1.490 | 0.015 | 649 ± 7 | 618 | 1.05 |
| 18 | mantissa | 2.587 | 0.027 | 1127 ± 12 | 687 | 1.64 |
| 19 | mantissa | 2.310 | 0.029 | 1006 ± 13 | 809 | 1.24 |
| 20 | mantissa | 2.270 | 0.121 | 988 ± 53 | 865 | 1.14 |
| 21 | mantissa | 2.259 | 0.018 | 984 ± 8 | 906 | 1.09 |
| 22 | mantissa | 3.030 | 0.125 | 1320 ± 54 | 1008 | 1.31 |
| 23 | exponent | 0.438 | 0.018 | 191 ± 8 | 173 | 1.10 |
| 24 | exponent | 0.433 | 0.013 | 189 ± 6 | 173 | 1.09 |
| 25 | exponent | 0.377 | 0.008 | 164 ± 4 | 149 | 1.10 |
| 26 | exponent | 0.469 | 0.021 | 204 ± 9 | 189 | 1.08 |
| 27 | exponent | 0.317 | 0.017 | 138 ± 8 | 111 | 1.24 |
| 28 | exponent | 0.594 | 0.019 | 259 ± 8 | 207 | 1.25 |
| 29 | exponent | 0.608 | 0.018 | 265 ± 8 | 231 | 1.15 |
| 30 | exponent | 0.477 | 0.056 | 208 ± 24 | 161 | 1.29 |
| 31 | sign | 0.297 | 0.009 | 129 ± 4 | 123 | 1.06 |

Mantissa Spearman ρ(bit, price) = **0.829**; span over the 32 positions whose price clears its own SE **15.2×** (87 fJ at bit 8, 1320 fJ at bit 22). Exponent mean 202 fJ, low-mantissa (0–15) mean 327 fJ, sign bit 129 fJ. Four cheapest positions: [8, 31, 4, 7].

A-side against E65's B side over the 23 mantissa positions: Spearman ρ = **0.817**, with **20 of 23** inside the registered [1/3, 3] band. Over all 32 shared positions the A/B ratio runs 0.76–3.46, median 1.24.

**Marginal prices** (post hoc, amendment A14): every per-position price is `e + T/(n·rate)`, and the A side's n is 2,048 against the B side's 4,096, so one fixed turn-on inflates an A-side price twice as much per bit. With **T = 1.353 W** from the grid, that is 589 fJ on every A price and 294 fJ on every B one. Taking it out, the A/B ratio over the mantissa has median **0.81** against the raw 1.31; 23 A and 21 B positions go negative once T is removed, which bounds T rather than pricing those positions.

### Block 2 — the busy partner (B = π)

| A bit | ΔW above `ap_h0` | SE (W) | fJ per flipped A bit | quiet partner (fJ) | busy − quiet (W) | SE | E65's B side with A = π (fJ) |
|---|---|---|---|---|---|---|---|
| 0 | 1.081 | 0.032 | 471 ± 14 | 141 | 0.756 | 0.048 | 445 |
| 8 | 1.242 | 0.109 | 541 ± 48 | 87 | 1.043 | 0.139 | 540 |
| 11 | 2.230 | 0.045 | 971 ± 19 | 425 | 1.254 | 0.090 | 745 |
| 16 | 2.499 | 0.197 | 1089 ± 86 | 846 | 0.558 | 0.191 | 1244 |
| 22 | 3.747 | 0.057 | 1632 ± 25 | 1320 | 0.718 | 0.150 | 1604 |

`abp_11`, the A-side mirror of the flow-M case: **971 ± 19 fJ** per flipped A bit, against E65's `bpi_11` (B bit 11 with A = π) at 745 ± 56 fJ — a ratio of **1.30**.

### Block 3 — the interaction grid: two flips at once against the sum of each alone

Base `ix_z` (both operands constant): 36.20 W. Margins, each against that base:

| margin | side | bit | ΔW | fJ per flipped bit |
|---|---|---|---|---|
| `ix_a0` | A | 0 | 0.919 | 413 |
| `ix_a8` | A | 8 | 1.221 | 550 |
| `ix_a16` | A | 16 | 2.372 | 1071 |
| `ix_a22` | A | 22 | 3.898 | 1736 |
| `ix_b0` | B | 0 | 2.199 | 495 |
| `ix_b8` | B | 8 | 2.668 | 601 |
| `ix_b16` | B | 16 | 5.356 | 1198 |
| `ix_b22` | B | 22 | 6.804 | 1541 |

| A bit \ B bit | 0 | 8 | 16 | 22 |
|---|---|---|---|---|
| **0** | 2.62 / 3.12 (-0.50) | 2.79 / 3.59 (-0.80) | 5.97 / 6.28 (-0.30) | 6.40 / 7.72 (-1.33) |
| **8** | 2.13 / 3.42 (-1.29) | 3.11 / 3.89 (-0.78) | 6.12 / 6.58 (-0.45) | 7.24 / 8.03 (-0.78) |
| **16** | 4.40 / 4.57 (-0.18) | 4.20 / 5.04 (-0.84) | 5.09 / 7.73 (-2.63) | 7.12 / 9.18 (-2.05) |
| **22** | 4.68 / 6.10 (-1.42) | 5.71 / 6.57 (-0.86) | 5.88 / 9.25 (-3.37) | 6.65 / 10.70 (-4.05) |

*cell ΔW / sum of its two margins (excess).* Mean excess over the 16 cells **-1.353 ± 0.281 W**, largest |excess| 4.053 W, mean excess as a fraction of the cell's sum -20.2%.

### Block 4 — the anchors on this card and pass set

| item | what it runs | board W | SE | ΔW above its zero | A bits/op | B bits/op |
|---|---|---|---|---|---|---|
| `anchor_zeros` | both operands zero | 27.86 | 0.03 | — | 0 | 0 |
| `anchor_ones` | both operands 1.0 | 36.23 | 0.09 | — | 0 | 0 |
| `anchor_pi` | both operands π | 36.28 | 0.15 | — | 0 | 0 |
| `anchor_randn` | both operands random fp32 (kernel-generated) | 52.88 | 0.06 | — | 0 | 0 |
| `nrd_a` | A random fp32, B = 1.0 | 43.69 | 0.03 | +7.25 | 27648 | 0 |
| `nrd_b` | A = 1.0, B random fp32 | 47.39 | 0.02 | +10.89 | 0 | 56784 |
| `lq_h0` | A = 1.0, B constant (E65's quiet zero) | 36.51 | 0.01 | — | 0 | 0 |
| `lb_h0` | A = π, B constant (E65's busy zero) | 36.60 | 0.01 | — | 0 | 0 |
| `aq_h0` | A constant, B = 1.0 (the A scan's zero) | 36.43 | 0.01 | — | 0 | 0 |
| `aq_e64` | A constant (exp 64), B = 1.0 | 36.41 | 0.05 | — | 0 | 0 |
| `ap_h0` | A constant, B = π | 36.53 | 0.05 | — | 0 | 0 |
| `ix_z` | the grid's base, both constant | 36.20 | 0.34 | — | 0 | 0 |

**The tie to E65**, the items both experiments ran on this card — this is what lets the two price lists be added without a conversion:

| item | E65 (W) | E67 (W) | difference |
|---|---|---|---|
| `anchor_pi` | 36.39 | 36.28 | -0.10 |
| `lq_h0` | 36.49 | 36.51 | +0.01 |
| `lb_h0` | 36.47 | 36.60 | +0.13 |

Largest disagreement 0.13 W over 3 shared items.


d(`nrd_a`) / d(`nrd_b`) = **0.666**, against the designed-bit ratio 27,648 / 56,784 = 0.487.

Random against zeros on this card at 600 MHz: **25.02 W** (27.86 → 52.88 W).

**Additivity at the whole-operand level** (beside the grid's per-bit additivity): both operands random is **16.48 W** above the constant-operand level, where one random side plus the other sums to **18.14 W** — a ratio of **0.91**. The 6 constant-operand items (`anchor_pi`, `lq_h0`, `aq_h0`, `aq_e64`, `ap_h0`, `ix_z`: the same state by six routes) span 0.33 W, which is this comparison's own noise floor.

### The closure test — do the summed per-position prices reproduce a random-data step?

| item | designed flips per multiply-add | predicted from the price lists | measured | measured / predicted | turn-on corrected | ratio |
|---|---|---|---|---|---|---|
| `nrd_a` | 27648 A + 0 B | 14.62 W | 7.25 ± 0.04 W | **0.50** | -2.29 W | **-3.17** |
| `nrd_b` | 0 A + 56784 B | 22.10 W | 10.89 ± 0.04 W | **0.49** | 4.70 W | **2.31** |

*Turn-on corrected* (post hoc, amendment A13, not a registered prediction): a price measured against a constant-operand zero is `T + e·n·rate`, so summing it over a random workload charges the fixed turn-on `T` once per flipped position — 13.5 times for `nrd_a`. Taking **T = 1.353 W** (minus the grid's mean interaction excess) out of every price and adding it back once gives the right-hand columns.


The both-sides anchor: `anchor_randn` − `anchor_zeros` = **25.02 W**. Its operands are made by the kernel, not read from a file, so its flip histogram cannot be counted; the nearest counted stimulus is `nrd_a` + `nrd_b` (one random side each), whose price-list prediction sums to 36.72 W — a stand-in, not the same workload, ratio 0.68.

### The registered rules, scored

| rule | what it asked | measured | verdict |
|---|---|---|---|
| **P1** | the A scan rises with the bit (mantissa ρ > 0.5) and spans > 5× | ρ = 0.829, span 15.2× | **PASS** |
| **P2** | A within a factor of 3 of E65's B at most shared positions, and ρ > 0.5 | ρ = 0.817, 20/23 in band, median ratio 1.24 | **PASS** |
| **P3** | the sign bit among the four cheapest; exponent dearer than mantissa 0–15 | sign bit ranks 2/32 (in the cheapest four); exponent mean 202 fJ vs low-mantissa 327 fJ, 86 mantissa-below-16 bits at or above an exponent bit | **PARTIAL** |
| **P4** | busy − quiet > 0 everywhere, at ≥ 2 SE for ≥ 3 of 5 | 5/5 positive, 5/5 at ≥ 2 SE | **PASS** |
| **P5** | `abp_11` within a factor of 3 of E65's `bpi_11` (745 fJ) | 971 fJ, ratio 1.30 | **PASS** |
| **P6** | every cell's excess within ±0.5 W, mean within ±0.3 W, ≥ 12 of 16 within 20% | mean excess -1.353 ± 0.281 W, |max| 4.053 W, 8/16 within 20% | **FAIL (sub-additive)** |
| **P7** | d(nrd_a)/d(nrd_b) in [0.3, 0.8] | 0.666 | **PASS** |
| **P8** | the summed price lists predict both one-sided steps within a factor of 2 | ratios 0.50, 0.49 (turn-on corrected -3.17, 2.31) | **FAIL** |
