# E220 arm A data, dated note 1: the frozen scorer's output, committed beside the data byte for byte - R0 and S6 PASS; T1 PASS 76/84, T2 FAIL 75/84, T3 PASS 78/84, E1-E4 FAIL 72-74/84; H1-H5 MM1-v3.2 BETTER than MM1-v3; against MM1-v3.1 H7, H9 and H10 MM1-v3.2 BETTER, H6 and H8 NOT DECIDED; CX-T TOO FEW, CX-E NOT DECIDED; with verify-e220d's re-derivation beside each result

*Fri 20 Nov 2026 (week 47), PST; written from about 16:40 PST by Q233's lane `scores-e220` at the desk on aifoundry2, under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It comes after this directory's data commit `fd074f9e` (committed 15:41:40 PST, pushed 15:41:45 PST) and after the day's data verifier `verify-e220d` (HOLDS, 16:23 PST: both arms re-derive bit-equal from their raw records, its own scoring equals each frozen scorer in every verdict, count, p and cell, and it asks for no change to the record; no fix lane ran, since it held). This note adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. The pooled rules over both arms (HP1-HP10, CXP-T, CXP-E) are dated note 17 of arm B's data directory, [`2026-11-20-e220-blind-matmul-aifoundry2/README.md.dated-note-17.md`](../2026-11-20-e220-blind-matmul-aifoundry2/README.md.dated-note-17.md); arm B's own scores are its dated note 16.* **Labels:** **BLIND** (every forecast E220 scores was frozen before either arm's first device access: MM1-v3.2's land `4e386f75`, committed 19:50:04 PST Thu 19 Nov 2026, and E220's registration `6901854c`, committed 12:31:40 PST and pushed 12:31:45 PST Fri 20 Nov 2026, with MM1-v3.1's, MM1-v3's and MM1-v2's E220 forecasts, the points, the bands, the rules and the scorer; the model session's sealed forecast was registered in `d5df9568`, committed 14:44:58 PST, before both bookings at 14:50:53 PST, and none of its numbers is read here; arm A's first device access was fwgate's read at 14:53:55 PST, arm B's at 14:57:42 PST), **measured** (the committed records), **registered** (E220.md, its dated note 1 and its kit), **REPORTED** (a reading, never a verdict), **post hoc** (anything read after the data), **desk** (a check of code at the desk).

## 1. The files this note adds

Four new files beside the data commit's 614. The first two are runbook step 13's outputs, copied byte for byte from the card lane's run folder (RB_OUT):

| file | what | bytes | sha256 | label |
|---|---|---|---|---|
| `scores-e220-A.json` | the frozen scorer [`tools/claims-v3/e220/score_e220.py`](../../../../tools/claims-v3/e220/score_e220.py) (`3c771990...`) on `data-e220a.json` with step 6n's `labels-e220.json`: every verdict, every cell of T1-T3 and E1-E4, every head-to-head and cross-card tally, the measured table it scored, and the REPORTED family table and readings | 108,265 | `7597be0103af6162...` | BLIND (its REPORTED parts never verdicts) |
| `scores-e220-A.txt` | the scorer's printed lines: the step's capture of the scorer's call, which the step copies (53 lines) | 870 | `b745141c4e71f90d...` | printed lines |
| `README.md.dated-note-1.md` | this note | - | - | dated note |
| `SHA256SUMS-note1` | the three files above, then `README.md` and `SHA256SUMS` as the data commit holds them (5 lines; `README.md` is in no other list here, the form of E215 arm B's directory) | - | - | - |

## 2. Where they come from: step 13 on the data commit (this lane's desk checks)

- **The step.** The card lane `card-e220a` ran the kit's step 13, [`tools/claims-v3/e220/rb/s24_score_e220a.sh`](../../../../tools/claims-v3/e220/rb/s24_score_e220a.sh) `A` (in the kit's list `SHA256SUMS-e220-kit`), inside a CPU slot after the data commit, as the card-lane brief's row 13 says (the round's slot log: one job, slot 2, 15:41:51 PST, ended rc 0 the same second). The runbook log's last six lines are the step's six calls, each rc 0 and all from one process (its six captures share one process id): (1) the data directory committed (a commit names it): `fd074f9eb E220 arm A data: ...`, the data commit; (2) the directory clean: nothing printed; (3) the data's `SHA256SUMS`: 612 of 612 entries OK; (4) the history check: "HISTORY OK: HEAD descends from the registration 6901854c4da4 (subtree 46dde0fd); 123 additions and nothing else under tools/claims-v3/e220 since it; ..."; (5) step 6n's labels: "LABELS-OK: 0 label(s) of arm A's registered points (none)"; (6) the frozen scorer on the committed `data-e220a.json` with `--a-tag A --labels labels-e220.json`, whose printed lines (below) are `scores-e220-A.txt` and whose JSON is `scores-e220-A.json`. The six commands are exactly those `s24_score_e220a.sh A` writes.
- **The commit it read.** `fd074f9e` was committed at 15:41:40 PST and pushed by 15:41:45 PST. The lab clone's reflog holds HEAD at `fd074f9e` from 15:41:40 to its next move at 15:44:26 PST (arm B's data commit), so the step (15:41:51) ran on it. This data directory (tree `4c8df560`), the kit's folder and the notes folder are unchanged from `fd074f9e` to this note's parent.
- **The scorer and its inputs, at their pins.** `score_e220.py` is `3c771990...` at `fd074f9e` and at HEAD. It refuses (exit 4) unless `points-e220.json`, `forecast-e220.json` and `rules-e220.json` read the sha256 the registration's list `SHA256SUMS-e220-registration` records; each does at the data commit (`2451ca9d`, `dd317667`, `5557d8b2`). The step's scripts `rb/s24_score_e220a.sh`, `rb/rb_e220a.sh`, `rb/check_history_e220a.py` and `desk/neverrun_card_e220.py` read their kit-list sha256 there. `sha256sum -c` from the lab's top reads `SHA256SUMS-e220-registration` 29 of 29 and `SHA256SUMS-e220-kit` 120 of 120 at HEAD.
- **The labels.** Step 6n's committed `labels-e220.json` names no point (`"ran_before_points": {"A": []}`), by E220's dated note 1's reading.
- **The bytes and the times.** The scorer wrote its JSON and text at 15:41:51.54 PST into its own output folder in RB_OUT, and the step copied both into RB_OUT's `scores-e220-A.json` and `.txt` at 15:41:51.55; the copies are byte for byte the scorer's, and the text is the step's capture 6 byte for byte. The JSON is in `main()`'s dump form (one-space indent, sorted keys), and the text is `main()`'s lines from its verdicts. The two sha256 are the ones card-e220a's and verify-e220d's results name. The slot log shows no run of the scorer on an arm's data before this step.
- **Made again.** This lane ran call 6 again, unchanged and in a CPU slot, on a tree exported from the lab clone's own objects at `fd074f9e`. The JSON, the text and the printed lines came out byte for byte equal to RB_OUT's and to the step's capture. The frozen scorer's own functions (`cells_of()`, `verdict()`, `h_cases()`, `decide()`, `cx_cases()`, `family_stats()`, `readings()`), called on the JSON's measured table, give every cell, verdict, tally, family figure and reading in it. verify-e220d made the same file from the committed bytes on its own, byte for byte, and scored every rule with its own code (section 10).

