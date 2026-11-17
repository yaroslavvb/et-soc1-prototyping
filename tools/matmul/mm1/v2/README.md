# MM1-v2: the lab's matmul model refitted with E208 on three cards, frozen for E209 (Mon 16 Nov 2026; fixed Tue 17 Nov 2026, before any E209 datum)

MM1-v2 predicts a matmul's clock cycles, seconds, joules (over idle and with the card at rest) and transistor switches on the ET-SoC-1
cards from the matrix size, the format, the data kind, the shire mask, the card and the clock. It is MM1-v1 (`../v1/`, landed 25d2e74e)
refitted with E208, the model session's matmul sweep (rgm136 at 74 arms on aifoundry2 card 0 under its governor, aifoundry1 card 1 at 600
MHz and aifoundry1 card 0 at low power), with the terms E208 identifies, and frozen for **E209, the blind matmul day on aifoundry2's card
under its governor**. This folder holds the model as frozen: the code, every input it reads (vendored and hashed), its fit and held-out
record, the unread scores of MM1-v1 and MM1-v0 on E208 made before any fit, and **its forecasts for E209's 45 never-run points, with MM1-v1
unchanged, F1 and F2 beside**. Desk only: this commit measured nothing.

The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription, where "matte mold"
is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number
of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy."

**Labels.** *Measured*: a card's committed reading. *Desk*: arithmetic or a fit made at a desk. *Post hoc*: fitted after its data existed
(every constant of MM1-v2 is). *Unread*: scored on data that existed but that the model never read. *Held out*: left out of that fit (one
experiment or one card at a time); held out is not blind. *Blind*: scored on data that did not exist when the model was frozen. A check not
run is NOT RUN. Error = forecast / measured - 1; rms and bias in %. Interpreter for every number: `/usr/bin/python3` 3.12.3, numpy 1.26.4,
scipy 1.11.4, run `-I -B`, on the lab box aifoundry2 (its desk).

## 0. On one screen

- **First, before any fit** (section 1): MM1-v1 as landed and MM1-v0 as frozen, unchanged, on all 401 committed E208 runs (UNREAD).
  Cycles (wall): **v1 7.59%** (-1.9; aifoundry2 8.92%, card 1 6.29%, card 0 7.56%), **v0 9.39%** (-3.7). W over idle given the seconds:
  **v1 9.57%** (aifoundry2 4.71%, card 1 12.0% with +5.5% bias), v0 11.39%. J with the card at rest given the seconds: v1 2.0%, v0 2.1%.
  Card 0 energy: NOT FORECAST by either (no card-0 term). Where v1 missed on aifoundry2: the knee (-12.9%, 16 runs), the one-K-block int8
  GEMM at 800 MHz (+33%: v1's L2 time is clock-free; the card's is a count of cycles), L3-served subsets (-4 to -14%: v1's contention speeds
  up an L3 stream that E208 shows does not speed up), the counter's mean at mask 0xf (-22%); ones: no price.
- **What changed** (section 2): the L2 time in cycles (F2 = 340 cycles, T2 = 0.02 us); the subset contention on the DRAM stream only (chiF
  0.27, chi3 -0.04); the L3 retention refitted on E208's K ladder (x50 39.7 MB, s 4.53 MB; v1 43.6, 7.14); the counter-mean imbalance only
  when MB >= 2; per-card terms (card 0's awake power and its own resident scale; aifoundry2's fp16 / int8 anchors scaled; card 1's awake
  power refitted on E208's 26 shapes); a price for the constant-one tile; the rest law per card; **aifoundry2's clock as an input**, with a
  governor clock model (post hoc) for the clock forecast.
- **Held out, the same points and folds** (section 3; 1,072 time points, 13 experiments, 4 cards; every fold fit converged from six cold
  starts, and a constant the fold cannot identify pinned at 0 by a declared rule): cycles LOEO **5.41%** v2 against **5.70%** for v1's form
  refitted; E206's fold 6.00% against 7.41%; subsets 7.87% against 10.62%; **LOCO aifoundry2 on E208's clean 800 MHz points 3.98% against
  7.09%**; LOCO all cards 5.50% against 5.37% (aifoundry2's older window-mean points 6.21% against 5.50%). Energy on the points both price:
  LOEO 6.59% against 6.55%, LOCO 10.13% against 9.15% (the awake power does not carry across cards).
- **E209** (section 5): 45 points, 55 runs, every shape never run on aifoundry2's card (the scan: 0 of 29 shapes in any aifoundry2 run
  data); predicted board at most 67.2 W, die at most 58.6 C in a 6 s burst, under E208's measured peaks on this card (board 71.81 / 71.86 W,
  hottest sensor 62 C), the planning bound; one point forecast capped by the governor (e44). The clock-forecast route equals the 799.0 MHz
  column at every point (the forecast win-view clock is 799.0 MHz at all 45): it adds only e44's capped flag and the burst means. **The
  forecasts are blind only once their sha256 (section 5) is in a pushed commit before E209's first card command.**
- **Fixed before landing** (fix-mm1v2, Tue 17 Nov 2026, answering verify-mm1v2; before E209's registration and any E209 datum): (1) the folds
  of the first freeze stopped wherever the optimizer did along three constants a fold without E206 or E208 cannot identify (its LOEO 5.61%,
  LOCO 5.54%, E206 fold 5.43% and subsets 7.90% were one optimizer path; equally good fits read 5.38-10.92%, 5.54-8.78%, 4.78-27.6% and up
  to 51%): the pin rule and the converged starts fix them (section 3); (2) the predictor's default volts for aifoundry1 card 1 (0.499 V)
  differed from the fit's footing (0.517 V, s_V = 1) and under-priced card-1 W about 5%: set to 0.517 V; (3) the F1/F2 route now fails on a
  missing input instead of writing 'NOT PRICED'; (4) wording (sections 4-6). **E209's forecasts are unchanged** (`out/mm1_v2_e209.csv`
  fdd018ca..., the points, MM1-v1's and F1/F2's columns: byte for byte); the files that changed are re-frozen in section 5's table.

