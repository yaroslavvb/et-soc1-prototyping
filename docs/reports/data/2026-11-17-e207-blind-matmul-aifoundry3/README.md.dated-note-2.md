# E207 data, dated note 2: the frozen scorer's output and the after-score tool's, committed beside the data byte for byte - every registered rule PASS and MM1-v1 BETTER on all four head-to-head rules, with verify-e207d's re-derivation beside each result

*Tue 17 Nov 2026 (week 47), PST; written at about 08:55 PST by Q199's lane `scores-e207`, after this directory's data commit `867f6a3f` (07:58:54 PST, pushed 07:58:58) and after the day's data verifier `verify-e207d` (HOLDS). It adds new files only: no committed file, rule, band, forecast, label or scorer is changed. Labels: **registered** (E207.md with its amendment A1, the kit), **measured** (this directory's records), **desk check of code** (this lane's checks and re-runs, verify-e207d's own code), **blind** (frozen before any E207 datum), **REPORTED** (never a verdict) and **post hoc**, as each line says. Every desk step ran on aifoundry2 under `/usr/bin/python3` 3.12.3 with `-I -B`.*

**The words.** The frozen scorer, run by the kit's step 13 on this directory's committed `data-e207.json`, printed: **R0 PASS** (112 checks, 0 wrong); **T1 PASS** 45/47, **T2 PASS** 44/47, **T3 PASS** 45/47 (cycles and seconds per case); **E1 PASS** 50/53, **E2 PASS** 48/53, **E3 PASS** 51/53, **E4 PASS** 50/53 (joules per point); **S6 PASS** 53/53 (the clock); **H1, H2, H3 and H4: MM1-v1 BETTER** (MM1-v1 closer at 39, 45, 47 and 47 cases or points, the other model at 8, 2, 2 and 2; p 5.54e-06, 1.60e-11, 4.36e-12 and 4.36e-12). The after-score tool (E207.md A1 item 3) read the labels file this directory holds (`ranbefore-e207-labels.json`: no point, no case), so **THE REGISTERED VERDICTS are the scorer's own**, rule by rule and count by count. **Blind:** MM1-v1's, F1's and F2's forecasts were pushed in `25d2e74e` at 21:14:57 PST Mon 16 Nov 2026, 9 h 52 min before the session's first card command (07:06:44 PST). verify-e207d scored all 13 rules with its own code and got the same verdicts, counts, cells, d values (worst difference 3.3e-16) and p values.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e207-A.json` | 295,071 | `be47e045da2ed6cfa8d0841ae3ce3318e336e70ce118d9712e214d1e76baa7eb` | the frozen scorer's output (`score_e207.py`, registered sha256 `209121fa...`): every rule, cell, d value, summary and reading |
| `scores-e207-A.txt` | 716 | `dfa35ae0ed5ff49f37afd3776d1fcb9eafa3a072b844f95a622d20663564f8e2` | its printed lines (step 13's capture of the call) |
| `postscore-e207-A.json` | 8,257 | `7921d90f9b00f58892eefac7a3b068d3a9eef331717af0c8613a35d2717564a8` | the after-score tool's output (`postscore_e207.py`, registered by A1, `ae3ddedf...`): THE REGISTERED VERDICTS, the family-level check, the checks read |
| `postscore-e207-A.txt` | 1,542 | `1b7fcadbc7a9e5dbfa89da99b7d05fb51598255fbd0048f751a4a216b2aee009` | its printed lines (step 13's capture of the call) |
| `README.md.dated-note-2.md` | (this note) | listed in `SHA256SUMS-note2` | this dated note |
| `SHA256SUMS-note2` | 9 lines | (not listed in itself) | the five files above but itself, and the four files `SHA256SUMS` does not list: `README.md`, `README.md.dated-note-1.md`, `ranbefore-e207-labels.json` and `SHA256SUMS` |

The four output files are card-e207's RB_OUT files byte for byte. With `SHA256SUMS` (589 entries) and `SHA256SUMS-note2`, every file of this directory is in a list except `SHA256SUMS-note2` itself.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e207.sh A`) is the runbook log's last six lines (lines 95-100), at 07:59:25 PST (calls 1-5) and 07:59:26 PST (call 6), each rc 0, one process for all six calls. Call 1 printed the data commit `867f6a3f` and its subject; call 2 (the directory clean) printed nothing; call 3 read all 589 `SHA256SUMS` entries OK, in the list's order; call 4 printed `HISTORY OK` naming the registration `3649245b7f22`; call 5 ran the frozen scorer, `/usr/bin/python3 -I -B tools/claims-v3/e207/score_e207.py docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json --out RB_OUT/scores-e207-A.json`; call 6 ran the after-score tool on that JSON with `--data-dir docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3`.
- **The bytes.** `scores-e207-A.txt` and `postscore-e207-A.txt` are the captures of calls 5 and 6 byte for byte; the scorer's lines also rebuild exactly from its JSON in its own print form. Each JSON was last written inside its own call (the scorer's at 07:59:25.812, the tool's at 07:59:26.009 PST), and the after-score JSON names the scorer's JSON by its sha256 (`be47e045...`). The log shows no earlier run of either program on data; the scorer's `--forecasts` and its two self-tests ran at step 3 (07:04:10-07:04:17 PST, rc 0).
- **The commit before it.** The data commit `867f6a3f` was made at 07:58:54 PST and pushed at 07:58:58; the card lane released its booking and THE QUIET HOLD at 07:59:04 and ran step 13 at 07:59:25.
- **The lab clone during the step.** Its HEAD at the step was `1393a649`, E211's registration, committed at 07:59:17 PST by another lane (Q204's land-e211) as a child of `867f6a3f`, all 39 of its files under `tools/claims-v3/e211/`. The card lane read 72 untracked lines right after the scorer: E211's kit, committed at 07:59:30 as `2b7f261f`, 72 new files, all under `tools/claims-v3/e211/`. None of them is a file either program opened or lies in a folder either imports from. The 43 committed files the two programs open (this lane's audited run, below) have one blob each at `867f6a3f`, at `1393a649` and at the lab's HEAD when this note was built (`7726e127`).
- **The frozen files.** The registration list's 24 files and the list have one blob each at `3649245b`, `117885d9` (the kit), `867f6a3f`, `1393a649` and `7726e127`; the kit list's 45 files and the list at `117885d9` onward; MM1-v1's frozen files of E207.md section 0 (9) at `25d2e74e` onward, each at its listed sha256. The scorer's five pins equal those files' sha256 at the data commit and the JSON's `pins`. `score_e207.py` is `209121fa...` (E207.md 0) and `postscore_e207.py` is `ae3ddedf...` (A1's list). `data-e207.json` is `e89d4149...`, the same bytes verify-e207d re-derived against.
- **The re-runs.** (1) In the lab clone's own tree at `030ffa42`, each program under an audit hook that lists every file it opens: both outputs, both printed texts, byte for byte equal to RB_OUT (08:38 PST; the clone's status 0 lines before and after). (2) In a pristine tree of exactly those 43 committed files, taken from the data commit `867f6a3f`'s objects, with no bytecode cache: the plain runs and the audited runs again byte for byte equal to RB_OUT and to the captures of calls 5 and 6 (08:39 PST). Every file the audited runs opened lies in that tree or the standard library (the import system also tried 13 bytecode-cache paths that do not exist there). Each run held one of the round's CPU slots at nice 10, with this box's own card out of reach.

