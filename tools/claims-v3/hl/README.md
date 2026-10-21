# V3-HL: the bit-flip ladder (E60, Q119)

*Pre-registered Tue 20 Oct 2026 (week 43) before the first measured pass; any change after this commit goes in the
Amendments section at the end, dated, before the data it touches.*

**The question.** What does one flipped bit cost on the ET-SoC-1? Horace He found that a matmul runs faster on
predictable data, because it flips fewer transistors; the Horace experiment (findings 10–11) showed the same matmul
drawing 38.3 / 46.7 / 63.4 W on zeros / ones / random data at one speed, and priced four kinds of counted RTL toggle by
fitting 14 patterns of opportunity. This experiment turns one knob at a time instead: **how many operand bits flip
between one operation and the next**, at fixed clock, voltage, launch temperature and throughput. The slope of power
against designed flips is the energy of a flip. It is the "Hamming ladder" of the 12 Oct plan
(`docs/findings/02-requests.md` Q119), with a second, one-gate-deep ladder on the vector integer unit added.

## The families (make_hl.py; every operand file and its designed flip counts are generated and re-derived by `--check`)

| Family | Kernel | What changes | Designed flips | What its slope means |
|---|---|---|---|---|
| `anchor_*` | Horace (`sparsity_host --test fma`, 1,024 minions) | built-in zeros, ones, pi, randn | — | ties to 21 Sep; card scale; drift (pi first and last in every block) |
| `lq_h<h>` quiet ladder | Horace | A = 1.0 everywhere; in lane l, B alternates every cycle between `b_l` and `b_l ^ (low h mantissa bits)` | 4,096·h B bits per op per minion | all-in cost of a flipped B mantissa bit with a quiet partner (the cascade it starts included) |
| `lb_h<h>` busy ladder | Horace | the same with A = pi | 4,096·h | the same with a busy partner: the first flipped bit wakes the multiplier tree |
| `ls_h<h>` | Horace | quiet partner, the h bits spread over the mantissa | 4,096·h | at equal Hamming weight, *which* bits flip |
| `ord_<o>_<pos>` | Horace | the 16 values of every A column in Gray, binary, shuffled or max-flip order (4 mantissa bits at bit 0 or 19); B fixed | A bits 2,048 / 3,840 / 4,352 / 7,168 per op | the same 4,096 multiply-adds (permuting A's rows permutes C's), only the order differs |
| `bit_<j>` | Horace | one B bit j flips every cycle, A = 1.0 (bit 30: base exponent 64 so both values stay normal) | 4,096 | which bit positions cost what: sign, exponent, mantissa |
| `xin_h<h>` | catalogue (`enercat_host --pattern fxor.pi --operands file:`, one hart per minion) | f0..f7 = x, y, x, y, … with y = x ^ (low h bits), every lane | 16·h port bits per instruction, result constant | price of a bit flip on the two read ports (one gate deep: an XOR) |
| `xio_h<h>` | catalogue, fxor.pi | f0..f7 = x, x, y, y, … | 8·h port bits and 8·h result bits per instruction | port flips plus result-path flips |
| `ain_h<h>` | catalogue, fand.pi | f0..f7 = x, y, x, y, … with x zero under the mask | 16·h port bits, result constant | the same as xin through an AND |

The catalogue block is `op f8,f0,f1 / op f9,f1,f2 / … / op f15,f7,f0` (gen_ops.py), so op i reads (f_i, f_i+1). Sources
are never written and every sink is rewritten with the same value, so no register cell flips: only the read ports, the
operand buses, the gate and the result path. `--harts 1` keeps the vector unit's op-to-op sequence the designed one (two
harts would interleave in the shared unit). Measured on the smoke runs: 0.58 instructions per cycle per hart.

The highest cycle of 16 four-bit codes is 3.5 flips a step, not the 12 Oct plan's "~3.75": a 4-bit step joins a code
only to its complement, so at most 8 of the 16 steps flip 4 bits.

## Protocol (run_hl.py inside a lib.sh block; one block = one pass = one replicate)

- **Launch reading.** Before every run: 2 s random-fp32 heater launches until the mean minion-shire reading is ≥
  `preheat`, then idle until it first shows ≤ `target`, then launch: the 21 Sep method (`run_horace_strict.sh`). A run
  whose reading is not reached is skipped and recorded, never launched off-protocol.
