# Q129 — the board-to-rail step, rail by rail

Tue 27 Oct 2026 (week 44). **Where the quarter of a multiply-add goes that the minion rail does not carry.**
From committed telemetry only: **no card was run for this**, no card was claimed, nothing was reset or set.

Q128's waterfall takes one random fp32 multiply-add at **5.783 pJ at the board** (E38's registered means, three
cards) and puts **0.75 of it on the minion rail, 4.337 pJ**. That 0.75 is E60's per-flipped-bit `rail_over_board`
(0.7455 and 0.7497), carried across to a per-multiply-add figure E38 measured. The other three rails had never
been read for the multiply-add itself, and the 1.446 pJ between board and rail had no account at all.

> **Corrected 27 Oct 2026, same day.** The first version of this directory (commit `68c50c37`) reported
> **uncorrected** window deltas and then multiplied every row by 5.783/6.176 to land on Q128's board figure.
> That treats an additive leakage term as a proportional scale, and it is wrong in a direction that matters.
> The headline moves from "a measured 4.549 pJ" to **4.77 pJ with a 4.55–4.95 pJ band**; the SRAM and NoC rows
> are **withdrawn** as per-MAC switching energies; "0.26 pJ on no meter and attributed to nothing" becomes
> **the off-rail fit's residual**, which is negative on one of the two cards. Every change is listed under
> [Corrections](#corrections-to-commit-68c50c37) with the number that forced it.

## The footing, first, because it moves the headline

A window delta `p_window − p_idle` carries the die heating that happened *inside* the window. Neither reference
this ledger is transferred onto does. E38's registered metric is `p_early − leak × (t_early − t_launch) −
p_before`, with `leak` **0.81 W/°C** on aifoundry2 and **0.55** on aifoundry3; the catalogue's `over_idle_w`
carries the same correction (`leak_correction_w`, mean 0.352 W) while its `rails_over` does not, so the
published off-rail fit is calibrated against a *corrected* board. The whole gap between this ledger's board
figure and the registered one is that correction:

| | uncorrected | − leak × ΔT | E38 registered |
|---|---|---|---|
| aifoundry2 | 6.421 pJ | 5.836 | 5.920 |
| aifoundry3 | 5.930 pJ | 5.513 | 5.369 |
| two-card mean | 6.176 | **5.674** | 5.645 (0.5% residual) |

The correction is **additive and is not shared out in proportion to the rows**: the minion rail carries only
32–37% of the board's within-run temperature rise (measured below), so a proportional scale takes too much off
the minion rail and too little off the off-rail remainder. Three footings are therefore computed and all three
published, and the choice between them is the largest single uncertainty in this directory:

* **uncorrected** — the raw delta. A **lower bound** on the rail's share.
* **drift_split** — the registered correction taken off the board and distributed over minion / SRAM / NoC /
  off-rail by **their own measured drift slopes**. The **central estimate**: the only one consistent both with
  the registered metric and with the measured fact that the rails do not carry all of the rise.
* **board_only** — the correction taken off the board alone, rails left raw. Literally what E38 does, because
  E38 has no rail numbers. An **upper bound** on the rail's share.

## Results

**One random fp32 multiply-add, launch window** (board over [t0+1, t0+3] s, the window Q128's board figure is
referenced to; rails deconvolved to the same samples), two cards, each row transferred onto Q128's 5.783 pJ:

| where it goes | central (drift_split) | lower (uncorrected) | upper (board_only) |
|---|---|---|---|
| **minion rail** | **4.77** | 4.55 | 4.95 |
| SRAM rail | 0.011 | 0.054 | 0.059 |
| NoC rail | −0.019 | 0.062 | 0.067 |
| regulators' delivery loss + off-rail logic in step with the rails | 0.875 | 0.859 | 0.935 |
| the off-rail fit's **residual** | 0.142 | 0.259 | −0.230 |
| board | 5.783 | 5.783 | 5.783 |
| minion / board | **0.825** | 0.787 | 0.856 |

**The minion rail carries more than Q128 gives it, and more than the first version of this ledger said.**
On the central footing it is **4.77 pJ**, band **4.55–4.95 pJ** over the leakage treatment, against the 4.337 pJ
the waterfall carries. The band is the honest interval and it is dominated by the footing, not by the data:

* **footing** 4.55 / **4.77** / 4.95 pJ (ratio 0.787 / 0.825 / 0.856);
* **card spread**, on the central footing: aifoundry2 **4.62**, aifoundry3 **4.93** pJ (ratios 0.799 and 0.853);
* **the leakage slope itself**, as a labelled sensitivity: the registered 0.81/0.55 gives 4.774; this ledger's
  own measured within-run board slope (0.725 / 0.358) gives 4.723; **E66's measured aifoundry2 idle slope,
  0.294 W/°C**, in place of 0.81 gives 4.690 — an 0.08 pJ spread, far smaller than the distribution choice;
* **the third card is assumed, not measured.** The 5.783 pJ denominator is a **three-card** registered mean
  (a2 5.920, a3 5.369, aifoundry1-c1 6.058); every ratio here is a **two-card** measurement, because
  aifoundry1-c1's whole E38 campaign is screened out (below). If its ratio equalled aifoundry2's — the
  conservative direction, since it launches as hot — the figure falls to **4.73 pJ (−0.05)**.

The whole range, 4.55–4.95 pJ (ratio 0.787–0.856), sits inside Q128's own stated 0.70–0.89 rail-ratio spread,
so **nothing in Q128 is contradicted; the 0.75 is at the bottom of what the multiply-add actually shows.**

**The SRAM and NoC rows are withdrawn as per-MAC switching energies.** Each small rail's launch-window delta is
the same size as its *own* leakage rise inside that window:

| | SRAM | NoC | minion |
|---|---|---|---|
| aifoundry2: the window's own leakage rise, as a share of the measured delta | 66% | **100%** | 4% |
| aifoundry3 | 61% | **103%** | 2% |

On the central footing they are **0.011 pJ and −0.019 pJ** — a negative energy, which is the correct reading of
"not separable from the window's own heating". What survives is a bound: **together the SRAM and NoC rails carry
at most 0.13 pJ of a 5.8 pJ multiply-add, 2.2% of the board** (the widest of the three footings; the central one
puts them at −0.008 pJ), and that is all this data can say about them.

**The off-rail remainder: a fit residual, not an unmetered energy.** The published attribution
(`unmetered_fit.json`: unmetered W = 0.188 × minion + 0.034 × SRAM + 0.291 × NoC on aifoundry2, 0.181 / 0.043 /
0.294 on aifoundry3) puts **0.875 pJ** of the off-rail remainder on the regulators' delivery loss plus the
unmetered logic that works in step with the rails. What is left over — 0.142 pJ on the central footing — is
**the residual of that fit**, and three facts say it must not be called energy on no meter:

* **the window's own off-rail heating explains most of it**: 0.198 pJ of aifoundry2's 0.440 pJ residual (45%)
  and 0.110 of aifoundry3's 0.113 (**97%**) on the uncorrected footing. This view is computed by the script
  (`offrail_split.*.temperature`) and the first version never reported it;
* **it changes sign across sibling configurations of the same pattern on the same card**: on aifoundry3,
  fp32_randn +0.113, fp32_randn_16 −0.133, fp32_randn_8 −0.251 pJ (1,024 / 512 / 256 harts); on aifoundry2
  +0.440 / +0.203 / +0.070. Over the configurations above 1 pJ it runs −0.251 to +0.440 pJ and is **negative in
  12 of 16 on aifoundry3**;
* **it changes sign with the footing**: +0.259 uncorrected, +0.142 central, **−0.230** on the board-only
  footing, and −0.010 on aifoundry3 alone on the central footing.

So the honest statement is: **the board-to-rail step is smaller than Q128 assumed — 1.01 pJ against 1.45 pJ,
because the rail is measured bigger — and the published fit accounts for 0.88 pJ of it. The 0.14 pJ left is the
fit's residual, consistent with zero and with the window's own heating.** The first version's "82% of the step
now has an account" and "4.5% of the board is on no meter and attributed to nothing" are both withdrawn.

**The rail ratio's fall over a run was the footing, not the rail.** The first version reported the ratio falling
0.788 → 0.760 from the launch window to the end of the run. On the corrected footing it is **near-flat**:

| footing | ratio, launch window | ratio, late | change over ~7 s |
|---|---|---|---|
| uncorrected | 0.787 | 0.758 | **−0.029** |
| **central (drift_split)** | **0.825** | **0.820** | **−0.005** |
| board_only | 0.856 | 0.873 | +0.017 |

So the apparent fall is the *uncorrected* window's own heating, and distributing that heating by the measured
drift slopes removes almost all of it. That is a **consistency check on the correction itself**: an estimate of
the rail at the launch temperature should not depend on which window it was measured in, and on the central
footing it very nearly does not (per card, aifoundry2 0.799 → 0.789, aifoundry3 0.853 → 0.854). The two bounding
footings move it in opposite directions, which is what bounds mean.

**What the drift measurement does say, and it is the warning worth carrying.** Pooled over every screened run of
a card that heats at least 2.5 °C, power against the die reading inside the run, with the standard errors
**propagated** (the first version left them null):

| W per °C | board | minion | SRAM | NoC | three rails | off-rail | off-rail share |
|---|---|---|---|---|---|---|---|
| aifoundry2 (81 °C) | +0.725 ± 0.019 | +0.268 ± 0.033 | +0.063 ± 0.001 | +0.120 ± 0.003 | +0.451 ± 0.033 | +0.275 ± 0.038 | **0.38 ± 0.05** |
| aifoundry3 (57 °C) | +0.358 ± 0.093 | +0.114 ± 0.067 | +0.037 ± 0.001 | +0.063 ± 0.002 | +0.213 ± 0.068 | +0.145 ± 0.115 | **0.41 ± 0.34** |

**A third to three quarters of the board's within-run rise is off the three rails** — that is the claim the data
supports, and no more:

* aifoundry2 **0.38 ± 0.05** is firm, and the per-run estimator agrees (0.37 ± 0.06, n 6);
* aifoundry3 **0.41 ± 0.34** is not. Its per-run estimator gives **0.90 ± 0.37**, whose 1σ range excludes 0.41,
  and its minion slope (+0.114 ± 0.067) is 1.7σ. The first version's "only the pooled share (0.41) is firm" is
  the opposite of the truth and is withdrawn;
* over defensible body windows (start at t0+1.5 / 2.5 / 3.5 s, ≥ 1.0 °C rise) the share moves **0.46 / 0.49 /
  0.34** on aifoundry2 and **0.60 / 0.47 / 0.76** on aifoundry3 — so **0.34–0.76** over window choices;
* the figure depends on the deconvolution. On the **raw** rails over the same window the share is **−1.92** and
  **−4.79**, because 24% of a 22 W step is still unsettled at t0+1.5 s and the deconvolution is removing a ramp
  about 6× the leakage signal. That is a bound on how much the deconvolution carries, not an alternative
  reading, and it is why this split needs a dedicated run to settle.

The direction is what matters and it is robust: **a reduction that corrects *board* power to a launch
temperature with a single slope and then applies a fixed rail ratio double-counts**, because a third or more of
what the correction removes was never on the metered rails. The size of that error is the gap between the
footings in the table above — **0.04 in the ratio at the launch window (0.787 against 0.825), 0.23 pJ on a
5.8 pJ multiply-add** — and it is the whole reason this directory publishes three footings instead of one.
The split of the off-rail rise between the unmetered rails' leakage, the regulators' loss rising as they heat,
and the card's fans is **not separated by this data** (ettelem carries no fan reading, and E38 ran in September,
before the October cooling changes).

**Idle, for scale** (fp32_randn's own pre-launch brackets): aifoundry2 board 36.31 W, rails 20.57 W, off-rail
**15.74 W (43%)**; aifoundry3 board 25.78 W, rails 12.69 W, off-rail **13.08 W (51%)**. The published figure is
"15.1 W of 31.8 at idle at 73 °C" (47%, `docs/findings/19-observability-and-the-unmetered.md`); 43% and 51%
**bracket** it rather than reproduce it. Half of idle being off-rail, and only a fifth of a multiply-add's delta
being off-rail, is the same fact from two sides: the unmetered rails are mostly static.

**The regulators' conversion loss does not separate from off-rail logic — this is the term E77 would settle.**
Over the catalogue's 375 non-DRAM configuration means (all at 600 MHz, so the test is correctly specified at a
fixed rail voltage), the off-rail remainder is **linear in the rails' watts**; adding a square term in the
rails' sum (which is what a regulator's I²R conduction loss would look like) is **not resolvable**:

| | minion | SRAM | NoC | per W² | rms |
|---|---|---|---|---|---|
| aifoundry2, linear | 0.1878 | 0.0405 | 0.2670 | — | 0.2659 W |
| aifoundry2, + square | 0.1946 | 0.0422 | 0.2788 | **−0.00055 ± 0.00035** (t −1.57) | 0.2650 W |
| aifoundry3, linear | 0.1808 | 0.0491 | 0.2699 | — | 0.2324 W |
| aifoundry3, + square | 0.1737 | 0.0473 | 0.2580 | **+0.00059 ± 0.00032** (t +1.85) | 0.2313 W |

Two cards on the same firmware give the square term **opposite signs** and improve the rms by 0.001 W, so there
is no quadratic term the catalogue can see over 0–22 W of rail load. The per-rail coefficients are also far too
unequal (0.19 minion against 0.04 SRAM) to be one board-level efficiency, which is the published reading: the
minion coefficient is mostly that regulator's delivery loss, the NoC coefficient is more than a regulator
because the memory shires' unmetered logic works whenever the mesh moves bytes. **What no committed data can do
is split the minion rail's 0.188 into conversion loss and off-rail logic**: the management struct
(`DM_CMD_GET_SP_STATS`) carries each regulator's **output** power and voltage and the board's input power, and
no input-side per-regulator power at all, so the conversion loss is never read directly. E77 is the cheapest run
that would separate it.

**A sustained cross-check, two clocks** (E64's own telemetry on aifoundry2, long stretches at one clock, idle
from each file's first 2 s, samples only from 3 s after the clock last changed):

| | minion/board, median [range] | off-rail share, median [range] | stretches |
|---|---|---|---|
| 800 MHz, 617–619 mV | 0.717 [0.660–0.755] | 14.9% [10.8–20.5] | 21 |
| 600 MHz, 517 mV | 0.781 [0.691–0.792] | 19.6% [19.1–29.1] | 5 |

These are **raw sustained readings on their own footing** — no launch window, no deconvolution and no leakage
correction, because a sustained stretch has no launch temperature to be corrected to. So the like-for-like
comparison is against the **uncorrected** burst row at the same clock, and it is close: sustained 600 MHz gives
**0.781** against the burst ledger's uncorrected **0.787**. That agreement is the useful part — **the ledger is
not an artefact of 7 s bursts.** Both sit below the corrected 0.825 for the same reason the uncorrected burst
row does: neither has the window's heating removed. The 800 MHz row (0.717) is a different operating point
rather than a check on the same one.

The two clocks do **not** separate anything, because pattern, clock, voltage and rail load all move together:
the 600 MHz stretches are the governor holding random data at the floor, the 800 MHz ones are the lighter
patterns, and the one term a voltage change would isolate has only two voltages and a confounded workload to
work with. That is the lever **E77** is designed around.

**E60's rail window, measured — and why Q128's 0.75 reads low.** The board meter is instantaneous; the rails are
the PMIC's first-order running average, τ ≈ 1.05 s, one service-processor pass late. E60 read the board over
[t0+1, t0+3) s and the rail over [t0+2, t0+4) s of a **4 s** run, so its rail difference is attenuated while its
board difference is not. Measured on E38's own 7 s runs, that window returns **0.891 ± 0.002** of a settled step
on aifoundry2 and **0.895 ± 0.001** on aifoundry3. **E60 ran on aifoundry3** (`transistor-ledger.json`:
"aifoundry3 at 600 MHz and 521.9 mV"), so its own attenuation is 0.8947, and carried onto E60's ratios that
would put them at **0.833 and 0.838** — not the 0.836/0.842 the first version printed, which used aifoundry2's
figure. Two caveats, both one-sided:

* **this is an upper bound.** Two further biases in E60's own reduction push the same way and are not removed
  here: its board is the leakage-corrected `p80` while its rail is raw, and its rail window sits 1 s later and
  hotter than its board window. Both raise E60's measured ratio, so dividing by the window attenuation alone
  over-corrects.
* **one time constant does not explain every rail.** The same window on the same runs returns **0.539 ± 0.005**
  on the NoC rail, which a single τ ≈ 1.05 s shared by all three rails cannot produce. The τ picture is
  incomplete, and that is a reason to confirm this against E60's own harness before restating any published
  number of E60's.

It remains **an inference about E60's reduction, not a re-reduction of E60**: it says the direction of the
error, and it agrees with the 0.79–0.86 measured here on a window where the filter has nothing left to hide.

## What it changes

* **Q128 level 3 (board → the rail).** `rail_pJ` 4.337, which was E60's per-flipped-bit ratio carried across,
  becomes a **measured 4.77 pJ [4.55–4.95]** at the launch window, 4.74 pJ late. The step below it falls from
  1.446 pJ to **1.01 pJ**, of which the published fit accounts for 0.88 pJ (the regulators' delivery loss plus
  logic in step with the rails); the SRAM and NoC rails are at most 0.13 pJ together and not separable from the
  window's own heating; 0.14 pJ is the fit's residual, consistent with zero.
* **The bottom-up gap against the rail GROWS**, from 2.39 pJ to **2.83 pJ** (4.774 − 1.946), band 2.60–3.00.
  "Unaccounted against the board" is untouched at **3.837 pJ**. This closes a step of the waterfall; it does
  not close the bottom-up gap, and it makes the rail-side gap larger.
* **Q128 §5 and the Levels tab, stop 2 ("the rail at the launch temperature; the regulators").** Partly
  answered, and the wording matters: every number here is at the **launch window**, which is 2.3–3.5 °C above
  the launch *reading*. On the central footing that window's own heating is removed from each row, so the
  corrected rows are the best available estimate *at the launch temperature* — but by correction, not by
  measurement, and the correction's distribution is the 4.55–4.95 band. **Stop 2's rail half moves from
  "missing" to "measured at the launch window, corrected to the launch temperature with a ±0.2 pJ band"; its
  regulator half stays missing**, because conversion loss and off-rail logic do not separate in any committed
  data. E77 is the run that would separate them.
* **A caution for every reduction in this project.** A fixed rail ratio plus a board-level leakage correction
  double-count: a third or more of the board's within-run rise is off the metered rails.
* **aifoundry1-c1 has no rail data in E38.** Its whole campaign is screened out (below). Any figure that reads
  that card's E38 rails as a delta over its pre-launch idle is reading the filter, not the workload, and its
  published rail attribution rests on the catalogue alone.

## Method, and what was screened out

Windows, both with board and rails read from the **same samples**, so no temperature correction stands between
them, and both as differences against the pre-launch idle bracket [t0−2, t0−0.3] s that the registered metric
uses:

* **launch** — board over [t0+1, t0+3] s (the registered `p_early` with its dropout rule), rails deconvolved to
  the same window with `tools/ettelem/deconv.py` and each card's own τ. 2.3–3.5 °C above the launch reading.
* **late** — board and rails both over [t1−1, t1] s, raw. Six to seven seconds after the step the rails' filter
  has 0.3% of it left, so no deconvolution is needed. The deconvolution's own closure check: at the launch
  window a quiet pattern's deconvolved minion rail (15.042 W on aifoundry2, 9.611 on aifoundry3) matches its
  settled late reading (15.024 and 9.618) to **17 mW and −7 mW**. Both inputs are in `rail-ledger.json`
  (`per_config.fp32_zeros.abs_w`).

Screens, declared in the script and counted in the output (`cards.*.screened_out` and `screen_evidence`):

| | aifoundry2 | aifoundry3 | aifoundry1-c1 |
|---|---|---|---|
| runs kept | **54** of 92 | **98** of 99 | **0** of 92 |
| S2, settling leg alone | 37 | 1 | **72** |
| S2, both legs | 1 | 0 | **20** |
| S2, approach leg alone | 0 | 0 | **0** |

**S2**, the screen that matters: the idle bracket's minion rail must agree within 0.15 W between [t0−5, t0−3]
and [t0−2, t0−0.3], **and** the strict start's approach must be at least 6 s (six time constants). aifoundry1-c1
fails it everywhere, and the leg that fires is the **settling** leg, not the approach — 72 of 92 on settling
alone, 20 on both, **none on the approach alone** (its approach is 3.1 s at the tenth percentile and 2.3 s at
the minimum, but 78% of its runs clear the 6 s bar). Its preheat runs to within 2 s of the launch, so the minion
rail enters a run far above idle — the far bracket sits **20.5 W above the early window** — and falls through
it, which makes a rail delta negative on a pattern that draws power: its **fp32_zeros minion delta reads −6.6 W
raw and −6.9 W deconvolved** (per pass −2.9 to −9.6) against a board delta of −0.1 W. **S1** is E38's own keep
rule (every launch ok, `mhz.minion` 600 throughout). **S3** drops the board's random 5–12 W meter dips (E62)
from every board window by the registered rule, samples more than 2 W below that window's median — applied to
the idle and late windows too, which the registered reduction applies to the early window only.

Departures: **none were possible** — this is existing data, so there was no pre-registration, and every number
here is a post-hoc reduction of runs made for other questions. The three-card mean is a two-card mean. E38's
cards launch 23 °C apart, which is why the card spread is given for every headline figure rather than averaged
away. The headline configuration rests on **3 of 4 passes on aifoundry2** (fp32_randn_16 on one pass) and 4 of 4
on aifoundry3. The drift split rests on **6 heating runs on aifoundry2 and 8 on aifoundry3**.

## Corrections to commit `68c50c37`

Found by this workflow's verification pass the same day; every one is a desk correction of a reduction, a
README figure or a label, and no card was touched for any of them.

| what was wrong | what it is now |
|---|---|
| **Critical.** Uncorrected deltas scaled proportionally onto Q128's corrected board figure | three footings computed and published; `footings` in the JSON; minion **4.77 pJ [4.55–4.95]**, not "a MEASURED 4.549" |
| "the rail ratio falls as the run heats, 0.788 → 0.760" presented as a property of the rail | the fall is the **uncorrected footing's** own window heating; on the central footing the ratio is near-flat (0.825 → 0.820), which is a consistency check on the correction |
| SRAM 0.054 and NoC 0.062 pJ given as per-MAC switching energies | withdrawn: 61–66% and 100–103% of each delta is the window's own leakage rise; 0.011 and −0.019 pJ corrected, reported as a ≤0.13 pJ bound |
| "0.26 pJ is on no meter and attributed to nothing"; "82% of the step has an account" | the **off-rail fit's residual**: the temperature view (45% / 97%) and the −0.25…+0.44 pJ configuration spread are now reported, both withdrawn |
| No interval on any headline number; a two-card ratio on a three-card board | band for footing, card spread, leakage slope and the unmeasured third card; the mixed denominator stated in the table |
| "38–41% … only the pooled share (0.41) is firm" | **a2 0.38 ± 0.05, a3 0.41 ± 0.34**, 0.34–0.76 over window choices, raw-rail sensitivity reported, "firm" withdrawn |
| No labelled leakage sensitivity (CONTEXT §2 item 3); E66's 0.294 W/°C never used | `leak_slope_sensitivity`: registered / measured within-run / E66 idle → 4.774 / 4.723 / 4.690 pJ |
| E77-PLAN: arms matched by the clock ratio alone; E62-CAL's refuted 800 MHz board law | arm B rebuilt at **0.52 × arm A** harts; a measured 600 MHz **minion-rail** law from this ledger |
| a1-c1's screen: "−1.5 W", "2.3 s at the tenth percentile", approach named as the cause | **−6.6 W raw / −6.9 W deconvolved**, p10 **3.1 s** (min 2.3), the **settling** leg named; all of it in `screen_evidence` |
| E60 inference used aifoundry2's attenuation; no caveats; NoC counterexample omitted | **0.8947** (aifoundry3's), presented as an **upper bound** with both biases named, NoC's 0.539 shown |
| "late 4.385 pJ" labelled as an energy; "reproduces the published 15.1 W"; closure "8 mW" | labelled as a **ratio transfer** (measured late minion is 4.94 pJ uncorrected at a 6.52 pJ late board); "brackets"; **17 mW / −7 mW** with both inputs in the JSON |
| Stop 2 claimed measured "at the launch temperature" | stated as measured at the launch **window** and corrected to the launch temperature with a band |

## Files

* `rail_ledger.py` — the whole reduction, including the three footings. Needs **numpy**
  (`/usr/bin/python3` on a stock Mac has it; a bare `python3` may not):
  `/usr/bin/python3 docs/reports/data/2026-10-27-q129-rail-ledger/rail_ledger.py . --out
  docs/reports/data/2026-10-27-q129-rail-ledger/rail-ledger.json --text .../reduce.txt`. Imports
  `tools/ettelem/deconv.py`. Runs in about 12 s.
* `rail-ledger.json` — every number, per card, per configuration, both windows, all three footings, with the
  per-rail drift and its intervals, the body-window and raw-rail sensitivities, the screen evidence, the idle
  split, E60's measured window attenuation, the load-dependence fits, the 600 MHz hart law and E64's stretches.
* `reduce.txt` — the printed tables.
* `E77-PLAN.md` — the 20-card-minute run that would separate the regulators' conversion loss. **Not run.**

## Related

* `docs/reports/data/2026-10-27-matmul-to-transistor/` — Q128's waterfall and its `data.json`.
* `docs/reports/data/2026-10-27-transistor-ledger/` — `up_to_the_board.per_random_fp32_multiply_add.rail_pJ`,
  the 4.337 this replaces.
* `docs/reports/data/2026-10-27-e66-idle-long/` — aifoundry2's measured idle leakage slope, 0.294 W/°C.
* `docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/` — the idle-bracketed hart ladder, and why E62's
  5.80 W offset is not on the card.
* `docs/findings/14-card-behaviour.md`, "The telemetry, and what each number really is" — what each rail number
  is.
* `docs/findings/19-observability-and-the-unmetered.md` — the meter chain and the published off-rail attribution.
