# E209 data, dated note 15 (POST HOC): the readings the frozen scorer left unprinted or uncomputed - the REPORTED readings beside every head-to-head, and the registered readings (a)-(d) - stated after the data verifier's findings; no committed file, rule, verdict or forecast changed

*Tue 17 Nov 2026 (week 47), PST. Written at about 13:55 PST by round Q212's lane `fix-e209d`. That was after this directory's data commit
`ea3fa3ce` (13:00:31 PST, pushed 13:00:36) and after the day's data verifier `verify-e209d` (13:04-13:34 PST: HOLDS WITH FIXES). The
scorer's outputs are not committed yet: a later lane commits them beside this directory. **It adds new files only.** README.md's notes 1-14 came with
the data commit; this is note 15. Labels: **registered** (E209.md with its amendment A1, `rules-e209.json`), **measured** (this directory's
records, read through E208's registered reducer), **blind** (MM1-v2's forecasts, pushed in `3ca4b717` at 01:44:48 PST, before the first card
command at 10:30:44 PST), **REPORTED** (never a verdict) and **post hoc** (chosen after the data), as each line says. Every desk step ran on
aifoundry2 under `/usr/bin/python3` 3.12.3 with `-I -B`.*

## 1. Why this note

`verify-e209d` re-derived the day from the raw files with its own code: 62 runs and 2,598 fields, 0 mismatches. Every registered verdict, count
and cell it scored equals the frozen scorer's (`score_e209.py`, `e522919a...`). Its two low findings are both about what the scorer printed:

1. **Readings (a)-(d) were not computed.** The scorer's `readings()` computes the registered readings (e)-(j). It does not compute E209.md
   section 7's (a) the stride step, (b) one K block, (c) the subsets or (d) the kinds, although its docstring says it reports "the readings
   (E209.md section 7)".
2. **Two of the three side readings beside each head-to-head were not printed.** The registration asks for three readings beside each
   head-to-head, in its words: "REPORTED beside every head-to-head, never verdicts: the other test's verdict; a family-level check (the sign test
   over the families' median d, E207's fix); the bootstrap of the median d". The scorer computed all three and stored them in its output JSON, but
   it printed only the other test's verdict. Beside H1-H3's "MM1-v2 BETTER", those unprinted readings disagree with the verdict.

This note states them. Each was computed after the scorer from the scorer's own figures, by the registered definitions, and each was
re-derived and checked equal. **The scorer stays frozen. Nothing is re-scored. The registered verdicts stand as the scorer printed them.**

## 2. The new files

| file | what |
|---|---|
| `README.md.dated-note-15.md` | this note |
| `posthoc_note15_e209.py` | the post hoc script (standard library only). It reads the frozen scorer's output JSON and its input JSON (step 13's two files), plus four registered or frozen files, each checked by sha256 first. It prints sections A-D and writes the JSON below |
| `posthoc-note15-e209.txt` | its printed lines (117 lines) |
| `posthoc-note15-e209.json` | every figure behind them: the d of every case and point, the cells, the intervals, the family tables, the readings, the margins and the governor's runs |
| `SHA256SUMS-note15` | the four files above, then `README.md` and `SHA256SUMS` as the data commit holds them |

**The inputs, by sha256:**

| role | file | sha256 |
|---|---|---|
| the scorer's output | step 13's `scored-e209.json` | `3e53bb3e587b899f44fb5ec5dc4610d704bc332f3997679ae5173d1472620e94` |
| its input | step 13's `data-e209.json`: E208's registered reducer on this directory's committed session | `90bc84ab52441f53a6283e5b096a83e02de5ed5979b4c0cd5423fb203a0c2805` |
| registered | `tools/claims-v3/e209/points-e209.json` | `cfdda741bcc8cbd8555ff21809f2897fae0f734b66727b108795cd138fb07261` |
| registered | `tools/claims-v3/e209/rules-e209.json` | `0d7dfa791573cf00505143a0188dff7ad5e2ce6f95447c66fef89e9d5b8a62bb` |
| frozen | `tools/matmul/mm1/v2/out/mm1_v2_e209.csv` | `fdd018ca9ceb420285746acdc94b2e0fc62a68141d9b0d3990c3cf9777ec3a63` |
| frozen | `tools/matmul/mm1/v2/out/f1f2_e209.csv` | `65a98e01868743b4daf4b06be1b1ba4edbd77c47f3d4824353ffdb0bf4ceefce` |

