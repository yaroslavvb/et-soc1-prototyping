# E207 scored for MM1-v2: its frozen E207 column on E207's data, beside MM1-v1, F1 and F2 (REPORTED)

*Tue 17 Nov 2026 (week 47), PST. Q206's lane `score-v2-e207`, at the desk on aifoundry2: no card claimed, no device command sent, no simulator run. The lane's own code (`score_v2_e207.py`: standard library only, importing nothing from E207's kit or from any model) compares every E207 run with MM1-v2's frozen E207 column and, beside it, with MM1-v1's, F1's and F2's frozen forecasts. It checks every input's sha256 first. **MM1-v2's label: BLIND**, as its freeze lane labelled it (`FREEZE-e207.md`). E207's registered rules (T1-T3, E1-E4, H1-H4) apply to MM1-v1, F1 and F2 only, so every MM1-v2 figure here is REPORTED, not a registered verdict. Every figure compares a value measured by E207 (its committed data) with a frozen forecast. Readings marked post hoc were made after the data.*

## 0. On one screen

- **Cycles an op, the wall** (per case): MM1-v2 4.8% rms (-1.0%); MM1-v1 5.6% rms (-2.5%); F1 18.1% rms (+14.0%).
- **Cycles an op, the counter's mean** (per case): MM1-v2 5.0% rms (-0.9%); MM1-v1 5.9% rms (-2.4%); F1 21.1% rms (+18.5%).
- **Seconds a GEMM** (per case): MM1-v2 4.8% rms (-1.1%); MM1-v1 5.7% rms (-2.6%); F1 18.0% rms (+13.9%) (F2's seconds are F1's).
- **J over idle given the measured seconds** (points at 3 W and above): MM1-v2 4.8% rms (-0.7%); MM1-v1 5.4% rms (-2.1%); F1 25.3% rms (-24.4%); F2 52.7% rms (+25.8%); at b34, b38, b40 in watts: MM1-v2 0.168 W rms (+0.146 W); MM1-v1 0.225 W rms (+0.210 W); F1 0.215 W rms (-0.210 W); F2 0.281 W rms (-0.260 W).
- **J over idle with the seconds forecast** (3 W and above): MM1-v2 5.2% rms (-0.9%); MM1-v1 5.8% rms (-2.4%); F1 16.4% rms (-13.8%); F2 52.7% rms (+25.7%).
- **J with the card at rest**, given the measured seconds: MM1-v2 1.9% rms (-0.2%); MM1-v1 2.1% rms (-0.7%); F1 9.2% rms (-8.6%); F2 17.5% rms (+8.4%); with the seconds forecast: MM1-v2 4.6% rms (-1.1%); MM1-v1 5.3% rms (-2.8%); F1 10.0% rms (+3.6%); F2 26.7% rms (+16.9%).
- **Like with like** (energy on the points MM1-v2 and MM1-v1 both price): J over idle given the measured seconds MM1-v2 4.8% rms (-0.7%) n46; MM1-v1 5.4% rms (-2.3%) n46; F1 25.5% rms (-25.0%) n44; F2 52.7% rms (+25.8%) n46; with the seconds forecast MM1-v2 5.2% rms (-0.9%) n46; MM1-v1 5.8% rms (-2.6%) n46; F1 16.3% rms (-14.2%) n44; F2 52.7% rms (+25.7%) n46; J at rest given MM1-v2 1.9% rms (-0.2%) n49; MM1-v1 2.1% rms (-0.8%) n49; F1 9.3% rms (-8.8%) n47; F2 17.5% rms (+8.4%) n49, forecast MM1-v2 4.6% rms (-1.1%) n49; MM1-v1 5.4% rms (-2.8%) n49; F1 10.2% rms (+3.7%) n47; F2 26.7% rms (+16.9%) n49. On the points all four models price: J over idle given MM1-v2 4.8% rms (-0.7%) n44; MM1-v1 5.4% rms (-2.3%) n44; F1 25.5% rms (-25.0%) n44; F2 53.2% rms (+25.8%) n44.
- **MM1-v2 against MM1-v1, case by case** (REPORTED): wall cycles MM1-v2 closer at 24, MM1-v1 at 18, 5 tied (sign test p 0.44: NOT DECIDED; families 5/1/1: NOT DECIDED); counter's mean MM1-v2 closer at 25, MM1-v1 at 18, 4 tied (sign test p 0.36: NOT DECIDED; families 4/2/1: NOT DECIDED); seconds MM1-v2 closer at 26, MM1-v1 at 16, 5 tied (sign test p 0.16: NOT DECIDED; families 5/1/1: NOT DECIDED); J over idle given t MM1-v2 closer at 28, MM1-v1 at 19, 2 tied (sign test p 0.24: NOT DECIDED; families 4/2/2: NOT DECIDED); with t forecast MM1-v2 closer at 28, MM1-v1 at 20, 1 tied (sign test p 0.31: NOT DECIDED; families 4/3/1: NOT DECIDED).
- **Both against F1 and F2**: MM1-v2 vs F1 on the wall MM1-v2 closer at 40, F1 at 6, 1 tied (sign test p 3.1e-07: MM1-v2 BETTER; families 7/0/0: MM1-v2 BETTER); MM1-v1 vs F1 on the wall (H1) MM1-v1 closer at 39, F1 at 8, 0 tied (sign test p 5.5e-06: MM1-v1 BETTER; families 7/0/0: MM1-v1 BETTER); MM1-v2 vs F2 on J over idle given t MM1-v2 closer at 48, F2 at 1, 0 tied (sign test p 1.8e-13: MM1-v2 BETTER; families 8/0/0: MM1-v2 BETTER); MM1-v1 vs F2 (H3) MM1-v1 closer at 47, F2 at 2, 0 tied (sign test p 4.4e-12: MM1-v1 BETTER; families 8/0/0: MM1-v1 BETTER); with t forecast MM1-v2 vs F2 MM1-v2 closer at 48, F2 at 0, 1 tied (sign test p 7.1e-15: MM1-v2 BETTER; families 8/0/0: MM1-v2 BETTER), MM1-v1 vs F2 (H4) MM1-v1 closer at 47, F2 at 2, 0 tied (sign test p 4.4e-12: MM1-v1 BETTER; families 8/0/0: MM1-v1 BETTER).
- **E207's registered verdicts** (its frozen scorer, run by the card lane after the data commit; not this lane's): R0, T1-T3, E1-E4 and S6 PASS; H1-H4 MM1-v1 BETTER. This lane's code reproduces H1-H4's counts and every d, and MM1-v1's T1-E4 pass counts, exactly (section 8).
- **Coverage:** MM1-v2 forecasts time at all 47 cases and energy at 49 of the 53 points. Its energy is NOT FORECAST at b49-b52 (the blind4 and blind3 kinds). MM1-v1 prices all 53 points, F1 50 (no e37 or blind3 rule) and F2 49 (no blind4 or blind3 row).
- **The day's largest misses** (post hoc, section 6) are shared by both MM1 versions: int8 inside the L3 runs about 6.4% slower than fp32 at the same shape where both forecast them equal, int8 at one K block, the stride step at NB 8, and the joules of the 3x5x1 shapes at one K block. MM1-v2's subset term fixed MM1-v1's two 1x2x2 subset misses.

