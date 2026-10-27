# E67 — the A side of the price list, the busy partner, and the interaction grid (Q128, aifoundry3, 2026-10-26/27)

*Pre-registered in [`tools/claims-v3/ha/README.md`](../../../tools/claims-v3/ha/README.md) (blocks 1–4, departures
D1–D4, predictions P1–P8, decision rules, amendments A11 and A12 with the registration and A13 after pass 750 and
before block 3's data), committed as `2e9ad85a` at **21:01:37 PDT — 2 min 32 s before the card was claimed and
3 min 51 s before the first measured launch**, with A13 as `ee9faed6` at 21:15:43, after block 1's first pass and
before any block-3 data. Card runs 2026-10-26 from 21:04 PDT on **aifoundry3 only**, whose governor is latched
at 600 MHz by `et-board-clock-guard`, so every number here is a 600 MHz, 521.9 mV number — the same card, clock and
voltage as E65's B-side scan, which is the point. Claimed in `#community-lab` at 21:03 PDT and released after the
last pass.*

## Why it ran

E65 (Q126) priced **one operand side**: all 32 positions of **B** with the quiet partner A = 1.0, and the flow-M
case (B bit 11 against A = π). The **A side had never been priced**, so the chain from "zeros run 15–33% faster
than random fp32" down to a transistor had a per-bit price list covering half the operand bits and assuming the
other half matched. A is the **Booth-recoded** operand — broadcast to all eight lanes, driving the recoder that
*selects* each partial product, where B is per-lane and *feeds* the partial-product muxes. Three holes:

| Block | What it closes | Items |
|---|---|---|
| **1** | the A side at every bit position | `abit_0` … `abit_31`, B = 1.0, each against a shared-base constant-A zero |
| **2** | the A-side mirror of the flow-M case | `abp_0, abp_8, abp_11, abp_16, abp_22`, B = π, against `ap_h0` |
| **3** | two flips at once: do per-bit prices add? | the 4 × 4 grid `ix_<i>_<j>` on one base, with its A-only and B-only margins and that base |
| **4** | the footing for the closure test | `anchor_{zeros,ones,pi,randn}`, `nrd_a` (A random), `nrd_b` (B random), and E65's `lq_h0` / `lb_h0` ties |

## The A side can only flip every second cycle

The issue order (PRM 9.4, `make_hl.py:issue_streams`) is: for each B row k, for each A row i, two micro-ops.
**A[i][k] is held across both**, and B alternates every micro-op. So an A word changes at most every *second*
cycle: 16 transitions per B row × 16 B rows × 8 lanes = **2,048 designed A-bit flips per multiply-add**, exactly
half of B's 4,096. That is the hardware's issue order, not a choice. Every count here is re-derived from the
written operand files by `make_hl.py --check`, and the reduction divides each item by its **own** manifest count,
so the A and B prices are per-flipped-bit numbers on one footing.

## Design tightening over E65

E60 and E65's `bit_<j>` drew a fresh random base word per position, so an item minus its zero carried both the
flip and the difference between two random words. Here **every A-side item shares one base word** and the zero
`aq_h0` is that word held constant, so an item minus its zero differs in bit j alone. Bit 30 is the exponent MSB
and cannot flip from exponent 127 (that is Inf), so it uses the exponent-64 twin of the same mantissa and gets its
own zero, `aq_e64`. This is why the reduction needed a per-item zero (amendment A12); every E60 and E65 item keeps
the family map and their reductions are unchanged.

## Amendments

A11 and A12 ship with the registration. A13 and A14 came after block 1's first pass and **before any block-3
data**, which is the data they touch; both add reported quantities and neither moves a registered band, a line of
the registered analysis, or a measured number.

| | What | Commit |
|---|---|---|
| **A11** | `make_hl.py` gains the seven A-side families (`aq`, `ap`, `abit`, `abp`, `ix`, `nrd`) and a per-item `zero` where the family map cannot name one. Every operand file E60 and E65 ran is byte-identical in `build/hl-gen4` — 87 of 87, checked on the box before the first launch. | `2e9ad85a` |
| **A12** | `reduce_hl.py` gains `item_zero()` (an item's own `zero` wins over the family map, in the cycles-per-op gate and in the item differences) and the `a_bits`, `a_bits_pi`, `a_partner`, `ix` and `anchors` sections. Every E60 and E65 item has no `zero` field and keeps the family map, so their reductions are unchanged. | `2e9ad85a` |
| **A13** | the reduction tools (`collect_e67.sh`, `closure.py`, `report_e67.py`), and a **turn-on-corrected** closure *beside* the registered one: a price measured against a constant-operand zero is `T + e·n·rate`, so summing it over a random workload charges the fixed turn-on once per flipped position instead of once. The grid measures `T` as minus the registered excess. P6 and P8 keep their bands. | `ee9faed6` |
| **A14** | the same argument applied to P2: the A side's `n` is 2,048 against the B side's 4,096, so one turn-on inflates an A-side price **twice as much per bit**, and the raw A/B ratio is biased upward by construction. The marginal ratio is printed beside the raw one. P2 keeps its band and is scored on the raw prices. | `655082c7` |
| — | two scoring corrections in the reporting tool, on pass 750's data and before any block-3 data: P1's span excludes by name a position whose price is not 1 SE above zero (a ratio needs a positive floor), P2's band test runs over the 23 mantissa positions the registration names, and P3 is scored in its two stated halves as E65 scored its own A3. No band moves. | `6dd3fd30`, `657fff18` |

## Files

| File | What |
|---|---|
| `hl.json`, `runs.csv`, `reduce.txt` | `hl/reduce_hl.py` over every pass that finished |
| `closure.json`, `closure.txt` | `ha/closure.py`: the per-position flip histograms of `nrd_a` and `nrd_b`, priced with E67's A list and E65's B list, against their measured steps |
| `results.md`, `scored.json` | `ha/report_e67.py`: the tables below and the scored rules |
| `manifest.json` | the operand set `build/hl-gen4`: every item and its designed flip counts, re-derived from the files |
| `aifoundry3/hl/p75*`, `aifoundry3/hl/p77*` | per pass: `block.json`, `configs.json`, `gen.sha256` (the operand files that ran), `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` |
| `logs/` | the queue and chain logs. `run_e67.sh as` truncates its queue log when the second group starts, so `e67-as-750.log` is the copy taken before that; each pass's own `run.log` and `block.json` are the complete record |

**Operand set and code.** `build/hl-gen4`, generated and `--check`ed on the box before the first launch; **every
one of the 87 operand files E60 and E65 ran is byte-identical in it**, so nothing already measured changes. The
box ran commit `2e9ad85a`'s `make_hl.py` and `reduce_hl.py` for every pass. A sibling job (`94d1df95`, Q128(e))
later added a four-line PEP 723 dependency comment to both files on `main`; it changes no executable line, so the
committed code reproduces this data exactly.

## Results — the registered reduction

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

## Sensitivity — the same analysis over the clean passes only (post hoc, amendment A15)

*Not the registered result. Passes whose constant-operand spread is ≤ 0.40 W: 750–753, 770, 774, 775;
277 of 277 runs kept, no pass set aside. Only P3 and P4 change, both toward the registered expectation.*

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

## Pass health: a diagnostic the registered gates do not have

Every pass runs several items whose operands never change — `aq_h0`, `aq_e64`, `ap_h0`, `lq_h0`, `lb_h0`, `ix_z`
and `anchor_pi` twice. They are one physical state reached by several routes, so within a pass they must read one
power. Their **spread** is therefore an assumption-free measure of the pass's health, and it disagrees sharply
with the registered gate (`ha/constspread.py`, `constspread.txt`):

| pass | constant runs | spread (W) | median (W) | registered `anchor_pi` drift | rate (Gop/s) | registered verdict |
|---|---|---|---|---|---|---|
| 750–753 | 7 each | 0.17–0.37 | 36.44–36.46 | +0.014 … +0.219 | 1.121 | kept |
| 754 | 7 | 0.62 | 36.44 | −0.478 | 1.101 | **set aside** |
| 755 | 7 | **2.02** | 36.43 | −0.007 | 1.085 | kept |
| 756 | 7 | **1.12** | 36.44 | +0.021 | 1.085 | kept |
| 757 | 7 | **0.97** | 36.46 | −0.028 | 1.087 | kept |
| 770, 774, 775 | 3 each | 0.09–0.12 | 35.44–36.45 | −0.055 … +0.039 | 1.086–1.090 | kept |
| 771, 772, 773 | 3 each | 0.43–0.98 | 35.61–36.42 | −0.326 … +0.981 | 1.084–1.091 | **set aside** |

**The registered gate fires on the wrong passes.** It sets aside 754 at a 0.62 W spread and keeps 755 at 2.02 W,
because `anchor_pi`'s own two runs happen to agree there. The cause is visible in the launch records: from pass
754 the host-side launch overhead grew — the calibration launch 18 → 23 ms, the gap between launches 1.5 → 10–15 ms,
the rate 1.121 → 1.085 Gop/s — and a minority of runs then read 1–2 W **low** at an unchanged clock, rail, launch
reading and cycles-per-op, so no per-run gate sees them. The pass median never moves, so the bad runs dip and
never rise.

So the results are given **twice**: the **registered** reduction over every pass the registered gates keep (10 of
14), and a **post-hoc sensitivity** over the passes whose constant-operand spread is ≤ 0.40 W (7 of 14, 277 of 277
runs kept, no pass set aside) — amendment A15, `results-clean.md` and `scored-clean.json`. **The registered one is
the result.** Only two verdicts differ, and both move the registered way: P3 FAIL → PARTIAL and P4 FAIL → PASS.
Every headline — the A side's shape, the busy partner, the sub-additivity and the closure — is the same in both.

## What this changes in the chain

Place in the chain (the Horace question, steps 5 → 6): E64 says zeros beat random fp32 because random data draws
more board power; E60 and E65 priced a flipped **B** bit; this prices a flipped **A** bit, ties the two together,
and tests whether they add.

1. **Half the operand bits now have a price**, measured on the same card, clock and rail as the other half. The
   tie is tight: the three items both experiments ran agree to **0.13 W** (`anchor_pi` 36.39 → 36.28, `lq_h0`
   36.49 → 36.51, `lb_h0` 36.47 → 36.60, four hours apart), so the two lists add with no conversion.
2. **The A side flips at half the rate of the B side**, by the issue order — 2,048 designed transitions per
   multiply-add against 4,096. A Hamming-distance model has to carry that before any price difference.
3. 🛑 **Per-bit prices do not add.** Every one of the 16 grid cells is sub-additive, and not by a constant: the
   excess tracks the size of the flips (Pearson r = **−0.739** against the sum; least squares gives
   `cell = 0.94 W + 0.64 × sum`, residual rms 0.73 W), so a cell costs **62–96% of the sum of its two margins**,
   median 83%. This is **saturation, not a fixed turn-on**: amendment A13's constant-`T` correction is refuted by
   the grid that was meant to measure `T` — taking a constant 1.35 W out of every position over-corrects and
   drives most positions negative (the corrected closure reads −3.17 and 2.31, worse than the raw 0.50 and 0.49).
4. **And the shortfall deepens with how many positions flip at once.** Two positions give a 17% shortfall on
   average; a random operand, which flips about 13.5 positions per multiply-add, gives **2.0–2.3×** — the summed
   price list over-predicts `nrd_a` by 2.3× and `nrd_b` by 2.0×. Scaling by the grid's own pair ratio (0.80) only
   takes that to 1.6–1.8×, so pairwise saturation does not by itself account for the many-flip case.
5. **But the two operand *paths* do add.** At the whole-operand level, both operands random is **16.48 W** above
   the constant-operand level where one random side plus the other sums to **18.14 W** — a ratio of **0.91**
   against a 0.33 W noise floor. So the A and B paths are nearly independent; what fails is the decomposition of
   one operand into independent **bits**.

That is the correction the chain needed. Step 5 → 6 cannot be "multiply a Hamming distance by a per-bit price":
the per-bit price list is an upper bound that over-states a random workload by about 2×, and the gap is measured
saturation, not noise.

## Deviations, and what to do differently

- **D1 (registered).** One shared A base word instead of E60/E65's per-position random base, with a separate zero
  (`aq_e64`) for bit 30. This removes a confound the earlier scans carried, and is why the reduction needed a
  per-item zero.
- The A-side designed count is **2,048**, not 4,096, and is read from the manifest rather than hard-coded. The
  B-side scan's reduction still divides by a literal 4,096 — correct there, but the next reducer should take both
  from the manifest.
- **P4's verdict depends on the pass set** (FAIL on the registered passes at 0/5 significant, PASS on the clean
  ones at 5/5). The busy partner is positive at every position in both, so the direction is not in doubt; the
  significance is, and it is the noisy passes that cost it.
- **The turn-on correction (A13) was wrong, and is reported as wrong.** It was registered before the grid ran, on
  a hypothesis the grid then refuted. The arithmetic stands — a price measured against a constant-operand zero is
  not a marginal price — but the correction is not a constant subtraction.

## Lessons

- **The issue order decides the flip rate, not the operand.** Reading `make_hl.py:issue_streams` before building
  the items is what caught that an A word is held for two micro-ops. A scan built on "both operands flip every
  cycle" would have reported every A-side price exactly 2× too low and nothing would have errored.
- 🛑 **A pass gate must watch every item that should not move, not one item's drift.** `anchor_pi` first-versus-last
  kept the worst pass of this session and discarded a better one. The replacement is in `ha/constspread.py`: the
  spread of all constant-operand runs in the pass. E67 is the first of these experiments to carry enough
  constant-operand items for that to be possible — six, by six different routes — and they cost one run each.
- **A price list measured one knob at a time cannot be summed without testing that it can be.** The only way to
  find the 2× was to turn two knobs at once and then to compare against a counted random workload. Both cost
  little card time (25 items and 2 items) next to the 32-position scan, and both changed the conclusion.
