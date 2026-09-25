# 9. Method, and the limits of every table

## How a number in this manual was made

1. **Board power** is the PMIC's reading through the management interface, 10 mW resolution, refreshed every
   133 ms, sampled at 10 Hz by `tools/ettelem`. The three rail figures (minions, SRAM, mesh) are the PMIC's own
   running averages (roughly first-order, time constant about 1 s), which the service processor reports; together
   they account for about half of board power, and the rest — PCIe, the DDR PHY, the IO shire, the regulators'
   own losses — has no sensor.
2. **Idle is subtracted locally.** Each measurement is a burst of a few seconds of back-to-back launches with
   idle on either side (4.5 s in the catalogue; the reruns of the rings and the levels leave 10 s); its idle is the
   mean of the two bracketing stretches, which removes the drift of idle power with die temperature to first
   order. The die still runs a little warmer during a burst than in the gaps, so the extra leakage — the §1 slope
   times the temperature difference — is taken out as well. Over the 23 September catalogue that correction was
   0.40 W in the median and 1.80 W at most over aifoundry2's 1,176 bursts, and 0.16 and 0.78 W over aifoundry3's
   1,158.
3. **Rates come from the device.** Every hart counts what it completed and the cycle counter says how long it
   took, at the 600 MHz the card is pinned to; wall-clock time would measure the host's launch overhead.
4. **Energy per event is power over idle times the burst's wall time, divided by the events completed in
   it.** The gaps between launches inside a burst draw idle power and cancel.

## The comprehensive catalogue: how the variance was driven down

The 23 September catalogue (`workloads/enercat/run_catalogue.py`) measured 386 configurations — every instruction
on zeros and random data, the write and read paths, the wire, line, row and neighbourhood probes — **three times
each, in a different random order every pass**, on both working cards at the same time: 9,264 launches per card,
about 2.6 hours each (`run_catalogue.py DATA --passes 3 --burst 3 --gap 4.5`, then
`analyze_catalogue.py DATA_A2 DATA_A3 DATA_A2_ROWS --out catalogue.json`). Shuffling the order means the slow drift of die temperature over the
session (71 to 85 °C on aifoundry2) lands on different configurations in each pass and averages out instead of
biasing a class. The result per configuration is the mean over the three passes with its standard error:

| | aifoundry2 | aifoundry3 |
|---|---|---|
| Pass-to-pass standard error, median | 1.9% | 1.2% |
| Pass-to-pass standard error, 90th percentile | 6.1% | 3.6% |
| Samples at 600 MHz | all | all |
| Launches that failed | 0 | 0 |

Across the two cards the ratio is 0.950 in the median with a 10th–90th percentile range of
0.906–0.987 over 386 configurations: the residual card-to-card scatter after the common
scale is about ±4%, the same size as the pass-to-pass error, which is what one expects if the scale factor is
real and the rest is measurement.

**The rails.** The service processor's minion, SRAM and mesh figures are `[average, minimum, maximum]` triples.
The minimum and maximum are since the last reset; the average is a first-order filtered reading with a time
constant of about one second (a step on the minion rail reaches 61% after 1 s and 88% after 2 s while board
power steps at once). The rail split of a burst is therefore read from its last 0.6 s and divided by the 0.94 of
the step reached there, against an idle read 3 s or more after the previous burst. `ettelem sample --reset-ms`
can reset the statistics on a schedule if a window mean is wanted instead. An earlier analysis averaged the
three numbers of the triple together, which is why the hot-line and relay reports said the rails barely moved;
those reports' board-power figures are unaffected.

## Confidence bars

Every repeated entry carries **mean** [lo–hi]: the mean over every pass on every card, and in brackets the full
range those passes spanned; a per-card column gives each card's own mean ± its pass-to-pass standard error. The
range is used rather than a standard error of the pooled sample because with n = 6 the bar is dominated by the
systematic difference between the cards (about 5%), which a standard error would understate. The bars confirm
the first edition's estimate for the catalogue (±3% claimed, ±6% measured over two cards) and correct it for the
hot line (±5% claimed, ±17% measured). Rows measured once, or derived, say so where they appear.