**The scorer's printed lines** (`scores-e220-A.txt`, all of it):

```
A:CX-E: NOT DECIDED
A:CX-T: TOO FEW
A:E1: FAIL
A:E2: FAIL
A:E3: FAIL
A:E4: FAIL
A:H1: MM1-v3.2 BETTER
A:H10: MM1-v3.2 BETTER
A:H2: MM1-v3.2 BETTER
A:H3: MM1-v3.2 BETTER
A:H4: MM1-v3.2 BETTER
A:H5: MM1-v3.2 BETTER
A:H6: NOT DECIDED
A:H7: MM1-v3.2 BETTER
A:H8: NOT DECIDED
A:H9: MM1-v3.2 BETTER
A:R0: PASS
A:S6: PASS
A:T1: PASS
A:T2: FAIL
A:T3: PASS
B:CX-E: NO DATA
B:CX-T: NO DATA
B:E1: NO DATA
B:E2: NO DATA
B:E3: NO DATA
B:E4: NO DATA
B:H1: NO DATA
B:H10: NO DATA
B:H2: NO DATA
B:H3: NO DATA
B:H4: NO DATA
B:H5: NO DATA
B:H6: NO DATA
B:H7: NO DATA
B:H8: NO DATA
B:H9: NO DATA
B:R0: NO DATA
B:T1: NO DATA
B:T2: NO DATA
B:T3: NO DATA
CXP-E: NOT DECIDED
CXP-T: TOO FEW
HP1: MM1-v3.2 BETTER
HP10: MM1-v3.2 BETTER
HP2: MM1-v3.2 BETTER
HP3: MM1-v3.2 BETTER
HP4: MM1-v3.2 BETTER
HP5: MM1-v3.2 BETTER
HP6: NOT DECIDED
HP7: MM1-v3.2 BETTER
HP8: NOT DECIDED
HP9: MM1-v3.2 BETTER
```

The `B:` lines read NO DATA: this call had no arm B input. **The `HP1`-`HP10`, `CXP-T` and `CXP-E` lines are arm A alone, not the registered pooled reading** (clause 1 of section 11).

## 3. The registered rules' words, and the verdicts (BLIND)

**R0 and S6.** The words: "R0 (every check of C exact or approx; the smoke good; the G block's smoke s03 failing while no gemmLnc point ran is flagged, not an R0 failure) and, arm A, S6 (every kept run's samples at 590-610 MHz): a FAIL labels every other verdict of its arm and of the pooled tests." Arm A: **R0 PASS** (no failure; the smoke s01's check of C read approx and the G block's smoke s03's approx, so nothing is flagged) and **S6 PASS** (every kept run's samples at 590-610 MHz; verify-e220d: "25,988/25,988 samples at 600 MHz", measured). No verdict carries a label.

**The per-case and per-point rules.** The words: MM1-v3.2's rules, per arm: "each passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its scored cases or points, FAIL otherwise, TOO FEW under 10, NO DATA with none". "The band is twice the larger of MM1-v3.2's two held-out rms errors without configuration twins" (E218's rule). "Points under about 3 W over idle are scored in watts in E1 and E2" (arm A within 0.52 W); "E3 and E4 stay relative." The ties on arm A: cycles 0.005 in ln, seconds 0.005 in ln, joules 0.01 in ln, watts points 0.05 W. With 84 points, 76 must pass.

