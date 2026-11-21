# 'MM1-v3.2 + mask-ceiling': a nonparametric REFERENCE for core-group mask placement (reference, REPORTED; round Q238, track C)

*Round Q238, lane mask-ceiling, Sat 21 Nov 2026 (week 47), Pacific time, at aifoundry2's desk. Desk only: no card, no simulator, no E226 file. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP / OPENBLAS / MKL / NUMEXPR_NUM_THREADS = 1), every job in the round's CPU slots, one at a time. **Never a model candidate**: it bounds what a mask term built from these features can reach, and ranks the features.*

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained."

**Labels.** *Post hoc*: every fit here (made after its data existed). *Held out*: left out of the fit that scores it (not blind). *REPORTED*: printed beside a rule, never deciding it; the whole reference is REPORTED. *NOT RUN*: not run. Errors: forecast / measured - 1 of the wall cycles an op (%), blind-e221's form.

## 1. The lead

The lab's blind test of E221 (tools/matmul/mm1/v3.1/blind-e221-scores/, 5eb23fd4) failed on MM1-v3.2's time bands; 152 of its 175 T1 misses are core-group mask placements: the MASK class reads 12.41% rms on 363 no-twin cases, every other class at most 9.05%. This reference asks how much of that a term built from mask features could remove, held out, and which features carry it.

## 2. The form (declared before any fit: `DECLARED-mask-ceiling.md`, sha256 `e9701ff2c7437736a2843266876461f96a44fd5f4774ef929430c06e6cdc3b4b`, hashed 01:28:32 PST)

T = T_v32 x exp(clip(yhat, -0.5, 0.5)) at the scope's points (rgm136 gemmL, MB x NB >= 2, a shire subset: 888 points), T_v32 to the last bit elsewhere; yhat = a random forest (this lane's numpy code, `scripts/rf_core.py`) of 200 CART trees, depth 6, leaf 5, bootstrap rows, 8 of 22 features a node, trained on ln(T_meas / T_v32) at the fold's base. Features: 17 mask features (n; R, C, rmax, cmax, rimb, cimb, dist_rel: the row and column groups that share A and B tiles; G1, hlag, spread, bbox: position on the mesh; memd: distance to the memory shires; link: the hottest link under X-then-Y routing, ASSUMED; Fp, Fs, LAG: layout2's private and shared DRAM-served shares and its LAGcore) and 5 shape-context features (MB, NB, ln KB, format, clock). The slice loads reduce to n, R and C for this kernel (every tile of an op step has the same PA[10]: `scripts/f01_features.py`). MM1-v3.2's constants unchanged.

## 3. The held-out record (the declared folds; no twins unless said)

| family | MASK points | MM1-v3.2 | the reference | share of MM1-v3.2's MASK residual explained | K1 (<= 0.90 x) | CART | kNN | mask features only | shape only |
|---|---|---|---|---|---|---|---|---|---|
| LOSO | 318 | 12.25% | **5.78%** | 0.778 | PASS | 6.78% | 7.06% | 7.69% | 9.58% |
| LOEO | 869 | 9.58% | **7.73%** | 0.348 | PASS | 8.66% | 8.12% | 8.30% | 8.86% |
| LOCO | 975 | 9.48% | **5.43%** | 0.672 | PASS | 6.30% | 6.65% | 6.59% | 7.89% |
| LOMO | 722 | 10.50% | **7.36%** | 0.509 | PASS | 7.92% | 8.14% | 8.36% | 8.77% |

**The E221 footing** (blind-e221's own 363 no-twin MASK cases, held out by session): MM1-v3.2 12.41% (the check: blind-e221's 12.41%), the reference **5.63%**, share explained 0.794; CART 6.69%, kNN 6.91%, mask features only 7.48%, shape only 9.87%.

| E221 placement family (LOSO) | cases | MM1-v3.2 | the reference |
|---|---|---|---|
| PLA | 74 | 11.52% | 5.35% |
| PLA+PLX | 6 | 13.79% | 4.61% |
| PLB | 25 | 10.49% | 4.54% |
| PLC | 24 | 2.52% | 2.45% |
| PLD | 21 | 2.31% | 2.82% |
| PLE | 46 | 3.01% | 5.20% |
| PLH | 24 | 13.74% | 4.69% |
| PLK | 19 | 13.07% | 4.45% |
| PLK3 | 13 | 12.62% | 3.81% |
| PLL | 23 | 6.61% | 3.10% |
| PLM | 24 | 28.19% | 11.69% |
| PLN | 18 | 13.39% | 6.57% |
| PLX | 46 | 13.47% | 6.28% |

