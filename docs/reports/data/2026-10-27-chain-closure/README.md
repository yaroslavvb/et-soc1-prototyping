# Chain closure — one flipped operand bit to the TFLOPS gap (Q128(f), 2026-10-27)

*An analysis, not an experiment: no card ran for this. Every number is recomputed from data already
committed in this repo (E38 / 21 Sep, E60, E64, E65, E67, and Q126's netlist and cell work).
`sh run.sh <repo-root> <this-dir>` rebuilds all of it; `report.txt` is that run's output verbatim.*

The question behind the whole Horace line is: **why do zeros multiply faster than random fp32 data on
an ET-SoC-1, and can the gap be traced down to the cost of switching one transistor?** Nine links were
in place by 26 October and three were untested joins. This directory tests the joins, from the card's
side, and says which hold.

## The answer in one table

| | zeros | random normal | ratio |
|---|---|---|---|
| **measured** (E64, fp32, 1,024 harts) burst / sustained | 12.3 / 12.3 TFLOPS | 10.7 / 9.2 TFLOPS | **1.150 / 1.337** |
| predicted from E67's measured 600 MHz board levels | 12.30 / 12.30 | 10.72 / 9.22 | **1.147 / 1.333** |
| predicted from the per-bit price list, compressed | 12.30 / 12.30 | 10.34 / 9.22 | 1.190 / 1.333 |
| predicted from the per-bit price list, flat in company | 12.30 / 12.30 | 11.57 / 9.93 | 1.063 / 1.239 |

Starting from board power the chain closes to **0.3%** on both the burst and the sustained ratio.
Starting one link lower, from the price of a single flipped bit, the two defensible readings of that
price list **bracket** the measurement rather than pinning it: 1.06–1.19 against 1.150 measured
(burst), 1.24–1.33 against 1.337 (sustained). The width of that bracket is this work's main
remaining gap, and §3 says exactly which experiment closes it.

## The chain, link by link, with what this directory adds

| # | Link | Status after tonight |
|---|---|---|
| 0 | zeros run faster than random fp32 | measured, E64 |
| 1 | because the governor holds a ~1.3 s average of board power to 65 W and the die trips at 66 °C | measured, E64 |
| 2 | because random data draws more board power | measured; E67 **24.66 W** step, 21 Sep 25.11 W on the other card |
| 3 | board → die/rail share ≈ 0.70–0.89 | unchanged |
| 4 | per multiply-add: static, per-hart, clocking, data | **§4 — reproduces E38 to 3%** |
| 5 | data energy → per flipped bit | **§1 — 64 positions, both operands, one card, one clock** |
| 6 | per bit → toggles | Q126(b) recount, Q126(e) netlist |
| 7 | per toggle → gate energy | Q126(d) ASAP7 cell table |
| 8 | per gate → one transistor switching | Q126(d) SPICE, BSIM-CMG at 0.517 V |
| 9 | electrons, Landauer | **0.153 fJ and 1,846 electrons** per FAx1 switch (Q126(d)) |

The three joins this directory tests are **5→4** (do per-bit prices add up to the measured data
power?), **4→2** (does the budget refer correctly to 800 MHz?) and **2→0** (does the governor turn
that power into the measured clocks?).

---

## 1. The price law

Both operand sides are now priced at all 32 bit positions on **one card at one clock**
(aifoundry3, 600 MHz, 521.9 mV): the B side from E65 block A, the A side from E67 block 1 (its
registered passes). The A-side figures here are the **registered** ones, not E67's clean subset.

| | low mantissa (0–9), mean | bit 22 | exponent (23–30), mean | sign |
|---|---|---|---|---|
| B side (quiet partner A = 1.0) | 109 fJ | 1,008 fJ | 174 fJ | 123 fJ |
| A side (quiet partner B = 1.0) | 295 fJ | 1,440 fJ | 282 fJ | 247 fJ |

The B side spans **12.2×** across positions, the A side **9.4×**. An independent check: E60 priced six
B positions on the same card and clock six days earlier, and E65 reproduces them to a median ratio of
**1.03** (range 0.99–1.12).

A flipped bit is dearer with a busy partner. The A = π prices (E65 block B) are **1.6–4.7×** the
quiet ones at the five shared positions, and the flow-M case — `b` bit 11 against `a` = π — is
**745 ± 56 fJ**.

## 2. What happens when bits flip together — the result that changes the picture

E60's `lq` ladder flips the *h* low mantissa bits of B in one word, for h = 1, 2, 4, 8, 12, 16, 23, on
this same card and clock. It has been in the repo since 20 October and had not been read against the
price list. It should be read, because it settles the saturation question that E67 left open.

| m bits flipping | measured W | measured fJ per bit | price list says, fJ per bit | measured / list |
|---|---|---|---|---|
| 1 | 0.594 | 129 | 136 | 0.95 |
| 2 | 0.841 | 92 | 124 | 0.74 |
| 4 | 1.712 | 93 | 110 | 0.85 |
| 8 | 3.206 | 87 | 106 | 0.83 |
| 12 | 5.536 | 101 | 128 | 0.78 |
| 16 | 8.299 | 113 | 206 | 0.55 |
| 23 | 12.261 | 116 | 382 | 0.30 |

**The measured price per flipped bit barely moves — 87 to 129 fJ across the whole ladder — while the
single-bit list says it should run from 106 to 382 fJ per bit over the same masks.** Three candidate
laws, scored on these seven rungs:

| law | rms | worst |
|---|---|---|
| flat, **107 fJ** per flipped bit, position ignored | **14.4%** | 22.7% |
| the price list × m^(α−1), α = 0.775 | 28.5% | 62.5% |
| free power law, 0.481 W × m^β, **β = 0.993** | 13.3% | 19.1% |

The free exponent is 1.00 within its scatter: along *this* ladder, board power simply counts flipped
bits. But that is not the same as saying position stops mattering, and the repo contains the one
contrast that separates the two.

### Which bits, at a fixed number of bits

E60 ran `lq_h2` (the two **lowest** mantissa bits) and `ls_h2` (two bits **spread**, 0 and 12) on
aifoundry2 — same nine passes, same clock, same zero, same m = 2.

| item | m | bit positions | measured ΔW | SE |
|---|---|---|---|---|
| `lq_h2` | 2 | 0, 1 | 1.962 W | 0.059 |
| `ls_h2` | 2 | 0, 12 | **4.207 W** | 0.033 |

Measured ratio **2.144 ± 0.066**; the single-bit price list predicts 1.926. **At m = 2 the position
premium is paid in full** — 111% of it, if anything slightly more. Now the far end of the ladder:
going from `lq_h16` to `lq_h23` adds bits 16–22, which cost **3.609 W each on their own**, for
**0.566 W each** in company — a **6.4× discount**.

So the premium is paid in full at m = 2 and is **84% gone by m = 23**. The compression is real, it is
a function of m, and the flat law fits the `lq` ladder only because that ladder always takes the
lowest bits, so the rising naive price and the deepening discount happen to cancel. Physically this
is what one expects if the premium is carry-chain and product-path depth: when many bits flip at
once those paths toggle once, not once per input bit.

**Across operands** the picture is different and much milder. E67's 4×4 grid (one A bit and one B bit
at a time) gives cell / (A + B) = **0.79** pooled, median 0.83; the whole-operand test at ~13.5 + ~13.9
bits gives **0.88**. Cross-operand sub-additivity is therefore roughly constant in size — about
10–20% — while within-word compression is strong and grows with m.

