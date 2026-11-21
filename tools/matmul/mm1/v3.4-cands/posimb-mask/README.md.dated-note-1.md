# Dated note 1 to 'MM1-v3.2 + posimb-mask': its two checks, and how to read the README with them

*Sat 21 Nov 2026 (week 47), Pacific time. Written by land-cands4 (round Q238) from 03:36 PST. Desk only. No E223 or E226 datum and no
E226 file was opened, and no E226 point was chosen: the next blind day is registered after these freezes. Every number below comes from
the two checks named, which ran on committed data (GitHub main cfd7e641) and on this folder; each keeps the label its check gave it
(desk, post hoc, held out, REPORTED). This note changes no file of the folder: the README, the declaration, the code, the outputs and the
frozen record are committed byte for byte as mask-posimb left them.*

## What is committed here, and its freeze line

- **The folder** is mask-posimb's land, byte for byte: 48 files, `SHA256SUMS` among them (sha256 `419dac6e69b35418...`, 47 of 47 OK),
  last written at 01:48:34 PST, before either check began (check-mask-posimb at 01:51 PST).
- **The frozen record** `FROZEN-posimb-mask.txt` is the lane's FROZEN.txt byte for byte (the land carries it): files final at 01:48:33
  PST, the record written at 01:48:34 PST, before any E223 or E226 datum. Its sha256 was posted as post **#1.30.1.2.1.1.1.1.1** on the
  owner's coordination thread at **01:49:15 PST**. That post is its freeze line:

      0cd8e9da11e1b0f0bedba342e40adf2a18e9ff112f87e5436d712f32fe5eafdc  FROZEN-posimb-mask.txt

  Its 46 hash lines name every other file of the folder but `SHA256SUMS`, with the sha256 as landed: all 46 are SAME here. The
  declaration `DECLARED-posimb-mask.md` (sha256 `b59f1c4dc5ff1b67...`) was written at 01:31:30 PST, never modified, and hashed at 01:31:42
  PST, before the fit script existed (first written at 01:33:34 PST). This commit is a later record of them, not their freeze line.
- **Added by this lane** (new files, listed in `SHA256SUMS-note1`): this note.
- **Two inputs are re-made, not landed** (check-mask-posimb, low): `base.npz` (sha256 `3872ff1a...`, named in the declaration and checked
  by `scripts/g01_fit.py`) and E224 arm B's 59 points (a reduction by E208's registered reducer; at cfd7e641 no data JSON for arm B was
  committed). check-mask-posimb re-made both bit-equal from the landed scripts and committed data. The same arm B reduction
  (`data-e224b.json`, sha256 `e5cf09f2...`) is landed with the two other tracks of this round, beside this folder.

## The two checks

