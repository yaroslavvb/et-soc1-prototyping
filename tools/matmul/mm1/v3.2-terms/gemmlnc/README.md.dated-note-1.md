# Dated note 1 to the gemmLnc term: its two checks, and how to read the README with them

*Thu 19 Nov 2026, Pacific time. Written by land-terms (round Q225) from 12:07 PST, before this lane read any E215 datum (it read
none at any time). Desk only. Every number below comes from the two checks named, which ran on committed data and on this folder;
each is labelled **desk**, **post hoc**, **held out** or **REPORTED** as the checks labelled it. This note changes no file of the
folder: the README, the code, the work files and the three frozen files are committed byte for byte as lnc-energy left them.*

## What is committed here, and its freeze line

- **The folder** is lnc-energy's land, byte for byte: 22 files and `SHA256SUMS` (sha256 `0f671361506bfcc9...`, 22 of 22 OK), last
  written at 09:34:30 PST, before either check began.
- **The three frozen files**, final at **09:30:36 PST** before any E215 datum, were posted by their sha256 as post **#1.29** on the
  owner's coordination thread at **09:32:02 PST** (before check-lnc ran). That post is their freeze line:

      00fcaf5dd05e7af5a95ce1b783b68588a416dde91d0434f4f82ba6bdee6f5a7c  forecasts-gemmlnc-e215.csv
      feba7e5e70829854169bb3671947767c56c2303c20a74b83c7949bcd6b024e7c  forecasts-gemmlnc-e215.json
      2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4  term-gemmlnc.json

  This commit is a later record of them, not their freeze line. E215's two arms were held from 09:59:39 PST and released at about
  11:55 PST, after both freeze posts.

## The two checks

**check-lnc: HOLDS** (09:36-09:58 PST; desk; `/usr/bin/python3` 3.12.3, numpy 1.26.4).

- An independent caller re-made the three frozen files bit for bit: MM1-v3.1's `predict` called one point at a time from a pinned copy
  of main 8bde0182, and the term written from the equation text in `term-gemmlnc.json`, not from this folder's code. CSV 259 of 259
  cells equal; JSON 434 of 434 number fields equal; the held-out E213 smokes 12 of 12 values; batch and single calls give the same
  bits; MM1-v3.1's base equals its own frozen E215 forecasts.
- The hashes match the lane's record and post #1.29; `SHA256SUMS` 22 of 22.
- No E215 datum was read by lnc-energy (its transcript: 111 tool calls, E215's registration and the frozen forecast files only).
- The term is exactly 0 on gemmL, and the walk at E215's own shapes gives 26 duplicate lines a minion-op on gemmLnc and 0 on gemmL.
- The two constants re-fit from this folder's fit inputs equal the frozen ones, and F3 is the form the declared rule picks.

**verify-lnc: HOLDS WITH FIXES** (09:59-10:25 PST; desk; the same interpreter; every numerical job single-threaded).

- Every number re-derives with its own code: the traffic from `sparsity.c` (832 duplicates a shire-op, 26 a minion-op); the rail
  split from the raw 10 Hz telemetry (all 9 pairs equal Table 2 to the printed digit; 27 of 27 runs equal the committed reducers,
  E211's 9 included); the fit, its folds and the declared selection (F3: 254.4 and 552.1 pJ; in sample 7.99%, leave one point out
  9.81%, leave one run out 9.63%); and the five frozen rows and two smoke rows from the equation text, within 5e-8 W.
- The measured core survives clock, voltage, the instruction census and the sampler's window. Its fixes are wording only.

## Read the README with these corrections

The README is not edited. Where it says otherwise, these readings stand.

1. **"Ruled out: more chip-level L3 or DRAM lines"** (item 3 of "The answer in five lines" and the "Ruled out" list of section 2;
   verify-lnc, medium). Read: *no more distinct lines (by the walk, by construction); at NB of 3 or less the card sends some
   duplicates beyond the L2, which the walk cannot see.* The walk's chip stream is equal for the two kernels only because its
   chip step ignores cooperation, and the NoC rail's +1.9 to +4.7 W at NB of 3 or less is itself extra chip-level transfer of the
   same lines. Whether any re-fetched duplicate of a fresh line reaches DRAM is **NOT RUN** (there is no DDR telemetry).
2. **The second variable, `first`** = (14 qA_b + 12 qB_b) / NB (verify-lnc, medium). It is a descriptor of NB, not a traffic
   count. By the walk's levels split by C block, the A panel's first C block is served from the same level as the later blocks at
   c01c, a079, a024, a026 and the smoke (A from the L3 at both), and the form divides B's share by NB although B changes with every
   C block. In "Gaps", read "pinned by 4 and 2 points respectively" as: *no fit point has NB above 6, so a024 (NB 15) and a026 (NB 12)
   extrapolate the 1/NB form from NB of 6 or less; the two smokes check it at NB 2.*
3. **The constants include self-heating** (verify-lnc, low). The gemmLnc die runs 0.83-2.88 C above its twin's in the settled window,
   which prices at 0.24-1.29 W: 3-13% of each excess. So c1, c2 and the per-line rail figures are effective constants that include
   this thermal feedback; they are not switching energies.
4. **The census share** (verify-lnc, low). Read "0.2% of the excess" as *0.2-0.8%, the wrong sign*: -0.015 to -0.068 W, 0.16-0.81%
   across the 9 points (0.66-0.81% at a087, a079 and c02c).
5. **The rails' basis** (verify-lnc, low). `board_w` is the instant 12 V reading; the three rails are the PMIC's averages over about
   1 s. Against the PMIC's own board average, settled, the rails carry 0.56-0.92 of the excess (the README's 0.55-0.87 is against
   `board_w`). The SRAM rail can also carry the re-fetched lines' L3 reads at their home slice, so "SRAM = duplicate L2 reads" and
   "NoC = re-fetch" are labels for the two constants, not a measured split.
