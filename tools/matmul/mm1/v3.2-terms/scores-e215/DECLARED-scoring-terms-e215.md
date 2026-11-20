# How score-terms-e215 scores the two frozen candidate terms and verify-lay's controls on E215 (declared before any term is scored)

*Thu 19 Nov 2026, Pacific time; round Q231, lane score-terms-e215. Written before this lane computed any score of the gemmLnc term, the contention
term or the controls on E215's data. Disclosure: before writing it the lane read the round log's E215 result lines (the registered scorer's
verdicts and verify-e215d's rms for MM1-v3.1, MM1-v3, MM1-v2 and 'v3.1 with T7'; none for the terms or controls), and, while reading the
card lane's scorer output for its structure, one measured record (a024: W over idle 26.30 W, wall cycles 993.5 an op). Every comparison here is
REPORTED: never a registered rule of E215; the candidates were frozen before any E215 datum (posts #1.29 09:32:02, #1.29.1 09:32:47,
#1.29.1.1 10:31:36 PST) and are scored after the data.*

## Inputs, read only through committed bytes

- E215's frozen scorer and inputs: `tools/claims-v3/e215/` at 8bde0182 (its `load_frozen(check=True)` checks every pin); arm A's MM1-v3.1 and MM1-v3
  forecasts in `tools/matmul/mm1/v3.1/out/e215/` at 2c971828.
- The measured side: the committed `data-e215.json` of arm A (8355db15) and arm B (4f648f24) through the frozen scorer's own reader
  (`reduce_arm`, with the committed `labels-e215.json`: no label), a point the mean of its kept runs, a case the mean of its points.
- The gemmLnc term F3: `tools/matmul/mm1/v3.2-terms/gemmlnc/forecasts-gemmlnc-e215.json` and `.csv` at aaeaa495 (sha256 checked against #1.29);
  its other frozen forms F1, F2, F4 from the same rows, REPORTED.
- The contention term F1: `tools/matmul/mm1/v3.2-terms/layout/forecast-e215-v31-layout.csv` at 595fcb59 (sha256 checked against #1.29.1).
- verify-lay's controls: `.../layout/controls-e215/v02_e215_controls.csv` at 595fcb59 (sha256 checked against #1.29.1.1): N3, N1+N2, G1, G1+N1,
  fresh24 (F1's column there checked equal to the frozen F1).
- Beside, context only: 'v3.1 with T7' (`forecast-e215-t7.csv`, registered in E215, REPORTED there).

## The models

- **MM1-v3.1, MM1-v3**: E215's frozen columns exactly as its scorer reads them.
- **'v3.1 + gemmLnc term' (F3)**: at E215's five gemmLnc points (a024, a026, a031, a032, b013) the frozen rows (A = lnc_A_W, B = lnc_B_W_us,
  W and J over idle at MM1-v3.1's own op time and seconds); time = MM1-v3.1's. At every other point it is MM1-v3.1 exactly (the term is 0 on
  every cooperative loop by its frozen definition: dup = 0).
- **'v3.1 + contention' (F1)**: wall cycles and seconds = the frozen `v31c_cycles_per_op_wall` and `v31c_seconds_per_gemm`; the factor
  g = v31c / v31 (exactly 1 at the full mask); the counter's mean = MM1-v3.1's x g (E216's declared composition; REPORTED); energy = MM1-v3.1's
  affine form A + B / t_op at its own op time (cycles / 600 MHz) and seconds, so given the measured op time it is MM1-v3.1's exactly.
- **The controls** (N3, N1+N2, G1, G1+N1, fresh24): wall cycles from the posted CSV; seconds = cycles / 600 MHz x the registered ops a minion a
  GEMM (as F1's freeze made its seconds; checked against MM1-v3.1's own frozen seconds by the same construction).
- **'v3.1 + both terms'**: E216's declared composition (written before any E215 datum): time = MM1-v3.1's x g; W at an op time t = A + (B + dB) / t
  with dB the gemmLnc term's (0 off gemmLnc); at its own seconds t = its own op time. On E215 no point carries both terms (every gemmLnc point is
  on the full chip, every subset point is cooperative), so it equals F3 on the gemmLnc points, F1 on the subset points and MM1-v3.1 elsewhere
  (checked).

## The quantities (E215's scorer's forms) and the error convention

- **Signed error = 100 (measured / forecast - 1)** (E215's scorer's convention: positive = the model under-forecasts). rms = the root mean square of
  that over the set. At a **watts point** (MM1-v3.1's frozen W under 3 W, or the measured W under 3 W: E215's rule) the energy errors are in watts
  (measured - forecast) and stay out of the % rms.
- Time per case (a point is its own case on every subset point): wall cycles an op, the counter's mean, seconds a GEMM.
- Energy per point: **W over idle given t** = A + B / (measured wall cycles / 600 MHz); **J over idle given t** = that x the measured seconds (E1);
  **J over idle with t forecast** = the model's frozen J (E2); **J at rest given t** = measured rest x measured seconds + E1's J (E3); **J at rest
  with t forecast** = measured rest x the model's seconds + its frozen J (E4).

## The head-to-heads (E215's rule, REPORTED)

- d = |ln(measured / other)| - |ln(measured / candidate)| (in watts of W at a watts point); the candidate is closer where d > the arm's tie, the
  other where d < -tie; ties: E215's registered ties per arm (cycles 0.005, seconds 0.005, joules 0.01 in ln; watts 0.05 W arm A, 0.1 W arm B).
- The exact two-sided sign test on the untied: decided at p < 0.05; **TOO FEW under 10 untied** (E215's); its p printed beside as REPORTED.
- Groups: part 1 the five gemmLnc points (pooled over both arms; per arm beside); part 2 the 28 subset-mask points (arm A 20, arm B 8, pooled);
  part 3 every point by E215's groups (registered P, C, R; post hoc L, S), per arm and pooled.

## The layout pairs (part 2)

- E215's equal-count layout sets: arm A gemmL1x9x6 at eight 28-shire masks (a001-a008) and two 24-shire masks (a009, a010); arm B gemmL1x15x4 at
  four 28-shire masks (b001-b004): 28 + 1 + 6 = 35 pairs.
- Noise: the pooled within-point sd s of ln of the per-run wall cycles over the arm's points with two or more kept runs; a pair differs **beyond
  noise** if |ln(cw_i / cw_j)| > 1.96 s sqrt(1/n_i + 1/n_j) (n the points' kept runs); the registered time tie 0.005 printed beside.
- A model **orders** a pair beyond noise if its predicted ln(i/j) has the measured sign and |predicted| > 1e-9; with |predicted| <= 1e-9 it
  **cannot order** it (it gives the layouts one value).
