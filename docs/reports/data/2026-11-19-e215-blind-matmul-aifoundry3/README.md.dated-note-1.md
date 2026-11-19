# E215 arm A data, dated note 1: the frozen scorer's output, committed beside the data byte for byte - registered (P, C, R): R0 and S6 PASS, T1 FAIL 27/32, T2 PASS 30/32, T3 FAIL 27/32, E1-E4 FAIL 28/32 each, H1-H3 NOT DECIDED, H4 and H5 TOO FEW; post hoc (L, S) apart; with verify-e215d's re-derivation beside each result

*Thu 19 Nov 2026 (week 47), PST; written at about 15:50 PST by Q224's lane `scores-e215`, after this directory's data commit `8355db15` (committed 13:00:32 PST, pushed by 13:00:37), after the day's data verifier `verify-e215d` (HOLDS WITH FIXES: both arms' data re-derive exactly from the raw records, its own scoring equals the frozen scorer's in every cell, verdict, count, p value and head-to-head, and its fixes are wording and records only) and after the fix lane `fix-e215d` (`2b0c8814`, 15:21:43 PST: arm B's data note 1 and E215's dated note 2, nothing in this directory). It adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. Labels: **registered** (E215.md with its dated departures D1 and D2, which change no rule or scorer), **measured** (this directory's committed records), **blind** (MM1-v3.1's and MM1-v3's arm A forecasts, frozen in `tools/matmul/mm1/v3.1/out/e215/` by MM1-v3.1's land `2c971828`, committed 23:09:13 PST Wed 18 Nov 2026; MM1-v2's and 'v3.1 with T7''s arm A forecasts frozen by E215's registration `4cb2c2ad`, committed 06:32:24 PST Thu 19 Nov; all before arm A's first card command, 12:05:55 PST), **REPORTED** (never a verdict), **post hoc** (families L and S, chosen after MM1-v3.1's fit and adopted by D1, and anything read after the data), **desk** (a check of code at the desk, under `/usr/bin/python3` 3.12.3).*

**The words.** The frozen scorer (`score_e215.py`, registered sha256 `cfa348d0...`), run by the kit's step 13 at 13:00:43 PST on this directory's committed `data-e215.json` with step 6n's committed `labels-e215.json` (no point and no case labelled 'ran before'), printed for arm A (aifoundry3 card 0 at its pinned 600 MHz):

