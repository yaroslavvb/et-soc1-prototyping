# E215 scores the two frozen candidate terms: the gemmLnc term held blind, the contention term did not

*Thu 19 Nov 2026, Pacific time. Round Q231, lane score-terms-e215. Desk only: no card, no simulator. Interpreter `/usr/bin/python3` 3.12.3,
standard library only, single-threaded.*

This is the first blind test of MM1-v3.1's two candidate terms. Both were frozen before any E215 datum and are scored here after it:

- **The gemmLnc term F3**, 'MM1-v3.1 + gemmLnc term'. It was frozen at 09:30:36 PST and posted as #1.29 at 09:32:02
  (`../gemmlnc/`, landed aaeaa495).
- **The contention term F1**, 'MM1-v3.1 + contention'. It was frozen at 09:31:34 PST and posted as #1.29.1 at 09:32:47 (`../layout/`, landed 595fcb59).
- **verify-lay's five layout controls**: N3, N1+N2, G1, G1+N1 and fresh24. They were written at 10:22:51 PST and posted as #1.29.1.1 at 10:31:36
  (`../layout/controls-e215/`).

Both arms were held from 09:59:39 PST and booked only from 11:56:00. Their first card commands came at 12:05 PST (arm A, aifoundry3 card 0,
the config read at 12:05:24) and 13:41 PST (arm B, aifoundry1 card 1, the firmware read at 13:41:24). The sessions ran 12:05:55-12:58:41 and
13:42:22-14:10:55 PST. So every E215 datum came after all three posts.

**How to read every number here:** each one is **REPORTED**. None is a registered rule of E215, and E215's registration scores none of these
candidates. A forecast is labelled **blind** when it was frozen before the data, and every comparison here was scored after the data. The
labels **post hoc** and **context** say where a reading goes beyond the declaration made before scoring (`DECLARED-scoring-terms-e215.md`).

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus
on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles.
From based on what I know about the size of a matrix and which operations are contained."

## The answer

1. **The gemmLnc term held blind, in direction and roughly in size.** E215 has five gemmLnc points: a024, a026, a031 and a032 on arm A, and b013 on arm B.
   - **Direction.** The measured excess over MM1-v3.1 is positive at all 5.
   - **Error.** The W over idle given the measured op time has an rms of **8.20%** with 'v3.1 + gemmLnc term'. MM1-v3.1 reads **34.74%** and MM1-v3 34.68%.
   - **Against its own held-out claims.** The term claimed a leave one point out rms of 9.81%, and a leave one run out rms of 9.63%.
   - **The sign test** is **TOO FEW**: 5 untied points, under E215's 10. All 5 favour the term, with exact p 0.0625, REPORTED.
   - **The size.** On aifoundry3 the measured excess is **0.65-0.71 of the term**: the term is 1.4-1.55x too large there. On card 1 (b013) it is
     **1.02**.
2. **The NB form held.** F3 is the frozen form with the term's falling 1/NB part.
   - **The flat ratio.** It is the only one of the four frozen forms whose measured / predicted excess is flat across NB on aifoundry3: 0.709 and
     0.645 at NB 15 and 12 (a024, a026), and 0.690 and 0.663 at NB 1 (a031, a032). F1 reads 0.54-0.57 against 1.48-1.54. F2 and F4 read
     0.33-0.35 against 0.91-0.95.
   - **At NB 12-15**, never fitted, F3 is the closest form: -4.9% and -6.2%, against F1's -8.6% and -9.4% and F2's and F4's -19% to -20%.
   - **What stays open** is the level on aifoundry3. It is 0.68x, against card 1's 1.02x: a card factor of about 1.5 at E215's shapes, beside
     the 1.20-1.31 found in sample.
3. **verify-lnc's nearest-analog reading held on arm A and not on b013.**
   - **a031 and a032.** F3 reads 2.67 W and 2.89 W high at its own op time, and the analog had said about 3 W. The analog itself lies within
     0.43 W and 0.20 W of the measurement.
   - **b013.** F3 is within 0.24 W, where the analog had said F3 would read 0.7-1.5 W low. The analog read 0.9-1.7 W high.
   - **a024 and a026.** The analog read 3.9 W and 3.4 W low.
4. **The contention term did not help blind.** On E215's 28 subset-mask points:
   - **Wall cycles rms.** F1 reads **9.63%**, against MM1-v3.1's **9.53%** and MM1-v3's 8.65%.
   - **The sign test against MM1-v3.1** is TOO FEW, at 1/3/24. F1 moves the forecast by less than E215's 0.005 tie at 24 of 28 points.
   - **Where it moves more** (the 14 rows of 2-15 shires, post hoc, no tie), it moved the wrong way at 12 of 14.
   - **The shire-count-only control N1+N2** is the one candidate decided closer than MM1-v3.1: 18/4/6, p 0.0043, rms 9.05%. G1+N1 reads 9.15%,
     NOT DECIDED.
   - **MM1-v3** is closer than F1 at 19 of 22 untied points (p 0.00086).
5. **E215's equal-count layout pairs.**
   - **Beyond noise.** 18 of the 35 pairs differ by more than the day's replicate noise: 16 on arm A, 2 on arm B. Only 3 differ by more than E215's 0.005 tie.
   - **Which models give each set one value.** F1, N3, N1+N2 and fresh24 do, and so do MM1-v3.1, MM1-v3 and 'v3.1 with T7'. None of them can
     order any pair.
   - **G1 and G1+N1** order 4 of the 18 and misorder 13 (1 they cannot tell apart).
   - **The fastest mask** in both 28-shire sets is 0xfff0ffff, on both cards (post hoc).
