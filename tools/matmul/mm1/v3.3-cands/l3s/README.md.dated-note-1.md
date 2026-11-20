# Dated note 1 to 'MM1-v3.2 + L3S': its two checks, and how to read the README with them

*Fri 20 Nov 2026, Pacific time. Written by land-cands (round Q234) from 07:42 PST, when E220 had booked no card: no E220 datum
existed, and this lane opened none at any time. Desk only. Every number below comes from the two checks named, which ran on committed
data and on this folder; each keeps the label its check gave it (desk, post hoc, held out, REPORTED). This note changes no file of the
folder: the README, the declaration, the code, the outputs and the frozen files are committed byte for byte as l3-edge left them.*

## What is committed here, and its freeze line

- **The folder** is l3-edge's land, byte for byte: 32 files and `SHA256SUMS` (sha256 `c5d4f03e4364d451...`, 32 of 32 OK). It was last
  written at 06:17:58 PST (`scripts/REWRITES.tsv` and `SHA256SUMS`): after the freeze and its post, before either check began
  (check-l3-edge at 06:20:28 PST). The four files the lane's FROZEN.txt names are unchanged since the freeze (their sha256 equal its
  lines).
- **The frozen forecasts**, final at **05:56:55 PST** (the lane's FROZEN.txt written 05:57:20 PST), before any E220 datum, were posted by
  their sha256 with FROZEN.txt's as post **#1.30.1.2.1.1** on the owner's coordination thread at **06:05:46 PST**. That post is their
  freeze line:

      e8216cbb2a222a1c48a4b929fd4f07d10d80f4b20f97813b700bbdc6cff401e0  FROZEN-e220.txt (the lane's FROZEN.txt)
      ff46a16ec6c83eb3464090db1c9295d9b75338309785f0f965d3d99039f42a2e  forecasts-e220-l3s.csv
      ac65c9596f5611c95899b1c5105eee137602d5afbe00dfa316582ea651b753a8  forecasts-e220-l3s.json

  FROZEN.txt also names `DECLARED-l3s.md` (`1e6e1c52...`, hashed at 05:52:57 PST, before the fit) and `fit-l3s.json` (`4fe92350...`).
  This commit is a later record of them, not their freeze line.
- **Added by this lane** (new files, listed in `SHA256SUMS-note1`): `FROZEN-e220.txt`, the lane's FROZEN.txt byte for byte, so that
  the posted FROZEN.txt sha256 can be checked here (its "OUT/..." path names the round's desk folder, not a file of this repository);
  and this note.
- **The points:** E220's POINTS.txt (sha256 `058984a0...`, final 05:24:17 PST): 306 rows, arm A's 84 points at 600 MHz on aifoundry1
  card 1 and arm B's 74 at 799, 700 and 600 MHz on aifoundry2 card 0, with MM1-v3.2 beside.

## The two checks

**check-l3-edge: HOLDS** (06:20-06:36 PST; desk; `/usr/bin/python3` 3.12.3; every job in the round's CPU slots).

- Its own caller re-made all 306 rows: 6,120 of 6,120 fields exactly equal, 612 of 612 line triples, the same in one batch or one at a
  time; the CSV rebuilt from its numbers is byte-equal (`ff46a16e...`).
- It wrote the term again from the declaration's section 3 and priced it with MM1-v3.2's own engine: T' agrees within 4.2e-16 (226 of
  306 bit-equal); Q' 306 of 306 and the energy given T' 918 of 918 exact; lam = 0 gives MM1-v3.2 exactly; no row is clipped.
- Its own 4-way LRU, driven by the committed walk's chip steps (MM1-v3.1's walk), gives the frozen feature at 42 of 42 shapes: all 41
  E220 domain shapes (34-1952 MiB) and gemmL2x1x7 (1 of 7 kept, 14.3%).
- The folder's path-rewritten scripts re-make the frozen numbers exactly (4,896 of 4,896 fields).
- Every hash matches FROZEN.txt and the post; POINTS.txt (`058984a0...`) equals the registration's point list, and the frozen rows
  cover all 158 points (A at 600 MHz; B at 799, 700 and 600 MHz). No E220 datum existed (no E220 data folder at 06:34:39 PST), and the
  order of the times is clean (declared 05:52:57, fit 05:54:34-05:56:22, final 05:56:55 PST).
- The keep rule, recomputed from the lane's own records: K1 drop 5.81 points; K2 rise -0.153 points on n 2,378, with the twin flags
  re-derived (3,408 of 3,408) and the base equal to MM1-v3.2's table LOEO (2,508 of 2,508); K3 100 of 100: KEPT.

**verify-l3-edge: HOLDS WITH FIXES** (06:36-07:26 PST; desk; the same interpreter; every numerical job in slots). Its fixes are caveats;
none changes a frozen number.

- Its own set model, written from the kernel and host source (rgm136's large-GEMM loop and the host's arm setup), equals l3-edge's
  feature at 600 of 600 shapes (difference 0); with the kernel's C-store order, hA is unchanged at 600 of 600 and hB within 0.0028.
- The data: 3,408 points re-read from the committed sources, 0 field differences. The fit: lam 0.6908933154 against 0.6908933060; SSE
  4.8770 -> 4.3496; 29 folds' lam within 6.1e-8 and rms within 5e-8 points; every held-out point within 4.3e-9; twins 3,408 of 3,408;
  MM1-v3.2's pricing linear in the term to 4.4e-16.
- The keep rule: K1 14.488 -> 8.677% (drop 5.81), K2 5.5758 -> 5.4229% (n 2,378), K3 100 of 100 (gain 0.52745 against a placebo
  maximum of 0.01366): KEPT. K1 also holds with every gemmL2x1x7 point (E216's too) out of lam's fit: lam 0.649, 14.49 -> 8.74%.
- E220: all 306 rows re-made, every field of both models within 4.4e-16 relative at the frozen lam.
- The mechanism is supported. A fully associative 32 MiB cliff in the same form carries no signal (lam 0.034; placebo 79 of 100:
  FAIL). At the lead, the measured wall over the counter's mean (1.076-1.079 in E215, 1.089 in E216, against MM1-v3.2's 1.011) matches
  the set model's split between row groups, a signal the term never used. Other causes are ruled out at the lead: the clock (0.5992-0.5996
  GHz in every counted launch of all 8 E215 runs), the die (gates 47-50 C), three cards, times from the kernel's counters (not the
  sampler), and B 100% in every column group.

