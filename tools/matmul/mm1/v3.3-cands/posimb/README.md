# 'MM1-v3.2 + posimb': a layout term for equal-count shire masks (a v3.3 candidate), frozen for E220

*Round Q234, lane layout2 (track Y), Fri 20 Nov 2026 (week 47), Pacific time, at aifoundry2's desk. Desk only: no card, no simulator, no E220 datum. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP / OPENBLAS / MKL / NUMEXPR_NUM_THREADS = 1), every job in the round's CPU slots, one at a time.*

The owner's words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained."

**Labels.** *Post hoc*: every constant and every choice here (made after its data existed; the form was chosen after an in-sample look at MM1-v3.2's residuals, disclosed in `DECLARED-posimb.md`). *Held out*: left out of the fit that scores it (not blind). *Blind*: only E220, once these forecasts' sha256 are posted or pushed before its first card command. *REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: not run. Errors: forecast / measured - 1 (%), pair errors in ln.

## 1. The lead

Equal-count layouts differ by a real 4-7%: E216 (aifoundry2 card 0) y01-y03, 0x3 against 0x10001, measured ln(a/b) +0.072, +0.068, +0.040 (repeat noise 0.0039 ln), where the frozen contention term F1 predicted -0.028, and the controls y07/y08 (0x101 against 0x10001, equal row and column groups) +0.036 / +0.042 against 0; E218 (aifoundry3 card 0) added seven pairs (y01 -0.090; y02, y04-y06 +0.042; y07/y08 -0.021 / -0.024). MM1-v3.2 prices equal-count masks alike (its layout rule chose no term), so it predicts 0 for every such pair.

## 2. What separates the faster layout from the slower (post hoc, in sample: `scripts/x02`-`x04`, `out/explore_x02.json`, `out/imbalance_x04.json`)

- **At deep K the op time is a property of the mask alone.** E218's KB-24 points read 1537.4 cycles at 0xf and 1473.8 at 0x3030 at four to five shapes each (within 0.2 cycle), 1603.2 at 0x55555555 at two shapes: a per-mask constant, so a position or arbitration effect, not a footprint one. The active shires' mean L3 latency on the mesh (the MARTY map, 110 + 12 x hops to the 32 homes; the hop-mean control) orders E218 y01, y02-y06 and E216 y07/y08, but not E218 y07/y08 (equal hop means) and not E216 y01-y06.
- **Half of every pair difference is the wall's excess over the counter's mean, between shires.** ln(wall / mean) is 0 at every single-shire point (52 points, |ln| < 1e-5), and over the 273 equal-count pairs of the data the mean part and the imbalance part of the wall difference have equal rms (0.078, 0.079 ln) and correlate -0.59. At E216 y01-y03 the slower layout (0x3: row group 0 only, so its DRAM stream, B, is private to each shire) carries ln(wall/mean) 0.028-0.044 and the faster (0x10001: B shared by both shires) 0; at E218 y01 the slower (0x1010101: its DRAM stream A private) 0.040, the faster (0xf000: A shared) 0. A private DRAM stream lets the shires drift; the wall is the laggard's.
- **Not explained here:** E217's and E214's large single-column pairs at gemmL2x6x10 (wall / mean up to 1.16 with an L3-resident working set, and n = 2 masks of the same row and column groups differing by 0.21 ln: 0x22 against 0x44), E212's sign flips by shape, and E218 y07/y08. Of the 145 pairs whose residual difference exceeds 1%, the hop mean orders 77, the slowest active shire's hop 37 and the mean hop to the memory shires 72.

## 3. The form (declared before any fit: `DECLARED-posimb.md`, sha256 `a7cd74a06da23523c32f5059465cfbea4c5dbbc61a24a934f43112b57b1098b9`, hashed 2026-11-20 05:35:31 PST)

T = T_v32 x clip(1 + a_hop Phi_hop + a_lag Phi_lag, 0.3, 3.0) at the subset points of rgm136's gemmL loop (every other point and every full-chip point keeps MM1-v3.2 to the last bit); the counter's mean takes only the position part. Phi_hop = e x (Lmean_act / Lmean_full - 1); Phi_lag = e x ((Lmax_act - Lmean_act) / Lmean_full) x Fp / (Fp + Fs); e = MM1-v3.2's elasticity of its op time to its L3 and DRAM constants (about 1 memory-bound, about 0 L2-resident); Fp, Fs = the walk's private and shared DRAM-served request shares (verify-lay's committed v01_map generator, strict LRU at 32 MB). Two new constants; MM1-v3.2's constants unchanged (two-stage).

## 4. The fit and the held-out record (post hoc, held out where it says so; `out/fit_results.json`, `logs/g01.log`)

Data: every committed time point through E219, 3231 points (640 in the term's scope), MM1-v3.2's 2508 (E105-E215) plus E216 46, E217 486, E218 52, E219 139; E146's store rungs out of every fit; twins (same card, kernel, arm, format, mask in another experiment): 976.

**All-data constants: a_hop = 0.1333, a_lag = 0.4367** (expected signs, both positive; a_lag positive in all 32 folds, from 0.27 to 0.76; a_hop positive in 31 of 32, from -0.507 to 0.397, negative only in LOLO other).

| the declared rule | MM1-v3.2 | + posimb | threshold | verdict |
|---|---|---|---|---|
| K1 the lead: 15 pairs' held-out ln(a/b) error rms, LO-Y fold (E216 + E218 out) | 0.0469 | **0.0329** | <= 0.0375 (0.80 x) | PASS |
| K2 pooled LOEO wall rms without twins (n 2255) | 5.738% | 5.733% | <= 5.788% | PASS |
| K3 placebo (the pair of features permuted among the scope points), 100 draws | - | beaten in 100 | >= 95 | PASS |

**Verdict: KEPT by its declared rule.** Placebo M1 quantiles (min, 5%, median, 95%, max): 0.0422, 0.0454, 0.0470, 0.0502, 0.0525.

REPORTED beside (never deciding): the lead's pairs ordered by sign: 10 of 15 (MM1-v3.2 none; hop mean 7; count only 4); the 31 Y points' own rms in the LO-Y fold 7.06% -> 7.12% (the pair differences improve, the levels do not); pooled LOEO with twins 5.121% -> 5.119% (n 3231); the scope points' LOEO without twins 7.12% -> 7.10%; LOCO pooled 5.132% -> 5.121%; **LOLO pooled 6.70% -> 6.91% (worse: the class 'other' 7.51% -> 8.25%, where the hop constant fitted without that class turns negative)**.

The baselines, fitted by the same procedure on the same folds (REPORTED): **hop mean** (T x (1 + a G1), one constant): M1 0.0439, pooled LOEO without twins 5.742%; **count only** (verify-lay's N1+N2): M1 0.0469, 5.773%. The term's parts alone on the LO-Y fold: hop part alone (e x G1core) a 0.219, M1 0.0429; lag part alone (e x LAGcore) a 0.536, M1 0.0344.

| fold | n (in scope) | MM1-v3.2 rms | + posimb | in scope: MM1-v3.2 | + posimb | a_hop, a_lag |
|---|---|---|---|---|---|---|
| LOEO E206 | 232 (28) | 4.176 | 4.205 | 5.027 | 5.221 | 0.135, 0.485 |
| LOEO E207 | 53 (8) | 4.461 | 4.485 | 8.242 | 8.327 | 0.132, 0.417 |
| LOEO E208 | 184 (23) | 3.413 | 3.390 | 2.514 | 2.254 | 0.119, 0.430 |
| LOEO E209 | 46 (9) | 5.314 | 5.317 | 8.226 | 8.235 | 0.086, 0.468 |
| LOEO E211 | 26 (0) | 6.406 | 6.406 | - | - | 0.134, 0.438 |
| LOEO E212 | 478 (122) | 4.619 | 4.570 | 5.991 | 5.843 | 0.059, 0.550 |
| LOEO E213 | 118 (22) | 4.212 | 4.087 | 5.681 | 5.169 | 0.170, 0.470 |
| LOEO E214 | 518 (167) | 5.933 | 5.889 | 6.788 | 6.670 | 0.126, 0.379 |
| LOEO E215 | 84 (28) | 7.134 | 7.134 | 9.152 | 9.151 | 0.089, 0.386 |
| LOEO E216 | 46 (16) | 7.167 | 7.293 | 8.710 | 9.008 | 0.140, 0.495 |
| LOEO E217 | 486 (196) | 6.468 | 6.541 | 7.275 | 7.436 | 0.397, 0.278 |
| LOEO E218 | 52 (15) | 7.289 | 7.221 | 4.685 | 4.307 | 0.125, 0.429 |
| LOEO E219 | 139 (6) | 3.868 | 3.868 | 0.128 | 0.128 | 0.133, 0.437 |
| LOCO aifoundry1 card 0 | 633 (208) | 5.996 | 5.987 | 6.936 | 6.914 | 0.220, 0.389 |
| LOCO aifoundry1 card 1 | 1117 (267) | 5.042 | 5.018 | 6.565 | 6.490 | 0.181, 0.273 |
| LOCO aifoundry2 card 0 | 824 (86) | 4.802 | 4.816 | 6.619 | 6.713 | 0.031, 0.598 |
| LOCO aifoundry3 card 0 | 657 (79) | 4.768 | 4.748 | 6.430 | 6.307 | 0.143, 0.426 |
| LO-Y | 98 (31) | 7.232 | 7.251 | 7.055 | 7.119 | 0.133, 0.489 |
| LOLO compact | 289 (289) | 5.162 | 5.162 | 5.162 | 5.162 | 0.099, 0.316 |
| LOLO spread | 203 (203) | 7.912 | 7.932 | 7.912 | 7.932 | 0.378, 0.277 |
| LOLO other | 148 (148) | 7.506 | 8.249 | 7.506 | 8.249 | -0.507, 0.757 |

(LOEO folds E105-E190 have no point in the term's scope and read MM1-v3.2's own figures: `out/fit_results.json` > folds.)

The lead's 15 pairs, held out (LO-Y): measured ln(a/b) against the term's (MM1-v3.2 predicts 0 at each):

| pair | arm | masks | measured | + posimb | hop mean | count only |
|---|---|---|---|---|---|---|
| E216 y01 | gemmL1x8x8 | 0x3 / 0x10001 | +0.0721 | +0.0326 | -0.0027 | +0.0000 |
| E216 y02 | gemmL1x8x12 | 0x3 / 0x10001 | +0.0683 | +0.0326 | -0.0027 | +0.0000 |
| E216 y03 | gemmL1x4x16 | 0x3 / 0x10001 | +0.0404 | +0.0326 | -0.0027 | +0.0000 |
| E216 y04 | gemmL4x2x16 | 0xf / 0x33 | -0.0457 | +0.0234 | +0.0023 | +0.0000 |
| E216 y05 | gemmL2x8x16 | 0x5555 / 0x11111111 | +0.0027 | -0.0207 | -0.0029 | +0.0000 |
| E216 y06 | gemmL4x8x16 | 0x5555 / 0x11111111 | +0.0035 | -0.0207 | -0.0029 | +0.0000 |
| E216 y07 | gemmL1x4x24 | 0x101 / 0x10001 | +0.0360 | +0.0041 | +0.0049 | +0.0000 |
| E216 y08 | gemmL1x8x24 | 0x101 / 0x10001 | +0.0420 | +0.0041 | +0.0049 | +0.0000 |
| E218 y01 | gemmL4x2x8 | 0xf000 / 0x1010101 | -0.0902 | -0.0380 | -0.0134 | +0.0000 |
| E218 y02 | gemmL1x16x24 | 0xf / 0x3030 | +0.0423 | +0.0248 | +0.0078 | +0.0000 |
| E218 y04 | gemmL2x16x24 | 0xf / 0x3030 | +0.0424 | +0.0247 | +0.0078 | +0.0000 |
| E218 y05 | gemmL2x2x24 | 0xf / 0x3030 | +0.0421 | +0.0245 | +0.0078 | +0.0000 |
| E218 y06 | gemmL2x8x24 | 0xf / 0x3030 | +0.0423 | +0.0247 | +0.0078 | +0.0000 |
| E218 y07 | gemmL4x16x24 | 0x55555555 / 0xffff0000 | -0.0213 | +0.0000 | +0.0000 | +0.0000 |
| E218 y08 | gemmL4x2x24 | 0x55555555 / 0xffff0000 | -0.0242 | +0.0000 | +0.0000 | +0.0000 |

The counter's mean at the 31 Y points (REPORTED): MM1-v3.2 10.11% rms -> x g_m 10.06%; MM1-v3.2's own mean misses the R1C4 masks at MB >= 2 by -13 to -24% (E218 y01a, y04a-y06a; E216 y04a: its imbalance_mean prices a wall / mean gap the card does not show there): a v3.2 gap this term does not touch.

## 5. The frozen forecasts for E220 (final 2026-11-20 05:39:30 PST, before any E220 datum)

For every point of `OUT/reg-e220/POINTS.txt` (FINAL 05:24:17 PST, sha256 `058984a04b90cd8585cb41cc6618430306d7bf1c7e230159e7719b9e9e1e9bdc`; points-e220.csv `64a7c99a90a2d899db44dc0c3790dfd840cd02b49c9d12f24396f4691125afc4`): arm A (aifoundry1 card 1) at 600.0 MHz, arm B (aifoundry2 card 0) at 799.0, 700.0 and 600.0 MHz, 306 rows, 100 in the term's scope (the XY and Y2 subset points), every other row MM1-v3.2's to the last bit; MM1-v3.2's own columns beside each row equal reg-e220's frozen MM1-v3.2 forecast to <= 5e-9 relative at 306 of 306 rows. Label: **MM1-v3.2 + posimb**.

| file | sha256 |
|---|---|
| `forecasts-e220-posimb.csv` | `1de81ec510573d184c960234f83f0ed51881a5b17b7e8ce75aa3702925e86182` |
| `forecasts-e220-posimb.json` | `3010f28c7e47e754a8bc4da5d0742e0d515c85da8d59e70a4ee3b798ccca1034` |
| `forecasts-e220-posimb.txt` | `1a25dd62d09f2e780bd5159e9289e95ca776b3a766a03ba99ebcd956739bacd4` |

Columns per model ('MM1-v3.2 + posimb|...' and 'MM1-v3.2|...'): cycles_per_op_wall, cycles_per_op_mean, T_op_us, seconds_per_gemm, W_over_idle (at the forecast t), A_W, B_W_us (W over idle given a measured t = A_W + B_W_us / t_us: MM1-v3.2's own), J_over_idle_per_gemm and J_at_rest_per_gemm (with t forecast; J at rest given t uses MM1-v3.2's rest-law P_rest, reg-e220's rest_law_W column, equal to J_at_rest_per_gemm / seconds_per_gemm - W_over_idle here); with each row's e, G1core, LAGcore, Phi_hop, Phi_lag, g_wall, g_mean, Fp, Fs, Lmean_act, Lmax_act.

What the term predicts blind for E220's pairs (ln(a/b) of wall cycles; the same on both arms and clocks to 1e-4; MM1-v3.2 0):

| pair | shape | masks | + posimb | measured on another card (E216 or E218) |
|---|---|---|---|---|
| p01 | gemmL1x8x9 | 0x3 / 0x10001 | +0.0289 | E216 y01-y03 (0x3 / 0x10001, other shapes) +0.040 to +0.072 |
| p02 | gemmL1x8x13 | 0x3 / 0x10001 | +0.0289 | as p01 |
| p03 | gemmL1x4x17 | 0x3 / 0x10001 | +0.0289 | as p01 |
| p04 | gemmL1x4x25 | 0x101 / 0x10001 | +0.0042 | E216 y07/y08 (0x101 / 0x10001) +0.036 / +0.042 |
| p05 | gemmL1x8x25 | 0x101 / 0x10001 | +0.0042 | as p04 |
| xy01 | gemmL4x2x8 | 0xf000 / 0x1010101 | -0.0352 | E218 y01 -0.090 |
| xy02 | gemmL1x16x24 | 0xf / 0x3030 | +0.0229 | E218 y02 +0.042 |
| xy04 | gemmL2x16x24 | 0xf / 0x3030 | +0.0228 | E218 y04 +0.042 |
| xy05 | gemmL2x2x24 | 0xf / 0x3030 | +0.0226 | E218 y05 +0.042 |
| xy06 | gemmL2x8x24 | 0xf / 0x3030 | +0.0228 | E218 y06 +0.042 |
| xy07 | gemmL4x16x24 | 0x55555555 / 0xffff0000 | +0.0000 | E218 y07 -0.021 |
| xy08 | gemmL4x2x24 | 0x55555555 / 0xffff0000 | +0.0000 | E218 y08 -0.024 |

## 6. Gaps, and what was NOT RUN

- Two-stage only: MM1-v3.2's constants were not refitted with the term (a joint refit: NOT RUN).
- The term explains part of the lead (K1) and little elsewhere: E217's and E214's L3-resident single-column imbalance, E212's shape-dependent signs and E218 y07/y08 are not captured; LOLO pooled is worse (section 4); the Y points' own levels do not improve.
- The mesh positions (the MARTY map) and the 110 + 12 x hops law are the lab's notes, used unchanged; the single-shire walls at gemmL2x6x10 (E214: shires 0 and 31; E217: shires 8-11) do not follow them (0 and 31 slowest, and of 8-11 the one nearest the homes, 10, the slowest); the memory shires' placement is not used.
- The walk's levels are a strict-LRU model at 32 MB (no measured L3 under a subset mask).
- The counter's mean: the term's g_m leaves MM1-v3.2's large miss at R1C4 masks with MB >= 2 as it is.
- No independent verifier of this lane's fit: NOT RUN (the round's verify lane, if any, is the check).

## 7. Files

- `DECLARED-posimb.md` (+ `.sha256`): the declaration, hashed before any fit.
- `forecasts-e220-posimb.csv`, `.json`, `.txt`: the frozen E220 forecasts (read only).
- `out/points_all.json` (every time point through E219 in MM1-v3.2's form), `out/base_meta.json` (the fold bases' checks: every fold's held-out base re-made to 0 difference from MM1-v3.2's stored predictions), `out/private_shared.json` (the features per configuration), `out/features_points.json` (v01 records), `out/fit_results.json` (the declared fit and rule), `out/reported_g02.json`, `out/explore_x02.json` and `out/imbalance_x04.json` (the in-sample looks), `out/check_c01.json` (the self-check).
- `scripts/`: the lane's scripts as run, with their absolute lane paths replaced by environment lookups (`SCRUB.json`: each file's sha256 as run and as landed): d01 (points), e01 (bases, elasticity), f01, f02 (features), x01-x04 (looks), g01 (the declared fit), h01 (the freeze), g02 (REPORTED), c01 (a self-check of g01's deciding numbers by separate code: equal to 1e-15), l01, l02 (this land). Re-run from a checkout at GitHub main 0f046200 placed at `$LAYOUT2_LANE/work/lab`, in that order, each as `/usr/bin/python3 -I -B scripts/<file>` with the four thread variables at 1.
- `logs/`: f01, f02, g01, g02 outputs.

SPDX-License-Identifier: Apache-2.0
