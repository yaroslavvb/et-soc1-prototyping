# E213 arm A data, dated note 2: the frozen scorer's output, committed beside the data byte for byte - R0, S6, T1-T3 and E1-E3 PASS, E4 FAIL by one point (78 of 87, 79 needed), and MM1-v3 BETTER than MM1-v2 on all five head-to-head rules, with verify-e213d's re-derivation beside each result

*Wed 18 Nov 2026 (week 47), PST; written at about 08:46 PST by Q216's lane `scores-e213`, after this directory's data commit `c69a12aa` (committed 07:23:29 PST, pushed by 07:23:33), after the day's data verifier `verify-e213d` (HOLDS WITH FIXES: this directory's data re-derive exactly from the raw records, and its own scoring equals the frozen scorer's on every verdict, count, p value and cell) and after dated note 1 (`2812fd87`). It adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. Labels: **registered** (E213.md with its Amendment A1, the kit), **measured** (this directory's committed records), **blind** (MM1-v3's and MM1-v2's arm A forecasts, frozen in MM1-v3's land `b1493082`, pushed 20:52:46 PST Tue 17 Nov 2026, before any E213 datum), **REPORTED** (never a verdict), **post hoc** (read after the data), **desk** (a check of code at the desk, under `/usr/bin/python3` 3.12.3).*

**The words.** The frozen scorer (`score_e213.py`, registered sha256 `a4eece29...`), run by the kit's step 13 at 07:23:40-41 PST on this directory's committed `data-e213.json` with step 6n's committed `labels-e213.json` (no point and no case labelled 'ran before'), printed for arm A: **R0 PASS**; **S6 PASS**; **T1 PASS** 81/84, **T2 PASS** 82/84, **T3 PASS** 81/84 (cycles and seconds per case); **E1 PASS** 82/87, **E2 PASS** 82/87, **E3 PASS** 81/87, **E4 FAIL** 78/87 (joules per point; E4 is one point short of the 79 its 90% rule needs); **H1-H5: MM1-v3 BETTER** than MM1-v2 (the sign test, MM1-v3 / MM1-v2 / ties: H1 65/6/13, H2 62/15/7, H3 65/6/13, H4 50/9/28, H5 45/11/31). Arm B: NO DATA on every rule (it stopped before any card command and has no data); the pooled HP1-HP5: NO DATA. With R0 and S6 PASS, no verdict of arm A carries a label: these are arm A's registered verdicts.

**MM1-v3 against MM1-v2, rms of the relative error** (desk arithmetic on this directory's measured values and the frozen forecasts, equal to verify-e213d's; REPORTED; blind): the wall cycles 4.61% against 9.79% (84 cases), the counter's mean 6.20% against 10.03%, seconds 4.66% against 9.86%; J over idle given the seconds 14.11% against 14.73% (65 points at 3 W and above; 3.92% against 7.15% without the five gemmLnc points, post hoc), with the seconds forecast 14.14% against 14.86%; W over idle at the 22 watts points 0.294 W against 0.362 W given the seconds; J with the card at rest given the seconds 5.29% against 5.48% (87 points), with the seconds forecast 6.60% against 10.58%.

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e213-A.json` | 178,989 | `6d894c0307e14bbf3c86fc355ea35855950d11a27c2ea67a2f66b56164bb39e7` | the frozen scorer's output (`score_e213.py`, registered sha256 `a4eece29...`): every verdict, count, cell, measured point, head-to-head count and REPORTED reading of arm A; arm B and the pooled rules NO DATA |
| `scores-e213-A.txt` | 1,172 | `f852f477ed710e0e1adb1e84812930ecfd35893263fe7f069ffa7e8c7bcdc662` | its printed lines (step 13's capture of the call) |
| `README.md.dated-note-2.md` | (this note) | listed in `SHA256SUMS-note2` | this dated note |
| `SHA256SUMS-note2` | 4 lines | (not listed in itself) | the three files above and `SHA256SUMS-note1` |

The two output files are card-e213a's RB_OUT files byte for byte. With `SHA256SUMS` (576 entries), `SHA256SUMS-note1` (6: note 1's four files, `README.md` and `SHA256SUMS`) and `SHA256SUMS-note2` (4), every file of this directory is in a list except `SHA256SUMS-note2` itself.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e213.sh A`) is the runbook log's last six lines (lines 100-105 of 105): 07:23:40 PST (calls 1-5) and 07:23:41 PST (call 6), each rc 0, the six captures under one process id. Call 1 printed the data commit `c69a12aa9` and its subject; call 2 (the directory clean) printed nothing; call 3 read all 576 `SHA256SUMS` entries OK, in the list's order; call 4 printed `HISTORY OK` naming the registration `291c8201ae4b`; call 5 printed `LABELS-OK`; call 6 ran `/usr/bin/python3 -I -B tools/claims-v3/e213/score_e213.py docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json --labels docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/labels-e213.json --out <the card lane's RB_OUT>/scores-e213-A.json` (0.9 s). The log holds no earlier run of the scorer on data: only its two self-tests and its forecasts print, in the runbook's desk step (`s03_desk_e213`, 06:35:52 PST, rc 0).
- **The bytes.** `scores-e213-A.txt` is the runbook's capture of call 6 byte for byte (the step's copy of it), and it rebuilds exactly from the JSON through the scorer's own print function (`text()`, read from `score_e213.py` at the data commit). The JSON is in the scorer's own dump form (indent 1, sorted keys, no trailing newline) and was last written inside call 6 (07:23:41.722 PST, 1 ms before the call's capture closed); the text file was copied after it (07:23:41.733).
- **The commit before it.** The data commit `c69a12aa` was made at 07:23:29 PST and pushed by 07:23:33; at 07:23:33 the card lane left its collect span, removed its hold line and released aifoundry3; step 13 ran at 07:23:40-41. The lab clone's HEAD during the step was the data commit itself (its reflog: `c69a12aa` from 07:23:29 until 07:23:48), and its status read 0 lines before and after the step (the card lane's record). The next two commits, MM1-v3.1's declaration `7375bc9c` (07:23:48) and its switch counts `3e8991d0` (07:23:56), came after the scorer's call and add files under `tools/matmul/mm1/v3.1/` only.
- **The frozen files.** The registration list's 27 files and the list itself have one blob each at `291c8201` (the registration), `6efdb002` (the kit), `8e91dda6` (the first seal's registration), `c69a12aa` and `f658861c` (LAB's HEAD at this note's checks); the kit list's 49 files and the list from `6efdb002` on; the 17 frozen files of E213.md section 0 (MM1-v3's and MM1-v2's) from `b1493082` on, each at its listed sha256 (MM1-v2's three as landed in `3ca4b717`). The scorer at the data commit is `a4eece29...` (the registration list's line), and its nine pins equal those files' sha256 at the data commit. None of the 12 committed files the scorer opens changed from the data commit to `f658861c`; what changed since: this directory's note 1, `tools/claims-v3/sealed-e213/e213-freeze-lines-2-correction-1.md`, `tools/claims-v3/sealed-e213/e213-freeze-lines-2.md` and `tools/matmul/mm1/v3.1/`.
- **The re-runs.** (1) In a tree of exactly the 12 committed files the scorer opens (its own file, its nine pinned inputs, `data-e213.json` and `labels-e213.json`), taken from the data commit's objects, with no bytecode cache, a plain run and a run under an audit hook that lists every file opened, each with step 13's arguments, wrote both outputs byte for byte equal to RB_OUT and to the capture of call 6 (08:33 PST); the audited run opened those 12 files, 33 standard-library files and nothing else but its own outputs. (2) The scorer imported unchanged from that tree and called in process (`score(data, labels, quiet=True)`) gives a result whose dump equals RB_OUT's JSON byte for byte; its own functions (`reduce_arm`, `score_arm`, `decide`, `family_check`), called as `score()` calls them, give every case's and point's d value (the JSON keeps only the counts), with the JSON's counts, p values, family checks and cells. Sections 4 and 5 print those d values.
- **The bytes named before.** card-e213a, verify-e213d and fix-e213d each named `scores-e213-A.json` by `6d894c03...`; card-e213a named the text file `f852f477...`: both equal.

## 3. The rules: their registered words, the verdicts, verify-e213d beside

The scorer's printed lines (`scores-e213-A.txt`, verbatim):

```
E213 scorer (score_e213.py), the registered verdicts:
ARM A: R0 PASS; S6 PASS; T1 PASS 81/84; T2 PASS 82/84; T3 PASS 81/84; E1 PASS 82/87; E2 PASS 82/87; E3 PASS 81/87; E4 FAIL 78/87
  H1 MM1-v3 BETTER (v3 65 / v2 6 / ties 13; p 1.3321308760808536e-13); REPORTED bootstrap MM1-v3 BETTER [0.03143757864188094, 0.04940573454148727]
  H2 MM1-v3 BETTER (v3 62 / v2 15 / ties 7; p 6.083249930070788e-08); REPORTED bootstrap MM1-v3 BETTER [0.020689999233477266, 0.04104450826532456]
  H3 MM1-v3 BETTER (v3 65 / v2 6 / ties 13; p 1.3321308760808536e-13); REPORTED bootstrap MM1-v3 BETTER [0.031172052990476016, 0.04896998061010384]
  H4 MM1-v3 BETTER (v3 50 / v2 9 / ties 28; p 5.264832102225281e-08); REPORTED bootstrap MM1-v3 BETTER [0.010385878829239192, 0.027159088207662253]
  H5 MM1-v3 BETTER (v3 45 / v2 11 / ties 31; p 5.37831811014966e-06); REPORTED bootstrap MM1-v3 BETTER [0.011506328620352026, 0.029922849268087835]
ARM B: R0 NO DATA; S6 NO DATA; T1 NO DATA; T2 NO DATA; T3 NO DATA; E1 NO DATA; E2 NO DATA; E3 NO DATA; E4 NO DATA
  H1 NO DATA
  H2 NO DATA
  H3 NO DATA
  H4 NO DATA
  H5 NO DATA
POOLED: HP1 NO DATA; HP2 NO DATA; HP3 NO DATA; HP4 NO DATA; HP5 NO DATA
```

**MM1-v3's rules, per arm** (E213.md 7, its words): "Each case or point passes when |measured / MM1-v3 - 1| is within its band; a rule's verdict: PASS if at least 90% of its scored cases or points pass, FAIL otherwise, TOO FEW under 10, NO DATA with none." "The band is twice the larger of two held-out errors of MM1-v3 for that quantity, rounded up to a whole percent:" B1, "leave one experiment out over every point without configuration twins", and B2, "the same over this arm's card's points". "The points under about 3 W over idle are scored in absolute watts in E1 and E2 (a point whose MM1-v3 frozen W over idle is under 3 W, or whose measured W over idle is; E3 and E4 stay relative, the card at rest dominating them)": "arm A 0.60 W = 2 x max(0.2969, 0.2933, SD_rep 0.12114) = 0.594 -> 0.60 W". The scorer's 90% rule passes a rule when the passing cases or points number at least ceil(0.9 n).

| rule | the registered words (E213.md 7, arm A) | band | scored | needed (90%) | the scorer (registered verdict) | verify-e213d's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good (walk_launches_bad 0, walk_ok on every launch) and its identity gate GATE OK. A FAIL of either labels every other verdict of its arm. | - | 109 checks of C (4 smoke processes, 102 point and reference runs, 3 tie runs); the four smoke counter means; 18 rgm211-host processes (s02-s04 and 15 point runs) | all | **PASS** (0 failures; the smoke s01-s04 at 819.274, 754.505, 755.0335, 788.551 cycles an op; every rgm211-host walk good and gate GATE OK; s04, Amendment A1's family smoke, passed, so A1's clause 2 had nothing to read) | PASS | - | none |
| **S6** | every kept run's counted samples at 590-610 MHz | 590-610 MHz | the 102 kept runs of the 90 points | all | **PASS** (0 failures) | PASS | - | none |
| **T1** | cycles an op, the wall, per case; 2 x max(5.038, 3.999) = 10.08 -> 11% | 11% | 84 | 76 | **PASS** (81/84) | PASS (81/84; the same cells, worst difference 0) | 5 | gemmL1x3x12 fp32 0x1010101 (+12.70%); gemmL1x3x12 fp32 0x11 (+11.86%); gemmL2x8x8 fp32 0x3 (+11.57%) |
| **T2** | cycles an op, the counter's mean, per case; 2 x max(6.029, 4.185) = 12.06 -> 13% | 13% | 84 | 76 | **PASS** (82/84) | PASS (82/84; the same cells, worst difference 0) | 6 | gemmL2x8x8 fp32 0xf0000 (+29.46%); gemmL2x8x8 fp32 0xf0f (+14.65%) |
| **T3** | seconds a GEMM, per case (T1's bases); 2 x max(5.038, 3.999) = 10.08 -> 11% | 11% | 84 | 76 | **PASS** (81/84) | PASS (81/84; the same cells, worst difference 0) | 5 | gemmL1x3x12 fp32 0x1010101 (+12.82%); gemmL1x3x12 fp32 0x11 (+11.96%); gemmL2x8x8 fp32 0x3 (+11.67%) |
| **E1** | J over idle given the measured seconds, per point (watts under 3 W); 2 x max(4.938, 5.375) = 10.75 -> 11% | 11% (0.60 W at the 22 watts points) | 87 | 79 | **PASS** (82/87) | PASS (82/87; the same cells, worst difference 0) | 3 | a075 (+59.28%); a079 (+15.37%); a082 (+37.85%); a086 (+47.02%); a087 (+67.98%) |
| **E2** | J over idle with the seconds forecast, per point (watts under 3 W); 2 x max(5.705, 5.620) = 11.41 -> 12% | 12% (0.60 W at the 22 watts points) | 87 | 79 | **PASS** (82/87) | PASS (82/87; the same cells, worst difference 0) | 3 | a075 (+59.38%); a079 (+14.98%); a082 (+37.86%); a086 (+48.29%); a087 (+67.93%) |
| **E3** | J with the card at rest given the measured seconds and rest, per point; 2 x max(1.711, 1.770) = 3.54 -> 4% | 4% | 87 | 79 | **PASS** (81/87) | PASS (81/87; the same cells, worst difference 0) | 2 | a073 (+4.05%); a075 (+30.16%); a079 (+7.52%); a082 (+15.71%); a086 (+18.27%); a087 (+26.98%) |
| **E4** | J with the card at rest with the seconds forecast, per point; 2 x max(4.687, 3.774) = 9.37 -> 10% | 10% | 87 | 79 | **FAIL** (78/87) | FAIL (78/87; the same cells, worst difference 0) | -1 | a050 (+12.30%); a053 (+10.15%); a054 (+10.83%); a063 (+11.68%); a064 (+13.70%); a075 (+30.17%); a082 (+14.91%); a086 (+25.47%); a087 (+25.13%) |

The slack is the passing count less the count the 90% rule needs (REPORTED, desk arithmetic). E4 fails with a slack of -1: section 7, clause 2. The time misses are family M's subset-mask cases (clause 4); the E1 and E2 misses are exactly the five gemmLnc points (clause 3).

**THE HEAD-TO-HEAD RULES** (E213.md 7, its words): "per case (cycles, seconds) or per point (joules), d = |ln(measured / MM1-v2)| - |ln(measured / MM1-v3)| (at a watts point, |W - W_v2| - |W - W_v3| in watts); MM1-v3 is closer where d > the tie, MM1-v2 where d < -the tie, a tie otherwise." The ties: "arm A 0.005 in ln for cycles and 0.005 for seconds, 0.01 for joules, 0.05 W at a watts point". "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v3 BETTER if p < 0.05 and it is closer in more cases than not; MM1-v2 BETTER if p < 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none."

| rule | the registered words (E213.md 7) | over | MM1-v3 closer | MM1-v2 closer | ties | p (exact, two-sided) | the scorer | verify-e213d | where MM1-v2 is closer |
|---|---|---|---|---|---|---|---|---|---|
| **H1** | cycles an op, the wall, per case | 84 cases | 65 | 6 | 13 | 1.332e-13 | **MM1-v3 BETTER** | MM1-v3 BETTER (65/6/13, the same p; every d equal, worst difference 0) | gemmL1x1x26 fp32; gemmL1x3x9 fp32; gemmL2x8x8 fp32 0x22222222; gemmL4x5x1 fp32; gemmL7x3x1 fp32; gemmL9x7x1 fp32 |
| **H2** | cycles an op, the counter's mean, per case | 84 cases | 62 | 15 | 7 | 6.083e-08 | **MM1-v3 BETTER** | MM1-v3 BETTER (62/15/7, the same p; every d equal, worst difference 0) | gemmL1x1x26 fp32; gemmL1x2x7 fp32; gemmL1x3x12 fp32 0x22222222; gemmL1x3x12 fp32 0x3030303; gemmL1x3x12 fp32 0x55555555; gemmL1x3x9 fp32; gemmL2x2x7 fp32; gemmL3x1x3 fp32; gemmL4x1x2 fp32; gemmL4x5x1 fp32; gemmL4x5x1 int8; gemmL7x3x1 fp32; gemmL7x3x1 int8; gemmL9x7x1 fp32; gemmL9x7x1 int8 |
| **H3** | seconds a GEMM, per case | 84 cases | 65 | 6 | 13 | 1.332e-13 | **MM1-v3 BETTER** | MM1-v3 BETTER (65/6/13, the same p; every d equal, worst difference 0) | gemmL1x1x26 fp32; gemmL1x3x9 fp32; gemmL2x8x8 fp32 0x22222222; gemmL4x5x1 fp32; gemmL7x3x1 fp32; gemmL9x7x1 fp32 |
| **H4** | J over idle given the measured seconds, per point both price | 87 points (22 in watts) | 50 | 9 | 28 | 5.265e-08 | **MM1-v3 BETTER** | MM1-v3 BETTER (50/9/28, the same p; every d equal, worst difference 0) | a001; a005; a011; a015; a033; a037; a055; a086; a087 |
| **H5** | J over idle with the seconds forecast, per point both price | 87 points (22 in watts) | 45 | 11 | 31 | 5.378e-06 | **MM1-v3 BETTER** | MM1-v3 BETTER (45/11/31, the same p; every d equal, worst difference 0) | a011; a015; a025; a031; a033; a035; a037; a055; a063; a086; a087 |

**HP1-HP5** (E213.md 7: "H1-H5 pooled over both arms, each case or point once with its own arm's tie; NO DATA unless both arms scored"): NO DATA in this file. Arm B has no data (section 7, clause 12).

## 4. Every case: cycles and seconds (T1-T3) and the head-to-head H1-H3, with verify-e213d beside

Errors are measured / MM1-v3 - 1 (the scorer's `err`; a miss in bold); d is the registered d (positive: MM1-v3 closer; the tie 0.005), from the frozen scorer's own functions (section 2); the closer is MM1-v3 (v3), MM1-v2 (v2) or a tie. A case is the mean of its points (the zeros points share their cases with random points: time is kind-blind in both models). The last column compares verify-e213d's own scoring (its `work/indep-scores-A-P.json`, code that imports nothing of the kit's) with the scorer's: its three cells and its three d values.

| case | family | points | T1 wall | T2 counter mean | T3 seconds | d H1 | H1 | d H2 | H2 | d H3 | H3 | verify-e213d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemmLnc1x1x1 int8 | A:P | a087 | -2.47% | -2.09% | -2.38% | +0.0631 | v3 | +0.0631 | v3 | +0.0631 | v3 | the same 3 cells and 3 d |
| gemmLnc1x1x44 fp32 | A:P | a086 | +9.39% | +10.10% | +9.70% | +0.0211 | v3 | +0.0211 | v3 | +0.0211 | v3 | the same 3 cells and 3 d |
| gemmLnc1x6x5 fp32 | A:P | a079 | -8.90% | -10.22% | -8.82% | +0.0228 | v3 | +0.0228 | v3 | +0.0228 | v3 | the same 3 cells and 3 d |
| gemmLnc3x1x3 fp32 | A:P | a075 | -0.12% | -0.63% | -0.05% | +0.0397 | v3 | +0.0397 | v3 | +0.0397 | v3 | the same 3 cells and 3 d |
| gemmLnc4x1x6 fp32 | A:P | a082 | -1.25% | -1.55% | -1.17% | +0.0649 | v3 | +0.0649 | v3 | +0.0649 | v3 | the same 3 cells and 3 d |
| gemmL10x10x1 fp32 | A:C | a046 | +3.25% | +4.37% | +3.37% | +0.0353 | v3 | +0.0353 | v3 | +0.0353 | v3 | the same 3 cells and 3 d |
| gemmL10x10x1 int8 | A:C | a045 | +3.94% | +5.07% | +4.03% | +0.0929 | v3 | +0.0929 | v3 | +0.0929 | v3 | the same 3 cells and 3 d |
| gemmL14x12x1 fp32 | A:C | a048 | +10.19% | +11.21% | +10.70% | +0.0698 | v3 | +0.0698 | v3 | +0.0698 | v3 | the same 3 cells and 3 d |
| gemmL14x12x1 int8 | A:C | a047 | +10.40% | +11.47% | +10.49% | +0.1187 | v3 | +0.1187 | v3 | +0.1187 | v3 | the same 3 cells and 3 d |
| gemmL1x1x18 fp32 | A:R | a017 | -2.83% | -2.52% | -2.74% | +0.0222 | v3 | +0.0222 | v3 | +0.0222 | v3 | the same 3 cells and 3 d |
| gemmL1x1x22 fp32 | A:R | a018 | -5.77% | -5.13% | -5.67% | -0.0023 | tie | -0.0023 | tie | -0.0023 | tie | the same 3 cells and 3 d |
| gemmL1x1x26 fp32 | A:R | a019 | -4.92% | -4.14% | -4.79% | -0.0070 | v2 | -0.0070 | v2 | -0.0070 | v2 | the same 3 cells and 3 d |
| gemmL1x1x30 fp32 | A:R | a020 | +2.29% | +3.40% | +2.39% | +0.0125 | v3 | +0.0125 | v3 | +0.0125 | v3 | the same 3 cells and 3 d |
| gemmL1x1x34 fp32 | A:R | a021 | +3.84% | +4.98% | +3.96% | +0.0189 | v3 | +0.0189 | v3 | +0.0189 | v3 | the same 3 cells and 3 d |
| gemmL1x1x44 fp32 | A:P | a083 | +5.79% | +6.95% | +5.61% | +0.0347 | v3 | +0.0347 | v3 | +0.0347 | v3 | the same 3 cells and 3 d |
| gemmL1x2x11 fp32 | A:I | a010 | +0.42% | +1.52% | +0.51% | +0.0426 | v3 | +0.0426 | v3 | +0.0426 | v3 | the same 3 cells and 3 d |
| gemmL1x2x11 int8 | A:I | a009 | +1.67% | +2.78% | +1.75% | +0.0483 | v3 | +0.0483 | v3 | +0.0483 | v3 | the same 3 cells and 3 d |
| gemmL1x2x13 fp32 | A:R | a022 | +1.46% | +2.57% | +1.55% | +0.0172 | v3 | +0.0172 | v3 | +0.0172 | v3 | the same 3 cells and 3 d |
| gemmL1x2x18 fp32 | A:R | a023 | +10.01% | +11.22% | +10.08% | -0.0014 | tie | -0.0014 | tie | -0.0014 | tie | the same 3 cells and 3 d |
| gemmL1x2x22 fp32 | A:R | a024 | +7.72% | +8.91% | +7.82% | +0.0191 | v3 | +0.0191 | v3 | +0.0191 | v3 | the same 3 cells and 3 d |
| gemmL1x2x7 fp32 | A:I | a008 | -1.04% | +1.80% | -0.95% | +0.0303 | v3 | -0.0052 | v2 | +0.0303 | v3 | the same 3 cells and 3 d |
| gemmL1x2x7 int8 | A:I | a007 | +0.93% | +1.54% | +1.02% | +0.0135 | v3 | +0.0135 | v3 | +0.0135 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x1010101 | A:M | a064 | **+12.70%** | +1.40% | **+12.82%** | +0.1280 | v3 | +0.1280 | v3 | +0.1280 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x11 | A:M | a063 | **+11.86%** | -5.64% | **+11.96%** | +0.1353 | v3 | +0.0193 | v3 | +0.1353 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x22222222 | A:M | a067 | +3.41% | -11.96% | +3.51% | +0.1138 | v3 | -0.1138 | v2 | +0.1138 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x3 | A:M | a062 | +0.91% | +2.01% | +0.98% | +0.1353 | v3 | +0.1353 | v3 | +0.1353 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x3030303 | A:M | a068 | +2.09% | -6.75% | +2.18% | +0.1138 | v3 | -0.0259 | v2 | +0.1138 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x55555555 | A:M | a072 | +4.67% | -6.09% | +4.72% | +0.0868 | v3 | -0.0390 | v2 | +0.0868 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0x7070707 | A:M | a070 | -0.47% | +0.62% | -0.39% | +0.0906 | v3 | +0.1001 | v3 | +0.0923 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0xf0000 | A:M | a065 | -0.47% | +0.62% | -0.39% | +0.1185 | v3 | +0.1280 | v3 | +0.1202 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0xf0f | A:M | a066 | +2.00% | +3.13% | +2.09% | +0.1138 | v3 | +0.1138 | v3 | +0.1138 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0xf0f0f0f | A:M | a071 | -0.60% | +0.49% | -0.52% | +0.0746 | v3 | +0.0868 | v3 | +0.0764 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 0xfff | A:M | a069 | +1.65% | +2.76% | +1.73% | +0.1001 | v3 | +0.1001 | v3 | +0.1001 | v3 | the same 3 cells and 3 d |
| gemmL1x3x12 fp32 | A:M | a061 | +1.90% | +3.01% | +2.01% | +0.0377 | v3 | +0.0377 | v3 | +0.0377 | v3 | the same 3 cells and 3 d |
| gemmL1x3x40 fp32 | A:E | a031, a032 | +5.51% | +6.67% | +5.50% | +0.0383 | v3 | +0.0383 | v3 | +0.0383 | v3 | the same 3 cells and 3 d |
| gemmL1x3x9 fp32 | A:I | a014 | +1.98% | +3.10% | +2.05% | -0.0155 | v2 | -0.0155 | v2 | -0.0155 | v2 | the same 3 cells and 3 d |
| gemmL1x3x9 int8 | A:I | a013 | +1.00% | +2.10% | +1.09% | +0.0052 | v3 | +0.0052 | v3 | +0.0052 | v3 | the same 3 cells and 3 d |
| gemmL1x4x36 fp32 | A:E | a035, a036 | +2.79% | +3.93% | +2.89% | +0.0171 | v3 | +0.0171 | v3 | +0.0171 | v3 | the same 3 cells and 3 d |
| gemmL1x6x5 fp32 | A:P | a076 | -0.72% | -0.88% | -0.64% | +0.0026 | tie | +0.0026 | tie | +0.0026 | tie | the same 3 cells and 3 d |
| gemmL2x1x10 fp32 | A:R | a026 | +0.28% | +0.47% | +0.37% | +0.0344 | v3 | +0.0305 | v3 | +0.0325 | v3 | the same 3 cells and 3 d |
| gemmL2x1x2 fp32 | A:I | a002 | +1.45% | +2.42% | +1.53% | -0.0022 | tie | -0.0022 | tie | -0.0022 | tie | the same 3 cells and 3 d |
| gemmL2x1x2 int8 | A:I | a001 | +2.83% | +2.55% | +2.92% | +0.0438 | v3 | +0.0438 | v3 | +0.0438 | v3 | the same 3 cells and 3 d |
| gemmL2x1x8 fp32 | A:R | a025 | +1.92% | +2.07% | +2.02% | +0.0577 | v3 | +0.0577 | v3 | +0.0577 | v3 | the same 3 cells and 3 d |
| gemmL2x2x44 fp32 | A:E | a033, a034 | +4.86% | +6.02% | +5.13% | +0.0411 | v3 | +0.0411 | v3 | +0.0411 | v3 | the same 3 cells and 3 d |
| gemmL2x2x7 fp32 | A:I | a012 | +0.29% | +1.38% | +0.38% | -0.0003 | tie | -0.0056 | v2 | -0.0020 | tie | the same 3 cells and 3 d |
| gemmL2x2x7 int8 | A:I | a011 | +0.15% | +1.24% | +0.25% | +0.0108 | v3 | +0.0109 | v3 | +0.0109 | v3 | the same 3 cells and 3 d |
| gemmL2x3x6 fp32 | A:I | a016 | -0.42% | +0.66% | -0.31% | -0.0021 | tie | +0.0063 | v3 | +0.0001 | tie | the same 3 cells and 3 d |
| gemmL2x3x6 int8 | A:I | a015 | -0.87% | +0.21% | -0.78% | +0.0078 | v3 | +0.0253 | v3 | +0.0097 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x1010101 | A:M | a052 | +3.02% | +4.15% | +3.11% | +0.0822 | v3 | +0.0822 | v3 | +0.0822 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x11 | A:M | a051 | +0.08% | +1.18% | +0.17% | +0.0885 | v3 | +0.0885 | v3 | +0.0885 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x22222222 | A:M | a055 | -4.19% | -3.14% | -4.11% | -0.0157 | v2 | +0.0061 | v3 | -0.0140 | v2 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x3 | A:M | a050 | **+11.57%** | +9.04% | **+11.67%** | +0.0885 | v3 | +0.0885 | v3 | +0.0885 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x3030303 | A:M | a056 | +3.04% | +2.29% | +3.13% | +0.0699 | v3 | +0.0699 | v3 | +0.0699 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x55555555 | A:M | a060 | +0.03% | +0.14% | +0.13% | +0.0464 | v3 | +0.0464 | v3 | +0.0464 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0x7070707 | A:M | a058 | +3.02% | +2.94% | +3.11% | +0.0580 | v3 | +0.0580 | v3 | +0.0580 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0xf0000 | A:M | a053 | +7.58% | **+29.46%** | +7.62% | +0.0822 | v3 | +0.0822 | v3 | +0.0822 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0xf0f | A:M | a054 | +8.39% | **+14.65%** | +8.45% | +0.0699 | v3 | +0.0699 | v3 | +0.0699 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0xf0f0f0f | A:M | a059 | +3.07% | +3.68% | +3.16% | +0.0464 | v3 | +0.0464 | v3 | +0.0464 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 0xfff | A:M | a057 | +7.55% | +10.16% | +7.66% | +0.0580 | v3 | +0.0580 | v3 | +0.0580 | v3 | the same 3 cells and 3 d |
| gemmL2x8x8 fp32 | A:M | a049 | +2.59% | +3.70% | +2.67% | +0.0034 | tie | +0.0034 | tie | +0.0034 | tie | the same 3 cells and 3 d |
| gemmL3x1x3 fp32 | A:I+P | a006 | +0.80% | +3.74% | +0.89% | -0.0009 | tie | -0.0151 | v2 | -0.0026 | tie | the same 3 cells and 3 d |
| gemmL3x1x3 int8 | A:I | a005 | +2.59% | +3.13% | +2.67% | +0.0306 | v3 | +0.0306 | v3 | +0.0306 | v3 | the same 3 cells and 3 d |
| gemmL3x1x6 fp32 | A:R | a027 | +0.93% | +1.03% | +1.01% | +0.0030 | tie | +0.0030 | tie | +0.0030 | tie | the same 3 cells and 3 d |
| gemmL3x1x7 fp32 | A:R | a028 | +0.55% | +0.67% | +0.62% | +0.0331 | v3 | +0.0306 | v3 | +0.0316 | v3 | the same 3 cells and 3 d |
| gemmL3x1x9 fp32 | A:R | a029 | +0.34% | +0.50% | +0.42% | +0.0513 | v3 | +0.0481 | v3 | +0.0496 | v3 | the same 3 cells and 3 d |
| gemmL3x2x1 fp32 | A:C | a038 | +1.76% | +1.90% | +1.84% | +0.0272 | v3 | +0.0272 | v3 | +0.0272 | v3 | the same 3 cells and 3 d |
| gemmL3x2x1 int8 | A:C | a037 | +2.26% | +2.37% | +2.35% | +0.0855 | v3 | +0.0855 | v3 | +0.0855 | v3 | the same 3 cells and 3 d |
| gemmL4x1x2 fp32 | A:I | a004 | +1.31% | +2.31% | +1.40% | +0.0009 | tie | -0.0186 | v2 | -0.0008 | tie | the same 3 cells and 3 d |
| gemmL4x1x2 int8 | A:I | a003 | +2.72% | +2.45% | +2.81% | +0.0190 | v3 | +0.0190 | v3 | +0.0190 | v3 | the same 3 cells and 3 d |
| gemmL4x1x6 fp32 | A:R+P | a030 | +0.72% | +0.84% | +0.81% | +0.0415 | v3 | +0.0392 | v3 | +0.0397 | v3 | the same 3 cells and 3 d |
| gemmL4x5x1 fp32 | A:C | a040 | -7.16% | -9.98% | -7.06% | -0.0698 | v2 | -0.0698 | v2 | -0.0698 | v2 | the same 3 cells and 3 d |
| gemmL4x5x1 int8 | A:C | a039 | -6.12% | -8.68% | -6.04% | -0.0047 | tie | -0.0599 | v2 | -0.0029 | tie | the same 3 cells and 3 d |
| gemmL7x3x1 fp32 | A:C | a042 | -4.48% | -5.58% | -4.39% | -0.0222 | v2 | -0.0222 | v2 | -0.0222 | v2 | the same 3 cells and 3 d |
| gemmL7x3x1 int8 | A:C | a041 | -3.18% | -4.32% | -3.10% | -0.0038 | tie | -0.0276 | v2 | -0.0022 | tie | the same 3 cells and 3 d |
| gemmL9x7x1 fp32 | A:C | a044 | -5.09% | -10.73% | -5.00% | -0.0463 | v2 | -0.0463 | v2 | -0.0463 | v2 | the same 3 cells and 3 d |
| gemmL9x7x1 int8 | A:C | a043 | -4.13% | -9.88% | -4.04% | +0.0179 | v3 | -0.1022 | v2 | +0.0197 | v3 | the same 3 cells and 3 d |
| gemmLn1x1x44 fp32 | A:P | a084 | +6.33% | +7.50% | +6.49% | +0.0030 | tie | +0.0030 | tie | +0.0030 | tie | the same 3 cells and 3 d |
| gemmLn1x6x5 fp32 | A:P | a077 | +1.21% | +0.50% | +1.28% | +0.0248 | v3 | +0.0389 | v3 | +0.0233 | v3 | the same 3 cells and 3 d |
| gemmLn3x1x3 fp32 | A:P | a073 | +2.06% | +1.05% | +2.15% | +0.0310 | v3 | +0.0509 | v3 | +0.0293 | v3 | the same 3 cells and 3 d |
| gemmLn4x1x6 fp32 | A:P | a080 | -2.41% | -2.30% | -2.31% | +0.0827 | v3 | +0.0827 | v3 | +0.0827 | v3 | the same 3 cells and 3 d |
| rgm211 gemmL1x1x44 fp32 | A:P | a085 | +5.41% | +6.57% | +5.63% | +0.0260 | v3 | +0.0260 | v3 | +0.0260 | v3 | the same 3 cells and 3 d |
| rgm211 gemmL1x6x5 fp32 | A:P | a078 | -0.54% | -1.35% | -0.44% | +0.0151 | v3 | +0.0151 | v3 | +0.0151 | v3 | the same 3 cells and 3 d |
| rgm211 gemmL3x1x3 fp32 | A:P | a074 | +0.36% | +0.69% | +0.45% | +0.0233 | v3 | +0.0167 | v3 | +0.0215 | v3 | the same 3 cells and 3 d |
| rgm211 gemmL4x1x6 fp32 | A:P | a081 | -1.34% | -1.54% | -1.26% | +0.0634 | v3 | +0.0634 | v3 | +0.0634 | v3 | the same 3 cells and 3 d |

## 5. Every point: joules (E1-E4) and the head-to-head H4 and H5, with verify-e213d beside

E1-E4 errors are measured / MM1-v3 - 1, except E1 and E2 at a watts point (marked W), where the scorer's error is |W measured - W MM1-v3| in watts against the 0.60 W band; a miss in bold. d as in section 4 (the tie 0.01 in ln, 0.05 W at a watts point). The three references (a088, a089 and a090, MM1-v3's declared 'ran before' rows) are measured but never scored, so they are in no table here: a088 is a087's gemmL twin in reading d, and a089 and a090 are reading i's anchor.

| point | family | the GEMM (arm, format, data, mask) | E1 | E2 | E3 | E4 | d H4 | H4 | d H5 | H5 | verify-e213d |
|---|---|---|---|---|---|---|---|---|---|---|---|
| a001 | A:I | gemmL2x1x2 int8 random | -3.88% | -3.55% | -1.19% | +0.90% | -0.0188 | v2 | -0.0037 | tie | the same 4 cells and 2 d |
| a002 | A:I | gemmL2x1x2 fp32 random | +4.75% | +4.89% | +2.39% | +3.23% | +0.0208 | v3 | +0.0210 | v3 | the same 4 cells and 2 d |
| a003 | A:I | gemmL4x1x2 int8 random | -3.20% | -2.88% | -0.99% | +1.02% | -0.0079 | tie | +0.0032 | tie | the same 4 cells and 2 d |
| a004 | A:I | gemmL4x1x2 fp32 random | +5.07% | +5.22% | +2.54% | +3.33% | +0.0193 | v3 | +0.0179 | v3 | the same 4 cells and 2 d |
| a005 | A:I | gemmL3x1x3 int8 random | -2.63% | -2.32% | -0.82% | +1.08% | -0.0207 | v2 | -0.0084 | tie | the same 4 cells and 2 d |
| a006 | A:I+P | gemmL3x1x3 fp32 random | +3.88% | +4.00% | +1.94% | +2.45% | +0.0088 | tie | +0.0080 | tie | the same 4 cells and 2 d |
| a007 | A:I | gemmL1x2x7 int8 random | -1.92% | -1.75% | -0.59% | +0.16% | -0.0048 | tie | -0.0073 | tie | the same 4 cells and 2 d |
| a008 | A:I | gemmL1x2x7 fp32 random | +3.82% | +3.87% | +1.91% | +1.45% | -0.0044 | tie | -0.0067 | tie | the same 4 cells and 2 d |
| a009 | A:I | gemmL1x2x11 int8 random | +1.49% | +1.77% | +0.39% | +1.75% | -0.0047 | tie | +0.0050 | tie | the same 4 cells and 2 d |
| a010 | A:I | gemmL1x2x11 fp32 random | -0.69% | -0.59% | -0.29% | +0.05% | +0.0094 | tie | +0.0054 | tie | the same 4 cells and 2 d |
| a011 | A:I | gemmL2x2x7 int8 random | -3.38% | -3.27% | -0.95% | -0.73% | -0.0127 | v2 | -0.0146 | v2 | the same 4 cells and 2 d |
| a012 | A:I | gemmL2x2x7 fp32 random | -2.69% | -2.59% | -1.19% | -0.94% | +0.0012 | tie | +0.0016 | tie | the same 4 cells and 2 d |
| a013 | A:I | gemmL1x3x9 int8 random | -1.73% | -1.53% | -0.49% | +0.35% | +0.0161 | v3 | +0.0146 | v3 | the same 4 cells and 2 d |
| a014 | A:I | gemmL1x3x9 fp32 random | -1.68% | -1.51% | -0.75% | +0.44% | +0.0154 | v3 | +0.0161 | v3 | the same 4 cells and 2 d |
| a015 | A:I | gemmL2x3x6 int8 random | -4.70% | -4.70% | -1.34% | -1.89% | -0.0130 | v2 | -0.0166 | v2 | the same 4 cells and 2 d |
| a016 | A:I | gemmL2x3x6 fp32 random | -2.32% | -2.23% | -1.04% | -1.17% | +0.0010 | tie | +0.0006 | tie | the same 4 cells and 2 d |
| a017 | A:R | gemmL1x1x18 fp32 random | -3.75% | -3.83% | -1.55% | -3.19% | +0.0161 | v3 | +0.0192 | v3 | the same 4 cells and 2 d |
| a018 | A:R | gemmL1x1x22 fp32 random | -4.17% | -4.41% | -1.74% | -5.16% | +0.0245 | v3 | +0.0262 | v3 | the same 4 cells and 2 d |
| a019 | A:R | gemmL1x1x26 fp32 random | -1.17% | -1.33% | -0.48% | -3.39% | +0.0353 | v3 | +0.0362 | v3 | the same 4 cells and 2 d |
| a020 | A:R | gemmL1x1x30 fp32 random | -2.22% | -1.99% | -0.88% | +0.62% | +0.0372 | v3 | +0.0353 | v3 | the same 4 cells and 2 d |
| a021 | A:R | gemmL1x1x34 fp32 random | -2.29% | -1.94% | -0.90% | +1.59% | +0.0341 | v3 | +0.0311 | v3 | the same 4 cells and 2 d |
| a022 | A:R | gemmL1x2x13 fp32 random | -0.55% | -0.37% | -0.22% | +0.77% | +0.0181 | v3 | +0.0160 | v3 | the same 4 cells and 2 d |
| a023 | A:R | gemmL1x2x18 fp32 random | -1.06% | -0.39% | -0.41% | +5.85% | +0.0258 | v3 | +0.0226 | v3 | the same 4 cells and 2 d |
| a024 | A:R | gemmL1x2x22 fp32 random | -2.10% | -1.55% | -0.81% | +4.05% | +0.0257 | v3 | +0.0213 | v3 | the same 4 cells and 2 d |
| a025 | A:R | gemmL2x1x8 fp32 random | -1.32% | -1.11% | -0.54% | +0.72% | -0.0042 | tie | -0.0102 | v2 | the same 4 cells and 2 d |
| a026 | A:R | gemmL2x1x10 fp32 random | -2.11% | -2.00% | -0.86% | -0.60% | +0.0064 | tie | +0.0102 | v3 | the same 4 cells and 2 d |
| a027 | A:R | gemmL3x1x6 fp32 random | -1.88% | -1.74% | -0.77% | -0.12% | -0.0037 | tie | -0.0043 | tie | the same 4 cells and 2 d |
| a028 | A:R | gemmL3x1x7 fp32 random | -2.10% | -2.00% | -0.86% | -0.45% | +0.0025 | tie | +0.0066 | tie | the same 4 cells and 2 d |
| a029 | A:R | gemmL3x1x9 fp32 random | -2.40% | -2.30% | -0.98% | -0.69% | +0.0068 | tie | +0.0124 | v3 | the same 4 cells and 2 d |
| a030 | A:R+P | gemmL4x1x6 fp32 random | -2.12% | -1.99% | -0.87% | -0.34% | +0.0015 | tie | +0.0067 | tie | the same 4 cells and 2 d |
| a031 | A:E | gemmL1x3x40 fp32 zeros | -4.34% | -3.21% | -0.64% | +4.21% | -0.0035 | tie | -0.0253 | v2 | the same 4 cells and 2 d |
| a032 | A:E | gemmL1x3x40 fp32 random | -4.18% | -3.74% | -1.64% | +1.74% | +0.0218 | v3 | +0.0163 | v3 | the same 4 cells and 2 d |
| a033 | A:E | gemmL2x2x44 fp32 zeros | -7.66% | -6.42% | -1.14% | +3.14% | -0.0107 | v2 | -0.0321 | v2 | the same 4 cells and 2 d |
| a034 | A:E | gemmL2x2x44 fp32 random | -4.16% | -3.62% | -1.62% | +1.78% | +0.0200 | v3 | +0.0143 | v3 | the same 4 cells and 2 d |
| a035 | A:E | gemmL1x4x36 fp32 zeros | -6.49% | -5.73% | -0.95% | +1.76% | -0.0051 | tie | -0.0156 | v2 | the same 4 cells and 2 d |
| a036 | A:E | gemmL1x4x36 fp32 random | -4.42% | -4.19% | -1.73% | -0.04% | +0.0212 | v3 | +0.0186 | v3 | the same 4 cells and 2 d |
| a037 | A:C | gemmL3x2x1 int8 random | -9.04% | -8.79% | -2.80% | -1.16% | -0.0568 | v2 | -0.0369 | v2 | the same 4 cells and 2 d |
| a038 | A:C | gemmL3x2x1 fp32 random | +3.65% | +3.80% | +1.85% | +2.84% | +0.0552 | v3 | +0.0574 | v3 | the same 4 cells and 2 d |
| a039 | A:C | gemmL4x5x1 int8 random | -6.20% | -6.60% | -2.07% | -6.22% | +0.1028 | v3 | +0.1085 | v3 | the same 4 cells and 2 d |
| a040 | A:C | gemmL4x5x1 fp32 random | +0.03% | -0.15% | +0.02% | -3.64% | +0.1009 | v3 | +0.1004 | v3 | the same 4 cells and 2 d |
| a041 | A:C | gemmL7x3x1 int8 random | -6.18% | -6.37% | -1.94% | -4.10% | +0.0873 | v3 | +0.0909 | v3 | the same 4 cells and 2 d |
| a042 | A:C | gemmL7x3x1 fp32 random | -2.00% | -2.09% | -0.98% | -3.29% | +0.0552 | v3 | +0.0535 | v3 | the same 4 cells and 2 d |
| a043 | A:C | gemmL9x7x1 int8 random | -3.66% | -3.89% | -1.21% | -3.99% | +0.1522 | v3 | +0.1599 | v3 | the same 4 cells and 2 d |
| a044 | A:C | gemmL9x7x1 fp32 random | +3.16% | +3.05% | +1.62% | -0.96% | +0.0988 | v3 | +0.1003 | v3 | the same 4 cells and 2 d |
| a045 | A:C | gemmL10x10x1 int8 random | -6.54% | -6.16% | -2.06% | +0.74% | +0.0764 | v3 | +0.1022 | v3 | the same 4 cells and 2 d |
| a046 | A:C | gemmL10x10x1 fp32 random | -3.02% | -2.79% | -1.49% | +0.27% | +0.0314 | v3 | +0.0394 | v3 | the same 4 cells and 2 d |
| a047 | A:C | gemmL14x12x1 int8 random | -6.08% | -5.18% | -1.78% | +5.61% | +0.0737 | v3 | +0.1206 | v3 | the same 4 cells and 2 d |
| a048 | A:C | gemmL14x12x1 fp32 random | -2.79% | -1.93% | -1.29% | +4.59% | +0.0322 | v3 | +0.0580 | v3 | the same 4 cells and 2 d |
| a049 | A:M | gemmL2x8x8 fp32 zeros | +6.04% | +6.82% | +0.87% | +3.28% | +0.0348 | v3 | +0.0403 | v3 | the same 4 cells and 2 d |
| a050 | A:M | gemmL2x8x8 fp32 zeros 0x3 (W) | 0.156 W | 0.135 W | +0.64% | **+12.30%** | +0.072 W | v3 | +0.063 W | v3 | the same 4 cells and 2 d |
| a051 | A:M | gemmL2x8x8 fp32 zeros 0x11 (W) | 0.004 W | 0.005 W | -0.02% | +0.15% | +0.068 W | v3 | +0.054 W | v3 | the same 4 cells and 2 d |
| a052 | A:M | gemmL2x8x8 fp32 zeros 0x1010101 (W) | 0.021 W | 0.009 W | +0.09% | +3.15% | +0.082 W | v3 | +0.059 W | v3 | the same 4 cells and 2 d |
| a053 | A:M | gemmL2x8x8 fp32 zeros 0xf0000 (W) | 0.582 W | 0.554 W | +2.47% | **+10.15%** | +0.078 W | v3 | +0.059 W | v3 | the same 4 cells and 2 d |
| a054 | A:M | gemmL2x8x8 fp32 zeros 0xf0f (W) | 0.588 W | 0.528 W | +2.45% | **+10.83%** | +0.084 W | v3 | +0.056 W | v3 | the same 4 cells and 2 d |
| a055 | A:M | gemmL2x8x8 fp32 zeros 0x22222222 (W) | 0.091 W | 0.057 W | -0.37% | -4.34% | -0.075 W | v2 | -0.056 W | v2 | the same 4 cells and 2 d |
| a056 | A:M | gemmL2x8x8 fp32 zeros 0x3030303 (W) | 0.211 W | 0.188 W | +0.87% | +3.93% | +0.093 W | v3 | +0.056 W | v3 | the same 4 cells and 2 d |
| a057 | A:M | gemmL2x8x8 fp32 zeros 0xfff (W) | 0.480 W | 0.399 W | +1.97% | +9.42% | +0.091 W | v3 | +0.059 W | v3 | the same 4 cells and 2 d |
| a058 | A:M | gemmL2x8x8 fp32 zeros 0x7070707 (W) | 0.332 W | 0.299 W | +1.36% | +4.37% | +0.103 W | v3 | +0.059 W | v3 | the same 4 cells and 2 d |
| a059 | A:M | gemmL2x8x8 fp32 zeros 0xf0f0f0f (W) | 0.479 W | 0.433 W | +1.90% | +4.93% | +0.111 W | v3 | +0.067 W | v3 | the same 4 cells and 2 d |
| a060 | A:M | gemmL2x8x8 fp32 zeros 0x55555555 (W) | 0.266 W | 0.266 W | +1.07% | +1.20% | +0.122 W | v3 | +0.067 W | v3 | the same 4 cells and 2 d |
| a061 | A:M | gemmL1x3x12 fp32 zeros | +1.37% | +1.97% | +0.19% | +2.00% | +0.0232 | v3 | +0.0414 | v3 | the same 4 cells and 2 d |
| a062 | A:M | gemmL1x3x12 fp32 zeros 0x3 (W) | 0.013 W | 0.015 W | -0.05% | +0.92% | +0.047 W | tie | +0.023 W | tie | the same 4 cells and 2 d |
| a063 | A:M | gemmL1x3x12 fp32 zeros 0x11 (W) | 0.039 W | 0.060 W | -0.16% | **+11.68%** | -0.009 W | tie | -0.052 W | v2 | the same 4 cells and 2 d |
| a064 | A:M | gemmL1x3x12 fp32 zeros 0x1010101 (W) | 0.229 W | 0.185 W | +0.97% | **+13.70%** | +0.068 W | v3 | +0.037 W | tie | the same 4 cells and 2 d |
| a065 | A:M | gemmL1x3x12 fp32 zeros 0xf0000 (W) | 0.033 W | 0.035 W | +0.14% | -0.24% | +0.079 W | v3 | +0.037 W | tie | the same 4 cells and 2 d |
| a066 | A:M | gemmL1x3x12 fp32 zeros 0xf0f (W) | 0.069 W | 0.054 W | +0.29% | +2.32% | +0.083 W | v3 | +0.015 W | tie | the same 4 cells and 2 d |
| a067 | A:M | gemmL1x3x12 fp32 zeros 0x22222222 (W) | 0.095 W | 0.069 W | +0.39% | +3.80% | +0.081 W | v3 | +0.015 W | tie | the same 4 cells and 2 d |
| a068 | A:M | gemmL1x3x12 fp32 zeros 0x3030303 (W) | 0.215 W | 0.199 W | +0.90% | +3.03% | +0.083 W | v3 | +0.015 W | tie | the same 4 cells and 2 d |
| a069 | A:M | gemmL1x3x12 fp32 zeros 0xfff (W) | 0.050 W | 0.031 W | +0.20% | +1.85% | +0.089 W | v3 | +0.000 W | tie | the same 4 cells and 2 d |
| a070 | A:M | gemmL1x3x12 fp32 zeros 0x7070707 (W) | 0.206 W | 0.211 W | +0.84% | +0.47% | +0.094 W | v3 | +0.000 W | tie | the same 4 cells and 2 d |
| a071 | A:M | gemmL1x3x12 fp32 zeros 0xf0f0f0f (W) | 0.072 W | 0.081 W | +0.28% | -0.20% | +0.100 W | v3 | -0.008 W | tie | the same 4 cells and 2 d |
| a072 | A:M | gemmL1x3x12 fp32 zeros 0x55555555 (W) | 0.579 W | 0.511 W | +2.34% | +6.88% | +0.082 W | v3 | -0.008 W | tie | the same 4 cells and 2 d |
| a073 | A:P | gemmLn3x1x3 fp32 random | +7.92% | +8.10% | **+4.05%** | +5.22% | +0.0057 | tie | +0.0016 | tie | the same 4 cells and 2 d |
| a074 | A:P | rgm211 gemmL3x1x3 fp32 random | +6.27% | +6.38% | +3.17% | +3.45% | +0.0074 | tie | +0.0055 | tie | the same 4 cells and 2 d |
| a075 | A:P | gemmLnc3x1x3 fp32 random | **+59.28%** | **+59.38%** | **+30.16%** | **+30.17%** | +0.0083 | tie | +0.0056 | tie | the same 4 cells and 2 d |
| a076 | A:P | gemmL1x6x5 fp32 random | -2.06% | -2.02% | -0.96% | -1.28% | +0.0047 | tie | +0.0051 | tie | the same 4 cells and 2 d |
| a077 | A:P | gemmLn1x6x5 fp32 random | -2.01% | -1.88% | -0.94% | -0.21% | +0.0080 | tie | +0.0113 | v3 | the same 4 cells and 2 d |
| a078 | A:P | rgm211 gemmL1x6x5 fp32 random | -1.30% | -1.23% | -0.61% | -0.81% | +0.0062 | tie | +0.0075 | tie | the same 4 cells and 2 d |
| a079 | A:P | gemmLnc1x6x5 fp32 random | **+15.37%** | **+14.98%** | **+7.52%** | +2.29% | -0.0032 | tie | -0.0074 | tie | the same 4 cells and 2 d |
| a080 | A:P | gemmLn4x1x6 fp32 random | -2.85% | -2.89% | -1.21% | -2.55% | +0.0034 | tie | +0.0122 | v3 | the same 4 cells and 2 d |
| a081 | A:P | rgm211 gemmL4x1x6 fp32 random | -2.43% | -2.43% | -1.01% | -1.75% | +0.0022 | tie | +0.0089 | tie | the same 4 cells and 2 d |
| a082 | A:P | gemmLnc4x1x6 fp32 random | **+37.85%** | **+37.86%** | **+15.71%** | **+14.91%** | -0.0018 | tie | -0.0085 | tie | the same 4 cells and 2 d |
| a083 | A:P | gemmL1x1x44 fp32 random | -3.24% | -3.06% | -1.29% | +2.04% | +0.0246 | v3 | +0.0194 | v3 | the same 4 cells and 2 d |
| a084 | A:P | gemmLn1x1x44 fp32 random | -4.10% | -3.59% | -1.65% | +2.31% | +0.0273 | v3 | +0.0249 | v3 | the same 4 cells and 2 d |
| a085 | A:P | rgm211 gemmL1x1x44 fp32 random | -4.59% | -4.06% | -1.82% | +1.67% | +0.0257 | v3 | +0.0215 | v3 | the same 4 cells and 2 d |
| a086 | A:P | gemmLnc1x1x44 fp32 random | **+47.02%** | **+48.29%** | **+18.27%** | **+25.47%** | -0.0265 | v2 | -0.0214 | v2 | the same 4 cells and 2 d |
| a087 | A:P | gemmLnc1x1x1 int8 random | **+67.98%** | **+67.93%** | **+26.98%** | **+25.13%** | -0.0357 | v2 | -0.0423 | v2 | the same 4 cells and 2 d |

## 6. REPORTED beside the verdicts (never verdicts)

**The bootstrap 95% interval of the mean d** (the scorer's; B = 10,000, seeded per rule; over the cases, or over the 65 points at 3 W and above for H4 and H5, as the scorer reads it; reproduced here by re-running the frozen scorer, not by independent code):

| rule | mean d | 95% interval | reading |
|---|---|---|---|
| H1 | +0.0402 (n 84) | [+0.0314, +0.0494] | MM1-v3 BETTER |
| H2 | +0.0308 (n 84) | [+0.0207, +0.0410] | MM1-v3 BETTER |
| H3 | +0.0401 (n 84) | [+0.0312, +0.0490] | MM1-v3 BETTER |
| H4 | +0.0184 (n 65) | [+0.0104, +0.0272] | MM1-v3 BETTER |
| H5 | +0.0203 (n 65) | [+0.0115, +0.0299] | MM1-v3 BETTER |

**The family check** (the sign test over the families' median d): the scorer counts a family for MM1-v3 when its median d is above 0 and for MM1-v2 when below 0; read that way every rule gives 7/1, p 0.0703 (the family A:I+P, one case, has a median d of -0.00088 in H1-H3, inside the 0.005 tie). Counting a family only when its median d is past the rule's tie (verify-e213d's finding 5; post hoc): H1 7/0, p 0.0156; H2 6/1, p 0.1250; H3 7/0, p 0.0156; H4 3/0, p 0.2500; H5 3/0, p 0.2500. Neither reading is a verdict; no verdict depends on them.

**The day offset and H4n, H5n** (reading h): the three tie runs (gemmL2x4x4 fp32 random, the full chip) read 19.575 W over idle against the committed reference's 19.86 W: offset_W -1.435%, and seconds +0.108%. H4 and H5 re-read with every measured J (and W) divided by (1 + offset_W): H4n MM1-v3 BETTER (52/6/29, p 3.158e-10); H5n MM1-v3 BETTER (47/8/32, p 8.068e-08). This lane re-derived the offset from the committed tie runs and H4n and H5n with its own arithmetic from the frozen forecast files: both equal to the scorer's.

**MM1-v3 and MM1-v2, rms and bias** (this lane's arithmetic on the JSON's measured points and the frozen CSV columns; equal to verify-e213d's on all 28 figures; relative error unless marked):

| quantity | n | MM1-v3 rms | MM1-v3 bias | MM1-v2 rms | MM1-v2 bias |
|---|---|---|---|---|---|
| wall cycles (per case, rel) | 84 | 4.61% | +1.73% | 9.79% | +5.20% |
| wall cycles (per case, ln) | 84 | 4.49% | +1.63% | 9.14% | +4.77% |
| counter mean (per case, rel) | 84 | 6.20% | +1.62% | 10.03% | +5.03% |
| counter mean (per case, ln) | 84 | 5.97% | +1.44% | 9.28% | +4.58% |
| seconds (per case, rel) | 84 | 4.66% | +1.83% | 9.86% | +5.30% |
| seconds (per case, ln) | 84 | 4.53% | +1.72% | 9.20% | +4.86% |
| J over idle given t (points at 3 W and above, rel) | 65 | 14.11% | +1.81% | 14.73% | +4.32% |
| J over idle given t (points at 3 W and above, ln) | 65 | 11.45% | +1.06% | 12.33% | +3.47% |
| J over idle with t forecast (points at 3 W and above, rel) | 65 | 14.14% | +2.04% | 14.86% | +4.88% |
| J over idle with t forecast (points at 3 W and above, ln) | 65 | 11.45% | +1.29% | 12.46% | +4.01% |
| W over idle given t (watts points, W) | 22 | 0.294 W | +0.205 W | 0.362 W | +0.292 W |
| W over idle frozen (watts points, W) | 22 | 0.265 W | +0.184 W | 0.297 W | +0.224 W |
| J at rest given t (every point, rel) | 87 | 5.29% | +0.96% | 5.48% | +1.65% |
| J at rest with t forecast (every point, rel) | 87 | 6.60% | +2.60% | 10.58% | +6.54% |
| post hoc: J over idle given t without the five gemmLnc points (rel) | 60 | 3.92% | -1.83% | 7.15% | +1.04% |
| post hoc: J over idle with t forecast without the five gemmLnc points (rel) | 60 | 3.79% | -1.60% | 7.55% | +1.67% |

**By family** (the scorer's `by_family_REPORTED`: the wall cycles per point, and J over idle with the seconds forecast at the points measured at 3 W and above; rms / bias):

| family | MM1-v3 wall cycles | MM1-v2 wall cycles | MM1-v3 J | MM1-v2 J |
|---|---|---|---|---|
| A:C | 5.83% / +0.14% (n 12) | 10.83% / +7.60% (n 12) | 4.84% / -3.09% (n 12) | 14.29% / +13.21% (n 12) |
| A:E | 4.54% / +4.39% (n 6) | 8.15% / +7.82% (n 6) | 4.64% / -4.48% (n 6) | 4.44% / -4.10% (n 6) |
| A:I | 1.57% / +1.00% (n 15) | 3.74% / +2.16% (n 15) | 3.14% / -0.74% (n 15) | 3.53% / +0.64% (n 15) |
| A:I+P | 0.80% / +0.80% (n 1) | 0.71% / -0.71% (n 1) | 4.00% / +4.00% (n 1) | 4.83% / +4.83% (n 1) |
| A:M | 5.52% / +3.56% (n 24) | 14.37% / +12.85% (n 24) | 5.02% / +4.39% (n 2) | 9.08% / +8.74% (n 2) |
| A:P | 4.41% / +0.85% (n 15) | 7.35% / -1.77% (n 15) | 28.63% / +14.78% (n 15) | 27.32% / +13.38% (n 15) |
| A:R | 4.41% / +1.22% (n 13) | 5.85% / +1.07% (n 13) | 2.22% / -1.92% (n 13) | 4.02% / -3.57% (n 13) |
| A:R+P | 0.72% / +0.72% (n 1) | 4.76% / -4.76% (n 1) | 1.99% / -1.99% (n 1) | 2.64% / -2.64% (n 1) |

**The census path (reading d)** - each loop's wall cycles over its rgm136 gemmL twin's, measured beside each model's ratio (MM1-v2 prices every loop as its twin, so its ratio is 1):

| ratio | points | measured | MM1-v3 | MM1-v2 |
|---|---|---|---|---|
| gemmLn/gemmL | a073 / a006 | 0.9567 | 0.9450 | 1.0000 |
| gemmLn/gemmL | a077 / a076 | 0.9733 | 0.9548 | 1.0000 |
| gemmLn/gemmL | a080 / a030 | 0.9434 | 0.9736 | 1.0000 |
| gemmLn/gemmL | a084 / a083 | 0.9738 | 0.9688 | 1.0000 |
| rgm211 gemmL/rgm136 gemmL | a074 / a006 | 0.9804 | 0.9848 | 1.0000 |
| rgm211 gemmL/rgm136 gemmL | a078 / a076 | 0.9893 | 0.9875 | 1.0000 |
| rgm211 gemmL/rgm136 gemmL | a081 / a030 | 0.9722 | 0.9925 | 1.0000 |
| rgm211 gemmL/rgm136 gemmL | a085 / a083 | 0.9877 | 0.9914 | 1.0000 |
| gemmLnc/gemmL | a075 / a006 | 0.9668 | 0.9757 | 1.0000 |
| gemmLnc/gemmL | a079 / a076 | 0.8992 | 0.9800 | 1.0000 |
| gemmLnc/gemmL | a082 / a030 | 0.9716 | 0.9910 | 1.0000 |
| gemmLnc/gemmL | a086 / a083 | 1.0201 | 0.9865 | 1.0000 |
| gemmLnc/gemmL | a087 / a088 | 0.9202 | 0.9436 | 1.0000 |
| zeros/random (W over idle) | a031 / a032 | 0.2692 | 0.2679 | 0.2570 |
| zeros/random (W over idle) | a033 / a034 | 0.2627 | 0.2692 | 0.2570 |
| zeros/random (W over idle) | a035 / a036 | 0.2640 | 0.2693 | 0.2602 |

The int8 / fp32 pairs (reading a, 14 pairs): measured 1.0110-1.0655, MM1-v3 1.0058-1.0471, MM1-v2 0.9630-1.0000. The subset layout (reading f): the measured spread of the wall cycles among the masks of one shire count runs 0.0138-0.1324 over the ten sets, where both models forecast one value a set. The timing simulation against the card (reading g, his question): over the 90 points, the measured cycles a GEMM run 8.0-35.1 times the simulator's step count (median 29.3; one step an instruction, not time), and the counter's mean 1.33-5.25 times the tensor unit's floor. The anchor's die (reading i): a089 and a090 started at 51.0 C and read 8.45 W and 8.43 W over idle against MM1-v3's 8.590 W at that die. Every reading is in the JSON (`readings_REPORTED`).

## 7. Dated clauses (Wed 18 Nov 2026), answering the card lanes' and the verifier's findings

1. **The outputs, committed now** (card-e213a's open issue; step 13's own words: "a later lane commits them beside the data"). The two files are RB_OUT's bytes, unchanged, after the checks of section 2. Nothing of them was re-made.
2. **E4 fails by one point** (card-e213a's finding, verify-e213d's finding 3, fix-e213d's clause). E4 (J with the card at rest, with the seconds forecast; band 10% = 2 x max(4.687, 3.774) = 9.37 rounded up) passes 78 of 87 points, and its 90% rule needs 79. Its nine failing points are exactly a050 (+12.30%), a053 (+10.15%), a054 (+10.83%), a063 (+11.68%), a064 (+13.70%), a075 (+30.17%), a082 (+14.91%), a086 (+25.47%), a087 (+25.13%). The nearest misses: a053 (0.15 points past the band) and a054 (0.83 points past the band). a073 and a079 pass E4 (a073 fails E3 alone; a079 fails E1, E2 and E3). E1 and E2 fail at exactly a075, a079, a082, a086 and a087; E3 at those five and a073. The verdict stands as registered: **FAIL**. A line in card-e213a's lane record (never committed) listed E4's failures after E3's ('E4 adds a050, a053, a054, a063, a064'), which reads as eleven; E4 has nine.
3. **The five gemmLnc points** (card-e213a's finding; the part of verify-e213d's finding 1 that is this arm's). Every E1 and E2 miss is a point of rgm136's gemmLnc loop: E1 a075 +59.28%, a079 +15.37%, a082 +37.85%, a086 +47.02%, a087 +67.98%. Their measured W over idle over MM1-v3's frozen W over idle (desk arithmetic): a075 1.595, a079 1.261, a082 1.395, a086 1.352, a087 1.720; their rgm136 gemmL twins a006 1.031, a076 0.986, a030 0.972, a083 0.918, a088 1.009; MM1-v3 itself put each gemmLnc point at 1.007-1.051 times its twin's W over idle. Their wall cycles held (T1 passes at all five; reading d above). Post hoc, without these five points, J over idle given the seconds reads MM1-v3 3.92% rms (3.9247%: verify-e213d's 3.925 at three places, which its result rounds again to 3.93%) against MM1-v2 7.15% (60 points), against 14.11% and 14.73% with them (65). REPORTED: the five stay in every rule as registered. Their board peaks against the planning peaks are note 1's section 3; MM1-v3.1's declaration (`7375bc9c`, declared before E213's data) names an item for the gemmLnc loop's census energy, which nothing here scores.
4. **The time misses are subset-mask cases** (card-e213a's finding). T1 and T3 miss at gemmL1x3x12 fp32 0x1010101 and 0x11 and gemmL2x8x8 fp32 0x3, T2 at gemmL2x8x8 fp32 0xf0000 and 0xf0f, every one slower than forecast (+11.6% to +29.5%): family M, where MM1-v3 has no layout model (E213.md 8: "The subset layout is a known gap"). Reading f's spreads above show the same: up to 13.2% between masks of one shire count, where both models forecast one value.
5. **The die latch** (card-e213a's finding). It rose from 51 C to 61 C in the session, under the registered 70 C line (card-e213a's record; verify-e213d replayed the stop lines on every sample: no trip). No scoring rule reads it.
6. **The smoke's rest reading** (card-e213a's finding). The reducer reads s02-s04's rest from the previous smoke process's tail (card-e213a's reading), so s04's J over idle in `reduce-e213.txt` is below zero (-0.000318 J: work 48.91 W against a rest of 49.33 W). R0 reads a smoke process's checks of C, its counter mean (200-4,000) and its walk and identity gate (the scorer's `reduce_arm`); no rule reads a smoke process's joules. Nothing scored depends on it.
7. **The second seal** (verify-e213d's finding 2). Corrected by the round's orchestrator in `f3de54a2` (`tools/claims-v3/sealed-e213/e213-freeze-lines-2-correction-1.md`) and recorded in note 1, section 1: for this arm, REPORTED as sealed during the session, before the data commit. The lab scores neither seal; nothing here depends on them.
8. **The smoke's arguments in `points-e213.json`** (verify-e213d's finding 4). Answered by note 1, section 2; no rule reads them.
9. **The family check and the tie** (verify-e213d's finding 5). Both readings are in section 6; they are REPORTED, and no verdict depends on them.
10. **The scans and the commit trailers** (verify-e213d's finding 6). This commit's message was scanned as the round's commit script builds it, its two standard trailer lines (the session line and the co-author line) set apart and named, and the rest scanned; the new files were scanned whole.
11. **Two commits right after the data commit** (card-e213a's open issue). `7375bc9c` (07:23:48 PST) and `3e8991d0` (07:23:56) landed 19 s and 27 s after the data commit, after step 13's scorer call (07:23:40-41), and add files under `tools/matmul/mm1/v3.1/` only: none of the 12 committed files the scorer opens (section 2). Their freeze lines are their own records' business.
12. **Arm B** (card-e213b). Arm B (aifoundry1 card 1) stopped at its step 4 at 06:39:56 PST, before any card command, by its kit's identity gate (the box had rebooted since the firmware read that gate relies on); it has no data directory and no scorer output. In this file arm B is NO DATA on every rule, and the pooled HP1-HP5 are NO DATA. Arm B's rerun is the round's next card work for E213 (the orchestrator's Amendments A2 and A3, not committed at `f658861c`); its scores lane commits arm B's scorer output and scores the pooled rules once arm B's data are committed.
13. **What the verifier did not run** (verify-e213d's list). The bands' bases B1 and B2 were not re-derived from MM1-v3's fold records there or here (NOT RUN). The bootstrap intervals are reproduced here by re-running the frozen scorer, not by independent code (NOT RUN). The day offset, H4n and H5n are re-derived here by independent arithmetic: equal (section 6). No box disk was read.

## 8. NOT RUN

- The scorer's self-tests and the kit's desk tests (they ran in the card lane's desk step `s03_desk_e213` at 06:35:52 PST, rc 0).
- verify-e213d's code: its outputs were read and compared, not re-run.
- Independent code for the bootstrap intervals; a re-derivation of the bands' bases B1 and B2.
- Any read of aifoundry1's or aifoundry3's disks.

## What this note changes

Nothing measured, forecast, registered or scored. It adds four new files: the frozen scorer's two outputs, byte for byte as step 13 wrote them, this note and `SHA256SUMS-note2`, which lists the other three and `SHA256SUMS-note1`. Every committed file stands as committed.

SPDX-License-Identifier: Apache-2.0
