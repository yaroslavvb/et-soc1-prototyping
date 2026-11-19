# unread-e214: MM1-v3.1, MM1-v3 and MM1-v2 scored UNREAD on E214 (the model session's third matmul sweep, 593 runs on aifoundry1's two cards)

*Round Q225 (track A), lane unread-e214, Thu 19 Nov 2026, at the desk on aifoundry2: no card, no simulator, nothing measured here. Every numerical job ran in the round's CPU slots single-threaded; interpreter `/usr/bin/python3` 3.12.3 (`-I -B`), numpy 1.26.4.*

**Label: UNREAD.** The three models are frozen and unchanged (MM1-v3.1 landed 2c971828, MM1-v3 b1493082, MM1-v2 3ca4b717), with the switch counts frozen (MM1-v3.1's `counts/`, 3e8991d0; `counts-e214/`, SHA256SUMS 4c39d0d3..., verified), before this lane read any E214 measurement. Not blind: E214's data existed (committed Wed 18 Nov 2026 16:44-21:06 PST, notes 10f662e3) and its data lanes had read them (section 7). **No E214 point entered any of the three fits** (section 6). Error = forecast / measured - 1; rms and signed mean (bias) in %; a case is (card, shape, format, kind, mask) over that card's sessions, its error the mean of its runs'.

The owner's words that started the matmul model (Mon 16 Nov 2026; "matte mold" is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained."

## 1. The order, hashed (Pacific, Thu 19 Nov 2026; `logs/progress.txt`)

| step | time | files (sha256) |
|---|---|---|
| 1. DECLARED (before any E214 measurement) | 10:42:28 written, 10:42:41 logged | `DECLARED-unread-e214.md` 82288925fc8b44a1cb645fbf751c60a16a86ff482d872ba16642209f9cc75e1d, `DECLARED-unread-e214.json` ef311b7186e849928c7b0394415f75426d8d36e6dc6ba0bb5402410eb36bbd88 |
| 2. conditions read (clock, minion volts, die at start only) | 10:43:04 | `inputs/step2/conditions-e214.json` 8b17ce5bd6e94d95bbe4a6ded751a2651bae7ae30af11fed7a38fd56f5801fb8 |
| 2. FORECAST (the frozen predictors, unchanged) | 10:44-10:46:14 written, 10:46:42 logged | `forecasts-unread-e214.csv` 0d15bd2beaad7978cf277bcb3f49be38c426267f04213db53b83d89c41470870, `forecasts-unread-e214.json` 60cd9d208ba4734fca3c5360d8f79b2af4f12c82fcf50b592206ced82bb38ece |
| the scorer frozen (after a stand-in code test) | 10:49:30 | `scripts/s03_score.py` (the lane's copy) 45948afef8b5db9a7436cff0e6085daed7375bc3e43fb67d4dc97d32e2b2f4dc |
| 3. READ AND SCORED | 10:49:34 | `scores-unread-e214.json` a43b5c67d8dd65b51209c3deb6ce4444336da162d8316f05c8f5ecefbfbd211b, `-cases.csv` 3840e93fc5c8745507aabc1827e4e640aa8194f80c9e5de46596fe84851a17da, `-runs.csv` e7d1b521d77e4baa44c5dd8b1d986c7c8bc512394f691bb809ae12a4748231dd |
| post hoc reading (REPORTED) | 10:50:23 | `posthoc-time-misses.json` 89d193338d1127ec2bf0d6b1dbc5969cd11c43d3e0c789d085feafe4e3f978d9 |
| recheck (independent path) | 10:51:07 | `recheck.json` 78fa826d07b9690daa1039e181f723be0c1c09a3a26c646b1bb8f1f85b57e4d9 |

Every step-1, step-2 and step-3 file is listed with its sha256 in `logs/step1-sha256.txt`, `logs/step2-sha256.txt` and `logs/step3-sha256.txt`. The scripts in `scripts/` are the lane's with the box's paths replaced by `<W>`, `<LAB>` and `<SCRATCH>`; the sha256 in the logs are of the lane's own copies.

## 2. The verdict (the declared pass rule, decided by `scripts/s03_score.py`): **FAIL**

- **Part A, MM1-v3.1 by E215's rule form (its bands, 90% bar and watts form; the per-case error in MM1's convention: section 9) on the no-twin cases: FAIL.** Failing: aifoundry1 card 1 T1, aifoundry1 card 1 T3, aifoundry1 card 0 T1, aifoundry1 card 0 T3, aifoundry1 card 0 E4. Each case passes when |error| is within its band (E1, E2: watts at a watts case); a rule passes when at least 90% of its cases pass.
- **Part S, the switch route with the new counts against the null: PASS** (P1-P4 all hold).

| rule | card 1 (band) | card 1 pass | card 0 (band) | card 0 pass |
|---|---|---|---|---|
| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |
| T2 | 13% | **PASS** 215/224 (96.0%) | 16% | **PASS** 193/201 (96.0%) |
| T3 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |
| E1 | 14%, 0.56 W | **PASS** 257/265 (97.0%) | 11%, 0.56 W | **PASS** 201/209 (96.2%) |
| E2 | 14%, 0.56 W | **PASS** 256/265 (96.6%) | 13%, 0.56 W | **PASS** 197/209 (94.3%) |
| E3 | 5% | **PASS** 263/265 (99.2%) | 5% | **PASS** 205/209 (98.1%) |
| E4 | 10% | **PASS** 243/265 (91.7%) | 10% | **FAIL** 179/209 (85.6%) |

T1: wall cycles; T2: the counter's mean; T3: seconds a GEMM (identical to T1 here: the reducer's seconds and cycles share the wall time, and every forecast is made at the run's measured clock); E1: J over idle given t; E2: J over idle with t forecast; E3, E4: J with the card at rest, given t and with t forecast. The bands are 2 x MM1-v3.1's own held-out error (card 1's equal E215 arm B's registered bands).

**At MM1-v3.1's bands (on MM1-v3.1's no-twin cases), REPORTED beside:** MM1-v3 card 1: E1 PASS 253/265, E2 PASS 251/265, E3 PASS 262/265, E4 PASS 248/265, T1 FAIL 196/224, T2 PASS 213/224, T3 FAIL 196/224; MM1-v3 card 0: E1 PASS 202/209, E2 PASS 195/209, E3 PASS 205/209, E4 FAIL 181/209, T1 FAIL 178/201, T2 PASS 194/201, T3 FAIL 178/201; MM1-v2 card 1: E1 PASS 195/212, E2 PASS 193/212, E3 PASS 209/212, E4 FAIL 172/212, T1 FAIL 173/224, T2 FAIL 198/224, T3 FAIL 173/224; MM1-v2 card 0: E1 FAIL 157/189, E2 FAIL 167/189, E3 PASS 185/189, E4 FAIL 153/189, T1 FAIL 160/201, T2 PASS 184/201, T3 FAIL 160/201.