- **Runs:** 4 s (fma and ec). Two unrecorded anchor_pi burn-in runs start every pass. anchor_pi runs first and last in
  every block (drift = last − first); everything else is shuffled with `Random("<card>|<pass>|<block>")`.
- **Safety:** every device process under `timeout 10`; sparsity launches with `--stop-file`; the pass stops (and writes
  STOP) at a reading of 78 C, on a telemetry line older than 3 s (no heating blind), or when another user appears on the
  card; the card lock is held for the pass and released between passes; block.sh kills the runner on any signal.
- **Telemetry:** ettelem at 10 Hz for the whole pass (board power, rails, clock, voltage, 34 shire sensors).

## Departures from the 21 Sep protocol and from the plan, and why

- **D1, idle logins.** On aifoundry3 (two other users with idle tmux logins since 11 and 16 Oct) and aifoundry1 (user
  max, whose card is card 1), a user who is only logged in does not block; another user on *this* card does (card-scoped
  `et-holders`, failing closed), as amendment A3 already does for aifoundry1. aifoundry2 keeps lib.sh's own test. The
  cards are claimed in #community-lab for the evening.
- **D2, the launch reading is 57–58 C, not 80 C.** Measured tonight (probe_heat.sh, data `hl-probe/p1`): twenty 2 s
  heater launches take aifoundry2 and aifoundry3 to 64 C and aifoundry1's card 0 to 60 C; the cards no longer reach
  80 C under this duty cycle. So the governor-free cards (aifoundry2, aifoundry1 card 0) run every measured window at
  **800 MHz** (0.618 V and 0.604 V; the clock steps 600 → 800 within 0.7 s of a launch, so seconds 1–3 are clean),
  and only aifoundry3, pinned at 600 MHz (0.522 V), measures the nominal point. Nothing on any card was changed.
  This turns the plan's ½CV² test into one done at natural operating points, across cards: 0.522, 0.604 and 0.618 V.
- **D3, 4 s runs** instead of 7.3 s: the power window is seconds 1–3; the shorter run heats less and shortens the
  approach.
- **D4, no pi bracket around every rung:** pi first and last in every block, shuffled blocks, one launch reading.
- **D5, the order family and the ladders' ties run on the 800 MHz cards** at the power each rung draws there; rungs
  whose 800 MHz power would pass ~65 W (the governor's power threshold) are not run on those cards (lq/ls above h = 8,
  lb, randn).

## Per card (tonight)

| Card | Clock, voltage | Launch | Items | Passes |
|---|---|---|---|---|
| aifoundry3 | 600 MHz, 0.522 V (pinned) | 58 C after 59 C | `anchor_pi,anchor_randn,lq_,lb_,xin_,xio_h8,xio_h16,xio_h32,ain_h0,ain_h8,ain_h32` (30 items) | 4 |
| aifoundry2 | 800 MHz, 0.618 V | 58 C after 59 C | `anchor_pi,anchor_ones,ord_,ls_h2,ls_h8,lq_h0,lq_h2,lq_h8,xin_h0,xin_h16,xin_h32` (18) | 5 |
| aifoundry1 card 0 | 800 MHz, 0.604 V | 57 C after 58 C | `anchor_pi,lq_h0,lq_h2,lq_h8,bit_31,bit_23,bit_0,bit_8,bit_16,bit_22,xin_h0,xin_h8,xin_h16,xin_h32,xio_h8,xio_h16,xio_h32,ain_h0,ain_h16,ain_h32` (20) | 5 |

Ties across cards: anchor_pi, lq_h0/h2/h8 and xin_h0/h16/h32 on all three. Cut order if time runs short: aifoundry3
drops lb_h2, lb_h12, then a pass (never below 3); aifoundry2 drops ls, then passes (never below 3 of ord);
aifoundry1 drops bit_8, bit_16, xio_h8, then passes (never below 3).

## Pre-registered analysis (reduce_hl.py)

