# V3-KSPEED: E80 — the speed of each kind of number under aifoundry2's own governor (Q130)

*Pre-registered Sat 31 Oct 2026 (week 44), before the `#community-lab` claim and before the first launch. This
commit freezes the design, the predictions ([`predictions.json`](predictions.json), sha256
`69a62b31607a02a481a8ea23ba716d42fae5822343cb372f7fa706e6ba00762c`), the analysis code
([`reduce_kspeed.py`](reduce_kspeed.py)) and the decision rules. Any change after it goes in Amendments at the end,
dated, before the data it touches. E80's clock starts at the kinds spec `7d9c0d9e` (Q130(s), revision 2) and the
frozen model `2bbe03dd` with its amendment A1 `320f3fdd` (Q130(c)); both are cited by sha256 below.*

**The ask** (the owner, Sat 31 Oct 2026, about 08:40 PDT): *"… The goal is to collect material for blog follow-up,
fully explain the speed/heat/power issues of multiplying varying kinds of numbers. Run experiments on aifoundry …"*
In Q130's plan this is **E80**: the speed of each kind of number under aifoundry2's own governor, with **no governor
move**.

**The question.** E64 measured the matmul's speed on aifoundry2 under the card's own governor for ten fp32 kinds, but
for fp16 and int8 only on zeros, ones and random data
([E64](../../../docs/reports/data/2026-10-23-e64-horace-power-limit/README.md)). Q130(c) predicted every kind's
switching power and turned it into a clock through E64's registered governor (the burst) and E64-T1 (the
sustained clock) ([Q130(c)](../../../docs/reports/data/2026-10-31-q130-kinds-model/README.md)). This experiment
measures, for 18 kinds across the three formats:

- the clock a short job gets: a **burst on a cool die**;
- the clock it settles at: **sustained**, about 76 s;
- the **board power** and **die temperature** at each;
- **which of the governor's two limits** sets the clock (the 65 W power test or the 65 °C thermal test), or neither.

It also scores the prediction chain, kind → watts → clock, cell by cell. One cell matters on its own. E64-T1
never closed the fp16 all-ones sustained cell: it missed by +7.8 to +21.3 MHz over six (γ, trip) pairings
([Q129(a2)](../../../docs/reports/data/2026-10-27-q129-governor-temperature/README.md)). E80 runs that cell twice.

## Design

**Card and instrument, as they are.** aifoundry2, card 0. Firmware per E69's 27 Oct reading: release 1.4.0,
BL2 0.22.0. DVFS 600, 700 and 800 MHz at 0.517, 0.568 and 0.618 V; static TDP 65 W; software threshold 65 °C.
**Nothing is set on the card**: no TDP, threshold, clock, voltage, log level or reset. The runner reads `ettelem
config` after every run, with the card lock held and `timeout 10`, and it ends the session unless the TDP and the
threshold both read 65. The session's first and last queries read it too.

**The runner is E64's.** [`run_kspeed.py`](run_kspeed.py) imports
[`../hpl/run_hpl.py`](../hpl/run_hpl.py) and runs it unchanged. It adds two things only:

1. a `--values file:<tile>` run, checked before the session against `kinds.json`;
2. a `--dry` toy card that draws each kind's predicted watts.

So the lock, the other-user checks, `timeout 10`, the sampler, the trace-ring reads, the safety stops and the config
check are E64's code.

**Kernel: E64's, unchanged.** `sparsity_host --test fma --pattern none --values file:<tile>`. Hart 0 of each of the
1,024 minions repeats one 16×16 TensorFMA on a tile pair in its L1 scratchpad. A launch lasts about 0.5 s, and
launches run back to back for `--seconds`. Each op is 546 cycles for fp32 and fp16 and 318 for int8, for 8,192 /
16,384 / 32,768 operations. The binaries are aifoundry2's `build/sparsity_t2`, which E64 and E69 ran: host sha256
`7adadf4f…`, kernel `990807f4…`. The host's `fillValues` reads `file:` as the raw A tile, then the raw B tile,
1,024 bytes each.

