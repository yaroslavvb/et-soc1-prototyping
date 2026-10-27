# Q129 — the board-to-rail step, rail by rail

Tue 27 Oct 2026 (week 44). **Where the quarter of a multiply-add goes that the minion rail does not carry.**
From committed telemetry only: **no card was run for this**, no card was claimed, nothing was reset or set.

Q128's waterfall takes one random fp32 multiply-add at **5.783 pJ at the board** (E38's registered means, three
cards) and puts **0.75 of it on the minion rail, 4.337 pJ**. That 0.75 is E60's per-flipped-bit `rail_over_board`
(0.7455 and 0.7497), carried across to a per-multiply-add figure E38 measured. The other three rails had never
been read for the multiply-add itself, and the 1.446 pJ between board and rail had no account at all.

## Results

**One random fp32 multiply-add, scaled onto Q128's own 5.783 pJ board figure.** Launch window (board over
[t0+1, t0+3] s, which is the window Q128's board figure is referenced to; rails deconvolved to the same
samples), aifoundry2 and aifoundry3:

| where it goes | pJ | share of the board | card spread (a2 / a3) |
|---|---|---|---|
| **minion rail** | **4.55** | **78.7%** | 4.57 / 4.53 |
| SRAM rail | 0.054 | 0.9% | 0.065 / 0.043 |
| NoC rail | 0.062 | 1.1% | 0.081 / 0.043 |
| the regulators' delivery loss + off-rail logic in step with the rails | 0.86 | 14.9% | 0.88 / 0.83 |
| off-rail, **unattributed** — rails with no meter at all | 0.26 | 4.5% | 0.41 / 0.11 |
| board | 5.783 | 100% | |

So **of Q128's 1.446 pJ board-to-rail step, 1.19 pJ (82%) now has an account** — 2% of the board on the SRAM and
NoC rails, 15% on the regulators and the logic that works in step with the rails — and **0.26 pJ (4.5% of the
board, 0.11–0.41 pJ by card) is on no meter and attributed to nothing.** The unattributed row is the one that
carries the card difference, and the card difference is a temperature difference: aifoundry2 launches 24 °C
hotter, and about two fifths of the board's temperature-dependent power is off the rails (next table but one).
The last two rows are an attribution, from the energy manual's
published fit (`unmetered_fit.json`: unmetered W = 0.188 × minion + 0.034 × SRAM + 0.291 × NoC on aifoundry2,
0.181 / 0.043 / 0.294 on aifoundry3), not a measurement; the first three rows are measured here.

**The minion rail carries more than Q128 gives it, and the direction is consistent.** Measured directly on the
multiply-add, minion/board is **0.788** at the launch window and **0.760** at the end of the run, against Q128's
0.75. Per card, 0.760 → 0.728 (aifoundry2, launching at 81 °C) and 0.815 → 0.792 (aifoundry3, at 57 °C). On
Q128's board figure the minion rail is **4.55 pJ at the launch temperature and 4.39 pJ late**, against the
4.337 pJ the waterfall carries. The whole range of the measurement, 4.33–4.57 pJ, sits inside Q128's own stated
0.70–0.89 rail-ratio spread, so **nothing in Q128 is wrong; it is now measured rather than borrowed, and the
0.75 is at the bottom of what the multiply-add actually shows.**

**Why Q128's 0.75 reads low: E60's rail window.** The board meter is instantaneous; the rails are the PMIC's
first-order running average, τ ≈ 1.05 s, one service-processor pass late. E60 read the board over [t0+1, t0+3) s
and the rail over [t0+2, t0+4) s of a **4 s** run, so its rail difference is attenuated while its board
difference is not. Measured on E38's own 7 s runs, where the same window can be compared with a settled one,
that window returns **0.891 ± 0.002** of a settled step on aifoundry2 and **0.895 ± 0.001** on aifoundry3.
Carried onto E60's own ratios that would put them at 0.836 and 0.842. This is an inference about E60's
reduction, not a re-reduction of E60: it says the direction of the error, and it agrees with the 0.788 measured
here on a window where the filter has nothing left to hide.

**The rail ratio falls as the run heats, and so does the board's leakage correction.** Pooled over every
screened run of a card that heats at least 2.5 °C, power against the die reading inside the run:

| W per °C | board | minion | SRAM | NoC | three rails | off-rail | off-rail share |
|---|---|---|---|---|---|---|---|
| aifoundry2 (81 °C) | +0.725 ± 0.019 | +0.268 ± 0.033 | +0.063 ± 0.001 | +0.120 ± 0.003 | +0.451 | +0.275 | **0.38** (per run 0.37 ± 0.06, n 6) |
| aifoundry3 (57 °C) | +0.358 ± 0.093 | +0.114 ± 0.067 | +0.037 ± 0.001 | +0.063 ± 0.002 | +0.213 | +0.145 | **0.41** (per run 0.90 ± 0.37, n 8) |

