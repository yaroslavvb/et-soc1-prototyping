# blind-e221-scores: dated note 1, the folder as landed and verify-blind-e221's check of it

*Fri 20 Nov 2026, Pacific time. Written by the lab's lane land-blind-e221 (round Q235) at 19:13 PST for this folder's commit, after verify-blind-e221 held the lab's blind test of E221 WITH FIXES (18:12-18:55 PST). Its fixes are all to the declaration's folder, `../blind-e221/`, committed just before as 88d16581; it found this folder CLEAN and named no fix to it. Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), standard library only, single-threaded. This note changes no file of the folder and no number, forecast, rule or verdict. Labels: **measured** is E221's committed data, **blind** the forecasts frozen before E221's first datum, **desk** the verifier's re-derivation; **REPORTED** and **post hoc** as the README uses them.*

## What is committed here

- **The folder** is blind-e221's land byte for byte: 43 files and `SHA256SUMS` (sha256 `bf1a15f582ff5c4a...`, 43 of 43 OK), written at 18:10 PST, after the measured-conditions forecasts were hashed (17:52:57), the scorer and the readings were hashed (17:59:51) and the data were read and scored (18:00:03).
- **The declaration it scores** is `../blind-e221/`, committed just before as 88d16581, so this README's links to it resolve.
- **The independent scorer the README lists as NOT RUN** (line 206) has now run. verify-blind-e221 re-derived this score with its own code, from the declaration's text, and every number, rule cell and verdict came out the same. **The declared test FAILS**: part A (MM1-v3.2 on the primary footing, the no-twin cases) fails the same 14 rules on the three cards, E1 and E3 pass on every card, and part S is NOT APPLICABLE. The nearest case to a band edge is 1.19e-4 from it. In detail:
  - **the label:** all nine sessions BLIND, their first card commands 9.997 to 568.363 minutes after the freeze post (06:22:58 PST), each under a claim posted after it;
  - **the order:** the conditions read at 17:46:51 (the declared fields only), the forecasts hashed at 17:52:57, the scorer and the readings hashed at 17:59:51 (the stand-in tests ran on the final scorer, 17:59:27-31), and the committed data first copied in at 18:00:03. All 12 frozen files of the lane are equal to their hashes now, the hash logs check 14 of 14, and none of the 74 stand-in files equals a committed file;
  - **the runs and conditions:** its own run list holds 811 runs in 733 cases, and its own reading of the conditions equals `inputs/conditions-e221.json` in 2,433 of 2,433 fields;
  - **the forecasts:** its own caller, at each run's measured conditions, equals `forecasts-blind-e221.json` bit for bit, 116,784 fields (the four base models, 12,976 each, and the eight composed forms, 8,110 each); at the nominal conditions it equals the declaration's frozen forecasts bit for bit as well;
  - **the scores:** its own scorer against `scores/` and `cases/`, on both footings: 42 of 42 part-A cells (n, passes, verdict and misses, for MM1-v3.2 and MM1-v3.1), 12 of 12 models' named fails, 156 of 156 comparison cells (D0-D2, D3, D3c; per card and pooled), 86,952 per-case values bit-equal, the twin flags 2,932 of 2,932 and the watts flags 733 of 733;
  - **the README:** the headline table's 96 printed figures equal its full precision rounded to their digits, and ten more README figures are as printed;
  - **post hoc (REPORTED):** the T1 misses by class, MASK 152, MQ3 12, KB1 6 and NB1 5; without the MASK class part A would pass on all three cards, as the README says;
  - **the land:** SHA256SUMS lists the other 43 files, 43 of 43 OK, new files only; all 14 scripts reverse exactly to their bytes as run through `scripts/SCRUB-MAP.json`; the strict public-text scan finds 0 hits here.
- **This note adds one new file**, itself, and `SHA256SUMS-note1` with its sha256. It edits no file.

## The scorer and the readings, as hashed before the read

- `scripts/s03_score.py` as run: `20534e559870b3188b2781482ac1d10bee89fa74c5f82c5afc2087a291e8a31a` (landed with placeholders as `93bdbccaf3b79c80...`; `scripts/SCRUB-MAP.json` maps the two and reverses exactly).
- `READINGS-blind-e221.md`: `44d32b5a76d7024bfbd509c7d2164e8b355cb5a4e56d957edecb8804f67a13c3` (byte-equal here).
- Both were hashed at 17:59:51 PST (`logs/step3-scorer-sha256.txt`), before the first read of any E221 measurement at 18:00:03, and the verifier found both equal to those hashes. The declaration asks for the scorer's hash to be posted with the result; this is that hash.

## verify-blind-e221's findings that touch this folder

1. **The departure in loading one frozen maker (low, process; it confirms this folder's own finding, R9 at line 65 of `READINGS-blind-e221.md`).** A cleanup of the round's old work clones at 16:07 PST removed the clone that posimb's as-run maker scripts import from, so the scoring lane ran the maker's landed copies, as R9 says, hashed before the read. Nothing computed changed: the verifier's own posimb composition, from the landed `f02_private`'s features (re-made 132 of 132 equal) and its own elasticity, re-makes the measured-conditions posimb forecasts here and the declaration's frozen nominal ones bit for bit. The fix belongs to the round's cleanups (skip any folder that a freeze record, a declaration's inputs or a frozen maker's imports name); nothing here changes.
2. **The run selection (info).** The declaration names its form but does not write the selection out; READINGS R1-R2, hashed before the read, take decl-e219's explicit selection. The queue condition removed 0 runs, and 14 capped runs were not read for energy. The T1 misses are 24-26% of each card's cases against a 10% allowance, so no reasonable selection changes the verdict.
3. **aifoundry2 card 0's weak floors (info).** E212's 3 cases set that card's watts band (0.72 W) and ties (0.02 in ln joules, 0.4 W). They decided no rule: all 130 no-twin watts cases are on aifoundry1 card 1. The README's section 3 prints the floors beside, as declared.
4. **The conditions (info).** The primary footing's conditions include two window values of each run's primary view (`kclock_mhz`, `rails.minion.mV`), as the declaration names them, so T3 equals T1 by construction (174/236 on aifoundry1 card 1 for both, and so on), as the README says.
5. **The switch counts behind the models (info).** The verifier re-counted 5 points on E221's own kind tiles with its own driver: three fp32 points equal to E210's committed raw points, and two int8 points equal to the committed counts-v2 points but for one count of trace identifiers (256 lower at both), which is not a switch-table input. E221 designs no tile, so no new count enters this score.

## What the verifier did not check

- The freeze post's text on the Discussion itself; fp16 counts; the T2, E2 and E4 band bases (their arithmetic is checked).
- The scoring lane's short inline read-only inspections, which are not files, and whether any lane read the model session's sealed forecast: the lab's files carry its digest only, never a forecast number, and this folder does not name it.

SPDX-License-Identifier: Apache-2.0
