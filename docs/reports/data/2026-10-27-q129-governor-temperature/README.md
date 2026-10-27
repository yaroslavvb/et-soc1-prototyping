# Q129(a2) — the governor's temperature term, and every aifoundry2 per-bit price on one leakage slope

*Desk work, Tue 27 Oct 2026 (week 44), 13:5x–15:xx PDT. **No card was touched and no governor was moved.**
Every number below is a re-reduction or a model fit on data already committed in this repo. Two items:
(1) the aifoundry2 per-flipped-bit prices that had not yet been re-reduced at E66's measured idle leakage
slope, as labelled sensitivities; (2) a new model version of E64's governor surface that carries leakage's
temperature dependence.*

> **Amended 27 Oct ~15:0x PDT, after Q129's verifier.** Fifteen faults were raised against the 14:24 draft
> and all fifteen are addressed here; nothing needed a card. The two that changed a conclusion:
> **(i)** the headline said the fp32 all-ones miss *closes*, quoting one of eight (γ, trip) pairings of two
> parameters this report itself calls unidentified — it is now stated as the full surface, and the Horace
> Hub's Levels-tab line stays **open**; **(ii)** the trip sensitivity this README promised had never been
> run on the card model — it is run, published at both trips, and it is material. Nine wording and label
> faults and four code faults are listed in [Fixed after review](#fixed-after-review) with what each one
> moved. The frozen E69 predictions are byte-identical after every correction: that check is below.

## Results first

**1. Every aifoundry2 per-flipped-bit price, at its own registered leakage slope and at E66's measured
0.2936 W/°C** ([`per-bit-band.txt`](per-bit-band.txt), [`per-bit-band.json`](per-bit-band.json)):

| source | item | registered | its slope | at 0.2936 W/°C | change |
|---|---|---:|---:|---:|---:|
| E60 | `lq`, per designed flipped B bit | 121.272 ± 0.613 fJ | 0.442 | **123.006 ± 0.767 fJ** | +1.4% |
| E60 | `lq`, per bus flip (RTL) | 79.516 ± 0.403 | 0.442 | 80.653 ± 0.503 | +1.4% |
| E60 | `lq`, per net toggle (RTL) | 0.338 ± 0.004 | 0.442 | 0.345 ± 0.003 | +2.2% |
| E60 | `e_in`, per x-in port bit | 28.662 ± 0.384 | 0.442 | 29.204 ± 0.405 | +1.9% |
| E60 | `ord` pos 0, max-flip − Gray | 1.291 ± 0.009 W | 0.442 | 1.285 ± 0.010 W | −0.5% |
| E60 | `ord` pos 19, max-flip − Gray | 1.311 ± 0.131 W | 0.442 | 1.479 ± 0.071 W | +12.8% |
| E63 s1 | TOP / MID / TOP2 per designed B bit | 154.04 / 121.72 / 154.44 | **0.000** | 147.87 / 116.49 / 147.06 | −4.0 / −4.3 / −4.8% |
| E63 s2 | TOP / MID / TOP2 per designed B bit | 151.70 / 120.26 / 152.38 | **0.000** | 148.34 / 120.26 / 148.80 | −2.2 / 0.0 / −2.3% |
| E68 | `sm_lo12` … `sm_e64` (9 items) | 112.8–282.5 | 1.508 | 123.2–276.4 | −9.8 to +17.9% |

E68's column is **its own 0.294 column**, headed "E66 p11 cooling 51–58 C" in that file: its table has no
0.2936 column and the 0.0004 W/°C difference is below E68's last published digit (under 0.01 fJ on a 136 fJ
price). E63's rows use the dT measured on `minshire[0]`, the single sensor E66's slope is defined on; the
same arithmetic on E63's own die column (the mean of three sensors) gives 149.34 / 116.37 / 148.80 and
146.68 / 120.17 / 148.49 — a ±1.5 fJ sensor sensitivity, carried as a second column
(`e66_fJ_other_sensor`) and discussed below.

