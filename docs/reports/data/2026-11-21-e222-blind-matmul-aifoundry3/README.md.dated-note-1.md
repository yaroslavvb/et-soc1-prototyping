# E222, dated note 1 (the scores lane): the frozen scorer's words on the committed data, the cross-card rule with E220's committed and verified data, and THE SELECTION RULE's outcome: **MM1-v3.3 = MM1-v3.2 + AF4**

*Sat 21 Nov 2026 (week 47), PST, written by the scores lane of round Q236 after the data commit `cfd7e641` (committed 00:57:50 PST, pushed 00:57:53) and after the data verifier's verdict HOLDS (verify-e222d, 01:01-01:28 PST). Post hoc to the data: no datum, point, forecast, band, tie, rule, margin or verdict changes here. Every number below is read from the frozen scorer's own outputs committed beside this note, unless it is marked as the data verifier's. **BLIND:** E222's forecasts were frozen at 13:50:25 PST Fri 20 Nov 2026 (FROZEN.txt `172ed079...`, posted 13:51:12), 10 h 16 min before the session's first card command (00:06:31 PST Sat), and before any E220 datum; no sealed forecast of the model session was registered for E222.*

## 1. What this note adds (new files only, in this directory)

| file | sha256 | bytes | what |
|---|---|---|---|
| `scores-e222-A.json` | `89738e2c3555e822...` | 96,422 | the frozen scorer's JSON from the kit's step 13 (`rb/s24_score_e222.sh A`): its registered call on this directory's committed `data-e222.json` with step 6n's committed `labels-e222.json`; byte for byte as the card lane's step wrote it |
| `scores-e222-A.txt` | `dc6ab3926ab5d41a...` | 426 | its printed lines (27), byte for byte = the runbook's capture of the call |
| `scores-e222-cx.json` | `9c8b668ff68b7634...` | 105,676 | the frozen scorer's registered call with the cross-card rule (E222.md 7: `--e220-a`, `--e220-b`, `--e220-verified`), made by this lane at 01:40:50 PST on the committed bytes; every field but `cross_card` and the CX verdicts equals `scores-e222-A.json` |
| `scores-e222-cx.txt` | `10960156d1ec90cb...` | 1,832 | its printed lines (68: the 26 lines of `scores-e222-A.txt` other than CX, and CX's 42 cells) |
| `nh-l3s-beside-e222.txt` | `779731a08f9e62f4...` | 895 | the registration's dated note 1's printer (`nh_l3s_e222_note1.py beside`) on `scores-e222-A.json`: NH-L3S, HC-L3S and SEL with that note's rates beside them |
| `README.md.dated-note-1.md` | (this file) | | this note |
| `SHA256SUMS-note1` | | | the sha256 of the five files above, this note, README.md and SHA256SUMS; `sha256sum -c SHA256SUMS-note1` from this directory |

The two `-cx` files are a second call of the same frozen scorer, not a second scoring: the card day's verdicts are step 13's, and the cross-card rule, which step 13 had to print PENDING, is read from the `-cx` call. E224's THE PICK reads every committed `scores-e222*.json` here; both files carry the same SEL.

## 2. The registered scorer run on its data commit (the scores lane's checks)

- **The runbook's log.** Its last six lines (105-110 of 110) are step 13 (`s24_score_e222`): calls 1-5 at 00:58:02 PST and call 6 at 00:58:03 PST, each rc 0, with exactly the commands `rb/s24_score_e222.sh A` writes. Call 6 is `/usr/bin/python3 -I -B tools/claims-v3/e222/score_e222.py --a <this directory>/data-e222.json --a-tag A --labels <this directory>/labels-e222.json --out <RB_OUT>/scores-A`. No earlier line of the log runs the scorer; step 2 ran only its two self-tests in memory (`rb/scorer_check_e222.py`).
- **The captures.** Six calls of one run of the step. Call 1 printed the data commit `cfd7e6415` and its subject; call 2 nothing; call 3 every SHA256SUMS entry OK (647 of 647); call 4 "HISTORY OK", naming the registration `3f1c631ee17e`; call 5 "LABELS-OK: 0 label(s) of E222's registered points (none)". The `.txt` is call 6's capture byte for byte and main()'s print form of the JSON's verdicts; the JSON is main()'s dump form.
- **The times and the tree.** The scorer's JSON was written inside call 6; LAB's HEAD at the step was the data commit itself (its reflog), and nothing has moved since. The round's CPU-slot log shows one step-13 job, 00:58:02-00:58:03 PST, rc 0. The frozen scorer (`1c2aeaeb...` = the registration list's line), its eight pins (E220's scorer and five E220 files for the cross-card rule; E218's committed scores and data), the registration list's 30 files (the list itself `de67150b...`), the kit list's 54 and dated note 1's 8 each have one blob from their freeze commit to HEAD; E222.md section 0's tables read 61 of 61 and its FROZEN block 17 of 17.
- **The re-run.** Step 13's calls 5 and 6 made again from a tree exported from the lab's objects at `cfd7e641` (= HEAD = the remote's main), in a CPU slot: the JSON, the printed lines and call 5's line equal the card lane's byte for byte; calls 1-4 made again as reads in the lab equal their captures (8 comparisons SAME, 0 differ; the tree unchanged after).

## 3. The rules' words and the verdicts (BLIND; registered, E222.md section 7, quoted verbatim)

### 3.1 R0 and S6

> **R0** (every check of C exact or approx; the smoke good; the G block's smoke failing while no gemmLnc point ran is flagged, not an R0 failure) and **S6** (every kept run at 590-610 MHz): a FAIL labels every other verdict and the selection. **Family R is in no rule.**

**R0 PASS, S6 PASS.** No verdict and no selection carries a label.

### 3.2 MM1-v3.2's per-case bands (T1-T3, E1-E4)

> **MM1-v3.2's per-case and per-point rules** (each passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its registered points, FAIL otherwise, TOO FEW under 10, NO DATA with none). **The band is twice the larger of MM1-v3.2's two held-out rms errors without configuration twins** - (i) leave one experiment out over every point, (ii) the same over this card's points - rounded up to a whole percent (E218's rule and bands on this card; MM1-v3.2's held-out record reproduced first: every figure `holdout_v32.json` holds for these quantities equal):

> **Points under about 3 W over idle are scored in watts in E1 and E2** (T-Y2's and Y3's subset points): |W measured - W forecast| <= **0.58 W** (2 x max(0.2598, 0.2868, 0.03079) -> 0.58 W).

| rule | what | band (registered arithmetic) | points within it (of 66; 60 needed) | verdict | the misses by group |
|---|---|---|---|---|---|
| **T1** | cycles an op, the wall | 11% (2 x max(5.295, 4.5281) = 10.59 -> 11%) | 53 | **FAIL** | T-G2 5, G3 4, Y3 3, T-L3 1 |
| **T2** | cycles an op, the counter's mean | 14% (2 x max(6.5118, 5.1384) = 13.02 -> 14%) | 59 | **FAIL** | T-G2 5, G3 1, Y3 1 |
| **T3** | seconds a GEMM | 11% (2 x max(5.295, 4.5281) = 10.59 -> 11%) | 53 | **FAIL** | T-G2 5, G3 4, Y3 3, T-L3 1 |
| **E1** | J over idle given the measured op time and seconds | 10% (2 x max(4.9755, 4.8271) = 9.95 -> 10%) | 57 | **FAIL** | T-G2 7, G3 2 |
| **E2** | J over idle with the seconds forecast | 12% (2 x max(5.7703, 4.9711) = 11.54 -> 12%) | 58 | **FAIL** | T-G2 7, G3 1 |
| **E3** | J with the card at rest given t | 4% (2 x max(1.6196, 1.5539) = 3.24 -> 4%) | 52 | **FAIL** | G3 7, T-G2 7 |
| **E4** | J with the card at rest with the seconds forecast | 10% (2 x max(4.7497, 4.029) = 9.50 -> 10%) | 53 | **FAIL** | T-G2 7, G3 3, Y3 3 |

**All seven FAIL.** Every E1, E2 and E3 miss is a gemmLnc point (T-G2 or G3); T1-T3's and E4's misses are mostly gemmLnc points too, with Y3's subset pairs and one T-L3 point beside them.

### 3.3 The head-to-heads H1-H10 (MM1-v3.2 against MM1-v3 and MM1-v3.1)

> **The head-to-heads** (registered now; their gaps and power in section 1): per case d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - |W - first|, in W), decided when |d| exceeds the tie; the exact two-sided sign test over the decided: '<first> BETTER' or '<second> BETTER' at p < 0.05 (**alpha 0.05**) with at least the rule's minimum decided, NOT DECIDED otherwise, TOO FEW under the minimum, NO DATA with none. **H1-H5** MM1-v3.2 vs MM1-v3 (wall, the counter's mean, seconds, W over idle given t, J over idle with t forecast), **H6-H10** the same against MM1-v3.1, over every registered point (minimum 10).