1. **Per run:** board power over seconds 1–3 after the first launch starts, corrected to the launch reading with the
   card's leakage slope (21 Sep's `p80`: P − k·(T̄₁₋₃ − T_launch); k fitted per card from the within-run drift of runs
   that heat ≥ 1 C, else 0.4 W/C at this temperature); raw seconds 1–3 and 1–4 kept as checks. Minion rail over
   seconds 2–4. The launch records of one run are one value.
2. **Gates, per run:** every telemetry sample in the window at the card's clock (600 or 800 MHz); the rail voltage
   within ±3 mV of the pass median; fma cycles per op within 0.5% of the family's h = 0 rung; on-protocol launch.
   Failures are counted and reported.
3. **Within a block,** every rung minus its own zero: lq_h0 (lq, ls, bit), lb_h0 (lb), xin_h0 (xin, xio), ain_h0
   (ain); the ord items against ord_gray at the same position.
4. **Slopes:** least squares of the block differences on designed flips per second over the h ≥ 1 rungs, with a free
   intercept (the first flipped bit turns the multiplier tree on: the h0 → h1 step is reported separately as the
   "turn-on"). The unit of replication is the (card, pass): per-pass slopes, then their mean, SE from the
   between-pass scatter. Units: J per flipped bit, C = 2E/V² at the run's mean voltage, electrons Q = CV/e.
   The fma ladders are also fitted against RTL-counted net toggles (predictions.json) for J per counted toggle.
5. **ec:** P = P0(block, op) + e_in·(port bits/s) + e_out·(result bits/s) over xin, xio and ain jointly; per-ladder
   slopes beside it. Rate = measured instructions per cycle per hart × 1,024 × the clock (enercat's own `ops_per_s`
   assumes 600 MHz).
6. **V² across cards:** the per-flip energies of lq (h2 → h8) and xin (h0 → h32) on each card, against V²; predicted
   ratios to aifoundry3: aifoundry1 card 0 (0.604/0.522)² = 1.339, aifoundry2 (0.618/0.522)² = 1.402, independent of
   the clock. Card-to-card scale at equal V and f was 0.88–0.99 (26 Sep), so a ratio is read against that band.

## Predictions (frozen with this commit)

- **fma items:** `predictions.json` beside this file's data (RTL replay of every tile through rtl-sim/fma_toggle,
  priced with the 21 Sep fit). Differences from each family's zero at 600 MHz, 0.517 V, 80 C: lq h1 +1.37, h8 +5.2,
  h23 +13.6 W; lb h1 +3.0, h8 +6.9, h23 +16.0 W; Gray vs max-flip +0.91 W (bits 0–3) and +0.87 W (bits 19–22); bit
  scan from the sign bit (+0.7 W) to mantissa bit 22 (+4.5 W). On the 800 MHz cards the switching differences scale by
  f·V²: ×1.87 (aifoundry2) and ×1.79 (aifoundry1 card 0); on aifoundry3 by (0.522/0.517)² = 1.02.
- **Per flipped bit,** from the same predictions: the lq slope over h ≥ 1 is 0.56 W per h, i.e. **~122 fJ per flipped
  B mantissa bit** all-in at 600 MHz (C ≈ 0.9 pF, ~3 M electrons per flipped input bit: the cascade); lb 0.59 W per h
  (~128 fJ) after a turn-on of +2.4 W; per counted RTL toggle ~0.1–0.15 fJ averaged over the unit's nets.
- **ec (no RTL for this unit; a range, not a model):** e_in 2–20 fJ per port bit and e_out 5–40 fJ per result bit at
  0.522 V, e_out > e_in. A page written today read 5.0 fJ (input) and 33.7 fJ (output and register write) out of the
  E46 catalogue; this measures both directly.
- **V²:** per-flip energies on the 800 MHz cards 1.34× and 1.40× aifoundry3's, within the 0.88–0.99 card band.

## Decision rules

- **Linear ladder:** residual rms of the h ≥ 1 points about the line ≤ 0.25 W (or ≤ 5% of the span) on aifoundry3;
  otherwise the ladder is reported as bent, with the RTL's own curvature beside it.
