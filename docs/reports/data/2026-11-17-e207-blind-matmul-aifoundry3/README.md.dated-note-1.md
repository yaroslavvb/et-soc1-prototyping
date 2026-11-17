# E207 data, dated note 1: step 6n's one TO DATE point, b50, dated after MM1-v1's freeze by its sessions' own start records - it stays in every rule

*Tue 17 Nov 2026 (week 47), PST. Written by Q199's card lane `card-e207` before this directory's data commit, as E207.md's amendment A1
(items 2 and 3) and CARD-LANE-BRIEF.md row 12 (b) ask when step 6n names a TO DATE point. A desk reading of records (file paths, file times
and two sessions' own start lines); no rule, band, forecast, label rule or scorer is changed. Every time is Pacific.*

## What step 6n printed

Step 6n (the never-run search, repeated right before the first card command) ran from 07:04:47 PST; its report is dated 07:06:00 PST, and the
session's first card command followed at 07:06:44 PST. Its line: **"NEVER-RUN 52 of 53 points, 46 of 47 cases; TO DATE: b50; DESK-ONLY
(dismissed): b04 b15 b25"**. Its full report is `neverrun-e207-card.txt`, `neverrun-e207-card.json` and `ranbefore-e207-card.json` in this
directory. Its proposal named one point to label (b50) and no case.

## The TO DATE point: b50

b50 is gemmL1x3x2 in fp16 on all 32 shires, with the data kind `real:blind4`, which is given to the host as tile files. Its case is
`gemmL1x3x2|fp16|0xffffffff`, which also holds b03. Step 6n's matching, as registered (`kind_scan` in `desk/neverrun_card_e207.py`), reads
every data kind given as tile files as one kind (`tiles:other`). So it counted runs of the same shape, format and mask with **`ones` tiles**
as records of b50's key, although `ones` is not b50's own data kind. Those runs are in four files, all in the lab's data lane folder
`OUT/data-e212`. That lane holds copies of E212's sessions for the lab's check before their data commit. E212 is the model session's second
matmul sweep (1117-mmsweep2, registered from its post #11 of 05:22:43 PST Tue 17 Nov 2026), run on aifoundry1. The four files are two files
and their staged copies. Step 6n could not date them, since no session start is in their paths and each was last written after the freeze.
The kit asks for the session's own start record, which reads as follows:

| file (relative to the round's folder) | step 6n's dating | its session's own record (`session.log` in the same session folder) |
|---|---|---|
| `OUT/data-e212/work/a1c1-S1/session/runs/004-1x3x2-fp16-ones/proc-00.out` | TO DATE: last written 2026-11-17 05:33:16 PST; no session start in its path | "2026-11-17 05:30:01 PST session start (T0 1794922201; card a1c1, aifoundry1 card 1; ...)"; the run 004-1x3x2-fp16-ones at 05:32:59-05:33:21 PST (rc 0, check exact); "2026-11-17 06:06:39 PST session end" |
| `OUT/data-e212/work/a1c1-S1/stage/2026-11-17-e212-mmsweep2-a1c1-S1/session/runs/004-1x3x2-fp16-ones/proc-00.out` | the same: the data lane's staged copy of the file above | the same session |
| `OUT/data-e212/work/a1c0-S1/session/runs/003-1x3x2-fp16-ones/proc-00.out` | TO DATE: last written 2026-11-17 06:18:57 PST; no session start in its path | "2026-11-17 06:16:04 PST session start (T0 1794924964; card a1c0, aifoundry1 card 0; ...)"; the run 003-1x3x2-fp16-ones at 06:18:41-06:19:02 PST (rc 0, check exact); "2026-11-17 06:52:08 PST session end" |
| `OUT/data-e212/work/a1c0-S1/stage/2026-11-17-e212-mmsweep2-a1c0-S1/session/runs/003-1x3x2-fp16-ones/proc-00.out` | the same: the staged copy of the file above | the same session |

**The reading (E207.md A1 item 2).** Both sessions started after MM1-v1's freeze, which was 21:14:57 PST Mon 16 Nov 2026 (`25d2e74e`). They
started at 05:30:01 and 06:16:04 PST Tue 17 Nov 2026, on aifoundry1 cards 1 and 0. Every record step 6n counted for b50 is therefore **AFTER THE
FREEZE**: b50 stays in every rule, and its case stays in the time rules. MM1-v1's, F1's and F2's forecasts for b50 were frozen before any of
those runs. In its own data kind (`real:blind4`), b50 had no card record before this session that step 6n found. No point and no case is
labelled.

**The final labels** (`ranbefore-e207-labels.json`, beside this note) list no point and no case. That file takes the place of step 6n's
proposal for the after-score tool (`postscore_e207.py` reads the final file first). The proposal is kept, unchanged, in
`ranbefore-e207-card.json`.

## The rest of step 6n's report (unchanged; repeated here for the reader)

- **DESK-ONLY (dismissed by A1 item 1):** b04, b15 and b25 in `OUT/fix-e211`, `OUT/kit-e211` and `OUT/verify-e211`, which hold E211's desk
  tests on doubles, and one case (gemmL1x7x6 in fp32) in `OUT/kit-e209`, which holds E209's desk test. None of these is a card run.
- **Not searched, as registered:** aifoundry1's own folders, and the model session's own work folders (`ee-*`, the orchestrator's rule of
  23:18:35 PST Mon 16 Nov 2026). E208's planned arms were read at their registered bytes (`b55f5e13...`). aifoundry3's run folders were
  searched: 40,255 files, none in E207's own `build/e207`.
- **Where the dating came from:** the two sessions' start, run and end lines were read, read-only, from `session.log` in the data lane's
  copies named above. No other file of those sessions was read for this note, and no operand-pattern arm was read.

SPDX-License-Identifier: Apache-2.0
