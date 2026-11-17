# E209 data, dated note 16: the frozen scorer's outputs, committed beside the data byte for byte - R0 PASS; T1-T3 PASS 39 of 41; E1-E4 PASS; K1 PASS 44 of 45; H1-H3 MM1-v2 BETTER by the registered bootstrap of the mean d, which the REPORTED side readings do not confirm; H4 NOT DECIDED; H5 and H6 MM1-v2 BETTER - with verify-e209d's re-derivation beside each result

*Tue 17 Nov 2026 (week 47), PST. Written at about 14:25 PST by round Q212's lane `scores-e209`. That was after this directory's data commit `ea3fa3ce` (13:00:31 PST, pushed 13:00:36), the day's data verifier `verify-e209d` (13:04-13:34 PST: HOLDS WITH FIXES), note 15 (`b067742b`, 13:56:32 PST) and its erratum 1 (`d4bd2425`, 14:01:32 PST). **It adds new files only:** no committed file, rule, band, tie, forecast, label or verdict is changed, and nothing is re-scored. README.md's notes 1-14 came with the data commit and note 15 with the data verifier's fix; this is note 16. Labels: **registered** (E209.md with its amendment A1, `rules-e209.json`), **measured** (this directory's records, read through E208's registered reducer), **blind** (MM1-v2's forecasts, pushed in `3ca4b717` at 01:44:48 PST, before the first card command at 10:30:44 PST), **REPORTED** (never a verdict), **post hoc** (computed after the data, by this lane), **desk check of code** (this lane's checks and re-runs, and verify-e209d's own code), as each line says. Every desk step ran on aifoundry2 under `/usr/bin/python3` 3.12.3 with `-I -B`.*

**The words.** The frozen scorer (`score_e209.py`, registered sha256 `e522919a...`), run by the kit's step 13 (`rb/s24_score_e209_n1.sh` of kit note 1) on this directory's committed session, printed (`score.out`, byte for byte):

```
E209 scored (R0 PASS)
  R0: PASS (- of -)
  T1m: PASS (39 of 41)
  T1c: PASS (39 of 41)
  T2m: PASS (39 of 41)
  T2c: PASS (39 of 41)
  T3m: PASS (39 of 41)
  T3c: PASS (39 of 41)
  E1: PASS (45 of 45)
  E2m: PASS (42 of 45)
  E2c: PASS (41 of 44)
  E3: PASS (43 of 45)
  E4m: PASS (42 of 45)
  E4c: PASS (41 of 44)
  K1: PASS (44 of 45)
  H1: MM1-v2 BETTER (v2 closer 17, other 11, ties 13, p 0.34492845088243484; sign NOT DECIDED, bootstrap MM1-v2 BETTER)
  H2: MM1-v2 BETTER (v2 closer 15, other 11, ties 15, p 0.557197093963623; sign NOT DECIDED, bootstrap MM1-v2 BETTER)
  H3: MM1-v2 BETTER (v2 closer 17, other 11, ties 13, p 0.34492845088243484; sign NOT DECIDED, bootstrap MM1-v2 BETTER)
  H4: NOT DECIDED (v2 closer 9, other 5, ties 25, p 0.4239501953125; sign NOT DECIDED, bootstrap NOT DECIDED)
  H5: MM1-v2 BETTER (v2 closer 38, other 3, ties 0, p 1.0479197953827679e-08; sign MM1-v2 BETTER, bootstrap MM1-v2 BETTER)
  H6: MM1-v2 BETTER (v2 closer 35, other 5, ties 2, p 1.382612026645802e-06; sign MM1-v2 BETTER, bootstrap MM1-v2 BETTER)
```

and the readings beside it (E209.md A1; `rb/post_e209.py after`; REPORTED, never verdicts) printed (`post.out`, byte for byte):

```
E209 step 13 readings beside the frozen scorer (E209.md A1; REPORTED, never verdicts)
NO DATA, named: no kept run: none; kept runs but no time reading (no window view): none; a time reading but no energy reading: none
THE DAY OFFSET (reading f; 5 kept anchor runs of the day against E208's 27): W over idle -1.902%, op time -0.092%, clock +0.008%
H4 (registered) NOT DECIDED; offset_W -1.902%; H4n (REPORTED, J over idle / (1 + offset_W)) NOT DECIDED (v2 closer 7, v1 closer 6, ties 26; mean d 95% [-0.00208, 0.00597])
H1-H3 (registered) {'H1': 'MM1-v2 BETTER', 'H2': 'MM1-v2 BETTER', 'H3': 'MM1-v2 BETTER'}; beside them the op-time offset -0.092% and the clock offset +0.008%
```

verify-e209d's own code (its own reducer from the raw files, its own scoring) gives every one of these verdicts, counts and cells. **How to read them:** every MM1-v2 rule passes; the registration said before the data that "a PASS here does not favour MM1-v2 over MM1-v1: the head-to-head does". Against F1@800 (H5) and F2@800 (H6) MM1-v2 is closer by every test. Against MM1-v1 the registered verdicts H1-H3 rest on the mean d; the sign test, the median d's interval and the family check beside them do not confirm it (note 15 section 3, with its erratum 1), and H4 is not decided.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `data-e209.json` | 671,784 | `90bc84ab52441f53a6283e5b096a83e02de5ed5979b4c0cd5423fb203a0c2805` | E208's registered reducer (`reduce_mms.py` `b9e32618...`, with `mms_common.py` `c3fc7883...`) on this directory's committed `session/`: the scorer's input |
| `reduce-e209.txt` | 6,324 | `ec120c1f6caab527eb3b4676b2fe5838fd88630f23ce8b74df1d6784cf58f913` | the reducer's text table (its `--txt`) |
| `reduce.out` | 6,324 | `ec120c1f6caab527eb3b4676b2fe5838fd88630f23ce8b74df1d6784cf58f913` | the reducer's printed lines; the same bytes as `reduce-e209.txt` (it prints the table it writes) |
| `scored-e209.json` | 163,338 | `3e53bb3e587b899f44fb5ec5dc4610d704bc332f3997679ae5173d1472620e94` | the frozen scorer's output: every rule, cell, flag, head-to-head (with its REPORTED side readings), reading (e)-(j) and summary |
| `score.out` | 1,051 | `c1cacaed09f038b0b74da8b8982b2030a497ea38db8fd698933b037117685b40` | the scorer's printed lines (quoted above) |
| `post-e209.json` | 3,320 | `c34baff91940bafff7417e358973b8ba36047647b8e7da5495ef4299f7b4e7ea` | `rb/post_e209.py after` (E209.md A1): the points NO DATA named, reading (f)'s day offset, H4n |
| `post.out` | 677 | `be2561335abe329616ce70de5d0b3f159cd30bd1b15aacc361777911c5c86b2d` | its printed lines (quoted above) |
| `README.md.dated-note-16.md` | (this note) | listed in `SHA256SUMS-note16` | this dated note |
| `SHA256SUMS-note16` | 12 lines | (not listed in itself) | the eight files above; then four files as committed before this note: `README.md`, `SHA256SUMS`, `SHA256SUMS-note15` and `README.md.dated-note-15-erratum-1.md` (the last two were in no list) |

