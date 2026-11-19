# E215 arm B data, dated note 2: the frozen scorer's output, committed beside the data byte for byte - registered (P, C, R): R0 and S6 PASS, T1 FAIL 15/18, T2 PASS 18/18, T3 FAIL 15/18, E1-E3 PASS 17/18, E4 FAIL 16/18, H1-H3 NOT DECIDED, H4 and H5 TOO FEW; post hoc (L, S) apart; with verify-e215d's re-derivation beside each result

*Thu 19 Nov 2026 (week 47), PST; written at about 15:50 PST by Q224's lane `scores-e215`, after this directory's data commit `4f648f24` (committed 14:14:38 PST, pushed by 14:14:44), after the day's data verifier `verify-e215d` (HOLDS WITH FIXES: both arms' data re-derive exactly from the raw records, its own scoring equals the frozen scorer's in every cell, verdict, count, p value and head-to-head, and its fixes are wording and records only) and after dated note 1 (`2b0c8814`, 15:21:43 PST, by `fix-e215d`). It adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. Labels: **registered** (E215.md with its dated departures D1 and D2, which change no rule or scorer), **measured** (this directory's committed records), **blind** (MM1-v3.1's, MM1-v3's, MM1-v2's and 'v3.1 with T7''s arm B forecasts, frozen by E215's registration `4cb2c2ad`, committed 06:32:24 PST Thu 19 Nov 2026 and on the lab repository's main branch by 06:32:29: arm B's freeze line, before arm B's first card command, fwgate's one firmware read at 13:41:24 PST, the session from 13:42:22), **REPORTED** (never a verdict), **post hoc** (families L and S, chosen after MM1-v3.1's fit and adopted by D1, and anything read after the data), **desk** (a check of code at the desk, under `/usr/bin/python3` 3.12.3).*

**The words.** The frozen scorer (`score_e215.py`, registered sha256 `cfa348d0...`), run by the kit's step 13 at 14:14:52 PST on this directory's committed `data-e215.json` with step 6n's committed `labels-e215.json` (no point and no case labelled 'ran before'), printed for arm B (aifoundry1 card 1 at 600 MHz, ET_DEVICES=1, nothing on card 0):

- **Registered (P, C, R; E215's answer):** **R0 PASS**; **S6 PASS**; **T1 FAIL** 15/18; **T2 PASS** 18/18; **T3 FAIL** 15/18; **E1 PASS** 17/18; **E2 PASS** 17/18; **E3 PASS** 17/18; **E4 FAIL** 16/18; head to head against MM1-v3 (the sign test, MM1-v3.1 / MM1-v3 / ties): **H1 NOT DECIDED** 5/7/6 (p 0.774); **H2 NOT DECIDED** 5/7/6 (p 0.774); **H3 NOT DECIDED** 5/7/6 (p 0.774); **H4 TOO FEW** 2/0/16; **H5 TOO FEW** 2/0/16.
- **Post hoc (L, S; reported apart, never the answer):** R0 PASS; S6 PASS; T1 TOO FEW 2/8; T2 TOO FEW 6/8; T3 TOO FEW 2/8; E1 PASS 12/12; E2 PASS 11/12; E3 PASS 12/12; E4 FAIL 10/12; H1 TOO FEW 1/5/2; H2 TOO FEW 1/5/2; H3 TOO FEW 1/5/2; H4 TOO FEW 0/0/8; H5 TOO FEW 0/0/8.
- Arm A: NO DATA in this one-arm file; the pooled HP1-HP5: NO DATA in this file. They are made by the same frozen scorer on both arms' committed data in dated note 3 of arm B's directory (`README.md.dated-note-3.md`, `scores-e215-pooled.json`).
- With R0 and S6 PASS, no verdict of arm B carries a label: these are arm B's registered verdicts (the registered group's) and its post hoc readings (the post hoc group's). "The registered answer is the registered group's (P, C, R); the post hoc group's (L, S) is reported apart."

**MM1-v3.1 against MM1-v3, rms of the relative error** (measured / forecast - 1; desk arithmetic on this directory's measured values and the frozen forecasts, equal to verify-e215d's in every figure; REPORTED; blind). Registered: the wall cycles 6.67% against 6.61% (18 cases), the counter's mean 5.38% against 5.10%, seconds 6.68% against 6.63%; J over idle given the seconds 12.80% against 12.97% (18 points), with the seconds forecast 12.81% against 12.98%; J with the card at rest given the seconds 4.66% against 4.72%, with the seconds forecast 7.03% against 7.11%. Without the gemmLnc points (a post hoc reading), J over idle given the seconds 3.68% against 4.00% (17 points). Post hoc group: the wall cycles 10.39% against 9.58% (8 cases); J over idle given the seconds 6.51% (10 points at 3 W or more) against 7.06% (6: MM1-v3 prices no family-S kind). Section 6 has every model and quantity.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e215-B.json` | 85,737 | `47c13d968a967843d491d9a83705d2582fe128223819aa3815ff3902a78f1ceb` | the frozen scorer's output (`score_e215.py`, registered sha256 `cfa348d0...`): every verdict, count, cell, measured point, head-to-head count and REPORTED reading of arm B, both groups; arm A and the pooled rules NO DATA |
| `scores-e215-B.txt` | 2,533 | `f0d35bc190e2ff32dd90ff9b8ce1134e42e8a49b92fd1c5a5ce2284a020ff47c` | its printed lines (step 13's capture of the call) |
| `README.md.dated-note-2.md` | (this note) | listed in `SHA256SUMS-note2` | this dated note |
| `SHA256SUMS-note2` | 4 lines | (not listed in itself) | the three files above and `SHA256SUMS-note1` |

The two output files are card-e215b's RB_OUT files of its second booking (its first booking sent nothing to either card and never reached step 13) byte for byte. With `SHA256SUMS` (416 entries), `SHA256SUMS-note1` (6: note 1's four files, `README.md` and `SHA256SUMS`) and `SHA256SUMS-note2` (4), every file of this directory is in a list except `SHA256SUMS-note2` itself. Dated note 3 (the pooled rules), committed after this note, brings its own list, `SHA256SUMS-note3`, which lists `SHA256SUMS-note2`.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e215.sh B`) is the runbook log's last six lines (lines 124-129 of 129), at 14:14:52-14:14:52 PST, each rc 0, the six captures under one process id. Call 1 printed the data commit `4f648f24b` and its subject; call 2 (the directory clean) printed nothing; call 3 read all 416 `SHA256SUMS` entries OK, in the list's order; call 4 printed `HISTORY OK` naming the registration `4cb2c2ad6092`; call 5 printed `LABELS-OK`; call 6 ran `/usr/bin/python3 -I -B tools/claims-v3/e215/score_e215.py docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/data-e215.json --labels docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/labels-e215.json --out <the card lane's RB_OUT>/scores-e215-B.json` (0.4 s). The log holds no earlier run of the scorer on data: only its two self-tests and the print-only forecasts helper, in the runbook's desk step (`s03_desk_e215`, 13:39:39 PST, rc 0); no run of `score_e215.py --forecasts` at all (the kit runs its print-only helper `rb/forecasts_print_e215.py` there, so no registered file is rewritten).
- **The bytes.** `scores-e215-B.txt` is the runbook's capture of call 6 byte for byte (the step's copy of it), and it rebuilds exactly from the JSON through the scorer's own print function (`text()`, read from `score_e215.py` at the data commit). The JSON is in the scorer's own dump form (indent 1, sorted keys, no trailing newline) and was last written inside call 6 (its time stamp 14:14:52.671 PST, call 6's capture 14:14:52.671); the text file was copied after it (14:14:52.681).
- **The commit before it.** The data commit `4f648f24` was made at 14:14:38 PST and pushed by 14:14:44; at 14:14:44 the card lane left its collect span, removed its hold line and released aifoundry1; step 13 ran at 14:14:52. The lab clone's HEAD during the step was the data commit itself (its reflog: `4f648f24` from 14:14:38 until 14:46:15, when `fd8b0ef4` followed). None of the 13 committed files the scorer opens changed from the data commit to the lab's HEAD when this note was built; the data directory has had only additions (dated note 1, five files) since its data commit.
- **The frozen files.** The registration list's 35 files and the list itself have one blob each at `4cb2c2ad` (the registration), `8bde0182` (the kit), `18398ed2` (the seal's registration), the data commit and HEAD; the kit list's 62 files and the list from `8bde0182` on; MM1-v3.1's land files (E215.md section 0, arm A's table: 18 files of MM1-v3.1, MM1-v3 and MM1-v2) from `2c971828` on, at their listed sha256; arm B's forecasts and the folder's frozen files (section 0's other tables: 25 files) at their listed sha256 from `4cb2c2ad` on; `tools/claims-v3/e215/` unchanged from the kit to HEAD. The scorer's ten pins equal those files' sha256 at the data commit.
- **The re-runs.** In a tree of exactly the 13 committed files the scorer opens (its own file, its ten pinned inputs, `data-e215.json` and `labels-e215.json`), taken from the data commit's objects, with no bytecode cache, a plain run and a run under an audit hook that lists every file opened, each with step 13's arguments, wrote both outputs byte for byte equal to RB_OUT and to the capture of call 6; the audited run opened those 13 files, 33 standard-library files and nothing else but its own outputs. The scorer imported unchanged and called in process (`score(data, labels, quiet=True)`) gives a result whose dump equals RB_OUT's JSON byte for byte; its own functions (`reduce_arm`, `score_group`, `decide`), called as `score()` calls them, give every case's and point's d value (the JSON keeps only the counts), with the JSON's counts, p values and cells. Sections 4 and 5 print those d values.
- **verify-e215d beside.** verify-e215d re-derived this directory's `data-e215.json` from the raw records (run records, process outputs and telemetry: 0 mismatches) and scored it with code that imports nothing of the kit's: its 198 cells, every pass flag, count, verdict and head-to-head (n, closer counts, ties, p), and its REPORTED 'v3.1 with T7' and MM1-v2 sign tests equal the scorer's. This lane compared its cells and d values with the scorer's own: the same cases and points, worst difference 0 (at a watts cell the scorer stores |W - W_fc| and verify-e215d the signed W - W_fc, the same number). Its rms tables equal this lane's in every figure.