- **Same arithmetic, different order:** max-flip − Gray > 0 at ≥ 3 SE on aifoundry2 at either position confirms
  that the order of identical multiply-adds changes the power; |difference| < 0.1 W at both positions kills it (the cost
  is in the values, at least on A's path).
- **RTL predictions:** scored as the rms over items of (measured − predicted) differences from each family's zero,
  after scaling the predictions to the card's f·V²; reported against the 21 Sep 0.50 / 0.92 W rms. An rms > 1.5 W on
  aifoundry3 is a failed prediction and is reported as one.
- **V²:** the 800 MHz cards' per-flip energy ratios to aifoundry3 inside [1.34 × 0.88, 1.40 / 0.88] support ½CV²
  scaling; a ratio near 1.33 × 1.40 (≈ 1.87) would mean the energy per flip scaled with f too, i.e. it was not a flip.

## Files

`make_hl.py` (items, operand files, designed counts), `predict_hl.py` (RTL predictions), `run_hl.py` (one pass),
`block.sh` (the lib.sh block), `queue_hl.sh` (passes in a row), `probe_heat.sh` (how far a card heats),
`reduce_hl.py` (the analysis above). The enercat host gained `--operands file:<256 B>` (backward compatible), built
into `build/enercat-hl` so no locked build directory changes.

## Amendments

**A1, Tue 20 Oct 2026, 20:35 PDT** (written after pass 1 on each card and before any pass it touches):
- *Why:* a run takes 8–12 s, not the ~50 s budgeted (the approach to the launch reading takes 1–10 s at 57–58 C), so a
  pass takes 5–6 min on aifoundry3 and about 4 min on the other two; there is time for more. And the design review's
  physics critique, which landed during pass 1: the order family is the headline and belongs on the pinned card; xio's
  results alternate between m and the all-zero word, and ain_h32's x is the zero word, so a zero-word skip in the vector
  integer unit could bias e_out and e_in.
- *aifoundry3, passes 5–8:* `anchor_pi,ord_,bit_31,bit_23,bit_0,bit_8,bit_16,bit_22,lq_h0,lq_h8,xin_h0,xin_h32,xnz_`
  (operand set `build/hl-gen2`, below). The order family at the pinned 600 MHz becomes the primary order measurement;
  aifoundry2's order passes become its 800 MHz replication. Passes 1–4 keep the registered list.
- *aifoundry2, passes 6–10* and *aifoundry1 card 0, passes 6–10:* the registered lists again, with `xnz_` added on
  aifoundry1 (operand set `build/hl-gen2`).
- *New control family `xnz_h<h>`* (h = 4, 8, 16, 24; make_hl.py): fxor.pi with f0..f7 = a, b, c, d, a, b, c, d where
  a = x, b = x^p, c = x^p^m, d = x^m, p = bits 28–31: the results alternate p ↔ m, never the zero word; ports and
  result each flip 8(4 + h) bits per op. Its slope against xio's tests the zero-result question. The set is generated
  into `build/hl-gen2`; every earlier file in it is byte-identical to `build/hl-gen`'s (checked).
- *Analysis additions:* ain_h32 is excluded from every e_in fit and reported as a labelled corner point; xio and xnz are
  both reported, e_out from each; runs are keyed by (pass, item, position), since anchor_pi runs twice a pass; the op
  rate is the work completed inside the power window (launches overlapping it, prorated), not a nominal clock; the fma
  ladders' primary regressor is the RTL-counted operand-bus bits (A + B + C: the accumulator reads co-vary with h),
  with the designed B flips and the counted net toggles beside it; the bit scan is quoted as "item minus lq_h0", not
  as a per-flip price.

**A2, Tue 20 Oct 2026, 20:40 PDT** (written after the gate counts of the first passes, before any result of the two
800 MHz cards was looked at: every one of their runs had been set aside by the gates):
- *Why:* on the governor-free cards the clock steps 600 → 700 → 800 MHz after a launch, and after an idle approach
  the step sometimes ends after second 1, inside the registered seconds 1–3 window (aifoundry2 8 of 19 runs, aifoundry1's
  card 0 13 of 42 in the first passes). The same ramp corrupts the within-run leakage fit there (2.4–4.8 W/C, against
  0.25 W/C on the pinned card).
- *Change, governor-free cards only:* the power window is the 2 s that start 0.5 s after the clock first reads the
  card's clock (800 MHz) in the run, but never before second 1; a run whose clock has not reached it by second 1.5 is
  rejected; the leakage fit uses only samples after the same point. aifoundry3 keeps seconds 1–3.
