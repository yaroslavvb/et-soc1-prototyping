# blind-e217-scores: dated note 1, the folder as landed and verify-blind-e217's findings on it

*Thu 19 Nov 2026, Pacific time. Written by the lab's lane land-blind-e217 (round Q228) at 22:22 PST for this folder's commit, after verify-blind-e217 held it WITH FIXES (21:19-21:56 PST). Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), single-threaded inside the round's CPU slots. This note changes no file of the folder and no verdict, count or rule; the four figures it corrects are printing slips, and nothing in it is a measurement.*

## What is committed here

- **The folder** is blind-e217's land byte for byte: 42 files and `SHA256SUMS` (sha256 `15918e9b6c6db547...`, 42 of 42 OK), written at 21:16:32 PST.
- **The verification.** verify-blind-e217 re-derived the score with its own code:
  - its own caller made the measured-conditions forecasts: 36,494 fields bit-equal to `forecasts-blind-e217.json` (`74aa5a03...`);
  - its own run list from the committed data equals the declaration's 599 runs and 486 cases (0 field differences), and MM1-v3.1's own loader agrees on 7,775 values;
  - its own scorer, written from the declaration alone, gives the same verdict (FAIL: part A FAIL, part S PASS) and the same missed cases under each of the 14 part-A rules (the nearest case to a band edge is 2.4e-5 away); part S's 128 per-case values agree within 2.2e-16, D1-D3 agree in 75 of 75 entries, D4 and the nominal footing agree;
  - every session is BLIND: the freeze post #13.1.1 came 135 to 401 minutes before each session's first card command (14:41:14.595 to 19:06:55.525 PST);
  - the order holds: the conditions read 20:53:41, the forecasts hashed 21:00:04, the scorer hashed 21:06:37 (`2921d487...`, unchanged when it ran), the read 21:06:44;
  - this folder holds new files only, and the round's strict public-text scan finds nothing in it.
- **Its one fix for this folder** is its finding 5, below. None changes a number that decides anything.
- **The declaration** this score follows is `../blind-e217/`, landed first as commit `14158948` (committed 22:21:26 PST), with its own dated note 1.
- **This note** and `SHA256SUMS-note1` (its sha256) are the only new files beside the land.

## The README's figures at full precision (verify-blind-e217's finding 5, nit)

The scorer stores each rms and bias at 3 decimals (watts at 4), and the README prints them at 2. A figure whose stored third decimal is 5 can therefore be rounded twice. land-blind-e217 re-ran the hashed scorer on a copy of blind-e217's inputs with only that storage rounding removed (its functions `st()` and `sta()`), and the post hoc step the same way. The E217 data were read from the same commit (`9f8b66bf`). Then the README builder, unchanged, wrote a README from that re-run.

- **The re-run equals this folder.** In `scores/scores-blind-e217.json`, 30,966 leaves are equal and every one of its 27,344 statistics rounds back to the landed value. Nothing else differs but the re-run's two time stamps. In `scores/posthoc-e217.json`, 1,047 leaves are equal and 2 round back. Both CSVs under `cases/` are byte for byte the same. So no verdict, count, p or missed case depends on the rounding.
- **Four printed figures change.** Read them as:

| README line | figure | printed | full precision | read as |
|---|---|---|---|---|
| 44 | MM1-v3: J over idle given t (E1), rms, no twin, pooled (the headline table) | 5.18% | 5.1855% | 5.19% |
| 45 | MM1-v2: J at rest given t (E3), rms, no twin, pooled (the headline table) | 2.58% | 2.5854% | 2.59% |
| 57 | MM1-v3.1, aifoundry1 card 0: the counter mean (T2), bias, no twin (the per-card table) | +3.65 | +3.6553 | +3.66 |
| 136 | the nominal footing, MM1-v3.1: wall cycles (T1), bias, no twin, pooled (section 5) | +2.29 | +2.2849 | +2.28 |

The first two are the verifier's. The re-run found the other two. Every other number in the README prints the same at full precision.

- **T1 and T3.** Line 52's "the same rms and bias on every scope: True" was decided on the stored 3-decimal statistics. At full precision the 162 rms and bias pairs differ by at most 7.4e-15 percentage points. That is floating-point rounding between seconds and cycles, so the sentence holds; the re-run's README prints False only because it compares exact floats.

## The measured conditions (verify-blind-e217's info finding)

The README (line 158) calls the conditions read "start-of-run fields only". As the declaration's field list says (`../blind-e217/DECLARED-blind-e217.md` line 62), they also include two window values of each run's primary view, `kclock_mhz` and `rails.minion.mV`, beside the start die.

- So T3 equals T1 by construction, and card 0 is forecast at its in-run governed clock and volts.
- The nominal footing (section 5), frozen before any datum, is the prior check, and it fails more widely.
- Nothing changes: it was declared.

## Three README sentences, as of this commit

- Section 7, "decl-e217's own land ... is not on GitHub main at this writing": it landed first, as `14158948`.
- Section 7, "NOT RUN here: no second, independent scorer": verify-blind-e217 has since been that scorer (above).
- Line 3, "Nothing here is committed by this lane": this folder is committed by land-blind-e217, byte for byte.

## What the verifier did not check

- The freeze post's exact second (12:25:56 or 12:26:07 PST): either is at least 135 minutes before E217's first card command.
- The energy twin keys (used as frozen, `3418b7d8...`), the T2, E2, E3, E4 and watts band bases, the counts of the other 17 new rows, and 32 of the 125 walk configurations.

SPDX-License-Identifier: Apache-2.0