**The band.** On one slope, the whole-word "per designed flipped B bit" prices measured on this card lie
between **116.5 and 148.8 fJ** (116.4–149.3 on the other die variable), and E68's stage-resolved prices for
named bit groups span **123.2–276.4 fJ** — low mantissa 135.9, high mantissa 194.4, split 216.4,
exponent-64 276.4. The nine mantissa-flip prices from the three experiments (E60's `lq`, E63's six camera
blocks, E68's `sm_lo12` and `sm_sgnlo`) spread **13.6% → 12.2%** of their midpoint when they are put on one
measured slope instead of three different ones: 117.5–154.4 fJ about 136.0 becomes 116.5–148.8 about 132.7.
Both spreads are printed by [`band.py`](band.py); that is the whole claim, and it is a modest one.

**Two things the re-reduction found that are not just a number moving:**

- 🛑 **E60's own pass gate moves with the slope.** `reduce_hl.py` sets a pass aside when its `anchor_pi`
  drift exceeds 0.3 W *after* the leakage correction. At 0.2936 W/°C, E60's pass 1 drifts +0.380 W and is set
  aside, so the registered gate re-applied keeps 8 passes and 143 of 180 runs instead of 9 and 160. At
  **1.508 W/°C — the slope E68's registered `--leak auto` used — every one of E60's ten passes fails the gate
  and nothing survives at all.** Both pass-gate modes are therefore published side by side: `live` (the gate
  re-applied at the new slope) and `frozen` (the registered nine-pass set held, so only the correction
  changes). For the `lq` prices they differ by 0.03%; for the `ord` pos 19 contrast they differ by 8%,
  because that contrast leans on the pass the gate removes.
- 🛑 **E63's published per-flip prices carry no leakage correction at all.** Its price is a paired same-lap
  board step, arm A's steady window minus arm B's, and the two windows sit about 10 s apart in a 20 s lap
  with the die hotter in the busy arm. Measured on the committed telemetry, that ΔT is **+0.000 to +0.888 °C**
  on `minshire[0]` (+0.003 to +0.679 on the mean of three), so at E66's slope the step falls by 0.0–4.8%.
  The control works: the `E63-NULL` block's ΔT is −0.011 °C in s1 and +0.016 in s2, and its step moves by
  less than 0.005 W.

**2. Model E64-T1 — a temperature term in the governor's power curve**
([`../../../../tools/claims-v3/hpl/surface_hpl_t.py`](../../../../tools/claims-v3/hpl/surface_hpl_t.py),
[`t1-report.txt`](t1-report.txt), [`figures-t1.json`](figures-t1.json)). E64's registered
`surface_hpl.py` is **untouched**; this is a new, labelled version beside it.

The model has **two declared parameters that the data do not pin**: γ, the leakage law's voltage exponent,
and the governor's thermal trip. Both are swept, and every claim is read off the surface
([`trip-surface.txt`](trip-surface.txt), [`trip_surface.py`](trip_surface.py)) rather than off one corner:

| out of sample, MHz | trip 65.5 °C, γ = 0 / 2 / 3 | trip 66.0 °C, γ = 0 / 2 / 3 |
|---|---:|---:|
| rms over E64's 9 sustained cells (E64's cap: **23.0**) | 5.6 / 4.8 / 5.0 | 9.6 / 7.1 / **6.2** |
| rms over the **5 cells that discriminate** (E64's cap: **30.8**) | 7.5 / 6.5 / 6.8 | 12.9 / 9.6 / 8.3 |
| fp32 all-ones (measured **737.9**; E64's cap 780.6, `chain.py` 775) | 745.2 / 733.5 / 730.1 | 756.4 / 745.0 / 735.5 |
| fp16 all-ones (measured **737.1**; E64's cap 780.6) | 750.4 / 747.5 / 744.9 | 758.4 / 756.5 / 754.5 |

Four of E64's nine sustained cells are **clamps both models hit exactly** (fp32-zeros, int8-ones,
fp32-randn, int8-zeros: the governor is pinned at 800 or at its 600 MHz floor and neither model has
anywhere to go). They enter the nine-cell rms as exact zeros, so the rms over the five that discriminate is
published beside it; the ratio is the same either way. The γ = 5.5 column — the rms scan's own optimum — is
in the files too: it improves the burst (5.3 MHz) and makes the sustained worse (8.0 / 9.3).

"Out of sample" means the cell's whole workload label was removed from every term — from `B_f`, from the die
line, from τ_th, from the governor's calibration — and its switching term solved against the held-out `B_f`
from its own **cool-die burst** runs alone. Nothing *fitted* on a sustained run predicts that sustained run;
the run's own launch die reading (`die_start`) is the simulation's initial condition and its length sets the
averaging window, which are boundary conditions, not fitted terms.

**So, stated as the surface and not as a corner:**

- The fp32 all-ones sustained miss goes from **+42.7 MHz** (E64's own cap) and **+37** (`chain.py`'s
  cross-card version) to between **+18.5 and −7.8 MHz** over the six (γ ∈ {0,2,3}, trip ∈ {65.5, 66}) pairings.
  It **crosses zero inside that set** — −2.4 MHz at (γ 3, trip 66), −4.4 at (γ 2, trip 65.5) — and is still
  **+18.5 MHz at the least-assumption corner**, γ = 0 with E66's idle law applied literally at the declared
  66 °C trip. So: narrowed by a factor of two to five, closing only at the larger exponents, and **not
  pinned**. Which (γ, trip) is right is what E69 and E71 decide, not this report.
- **The fp16 all-ones cell never closes**: +7.8 to +21.3 MHz over the same six pairings (+4.9 at γ = 5.5,
  trip 65.5). Reported as a miss, not folded into an average.
- Over the nine cells the improvement on E64's registered cap is a factor of **2.4 to 4.8** (23.0 → 4.8–9.6);
  over the five that discriminate, **2.4 to 4.7** (30.8 → 6.5–12.9). That *some* temperature term helps by
  a factor of two to five is the robust part; the exponent and the trip are not.
- The trip is not uniformly kind: 65.5 °C improves both all-ones cells and makes `int8-randn` worse
  (758.4 against a measured 763.2, where trip 66 gives 766.4). It trades cells, which is what an
  unidentified parameter does.

**The cost, stated plainly.** The temperature term makes the burst slightly worse. On E64's own calibration
path — the governor simulated on each run's own measured powers, which is what E64's published 3.3 MHz rms
measures — the rms goes from **3.34 MHz to 4.38 / 4.61 / 4.32** (γ = 0 / 2 / 3), and 4.20 at γ = 5.5. The
whole model's burst rms is **5.8–6.7 MHz** in sample and **6.1–6.9** leave-one-label-out (5.6 / 5.3 at
γ = 5.5). Neither depends on the trip.

**3. What it does to the chain closure** ([`chain_t.py`](chain_t.py),
[`chain-t1-report.txt`](chain-t1-report.txt)). `chain.py` is untouched; its committed `chain.json` supplies
every input, and nothing is refitted.

- **The burst prediction is not improved, and gains a declared launch-temperature band.** At the referral's
  own 58 °C the ratio is identically 1.1471, by construction. At the launch readings E64's LAD runs actually
  had, the random burst clock rises and the ratio falls: **1.1383–1.1402 at a 56 °C launch** (the modal
  reading) and **1.1166–1.1241 at 50 °C** (the coolest). The four measured comparators are 1.1268, 1.1331,
  1.1414 and 1.1495. So the single point 1.147 becomes a band **1.117–1.147**, which contains three of those
  four and excludes the highest; at the 56 °C modal launch the prediction is 1.139, which sits between the
  second and third of them. The temperature term's contribution here is about ±0.015 in
  the ratio — roughly half the width of the measured spread, so it is a term the burst prediction should
  carry even though it does not resolve anything.
- 🛑 **The sustained ratio is still a clamp.** The window moves up and narrows: 37.93–52.49 W (width 14.56) →
  **42.48–55.33 W (width 12.85)** at γ = 3 and a 65.5 °C trip, and 42.83–55.54 (12.72) at a 66 °C trip.
  E64's registered 50.3 W cap stays inside the window in every variant, so zeros still clamps at 800 and
  random at 600 and the predicted ratio is exactly 800/600 = 1.3333 by construction. **The temperature term
  does not rescue the sustained ratio from being a clamp; that result stays ordinal.** What it does rescue is
  the one sustained cell *inside* the window: all-ones moves from 775 MHz to **747.6 / 740.3 / 736.2** MHz
  (γ = 0 / 2 / 3) at a 65.5 °C trip and **756.0 / 747.7 / 743.1** at 66 °C, against a measured 738 — so the
  miss goes from +37 MHz to between **+18.0 and −1.8 MHz**, closing only at the warm end of the γ range and
  the cool end of the trip range.

**4. E69's cells, frozen under this model** ([`predictions-t1-e69.json`](predictions-t1-e69.json),
[`predict_knob_t1.py`](predict_knob_t1.py)). E69 (the knob test, running on aifoundry2 as this was written)
pre-registered from E64's original model. T1's numbers for the same cells were **committed in `6422fac8` at
2026-10-27T14:19:37−07:00, before any E69 commit existed at all** — E69's own pre-registration `2d35d1b9`
landed three seconds later, as that commit's child — so E69's data will score two models rather than one.
Two cells disagree outright, and they are the discriminating ones:

