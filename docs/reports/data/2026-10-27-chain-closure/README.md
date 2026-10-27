# Chain closure — one flipped operand bit to the TFLOPS gap (Q128(f), 2026-10-27)

*An analysis, not an experiment: no card ran for this. Every number below is recomputed from data
already committed in this repo (E38 / 21 Sep, E60, E64, E65, E67), except the four Q126 figures in
the chain table's rows 6–9, which are quoted from Q126's own directories. `sh run.sh <repo-root>
<this-dir>` rebuilds all of it; `report.txt` is that run's output verbatim.*

The question behind the whole Horace line is: **why do zeros multiply faster than random fp32 data on
an ET-SoC-1, and can the gap be traced down to the cost of switching one transistor?** Nine links were
in place by 26 October and three were untested joins. This directory tests the joins, from the card's
side, and says which hold.

## The answer in one table

| | zeros | random normal | burst ratio | sustained ratio |
|---|---|---|---|---|
| **measured** (E64, fp32, 1,024 harts) burst / sustained | 12.3 / 12.3 TFLOPS | 10.7 / 9.2 TFLOPS | **1.150** † | **1.333** ‡ |
| predicted from E67's measured 600 MHz board levels | 12.30 / 12.30 | 10.72 / 9.22 | **1.147** | 1.333 ‡ |
| predicted from the per-bit price list, compressed | 12.30 / 12.30 | 10.34 / 9.22 | 1.190 | 1.333 ‡ |
| predicted from the per-bit price list, flat in company | 12.30 / 12.30 | 11.57 / 9.77 | 1.063 | 1.259 |

**The burst ratio is the quantitative result; the sustained one is only ordinal.** Read the two
footnotes before quoting either.

† **1.150 is one of four measured comparators in E64, and it is the one the prediction matches
best.** E64 also gives whole-run LAD TFLOPS 12.11 / 10.61 = 1.141, burst clocks 800 / 706 = 1.133,
and LAD mean MHz 800 / 710 = 1.127. Against the predicted 1.147 those are −0.2%, +0.5%, +1.2% and
+1.8%. The honest statement is **predicted 1.147 against measured 1.127–1.150, depending on whether
you read TFLOPS or clocks**. The prediction is also only as sharp as its two inputs: the 65 W power
cap (64 W → 1.159, 67 W → 1.127) and the referral, whose own −11% drift (§5), carried as a band of
that size, puts the prediction anywhere in **1.104–1.201**. So: the point estimate lands on the
measurement, and the model cannot resolve the four measurements from each other.