- **Registered (P, C, R; E215's answer):** **R0 PASS**; **S6 PASS**; **T1 FAIL** 27/32; **T2 PASS** 30/32; **T3 FAIL** 27/32; **E1 FAIL** 28/32; **E2 FAIL** 28/32; **E3 FAIL** 28/32; **E4 FAIL** 28/32; head to head against MM1-v3 (the sign test, MM1-v3.1 / MM1-v3 / ties): **H1 NOT DECIDED** 8/12/12 (p 0.503); **H2 NOT DECIDED** 8/12/12 (p 0.503); **H3 NOT DECIDED** 8/12/12 (p 0.503); **H4 TOO FEW** 4/2/26; **H5 TOO FEW** 4/1/27.
- **Post hoc (L, S; reported apart, never the answer):** R0 PASS; S6 PASS; T1 FAIL 16/20; T2 FAIL 17/20; T3 FAIL 16/20; E1 PASS 27/28; E2 PASS 27/28; E3 PASS 28/28; E4 FAIL 24/28; H1 MM1-v3 BETTER 2/12/6 (p 0.0129); H2 MM1-v3 BETTER 1/13/6 (p 0.00183); H3 MM1-v3 BETTER 2/12/6 (p 0.0129); H4 TOO FEW 3/3/14; H5 TOO FEW 3/2/15.
- Arm B: NO DATA in this one-arm file; the pooled HP1-HP5: NO DATA in this file. They are made by the same frozen scorer on both arms' committed data in dated note 3 of arm B's directory (`README.md.dated-note-3.md`, `scores-e215-pooled.json`).
- With R0 and S6 PASS, no verdict of arm A carries a label: these are arm A's registered verdicts (the registered group's) and its post hoc readings (the post hoc group's). "The registered answer is the registered group's (P, C, R); the post hoc group's (L, S) is reported apart."

**MM1-v3.1 against MM1-v3, rms of the relative error** (measured / forecast - 1; desk arithmetic on this directory's measured values and the frozen forecasts, equal to verify-e215d's in every figure; REPORTED; blind). Registered: the wall cycles 7.20% against 6.87% (32 cases), the counter's mean 6.97% against 6.54%, seconds 7.18% against 6.85%; J over idle given the seconds 10.70% against 10.71% (32 points), with the seconds forecast 10.68% against 10.67%; J with the card at rest given the seconds 4.49% against 4.49%, with the seconds forecast 5.82% against 5.67%. Without the gemmLnc points (a post hoc reading), J over idle given the seconds 3.54% against 3.83% (28 points). Post hoc group: the wall cycles 9.16% against 8.24% (20 cases); J over idle given the seconds 6.96% (25 points at 3 W or more) against 6.58% (17: MM1-v3 prices no family-S kind). Section 6 has every model and quantity.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e215-A.json` | 147,359 | `58d777e023db50c0d743ed2f19d5b056d61fde5bf2870323d52e8f56386dae91` | the frozen scorer's output (`score_e215.py`, registered sha256 `cfa348d0...`): every verdict, count, cell, measured point, head-to-head count and REPORTED reading of arm A, both groups; arm B and the pooled rules NO DATA |
| `scores-e215-A.txt` | 2,617 | `5eab93b1b67decc37ec4e76668ecc5b440814c102e197b88ca57c7b3e28276db` | its printed lines (step 13's capture of the call) |
| `README.md.dated-note-1.md` | (this note) | listed in `SHA256SUMS-note1` | this dated note |
| `SHA256SUMS-note1` | 5 lines | (not listed in itself) | the three files above, `README.md` and `SHA256SUMS` |

The two output files are card-e215a's RB_OUT files byte for byte. With `SHA256SUMS` (648 entries) and `SHA256SUMS-note1` (5), every file of this directory is in a list except `SHA256SUMS-note1` itself; this is the directory's first note.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e215.sh A`) is the runbook log's last six lines (lines 105-110 of 110), at 13:00:42-13:00:43 PST, each rc 0, the six captures under one process id. Call 1 printed the data commit `8355db158` and its subject; call 2 (the directory clean) printed nothing; call 3 read all 648 `SHA256SUMS` entries OK, in the list's order; call 4 printed `HISTORY OK` naming the registration `4cb2c2ad6092`; call 5 printed `LABELS-OK`; call 6 ran `/usr/bin/python3 -I -B tools/claims-v3/e215/score_e215.py docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json --labels docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/labels-e215.json --out <the card lane's RB_OUT>/scores-e215-A.json` (0.7 s). The log holds no earlier run of the scorer on data: only its two self-tests and the print-only forecasts helper, in the runbook's desk step (`s03_desk_e215`, 12:04:21 PST, rc 0); no run of `score_e215.py --forecasts` at all (the kit runs its print-only helper `rb/forecasts_print_e215.py` there, so no registered file is rewritten).
- **The bytes.** `scores-e215-A.txt` is the runbook's capture of call 6 byte for byte (the step's copy of it), and it rebuilds exactly from the JSON through the scorer's own print function (`text()`, read from `score_e215.py` at the data commit). The JSON is in the scorer's own dump form (indent 1, sorted keys, no trailing newline) and was last written inside call 6 (its time stamp 13:00:43.109 PST, call 6's capture 13:00:43.110); the text file was copied after it (13:00:43.121).
- **The commit before it.** The data commit `8355db15` was made at 13:00:32 PST and pushed by 13:00:37; at 13:00:37 the card lane left its collect span, removed its hold line and released aifoundry3; step 13 ran at 13:00:42-43. The lab clone's HEAD during the step was the data commit itself (its reflog: `8355db15` from 13:00:32 until 13:14:37, when `aaeaa495` followed). None of the 13 committed files the scorer opens changed from the data commit to the lab's HEAD when this note was built; the data directory has had no change since its data commit.
- **The frozen files.** The registration list's 35 files and the list itself have one blob each at `4cb2c2ad` (the registration), `8bde0182` (the kit), `18398ed2` (the seal's registration), the data commit and HEAD; the kit list's 62 files and the list from `8bde0182` on; MM1-v3.1's land files (E215.md section 0, arm A's table: 18 files of MM1-v3.1, MM1-v3 and MM1-v2) from `2c971828` on, at their listed sha256; arm B's forecasts and the folder's frozen files (section 0's other tables: 25 files) at their listed sha256 from `4cb2c2ad` on; `tools/claims-v3/e215/` unchanged from the kit to HEAD. The scorer's ten pins equal those files' sha256 at the data commit.
- **The re-runs.** In a tree of exactly the 13 committed files the scorer opens (its own file, its ten pinned inputs, `data-e215.json` and `labels-e215.json`), taken from the data commit's objects, with no bytecode cache, a plain run and a run under an audit hook that lists every file opened, each with step 13's arguments, wrote both outputs byte for byte equal to RB_OUT and to the capture of call 6; the audited run opened those 13 files, 33 standard-library files and nothing else but its own outputs. The scorer imported unchanged and called in process (`score(data, labels, quiet=True)`) gives a result whose dump equals RB_OUT's JSON byte for byte; its own functions (`reduce_arm`, `score_group`, `decide`), called as `score()` calls them, give every case's and point's d value (the JSON keeps only the counts), with the JSON's counts, p values and cells. Sections 4 and 5 print those d values.
- **verify-e215d beside.** verify-e215d re-derived this directory's `data-e215.json` from the raw records (run records, process outputs and telemetry: 0 mismatches) and scored it with code that imports nothing of the kit's: its 396 cells, every pass flag, count, verdict and head-to-head (n, closer counts, ties, p), and its REPORTED 'v3.1 with T7' and MM1-v2 sign tests equal the scorer's. This lane compared its cells and d values with the scorer's own: the same cases and points, worst difference 0 (at a watts cell the scorer stores |W - W_fc| and verify-e215d the signed W - W_fc, the same number). Its rms tables equal this lane's in every figure.

## 3. The rules: their registered words, the verdicts, verify-e215d beside

The scorer's printed lines (`scores-e215-A.txt`, verbatim):

```
E215 scorer (score_e215.py), the verdicts - registered: families P, C, R; post hoc (reported apart): families L, S, 'points chosen post hoc after the fit; forecasts frozen before any E215 datum':
ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32; T2 PASS 30/32; T3 FAIL 27/32; E1 FAIL 28/32; E2 FAIL 28/32; E3 FAIL 28/32; E4 FAIL 28/32
  registered H1 NOT DECIDED (v3.1 8 / v3 12 / ties 12; p 0.5034446716308594); REPORTED bootstrap MM1-v3 BETTER [-0.008640053740991749, -0.00058826016134766]
  registered H2 NOT DECIDED (v3.1 8 / v3 12 / ties 12; p 0.5034446716308594); REPORTED bootstrap MM1-v3 BETTER [-0.008690110163055292, -0.0005589496943689047]
  registered H3 NOT DECIDED (v3.1 8 / v3 12 / ties 12; p 0.5034446716308594); REPORTED bootstrap MM1-v3 BETTER [-0.008567152436825596, -0.0005026924774683608]
  registered H4 TOO FEW (v3.1 4 / v3 2 / ties 26; p None); REPORTED bootstrap NOT DECIDED [-0.0005075831317993123, 0.004792431646882364]
  registered H5 TOO FEW (v3.1 4 / v3 1 / ties 27; p None); REPORTED bootstrap NOT DECIDED [-0.00042647083191634275, 0.004694712045407785]
ARM A POSTHOC (L, S): R0 PASS; S6 PASS; T1 FAIL 16/20; T2 FAIL 17/20; T3 FAIL 16/20; E1 PASS 27/28; E2 PASS 27/28; E3 PASS 28/28; E4 FAIL 24/28
  posthoc H1 MM1-v3 BETTER (v3.1 2 / v3 12 / ties 6; p 0.012939453125); REPORTED bootstrap MM1-v3 BETTER [-0.016423731330803337, -0.005522480025213977]
  posthoc H2 MM1-v3 BETTER (v3.1 1 / v3 13 / ties 6; p 0.0018310546875); REPORTED bootstrap MM1-v3 BETTER [-0.016866849777368027, -0.006812311614972348]
  posthoc H3 MM1-v3 BETTER (v3.1 2 / v3 12 / ties 6; p 0.012939453125); REPORTED bootstrap MM1-v3 BETTER [-0.016408154427190662, -0.005431607179750966]
  posthoc H4 TOO FEW (v3.1 3 / v3 3 / ties 14; p None); REPORTED bootstrap NOT DECIDED [-0.0019091227034931657, 0.004853019104704774]
  posthoc H5 TOO FEW (v3.1 3 / v3 2 / ties 15; p None); REPORTED bootstrap NOT DECIDED [-0.0025982758856660437, 0.004765442475364424]
ARM B REGISTERED (P, C, R): R0 NO DATA; S6 NO DATA; T1 NO DATA; T2 NO DATA; T3 NO DATA; E1 NO DATA; E2 NO DATA; E3 NO DATA; E4 NO DATA
  registered H1 NO DATA
  registered H2 NO DATA
  registered H3 NO DATA
  registered H4 NO DATA
  registered H5 NO DATA
ARM B POSTHOC (L, S): R0 NO DATA; S6 NO DATA; T1 NO DATA; T2 NO DATA; T3 NO DATA; E1 NO DATA; E2 NO DATA; E3 NO DATA; E4 NO DATA
  posthoc H1 NO DATA
  posthoc H2 NO DATA
  posthoc H3 NO DATA
  posthoc H4 NO DATA
  posthoc H5 NO DATA
POOLED REGISTERED: HP1 NO DATA; HP2 NO DATA; HP3 NO DATA; HP4 NO DATA; HP5 NO DATA
POOLED POSTHOC: HP1 NO DATA; HP2 NO DATA; HP3 NO DATA; HP4 NO DATA; HP5 NO DATA
```

**MM1-v3.1's rules, per arm and group** (E215.md 7, its words): "Each case or point passes when |measured / MM1-v3.1 - 1| is within its band; a rule's verdict: PASS if at least 90% of its scored cases or points pass, FAIL otherwise, TOO FEW under 10, NO DATA with none." "The band is twice the larger of two held-out errors of MM1-v3.1 for that quantity, rounded up to a whole percent:" B1, the leave-one-experiment-out error over every point without configuration twins, and B2, the same over this arm's card's points. "The points under about 3 W over idle are scored in absolute watts in E1 and E2" "(a point whose MM1-v3.1 frozen W over idle is under 3 W, or whose measured W over idle is; E3 and E4 stay relative)"; "arm A 0.60 W = 2 x max(0.2794, 0.2961, SD_rep 0.06083) = 0.592 -> 0.60 W". The section's title: "a point or case with no run is NO DATA, never a failure". The scorer's 90% rule passes a rule when the passing cases or points number at least ceil(0.9 n). R0: "every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its identity gate GATE OK; a family smoke's failure with no run of its family (dropped by its own stop path) is flagged and REPORTED, not an R0 failure; with a run of its family it counts." S6: "every kept run's counted samples at 590-610 MHz." "A FAIL of either labels every other verdict of its arm."

**The registered (families P, C, R) group:**

| rule | the registered words (E215.md 7) | band | scored | needed (90%) | the scorer | verify-e215d's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | "every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its identity gate GATE OK; a family smoke's failure with no run of its family (dropped by its own stop path) is flagged and REPORTED, not an R0 failure; with a run of its family it counts." | - | every check of C of the arm (smoke, points, references, ties) | all | **PASS** (0 failures) | PASS | - | none |
| **S6** | "every kept run's counted samples at 590-610 MHz." | 590-610 MHz | every kept run | all | **PASS** (0 failures) | PASS | - | none |
| **T1** | "cycles an op, the wall, per case"; "2 x max(4.723, 4.058) = 9.45 -> 10%" | 10% | 32 | 29 | **FAIL** (27/32) | FAIL (27/32; the same cells, worst difference 0) | -2 | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc) (-14.75%); `gemmLnc1x15x3` fp32 (rgm136 gemmLnc) (-15.46%); `gemmL2x1x7` fp32 (+12.81%); `gemmL2x1x7` int8 (+14.94%); `gemmL8x15x1` int8 (+11.03%) |
| **T2** | "cycles an op, the counter's mean, per case"; "2 x max(6.050, 4.581) = 12.10 -> 13%" | 13% | 32 | 29 | **PASS** (30/32) | PASS (30/32; the same cells, worst difference 0) | 1 | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc) (-15.94%); `gemmLnc1x15x3` fp32 (rgm136 gemmLnc) (-16.75%) |
| **T3** | "seconds a GEMM, per case (T1's bases)"; "2 x max(4.723, 4.058) = 9.45 -> 10%" | 10% | 32 | 29 | **FAIL** (27/32) | FAIL (27/32; the same cells, worst difference 0) | -2 | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc) (-14.68%); `gemmLnc1x15x3` fp32 (rgm136 gemmLnc) (-15.38%); `gemmL2x1x7` fp32 (+12.92%); `gemmL2x1x7` int8 (+15.04%); `gemmL8x15x1` int8 (+11.14%) |
| **E1** | "J over idle given the measured seconds, per point (watts under 3 W)"; "2 x max(5.476, 6.263) = 12.53 -> 13%" | 13% (watts 0.60 W) | 32 | 29 | **FAIL** (28/32) | FAIL (28/32; the same cells, worst difference 0) | -1 | a024 (+14.54%); a026 (+13.73%); a031 (+38.79%); a032 (+37.56%) |
| **E2** | "J over idle with the seconds forecast, per point (watts under 3 W)"; "2 x max(6.014, 6.357) = 12.71 -> 13%" | 13% (watts 0.60 W) | 32 | 29 | **FAIL** (28/32) | FAIL (28/32; the same cells, worst difference 0) | -1 | a024 (+13.80%); a026 (+13.02%); a031 (+38.84%); a032 (+37.56%) |
| **E3** | "J with the card at rest given the measured seconds and rest, per point"; "2 x max(2.153, 2.535) = 5.07 -> 6%" | 6% | 32 | 29 | **FAIL** (28/32) | FAIL (28/32; the same cells, worst difference 0) | -1 | a024 (+7.18%); a026 (+6.74%); a031 (+16.13%); a032 (+15.56%) |
| **E4** | "J with the card at rest with the seconds forecast, per point"; "2 x max(4.473, 4.131) = 8.95 -> 9%" | 9% | 32 | 29 | **FAIL** (28/32) | FAIL (28/32; the same cells, worst difference 0) | -1 | a031 (+15.55%); a032 (+14.86%); a043 (+9.62%); a044 (+12.91%) |

**The post hoc (families L, S; reported apart) group:**