| cell | E69, from E64's registered model | E64-T1 (γ = 0 / 2 / 3) |
|---|---:|---:|
| `S-tdp65-thr70-fp32-randn` | 600.0 MHz | **630.3 / 628.6 / 627.7** |
| `S-tdp50-thr65-fp32-ones` | 700.0 MHz | **743.4 / 731.2 / 721.7** |
| `S-tdp65-thr65-fp32-ones` (control) | 736.5 | 736.7 / 726.1 / 718.7 |
| `S-tdp65-thr62-fp32-ones` | 649.8 | 662.9 / 658.8 / 657.8 |
| `B-tdp45-fp32-ones` | 733.3 | 717.9 / 713.6 / 716.7 |
| `B-tdp35-fp32-zeros` | 795.2 | 785.7 / 781.8 / 777.8 |

T1's sustained cells come out of the same simulation as its burst cells, from the cool-die ladder and the
leakage law. They are **not** anchored on each pattern's own E64 sustained mean, which is the circularity
E69's own README names as its honest limitation — so T1's two control cells are a genuine out-of-sample
check where E69's are partly self-fitting. These predictions are at the declared 66 °C trip; the sustained
cells each trip on their own commanded threshold, so only the burst cells carry that parameter.

**The freeze survives this amendment.** Every correction above was applied and `predict_knob_t1.py` re-run
against the corrected `figures-t1.json`: `predictions-t1-e69.json` comes back **identical, field for field**
(it reads only `t_trip_c` and each variant's `B_f`, governor, die line and τ_th, none of which the
corrections move). The file committed at 14:19:37 is therefore still the frozen artifact, not a re-derived
one. **Scoring it against E69's measured results is deliberately not done here** — E69's reduction belongs
to the agent that ran it — and is listed as an open issue.

