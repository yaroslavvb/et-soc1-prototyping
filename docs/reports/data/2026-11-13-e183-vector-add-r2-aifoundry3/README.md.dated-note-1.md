# E183's data README, dated note 1 (Sat 14 Nov 2026; after the data verifier): T3's opening anchor reads low on four board-meter dip samples, and no train reading moves (post hoc); line 108 wrongly groups note M2 with the arms read through the gate, and M2-4's scoring is still owed; T2's half-width is 0.0149 W; the build log's committed path; the carry-over figure is c, the difference over twice the estimate; the card lock and `timeout 10` in the code each block pinned; lines for the records

*Written on aifoundry2 from about 15:10 PST on Sat 14 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e183g` of Q173, after E183's data verifier `verify-e183g` (Sat 14 Nov 2026, 14:42-15:05 PST: holds with fixes;
two low findings, three nits and two notes, none of them a fault in a datum, a scored figure or a verdict; every registered verdict
re-derived from the raw files by its own code; the kit's reducer, scorer and note M1's reader re-run byte for byte). [`README.md`](README.md) and
[`SHA256SUMS`](SHA256SUMS) (lab `39970848`, git 16:43:38 PST Fri 13 Nov 2026) stay as committed, and so do note M1, its two outputs and
`SHA256SUMS-m1` (`49a4152e`, git 16:44:45 PST). **No number, rule, verdict or gate reading changes, and nothing is scored.** The figures
come from [`posthoc_note1_e183.py`](posthoc_note1_e183.py), which reads only committed files: this directory's six train blocks,
`reduced-e183.json`, `scored-e183.json`, `SHA256SUMS`, and as text `README.md`, note M1 and its two outputs (of october-forecast-model only
the version ids in their freeze lines); and, as text, the kit's and the lab's files whose lines its section 0 anchors, with the sha256 of
four kit files. It imports no lab module. Its output is [`posthoc-note1-e183.txt`](posthoc-note1-e183.txt) and
[`posthoc-note1-e183.json`](posthoc-note1-e183.json) ("output §" below is that output's), and a re-run from this tree writes both byte for
byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins
this note, the script, its two outputs, `README.md`, `SHA256SUMS`, note M1 and `SHA256SUMS-m1`, so the line numbers below refer to their
committed bytes; with `SHA256SUMS` (105 entries) and `SHA256SUMS-m1` (3), every file here is pinned but `SHA256SUMS-note1` itself.
Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E183.md, its notes and the kit as committed), **measured**
(the session's committed files), **desk check of code**, **post hoc** (desk readings after the data, deciding nothing).*

## 1. T3's opening anchor reads low on four board-meter dip samples; no train reading moves (low; post hoc)

The README reports the anchors (lines 96-99): fadd.ps random − fadd.ps zeros at each train block's open and close, 12 readings, **+8.493
W [+8.052, +8.935]**, AGREES with E180's RA5 board reading (RA5's mean inside), and T3's opening reading, 6.373 W, the lowest of the twelve.
Their registered reduction is E180's catalogue burst formula over every sample (E183.md section 5.3;
[`reduce_e183_v2.py`](../../../../tools/claims-v3/e183/reduce_e183_v2.py) line 130 calls
[`analyze_catalogue.bursts_of`](../../../../workloads/enercat/analyze_catalogue.py), whose lines 59-74 take the board's mean over the busy
window, from 0.5 s after a burst's first launch starts to its last launch's end, less the idle around it, less the leak law's
correction). It has no dip rule. The script re-writes it
line for line and gets `reduced-e183.json`'s 12 readings within 1e-9 W (output § 1).

- **The four samples** (measured): T3's opening random burst holds four samples that E82 A2's rule drops (a sample more than 4 W below
  both samples two steps away: [E82's data README](../2026-10-31-e82-kinds-aifoundry1/README.md) line 304, the rule the trains apply,
  [`e182_stats.py`](../../../../tools/claims-v3/e182/e182_stats.py) lines 19-20 and 110). They come as two pairs at a launch's start:
  24.70 W twice in launch 3 of the burst's eight (20 and 120 ms into it) and 35.30 W twice in launch 8 (13 and 113 ms in), where the
  samples two steps away read 43.16-43.77 W. That is the kind E82 A2 names, the board meter's dip at a launch's start. At each of the four the card's own readings show no step: its clock reads 600 MHz and its minion die 521-522 mV, the
  service processor's board average and minion-rail average hold one value across the pair and rise from the samples before it to those
  after it, and the two launches ran at 4.6098e11 and 4.5751e11 instructions a second, inside the range of block 18310's other 30 anchor
  launches (4.5557e11-4.6187e11) (output § 1).
- **With the dips dropped** (post hoc): the same formula over the block's samples less those E82 A2's rule drops reads T3's opening at
  **8.375 W**; T3's closing reading (1 dip sample, in its zeros burst) moves from 8.930 to 8.570 W and T4's opening (2, in its zeros burst)
  from 9.124 to 8.570 W; the other nine have no dip in their busy windows and do not move. The 12 read **8.584 W, sd 0.121** (registered:
  8.493, sd 0.695), 95% [8.507, 8.661] with the committed reading's own t multiplier (2.200985, its hw over its se, at the same 12
  readings) (output § 1).
- **Against E180's RA5** (+8.455 W [+8.342, +8.568]): the intervals overlap on both readings (the scorer's `intervals_overlap`, AGREES);
  RA5's mean lies inside the registered interval, as line 97 says, and below the post hoc one. The anchors are reported, never a verdict
  (E183.md section 5.3), and their registered reduction keeps every sample, so lines 96-99 stand as printed; the post hoc reading decides
  nothing.
- **No train reading moves:** the trains' launch reading drops these samples by its registered rule (`reduce_e183_v2.py` line 65), and
  none of the 278 samples the rule drops in the six blocks lies inside a launch's reading window, which starts 170 ms after the launch
  does (`e182_stats.py` line 19): 148 fall in a launch's first 170 ms, 7 in an anchor's busy window and 123 elsewhere (output § 2). So
  the six trains read the same with the rule or without it.

## 2. Line 108: note M2's arms were not read through the gate, and their scoring is owed (low)

Lines 108-110 say that october-forecast-model's arms, "E183.md's dated note M1, with its dated note 1, and note M2", are read after this
directory's commit, through the day-2 check v2's gate. The gate read note M1's two arms only: note M1's freeze lines and its reader's two
outputs name **v3 and v4**, and no file in this directory before this note names october-forecast-model v5, v6 or v7 (output § 3).
[Note M2](../../../../tools/claims-v3/e183/E183.md.dated-note-M2.md) registers **v5, v6 and v7** with no reader and no step on the day; its
M2-4 (line 124) places their scoring "after E183's data commit, in a later records round, from the committed data directory's
`scored-e183.json`".

- So lines 108-110 read: **note M1's arms, v3 and v4 (with note M1's dated note 1), are read after this directory's commit, through the
  day-2 check v2's gate ([README.md.dated-note-M1.md](README.md.dated-note-M1.md)); note M2's arms, v5, v6 and v7, have no reader and are
  scored by M2-4's rule in a later records round, from `scored-e183.json`.**
- That scoring had not run when this note was written: it is owed. The records round that runs it, or records why it does not, restates
  none of its readings in public prose. This note scores nothing and restates none of the arms' readings; note M1's outputs stand as
  committed.

## 3. T2's half-width is 0.0149 W (nit)

`scored-e183.json` gives T2's half-width (its `hi` less its `mean`) as **0.014948 W**, 0.0149 at four places; line 62 prints 0.0150. The
other five are as printed: T3 0.0107, T1 0.0117, T4 0.0138, T6 0.0149, T5 0.0059 W (output § 4). E183-TR-H's ratios are the scorer's,
from the unrounded figures, so no word moves.

## 4. The build log's committed path (nit)

Line 161 names `e183-build-logs/2026-11-13/` among the train host's build records. The commit holds
**`logs/e183-build-logs/e183-build-host-start1.txt`**, beside `logs/e183-build-host.txt` and `logs/e183-build-attempts.txt`, and no entry
of `SHA256SUMS` lies under `e183-build-logs/2026-11-13/` (output § 5). Records quote the committed path.

## 5. The carry-over figure is c: the difference over twice the train's estimate (nit)

E183.md section 5.3 (lines 236-237) defines each train's carry-over reading as the mean of L3 − L2 in SFFS quads against the same in
FSSF, "over the train's estimate", and names its model: a first-order carry-over c attenuates every contrast by 1 − c (section 11, line
371, the same). The kit divides the difference by **twice** the estimate
([`score_e183.py`](../../../../tools/claims-v3/e183/score_e183.py) line 151), and README lines 103-104 say so.

- **Under that model** (desk algebra): a launch reads (1 − c) times its own kind's level plus c times the level of the launch before it.
  In an SFFS quad (S F F S) L2 is an F after an S and L3 an F after an F, so L3 − L2 = c (F − S); in an FSSF quad L3 − L2 = −c (F − S);
  their difference is 2c (F − S), while each quad, and so the train's estimate, reads (1 − c)(F − S). The difference over twice the
  estimate is c / (1 − c), which is c to first order; over the estimate alone it is about 2c.
- So the figure the kit prints and the README quotes is the c that section 5.3 names: T3 +0.089, T1 +0.050, T4 −0.454, T6 +0.071, T2
  +0.011, T5 −0.037, each equal to `scored-e183.json`'s and to the README's; the difference over the estimate alone would read twice
  each (T3 +0.178) (output § 6). No number changes: records call the figure c and give the kit's divisor.

## 6. The card lock and `timeout 10` in the code each block pinned (the verifier's open item; desk check of code)

Lines 33-36 say that the kit takes the card's lock for each block (`lib.sh`) and runs every device process under `timeout 10`, the kit's
design, which this session's files do not print; the verifier recorded the check as not run. Read in the code itself: each of the six
blocks' `code.sha256`, which `lib.sh`'s `block_begin` writes at the block's start (line 189), pins `tools/claims-v3/lib.sh`,
`block_e183_v3.sh`, `run_e183.py` and `session_e183_v3.sh` at their committed bytes (output § 7). In them, `block_begin` (line 179), when
the machine's advisory lock file `/run/lock/etsoc-shire${V3_DEVICE:-0}.lock` exists and the pass is not a dry one, takes it with `flock -n`,
holds it until the block exits, and exits 3 when another process holds it (lines 183-185); `lib.sh`'s `hold10` caps a device process at
`timeout 10` (line 100); `run_e183.py` starts each anchor burst and each train process as `timeout 10 <host>` (lines 290 and 312); and
the session's two config reads run under the card's lock with `timeout 10` (`session_e183_v3.sh` line 57). So the code each block ran
holds both; whether each took effect on the day, the lock file's presence included, the session's files do not print.

## 7. Lines for the records

1. **The anchors** (reported): 12 readings +8.493 W [+8.052, +8.935], AGREES with E180's RA5 by overlap, RA5's mean inside. T3's opening
   6.373 W rests on four board-meter dip samples of E82 A2's kind in its random burst, which the registered reduction keeps; with the dips
   dropped (post hoc, deciding nothing) it reads 8.375 W, and the 12 read 8.584 W (sd 0.121) [8.507, 8.661], AGREES by overlap, RA5's mean
   below. No train reading moves: no dropped sample lies inside a train launch's reading window (§ 1).
2. **october-forecast-model:** note M1's arms, v3 and v4, were read through the day-2 check v2's gate (README.md.dated-note-M1.md); note
   M2's arms, v5, v6 and v7, have no reader and are owed M2-4's scoring in a later records round, its readings kept out of public prose
   (§ 2).
3. **T2's half-width:** 0.0149 W (0.014948) (§ 3).
4. **The build log:** `logs/e183-build-logs/e183-build-host-start1.txt` (§ 4).
5. **The carry-over:** c, the kit's figure, the SFFS-less-FSSF difference of the mean L3 − L2 over twice the train's estimate: T3
   +0.089, T1 +0.050, T4 −0.454, T6 +0.071, T2 +0.011, T5 −0.037 (§ 5).
6. **The card lock and `timeout 10`:** in the code every block pinned (desk check of code; the lock whenever the machine's lock file
   exists); the session's files print neither (§ 6).

## What does not change

Every reading, verdict, gate, stop and figure of `README.md`, note M1 and their files stands. The exceptions are the printed details §§ 2-4
correct (line 108's grouping, line 62's T2 half-width, line 161's path) and the readings §§ 1, 5 and 6 explain. The reducer, the scorer
and note M1's reader read none of this note's files. With the five new files in this directory (this note, the script, its two outputs
and `SHA256SUMS-note1`), before the commit:
- `SHA256SUMS` read 105 of 105 OK, `SHA256SUMS-m1` 3 of 3 and `SHA256SUMS-note1` 8 of 8; the directory held 116 files, and every one but
  `SHA256SUMS-note1` was in one of the three lists;
- the post hoc script, run from a copy and again into an empty folder, wrote its two outputs byte for byte;
- the desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the lane's folders forbidden) read the five new files with 0 hits,
  and a login check found no home path, no login and no holder line in them;
- the public-text scan (`sanitize_extracts.py`'s fixed list and the box's local table, and a list of private, vendor and mechanism words)
  found nothing in the five new files or in this commit's subject and body.

SPDX-License-Identifier: Apache-2.0
