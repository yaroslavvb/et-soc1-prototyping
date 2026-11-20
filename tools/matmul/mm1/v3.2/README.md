# MM1-v3.2: the matmul model refitted on every committed matmul point through E215 and E214, with the gemmLnc energy term F3 and no layout term (its declared rule chose none), fitted exactly by its declaration

*Written Thu 19 Nov 2026 (week 47), Pacific time, by lane fit-v32 (round Q230) at aifoundry2's desk; E218's draw and forecasts, this README and the land re-made by lane fix-fit-v32 (the same round) after verify-fit-v32's findings, nothing in MM1-v3.2 changed. Desk only: no card, no simulator. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`, single-threaded (OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = NUMEXPR_NUM_THREADS = 1), every fit inside the round's CPU slots, one slot job at a time.*

The owner's words that started the matmul model (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well the timing simulation for the matte mold matches reality and the energy." The checkpoint's step 5: fix what the blind day names, then test the fix in one card session (E218, section 7).

**Labels.** *Registered*: declared in `DECLARED-v32.md` before any fit. *Post hoc*: every constant here (fitted after its data existed). *Held out*: left out of the fit that scores it (not blind). *Blind*: scored on data that did not exist when the forecast was frozen. *REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: a check that did not run. Error = forecast / measured - 1; rms and bias in %.

## 0. On one screen

| item | declared (DECLARED-v32.md) | decided here | by |
|---|---|---|---|
| time | T5r+G0+n32 refitted, no v3.1 item reopened | T5r+G0+n32 at its refitted constants (19 free) | fixed (section 1.1) |
| layout term | at most one of N3, N1+N2, G1, G1+N1, F1, fresh24 | **none** (rule winner: none) | `layout_rule_v32.py` (section 3) |
| energy | E1t + F3 (c1, c2 in [0, 10,000] pJ) | E1t + F3: c1 = 247.7 pJ, c2 = 448.6 pJ (all data) | fixed; F3's pin rule |
| data | MM1-v3.1's points + E214 + E215 | 2508 time, 2443 energy points (2443 priced) | section 4 |
| acceptance | rules 1-3, 4(a)-4(d), 5 against MM1-v3 refitted | **NOT ACCEPTED: rule 4c fails** | section 7 |
| E218 | about 54 points on aifoundry3 card 0 | 54 points: {'F': 14, 'G': 12, 'Gt': 12, 'Y': 16} | section 9's point rule |

**Held out, without twins, MM1-v3.2 against MM1-v3 refitted on the same points and folds:**

| quantity | MM1-v3.2 | MM1-v3 refitted |
|---|---|---|
| LOEO wall cycles (n 1769) | 5.295% | 5.295% |
| LOEO W over idle given t (>= 3 W) | 4.976% | 5.680% |
| LOEO J over idle with t forecast | 5.770% | 6.412% |
| LOEO J at rest given t | 1.620% | 2.088% |
| LOCO wall cycles (every point) | 4.698% | 4.698% |
| LOCO W over idle given t (fallback route) | 9.292% | 9.943% |
| LOEO W over idle given t at the gemmLnc points (n 14) | 8.429% | 30.459% |

## 1. The data (section 4)