The two step-13 files sit in the card lane's run folder, outside the lab, until a later lane commits them beside this directory byte for byte.

## 3. Beside every head-to-head (section A of the printout)

**How d is defined.** d = |ln(measured / other)| - |ln(measured / MM1-v2)|, taken per time case for H1-H3 and H5, and per point for H4 and H6.
MM1-v2 is closer where d is above the tie: 0.005 in ln for cycles and seconds, 0.01 for joules. No point was scored in watts.

| rule | registered verdict (its test) | cells: MM1-v2 / other / tie | REPORTED: the other test's verdict | REPORTED: the bootstrap of the median d | REPORTED: the family-level check |
|---|---|---|---|---|---|
| H1 (cycles, the wall, against MM1-v1) | **MM1-v2 BETTER**: the mean d +0.0158, 95% [+0.0037, +0.0293] | 17 / 11 / 13 | the sign test, 17 against 11, p 0.345: **NOT DECIDED** | median +0.0024, 95% [-0.0042, +0.0096]: **spans 0** | 2 families against 2, 5 within the tie; p 1.000 |
| H2 (cycles, the counter's mean, against MM1-v1) | **MM1-v2 BETTER**: +0.0233, [+0.0063, +0.0451] | 15 / 11 / 15 | 15 against 11, p 0.557: **NOT DECIDED** | +0.0028, [-0.0039, +0.0096]: **spans 0** | 2 against 2, 5 within the tie; p 1.000 |
| H3 (seconds, against MM1-v1; H1's cells) | **MM1-v2 BETTER**: +0.0158, [+0.0036, +0.0291] | 17 / 11 / 13 | 17 against 11, p 0.345: **NOT DECIDED** | +0.0024, [-0.0042, +0.0096]: **spans 0** | 2 against 2, 5 within the tie; p 1.000 |
| H4 (J over idle given t, against MM1-v1) | **NOT DECIDED**: +0.0038, [-0.0005, +0.0085] | 9 / 5 / 25 | 9 against 5, p 0.424: NOT DECIDED | +0.0011, [-0.0032, +0.0054]: spans 0 | 1 against 0, 8 within the tie; p 1.000 |
| H5 (cycles, the wall, against F1@800) | **MM1-v2 BETTER**: the sign test, 38 against 3, p 1.05e-08 | 38 / 3 / 0 | the bootstrap of the mean d +0.1098, [+0.0831, +0.1365]: MM1-v2 BETTER | +0.1027, [+0.0805, +0.1576]: above 0 | 9 against 0; p 0.00391 |
| H6 (J over idle, t forecast, against F2@800) | **MM1-v2 BETTER**: 35 against 5, p 1.38e-06 | 35 / 5 / 2 | +0.4778, [+0.2990, +0.6730]: MM1-v2 BETTER | +0.1801, [+0.0897, +0.3788]: above 0 | 9 against 0; p 0.00391 |

**What the side readings say (REPORTED, never a verdict).** H5 and H6 have the support of every side reading. H1-H3 do not. Their registered
"MM1-v2 BETTER" rests on the mean d, and that mean holds steady when the seed changes (verify-e209d: the interval's lower bound stays at
0.0035-0.0041 over 20 other seeds). But the case-by-case readings do not show it: the sign test is NOT DECIDED, the median d's interval spans 0,
and the families split 2 against 2.

The family table (post hoc, H1) shows where the mean comes from:
- **The subsets carry 67% of the summed d** (median d +0.054; MM1-v2 closer at 5 of 8).
- **The knee carries 29%** (+0.012; 5 of 7).
- **MM1-v1 is closer on one K block** (-0.035; 2 of 2) **and on the power-of-two strides** (-0.017; 3 of 5).

The registration stated this cost before the data: "the bootstrap's simulated false-winner rate under the midpoint (both directions) is 6-8%,
above its nominal 5% ... with correlated errors within a family both rise". So the registered verdict stands, and it reads as **MM1-v2 closer on
average, mostly through the subsets**, not as MM1-v2 closer case by case. Every family's median d, count and mean d for all six rules are in the
printout and the JSON.

**Re-derived.** The script recomputes every d from the scorer's per-case and per-point figures, then the cells, the exact sign test, both
bootstrap intervals and the family check. For the bootstraps it uses the registered seed `E209|bootstrap|<rule>` and 10,000 resamples, in the
scorer's order. **All of it is equal, exactly, to the scorer's JSON for all six rules.**

## 4. The registered readings (a)-(d) (section B of the printout)

These are the scorer's own figures. Measured = the mean of a point's kept runs. MM1-v2 and MM1-v1 are called at each run's measured clock
(route m). F1@800 and F2@800 are as frozen.

**(a) The stride step, the wall.**
- **e28 / e29** (gemmL1x8x6 over gemmL1x7x6, fp32, the full chip, 2 runs each): measured **1.297**; MM1-v2 1.187, MM1-v1 1.179, F1@800 1.000.
  Every model under-reads the step at NB 8. MM1-v2 comes closest, and it still reads only about two thirds of it in ln (0.171 of 0.260).
- **e33** (gemmL1x16x6 fp16) **and e30** (gemmL2x8x4 int8) "against their neighbours' forecasts". No neighbour of theirs ran on the day, and the
  registration names none. So each model's step is read against that model's own forecast of the point. The measured step against a model's
  neighbour forecast, over that model's step, is measured over the model's forecast, whichever neighbour is taken, and no new forecast is made.
  - e33: measured / MM1-v2 **1.043**, / MM1-v1 1.022, / F1@800 1.055.
  - e30: measured / MM1-v2 1.016, / MM1-v1 1.018, / F1@800 0.999.
  - Beside them, not named in (a), the family's NB 4 point e32 (gemmL1x4x12 fp32): measured / MM1-v2 0.941, / MM1-v1 0.960, / F1@800 0.868.

**(b) One K block** (int8, the full chip, at the top point):

| point | measured wall / counter's mean | MM1-v2 (L2 time in cycles) | MM1-v1 (L2 time clock-free) |
|---|---|---|---|
| e07 (gemmL1x3x1; 2 runs read for time; one run capped, its time still read) | 1008.8 / 885.9 cycles an op | 870.9 / 773.4: measured **x1.158** / x1.145 | 905.1 / 803.8: measured **x1.115** / x1.102 |
| e08 (gemmL3x5x1; 1 run) | 1033.8 / 946.6 | 937.0 / 926.8: x1.103 / x1.021 | 967.2 / 956.7: x1.069 / x0.989 |

Both models under-read one K block on the wall. MM1-v1, whose L2 time is clock-free, is the closer of the two at both points, on the wall and
on the counter's mean.

**(c) The subsets.** The table gives the wall and the counter's mean at each registered mask, and which model is closer on each, by the
registered tie of 0.005 in ln. These are H1's and H2's own cells at these time cases.

| point, mask (shires) | measured wall / mean / ratio | MM1-v2 ratio | ln(measured / forecast), wall: MM1-v2, MM1-v1 | closer, wall | closer, mean |
|---|---|---|---|---|---|
| e43, 0x1 (1) | 1060.2 / 1060.2 / 1.000 | 1.126 | -2.6%, +13.9% | MM1-v2 | MM1-v2 |
| e39, 0x80000000 (1) | 1655.7 / 1655.7 / 1.000 | 1.011 | +21.5%, +20.2% | MM1-v1 | MM1-v1 |
| e17, 0xf (4) | 1152.4 / 1056.8 / 1.090 | 1.126 | +5.0%, +17.2% | MM1-v2 | MM1-v2 |
| e31, 0x1111 (4) | 1134.8 / 1038.0 / 1.093 | 1.126 | +4.2%, +18.2% | MM1-v2 | MM1-v2 |
| e40, 0x1111 (4) | 1560.0 / 1560.0 / 1.000 | 1.011 | +9.9%, +8.0% | MM1-v1 | MM1-v1 |
| e42, 0xf000 (4) | 1239.8 / 1239.4 / 1.000 | 1.227 | -3.0%, -3.7% | MM1-v2 | MM1-v1 |
| e09, 0xff (8) | 1077.1 / 985.5 / 1.093 | 1.212 | -0.8%, +10.9% | MM1-v2 | MM1-v2 |
| e04, 0xffff (16) | 1063.2 / 956.6 / 1.111 | 1.126 | -1.3%, +7.2% | MM1-v2 | MM1-v2 |
| e41, 0xffff0000 (16) | 1212.6 / 1212.5 / 1.000 | 1.011 | -10.2%, -8.3% | MM1-v1 | MM1-v1 |

- **On the wall, MM1-v2 is closer at 6 of 9 subset points and MM1-v1 at 3. On the counter's mean it is 5 and 4.**
- MM1-v1's ratio of the wall to the mean is MM1-v2's at every point but e17 (1.367 there).
- Five points measure a wall-to-mean ratio of 1.000, where the models put 1.011-1.227: there the counter's mean equals the slowest minion.
  Those five are e43, e39, e40 and e42 at 1 and 4 shires, and e41 at 16.

**(d) The kinds**: J over idle of each zeros, ones and real point over its time case's random point, measured beside each model's ratio.

| pair (kind over random, format) | measured | MM1-v2 | MM1-v1 | F1@800 | F2@800 |
|---|---|---|---|---|---|
| e34 / e18 (real, fp32) | 0.986 | 0.992 | n.f. | 0.997 | 0.979 |
| e35 / e01 (real, int8) | **0.910** | 0.973 | n.f. | 0.926 | 0.873 |
| e36 / e19 (real, fp16) | 0.970 | 0.983 | n.f. | 0.991 | 0.971 |
| e38 / e20 (zeros, int8) | 0.589 | 0.571 | 0.581 | 0.705 | 0.630 |

Each model's ratio is taken at its own seconds. Given the measured seconds instead, MM1-v2 reads 0.992, 0.975, 0.982 and 0.566, and MM1-v1 reads
0.572 for e38 / e20. 'n.f.' means NOT FORECAST: MM1-v1 prices no real tile here. Each pair's two points take the same time to within 0.5%
(measured time ratios 0.996-1.004), so each ratio is a ratio of watts.

**MM1-v2's real-data price is short of the measured saving in int8.** Real int8 data save 9.0% against random, and MM1-v2 forecast 2.7%. In fp32
and fp16 it is short by 0.6 and 1.3 points. For zeros in int8 it goes the other way: MM1-v2 forecast a saving 1.8 points larger than measured,
and MM1-v1 (0.581) is nearer.

## 5. POST HOC: the margins of the registered rules (section C of the printout)

A rule PASSES when at least 90% of its scored cells pass. "Could take" is how many more failing cells the rule could take and still PASS. Every
cell was re-derived from the scorer's figures, and all equal its cells.

| rule (band) | verdict | could take | failing cells | the passing cells nearest the band |
|---|---|---|---|---|
| T1m, T3m (19%) | PASS 39 of 41 | 2 | e39 +23.96%, e15 +19.34% | e07 +15.84%, e11 +15.07%, e24 +11.93% |
| T1c (19%) | PASS 39 of 41 | 2 | e39 +23.98%, e15 +19.36% | e07 +15.86%, e11 +15.09%, e24 +11.94% |
| T3c (19%) | PASS 39 of 41 | 2 | e39 +23.96%, e15 +19.34% | e07 +15.83%, e11 +15.07%, e24 +11.93% |
| T2m (19%) | PASS 39 of 41 | 2 | e39 +25.33%, **e42 +19.03%** | **e15 +18.57%**, e07 +14.55%, e11 +14.32% |
| T2c (19%) | PASS 39 of 41 | 2 | e39 +25.34%, e42 +19.04% | e15 +18.58%, e07 +14.56%, e11 +14.33% |
| E1 (14%) | PASS 45 of 45 | 4 | none | e08 +11.13%, e25 -10.07%, e23 -8.99% |
| E2m (15%) | PASS 42 of 45 | **1** | e39 +21.09%, e15 +18.14%, e08 +15.47% | e11 +13.27%, e25 -11.27%, e41 -10.93% |
| E2c (15%) | PASS 41 of 44 | **1** | e39 +21.17%, e15 +18.19%, e08 +15.47% | e11 +13.33%, e25 -11.25%, e41 -10.90% |
| E3 (5%) | PASS 43 of 45 | 2 | e08 +5.46%, e23 -5.16% | e25 -4.72%, e36 -4.27%, e41 -4.16% |
| E4m (13%) | PASS 42 of 45 | **1** | e39 +23.23%, e15 +18.93%, e11 +14.46% | **e08 +12.93%**, e07 +12.19%, e41 -10.33% |
| E4c (13%) | PASS 41 of 44 | **1** | e39 +23.25%, e15 +18.95%, e11 +14.47% | e08 +12.93%, e07 +12.22%, e41 -10.32% |
| K1 (23 MHz) | PASS 44 of 45 | 3 | e44 +24.8 MHz | e45 +17.6, e02 +16.9, e30 -16.5 MHz |

E2c and E4c score 44 points: e44 was forecast capped, so route c forecasts no energy reading there (NO DATA, never a failure).

- **E2m, E2c, E4m and E4c each pass with one failing cell to spare.** A second failing cell would make any of them FAIL.
- Two cells sit within 0.1 point of their band: E4's e08 is inside at 12.93% of 13%, and T2's e42 is outside at 19.03% of 19%.
- The time cases above are named by their points (e07 = gemmL1x3x1 int8, e11 = gemmL1x1x13 fp32, e15 = gemmL3x1x5 fp32, e24 = gemmL1x2x24
  fp32, e39 = gemmL2x6x10 fp32 at 0x80000000, e42 = gemmL6x6x6 int8 at 0xf000).
- **The day's replicate spread**, the scorer's reading (h): the pooled sd of W over idle over the 9 points read twice for energy is **0.299 W**
  (df 9). The registered SD_rep is 0.173 W. No point was scored in watts, so the 0.35 W band (2 x SD_rep) touched no cell.

**The verdicts stand as registered.** These margins are read after the data and change none of them.

## 6. REPORTED: the governor (section D of the printout)

**K1** (each point's burst-mean clock within 23 MHz of MM1-v2's forecast) PASSES at 44 of 45 (rms 9.89 MHz, mean +2.37 MHz). The failing point is
**e44**: it measured 788.9 MHz against the forecast's 764.1. **K2** (REPORTED): MM1-v2's capped forecast agrees with 53 of 55 kept runs'
measured capped flags, and "never capped" agrees with 54. The two runs it misses:

- **036-e44** was forecast capped, with an 800 MHz share of 0.78 under the reducer's 0.8 line. It ran uncapped (share 1.000), with the board
  at 68.27 W mean in its view.
- **056-e07** was forecast uncapped (share 1.00). It ran capped (share 0.727), with the board at 44.22 W, and was read for time only.

Between them they make K1's one failure and K2's two disagreements: input for MM1-v3's governor term.

## 7. The data verifier's other findings, dated (Tue 17 Nov 2026, PST)

- **The live view's "held" spans before T0 were desk tests, not card use.** The box's live history shows the card's lock "held" in 15 short
  spans between E208 a2c0-S1r's end (00:10:41.915) and E209's T0. Each matches one of E209's own desk tests in the round's no-device sandbox
  (`nodev.sh`): the kit's, the verifier's, the fix's and the readiness check's. The cause is in the collector:
  - inside the sandbox, the private lock directory gives the sandbox's lock file the inode number of the card's real lock;
  - `tools/lab/live/live-collector.py`'s `lock_inodes()` matches the kernel's lock table by inode number alone.

  No card command was sent in those spans: the reboot gate's attempt ledger is silent from Mon 16 Nov 09:37:17 to Tue 17 Nov 10:30:44 PST. The
  rest holds even if the spans are counted, since the last ended at 09:48:54 PST, 41.8 minutes before T0. The collector's fix is lab tooling,
  not E209: match the device and the inode together. Nothing of it is changed here.
- **Blindness holds.** Two commits came just before the data commit: `d6d62660` (12:45:00, the model session's sealed forecast registered as
  REPORTED) and `f92136dd` (12:45:34, kit note 1). They carry session metadata only: the session id, its times, the checker's ALL PASS line,
  the copy-back counts and the reboot-gate record's sha256s. Neither carries a measured figure. MM1-v2's forecasts (`3ca4b717`) precede T0 by
  8 h 46 min.
- **The stop lines stood as registered.** No separate confirmation of the stop lines was written before the day, so the registered lines held
  (E209.md section 6): the board strictly above 85 W on 3 samples in a row; the shires' mean die at or above 80 C; the hottest-sensor latch at
  or above 80 C once it has risen during the session. The day's peaks stayed far under them: the board 69.55 W (run 036-e44), the shires' mean
  die 55 C, and the hottest-sensor latch at 62 C from its first sample on.

## 8. What this note does not change

No committed file is edited. No rule, band, tie, forecast, label or verdict is changed. The scorer is not re-run, and nothing is re-scored.
The registered verdicts are the frozen scorer's, as printed at step 13:
- R0 PASS;
- T1m, T1c, T2m, T2c, T3m and T3c PASS at 39 of 41;
- E1 PASS 45/45, E2m 42/45, E2c 41/44, E3 43/45, E4m 42/45, E4c 41/44;
- K1 PASS 44/45;
- H1-H3 MM1-v2 BETTER, H4 NOT DECIDED, H5 and H6 MM1-v2 BETTER.

The model session's sealed forecast for E209 (registered as REPORTED in `d6d62660`) is neither read nor scored here.

## 9. Reproduce

Run this in this directory, with the two step-13 files beside it:

`python3 -I -B posthoc_note15_e209.py <the scorer's output JSON> <its input JSON> --json posthoc-note15-e209.json > posthoc-note15-e209.txt`

Under `/usr/bin/python3` 3.12.3 it writes both files byte for byte and exits 0. It exits 4 if any input's sha256 differs, writing nothing, and 5 if a re-derived figure
differs from the scorer's. Until those two files are committed, the kit's step 13 (`tools/claims-v3/e209/rb/s24_score_e209_n1.sh`: E208's
registered reducer on this directory's committed session, then the frozen scorer) makes both from what is committed now.

Two desk checks by this lane are not committed:
- the script's re-derivation is equal, exactly, to the scorer's JSON;
- the 2,108 figures the script reads from the scorer's output are equal to `verify-e209d`'s own re-derivation and scoring (worst relative
  difference 0), so the readings come out the same from the verifier's independent route.