| rule | what | band | passes / scored (needed) | verdict | the misses by family | the misses (measured / forecast - 1; a watts cell: measured - forecast, in W) |
|---|---|---|---|---|---|---|
| **T1** | cycles an op, the wall | 12% | 76 / 84 (76) | **PASS** | G2/G2-NB56 5, X/XG 3 | n01 +21.84%, n02 +13.62%, n03 +13.91%, n04 +20.37%, n05 +21.03%, xg03 -12.07%, xg05 -12.91%, xg11 +18.55% |
| **T2** | cycles an op, the counter's mean | 14% | 75 / 84 (76) | **FAIL** | G2/G2-NB56 4, X/XY 4, X/XG 1 | n01 +22.65%, n03 +14.64%, n04 +21.20%, n05 +21.81%, xg11 +19.53%, xy01a +14.79%, xy04a +25.98%, xy05a +30.75%, xy06a +25.98% |
| **T3** | seconds a GEMM | 12% | 78 / 84 (76) | **PASS** | G2/G2-NB56 4, X/XG 2 | n01 +21.31%, n03 +14.42%, n04 +19.48%, n05 +19.42%, xg05 -12.81%, xg11 +19.21% |
| **E1** | J over idle given the measured op time and seconds | 12% (watts cells 0.52 W) | 72 / 84 (76) | **FAIL** | G2/G2-NB56 7, X/XG 3, X/XY 2 | n01 +27.68%, n02 +28.69%, n03 +30.58%, n04 +29.69%, n05 +29.42%, n06 +30.27%, n07 +30.80%, xg04 +28.52%, xg08 +34.89%, xg11 +17.43%, xy04a +0.56 W, xy05a +0.58 W |
| **E2** | J over idle with the seconds forecast | 12% (watts cells 0.52 W) | 74 / 84 (76) | **FAIL** | G2/G2-NB56 7, X/XG 3 | n01 +29.31%, n02 +27.91%, n03 +32.60%, n04 +30.79%, n05 +29.81%, n06 +28.86%, n07 +31.55%, xg04 +30.14%, xg08 +34.64%, xg11 +19.67% |
| **E3** | J with the card at rest given t | 4% | 74 / 84 (76) | **FAIL** | G2/G2-NB56 7, X/XG 3 | n01 +10.24%, n02 +11.04%, n03 +11.76%, n04 +11.07%, n05 +10.93%, n06 +11.89%, n07 +12.08%, xg04 +11.35%, xg08 +13.60%, xg11 +6.85% |
| **E4** | J with the card at rest with the seconds forecast | 10% | 74 / 84 (76) | **FAIL** | G2/G2-NB56 7, X/XG 3 | n01 +24.62%, n02 +18.42%, n03 +21.93%, n04 +24.15%, n05 +23.71%, n06 +16.56%, n07 +19.44%, xg04 +18.41%, xg08 +19.62%, xg11 +19.41% |

Every miss is listed by its point id, and counted by its family and subfamily (`points-e220.json`); the cell figures are the scorer's (`scores-e220-A.json` > `arms` > `A` > `cells`).

## 4. The head-to-heads (BLIND)

The words: "per case d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - |W - first|, in W), decided when |d| exceeds the arm's tie; the exact two-sided sign test over the decided: 'MM1-v3.2 BETTER' or '<second> BETTER' at p < 0.05 with at least 10 decided, NOT DECIDED otherwise, TOO FEW under 10, NO DATA with none." "H1-H5 MM1-v3.2 vs MM1-v3: wall, the counter's mean, seconds (per case), W over idle given the measured op time (Wg; per point), J over idle with t forecast (Jf; per point), over every registered point of the arm; H6-H10 the same against MM1-v3.1; HP1-HP10 the same pooled over both arms' points, each case with its own arm's tie."

| rule | quantity | MM1-v3.2 against | over | MM1-v3.2 closer / the other closer / ties | p (exact, two-sided) | the scorer's verdict | verify-e220d (own code) |
|---|---|---|---|---|---|---|---|
| **H1** | the wall cycles | MM1-v3 | 84 | 49/22/13 | 0.00182 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H2** | the counter's mean | MM1-v3 | 84 | 48/17/19 | 1.52e-4 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H3** | seconds | MM1-v3 | 84 | 49/22/13 | 0.00182 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H4** | W over idle given t | MM1-v3 | 84 | 58/2/24 | 3.18e-15 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H5** | J over idle, t forecast | MM1-v3 | 84 | 46/2/36 | 8.36e-12 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H6** | the wall cycles | MM1-v3.1 | 84 | 39/25/20 | 0.103 | **NOT DECIDED** | the same counts, p and verdict |
| **H7** | the counter's mean | MM1-v3.1 | 84 | 39/19/26 | 0.0119 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H8** | seconds | MM1-v3.1 | 84 | 39/25/20 | 0.103 | **NOT DECIDED** | the same counts, p and verdict |
| **H9** | W over idle given t | MM1-v3.1 | 84 | 35/2/47 | 1.02e-8 | **MM1-v3.2 BETTER** | the same counts, p and verdict |
| **H10** | J over idle, t forecast | MM1-v3.1 | 84 | 36/2/46 | 5.40e-9 | **MM1-v3.2 BETTER** | the same counts, p and verdict |