## 3. The rules: their registered words, the verdicts, verify-e215d beside

The scorer's printed lines (`scores-e215-B.txt`, verbatim):

```
E215 scorer (score_e215.py), the verdicts - registered: families P, C, R; post hoc (reported apart): families L, S, 'points chosen post hoc after the fit; forecasts frozen before any E215 datum':
ARM A REGISTERED (P, C, R): R0 NO DATA; S6 NO DATA; T1 NO DATA; T2 NO DATA; T3 NO DATA; E1 NO DATA; E2 NO DATA; E3 NO DATA; E4 NO DATA
  registered H1 NO DATA
  registered H2 NO DATA
  registered H3 NO DATA
  registered H4 NO DATA
  registered H5 NO DATA
ARM A POSTHOC (L, S): R0 NO DATA; S6 NO DATA; T1 NO DATA; T2 NO DATA; T3 NO DATA; E1 NO DATA; E2 NO DATA; E3 NO DATA; E4 NO DATA
  posthoc H1 NO DATA
  posthoc H2 NO DATA
  posthoc H3 NO DATA
  posthoc H4 NO DATA
  posthoc H5 NO DATA
ARM B REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 15/18; T2 PASS 18/18; T3 FAIL 15/18; E1 PASS 17/18; E2 PASS 17/18; E3 PASS 17/18; E4 FAIL 16/18
  registered H1 NOT DECIDED (v3.1 5 / v3 7 / ties 6; p 0.7744140625); REPORTED bootstrap NOT DECIDED [-0.00981680812437277, 0.001432281652616267]
  registered H2 NOT DECIDED (v3.1 5 / v3 7 / ties 6; p 0.7744140625); REPORTED bootstrap NOT DECIDED [-0.009837747699500172, 0.0012983957725371592]
  registered H3 NOT DECIDED (v3.1 5 / v3 7 / ties 6; p 0.7744140625); REPORTED bootstrap NOT DECIDED [-0.009763313452354724, 0.001420814056779884]
  registered H4 TOO FEW (v3.1 2 / v3 0 / ties 16; p None); REPORTED bootstrap NOT DECIDED [-3.515087372426558e-05, 0.005687457819053954]
  registered H5 TOO FEW (v3.1 2 / v3 0 / ties 16; p None); REPORTED bootstrap NOT DECIDED [-0.00014715072590185149, 0.005127888479749306]
ARM B POSTHOC (L, S): R0 PASS; S6 PASS; T1 TOO FEW 2/8; T2 TOO FEW 6/8; T3 TOO FEW 2/8; E1 PASS 12/12; E2 PASS 11/12; E3 PASS 12/12; E4 FAIL 10/12
  posthoc H1 TOO FEW (v3.1 1 / v3 5 / ties 2; p None); REPORTED bootstrap MM1-v3 BETTER [-0.013842106370353366, -0.0025187823931589258]
  posthoc H2 TOO FEW (v3.1 1 / v3 5 / ties 2; p None); REPORTED bootstrap MM1-v3 BETTER [-0.013842078107036655, -0.0026327792637453034]
  posthoc H3 TOO FEW (v3.1 1 / v3 5 / ties 2; p None); REPORTED bootstrap MM1-v3 BETTER [-0.013842048935777923, -0.002508573590881095]
  posthoc H4 TOO FEW (v3.1 0 / v3 0 / ties 8; p None); REPORTED bootstrap NOT DECIDED [-0.0017488672263396832, 0.00460216317741997]
  posthoc H5 TOO FEW (v3.1 0 / v3 0 / ties 8; p None); REPORTED bootstrap NOT DECIDED [-0.0026924469855638157, 0.004174764819305433]
POOLED REGISTERED: HP1 NO DATA; HP2 NO DATA; HP3 NO DATA; HP4 NO DATA; HP5 NO DATA
POOLED POSTHOC: HP1 NO DATA; HP2 NO DATA; HP3 NO DATA; HP4 NO DATA; HP5 NO DATA
```

**MM1-v3.1's rules, per arm and group** (E215.md 7, its words): "Each case or point passes when |measured / MM1-v3.1 - 1| is within its band; a rule's verdict: PASS if at least 90% of its scored cases or points pass, FAIL otherwise, TOO FEW under 10, NO DATA with none." "The band is twice the larger of two held-out errors of MM1-v3.1 for that quantity, rounded up to a whole percent:" B1, the leave-one-experiment-out error over every point without configuration twins, and B2, the same over this arm's card's points. "The points under about 3 W over idle are scored in absolute watts in E1 and E2" "(a point whose MM1-v3.1 frozen W over idle is under 3 W, or whose measured W over idle is; E3 and E4 stay relative)"; "arm B 0.56 W = 2 x max(0.2794, 0.2607, SD_rep 0.08373) = 0.559 -> 0.56 W". The section's title: "a point or case with no run is NO DATA, never a failure". The scorer's 90% rule passes a rule when the passing cases or points number at least ceil(0.9 n). R0: "every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its identity gate GATE OK; a family smoke's failure with no run of its family (dropped by its own stop path) is flagged and REPORTED, not an R0 failure; with a run of its family it counts." S6: "every kept run's counted samples at 590-610 MHz." "A FAIL of either labels every other verdict of its arm."

**The registered (families P, C, R) group:**