## What was done, and what each piece rests on

### Item 1: the re-reductions

**E60's aifoundry2 rows** were re-run with the registered reducer itself, `tools/claims-v3/hl/reduce_hl.py`,
on E60's own committed pass directories, with `--leak` the one input changed. The check that this is the
registered reduction and not a new one: at `--leak auto` it prints E60's committed `reduce.txt` line for
aifoundry2 **bit for bit** — 800 MHz, 617.4 mV, passes [1,2,3,4,6,7,8,9,10], 160/180 runs, leak 0.442 W/°C,
pass 5 set aside with a π drift of −1.7817 W, `lq` 121.272 ± 0.613 / 79.516 ± 0.403 / 0.338 ± 0.004 fJ,
`ord` 1.291 ± 0.009 and 1.311 ± 0.131 W, `e_in` 28.66 ± 0.38 fJ.

[`posthoc_e60.py`](posthoc_e60.py) then repeats the same arithmetic from E60's committed `runs.csv`, which is
what makes the **frozen** pass-gate column possible (the reducer has no knob to hold a pass set). It is
validated against the reducer at every slope on the ladder: identical to the last published digit at 0.000,
0.294, 0.327, 0.360, 0.442, 0.456 and 1.000 W/°C. The slope ladder is E68's, so the two experiments'
sensitivity tables can be read side by side, plus E66's own median and the extremes of its 18 cycles.
Across that whole interval (0.2917 → 0.2961 W/°C) the price moves **0.052 fJ, about 7% of its 0.767 SE**
(frozen gate: 0.053 fJ, 7.8%) — so E66's own spread in the slope is not what limits this price.

**E63's prices** were re-reduced by [`posthoc_e63.py`](posthoc_e63.py), which reads only committed session
records: `launches.jsonl` for the two arms' windows, `tel.jsonl.gz` for the board power and the minion-shire
reading in exactly the windows `lockin_hlc.steady_steps` uses (2.0 s after a launch's start to 0.3 s before
its end), and `lockin.json` for the analysed lap set. Two checks: the recomputed per-lap steps **matched
`lockin.json`'s own `per_lap.board_step_w` list element for element** in all four blocks of both sessions, so
the lap set is identified rather than guessed; and at a slope of zero the prices reproduce the committed
`summary.json` exactly (154.04 / 121.72 / 154.44 and 151.70 / 120.26 / 152.38 fJ).

🛑 **Which temperature variable.** `temp_c.minshire` is three integer-degree readings. The slope being
multiplied in is defined on **one** of them — E66's `idle_slope.py` and the registered `reduce_hl.py` both
read `minshire[0]` — while E63's own analysis reports their **mean** as its die column. A W/°C measured
against sensor 0 times a ΔT measured on the mean of three is not the leakage difference unless the die is
isothermal, which in a busy window it is not, so both are computed for every lap and every slope. Sensor 0
is the primary column, for consistency with the slope; the mean of three is `slopes_alt`. The two differ by
up to 1.5 fJ (1%), and the comparison exposes the honest limit of each: sensor 0 is 1 °C-quantised, so for
s2's `MID` block its per-lap ΔT is identically zero and that price gets no correction at all, where the mean
of three resolves +0.003 °C. Neither variable is the junction temperature; the spread between them is
smaller than the 600-vs-800 MHz caveat below.

