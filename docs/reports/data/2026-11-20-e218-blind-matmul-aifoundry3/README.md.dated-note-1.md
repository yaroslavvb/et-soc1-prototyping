# E218 data, dated note 1: the frozen scorer's output, committed beside the data byte for byte - R0 FAIL (one run printed no check of C), which labels every other verdict; S6 PASS; T1 FAIL 45/52, T2 PASS 47/52, T3 FAIL 45/52, E1 PASS 48/52, E2 PASS 49/52, E3 FAIL 46/52, E4 PASS 47/52; H1-H10, HG1 and HG2 MM1-v3.2 BETTER; HG3, HG4 and HY2 NOT DECIDED; HY1 TOO FEW; P1 FAIL (7 of 7 pairs separated); with verify-e218d's re-derivation beside each result

*Fri 20 Nov 2026 (week 47), PST; written at about 04:55 PST by Q230's lane `scores-e218` at the desk on aifoundry2, under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It comes after this directory's data commit `b445b0f5` (committed 04:00:11 PST, pushed by 04:00:14) and after the day's data verifier `verify-e218d` (HOLDS: the data re-derive exactly from the raw records, its own scoring equals the frozen scorer's in every verdict, cell, case and tally, and it asks for no change to the record; no fix lane ran, since it held). This note adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. **Labels:** **BLIND** (every forecast E218 scores was frozen before its first card command at 03:11:24 PST: every declared model's by MM1-v3.2's land `4e386f75`, committed 19:50:04 PST Thu 19 Nov 2026, and 'MM1-v3.2 without its gemmLnc term' by the registration `1b853bac`, committed 01:23:43 PST Fri 20 Nov), **measured** (this directory's committed records), **registered** (E218.md and its kit), **REPORTED** (a reading, never a verdict), **post hoc** (anything read after the data), **desk** (a check of code at the desk).*

## 1. The files this note adds

Four new files beside the data commit's 584. The first two are runbook step 13's outputs, copied byte for byte from the card lane's run folder:

| file | what | sha256 | label |
|---|---|---|---|
| `scores-e218-A.json` | the frozen scorer `tools/claims-v3/e218/score_e218.py` (`1434e7e6...`) on `data-e218.json` with step 6n's `labels-e218.json`: every verdict, every cell of T1-T3 and E1-E4, every head-to-head with its cases and bootstrap, the pair rule and its candidates, and the REPORTED readings (204,841 bytes) | `b386d14a4a0e5094...` | BLIND (its REPORTED parts never verdicts) |
| `scores-e218-A.txt` | the scorer's printed lines: the step's capture of the scorer's call, which the step copies (877 bytes, 26 lines) | `f6998dff5f2a8e50...` | printed lines |
| `README.md.dated-note-1.md` | this note | - | dated note |
| `SHA256SUMS-note1` | the three files above, then `README.md` and `SHA256SUMS` as the data commit holds them (5 lines) | - | - |

## 2. Where they come from: step 13 on the data commit (this lane's desk checks)

- **The step.** The card lane `card-e218` ran the kit's step 13, `tools/claims-v3/e218/rb/s24_score_e218.sh A` (in the kit's list `SHA256SUMS-e218-kit`), inside a CPU slot after the data commit, as the card-lane brief's row 13 says (the round's slot log: one job, 04:00:28-04:00:30 PST, rc 0). The runbook log's last six lines are the step's six calls, each rc 0 and all from one process: (1) the data directory committed (a commit names it): `b445b0f5c E218 data: ...`, the data commit; (2) the directory clean: nothing printed; (3) the data's `SHA256SUMS`: 582 of 582 entries OK, in the list's order; (4) the history check: "HISTORY OK: HEAD descends from the registration 1b853bac2fd5 (subtree deb6726f); ..."; (5) step 6n's labels: `LABELS-OK`; (6) the frozen scorer on the committed `data-e218.json` with `--labels labels-e218.json`, whose printed lines (below) are `scores-e218-A.txt` and whose JSON is `scores-e218-A.json`.
- **The commit it read.** `b445b0f5` was committed at 04:00:11 PST and pushed by 04:00:14 (the lab clone's push record). The lab clone's HEAD has been `b445b0f5` from 04:00:11 to this note's parent, so the step ran on it. The data directory, its 582-line `SHA256SUMS` and the kit's folder are unchanged from `b445b0f5` to this note's parent.
- **The scorer and its inputs, at their pins.** `score_e218.py` is `1434e7e6...`, as E218.md section 0 and the registration's list name it. Its six pins read their sha256 at the data commit: MM1-v3.2's land files `forecasts-e218.json` `1236dd99`, `forecasts-e218.csv` `52e78762` and `points-e218.csv` `1771826e`, and this folder's `forecast-e218-reg.json` `0a8a7d57`, `rules-e218.json` `b8037cd6` and `points-e218.json` `9a5f252f`. Every file of E218.md section 0's two tables (22 and 14 files), of the registration's list (24 files) and of the kit's list (48 files) has one blob from its freeze commit through the registration `1b853bac`, the kit `5582edfc`, the seal's note `6dc30e04` and the data commit to this note's parent. Each model's and term's file read in place is its blob as landed (MM1-v3.1 `2c971828`, MM1-v3 `b1493082`, MM1-v2 `3ca4b717`, the gemmLnc term `aaeaa495`, the layout term `595fcb59`).
- **The labels.** Step 6n's committed `labels-e218.json` names no point (`"ran_before_points": []`). The scorer read it with `--labels`, and the JSON's `labels_applied` repeats it.
- **The bytes and the times.** The two files' sha256 are the ones card-e218's and verify-e218d's results name. The JSON was written inside the scorer's call (04:00:30.17 PST), in `main()`'s dump form, and the text is the step's copy of that call's capture, made 9 ms later.
- **Made again.** This lane ran calls 5 and 6 again, unchanged and in a CPU slot, on a tree exported from the lab clone's own objects at `b445b0f5`. That commit was also HEAD and the remote's main (read by `git ls-remote` at 04:36 PST). The JSON and the printed lines came out byte for byte equal. Calls 1-4, made again in the lab clone as reads, equal the step's captures. The frozen scorer's `score()`, called in process on the committed data and labels and dumped as its `main()` dumps it, gives `scores-e218-A.json` byte for byte. verify-e218d scored every rule with its own code and equals the scorer throughout (section 10).

**The scorer's printed lines** (`scores-e218-A.txt`, all of it):

```
R0: FAIL
S6: PASS
T1: FAIL (labelled: R0 FAIL)
T2: PASS (labelled: R0 FAIL)
T3: FAIL (labelled: R0 FAIL)
E1: PASS (labelled: R0 FAIL)
E2: PASS (labelled: R0 FAIL)
E3: FAIL (labelled: R0 FAIL)
E4: PASS (labelled: R0 FAIL)
H1: MM1-v3.2 BETTER (labelled: R0 FAIL)
H10: MM1-v3.2 BETTER (labelled: R0 FAIL)
H2: MM1-v3.2 BETTER (labelled: R0 FAIL)
H3: MM1-v3.2 BETTER (labelled: R0 FAIL)
H4: MM1-v3.2 BETTER (labelled: R0 FAIL)
H5: MM1-v3.2 BETTER (labelled: R0 FAIL)
H6: MM1-v3.2 BETTER (labelled: R0 FAIL)
H7: MM1-v3.2 BETTER (labelled: R0 FAIL)
H8: MM1-v3.2 BETTER (labelled: R0 FAIL)
H9: MM1-v3.2 BETTER (labelled: R0 FAIL)
HG1: MM1-v3.2 BETTER (labelled: R0 FAIL)
HG2: MM1-v3.2 BETTER (labelled: R0 FAIL)
HG3: NOT DECIDED (labelled: R0 FAIL)
HG4: NOT DECIDED (labelled: R0 FAIL)
HY1: TOO FEW (labelled: R0 FAIL)
HY2: NOT DECIDED (labelled: R0 FAIL)
P1: FAIL (labelled: R0 FAIL)
```

## 3. The registered rules' words, and the verdicts (BLIND; every verdict but R0's and S6's carries the label "R0 FAIL")

Quoted from `E218.md` (section 7 unless named), pinned in `SHA256SUMS-e218-registration`:

- **The question** (section 1): "Do MM1-v3.2's frozen forecasts of a matmul's clock cycles, seconds and joules hold on points that never ran on aifoundry3 card 0, does MM1-v3.2 beat MM1-v3 and MM1-v3.1 there, and does each change it made - the gemmLnc term and the layout term - beat the model without it on its own family?" "The registered answer is every registered point's": "families G, Gt, Y and F as kept".
- **The measured side:** "per run: the wall cycles an op (the slowest minion's counter a GEMM / ops a minion a GEMM), the counter's mean, seconds a GEMM, W over idle (the board's median inside the counted launches less the median of the run's last 5 s of rest), J over idle (W x seconds), J with the card at rest (the board's work median x seconds)"; "a run whose record differs from its point (arm, type, minions, or the shire mask read as a number), or whose rgm211-host walk or gate is not good, is set aside and flagged. A point is the mean of its kept runs; every E218 point is its own case." No run was set aside: the scorer's flags are empty, and every point has its two kept runs.
- **R0 and S6:** R0 is "every check of C exact or approx; the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its gate GATE OK; family G's smoke s03 failing while no G point ran is flagged, not an R0 failure"; S6 is "every kept run's samples at 590-610 MHz"; for either, "a FAIL labels every other verdict".
- **MM1-v3.2's per-case and per-point rules:** "each passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its scored cases or points, FAIL otherwise, TOO FEW under 10, NO DATA with none". "The band is twice the larger of MM1-v3.2's two held-out rms errors without configuration twins" "- (i) leave one experiment out over every point, (ii) the same over this card's points - rounded up to a whole percent". With 52 cases or points, 47 must pass.
- **The watts points:** "Points under about 3 W over idle are scored in watts in E1 and E2" "(MM1-v3.2's frozen W or the measured W under 3 W)", within 0.58 W; "E3 and E4 stay relative." 11 points read so: y01a, y01b, y02a, y02b, y03b, y04a, y04b, y05a, y05b, y06a, y06b (every Y point but y07a, y07b, y08a, y08b).
- **The ties:** "cycles 0.005 in ln, seconds 0.005 in ln, joules 0.01 in ln, watts points 0.1 W".
- **The head-to-heads:** "per case d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - |W - first|, in W), decided when |d| exceeds the tie; the exact two-sided sign test over the decided: '<first> BETTER' or '<second> BETTER' at p < 0.05 with at least the rule's minimum decided (10; 8 for family G's tests, which hold 12 points: at 8 decided only 8 of 8 decides, p 0.008), NOT DECIDED otherwise, TOO FEW under the minimum, NO DATA with none." H1-H5 are "MM1-v3.2 vs MM1-v3: wall, the counter's mean, seconds (per case), J over idle given t, J over idle with t forecast (per point), over every registered point"; H6-H10 "the same against MM1-v3.1"; HG1 and HG2 "MM1-v3.2 vs 'MM1-v3.2 without its gemmLnc term' on family G (given t; with t forecast)"; HG3 and HG4 "MM1-v3.2 vs 'v3.1 + gemmLnc term' on G"; HY1 "MM1-v3.2 vs 'MM1-v3.2 without its layout term' on Y (D3: TOO FEW by construction)"; HY2 "MM1-v3.2 vs 'v3.1 + contention' on Y (wall)". "The bootstrap 95% interval of each test's mean d is REPORTED beside (10,000 resamples, seeded "E218|bootstrap|<rule>")." The interval counts only the cases scored in ln (none of the watts cases).
- **THE PAIR RULE (P1):** "MM1-v3.2 prices both masks of every Y pair alike; of the complete Y pairs with data, a pair is SEPARATED when its measured |ln(wall a / wall b)| (each point's mean) exceeds" 0.0077 "in ln (E216's registered threshold, twice the governed card's cycles session-repeat rms: far above this card's within-session floor, 0.00056 in ln a run)". PASS "(MM1-v3.2's claim holds: no layout effect it misses at equal shire count) when at least 5 pairs have data and at most one is separated"; FAIL "when at least 5 have data and two or more are separated; TOO FEW under 5; NO DATA with none." Stated before the data: "E216 measured a real 4-7% placement effect on aifoundry2 card 0 (its P1 FAIL), so a FAIL here is a live possibility, stated before the data."
- **P1 for each frozen candidate, E216's form (REPORTED):** "of the separated pairs, the share the candidate orders right (a 0 forecast orders none); PASS with at least 5 separated, more than half right and the one-sided exact binomial p <= 0.05; FAIL otherwise; TOO FEW under 5."
- **What the day can say** (section 8, before the data): "H1-H3 and H6-H8 test refits, not a new time form; a NOT DECIDED is the expected reading whichever is better where the gaps are small (section 1)." And on MM1-v3.2's own declaration: "A PASS here does not reverse that rule; a FAIL is a blind failure of a model its own rules had not accepted."

| rule | what it scores | band | verdict (printed) | in band (needed) | MM1-v3.2 out of band (measured / forecast - 1, %; at a watts point the absolute W difference) |
|---|---|---|---|---|---|
| R0 | the checks of C, the smokes, the rgm211-host walks and gates | - | **FAIL** | one failure: `f04 run 77: checks []` (f04's run 77 printed no check of C; section 11, clause 1); every other check read approx (98) or exact (10); the smokes' counter means 819.28 and 754.18 cycles an op; walks and gates good | - |
| S6 | every kept run's clock | 590-610 MHz | **PASS** | every kept run inside it (no S6 failure) | - |
| T1 | cycles an op, the wall | 11% | **FAIL (labelled: R0 FAIL)** | 45 of 52 (47) | g01 -11.69, g02 -11.88, g03 -11.98, g04 +12.93, g05 -12.83, g08 +11.68, g11 +23.72 |
| T2 | cycles an op, the counter's mean | 14% | **PASS (labelled: R0 FAIL)** | 47 of 52 (47) | g11 +24.52, y01a +14.85, y04a +26.12, y05a +30.87, y06a +26.11 |
| T3 | seconds a GEMM (T1's bases) | 11% | **FAIL (labelled: R0 FAIL)** | 45 of 52 (47) | g01 -11.61, g02 -11.80, g03 -11.90, g04 +12.85, g05 -12.75, g08 +11.50, g11 +21.72 |
| E1 | J over idle given the measured op time and seconds | 10% | **PASS (labelled: R0 FAIL)** | 48 of 52 (47) | g03 -10.07, g04 +23.83, g08 +30.77, g11 +14.52 |
| E2 | J over idle with the seconds forecast | 12% | **PASS (labelled: R0 FAIL)** | 49 of 52 (47) | g04 +24.55, g08 +31.36, g11 +13.95 |
| E3 | J with the card at rest given t (the measured rest x t + E1's J) | 4% | **FAIL (labelled: R0 FAIL)** | 46 of 52 (47) | g03 -5.36, g04 +10.26, g05 -4.04, g08 +13.08, g09 -4.28, g11 +6.13 |
| E4 | J with the card at rest with the seconds forecast | 10% | **PASS (labelled: R0 FAIL)** | 47 of 52 (47) | g03 -11.17, g04 +18.22, g05 -10.13, g08 +20.45, g11 +18.04 |
| P1 | the pair rule | 0.0077 ln | **FAIL (labelled: R0 FAIL)** | 7 of 7 complete pairs separated (PASS allows at most one) | section 6 |

The bands' arithmetic, as registered: T1 2 x max(5.295, 4.5281) = 10.59 -> 11%; T2 2 x max(6.5118, 5.1384) = 13.02 -> 14%; T3 2 x max(5.295, 4.5281) = 10.59 -> 11%; E1 2 x max(4.9755, 4.8271) = 9.95 -> 10%; E2 2 x max(5.7703, 4.9711) = 11.54 -> 12%; E3 2 x max(1.6196, 1.5539) = 3.24 -> 4%; E4 2 x max(4.7497, 4.029) = 9.50 -> 10%; the watts band 2 x max(0.2598, 0.2868, 0.06723) -> 0.58 W.

| test | first vs second | on | quantity | verdict (printed) | first / second / ties | p (two-sided) | decided needed | bootstrap mean d [95%] (REPORTED) | P(first BETTER if truth first), registered (REPORTED) |
|---|---|---|---|---|---|---|---|---|---|
| H1 | MM1-v3.2 vs MM1-v3 | every registered point (52) | wall cycles | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 32 / 13 / 7 | 0.0066 | 10 | +0.0207 [+0.0127, +0.0291] (n 52) | 0.289 |
| H2 | MM1-v3.2 vs MM1-v3 | every registered point (52) | the counter's mean | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 36 / 7 / 9 | 8.96e-06 | 10 | +0.0231 [+0.0155, +0.0306] (n 52) | 0.197 |
| H3 | MM1-v3.2 vs MM1-v3 | every registered point (52) | seconds | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 32 / 13 / 7 | 0.0066 | 10 | +0.0209 [+0.0131, +0.0293] (n 52) | 0.272 |
| H4 | MM1-v3.2 vs MM1-v3 | every registered point (52) | J over idle given t | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 26 / 0 / 26 | 2.98e-08 | 10 | +0.0505 [+0.0287, +0.0748] (n 41) | 0.737 |
| H5 | MM1-v3.2 vs MM1-v3 | every registered point (52) | J over idle, t forecast | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 25 / 1 / 26 | 8.05e-07 | 10 | +0.0506 [+0.0289, +0.0759] (n 41) | 0.726 |
| H6 | MM1-v3.2 vs MM1-v3.1 | every registered point (52) | wall cycles | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 28 / 13 / 11 | 0.0275 | 10 | +0.0254 [+0.0159, +0.0353] (n 52) | 0.363 |
| H7 | MM1-v3.2 vs MM1-v3.1 | every registered point (52) | the counter's mean | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 31 / 7 / 14 | 1.16e-04 | 10 | +0.0276 [+0.0183, +0.0372] (n 52) | 0.256 |
| H8 | MM1-v3.2 vs MM1-v3.1 | every registered point (52) | seconds | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 28 / 13 / 11 | 0.0275 | 10 | +0.0255 [+0.0156, +0.0353] (n 52) | 0.37 |
| H9 | MM1-v3.2 vs MM1-v3.1 | every registered point (52) | J over idle given t | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 24 / 0 / 28 | 1.19e-07 | 10 | +0.0488 [+0.0273, +0.0745] (n 41) | 0.781 |
| H10 | MM1-v3.2 vs MM1-v3.1 | every registered point (52) | J over idle, t forecast | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 26 / 1 / 25 | 4.17e-07 | 10 | +0.0490 [+0.0271, +0.0746] (n 41) | 0.718 |
| HG1 | MM1-v3.2 vs MM1-v3.2 without its gemmLnc term | family G (12) | J over idle given t | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 11 / 0 / 1 | 9.77e-04 | 8 | +0.1543 [+0.1064, +0.2001] (n 12) | 0.999 |
| HG2 | MM1-v3.2 vs MM1-v3.2 without its gemmLnc term | family G (12) | J over idle, t forecast | **MM1-v3.2 BETTER (labelled: R0 FAIL)** | 11 / 0 / 1 | 9.77e-04 | 8 | +0.1508 [+0.1007, +0.1990] (n 12) | 0.994 |
| HG3 | MM1-v3.2 vs v3.1 + gemmLnc term | family G (12) | J over idle given t | **NOT DECIDED (labelled: R0 FAIL)** | 9 / 2 / 1 | 0.0654 | 8 | +0.0211 [+0.0053, +0.0356] (n 12) | 0.062 |
| HG4 | MM1-v3.2 vs v3.1 + gemmLnc term | family G (12) | J over idle, t forecast | **NOT DECIDED (labelled: R0 FAIL)** | 9 / 2 / 1 | 0.0654 | 8 | +0.0217 [+0.0054, +0.0363] (n 12) | 0.043 |
| HY1 | MM1-v3.2 vs MM1-v3.2 without its layout term | family Y (15) | wall cycles | **TOO FEW (labelled: R0 FAIL)** | 0 / 0 / 15 | - | 10 | +0.0000 [+0.0000, +0.0000] (n 15) | - |
| HY2 | MM1-v3.2 vs v3.1 + contention | family Y (15) | wall cycles | **NOT DECIDED (labelled: R0 FAIL)** | 10 / 5 / 0 | 0.3018 | 10 | +0.0111 [+0.0021, +0.0198] (n 15) | 0.05 |

## 4. MM1-v3.2 point by point (the scorer's cells; BLIND)

Measured / forecast - 1 in %, **bold** where out of its band. Wall and counter-mean cycles an op are the card's and MM1-v3.2's (its frozen 600 MHz figures); seconds are milliseconds a GEMM. MM1-v3.2's W over idle given t is its frozen A + B / t_op at the point's measured op time (the measured wall cycles an op / 600 MHz), and E1 is that W times the measured seconds against the measured J over idle. At a watts point (marked W), E1 and E2 read |W measured - W forecast| in W, against the 0.58 W band. The runs column names the point's two kept runs by their place in the session.

**Family G: 'rgm136 gemmLnc' on rgm211's host (12 points; the G block, last)**

| point | GEMM, format, mask | runs | wall: measured / v3.2 | T1 | counter: measured / v3.2 | T2 | ms: measured / v3.2 | T3 | W over idle: measured / v3.2 given t | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | `gemmLnc2x6x8` fp32, 0xffffffff; twin g01t; NB5-6 | 88, 105 | 1,033.2 / 1,170.0 | **-11.69** | 1,032.9 / 1,157.3 | -10.74 | 10.589 / 11.981 | **-11.61** | 25.12 / 26.59 | -5.53 | -5.91 | -2.94 | -8.75 |
| g02 | `gemmLnc2x6x7` fp32, 0xffffffff; twin g02t; NB5-6 | 90, 103 | 1,017.3 / 1,154.4 | **-11.88** | 1,017.1 / 1,141.9 | -10.93 | 9.123 / 10.344 | **-11.80** | 25.54 / 26.98 | -5.33 | -5.72 | -2.85 | -8.73 |
| g03 | `gemmLnc2x5x8` fp32, 0xffffffff; twin g03t; NB5-6 | 89, 104 | 1,038.7 / 1,180.1 | **-11.98** | 1,038.5 / 1,167.2 | -11.03 | 8.872 / 10.070 | **-11.90** | 24.02 / 26.72 | **-10.07** | -10.45 | **-5.36** | **-11.17** |
| g04 | `gemmLnc7x5x14` fp32, 0xffffffff; twin g04t; NB5-6 | 86, 107 | 1,664.4 / 1,473.9 | **+12.93** | 1,650.3 / 1,457.9 | +13.20 | 86.933 / 77.036 | **+12.85** | 21.89 / 17.67 | **+23.83** | **+24.55** | **+10.26** | **+18.22** |
| g05 | `gemmLnc8x6x3` fp32, 0xffffffff; twin g05t; NB5-6 | 95, 98 | 951.4 / 1,091.5 | **-12.83** | 951.3 / 1,079.6 | -11.88 | 14.628 / 16.765 | **-12.75** | 26.81 / 28.93 | -7.32 | -7.71 | **-4.04** | **-10.13** |
| g06 | `gemmLnc1x14x4` fp32, 0xffffffff; twin g06t; NB12-15 | 93, 100 | 993.0 / 1,092.6 | -9.11 | 968.3 / 1,080.7 | -10.40 | 5.937 / 6.526 | -9.03 | 25.98 / 26.95 | -3.61 | -3.88 | -1.93 | -6.40 |
| g07 | `gemmLnc1x13x4` fp32, 0xffffffff; no twin (D1); NB12-15 | 94, 99 | 990.8 / 1,090.8 | -9.17 | 966.1 / 1,079.0 | -10.46 | 5.501 / 6.050 | -9.08 | 26.11 / 27.04 | -3.47 | -3.73 | -1.86 | -6.34 |
| g08 | `gemmLnc2x14x16` fp32, 0xffffffff; twin g08t; NB12-15 | 85, 108 | 1,654.4 / 1,481.4 | **+11.68** | 1,641.9 / 1,465.3 | +12.06 | 78.932 / 70.790 | **+11.50** | 22.57 / 17.25 | **+30.77** | **+31.36** | **+13.08** | **+20.45** |
| g09 | `gemmLnc5x1x3` fp32, 0xffffffff; twin g09t; NB1-3 | 96, 97 | 1,377.5 / 1,344.7 | +2.44 | 1,359.9 / 1,330.1 | +2.24 | 2.206 / 2.152 | +2.52 | 22.78 / 24.85 | -8.32 | -8.15 | **-4.28** | -3.03 |
| g10 | `gemmLnc2x1x12` fp32, 0xffffffff; twin g10t; NB1-3 | 91, 102 | 1,374.7 / 1,399.3 | -1.76 | 1,354.8 / 1,384.0 | -2.11 | 3.522 / 3.582 | -1.68 | 22.79 / 24.66 | -7.57 | -7.57 | -3.88 | -4.67 |
| g11 | `gemmLnc6x2x48` fp32, 0xffffffff; twin g11t; NB1-3 | 87, 106 | 1,889.5 / 1,527.2 | **+23.72** | 1,881.0 / 1,510.6 | **+24.52** | 114.215 / 93.832 | **+21.72** | 19.64 / 17.15 | **+14.52** | **+13.95** | **+6.13** | **+18.04** |
| g12 | `gemmLnc5x1x8` fp32, 0xffffffff; twin g12t; NB1-3 | 92, 101 | 1,376.8 / 1,398.7 | -1.57 | 1,356.7 / 1,383.5 | -1.94 | 5.877 / 5.968 | -1.53 | 23.04 / 24.67 | -6.62 | -6.64 | -3.39 | -4.13 |

**Family Gt: the G points' cooperative twins, 'rgm136 gemmL' (11 points; g07t dropped by D1)**

| point | GEMM, format, mask | runs | wall: measured / v3.2 | T1 | counter: measured / v3.2 | T2 | ms: measured / v3.2 | T3 | W over idle: measured / v3.2 given t | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g01t | `gemmL2x6x8` fp32, 0xffffffff; twin of g01 | 10, 74 | 1,173.0 / 1,190.6 | -1.48 | 1,172.9 / 1,177.6 | -0.40 | 12.024 / 12.192 | -1.37 | 19.23 / 19.15 | +0.41 | +0.44 | +0.18 | -0.56 |
| g02t | `gemmL2x6x7` fp32, 0xffffffff; twin of g02 | 12, 72 | 1,158.8 / 1,175.3 | -1.40 | 1,158.7 / 1,162.5 | -0.33 | 10.391 / 10.530 | -1.32 | 19.23 / 19.36 | -0.69 | -0.69 | -0.31 | -1.04 |
| g03t | `gemmL2x5x8` fp32, 0xffffffff; twin of g03 | 36, 48 | 1,186.8 / 1,200.5 | -1.14 | 1,186.7 / 1,187.4 | -0.05 | 10.137 / 10.244 | -1.04 | 18.53 / 18.96 | -2.25 | -2.22 | -1.01 | -1.57 |
| g04t | `gemmL7x5x14` fp32, 0xffffffff; twin of g04 | 9, 75 | 1,520.1 / 1,491.3 | +1.93 | 1,516.2 / 1,475.0 | +2.79 | 79.550 / 77.943 | +2.06 | 15.52 / 15.71 | -1.17 | -0.93 | -0.47 | +0.84 |
| g05t | `gemmL8x6x3` fp32, 0xffffffff; twin of g05 | 8, 76 | 1,097.8 / 1,112.2 | -1.30 | 1,097.8 / 1,100.1 | -0.21 | 16.879 / 17.084 | -1.20 | 19.96 / 20.51 | -2.67 | -2.64 | -1.26 | -1.87 |
| g06t | `gemmL1x14x4` fp32, 0xffffffff; twin of g06 | 37, 47 | 1,097.9 / 1,114.6 | -1.49 | 1,084.2 / 1,102.4 | -1.65 | 6.563 / 6.658 | -1.42 | 20.12 / 20.40 | -1.38 | -1.37 | -0.64 | -1.40 |
| g08t | `gemmL2x14x16` fp32, 0xffffffff; twin of g08 | 23, 61 | 1,563.1 / 1,499.1 | +4.27 | 1,563.0 / 1,482.7 | +5.41 | 74.758 / 71.635 | +4.36 | 14.97 / 15.34 | -2.47 | -2.12 | -0.98 | +1.72 |
| g09t | `gemmL5x1x3` fp32, 0xffffffff; twin of g09 | 20, 64 | 1,429.1 / 1,358.2 | +5.22 | 1,412.8 / 1,343.4 | +5.17 | 2.289 / 2.173 | +5.31 | 16.12 / 16.18 | -0.36 | +0.03 | -0.15 | +3.08 |
| g10t | `gemmL2x1x12` fp32, 0xffffffff; twin of g10 | 39, 45 | 1,409.3 / 1,411.8 | -0.17 | 1,397.3 / 1,396.4 | +0.06 | 3.611 / 3.614 | -0.08 | 15.83 / 16.15 | -2.01 | -1.93 | -0.82 | -0.83 |
| g11t | `gemmL6x2x48` fp32, 0xffffffff; twin of g11 | 41, 43 | 1,637.3 / 1,547.7 | +5.79 | 1,637.3 / 1,530.9 | +6.95 | 100.596 / 95.093 | +5.79 | 14.48 / 15.02 | -3.56 | -3.21 | -1.39 | +2.16 |
| g12t | `gemmL5x1x8` fp32, 0xffffffff; twin of g12 | 25, 59 | 1,414.9 / 1,411.2 | +0.26 | 1,401.0 / 1,395.9 | +0.37 | 6.042 / 6.021 | +0.34 | 15.89 / 16.15 | -1.60 | -1.50 | -0.65 | -0.41 |

**Family Y: subset masks, 'rgm136 gemmL' (15 points; y03a dropped by D1)**

| point | GEMM, format, mask | runs | wall: measured / v3.2 | T1 | counter: measured / v3.2 | T2 | ms: measured / v3.2 | T3 | W over idle: measured / v3.2 given t | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| y01a | `gemmL4x2x8` fp32, 0xf000; pair y01 | 11, 73 | 1,109.6 / 1,185.5 | -6.40 | 1,109.6 / 966.1 | **+14.85** | 7.582 / 8.093 | -6.31 | 2.36 / 2.82 (W) | 0.46 W | 0.31 W | -1.77 | -7.43 |
| y01b | `gemmL4x2x8` fp32, 0x1010101; pair y01 | 6, 78 | 1,214.4 / 1,185.5 | +2.44 | 1,166.5 / 1,172.6 | -0.52 | 8.297 / 8.093 | +2.53 | 2.54 / 2.61 (W) | 0.07 W | 0.12 W | -0.27 | +2.04 |
| y02a | `gemmL1x16x24` fp32, 0xf; pair y02 | 14, 70 | 1,537.4 / 1,495.8 | +2.78 | 1,537.4 / 1,479.5 | +3.91 | 63.029 / 61.269 | +2.87 | 2.78 / 2.28 (W) | 0.50 W | 0.45 W | +1.95 | +4.67 |
| y02b | `gemmL1x16x24` fp32, 0x3030; pair y02 | 4, 80 | 1,473.8 / 1,495.8 | -1.47 | 1,473.8 / 1,479.5 | -0.39 | 60.415 / 61.269 | -1.39 | 2.54 / 2.36 (W) | 0.18 W | 0.21 W | +0.72 | -0.57 |
| y03b | `gemmL1x4x24` fp32, 0x3030; pair y03 | 30, 54 | 1,473.8 / 1,495.8 | -1.47 | 1,473.8 / 1,479.5 | -0.39 | 15.104 / 15.317 | -1.39 | 2.54 / 2.36 (W) | 0.18 W | 0.21 W | +0.71 | -0.58 |
| y04a | `gemmL2x16x24` fp32, 0xf; pair y04 | 34, 50 | 1,537.5 / 1,495.8 | +2.79 | 1,537.5 / 1,219.1 | **+26.12** | 126.085 / 122.537 | +2.90 | 2.79 / 2.28 (W) | 0.51 W | 0.46 W | +1.98 | +4.72 |
| y04b | `gemmL2x16x24` fp32, 0x3030; pair y04 | 28, 56 | 1,473.7 / 1,495.8 | -1.48 | 1,473.7 / 1,479.5 | -0.39 | 120.832 / 122.537 | -1.39 | 2.54 / 2.36 (W) | 0.18 W | 0.21 W | +0.70 | -0.59 |
| y05a | `gemmL2x2x24` fp32, 0xf; pair y05 | 18, 66 | 1,537.4 / 1,441.4 | +6.66 | 1,537.4 / 1,174.7 | **+30.87** | 15.756 / 14.760 | +6.75 | 2.80 / 2.27 (W) | 0.53 W | 0.41 W | +2.07 | +8.43 |
| y05b | `gemmL2x2x24` fp32, 0x3030; pair y05 | 5, 79 | 1,473.9 / 1,441.4 | +2.26 | 1,473.9 / 1,425.7 | +3.38 | 15.106 / 14.760 | +2.34 | 2.59 / 2.35 (W) | 0.24 W | 0.20 W | +0.97 | +3.15 |
| y06a | `gemmL2x8x24` fp32, 0xf; pair y06 | 24, 60 | 1,537.4 / 1,495.8 | +2.78 | 1,537.4 / 1,219.1 | **+26.11** | 63.029 / 61.269 | +2.87 | 2.83 / 2.28 (W) | 0.55 W | 0.50 W | +2.14 | +4.86 |
| y06b | `gemmL2x8x24` fp32, 0x3030; pair y06 | 2, 82 | 1,473.7 / 1,495.8 | -1.48 | 1,473.7 / 1,479.5 | -0.39 | 60.417 / 61.269 | -1.39 | 2.55 / 2.36 (W) | 0.19 W | 0.22 W | +0.74 | -0.55 |
| y07a | `gemmL4x16x24` fp32, 0x55555555; pair y07 | 29, 55 | 1,603.2 / 1,539.3 | +4.16 | 1,603.2 / 1,522.5 | +5.30 | 263.078 / 252.191 | +4.32 | 7.84 / 7.85 | -0.07 | +0.42 | -0.02 | +3.31 |
| y07b | `gemmL4x16x24` fp32, 0xffff0000; pair y07 | 31, 53 | 1,637.7 / 1,539.3 | +6.40 | 1,637.7 / 1,522.5 | +7.57 | 268.529 / 252.191 | +6.48 | 7.68 / 7.69 | -0.25 | +0.34 | -0.06 | +4.89 |
| y08a | `gemmL4x2x24` fp32, 0x55555555; pair y08 | 3, 81 | 1,603.2 / 1,483.3 | +8.09 | 1,603.2 / 1,467.1 | +9.28 | 32.860 / 30.377 | +8.17 | 7.82 / 7.80 | +0.23 | +0.95 | +0.06 | +6.23 |
| y08b | `gemmL4x2x24` fp32, 0xffff0000; pair y08 | 21, 63 | 1,642.6 / 1,483.3 | +10.74 | 1,642.6 / 1,467.1 | +11.96 | 33.629 / 30.377 | +10.71 | 7.67 / 7.63 | +0.50 | +1.33 | +0.12 | +8.23 |

**Family F: full chip, 'rgm136 gemmL' (14 points)**

| point | GEMM, format, mask | runs | wall: measured / v3.2 | T1 | counter: measured / v3.2 | T2 | ms: measured / v3.2 | T3 | W over idle: measured / v3.2 given t | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f01 | `gemmL2x16x3` fp32, 0xffffffff | 15, 69 | 1,136.4 / 1,248.9 | -9.01 | 1,136.2 / 1,235.3 | -8.02 | 11.650 / 12.788 | -8.90 | 19.44 / 20.17 | -3.61 | -3.97 | -1.68 | -6.72 |
| f02 | `gemmL10x16x3` fp32, 0xffffffff | 22, 62 | 1,141.0 / 1,248.9 | -8.64 | 1,140.6 / 1,235.3 | -7.66 | 58.446 / 63.942 | -8.59 | 19.39 / 20.09 | -3.48 | -3.89 | -1.61 | -6.51 |
| f03 | `gemmL1x10x3` fp32, 0xffffffff | 16, 68 | 1,102.0 / 1,112.5 | -0.94 | 1,089.5 / 1,100.4 | -0.99 | 3.530 / 3.560 | -0.85 | 20.14 / 20.46 | -1.57 | -1.52 | -0.73 | -1.16 |
| f04 | `gemmL15x16x32` fp32, 0xffffffff | 7, 77 | 1,621.3 / 1,597.5 | +1.49 | 1,621.3 / 1,580.1 | +2.61 | 1,327.858 / 1,308.631 | +1.47 | 14.62 / 15.20 | -3.77 | -3.70 | -1.50 | -0.60 |
| f05 | `gemmL11x16x3` fp16, 0xffffffff | 33, 51 | 1,143.9 / 1,248.9 | -8.40 | 1,141.8 / 1,235.3 | -7.57 | 64.466 / 70.336 | -8.35 | 18.32 / 19.03 | -3.69 | -4.10 | -1.66 | -6.52 |
| f06 | `gemmL12x16x3` fp16, 0xffffffff | 13, 71 | 1,154.8 / 1,248.9 | -7.53 | 1,151.7 / 1,235.3 | -6.76 | 71.028 / 76.730 | -7.43 | 18.18 / 18.86 | -3.61 | -3.92 | -1.62 | -5.92 |
| f07 | `gemmL13x16x3` fp16, 0xffffffff | 40, 44 | 1,145.7 / 1,248.9 | -8.26 | 1,144.6 / 1,235.3 | -7.34 | 76.337 / 83.124 | -8.17 | 18.16 / 19.00 | -4.45 | -4.80 | -1.99 | -6.73 |
| f08 | `gemmL3x14x4` fp16, 0xffffffff | 19, 65 | 1,109.1 / 1,165.6 | -4.85 | 1,108.9 / 1,153.0 | -3.82 | 19.893 / 20.888 | -4.77 | 18.57 / 19.30 | -3.78 | -3.95 | -1.71 | -4.41 |
| f09 | `gemmL6x13x4` fp16, 0xffffffff | 38, 46 | 1,113.4 / 1,143.0 | -2.58 | 1,113.2 / 1,130.5 | -1.53 | 37.089 / 38.038 | -2.49 | 18.56 / 19.16 | -3.13 | -3.17 | -1.41 | -2.79 |
| f10 | `gemmL14x16x3` int8, 0xffffffff | 26, 58 | 1,152.0 / 1,273.5 | -9.54 | 1,151.6 / 1,259.7 | -8.58 | 82.694 / 91.285 | -9.41 | 9.43 / 10.15 | -7.04 | -7.86 | -2.14 | -8.97 |
| f11 | `gemmL15x16x3` int8, 0xffffffff | 27, 57 | 1,157.8 / 1,273.5 | -9.08 | 1,155.1 / 1,259.7 | -8.30 | 89.038 / 97.806 | -8.96 | 9.47 / 10.10 | -6.29 | -7.09 | -1.91 | -8.43 |
| f12 | `gemmL16x16x3` int8, 0xffffffff | 32, 52 | 1,168.3 / 1,273.5 | -8.26 | 1,163.7 / 1,259.7 | -7.62 | 95.821 / 104.326 | -8.15 | 9.45 / 10.02 | -5.70 | -6.43 | -1.72 | -7.66 |
| f13 | `gemmL7x9x3` int8, 0xffffffff | 35, 49 | 1,144.3 / 1,180.3 | -3.05 | 1,144.2 / 1,167.4 | -1.99 | 23.095 / 23.795 | -2.94 | 9.55 / 10.02 | -4.68 | -4.87 | -1.41 | -3.51 |
| f14 | `gemmL5x7x4` int8, 0xffffffff | 17, 67 | 1,152.7 / 1,190.4 | -3.16 | 1,152.6 / 1,177.4 | -2.11 | 17.228 / 17.776 | -3.08 | 9.31 / 9.85 | -5.47 | -5.70 | -1.62 | -3.84 |

**The reading** (post hoc, REPORTED). Every T1, T3 and E1-E4 miss is a family G point. The time misses go both ways: g01, g02, g03, g05 read 11.7-12.8% under MM1-v3.2's wall, and g04, g08, g11 11.7-23.7% over it. At the 11 G-Gt pairs the card's gemmLnc wall reads 0.867-1.154 of its cooperative twin's, while MM1-v3.2 prices each G point at 0.980-0.991 of its twin's (section 8). The energy misses are the gemmLnc points E215 named, and the Gt, Y and F points pass every energy rule. 4 of T2's 5 misses are Y points at the masks 0xf and 0xf000 (y01a, y04a, y05a, y06a). There the card's counter mean is its wall (0.99999-1.00000 of it), while MM1-v3.2's counter mean is 0.815 of its own wall at each.

## 5. The head-to-heads, case by case (BLIND; the scorer's own `h_cells()`, `decide()` and `boot()` made again, every d, tally, p and interval equal to `scores-e218-A.json`)

Each case's d = |ln(measured / second)| - |ln(measured / first)| (at a watts point, marked W, |W - second| - |W - first| in W). A case reads for the **first** model when d > the tie, for the **second** when d < -tie, and tie otherwise. The errors are measured / forecast - 1 in % (at a watts point, W measured - W forecast in W), the first model's then the second's.

**H1-H3: MM1-v3.2 (first) against MM1-v3 (second), time per case (tie 0.005 in ln)**

| point | H1: errors v3.2 / v3 | d | reads | H2: errors v3.2 / v3 | d | reads | H3: errors v3.2 / v3 | d | reads |
|---|---|---|---|---|---|---|---|---|---|
| g01 | -11.69 / -15.57 | +0.0449 | v3.2 | -10.74 / -14.66 | +0.0449 | v3.2 | -11.61 / -15.50 | +0.0449 | v3.2 |
| g02 | -11.88 / -14.96 | +0.0356 | v3.2 | -10.93 / -14.04 | +0.0356 | v3.2 | -11.80 / -14.89 | +0.0356 | v3.2 |
| g03 | -11.98 / -14.29 | +0.0265 | v3.2 | -11.03 / -13.36 | +0.0265 | v3.2 | -11.90 / -14.21 | +0.0265 | v3.2 |
| g04 | +12.93 / +13.43 | +0.0044 | tie | +13.20 / +13.71 | +0.0044 | tie | +12.85 / +13.35 | +0.0044 | tie |
| g05 | -12.83 / -12.03 | -0.0091 | v3 | -11.88 / -11.08 | -0.0091 | v3 | -12.75 / -11.95 | -0.0091 | v3 |
| g06 | -9.11 / -15.40 | +0.0717 | v3.2 | -10.40 / -16.60 | +0.0717 | v3.2 | -9.03 / -15.32 | +0.0717 | v3.2 |
| g07 | -9.17 / -14.67 | +0.0624 | v3.2 | -10.46 / -15.88 | +0.0624 | v3.2 | -9.08 / -14.59 | +0.0624 | v3.2 |
| g08 | +11.68 / +12.31 | +0.0056 | v3.2 | +12.06 / +12.69 | +0.0056 | v3.2 | +11.50 / +12.13 | +0.0056 | v3.2 |
| g09 | +2.44 / +1.36 | -0.0105 | v3 | +2.24 / +1.17 | -0.0105 | v3 | +2.52 / +1.45 | -0.0105 | v3 |
| g10 | -1.76 / -1.47 | -0.0029 | tie | -2.11 / -1.82 | -0.0029 | tie | -1.68 / -1.39 | -0.0029 | tie |
| g11 | +23.72 / +23.01 | -0.0058 | v3 | +24.52 / +23.80 | -0.0058 | v3 | +21.72 / +21.02 | -0.0058 | v3 |
| g12 | -1.57 / -1.22 | -0.0036 | tie | -1.94 / -1.59 | -0.0036 | tie | -1.53 / -1.17 | -0.0036 | tie |
| g01t | -1.48 / -5.76 | +0.0444 | v3.2 | -0.40 / -4.73 | +0.0444 | v3.2 | -1.37 / -5.66 | +0.0444 | v3.2 |
| g02t | -1.40 / -4.81 | +0.0352 | v3.2 | -0.33 / -3.77 | +0.0352 | v3.2 | -1.32 / -4.73 | +0.0352 | v3.2 |
| g03t | -1.14 / -3.71 | +0.0263 | v3.2 | -0.05 / -2.65 | +0.0263 | v3.2 | -1.04 / -3.61 | +0.0263 | v3.2 |
| g04t | +1.93 / +2.38 | +0.0044 | tie | +2.79 / +3.24 | +0.0044 | tie | +2.06 / +2.51 | +0.0044 | tie |
| g05t | -1.30 / -0.41 | -0.0089 | v3 | -0.21 / +0.68 | +0.0046 | tie | -1.20 / -0.31 | -0.0089 | v3 |
| g06t | -1.49 / -8.18 | +0.0703 | v3.2 | -1.65 / -8.33 | +0.0703 | v3.2 | -1.42 / -8.11 | +0.0703 | v3.2 |
| g08t | +4.27 / +4.85 | +0.0056 | v3.2 | +5.41 / +6.00 | +0.0056 | v3.2 | +4.36 / +4.95 | +0.0056 | v3.2 |
| g09t | +5.22 / +4.15 | -0.0102 | v3 | +5.17 / +4.10 | -0.0102 | v3 | +5.31 / +4.24 | -0.0102 | v3 |
| g10t | -0.17 / +0.11 | -0.0007 | tie | +0.06 / +0.34 | +0.0028 | tie | -0.08 / +0.20 | +0.0012 | tie |
| g11t | +5.79 / +5.11 | -0.0064 | v3 | +6.95 / +6.27 | -0.0064 | v3 | +5.79 / +5.11 | -0.0064 | v3 |
| g12t | +0.26 / +0.61 | +0.0035 | tie | +0.37 / +0.72 | +0.0035 | tie | +0.34 / +0.69 | +0.0035 | tie |
| y01a | -6.40 / -4.97 | -0.0151 | v3 | +14.85 / +16.60 | +0.0151 | v3.2 | -6.31 / -4.88 | -0.0151 | v3 |
| y01b | +2.44 / +4.00 | +0.0151 | v3.2 | -0.52 / +1.00 | +0.0047 | tie | +2.53 / +4.09 | +0.0151 | v3.2 |
| y02a | +2.78 / +4.33 | +0.0150 | v3.2 | +3.91 / +5.48 | +0.0150 | v3.2 | +2.87 / +4.42 | +0.0150 | v3.2 |
| y02b | -1.47 / +0.01 | -0.0148 | v3 | -0.39 / +1.11 | +0.0071 | v3.2 | -1.39 / +0.09 | -0.0131 | v3 |
| y03b | -1.47 / +0.03 | -0.0145 | v3 | -0.39 / +1.13 | +0.0074 | v3.2 | -1.39 / +0.12 | -0.0128 | v3 |
| y04a | +2.79 / +4.34 | +0.0150 | v3.2 | +26.12 / +28.02 | +0.0150 | v3.2 | +2.90 / +4.45 | +0.0150 | v3.2 |
| y04b | -1.48 / +0.01 | -0.0148 | v3 | -0.39 / +1.11 | +0.0071 | v3.2 | -1.39 / +0.10 | -0.0131 | v3 |
| y05a | +6.66 / +7.87 | +0.0113 | v3.2 | +30.87 / +32.36 | +0.0113 | v3.2 | +6.75 / +7.96 | +0.0113 | v3.2 |
| y05b | +2.26 / +3.42 | +0.0113 | v3.2 | +3.38 / +4.56 | +0.0113 | v3.2 | +2.34 / +3.51 | +0.0113 | v3.2 |
| y06a | +2.78 / +4.33 | +0.0150 | v3.2 | +26.11 / +28.01 | +0.0150 | v3.2 | +2.87 / +4.42 | +0.0150 | v3.2 |
| y06b | -1.48 / +0.01 | -0.0148 | v3 | -0.39 / +1.11 | +0.0071 | v3.2 | -1.39 / +0.10 | -0.0130 | v3 |
| y07a | +4.16 / +5.52 | +0.0130 | v3.2 | +5.30 / +6.68 | +0.0130 | v3.2 | +4.32 / +5.69 | +0.0130 | v3.2 |
| y07b | +6.40 / +7.80 | +0.0130 | v3.2 | +7.57 / +8.98 | +0.0130 | v3.2 | +6.48 / +7.88 | +0.0130 | v3.2 |
| y08a | +8.09 / +9.11 | +0.0094 | v3.2 | +9.28 / +10.31 | +0.0094 | v3.2 | +8.17 / +9.19 | +0.0094 | v3.2 |
| y08b | +10.74 / +11.78 | +0.0094 | v3.2 | +11.96 / +13.01 | +0.0094 | v3.2 | +10.71 / +11.75 | +0.0094 | v3.2 |
| f01 | -9.01 / -15.13 | +0.0697 | v3.2 | -8.02 / -14.21 | +0.0697 | v3.2 | -8.90 / -15.04 | +0.0697 | v3.2 |
| f02 | -8.64 / -14.79 | +0.0697 | v3.2 | -7.66 / -13.88 | +0.0697 | v3.2 | -8.59 / -14.75 | +0.0697 | v3.2 |
| f03 | -0.94 / -0.49 | -0.0045 | tie | -0.99 / -0.54 | -0.0045 | tie | -0.85 / -0.39 | -0.0045 | tie |
| f04 | +1.49 / +2.22 | +0.0072 | v3.2 | +2.61 / +3.35 | +0.0072 | v3.2 | +1.47 / +2.20 | +0.0072 | v3.2 |
| f05 | -8.40 / -14.57 | +0.0697 | v3.2 | -7.57 / -13.79 | +0.0697 | v3.2 | -8.35 / -14.52 | +0.0697 | v3.2 |
| f06 | -7.53 / -13.76 | +0.0697 | v3.2 | -6.76 / -13.04 | +0.0697 | v3.2 | -7.43 / -13.66 | +0.0697 | v3.2 |
| f07 | -8.26 / -14.44 | +0.0697 | v3.2 | -7.34 / -13.58 | +0.0697 | v3.2 | -8.17 / -14.35 | +0.0697 | v3.2 |
| f08 | -4.85 / -9.60 | +0.0512 | v3.2 | -3.82 / -8.62 | +0.0512 | v3.2 | -4.77 / -9.52 | +0.0512 | v3.2 |
| f09 | -2.58 / -8.66 | +0.0645 | v3.2 | -1.53 / -7.68 | +0.0645 | v3.2 | -2.49 / -8.58 | +0.0645 | v3.2 |
| f10 | -9.54 / -15.01 | +0.0623 | v3.2 | -8.58 / -14.10 | +0.0623 | v3.2 | -9.41 / -14.88 | +0.0623 | v3.2 |
| f11 | -9.08 / -14.58 | +0.0623 | v3.2 | -8.30 / -13.84 | +0.0623 | v3.2 | -8.96 / -14.46 | +0.0623 | v3.2 |
| f12 | -8.26 / -13.80 | +0.0623 | v3.2 | -7.62 / -13.20 | +0.0623 | v3.2 | -8.15 / -13.70 | +0.0623 | v3.2 |
| f13 | -3.05 / -2.37 | -0.0070 | v3 | -1.99 / -1.31 | -0.0070 | v3 | -2.94 / -2.26 | -0.0070 | v3 |
| f14 | -3.16 / -2.56 | -0.0062 | v3 | -2.11 / -1.50 | -0.0062 | v3 | -3.08 / -2.48 | -0.0062 | v3 |

- **H1** (wall cycles): 32 / 13 / 7, p 0.0066: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **H2** (the counter's mean): 36 / 7 / 9, p 8.96e-06: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **H3** (seconds): 32 / 13 / 7, p 0.0066: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).

**H4 and H5: MM1-v3.2 (first) against MM1-v3 (second), J over idle per point (tie 0.01 in ln; 0.1 W at a watts point)**

| point | H4: errors v3.2 / v3 | d | reads | H5: errors v3.2 / v3 | d | reads |
|---|---|---|---|---|---|---|
| g01 | -5.53 / +14.57 | +0.0791 | v3.2 | -5.91 / +13.72 | +0.0676 | v3.2 |
| g02 | -5.33 / +15.03 | +0.0852 | v3.2 | -5.72 / +14.23 | +0.0741 | v3.2 |
| g03 | -10.07 / +10.32 | -0.0080 | tie | -10.45 / +9.59 | -0.0187 | v3 |
| g04 | +23.83 / +51.52 | +0.2018 | v3.2 | +24.55 / +52.66 | +0.2035 | v3.2 |
| g05 | -7.32 / +13.08 | +0.0469 | v3.2 | -7.71 / +12.54 | +0.0380 | v3.2 |
| g06 | -3.61 / +13.57 | +0.0905 | v3.2 | -3.88 / +12.78 | +0.0807 | v3.2 |
| g07 | -3.47 / +14.06 | +0.0962 | v3.2 | -3.73 / +13.32 | +0.0870 | v3.2 |
| g08 | +30.77 / +55.06 | +0.1704 | v3.2 | +31.36 / +55.98 | +0.1718 | v3.2 |
| g09 | -8.32 / +34.70 | +0.2110 | v3.2 | -8.15 / +34.92 | +0.2145 | v3.2 |
| g10 | -7.57 / +36.90 | +0.2354 | v3.2 | -7.57 / +36.88 | +0.2352 | v3.2 |
| g11 | +14.52 / +48.48 | +0.2597 | v3.2 | +13.95 / +48.16 | +0.2626 | v3.2 |
| g12 | -6.62 / +38.19 | +0.2550 | v3.2 | -6.64 / +38.14 | +0.2544 | v3.2 |
| g01t | +0.41 / -1.20 | +0.0080 | tie | +0.44 / -1.39 | +0.0097 | tie |
| g02t | -0.69 / -2.11 | +0.0144 | v3.2 | -0.69 / -2.29 | +0.0162 | v3.2 |
| g03t | -2.25 / -3.51 | +0.0130 | v3.2 | -2.22 / -3.61 | +0.0144 | v3.2 |
| g04t | -1.17 / -1.38 | +0.0021 | tie | -0.93 / -1.11 | +0.0018 | tie |
| g05t | -2.67 / -3.60 | +0.0096 | tie | -2.64 / -3.52 | +0.0092 | tie |
| g06t | -1.38 / -3.32 | +0.0199 | v3.2 | -1.37 / -3.66 | +0.0234 | v3.2 |
| g08t | -2.47 / -2.58 | +0.0012 | tie | -2.12 / -2.21 | +0.0008 | tie |
| g09t | -0.36 / -1.47 | +0.0112 | v3.2 | +0.03 / -1.15 | +0.0113 | v3.2 |
| g10t | -2.01 / -2.78 | +0.0079 | tie | -1.93 / -2.68 | +0.0077 | tie |
| g11t | -3.56 / -4.26 | +0.0072 | tie | -3.21 / -3.95 | +0.0077 | tie |
| g12t | -1.60 / -2.36 | +0.0078 | tie | -1.50 / -2.24 | +0.0076 | tie |
| y01a | -0.46 / -0.41 W | -0.049 W | tie | -0.31 / -0.29 W | -0.016 W | tie |
| y01b | -0.07 / -0.02 W | -0.051 W | tie | -0.12 / -0.11 W | -0.016 W | tie |
| y02a | +0.50 / +0.57 W | +0.068 W | tie | +0.45 / +0.49 W | +0.039 W | tie |
| y02b | +0.18 / +0.25 W | +0.068 W | tie | +0.21 / +0.25 W | +0.039 W | tie |
| y03b | +0.18 / +0.25 W | +0.069 W | tie | +0.21 / +0.25 W | +0.039 W | tie |
| y04a | +0.51 / +0.58 W | +0.068 W | tie | +0.46 / +0.49 W | +0.039 W | tie |
| y04b | +0.18 / +0.25 W | +0.068 W | tie | +0.21 / +0.25 W | +0.039 W | tie |
| y05a | +0.53 / +0.60 W | +0.068 W | tie | +0.41 / +0.45 W | +0.046 W | tie |
| y05b | +0.24 / +0.31 W | +0.068 W | tie | +0.20 / +0.25 W | +0.046 W | tie |
| y06a | +0.55 / +0.62 W | +0.068 W | tie | +0.50 / +0.53 W | +0.039 W | tie |
| y06b | +0.19 / +0.25 W | +0.068 W | tie | +0.22 / +0.25 W | +0.039 W | tie |
| y07a | -0.07 / +0.58 | +0.0051 | tie | +0.42 / +1.16 | +0.0074 | tie |
| y07b | -0.25 / +0.41 | +0.0016 | tie | +0.34 / +1.08 | +0.0074 | tie |
| y08a | +0.23 / +0.89 | +0.0066 | tie | +0.95 / +1.65 | +0.0069 | tie |
| y08b | +0.50 / +1.18 | +0.0067 | tie | +1.33 / +2.03 | +0.0069 | tie |
| f01 | -3.61 / -5.52 | +0.0200 | v3.2 | -3.97 / -6.22 | +0.0237 | v3.2 |
| f02 | -3.48 / -5.39 | +0.0200 | v3.2 | -3.89 / -6.14 | +0.0237 | v3.2 |
| f03 | -1.57 / -2.56 | +0.0102 | v3.2 | -1.52 / -2.49 | +0.0099 | tie |
| f04 | -3.77 / -3.83 | +0.0006 | tie | -3.70 / -3.72 | +0.0002 | tie |
| f05 | -3.69 / -5.59 | +0.0199 | v3.2 | -4.10 / -6.35 | +0.0237 | v3.2 |
| f06 | -3.61 / -5.50 | +0.0199 | v3.2 | -3.92 / -6.17 | +0.0237 | v3.2 |
| f07 | -4.45 / -6.33 | +0.0199 | v3.2 | -4.80 / -7.03 | +0.0237 | v3.2 |
| f08 | -3.78 / -5.40 | +0.0169 | v3.2 | -3.95 / -5.82 | +0.0197 | v3.2 |
| f09 | -3.13 / -4.98 | +0.0193 | v3.2 | -3.17 / -5.35 | +0.0227 | v3.2 |
| f10 | -7.04 / -9.23 | +0.0239 | v3.2 | -7.86 / -10.61 | +0.0303 | v3.2 |
| f11 | -6.29 / -8.50 | +0.0239 | v3.2 | -7.09 / -9.85 | +0.0303 | v3.2 |
| f12 | -5.70 / -7.92 | +0.0238 | v3.2 | -6.43 / -9.22 | +0.0303 | v3.2 |
| f13 | -4.68 / -5.00 | +0.0034 | tie | -4.87 / -5.12 | +0.0026 | tie |
| f14 | -5.47 / -5.64 | +0.0019 | tie | -5.70 / -5.82 | +0.0012 | tie |

- **H4** (J over idle given t): 26 / 0 / 26, p 2.98e-08: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **H5** (J over idle, t forecast): 25 / 1 / 26, p 8.05e-07: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).

**H6-H8: MM1-v3.2 (first) against MM1-v3.1 (second), time per case (tie 0.005 in ln)**

| point | H6: errors v3.2 / v3.1 | d | reads | H7: errors v3.2 / v3.1 | d | reads | H8: errors v3.2 / v3.1 | d | reads |
|---|---|---|---|---|---|---|---|---|---|
| g01 | -11.69 / -16.93 | +0.0611 | v3.2 | -10.74 / -16.04 | +0.0611 | v3.2 | -11.61 / -16.86 | +0.0611 | v3.2 |
| g02 | -11.88 / -16.43 | +0.0531 | v3.2 | -10.93 / -15.53 | +0.0531 | v3.2 | -11.80 / -16.36 | +0.0531 | v3.2 |
| g03 | -11.98 / -15.62 | +0.0422 | v3.2 | -11.03 / -14.71 | +0.0422 | v3.2 | -11.90 / -15.54 | +0.0422 | v3.2 |
| g04 | +12.93 / +13.25 | +0.0029 | tie | +13.20 / +13.53 | +0.0029 | tie | +12.85 / +13.18 | +0.0029 | tie |
| g05 | -12.83 / -11.88 | -0.0109 | v3.1 | -11.88 / -10.92 | -0.0109 | v3.1 | -12.75 / -11.80 | -0.0109 | v3.1 |
| g06 | -9.11 / -17.03 | +0.0912 | v3.2 | -10.40 / -18.21 | +0.0912 | v3.2 | -9.03 / -16.96 | +0.0912 | v3.2 |
| g07 | -9.17 / -16.52 | +0.0844 | v3.2 | -10.46 / -17.71 | +0.0844 | v3.2 | -9.08 / -16.44 | +0.0844 | v3.2 |
| g08 | +11.68 / +12.22 | +0.0048 | tie | +12.06 / +12.60 | +0.0048 | tie | +11.50 / +12.04 | +0.0048 | tie |
| g09 | +2.44 / +1.05 | -0.0136 | v3.1 | +2.24 / +0.86 | -0.0136 | v3.1 | +2.52 / +1.14 | -0.0136 | v3.1 |
| g10 | -1.76 / -1.21 | -0.0055 | v3.1 | -2.11 / -1.57 | -0.0055 | v3.1 | -1.68 / -1.14 | -0.0055 | v3.1 |
| g11 | +23.72 / +22.27 | -0.0118 | v3.1 | +24.52 / +23.06 | -0.0118 | v3.1 | +21.72 / +20.29 | -0.0118 | v3.1 |
| g12 | -1.57 / -0.97 | -0.0060 | v3.1 | -1.94 / -1.34 | -0.0060 | v3.1 | -1.53 / -0.93 | -0.0060 | v3.1 |
| g01t | -1.48 / -7.26 | +0.0604 | v3.2 | -0.40 / -6.25 | +0.0604 | v3.2 | -1.37 / -7.16 | +0.0604 | v3.2 |
| g02t | -1.40 / -6.43 | +0.0524 | v3.2 | -0.33 / -5.41 | +0.0524 | v3.2 | -1.32 / -6.36 | +0.0524 | v3.2 |
| g03t | -1.14 / -5.18 | +0.0418 | v3.2 | -0.05 / -4.15 | +0.0418 | v3.2 | -1.04 / -5.10 | +0.0418 | v3.2 |
| g04t | +1.93 / +2.23 | +0.0029 | tie | +2.79 / +3.09 | +0.0029 | tie | +2.06 / +2.36 | +0.0029 | tie |
| g05t | -1.30 / -0.23 | -0.0107 | v3.1 | -0.21 / +0.86 | +0.0064 | v3.2 | -1.20 / -0.14 | -0.0107 | v3.1 |
| g06t | -1.49 / -9.92 | +0.0894 | v3.2 | -1.65 / -10.07 | +0.0894 | v3.2 | -1.42 / -9.85 | +0.0894 | v3.2 |
| g08t | +4.27 / +4.78 | +0.0048 | tie | +5.41 / +5.92 | +0.0048 | tie | +4.36 / +4.87 | +0.0048 | tie |
| g09t | +5.22 / +3.85 | -0.0132 | v3.1 | +5.17 / +3.79 | -0.0132 | v3.1 | +5.31 / +3.93 | -0.0132 | v3.1 |
| g10t | -0.17 / +0.36 | +0.0019 | tie | +0.06 / +0.60 | +0.0054 | v3.2 | -0.08 / +0.46 | +0.0038 | tie |
| g11t | +5.79 / +4.47 | -0.0125 | v3.1 | +6.95 / +5.62 | -0.0125 | v3.1 | +5.79 / +4.47 | -0.0125 | v3.1 |
| g12t | +0.26 / +0.86 | +0.0059 | v3.2 | +0.37 / +0.97 | +0.0059 | v3.2 | +0.34 / +0.94 | +0.0059 | v3.2 |
| y01a | -6.40 / -4.88 | -0.0161 | v3.1 | +14.85 / +16.71 | +0.0161 | v3.2 | -6.31 / -4.79 | -0.0161 | v3.1 |
| y01b | +2.44 / +4.10 | +0.0161 | v3.2 | -0.52 / +1.09 | +0.0057 | v3.2 | +2.53 / +4.19 | +0.0161 | v3.2 |
| y02a | +2.78 / +4.06 | +0.0124 | v3.2 | +3.91 / +5.21 | +0.0124 | v3.2 | +2.87 / +4.16 | +0.0124 | v3.2 |
| y02b | -1.47 / -0.25 | -0.0124 | v3.1 | -0.39 / +0.85 | +0.0046 | tie | -1.39 / -0.16 | -0.0124 | v3.1 |
| y03b | -1.47 / -0.24 | -0.0124 | v3.1 | -0.39 / +0.86 | +0.0046 | tie | -1.39 / -0.16 | -0.0124 | v3.1 |
| y04a | +2.79 / +4.07 | +0.0124 | v3.2 | +26.12 / +27.69 | +0.0124 | v3.2 | +2.90 / +4.18 | +0.0124 | v3.2 |
| y04b | -1.48 / -0.25 | -0.0124 | v3.1 | -0.39 / +0.85 | +0.0045 | tie | -1.39 / -0.16 | -0.0124 | v3.1 |
| y05a | +6.66 / +7.26 | +0.0056 | v3.2 | +30.87 / +31.60 | +0.0056 | v3.2 | +6.75 / +7.35 | +0.0056 | v3.2 |
| y05b | +2.26 / +2.83 | +0.0056 | v3.2 | +3.38 / +3.96 | +0.0056 | v3.2 | +2.34 / +2.92 | +0.0056 | v3.2 |
| y06a | +2.78 / +4.06 | +0.0124 | v3.2 | +26.11 / +27.69 | +0.0124 | v3.2 | +2.87 / +4.16 | +0.0124 | v3.2 |
| y06b | -1.48 / -0.25 | -0.0124 | v3.1 | -0.39 / +0.85 | +0.0045 | tie | -1.39 / -0.16 | -0.0124 | v3.1 |
| y07a | +4.16 / +5.37 | +0.0116 | v3.2 | +5.30 / +6.53 | +0.0116 | v3.2 | +4.32 / +5.54 | +0.0116 | v3.2 |
| y07b | +6.40 / +7.64 | +0.0116 | v3.2 | +7.57 / +8.83 | +0.0116 | v3.2 | +6.48 / +7.72 | +0.0116 | v3.2 |
| y08a | +8.09 / +8.61 | +0.0048 | tie | +9.28 / +9.80 | +0.0048 | tie | +8.17 / +8.70 | +0.0048 | tie |
| y08b | +10.74 / +11.28 | +0.0048 | tie | +11.96 / +12.50 | +0.0048 | tie | +10.71 / +11.24 | +0.0048 | tie |
| f01 | -9.01 / -16.19 | +0.0823 | v3.2 | -8.02 / -15.28 | +0.0823 | v3.2 | -8.90 / -16.10 | +0.0823 | v3.2 |
| f02 | -8.64 / -15.85 | +0.0823 | v3.2 | -7.66 / -14.95 | +0.0823 | v3.2 | -8.59 / -15.81 | +0.0823 | v3.2 |
| f03 | -0.94 / -0.73 | -0.0022 | tie | -0.99 / -0.78 | -0.0022 | tie | -0.85 / -0.63 | -0.0022 | tie |
| f04 | +1.49 / +1.98 | +0.0048 | tie | +2.61 / +3.10 | +0.0048 | tie | +1.47 / +1.95 | +0.0048 | tie |
| f05 | -8.40 / -15.64 | +0.0823 | v3.2 | -7.57 / -14.87 | +0.0823 | v3.2 | -8.35 / -15.58 | +0.0823 | v3.2 |
| f06 | -7.53 / -14.83 | +0.0823 | v3.2 | -6.76 / -14.13 | +0.0823 | v3.2 | -7.43 / -14.74 | +0.0823 | v3.2 |
| f07 | -8.26 / -15.51 | +0.0823 | v3.2 | -7.34 / -14.66 | +0.0823 | v3.2 | -8.17 / -15.42 | +0.0823 | v3.2 |
| f08 | -4.85 / -10.88 | +0.0655 | v3.2 | -3.82 / -9.92 | +0.0655 | v3.2 | -4.77 / -10.80 | +0.0655 | v3.2 |
| f09 | -2.58 / -10.22 | +0.0816 | v3.2 | -1.53 / -9.25 | +0.0816 | v3.2 | -2.49 / -10.14 | +0.0816 | v3.2 |
| f10 | -9.54 / -16.03 | +0.0744 | v3.2 | -8.58 / -15.13 | +0.0744 | v3.2 | -9.41 / -15.90 | +0.0744 | v3.2 |
| f11 | -9.08 / -15.60 | +0.0744 | v3.2 | -8.30 / -14.87 | +0.0744 | v3.2 | -8.96 / -15.49 | +0.0744 | v3.2 |
| f12 | -8.26 / -14.84 | +0.0744 | v3.2 | -7.62 / -14.24 | +0.0744 | v3.2 | -8.15 / -14.74 | +0.0744 | v3.2 |
| f13 | -3.05 / -2.62 | -0.0044 | tie | -1.99 / -1.56 | -0.0044 | tie | -2.94 / -2.51 | -0.0044 | tie |
| f14 | -3.16 / -2.83 | -0.0035 | tie | -2.11 / -1.77 | -0.0035 | tie | -3.08 / -2.75 | -0.0035 | tie |

- **H6** (wall cycles): 28 / 13 / 11, p 0.0275: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **H7** (the counter's mean): 31 / 7 / 14, p 1.16e-04: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **H8** (seconds): 28 / 13 / 11, p 0.0275: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).

**H9 and H10: MM1-v3.2 (first) against MM1-v3.1 (second), J over idle per point (tie 0.01 in ln; 0.1 W at a watts point)**

| point | H9: errors v3.2 / v3.1 | d | reads | H10: errors v3.2 / v3.1 | d | reads |
|---|---|---|---|---|---|---|
| g01 | -5.53 / +14.39 | +0.0776 | v3.2 | -5.91 / +13.52 | +0.0658 | v3.2 |
| g02 | -5.33 / +14.87 | +0.0839 | v3.2 | -5.72 / +14.03 | +0.0724 | v3.2 |
| g03 | -10.07 / +10.16 | -0.0094 | tie | -10.45 / +9.40 | -0.0205 | v3.1 |
| g04 | +23.83 / +51.63 | +0.2026 | v3.2 | +24.55 / +52.68 | +0.2036 | v3.2 |
| g05 | -7.32 / +13.54 | +0.0509 | v3.2 | -7.71 / +13.04 | +0.0424 | v3.2 |
| g06 | -3.61 / +13.55 | +0.0904 | v3.2 | -3.88 / +12.71 | +0.0801 | v3.2 |
| g07 | -3.47 / +14.01 | +0.0958 | v3.2 | -3.73 / +13.21 | +0.0860 | v3.2 |
| g08 | +30.77 / +55.23 | +0.1715 | v3.2 | +31.36 / +56.07 | +0.1724 | v3.2 |
| g09 | -8.32 / +35.16 | +0.2145 | v3.2 | -8.15 / +35.36 | +0.2177 | v3.2 |
| g10 | -7.57 / +37.19 | +0.2374 | v3.2 | -7.57 / +37.20 | +0.2375 | v3.2 |
| g11 | +14.52 / +48.21 | +0.2579 | v3.2 | +13.95 / +47.70 | +0.2595 | v3.2 |
| g12 | -6.62 / +38.52 | +0.2574 | v3.2 | -6.64 / +38.50 | +0.2570 | v3.2 |
| g01t | +0.41 / -1.29 | +0.0089 | tie | +0.44 / -1.55 | +0.0112 | v3.2 |
| g02t | -0.69 / -2.19 | +0.0152 | v3.2 | -0.69 / -2.43 | +0.0177 | v3.2 |
| g03t | -2.25 / -3.59 | +0.0138 | v3.2 | -2.22 / -3.76 | +0.0159 | v3.2 |
| g04t | -1.17 / -1.33 | +0.0016 | tie | -0.93 / -1.08 | +0.0015 | tie |
| g05t | -2.67 / -3.16 | +0.0051 | tie | -2.64 / -3.08 | +0.0045 | tie |
| g06t | -1.38 / -3.29 | +0.0196 | v3.2 | -1.37 / -3.69 | +0.0238 | v3.2 |
| g08t | -2.47 / -2.48 | +0.0001 | tie | -2.12 / -2.13 | +0.0000 | tie |
| g09t | -0.36 / -1.10 | +0.0074 | tie | +0.03 / -0.81 | +0.0078 | tie |
| g10t | -2.01 / -2.55 | +0.0055 | tie | -1.93 / -2.44 | +0.0052 | tie |
| g11t | -3.56 / -4.48 | +0.0096 | tie | -3.21 / -4.23 | +0.0106 | v3.2 |
| g12t | -1.60 / -2.10 | +0.0051 | tie | -1.50 / -1.97 | +0.0048 | tie |
| y01a | -0.46 / -0.47 W | +0.013 W | tie | -0.31 / -0.36 W | +0.049 W | tie |
| y01b | -0.07 / -0.08 W | +0.011 W | tie | -0.12 / -0.17 W | +0.049 W | tie |
| y02a | +0.50 / +0.50 W | +0.002 W | tie | +0.45 / +0.43 W | -0.023 W | tie |
| y02b | +0.18 / +0.18 W | +0.001 W | tie | +0.21 / +0.19 W | -0.023 W | tie |
| y03b | +0.18 / +0.18 W | +0.001 W | tie | +0.21 / +0.19 W | -0.023 W | tie |
| y04a | +0.51 / +0.51 W | +0.002 W | tie | +0.46 / +0.43 W | -0.023 W | tie |
| y04b | +0.18 / +0.18 W | +0.001 W | tie | +0.21 / +0.19 W | -0.023 W | tie |
| y05a | +0.53 / +0.53 W | -0.000 W | tie | +0.41 / +0.39 W | -0.012 W | tie |
| y05b | +0.24 / +0.24 W | -0.001 W | tie | +0.20 / +0.19 W | -0.012 W | tie |
| y06a | +0.55 / +0.55 W | +0.002 W | tie | +0.50 / +0.47 W | -0.023 W | tie |
| y06b | +0.19 / +0.19 W | +0.001 W | tie | +0.22 / +0.19 W | -0.023 W | tie |
| y07a | -0.07 / +0.15 | +0.0008 | tie | +0.42 / +0.72 | +0.0030 | tie |
| y07b | -0.25 / -0.02 | -0.0023 | tie | +0.34 / +0.64 | +0.0030 | tie |
| y08a | +0.23 / +0.35 | +0.0012 | tie | +0.95 / +1.07 | +0.0013 | tie |
| y08b | +0.50 / +0.64 | +0.0013 | tie | +1.33 / +1.46 | +0.0013 | tie |
| f01 | -3.61 / -5.38 | +0.0185 | v3.2 | -3.97 / -6.10 | +0.0223 | v3.2 |
| f02 | -3.48 / -5.25 | +0.0185 | v3.2 | -3.89 / -6.01 | +0.0223 | v3.2 |
| f03 | -1.57 / -2.17 | +0.0062 | tie | -1.52 / -2.11 | +0.0061 | tie |
| f04 | -3.77 / -3.93 | +0.0017 | tie | -3.70 / -3.85 | +0.0015 | tie |
| f05 | -3.69 / -5.19 | +0.0156 | v3.2 | -4.10 / -5.97 | +0.0197 | v3.2 |
| f06 | -3.61 / -5.10 | +0.0156 | v3.2 | -3.92 / -5.79 | +0.0197 | v3.2 |
| f07 | -4.45 / -5.93 | +0.0156 | v3.2 | -4.80 / -6.66 | +0.0197 | v3.2 |
| f08 | -3.78 / -5.06 | +0.0134 | v3.2 | -3.95 / -5.53 | +0.0166 | v3.2 |
| f09 | -3.13 / -4.69 | +0.0162 | v3.2 | -3.17 / -5.11 | +0.0203 | v3.2 |
| f10 | -7.04 / -9.03 | +0.0216 | v3.2 | -7.86 / -10.43 | +0.0282 | v3.2 |
| f11 | -6.29 / -8.29 | +0.0216 | v3.2 | -7.09 / -9.67 | +0.0282 | v3.2 |
| f12 | -5.70 / -7.71 | +0.0215 | v3.2 | -6.43 / -9.04 | +0.0282 | v3.2 |
| f13 | -4.68 / -4.33 | -0.0037 | tie | -4.87 / -4.46 | -0.0043 | tie |
| f14 | -5.47 / -5.14 | -0.0035 | tie | -5.70 / -5.32 | -0.0040 | tie |

- **H9** (J over idle given t): 24 / 0 / 28, p 1.19e-07: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **H10** (J over idle, t forecast): 26 / 1 / 25, p 4.17e-07: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).

**HG1-HG4: MM1-v3.2 (first) against 'MM1-v3.2 without its gemmLnc term' (HG1, HG2) and against 'v3.1 + gemmLnc term' (HG3, HG4), family G, J over idle (tie 0.01 in ln)**

| point | HG1: errors v3.2 / no lnc | d | reads | HG2: errors v3.2 / no lnc | d | reads | HG3: errors v3.2 / v3.1+lnc | d | reads | HG4: errors v3.2 / v3.1+lnc | d | reads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | -5.53 / +16.42 | +0.0952 | v3.2 | -5.91 / +15.82 | +0.0859 | v3.2 | -5.53 / -8.12 | +0.0278 | v3.2 | -5.91 / -8.67 | +0.0298 | v3.2 |
| g02 | -5.33 / +16.70 | +0.0997 | v3.2 | -5.72 / +16.08 | +0.0902 | v3.2 | -5.33 / -7.79 | +0.0264 | v3.2 | -5.72 / -8.32 | +0.0280 | v3.2 |
| g03 | -10.07 / +11.76 | +0.0050 | tie | -10.45 / +11.16 | -0.0045 | tie | -10.07 / -12.47 | +0.0270 | v3.2 | -10.45 / -12.93 | +0.0281 | v3.2 |
| g04 | +23.83 / +51.81 | +0.2037 | v3.2 | +24.55 / +52.92 | +0.2052 | v3.2 | +23.83 / +21.91 | -0.0156 | v3.1+lnc | +24.55 / +22.57 | -0.0160 | v3.1+lnc |
| g05 | -7.32 / +14.17 | +0.0565 | v3.2 | -7.71 / +13.56 | +0.0470 | v3.2 | -7.32 / -8.99 | +0.0181 | v3.2 | -7.71 / -9.29 | +0.0173 | v3.2 |
| g06 | -3.61 / +15.85 | +0.1104 | v3.2 | -3.88 / +15.44 | +0.1040 | v3.2 | -3.61 / -5.97 | +0.0248 | v3.2 | -3.88 / -6.53 | +0.0280 | v3.2 |
| g07 | -3.47 / +16.20 | +0.1149 | v3.2 | -3.73 / +15.79 | +0.1086 | v3.2 | -3.47 / -5.78 | +0.0243 | v3.2 | -3.73 / -6.31 | +0.0272 | v3.2 |
| g08 | +30.77 / +55.21 | +0.1713 | v3.2 | +31.36 / +56.09 | +0.1725 | v3.2 | +30.77 / +29.78 | -0.0076 | tie | +31.36 / +30.33 | -0.0079 | tie |
| g09 | -8.32 / +36.19 | +0.2221 | v3.2 | -8.15 / +36.50 | +0.2262 | v3.2 | -8.32 / -13.22 | +0.0549 | v3.2 | -8.15 / -13.11 | +0.0555 | v3.2 |
| g10 | -7.57 / +37.97 | +0.2431 | v3.2 | -7.57 / +37.92 | +0.2428 | v3.2 | -7.57 / -12.44 | +0.0541 | v3.2 | -7.57 / -12.42 | +0.0539 | v3.2 |
| g11 | +14.52 / +49.51 | +0.2666 | v3.2 | +13.95 / +49.28 | +0.2701 | v3.2 | +14.52 / +10.60 | -0.0349 | v3.1+lnc | +13.95 / +9.86 | -0.0365 | v3.1+lnc |
| g12 | -6.62 / +39.25 | +0.2626 | v3.2 | -6.64 / +39.17 | +0.2619 | v3.2 | -6.62 / -11.51 | +0.0538 | v3.2 | -6.64 / -11.50 | +0.0535 | v3.2 |

- **HG1** (J over idle given t): 11 / 0 / 1, p 9.77e-04: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **HG2** (J over idle, t forecast): 11 / 0 / 1, p 9.77e-04: **MM1-v3.2 BETTER** (printed: MM1-v3.2 BETTER (labelled: R0 FAIL)).
- **HG3** (J over idle given t): 9 / 2 / 1, p 0.0654: **NOT DECIDED** (printed: NOT DECIDED (labelled: R0 FAIL)).
- **HG4** (J over idle, t forecast): 9 / 2 / 1, p 0.0654: **NOT DECIDED** (printed: NOT DECIDED (labelled: R0 FAIL)).

**HY1 and HY2: MM1-v3.2 (first) against 'MM1-v3.2 without its layout term' (HY1: the same model, D3) and against 'v3.1 + contention' (HY2), family Y, wall cycles (tie 0.005 in ln)**

| point | HY1: errors v3.2 / no layout | d | reads | HY2: errors v3.2 / +contention | d | reads |
|---|---|---|---|---|---|---|
| y01a | -6.40 / -6.40 | +0.0000 | tie | -6.40 / -5.61 | -0.0083 | +contention |
| y01b | +2.44 / +2.44 | +0.0000 | tie | +2.44 / +4.74 | +0.0222 | v3.2 |
| y02a | +2.78 / +2.78 | +0.0000 | tie | +2.78 / +6.22 | +0.0329 | v3.2 |
| y02b | -1.47 / -1.47 | +0.0000 | tie | -1.47 / +0.25 | -0.0124 | +contention |
| y03b | -1.47 / -1.47 | +0.0000 | tie | -1.47 / +0.25 | -0.0123 | +contention |
| y04a | +2.79 / +2.79 | +0.0000 | tie | +2.79 / +6.23 | +0.0329 | v3.2 |
| y04b | -1.48 / -1.48 | +0.0000 | tie | -1.48 / +0.30 | -0.0119 | +contention |
| y05a | +6.66 / +6.66 | +0.0000 | tie | +6.66 / +9.50 | +0.0263 | v3.2 |
| y05b | +2.26 / +2.26 | +0.0000 | tie | +2.26 / +3.80 | +0.0150 | v3.2 |
| y06a | +2.78 / +2.78 | +0.0000 | tie | +2.78 / +6.22 | +0.0330 | v3.2 |
| y06b | -1.48 / -1.48 | +0.0000 | tie | -1.48 / +0.36 | -0.0113 | +contention |
| y07a | +4.16 / +4.16 | +0.0000 | tie | +4.16 / +6.11 | +0.0186 | v3.2 |
| y07b | +6.40 / +6.40 | +0.0000 | tie | +6.40 / +8.39 | +0.0186 | v3.2 |
| y08a | +8.09 / +8.09 | +0.0000 | tie | +8.09 / +9.37 | +0.0118 | v3.2 |
| y08b | +10.74 / +10.74 | +0.0000 | tie | +10.74 / +12.05 | +0.0118 | v3.2 |

- **HY1** (wall cycles): 0 / 0 / 15: **TOO FEW** (printed: TOO FEW (labelled: R0 FAIL)).
- **HY2** (wall cycles): 10 / 5 / 0, p 0.3018: **NOT DECIDED** (printed: NOT DECIDED (labelled: R0 FAIL)).

## 6. The pair rule, pair by pair (P1, registered; BLIND)

ln(wall a / wall b) of each complete pair's two point means; a pair is separated when |measured| > 0.0077. MM1-v3.2 predicts 0 at every pair (its registered |ln(T_a / T_b)| is at most 1.0e-09 at each). Beside it, each frozen candidate's predicted ln(T_a / T_b) (`rules-e218.json` > `pair_rule` > `pairs`) and whether it orders the separated pair right (+ right, - wrong; a 0 forecast orders none): REPORTED, E216's form.

| pair | GEMM | masks a / b | measured ln(a / b) | separated | MM1-v3.2 | v3.1 + contention | v3.1 with T7 | G1 | G1+N1 | fresh24 | N1+N2 | N3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| y01 | `gemmL4x2x8` | 0xf000 / 0x1010101 | -0.0902 | yes | +0.0000 | +0.0138 - | -0.1972 + | -0.0257 + | -0.0520 + | +0.0112 - | +0.0000 - | +0.0000 - |
| y02 | `gemmL1x16x24` | 0xf / 0x3030 | +0.0423 | yes | +0.0000 | -0.0156 - | +0.0420 + | +0.0150 + | +0.0305 + | -0.0388 - | +0.0000 - | +0.0000 - |
| y04 | `gemmL2x16x24` | 0xf / 0x3030 | +0.0424 | yes | +0.0000 | -0.0150 - | +0.0369 + | +0.0150 + | +0.0305 + | -0.0388 - | +0.0000 - | +0.0000 - |
| y05 | `gemmL2x2x24` | 0xf / 0x3030 | +0.0421 | yes | +0.0000 | -0.0113 - | +0.1218 + | +0.0150 + | +0.0305 + | -0.0388 - | +0.0000 - | +0.0000 - |
| y06 | `gemmL2x8x24` | 0xf / 0x3030 | +0.0423 | yes | +0.0000 | -0.0145 - | +0.0460 + | +0.0150 + | +0.0305 + | -0.0388 - | +0.0000 - | +0.0000 - |
| y07 | `gemmL4x16x24` | 0x55555555 / 0xffff0000 | -0.0213 | yes | +0.0000 | +0.0000 - | -0.0155 + | +0.0000 - | +0.0000 - | +0.0000 - | +0.0000 - | +0.0000 - |
| y08 | `gemmL4x2x24` | 0x55555555 / 0xffff0000 | -0.0242 | yes | +0.0000 | +0.0000 - | -0.0313 + | +0.0000 - | +0.0000 - | +0.0000 - | +0.0000 - | +0.0000 - |
| y03 | `gemmL1x4x24` | (y03a dropped, D1) / 0x3030 | - | incomplete: y03b is scored alone, outside the pair rule | - | - | - | - | - | - | - | - |

**P1 reads FAIL** (printed: FAIL (labelled: R0 FAIL)): 7 of 7 complete pairs separated, where PASS allows at most one. The measured differences run 0.021-0.090 in ln: y01 -0.090; y02, y04, y05 and y06 (0xf against 0x3030 at KB-24 shapes) +0.0421 to +0.0424; the controls y07 -0.021 and y08 -0.024. **The day's own within-point repeat** (REPORTED, beside the fixed 0.0077): each Y point's pass-2 run against its pass-1 run, n 15, rms ln(pass 2 / pass 1) **0.00048**, largest |ln| 0.00134 (over all 52 points 0.00202, largest 0.01206, at G). So every separation sits 44 to 188 times above the day's Y repeat.

**Each frozen candidate in E216's form (REPORTED, never a verdict):** v3.1 + contention FAIL (0 of 7 separated pairs ordered right); v3.1 with T7 PASS (7 of 7 separated pairs ordered right); G1 FAIL (5 of 7 separated pairs ordered right); G1+N1 FAIL (5 of 7 separated pairs ordered right); fresh24 FAIL (0 of 7 separated pairs ordered right); N1+N2 FAIL (0 of 7 separated pairs ordered right); N3 FAIL (0 of 7 separated pairs ordered right). Only 'v3.1 with T7' orders every separated pair, the controls y07 and y08 among them; G1 and G1+N1 order five of seven. The count-only controls (N1+N2, N3) predict 0, so they order none; 'v3.1 + contention' and fresh24 order none either.

## 7. Each model's error by family (REPORTED; desk arithmetic; equal to verify-e218d's independent table)

rms of ln(measured / forecast) in %, with the bias (the mean) in brackets, from each point's measured mean and each model's frozen forecast (given t: the model's frozen A + B / t_op at the point's measured op time, times the measured seconds). This is verify-e218d's form; its 825 cells (15 models, 5 groups, 11 quantities) equal this lane's to the last printed digit, and the three quantities the scorer reports (`model_stats_REPORTED`: wall cycles, J over idle with t forecast at 3 W and above, W at the watts points) equal it in all 225 cells. n is G 12, Gt 11, Y 15, F 14 and all 52 for time; the joules over idle count the points at 3 W and above (G 12, Gt 11, Y 4, F 14, all 41), and Y's 11 watts points are read in W in their own table. 'v3.1 with T7', 'v3.1 + both terms' and 'MM1-v3 refitted' are REPORTED columns of MM1-v3.2's land; verify-lay's five controls forecast time only.

**wall cycles an op (T1's quantity)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 11.49 (-2.27) | 2.83 (+0.91) | 4.81 (+2.33) | 7.09 (-6.09) | **7.24 (-1.30)** |
| MM1-v3.1 | 14.39 (-4.99) | 5.22 (-1.27) | 5.23 (+3.42) | 13.52 (-11.56) | **10.52 (-3.55)** |
| MM1-v3 | 13.57 (-4.20) | 4.44 (-0.61) | 5.47 (+3.69) | 12.45 (-10.56) | **9.85 (-2.88)** |
| MM1-v2 | 13.80 (-3.91) | 5.64 (+0.76) | 14.62 (+13.73) | 11.67 (-9.07) | **12.21 (+0.78)** |
| MM1-v3.2 without its gemmLnc term | 11.49 (-2.27) | 2.83 (+0.91) | 4.81 (+2.33) | 7.09 (-6.09) | **7.24 (-1.30)** |
| v3.1 + gemmLnc term | 14.39 (-4.99) | 5.22 (-1.27) | 5.23 (+3.42) | 13.52 (-11.56) | **10.52 (-3.55)** |
| v3.1 + contention | 14.39 (-4.99) | 5.22 (-1.27) | 6.17 (+4.35) | 13.52 (-11.56) | **10.66 (-3.28)** |
| v3.1 + both terms (REPORTED) | 14.39 (-4.99) | 5.22 (-1.27) | 6.17 (+4.35) | 13.52 (-11.56) | **10.66 (-3.28)** |
| v3.1 with T7 (REPORTED) | 13.62 (-4.06) | 4.76 (-0.52) | 7.65 (-3.62) | 11.36 (-9.54) | **9.96 (-4.66)** |
| MM1-v3 refitted (REPORTED) | 11.49 (-2.27) | 2.83 (+0.91) | 4.81 (+2.33) | 7.09 (-6.09) | **7.24 (-1.30)** |
| control N3 | 14.39 (-4.99) | 5.22 (-1.27) | 5.04 (+2.88) | 13.52 (-11.56) | **10.49 (-3.70)** |
| control N1+N2 | 14.39 (-4.99) | 5.22 (-1.27) | 5.82 (+3.28) | 13.52 (-11.56) | **10.61 (-3.59)** |
| control G1 | 14.39 (-4.99) | 5.22 (-1.27) | 5.02 (+3.52) | 13.52 (-11.56) | **10.49 (-3.52)** |
| control G1+N1 | 14.39 (-4.99) | 5.22 (-1.27) | 6.13 (+5.32) | 13.52 (-11.56) | **10.66 (-3.00)** |
| control fresh24 | 14.39 (-4.99) | 5.22 (-1.27) | 7.34 (+5.54) | 13.52 (-11.56) | **10.88 (-2.94)** |

**the counter's mean (T2's)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 11.47 (-2.12) | 3.15 (+1.59) | 12.40 (+8.32) | 6.29 (-5.17) | **9.35 (+0.86)** |
| MM1-v3.1 | 14.43 (-4.85) | 5.14 (-0.59) | 13.09 (+9.41) | 12.71 (-10.65) | **12.11 (-1.40)** |
| MM1-v3 | 13.61 (-4.05) | 4.47 (+0.07) | 13.31 (+9.68) | 11.65 (-9.64) | **11.60 (-0.73)** |
| MM1-v2 | 13.79 (-3.77) | 5.83 (+1.44) | 22.11 (+19.72) | 10.96 (-8.15) | **14.98 (+2.93)** |
| MM1-v3.2 without its gemmLnc term | 11.47 (-2.12) | 3.15 (+1.59) | 12.40 (+8.32) | 6.29 (-5.17) | **9.35 (+0.86)** |
| v3.1 + gemmLnc term | 14.43 (-4.85) | 5.14 (-0.59) | 13.09 (+9.41) | 12.71 (-10.65) | **12.11 (-1.40)** |
| v3.1 + contention | 14.43 (-4.85) | 5.14 (-0.59) | 14.06 (+10.34) | 12.71 (-10.65) | **12.42 (-1.13)** |
| v3.1 + both terms (REPORTED) | 14.43 (-4.85) | 5.14 (-0.59) | 14.06 (+10.34) | 12.71 (-10.65) | **12.42 (-1.13)** |
| v3.1 with T7 (REPORTED) | 13.63 (-3.92) | 4.73 (+0.16) | 11.22 (+2.37) | 10.57 (-8.62) | **10.67 (-2.51)** |
| MM1-v3 refitted (REPORTED) | 11.47 (-2.12) | 3.15 (+1.59) | 12.40 (+8.32) | 6.29 (-5.17) | **9.35 (+0.86)** |

**seconds a GEMM (T3's)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 11.18 (-2.36) | 2.85 (+1.00) | 4.84 (+2.42) | 7.00 (-6.00) | **7.11 (-1.25)** |
| MM1-v3.1 | 14.14 (-5.09) | 5.19 (-1.18) | 5.27 (+3.50) | 13.43 (-11.47) | **10.41 (-3.50)** |
| MM1-v3 | 13.30 (-4.29) | 4.42 (-0.53) | 5.52 (+3.77) | 12.36 (-10.47) | **9.74 (-2.83)** |
| MM1-v2 | 13.51 (-4.01) | 5.64 (+0.84) | 14.69 (+13.82) | 11.59 (-8.98) | **12.13 (+0.82)** |
| MM1-v3.2 without its gemmLnc term | 11.18 (-2.36) | 2.85 (+1.00) | 4.84 (+2.42) | 7.00 (-6.00) | **7.11 (-1.25)** |
| v3.1 + gemmLnc term | 14.14 (-5.09) | 5.19 (-1.18) | 5.27 (+3.50) | 13.43 (-11.47) | **10.41 (-3.50)** |
| v3.1 + contention | 14.14 (-5.09) | 5.19 (-1.18) | 6.22 (+4.43) | 13.43 (-11.47) | **10.56 (-3.23)** |
| v3.1 + both terms (REPORTED) | 14.14 (-5.09) | 5.19 (-1.18) | 6.22 (+4.43) | 13.43 (-11.47) | **10.56 (-3.23)** |
| v3.1 with T7 (REPORTED) | 13.35 (-4.15) | 4.74 (-0.44) | 7.60 (-3.54) | 11.27 (-9.45) | **9.84 (-4.62)** |
| MM1-v3 refitted (REPORTED) | 11.18 (-2.36) | 2.85 (+1.00) | 4.84 (+2.42) | 7.00 (-6.00) | **7.11 (-1.25)** |
| control N3 | 14.14 (-5.09) | 5.19 (-1.18) | 5.08 (+2.96) | 13.43 (-11.47) | **10.38 (-3.66)** |
| control N1+N2 | 14.14 (-5.09) | 5.19 (-1.18) | 5.85 (+3.37) | 13.43 (-11.47) | **10.50 (-3.54)** |
| control G1 | 14.14 (-5.09) | 5.19 (-1.18) | 5.07 (+3.60) | 13.43 (-11.47) | **10.38 (-3.47)** |
| control G1+N1 | 14.14 (-5.09) | 5.19 (-1.18) | 6.19 (+5.41) | 13.43 (-11.47) | **10.56 (-2.95)** |
| control fresh24 | 14.14 (-5.09) | 5.19 (-1.18) | 7.40 (+5.62) | 13.43 (-11.47) | **10.78 (-2.89)** |

**J over idle given t, points at 3 W and above (E1's)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 12.26 (+0.15) | 1.97 (-1.63) | 0.30 (+0.10) | 4.64 (-4.41) | **7.24 (-1.89)** |
| MM1-v3.1 | 27.61 (+24.57) | 2.75 (-2.54) | 0.37 (+0.28) | 5.98 (-5.69) | **15.40 (+4.59)** |
| MM1-v3 | 27.53 (+24.51) | 2.81 (-2.64) | 0.82 (+0.76) | 6.27 (-6.01) | **15.41 (+4.49)** |
| MM1-v2 | 26.95 (+24.23) | 3.44 (-2.98) | 1.15 (-1.15) | 3.99 (-3.85) | **14.87 (+4.86)** |
| MM1-v3.2 without its gemmLnc term | 28.27 (+25.57) | 1.97 (-1.63) | 0.30 (+0.10) | 4.64 (-4.41) | **15.57 (+5.55)** |
| v3.1 + gemmLnc term | 13.47 (-2.93) | 2.75 (-2.54) | 0.37 (+0.28) | 5.98 (-5.69) | **8.21 (-3.46)** |
| v3.1 + contention | 27.61 (+24.57) | 2.75 (-2.54) | 0.37 (+0.28) | 5.98 (-5.69) | **15.40 (+4.59)** |
| v3.1 + both terms (REPORTED) | 13.47 (-2.93) | 2.75 (-2.54) | 0.37 (+0.28) | 5.98 (-5.69) | **8.21 (-3.46)** |
| v3.1 with T7 (REPORTED) | 27.54 (+24.56) | 2.76 (-2.58) | 1.79 (+1.57) | 5.79 (-5.52) | **15.36 (+4.77)** |
| MM1-v3 refitted (REPORTED) | 27.68 (+24.89) | 2.54 (-2.31) | 0.38 (-0.26) | 4.99 (-4.82) | **15.32 (+5.00)** |

**J over idle with t forecast, points at 3 W and above (E2's)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 12.47 (+0.02) | 1.83 (-1.48) | 0.85 (+0.76) | 5.05 (-4.77) | **7.43 (-1.95)** |
| MM1-v3.1 | 27.59 (+24.31) | 2.73 (-2.51) | 1.02 (+0.97) | 6.78 (-6.37) | **15.51 (+4.36)** |
| MM1-v3 | 27.55 (+24.28) | 2.76 (-2.57) | 1.52 (+1.47) | 7.05 (-6.66) | **15.53 (+4.29)** |
| MM1-v2 | 27.04 (+23.93) | 3.38 (-2.81) | 0.62 (+0.57) | 5.03 (-4.80) | **15.02 (+4.66)** |
| MM1-v3.2 without its gemmLnc term | 28.31 (+25.44) | 1.83 (-1.48) | 0.85 (+0.76) | 5.05 (-4.77) | **15.63 (+5.50)** |
| v3.1 + gemmLnc term | 13.72 (-3.16) | 2.73 (-2.51) | 1.02 (+0.97) | 6.78 (-6.37) | **8.54 (-3.68)** |
| v3.1 + contention | 27.59 (+24.31) | 2.73 (-2.51) | 1.07 (+1.02) | 6.78 (-6.37) | **15.51 (+4.37)** |
| v3.1 + both terms (REPORTED) | 13.72 (-3.16) | 2.73 (-2.51) | 1.07 (+1.02) | 6.78 (-6.37) | **8.54 (-3.67)** |
| v3.1 with T7 (REPORTED) | 27.55 (+24.35) | 2.71 (-2.50) | 1.81 (+1.55) | 6.43 (-6.06) | **15.44 (+4.54)** |
| MM1-v3 refitted (REPORTED) | 27.75 (+24.76) | 2.39 (-2.16) | 0.58 (+0.42) | 5.44 (-5.21) | **15.40 (+4.93)** |

**J at rest given t (E3's)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 5.78 (-0.26) | 0.82 (-0.69) | 1.23 (+0.66) | 1.67 (-1.64) | **3.00 (-0.45)** |
| MM1-v3.1 | 12.28 (+11.20) | 1.18 (-1.09) | 1.23 (+0.67) | 2.22 (-2.16) | **6.07 (+1.97)** |
| MM1-v3 | 12.25 (+11.17) | 1.21 (-1.13) | 1.39 (+0.89) | 2.34 (-2.28) | **6.08 (+1.98)** |
| MM1-v2 | 12.06 (+11.09) | 1.44 (-1.26) | 1.43 (+0.83) | 1.55 (-1.49) | **5.94 (+2.13)** |
| MM1-v3.2 without its gemmLnc term | 12.60 (+11.66) | 0.82 (-0.69) | 1.23 (+0.66) | 1.67 (-1.64) | **6.16 (+2.30)** |
| v3.1 + gemmLnc term | 6.56 (-1.84) | 1.18 (-1.09) | 1.23 (+0.67) | 2.22 (-2.16) | **3.46 (-1.04)** |
| v3.1 + contention | 12.28 (+11.20) | 1.18 (-1.09) | 1.23 (+0.67) | 2.22 (-2.16) | **6.07 (+1.97)** |
| v3.1 + both terms (REPORTED) | 6.56 (-1.84) | 1.18 (-1.09) | 1.23 (+0.67) | 2.22 (-2.16) | **3.46 (-1.04)** |
| v3.1 with T7 (REPORTED) | 12.26 (+11.20) | 1.18 (-1.10) | 1.42 (+0.99) | 2.15 (-2.09) | **6.07 (+2.07)** |
| MM1-v3 refitted (REPORTED) | 12.34 (+11.36) | 1.07 (-0.98) | 1.22 (+0.62) | 1.83 (-1.80) | **6.06 (+2.11)** |

**J at rest with t forecast (E4's)**

| model | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| MM1-v3.2 | 11.03 (-1.18) | 1.59 (-0.00) | 4.74 (+2.61) | 6.05 (-5.45) | **6.71 (-0.99)** |
| MM1-v3.1 | 15.18 (+8.64) | 3.48 (-1.66) | 5.17 (+3.58) | 10.67 (-9.41) | **9.70 (+0.14)** |
| MM1-v3 | 15.15 (+9.07) | 2.97 (-1.31) | 5.55 (+4.03) | 10.09 (-8.90) | **9.54 (+0.58)** |
| MM1-v2 | 15.01 (+9.05) | 3.73 (-0.67) | 13.93 (+12.88) | 8.82 (-7.35) | **11.48 (+3.69)** |
| MM1-v3.2 without its gemmLnc term | 15.23 (+10.64) | 1.59 (-0.00) | 4.74 (+2.61) | 6.05 (-5.45) | **8.39 (+1.74)** |
| v3.1 + gemmLnc term | 12.82 (-4.14) | 3.48 (-1.66) | 5.17 (+3.58) | 10.67 (-9.41) | **8.88 (-2.81)** |
| v3.1 + contention | 15.18 (+8.64) | 3.48 (-1.66) | 6.14 (+4.40) | 10.67 (-9.41) | **9.86 (+0.38)** |
| v3.1 + both terms (REPORTED) | 12.82 (-4.14) | 3.48 (-1.66) | 6.14 (+4.40) | 10.67 (-9.41) | **9.06 (-2.57)** |
| v3.1 with T7 (REPORTED) | 15.22 (+9.18) | 3.12 (-1.23) | 5.87 (-2.28) | 9.17 (-8.04) | **9.39 (-0.96)** |
| MM1-v3 refitted (REPORTED) | 15.07 (+10.34) | 1.66 (-0.29) | 4.71 (+2.57) | 6.20 (-5.62) | **8.35 (+1.55)** |

**W over idle at Y's 11 watts points, in W (rms (bias) of W measured - W forecast; E1's and E2's readings there)**

| model | given t | t forecast |
|---|---|---|
| MM1-v3.2 | 0.369 (+0.230) | 0.323 (+0.220) |
| MM1-v3.1 | 0.371 (+0.228) | 0.313 (+0.194) |
| MM1-v3 | 0.417 (+0.295) | 0.354 (+0.256) |
| MM1-v2 | 0.427 (+0.319) | 0.195 (+0.055) |
| MM1-v3.2 without its gemmLnc term | 0.369 (+0.230) | 0.323 (+0.220) |
| v3.1 + gemmLnc term | 0.371 (+0.228) | 0.313 (+0.194) |
| v3.1 + contention | 0.371 (+0.228) | 0.289 (+0.174) |
| v3.1 + both terms (REPORTED) | 0.371 (+0.228) | 0.289 (+0.174) |
| v3.1 with T7 (REPORTED) | 0.421 (+0.309) | 0.571 (+0.378) |
| MM1-v3 refitted (REPORTED) | 0.368 (+0.225) | 0.322 (+0.215) |

**MM1-v3.2's registered cells by family** (rms (bias) of measured / forecast - 1 in %, the scorer's cells; E1 and E2 at the points at 3 W and above; desk arithmetic, REPORTED):

| rule | G | Gt | Y | F | **all** |
|---|---|---|---|---|---|
| T1 | 11.66 (-1.60), n 12 | 2.89 (+0.95), n 11 | 4.95 (+2.45), n 15 | 6.79 (-5.84), n 14 | **7.25 (-1.03), n 52** |
| T2 | 11.72 (-1.46), n 12 | 3.24 (+1.65), n 11 | 13.86 (+9.15), n 15 | 6.06 (-4.98), n 14 | **9.96 (+1.31), n 52** |
| T3 | 11.27 (-1.73), n 12 | 2.91 (+1.04), n 11 | 4.98 (+2.54), n 15 | 6.71 (-5.76), n 14 | **7.10 (-1.00), n 52** |
| E1 | 13.34 (+0.94), n 12 | 1.94 (-1.61), n 11 | 0.31 (+0.10), n 4 | 4.52 (-4.30), n 14 | **7.75 (-1.62), n 41** |
| E2 | 13.58 (+0.84), n 12 | 1.81 (-1.47), n 11 | 0.86 (+0.76), n 4 | 4.91 (-4.64), n 14 | **7.95 (-1.66), n 41** |
| E3 | 5.97 (-0.09), n 12 | 0.82 (-0.68), n 11 | 1.23 (+0.67), n 15 | 1.65 (-1.62), n 14 | **3.09 (-0.41), n 52** |
| E4 | 11.49 (-0.55), n 12 | 1.60 (+0.01), n 11 | 4.83 (+2.72), n 15 | 5.83 (-5.27), n 14 | **6.85 (-0.76), n 52** |

## 8. The frozen terms and controls (REPORTED; never verdicts)

- **The gemmLnc term.** MM1-v3.2 carries the term refitted (F3 on its own base); 'v3.1 + gemmLnc term' carries Q225's frozen F3 (`aaeaa495`) on MM1-v3.1. Against the model without it, the refitted term is the registered winner on family G: HG1 11 / 0 / 1 and HG2 11 / 0 / 1 (p 0.00098), J over idle given t rms at G 12.26% against 28.27%. Against the frozen term on MM1-v3.1, HG3 and HG4 read 9 / 2 / 1 (p 0.065): NOT DECIDED, with J over idle given t rms at G 12.26% against 13.47%. The gemmLnc excess at each complete G-Gt pair (measured W over idle G / Gt beside each model's ratio; and the wall cycles' ratio, measured beside MM1-v3.2's):

| G | twin | G's regime | measured W ratio | MM1-v3.2 | no lnc | MM1-v3.1 | v3.1+lnc | MM1-v3 | MM1-v2 | measured wall ratio | MM1-v3.2 wall ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | g01t | NB5-6 | 1.307 | 1.250 | 1.016 | 1.015 | 1.262 | 1.015 | 1.000 | 0.881 | 0.983 |
| g02 | g02t | NB5-6 | 1.329 | 1.251 | 1.016 | 1.015 | 1.263 | 1.015 | 1.000 | 0.878 | 0.982 |
| g03 | g03t | NB5-6 | 1.296 | 1.260 | 1.015 | 1.015 | 1.275 | 1.015 | 1.000 | 0.875 | 0.983 |
| g04 | g04t | NB5-6 | 1.410 | 1.240 | 1.010 | 1.010 | 1.258 | 1.010 | 1.000 | 1.095 | 0.988 |
| g05 | g05t | NB5-6 | 1.343 | 1.251 | 1.017 | 1.017 | 1.268 | 1.017 | 1.000 | 0.867 | 0.981 |
| g06 | g06t | NB12-15 | 1.291 | 1.223 | 1.018 | 1.016 | 1.226 | 1.017 | 1.000 | 0.904 | 0.980 |
| g08 | g08t | NB12-15 | 1.508 | 1.200 | 1.010 | 1.010 | 1.210 | 1.010 | 1.000 | 1.058 | 0.988 |
| g09 | g09t | NB1-3 | 1.413 | 1.499 | 1.008 | 1.008 | 1.570 | 1.008 | 1.000 | 0.964 | 0.990 |
| g10 | g10t | NB1-3 | 1.440 | 1.503 | 1.007 | 1.007 | 1.578 | 1.007 | 1.000 | 0.975 | 0.991 |
| g11 | g11t | NB1-3 | 1.356 | 1.325 | 1.012 | 1.012 | 1.361 | 1.012 | 1.000 | 1.154 | 0.987 |
| g12 | g12t | NB1-3 | 1.450 | 1.502 | 1.007 | 1.007 | 1.577 | 1.007 | 1.000 | 0.973 | 0.991 |

  The card's gemmLnc excess reads 1.29-1.51 in W over idle; MM1-v3.2 prices 1.20-1.50 and the frozen term on MM1-v3.1 1.21-1.58, while the models without a term price 1.00-1.02. g07 has no twin (D1).

- **The layout term and verify-lay's controls.** MM1-v3.2 entered no layout term, so HY1 ties at every case (0 / 0 / 15, TOO FEW, as D3 registered). HY2 (MM1-v3.2 against 'v3.1 + contention', Q225's frozen F1 `595fcb59`) reads 10 / 5 / 0 (p 0.30): NOT DECIDED. On family Y's wall cycles (section 7): MM1-v3.2 4.81%, 'v3.1 + contention' 6.17%, 'v3.1 with T7' 7.65%, and the controls N3 5.04%, N1+N2 5.82%, G1 5.02%, G1+N1 6.13%, fresh24 7.34%. The pair rule's orderings are in section 6. P1 FAIL says the card shows a placement effect at equal shire count that MM1-v3.2 does not price. Of the frozen candidates only 'v3.1 with T7' orders all 7 separated pairs, yet its family-Y wall error is 7.65%, larger than every other time model's here but MM1-v2's (14.62%), against MM1-v3.2's 4.81%.

- **Every other model's cells at MM1-v3.2's bands** (the scorer's `others_at_v32_bands_REPORTED`, made again by its `cells_for()`; points in band of 52, with the verdict the rule would read; REPORTED, never verdicts):

| model | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.2 (the registered rules, section 3) | 45 FAIL | 47 PASS | 45 FAIL | 48 PASS | 49 PASS | 46 FAIL | 47 PASS |
| MM1-v3.1 | 34 FAIL | 34 FAIL | 34 FAIL | 40 FAIL | 41 FAIL | 40 FAIL | 38 FAIL |
| MM1-v3 | 34 FAIL | 41 FAIL | 34 FAIL | 38 FAIL | 41 FAIL | 40 FAIL | 38 FAIL |
| MM1-v2 | 21 FAIL | 32 FAIL | 21 FAIL | 37 FAIL | 41 FAIL | 40 FAIL | 29 FAIL |
| MM1-v3.2 without its gemmLnc term | 45 FAIL | 47 PASS | 45 FAIL | 40 FAIL | 41 FAIL | 40 FAIL | 46 FAIL |
| v3.1 + gemmLnc term | 34 FAIL | 34 FAIL | 34 FAIL | 45 FAIL | 47 PASS | 42 FAIL | 35 FAIL |
| v3.1 + contention | 34 FAIL | 34 FAIL | 34 FAIL | 40 FAIL | 41 FAIL | 40 FAIL | 37 FAIL |
| v3.1 + both terms | 34 FAIL | 34 FAIL | 34 FAIL | 45 FAIL | 47 PASS | 42 FAIL | 34 FAIL |
| v3.1 with T7 | 34 FAIL | 45 FAIL | 34 FAIL | 38 FAIL | 36 FAIL | 40 FAIL | 38 FAIL |
| MM1-v3 refitted | 45 FAIL | 47 PASS | 45 FAIL | 40 FAIL | 41 FAIL | 40 FAIL | 46 FAIL |

## 9. The readings beside the scorer (REPORTED)

- **The tie t01** (`gemmL2x4x4` fp32, rgm136; 3 runs at places 1, 42 and 83): 1121.67 wall cycles an op, +0.0157% against E215 arm A's t01 on this card and -0.0003% against E213 arm A's: the tie moved by less than 0.02% between the days.
- **His question, as E215 read it** (the measured cycles an op over the resident tensor op's floor, 529 cycles an op in fp32 and fp16 and 270 in int8): the counter's mean reads G 1.80-3.56 (median 2.56); Gt 2.05-3.10 (median 2.64); Y 2.10-3.11 (median 2.91); F 2.06-4.31 (median 2.18) times the floor; the wall 1.80-4.33 times (median 2.70) over all 52.
- **E4 against MM1-v3.2's own frozen J at rest** (its rest law; verify-e218d's info finding 4, made again here): 40 of 52 points in the 10% band. The registered E4 reads the measured rest x the forecast seconds + the frozen J (the scorer's docstring and the band's held-out basis), and it is the one scored.
- **The transistor switches** "are estimated, not measured": "no card counts switches; MM1-v3.2's switch outputs sit beside every point and are never scored." This note scores none.

## 10. verify-e218d's re-derivation, beside (its own code; verdict HOLDS)

- **The measured side.** Its own reader of the session's raw files rebuilt 107 runs and 2 smokes: 872 of 872 run fields are bit-equal to `data-e218.json`, and 364 of 364 point means equal the scorer's. This lane compared its measured table with the scorer's means field by field: 364 of 364 equal.
- **The rules,** scored from E218.md's words with its own code: verdicts 26 of 26, cells 364 of 364, head-to-heads 16 of 16 (counts, p and every d), P1 rows 7 of 7, the REPORTED model statistics 105 of 105 and the other models at MM1-v3.2's bands 63 of 63, all equal.
- **Against this note:** its family table equals section 7's in 825 of 825 cells; its misses and counts per rule equal section 3's; its G-Gt ratios, the tie's offset, the timing over the floor and the candidates' P1 tallies equal sections 6, 8 and 9.
- **Its other checks** (its result): the files (`SHA256SUMS` 582/582; the raw copy against the session's manifest 572/572; the committed session 575/575 under the scrub), the scrub, the blindness (only `b445b0f5` touches an E218 data path on any ref, after every freeze line), the seal (registered before the booking), the go lines, the window, the rest (852 minutes), reads only, the clock (27,078 of 27,078 samples at 600 MHz), nothing set, 45.2 of 70 card-minutes, no stop, no SIGKILL, every release and a clean lab clone: all hold.

## 11. Findings, answered as dated clauses (Fri 20 Nov 2026, after the data; post hoc; nothing re-scored)

1. **R0 FAIL comes from one run: f04's run 77 printed no check of C** (card-e218's finding, verify-e218d's finding 1, both medium). f04 is `gemmL15x16x32` fp32 (MM1-v3.2's frozen seconds a GEMM 1.3086 s; measured 1.3279 s). Each of its two processes (registered `--seconds 6 --budget 7.5`) began its first launch 1.665 s and 1.669 s after it started and ran six launches of 1.32-1.34 s each (to 9.62 s and 9.64 s), and its stderr then read "stopping: device-time budget of 7.5 s used". Run 7's check of C then printed `approx` from 9.62 to 9.98 s, and its process ended at 10.088 s on the plain `timeout 10`'s TERM (rc 124). Run 77's process ended the same way at 10.136 s (rc 124) before any check line. The session log reads "run 077-pass2-f04 done: 1 process(es), rc [124], checks ['None'], gate ['GATE OK'], walk ['none'], the process rc 124". Neither was hung, and nothing was killed. **Answered:** the registered reading stands. The frozen scorer counts a run with no check as an R0 failure, R0 FAIL labels every other verdict, and every verdict stays as printed with that label. Nothing in R0's other parts failed: every other check of C read approx (98) or exact (10), none read wrong, the smokes' counter means sat inside 200-4,000 cycles an op, and every rgm211-host process's walk and gate were good. f04's counted launches are complete in both runs, so both runs stay kept, and f04 is inside every band. The lesson is for future kits: check at the desk, for each point, that the startup, `--budget`, one forecast GEMM and the check fit inside the plain timeout, or size `--budget` per point. verify-e218d found that no desk check at the registration, kit, verifier or readiness stage compared a process's length with the timeout.
2. **The seal's note has a broken sentence** (verify-e218d's finding 2, a nit): `tools/claims-v3/sealed-e218/e218-freeze-lines.md` (`6dc30e04`) reads "...as this note is written the box is still held by / written, nor when it is committed (above)." Its sha256 line, its times and its record are right. **Answered:** words only, recorded here; the note is not edited.
3. **The scorer's outputs were not yet committed** (card-e218's open issue, verify-e218d's info finding 3). **Answered** by this note's commit: both files byte for byte, with `SHA256SUMS-note1`. As in E215 arm A's directory, `README.md` sits outside `SHA256SUMS`, and the session's `runner.out` and `runner.rc` sit outside its manifest; `SHA256SUMS-note1` lists `README.md` and `SHA256SUMS` as committed.
4. **E4's reading** (verify-e218d's info finding 4). **Answered:** E4 is registered as the measured rest x the forecast seconds + the frozen J. Read against MM1-v3.2's own frozen J at rest, it would be 40 of 52 (section 9). That figure is REPORTED only.
5. **P1 FAIL is robust** (verify-e218d's info finding 5). **Answered:** section 6 makes it again from the committed runs. The day's own Y repeat is 0.00048 in ln, and every separation is 0.021 or more.
6. **Every T1 and T3 miss is in family G** (verify-e218d's info finding 6). **Answered:** section 4's reading. The gemmLnc branch's wall differs from its cooperative twin's by -13.3% to +15.4%, while MM1-v3.2 prices the two within 2.0% of each other.
7. **The G block's board peak was 51.32 W, against verify-e218's expected ~64 W, and the card time was 45.2 minutes, against 48.0 planned and verify-e218's ~53 expected** (card-e218's two info findings, its figures). **Answered:** recorded here. Both sit inside the registered stops and the 70-minute cap, and nothing changes.
8. **The model session's sealed forecast** of E218's points is registered in `6dc30e04`, before the booking. **Answered:** the lab scores none of it, and this note holds no number of it.

## 12. What this note does not do

- It changes no committed file, re-scores nothing and moves no verdict.
- **NOT RUN here:** an independent re-computation of the bootstrap intervals (they are the scorer's, made again by its own `boot()`); a re-derivation of the bands' held-out bases (taken as registered); a re-derivation of the measured side from the session's raw files (verify-e218d's, section 10); any read of a box's disk.
- **The public-text scan** of the four files and the commit's message (login and home paths, the lab scanner's fixed list and this box's privacy table, the tier classes, desk paths) found no hit but one class's reading of verify-lay's three registered control names: 24 matches in the scorer's JSON and 24 in this note, reviewed as the lab's own names and passed with those exact counts.

## 13. `SHA256SUMS-note1`

`SHA256SUMS-note1` lists `scores-e218-A.json`, `scores-e218-A.txt` and this note, then `README.md` and `SHA256SUMS` as the data commit holds them. In this directory, `sha256sum -c SHA256SUMS-note1` reads all 5 lines OK, and `SHA256SUMS` still reads its 582 lines OK.

SPDX-License-Identifier: Apache-2.0