## Read the README with these corrections

The README and the declaration are not edited. Where they say otherwise, these readings stand.

1. **Which share the term moves** (verify-l3-edge, medium). The term prices the wall (the slowest minion) with the set model's
   chip-average A share and keeps MM1-v3.2's rho (1.011). At the lead the set model splits the row groups (0% and 28.6% of A kept); the
   measured wall over mean is 1.076-1.091; under MM1-v3.2's prices the wall implies an A L3 share of -0.002 (the slow row groups keep
   0.000) while the counter's mean implies 0.176 (the set model's average: 0.143). So the lead stays -7.7 to -10.0% held out. Read: *the
   term moves the average minion's A share; it cannot give the split between the wall and the mean.* A rule on the slowest row group
   fits the lead (at lam 1: 1.5%) but fails gemmL1x1x11 (6.3% against 0.9%) and gemmL9x1x1 (9.4% against 1.0%), so it is not the fix
   (post hoc, REPORTED). A rho rule from the row-group split would need its own declaration before a later test.
2. **Lock step** (verify-l3-edge, medium). At NB = 1 the feature does not depend on drift between the row groups (unchanged up to 256
   steps); at NB >= 2 it rests on the row groups staying in step: gemmL2x5x9 goes 0.503 -> 0.402 with 16 steps of drift and 0.151
   with 64; gemmL2x6x8 0.706 -> 0.441 with 64. The measured wall over mean at the NB = 2 split shapes is 1.000. Held out (no twins), the
   moved NB = 1 points go 6.47 -> 3.24% (n 45) and the moved NB >= 2 points 6.41 -> 5.94% (n 488; with twins, 437 points better and 353
   worse). lam fitted alone (in sample): 0.88 at NB = 1, 0.65 at NB >= 2, 0.33 at KB <= 2, 0.00 on gemmLnc. E220's l06, xf01-xf12,
   xg01-xg03 and their twins rest on lock step.
