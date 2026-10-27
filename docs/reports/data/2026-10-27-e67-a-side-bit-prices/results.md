Card aifoundry3, 600 MHz, 521.9 mV. Passes kept [750, 751, 752, 753, 755, 756, 757, 770, 774, 775]; runs kept 424 of 554; leakage 0.175 W/°C (547 runs). Passes set aside: [{'pass': 754, 'failed_runs': 0, 'pi_drift_W': -0.47845454545453947}, {'pass': 771, 'failed_runs': 0, 'pi_drift_W': 0.5813636363636334}, {'pass': 772, 'failed_runs': 0, 'pi_drift_W': -0.32581818181818534}, {'pass': 773, 'failed_runs': 0, 'pi_drift_W': 0.9810454545454661}].

### Block 1 — the A side at all 32 positions (B = 1.0)

| bit | field | ΔW above the constant-A zero | SE (W) | fJ per flipped A bit | E65's B side (fJ) | A / B |
|---|---|---|---|---|---|---|
| 0 | mantissa | 0.459 | 0.241 | 203 ± 107 | 136 | 1.49 |
| 1 | mantissa | 1.140 | 0.240 | 503 ± 106 | 112 | 4.51 |
| 2 | mantissa | 0.473 | 0.201 | 209 ± 89 | 88 | 2.37 |
| 3 | mantissa | 1.078 | 0.182 | 476 ± 81 | 105 | 4.54 |
| 4 | mantissa | 0.346 | 0.237 | 153 ± 104 | 105 | 1.45 |
| 5 | mantissa | 0.713 | 0.082 | 314 ± 36 | 100 | 3.13 |
| 6 | mantissa | 0.990 | 0.224 | 437 ± 99 | 83 | 5.27 |
| 7 | mantissa | 0.584 | 0.221 | 257 ± 97 | 116 | 2.20 |
| 8 | mantissa | 0.376 | 0.172 | 167 ± 76 | 114 | 1.46 |
| 9 | mantissa | 0.754 | 0.382 | 333 ± 168 | 132 | 2.52 |
| 10 | mantissa | 0.851 | 0.272 | 375 ± 120 | 210 | 1.78 |
| 11 | mantissa | 1.259 | 0.229 | 558 ± 102 | 239 | 2.33 |
| 12 | mantissa | 0.970 | 0.179 | 429 ± 79 | 341 | 1.26 |
| 13 | mantissa | 2.003 | 0.173 | 883 ± 76 | 387 | 2.28 |
| 14 | mantissa | 1.471 | 0.287 | 648 ± 126 | 470 | 1.38 |
| 15 | mantissa | 2.444 | 0.263 | 1079 ± 116 | 554 | 1.95 |
| 16 | mantissa | 1.880 | 0.252 | 834 ± 112 | 609 | 1.37 |
| 17 | mantissa | 1.504 | 0.313 | 663 ± 138 | 618 | 1.07 |
| 18 | mantissa | 2.481 | 0.389 | 1100 ± 172 | 687 | 1.60 |
| 19 | mantissa | 2.669 | 0.240 | 1178 ± 106 | 809 | 1.45 |
| 20 | mantissa | 2.516 | 0.266 | 1116 ± 118 | 865 | 1.29 |
| 21 | mantissa | 2.629 | 0.243 | 1162 ± 107 | 906 | 1.28 |
| 22 | mantissa | 3.259 | 0.168 | 1440 ± 74 | 1008 | 1.43 |
| 23 | exponent | 0.637 | 0.146 | 281 ± 65 | 173 | 1.62 |
| 24 | exponent | 0.611 | 0.217 | 270 ± 96 | 173 | 1.56 |
| 25 | exponent | 0.359 | 0.345 | 158 ± 152 | 149 | 1.06 |
| 26 | exponent | 0.662 | 0.160 | 291 ± 70 | 189 | 1.54 |
| 27 | exponent | 0.531 | 0.310 | 235 ± 137 | 111 | 2.12 |
| 28 | exponent | 0.730 | 0.176 | 322 ± 78 | 207 | 1.55 |
| 29 | exponent | 0.874 | 0.181 | 386 ± 80 | 231 | 1.67 |
| 30 | exponent | 0.403 | 0.064 | 178 ± 28 | 161 | 1.11 |
| 31 | sign | 0.561 | 0.182 | 247 ± 80 | 123 | 2.02 |

Mantissa Spearman ρ(bit, price) = **0.851**; span over the 32 positions whose price clears its own SE **9.4×** (153 fJ at bit 4, 1440 fJ at bit 22). Exponent mean 265 fJ, low-mantissa (0–15) mean 439 fJ, sign bit 247 fJ. Four cheapest positions: [4, 25, 8, 30].