## 3. The errors, per case (no configuration twin; all cases and twins beside)

**aifoundry1 card 1**

| quantity | MM1-v3.1 no twin | MM1-v3 no twin | MM1-v2 no twin | MM1-v3.1 all | MM1-v3.1 twins |
|---|---|---|---|---|---|
| T1 wall cycles | 6.35% (+0.72), n 224 | 6.19% (+0.42), n 228 | 7.90% (-3.26), n 243 | 5.60% (+0.43), n 297 | 1.96% (-0.48), n 73 |
| T2 counter mean | 7.09% (+0.25), n 224 | 6.97% (-0.04), n 228 | 8.41% (-3.77), n 243 | 6.27% (-0.09), n 297 | 2.46% (-1.12), n 73 |
| T3 seconds a GEMM | 6.35% (+0.72), n 224 | 6.19% (+0.42), n 228 | 7.90% (-3.26), n 243 | 5.60% (+0.43), n 297 | 1.96% (-0.48), n 73 |
| E1 J over idle given t (3 W and above) | 6.00% (-1.20), n 216 | 6.28% (-0.98), n 217 | 8.16% (+0.78), n 175 | 5.71% (-1.17), n 247 | 3.03% (-0.99), n 31 |
| E1 J over idle given t, watts cases | 0.248 W (-0.030), n 49 | 0.255 W (-0.080), n 49 | 0.219 W (-0.023), n 47 | 0.245 W (-0.030), n 50 | 0.040 W (-0.040), n 1 |
| E2 J over idle, t forecast (3 W and above) | 6.44% (-1.02), n 216 | 6.74% (-0.85), n 217 | 8.70% (-0.10), n 175 | 6.12% (-1.02), n 247 | 3.20% (-1.05), n 31 |
| E2 J over idle, t forecast, watts cases | 0.235 W (-0.022), n 49 | 0.237 W (-0.070), n 49 | 0.200 W (+0.028), n 47 | 0.233 W (-0.022), n 50 | 0.037 W (-0.037), n 1 |
| E3 J at rest given t | 1.20% (-0.17), n 265 | 1.28% (-0.14), n 266 | 1.67% (-0.10), n 222 | 1.17% (-0.18), n 297 | 0.81% (-0.21), n 32 |
| E4 J at rest, t forecast | 5.43% (+0.19), n 265 | 5.41% (+0.02), n 266 | 7.69% (-3.05), n 222 | 5.18% (+0.13), n 297 | 2.17% (-0.40), n 32 |