The seven output files are card-e209's step-13 files byte for byte (its run folder, outside the lab), under the names step 13 gave them. So note 15's reproduce line now runs in this directory as `python3 -I -B posthoc_note15_e209.py scored-e209.json data-e209.json --json posthoc-note15-e209.json > posthoc-note15-e209.txt`. With `SHA256SUMS` (231 entries), `SHA256SUMS-note15` and `SHA256SUMS-note16`, every file of this directory is in a list except `SHA256SUMS-note16` itself.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 is the runbook log's lines 53-54 of 56: `s24_score_n1_e209` started at 13:00:55 PST and ended "exit 0: scored: ..." at 13:00:57. It is the log's only run of step 13; the kit's unfixed `rb/s24_score_e209.sh` never ran. The lane that ran it (`collect-e209`) captured its printed lines: "the data commit ea3fa3ce340b (2026-11-17 13:00:31 -0800); HEAD ea3fa3ce", "MANIFEST CHECK: 221 of 221 manifest lines OK (1 by THE MASK of KIT.md.dated-note-1.md ...)", "reduce_mms.py rc 0", "LABELS OK: 0 point label(s), 0 time-case label(s) ...", "score_e209.py rc 0", the scorer's lines above, "post_e209.py after rc 0" and the readings above; then the seven sha256 at 13:00:58 and "LAB status after: 0 lines".
- **The commit before it.** The data commit `ea3fa3ce` was made at 13:00:31 PST and pushed at 13:00:36 (the lab clone's record of the push); the lane left its collect span and removed its hold line at 13:00:36-37 and ran step 13 at 13:00:55. The lab clone's HEAD at the step was the data commit (its next move came at 13:41:44, another lane's E211 data commit). Step 13 refuses unless the data directory is committed and unchanged from its commit, and its manifest read passes; both held.
- **The bytes and their times.** The seven files read today the sha256 the step's capture listed at 13:00:58, and each was last written inside the step (13:00:56.141 to 13:00:57.929 PST). No other file is in that folder.
- **The programs, at their pins.** At the data commit and in the lab now: `rb/s24_score_e209_n1.sh` `d37c86c3...` and `collect_e209_n1.py` `aad4926b...` (kit note 1's list), `score_e209.py` `e522919a...` (the registration's list), `rb/post_e209.py` `8985d505...` and `rb/rb_e209.sh` `9f9f0585...` (the kit's list), `reduce_mms.py` `b9e32618...` and `mms_common.py` `c3fc7883...` (E209.md section 7). The three lists read OK (22, 47 and 6 entries). The scorer refuses (exit 4) if any of its 18 frozen files or `points-e209.json` and `rules-e209.json` changed; it ended rc 0.
- **No label.** `ranbefore-e209.json` (this directory's, the same bytes the step read) names no point and no case; the step passed no `--labels`, and the scorer's output records none applied. So every point and case is in every rule it can enter.
- **The re-runs** (14:09:50 PST, this lane): in a fresh scratch clone of the lab, step 13's four calls exactly as the step makes them (the reducer, the label check, the scorer, the readings), each inside the round's CPU slot, (1) at the data commit `ea3fa3ce` and (2) at GitHub main as it stood then, `d4bd2425`: **all seven outputs equal card-e209's byte for byte, both times**, and the clone read 0 status lines after each.
- **Note 15's reproduce line** (14:14:58 PST, this lane), run in the data directory of that clone with the two files placed under the names they carry here: rc 0, and both its outputs equal note 15's committed `posthoc-note15-e209.txt` and `posthoc-note15-e209.json` byte for byte.
- **verify-e209d** (desk; its own reducer, standard library only, on the data commit's tree, and its own scoring with the frozen predictors called at each run's measured clock in a separate process) re-derived 62 runs and 2,598 fields against `data-e209.json` with 0 mismatches, and scored every rule: every verdict, count and cell equals `scored-e209.json`, and its bootstrap intervals equal the scorer's to the last digit (the same registered seeds). This lane compared its figures again (step 6 below): every point's and time case's measured figures and forecasts in its `mine-score.json` equal the scorer's, so every d below is the same from either.

## 3. The rules: their registered words, the scorer's verdict, verify-e209d's beside

The registered words are quoted from E209.md section 7 (line breaks aside); the cells and errors were re-made by this lane from the scorer's own figures and equal its cells and its `error` fields.

> **MM1-v2's rules.** Each time case or point passes when |measured / forecast - 1| is within its band; **a rule's verdict: PASS if at least 90% of its scored cases or points pass, FAIL otherwise, TOO FEW under 10, NO DATA with none.** The band is **twice the larger of MM1-v2's two held-out rms errors** for that quantity - (i) the E208 fold (every constant refitted without E208, the experiment that taught MM1-v2 its 800 MHz terms) on E208's aifoundry2 card 0 points, this day's card and clock, and (ii) leave one experiment out over all points - rounded up to a whole percent (E207's rule, with E208 in E206's place). If MM1-v2's blind errors are normal with an sd equal to that basis, a rule passes with the probability in the last column; at 1.25 or 1.5 times that error it mostly does not (MM1-v0 ran 1.3-1.6 times its held-out numbers blind on E206):

| rule | registered words (E209.md's table: what; band; arithmetic) | the scorer | failing cells (measured / forecast - 1) | the nearest passing cells (post hoc) | MM1-v2's error, rms (mean) of ln | verify-e209d |
|---|---|---|---|---|---|---|
| **T1m** | cycles an op, the wall, per time case (m: given the measured clock; c: with the clock forecast); 19%; 2 x max(9.09, 5.41) = 18.18 -> 19% | **PASS** 39 of 41 | `gemmL2x6x10\|fp32\|0x80000000` (e39) +23.96%; `gemmL3x1x5\|fp32\|0xffffffff` (e15) +19.34% | `gemmL1x3x1\|int8\|0xffffffff` (e07) +15.84%; `gemmL1x1x13\|fp32\|0xffffffff` (e11) +15.07%; `gemmL1x2x24\|fp32\|0xffffffff` (e24) +11.93% | 7.22% (+2.88%; 41) | PASS 39 of 41; 7.22% (+2.88%) |
| **T1c** | cycles an op, the wall, per time case (m: given the measured clock; c: with the clock forecast); 19%; 2 x max(9.09, 5.41) = 18.18 -> 19% | **PASS** 39 of 41 | `gemmL2x6x10\|fp32\|0x80000000` (e39) +23.98%; `gemmL3x1x5\|fp32\|0xffffffff` (e15) +19.36% | `gemmL1x3x1\|int8\|0xffffffff` (e07) +15.86%; `gemmL1x1x13\|fp32\|0xffffffff` (e11) +15.09%; `gemmL1x2x24\|fp32\|0xffffffff` (e24) +11.94% | 7.23% (+2.89%; 41) | PASS 39 of 41; 7.23% (+2.89%) |
| **T2m** | cycles an op, the counter's mean, per time case; 19%; 2 x max(9.1, 7.88) = 18.20 -> 19% | **PASS** 39 of 41 | `gemmL2x6x10\|fp32\|0x80000000` (e39) +25.33%; `gemmL6x6x6\|int8\|0xf000` (e42) +19.03% | `gemmL3x1x5\|fp32\|0xffffffff` (e15) +18.57%; `gemmL1x3x1\|int8\|0xffffffff` (e07) +14.55%; `gemmL1x1x13\|fp32\|0xffffffff` (e11) +14.32% | 8.12% (+3.97%; 41) | PASS 39 of 41; 8.12% (+3.97%) |
| **T2c** | cycles an op, the counter's mean, per time case; 19%; 2 x max(9.1, 7.88) = 18.20 -> 19% | **PASS** 39 of 41 | `gemmL2x6x10\|fp32\|0x80000000` (e39) +25.34%; `gemmL6x6x6\|int8\|0xf000` (e42) +19.04% | `gemmL3x1x5\|fp32\|0xffffffff` (e15) +18.58%; `gemmL1x3x1\|int8\|0xffffffff` (e07) +14.56%; `gemmL1x1x13\|fp32\|0xffffffff` (e11) +14.33% | 8.12% (+3.98%; 41) | PASS 39 of 41; 8.12% (+3.98%) |
| **T3m** | seconds a GEMM, per time case (T3m = T1m); 19%; 2 x max(9.09, 5.41) = 18.18 -> 19% | **PASS** 39 of 41 | `gemmL2x6x10\|fp32\|0x80000000` (e39) +23.96%; `gemmL3x1x5\|fp32\|0xffffffff` (e15) +19.34% | `gemmL1x3x1\|int8\|0xffffffff` (e07) +15.84%; `gemmL1x1x13\|fp32\|0xffffffff` (e11) +15.07%; `gemmL1x2x24\|fp32\|0xffffffff` (e24) +11.93% | 7.22% (+2.88%; 41) | PASS 39 of 41; 7.22% (+2.88%) |
| **T3c** | seconds a GEMM, per time case (T3m = T1m); 19%; 2 x max(9.09, 5.41) = 18.18 -> 19% | **PASS** 39 of 41 | `gemmL2x6x10\|fp32\|0x80000000` (e39) +23.96%; `gemmL3x1x5\|fp32\|0xffffffff` (e15) +19.34% | `gemmL1x3x1\|int8\|0xffffffff` (e07) +15.83%; `gemmL1x1x13\|fp32\|0xffffffff` (e11) +15.07%; `gemmL1x2x24\|fp32\|0xffffffff` (e24) +11.93% | 7.22% (+2.88%; 41) | PASS 39 of 41; 7.22% (+2.88%) |
| **E1** | J over idle given the measured seconds (and clock), per point; 14%; 2 x max(4.82, 6.59) = 13.18 -> 14% | **PASS** 45 of 45 | none | e08 +11.13%; e25 -10.07%; e23 -8.99% | 5.42% (-2.48%; 45) | PASS 45 of 45; 5.42% (-2.48%) |
| **E2m** | J over idle with the seconds forecast, per point; 15%; 2 x max(5.94, 7.35) = 14.70 -> 15% | **PASS** 42 of 45 | e08 +15.47%; e15 +18.14%; e39 +21.09% | e11 +13.27%; e25 -11.27%; e41 -10.93% | 7.06% (-0.78%; 45) | PASS 42 of 45; 7.06% (-0.78%) |
| **E2c** | J over idle with the seconds forecast, per point; 15%; 2 x max(5.94, 7.35) = 14.70 -> 15% | **PASS** 41 of 44 | e08 +15.47%; e15 +18.19%; e39 +21.17%; NO DATA: e44 (forecast capped: route c forecasts no energy there) | e11 +13.33%; e25 -11.25%; e41 -10.90% | 7.11% (-0.86%; 44) | PASS 41 of 44; 7.11% (-0.86%) |
| **E3** | J with the card at rest given the measured seconds and rest, per point; 5%; 2 x max(2.02, 2.03) = 4.06 -> 5% | **PASS** 43 of 45 | e08 +5.46%; e23 -5.16% | e25 -4.72%; e36 -4.27%; e41 -4.16% | 2.76% (-1.23%; 45) | PASS 43 of 45; 2.76% (-1.23%) |
| **E4m** | J with the card at rest with the seconds forecast (the measured rest), per point; 13%; 2 x max(6.31, 5.05) = 12.62 -> 13% | **PASS** 42 of 45 | e11 +14.46%; e15 +18.93%; e39 +23.23% | e08 +12.93%; e07 +12.19%; e41 -10.33% | 6.40% (+1.03%; 45) | PASS 42 of 45; 6.40% (+1.03%) |
| **E4c** | J with the card at rest with the seconds forecast (the measured rest), per point; 13%; 2 x max(6.31, 5.05) = 12.62 -> 13% | **PASS** 41 of 44 | e11 +14.47%; e15 +18.95%; e39 +23.25%; NO DATA: e44 (forecast capped: route c forecasts no energy there) | e08 +12.93%; e07 +12.22%; e41 -10.32% | 6.46% (+1.00%; 44) | PASS 41 of 44; 6.46% (+1.00%) |

> **Seconds given the measured clock are the wall cycles given the clock** by the reducer's own arithmetic (`cyc_op_max` = `kclock_mhz` x `T_op_us` and `t_pass_s` = `T_op_us` x the ops a GEMM): T3m is T1m, registered as one test under both names (the scorer asserts their cells equal). **The bands are wide because the rule makes them so, not by choice:** the E208 fold's 9.1% on this card's points is MM1-v2 without the L2 time in cycles and the subset term (they are pinned at zero in a fold without E208); the bands hold MM1-v1 too at most cases (MM1-v1 read E208's aifoundry2 runs at 8.92% rms in the wall cycles, unread), so **a PASS here does not favour MM1-v2 over MM1-v1: the head-to-head does**.

**The scorer:** T3m's cells equal T1m's and T3c's equal T1c's (the same two failing time cases), as it asserts; verify-e209d: "H3 cells equal H1 cells: True; T3m cells equal T1m cells: True".

> **The points under about 3 W over idle are scored in absolute watts in E1, E2m and E2c:** |W measured - W forecast| <= **0.35 W** = 2 x SD_rep rounded up, SD_rep = 0.173 W, the meter's replicate spread on this card: the pooled within-session sd of the W over idle of E208's anchor (the one arm run more than once within a session there: 9 runs in each of a2c0-S1, a2c0-S2 and a2c0-S1r, df 24); beside it, REPORTED: the S1 / S1r per-run spread over the 61 arms both read, 0.118 W (S1 0.169 W higher on average). **Which points:** a point whose MM1-v2 W over idle at 799.0 MHz is under 3 W (none of the 45: MM1-v2's lowest is e39, 7.51 W, because it keeps the governed base and the memory path awake on a subset; E208's one-shire runs on this card read 6.7-8.3 W over idle), or whose measured W over idle is under 3 W. F1 and F2 put five or six of the subset points under 3 W (they scale a subset's watts by its shires), but that does not make a watts point: only MM1-v2's W at 799.0 MHz or the measured W under 3 W does (`score_e209.py` > `point_figures`), so at those points H6 is decided in ln of J over idle unless the card itself reads under 3 W there. (Wording corrected before the land by amendment A1, item 4.) E3 and the E4s stay relative (the card at rest dominates them).

**The scorer:** no point is a watts point (MM1-v2's lowest W over idle at 799.0 MHz is e39's, 7.51 W, and the lowest measured is e43's, 7.26 W), so no cell of E1, E2m or E2c was scored in watts and the 0.35 W band touched nothing. verify-e209d: the same.

> **R0, the checks:** every check of C of the day exact or approx (every point run's processes, kept or set aside, and every anchor's), and the smoke good (rc 0, its check exact or approx, the runner's own smoke gates met: every launch ok, cycles an op 200-4,000, the host on its card, the board 2 W over its rest on at least 3 samples); a process with no check printed fails R0. **A FAIL labels every other verdict.**

**The scorer: R0 PASS** (64 checks read, 0 not exact or approx; the smoke good, 3 records). verify-e209d: PASS (64 checks: 30 exact, 34 approx; 64 processes rc 0; the smoke 3 of 3 good, the board 12.6-17.9 W over its rest on 22-23 samples). So no verdict carries R0's label.

> **K1, the clock forecast:** each point's measured burst clock (the reducer's `burst` view `kclock_mhz`, all launches at the governor's own mix, the mean over its runs) within **23 MHz** of MM1-v2's forecast burst-mean clock (2 x the governor model's chain rms on E208's 160 aifoundry2 runs, 11.15 MHz, in sample); PASS at 90% of points. **K2 (REPORTED):** MM1-v2's capped forecast (e44 alone) against every kept run's measured capped flag, beside 'never capped' (E208 on this card: 19 of 160 runs capped, so 'never capped' agreed on 141 and the model on 159 in sample, 157 in its chain).

**The scorer: K1 PASS** 44 of 45 (rms 9.89 MHz, mean +2.37 MHz); the failing point is e44: measured 788.9 MHz against the forecast's 764.1 (+24.8 MHz). **K2 (REPORTED):** MM1-v2's capped forecast agrees with 53 of 55 kept runs' capped flags, 'never capped' with 54. verify-e209d: K1 PASS 44 of 45 (9.89 MHz rms); K2 53 and 54 of 55. The runs behind both are named in note 15 section 6.

**The head-to-head rules.**

> **THE HEAD-TO-HEAD RULES** (registered now): per time case (cycles, seconds) or per point (joules), **d = |ln(measured / other)| - |ln(measured / MM1-v2)|** (at a watts point, |W - W_other| - |W - W_v2| in watts): MM1-v2 is closer where d > the tie, the other model where d < -the tie, a tie otherwise. **The ties** sit at or above this card's replicate floor (the pooled within-session sd of ln of each reading of E208's anchor): **0.005 in ln for cycles and seconds** (floors wall 0.0021, mean 0.0021, seconds 0.0021), **0.01 for joules** (floor 0.0099), **0.05 W** at a watts point.

| rule | registered words (what; cases or points; decided by) | the scorer's line (`score.out`) | verify-e209d |
|---|---|---|---|
| **H1** | cycles an op, the wall: MM1-v2 against MM1-v1, both at each run's measured clock, per time case; 41 time cases; the bootstrap interval of the mean d | MM1-v2 BETTER (v2 closer 17, other 11, ties 13, p 0.34492845088243484; sign NOT DECIDED, bootstrap MM1-v2 BETTER) | MM1-v2 BETTER (17/11/13; sign NOT DECIDED, p 0.345; bootstrap MM1-v2 BETTER, mean d 95% [+0.00370, +0.02934]) |
| **H2** | cycles an op, the counter's mean: MM1-v2 against MM1-v1 at the measured clock, per time case; 41 time cases; the bootstrap interval of the mean d | MM1-v2 BETTER (v2 closer 15, other 11, ties 15, p 0.557197093963623; sign NOT DECIDED, bootstrap MM1-v2 BETTER) | MM1-v2 BETTER (15/11/15; sign NOT DECIDED, p 0.557; bootstrap MM1-v2 BETTER, mean d 95% [+0.00630, +0.04505]) |
| **H3** | seconds a GEMM given the measured clock: MM1-v2 against MM1-v1, per time case (equal to H1 by the reducer's arithmetic); 41 time cases; the bootstrap interval of the mean d | MM1-v2 BETTER (v2 closer 17, other 11, ties 13, p 0.34492845088243484; sign NOT DECIDED, bootstrap MM1-v2 BETTER) | MM1-v2 BETTER (17/11/13; sign NOT DECIDED, p 0.345; bootstrap MM1-v2 BETTER, mean d 95% [+0.00361, +0.02907]) |
| **H4** | J over idle given the measured seconds (and clock): MM1-v2 against MM1-v1, per point both price; the 39 points MM1-v1 prices; the bootstrap interval of the mean d | NOT DECIDED (v2 closer 9, other 5, ties 25, p 0.4239501953125; sign NOT DECIDED, bootstrap NOT DECIDED) | NOT DECIDED (9/5/25; sign NOT DECIDED, p 0.424; bootstrap NOT DECIDED, mean d 95% [-0.00047, +0.00849]) |
| **H5** | cycles an op, the wall: MM1-v2 (measured clock) against F1@800, per time case; 41 time cases; the exact sign test | MM1-v2 BETTER (v2 closer 38, other 3, ties 0, p 1.0479197953827679e-08; sign MM1-v2 BETTER, bootstrap MM1-v2 BETTER) | MM1-v2 BETTER (38/3/0; sign MM1-v2 BETTER, p 1.05e-08; bootstrap MM1-v2 BETTER, mean d 95% [+0.08307, +0.13648]) |
| **H6** | J over idle with the seconds forecast: MM1-v2 (measured clock) against F2@800, per point both price; the 42 points F2 prices; the exact sign test | MM1-v2 BETTER (v2 closer 35, other 5, ties 2, p 1.382612026645802e-06; sign MM1-v2 BETTER, bootstrap MM1-v2 BETTER) | MM1-v2 BETTER (35/5/2; sign MM1-v2 BETTER, p 1.38e-06; bootstrap MM1-v2 BETTER, mean d 95% [+0.29902, +0.67297]) |

> **MM1-v2 against MM1-v1 (H1-H4) is decided by the percentile bootstrap 95% interval of the mean d over the cases** (B = 10,000, seeded `random.Random("E209|bootstrap|<rule>")`: MM1-v2 BETTER if the interval lies above 0, MM1-v1 BETTER if below, NOT DECIDED otherwise; TOO FEW under 10 untied cases; the watts points counted in the untied number, left out of the interval)

> **MM1-v2 against F1 (H5) and F2 (H6) is decided by the exact two-sided sign test at alpha 0.05 on the untied cases** (E207's form)

> **REPORTED beside every head-to-head, never verdicts:** the other test's verdict; a family-level check (the sign test over the families' median d, E207's fix); the bootstrap of the median d.

## 4. The head-to-head results, rule by rule and case by case

**Beside each registered verdict, the REPORTED side readings** (from the scorer's own JSON; note 15 section 3 states them with its family table, and its erratum 1 corrects two of its figures: H2's registered interval reads [+0.0063, **+0.0450**] and H5's bootstrap mean d **+0.1097**, as below):

| rule | registered verdict (its test) | cells: MM1-v2 / other / tie (not compared) | the bootstrap of the mean d, 95% | the exact sign test | the bootstrap of the median d, 95% (REPORTED) | the family check (REPORTED) |
|---|---|---|---|---|---|---|
| **H1** | **MM1-v2 BETTER** (the bootstrap of the mean d) | 17 / 11 / 13 | +0.0158 [+0.0037, +0.0293]: MM1-v2 BETTER | 17 against 11, p 0.345: NOT DECIDED | +0.0024 [-0.0042, +0.0096]: spans 0 | 2 families against 2, p 1.000 |
| **H2** | **MM1-v2 BETTER** (the bootstrap of the mean d) | 15 / 11 / 15 | +0.0233 [+0.0063, +0.0450]: MM1-v2 BETTER | 15 against 11, p 0.557: NOT DECIDED | +0.0028 [-0.0039, +0.0096]: spans 0 | 2 families against 2, p 1.000 |
| **H3** | **MM1-v2 BETTER** (the bootstrap of the mean d) | 17 / 11 / 13 | +0.0158 [+0.0036, +0.0291]: MM1-v2 BETTER | 17 against 11, p 0.345: NOT DECIDED | +0.0024 [-0.0042, +0.0096]: spans 0 | 2 families against 2, p 1.000 |
| **H4** | **NOT DECIDED** (the bootstrap of the mean d) | 9 / 5 / 25 (6) | +0.0038 [-0.0005, +0.0085]: NOT DECIDED | 9 against 5, p 0.424: NOT DECIDED | +0.0011 [-0.0032, +0.0054]: spans 0 | 1 family against 0, p 1.000 |
| **H5** | **MM1-v2 BETTER** (the exact sign test) | 38 / 3 / 0 | +0.1097 [+0.0831, +0.1365]: MM1-v2 BETTER | 38 against 3, p 1.05e-08: MM1-v2 BETTER | +0.1027 [+0.0805, +0.1576]: above 0 | 9 families against 0, p 0.00391 |
| **H6** | **MM1-v2 BETTER** (the exact sign test) | 35 / 5 / 2 (3) | +0.4778 [+0.2990, +0.6730]: MM1-v2 BETTER | 35 against 5, p 1.38e-06: MM1-v2 BETTER | +0.1801 [+0.0897, +0.3788]: above 0 | 9 families against 0, p 0.00391 |

**Beside H1-H4, step 13's readings (E209.md A1, REPORTED):** the day offset against E208's 27 anchor runs on this card is -1.902% in W over idle, -0.092% in op time and +0.008% in the clock (`post.out`), so the time offsets beside H1-H3 are under a fifth of their 0.005 tie (0.0009 and 0.0001 in ln); H4n (H4 with every measured J over idle divided by 1 + offset_W) is NOT DECIDED (7 / 6 / 26; mean d 95% [-0.00208, +0.00597]), as H4 is. verify-e209d: the same offsets and H4n (7 / 6 / 26, [-0.00208, 0.00597]). The registration's words for H4n: "**H4n, REPORTED only:** H4 re-read with every measured J over idle (and W, at a watts point) divided by (1 + offset_W), with H4's ties, test and interval (the scorer's own `h2h`, seed `E209|bootstrap|H4n`). The day's result prints offset_W and H4n on H4's line, and the cycle offsets beside H1-H3. H1-H4 stay decided as registered."

**What the side readings say** (REPORTED, never a verdict; note 15 section 3). H5 and H6 have every side reading with them. H1-H3's registered "MM1-v2 BETTER" rests on the mean d, and that mean holds when the seed changes (verify-e209d: the interval's lower bound stays at 0.0035-0.0041 over 20 other seeds), but case by case the day does not show it: the sign test is NOT DECIDED, the median d's interval spans 0 and the families split 2 against 2. The mean comes mostly from the subsets (median d +0.054 in H1); MM1-v1 is closer on one K block (-0.035) and on the power-of-two strides (-0.017). So H1-H3 read as **MM1-v2 closer on average, mostly through the subsets**, not as MM1-v2 closer case by case.

**Per time case** (41; H1, H2, H3 and H5). d = |ln(measured / other)| - |ln(measured / MM1-v2)|, MM1-v2 at each run's measured clock (route m); MM1-v2 is closer where d > 0.005, the other where d < -0.005, a tie otherwise. The ln errors are 100 x ln(measured / forecast) of the wall. H3's cells equal H1's (asserted by the scorer; its d equal H1's to 2.4e-08).

| time case (points) | family | measured wall, cycles an op | ln err MM1-v2 | ln err MM1-v1 | ln err F1@800 | H1 d: cell | H2 d: cell | H5 d: cell |
|---|---|---|---|---|---|---|---|---|
| `gemmL1x16x6\|fp16\|0xffffffff` (e33) | power-of-two stride | 1698.9 | +4.24 | +2.19 | +5.35 | -0.0205: v1 | -0.0205: v1 | +0.0111: v2 |
| `gemmL1x1x11\|fp32\|0xffffffff` (e10) | the knee | 1283.8 | +0.73 | +1.93 | -22.54 | +0.0119: v2 | -0.0119: v1 | +0.2180: v2 |
| `gemmL1x1x13\|fp32\|0xffffffff` (e11) | the knee | 1746.1 | +14.04 | +21.34 | +8.22 | +0.0730: v2 | +0.0730: v2 | -0.0582: F1 |
| `gemmL1x1x40\|fp32\|0xffffffff` (e23) | long K | 2036.8 | +10.35 | +9.88 | -15.03 | -0.0048: tie | -0.0048: tie | +0.0468: v2 |
| `gemmL1x1x7\|int8\|0xf` (e17) | subsets | 1152.4 | +5.00 | +17.23 | -11.67 | +0.1223: v2 | +0.3159: v2 | +0.0667: v2 |
| `gemmL1x2x14\|int8\|0xffffffff` (e26) | long K | 1876.8 | +4.70 | +8.69 | -5.56 | +0.0399: v2 | +0.0399: v2 | +0.0086: v2 |
| `gemmL1x2x24\|fp32\|0xffffffff` (e24) | long K | 2055.5 | +11.27 | +10.85 | -14.12 | -0.0043: tie | -0.0043: tie | +0.0284: v2 |
| `gemmL1x2x9\|fp32\|0xffffffff` (e12) | the knee | 1474.0 | +9.56 | +11.75 | -23.29 | +0.0219: v2 | +0.0219: v2 | +0.1373: v2 |
| `gemmL1x3x1\|int8\|0xffffffff` (e07) | one K block | 1008.8 | +14.71 | +10.85 | +24.98 | -0.0386: v1 | -0.0386: v1 | +0.1027: v2 |
| `gemmL1x3x2\|fp16\|0x1` (e43) | subsets | 1060.2 | -2.60 | +13.90 | -10.24 | +0.1130: v2 | +0.1650: v2 | +0.0764: v2 |
| `gemmL1x3x2\|fp32\|0xffff` (e04) | inside the L3 | 1063.2 | -1.27 | +7.18 | -9.65 | +0.0591: v2 | +0.0846: v2 | +0.0838: v2 |
| `gemmL1x3x2\|fp32\|0xffffffff` (e44) | governor | 1059.7 | -0.48 | -0.11 | -9.98 | -0.0037: tie | +0.0004: tie | +0.0951: v2 |
| `gemmL1x3x2\|int8\|0xffffffff` (e01, e35) | inside the L3 | 1129.8 | +5.93 | +6.30 | -6.88 | +0.0037: tie | +0.0037: tie | +0.0095: v2 |
| `gemmL1x3x7\|int8\|0xffffffff` (e16) | the knee | 1298.2 | +3.69 | +4.67 | -23.35 | +0.0097: v2 | +0.0097: v2 | +0.1966: v2 |
| `gemmL1x4x12\|fp32\|0xffffffff` (e32) | power-of-two stride | 1725.8 | -6.08 | -4.11 | -14.13 | -0.0198: v1 | -0.0198: v1 | +0.0805: v2 |
| `gemmL1x4x3\|fp16\|0xffffffff` (e45) | governor | 1075.5 | -0.63 | -1.59 | -13.64 | +0.0096: v2 | +0.0028: tie | +0.1301: v2 |
| `gemmL1x4x3\|fp32\|0xffffffff` (e05) | inside the L3 | 1070.0 | -1.14 | -2.10 | -13.85 | +0.0096: v2 | +0.0096: v2 | +0.1271: v2 |
| `gemmL1x7x6\|fp32\|0xffffffff` (e29) | power-of-two stride | 1314.3 | -4.32 | -6.70 | -20.19 | +0.0238: v2 | +0.0238: v2 | +0.1586: v2 |
| `gemmL1x8x6\|fp32\|0x1111` (e40) | subsets | 1560.0 | +9.89 | +8.00 | +23.86 | -0.0189: v1 | -0.0189: v1 | +0.1397: v2 |
| `gemmL1x8x6\|fp32\|0xffffffff` (e28) | power-of-two stride | 1704.8 | +4.58 | +2.86 | +5.82 | -0.0172: v1 | -0.0172: v1 | +0.0124: v2 |
| `gemmL2x1x20\|int8\|0xffffffff` (e25) | long K | 1782.2 | -2.99 | -3.46 | -26.74 | +0.0047: tie | +0.0047: tie | +0.2375: v2 |
| `gemmL2x1x3\|fp32\|0xff` (e09) | subsets | 1077.1 | -0.83 | +10.93 | -13.19 | +0.1010: v2 | +0.1177: v2 | +0.1235: v2 |
| `gemmL2x1x6\|int8\|0xffffffff` (e13) | the knee | 1186.6 | -2.75 | -2.03 | -32.33 | -0.0073: v1 | -0.0073: v1 | +0.2958: v2 |
| `gemmL2x2x5\|fp16\|0xffffffff` (e14) | the knee | 1136.4 | -4.41 | -4.01 | -22.39 | -0.0039: tie | -0.0039: tie | +0.1799: v2 |
| `gemmL2x3x16\|fp16\|0xffffffff` (e27) | long K | 1908.0 | +4.24 | +5.27 | -21.52 | +0.0103: v2 | +0.0103: v2 | +0.1728: v2 |
| `gemmL2x3x2\|fp16\|0xffffffff` (e02) | inside the L3 | 1055.4 | -1.34 | -1.57 | -10.69 | +0.0023: tie | +0.0023: tie | +0.0934: v2 |
| `gemmL2x3x2\|fp32\|0xffffffff` (e06) | inside the L3 | 1055.3 | -1.35 | -1.58 | -10.40 | +0.0023: tie | +0.0023: tie | +0.0905: v2 |
| `gemmL2x3x2\|int8\|0x1111` (e31) | subsets | 1134.8 | +4.16 | +18.24 | -6.44 | +0.1408: v2 | +0.1408: v2 | +0.0228: v2 |
| `gemmL2x6x10\|fp16\|0xffffffff` (e37) | kinds | 1617.8 | +1.93 | +2.16 | -20.59 | +0.0024: tie | +0.0024: tie | +0.1867: v2 |
| `gemmL2x6x10\|fp32\|0x80000000` (e39) | subsets | 1655.7 | +21.48 | +20.16 | +29.81 | -0.0132: v1 | -0.0132: v1 | +0.0833: v2 |
| `gemmL2x6x10\|fp32\|0xffffffff` (e18, e34) | past the L3 | 1623.0 | +2.26 | +2.50 | -20.25 | +0.0024: tie | +0.0024: tie | +0.1799: v2 |
| `gemmL2x8x4\|int8\|0xffffffff` (e30) | power-of-two stride | 1680.8 | +1.53 | +1.83 | -0.11 | +0.0030: tie | +0.0030: tie | -0.0142: F1 |
| `gemmL3x1x5\|fp32\|0xffffffff` (e15) | the knee | 1768.9 | +17.68 | +25.89 | +9.52 | +0.0820: v2 | +0.0820: v2 | -0.0817: F1 |
| `gemmL3x2x2\|int8\|0xffffffff` (e03) | inside the L3 | 1132.7 | +4.79 | +4.32 | -6.62 | -0.0047: tie | -0.0047: tie | +0.0183: v2 |
| `gemmL3x5x1\|int8\|0xffffffff` (e08) | one K block | 1033.8 | +9.83 | +6.65 | +15.12 | -0.0318: v1 | -0.0106: v1 | +0.0529: v2 |
| `gemmL3x5x5\|fp16\|0xffffffff` (e19, e36) | past the L3 | 1416.6 | -1.40 | -0.33 | -17.41 | -0.0107: v1 | +0.0044: tie | +0.1602: v2 |
| `gemmL3x5x5\|fp32\|0xffff0000` (e41) | subsets | 1212.6 | -10.22 | -8.28 | -32.85 | -0.0194: v1 | -0.0194: v1 | +0.2263: v2 |
| `gemmL3x5x5\|int8\|0xffffffff` (e22) | past the L3 | 1424.8 | -0.82 | +0.25 | -18.16 | -0.0057: v1 | +0.0107: v2 | +0.1734: v2 |
| `gemmL5x3x6\|fp32\|0xffffffff` (e21) | past the L3 | 1430.7 | -0.69 | -0.27 | -19.27 | -0.0042: tie | +0.0042: tie | +0.1858: v2 |
| `gemmL6x6x6\|int8\|0xf000` (e42) | subsets | 1239.8 | -3.01 | -3.73 | -31.39 | +0.0072: v2 | -0.0072: v1 | +0.2839: v2 |
| `gemmL6x6x6\|int8\|0xffffffff` (e20, e38) | past the L3 | 1418.9 | -2.14 | -4.11 | -17.90 | +0.0196: v2 | +0.0196: v2 | +0.1576: v2 |

**Per point** (45; H4 and H6). H4: J over idle given the measured seconds, MM1-v2 against MM1-v1; H6: J over idle with the seconds forecast, MM1-v2 (measured clock) against F2@800; the tie 0.01 in ln; no watts point. 'n.c.' = not compared (the other model does not price the point: MM1-v1 prices no ones or real tile, F2@800 no ones tile).

| point | kind, format | time case | measured J over idle, mJ | ln err MM1-v2 given t | ln err MM1-v1 given t | H4 d: cell | ln err MM1-v2, t forecast | ln err F2@800 | H6 d: cell |
|---|---|---|---|---|---|---|---|---|---|
| e01 | random, int8 | `gemmL1x3x2\|int8\|0xffffffff` | 12.117 | +1.36 | +2.75 | +0.0139: v2 | +3.54 | +92.96 | +0.8942: v2 |
| e02 | random, fp16 | `gemmL2x3x2\|fp16\|0xffffffff` | 44.203 | +4.52 | +5.18 | +0.0067: tie | +4.24 | +41.93 | +0.3769: v2 |
| e03 | zeros, int8 | `gemmL3x2x2\|int8\|0xffffffff` | 12.775 | +3.46 | +2.94 | -0.0052: tie | +7.06 | +86.08 | +0.7902: v2 |
| e04 | random, fp32 | `gemmL1x3x2\|fp32\|0xffff` | 12.950 | +0.22 | +0.60 | +0.0037: tie | -0.16 | +49.30 | +0.4915: v2 |
| e05 | ones, fp32 | `gemmL1x4x3\|fp32\|0xffffffff` | 24.279 | +4.14 | n.f. | n.c. | +3.71 | n.p. | n.c. |
| e06 | zeros, fp32 | `gemmL2x3x2\|fp32\|0xffffffff` | 13.266 | +8.22 | +8.22 | +0.0000: tie | +7.26 | +81.09 | +0.7383: v2 |
| e07 | random, int8 | `gemmL1x3x1\|int8\|0xffffffff` | 5.282 | +3.07 | +3.47 | +0.0040: tie | +8.61 | +97.45 | +0.8884: v2 |
| e08 | random, int8 | `gemmL3x5x1\|int8\|0xffffffff` | 29.111 | +10.56 | +10.91 | +0.0036: tie | +14.39 | +78.34 | +0.6396: v2 |
| e09 | random, fp32 | `gemmL2x1x3\|fp32\|0xff` | 8.062 | -2.05 | -2.79 | +0.0073: tie | -2.42 | +70.22 | +0.6780: v2 |
| e10 | random, fp32 | `gemmL1x1x11\|fp32\|0xffffffff` | 44.914 | +2.43 | +3.45 | +0.0102: v2 | +2.59 | +9.29 | +0.0670: v2 |
| e11 | zeros, fp32 | `gemmL1x1x13\|fp32\|0xffffffff` | 20.823 | +1.94 | +1.98 | +0.0004: tie | +12.46 | +27.16 | +0.1470: v2 |
| e12 | random, fp32 | `gemmL1x2x9\|fp32\|0xffffffff` | 71.577 | -4.63 | -3.40 | -0.0124: v1 | -2.40 | -10.67 | +0.0827: v2 |
| e13 | random, int8 | `gemmL2x1x6\|int8\|0xffffffff` | 24.056 | -4.60 | -3.18 | -0.0142: v1 | -5.67 | +6.34 | +0.0066: tie |
| e14 | random, fp16 | `gemmL2x2x5\|fp16\|0xffffffff` | 70.115 | -3.77 | -3.09 | -0.0068: tie | -4.72 | +16.33 | +0.1160: v2 |
| e15 | zeros, fp32 | `gemmL3x1x5\|fp32\|0xffffffff` | 24.380 | +3.32 | +3.58 | +0.0026: tie | +16.67 | +28.62 | +0.1195: v2 |
| e16 | random, int8 | `gemmL1x3x7\|int8\|0xffffffff` | 44.202 | -5.47 | -3.75 | -0.0173: v1 | -4.01 | +11.21 | +0.0720: v2 |
| e17 | random, int8 | `gemmL1x1x7\|int8\|0xf` | 5.226 | -4.56 | -7.62 | +0.0306: v2 | -0.59 | +198.11 | +1.9752: v2 |
| e18 | random, fp32 | `gemmL2x6x10\|fp32\|0xffffffff` | 494.304 | -5.87 | -5.25 | -0.0062: tie | -5.29 | -14.82 | +0.0953: v2 |
| e19 | random, fp16 | `gemmL3x5x5\|fp16\|0xffffffff` | 279.238 | -6.01 | -5.19 | -0.0083: tie | -6.32 | +0.14 | -0.0619: F2 |
| e20 | random, int8 | `gemmL6x6x6\|int8\|0xffffffff` | 482.333 | -6.75 | -6.17 | -0.0058: tie | -7.55 | +8.17 | +0.0061: tie |
| e21 | zeros, fp32 | `gemmL5x3x6\|fp32\|0xffffffff` | 124.536 | +0.45 | +0.98 | +0.0054: tie | -0.05 | -4.97 | +0.0492: v2 |
| e22 | ones, int8 | `gemmL3x5x5\|int8\|0xffffffff` | 111.693 | -4.51 | n.f. | n.c. | -5.02 | n.p. | n.c. |
| e23 | random, fp32 | `gemmL1x1x40\|fp32\|0xffffffff` | 176.667 | -9.43 | -9.54 | +0.0011: tie | -6.55 | -27.88 | +0.2132: v2 |
| e24 | zeros, fp32 | `gemmL1x2x24\|fp32\|0xffffffff` | 89.544 | -7.42 | -7.17 | -0.0025: tie | +0.35 | -34.02 | +0.3367: v2 |
| e25 | random, int8 | `gemmL2x1x20\|int8\|0xffffffff` | 99.246 | -10.62 | -9.17 | -0.0145: v1 | -11.95 | -47.69 | +0.3573: v2 |
| e26 | random, int8 | `gemmL1x2x14\|int8\|0xffffffff` | 73.554 | -6.50 | -5.48 | -0.0101: v1 | -4.37 | -11.24 | +0.0687: v2 |
| e27 | random, fp16 | `gemmL2x3x16\|fp16\|0xffffffff` | 398.077 | -6.54 | -6.60 | +0.0006: tie | -5.31 | -30.44 | +0.2513: v2 |
| e28 | random, fp32 | `gemmL1x8x6\|fp32\|0xffffffff` | 201.671 | -4.71 | -4.41 | -0.0030: tie | -3.52 | +12.15 | +0.0863: v2 |
| e29 | random, fp32 | `gemmL1x7x6\|fp32\|0xffffffff` | 161.861 | -6.18 | -5.37 | -0.0081: tie | -7.15 | +3.51 | -0.0364: F2 |
| e30 | random, int8 | `gemmL2x8x4\|int8\|0xffffffff` | 154.563 | -7.10 | -6.78 | -0.0032: tie | -6.42 | +18.17 | +0.1175: v2 |
| e31 | random, int8 | `gemmL2x3x2\|int8\|0x1111` | 8.884 | -3.31 | -6.32 | +0.0301: v2 | +0.01 | +200.55 | +2.0054: v2 |
| e32 | random, fp32 | `gemmL1x4x12\|fp32\|0xffffffff` | 202.820 | -6.50 | -5.81 | -0.0069: tie | -8.13 | -12.31 | +0.0417: v2 |
| e33 | random, fp16 | `gemmL1x16x6\|fp16\|0xffffffff` | 382.418 | -4.60 | -4.79 | +0.0019: tie | -3.44 | +12.75 | +0.0932: v2 |
| e34 | real, fp32 | `gemmL2x6x10\|fp32\|0xffffffff` | 487.337 | -6.49 | n.f. | n.c. | -5.93 | -14.15 | +0.0823: v2 |
| e35 | real, int8 | `gemmL1x3x2\|int8\|0xffffffff` | 11.029 | -5.52 | n.f. | n.c. | -3.12 | +97.10 | +0.9398: v2 |
| e36 | real, fp16 | `gemmL3x5x5\|fp16\|0xffffffff` | 270.889 | -7.24 | n.f. | n.c. | -7.63 | +0.06 | -0.0757: F2 |
| e37 | ones, fp16 | `gemmL2x6x10\|fp16\|0xffffffff` | 285.782 | -4.67 | n.f. | n.c. | -3.82 | n.p. | n.c. |
| e38 | zeros, int8 | `gemmL6x6x6\|int8\|0xffffffff` | 284.158 | -2.75 | -3.28 | +0.0054: tie | -4.43 | +1.47 | -0.0296: F2 |
| e39 | random, fp32 | `gemmL2x6x10\|fp32\|0x80000000` | 116.803 | +0.13 | -4.21 | +0.0408: v2 | +19.14 | +245.93 | +2.2679: v2 |
| e40 | random, fp32 | `gemmL1x8x6\|fp32\|0x1111` | 57.973 | -3.36 | -6.15 | +0.0280: v2 | +3.22 | +128.88 | +1.2565: v2 |
| e41 | random, fp32 | `gemmL3x5x5\|fp32\|0xffff0000` | 161.317 | -8.26 | -7.76 | -0.0049: tie | -11.57 | +8.98 | -0.0259: F2 |
| e42 | random, int8 | `gemmL6x6x6\|int8\|0xf000` | 184.070 | +0.58 | -2.62 | +0.0204: v2 | -1.81 | +119.78 | +1.1797: v2 |
| e43 | random, fp16 | `gemmL1x3x2\|fp16\|0x1` | 3.697 | -4.30 | -8.37 | +0.0407: v2 | -6.54 | +209.70 | +2.0316: v2 |
| e44 | random, fp32 | `gemmL1x3x2\|fp32\|0xffffffff` | 23.530 | +4.42 | +5.61 | +0.0120: v2 | +4.33 | +39.71 | +0.3538: v2 |
| e45 | random, fp16 | `gemmL1x4x3\|fp16\|0xffffffff` | 44.448 | +3.43 | +4.15 | +0.0072: tie | +3.30 | +41.39 | +0.3808: v2 |

**Checked (desk, this lane's step 6):** every cell above, re-made from the scorer's per-case and per-point figures with the registered ties, equals the scorer's cell (41 x 4 time-case cells, 45 x 2 point cells) and verify-e209d's; every d equals note 15's committed d exactly (difference 0) and the d from verify-e209d's own figures exactly (difference 0); the counts equal the scorer's. 'n.f.' = NOT FORECAST, 'n.p.' = NOT PRICED.

## 5. The errors (REPORTED): MM1-v2 against MM1-v1, F1@800 and F2@800

> **REPORTED beside, never verdicts:** MM1-v1's own cells at MM1-v2's bands; F1 against F2 on J over idle; the rms and mean of ln(measured / forecast) of every model by family, format, kind and shire count; every flag.

rms (mean) of ln(measured / forecast), and the count. **S** = in the scorer's own output (its summaries or a rule's `error`); **V** = verify-e209d printed the same figure from its own scoring; **P** = post hoc, this lane's arithmetic on the scorer's measured figures and the frozen `f1f2_e209.csv` (F1@800 registered cycles, seconds and W over idle, F2@800 J over idle: E209.md section 5; F1@800's J columns and F2@800's J at rest are in the same frozen file). MM1-v2 and MM1-v1 at each run's measured clock unless 'clock forecast' (route c, MM1-v2's 799.0 MHz column); F1@800 and F2@800 as frozen. '-' = the model forecasts no such figure.

| quantity | MM1-v2 | MM1-v2, clock forecast | MM1-v1 | F1@800 | F2@800 |
|---|---|---|---|---|---|
| cycles an op, the wall (41 time cases) | 7.22% (+2.88%; 41) S V | 7.23% (+2.89%; 41) S V | 9.27% (+4.68%; 41) S V | 18.13% (-10.24%; 41) S V | - |
| cycles an op, the counter's mean (41 time cases) | 8.12% (+3.97%; 41) S V | 8.12% (+3.98%; 41) S V | 12.17% (+6.24%; 41) V | - | - |
| seconds a GEMM (41 time cases) | 7.22% (+2.88%; 41) S V | 7.22% (+2.88%; 41) S V | 9.27% (+4.68%; 41) V | 18.07% (-10.13%; 41) P | - |
| J over idle given the measured seconds (points) | 5.42% (-2.48%; 45) S V | - | 5.59% (-2.32%; 39) S V | - | - |
| J over idle with the seconds forecast (points) | 7.06% (-0.78%; 45) S V | 7.11% (-0.86%; 44) S V | 7.74% (+0.89%; 39) V | 55.38% (+14.59%; 42) V | 82.21% (+43.68%; 42) S V |
| J with the card at rest given the measured seconds (points) | 2.76% (-1.23%; 45) S V | - | 2.69% (-1.00%; 39) V | - | - |
| J with the card at rest with the seconds forecast (points) | 6.40% (+1.03%; 45) S V | 6.46% (+1.00%; 44) S V | 8.41% (+3.12%; 39) P | 17.35% (-6.07%; 42) P | 26.36% (-18.00%; 42) P |
| W over idle at the model's own seconds (points) | 6.31% (-3.50%; 45) V | - | - | 55.31% (+24.72%; 42) V | 83.51% (+53.80%; 42) V |

On MM1-v1's 39 points, MM1-v2's J over idle given the seconds reads 5.40% (-2.24%) **V**. So, blind on this card under its governor: MM1-v2's wall cycles and seconds are 22% smaller in rms than MM1-v1's and 2.5 times smaller than F1@800's; its joules over idle given the seconds are MM1-v1's within 0.19 points on the same 39 points (H4 NOT DECIDED); with the seconds forecast they are 8 and 12 times smaller than F1@800's and F2@800's; with the card at rest, given the seconds, both MM1 versions are within 3%.

**By family, format, kind and shire count** (the scorer's own `summaries_REPORTED`, **S**; rms (mean) of ln, and the count): the wall cycles per time case and J over idle given the seconds per point.

| group | wall: MM1-v2 | wall: MM1-v1 | wall: F1@800 | J over idle given t: MM1-v2 | J over idle given t: MM1-v1 | J over idle: F2@800 |
|---|---|---|---|---|---|---|
| all | 7.2% (+2.9%; 41) | 9.3% (+4.7%; 41) | 18.1% (-10.2%; 41) | 5.4% (-2.5%; 45) | 5.6% (-2.3%; 39) | 82.2% (+43.7%; 42) |
| family:governor | 0.6% (-0.6%; 2) | 1.1% (-0.9%; 2) | 12.0% (-11.8%; 2) | 4.0% (+3.9%; 2) | 4.9% (+4.9%; 2) | 40.6% (+40.5%; 2) |
| family:inside the L3 | 3.3% (+0.9%; 6) | 4.5% (+2.1%; 6) | 10.0% (-9.7%; 6) | 4.5% (+3.7%; 6) | 4.7% (+3.9%; 5) | 73.2% (+70.3%; 5) |
| family:kinds | 1.9% (+1.9%; 1) | 2.2% (+2.2%; 1) | 20.6% (-20.6%; 1) | 5.6% (-5.3%; 5) | 3.3% (-3.3%; 1) | 49.1% (+21.1%; 4) |
| family:long K | 7.5% (+5.5%; 5) | 8.1% (+6.2%; 5) | 18.1% (-16.6%; 5) | 8.3% (-8.1%; 5) | 7.7% (-7.6%; 5) | 32.4% (-30.3%; 5) |
| family:one K block | 12.5% (+12.3%; 2) | 9.0% (+8.8%; 2) | 20.6% (+20.0%; 2) | 7.8% (+6.8%; 2) | 8.1% (+7.2%; 2) | 88.4% (+87.9%; 2) |
| family:past the L3 | 1.6% (-0.6%; 5) | 2.2% (-0.4%; 5) | 18.6% (-18.6%; 5) | 5.2% (-4.5%; 5) | 4.8% (-3.9%; 4) | 8.8% (-2.9%; 4) |
| family:power-of-two stride | 4.4% (-0.0%; 5) | 4.0% (-0.8%; 5) | 11.6% (-4.7%; 5) | 5.9% (-5.8%; 5) | 5.5% (-5.4%; 5) | 12.7% (+6.9%; 5) |
| family:subsets | 9.5% (+3.0%; 8) | 13.7% (+9.6%; 8) | 22.3% (-6.5%; 8) | 4.1% (-3.1%; 8) | 6.1% (-5.7%; 8) | 165.8% (+147.8%; 8) |
| family:the knee | 9.6% (+5.5%; 7) | 13.7% (+8.5%; 7) | 21.7% (-15.2%; 7) | 3.9% (-1.5%; 7) | 3.2% (-0.6%; 7) | 17.7% (+12.6%; 7) |
| fmt:fp16 | 3.0% (+0.0%; 8) | 5.6% (+2.0%; 8) | 16.3% (-13.9%; 8) | - | - | - |
| fmt:fp32 | 9.1% (+4.0%; 19) | 10.9% (+5.8%; 19) | 18.2% (-8.5%; 19) | - | - | - |
| fmt:int8 | 5.9% (+3.0%; 14) | 8.4% (+4.7%; 14) | 19.1% (-10.5%; 14) | - | - | - |
| kind:ones | - | - | - | 4.4% (-1.7%; 3) | - | - |
| kind:random | - | - | - | 5.5% (-3.0%; 32) | 5.8% (-3.1%; 32) | 89.7% (+48.9%; 32) |
| kind:real | - | - | - | 6.5% (-6.4%; 3) | - | 56.7% (+27.7%; 3) |
| kind:zeros | - | - | - | 4.7% (+1.0%; 7) | 4.7% (+1.0%; 7) | 48.9% (+26.5%; 7) |
| shires:1 | 15.3% (+9.4%; 2) | 17.3% (+17.0%; 2) | 22.3% (+9.8%; 2) | 3.0% (-2.1%; 2) | 6.6% (-6.3%; 2) | 228.5% (+227.8%; 2) |
| shires:16 | 7.3% (-5.7%; 2) | 7.8% (-0.6%; 2) | 24.2% (-21.3%; 2) | 5.8% (-4.0%; 2) | 5.5% (-3.6%; 2) | 35.4% (+29.1%; 2) |
| shires:32 | 6.7% (+3.0%; 32) | 7.9% (+3.4%; 32) | 17.1% (-11.2%; 32) | 5.7% (-2.4%; 36) | 5.5% (-1.5%; 30) | 43.2% (+18.3%; 33) |
| shires:4 | 6.1% (+4.0%; 4) | 13.3% (+9.9%; 4) | 20.8% (-6.4%; 4) | 3.3% (-2.7%; 4) | 6.0% (-5.7%; 4) | 166.2% (+161.8%; 4) |
| shires:8 | 0.8% (-0.8%; 1) | 10.9% (+10.9%; 1) | 13.2% (-13.2%; 1) | 2.1% (-2.1%; 1) | 2.8% (-2.8%; 1) | 70.2% (+70.2%; 1) |

**MM1-v1's own cells at MM1-v2's bands** (REPORTED, never verdicts; computed by this lane after the scorer from its figures, MM1-v1 at each run's measured clock, by the registered cell rule): T1m 37 of 41 (PASS at MM1-v2's 19%); T2m 34 of 41 (FAIL at MM1-v2's 19%); T3m 37 of 41 (PASS at MM1-v2's 19%); E1 39 of 39 (PASS at MM1-v2's 14%); E2m 37 of 39 (PASS at MM1-v2's 15%); E3 37 of 39 (PASS at MM1-v2's 5%); E4m 34 of 39 (FAIL at MM1-v2's 13%). So at MM1-v2's bands MM1-v1 would pass 5 of these 7 rules: as the registration said before the data, the bands hold MM1-v1 too at most cases.

**F1@800 against F2@800 on J over idle** (REPORTED; post hoc, this lane, both as frozen, the tie 0.01 in ln): F1@800 closer at 33 points, F2@800 at 9, 0 ties, over the 42 both price; rms 55.38% against 82.21%.

**The scorer's readings (e)-(j)** are in `scored-e209.json` (`readings_REPORTED`; REPORTED, never verdicts); (a)-(d) are in note 15 section 4. Reading (e), the timing simulation against the card: a minion's measured cycles a GEMM run 21.1 to 44.0 times the simulator's instruction count for it (median 30.2; the simulator counts one step an instruction, not time), and the counter's mean runs 1.78 to 6.95 times the tensor unit's measured floor (median 3.18), over 45 points. Reading (h): the day's replicate spread of W over idle over the 9 points read twice for energy is 0.299 W (the registered SD_rep 0.173 W).

## 6. NO DATA, not compared and the flags, named (the card-lane brief's step-13 line; E209.md A1 item 2)

> **Such a point is NO DATA in every rule** (section 7's heading: never a failure), **and the kit's step 13 names it** for the day's note, beside every point with no kept run (it did not run, or every run was set aside) and every point with a time reading but no energy reading (capped or thin).

- **Step 13's readings name none** (`post.out`): no point without a kept run, none with kept runs but no time reading, none with a time reading but no energy reading. All 45 points ran (62 of 62 runs), each with a kept run, a time reading and an energy reading.
- **Route c's NO DATA:** e44 in E2c and E4c (MM1-v2 forecast it capped, so route c forecasts no energy reading there; E209.md section 5). Hence 44 scored points in those two rules. It is scored in E1, E2m, E3 and E4m.
- **Not compared by registration:** H4 reads the 39 points MM1-v1 prices; it prices none of e05, e22, e34, e35, e36, e37 (the ones and real tiles; NOT FORECAST). H6 reads the 42 points F2@800 prices; it prices none of e05, e22, e37 (the ones tile). F1@800 prices the same 42 for energy.
- **The flags** (the scorer's output; E209.md section 7: "every flag (STEP, NO STEP, CAPPED, set aside, did not run) is listed"): run 56 of e07: STEP and CAPPED (its time read, its energy not: the reducer's rule; e07's other run carries the point's energy). No run is flagged NO STEP, set aside or did not run.

## 7. The findings, answered as dated clauses (Tue 17 Nov 2026, PST)

- **verify-e209d's finding 1 (low): the frozen scorer does not compute readings (a)-(d).** Answered by note 15 section 4 (`b067742b`, 13:56:32), with erratum 1 (`d4bd2425`, 14:01:32: e30's measured over MM1-v2 reads 1.015). Note 15 computed them from the two step-13 files that this commit adds; with them here, its reproduce line runs in this directory and gives its committed printout and JSON byte for byte (section 2).
- **verify-e209d's finding 2 (low): H1-H3's REPORTED side readings must be printed beside 'MM1-v2 BETTER'.** Answered by note 15 section 3 (with erratum 1) and again in section 4 above, beside every head-to-head, from the scorer's own JSON.
- **verify-e209d's findings 3-6 (info: the live view's 'held' spans before T0, blindness, the stop lines, the governor's two misses).** Answered by note 15 sections 6 and 7. The live collector's match by inode alone is lab tooling, not E209: it is left to the orchestrator and nothing of it is changed here.
- **The data lane's findings** (`collect-e209`): SHA256SUMS lists README.md and was made again after the README's notes (README note 12); README items 10-14 use a three-space continuation indent, which may render item 11's two bullets after the item on GitHub (left as committed: this note adds files only); the README's opening line names `collect_e209.py`, and note 10 says the directory was written by `collect_e209_n1.py`.
- **The card lane's departure** (steps 4 and 5 in the other order, on the day's newly made box folder): README note 3 and kit note 1 section 4.
- **The data verifier's question to the orchestrator** (where readings (a)-(d) go): answered by fix-e209d's note 15.
- **fix-e209d's open item for this lane:** step 13's `scored-e209.json` (`3e53bb3e...`) and `data-e209.json` (`90bc84ab...`) are committed byte for byte under those names, this note is numbered 16, and note 15 section 3 with erratum 1 is cited beside H1-H3 (section 4). Done here.
- **The card-lane brief's line for step 13** ("A later lane commits the outputs byte for byte and names the NO DATA points in its note"): the outputs are section 1's seven files; the NO DATA points are named in section 6.

## 8. What this note does not change

No committed file is edited. No rule, band, tie, forecast, label or verdict is changed; the scorer is not re-run for a verdict, and nothing is re-scored. The registered verdicts are the frozen scorer's, as printed at step 13 and quoted above. The model session's sealed forecast for E209 (registered as REPORTED in `d6d62660`: posted after the session and before the data commit) is neither read nor scored here, and no number of it is in this note.

## 9. Reproduce

From the lab's top, with this directory committed (`DD=docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2`, `X` any folder):

```
python3 -I -B tools/claims-v3/e208/proposal/src/reduce_mms.py $DD/session --out X/data-e209.json --txt X/reduce-e209.txt > X/reduce.out 2>&1
python3 -I -B tools/claims-v3/e209/rb/post_e209.py labels $DD/ranbefore-e209.json
OMP_NUM_THREADS=1 python3 -I -B tools/claims-v3/e209/score_e209.py X/data-e209.json --out X/scored-e209.json > X/score.out 2>&1
python3 -I -B tools/claims-v3/e209/rb/post_e209.py after X/data-e209.json X/scored-e209.json --out X/post-e209.json > X/post.out 2>&1
```

Under `/usr/bin/python3` 3.12.3 each writes its files byte for byte as committed here (this lane ran the four calls at `ea3fa3ce` and at `d4bd2425`). The kit's own form is `RB_OUT=... bash tools/claims-v3/e209/rb/s24_score_e209_n1.sh` (kit note 1 section 3). `sha256sum -c SHA256SUMS-note16` in this directory checks the files of section 1.

