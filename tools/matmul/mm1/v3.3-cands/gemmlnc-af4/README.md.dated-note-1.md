# Dated note 1 to 'MM1-v3.2 + gemmLnc term AF4': its two checks, and how to read the README with them

*Fri 20 Nov 2026, Pacific time. Written by land-cands (round Q234) from 07:40 PST, when E220 had booked no card: no E220 datum
existed, and this lane opened none at any time. Desk only. Every number below comes from the two checks named, which ran on committed
data and on this folder, or from this lane's own comparison of two files (named); each keeps the label its check gave it (desk, post
hoc, held out, REPORTED). This note changes no file of the folder: the README, the declarations, the code, the data, the logs and the
frozen files are committed byte for byte as lnc-form left them.*

## What is committed here, and its freeze line

- **The folder** is lnc-form's land, byte for byte: 43 files and `SHA256SUMS` (sha256 `ef885cb8cdf37dff...`, 43 of 43 OK), last
  written at 05:46:46 PST, before either check began (check-lnc-form at 05:47:38 PST).
- **The frozen files** were written at 05:35:07 PST (mode 444 since) and recorded in the lane's FROZEN.txt at **05:35:36 PST**, before
  any E220 datum (E220's points final 05:24:17 PST). They were posted by their sha256 as post **#1.30.1.2.1** on the owner's coordination
  thread at **05:47:36 PST**. That post is their freeze line:

      5373973ff4ce03175df72801163241cc7015003b8c0fd52e2f0b5cfaf999bfab  FROZEN-e220.txt (the lane's FROZEN.txt, byte for byte)
      3005869e7c490061100b741da2b90f20731b89ea4c0838c09719ca264f538952  forecasts-e220-af4.csv
      37ace71c028a707ef07e9658cfdb2a4b3743ec0498b20b3bae93f79ac6af93e4  forecasts-e220-af4.json

  The term file `term-gemmlnc-af4.json` (`dfcd58a0...`) and the declaration `DECLARED-lnc-form.md` (`7e1c01e4...`, hashed at 05:30:58
  PST, before any fit) are covered by the post only through FROZEN.txt, which lists them. This commit is a later record of them, not
  their freeze line.
- **The fit record and the data table named in FROZEN.txt** are the lane's working copies `work/s02_fit.json` (`e87ae81c...`) and
  `work/s01_points.json` (`cc23fbce...`). Here `data/s01_points.json` is the second byte for byte (`cc23fbce...`), and
  `data/fit-record.json` (`d5aea26a...`) is the first with one string changed (the path in `declared_sha256_file`) and one key added
  (`note`): this lane compared the two files leaf by leaf (3,733 leaves; every number identical; desk), as check-lnc-form had said.
- **Added by this lane** (new files, listed in `SHA256SUMS-note1`): this note.
- **The points:** E220's POINTS.txt (sha256 `058984a0...`, final 05:24:17 PST): 306 rows, arm A's 84 points at 600 MHz on aifoundry1
  card 1 and arm B's 74 at 799, 700 and 600 MHz on aifoundry2 card 0; the term moves the 46 gemmLnc rows (28 points) and leaves the 260
  cooperative rows equal to MM1-v3.2.

## The two checks

**check-lnc-form: HOLDS WITH FIXES** (05:47-06:01 PST; desk; `/usr/bin/python3` 3.12.3). Its fixes are wording only.

- Its own caller re-made all 306 rows from MM1-v3.2 (a git archive of tools/ at GitHub main 0f046200, unchanged since 4e386f75) and the
  term as the declaration's text defines it: the features 46 of 46 bit-equal; the CSV 6,732 of 6,732 cells equal as written; W, J and
  B' differ only by rounding (299 of 306 W bit-equal; at most 3.9e-16 relative from its own arithmetic) and are 46 of 46 bit-equal in
  lnc-form's order; E220's registered planning peak PP32 exact at 158 of 158 points; single-point calls equal the batch call.
- MM1-v3.2's columns equal E220's registered MM1-v3.2 forecasts (reg-e220's local land, `forecast-e220.json`, sha256 `dd317667...`)
  at 306 of 306 rows within 4.6e-12, the file's stored precision.
- POINTS.txt is `058984a0...`, and all 158 points (A 84; B 74 at three clocks) are covered once. No E220 datum existed (GitHub main
  0f046200, no E220 data folder, no booking).
- Its own solver re-made the keep rule exactly: AF4 c1 236.349 pJ, c2 597.345 pJ; LOEO 3.879% against F3 refitted 8.688%; the pooled
  guard 4.9214% against 5.0478% (n 1,851 with the 22 new points; the record 4.9755%, n 1,829); placebo 100 of 100 (median 12.298%,
  min 10.968%). KEPT: AF4, AF3, AF2, AF1; AF4 chosen.
- Every hash posted at #1.30.1.2.1 is exactly right.

**verify-lnc-form: HOLDS WITH FIXES** (06:01-06:30 PST; desk; the same interpreter; single-threaded). Its fixes are wording and scoring
only; no frozen file changes.

- Its own code re-derives AF4 exactly. All 36 points and 30 twins, read from the committed raw data folders, are bit-equal to the lane's
  table (the 14 in-fit points equal MM1-v3.2's energy points; E218's raw re-reduction equals the committed W to 7e-15). The base agrees
  within 3.6e-15 W, S within 4.4e-16, the features exactly. The walk confirms dup = 26 (14 A + 12 B) and phi at 11 of 11 shapes (on
  the desk's L2, 100% of duplicate reads hit).
- The fit by an exact solver: c1 236.35, c2 597.34 pJ; LOEO 3.88% (bias +0.14) against F3 refitted 8.69%; folds E211 8.45, E213 5.79,
  E215 2.96, E216 1.54, E218 2.84%; LOCO aifoundry3 4.74, aifoundry2 1.54, card 1 8.93%; LOPO 3.71%; pooled 5.048 -> 4.921%; placebo
  100 of 100.
- E220: the 46 gemmLnc rows re-made within 3.9e-16 relative, the 260 cooperative rows exactly; AF4 minus MM1-v3.2 -1.644 to +5.880 W.
- The result survives nine sampler readings (AF4 3.82-4.18%; F3 refitted 8.51-8.98%), twin-corrected bases (3.90%, 3.91%), the die in
  the window (3.93%), D = 1 (3.79%) and the fold-base footing (3.90%); within-group placebos 100 of 100 (four kinds). The NoC rails split
  the regimes on every card (gemmLnc minus its twin: R4 = 0 points 0.29-0.70 W, n 14; R4 > 0 points 1.19-4.51 W, n 16).

## Read the README with these corrections

The README, the declarations and FROZEN-e220.txt are not edited. Where they say otherwise, these readings stand.

1. **The distance the m step uses** (verify-lnc-form, medium). AF4's m tests whether 3 KB (in MB: 36 MB at KB 12) passes x1, but the walk's exact
   LRU and MM1-v3.2's map both give A's near-reuse distance as (3 + u) KB + 2 MB. At KB 12, exactly E216's g01-g06 and the only integer KB
   where the two disagree, that is 38-50 MB: the walk holds none of A under x1 (its strict-L3 hit share is 0.000) and the map puts A
   89-94% fresh, yet m = 0. With m at the walk's distance, LOEO goes 3.88 -> 6.39% and E216's fold 1.54 -> 8.70%. The data place the
   edge in 36 < 3 KB <= 42 MB (LOEO stays 3.88% across that window). Read the README's "3 KB = 36 MB at KB 12" (section 5, "The
   edges") as: *m uses 3 KB, which departs from the walk's and the map's distance; E216's fold tests the constants on an edge set after
   E216 was seen, not the edge itself.* No E220 forecast depends on the difference.
2. **What the frozen W over idle is** (verify-lnc-form, medium, scoring). `W_over_idle` in the frozen files is W at MM1-v3.2's forecast
   op time, which is wrong by regime at gemmLnc (measured over forecast op time 1.04-1.24 at the L3 edge, 0.87-0.92 where A is reused).
   In sample, W at the forecast t errs +8.9% (L3 edge) and -8.2% (A reused); W given the measured t errs -3.0% and +1.6%; J with t
   forecast -3.5% and +2.7%. Read W at the forecast t as *a time-plus-energy quantity*. The README's "the 'with t forecast' joules carry
   that time error" (section 5, "Time") overstates it: J carries only the A/W share of it (about 4% with the clock pinned, 21% on
   aifoundry2). The time-error ranges there read *4-24% slower* (near-reuse miss) and *8-13% faster* (A reused), not 12-24% and 9-13%.
3. **The safety numbers** (verify-lnc-form, medium; check-lnc-form, nit). In the L3-edge regime the G2 and arm B safety numbers are
   likely high: a run 4-24% slower than MM1-v3.2's op time reads about 33-38 W over idle, not 39.5-40.0 W, so the safety note is
   conservative there. MM1-v3.2's own W at arm B's 799 MHz gemmLnc rows is **33.99-34.83 W** (xg04 34.83 W), not "34.0-34.5 W"
   (README lines 41 and 274, and FROZEN-e220.txt's SAFETY line, an information line kept as hashed); the AF4 and planning-peak numbers
   on those lines are right.
4. **The size of AF4's move** (check-lnc-form, nit). At the registered clocks AF4 moves MM1-v3.2's W over idle by **-1.64 W** (xg09,
   arm A) to **+5.88 W** (n01, arm B at 799 MHz): read "-1.6 to +5.9 W" for README line 39's "-1.7 to +5.9 W". README line 267: the
   NB-1 points (xg09, xg10, xg12) sit **1.57-1.64 W** below MM1-v3.2, not "1.6-1.7 W". The G2 block sits +4.16 to +4.90 W (arm A) and
   +4.99 to +5.88 W (arm B at 799 MHz) above it.
5. **The rails** (verify-lnc-form, nit). README lines 74-75, "+0.49 to +0.70 W at every R4-0 point on all three cards", leave out the
   L2-resident pair (a087 +0.29 W; k40 +0.31 to +0.38 W, card 1's only R4-0 point), and within R4 > 0 the rails do not follow R4. Read:
   *the rails corroborate the split between the regimes, not the size of the term.*
6. **No card factor** (verify-lnc-form, low). Card 1's measured excess is 1.20-1.30 times aifoundry3's at the same configuration
   (k37/a075, k40/a087), and card 1's LOEO bias is -8.6%. E220's arm A holds 19 of its 28 gemmLnc points on card 1: expect arm A to
   read high against the term. A declared card factor is for v3.3.
7. **The placebo's row order** (verify-lnc-form, low). The placebo's draws depend on the table's row order, which the declaration does
   not fix. In lnc-form's order (`data/s01_points.json`) the verifier's solver and bvls reproduce its numbers; in another order AF4's
   minimum is 11.64% and F2r scores 34-35 of 100. AF4 is 100 of 100 in both. Read the placebo record as *in the row order of
   data/s01_points.json*.
8. **F2r's placebo** (check-lnc-form, nit; REPORTED only). In 5 of the 100 draws (j = 0, 3, 42, 53, 69) the E218 fold's training
   columns are collinear (the permuted beyond equals 26 = dup), and two solvers (bvls and an exact active-set solver) reach the same
   objective with different held-out E218 forecasts, so F2r wins 41 or 36 times. F2r is not kept either way; a later declaration needs a tie rule (minimum norm).
9. **The A-reused regime** (verify-lnc-form, low). AF4 reads +1.55% high in sample there (15 points; c1 is 236 pJ, against 207 pJ from
   those points alone). n01 and n05 (MB 1, NB 6, m 1) sit in a corner with no committed point.

## For E220's scores (REPORTED; not a freeze, not a rule)

- Score the term on W given the measured t and on J, not on the frozen W at MM1-v3.2's forecast op time (item 2).
- Score XG apart from G2: XG's gemmLnc points (arm A's twelve; arm B's xg04 and xg08) are E218's configurations, which are in AF4's fit
  (measured on aifoundry3), so on these two cards they test the term's transfer; the G2 block (n01-n07) never ran on any card, a
  shape-blind test of AF4's L3-edge clause. Score n01 and n05 apart within G2 (item 9), and the two arms apart (item 6).
- The pooled guard cannot see the cooperative points (the term is 0 there and MM1-v3.2 was not refitted): it restates the margin rule
  (verify-lnc-form, info).

## NOT RUN

- verify-lnc-form: a refit of MM1-v3.2's constants with AF4; the gemmLnc smokes; a raw-telemetry re-reduction of E211, E213 and E215
  (their committed run fields were read).
- check-lnc-form: the 36-point table re-derived from the committed data folders (verify-lnc-form did it).
- This lane re-ran no number. It copied the folder, checked its hashes against the posted ones, compared the fit record with its
  landed copy, added this note, ran the public-text scans, and committed.