| rule | the registered words (E215.md 7) | band | scored | needed (90%) | the scorer | verify-e215d's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | "every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its identity gate GATE OK; a family smoke's failure with no run of its family (dropped by its own stop path) is flagged and REPORTED, not an R0 failure; with a run of its family it counts." | - | every check of C of the arm (smoke, points, references, ties) | all | **PASS** (0 failures) | PASS | - | none |
| **S6** | "every kept run's counted samples at 590-610 MHz." | 590-610 MHz | every kept run | all | **PASS** (0 failures) | PASS | - | none |
| **T1** | "cycles an op, the wall, per case"; "2 x max(4.723, 4.998) = 10.00 -> 10%" | 10% | 18 | 17 | **FAIL** (15/18) | FAIL (15/18; the same cells, worst difference 0) | -2 | `gemmL16x14x1` fp32 (+10.90%); `gemmL2x1x7` fp32 (+12.74%); `gemmL2x1x7` int8 (+13.97%) |
| **T2** | "cycles an op, the counter's mean, per case"; "2 x max(6.050, 6.450) = 12.90 -> 13%" | 13% | 18 | 17 | **PASS** (18/18) | PASS (18/18; the same cells, worst difference 0) | 1 | none |
| **T3** | "seconds a GEMM, per case (T1's bases)"; "2 x max(4.723, 4.998) = 10.00 -> 10%" | 10% | 18 | 17 | **FAIL** (15/18) | FAIL (15/18; the same cells, worst difference 0) | -2 | `gemmL16x14x1` fp32 (+11.02%); `gemmL2x1x7` fp32 (+12.85%); `gemmL2x1x7` int8 (+14.08%) |
| **E1** | "J over idle given the measured seconds, per point (watts under 3 W)"; "2 x max(5.476, 6.623) = 13.25 -> 14%" | 14% (watts 0.56 W) | 18 | 17 | **PASS** (17/18) | PASS (17/18; the same cells, worst difference 0) | 0 | b013 (+52.14%) |
| **E2** | "J over idle with the seconds forecast, per point (watts under 3 W)"; "2 x max(6.014, 6.731) = 13.46 -> 14%" | 14% (watts 0.56 W) | 18 | 17 | **PASS** (17/18) | PASS (17/18; the same cells, worst difference 0) | 0 | b013 (+51.76%) |
| **E3** | "J with the card at rest given the measured seconds and rest, per point"; "2 x max(2.153, 2.321) = 4.64 -> 5%" | 5% | 18 | 17 | **PASS** (17/18) | PASS (17/18; the same cells, worst difference 0) | 0 | b013 (+19.01%) |
| **E4** | "J with the card at rest with the seconds forecast, per point"; "2 x max(4.473, 4.628) = 9.26 -> 10%" | 10% | 18 | 17 | **FAIL** (16/18) | FAIL (16/18; the same cells, worst difference 0) | -1 | b013 (+20.00%); b022 (+12.78%) |

**The post hoc (families L, S; reported apart) group:**

| rule | the registered words (E215.md 7) | band | scored | needed (90%) | the scorer | verify-e215d's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | "every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good and its identity gate GATE OK; a family smoke's failure with no run of its family (dropped by its own stop path) is flagged and REPORTED, not an R0 failure; with a run of its family it counts." | - | every check of C of the arm (smoke, points, references, ties) | all | **PASS** (0 failures) | PASS | - | none |
| **S6** | "every kept run's counted samples at 590-610 MHz." | 590-610 MHz | every kept run | all | **PASS** (0 failures) | PASS | - | none |
| **T1** | "cycles an op, the wall, per case"; "2 x max(4.723, 4.998) = 10.00 -> 10%" | 10% | 8 | - | **TOO FEW** (2/8) | TOO FEW (2/8; the same cells, worst difference 0) | - | `gemmL1x15x4` fp32 at 0xf0ffffff (-10.88%); `gemmL1x15x4` fp32 at 0xff0fffff (-10.93%); `gemmL1x15x4` fp32 at 0xfff0ffff (-11.25%); `gemmL1x15x4` fp32 at 0xffff0fff (-10.83%); `gemmL3x5x7` fp32 at 0x60000006 (-13.43%); `gemmL8x4x4` fp32 at 0x50005500 (-14.14%) |
| **T2** | "cycles an op, the counter's mean, per case"; "2 x max(6.050, 6.450) = 12.90 -> 13%" | 13% | 8 | - | **TOO FEW** (6/8) | TOO FEW (6/8; the same cells, worst difference 0) | - | `gemmL1x1x16` fp32 at 0xee000e (-20.99%); `gemmL8x4x4` fp32 at 0x50005500 (-14.09%) |
| **T3** | "seconds a GEMM, per case (T1's bases)"; "2 x max(4.723, 4.998) = 10.00 -> 10%" | 10% | 8 | - | **TOO FEW** (2/8) | TOO FEW (2/8; the same cells, worst difference 0) | - | `gemmL1x15x4` fp32 at 0xf0ffffff (-10.78%); `gemmL1x15x4` fp32 at 0xff0fffff (-10.83%); `gemmL1x15x4` fp32 at 0xfff0ffff (-11.14%); `gemmL1x15x4` fp32 at 0xffff0fff (-10.73%); `gemmL3x5x7` fp32 at 0x60000006 (-13.34%); `gemmL8x4x4` fp32 at 0x50005500 (-14.06%) |
| **E1** | "J over idle given the measured seconds, per point (watts under 3 W)"; "2 x max(5.476, 6.623) = 13.25 -> 14%" | 14% (watts 0.56 W) | 12 | 11 | **PASS** (12/12) | PASS (12/12; the same cells, worst difference 0) | 1 | none |
| **E2** | "J over idle with the seconds forecast, per point (watts under 3 W)"; "2 x max(6.014, 6.731) = 13.46 -> 14%" | 14% (watts 0.56 W) | 12 | 11 | **PASS** (11/12) | PASS (11/12; the same cells, worst difference 0) | 0 | b007 (-14.59%) |
| **E3** | "J with the card at rest given the measured seconds and rest, per point"; "2 x max(2.153, 2.321) = 4.64 -> 5%" | 5% | 12 | 11 | **PASS** (12/12) | PASS (12/12; the same cells, worst difference 0) | 1 | none |
| **E4** | "J with the card at rest with the seconds forecast, per point"; "2 x max(4.473, 4.628) = 9.26 -> 10%" | 10% | 12 | 11 | **FAIL** (10/12) | FAIL (10/12; the same cells, worst difference 0) | -1 | b006 (-13.64%); b007 (-14.13%) |

The slack is the passing count less the count the 90% rule needs (REPORTED, desk arithmetic): 0 passes at the rule's minimum, a negative slack is the shortfall; a rule under 10 scored reads TOO FEW, never PASS or FAIL. Errors are measured / MM1-v3.1 - 1; at a watts point E1 and E2 read |W - W_v3.1| in watts.

**THE HEAD-TO-HEAD RULES** (E215.md 7, its words): "per case (cycles, seconds) or per point (joules), d = |ln(measured / MM1-v3)| - |ln(measured / MM1-v3.1)| (at a watts point, |W - W_v3| - |W - W_v3.1| in watts); MM1-v3.1 is closer where d > the tie, MM1-v3 where d < -the tie, a tie otherwise." The ties: "arm B 0.005, 0.005, 0.01, 0.1 W". "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v3.1 BETTER if p < 0.05 and it is closer in more cases than not; MM1-v3 BETTER if p < 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none." HP1-HP5: "H1-H5 pooled over both arms per group, each case or point once with its own arm's tie; NO DATA unless both arms scored that group". Stated before the data: "the sign test's power is 2-8% wherever it can decide, and H4 and H5 are TOO FEW by construction". "So E215's head-to-head is registered, will be scored and printed, and is expected to read NOT DECIDED or TOO FEW whichever model is better: MM1-v3.1 and MM1-v3 differ by less than either's error."

