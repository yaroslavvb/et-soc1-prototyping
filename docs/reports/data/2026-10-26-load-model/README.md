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

## What the joining changed

| Fitted here | Value | What it replaces |
|---|---|---|
| idle anchor at 58 °C | **24.46 W** | the 21 Sep law read at 58 °C, 25.26 W: 0.80 W high, because it was fitted at 64–88 °C |
| clock-dependent static `k_clk` | **8.40 W** per unit of `s(f) − 1` | nothing: the old static part was 27.11 W at every clock |
| per-kernel offset `c0` | **−1.18 W** at 600 MHz / 0.517 V | nothing (the model predicted 0 W) — see below |
| leakage over 54–67 °C | P_fix 16.69 W, A(80 °C) 20.95 W, **e-fold 27.0 °C** (0.026 W rms over 14 bins) | the 21 Sep law's 36 °C e-fold, fitted at 64–88 °C. Refit on E44's aifoundry3 idle cycles, the only committed idle below 64 °C. Local slope at 58 °C: 0.344 W/°C refit, 0.351 W/°C old, 0.442 W/°C measured on aifoundry2 at 800 MHz |

**The per-kernel offset is not 5.4 W; it is about zero.** Recap item 5 read E62's hart line as "5.80 W + 55.8 mW
a hart, and the model, forced through zero, predicts 0 W for that offset". Fit E64's floor by clock and E62's
de-leaked 0-hart intercept *together* and there is no room left for a positive kernel cost: `c0` comes out at
−1.18 W. **E62's 5.4 W offset is the 600 → 800 MHz clock step, which the model now has, not a fixed cost of
running a kernel.** The three static observations determine three parameters with one degree of freedom left
(0.42 W rms; the 700 MHz point is +0.59 W), and E62's intercept carries a ±0.30 W interval of its own, so read
`c0` as "within about a watt of zero", not as a negative power. The experiment that would settle it is the
two-kernel hart ladder at one clock that the recap's item 5 asks for.

## The four held-out loads

Predicted first ([`frozen_predictions.json`](frozen_predictions.json), pushed as `92b30b8d` before any score was
computed), then scored ([`scores.json`](scores.json)). Nothing in the model is fitted on any of them.

| Load | Measured | Predicted | Miss |
|---|---|---|---|
| **E43 the relay**, DRAM route | 116.24 pJ/B [104.5–135.3] | 115.31 | **−0.8%**, inside the 99% interval |
| the next shire's scratchpad | 8.92 [7.63–10.18] | 9.18 | **+2.9%**, inside |
| this shire's own scratchpad | 4.34 [3.75–5.07] | 4.04 | **−6.9%**, inside |
| **E39 gemv ladder**, slope | 14.97 / 14.50 / 15.78 W | 15.59 / 13.89 / 14.42 | +4.1% / −4.2% / −8.6% |
| intercept (the all-zero rung) | 2.30 / 0.93 / 1.48 W | 0.69 / 0.84 / 0.02 | −1.61 / −0.09 / −1.46 W |
| **E37 mmbench from DRAM** | 8.78 / 8.36 / 8.87 W over idle | 10.78 / 10.36 / 11.26 | **+23% / +24% / +27%** |
| **E59 sparse parity**, L1 | 12.74 W over idle, 1.66 J a solve | 9.80 W, 1.34 J | −23.0% |
| L2 | 14.66 W, 6.20 J | 12.69 W, 5.43 J | −13.4% |
| (256,5) first half | 13.92 W, 12.60 J | 11.18 W, 10.58 J | −19.6% |
| (256,5) second half | 10.46 W, 15.82 J | 6.40 W, 9.89 J | −38.8% |

Per load: E43 **4.3% rms** in pJ per byte and within ±8% on all nine card-and-route pairs; E39 **1.38 W rms**
over the twelve slope, intercept and endpoint comparisons, bias −1.06 W; E37 **2.14 W rms**, bias **+2.13 W**,
every card high; E59 **3.02 W rms**, bias **−2.92 W**, every size low.