## 3. Superposition: do the per-bit prices add up to the Horace step?

The flip counts of a random normal fp32 operand are exact, not modelled: `nrd_a` and `nrd_b` are
committed tiles built from seed 20261020, and their per-position histograms are in `chain.json`.
A random operand flips **13.50** bits per A transition and **13.86** per B transition — sign and
mantissa on about half of them, the exponent's top bits almost never (A bits 27–30 flip 128 times in
2,048; B bits 28–31 544 in 4,096).

| | naive sum of the price list | compressed list | flat in-company price | **measured** |
|---|---|---|---|---|
| A random, B = 1.0 | 17.30 W | 9.62 W (1.29×) | 5.33 W (0.71×) | **7.48 ± 0.23 W** |
| A = 1.0, B random | 21.85 W | 12.08 W (1.11×) | 6.74 W (0.62×) | **10.89 ± 0.02 W** |
| both random | 39.14 W (2.42×) | 19.12 W (1.18×) | 10.63 W (0.66×) | **16.18 W** |

So the naive price list over-predicts the data term by **2.4×**, and the two corrected laws bracket
the measurement at **−34% / +18%**. Neither is right, and the reason is now specific rather than
mysterious: the flat 107 fJ was fitted on *contiguous low* mantissa bits, which never exercise the
dear high-mantissa positions; random operands flip those too, and the flat law prices them at the
floor. The compressed list keeps too much of the single-bit premium.