**aifoundry1 card 0**

| quantity | MM1-v3.1 no twin | MM1-v3 no twin | MM1-v2 no twin | MM1-v3.1 all | MM1-v3.1 twins |
|---|---|---|---|---|---|
| T1 wall cycles | 6.98% (+1.59), n 201 | 6.88% (+1.47), n 201 | 8.24% (-3.01), n 219 | 6.66% (+1.41), n 221 | 0.81% (-0.33), n 20 |
| T2 counter mean | 7.61% (+1.36), n 201 | 7.52% (+1.24), n 201 | 8.55% (-3.20), n 219 | 7.26% (+1.24), n 221 | 0.70% (-0.06), n 20 |
| T3 seconds a GEMM | 6.98% (+1.59), n 201 | 6.88% (+1.47), n 201 | 8.24% (-3.01), n 219 | 6.66% (+1.41), n 221 | 0.81% (-0.33), n 20 |
| E1 J over idle given t (3 W and above) | 4.89% (+2.27), n 209 | 4.67% (+2.17), n 209 | 7.68% (+5.14), n 197 | 4.84% (+2.18), n 218 | 3.50% (+0.15), n 9 |
| E1 J over idle given t, watts cases | - | - | - | - | - |
| E2 J over idle, t forecast (3 W and above) | 7.35% (+3.02), n 209 | 7.20% (+2.88), n 209 | 8.86% (+2.68), n 197 | 7.24% (+2.90), n 218 | 3.72% (-0.01), n 9 |
| E2 J over idle, t forecast, watts cases | - | - | - | - | - |
| E3 J at rest given t | 1.79% (+0.80), n 209 | 1.76% (+0.78), n 209 | 2.75% (+1.80), n 197 | 1.79% (+0.77), n 218 | 1.58% (+0.05), n 9 |
| E4 J at rest, t forecast | 6.47% (+1.95), n 209 | 6.41% (+1.85), n 209 | 7.70% (-1.09), n 197 | 6.35% (+1.86), n 218 | 2.00% (-0.23), n 9 |

**pooled**

| quantity | MM1-v3.1 no twin | MM1-v3 no twin | MM1-v2 no twin | MM1-v3.1 all | MM1-v3.1 twins |
|---|---|---|---|---|---|
| T1 wall cycles | 6.66% (+1.13), n 425 | 6.52% (+0.91), n 429 | 8.06% (-3.14), n 462 | 6.08% (+0.85), n 518 | 1.77% (-0.45), n 93 |
| T2 counter mean | 7.34% (+0.78), n 425 | 7.23% (+0.56), n 429 | 8.48% (-3.50), n 462 | 6.71% (+0.48), n 518 | 2.21% (-0.90), n 93 |
| T3 seconds a GEMM | 6.66% (+1.13), n 425 | 6.52% (+0.91), n 429 | 8.06% (-3.14), n 462 | 6.08% (+0.85), n 518 | 1.77% (-0.45), n 93 |
| E1 J over idle given t (3 W and above) | 5.48% (+0.51), n 425 | 5.55% (+0.56), n 426 | 7.91% (+3.09), n 372 | 5.32% (+0.40), n 465 | 3.15% (-0.73), n 40 |
| E1 J over idle given t, watts cases | 0.248 W (-0.030), n 49 | 0.255 W (-0.080), n 49 | 0.219 W (-0.023), n 47 | 0.245 W (-0.030), n 50 | 0.040 W (-0.040), n 1 |
| E2 J over idle, t forecast (3 W and above) | 6.90% (+0.97), n 425 | 6.97% (+0.98), n 426 | 8.79% (+1.37), n 372 | 6.67% (+0.81), n 465 | 3.32% (-0.82), n 40 |
| E2 J over idle, t forecast, watts cases | 0.235 W (-0.022), n 49 | 0.237 W (-0.070), n 49 | 0.200 W (+0.028), n 47 | 0.233 W (-0.022), n 50 | 0.037 W (-0.037), n 1 |
| E3 J at rest given t | 1.49% (+0.26), n 474 | 1.51% (+0.27), n 475 | 2.24% (+0.79), n 419 | 1.46% (+0.23), n 515 | 1.03% (-0.15), n 41 |
| E4 J at rest, t forecast | 5.91% (+0.97), n 474 | 5.87% (+0.82), n 475 | 7.69% (-2.13), n 419 | 5.70% (+0.86), n 515 | 2.13% (-0.36), n 41 |