**What the misses say.**
- **E37 is the model's clearest failure, and it is one assumption.** The prediction streams 2,048 B an op (the A
  and B tiles) from DRAM at the catalogue's 114.6 pJ/B, which is 9.19 of the 10.78 W. Either the 32 MB L3 catches
  a third of that traffic, or a bandwidth-bound stream costs less a byte than the catalogue's DRAM row, which was
  measured with the L3 defeated. The measurement sits inside the 1,024–3,072 B bracket the prediction carried:
  back-solving gives **1,604 / 1,577 / 1,578 B an op** on the three cards, three-quarters of the 2,048 B frozen,
  and the three agree to 2%, which says the assumption is wrong by a fixed factor rather than noisy.
- **E59 is low on all four sizes, and most on the one with the lowest tensor duty.** The second half of (256,5)
  runs at a 0.17 duty and misses by 39%; L2, at 0.36, misses by 13%. So what the model lacks is the part of the
  kernel that is *not* the tensor unit and *not* scratchpad bytes: hart 1's row generation as instructions, the
  1,606-cycle epilogue, and the awake core of two harts. The structure is right — the model puts 9.98 of L2's
  12.69 W in the scratchpad, and E59's own rails put the SRAM rail at 2.89 of 6.20 J a solve — but a per-hart
  instruction term is missing, which is the same hole E62 names.
- **E39's slopes are within ±9% but every intercept is low.** The all-zero rung costs 0.9–2.3 W that the model,
  with the zero gate as a hard gate, prices at 0.0–0.8 W. A zero operand slot is not free.
- **E43 is the weakest of the four as a held-out test** and should be read as a consistency check: the level
  prices and the relay were measured in the same campaign, and energy manual §7.2 already prices the relay by
  hand with brackets 95–137 / 5.3–11.8 / 4.5–7.4 pJ/B. What is new is that one script now produces a point
  prediction per card with no person choosing rows. Its watts are reported, not scored: **finding 18's own table
  is not internally consistent** — 104.8 pJ/B × 48.4 GB/s is 5.07 W beside its printed 4.34 W over idle, 17%
  apart — so the model is scored on pJ per byte, the manual's primary quantity.

## E64's 103 points and E62's ladder, re-scored

| | rms over E64's 103 points |
|---|---|
| The old static part (the 21 Sep idle law + `p_sm`, the same at every clock), with each run's measured `c` | **4.05 W** |
| The joined model's static part, with each run's measured `c` | **0.92 W** (bias +0.02 W) |
| E64's own fit, `B` free at each clock and `c` free per run | 0.82 W (its published figure) |
| The whole chain — joined static **and** `c` from the flip counts — on the 85 fp32 points | **1.44 W** (bias +0.67 W) |

**The clock-dependent static term is most of what was missing.** With it the static half goes from 4.05 W rms to
0.92 W, within 0.10 W of a fit that lets the floor float freely at each clock, and the −19% miss at 800 MHz that
recap item 4 names is gone. The whole chain, which has to predict each load's switching from toggle counts as
well, reads 1.44 W. Its residuals are **low on the quiet patterns** (zeros +2.03 W, ones +2.16, sparse75 +1.37,
signs +1.18 measured above model) and near zero on the busy ones (randn +0.18, uniform −0.11, mant +0.23) — the
opposite sign to E60's ladder, where the model reads high. A term that is missing at low activity and absent at
high activity is a floor, not a slope: the same per-hart or per-kernel floor E59 and E39 point at.

E62's ladder, rungs 1–6 at 800 MHz:

| | intercept | slope | rms over the six rungs |
|---|---|---|---|
| Measured, raw | 5.80 W | 55.77 mW a hart | — |
| Measured, de-leaked (k = 0.442 W/°C, 49 °C baseline) | 5.35 W | 46.28 mW a hart | — |
| The model **before** Q126 | **0.00 W** | 50.5 mW a hart | — |
| The model now | **5.33 W** | 50.47 mW a hart | **1.25 W** de-leaked, 2.01 W raw |

The intercept the old model could not produce at all is now right to 0.02 W, from terms fitted on E64 rather than
on E62's own line. What remains is the slope, 9% high against the de-leaked measurement, which is the flip model's
own 1–2 W of per-hart bias.

