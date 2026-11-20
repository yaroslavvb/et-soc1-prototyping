# Dated note 1 to 'MM1-v3.2 + posimb': its two checks, and how to read the README with them

*Fri 20 Nov 2026, Pacific time. Written by land-cands (round Q234) from 07:38 PST, when E220 had booked no card: no E220 datum
existed, and this lane opened none at any time. Desk only. Every number below comes from the two checks named, which ran on committed
data and on this folder; each keeps the label its check gave it (desk, post hoc, held out, REPORTED). This note changes no file of the
folder: the README, the declaration, the code, the outputs and the three frozen forecast files are committed byte for byte as layout2
left them.*

## What is committed here, and its freeze line

- **The folder** is layout2's land, byte for byte: 34 files and `SHA256SUMS` (sha256 `acef395141bb0ca1...`, 34 of 34 OK), last
  written at 05:45:06 PST, before either check began (check-layout2 at 05:47 PST).
- **The frozen forecasts**, final at **05:39:30 PST** (the lane's FROZEN.txt written 05:39:48 PST), before any E220 datum, were posted
  by their sha256 with FROZEN.txt's as post **#1.30.1.2.1** on the owner's coordination thread at **05:47:36 PST**. That post is their
  freeze line:

      81d04c97af0ecf69e16d2a7a17141e0ca0bdf7ce57ebfd9cc42a3440516dd85f  FROZEN-e220.txt (the lane's FROZEN.txt)
      1de81ec510573d184c960234f83f0ed51881a5b17b7e8ce75aa3702925e86182  forecasts-e220-posimb.csv
      3010f28c7e47e754a8bc4da5d0742e0d515c85da8d59e70a4ee3b798ccca1034  forecasts-e220-posimb.json
      1a25dd62d09f2e780bd5159e9289e95ca776b3a766a03ba99ebcd956739bacd4  forecasts-e220-posimb.txt

  FROZEN.txt also names `DECLARED-posimb.md` (sha256 `a7cd74a06da23523...`), hashed at 05:35:31 PST before any fit. This commit is a
  later record of them, not their freeze line.
- **Added by this lane** (new files, listed in `SHA256SUMS-note1`): `FROZEN-e220.txt`, the lane's FROZEN.txt byte for byte, so that
  the posted FROZEN.txt sha256 can be checked here (its "OUT/..." paths name the round's desk folders, not files of this repository);
  and this note.
- **The points:** E220's POINTS.txt (sha256 `058984a0...`, final 05:24:17 PST) and points-e220.csv (`64a7c99a...`): 306 rows, arm A's
  84 points at 600 MHz on aifoundry1 card 1 and arm B's 74 at 799, 700 and 600 MHz on aifoundry2 card 0. 100 rows are in the term's
  scope (the XY and Y2 subset points); every other row is MM1-v3.2's to the last bit.

## The two checks

**check-layout2: HOLDS** (05:47-06:05 PST; desk; `/usr/bin/python3` 3.12.3, numpy 1.26.4; six jobs, single-threaded, in the round's
CPU slots).

- Its own caller re-made the frozen forecasts bit for bit: 306 of 306 rows in all 29 numeric columns of the CSV and the JSON, and the
  .txt rendered again byte for byte. The caller parses POINTS.txt itself, makes one MM1-v3.2 call for all 306 rows (tools/ at GitHub
  main 0f046200), computes its own elasticity, and takes the two shares from the committed LRU walk and each tile's sharers. 100 rows
  are in scope (= the folder's own test); the 206 others equal MM1-v3.2 in every cell.
- The features at E220's 25 configurations are bit-equal from its own code.
- MM1-v3.2's columns equal reg-e220's registered MM1-v3.2 forecast (`forecast-e220.csv`, sha256 `082e3d9c...`, as reg-e220 rewrote it
  at 05:53:22 PST) at 306 of 306 rows, within 4.8e-9 relative (the folder says 5e-9).
- KEPT follows from the folder's numbers: K1 0.0329 <= 0.0375, K2 5.733% <= 5.788%, K3 100 of 100. Its own fits on the stored bases
  and features give M1, M2 and the placebo count exactly as stored (the constants within 1 ulp); Phi, e and the base at the 30 pair
  points are bit-equal; a_lag > 0 in 32 of 32 folds, a_hop in 31 of 32.
- Every hash is as stated; `SHA256SUMS` 34 of 34.

**verify-layout2: HOLDS WITH FIXES** (06:05-06:31 PST; desk; the same interpreter; seven jobs, single-threaded, in slots; its inputs its
own extraction of GitHub main 0f046200).

- Re-made with its own code, and equal to layout2's: the measured op times (MM1-v3.2's table for 2,508 points; E216 and E218 from their
  raw runs); MM1-v3.2's base and elasticity at its all-data constants and at 27 fold constants (bit-equal, through MM1-v3.2's own
  engine); the features from its own generator and LRU (which agrees with the walk's stack distances 8 of 8) at all 306 configurations
  and the 100 frozen rows (largest difference 0); the constants (a_hop 0.1333333, a_lag 0.4367172, within 2e-16), M1, M2, the placebo,
  LOCO, LOLO and K1-K3 (KEPT); and the 306 frozen rows from the declared form, within 2.2e-16.
- The lead's effects are real: the clock (ln of the clock ratio at most 2.4e-4 at every lead pair), the die, the run order and the
  sampler's window do not explain them (the window view equals the 800 MHz band view within 0.001 ln).
- Its fixes are claims and labels. No number and no hash changes.

## Read the README with these corrections

The README and the declaration are not edited. Where they say otherwise, these readings stand.

1. **What the term means** (verify-layout2, medium). The physical reading, *the slowest active shire's excess when the DRAM stream is
   private*, is **not established**. 57 of 200 random mesh maps (the private and shared shares kept) also pass K1 (19 of 200 reach M1
   <= 0.0329; median 0.0411), because the sign at the 8 pairs the term helps comes from the private-share indicator, which every map
   keeps; a permutation within (shire count, shape) reaches the real M1 in 0 of 200 (min 0.0399). The lag channel puts 0.018-0.022 ln
   of wall over mean at 7 of the 15 lead pairs where the counters read 0, and E218 y02-y06's +0.042 is all in the counter's mean (the
   imbalance part is non-zero at 4 of the 15 lead pairs). Read a_lag as *a fitted 'private DRAM stream x spread' factor on the wall*,
   and the position and imbalance readings as hypotheses that K1 does not establish.
2. **What K1 tests** (verify-layout2, medium). Read K1 as *form post hoc, constants held out*: the form was chosen after in-sample
   looks at the same pairs (as the declaration discloses), and only the constants are held out. E220's layout pairs reuse the lead's
   mask pairs (0x3 against 0x10001, 0x101 against 0x10001, E218's Y pairs), so E220 tests the term's transfer to other cards, not new
   layouts.
3. **Little gain outside the lead** (verify-layout2, medium). Over 215 equal-count pairs outside the lead (LOEO) the rms goes only
   0.0784 -> 0.0766 ln. E217 gets worse, 0.0832 -> 0.0877, with the sign right at 20 of its 47 large calls; the largest misses are
   E217's gemmL2x6x10 at two shires (0.14-0.22 ln either way), where L3-resident masks run slower than DRAM-private ones. On aifoundry1
   card 1 (E220's arm A) the gain was 0.0821 -> 0.0807: expect little there.
4. **K1 is fragile** (verify-layout2, low). E216's pairs alone give a ratio of 0.822 (above the 0.80 margin). With the L3 taken as 48
   MB, M1 is 0.0377 (over 0.0375); at 24 MB, 0.0306. Near forms fail K1 (position-free forms 0.0387-0.0464; the spread without the
   share 0.0429). a_hop is poorly identified: 0.006 to 0.42 across the leave-one-experiment-out fits of the LO-Y fold, and -0.51 in
   LOLO 'other'.
5. **The placebo** (verify-layout2, low). The declared placebo permutes the features across shire counts and shapes. The term also
   beats a placebo permuted within (count, shape) 200 of 200 times, but a random-map placebo only 181 of 200. A v3.3 keep rule should
   declare both.
6. **The sign counts** (check-layout2 and verify-layout2, low). The "4 right" counted for count-only (and for MM1-v3.2) come from
   MM1-v3.2's pair predictions of +1.0e-9 ln (E216 y04; E218 y01-y06), not real sign calls: read *MM1-v3.2 and count-only predict no
   difference (|ln| <= 1e-9) at all 15 pairs*. posimb's 10 of 15 counts by strict sign: its zero predictions at E218 y07 and y08 count
   as misses, and 10 of its 13 non-zero calls are right (wrong: E216 y04, y05, y06).

## A sentence added to the declaration's disclosure (check-layout2, low)

`scripts/x04_imbalance.py` wrote its output (the lane's work/imbalance_x04.json; `out/imbalance_x04.json` here) at 05:32:49 PST,
before the declaration was hashed at 05:35:31 PST. That file holds the two shares Fp and Fs (read from a `private_shared.json` that was
still being written) beside MM1-v3.2's wall residual and ln(wall / mean) at 546 of the 640 subset points. The code computed and printed
no comparison of them. The declaration says the features' values were computed but not compared with any residual before its hash; this
sentence adds that, in that one file, they sat beside the residuals before the hash.

## For E220's scores (REPORTED; not a freeze, not a rule)

- Score posimb on the pair differences, ln(a/b), and give the levels apart: in the LO-Y fold the Y points' own levels did not improve
  (7.06% -> 7.12%); only the differences within pairs did.
- The frozen pair predictions, the same on both arms and at every clock: p01-p03 +0.0289, p04-p05 +0.0042, xy01 -0.0352, xy02 and
  xy04-xy06 +0.0226 to +0.0229, xy07-xy08 0. MM1-v3.2 predicts 0 (or 1e-9) at all of them. xy03 has one registered member (xy03b, as in
  E218), so it has no pair prediction: not a gap in coverage (check-layout2, info).
- Watch E220's 600 MHz columns (verify-layout2, info): in E216's single-launch 600 MHz views y03 read -0.006, against +0.040 at 800
  MHz; the term forecasts +0.029 at every clock (thin evidence: one or two first launches).
- E220's counter-mean rule may miss at the XY 'a' points with MB >= 2 (xy01a, xy04a, xy05a, xy06a; R1C4 masks) for MM1-v3.2 and for
  every candidate built on it (layout2's own note: E218's same points missed by -13 to -24%); the term does not touch the counter's
  mean there.

## NOT RUN

- verify-layout2: an independent re-implementation of MM1-v3.2's engine (the base was rebuilt with MM1-v3.2's own engine at its stored
  constants); 20 E217 cases and 2 E219 cases (sparse50i kind names, anchors) were not checked against the session data (they equal
  the case tables layout2 used).
- layout2: a joint refit with MM1-v3.2's time constants.
- This lane re-ran no number. It copied the folder, checked its hashes against the posted ones, added `FROZEN-e220.txt` and this note,
  ran the public-text scans, and committed.