Twins (configuration in the model's training set from E206, E208, E212 and E213 on these cards): MM1-v3.1 93 time and 41 energy cases of 518; MM1-v3 89 / 40; MM1-v2 56 / 21. MM1-v2 prices energy for random, zeros and ones only (98 runs NOT FORECAST in energy).

**By card and format** (MM1-v3.1, no twin; MM1-v3 and MM1-v2 in `scores-unread-e214.json` > by_card_format_kind):

| card | format | wall | J over idle given t (3 W and above) | J at rest given t |
|---|---|---|---|---|
| aifoundry1 card 1 | fp32 | 6.57% (+0.70), n 122 | 5.67% (-1.52), n 108 | 0.99% (-0.17), n 141 |
| aifoundry1 card 1 | fp16 | 5.98% (+1.73), n 41 | 4.20% (+0.02), n 46 | 1.08% (+0.12), n 49 |
| aifoundry1 card 1 | int8 | 6.15% (+0.10), n 61 | 7.50% (-1.53), n 62 | 1.58% (-0.37), n 75 |
| aifoundry1 card 0 | fp32 | 6.89% (+1.34), n 105 | 5.08% (+2.36), n 104 | 1.59% (+0.70), n 104 |
| aifoundry1 card 0 | fp16 | 6.74% (+1.91), n 28 | 5.28% (+3.22), n 31 | 2.19% (+1.35), n 31 |
| aifoundry1 card 0 | int8 | 7.21% (+1.83), n 68 | 4.41% (+1.74), n 74 | 1.88% (+0.71), n 74 |

## 4. The comparisons (exact two-sided sign test, alpha 0.05; per case; ties at each card's replicate floor)

| pair | rule | pooled: A closer / B closer / ties, p | card 1 | card 0 |
|---|---|---|---|---|
| MM1-v3.1 vs MM1-v3 | H1 | **NOT DECIDED** 61/71/386, p 0.43 | **NOT DECIDED** 35/37/225, p 0.91 | **NOT DECIDED** 26/34/161, p 0.37 |
| MM1-v3.1 vs MM1-v3 | H2 | **NOT DECIDED** 62/72/384, p 0.44 | **NOT DECIDED** 35/38/224, p 0.82 | **NOT DECIDED** 27/34/160, p 0.44 |
| MM1-v3.1 vs MM1-v3 | H3 | **NOT DECIDED** 61/71/386, p 0.43 | **NOT DECIDED** 35/37/225, p 0.91 | **NOT DECIDED** 26/34/161, p 0.37 |
| MM1-v3.1 vs MM1-v3 | H4 | **NOT DECIDED** 48/55/412, p 0.55 | **NOT DECIDED** 23/31/243, p 0.34 | **NOT DECIDED** 25/24/169, p 1 |
| MM1-v3.1 vs MM1-v3 | H5 | **NOT DECIDED** 51/72/392, p 0.071 | **NOT DECIDED** 26/36/235, p 0.25 | **NOT DECIDED** 25/36/157, p 0.2 |
| MM1-v3.1 vs MM1-v2 | H1 | **MM1-v3.1 BETTER** 284/154/80, p 5.3e-10 | **MM1-v3.1 BETTER** 153/83/61, p 6.1e-06 | **MM1-v3.1 BETTER** 131/71/19, p 2.9e-05 |
| MM1-v3.1 vs MM1-v2 | H2 | **MM1-v3.1 BETTER** 278/155/85, p 3.6e-09 | **MM1-v3.1 BETTER** 154/83/60, p 4.7e-06 | **MM1-v3.1 BETTER** 124/72/25, p 0.00025 |
| MM1-v3.1 vs MM1-v2 | H3 | **MM1-v3.1 BETTER** 284/154/80, p 5.3e-10 | **MM1-v3.1 BETTER** 153/83/61, p 6.1e-06 | **MM1-v3.1 BETTER** 131/71/19, p 2.9e-05 |
| MM1-v3.1 vs MM1-v2 | H4 | **MM1-v3.1 BETTER** 270/73/97, p 1e-27 | **MM1-v3.1 BETTER** 116/50/76, p 3.2e-07 | **MM1-v3.1 BETTER** 154/23/21, p 5.4e-25 |
| MM1-v3.1 vs MM1-v2 | H5 | **MM1-v3.1 BETTER** 236/103/101, p 3.8e-13 | **MM1-v3.1 BETTER** 116/52/74, p 8.7e-07 | **MM1-v3.1 BETTER** 120/51/27, p 1.4e-07 |
| MM1-v3 vs MM1-v2 | H1 | **MM1-v3 BETTER** 276/147/95, p 3.6e-10 | **MM1-v3 BETTER** 146/82/69, p 2.7e-05 | **MM1-v3 BETTER** 130/65/26, p 3.8e-06 |
| MM1-v3 vs MM1-v2 | H2 | **MM1-v3 BETTER** 269/149/100, p 4.6e-09 | **MM1-v3 BETTER** 145/82/70, p 3.5e-05 | **MM1-v3 BETTER** 124/67/30, p 4.5e-05 |
| MM1-v3 vs MM1-v2 | H3 | **MM1-v3 BETTER** 276/147/95, p 3.6e-10 | **MM1-v3 BETTER** 146/82/69, p 2.7e-05 | **MM1-v3 BETTER** 130/65/26, p 3.8e-06 |
| MM1-v3 vs MM1-v2 | H4 | **MM1-v3 BETTER** 269/71/100, p 2.9e-28 | **MM1-v3 BETTER** 119/47/76, p 2.2e-08 | **MM1-v3 BETTER** 150/24/24, p 1.8e-23 |
| MM1-v3 vs MM1-v2 | H5 | **MM1-v3 BETTER** 238/97/105, p 8.1e-15 | **MM1-v3 BETTER** 116/51/75, p 5.3e-07 | **MM1-v3 BETTER** 122/46/30, p 3.9e-09 |

H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t, H5 J over idle with t forecast. Over the cases that are twins for neither model (REPORTED, `scores-unread-e214.json` > head_to_head) every verdict is the same. MM1-v3.1's time form is MM1-v3's refitted (its declaration's outcome), so the two differ by less than either's error and most cases tie.

## 5. The switch-pattern arms (group S: E214's 20 new tile kinds, 33 arms, 54 runs), Q218's test

- **Q1, W over idle given t** (33 cases at 3 W and above): MM1-v3.1 + the counts **7.76% (+4.41), n 33** against the null N (each format's mean of zeros, ones and random, the same model) 28.05% (-4.18), n 33; MM1-v3.1 closer in 29, N in 3, 1 tie; p = 2.6e-06. N2 (ones and random, REPORTED) 43.61% (+22.59), n 33.
- **Q2, the share of D** (E210's metric; 28 cases with a random and a zeros case of the same card, shape, format and mask): **7.57% (+4.19), n 28 of D** against N's 32.44% (-15.26), n 28; closer 24 / 4; p = 0.00018.
- By format (Q1): fp16 8.48% (+6.61), n 7; fp32 5.78% (+2.95), n 14; int8 9.21% (+4.84), n 12. By card: aifoundry1 card 0 11.29% (+10.17), n 8; aifoundry1 card 1 6.23% (+2.57), n 25.
- MM1-v3 + the same counts (REPORTED): Q1 10.03% (+1.61), n 33 vs N 28.03% (-4.32), n 33 (27/6, p 0.00032); Q2 9.45% (+1.37), n 28 of D vs 32.40% (-15.13), n 28: PASS by the same rule.
- **The sp_ar4 gate** (declared before the read: arow50's, (0.5, 0, 0)): J over idle given t gemmL1x1x1 declared gate -5.5%, the frozen literal (no gate, REPORTED) +38.1%; gemmL4x8x8 declared gate -5.2%, the frozen literal (no gate, REPORTED) +17.5% (MM1-v3.1).
- Group C, the sparse50 pools at the committed sparse50 row (REPORTED): MM1-v3.1 J over idle given t 5.91% (-3.08), n 40, MM1-v3 5.29% (-1.32), n 40.

## 6. Did any E214 point enter a fit? No

NO E214 point entered MM1-v3.1's fit, nor MM1-v3's or MM1-v2's: (a) no E214 token in any model's inputs or loaders (MM1-v3.1 28 files, MM1-v3 115, MM1-v2 86: 0 hits); (b) no E214 id in the landed point records (points_time / points_energy of each model; MM1-v3.1's experiments E105-E213); (c) by git, E214 a1c0-S1's data commit 3b3e4182 (16:44:33 PST) was ON GitHub main f0d58c84 when MM1-v3.1's fit started (17:02:54 PST, by `../out/run.log`), but data_v31.py reads only vendored inputs (inputs/ and ../v3/inputs/) and none is E214's; its README section 0: "E214 ... enters only by a dated amendment (none was made)". Every other E214 session was committed after the fit started. MM1-v3 (landed b1493082, fitted at main 58f01105) and MM1-v2 (3ca4b717) predate every E214 datum. So every E214 point is unread for all three models.

## 7. Earlier reads of E214 (disclosed in the declaration, section g)

- **MM1 model lanes**: no MM1-v3.1 lane read an E214 measurement (section a2); MM1-v3 and MM1-v2 predate it. So, unlike Q218 (where MM1-v3's design lanes had tabulated some of E212's runs), no lane that shaped any of the three models read an E214 measurement (fit-v31's E215 never-run scan, after its final fit, read E214's files for configuration tokens only: the never-run scans line below).
- **data lanes (read every E214 measurement)**: data-e214 (Q220): rsynced each released session read-only, checked it (C0-C9, W), reduced it with the registered reducer, committed it; fix-e214d (Q220): dated note 1 in each data folder (the checker's planning line, a1c1-S1's die reference, check K's lines); verify-e214d (Q220): re-derived every session from its raw files (183,450 numeric leaves)
- **named E214 without reading its data**: card-e213b2, ready-e213b2 (Q219): E214's kit folder by name (before any E214 session); counts-e214, verify-counts-e214 (Q225): arms.json and the tiles only: "No E214 measurement ... was read"; lnc-energy (Q225): "No E214 data file was read" (E214 holds no gemmLnc arm); reg-e214, verify-reg-e214, land-reg-e214 (Q220): the registration, before any E214 datum; report-v2-draft (Q226): E214's run count and card-minutes from data-e214's result; E214's unread score PENDING; the orchestrator (CONTEXT 126-129, the Discussion, the status page): claims and releases (runs, card-minutes, no stop); no measurement
- **never-run scans (configuration tokens only)**: E215's scans (fit-v31's e215_v31.py scan, reg-e215, verify-e215: "81,355 files, E214 included") and ready-e213b2's step 6n read E214's planned or committed arm names
- **parser tests (raw host records, no model, no number reported)**: kit-e215 (Q224), verify-e215, fix-e215, ready-e215: E215 kit's real-bytes desk test RB-E214 read the 4 committed card-1 sessions' 376 host stdouts (5,951 records) through the host-record parser; printed counts only (tools/claims-v3/e215/logs/realbytes-e215.txt)
- **search**: scripts/s01g_search.py over 10507 lane files (scripts, results, progress logs; card-e215 lanes and E215 data paths skipped): lanes naming an E214 data token: ['card-e213b2', 'counts-e214', 'data-e214', 'fix-e214d', 'kit-e215', 'land-reg-e214', 'lnc-energy', 'ready-e213b2', 'reg-e214', 'verify-counts-e214', 'verify-e214d', 'verify-reg-e214']
- **the model session (its own box)**: ran and reduced every E214 session and sealed its own forecasts (27bf4e19, 804e269b); its models are not scored here

## 8. Post hoc: where MM1-v3.1's time misses sit (REPORTED; read after the scores, deciding nothing)

55 of 425 no-twin cases miss T1's band. No-twin wall rms by group (MM1-v3.1 / MM1-v3 / MM1-v2):

| group | MM1-v3.1 | MM1-v3 | MM1-v2 | T1 misses |
|---|---|---|---|---|
| mask: full chip | 6.35% (+2.00), n 281 | 6.17% (+1.76), n 281 | 6.80% (-1.80), n 281 | 31 |
| mask: subset mask | 7.21% (-0.57), n 144 | 7.23% (-0.72), n 144 | 10.59% (-5.96), n 144 | 24 |
| KB: KB 1 | 4.74% (+0.01), n 83 | 4.86% (-0.03), n 83 | 7.89% (-5.57), n 83 | 1 |
| KB: KB 2-4 | 7.34% (+3.11), n 73 | 7.00% (+2.90), n 73 | 6.04% (+1.28), n 73 | 13 |
| KB: KB 5-16 | 7.08% (+1.10), n 253 | 6.97% (+0.82), n 253 | 8.96% (-3.59), n 253 | 41 |
| KB: KB > 16 | 4.79% (-1.61), n 16 | 4.97% (-1.73), n 16 | 7.85% (-5.44), n 16 | 0 |
| NB: NB 1 | 4.25% (-1.93), n 46 | 4.19% (-1.73), n 46 | 6.06% (-1.31), n 46 | 1 |
| NB: NB 2-4 | 6.00% (+0.85), n 144 | 6.24% (+0.91), n 144 | 7.89% (-2.01), n 144 | 14 |
| NB: NB > 4 | 7.38% (+1.90), n 235 | 7.09% (+1.44), n 235 | 8.87% (-4.32), n 235 | 40 |
| depth: past the first sweep's largest K | 5.92% (+1.82), n 40 | 5.99% (+1.69), n 40 | 6.10% (-1.95), n 40 | 3 |
| kind: zeros | 6.95% (+1.04), n 215 | 6.85% (+0.80), n 215 | 9.12% (-3.54), n 215 | 30 |
| kind: random | 6.74% (+0.93), n 105 | 6.62% (+0.67), n 105 | 7.83% (-3.72), n 105 | 15 |
| kind: ones | 5.97% (+1.37), n 68 | 5.86% (+1.30), n 68 | 6.88% (-1.63), n 68 | 6 |
| kind: sparse50 pools | 6.07% (+1.95), n 34 | 5.91% (+1.75), n 34 | 6.80% (-2.98), n 34 | 4 |
| top family: blind | 6.57% (+2.19), n 254 | 6.44% (+2.00), n 254 | 7.37% (-2.25), n 254 | 32 |
| top family: mech | 6.88% (-0.45), n 166 | 6.80% (-0.71), n 166 | 9.61% (-4.77), n 166 | 23 |
| tag: MQ2-mixed | 9.57% (-0.38), n 20 | 9.57% (-1.25), n 20 | 16.15% (-13.61), n 20 | 8 |
| tag: bl-held | 9.95% (+8.28), n 20 | 10.30% (+8.58), n 20 | 7.89% (+6.18), n 20 | 7 |
| tag: bl-mixed | 8.80% (+5.50), n 22 | 8.00% (+4.70), n 22 | 5.94% (+0.72), n 22 | 7 |
| tag: MQ6 | 1.48% (-1.07), n 19 | 1.51% (-1.11), n 19 | 7.46% (-6.08), n 19 | 0 |
| tag: bl-L3 | 1.17% (-0.14), n 15 | 1.20% (-0.11), n 15 | 7.02% (-4.97), n 15 | 0 |

The largest misses (MM1-v3.1 / MM1-v3 / MM1-v2): 3x4x6-fp32-zeros-s8 +18.2 / +19.1 / +15.3%; 2x6x10-fp32-zeros-m44 +17.9 / +16.9 / -0.3%; 10x4x3-int8-sparse50i +16.2 / +17.0 / +13.7%; 2x6x10-fp32-zeros-mc +16.0 / +15.1 / -1.9%; 8x4x3-int8-ones +15.9 / +16.7 / +13.5%; 4x4x8-int8-rnd-s24 -15.8 / -16.1 / -15.3%; 3x14x6-fp32-zeros +15.7 / +15.5 / +5.6%; 4x14x6-int8-sparse50i +15.6 / +15.4 / +3.9%; 16x4x2-fp32-zeros +15.4 / +16.2 / +14.6%; 3x5x6-fp32-ones-m7777 +15.3 / +14.7 / +10.7%; 7x14x8-int8-zeros +14.8 / +14.8 / +5.3%; 2x11x8-int8-rnd-s24 +14.7 / +14.6 / +3.6%. 45 of the 55 misses are over-forecasts (MM1-v3.1 slower than the card), mostly mid-depth shapes (KB 2-16, NB above 4) on both cards; 10 are under-forecasts, most on spread or offset masks (0x11111111, 0x1111, the 24-shire 4x4x8 int8 pair). KB 1, deep K past the first sweep's largest, the L3 ladder (bl-L3) and the MQ6 pairs hold to 1-5%. MM1-v3 misses the same cases (its time form is the same); MM1-v2 is closer on several full-chip zeros shapes and worse on the masks.

## 9. Departures, gaps and NOT RUN

- The pass rule is this lane's, declared before the read: E215's registered rule form (bands, 90%, watts at points under 3 W) applied to an unread sweep, plus Q218's switch test. One departure from E215's form: the per-case error is the declared MM1 convention (forecast / measured - 1, the mean of a case's runs' errors, as the Label paragraph says), not E215's scorer's |measured case mean / forecast - 1|; under E215's literal form (verify-unread-e214's reading, REPORTED) the same five rules fail and the others pass (card 1 T1 and T3 198/224, card 0 T1 and T3 175/201 and E4 182/209), so the verdict does not depend on the error's direction. Card 0's bands were computed by E215's own code from MM1-v3.1's record (card 0's B2); its watts band and ties use E212 a1c0-S1/S2's replicate spread (no E213 or E215 arm ran on card 0).
- T3 equals T1 identically in this run form (section 2); both are printed.
- MM1-v2: energy NOT FORECAST for the 98 runs of new tiles and sparse50 pools (it prices random, zeros and ones only), as MM1-v3's caller of MM1-v2 does.
- The sp_ar4 gate is a declared input (arow50's), not the frozen code's literal reading of an unknown kind name; both are printed.
- The scorer was tested on a stand-in day built from the forecasts alone before the read (its outputs kept apart, never a result); it was not changed after the read. One print label beside a sha256 in `scripts/s03_score.py` was edited at 10:49:13, after that stand-in code test (10:48:57) and before its freeze hash 45948afe (10:49:30), so the frozen bytes are not the tested bytes; no computation changed (verify-unread-e214's reading). The post hoc reading was re-run once after the read with kind groups added (post hoc either way).
- NOT RUN here: an independent verifier (the next lane); the model session's sealed E214 forecasts (27bf4e19, 804e269b; theirs to score); phi = 1 for the new kinds; a card-held-out reading.
- No E215 datum was opened at any step: the earlier-reads search skipped the E215 card lanes and every E215 data path.

## 10. Files and how to reproduce

- `DECLARED-unread-e214.md` / `.json` (step 1), `inputs/step1/` (runs listed from schedules and queues, fit inclusion and phi, count cells, bands, twin keys, the earlier-reads search), `inputs/step2/` (conditions, each model's forecasts), `forecasts-unread-e214.csv` / `.json` (step 2), `scores-unread-e214.json` / `-cases.csv` / `-runs.csv` (step 3), `posthoc-time-misses.json`, `recheck.json`, `logs/`, `scripts/`.
- From a lane folder holding `work/lab` (git archive of GitHub main 8bde0182: tools/matmul/mm1/v3.1, v3, v2, tools/claims-v3/e214, tools/claims-v3/e215/rules_e215.py and rules-e215.json) and `work/counts-e214` (the counts-e214 land dir), each with `/usr/bin/python3 -I -B` and single-threaded: s01_list.py, s01b_models.py, s01c_cells.py (v31, v3), s01d_bands.py, s01g_search.py, s01e_declare.py; s02a_conditions.py, s02b_forecast.py (v31, v3, v2), s02c_merge.py; s03_score.py; s03p_posthoc.py; s04_recheck.py; s05_land.py. `SHA256SUMS`: every file here but itself.

## 11. Corrections before the commit (Thu 19 Nov 2026, lane land-e214u)

This folder's verifier, verify-unread-e214 (round Q225), re-derived it from its own code (REPORTED: 30,836 of 30,836 forecast fields
bit-equal, 1,479 of 1,479 score checks equal, the order and the fit-input check hold) and found the verdict standing (FAIL: part A FAIL,
part S PASS); its verdict was HOLDS WITH FIXES, for seven wording findings in this README. The land lane land-e214u applied them here by
hand before the commit, after `scripts/s05_land.py` had written this file:

1. Section 3: the twins come "from E206, E208, E212 and E213 on these cards" (it said "from E208/E212": 9 of MM1-v3.1's 93 time-twin cases
   and 2 of its 41 energy-twin cases match only E206 arm B or E213 arm B configurations on card 1; the twin flags themselves were right).
2. Section 9 (and a pointer in section 2): part A's per-case error is MM1's convention, not E215's literal form, and E215's literal
   reading gives the same five FAILs.
3. Section 9: the scorer's one print label, edited after its stand-in test and before its freeze hash.
4. Section 6: MM1-v3.1's fit started at 17:02:54 PST (`../out/run.log`). The value typed into `scripts/s01b_models.py`, and so carried by
   `inputs/step1/models-step1.json` and the declaration, reads 17:03:47. No reading changes: E214 a1c0-S1's data commit (16:44:33) falls
   before both times, a1c1-S1's (17:28:54) after both.
5. Section 6: MM1-v3 is named by both its commits (landed b1493082, fitted at main 58f01105).
6. Section 7: "no MM1-v3.1 lane read an E214 measurement" (it said "read E214"): fit-v31's E215 never-run scan (20:21:43-20:21:52 PST Wed
   18 Nov, after its final fit ended at 20:19:32) read E214's files for configuration tokens, as the never-run scans line discloses.
7. Section 2: MM1-v3's and MM1-v2's cells at MM1-v3.1's bands are on MM1-v3.1's no-twin cases.

No other file changed: the 42 files besides this README and `SHA256SUMS` are byte for byte those of unread-e214's land dir, the frozen
declaration, forecasts, scorer and scores among them, and they keep their own wording (the declaration's 17:03:47 and its section a2, for
example). `SHA256SUMS` was re-made for this README's new bytes alone. Before these corrections `SHA256SUMS` was
e931d5323dfcc51cd127fd29c3c174472415950a90e9b63795d98a8ca8075fe4 and this README
652160502df40ac79bc8d222c32891119dcbfa4bde280853f1e2f1199bad5b55: `scripts/s05_land.py` re-makes that earlier README. The switch counts this test read, `../counts-e214/`, were committed first, unchanged (SHA256SUMS
4c39d0d3cf4ad405d5d32d4128f828d0d39272aab8dc0c822a2eacbb49be664a), with their own verifier's nits in a dated note beside them.