‡ **The sustained ratio is a clamp, not a fit.** Zeros at 800 MHz draws 37.9 W and random at
600 MHz draws 52.5 W, so *any* sustained cap in that 14.6 W window returns exactly 800 / 600 =
1.3333 — and three of the four candidate caps are inside it (E64's registered 50.3 W, a 66 °C trip's
51.4 W, E64's measured sustained ones level 49.4 W). The fourth, E64's own measured sustained random point at
54.4 W, is above it: at that cap random would settle above the 600 MHz floor and the ratio would fall to about
1.30, so the ordinal prediction below is what survives every candidate. *(Corrected Tue 27 Oct 2026: this
read "every candidate cap is inside it", which the 54.4 W point contradicts; the page caught it first.)* For
the three caps inside, the measurement is the same number: E64 reports
sustained 800 and 600 MHz, and its 9.2 TFLOPS is 12.3 × 600/800 = 9.225 rounded. So the predicted
and measured sustained ratios are *identically* 1.3333 and the earlier "0.3%" was E64's rounding.
What the chain does predict here is ordinal and still real: **random falls to the governor's
600 MHz floor and zeros does not.**

Starting one link lower, from the price of a single flipped bit, the readings of that price list
give a **range** rather than a number: 1.063–1.190 for the burst ratio, which contains the measured
1.127–1.150. The width of that range is this work's main remaining gap, and §3 says exactly which
experiment closes it.

## The chain, link by link, with what this directory adds

| # | Link | Status after tonight |
|---|---|---|
| 0 | zeros run faster than random fp32 | measured, E64 |
| 1 | because the governor holds a ~1.3 s average of board power to the card's 65 W TDP, and the die line reads 65.5 °C at 50.3 W of board power | measured, E64 |
| 2 | because random data draws more board power | measured; E67 **24.66 W** step, 21 Sep 25.11 W on the other card |
| 3 | board → die/rail share ≈ 0.70–0.89 | unchanged |
| 4 | per multiply-add: static, per-hart, clocking, data | **§4 — reproduces E38 to 2% / 1% across cards, 3% / 5% on the same card** |
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
| A side (quiet partner B = 1.0) | 305 fJ | 1,440 fJ | 265 fJ | 247 fJ |

*(This table is `report.txt` lines 9–10. An earlier revision typed the A row's first and third
cells as 295 and 282, which were wrong; they are 305.1 and 265.2 fJ.)*

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
laws, each **fitted on and scored on these same seven rungs — in-sample, not a test**:

| law (in-sample) | rms | worst |
|---|---|---|
| flat, 107 fJ per flipped bit, position ignored | 14.4% | 22.7% |
| the price list × m^(α−1), α = 0.775 | 28.5% | 62.5% |
| free power law, 0.481 W × m^β, **β = 0.993** | 13.3% | 19.1% |

The finding here is **the free exponent, 0.993**, which is 1.00 within its scatter. The two
one-parameter-equivalent laws (flat, and c·m^β) are indistinguishable on seven in-sample rungs and
neither "wins"; only the price-list law is clearly worse. The out-of-sample test is `nrd_a` /
`nrd_b` in §3, and *both* laws miss there, which is where the weight belongs.

So along *this* ladder, board power simply counts flipped bits. But that is not the same as saying
position stops mattering, and the repo contains the one contrast that separates the two.

### Which bits, at a fixed number of bits

E60 ran `lq_h2` (the two **lowest** mantissa bits) and `ls_h2` (two bits **spread**, 0 and 12) on
**aifoundry2 at 800 MHz** — same nine passes, same clock, same zero, same m = 2.

| item | m | bit positions | measured ΔW | SE |
|---|---|---|---|---|
| `lq_h2` | 2 | 0, 1 | 1.962 W | 0.059 |
| `ls_h2` | 2 | 0, 12 | **4.207 W** | 0.033 |

Measured ratio **2.144 ± 0.066**; the single-bit price list predicts 1.926, i.e. 111% of the
premium. **That prediction is cross-card and cross-clock, and no on-card control exists**: the
measurement is aifoundry2 at 800 MHz, the price list is aifoundry3's at 600 MHz. E60 measured no
single-bit prices at all on aifoundry2, and aifoundry1-c0's 800 MHz list covers bits 0, 8, 16, 22,
23 and 31, so it has neither bit 1 nor bit 12. The 800/600 price ratio itself spans 1.30–1.54
across positions (§5), which puts the 111% anywhere in roughly 97–128%. So the safe reading is
**at m = 2 the position premium is paid in full, within a cross-card systematic of order 15%**.
The direction is solid; the precision is not.

Now the far end of the ladder — **a different card and clock, aifoundry3 at 600 MHz**: going from
`lq_h16` to `lq_h23` adds bits 16–22, which cost **3.609 W each on their own** (E65, the same card
and clock as that ladder, so *this* comparison is internal), for **0.566 W each** in company — a
**6.4× discount**.

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
the measurement. Neither is right, and the reason is now specific rather than mysterious: the flat
107 fJ was fitted on *contiguous low* mantissa bits, which never exercise the dear high-mantissa
positions; random operands flip those too, and the flat law prices them at the floor. The
compressed list keeps too much of the single-bit premium.

**The low arm is not one number.** The flat law needs a per-bit price and an A-side carry-over, and
the data settles neither:

| flat price | A-side carry-over | both random | vs measured |
|---|---|---|---|
| 107.1 fJ, zero-intercept pooled | 1.637, sum-weighted | 10.63 W | −34% |
| 107.1 fJ, zero-intercept pooled | 1.990, mean of per-position ratios | 11.64 W | −28% |
| 116.8 fJ, E60's own marginal slope | 1.637, sum-weighted | 11.60 W | −28% |
| 116.8 fJ, E60's own marginal slope | 1.990, mean of per-position ratios | 12.70 W | −22% |

E60's own fit of this very ladder keeps an intercept (−0.420 W, 71% of the m = 1 rung) and its
marginal slope is **116.8 fJ** — which is also E60's registered `lq.designed` figure of 116.7 fJ,
the number the chain's link 5 quotes. Forcing that intercept to zero is exactly what drops it to
107.1. And a law whose whole claim is that position stops mattering in company arguably should not
then import a position-*weighted* A/B ratio. So the honest bracket is **−34% to −22% / +18%**, and
the −34% quoted elsewhere is its most pessimistic corner.

**The missing experiment, and it is already written.** Every other multi-bit stimulus confounds *how
many* bits flip with *which* ones, because `lq_h<h>` always takes the lowest h. The control is the
`ls` **spread** family — `spread_mask(h)` puts the h bits at `round(j·23/h)`, across the whole
mantissa — and `make_hl.py` has built `ls_h2, ls_h4, ls_h8, ls_h12, ls_h16` since 20 October.
**Only `ls_h2` has ever run, on one card.** Running the other four rungs against the matching `lq`
rungs, on aifoundry3 at 600 MHz so they join the rest of this analysis, measures the discount as a
function of m directly, at two position mixes. That is 9 items plus a zero, about 20 card-minutes at
this duty cycle, and it turns the −34% to −22% / +18% bracket into a single law. It is the
highest-value 20 minutes of card time left on this question. Running two `lq` rungs alongside would
also put the new ladder and E60's old one on one pass set, which E60's 4-pass rungs need.

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

E38 (V3-ABL-A, 21 Sep, four 7 s runs per card, the same 600 MHz boot clock) measured the same three
terms five weeks earlier. These are its **registered** values — `docs/findings/05-claims.md`
line 486, read by `chain.py` out of the sparsity page's own data block
(`docs/reports/2026-09-18-et-soc1-sparsity.html`, `<script id="sparsity-data">`,
`.v3.operands.<card>.patterns.<p>.pj_mac.mean`):

| card | zeros | ones | random | clocking | data |
|---|---|---|---|---|---|
| aifoundry2 | 0.40 | 2.26 | 5.92 pJ | **1.85** | **3.66** |
| aifoundry3 | 0.16 | 1.93 | 5.37 pJ | **1.76** | **3.44** |
| aifoundry1-c1 | 0.25 | 2.21 | 6.06 pJ | 1.96 | 3.85 |

This work gives 1.81 and 3.63: **98% and 99%** of aifoundry2's pair, and **103% and 105%** of
aifoundry3's own pair on the same card. That is a strong, previously unmade tie: the
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

**B(f) is E64's own joint fit over 103 points, and those points include the very fp32
zeros/ones/randn LAD runs whose clocks this section predicts.** B(800) = 33.61 W is 40.5% of the
predicted random board power at 800 MHz, the number that sets the burst clock. So the
absolute-power agreement below is partly in-sample. The step is the independent comparison:

The card-to-card offset on zeros at 600 MHz is 1.55 W, so the card-independent quantity is the step:
predicted 24.66 / 33.87 / 45.01 W against E64's measured 23.23 / 34.90 / 47.76 W — **ratios 1.062,
0.970, 0.942**. **At 600 MHz nothing is referred** — the model uses E67's own measured anchors —
so the +6% there is the pure aifoundry3-against-aifoundry2 card offset, not a referral error. The
referral's *own* error is the drift off that anchor, 0.942 / 1.062 = **0.888, i.e. −11% over
200 MHz**, and it is monotone, not scatter. Quoting max|ratio − 1| over the three points as "good
to 6%" hides that. **−11% is the figure that propagates into the clocks.**

Feeding that into E64's governor — a ~1.3 s average of board power held to the card's **65 W**
read-back TDP (the literal E64's own `surface_hpl.py` passes to `simulate()`; it is not a fitted
governor parameter, and the registered `governor` dict holds no cap) and a sustained cap of E64's
**registered `cap_w_at_65_5` = 50.3 W**, the board power at which its die line T = 41.88 +
0.4696 × W reads 65.5 °C:

| workload | burst MHz | burst TFLOPS | sustained MHz | sustained TFLOPS |
|---|---|---|---|---|
| zeros | 800.0 | 12.30 | 800.0 | 12.30 |
| ones | 800.0 | 12.30 | 774.9 | 11.91 |
| random | 697.4 | 10.72 | 600.0 ‡ | 9.22 ‡ |

*(An earlier revision used a 66 °C trip, giving a 51.4 W cap and 785.1 MHz for ones. E64's own
sustained fp32 randn point sits at 67.1 °C and 54.4 W, so 66 °C is not a hard trip, and its three
measured sustained board powers — 36.4 / 49.4 / 54.4 W — are not one cap either. The registered
50.3 W is used instead. Random's sustained row is the clamp of footnote ‡, unchanged by this.)*

against E64's measured 800 MHz / 12.3 / 12.3 for zeros, 738 / 12.3 / 11.1 for ones, and 706 burst /
600 sustained / 10.7 / 9.2 for random. Zeros' sustained clock and random's sustained clock are
both clamps (footnote ‡); random's burst clock, the one quantitative prediction in the table,
is 697.4 against a measured 706–713.5 MHz. Ones' sustained clock is the one outright miss, **775
against 738 MHz**; E64's own measured surface misses it the same way (791 MHz) under a flat cap,
so this is the thermal model's error, not the referral's — the sustained points sit 6–8 °C hotter
than the ladder runs that fixed B(f), and B(f) carries no temperature term.

## What closes and what does not

**Closes.**
1. The per-multiply-add split (clocking 1.81 pJ, data 3.63 pJ) against E38's registered
   1.85 / 3.66 on aifoundry2 and 1.76 / 3.44 on aifoundry3 — 98% / 99% across cards and
   103% / 105% on the same card, five weeks apart. **This is the strongest single check here**,
   because nothing in it is shared with the experiments it is checked against.
2. Board power → burst clock → TFLOPS: predicted 1.147 against four measured comparators spanning
   1.127–1.150. Point estimate on the measurement; see footnote † for what that does and does not
   establish.
3. Board power → sustained regime, **ordinally**: random falls to the 600 MHz floor and zeros does
   not. No quantitative content (footnote ‡).
4. The 600 MHz budget → 800 MHz board power: +6% card offset at 600 MHz and a further −11% of
   referral drift by 800 MHz.
5. The price list's internal consistency: E65 reproduces E60's six B positions to 1.03.

**Does not close.**
1. **Per-bit prices → the data term**, to better than the −34% to −22% / +18% bracket. §3 names the
   20-minute experiment that would, and shows that the low arm's width is itself two unsettled
   modelling choices.
2. **Which-bits versus how-many** cannot be separated with any committed stimulus; every multi-bit
   ladder here flips the lowest bits. The one contrast that exists (`ls_h2` vs `lq_h2`) is
   cross-card and cross-clock with no on-card control.
3. The A side's in-company price is carried over from the B side by the ratio of the two single-bit
   lists — 1.64 sum-weighted, or 1.99 as a mean of per-position ratios — because no A-side
   multi-bit ladder exists.
4. Ones' sustained clock, 775 predicted against 738 measured — a missing temperature term in B(f).
   E65's leakage slope, 0.18 W/°C over the 6–8 °C these points run hotter, covers only about 1.4 W
   of the roughly 4 W needed, so something else is also missing.
5. Link 3 (board → die/rail share, 0.70–0.89) is still a range, and it sits under everything in §4.
6. The cross-experiment offset E67 disclosed — 0.40 W on `lb_h0` between E65 and E67, four hours
   apart on one card — is larger than the three cheapest A-side prices and caps how finely a summed
   price list can be trusted at the bottom of its range.
7. The governor's absolute-power arm is partly in-sample: B(f) is E64's fit over points that
   include the runs being predicted, and it supplies 40.5% of the predicted 800 MHz random board
   power.
8. E60's `lq` ladder ran with 4 passes per rung on one session, so the saturation law rests on
   seven rungs from one sitting; the three candidate laws are scored in-sample on exactly those
   rungs.

## Files

| File | What |
|---|---|
| `chain.py` | the whole analysis: price list, saturation, cross-operand, superposition, budget, governor |
| `models.py` | the three candidate laws scored against E60's ladder, and carried to the random operands |
| `effective.py` | the effective price of one flipped bit for every multi-bit stimulus with an exact flip count |
| `position.py` | `ls_h2` against `lq_h2`: which bits, at a fixed number of bits |
| `chain.json`, `models.json`, `effective.json`, `position.json` | every number above, machine-readable |
| `report.txt` | the four scripts' printed output, verbatim |
| `run.sh` | rebuilds all of it from the repo |

Inputs, all committed and all actually opened by the scripts:
`docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/` (B-side prices, hart ladder),
`docs/reports/data/2026-10-27-e67-a-side-bit-prices/` (A-side prices, grid, anchors,
random-operand items), `docs/reports/data/2026-10-20-bitflip-ladder/` (the flip-count ladder, the
800 MHz operating points), `docs/reports/data/2026-10-23-e64-horace-power-limit/` (the static line,
the governor, the die line, the caps, the TFLOPS), and
`docs/reports/2026-09-18-et-soc1-sparsity.html` → `<script id="sparsity-data">` (E38's registered
per-multiply-add energies, the values `docs/findings/05-claims.md` line 486 carries).

An earlier revision listed `2026-09-21-horace-aifoundry2/` here and hardcoded E38 as 0.27 / 2.13 /
5.78 pJ, a triple that appears nowhere in this repo and that no script read. It sat exactly
0.13 pJ below the registered 0.40 / 2.26 / 5.92, which is why its *differences* still agreed. The
registered values are now read at run time from the path above.
