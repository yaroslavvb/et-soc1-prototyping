# V3-HPL: Horace — power limit (E64, Q123)

*Pre-registered Fri 23 Oct 2026 (week 43), before the first card pass. This commit freezes the design, the
predictions, the analysis code (`reduce_hpl.py`) and the decision rules; any change after it goes in Amendments at
the end, dated, before the data it touches.*

**The ask** (the owner, Fri 23 Oct 2026, about 19:50 PDT): *"test the hypothesis that the underlying issue is power
limit and not temperature limit. Look up the existing numbers … Do a study of underlying specifications of the chip
and check if it's indeed the power limit that's limiting it, and give me the surface of this power limit. What kind
of speeds would I expect for different types of numbers? … Run necessary experiments on AI Foundry2."*

**The question.** Horace He's A100 ran a matmul 15% faster on zeros than on random data because the GPU sits at its
power cap: data that flips fewer bits draws fewer watts and earns a higher clock. The ET-SoC-1's governor has two
limits, not one: `check_power_throttle_conditions()` steps the minion clock down when the integer mean of the 34
minion-shire sensors reads **above 65 °C** (tested first) or when the PMIC's instantaneous board reading is **above
the 65 W TDP** (`thermal_pwr_mgmt.c` at et-platform `ffca4cbb4`, the closest public source to the cards' BL2 0.20.0;
[14-card-behaviour.md](../../../docs/findings/14-card-behaviour.md), "The clock governor, by firmware build"). The
Horace experiment's speed effect (11.4–11.8 TFLOPS on zeros against 9.3 on random data, 21 September) was measured
from a 62–63 °C die before the October cooling, where the two limits were tangled: random data at 800 MHz drew up to
88 W and took the die past 65 °C within half a second, and ones (56 W, under the TDP) lost 800 MHz to the thermal
test alone. **Which limit sets the speed, for which data and for how long, has never been tested on its own.** Since
the 9 October fan bracket aifoundry2's die idles at 49–51 °C, so the two limits can now be pulled apart without
changing anything on the card.

**What would count.** The hypothesis H is *"the speed is set by the power limit, not by the temperature limit."*

- If the power test steps the clock down on a die that reads at most 65 °C whenever the work draws more than 65 W at
  800 MHz, and never when it draws less, the power limit acts on its own (R1, R2).
- If the thermal test steps the clock down at a reading of 66 °C for work that draws less than 65 W, and holds it at
  600 MHz on a die that starts above 65 °C, the temperature limit acts on its own too (R3).
- Which of the two holds a **sustained** matmul on this card is R4: H survives for sustained work only if the power
  test, not the thermal one, accounts for most of the time below 800 MHz.

## Design

**Card and instrument, as they are.** aifoundry2 (release 1.3.1, BL2 0.20.0; DVFS between 600, 700 and 800 MHz at
0.517, 0.568 and 0.618 V; static TDP 65 W, software threshold 65 °C). **Nothing is set on the card**: no TDP,
threshold, clock, voltage or log level (the lab rule, AGENT.md §5). The runner reads the TDP and the threshold with
`ettelem config` after every run and ends the session if either is not 65.

**Kernel: the Horace experiment's, unchanged.** `sparsity_host --test fma --pattern none`: hart 0 of each running
minion repeats one 16×16 TensorFMA on a tile pair in its L1 scratchpad (546 cycles per op for fp32 and fp16, 318 for
int8 on the full card: 05-claims.md), back to back in ~0.5 s launches for `--seconds`. aifoundry2's build
`build/sparsity_t2` (kernel sha256 `990807f4…`, byte-identical to `build/sparsity`'s, which the Horace experiment
ran). The work per op is 2·16·16·K operations, K = 16 (fp32), 32 (fp16), 64 (int8).

**Instruments.** (1) `ettelem sample --every-ms 100` from the start gate to the end of the idle tail, **without
`--reset-ms`**: a statistics reset restarts the PMIC's running average (E41), and the governor's power loops exit on
that average (`power_throttling()`), so a reset would change the behaviour under test. (2) After every run, with the
sampler stopped (the management node is single-opener): the SP's 4 KB trace ring (`ettelem sptrace`), in which the
governor logs every decision with its cause and its input — `Power throttle down event, current pwr <mW> tdp level:
<mW>`, `Thermal throttle down event, current temperature: <°C>, threshold: 65`, `Thermal idle state event …`,
`Power throttle up event …`, `Power idle state event …` (parsed by `tools/claims-v3/dv2/sptrace_events.py`); the
throttle residencies (`ettelem residency 2 3 4 5 6`, from `ettelem-dv2`, built into `build/ettelem-hpl`); and
`ettelem config`. (3) The kernel's own cycle counters per launch (`cycles_max`, `wall_s`, `ghz`), which give the clock
the work actually ran at and the operations per second.

