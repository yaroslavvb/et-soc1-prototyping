# 'MM1-v3.2 + posimb-mask': posimb's layout term refitted on the mask data through E224, with one alignment constant (a v3.4 candidate)

*Round Q238, lane mask-posimb (track P), Sat 21 Nov 2026 (week 47), Pacific time, at aifoundry2's desk. Desk only: no card, no simulator, no
E226 file. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP / OPENBLAS / MKL /
NUMEXPR_NUM_THREADS = 1), every job in the round's CPU slots, one at a time.*

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus
on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles.
From based on what I know about the size of a matrix and which operations are contained."

**Labels.** *Post hoc*: every constant here, and the form's third feature (chosen after in-sample looks at MM1-v3.2's residuals, disclosed in
`DECLARED-posimb-mask.md` section 0). *Held out*: left out of the fit that scores it (not blind). *Blind*: none here; the next blind day
(E226) is the first blind test. *REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: not run. Errors: forecast / measured - 1 (%).

## 1. The lead

The lab's blind test of E221 (`../../v3.1/blind-e221-scores/`, 5eb23fd4): 152 of MM1-v3.2's 175 T1 misses are core-group mask placements; the
MASK class reads **12.41%** wall rms on its 363 no-twin cases (every other class at most 9.05%). Q234's frozen posimb (`../../v3.3-cands/posimb/`)
read 12.14% there (REPORTED) and was NOT DECIDED in E222.

**What separates the masks (post hoc, in sample, before the declaration: `scripts/x02`, `x04`, `x05`).** The kernel groups shires by row group
s >> 2 (A tiles shared within it) and column group s & 3 (B tiles shared within it). At one shire, MM1-v3.2 is right where (s >> 2) & 3 equals
s & 3 (shires 0, 5, 10, 15, 16, 21, 26, 31: mean residual +1.15%, n 79) and forecasts the other 24 shires about 12% too slow (mean -11.73%,
n 126); at gemmL2x6x10 the error is -8% to +3% at the first set and +9% to +20% at the others. Over the 936 multi-tile subset points, masks
that hold none of those shires (A1 = 1) read -10.8% (n 216) against +1.3% for the rest (n 720). MM1-v3.2's own subset data (E206-E215) held
one of those shires at 323 of its 331 multi-tile points, so it learned their speed. This is posimb's unexplained gemmL2x6x10 pair 0x44 against
0x22 (0.21 ln). posimb's features cannot see it (G1core is a mesh-latency mean; LAGcore is 0 at one shire).

## 2. The form (declared before any fit: `DECLARED-posimb-mask.md`, sha256 `b59f1c4dc5ff1b67483face805216585cfca94b2fe709700c458ff2ca4714f40`, hashed 2026-11-21 01:31:42 PST)

At the subset points of rgm136's gemmL loop (every other point keeps MM1-v3.2's forecast to the last bit):