**The missing experiment, and it is already written.** Every other multi-bit stimulus confounds *how
many* bits flip with *which* ones, because `lq_h<h>` always takes the lowest h. The control is the
`ls` **spread** family — `spread_mask(h)` puts the h bits at `round(j·23/h)`, across the whole
mantissa — and `make_hl.py` has built `ls_h2, ls_h4, ls_h8, ls_h12, ls_h16` since 20 October.
**Only `ls_h2` has ever run, on one card.** Running the other four rungs against the matching `lq`
rungs, on aifoundry3 at 600 MHz so they join the rest of this analysis, measures the discount as a
function of m directly, at two position mixes. That is 9 items plus a zero, about 20 card-minutes at
this duty cycle, and it turns the −34% / +18% bracket into a single law. It is the highest-value
15 minutes of card time left on this question.

## 4. The per-multiply-add budget

4,096 scalar fp32 multiply-adds per TensorFMA32 minion-op × 1.107 × 10⁹ minion-ops/s = **4.53 × 10¹²
multiply-adds/s**, i.e. 9.07 TFLOP/s at 600 MHz and 12.1 at 800 — which is where E64's 12.3 TFLOPS
peak comes from.

| term | board W | pJ per multiply-add |
|---|---|---|
| card idle, no kernel | 24.60 | — |
| leakage slope | 0.182 W/°C | — |
| per hart, zeros / random | 2.08 / 27.1 mW | — |
| zeros, whole board at 1,024 harts | 27.83 | 6.14 |
| clocking (ones − zeros) | 8.22 | **1.81** |
| data (random − ones) | 16.44 | **3.63** |
| random normal, whole board | 52.49 | 11.58 |