**Why the trace attributes a step without inference.** In `update_module_soc_power()` the power test runs only while
the throttle state is below `POWER_THROTTLE_STATE_THERMAL_DOWN`, so a logged *power* throttle-down is a step the
power limit took while the thermal branch was not acting; a *thermal* throttle-down names the reading that crossed
65.

**The blocks** (`protocol.json`; 43 runs, about 38 min of card load plus the start gates):

| Block | Runs | Start | Load | What it tests |
|---|---|---|---|---|
| `LAD` | 10 fp32 operand patterns on all 1,024 minions (zeros, sparse75, ones, signs, pow2, a_randn_b_ones, a_ones_b_randn, mant, uniform, randn) × 2 passes, shuffled | die reading ≤ 55 °C | one 6 s process | R1, R2: the power test on a cool die, across 36–84 W at 800 MHz |
| `MIN` | random normal fp32 on 768, 640 and 512 minions (24, 20, 16 per shire) × 2, shuffled | ≤ 55 °C | one 6 s process | R1, R2: the same data across the 65 W line: the watts, not the data |
| `HOT` | fp32 ones and zeros (both under the TDP at 800 MHz) × launch at a falling edge of 67 °C or 63 °C × 2 passes, shuffled | heat with random normal on the full card to a reading of 69 °C, then launch at the first reading ≤ the edge | one 6 s process | R3: the thermal test with power under the TDP |
| `SUS` | fp32, fp16, int8 × zeros, ones, random × 1, shuffled | ≤ 57 °C | nine 8 s processes back to back (~75 s) | R4: which limit holds a sustained matmul; the speeds by number type |

`SMOKE` (four 2 s runs: fp32, fp16 and int8 random, fp32 zeros) runs first and is not analysed.

**Etiquette.** The card is claimed in `#community-lab` before the smoke and released after. The runner holds the card
lock for the session, checks for other users and device processes before every launch process (exit 3), caps every
device process at `timeout 10`, stops on a die mean or hottest sensor of 85 °C or a board reading over 97 W on three
samples, and never signals a device process.

## Predictions (frozen)

**Board power at 800 MHz on the full card from a ~55 °C die** (`p800_w`, the median of the 800 MHz samples in the
first second after the clock reaches 800): the switching watts of the Horace table (600 MHz, 81 °C,
[10-data-dependent-power.md](../../../docs/findings/10-data-dependent-power.md)) scaled by (V/0.517)²·f/600 = 1.905,
on an 800 MHz busy offset of 32.1 W (E60's ones and pi on this card at 800 MHz from 58 °C, 53.3 W, less 1.905 × 10.4 W
of switching, less 0.44 W/°C × 3 °C of leakage). MIN scales the switching watts by minions / 1,024.

| Run | Predicted p800 (W) | Against 65 W |
|---|---|---|
| zeros | 35.9 | under |
| sparse75 | 41.1 | under |
| ones | 52.0 | under |
| signs | 60.9 | under |
| pow2 | 63.1 | margin (63–67) |
| a_randn_b_ones | 66.4 | margin |
| a_ones_b_randn | 73.3 | over |
| mant | 78.0 | over |
| uniform | 79.7 | over |
| randn | 83.7 | over |
| randn, 768 minions | 70.8 | over |
| randn, 640 minions | 64.4 | margin |
| randn, 512 minions | 57.9 | under |

**P1 (R1).** Every run over 67 W logs a power throttle-down with a current power over 65,000 mW before any thermal
throttle-down, and leaves 800 MHz while the die reads ≤ 65 °C.

**P2 (R2).** No run under 62 W logs a power throttle-down.

**P3 (R3).** A run launched on a 67 °C falling edge stays at 600 MHz until the die first reads 65 or less; a run
launched at 63 °C that reaches 66 °C at 800 MHz steps down with a thermal throttle-down and no power throttle-down.

