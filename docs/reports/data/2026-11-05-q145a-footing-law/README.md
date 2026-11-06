# Q145(a): one leakage law per card, the slopes re-derived and explained, and what the footing law changes on pool 8 (post hoc)

*Thu 5 Nov 2026 (week 45), about 22:20-23:30 PST, on the Intel, desk only (no card, no lab box), by the lane heat-q145a of Q145(a), round A
(the stock-take's step 3; the card day critic's rank 5). **Everything here is post hoc**: it reads committed files only, with code that
imports nothing of the lab's except the registered reducers and scorer it runs unchanged. It is the evidence behind the footing law's
registration, [`tools/claims-v3/footing-law/FOOTING-LAW.md`](../../../../tools/claims-v3/footing-law/FOOTING-LAW.md) (`c14e5f35`,
22:46:56 PST), and its FL7 study, run after that commit. No registered verdict changes. It answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6**, with **items 8 and 9**.*

## Results

**1. Every committed slope, re-derived from its committed data by this lane's own code.**

| slope | card, clock, minion voltage | die temperature | method (what it measures) | committed | re-derived here |
|---|---|---|---|---|---|
| E44 (25-26 Sep) | aifoundry3, 600 MHz, 523 mV | 58-62 °C | dedicated idle cycles: board W on the firmware reading over a cooling of minutes, one line per cycle, the median | 0.3799 | **0.3799** (raw telemetry) |
| E71 (27 Oct) | aifoundry3, 600 MHz, 523 mV | 58-62 / 51-58 °C | the same, six cycles | 0.3803 / 0.3200 | **0.3803 / 0.3200** (162 per-cycle band fits of E44, E66, E71 to 7e-15) |
| E66 (26-27 Oct) | aifoundry2, 600 MHz (its idle), 519 mV | 51-58 / 58-62 °C | the same, 18 cycles | 0.2936 / 0.3452 | **0.2936 / 0.3452** |
| E44 on card 1 (25-26 Sep) | aifoundry1 card 1, 600 MHz, 499 mV | 58-62 / 56-66 °C | the same, three cycles (never fitted before) | none | **0.5313 / 0.5092** |
| E97's pooled law (1 Nov) | aifoundry3, 600 MHz, 523 mV | 50.5-64.8 °C | the rests after its holds: 0.5 °C bins of the 34-sensor mean, a quadratic | 0.3498 at 58 °C | **the same quadratic to 1.2e-12** (22,726 samples, 30 bins) |
| Q139(u)'s footing (3 Nov) | aifoundry3 / card 1, 600 MHz | 58.0-58.9 / 55-59 °C | 1 s idle brackets before each run, one line per card with an intercept per pass | 0.2056 / 0.3134 | **0.20564 / 0.31341** (2,334 rests in 49 passes; card 1's 2,687 of 2,700 in the 61 of 74 passes with two or more); reverse regressions **0.455 / 0.512** |
| E60's in-run slopes (20 Oct) | aifoundry3 600 MHz 521.8 mV; aifoundry2 800 MHz 617.4 mV; card 0 800 MHz 603.9 mV | 58-61 °C | board W on the firmware reading inside each ~4 s run, the median over runs | 0.203 / 0.442 / 0.327 | **0.2026 / 0.4420 / 0.3273** (149 / 179 / 229 runs) |
| E171's and E172's own (5 Nov) | aifoundry3 / card 1, 600 MHz | 58-61 °C | the in-run median (`--leak auto`), dips removed | 0.2850 / 0.4030 | **0.2850 / 0.4030** (dips kept 0.2898 / 0.3950) |
| E171's and E172's own rests | aifoundry3 / card 1 | 58-59 °C | Q139(u)'s F1 on the session alone | none | 0.127 [0.105, 0.160] / 0.242 [0.217, 0.266]; reverse 0.613 / 0.466 |

**2. Why they disagree, in physical terms: one law, read by three estimators.**
- *A slope of total board power on the die reading across a cooling of minutes, no launch* (E44, E66, E71, E97): the package cools as a
  whole, so the reading follows the temperature the leakage sees, at a fixed clock and voltage. Pooled, aifoundry3's nine cycles give
  0.3509 W/°C at 58 °C and E97's rests (another sensor, another week) 0.3498: one quasi-static law, rising about 0.012 W/°C per °C as
  leakage's exponential does. Only that law closes E97's steady heat balance: (board rise − leakage) / (S × share) = 0.990 / 0.991 / 1.001
  with it, 1.149 / 1.169 / 1.232 with the footing's 0.2056, 1.048 / 1.064 / 1.127 with E171's own 0.285 (`law.json` › `E97_closure`).