**The tiles: Q130(s) revision 2** ([`../kinds/`](../kinds/README.md), `kinds.json` sha256 `9586568f…`, commit
`7d9c0d9e`). The 18 kinds, as the brief named them:

| format | kinds |
|---|---|
| fp16 | zeros, ones, randn, sparse50, smallint, fp8grid, nn_like |
| int8 | zeros, neg_ones, full (= E64's int8 `randn`), smallint, gauss_q, sparse50 |
| fp32 | randn (the anchor to E64), bf16trunc, sparse90, smallint, nn_like |

The runner refuses a session if any tile is not 2,048 bytes or its sha256 is not `kinds.json`'s. A `file:` run
prints the wrong metadata and checks no arithmetic (kinds README §1.5). Its `SPARSITY` lines' `nnz_a`, `a_elems` and
`fp16_one_sided_pairs` describe the discarded random fill, and `result` is `unchecked`. Every statistic of a kind
comes from `kinds.json`, never from those lines.

**The blocks** ([`protocol.json`](protocol.json), order seed 80):

| block | runs | start | load | scores |
|---|---|---|---|---|
| `SMOKE` | fp16 ones, int8 full, fp32 randn, 2 s each | none | one 2 s process | not analysed: it checks the `file:` path on the card |
| `BURST` | 18 kinds × 2 passes, each pass shuffled | die reading ≤ 55 °C | one 6 s process (E64's `LAD` shape) | the burst clock, p800, burst W, die, the burst limit, the kernel's rate, the switching term c |
| `SUS` | 18 kinds, plus fp16 ones, fp32 randn and int8 full again (21 runs), shuffled | die reading ≤ 57 °C | nine back-to-back 8 s processes, about 76 s (E64's `SUS` shape) | the last 40 s: clock, board W, die, rate, the limit labels |

That is 60 runs. Expected card time is about 50 min: E64's 20 `LAD` runs took 5.9 min and its 9 `SUS` runs
15.8 min. The cap is 80 card-minutes for the main session and 90 in all, smoke included.

**Two departures from the brief, named.**

1. **Every kind's burst is run twice, not only the anchors'.** The burst rule compares 18 cells to a 25 MHz bar, and
   a single pass gives no replicate spread. E64's `LAD` ran two passes too, and the cost is about 6 card-minutes.
2. **The sustained replicates are fp16 ones, fp32 randn and int8 full.** fp16 ones is the cell E64-T1 never closes.
   fp32 randn is the named anchor to E64. int8 full is E64's int8 random: the one int8 sustained cell E64 measured
   inside the clamp window (763 MHz), so it is int8's drift check.

**Instruments (E64's).**

- `ettelem sample --every-ms 100` from the gate to the end of the idle tail, **without `--reset-ms`**. A reset
  restarts the PMIC's running average, which the governor's power loop exits on.
- After every run, with the sampler stopped: the service processor's 4 KB trace ring, read with
  [`../hpl/sptrace_full.py`](../hpl/sptrace_full.py). It logs every governor decision with its cause.
- The throttle residencies, and `ettelem config`.
- The kernel's own cycle counters, per ~0.5 s launch.

**Living with the lab's dashboard, as E64 and E69 did** ([`../knob/CHANGE-RECORD.md`](../knob/CHANGE-RECORD.md)).

- The runner holds the card lock `/run/lock/etsoc-shire0.lock` for the whole session.
- The live collector (`tools/lab/live/live-collector.py`) reads a card's temperature only while nobody holds a card
  node or lock on the machine. It probes the lock again just before opening the management node. Its reader is a
  copy of `ettelem` named `lab-monitor`, so the runner's device-process check, which matches `ettelem` by name, does
  not mistake it for a second user of the card.
- The dashboard's `update.sh` card sample gates on `et-who` and `flock -n`.
- `keeper.py` never opens a card.

Nothing of theirs is stopped or killed. If the collector holds the node at the moment a sampler starts, the runner
retries the start, as it always has.

**Etiquette.** The card is claimed in `#community-lab` with one line after this commit is pushed, and the same post
is edited at the release. The runner refuses when another user is logged in or another process holds the card, and
before every launch process. It caps every device process at `timeout 10` and never signals one. It stops on a die
reading of 85 °C, or a board reading over 97 W on three samples.

## Predictions (frozen)

[`predict_kspeed.py`](predict_kspeed.py) builds [`predictions.json`](predictions.json) from committed inputs only. It
refuses unless each input's sha256 is:

- `c5a66cb6…` for Q130(c)'s `predictions.json`;
- `6ffc701b…` for its `amendment-a1.json`;
- `9586568f…` for `kinds.json`;
- `f6bdb19f…` for E64's `results.json`;
- `d430bfab…` for E64's `figures.json`.

It reproduces Q130(c)'s own frozen burst and sustained clocks for all 18 kinds (`checks`: 18/18 and 18/18).

**From watts to a clock.** Q130(c) predicts each kind's switching power W over its type's own zero-data level, on
aifoundry3 at 600 MHz / 521.8 mV. It carries W back to aifoundry2 with its own stated rule (model.py rules 7 and 8):

`c = c_E64(type, zeros) + W / 1.01865`, where 1.01865 = (0.5218 / 0.517)².

`c` is the switching term at 600 MHz / 517 mV in E64's power curve `P_f = B_f + c·s_f`, with
`s_f = (V_f / 0.517)² · f / 600`. That curve carries it to 700 and 800 MHz.

**The predicted clocks.**

- **Burst (primary):** E64's registered governor (`surface_hpl.simulate`: τ 1.3 s, pass 0.24 s, 65 W). It is scored
  over the window it was calibrated on, the mean clock from 1.5 to 6.5 s of a 6 s run.
- **Burst (secondary):** E64-T1 at γ = 3 over the same window, from the run's own launch reading.
- **Sustained:** E64-T1 at γ = 3: E66's leakage law, a die state relaxing toward E64's line `die = 41.88 + 0.4696 °C
  per W` with τ_th 14 s, and a thermal limb at 66 °C. It is scored on the last 40 s of the 76.2 s work, from the
  run's own launch reading. The γ = 2 and γ = 0 arms are tabulated too.

**The limit.**

- `none` when the simulation spends ≥ 90% of the window at 800 MHz;
- otherwise `thermal` when its mean die is ≥ 65.5 °C (Q130(c)'s criterion);
- otherwise `power`.

| kind | c (W) | c 95% | p800 at 58 °C | burst, registered (from c 95%) | burst limit | Q130(c) burst 4–12 s | sustained, T1 γ3 from 57 °C (from c 95%) | Q130(c) sustained | sustained limit | rate at the sustained clock |
|---|---|---|---|---|---|---|---|---|---|---|
| fp16 zeros | 1.39 | 1.39–1.69 | 36.3 | 800 (800–800) | none | 800 | 800 (800–800) | 800 | none | 24.58 TFLOPS |
| fp16 ones | 9.70 | 7.33–12.07 | 52.1 | 800 (800–800) | none | 800 | 745.5 (711–792) | 745 | thermal | 22.91 |
| fp16 randn | 23.28 | 19.96–26.61 | 78.0 | 728.6 (695–767) | power | 715 | 600 (600–625) | 600 | thermal | 18.44 |
| fp16 sparse50 | 16.62 | 9.99–23.26 | 65.3 | 800 (729–800) | none | 794 | 655.7 (600–741) | 656 | thermal | 20.15 |
| fp16 smallint | 21.14 | 13.60–28.68 | 73.9 | 752.4 (676–800) | power | 739 | 614.4 (600–690) | 614 | thermal | 18.88 |
| fp16 fp8grid | 22.44 | 14.15–30.74 | 76.4 | 733.3 (662–800) | power | 715 | 604.2 (600–683) | 604 | thermal | 18.57 |
| fp16 nn_like | 20.42 | 12.47–28.37 | 72.5 | 761.9 (686–800) | power | 752 | 620.4 (600–705) | 621 | thermal | 19.06 |
| int8 zeros | 2.12 | 2.12–2.42 | 37.6 | 800 (800–800) | none | 800 | 800 (800–800) | 800 | none | 84.41 TOPS |
| int8 neg_ones | 2.68 | 2.12–5.04 | 38.7 | 800 (800–800) | none | 800 | 800 (800–800) | 800 | none | 84.41 |
| int8 full | 9.10 | 5.79–12.41 | 51.0 | 800 (800–800) | none | 800 | 757.5 (706–800) | 758 | thermal | 79.93 |
| int8 smallint | 9.12 | 4.03–14.21 | 51.0 | 800 (800–800) | none | 800 | 756.9 (683–800) | 757 | thermal | 79.86 |
| int8 gauss_q | 9.10 | 4.02–14.17 | 50.9 | 800 (800–800) | none | 800 | 757.5 (684–800) | 758 | thermal | 79.93 |
| int8 sparse50 | 8.07 | 3.68–12.47 | 49.0 | 800 (800–800) | none | 800 | 774.9 (705–800) | 774 | thermal | 81.76 |
| fp32 randn | 25.21 | 21.41–29.01 | 81.6 | 704.8 (671–743) | power | 700 | 600 (600–612) | 600 | thermal | 9.22 TFLOPS |
| fp32 bf16trunc | 24.27 | 20.70–27.85 | 79.9 | 714.3 (686–762) | power | 706 | 600 (600–618) | 600 | thermal | 9.22 |
| fp32 sparse90 | 1.89 | 1.57–2.20 | 37.2 | 800 (800–800) | none | 800 | 800 (800–800) | 800 | none | 12.29 |
| fp32 smallint | 18.52 | 16.07–20.96 | 68.9 | 781.0 (762–800) | power | 770 | 638.9 (616–661) | 639 | thermal | 9.82 |
| fp32 nn_like | 17.15 | 14.24–20.06 | 66.3 | 795.2 (767–800) | power | 785 | 650.3 (624–683) | 649 | thermal | 9.99 |

`predictions.txt` prints the same table with the T1 burst and the sustained clock at other launch readings. The
sustained prediction hardly depends on the launch reading (the die converges), so the 57 °C column stands for all.

**What each prediction rests on, and what it does not cover.**

- Q130(c)'s freeze stands, and amendment A1 withdrew its explanation, not its numbers. E80 scores the frozen numbers.
- fp32 randn is **selected-on**, not out of sample (A1.3).
- fp16 and int8 zeros, ones and randn/full are the model's calibration points. Their clocks therefore test only the
  speed path.
- The speed path's own accuracy is E64-T1's out-of-sample 6.2 MHz (8.3 MHz on its five informative cells), not the
  in-sample 3.64 MHz (A1.9).
- The sustained column inherits E69's failed drift check (+2.51 W at one die reading between 23 and 27 Oct).
  Aifoundry2 idles cooler today than on 23 Oct (a 45–46 °C reading at about 21.8 W this morning, against 49–51 °C
  then). If the thermal path moved, the thermal-limited cells move with it. That is what E80-R4 and the post-hoc die
  line are for.
- **int8 is provisional throughout.** Q130(c)'s U_int8 is 0.571 W against E79's measured 1.834 W. A labelled arm with
  E79's value is tabulated (`u_int8_arm`). It lowers the sustained prediction of int8 full, smallint, gauss_q and
  sparse50 by 19–23 MHz, to 734–756 MHz; zeros and neg_ones stay at 800, and every int8 burst stays at 800. The
  frozen column is the prediction; the arm is reported beside it, never instead of it.

## Decision rules (frozen; `reduce_kspeed.py` implements them)

**Definitions.**

- A run's **burst clock** is the mean sampled clock from 1.5 s after the first launch to the end of the work. This is
  E64's `mhz_steady`, the quantity its governor was calibrated on.
- A kind's **burst cell** is the mean of its two passes. Its interval is the two passes.
- A **sustained cell** is the mean clock over the last 40 s of the work, averaged over the kind's runs.
- **Board W and die °C** are the sampler's, over the same spans. p800 is E64's: the median board reading at 800 MHz
  in the first second after the clock first reads 800.
- **TFLOPS / TOPS** are the kernel's own operations over its own wall time:
  - for the burst, over the launches that start 1.5 s or more into the run;
  - for the sustained clock, over the last 40 s (E64's `sus_rate_t`).
- A sustained run's **measured limit** uses E64's R4 per-sample labels over the last 40 s, with A1's and A3's
  readings.
  - `none` if ≥ 90% of the samples read 800 MHz.
  - Otherwise `thermal` if the thermal label holds ≥ 50% of the samples below 800. That label means a die reading
    ≥ 66 °C in the 2 s before, or a last throttle-down line that was thermal.
  - Otherwise `power` if the power label does.
  - Otherwise `unresolved`, which counts as wrong.
- A run's **measured switching term c** follows E64's own method. Its powers at 600/700/800 MHz are referred to a
  58 °C die at 0.442 W/°C (`surface_hpl.powers`) and fitted against E64's registered B_f.

**Primary rules.**

- **E80-R1, burst speed.** The rms over the 18 kinds of (measured burst cell − registered-governor burst
  prediction) is at most **25 MHz** (E69's bar). The T1 burst rms and the rms against Q130(c)'s own 4–12 s numbers
  are reported beside it.
- **E80-R2, the sustained limit.** The three-way limit is called right for at least **80%** of the 18 kinds. A kind
  is right only if every one of its runs carries the predicted label.
- **E80-R3, the fp16 all-ones sustained cell.** The mean of its two runs lies within **15 MHz** of E64-T1's
  prediction at those runs' launch readings (745.5 MHz from 57 °C). A miss is reported as a miss, with its size, the
  E64 measurement (737.1 MHz) and E64-T1's out-of-sample number (754.5 MHz at γ 3, trip 66) beside it.
- **E80-R4, E64's own cells reproduce (the drift check).** E80's fp32 randn burst cell is within **25 MHz** of
  E64's (706 and 713.5 MHz: mean 709.75). So is each of E64's six sustained cells E80 repeats:

  | cell | E64 sustained (MHz) |
  |---|---|
  | fp32 randn | 600.0 |
  | fp16 zeros | 794.4 |
  | fp16 ones | 737.1 |
  | fp16 randn | 600.5 |
  | int8 zeros | 800.0 |
  | int8 full | 763.2 |

  A failure means the card moved since 23 Oct, not that a model did.

**Q130(c)'s own E80 rules, scored exactly as Q130(c) registered them on its frozen numbers.**

- **R7.** The predicted burst (4–12 s) lies within 25 MHz for ≥ 70% of the cells, and every cell predicted at 800
  measures ≥ 790.
- **R8.** The sustained limit, thermal against power, is called right for every cell, and the clock is within 40 MHz
  for ≥ 70%. Q130(c) labels every cell under its trip `power`, so a measured `none` or `power` counts as Q130(c)'s
  `power`.

**Secondary rules.**

- **E80-S1, the power model on aifoundry2.** The measured switching term c lies inside Q130(c)'s converted 95%
  interval for ≥ 70% of the out-of-sample kinds. Excluded: the calibration kinds, the zeros basis, and fp32 randn
  (selected-on).
- **E80-S2, the governor alone.** E64's registered governor, simulated on each burst run's own measured powers,
  reproduces the burst clocks to ≤ 10 MHz rms. E64's in-sample figure is 3.3 MHz.
- **E80-S3, the sustained clock.** The rms of (measured − E64-T1 at γ 3) over the 18 sustained cells is ≤ 15 MHz.

A rule with fewer than 12 cells (R1, R2, R7, R8, S2, S3), 8 kinds (S1), or two fp16-ones runs (R3) is
UNDER-RESOLVED.

**Post hoc, labelled, never a verdict.** E64-T1 is re-run three ways:

- on the measured c instead of the predicted one;
- with the die line refitted on E80's own sustained runs;
- with both.

Together they split a sustained miss into its power-model part and its thermal-path part. The int8 U arm is
reported beside the frozen int8 column.

## What a result fills

Each of the 18 kinds gets these cells of the blog's kinds-of-numbers table:

- burst MHz, sustained MHz;
- TFLOPS or TOPS at each;
- board W (p800, burst mean, sustained mean);
- die °C (burst start and peak, sustained mean);
- the limiting test.

The data goes to [`docs/reports/data/2026-10-31-e80-kinds-speed/`](../../../docs/reports/data/2026-10-31-e80-kinds-speed/).

## Files

| file | what |
|---|---|
| `protocol.json` | the blocks, the tiles, the gates, the safety caps |
| `run_kspeed.py` | the runner: E64's `run_hpl.py`, imported, plus `file:` tiles and a predicted-watts dry card |
| `predict_kspeed.py`, `predictions.json`, `predictions.txt` | the frozen predictions and their console table |
| `reduce_kspeed.py` | the registered reduction (per-run metrics from E64's `reduce_hpl.run_metrics`, unchanged) |

Run, on aifoundry2, from the lab checkout:

```bash
python3 tools/claims-v3/kspeed/run_kspeed.py --protocol tools/claims-v3/kspeed/protocol.json --out build/e80/runs/<s> --dry --only SMOKE   # toy card
python3 tools/claims-v3/kspeed/run_kspeed.py --protocol tools/claims-v3/kspeed/protocol.json --out build/e80/runs/smoke --only SMOKE --max-card-min 5
python3 tools/claims-v3/kspeed/run_kspeed.py --protocol tools/claims-v3/kspeed/protocol.json --out build/e80/runs/s1
python3 tools/claims-v3/kspeed/reduce_kspeed.py <data>/s1 --out <data>/results.json > <data>/reduce.txt
```

## Amendments

- **A1 (Sat 31 Oct 2026, about 12:35 PDT; written after the 36 BURST runs had been reduced and while the SUS block
  ran, with one SUS run, fp16 nn_like, already seen in that partial reduction).** It adds a labelled post-hoc view.
  **No registered rule, threshold, population or verdict changes.**

  *What was seen.* Two of the 36 bursts fell from 800 MHz straight to 600 MHz in mid-launch, with no power or thermal
  line in the governor's trace ring and the work running on at the lower clock:

  | run | at | board W before → during | die |
  |---|---|---|---|
  | int8 neg_ones, pass 1 | 4.2 s | 39.9 → 28.8 W | 57 °C |
  | fp32 nn_like, pass 1 | 5.2 s | 60.2 → 39.2 W | 58 °C |

  For about 1 s each, the ring holds a power-status record in throttle state 0, POWER_IDLE. fp32 nn_like's pass 1
  also sat at 600 MHz for 2.2 s after its start before climbing.

  This is the behaviour [`docs/findings/14-card-behaviour.md`](../../../docs/findings/14-card-behaviour.md) records as
  "A one-second idle reset inside a launch" (E63, 8 of 360 launches): the governor resets as if the card were idle.
  It is neither of its two limits, and neither model has it.

  *What the registered rules make of it.* R7's second clause ("every cell predicted at 800 measures ≥ 790") now hangs
  on int8 neg_ones (777.5 MHz, from 755.1 and 800). E80-S2's governor-only rms carries both runs. R2's three-way label
  counts an `unresolved` cell as wrong, and an idle reset in a sustained run could push a 800-MHz cell below 90%.
  All of that is scored exactly as registered.

  *What is added.* [`posthoc_idle.py`](posthoc_idle.py) finds these episodes from the sampler alone, in every run:

  - a **dip** is a work sample at 600 MHz straight after one at 800 (a power step and a thermal step both go one
    point at a time). It must come more than 1.5 s after its process started and more than 0.3 s before it ended,
    with the die under 65 °C.
  - a **late ramp** is a first 800 MHz sample more than 1.2 s after the process start (E63's measured maximum), while
    the die reads under 65 °C and the board under 65 W.

  It then reports, *beside* the registered numbers:

  - each burst cell without those samples, and R1, R7 and S2 on those means;
  - each sustained run's limit with those samples left out (sampler-only, as A3 of E64);
  - R2 on those limits;
  - how many episodes there were, per kind and in all.