**check-mask-posimb: HOLDS** (01:51-02:08 PST; desk; `/usr/bin/python3` 3.12.3, numpy 1.26.4; every numpy job single-threaded in the
round's CPU slots).

- Hashes: FROZEN.txt has the posted sha256; its 46 lines match; `SHA256SUMS` 47 of 47; no land file is newer than FROZEN.txt.
- Order: the declaration was created at 01:31:30 and never modified, its sha256 file written at 01:31:42; the fit script was first
  created at 01:33:34 and its outputs at 01:33:38; it checks the declaration's sha256 before it reads anything.
- Re-run: the landed `scripts/e01_base.py` and `scripts/g01_fit.py`, run unchanged from the checker's own clone at cfd7e641, re-made
  `base.npz`, `out/base_meta.json` and `out/heldout_points.csv` bit-equal; `out/fit_results.json` is equal in 8,180 of 8,180 leaves but
  its `secs` field (1.6 against 1.5). E224 arm B's reduction, `out/points_all.json` and `out/private_shared.json` (458 configurations, by
  posimb's landed maker) re-made bit-equal.
- 20 held-out predictions (10 LOSO, 5 LOMO, 5 LOEO) re-made by the checker's own code equal the frozen record exactly; 15 fold constant
  sets by its own QR agree to 2.0e-15, the all-data constants to 3.9e-16.
- The keep rule by its own code: M1 8.1259% (<= 11.409), M1L 8.1215% (<= 11.909), M2 5.4196% = 5.4196%, M4 6.8342% (<= 7.1183), the
  placebo beaten 100 of 100: KEPT.
- AF4: the composition holds by construction. The scopes are disjoint (posimb-mask acts at rgm136 gemmL subset points, AF4 at gemmLnc
  points). Of the 326 registered E222 and E224 rows, 62 are the term's only, 36 AF4's only, 228 neither's and none both's. The module
  re-made all 11,416 values exactly, and its MM1-v3.2 and 'MM1-v3.2 + AF4' equal E222's and E224's registered frozen forecasts in 5,708
  values to 4.3e-12.

**verify-mask-posimb: HOLDS WITH FIXES** (02:08-02:40 PST; desk; the same interpreter; numerical jobs single-threaded in slots under a
4 GB cap; its own clone at cfd7e641).

- Re-made by its own code, equal to the record: E221's 733 cases from the nine raw session files (811 runs); E222's 70 and E224 arm A's
  62 points from their data files; A1, the scope, the MASK class and the twins at all 4,311 points (E221's committed class 392 of 392
  MASK, 341 of 341 non-MASK); G1core and LAGcore; posimb's Fp and Fs by its own stack-distance LRU over the walk's own generator, 38 of 38
  sampled configurations; the fit and every fold (M1 8.1259%, M1L 8.1215%, M2 5.4196%, M4 6.8342% against MM1-v3.2's 7.0683%; the
  constants a_hop 0.411735, a_lag 0.334919, a_al -0.104690; held-out op times to 4.4e-16); the placebo with its own random draws, beaten
  100 of 100; the README's REPORTED tables; the frozen predictor at 43 points, 3 of them configurations not in the cache.
- The alignment effect is real: the same per-shape offsets on all three E221 cards; A1's coefficient -0.113 +- 0.007 with shape, card,
  shire-count bins, clock, die, run order and clock dips beside it (-0.138 alone); a placebo permuting A1 within arm and shire count
  beaten 100 of 100 (9.62-10.19%); none of 150 random one-per-row-group shire sets beats the aligned set (best 8.69%); LOSO with every
  point at the test point's arm and mask also left out of training 8.35%; constants fitted with no E221 datum 8.45% on the 363 cases.
- Its fixes are labels and readings. No number and no hash changes.

## Read the README with these corrections

The README and the declaration are not edited. Where they say otherwise, these readings stand.

1. **Post hoc, at E221's shapes** (check-mask-posimb, medium; verify-mask-posimb, high). A1, the third feature, was chosen after
   in-sample looks at MM1-v3.2's residuals on the same E221 cases (the declaration's section 0; the README's "Labels"). The LOSO and LOMO
   folds refit only the constants, so M1 8.13% and M1L 8.12% are post hoc figures with the constants held out; the freeze post's "held
   out" carries that label. Read every held-out number here and in the README as *post hoc, at E221's shapes*:
   - MM1-v3.2's A1 offset depends on the shape: -24.5% (gemmL3x4x6), -20.2% (2x6x10), -15.3% (1x12x8), -14.4% (1x8x11), -8.2% (1x7x8),
     -4.1% (4x6x2), -3.4% (1x16x6), -2.9% (1x3x4 and 2x4x24), -0.9% (2x1x16), -0.2% (4x1x10), the same on the three E221 cards within
     about 3 points; 45% of the 216 A1 points are gemmL2x6x10.
   - With each shape held out whole (every mask, card and experiment), E221's 363 cases read 8.69% (the alignment term alone 8.73%), and
     the term beats MM1-v3.2 at the A1 points of 7 of 12 shapes; it is worse at 1x16x6, 1x7x8, 2x1x16, 2x4x24 and 4x1x10. Its bias on a
     held-out shape runs from -14.1% (4x1x10) to +23.5% (3x4x6).
   - **At the 23 A1 points outside E221, at shapes E221 never ran at an A1 mask (E215, E217, E222, E224), the term reads 10.17% (bias
     -8.2%) against MM1-v3.2's 7.95% (+3.5%), each experiment held out, and is closer at 7 of 23** (REPORTED). K4 passes because the 31
     A1 points outside E221 at E221's shapes (E214 and E217) improve, 13.69% -> 7.95%, closer at 25 of 31.
2. **The aligned set was identified at one shape** (verify-mask-posimb, medium). E221's 32-shire single-shire scan is gemmL2x6x10 fp32
   zeros on the three cards; other shapes saw only shire 10 against shires 14 and 17, plus multi-shire masks. Within the scan the binary
   A1 hides a spread (low; REPORTED, for a later form): aligned shires 0 and 31 read +8% and +6%, aligned shires 10, 15, 21 and 26 read
   -4% to -0.2%, the same on all three cards, and the off-diagonal shires read -9% to -18%.
3. **aifoundry3 card 0 is untested where the effect is large** (verify-mask-posimb, medium). Fitted per card, the alignment constant is
   -0.017 on aifoundry3 card 0 (9 A1 points) against -0.094 (aifoundry1 card 1), -0.114 (aifoundry2 card 0) and -0.118 (aifoundry1 card
   0). Leaving that card out, its MASK points go 6.50% -> 6.79%, and E222's 6 A1 points are over-corrected (from -3.3..+13.6% to
   -16.3..-1.7%). Every A1 point on that card is at a shape E221 never ran, so the card and the shape cannot be separated.