- GitHub main at the fit's start: `7edf3477e4ca1ffc805ac91bf4c9f99652d091e7` (2026-11-19 15:51:20 -0800); the gate: **OPEN** (3 E215 scores files on main: `docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/scores-e215-B.json` 4cd7b8643f; `docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/scores-e215-pooled.json` 7edf3477e4; `docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/scores-e215-A.json` 7cddc40617).
- Time points by experiment: {'E105': 73, 'E107': 224, 'E119': 63, 'E126': 46, 'E136': 36, 'E146': 108, 'E158': 102, 'E159': 13, 'E168': 14, 'E169': 54, 'E190': 36, 'E206': 232, 'E207': 53, 'E208': 184, 'E209': 46, 'E211': 26, 'E212': 478, 'E213': 118, 'E214': 518, 'E215': 84}.
- Energy points by experiment: {'E105': 45, 'E107': 179, 'E119': 63, 'E126': 46, 'E136': 24, 'E146': 108, 'E158': 102, 'E159': 13, 'E168': 12, 'E169': 54, 'E190': 36, 'E206': 232, 'E207': 53, 'E208': 173, 'E209': 43, 'E210': 22, 'E211': 26, 'E212': 473, 'E213': 128, 'E214': 515, 'E215': 96}; not priced: 0.
- Frozen inputs: 46 files equal to the declaration's sha256; 133 vendored inputs of MM1-v3 and MM1-v3.1 equal to their SOURCES.tsv; counts SHA256SUMS `c74c2d49c336159f...` and counts-e214 `4c39d0d3cf4ad405...` (`sha256sum -c` rc 0 / 0).
- E214 (seven sessions, the model session's third sweep), vendored under `inputs/e214/`:

| session | sha256 | data commit | ancestor of the fit's main |
|---|---|---|---|
| a1c0-S1 | `10bf37ac692097be692000c36ab6c49eedc8e11298eef915e7f761fe09094442` | 3b3e4182d7 | True |
| a1c0-S2 | `1d85c3f84e5216b5ccf64b1ec6d37b00b071770b342d8949025a62e282ddfb2e` | 317ce38cf7 | True |
| a1c0-S3 | `e22515115a4f712cf08a3b9a1940c5244473d7bf1db93f2aa58f8fb1f8d094ea` | 117ca63753 | True |
| a1c1-S1 | `e292c5b24adf311326cd207824a93c13f951851570c8590063f0436649300ea6` | f7f3257c2c | True |
| a1c1-S2 | `4220077f668729bd97a772f6bdb84f1f5e2ccbd0169570356305894804d63128` | a457d7fcaa | True |
| a1c1-S3 | `8fbb1d36a95f80aee92a74ac5d14330b49610a9f8e7b524b087fd814c9d710b0` | 9ac3c33873 | True |
| a1c1-S4 | `a7691bd90b934ca5a4b4fa993fd5d13a5b94bba17ee5e5cc182934f855155848` | 0e95201d39 | True |

- E215 (MM1-v3.1's blind day), vendored under `inputs/e215/` after the gate, each checked by `git hash-object` against the declared blob id:

| arm | git hash-object = declared blob | sha256 | data commit | kept runs | set aside | the two record readings keep the same runs |
|---|---|---|---|---|---|---|
| A | True (`d88420610ecb`) | `651e954328c700205df64c497698621315870ad47d9223a25424e3df842ce763` | 8355db1587 | 119 | 0 | True |
| B | True (`f6cc1cff2314`) | `b4c6bdb54b079565959a13df82e8ba13e32f988beee700540d25614eb44780c9` | 4f648f24b9 | 71 | 0 | True |

## 2. Time (sections 1.1, 2, 5)

MM1-v3.1's chosen form T5r+G0+n32 (`../v3.1/time_v31.py`, unchanged) refitted by `../v3.1/fit_v31.py` `fit_time` and `run_time` unchanged (18 starts, phase 2, the tie rule) with v3.1's pin rule plus the eta pin; 41 folds and the all-data fit. eta was pinned at 0 in: ['LOLO compact'].

| fold | n | MM1-v3.2 rms (bias) | without twins | twins | winner start | pins |
|---|---|---|---|---|---|---|
| LEAVE rgm211 out | 29 | 5.723 (-1.052) | 5.723 | 0 | S11 | - |
| LOCO aifoundry1 card 0 | 359 | 5.646 (0.274) | 5.646 | 0 | S10 | - |
| LOCO aifoundry1 card 1 | 766 | 4.716 (-0.148) | 4.716 | 0 | S9 | - |
| LOCO aifoundry2 card 0 | 778 | 4.615 (-1.030) | 4.615 | 0 | S0 | - |
| LOCO aifoundry3 card 0 | 605 | 4.128 (-0.216) | 4.128 | 0 | S8 | - |
| LOEO E105 | 73 | 2.422 (-1.795) | 2.005 | 57 | S10 | - |
| LOEO E107 | 224 | 2.890 (0.068) | 1.965 | 99 | S10 | - |
| LOEO E119 | 63 | 2.525 (-1.432) | 2.506 | 12 | S10 | - |
| LOEO E126 | 46 | 3.347 (1.452) | 3.516 | 6 | S10 | - |
| LOEO E136 | 36 | 2.011 (-1.900) | 2.379 | 18 | S10 | - |
| LOEO E146 | 108 | 4.851 (0.406) | 5.644 | 46 | S10 | - |
| LOEO E158 | 102 | 4.482 (-0.690) | 4.224 | 26 | S7 | - |
| LOEO E159 | 13 | 6.183 (-2.408) | 6.107 | 2 | S10 | - |
| LOEO E168 | 14 | 1.107 (-0.262) | 1.107 | 0 | S10 | - |
| LOEO E169 | 54 | 7.736 (-1.602) | 7.841 | 7 | S10 | - |
| LOEO E190 | 36 | 5.467 (3.914) | 5.844 | 18 | S10 | - |
| LOEO E206 | 232 | 4.176 (0.476) | 4.415 | 68 | S2 | - |
| LOEO E207 | 53 | 4.462 (0.822) | 4.568 | 3 | S10 | - |
| LOEO E208 | 184 | 3.413 (-1.064) | 3.809 | 109 | S10 | - |
| LOEO E209 | 46 | 5.314 (-0.824) | 5.436 | 6 | S10 | - |
| LOEO E211 | 26 | 6.406 (-0.275) | 7.165 | 7 | S11 | - |
| LOEO E212 | 478 | 4.619 (-1.029) | 5.256 | 146 | S7 | - |
| LOEO E212 a1c0 | 100 | 4.913 (-1.076) | 5.547 | 24 | S10 | - |
| LOEO E212 a1c1 | 203 | 4.227 (-1.174) | 4.941 | 73 | S0 | - |
| LOEO E212 a2c0 | 175 | 4.683 (-0.549) | 5.162 | 49 | S8 | - |
| LOEO E213 | 118 | 4.212 (-1.188) | 4.354 | 10 | S7 | - |
| LOEO E213 A | 86 | 4.534 (-1.758) | 4.608 | 3 | S7 | - |
| LOEO E213 B | 32 | 3.206 (0.343) | 3.393 | 7 | S8 | - |
| LOEO E214 | 518 | 5.933 (0.481) | 6.493 | 93 | S8 | - |
| LOEO E214 a1c0 | 221 | 6.349 (0.960) | 6.652 | 20 | S10 | - |
| LOEO E214 a1c1 | 297 | 5.391 (-0.006) | 6.095 | 73 | S10 | - |
| LOEO E215 | 84 | 7.134 (1.271) | 7.381 | 6 | S0 | - |
| LOEO E215 A | 55 | 6.918 (1.074) | 7.087 | 3 | S2 | - |
| LOEO E215 B | 29 | 6.429 (0.179) | 6.773 | 3 | S11 | - |
| LOKO gemmLnc | 14 | 6.696 (2.837) | 6.696 | 0 | S10 | - |
| LOKO rgm211 gemmL | 5 | 3.451 (-0.315) | 3.451 | 0 | S10 | - |
| LOKO rgm211 gemmLn | 24 | 6.091 (-1.200) | 6.091 | 0 | S11 | - |
| LOKO run_gemm | 426 | 2.878 (-0.226) | 2.878 | 0 | S10 | - |
| LOLO compact | 227 | 5.650 (0.459) | 5.650 | 0 | S10 | eta |
| LOLO other | 73 | 7.302 (-0.638) | 7.302 | 0 | S10 | - |
| LOLO spread | 107 | 7.446 (-1.151) | 7.446 | 0 | S13 | - |

## 3. The layout term (section 3, `layout_rule_v32.py`)

Features by verify-lay's `v01_map.py` functions at every subset configuration of rgm136 gemmL in the data (407 subset points; sources {'committed v01_map.json': 279, 'made here (cache)': 128}); F1's check against lay-contention's frozen Phi_fresh: 188 configurations, worst |difference| 9.22e-10, 0 failing.

| candidate | LOEO no twin | LOLO | LOCO by card | all-data constants | eligible | conditions |
|---|---|---|---|---|---|---|
| F1 | 5.2962 | 6.4697 | aifoundry1 card 0 6.76, aifoundry1 card 1 6.17, aifoundry2 card 0 5.89, aifoundry3 card 0 6.74 | ['-0.0281359'] | False | {'i_margin': False, 'ii_bootstrap': False, 'iii_loeo_guard': True, 'iv_cards': False, 'v_l3_conventions': False} |
| G1 | 5.2628 | 6.4194 | aifoundry1 card 0 6.67, aifoundry1 card 1 6.07, aifoundry2 card 0 5.62, aifoundry3 card 0 6.72 | ['0.357794'] | False | {'i_margin': False, 'ii_bootstrap': False, 'iii_loeo_guard': True, 'iv_cards': True} |
| G1+N1 | 5.2500 | 6.3568 | aifoundry1 card 0 6.59, aifoundry1 card 1 5.99, aifoundry2 card 0 5.55, aifoundry3 card 0 6.69 | ['0.617235', '-0.018035'] | False | {'i_margin': False, 'ii_bootstrap': True, 'iii_loeo_guard': True, 'iv_cards': True} |
| N1+N2 | 5.2947 | 6.4622 | aifoundry1 card 0 6.78, aifoundry1 card 1 6.18, aifoundry2 card 0 5.79, aifoundry3 card 0 6.52 | ['-0.0489046', '0.062925'] | False | {'i_margin': False, 'ii_bootstrap': False, 'iii_loeo_guard': True, 'iv_cards': True} |
| N3 | 5.2750 | 6.4642 | aifoundry1 card 0 6.71, aifoundry1 card 1 6.13, aifoundry2 card 0 5.70, aifoundry3 card 0 6.65 | ['0.000922819'] | False | {'i_margin': False, 'ii_bootstrap': False, 'iii_loeo_guard': True, 'iv_cards': True} |
| fresh24 | 5.2907 | 6.4428 | aifoundry1 card 0 6.70, aifoundry1 card 1 6.16, aifoundry2 card 0 5.80, aifoundry3 card 0 6.75 | ['-0.0689798'] | False | {'i_margin': False, 'ii_bootstrap': False, 'iii_loeo_guard': True, 'iv_cards': True, 'v_l3_conventions': False} |
| none | 5.2950 | 6.4764 | aifoundry1 card 0 6.74, aifoundry1 card 1 6.19, aifoundry2 card 0 5.88, aifoundry3 card 0 6.68 | [] | - | - |

Rule winner: **none**; the selection placebo: NOT RUN (no rule winner); **enters: none**.

## 4. Energy (sections 1.2-1.4)

E1t (`../v3.1/energy_v31.py`, unchanged) plus F3 (`energy_v32.py`), fitted by `fit_v32.fit_energy` (v3.1's procedure line for line: nine starts, the linear solve with c1 and c2 among the linear constants, clipped into [0, 10,000] pJ, least squares at 1e-12); MM1-v3 refitted's E1u by `fit_v31.fit_energy` unchanged; each energy fold on its own time fold.

| fold | MM1-v3.2 W given t (>= 3 W) | MM1-v3 refitted | c1 (pJ) | c2 (pJ) | F3 pins |
|---|---|---|---|---|---|
| LEAVE rgm211 out | 2.924 | 3.115 | 247.7 | 448.1 | c1 and c2 free |
| LOCO aifoundry1 card 0 | 5.999 | 5.990 | 248.0 | 450.9 | c1 and c2 free |
| LOCO aifoundry1 card 1 | 7.110 | 11.201 | 218.1 | 418.0 | c1 and c2 free |
| LOCO aifoundry2 card 0 | 9.694 | 9.522 | 250.7 | 445.8 | c1 and c2 free |
| LOCO aifoundry3 card 0 | 12.458 | 10.853 | 304.2 | 615.0 | c1 and c2 free |
| LOEO E105 | 4.855 | 4.668 | 248.0 | 448.2 | c1 and c2 free |
| LOEO E107 | 5.053 | 5.767 | 248.6 | 449.3 | c1 and c2 free |
| LOEO E119 | 3.858 | 3.675 | 248.4 | 447.4 | c1 and c2 free |
| LOEO E126 | 4.646 | 4.622 | 248.1 | 448.5 | c1 and c2 free |
| LOEO E136 | 4.715 | 4.613 | 247.9 | 448.4 | c1 and c2 free |
| LOEO E146 | 4.729 | 4.702 | 247.7 | 448.7 | c1 and c2 free |
| LOEO E158 | 4.585 | 4.456 | 247.4 | 447.4 | c1 and c2 free |
| LOEO E159 | 3.899 | 3.881 | 247.8 | 448.8 | c1 and c2 free |
| LOEO E168 | 5.364 | 5.322 | 247.6 | 449.0 | c1 and c2 free |
| LOEO E169 | 3.342 | 3.419 | 247.8 | 448.2 | c1 and c2 free |
| LOEO E190 | 7.863 | 7.931 | 247.4 | 449.2 | c1 and c2 free |
| LOEO E206 | 4.833 | 4.740 | 249.1 | 448.7 | c1 and c2 free |
| LOEO E207 | 4.693 | 4.788 | 247.3 | 447.4 | c1 and c2 free |
| LOEO E208 | 3.976 | 3.850 | 247.8 | 448.5 | c1 and c2 free |
| LOEO E209 | 3.080 | 3.017 | 247.8 | 448.2 | c1 and c2 free |
| LOEO E210 | 4.516 | 4.179 | 248.9 | 450.3 | c1 and c2 free |
| LOEO E211 | 3.933 | 7.238 | 248.2 | 441.5 | c1 and c2 free |
| LOEO E212 | 4.916 | 4.890 | 246.7 | 447.6 | c1 and c2 free |
| LOEO E212 a1c0 | 4.332 | 4.255 | 247.8 | 449.1 | c1 and c2 free |
| LOEO E212 a1c1 | 5.495 | 5.517 | 246.4 | 448.5 | c1 and c2 free |
| LOEO E212 a2c0 | 4.772 | 4.748 | 247.9 | 445.7 | c1 and c2 free |
| LOEO E213 | 4.297 | 9.871 | 206.0 | 442.3 | c1 and c2 free |
| LOEO E213 A | 4.092 | 9.457 | 269.6 | 431.0 | c1 and c2 free |
| LOEO E213 B | 4.509 | 10.456 | 220.3 | 442.7 | c1 and c2 free |
| LOEO E214 | 5.369 | 5.506 | 245.7 | 450.1 | c1 and c2 free |
| LOEO E214 a1c0 | 4.874 | 4.874 | 247.8 | 450.0 | c1 and c2 free |
| LOEO E214 a1c1 | 5.794 | 5.983 | 246.0 | 450.5 | c1 and c2 free |
| LOEO E215 | 5.331 | 7.746 | 253.1 | 483.4 | c1 and c2 free |
| LOEO E215 A | 5.873 | 7.799 | 252.5 | 506.6 | c1 and c2 free |
| LOEO E215 B | 4.239 | 7.577 | 248.3 | 425.6 | c1 and c2 free |
| LOKO gemmLnc | 30.725 | 30.817 | 0.0 | 0.0 | no training gemmLnc point: c1 and c2 pinned 0 |
| LOKO rgm211 gemmL | 3.247 | 3.290 | 247.7 | 448.7 | c1 and c2 free |
| LOKO rgm211 gemmLn | 2.845 | 3.063 | 247.7 | 448.1 | c1 and c2 free |
| LOKO run_gemm | 5.307 | 6.541 | 253.7 | 445.1 | c1 and c2 free |
| LOLO compact | 6.947 | 7.144 | 244.3 | 450.6 | c1 and c2 free |
| LOLO other | 7.328 | 7.402 | 247.1 | 447.6 | c1 and c2 free |
| LOLO spread | 6.244 | 6.250 | 247.0 | 445.3 | c1 and c2 free |

## 5. Acceptance (section 7, against MM1-v3 refitted on the same points and folds)

| rule | MM1-v3.2 | MM1-v3 refitted / the predecessor | verdict |
|---|---|---|---|
| 1 LOEO wall, no twin | 5.295% | 5.295% | EQUAL BY CONSTRUCTION (the layout rule chose none: MM1-v3.2 time = MM1-v3 refitted time): PASS |
| 1 LOEO W given t, no twin | 4.976% | 5.680% | rule 1 **PASS** |
| 2 LOCO wall | 4.698% | 4.698% | |
| 2 LOCO W given t (fallback) | 9.292% | 9.943% | rule 2 **PASS** (without the anchor points, REPORTED: PASS) |
| 3 leave rgm211 out | 5.723%, 8 of 10 pairs | <= 8.0%, >= 7 | **PASS** |
| 4(a) E212 fold vs MM1-v2 unread (comparator_4a_v31.py) | wall 4.765%, W 4.921% | wall 6.807%, W 7.702% | **PASS** |
| 4(b) E213 fold vs MM1-v3 blind | wall 4.262%, W 4.353% | wall 4.272%, W 15.361% | **PASS** |
| 4(c) E214 fold vs MM1-v3.1 unread | wall 5.933%, W 5.369% | wall 6.076%, W 5.343% | **FAIL** |
| 4(d) E215 fold vs MM1-v3.1 blind | wall 7.381%, W 5.461% | wall 8.508%, W 7.988% | **PASS** |
| 5 gemmLnc points, LOEO W given t | 8.429% (n 14) | 30.459% | **PASS** |

**Verdict: NOT ACCEPTED (rule 4c).** As declared, MM1-v3.2 is frozen as built either way and E218 runs either way.

## 6. REPORTED (section 8, never deciding)

- The predictor's self-check: {'time_points': 2508, 'max_rel_diff_T_predictor_vs_fit_in_sample': 0.0, 'energy_points_checked': 2443, 'max_rel_diff_W_given_t_predictor_vs_fit_in_sample': 6.661338147750939e-16, 'how': "the land's predictor (mm1_v32.Model on out/mm1_v32_params.json) at every time point (spec kind 'random': time is kind-blind) and every priced energy point (its kind, clock, die, governed base, minions and the volts that give its s_V), against the fit's all-data in-sample op times and W given the measured op time"}.
- Identification of the all-data constants (Jacobian rse above 100%: not identified): ['T2', 'eta'].
- E215 per point by family (MM1-v3.2: its E215 fold, held out; the others: their frozen blind forecasts):

| family | quantity | n | rms % | bias % |
|---|---|---|---|---|
| C | MM1-v3 W given t | 6 | 4.73 | 4.61 |
| C | MM1-v3 cw | 16 | 5.35 | -1.45 |
| C | MM1-v3.1 W given t | 16 | 3.15 | 2.95 |
| C | MM1-v3.1 cw | 16 | 5.89 | -0.69 |
| C | v3.1 + contention cw | 16 | 5.89 | -0.69 |
| C | v32 W given t | 16 | 2.31 | 2.02 |
| C | v32 cw | 16 | 4.98 | -1.86 |
| C | verify-lay G1 cw | 16 | 5.89 | -0.69 |
| C | verify-lay G1+N1 cw | 16 | 5.89 | -0.69 |
| C | verify-lay N1+N2 cw | 16 | 5.89 | -0.69 |
| C | verify-lay N3 cw | 16 | 5.89 | -0.69 |
| C | verify-lay fresh24 cw | 16 | 5.89 | -0.69 |
| L | MM1-v3 W given t | 6 | 7.63 | 4.60 |
| L | MM1-v3 cw | 28 | 9.65 | 7.20 |
| L | MM1-v3.1 W given t | 23 | 6.90 | 3.36 |
| L | MM1-v3.1 cw | 28 | 10.72 | 8.52 |
| L | v3.1 + contention cw | 28 | 10.85 | 8.72 |
| L | v32 W given t | 23 | 6.20 | 2.12 |
| L | v32 cw | 28 | 9.15 | 6.62 |
| L | verify-lay G1 cw | 28 | 10.74 | 8.55 |
| L | verify-lay G1+N1 cw | 28 | 10.12 | 7.49 |
| L | verify-lay N1+N2 cw | 28 | 10.13 | 7.97 |
| L | verify-lay N3 cw | 28 | 10.88 | 8.83 |
| L | verify-lay fresh24 cw | 28 | 10.87 | 8.69 |
| P | MM1-v3 W given t | 6 | 14.50 | -2.56 |
| P | MM1-v3 cw | 18 | 6.47 | 3.92 |
| P | MM1-v3.1 W given t | 18 | 13.53 | -3.66 |
| P | MM1-v3.1 cw | 18 | 7.96 | 5.16 |
| P | v3.1 + contention cw | 18 | 7.96 | 5.16 |
| P | v3.1 + gemmLnc term W given t | 5 | 9.18 | 7.50 |
| P | v3.1 + gemmLnc term cw | 5 | 11.31 | 7.17 |
| P | v32 W given t | 18 | 5.20 | 3.16 |
| P | v32 cw | 18 | 5.53 | 3.03 |
| P | verify-lay G1 cw | 18 | 7.96 | 5.16 |
| P | verify-lay G1+N1 cw | 18 | 7.96 | 5.16 |
| P | verify-lay N1+N2 cw | 18 | 7.96 | 5.16 |
| P | verify-lay N3 cw | 18 | 7.96 | 5.16 |
| P | verify-lay fresh24 cw | 18 | 7.96 | 5.16 |
| R | MM1-v3 W given t | 6 | 3.63 | 0.21 |
| R | MM1-v3 cw | 16 | 7.46 | -6.06 |
| R | MM1-v3.1 W given t | 16 | 3.42 | 0.26 |
| R | MM1-v3.1 cw | 16 | 6.78 | -5.48 |
| R | v3.1 + contention cw | 16 | 6.78 | -5.48 |
| R | v32 W given t | 16 | 3.26 | -0.38 |
| R | v32 cw | 16 | 7.74 | -6.23 |
| R | verify-lay G1 cw | 16 | 6.78 | -5.48 |
| R | verify-lay G1+N1 cw | 16 | 6.78 | -5.48 |
| R | verify-lay N1+N2 cw | 16 | 6.78 | -5.48 |
| R | verify-lay N3 cw | 16 | 6.78 | -5.48 |
| R | verify-lay fresh24 cw | 16 | 6.78 | -5.48 |
| S | MM1-v3.1 W given t | 12 | 8.45 | 2.53 |
| S | v32 W given t | 12 | 8.70 | 1.68 |
| all | MM1-v3 W given t | 24 | 8.72 | 1.71 |
| all | MM1-v3 cw | 78 | 7.77 | 1.95 |
| all | MM1-v3.1 W given t | 85 | 8.11 | 1.09 |
| all | MM1-v3.1 cw | 78 | 8.51 | 2.99 |
| all | v3.1 + contention cw | 78 | 8.57 | 3.06 |
| all | v3.1 + gemmLnc term W given t | 5 | 9.18 | 7.50 |
| all | v3.1 + gemmLnc term cw | 5 | 11.31 | 7.17 |
| all | v32 W given t | 85 | 5.46 | 1.79 |
| all | v32 cw | 78 | 7.38 | 1.41 |
| all | verify-lay G1 cw | 78 | 8.52 | 2.99 |
| all | verify-lay G1+N1 cw | 78 | 8.24 | 2.62 |
| all | verify-lay N1+N2 cw | 78 | 8.25 | 2.79 |
| all | verify-lay N3 cw | 78 | 8.58 | 3.09 |
| all | verify-lay fresh24 cw | 78 | 8.58 | 3.05 |
| posthoc | MM1-v3 W given t | 6 | 7.63 | 4.60 |
| posthoc | MM1-v3 cw | 28 | 9.65 | 7.20 |
| posthoc | MM1-v3.1 W given t | 35 | 7.46 | 3.08 |
| posthoc | MM1-v3.1 cw | 28 | 10.72 | 8.52 |
| posthoc | v3.1 + contention cw | 28 | 10.85 | 8.72 |
| posthoc | v32 W given t | 35 | 7.16 | 1.97 |
| posthoc | v32 cw | 28 | 9.15 | 6.62 |
| posthoc | verify-lay G1 cw | 28 | 10.74 | 8.55 |
| posthoc | verify-lay G1+N1 cw | 28 | 10.12 | 7.49 |
| posthoc | verify-lay N1+N2 cw | 28 | 10.13 | 7.97 |
| posthoc | verify-lay N3 cw | 28 | 10.88 | 8.83 |
| posthoc | verify-lay fresh24 cw | 28 | 10.87 | 8.69 |
| registered | MM1-v3 W given t | 18 | 9.05 | 0.75 |
| registered | MM1-v3 cw | 50 | 6.48 | -0.99 |
| registered | MM1-v3.1 W given t | 50 | 8.54 | -0.29 |
| registered | MM1-v3.1 cw | 50 | 6.97 | -0.12 |
| registered | v3.1 + contention cw | 50 | 6.97 | -0.12 |
| registered | v3.1 + gemmLnc term W given t | 5 | 9.18 | 7.50 |
| registered | v3.1 + gemmLnc term cw | 5 | 11.31 | 7.17 |
| registered | v32 W given t | 50 | 3.85 | 1.66 |
| registered | v32 cw | 50 | 6.17 | -1.50 |
| registered | verify-lay G1 cw | 50 | 6.97 | -0.12 |
| registered | verify-lay G1+N1 cw | 50 | 6.97 | -0.12 |
| registered | verify-lay N1+N2 cw | 50 | 6.97 | -0.12 |
| registered | verify-lay N3 cw | 50 | 6.97 | -0.12 |
| registered | verify-lay fresh24 cw | 50 | 6.97 | -0.12 |

- The anchor route's LOCO W given t without the anchor points (REPORTED; the fallback decides): MM1-v3.2 10.618%, MM1-v3 refitted 9.760%; the anchor kc by card: aifoundry1 card 0 1.1782, aifoundry1 card 1 1.2453, aifoundry2 card 0 1.4228, aifoundry3 card 0 0.7432.
- The layout term refitted jointly: NOT RUN: section 3's rule chose none.

## 7. E218, MM1-v3.2's blind day (section 9)

Points by section 9's rule on the landed constants, with the never-run scan (`e218_v32.py scan`): {'F': 14, 'G': 12, 'Gt': 12, 'Y': 16}; G {'candidates_by_regime': {'L2': 2, 'NB1-3': 431, 'NB12-15': 576, 'NB5-6': 288}, 'drawn': 12, 'eps_G': 0.0842859166373489, 'secs': 159.7, 'short': False, 'short_by': 0}; Y {'control_pool': 3600, 'drawn': 8, 'feature_records_made': 0, 'pairs': 3600, 'secs': 0.3, 'short': False}; F {'by_format': {'fp16': 5, 'fp32': 4, 'int8': 5}, 'drawn': 14, 'secs': 947.2, 'short': False}. The order (REPORTED for the kit): 111 runs and 2 smoke processes, 45.3 card-minutes at E213 arm A's 24.47 s a run.

These are fix-fit-v32's provisional draw (section 8): fit-v32's draw re-made by the same rule after verify-fit-v32 found 5 of its points reading as already run under the declared literal scan; E218's registration re-runs that scan and decides E218's points (DECLARED-v32.md section 10).

The readings this file applies where section 9 leaves one open:

- draws: random.Random('v3.2-blind|E218|<family>|<stratum>') is made once a stratum and its .sample(remaining qualifying, k) taken in its returned order; a pick that no longer qualifies given the points accepted before it (a shape or (NB, KB, format) clash) is skipped and the shortfall re-drawn from the then-remaining qualifying candidates with the same generator
- G's quotas: regimes processed in the pass-on order L2, NB5-6, NB12-15, NB1-3, each at its quota plus the shortfall passed on to it, then L2 again with any shortfall left; ceil(q / 2) by score and the rest by draw at each regime's effective quota q
- ties: within 1e-12 relative of the group's first score, broken by the string loop|token|format|kind|mask (a Y pair's string: the lower mask's point string + '+' + the higher mask)
- Y's planning peak uses an upper bound of 'v3.1 + contention''s W over its factor's range [1 - |a|, 1 + |a|] (|Phi_fresh| <= 1); the exact walk feature is made only where the bound reaches 67.0 W; the chosen points' contention forecasts are exact
- Y's d_c: every candidate at the layout rule's all-data two-stage constants (its output's candidates > a_all) on MM1-v3.2's base op time (the refitted T5r+G0+n32 at its all-data constants), the factor clipped to [0.3, 3.0]
- the scan's three named changes (module docstring): E218's folders subtracted, MM1-v3.2's points, E216 and E217 unread (E216's registered points counted as run on aifoundry2 card 0; every token E217's registration names counted as run on every card at every mask, as the scanner counts a lane file naming no card; a stand-in, not the literal scan)

Every declared model's forecasts are in `out/e218/forecasts-e218.csv` and `.json` (MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, 'v3.1 + gemmLnc term', 'v3.1 + contention', verify-lay's controls; REPORTED: 'v3.1 + both terms', 'v3.1 with T7', MM1-v3 refitted). Their sha256 are in `out/e218/E218-FROZEN.txt`; the land's push is their freeze line.

## 8. Named readings, departures and gaps

- THE CODE: time by `../v3.1/fit_v31.py`'s `fit_time` and `run_time` unchanged, with two of its module globals replaced by `fit_v32.py` (`pins_for`: v3.1's rule plus the declared eta pin; `folds`: the declared folds); the energy procedure `fit_v31.fit_energy` copied line for line into `fit_v32.fit_energy` for E1t+F3 (c1, c2 among the linear constants, bounds [0, 10,000], F3's pins), and called unchanged for E1u and the ledger. The predictor `mm1_v32.py` is `../v3.1/mm1_v31.py` with W from `energy_v32.W32` and the layout factor; its self-check reproduces the fit's in-sample op times and W given t (out/selfcheck_v32.json).
- THE eta PIN (section 2) uses engine_v3's row-imbalance flag literally (a subset mask, all four column groups, fewer than eight row groups); engine_v3's eta term is max(0, (4 - R) / 3) and so is 0 at R = 4-7: a fold whose only flagged training points have R >= 4 leaves eta free but unidentified (REPORTED per fold in decisions step 1). eta was pinned in: ['LOLO compact'].
- F3's PIN RULE (section 1.3): S_i = D_i sL_i n_i / t_i x 1e-12 needs xi, a constant of the same fit; the rule is read at xi = 1 (the energy fit's first start, MM1-v3's declared S0) and the condition number at xi = 0 and 1 is printed beside every fold's pin, with whether the decision differs there (decisions step 3 > F3_by_fold). All-data: c1 and c2 free.
- RULE 2 reads 'every point both price at 3 W and above' literally (the anchor points included, they are priced by both); the figures without the anchor points (v3.1's reading) are printed beside, with their verdict (PASS there).
- RULE 4(a): `comparator_4a_v31.py` unchanged scores the fold it is given; its column named 'v31' is the fold under test, here MM1-v3.2's E212 fold (the same CSV form fit-v31 wrote).
- RULE 4(d): a time case enters when one of its points is of families P, C, R or L (family S shares its case with its reference and is scored in energy only, E215's own form); references (r01, r02, r11, r12) and ties (t01, t02) are excluded in time and energy.
- RULE 5 is read at 3 W and above, as every 'W over idle given t' figure of section 6 (every gemmLnc point is far above 3 W).
- E215's READER: data_v31's E213 reader on each arm's data-e215.json, with the ties (t01 arm A gemmL2x4x4 fp32, t02 arm B gemmL4x8x8 int8, the full chip, random, as E215.md names them) read from the arm's 'ties' runs as points (section 4); a run's record is compared with the registered point with the shire mask read as a number (E215's scorer's reading) and, REPORTED, as the E213 reader's string: arm A: the two readings keep the same runs: True; arm B: the two readings keep the same runs: True.
- E215's DATA were vendored only after the gate (E215's blind scores on GitHub main); the labelled rehearsal before it (E105-E214, no E215) is not reported and nothing was chosen from it (OUT/fit-v32/work/rehearsal).
- E218's DRAW IS THIS LAND'S, AND PROVISIONAL (section 9 says E218's points are decided 'at E218's registration'; section 10). fit-v32 drew them at the fit (the round's brief, fit-v31's form) with a never-run scan that opened no E216 or E217 data file (section 4) and counted their committed registrations as run instead: E216's registered points on aifoundry2 card 0, E217's registered schedules and arms on aifoundry1 only. It called that a superset of what ran, and it was not one: the scanner's folder rule counts a lane file whose path names no card for every card, and the round's data-e217 lane folder holds such files, so under the declared literal scan verify-fit-v32 found 5 of fit-v32's 54 points reading as already run on aifoundry3 card 0 (g05t, g06t, g10t, y04a, y04b; g06t's through a file of the data-e219 lane written at 18:17 PST, after fit-v32's scan at 16:10). Lane fix-fit-v32 re-drew E218 by the same rule and the same code with that stand-in corrected: every shape token E217's registration names now counts as run on every card at every mask; E216's registered points stay on aifoundry2 card 0 (the card the scanner's classes give its data and lane folders at GitHub main); every other folder is read as the scanner reads it, data-e219 included (scan 2026-11-19 18:51:41 PST to 2026-11-19 18:51:52 PST, 84181 files, E216 and E217 files not read: 6704). Changed against fit-v32's draw: f08, f09, f13, f14, g04, g04t, g05, g05t, g06, g06t, g07, g07t, g08, g08t, g10, g10t, g11, g11t, g12, g12t, y04a, y04b, y05a, y05b, y06a, y06b, y07a, y07b, y08a, y08b (30 points); unchanged: 24. verify-fit-v32's own re-draw under this stand-in (independent code; its scan at 18:29 PST; F kept as fit-v32 drew it) equals this draw at 50 of 54 points (it differs at f08, f09, f13, f14, F's drawn half, which it did not re-draw: here F's pool of never-run tokens moved, 8 tokens leaving it (gemmL1x11x6, gemmL1x13x1, gemmL1x13x6, gemmL2x10x1, gemmL2x12x1, gemmL3x10x1, gemmL4x3x3, gemmL5x3x2) because the data-e219 lane's copy of E219's kit names them in an arms list whose path names no card, and G and Y took other shapes first, so the declared draw picked differently). It is still a stand-in, not the literal scan: it covers what the two registrations name, not any other token those unread folders may name, and the literal scan's result depends on when it runs (data lanes keep adding files). So E218's points and forecasts here are a provisional draw: E218's registration re-runs the declared scan literally (it is not the fit lane) and, if any point reads as run, re-runs the whole of section 9's rule rather than dropping points (a dropped point would shrink a family and could leave a G point without its twin), freezing section 9.6's forecasts of every point it draws from the landed predictors unchanged; the card lane repeats the scan (step 6n). Nothing in MM1-v3.2 changed: out/mm1_v32_params.json is fit-v32's byte for byte.
- LAYOUT FEATURES at E218's Y candidates were made at the two capacities the candidates read (24 and 32 MB) and without v01_map's walk cross-check of the generator (verify-lay's check 1 held at 148 of 148 configurations); the data's configurations carry every capacity and the check.
- E218 GAPS (REPORTED, as the declared rule chose): (1) family G holds no L2-resident point: the regime's only two candidates (gemmLnc1x1x1 in fp32 and int8) ran on aifoundry3 card 0, so its quota of 2 passed on to NB5-6 (5 points there); (2) family F's scored half sits on one per-op forecast family: 8 of its 14 points are gemmL<MB>x16x3 (the largest |ln(cycles_v3.2 / cycles_v3.1)| is the same at every MB there; section 9.4 has no clause like G's (NB, KB, format) one); (3) Y's two control pairs have D_p = 0 exactly (every candidate prices both masks alike there).
- E218's FAMILY Y, RANKED HALF (verify-fit-v32's finding; REPORTED): 5 of its 6 ranked pairs (y02, y03, y04, y05, y06) are one mask pair, 0xf against 0x3030, at KB-24 shapes (gemmL1x16x24, gemmL1x4x24, gemmL2x16x24, gemmL2x2x24, gemmL2x8x24); their D_p values agree to 7.3e-15 relative, inside the declared 1e-12 tie window, so they are one tie broken by the sorted string, and the ranked half tests one mask pair at several shapes more than several mask pairs. The declared rule decided it; a later declaration could spread the mask pairs (as G's (NB, KB, format) clause spreads G); E218's registration should say it.
- E218's FAMILY F, ORDER INSIDE gemmL<MB>x16x3 (verify-fit-v32's finding; REPORTED): there the score s = |ln(cycles_v3.2 / cycles_v3.1)| is the same at every MB but for floating-point rounding: in each format the choice log's candidates of that family (fp16: gemmL2x16x3 1.1e-11 relative above the rest, which tie exactly, fp32: gemmL2x16x3 1.1e-11 relative above the rest, which tie exactly, int8: gemmL2x16x3 1.1e-11 relative above the rest, which tie exactly) differ by about 1e-11, just outside the declared 1e-12 tie window (fp32: 0.08226654165505058 against 0.08226654165417208), so f01 is gemmL2x16x3 rather than the string-first gemmL10x16x3, and the MB a format's scored half takes is set by rounding, not by the model; the declared rule decided it.
- RULE 4(c) fails on its energy half alone: MM1-v3.2's E214 fold reads W over idle given t 5.369% against MM1-v3.1's unread 5.343% (n 466, twins included as declared; its time half passes, 5.933% against 6.076%). Without twins (REPORTED) the energy half reads 5.534% against 5.504% (n 426) and the time half 6.493% against 6.656% (n 425). As declared, MM1-v3.2 is frozen as built and E218 runs either way.

## 9. Files, and how to re-run

- `DECLARED-v32.md`, `declared-v32.json`, `layout_rule_v32.py`, `layout_rule_v32_deskcheck.py`, `DECLARED-v32.sha256`, `out/deskcheck-layout-rule.json`, `out/selftest-layout-rule.json`: the declaration (decl-v32, hashed 14:56:30 PST, posted #1.30), byte for byte.
- `data_v32.py` (the points), `energy_v32.py` (E1t + F3, the counts merge), `fit_v32.py` (the pins, folds, energy fit), `layout_v32.py` (features, F1's check, the factor), `run_v32.py` (the declared order, the acceptance rules), `summary_v32.py` (params, held-out record, identification, self-check), `reported_v32.py` (section 8), `mm1_v32.py` (the predictor), `e218_v32.py` (E218's scan, point rule, forecasts), `readme_v32.py`.
- `inputs/e214/` (E214's seven reductions), `inputs/e215/` (E215's two data-e215.json and its registered points-e215.csv), byte for byte.
- `out/mm1_v32_params.json` (the frozen constants), `out/decisions_v32.json` (every step's record), `out/holdout_v32.json` (the held-out record beside MM1-v3 refitted), `out/points_time_v32.csv`, `out/points_energy_v32.csv`, `out/identification_v32.json`, `out/reported_v32.json`, `out/selfcheck_v32.json`, `out/rule4a_v32.json` with `out/v32-e212-fold.csv`, `out/rule4-e214-rows.json`, `out/rule4-e215-rows.json`, `out/run.log`.
- `out/fits/time_T5r+G0+n32.json` (every time fit), `out/fits/v32/energy_T5r+G0+n32.json` (E1t+F3), `out/fits/v3refit/energy_T5r+G0+n32.json` (E1u and the ledger).
- `out/layout/` (the bundle, the rule's output, the features made here, lay-contention's records made for F1's check).
- `out/e218/` (the scan, the choice record, the points, every model's forecasts, E218-FROZEN.txt).
- To re-run: `/usr/bin/python3 -I -B run_v32.py --out <dir> --tag final --scores-e215 docs/reports/data`, then `summary_v32.py --out <dir>`, `reported_v32.py --out <dir>`, `e218_v32.py scan ...` and `e218_v32.py choose --scan ... --fit <dir> --out <dir>/e218`, each with the four thread variables at 1.

## 10. NOT RUN

- No card, no simulator run, no commit, nothing written in the shared lab clone.
- Section 6's held-out figures for the counter's mean cycles: NOT RUN (the wall cycles are scored in every fold; at the measured clock the seconds' errors equal the wall's; the counter's mean is in every forecast of E218 and in the predictor).
- Section 6's held-out energy figures with the seconds forecast for LOCO, LOKO, LOLO and leave rgm211 out: W given t only there (out/holdout_v32.json); LOEO carries all four energy quantities.
- The chosen layout term refitted jointly with the time constants (section 8): NOT RUN.
- An independent verifier of the fit: verify-fit-v32 (the round's lane) HOLDS WITH FIXES: every number and decision re-derived by independent code and equal; its findings are answered here (E218 re-drawn; this README's wording). An independent check of fix-fit-v32's re-draw beyond verify-fit-v32's own variant re-draw: NOT RUN.
- E218's literal never-run scan (it opens E216's and E217's folders, which a fit lane may not) at E218's registration, and the card lane's step 6n: theirs, not run here.