| Table | Passes behind each bar | Bar, typical |
|---|---|---|
| §2, §3, §3.1, §4.1, §4.3, §8 | the catalogue: 3 shuffled passes × 2 cards, n = 6 (3 for the constant set) | ±6% median, ±12% at the 90th percentile; pass-to-pass on one card 1–2% |
| §3.2 fp32 | the ablation's 2 runs + the card transfer on both cards, n = 4 | the envelope of ±1 sd: ±2–7% |
| §3.2 fp16, int8 | the ablation's 2 runs on aifoundry2 | ±1 sd of the two runs: under 1% on random data, 1.5% on int8 zeros, 5–6% on the ones patterns (one card) |
| §4.2 levels | 3 passes per card with the manual's sampler, n = 6 | ±5–16% |
| §5 rings | 3 passes per card, n = 6 (s ↔ s+16: aifoundry3 only, see below) | ±4–17% |
| §5 relay | 22 September + 3 warm passes on aifoundry2 + 4 on aifoundry3, n = 8 | ±5% (DRAM), ±4% (scratchpad), ±8% (hop) |
| §6 hot line | 22 September + 3 warm passes on aifoundry2 + 3 on aifoundry3, n = 7 | ±17%: a 1.2 W signal |
| §1 idle law | one fit; a check 20.6 hours after the last workload; the other card | ±0.2 W; +0.7 W on the other card |

Two lessons from the reruns, both now built into the runners and the analysis (`tools/ettelem/run_reruns_warm.sh`,
`run_rings_levels_power.sh`, `analyze_reruns.py`):

- **The die must be warm on aifoundry2.** Its first rerun session (12:51–13:10) ran at 65 °C, the governor's
  threshold, and the minion clock went to 700–800 MHz inside a fifth of the samples of most bursts — a 20 W
  swing in a 2 W measurement. Every pass since is preceded by heating the die past 76 °C, and the analysis drops
  any burst whose samples show the clock off 600 MHz. aifoundry3, pinned by its firmware, needs neither.
- **Some traffic starves the instrument.** Rings between shires s and s+16 slow the service processor's own
  management path: the sampler's command latency goes from 22 ms to 76–146 ms and the board reading is held for
  seconds at a time, on aifoundry2 in every pass. Those bursts are dropped by the sampler's own latency, and the
  observability report lists this among the meter's limits.

The rings and levels of 18 September, polled by `run_energy.py` without the die temperature, are no longer
pooled: on a cooling card the uncorrected method reads 10–50% high on 2 W signals. The ring values On-chip
communication publishes from them read 2–20% higher than the new passes in every configuration (median 10%).

## What "per instruction" means

The cost of that instruction retired on every hart of every minion at once, above idle, including the
cost of the core being awake to issue it (§2: 4.5–5.3 pJ per slot with both harts, what a `fence` or a `nop`
costs; the `addi` loop's 7.2 pJ is not the floor, because its operands change on every instruction). The "marginal over the
`addi` loop" figures in the data subtract that loop's cost, and go negative for a multi-cycle instruction that stalls
the core — the stall is cheaper than issuing `addi` every cycle — so they are given only where they mean
something.

## What a "flip" is, and is not

Only the tensor unit has been resolved below the instruction, and only because its RTL was available
(docs/findings/11-thermal-model.md). A register bit clocked, a net toggled: these are events in a simulation
of the design, counted for the operands the card ran, and the energies attached to them were fitted to the
card's power. They are **not** transistor switches — the open RTL has no cell library, no netlist and no
capacitances — and the fitted energy of one class absorbs whatever real switching correlates with it. The
scalar and vector units have no such model here; their tables are empirical, and the zeros / constant /
random columns are the only window on their data dependence.

## What is not in this manual

- **The other operating points.** Everything is at 600 MHz; the minion rail reads 0.518 V on aifoundry2 and
  0.523 V on aifoundry3 (0.517 V in the DVFS table). The V²f ratios in §1 say what to expect at 700 and 800 MHz
  (1.41× and 1.91× switching power) and one cool-start session agreed to within
  its noise, but no table was re-measured there.
- **Divide and square root**: thirteen instructions trap in U-mode (listed in [3.1](03a-every-instruction.md)), among them every float and
  vector divide and square root.
- **Per-flip energies outside the tensor unit.** See above.
- **Anything at the 0.4 V operating point Esperanto designed for.** This card's firmware does not offer it.
- **The unsensed 15 W, split by sensor.** It is the largest single component of idle and no instrument here can
  split it. [§4.3](04a-fine-grain.md) attributes what a workload adds above idle by regression (delivery losses per rail plus a DRAM
  term), but not the idle 15 W; the improvement ladder in
  [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) says what would
  meter it. That regression and the DDR droop meter are in `docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json`,
  first computed inline and kept as computed; the committed `tools/ettelem/fit_unmetered.py` reproduces the
  attribution exactly and the droop coefficient to within 3% (0.87 against 0.84 mV/W).