**About two fifths of the board's within-run rise is off the three rails.** That is what makes the rail ratio
drop from 0.788 to 0.760 over a 7 s run, and it is a warning about every reduction in this project that corrects
*board* power to a launch temperature with a single slope and then applies a fixed rail ratio: the correction and
the ratio are not independent. The split of that off-rail rise between the unmetered rails' own leakage, the
regulators' loss rising as they heat, and the card's fans is **not separated by this data** (ettelem carries no
fan reading, and E38 ran in September, before the October cooling changes); aifoundry3's per-run share has a wide
interval because its runs heat least.

**Idle, for scale** (fp32_randn's own pre-launch brackets): aifoundry2 board 36.31 W, rails 20.57 W, off-rail
**15.74 W (43%)**; aifoundry3 board 25.78 W, rails 12.69 W, off-rail **13.08 W (51%)**. This reproduces the
published "15.1 W of 31.8 at idle at 73 °C" (`docs/findings/19-observability-and-the-unmetered.md`). Half of idle
being off-rail, and only a fifth of a multiply-add's delta being off-rail, is the same fact from two sides: the
unmetered rails are mostly static.

**The regulators' conversion loss does not separate from off-rail logic — this is the term E77 would settle.**
Over the catalogue's 375 non-DRAM configuration means, the off-rail remainder is **linear in the rails' watts**;
adding a square term in the rails' sum (which is what a regulator's I²R conduction loss would look like at a
fixed rail voltage) is **not resolvable**:

| | minion | SRAM | NoC | per W² | rms |
|---|---|---|---|---|---|
| aifoundry2, linear | 0.1878 | 0.0405 | 0.2670 | — | 0.2659 W |
| aifoundry2, + square | 0.1946 | 0.0422 | 0.2788 | **−0.00055 ± 0.00035** (t −1.57) | 0.2650 W |
| aifoundry3, linear | 0.1808 | 0.0491 | 0.2699 | — | 0.2324 W |
| aifoundry3, + square | 0.1737 | 0.0473 | 0.2580 | **+0.00059 ± 0.00032** (t +1.85) | 0.2313 W |

Two cards on the same firmware give the square term **opposite signs** and improve the rms by 0.001 W, so there
is no quadratic term the catalogue can see over 0–22 W of rail load. The per-rail coefficients are also far too
unequal (0.19 minion against 0.04 SRAM) to be one board-level efficiency, which is the published reading:
the minion coefficient is mostly that regulator's delivery loss, the NoC coefficient is more than a regulator
because the memory shires' unmetered logic works whenever the mesh moves bytes. **What no committed data can do
is split the minion rail's 0.188 into conversion loss and off-rail logic**: the management struct
(`DM_CMD_GET_SP_STATS`) carries each regulator's **output** power and voltage and the board's input power, and no
input-side per-regulator power at all, so the conversion loss is never read directly. E77 below is the cheapest
run that would separate it.