## The 14 fp32 patterns

| | rms |
|---|---|
| The published prices, no refit (aifoundry2, 600 MHz) | 1.11 W |
| Refit in sample | 0.65 W |
| Leave one out, each pattern predicted from the other 13 | **0.74 W** (worst `checker`, −1.38 W) |
| E38's published per-card leave-one-out | 1.008 / 0.906 / 0.966 W, **FAIL** against a registered 0.6 W |

This leg cannot move and is reported to show so: at 600 MHz on the card the prices were fitted on, every new term
is one constant, which a refit absorbs. The honest held-out accuracy on the fp32 multiply-add is still about
0.7–1.0 W, and it is still a FAIL against the 0.6 W mark. What the new terms buy is everywhere else: other
clocks, other cards, other die temperatures, and loads that are not an fp32 tile at all.

## The toggle-recount hook (job b)

`load_model.recount_counts()` and `load_model.refit_prices()` take job (b)'s recount
(`docs/reports/data/2026-10-26-toggle-recount/counts.json`) and refit the four per-event prices on it;
`score_load_predictions.py` reports the result as a **second, separate pass**, because a recount changes the price
per toggle and not the watts — nothing above it moves. The file is not on `main` as of this commit, so
`scores.json` records `recount_present: false` and the bench-count fit beside it. Expected shape, either
`{"per_pattern": {"<pattern>": {"ffclk": …, "mult": …, "rest": …, "bus": …}}}` or
`{"scale": {"ffclk": …, …}}`; anything else is reported as unreadable rather than guessed at.

Refit on the bench's own counts, for comparison when it lands: ffclk 3.62, mult 0.0321, rest 0.629, **bus
25.34 fJ** — against the published 15.54 and E60's measured 20.83 fJ read-port bit. Recap item 10's point stands:
the operand-bus term is the loosest in the model.

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
clocked bits (0.3%) and loose on the operand bus (49%), which is the term recap item 10 already calls the
loosest in the model.

`predict_load.py --tiles-bin <file>` prices a raw tile pair this way. One approximation is named in the script:
the 14 patterns' own tiles were drawn on the card and not kept, so they are re-drawn from the same distributions
with `rtl-sim/fma_toggle/tiles.py` over seeds 1–5. Every feature is distributional, so a re-draw reproduces it to
sampling noise, and four of the fourteen patterns are deterministic. The structured matrices' tiles are the
actual bytes the card was given, so their side is exact.

`operand_stats.py` needs numpy; on the Intel only `/usr/bin/python3` has it.

## The files

| File | What |
|---|---|
| `frozen_predictions.json` | the four loads' predictions, with the rule and the assumptions behind each. Pushed before any score |
| `scores.json` | those predictions against the committed measurements, the 14-pattern fit, the E64 and E62 re-scores, and the recount hook's state |
| `fit.txt` | the fitted constants and their residuals, as `load_model.py` prints them |
| `operand_stats.json` | the stretch: an operand-statistics front end, fitted without the RTL bench |

## How frozen the predictions are

Frozen by commit order: `frozen_predictions.json` was pushed to `main` as `92b30b8d` before any score was
computed, and no coefficient and no rule was changed after a predicted number was put beside its measurement.
**It is not blind.** The session read the four experiments' records while choosing their operating points — the
duty cycles, the op rates, the die temperatures and the cards all come from the same files that carry the
measured watts — so a measured value was on screen before its prediction was written. E13's and E38's
pre-registrations were stronger than this. What this does establish is that one script, with coefficients from
other experiments, produces every number with nobody in the loop.

One bug was found and fixed between the freeze and the scoring: `flip_w` applied the `f/600` factor twice, once
as a faster op rate and once inside `s(f, V)`. Every frozen prediction is at 600 MHz, where that factor is 1.0,
so re-running the freeze after the fix reproduces all of them to the last float digit; what it changed was the
E64 and E62 re-scores above, which are at 700 and 800 MHz.

The model's coefficients come from E17 (21 Sep), E44, E60, E61, E62, E64 and the energy manual's catalogue, and
from nothing in E37, E39, E43 or E59.