**The registered (families P, C, R) group:**

| rule | the registered words (E215.md 7) | over | MM1-v3.1 closer | MM1-v3 closer | ties | p (exact, two-sided) | the scorer | verify-e215d | REPORTED: bootstrap 95% interval of the mean d (its reading) | REPORTED: the family check (family median d) | where MM1-v3 is closer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H1** | "cycles an op, the wall, per case" | 18 | 5 | 7 | 6 | 0.774 | **NOT DECIDED** | NOT DECIDED (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0098, +0.0014] (mean d -0.0041, n 18) | C -0.0120, P -0.0120, R +0.0065 | `gemmL10x15x2` fp32; `gemmL2x14x2` int8; `gemmL2x15x2` fp32; `gemmL3x15x2` fp32; `gemmLn1x10x5` fp32 (rgm211 gemmLn); `gemmLn1x12x4` fp32 (rgm211 gemmLn); `gemmLn1x15x3` fp32 (rgm211 gemmLn) |
| **H2** | "cycles an op, the counter's mean, per case" | 18 | 5 | 7 | 6 | 0.774 | **NOT DECIDED** | NOT DECIDED (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0098, +0.0013] (mean d -0.0042, n 18) | C -0.0120, P -0.0120, R +0.0051 | `gemmL10x15x2` fp32; `gemmL2x14x2` int8; `gemmL2x15x2` fp32; `gemmL3x15x2` fp32; `gemmLn1x10x5` fp32 (rgm211 gemmLn); `gemmLn1x12x4` fp32 (rgm211 gemmLn); `gemmLn1x15x3` fp32 (rgm211 gemmLn) |
| **H3** | "seconds a GEMM, per case" | 18 | 5 | 7 | 6 | 0.774 | **NOT DECIDED** | NOT DECIDED (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0098, +0.0014] (mean d -0.0041, n 18) | C -0.0120, P -0.0120, R +0.0065 | `gemmL10x15x2` fp32; `gemmL2x14x2` int8; `gemmL2x15x2` fp32; `gemmL3x15x2` fp32; `gemmLn1x10x5` fp32 (rgm211 gemmLn); `gemmLn1x12x4` fp32 (rgm211 gemmLn); `gemmLn1x15x3` fp32 (rgm211 gemmLn) |
| **H4** | "J over idle given the measured seconds, per point both price" | 18 | 2 | 0 | 16 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0000, +0.0057] (mean d +0.0029, n 18) | C +0.0079, P +0.0034, R -0.0050 | none |
| **H5** | "J over idle with the seconds forecast, per point both price" | 18 | 2 | 0 | 16 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0001, +0.0051] (mean d +0.0025, n 18) | C +0.0063, P +0.0028, R -0.0033 | none |

**The post hoc (families L, S; reported apart) group:**

| rule | the registered words (E215.md 7) | over | MM1-v3.1 closer | MM1-v3 closer | ties | p (exact, two-sided) | the scorer | verify-e215d | REPORTED: bootstrap 95% interval of the mean d (its reading) | REPORTED: the family check (family median d) | where MM1-v3 is closer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H1** | "cycles an op, the wall, per case" | 8 | 1 | 5 | 2 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0138, -0.0025] (mean d -0.0086, n 8) | L -0.0137 | `gemmL1x15x4` fp32 at 0xf0ffffff; `gemmL1x15x4` fp32 at 0xff0fffff; `gemmL1x15x4` fp32 at 0xfff0ffff; `gemmL1x15x4` fp32 at 0xffff0fff; `gemmL3x5x7` fp32 at 0x60000006 |
| **H2** | "cycles an op, the counter's mean, per case" | 8 | 1 | 5 | 2 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0138, -0.0026] (mean d -0.0086, n 8) | L -0.0137 | `gemmL1x15x4` fp32 at 0xf0ffffff; `gemmL1x15x4` fp32 at 0xff0fffff; `gemmL1x15x4` fp32 at 0xfff0ffff; `gemmL1x15x4` fp32 at 0xffff0fff; `gemmL3x5x7` fp32 at 0x60000006 |
| **H3** | "seconds a GEMM, per case" | 8 | 1 | 5 | 2 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | MM1-v3 BETTER [-0.0138, -0.0025] (mean d -0.0086, n 8) | L -0.0137 | `gemmL1x15x4` fp32 at 0xf0ffffff; `gemmL1x15x4` fp32 at 0xff0fffff; `gemmL1x15x4` fp32 at 0xfff0ffff; `gemmL1x15x4` fp32 at 0xffff0fff; `gemmL3x5x7` fp32 at 0x60000006 |
| **H4** | "J over idle given the measured seconds, per point both price" | 8 | 0 | 0 | 8 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0017, +0.0046] (mean d +0.0020, n 6) | L +0.0033 | none |
| **H5** | "J over idle with the seconds forecast, per point both price" | 8 | 0 | 0 | 8 | - | **TOO FEW** | TOO FEW (the same counts; every d equal, worst difference 0) | NOT DECIDED [-0.0027, +0.0042] (mean d +0.0013, n 6) | L +0.0024 | none |

## 4. Every case: cycles and seconds (T1-T3) and the head-to-head H1-H3, with verify-e215d beside

Errors are measured / MM1-v3.1 - 1 (the scorer's `err`; a miss in bold); d is the registered d (positive: MM1-v3.1 closer; the tie 0.005), from the frozen scorer's own functions (section 2); the closer is MM1-v3.1 (v3.1), MM1-v3 (v3) or a tie. MM1-v3's, 'v3.1 with T7''s and MM1-v2's wall errors are REPORTED beside (in parentheses after T7's: the closer of T7 and MM1-v3.1 by the same d and tie, REPORTED). Every case runs the full chip (mask 0xffffffff) on rgm136's gemmL loop unless the table names a mask or a loop. The last column compares verify-e215d's re-derivation (its own cells and d values) with the scorer's.

**The registered (families P, C, R) group** (18 cases):