## 1. The label, the times and the freeze lines

- **MM1-v2 (BLIND).** Its E207 column (`forecasts-e207.csv`, sha256 `873360bb...`) was frozen in commit `4e518735`. Q202's lane `mm1v2-e207` pushed it to GitHub at 02:06:33 PST Tue 17 Nov 2026, made by the landed predictor unchanged (`3ca4b717`). Its note `FREEZE-e207.md` reads **'Blindness: BLIND'**: before the push no lane had booked aifoundry3 for E207, E207's card lane had not started, and no E207 datum was in any ref. E207's first card command came 5 h 0 min 11 s later, at 07:06:44 PST.
- **MM1-v1, F1 and F2 (BLIND).** They were frozen in commit `25d2e74e`, pushed at 21:14:57 PST Mon 16 Nov 2026 (E207.md section 0).
- **E207's day** (the card lane's record): aifoundry3 card 0 at its pinned 600 MHz. The first card command was at 07:06:44 and the session ended at 07:53:54 PST Tue 17 Nov 2026, 47.16 card-minutes. The smoke and 109 of 109 runs ran in the registered order, with no stop and nothing set. The data commit `867f6a3f` was pushed at 07:58:58 PST (`docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/`); its SHA256SUMS read 589 of 589 OK here. All 106 point runs (two a point) were kept.
- **No 'ran before' labels.** Step 6n's one TO DATE point, b50, was dated by its records' own session starts: 05:30:01 and 06:16:04 PST Tue 17 Nov 2026 (the model session's second sweep, on aifoundry1 cards 1 and 0). Both are after MM1-v1's freeze, and after MM1-v2's too. So b50 stays in every comparison here, and MM1-v2 is blind there as well (the data directory's `ranbefore-e207-labels.json` and its dated note 1).
- **The model session's sealed E207 forecast** (registered in `221a233f` before the first card command) is theirs to score; this lane did not read it.
- **F2's given()** is F2's J over idle at each point's measured seconds and starting die, run through E206's route. It is a model computation, and this lane does not repeat it. It is read from E207's registered scorer output (the card lane's step 13, sha256 `be47e045...`, not yet committed when read) and copied exactly into `f2-given-e207.json`.

| input | path | sha256 |
|---|---|---|
| E207's committed data | `docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json` | `e89d4149b95fa2b3ef5172e8f8dadf7eb0266fff63a7d9e4c7b906fb31ee5d35` |
| F1's and F2's frozen forecasts | `tools/matmul/mm1/v1/out/f1f2_blind_day.json` | `2f252ebdfd0ada66684a71adceb2f227ca559818b1bfb188322378296641a3d0` |
| the same, one row a point | `tools/matmul/mm1/v1/out/f1f2_blind_day.csv` | `8ff5e73a077e02513b15ff15a4067ab839186b3b56519118e6774376b5a46645` |
| F2's given() copied from E207's registered scorer output | `tools/matmul/mm1/v2/f2-given-e207.json` | `f6158ffc1bd8ee7278a2988cd78230718c757a19b2cfb6db86c43abcd79c2746` |
| E207's points (registration) | `tools/claims-v3/e207/points-e207.json` | `2a905b4ec9e6295bdce5f55a67669d247f11bdc475e9ab51873f68ad02b899e1` |
| E207's rules (registration) | `tools/claims-v3/e207/rules-e207.json` | `ffeb322e9d83e46bf41cdf55ecd4a5e5e1d42e30b07ba56f52d1c8fa6f881dec` |
| MM1-v1's frozen forecasts | `tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv` | `90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6` |
| MM1-v2's frozen E207 column | `tools/matmul/mm1/v2/forecasts-e207.csv` | `873360bb7ef028c4922f6f55c6c61133a32da28fa6e19a6a02fa7f77d45d63d3` |