## 3. The rules: their registered words, the verdicts, verify-e207d beside

The scorer's printed lines (`scores-e207-A.txt`, verbatim):

```
E207 scored (BLIND: MM1-v1, F1 and F2 were frozen (pushed 25d2e74e, 21:14:57 PST Mon 16 Nov 2026) before any E207 datum)
R0 PASS (112 checks, 0 wrong)
T1 PASS (45/47 within 0.13)
T2 PASS (44/47 within 0.16)
T3 PASS (45/47 within 0.13)
E1 PASS (50/53 within 0.15)
E2 PASS (48/53 within 0.16)
E3 PASS (51/53 within 0.05)
E4 PASS (50/53 within 0.13)
S6 PASS (53/53 within None)
H1 MM1-v1 BETTER (MM1-v1 closer 39, other closer 8, ties 0, p 5.539621596994948e-06)
H2 MM1-v1 BETTER (MM1-v1 closer 45, other closer 2, ties 0, p 1.6044054973463062e-11)
H3 MM1-v1 BETTER (MM1-v1 closer 47, other closer 2, ties 0, p 4.355626970209414e-12)
H4 MM1-v1 BETTER (MM1-v1 closer 47, other closer 2, ties 0, p 4.355626970209414e-12)
```

**MM1-v1's rules** (E207.md 7, its words): "Each case or point passes when |measured / MM1-v1 - 1| is within its band; a rule's verdict: PASS if at least 90% of its scored cases or points pass, FAIL otherwise, TOO FEW under 10, NO DATA with none." The band is twice the larger of MM1-v1's two held-out rms errors for that quantity, rounded up to a whole percent (E207.md 7). "The points under about 3 W over idle (b34, b38, b40: MM1-v1's own frozen flags, at 0.92-1.89 W; F1 puts them at 0.44-1.21 W, F2 at 0.38-1.13 W) are scored in absolute watts in E1 and E2: |W measured - W forecast| <= 0.215 W = 2 x SD_rep".

| rule | the registered words (E207.md 7) | band | scored | needed (90%) | the scorer (registered verdict) | verify-e207d's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | every check of C exact or approx (the smoke's, every point run's, counted or not, kept or set aside, and every tie run's); the smoke's cycles an op 50-250% of MM1-v1's counter-mean forecast at b01, b02 and b03. A FAIL labels every other verdict. | - | 112 checks | all | **PASS** (112 checks, 0 wrong; the smoke at 1.0447, 1.0892 and 1.0446 of the counter-mean forecast 784.25) | PASS (112, 0 wrong; 1.0447, 1.0892, 1.0446) | - | none |
| **T1** | cycles an op, the wall (cycles_max / passes / ops), per case | 13% | 47 | 43 | **PASS** (45/47) | PASS (45/47; the same cells) | 2 | gemmL1x2x2 fp32 0x3 (+16.3%); gemmL1x3x1 int8 (+16.0%) |
| **T2** | cycles an op, the counter's mean (the host's cycles_per_op), per case | 16% | 47 | 43 | **PASS** (44/47) | PASS (44/47; the same cells) | 1 | gemmL1x2x2 fp32 0x3 (+24.1%); gemmL1x2x2 fp32 0xfff (+17.5%); gemmL1x3x1 int8 (+16.2%) |
| **T3** | seconds a GEMM (t_gemm), per case | 13% | 47 | 43 | **PASS** (45/47) | PASS (45/47; the same cells) | 2 | gemmL1x2x2 fp32 0x3 (+16.4%); gemmL1x3x1 int8 (+16.1%) |
| **E1** | J over idle given the measured seconds, per point (at 3 W and above) | 15% (0.215 W at b34, b38, b40) | 53 | 48 | **PASS** (50/53) | PASS (50/53; the same cells) | 2 | b40 (-0.321 W); n02 (+24.9%); n03 (+16.7%) |
| **E2** | J over idle with the seconds forecast, per point (at 3 W and above) | 16% (0.215 W at b34, b38, b40) | 53 | 48 | **PASS** (48/53) | PASS (48/53; the same cells) | 0 | b34 (-0.228 W); b38 (-0.238 W); b40 (-0.539 W); n02 (+27.1%); n03 (+17.0%) |
| **E3** | J with the card at rest given the measured seconds and rest, per point | 5% | 53 | 48 | **PASS** (51/53) | PASS (51/53; the same cells) | 3 | n02 (+7.0%); n03 (+8.3%) |
| **E4** | J with the card at rest with the seconds forecast (the measured rest), per point | 13% | 53 | 48 | **PASS** (50/53) | PASS (50/53; the same cells) | 2 | b40 (+14.0%); n01 (+13.9%); n02 (+16.0%) |
| **S6** | the clock: every counted sample in 590-610 MHz (the lowest and the highest), per point. | 590-610 MHz | 53 | 48 | **PASS** (53/53) | PASS (53/53) | 5 | none (every point's counted samples at 600 MHz) |

**THE HEAD-TO-HEAD RULES** (E207.md 7, its words): "per case (time) or per point (energy), d = |ln(measured / other)| - |ln(measured / MM1-v1)| (at b34, b38, b40: |W - W_other| - |W - W_MM1-v1| in watts); MM1-v1 is closer where d > the tie, the other model where d < -the tie, a tie otherwise" (the ties: 0.001 in ln for cycles, 0.005 for joules, 0.05 W in watts). "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v1 BETTER if p <= 0.05 and it is closer in more cases than not; F1 BETTER (or F2 BETTER) if p <= 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none."

| rule | the registered words (E207.md 7) | over | MM1-v1 closer | the other closer | ties | p (exact, two-sided) | the scorer | verify-e207d | where the other model is closer |
|---|---|---|---|---|---|---|---|---|---|
| **H1** | cycles an op, the wall: MM1-v1 (cycles_per_op_wall) against F1 (F1_cycles_per_op) | 47 cases | 39 | 8 | 0 | 5.540e-06 | **MM1-v1 BETTER** | MM1-v1 BETTER (39/8/0, the same p) | gemmL1x3x2 int8; gemmL2x3x2 int8; gemmL3x2x2 int8; gemmL3x6x4 fp32 0x3; gemmL3x6x4 int8 0x3; gemmL1x2x2 fp32 0x3; gemmL1x2x2 fp32 0xfff; gemmL3x5x1 fp32 |
| **H2** | cycles an op, the counter's mean: MM1-v1 (cycles_per_op_mean) against F1 (its one cycles number) | 47 cases | 45 | 2 | 0 | 1.604e-11 | **MM1-v1 BETTER** | MM1-v1 BETTER (45/2/0, the same p) | gemmL1x2x2 fp32 0x3; gemmL1x3x1 int8 |
| **H3** | J over idle given the measured seconds: MM1-v1's given() against F2's given() | the 49 points both price | 47 | 2 | 0 | 4.356e-12 | **MM1-v1 BETTER** | MM1-v1 BETTER (47/2/0, the same p) | b18; b40; not compared: b49, b50, b51, b52 (no F2 price) |
| **H4** | J over idle with the seconds forecast: MM1-v1's frozen J against F2's frozen J | the 49 points both price | 47 | 2 | 0 | 4.356e-12 | **MM1-v1 BETTER** | MM1-v1 BETTER (47/2/0, the same p) | b18; b40; not compared: b49, b50, b51, b52 (no F2 price) |

The slack is the passing count less the count the 90% rule needs (REPORTED, desk arithmetic). E2 passes with none to spare; its nearest passing point is n01 at 0.55 of its band. In T1 and T3, gemmL3x6x4 int8 0x3 passes at 12.86% and 12.95% against the 13% band.

## 4. Every case: cycles and seconds (T1-T3) and the head-to-head H1 and H2, with verify-e207d beside

Errors are measured / MM1-v1 - 1 (the scorer's `err`); d is the registered d (positive: MM1-v1 closer). A case is the mean of its points (the kinds points share their cases with random points). The last column compares verify-e207d's own scoring (`work/my-scores.json` of that lane, code that imports nothing of the kit's) with the scorer's: its three cells, its two head-to-head cells and the largest difference of its five numbers from the scorer's. F1's cycles are its one cycles number.

| case | family | points | T1 wall | T2 counter mean | T3 seconds | T1 / T2 / T3 | d H1 | H1 closer | d H2 | H2 closer | verify-e207d |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemmL1x3x2 fp32 | inside | b01, b42, b49 | +2.46% | +4.46% | +2.55% | PASS / PASS / PASS | +0.0766 | MM1-v1 | +0.1567 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x3x2 int8 | inside | b02, b51 | +8.96% | +8.92% | +9.05% | PASS / PASS / PASS | -0.0303 | F1 | +0.0891 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x3x2 fp16 | inside | b03, b50 | +2.46% | +4.46% | +2.55% | PASS / PASS / PASS | +0.0753 | MM1-v1 | +0.1554 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x3x2 fp32 | inside | b04 | +1.43% | +3.42% | +1.52% | PASS / PASS / PASS | +0.0868 | MM1-v1 | +0.1667 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x3x2 int8 | inside | b05 | +7.87% | +7.83% | +7.97% | PASS / PASS / PASS | -0.0203 | F1 | +0.0991 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x2x2 fp32 | inside | b06 | +0.34% | +2.31% | +0.42% | PASS / PASS / PASS | +0.0976 | MM1-v1 | +0.1774 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x2x2 int8 | inside | b07 | +6.71% | +6.67% | +6.80% | PASS / PASS / PASS | -0.0095 | F1 | +0.1099 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x4x3 fp32 | inside | b08 | +0.27% | +3.17% | +0.35% | PASS / PASS / PASS | +0.1320 | MM1-v1 | +0.1936 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x4x3 int8 | inside | b09 | +6.83% | +7.40% | +6.91% | PASS / PASS / PASS | +0.0453 | MM1-v1 | +0.1533 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x9x3 fp32 | knee | b10 | +3.05% | +3.06% | +3.15% | PASS / PASS / PASS | +0.1559 | MM1-v1 | +0.1667 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x9x3 int8 | knee | b11 | +4.21% | +4.06% | +4.30% | PASS / PASS / PASS | +0.1395 | MM1-v1 | +0.1532 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x3x5 fp32 | knee | b12 | +4.68% | +5.82% | +4.77% | PASS / PASS / PASS | +0.1661 | MM1-v1 | +0.1554 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x3x5 int8 | knee | b13 | +6.18% | +7.32% | +6.27% | PASS / PASS / PASS | +0.1419 | MM1-v1 | +0.1315 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x3x5 fp16 | knee | b14 | +4.68% | +5.82% | +4.78% | PASS / PASS / PASS | +0.1651 | MM1-v1 | +0.1544 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x3x4 fp32 | knee | b15 | -0.31% | +0.78% | -0.21% | PASS / PASS / PASS | +0.1572 | MM1-v1 | +0.1527 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x3x4 int8 | knee | b16 | +1.52% | +2.62% | +1.61% | PASS / PASS / PASS | +0.1429 | MM1-v1 | +0.1322 | MM1-v1 | the same 5 of 5; 0 |
| gemmL5x2x3 fp32 | knee | b17 | -1.15% | -1.45% | -1.07% | PASS / PASS / PASS | +0.0464 | MM1-v1 | +0.0574 | MM1-v1 | the same 5 of 5; 0 |
| gemmL5x2x3 int8 | knee | b18 | +1.73% | +1.12% | +1.82% | PASS / PASS / PASS | +0.0334 | MM1-v1 | +0.0563 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x5x5 fp32 | past | b19, b43, b52 | +0.65% | +1.75% | +0.73% | PASS / PASS / PASS | +0.1588 | MM1-v1 | +0.1480 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x5x5 int8 | past | b20 | +1.15% | +2.25% | +1.24% | PASS / PASS / PASS | +0.1496 | MM1-v1 | +0.1389 | MM1-v1 | the same 5 of 5; 0 |
| gemmL5x3x6 fp32 | past | b21 | +1.06% | +2.16% | +1.13% | PASS / PASS / PASS | +0.1682 | MM1-v1 | +0.1574 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x6x10 fp32 | past | b22 | +2.77% | +3.89% | +2.87% | PASS / PASS / PASS | +0.1654 | MM1-v1 | +0.1546 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x3x24 fp32 | past | b23 | +1.94% | +2.82% | +2.00% | PASS / PASS / PASS | +0.1966 | MM1-v1 | +0.1902 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x3x24 int8 | past | b24 | +3.77% | +4.49% | +3.77% | PASS / PASS / PASS | +0.1279 | MM1-v1 | +0.1250 | MM1-v1 | the same 5 of 5; 0 |
| gemmL6x6x6 fp32 | past | b25 | -3.70% | -2.64% | -3.62% | PASS / PASS / PASS | +0.1278 | MM1-v1 | +0.1388 | MM1-v1 | the same 5 of 5; 0 |
| gemmL6x6x6 fp16 | past | b26 | -3.71% | -2.65% | -3.62% | PASS / PASS / PASS | +0.1269 | MM1-v1 | +0.1378 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x7x6 fp32 | stride | b27 | -5.10% | -5.24% | -5.02% | PASS / PASS / PASS | +0.1412 | MM1-v1 | +0.1522 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x8x6 fp32 | stride | b28 | +2.88% | +2.93% | +2.98% | PASS / PASS / PASS | +0.0185 | MM1-v1 | +0.0075 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x9x6 fp32 | stride | b29 | -5.66% | -5.78% | -5.58% | PASS / PASS / PASS | +0.1343 | MM1-v1 | +0.1452 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x4x12 fp32 | stride | b30 | -3.25% | -2.19% | -3.16% | PASS / PASS / PASS | +0.0959 | MM1-v1 | +0.1068 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x5x10 fp32 | stride | b31 | +3.30% | +4.42% | +3.39% | PASS / PASS / PASS | +0.1883 | MM1-v1 | +0.1776 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x8x6 int8 | stride | b32 | +2.57% | +2.70% | +2.69% | PASS / PASS / PASS | +0.0124 | MM1-v1 | +0.0015 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x7x6 int8 | stride | b33 | -3.81% | -4.02% | -3.74% | PASS / PASS / PASS | +0.1473 | MM1-v1 | +0.1582 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x6x4 fp32 0x3 | subset | b34 | +7.71% | -0.37% | +7.80% | PASS / PASS / PASS | -0.0506 | F1 | +0.0615 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x6x4 fp32 0xfff | subset | b35 | -8.66% | -6.46% | -8.58% | PASS / PASS / PASS | +0.2375 | MM1-v1 | +0.2614 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x6x4 fp32 0xffffff | subset | b36 | -1.29% | -4.39% | -1.21% | PASS / PASS / PASS | +0.2250 | MM1-v1 | +0.2359 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x6x4 fp32 0xf0f0f0f | subset | b37 | +3.46% | -5.96% | +3.53% | PASS / PASS / PASS | +0.1921 | MM1-v1 | +0.2711 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x6x4 int8 0x3 | subset | b38 | +12.86% | +3.59% | +12.95% | PASS / PASS / PASS | -0.0907 | F1 | +0.0310 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x6x4 int8 0xffffff | subset | b39 | +0.93% | -2.89% | +1.72% | PASS / PASS / PASS | +0.2080 | MM1-v1 | +0.2376 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x2x2 fp32 0x3 | subset | b40 | +16.34% | +24.14% | +16.42% | FAIL / FAIL / FAIL | -0.0546 | F1 | -0.0657 | F1 | the same 5 of 5; 0 |
| gemmL1x2x2 fp32 0xfff | subset | b41 | +11.33% | +17.49% | +11.42% | PASS / FAIL / PASS | -0.0083 | F1 | +0.0155 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x3x1 int8 | int8 one K block | n01 | +16.04% | +16.25% | +16.13% | FAIL / FAIL / FAIL | +0.0884 | MM1-v1 | -0.0303 | F1 | the same 5 of 5; 0 |
| gemmL3x5x1 int8 | int8 one K block | n02 | +11.19% | +3.06% | +11.30% | PASS / PASS / PASS | +0.0499 | MM1-v1 | +0.0390 | MM1-v1 | the same 5 of 5; 0 |
| gemmL3x5x1 fp32 | int8 one K block | n03 | +3.93% | -3.89% | +4.03% | PASS / PASS / PASS | -0.0238 | F1 | +0.0643 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x7x16 fp32 | long K | n04 | +5.63% | +6.50% | +5.71% | PASS / PASS / PASS | +0.1529 | MM1-v1 | +0.1474 | MM1-v1 | the same 5 of 5; 0 |
| gemmL1x8x16 fp32 | long K | n05 | -6.56% | -5.54% | -6.47% | PASS / PASS / PASS | +0.2044 | MM1-v1 | +0.2154 | MM1-v1 | the same 5 of 5; 0 |
| gemmL2x3x16 int8 | long K | n06 | +4.83% | +5.62% | +4.94% | PASS / PASS / PASS | +0.1258 | MM1-v1 | +0.1217 | MM1-v1 | the same 5 of 5; 0 |

Over the 47 cases verify-e207d's cells are the scorer's (141 of 141 rule cells, 94 of 94 head-to-head cells) and its numbers differ by at most 0.0e+00. Summary per rule: T1 misses gemmL1x2x2 fp32 0x3 and gemmL1x3x1 int8, T2 those two and gemmL1x2x2 fp32 0xfff, T3 the same two as T1; F1 is closer in H1 at 8 cases and in H2 at 2.

## 5. Every point: joules (E1-E4), the clock (S6) and the head-to-head H3 and H4, with verify-e207d beside

Errors are measured / MM1-v1 - 1; at b34, b38 and b40 E1 and E2 are W measured - W forecast (watts, the registered form). H3 and H4 set MM1-v1 against F2, which prices 49 of the 53 points (b49-b52 are not compared). The last column: verify-e207d's five cells (E1-E4, S6), its two head-to-head cells and the largest difference of its numbers from the scorer's.

| point | case | kind | W over idle | E1 | E2 | E3 | E4 | E1 / E2 / E3 / E4 / S6 | d H3 | H3 closer | d H4 | H4 closer | verify-e207d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b01 | gemmL1x3x2 fp32 | random | 24.898 W | +7.86% | +8.05% | +3.87% | +5.29% | PASS / PASS / PASS / PASS / PASS | +0.1441 | MM1-v1 | +0.1432 | MM1-v1 | the same 7 of 7; 0 |
| b02 | gemmL1x3x2 int8 | random | 10.395 W | +6.46% | +8.01% | +1.88% | +8.73% | PASS / PASS / PASS / PASS / PASS | +0.4008 | MM1-v1 | +0.3873 | MM1-v1 | the same 7 of 7; 0 |
| b03 | gemmL1x3x2 fp16 | random | 23.123 W | +7.04% | +7.25% | +3.36% | +4.82% | PASS / PASS / PASS / PASS / PASS | +0.1562 | MM1-v1 | +0.1552 | MM1-v1 | the same 7 of 7; 2e-16 |
| b04 | gemmL2x3x2 fp32 | random | 24.910 W | +7.82% | +7.93% | +3.87% | +4.72% | PASS / PASS / PASS / PASS / PASS | +0.1454 | MM1-v1 | +0.1448 | MM1-v1 | the same 7 of 7; 0 |
| b05 | gemmL2x3x2 int8 | random | 10.380 W | +6.11% | +7.49% | +1.79% | +7.82% | PASS / PASS / PASS / PASS / PASS | +0.4026 | MM1-v1 | +0.3908 | MM1-v1 | the same 7 of 7; 0 |
| b06 | gemmL3x2x2 fp32 | random | 24.880 W | +7.65% | +7.68% | +3.77% | +4.01% | PASS / PASS / PASS / PASS / PASS | +0.1453 | MM1-v1 | +0.1460 | MM1-v1 | the same 7 of 7; 0 |
| b07 | gemmL3x2x2 int8 | random | 10.347 W | +5.69% | +6.87% | +1.66% | +6.82% | PASS / PASS / PASS / PASS / PASS | +0.4035 | MM1-v1 | +0.3935 | MM1-v1 | the same 7 of 7; 0 |
| b08 | gemmL1x4x3 fp32 | random | 24.732 W | +6.24% | +6.27% | +3.09% | +3.29% | PASS / PASS / PASS / PASS / PASS | +0.1438 | MM1-v1 | +0.1445 | MM1-v1 | the same 7 of 7; 0 |
| b09 | gemmL1x4x3 int8 | random | 10.492 W | +4.82% | +5.99% | +1.43% | +6.63% | PASS / PASS / PASS / PASS / PASS | +0.3911 | MM1-v1 | +0.3809 | MM1-v1 | the same 7 of 7; 0 |
| b10 | gemmL1x9x3 fp32 | random | 20.400 W | +1.26% | +1.52% | +0.58% | +2.39% | PASS / PASS / PASS / PASS / PASS | +0.1966 | MM1-v1 | +0.1930 | MM1-v1 | the same 7 of 7; 0 |
| b11 | gemmL1x9x3 int8 | random | 9.795 W | +2.95% | +3.73% | +0.84% | +4.13% | PASS / PASS / PASS / PASS / PASS | +0.3462 | MM1-v1 | +0.3377 | MM1-v1 | the same 7 of 7; 0 |
| b12 | gemmL2x3x5 fp32 | random | 19.965 W | -0.72% | -0.33% | -0.33% | +2.38% | PASS / PASS / PASS / PASS / PASS | +0.2573 | MM1-v1 | +0.2602 | MM1-v1 | the same 7 of 7; 0 |
| b13 | gemmL2x3x5 int8 | random | 9.595 W | +2.90% | +4.03% | +0.82% | +5.61% | PASS / PASS / PASS / PASS / PASS | +0.4138 | MM1-v1 | +0.4019 | MM1-v1 | the same 7 of 7; 0 |
| b14 | gemmL2x3x5 fp16 | random | 18.770 W | -0.54% | -0.13% | -0.24% | +2.55% | PASS / PASS / PASS / PASS / PASS | +0.2711 | MM1-v1 | +0.2743 | MM1-v1 | the same 7 of 7; 0 |
| b15 | gemmL3x3x4 fp32 | random | 20.792 W | +0.33% | +0.31% | +0.15% | +0.04% | PASS / PASS / PASS / PASS / PASS | +0.1160 | MM1-v1 | +0.1152 | MM1-v1 | the same 7 of 7; 1e-16 |
| b16 | gemmL3x3x4 int8 | random | 9.705 W | +1.94% | +2.23% | +0.56% | +1.79% | PASS / PASS / PASS / PASS / PASS | +0.1893 | MM1-v1 | +0.1854 | MM1-v1 | the same 7 of 7; 0 |
| b17 | gemmL5x2x3 fp32 | random | 20.002 W | +1.99% | +1.89% | +0.90% | +0.26% | PASS / PASS / PASS / PASS / PASS | +0.0101 | MM1-v1 | +0.0101 | MM1-v1 | the same 7 of 7; 0 |
| b18 | gemmL5x2x3 int8 | random | 9.495 W | +5.34% | +5.70% | +1.47% | +2.90% | PASS / PASS / PASS / PASS / PASS | -0.0248 | F2 | -0.0292 | F2 | the same 7 of 7; 2e-16 |
| b19 | gemmL3x5x5 fp32 | random | 18.555 W | -3.50% | -3.44% | -1.57% | -1.15% | PASS / PASS / PASS / PASS / PASS | +0.2711 | MM1-v1 | +0.2708 | MM1-v1 | the same 7 of 7; 2e-16 |
| b20 | gemmL3x5x5 int8 | random | 9.175 W | -1.12% | -0.90% | -0.32% | +0.64% | PASS / PASS / PASS / PASS / PASS | +0.4839 | MM1-v1 | +0.4852 | MM1-v1 | the same 7 of 7; 2e-16 |
| b21 | gemmL5x3x6 fp32 | random | 18.703 W | -0.86% | -0.76% | -0.38% | +0.29% | PASS / PASS / PASS / PASS / PASS | +0.3180 | MM1-v1 | +0.3180 | MM1-v1 | the same 7 of 7; 3e-16 |
| b22 | gemmL2x6x10 fp32 | random | 17.435 W | -0.63% | -0.36% | -0.27% | +1.47% | PASS / PASS / PASS / PASS / PASS | +0.4630 | MM1-v1 | +0.4648 | MM1-v1 | the same 7 of 7; 2e-16 |
| b23 | gemmL1x3x24 fp32 | random | 15.670 W | -3.74% | -3.54% | -1.52% | -0.28% | PASS / PASS / PASS / PASS / PASS | +0.6240 | MM1-v1 | +0.6251 | MM1-v1 | the same 7 of 7; 0 |
| b24 | gemmL1x3x24 int8 | random | 8.900 W | +4.26% | +5.03% | +1.13% | +4.11% | PASS / PASS / PASS / PASS / PASS | +0.8740 | MM1-v1 | +0.8657 | MM1-v1 | the same 7 of 7; 0 |
| b25 | gemmL6x6x6 fp32 | random | 19.410 W | -0.66% | -0.98% | -0.30% | -2.45% | PASS / PASS / PASS / PASS / PASS | +0.2516 | MM1-v1 | +0.2473 | MM1-v1 | the same 7 of 7; 0 |
| b26 | gemmL6x6x6 fp16 | random | 18.038 W | -1.88% | -2.23% | -0.82% | -3.02% | PASS / PASS / PASS / PASS / PASS | +0.2646 | MM1-v1 | +0.2601 | MM1-v1 | the same 7 of 7; 0 |
| b27 | gemmL1x7x6 fp32 | random | 20.177 W | -1.85% | -2.28% | -0.86% | -3.78% | PASS / PASS / PASS / PASS / PASS | +0.2092 | MM1-v1 | +0.2038 | MM1-v1 | the same 7 of 7; 2e-16 |
| b28 | gemmL1x8x6 fp32 | random | 16.808 W | +0.25% | +0.54% | +0.10% | +1.96% | PASS / PASS / PASS / PASS / PASS | +0.1675 | MM1-v1 | +0.1636 | MM1-v1 | the same 7 of 7; 1e-16 |
| b29 | gemmL1x9x6 fp32 | random | 20.180 W | -1.88% | -2.37% | -0.87% | -4.13% | PASS / PASS / PASS / PASS / PASS | +0.2077 | MM1-v1 | +0.2018 | MM1-v1 | the same 7 of 7; 0 |
| b30 | gemmL1x4x12 fp32 | random | 16.387 W | -2.78% | -3.10% | -1.15% | -3.13% | PASS / PASS / PASS / PASS / PASS | +0.4395 | MM1-v1 | +0.4352 | MM1-v1 | the same 7 of 7; 0 |
| b31 | gemmL1x5x10 fp32 | random | 17.405 W | -2.79% | -2.48% | -1.20% | +0.82% | PASS / PASS / PASS / PASS / PASS | +0.4708 | MM1-v1 | +0.4731 | MM1-v1 | the same 7 of 7; 0 |
| b32 | gemmL1x8x6 int8 | random | 8.650 W | +2.60% | +3.15% | +0.69% | +2.81% | PASS / PASS / PASS / PASS / PASS | +0.2542 | MM1-v1 | +0.2488 | MM1-v1 | the same 7 of 7; 3e-16 |
| b33 | gemmL1x7x6 int8 | random | 9.593 W | -2.33% | -2.99% | -0.68% | -3.52% | PASS / PASS / PASS / PASS / PASS | +0.3781 | MM1-v1 | +0.3704 | MM1-v1 | the same 7 of 7; 0 |
| b34 | gemmL3x6x4 fp32 0x3 | random | 1.427 W | -0.135 W | -0.228 W | -0.54% | +6.83% | PASS / FAIL / PASS / PASS / PASS | +0.2175 | MM1-v1 | +0.0984 | MM1-v1 | the same 7 of 7; 2e-16 |
| b35 | gemmL3x6x4 fp32 0xfff | random | 8.490 W | -4.42% | -5.24% | -1.21% | -7.72% | PASS / PASS / PASS / PASS / PASS | +0.1980 | MM1-v1 | +0.1889 | MM1-v1 | the same 7 of 7; 3e-16 |
| b36 | gemmL3x6x4 fp32 0xffffff | random | 15.922 W | +2.65% | +2.54% | +1.05% | +0.27% | PASS / PASS / PASS / PASS / PASS | +0.2144 | MM1-v1 | +0.2150 | MM1-v1 | the same 7 of 7; 0 |
| b37 | gemmL3x6x4 fp32 0xf0f0f0f | random | 11.020 W | +6.74% | +7.10% | +2.06% | +4.64% | PASS / PASS / PASS / PASS / PASS | +0.1257 | MM1-v1 | +0.1223 | MM1-v1 | the same 7 of 7; 0 |
| b38 | gemmL3x6x4 int8 0x3 | random | 0.685 W | -0.175 W | -0.238 W | -0.71% | +11.85% | PASS / FAIL / PASS / PASS / PASS | +0.1432 | MM1-v1 | +0.0681 | MM1-v1 | the same 7 of 7; 6e-17 |
| b39 | gemmL3x6x4 int8 0xffffff | random | 7.795 W | +6.94% | +7.28% | +1.64% | +3.05% | PASS / PASS / PASS / PASS / PASS | +0.3406 | MM1-v1 | +0.3372 | MM1-v1 | the same 7 of 7; 0 |
| b40 | gemmL1x2x2 fp32 0x3 | random | 1.355 W | -0.321 W | -0.539 W | -1.27% | +13.96% | FAIL / FAIL / PASS / FAIL / PASS | -0.2096 | F2 | -0.3132 | F2 | the same 7 of 7; 0 |
| b41 | gemmL1x2x2 fp32 0xfff | random | 8.680 W | -1.32% | -0.40% | -0.36% | +7.97% | PASS / PASS / PASS / PASS / PASS | +0.1362 | MM1-v1 | +0.1458 | MM1-v1 | the same 7 of 7; 0 |
| b42 | gemmL1x3x2 fp32 | e37 | 14.400 W | +6.85% | +7.19% | +2.49% | +4.26% | PASS / PASS / PASS / PASS / PASS | +0.0103 | MM1-v1 | +0.0081 | MM1-v1 | the same 7 of 7; 0 |
| b43 | gemmL3x5x5 fp32 | e37 | 11.312 W | -1.84% | -1.73% | -0.60% | -0.07% | PASS / PASS / PASS / PASS / PASS | +0.4512 | MM1-v1 | +0.4517 | MM1-v1 | the same 7 of 7; 2e-16 |
| b49 | gemmL1x3x2 fp32 | real:blind4 | 18.588 W | +5.69% | +5.95% | +2.44% | +4.02% | PASS / PASS / PASS / PASS / PASS | - | not compared | - | not compared | the same 7 of 7; 0 |
| b50 | gemmL1x3x2 fp16 | real:blind4 | 21.608 W | +6.41% | +6.63% | +2.96% | +4.46% | PASS / PASS / PASS / PASS / PASS | - | not compared | - | not compared | the same 7 of 7; 0 |
| b51 | gemmL1x3x2 int8 | real:blind4 | 8.970 W | -4.06% | -2.60% | -1.15% | +5.58% | PASS / PASS / PASS / PASS / PASS | - | not compared | - | not compared | the same 7 of 7; 0 |
| b52 | gemmL3x5x5 fp32 | designed:blind3 a_colconst_b_randn | 17.062 W | -6.66% | -6.59% | -2.91% | -2.48% | PASS / PASS / PASS / PASS / PASS | - | not compared | - | not compared | the same 7 of 7; 0 |
| n01 | gemmL1x3x1 int8 | random | 9.847 W | +6.26% | +8.84% | +1.76% | +13.89% | PASS / PASS / PASS / FAIL / PASS | +0.4854 | MM1-v1 | +0.4625 | MM1-v1 | the same 7 of 7; 0 |
| n02 | gemmL3x5x1 int8 | random | 11.538 W | +24.87% | +27.09% | +6.97% | +16.01% | FAIL / FAIL / FAIL / FAIL / PASS | +0.1717 | MM1-v1 | +0.1551 | MM1-v1 | the same 7 of 7; 0 |
| n03 | gemmL3x5x1 fp32 | random | 26.867 W | +16.73% | +17.05% | +8.26% | +10.57% | FAIL / FAIL / FAIL / PASS / PASS | +0.0548 | MM1-v1 | +0.0526 | MM1-v1 | the same 7 of 7; 0 |
| n04 | gemmL1x7x16 fp32 | random | 15.515 W | -1.58% | -1.00% | -0.63% | +2.95% | PASS / PASS / PASS / PASS / PASS | +0.6478 | MM1-v1 | +0.6528 | MM1-v1 | the same 7 of 7; 0 |
| n05 | gemmL1x8x16 fp32 | random | 16.117 W | -4.49% | -5.16% | -1.88% | -5.94% | PASS / PASS / PASS / PASS / PASS | +0.6432 | MM1-v1 | +0.6362 | MM1-v1 | the same 7 of 7; 2e-16 |
| n06 | gemmL2x3x16 int8 | random | 8.610 W | +4.78% | +5.82% | +1.24% | +5.18% | PASS / PASS / PASS / PASS / PASS | +0.9082 | MM1-v1 | +0.8983 | MM1-v1 | the same 7 of 7; 0 |

Over the 53 points verify-e207d's cells are the scorer's (265 of 265 rule cells, 106 of 106 head-to-head cells) and its numbers differ by at most 3.3e-16. The misses: E1 at b40, n02 and n03; E2 at b34, b38, b40, n02 and n03; E3 at n02 and n03; E4 at b40, n01 and n02. F2 is closer in H3 and H4 at b18 and b40.

## 6. Beside the head-to-head verdicts (REPORTED, never verdicts)

**The family-level check** (E207.md A1 item 5, the after-score tool): the exact sign test over the families' median d, and a cluster bootstrap over families of the mean d. It decides only at 6 of 6, 7 of 7 or 8 of 8 untied families.

| rule | families: MM1-v1 / the other / tied | p | its reading | mean d, cluster bootstrap 95% | the families' median d | verify-e207d |
|---|---|---|---|---|---|---|
| H1 | 7 / 0 / 0 | 0.015625 | MM1-v1 BETTER | +0.1025 [+0.0723, +0.1326] over 7 | inside +0.075; int8 one K block +0.050; knee +0.143; long K +0.153; past +0.154; stride +0.134; subset +0.092 | the same (7 of 7, p 0.015625) |
| H2 | 7 / 0 / 0 | 0.015625 | MM1-v1 BETTER | +0.1278 [+0.1043, +0.1429] over 7 | inside +0.155; int8 one K block +0.039; knee +0.153; long K +0.147; past +0.143; stride +0.145; subset +0.149 | the same (7 of 7, p 0.015625) |
| H3 | 8 / 0 / 0 | 0.0078125 | MM1-v1 BETTER | +0.3081 [+0.2294, +0.4100] over 8 | inside +0.156; int8 one K block +0.172; kinds +0.231; knee +0.197; long K +0.648; past +0.391; stride +0.254; subset +0.198 | the same (8 of 8, p 0.0078125) |
| H4 | 8 / 0 / 0 | 0.0078125 | MM1-v1 BETTER | +0.3042 [+0.2252, +0.4108] over 8 | inside +0.155; int8 one K block +0.155; kinds +0.230; knee +0.193; long K +0.653; past +0.391; stride +0.249; subset +0.189 | the same (8 of 8, p 0.0078125) |

**The percentile bootstrap of d over cases or points** (the scorer; 10,000 resamples; the watts points left out):

| rule | n | median d [95%] | mean d [95%] |
|---|---|---|---|
| H1 | 47 | +0.1279 [+0.0868, +0.1473] | +0.1025 [+0.0783, +0.1252] |
| H2 | 47 | +0.1474 [+0.1315, +0.1544] | +0.1278 [+0.1068, +0.1480] |
| H3 | 46 | +0.2609 [+0.1992, +0.3781] | +0.3081 [+0.2519, +0.3682] |
| H4 | 46 | +0.2601 [+0.1946, +0.3593] | +0.3042 [+0.2484, +0.3641] |

**The other comparisons on J over idle** (the scorer, REPORTED; verify-e207d's the same):

| comparison | closer: the first / the second / ties | p | reading |
|---|---|---|---|
| MM1-v1 against F1, given the measured seconds (50 points F1 prices) | 48 / 2 / 0 | 2.267e-12 | MM1-v1 BETTER |
| MM1-v1 against F1, with the seconds forecast | 45 / 2 / 3 | 1.604e-11 | MM1-v1 BETTER |
| F1 against F2, given the measured seconds | 24 / 21 / 2 | 7.660e-01 | NOT DECIDED |
| F1 against F2, with the seconds forecast | 42 / 4 / 1 | 5.100e-09 | F1 BETTER |

**F1's and F2's own E206 rules on these points** (REPORTED, never E207 verdicts): F1.C1 FAIL 12/47; F1.S1 FAIL 21/47; F1.S2 FAIL 2/50; F1.S3 FAIL 7/50; F1.S4 PASS 50/50; F2.S2 FAIL 4/49; F2.S3 FAIL 7/49; F2.S4 FAIL 4/49.

## 7. How far each model was, by group (REPORTED: rms and mean of ln(measured / forecast))

Time per case; energy per point at 3 W and above (J over idle), every point for J at rest. F1 prices 50 points (47 at 3 W and above) and F2 49 (46).

| quantity | MM1-v1 | F1 | F2 |
|---|---|---|---|
| cycles an op, the wall | 0.0583 / +0.0269 (n 47) | 0.1646 / -0.1256 (n 47) | - |
| cycles an op, the counter's mean | 0.0624 / +0.0256 (n 47) | 0.1887 / -0.1659 (n 47) | - |
| seconds a GEMM | 0.0587 / +0.0279 (n 47) | 0.1638 / -0.1246 (n 47) | - |
| J over idle, given the measured seconds | 0.0571 / +0.0227 (n 50) | 0.2946 / +0.2830 (n 47) | 0.4032 / -0.1634 (n 46) |
| J over idle, with the seconds forecast | 0.0615 / +0.0261 (n 50) | 0.1878 / +0.1539 (n 47) | 0.4029 / -0.1626 (n 46) |
| J with the card at rest, given the measured seconds | 0.0218 / +0.0075 (n 53) | - | - |
| J with the card at rest, with the seconds forecast | 0.0554 / +0.0294 (n 53) | - | - |
| W over idle at b34, b38, b40 (watts) | given 0.225 W rms (-0.210); forecast 0.365 W rms (-0.335) | - | - |

By group, the wall cycles, the seconds and J over idle given the seconds (rms of ln; MM1-v1 against F1, and F2 where it prices):

| group | cases / points | wall: MM1-v1 / F1 | seconds: MM1-v1 / F1 | J over idle given: MM1-v1 / F1 / F2 |
|---|---|---|---|---|
| family=inside | 9 / 9 | 0.051 / 0.094 | 0.051 / 0.094 | 0.065 / 0.319 / 0.344 |
| family=int8 one K block | 3 / 3 | 0.108 / 0.164 | 0.109 / 0.165 | 0.160 / 0.276 / 0.407 |
| family=kinds | 0 / 6 | - / - | - / - | 0.055 / 0.246 / 0.337 |
| family=knee | 9 / 9 | 0.035 / 0.168 | 0.036 / 0.167 | 0.024 / 0.300 / 0.255 |
| family=long K | 3 / 3 | 0.057 / 0.221 | 0.057 / 0.221 | 0.039 / 0.287 / 0.780 |
| family=past | 8 / 8 | 0.026 / 0.177 | 0.026 / 0.176 | 0.025 / 0.276 / 0.511 |
| family=stride | 7 / 7 | 0.040 / 0.160 | 0.040 / 0.159 | 0.022 / 0.254 / 0.346 |
| family=subset | 8 / 8 | 0.090 / 0.188 | 0.090 / 0.187 | 0.048 / 0.357 / 0.262 |
| format=fp16 | 3 / 4 | 0.037 / 0.165 | 0.037 / 0.164 | 0.047 / 0.289 / 0.263 |
| format=fp32 | 27 / 31 | 0.052 / 0.175 | 0.053 / 0.174 | 0.050 / 0.265 / 0.344 |
| format=int8 | 17 / 18 | 0.069 / 0.148 | 0.070 / 0.147 | 0.069 / 0.335 / 0.504 |
| kind=designed:blind3 a_colconst_b_randn | 0 / 1 | - / - | - / - | 0.069 / - / - |
| kind=e37 | 0 / 2 | - / - | - / - | 0.049 / - / 0.337 |
| kind=random | 0 / 47 | - / - | - / - | 0.057 / 0.298 / 0.406 |
| kind=real:blind4 | 0 / 3 | - / - | - / - | 0.054 / 0.246 / - |
| mask=full | 39 / 45 | 0.050 / 0.159 | 0.050 / 0.159 | 0.058 / 0.286 / 0.417 |
| mask=subset | 8 / 8 | 0.090 / 0.188 | 0.090 / 0.187 | 0.048 / 0.357 / 0.262 |

## 8. The registered readings (REPORTED, the scorer's)

- **(a) The stride step**, measured wall ratio against MM1-v1's and F1's: fp32 1x8x6 over 1x7x6: 1.2719 (MM1-v1 1.1732, F1 1.0000); fp32 1x8x6 over 1x9x6: 1.2705 (MM1-v1 1.1650, F1 1.0000); int8 1x8x6 over 1x7x6: 1.2510 (MM1-v1 1.1732, F1 1.0000); fp32 1x8x16 over 1x7x16: 0.9374 (MM1-v1 1.0597, F1 1.0000); fp32 1x4x12 over 1x5x10: 1.0965 (MM1-v1 1.1707, F1 1.0003).
- **(b) int8 at one K block**: n01 wall 862.2 cycles an op (MM1-v1 743.0, F1 680.2); n02 884.2 (795.2, 756.5); n03 (fp32) 856.6 (824.1, 869.3); n02 over n03 1.0323 (MM1-v1 0.9649, F1 0.8703).
- **(c) The subsets** (mm-critic's open question: which of MM1-v1's full-chip lines with its contention term and F1's masked map is closer on the wall): b34 0x3: wall 1067 over the counter's mean 1.093, closer F1; b35 0xfff: wall 948 over the counter's mean 1.000, closer MM1-v1; b36 0xffffff: wall 1080 over the counter's mean 1.044, closer MM1-v1; b37 0xf0f0f0f: wall 1093 over the counter's mean 1.112, closer MM1-v1; b38 0x3: wall 1118 over the counter's mean 1.101, closer F1; b39 0xffffff: wall 1104 over the counter's mean 1.051, closer MM1-v1; b40 0x3: wall 909 over the counter's mean 1.055, closer F1; b41 0xfff: wall 907 over the counter's mean 1.081, closer F1.
- **(d) The kinds**, J over idle over the case's random point, measured against MM1-v1: b42 (e37 over b01) 0.578 against 0.583; b49 (real:blind4 over b01) 0.747 against 0.761; b50 (real:blind4 over b03) 0.935 against 0.940; b51 (real:blind4 over b02) 0.863 against 0.957; b43 (e37 over b19) 0.610 against 0.599; b52 (designed:blind3 a_colconst_b_randn over b19) 0.920 against 0.951; their wall cycles and seconds within 0.038% of the random points'.
- **(e) The timing simulation against the card**: over the 53 points, the measured cycles a GEMM are 18.0 to 33.2 times the simulator's instruction count (one step an instruction, not time), and the counter's mean is 1.48 to 5.71 times the tensor unit's measured floor.
- **(f) The tie** (t01 = E206's p001): runs 1, 55 and 109 at 3.8308, 3.8310 and 3.8310 ms a GEMM; drift last over first: seconds 1.00007, W over idle 1.0020. The bridge to E206's p001 (its five runs): seconds 0.99992, cycles 0.99994, W over idle 0.9896, the rest 0.9550.
- **(g) MM1-v1's rest law**: 24.741 W against the measured mean rest 23.667 W (-1.074 W).
- **(h) The day's replicate spread**: the pooled sd of a run's W over idle 0.1211 W over 53 points (median 0.0354 W), against the frozen SD_rep 0.1075 W.
- **(i)** MM1-v1's switch estimates sit beside every point in `scores-e207-A.json` (`switches_mm1_v1_REPORTED`); nothing on the card counts switches, and no rule reads them.
- **The checks of C read** (A1 item 7, the after-score tool): 0 of 109 runs printed no check of C.

## 9. The findings, answered as dated clauses (Tue 17 Nov 2026, PST)

1. **The scorer's outputs were not committed** (card-e207's open issue). Answered by this note: they are committed here, byte for byte, with their printed lines and `SHA256SUMS-note2`.
2. **The one-lab race at step 13** (card-e207, low: another lane copied its files into the lab clone right after THE QUIET HOLD came off, while the scorer ran). Answered by section 2: the clone's HEAD at the step was E211's registration (`1393a649`) and the 72 untracked files were E211's kit (`2b7f261f`), all under `tools/claims-v3/e211/`; none is a file the two programs opened or lies in a folder either imports from; the 43 files they opened are unchanged from the data commit to `7726e127`; and both programs re-run in a pristine tree of the data commit give the same bytes. No verdict depends on the race.
3. **Step 6n's tile-kind matching** (card-e207, low; verify-e207d note 5 confirms it). Note 1 dated the only records it found (E212's gemmL1x3x2 fp16 runs with `ones` tiles) after MM1-v1's freeze, so b50 and its case stay in every rule and the labels file names nothing. **Today's record** (a desk reading of the lab's committed E212 sessions at `7726e127`, run folder names only): 3 E212 sessions are committed; their records of an E207 case are 3 runs, all of gemmL1x3x2 fp16 with `ones` tiles (the case of b03 and b50, in another data kind): `2026-11-17-e212-mmsweep2-a1c1-S1` (run `004-1x3x2-fp16-ones`; its session started at 05:30:01 PST); `2026-11-17-e212-mmsweep2-a1c0-S1` (run `003-1x3x2-fp16-ones`; its session started at 06:16:04 PST); `2026-11-17-e212-mmsweep2-a1c1-S4` (run `004-1x3x2-fp16-ones`; its session started at 07:02:03 PST), Tue 17 Nov 2026, all after the freeze (21:14:57 PST Mon 16 Nov 2026). verify-e207d also found E207's point b08 (gemmL1x4x3 fp32, random) among E212's registered arms (posted 05:22:43 PST, after the freeze); no committed E212 session holds it yet. By A1 item 2, records dated after the freeze take nothing out of E207's rules: REPORTED only. Later kits may match a tile file's own kind.
4. **The public-text scan's false positives in step 6n's report files** (card-e207, note). They stand as committed (a desk-test folder's name and the lab's own path form, as card-e207 lists them). This note's own scan is in its lane's record.
5. **The card time: 47.16 card-minutes against the 40.6 planned** (verify-e207d, low: the cause not stated in the README). The cause is the die gate (desk arithmetic of the committed `session/runs/*/run.json`): 78 of 109 runs waited at the gate before their rest, 489.5 s in all (8.2 min), at most 18.0 s for a run. The gate was 51.0 C (the session's rest die, 47 C, plus 4) and the gate's own die readings at the runs' starts were 50-51 C. The plan allowed 22.0 s for each run (E206's slowest on this card, timed from the runner's start line, which it writes after the die gate, to its done line) and nothing for the gate. By the same lines in this directory's `session/session.log`, the 109 runs took 2,288 s (20-22 s each, 1.8 min under the plan), the smoke 40 s, and the time between runs 502 s, the gate waits nearly all of it: 40 + 2,288 + 502 = 2,830 s, the log's whole-second span of the session. Still inside the cap (70) and the rule of no run after 60. For the next days on aifoundry3 with this gate (E210, E211), about 8 more card-minutes is a fair allowance (verify-e207d's estimate).
6. **"Starts under" the gate** (verify-e207d, note: E207.md 6's wording). The kit compares die <= gate, as E206's kit did: 100 of 109 runs started at exactly 51 C, the gate, and 9 under it. Wording only; no verdict depends on it.
7. **The margins** (verify-e207d, note; REPORTED): E2 passes with no slack (48 of 53, 48 needed); T1 and T3 hold gemmL3x6x4 int8 0x3 at 12.86% and 12.95% of a 13% band, each with a slack of 2; the day's pooled replicate sd of W over idle, 0.121 W, is above the frozen 0.1075 W that set the 0.215 W band.
8. **The tie's seconds ratio** (verify-e207d, note: card-e207's result line set E206's three-tie means beside a ratio over all five of E206's p001 runs). The scorer's reading (f) takes the five runs: 0.99992; over E206's three tie runs alone the same ratio is 0.99996 (desk arithmetic of the committed `data-e206.json`). The README's own figures are right; nothing changes.
9. **The README's order and its per-point table** (verify-e207d, note: departures before results, as the round's go asks; the wall reading given as cycles a GEMM). Cosmetic; the README is not changed (new files only).
10. **verify-e207d's question: a dated note listing the records of E207's cases made after the freeze.** Clause 3 above lists those committed today; any later one (b08's case once E212 commits it) belongs in a later dated note. None can change a rule (A1 item 2).

**Not here, by the rules:** the model session's sealed E207 forecast (registered in `221a233f` before the first card command) is not scored by the lab, and nothing of it is quoted. MM1-v2's frozen E207 column (`4e518735`) was scored after the data by another lane, under `tools/matmul/mm1/v2/` (`030ffa42`); it is not one of E207's rules.

## 10. NOT RUN

- The scorer's self-tests and the kit's desk tests: they ran at step 3 (rc 0); this lane did not re-run them.
- verify-e207d's code: its outputs were read and compared, not re-run.
- The bootstrap intervals and the family check's cluster bootstrap were re-made by the re-runs (the same bytes), not by independent code.
- Any read of aifoundry1 or aifoundry3, and any card, device or simulator.

SPDX-License-Identifier: Apache-2.0
