# E220 arm B data, dated note 16: runbook step 13's outputs (E208's registered reduction, the frozen scorer's output and the readings beside it), committed beside the data byte for byte - R0 PASS; T1 67/72, T2 65/72, T3 67/72 PASS; E1 70/72, E2 67/72, E4 65/72 PASS, E3 FAIL 51/72; H4 MM1-v3 BETTER, H1-H3 and H5-H10 NOT DECIDED; CX-T and CX-E LARGER HERE; with verify-e220d's re-derivation beside each result

*Fri 20 Nov 2026 (week 47), PST; written from about 16:40 PST by Q233's lane `scores-e220` at the desk on aifoundry2, under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It comes after this directory's data commit `257496b7` (committed 15:44:26 PST; the card lane read it as the remote's main at 15:44:41 PST) and after the day's data verifier `verify-e220d` (HOLDS, 16:23 PST; no fix lane ran). It is numbered after this README's own dated notes 1-15. This note adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. The pooled rules over both arms (HP1-HP10, CXP-T, CXP-E) are this directory's dated note 17; arm A's own scores are dated note 1 of [`2026-11-20-e220-blind-matmul-aifoundry1-c1`](../2026-11-20-e220-blind-matmul-aifoundry1-c1/README.md.dated-note-1.md).* **Labels:** **BLIND** (every forecast E220 scores was frozen before either arm's first device access: MM1-v3.2's land `4e386f75`, committed 19:50:04 PST Thu 19 Nov 2026, and E220's registration `6901854c`, committed 12:31:40 PST and pushed 12:31:45 PST Fri 20 Nov 2026, with MM1-v3.1's, MM1-v3's and MM1-v2's E220 forecasts, the points, the bands, the rules and the scorer; the model session's sealed forecast was registered in `d5df9568`, committed 14:44:58 PST, before both bookings at 14:50:53 PST, and none of its numbers is read here; arm A's first device access was fwgate's read at 14:53:55 PST, arm B's at 14:57:42 PST), **measured** (the committed records), **registered** (E220.md, its dated note 1 and its kit), **REPORTED** (a reading, never a verdict), **post hoc** (anything read after the data), **desk** (a check of code at the desk).

## 1. The files this note adds

Ten new files beside the data commit's 353. The first eight are runbook step 13's outputs, copied byte for byte from the card lane's run folder (RB_OUT, its `score/` folder):

| file | what | bytes | sha256 | label |
|---|---|---|---|---|
| `data-e220b.json` | E208's registered reducer ([`reduce_mms.py`](../../../../tools/claims-v3/e208/proposal/src/reduce_mms.py) `b9e32618...`, with its `mms_common.py` `c3fc7883...`) on `session/`: every run's views, E220.md section 7's measured side for arm B | 1,097,924 | `c7a50cb1aeefcf1b...` | measured (reduced) |
| `reduce-e220b.txt` | the reducer's table of the runs | 9,721 | `c4b9e2e09ac50542...` | measured (reduced) |
| `reduce.out` | the reducer's printed lines (the same bytes as `reduce-e220b.txt`) | 9,721 | `c4b9e2e09ac50542...` | printed lines |
| `scores-e220.json` | the frozen scorer `score_e220.py` (`3c771990...`) on `data-e220b.json`: every verdict, every cell, every tally, the measured table it scored (route c) and route m's figures, and the REPORTED family table and readings | 100,435 | `d6f546288b395969...` | BLIND (its REPORTED parts never verdicts) |
| `scores-e220.txt` | the scorer's lines from its verdicts | 821 | `521e167c468bd9dc...` | BLIND |
| `score.out` | the scorer's printed lines (the same bytes as `scores-e220.txt`) | 821 | `521e167c468bd9dc...` | printed lines |
| `post-e220b.json` | `rb/post_e220b.py after`: the points with no route-c reading named, by family, and the session's stop | 335 | `e41c36ffa0e4f1a2...` | REPORTED |
| `post.out` | its printed line | 129 | `88eccb88cd413a6b...` | printed lines |
| `README.md.dated-note-16.md` | this note | - | - | dated note |
| `SHA256SUMS-note16` | the nine files above, then `README.md` and `SHA256SUMS` as the data commit holds them (11 lines) | - | - | - |

## 2. Where they come from: step 13 on the data commit (this lane's desk checks)

- **The step.** The card lane `card-e220b` ran the kit's step 13, [`tools/claims-v3/e220/rb/s24_score_e220b.sh`](../../../../tools/claims-v3/e220/rb/s24_score_e220b.sh) (in the kit's list), inside a CPU slot after the data commit (the round's slot log: one job, slot 2, 15:44:48-15:44:49 PST, rc 0; the runbook log: "s24_score_e220b start" at 15:44:48 and "exit 0" at 15:44:49, its one step-13 block). The step's one manifest read of the committed session (`collect_e220b.py --manifest-check`) read 342 of 342 lines OK, one by THE MASK (fwgate's record, line 34, as the kit registers); it printed "the data commit 257496b7a907 (2026-11-20 15:44:26 -0800); HEAD 257496b7a"; E208's reducer at its two pins ran rc 0; step 6n's labels read "LABELS-OK: 0 label(s) of arm B's registered points (none)", so the scorer ran without `--labels`, as the step does when the labels name no point; the scorer ran rc 0 and `rb/post_e220b.py after` rc 0.
- **The commit it read.** The lab clone's reflog holds HEAD at `257496b7` from 15:44:26 PST to its next move at 16:33:29 PST, so the whole step ran on it. This data directory (tree `a4b3464d`), the kit's folder and the notes folder are unchanged from `257496b7` to this note's parent.
- **The programs, at their pins** (at `257496b7` and at HEAD alike): the scorer `score_e220.py` `3c771990` with its three frozen inputs at the registration list's sha256; E208's `reduce_mms.py` `b9e32618` and `mms_common.py` `c3fc7883` (E220.md section 7, and the step's own check); `rb/s24_score_e220b.sh`, `rb/rb_e220b.sh`, `rb/post_e220b.py`, `collect_e220b.py` and `desk/neverrun_card_e220.py` at their kit-list sha256.
- **The labels.** The labels file the step read (RB_OUT's `ranbefore-e220b.json`) is byte for byte the committed `ranbefore-e220b.json`, and it names no point (`"ran_before_points": {"B": []}`).
- **The bytes and the times.** The eight files were written 15:44:49.24-15:44:49.37 PST inside the step, and they are RB_OUT's `score/` folder whole. `reduce.out` equals `reduce-e220b.txt` and `score.out` equals `scores-e220.txt` byte for byte (each tool prints what it writes). The card lane's capture of the step holds the scorer's printed lines and the readings' line byte for byte as `score.out` and `post.out`. The JSON files are in their writers' dump forms. The sha256 of `data-e220b.json`, `scores-e220.json` and `scores-e220.txt` are the ones card-e220b's and verify-e220d's results name.
- **Made again.** This lane ran step 13's three calls again, unchanged and in a CPU slot, on a tree exported from the lab clone's own objects at `257496b7`: all eight files came out byte for byte equal to RB_OUT's. The frozen scorer's own functions, called on the JSON's measured table, give every cell, verdict, tally, family figure and reading in it. verify-e220d re-made the reduction from the committed session and both scorer files from committed bytes on its own, byte for byte, and scored every rule with its own code (section 10).

**The scorer's printed lines** (`score.out`, all of it), then the readings' (`post.out`):

```
A:CX-E: NO DATA
A:CX-T: NO DATA
A:E1: NO DATA
A:E2: NO DATA
A:E3: NO DATA
A:E4: NO DATA
A:H1: NO DATA
A:H10: NO DATA
A:H2: NO DATA
A:H3: NO DATA
A:H4: NO DATA
A:H5: NO DATA
A:H6: NO DATA
A:H7: NO DATA
A:H8: NO DATA
A:H9: NO DATA
A:R0: NO DATA
A:S6: NO DATA
A:T1: NO DATA
A:T2: NO DATA
A:T3: NO DATA
B:CX-E: LARGER HERE
B:CX-T: LARGER HERE
B:E1: PASS
B:E2: PASS
B:E3: FAIL
B:E4: PASS
B:H1: NOT DECIDED
B:H10: NOT DECIDED
B:H2: NOT DECIDED
B:H3: NOT DECIDED
B:H4: MM1-v3 BETTER
B:H5: NOT DECIDED
B:H6: NOT DECIDED
B:H7: NOT DECIDED
B:H8: NOT DECIDED
B:H9: NOT DECIDED
B:R0: PASS
B:T1: PASS
B:T2: PASS
B:T3: PASS
CXP-E: LARGER HERE
CXP-T: LARGER HERE
HP1: NOT DECIDED
HP10: NOT DECIDED
HP2: NOT DECIDED
HP3: NOT DECIDED
HP4: MM1-v3 BETTER
HP5: NOT DECIDED
HP6: NOT DECIDED
HP7: NOT DECIDED
HP8: NOT DECIDED
HP9: NOT DECIDED
REPORTED: no run read 0, route m only 2, no energy 0, labelled []; by family {"X": {"route_m_only": 2}}; the session's stop None
```

The `A:` lines read NO DATA: this call had no arm A input. **The `HP1`-`HP10`, `CXP-T` and `CXP-E` lines are arm B alone, not the registered pooled reading** (clause 1 of section 11). The reducer's printed lines are `reduce.out`, a table of 80 lines, not repeated here.

## 3. The registered rules' words, and the verdicts (BLIND)

**The measured side on this card.** E220.md section 7: per run in its primary view, "route c (registered) when the view clock reads 790-810 MHz with no step and not NO STEP, scored against the 799.0 MHz column; route m (REPORTED) otherwise, against the column nearest its clock; a capped or thin run carries no energy; t_op the view's measured op time." By route c, 72 of the arm's 74 points read (the scorer's measured table). 5 runs read route m (REPORTED; the scorer's flags: xg10t run 11: ['STEP', 'CAPPED: no energy', 'ROUTE m at 799.0 MHz']; p04b run 33: ['STEP', 'CAPPED: no energy', 'ROUTE m at 799.0 MHz']; xg01t run 56: ['STEP', 'ROUTE m at 799.0 MHz']; n07 run 95: ['STEP', 'ROUTE m at 799.0 MHz']; n02 run 99: ['STEP', 'ROUTE m at 799.0 MHz']): xg01t and xg10t read route m only, so they leave every rule, while n02, n07, p04b keep their other, route-c runs (the route-m figures are in `scores-e220.json` > `arms` > `B` > `route_m_REPORTED`; `post.out` names the route-m-only points by family).

**R0.** The words: "R0 (every check of C exact or approx; the smoke good; the G block's smoke s03 failing while no gemmLnc point ran is flagged, not an R0 failure) and, arm A, S6 (every kept run's samples at 590-610 MHz): a FAIL labels every other verdict of its arm and of the pooled tests." Arm B: **R0 PASS** (no failure; the smoke good). No verdict carries a label. (The G block's smoke s03 is not among the runs this reader passes to R0: clause 2.)

**The per-case and per-point rules.** The words: "each passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its scored cases or points, FAIL otherwise, TOO FEW under 10, NO DATA with none". "The band is twice the larger of MM1-v3.2's two held-out rms errors without configuration twins". "Points under about 3 W over idle are scored in watts in E1 and E2" (arm B within 0.52 W); "E3 and E4 stay relative." The ties on arm B: cycles 0.005 in ln, seconds 0.005 in ln, joules 0.01 in ln, watts points 0.1 W (E216's on this card). With 72 points, 65 must pass.

| rule | what | band | passes / scored (needed) | verdict | the misses by family | the misses (measured / forecast - 1; a watts cell: measured - forecast, in W) |
|---|---|---|---|---|---|---|
| **T1** | cycles an op, the wall | 11% | 67 / 72 (65) | **PASS** | G2/G2-NB56 4, L3/L3-1 1 | l01 +11.39%, n01 +19.60%, n03 +15.59%, n04 +16.88%, n05 +20.35% |
| **T2** | cycles an op, the counter's mean | 14% | 65 / 72 (65) | **PASS** | G2/G2-NB56 4, X/XY 3 | n01 +20.00%, n03 +16.44%, n04 +17.76%, n05 +21.17%, xy04a +25.68%, xy05a +30.90%, xy06a +25.56% |
| **T3** | seconds a GEMM | 11% | 67 / 72 (65) | **PASS** | G2/G2-NB56 4, L3/L3-1 1 | l01 +11.37%, n01 +19.56%, n03 +15.55%, n04 +16.85%, n05 +20.30% |
| **E1** | J over idle given the measured op time and seconds | 10% | 70 / 72 (65) | **PASS** | G2/G2-NB56 1, X/XG 1 | n05 +10.64%, xg08 +11.02% |
| **E2** | J over idle with the seconds forecast | 12% | 67 / 72 (65) | **PASS** | G2/G2-NB56 3, X/XG 1, Y2/Y2-pair 1 | n01 +13.36%, n04 +13.88%, n05 +15.73%, p01a +16.09%, xg08 +13.29% |
| **E3** | J with the card at rest given t | 4% | 51 / 72 (65) | **FAIL** | X/XF 7, G2/G2-NB56 6, G2t/G2t-NB56 5, X/XGt 2, X/XG 1 | n01 +4.97%, n01t -4.61%, n02t -4.24%, n03 +4.64%, n03t -4.38%, n04 +5.67%, n05 +6.17%, n05t -4.49%, n06 +4.91%, n07 +5.71%, n07t -4.15%, xf01 -4.29%, xf02 -4.52%, xf05 -4.01%, xf06 -4.21%, xf07 -4.49%, xf08 -5.26%, xf09 -4.43%, xg02t -4.64%, xg08 +6.60%, xg11t -4.55% |
| **E4** | J with the card at rest with the seconds forecast | 10% | 65 / 72 (65) | **PASS** | G2/G2-NB56 4, X/XF 1, X/XG 1, Y2/Y2-pair 1 | n01 +15.75%, n03 +13.19%, n04 +15.03%, n05 +17.49%, p01a +12.11%, xf11 -10.08%, xg08 +11.63% |

E3 is the one rule to fail: 21 misses, 14 of them below the forecast (measured under MM1-v3.2's J at rest given t); its closest miss is xf05 at -4.007% against the 4% band.

## 4. The head-to-heads (BLIND)

The words: "per case d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - |W - first|, in W), decided when |d| exceeds the arm's tie; the exact two-sided sign test over the decided: 'MM1-v3.2 BETTER' or '<second> BETTER' at p < 0.05 with at least 10 decided, NOT DECIDED otherwise, TOO FEW under 10, NO DATA with none." "H1-H5 MM1-v3.2 vs MM1-v3: wall, the counter's mean, seconds (per case), W over idle given the measured op time (Wg; per point), J over idle with t forecast (Jf; per point), over every registered point of the arm; H6-H10 the same against MM1-v3.1; HP1-HP10 the same pooled over both arms' points, each case with its own arm's tie."

| rule | quantity | MM1-v3.2 against | over | MM1-v3.2 closer / the other closer / ties | p (exact, two-sided) | the scorer's verdict | verify-e220d (own code) |
|---|---|---|---|---|---|---|---|
| **H1** | the wall cycles | MM1-v3 | 72 | 25/18/29 | 0.36 | **NOT DECIDED** | the same counts, p and verdict |
| **H2** | the counter's mean | MM1-v3 | 72 | 26/18/28 | 0.291 | **NOT DECIDED** | the same counts, p and verdict |
| **H3** | seconds | MM1-v3 | 72 | 25/18/29 | 0.36 | **NOT DECIDED** | the same counts, p and verdict |
| **H4** | W over idle given t | MM1-v3 | 72 | 10/24/38 | 0.0243 | **MM1-v3 BETTER** | the same counts, p and verdict |
| **H5** | J over idle, t forecast | MM1-v3 | 72 | 23/12/37 | 0.0895 | **NOT DECIDED** | the same counts, p and verdict |
| **H6** | the wall cycles | MM1-v3.1 | 72 | 26/20/26 | 0.461 | **NOT DECIDED** | the same counts, p and verdict |
| **H7** | the counter's mean | MM1-v3.1 | 72 | 26/20/26 | 0.461 | **NOT DECIDED** | the same counts, p and verdict |
| **H8** | seconds | MM1-v3.1 | 72 | 26/20/26 | 0.461 | **NOT DECIDED** | the same counts, p and verdict |
| **H9** | W over idle given t | MM1-v3.1 | 72 | 10/17/45 | 0.248 | **NOT DECIDED** | the same counts, p and verdict |
| **H10** | J over idle, t forecast | MM1-v3.1 | 72 | 28/18/26 | 0.184 | **NOT DECIDED** | the same counts, p and verdict |

On arm B: MM1-v3.2 BETTER: none; NOT DECIDED: H1, H2, H3, H5, H6, H7, H8, H9, H10; H4 MM1-v3 BETTER (10/24/38, p 0.0243). E220.md section 8, stated before the data: "a NOT DECIDED says the models' time forecasts are close, not that they are equally good".

## 5. The cross-card rule (BLIND), with dated note 1's rates beside

The words: "per X twin with data on the arm and in E218 (aifoundry3 card 0), e_here = |ln(measured / MM1-v3.2's frozen forecast)| on this card at its registered clock and e_a3 = the same in E218"; "d = e_here - e_a3, decided when |d| exceeds the arm's tie; the exact two-sided sign test over the decided: 'LARGER HERE' (MM1-v3.2's error larger on this card) or 'SMALLER HERE' at p < 0.05 with at least 10 decided, NOT DECIDED otherwise, TOO FEW under 10, NO DATA with none." "CX-T the wall cycles an op; CX-E W over idle given the measured op time, at the twins measured at 3 W and above on both cards; per arm, and pooled (CXP-T, CXP-E)." "REPORTED beside: the per-twin ln(measured here / measured on aifoundry3) of the wall cycles (the card offset; MM1-v3.2's time has no per-card term)."

| rule | twins | larger here / larger on aifoundry3 / ties | p | the scorer's verdict | verify-e220d |
|---|---|---|---|---|---|
| **CX-T** (wall cycles) | 40 | 20/4/16 | 0.00154 | **LARGER HERE** | the same |
| **CX-E** (W over idle given t, 3 W and above on both cards) | 29 | 21/4/4 | 9.11e-4 | **LARGER HERE** | the same |

The card offset (REPORTED; "MM1-v3.2's time has no per-card term"): ln(measured wall here / measured wall on aifoundry3) over 40 twins, median +0.1989, mean +0.1992 (cycles an op on this card under its governor, scored at 799.0 MHz, against aifoundry3 card 0's at 600 MHz). E220.md section 8, stated before the data: "The cross-card energy test reads LARGER HERE at equal error with a simulated rate of 0.095 on arm A and 0.331 on arm B". Dated note 1's printer, run by the card lane at step 13 on `scores-e220.json`, printed (made again here byte for byte):

```
A:CX-E: NO DATA (0 twins, 0 larger here, 0 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0032 (resampled aifoundry3 errors), at equal rms with normal errors 0.1084 (registered 0.095)
B:CX-E: LARGER HERE (29 twins, 21 larger here, 4 larger on aifoundry3, p 0.0009105205535888672) | dated note 1: false LARGER HERE at equal distribution 0.0019 (resampled aifoundry3 errors), at equal rms with normal errors 0.3379 (registered 0.331)
CXP-E: LARGER HERE (29 twins, 21 larger here, 4 larger on aifoundry3, p 0.0009105205535888672) | dated note 1: false LARGER HERE at equal distribution 0.0033 (resampled aifoundry3 errors), at equal rms with normal errors 0.4986
A:CX-T: NO DATA (0 twins, 0 larger here, 0 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0039 (resampled aifoundry3 errors), at equal rms with normal errors 0.0088 (registered 0.009)
B:CX-T: LARGER HERE (40 twins, 20 larger here, 4 larger on aifoundry3, p 0.001543879508972168) | dated note 1: false LARGER HERE at equal distribution 0.0039 (resampled aifoundry3 errors), at equal rms with normal errors 0.0021 (registered 0.004)
CXP-T: LARGER HERE (40 twins, 20 larger here, 4 larger on aifoundry3, p 0.001543879508972168) | dated note 1: false LARGER HERE at equal distribution 0.0052 (resampled aifoundry3 errors), at equal rms with normal errors 0.0089
CX-BESIDE-E220-NOTE1: 6 cross-card verdict(s) printed with the null rates beside
```

Its `A:` lines read NO DATA and its `CXP-` lines are arm B alone (clause 1). Dated note 1's reading: "A LARGER HERE there is read as "this card's errors are not distributed like aifoundry3's: larger, or less heavy-tailed". It is not read as "larger at an equal shape"."

## 6. MM1-v3.2 point by point, at the zero-slack verdicts (BLIND)

T2 and E4 pass with no slack: 65 of 72 each, 65 needed. T2's closest pass is xy08b at +11.949% against the 14% band and its closest miss n03 at +16.435%; E4's closest pass is xf10 at -9.762% against the 10% band and its closest miss xf11 at -10.084%. E3's closest miss is xf05 at -4.007% against 4%. Each is exact as registered and stands (clause 4).

## 7. Each model's error by family and subfamily (REPORTED; the scorer's table, `family_stats_REPORTED`, route c)

The words: "every family and subfamily: each model's rms and bias of ln(measured / forecast), wall cycles and W given t; route m on arm B; the twins' card offset." Each cell is rms (bias) of ln(measured / forecast) in %, over the points with data; W over idle given t counts only points at 3 W and above on both sides. verify-e220d's own code gives every figure.

The wall cycles:

| family / subfamily | n | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| X | 40 | 6.06 (-1.36) | 10.09 (-3.81) | 9.47 (-3.48) | 13.01 (+3.04) |
| X/XF | 14 | 8.01 (-6.93) | 15.27 (-13.17) | 14.32 (-12.32) | 12.66 (-9.99) |
| X/XG | 2 | 6.15 (+4.87) | 6.26 (+4.94) | 6.03 (+4.68) | 7.51 (+6.75) |
| X/XGt | 9 | 3.26 (+0.82) | 5.95 (-1.72) | 5.07 (-1.30) | 6.72 (+2.11) |
| X/XY | 15 | 5.15 (+1.71) | 5.23 (+2.49) | 5.25 (+2.39) | 16.35 (+15.26) |
| L3 | 8 | 5.54 (+2.07) | 6.11 (+0.54) | 5.88 (+1.00) | 9.20 (+3.22) |
| L3/L3-1 | 5 | 6.68 (+4.55) | 6.04 (+4.45) | 6.30 (+4.59) | 11.08 (+7.37) |
| L3/L3-2 | 3 | 2.71 (-2.07) | 6.23 (-5.97) | 5.10 (-4.98) | 4.58 (-3.69) |
| Y2 | 10 | 4.70 (+0.35) | 4.53 (+0.87) | 4.66 (+0.89) | 16.25 (+15.71) |
| Y2/Y2-pair | 6 | 5.75 (-0.53) | 5.29 (-0.25) | 5.49 (-0.16) | 14.29 (+13.70) |
| Y2/Y2-control | 4 | 2.38 (+1.67) | 3.06 (+2.55) | 3.00 (+2.47) | 18.81 (+18.73) |
| G2 | 7 | 13.38 (+12.38) | 12.77 (+11.97) | 12.82 (+11.95) | 16.65 (+15.66) |
| G2/G2-NB56 | 7 | 13.38 (+12.38) | 12.77 (+11.97) | 12.82 (+11.95) | 16.65 (+15.66) |
| G2t | 7 | 5.66 (+5.61) | 5.31 (+5.19) | 5.27 (+5.17) | 10.04 (+9.94) |
| G2t/G2t-NB56 | 7 | 5.66 (+5.61) | 5.31 (+5.19) | 5.27 (+5.17) | 10.04 (+9.94) |
| **all** | 72 | 6.88 (+1.27) | 9.06 (-0.27) | 8.68 (-0.03) | 13.30 (+6.72) |

W over idle given t:

| family / subfamily | n | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| X | 40 | 5.83 (-2.44) | 7.03 (-2.54) | 6.98 (-1.98) | 7.63 (-4.24) |
| X/XF | 14 | 6.56 (-6.46) | 6.94 (-6.80) | 6.66 (-6.56) | 8.25 (-8.19) |
| X/XG | 2 | 7.84 (+7.08) | 19.81 (+19.68) | 20.39 (+20.27) | 17.05 (+16.94) |
| X/XGt | 9 | 5.93 (-5.72) | 6.05 (-5.84) | 5.51 (-5.30) | 7.72 (-7.42) |
| X/XY | 15 | 4.58 (+2.01) | 3.58 (+0.46) | 3.86 (+1.33) | 4.17 (-1.46) |
| L3 | 8 | 5.48 (-4.89) | 5.73 (-5.10) | 5.52 (-4.84) | 4.83 (-3.68) |
| L3/L3-1 | 5 | 5.23 (-4.31) | 5.37 (-4.42) | 5.38 (-4.30) | 2.99 (-1.96) |
| L3/L3-2 | 3 | 5.88 (-5.86) | 6.27 (-6.23) | 5.76 (-5.73) | 6.87 (-6.55) |
| Y2 | 10 | 4.38 (+4.04) | 2.09 (+1.26) | 2.79 (+2.23) | 1.70 (+0.32) |
| Y2/Y2-pair | 6 | 4.50 (+3.95) | 2.42 (+1.16) | 3.00 (+2.12) | 2.15 (+0.34) |
| Y2/Y2-control | 4 | 4.19 (+4.16) | 1.48 (+1.40) | 2.44 (+2.39) | 0.55 (+0.29) |
| G2 | 7 | 8.37 (+8.26) | 20.88 (+20.84) | 21.58 (+21.55) | 17.24 (+17.19) |
| G2/G2-NB56 | 7 | 8.37 (+8.26) | 20.88 (+20.84) | 21.58 (+21.55) | 17.24 (+17.19) |
| G2t | 7 | 7.66 (-7.65) | 7.39 (-7.36) | 6.64 (-6.62) | 10.85 (-10.82) |
| G2t/G2t-NB56 | 7 | 7.66 (-7.65) | 7.39 (-7.36) | 6.64 (-6.62) | 10.85 (-10.82) |
| **all** | 72 | 6.11 (-1.28) | 8.91 (-0.49) | 9.01 (+0.13) | 8.70 (-2.10) |

Every point, each model's rms (bias), desk arithmetic in verify-e220d's definitions (equal to its figures):

| quantity | scope (n) | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| wall cycles | arm B (72) | 6.88 (+1.27) | 9.06 (-0.27) | 8.68 (-0.03) | 13.30 (+6.72) |
| the counter's mean | arm B (72) | 8.48 (+2.88) | 10.26 (+1.34) | 9.93 (+1.58) | 15.48 (+8.33) |
| seconds | arm B (72) | 6.88 (+1.26) | 9.06 (-0.28) | 8.68 (-0.05) | 13.29 (+6.70) |
| W over idle given t (3 W and above) | arm B (72) | 6.11 (-1.28) | 8.91 (-0.49) | 9.01 (+0.13) | 8.70 (-2.10) |
| J over idle, t forecast (3 W and above) | arm B (72) | 7.27 (-0.95) | 10.69 (-0.42) | 10.79 (+0.25) | 12.17 (+1.87) |
| J at rest given t (every point) | arm B (72) | 3.36 (-1.04) | 5.17 (-0.39) | 5.19 (-0.11) | 5.03 (-1.18) |

## 8. The leads, reported per family (REPORTED readings, never verdicts)

**L3** (the L3 edges). The words: "L3: MM1-v3.2's ln(measured / forecast) of the wall cycles per point by edge and side (does the miss above x1 repeat: the L3-1 points above x1 slower than forecast, those below not)".

| point | shape | edge | side | footprint (MB) | MM1-v3.2 ln(measured / forecast), wall |
|---|---|---|---|---|---|
| l01 | gemmL10x1x1 | L3-1 | above | 41.0 | +0.1078 |
| l02 | gemmL4x1x3 | L3-1 | below | 35.0 | +0.0772 |
| l03 | gemmL3x1x4 | L3-1 | below | 34.0 | -0.0364 |
| l04 | gemmL7x1x2 | L3-1 | above | 44.0 | +0.0268 |
| l05 | gemmL11x1x1 | L3-1 | above | 45.0 | +0.0520 |
| l06 | gemmL2x5x9 | L3-2 | below | 101.0 | +0.0004 |
| l07 | gemmL12x2x2 | L3-2 | below | 100.0 | -0.0425 |
| l08 | gemmL2x13x3 | L3-2 | above | 103.0 | -0.0200 |

The means by edge and side: L3-1 below +0.0204; L3-1 above +0.0622; L3-2 below -0.0210; L3-2 above -0.0200.

**Y2** (the equal-count layout effect). The words: "Y2: per pair the measured ln(wall a / wall b) against theta = 0.0077 in ln (E216's registered pair threshold): a pair REPEATS E216's effect when it exceeds theta with E216's sign (the first mask slower); the arm's reading REPEATS at 4 or more of its 5 pairs, DOES NOT REPEAT at 1 or fewer, MIXED otherwise".

| pair | shape | masks (first, second) | measured ln(wall first / wall second) | E216's measured (its source pair) | repeats |
|---|---|---|---|---|---|
| p01 | gemmL1x8x9 | 0x3, 0x10001 | +0.0734 | +0.0721 (y01) | yes |
| p02 | gemmL1x8x13 | 0x3, 0x10001 | +0.0676 | +0.0683 (y02) | yes |
| p03 | gemmL1x4x17 | 0x3, 0x10001 | -0.0019 | +0.0404 (y03) | no |
| p04 | gemmL1x4x25 | 0x101, 0x10001 | +0.0350 | +0.0360 (y07) | yes |
| p05 | gemmL1x8x25 | 0x101, 0x10001 | +0.0329 | +0.0420 (y08) | yes |

Reading: **REPEATS** (4 of 5 pairs repeat; theta 0.0077 in ln).

**G2** (the gemmLnc term at small excess). The words: "G2: per G2 point the measured W over idle less its twin's (each at its own measured seconds) against MM1-v3.2's F3 W: the term OVER-PREDICTS when the measured excess is under F3's at 5 or more of the 7 points (at least 70%), UNDER-PREDICTS when over it as often, MIXED otherwise".

| point | shape | twin | measured excess W over idle (point less twin) | F3's W | measured / F3 |
|---|---|---|---|---|---|
| n01 | gemmLnc1x6x48 | n01t | 5.960 | 4.048 | 1.47 |
| n02 | gemmLnc2x6x24 | n02t | 7.698 | 4.060 | 1.90 |
| n03 | gemmLnc2x6x28 | n03t | 6.759 | 4.059 | 1.67 |
| n04 | gemmLnc2x6x32 | n04t | 6.597 | 4.059 | 1.63 |
| n05 | gemmLnc1x6x40 | n05t | 6.325 | 4.059 | 1.56 |
| n06 | gemmLnc2x6x20 | n06t | 8.421 | 4.082 | 2.06 |
| n07 | gemmLnc4x6x16 | n07t | 8.992 | 4.175 | 2.15 |

Reading: **UNDER-PREDICTS** (F3 over-predicts at 0 of 7; the measured excess is 1.47-2.15 times F3's).

## 9. Q234's MM1-v3.3 candidates on arm B (REPORTED, never a registered rule; as verify-e220d scored them)

Frozen and posted before any E220 datum (05:47:36 and 06:05:46 PST), more than eight hours before arm B's first device access (14:57:42 PST): BLIND. verify-e220d's figures, quoted as it scored them (each file's sha256 checked against its post first; this lane read the six forecast files' sha256 again at HEAD):

- **'MM1-v3.2 + gemmLnc term AF4'** (posted 05:47:36 PST; 9 of this arm's points changed). Bands with it (REPORTED; MM1-v3.2's passes in brackets): T1 PASS 67/72 (MM1-v3.2 67); T2 PASS 65/72 (MM1-v3.2 65); T3 PASS 67/72 (MM1-v3.2 67); E1 PASS 72/72 (MM1-v3.2 70); E2 PASS 71/72 (MM1-v3.2 67); E3 FAIL 53/72 (MM1-v3.2 51); E4 PASS 70/72 (MM1-v3.2 65). Head to head against MM1-v3.2 (the same ties and sign test; candidate closer / MM1-v3.2 closer / ties): the wall cycles TOO FEW 0/0/72; the counter's mean TOO FEW 0/0/72; seconds TOO FEW 0/0/72; W over idle given t TOO FEW 5/2/65; J over idle, t forecast TOO FEW 7/2/63. rms of ln(measured / forecast), the candidate vs MM1-v3.2: wall (changed points) 12.15% vs 12.15% (n 9); Wg (changed points) 6.89% vs 8.26% (n 9); Jf (changed points) 5.11% vs 10.98% (n 9); wall (all) 6.88% vs 6.88% (n 72); Wg (all) 5.90% vs 6.11% (n 72). G2's measured excess in W against AF4's term and F3's: n01 5.96 / 9.93 / 4.05; n02 7.70 / 9.86 / 4.06; n03 6.76 / 9.86 / 4.06; n04 6.60 / 9.86 / 4.06; n05 6.32 / 9.86 / 4.06; n06 8.42 / 9.72 / 4.08; n07 8.99 / 9.17 / 4.17.
- **'MM1-v3.2 + posimb'** (posted 05:47:36 PST; 25 of this arm's points changed). Bands with it (REPORTED; MM1-v3.2's passes in brackets): T1 PASS 67/72 (MM1-v3.2 67); T2 PASS 65/72 (MM1-v3.2 65); T3 PASS 67/72 (MM1-v3.2 67); E1 PASS 70/72 (MM1-v3.2 70); E2 PASS 67/72 (MM1-v3.2 67); E3 FAIL 51/72 (MM1-v3.2 51); E4 PASS 66/72 (MM1-v3.2 65). Head to head against MM1-v3.2 (the same ties and sign test; candidate closer / MM1-v3.2 closer / ties): the wall cycles NOT DECIDED 9/5/58, p 0.424; the counter's mean TOO FEW 5/4/63; seconds NOT DECIDED 9/5/58, p 0.424; W over idle given t TOO FEW 0/0/72; J over idle, t forecast TOO FEW 7/0/65. rms of ln(measured / forecast), the candidate vs MM1-v3.2: wall (changed points) 4.76% vs 4.98% (n 25); Wg (changed points) 4.50% vs 4.50% (n 25); Jf (changed points) 5.26% vs 6.03% (n 25); wall (all) 6.83% vs 6.88% (n 72); Wg (all) 6.11% vs 6.11% (n 72). Its pairs (measured ln / its predicted ln): p01 +0.073 / +0.029; p02 +0.068 / +0.029; p03 -0.002 / +0.029; p04 +0.035 / +0.004; p05 +0.033 / +0.004; XY xy01 -0.109 / -0.035; xy02 +0.054 / +0.023; xy04 +0.047 / +0.023; xy05 +0.051 / +0.023; xy06 +0.050 / +0.023; xy07 -0.019 / +0.000; xy08 -0.023 / +0.000 (sign right at 9 of 10 pairs with a nonzero predicted difference).
- **'MM1-v3.2 + L3S'** (posted 06:05:46 PST; 34 of this arm's points changed). Bands with it (REPORTED; MM1-v3.2's passes in brackets): T1 PASS 66/72 (MM1-v3.2 67); T2 PASS 65/72 (MM1-v3.2 65); T3 PASS 66/72 (MM1-v3.2 67); E1 PASS 70/72 (MM1-v3.2 70); E2 PASS 67/72 (MM1-v3.2 67); E3 FAIL 50/72 (MM1-v3.2 51); E4 FAIL 63/72 (MM1-v3.2 65). Head to head against MM1-v3.2 (the same ties and sign test; candidate closer / MM1-v3.2 closer / ties): the wall cycles NOT DECIDED 5/12/55, p 0.143; the counter's mean MM1-v3.2 BETTER 4/13/55, p 0.049; seconds NOT DECIDED 5/12/55, p 0.143; W over idle given t TOO FEW 0/0/72; J over idle, t forecast TOO FEW 1/1/70. rms of ln(measured / forecast), the candidate vs MM1-v3.2: wall (changed points) 6.45% vs 6.49% (n 34); Wg (changed points) 6.45% vs 6.38% (n 34); Jf (changed points) 7.61% vs 7.40% (n 34); wall (all) 6.87% vs 6.88% (n 72); Wg (all) 6.14% vs 6.11% (n 72). L3's points, ln(measured / forecast) of the wall, the candidate / MM1-v3.2: l01 +0.040 / +0.108; l02 +0.023 / +0.077; l03 -0.070 / -0.036; l04 +0.007 / +0.027; l05 +0.037 / +0.052; l06 -0.028 / +0.000; l07 -0.042 / -0.042; l08 -0.020 / -0.020.

Pooled over both arms they are dated note 17.

## 10. verify-e220d's re-derivation, beside (its own code; verdict HOLDS)

- **The data.** E208's registered reducer's rules written in its own code: 103 runs × 18 fields = 1,854/1,854 against the registered reducer's output, and that output itself re-made byte for byte from the committed session; the scorer's measured tables 966/966 cells. Its words: "94 runs route c and 5 route m (xg10t and p04b CAPPED; xg01t, n07 and n02 a step)"; "72 points by route c; xg01t and xg10t are route m only (REPORTED)"; the checks of C "98 approx and 5 exact; the smoke (3 arms) exact, good, rc 0".
- **The scoring.** Its own code: verdicts 20/20 (19/19), cells 504/504; the REPORTED family statistics and the L3, Y2 and G2 readings equal the scorer's.
- **The reproduction.** The registered reducer on the committed session is byte-equal to RB_OUT's reduction, and the frozen scorer on committed bytes byte-equal to both arms' RB_OUT files.
- **The conduct**, as its result says, holds throughout (blindness, the seal, the files, THE MASK, the go lines, the order, the window, the rest from 12:20:40 PST, reads only, the governed clocks read and never set, nothing set, the card time 39.36 card-minutes, no stop, fwgate's one read EQUAL, THE QUIET DESK FLAG 14:55:42-15:37:34 PST, no SIGKILL, the releases, LAB clean).

## 11. Findings, answered as dated clauses (Fri 20 Nov 2026, after the data; post hoc; nothing re-scored)

1. **The one-arm file's pooled lines are arm B alone** (card-e220b's finding, info; verify-e220d's finding 8). With arm B's data alone the frozen scorer's `HP1`-`HP10`, `CXP-T` and `CXP-E` read arm B's own cases: HP4 MM1-v3 BETTER (10/24/38), the other HP NOT DECIDED, CXP-T LARGER HERE (20/4/16) and CXP-E LARGER HERE (21/4/4), each over arm B's 72 points. Step 13's header says the pooled rules "read NO DATA in this file"; they do not (the kit's words, not the scorer's). **They are not the registered pooled reading**, which is this directory's dated note 17 (the frozen scorer on both committed arms at once): HP1-HP5 MM1-v3.2 BETTER (HP4 68/26/62, p 1.73e-5), HP7, HP9 and HP10 MM1-v3.2 BETTER, HP6 and HP8 NOT DECIDED, CXP-T and CXP-E LARGER HERE. Its arm B section equals this file's arm B section exactly.
2. **R0 never reads the G block's smoke s03 on this arm** (verify-e220d's finding 1, low). The registered reader `read_b` drops every run of role 'arm' whose id is not a registered point before R0's loop, and s03 (run `087-s03`, gemmLnc6x5x10) is such a run, so E220.md 7's rule for s03 never reaches it here (arm A reads s03 through its smoke runs). verify-e220d read it: "s03 read approx, rc 0, GATE OK (cycles an op 1,452.9 in the view)". So R0 PASS stands as printed. For future kits: the arm-B reader takes s03 by its id.
3. **The README's never-run row reads NOT RUN, and `neverrun-e220b-card.txt` is not in this directory** (card-e220b's kit finding, confirmed by verify-e220d's finding 2, low). Step 6n did run (14:57:23-14:57:36 PST): 74 of 74 registered points never ran on aifoundry2 card 0 by dated note 1's reading, none labelled; README note 8 quotes its line, and the committed `ranbefore-e220b.json` (no point) is what step 13 read. The collection copies that report under a name step 6n does not write. Nothing changes; for the kit: copy step 6n's report under the name the Files table uses.
4. **Three verdicts sit at zero slack** (verify-e220d's finding 3, info): T2 PASS 65/72 and E4 PASS 65/72 with 65 needed, and E3 FAIL with its closest miss xf05 at -4.007% (section 6). Each is exact as registered and stands.
5. **E208's checker reads C0 FAIL and C2 FAIL; neither is a fault** (card-e220b's finding, info; verify-e220d's finding 6). C2: xf04's host printed "stopping: device-time budget of 7.5 s used", which E208's runner records as stopped by a file; no STOP file was written, and the run had 6 launches ok, its check of C approx, rc 0. C0 is E216's log-first-line reading. README note 13 records both.
6. **Arm B's H4 and the pooled HP4 point opposite ways** (verify-e220d's finding 4, info): here MM1-v3 is closer in W over idle given t (10/24/38, p 0.0243); pooled, arm A's lead (58/2/24) outweighs it and HP4 reads MM1-v3.2 BETTER (68/26/62). Both are as registered.

## 12. What this note does not do

It changes no committed file and re-scores nothing: every verdict is the frozen scorer's at step 13 on this card's reduction. It makes no pooled verdict (dated note 17 does). It reads no box's disk and no model session's folder, opens none of the model session's sealed numbers, and adds no forecast. The candidates' figures are verify-e220d's, REPORTED. Not re-made here: the registration's simulations and the never-run scanner; dated note 1's rates are the note's (its printer is re-run).

## 13. `SHA256SUMS-note16`

Eleven lines, in this order: the eight step-13 files of section 1 (`data-e220b.json`, `reduce-e220b.txt`, `reduce.out`, `scores-e220.json`, `scores-e220.txt`, `score.out`, `post-e220b.json`, `post.out`), `README.md.dated-note-16.md`, then `README.md` and `SHA256SUMS` as the data commit holds them, each with its sha256; `sha256sum -c SHA256SUMS-note16` from this directory reads 11 of 11 OK. With `SHA256SUMS` (352 lines), every file of this directory is in a list except `SHA256SUMS-note16` itself (until note 17 lists it).

SPDX-License-Identifier: Apache-2.0