With twins (REPORTED): LOSO 12.05% -> 5.50% (n 392); LOEO 9.55% -> 7.47% (n 975); LOCO 9.48% -> 5.43% (n 975); LOMO 10.50% -> 7.36% (n 722).

Per card (MASK, no twin; REPORTED): LOSO: a1 card 0 12.81 -> 6.10 (n 102), a1 card 1 10.70 -> 5.20 (n 97), a2 card 0 12.93 -> 5.94 (n 119); LOEO: a1 card 0 10.46 -> 8.53 (n 242), a1 card 1 8.78 -> 7.03 (n 316), a2 card 0 10.69 -> 8.50 (n 214), a3 card 0 6.73 -> 5.75 (n 97); LOCO: a1 card 0 10.51 -> 5.65 (n 286), a1 card 1 8.73 -> 5.04 (n 362), a2 card 0 10.38 -> 5.86 (n 225), a3 card 0 6.42 -> 5.18 (n 102); LOMO: a1 card 0 11.35 -> 7.85 (n 233), a1 card 1 9.51 -> 6.96 (n 280), a2 card 0 11.52 -> 7.63 (n 173), a3 card 0 6.23 -> 5.53 (n 36).

LOEO by experiment (MASK, no twin; REPORTED): E206 6.03 -> 3.67 (n 24), E207 8.24 -> 6.65 (n 8), E209 8.30 -> 7.38 (n 10), E212 6.72 -> 6.88 (n 81), E213 5.50 -> 4.90 (n 24), E214 7.33 -> 6.32 (n 126), E215 9.31 -> 7.89 (n 27), E216 8.71 -> 9.30 (n 16), E217 8.04 -> 7.55 (n 104), E218 4.62 -> 2.71 (n 13), E220 4.73 -> 3.66 (n 50), E221 12.34 -> 9.32 (n 347), E222 6.81 -> 5.93 (n 20), E224 7.40 -> 5.98 (n 19).

## 3b. What these numbers can and cannot say