> **The ties** (E215's ties_of on E218's floors (this card, b445b0f5), never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W)): cycles 0.005 in ln, seconds 0.005, joules 0.01, watts points 0.05 W.

| rule | first vs second | quantity | first closer / second closer / ties | p | verdict |
|---|---|---|---|---|---|
| H1 | MM1-v3.2 vs MM1-v3 | wall cycles | 25 / 27 / 14 | 0.89 | NOT DECIDED |
| H2 | MM1-v3.2 vs MM1-v3 | the counter's mean | 27 / 25 / 14 | 0.89 | NOT DECIDED |
| H3 | MM1-v3.2 vs MM1-v3 | seconds | 24 / 26 / 16 | 0.888 | NOT DECIDED |
| H4 | MM1-v3.2 vs MM1-v3 | W over idle given t | 38 / 3 / 25 | 1.05e-8 | **MM1-v3.2 BETTER** |
| H5 | MM1-v3.2 vs MM1-v3 | J over idle with t forecast | 36 / 3 / 27 | 3.61e-8 | **MM1-v3.2 BETTER** |
| H6 | MM1-v3.2 vs MM1-v3.1 | wall cycles | 20 / 31 / 15 | 0.161 | NOT DECIDED |
| H7 | MM1-v3.2 vs MM1-v3.1 | the counter's mean | 22 / 28 / 16 | 0.48 | NOT DECIDED |
| H8 | MM1-v3.2 vs MM1-v3.1 | seconds | 21 / 30 / 15 | 0.262 | NOT DECIDED |
| H9 | MM1-v3.2 vs MM1-v3.1 | W over idle given t | 17 / 0 / 49 | 1.53e-5 | **MM1-v3.2 BETTER** |
| H10 | MM1-v3.2 vs MM1-v3.1 | J over idle with t forecast | 16 / 2 / 48 | 0.00131 | **MM1-v3.2 BETTER** |

MM1-v3.2 is BETTER than both older models on energy (H4, H5, H9, H10); on time no head-to-head decides (H1-H3, H6-H8: weak by construction, E222.md section 1).

### 3.4 Each candidate's head-to-head against MM1-v3.2 on its own family