| rule | the registered words (E215.md 7) | band | scored | needed (90%) | the scorer | verify-e215d's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | "every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its identity gate GATE OK; a family smoke's failure with no run of its family (dropped by its own stop path) is flagged and REPORTED, not an R0 failure; with a run of its family it counts." | - | every check of C of the arm (smoke, points, references, ties) | all | **PASS** (0 failures) | PASS | - | none |
| **S6** | "every kept run's counted samples at 590-610 MHz." | 590-610 MHz | every kept run | all | **PASS** (0 failures) | PASS | - | none |
| **T1** | "cycles an op, the wall, per case"; "2 x max(4.723, 4.058) = 9.45 -> 10%" | 10% | 20 | 18 | **FAIL** (16/20) | FAIL (16/20; the same cells, worst difference 0) | -2 | `gemmL1x6x5` fp32 at 0x33000333 (-11.96%); `gemmL1x9x6` fp32 at 0x2002202 (-10.11%); `gemmL2x3x5` fp32 at 0x99990000 (-11.81%); `gemmL2x4x4` fp32 at 0xee0e00 (-16.63%) |
| **T2** | "cycles an op, the counter's mean, per case"; "2 x max(6.050, 4.581) = 12.10 -> 13%" | 13% | 20 | 18 | **FAIL** (17/20) | FAIL (17/20; the same cells, worst difference 0) | -1 | `gemmL1x2x13` fp32 at 0x77007707 (-13.26%); `gemmL2x3x5` fp32 at 0x99990000 (-15.75%); `gemmL2x4x4` fp32 at 0xee0e00 (-19.51%) |
| **T3** | "seconds a GEMM, per case (T1's bases)"; "2 x max(4.723, 4.058) = 9.45 -> 10%" | 10% | 20 | 18 | **FAIL** (16/20) | FAIL (16/20; the same cells, worst difference 0) | -2 | `gemmL1x6x5` fp32 at 0x33000333 (-11.88%); `gemmL1x9x6` fp32 at 0x2002202 (-10.03%); `gemmL2x3x5` fp32 at 0x99990000 (-11.79%); `gemmL2x4x4` fp32 at 0xee0e00 (-16.56%) |
| **E1** | "J over idle given the measured seconds, per point (watts under 3 W)"; "2 x max(5.476, 6.263) = 12.53 -> 13%" | 13% (watts 0.60 W) | 28 | 26 | **PASS** (27/28) | PASS (27/28; the same cells, worst difference 0) | 1 | a057 (-19.12%) |
| **E2** | "J over idle with the seconds forecast, per point (watts under 3 W)"; "2 x max(6.014, 6.357) = 12.71 -> 13%" | 13% (watts 0.60 W) | 28 | 26 | **PASS** (27/28) | PASS (27/28; the same cells, worst difference 0) | 1 | a057 (-18.88%) |
| **E3** | "J with the card at rest given the measured seconds and rest, per point"; "2 x max(2.153, 2.535) = 5.07 -> 6%" | 6% | 28 | 26 | **PASS** (28/28) | PASS (28/28; the same cells, worst difference 0) | 2 | none |
| **E4** | "J with the card at rest with the seconds forecast, per point"; "2 x max(4.473, 4.131) = 8.95 -> 9%" | 9% | 28 | 26 | **FAIL** (24/28) | FAIL (24/28; the same cells, worst difference 0) | -2 | a011 (-11.82%); a013 (-11.55%); a015 (-10.84%); a020 (-15.38%) |

The slack is the passing count less the count the 90% rule needs (REPORTED, desk arithmetic): 0 passes at the rule's minimum, a negative slack is the shortfall; a rule under 10 scored reads TOO FEW, never PASS or FAIL. Errors are measured / MM1-v3.1 - 1; at a watts point E1 and E2 read |W - W_v3.1| in watts.

**THE HEAD-TO-HEAD RULES** (E215.md 7, its words): "per case (cycles, seconds) or per point (joules), d = |ln(measured / MM1-v3)| - |ln(measured / MM1-v3.1)| (at a watts point, |W - W_v3| - |W - W_v3.1| in watts); MM1-v3.1 is closer where d > the tie, MM1-v3 where d < -the tie, a tie otherwise." The ties: "arm A 0.005 in ln for cycles, 0.005 for seconds, 0.01 for joules, 0.05 W at a watts point". "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v3.1 BETTER if p < 0.05 and it is closer in more cases than not; MM1-v3 BETTER if p < 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none." HP1-HP5: "H1-H5 pooled over both arms per group, each case or point once with its own arm's tie; NO DATA unless both arms scored that group". Stated before the data: "the sign test's power is 2-8% wherever it can decide, and H4 and H5 are TOO FEW by construction". "So E215's head-to-head is registered, will be scored and printed, and is expected to read NOT DECIDED or TOO FEW whichever model is better: MM1-v3.1 and MM1-v3 differ by less than either's error."

**The registered (families P, C, R) group:**

| rule | the registered words (E215.md 7) | over | MM1-v3.1 closer | MM1-v3 closer | ties | p (exact, two-sided) | the scorer | verify-e215d | REPORTED: bootstrap 95% interval of the mean d (its reading) | REPORTED: the family check (family median d) | where MM1-v3 is closer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H1** | "cycles an op, the wall, per case" | 32 | 8 | 12 | 12 | 0.503 | **NOT DECIDED** | NOT DECIDED (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0086, -0.0006] (mean d -0.0046, n 32) | C -0.0089, P -0.0139, R +0.0101 | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc); `gemmLnc1x15x3` fp32 (rgm136 gemmLnc); `gemmL10x15x2` fp32; `gemmL11x15x2` fp32; `gemmL12x15x2` fp32; `gemmL2x15x2` fp32; `gemmL3x15x2` fp32; `gemmLn1x10x5` fp32 (rgm211 gemmLn); `gemmLn1x12x4` fp32 (rgm211 gemmLn); `gemmLn1x15x3` fp32 (rgm211 gemmLn); `gemmLn1x9x6` fp32 (rgm211 gemmLn); `gemmL1x5x7` fp32 (rgm211 gemmL) |
| **H2** | "cycles an op, the counter's mean, per case" | 32 | 8 | 12 | 12 | 0.503 | **NOT DECIDED** | NOT DECIDED (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0087, -0.0006] (mean d -0.0046, n 32) | C -0.0089, P -0.0139, R +0.0101 | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc); `gemmLnc1x15x3` fp32 (rgm136 gemmLnc); `gemmL10x15x2` fp32; `gemmL11x15x2` fp32; `gemmL12x15x2` fp32; `gemmL2x15x2` fp32; `gemmL3x15x2` fp32; `gemmLn1x10x5` fp32 (rgm211 gemmLn); `gemmLn1x12x4` fp32 (rgm211 gemmLn); `gemmLn1x15x3` fp32 (rgm211 gemmLn); `gemmLn1x9x6` fp32 (rgm211 gemmLn); `gemmL1x5x7` fp32 (rgm211 gemmL) |
| **H3** | "seconds a GEMM, per case" | 32 | 8 | 12 | 12 | 0.503 | **NOT DECIDED** | NOT DECIDED (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0086, -0.0005] (mean d -0.0046, n 32) | C -0.0089, P -0.0139, R +0.0101 | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc); `gemmLnc1x15x3` fp32 (rgm136 gemmLnc); `gemmL10x15x2` fp32; `gemmL11x15x2` fp32; `gemmL12x15x2` fp32; `gemmL2x15x2` fp32; `gemmL3x15x2` fp32; `gemmLn1x10x5` fp32 (rgm211 gemmLn); `gemmLn1x12x4` fp32 (rgm211 gemmLn); `gemmLn1x15x3` fp32 (rgm211 gemmLn); `gemmLn1x9x6` fp32 (rgm211 gemmLn); `gemmL1x5x7` fp32 (rgm211 gemmL) |
| **H4** | "J over idle given the measured seconds, per point both price" | 32 | 4 | 2 | 26 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0005, +0.0048] (mean d +0.0020, n 32) | C +0.0049, P -0.0001, R -0.0028 | a046; a051 |
| **H5** | "J over idle with the seconds forecast, per point both price" | 32 | 4 | 1 | 27 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0004, +0.0047] (mean d +0.0020, n 32) | C +0.0047, P -0.0001, R -0.0021 | a046 |

**The post hoc (families L, S; reported apart) group:**

| rule | the registered words (E215.md 7) | over | MM1-v3.1 closer | MM1-v3 closer | ties | p (exact, two-sided) | the scorer | verify-e215d | REPORTED: bootstrap 95% interval of the mean d (its reading) | REPORTED: the family check (family median d) | where MM1-v3 is closer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H1** | "cycles an op, the wall, per case" | 20 | 2 | 12 | 6 | 0.0129 | **MM1-v3 BETTER** | MM1-v3 BETTER (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0164, -0.0055] (mean d -0.0111, n 20) | L -0.0209 | `gemmL1x7x6` fp32 at 0x10100000; `gemmL1x9x6` fp32 at 0x2002202; `gemmL1x9x6` fp32 at 0xbbbbbbbb; `gemmL1x9x6` fp32 at 0xdddddddd; `gemmL1x9x6` fp32 at 0xf0ffffff; `gemmL1x9x6` fp32 at 0xff0fffff; `gemmL1x9x6` fp32 at 0xfff0ffff; `gemmL1x9x6` fp32 at 0xffff0fff; `gemmL1x9x6` fp32 at 0xfffff0ff; `gemmL1x9x6` fp32 at 0xffffff0f; `gemmL1x9x6` fp32 at 0xfffffff; `gemmL1x9x6` fp32 at 0xfffffff0 |
| **H2** | "cycles an op, the counter's mean, per case" | 20 | 1 | 13 | 6 | 0.00183 | **MM1-v3 BETTER** | MM1-v3 BETTER (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0169, -0.0068] (mean d -0.0121, n 20) | L -0.0209 | `gemmL1x7x6` fp32 at 0x10100000; `gemmL1x9x6` fp32 at 0x2002202; `gemmL1x9x6` fp32 at 0xbbbbbbbb; `gemmL1x9x6` fp32 at 0xdddddddd; `gemmL1x9x6` fp32 at 0xf0ffffff; `gemmL1x9x6` fp32 at 0xff0fffff; `gemmL1x9x6` fp32 at 0xfff0ffff; `gemmL1x9x6` fp32 at 0xffff0fff; `gemmL1x9x6` fp32 at 0xfffff0ff; `gemmL1x9x6` fp32 at 0xffffff0f; `gemmL1x9x6` fp32 at 0xfffffff; `gemmL1x9x6` fp32 at 0xfffffff0; `gemmL2x6x10` fp32 at 0x4404444 |
| **H3** | "seconds a GEMM, per case" | 20 | 2 | 12 | 6 | 0.0129 | **MM1-v3 BETTER** | MM1-v3 BETTER (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0164, -0.0054] (mean d -0.0111, n 20) | L -0.0209 | `gemmL1x7x6` fp32 at 0x10100000; `gemmL1x9x6` fp32 at 0x2002202; `gemmL1x9x6` fp32 at 0xbbbbbbbb; `gemmL1x9x6` fp32 at 0xdddddddd; `gemmL1x9x6` fp32 at 0xf0ffffff; `gemmL1x9x6` fp32 at 0xff0fffff; `gemmL1x9x6` fp32 at 0xfff0ffff; `gemmL1x9x6` fp32 at 0xffff0fff; `gemmL1x9x6` fp32 at 0xfffff0ff; `gemmL1x9x6` fp32 at 0xffffff0f; `gemmL1x9x6` fp32 at 0xfffffff; `gemmL1x9x6` fp32 at 0xfffffff0 |
| **H4** | "J over idle given the measured seconds, per point both price" | 20 | 3 | 3 | 14 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0019, +0.0049] (mean d +0.0012, n 17) | L -0.0014 | a014; a015; a019 |
| **H5** | "J over idle with the seconds forecast, per point both price" | 20 | 3 | 2 | 15 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0026, +0.0048] (mean d +0.0007, n 17) | L -0.0023 | a014; a019 |