A-side against E65's B side over the 23 mantissa positions: Spearman ρ = **0.833**, with **19 of 23** inside the registered [1/3, 3] band. Over all 32 shared positions the A/B ratio runs 1.06–5.27, median 1.60.

**Marginal prices** (post hoc, amendment A14): every per-position price is `e + T/(n·rate)`, and the A side's n is 2,048 against the B side's 4,096, so one fixed turn-on inflates an A-side price twice as much per bit. With **T = 1.351 W** from the grid, that is 597 fJ on every A price and 298 fJ on every B one. Taking it out, the A/B ratio over the mantissa has median **0.93** against the raw 1.60; 22 A and 21 B positions go negative once T is removed, which bounds T rather than pricing those positions.

### Block 2 — the busy partner (B = π)

| A bit | ΔW above `ap_h0` | SE (W) | fJ per flipped A bit | quiet partner (fJ) | busy − quiet (W) | SE | E65's B side with A = π (fJ) |
|---|---|---|---|---|---|---|---|
| 0 | 0.810 | 0.166 | 359 ± 74 | 203 | 0.351 | 0.340 | 445 |
| 8 | 1.122 | 0.269 | 493 ± 118 | 167 | 0.747 | 0.377 | 540 |
| 11 | 1.941 | 0.236 | 856 ± 104 | 558 | 0.681 | 0.437 | 745 |
| 16 | 2.622 | 0.223 | 1160 ± 98 | 834 | 0.742 | 0.453 | 1244 |
| 22 | 3.542 | 0.313 | 1566 ± 139 | 1440 | 0.283 | 0.452 | 1604 |

`abp_11`, the A-side mirror of the flow-M case: **856 ± 104 fJ** per flipped A bit, against E65's `bpi_11` (B bit 11 with A = π) at 745 ± 56 fJ — a ratio of **1.15**.

### Block 3 — the interaction grid: two flips at once against the sum of each alone

Base `ix_z` (both operands constant): 36.19 W. Margins, each against that base:

| margin | side | bit | ΔW | fJ per flipped bit |
|---|---|---|---|---|
| `ix_a0` | A | 0 | 0.918 | 412 |
| `ix_a8` | A | 8 | 1.220 | 549 |
| `ix_a16` | A | 16 | 2.369 | 1069 |
| `ix_a22` | A | 22 | 3.895 | 1734 |
| `ix_b0` | B | 0 | 2.197 | 495 |
| `ix_b8` | B | 8 | 2.666 | 600 |
| `ix_b16` | B | 16 | 5.352 | 1197 |
| `ix_b22` | B | 22 | 6.800 | 1541 |

| A bit \ B bit | 0 | 8 | 16 | 22 |
|---|---|---|---|---|
| **0** | 2.61 / 3.12 (-0.50) | 2.79 / 3.58 (-0.80) | 5.97 / 6.27 (-0.30) | 6.39 / 7.72 (-1.33) |
| **8** | 2.13 / 3.42 (-1.29) | 3.11 / 3.89 (-0.78) | 6.12 / 6.57 (-0.45) | 7.24 / 8.02 (-0.78) |
| **16** | 4.39 / 4.57 (-0.17) | 4.20 / 5.04 (-0.84) | 5.09 / 7.72 (-2.63) | 7.12 / 9.17 (-2.05) |
| **22** | 4.68 / 6.09 (-1.42) | 5.70 / 6.56 (-0.86) | 5.88 / 9.25 (-3.37) | 6.64 / 10.69 (-4.05) |

*cell ΔW / sum of its two margins (excess).* Mean excess over the 16 cells **-1.351 ± 0.281 W**, largest |excess| 4.051 W, mean excess as a fraction of the cell's sum -20.1%.

### Block 4 — the anchors on this card and pass set