- *Across the rests of a pass* (Q139(u)): the same quantity over a 0.33 °C spread that the launch gate enforces, read by a whole degree
  averaged over 1 s; the reading's error is a large part of the spread (within-pass R² 0.45), so least squares is diluted. The law at the
  rests' temperatures lies between the fit and its reverse regression on both cards; a Monte Carlo with the law's slope reproduces the
  pattern (OLS 0.21-0.22 and 0.28-0.31 under reverse regressions of 0.53-0.70; `sim.json`).
- *Inside a run* (E60, a session's own): one line per ~4 s run while the reading climbs about 1.5 °C, one or two whole degrees. The
  per-run fits fall when the trace starts later (aifoundry3 0.203 → 0.124 → 0.096 W/°C from 0.8 / 1.5 / 2.0 s; E171 0.290 → 0.233 → 0.183;
  E172 0.395 → 0.377 → 0.303; aifoundry2 at 800 MHz 0.442 → 0.400 → 0.340; card 0 0.327 → 0.271 → 0.226), and the Monte Carlo gives
  0.29-0.59 of the true slope. The ensemble of the same runs (the mean profile of hundreds of launches) climbs 0.30-0.54 W per degree on
  aifoundry3 and 0.54-0.62 on card 1 over 1-4 s, at or above the law (`law.json` › `ensemble_inrun`). The 34 raw codes, where a session had
  them (E97's four fp32 random steps), rise with the firmware reading (1.07 times it over 1-3 s; `inrun.json` › `sensor_test`).
- *The clock and voltage at the time:* aifoundry2's 0.442 is the in-run estimator at 800 MHz and 617 mV, against its 600 MHz idle law at
  519 mV (0.338 at 58 °C). Leakage rises with voltage, so the direction is right, but the method differs (it reads aifoundry3 at about 0.56
  of its law), so it is a referral for its own use in `surface_hpl.py` (each burst sample referred within its burst), kept there as the
  check at that point, not a law.
- *Card to card:* at 58-62 °C and 600 MHz, aifoundry2 0.345, aifoundry3 0.380 and card 1 0.531 W/°C: card 1, at the lowest voltage (499 mV),
  leaks most; its idle board power is also the highest (about 34 W at 61 °C against about 27 W on aifoundry3). Process spread, not voltage.

**3. FL7: what the footing law changes on pool 8's two 600 MHz sessions.** The law's slope at each session's own temperature (E171 0.3601
W/°C at T_mid 58.775 °C; E172 0.4930 at 58.85 °C) through the registered reducers and scorer, with each committed primary re-scored by the
same route as a control (both reproduce every committed verdict). The arm is measured on the law while M10 and M9 stay fitted on Q139(u)'s
footing; the **one-footing companion** removes that train/test mismatch to first order (every unscaled prediction × f = 1 − c1 Δk, c1
0.1234 / 0.1133 °C per W from the committed arms, f 0.9809 / 0.9796), reproducing the arm exactly at f = 1. W, d = rms(M10) − rms(other):

| rule | E171 committed (k 0.2056) | E171 law arm (0.3601) | E171 one-footing | E172 committed (0.3134) | E172 law arm (0.4930) | E172 one-footing |
|---|---|---|---|---|---|---|
| passes kept; s | 4; 1.0061 | 3 (17113 set aside: int8 zeros +0.268 W off their line); 0.9858 | 3 | 3; 1.0080 | 4 (17213 kept); 0.9853 | 4 |
| **M1** (M10 − M9) | BETTER −0.065 [−0.122, −0.012] | BETTER −0.097 [−0.155, −0.037] | **BETTER −0.052 [−0.105, −0.004]** | BETTER −0.080 [−0.134, −0.034] | BETTER −0.081 [−0.137, −0.024] | **BETTER −0.058 [−0.107, −0.015]** |
| M1f (floats) | BETTER −0.091 | BETTER −0.139 | BETTER −0.071 | BETTER −0.112 | BETTER −0.129 | BETTER −0.084 |
| **A1** (scale − a priori) | BETTER −0.062 [−0.093, −0.033] | BETTER −0.075 [−0.144, −0.001] | **BETTER −0.047 [−0.074, −0.020]** | BETTER −0.095 [−0.135, −0.050] | NOT RESOLVED −0.061 [−0.122, +0.008] | **BETTER −0.058 [−0.090, −0.022]** |
| **KA** (Σe² term a < a priori) | PASS 0.047 < 0.128 | PASS 0.037 < 0.163 | **PASS 0.037 < 0.094** | PASS 0.037 < 0.197 | PASS 0.031 < 0.100 | **PASS 0.031 < 0.120** |
| B2 (int8 bias) | PASS +0.035 | PASS −0.093 | PASS +0.027 | PASS +0.005 | FAIL HIGH −0.167 | PASS −0.044 |
| B1 (float bias) | FAIL LOW +0.092 | FAIL LOW +0.078 | FAIL LOW +0.078 | FAIL LOW +0.105 | FAIL LOW +0.074 | FAIL LOW +0.074 |

**P8-KA pooled** over the two: committed PASS (0.084 < 0.325 W²), the law arm PASS (0.069 < 0.263), the one-footing companion PASS (0.069 <
0.214). In the law arm E171's P2 also moves FAIL → PASS (0.238 → 0.215 W) and LG reads GAIN (E171) and BOTH (E172).

**So M1 BETTER and term a's carry (A1, KA, pooled KA) survive on the leakage law, on both cards, once the model and the data share one
footing.** The same companion turns the committed session-own arms' readings around: E171 at its own 0.2850, M1 NOT RESOLVED → BETTER
(−0.062), A1 NOT RESOLVED → BETTER (−0.060), KA FAIL → PASS; E172 at its own 0.4030, M1 → BETTER (−0.077), A1 → BETTER (−0.088), KA →
PASS (`fl7/companion-*-own.json`). The 5 Nov caveat ("on each session's own slope they read NOT RESOLVED, and KA fails") was mostly the
arms' mismatch: M9 and the a-priori arm, which no session scale absorbs, shifted by c1 Δk × D while M10's scale moved with the data.

**4. The heat chain's loop gain** is unchanged under the law (FL2: the chain keeps E97's law, the same law within 0.003 W/°C): g = R × k(T) =
0.272 at 55 °C, 0.304 at 58, 0.347 at 62, 0.390 at 66. Had the loop taken the footing's slope it would read 0.179 everywhere, and E97's
heat balance would miss by 15-23%.

