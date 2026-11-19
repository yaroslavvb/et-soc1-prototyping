# E213 arm B data, dated note 2: the frozen scorer's output, committed beside the data byte for byte - R0, S6 and T1-T3 PASS (31 of 31 cases), E1-E4 PASS (36 of 38 points; the misses are exactly the two gemmLnc points, k37 and k40), MM1-v3 BETTER than MM1-v2 on H1, H3, H4 and H5 and H2 NOT DECIDED, with verify-e213bd's re-derivation beside each result

*Wed 18 Nov 2026 (week 47), PST; written at about 16:56 PST by Q219's lane `scores-e213b`, after this directory's data commit `b0c727c5` (committed 15:49:38 PST, pushed by 15:49:43), after the day's data verifier `verify-e213bd` (HOLDS WITH FIXES: this directory's data re-derive exactly from the raw records, its own scoring equals the frozen scorer's on every verdict, count, p value and cell, and the frozen scorer re-run on the committed data reproduces both outputs byte for byte) and after dated note 1 (`3e1d1d43`, 16:30:24 PST). It adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed, and nothing is re-scored. Labels: **registered** (E213.md with its Amendment A1; arm B's dated Amendments A2 and A3, which change no point, forecast, rule or scorer), **measured** (this directory's committed records), **blind** (MM1-v3's and MM1-v2's arm B forecasts, frozen by E213's registration `291c8201`, pushed to the lab repository's main branch by 04:18:27 PST Wed 18 Nov 2026, before arm B's first card command: fwgate's one firmware read at 15:13:25 PST, the session from 15:15:28), **REPORTED** (never a verdict), **post hoc** (read after the data), **desk** (a check of code at the desk, under `/usr/bin/python3` 3.12.3).*

**The words.** The frozen scorer (`score_e213.py`, registered sha256 `a4eece29...`), run by the kit's step 13 at 15:49:54 PST on this directory's committed `data-e213.json` with step 6n's committed `labels-e213.json` (no point and no case labelled 'ran before'), printed for arm B: **R0 PASS**; **S6 PASS**; **T1 PASS** 31/31, **T2 PASS** 31/31, **T3 PASS** 31/31 (cycles and seconds per case); **E1 PASS** 36/38, **E2 PASS** 36/38, **E3 PASS** 36/38, **E4 PASS** 36/38 (joules per point; each rule needs 35 of 38, and each misses exactly k37 and k40, the two gemmLnc points); head to head against MM1-v2 (the sign test, MM1-v3 / MM1-v2 / ties): **H1 MM1-v3 BETTER** 21/7/3 (p 0.0125), **H2 NOT DECIDED** 20/10/1 (p 0.0987), **H3 MM1-v3 BETTER** 20/7/4 (p 0.0192), **H4 MM1-v3 BETTER** 20/4/13 (p 0.0015), **H5 MM1-v3 BETTER** 22/4/11 (p 0.00053). Arm A: NO DATA in this one-arm file; the pooled HP1-HP5: NO DATA in this file (they are dated note 3, made by the same scorer on both arms' committed data). k38 and k39 are NO DATA (the registered board stop in run 079 started nothing further); k37 and k40 have one run each. With R0 and S6 PASS, no verdict of arm B carries a label: these are arm B's registered verdicts.

