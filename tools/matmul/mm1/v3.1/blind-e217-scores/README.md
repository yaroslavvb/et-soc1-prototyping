# MM1's frozen matmul models scored BLIND on E217 (blind-e217, round Q228)

*Scored Thu 19 Nov 2026 at the desk on aifoundry2: the read Thu 19 Nov 2026 21:06:44 PST; Python /usr/bin/python3 3.12.3 (numpy 1.26.4 for the forecasts), every numerical step single-threaded inside the round's CPU slots. No card, no device, no ssh. Nothing here is committed by this lane.*

**What this is.** E217 is the model session's fourth matmul sweep (1119-mmsweep4, Discussion #13: rgm136's gemmL loop, 630 runs over 331 arms and an anchor in seven sessions on aifoundry1, card 1 S1-S4 at 600 MHz and card 0 S1-S3 at low power under its governor). Before any E217 datum existed, the lab DECLARED how it would score its frozen models on E217 (decl-e217: `../blind-e217/DECLARED-blind-e217.md`, sha256 099806dc..., FROZEN.txt 32311daf... at 11:37:53 PST, the counts of E217's 21 new tile kinds frozen in COUNTS-FROZEN.txt 4867c1d0... at 12:22:24 PST, both posted on the Discussion as #13.1.1). This folder is that test, run EXACTLY as declared: every frozen file's sha256 checked, the forecasts made by the declared procedure at each run's measured clock, minion volts and die at start and hashed, the scorer hashed, and only then the measurements read and scored.

**Label: BLIND (every session: its first datum after the freeze post).** The freeze post #13.1.1 is stamped 2026-11-19 12:26:07 PST in the round's record (12:25:56 PST in the round log; the exact second is not checked, and either is more than two hours before E217's first card command):

| session | label (declaration / counts route) | T0 (PST) | first card command (README) | claim post | minutes after the freeze post | runs | MM1-v3.1 per run, REPORTED: wall / J over idle given t |
|---|---|---|---|---|---|---|---|
| a1c0-S1 | BLIND / BLIND | 15:27:34 | 15:27:37.990 | #13.1.2.1.1.1.1.1.1 15:27:30 | 181.4 | 86 | 6.83% / 6.23% |
| a1c0-S2 | BLIND / BLIND | 16:57:41 | 16:57:44.501 | #13.1.2.1.1.1.1.1.1.1.1.1.2 16:57:36 | 271.6 | 85 | 6.11% / 4.18% |
| a1c0-S3 | BLIND / BLIND | 18:25:38 | 18:25:41.539 | #13.1.2.1.1.1.1.1.1.1.1.1.6 18:25:33 | 359.5 | 83 | 7.42% / 4.99% |
| a1c1-S1 | BLIND / BLIND | 14:41:11 | 14:41:14.595 | #13.1.2.1.1.1.1 14:41:06 | 135.1 | 87 | 5.99% / 10.42% |
| a1c1-S2 | BLIND / BLIND | 16:12:57 | 16:13:00.693 | #13.1.2.1.1.1.1.1.1.1.1.1 16:12:51 | 226.8 | 83 | 5.68% / 6.22% |
| a1c1-S3 | BLIND / BLIND | 17:40:55 | 17:40:59.340 | #13.1.2.1.1.1.1.1.1.1.1.1.4 17:40:53 | 314.8 | 90 | 6.27% / 5.84% |
| a1c1-S4 | BLIND / BLIND | 19:06:52 | 19:06:55.525 | #13.1.2.1.1.1.1.1.1.1.1.1.8 19:06:49 | 400.8 | 85 | 5.15% / 4.00% |

## 1. The verdict (decided by the script, as declared)

**FAIL.** Part A (MM1-v3.1 on the primary footing, E215's rule form, each card over its no-twin cases) **FAIL**: aifoundry1 card 1 T1, aifoundry1 card 1 T3, aifoundry1 card 1 E4, aifoundry1 card 0 T1, aifoundry1 card 0 T3, aifoundry1 card 0 E4. Part S (the switch route on E217's 21 new tile kinds against the null) **PASS** (P1 True, P2 True, P3 True, P4 True). The declaration's rule: PASS needs both parts to pass; a failing part fails the test.

| rule (band) | aifoundry1 card 1 | aifoundry1 card 0 |
|---|---|---|
| T1 (10% / 11%) | FAIL 179/218 | FAIL 172/205 |
| T2 (13% / 16%) | PASS 202/218 | PASS 196/205 |
| T3 (10% / 11%) | FAIL 179/218 | FAIL 172/205 |
| E1 (14% / 11%; watts 0.56 W) | PASS 235/248 | PASS 199/210 |
| E2 (14% / 13%; watts 0.56 W) | PASS 237/248 | PASS 191/210 |
| E3 (5% / 5%) | PASS 246/248 | PASS 208/210 |
| E4 (10% / 10%) | FAIL 214/248 | FAIL 175/210 |

T1 wall cycles an op, T2 the counter's mean cycles, T3 seconds a GEMM, E1 J over idle given the measured op time (watts at a case under 3 W), E2 J over idle with the op time forecast, E3 J with the card at rest given t, E4 J at rest with t forecast. A rule passes when 90% of its cases are inside the band.

Part S, pooled over both cards: Q1 (W over idle given t, 35 group-S cases): MM1-v3.1 with the counts 6.30% rms (+2.80) against the null N (the mean of zeros, ones and random at the same conditions) 47.58%; closer 30/2/3 ties, p 2.5e-07. Q2 (the share of the data-dependent power D, 29 cases): 8.48% of D against 27.46%; closer 24/1/4, p 1.5e-06. MM1-v3 with the same counts (REPORTED): Q1 7.29%, Q2 10.23% of D.

## 2. The headline: no-twin cases, the primary footing (each run at its measured conditions)

rms % (bias %), n cases; E1 and E2 relative where the case is 3 W or more, watts beside.

| model | wall cycles (T1) | counter mean (T2) | J over idle given t (E1) | J over idle, t forecast (E2) | J at rest given t (E3) | J at rest, t forecast (E4) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 7.36% (+2.21), n 423 | 7.55% (+3.00), n 423 | 5.33% (+1.32), n 386; watts 0.38 W (-0.12), n 72 | 7.87% (+2.31), n 386; watts 0.33 W (-0.11), n 72 | 1.56% (+0.43), n 458 | 6.91% (+1.97), n 458 |
| MM1-v3 | 7.20% (+1.98), n 423 | 7.39% (+2.76), n 423 | 5.18% (+1.39), n 386; watts 0.39 W (-0.17), n 72 | 7.67% (+2.32), n 386; watts 0.34 W (-0.15), n 72 | 1.52% (+0.42), n 458 | 6.81% (+1.77), n 458 |
| MM1-v2 | 8.43% (-3.39), n 439 | 7.56% (-2.68), n 439 | 9.08% (+3.86), n 342; watts 0.28 W (-0.10), n 68 | 9.63% (+2.18), n 342; watts 0.23 W (-0.06), n 68 | 2.58% (+0.98), n 410 | 7.90% (-2.11), n 410 |
| v3.1+contention | 7.42% (+2.14), n 423 | 7.58% (+2.92), n 423 | 5.33% (+1.32), n 386; watts 0.38 W (-0.12), n 72 | 7.92% (+2.27), n 386; watts 0.33 W (-0.11), n 72 | 1.56% (+0.43), n 458 | 6.98% (+1.91), n 458 |
| ctrl N1+N2 | 7.60% (+2.25), n 423 | 7.75% (+3.03), n 423 | 5.33% (+1.32), n 386; watts 0.38 W (-0.12), n 72 | 8.16% (+2.35), n 386; watts 0.32 W (-0.11), n 72 | 1.56% (+0.43), n 458 | 7.19% (+2.02), n 458 |
| ctrl G1 | 7.42% (+2.36), n 423 | 7.61% (+3.15), n 423 | 5.33% (+1.32), n 386; watts 0.38 W (-0.12), n 72 | 7.99% (+2.37), n 386; watts 0.33 W (-0.11), n 72 | 1.56% (+0.43), n 458 | 7.00% (+2.11), n 458 |
| ctrl G1+N1 | 7.38% (+1.83), n 423 | 7.44% (+2.61), n 423 | 5.33% (+1.32), n 386; watts 0.38 W (-0.12), n 72 | 7.74% (+2.12), n 386; watts 0.32 W (-0.10), n 72 | 1.56% (+0.43), n 458 | 6.90% (+1.65), n 458 |
| ctrl F1-layout-blind | 7.49% (+2.06), n 423 | 7.62% (+2.84), n 423 | 5.33% (+1.32), n 386; watts 0.38 W (-0.12), n 72 | 7.97% (+2.23), n 386; watts 0.32 W (-0.10), n 72 | 1.56% (+0.43), n 458 | 7.06% (+1.85), n 458 |

T3 (seconds) equals T1 at the measured clock, as the declaration says (the same rms and bias on every scope: True). 'v3.1+both' equals 'v3.1+contention' on every case and quantity (True); 'v3.1+gemmLnc' is not applicable (E217 runs no gemmLnc arm). MM1-v3.1 per card (no twin):

| card | wall | counter mean | E1 | E3 | E4 |
|---|---|---|---|---|---|
| aifoundry1 card 1 | 7.16% (+1.76), n 218 | 7.20% (+2.38), n 218 | 5.23% (-0.91), n 176; watts 0.38 W (-0.12), n 72 | 1.15% (-0.18), n 248 | 6.46% (+0.96), n 248 |
| aifoundry1 card 0 | 7.56% (+2.70), n 205 | 7.90% (+3.65), n 205 | 5.42% (+3.19), n 210 | 1.93% (+1.15), n 210 | 7.40% (+3.17), n 210 |

Twins (a case whose configuration is in the model's training data at the same card and clock to 25 MHz): MM1-v3.1 63 time and 24 energy twin cases of 486, MM1-v3 63/24, MM1-v2 47/19. MM1-v3.1 on its twin cases: wall 1.22% (-0.59), n 63; on all cases: wall 6.88% (+1.85), n 486, E1 5.23% (+1.20), n 409; watts 0.37 W (-0.12), n 73.

## 3. The comparisons (each its own verdict; exact two-sided sign test on the untied cases, closer A / closer B / ties)

| comparison | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |
|---|---|---|---|---|---|
| D1 MM1-v3.1 vs MM1-v3, pooled | MM1-v3 BETTER (41/86/359, p 8.1e-05) | MM1-v3 BETTER (27/99/360, p 7.5e-11) | MM1-v3 BETTER (41/86/359, p 8.1e-05) | NOT DECIDED (53/61/368, p 0.512) | NOT DECIDED (71/74/337, p 0.868) |
| D1 MM1-v3.1 vs MM1-v3, card 1 | MM1-v3 BETTER (24/47/196, p 0.009) | MM1-v3 BETTER (16/53/198, p 9.1e-06) | MM1-v3 BETTER (24/47/196, p 0.009) | NOT DECIDED (29/21/217, p 0.322) | NOT DECIDED (35/24/208, p 0.193) |
| D1 MM1-v3.1 vs MM1-v3, card 0 | MM1-v3 BETTER (17/39/163, p 0.005) | MM1-v3 BETTER (11/46/162, p 3.3e-06) | MM1-v3 BETTER (17/39/163, p 0.005) | NOT DECIDED (24/40/151, p 0.060) | NOT DECIDED (36/50/129, p 0.161) |
| D2 MM1-v3.1 vs MM1-v2, pooled | MM1-v3.1 BETTER (221/155/110, p 0.00078) | NOT DECIDED (199/161/126, p 0.051) | MM1-v3.1 BETTER (221/155/110, p 0.00078) | MM1-v3.1 BETTER (273/64/92, p 7.2e-32) | MM1-v3.1 BETTER (229/82/118, p 3.1e-17) |
| D2 MM1-v3.1 vs MM1-v2, card 1 | MM1-v3.1 BETTER (122/77/68, p 0.002) | MM1-v3.1 BETTER (112/79/76, p 0.020) | MM1-v3.1 BETTER (122/77/68, p 0.002) | MM1-v3.1 BETTER (114/42/73, p 7.1e-09) | MM1-v3.1 BETTER (110/36/83, p 6.5e-10) |
| D2 MM1-v3.1 vs MM1-v2, card 0 | NOT DECIDED (99/78/42, p 0.133) | NOT DECIDED (87/82/50, p 0.758) | NOT DECIDED (99/78/42, p 0.133) | MM1-v3.1 BETTER (159/22/19, p 8.3e-27) | MM1-v3.1 BETTER (119/46/35, p 1.2e-08) |

D3, on the subset-mask cases (MG and SUB), each candidate as A against MM1-v3.1 as B:

| D3 | H1 wall, pooled | H1 card 1 | H1 card 0 | H2 counter mean, pooled | H2 card 1 | H2 card 0 |
|---|---|---|---|---|---|---|
| v3.1+contention vs MM1-v3.1 | MM1-v3.1 BETTER (24/42/130, p 0.036) | NOT DECIDED (14/23/61, p 0.188) | NOT DECIDED (10/19/69, p 0.136) | NOT DECIDED (28/38/130, p 0.268) | NOT DECIDED (15/22/61, p 0.324) | NOT DECIDED (13/16/69, p 0.711) |
| ctrl N1+N2 vs MM1-v3.1 | MM1-v3.1 BETTER (41/116/39, p 1.7e-09) | MM1-v3.1 BETTER (23/59/16, p 8.7e-05) | MM1-v3.1 BETTER (18/57/23, p 7.2e-06) | MM1-v3.1 BETTER (34/112/50, p 6.4e-11) | MM1-v3.1 BETTER (17/58/23, p 2.2e-06) | MM1-v3.1 BETTER (17/54/27, p 1.3e-05) |
| ctrl G1 vs MM1-v3.1 | NOT DECIDED (30/43/123, p 0.160) | NOT DECIDED (19/22/57, p 0.755) | NOT DECIDED (11/21/66, p 0.110) | NOT DECIDED (34/37/125, p 0.813) | NOT DECIDED (21/21/56, p 1.000) | NOT DECIDED (13/16/69, p 0.711) |
| ctrl G1+N1 vs MM1-v3.1 | MM1-v3.1 BETTER (43/116/37, p 6.2e-09) | MM1-v3.1 BETTER (21/63/14, p 5e-06) | MM1-v3.1 BETTER (22/53/23, p 0.00045) | MM1-v3.1 BETTER (56/103/37, p 0.00024) | MM1-v3.1 BETTER (25/58/15, p 0.00038) | NOT DECIDED (31/45/22, p 0.135) |
| ctrl F1-layout-blind vs MM1-v3.1 | NOT DECIDED (27/43/126, p 0.072) | NOT DECIDED (17/23/58, p 0.430) | NOT DECIDED (10/20/68, p 0.099) | NOT DECIDED (33/34/129, p 1.000) | NOT DECIDED (19/19/60, p 1.000) | NOT DECIDED (14/15/69, p 1.000) |

On the 48 new core-group masks alone (MG, REPORTED) the factor of 'v3.1+contention' is exactly 1 in 48 cases and the layout-blind F1's in 48 (both equal MM1-v3.1 there: every case a tie); N1+N2 vs MM1-v3.1 there: MM1-v3.1 BETTER (0/42/6, p 4.5e-13). 'v3.1+contention' against each control (REPORTED): vs ctrl N1+N2 H1 v3.1+contention BETTER (124/42/30, p 1.4e-10); vs ctrl G1 H1 NOT DECIDED (50/37/109, p 0.198); vs ctrl G1+N1 H1 v3.1+contention BETTER (104/49/43, p 1e-05); vs ctrl F1-layout-blind H1 NOT DECIDED (44/30/122, p 0.130).

D4 (group S, MM1-v3.1 with counts-e217 against the null N): Q1 MM1-v3.1 + counts-e217 BETTER (P2 True), Q2 MM1-v3.1 + counts-e217 BETTER (P4 True).

D3's H5 (J over idle with t forecast, MG and SUB, pooled; REPORTED): v3.1+contention vs MM1-v3.1 NOT DECIDED (7/11/177, p 0.481); ctrl N1+N2 vs MM1-v3.1 MM1-v3.1 BETTER (2/38/155, p 1.5e-09); ctrl G1 vs MM1-v3.1 TOO FEW (1/5/189, p 0.219); ctrl G1+N1 vs MM1-v3.1 NOT DECIDED (15/6/174, p 0.078); ctrl F1-layout-blind vs MM1-v3.1 NOT DECIDED (6/15/174, p 0.078).

## 4. Where it holds and where it misses (the declared splits, REPORTED; MM1-v3.1, no twin, pooled)

| split | wall cycles | J over idle given t (E1) | J at rest, t forecast (E4) | part A beside (card 1; card 0): T1, E1, E4 |
|---|---|---|---|---|
| 1x1x1 cells | 0.15% (n 60) | 5.80% (n 76) | 1.97% | T1 PASS 27/27, E1 PASS 48/49, E4 PASS 49/49; T1 PASS 33/33, E1 PASS 38/41, E4 PASS 41/41 |
| other shapes | 7.94% (n 363) | 5.21% (n 310) | 7.65% | T1 FAIL 152/191, E1 PASS 187/199, E4 FAIL 165/199; T1 FAIL 139/172, E1 PASS 161/169, E4 FAIL 134/169 |
| MG: the 48 new core-group masks (1x1x1) | 0.16% (n 48) | 5.36% (n 36) | 1.57% | T1 PASS 24/24, E1 PASS 24/24, E4 PASS 24/24; T1 PASS 24/24, E1 PASS 24/24, E4 PASS 24/24 |
| SUB: the other subset masks | 8.99% (n 134) | 8.72% (n 82) | 9.54% | T1 FAIL 53/70, E1 FAIL 60/71, E4 FAIL 51/71; T1 FAIL 50/64, E1 FAIL 60/71, E4 FAIL 52/71 |
| FULL: the full chip | 7.07% (n 241) | 3.71% (n 268) | 5.74% | T1 FAIL 102/124, E1 PASS 151/153, E4 PASS 139/153; T1 FAIL 98/117, E1 PASS 115/115, E4 FAIL 99/115 |
| S: the 21 new tile kinds | 0.04% (n 4) | 6.30% (n 35) | 2.45% | T1 NO DATA 0/0, E1 PASS 25/26, E4 PASS 26/26; T1 TOO FEW 4/4, E1 TOO FEW 6/9, E4 TOO FEW 9/9 |
| C: the sparse50 pools | 11.43% (n 17) | 4.81% (n 14) | 11.44% | T1 FAIL 5/11, E1 FAIL 10/12, E4 FAIL 7/12; T1 TOO FEW 3/6, E1 TOO FEW 6/6, E4 TOO FEW 2/6 |
| K: zeros, ones, random | 7.17% (n 402) | 5.24% (n 337) | 6.90% | T1 FAIL 174/207, E1 PASS 200/210, E4 FAIL 181/210; T1 FAIL 165/195, E1 PASS 187/195, E4 FAIL 164/195 |
| fp32 | 7.69% (n 209) | 6.24% (n 168) | 7.67% | T1 FAIL 89/109, E1 PASS 114/122, E4 FAIL 100/122; T1 FAIL 83/100, E1 PASS 88/97, E4 FAIL 78/97 |
| fp16 | 6.65% (n 103) | 4.58% (n 100) | 5.73% | T1 FAIL 49/60, E1 PASS 65/66, E4 PASS 61/66; T1 PASS 39/43, E1 PASS 44/46, E4 PASS 42/46 |
| int8 | 7.34% (n 111) | 4.45% (n 118) | 6.46% | T1 FAIL 41/49, E1 PASS 56/60, E4 FAIL 53/60; T1 FAIL 50/62, E1 PASS 67/67, E4 FAIL 55/67 |

**Post hoc readings (made after the read; REPORTED; they decide nothing).** Every T1, T3 and E4 miss of part A is at a shape other than 1x1x1 (True): MM1-v3.1's wall cycles are 0.15% rms on the 60 no-twin 1x1x1 cells (the 48 new core-group masks among them) and 7.94% on the 363 other no-twin cases, both on the full chip and on subset masks. Of the no-twin cases more than 10% off, 62 are over-predicted (more cycles forecast than measured) and 13 under-predicted. The E4 misses follow the time misses: 30 of card 1's 34 and 30 of card 0's 35 E4 misses are also T1 misses. The largest no-twin wall misses (MM1-v3.1, MM1-v3 and MM1-v2 beside):

| card | arm | format | kind | mask | measured cycles an op | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|---|---|---|
| card 0 | gemmL3x4x6 | fp32 | zeros | 0x44 | 1091.3 | +35.2% | +36.3% | +29.3% |
| card 1 | gemmL3x4x6 | fp32 | zeros | 0x44 | 938.9 | +28.2% | +28.9% | +24.4% |
| card 1 | gemmL8x13x12 | fp16 | random | 0x80 | 1129.7 | +20.7% | +20.1% | +2.7% |
| card 0 | gemmL2x6x10 | fp32 | zeros | 0x44 | 1349.3 | +17.8% | +16.9% | -0.4% |
| card 0 | gemmL8x14x9 | int8 | pattern:sparse50i | 0x9999 | 1864.9 | -17.6% | -17.7% | -28.7% |
| card 0 | gemmL1x15x8 | fp32 | ones | 0xb7b2effb | 1280.0 | +17.5% | +17.6% | +7.1% |
| card 0 | gemmL2x6x10 | fp32 | zeros | 0x88 | 1354.3 | +17.3% | +16.4% | -0.8% |
| card 0 | gemmL8x21x4 | int8 | random | 0xffffffff | 1341.6 | +16.0% | +15.9% | +3.3% |
| card 0 | gemmL5x15x5 | int8 | random | 0xffffffff | 1346.7 | +16.0% | +15.6% | +3.8% |
| card 0 | gemmL2x6x10 | fp32 | zeros | 0x90 | 1372.6 | +15.8% | +14.9% | -2.1% |
| card 1 | gemmL8x14x9 | int8 | pattern:sparse50i | 0x9999 | 1482.4 | -15.7% | -16.0% | -26.0% |
| card 1 | gemmL2x6x10 | fp32 | zeros | 0x110 | 1112.7 | +15.5% | +14.3% | -0.1% |

**The four zero-row tiles (REPORTED).** MM1-v3.1's J over idle given t on the 6 cases of gt125, gt25, gt875 and h_gt25, with the declared gate (the all-zero A-row share), the frozen code's literal (0, 0, 0) and the gate the count implies:

| case | measured W over idle | declared gate | literal (0, 0, 0) | count-implied gate |
|---|---|---|---|---|
| card 0 gemmL1x1x1 fp32 pattern:gt25 0xff | 8.48 W | +10.1% | +40.9% | +7.2% |
| card 1 gemmL1x1x1 fp16 pattern:h_gt25 0xffffffff | 7.28 W | -3.7% | +84.6% | -5.1% |
| card 1 gemmL1x1x1 fp32 pattern:gt125 0xffffffff | 6.31 W | +0.6% | +110.7% | -3.5% |
| card 1 gemmL1x1x1 fp32 pattern:gt25 0xffffffff | 7.42 W | +7.6% | +79.5% | +0.7% |
| card 1 gemmL1x1x1 fp32 pattern:gt875 0xffffffff | 12.45 W | -2.4% | +6.2% | -2.4% |
| card 1 gemmL4x8x8 fp32 pattern:gt25 0xffffffff | 6.12 W | -0.2% | +32.8% | -3.4% |

**Group C, the sparse50 pools priced as the committed sparse50 kind (REPORTED):** MM1-v3.1 J over idle given t 4.81% (n 14; watts 1.03 W, n 4), J at rest given t 2.15%, wall cycles 11.11% (n 18, twins included).

## 5. The nominal footing (frozen by decl-e217 before any datum; scored beside by the same rules; REPORTED, deciding nothing)

The same models at the declared nominal conditions (card 1 600 MHz, 0.517 V, die 60 C; card 0 800 MHz, the model's own volts, die 55 C): VERDICT FAIL, part A FAIL (aifoundry1 card 1 T1, aifoundry1 card 1 T3, aifoundry1 card 1 E4, aifoundry1 card 0 T1, aifoundry1 card 0 T3, aifoundry1 card 0 E1, aifoundry1 card 0 E2, aifoundry1 card 0 E3, aifoundry1 card 0 E4), part S PASS. MM1-v3.1 no twin, pooled: wall 7.39% (+2.29), n 423, E1 9.76% (+8.11), n 386; watts 0.33 W (-0.03), n 72, E3 3.11% (+2.30), n 458. The nominal die sits above the measured start dies (card 1 44.0-47.5 C against 60 C, card 0 42.0-44.0 C against 55 C), so the nominal energy reads high, as the declaration expected.

On the nominal footing, pooled: D1 H1 MM1-v3 BETTER (42/86/358, p 0.00013), H4 NOT DECIDED (72/55/355, p 0.155); D2 H1 MM1-v3.1 BETTER (220/156/110, p 0.001), H4 MM1-v2 BETTER (113/217/99, p 1.1e-08), H5 MM1-v2 BETTER (99/230/100, p 3.8e-13) (MM1-v2 has no die term, so the nominal die does not move it).

## 6. The order of hashes and times (Pacific), and the checks

- decl-e217's declaration hashed 11:35:59-11:36:23, FROZEN.txt 11:37:53, COUNTS-FROZEN.txt 12:22:24, posted #13.1.1 (12:26:07); E217's first card command 14:41:14.595 (a1c1-S1).
- This lane, Thu 19 Nov 2026: every frozen file's sha256 checked at 20:52:55 (MM1-v3.1 64/64, its counts 71/71, MM1-v3 170/170, MM1-v2 114/114, the layout term 25/25 and its note 6/6, the gemmLnc term 22/22, the posted term files, verify-lay's three files, FROZEN.txt, COUNTS-FROZEN.txt, the declaration, the nominal forecasts and the counts tables equal to their posted or listed sha256; decl-e217's land 81/81); the conditions read 20:53:41 (only the declared start-of-run fields); the forecasts made 20:56:26-20:59:55 and hashed 21:00:04 (forecasts-blind-e217.csv ed81a5dbfe3c18a4..., .json 74aa5a0314cc5d30...); the scorer tested on two stand-in days 21:06:17-21:06:19 and hashed 21:06:37 (s03_score.py 2921d487dbe21898...); the read and the scores 21:06:44.
- **The procedure check:** this lane's forecast code, run at the declared nominal conditions, re-makes decl-e217's frozen nominal forecasts bit for bit (SAME PROCEDURE: every field bit-equal: MM1-v3.1 5015, MM1-v3 5015, MM1-v2 3947 fields, 0 differ), so the measured-conditions forecasts are the declared procedure with only the conditions changed. The layout factors equal the frozen nominal ones 2,430 of 2,430.
- **The loader check:** the scorer's own selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all) on the same bytes: 599 runs, 0 field differences, equal True. The seven data files read are byte-equal to the ones the conditions step read (True).
- **The recheck** (independent code path, a fresh read): T1, T3 and E4 per card, the wall rms per card, Q1 and D1's H1 counts all equal the scorer's (True).
- **Counts:** 599 listed runs (544 arm + 55 anchor; nulls left out), 599 with time, 595 with energy (4 capped: card 1 0, card 0 4; energy not read there), 486 cases (482 with energy, 73 watts cases).

## 7. Disclosures, gaps and what was not run

- **Earlier reads.** This lane's brief quoted the data lanes' result summaries (aggregate board maxima, clock-sample counts, the anchors' joule and time ranges) before the read. No per-run measurement was read before the forecasts and the scorer were hashed, and nothing in the procedure could use them: the predictors, the terms, the counts and the scoring rules were frozen before any E217 datum.
- **Labels.** Each session's label is decided by its T0 (its session id, a start-of-run field) against the freeze post; the first card command times in the table come from each data folder's README, read after the scores, and agree (7 of 7 found, each 3.5-4.3 s after T0).
- **NOT RUN here:** no second, independent scorer; the per-run figures are REPORTED beside the case figures only; the model session's sealed E217 forecast was not read or scored by this lane.
- decl-e217's own land (`../blind-e217/`, the declaration, the nominal forecasts and counts-e217) is not on GitHub main at this writing: it lands first or together with this folder.

## 8. Files

- `forecasts-blind-e217.csv` / `.json`: the frozen measured-conditions forecasts, one row a run, every declared model (W over idle at a measured op time t is W_A + W_B / t). `inputs/`: the conditions read (start-of-run fields only), each model's record, the layout factors, the nominal procedure check.
- `scores/scores-blind-e217.json` (every figure, both footings, the labels), `scores/scores-blind-e217.txt` (the summary), `cases/scores-blind-e217-cases.csv` and `-runs.csv` (per case and per run errors), `scores/posthoc-e217.json` (post hoc), `scores/recheck.json`.
- `scripts/` (the box's paths replaced; `scripts/SCRUB-MAP.json` maps each to its sha256 as run), `logs/` (progress, the hash records, each step's output), `SHA256SUMS`.

To reproduce: from a work copy of GitHub main with decl-e217's land at work/decl/, run s00_setup.sh, then s02a_conditions.py, s02b_chain.sh, s02d_nominal_check.py, s02c_merge.py, s03_score.py, s03p_posthoc.py and s04_recheck.py, each as `/usr/bin/python3 -I -B <script> <lane dir>` inside the CPU slot (run_slot.sh), with the paths put back as SCRUB-MAP.json says.