**5. The first blind tests** (FOOTING-LAW.md): the law, by M11's next aifoundry3 session's rests (its slope at 52-58 °C within ±0.02 W/°C of
0.280-0.351); the footing's consequences, by the next 600 MHz kinds session with FL3's arm frozen in its registration.

## What this cannot say

- **The one-footing companion is first order.** It treats a slope change as a gain c1 Δk on every row; the zeros' own rise, the dips and
  the pass gates (E171's third pass set aside at the law's k) are second order. The exact test refits M10 on rows re-reduced by FL3 ("M10
  on the law"), owed. Nothing here is blind: the law's sources, the sessions and the arms were all seen before the rule was written.
- **Card 1's law rests on three cycles of one September session** (bootstrap [0.412, 0.500] W/°C at 58 °C); its first check is a cooling
  at the end of its next kinds session.
- The ensemble in-run slope is a few points of a mean profile; it brackets the law, it does not measure it.

## Files and how to reproduce

`run_posthoc.sh <scratch>` re-runs everything from the lab clone's top (Python 3.9 with numpy). The scripts: `rederive_idle.py` (the
cycles), `rederive_e97.py` (E97's law), `footing_inrun.py` (the in-run and rest slopes, Q139(u)'s footing, the sensor test),
`profile_inrun.py` (the run profile), `law_rule.py` (the laws, the sessions' T_mid, s against k, E97's closure, the loop gain, the
ensemble slope), `sim_attenuation.py` (the estimators' Monte Carlo), `companion_fl7.py` (the one-footing companion). Their outputs:
`idle.json`, `e97-law.json`, `inrun.json`, `profile.json`, `law.json`, `sim.json`; and `fl7/` (the two law reductions with their runs, logs
and text, the registered scorer's output on the law arms, the controls and the committed session-own arms, the pooled KA readings and the
companions). In the E172 scored files, the one path of this lane's scratch copy of `ccheck/ccheck-session.json.gz` is replaced by a label.
`SHA256SUMS` lists every file.

SPDX-License-Identifier: Apache-2.0