**MM1-v3 against MM1-v2, rms of the relative error** (desk arithmetic on this directory's measured values and the frozen arm B forecasts, equal to verify-e213bd's; REPORTED; blind): the wall cycles 3.19% against 5.84% (31 cases), the counter's mean 3.91% against 5.88%, seconds 3.17% against 5.87%; J over idle given the seconds 17.29% (38 points) against 18.88% (37: MM1-v2 prices no sparse50, k34), and 3.87% against 7.65% without the two gemmLnc points (post hoc); with the seconds forecast 17.24% against 18.54%; J with the card at rest given the seconds 7.00% against 7.51%, with the seconds forecast 7.10% against 7.87%. Arm B has no point under 3 W (no watts point).

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e213-B.json` | 79,262 | `692bfed37711d069c8fb185f2dae2c21490f5d957fac0cc365bdb3bfccdebb52` | the frozen scorer's output (`score_e213.py`, registered sha256 `a4eece29...`): every verdict, count, cell, measured point, head-to-head count and REPORTED reading of arm B; arm A and the pooled rules NO DATA |
| `scores-e213-B.txt` | 1,159 | `02e685898f5b83fb5f53983bdfc816ec07ebe2baa4e63d8b98d833935dc7001f` | its printed lines (step 13's capture of the call) |
| `README.md.dated-note-2.md` | (this note) | listed in `SHA256SUMS-note2` | this dated note |
| `SHA256SUMS-note2` | 4 lines | (not listed in itself) | the three files above and `SHA256SUMS-note1` |

The two output files are card-e213b2's RB_OUT files byte for byte. With `SHA256SUMS` (453 entries), `SHA256SUMS-note1` (6: note 1's four files, `README.md` and `SHA256SUMS`) and `SHA256SUMS-note2` (4), every file of this directory is in a list except `SHA256SUMS-note2` itself. Dated note 3 (the pooled rules), committed after this note, brings its own list, `SHA256SUMS-note3`, which lists `SHA256SUMS-note2`.

## 2. Where the outputs came from (desk checks of code)

- **The step.** The kit's step 13 (`rb/s24_score_e213.sh B`) is the runbook log's last six lines (lines 130-135 of 135), all at 15:49:54 PST, each rc 0, the six captures under one process id. Call 1 printed the data commit `b0c727c54` and its subject; call 2 (the directory clean) printed nothing; call 3 read all 453 `SHA256SUMS` entries OK, in the list's order; call 4 printed `HISTORY OK` naming the registration `291c8201ae4b`; call 5 printed `LABELS-OK`; call 6 ran `/usr/bin/python3 -I -B tools/claims-v3/e213/score_e213.py docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json --labels docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/labels-e213.json --out <the card lane's RB_OUT>/scores-e213-B.json` (0.4 s). The log holds no earlier run of the scorer on data: only its two self-tests and its forecasts print, in the runbook's desk step (`s03_desk_e213`, 15:12:43 PST, rc 0).
- **The bytes.** `scores-e213-B.txt` is the runbook's capture of call 6 byte for byte (the step's copy of it), and it rebuilds exactly from the JSON through the scorer's own print function (`text()`, read from `score_e213.py` at the data commit). The JSON is in the scorer's own dump form (indent 1, sorted keys, no trailing newline) and was last written inside call 6 (its time stamp equals call 6's capture's, 15:49:54.966 PST, at the file system's clock step); the text file was copied after it (15:49:54.975).
- **The commit before it.** The data commit `b0c727c5` was made at 15:49:38 PST and pushed by 15:49:43; at 15:49:43 the card lane left its collect span, removed its hold line and released aifoundry1; step 13 ran at 15:49:54. The lab clone's HEAD during the step was the data commit itself (its reflog: `b0c727c5` from 15:49:38 until 15:50:02). The commits since, none touching any of the 12 committed files the scorer opens: `b2230d68` (15:50:02 PST, 1 file: `tools/claims-v3/sealed-e214`); `3e1d1d43` (16:30:24 PST, 5 files: `docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1`); `321f992c` (16:31:02 PST, 217 files: `docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3`); `29b741e0` (16:38:58 PST, 33 files: `tools/matmul/mm1`); `3b3e4182` (16:44:33 PST, 327 files: `docs/reports/data/2026-11-18-e214-mmsweep3-a1c0-S1`).
- **The frozen files.** The registration list's 27 files and the list itself have one blob each at `291c8201` (the registration: arm B's freeze line), `6efdb002` (the kit), `8e91dda6` and `d8404ef2` (the two seals' registrations), `8b675547` (A2 and A3), `b0c727c5` and HEAD; the kit list's 49 files and the list from `6efdb002` on; A2's and A3's lists from `8b675547` on; `tools/claims-v3/e213/` is unchanged from the kit to the data commit (A2 and A3 add files under `tools/claims-v3/e213-a2/` and `e213-a3/` only); arm B's frozen files (E213.md section 0: `forecast-e213b-v3.csv` `e529bbb2...`, `forecast-e213b-v3.json` `fc7ac542...`, `forecast-e213b-v2.csv` `297762eb...`, `points-e213.json`, `rules-e213.json`, `score_e213.py`) at their listed sha256 and one blob at the registration and the data commit; arm A's frozen files (MM1-v3's land `b1493082`, which the scorer also pins) likewise. The scorer's nine pins equal those files' sha256 at the data commit.
- **The re-runs.** In a tree of exactly the 12 committed files the scorer opens (its own file, its nine pinned inputs, `data-e213.json` and `labels-e213.json`), taken from the data commit's objects, with no bytecode cache, a plain run and a run under an audit hook that lists every file opened, each with step 13's arguments, wrote both outputs byte for byte equal to RB_OUT and to the capture of call 6; the audited run opened those 12 files, 33 standard-library files and nothing else but its own outputs. The scorer imported unchanged from that tree and called in process (`score(data, labels, quiet=True)`) gives a result whose dump equals RB_OUT's JSON byte for byte; its own functions (`reduce_arm`, `score_arm`, `decide`, `family_check`), called as `score()` calls them, give every case's and point's d value (the JSON keeps only the counts), with the JSON's counts, p values, family checks and cells. Sections 4 and 5 print those d values. verify-e213bd's own re-run of the frozen scorer on the committed data gave the same two files (its `v8_rescore` record).
- **The bytes named before.** card-e213b2 and verify-e213bd named `scores-e213-B.json` by `692bfed3...` and the text file by `02e68589...`: both equal.

## 3. The rules: their registered words, the verdicts, verify-e213bd beside

The scorer's printed lines (`scores-e213-B.txt`, verbatim):

```
E213 scorer (score_e213.py), the registered verdicts:
ARM A: R0 NO DATA; S6 NO DATA; T1 NO DATA; T2 NO DATA; T3 NO DATA; E1 NO DATA; E2 NO DATA; E3 NO DATA; E4 NO DATA
  H1 NO DATA
  H2 NO DATA
  H3 NO DATA
  H4 NO DATA
  H5 NO DATA
ARM B: R0 PASS; S6 PASS; T1 PASS 31/31; T2 PASS 31/31; T3 PASS 31/31; E1 PASS 36/38; E2 PASS 36/38; E3 PASS 36/38; E4 PASS 36/38
  H1 MM1-v3 BETTER (v3 21 / v2 7 / ties 3; p 0.012540951371192932); REPORTED bootstrap MM1-v3 BETTER [0.01189045941704969, 0.03500549371741206]
  H2 NOT DECIDED (v3 20 / v2 10 / ties 1; p 0.09873714670538902); REPORTED bootstrap MM1-v3 BETTER [0.002858401163783083, 0.029698505296708345]
  H3 MM1-v3 BETTER (v3 20 / v2 7 / ties 4; p 0.0191572904586792); REPORTED bootstrap MM1-v3 BETTER [0.011904402025974517, 0.03455362435482624]
  H4 MM1-v3 BETTER (v3 20 / v2 4 / ties 13; p 0.001543879508972168); REPORTED bootstrap MM1-v3 BETTER [0.013974032138539238, 0.039567420752530336]
  H5 MM1-v3 BETTER (v3 22 / v2 4 / ties 11; p 0.0005335211753845215); REPORTED bootstrap MM1-v3 BETTER [0.015283043926518173, 0.04023316284254403]
POOLED: HP1 NO DATA; HP2 NO DATA; HP3 NO DATA; HP4 NO DATA; HP5 NO DATA
```

**MM1-v3's rules, per arm** (E213.md 7, its words): "Each case or point passes when |measured / MM1-v3 - 1| is within its band; a rule's verdict: PASS if at least 90% of its scored cases or points pass, FAIL otherwise, TOO FEW under 10, NO DATA with none." "The band is twice the larger of two held-out errors of MM1-v3 for that quantity, rounded up to a whole percent:" B1, "leave one experiment out over every point without configuration twins", and B2, "the same over this arm's card's points". "The points under about 3 W over idle are scored in absolute watts in E1 and E2": "arm B 0.60 W = 2 x max(0.2969, 0.2983, SD_rep 0.1146) = 0.597 -> 0.60 W"; "arm B has none forecast", and none measured under 3 W. The section's title: "a point or case with no run is NO DATA, never a failure". The scorer's 90% rule passes a rule when the passing cases or points number at least ceil(0.9 n).

| rule | the registered words (E213.md 7, arm B) | band | scored | needed (90%) | the scorer (registered verdict) | verify-e213bd's own scoring | slack (REPORTED) | the cases or points that miss |
|---|---|---|---|---|---|---|---|---|
| **R0** | every check of C exact or approx (the smoke's, every point run's, kept or set aside, every reference's and tie's); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk good (walk_launches_bad 0, walk_ok on every launch) and its identity gate GATE OK. A FAIL of either labels every other verdict of its arm. | - | 83 checks of C (4 smoke processes, 76 point and reference runs, 3 tie runs); the four smoke counter means; 3 rgm211-host processes (s14 and the runs of k37 and k40) | all | **PASS** (0 failures; the smoke s11-s14 at 1119.81, 819.096, 787.416, 754.258 cycles an op; every rgm211-host walk good and gate GATE OK) | PASS | - | none |
| **S6** | every kept run's counted samples at 590-610 MHz. | 590-610 MHz | the 76 kept runs of the 39 points that ran | all | **PASS** (0 failures) | PASS | - | none |
| **T1** | cycles an op, the wall, per case; 2 x max(5.038, 5.668) = 11.34 -> 12% | 12% | 31 | 28 | **PASS** (31/31) | PASS (31/31; the same cells, worst difference 0) | 3 | none (worst passing case 6.15%) |
| **T2** | cycles an op, the counter's mean, per case; 2 x max(6.029, 6.843) = 13.69 -> 14% | 14% | 31 | 28 | **PASS** (31/31) | PASS (31/31; the same cells, worst difference 0) | 3 | none (worst passing case 7.70%) |
| **T3** | seconds a GEMM, per case (T1's bases); 2 x max(5.038, 5.668) = 11.34 -> 12% | 12% | 31 | 28 | **PASS** (31/31) | PASS (31/31; the same cells, worst difference 0) | 3 | none (worst passing case 6.05%) |
| **E1** | J over idle given the measured seconds, per point (watts under 3 W); 2 x max(4.938, 5.639) = 11.28 -> 12% | 12% | 38 | 35 | **PASS** (36/38) | PASS (36/38; the same cells, worst difference 0) | 1 | k37 (+66.14%); k40 (+80.32%) |
| **E2** | J over idle with the seconds forecast, per point (watts under 3 W); 2 x max(5.705, 5.874) = 11.75 -> 12% | 12% | 38 | 35 | **PASS** (36/38) | PASS (36/38; the same cells, worst difference 0) | 1 | k37 (+66.28%); k40 (+80.18%) |
| **E3** | J with the card at rest given the measured seconds and rest, per point; 2 x max(1.711, 1.252) = 3.42 -> 4% | 4% | 38 | 35 | **PASS** (36/38) | PASS (36/38; the same cells, worst difference 0) | 1 | k37 (+30.98%); k40 (+29.28%) |
| **E4** | J with the card at rest with the seconds forecast, per point; 2 x max(4.687, 5.124) = 10.25 -> 11% | 11% | 38 | 35 | **PASS** (36/38) | PASS (36/38; the same cells, worst difference 0) | 1 | k37 (+31.01%); k40 (+27.31%) |

The slack is the passing count less the count the 90% rule needs (REPORTED, desk arithmetic). Every energy rule passes with a slack of 1: its two misses are k37 and k40, the gemmLnc points (section 7, clause 3); no time case misses.

**THE HEAD-TO-HEAD RULES** (E213.md 7, its words): "per case (cycles, seconds) or per point (joules), d = |ln(measured / MM1-v2)| - |ln(measured / MM1-v3)| (at a watts point, |W - W_v2| - |W - W_v3| in watts); MM1-v3 is closer where d > the tie, MM1-v2 where d < -the tie, a tie otherwise." The ties: "arm B 0.005 in ln for cycles and 0.005 for seconds, 0.015 for joules, 0.05 W at a watts point". "Decided by the exact two-sided sign test at alpha 0.05 on the untied cases: MM1-v3 BETTER if p < 0.05 and it is closer in more cases than not; MM1-v2 BETTER if p < 0.05 the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none." Registered over "arm A 84, arm B 33" cases (H1-H3) and "arm A 87 (22 in watts), arm B 39 (k34: MM1-v2 prices no sparse50)" points (H4, H5); scored over 31 cases and 37 points (k38 and k39 NO DATA).

| rule | the registered words (E213.md 7) | over | MM1-v3 closer | MM1-v2 closer | ties | p (exact, two-sided) | the scorer | verify-e213bd | where MM1-v2 is closer |
|---|---|---|---|---|---|---|---|---|---|
| **H1** | cycles an op, the wall, per case | 31 cases | 21 | 7 | 3 | 0.01254 | **MM1-v3 BETTER** | MM1-v3 BETTER (21/7/3, the same p; every d equal, worst difference 0) | `gemmL1x1x26` fp32; `gemmL1x1x26` int8; `gemmL4x3x2` fp32; `gemmL4x3x2` int8; `gemmL4x4x1` fp32; `gemmL7x3x1` fp32; `gemmL7x3x1` int8 |
| **H2** | cycles an op, the counter's mean, per case | 31 cases | 20 | 10 | 1 | 0.09874 | **NOT DECIDED** | NOT DECIDED (20/10/1, the same p; every d equal, worst difference 0) | `gemmL1x1x26` fp32; `gemmL1x1x26` int8; `gemmL1x2x7` fp32; `gemmL3x1x3` fp32; `gemmL4x1x2` fp32; `gemmL4x3x2` fp32; `gemmL4x3x2` int8; `gemmL4x4x1` fp32; `gemmL7x3x1` fp32; `gemmL7x3x1` int8 |
| **H3** | seconds a GEMM, per case | 31 cases | 20 | 7 | 4 | 0.01916 | **MM1-v3 BETTER** | MM1-v3 BETTER (20/7/4, the same p; every d equal, worst difference 0) | `gemmL1x1x26` fp32; `gemmL1x1x26` int8; `gemmL4x3x2` fp32; `gemmL4x3x2` int8; `gemmL4x4x1` fp32; `gemmL7x3x1` fp32; `gemmL7x3x1` int8 |
| **H4** | J over idle given the measured seconds, per point both price | 37 points | 20 | 4 | 13 | 0.001544 | **MM1-v3 BETTER** | MM1-v3 BETTER (20/4/13, the same p; every d equal, worst difference 0) | k09; k11; k20; k40 |
| **H5** | J over idle with the seconds forecast, per point both price | 37 points | 22 | 4 | 11 | 0.0005335 | **MM1-v3 BETTER** | MM1-v3 BETTER (22/4/11, the same p; every d equal, worst difference 0) | k09; k11; k20; k40 |

**HP1-HP5** (E213.md 7: "H1-H5 pooled over both arms, each case or point once with its own arm's tie; NO DATA unless both arms scored"): NO DATA in this one-arm file. They are made by the same frozen scorer on both arms' committed data in dated note 3 of this directory (`README.md.dated-note-3.md`, `scores-e213-pooled.json`): MM1-v3 BETTER on all five.

## 4. Every case: cycles and seconds (T1-T3) and the head-to-head H1-H3, with verify-e213bd beside

Errors are measured / MM1-v3 - 1 (the scorer's `err`; a miss would be in bold: there is none); d is the registered d (positive: MM1-v3 closer; the tie 0.005), from the frozen scorer's own functions (section 2); the closer is MM1-v3 (v3), MM1-v2 (v2) or a tie. Every case runs the full chip (mask 0xffffffff) on rgm136's gemmL loop, except the two gemmLnc cases. MM1-v2's wall error is REPORTED beside. The last column compares verify-e213bd's re-derivation (its `rederive-e213b.json`, code that imports nothing of the kit's) with the scorer's: its three cells and its three d values.

| case | points | family | T1 wall | T2 counter | T3 seconds | H1 d (closer) | H2 d (closer) | H3 d (closer) | MM1-v2 wall (REPORTED) | verify-e213bd |
|---|---|---|---|---|---|---|---|---|---|---|
| `gemmLnc1x1x1` int8 (gemmLnc) | k40 | BP | -2.45% | -2.10% | -2.34% | +0.0631 (v3) | +0.0631 (v3) | +0.0631 (v3) | -8.41% | equal |
| `gemmLnc3x1x3` fp32 (gemmLnc) | k37 | BP | -0.13% | -0.66% | -0.04% | +0.0397 (v3) | +0.0397 (v3) | +0.0397 (v3) | -4.02% | equal |
| `gemmL1x1x18` fp32 | k13 | BR | -2.94% | -2.60% | -2.85% | +0.0222 (v3) | +0.0222 (v3) | +0.0222 (v3) | -5.07% | equal |
| `gemmL1x1x26` fp32 | k17 | BR | -5.15% | -4.41% | -4.99% | -0.0070 (v2) | -0.0070 (v2) | -0.0070 (v2) | -4.48% | equal |
| `gemmL1x1x26` int8 | k18 | BR | -3.86% | -3.15% | -3.75% | -0.0070 (v2) | -0.0070 (v2) | -0.0070 (v2) | -3.18% | equal |
| `gemmL1x1x34` fp32 | k19 | BR | +3.51% | +4.65% | +3.67% | +0.0189 (v3) | +0.0189 (v3) | +0.0189 (v3) | +5.49% | equal |
| `gemmL1x2x11` fp32 | k10 | BI | +0.28% | +1.37% | +0.37% | +0.0426 (v3) | +0.0426 (v3) | +0.0426 (v3) | +4.64% | equal |
| `gemmL1x2x11` int8 | k09 | BI | +1.39% | +2.49% | +1.50% | +0.0483 (v3) | +0.0483 (v3) | +0.0483 (v3) | +6.40% | equal |
| `gemmL1x2x7` fp32 | k08 | BI | -1.07% | +1.78% | -0.96% | +0.0303 (v3) | -0.0050 (v2) | +0.0303 (v3) | -4.02% | equal |
| `gemmL1x2x7` int8 | k07 | BI | +0.91% | +1.53% | +1.02% | +0.0135 (v3) | +0.0135 (v3) | +0.0135 (v3) | +2.27% | equal |
| `gemmL1x3x40` fp32 | k28, k29 | BE | +5.29% | +6.45% | +5.37% | +0.0383 (v3) | +0.0383 (v3) | +0.0383 (v3) | +9.40% | equal |
| `gemmL2x1x2` fp32 | k02 | BI | +1.43% | +2.41% | +1.53% | -0.0022 (tie) | -0.0022 (tie) | -0.0022 (tie) | +1.20% | equal |
| `gemmL2x1x2` int8 | k01 | BI | +2.81% | +2.54% | +2.91% | +0.0438 (v3) | +0.0438 (v3) | +0.0438 (v3) | +7.42% | equal |
| `gemmL2x1x8` fp32 | k11 | BR | +1.77% | +1.99% | +1.87% | +0.0577 (v3) | +0.0577 (v3) | +0.0577 (v3) | +7.81% | equal |
| `gemmL2x2x44` fp32 | k30, k31 | BE | +5.14% | +6.30% | +5.19% | +0.0411 (v3) | +0.0411 (v3) | +0.0411 (v3) | +9.55% | equal |
| `gemmL2x3x1` fp32 | k21 | BK | +1.03% | +1.01% | +1.13% | +0.0459 (v3) | +0.0459 (v3) | +0.0459 (v3) | +5.78% | equal |
| `gemmL2x3x1` int8 | k20 | BK | +1.39% | +1.49% | +1.50% | +0.1090 (v3) | +0.1090 (v3) | +0.1090 (v3) | +13.06% | equal |
| `gemmL3x1x3` fp32 | k06, k32, k33, k34 | BI | +0.77% | +3.72% | +0.88% | -0.0003 (tie) | -0.0151 (v2) | -0.0024 (tie) | -0.74% | equal |
| `gemmL3x1x3` int8 | k05, k35, k36 | BI | +2.56% | +3.12% | +2.67% | +0.0306 (v3) | +0.0306 (v3) | +0.0306 (v3) | +5.74% | equal |
| `gemmL3x1x7` fp32 | k12 | BR | +0.40% | +0.60% | +0.52% | +0.0360 (v3) | +0.0321 (v3) | +0.0335 (v3) | -3.92% | equal |
| `gemmL3x1x9` fp32 | k15 | BR | +0.19% | +0.44% | +0.32% | +0.0541 (v3) | +0.0492 (v3) | +0.0516 (v3) | -5.45% | equal |
| `gemmL3x1x9` int8 | k16 | BR | +2.58% | +2.37% | +2.72% | +0.0070 (v3) | +0.0111 (v3) | +0.0044 (tie) | -3.20% | equal |
| `gemmL4x1x2` fp32 | k04 | BI | +1.29% | +2.29% | +1.40% | +0.0013 (tie) | -0.0184 (v2) | -0.0009 (tie) | -1.40% | equal |
| `gemmL4x1x2` int8 | k03 | BI | +2.70% | +2.44% | +2.81% | +0.0190 (v3) | +0.0190 (v3) | +0.0190 (v3) | +4.67% | equal |
| `gemmL4x1x6` fp32 | k14 | BR | +0.53% | +0.71% | +0.64% | +0.0453 (v3) | +0.0417 (v3) | +0.0432 (v3) | -4.94% | equal |
| `gemmL4x3x2` fp32 | k27 | BK | -6.15% | -7.19% | -6.05% | -0.0387 (v2) | -0.0387 (v2) | -0.0387 (v2) | -2.45% | equal |
| `gemmL4x3x2` int8 | k26 | BK | -5.47% | -7.17% | -5.36% | -0.0461 (v2) | -0.0664 (v2) | -0.0438 (v2) | +1.02% | equal |
| `gemmL4x4x1` fp32 | k23 | BK | -5.36% | -7.70% | -5.25% | -0.0128 (v2) | -0.0627 (v2) | -0.0104 (v2) | +4.32% | equal |
| `gemmL4x4x1` int8 | k22 | BK | -4.42% | -6.51% | -4.31% | +0.0594 (v3) | +0.0153 (v3) | +0.0618 (v3) | +11.04% | equal |
| `gemmL7x3x1` fp32 | k25 | BK | -4.58% | -5.66% | -4.47% | -0.0222 (v2) | -0.0222 (v2) | -0.0222 (v2) | -2.44% | equal |
| `gemmL7x3x1` int8 | k24 | BK | -3.37% | -4.46% | -3.26% | -0.0077 (v2) | -0.0304 (v2) | -0.0055 (v2) | +2.69% | equal |

k38 (`gemmLnc1x2x7` fp32) and k39 (`gemmLnc4x1x6` fp32) are two more cases: NO DATA (no run), never a failure.

## 5. Every point: joules (E1-E4) and the head-to-head H4 and H5, with verify-e213bd beside

Errors are measured / MM1-v3 - 1 (a miss in bold); every arm B point is scored in relative terms (no point under 3 W). d is the registered d (the tie 0.015 in ln). k34 (sparse50) is priced by MM1-v3 alone, so it is in E1-E4 and in no head-to-head. W over idle is the measured mean of the point's kept runs.

| point | family | GEMM | runs | W over idle | E1 | E2 | E3 | E4 | H4 d (closer) | H5 d (closer) | verify-e213bd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| k01 | BI | `gemmL2x1x2` int8 random | 2 | 10.78 W | -2.04% | -1.59% | -0.57% | +1.64% | -0.0014 (tie) | +0.0210 (v3) | equal |
| k02 | BI | `gemmL2x1x2` fp32 random | 2 | 25.05 W | +2.60% | +2.79% | +1.20% | +2.12% | +0.0466 (v3) | +0.0471 (v3) | equal |
| k03 | BI | `gemmL4x1x2` int8 random | 2 | 10.78 W | -2.05% | -1.61% | -0.57% | +1.55% | -0.0046 (tie) | +0.0118 (tie) | equal |
| k04 | BI | `gemmL4x1x2` fp32 random | 2 | 24.87 W | +1.83% | +2.02% | +0.85% | +1.69% | +0.0452 (v3) | +0.0429 (v3) | equal |
| k05 | BI | `gemmL3x1x3` int8 random | 2 | 11.21 W | +0.04% | +0.48% | +0.01% | +2.04% | +0.0147 (tie) | +0.0242 (v3) | equal |
| k06 | BI | `gemmL3x1x3` fp32 random | 2 | 24.94 W | +1.78% | +1.93% | +0.82% | +1.37% | +0.0344 (v3) | +0.0331 (v3) | equal |
| k07 | BI | `gemmL1x2x7` int8 random | 2 | 11.16 W | +1.12% | +1.35% | +0.31% | +1.11% | -0.0109 (tie) | -0.0075 (tie) | equal |
| k08 | BI | `gemmL1x2x7` fp32 random | 2 | 24.84 W | +2.08% | +2.13% | +0.96% | +0.46% | +0.0216 (v3) | +0.0177 (v3) | equal |
| k09 | BI | `gemmL1x2x11` int8 random | 2 | 9.30 W | +3.09% | +3.44% | +0.74% | +1.97% | -0.0268 (v2) | -0.0194 (v2) | equal |
| k10 | BI | `gemmL1x2x11` fp32 random | 2 | 17.15 W | -2.57% | -2.46% | -0.98% | -0.71% | -0.0051 (tie) | -0.0114 (tie) | equal |
| k11 | BR | `gemmL2x1x8` fp32 random | 2 | 16.22 W | -3.92% | -3.67% | -1.45% | -0.20% | -0.0169 (v2) | -0.0268 (v2) | equal |
| k12 | BR | `gemmL3x1x7` fp32 random | 2 | 16.24 W | -4.01% | -3.86% | -1.50% | -1.12% | -0.0105 (tie) | -0.0038 (tie) | equal |
| k13 | BR | `gemmL1x1x18` fp32 random | 2 | 16.21 W | -5.77% | -5.93% | -2.18% | -3.99% | +0.0024 (tie) | +0.0078 (tie) | equal |
| k14 | BR | `gemmL4x1x6` fp32 random | 2 | 16.30 W | -3.74% | -3.59% | -1.39% | -0.94% | -0.0114 (tie) | -0.0029 (tie) | equal |
| k15 | BR | `gemmL3x1x9` fp32 random | 2 | 16.23 W | -3.97% | -3.83% | -1.48% | -1.23% | -0.0063 (tie) | +0.0027 (tie) | equal |
| k16 | BR | `gemmL3x1x9` int8 random | 2 | 8.52 W | -0.36% | +0.20% | -0.08% | +2.13% | +0.0331 (v3) | +0.0431 (v3) | equal |
| k17 | BR | `gemmL1x1x26` fp32 random | 2 | 16.94 W | -2.68% | -2.95% | -1.01% | -4.24% | +0.0211 (v3) | +0.0233 (v3) | equal |
| k18 | BR | `gemmL1x1x26` int8 random | 2 | 9.37 W | +1.76% | +1.22% | +0.43% | -2.57% | +0.0431 (v3) | +0.0558 (v3) | equal |
| k19 | BR | `gemmL1x1x34` fp32 random | 2 | 15.39 W | -3.89% | -3.44% | -1.40% | +1.06% | +0.0231 (v3) | +0.0180 (v3) | equal |
| k20 | BK | `gemmL2x3x1` int8 random | 2 | 10.36 W | -8.23% | -7.98% | -2.33% | -1.21% | -0.0608 (v2) | -0.0279 (v2) | equal |
| k21 | BK | `gemmL2x3x1` fp32 random | 2 | 25.27 W | +0.56% | +0.72% | +0.26% | +0.94% | +0.0825 (v3) | +0.0878 (v3) | equal |
| k22 | BK | `gemmL4x4x1` int8 random | 2 | 11.72 W | -3.04% | -3.44% | -0.90% | -4.06% | +0.1420 (v3) | +0.1646 (v3) | equal |
| k23 | BK | `gemmL4x4x1` fp32 random | 2 | 24.89 W | -1.67% | -1.87% | -0.79% | -3.70% | +0.0931 (v3) | +0.0969 (v3) | equal |
| k24 | BK | `gemmL7x3x1` int8 random | 2 | 10.90 W | -4.17% | -4.47% | -1.19% | -3.60% | +0.0958 (v3) | +0.1007 (v3) | equal |
| k25 | BK | `gemmL7x3x1` fp32 random | 2 | 22.71 W | -3.15% | -3.32% | -1.42% | -3.96% | +0.0531 (v3) | +0.0496 (v3) | equal |
| k26 | BK | `gemmL4x3x2` int8 random | 2 | 11.22 W | -1.50% | -2.11% | -0.43% | -4.47% | +0.0509 (v3) | +0.0483 (v3) | equal |
| k27 | BK | `gemmL4x3x2` fp32 random | 2 | 23.04 W | -1.79% | -2.08% | -0.80% | -4.32% | +0.0299 (v3) | +0.0251 (v3) | equal |
| k28 | BE | `gemmL1x3x40` fp32 zeros | 2 | 4.17 W | -8.89% | -7.36% | -1.25% | +3.41% | +0.0884 (v3) | +0.0595 (v3) | equal |
| k29 | BE | `gemmL1x3x40` fp32 random | 2 | 14.79 W | -5.68% | -5.16% | -2.02% | +1.61% | +0.0127 (tie) | +0.0032 (tie) | equal |
| k30 | BE | `gemmL2x2x44` fp32 zeros | 2 | 4.11 W | -10.59% | -9.12% | -1.48% | +3.17% | +0.0837 (v3) | +0.0532 (v3) | equal |
| k31 | BE | `gemmL2x2x44` fp32 random | 2 | 14.90 W | -5.16% | -4.67% | -1.84% | +1.54% | +0.0109 (tie) | +0.0012 (tie) | equal |
| k32 | BS | `gemmL3x1x3` fp32 zeros | 2 | 4.66 W | -1.39% | -1.05% | -0.20% | +0.60% | -0.0003 (tie) | +0.0061 (tie) | equal |
| k33 | BS | `gemmL3x1x3` fp32 ones | 2 | 10.96 W | -1.18% | -0.97% | -0.33% | +0.35% | +0.0145 (tie) | +0.0172 (v3) | equal |
| k34 | BS | `gemmL3x1x3` fp32 sparse50 | 2 | 13.49 W | -0.11% | +0.08% | -0.04% | +0.62% | - (MM1-v2 prices none) | - (MM1-v2 prices none) | equal |
| k35 | BS | `gemmL3x1x3` int8 zeros | 2 | 4.03 W | -2.01% | -1.02% | -0.26% | +2.19% | +0.0556 (v3) | +0.0317 (v3) | equal |
| k36 | BS | `gemmL3x1x3` int8 ones | 2 | 5.44 W | -2.49% | -1.74% | -0.42% | +1.92% | +0.0254 (v3) | +0.0071 (tie) | equal |
| k37 | BP | `gemmLnc3x1x3` fp32 random | 1 | 41.96 W | **+66.14%** | **+66.28%** | **+30.98%** | **+31.01%** | +0.0347 (v3) | +0.0304 (v3) | equal |
| k40 | BP | `gemmLnc1x1x1` int8 random | 1 | 29.31 W | **+80.32%** | **+80.18%** | **+29.28%** | **+27.31%** | -0.0178 (v2) | -0.0292 (v2) | equal |

k38 and k39: NO DATA (no run). k41, the reference (`gemmL1x1x1` int8 random, k40's twin, which ran on card 1 before), is measured and read in reading d, and scored by no rule.

## 6. REPORTED beside the verdicts (never verdicts)

**The bootstrap 95% interval of the mean d** (the scorer's; B = 10,000, seeded per rule; over the cases, or the 37 points both price; reproduced here by re-running the frozen scorer, not by independent code): H1 [+0.0119, +0.0350] (mean d +0.0233, MM1-v3 BETTER); H2 [+0.0029, +0.0297] (mean d +0.0164, MM1-v3 BETTER); H3 [+0.0119, +0.0346] (mean d +0.0232, MM1-v3 BETTER); H4 [+0.0140, +0.0396] (mean d +0.0266, MM1-v3 BETTER); H5 [+0.0153, +0.0402] (mean d +0.0271, MM1-v3 BETTER). The bootstrap reads MM1-v3 BETTER at H2 too, where the registered sign test does not decide; the sign test is the registered test, chosen before the data for this reason (E213.md 7): "The sign test keeps its false-winner rate under the midpoint at 2-5% (nominal), where the percentile bootstrap of the mean d runs 4.5-7.6% (above nominal, as E209's registration found)."

**The family check** (the sign test over the families' median d; the scorer counts a family for MM1-v3 when its median d is above 0 and for MM1-v2 when below 0): H1 4/1 p 0.3750; H2 4/1 p 0.3750; H3 4/1 p 0.3750; H4 6/0 p 0.0312; H5 6/0 p 0.0312; read with each rule's tie instead of 0: H1 4/1 p 0.3750; H2 4/1 p 0.3750; H3 4/1 p 0.3750; H4 3/0 p 0.2500; H5 3/0 p 0.2500. The family medians of H1: BE +0.0397, BI +0.0247, BK -0.0103, BP +0.0514, BR +0.0222 (BK, the one-K-block family, leans to MM1-v2 in time).

**The day offset and H4n, H5n** (reading h: "offset_W = the mean W over idle of the arm's tie runs over the committed reference, less 1, and the same for the seconds"): the three tie runs (t02, `gemmL4x8x8` int8 random, the full chip; runs 001, 039 and 077) read 9.078 W over idle against the committed reference's 9.503 W: offset_W -4.471%, and seconds -0.053%. "H4 and H5 re-read with every measured J (and W at a watts point) divided by (1 + offset_W), by the same test; H1-H5 stay decided as registered": H4n MM1-v3 BETTER 18/6/13 (p 0.0227), H5n MM1-v3 BETTER 19/6/12 (p 0.0146), re-derived here by independent arithmetic: equal to the scorer's.

**MM1-v3 and MM1-v2, rms and bias** (this lane's arithmetic on the JSON's measured points and the frozen CSV columns, read with Python's csv module; equal to verify-e213bd's re-derivation on all 26 figures compared; relative error measured / forecast - 1 unless marked):

| quantity | MM1-v3 rms (bias; n) | MM1-v2 rms (bias; n) |
|---|---|---|
| wall cycles an op, per case | 3.19% (-0.29%; n 31) | 5.84% (+1.57%; n 31) |
| wall cycles, per case, ln | 3.22% (-0.34%; n 31) | 5.69% (+1.41%; n 31) |
| counter's mean, per case | 3.91% (-0.06%; n 31) | 5.88% (+1.78%; n 31) |
| seconds a GEMM, per case | 3.17% (-0.18%; n 31) | 5.87% (+1.69%; n 31) |
| J over idle given the seconds, per point | 17.29% (+1.72%; n 38) | 18.88% (+4.11%; n 37) |
| J over idle given the seconds, ln | 13.21% (+0.68%; n 38) | 14.96% (+2.81%; n 37) |
| J over idle with the seconds forecast | 17.24% (+1.94%; n 38) | 18.54% (+4.84%; n 37) |
| J with the card at rest given the seconds | 7.00% (+0.99%; n 38) | 7.51% (+1.98%; n 37) |
| J with the card at rest with the seconds forecast | 7.10% (+1.36%; n 38) | 7.87% (+3.77%; n 37) |
| post hoc: J over idle given the seconds without k37, k40 | 3.87% (-2.26%; n 36) | 7.65% (+0.08%; n 35) |
| post hoc: J over idle with the seconds forecast without k37, k40 | 3.61% (-2.03%; n 36) | 7.54% (+0.93%; n 35) |
| post hoc: J at rest given the seconds without k37, k40 | 1.12% (-0.63%; n 36) | 2.27% (+0.34%; n 35) |
| post hoc: J at rest with the seconds forecast without k37, k40 | 2.41% (-0.19%; n 36) | 5.21% (+2.53%; n 35) |
| J over idle given the seconds, on the 37 points both price | 17.53% (+1.77%) | 18.88% (+4.11%) |

**By family** (the scorer's `by_family_REPORTED`: the wall cycles per point, and J over idle with the seconds forecast at the points measured at 3 W and above; rms / bias):

| family | MM1-v3 wall | MM1-v2 wall | MM1-v3 J | MM1-v2 J |
|---|---|---|---|---|
| BE | 5.22% / +5.22% (n 4) | 9.48% / +9.48% (n 4) | 6.82% / -6.58% (n 4) | 10.07% / -9.20% (n 4) |
| BI | 1.73% / +1.31% (n 10) | 4.45% / +2.62% (n 10) | 2.13% / +0.85% (n 10) | 4.26% / +3.38% (n 10) |
| BK | 4.35% / -3.37% (n 8) | 6.75% / +4.13% (n 8) | 3.86% / -3.07% (n 8) | 12.09% / +10.80% (n 8) |
| BP | 1.73% / -1.29% (n 2) | 6.59% / -6.22% (n 2) | 73.56% / +73.23% (n 2) | 73.23% / +73.21% (n 2) |
| BR | 2.84% / -0.33% (n 9) | 5.02% / -1.88% (n 9) | 3.55% / -2.87% (n 9) | 4.73% / -4.44% (n 9) |
| BS | 1.73% / +1.49% (n 5) | 3.68% / +1.86% (n 5) | 1.11% / -0.94% (n 5) | 2.86% / -2.72% (n 4) |

Families (E213.md, Appendix B): BI int8 against fp32 inside the L3; BR the two-edge retention ladder; BK one K block; BE the switch route's kinds at deep K (zeros beside random); BS the kinds at one shape (zeros, ones, sparse50); BP the census path (gemmLnc beside its rgm136 gemmL twins).

**The readings** (registered before the data; measured beside each model's ratio; REPORTED):

| reading | pair | quantity | measured | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| int8/fp32 | k01 / k02 | wall cycles | 1.0614 | 1.0471 | 1.0000 |
| int8/fp32 | k03 / k04 | wall cycles | 1.0616 | 1.0470 | 1.0000 |
| int8/fp32 | k05 / k06 | wall cycles | 1.0653 | 1.0468 | 1.0000 |
| int8/fp32 | k07 / k08 | wall cycles | 1.0656 | 1.0448 | 1.0000 |
| int8/fp32 | k09 / k10 | wall cycles | 1.0169 | 1.0058 | 1.0000 |
| int8/fp32 | k16 / k15 | wall cycles | 1.0238 | 1.0000 | 1.0000 |
| int8/fp32 | k18 / k17 | wall cycles | 1.0136 | 1.0000 | 1.0000 |
| int8/fp32 | k20 / k21 | wall cycles | 1.0369 | 1.0332 | 0.9701 |
| int8/fp32 | k22 / k23 | wall cycles | 1.0305 | 1.0205 | 0.9682 |
| int8/fp32 | k24 / k25 | wall cycles | 1.0271 | 1.0142 | 0.9758 |
| int8/fp32 | k26 / k27 | wall cycles | 1.0356 | 1.0281 | 1.0000 |
| gemmLnc/gemmL | k37 / k06 | wall cycles | 0.9669 | 0.9757 | 1.0000 |
| gemmLnc/gemmL | k40 / k41 | wall cycles | 0.9204 | 0.9436 | 1.0000 |
| zeros/random | k28 / k29 | W over idle | 0.2823 | 0.2882 | 0.3049 |
| zeros/random | k30 / k31 | W over idle | 0.2757 | 0.2895 | 0.3049 |
| zeros/random | k32 / k06 | W over idle | 0.1871 | 0.1927 | 0.2004 |
| ones/random | k33 / k06 | W over idle | 0.4393 | 0.4522 | 0.4755 |
| sparse50/random | k34 / k06 | W over idle | 0.5412 | 0.5512 | - |
| zeros/random | k35 / k05 | W over idle | 0.3595 | 0.3649 | 0.3859 |
| ones/random | k36 / k05 | W over idle | 0.4853 | 0.4962 | 0.5120 |

The pairs with k38 or k39 (k38 / k08, k39 / k14) have no reading: NO DATA. Reading (a), the int8 L3 factor: measured int8 / fp32 1.014-1.066 at the 11 pairs, MM1-v3 1.000-1.047, MM1-v2 0.968-1.000. Reading (d), the census path: gemmLnc ran 3.3% (k37) and 8.0% (k40) under its gemmL twin's wall cycles, MM1-v3 2.4% and 5.6%, MM1-v2 0. Reading (e), the switch route: the kinds' W over idle over random, measured 0.187-0.541, MM1-v3 within 0.005-0.014 of each (7 pairs), MM1-v2 within 0.013-0.036 (6 pairs: none for sparse50).

**The timing simulation against reality** (reading g, his question): each point's measured cycles a GEMM (the slowest minion's counter) over the simulator's step count in MM1-v3's column (one step an instruction, not time): 7.98-35.05, median 20.73 (37 points with a step count); the counter's mean over the tensor unit's floor (529 cycles an op for fp32, 270 for int8, measured): 1.326-5.330. So the simulator's step count is not a time model here either (E213.md 7, reading g).

## 7. Dated clauses (Wed 18 Nov 2026), answering the card lane's, the verifier's and the fix lane's findings

1. **The outputs, committed now** (card-e213b2's open issue; step 13's own words: "a later lane commits it beside the data"). The two files are RB_OUT's bytes, unchanged, after the checks of section 2. Nothing of them was re-made.
2. **The short day** (card-e213b2's finding 1, verify-e213bd's finding 1). The registered board stop (72 W on 3 samples in a row, E213's stop lines for arm B) tripped during run 079 (k37, pass 1; 72.04, 72.04 and 72.24 W at 15:45:08 PST, verify-e213bd's reading of the samples); the runner started nothing further, so runs 080-085 never ran: k38 and k39 are NO DATA, and k37 and k40 have one run each. Amendment A3 had moved the gemmLnc block to the session's end so that a trip there cost only that block (A3 saved runs 041-078). The round's orchestrator accepted the short day as registered: no amendment and no rerun of the gemmLnc block (its answer of 15:5x PST: a rerun would trip the same stop on card 1). The scorer reads the two missing points as NO DATA, never a failure: E1-E4 are scored over 38 points and T1-T3 over 31 cases.
3. **MM1-v3 underprices gemmLnc energy on card 1** (card-e213b2's finding 2, verify-e213bd's finding 2). Every E1-E4 miss is k37 or k40: E1 k37 +66.14%, k40 +80.32%; E3 k37 +30.98%, k40 +29.28%. Their measured J over idle over MM1-v3's J given the measured seconds: k37 1.661, k40 1.803 (arm A's five gemmLnc points on the same footing, from its committed scores: 1.15-1.68); their cycles held (T1 at k37 -0.13%, at k40 -2.45%). Post hoc, without the two, J over idle given the seconds reads MM1-v3 3.87% against MM1-v2 7.65% (36 and 35 points). REPORTED: the two stay in every rule as registered, and every energy rule still passes (36 of 38). MM1-v3.1's declaration (`7375bc9c`, declared before E213's data) names an item for the gemmLnc loop's census energy, which nothing here scores.
4. **H2 NOT DECIDED** (card-e213b2's finding 3, verify-e213bd's finding 4). MM1-v3 is closer in 20 cases and MM1-v2 in 10 (1 tie), p 0.0987: not decided by the registered test, as registered. E213.md 7 said so before the data: "on arm B alone it is weak, 0.24-0.50"; "So the pooled rules carry the day's answer when both arms run, and arm B's own head-to-head says NOT DECIDED more often than not even if MM1-v3 is better there." The pooled HP2 decides: MM1-v3 BETTER (dated note 3). The bootstrap reading beside (REPORTED) is MM1-v3 BETTER.
5. **Step 6n's never-run line** (card-e213b2's finding 4, verify-e213bd's finding 3, fix-e213bd). Answered by dated note 1 (`3e1d1d43`): the judgement holds 126 counted hits in 12 files (110 dated 13:42:16 PST, 16 dated 06:29:02 PST), all copies of E214's planned arms, none a run, none marked before the freeze line; the README's 112 counts the capped text form. The labels are empty, so every point is scored: nothing here changes.
6. **The outputs reproduce byte for byte** (verify-e213bd's finding 5). Confirmed here too (section 2), and committed as they are.
7. **The card's power state** (the README's reading 15). Read 3 at the start and 1 at the end, never set; no scoring rule reads it.
8. **Amendments A2 and A3** change no point, forecast, rule, band or scorer (A2: the firmware identity shown on the present boot by fwgate's one read; A3: the gemmLnc block's place in the session). A3's own check found that the scorer and every rule read runs by point id and pass, never by place, and the scorer here read the committed runs by point id: the session's order does not enter any verdict.
9. **The day offset** (reading h). Card 1 read the tie 4.47% under its committed reference (E208's and E212's card-1 points), with seconds equal to 0.05%. Re-read with every measured J divided by (1 + offset_W), H4 and H5 stay MM1-v3 BETTER (section 6). REPORTED only.
10. **What the verifier did not run.** The bands' bases B1 and B2 were not re-derived from MM1-v3's fold records there or here (NOT RUN). The bootstrap intervals are reproduced here by re-running the frozen scorer, not by independent code (NOT RUN). The day offset, H4n and H5n are re-derived here by independent arithmetic: equal (section 6). No box disk was read.

## 8. NOT RUN

- The scorer's self-tests and the kit's desk tests (they ran in the card lane's desk step `s03_desk_e213` at 15:12:43 PST, rc 0).
- verify-e213bd's code: its outputs were read and compared, not re-run.
- Independent code for the bootstrap intervals; a re-derivation of the bands' bases B1 and B2.
- Any read of aifoundry1's disk.

## What this note changes

Nothing measured, forecast, registered or scored. It adds four new files: the frozen scorer's two outputs, byte for byte as step 13 wrote them, this note and `SHA256SUMS-note2`, which lists the other three and `SHA256SUMS-note1`. Every committed file stands as committed.

SPDX-License-Identifier: Apache-2.0