**E68** was already re-reduced at this slope on 27 Oct and is quoted, not recomputed, from
[`../2026-10-27-e68-stage-map/leak-sensitivity.txt`](../2026-10-27-e68-stage-map/leak-sensitivity.txt),
from its **0.294** column.

**What was deliberately not re-reduced.** E65 and E67 ran on aifoundry3, whose idle slope has never been
measured (that is E71). E60's `aifoundry1-c0` and `aifoundry3` rows are other cards. E66's slope is this
card's and is applied to this card only.

### Item 2: the model

E64's registered model refers every board power to a 58 °C die with one constant slope (0.442 W/°C, E60's
busy-window estimate) and then simulates the governor at a fixed 58 °C die. It therefore has no die
temperature to trip on, and its sustained clock has to come from a separate board-power cap. E64-T1 adds:

1. **E66's measured law instead of the constant.** `Λ(T, V) = A80·e^((T−80)/T_L)·(V/0.519)^γ` with
   A80 = 20.41 W and T_L = 29.8 °C, E66's 18-cycle fit on this card (local slope 0.2936 W/°C over 51–58 °C).
   Every sample is referred with `Λ(T, V_f) − Λ(58, V_f)`.
2. **The die as a state in the simulation**, relaxing towards E64's own die line
   (41.884 + 0.4696 °C per W) with a time constant **τ_th = 14.0 s**, fitted to the SUS runs' measured die
   rise (rms 0.246 °C over 339 two-second bins).
3. **A thermal limb in the governor**: a pass whose die reading is at or above the trip steps the clock down.
   That is what E64's R3 measured, and it makes the sustained clock a duty cycle that holds the die at the
   trip — which is exactly what E64's SUS traces show (fp32 all-ones sits at 65.0–65.6 °C from t = 28 s and
   dithers 695–790 MHz). The trip is **declared, not fitted, and both declared values are run**: 66.0 °C
   (E64's R3) in [`figures-t1.json`](figures-t1.json) and 65.5 °C (E64's registered sustained reading) in
   [`figures-t1-trip655.json`](figures-t1-trip655.json), with the surface in
   [`trip-surface.txt`](trip-surface.txt).

This hard trip does **not** contradict `chain.json`'s registered note that "66 C is not a hard trip": E64's
fp32-randn sustained point sits at 67.1 °C and T1 reproduces it (die column 67.4–67.7 °C) because the
governor is already at its 600 MHz floor and has no step left to take.

**The port is bit-exact.** With the temperature term switched off and at E64's own 2-decimal rounding of
each clock's median power, this file reproduces E64's registered fit to the last printed digit: `B_f`
{600: 25.455614671708, 700: 28.243261128821, 800: 33.609566845262} W at **rms 0.8242388715772777 W** over
103 points against E64's `figures.json` 0.8242388715772772 (a float summation-order difference in the
sixteenth significant figure), the die line 0.4696 °C/W and 41.884 °C with `cap_w_at_65_5` 50.2868 W
(E64: 50.3), and the governor calibration **τ 1.3 s, pass 0.24 s, rms 3.34 MHz**. The T1 variants keep **3**
decimals, because the leakage referral moves a sample by milliwatts and 2 dp quantises it; the same
registered fit at 3 dp reads rms 0.8247507 W, which is the "0.825" the first draft of this report quoted as
the port. Both are in `registered_comparison` (`rms_w` and `rms_w_at_t1_rounding`). One small correction to
E64's own report while reproducing it: E64 prints `n 26` for that calibration, but two of its 26 cool-die
runs have a missing power point and its own loop skips them, so the rms is over **24** runs.

**With the term on, the power curve itself gets better** on the same 103 points: rms 0.825 → 0.780 (γ = 0),
0.725 (γ = 2), 0.698 (γ = 3), 0.654 (γ = 5.5) W.

**γ, the first free choice, and why it is not settled.** E66 measured leakage *idle*, at 600 MHz and 519 mV;
E64's three clocks run at 517, 568 and 618 mV, so applying the law needs a voltage exponent. Three pieces of
evidence, which do not fully agree:

- **Measured inside E64's own sustained runs at a held clock** (`figures-t1.json` `busy_slope_measured`):
  dP/dT at 800 MHz is 0.351, 0.498, 0.515 and 0.625 W/°C over four runs, median **0.507** — that is
  **1.73 × E66's idle 0.2936**, and (618/519) = 1.191, so the implied **γ = 3.1**. This is an *upper* bound:
  during a warm-up the regulators drift and the die reading lags the power, both of which inflate a
  within-run slope.
- **The power curve's rms** falls monotonically with γ out to 5.5, so it points the same way but does
  not identify a value — and at 5.5 the sustained cells get worse, so the power curve's optimum is not the
  model's.
- **Which γ best reproduces the all-ones sustained cell depends on the input path and on the trip.** Through
  the fitted `B_f + c` at a 66 °C trip it is γ = 3 (735.5 against 737.9); at a 65.5 °C trip it is γ = 2
  (733.5); and through each pattern's raw cool-die ladder, which is the path the E69 predictor uses, it is
  γ = 0 (736.7 against 737.9).

**The trip, the second free choice.** 66.0 °C is E64's R3 reading and 65.5 °C is its registered sustained
one; nothing here fits either. Moving between them changes the nine-cell out-of-sample rms by up to 4 MHz,
moves the γ that closes the fp32 cell from 3 to 2, and halves the fp16 miss. γ and the trip are therefore
**jointly** unidentified, and the published pairing is not the model's own best — (γ 2, trip 65.5) has the
lowest nine-cell rms at 4.8 MHz, which is one more reason not to quote a single corner as the result.

So no default is asserted on either parameter. The robust claim is that *some* temperature term cuts the
sustained rms by a factor of two to five; the exponent and the trip are open, and **E69's knob cells are
what pin them** — the two cells where T1 and E69's registered model disagree are both sensitive to γ.
E69's measurements had landed by the time this amendment was written; scoring the frozen predictions
against them is left to E69's own reduction, and is an open issue here.

## Honest limitations

- Nothing here is a card run. No governor was moved, no card opened, no firmware read.
- The die line (0.4696 °C/W, 41.884 °C) is E64's, fitted on nine points pooled across fp32, fp16 and int8.
  T1 inherits it unchanged and does not test it.
- Both the thermal trip and γ are declared parameters, not fitted ones, and they are jointly unidentified.
- **T_L = 29.8 °C, the e-folding the whole law is built on, is inherited from a gate E66 itself scored
  UNDECIDED** (its L1 row: point value 29.8, interval 27.7–32.0, registered band 30–45 — the point value
  sits *below* its own registered band). T1 uses the point value unchanged and does not test it.
- E66's law is this card's idle split. Its A80 is an extrapolation to 80 °C (E66 amendment A1) and nothing
  measured above 70 °C constrains it; the SUS cells sit at 59–68 °C, inside the measured band, but the law's
  shape above that is untested.
- The governor's τ and pass length are calibrated with the thermal limb **off** and then used for
  predictions with it on. Defensible on a 6.5 s burst against τ_th = 14 s — the die barely moves inside the
  window the calibration scores — and it keeps τ comparable with E64's registered 1.3 s, but it is a
  mismatch between the calibration model and the prediction model, and it is declared in
  `surface_hpl_t.py`'s header and in each variant's `notes`.
- The "E64 cap" baseline column (23.0 MHz, and each cell's `registered_cap_mhz`) is **T1's own
  reconstruction** of the registered model's sustained rule — a bisection on an interpolated `B_f` against
  `cap_w_at_65_5` — not E64's discrete three-point simulation. It does not depend on the trip (identical at
  66 and 65.5), so the baseline is stable, but it is a reconstruction rather than a quoted E64 number.
- E60's `ord` pos 19 contrast moves 13% at the new slope under the live gate and 4% under the frozen one. It
  rests on a single pass either way and should not be quoted tighter than ±0.13 W.
- E63's ΔT correction assumes the leakage slope measured at 600 MHz idle applies to the 800 MHz busy windows
  the steps are taken in. By item 2's own finding that is probably an underestimate by up to 1.7×, which
  would make E63's prices fall by 5–7% rather than 3–5%. The 0.327, 0.442 and 1.508 W/°C columns in
  [`e63-leak-sensitivity.txt`](e63-leak-sensitivity.txt) bracket it. The sensor choice above is a second,
  smaller (±1%) uncertainty on the same correction.

## What it changes