- wall: **T = T_v32 x clip(1 + a_hop e G1core + a_lag e LAGcore + a_al e A1, 0.3, 3.0)**
- the counter's mean: MM1-v3.2's mean x clip(1 + a_hop e G1core + a_al e A1, 0.3, 3.0)
- energy: MM1-v3.2's W over idle A_W + B_W / t at the term's op time t (posimb's composition)

G1core and LAGcore are posimb's features, unchanged: the active shires' mean L3 latency on the mesh over the full chip's, minus 1; the slowest
active shire's latency excess times the private share of the DRAM-served stream. **A1 = 1 when no active shire s has (s >> 2) & 3 == s & 3,
else 0** (0 at the full chip). e is MM1-v3.2's elasticity of its op time to its memory constants (0 at the 1x1x1 cells, 0.97-1.00 at every
other in-scope point). Three constants (two-stage: MM1-v3.2's constants unchanged). The reason for the third, stated before the fit, is
section 1. A reading, **not established**: a shire with R = C mod 4 has its A and B tile streams at equal offsets modulo 32 KT tiles in the walk,
so the two streams might compete for the same cache sets or DRAM banks; the wall is the slowest active shire's.

## 3. The fit (post hoc, `scripts/g01_fit.py`, `out/fit_results.json`)

Data: every committed matmul time point through E224, **4311 points** (`out/points_all.json`): MM1-v3.2's 2508 (E105-E215 with E214), E216 46,
E217 486, E218 52, E219 139, E220 156 (arm A 84; arm B 72 at route c), E221 733 cases, E222 70, E224 121. Every run whose check of C is
missing or not exact/approx is dropped first (E218 f04's run 77; E224's p3a and p3b on both arms, every run wrong, so those points are out).
E224 arm B was reduced here by E208's registered reducer (`reduce_mms.py` b9e32618) on its committed session. E146's 87 store rungs are out.

**All-data constants: a_hop = 0.4117, a_lag = 0.3349, a_al = -0.1047** (the expected signs). Across every held-out fold the constants stay
put: LOEO a_al from -0.108 to -0.079, a_hop from 0.36 to 0.42, a_lag from 0.26 to 0.42; LOMO (115 folds) a_al from -0.107 to -0.097.

## 4. The held-out record, against MM1-v3.2

| the declared rule | MM1-v3.2 | + posimb-mask | threshold | verdict |
|---|---|---|---|---|
| K1: E221's 363 MASK no-twin cases, wall rms, LOSO (one E221 session out at a time) | 12.409% | **8.126%** | <= 11.409% (a 1.00-point margin) | PASS |
| K1L: the same 363 cases, LOMO (every point at the mask held out, 115 masks) | 12.409% | **8.122%** | <= 11.909% | PASS |
| K2: non-MASK points, LOEO, no twins (n 2326) | 5.4196% | 5.4196% | <= 5.4696% | PASS |
| K4: MASK points outside E221, LOEO, no twins (n 571) | 7.068% | 6.834% | <= 7.118% | PASS |
| K3: placebo (the three features permuted within each arm), M1 | - | beaten in 100 of 100 (placebo 11.56-12.08%) | >= 95 | PASS |

**Verdict: KEPT by its declared rule.** K2 holds by construction: the term moves no non-MASK point (e = 0 at the in-scope 1x1x1 cells). A
self-check by separate code (`scripts/c01_check.py`) re-made M1, M1L, M2 and M4 to the last digit and the constants to 7.2e-16.

REPORTED beside (never deciding), the same folds and procedure:

| model | M1 LOSO | M1L LOMO | M4 | MASK LOEO no twin (n 918) | MASK LOMO no twin (n 704) | MASK LOCO no twin |
|---|---|---|---|---|---|---|
| MM1-v3.2 | 12.41% | 12.41% | 7.07% | 9.41% | 10.14% | 9.33% |
| **+ posimb-mask** (3 constants) | **8.13%** | **8.12%** | **6.83%** | **7.45%** | **7.59%** | **7.24%** |
| posimb's form refitted, its two constants only (a_hop 0.925, a_lag 0.037) | 11.11% | 11.25% | 7.17% | 9.18% | 9.51% | 8.69% |
| the alignment term alone (a_al -0.113) | 8.24% | 8.22% | 7.08% | 7.82% | 7.74% | 7.41% |
| the frozen posimb (a_hop 0.1333, a_lag 0.4367, no fit) | 12.14% | 12.14% | 6.96% | 9.22% | 9.94% | 9.15% |

posimb's form refitted alone would fail this lane's K4 (7.17% against 7.12%): refitted on the new masks, it moves its hop constant to 0.93 and
gets worse on the other experiments' masks. Its placebo is beaten 100 of 100 (11.11% against 12.07-12.43%).

**LOEO by experiment, MASK points without twins** (MM1-v3.2 -> + posimb-mask): **E206 6.03 -> 6.35 (n 24)**; **E207 8.24 -> 8.53 (8)**; E208
4.57 -> 3.15 (7); E209 8.15 -> 7.64 (11); E212 6.43 -> 6.15 (n 114); E213 5.50 -> 4.80 (24); E214 7.33 ->
6.96 (132); **E215 9.15 -> 9.20 (28)**; **E216 8.71 -> 9.09 (16)**; E217 8.04 -> 7.54 (104); E218 4.62 -> 4.30 (13); E220 4.73 -> 4.56 (50);
E221 12.34 -> 8.37 (347); **E222 6.81 -> 7.85 (20)**; E224 7.46 -> 7.19 (20). **LOCO, MASK points without twins:** aifoundry1 card 0 10.38 ->
7.71; aifoundry1 card 1 8.51 -> 6.83; aifoundry2 card 0 10.26 -> 7.50; **aifoundry3 card 0 6.50 -> 6.79**. **LOSO by E221 session, MASK
without twins:** eight of nine improve (10.4-16.0% -> 5.1-10.6%); **a2c0-S2 2.92 -> 7.94%** (its 16 MASK cases are gemmL1x16x6 and gemmL4x1x10,
section 5). LOLO (MASK no twin): compact 6.37 -> 6.44, spread 9.25 -> 8.18, other 11.50 -> 7.60. posimb's lead pairs on its LO-Y fold
(E216 + E218 out): 0.0469 -> 0.0321 ln (the frozen posimb 0.0337). The counter's mean at E221's 363 (REPORTED, `out/` g02): MM1-v3.2 12.36% ->
8.98% held out.

## 5. What its features miss (`out/fit_results.json` > what_the_features_miss_LOMO; the candidate's LOMO residuals at the 758 subset MASK points)

- **The alignment effect's size depends on the shape; one constant carries its mean.** MM1-v3.2's offset between A1 = 1 and A1 = 0 masks
  (before the fit, `scripts/x05`, its A2 reading, equal to A1 at 935 of 936 points) is about -25% at gemmL3x4x6, -20% at gemmL2x6x10, -16% at gemmL1x12x8, -14% at gemmL1x8x11, but about 0 at
  gemmL4x1x10, gemmL2x1x16, gemmL1x8x24, and -3% to -4% at gemmL1x16x6, gemmL2x4x24, gemmL1x3x4, gemmL4x6x2. So the term **over-corrects**
  where the effect is absent: by shape (LOMO bias, MM1-v3.2 -> term) gemmL4x1x10 -1.4 -> **-7.0%**, gemmL2x1x16 -1.5 -> **-5.4%**,
  gemmL1x16x6 +0.2 -> **-5.4%**, gemmL2x4x24 +0.8 -> **-4.8%**; E222's six A1 points (q01b, q03a, q03b, q04a, q04b, q05b: gemmL1x8x8,
  1x4x16, 1x4x23, 1x8x24 at two shires outside the set) go from -3.3..+13.6% to -16.3..-1.7% (LOEO). It **under-corrects** where the effect is large: gemmL3x4x6 +17.7 -> +12.6% (15.7% rms), gemmL4x6x2 +13.8 ->
  +7.2%. A form that says which shapes lose speed at an aligned shire needs the panels' address bases and the caches' set mapping, which this
  lane does not have (NOT RUN).
