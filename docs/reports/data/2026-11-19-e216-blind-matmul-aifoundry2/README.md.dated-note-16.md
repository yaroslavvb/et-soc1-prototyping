# E216 data, dated note 16: the frozen scorer's outputs, committed beside the data byte for byte (Thu 19 Nov 2026, PST)

*Dated Thu 19 Nov 2026 (week 47), PST, after the data; written by the lane `scores-e216` (round Q227) at the desk on aifoundry2 under `/usr/bin/python3` 3.12.3 (`-I -B`), every numerical step single-threaded inside the round's CPU slots. This note adds new files only: no committed file changes and nothing is re-scored. **Labels:** the scorer's verdicts are **BLIND** (every forecast E216 scores was frozen by its registration `1e3e02b0`, pushed 15:32:32 PST, before the day's first card command at 16:55:55 PST); everything marked REPORTED is a reading, never a verdict; the re-derivations named are **desk** checks.*

## 1. The files this note adds

Eleven new files beside the data commit `a8ce142d`'s 248. The first nine are runbook step 13's outputs, copied byte for byte from the card lane's run folder:

| file | what | sha256 | label |
|---|---|---|---|
| `data-e216.json` | E208's registered reducer (`tools/claims-v3/e208/proposal/src/reduce_mms.py` `b9e32618...`, with its `mms_common.py` `c3fc7883...`) on `session/`: every run's views, E216.md section 7's measured side | `bd2ea4b3a65f38af...` | measured (reduced) |
| `reduce-e216.txt` | the reducer's table of the runs | `d9d38b00db9714a2...` | measured (reduced) |
| `reduce.out` | the reducer's printed lines (the same bytes as `reduce-e216.txt`) | `d9d38b00db9714a2...` | printed lines |
| `scored-e216.json` | the frozen scorer `tools/claims-v3/e216/score_e216.py` (`9c61d06c...`): every rule, every head-to-head and the pair rule, every point's route-c figures and cells, the flags | `e77ed255b9000252...` | BLIND (the other models' cells REPORTED) |
| `score.out` | the scorer's printed lines | `eadb2fbd42d82c16...` | printed lines |
| `post-e216.json`, `post.out` | `rb/post_e216.py after`: the points left NO DATA, named by family, and the session's stop | `c44d42058664100e...`, `9d1a4eb7e889f98f...` | REPORTED |
| `reported-e216.json`, `reported.out` | `report_e216.py`: Amendment 1's A2 (T1-T3 and E1-E4 without family G and with G alone) and A4 (the head-to-heads by distinct configuration) | `4095141ad89ac15c...`, `72dc405575ae9673...` | REPORTED |
| `README.md.dated-note-16.md` | this note | - | dated note |
| `SHA256SUMS-note16` | the ten files above it, then `README.md` and `SHA256SUMS` as the data commit holds them (12 lines) | - | - |

## 2. Where they come from: step 13 on the data commit (this lane's desk checks)

