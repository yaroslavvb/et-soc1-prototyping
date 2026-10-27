# The joined load model (Q126), 26 October 2026

One model that takes a load and returns board watts, the clock the governor gives it, the die temperature, the
speed and the energy per unit of work. Until now four pieces did parts of this and none of them joined:

- the flip model, [`tools/ettelem/predict_heat.py`](../../../../tools/ettelem/predict_heat.py) — fp32
  TensorFMA32 tiles only, with no clock, voltage, card or temperature input, a static part of 27.11 W at every
  clock and no term for the cost of running a kernel at all;
- the instruction-and-byte catalogue, [`docs/energy-manual/`](../../../energy-manual/README.md) — 161
  instructions and every memory level, which no predictor reads;
- E60 and E61's measured per-flip prices — in no predictor;
- E64's governor and heat path — in its own reduction.

The model is [`tools/ettelem/load_model.py`](../../../../tools/ettelem/load_model.py); its command line is
[`tools/ettelem/predict_load.py`](../../../../tools/ettelem/predict_load.py).

> **Revised twice the same day.** A check of the first version found ten things wrong with how this page read
> its own numbers, and one bug in the shipped command line. Then job (b) corrected the recount this page's
> second pass was built on (`d1059a8e`), and the second pass was re-run against the corrected files: two more
> claims fell, including the negative multiplier price. Every correction is in place below, in
> [`scores.json`](scores.json) and in [`refit_on_recount.json`](refit_on_recount.json); the section
> [What the first version of this page got wrong](#what-the-first-version-of-this-page-got-wrong) lists all
> thirteen against the sentences they replace. **No frozen prediction changed** — every fix is to the reading,
> to `predict()`, which the freeze never calls, and to the second pass, which is reported separately by
> construction (`scores.json` → `freeze_reproduction`).

## The form

```
P_board = idle(T, card)                     the idle law, re-anchored on E64's own 600 MHz floor
        + k_clk * (s(f) - 1)                the clock-dependent static part (E64's floor by clock)
        + c0 * s(f)                         a per-kernel offset, paid once while any hart runs
        + p_sm * (active/1024) * s(f)       the tensor state machines
        + flips * prices * (V/0.517)^2 * k_T * k_card       the four flip prices, zero-gated
        + catalogue rows * k_card           instructions, bytes per memory level, bytes per mesh hop

s(f, V) = (f/600) * (V/0.517)^2      k_T = 1 + temp_coeff * (T - 80.96 C)
```

f, V, the card, the die temperature, the switching-temperature coefficient and the card scale are **arguments**,
not corrections a person applies afterwards. `predict_heat.py` now takes the same four
(`--f-mhz --volts --card --temp-coeff`) with **defaults that reproduce its old output byte for byte**
(600 MHz, 0.517 V, card scale 1.0, no temperature drift — every multiplier is exactly 1.0; checked against the
pre-change JSON for `randn`).

A catalogue row that is the card's **own** measured pJ per byte already carries the card, so `predict()` no
longer multiplies it by the card's switching scale as well. Only a pooled price takes that scale.

## What the joining changed

| Fitted here | Value | What it replaces |
|---|---|---|
| idle anchor at 58 °C | **24.46 W** | the 21 Sep law read at 58 °C, 25.26 W: 0.80 W high, because it was fitted at 64–88 °C |
| clock-dependent static `k_clk` | **8.40 W** per unit of `s(f) − 1` | nothing: the old static part was 27.11 W at every clock |
| per-kernel offset `c0` | **−1.18 W** at 600 MHz / 0.517 V | nothing (the model predicted 0 W) — and the 14 fp32 patterns argue against it, see below |
| leakage over 54–67 °C | P_fix 16.69 W, A(80 °C) 20.95 W, **e-fold 27.0 °C** (0.026 W rms over 14 bins) | the 21 Sep law's 36 °C e-fold, fitted at 64–88 °C. **Fitted, not yet used by any number in this report**: the freeze, the scoring and `predict()` all run on the `e64` law. It is reachable only as `predict_load.py --law cool`. Refit on E44's aifoundry3 idle cycles, the only committed idle below 64 °C. Local slope at 58 °C: 0.344 W/°C refit, 0.351 W/°C old, 0.442 W/°C measured on aifoundry2 at 800 MHz |

### The per-kernel offset: about zero on two experiments, against the fp32 patterns on a third

Recap item 5 read E62's hart line as "5.80 W + 55.8 mW a hart, and the model, forced through zero, predicts 0 W
for that offset". Fit E64's floor by clock and E62's de-leaked 0-hart intercept *together* and there is no room
left for a positive kernel cost: `c0` comes out at **−1.18 W**, which says E62's 5.4 W offset is the 600 → 800 MHz
clock step, not a fixed cost of running a kernel.

Three things bound how far that goes.

1. **It is three parameters on four observations**, one degree of freedom, 0.42 W rms (the 700 MHz point is
   +0.59 W), and E62's intercept carries a ±0.30 W interval of its own. Read `c0` as "within about a watt of
   zero".
2. **E62's intercept is one of those four observations, not a test of them** — see the E62 section below.
3. 🛑 **The 14 fp32 patterns do not support it.** Put `c0 = −1.18 W` into the base the four flip prices are
   fitted on and the leave-one-out error goes from **0.458 W to 0.739 W**, 61% worse, and the fitted
   operand-bus price swings from 16.09 to 25.34 fJ. The design matrix has four flip-rate columns and no
   constant column, so a constant in the base is *not* absorbed: the four prices have to take it up through
   regressors that cannot represent one. On that measurement the offset is wrong.

The experiment that would settle it is the two-kernel hart ladder at one clock that the recap's item 5 asks for.

## The four held-out loads

Predicted first ([`frozen_predictions.json`](frozen_predictions.json), pushed as `92b30b8d` before any score was
computed), then scored ([`scores.json`](scores.json)).

| Load | Measured | Predicted | Miss |
|---|---|---|---|
| **E43 the relay**, DRAM route, pJ/B | 116.24 [104.5–135.3] | 115.31 | **−0.8%**, inside the 99% interval |
| the next shire's scratchpad | 8.92 [7.63–10.18] | 9.18 | **+2.9%**, inside |
| this shire's own scratchpad | 4.34 [3.75–5.07] | 4.04 | **−6.9%**, inside |
| **the same three in WATTS** (aifoundry2) | 4.34 / 4.42 / 5.30 W | 6.12 / 5.90 / 6.38 | **+41.1% / +33.6% / +20.3%** |
| **E39 gemv ladder**, slope | 14.97 / 14.50 / 15.78 W | 15.59 / 13.89 / 14.42 | +4.1% **outside** / −4.2% inside / −8.6% **outside** the 99% interval |
| intercept (the all-zero rung) | 2.30 / 0.93 / 1.48 W | 0.69 / 0.84 / 0.02 | −1.61 / −0.09 / −1.46 W |
| **E37 mmbench from DRAM** | 8.78 / 8.36 / 8.87 W over idle | 10.78 / 10.36 / 11.26 | **+23% / +24% / +27%** |
| **E59 sparse parity**, L1 | 12.74 W over idle, 1.66 J a solve | 9.80 W, 1.34 J | −23.0% |
| L2 | 14.66 W, 6.20 J | 12.69 W, 5.43 J | −13.4% |
| (256,5) first half | 13.92 W, 12.60 J | 11.18 W, 10.58 J | −19.6% |
| (256,5) second half | 10.46 W, 15.82 J | 6.40 W, 9.89 J | −38.8% |

Per load: E43 **4.3% rms** in pJ per byte and within ±8% on all nine card-and-route pairs, but **+20 to +41% on
watts**; E39 **1.10 W rms** over its six independent predictions (three slopes, three intercepts), bias −0.75 W,
with **2 of 3 slopes outside the measurement's 99% interval**; E37 **2.14 W rms**, bias **+2.13 W**, every card
high; E59 **3.02 W rms**, bias **−2.92 W**, every size low.

**What the misses say.**

- **E43 is the model's best load on pJ per byte and one of its worst on watts.** The pJ/B figure is the headline
  because **finding 18's own table is not internally consistent** — 104.8 pJ/B × 48.4 GB/s is 5.07 W beside its
  printed 4.34 W over idle, 17% apart — but a 17% source inconsistency does not cover a 41% miss. Decomposed
  (`scores.json` → `loads.E43_relay.watts_decomposed`), on aifoundry2:

  | route | miss | finding 18's own inconsistency | the +0.69 W static offset | the pJ/B error |
  |---|---|---|---|---|
  | DRAM | +41.1% | +29.6 pts | +15.9 pts | −4.4 pts |
  | next shire's scratchpad | +33.6% | +19.7 pts | +15.6 pts | −1.7 pts |
  | own scratchpad | +20.3% | +21.5 pts | +13.0 pts | −14.1 pts |

  So most of the DRAM miss is the measurement disagreeing with itself, and most of the rest is the per-kernel
  offset and the state machines, which finding 18's "over idle" evidently does not carry. What is left the test
  cannot resolve. E43 is also the weakest of the four as a held-out test — the level prices and the relay were
  measured in the same campaign, and energy manual §7.2 already prices the relay by hand with brackets
  95–137 / 5.3–11.8 / 4.5–7.4 pJ/B. What is new is that one script now produces a point prediction per card with
  no person choosing rows.

- **E37 is one assumption.** The prediction streams 2,048 B an op (the A and B tiles) from DRAM at the
  catalogue's 114.6 pJ/B, which is 9.19 of the 10.78 W. Either the 32 MB L3 catches a third of that traffic, or
  a bandwidth-bound stream costs less a byte than the catalogue's DRAM row, which was measured with the L3
  defeated. The measurement sits inside the 1,024–3,072 B bracket the prediction carried: back-solving gives
  **1,604 / 1,577 / 1,578 B an op** on the three cards, three-quarters of the 2,048 B frozen, and the three agree
  to 2%, which says the assumption is wrong by a fixed factor rather than noisy.

- **E59's biggest term had no bracket, and its miss is not a flat floor.** `E59_BYTES_PER_OP = 4,096` carries
  **73–79%** of each prediction, and unlike E37's byte assumption the freeze gave it no bracket. Halving and
  doubling it *after the fact* (2,048–8,192 B an op) brackets all four measurements — so the byte count *can*
  absorb the whole miss — but not as one factor: it would need **4,903 / 5,382 / 5,687 / 7,651 B an op**, a 1.56×
  spread that grows as the tensor duty falls. E37's analogous back-solve agreed to 2% across three cards; this
  one does not.

  The shortfall itself is **2.93 / 1.97 / 2.73 / 4.06 W** over four runs of the *same* kernel on the *same* card
  at duties 0.274 / 0.362 / 0.316 / 0.170 — a 2.06× spread, so a constant per-hart floor does not fit it.
  Divided by (1 − duty), the share of the time the tensor unit is **not** issuing, it reads
  **4.04 / 3.08 / 4.00 / 4.89 W** and tightens to 1.59×. So the missing term scales with the time the core is
  awake and not issuing tensor work — hart 1's row generation as instructions, the 1,606-cycle epilogue, the
  awake core of two harts — which the energy manual's instruction catalogue could price. The same hole shows as
  E64's whole-chain bias on the quiet patterns and as E39's low intercepts.

- **E39's slopes look close and still miss the interval.** Within ±9% in percentage terms, but ABLB-3c's
  intervals are tight and two of the three fall outside them. Every intercept is low: the all-zero rung costs
  0.9–2.3 W that the model, with the zero gate as a hard gate, prices at 0.0–0.8 W. A zero operand slot is not
  free.

**On the E39 rms.** The model's predicted zero rung *equals* its predicted intercept and its predicted dense
rung *equals* intercept + slope, exactly, so the four E39 numbers per card are two independent predictions
scored twice — once against ABLB-3c's line fit and once against ABLB-3ab's endpoints. The primary figure is
**1.10 W over the six independent predictions**; the endpoint cross-check against a different reduction reads
1.60 W, and all twelve pooled (the first version's figure) read 1.38 W.

## E64's 103 points and E62's ladder, re-scored

| | rms over E64's 103 points |
|---|---|
| The old static part (the 21 Sep idle law + `p_sm`, the same at every clock), with each run's measured `c` | **4.05 W** |
| The joined model's static part, with each run's measured `c` | **0.92 W** (bias +0.02 W) |
| E64's own fit, `B` free at each clock and `c` free per run | 0.82 W (its published figure) |
| The whole chain — joined static **and** `c` from the flip counts — on the 85 fp32 points | **1.44 W** (bias +0.67 W) |

🛑 **Row 2 is not held out.** E64's three floors B(600), B(700), B(800) are three of the four observations the
joined static part is fitted on. The joined static part has **three** free parameters (the 58 °C idle anchor,
`c0`, `k_clk`) where E64's own fit has three free floors — and must in addition match E62's intercept exactly.
Read row 2 against row 3 as *the same three floors, reached through a two-parameter clock law plus an offset
tied to another experiment, cost 0.10 W of rms*, not as a prediction. Where that cost shows is the fit's own
residuals: **0.42 W rms over four observations**, +0.32 / −0.59 / +0.27 W at 600 / 700 / 800 MHz.

What *is* new, and not circular: before Q126 the static part was one number at every clock, and it read 4.05 W
rms over the same points — the −19% miss at 800 MHz that recap item 4 names. The clock-dependent term is most of
what was missing.

The whole chain, which has to predict each load's switching from toggle counts as well, reads 1.44 W. Its
residuals are **low on the quiet patterns** (zeros +2.03 W, ones +2.16, sparse75 +1.37, signs +1.18 measured
above model) and near zero on the busy ones (randn +0.18, uniform −0.11, mant +0.23) — the opposite sign to
E60's ladder, where the model reads high. A term that is missing at low activity and absent at high activity is
a floor, not a slope: the same term E59 and E39 point at.

### E62's ladder — the intercept is a fit target

| | intercept | slope | rms over the six rungs |
|---|---|---|---|
| Measured, raw | 5.80 W | 55.77 mW a hart | — |
| Measured, de-leaked (k = 0.442 W/°C, 49 °C baseline) | 5.35 W | 46.28 mW a hart | — |
| The model **before** Q126 | 0.00 W | 50.5 mW a hart | — |
| The model now | 5.33 W | 50.47 mW a hart | **1.25 W** de-leaked, 2.01 W raw |

🛑 **The intercept row is not evidence.** `load_model.fit_static()` solves `k_clk` in closed form from E62's
de-leaked 0-hart intercept at every trial `c0` — `k_clk = (i62 − c0·s(800)) / (s(800) − 1)` — so the fitted model
reproduces that intercept to **8.9 × 10⁻¹⁶ W by construction**. It is fit observation number four.

The 0.026 W that still separates 5.33 from 5.35 is not a prediction error either: it is an **internal
inconsistency in the model**. `fit_static()` refers the clock with E64's *fitted* s(800) = 1.905174, while
`static_w()` and `predict()` refer it with the model's own f·V² = 1.901544 — 0.19% apart. (At 600 MHz the same
mismatch runs the other way, 1.0 against 1.00155, worth about 0.001 W on each frozen over-idle prediction.)

What is scored here is the **slope**: 50.47 mW a hart against 46.28 measured de-leaked, 9% high, which is the
flip model's own per-hart bias, and 1.25 W rms over the six rungs.

## The 14 fp32 patterns

| | at c0 = 0 (the base the prices were fitted on) | at c0 = −1.18 W (the joined offset) |
|---|---|---|
| The published prices, no refit | **0.451 W** | 1.114 W |
| Refit in sample | 0.359 W | 0.652 W |
| Leave one out, each pattern predicted from the other 13 | **0.458 W** (worst `pow2`, +0.97 W) | **0.739 W** (worst `checker`, −1.38 W) |
| Refitted operand-bus price | 16.09 fJ | 25.34 fJ |
| E38's published per-card leave-one-out | 1.008 / 0.906 / 0.966 W, **FAIL** against a registered 0.6 W | — |

At `c0 = 0` the refit reproduces the published 21 Sep fit (3.14 / 0.0315 / 0.742 / 16.09 fJ against the
published 3.179 / 0.0250 / 0.801 / 15.539), as it should. Adding the joined model's per-kernel offset makes the
leave-one-out **61% worse** and swings the bus price 58% up. **That is the result, and it is a negative one for
`c0`:** on the one load where the flip prices themselves were measured, a −1.18 W kernel offset does not belong.

The honest held-out accuracy on the fp32 multiply-add is therefore about **0.46 W on aifoundry2** (the 21 Sep
patterns' own leave-one-out) and E38's 0.91–1.01 W across cards — still a FAIL against the 0.6 W mark on the
cross-card test. What the new terms buy is everywhere else: other clocks, other cards, other die temperatures,
and loads that are not an fp32 tile at all.

## Pinning the operand bus to E60's measured read-port bit (recap item 10)

Q126 shipped `--pin-bus` in `flip_w()` and `predict_load.py` and never scored a fit with it. This is that
fit: [`pin_bus.json`](pin_bus.json), written by
[`tools/ettelem/pin_bus_fit.py`](../../../../tools/ettelem/pin_bus_fit.py). The bus column is moved out of
the design matrix and into the target, so the pinned arm fits **three** prices against the same measurements
with the fourth held at E60/E61's measured register-file read-port bit, **20.83 fJ**. The free arms reproduce
[`scores.json`](scores.json)'s `fp32_14_patterns` to the last float digit — 12 comparisons, asserted in the
file as `reproduction_check` — so the two arms differ only in the pin.

### The 14 fp32 patterns (aifoundry2, 21 Sep)

| | free bus | bus pinned at 20.83 fJ |
|---|---|---|
| **at c0 = 0** — fitted bus | 16.09 fJ | 20.83 fJ (held) |
| in sample | 0.359 W | 0.411 W |
| leave one out | **0.458 W** | **0.495 W** (+8.0%) |
| free parameters | 4 | 3 |
| **at c0 = −1.18 W** — fitted bus | 25.34 fJ | 20.83 fJ (held) |
| in sample | 0.652 W | 0.679 W |
| leave one out | **0.739 W** | **0.748 W** (+1.1%) |

**Pinning is nearly free.** On the base the prices were fitted on it costs 8.0% of the leave-one-out and one
parameter; on the joined model's base, 1.1%. The other three prices barely move (`ffclk` 3.142 → 3.153,
`mult` 0.0315 → 0.0326, `rest` 0.742 → 0.680 at c0 = 0), so the pinned watt comes out of `rest`, not out of
the clock term. The in-sample bias flips sign — −0.054 W free, +0.011 W pinned — which says the free fit was
buying a little of the base with the bus column.

### The per-card spread: it collapses, and on three cards it is cheaper

Three cards is the question item 10 actually asks. The only committed board powers measured on more than one
card are the version-3 check of 26 September, ABL-R's own 14 rows (8 fp32 patterns + 6 structured matrices)
on aifoundry2, aifoundry3 and aifoundry1's card 1 — 4 kept busy runs each, 1,024 minions at 600 MHz, each
card fitted on **its own** measured idle and **its own** measured rail, so the prices are referred to 0.517 V
and the spread is the card's, not the rail's.

| bus price, fJ | aifoundry2 | aifoundry3 | aifoundry1-c1 | max ÷ min |
|---|---|---|---|---|
| free, c0 = 0 | 31.17 | 18.35 | 28.59 | **1.70×** |
| free, c0 = −1.18 W | 41.64 | 28.65 | 39.89 | 1.45× |
| pinned | 20.83 | 20.83 | 20.83 | **1.00×** |
| the published ABL-R refit, for reference | 30.56 | 28.03 | 32.79 | 1.17× |

| leave-one-out rms, W | aifoundry2 | aifoundry3 | aifoundry1-c1 |
|---|---|---|---|
| free, c0 = 0 (4 parameters) | 0.947 | 0.930 | 0.933 |
| **pinned, c0 = 0 (3 parameters)** | **0.905** | **0.835** | **0.863** |
| the published ABL-R refit (5 parameters) | 1.005 | 0.907 | 0.966 |

**The spread collapses and nothing pays for it.** The free bus term moves 1.70× across the three cards — the
loosest term in the model, as item 10 says. Pinned, the leave-one-out improves on **every** card, and on
three free parameters it beats the published five-parameter per-card refit (non-negative least squares with a
free constant) on every card too.

**And the spread does not simply move somewhere else.** The other three prices spread 1.29 / 1.27 / 1.25×
(`ffclk` / `mult` / `rest`) in the free arm and 1.28 / 1.26 / 1.31× pinned — unchanged to within a few points.
That residual ~1.3× is the card-to-card term the model already has a name for (E38's switching scale, 0.958–
0.969 for aifoundry3) plus the launch-temperature difference below; it is not the bus term in disguise.

Three things this does **not** settle.

1. **It does not rescue the cross-card claim.** 0.835–0.905 W is still well above ABL-R's registered 0.6 W
   leave-one-out bound. Pinning makes the model smaller and more honest, not accurate across cards.
2. **The three cards launched at different die temperatures** (80.9 / 55.8 / 80.9 °C registered; 80.1 / 57.4 /
   80.0 °C mean reading). Each card's switching is measured against its own idle at its own temperature, so
   each fit is internally matched, but the across-card comparison carries that difference. It carries it
   identically in both arms, so the free-against-pinned comparison is unaffected.
3. **The bus term's spread across *populations* is still the larger number.** Counting the fits now on
   record at c0 = 0 — 16.09 (14 fp32 patterns), 16.72 and 14.16 (the two recount rungs), and 31.17 / 18.35 /
   28.59 (the three cards) — the free bus runs 14.16 to 31.17 fJ, **2.2×**. That is the spread pinning is for.

## The second pass: job (b)'s toggle recount, verified and corrected

Job (b) landed on `main` while the first pass was running (`dc3a5820`, `b2e180b9`) and shipped
[`recount.json`](../2026-10-26-toggle-recount/recount.json), not the `counts.json` this hook first expected, with
no four-class split of its own, so `load_model.recount_reading()` builds one. **The split is this model's, not
job (b)'s.** Then job (b) revised its own files (`d1059a8e`) — after this page had been written. The whole second
pass was therefore re-run: [`refit_on_recount.json`](refit_on_recount.json), written by
[`tools/ettelem/refit_on_recount.py`](../../../../tools/ettelem/refit_on_recount.py). Nothing in it touches the
frozen predictions or their scores.

**What survived the re-run.** Two of the three fits the first pass published reproduce **to the last float
digit**. The third cannot be re-run at all: it divided `by_block_settled` by `hier-factors.json`'s per-module
factors, and that file now lists all 40 switching modules with a **null** factor on the 12 that hold no merged
net — and says in its own `_how_to_use`, *"Do NOT divide `by_block_settled` by the per-module factors below"*.
So the 0.707 W leave-one-out this page used to report for that rung is withdrawn, not restated; the rung is
retired in `load_model.RUNG_RETIRED` and returns a reason instead of a traceback.

**What was wrong, and it was the headline.** The negative multiplier price was an artefact of the split, not a
property of the counts. `by_block_hier` is not a per-block net count: a net is credited to the **outermost**
module that names it, so the multiplier's share reads 54.8% of `by_block_settled` but 22.8% of `by_block_hier`
on `randn` and **0.0%** on `pow2` and `signs`. A least-squares fit whose multiplier column collapses to zero for
an attribution reason has nothing left to fit. Taking the shares from `by_block_settled` and letting the rung
choose only the *total* — job (b)'s corrected recipe — the multiplier prices at **+1.20 fJ a net**. All at
`c0 = 0`, prices in fJ:

| counts, per multiply-add | ffclk | mult | rest | bus | in sample | leave one out | per counted wire |
|---|---|---|---|---|---|---|---|
| the bench's own, 21,331 names | 3.14 | 0.032 | 0.742 | 16.09 | 0.359 W | **0.458 W** | 0.140 fJ (1.0 fF) |
| settled names, 7,083 | 3.25 | 0.225 | 0.710 | 16.03 | 0.488 W | 0.698 W | 0.444 fJ (3.3 fF) |
| per VCD identifier, 3,968 | 3.25 | 0.378 | 1.296 | 16.04 | 0.592 W | 0.872 W | 0.793 fJ (5.9 fF) |
| **per net, one factor (5.327), 1,330** | 3.25 | **1.197** | 3.783 | 16.03 | 0.488 W | **0.698 W** | **2.367 fJ (17.7 fF)** |
| per net, pattern by pattern, 1,301 | 3.36 | 1.179 | 3.885 | 17.96 | 0.853 W | 1.364 W | 2.403 fJ (18.0 fF) |
| per distinct waveform, one factor, 1,007 | 3.25 | 1.580 | 4.994 | 16.03 | 0.488 W | 0.698 W | 3.125 fJ (23.4 fF) |
| per distinct waveform, pattern by pattern | 4.01 | 1.719 | 2.281 | 31.62 | 1.636 W | 2.450 W | 1.973 fJ (14.8 fF) |
| *`by_block_hier` — what the first pass read* | 3.34 | *−1.769* | 3.716 | 16.72 | 0.788 W | 1.347 W | 2.465 fJ (18.4 fF) |

Four things fall out of that table.

**1. The deduplicated counts still fit worse, by half.** Leave-one-out goes 0.458 W → **0.698 W**, in sample
0.359 → 0.488 W, on the best reading of the recount. That is a real cost and a smaller one than the first pass
reported (it had 1.347 W): most of the gap it saw was the attribution artefact, not the recount.

**2. The damage is the per-pattern merge factor, not the merge.** Scaling the whole unit by *one* factor
(5.327 settled names a net) leaves the fit exactly where the settled counts put it — 0.698 W — because a
constant rescale only moves the prices. Using each pattern's own `nets_hier` costs another 0.67 W, and the
reason is in `merge_factor_per_pattern`: among the patterns that really switch, the factor runs **5.02 to 7.20**
(`sparse75` 5.22, `signs` 6.15, `a_ones_b_randn` 7.20). The hierarchy merge is not pattern-neutral, and fitting
through it imports that variation as noise. Quote 1,301 as a count; scale with one factor when pricing.

**3. The energy per physical wire is 2.37 fJ, an effective 17.7 fF — and both halves of that are too big.**
Taking `E = ½CV²` at the fit's 0.517 V (7.48 fF per fJ), the activity-weighted price of one *merged net* on
`randn` is **2.37 fJ ≈ 17.7 fF**, against 0.140 fJ ≈ 1.0 fF for one bench-counted *name*. 17.7 fF is far above
any plausible single wire in this technology, which is the quantitative form of job (b)'s warning that **1,301
is a floor**. Both ends of the division are now measurable against something outside this fit, and both are
loose in the same direction — Q126(e)'s open synthesised netlist of the same unit
([`POWER.md`](../2026-10-26-open-netlist/POWER.md)) counts **3,299 unique physical nets** a multiply-add
(3,623 keeping hierarchy), 2.5× the merged-RTL count, and prices the unit at **1.47–1.52 pJ** against the
3.15 pJ this fit puts on nets alone and 5.62 pJ on all four classes:

| divisor | wires per multiply-add | fJ per wire | effective fF |
|---|---|---|---|
| bench-counted names | 21,331 | 0.140 | 1.0 |
| merged RTL nets (job (b)'s floor) | 1,330 | 2.367 | 17.7 |
| open netlist, unique physical nets | 3,299 | **0.954** | **7.1** |
| open netlist, hierarchy kept | 3,623 | 0.869 | 6.5 |

So the honest reading is **about 7 fF a physical wire, with a factor of 2 either way**, and even that is an
upper bound: the board-power fit carries **3.7–3.8×** the energy the netlist's own power analysis puts on the
unit, which is the size of everything the board meter sees and the lane's nets are not. The one thing every
rung agrees on is the total — the fit puts **5.42–5.76 pJ on one random fp32 multiply-add** at every one of the
eight rungs, because the watts are measured and only the divisor moves.

**4. "16× too large" is right for the whole unit and wrong class by class.** 21,331 counted names against
1,330 merged nets is 16.0× overall, and the published fJ figures are indeed prices per counted *name*. But the
refit does not scale by 16: the multiplier price goes up **38.0×** (0.032 → 1.197 fJ) on a count that fell
24.8×, and `rest` goes up 5.10× on a count that fell 5.40×, while `ffclk` (1.04×) and `bus` (1.00×) barely
move. The classes do not travel together, which is the arithmetic statement of "a refit is not a rescale".

### Does the recount explain the systematic over-prediction?

Mostly no. E60's frozen bit-flip ladder over-predicts: measured differences are **0.832 of predicted** on
aifoundry3's 26 items with 25 of 26 residuals sharing a sign (recap, "it is biased, not noisy"). Each item's
predicted watts are exactly linear in the four flip columns, so a new price vector re-scores the ladder exactly
— except that E60's items are counted in the *bench's* currency, so each class is converted by
κ = (rung count ÷ bench count) over the 14 patterns. Ratio of measured to predicted, and rms:

| prices | aifoundry3, 26 items | aifoundry2, 9 | aifoundry1-c0, 8 |
|---|---|---|---|
| as published | 0.832 / 1.28 W | 0.632 / 1.59 W | 0.721 / 1.89 W |
| refit, the bench's own counts | 0.848 / 1.17 W | 0.660 / 1.42 W | 0.755 / 1.72 W |
| **refit on the recount, one factor** | **0.854 / 1.15 W** | 0.706 / 1.15 W | 0.817 / 1.49 W |
| refit on the recount, pattern by pattern | 0.882 / 0.99 W | 0.722 / 1.06 W | 0.834 / 1.43 W |

Every rung moves the ratio toward 1 on all three cards and lowers the rms, so the direction is consistent. The
size is not established: on the 26-item set the shift is 0.832 → 0.854, and the κ band over the seven patterns
whose multiplier really switches (κ_mult 0.0392–0.0494) moves the same number **0.933 to 0.746** — wider than
the shift itself. **25 of 26 residuals keep their sign under every rung.** So the recount removes at most a
sixth of the bias and leaves the one-sided shape untouched: the over-prediction is a missing or mis-split term,
not a counting artefact. The two-kernel hart ladder at one clock (recap item 5) is still the experiment that
would find it.

*(One cell in that table looks like a result and is not: the per-pattern `distinct` rung reads 0.974 and 0.17 W
on aifoundry2's nine items. Its own fit is the worst of the eight — 2.450 W leave-one-out — so that is a
coincidence between two bad numbers, and it is in `refit_on_recount.json` so nobody has to rediscover it.)*

## The operand-statistics front end (recap item 2b)

[`tools/ettelem/operand_stats.py`](../../../../tools/ettelem/operand_stats.py) predicts the four counted classes
from the operands alone — **no Verilator, no card**. Five features with a reason each: an intercept, the
zero-gated live multiply-adds (computed exactly, as the count of `(i, k, j)` with both operands nonzero), the
operand bits that flip word to word, the partial products the tree has to add (mantissa populations multiplied),
and the partial products that *change*. Fitted on the 14 fp32 patterns of 21 Sep, scored on the structured
matrices **without refitting**.

| | rms |
|---|---|
| The zero gate alone, predicted live multiply-adds against the bench's `lane_valid` | **7.9 of 4,096** |
| Switching watts on the 14 structured matrices, from operand statistics | **1.61 W** |
| The same from the RTL bench's own counts | 0.97 W |

The 14 matrices span 2.28 to 27.64 W measured, so **replacing the bench with arithmetic on the operands costs
about 0.6 W of rms**. Worst: `dct` −3.20 W, `negzero` +2.49 W, `fft_cos` +2.36 W; `fft_cos` is the one the bench
itself misses most (−2.95 W), the cancelling cos/sin pair of recap item 9. Per class the fit is tight on the
clocked bits (0.3%) and loose on the operand bus (49%).

`predict_load.py --tiles-bin <file>` prices a raw tile pair this way. One approximation is named in the script:
the 14 patterns' own tiles were drawn on the card and not kept, so they are re-drawn from the same distributions
with `rtl-sim/fma_toggle/tiles.py` over seeds 1–5. Every feature is distributional, so a re-draw reproduces it to
sampling noise, and four of the fourteen patterns are deterministic. The structured matrices' tiles are the
actual bytes the card was given, so their side is exact.

`operand_stats.py` needs numpy. Since Q128(e) it carries a `uv run --script` shebang with a PEP 723
block, so `./operand_stats.py` fetches its own interpreter and numpy and needs nothing installed; the
block pins python < 3.13 (3.13 dedents docstrings, and this script publishes one into the JSON) and
numpy == 1.26.4 (the version the committed JSON was made with). `python3 operand_stats.py` still works
under any interpreter that already has numpy — on the Intel that is `/usr/bin/python3`, not
`/usr/local/bin/python3.12`. A re-run reproduces the committed JSON to about 1e-12, not to the byte:
the system numpy links Accelerate and uv's wheel links OpenBLAS.

## The files

| File | What |
|---|---|
| `frozen_predictions.json` | the four loads' predictions, with the rule and the assumptions behind each. Pushed before any score |
| `scores.json` | those predictions against the committed measurements, the 14-pattern fit at both bases, the E64 and E62 re-scores, the recount second pass in summary, the freeze-reproduction check and `held_out_leaks` |
| `refit_on_recount.json` | the second pass in full: every rung of job (b)'s ladder refitted, the capacitance each price implies, E60's ladder re-scored under each, and a re-run of what the first pass published. Written by `tools/ettelem/refit_on_recount.py`; it changes no frozen prediction and no score |
| `fit.txt` | the fitted constants and their residuals, as `load_model.py` prints them |
| `operand_stats.json` | the stretch: an operand-statistics front end, fitted without the RTL bench |
| `pin_bus.json` | the operand bus pinned at E60's measured read-port bit, 20.83 fJ: the 14-pattern fit and the three-card fit, free against pinned, at both per-kernel offsets, with the reproduction check against `scores.json`. Written by `tools/ettelem/pin_bus_fit.py` |

## How frozen the predictions are, and what the model takes from the four loads

Frozen by commit order: `frozen_predictions.json` was pushed to `main` as `92b30b8d` before any score was
computed, and no coefficient and no rule was changed after a predicted number was put beside its measurement.
**It is not blind.** The session read the four experiments' records while choosing their operating points — the
duty cycles, the op rates, the die temperatures and the cards all come from the same files that carry the
measured watts — so a measured value was on screen before its prediction was written. E13's and E38's
pre-registrations were stronger than this. What this does establish is that one script, with coefficients from
other experiments, produces every number with nobody in the loop.

**Three constants in the model come from the four held-out loads** (`load_model.HELD_OUT_LEAKS`, also copied into
`scores.json`). None is fitted — each is one number read from the other experiment's record — but a held-out test
has to name them:

| constant | from | reaches | what it did to the score |
|---|---|---|---|
| `hop_pj_per_byte = 1.753` | E43 RL-a, the pooled mesh slope per hop (finding 20) | `hop_w()`, `predict_load.py --hops` | **nothing**: no scored number reads it. E43's own rows are priced from the level prices, not the hop slope |
| `CARDS['aifoundry1-c1']['volts'] = 0.4979` | E39 `ablb.runs.json` `busy_mv` — the only committed rail voltage for that card | every aifoundry1-c1 prediction: E39's line, E43's third card, E37's third card | **made E39 worse.** At this voltage the predicted slope is 14.425 W, −8.60% — the worst number in the E39 row. At a neutral 0.517 V it would be 15.553 W, −1.45% |
| `E59_CYCLES_IDEAL = 280.35` | E37 MMB-a, the measured int8 shared-tile cycles an op | sets E59's tensor duty, and so its tensor term | the tensor term is 9–14% of each E59 prediction, and E59 misses low by 13–39%, so it is not what carries that load |

One bug was found and fixed between the freeze and the scoring: `flip_w` applied the `f/600` factor twice, once
as a faster op rate and once inside `s(f, V)`. Every frozen prediction is at 600 MHz, where that factor is 1.0.
Re-running the freeze today reproduces **219 of the 234 frozen numbers exactly and the other 15 — all E39's — to
within 7.1 × 10⁻¹⁵ W**, a few units in the last place of a double, amplified where a least-squares intercept
subtracts two close numbers (`scores.json` → `freeze_reproduction`). What the bug did change is the E64 and E62
re-scores above, which are at 700 and 800 MHz.

## What the first version of this page got wrong

A check of this page's first version, at commit `fd49b277`, found ten problems. All ten were real. What each
sentence said, and what replaced it:

| | the claim | why it was wrong | where it is now |
|---|---|---|---|
| 1 | "The intercept the old model could not produce at all is now right to 0.02 W, from terms fitted on E64 rather than on E62's own line" | E62's de-leaked intercept **is** one of the four fit observations; the fit matches it to 8.9e-16 W by construction, and the 0.026 W is the model's own s(800) mismatch | [E62's ladder](#e62s-ladder--the-intercept-is-a-fit-target) |
| 2 | "This leg cannot move … every new term is one constant, which a refit absorbs" | the design matrix has no constant column, so `c0` is **not** absorbed: it worsens the leave-one-out from 0.458 to 0.739 W and swings the bus price 16.09 → 25.34 fJ. The "0.74 W honest held-out" and "bus 25.34 fJ, the loosest term" figures were both consequences of injecting `c0` | [The 14 fp32 patterns](#the-14-fp32-patterns) |
| 3 | "E43 4.3% rms, all inside the 99% interval" with its watt errors in a bare array | on watts — what the model is for — E43 misses +20 to +41%, and the stated 17% source inconsistency covers only part of it | [the E43 bullet](#the-four-held-out-loads) |
| 4 | "slopes within ±8.6%" | 2 of 3 predicted slopes fall **outside** ABLB-3c's 99% interval; the scoring computed the flag and the page dropped it | the held-out table and the E39 bullet |
| 5 | "Nothing in the model is fitted on E37, E39, E43 or E59" | three constants do come from them, and one of them sets the worst number in the E39 row | [the leaks table](#how-frozen-the-predictions-are-and-what-the-model-takes-from-the-four-loads) |
| 6 | "E39 1.38 W rms over twelve comparisons" | six of the twelve re-score the same two predictions against a second reduction; over the six independent ones it is 1.10 W | "On the E39 rms" |
| 7 | — | `LM.predict()` multiplied every catalogue row by the card scale on top of a price that was already the card's own, so `predict_load.py` read 10.17 W where aifoundry3's own DRAM price gives 10.56. No published number was affected (the freeze bypasses `predict()`); the shipped tool was | fixed in `load_model.predict()` |
| 8 | — | `--law cool` returned aifoundry3's absolute idle for every card — 8.6 W out on aifoundry1-c0 — and no published number used the flag at all | fixed in `idle_w()`; the table row now says so |
| 9 | "a per-hart instruction term is missing" | true but untested: E59's largest term had no bracket, and the miss is not a flat floor — it is 2.06× across four runs, 1.59× divided by (1 − duty) | the E59 bullet |
| 10 | — | no `docs/findings/` entry, which `AGENT.md` §10 requires for a new result about the chip | [12-heat-management.md](../../../findings/12-heat-management.md) § Pricing a whole load, and the findings README |

An eleventh, found while fixing these: "re-running the freeze reproduces all of them to the last float digit"
is 15 numbers out, by at most 7.1e-15 W. Stated exactly above.

A twelfth and a thirteenth, found when the second pass was re-run against job (b)'s corrected files
(`d1059a8e`, which landed after both earlier versions of this page):

| | the claim | why it was wrong | where it is now |
|---|---|---|---|
| 12 | "on the per-net reading the multiplier-tree price comes out **−1.769 fJ**, which is unphysical" | the price was an artefact of the split, not of the counts: `by_block_hier` credits a net to the outermost module that names it, so the multiplier column read 0.0% on two patterns. Shares from `by_block_settled` give **+1.20 fJ a net**, and the leave-one-out cost of the recount is 0.698 W, not 1.347 | [the second pass](#the-second-pass-job-bs-toggle-recount-verified-and-corrected) |
| 13 | "settled ÷ hierarchy factors … 0.707 W" | that rung cannot be re-run: `hier-factors.json` now nulls the 12 modules that hold no merged net and says not to divide by those factors. The number is withdrawn; `recount_reading('settled_over_hf')` returns the reason instead of raising | `load_model.RUNG_RETIRED` |

Both earlier fits that *can* be re-run — the bench counts at both bases, and the `by_block_hier` rung — reproduce
to the last float digit under this commit, and the check is kept in
[`refit_on_recount.json`](refit_on_recount.json) → `verification_of_the_first_pass`.
