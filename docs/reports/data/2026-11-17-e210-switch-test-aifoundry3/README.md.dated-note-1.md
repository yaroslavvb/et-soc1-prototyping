# E210 data, dated note 1: the frozen scorer's output, committed beside the data byte for byte - R0, the time equality and B5 PASS; the switch route R1 BETTER than the null and than both bit-flip routes (H1-H3); H4 UNDECIDED, as registered; with verify-e210d's re-derivation beside each result

*Tue 17 Nov 2026 (week 47), PST; written at about 13:29 PST by Q202c's lane `scores-e210`, after this directory's data commit `6689d68f` (12:44:27 PST, pushed 12:44:33) and after the day's data verifier `verify-e210d` (HOLDS). It adds new files only: no committed file, rule, band, forecast, label or scorer is changed. Labels: **registered** (E210.md with its amendment A1; the kit), **measured** (this directory's records), **blind** (the routes' forecasts, frozen in `forecast-e210.json` before any E210 datum), **REPORTED** (the scorer's summaries and E210.md 8's reported lines, never verdicts), **post hoc** (the card's own constant), **desk check of code** (this lane's checks and re-runs, and verify-e210d's own code). Every check named here ran on aifoundry2 under `/usr/bin/python3` 3.12.3 (`-I -B`).*