On arm A: MM1-v3.2 BETTER: H1, H2, H3, H4, H5, H7, H9, H10; NOT DECIDED: H6, H8. H6 and H8 (the wall cycles and the seconds against MM1-v3.1) read 39/25/20 and 39/25/20, p 0.103 and 0.103. E220.md section 8, stated before the data: "a NOT DECIDED says the models' time forecasts are close, not that they are equally good".

## 5. The cross-card rule (BLIND), with dated note 1's rates beside

The words: "per X twin with data on the arm and in E218 (aifoundry3 card 0), e_here = |ln(measured / MM1-v3.2's frozen forecast)| on this card at its registered clock and e_a3 = the same in E218"; "d = e_here - e_a3, decided when |d| exceeds the arm's tie; the exact two-sided sign test over the decided: 'LARGER HERE' (MM1-v3.2's error larger on this card) or 'SMALLER HERE' at p < 0.05 with at least 10 decided, NOT DECIDED otherwise, TOO FEW under 10, NO DATA with none." "CX-T the wall cycles an op; CX-E W over idle given the measured op time, at the twins measured at 3 W and above on both cards; per arm, and pooled (CXP-T, CXP-E)." "REPORTED beside: the per-twin ln(measured here / measured on aifoundry3) of the wall cycles (the card offset; MM1-v3.2's time has no per-card term)."

| rule | twins | larger here / larger on aifoundry3 / ties | p | the scorer's verdict | verify-e220d |
|---|---|---|---|---|---|
| **CX-T** (wall cycles) | 52 | 0/4/48 | - | **TOO FEW** | the same |
| **CX-E** (W over idle given t, 3 W and above on both cards) | 41 | 21/12/8 | 0.163 | **NOT DECIDED** | the same |

The card offset (REPORTED; "MM1-v3.2's time has no per-card term"): ln(measured wall here / measured wall on aifoundry3) over 52 twins, median -0.0016, mean -0.0034 (card 1 at 600 MHz against aifoundry3 card 0 at 600 MHz); 48 of the 52 twins tie in the wall error. Dated note 1's printer ([`cx_null_e220_note1.py`](../../../../tools/claims-v3/e220-notes/cx_null_e220_note1.py) `beside`, as the note says: "The card lanes run it at step 13 and the scores lane runs it with the pooled verdicts."), run by the card lane at step 13 on `scores-e220-A.json`, printed (made again here byte for byte):

```
A:CX-E: NOT DECIDED (41 twins, 21 larger here, 12 larger on aifoundry3, p 0.16275565745308995) | dated note 1: false LARGER HERE at equal distribution 0.0032 (resampled aifoundry3 errors), at equal rms with normal errors 0.1084 (registered 0.095)
B:CX-E: NO DATA (0 twins, 0 larger here, 0 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0019 (resampled aifoundry3 errors), at equal rms with normal errors 0.3379 (registered 0.331)
CXP-E: NOT DECIDED (41 twins, 21 larger here, 12 larger on aifoundry3, p 0.16275565745308995) | dated note 1: false LARGER HERE at equal distribution 0.0033 (resampled aifoundry3 errors), at equal rms with normal errors 0.4986
A:CX-T: TOO FEW (52 twins, 0 larger here, 4 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0039 (resampled aifoundry3 errors), at equal rms with normal errors 0.0088 (registered 0.009)
B:CX-T: NO DATA (0 twins, 0 larger here, 0 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0039 (resampled aifoundry3 errors), at equal rms with normal errors 0.0021 (registered 0.004)
CXP-T: TOO FEW (52 twins, 0 larger here, 4 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0052 (resampled aifoundry3 errors), at equal rms with normal errors 0.0089
CX-BESIDE-E220-NOTE1: 6 cross-card verdict(s) printed with the null rates beside
```

Its `B:` lines read NO DATA and its `CXP-` lines are arm A alone (clause 1). Dated note 1: "On arm A the two rates are 0.11 and 0.003."

## 6. MM1-v3.2 point by point, at the zero-slack verdict (BLIND)