**A sustained cross-check, two clocks** (E64's own telemetry on aifoundry2, long stretches at one clock, idle
from each file's first 2 s, samples only from 3 s after the clock last changed):

| | minion/board, median [range] | off-rail share, median [range] | stretches |
|---|---|---|---|
| 800 MHz, 617–619 mV | 0.717 [0.660–0.755] | 14.9% [10.8–20.5] | 21 |
| 600 MHz, 517 mV | 0.781 [0.691–0.792] | 19.6% [19.1–29.1] | 5 |

The sustained figures bracket the burst ledger — 0.66 to 0.79 against the burst's 0.76–0.82 — which is the useful
part: the ledger is not an artefact of 7 s bursts. The two clocks do **not** separate anything, because pattern,
clock, voltage and rail load all move together: the 600 MHz stretches are the governor holding random data at the
floor, the 800 MHz ones are the lighter patterns, and the one term a voltage change would isolate (a conduction
loss, which costs 1/V² at the same watts) has only two voltages and a confounded workload to work with. That is
the lever **E77** is designed around.

## What it changes

- **Q128 level 3 (board → the rail).** `rail_pJ` 4.337 becomes a measured **4.55 pJ at the launch temperature**
  (4.39 late), with the step below it named: 0.05 SRAM + 0.06 NoC + 0.86 regulators/in-step + 0.26 unattributed.
  The waterfall's "unaccounted against the rail" therefore **grows** from 2.39 pJ to **2.60 pJ** (4.549 − 1.946),
  while "unaccounted against the board" is untouched at 3.837 pJ. This closes a step of the waterfall; it does
  not close the bottom-up gap, and it makes the rail-side gap slightly larger.
- **Q128 §5 and the Levels tab, stop 2 ("the rail at the launch temperature; the regulators").** Answered for the
  rails: 2% of the board on the SRAM and NoC rails, 15% attributed to the regulators and in-step logic, 4.5%
  unattributed. Not answered for the regulators themselves: conversion loss and off-rail logic do not separate in
  any committed data. Stop 2 moves from "missing" to "partly measured, one term needs E77".
- **A caution for every reduction in this project.** A fixed rail ratio plus a board-level leakage correction
  double-count: two fifths of the board's within-run rise is off the metered rails, so a correction applied at
  the board moves the rail ratio by about 0.03 over a 7 s run.
- **aifoundry1-c1 has no rail data in E38.** Its whole campaign is screened out (below). Any figure that reads
  that card's E38 rails as a delta over its pre-launch idle is reading the filter, not the workload.

## Method, and what was screened out

Windows, both with board and rails read from the **same samples**, so no temperature correction stands between
them, and both as differences against the pre-launch idle bracket [t0−2, t0−0.3] s that the registered metric uses:

* **launch** — board over [t0+1, t0+3] s (the registered `p_early` with its dropout rule), rails deconvolved to
  the same window with `tools/ettelem/deconv.py` and each card's own τ. 2.3–3.5 °C above the launch reading.
* **late** — board and rails both over [t1−1, t1] s, raw. Six to seven seconds after the step the rails' filter
  has 0.3% of it left, so no deconvolution is needed; the deconvolution's own closure check is that at the launch
  window a quiet pattern's deconvolved rail (15.040 W) matches its settled late reading (15.032 W) to 8 mW.

Screens, declared in the script and counted in the output:

| | aifoundry2 | aifoundry3 | aifoundry1-c1 |
|---|---|---|---|
| runs kept | **54** of 92 | **98** of 99 | **0** of 92 |
| screened out: the idle bracket's rails not settled | 38 | 1 | 92 |

**S2**, the screen that matters: the idle bracket's minion rail must agree within 0.15 W between [t0−5, t0−3] and
[t0−2, t0−0.3], and the strict start's approach must be at least 6 s (six time constants). aifoundry1-c1 fails it
everywhere — its approach is 2.3 s at the tenth percentile and its preheat runs to within 2 s of the launch, so
the minion rail enters a run 10–20 W above idle and falls through it; its fp32_zeros rail delta reads **−1.5 W**,
which is the filter. aifoundry2 loses 38 runs to it (approach median 15.6 s but minimum 4.9 s), aifoundry3 one
(approach median 39.9 s). **S1** is E38's own keep rule (every launch ok, `mhz.minion` 600 throughout). **S3**
drops the board's random 5–12 W meter dips (E62) from every board window by the registered rule, samples more
than 2 W below that window's median — applied to the idle and late windows too, which the registered reduction
applies to the early window only.

Departures from what a card run would have given: none were possible — this is existing data, so there was no
pre-registration, and every number here is a post-hoc reduction of runs made for other questions. The three-card
mean is a two-card mean. E38's cards launch 23 °C apart, which is why the card spread is given in every row
rather than averaged away.

## Files

* `rail_ledger.py` — the whole reduction. `python3 docs/reports/data/2026-10-27-q129-rail-ledger/rail_ledger.py .
  --out docs/reports/data/2026-10-27-q129-rail-ledger/rail-ledger.json --text .../reduce.txt` (numpy only;
  imports `tools/ettelem/deconv.py`).
* `rail-ledger.json` — every number, per card, per configuration, both windows, with the per-rail drift, the idle
  split, E60's measured window attenuation, the load-dependence fits and E64's sustained stretches.
* `reduce.txt` — the printed tables.
* `E77-PLAN.md` — the 20-card-minute run that would separate the regulators' conversion loss. **Not run.**

## Related

* `docs/reports/data/2026-10-27-matmul-to-transistor/` — Q128's waterfall and its `data.json`.
* `docs/reports/data/2026-10-27-transistor-ledger/` — `up_to_the_board.per_random_fp32_multiply_add.rail_pJ`, the
  4.337 this replaces.
* `docs/findings/14-card-behaviour.md`, "The telemetry, and what each number really is" — what each rail number is.
* `docs/findings/19-observability-and-the-unmetered.md` — the meter chain and the published off-rail attribution.