## 4. Every case: cycles and seconds (T1-T3) and the head-to-head H1-H3, with verify-e215d beside

Errors are measured / MM1-v3.1 - 1 (the scorer's `err`; a miss in bold); d is the registered d (positive: MM1-v3.1 closer; the tie 0.005), from the frozen scorer's own functions (section 2); the closer is MM1-v3.1 (v3.1), MM1-v3 (v3) or a tie. MM1-v3's, 'v3.1 with T7''s and MM1-v2's wall errors are REPORTED beside (in parentheses after T7's: the closer of T7 and MM1-v3.1 by the same d and tie, REPORTED). Every case runs the full chip (mask 0xffffffff) on rgm136's gemmL loop unless the table names a mask or a loop. The last column compares verify-e215d's re-derivation (its own cells and d values) with the scorer's.

**The registered (families P, C, R) group** (32 cases):

| case | points | family | T1 wall | T2 counter | T3 seconds | H1 d (closer) | H2 d (closer) | H3 d (closer) | MM1-v3 wall (REPORTED) | v3.1 with T7 wall (REPORTED) | MM1-v2 wall (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemmLnc1x12x4` fp32 (rgm136 gemmLnc) | a026 | P | **-14.75%** | **-15.94%** | **-14.68%** | -0.0227 (v3) | -0.0227 (v3) | -0.0227 (v3) | -12.79% | -12.49% (T7) | -10.60% | equal |
| `gemmLnc1x15x3` fp32 (rgm136 gemmLnc) | a024 | P | **-15.46%** | **-16.75%** | **-15.38%** | -0.0229 (v3) | -0.0229 (v3) | -0.0229 (v3) | -13.50% | -13.10% (T7) | -11.06% | equal |
| `gemmLnc5x1x10` fp32 (rgm136 gemmLnc) | a032 | P | -1.10% | -1.43% | -1.04% | +0.0025 (tie) | +0.0025 (tie) | +0.0025 (tie) | -1.35% | -1.13% (tie) | -7.79% | equal |
| `gemmLnc8x1x5` fp32 (rgm136 gemmLnc) | a031 | P | -0.97% | -1.21% | -0.88% | +0.0024 (tie) | +0.0024 (tie) | +0.0024 (tie) | -1.21% | -0.78% (tie) | -7.74% | equal |
| `gemmL10x15x2` fp32 | a035 | C | -3.96% | -3.36% | -3.87% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.58% | -2.25% (T7) | -1.88% | equal |
| `gemmL11x11x1` int8 | a038 | C | +9.25% | +10.44% | +9.35% | +0.0003 (tie) | +0.0003 (tie) | +0.0003 (tie) | +9.28% | +8.62% (T7) | +20.72% | equal |
| `gemmL11x15x2` fp32 | a036 | C | -3.93% | -3.31% | -3.84% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.55% | -2.22% (T7) | -1.85% | equal |
| `gemmL12x15x2` fp32 | a037 | C | -3.95% | -3.35% | -3.85% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.58% | -2.24% (T7) | -1.88% | equal |
| `gemmL15x9x2` fp32 | a041 | C | +3.03% | +4.16% | +3.13% | -0.0035 (tie) | -0.0035 (tie) | -0.0035 (tie) | +2.67% | +3.80% (v3.1) | +4.89% | equal |
| `gemmL16x9x2` fp32 | a042 | C | +3.34% | +4.47% | +3.44% | -0.0035 (tie) | -0.0035 (tie) | -0.0035 (tie) | +2.99% | +4.12% (v3.1) | +5.20% | equal |
| `gemmL1x10x1` int8 | a030 | P | -1.73% | -1.56% | -1.64% | +0.0007 (tie) | +0.0007 (tie) | +0.0007 (tie) | -1.80% | -3.21% (v3.1) | +11.58% | equal |
| `gemmL1x15x1` int8 | a028 | P | +9.15% | +7.85% | +9.23% | -0.0036 (tie) | -0.0036 (tie) | -0.0036 (tie) | +8.75% | +11.08% (v3.1) | +20.27% | equal |
| `gemmL1x1x37` int8 | a051 | R | +4.97% | +6.13% | +4.83% | +0.0099 (v3.1) | +0.0099 (v3.1) | +0.0099 (v3.1) | +6.01% | +6.13% (v3.1) | +8.59% | equal |
| `gemmL1x1x39` fp32 | a047 | R | +5.76% | +6.93% | +5.66% | +0.0104 (v3.1) | +0.0104 (v3.1) | +0.0104 (v3.1) | +6.87% | +7.01% (v3.1) | +9.84% | equal |
| `gemmL1x1x41` fp32 | a045 | R | +5.14% | +6.29% | +5.08% | +0.0105 (v3.1) | +0.0105 (v3.1) | +0.0105 (v3.1) | +6.25% | +6.40% (v3.1) | +9.54% | equal |
| `gemmL1x1x41` int8 | a046 | R | +4.09% | +5.23% | +3.68% | +0.0105 (v3.1) | +0.0105 (v3.1) | +0.0105 (v3.1) | +5.19% | +5.34% (v3.1) | +8.45% | equal |
| `gemmL1x4x22` fp32 | a050 | R | +3.31% | +4.44% | +3.31% | +0.0001 (tie) | +0.0001 (tie) | +0.0001 (tie) | +3.32% | +4.60% (v3.1) | +4.33% | equal |
| `gemmL1x4x5` fp32 | a029 | P | -2.77% | -3.24% | -2.68% | +0.0056 (v3.1) | +0.0056 (v3.1) | +0.0056 (v3.1) | -3.31% | -5.36% (v3.1) | -2.47% | equal |
| `gemmL2x15x2` fp32 | a033 | C | -4.18% | -3.92% | -4.10% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.81% | -2.47% (T7) | -2.11% | equal |
| `gemmL2x1x7` fp32 | a043 | R | **+12.81%** | +5.98% | **+12.92%** | +0.0121 (v3.1) | +0.0121 (v3.1) | +0.0121 (v3.1) | +14.18% | +15.43% (v3.1) | +21.71% | equal |
| `gemmL2x1x7` int8 | a044 | R | **+14.94%** | +7.67% | **+15.04%** | +0.0110 (v3.1) | +0.0110 (v3.1) | +0.0110 (v3.1) | +16.22% | +17.66% (v3.1) | +25.43% | equal |
| `gemmL2x2x11` fp32 | a052 | R | +2.77% | +3.89% | +2.87% | +0.0018 (tie) | +0.0018 (tie) | +0.0018 (tie) | +2.95% | +3.44% (v3.1) | +3.46% | equal |
| `gemmL2x2x11` int8 | a049 | R | +3.43% | +4.56% | +3.53% | +0.0016 (tie) | +0.0016 (tie) | +0.0016 (tie) | +3.60% | +4.12% (v3.1) | +4.40% | equal |
| `gemmL2x3x12` int8 | a048 | R | +2.17% | +3.29% | +2.25% | +0.0057 (v3.1) | +0.0057 (v3.1) | +0.0057 (v3.1) | +2.76% | +3.41% (v3.1) | +5.32% | equal |
| `gemmL3x15x2` fp32 | a034 | C | -3.88% | -3.26% | -3.79% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.50% | -2.17% (T7) | -1.81% | equal |
| `gemmL4x13x1` fp32 | a040 | C | +8.44% | +8.72% | +8.26% | -0.0035 (tie) | -0.0035 (tie) | -0.0035 (tie) | +8.06% | +10.24% (v3.1) | +15.99% | equal |
| `gemmL8x15x1` int8 | a039 | C | **+11.03%** | +10.05% | **+11.14%** | -0.0027 (tie) | -0.0027 (tie) | -0.0027 (tie) | +10.74% | +12.73% (v3.1) | +19.73% | equal |
| `gemmLn1x10x5` fp32 (rgm211 gemmLn) | a023 | P | -6.83% | -7.46% | -6.75% | -0.0232 (v3) | -0.0232 (v3) | -0.0232 (v3) | -4.65% | -4.42% (T7) | -4.81% | equal |
| `gemmLn1x12x4` fp32 (rgm211 gemmLn) | a022 | P | -6.40% | -7.06% | -6.32% | -0.0233 (v3) | -0.0233 (v3) | -0.0233 (v3) | -4.19% | -3.85% (T7) | -4.16% | equal |
| `gemmLn1x15x3` fp32 (rgm211 gemmLn) | a021 | P | -6.54% | -7.10% | -6.45% | -0.0234 (v3) | -0.0234 (v3) | -0.0234 (v3) | -4.32% | -3.87% (T7) | -4.00% | equal |
| `gemmLn1x9x6` fp32 (rgm211 gemmLn) | a025 | P | -8.10% | -8.74% | -8.04% | -0.0228 (v3) | -0.0228 (v3) | -0.0228 (v3) | -5.98% | -5.82% (T7) | -5.71% | equal |
| `gemmL1x5x7` fp32 (rgm211 gemmL) | a027 | P | -2.74% | -3.55% | -2.66% | -0.0051 (v3) | -0.0051 (v3) | -0.0051 (v3) | -2.24% | -3.20% (tie) | -4.88% | equal |

**The post hoc (families L, S; reported apart) group** (20 cases; family S is scored in energy only, so its points hold no case here):

| case | points | family | T1 wall | T2 counter | T3 seconds | H1 d (closer) | H2 d (closer) | H3 d (closer) | MM1-v3 wall (REPORTED) | v3.1 with T7 wall (REPORTED) | MM1-v2 wall (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemmL1x2x13` fp32 at 0x77007707 | a012 | L | -1.02% | **-13.26%** | -0.93% | -0.0023 (tie) | -0.0023 (tie) | -0.0023 (tie) | -0.80% | +17.15% (v3.1) | +6.80% | equal |
| `gemmL1x6x5` fp32 at 0x33000333 | a011 | L | **-11.96%** | -11.42% | **-11.88%** | +0.0023 (tie) | +0.0023 (tie) | +0.0023 (tie) | -12.16% | -6.18% (T7) | -9.53% | equal |
| `gemmL1x7x6` fp32 at 0x10100000 | a019 | L | -3.40% | -2.34% | -3.32% | -0.0136 (v3) | -0.0136 (v3) | -0.0136 (v3) | -2.08% | +3.90% (tie) | +4.14% | equal |
| `gemmL1x8x6` fp32 at 0xd000dd0 | a017 | L | +7.14% | +7.42% | +7.23% | +0.0149 (v3.1) | +0.0149 (v3.1) | +0.0149 (v3.1) | +8.74% | +2.71% (T7) | +11.35% | equal |
| `gemmL1x9x6` fp32 at 0x2002202 | a015 | L | **-10.11%** | -9.12% | **-10.03%** | -0.0204 (v3) | -0.0204 (v3) | -0.0204 (v3) | -8.26% | +1.89% (T7) | +0.54% | equal |
| `gemmL1x9x6` fp32 at 0xbbbbbbbb | a009 | L | -9.80% | -9.65% | -9.72% | -0.0214 (v3) | -0.0214 (v3) | -0.0214 (v3) | -7.85% | -10.16% (tie) | -2.31% | equal |
| `gemmL1x9x6` fp32 at 0xdddddddd | a010 | L | -9.52% | -9.63% | -9.45% | -0.0214 (v3) | -0.0214 (v3) | -0.0214 (v3) | -7.56% | -9.88% (tie) | -2.01% | equal |
| `gemmL1x9x6` fp32 at 0xf0ffffff | a001 | L | -9.41% | -9.71% | -9.32% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.43% | -8.08% (T7) | -2.48% | equal |
| `gemmL1x9x6` fp32 at 0xff0fffff | a002 | L | -9.41% | -9.66% | -9.34% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.43% | -8.09% (T7) | -2.48% | equal |
| `gemmL1x9x6` fp32 at 0xfff0ffff | a003 | L | -9.77% | -9.91% | -9.69% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.80% | -8.45% (T7) | -2.87% | equal |
| `gemmL1x9x6` fp32 at 0xffff0fff | a004 | L | -9.33% | -9.47% | -9.25% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.35% | -8.00% (T7) | -2.39% | equal |
| `gemmL1x9x6` fp32 at 0xfffff0ff | a005 | L | -9.19% | -9.43% | -9.14% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.21% | -7.87% (T7) | -2.25% | equal |
| `gemmL1x9x6` fp32 at 0xffffff0f | a006 | L | -9.27% | -9.74% | -9.18% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.29% | -7.94% (T7) | -2.33% | equal |
| `gemmL1x9x6` fp32 at 0xfffffff | a007 | L | -9.51% | -9.76% | -9.42% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.53% | -8.18% (T7) | -2.58% | equal |
| `gemmL1x9x6` fp32 at 0xfffffff0 | a008 | L | -9.21% | -9.45% | -9.12% | -0.0216 (v3) | -0.0216 (v3) | -0.0216 (v3) | -7.23% | -7.88% (T7) | -2.27% | equal |
| `gemmL2x3x5` fp32 at 0x99990000 | a013 | L | **-11.81%** | **-15.75%** | **-11.79%** | +0.0006 (tie) | +0.0006 (tie) | +0.0006 (tie) | -11.87% | -4.72% (T7) | -7.76% | equal |
| `gemmL2x4x16` fp32 at 0x990009 | a018 | L | -4.42% | -3.37% | -4.33% | -0.0025 (tie) | -0.0025 (tie) | -0.0025 (tie) | -4.18% | -6.57% (v3.1) | +5.23% | equal |
| `gemmL2x4x4` fp32 at 0xee0e00 | a020 | L | **-16.63%** | **-19.51%** | **-16.56%** | +0.0042 (tie) | +0.0042 (tie) | +0.0042 (tie) | -16.98% | -17.32% (v3.1) | -12.63% | equal |
| `gemmL2x6x10` fp32 at 0x4404444 | a016 | L | +5.52% | -1.28% | +5.56% | +0.0101 (v3.1) | -0.0101 (v3) | +0.0101 (v3.1) | +6.59% | +8.60% (v3.1) | +20.52% | equal |
| `gemmL8x1x4` fp32 at 0x30000000 | a014 | L | +3.62% | +4.76% | +3.71% | +0.0004 (tie) | +0.0004 (tie) | +0.0004 (tie) | +3.66% | +39.89% (v3.1) | +9.96% | equal |

## 5. Every point: joules (E1-E4) and the head-to-head H4 and H5, with verify-e215d beside

E1 and E3 use the measured seconds (MM1-v3.1's frozen affine W at the measured op time); E2 and E4 the seconds forecast. At a watts point E1 and E2 read |W - W_v3.1| in watts against the watts band, and H4 and H5 the registered watts d (positive: MM1-v3.1 closer; the watts tie). The W column is the measured W over idle. MM1-v3's, 'v3.1 with T7''s and MM1-v2's E1 errors are REPORTED beside ('-' where the model prices no energy for the point's kind: MM1-v3 and MM1-v2 price no family-S kind).

**The registered (families P, C, R) group** (32 points):

| point | family | case | W over idle | E1 | E2 | E3 | E4 | H4 d (closer) | H5 d (closer) | MM1-v3 E1 (REPORTED) | v3.1 with T7 E1 (REPORTED) | MM1-v2 E1 (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a021 | P | `gemmLn1x15x3` fp32 (rgm211 gemmLn) | 20.83 W | -2.10% | -2.31% | -1.00% | -4.55% | +0.0007 (tie) | -0.0002 (tie) | -2.17% | -1.76% | -1.18% | equal |
| a022 | P | `gemmLn1x12x4` fp32 (rgm211 gemmLn) | 20.64 W | -2.35% | -2.56% | -1.11% | -4.60% | -0.0001 (tie) | -0.0010 (tie) | -2.34% | -2.03% | -2.14% | equal |
| a023 | P | `gemmLn1x10x5` fp32 (rgm211 gemmLn) | 20.65 W | -2.34% | -2.57% | -1.12% | -4.83% | -0.0006 (tie) | -0.0015 (tie) | -2.29% | -2.04% | -2.55% | equal |
| a024 | P | `gemmLnc1x15x3` fp32 (rgm136 gemmLnc) | 26.30 W | **+14.54%** | **+13.80%** | **+7.18%** | -2.14% | -0.0003 (tie) | +0.0003 (tie) | +14.50% | +14.93% | +16.20% | equal |
| a025 | P | `gemmLn1x9x6` fp32 (rgm211 gemmLn) | 20.67 W | -2.54% | -2.85% | -1.21% | -5.68% | -0.0009 (tie) | -0.0018 (tie) | -2.45% | -2.25% | -2.93% | equal |
| a026 | P | `gemmLnc1x12x4` fp32 (rgm136 gemmLnc) | 25.77 W | **+13.73%** | **+13.02%** | **+6.74%** | -2.13% | +0.0004 (tie) | +0.0011 (tie) | +13.78% | +14.10% | +14.53% | equal |
| a027 | P | `gemmL1x5x7` fp32 (rgm211 gemmL) | 20.35 W | -1.63% | -1.67% | -0.76% | -2.20% | +0.0017 (tie) | +0.0015 (tie) | -1.79% | -1.76% | -3.11% | equal |
| a028 | P | `gemmL1x15x1` int8 | 9.21 W | -3.91% | -3.13% | -1.13% | +5.44% | +0.0215 (v3.1) | +0.0212 (v3.1) | -5.95% | -3.31% | +12.84% | equal |
| a029 | P | `gemmL1x4x5` fp32 | 20.44 W | -2.61% | -2.64% | -1.23% | -2.66% | +0.0026 (tie) | +0.0029 (tie) | -2.86% | -3.07% | -2.65% | equal |
| a030 | P | `gemmL1x10x1` int8 | 9.72 W | -11.72% | -11.75% | -3.74% | -4.83% | -0.0002 (tie) | -0.0000 (tie) | -11.69% | -12.71% | +1.38% | equal |
| a031 | P | `gemmLnc8x1x5` fp32 (rgm136 gemmLnc) | 23.23 W | **+38.79%** | **+38.84%** | **+16.13%** | **+15.55%** | -0.0030 (tie) | -0.0032 (tie) | +38.37% | +38.30% | +38.49% | equal |
| a032 | P | `gemmLnc5x1x10` fp32 (rgm136 gemmLnc) | 22.86 W | **+37.56%** | **+37.56%** | **+15.56%** | **+14.86%** | -0.0022 (tie) | -0.0024 (tie) | +37.25% | +36.87% | +36.09% | equal |
| a033 | C | `gemmL2x15x2` fp32 | 20.03 W | -2.43% | -2.53% | -1.13% | -3.38% | +0.0035 (tie) | +0.0029 (tie) | -2.77% | -2.21% | -0.36% | equal |
| a034 | C | `gemmL3x15x2` fp32 | 19.90 W | -2.79% | -2.87% | -1.30% | -3.37% | +0.0035 (tie) | +0.0029 (tie) | -3.12% | -2.57% | -0.74% | equal |
| a035 | C | `gemmL10x15x2` fp32 | 20.01 W | -2.32% | -2.41% | -1.08% | -3.20% | +0.0035 (tie) | +0.0029 (tie) | -2.66% | -2.11% | -0.27% | equal |
| a036 | C | `gemmL11x15x2` fp32 | 20.03 W | -2.18% | -2.28% | -1.02% | -3.13% | +0.0035 (tie) | +0.0029 (tie) | -2.52% | -1.97% | -0.12% | equal |
| a037 | C | `gemmL12x15x2` fp32 | 19.92 W | -2.75% | -2.82% | -1.28% | -3.38% | +0.0035 (tie) | +0.0029 (tie) | -3.09% | -2.53% | -0.70% | equal |
| a038 | C | `gemmL11x11x1` int8 | 9.60 W | -4.10% | -3.33% | -1.23% | +5.34% | +0.0211 (v3.1) | +0.0205 (v3.1) | -6.10% | -4.42% | +15.07% | equal |
| a039 | C | `gemmL8x15x1` int8 | 9.07 W | -2.28% | -1.32% | -0.65% | +7.36% | +0.0215 (v3.1) | +0.0210 (v3.1) | -4.36% | -1.88% | +13.68% | equal |
| a040 | C | `gemmL4x13x1` fp32 | 19.56 W | -1.45% | -1.28% | -0.66% | +3.70% | +0.0111 (v3.1) | +0.0110 (v3.1) | -2.53% | -1.17% | +6.29% | equal |
| a041 | C | `gemmL15x9x2` fp32 | 19.62 W | -1.94% | -1.72% | -0.89% | +0.86% | +0.0063 (tie) | +0.0064 (tie) | -2.56% | -1.90% | +0.46% | equal |
| a042 | C | `gemmL16x9x2` fp32 | 19.48 W | -2.37% | -2.13% | -1.09% | +0.83% | +0.0064 (tie) | +0.0064 (tie) | -2.99% | -2.33% | +0.01% | equal |
| a043 | R | `gemmL2x1x7` fp32 | 16.93 W | +4.58% | +5.36% | +1.87% | **+9.62%** | -0.0012 (tie) | -0.0001 (tie) | +4.45% | +4.51% | +4.64% | equal |
| a044 | R | `gemmL2x1x7` int8 | 8.25 W | +5.51% | +7.26% | +1.38% | **+12.91%** | -0.0018 (tie) | +0.0005 (tie) | +5.32% | +5.37% | +7.15% | equal |
| a045 | R | `gemmL1x1x41` fp32 | 14.54 W | -3.79% | -3.55% | -1.49% | +1.60% | -0.0056 (tie) | -0.0065 (tie) | -3.25% | -2.87% | -5.87% | equal |
| a046 | R | `gemmL1x1x41` int8 | 8.01 W | -2.21% | -2.15% | -0.57% | +2.13% | -0.0113 (v3) | -0.0129 (v3) | -1.10% | -0.45% | -4.71% | equal |
| a047 | R | `gemmL1x1x39` fp32 | 14.56 W | -3.16% | -2.94% | -1.24% | +2.19% | -0.0056 (tie) | -0.0065 (tie) | -2.62% | -2.27% | -5.47% | equal |
| a048 | R | `gemmL2x3x12` int8 | 8.13 W | -1.27% | -0.96% | -0.33% | +1.40% | -0.0034 (tie) | -0.0042 (tie) | -0.94% | -0.73% | -2.01% | equal |
| a049 | R | `gemmL2x2x11` int8 | 8.35 W | +1.93% | +2.41% | +0.50% | +3.23% | -0.0021 (tie) | -0.0017 (tie) | +1.72% | +1.81% | -0.25% | equal |
| a050 | R | `gemmL1x4x22` fp32 | 14.56 W | -3.43% | -3.24% | -1.34% | +0.70% | +0.0007 (tie) | +0.0006 (tie) | -3.50% | -3.36% | -5.33% | equal |
| a051 | R | `gemmL1x1x37` int8 | 8.02 W | -1.14% | -0.73% | -0.30% | +3.34% | -0.0105 (v3) | -0.0025 (tie) | -0.09% | +0.44% | -4.54% | equal |
| a052 | R | `gemmL2x2x11` fp32 | 15.84 W | -1.75% | -1.50% | -0.71% | +1.06% | +0.0014 (tie) | +0.0012 (tie) | -1.89% | -1.81% | -3.56% | equal |

**The post hoc (families L, S; reported apart) group** (28 points):

| point | family | case | W over idle | E1 | E2 | E3 | E4 | H4 d (closer) | H5 d (closer) | MM1-v3 E1 (REPORTED) | v3.1 with T7 E1 (REPORTED) | MM1-v2 E1 (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a001 | L | `gemmL1x9x6` fp32 at 0xf0ffffff | 17.79 W | -2.90% | -3.28% | -1.28% | -6.80% | -0.0014 (tie) | -0.0023 (tie) | -2.77% | -2.50% | -2.87% | equal |
| a002 | L | `gemmL1x9x6` fp32 at 0xff0fffff | 17.59 W | -3.97% | -4.35% | -1.75% | -7.26% | -0.0014 (tie) | -0.0023 (tie) | -3.84% | -3.57% | -3.93% | equal |
| a003 | L | `gemmL1x9x6` fp32 at 0xfff0ffff | 17.71 W | -3.68% | -4.08% | -1.62% | -7.35% | -0.0014 (tie) | -0.0023 (tie) | -3.55% | -3.28% | -3.63% | equal |
| a004 | L | `gemmL1x9x6` fp32 at 0xffff0fff | 17.62 W | -3.72% | -4.10% | -1.64% | -7.11% | -0.0014 (tie) | -0.0023 (tie) | -3.59% | -3.32% | -3.69% | equal |
| a005 | L | `gemmL1x9x6` fp32 at 0xfffff0ff | 17.67 W | -3.31% | -3.71% | -1.46% | -6.87% | -0.0014 (tie) | -0.0023 (tie) | -3.18% | -2.91% | -3.28% | equal |
| a006 | L | `gemmL1x9x6` fp32 at 0xffffff0f | 17.74 W | -3.01% | -3.37% | -1.32% | -6.76% | -0.0014 (tie) | -0.0023 (tie) | -2.88% | -2.60% | -2.97% | equal |
| a007 | L | `gemmL1x9x6` fp32 at 0xfffffff | 17.67 W | -3.63% | -4.01% | -1.60% | -7.16% | -0.0014 (tie) | -0.0023 (tie) | -3.50% | -3.23% | -3.59% | equal |
| a008 | L | `gemmL1x9x6` fp32 at 0xfffffff0 | 17.60 W | -3.71% | -4.08% | -1.64% | -7.01% | -0.0014 (tie) | -0.0023 (tie) | -3.58% | -3.31% | -3.68% | equal |
| a009 | L | `gemmL1x9x6` fp32 at 0xbbbbbbbb | 14.99 W | -5.89% | -6.31% | -2.39% | -8.41% | -0.0021 (tie) | -0.0031 (tie) | -5.69% | -5.11% | -5.70% | equal |
| a010 | L | `gemmL1x9x6` fp32 at 0xdddddddd | 15.05 W | -5.24% | -5.65% | -2.14% | -7.98% | -0.0021 (tie) | -0.0031 (tie) | -5.04% | -4.45% | -5.05% | equal |
| a011 | L | `gemmL1x6x5` fp32 at 0x33000333 | 6.86 W | -10.89% | -11.61% | -2.70% | **-11.82%** | -0.0042 (tie) | -0.0046 (tie) | -10.52% | -9.11% | -10.02% | equal |
| a012 | L | `gemmL1x2x13` fp32 at 0x77007707 | 8.83 W | +8.52% | +8.54% | +2.20% | +1.50% | +0.0041 (tie) | +0.0043 (tie) | +8.97% | +13.49% | +7.75% | equal |
| a013 | L | `gemmL2x3x5` fp32 at 0x99990000 | 5.58 W | -9.62% | -10.52% | -2.01% | **-11.55%** | -0.0069 (tie) | -0.0077 (tie) | -8.99% | -8.02% | -7.11% | equal |
| a014 | L | `gemmL8x1x4` fp32 at 0x30000000 | 1.10 W (watts point) | 0.278 W | 0.315 W | -1.12% | +2.40% | -0.069 W (v3) | -0.068 W (v3) | 0.209 W | 0.237 W | 0.138 W | equal |
| a015 | L | `gemmL1x9x6` fp32 at 0x2002202 | 2.54 W (watts point) | 0.500 W | 0.233 W | -1.89% | **-10.84%** | -0.070 W (v3) | -0.021 W (tie) | 0.429 W | 0.407 W | 0.370 W | equal |
| a016 | L | `gemmL2x6x10` fp32 at 0x4404444 | 3.86 W | +11.27% | +12.06% | +1.45% | +6.43% | +0.0188 (v3.1) | +0.0193 (v3.1) | +13.38% | +15.17% | +14.72% | equal |
| a017 | L | `gemmL1x8x6` fp32 at 0xd000dd0 | 5.35 W | +4.91% | +5.69% | +0.89% | +6.94% | +0.0105 (v3.1) | +0.0113 (v3.1) | +6.02% | +5.95% | +6.13% | equal |
| a018 | L | `gemmL2x4x16` fp32 at 0x990009 | 3.58 W | +1.97% | +1.46% | +0.26% | -3.60% | +0.0178 (v3.1) | +0.0187 (v3.1) | +3.80% | +6.29% | +4.45% | equal |
| a019 | L | `gemmL1x7x6` fp32 at 0x10100000 | 1.37 W (watts point) | 0.270 W | 0.227 W | -1.08% | -4.20% | -0.072 W (v3) | -0.055 W (v3) | 0.198 W | 0.232 W | 0.142 W | equal |
| a020 | L | `gemmL2x4x4` fp32 at 0xee0e00 | 6.36 W | -9.62% | -10.80% | -2.24% | **-15.38%** | -0.0046 (tie) | -0.0052 (tie) | -9.21% | -8.40% | -6.99% | equal |
| a053 | S | `gemmL3x1x3` int8, pattern:i8_den6 | 5.96 W | -6.68% | -6.26% | -1.43% | +0.67% | - | - | - | -7.90% | - | equal |
| a054 | S | `gemmL3x1x3` int8, pattern:i8_den3 | 5.45 W | -5.36% | -4.90% | -1.06% | +1.10% | - | - | - | -6.70% | - | equal |
| a055 | S | `gemmL3x1x3` fp32, pattern:pow2 | 14.54 W | +7.21% | +7.36% | +2.64% | +3.31% | - | - | - | +6.54% | - | equal |
| a056 | S | `gemmL3x1x3` fp32, pattern:den21 | 20.17 W | +4.46% | +4.59% | +2.01% | +2.60% | - | - | - | +3.97% | - | equal |
| a057 | S | `gemmL3x1x3` int8, pattern:i8_pm1 | 8.53 W | **-19.12%** | **-18.88%** | -5.94% | -4.17% | - | - | - | -19.83% | - | equal |
| a058 | S | `gemmL3x1x3` fp32, pattern:lanes2 | 11.80 W | +1.36% | +1.52% | +0.45% | +1.14% | - | - | - | +0.61% | - | equal |
| a059 | S | `gemmL3x1x3` fp32, pattern:fp16grid | 18.79 W | +0.91% | +1.04% | +0.41% | +0.99% | - | - | - | +0.42% | - | equal |
| a060 | S | `gemmL3x1x3` fp32, pattern:bf16trunc | 17.50 W | +2.13% | +2.27% | +0.90% | +1.51% | - | - | - | +1.59% | - | equal |

## 6. REPORTED beside the verdicts (never verdicts)

E215.md 7: "REPORTED beside, never verdicts: MM1-v2's, MM1-v3's and 'v3.1 with T7''s cells at MM1-v3.1's bands; the rms and bias of ln(measured / forecast) of all four models by family; every flag." Beside every head-to-head, "and the same sign test, cases and ties for MM1-v3.1 against MM1-v2 and for 'v3.1 with T7' against MM1-v3.1 (the walk's layout term at never-run layouts; at family L's points the two time forms differ by up to 28% in the wall cycles)."

**'v3.1 with T7' against MM1-v3.1** (the same sign test, cases and ties; T7 / MM1-v3.1 / ties; the scorer's REPORTED pair, equal to verify-e215d's and to this lane's copy of the scorer's pair loop):

| registered (families P, C, R) | over | T7 closer | MM1-v3.1 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 32 | 12 | 17 | 3 | 0.458 | NOT DECIDED |
| H2 | 32 | 12 | 17 | 3 | 0.458 | NOT DECIDED |
| H3 | 32 | 12 | 17 | 3 | 0.458 | NOT DECIDED |
| H4 | 32 | 1 | 1 | 30 | - | TOO FEW |
| H5 | 32 | 2 | 1 | 29 | - | TOO FEW |

| post hoc (families L, S; reported apart) | over | T7 closer | MM1-v3.1 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 20 | 12 | 5 | 3 | 0.143 | NOT DECIDED |
| H2 | 20 | 13 | 4 | 3 | 0.049 | v3.1 with T7 CLOSER |
| H3 | 20 | 12 | 6 | 2 | 0.238 | NOT DECIDED |
| H4 | 28 | 4 | 5 | 19 | - | TOO FEW |
| H5 | 28 | 3 | 8 | 17 | 0.227 | NOT DECIDED |

**MM1-v3.1 against MM1-v2** (the same test; MM1-v3.1 / MM1-v2 / ties):

| registered (families P, C, R) | over | MM1-v3.1 closer | MM1-v2 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 32 | 20 | 11 | 1 | 0.15 | NOT DECIDED |
| H2 | 32 | 20 | 11 | 1 | 0.15 | NOT DECIDED |
| H3 | 32 | 20 | 11 | 1 | 0.15 | NOT DECIDED |
| H4 | 32 | 13 | 10 | 9 | 0.678 | NOT DECIDED |
| H5 | 32 | 14 | 9 | 9 | 0.405 | NOT DECIDED |

| post hoc (families L, S; reported apart) | over | MM1-v3.1 closer | MM1-v2 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 20 | 6 | 14 | 0 | 0.115 | NOT DECIDED |
| H2 | 20 | 5 | 15 | 0 | 0.0414 | MM1-v2 CLOSER |
| H3 | 20 | 6 | 14 | 0 | 0.115 | NOT DECIDED |
| H4 | 20 | 3 | 5 | 12 | - | TOO FEW |
| H5 | 20 | 4 | 4 | 12 | - | TOO FEW |

**Every model's cells at MM1-v3.1's bands** (the scorer's REPORTED counts for T1-T3, E1 and E2; E3 and E4 for the other models are desk arithmetic, section 7's clause on them):

| registered (families P, C, R) | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.1 (the registered model) | FAIL 27/32 | PASS 30/32 | FAIL 27/32 | FAIL 28/32 | FAIL 28/32 | FAIL 28/32 | FAIL 28/32 |
| MM1-v3 | FAIL 27/32 | PASS 30/32 | FAIL 27/32 | FAIL 28/32 | FAIL 28/32 | FAIL 28/32 (desk; the scorer: NO DATA, n 0) | FAIL 28/32 (desk; the scorer: NO DATA, n 0) |
| v3.1 with T7 | FAIL 25/32 | PASS 30/32 | FAIL 25/32 | FAIL 28/32 | FAIL 28/32 | FAIL 28/32 (desk; the scorer: NO DATA, n 0) | FAIL 28/32 (desk; the scorer: NO DATA, n 0) |
| MM1-v2 | FAIL 23/32 | FAIL 26/32 | FAIL 23/32 | FAIL 26/32 | FAIL 25/32 | FAIL 28/32 (desk; the scorer: NO DATA, n 0) | FAIL 23/32 (desk; the scorer: NO DATA, n 0) |

| post hoc (families L, S; reported apart) | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.1 (the registered model) | FAIL 16/20 | FAIL 17/20 | FAIL 16/20 | PASS 27/28 | PASS 27/28 | PASS 28/28 | FAIL 24/28 |
| MM1-v3 | FAIL 17/20 | FAIL 17/20 | FAIL 17/20 | PASS 19/20 | PASS 19/20 | PASS 20/20 (desk; the scorer: NO DATA, n 0) | FAIL 17/20 (desk; the scorer: NO DATA, n 0) |
| v3.1 with T7 | FAIL 16/20 | PASS 18/20 | FAIL 16/20 | FAIL 25/28 | FAIL 24/28 | PASS 27/28 (desk; the scorer: NO DATA, n 0) | FAIL 24/28 (desk; the scorer: NO DATA, n 0) |
| MM1-v2 | FAIL 17/20 | PASS 19/20 | FAIL 16/20 | PASS 19/20 | PASS 19/20 | PASS 20/20 (desk; the scorer: NO DATA, n 0) | FAIL 15/20 (desk; the scorer: NO DATA, n 0) |

**rms of the relative error, measured / forecast - 1** (desk arithmetic on the scorer's measured values and the frozen forecasts; equal to verify-e215d's in every figure; time per case, energy per point; J over idle at points of 3 W and more, the watts points' W error apart):

| registered (families P, C, R) | wall cycles (cases) | counter's mean | seconds | J over idle given t (points) | J over idle, t forecast | J at rest given t (points) | J at rest, t forecast | W at the watts points, given t |
|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 7.20% (32) | 6.97% | 7.18% | 10.70% (32) | 10.68% | 4.49% (32) | 5.82% | - |
| MM1-v3 | 6.87% (32) | 6.54% | 6.85% | 10.71% (32) | 10.67% | 4.49% (32) | 5.67% | - |
| v3.1 with T7 | 7.40% (32) | 7.01% | 7.38% | 10.59% (32) | 10.58% | 4.46% (32) | 6.08% | - |
| MM1-v2 | 10.74% (32) | 10.19% | 10.74% | 11.38% (32) | 11.72% | 4.61% (32) | 8.77% | - |

Without the gemmLnc points (a post hoc reading; J over idle given t (n), with t forecast, J at rest given t, with t forecast): MM1-v3.1 3.54% (28), 3.62%, 1.28%, 4.67%; MM1-v3 3.83% (28), 3.85%, 1.38%, 4.56%; v3.1 with T7 3.50% (28), 3.61%, 1.25%, 5.10%; MM1-v2 5.62% (28), 6.88%, 1.71%, 8.99%.

| post hoc (families L, S; reported apart) | wall cycles (cases) | counter's mean | seconds | J over idle given t (points) | J over idle, t forecast | J at rest given t (points) | J at rest, t forecast | W at the watts points, given t |
|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 9.16% (20) | 10.11% | 9.11% | 6.96% (25) | 7.24% | 1.98% (28) | 6.89% | 0.37 W (3) |
| MM1-v3 | 8.24% (20) | 9.24% | 8.19% | 6.58% (17) | 7.05% | 1.67% (20) | 7.47% | 0.30 W (3) |
| v3.1 with T7 | 12.47% (20) | 12.40% | 12.47% | 7.46% (25) | 7.77% | 1.96% (28) | 9.51% | 0.30 W (3) |
| MM1-v2 | 7.45% (20) | 7.32% | 7.45% | 6.36% (17) | 7.11% | 1.59% (20) | 7.33% | 0.24 W (3) |

**By family** (the scorer's REPORTED rms / bias of ln(measured / forecast), in percent: the wall cycles per point, J over idle at points of 3 W and more, and the watts points' W in watts):

| family | model | wall cycles: rms / bias (n) | J over idle: rms / bias (n) | watts points: rms / bias (n) |
|---|---|---|---|---|
| C | MM1-v3.1 | 5.96% / +1.34% (10) | 2.39% / -2.30% (10) | - |
| C | MM1-v3 | 5.42% / +1.92% (10) | 3.21% / -3.10% (10) | - |
| C | v3.1 with T7 | 6.03% / +2.63% (10) | 2.23% / -2.08% (10) | - |
| C | MM1-v2 | 9.83% / +5.19% (10) | 7.78% / +3.92% (10) | - |
| L | MM1-v3.1 | 9.67% / -7.33% (20) | 7.02% / -3.07% (17) | 0.261 W / -0.258 W (3) |
| L | MM1-v3 | 8.65% / -5.96% (20) | 7.09% / -2.51% (17) | 0.212 W / -0.210 W (3) |
| L | v3.1 with T7 | 11.69% / -2.97% (20) | 7.37% / -1.57% (17) | 0.474 W / -0.453 W (3) |
| L | MM1-v2 | 7.24% / -0.04% (20) | 7.00% / -1.85% (17) | 0.282 W / -0.270 W (3) |
| P | MM1-v3.1 | 8.39% / -5.19% (12) | 14.76% / +4.95% (12) | - |
| P | MM1-v3 | 7.01% / -4.12% (12) | 14.72% / +4.74% (12) | - |
| P | v3.1 with T7 | 7.22% / -4.10% (12) | 14.74% / +5.00% (12) | - |
| P | MM1-v2 | 9.03% / -3.03% (12) | 14.66% / +7.59% (12) | - |
| R | MM1-v3.1 | 6.85% / +5.70% (10) | 3.51% / -0.07% (10) | - |
| R | MM1-v3 | 7.62% / +6.43% (10) | 3.34% / +0.33% (10) | - |
| R | v3.1 with T7 | 8.22% / +7.00% (10) | 3.29% / +0.59% (10) | - |
| R | MM1-v2 | 11.31% / +9.43% (10) | 5.28% / -0.82% (10) | - |
| S | MM1-v3.1 | - | 8.54% / -2.00% (8) | - |
| S | MM1-v3 | - | - | - |
| S | v3.1 with T7 | - | 8.98% / -2.97% (8) | - |
| S | MM1-v2 | - | - | - |

**The readings** (registered before the data; the scorer's `readings_REPORTED`):

- **(a) The census path** (family P's two loops at one shape, measured ratio beside each model's), rgm136 gemmLnc / rgm211 gemmLn at x12x4 (a026 over a022): wall cycles measured 0.9328 (models: MM1-v2 1.0000, MM1-v3 1.0248, MM1-v3.1 1.0242, v3.1 with T7 1.0249); W over idle measured 1.2484.
- **(a) The census path** (family P's two loops at one shape, measured ratio beside each model's), rgm136 gemmLnc / rgm211 gemmLn at x15x3 (a024 over a021): wall cycles measured 0.9264 (models: MM1-v2 1.0000, MM1-v3 1.0248, MM1-v3.1 1.0242, v3.1 with T7 1.0249); W over idle measured 1.2623.
- **(b) The layout** (gemmL1x9x6 fp32 random, 24 shires, points a009, a010): the measured spread of the wall cycles 0.31% (max over min, less 1); MM1-v3.1's forecast spread 0.00%, 'v3.1 with T7''s 0.00%.
- **(b) The layout** (gemmL1x9x6 fp32 random, 28 shires, points a001, a002, a003, a004, a005, a006, a007, a008): the measured spread of the wall cycles 0.64% (max over min, less 1); MM1-v3.1's forecast spread 0.00%, 'v3.1 with T7''s 0.00%.
- **(c) The switch route** (each family-S kind's W over idle over its random partner's, measured, beside MM1-v3.1's ratio and 'v3.1 with T7''s; MM1-v3 and MM1-v2 price none of these kinds): a053, pattern:i8_den6 / random (int8, gemmL3x1x3): measured 0.5700, MM1-v3.1 0.5987, T7 0.6019; a054, pattern:i8_den3 / random (int8, gemmL3x1x3): measured 0.5210, MM1-v3.1 0.5394, T7 0.5429; a055, pattern:pow2 / random (fp32, gemmL3x1x3): measured 0.5896, MM1-v3.1 0.5691, T7 0.5708; a056, pattern:den21 / random (fp32, gemmL3x1x3): measured 0.8181, MM1-v3.1 0.8106, T7 0.8112; a057, pattern:i8_pm1 / random (int8, gemmL3x1x3): measured 0.8162, MM1-v3.1 0.9907, T7 0.9908; a058, pattern:lanes2 / random (fp32, gemmL3x1x3): measured 0.4785, MM1-v3.1 0.4885, T7 0.4906; a059, pattern:fp16grid / random (fp32, gemmL3x1x3): measured 0.7621, MM1-v3.1 0.7816, T7 0.7825; a060, pattern:bf16trunc / random (fp32, gemmL3x1x3): measured 0.7099, MM1-v3.1 0.7194, T7 0.7205.
- **(e) The timing simulation against reality** (his question): each point's measured cycles a GEMM over the simulator's step count (MM1-v3's column: one step an instruction, not time) reads 18.14 to 35.10 over 53 points and references; the counter's mean over the tensor unit's floor (529 cycles an op for fp32 and fp16, 270 for int8, measured) reads 1.573 to 6.000 over 62. Every point's pair of figures is in the JSON (`readings_REPORTED` > `timing_simulation`).
- **(f) The ties and the day offset:** 3 tie runs (gemmL2x4x4 fp32 random, the full chip, aifoundry3 card 0) read W over idle 19.485 W against the committed reference's 19.860 W: offset_W -1.89%, the seconds +0.098%. H4n and H5n (H4 and H5 re-read with every measured J divided by 1 + offset_W): posthoc:H4n TOO FEW (3/3/14); posthoc:H5n TOO FEW (3/2/15); registered:H4n TOO FEW (4/0/28); registered:H5n TOO FEW (3/0/29).
- **Flags:** none (no run set aside, no family dropped, no label).
- **(d) The card transfer** (the configurations both arms run) needs both arms in one data file: this one-arm file holds none; dated note 3 of arm B's directory gives it from the pooled run.

## 7. Dated clauses (Thu 19 Nov 2026), answering the card lane's, the verifier's and the fix lane's findings

1. **Arm A's registered E2 is decided by one point at the band's edge** (verify-e215d's finding 1; fix-e215d's clause, checked here with the frozen scorer's own cell). E2 reads FAIL 28/32 (29 needed). The nearest miss is a026 (gemmLnc1x12x4), whose J over idle with the seconds forecast came out +13.021% against the 13% band: measured 0.132028 J against MM1-v3.1's frozen 0.116817 J, the band's edge 0.132004 J. It stayed outside under every reading verify-e215d tried (the mean of run J against the product of the means, either edge of the work window, and no rest-edge sample). The other misses: a024 +13.80%, a031 +38.84%, a032 +37.56%. Any one of the four inside its band would have made E2 29/32 PASS; a026 is the nearest, 0.021 points outside. **The verdict stands as registered.**
2. **The registered energy rules fail on the gemmLnc points, as E215.md said before the data** (card-e215a's medium finding): every E1-E3 miss is one of the four gemmLnc points (a024 +14.54%, a026 +13.73%, a031 +38.79%, a032 +37.56% in E1). The card ran two of their cases about 15% faster than forecast (gemmLnc1x12x4 and gemmLnc1x15x3: T1 -14.75% and -15.46%) and the other two within 1.1% (gemmLnc5x1x10, gemmLnc8x1x5). E215.md 7: "Arm A's registered group holds 4 gemmLnc points of 32 energy points; misses at all 4 would leave 28 of 32 (87.5%) and fail E1 and E2 by themselves. This is MM1-v3.1's known gap, tested blind, not a fault of the day." E4 misses two of them (a031, a032) and a043 and a044 (gemmL2x1x7 fp32 and int8). The registered T1 and T3 misses are the two faster gemmLnc cases, gemmL2x1x7 fp32 and int8, and gemmL8x15x1 int8 (section 4). No datum, rule or verdict changes.
3. **On the post hoc layout family L, MM1-v3 is closer than MM1-v3.1 on time** (card-e215a's second medium finding): H1-H3 read MM1-v3 BETTER (p 0.0129, 0.00183, 0.0129) and T1-T3 FAIL, the card running 10-20% faster than forecast at four subset masks (0x33000333, 0x2002202, 0x99990000, 0xee0e00). These are post hoc readings, reported apart by D1 ("families L and S are ADOPTED in both arms, labelled 'points chosen post hoc after the fit; forecasts frozen before any E215 datum'."); they are not E215's answer.
4. **The other models' E3 and E4 at MM1-v3.1's bands** (verify-e215d's finding 2; fix-e215d's clause): the frozen scorer's REPORTED cells for the other models hold T1-T3, E1 and E2 only; its E3 and E4 for MM1-v3, MM1-v2 and 'v3.1 with T7' read NO DATA (n 0) in both arms because it does not compute them. Desk arithmetic (REPORTED, not verdicts; the scorer's own given() and its inclusion rule for the other models; equal in every cell to verify-e215d's and fix-e215d's counts): registered MM1-v3 E3 28/32, E4 28/32, MM1-v2 E3 28/32, E4 23/32, v3.1 with T7 E3 28/32, E4 28/32; post hoc MM1-v3 E3 20/20, E4 17/20, MM1-v2 E3 20/20, E4 15/20, v3.1 with T7 E3 27/28, E4 24/28. No verdict changes.
5. **The model session's sealed forecast** of E215's points (registered as a freeze line of both arms in `18398ed2`, 11:43:33 PST, before either arm's first card command) is the model session's to score: the lab neither read nor scored it, and nothing of it is in this note.
6. **The card time ran 3.4 card-minutes over plan** (card-e215a's low finding): 52.76 card-minutes against 49.4 planned, inside the registered 60-minute run rule and 70-minute cap; the die gate's waits (586 s in all over 73 runs) made the difference. Nothing of the scoring depends on it.
7. **Arm B's never-run report carries an arm A line** that is not arm A's judgement: arm A's own step 6n (12:05:06-12:05:17 PST, before its first card command) read 60 of 60 never ran, and this directory's labels are empty. Arm B's dated note 1 says what that line reads.

## 8. NOT RUN

- An independent re-derivation of the bands' bases B1 and B2 from MM1-v3.1's fold records (verify-e215d re-derived the bands from the registered bases only).
- Independent code for the REPORTED bootstrap intervals, the family check, H4n and H5n and the readings: they are the frozen scorer's own figures, reproduced byte for byte by its re-runs, not re-derived by other code.
- Any score of the frozen terms posted before the data (the gemmLnc term and the layout term, landed in `aaeaa495` and `595fcb59`): not this note's; nothing of them is read here.
- Any read of a box's disk.

## What this note changes

Nothing committed. It adds the frozen scorer's two output files, byte for byte as step 13 wrote them, this note and its hash list. Every verdict above is the scorer's as printed at 13:00:43 PST; the registered group's are E215 arm A's registered verdicts, and the post hoc group's stay reported apart.