3. **gemmLnc** (verify-l3-edge, low). On the gemmLnc points alone lam fits to 0 (in sample 9.12 -> 9.48% at lam 0.691); held out 9.27 ->
   9.63% (n 36). The term slows E220's xg01-xg03 and xg09 by 0.8-2.8% on top of MM1-v3.2's gemmLnc bias. If the candidates are ever
   combined with the gemmLnc term AF4, leave gemmLnc out of L3S or refit jointly.
4. **The 'change' columns are ln** (verify-l3-edge, low). Section 7's 'change' column (+1.35% to +6.76% at l01-l06) is ln(T'/T) in
   percent. As relative changes, A l01 is +6.45% and B l01 +6.99% (the column's +6.25% and +6.76%).
5. **The 5e-9 claim** (check-l3-edge, nit). The README and FROZEN.txt say the MM1-v3.2 column equals E220's registered MM1-v3.2
   forecasts "to 5e-9", but no file here compares them. check-l3-edge measured it: largest relative difference 4.6e-12 over 3,060
   fields (the registered file has 12 digits).
6. **The pool layout** (verify-l3-edge, info). The feature depends on where the pools sit: reversed pools change hA at 143 of 600 shapes
   (by up to 0.167). The assumption holds for the fit's data: rgm136 and rgm211 allocate out, a, b; the allocator is first-fit over 4 KiB
   blocks; the E215 and E216 runs read used one device process each. For E220, its registration's text (reg-e220's draft, not yet on
   GitHub main when this note was written) runs each arm A run as one host process (E215 arm B's run form) and arm B in E216's run form;
   E220's kit was NOT CHECKED, by the verifier or by this lane.
7. **What is assumed** (verify-l3-edge, open). The cards' L3 mode (M0) and contiguous physical addresses were not read on a card. The
   data support them indirectly: the 32 MiB edge, the 0%-kept shapes at 41-48 MiB, and the row-group signature.

## For E220's scores (REPORTED; not a freeze, not a rule)

- The rows that separate the candidate from MM1-v3.2 at E220 are the 39 it moves by more than 1%, all slower: l01-l06, and xg01, xg02
  and xg09 with their gemmL twins (check-l3-edge, info). In all, the term moves T at 185 of the 306 rows (206 in its domain), by -0.37%
  to +6.99%.
- E220's l02 (gemmL4x1x3) is the one NB = 1 L3 point whose row groups the set model splits (0.50 and 0.75 kept; drift-invariant): the
  blind case for item 1. If the mechanism holds, l02's measured wall over mean comes out well above 1.011, and l01, l03, l04 and l05's
  do not. verify-l3-edge's desk numbers for l02 at 600 MHz (written at 07:09:47 PST before any E220 datum; REPORTED, not forecasts and
  not a rule): MM1-v3.2 1.6965 us, the frozen L3S 1.7799 us, a slowest-row-group variant 1.8304 us at lam 0.588 and 1.9241 us at lam 1.

## NOT RUN

- verify-l3-edge: the lane's energy table (REPORTED), its own re-run of the folder's scripts (check-l3-edge ran it), the E105-E215-only
  K2 figure, and any check of E220's kit.
- l3-edge: the card's L3 mode, read from any card.
- This lane re-ran no number. It copied the folder, checked its hashes against the posted ones, added `FROZEN-e220.txt` and this note,
  ran the public-text scans, and committed.