6. **The equation's three readings** (check-lnc, nit). The text in `term-gemmlnc.json` needs three readings that only `s05_freeze.py`
   states: Q = (Q0 + Q1) / 2 from the predictor's output; t_op in seconds (the predictor's op time in microseconds x 1e-6); and "die"
   is the predictor's die at the start, 50 C at these forecasts, so D = 1. With them the text alone re-makes every frozen number bit
   for bit (check-lnc).
7. **E215's 65 W line beside the stops** (check-lnc, low). Section 4 compares planning peaks with the live stops only (70 W x3 on arm
   A, 72 W x3 on arm B). E215's registration also sets, on both arms, a 65 W line: no point runs whose planning peak passes it. With
   the term every registered gemmLnc point stays under it (the closest, b013, at 58.80 W: 6.20 W under). The smoke s14 plans at
   68.56 W, 3.56 W over the line; the line binds points, not smokes, and E213 measured s14's peak at 66.1 W.

## For E215's scores (REPORTED, post hoc; not a freeze)

- **The forms split E215's points both ways** (check-lnc, info). At NB 12-15, F3 is the lowest form (a024 23.53 W, a026 23.57 W,
  against about 27.5 W by F2 and F4); at NB 1 it is the highest (a031 25.90, a032 25.75, b013 25.04 W, against 20.4-20.7 W by F1).
  So E215 tests the 1/NB form blind in both directions, and F3 against F2/F4 at a024 and a026 is its clean test.
- **Alternative forms of the same size** (verify-lnc, info). A step at NB of 3 or less beats F3 on leave one point out (8.22% against
  9.81%) but misses the held-out smokes (+9.1% and +4.2%, against F3's -2.1% and -6.3%); F3 is the only form good on both. Across
  the six alternative forms G1-G6, E215's forecasts move against F3 by -0.6 to +1.2 W at a024 and a026, -0.8 to +0.1 W at a031 and
  a032, and -0.6 to +1.5 W at b013.
- **A nearest-analog reading** (verify-lnc, info). Matching each E215 shape to the fit point with the same walk level signature
  (a024 and a026 to a079; a031 and a032 to a082; b013 to a086, times card 1's measured ratio 1.20-1.31) gives a024 22.42, a026 22.33,
  a031 22.80, a032 22.66 and b013 25.7-26.5 W: F3 may read high on arm A (by about 3 W at a031 and a032) and low on b013 (by 0.7 to
  1.5 W).
- **Safety, information only** (both checks). s14's planning peak is 68.56 W by F3, 69.54 W by F2, 69.84-70.24 W by the other forms
  best on the smokes, 70.42 W by E213's measured analog and 72.47 W by the step forms, against the 72 W x3 stop. A trip there is the
  registered safe-side stop and would end arm B before b013.

## NOT RUN by either check

- Any card, simulator or DDR reading; the registered 0.55 W/C self-heating price on card 1 (it exists only for aifoundry3).
- The mechanism of the NB / B-share split: NB of 5 or more and "B partly fresh" coincide on all 9 points and on all of E215's, so
  E215 cannot separate them.
- A card factor (two pooled constants; card 1's excess is 1.20-1.31 times aifoundry3's at the same shape); data kind (every point is
  random data); format (the only int8 points are the L2-resident 1x1x1).

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `SHA256SUMS-note1` | its sha256 (`SHA256SUMS` is lnc-energy's and lists the 22 files it froze) |