**In the Horace Hub's Levels tab, stop 1** ("Missing: a temperature term in the governor's power curve — the
all-ones miss"): **the line stays open, narrowed.** The term now exists and is measured, and it takes the
fp32 all-ones sustained miss from +42.7 MHz (E64's cap) and +37 (through the chain) to between +18.5 and
−7.8 MHz on the card's own fit, out of sample — closing at the larger voltage exponents and still missing by
+18.5 MHz at the least-assumption corner. γ and the trip are not pinned; E69's knob cells and E71's
aifoundry3 slope are what pin them. The fp16 all-ones miss remains open at +7.8 to +21.3 MHz, and the
sustained zeros/random ratio remains a clamp.

**In Q128 §5 item 3** ("the leakage slope — re-run reductions with measured slopes as labelled
sensitivities"): done for every aifoundry2 price. E60 and E63 join E68. aifoundry3's half still waits on E71.

**In the waterfall: nothing moves from "unaccounted" to "accounted".** These are corrections to the *inputs*
of the per-bit price list, not new accounted pJ. The board's 5.783 pJ per random multiply-add and its 3.837 pJ
unaccounted come from E38 and are untouched. What moves is the price list the chain uses to predict a random
word: the mantissa-flip price rises 1.4% (E60) and the camera-side price falls 0.0–4.8% (E63), both inside
the bands those experiments already published, so **the published bands stand**.

## Fixed after review

Q129's verifier re-derived every headline number from the committed inputs and raised fifteen faults against
the 14:24 draft. All fifteen are addressed; none needed a card. What each one moved:

| # | fault | what was done | did a number move? |
|---|---|---|---|
| 1 | headline "the miss closes" and the Levels-tab strike quoted one (γ, trip) pairing of two unidentified parameters | stated as the full surface (+18.5 to −7.8 MHz on-card, +18.0 to −1.8 through the chain); Levels-tab line left **open** | no number; the **conclusion** changed |
| 2 | the 65.5 °C trip sensitivity this README promised was never run on the card model | run: `figures-t1-trip655.json`, `t1-report-trip655.txt`, and `trip_surface.py` → `trip-surface.{json,txt}` | **yes**: 9-cell oos rms 4.8–9.6 (was one column 6.2–9.6); closing γ moves 3 → 2; fp16 miss 7.8–21.3 |
| 3 | the "port check" rounded medians to 3 dp where E64 uses 2, undisclosed | registered comparison column now built at E64's own 2 dp; the 3 dp value kept as `rms_w_at_t1_rounding`; both disclosed | **yes**: the port is now bit-exact (0.8242388715772777 vs …772, was 0.8247507); one cell's reconstructed `registered_cap_mhz` 612.2 → 612.3 |
| 4 | the burst "leave-one-label-out" column took `c` from the in-sample fit | new `c_run_against()` solves `c` against the held-out `B_f` from the run's own samples; the old column kept as `t1_oos_cinfit_mhz` | **no**: 0 of 26 cells moved their 1-dp clock, rms identical to 4 dp (6.9459 / 6.0983 / 6.4389); max \|Δc\| 0.014 W |
| 5 | README burst-rms ranges ("5.7–6.7 / 5.9–6.9") matched no published value | corrected to 5.8–6.7 in sample, 6.1–6.9 held out | text |
| 6 | "a factor of three at every γ" is 2.4 at γ = 0 | "a factor of two to five", computed over the whole surface by `trip_surface.py` | text |
| 7 | E63's ΔT was measured on the mean of three sensors, the slope on `minshire[0]` | `posthoc_e63.py` computes both; sensor 0 is primary, the mean is `slopes_alt`, both printed | **yes**: E63 prices at 0.2936 move up to 1.7 fJ; band 116.4–149.3 → **116.5–148.8** |
| 8 | the "±13%" convergence was tuned to a threshold between the before and after | `band.py` prints the two spreads: 13.6% → 12.2% of the midpoint | text + a computed field |
| 9 | "the price moves 0.03 fJ = 4% of its SE" across E66's interval was the half-range | 0.052 fJ = 6.7% of the SE (frozen 0.053, 7.8%) | text |
| 10 | the freeze parenthetical said E69's pre-registration existed at the freeze; it is the freeze commit's child | "before any E69 commit existed at all; `2d35d1b9` landed three seconds later as its child" | text; the freeze itself always held |
| 11 | the nine-cell rms counts four cells both models hit exactly | `clamp_cell_both_models` per cell, plus the rms over the five that discriminate (30.8 → 6.5–12.9) | new fields; the ratio is unchanged |
| 12 | E68's prices labelled "at 0.2936" are read from its 0.294 column | labelled as E68's 0.294 column in `band.py`, the README and the json | text + a label field |
| 13 | the governor is calibrated with the thermal limb off and used with it on | declared in `surface_hpl_t.py`'s header, in `calibrate_governor`'s docstring and in each variant's `notes` | text |
| 14 | T_L = 29.8 °C is inherited from a gate E66 scored UNDECIDED | added to the limitations, with its interval and its registered band | text |
| 15 | "nothing from a sustained run predicts that sustained run" is absolute | "nothing *fitted* on a sustained run"; `die_start` and the run length named as boundary conditions | text |

Also done while in there: `chain_t.py`'s `figures-t1.json` argument supplied no number, so it is now a
consistency gate — the run refuses if that file's leakage law or `T_ref` differs from the one `chain_t.py`
codes. `chain-t1.json` and `chain-t1-report.txt` are byte-identical after the change.

## Files

| Path | What |
|---|---|
| [`../../../../tools/claims-v3/hpl/surface_hpl_t.py`](../../../../tools/claims-v3/hpl/surface_hpl_t.py) | model **E64-T1**; a new version beside E64's registered `surface_hpl.py`, which is unchanged |
| `figures-t1.json`, `t1-report.txt` | the model at the declared 66 °C trip: the γ scan, the busy-slope measurement, the fit, every burst and sustained cell in sample and held out |
| `figures-t1-trip655.json`, `t1-report-trip655.txt` | the same at the 65.5 °C trip (`--trip 65.5`) |
| `trip_surface.py`, `trip-surface.{json,txt}` | the (γ, trip) surface: every rms and every informative cell over both declared parameters |
| `chain_t.py`, `chain-t1.json`, `chain-t1-report.txt` | what the term does to the chain closure's burst ratio and sustained clamp window, at both trips |
| `predict_knob_t1.py`, `predictions-t1-e69.json` | E64-T1's frozen predictions for E69's cells, committed before any E69 commit; unchanged by this amendment |
| `posthoc_e60.py`, `e60-a2-leak-sensitivity.{json,txt}` | E60's aifoundry2 prices at eleven slopes, both pass-gate modes |
| `posthoc_e63.py`, `e63-s{1,2}-leak-sensitivity.json`, `e63-leak-sensitivity.txt` | E63's per-flip prices with the paired step's ΔT correction, in both die variables |
| `band.py`, `per-bit-band.{json,txt}` | every aifoundry2 per-flipped-bit price on one slope, the band, and the two convergence spreads |

Rebuild everything (read-only; no card, no network):

```bash
R=.                       # the repo root
D=$R/docs/reports/data/2026-10-20-bitflip-ladder
E=$R/docs/reports/data/2026-10-23-e63-camera-hamming-ladder
O=$R/docs/reports/data/2026-10-27-q129-governor-temperature
RES=$R/docs/reports/data/2026-10-23-e64-horace-power-limit/results.json
# E60 at the registered slope, the check that this is its own reduction
python3 $R/tools/claims-v3/hl/reduce_hl.py $D/aifoundry2/hl/p* --gen <dir holding manifest-a1.json> \
        --pred $D/predictions.json --leak auto --out /dev/null
python3 $O/posthoc_e60.py $D/runs.csv $D/manifest-a1.json $D/predictions.json \
        --card aifoundry2 --frozen 1,2,3,4,6,7,8,9,10 --out $O/e60-a2-leak-sensitivity.json
for s in s1 s2; do
  python3 $O/posthoc_e63.py $E/$s/session $E/$s/analysis/lockin.json \
          --die-sensor 0 --out $O/e63-$s-leak-sensitivity.json
done
python3 $O/band.py $R $O/e60-a2-leak-sensitivity.json $O/e63-s1-leak-sensitivity.json \
        $O/e63-s2-leak-sensitivity.json --out $O/per-bit-band.json
python3 $R/tools/claims-v3/hpl/surface_hpl_t.py $RES --out $O/figures-t1.json
python3 $R/tools/claims-v3/hpl/surface_hpl_t.py $RES --trip 65.5 --out $O/figures-t1-trip655.json
python3 $O/trip_surface.py $O/figures-t1.json $O/figures-t1-trip655.json --out $O/trip-surface.json
python3 $O/chain_t.py $R/docs/reports/data/2026-10-27-chain-closure/chain.json $O/figures-t1.json \
        --out $O/chain-t1.json
# the freeze check: this must come back identical to the committed file
python3 $O/predict_knob_t1.py --results $RES --figures-t1 $O/figures-t1.json \
        --out /tmp/predictions-t1-e69.json
```

`posthoc_e60.py` and `posthoc_e63.py` need numpy; `surface_hpl_t.py`, `chain_t.py`, `trip_surface.py` and
`band.py` are stdlib only, like E64's own surface. Each `.txt` in this directory is the corresponding
script's stdout.