T1 passes with no slack: 76 of 84 pass and 76 are needed. Its closest pass is xg02 at -11.990% against the 12% band, and its closest miss xg03 at -12.067%. verify-e220d's reading of such verdicts: "Each would flip at the card's repeat-noise level (E208's session-repeat floor: cycles rms 0.38%, energy 0.7-1.2%)". It is exact as registered and stands (clause 2).

## 7. Each model's error by family and subfamily (REPORTED; the scorer's table, `family_stats_REPORTED`)

The words: "every family and subfamily: each model's rms and bias of ln(measured / forecast), wall cycles and W given t; route m on arm B; the twins' card offset." Each cell is rms (bias) of ln(measured / forecast) in %, over the points with data; W over idle given t counts only points at 3 W and above on both sides. verify-e220d's own code gives every figure (244 groups over both arms, 0 differ).

The wall cycles:

| family / subfamily | n | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| X | 52 | 6.95 (-1.64) | 10.38 (-3.89) | 9.68 (-3.22) | 11.98 (+0.44) |
| X/XF | 14 | 7.30 (-6.29) | 13.73 (-11.77) | 12.66 (-10.77) | 11.87 (-9.27) |
| X/XG | 12 | 10.57 (-3.07) | 13.72 (-5.80) | 12.83 (-5.01) | 12.98 (-4.72) |
| X/XGt | 11 | 2.62 (+0.66) | 5.20 (-1.52) | 4.39 (-0.86) | 5.47 (+0.51) |
| X/XY | 15 | 4.80 (+2.18) | 5.18 (+3.27) | 5.42 (+3.53) | 14.48 (+13.58) |
| L3 | 8 | 5.40 (+2.62) | 5.88 (+1.46) | 5.78 (+2.06) | 8.20 (+3.37) |
| L3/L3-1 | 5 | 6.63 (+4.97) | 6.33 (+5.11) | 6.70 (+5.42) | 9.92 (+7.16) |
| L3/L3-2 | 3 | 2.10 (-1.29) | 5.04 (-4.64) | 3.79 (-3.53) | 3.90 (-2.95) |
| Y2 | 10 | 4.36 (+0.79) | 4.42 (+1.64) | 4.65 (+2.03) | 14.36 (+13.78) |
| Y2/Y2-pair | 6 | 4.96 (-0.44) | 4.51 (+0.18) | 4.71 (+0.61) | 12.07 (+11.54) |
| Y2/Y2-control | 4 | 3.25 (+2.63) | 4.28 (+3.84) | 4.56 (+4.14) | 17.23 (+17.13) |
| G2 | 7 | 15.27 (+14.74) | 15.03 (+14.65) | 15.43 (+15.01) | 17.07 (+16.46) |
| G2/G2-NB56 | 7 | 15.27 (+14.74) | 15.03 (+14.65) | 15.43 (+15.01) | 17.07 (+16.46) |
| G2t | 7 | 5.62 (+5.56) | 5.56 (+5.45) | 5.90 (+5.81) | 8.72 (+8.58) |
| G2t/G2t-NB56 | 7 | 5.62 (+5.56) | 5.56 (+5.45) | 5.90 (+5.81) | 8.72 (+8.58) |
| **all** | 84 | 7.55 (+1.02) | 9.68 (-0.40) | 9.30 (+0.18) | 12.27 (+4.32) |

W over idle given t:

| family / subfamily | n | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| X | 41 | 7.65 (-1.66) | 16.67 (+4.89) | 16.58 (+4.46) | 16.69 (+5.97) |
| X/XF | 14 | 4.33 (-4.15) | 5.37 (-5.02) | 5.95 (-5.68) | 3.42 (-3.15) |
| X/XG | 12 | 12.75 (+3.02) | 29.93 (+26.85) | 29.58 (+26.49) | 30.34 (+27.93) |
| X/XGt | 11 | 3.99 (-3.72) | 4.65 (-4.38) | 5.00 (-4.77) | 4.27 (-3.60) |
| X/XY | 4 | 1.50 (-1.35) | 1.09 (-0.87) | 0.96 (-0.71) | 1.86 (-1.70) |
| L3 | 8 | 2.57 (-1.60) | 3.17 (-2.37) | 3.80 (-3.07) | 3.52 (+1.90) |
| L3/L3-1 | 5 | 2.83 (-1.38) | 3.19 (-1.97) | 3.92 (-2.80) | 4.15 (+3.28) |
| L3/L3-2 | 3 | 2.06 (-1.97) | 3.13 (-3.02) | 3.59 (-3.51) | 2.11 (-0.40) |
| Y2 | 0 | - | - | - | - |
| Y2/Y2-pair | 0 | - | - | - | - |
| Y2/Y2-control | 0 | - | - | - | - |
| G2 | 7 | 25.93 (+25.92) | 44.48 (+44.46) | 44.20 (+44.19) | 42.31 (+42.29) |
| G2/G2-NB56 | 7 | 25.93 (+25.92) | 44.48 (+44.46) | 44.20 (+44.19) | 42.31 (+42.29) |
| G2t | 7 | 5.14 (-5.08) | 5.09 (-4.97) | 5.31 (-5.22) | 6.55 (-6.45) |
| G2t/G2t-NB56 | 7 | 5.14 (-5.08) | 5.09 (-4.97) | 5.31 (-5.22) | 6.55 (-6.45) |
| **all** | 63 | 10.80 (+1.03) | 20.12 (+7.27) | 20.03 (+6.84) | 19.66 (+8.11) |

Every point, each model's rms (bias), desk arithmetic in verify-e220d's definitions (equal to its figures):

| quantity | scope (n) | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| wall cycles | arm A (84) | 7.55 (+1.02) | 9.68 (-0.40) | 9.30 (+0.18) | 12.27 (+4.32) |
| the counter's mean | arm A (84) | 8.96 (+2.48) | 10.81 (+1.06) | 10.53 (+1.64) | 14.19 (+5.78) |
| seconds | arm A (84) | 7.42 (+1.05) | 9.56 (-0.37) | 9.18 (+0.21) | 12.21 (+4.34) |
| W over idle given t (3 W and above) | arm A (63) | 10.80 (+1.03) | 20.12 (+7.27) | 20.03 (+6.84) | 19.66 (+8.11) |
| J over idle, t forecast (3 W and above) | arm A (63) | 11.02 (+1.14) | 20.35 (+7.20) | 20.29 (+6.84) | 20.23 (+8.34) |
| J at rest given t (every point) | arm A (84) | 3.90 (+0.47) | 6.99 (+2.38) | 6.97 (+2.32) | 6.89 (+2.77) |

## 8. The leads, reported per family (REPORTED readings, never verdicts)

**L3** (the L3 edges). The words: "L3: MM1-v3.2's ln(measured / forecast) of the wall cycles per point by edge and side (does the miss above x1 repeat: the L3-1 points above x1 slower than forecast, those below not)".

| point | shape | edge | side | footprint (MB) | MM1-v3.2 ln(measured / forecast), wall |
|---|---|---|---|---|---|
| l01 | gemmL10x1x1 | L3-1 | above | 41.0 | +0.1047 |
| l02 | gemmL4x1x3 | L3-1 | below | 35.0 | +0.0804 |
| l03 | gemmL3x1x4 | L3-1 | below | 34.0 | -0.0228 |
| l04 | gemmL7x1x2 | L3-1 | above | 44.0 | +0.0299 |
| l05 | gemmL11x1x1 | L3-1 | above | 45.0 | +0.0562 |
| l06 | gemmL2x5x9 | L3-2 | below | 101.0 | +0.0092 |
| l07 | gemmL12x2x2 | L3-2 | below | 100.0 | -0.0304 |
| l08 | gemmL2x13x3 | L3-2 | above | 103.0 | -0.0176 |

The means by edge and side: L3-1 below +0.0288; L3-1 above +0.0636; L3-2 below -0.0106; L3-2 above -0.0176.

**Y2** (the equal-count layout effect). The words: "Y2: per pair the measured ln(wall a / wall b) against theta = 0.0077 in ln (E216's registered pair threshold): a pair REPEATS E216's effect when it exceeds theta with E216's sign (the first mask slower); the arm's reading REPEATS at 4 or more of its 5 pairs, DOES NOT REPEAT at 1 or fewer, MIXED otherwise".

| pair | shape | masks (first, second) | measured ln(wall first / wall second) | E216's measured (its source pair) | repeats |
|---|---|---|---|---|---|
| p01 | gemmL1x8x9 | 0x3, 0x10001 | +0.0547 | +0.0721 (y01) | yes |
| p02 | gemmL1x8x13 | 0x3, 0x10001 | +0.0529 | +0.0683 (y02) | yes |
| p03 | gemmL1x4x17 | 0x3, 0x10001 | -0.0095 | +0.0404 (y03) | no |
| p04 | gemmL1x4x25 | 0x101, 0x10001 | +0.0381 | +0.0360 (y07) | yes |
| p05 | gemmL1x8x25 | 0x101, 0x10001 | +0.0381 | +0.0420 (y08) | yes |

Reading: **REPEATS** (4 of 5 pairs repeat; theta 0.0077 in ln).

**G2** (the gemmLnc term at small excess). The words: "G2: per G2 point the measured W over idle less its twin's (each at its own measured seconds) against MM1-v3.2's F3 W: the term OVER-PREDICTS when the measured excess is under F3's at 5 or more of the 7 points (at least 70%), UNDER-PREDICTS when over it as often, MIXED otherwise".

| point | shape | twin | measured excess W over idle (point less twin) | F3's W | measured / F3 |
|---|---|---|---|---|---|
| n01 | gemmLnc1x6x48 | n01t | 6.602 | 3.373 | 1.96 |
| n02 | gemmLnc2x6x24 | n02t | 8.057 | 3.383 | 2.38 |
| n03 | gemmLnc2x6x28 | n03t | 8.490 | 3.382 | 2.51 |
| n04 | gemmLnc2x6x32 | n04t | 7.030 | 3.382 | 2.08 |
| n05 | gemmLnc1x6x40 | n05t | 6.855 | 3.382 | 2.03 |
| n06 | gemmLnc2x6x20 | n06t | 9.155 | 3.401 | 2.69 |
| n07 | gemmLnc4x6x16 | n07t | 8.575 | 3.478 | 2.47 |

Reading: **UNDER-PREDICTS** (F3 over-predicts at 0 of 7; the measured excess is 1.96-2.69 times F3's).

## 9. Q234's MM1-v3.3 candidates on arm A (REPORTED, never a registered rule; as verify-e220d scored them)

The three candidates were frozen for E220's points and posted before any E220 datum (05:47:36 PST for posimb and AF4, 06:05:46 PST for L3S; landed `badf08fa`, `911651ee`, `2a509f5a` at 07:49 PST), eight hours and more before arm A's first device access: BLIND. verify-e220d read each from its posted files after checking every file's sha256 against its post (this lane read the six forecast files' sha256 again at HEAD: each as posted), scored it with MM1-v3.2's bands, ties and sign test, and checked each candidate's own MM1-v3.2 column against the registered forecasts (posimb to 4.6e-12 relative over 612 values; AF4 to 4.6e-10 relative over 612 values; L3S to 4.6e-12 relative over 612 values). Its figures, quoted as it scored them:

- **'MM1-v3.2 + gemmLnc term AF4'** (posted 05:47:36 PST; 19 of this arm's points changed). Bands with it (REPORTED; MM1-v3.2's passes in brackets): T1 PASS 76/84 (MM1-v3.2 76); T2 FAIL 75/84 (MM1-v3.2 75); T3 PASS 78/84 (MM1-v3.2 78); E1 PASS 82/84 (MM1-v3.2 72); E2 PASS 84/84 (MM1-v3.2 74); E3 PASS 83/84 (MM1-v3.2 74); E4 PASS 78/84 (MM1-v3.2 74). Head to head against MM1-v3.2 (the same ties and sign test; candidate closer / MM1-v3.2 closer / ties): the wall cycles TOO FEW 0/0/84; the counter's mean TOO FEW 0/0/84; seconds TOO FEW 0/0/84; W over idle given t the candidate BETTER 16/2/66, p 0.00131; J over idle, t forecast the candidate BETTER 17/1/66, p 1.45e-4. rms of ln(measured / forecast), the candidate vs MM1-v3.2: wall (changed points) 12.51% vs 12.51% (n 19); Wg (changed points) 4.43% vs 18.72% (n 19); Jf (changed points) 4.67% vs 19.14% (n 19); wall (all) 7.55% vs 7.55% (n 84); Wg (all) 4.10% vs 10.80% (n 63). G2's measured excess in W against AF4's term and F3's: n01 6.60 / 8.27 / 3.37; n02 8.06 / 8.21 / 3.38; n03 8.49 / 8.22 / 3.38; n04 7.03 / 8.22 / 3.38; n05 6.86 / 8.22 / 3.38; n06 9.16 / 8.10 / 3.40; n07 8.57 / 7.64 / 3.48.
- **'MM1-v3.2 + posimb'** (posted 05:47:36 PST; 25 of this arm's points changed). Bands with it (REPORTED; MM1-v3.2's passes in brackets): T1 PASS 76/84 (MM1-v3.2 76); T2 FAIL 75/84 (MM1-v3.2 75); T3 PASS 78/84 (MM1-v3.2 78); E1 FAIL 72/84 (MM1-v3.2 72); E2 FAIL 73/84 (MM1-v3.2 74); E3 FAIL 74/84 (MM1-v3.2 74); E4 FAIL 74/84 (MM1-v3.2 74). Head to head against MM1-v3.2 (the same ties and sign test; candidate closer / MM1-v3.2 closer / ties): the wall cycles NOT DECIDED 12/4/68, p 0.0768; the counter's mean TOO FEW 5/4/75; seconds NOT DECIDED 12/4/68, p 0.0768; W over idle given t TOO FEW 0/0/84; J over idle, t forecast TOO FEW 1/0/83. rms of ln(measured / forecast), the candidate vs MM1-v3.2: wall (changed points) 4.41% vs 4.63% (n 25); Wg (changed points) 1.50% vs 1.50% (n 4); Jf (changed points) 0.78% vs 0.79% (n 4); wall (all) 7.51% vs 7.55% (n 84); Wg (all) 10.80% vs 10.80% (n 63). Its pairs (measured ln / its predicted ln): p01 +0.055 / +0.029; p02 +0.053 / +0.029; p03 -0.010 / +0.029; p04 +0.038 / +0.004; p05 +0.038 / +0.004; XY xy01 -0.088 / -0.035; xy02 +0.044 / +0.023; xy04 +0.044 / +0.023; xy05 +0.044 / +0.023; xy06 +0.044 / +0.023; xy07 -0.023 / +0.000; xy08 -0.027 / +0.000 (sign right at 9 of 10 pairs with a nonzero predicted difference).
- **'MM1-v3.2 + L3S'** (posted 06:05:46 PST; 44 of this arm's points changed). Bands with it (REPORTED; MM1-v3.2's passes in brackets): T1 FAIL 74/84 (MM1-v3.2 76); T2 FAIL 75/84 (MM1-v3.2 75); T3 FAIL 75/84 (MM1-v3.2 78); E1 FAIL 72/84 (MM1-v3.2 72); E2 FAIL 74/84 (MM1-v3.2 74); E3 FAIL 74/84 (MM1-v3.2 74); E4 FAIL 73/84 (MM1-v3.2 74). Head to head against MM1-v3.2 (the same ties and sign test; candidate closer / MM1-v3.2 closer / ties): the wall cycles NOT DECIDED 6/15/63, p 0.0784; the counter's mean NOT DECIDED 6/15/63, p 0.0784; seconds NOT DECIDED 6/14/64, p 0.115; W over idle given t TOO FEW 0/0/84; J over idle, t forecast TOO FEW 0/1/83. rms of ln(measured / forecast), the candidate vs MM1-v3.2: wall (changed points) 7.38% vs 7.29% (n 44); Wg (changed points) 9.04% vs 8.99% (n 44); Jf (changed points) 9.21% vs 9.14% (n 44); wall (all) 7.59% vs 7.55% (n 84); Wg (all) 10.82% vs 10.80% (n 63). L3's points, ln(measured / forecast) of the wall, the candidate / MM1-v3.2: l01 +0.042 / +0.105; l02 +0.032 / +0.080; l03 -0.052 / -0.023; l04 +0.011 / +0.030; l05 +0.043 / +0.056; l06 -0.016 / +0.009; l07 -0.030 / -0.030; l08 -0.018 / -0.018.

Pooled over both arms they are dated note 17's (arm B's directory).