| case | points | family | T1 wall | T2 counter | T3 seconds | H1 d (closer) | H2 d (closer) | H3 d (closer) | MM1-v3 wall (REPORTED) | v3.1 with T7 wall (REPORTED) | MM1-v2 wall (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemmLnc2x1x37` fp32 (rgm136 gemmLnc) | b013 | P | +1.88% | +2.31% | +1.47% | +0.0096 (v3.1) | +0.0096 (v3.1) | +0.0096 (v3.1) | +2.86% | +2.95% (v3.1) | +4.00% | equal |
| `gemmL10x15x2` fp32 | b017 | C | -4.18% | -3.57% | -4.06% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.81% | -2.47% (T7) | -2.11% | equal |
| `gemmL16x14x1` fp32 | b019 | C | **+10.90%** | +9.59% | **+11.02%** | -0.0046 (tie) | -0.0046 (tie) | -0.0046 (tie) | +10.39% | +12.31% (v3.1) | +16.36% | equal |
| `gemmL1x1x41` fp32 | b023 | R | +5.02% | +6.17% | +5.12% | +0.0105 (v3.1) | +0.0105 (v3.1) | +0.0105 (v3.1) | +6.13% | +6.28% (v3.1) | +9.42% | equal |
| `gemmL2x14x2` int8 | b018 | C | -3.93% | -2.98% | -3.83% | -0.0098 (v3) | -0.0098 (v3) | -0.0098 (v3) | -2.98% | -2.34% (T7) | -0.85% | equal |
| `gemmL2x15x2` fp32 | b015 | C | -4.37% | -4.11% | -4.27% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -3.00% | -2.67% (T7) | -2.30% | equal |
| `gemmL2x1x15` fp32 | b026 | R | -0.16% | +0.14% | -0.04% | +0.0026 (tie) | -0.0003 (tie) | +0.0026 (tie) | -0.42% | -0.72% (v3.1) | -5.73% | equal |
| `gemmL2x1x17` fp32 | b014 | P | -1.48% | -1.14% | -1.35% | +0.0017 (tie) | +0.0017 (tie) | +0.0017 (tie) | -1.65% | -1.99% (v3.1) | -5.82% | equal |
| `gemmL2x1x7` fp32 | b021 | R | **+12.74%** | +5.94% | **+12.85%** | +0.0121 (v3.1) | +0.0121 (v3.1) | +0.0121 (v3.1) | +14.11% | +15.35% (v3.1) | +21.63% | equal |
| `gemmL2x1x7` int8 | b022 | R | **+13.97%** | +7.08% | **+14.08%** | +0.0110 (v3.1) | +0.0110 (v3.1) | +0.0110 (v3.1) | +15.23% | +16.66% (v3.1) | +24.36% | equal |
| `gemmL3x15x2` fp32 | b016 | C | -4.08% | -3.46% | -3.96% | -0.0142 (v3) | -0.0142 (v3) | -0.0142 (v3) | -2.71% | -2.37% (T7) | -2.01% | equal |
| `gemmL3x2x9` int8 | b024 | R | +2.22% | +3.34% | +2.32% | -0.0009 (tie) | -0.0009 (tie) | -0.0009 (tie) | +2.12% | +1.90% (tie) | +1.53% | equal |
| `gemmL4x1x10` int8 | b025 | R | +2.67% | +2.47% | +2.80% | -0.0025 (tie) | -0.0025 (tie) | -0.0025 (tie) | +2.41% | +2.60% (tie) | -3.41% | equal |
| `gemmL9x1x1` int8 | b020 | C | +7.37% | +6.59% | +7.50% | +0.0107 (v3.1) | +0.0107 (v3.1) | +0.0107 (v3.1) | +8.52% | +8.19% (v3.1) | +8.09% | equal |
| `gemmLn1x10x5` fp32 (rgm211 gemmLn) | b011 | P | -7.11% | -7.72% | -6.99% | -0.0232 (v3) | -0.0232 (v3) | -0.0232 (v3) | -4.93% | -4.70% (T7) | -5.09% | equal |
| `gemmLn1x12x4` fp32 (rgm211 gemmLn) | b010 | P | -6.69% | -7.33% | -6.59% | -0.0233 (v3) | -0.0233 (v3) | -0.0233 (v3) | -4.50% | -4.15% (T7) | -4.47% | equal |
| `gemmLn1x15x3` fp32 (rgm211 gemmLn) | b009 | P | -6.81% | -7.36% | -6.70% | -0.0234 (v3) | -0.0234 (v3) | -0.0234 (v3) | -4.60% | -4.14% (T7) | -4.27% | equal |
| `gemmLn3x1x2` int8 (rgm211 gemmLn) | b012 | P | -4.25% | -4.46% | -4.15% | -0.0007 (tie) | -0.0007 (tie) | -0.0007 (tie) | -4.18% | -4.14% (tie) | -5.57% | equal |

**The post hoc (families L, S; reported apart) group** (8 cases; family S is scored in energy only, so its points hold no case here):

| case | points | family | T1 wall | T2 counter | T3 seconds | H1 d (closer) | H2 d (closer) | H3 d (closer) | MM1-v3 wall (REPORTED) | v3.1 with T7 wall (REPORTED) | MM1-v2 wall (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemmL1x15x4` fp32 at 0xf0ffffff | b001 | L | **-10.88%** | -11.19% | **-10.78%** | -0.0158 (v3) | -0.0158 (v3) | -0.0158 (v3) | -9.45% | -9.74% (T7) | -1.81% | equal |
| `gemmL1x15x4` fp32 at 0xff0fffff | b002 | L | **-10.93%** | -11.18% | **-10.83%** | -0.0158 (v3) | -0.0158 (v3) | -0.0158 (v3) | -9.51% | -9.79% (T7) | -1.87% | equal |
| `gemmL1x15x4` fp32 at 0xfff0ffff | b003 | L | **-11.25%** | -11.35% | **-11.14%** | -0.0158 (v3) | -0.0158 (v3) | -0.0158 (v3) | -9.83% | -10.11% (T7) | -2.22% | equal |
| `gemmL1x15x4` fp32 at 0xffff0fff | b004 | L | **-10.83%** | -10.98% | **-10.73%** | -0.0158 (v3) | -0.0158 (v3) | -0.0158 (v3) | -9.41% | -9.69% (T7) | -1.76% | equal |
| `gemmL1x1x16` fp32 at 0xee000e | b008 | L | -1.40% | **-20.99%** | -1.29% | +0.0001 (tie) | +0.0001 (tie) | +0.0001 (tie) | -1.41% | +36.87% (v3.1) | +4.85% | equal |
| `gemmL2x1x16` fp32 at 0xcc000 | b005 | L | +0.25% | +1.31% | +0.33% | +0.0002 (tie) | +0.0002 (tie) | +0.0002 (tie) | +0.27% | +37.58% (v3.1) | +6.29% | equal |
| `gemmL3x5x7` fp32 at 0x60000006 | b006 | L | **-13.43%** | -12.48% | **-13.34%** | -0.0116 (v3) | -0.0116 (v3) | -0.0116 (v3) | -12.41% | -2.06% (T7) | -6.72% | equal |
| `gemmL8x4x4` fp32 at 0x50005500 | b007 | L | **-14.14%** | **-14.09%** | **-14.06%** | +0.0055 (v3.1) | +0.0055 (v3.1) | +0.0055 (v3.1) | -14.61% | -23.50% (v3.1) | -11.44% | equal |

## 5. Every point: joules (E1-E4) and the head-to-head H4 and H5, with verify-e215d beside

E1 and E3 use the measured seconds (MM1-v3.1's frozen affine W at the measured op time); E2 and E4 the seconds forecast. At a watts point E1 and E2 read |W - W_v3.1| in watts against the watts band, and H4 and H5 the registered watts d (positive: MM1-v3.1 closer; the watts tie). The W column is the measured W over idle. MM1-v3's, 'v3.1 with T7''s and MM1-v2's E1 errors are REPORTED beside ('-' where the model prices no energy for the point's kind: MM1-v3 and MM1-v2 price no family-S kind).

**The registered (families P, C, R) group** (18 points):

| point | family | case | W over idle | E1 | E2 | E3 | E4 | H4 d (closer) | H5 d (closer) | MM1-v3 E1 (REPORTED) | v3.1 with T7 E1 (REPORTED) | MM1-v2 E1 (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b009 | P | `gemmLn1x15x3` fp32 (rgm211 gemmLn) | 21.16 W | -3.35% | -3.69% | -1.46% | -5.44% | +0.0038 (tie) | +0.0024 (tie) | -3.72% | -3.02% | -0.65% | equal |
| b010 | P | `gemmLn1x12x4` fp32 (rgm211 gemmLn) | 20.98 W | -3.59% | -3.93% | -1.56% | -5.48% | +0.0030 (tie) | +0.0016 (tie) | -3.89% | -3.29% | -1.59% | equal |
| b011 | P | `gemmLn1x10x5` fp32 (rgm211 gemmLn) | 21.01 W | -3.47% | -3.82% | -1.50% | -5.66% | +0.0026 (tie) | +0.0011 (tie) | -3.71% | -3.17% | -1.85% | equal |
| b012 | P | `gemmLn3x1x2` int8 (rgm211 gemmLn) | 11.89 W | -1.69% | -2.08% | -0.51% | -3.54% | +0.0043 (tie) | +0.0044 (tie) | -2.11% | -2.10% | +2.26% | equal |
| b013 | P | `gemmLnc2x1x37` fp32 (rgm136 gemmLnc) | 24.80 W | **+52.14%** | **+51.76%** | **+19.01%** | **+20.00%** | +0.0022 (tie) | +0.0032 (tie) | +52.48% | +53.39% | +49.46% | equal |
| b014 | P | `gemmL2x1x17` fp32 | 16.22 W | -4.43% | -4.43% | -1.65% | -2.49% | +0.0047 (tie) | +0.0049 (tie) | -4.88% | -5.06% | -5.40% | equal |
| b015 | C | `gemmL2x15x2` fp32 | 20.36 W | -3.61% | -3.80% | -1.54% | -4.07% | +0.0065 (tie) | +0.0056 (tie) | -4.23% | -3.40% | +0.08% | equal |
| b016 | C | `gemmL3x15x2` fp32 | 20.19 W | -4.14% | -4.29% | -1.77% | -4.10% | +0.0065 (tie) | +0.0056 (tie) | -4.76% | -3.93% | -0.49% | equal |
| b017 | C | `gemmL10x15x2` fp32 | 20.31 W | -3.64% | -3.80% | -1.56% | -3.95% | +0.0065 (tie) | +0.0056 (tie) | -4.26% | -3.43% | +0.04% | equal |
| b018 | C | `gemmL2x14x2` int8 | 10.35 W | -2.59% | -3.01% | -0.71% | -3.61% | +0.0115 (v3.1) | +0.0103 (v3.1) | -3.71% | -2.33% | -0.03% | equal |
| b019 | C | `gemmL16x14x1` fp32 | 19.45 W | -1.77% | -1.02% | -0.73% | +5.79% | +0.0141 (v3.1) | +0.0140 (v3.1) | -3.14% | -1.55% | +6.82% | equal |
| b020 | C | `gemmL9x1x1` int8 | 8.41 W | -5.40% | -4.35% | -1.29% | +4.52% | +0.0093 (tie) | +0.0071 (tie) | -6.27% | -5.12% | +6.37% | equal |
| b021 | R | `gemmL2x1x7` fp32 | 17.19 W | +2.68% | +3.77% | +1.00% | +9.24% | -0.0042 (tie) | -0.0028 (tie) | +2.25% | +2.62% | +3.78% | equal |
| b022 | R | `gemmL2x1x7` int8 | 8.90 W | +6.48% | +8.82% | +1.47% | **+12.78%** | -0.0058 (tie) | -0.0032 (tie) | +5.86% | +6.35% | +3.96% | equal |
| b023 | R | `gemmL1x1x41` fp32 | 14.88 W | -4.90% | -4.40% | -1.74% | +1.64% | -0.0023 (tie) | -0.0034 (tie) | -4.69% | -4.03% | -6.39% | equal |
| b024 | R | `gemmL3x2x9` int8 | 9.22 W | +1.15% | +1.60% | +0.28% | +2.14% | -0.0082 (tie) | -0.0082 (tie) | +0.33% | +0.76% | -3.16% | equal |
| b025 | R | `gemmL4x1x10` int8 | 8.55 W | +0.85% | +1.42% | +0.20% | +2.48% | -0.0082 (tie) | -0.0085 (tie) | +0.02% | -0.08% | -3.45% | equal |
| b026 | R | `gemmL2x1x15` fp32 | 16.20 W | -3.73% | -3.63% | -1.39% | -1.38% | +0.0052 (tie) | +0.0054 (tie) | -4.23% | -4.46% | -4.54% | equal |

**The post hoc (families L, S; reported apart) group** (12 points):

| point | family | case | W over idle | E1 | E2 | E3 | E4 | H4 d (closer) | H5 d (closer) | MM1-v3 E1 (REPORTED) | v3.1 with T7 E1 (REPORTED) | MM1-v2 E1 (REPORTED) | verify-e215d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| b001 | L | `gemmL1x15x4` fp32 at 0xf0ffffff | 18.20 W | -4.04% | -4.71% | -1.63% | -8.49% | +0.0033 (tie) | +0.0024 (tie) | -4.36% | -3.69% | -1.31% | equal |
| b002 | L | `gemmL1x15x4` fp32 at 0xff0fffff | 18.13 W | -4.50% | -5.17% | -1.82% | -8.69% | +0.0033 (tie) | +0.0024 (tie) | -4.81% | -4.15% | -1.77% | equal |
| b003 | L | `gemmL1x15x4` fp32 at 0xfff0ffff | 18.16 W | -4.65% | -5.34% | -1.87% | -8.96% | +0.0033 (tie) | +0.0024 (tie) | -4.96% | -4.29% | -1.91% | equal |
| b004 | L | `gemmL1x15x4` fp32 at 0xffff0fff | 18.09 W | -4.57% | -5.24% | -1.85% | -8.65% | +0.0033 (tie) | +0.0024 (tie) | -4.89% | -4.22% | -1.86% | equal |
| b005 | L | `gemmL2x1x16` fp32 at 0xcc000 | 0.62 W (watts point) | 0.205 W | 0.206 W | -0.70% | -0.38% | -0.067 W (tie) | -0.067 W (tie) | 0.138 W | 0.127 W | 0.127 W | equal |
| b006 | L | `gemmL3x5x7` fp32 at 0x60000006 | 2.71 W (watts point) | 0.472 W | 0.107 W | -1.51% | **-13.64%** | -0.060 W (tie) | -0.032 W (tie) | 0.413 W | 0.373 W | 0.304 W | equal |
| b007 | L | `gemmL8x4x4` fp32 at 0x50005500 | 4.16 W | -13.12% | **-14.59%** | -1.91% | **-14.13%** | -0.0068 (tie) | -0.0077 (tie) | -12.52% | -12.65% | -8.19% | equal |
| b008 | L | `gemmL1x1x16` fp32 at 0xee000e | 5.61 W | +6.53% | +6.46% | +1.02% | -0.09% | +0.0059 (tie) | +0.0060 (tie) | +7.16% | +10.80% | +8.40% | equal |
| b027 | S | `gemmL3x1x3` fp32, designed:blind3 a_colconst_b_randn | 21.89 W | -5.30% | -5.16% | -2.39% | -1.82% | - | - | - | -5.70% | - | equal |
| b028 | S | `gemmL3x1x3` fp32, e37 | 14.46 W | +5.69% | +5.89% | +1.85% | +2.55% | - | - | - | +5.03% | - | equal |
| b029 | S | `gemmL3x1x3` fp32, real:blind4 | 18.34 W | +0.07% | +0.25% | +0.03% | +0.67% | - | - | - | -0.41% | - | equal |
| b030 | S | `gemmL3x1x3` int8, real:blind4 | 9.91 W | -8.36% | -7.97% | -2.32% | -0.38% | - | - | - | -9.13% | - | equal |

## 6. REPORTED beside the verdicts (never verdicts)

E215.md 7: "REPORTED beside, never verdicts: MM1-v2's, MM1-v3's and 'v3.1 with T7''s cells at MM1-v3.1's bands; the rms and bias of ln(measured / forecast) of all four models by family; every flag." Beside every head-to-head, "and the same sign test, cases and ties for MM1-v3.1 against MM1-v2 and for 'v3.1 with T7' against MM1-v3.1 (the walk's layout term at never-run layouts; at family L's points the two time forms differ by up to 28% in the wall cycles)."

**'v3.1 with T7' against MM1-v3.1** (the same sign test, cases and ties; T7 / MM1-v3.1 / ties; the scorer's REPORTED pair, equal to verify-e215d's and to this lane's copy of the scorer's pair loop):

| registered (families P, C, R) | over | T7 closer | MM1-v3.1 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 18 | 7 | 8 | 3 | 1 | NOT DECIDED |
| H2 | 18 | 7 | 7 | 4 | 1 | NOT DECIDED |
| H3 | 18 | 7 | 8 | 3 | 1 | NOT DECIDED |
| H4 | 18 | 0 | 0 | 18 | - | TOO FEW |
| H5 | 18 | 1 | 0 | 17 | - | TOO FEW |

| post hoc (families L, S; reported apart) | over | T7 closer | MM1-v3.1 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 8 | 5 | 3 | 0 | - | TOO FEW |
| H2 | 8 | 6 | 2 | 0 | - | TOO FEW |
| H3 | 8 | 5 | 3 | 0 | - | TOO FEW |
| H4 | 12 | 0 | 1 | 11 | - | TOO FEW |
| H5 | 12 | 0 | 4 | 8 | - | TOO FEW |

**MM1-v3.1 against MM1-v2** (the same test; MM1-v3.1 / MM1-v2 / ties):

| registered (families P, C, R) | over | MM1-v3.1 closer | MM1-v2 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 18 | 10 | 8 | 0 | 0.815 | NOT DECIDED |
| H2 | 18 | 10 | 8 | 0 | 0.815 | NOT DECIDED |
| H3 | 18 | 10 | 8 | 0 | 0.815 | NOT DECIDED |
| H4 | 18 | 6 | 9 | 3 | 0.607 | NOT DECIDED |
| H5 | 18 | 8 | 9 | 1 | 1 | NOT DECIDED |

| post hoc (families L, S; reported apart) | over | MM1-v3.1 closer | MM1-v2 closer | ties | p | the scorer's reading |
|---|---|---|---|---|---|---|
| H1 | 8 | 2 | 6 | 0 | - | TOO FEW |
| H2 | 8 | 1 | 7 | 0 | - | TOO FEW |
| H3 | 8 | 2 | 6 | 0 | - | TOO FEW |
| H4 | 8 | 1 | 6 | 1 | - | TOO FEW |
| H5 | 8 | 1 | 5 | 2 | - | TOO FEW |

**Every model's cells at MM1-v3.1's bands** (the scorer's REPORTED counts for T1-T3, E1 and E2; E3 and E4 for the other models are desk arithmetic, section 7's clause on them):

| registered (families P, C, R) | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.1 (the registered model) | FAIL 15/18 | PASS 18/18 | FAIL 15/18 | PASS 17/18 | PASS 17/18 | PASS 17/18 | FAIL 16/18 |
| MM1-v3 | FAIL 15/18 | PASS 18/18 | FAIL 15/18 | PASS 17/18 | PASS 17/18 | PASS 17/18 (desk; the scorer: NO DATA, n 0) | FAIL 16/18 (desk; the scorer: NO DATA, n 0) |
| v3.1 with T7 | FAIL 15/18 | PASS 18/18 | FAIL 15/18 | PASS 17/18 | PASS 17/18 | PASS 17/18 (desk; the scorer: NO DATA, n 0) | FAIL 15/18 (desk; the scorer: NO DATA, n 0) |
| MM1-v2 | FAIL 15/18 | FAIL 15/18 | FAIL 15/18 | PASS 17/18 | PASS 17/18 | PASS 17/18 (desk; the scorer: NO DATA, n 0) | FAIL 14/18 (desk; the scorer: NO DATA, n 0) |

| post hoc (families L, S; reported apart) | T1 | T2 | T3 | E1 | E2 | E3 | E4 |
|---|---|---|---|---|---|---|---|
| MM1-v3.1 (the registered model) | TOO FEW 2/8 | TOO FEW 6/8 | TOO FEW 2/8 | PASS 12/12 | PASS 11/12 | PASS 12/12 | FAIL 10/12 |
| MM1-v3 | TOO FEW 6/8 | TOO FEW 6/8 | TOO FEW 6/8 | TOO FEW 8/8 | TOO FEW 8/8 | TOO FEW 8/8 (desk; the scorer: NO DATA, n 0) | TOO FEW 6/8 (desk; the scorer: NO DATA, n 0) |
| v3.1 with T7 | TOO FEW 4/8 | TOO FEW 6/8 | TOO FEW 4/8 | PASS 12/12 | FAIL 10/12 | PASS 12/12 (desk; the scorer: NO DATA, n 0) | FAIL 9/12 (desk; the scorer: NO DATA, n 0) |
| MM1-v2 | TOO FEW 7/8 | TOO FEW 7/8 | TOO FEW 7/8 | TOO FEW 8/8 | TOO FEW 8/8 | TOO FEW 8/8 (desk; the scorer: NO DATA, n 0) | TOO FEW 7/8 (desk; the scorer: NO DATA, n 0) |

**rms of the relative error, measured / forecast - 1** (desk arithmetic on the scorer's measured values and the frozen forecasts; equal to verify-e215d's in every figure; time per case, energy per point; J over idle at points of 3 W and more, the watts points' W error apart):

| registered (families P, C, R) | wall cycles (cases) | counter's mean | seconds | J over idle given t (points) | J over idle, t forecast | J at rest given t (points) | J at rest, t forecast | W at the watts points, given t |
|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 6.67% (18) | 5.38% | 6.68% | 12.80% (18) | 12.81% | 4.66% (18) | 7.03% | - |
| MM1-v3 | 6.61% (18) | 5.10% | 6.63% | 12.97% (18) | 12.98% | 4.72% (18) | 7.11% | - |
| v3.1 with T7 | 7.04% (18) | 5.42% | 7.07% | 13.05% (18) | 13.09% | 4.72% (18) | 7.36% | - |
| MM1-v2 | 9.69% (18) | 7.82% | 9.71% | 12.22% (18) | 12.75% | 4.47% (18) | 9.18% | - |

Without the gemmLnc points (a post hoc reading; J over idle given t (n), with t forecast, J at rest given t, with t forecast): MM1-v3.1 3.68% (17), 4.01%, 1.30%, 5.37%; MM1-v3 4.00% (17), 4.23%, 1.44%, 5.28%; v3.1 with T7 3.57% (17), 3.89%, 1.26%, 5.56%; MM1-v2 3.77% (17), 5.16%, 1.26%, 7.96%.

| post hoc (families L, S; reported apart) | wall cycles (cases) | counter's mean | seconds | J over idle given t (points) | J over idle, t forecast | J at rest given t (points) | J at rest, t forecast | W at the watts points, given t |
|---|---|---|---|---|---|---|---|---|
| MM1-v3.1 | 10.39% (8) | 12.73% | 10.31% | 6.51% (10) | 6.96% | 1.70% (12) | 7.63% | 0.36 W (2) |
| MM1-v3 | 9.58% (8) | 12.08% | 9.50% | 7.06% (6) | 7.73% | 1.63% (8) | 8.76% | 0.31 W (2) |
| v3.1 with T7 | 21.55% (8) | 17.93% | 21.57% | 6.96% (10) | 8.26% | 1.69% (12) | 16.29% | 0.28 W (2) |
| MM1-v2 | 5.63% (8) | 7.83% | 5.60% | 4.99% (6) | 5.72% | 0.87% (8) | 5.62% | 0.23 W (2) |

**By family** (the scorer's REPORTED rms / bias of ln(measured / forecast), in percent: the wall cycles per point, J over idle at points of 3 W and more, and the watts points' W in watts):

| family | model | wall cycles: rms / bias (n) | J over idle: rms / bias (n) | watts points: rms / bias (n) |
|---|---|---|---|---|
| C | MM1-v3.1 | 6.18% / +0.09% (6) | 3.64% / -3.44% (6) | - |
| C | MM1-v3 | 5.75% / +1.07% (6) | 4.34% / -4.25% (6) | - |
| C | v3.1 with T7 | 6.08% / +1.58% (6) | 3.29% / -3.08% (6) | - |
| C | MM1-v2 | 7.13% / +2.60% (6) | 5.00% / +2.72% (6) | - |
| L | MM1-v3.1 | 11.08% / -9.66% (8) | 8.15% / -5.09% (6) | 0.164 W / -0.157 W (2) |
| L | MM1-v3 | 10.19% / -8.79% (8) | 8.09% / -5.01% (6) | 0.112 W / -0.107 W (2) |
| L | v3.1 with T7 | 19.86% / -0.87% (8) | 9.70% / -3.69% (6) | 0.281 W / -0.278 W (2) |
| L | MM1-v2 | 5.81% / -2.00% (8) | 5.76% / -1.45% (6) | 0.139 W / -0.139 W (2) |
| P | MM1-v3.1 | 5.42% / -4.22% (6) | 17.37% / +3.90% (6) | - |
| P | MM1-v3 | 4.04% / -2.91% (6) | 17.55% / +3.72% (6) | - |
| P | v3.1 with T7 | 3.86% / -2.77% (6) | 17.72% / +4.12% (6) | - |
| P | MM1-v2 | 5.02% / -3.66% (6) | 16.75% / +4.93% (6) | - |
| R | MM1-v3.1 | 7.64% / +5.77% (6) | 4.54% / +1.16% (6) | - |
| R | MM1-v3 | 8.37% / +6.23% (6) | 4.36% / +0.74% (6) | - |
| R | v3.1 with T7 | 9.03% / +6.58% (6) | 4.54% / +1.02% (6) | - |
| R | MM1-v2 | 12.84% / +7.09% (6) | 6.17% / -0.16% (6) | - |
| S | MM1-v3.1 | - | 5.70% / -1.91% (4) | - |
| S | MM1-v3 | - | - | - |
| S | v3.1 with T7 | - | 6.01% / -2.69% (4) | - |
| S | MM1-v2 | - | - | - |

**The readings** (registered before the data; the scorer's `readings_REPORTED`):

- **(a) The census path:** none in this arm (no family P shape holds two loops here).
- **(b) The layout** (gemmL1x15x4 fp32 random, 28 shires, points b001, b002, b003, b004): the measured spread of the wall cycles 0.47% (max over min, less 1); MM1-v3.1's forecast spread 0.00%, 'v3.1 with T7''s 0.00%.
- **(c) The switch route** (each family-S kind's W over idle over its random partner's, measured, beside MM1-v3.1's ratio and 'v3.1 with T7''s; MM1-v3 and MM1-v2 price none of these kinds): b027, designed:blind3 a_colconst_b_randn / random (fp32, gemmL3x1x3): measured 0.8823, MM1-v3.1 0.9476, T7 0.9478; b028, e37 / random (fp32, gemmL3x1x3): measured 0.5828, MM1-v3.1 0.5606, T7 0.5625; b029, real:blind4 / random (fp32, gemmL3x1x3): measured 0.7391, MM1-v3.1 0.7511, T7 0.7521; b030, real:blind4 / random (int8, gemmL3x1x3): measured 0.8857, MM1-v3.1 0.9712, T7 0.9715.
- **(e) The timing simulation against reality** (his question): each point's measured cycles a GEMM over the simulator's step count (MM1-v3's column: one step an instruction, not time) reads 19.35 to 34.97 over 27 points and references; the counter's mean over the tensor unit's floor (529 cycles an op for fp32 and fp16, 270 for int8, measured) reads 1.573 to 5.268 over 32. Every point's pair of figures is in the JSON (`readings_REPORTED` > `timing_simulation`).
- **(f) The ties and the day offset:** 3 tie runs (gemmL4x8x8 int8 random, the full chip, aifoundry1 card 1) read W over idle 9.077 W against the committed reference's 9.503 W: offset_W -4.49%, the seconds -0.065%. H4n and H5n (H4 and H5 re-read with every measured J divided by 1 + offset_W): posthoc:H4n TOO FEW (0/0/8); posthoc:H5n TOO FEW (0/0/8); registered:H4n TOO FEW (0/2/16); registered:H5n TOO FEW (0/2/16).
- **Flags:** none (no run set aside, no family dropped, no label).
- **(d) The card transfer** (the configurations both arms run) needs both arms in one data file: this one-arm file holds none; dated note 3 of arm B's directory gives it from the pooled run.

## 7. Dated clauses (Thu 19 Nov 2026), answering the card lane's, the verifier's and the fix lane's findings

1. **b013, the arm's one gemmLnc point, is the only registered E1-E3 miss** (card-e215b's finding): its J over idle given the seconds came out +52.14% against MM1-v3.1 (band 14%), so E1, E2 and E3 PASS 17/18, at the 90% rule's minimum of 17 (no slack). E4 misses b013 (+20.00%) and b022 (+12.78%), b022 being gemmL2x1x7 int8. The registered T1 and T3 misses are `gemmL16x14x1` fp32 (b019), `gemmL2x1x7` fp32 (b021), `gemmL2x1x7` int8 (b022) (section 4). No datum, rule or verdict changes.
2. **Step 6n's 26 'ran after' readings, and the arm A line of this directory's never-run report** (card-e215b's finding; verify-e215d's finding 3): dated note 1 of this directory (`2b0c8814`, fix-e215d) says what both read: E217's registration desk, copied into the round's data lane for E217 (its never-run index's PLANNED rows; its copy of the cards' power record), dated after arm A's data commit. This arm's step 6n stands as printed (4 of 30, the 26 'ran after' readings REPORTED and kept), its labels are empty, and the scorer's input is unchanged. The scanner's fix for later kits is E215's dated note 2 (`tools/claims-v3/e215-notes/`, the same commit).
3. **fwgate's one firmware read came before step 6n** (verify-e215d's finding 4, info): the read at 13:41:24 PST (step 4) preceded step 6n (13:41:38) by 14 s. That is the order arm B's Amendment A2 form registers (the README says so), and the read runs no point.
4. **The day's first booking sent nothing** (card-e215b's first-booking record): booked at 12:00:51 PST, it was refused at step 4 by the kit's rest rule at 12:34:27 and 13:12:51 before any card command, because the model session's E217 preflight had written in its own folder on aifoundry1; it ended at 13:14:28. The second booking (G 13:21:36) ran every step; its RB_OUT is the one committed here.
5. **The other models' E3 and E4 at MM1-v3.1's bands** (verify-e215d's finding 2; fix-e215d's clause): the frozen scorer's REPORTED cells for the other models hold T1-T3, E1 and E2 only; its E3 and E4 for MM1-v3, MM1-v2 and 'v3.1 with T7' read NO DATA (n 0) in both arms because it does not compute them. Desk arithmetic (REPORTED, not verdicts; the scorer's own given() and its inclusion rule for the other models; equal in every cell to verify-e215d's and fix-e215d's counts): registered MM1-v3 E3 17/18, E4 16/18, MM1-v2 E3 17/18, E4 14/18, v3.1 with T7 E3 17/18, E4 15/18; post hoc MM1-v3 E3 8/8, E4 6/8, MM1-v2 E3 8/8, E4 7/8, v3.1 with T7 E3 12/12, E4 9/12. No verdict changes.
6. **The model session's sealed forecast** of E215's points (registered as a freeze line of both arms in `18398ed2`, 11:43:33 PST, before either arm's first card command) is the model session's to score: the lab neither read nor scored it, and nothing of it is in this note.

## 8. NOT RUN

- An independent re-derivation of the bands' bases B1 and B2 from MM1-v3.1's fold records (verify-e215d re-derived the bands from the registered bases only).
- Independent code for the REPORTED bootstrap intervals, the family check, H4n and H5n and the readings: they are the frozen scorer's own figures, reproduced byte for byte by its re-runs, not re-derived by other code.
- Any score of the frozen terms posted before the data (the gemmLnc term and the layout term, landed in `aaeaa495` and `595fcb59`): not this note's; nothing of them is read here.
- Any read of a box's disk.

## What this note changes

Nothing committed. It adds the frozen scorer's two output files, byte for byte as step 13 wrote them, this note and its hash list. Every verdict above is the scorer's as printed at 14:14:52 PST; the registered group's are E215 arm B's registered verdicts, and the post hoc group's stay reported apart.