- **The step.** The card lane `card-e216` ran `tools/claims-v3/e216/rb/s24_score_e216.sh` (the kit's list `e4601f6f...`) inside a CPU slot after the data commit, as the card-lane brief's row 13 says (the round's slot log: one job, 17:30:23-17:30:24 PST, rc 0). Its runbook log holds exactly two step-13 lines: start 17:30:23 PST and exit 0 at 17:30:24 PST, between the collection (exit 0 at 17:23:52) and the lane's end.
- **The commit it read.** `a8ce142d` was committed at 17:30:00 PST and pushed by 17:30:05 (the lab clone's push record). The lab clone's HEAD was `a8ce142d` from 17:30:00 until its next commit at 17:31:16 PST, so the whole step ran on it, and it printed so: "the data commit a8ce142d1108 (2026-11-19 17:30:00 -0800); HEAD a8ce142d1". E216's data directory and its kit folder are unchanged from `a8ce142d` to this note's parent (trees `12db6bee` and `9c4f9c48`).
- **The bytes.** The nine files were written 17:30:24.5-17:30:24.8 PST, and their sha256 equal the ones the card lane reported. `reduce.out` equals `reduce-e216.txt` byte for byte: the reducer prints the table it writes.
- **The programs, at their pins** (at `a8ce142d` and at HEAD alike): the scorer `score_e216.py` `9c61d06c` (E216.md section 0, and the registration's list); its three pinned inputs `points-e216.json` `63899cae`, `forecast-e216.json` `92c9444a` and `rules-e216.json` `c6a8f10c`; `report_e216.py` `fe76f9b9`; `rb/post_e216.py` `12ed308c`, `rb/s24_score_e216.sh` `e4601f6f`, `rb/rb_e216.sh` `05d4139e` and `collect_e216.py` `7f1a852b` (the kit's list); E208's `reduce_mms.py` `b9e32618` and `mms_common.py` `c3fc7883` (E216.md section 7). `sha256sum -c` reads `SHA256SUMS-e216-registration` 40 of 40 and `SHA256SUMS-e216-kit` 58 of 58.
- **The labels.** `ranbefore-e216.json` (committed beside the data) names no point, so the scorer ran without `--labels`, and `scored-e216.json` reads `labels_applied` [] and `other_runs` [].
- **Made again.** This lane ran step 13's calls again, unchanged, on two trees exported from the lab clone's own objects: one at `a8ce142d`, and one at HEAD `1c446c93`, which `git ls-remote` read equal to the remote's main at 18:20 PST. Each ran in a CPU slot, and all nine outputs came out byte for byte equal in both. The frozen scorer's `score()`, called in process on `data-e216.json` and written as its `main()` writes it, gives `scored-e216.json` byte for byte. verify-e216d made step 13 again on the committed bytes on its own, and its nine outputs are byte-equal too.

**The step's own printed lines** (the card lane's capture; the scorer's, the readings' and Amendment 1's lines followed, and they are `score.out`, `post.out` and `reported.out` byte for byte):

```
== s24_score_e216 2026-11-19 17:30:23 PST (aifoundry2; s24_score_e216.sh)
MANIFEST CHECK: 236 of 236 manifest lines OK (1 by THE MASK of E209's kit note 1 (E216's kit): first/fwgate-aifoundry2-c0-20261119-165555.json line 34 (the box's bytes 5204a9adc5eb1494... = its manifest line; committed 9b49fec575adabe5...))
the data commit a8ce142d1108 (2026-11-19 17:30:00 -0800); HEAD a8ce142d1
reduce_mms.py rc 0
LABELS OK: 0 point(s) labelled ran before (none)
score_e216.py rc 0
```

**The scorer's printed lines** (`score.out`, all of it):

```
R0 PASS {}
T1 FAIL {'n': 40, 'pass': 29, 'need': 36}
T2 PASS {'n': 40, 'pass': 36, 'need': 36}
T3 FAIL {'n': 40, 'pass': 29, 'need': 36}
E1 FAIL {'n': 40, 'pass': 35, 'need': 36}
E2 FAIL {'n': 40, 'pass': 34, 'need': 36}
E3 FAIL {'n': 40, 'pass': 35, 'need': 36}
E4 FAIL {'n': 40, 'pass': 34, 'need': 36}
T1-twins TOO FEW {'n': 6, 'pass': 5}
T2-twins TOO FEW {'n': 6, 'pass': 6}
T3-twins TOO FEW {'n': 6, 'pass': 5}
E1-twins TOO FEW {'n': 6, 'pass': 6}
E2-twins TOO FEW {'n': 6, 'pass': 6}
E3-twins TOO FEW {'n': 6, 'pass': 6}
E4-twins TOO FEW {'n': 6, 'pass': 6}
P1 FAIL {'decided': 6, 'ordered_right': 1}
H1t MM1-v3 BETTER 2/12/26 p 0.012939453125
H1w TOO FEW 0/0/40 p 1.0
H1t-twins TOO FEW 1/5/0 p 0.21875
H1w-twins TOO FEW 0/0/6 p 1.0
H2w NOT DECIDED 5/5/0 p 1.0
H2f NOT DECIDED 5/5/0 p 1.0
H3 NOT DECIDED 5/5/6 p 1.0
H4 NOT DECIDED 10/10/20 p 1.0
H2j NOT DECIDED 5/5/0 p 1.0
```

## 3. The registered rules' words, and the verdicts (BLIND)

Quoted from `E216.md` (section 7 unless named) and `E216-amendment-1.md`, both pinned in `SHA256SUMS-e216-registration`:

- **The answer:** "The registered answer is the registered points' (G, Gt, Y and F's new points); F's card-transfer twins are scored by the same rules and reported apart." (section 1)
- **The measured side:** "Per run, in its primary view (`win`): the clock `kclock_mhz`; cycles an op, the wall `cyc_op_max`; the counter's mean `cyc_op_mean`; seconds a GEMM `t_pass_s`; the op time `T_op_us`; W over idle `dP_w`; J over idle `J_pass_over`; J with the card at rest `J_pass_with`; the rest = p_mean - dP." "A capped or thin run carries no energy (the reducer's rule)." "A point is the mean of its kept runs (route c); a time case is its point."
- **The routes:** "Route c (registered): a run whose view clock reads 790-810 MHz with no step inside its busy window (E209's STEP test) and not NO STEP, scored against the frozen 799.0 MHz column." "Route m (REPORTED): every other run, against the frozen column nearest its view clock (700 or 600 MHz), flagged."
- **MM1-v3.1's per-point rules:** "each point passes when |measured / forecast - 1| is within its band; a rule PASSES with at least 90% of its scored points, FAIL otherwise, TOO FEW under 10, NO DATA with none". "The band is twice the larger of MM1-v3.1's two held-out rms errors without configuration twins". "Points under about 3 W over idle are scored in watts in E1 and E2" (no E216 point is: every one reads more than 3 W over idle).
- **R0:** "every check of C of the day exact or approx (every point run's and anchor's) and the smoke good (rc 0, its check exact or approx); a FAIL labels every other verdict."
- **The head-to-heads:** "per case d = |ln(measured / second)| - |ln(measured / first)|, decided when |d| exceeds the tie; the exact two-sided sign test over the decided: FIRST BETTER or SECOND BETTER at p < 0.05 with at least 10 decided (8 for H2w and H2f: family G holds 10 points; at 8 decided only 8 of 8 decides, p 0.008), NOT DECIDED otherwise, TOO FEW under that minimum, NO DATA with none"; the ties: "cycles and seconds 0.005 in ln, W over idle and joules 0.01 in ln, watts points 0.1 W". **H1t** "MM1-v3.1 vs MM1-v3, wall cycles, every registered point"; **H1w** "the same, W over idle given the measured op time (each model's A + B / T_op)"; **H2w** "'v3.1 + gemmLnc term' vs MM1-v3.1 on family G, W over idle given t" (**H2j** "is the same test: both models are given the same measured seconds"); **H2f** "the same pair, J over idle with the seconds forecast"; **H3** "'v3.1 + contention' vs MM1-v3.1 on family Y, wall cycles"; **H4** "'v3.1 + both terms' vs MM1-v3.1 over every registered point (wall cycles at Y, W over idle given t at G; every other point a tie by construction)".
- **The twins apart:** "H1t-twins and H1w-twins, and the per-point rules on the six twins (T1-twins ... E4-twins), never part of the answer."
- **The pair rule (P1):** "of the Y pairs whose measured within-pair difference |ln(wall a / wall b)| (each point's route-c mean) exceeds" 0.0077 in ln, "the share that 'v3.1 + contention' orders right (its predicted sign equals the measured sign); MM1-v3.1 prices every pair alike and orders none (a tie)." PASS "when at least 5 pairs are decided, more than half are ordered right, and the one-sided exact binomial p (k of m at 1/2) is at most 0.05 (for 5 decided: 5 right; for 6: 6 right; for 8: 7 or more)"; FAIL "when at least 5 are decided and that does not hold; TOO FEW under 5; NO DATA with none." "The two control pairs enter the rule like the others (their predicted difference is small, so their sign is the term's weakest claim)." Amendment 1, A1: "the minimum was 4, and 4 of 4 (p 0.0625) could only read FAIL; 4 or fewer decided pairs now read TOO FEW."
- **What a P1 FAIL means, registered before the data** (Amendment 1, A9): "A FAIL (pairs separated but misordered, or a control separated) contradicts both the term and that reading." (that reading is verify-lay's count-only reading of the contention term). Section 8: "a control that the card separates beyond the threshold counts against the term (it cannot order a pair it calls equal)."

| rule | what it scores | band | verdict | points in band (needed) | MM1-v3.1's points out of band (measured / forecast - 1, %) |
|---|---|---|---|---|---|
| R0 | the checks | - | **PASS** | 67 checks of C (61 approx, 6 exact), not one other; 3 smoke records good (exact) | - |
| T1 | cycles an op, the wall | 10% | **FAIL** | 29 of 40 (36) | g01 -11.62, g07 -14.09, g08 -14.17, g09 -14.12, g10 -13.71, y01a +12.98, y05a -10.25, y05b -10.49, y06a -10.36, y06b -10.68, f09 -11.24 |
| T2 | cycles an op, the counter's mean | 13% | **PASS** | 36 of 40 (36) | g07 -13.16, g08 -13.23, g09 -13.19, y04a +18.51 |
| T3 | seconds a GEMM (T1's bases) | 10% | **FAIL** | 29 of 40 (36) | g01 -11.62, g07 -14.11, g08 -14.17, g09 -14.14, g10 -13.72, y01a +12.95, y05a -10.26, y05b -10.50, y06a -10.37, y06b -10.68, f09 -11.24 |
| E1 | J over idle given the measured op time and seconds | 11% | **FAIL** | 35 of 40 (36) | g02 +17.23, g03 +15.50, g04 +16.10, g05 +17.09, g06 +16.97 |
| E2 | J over idle with the seconds forecast | 13% | **FAIL** | 34 of 40 (36) | g02 +15.38, g03 +13.53, g04 +14.16, g05 +15.10, g06 +15.05, y01a +14.36 |
| E3 | J with the card at rest given t (the measured rest x t + E1's J) | 5% | **FAIL** | 35 of 40 (36) | g02 +10.27, g03 +9.31, g04 +9.65, g05 +10.23, g06 +10.14 |
| E4 | J with the card at rest with the seconds forecast (the measured rest) | 10% | **FAIL** | 34 of 40 (36) | y01a +13.34, y05a -10.08, y05b -10.75, y06a -10.25, y06b -11.01, f09 -10.28 |
| T1-twins | the same, on the six twins (apart) | 10% | TOO FEW | 5 of 6 | f06 +13.35 |
| T2-twins | the same, on the six twins (apart) | 13% | TOO FEW | 6 of 6 | none |
| T3-twins | the same, on the six twins (apart) | 10% | TOO FEW | 5 of 6 | f06 +13.34 |
| E1-twins | the same, on the six twins (apart) | 11% | TOO FEW | 6 of 6 | none |
| E2-twins | the same, on the six twins (apart) | 13% | TOO FEW | 6 of 6 | none |
| E3-twins | the same, on the six twins (apart) | 5% | TOO FEW | 6 of 6 | none |
| E4-twins | the same, on the six twins (apart) | 10% | TOO FEW | 6 of 6 | none |
| P1 | the pair rule | 0.0077 ln | **FAIL** | 6 of 8 pairs decided, 1 ordered right (share 0.167; one-sided p 0.9844) | section 6 |

| head-to-head | first vs second | on | verdict | first closer / second closer / ties | p (two-sided) | decided needed |
|---|---|---|---|---|---|---|
| H1t | MM1-v3.1 vs MM1-v3 | the 40 registered points | **MM1-v3 BETTER** | 2 / 12 / 26 | 0.01294 | 10 |
| H1w | MM1-v3.1 vs MM1-v3 | the 40 registered points | **TOO FEW** | 0 / 0 / 40 | 1 | 10 |
| H2w | v3.1+lnc vs MM1-v3.1 | family G (10) | **NOT DECIDED** | 5 / 5 / 0 | 1 | 8 |
| H2j | v3.1+lnc vs MM1-v3.1 | family G (10) | **NOT DECIDED** | 5 / 5 / 0 | 1 | 8 |
| H2f | v3.1+lnc vs MM1-v3.1 | family G (10) | **NOT DECIDED** | 5 / 5 / 0 | 1 | 8 |
| H3 | v3.1+contention vs MM1-v3.1 | family Y (16) | **NOT DECIDED** | 5 / 5 / 6 | 1 | 10 |
| H4 | v3.1+both vs MM1-v3.1 | the 40 registered points | **NOT DECIDED** | 10 / 10 / 20 | 1 | 10 |
| H1t-twins | MM1-v3.1 vs MM1-v3 | the 6 twins (apart) | **TOO FEW** | 1 / 5 / 0 | 0.2188 | 10 |
| H1w-twins | MM1-v3.1 vs MM1-v3 | the 6 twins (apart) | **TOO FEW** | 0 / 0 / 6 | 1 | 10 |

## 4. MM1-v3.1 point by point (the scorer's cells)

Measured / forecast - 1 in %, bold where out of its band; route c, the 799.0 MHz column. The cycle columns are the timing that MM1-v3.1 prints, its cycles an op on the wall (the slowest minion) and the counter's mean, beside the card's. W over idle given t is MM1-v3.1's A + B / T_op at the point's measured op time, and E1 is that times the measured seconds. Runs: one a point, but two for every Y point other than y04b, whose second run is route m (section 11).

| point | family | GEMM | wall: measured / MM1-v3.1 | T1 | counter: measured / MM1-v3.1 | T2 | T3 | W over idle: measured / given t | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | G | `gemmLnc1x2x12` fp32, mask 0xffffffff | 1,560.1 / 1,765.2 | **-11.62** | 1,560.0 / 1,746.0 | -10.65 | **-11.62** | 36.24 / 34.01 W | +6.54 | +3.46 | +3.98 | -2.79 |
| g02 | G | `gemmLnc2x2x12` fp32, mask 0xffffffff | 1,677.5 / 1,789.8 | -6.28 | 1,659.1 / 1,770.4 | -6.29 | -6.30 | 37.81 / 32.25 W | **+17.23** | **+15.38** | **+10.27** | +6.37 |
| g03 | G | `gemmLnc4x2x12` fp32, mask 0xffffffff | 1,668.1 / 1,789.8 | -6.81 | 1,655.3 / 1,770.4 | -6.50 | -6.82 | 37.41 / 32.39 W | **+15.50** | **+13.53** | **+9.31** | +5.14 |
| g04 | G | `gemmLnc5x2x12` fp32, mask 0xffffffff | 1,671.0 / 1,789.8 | -6.64 | 1,654.0 / 1,770.4 | -6.57 | -6.65 | 37.55 / 32.35 W | **+16.10** | **+14.16** | **+9.65** | +5.56 |
| g05 | G | `gemmLnc6x2x12` fp32, mask 0xffffffff | 1,669.2 / 1,789.8 | -6.74 | 1,652.9 / 1,770.4 | -6.64 | -6.76 | 37.91 / 32.38 W | **+17.09** | **+15.10** | **+10.23** | +6.05 |
| g06 | G | `gemmLnc7x2x12` fp32, mask 0xffffffff | 1,673.1 / 1,789.8 | -6.52 | 1,659.3 / 1,770.4 | -6.28 | -6.54 | 37.80 / 32.32 W | **+16.97** | **+15.05** | **+10.14** | +6.10 |
| g07 | G | `gemmLnc3x5x10` fp32, mask 0xffffffff | 1,449.6 / 1,687.5 | **-14.09** | 1,449.4 / 1,669.1 | **-13.16** | **-14.11** | 37.77 / 36.07 W | +4.72 | +1.17 | +2.99 | -4.86 |
| g08 | G | `gemmLnc4x5x10` fp32, mask 0xffffffff | 1,448.4 / 1,687.5 | **-14.17** | 1,448.3 / 1,669.1 | **-13.23** | **-14.17** | 37.95 / 36.09 W | +5.14 | +1.57 | +3.25 | -4.68 |
| g09 | G | `gemmLnc5x5x10` fp32, mask 0xffffffff | 1,449.2 / 1,687.5 | **-14.12** | 1,449.0 / 1,669.1 | **-13.19** | **-14.14** | 38.05 / 36.08 W | +5.45 | +1.87 | +3.43 | -4.51 |
| g10 | G | `gemmLnc6x5x10` fp32, mask 0xffffffff | 1,456.2 / 1,687.5 | **-13.71** | 1,456.0 / 1,669.1 | -12.77 | **-13.72** | 37.83 / 35.94 W | +5.25 | +1.78 | +3.29 | -4.43 |
| g01t | Gt | `gemmL1x2x12` fp32, mask 0xffffffff | 1,728.4 / 1,781.1 | -2.96 | 1,728.3 / 1,761.7 | -1.89 | -2.96 | 29.49 / 31.48 W | -6.33 | -7.02 | -3.77 | -5.36 |
| g02t | Gt | `gemmL2x2x12` fp32, mask 0xffffffff | 1,806.8 / 1,805.7 | +0.06 | 1,806.7 / 1,786.1 | +1.15 | +0.03 | 28.74 / 30.52 W | -5.83 | -5.82 | -3.43 | -3.41 |
| g03t | Gt | `gemmL4x2x12` fp32, mask 0xffffffff | 1,801.6 / 1,805.7 | -0.23 | 1,801.5 / 1,786.1 | +0.86 | -0.24 | 29.03 / 30.59 W | -5.09 | -5.15 | -3.00 | -3.13 |
| g04t | Gt | `gemmL5x2x12` fp32, mask 0xffffffff | 1,806.8 / 1,805.7 | +0.06 | 1,806.7 / 1,786.1 | +1.16 | +0.05 | 28.73 / 30.52 W | -5.87 | -5.86 | -3.45 | -3.42 |
| g05t | Gt | `gemmL6x2x12` fp32, mask 0xffffffff | 1,797.7 / 1,805.7 | -0.44 | 1,797.6 / 1,786.1 | +0.65 | -0.46 | 28.75 / 30.64 W | -6.15 | -6.26 | -3.63 | -3.88 |
| g06t | Gt | `gemmL7x2x12` fp32, mask 0xffffffff | 1,805.5 / 1,805.7 | -0.01 | 1,805.4 / 1,786.1 | +1.08 | -0.03 | 28.94 / 30.54 W | -5.23 | -5.24 | -3.07 | -3.09 |
| g07t | Gt | `gemmL3x5x10` fp32, mask 0xffffffff | 1,633.0 / 1,706.6 | -4.31 | 1,632.8 / 1,688.0 | -3.27 | -4.31 | 30.53 / 32.91 W | -7.24 | -8.21 | -4.40 | -6.65 |
| g08t | Gt | `gemmL4x5x10` fp32, mask 0xffffffff | 1,641.7 / 1,706.6 | -3.80 | 1,641.6 / 1,688.0 | -2.75 | -3.81 | 30.96 / 32.78 W | -5.55 | -6.42 | -3.37 | -5.38 |
| g09t | Gt | `gemmL5x5x10` fp32, mask 0xffffffff | 1,640.2 / 1,706.6 | -3.89 | 1,640.0 / 1,688.0 | -2.84 | -3.90 | 30.21 / 32.80 W | -7.88 | -8.75 | -4.78 | -6.80 |
| g10t | Gt | `gemmL6x5x10` fp32, mask 0xffffffff | 1,638.0 / 1,706.6 | -4.02 | 1,637.9 / 1,688.0 | -2.97 | -4.03 | 30.52 / 32.83 W | -7.06 | -7.96 | -4.29 | -6.39 |
| y01a | Y | `gemmL1x8x8` fp32, mask 0x3 | 1,767.4 / 1,564.3 | **+12.98** | 1,690.8 / 1,547.3 | +9.27 | **+12.95** | 8.28 / 7.99 W | +3.62 | **+14.36** | +0.99 | **+13.34** |
| y01b | Y | `gemmL1x8x8` fp32, mask 0x10001 | 1,644.5 / 1,564.3 | +5.12 | 1,644.5 / 1,547.3 | +6.28 | +5.12 | 7.94 / 8.10 W | -2.01 | +2.00 | -0.55 | +4.25 |
| y02a | Y | `gemmL1x8x12` fp32, mask 0x3 | 1,768.4 / 1,774.0 | -0.32 | 1,692.4 / 1,754.7 | -3.55 | -0.34 | 8.25 / 8.03 W | +2.71 | +2.42 | +0.75 | +0.42 |
| y02b | Y | `gemmL1x8x12` fp32, mask 0x10001 | 1,651.7 / 1,774.0 | -6.89 | 1,651.7 / 1,754.7 | -5.87 | -6.91 | 8.05 / 8.14 W | -1.12 | -6.69 | -0.31 | -6.85 |
| y03a | Y | `gemmL1x4x16` fp32, mask 0x3 | 1,787.0 / 1,791.9 | -0.27 | 1,738.6 / 1,772.4 | -1.91 | -0.30 | 8.22 / 8.02 W | +2.52 | +2.26 | +0.69 | +0.40 |
| y03b | Y | `gemmL1x4x16` fp32, mask 0x10001 | 1,716.3 / 1,791.9 | -4.22 | 1,716.3 / 1,772.4 | -3.17 | -4.25 | 8.06 / 8.08 W | -0.29 | -3.75 | -0.08 | -4.11 |
| y04a | Y | `gemmL4x2x16` fp32, mask 0xf | 1,662.3 / 1,721.1 | -3.42 | 1,662.3 / 1,402.7 | **+18.51** | -3.42 | 9.21 / 9.75 W | -5.50 | -7.72 | -1.73 | -4.77 |
| y04b | Y | `gemmL4x2x16` fp32, mask 0x33 | 1,740.1 / 1,721.1 | +1.10 | 1,740.1 / 1,702.3 | +2.22 | +1.08 | 9.55 / 9.61 W | -0.69 | +0.05 | -0.21 | +0.76 |
| y05a | Y | `gemmL2x8x16` fp32, mask 0x5555 | 1,636.4 / 1,823.3 | **-10.25** | 1,636.4 / 1,803.5 | -9.26 | **-10.26** | 12.62 / 13.22 W | -4.50 | -9.79 | -1.73 | **-10.08** |
| y05b | Y | `gemmL2x8x16` fp32, mask 0x11111111 | 1,632.0 / 1,823.3 | **-10.49** | 1,632.0 / 1,803.5 | -9.51 | **-10.50** | 12.46 / 13.24 W | -5.82 | -11.16 | -2.24 | **-10.75** |
| y06a | Y | `gemmL4x8x16` fp32, mask 0x5555 | 1,634.4 / 1,823.3 | **-10.36** | 1,634.3 / 1,803.5 | -9.38 | **-10.37** | 12.60 / 13.23 W | -4.73 | -10.06 | -1.82 | **-10.25** |
| y06b | Y | `gemmL4x8x16` fp32, mask 0x11111111 | 1,628.6 / 1,823.3 | **-10.68** | 1,628.6 / 1,803.5 | -9.70 | **-10.68** | 12.43 / 13.25 W | -6.15 | -11.56 | -2.37 | **-11.01** |
| y07a | Y | `gemmL1x4x24` fp32, mask 0x101 | 1,915.3 / 1,830.0 | +4.66 | 1,915.3 / 1,810.1 | +5.81 | +4.63 | 8.01 / 7.94 W | +0.87 | +4.69 | +0.24 | +4.65 |
| y07b | Y | `gemmL1x4x24` fp32, mask 0x10001 | 1,847.6 / 1,830.0 | +0.96 | 1,847.6 / 1,810.1 | +2.07 | +0.94 | 8.12 / 7.99 W | +1.65 | +2.43 | +0.45 | +1.34 |
| y08a | Y | `gemmL1x8x24` fp32, mask 0x101 | 1,915.7 / 1,830.1 | +4.68 | 1,915.7 / 1,810.2 | +5.83 | +4.67 | 7.94 / 7.94 W | -0.02 | +3.80 | -0.01 | +4.43 |
| y08b | Y | `gemmL1x8x24` fp32, mask 0x10001 | 1,836.9 / 1,830.1 | +0.37 | 1,836.9 / 1,810.2 | +1.48 | +0.35 | 8.00 / 8.00 W | -0.02 | +0.26 | -0.01 | +0.32 |
| f07 | F (new) | `gemmL1x15x3` fp16, mask 0xffffffff | 1,334.3 / 1,464.5 | -8.89 | 1,316.9 / 1,448.6 | -9.09 | -8.92 | 34.12 / 36.47 W | -6.43 | -8.32 | -4.06 | -8.55 |
| f08 | F (new) | `gemmL1x14x3` fp16, mask 0xffffffff | 1,333.1 / 1,444.8 | -7.74 | 1,315.6 / 1,429.1 | -7.94 | -7.75 | 34.08 / 36.44 W | -6.48 | -8.11 | -4.09 | -7.97 |
| f09 | F (new) | `gemmL1x13x4` int8, mask 0xffffffff | 1,338.6 / 1,508.1 | **-11.24** | 1,319.2 / 1,491.7 | -11.56 | **-11.24** | 19.84 / 20.88 W | -4.97 | -9.21 | -2.46 | **-10.28** |
| f10 | F (new) | `gemmL2x14x3` fp32, mask 0xffffffff | 1,352.1 / 1,492.8 | -9.43 | 1,351.9 / 1,476.6 | -8.45 | -9.44 | 35.31 / 38.02 W | -7.12 | -9.04 | -4.55 | -9.19 |
| f01 | F (twin) | `gemmL2x15x2` fp32, mask 0xffffffff | 1,350.2 / 1,423.9 | -5.18 | 1,347.8 / 1,408.4 | -4.30 | -5.18 | 35.65 / 37.96 W | -6.10 | -7.13 | -3.90 | -6.41 |
| f02 | F (twin) | `gemmL3x15x2` fp32, mask 0xffffffff | 1,353.3 / 1,423.9 | -4.96 | 1,350.8 / 1,408.4 | -4.09 | -4.96 | 35.61 / 37.89 W | -6.02 | -7.01 | -3.85 | -6.25 |
| f03 | F (twin) | `gemmL10x15x2` fp32, mask 0xffffffff | 1,351.1 / 1,423.9 | -5.11 | 1,348.6 / 1,408.4 | -4.24 | -5.11 | 35.72 / 37.94 W | -5.84 | -6.86 | -3.76 | -6.22 |
| f04 | F (twin) | `gemmL11x15x2` fp32, mask 0xffffffff | 1,357.2 / 1,423.9 | -4.68 | 1,354.1 / 1,408.4 | -3.85 | -4.69 | 35.93 / 37.80 W | -4.95 | -5.89 | -3.17 | -5.45 |
| f05 | F (twin) | `gemmL12x15x2` fp32, mask 0xffffffff | 1,355.0 / 1,423.9 | -4.84 | 1,352.6 / 1,408.4 | -3.96 | -4.84 | 35.73 / 37.85 W | -5.61 | -6.58 | -3.60 | -5.94 |
| f06 | F (twin) | `gemmL2x1x7` fp32, mask 0xffffffff | 1,735.2 / 1,530.8 | **+13.35** | 1,591.2 / 1,514.1 | +5.09 | **+13.34** | 30.57 / 30.78 W | -0.67 | +2.34 | -0.40 | +6.59 |

## 5. The head-to-heads, case by case (BLIND; the scorer's own loop made again, every tally equal to `scored-e216.json`)

Each case's d = |ln(measured / second)| - |ln(measured / first)|. It reads **first** when d > the tie, **second** when d < -tie, and tie otherwise. The errors are measured / forecast - 1, in %.

**H1, MM1-v3.1 (first) vs MM1-v3 (second).** H1t (wall cycles, tie 0.005): 2 / 12 / 26, p 0.0129, **MM1-v3 BETTER**. H1w (W over idle given t, tie 0.01): 0 / 0 / 40, **TOO FEW**. Every H1w |d| is at most 0.0099, under the tie, as section 1's table registered ("TOO FEW by construction"). The twins, apart: H1t-twins 1/5/0 and H1w-twins 0/0/6, both TOO FEW.

| point | wall measured | MM1-v3.1 | MM1-v3 | errors v3.1 / v3 | d | reads | W measured | MM1-v3.1 given t | MM1-v3 given t | d | reads |
|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | 1,560.1 | 1,765.2 | 1,767.3 | -11.62% / -11.72% | +0.0012 | tie | 36.24 | 34.01 | 33.82 | +0.0058 | tie |
| g02 | 1,677.5 | 1,789.8 | 1,792.9 | -6.28% / -6.44% | +0.0017 | tie | 37.81 | 32.25 | 32.06 | +0.0059 | tie |
| g03 | 1,668.1 | 1,789.8 | 1,792.9 | -6.81% / -6.97% | +0.0017 | tie | 37.41 | 32.39 | 32.20 | +0.0059 | tie |
| g04 | 1,671.0 | 1,789.8 | 1,792.9 | -6.64% / -6.80% | +0.0017 | tie | 37.55 | 32.35 | 32.16 | +0.0059 | tie |
| g05 | 1,669.2 | 1,789.8 | 1,792.9 | -6.74% / -6.90% | +0.0017 | tie | 37.91 | 32.38 | 32.18 | +0.0059 | tie |
| g06 | 1,673.1 | 1,789.8 | 1,792.9 | -6.52% / -6.68% | +0.0017 | tie | 37.80 | 32.32 | 32.13 | +0.0059 | tie |
| g07 | 1,449.6 | 1,687.5 | 1,671.6 | -14.09% / -13.28% | -0.0095 | second | 37.77 | 36.07 | 35.78 | +0.0079 | tie |
| g08 | 1,448.4 | 1,687.5 | 1,671.6 | -14.17% / -13.35% | -0.0095 | second | 37.95 | 36.09 | 35.81 | +0.0079 | tie |
| g09 | 1,449.2 | 1,687.5 | 1,671.6 | -14.12% / -13.30% | -0.0095 | second | 38.05 | 36.08 | 35.79 | +0.0079 | tie |
| g10 | 1,456.2 | 1,687.5 | 1,671.6 | -13.71% / -12.89% | -0.0095 | second | 37.83 | 35.94 | 35.66 | +0.0079 | tie |
| g01t | 1,728.4 | 1,781.1 | 1,783.3 | -2.96% / -3.08% | +0.0013 | tie | 29.49 | 31.48 | 31.32 | -0.0050 | tie |
| g02t | 1,806.8 | 1,805.7 | 1,808.8 | +0.06% / -0.12% | +0.0006 | tie | 28.74 | 30.52 | 30.36 | -0.0053 | tie |
| g03t | 1,801.6 | 1,805.7 | 1,808.8 | -0.23% / -0.40% | +0.0017 | tie | 29.03 | 30.59 | 30.43 | -0.0053 | tie |
| g04t | 1,806.8 | 1,805.7 | 1,808.8 | +0.06% / -0.11% | +0.0005 | tie | 28.73 | 30.52 | 30.36 | -0.0053 | tie |
| g05t | 1,797.7 | 1,805.7 | 1,808.8 | -0.44% / -0.61% | +0.0017 | tie | 28.75 | 30.64 | 30.48 | -0.0053 | tie |
| g06t | 1,805.5 | 1,805.7 | 1,808.8 | -0.01% / -0.19% | +0.0017 | tie | 28.94 | 30.54 | 30.38 | -0.0053 | tie |
| g07t | 1,633.0 | 1,706.6 | 1,690.6 | -4.31% / -3.41% | -0.0094 | second | 30.53 | 32.91 | 32.68 | -0.0070 | tie |
| g08t | 1,641.7 | 1,706.6 | 1,690.6 | -3.80% / -2.89% | -0.0094 | second | 30.96 | 32.78 | 32.55 | -0.0070 | tie |
| g09t | 1,640.2 | 1,706.6 | 1,690.6 | -3.89% / -2.98% | -0.0094 | second | 30.21 | 32.80 | 32.57 | -0.0070 | tie |
| g10t | 1,638.0 | 1,706.6 | 1,690.6 | -4.02% / -3.11% | -0.0094 | second | 30.52 | 32.83 | 32.61 | -0.0070 | tie |
| y01a | 1,767.4 | 1,564.3 | 1,550.7 | +12.98% / +13.98% | +0.0088 | first | 8.28 | 7.99 | 7.92 | +0.0093 | tie |
| y01b | 1,644.5 | 1,564.3 | 1,550.7 | +5.12% / +6.05% | +0.0088 | first | 7.94 | 8.10 | 8.03 | -0.0093 | tie |
| y02a | 1,768.4 | 1,774.0 | 1,775.1 | -0.32% / -0.37% | +0.0006 | tie | 8.25 | 8.03 | 7.96 | +0.0097 | tie |
| y02b | 1,651.7 | 1,774.0 | 1,775.1 | -6.89% / -6.95% | +0.0006 | tie | 8.05 | 8.14 | 8.06 | -0.0098 | tie |
| y03a | 1,787.0 | 1,791.9 | 1,790.6 | -0.27% / -0.20% | -0.0007 | tie | 8.22 | 8.02 | 7.94 | +0.0099 | tie |
| y03b | 1,716.3 | 1,791.9 | 1,790.6 | -4.22% / -4.15% | -0.0007 | tie | 8.06 | 8.08 | 8.00 | +0.0042 | tie |
| y04a | 1,662.3 | 1,721.1 | 1,716.7 | -3.42% / -3.17% | -0.0025 | tie | 9.21 | 9.75 | 9.66 | -0.0094 | tie |
| y04b | 1,740.1 | 1,721.1 | 1,716.7 | +1.10% / +1.36% | +0.0025 | tie | 9.55 | 9.61 | 9.52 | -0.0045 | tie |
| y05a | 1,636.4 | 1,823.3 | 1,828.5 | -10.25% / -10.51% | +0.0029 | tie | 12.62 | 13.22 | 13.11 | -0.0085 | tie |
| y05b | 1,632.0 | 1,823.3 | 1,828.5 | -10.49% / -10.75% | +0.0029 | tie | 12.46 | 13.24 | 13.12 | -0.0085 | tie |
| y06a | 1,634.4 | 1,823.3 | 1,828.5 | -10.36% / -10.62% | +0.0029 | tie | 12.60 | 13.23 | 13.11 | -0.0085 | tie |
| y06b | 1,628.6 | 1,823.3 | 1,828.5 | -10.68% / -10.93% | +0.0029 | tie | 12.43 | 13.25 | 13.14 | -0.0085 | tie |
| y07a | 1,915.3 | 1,830.0 | 1,831.7 | +4.66% / +4.56% | -0.0009 | tie | 8.01 | 7.94 | 7.86 | +0.0099 | tie |
| y07b | 1,847.6 | 1,830.0 | 1,831.7 | +0.96% / +0.87% | -0.0009 | tie | 8.12 | 7.99 | 7.91 | +0.0099 | tie |
| y08a | 1,915.7 | 1,830.1 | 1,832.1 | +4.68% / +4.56% | -0.0011 | tie | 7.94 | 7.94 | 7.86 | +0.0095 | tie |
| y08b | 1,836.9 | 1,830.1 | 1,832.1 | +0.37% / +0.26% | -0.0011 | tie | 8.00 | 8.00 | 7.92 | +0.0095 | tie |
| f07 | 1,334.3 | 1,464.5 | 1,431.5 | -8.89% / -6.79% | -0.0228 | second | 34.12 | 36.47 | 36.35 | -0.0032 | tie |
| f08 | 1,333.1 | 1,444.8 | 1,413.6 | -7.74% / -5.70% | -0.0218 | second | 34.08 | 36.44 | 36.33 | -0.0030 | tie |
| f09 | 1,338.6 | 1,508.1 | 1,477.3 | -11.24% / -9.38% | -0.0206 | second | 19.84 | 20.88 | 20.89 | +0.0005 | tie |
| f10 | 1,352.1 | 1,492.8 | 1,462.2 | -9.43% / -7.53% | -0.0207 | second | 35.31 | 38.02 | 37.78 | -0.0062 | tie |
| f01 (twin) | 1,350.2 | 1,423.9 | 1,404.2 | -5.18% / -3.85% | -0.0139 | second | 35.65 | 37.96 | 37.79 | -0.0044 | tie |
| f02 (twin) | 1,353.3 | 1,423.9 | 1,404.2 | -4.96% / -3.63% | -0.0139 | second | 35.61 | 37.89 | 37.72 | -0.0044 | tie |
| f03 (twin) | 1,351.1 | 1,423.9 | 1,404.2 | -5.11% / -3.78% | -0.0139 | second | 35.72 | 37.94 | 37.77 | -0.0044 | tie |
| f04 (twin) | 1,357.2 | 1,423.9 | 1,404.2 | -4.68% / -3.35% | -0.0139 | second | 35.93 | 37.80 | 37.64 | -0.0044 | tie |
| f05 (twin) | 1,355.0 | 1,423.9 | 1,404.2 | -4.84% / -3.51% | -0.0139 | second | 35.73 | 37.85 | 37.69 | -0.0044 | tie |
| f06 (twin) | 1,735.2 | 1,530.8 | 1,514.1 | +13.35% / +14.61% | +0.0110 | first | 30.57 | 30.78 | 30.68 | -0.0034 | tie |

**H2, 'v3.1 + gemmLnc term' (first) vs MM1-v3.1 (second), family G.** H2w = H2j (W over idle given t; J over idle given t is the same test, and this lane's own J reading decides every case alike, |d_J - d_W| at most 3.5e-16): 5/5/0, **NOT DECIDED**. H2f (J over idle with t forecast): 5/5/0, **NOT DECIDED**. The minimum is 8 decided, and 10 are decided in each; 5 of 10 cannot reach p < 0.05.

| point | W measured | MM1-v3.1 given t | +gemmLnc given t | errors v3.1 / +gemmLnc | d (H2w) | reads | J measured (mJ) | MM1-v3.1, t forecast | +gemmLnc, t forecast | errors | d (H2f) | reads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | 36.24 | 34.01 | 42.01 | +6.54% / -13.74% | -0.0844 | second | 108.68 | 105.05 | 129.03 | +3.46% / -15.77% | -0.1375 | second |
| g02 | 37.81 | 32.25 | 39.69 | +17.23% / -4.74% | +0.1104 | first | 243.82 | 211.32 | 259.29 | +15.38% / -5.96% | +0.0816 | first |
| g03 | 37.41 | 32.39 | 39.87 | +15.50% / -6.17% | +0.0805 | first | 479.82 | 422.65 | 518.57 | +13.53% / -7.47% | +0.0492 | first |
| g04 | 37.55 | 32.35 | 39.81 | +16.10% / -5.67% | +0.0908 | first | 603.12 | 528.31 | 648.22 | +14.16% / -6.96% | +0.0603 | first |
| g05 | 37.91 | 32.38 | 39.85 | +17.09% / -4.88% | +0.1077 | first | 729.71 | 633.97 | 777.86 | +15.10% / -6.19% | +0.0767 | first |
| g06 | 37.80 | 32.32 | 39.78 | +16.97% / -4.96% | +0.1059 | first | 850.98 | 739.63 | 907.51 | +15.05% / -6.23% | +0.0759 | first |
| g07 | 37.77 | 36.07 | 41.99 | +4.72% / -10.04% | -0.0597 | second | 657.79 | 650.16 | 753.24 | +1.17% / -12.67% | -0.1238 | second |
| g08 | 37.95 | 36.09 | 42.01 | +5.14% / -9.68% | -0.0517 | second | 880.44 | 866.88 | 1004.32 | +1.57% / -12.33% | -0.1161 | second |
| g09 | 38.05 | 36.08 | 42.00 | +5.45% / -9.42% | -0.0458 | second | 1103.87 | 1083.59 | 1255.40 | +1.87% / -12.07% | -0.1101 | second |
| g10 | 37.83 | 35.94 | 41.84 | +5.25% / -9.58% | -0.0496 | second | 1323.44 | 1300.31 | 1506.49 | +1.78% / -12.15% | -0.1119 | second |

**The reading** (post hoc, REPORTED). The term is closer at g02, g03, g04, g05, g06, where MM1-v3.1 reads W over idle +15.5 to +17.2% and the term -6.2 to -4.7%. It is farther at g01, g07, g08, g09, g10, where MM1-v3.1 reads +4.7 to +6.5% and the term -13.7 to -9.4%. So where the card's excess over MM1-v3.1 is small, the term adds more than the card shows. The A4 tally by configuration (below) counts the term closer at one of G's three distinct configurations and farther at two.

**H3, 'v3.1 + contention' (first) vs MM1-v3.1 (second), family Y, wall cycles (tie 0.005):** 5/5/6, **NOT DECIDED**. At the four control points the two models are equal, so those cases are ties by construction.

| point | mask | wall measured | MM1-v3.1 | +contention | errors v3.1 / +contention | d | reads |
|---|---|---|---|---|---|---|---|
| y01a | 0x3 | 1,767.4 | 1,564.3 | 1,529.1 | +12.98% / +15.59% | -0.0228 | second |
| y01b | 0x10001 | 1,644.5 | 1,564.3 | 1,572.5 | +5.12% / +4.58% | +0.0052 | first |
| y02a | 0x3 | 1,768.4 | 1,774.0 | 1,743.3 | -0.32% / +1.44% | -0.0111 | second |
| y02b | 0x10001 | 1,651.7 | 1,774.0 | 1,792.5 | -6.89% / -7.85% | -0.0103 | second |
| y03a | 0x3 | 1,787.0 | 1,791.9 | 1,767.1 | -0.27% / +1.13% | -0.0085 | second |
| y03b | 0x10001 | 1,716.3 | 1,791.9 | 1,816.7 | -4.22% / -5.53% | -0.0138 | second |
| y04a | 0xf | 1,662.3 | 1,721.1 | 1,689.7 | -3.42% / -1.62% | +0.0184 | first |
| y04b | 0x33 | 1,740.1 | 1,721.1 | 1,733.0 | +1.10% / +0.41% | +0.0069 | first |
| y05a | 0x5555 | 1,636.4 | 1,823.3 | 1,831.4 | -10.25% / -10.65% | -0.0044 | tie |
| y05b | 0x11111111 | 1,632.0 | 1,823.3 | 1,791.7 | -10.49% / -8.91% | +0.0175 | first |
| y06a | 0x5555 | 1,634.4 | 1,823.3 | 1,831.4 | -10.36% / -10.76% | -0.0044 | tie |
| y06b | 0x11111111 | 1,628.6 | 1,823.3 | 1,791.7 | -10.68% / -9.10% | +0.0175 | first |
| y07a | 0x101 | 1,915.3 | 1,830.0 | 1,830.0 | +4.66% / +4.66% | +0.0000 | tie |
| y07b | 0x10001 | 1,847.6 | 1,830.0 | 1,830.0 | +0.96% / +0.96% | +0.0000 | tie |
| y08a | 0x101 | 1,915.7 | 1,830.1 | 1,830.1 | +4.68% / +4.68% | +0.0000 | tie |
| y08b | 0x10001 | 1,836.9 | 1,830.1 | 1,830.1 | +0.37% / +0.37% | +0.0000 | tie |

**H4, 'v3.1 + both terms' (first) vs MM1-v3.1 (second), the 40 registered points:** 10/10/20, **NOT DECIDED**. Its ten G cases are H2w's cases, d for d, and its sixteen Y cases are H3's. At its other 14 points (g01t, g02t, g03t, g04t, g05t, g06t, g07t, g08t, g09t, g10t, f07, f08, f09, f10) the two models are equal, so d is 0 and each case is a tie, as the registration said. Its first-closer cases are g02, g03, g04, g05, g06, y01b, y04a, y04b, y05b, y06b; its second-closer cases are g01, g07, g08, g09, g10, y01a, y02a, y02b, y03a, y03b.

**Amendment 1's A4, by distinct configuration (REPORTED, `reported-e216.json`; never a verdict):** H1t 1/6/10 of 17, p 0.125; H1w 0/0/17 of 17; H1t-twins 1/2/0 of 3, p 1; H1w-twins 0/0/2 of 2; H2w 1/2/0 of 3, p 1; H2f 1/2/0 of 3, p 1; H3 4/5/3 of 12, p 1; H4 5/7/10 of 22, p 0.774. A4's words: "power with errors shared by configuration (`rules-e216.json > power_shared_REPORTED`): a midpoint 'winner' of H2w 0.437, H2f 0.450 and H4 0.224."

## 6. The pair rule, pair by pair (P1, registered; BLIND)

ln(wall a / wall b) of each pair's two route-c means. A pair is decided when |measured| > 0.0077, and ordered right when the measured sign equals the sign 'v3.1 + contention' predicted. MM1-v3.1 predicts 0 for every pair.

| pair | role | GEMM, shires | masks a / b | measured ln(a / b) | predicted (+contention) | decided | ordered right |
|---|---|---|---|---|---|---|---|
| y01 | largest delta | `gemmL1x8x8`, 2 | 0x3 / 0x10001 | +0.0721 | -0.0280 | yes | no |
| y02 | largest delta | `gemmL1x8x12`, 2 | 0x3 / 0x10001 | +0.0683 | -0.0278 | yes | no |
| y03 | largest delta | `gemmL1x4x16`, 2 | 0x3 / 0x10001 | +0.0404 | -0.0277 | yes | no |
| y04 | largest delta | `gemmL4x2x16`, 4 | 0xf / 0x33 | -0.0457 | -0.0253 | yes | yes |
| y05 | largest delta | `gemmL2x8x16`, 8 | 0x5555 / 0x11111111 | +0.0027 | +0.0219 | no | no |
| y06 | largest delta | `gemmL4x8x16`, 8 | 0x5555 / 0x11111111 | +0.0035 | +0.0219 | no | no |
| y07 | control | `gemmL1x4x24`, 2 | 0x101 / 0x10001 | +0.0360 | +0.0000 | yes | no |
| y08 | control | `gemmL1x8x24`, 2 | 0x101 / 0x10001 | +0.0420 | +0.0000 | yes | no |

**P1 reads FAIL:** 6 pairs decided, 1 ordered right (y04). y01-y03 measured +0.072, +0.068 and +0.040, where the term predicted about -0.028 (the opposite sign). The controls y07 and y08 measured +0.036 and +0.042, where the term predicts 0. y05 and y06 (+0.0027, +0.0035) are undecided. By A9's registered words this contradicts both the contention term and the count-only reading. **The session's own within-session spread** (REPORTED, beside the fixed 0.0077): the second runs of the Y points against their first, route c, n 15 (y04b's second run is route m), rms ln(pass 2 / pass 1) **0.0039**, largest |ln| 0.0107 (y04a). So the decided differences at y01-y03, y07 and y08 (0.036 to 0.072 in ln) sit 9 to 18 times above the session's own repeat.

## 7. Each model's error by family (REPORTED; desk arithmetic; equal to verify-e216d's independent table)

rms of measured / forecast - 1 in %, with the bias (the mean) in brackets; route c, each model's own 799.0 MHz column at the point's measured figures (given t: the model's A + B / T_op at the measured op time). n is 10 for G, 10 for Gt, 16 for Y, 4 for F (new), 40 registered and 6 twins. Its 336 cells equal verify-e216d's own table, worst difference 0.0e+00 points.

**wall cycles an op (T1's quantity)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 10.67 (-10.07) | 2.71 (-1.95) | 6.87 (-1.69) | 9.41 (-9.32) | **7.62 (-4.61)** | 7.08 (-1.90) |
| MM1-v3 | 10.31 (-9.83) | 2.20 (-1.69) | 7.12 (-1.63) | 7.47 (-7.35) | **7.32 (-4.27)** | 6.82 (-0.59) |
| MM1-v2 | 7.27 (-7.03) | 2.41 (+2.40) | 15.20 (+12.73) | 2.28 (-2.22) | **10.37 (+3.71)** | 10.16 (+1.74) |
| v3.1 + gemmLnc term | 10.67 (-10.07) | 2.71 (-1.95) | 6.87 (-1.69) | 9.41 (-9.32) | **7.62 (-4.61)** | 7.08 (-1.90) |
| v3.1 + contention | 10.67 (-10.07) | 2.71 (-1.95) | 7.06 (-1.29) | 9.41 (-9.32) | **7.69 (-4.45)** | 7.08 (-1.90) |
| v3.1 + both terms | 10.67 (-10.07) | 2.71 (-1.95) | 7.06 (-1.29) | 9.41 (-9.32) | **7.69 (-4.45)** | 7.08 (-1.90) |
| v3.1 with T7 (REPORTED) | 9.74 (-9.15) | 1.89 (-0.97) | 16.98 (+5.23) | 6.41 (-6.30) | **12.00 (-1.07)** | 7.18 (+0.50) |

**the counter's mean cycles an op (T2's)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 10.03 (-9.53) | 2.09 (-0.88) | 7.77 (-0.05) | 9.36 (-9.26) | **7.69 (-3.55)** | 4.28 (-2.56) |
| MM1-v3 | 9.67 (-9.29) | 1.56 (-0.62) | 8.01 (+0.01) | 7.43 (-7.29) | **7.43 (-3.20)** | 3.58 (-1.25) |
| MM1-v2 | 6.62 (-6.46) | 3.53 (+3.52) | 17.42 (+14.60) | 2.16 (-2.16) | **11.66 (+4.89)** | 6.38 (+0.97) |
| v3.1 + gemmLnc term | 10.03 (-9.53) | 2.09 (-0.88) | 7.77 (-0.05) | 9.36 (-9.26) | **7.69 (-3.55)** | 4.28 (-2.56) |
| v3.1 + contention | 10.03 (-9.53) | 2.09 (-0.88) | 8.16 (+0.36) | 9.36 (-9.26) | **7.85 (-3.38)** | 4.28 (-2.56) |
| v3.1 + both terms | 10.03 (-9.53) | 2.09 (-0.88) | 8.16 (+0.36) | 9.36 (-9.26) | **7.85 (-3.38)** | 4.28 (-2.56) |
| v3.1 with T7 (REPORTED) | 9.09 (-8.60) | 1.65 (+0.11) | 17.33 (+6.85) | 6.37 (-6.24) | **12.07 (-0.01)** | 3.68 (-0.18) |

**seconds a GEMM (T3's)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 10.69 (-10.08) | 2.71 (-1.97) | 6.86 (-1.71) | 9.42 (-9.34) | **7.62 (-4.63)** | 7.08 (-1.91) |
| MM1-v3 | 10.33 (-9.85) | 2.21 (-1.70) | 7.11 (-1.64) | 7.49 (-7.37) | **7.33 (-4.28)** | 6.82 (-0.59) |
| MM1-v2 | 7.29 (-7.05) | 2.40 (+2.39) | 15.18 (+12.71) | 2.29 (-2.24) | **10.36 (+3.69)** | 10.15 (+1.73) |
| v3.1 + gemmLnc term | 10.69 (-10.08) | 2.71 (-1.97) | 6.86 (-1.71) | 9.42 (-9.34) | **7.62 (-4.63)** | 7.08 (-1.91) |
| v3.1 + contention | 10.69 (-10.08) | 2.71 (-1.97) | 7.06 (-1.31) | 9.42 (-9.34) | **7.70 (-4.47)** | 7.08 (-1.91) |
| v3.1 + both terms | 10.69 (-10.08) | 2.71 (-1.97) | 7.06 (-1.31) | 9.42 (-9.34) | **7.70 (-4.47)** | 7.08 (-1.91) |
| v3.1 with T7 (REPORTED) | 9.75 (-9.16) | 1.89 (-0.98) | 16.96 (+5.21) | 6.43 (-6.32) | **12.00 (-1.08)** | 7.18 (+0.49) |

**W over idle given t (J over idle given t, E1's quantity, reads within 0.0005 points of it in every cell)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 12.35 (+11.00) | 6.28 (-6.22) | 3.36 (-1.22) | 6.30 (-6.25) | **7.52 (+0.08)** | 5.23 (-4.87) |
| MM1-v3 | 12.99 (+11.74) | 5.72 (-5.66) | 3.22 (-0.29) | 6.00 (-5.97) | **7.62 (+0.81)** | 4.84 (-4.46) |
| MM1-v2 | 9.81 (+8.50) | 8.44 (-8.42) | 4.14 (-2.37) | 6.91 (-6.87) | **7.31 (-1.62)** | 4.89 (-4.66) |
| v3.1 + gemmLnc term | 8.39 (-7.89) | 6.28 (-6.22) | 3.36 (-1.22) | 6.30 (-6.25) | **6.00 (-4.64)** | 5.23 (-4.87) |
| v3.1 + contention | 12.35 (+11.00) | 6.28 (-6.22) | 3.36 (-1.22) | 6.30 (-6.25) | **7.52 (+0.08)** | 5.23 (-4.87) |
| v3.1 + both terms | 8.39 (-7.89) | 6.28 (-6.22) | 3.36 (-1.22) | 6.30 (-6.25) | **6.00 (-4.64)** | 5.23 (-4.87) |
| v3.1 with T7 (REPORTED) | 12.37 (+11.06) | 6.22 (-6.17) | 3.11 (-0.20) | 6.06 (-5.99) | **7.45 (+0.54)** | 5.10 (-4.76) |

**J over idle with t forecast (E2's)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 10.47 (+8.31) | 6.78 (-6.67) | 7.23 (-1.78) | 8.68 (-8.67) | **8.21 (-1.17)** | 6.20 (-5.19) |
| MM1-v3 | 10.97 (+9.02) | 6.16 (-6.06) | 7.34 (-0.80) | 7.94 (-7.93) | **8.21 (-0.37)** | 5.65 (-4.51) |
| MM1-v2 | 8.40 (+6.54) | 7.87 (-7.85) | 12.27 (+7.42) | 7.48 (-7.43) | **9.95 (+1.90)** | 5.66 (-4.23) |
| v3.1 + gemmLnc term | 10.35 (-9.78) | 6.78 (-6.67) | 7.23 (-1.78) | 8.68 (-8.67) | **8.17 (-5.69)** | 6.20 (-5.19) |
| v3.1 + contention | 10.47 (+8.31) | 6.78 (-6.67) | 7.47 (-1.50) | 8.68 (-8.67) | **8.29 (-1.06)** | 6.20 (-5.19) |
| v3.1 + both terms | 10.35 (-9.78) | 6.78 (-6.67) | 7.47 (-1.50) | 8.68 (-8.67) | **8.25 (-5.58)** | 6.20 (-5.19) |
| v3.1 with T7 (REPORTED) | 10.66 (+8.63) | 6.48 (-6.39) | 14.82 (+5.26) | 7.63 (-7.62) | **11.51 (+1.90)** | 5.71 (-4.59) |

**J at rest given t (E3's)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 7.42 (+6.65) | 3.76 (-3.72) | 1.19 (-0.50) | 3.87 (-3.79) | **4.40 (+0.16)** | 3.35 (-3.11) |
| MM1-v3 | 7.79 (+7.09) | 3.42 (-3.38) | 1.08 (-0.21) | 3.67 (-3.61) | **4.46 (+0.48)** | 3.10 (-2.85) |
| MM1-v2 | 5.95 (+5.18) | 5.09 (-5.07) | 1.51 (-0.87) | 4.12 (-4.10) | **4.24 (-0.73)** | 3.13 (-2.97) |
| v3.1 + gemmLnc term | 5.53 (-5.19) | 3.76 (-3.72) | 1.19 (-0.50) | 3.87 (-3.79) | **3.64 (-2.80)** | 3.35 (-3.11) |
| v3.1 + contention | 7.42 (+6.65) | 3.76 (-3.72) | 1.19 (-0.50) | 3.87 (-3.79) | **4.40 (+0.16)** | 3.35 (-3.11) |
| v3.1 + both terms | 5.53 (-5.19) | 3.76 (-3.72) | 1.19 (-0.50) | 3.87 (-3.79) | **3.64 (-2.80)** | 3.35 (-3.11) |
| v3.1 with T7 (REPORTED) | 7.43 (+6.69) | 3.72 (-3.69) | 1.04 (-0.18) | 3.73 (-3.64) | **4.37 (+0.31)** | 3.27 (-3.04) |

**J at rest with t forecast (E4's)**

| model | G | Gt | Y | F (new) | **registered (40)** | twins (apart) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 5.15 (+0.79) | 4.97 (-4.75) | 6.94 (-1.74) | 9.04 (-9.00) | **6.34 (-2.59)** | 6.15 (-3.95) |
| MM1-v3 | 4.98 (+1.29) | 4.44 (-4.28) | 7.10 (-1.41) | 7.79 (-7.74) | **6.11 (-2.08)** | 5.61 (-3.04) |
| MM1-v2 | 3.95 (+1.14) | 3.85 (-3.82) | 14.16 (+10.97) | 5.32 (-5.29) | **9.52 (+3.19)** | 6.40 (-2.04) |
| v3.1 + gemmLnc term | 10.44 (-9.89) | 4.97 (-4.75) | 6.94 (-1.74) | 9.04 (-9.00) | **7.80 (-5.26)** | 6.15 (-3.95) |
| v3.1 + contention | 5.15 (+0.79) | 4.97 (-4.75) | 7.15 (-1.39) | 9.04 (-9.00) | **6.43 (-2.44)** | 6.15 (-3.95) |
| v3.1 + both terms | 10.44 (-9.89) | 4.97 (-4.75) | 7.15 (-1.39) | 9.04 (-9.00) | **7.88 (-5.11)** | 6.15 (-3.95) |
| v3.1 with T7 (REPORTED) | 5.12 (+1.39) | 4.38 (-4.19) | 16.25 (+5.30) | 7.17 (-7.15) | **11.05 (+0.70)** | 5.55 (-2.70) |

## 8. 'v3.1 with T7' (REPORTED)

The same fit's declared T7 time form, frozen with the registration (`tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+T7.json`), is in every table of section 7. By point, wall cycles, measured / forecast - 1 in %, beside MM1-v3.1's (`scored-e216.json`'s REPORTED cells). The tally is a desk count against MM1-v3.1 at the registered cycles tie, 0.005 in ln, given as T7 closer / v3.1 closer / ties with the sign test's p; it is never a verdict:

| family | tally | points: v3.1 / T7 |
|---|---|---|
| G | 10 / 0 / 0, p 0.00195 | g01 -11.6 / -10.3; g02 -6.3 / -5.6; g03 -6.8 / -6.1; g04 -6.6 / -5.9; g05 -6.7 / -6.0; g06 -6.5 / -5.8; g07 -14.1 / -13.0; g08 -14.2 / -13.1; g09 -14.1 / -13.0; g10 -13.7 / -12.6 |
| Gt | 5 / 3 / 2, p 0.727 | g01t -3.0 / -1.6; g02t +0.1 / +0.8; g03t -0.2 / +0.5; g04t +0.1 / +0.8; g05t -0.4 / +0.3; g06t -0.0 / +0.7; g07t -4.3 / -3.1; g08t -3.8 / -2.6; g09t -3.9 / -2.7; g10t -4.0 / -2.8 |
| Y | 0 / 16 / 0, p 3.05e-05 | y01a +13.0 / +17.1; y01b +5.1 / +15.4; y02a -0.3 / +3.1; y02b -6.9 / +17.8; y03a -0.3 / +19.1; y03b -4.2 / +26.1; y04a -3.4 / -6.5; y04b +1.1 / +4.9; y05a -10.3 / -16.5; y05b -10.5 / -20.2; y06a -10.4 / -16.6; y06b -10.7 / -20.4; y07a +4.7 / +26.6; y07b +1.0 / +22.1; y08a +4.7 / +8.0; y08b +0.4 / +3.6 |
| F new | 4 / 0 / 0, p 0.125 | f07 -8.9 / -5.8; f08 -7.7 / -4.8; f09 -11.2 / -8.1; f10 -9.4 / -6.6 |
| registered (40) | 19 / 19 / 2, p 1 | the rows above |
| F twins (apart) | 5 / 1 / 0, p 0.219 | f01 -5.2 / -2.9; f02 -5.0 / -2.7; f03 -5.1 / -2.9; f04 -4.7 / -2.4; f05 -4.8 / -2.6; f06 +13.4 / +16.5 |

So T7's time form is closer at family G (10 of 10) and at F (new) (4 of 4), splits Gt (5 / 3 / 2), and is farther at every subset mask of family Y (16 of 16); over the registered 40 it reads 19 / 19 / 2 against MM1-v3.1. Its W over idle given t errors are within 1.45 points of MM1-v3.1's at every point.

## 9. The card-transfer twins, apart, beside E215 arm A's committed data (REPORTED)

E215 arm A ran these six configurations on aifoundry3 card 0 at 600 MHz (its data `8355db15`, its scores committed in `7cddc406`). E216 ran them here on aifoundry2 card 0 at 799 MHz. Each card has its own frozen MM1-v3.1 forecast. E215's figures are read from `docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/scores-e215-A.json` at HEAD (sha256 `58d777e023db50c0...`, as its `SHA256SUMS-note1` lists it), and its measured values equal verify-e216d's re-derivation from E215's raw files. The move is ln(1 + error here) - ln(1 + error there). Errors are measured / forecast - 1, in %.

| twin | E215 point | wall there: measured / v3.1 / error | wall here: measured / v3.1 / error | move (ln) | seconds: there / here | J over idle given t: there / here | W over idle given t: there (verify-e216d) / here | MM1-v3 wall: there / here (verify-e216d) |
|---|---|---|---|---|---|---|---|---|
| f01 | a033 (`gemmL2x15x2`) | 1,116.9 / 1,165.6 / -4.18% | 1,350.2 / 1,423.9 / -5.18% | -0.0105 | -4.10% / -5.18% | -2.43% / -6.10% | -2.35% / -6.10% | -2.81% / -3.85% |
| f02 | a034 (`gemmL3x15x2`) | 1,120.3 / 1,165.6 / -3.88% | 1,353.3 / 1,423.9 / -4.96% | -0.0113 | -3.79% / -4.96% | -2.79% / -6.02% | -2.70% / -6.02% | -2.50% / -3.63% |
| f03 | a035 (`gemmL10x15x2`) | 1,119.4 / 1,165.6 / -3.96% | 1,351.1 / 1,423.9 / -5.11% | -0.0121 | -3.87% / -5.11% | -2.32% / -5.84% | -2.24% / -5.84% | -2.58% / -3.78% |
| f04 | a036 (`gemmL11x15x2`) | 1,119.8 / 1,165.6 / -3.93% | 1,357.2 / 1,423.9 / -4.68% | -0.0079 | -3.84% / -4.69% | -2.18% / -4.95% | -2.10% / -4.95% | -2.55% / -3.35% |
| f05 | a037 (`gemmL12x15x2`) | 1,119.5 / 1,165.6 / -3.95% | 1,355.0 / 1,423.9 / -4.84% | -0.0093 | -3.85% / -4.84% | -2.75% / -5.61% | -2.65% / -5.61% | -2.58% / -3.51% |
| f06 | a043 (`gemmL2x1x7`) | 1,397.9 / 1,239.2 / +12.81% | 1,735.2 / 1,530.8 / +13.35% | +0.0048 | +12.92% / +13.34% | +4.58% / -0.67% | +4.67% / -0.67% | +14.18% / +14.61% |

**The reading** (post hoc, REPORTED). A configuration's time error moves little between the two cards: f01-f05 read -4.2 to -3.9% there and -5.2 to -4.7% here, and f06's L3-edge miss (a043, `gemmL2x1x7`) reads +12.8% there and +13.4% here. The energy error given t reads 2.8 to 5.2 points lower here. E215's J over idle given t (its E1) and verify-e216d's W reading differ by up to 0.10 points there; here the two readings agree within 1.1e-14 points. The twins' own rule lines (T1-twins to E4-twins) are in section 3, all TOO FEW (6 points, 10 needed).

## 10. Amendment 1's A2 (REPORTED; `reported-e216.json`, never a verdict)

A2's words: "if the frozen gemmLnc term is right at G, E1, E2 and E3 read FAIL at 30 of 40 and E4 at 34 of 40, from family G alone, while the 30 points outside G PASS." It was read again by `report_e216.py` from the scorer's own output, and the registered verdicts it made again equal the scorer's (True):

| rule | registered (40) | without G (30) | G alone (10) |
|---|---|---|---|
| T1 | FAIL 29/40 | FAIL 24/30 | FAIL 5/10 |
| T2 | PASS 36/40 | PASS 29/30 | FAIL 7/10 |
| T3 | FAIL 29/40 | FAIL 24/30 | FAIL 5/10 |
| E1 | FAIL 35/40 | PASS 30/30 | FAIL 5/10 |
| E2 | FAIL 34/40 | PASS 29/30 | FAIL 5/10 |
| E3 | FAIL 35/40 | PASS 30/30 | FAIL 5/10 |
| E4 | FAIL 34/40 | FAIL 24/30 | PASS 10/10 |

So E1-E3 PASS on the 30 points outside family G and fail only by G, where MM1-v3.1 reads the gemmLnc points' W over idle 15.5 to 17.2% low at g02-g06. The term was meant to supply that excess, and section 5's H2 shows where it does and where it overshoots.

## 11. The readings beside the scorer, and the one flagged run (REPORTED)

- **`post.out`:** "NO DATA, NAMED (REPORTED): no run []; route m only []; no energy []; labelled []; by family {}; the session's stop None": every point has a route-c run with energy, none is route m only, and none is labelled.
- **The scorer's one flag:** y04b's second run, run 043, reads "STEP", "CAPPED: no energy" and "ROUTE m at 799.0 MHz". The governor stepped the clock down inside its busy window (verify-e216d read it at about 564-600 MHz, 2.3-3.3 s into the process), so the run carries no energy and is scored on route m only: its wall 1,734.24 cycles an op against MM1-v3.1's 799.0 MHz column 1,721.1 (+0.77%), REPORTED. y04b's registered figure is its first run (run 034, route c) alone. This is registered behaviour.
- **Route c** holds 61 of the 62 point runs, and their view clocks read 798.93-799.27 MHz.

## 12. verify-e216d's re-derivation, beside (its own code; verdict HOLDS)

- **The measured side:** its own reader of the session's raw files gives 1,617 fields, bit-equal to `data-e216.json`, with 0 mismatches.
- **The rules:** re-scored from E216.md's words with its own code, 1,384 items, 0 differences from `scored-e216.json`; A2 14/14 and A4 8/8 equal.
- **Step 13 made again** on the committed bytes: 9 of 9 outputs byte-equal.
- **Against this note:** its route-c figures are bit-equal to the scorer's; its per-point MM1-v3.1 errors equal the scorer's cells, worst difference 0.0e+00; its rms table equals section 7's, worst difference 0.0e+00 points; its pass-2 spread is n 15, rms 0.00390, equal; and its twins re-derivation from E215's raw files equals E215's committed measured values, difference 0.
- **Its words on H2** (its result): "The gemmLnc term is closer at g02-g06, where v3.1 reads +15.5 to +17.2% and the term -4.7 to -6.2%. It is farther at g01 and g07-g10, where v3.1 reads +4.7 to +6.5% and the term -9.4 to -13.7%."

## 13. Findings, answered as dated clauses (Thu 19 Nov 2026, after the data; post hoc; nothing re-scored)

1. **The lab's check C0 (README note 13; card-e216's finding 1, confirmed by verify-e216d's finding 1).** `checks-e216.txt` reads C0_src FAIL only because E208's checker takes the schedule from `session/session.log`'s first line, where E216's runner writes its own line. verify-e216d read the checker's own C0 conditions on the log's second line, and C0 PASSES there: the prefix `42c425da6ead86e0` equals the box's src list, `queue.json` and the schedule file, and the harness reads OK with 69 files. **Answered:** the committed checks files stand as written, REPORTED and never a gate. R0, the scorer's rule, reads each run's check of C, not the data checker's C0, and it PASSES.
2. **y04b's run 043** (card-e216's finding 2; verify-e216d's finding 3). It is flagged STEP and CAPPED and scored on route m only, by the registered routes. **Answered:** this is registered behaviour. y04b's point is its run 034. The pair y04 is decided on that run and on y04a's two runs, and it is ordered right.
3. **T2's PASS is a hairline** (verify-e216d's finding 4). 36 of 40 are in band, and 36 are needed. g10's counter reads -12.77% against the 13% band, while g07-g09 miss it by 0.16-0.23 points (g07 -13.16, g08 -13.23, g09 -13.19). **Answered:** the verdict stands as registered.
4. **The card monitors read the kit lanes' desk tests as holds of the card** (verify-e216d's finding 2, cross-lane). On Thursday, before the day, the box's card monitors counted the kit lanes' sandboxed desk tests (their stand-in card lock) as holds of aifoundry2 card 0, and the lab's temperature monitor paused its reads in those spans. No real access happened: the box's usage daemon counts 0 opens of the card's ops node from 16:23:12 PST Wed 18 Nov to 16:56:12 PST Thu 19 Nov. **Answered:** E216's rest holds, and nothing in E216's record changes. A change to the sandbox or the collector is the orchestrator's call, outside E216.
5. **Two wordings in the data commit** (verify-e216d's finding 5, a nit). README note 11's "612 / 132 / 3,888" samples count the 67 run processes' windows; with the smoke's three processes they are 645 / 138 / 3,933. The data commit's message says the card lane's departures and notes are "README notes 2-15", but they are notes 1-15. **Answered:** words only, recorded here.
6. **The public-text scan's two hits in the data commit** (card-e216's finding 3) were the data README form's own word and a word of the never-run line, read and judged benign before that commit. **Answered:** nothing in those files changes. Before this commit, this note, its list and the commit's message were scanned and gave no hit. In the nine copied files the scans found one match: the scorer's own key for y04b's route-m figure in `scored-e216.json`, which the address pattern reads as an e-mail address. It was reviewed as benign, and the bytes stay as the step wrote them.

## 14. What this note does not do

- It changes no committed file, re-scores nothing and moves no verdict.
- It does not score the model session's sealed forecast (registered in `794592a2`), and it holds no number of it.
- **Transistor switches** are estimated and never measured: no card counts switches, so no rule scores them (E216.md section 8).
- **NOT RUN here:** a re-derivation of the bands' held-out bases (taken as registered); a re-derivation of the measured side from the session's raw files (verify-e216d's, section 12); any E217 datum.

## 15. `SHA256SUMS-note16`

`SHA256SUMS-note16` lists the nine step-13 files and this note, then `README.md` and `SHA256SUMS` as the data commit holds them. `sha256sum -c SHA256SUMS-note16` in this directory reads all 12 lines OK, and `SHA256SUMS` still reads its 247 lines OK.