## 2. How it was scored

- **Measured** (E207.md section 7, recomputed here from `data-e207.json`). A run is kept when its host record matches its point (arm, type, minions, and the shire mask read as a number) and it carries t_gemm, p_work and p_rest. Per run: t = t_gemm; cycles an op on the wall = cycles_gemm / ops a minion a GEMM; the counter's mean = the host's cycles_per_op; W over idle = p_work - p_rest; J over idle = W x t; J with the card at rest = p_work x t. A point is the mean of its kept runs, and a case (shape, format, mask) the mean of its points.
- **Given the measured seconds.** For MM1-v1 and MM1-v2, W = A + B / t_op at the point's measured t (t_op in us an op), and J over idle = W x t. For F1 it is its frozen W x t, and for F2 the registered given(). J at rest given = the measured rest x t + J over idle given.
- **With the seconds forecast.** Each model's frozen W and J over idle are used, and J at rest = the measured rest x the model's seconds + its frozen J. F2's seconds are F1's.
- **Error** = forecast / measured - 1, the MM1 READMEs' convention. Its rms and bias (the mean) are in %, per case for time and per point for energy. At the three points under 3 W over idle (b34, b38, b40), W and J over idle are scored in watts (forecast - measured), as E207 registered.
- **Head to head.** d = |ln(measured / other)| - |ln(measured / first)|, with E207's ties (0.001 in ln for cycles and seconds, 0.005 for joules, 0.05 W at the watts points) and the exact two-sided sign test on the untied cases or points. Beside it is E207.md A1 item 5's family-level check: per family the median d, and a sign test over the untied families (TOO FEW under 5).
- **Pins.** Every input's sha256 is checked before use; otherwise the scorer refuses with exit 4 (section 1's table).
- **Per run.** Every kept run is compared with its point's forecast. F2's given() exists per point only.

## 3. Every model on every quantity

Error = forecast / measured - 1; **rms (bias)** in %, over E207's distinct cases for time (the mean of a case's points; a point the mean of its runs) and its points for energy; W and J over idle relative at the points at 3 W over idle and above, in watts at b34, b38 and b40 (forecast - measured); n beside. Labels: MM1-v2 **BLIND**; MM1-v1, F1 and F2 **BLIND**. Every MM1-v2 figure is REPORTED, not a registered rule.

| quantity | MM1-v2 | MM1-v1 | F1 | F2 | n (v2 / v1 / F1 / F2) |
|---|---|---|---|---|---|
| cycles an op, the wall (per case) | 4.80% (-1.02) | 5.62% (-2.52) | 18.07% (+14.00) | - | 47 / 47 / 47 / 0 |
| cycles an op, the counter's mean (per case) | 5.01% (-0.86) | 5.93% (-2.37) | 21.10% (+18.51) | - | 47 / 47 / 47 / 0 |
| seconds a GEMM (per case) | 4.81% (-1.12) | 5.66% (-2.62) | 17.97% (+13.89) | 17.97% (+13.89) | 47 / 47 / 47 / 47 |
| W over idle given the measured seconds (>= 3 W) | 4.82% (-0.71) | 5.42% (-2.11) | 25.26% (-24.39) | 52.74% (+25.84) | 46 / 50 / 47 / 46 |
| W over idle with the seconds forecast (>= 3 W) | 4.33% (+0.13) | 4.92% (-0.22) | 25.26% (-24.39) | 36.22% (+8.34) | 46 / 50 / 47 / 46 |
| J over idle given the measured seconds (>= 3 W) | 4.82% (-0.71) | 5.42% (-2.11) | 25.26% (-24.39) | 52.74% (+25.84) | 46 / 50 / 47 / 46 |
| J over idle with the seconds forecast (>= 3 W) | 5.15% (-0.87) | 5.80% (-2.43) | 16.44% (-13.78) | 52.68% (+25.74) | 46 / 50 / 47 / 46 |
| W over idle given the seconds at b34, b38, b40 (watts) | 0.168 W (+0.146) | 0.225 W (+0.210) | 0.215 W (-0.210) | 0.281 W (-0.260) | 3 / 3 / 3 / 3 |
| W over idle with the seconds forecast at b34, b38, b40 (watts) | 0.189 W (+0.176) | 0.365 W (+0.335) | 0.215 W (-0.210) | 0.290 W (-0.286) | 3 / 3 / 3 / 3 |
| J with the card at rest given the measured seconds | 1.92% (-0.25) | 2.13% (-0.73) | 9.21% (-8.62) | 17.45% (+8.38) | 49 / 53 / 50 / 49 |
| J with the card at rest with the seconds forecast | 4.60% (-1.13) | 5.34% (-2.79) | 10.01% (+3.64) | 26.68% (+16.94) | 49 / 53 / 50 / 49 |