- **By shire count:** one shire 12.99% (+7.6) -> **6.97% (-0.3)**, n 205; two shires 11.21 -> 7.89%, n 190; four 6.72 -> 6.82%; 8-15 8.14 ->
  8.12%; 16-23 7.30 -> 7.28%; **24-31 9.32 -> 9.39% (-3.8% bias: forecast too fast)**, n 75.
- **By row and column groups** (R active row groups, C active column groups): R1 C1 12.99 -> 6.97%; R2 C1 12.78 -> 8.64%; R1 C2 7.61 -> 6.31%;
  **R8 C3 10.42 -> 10.49% (-6.8%)**, R8 C1 8.40 -> 7.89% (-5.4%), R6 C4 8.52 -> 8.58% (-3.7%), R8 C4 10.60 -> 10.79% (+7.6%). Column sets
  missing one or two groups at every row are forecast too fast: cols 013 -8.7%, cols 023 -12.7%, cols 123 -11.3%, cols 13 -10.9% (n 3-6
  each). The worst masks after the term are of that kind: 0x99999999 -13.5%, 0xdddddddd -12.6%, 0xeeeeeeee -11.3%, 0xaaaaaaaa -10.9%,
  0xbbbbbbbb -9.6% (16-24 shires; the B panel shared within fewer column groups), and 0xb7b2effb +16.9%, 0x46950281 -14.2%.
- **By spread** (`fit_v31.lolo_class`): compact 6.76 -> 6.92% (+1.0), other 11.77 -> 7.02%, spread 10.38 -> 8.50% (-1.6).
- **Single shires after the term:** bias within about +-5% at most shires (n 3-6 each); shires 14 and 17 (E221's 32 cases each, several shapes)
  10.4% and 10.1% rms; shire 10 (n 34) 6.2%; shire 0 (n 24) 3.95%.
- **Where it hurts:** E222 (aifoundry3 card 0) 6.81 -> 7.85%, E216 8.71 -> 9.09%, aifoundry3 card 0 by LOCO 6.50 -> 6.79%, E221's a2c0-S2
  (above): all from the shape dependence or from E216's and E222's equal-count pairs, where posimb's refitted hop constant (0.41 against the
  frozen 0.13) moves both members.

## 6. How to call it