E38 measured the same two terms five weeks earlier on the *other* card and got **1.86** and **3.65**
pJ. This work gives 1.81 and 3.63 — **97% and 99%**. That is a strong, previously unmade tie: the
per-multiply-add energy budget transfers across cards and across five weeks. The hart ladder adds
that the data term is linear in harts with a −0.51 W intercept, so there is no fixed per-kernel
offset (E65's C1/C2 verdicts, "neither band").

## 5. End to end

Referring the 600 MHz budget to 800 MHz needs the voltage. E60 measured 521.9 mV at 600 MHz and
603.9 / 617.4 mV at 800 on the two other cards, so dynamic energy should scale by V² = **1.369**; the
six bit prices measured at both clocks give **1.425** on average (1.30–1.54, a cross-card comparison,
hence the spread). Board power is then E64's static line B(f) = {600: 25.46, 700: 28.24, 800: 33.61} W
plus the 600 MHz dynamic part scaled by f·V(f)².

| f | zeros | ones | random | E64 measured (other card) zeros / ones / random |
|---|---|---|---|---|
| 600 | 27.83 | 36.05 | 52.49 | 26.28 / 34.36 / 49.51 |
| 700 | 31.49 | 42.78 | 65.36 | 29.94 / 41.55 / 64.84 |
| 800 | 37.93 | 52.93 | 82.94 | 35.31 / 52.27 / 83.07 |

The card-to-card offset on zeros at 600 MHz is 1.55 W, so the card-independent quantity is the step:
predicted 24.66 / 33.87 / 45.01 W against E64's measured 23.23 / 34.90 / 47.76 W — **ratios 1.06,
0.97, 0.94**. The referral is good to about 6% over the whole 600–800 MHz range.

Feeding that into E64's governor — a ~1.3 s average of board power held to 65 W, and a die line
T = 41.88 + 0.4696 × W tripping at 66 °C, so a sustained board cap of **51.4 W**:

| workload | burst MHz | burst TFLOPS | sustained MHz | sustained TFLOPS |
|---|---|---|---|---|
| zeros | 800.0 | 12.30 | 800.0 | 12.30 |
| ones | 800.0 | 12.30 | 785.1 | 12.07 |
| random | 697.4 | 10.72 | 600.0 | 9.22 |

against E64's measured 800 MHz / 12.3 / 12.3 for zeros, 738 / 12.3 / 11.1 for ones, and 706 burst /
600 sustained / 10.7 / 9.2 for random. **Zeros' and random's four numbers land within 1.2%.** Ones'
sustained clock is the one real miss, 785 against 738 MHz; E64's own measured surface misses it the
same way (791 MHz) under a flat cap, so this is the thermal model's error, not the referral's — the
sustained points sit 6–8 °C hotter than the ladder runs that fixed B(f), and B(f) carries no
temperature term.

## What closes and what does not

**Closes.**
1. Board power → clock → TFLOPS, both regimes, to 0.3% on the ratio.
2. The 600 MHz budget → 800 MHz board power, to 6% on the data step across three clocks.
3. The per-multiply-add split (clocking 1.81 pJ, data 3.63 pJ) against E38's independent 1.86 / 3.65,
   on a different card five weeks apart.
4. The price list's internal consistency: E65 reproduces E60's six B positions to 1.03.

**Does not close.**
1. **Per-bit prices → the data term**, to better than the −34% / +18% bracket. §3 names the 20-minute
   experiment that would.
2. **Which-bits versus how-many** cannot be separated with any committed stimulus; every multi-bit
   ladder here flips the lowest bits.
3. The A side's in-company price is carried over from the B side by the ratio of the two single-bit
   lists (1.64), because no A-side multi-bit ladder exists.
4. Ones' sustained clock, 785 predicted against 738 measured — a missing temperature term in B(f).
   E65's leakage slope, 0.18 W/°C over the 6–8 °C these points run hotter, covers only about 1.4 W
   of the roughly 4 W needed, so something else is also missing.
5. Link 3 (board → die/rail share, 0.70–0.89) is still a range, and it sits under everything in §4.
6. The cross-experiment offset E67 disclosed — 0.40 W on `lb_h0` between E65 and E67, four hours
   apart on one card — is larger than the three cheapest A-side prices and caps how finely a summed
   price list can be trusted at the bottom of its range.

## Files

| File | What |
|---|---|
| `chain.py` | the whole analysis: price list, saturation, cross-operand, superposition, budget, governor |
| `models.py` | the three candidate laws scored against E60's ladder, and carried to the random operands |
| `effective.py` | the effective price of one flipped bit for every multi-bit stimulus with an exact flip count |
| `position.py` | `ls_h2` against `lq_h2`: which bits, at a fixed number of bits |
| `chain.json`, `models.json`, `effective.json`, `position.json` | every number above, machine-readable |
| `report.txt` | the three scripts' printed output, verbatim |
| `run.sh` | rebuilds all of it from the repo |

Inputs, all committed: `2026-10-26-e65-bit-prices-hart-ladder/` (B-side prices, hart ladder),
`2026-10-27-e67-a-side-bit-prices/` (A-side prices, grid, anchors, random-operand items),
`2026-10-20-bitflip-ladder/` (the flip-count ladder, the 800 MHz operating points),
`2026-10-23-e64-horace-power-limit/` (the static line, the governor, the die line, the TFLOPS),
`2026-09-21-horace-aifoundry2/` (E38's per-multiply-add energies and the 21 Sep step).