Per run (every kept run against its point's forecast; F2's given() exists per point only):

| quantity, per run | MM1-v2 | MM1-v1 | F1 | F2 |
|---|---|---|---|---|
| cycles an op, the wall | 4.67% (-1.14) | 5.44% (-2.55) | 17.57% (+13.80) | - |
| cycles an op, the counter's mean | 4.92% (-1.14) | 5.79% (-2.56) | 21.01% (+18.70) | - |
| seconds a GEMM | 4.68% (-1.24) | 5.48% (-2.65) | 17.47% (+13.69) | 17.47% (+13.69) |
| J over idle given the run's seconds (>= 3 W points) | 4.85% (-0.70) | 5.44% (-2.11) | 25.26% (-24.39) | - |
| J over idle with the seconds forecast (>= 3 W points) | 5.18% (-0.87) | 5.83% (-2.43) | 16.45% (-13.77) | 52.68% (+25.75) |
| J at rest given the run's seconds | 1.93% (-0.25) | 2.14% (-0.73) | 9.21% (-8.62) | - |
| J at rest with the seconds forecast | 4.60% (-1.13) | 5.34% (-2.79) | 10.01% (+3.65) | 26.68% (+16.94) |

Like with like (energy on common point sets; each model's n beside):

| set | quantity | MM1-v2 | MM1-v1 | F1 | F2 |
|---|---|---|---|---|---|
| the points MM1-v2 and MM1-v1 both price | J over idle given the measured seconds (>= 3 W) | 4.82% (-0.71) n46 | 5.38% (-2.29) n46 | 25.51% (-24.98) n44 | 52.74% (+25.84) n46 |
| the points MM1-v2 and MM1-v1 both price | J over idle with the seconds forecast (>= 3 W) | 5.15% (-0.87) n46 | 5.82% (-2.60) n46 | 16.29% (-14.16) n44 | 52.68% (+25.74) n46 |
| the points MM1-v2 and MM1-v1 both price | J at rest given the measured seconds | 1.92% (-0.25) n49 | 2.10% (-0.76) n49 | 9.30% (-8.81) n47 | 17.45% (+8.38) n49 |
| the points MM1-v2 and MM1-v1 both price | J at rest with the seconds forecast | 4.60% (-1.13) n49 | 5.42% (-2.79) n49 | 10.15% (+3.70) n47 | 26.68% (+16.94) n49 |
| the points all four price | J over idle given the measured seconds (>= 3 W) | 4.83% (-0.68) n44 | 5.41% (-2.29) n44 | 25.51% (-24.98) n44 | 53.15% (+25.82) n44 |
| the points all four price | J over idle with the seconds forecast (>= 3 W) | 5.17% (-0.84) n44 | 5.86% (-2.60) n44 | 16.29% (-14.16) n44 | 53.09% (+25.72) n44 |
| the points all four price | J at rest given the measured seconds | 1.92% (-0.23) n47 | 2.12% (-0.76) n47 | 9.30% (-8.81) n47 | 17.59% (+8.39) n47 |
| the points all four price | J at rest with the seconds forecast | 4.66% (-1.13) n47 | 5.51% (-2.83) n47 | 10.15% (+3.70) n47 | 26.85% (+16.91) n47 |

At the two e37 points MM1-v2 is -5.8% (b42) and +3.0% (b43) on J over idle given the measured seconds (MM1-v1 -6.4% and +1.9%; F2 -7.4% and +60.0%). F2's seconds are F1's, so its seconds column repeats F1's.

## 4. Head to head

d = |ln(measured / other)| - |ln(measured / first)| per case (time) or point (energy; watts at b34, b38, b40 for W and J over idle); the first model is closer where d exceeds E207's registered tie (0.001 in ln for cycles and seconds, 0.005 for joules, 0.05 W), the other where d is below minus the tie; the exact two-sided sign test on the untied. **Every line with MM1-v2 in it is REPORTED.** The MM1-v1 lines against F1 (wall, counter's mean) and F2 (J over idle) are E207's registered H1-H4 recomputed by this lane's code (section 8 compares them with the registered scorer's).

| comparison | quantity | first closer | other closer | ties | p (two-sided) | reading | median d (ln) | families (first / other / tied): reading |
|---|---|---|---|---|---|---|---|---|
| MM1-v2 vs MM1-v1 | cycles, the wall | 24 | 18 | 5 | 0.441 | NOT DECIDED | +0.0050 | 5 / 1 / 1: NOT DECIDED |
| MM1-v2 vs MM1-v1 | cycles, the counter's mean | 25 | 18 | 4 | 0.36 | NOT DECIDED | +0.0050 | 4 / 2 / 1: NOT DECIDED |
| MM1-v2 vs MM1-v1 | seconds | 26 | 16 | 5 | 0.164 | NOT DECIDED | +0.0050 | 5 / 1 / 1: NOT DECIDED |
| MM1-v2 vs MM1-v1 | J over idle given t | 28 | 19 | 2 | 0.243 | NOT DECIDED | +0.0073 | 4 / 2 / 2: NOT DECIDED |
| MM1-v2 vs MM1-v1 | J over idle, t forecast | 28 | 20 | 1 | 0.312 | NOT DECIDED | +0.0079 | 4 / 3 / 1: NOT DECIDED |
| MM1-v2 vs MM1-v1 | J at rest given t | 17 | 6 | 26 | 0.0347 | MM1-v2 BETTER | +0.0025 | 2 / 0 / 6: TOO FEW |
| MM1-v2 vs MM1-v1 | J at rest, t forecast | 30 | 11 | 8 | 0.00432 | MM1-v2 BETTER | +0.0065 | 5 / 0 / 3: NOT DECIDED |
| MM1-v2 vs MM1-v1 | W over idle, t forecast | 21 | 20 | 8 | 1 | NOT DECIDED | -0.0026 | 2 / 2 / 4: TOO FEW |
| MM1-v2 vs F1 | cycles, the wall | 40 | 6 | 1 | 3.1e-07 | MM1-v2 BETTER | +0.1399 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F1 | cycles, the counter's mean | 44 | 3 | 0 | 2.46e-10 | MM1-v2 BETTER | +0.1603 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F1 | seconds | 40 | 6 | 1 | 3.1e-07 | MM1-v2 BETTER | +0.1377 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F1 | J over idle given t | 46 | 1 | 0 | 6.82e-13 | MM1-v2 BETTER | +0.2482 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F1 | J over idle, t forecast | 44 | 3 | 0 | 2.46e-10 | MM1-v2 BETTER | +0.0946 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F1 | J at rest given t | 46 | 0 | 1 | 2.84e-14 | MM1-v2 BETTER | +0.0891 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F1 | J at rest, t forecast | 35 | 10 | 2 | 0.000247 | MM1-v2 BETTER | +0.0545 | 6 / 1 / 0: NOT DECIDED |
| MM1-v2 vs F1 | W over idle, t forecast | 46 | 1 | 0 | 6.82e-13 | MM1-v2 BETTER | +0.2610 | 7 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F2 | J over idle given t | 48 | 1 | 0 | 1.78e-13 | MM1-v2 BETTER | +0.2546 | 8 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F2 | J over idle, t forecast | 48 | 0 | 1 | 7.11e-15 | MM1-v2 BETTER | +0.2533 | 8 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F2 | J at rest given t | 47 | 1 | 1 | 3.48e-13 | MM1-v2 BETTER | +0.1094 | 8 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F2 | J at rest, t forecast | 44 | 2 | 3 | 3.08e-11 | MM1-v2 BETTER | +0.1883 | 8 / 0 / 0: MM1-v2 BETTER |
| MM1-v2 vs F2 | W over idle, t forecast | 44 | 4 | 1 | 1.51e-09 | MM1-v2 BETTER | +0.1998 | 8 / 0 / 0: MM1-v2 BETTER |
| MM1-v1 vs F1 | cycles, the wall | 39 | 8 | 0 | 5.54e-06 | MM1-v1 BETTER | +0.1279 | 7 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F1 | cycles, the counter's mean | 45 | 2 | 0 | 1.6e-11 | MM1-v1 BETTER | +0.1474 | 7 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F1 | seconds | 39 | 8 | 0 | 5.54e-06 | MM1-v1 BETTER | +0.1278 | 7 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F1 | J over idle given t | 48 | 2 | 0 | 2.27e-12 | MM1-v1 BETTER | +0.2551 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F1 | J over idle, t forecast | 45 | 2 | 3 | 1.6e-11 | MM1-v1 BETTER | +0.0891 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F1 | J at rest given t | 46 | 2 | 2 | 8.36e-12 | MM1-v1 BETTER | +0.0807 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F1 | J at rest, t forecast | 34 | 15 | 1 | 0.0094 | MM1-v1 BETTER | +0.0482 | 6 / 2 / 0: NOT DECIDED |
| MM1-v1 vs F1 | W over idle, t forecast | 46 | 1 | 3 | 6.82e-13 | MM1-v1 BETTER | +0.2385 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F2 | J over idle given t | 47 | 2 | 0 | 4.36e-12 | MM1-v1 BETTER | +0.2609 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F2 | J over idle, t forecast | 47 | 2 | 0 | 4.36e-12 | MM1-v1 BETTER | +0.2601 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F2 | J at rest given t | 45 | 2 | 2 | 1.6e-11 | MM1-v1 BETTER | +0.1017 | 8 / 0 / 0: MM1-v1 BETTER |
| MM1-v1 vs F2 | J at rest, t forecast | 37 | 8 | 4 | 1.54e-05 | MM1-v1 BETTER | +0.1701 | 7 / 0 / 1: MM1-v1 BETTER |
| MM1-v1 vs F2 | W over idle, t forecast | 42 | 3 | 4 | 8.65e-10 | MM1-v1 BETTER | +0.2003 | 8 / 0 / 0: MM1-v1 BETTER |
| F1 vs F2 | J over idle given t | 24 | 21 | 2 | 0.766 | NOT DECIDED | +0.0037 | 4 / 3 / 0: NOT DECIDED |
| F1 vs F2 | J over idle, t forecast | 42 | 4 | 1 | 5.1e-09 | F1 BETTER | +0.1506 | 6 / 1 / 0: NOT DECIDED |
| F1 vs F2 | J at rest given t | 26 | 16 | 5 | 0.164 | NOT DECIDED | +0.0142 | 4 / 2 / 1: NOT DECIDED |
| F1 vs F2 | J at rest, t forecast | 39 | 5 | 3 | 1.41e-07 | F1 BETTER | +0.1037 | 6 / 1 / 0: NOT DECIDED |
| F1 vs F2 | W over idle, t forecast | 23 | 22 | 2 | 1 | NOT DECIDED | -0.0365 | 2 / 4 / 1: NOT DECIDED |

**Reading (REPORTED).** MM1-v2 is closer than MM1-v1 at more cases than not in every time and joule quantity, but no time or J-over-idle comparison between them is decided (p 0.16-0.44). On J with the card at rest the sign test favours MM1-v2 (p 0.035 given the seconds, 0.0043 with the seconds forecast), but the family-level check does not confirm it (TOO FEW; NOT DECIDED). The two versions' forecasts differ little to begin with: 3.2% rms on the wall by mm1v2-e207's desk check before the data. Against F1 and F2, both MM1 versions are closer at nearly every case and point (sign test p below 0.01 in every quantity). No family favours F1 or F2, except in J at rest with the seconds forecast against F1 (one family for MM1-v2, two for MM1-v1).

## 5. By family, format, mask and kind

rms (bias) in % of the wall cycles per case and of J over idle given the measured seconds per point (>= 3 W):

| group | cases | MM1-v2 wall | MM1-v1 wall | F1 cycles | points | MM1-v2 J given | MM1-v1 J given | F1 J given | F2 J given |
|---|---|---|---|---|---|---|---|---|---|
| all | 47 | 4.80% (-1.02) | 5.62% (-2.52) | 18.07% (+14.00) | 50 | 4.82% (-0.71) | 5.42% (-2.11) | 25.26% (-24.39) | 52.74% (+25.84) |
| family=inside | 9 | 4.92% (-3.96) | 4.89% (-3.89) | 9.96% (+9.52) | 9 | 4.49% (-4.22) | 6.27% (-6.21) | 27.10% (-26.77) | 28.42% (-27.12) |
| family=int8 one K block | 3 | 10.38% (-9.53) | 10.11% (-9.23) | 14.79% (-11.36) | 3 | 13.41% (-12.00) | 14.57% (-13.38) | 23.78% (-22.82) | 32.60% (-31.18) |
| family=knee | 9 | 2.64% (+0.74) | 3.42% (-2.61) | 18.49% (+17.26) | 9 | 1.48% (+0.69) | 2.40% (-1.66) | 25.78% (-25.39) | 30.47% (+25.36) |
| family=long K | 3 | 5.52% (+0.62) | 5.74% (-0.97) | 24.96% (+24.42) | 3 | 3.89% (+1.27) | 3.89% (+0.58) | 24.91% (-24.86) | 121.47% (+117.75) |
| family=past | 8 | 1.98% (-0.36) | 2.66% (-0.42) | 19.39% (+19.27) | 8 | 3.43% (+2.46) | 2.54% (+1.08) | 24.05% (-23.97) | 73.91% (+63.07) |
| family=stride | 7 | 3.66% (+0.55) | 4.07% (+1.45) | 17.56% (+13.32) | 7 | 3.12% (+2.30) | 2.26% (+1.31) | 22.23% (-21.42) | 42.89% (+39.38) |
| family=subset | 8 | 5.74% (+0.84) | 8.55% (-4.53) | 21.47% (+16.32) | 5 | 3.95% (-0.30) | 4.73% (-1.88) | 29.68% (-28.96) | 30.55% (+22.45) |
| format=fp16 | 3 | 1.81% (-0.29) | 3.68% (-1.01) | 18.09% (+17.29) | 4 | 3.66% (-0.00) | 4.57% (-2.54) | 25.07% (-24.99) | 28.83% (+14.85) |
| format=fp32 | 27 | 4.05% (+0.75) | 5.11% (-1.12) | 19.49% (+16.90) | 29 | 4.57% (+0.11) | 4.82% (-0.86) | 23.07% (-21.99) | 44.49% (+27.12) |
| format=int8 | 17 | 6.10% (-3.97) | 6.59% (-5.02) | 15.56% (+8.83) | 17 | 5.39% (-2.21) | 6.45% (-4.13) | 28.32% (-27.92) | 67.10% (+25.75) |
| kind=designed:blind3 a_colconst_b_randn | 0 | - | - | - | 1 | - | 7.13% (+7.13) | - | - |
| kind=e37 | 0 | - | - | - | 2 | 4.62% (-1.37) | 4.73% (-2.27) | - | 42.73% (+26.30) |
| kind=random | 0 | - | - | - | 44 | 4.83% (-0.68) | 5.41% (-2.29) | 25.51% (-24.98) | 53.15% (+25.82) |
| kind=real:blind4 | 0 | - | - | - | 3 | - | 5.27% (-2.39) | 21.16% (-15.79) | - |
| mask=full | 39 | 4.59% (-1.41) | 4.80% (-2.11) | 17.29% (+13.53) | 45 | 4.92% (-0.75) | 5.49% (-2.13) | 24.68% (-23.85) | 54.84% (+26.26) |
| mask=subset | 8 | 5.74% (+0.84) | 8.55% (-4.53) | 21.47% (+16.32) | 5 | 3.95% (-0.30) | 4.73% (-1.88) | 29.68% (-28.96) | 30.55% (+22.45) |

## 6. The worst cases, and why

- **int8 inside the L3 (time, both versions; post hoc).** At the four int8 shapes the L3 holds (1x3x2, 2x3x2, 3x2x2, 1x4x3), the card ran 6.3-6.6% more cycles an op on the wall than at the same shapes in fp32, and 4.1-4.3% more on the counter's mean (962.2 against 904.8 at gemmL1x3x2). MM1-v2 and MM1-v1 forecast the two formats equal there (MM1-v2 887.5 at both b01 and b02). So both are 6.3-8.2% low on int8 inside, which is most of the inside family's bias (-4.0% for MM1-v2 over its 9 cases).
- **int8 at one K block (time; post hoc).** n01 (1x3x1 int8) ran 862.2 cycles an op on the wall against MM1-v2's 741.2 (-14.0%; MM1-v1 -13.8%), with the counter's mean as far off (-14.2%): the op itself was slower than MM1-v2's L2 time there. n02 (3x5x1 int8) is -10.4% on the wall (MM1-v1 -10.1%) but only -3.4% on the counter's mean, so there the slowest minion lags: wall over mean 1.091 measured, against MM1-v2's 1.011. Its fp32 twin n03 shows the same lag (1.093 against 1.011; -4.1% on the wall, +3.7% on the mean). MM1-v2's L2 time in cycles, new in v2, left these cases where MM1-v1 had them.
- **The subsets (time; post hoc).** MM1-v2's subset term (contention on the DRAM stream only, new in v2) moved the two 1x2x2 subsets from MM1-v1's -14.0% (0x3) and -10.2% (0xfff) to -0.5% and -0.9%. It also moved the subset family from 8.6% rms (-4.5% bias) to 5.7% (+0.8%). MM1-v2's worst case of the day is 3x6x4 fp32 on 12 shires (0xfff): 947.8 cycles an op measured, +13.3% (MM1-v1 +9.5%, F1 +38.8%). On that mask the shape ran faster than on 2 shires (0x3, 1066.7) or on 24 (0xffffff, 1080.0), which no model forecast.
- **The stride step (time; E207's reading a, read here post hoc).** At K 6 the power-of-two NB 8 shape ran 1.272 times 1x7x6's wall cycles in fp32 (1.251 in int8). MM1-v2 forecast 1.182 and MM1-v1 1.173 (F1 1.000), so MM1-v2 is -4.1% at 1x8x6. At long K the step reversed: 1x8x16 ran 0.937 times 1x7x16 (MM1-v2 1.050, MM1-v1 1.060), so 1x8x16 is MM1-v2's +8.4% (MM1-v1 +7.0%, F1 +31.3%). 1x4x12 over 1x5x10 measured 1.097, against MM1-v2's 1.188.
- **Energy at one K block (both versions; post hoc).** The day's largest misses in J over idle are the 3x5x1 shapes, given the measured seconds: n02 (int8) -18.4% for MM1-v2 (MM1-v1 -19.9%) and n03 (fp32) -13.6% (MM1-v1 -14.3%). The card drew 26.87 W over idle at n03, the most of any point, against MM1-v2's 23.20 W. MM1-v2's map puts 47% of the lines there in the L2 (89.6 of 192), against 8% at gemmL1x3x2 (16 of 192), where it is -6.0%. n01 (1x3x1 int8, 50% in the L2) is only -4.0% off, so the L2 share alone does not explain the miss.
- **Energy inside the L3 (fp32; post hoc).** MM1-v2 is 4.5-6.0% low on J over idle at the four fp32 inside points (b01, b04, b06, b08), and MM1-v1 5.9-7.3% low. That is the inside family's bias: -4.2% for MM1-v2, -6.2% for MM1-v1.
- **The three points under 3 W** (W over idle given the measured seconds, in watts). MM1-v2 is +0.070, +0.108 and +0.260 W at b34, b38 and b40 (MM1-v1 +0.135, +0.175, +0.321; F1 -0.239, -0.246, -0.146; F2 -0.352, -0.318, -0.111). For both MM1 versions b40 (1x2x2 on 0x3) lies outside MM1-v1's 0.215 W band.
- **F1 and F2.** F1 is low on J over idle in every family by about a quarter (bias -24.4% given the seconds; -21% to -29% by family): a scale, not a shape. F2's error grows with the fresh lines: +94% to +160% at the long-K points (n04, n05, n06, b23, b24), against -19% to -42% at one K block. Its byte convention counts every shire's request (E206.md section 5).

## 7. MM1-v2 inside MM1-v1's registered bands (REPORTED, never a verdict)

| band (MM1-v1's, E207.md section 7) | MM1-v2 inside | MM1-v1 inside |
|---|---|---|
| T1 | 46 of 47 | 45 of 47 |
| T2 | 46 of 47 | 44 of 47 |
| T3 | 46 of 47 | 45 of 47 |
| E1 | 46 of 49 | 50 of 53 |
| E2 | 46 of 49 | 48 of 53 |
| E3 | 47 of 49 | 51 of 53 |
| E4 | 47 of 49 | 50 of 53 |

Counts only. E207's registered verdicts on MM1-v1 (every rule PASS at 90% of its cases or points) are the card lane's; no MM1-v2 band was registered, so MM1-v2's counts here are not verdicts.

## 8. Cross-checks of this lane's code

Config B (`score-e207-xcheck-config.json`) reads E207's registered scorer output in place of `f2-given-e207.json`; every other number it gives equals config A's (yes). Against that output: the measured side, 371 fields, worst relative difference 2.1e-16; F2's given() at 49 points.

| registered rule | registered (MM1-v1 closer / other closer / ties: verdict) | this code | counts equal | d compared | worst abs d difference (ln rows; watts rows, W) |
|---|---|---|---|---|---|
| H1 | 39 / 8 / 0: MM1-v1 BETTER | 39 / 8 / 0: MM1-v1 BETTER | yes | 47 | 5.0e-16; 0.0e+00 |
| H2 | 45 / 2 / 0: MM1-v1 BETTER | 45 / 2 / 0: MM1-v1 BETTER | yes | 47 | 0.0e+00; 0.0e+00 |
| H3 | 47 / 2 / 0: MM1-v1 BETTER | 47 / 2 / 0: MM1-v1 BETTER | yes | 49 | 0.0e+00; 2.8e-07 |
| H4 | 47 / 2 / 0: MM1-v1 BETTER | 47 / 2 / 0: MM1-v1 BETTER | yes | 49 | 0.0e+00; 2.8e-07 |

| MM1-v1's registered rule | registered pass / scored: verdict | this code inside / of | equal |
|---|---|---|---|
| T1 | 45 / 47: PASS | 45 / 47 | yes |
| T2 | 44 / 47: PASS | 44 / 47 | yes |
| T3 | 45 / 47: PASS | 45 / 47 | yes |
| E1 | 50 / 53: PASS | 50 / 53 | yes |
| E2 | 48 / 53: PASS | 48 / 53 | yes |
| E3 | 51 / 53: PASS | 51 / 53 | yes |
| E4 | 50 / 53: PASS | 50 / 53 | yes |

- **Self-tests** (`selftest_score_v2_e207.py`; output `selftest-score-v2-e207.txt`, 35 of 35 PASS). On E206 arm A's committed data, the measured side equals E206's committed scores (119 points, 833 fields, worst relative difference 1.9e-16). Stand-in E207 days are built from the frozen files, with every outcome stated by arithmetic written apart from the scorer: MM1-v1 exact, a stand-in v2 at 1.05 x time and 1.10 x W, set-aside and unkept runs, the watts reading, F2's given(), 'ran before' labels applied as A1 applies them, an unknown label refused, the family check and the common sets.
- **The cross-check test** (`selftest_xcheck_v2_e207.py`; output `selftest-xcheck-v2-e207.txt`, PASS). The stand-in day is off MM1-v1 by stated per-point factors. On it, E207's registered scorer (run unchanged as its own process) and this code agree on the measured side, on H1-H4's counts and every d, and on MM1-v1's rule counts.
- **Re-run.** `score-e207-config.json`, run from the top of a copy of the lab at the data commit plus these files, re-made `score-e207.json` and `score-e207.txt` byte for byte (section 10).

## 9. What this score cannot say

- **MM1-v2's scores are REPORTED.** E207 registered its rules for MM1-v1, F1 and F2 before MM1-v2 existed. No MM1-v2 band or head-to-head rule was registered, so nothing here is a verdict on MM1-v2.
- **One card, one clock, one session.** That is aifoundry3 card 0 at 600 MHz, with two runs a point. The head-to-head counts cases as independent; E207.md A1 item 5's family check sits beside it.
- **Neither version saw an E207 datum; both are fits to earlier days.** MM1-v1's constants were fitted on the lab's measured matmul points, E206 arm A's among them; MM1-v2 refitted them with E208's sessions on three cards (it never read E206 arm B). Their forecasts differ by 3.2% rms on the wall (desk, before the data), so the head-to-head between them has little room to decide.
- **No transistor switch is measured.** MM1-v2's switch estimates are not scored.
- **F2's given() is the registered scorer's number**, not recomputed here.
- **E207's other registered readings** (the timing simulation's columns among them) are in the registered scorer's output and are not repeated here. The stride, one-K-block and subset readings above are this lane's, post hoc.

## 10. Files, and how to re-run

- `score_v2_e207.py`: the scorer (standard library only). From the lab's top, `/usr/bin/python3 -I -B tools/matmul/mm1/v2/score_v2_e207.py tools/matmul/mm1/v2/score-e207-config.json OUT.json --text OUT.txt` re-makes `score-e207.json` and `score-e207.txt`.
- `score-e207-config.json` (config A): every input by path and sha256, with F2's given() from `f2-given-e207.json`.
- `score-e207-xcheck-config.json` (config B): the same, but reading E207's registered scorer output at `docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.json` (sha256 `be47e045...`), the path where E207's scores lane commits it. It runs only once that file is there with those bytes.
- `score-e207-crosscheck.json`: config B's cross-check, run here on the card lane's copy of that output. `score-e207.json` and `score-e207.txt`: config A's output. `score-e207.md`: this file.
- `f2-given-e207.json`; the two self-tests and their outputs; `SHA256SUMS-score-e207` (every file above but itself).
- Interpreter for every number: `/usr/bin/python3` 3.12.3, run `-I -B`, standard library only.