4. **"One aligned shire sets the wall" is not supported** (verify-mask-posimb, medium). The README's reading (section 2: the wall is the
   slowest active shire's) does not fit E221's runs. Within one run, ln(wall / counter mean) is 3.21% at masks that mix aligned and other
   shires (n 142), 0.63% at A1 masks (n 50) and 0.00% at purely aligned masks (n 3). Regressed on the non-aligned share, that excess has
   a slope of 2.7 +- 2.0% (gemmL2x6x10 alone 4.7%), against a wall offset near 20%: most shires of a mixed mask run slow, not only one.
   That fits a row-group by column-group pair form (A2). The one multi-tile point where A1 and A2 differ (E217 gemmL3x3x15 at 0x40081000)
   reads like A0 (+3.9%). The physical reading stays **not established**, as the README says.
5. **K2 cannot fail** (check-mask-posimb, low). The term's only in-scope non-MASK points are 1x1x1 cells, where e = 0, so M2 5.4196% =
   5.4196% is an identity, not evidence. The guard that bites is K4 (a margin of 0.28 points).
6. **Counts** (nits). The declaration's section 6 says 29 LOEO folds; there are 28 experiments and 28 folds (verify-mask-posimb; no number
   changes). Its section 8 says E222's 70 points; the composition files hold 73 E222 rows, the 70 points plus 2 smoke gates and 1 tie,
   matching the 73 entries of E222's registered forecast file, and the 62 / 36 / 228 counts include those 3 rows (check-mask-posimb).
7. **The address bases** (verify-mask-posimb, nit; a read of the host code, not a measurement). The GEMM's host allocates its C, A and B
   buffers in that order, each a whole number of MiB, C and A multiples of 2 MiB. A contiguous allocator would make the A and B bases
   congruent mod 2 MiB at every shape, so the reading's premise cannot by itself explain the shape dependence. The allocator's placement
   is NOT measured.

## REPORTED beside (never deciding)

- Energy (verify-mask-posimb, post hoc): J over idle with the op time forecast (blind-e221's E2 form) at 246 of the 363 cases, MM1-v3.2
  16.67% -> 12.08% (at the A1 cases 21.29% -> 11.90%); given the measured op time (E1) it is unchanged by construction.
- check-mask-posimb's 20 picks: 2 are in-scope 1x1x1 cells (e = 0), so 18 test the term; one, E221's aifoundry1 card 1 gemmL2x1x16 at
  0x20000 (A1 = 1), goes from -1.67% to -14.24% held out: the over-correction at 2x1x16 that README section 5 names.

## For the next blind day (the verifier's advice; no point is chosen here)

- Score the A1 points at shapes without E221 A1 data apart from those at E221's shapes, and carry A1 masks at both kinds of shape.
- On aifoundry3 card 0, an A1 mask at a shape where the effect is large.
- Masks where A1 and A2 differ; a second single-shire scan at another shape.

## NOT RUN

- check-mask-posimb (left to the verifier): the features from the walk by its own code (posimb's frozen maker was re-run unchanged); the
  MASK class over every point by its own code; the placebo by its own code; leakage and alternative explanations.
- verify-mask-posimb: a joint refit with MM1-v3.2's constants; a shape-aware form; the physical mechanism (address bases, set and bank
  mapping); E216-E220's points re-derived from raw (taken from the committed tables as `scripts/d01_points.py` reads them); E224 arm B's
  reduction and the AF4 composition (check-mask-posimb re-made both).
- This lane re-ran no number. It copied the folder, checked its hashes against the posted ones, added this note, ran the public-text
  scans and committed.

SPDX-License-Identifier: Apache-2.0