**P4 (R4).** On this card's cooling, the temperature limit holds a sustained matmul on random data: in the last 40 s of
each random-data SUS run, ≥ 60% of the samples below 800 MHz come within 2 s of a reading ≥ 66 °C or follow a thermal
throttle-down; zeros run at 800 MHz in ≥ 90% of the last 40 s. Expected rates: zeros about 12 TFLOPS fp32 (800 MHz
less the launch ramps), random about 9.2–9.8 TFLOPS fp32 (600 MHz with excursions). fp16 is 2× and int8 about 6.9× the
fp32 rate per cycle (546, 546 and 318 cycles per op for 8,192, 16,384 and 32,768 operations).

**P5 (exploratory, from the source).** In 0.20.0 the power-down state is left only through the idle reset or the
thermal path (`update_module_soc_power()`: the up test needs a state below `POWER_UP`), so after a power throttle-down
a run's clock stays where the power-down loop left it (700 or 600 MHz) until the process ends or a thermal event
intervenes: no power throttle-up follows a power throttle-down within a process.

## Decision rules (frozen; `reduce_hpl.py` implements them)

- **R1, the power limit acts on its own.** Population: LAD and MIN runs with `p800_w` ≥ 67 W. PASS if at least 90% of
  them log, inside the work window, a power throttle-down with current power > 65,000 mW as their first throttle-down
  (power or thermal). Needs ≥ 4 runs, else UNDER-RESOLVED. Also reported: how many left 800 MHz with the die at ≤ 65.
- **R2, the power limit is silent under the TDP.** Population: LAD and MIN runs with `p800_w` ≤ 62 W. PASS if at most
  10% log any power throttle-down in the work window. Needs ≥ 4 runs.
- **R3, the temperature limit acts on its own.** (a) Every HOT run launched at a 67 °C edge has at most one work sample
  above 600 MHz before the first reading ≤ 65; (b) every HOT run launched at 63 °C whose die reads ≥ 66 within 1 s of a
  sample at 800 MHz logs a thermal throttle-down and no power throttle-down in its work window. PASS if (a) and (b)
  hold in every run they apply to, with at least 2 runs each; else UNDER-RESOLVED if either has fewer than 2.
- **R4, which limit holds a sustained matmul.** Over the last 40 s of each SUS run, every sample below 800 MHz is
  labelled *thermal* (a reading ≥ 66 in the 2 s before it, or the last governor line before it a thermal
  throttle-down), else *power* (the last governor line a power throttle-down), else *ramp* (within 1.5 s of a process
  start), else *other*. PASS (= the temperature limit holds sustained random data, H fails for sustained work) if every
  random-data run's thermal share of its below-800 samples is ≥ 0.6 and every zeros run is at 800 MHz in ≥ 90% of its
  samples. FAIL otherwise; the shares are reported either way.

Events are placed on the host clock by one fit per session (`sptrace_events.fit_ticks`, anchors: the work and heater
processes' starts and ends; lag 0–1.6 s). If the fit fails, every event since the previous dump counts as the run's,
which is exact for LAD, MIN and SUS (no heating in their gates) and is reported as a deviation for HOT.

## The surface

Descriptive, from the same data: (1) the governor's clock against the work's 800 MHz power (`p800_w`) and the die
reading, every sample of every run; (2) for each number type, the burst rate (LAD, SMOKE) and the sustained rate (SUS,
last 40 s); (3) a model, labelled as one: the board power of each pattern at 600, 700 and 800 MHz fitted from the
measured points (switching ∝ V²f, leakage from the die reading), and the highest operating point each pattern holds
under a power cap from 30 to 90 W at die temperatures from 50 to 80 °C: the power-limited throughput surface, checked
against the measured runs at 65 W.

## Files

`run_hpl.py` (the runner; `--dry` uses a toy card and touches no device), `protocol.json`, `reduce_hpl.py`. Raw data:
`docs/reports/data/2026-10-23-e64-horace-power-limit/` (runs.jsonl, launches.jsonl, tel/, sp/, manifest).

## Amendments

- **A0 (Fri 23 Oct 2026, 20:3x PDT, before any data).** The first smoke (20:31) ended at its first run, before any
  launch, with exit 3 `other_user:et_soc1_use:1>0`: the runner took the et_soc1 use count's baseline before its own
  sampler opened the device, so the sampler read as another user. The baseline is now taken after each sampler start,
  with only our sampler open, as E63's runner does (`run_hlc.py` `take_ns_baseline`). Nothing else changes; that
  session's directory (`build/e64/runs/smoke`) holds only the start-of-session queries.
