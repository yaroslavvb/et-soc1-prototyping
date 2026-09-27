# 9. Method, and the limits of every table

## How a number in this manual was made

1. **Board power** is the PMIC's reading through the management interface, 10 mW resolution, sampled at 10 Hz by
   `tools/ettelem`; under that sampling it takes a new value about every 156 ms on aifoundry2, 158 ms on aifoundry1's
   card 1 and 263 ms on aifoundry3 (the version-3 check, three passes each; the board value's refresh seen by a light
   poller is 126–135, 134–139 and 223–224 ms, and that the 10 Hz sampler lengthens this refresh is resolved at 99% only
   on aifoundry3; the service processor's own pass, timed in its trace, lengthens under the sampler on every card: from
   133 to 160 ms on aifoundry2, 135 to 162 ms on aifoundry1's card 1 and 224 to 266 ms on aifoundry3). The three rail figures (minions, SRAM, mesh) are the PMIC's own running averages (roughly first-order,
   time constant 1.13 s on aifoundry2, 1.24 s on aifoundry3 and 1.15 s on aifoundry1's card 1), which the service
   processor reports; together
   they account for about half of board power, and the rest — PCIe, the DDR PHY, the IO shire, the regulators'
   own losses — has no sensor.
2. **Idle is subtracted locally.** Each measurement is a burst of a few seconds of back-to-back launches with
   idle on either side (4.5 s in the catalogue; the reruns of the rings and the levels leave 10 s); its idle is the
   mean of the two bracketing stretches, which removes the drift of idle power with die temperature to first
   order. The die still runs a little warmer during a burst than in the gaps, so the extra leakage — the §1 slope
   times the temperature difference — is taken out as well. Over the catalogue that correction was 0.33 W in the
   median and 1.92 W at most over aifoundry2's 1,176 bursts, 0.19 and 0.89 W over aifoundry3's and 0.28 and 1.05 W
   over aifoundry1's card 1's (1,176 each).
3. **Rates come from the device.** Every hart counts what it completed and the cycle counter says how long it
   took, at the 600 MHz the card is pinned to; wall-clock time would measure the host's launch overhead.
4. **Energy per event is power over idle times the burst's wall time, divided by the events completed in
   it.** The gaps between launches inside a burst draw idle power and cancel.

## The comprehensive catalogue: how the variance was driven down

The catalogue (`workloads/enercat/run_catalogue.py`'s configurations) was measured first on 23 September on two
cards and again in the version-3 check of 26 September (V3-CATFULL), on three: 392 configurations — every instruction
on zeros and random data, the write and read paths, the wire, line, row and neighbourhood probes — **three times
each, in a different random order every pass**, each pass cut into three parts of about 130 configurations with the
die preheated past 76 °C before each part on the governor-free cards (`tools/claims-v3/catfull/block.sh`, then
`tools/claims-v3/catfull/reduce.py --catalogue-out catalogue.json`, which cuts the bursts with
`analyze_catalogue.py`'s own code). Shuffling the order means the slow drift of die temperature over the session
lands on different configurations in each pass and averages out instead of biasing a class. The result per
configuration is the mean over the three passes with its standard error:

| | aifoundry2 | aifoundry3 | aifoundry1 card 1 |
|---|---|---|---|
| Firmware | 1.3.1 | 1.3.1 (pinned at 600 MHz) | 1.2.0 |
| Pass-to-pass standard error over every configuration, median | 2.1% | 1.4% | 1.5% |
| Pass-to-pass standard error over every configuration, 90th percentile | 5.7% | 3.6% | 4.1% |
| Die temperature under load, median | 74 °C | 58 °C | 61 °C |
| Bursts kept, idle and busy samples at 600 MHz | 1,176 of 1,176, all | 1,176 of 1,176, all | 1,176 of 1,176, all |

Against aifoundry2 the median ratio is 0.972 for aifoundry3 (10th–90th percentile 0.916–1.004) and 0.962 for
aifoundry1's card 1 (0.902–1.141; 0.954 per instruction and 1.147 per byte); on 23 September it was 0.950 for
aifoundry3 (that catalogue is `docs/reports/data/2026-09-23-energy-manual/catalogue-23sep.json`). The energy per
operation rises with die temperature, 0.48% per °C on aifoundry2 and 0.30% on aifoundry3, which accounts for a gap
of aifoundry3's size at its cooler die; aifoundry1's card 1 runs its minion rail 19 mV lower and its SRAM rail 47 mV
higher than aifoundry2's (§8).

**The rails.** The service processor's minion, SRAM and mesh figures are `[average, minimum, maximum]` triples.
The minimum and maximum are since the last reset; the average is the PMIC's own running average, roughly
first-order. Measured on the catalogue's bursts (those with more than 8 W on the minion rail and at least 4 s of
idle either side, `rail_filter` in `catalogue.json`), after board power steps down the minion rail has fallen
57% of the way after 1 s and 85% after 2 s on aifoundry2 (τ ≈ 1.13 s, 241 bursts), 54% and 82% on aifoundry3
(τ ≈ 1.24 s, 238 bursts) and 57% and 84% on aifoundry1's card 1 (τ ≈ 1.15 s, 252 bursts). The rail split of a burst is read from its last 0.6 s and divided by 0.94, the fraction
of the step taken to be reached there, against an idle read 3 s or more after the previous burst. The 0.94 is kept
as it was; the rails' scale rests on it, and each 1% it is off moves the attributed minion delivery loss by about
1.2 points ([Limits of observability, §4.2](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed)).
`ettelem sample --reset-ms` resets the statistics on a schedule; whether that makes the average a window mean is
untested (no script or experiment here has used it). An earlier analysis averaged the
three numbers of the triple together, which is why the hot-line and relay reports said the rails barely moved;
those reports' board-power figures are unaffected.

## Confidence bars

Every repeated entry carries **mean** [lo–hi]: the mean over every pass on every card, and in brackets the full
range those passes spanned; a per-card column gives each card's own mean ± its pass-to-pass standard error. The
range is used rather than a standard error of the pooled sample because about half of the bar is the systematic
difference between the cards, which a standard error would understate. The bars confirm the first edition's
estimate for the catalogue (±3% claimed; ±6% measured over two cards on 23 September, ±7% over three on 26
September) and correct it for the hot line (±5% claimed, ±17% measured). Rows measured once, or derived, say so
where they appear.

| Table | Passes behind each bar | Bar, typical |
|---|---|---|
| §2, §3, §3.1, §4.1, §4.3, §8 | the catalogue (V3-CATFULL): 3 shuffled passes × 3 cards, n = 9 | ±7% median, ±15% at the 90th percentile; pass-to-pass on one card 1–2% |
| §3.2 | the version-3 ablation (V3-ABL-A): 4 runs × 3 cards, n = 12 | ±6–10% on random data, ±9–21% on ones, ±32–59% on zeros, most of it the difference between the cards and the launch-temperature offset of note C2 (§3.2) |
| §4.2 levels | V3-RL: 6 passes per card, the scratchpads filled with zeros or random data on alternate passes, n = 18 | ±17% (L1) to ±46–59% (L2, L3, the scratchpads over both contents); split by contents the scratchpads are much tighter |
| §5 rings | V3-RL: 6 passes per card, n = 18 (s ↔ s+16: aifoundry3's 23 September passes only, see below) | ±11–24% |
| §5 relay | V3-RL: 6 passes per card, n = 18 | ±13–15%, mostly aifoundry1's card 1 reading 17–21% above the other two |
| §3.1's last table, §4.3's gathers, §4.4, §6's last six rows | E48 (V3-GS): 3 passes × 3 cards, n = 9, with the catalogue's clock rule (§3.1's bold figures: aifoundry2 and aifoundry3, n = 6; the 64 KB gather: aifoundry3 alone, n = 3, the rule having dropped the other cards' bursts) | ±8% median, ±10% at the 90th percentile, mostly the difference between the cards; pass-to-pass on one card 0.8% median, 2.5% at the 90th |
| §6 hot line | 22 September + 3 warm passes on aifoundry2 + 3 on aifoundry3, n = 7 | ±17%: a 1.2 W signal, widened mostly by the first session (1.4 W against 1.0–1.2 W since) |
| §1 idle law | one fit on aifoundry2; a check 20.6 hours after the last workload; the version-3 idle cycles on three cards | within 0.1 W on aifoundry2 at 67–83 °C (+0.04 [−0.15, +0.22] W); aifoundry3 +1.0 W and aifoundry1's card 1 +10.1 W above it, each with its own refitted law to 0.1 W rms; the leakage within it 20–29 W at 80 °C, depending on the law's shape |

Two lessons from the reruns, both now built into the runners and the analysis (`tools/ettelem/run_reruns_warm.sh`,
`run_rings_levels_power.sh`, `analyze_reruns.py`):

- **The die must be warm on aifoundry2.** Its first rerun session (12:51–13:10) ran at 65 °C, the governor's
  threshold, and the minion clock went to 700–800 MHz inside a fifth of the samples of most bursts — a 20 W
  swing in a 2 W measurement. Every pass since is preceded by heating the die past 76 °C (the bursts then ran at
  69–73 °C, all at 600 MHz), and the analysis drops any burst whose samples show the clock off 600 MHz.
  aifoundry3, pinned by its firmware, needs neither.
- **Some traffic starves the instrument.** Rings between shires s and s+16 slow the service processor's own
  management path: the sampler's command latency goes from 22 ms to 76–146 ms and the board reading takes a
  new value about twice a second instead of six times, on aifoundry2 in every pass (aifoundry3's sampler stayed at
  22 ms in the same ring on 23 September; in the version-3 passes of 26 September the ring starved it on all three
  cards, 63–141 ms). Those bursts are dropped by the sampler's own latency, and the
  observability report lists this among the meter's limits.

The catalogue, by contrast, keeps its slow-sampler bursts. In the version-3 catalogue six DRAM-read bursts on
aifoundry3 and one on aifoundry2 (tensor loads from DRAM and `dramrow/stride1K`) slowed the sampler to a median of
up to 206 ms per sample against the usual 22 ms (none on aifoundry1's card 1); they stay in the means (`sampler_median_ms` per burst in `catalogue.json`;
[Limits of observability, §4.1](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-chain)).

The rings and levels of 18 September, one pair of runs on aifoundry2 polled by `run_energy.py` without the die
temperature, are no longer pooled: on a cooling card the uncorrected method reads 10–50% high on 2 W signals. The
ring values On-chip communication publishes from them read −1% to +22% against aifoundry2's own new passes
(median +10%).

## What "per instruction" means

The cost of that instruction retired on every hart of every minion at once, above idle, including the
cost of the core being awake to issue it (§2: 4.4–5.1 pJ per slot with both harts, what a `fence` or a `nop`
costs; the `addi` loop's 6.6 pJ is not the floor, because its operands change on every instruction). The "marginal over the
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

- **The other operating points.** Everything is at 600 MHz; the minion rail reads 0.518 V on aifoundry2, 0.523 V on
  aifoundry3 and 0.499 V on aifoundry1's card 1 (0.517 V in the DVFS table). The V²f ratios in §1 say what to expect at 700 and 800 MHz
  (1.41× and 1.91× switching power) and one cool-start session agreed to within
  its noise, but no table was re-measured there.
- **Divide and square root**: thirteen instructions trapped in U-mode in a one-off check while the catalogue was
  written (listed in [3.1](03a-every-instruction.md); the card and the log of that check were not kept), among them every float and
  vector divide and square root.
- **Per-flip energies outside the tensor unit.** See above.
- **Anything at the 0.4 V operating point Esperanto designed for.** This card's firmware does not offer it.
- **The unsensed remainder, split by sensor** (about 15 W on aifoundry2, 13 W on aifoundry3 and 16 W on aifoundry1's
  card 1). It is the largest single component of idle on every card and no instrument here can split it. [§4.3](04a-fine-grain.md) attributes what a
  workload adds above idle by regression (delivery losses per rail plus a DRAM term), but not the idle remainder; the improvement ladder in
  [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) says what would
  meter it. That regression and the DDR droop meter are in `docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json`,
  written by `tools/ettelem/fit_unmetered.py`; their canonical account is
  [Limits of observability, §4.2–4.3](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed).