## 10. verify-e220d's re-derivation, beside (its own code; verdict HOLDS)

- **The data.** Rebuilt from `proc-00.out`, `run.json` and `telemetry.jsonl.gz` with its own reader: 896/896 run fields bit-equal (t_gemm_s, cycles_per_op, cycles_gemm, p_work_w, p_rest_w, die_start_c, mhz_min, mhz_max); the scorer's measured table, 84 points x 11 means, 924/924 bit-equal. Its words: "59 points have 1 kept run and 25 have 2 (L3, Y2, G2), as planned"; the checks of C "109 approx, 5 exact, 0 wrong"; R0 and S6 0 failures, "kernel clock 598.4-599.8 MHz".
- **The scoring.** Its own code: verdicts 21/21 equal (counts, p 19/19), cells 588/588; the REPORTED family statistics and the L3, Y2 and G2 readings equal the scorer's (its 12 'differences' on this arm are only Y2's empty W given t group, written as an empty group by it and with n 0 by the scorer). The cross-card baseline re-made from E218's committed measurement and MM1-v3.2's frozen E218 forecasts: 94/94 wall errors and 72/72 energy errors, max difference 0.0.
- **The reproduction.** The frozen scorer on committed bytes: A alone and B alone are byte-equal to both lanes' RB_OUT json and txt.
- **The conduct**, as its result says: blindness, the seal registered before both bookings, the files, the scrub, the go lines, the order, the window, the rest, reads only, the clocks, nothing set, the card time, the stops, fwgate's one read EQUAL, the quiet-desk flag's times, no SIGKILL, the releases and LAB clean all hold.