6. **'v3.1 + both terms'** (REPORTED; E216's declared composition).
   - **On the registered points**, the energy moves; the time is MM1-v3.1's. J over idle given t reads **4.28%**, against MM1-v3.1's 11.50% and
     MM1-v3's 11.57%, and it is closer than MM1-v3 at 11/2/37 (p 0.022). Wall cycles read 7.01%, against MM1-v3's 6.78% (NOT DECIDED).
   - **On the post hoc points** it gains nothing. Wall cycles read 9.63%, and MM1-v3 is closer at 3/19/6 (p 0.00086).
   - **Over all 90 points**, J over idle given t reads 5.48%, against MM1-v3.1's 9.85%. J at rest given t reads 1.87%, against 3.62%.

## Inputs and their checks

- **The freeze lines.** Every frozen candidate file's sha256, from its committed blob, equals its posted hash: 6 of 6.
  - `forecasts-gemmlnc-e215.csv` 00fcaf5d..., `.json` feba7e5e... and `term-gemmlnc.json` 2ee478f8... (#1.29).
  - `forecast-e215-v31-layout.csv` 50949ba3... and `.json` f09f9e1a... (#1.29.1).
  - `v02_e215_controls.csv` c5bc2394... (#1.29.1.1).
- **Two posted hashes that differ, for reasons already recorded:**
  - **The layout land's SHA256SUMS.** #1.29.1 named the 19-file land, `d5ec254d...`. The committed land holds 25 files, `dc2ae924...`, after
    REPORTED additions made after the freeze. Its dated note records this, and the 19-file bytes were not kept, so `d5ec254d` **cannot be
    re-verified**. All 9 files the freeze record names are byte-equal in the committed tree.
  - **The controls' maker** `v02_fits.py`. It is committed with three path lines rewritten, so its sha256 is `506bc7e8...`. verify-lay's own copy
    equals the posted `4fb92de3...` byte for byte, and the CSV it made is byte-equal to the post.
- **E215's frozen scorer** is imported from its committed folder (kit 8bde0182; the 36 registration files equal 4cb2c2ad's). Its
  `load_frozen(check=True)` verified every pin.
- **The measured side** is the committed `data-e215.json` of each arm (arm A data 8355db15, arm B data 4f648f24), each equal to its folder's
  SHA256SUMS. It is read through the frozen scorer's own reader, with the committed labels (none).
  - **Against the card lanes' own scorer outputs** (each card day's step 13): 1,880 of 1,880 fields bit-equal. No run was set aside, and R0 and S6
    have no failures.
- **This lane's code against the frozen scorer.**
  - Its MM1-v3.1 cells equal the frozen scorer's: 360 cells, worst difference 0.
  - Its head-to-head arithmetic equals the scorer's `h_pair`: 20 of 20.
  - Its MM1-v3.1 and MM1-v3 rms equal verify-e215d's independent table in every cell, to the printed digit.
- **The candidates.**
  - **The term's base.** The gemmLnc term's MM1-v3.1 equals E215's frozen MM1-v3.1 at its five points within 2.2e-7, the rounding of arm B's
    6-decimal CSV.
  - **The full mask.** At all 66 full-mask rows, F1's factor is exactly 1 and every control equals MM1-v3.1.
  - **The controls' columns.** Their F1 column equals the frozen F1 exactly, and their MM1-v3.1 column equals E215's to 5e-5 cycles (4-decimal
    printing).

## The models as scored (declared before any term was scored)

| model | time | energy |
|---|---|---|
| MM1-v3.1, MM1-v3 | E215's frozen columns, exactly as its scorer reads them | the same |
| **v3.1 + gemmLnc term (F3)** | MM1-v3.1's | at the 5 gemmLnc points the frozen rows (A, and B with the term's energy an op); elsewhere MM1-v3.1 (the term is 0 on every cooperative loop) |
| F1, F2, F4 of the gemmLnc term (REPORTED) | MM1-v3.1's | the same frozen rows' other forms |
| **v3.1 + contention (F1)** | the frozen `v31c` cycles and seconds; the counter's mean x the factor (E216's composition, REPORTED) | MM1-v3.1's affine form at its own op time (so given t it is MM1-v3.1's) |
| the controls | the posted cycles; seconds = cycles / 600 MHz x the registered ops (F1's own construction; MM1-v3.1's frozen seconds follow it to 5e-8) | none |
| **v3.1 + both terms** | MM1-v3.1's x the F1 factor | A + (B + the term's dB) / t | 

The composition is E216's: its registration (round Q227, written 10:25-10:55 PST, before any E215 datum) declares it, and that registration was
not yet on GitHub main when this was written. On E215 no point carries both terms: every gemmLnc point is on
the full chip and every subset point is cooperative. So 'both' equals F3 at the 5 gemmLnc points, F1 at the 28 subset points and MM1-v3.1 at the
other 61, as checked. 'v3.1 with T7', E215's REPORTED column, is shown beside for context only.

**The quantities and convention** are E215's scorer's:

- **The error.** Signed error = 100 (measured / forecast - 1), so it is positive where the model under-forecasts.
- **W over idle given t** = A + B / t_op, with t_op the measured wall cycles an op / 600 MHz.
- **J over idle given t** = that times the measured seconds (E1). **With t forecast** it is the model's frozen J (E2).
- **J at rest** = the measured rest x the seconds + J over idle, given t (E3) or with t forecast (E4).
- **The head-to-head.** d = |ln(measured / other)| - |ln(measured / candidate)|, with E215's registered ties: cycles and seconds 0.005, joules
  0.01, watts 0.05 W on arm A and 0.1 W on arm B. The test is the exact two-sided sign test, TOO FEW under 10 untied.