`posimb_mask.py` (the predictor, frozen with `params-posimb-mask.json`; it needs this repository's `tools/matmul/mm1/v3.2`, `v3.1`, `v3`,
`v3.2-terms/layout/controls-e215/v01_map.py` and, for AF4, `v3.3-cands/gemmlnc-af4/`):

    import sys; sys.path.insert(0, 'tools/matmul/mm1/v3.4-cands/posimb-mask')
    import posimb_mask
    M = posimb_mask.Model()
    rows = M.predict_many([{'card': 'aifoundry1 card 1', 'arm': 'gemmL2x6x10', 'fmt': 'fp32', 'kind': 'zeros', 'mask': '0x4000', 'f': 600.0,
                            'kernel': 'rgm136'}])
    rows[0]['MM1-v3.2 + posimb-mask']        # T_op_us, cycles_per_op_wall, cycles_per_op_mean, seconds_per_gemm, W_over_idle, A_W, B_W_us, J...
    rows[0]['term']                          # e, Phi_hop, Phi_lag, Phi_al, g_wall, g_mean, G1core, LAGcore, A1, Fp, Fs, Lmean_act, Lmax_act
    M.predict_many_with_af4([...])[0]['MM1-v3.2 + AF4 + posimb-mask']

A configuration not in `out/private_shared.json` is made by the walk on the call (seconds for most shapes). **With AF4, by construction, no
refit:** the term acts only at rgm136 gemmL subset points, AF4 only at gemmLnc points (energy), so a composed row is the one that acts (the
module exits 5 if both act at a row, or if a term moved a row outside its scope). Shown on E222's 73 and E224's 253 registered rows (arm A at
600 MHz; arm B at 799, 700 and 600 MHz): `forecasts-compose-e222-e224.json` and `.csv` (POST HOC: those points' data are in the fit; REPORTED).
The term acts alone at 62 rows and AF4 alone at 36; neither acts at 228. The module's MM1-v3.2 and 'MM1-v3.2 + AF4' equal E222's and E224's
registered frozen forecasts to 4.3e-12 at every row. At E224's 16 family-P pattern rows MM1-v3.2 prices no energy (no switch count passed), so
those rows are time only.

## 7. Gaps, and what was NOT RUN

- Two-stage only: MM1-v3.2's 19 time constants were not refitted with the term (a joint refit: NOT RUN).
- The physical reading of A1 (aligned A and B streams sharing sets or banks) is not established: no address bases, set or bank mapping read.
- The shape dependence of the alignment effect (section 5) is not modelled.
- The LOMO and LOEO bases for E212, E214 and E215 points are MM1-v3.2's all-data or stored fold constants, which saw some of those masks
  (MM1-v3.2 has no mask-specific constant). E221's 363 headline cases are clean: MM1-v3.2 never saw E221.
- E221's twelve multi-session cases take the mean of their LOSO folds' predictions; E221's cases carry the case's mean clock.
- E220 arm B's xg01t and xg10t and E224 arm B's d06 and d17 read only off route c (route m) and are left out.
- The check-of-C scan reads the reducer forms of E206-E224; E210's and E211's data files are in other forms and were not scanned (their
  points enter as MM1-v3.2's own).
- No independent verifier of this lane: NOT RUN here (the round's check and verify lanes are the check).

## 8. Files

- `DECLARED-posimb-mask.md` (+ `.sha256`): the declaration, hashed before any fit.
- `posimb_mask.py`, `params-posimb-mask.json`: the predictor and its constants.
- `out/points_all.json` (every time point through E224 in MM1-v3.2's form), `out/private_shared.json` (posimb's features at 458
  configurations, made fresh here by its landed `f02_private.py`), `out/base_meta.json` (MM1-v3.2's base re-made: 0 difference from its stored
  predictions at the all-data and 27 fold constants), `out/fit_results.json` (the declared fit, folds, rule, placebo, REPORTED tables and
  what the features miss), `out/heldout_points.csv` (every point's held-out op time in every fold family, MM1-v3.2, the term and the
  two-constant refit), `out/check_c01.json` (the separate-code self-check), `out/g02_mean.json` (the counter's mean).
- `forecasts-compose-e222-e224.json`, `.csv`: the AF4 composition, post hoc.
- `scripts/`: the lane's scripts as run (absolute paths replaced by environment lookups in the shell scripts: `SCRUB.json`), and `logs/`.
  Re-run from a lab checkout at GitHub main cfd7e641 with `MASKPOS_LANE` naming a folder whose `work/lab` is that checkout.
- `SHA256SUMS`.

SPDX-License-Identifier: Apache-2.0
