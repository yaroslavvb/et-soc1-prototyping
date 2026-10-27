# Q129(a2) — the governor's temperature term, and every aifoundry2 per-bit price on one leakage slope

*Desk work, Tue 27 Oct 2026 (week 44), 13:5x–15:xx PDT. **No card was touched and no governor was moved.**
Every number below is a re-reduction or a model fit on data already committed in this repo. Two items:
(1) the aifoundry2 per-flipped-bit prices that had not yet been re-reduced at E66's measured idle leakage
slope, as labelled sensitivities; (2) a new model version of E64's governor surface that carries leakage's
temperature dependence.*

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
| E63 s1 | TOP / MID / TOP2 per designed B bit | 154.04 / 121.72 / 154.44 | **0.000** | 149.34 / 116.37 / 148.80 | −3.0 / −4.4 / −3.7% |
| E63 s2 | TOP / MID / TOP2 per designed B bit | 151.70 / 120.26 / 152.38 | **0.000** | 146.68 / 120.17 / 148.49 | −3.3 / −0.1 / −2.5% |
| E68 | `sm_lo12` … `sm_e64` (9 items) | 112.8–282.5 | 1.508 | 123.2–276.4 | −9.8 to +17.9% |

**The band.** On one slope, the whole-word "per designed flipped B bit" prices measured on this card lie
between **116.4 and 149.3 fJ** (E60's mantissa ladder at 123.0, E63's camera-session blocks at 116.4–149.3),
and E68's stage-resolved prices for named bit groups span **123.2–276.4 fJ** — low mantissa 135.9, high
mantissa 194.4, split 216.4, exponent-64 276.4. The mantissa-flip numbers from all three experiments
(E60 123.0, E63 116.4–149.3, E68 `sm_lo12` 135.9 and `sm_sgnlo` 135.4) agree inside ±13% of their midpoint,
which they did not when each carried its own slope.

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
  with the die hotter in the busy arm. Measured on the committed telemetry, that ΔT is **+0.003 to +0.679 °C**,
  so at E66's slope the step falls by 0.1–4.4%. The control works: the `E63-NULL` block's ΔT is 0.003 °C in
  s1 and −0.002 in s2, and its step moves by less than 0.002 W.

**2. Model E64-T1 — a temperature term in the governor's power curve**
([`../../../../tools/claims-v3/hpl/surface_hpl_t.py`](../../../../tools/claims-v3/hpl/surface_hpl_t.py),
[`t1-report.txt`](t1-report.txt), [`figures-t1.json`](figures-t1.json)). E64's registered
`surface_hpl.py` is **untouched**; this is a new, labelled version beside it.

Over E64's nine sustained cells, the mean clock's rms error:

| | rms over the 9 SUS cells | fp32 all-ones sustained (measured **737.9 MHz**) |
|---|---:|---:|
| E64 registered, a board-power cap at 50.3 W | **23.0 MHz** | 780.6 MHz (chain.py's cross-card version: **775**) |
| E64-T1, γ = 0 (E66's idle law literally) | 9.7 in sample / 9.6 out of sample | 757.2 / 756.4 |
| E64-T1, γ = 2 (leakage scaled like the dynamic term) | 8.4 / 7.1 | 754.5 / 745.0 |
| E64-T1, γ = 3 (what E64's own hot traces measure) | 7.6 / **6.2** | 753.0 / **735.5** |

"Out of sample" means the cell's whole workload label was removed from every term — from `B_f`, from the die
line, from τ_th, from the governor's calibration — and its switching term solved against the held-out `B_f`
from its own **cool-die burst** runs alone. Nothing from a sustained run predicts that sustained run.

**So: the all-ones miss closes, at the larger voltage exponents, and narrows by half at the smaller ones.**
Over all nine cells the factor-of-three improvement holds at every γ, and that part does not depend on the
model's one free choice. **The fp16 all-ones cell does not close** (measured 737.1, T1 out of sample 754.5
at γ = 3), and that is reported as a miss, not folded into an average.

**The cost, stated plainly.** The temperature term makes the burst slightly worse. On E64's own calibration
path — the governor simulated on each run's own measured powers, which is what E64's published 3.3 MHz rms
over 26 runs measures — the rms goes from 3.34 MHz to 4.32–4.61 MHz. The whole model's burst rms is
5.7–6.7 MHz in sample and 5.9–6.9 MHz leave-one-label-out.

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
  **42.48–55.33 W (width 12.85)** at γ = 3 and a 65.5 °C trip. E64's registered 50.3 W cap stays inside the
  window in every variant, so zeros still clamps at 800 and random at 600 and the predicted ratio is exactly
  800/600 = 1.3333 by construction. **The temperature term does not rescue the sustained ratio from being a
  clamp; that result stays ordinal.** What it does rescue is the one sustained cell *inside* the window:
  all-ones moves from 775 MHz to **747.6 / 740.3 / 736.2** MHz (γ = 0 / 2 / 3) against a measured 738, so the
  miss goes from +37 MHz to **+9.6 / +2.3 / −1.8 MHz**.

**4. E69's cells, frozen under this model** ([`predictions-t1-e69.json`](predictions-t1-e69.json),
[`predict_knob_t1.py`](predict_knob_t1.py)). E69 (the knob test, running on aifoundry2 as this was written)
pre-registered from E64's original model. T1's numbers for the same cells were **committed in `6422fac8` at
2026-10-27T14:19:37−07:00, before any E69 result existed** (the only E69 commit in the repo at that moment
was its own pre-registration), so E69's data will score two models rather than one. Two cells disagree
outright, and they are the discriminating ones:

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
check where E69's are partly self-fitting.

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
sensitivity tables can be read side by side, plus E66's own median and the extremes of its 18 cycles
(0.2917 / 0.2936 / 0.2961 — the price moves by 0.03 fJ across that whole interval, which is 4% of its SE).

**E63's prices** were re-reduced by [`posthoc_e63.py`](posthoc_e63.py), which reads only committed session
records: `launches.jsonl` for the two arms' windows, `tel.jsonl.gz` for the board power and the minion-shire
reading in exactly the windows `lockin_hlc.steady_steps` uses (2.0 s after a launch's start to 0.3 s before
its end), and `lockin.json` for the analysed lap set. Two checks: the recomputed per-lap steps **matched
`lockin.json`'s own `per_lap.board_step_w` list element for element** in all four blocks of both sessions, so
the lap set is identified rather than guessed; and at a slope of zero the prices reproduce the committed
`summary.json` exactly (154.04 / 121.72 / 154.44 and 151.70 / 120.26 / 152.38 fJ).

**E68** was already re-reduced at this slope on 27 Oct and is quoted, not recomputed, from
[`../2026-10-27-e68-stage-map/leak-sensitivity.txt`](../2026-10-27-e68-stage-map/leak-sensitivity.txt).

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
   dithers 695–790 MHz). The trip is declared, not fitted: 66.0 °C (E64's R3) with 65.5 °C as a sensitivity.

**The port is checked.** With the temperature term switched off, this file reproduces E64's registered fit:
`B_f` {600: 25.46, 700: 28.24, 800: 33.61} W at rms 0.825 W over 103 points (E64: 0.8242), the die line
0.4696 °C/W and 41.884 °C with `cap_w_at_65_5` 50.287 W (E64: 50.3), and the governor calibration
**τ 1.3 s, pass 0.24 s, rms 3.34 MHz** (E64 publishes 3.3 MHz). One small correction to E64's own report
while reproducing it: E64 prints `n 26` for that calibration, but two of its 26 cool-die runs have a missing
power point and its own loop skips them, so the rms is over **24** runs.

**With the term on, the power curve itself gets better** on the same 103 points: rms 0.825 → 0.780 (γ = 0),
0.725 (γ = 2), 0.698 (γ = 3) W.

**γ, the one free choice, and why it is not settled.** E66 measured leakage *idle*, at 600 MHz and 519 mV;
E64's three clocks run at 517, 568 and 618 mV, so applying the law needs a voltage exponent. Three pieces of
evidence, which do not fully agree:

- **Measured inside E64's own sustained runs at a held clock** (`figures-t1.json` `busy_slope_measured`):
  dP/dT at 800 MHz is 0.351, 0.498, 0.515 and 0.625 W/°C over four runs, median **0.507** — that is
  **1.73 × E66's idle 0.2936**, and (618/519) = 1.191, so the implied **γ = 3.1**. This is an *upper* bound:
  during a warm-up the regulators drift and the die reading lags the power, both of which inflate a
  within-run slope.
- **The power curve's rms** falls monotonically with γ out to about 5.5, so it points the same way but does
  not identify a value.
- **Which γ best reproduces the all-ones sustained cell depends on the input path.** Through the fitted
  `B_f + c` it is γ = 3 (735.5 out of sample against 737.9); through each pattern's raw cool-die ladder, which
  is the path the E69 predictor uses, it is γ = 0 (736.7 against 737.9).

So γ is published as three labelled variants and no default is asserted. The robust claim is that *some*
temperature term cuts the sustained rms by a factor of three; the exponent is open, and **E69's knob cells
are what will pin it** — the two cells where T1 and E69's registered model disagree are both sensitive to it.

## Honest limitations

- Nothing here is a card run. No governor was moved, no card opened, no firmware read.
- The die line (0.4696 °C/W, 41.884 °C) is E64's, fitted on nine points pooled across fp32, fp16 and int8.
  T1 inherits it unchanged and does not test it.
- The thermal trip is a declared parameter, not a fitted one.
- E66's law is this card's idle split. Its A80 is an extrapolation to 80 °C (E66 amendment A1) and nothing
  measured above 70 °C constrains it; the SUS cells sit at 59–68 °C, inside the measured band, but the law's
  shape above that is untested.
- E60's `ord` pos 19 contrast moves 13% at the new slope under the live gate and 4% under the frozen one. It
  rests on a single pass either way and should not be quoted tighter than ±0.13 W.
- E63's ΔT correction assumes the leakage slope measured at 600 MHz idle applies to the 800 MHz busy windows
  the steps are taken in. By item 2's own finding that is probably an underestimate by up to 1.7×, which
  would make E63's prices fall by 5–7% rather than 3–4%. The 0.327, 0.442 and 1.508 W/°C columns in
  [`e63-leak-sensitivity.txt`](e63-leak-sensitivity.txt) bracket it.

## What it changes

**In the Horace Hub's Levels tab, stop 1** ("Missing: a temperature term in the governor's power curve — the
all-ones miss"): the term now exists, is measured, and closes the fp32 all-ones sustained miss out of sample
(735.5 against 737.9 on the card's own fit; 736.2 against 738 through the chain). The fp16 all-ones miss
remains open at +17 MHz, and the sustained zeros/random ratio remains a clamp.

**In Q128 §5 item 3** ("the leakage slope — re-run reductions with measured slopes as labelled
sensitivities"): done for every aifoundry2 price. E60 and E63 join E68. aifoundry3's half still waits on E71.

**In the waterfall: nothing moves from "unaccounted" to "accounted".** These are corrections to the *inputs*
of the per-bit price list, not new accounted pJ. The board's 5.783 pJ per random multiply-add and its 3.837 pJ
unaccounted come from E38 and are untouched. What moves is the price list the chain uses to predict a random
word: the mantissa-flip price rises 1.4% (E60) and the camera-side price falls 0.1–4.4% (E63), both inside
the bands those experiments already published, so **the published bands stand**.

## Files

| Path | What |
|---|---|
| [`../../../../tools/claims-v3/hpl/surface_hpl_t.py`](../../../../tools/claims-v3/hpl/surface_hpl_t.py) | model **E64-T1**; a new version beside E64's registered `surface_hpl.py`, which is unchanged |
| `figures-t1.json`, `t1-report.txt` | the model's full output: the γ scan, the busy-slope measurement, the fit, every burst and sustained cell in sample and held out |
| `chain_t.py`, `chain-t1.json`, `chain-t1-report.txt` | what the term does to the chain closure's burst ratio and sustained clamp window |
| `predict_knob_t1.py`, `predictions-t1-e69.json` | E64-T1's frozen predictions for E69's cells, committed before E69's results |
| `posthoc_e60.py`, `e60-a2-leak-sensitivity.{json,txt}` | E60's aifoundry2 prices at eleven slopes, both pass-gate modes |
| `posthoc_e63.py`, `e63-s{1,2}-leak-sensitivity.json`, `e63-leak-sensitivity.txt` | E63's per-flip prices with the paired step's ΔT correction |
| `band.py`, `per-bit-band.{json,txt}` | every aifoundry2 per-flipped-bit price on one slope, and the band |

Rebuild everything (read-only; no card, no network):

```bash
R=.                       # the repo root
D=$R/docs/reports/data/2026-10-20-bitflip-ladder
O=$R/docs/reports/data/2026-10-27-q129-governor-temperature
# E60 at the registered slope, the check that this is its own reduction
python3 $R/tools/claims-v3/hl/reduce_hl.py $D/aifoundry2/hl/p* --gen <dir holding manifest-a1.json> \
        --pred $D/predictions.json --leak auto --out /dev/null
python3 $O/posthoc_e60.py $D/runs.csv $D/manifest-a1.json $D/predictions.json \
        --card aifoundry2 --frozen 1,2,3,4,6,7,8,9,10 --out $O/e60-a2-leak-sensitivity.json
for s in s1 s2; do
  python3 $O/posthoc_e63.py $R/docs/reports/data/2026-10-23-e63-camera-hamming-ladder/$s/session \
          $R/docs/reports/data/2026-10-23-e63-camera-hamming-ladder/$s/analysis/lockin.json \
          --out $O/e63-$s-leak-sensitivity.json
done
python3 $O/band.py $R $O/e60-a2-leak-sensitivity.json $O/e63-s1-leak-sensitivity.json \
        $O/e63-s2-leak-sensitivity.json --out $O/per-bit-band.json
python3 $R/tools/claims-v3/hpl/surface_hpl_t.py \
        $R/docs/reports/data/2026-10-23-e64-horace-power-limit/results.json --out $O/figures-t1.json
python3 $O/chain_t.py $R/docs/reports/data/2026-10-27-chain-closure/chain.json $O/figures-t1.json \
        --out $O/chain-t1.json
python3 $O/predict_knob_t1.py --results \
        $R/docs/reports/data/2026-10-23-e64-horace-power-limit/results.json \
        --figures-t1 $O/figures-t1.json --out $O/predictions-t1-e69.json
```

`posthoc_e60.py` and `posthoc_e63.py` need numpy; `surface_hpl_t.py`, `chain_t.py` and `band.py` are stdlib
only, like E64's own surface.