**The words.** The frozen scorer (`score_e210.py` as re-frozen by A1, sha256 `42e26343...`), run by the kit's step 13 on this directory's committed `data-e210.json`, printed: **R0 PASS** (146 checks read; none missing, none bad); **B5 PASS** (13 of 13 scored test cases inside the switch route's band; 10 needed); **B10 (REPORTED) PASS** 13 of 13; the time equality **T PASS** in all 20 cases. Head to head over the 13 scored test cases, **R1, the switch route, is BETTER** than R4, the null (H1: 10 to 1, 2 ties), than R3, the raw bit-flip price (H2: 12 to 0, 1 tie), and than R3L, the bit-flip price with one scale (H3: 10 to 0, 3 ties); **H4**, R1 against R2 (MM1-v1's kind term), is **UNDECIDED** (4 to 0, 1 tie), as E210.md 8 stated before the data. With the pattern as the unit (A1 item 3, REPORTED): H1p UNDECIDED, H2p R1 BETTER, H3p R1 BETTER, H4p UNDECIDED. R1's errors on the 13 scored cases run from -0.844 to +0.785 W, **0.481 W rms, 1.87% of D** (REPORTED), against 3.85 W for R3L, 5.13 W for R4, 12.17 W for R3 and 5.57 W for R2 on its 5 cases. verify-e210d's own code gives every one of these verdicts, counts and numbers.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e210-A.json` | 65,860 | `4b9072a1acc76b8b0f5d8fd213dc244f8308b8114c365d6ad696fdb21b31d379` | the frozen scorer's output (`score_e210.py`, registered sha256 `42e26343...`): every rule, case, block, route error, head-to-head result and reported line |
| `scores-e210-A.txt` | 3,780 | `9be2a9bb8301eab806d877b48217e909a516dc1c8b9e25e25814031551edbb8f` | its text, written by the scorer itself (its `--txt`) |
| `scores-e210-A.printed.txt` | 3,780 | `9be2a9bb8301eab806d877b48217e909a516dc1c8b9e25e25814031551edbb8f` | its printed lines (step 13's capture of the call) |
| `README.md.dated-note-1.md` | (this note) | listed in `SHA256SUMS-note1` | this dated note |
| `SHA256SUMS-note1` | 6 lines | (not listed in itself) | the four files above (the three outputs and this note), and the two files `SHA256SUMS` does not list: `README.md` and `SHA256SUMS` |

The three output files are card-e210's RB_OUT files byte for byte. `scores-e210-A.txt` and `scores-e210-A.printed.txt` hold the same bytes: the scorer's `main()` writes its one text to the `--txt` file and then prints it, and step 13 copies what it printed. With `SHA256SUMS` (762 entries) and `SHA256SUMS-note1`, every file of this directory is in a list except `SHA256SUMS-note1` itself.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e210.sh A`) is the runbook log's last five lines (lines 103-107), all at 12:44:56 PST, each rc 0, one process for the five calls. Call 1 printed the data commit `6689d68f` and its subject; call 2 (the directory clean) printed nothing; call 3 read all 762 `SHA256SUMS` entries OK, in the list's order; call 4 printed "HISTORY OK: HEAD descends from the registration 7b59f7191d76 (subtree adef3701); 47 additions and nothing else under t..."; call 5, the frozen scorer on `data-e210.json` with `--out` and `--txt`, printed the lines of section 3. The log shows no earlier run of the scorer on data (its stand-in self-test ran once, at step 3, 11:06:00 PST, rc 0).
- **The bytes and their times.** The JSON was last written at 12:44:56.564 and the text at 12:44:56.566 PST, both inside call 5; the printed copy at 12:44:56.573, after call 5's capture closed. The printed lines equal that capture byte for byte, and they rebuild exactly from the JSON by the scorer's own `text()` (taken from the committed source, with the JSON's rules and cases put back in the order the scorer builds them: the JSON is written with sorted keys).
- **The commit before it.** The data commit `6689d68f` was made at 12:44:27 PST and pushed at 12:44:33 (the lab clone's record of the push); the card lane removed THE QUIET HOLD and released its booking at 12:44:50 and ran step 13 at 12:44:56. The lab clone's HEAD at the step was the data commit itself (its next move came at 12:45:00, another lane's E209 note).
- **The frozen files.** The registration list's 523 files and the list have one blob each at `7b59f719` (the registration, pushed 08:48:35 PST), `8f420314` (the kit, pushed 08:48:51), `75ecdd29` (the seal note, pushed 11:02:49), `6689d68f` and `ea3fa3ce` (the lab's head when this note was written); the kit list's 45 files and the list from `8f420314` on. `score_e210.py` at the data commit is E210.md 0's re-frozen scorer (A1 item 6, `42e263431d68b0ee...`); its two pins equal the sha256 of `forecast-e210.json` (`dbc2d3f3...`) and `points-e210.json` (`5773671b...`) at the data commit, E210.md 0's lines, and the JSON's own `frozen` field.
- **The re-runs** (13:16 PST, this lane): (1) the step's command in the lab clone's own tree, (2) the same under an audit hook that lists every file it opens, and (3) in a fresh tree holding only the four committed files it opened (`score_e210.py`, `forecast-e210.json`, `points-e210.json` and `data-e210.json`, taken from `6689d68f`'s objects; no bytecode cache): each run's three outputs equal RB_OUT's byte for byte; the clone read 0 status lines before and after.
- **verify-e210d** (desk; its own code, importing nothing from the kit, the scorer or any forecaster) re-derived every run from the raw files (4,002 fields equal `data-e210.json`) and scored every rule against the frozen forecasts: 951 values equal the scorer's JSON (worst relative difference 1.5e-16); its re-runs of the frozen scorer reproduced the three files byte for byte. This lane compared 1,143 values of the scorer's JSON with verify-e210d's scoring and with `forecast-e210.json` (worst relative difference 4.2e-15), and re-derived each case's head-to-head result, each pattern-level unit and both card constants with its own arithmetic: all equal.

## 3. The rules: their registered words, the verdicts, verify-e210d beside

The scorer's printed lines (`scores-e210-A.txt`, verbatim):

```
E210 scored: R0 PASS

B5: PASS (13 of 13 scored test cases; needed 10)
B10_REPORTED: PASS (13 of 13 scored test cases; needed 10)
H1 R1 against R4: R1 BETTER (R1 10, R4 1, ties 2; needed 10)
H2 R1 against R3: R1 BETTER (R1 12, R3 0, ties 1; needed 10)
H3 R1 against R3L: R1 BETTER (R1 10, R3L 0, ties 3; needed 9)
H4 R1 against R2: UNDECIDED (R1 4, R2 0, ties 1; needed 5)
H1p (REPORTED, A1 item 3: the pattern as the unit) R1 against R4: UNDECIDED (R1 6, R4 1, ties 1 of 8 patterns; needed 7)
H2p (REPORTED, A1 item 3: the pattern as the unit) R1 against R3: R1 BETTER (R1 7, R3 0, ties 1 of 8 patterns; needed 7)
H3p (REPORTED, A1 item 3: the pattern as the unit) R1 against R3L: R1 BETTER (R1 6, R3L 0, ties 2 of 8 patterns; needed 6)
H4p (REPORTED, A1 item 3: the pattern as the unit) R1 against R2: UNDECIDED (R1 2, R2 0, ties 1 of 3 patterns; needed 3)

zeros@S1         control   dW  -29.513 W (SE 0.078; -0.9910 D) T PASS B5 -    | errors W: R1     n/f R3     n/f R3L     n/f R2     n/f R4  +0.267
ones@S1          control   dW  -20.283 W (SE 0.078; -0.6811 D) T PASS B5 -    | errors W: R1  +0.285 R3 +15.285 R3L  +0.297 R2     n/f R4  +0.300
sparse50@S1      control   dW  -18.480 W (SE 0.078; -0.6206 D) T PASS B5 -    | errors W: R1     n/f R3     n/f R3L     n/f R2     n/f R4  +0.173
negzero@S1       test      dW  -20.728 W (SE 0.064; -0.6960 D) T PASS B5 PASS | errors W: R1  +0.785 R3 +15.727 R3L  +0.738 R2     n/f R4  -0.144
signs@S1         test      dW  -16.352 W (SE 0.078; -0.5491 D) T PASS B5 PASS | errors W: R1  +0.379 R3 +18.686 R3L  +3.889 R2     n/f R4  +4.231
lowmant8@S1      test      dW  -14.152 W (SE 0.078; -0.4752 D) T PASS B5 PASS | errors W: R1  -0.568 R3 +17.611 R3L  +3.962 R2     n/f R4  +6.433
highmant8@S1     test      dW  -12.260 W (SE 0.078; -0.4117 D) T PASS B5 PASS | errors W: R1  -0.324 R3  +1.272 R3L  -4.127 R2     n/f R4  +8.326
bhalfeq@S1       test      dW   -9.153 W (SE 0.064; -0.3074 D) T PASS B5 PASS | errors W: R1  -0.432 R3 +12.245 R3L  +2.561 R2  -9.156 R4  -9.153
badjeq@S1        test      dW   -0.030 W (SE 0.064; -0.0010 D) T PASS B5 PASS | errors W: R1  -0.012 R3  +0.059 R3L  +0.021 R2  -0.026 R4  -0.030
hd4@S1           test      dW   -5.790 W (SE 0.064; -0.1944 D) T PASS B5 PASS | errors W: R1  -0.844 R3 +15.936 R3L  +6.187 R2  -5.609 R4  -5.790
arow50@S1        reported  dW  -12.529 W (SE 0.064; -0.4207 D) T PASS B5 -    | errors W: R1     n/f R3     n/f R3L     n/f R2     n/f R4 -12.052
zeros@S2         control   dW  -20.464 W (SE 0.078; -0.9967 D) T PASS B5 -    | errors W: R1     n/f R3     n/f R3L     n/f R2     n/f R4  +0.068
ones@S2          control   dW  -14.091 W (SE 0.078; -0.6863 D) T PASS B5 -    | errors W: R1  -0.115 R3  +8.633 R3L  -0.115 R2     n/f R4  -0.115
sparse50@S2      control   dW  -11.967 W (SE 0.078; -0.5828 D) T PASS B5 -    | errors W: R1     n/f R3     n/f R3L     n/f R2     n/f R4 -11.967
negzero@S2       test      dW  -14.592 W (SE 0.078; -0.7108 D) T PASS B5 PASS | errors W: R1  +0.538 R3  +9.249 R3L  +0.502 R2     n/f R4  -0.617
lowmant8@S2      test      dW   -9.600 W (SE 0.078; -0.4676 D) T PASS B5 PASS | errors W: R1  -0.437 R3 +10.303 R3L  +2.336 R2     n/f R4  +4.376
highmant8@S2     test      dW   -8.514 W (SE 0.078; -0.4147 D) T PASS B5 PASS | errors W: R1  -0.271 R3  +0.594 R3L  -2.563 R2     n/f R4  +5.462
bhalfeq@S2       test      dW   -5.464 W (SE 0.078; -0.2661 D) T PASS B5 PASS | errors W: R1  -0.272 R3  +7.220 R3L  +1.567 R2  -5.468 R4  -5.464
hd4@S2           test      dW   -3.424 W (SE 0.078; -0.1667 D) T PASS B5 PASS | errors W: R1  -0.363 R3  +9.562 R3L  +3.879 R2  -3.194 R4  -3.424
maxalte@S2       test      dW   +2.249 W (SE 0.078; +0.1095 D) T PASS B5 PASS | errors W: R1  +0.399 R3 -16.618 R3L  -8.341 R2     n/f R4  +2.249
```

Each rule's registered words (E210.md 8, its table's two columns joined by "; threshold:", and A1, quoted with their emphasis and code marks left out), the scorer's verdict, and verify-e210d's:

- **R0, the checks.** "every check of C of every run (blocks, ties, the probe, the smoke) exact or approx; threshold: one verdict; a FAIL labels every other verdict"; A1 item 5: "R0 now reads FAIL when any check a process printed is not exact or approx; PASS when checks were read and every one is; NO DATA when none was read. A process that printed no check is REPORTED apart by name". **The scorer: PASS** (146 checks read; printed no check: none; bad: none). verify-e210d: PASS (146 checks, 0 missing, 0 bad).
- **Q, the quorum.** "a block (R, P, P, R) is complete when its four runs ran, each with a counted launch, every check good, its host record the case's (arm, fp32, 1,024 minions, 0xffffffff) and every counted sample at 590-610 MHz; threshold: a test case needs 2 complete blocks, a control or the reported case 1; else NO DATA". **The scorer: every case has its quorum**: the four S1 test cases negzero, bhalfeq, badjeq and hd4 and the reported arow50 on 3 of 3 blocks; the other nine test cases on 2 of 3 (the card-time cut, clause 2); each control on 2 of 2. verify-e210d: the same complete blocks, case by case.
- **T, the time equality.** "per complete block, the pattern runs' mean cycles an op within +-0.1% of the flanking random runs' mean, and their mean t_gemm within +-0.1%; threshold: a case passes when every complete block does; a case that fails T is reported, not scored for switches (out of B5, B10 and H)". **The scorer: PASS in all 20 cases**; the worst complete block read 0.0025% in cycles an op and 0.0149% in t_gemm against 0.1%. verify-e210d: 20 of 20 (its worst 0.0025% and 0.0149%).
- **B5, the switch route's band.** "per scored test case, |dJ_R1 - dJ| <= max(0.05 D_S, 2 SE), D_S the committed D at the shape (S1 29.78 W, S2 20.53 W); every band absolute, so a case under about 3 W is treated as any other; threshold: PASS when at least 75% of the scored test cases pass (at least 6 scored, else TOO FEW; none: NO DATA)". **The scorer: PASS**, 13 of 13 (10 needed); every band was 0.05 D (2 SE was smaller in each case), and the largest error used 0.57 of its band (hd4@S1: -0.844 W against 1.489 W). verify-e210d: PASS 13 of 13, and 13 of 13 again with E206's t_gemm in the SE floor.
- **B10 (REPORTED).** "the same at 10% of D; threshold: REPORTED". **The scorer: PASS** 13 of 13. verify-e210d: PASS 13 of 13.
- **H1, H2, H3, the head to head.** "per scored test case, e = dJ - forecast for R1 and for R4 (H1), R3 (H2), R3L (H3); decided when ||e_R1| - |e_k|| >= 2 SE, else a tie (dropped); threshold: the exact two-sided sign test at 0.05 over the decided cases: R1 BETTER, Rk BETTER or UNDECIDED (n decided needs: 10 of 12, 11 of 13; under 6 it cannot decide)". **The scorer:** H1 (R1 against R4) R1 BETTER (R1 nearer 10, R4 nearer 1, ties 2; 11 decided, 10 needed; exact two-sided p 0.01171875); H2 (against R3) R1 BETTER (R1 nearer 12, R3 nearer 0, ties 1; 12 decided, 10 needed; exact two-sided p 0.00048828125); H3 (against R3L) R1 BETTER (R1 nearer 10, R3L nearer 0, ties 3; 10 decided, 9 needed; exact two-sided p 0.001953125). verify-e210d: the same counts and verdicts (p 0.01171875, 0.00048828125, 0.001953125).
- **H4.** "R1 against R2 on the cases R2 forecasts; threshold: the same; R2 forecasts 5 test cases, so H4 cannot decide (stated now); its per-case results are reported". **The scorer:** UNDECIDED (R1 nearer 4, R2 nearer 0, ties 1; 4 decided, 5 needed (more than were decided, so it cannot decide); exact two-sided p 0.125). verify-e210d: UNDECIDED 4/0/1 (p 0.125).
- **The paired difference and its SE** (E210.md 8): "The measured paired difference of a case = the mean over its complete blocks of mean(J(P1), J(P2)) - mean(J(R1), J(R2)), each run's J = (p_work - p_rest) t_gemm; SE = max(sd of the block values / sqrt(n), 0.11 W x t_gemm / sqrt(n)), n its complete blocks." The case values are in sections 4 and 5.
- **H1p-H4p, the pattern as the unit** (A1 item 3, REPORTED beside H1-H4): "per pattern with a scored test case both routes forecast, d_p = the mean over its cases of (|e_R1| - |e_k|) / D_S and SE_p = sqrt(sum of (SE_J / D_S)^2) / n_p, decided when |d_p| >= 2 SE_p, else a tie (dropped); the exact two-sided sign test at 0.05 over the decided patterns (8 patterns: it decides only at 6 of 6, 7 of 7 or 8 of 8; H4p's 3 patterns never decide)"; "The registered verdicts stay as registered; each BETTER is read beside its pattern-level line." **The scorer:** H1p UNDECIDED (R1 6, R4 1, ties 1 of 8 patterns; 7 needed; p 0.125); H2p R1 BETTER (R1 7, R3 0, ties 1 of 8 patterns; 7 needed; p 0.015625); H3p R1 BETTER (R1 6, R3L 0, ties 2 of 8 patterns; 6 needed; p 0.03125); H4p UNDECIDED (R1 2, R2 0, ties 1 of 3 patterns; 3 needed; p 0.5). verify-e210d: the same, pattern by pattern (section 6).
- **The reported lines** (E210.md 8, never a verdict): "each route's rms and mean error over the scored test cases (W and fractions of D); a paired bootstrap of mean |e_R1| - mean |e_k| (10,000 resamples of the cases, seed E210|bootstrap, the 2.5-97.5% interval); R1_hi and R1pure; the card's own constant (least squares of dJ - dL on dS over the scored test cases, through the origin) beside the calibrated kappa_S" and the controls, arow50 and the random runs' drift: section 7.

## 4. Every scored test case: the measured paired difference, the time equality and B5, with verify-e210d beside

dW is the measured paired difference in W over random at the same shape (dJ over the case's own mean t_gemm), measured; SE as registered; D_S the committed D (S1 29.78 W, S2 20.53 W). R1's error is the measured dW less R1's frozen forecast. "=" in the last column: verify-e210d's own scoring gives the same blocks, values and results (the largest relative difference 4.2e-15).

| case | complete blocks | dW (W) | SE (W) | dW / D_S | T: worst block, cycles / t_gemm | B5 band (W) | R1 error (W) | of its band | B5 | verify-e210d |
|---|---|---|---|---|---|---|---|---|---|---|
| negzero@S1 | 3 of 3 | -20.728 | 0.064 | -0.6960 | 0.0005% / 0.0077% | 1.489 | +0.785 | 0.53 | PASS | = |
| signs@S1 | 2 of 3 | -16.352 | 0.078 | -0.5491 | 0.0006% / 0.0062% | 1.489 | +0.379 | 0.25 | PASS | = |
| lowmant8@S1 | 2 of 3 | -14.152 | 0.078 | -0.4752 | 0.0016% / 0.0051% | 1.489 | -0.568 | 0.38 | PASS | = |
| highmant8@S1 | 2 of 3 | -12.260 | 0.078 | -0.4117 | 0.0007% / 0.0084% | 1.489 | -0.324 | 0.22 | PASS | = |
| bhalfeq@S1 | 3 of 3 | -9.153 | 0.064 | -0.3074 | 0.0025% / 0.0149% | 1.489 | -0.432 | 0.29 | PASS | = |
| badjeq@S1 | 3 of 3 | -0.030 | 0.064 | -0.0010 | 0.0015% / 0.0122% | 1.489 | -0.012 | 0.01 | PASS | = |
| hd4@S1 | 3 of 3 | -5.790 | 0.064 | -0.1944 | 0.0010% / 0.0064% | 1.489 | -0.844 | 0.57 | PASS | = |
| negzero@S2 | 2 of 3 | -14.592 | 0.078 | -0.7108 | 0.0011% / 0.0073% | 1.027 | +0.538 | 0.52 | PASS | = |
| lowmant8@S2 | 2 of 3 | -9.600 | 0.078 | -0.4676 | 0.0010% / 0.0014% | 1.027 | -0.437 | 0.43 | PASS | = |
| highmant8@S2 | 2 of 3 | -8.514 | 0.078 | -0.4147 | 0.0003% / 0.0054% | 1.027 | -0.271 | 0.26 | PASS | = |
| bhalfeq@S2 | 2 of 3 | -5.464 | 0.078 | -0.2661 | 0.0008% / 0.0062% | 1.027 | -0.272 | 0.26 | PASS | = |
| hd4@S2 | 2 of 3 | -3.424 | 0.078 | -0.1667 | 0.0001% / 0.0065% | 1.027 | -0.363 | 0.35 | PASS | = |
| maxalte@S2 | 2 of 3 | +2.249 | 0.078 | +0.1095 | 0.0004% / 0.0008% | 1.027 | +0.399 | 0.39 | PASS | = |

## 5. Each route's error on the paired differences, and the head to head per case, with verify-e210d beside

Errors in W, the measured dW less each route's frozen forecast (blind); n/f = the route does not forecast the case. A head-to-head cell names the route nearer the measured value, or a tie when the two errors' sizes differ by less than 2 SE (E210.md 8).

| case | R1 | R3 | R3L | R2 | R4 | 2 SE (W) | H1: R1 / R4 | H2: R1 / R3 | H3: R1 / R3L | H4: R1 / R2 | verify-e210d |
|---|---|---|---|---|---|---|---|---|---|---|---|
| negzero@S1 | +0.785 | +15.727 | +0.738 | n/f | -0.144 | 0.127 | R4 | R1 | tie | - | = |
| signs@S1 | +0.379 | +18.686 | +3.889 | n/f | +4.231 | 0.156 | R1 | R1 | R1 | - | = |
| lowmant8@S1 | -0.568 | +17.611 | +3.962 | n/f | +6.433 | 0.156 | R1 | R1 | R1 | - | = |
| highmant8@S1 | -0.324 | +1.272 | -4.127 | n/f | +8.326 | 0.156 | R1 | R1 | R1 | - | = |
| bhalfeq@S1 | -0.432 | +12.245 | +2.561 | -9.156 | -9.153 | 0.127 | R1 | R1 | R1 | R1 | = |
| badjeq@S1 | -0.012 | +0.059 | +0.021 | -0.026 | -0.030 | 0.127 | tie | tie | tie | tie | = |
| hd4@S1 | -0.844 | +15.936 | +6.187 | -5.609 | -5.790 | 0.127 | R1 | R1 | R1 | R1 | = |
| negzero@S2 | +0.538 | +9.249 | +0.502 | n/f | -0.617 | 0.156 | tie | R1 | tie | - | = |
| lowmant8@S2 | -0.437 | +10.303 | +2.336 | n/f | +4.376 | 0.156 | R1 | R1 | R1 | - | = |
| highmant8@S2 | -0.271 | +0.594 | -2.563 | n/f | +5.462 | 0.156 | R1 | R1 | R1 | - | = |
| bhalfeq@S2 | -0.272 | +7.220 | +1.567 | -5.468 | -5.464 | 0.156 | R1 | R1 | R1 | R1 | = |
| hd4@S2 | -0.363 | +9.562 | +3.879 | -3.194 | -3.424 | 0.156 | R1 | R1 | R1 | R1 | = |
| maxalte@S2 | +0.399 | -16.618 | -8.341 | n/f | +2.249 | 0.156 | R1 | R1 | R1 | - | = |
| **count** | | | | | | | R1 10, R4 1, tie 2 | R1 12, R3 0, tie 1 | R1 10, R3L 0, tie 3 | R1 4, R2 0, tie 1 | = |

## 6. The head to head with the pattern as the unit (A1 item 3, REPORTED), and H1 read beside H1p

Per pattern, d_p is the mean over its cases of (|e_R1| - |e_k|) / D_S and SE_p as A1 item 3 registers it, both as fractions of D; a negative d_p favours R1. The result is the nearer route, or a tie when |d_p| < 2 SE_p.

| pattern | cases | H1p: against R4 | H2p: against R3 | H3p: against R3L | H4p: against R2 | verify-e210d |
|---|---|---|---|---|---|---|
| negzero | S1, S2 | +0.0088 (SE 0.0022): R4 | -0.4630 (SE 0.0022): R1 | +0.0017 (SE 0.0022): tie | - | = |
| signs | S1 | -0.1294 (SE 0.0026): R1 | -0.6147 (SE 0.0026): R1 | -0.1179 (SE 0.0026): R1 | - | = |
| lowmant8 | S1, S2 | -0.1944 (SE 0.0023): R1 | -0.5264 (SE 0.0023): R1 | -0.1033 (SE 0.0023): R1 | - | = |
| highmant8 | S1, S2 | -0.2607 (SE 0.0023): R1 | -0.0238 (SE 0.0023): R1 | -0.1197 (SE 0.0023): R1 | - | = |
| bhalfeq | S1, S2 | -0.2729 (SE 0.0022): R1 | -0.3676 (SE 0.0022): R1 | -0.0673 (SE 0.0022): R1 | -0.2730 (SE 0.0022): R1 | = |
| badjeq | S1 | -0.0006 (SE 0.0021): tie | -0.0016 (SE 0.0021): tie | -0.0003 (SE 0.0021): tie | -0.0005 (SE 0.0021): tie | = |
| hd4 | S1, S2 | -0.1576 (SE 0.0022): R1 | -0.4774 (SE 0.0022): R1 | -0.1753 (SE 0.0022): R1 | -0.1489 (SE 0.0022): R1 | = |
| maxalte | S2 | -0.0901 (SE 0.0038): R1 | -0.7899 (SE 0.0038): R1 | -0.3868 (SE 0.0038): R1 | - | = |
| **verdict** | | UNDECIDED (6/1/1) | R1 BETTER (7/0/1) | R1 BETTER (6/0/2) | UNDECIDED (2/0/1) | = |

**H1 beside H1p** (verify-e210d's note 2; A1 item 3 reads each BETTER beside its pattern-level line). The registered H1 stands: R1 BETTER than R4, 10 to 1 with 2 ties (p 0.01171875). With the pattern as the unit it is UNDECIDED: 6 to 1 with 1 tie of 8 patterns, where 7 of 7 decided are needed. The one pattern R4 wins is negzero: at S1, R4's forecast (ones' level) is nearer the measured -20.728 W than R1's (errors -0.144 W against +0.785 W); at S2 the two are a tie (+0.538 W against -0.617 W, 2 SE 0.156 W); so negzero's d_p is +0.0088 D (SE 0.0022). Every other decided pattern goes to R1, by 0.09 to 0.27 D. H2 and H3 hold at the pattern level (7 to 0 and 6 to 0); H4p, like H4, cannot decide (3 patterns).

## 7. Beside the verdicts (REPORTED, never verdicts)

**Each route's error over the 13 scored test cases** (the scorer's summaries; verify-e210d's equal):

| route | cases | rms (W) | mean (W) | rms / D_S |
|---|---|---|---|---|
| R1, the switch route | 13 | 0.481 | -0.109 | 1.87% |
| R1's high column | 13 | 0.481 | -0.109 | 1.87% |
| R1g, two classes | 13 | 0.481 | -0.109 | 1.87% |
| R1pure, no line term | 13 | 0.530 | -0.055 | 2.33% |
| R3L, the bit-flip price with one scale | 13 | 3.849 | +0.816 | 16.19% |
| R4, the null (nearest kind) | 13 | 5.128 | +0.496 | 19.71% |
| R2, MM1-v1's kind term | 5 | 5.575 | -4.691 | 21.22% |
| R3, the raw bit-flip price | 13 | 12.165 | +7.834 | 47.48% |

R1's high column and R1g equal R1 on every scored case: for an ungated pattern the clock part of the count is random's and cancels (E210.md 7), and no gated case is scored.

**The paired bootstrap** of mean |e_R1| - mean |e_k| over the scored cases (10,000 resamples, seed `E210|bootstrap`; mJ a GEMM, so the longer S2 GEMMs weigh more): H1 against R4 -0.714 mJ (2.5-97.5%: -1.119 to -0.356); H2 against R3 -1.879 mJ (2.5-97.5%: -2.957 to -0.940); H3 against R3L -0.586 mJ (2.5-97.5%: -1.080 to -0.220); H4 against R2 -0.780 mJ (2.5-97.5%: -1.469 to -0.211). Every interval lies below zero (R1 nearer). verify-e210d's own bootstrap gives the same numbers.

**The card's own constant (post hoc)**, least squares through the origin of the measured dJ less MM1-v1's line term on the counted switch difference, over the scored test cases at each shape: **S1 kappa 1.6767 x 10^16 switches a J** (7 cases; b 5.9640e-17 J a switch) against the calibrated 1.6733 x 10^16 (ratio 1.0020); **S2 kappa 1.6235 x 10^16** (6 cases; b 6.1594e-17) against 1.6367 x 10^16 (ratio 0.9920). This lane's arithmetic and verify-e210d's give the same constants.

**The controls and the reported case.** R4's forecast for a control is the committed value of that kind (E206 arm A's zeros and sparse50, ones carried over from aifoundry1 card 1), so its error is the control measured today against that value:

| case | measured dW (W) | the committed value R4 carries (W) | R4's error (W) | R1 (W) | R1g (W) | R1pure (W) |
|---|---|---|---|---|---|---|
| zeros@S1 | -29.513 | -29.780 | +0.267 | n/f | +0.267 | -7.824 |
| ones@S1 | -20.283 | -20.584 | +0.300 | +0.285 | +0.285 | +0.285 |
| sparse50@S1 | -18.480 | -18.653 | +0.173 | n/f | +1.809 | -2.892 |
| zeros@S2 | -20.464 | -20.533 | +0.068 | n/f | +0.068 | -5.721 |
| ones@S2 | -14.091 | -13.976 | -0.115 | -0.115 | -0.115 | -0.115 |
| sparse50@S2 | -11.967 | +0.000 | -11.967 | n/f | +0.880 | -1.826 |
| arow50@S1 | -12.529 | -0.477 | -12.052 | n/f | -0.453 | -2.573 |

At S2 no sparse50 point is committed, so R4's nearest kind there is random (0 W). arow50 (half the multiply-adds gated) is reported only; R1g, the one route that forecasts it, misses by the amount in its row; R4's nearest kind for it is real.

**The random runs' drift** (W over idle): random@S1, 32 runs, first 33.255 W, last 33.690 W; random@S2, 20 runs, first 24.805 W, last 24.820 W. Every block is a pattern between two random runs, so a slow drift cancels in dW.

## 8. The findings, answered as dated clauses (Tue 17 Nov 2026, PST)

1. **The scorer's outputs were not committed** (card-e210's item for a later lane; verify-e210d's open item 5). Answered by this note: they are committed here, byte for byte, with their printed lines and `SHA256SUMS-note1`, and section 2 gives where they came from.
2. **The card-time cut and its cause** (card-e210's finding 1; verify-e210d's note 1). E210.md 6 registered: "Card time (plan): 171 runs at 26 s (S1) and 22.5 s (S2) a run (E206 arm A's pace on this card, 21.97 s a run on average with 8-14 s die-gate waits after a 59 W run) and about 4 minutes of opening: about 73 card-minutes. The cap: no run starts after 85 card-minutes; the session ends at 95 after the run in progress (the round's cap is 100). The registered subset if cut: the opening and passes 1-4 (every kind twice at both shapes; about 55 card-minutes)." At 85.01 card-minutes the rule left runs 143-171 unstarted (29 runs); the registered subset (the opening and passes 1-4) is complete. So 9 of the 13 test cases are scored on 2 of 3 blocks (signs, lowmant8, highmant8 at S1; negzero, lowmant8, highmant8, bhalfeq, hd4, maxalte at S2), the other four (negzero@S1, bhalfeq@S1, badjeq@S1, hd4@S1) and arow50 on 3 of 3, and each control on 2 of 2. The cause, from this directory's `session/runs/*/run.json` (desk arithmetic of the measured records): 132 of 142 runs waited at the 52.0 C die gate before their rest, 2,009 s in all (33.5 minutes); the median wait was 12.75 s over all 142 runs (13.5 s over the 132 that waited) and the longest 34.5 s. From the first run's rest to the last run's end the session took 35.1 s a run (verify-e210d's reading: 35.2 s), against the plan's 26 s (S1) and 22.5 s (S2), which assumed E206 arm A's 8-14 s gate waits. The cut changes no verdict: every rule decided as registered. A later kit on this card under the same gate can plan from this pace.
3. **H4 UNDECIDED** (card-e210's note). As E210.md 8 stated before the data ("the same; R2 forecasts 5 test cases, so H4 cannot decide (stated now); its per-case results are reported"): R1 is nearer at 4 of the 5 cases R2 forecasts (bhalfeq and hd4 at both shapes); at badjeq@S1 the two are a tie (errors -0.012 W and -0.026 W).
4. **H1 with the pattern as the unit** (verify-e210d's note 2): read beside H1p in section 6. The registered H1 is unchanged.
5. **The seal note's push time** (verify-e210d's note 3). The README's departure 6 says the seal note `75ecdd29` was "pushed 11:02:46 PST". 11:02:46 is its commit time; the lab clone's record of the push reads 11:02:49 PST. Both come before E210's booking (11:05:20) and its first card command (11:11:19). Nothing else changes; the README is not changed (new files only).
6. **The rest windows** (verify-e210d's note 4). In this directory's run files, 38 of the 142 runs' 10 s rest windows are not exactly 10,000 ms ending at the process's start: 26 are 10,001 ms long and the other 12 end 1 ms before the start (millisecond rounding). The reducer reads p_rest from the samples in the 5 s before each process's start, not from the window's ends (E210.md 6: "p_rest = the median of its last 5 s"), and verify-e210d's own reduction, which reads it so, equals `data-e210.json` in all 4,002 fields; nothing changes.
7. **card-e210's item for the orchestrator** (to report E210's end, for which four of E212's planned sessions with its own sign tile waited) concerns E212, not this directory; the orchestrator reported it at 12:47 PST.
8. **card-e210's incidents.** Its progress-log slip about another lane (11:00:38, corrected 11:06:42) is in that lane's log only; nothing in this directory carries it. The tier-class matches its scan reviewed (a word inside his quoted words in `README.md`, the runtime's address prints in the `.err` files, a tile file name and a lane-folder name inside the never-run reports) are in files committed before this note; this note's new files match no tier class.

**Not here, by the rules:** the model session's sealed E210 forecast (its sha256 registered in `75ecdd29` before the first card command) is not scored by the lab, and nothing of it is quoted.

## 9. NOT RUN

- The private-number scan (this lane read nothing outside the lab's own files and the round's lane records).
- The scorer's stand-in self-test and the kit's desk tests (they ran at step 3, rc 0): not re-run.
- verify-e210d's code: its outputs were read and compared, not re-run.
- This lane wrote no bootstrap of its own: the intervals come from the scorer (re-run, the same bytes) and agree with verify-e210d's own.
- Any read of aifoundry3 or another box, and any card, device or simulator.

SPDX-License-Identifier: Apache-2.0