> - **HC-posimb** ('MM1-v3.2 + posimb' vs MM1-v3.2) **per pair** of Y3 and T-Y2 (10 pairs): r = the measured ln(wall a / wall b) (each point's mean of its kept runs); d = |r - MM1-v3.2's ln(wall a / wall b)| - |r - posimb's|; decided when |d| exceeds the cycles tie (0.005 in ln); the exact two-sided sign test, alpha 0.05, **at least 6 decided** (two pairs, T's p04 and p05, can never be decided: posimb's predicted gap there, 0.0042, is under the tie). Power from posimb's held-out pair error (0.0329, its K1) and MM1-v3.2's (0.0469): section 1.

> - **HC-AF4** ('MM1-v3.2 + AF4' vs MM1-v3.2) **per point** of G3 and T-G2 (14 gemmLnc points), W over idle given the measured op time (each forecaster's A + B / t_measured); tie the joules tie (0.01 in ln); alpha 0.05; **at least 8 decided** (E218's minimum for its family-G tests). Power from AF4's LOEO error (3.88%) and MM1-v3.2's held-out gemmLnc error (8.43%).

> - **HC-L3S** ('MM1-v3.2 + L3S' vs MM1-v3.2) **per point** of L3b and T-L3 (18 points), the wall cycles an op; tie the cycles tie (0.005 in ln); alpha 0.05; **at least 10 decided**. Power from L3S's EDGE fold ((32, 48] MiB: candidate 4.47%, MM1-v3.2 4.89%).

| rule | cases | candidate closer / MM1-v3.2 closer / ties | decided (minimum) | p | verdict |
|---|---|---|---|---|---|
| HC-posimb | 10 pairs (Y3 5, T-Y2 5) | 5 / 3 / 2 | 8 (6) | 0.727 | NOT DECIDED |
| HC-AF4 | 14 points (G3 7, T-G2 7), W over idle given t | 12 / 2 / 0 | 14 (8) | 0.0129 | **MM1-v3.2 + AF4 BETTER** |
| HC-L3S | 18 points (L3b 10, T-L3 8), wall cycles | 9 / 4 / 5 | 13 (10) | 0.267 | NOT DECIDED |

**HC-AF4: 'MM1-v3.2 + AF4' BETTER.** HC-posimb and HC-L3S: NOT DECIDED, which E222.md section 1 named their expected reading whichever model is right; by the registration's dated note 1 (section 3, reading 3) a NOT DECIDED reads **"not shown", never "rejected"**. HC-AF4 tests AF4 in two regimes only (dated note 1, reading 1): G3's seven points at NB 5-6 in AF4's R4 = 0 regime, and T's seven G2 points past the L3 edge at NB 6.

HC-posimb's pairs (ln(wall a / wall b): measured; MM1-v3.2's frozen forecast; posimb's):

| pair | measured | MM1-v3.2 | 'MM1-v3.2 + posimb' |
|---|---|---|---|
| q01 (q01a / q01b) | +0.1461 | +0.0000 | +0.0406 |
| q02 (q02a / q02b) | +0.1032 | +0.0000 | +0.0332 |
| q03 (q03a / q03b) | +0.0731 | +0.0000 | +0.0301 |
| q04 (q04a / q04b) | -0.0042 | +0.0000 | +0.0296 |
| q05 (q05a / q05b) | -0.0198 | +0.0000 | +0.0288 |
| wp01 (wp01a / wp01b) | +0.0542 | +0.0000 | +0.0289 |
| wp02 (wp02a / wp02b) | +0.0522 | +0.0000 | +0.0289 |
| wp03 (wp03a / wp03b) | -0.0088 | +0.0000 | +0.0289 |
| wp04 (wp04a / wp04b) | +0.0386 | +0.0000 | +0.0042 |
| wp05 (wp05a / wp05b) | +0.0386 | +0.0000 | +0.0042 |

### 3.5 The no-harm rules

> **THE NO-HARM RULES (registered now):** **NH-<candidate>** on every OTHER test group (T-L3, T-Y2, T-G2, T-G2t, L3b, Y3, G3, G3t, less the candidate's own) with at least 5 points with data: the candidate's rms of ln(measured / forecast) less MM1-v3.2's, on the wall cycles and on W over idle given the measured op time (points at 3 W and above), must not exceed **0.5 percentage point** in either; PASS when no group exceeds it, FAIL when one does, NO DATA when no group has enough points.

| rule | verdict | worst excess (percentage points; margin 0.5) | per group: wall excess / W-given-t excess (n) |
|---|---|---|---|
| NH-posimb | **PASS** | +0.000 | G3 +0.000 / +0.000 (7); G3t +0.000 / +0.000 (7); L3b +0.000 / +0.000 (10); T-G2 +0.000 / +0.000 (7); T-G2t +0.000 / +0.000 (7); T-L3 +0.000 / +0.000 (8) |
| NH-AF4 | **PASS** | +0.000 | G3t +0.000 / +0.000 (7); L3b +0.000 / +0.000 (10); T-G2t +0.000 / +0.000 (7); T-L3 +0.000 / +0.000 (8); T-Y2 +0.000 / - (10); Y3 +0.000 / - (10) |
| NH-L3S | **PASS** | +0.483 | G3 +0.483 / +0.081 (7); G3t +0.133 / +0.040 (7); T-G2 +0.024 / +0.012 (7); T-G2t +0.030 / -0.011 (7); T-Y2 +0.000 / - (10); Y3 +0.000 / - (10) |

**All three PASS.** NH-posimb and NH-AF4 cannot FAIL by construction (each term is MM1-v3.2 exactly on every other group; the registration's frozen moves are 0.000): their PASS says nothing about harm. **NH-L3S passes by 0.017 point**: its worst group is G3's wall, +0.483 against the 0.5 margin (G3t +0.133); read beside dated note 1's rates (section 5): a PASS there does not show that L3S does no harm at G3 and G3t.

### 3.6 THE SELECTION RULE's outcome

> **THE SELECTION RULE (SEL), registered now:** **MM1-v3.3 = MM1-v3.2 plus every candidate term whose HC test reads '<candidate> BETTER' and whose NH test reads PASS**; with two or more, their composition only as the registered combination (`desk/models_e222.compose` restricted to the joining terms: each term is exactly MM1-v3.2 outside its domain, so any subset composes the same way, with no refit); with none, MM1-v3.3 = MM1-v3.2 unchanged. A NOT DECIDED or TOO FEW leaves that term out. R0 or S6 FAIL labels the outcome. **The outcome is declared after E222's scores in a dated note; MM1-v3.3's own blind day follows on never-run points.**

**SEL: MM1-v3.3 = MM1-v3.2 + AF4** ("one term"; no label, R0 and S6 PASS). AF4 joins: HC-AF4 reads 'MM1-v3.2 + AF4' BETTER and NH-AF4 PASS. posimb and L3S do not join: HC-posimb and HC-L3S read NOT DECIDED (not shown, never rejected), whatever their no-harm rules read. MM1-v3.3 is MM1-v3.2 with F3 replaced at gemmLnc points by AF4's term (energy only; its time is MM1-v3.2's), with no refit.

## 4. The cross-card rule CX on T (scored now: E220's data are committed and verified)

> **THE CROSS-CARD RULE (CX), registered now, scored only once E220's data are committed and verified** (a verify lane's HOLDS; until then it reads PENDING E220 DATA): per T twin with data here and on that E220 arm's card, for each forecaster (MM1-v3.2, the three candidates, MM1-v3.1, MM1-v3, MM1-v2): e_a3 = |ln(measured here / its frozen E222 forecast)|, e_x = |ln(measured there / its frozen E220 forecast)|, each forecaster's own (E220's `forecast-e220.json` for the four models at arm A's 600.0 and arm B's 799.0 column; the candidates' own E220 files, posimb's, AF4's, L3S's); E220's measured side by E220's frozen scorer's readers at its pin (arm A `read_a`; arm B `read_b`, route c only); d = e_a3 - e_x, decided when |d| exceeds the tie (0.005 in ln for the wall, 0.01 for W over idle given t, twins at 3 W and above on both cards); the exact two-sided sign test: **'LARGER ON aifoundry3' / 'SMALLER ON aifoundry3'** at p < 0.05 with at least 10 decided; per E220 arm (CX-T, CX-E) and pooled over both arms (CXP-T, CXP-E). Its power (REPORTED; both sides' errors drawn |N(0, sigma)|, here k sigma; MM1-v3.2's held-out sigma): the wall at k = 1 / 1.5 / 2 reads LARGER 0.019 / 0.25 / 0.608 (32 twins an arm); W given t 0.018 / 0.187 / 0.443 (22 twins). Family R's repeats against E218 (REPORTED) give this card's day-to-day spread beside it.

**E220 is committed and verified:** arm A (aifoundry1 card 1 at 600 MHz) `fd074f9e`; arm B (aifoundry2 card 0 under its governor) `257496b7`, its route-c reduction `data-e220b.json` committed with its step-13 outputs in `240aa9cf`; the data verifier of E220 read HOLDS (Fri 20 Nov 2026, 16:23 PST) and E220's scores are on main (`b62e5d93`, `240aa9cf`, `e5ae242a`). **The call** (this lane, 01:40:50 PST, in a CPU slot, from a tree exported from the lab's objects at `cfd7e641`, after `sha256sum -c` of `tools/claims-v3/e222/SHA256SUMS-e222-registration` read 30 of 30 OK and the list's own sha256 read `de67150b...`): `score_e222.py --a <this directory>/data-e222.json --a-tag A --labels <this directory>/labels-e222.json --out <dir> --e220-a docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry1-c1/data-e220a.json --e220-b docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry2/data-e220b.json --e220-verified <the E220 data verifier's result file>` (the scorer checks only that the last file exists; E220's labels files label no point, so its optional `--e220-labels` would change nothing). The output equals the data verifier's own cross-check run of the same call byte for byte.

Counts are larger on aifoundry3 / smaller on aifoundry3 / ties (the JSON's `first_closer` / `second_closer` / `ties`: d = e_a3 - e_x); p of the exact sign test; 10 decided needed.

| forecaster | CX-T arm A (wall) | CX-T arm B | CXP-T pooled | CX-E arm A (W given t) | CX-E arm B | CXP-E pooled |
|---|---|---|---|---|---|---|
| MM1-v3.2 | TOO FEW 4/2/26 | NOT DECIDED 16/7/9, p 0.0931 | NOT DECIDED 20/9/35, p 0.0614 | **SMALLER** 1/18/3, p 7.63e-5 | NOT DECIDED 8/14/0, p 0.286 | **SMALLER** 9/32/3, p 4.31e-4 |
| MM1-v3.2 + posimb | TOO FEW 4/2/26 | NOT DECIDED 15/8/9, p 0.21 | NOT DECIDED 19/10/35, p 0.136 | **SMALLER** 1/18/3, p 7.63e-5 | NOT DECIDED 8/14/0, p 0.286 | **SMALLER** 9/32/3, p 4.31e-4 |
| MM1-v3.2 + AF4 | TOO FEW 4/2/26 | NOT DECIDED 16/7/9, p 0.0931 | NOT DECIDED 20/9/35, p 0.0614 | **SMALLER** 1/19/2, p 4.01e-5 | **SMALLER** 1/21/0, p 1.10e-5 | **SMALLER** 2/40/2, p 4.11e-10 |
| MM1-v3.2 + L3S | TOO FEW 4/2/26 | NOT DECIDED 16/8/8, p 0.152 | NOT DECIDED 20/10/34, p 0.0987 | **SMALLER** 1/18/3, p 7.63e-5 | NOT DECIDED 8/14/0, p 0.286 | **SMALLER** 9/32/3, p 4.31e-4 |
| MM1-v3.1 | TOO FEW 4/2/26 | NOT DECIDED 17/9/6, p 0.169 | NOT DECIDED 21/11/32, p 0.11 | **SMALLER** 1/16/5, p 2.75e-4 | NOT DECIDED 8/14/0, p 0.286 | **SMALLER** 9/30/5, p 0.00107 |
| MM1-v3 | TOO FEW 4/2/26 | NOT DECIDED 19/9/4, p 0.0872 | NOT DECIDED 23/11/30, p 0.0576 | **SMALLER** 1/18/3, p 7.63e-5 | NOT DECIDED 8/14/0, p 0.286 | **SMALLER** 9/32/3, p 4.31e-4 |
| MM1-v2 | TOO FEW 4/2/26 | **SMALLER** 6/24/2, p 0.00143 | **SMALLER** 10/26/28, p 0.0113 | NOT DECIDED 4/8/10, p 0.388 | NOT DECIDED 10/12/0, p 0.832 | NOT DECIDED 14/20/10, p 0.392 |

LARGER and SMALLER read LARGER ON aifoundry3 and SMALLER ON aifoundry3. **For MM1-v3.2, pooled over both E220 cards: the wall NOT DECIDED (20/9/35, p 0.0614); W over idle given t SMALLER ON aifoundry3 (9/32/3, p 4.31e-4)**: MM1-v3.2's energy error at T's twins is smaller on this card than on the E220 cards, as for every forecaster but MM1-v2. As registered (E222.md section 8), the twins' errors here and there are both drawn on the day, so a verdict says the errors differ, not why. CX-T on arm A is TOO FEW for every forecaster (most of its twins tie within 0.005 in ln).

## 5. Dated note 1's rates beside NH-L3S, HC-L3S and SEL (`nh-l3s-beside-e222.txt`)

The registration's dated note 1 (`tools/claims-v3/e222-notes/E222.md.dated-note-1.md`, section 2) says "Every NH-L3S verdict is printed with these rates beside it". Its printer ran here at 01:40:50 PST after `sha256sum -c` of its list (`SHA256SUMS-e222-note1`, 8 of 8 OK), on `scores-e222-A.json` (and, the same six lines, on `scores-e222-cx.json`); its lines, verbatim:

```
NH-L3S: PASS (registered rule: margin 0.5 point; worst excess +0.483 point; G3: wall +0.483; G3t: wall +0.133)
   beside it (E222 dated note 1, simulated, REPORTED): P(NH-L3S FAIL) if 'MM1-v3.2 + L3S' is right 0.050/0.085/0.115 at 2/3/5% independent errors; if MM1-v3.2 is right 0.393/0.311/0.256 (it can FAIL only at G3 and G3t, on the wall)
HC-L3S: NOT DECIDED (L3S closer 9, MM1-v3.2 closer 4, ties 5, p 0.266845703125)
SEL: MM1-v3.3 = MM1-v3.2 + AF4
   beside it: P(L3S joins MM1-v3.3) at the registered sigmas: if 'MM1-v3.2 + L3S' is right: 0.140; if MM1-v3.2 is right: 0.000; if L3S is right only on L3b and T-L3: 0.111
READING (E222 dated note 1, section 3): a NOT DECIDED or TOO FEW on HC-posimb or HC-L3S reads 'not shown', never 'rejected'; NH-posimb and NH-AF4 cannot FAIL by construction (a PASS there says nothing about harm); HC-AF4 tests AF4 at G3 (R4 = 0, NB 5-6) and T-G2 only.
```

Read beside them, in that note's words (section 2): "**A PASS does not show that L3S does no harm at G3 and G3t.**" and "**So SEL's L3S clause is mostly HC-L3S.**" L3S's clause in SEL fell on HC-L3S (NOT DECIDED), not on NH-L3S.

## 6. REPORTED (never a verdict): each model's rms per family, family R, the gemmLnc excess, the L3 deltas

> **REPORTED, never a verdict:** every family's and test group's rms and bias of ln(measured / forecast) per forecaster (wall cycles and W given t); the pairs' measured ln(a / b) against every forecaster's; the measured gemmLnc excess (a G3, T-G2 or R-G point's W over idle less its twin's) against MM1-v3.2's F3 and AF4's term; the L3b and T-L3 errors of MM1-v3.2 and L3S with L3S's Delta; family R's ln(E222 / E218) per quantity.

**Wall cycles an op**, rms of ln(measured / forecast) in % (the frozen scorer's `family_stats_REPORTED`; n per group: all 66, T 32, T-L3 8, T-Y2 10, T-G2 7, T-G2t 7, L3b 10, Y3 10, G3 7, G3t 7, R 4):

| model | all registered | T | T-L3 | T-Y2 | T-G2 | T-G2t | L3b | Y3 | G3 | G3t | R |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MM1-v3.2 | 8.38 | 9.04 | 5.44 | 4.33 | 16.78 | 5.62 | 4.76 | 8.61 | 12.04 | 2.29 | 7.18 |
| MM1-v3.2 + posimb | 8.32 | 9.04 | 5.44 | 4.36 | 16.78 | 5.62 | 4.76 | 8.24 | 12.04 | 2.29 | 6.95 |
| MM1-v3.2 + AF4 | 8.38 | 9.04 | 5.44 | 4.33 | 16.78 | 5.62 | 4.76 | 8.61 | 12.04 | 2.29 | 7.18 |
| MM1-v3.2 + L3S | 8.19 | 8.80 | 3.36 | 4.33 | 16.80 | 5.65 | 2.60 | 8.61 | 12.52 | 2.42 | 8.00 |
| MM1-v3.2 + all three | 8.13 | 8.80 | 3.36 | 4.36 | 16.80 | 5.65 | 2.60 | 8.24 | 12.52 | 2.42 | 7.80 |
| MM1-v3.1 | 8.12 | 9.01 | 5.87 | 4.39 | 16.52 | 5.57 | 4.43 | 7.12 | 11.99 | 2.49 | 10.50 |
| MM1-v3 | 8.24 | 9.24 | 5.78 | 4.62 | 16.92 | 5.90 | 4.75 | 7.07 | 11.90 | 2.27 | 9.52 |
| MM1-v2 | 11.51 | 13.17 | 8.24 | 14.33 | 18.60 | 8.71 | 8.10 | 11.18 | 12.94 | 4.07 | 9.30 |

**W over idle given the measured op time**, rms of ln in %, at points of 3 W and more (n: all registered 46, T 22, T-L3 8, T-Y2 0, T-G2 7, T-G2t 7, L3b 10, Y3 0, G3 7, G3t 7, R 2; T-Y2's and Y3's points are all under 3 W, where E1 and E2 score watts):

| model | all registered | T | T-L3 | T-G2 | T-G2t | L3b | G3 | G3t | R |
|---|---|---|---|---|---|---|---|---|---|
| MM1-v3.2 | 10.36 | 13.25 | 2.17 | 23.14 | 3.33 | 1.92 | 11.86 | 2.64 | 3.27 |
| MM1-v3.2 + posimb | 10.36 | 13.25 | 2.17 | 23.14 | 3.33 | 1.92 | 11.86 | 2.64 | 3.27 |
| MM1-v3.2 + AF4 | 5.27 | 2.68 | 2.17 | 2.46 | 3.33 | 1.92 | 12.16 | 2.64 | 0.59 |
| MM1-v3.2 + L3S | 10.38 | 13.25 | 2.09 | 23.15 | 3.32 | 2.13 | 11.94 | 2.68 | 3.42 |
| MM1-v3.2 + all three | 5.31 | 2.65 | 2.09 | 2.47 | 3.32 | 2.13 | 12.23 | 2.68 | 0.65 |
| MM1-v3.1 | 18.58 | 23.86 | 2.56 | 42.05 | 3.61 | 1.91 | 21.54 | 3.09 | 10.42 |
| MM1-v3 | 18.59 | 23.89 | 2.82 | 42.09 | 3.51 | 2.09 | 21.49 | 3.27 | 10.52 |
| MM1-v2 | 17.80 | 22.64 | 4.14 | 39.48 | 5.66 | 3.49 | 21.04 | 3.41 | 10.24 |

**Seconds a GEMM and J with the card at rest given t**, rms of ln in % (the data verifier's own re-derivation, its family table; its wall and W-given-t cells equal the scorer's above):

| model | all registered: s / J at rest | T: s / J at rest | L3b: s / J at rest | Y3: s / J at rest | G3: s / J at rest | G3t: s / J at rest | R: s / J at rest |
|---|---|---|---|---|---|---|---|
| MM1-v3.2 | 8.30 / 3.91 | 8.87 / 4.88 | 4.80 / 0.90 | 8.59 / 0.72 | 12.08 / 5.64 | 2.35 / 1.17 | 7.12 / 1.50 |
| MM1-v3.2 + posimb | 8.24 / 3.91 | 8.87 / 4.88 | 4.80 / 0.90 | 8.21 / 0.72 | 12.08 / 5.64 | 2.35 / 1.17 | 6.89 / 1.50 |
| MM1-v3.2 + AF4 | 8.30 / 1.99 | 8.87 / 1.01 | 4.80 / 0.90 | 8.59 / 0.72 | 12.08 / 5.42 | 2.35 / 1.17 | 7.12 / 0.90 |
| MM1-v3.2 + L3S | 8.09 / 3.92 | 8.61 / 4.88 | 2.59 / 0.99 | 8.59 / 0.72 | 12.55 / 5.68 | 2.46 / 1.19 | 7.95 / 1.54 |
| MM1-v3.2 + all three | 8.03 / 2.00 | 8.61 / 1.00 | 2.59 / 0.99 | 8.21 / 0.72 | 12.55 / 5.45 | 2.46 / 1.19 | 7.74 / 0.90 |
| MM1-v3.1 | 8.03 / 6.60 | 8.83 / 8.34 | 4.48 / 0.88 | 7.08 / 0.70 | 12.02 / 9.45 | 2.53 / 1.37 | 10.45 / 3.80 |
| MM1-v3 | 8.16 / 6.61 | 9.06 / 8.36 | 4.80 / 0.95 | 7.04 / 0.91 | 11.94 / 9.41 | 2.33 / 1.45 | 9.47 / 3.80 |
| MM1-v2 | 11.47 / 6.39 | 13.06 / 7.98 | 8.15 / 1.65 | 11.25 / 1.08 | 12.97 / 9.26 | 4.20 / 1.51 | 9.27 / 3.68 |

Over all 66 points MM1-v3.2's wall rms is 8.38% (bias +2.36%) and its W over idle given t 10.36% (bias +2.41%, n 46); 'MM1-v3.2 + AF4' brings the latter to 5.27% (T-G2 23.14% -> 2.46%; G3 11.86% -> 12.16%); 'MM1-v3.2 + L3S' brings L3b's wall from 4.76% to 2.60% and T-L3's from 5.44% to 3.36%, and moves G3's from 12.04% to 12.52%; 'MM1-v3.2 + posimb' moves Y3's wall from 8.61% to 8.24%.

At those 20 watts points, the data verifier's own figure: watts points (20: T-Y2, Y3) |W - Wg| rms: v3.2 0.161 W, v3.1 0.158, v3 0.208, v2 0.250.

**Family R: E218's points re-run on this card** (ln(E222 / E218) per quantity, each point's mean of its kept runs against E218's committed scorer's; the scorer's `family_R_repeats_REPORTED`, equal to the data verifier's):

| point (E218's) | wall cycles | the counter's mean | W over idle | seconds (the data verifier's) |
|---|---|---|---|---|
| ry01a (y01a) | +0.00007 | +0.00007 | +0.0063 | +0.00002 |
| ry01b (y01b) | +0.00005 | -0.00002 | -0.0089 | +0.00003 |
| rg01 (g01) | +0.00012 | +0.00011 | +0.0110 | -0.00001 |
| rg01t (g01t) | +0.00021 | +0.00021 | -0.0102 | +0.00002 |

This card repeats E218's wall cycles within 0.0003 in ln and its W over idle within 0.011 in ln, about 21 hours later (E218's session 03:11-03:56 PST Fri, E222's 00:06-00:55 PST Sat).

**The measured gemmLnc excess** (a point's W over idle less its cooperative twin's) against MM1-v3.2's F3 and AF4's term, in W (the scorer's `readings_REPORTED`):

| point | twin | measured | MM1-v3.2's F3 | AF4's term | nearer |
|---|---|---|---|---|---|
| wn01 | wn01t | 5.28 | 3.39 | 8.32 | F3 |
| wn02 | wn02t | 6.55 | 3.40 | 8.26 | AF4 |
| wn03 | wn03t | 6.65 | 3.40 | 8.27 | AF4 |
| wn04 | wn04t | 6.17 | 3.40 | 8.27 | AF4 |
| wn05 | wn05t | 5.52 | 3.40 | 8.27 | F3 |
| wn06 | wn06t | 7.99 | 3.42 | 8.15 | AF4 |
| wn07 | wn07t | 7.39 | 3.50 | 7.68 | AF4 |
| k01 | k01t | 4.39 | 3.57 | 2.62 | F3 |
| k02 | k02t | 5.37 | 3.76 | 2.63 | F3 |
| k03 | k03t | 4.32 | 3.87 | 2.83 | F3 |
| k04 | k04t | 4.54 | 4.14 | 2.90 | F3 |
| k05 | k05t | 6.16 | 4.52 | 3.31 | F3 |
| k06 | k06t | 6.03 | 4.67 | 3.27 | F3 |
| k07 | k07t | 6.45 | 4.79 | 3.35 | F3 |

The excess is nearer F3 at 9 of 14 points (all seven G3 points, and wn01, wn05) and nearer AF4's term at 5 (wn02, wn03, wn04, wn06, wn07). HC-AF4 is decided on each point's whole W over idle given its own measured op time, as registered, not on the excess, which also carries the point's and its twin's different op times.

**The L3 deltas** (ln(measured / forecast) of the wall at L3b and T-L3, MM1-v3.2 and 'MM1-v3.2 + L3S', and L3S's frozen move):

| point | group | MM1-v3.2 | 'MM1-v3.2 + L3S' | L3S's move |
|---|---|---|---|---|
| wl01 | T-L3 | +0.1055 | +0.0429 | +0.0625 |
| wl02 | T-L3 | +0.0808 | +0.0328 | +0.0480 |
| wl03 | T-L3 | -0.0227 | -0.0521 | +0.0294 |
| wl04 | T-L3 | +0.0319 | +0.0133 | +0.0186 |
| wl05 | T-L3 | +0.0572 | +0.0436 | +0.0135 |
| wl06 | T-L3 | +0.0115 | -0.0142 | +0.0257 |
| wl07 | T-L3 | -0.0292 | -0.0292 | -0.0000 |
| wl08 | T-L3 | -0.0156 | -0.0156 | -0.0000 |
| b01 | L3b | +0.0752 | +0.0043 | +0.0709 |
| b02 | L3b | +0.0847 | +0.0291 | +0.0556 |
| b03 | L3b | -0.0403 | -0.0034 | -0.0369 |
| b04 | L3b | -0.0233 | -0.0527 | +0.0294 |
| b05 | L3b | +0.0338 | +0.0158 | +0.0180 |
| b06 | L3b | +0.0682 | +0.0083 | +0.0598 |
| b07 | L3b | +0.0206 | -0.0193 | +0.0399 |
| b08 | L3b | -0.0002 | -0.0234 | +0.0232 |
| b09 | L3b | -0.0022 | -0.0170 | +0.0148 |
| b10 | L3b | +0.0378 | +0.0398 | -0.0020 |

L3S's forecast is the nearer at 12 of 18 points (HC-L3S counts only differences past the 0.005 tie: 9 / 4 / 5).

## 7. The data verifier's re-derivation, beside (verify-e222d: HOLDS)

The data verifier re-derived E222's card day from the committed raw files with its own code (it imports nothing from the kit, the models or E220's scorer) and scored every registered rule against the frozen forecasts after checking their sha256:

- measured side from raw (own code): 120 runs + s01 + s03, 1,548 counted launches (0 excluded by the clock band); 840/840 run fields = data-e222.json; 770/770 point fields = RB_OUT scores' measured; 630/630 README values + 3 tie rows; order 122/122 = plan-e222.json.
- R0 PASS (122 checks approx, 122/122 GATE OK, 22/22 walks + s03); S6 PASS (29,234/29,234 samples at 600 MHz).
- bands MM1-v3.2: T1 53, T2 59, T3 53, E1 57, E2 58, E3 52, E4 53 of 66, all FAIL (60 needed); 462/462 cells = scorer.
- H1 25/27/14 p 0.89, H2 27/25/14 p 0.89, H3 24/26/16 p 0.89 NOT DECIDED; H4 38/3/25 p 1.05e-8, H5 36/3/27 p 3.61e-8 MM1-v3.2 BETTER (vs v3).
- H6 20/31/15 p 0.16, H7 22/28/16 p 0.48, H8 21/30/15 p 0.26 NOT DECIDED; H9 17/0/49 p 1.53e-5, H10 16/2/48 p 0.00131 MM1-v3.2 BETTER (vs v3.1).
- HC-AF4: 'MM1-v3.2 + AF4' BETTER 12/2/0 of 14, p 0.0129 (T-G2 7/7 by +0.18 to +0.22 ln; G3 5/7); NH-AF4 PASS (0.000, vacuous).
- HC-L3S: NOT DECIDED 9/4/5 of 18, p 0.267 ('not shown'); NH-L3S PASS, worst +0.483 point at G3 wall (margin 0.5); dated note 1: P(FAIL) 0.050/0.085/0.115 if L3S right, 0.393/0.311/0.256 if v3.2 right.
- HC-posimb: NOT DECIDED 5/3/2 of 10 pairs, p 0.727 ('not shown'); NH-posimb PASS (0.000, vacuous).
- SEL: MM1-v3.3 = MM1-v3.2 + AF4 (one term); P(L3S joins) 0.140 / 0.000 / 0.111 (dated note 1).
- CX (own, = frozen scorer cross-check 42/42): MM1-v3.2 CX-T A TOO FEW 4/2/26, B NOT DECIDED 16/7/9; CXP-T NOT DECIDED 20/9/35 p 0.061; CX-E A SMALLER ON aifoundry3 1/18/3 p 7.6e-5, B NOT DECIDED 8/14/0; CXP-E SMALLER ON aifoundry3 9/32/3 p 4.3e-4; +AF4 CXP-E SMALLER 2/40/2 p 4.1e-10; MM1-v2 CXP-T SMALLER 10/26/28 p 0.011.
- family R vs E218 (REPORTED, both re-derived from raw): ln wall +0.00005..+0.00021, mean -0.00002..+0.00021, seconds -0.00001..+0.00003, W -0.0102..+0.0110.
- files: SHA256SUMS 647/647; raw copy-back = box MANIFEST 637/637; committed session = raw (395) or raw after own scrub (245), 0 unexplained; scrub 0 hits in 649 files.

This lane's checks of the scorer's two JSONs against the data verifier's own files: every verdict but CX equal (26 of 26), every band count, every head-to-head's counts and p, the three candidates' tests, the no-harm verdicts and worst excesses, SEL and its joining term, the 42 cross-card cells (counts, ties, verdicts and p), the family table's wall and W-given-t cells and family R's repeats: 671 comparisons, 0 differ.

## 8. Dated clauses (Sat 21 Nov 2026; findings answered; nothing above changes)

1. **The rates beside NH-L3S** (the data verifier's finding 1, low). Dated note 1 says the card lane's step 13 runs its printer; the kit's frozen step 13 could not (the note landed outside its pinned folder; the readiness lane's go lines moved the printer to the lanes after the card). *Answered:* `nh-l3s-beside-e222.txt` is that printer's output, committed beside the scores (section 5).
2. **CX was PENDING** (its finding 2, low). Step 13 printed "CX: PENDING E220 DATA", as its kit must. *Answered:* `scores-e222-cx.*` is the frozen scorer's registered cross-card call with E220's committed and verified data (section 4), equal byte for byte to the data verifier's own cross-check run; its own code's CX equals it in 42 of 42 cells.
3. **NH-L3S is a near-miss** (its finding 3, info): +0.483 point against the 0.5 margin at G3's wall. *Answered:* stated beside the verdict (sections 3.5 and 5); SEL does not depend on it, because HC-L3S is NOT DECIDED.
4. **The gemmLnc excess** (its finding 4, info): nearer F3 at 9 of 14 points, all seven G3 among them. *Answered:* tabled in section 6 from the scorer's own reading. HC-AF4 stands as registered; AF4's form is tested again on MM1-v3.3's own blind day, E224, registered before this day's data and scored by its own lanes.
5. **Two README wordings** (its finding 5, nit; checked here). (a) The ties' heading reads "the day offset the scorer reads": E222's frozen scorer reads the ties (t01) for R0 only, their checks of C, and applies no day offset (it imports E220's `read_a`, which reads ties and smoke runs for R0 alone). (b) The README gives the shires' mean peak as "55 C at 00:53:07": in the committed telemetry (29,234 samples) 67 samples read 55 C, the first at 00:49:32 PST and the last at 00:53:07 PST. *Answered* by this clause; the README is not edited.
6. **The collect spans overlapped** (its finding 6, info): the card lane's collect span (00:55:39-00:57:53 PST) overlapped E224 arm B's by about 20-40 s; the two pushes were serial, new files only, on disjoint paths (`087f9baa`, then `cfd7e641` on it). *Recorded*; no file of this directory is affected.
7. **The booking's reading of row B** (its finding 7 and the card lane's own, low; README departure 13): E224's seal hold stood on aifoundry1 and aifoundry2 only and was released at 23:33:15 PST, before G (00:00:36): either reading gives the same G. *Recorded.*
8. **Step 6n's literal reading** (the card lane's finding, low; README departure 16) read 0 of 70 never ran, against 47 of 70 at the readiness lane; it is REPORTED, never a label. The judgement by session records on this card stands: 66 of 66 non-R points never ran, family R RAN (exempt by name), the positive control 4 of 4. *Recorded.*
9. **The data commit's message** (the card lane's finding, nit): its generator cut step 6n's line mid-word; the card lane rewrote the body by hand and scanned it again before the commit. *Recorded*; no file is affected.
10. **Two roundings of one rate** (this lane, nit). The printer's "0.311" (MM1-v3.2 right, 3% errors) is dated note 1's Table 1 "0.312": the same simulated rate, 0.3115 in `nh-l3s-e222-note1.json`, rounded two ways. The readiness lane's go lines quoted "0.05/0.085/0.125" (the registration verifier's own 5% figure); the note's own simulation, which the printer reads, gives 0.115. *Recorded*; no reading changes.

## 9. How this note was made, and what was not run

- **Where and how.** On aifoundry2 (the round's desk), `/usr/bin/python3` 3.12.3 with `-I -B`; every numerical job single-threaded inside the round's CPU slots, one at a time (the re-run, the cross-card call, the printer, the facts and this note's build). Git reads only in the lab clone; the calls ran on a tree exported from the lab's objects at `cfd7e641`. No card and no box was touched.
- **Facts.** Every number here was read from the two scorer JSONs and the printer's output by this lane's facts step, and compared with the data verifier's own files (section 7).
- **NOT RUN here:** a re-derivation from the raw session files (the data verifier's: section 7); the bootstrap or power simulations; dated note 1's simulation (only its printer); the never-run scanner (step 6n's committed reports are read as they stand); any scoring of the model session's forecasts (none was registered for E222).

SPDX-License-Identifier: Apache-2.0