- **LOSO and LOCO include cross-card repeats.** 308 of the 308 in-scope MASK points LOSO tests have their arm, format and mask run on another card (or in another experiment) in that fold's training set: E221 ran each placement on three cards. The twin key holds the card, so they are not twins, and the transfer is real (the same placement repeats across cards), but it is not a never-run mask. **For never-run masks (E226) read LOMO** (every point at the held-out mask out of training: 10.50% -> 7.36%, share 0.51) **and E221 held out whole** (LOEO: 12.34% -> 9.32% on its 347 MASK points).
- **Part of the MASK residual is shape-level at subsets:** the shape-only control (no mask feature) reads 9.87% on E221's 363 (LOMO 8.77%); the mask features add the rest beyond it (the placebo, which keeps the shape context, reads about 9.9% on LOSO and 9.0% on LOMO).
- **Where it is worse than MM1-v3.2, held out:** LOEO E212 6.72 -> 6.88%, LOEO E216 8.71 -> 9.30%, LOMO E212 7.66 -> 8.46%, LOMO E213 5.15 -> 5.72%, E221 PLD 2.31 -> 2.82%, E221 PLE 3.01 -> 5.20%.
- **Assumed, not measured:** X-then-Y routing for `link`; the memory shires' places (the lab's notes, as layout2 placed them). The twin rule here is per fold (layout2's key against the fold's training points: LOSO 318 no-twin MASK points); blind-e221's own flags give its 363, both printed.
- **A ceiling for these features and this learner family, not a proof:** a term with other inputs (the walk's per-link or per-slice loads, a measured arbitration) could do better; a two-constant term from these features should not expect to beat the LOMO figure.

## 4. The keep rule (declared) and the verdict

- **K1** (every family, M1 <= 0.90 x MM1-v3.2's): PASS.
- **K2** (the non-MASK classes, LOEO, no twin: 5.427% -> 5.427%, limit 5.477%): PASS (the reference never moves a non-MASK point).
- **K3** (the placebo: the 17 mask features permuted within each shape, the LOSO family refitted, 100 draws): the real M1 5.78% is below the placebo's in **100 of 100** draws (placebo M1 min / 5% / median / 95% / max: 9.65 / 9.76 / 9.90 / 10.09 / 10.13): PASS. The identity draw reproduced the real fit exactly.
- REPORTED: the LOMO placebo (10 draws): real 7.36%, below the placebo in 10 of 10 (placebo min / median / max 8.95 / 9.01 / 9.08%).

**Verdict: meets the keep rule (K1, K2, K3).** Frozen either way as **'MM1-v3.2 + mask-ceiling (reference, REPORTED)'**: it never joins MM1.

## 5. The feature ranking (REPORTED)

- **Permutation importance, LOSO** (rise of the in-scope MASK M1 5.84%, n 308, when one feature is shuffled across the in-scope points; mean of 3 draws): hlag +2.26, lnKB +1.57, NB +1.24, MB +0.81, memd +0.70, link +0.60, G1 +0.55, Fs +0.29, dist_rel +0.27, R +0.25.
- **Permutation importance, LOMO** (rise of the in-scope MASK M1 7.36%, n 722, when one feature is shuffled across the in-scope points; mean of 3 draws): hlag +1.02, lnKB +0.81, NB +0.47, MB +0.35, G1 +0.27, memd +0.22, R +0.09, spread +0.09, link +0.09, dist_rel +0.05.
- **Group drop-out, LOSO** (the forest refitted without the group; M1 with it 5.78%): context (shape) 7.69% (+1.91), position 6.14% (+0.36), memory distance 6.03% (+0.25), groups 5.95% (+0.17), link 5.94% (+0.16), count 5.86% (+0.08), DRAM private/shared 5.77% (-0.01).
- **Impurity share of the all-data forest:** hlag 0.166, lnKB 0.141, G1 0.116, NB 0.091, memd 0.079, MB 0.072, link 0.059, dist_rel 0.059, spread 0.041, Fs 0.038.
- **The all-data CART (depth 4, leaf 10), its splits** (in sample, REPORTED): hlag <= 0.01573 |   G1 <= 0.07896 |     NB <= 2 |       G1 <= -0.02269 |         leaf: mean ln residual -0.0078 |       else (G1 > -0.02269) |         leaf: mean ln residual +0.0306 |     else (NB > 2) |       MB <= 2.5 |         leaf: mean ln residual -0.0885 |       else (MB > 2.5) |         leaf: mean ln residual -0.2036 |   else (G1 > 0.07896) |     lnKB <= 2.191 |       leaf: mean ln residual +0.0343 | ...

## 6. The composition with AF4 (by construction, no refit; `scripts/c01_af4.py`)

- C1 data points: 4311, in the reference scope 888, gemmLnc 89, in both 0
- C1 registered points E220/E222/E224: 355, in the reference scope 91, gemmLnc 53, in both 0
- C2 AF4 changes no op time: 326 rows, differing 0 []
- C3 AF4 equals MM1-v3.2 in every number off gemmLnc: 290 rows, differing 0 []
- C4 MM1-v3.2 energy law at t: 326 rows, failing 0 []
- composed rows 326: the reference acts at 59 (factor range 0.8930-1.0496), AF4 at 36, neither at 231
- COMPOSITION BY CONSTRUCTION: SHOWN (C1-C4 hold)

So 'MM1-v3.2 + AF4 + mask-ceiling' = AF4's row at a gemmLnc token; at an in-scope point MM1-v3.2's row with its op time times the reference's factor and W over idle by MM1-v3.2's own law at the new time (A_W + B_W_us / T_op_us); MM1-v3.2 elsewhere. The composed rows at E222's and E224's registered points are in `composed-af4-REPORTED.json` (not blind: those days are in the training set).

## 7. How to call it on new points (and with AF4)

`python3 -I -B mask_ceiling.py --points points.json --out factors.json` with points.json a list of {arm, kernel, fmt, mask, f}: the factor (1 off the scope). The forecast is MM1-v3.2's own row (tools/matmul/mm1/v3.2/mm1_v32.py, Model at out/mm1_v32_params.json) with T_op_us, cycles_per_op_wall and seconds_per_gemm times the factor; with AF4 take AF4's row at a gemmLnc token (the factor is 1 there). `python3 -I -B mask_ceiling.py --selftest` re-makes 20 training configurations' features from code and checks the frozen fit. To re-run the pipeline set MASK_CEILING_LANE to a folder holding work/lab (the lab's top) and the work/ inputs (SCRUB.json: the only change from the code as run).

## 8. Files

`DECLARED-mask-ceiling.md` (+ .sha256); `params-mask-ceiling.json` (the all-data forest, its training ids and targets); `fits-mask-ceiling.json` (every fold's summary, the in-sample fit); `holdout-mask-ceiling.json` and `holdout-points-mask-ceiling.csv` (the held-out record, every test point of every fold, every learner); `placebo-mask-ceiling.json`; `composed-af4-REPORTED.json`; `verdict-mask-ceiling.json`; `inputs/` (the points, features, base checks, E224 arm B's reduction); `scripts/` (as run but for SCRUB.json's path lookups); `logs/`; `SHA256SUMS`.

SPDX-License-Identifier: Apache-2.0