| item | what it runs | board W | SE | ΔW above its zero | A bits/op | B bits/op |
|---|---|---|---|---|---|---|
| `anchor_zeros` | both operands zero | 27.83 | 0.04 | — | 0 | 0 |
| `anchor_ones` | both operands 1.0 | 36.05 | 0.14 | — | 0 | 0 |
| `anchor_pi` | both operands π | 36.32 | 0.10 | — | 0 | 0 |
| `anchor_randn` | both operands random fp32 (kernel-generated) | 52.49 | 0.36 | — | 0 | 0 |
| `nrd_a` | A random fp32, B = 1.0 | 43.56 | 0.13 | +7.48 | 27648 | 0 |
| `nrd_b` | A = 1.0, B random fp32 | 47.39 | 0.02 | +10.89 | 0 | 56784 |
| `lq_h0` | A = 1.0, B constant (E65's quiet zero) | 36.50 | 0.01 | — | 0 | 0 |
| `lb_h0` | A = π, B constant (E65's busy zero) | 36.07 | 0.30 | — | 0 | 0 |
| `aq_h0` | A constant, B = 1.0 (the A scan's zero) | 36.07 | 0.24 | — | 0 | 0 |
| `aq_e64` | A constant (exp 64), B = 1.0 | 36.42 | 0.03 | — | 0 | 0 |
| `ap_h0` | A constant, B = π | 36.31 | 0.15 | — | 0 | 0 |
| `ix_z` | the grid's base, both constant | 36.19 | 0.34 | — | 0 | 0 |

**The tie to E65**, the items both experiments ran on this card — this is what lets the two price lists be added without a conversion:

| item | E65 (W) | E67 (W) | difference |
|---|---|---|---|
| `anchor_pi` | 36.39 | 36.32 | -0.06 |
| `lq_h0` | 36.49 | 36.50 | +0.01 |
| `lb_h0` | 36.47 | 36.07 | -0.40 |

Largest disagreement 0.40 W over 3 shared items.


d(`nrd_a`) / d(`nrd_b`) = **0.687**, against the designed-bit ratio 27,648 / 56,784 = 0.487.

Random against zeros on this card at 600 MHz: **24.66 W** (27.83 → 52.49 W).

**Additivity at the whole-operand level** (beside the grid's per-bit additivity): both operands random is **16.18 W** above the constant-operand level, where one random side plus the other sums to **18.37 W** — a ratio of **0.88**. The 6 constant-operand items (`anchor_pi`, `lq_h0`, `aq_h0`, `aq_e64`, `ap_h0`, `ix_z`: the same state by six routes) span 0.42 W, which is this comparison's own noise floor.

### The closure test — do the summed per-position prices reproduce a random-data step?

| item | designed flips per multiply-add | predicted from the price lists | measured | measured / predicted | turn-on corrected | ratio |
|---|---|---|---|---|---|---|
| `nrd_a` | 27648 A + 0 B | 17.30 W | 7.48 ± 0.23 W | **0.43** | 0.41 W | **18.37** |
| `nrd_b` | 0 A + 56784 B | 21.85 W | 10.89 ± 0.02 W | **0.50** | 4.47 W | **2.44** |

*Turn-on corrected* (post hoc, amendment A13, not a registered prediction): a price measured against a constant-operand zero is `T + e·n·rate`, so summing it over a random workload charges the fixed turn-on `T` once per flipped position — 13.5 times for `nrd_a`. Taking **T = 1.351 W** (minus the grid's mean interaction excess) out of every price and adding it back once gives the right-hand columns.


The both-sides anchor: `anchor_randn` − `anchor_zeros` = **24.66 W**. Its operands are made by the kernel, not read from a file, so its flip histogram cannot be counted; the nearest counted stimulus is `nrd_a` + `nrd_b` (one random side each), whose price-list prediction sums to 39.14 W — a stand-in, not the same workload, ratio 0.63.

### The registered rules, scored

| rule | what it asked | measured | verdict |
|---|---|---|---|
| **P1** | the A scan rises with the bit (mantissa ρ > 0.5) and spans > 5× | ρ = 0.851, span 9.4× | **PASS** |
| **P2** | A within a factor of 3 of E65's B at most shared positions, and ρ > 0.5 | ρ = 0.833, 19/23 in band, median ratio 1.60 | **PASS** |
| **P3** | the sign bit among the four cheapest; exponent dearer than mantissa 0–15 | sign bit ranks 8/32 (not in the cheapest four); exponent mean 265 fJ vs low-mantissa 439 fJ, 92 mantissa-below-16 bits at or above an exponent bit | **FAIL** |
| **P4** | busy − quiet > 0 everywhere, at ≥ 2 SE for ≥ 3 of 5 | 5/5 positive, 0/5 at ≥ 2 SE | **FAIL** |
| **P5** | `abp_11` within a factor of 3 of E65's `bpi_11` (745 fJ) | 856 fJ, ratio 1.15 | **PASS** |
| **P6** | every cell's excess within ±0.5 W, mean within ±0.3 W, ≥ 12 of 16 within 20% | mean excess -1.351 ± 0.281 W, |max| 4.051 W, 8/16 within 20% | **FAIL (sub-additive)** |
| **P7** | d(nrd_a)/d(nrd_b) in [0.3, 0.8] | 0.687 | **PASS** |
| **P8** | the summed price lists predict both one-sided steps within a factor of 2 | ratios 0.43, 0.50 (turn-on corrected 18.37, 2.44) | **FAIL** |