## 1. MM1-v1 and MM1-v0 on E208, UNREAD, before any fit (`score_unread.py`, `out/unread_e208.*`)

**Why unread, not blind.** E208's first five data commits came before MM1-v1's freeze: e99209a5 (a2c0-S1, 20:32:30 PST), d40b6fe8 (a1c1-S1,
20:32:40), c2d6536c (a1c0-S1, 20:32:50), eed9624f (a2c0-S2, 20:32:59), 76fb5344 (a1c1-S2, 20:33:09), all before 25d2e74e (21:14:55); the
sixth, 7693a23c (a1c1-S3, 22:28:32), came after it. MM1-v1 did not read any of them: its inputs are vendored at d7e4f35e and its manifest
lists no E208 file. MM1-v0's predictor and constants were frozen at 13:04:57 PST, before E208's first datum (18:25:26), but no forecast for
E208's points was frozen then: these are made now by the frozen code, the call's arguments chosen now. Neither is a registered blind test.

**How each model is called** (nothing refitted). aifoundry2: the run's measured kernel clock in its primary view (about 799 MHz), the run's
measured minion volts (the view's rail; the energy manual's 0.517 / 0.568 / 0.618 V line when absent) and G = B(f) - B(600) by the M7
relation, as both models' energy fits carried aifoundry2's governed points. **How the models handle a clock other than 600 MHz**: in time,
the fixed latencies (c3, cF, the c1 law's cycles) scale as 1/f and the m terms (us, and v1's T2) do not; in energy, the resident and line
prices are per op at 0.517 V x (V / 0.517 V)^2, the awake powers are constant watts and g [B(f) - B(600)] adds the governed base. The
predictors take V and G from the caller. Card 1: its measured clock, V = 0.517 V (s_V = 1, the footing of both models' card-1 rows and of
their frozen arm B forecasts), G = 0. Card 0: neither model has a card-0 term: cycles at its clock, energy NOT FORECAST (a side reading on
aifoundry2's card terms: v1 6.28% (+3.9), v0 5.55% (+3.0), labelled 'borrowed footing', not a forecast). Ones: no resident price in either
model (NOT FORECAST; their cycles are forecast). v0 has no mask term.

| model, card | cycles (wall) | counter's mean | seconds | W = J over idle given t | J over idle, t forecast | J at rest given t | J at rest, t forecast |
|---|---|---|---|---|---|---|---|
| v1, all (401 / 278 / 296) | 7.59 (-1.9) | 9.05 (-3.3) | 7.59 (-1.9) | 9.57 (+3.1) | 9.42 (+2.0) | 2.00 (+0.3) | 5.85 (-1.9) |
| v1, aifoundry2 card 0 (160 / 120) | 8.92 (-0.8) | 10.03 (-1.9) | 8.92 (-0.8) | 4.71 (-0.1) | 5.74 (-1.2) | 1.98 (+0.1) | 6.26 (-1.6) |
| v1, aifoundry1 card 1 (195 / 158) | 6.29 (-2.9) | 8.44 (-4.8) | 6.29 (-2.9) | 12.0 (+5.5) | 11.44 (+4.4) | 2.02 (+0.4) | 5.55 (-2.1) |
| v1, aifoundry1 card 0 (46) | 7.56 (-1.5) | 7.88 (-2.1) | 7.56 (-1.5) | NOT FORECAST | NOT FORECAST | NOT FORECAST | NOT FORECAST |
| v0, all | 9.39 (-3.7) | 9.32 (-4.5) | 9.39 (-3.7) | 11.39 (+3.4) | 10.87 (+1.4) | 2.11 (+0.2) | 7.51 (-3.1) |
| v0, aifoundry2 card 0 | 9.45 (-3.2) | 9.34 (-3.7) | 9.45 (-3.2) | 4.25 (-1.0) | 6.95 (-2.9) | 1.80 (-0.3) | 7.66 (-3.4) |
| v0, aifoundry1 card 1 | 9.47 (-4.0) | 9.41 (-5.3) | 9.47 (-4.0) | 14.65 (+6.8) | 13.08 (+4.6) | 2.30 (+0.6) | 7.41 (-2.9) |
| v0, aifoundry1 card 0 | 8.86 (-3.9) | 8.82 (-4.1) | 8.86 (-3.9) | NOT FORECAST | NOT FORECAST | NOT FORECAST | NOT FORECAST |

By class (MM1-v1, cycles wall; full tables per card, shape class, format, data kind, mask, family and role in `out/unread_e208.md`):
aifoundry2 inside the L3 6.1% (54 runs), one K block 15.1% (+6.1; 30), the knee 13.9% (-12.9; 16), past the L3 3.6% (60); card 1 the knee
13.5% (-12.8), one K block 2.6%; zeros on card 1: W over idle +21.2% (42 runs: v1's card-1 awake power came from one shape). Per distinct
case (one value a card and case, 184 cases): v1 8.06% cycles, 9.85% W over idle; v0 9.73%, 11.83%. W under 3 W (18 runs, in watts): v1 0.29 W rms (+0.22), v0 0.32 W (+0.18).

## 2. What MM1-v2 computes, and what changed (mm1_core_v2.py, mm1_v2.py)

MM1-v1's map is unchanged (section 2 of `../v1/README.md`: 192 lines a shire-op by place, design B's stack distances, the lab's L2 model,
the logistic L3 retention, the power-of-two terms; subsets mapped at the full chip's lines). The equations, with v2's changes in bold:

```
T_op = 1/2 sum Q0 max(Tc, kA tau_A[a], tau_B0[b]) + 1/2 sum Q1 max(Tc, kA tau_A[a], tau[b])          (wall basis, us, at the clock f)
tau[L2] = F2 / f + T2  (gemmL loop)    tau[L3] = c3 / f + m3 X3    tau[F] = cF / f + mF XF    X3 = 1 - chi3 (1 - n/32), XF = 1 - chiF (1 - n/32)
counter's mean = wall / rho / imbalance (imbalance only when MB >= 2)
W = Pmin(card) n/1,024 + Pmem u + g [B(f) - B(600)] + (n / t_op) s_V(f) [k_res(card, fmt) e_res(card, fmt, kind) + sum_l n_l/32 (b_l + d_l phi)]
e_res(ones) = (k_res Z + D_ones(fmt)) / R      s_V = (V(f) / 0.517 V)^2      J at rest = P_rest(T0) t + J over idle
```

| change | value (desk, post hoc) | read off E208 |
|---|---|---|
| **the L2 time in cycles** (F2 beside v1's clock-free T2) | F2 339.6 cycles, T2 0.023 us | gemmL1x1x1 int8 takes 392.5 cycles an op at 799 MHz (aifoundry2, card 0) and 389.8 at 600 MHz (card 1): a count of cycles. v1's 0.614 us read +33% at 800 MHz |
| **subset contention on the DRAM stream only** (chiF; chi3 on the L3 stream apart) | chiF 0.270, chi3 -0.036 | E208's gemmL1x1x4 (L3-served) at 1, 4 and 16 shires ran within 0.6% of the full chip (slower, not faster), on aifoundry2 and card 1; E206's fresh-served gemmL4x8x4 subsets ran faster than the full chip (v1's reading: one shire at 0.88) |
| **the L3 retention refitted** (no new term) | x50 39.7 MB, s 4.53 MB (v1 43.6, 7.14) | the K ladder gemmL1x1xKB: all L3-served to KB 10 (32 MB), fresh from KB 14 (44 MB) |
| **the counter-mean imbalance only when MB >= 2** | v1's eta_m 0.214, gamma 2.54 (the same 4 E206 points) | E208's MB = 1 subsets at 0xf read wall / mean 1.001-1.08, not v1's 1.21 |
| **the clock an input on aifoundry2** | V(f): 0.517 / 0.568 / 0.618 V; G(f) by the M7 relation | E208's win view at 799 MHz; E208's measured minion rail 616-619 mV there |
| **card 0's terms** (new card) | Pmin 1.132 W; k_res fp32 1.344, fp16 1.445, int8 1.101 on aifoundry2's anchors; V 0.604 V at 800 MHz | its 37 low-power arms (zeros, ones, int8 random); see section 6 for what they cannot identify |
| **aifoundry2's fp16 / int8 anchors** (ledger v2 placeholders: aifoundry3's zeros anchor) | k_res fp16 0.990, int8 0.968 | E208's aifoundry2 fp16 and int8 arms |
| **card 1's awake power refitted** | Pmin 2.406 W (v1 3.257 from one shape) | E208's 74 card-1 cases (24 shapes) at 600 MHz |
| **ones** (no ledger row) | D_ones fp32 8.52 W, fp16 8.30 W, int8 1.84 W over zeros (resident, 600 MHz); phi from the tile's bits | E208's ones arms at three shapes, three formats, three cards |
| **the rest law per card** (REPORTED) | aifoundry2, aifoundry3, card 1: ledger v2's frozen footing quads; card 0: a line on E208's rests | on E208's rests: aifoundry2 +0.14 W mean (0.18 rms, 137 runs), card 1 +0.28 W (0.31), card 0 0.00 (0.08, fitted) |
| **the governor clock model** (section 4) | t_climb 0.638 s, tau 1.40 s, P_th 66.6 W on measured powers; 63.3 W in the chain | E208's 160 aifoundry2 runs |

The other constants (all refitted): c3 318.8, cF 408.9 cycles; m3 0.801, mF 1.562 us; kA 1.108; zeta 0.721; piF0 0.214; eta 0; Pmin
aifoundry3 1.379 W, aifoundry2 2.061 W; Pmem 0.184 W; b2/d2 58.9/501.2, b3/d3 245.1/1,150.2, bF/dF 794.7/1,298.6 pJ a line a shire-op;
g 0.779. Every constant: `out/mm1_v2_params.json`. Card 1 keeps v1's footing (s_V = 1: its ledger anchors were measured on the card itself);
a fit at its measured 0.499 V read worse in sample (E208's card-1 W given t 8.3% against 6.3%, on five of E208's sessions) and was not kept.
The predictor's default for card 1 is that footing, 0.517 V (`mm1_core_v2.CARD_V`; fix-mm1v2: the first freeze's default was 0.499 V, and
priced at each fit point's measured seconds it read card-1 W 5.0% below the fit's own (-6.3 to -2.7%, 92 points); now +0.00%; aifoundry3's
default 0.522 V reads +0.05%, aifoundry2's volts law -0.00% and card 0's -0.06% against the fit's measured volts).

## 3. Held out: the same points and folds for v2 and for MM1-v1's form refitted (`fit_v2.py`, `out/holdout_v2.json`, `out/summary_v2.md`)

1,072 time points (MM1-v1's 888 and E208's 184: one point a card and case, the mean of its runs in the primary view) and 964 energy points
(v1's 791 and E208's 173; v1's form prices 940 of them: not ones). Leave one experiment out (13 folds) and one card out (4: aifoundry3,
card 1, aifoundry2, card 0); cold starts; every constant refitted in every fold, the energy fold on its own time fold's lines and seconds
(ones NOT FORECAST in a fold with no ones point of their format; a missing card takes the other cards' mean awake power and k_res 1).

**The fold fits** (fix-mm1v2, Tue 17 Nov 2026, answering verify-mm1v2's finding 1; a rule declared before this rerun, post hoc as an act):
- **The pin rule.** Three of v2's time constants are each identified by one experiment's points only: chiF (the DRAM stream's subset
  contention) by E206's fresh-served subsets; chi3 (the L3 stream's) by E208's L3-served subsets; F2 (the L2 time in cycles, apart from T2
  in us) by E208's one-K-block gemmL loop at two clocks. In a fold whose training points hold none of that experiment the constant is
  pinned at 0 (no contention on that stream; the L2 time all in us, as in v1's form): chiF in LOEO E206 and LOCO aifoundry3, chi3 and F2 in
  LOEO E208. One-chi forms (v1's and v2 with one chi) are never pinned: E206's and E208's subsets both move their chi.
- **Converged, six starts.** Every fold fit runs from v2's cold start and five spread starts (none read off any fit) until its tolerances
  are met, at most 6,000 evaluations (one of the 408 fold-fit starts, v2's LOEO E146 start 2, stopped at that limit, 3e-6 above its fold's
  best cost, with the same held-out error); the lowest training cost is kept, and every kept fit converged. The starts that reach the best
  cost agree on the held-out error to 0.01 point in every fold.
- **The all-data fit is the frozen one** (one start, at most 800 evaluations): it sets the parameter files and E209's forecasts. Its
  converged refit lowers its training cost by 3e-6 and would move E209's cycles 0.013% rms (max 0.05%) and W 0.006% rms: kept as frozen.

| cycles (wall) | v2 | v1's form refitted | v2 without F2 | v2 with one chi |
|---|---|---|---|---|
| in sample | 4.11 (-0.3) | 4.43 (-0.3) | 4.36 | 4.18 |
| LOEO all (1,072) | **5.41** (-0.1) | **5.70** (-0.2) | 5.55 | 5.56 |
| LOEO, the 888 pre-E208 points | 4.77 | 5.07 | 4.96 | 4.89 |
| LOEO, E208 (its fold, 184) | 7.77 (-1.5) | 8.05 (-1.8) | 7.77 | 8.05 |
| LOEO, E206 (its fold, 119) | 6.00 | 7.41 | 7.10 | 6.36 |
| LOEO, subsets (37) | 7.87 | 10.62 | 8.73 | 9.92 |
| LOCO all | 5.50 (+1.4) | 5.37 (+0.9) | 5.34 | 5.65 |
| LOCO aifoundry3 / card 1 / aifoundry2 / card 0 | 4.46 / 4.98 / 6.21 / 5.24 | 4.95 / 5.83 / 5.50 / 6.19 | 4.94 / 5.49 / 5.52 / 6.19 | 4.48 / 5.36 / 6.40 / 5.24 |
| **E208's aifoundry2 points: in sample / LOEO / LOCO** | 4.59 / 9.09 / **3.98** | 6.16 / 9.39 / **7.09** | 5.95 / 9.09 / 6.94 | 4.85 / 9.39 / 4.22 |
| E208's card 1 / card 0 points, LOCO | 4.98 / 5.24 | 6.03 / 6.19 | 5.60 / 6.19 | 5.46 / 5.24 |

- LOEO by experiment (v2): E105 2.6, E107 4.0, E119 4.1, E126 4.1, E136 3.5, E146 4.8, E158 5.2, E159 4.5, E168 2.3, E169 7.1, E190 6.2,
  E206 6.0, E208 7.8 (v1's form: 2.6, 4.3, 3.9, 4.2, 3.6, 4.6, 5.2, 4.7, 2.3, 7.1, 6.2, 7.4, 8.1).
- **Why the rule: the flat directions** (the training cost along the pinned constant, every other constant refitted from the fold's pinned
  solution; `holdout_v2.json` 'profiles'): LOEO E206, chiF from -0.6 to 0.9: training cost 0.78785-0.78786, while the held-out E206 error
  runs 4.6-13.0% and its subsets 5.8-35.9%; LOCO aifoundry3, the same chiF range: cost 0.664885 throughout, held out 3.9-8.0% (subsets
  6.0-36.7%); LOEO E208, chi3 from -0.2 to 0.4: cost 0.646818 throughout, held out 7.8-8.7% (its subsets 1.4-11.1%). F2 in LOEO E208 is not
  flat: the cost rises from F2 = 0 (0.6468) to 0.7346 at 450 cycles, so the pin is the training optimum there. **The first freeze's numbers**
  (LOEO 5.61, LOCO 5.54, E206 fold 5.43, subsets 7.90, E208 fold 8.45, v2 without F2 5.82 / 5.20) were where one optimizer path stopped on
  these flats (verify-mm1v2 found equally good fits from 5.38 to 10.92% LOEO); they are superseded.
- **Two folds have two minima**: LOEO E169 (v2 training cost 0.7790 -> held out 7.08%, against 0.8031 -> 8.47%; v1's form
  0.9242 -> 7.05% against 0.9487 -> 8.62%; the first freeze sat in v2's higher one) and LOCO aifoundry2 (v2 0.3310 -> 6.21% against 0.3471 ->
  5.17%; v2 with one chi 0.3463 -> 6.40% against 0.3696 -> 5.16%). The lower training cost is kept, whatever it reads held out.
- **LOCO aifoundry2 is identified now** (v1: unidentified, 36.9%): card 0 ran at 800 MHz, so the fold without aifoundry2 still sees the top
  point. On E208's clean 800 MHz points v2 carries from the other cards at 3.98% against 7.09%; on aifoundry2's older points (window-mean
  clocks of governed runs, E119-E190) v2 is worse (6.21% against 5.50% over all 557).
- **F2** fixes E208's one-K-block int8 at 800 MHz in sample (+1% against +19-33%) and is the physical reading of 392.5 / 389.8 cycles at the
  two clocks; held out, v2 without F2 reads 5.55% LOEO / 5.34% LOCO against v2's 5.41% / 5.50%: the folds neither support nor refute it
  clearly, and without E208 no fold identifies it. v2 keeps it because E209 runs at E208's clock on E208's card.
- **Not every LOEO case is unseen**: 12 of E208's aifoundry2 cases (gemmL4x8x8 in three formats and two kinds, 1x1x8 three times, 1x2x4,
  4x8x2, 1x2x2) were also run in E136, E146 or E159, and 11 of E206's cases (gemmc1, gemmc16s, gemmc8s) in E105 or E107, which train in the
  experiment's LOEO fold. LOCO holds every case of its card out.
- Counter's mean, E208's points: in sample 4.81%, LOEO 7.88%, LOCO 4.84%.

| energy, the 940 points both forms price | v2 | v1's form refitted |
|---|---|---|
| W = J over idle given t (>= 3 W), in sample / LOEO / LOCO | 5.13 / **6.59** / 10.13 | 5.15 / **6.55** / 9.15 |
| J over idle, seconds forecast, LOEO / LOCO | 7.35 / 10.20 | 7.35 / 9.55 |
| J at rest given t, LOEO / LOCO | 2.03 / 3.02 | 1.98 / 2.58 |
| J at rest, seconds forecast, LOEO / LOCO | 5.05 / 5.41 | 5.25 / 5.16 |
| E208 aifoundry2, W given t: in / LOEO / LOCO | 5.06 / 4.82 / 9.03 | 5.05 / 4.81 / 7.75 |
| E208 card 1, W given t: in / LOEO / LOCO | 6.10 / 12.63 / 13.88 | 6.27 / 12.72 / 11.40 |
| E208 card 0, W given t: in / LOEO / LOCO | 4.28 / 6.99 / 6.17 | 4.94 / 6.95 / 6.08 |
| W under 3 W (18 points), watts rms: in / LOEO / LOCO | 0.23 / 0.39 / 0.50 | 0.23 / 0.40 / 0.55 |
| ones (v2 only), W given t: in / LOCO | 4.0 / 7.7 (-4.3) | NOT FORECAST |

The energy additions do not improve the held-out energy on the points both forms price; they price ones (24 points, LOCO 7.7%) and card 0
in sample (4.3% against 4.9%). LOCO energy is poor for both: each card needs its own GEMM anchor (v1's finding stands).

## 4. aifoundry2's clock: given the measured clock, and the governor's forecast (`governor_v2.py`, `out/governor_v2.json`)

- **Given the measured clock**: the frozen predictor at the run's measured kernel clock in its scored window, with V(f) and G(f) from the
  clock. `out/mm1_v2_e209.csv` tabulates it at 799.0 MHz (E208's aifoundry2 win-view median), 700 and 600 MHz, with the affine W (A + B /
  t_us) for the given-seconds score; any other clock is `mm1_v2.Model(params).predict(..., f=<clock>)`.
- **The governor model** (post hoc; fitted on E208's aifoundry2 runs only): the loop the lab's findings document (16-dvfs-and-leakage.md,
  14-card-behaviour.md, E64): each process starts at the 600 MHz boot point and climbs; once per pass (0.16 s), thermal first (the shires'
  mean above 65 C steps down), then the power test on a first-order average of the board (tau) against a threshold, one point down above it,
  one up below it, no dead band; three points 600 / 700 / 800 MHz. On each run's measured powers: t_climb 0.638 s, tau 1.40 s (E64: 1.3 s),
  P_th 66.6 W (the card's TDP 65 W); capped (the reducer's rule) agrees on 159 of 160 runs; the burst's mean clock 10.8 MHz rms.
- **Its base rate** (fix-mm1v2): 19 of the 160 runs were measured capped, so 'never capped' would agree on 141 of 160; the loop's 159 is
  measured against that. The one run it misses on measured powers, a2c0-S2 052 (gemmL1x1x1 int8 ones), was capped (an 800 MHz share of
  0.75 against the 0.8 line) at a launch power of 41.8 W and a die of at most 54 C: neither the power test nor the thermal test explains that
  cap. The governor model is in sample on E208 only: its out-of-sample check on this card's other governed runs (E190 arm A, E194, E200) is
  NOT RUN, and no script here reads the vendored telemetry files (`inputs/e208/a2c0-S*__telemetry.jsonl.gz`).
- **The chain** (the clock-forecast route: v2's own powers, the rest law's rest + v2's W at each point, into the same loop): P_th refitted
  to 63.3 W; capped agrees on 157 of 160 (it misses 052 and two fp32-random gemmL1x1x10 runs whose powers v2 puts at 64.3-64.4 W against
  69.5-70.2 W measured); burst clock 11.2 MHz rms. **v2's W in the fp32-random L3-served corner at 800 MHz is not validated**: E208's 18
  runs there were capped, so the registered reducer read no energy, and their launches' board power read 2.5-6 W above v2's forecast (47 W
  against 41-45 W over idle); the chain's lower threshold absorbs that bias for the capped forecast, not for the watts.
- **With the clock forecast**: the frozen predictor at the forecast clock: the win view's clock (799.0 MHz whenever a launch 1.0-3.5 s into
  a process holds the top point) and the burst's mean clock (`clock_fc_*` columns); a point forecast capped carries no energy reading under
  E208's reducer rule. **On E209's points the two routes coincide** (fix-mm1v2): the forecast win-view clock is 799.0 MHz at all 45 points,
  so the clock-forecast route's cycles, seconds and W are the 799.0 MHz column, which is also what 'given the measured clock' gives a run
  measured at 799.0 MHz. The clock forecast adds only e44's capped flag (its forecast 800 MHz share 0.78, just under the reducer's 0.8 line) and the
  burst-mean columns (764-779 MHz; cycles an op 1.5-2.9% fewer there); the routes part on E209 only where a run's measured clock is not 799.

## 5. E209: the points and the forecasts (`e209_v2.py`, `f1f2_e209.py`, `out/e209_points.csv`, `out/mm1_v2_e209.*`, `out/mm1_v1_e209.csv`, `out/f1f2_e209.*`)

**Card**: aifoundry2 card 0 under its own governor, as found (TDP 65 W, threshold 65 C, power state 3), nothing set; rgm136 unchanged (kernel
ELF aace138c..., E206's and E208's host flags); a 6 s burst a process (E208's form). **45 points (distinct cases), 55 runs planned**:

| family | points | shapes (gemmL MBxNBxKB; format kind mask, full chip unless named) |
|---|---:|---|
| inside the L3 | 6 | 1x3x2 int8 (2 runs), 2x3x2 fp16, 3x2x2 int8 zeros, 1x3x2 fp32 at 0x0000ffff (2), 1x4x3 fp32 ones, 2x3x2 fp32 zeros |
| one K block | 2 | 1x3x1 int8 (2), 3x5x1 int8 |
| the knee | 7 | 1x1x11 fp32 (2), 1x1x13 fp32 zeros, 1x2x9 fp32 (2), 2x1x6 int8, 2x2x5 fp16, 3x1x5 fp32 zeros, 1x3x7 int8 |
| past the L3 | 5 | 2x6x10 fp32 (2), 3x5x5 fp16, 6x6x6 int8, 5x3x6 fp32 zeros, 3x5x5 int8 ones |
| long K | 5 | 1x1x40 fp32 (2), 1x2x24 fp32 zeros, 2x1x20 int8, 1x2x14 int8, 2x3x16 fp16 |
| power-of-two strides | 5 | 1x8x6 / 1x7x6 fp32 (2 each), 2x8x4 int8, 1x4x12 fp32, 1x16x6 fp16 |
| data kinds | 5 | real (E206's four tiles a format): 2x6x10 fp32 (2), 1x3x2 int8, 3x5x5 fp16; ones 2x6x10 fp16; zeros 6x6x6 int8 |
| subsets | 8 | 2x1x3 fp32 at 0xff, 1x1x7 int8 at 0xf, 2x3x2 int8 at 0x1111, 2x6x10 fp32 at 0x80000000 (1 shire), 1x8x6 fp32 at 0x1111, 3x5x5 fp32 at 0xffff0000, 6x6x6 int8 at 0xf000, 1x3x2 fp16 at 0x1 |
| the governor | 2 | 1x3x2 fp32 (forecast capped), 1x4x3 fp16 (forecast near the cap) |

(Formats fp32 20, int8 16, fp16 9; kinds random 32, zeros 7, ones 3, real 3; shires 32 /
16 / 8 / 4 / 1 on 36 / 2 / 1 / 4 / 2 points.)

- **Never run on aifoundry2's card** (`out/neverrun_e209.json`, Mon 16 Nov 2026 about 23:12 PST): every one of the 29 shapes grepped (the
  token gemmL<MB>x<NB>x<KB>) in the lab at GitHub main 7693a23c (docs and tools: every data folder, aifoundry2's E105-E208 among them), the
  round's lane folders and the lab account's work folders on aifoundry2 (the model session's sweep sessions there included); a hit in any
  aifoundry2 run data takes a shape off (a data folder not named for another card counts as aifoundry2's). gemmL1x1x24 was taken off (E208
  ran it on aifoundry2 in fp32); 0 of the 29 kept shapes have any aifoundry2 run. Not scanned: aifoundry1's and aifoundry3's own folders
  (other cards). Since the scan, the model session ran an added repeat of E208's session a2c0-S1 on this card (from 23:31 PST Mon 16 Nov,
  announced as S1's schedule unchanged): that schedule (`inputs/e208/src__sched__a2c0-S1.json`) holds 24 shapes and none of E209's 29; its
  data was not read here. **Re-check at E209's registration and right before its first card command, the repeat's committed data
  included.**
- **Planning** (not forecasts of a stop): the highest forecast board power at the top point 67.2 W (e44; the rest law's 23.2 W at 51 C + v2's
  W); the die at most 58.6 C over a 6 s burst (die0 51 C + 0.173 C/W x W) and 64.2 C over three back-to-back processes (a desk 0.30 C/W).
  **The planning bound is E208's measured peaks on this card**, which sit above that forecast: board at most 71.81 W (a2c0-S1) and 71.86 W
  (a2c0-S2), die at most 59 / 60 C, hottest sensor 62 C (E208's checks, C5); v2 under-reads the fp32-random L3-served corner by 2.5-6 W
  (section 4). Both are well under the stops of E194's and E200's kits on this card: board above 85 W on 3 samples in a row, the shires'
  mean or the hottest sensor at or above 80 C. Card time: 22.6 card-minutes in E208's forms (a burst a run, three processes under 8 W over idle), 64.2 with three processes a
  run; about 5 more for the anchor, the smoke and the opening rest.
- **Each point's record**: cycles an op (wall and the counter's mean), seconds a GEMM, W over idle, the affine W and J over idle at 799, 700
  and 600 MHz; the clock forecast (capped, burst mean, the 800 MHz share) and the forecast at it; the rest law's J at rest (REPORTED);
  switches (MM1-v1's estimate, carried unchanged); the timing simulation's count and the measured floor.
- **MM1-v1 beside** (`out/mm1_v1_e209.csv`): the landed predictor unchanged (its SHA256SUMS checked: 77 of 77), called with aifoundry2's
  arguments at the same clocks (V by the energy manual's line, G by the M7 relation); ones and real energy NOT FORECAST (no aifoundry2 row).
- **F1 and F2 beside** (`out/f1f2_e209.*`): E206's registered routes are registered for its arms only (aifoundry3 and card 1 at 600 MHz) and
  cannot be called as registered for E209's top-point runs. F1@600: E206's F1 unchanged for aifoundry2 at its boot point (its watts are
  aifoundry2's own; kappa 1). **F1@800**: E190's arm-A route (E206's F1's source, which forecast aifoundry2 at 800 MHz) generalized with
  E206's lines. **F2@800**: ledger v3 priced as E206's F2 prices a GEMM, the load's card aifoundry2 at 800 MHz (rule 7 adds the governed
  base). Ones: NOT PRICED by either. The route reads the lab at run time, its three named files pinned by sha256 (as MM1-v1's), and ledger v3
  reads the lab's data folders: run it at the lab's top in a full checkout. It now stops, writing nothing, on a missing or unreadable file or
  when F2 prices fewer points than have a ledger row (42 of 45 here); the first freeze's copy wrote 'NOT PRICED' instead (fix-mm1v2's test:
  with the ledger's inputs absent, the first copy exited 0 with F2 unpriced on 42 points; the fixed copy exits 1 and writes nothing).
- **F1@800 and F2@800 are desk generalizations made by the lane that built v2, and they already miss E208's aifoundry2 points** (post hoc:
  `f1f2_e209.py` run by fix-mm1v2 on E208's 63 aifoundry2 zeros and random cases, against their measured values): F1's cycles an op 15.8%
  rms (+7.0); W over idle on the full chip F1 12.5% (+2.4), F2 39.5% (-27.3) (42 cases); on subsets F1 58.2% (-50.9), F2 70.7% (-65.9) (10
  cases). v2 was fitted on those points, so E209's head-to-head of v2 against F1 and F2 is largely decided before E209 runs. **The
  informative head-to-head is v2 against v1** (predicted gaps 4.8% in cycles, 2.6% in W): E209's registration should weight those rules.
- **The predicted gaps** (rms |ln| on the same points; not a score): cycles v1 / v2 4.8% (45), F1@800 / v2 17.1%; W over idle v1 / v2 2.6%
  (39), F1@800 / v2 56.9% (42), F2@800 / v2 84.9% (42). v1 and v2 part mostly on the L3-served subsets (v1 0.85-0.92 of v2 in cycles), the
  knee's zeros, ones and real (v1 NOT FORECAST); F1 and F2 part from v2 on the 1-, 4- and 16-shire points (F1 scales a subset's watts by
  shires / 32; v2 keeps the governed base and the memory path awake).

**The freeze line** (E209's forecasts and what makes them; every file is in `SHA256SUMS`):

| file | sha256 |
|---|---|
| `out/mm1_v2_e209.csv` (MM1-v2's forecasts) | `fdd018ca9ceb420285746acdc94b2e0fc62a68141d9b0d3990c3cf9777ec3a63` |
| `out/mm1_v2_e209.json` (the same, every field) | `f6c5c0ed3451e5b7418b980a8cfc03d9b1f4ab404d2fe1c22f02a070db29e970` |
| `out/e209_points.csv` (the points) | `5e425b771f84e0af53068a6293d46a8fdec40f17dd0381f6a909a9eae2298e8a` |
| `out/mm1_v2_params.json` | `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5` |
| `mm1_v2.py` / `mm1_core_v2.py` / `kinds_v2.py` / `governor_v2.py` | `5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08` / `f78c21b4f8b4c43a9a6c7319f12092937e9e92c69d3e7dc036f0e1f92b9d7e08` / `14c72c298956c551439a6eddb77f9d75a7b7fe3414cbb78cfbd0ad5a70ed686d` / `6276d4c7f7f074fbc2681040a8d63eb2ab07104e96e4ebd5459d8ef7adbadd44` |
| `out/mm1_v1_e209.csv` (MM1-v1 beside) | `f51336af951447678763f0b483c06668d3b462c3c4c30891dc14286112d3a7d3` |
| `out/f1f2_e209.csv` / `.json` (F1, F2 beside) | `65a98e01868743b4daf4b06be1b1ba4edbd77c47f3d4824353ffdb0bf4ceefce` / `a32f166d2a893fa724fb8cdbc937ed7e7ddb6f304790f0834ca0f3eda163b54f` |

**Re-frozen by fix-mm1v2** (Tue 17 Nov 2026, before E209's registration and before any E209 datum): against the first freeze (the lane's
local commit, never pushed), three rows changed and no forecast did: `out/mm1_v2_e209.json` (was 49ced52e...: only its `params_sha256`
field), `out/mm1_v2_params.json` (was dbd52e61...: only its volts record, card 1 0.499 -> 0.517 V) and `mm1_core_v2.py` (was 76fe2a7f...:
`CARD_V` card 1 and two comments). `out/mm1_v2_e209.csv`, the points, MM1-v1's and F1/F2's files are byte for byte the first freeze's.

## 6. What the data cannot identify (stated)

- **Card 0** (aifoundry1 card 0, low power only): all its 38 energy points ran at 799 MHz, so its awake power and its governed base cannot
  be told apart. v2 **assumes** card 0's governed base is aifoundry2's (the shared g times the M7 relation: 0.779 x 8.10 W = 6.31 W at 799
  MHz; not identified), and Pmin card 0 (1.13 +- 0.32 W, a 28% standard error) is the residual awake power, not both (corrected by
  fix-mm1v2: the first freeze's text said Pmin carried both). Its resident scale k_res is fitted per format on its own arms: fp32 1.34 +-
  0.17 on 17 points (zeros and ones only), fp16 1.45 +- 0.19 on 5 (zeros and ones), int8 1.10 +- 0.10 on 16 (zeros, ones and random); no fp32
  or fp16 random ran (their planning estimates passed the card's 52 W line), so a card-0 fp32 / fp16 random forecast leans on aifoundry2's
  anchor x a k_res fitted on zeros and ones; its volts below 800 MHz are a guess (0.517 V at 600). LOCO card 0: cycles 5.24%, W given t
  6.17%. (Standard errors: the all-data energy fit's weighted least squares, s^2 (X'X)^-1, desk.)
- **aifoundry2 above the cap**: E208's fp32-random L3-served arms were capped (time only): v2's watts there are an extrapolation (section 4).
- **The L2 time's clock law** rests on E208's one-K-block int8 shape at two clocks (gemmL1x1x1 at 799 and 600 MHz); other KB = 1 shapes are
  L3-bound (v1 and v2 agree within 4%).
- **Subsets**: E206's 14 and E208's 23 subset points (masks 0x1, 0xf, 0xff, 0xffff, 0x11111111); the 8- and 4-shire layouts of E209 (0xff,
  0x1111, 0xf000) and the 1-shire 0x80000000 are new.
- **Ones**: three shapes (1x1x1, 1x1x4, 4x8x8) a format; E209's ones points (1x4x3, 3x5x5, 2x6x10) test the price elsewhere.
- **Real on aifoundry2**: ledger v2 has real rows on aifoundry3 only; v2 carries them by the card's own random / aifoundry3's random ratio
  (a desk transfer rule); E209's three real points test it.

## 7. Transistor switches (carried from MM1-v1 unchanged)

v2 carries MM1-v1's switch estimate exactly as v1 defines it (`../v1/README.md` section 7: the die, the fresh-line path set apart; counted =
the tensor unit's open-flow fin edges; estimated = the die's other classes from the energy, int8 arithmetic included), applied to v2's own
energy split by class; card 0 takes aifoundry2's regulator coefficient. No fault was named in it; nothing on a card measures switches (not
scorable).

## 8. Gaps and NOT RUN

- One card on the blind day (aifoundry2 under its governor); its scored window holds one clock (the top point), so E209 tests the clock law
  only through the governor points and the comparison with E207's shapes on aifoundry3 card 0.
- The energy additions do not improve held-out energy on the points v1's form prices (section 3).
- The governor model and the chain are post hoc on the card E209 runs on; their capped forecast is tested only by e44 and e45; 'never
  capped' would already agree on 141 of E208's 160 runs (section 4).
- E209's two clock routes coincide on its points unless a run's measured clock leaves 799 MHz (section 4); its head-to-head against F1 and
  F2 is largely decided by E208 already (section 5).
- The pin rule is post hoc as an act: declared after verify-mm1v2 found the flat directions, before this rerun, and the same for every
  form; the first freeze's held-out numbers are kept in section 3 as superseded.
- NOT RUN: any card or simulator; any remote command (neither lane made one); a scan of aifoundry1's and aifoundry3's own folders; a
  leave-one-mask-out of the subset terms with v2's split; an RSW second form; F1 / F2's own given-seconds evaluation on E209 (that is E209's
  scorer's); the governor model on this card's other governed runs (E190 arm A, E194, E200); a multi-start of the all-data fit as the frozen
  fit (it stays one start: its converged refit is recorded, and moves E209's cycles 0.013% rms).

## 9. Files and how to reproduce

- **Code**: `mm1_core_v2.py` (MM1-v1's map and equations, copied from `../v1/mm1_core.py` at 25d2e74e with its inputs' folder moved to
  `inputs/v1/`, and v2's time form appended), `mm1_v2.py` (the predictor), `kinds_v2.py` (v1's kind term, the same move), `data_v1pts.py`
  (v1's measured points, the same move), `data_e208.py` (E208's runs), `score_unread.py` (section 1), `fit_v2.py` (the fit and folds),
  `governor_v2.py` (the governor, the chain, the rest laws, the merged parameter file), `e209_v2.py` (E209's scan, points and forecasts),
  `f1f2_e209.py` (F1 and F2 beside), `summary_v2.py` (the tables).
- **inputs/**: 82 files, each with its source and sha256 in `inputs/MANIFEST.json`: `v1/` MM1-v1's 44 inputs and its MANIFEST.json, byte for byte (45 files); `e208/` the six
  sessions' reducer output, checks and sums and aifoundry2's two telemetry files, byte for byte from GitHub main 7693a23c (`e208/SOURCES.json`
  names each file's commit), with E208's arms and schedules; `tiles/` the three ones tiles.
- **out/**: 19 files: `unread_e208.*`, `holdout_v2.json`, `points_time_v2.csv`, `points_energy_v2.csv`, `mm1_v2_params_core.json`,
  `mm1_v2_params.json`, `governor_v2.json`, `rest_v2.json`, `neverrun_e209.json` (the scan's record, not a generator's output), `e209_points.csv`,
  `mm1_v2_e209.csv` / `.json`, `mm1_v1_e209.csv`, `f1f2_e209.csv` / `.json`, `summary_v2.json` / `.md`.
- **Reproduce** (from this folder, `/usr/bin/python3 -I -B`, each into a new folder D): `score_unread.py --out D --scratch <new folder>`;
  `fit_v2.py --out D`; `governor_v2.py --core D --out D`; copy `out/neverrun_e209.json` to D; `e209_v2.py forecast --params D/mm1_v2_params.json
  --scan D/neverrun_e209.json --out D`; `f1f2_e209.py --repo <the lab's top> --points D/e209_points.csv --out D`; `summary_v2.py --out D`
  (about 16 minutes in all, single-threaded: `fit_v2.py` runs every fold from six starts to convergence; set OPENBLAS_NUM_THREADS=1 on a
  shared box). The first freeze reproduced 19 of 19 outputs byte for byte (Mon 16 Nov, the last at 23:15 PST); after fix-mm1v2's changes
  the whole chain was run again on aifoundry2 into a new folder from a `git archive` of the commit's tree (the code as it lands), Tue 17 Nov
  2026, 00:42-00:57 PST: **19 of 19 outputs byte for byte**. (This README's text was edited after that run; no code or output was.)

SPDX-License-Identifier: Apache-2.0