## 11. Findings, answered as dated clauses (Fri 20 Nov 2026, after the data; post hoc; nothing re-scored)

1. **The one-arm file's pooled lines are arm A alone** (card-e220a's finding, info; verify-e220d's finding 8). The frozen scorer pools whatever arms it is given, so with arm A's data alone its `HP1`-`HP10`, `CXP-T` and `CXP-E` read arm A's own cases: HP1-HP5 MM1-v3.2 BETTER (49/22/13 ... 46/2/36), HP6 and HP8 NOT DECIDED, HP7, HP9 and HP10 MM1-v3.2 BETTER, CXP-T TOO FEW (0/4/48), CXP-E NOT DECIDED (21/12/8, p 0.163), each over arm A's 84 points. Step 13's header says these "read NO DATA in this file"; they do not, and the words were the kit's, not the scorer's (the scorer is as registered). **They are not the registered pooled reading.** That reading is the frozen scorer run on both committed arms at once, dated note 17 of arm B's directory: HP1-HP5 MM1-v3.2 BETTER, HP7, HP9 and HP10 MM1-v3.2 BETTER, HP6 and HP8 NOT DECIDED, CXP-T LARGER HERE (20/8/64, p 0.0357) and CXP-E LARGER HERE (42/16/12, p 8.62e-4). The arm A section of that two-arm run equals this file's arm A section exactly.
2. **T1 passes at zero slack** (verify-e220d's finding 3, info): xg02 at -11.99% against its 12% band is the 76th pass, and xg03 at -12.07% the closest miss. The verdict is exact as registered and stands.
3. **The card time, counted three ways** (verify-e220d's finding 5, info): 43.38 card-minutes from the runner's own config read (T0, 14:55:15 PST), 43.8 from step 7's config read (14:54:49, which the go lines name as the session's first card command) and 44.7 from step 4's firmware read (14:53:55, the first device access). Each is inside the 60-minute rule and the 70-minute cap, and every freeze line precedes all three. The data README reports both earlier reads apart.
4. **Two wordings of the day** (verify-e220d's finding 7, nit): the card lane recorded row 3 (the waived post, a record-only row) at 14:53:49 PST, before row 4 (14:53:55), while its go lines list 4 before 3; and its step-2 REPORTED line `sha256sum -c` of arm B's box sources list exits 1 from the lab's top because the list's paths are relative to arm B's own box folder, where verify-e220d read it 69 of 69 OK. Neither touches a datum or a verdict; for future kits, run such a list from its own folder.
5. **Both seal holds were released together** (card-e220a's finding, low): both card lanes booked at 14:50:53 PST, so the plan's 'aifoundry1 first' booking order was not used; THE ORDER held anyway (arm A's desk span 14:51:23-14:53:43 PST came first, and arm B raised THE QUIET DESK FLAG at 14:55:42, after arm A's launch marker at 14:55:20). No change.
6. **The card lane's REPORTED lead on card 1** (card-e220a's finding, info): F3 under-predicts the gemmLnc excess at all 7 G2 points here (section 8), where on aifoundry3 it had over-predicted; Q234's AF4 is the candidate that reads it (section 9). A lead for MM1-v3.3, never a verdict.

## 12. What this note does not do

It changes no committed file and re-scores nothing: every verdict is the frozen scorer's at step 13. It makes no pooled verdict (dated note 17 of arm B's directory does, by the same frozen scorer). It reads no box's disk and no model session's folder, opens none of the model session's sealed numbers, and adds no forecast. The candidates' figures are verify-e220d's, REPORTED; this lane re-checked their files' sha256 only. Not re-made here: the bootstrap and power simulations of the registration, the never-run scanner (step 6n's committed report is read as it stands), and dated note 1's simulation (its printer is re-run; its rates are the note's).

## 13. `SHA256SUMS-note1`

Five lines, in this order: `scores-e220-A.json`, `scores-e220-A.txt`, `README.md.dated-note-1.md`, `README.md`, `SHA256SUMS`, each with its sha256 as committed; `sha256sum -c SHA256SUMS-note1` from this directory reads 5 of 5 OK. With `SHA256SUMS` (612 lines), every file of this directory is in a list except `SHA256SUMS-note1` itself.

SPDX-License-Identifier: Apache-2.0