- **Watts points.** A point whose W over idle is under 3 W (MM1-v3.1's frozen or the measured) is scored in watts, outside the % rms.

## 1. The gemmLnc term on E215's gemmLnc points

W over idle given the measured op time (signed error in brackets):

| point | arm, card | shape | NB | measured W over idle (wall cycles an op) | MM1-v3.1 | MM1-v3 | **F3** | F1 | F2 | F4 |
|---|---|---|---|---|---|---|---|---|---|---|
| a024 | A, aifoundry3 card 0 | gemmLnc1x15x3 | 15 | 26.30 W (993.5) | 22.96 W (+14.5%) | 22.97 W (+14.5%) | **27.66 W (-4.9%)** | 28.78 W (-8.6%) | 32.42 W (-18.9%) | 32.45 W (-19.0%) |
| a026 | A, aifoundry3 card 0 | gemmLnc1x12x4 | 12 | 25.77 W (999.7) | 22.66 W (+13.7%) | 22.65 W (+13.8%) | **27.48 W (-6.2%)** | 28.45 W (-9.4%) | 32.06 W (-19.6%) | 32.09 W (-19.7%) |
| a031 | A, aifoundry3 card 0 | gemmLnc8x1x5 | 1 | 23.23 W (1376.3) | 16.74 W (+38.8%) | 16.79 W (+38.4%) | **26.14 W (-11.1%)** | 20.94 W (+10.9%) | 23.57 W (-1.4%) | 23.59 W (-1.5%) |
| a032 | A, aifoundry3 card 0 | gemmLnc5x1x10 | 1 | 22.86 W (1375.5) | 16.62 W (+37.6%) | 16.66 W (+37.3%) | **26.03 W (-12.2%)** | 20.82 W (+9.8%) | 23.45 W (-2.5%) | 23.47 W (-2.6%) |
| b013 | B, aifoundry1 card 1 | gemmLnc2x1x37 | 1 | 24.80 W (1551.3) | 16.30 W (+52.1%) | 16.26 W (+52.5%) | **24.60 W (+0.8%)** | 20.01 W (+23.9%) | 22.33 W (+11.1%) | 22.35 W (+11.0%) |

Joules, signed %. Each cell reads J over idle given t / with t forecast, then J at rest given t / with t forecast:

| point | MM1-v3.1 | MM1-v3 | **F3** |
|---|---|---|---|
| a024 | +14.5 / +13.8; +7.2 / -2.1 | +14.5 / +13.8; +7.2 / -0.9 | **-4.9 / -5.4; -2.7 / -10.4** |
| a026 | +13.7 / +13.0; +6.7 / -2.1 | +13.8 / +13.1; +6.8 / -0.9 | **-6.2 / -6.7; -3.4 / -10.7** |
| a031 | +38.8 / +38.8; +16.1 / +15.6 | +38.4 / +38.4; +16.0 / +15.2 | **-11.1 / -11.1; -5.9 / -6.2** |
| a032 | +37.6 / +37.6; +15.6 / +14.9 | +37.3 / +37.2; +15.5 / +14.6 | **-12.2 / -12.2; -6.4 / -6.8** |
| b013 | +52.1 / +51.8; +19.0 / +20.0 | +52.5 / +52.2; +19.1 / +20.9 | **+0.8 / +0.5; +0.4 / +1.0** |

rms over the five, with the bias in brackets:

| model | W over idle given t | J over idle given t | J over idle, t forecast | J at rest given t | J at rest, t forecast |
|---|---|---|---|---|---|
| MM1-v3.1 | 34.74% (+31.35) | 34.74% (+31.35) | 34.52% (+31.00) | 13.86% (+12.92) | 13.21% (+9.23) |
| MM1-v3 | 34.68% (+31.28) | 34.68% (+31.27) | 34.51% (+30.97) | 13.83% (+12.89) | 13.28% (+9.78) |
| **v3.1 + gemmLnc term (F3)** | **8.20% (-6.74)** | **8.20% (-6.74)** | **8.31% (-6.98)** | **4.33% (-3.59)** | **7.87% (-6.63)** |
| form F1 (REPORTED) | 13.79% (+5.32) | 13.79% (+5.32) | 13.80% (+5.09) | 6.24% (+1.95) | 9.49% (-0.99) |
| form F2 (REPORTED) | 13.21% (-6.28) | 13.21% (-6.28) | 13.35% (-6.47) | 7.40% (-3.88) | 11.38% (-6.46) |
| form F4 (REPORTED) | 13.24% (-6.37) | 13.24% (-6.37) | 13.39% (-6.55) | 7.43% (-3.92) | 11.40% (-6.50) |

By arm, W over idle given t: on arm A (4 points) F3 reads 9.16% (bias -8.63%), against MM1-v3.1's 28.79%; on arm B (b013) F3 reads +0.79%,
against MM1-v3.1's +52.14%.

**The sign test** (F3 / the other / ties; exact two-sided p REPORTED):

| quantity | against MM1-v3.1 | against MM1-v3 |
|---|---|---|
| J over idle given t (H4) | TOO FEW, 5/0/0 (p 0.0625) | TOO FEW, 5/0/0 (p 0.0625) |
| J over idle with t forecast (H5) | TOO FEW, 5/0/0 (p 0.0625) | TOO FEW, 5/0/0 (p 0.0625) |
| J at rest given t | TOO FEW, 5/0/0 (p 0.0625) | TOO FEW, 5/0/0 (p 0.0625) |
| J at rest with t forecast | TOO FEW, 3/2/0 (p 1) | TOO FEW, 3/2/0 (p 1) |

**Too few is too few.** Five points cannot decide a sign test at 0.05 even if all five agree. Against its sibling forms F1, F2 and F4, F3 is
closer at 3 of 5 points: TOO FEW.

**The two points that go the other way with t forecast** are a024 and a026, J at rest with the seconds forecast. MM1-v3.1's time for gemmLnc at
NB 12-15 is 15.5% and 14.8% too long: wall cycles -15.5% and -14.8%, E215's own T1 misses. So the measured rest x the forecast seconds over-counts.
That had partly cancelled MM1-v3.1's under-priced W, and the term's added W tips it over. The term's README had named this: "MM1-v3.1's op time
overprices gemmLnc's cycles at NB 5-6 ... so a024 and a026 may run faster than forecast. That affects J with the time forecast, not W given t."
The fully forecast J at rest in the term's file, at the rest law's 24.74 W and 31.76 W, reads -12.7%, -13.0%, -8.5%, -9.1% and -5.0%. Most of
that is the rest law: the measured rests were 23.49-23.53 W and 28.40 W.

### Did the term's direction and size hold?

Given the measured op time (the term adds dW = dB / t_op):

| point | NB | measured excess over MM1-v3.1 | F3's term | measured / F3 | measured / F1 | / F2 | / F4 | F3 frozen - measured (own op time) | analog - measured |
|---|---|---|---|---|---|---|---|---|---|
| a024 | 15 | +3.34 W | +4.70 W | 0.709 | 0.573 | 0.353 | 0.352 | -2.77 W | -3.88 W |
| a026 | 12 | +3.11 W | +4.82 W | 0.645 | 0.538 | 0.331 | 0.330 | -2.20 W | -3.44 W |
| a031 | 1 | +6.49 W | +9.41 W | 0.690 | 1.545 | 0.950 | 0.947 | +2.67 W | -0.43 W |
| a032 | 1 | +6.24 W | +9.41 W | 0.663 | 1.484 | 0.913 | 0.910 | +2.89 W | -0.20 W |
| b013 | 1 | +8.50 W | +8.30 W | 1.023 | 2.290 | 1.409 | 1.405 | +0.24 W | +0.91 to +1.71 W |

The ratios are per op, the measured excess energy an op step against each form's; given t they equal the watt ratio. The analog is verify-lnc's
nearest-analog reading, from the term's dated note: a024 22.42 W, a026 22.33, a031 22.80, a032 22.66 and b013 25.7-26.5 W.

- **Direction: held at 5 of 5.** gemmLnc costs more than MM1-v3.1 prices it at every point. MM1-v3.1 prices it at about its cooperative
  twins, and the measured W over idle sits 13.7-52.1% above MM1-v3.1's given t.
- **Size: held on card 1, too large on aifoundry3.**
  - On card 1 the measured excess is 1.02 of the term.
  - On aifoundry3 it is 0.65-0.71 at all four points. The term over-prices aifoundry3's points by 5-12% in W, and its blind rms of 8.20% stays
    within its held-out claims.
  - In sample, card 1's excess was 1.20-1.31x aifoundry3's at the same shape, and the term pools the two cards with no card factor. Here the
    two cards sit about 1.5x apart. That compares different shapes: b013 against a031 and a032, all at NB 1 and served beyond the L2 in
    MM1-v3.1's map. b013's B tiles come mostly from DRAM (0.84), where a031's and a032's come from the L3.
- **The NB form: held.**
  - **The flat ratio.** On aifoundry3 the measured / predicted excess is flat across NB only for F3: 0.709 and 0.645 at NB 15 and 12; 0.690 and
    0.663 at NB 1.
  - **The sibling forms.** F1 (duplicates only) swings 0.54-0.57 against 1.48-1.54. F2 and F4 (every duplicate of a beyond-L2 line re-fetched,
    no 1/NB) swing 0.33-0.35 against 0.91-0.95.
  - **At NB 12-15**, where the 1/NB part extrapolated from NB 6 or less and no fit point lay, F3 is the closest frozen form. F2 and F4 are
    about 3x too high in the excess there.
  - **What the data do not separate.** The measured excess at NB 12-15 (5.53 and 5.18 W us an op step) lies below even F3's duplicate-read
    part alone (6.81 W us), 0.81 and 0.76 of it (`term` > `measured_over_F3_duplicate_read_part` in the JSON). So the overshoot on aifoundry3
    is a level common to both of F3's parts, and E215 cannot split c1 from c2.
- **verify-lnc's nearest-analog reading.**
  - **a031 and a032, "F3 high by about 3 W": held.** F3 reads 2.67 W and 2.89 W high at its own op time, and 2.91 W and 3.17 W given t. The analog
    itself lies within 0.43 W and 0.20 W.
  - **b013, "F3 low by 0.7-1.5 W": did not hold.** F3 is 0.24 W high at its own op time and 0.19 W low given t. The analog read 0.9-1.7 W high.
  - **a024 and a026**, which the reading did not name: the analog read 3.9 W and 3.4 W low there, and F3 read 2.8 W and 2.2 W low at its own op
    time. At its own op time F3's W is low there because gemmLnc ran 15% faster than MM1-v3.1's time; given t it is 1.4 W and 1.7 W high.

**The cooperative twins.** These are E215's cooperative points at a024's and a026's shapes: a021 (rgm211 gemmLn1x15x3) and a022
(gemmLn1x12x4). Their loads are cooperative, and they are rgm211's swapped C-block walk.

- The term is 0 on them by construction, so 'v3.1 + gemmLnc term' is MM1-v3.1 there.
- MM1-v3.1 reads them at -2.1% and -2.3% (W over idle given t), so its base is about 2% high at these shapes.
- **The measured W ratio gemmLnc / twin** is 1.262 and 1.248. MM1-v3.1 says 1.079 and 1.072, given t; F3 says 1.300 and 1.300.
- **The measured wall-cycle ratio** is 0.926 and 0.933, where MM1-v3.1 and MM1-v3 say 1.024: gemmLnc ran 7% faster than the twin, where the
  models have it 2.4% slower.
- a031, a032 and b013 have no cooperative point at their shapes in E215.

## 2. The contention term and the controls on E215's subset-mask points

- **The points.** 28 subset-mask points: arm A a001-a020, one run each; arm B b001-b008, two runs each.
- **The full-chip points are kept apart.** At all 62 of them F1 and every control equal MM1-v3.1 exactly, so nothing there tests a term.

Wall cycles an op, signed %:

| point | shape | mask | shires | runs | measured | MM1-v3.1 | MM1-v3 | **F1** | N3 | N1+N2 | G1 | G1+N1 | fresh24 | T7 (context) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a001 | gemmL1x9x6 | 0xf0ffffff | 28 | 1 | 1083.7 | -9.41 | -7.43 | -9.36 | -9.42 | -8.51 | -9.41 | -9.17 | -9.56 | -8.08 |
| a002 | gemmL1x9x6 | 0xff0fffff | 28 | 1 | 1083.6 | -9.41 | -7.43 | -9.37 | -9.42 | -8.51 | -9.48 | -9.30 | -9.56 | -8.09 |
| a003 | gemmL1x9x6 | 0xfff0ffff | 28 | 1 | 1079.3 | -9.77 | -7.80 | -9.73 | -9.79 | -8.88 | -9.86 | -9.70 | -9.92 | -8.45 |
| a004 | gemmL1x9x6 | 0xffff0fff | 28 | 1 | 1084.6 | -9.33 | -7.35 | -9.29 | -9.34 | -8.43 | -9.50 | -9.42 | -9.48 | -8.00 |
| a005 | gemmL1x9x6 | 0xfffff0ff | 28 | 1 | 1086.2 | -9.19 | -7.21 | -9.15 | -9.21 | -8.29 | -9.10 | -8.76 | -9.34 | -7.87 |
| a006 | gemmL1x9x6 | 0xffffff0f | 28 | 1 | 1085.3 | -9.27 | -7.29 | -9.22 | -9.28 | -8.37 | -9.22 | -8.92 | -9.42 | -7.94 |
| a007 | gemmL1x9x6 | 0xfffffff | 28 | 1 | 1082.5 | -9.51 | -7.53 | -9.46 | -9.52 | -8.61 | -9.41 | -9.08 | -9.65 | -8.18 |
| a008 | gemmL1x9x6 | 0xfffffff0 | 28 | 1 | 1086.0 | -9.21 | -7.23 | -9.17 | -9.22 | -8.31 | -9.12 | -8.77 | -9.36 | -7.88 |
| a009 | gemmL1x9x6 | 0xbbbbbbbb | 24 | 1 | 1070.7 | -9.80 | -7.85 | -9.80 | -9.83 | -8.33 | -10.08 | -9.86 | -10.02 | -10.16 |
| a010 | gemmL1x9x6 | 0xdddddddd | 24 | 1 | 1074.0 | -9.52 | -7.56 | -9.52 | -9.55 | -8.05 | -9.79 | -9.56 | -9.74 | -9.88 |
| a011 | gemmL1x6x5 | 0x33000333 | 10 | 1 | 930.6 | -11.96 | -12.16 | -12.26 | -12.15 | -11.19 | -12.35 | -11.43 | -11.76 | -6.18 |
| a012 | gemmL1x2x13 | 0x77007707 | 15 | 1 | 1378.9 | -1.02 | -0.80 | -1.07 | -1.14 | +0.63 | -0.85 | +0.48 | -0.93 | +17.15 |
| a013 | gemmL2x3x5 | 0x99990000 | 8 | 1 | 935.5 | -11.81 | -11.87 | -12.24 | -12.08 | -11.46 | -12.65 | -12.06 | -12.36 | -4.72 |
| a014 | gemmL8x1x4 | 0x30000000 | 2 | 1 | 1351.7 | +3.62 | +3.66 | +2.91 | +2.08 | +2.01 | +3.16 | +4.82 | +2.85 | +39.89 |
| a015 | gemmL1x9x6 | 0x2002202 | 4 | 1 | 1025.7 | -10.11 | -8.26 | -10.42 | -10.74 | -10.85 | -9.29 | -6.66 | -10.67 | +1.89 |
| a016 | gemmL2x6x10 | 0x4404444 | 6 | 1 | 1370.0 | +5.52 | +6.59 | +5.40 | +5.06 | +5.34 | +6.39 | +9.23 | +5.39 | +8.60 |
| a017 | gemmL1x8x6 | 0xd000dd0 | 9 | 1 | 1333.8 | +7.14 | +8.74 | +7.76 | +6.87 | +7.83 | +6.70 | +7.93 | +7.54 | +2.71 |
| a018 | gemmL2x4x16 | 0x990009 | 6 | 1 | 1391.0 | -4.42 | -4.18 | -4.53 | -4.83 | -4.58 | -5.31 | -4.52 | -3.95 | -6.57 |
| a019 | gemmL1x7x6 | 0x10100000 | 2 | 1 | 1054.2 | -3.40 | -2.08 | -3.73 | -4.84 | -4.90 | -4.32 | -3.29 | -4.00 | +3.90 |
| a020 | gemmL2x4x4 | 0xee0e00 | 9 | 1 | 929.8 | -16.63 | -16.98 | -17.02 | -16.84 | -16.09 | -16.32 | -14.68 | -17.10 | -17.32 |
| b001 | gemmL1x15x4 | 0xf0ffffff | 28 | 2 | 1083.6 | -10.88 | -9.45 | -10.83 | -10.89 | -9.99 | -10.88 | -10.64 | -10.83 | -9.74 |
| b002 | gemmL1x15x4 | 0xff0fffff | 28 | 2 | 1083.0 | -10.93 | -9.51 | -10.88 | -10.94 | -10.04 | -11.00 | -10.82 | -10.88 | -9.79 |
| b003 | gemmL1x15x4 | 0xfff0ffff | 28 | 2 | 1079.1 | -11.24 | -9.83 | -11.20 | -11.26 | -10.36 | -11.33 | -11.18 | -11.20 | -10.11 |
| b004 | gemmL1x15x4 | 0xffff0fff | 28 | 2 | 1084.2 | -10.83 | -9.40 | -10.78 | -10.84 | -9.94 | -10.99 | -10.92 | -10.78 | -9.69 |
| b005 | gemmL2x1x16 | 0xcc000 | 4 | 2 | 1325.2 | +0.25 | +0.27 | -1.12 | -0.45 | -0.57 | +1.06 | +3.87 | +0.25 | +37.58 |
| b006 | gemmL3x5x7 | 0x60000006 | 4 | 2 | 998.9 | -13.43 | -12.41 | -13.85 | -14.04 | -14.14 | -12.83 | -10.51 | -13.29 | -2.06 |
| b007 | gemmL8x4x4 | 0x50005500 | 6 | 2 | 958.1 | -14.14 | -14.61 | -14.25 | -14.51 | -14.29 | -13.92 | -12.14 | -14.30 | -23.50 |
| b008 | gemmL1x1x16 | 0xee000e | 9 | 2 | 1319.2 | -1.40 | -1.41 | -2.74 | -1.65 | -0.76 | -0.89 | +1.21 | -1.89 | +36.87 |

The seconds a GEMM per point are in `part2-subset-points.csv`. They read as the wall cycles do: every model's seconds rms lies within 0.07
points of its wall-cycle rms.

rms with the bias, and the sign test against MM1-v3.1 on the wall cycles (candidate / MM1-v3.1 / ties; tie 0.005 in ln):

| model | wall cycles, 28 | seconds, 28 | arm A wall (20) | arm B wall (8) | sign test, pooled | arm A | arm B |
|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 9.53% (-7.50) | 9.47% (-7.42) | 9.16% | 10.39% | - | - | - |
| MM1-v3 | 8.65% (-6.37) | 8.59% (-6.29) | 8.24% | 9.58% | - | - | - |
| **F1** | **9.63% (-7.68)** | **9.57% (-7.59)** | 9.27% | 10.49% | TOO FEW 1/3/24 (p 0.625) | TOO FEW 1/1/18 | TOO FEW 0/2/6 |
| N3 | 9.65% (-7.78) | 9.58% (-7.70) | 9.25% | 10.57% | TOO FEW 1/3/24 (p 0.625) | TOO FEW 1/2/17 | TOO FEW 0/1/7 |
| N1+N2 | 9.05% (-7.06) | 8.99% (-6.97) | 8.61% | 10.07% | **CLOSER 18/4/6 (p 0.0043)** | CLOSER 13/3/4 (p 0.021) | TOO FEW 5/1/2 |
| G1 | 9.56% (-7.52) | 9.50% (-7.44) | 9.25% | 10.30% | TOO FEW 3/5/20 (p 0.727) | TOO FEW 1/4/15 | TOO FEW 2/1/5 |
| G1+N1 | 9.15% (-6.57) | 9.09% (-6.48) | 8.94% | 9.68% | NOT DECIDED 6/4/18 (p 0.754) | TOO FEW 4/3/13 | TOO FEW 2/1/5 |
| fresh24 | 9.65% (-7.64) | 9.59% (-7.56) | 9.35% | 10.38% | TOO FEW 1/4/23 (p 0.375) | TOO FEW 1/4/15 | TOO FEW 0/0/8 |
| T7 (context) | 15.61% (-1.27) | 15.62% (-1.19) | 12.47% | 21.55% | NOT DECIDED 17/8/3 (p 0.108) | NOT DECIDED 12/5/3 | TOO FEW 5/3/0 |

The seconds give the same verdicts. F1 against MM1-v3 on the wall cycles: **MM1-v3 CLOSER**, 3/19/6 (p 0.00086).

**Every model runs E215's subset points too slow.** The bias is -6.4% to -7.8%, and -9% to -11% at the 28-shire masks. F1 moves the 28-shire
rows by -0.05% and the 24-shire rows by 0, all within the tie, so that offset is untouched.

**By shire count** (post hoc, beyond the declaration; tie 0.005, and "no tie" counting every row a candidate moves):

| rows | model | wall cycles rms (bias) | sign test with tie | closer without tie |
|---|---|---|---|---|
| 24-28 shires (14) | MM1-v3.1 | 9.90% (-9.88) | - | - |
| | F1 | 9.87% (-9.84) | TOO FEW 0/0/14 | 12 of 12 moved |
| | N1+N2 | 8.93% (-8.90) | CLOSER 14/0/0 | 14 of 14 |
| | MM1-v3 | 8.12% (-8.06) | CLOSER 14/0/0 | 14 of 14 |
| | T7 (context) | 8.90% (-8.85) | CLOSER 12/0/2 | 12 of 14 |
| 2-15 shires (14) | MM1-v3.1 | 9.14% (-5.13) | - | - |
| | F1 | 9.39% (-5.51) | TOO FEW 1/3/10 | **2 of 14** (p 0.013) |
| | N1+N2 | 9.17% (-5.22) | TOO FEW 4/4/6 | 7 of 14 |
| | G1+N1 | 8.51% (-3.41) | NOT DECIDED 6/4/4 | 8 of 14 |
| | T7 (context) | 20.21% (+6.30) | NOT DECIDED 5/8/1 | 5 of 14 |

The 14 rows of 2-15 shires are where the layout term's dated note says F1 moves, by -0.6% to +1.4%. There it moved away from the measurement at
12 of 14.

### E215's equal-count layout pairs

There are three sets, 35 pairs in all:

- arm A, gemmL1x9x6 at eight 28-shire masks (a001-a008, one row group off each): 28 pairs;
- arm A, gemmL1x9x6 at two 24-shire spread masks (a009, a010): 1 pair;
- arm B, gemmL1x15x4 at four 28-shire masks (b001-b004): 6 pairs.

**The noise** is the pooled within-point sd of ln(per-run wall cycles) over the arm's points with two or more kept runs. It is **0.00056** on
arm A (42 points, 54 degrees of freedom) and **0.0021** on arm B (32 points, 36). A pair differs beyond noise if |ln ratio| > 1.96 sd
sqrt(1/n_i + 1/n_j).

| set | measured wall cycles an op | spread (ln, max - min) | pairs beyond noise | beyond the 0.005 tie |
|---|---|---|---|---|
| A, 28 shires | 1083.65, 1083.64, **1079.31** (0xfff0ffff), 1084.60, 1086.22, 1085.31, 1082.50, 1086.02 | 0.0064 | 15 of 28 | 3 (all against 0xfff0ffff) |
| A, 24 shires | 1070.70 (0xbbbbbbbb), 1074.00 (0xdddddddd) | 0.0031 | 1 of 1 | 0 |
| B, 28 shires | 1083.62, 1083.02, **1079.14** (0xfff0ffff), 1084.21 | 0.0047 | 2 of 6 | 0 |

**Which model ordered them**, of the 18 pairs beyond noise:

- **MM1-v3.1, MM1-v3, F1, N3, N1+N2, fresh24 and T7** give every set one value (exactly equal forecasts), so they **cannot order any**.
- **G1 and G1+N1** separate the layouts: they ordered **4** (a003/a004, a004/a007, a006/a007, b003/b004), misordered **13**, and give 1 pair
  (a005/a007) one value. They misorder all 3 pairs beyond the tie.
- **The fastest mask** in both 28-shire sets is 0xfff0ffff (shires 16-19 off), on both cards: a003 at 0.30-0.64% under its set's others,
  and b003 at 0.36-0.47% (post hoc).

These layout effects are a few tenths of a percent. The models' shared offset at these masks is 9-11%.

## 3. 'v3.1 + both terms' over every E215 point (REPORTED)

rms with the bias and n, pooled over both arms (time per case, energy per point; watts points apart):

| group | model | wall cycles | counter mean | seconds | W over idle given t | J over idle given t | J over idle, t forecast | J at rest given t | J at rest, t forecast |
|---|---|---|---|---|---|---|---|---|---|
| registered (P, C, R) | MM1-v3.1 | 7.01% (+0.60, n 50) | 6.44% (+0.21) | 7.00% (+0.66) | 11.50% (+1.26, n 50) | 11.50% (+1.26) | 11.49% (+1.44) | 4.55% (+0.53, n 50) | 6.28% (+1.22) |
| | MM1-v3 | 6.78% (+1.43, n 50) | 6.06% (+1.03) | 6.77% (+1.49) | 11.57% (+0.90, n 50) | 11.57% (+0.90) | 11.55% (+1.15) | 4.57% (+0.39, n 50) | 6.23% (+1.60) |
| | **both** | 7.01% (+0.60, n 50) | 6.44% (+0.21) | 7.00% (+0.66) | **4.28% (-2.55, n 50)** | **4.28% (-2.55)** | **4.44% (-2.35)** | **1.83% (-1.12, n 50)** | **5.31% (-0.37)** |
| post hoc (L, S) | MM1-v3.1 | 9.53% (-7.50, n 28) | 10.92% (-8.97) | 9.47% (-7.42) | 6.83% (-2.57, n 35) | 6.83% (-2.57) | 7.16% (-2.77) | 1.90% (-0.95, n 40) | 7.12% (-4.19) |
| | MM1-v3 | 8.65% (-6.37, n 28) | 10.13% (-7.84) | 8.59% (-6.29) | 6.71% (-2.55, n 23) | 6.71% (-2.55) | 7.23% (-2.90) | 1.66% (-1.09, n 28) | 7.86% (-5.42) |
| | **both** | 9.63% (-7.68, n 28) | 11.08% (-9.14) | 9.57% (-7.59) | 6.83% (-2.57, n 35) | 6.83% (-2.57) | 7.16% (-2.78) | 1.90% (-0.95, n 40) | 7.20% (-4.31) |
| all 90 | MM1-v3.1 | 8.01% (-2.31, n 78) | 8.33% (-3.09) | 7.98% (-2.24) | 9.85% (-0.32, n 85) | 9.85% (-0.32) | 9.94% (-0.29) | 3.62% (-0.13, n 90) | 6.67% (-1.19) |
| | MM1-v3 | 7.50% (-1.37, n 78) | 7.77% (-2.16) | 7.47% (-1.30) | 10.29% (-0.18, n 73) | 10.29% (-0.18) | 10.39% (-0.13) | 3.79% (-0.14, n 78) | 6.86% (-0.92) |
| | **both** | 8.05% (-2.37, n 78) | 8.40% (-3.15) | 8.02% (-2.30) | **5.48% (-2.56, n 85)** | **5.48% (-2.56)** | **5.72% (-2.53)** | **1.87% (-1.05, n 90)** | **6.22% (-2.12)** |

**How to compare the rows.** MM1-v3 prices no family-S kind, so its energy n is smaller, and the energy rows of different models are not on one
point set. The sign tests below use only points both models price. The five watts points (a014, a015, a019, b005, b006) read in watts. There
'both' equals MM1-v3.1 given t: 0.37 W rms on arm A and 0.36 W on arm B. With t forecast it reads 0.25 W and 0.16 W, against MM1-v3.1's 0.26 W
and 0.16 W.

**The sign tests, pooled over both arms** ('both' / the other / ties). Each cell reads wall cycles (H1); J over idle given t (H4); J over idle
with t forecast (H5); J at rest with t forecast:

| group | against MM1-v3.1 | against MM1-v3 |
|---|---|---|
| registered | TOO FEW 0/0/50; TOO FEW 5/0/45; TOO FEW 5/0/45; TOO FEW 3/2/45 | NOT DECIDED 13/19/18 (p 0.377); **CLOSER 11/2/37 (p 0.022)**; **CLOSER 11/1/38 (p 0.0063)**; NOT DECIDED 5/9/36 |
| post hoc | TOO FEW 1/3/24; TOO FEW 0/0/40; TOO FEW 0/0/40; TOO FEW 0/2/38 | **MM1-v3 CLOSER 3/19/6 (p 0.00086)**; TOO FEW 3/3/22; TOO FEW 3/2/23; **MM1-v3 CLOSER 1/15/12 (p 0.00052)** |
| all | TOO FEW 1/3/74; TOO FEW 5/0/85; TOO FEW 5/0/85; TOO FEW 3/4/83 | **MM1-v3 CLOSER 16/38/24 (p 0.0038)**; NOT DECIDED 14/5/59 (p 0.064); **CLOSER 14/3/61 (p 0.013)**; **MM1-v3 CLOSER 6/24/48 (p 0.0014)** |

The counter's mean and the seconds read as the wall cycles do. Per arm and group (wall cycles / J over idle given t / J at rest with t forecast):

| group, arm | MM1-v3.1 | MM1-v3 | both |
|---|---|---|---|
| registered A | 7.20 / 10.70 / 5.82% | 6.87 / 10.71 / 5.67% | 7.20 / 4.63 / 5.36% |
| registered B | 6.67 / 12.80 / 7.03% | 6.61 / 12.97 / 7.11% | 6.67 / 3.58 / 5.23% |
| post hoc A | 9.17 / 6.96 / 6.89% | 8.24 / 6.58 / 7.47% | 9.27 / 6.96 / 6.97% |
| post hoc B | 10.39 / 6.51 / 7.63% | 9.58 / 7.06 / 8.76% | 10.50 / 6.51 / 7.72% |

**Reading.** The candidate MM1-v3.2 built from these two terms gains in energy only, and only through the gemmLnc term: E215's registered
energy misses were the gemmLnc points. Its time is MM1-v3.1's, which MM1-v3 still beats on the subset masks. The time misses that remain are a
shared offset at the subset masks (-9% to -11% at 28 shires), and MM1-v3.1's gemmLnc time at NB 12-15 (-15%).

## What this cannot say

- **Five gemmLnc points.** No sign test decides on five. The term's size on aifoundry3 rests on four points, all random fp32 data and none
  L2-resident. Card 1 rests on one point.
- **The card factor.** It is not identified (two pooled constants). E215 shows the two cards about 1.5x apart in the excess, at different shapes.
- **F1 on placement.** E215 cannot test F1's placement sensitivity. F1 gives one factor to every layout of a shape at an equal shire count:
  the layout term's own dated note, correction 6.
- **The pair noise.** Arm A's subset points ran once each, all in pass 1, so its pair noise comes from the day's two-run points. That spread
  includes the pass-1-to-pass-2 drift, so it is if anything wide.
- **verify-lnc's alternative forms** (a step at NB of 3 or less, and the forms G1-G6 of its note) were never frozen in a posted file: NOT SCORED.
- **The composition.** The counter's mean under F1, and F1's energy with t forecast, follow E216's declared composition. They were not frozen
  with F1 itself (REPORTED).
- **The model session's sealed E215 forecast** (registered 18398ed2, sha256 only) is not opened or scored here.

## Files

| file | what |
|---|---|
| `README.md` | this note |
| `DECLARED-scoring-terms-e215.md`, `.sha256` | how the terms are scored, written and hashed (e7ad00c7...) before any term was scored, with what this lane had seen by then |
| `score_terms_e215.py` | the scorer: E215's frozen scorer imported for the measured side, the frozen forecasts and the head-to-head arithmetic; standard library |
| `scores-terms-e215.json` | every number above, the checks, every per-point and per-pair record, the measured side |
| `scores-terms-e215.txt` | the scorer's printed summary |
| `part1-gemmlnc-points.csv` | part 1 per point and model |
| `part2-subset-points.csv`, `part2-layout-pairs.csv` | part 2 per subset point and per layout pair |
| `part3-all-points.csv` | part 3 per point: MM1-v3.1, MM1-v3, 'v3.1 + both terms' |
| `SHA256SUMS` | every file here |

**To re-run** from a checkout of the lab at or after 595fcb59 holding E215's data (8355db15, 4f648f24): from this folder run
`/usr/bin/python3 -I -B score_terms_e215.py`, single-threaded (OMP_NUM_THREADS=1 and the like). The lab is found five levels up, or from
`ET_LAB`.

It refuses (exit 4) if a frozen file differs from its post or a data file from its SHA256SUMS. It re-makes every file here byte for byte, but
the JSON's `made` time: checked by this lane from a lab-shaped tree. The cross-check against the card lanes' own scorer outputs (1,880 of
1,880 fields equal) was a lane-side check and is not part of this folder.

SPDX-License-Identifier: Apache-2.0
