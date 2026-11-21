# MM1's frozen matmul models scored BLIND on E221 (blind-e221, round Q235)

*Scored Fri 20 Nov 2026 at the desk on aifoundry2: the read 18:00:03 PST; Python /usr/bin/python3 3.12.3 (numpy 1.26.4 for the forecasts), every numerical step single-threaded inside the round's CPU slots. No card, no device, no ssh. Nothing here is committed by this lane.*

**What this is.** E221 is the model session's sixth matmul sweep (1120-mmsweep6, Discussion #15): E136's rgm136 unchanged over its cooperative gemmL loop, 847 runs over 345 arms and an anchor in nine sessions on three cards (aifoundry1 card 1 S1-S3 at 600 MHz, aifoundry1 card 0 S1-S3 at low power under its governor, aifoundry2 card 0 S1-S3 under its governor). Before any E221 run, the lab DECLARED how it would score its frozen models on E221, with MM1's domain stated first (decl-e221: `../blind-e221/DECLARED-blind-e221.md`, sha256 9cd8256b..., `FROZEN.txt` 2df06f06... at 06:17:38 PST Fri 20 Nov, posted on the Discussion as #15.2.1.1). All 733 of E221's cases (811 runs: 740 arm and 71 anchor runs; the 36 nulls and each session's smoke left out) are IN DOMAIN. The pass rule's model is **MM1-v3.2** (the lab's newest, landed 4e386f75); MM1-v3.1, MM1-v3, MM1-v2, the layout term '+contention', '+both' and verify-lay's four controls are scored beside, and the two MM1-v3.3 candidates ('MM1-v3.2+posimb' at the subset masks, 'MM1-v3.2+L3S' at the full chip) are REPORTED by their own frozen makers. This folder is that test, run EXACTLY as declared: every frozen file's sha256 checked, the forecasts made by the declared procedure at each run's measured clock, minion volts and die at start and hashed, the scorer code-tested and hashed, and only then the measurements read and scored.

**Label: BLIND (every session: its first datum after the freeze post).** The freeze post #15.2.1.1 is stamped 2026-11-20 06:22:53.507 PST by the post itself and 06:22:58 PST in the round's record; the later is used. Every session's claim and first card command come after it (the stopped first S1 start of 05:53:56-05:55:27, which ran no run, is not a committed session and is not scored):

| session | label | claim (PST) | T0 (PST) | first card command (queue / README) | minutes after the freeze post | runs | MM1-v3.2 per run, REPORTED: wall / J over idle given t |
|---|---|---|---|---|---|---|---|
| a1c1-S1 | BLIND | #15.3 06:32:49 | 06:32:54 | 06:32:57.848 / 06:32:57.848 | 10.00 | 92 | 7.42% / 10.11% |
| a1c0-S1 | BLIND | #15.4 07:17:41 | 07:17:46 | 07:17:49.465 / 07:17:49.465 | 54.86 | 89 | 8.44% / 5.27% |
| a1c1-S2 | BLIND | #15.5 08:00:46 | 08:00:52 | 08:00:55.855 / 08:00:55.855 | 97.96 | 91 | 8.89% / 4.46% |
| a1c0-S2 | BLIND | #15.6 08:45:38 | 08:45:43 | 08:45:46.958 / 08:45:46.958 | 142.82 | 92 | 8.27% / 4.64% |
| a1c1-S3 | BLIND | #15.7 09:29:19 | 09:29:25 | 09:29:29.372 / 09:29:29.372 | 186.52 | 93 | 8.72% / 10.40% |
| a1c0-S3 | BLIND | #15.8 10:14:05 | 10:14:10 | 10:14:13.396 / 10:14:13.396 | 231.26 | 78 | 12.31% / 6.44% |
| a2c0-S1 | BLIND | #15.9 10:16:52 | 10:16:57 | 10:17:00.570 / 10:17:00.570 | 234.04 | 93 | 8.29% / 5.07% |
| a2c0-S2 | BLIND | #15.10 11:01:43 | 11:01:47 | 11:01:50.830 / 11:01:50.830 | 278.88 | 90 | 5.69% / 3.72% |
| a2c0-S3 | BLIND | #15.11 15:51:11 | 15:51:16 | 15:51:19.767 / 15:51:19.767 | 568.36 | 93 | 12.85% / 4.29% |

## 1. The verdict (decided by the script, as declared)

**FAIL.** Part A (MM1-v3.2 on the primary footing, E215's rule form, each card over its no-twin cases, every class) **FAILS**: 14 rules fail across the three cards (aifoundry1 card 1 T1, aifoundry1 card 1 T2, aifoundry1 card 1 T3, aifoundry1 card 1 E4, aifoundry1 card 0 T1, aifoundry1 card 0 T2, aifoundry1 card 0 T3, aifoundry1 card 0 E2, aifoundry1 card 0 E4, aifoundry2 card 0 T1, aifoundry2 card 0 T2, aifoundry2 card 0 T3, aifoundry2 card 0 E2, aifoundry2 card 0 E4). Part S is NOT APPLICABLE (E221 has no operand-pattern arm), so the verdict is part A's. A rule passes when at least 90% of its cases are inside the band; the bands are E215's form from MM1-v3.1's held-out errors, the same for every model.

| rule | band (card 1 / aifoundry1 card 0 / aifoundry2 card 0) | aifoundry1 card 1 | aifoundry1 card 0 | aifoundry2 card 0 |
|---|---|---|---|---|
| T1 | 10% / 11% / 10% | FAIL 174/236 | FAIL 164/220 | FAIL 185/242 |
| T2 | 13% / 16% / 13% | FAIL 199/236 | FAIL 186/220 | FAIL 191/242 |
| T3 | 10% / 11% / 10% | FAIL 174/236 | FAIL 164/220 | FAIL 185/242 |
| E1 | 14% / 11% / 11%; watts 0.56 / 0.56 / 0.72 W | PASS 228/238 | PASS 214/217 | PASS 228/236 |
| E2 | 14% / 13% / 13%; watts 0.56 / 0.56 / 0.72 W | PASS 228/238 | FAIL 157/217 | FAIL 207/236 |
| E3 | 5% / 5% / 5% | PASS 237/238 | PASS 217/217 | PASS 235/236 |
| E4 | 10% / 10% / 10% | FAIL 177/238 | FAIL 155/217 | FAIL 180/236 |

T1 wall cycles an op (the slowest minion), T2 the counter's mean cycles an op, T3 seconds a pass (64 MB NB KB ops a minion x the op time), E1 J over idle given the measured op time (watts at a case under 3 W), E2 J over idle with the op time forecast, E3 J with the card at rest given t, E4 J at rest with t forecast. **Where the misses are** (MM1-v3.2, all three cards; post hoc count, REPORTED):

| rule | misses by class |
|---|---|
| T1 | MASK 152, MQ3 12, KB1 6, NB1 5 |
| E2 | MASK 98, NB1 1 |
| E4 | MASK 160, MQ3 10, NB1 5, KB1 4 |

So 152 of the 175 T1 misses are core-group mask placements (the MASK class); the energy rules given the measured time (E1, E3) pass on every card, and E2 and E4 fail where the time forecast fails (167 of the 179 E4 misses are T1 misses too). Every miss, case by case, is in `cases/scores-blind-e221-cases.csv` and `scores/scores-blind-e221.json` (part_A ... misses).

MM1-v3.1's part A, REPORTED beside (the continuity with E215, E217 and E219; deciding nothing): **FAIL** (aifoundry1 card 1 T1, aifoundry1 card 1 T2, aifoundry1 card 1 T3, aifoundry1 card 1 E4, aifoundry1 card 0 T1, aifoundry1 card 0 T2, aifoundry1 card 0 T3, aifoundry1 card 0 E1, aifoundry1 card 0 E2, aifoundry1 card 0 E4, aifoundry2 card 0 T1, aifoundry2 card 0 T2, aifoundry2 card 0 T3, aifoundry2 card 0 E2, aifoundry2 card 0 E4).

| rule | aifoundry1 card 1 | aifoundry1 card 0 | aifoundry2 card 0 |
|---|---|---|---|
| T1 | FAIL 183/246 | FAIL 172/228 | FAIL 181/242 |
| T2 | FAIL 210/246 | FAIL 192/228 | FAIL 192/242 |
| T3 | FAIL 183/246 | FAIL 172/228 | FAIL 181/242 |
| E1 | PASS 236/246 | FAIL 170/225 | PASS 232/236 |
| E2 | PASS 232/246 | FAIL 159/225 | FAIL 190/236 |
| E3 | PASS 245/246 | PASS 225/225 | PASS 235/236 |
| E4 | FAIL 185/246 | FAIL 163/225 | FAIL 178/236 |

## 2. The headline: no-twin cases, the primary footing (each run at its measured conditions)

rms % (bias %), n cases; error = forecast / measured - 1; a case's error is the mean of its runs' errors; E1 and E2 relative where the case is 3 W or more (by MM1-v3.2 and the measurement), watts beside.

| model | wall cycles (T1) | counter mean (T2) | J over idle given t (E1) | J over idle, t forecast (E2) | J at rest given t (E3) | J at rest, t forecast (E4) |
|---|---|---|---|---|---|---|
| MM1-v3.2 | 9.74% (+2.38), n 698 | 9.87% (+1.71), n 698 | 5.74% (-0.61), n 561; watts 0.222 W (+0.044), n 130 | 11.64% (+1.73), n 561; watts 0.199 W (+0.039), n 130 | 1.42% (-0.11), n 691 | 9.95% (+2.39), n 691 |
| MM1-v3.1 | 9.74% (+2.46), n 716 | 9.92% (+1.80), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 13.11% (+3.59), n 573; watts 0.201 W (+0.037), n 134 | 1.60% (+0.28), n 707 | 10.20% (+2.87), n 707 |
| MM1-v3 | 9.69% (+2.32), n 716 | 9.86% (+1.65), n 716 | 6.22% (+0.92), n 573; watts 0.213 W (-0.015), n 134 | 12.58% (+3.35), n 573; watts 0.191 W (-0.019), n 134 | 1.51% (+0.22), n 707 | 10.04% (+2.66), n 707 |
| MM1-v2 | 10.76% (-3.65), n 725 | 11.07% (-4.29), n 725 | 9.57% (+4.45), n 580; watts 0.191 W (-0.023), n 134 | 13.43% (+1.96), n 580; watts 0.164 W (-0.007), n 134 | 2.45% (+1.01), n 714 | 10.66% (-2.27), n 714 |
| v3.1+contention | 10.02% (+2.65), n 716 | 10.23% (+1.99), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 13.40% (+3.75), n 573; watts 0.200 W (+0.037), n 134 | 1.60% (+0.28), n 707 | 10.50% (+3.06), n 707 |
| v3.1+both | 10.02% (+2.65), n 716 | 10.23% (+1.99), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 13.40% (+3.75), n 573; watts 0.200 W (+0.037), n 134 | 1.60% (+0.28), n 707 | 10.50% (+3.06), n 707 |
| ctrl N1+N2 | 10.59% (+3.11), n 716 | 10.61% (+2.42), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 14.02% (+4.17), n 573; watts 0.197 W (+0.037), n 134 | 1.60% (+0.28), n 707 | 11.11% (+3.54), n 707 |
| ctrl G1 | 9.39% (+2.18), n 716 | 9.59% (+1.52), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 12.74% (+3.36), n 573; watts 0.201 W (+0.038), n 134 | 1.60% (+0.28), n 707 | 9.82% (+2.60), n 707 |
| ctrl G1+N1 | 8.54% (+0.70), n 716 | 8.98% (+0.05), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 11.57% (+2.22), n 573; watts 0.201 W (+0.047), n 134 | 1.60% (+0.28), n 707 | 8.83% (+1.17), n 707 |
| ctrl F1-layout-blind | 10.33% (+2.85), n 716 | 10.49% (+2.19), n 716 | 6.61% (+1.04), n 573; watts 0.223 W (+0.043), n 134 | 13.72% (+3.92), n 573; watts 0.199 W (+0.037), n 134 | 1.60% (+0.28), n 707 | 10.83% (+3.27), n 707 |
| MM1-v3.2+posimb (REPORTED) | 9.56% (+2.32), n 698 | 9.71% (+1.58), n 698 | 5.74% (-0.61), n 561; watts 0.222 W (+0.044), n 130 | 11.46% (+1.69), n 561; watts 0.200 W (+0.039), n 130 | 1.42% (-0.11), n 691 | 9.76% (+2.34), n 691 |
| MM1-v3.2+L3S (REPORTED) | 9.67% (+2.66), n 698 | 9.84% (+1.99), n 698 | 5.74% (-0.54), n 561; watts 0.222 W (+0.044), n 130 | 11.60% (+1.97), n 561; watts 0.199 W (+0.039), n 130 | 1.42% (-0.09), n 691 | 9.90% (+2.65), n 691 |

T3 (seconds a pass) equals T1 at the measured clock, as the declaration says (on the primary footing the same rms and bias on every scope, to 1e-14 points; on the nominal footing they differ by up to 0.12 points, the 800 MHz footing against the measured clock). 'v3.1+both' equals 'v3.1+contention' on every case and quantity (True); posimb equals MM1-v3.2 off its scope (True) and L3S equals MM1-v3.2 off its domain (True). 'v3.1+gemmLnc' and 'MM1-v3.2+AF4' are NOT APPLICABLE (no gemmLnc arm). Per card (no twin):

| model, card | measured clock (MHz) | wall | counter mean | E1 | E3 | E4 |
|---|---|---|---|---|---|---|
| MM1-v3.2, aifoundry1 card 1 | 599.2-599.5 | 8.86% (+1.81), n 236 | 9.23% (+1.03), n 236 | 7.69% (-2.80), n 108; watts 0.222 W (+0.044), n 130 | 1.08% (-0.14), n 238 | 8.99% (+1.81), n 238 |
| MM1-v3.2, aifoundry1 card 0 | 797.6-799.3 | 10.33% (+2.93), n 220 | 10.37% (+2.36), n 220 | 5.76% (+2.99), n 217 | 1.64% (+0.67), n 217 | 11.25% (+3.77), n 217 |
| MM1-v3.2, aifoundry2 card 0 | 797.9-799.3 | 9.99% (+2.42), n 242 | 10.01% (+1.78), n 242 | 4.58% (-2.91), n 236 | 1.49% (-0.79), n 236 | 9.60% (+1.72), n 236 |
| MM1-v3.1, aifoundry1 card 1 | 599.2-599.5 | 8.85% (+1.77), n 246 | 9.24% (+0.99), n 246 | 7.82% (-3.13), n 112; watts 0.223 W (+0.043), n 134 | 1.07% (-0.15), n 246 | 8.94% (+1.75), n 246 |
| MM1-v3.1, aifoundry1 card 0 | 797.6-799.3 | 10.28% (+3.06), n 228 | 10.37% (+2.49), n 228 | 8.25% (+5.51), n 225 | 2.25% (+1.42), n 225 | 11.67% (+4.66), n 225 |
| MM1-v3.1, aifoundry2 card 0 | 797.9-799.3 | 10.08% (+2.60), n 242 | 10.17% (+1.97), n 242 | 3.51% (-1.23), n 236 | 1.27% (-0.37), n 236 | 9.93% (+2.35), n 236 |

Twins (a case whose configuration is in the model's training data at the same card, kernel and clock to 25 MHz): MM1-v3.2 35 time and 31 energy twin cases of 733, MM1-v3.1 17/15, MM1-v3 17/15, MM1-v2 8/8 (the nominal-clock preview the declaration printed, exactly). MM1-v3.2 on its twin cases: wall 5.30% (+0.04), n 35; on all cases: wall 9.57% (+2.26), n 733, E1 5.68% (-0.55), n 587; watts 0.219 W (+0.046), n 134.

## 3. The comparisons (each its own verdict; exact two-sided sign test on the untied cases, closer A / closer B / ties)

Over every case both models price (twins included); the ties are the declaration's per card (cycles and seconds 0.005 in ln; J 0.01 in ln on card 1 and aifoundry1 card 0, 0.02 on aifoundry2 card 0; watts 0.1 / 0.15 / 0.4 W). Their floors, printed beside as the declaration asks: aifoundry1 card 0 from E212's a1c0 sessions (32 cases with two runs or more: wall 0.00161, J 0.00699 in ln, W 0.11509 W); aifoundry2 card 0 from E212's a2c0 sessions, a weak floor (3 cases: wall 0.00158, J 0.01885 in ln, W 0.35823 W); card 1 E215 arm B's registered ties.

| comparison, scope | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |
|---|---|---|---|---|---|
| D0 MM1-v3.2 vs MM1-v3.1, pooled | NOT DECIDED (256/215/262, p 0.0652) | MM1-v3.2 BETTER (275/187/271, p 4.93e-05) | NOT DECIDED (256/215/262, p 0.0652) | MM1-v3.2 BETTER (174/117/430, p 0.000994) | MM1-v3.2 BETTER (223/113/385, p 1.98e-09) |
| D0 MM1-v3.2 vs MM1-v3.1, aifoundry1 card 1 | NOT DECIDED (96/74/80, p 0.107) | MM1-v3.2 BETTER (102/60/88, p 0.00121) | NOT DECIDED (96/74/80, p 0.107) | NOT DECIDED (27/14/209, p 0.0596) | NOT DECIDED (27/16/207, p 0.126) |
| D0 MM1-v3.2 vs MM1-v3.1, aifoundry1 card 0 | NOT DECIDED (75/72/85, p 0.869) | NOT DECIDED (81/66/85, p 0.248) | NOT DECIDED (75/72/85, p 0.869) | MM1-v3.2 BETTER (144/26/58, p 5.27e-21) | MM1-v3.2 BETTER (143/40/45, p 8.66e-15) |
| D0 MM1-v3.2 vs MM1-v3.1, aifoundry2 card 0 | NOT DECIDED (85/69/97, p 0.227) | MM1-v3.2 BETTER (92/61/98, p 0.015) | NOT DECIDED (85/69/97, p 0.227) | MM1-v3.1 BETTER (3/77/163, p 1.41e-19) | NOT DECIDED (53/57/133, p 0.775) |
| D1 MM1-v3.1 vs MM1-v3, pooled | NOT DECIDED (144/145/444, p 1) | MM1-v3 BETTER (122/162/449, p 0.0205) | NOT DECIDED (144/145/444, p 1) | MM1-v3 BETTER (13/95/613, p 1.46e-16) | MM1-v3 BETTER (31/89/601, p 1.12e-07) |
| D1 MM1-v3.1 vs MM1-v3, aifoundry1 card 1 | NOT DECIDED (43/44/163, p 1) | NOT DECIDED (34/47/169, p 0.182) | NOT DECIDED (43/44/163, p 1) | MM1-v3 BETTER (5/26/219, p 0.000192) | NOT DECIDED (16/28/206, p 0.0961) |
| D1 MM1-v3.1 vs MM1-v3, aifoundry1 card 0 | NOT DECIDED (52/47/133, p 0.688) | NOT DECIDED (45/55/132, p 0.368) | NOT DECIDED (52/47/133, p 0.688) | MM1-v3 BETTER (6/69/153, p 1.16e-14) | MM1-v3 BETTER (13/61/154, p 1.39e-08) |
| D1 MM1-v3.1 vs MM1-v3, aifoundry2 card 0 | NOT DECIDED (49/54/148, p 0.694) | NOT DECIDED (43/60/148, p 0.114) | NOT DECIDED (49/54/148, p 0.694) | TOO FEW (2/0/241, p 0.5) | TOO FEW (2/0/241, p 0.5) |
| D2 MM1-v3.1 vs MM1-v2, pooled | MM1-v3.1 BETTER (430/192/111, p 6.4e-22) | MM1-v3.1 BETTER (401/211/121, p 1.34e-14) | MM1-v3.1 BETTER (430/192/111, p 6.4e-22) | MM1-v3.1 BETTER (424/134/163, p 4.71e-36) | MM1-v3.1 BETTER (337/210/174, p 6.27e-08) |
| D2 MM1-v3.1 vs MM1-v2, aifoundry1 card 1 | MM1-v3.1 BETTER (146/67/37, p 6.48e-08) | MM1-v3.1 BETTER (131/71/48, p 2.92e-05) | MM1-v3.1 BETTER (146/67/37, p 6.48e-08) | MM1-v3.1 BETTER (105/72/73, p 0.0159) | MM1-v3.1 BETTER (95/67/88, p 0.0336) |
| D2 MM1-v3.1 vs MM1-v2, aifoundry1 card 0 | MM1-v3.1 BETTER (138/61/33, p 4.92e-08) | MM1-v3.1 BETTER (132/67/33, p 4.75e-06) | MM1-v3.1 BETTER (138/61/33, p 4.92e-08) | MM1-v3.1 BETTER (185/30/13, p 1.92e-28) | NOT DECIDED (111/90/27, p 0.158) |
| D2 MM1-v3.1 vs MM1-v2, aifoundry2 card 0 | MM1-v3.1 BETTER (146/64/41, p 1.51e-08) | MM1-v3.1 BETTER (138/73/40, p 9.03e-06) | MM1-v3.1 BETTER (146/64/41, p 1.51e-08) | MM1-v3.1 BETTER (134/32/77, p 4.79e-16) | MM1-v3.1 BETTER (131/53/59, p 8.29e-09) |

Over the cases that are twins for neither model (REPORTED), pooled: D0 H1 MM1-v3.2 BETTER (244/201/253, p 0.0464), H4 MM1-v3.2 BETTER (164/114/413, p 0.00322); D1 H1 NOT DECIDED (140/143/433, p 0.905), H4 MM1-v3 BETTER (13/95/599, p 1.46e-16); D2 H1 MM1-v3.1 BETTER (419/190/107, p 8.64e-21), H4 MM1-v3.1 BETTER (413/133/161, p 2.25e-34).

D3, on the 461 subset-mask cases (the MASK, CELL1 and L2I8 classes at shire subsets), each candidate as A against MM1-v3.1 as B:

| D3 | H1 wall, pooled | H1 card 1 | H1 aifoundry1 card 0 | H1 aifoundry2 card 0 | H2 counter mean, pooled | H2 card 1 | H2 aifoundry1 card 0 | H2 aifoundry2 card 0 |
|---|---|---|---|---|---|---|---|---|
| v3.1+contention vs MM1-v3.1 | MM1-v3.1 BETTER (66/175/220, p 1.44e-12) | MM1-v3.1 BETTER (26/58/69, p 0.000628) | MM1-v3.1 BETTER (20/62/72, p 3.71e-06) | MM1-v3.1 BETTER (20/55/79, p 6.49e-05) | MM1-v3.1 BETTER (64/182/215, p 2.73e-14) | MM1-v3.1 BETTER (24/60/69, p 0.000107) | MM1-v3.1 BETTER (21/63/70, p 4.97e-06) | MM1-v3.1 BETTER (19/59/76, p 6.42e-06) |
| ctrl N1+N2 vs MM1-v3.1 | MM1-v3.1 BETTER (90/346/25, p 1.86e-36) | MM1-v3.1 BETTER (38/106/9, p 1.27e-08) | MM1-v3.1 BETTER (27/121/6, p 2.08e-15) | MM1-v3.1 BETTER (25/119/10, p 7.25e-16) | MM1-v3.1 BETTER (111/309/41, p 1.1e-22) | MM1-v3.1 BETTER (43/93/17, p 2.17e-05) | MM1-v3.1 BETTER (34/109/11, p 2.33e-10) | MM1-v3.1 BETTER (34/107/13, p 5.45e-10) |
| ctrl G1 vs MM1-v3.1 | NOT DECIDED (178/147/136, p 0.0959) | NOT DECIDED (62/49/42, p 0.255) | NOT DECIDED (60/48/46, p 0.29) | NOT DECIDED (56/50/48, p 0.627) | NOT DECIDED (168/152/141, p 0.402) | NOT DECIDED (55/51/47, p 0.771) | NOT DECIDED (58/52/44, p 0.634) | NOT DECIDED (55/49/50, p 0.624) |
| ctrl G1+N1 vs MM1-v3.1 | NOT DECIDED (174/189/98, p 0.463) | NOT DECIDED (53/66/34, p 0.271) | NOT DECIDED (61/63/30, p 0.928) | NOT DECIDED (60/60/34, p 1) | MM1-v3.1 BETTER (161/210/90, p 0.0126) | NOT DECIDED (53/73/27, p 0.0901) | NOT DECIDED (54/70/30, p 0.178) | NOT DECIDED (54/67/33, p 0.275) |
| ctrl F1-layout-blind vs MM1-v3.1 | MM1-v3.1 BETTER (65/177/219, p 3.64e-13) | MM1-v3.1 BETTER (26/57/70, p 0.000878) | MM1-v3.1 BETTER (20/63/71, p 2.43e-06) | MM1-v3.1 BETTER (19/57/78, p 1.48e-05) | MM1-v3.1 BETTER (77/164/220, p 2.15e-08) | MM1-v3.1 BETTER (30/54/69, p 0.0116) | MM1-v3.1 BETTER (23/56/75, p 0.000264) | MM1-v3.1 BETTER (24/54/76, p 0.000901) |

D3c, the MM1-v3.3 candidates (REPORTED, deciding nothing; posimb on the 461 subset-mask cases, L3S on its 272 full-mask cases):

| D3c, pooled | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |
|---|---|---|---|---|---|
| MM1-v3.2+posimb vs MM1-v3.2 (the subset masks) | MM1-v3.2+posimb BETTER (108/28/325, p 2.78e-12) | MM1-v3.2+posimb BETTER (80/25/356, p 6.88e-08) | - | - | - |
| MM1-v3.2+L3S vs MM1-v3.2 (L3S's full-mask cases) | NOT DECIDED (38/45/189, p 0.51) | MM1-v3.2 BETTER (32/53/187, p 0.0295) | NOT DECIDED (38/45/189, p 0.51) | NOT DECIDED (8/3/258, p 0.227) | MM1-v3.2+L3S BETTER (26/12/231, p 0.0336) |
| MM1-v3.2+posimb vs MM1-v3.1 (the subset masks) | NOT DECIDED (136/109/216, p 0.0965) | MM1-v3.2+posimb BETTER (149/99/213, p 0.0018) | - | - | - |
| MM1-v3.2+L3S vs MM1-v3.1 (L3S's full-mask cases) | MM1-v3.2+L3S BETTER (121/50/101, p 5.64e-08) | MM1-v3.2+L3S BETTER (117/50/105, p 2.28e-07) | MM1-v3.2+L3S BETTER (121/50/101, p 5.64e-08) | MM1-v3.2+L3S BETTER (47/28/194, p 0.037) | NOT DECIDED (56/37/176, p 0.0614) |

D4 (the switch route): NOT APPLICABLE: E221 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random).

## 4. Where it holds and where it misses (the declared splits, REPORTED; no twin, pooled)

| class | cases | MM1-v3.2 wall / E1 / E3 | MM1-v3.1 | MM1-v3 | MM1-v2 | MM1-v3.2 part A beside (card 1; aifoundry1 card 0; aifoundry2 card 0): T1, E1, E4 |
|---|---|---|---|---|---|---|
| MASK: the core-group masks (12 placement families) with their whole-chip twins | 392 | 12.41% / 7.48% / 1.57% | 12.19% / 8.67% / 1.79% | 12.11% / 8.28% / 1.70% | 13.17% / 11.08% / 2.30% | T1 FAIL 70/121, E1 PASS 113/123, E4 FAIL 70/123; T1 FAIL 72/123, E1 PASS 118/121, E4 FAIL 64/121; T1 FAIL 69/119, E1 PASS 108/116, E4 FAIL 66/116 |
| CELL1: the 1x1x1 cells at new masks | 79 | 0.21% / 4.26% / 1.11% | 0.21% / 4.99% / 1.42% | 0.21% / 4.83% / 1.32% | 0.21% / 8.97% / 2.43% | T1 PASS 22/22, E1 PASS 22/22, E4 PASS 22/22; T1 PASS 22/22, E1 PASS 22/22, E4 PASS 22/22; T1 PASS 32/32, E1 PASS 32/32, E4 PASS 32/32 |
| KB1: KB = 1 at the whole chip | 72 | 7.76% / 4.43% / 1.19% | 8.66% / 4.84% / 1.32% | 8.59% / 3.16% / 1.09% | 11.06% / 9.74% / 2.80% | T1 FAIL 22/28, E1 PASS 28/28, E4 FAIL 24/28; T1 PASS 16/16, E1 PASS 16/16, E4 PASS 16/16; T1 PASS 28/28, E1 PASS 28/28, E4 PASS 28/28 |
| L2I8: the int8 L2 point (1x1xK) at the whole chip and at masks | 54 | 3.10% / 3.86% / 1.40% | 2.51% / 4.44% / 1.54% | 2.66% / 4.60% / 1.60% | 6.40% / 6.78% / 2.05% | T1 PASS 18/18, E1 PASS 18/18, E4 PASS 18/18; T1 PASS 22/22, E1 PASS 21/21, E4 PASS 21/21; T1 PASS 14/14, E1 PASS 13/13, E4 PASS 13/13 |
| MQ3: the MB = 3 ladders | 47 | 8.56% / 2.58% / 0.94% | 8.49% / 2.60% / 1.08% | 8.45% / 2.56% / 0.99% | 4.76% / 5.81% / 2.46% | T1 FAIL 12/17, E1 PASS 17/17, E4 FAIL 13/17; T1 FAIL 8/10, E1 PASS 10/10, E4 FAIL 8/10; T1 FAIL 15/20, E1 PASS 20/20, E4 FAIL 16/20 |
| DK: deep K (KB 16-32) | 30 | 4.35% / 3.80% / 1.58% | 4.71% / 3.32% / 1.45% | 4.61% / 2.98% / 1.23% | 7.32% / 10.76% / 4.44% | T1 PASS 10/10, E1 PASS 10/10, E4 PASS 10/10; T1 TOO FEW 8/8, E1 TOO FEW 8/8, E4 TOO FEW 8/8; T1 PASS 12/12, E1 PASS 12/12, E4 PASS 12/12 |
| HLD: the held walks (small shapes) | 23 | 2.36% / 4.04% / 1.65% | 2.63% / 3.86% / 1.43% | 2.65% / 3.39% / 1.31% | 2.58% / 5.30% / 1.70% | T1 TOO FEW 9/9, E1 TOO FEW 9/9, E4 TOO FEW 9/9; T1 TOO FEW 6/6, E1 TOO FEW 6/6, E4 TOO FEW 6/6; T1 TOO FEW 8/8, E1 TOO FEW 8/8, E4 TOO FEW 8/8 |
| BW: the BW shapes (2x12x4, 5x12x2, 6x5x3) | 18 | 1.91% / 1.38% / 0.58% | 4.48% / 2.26% / 0.95% | 3.67% / 2.07% / 0.89% | 2.29% / 4.78% / 2.15% | T1 TOO FEW 9/9, E1 TOO FEW 9/9, E4 TOO FEW 9/9; T1 TOO FEW 6/6, E1 TOO FEW 6/6, E4 TOO FEW 6/6; T1 TOO FEW 3/3, E1 TOO FEW 2/2, E4 TOO FEW 2/2 |
| NB1: NB = 1 | 15 | 9.05% / 3.19% / 1.32% | 8.26% / 3.21% / 1.31% | 9.00% / 3.44% / 1.43% | 12.59% / 2.34% / 0.97% | T1 TOO FEW 2/2, E1 TOO FEW 2/2, E4 TOO FEW 2/2; T1 TOO FEW 4/7, E1 TOO FEW 7/7, E4 TOO FEW 4/7; T1 TOO FEW 4/6, E1 TOO FEW 5/5, E4 TOO FEW 3/5 |
| ANCHOR: the anchor (4x8x8 int8 random) | 3 | - / - / - | - / - / - | - / - / - | - / - / - | T1 NO DATA 0/0, E1 NO DATA 0/0, E4 NO DATA 0/0; T1 NO DATA 0/0, E1 NO DATA 0/0, E4 NO DATA 0/0; T1 NO DATA 0/0, E1 NO DATA 0/0, E4 NO DATA 0/0 |

The anchor's three cases are twins for every model (its configuration is in each fit), so they leave the no-twin headline.

**The mask ladders** (each MASK subset case against its whole-chip twin, the same card, arm, format and kind at 0xffffffff: the forecast subset/full ratio of the cycles an op over the measured one, minus 1; rms % (bias %), n pairs; REPORTED):

| family | pairs | MM1-v3.2 wall | MM1-v3.1 wall | MM1-v3 wall | MM1-v2 wall | v3.1+contention wall | MM1-v3.2+posimb wall | MM1-v3.2 counter mean |
|---|---|---|---|---|---|---|---|---|
| PLA | 78 | 10.93% (-0.96) | 10.90% (-1.33) | 10.89% (-1.44) | 13.15% (-9.40) | 11.09% (-1.02) | 10.65% (-0.67) | 10.16% (+1.26) |
| PLB | 24 | 18.99% (+16.28) | 18.49% (+15.76) | 18.48% (+15.75) | 12.68% (+9.37) | 18.50% (+15.53) | 18.76% (+16.27) | 17.96% (+15.13) |
| PLC | 24 | 3.24% (-2.32) | 3.36% (-2.48) | 3.54% (-2.73) | 13.91% (-13.69) | 2.73% (-1.30) | 3.40% (-2.59) | 7.63% (-5.53) |
| PLD | 21 | 4.17% (+3.54) | 4.01% (+3.37) | 3.77% (+3.11) | 8.66% (-8.42) | 3.24% (+2.21) | 3.78% (+3.38) | 7.97% (+1.04) |
| PLE | 42 | 3.34% (-0.30) | 3.32% (-0.58) | 3.38% (-0.76) | 10.84% (-9.82) | 3.69% (-0.38) | 3.00% (-0.52) | 5.84% (-2.46) |
| PLH | 21 | 10.65% (+9.69) | 9.78% (+8.77) | 10.03% (+9.03) | 10.53% (+9.56) | 9.87% (+8.86) | 10.12% (+9.28) | 13.24% (+8.19) |
| PLK | 18 | 11.72% (+3.75) | 11.51% (+3.36) | 11.45% (+3.25) | 10.33% (-5.06) | 12.26% (+3.90) | 11.26% (+3.62) | 13.60% (+2.20) |
| PLK3 | 12 | 11.72% (+3.60) | 11.52% (+3.21) | 11.46% (+3.09) | 10.41% (-5.07) | 12.26% (+3.74) | 11.25% (+3.46) | 13.65% (+2.04) |
| PLL | 21 | 7.77% (+6.91) | 6.69% (+5.73) | 7.08% (+6.16) | 12.24% (+11.55) | 6.69% (+5.73) | 7.24% (+6.51) | 2.92% (-1.88) |
| PLM | 24 | 23.51% (+19.84) | 23.05% (+19.35) | 22.95% (+19.25) | 14.44% (+9.56) | 23.58% (+19.90) | 23.08% (+19.48) | 24.17% (+18.93) |
| PLN | 18 | 15.31% (-12.14) | 15.38% (-12.21) | 15.40% (-12.23) | 16.82% (-13.76) | 15.33% (-12.13) | 15.31% (-12.15) | 13.36% (-10.53) |
| PLX | 51 | 10.45% (+6.14) | 10.17% (+5.70) | 10.09% (+5.57) | 8.53% (-3.78) | 10.89% (+6.80) | 10.24% (+6.23) | 10.44% (+6.13) |

(Six MASK cases belong to a combined 'PLA+PLX' block; they are in the per-card table of `scores/scores-blind-e221.json`, mask_ladders_REPORTED.by_card_family.)

## 5. Reported beside (deciding nothing)

**The nominal footing** (decl-e221's frozen nominal forecasts: card 1 at 600 MHz, 0.517 V, 60 C; the governed cards at 800 MHz, each model's own volts, 55 C; scored by the same script and rules): VERDICT FAIL (part A FAIL: aifoundry1 card 1 T1, aifoundry1 card 1 T2, aifoundry1 card 1 T3, aifoundry1 card 1 E4, aifoundry1 card 0 T1, aifoundry1 card 0 T2, aifoundry1 card 0 T3, aifoundry1 card 0 E1, aifoundry1 card 0 E2, aifoundry1 card 0 E4, aifoundry2 card 0 T1, aifoundry2 card 0 T2, aifoundry2 card 0 T3, aifoundry2 card 0 E2, aifoundry2 card 0 E4); the watts set differs from the primary footing's in 0 cases.

| nominal footing, no twin, pooled | wall | E1 | E3 |
|---|---|---|---|
| MM1-v3.2 | 9.76% (+2.44), n 698 | 8.76% (+6.31), n 561; watts 0.227 W (+0.108), n 130 | 2.41% (+1.69), n 691 |
| MM1-v3.1 | 9.77% (+2.53), n 716 | 10.68% (+8.09), n 573; watts 0.226 W (+0.106), n 134 | 2.85% (+2.09), n 707 |
| MM1-v3 | 9.72% (+2.39), n 716 | 10.32% (+7.96), n 573; watts 0.200 W (+0.044), n 134 | 2.79% (+2.03), n 707 |
| MM1-v2 | 10.74% (-3.59), n 725 | 9.85% (+4.78), n 580; watts 0.191 W (-0.023), n 134 | 2.51% (+1.08), n 714 |

**The governed clocks** (each run's measured kernel clock beside the nominal 800 MHz; MM1-v3.2's per-run wall error on both footings):

| card | runs | clock (MHz) min / mean / max | runs within 25 MHz of 800 | MM1-v3.2 wall, primary | MM1-v3.2 wall, nominal 800 MHz | MM1-v3.2 E1 (3 W and above), primary / nominal |
|---|---|---|---|---|---|---|
| aifoundry1 card 0 | 259 | 797.55 / 799.06 / 799.27 | 259 | 9.72% (+2.52), n 259 | 9.75% (+2.59), n 259 | 5.45% / 11.00% |
| aifoundry2 card 0 | 276 | 797.93 / 799.08 / 799.32 | 276 | 9.45% (+2.15), n 276 | 9.48% (+2.23), n 276 | 4.41% / 5.30% |

## 6. Post hoc readings (made after the read; REPORTED; they decide nothing)

- **Without the MASK class**, MM1-v3.2's part A cells would read PASS on every card: aifoundry1 card 1 T1 104/115, T2 113/115, T3 104/115, E1 115/115, E2 115/115, E3 115/115, E4 107/115; aifoundry1 card 0 T1 92/97, T2 96/97, T3 92/97, E1 96/96, E2 96/96, E3 96/96, E4 91/96; aifoundry2 card 0 T1 116/123, T2 116/123, T3 116/123, E1 120/120, E2 119/120, E3 120/120, E4 114/120. MM1-v3.1 the same way: FAIL (aifoundry1 card 1 T1 99/115, aifoundry1 card 1 T3 99/115).
- **At the full chip only** (every class): FAIL (aifoundry1 card 1|T1, aifoundry1 card 1|T3): aifoundry1 card 1 T1 76/87; aifoundry1 card 0 T1 65/70; aifoundry2 card 0 T1 82/89.
- **The MASK class by shire count** (MM1-v3.2 wall, no twin; rms % (bias %), n): 1 shire 14.19% (+10.32), n 160; 2-3 shires 12.96% (+5.91), n 91; 4-7 shires 5.59% (+0.16), n 41; 8-15 shires 12.46% (-12.43), n 3; 16-31 shires 10.78% (-4.74), n 56; the whole chip (32) 3.48% (+0.49), n 12. The model forecasts the single-shire and two-to-three-shire placements too slow on average and the 16-31-shire ones too fast.
- **The worst placement families at the subset masks** (MM1-v3.2 wall): PLM 28.19% (+24.95), n 24; PLH 14.61% (+13.82), n 21; PLA+PLX 13.79% (+10.59), n 6; PLX 13.47% (+11.30), n 46; PLK 13.41% (+6.96), n 18.
- **The worst cases** (MM1-v3.2 wall error): a1c0 gemmL3x4x6 fp32 zeros 0x4000 +45.6%; a2c0 gemmL3x4x6 fp32 zeros 0x4000 +44.6%; a1c0 gemmL3x4x6 fp32 zeros 0x20000 +41.1%; a2c0 gemmL3x4x6 fp32 zeros 0x20000 +40.9%; a1c1 gemmL3x4x6 fp32 zeros 0x4000 +38.2%; a1c0 gemmL3x4x6 fp32 zeros 0x44 +36.5%: the same shape, gemmL3x4x6 fp32 zeros, at small masks on all three cards.
- **E2 and E4 follow the time:** 85 of MM1-v3.2's 99 E2 misses and 167 of its 179 E4 misses are also T1 misses.

## 7. How it was done (Pacific; every step one slot job; the hashes)

1. **Every frozen file by sha256** (17:45:50-17:46:01): 104 checks, 0 failed (the first run had one failure, the registration's sums read from the wrong folder; the re-run read them from the repository top): MM1-v3.2 58/58, MM1-v3.1 64/64 and its counts 71/71, MM1-v3 170/170, MM1-v2 114/114, the layout term 25/25 and its note 6/6, the gemmLnc term 22/22; the declaration's 52 input sha256 52/52; FROZEN.txt 2df06f06 and the four frozen files equal to the posted record #15.2.1.1; decl-e221's land 39/39; the three candidates' FROZEN.txt and posted forecasts equal to their record and to main's land; decl-e221's copy of main at 0f046200, 2,761/2,761 files, equal to today's main (1a259ddc).
2. **Conditions read** (17:46:51): only the declared start-of-run fields of the nine committed data files at 1a259ddc (the top card, session and primary view; per run its identity fields, die_start_c and the primary view's kclock_mhz and rails.minion.mV): 811/811 listed runs found, all ran, one without a minion rail reading (the declared fallback: the model's own volts at the clock).
3. **Procedure check** (17:50:16-17:51:00): this lane's forecast code, run at the declared NOMINAL conditions, re-makes decl-e221's frozen nominal forecasts **bit for bit**: 214,915 fields over 811 runs (733 cases) and 12 models, 0 differ; the four maker checks equal decl-e221's figures to the last digit.
4. **Forecasts** at each run's measured conditions (17:51:05-17:52:49), hashed at 17:52:57 (`logs/step2-sha256.txt`): `forecasts-blind-e221.csv` 962252bd..., `forecasts-blind-e221.json` 10dac661....
5. **The scorer** code-tested on two stand-in days built from the forecasts alone (exact and noise), then hashed with the readings file at 17:59:51 (`logs/step3-scorer-sha256.txt`): `scripts/s03_score.py` 20534e559870b3188b2781482ac1d10bee89fa74c5f82c5afc2087a291e8a31a, `READINGS-blind-e221.md` 44d32b5a76d7024bfbd509c7d2164e8b355cb5a4e56d957edecb8804f67a13c3.
6. **Read and scored** (18:00:03): the data files equal to step 2's bytes; the loader check (MM1-v3.1's own reader on the same bytes) EQUAL: 811/811 runs, 0 field differences; the queue condition removed 0 runs; 14 capped runs not read for energy (797 energy runs).
7. **Independent recheck** (18:01:28): a second code path from the CSV and a fresh read: part A 42/42 cells (MM1-v3.2 and MM1-v3.1), 16/16 rms cells and 4/4 sign-test tallies equal to the scorer's.

**Readings and one departure.** Where the declaration is silent, the scorer takes its form's reading (decl-e219's, verified), stated and hashed before the read in `READINGS-blind-e221.md`: the run selection (MM1's loader conditions and the session's queue; energy also needs dP_w and p_mean_w, not capped, not a 'time' run), 'at least 90%' by integer arithmetic, the test's NO DATA line, the twin key's clock, the watts set, the label's times and the REPORTED tables' forms. One departure, in how a frozen maker is loaded, not in what it computes: posimb's as-run scripts name their own lane folder, whose lab copy was removed by a cleanup before this lane ran; the landed copies (the same files but for the two path lines) ran instead, and re-made decl-e221's four maker checks and frozen nominal forecasts exactly.

**NOT RUN:** a second, independent scorer by another lane (the verify lane's); any reading of the model session's sealed E221 forecast (it was not opened); a switch count (E221 designs no tile).

## 8. Files

- `README.md` (this file); `READINGS-blind-e221.md` (the readings, hashed before the read)
- `forecasts-blind-e221.csv`, `forecasts-blind-e221.json`: the measured-conditions forecasts, byte for byte as hashed before the read
- `scores/scores-blind-e221.json` (every declared figure, both footings), `scores/scores-blind-e221.txt` (the scorer's summary), `scores/posthoc-e221.json` (section 6), `scores/recheck-e221.json` (step 7)
- `cases/scores-blind-e221-cases.csv` (one row a case: measured, every model's errors, twins, nominal errors), `cases/scores-blind-e221-runs.csv` (one row a run)
- `inputs/conditions-e221.json` (the start-of-run fields only), `inputs/nominal-check.json` (the procedure check), `inputs/step0-checks.json` (step 1)
- `logs/`: the progress log, the two hash logs and each step's output; `scripts/`: every script as run, its desk paths written as `<WF>` (the round's folder) and `<LAB>` (the lab clone), the HTTPS rewrite's value as `<GITHUB_SSH_PREFIX>`, and in the logs the file owner as `<user> <group>`; `scripts/SCRUB-MAP.json` gives each replacement and both sha256 (the landed text reverses to the as-run bytes)
- `SHA256SUMS` over every other file here

SPDX-License-Identifier: Apache-2.0
