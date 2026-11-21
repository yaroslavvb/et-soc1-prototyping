# Dated note 1 to 'MM1-v3.2 + mask-ceiling': its two checks, its freeze line, and how to read the README with them

*Sat 21 Nov 2026 (week 47), Pacific time. Written by land-cands4 (round Q238) from 03:36 PST. Desk only. No E223 or E226 datum and no
E226 file was opened, and no E226 point was chosen: the next blind day is registered after these freezes. Every number below comes from
the two checks named, which ran on committed data (GitHub main cfd7e641) and on this folder; each keeps the label its check gave it
(desk, post hoc, held out, REPORTED). This note changes no file of the folder: the README, the declaration, the code, the outputs and the
frozen record are committed byte for byte as mask-ceiling left them. The reference stays what its README calls it, REPORTED and never a
model candidate.*

## What is committed here, and its freeze line

- **The folder** is mask-ceiling's land, byte for byte: 41 files, all written at 02:22:21 PST, before either check began
  (check-mask-ceiling at 02:24 PST). `SHA256SUMS` (sha256 `9bb5734fbacb145a...`, 39 of 39 OK) lists every file but itself and FROZEN.txt;
  FROZEN.txt names the other 40, `SHA256SUMS` among them, with their sha256 as landed: all 40 are SAME here.
- **The frozen record** `FROZEN.txt` (in the land as frozen; the lane's FROZEN.txt byte for byte) is final at **02:22:21 PST**, before
  any E223 or E226 datum. Its freeze line is the CORRECTION post **#1.30.1.2.1.1.1.1.1.1.1.1** on the owner's coordination thread at
  **02:42:04 PST**:

      bf6e2d9643bd886984f370b37017a7a915051d1bdeed73fd4eb6f59dce7a112f  FROZEN.txt

  This commit is a later record, not the freeze line.
- **The first post, and the file added with this note.** The post at 02:21:44 PST (#1.30.1.2.1.1.1.1.1.1.1) named `1649ba5b...`, the
  lane's first FROZEN.txt write, of 02:21:13 PST, which the lane kept read only as `FROZEN.txt.superseded-022113`. This lane adds that
  file here byte for byte (sha256 `1649ba5ba69e1061af112e0ce6b98e4d42101080cd9e202f1bacea51edb8b45f`), so that the first post can be
  checked on the repository too: the dated amendment 1 to the lab's blind declaration of E223 names that post's sha256 and records the
  final one (check-mask-ceiling). The two records differ only in their time line and in the lines for `README.md` (a new section 3b,
  written at 02:22:21), `SCRUB.json`, `logs/progress.txt`, `scripts/l01_readme.py` and `SHA256SUMS`. Their other 35 file lines are
  equal: the declaration, the params, the fits, the held-out record and points, the placebo, the composition, the verdict, the self-test,
  the inputs and every script of the fit. Those five files of 02:21:13 were rewritten at 02:22:21 and not kept; every file the forecasts
  call is equal under both records (check-mask-ceiling).
- **How to read FROZEN.txt.** Its paths are this folder's and its sha256 are as landed. Beside each of the 10 scripts whose one lane-path
  line the land replaced by an environment lookup (`SCRUB.json`: `MASK_CEILING_LANE`, default the folder above `scripts/`), it gives the
  as-run sha256 in parentheses.
- **The declaration** `DECLARED-mask-ceiling.md` (sha256 `e9701ff2c7437736...`) was written at 01:28:28 PST and hashed at 01:28:32 PST,
  before the fit scripts (01:30-01:32 PST) and their outputs (01:38 PST).
- **Added by this lane** (new files, listed in `SHA256SUMS-note1`): `FROZEN.txt.superseded-022113` and this note.

## The two checks

**check-mask-ceiling: HOLDS WITH FIXES** (02:24-02:44 PST; desk; `/usr/bin/python3` 3.12.3, numpy 1.26.4; every numerical job
single-threaded in the round's CPU slots, one at a time). No fix touches a frozen byte.

- Hashes: the lane's and the land's FROZEN.txt are byte-equal; all 40 file lines re-hash equal, as landed and as run; `SHA256SUMS` 39 of
  39; each of the 10 scrubbed scripts differs from its as-run copy only in its one lane-path line.
- The declaration came before the fit: the 10 sha256 it pins match files written before it; `scripts/r01_holdout.py` refuses to run
  unless the declaration's sha256 holds; no fit output is dated before 01:28:32.
- The fit re-run by its own caller of the frozen `scripts/rf_core.py` and `scripts/r_common.py` (its own scope, classes, folds, twins,
  rows, seeds, bases and metrics): the reference's held-out prediction at 10,357 of 10,357 rows bit-equal over 156 folds; the REPORTED
  learners on LOSO 733 of 733 each; M1 exactly: LOSO 12.2523% -> 5.7789% (n 318), LOEO 9.5767% -> 7.7302% (869), LOCO 9.4837% ->
  5.4308% (975), LOMO 10.5045% -> 7.3574% (722); K2 5.4273% -> 5.4273% (n 2,375); the E221 footing 12.409% -> 5.628% (n 363); the
  all-data forest refit equal to `params-mask-ceiling.json` (exact JSON, 200 trees).
- The base: the landed `scripts/e01_base.py` re-made `base.npz` byte for byte against the lab at cfd7e641 (sha256 `c19c3a64...`, the
  declaration's pin; 102 of 102 arrays), and it equals MM1-v3.2's stored predictions at 2,508 points and every stored fold's (largest
  relative difference 0.0).
- Its own code: its own forest code, written from the declaration without importing `rf_core`, re-made 22 of 22 held-out predictions
  bit-equal; its own tree walker on the frozen params 20 of 20; the landed predictor's self-test 20 of 20 (a single row's mean is within
  4.2e-17 in ln of the batch mean, because numpy sums the 200 trees in another order; the self-test's tolerance of 1e-12 is right).
- The keep rule: K1 passes on every family (5.779 <= 11.027, 7.730 <= 8.619, 5.431 <= 8.535, 7.357 <= 9.454); K2 5.427 <= 5.477; K3 100
  of 100 (the placebo 9.650-10.129%), the identity draw and LOSO draws 0, 1 and 99 re-made bit-equal; the LOMO placebo (REPORTED) 10 of
  10: "meets the keep rule (K1, K2, K3)".
- AF4: the composition holds by construction: 0 of 4,311 data points and 0 of 355 registered E220, E222 and E224 points are in both
  scopes; AF4's frozen E220 forecasts carry MM1-v3.2's op time at 306 of 306 rows (relative <= 4.3e-12) and equal MM1-v3.2 in every number
  off gemmLnc at 260 of 260 rows.
- The data: the E224 points equal verify-e224d's own re-derivation from raw (62 of 62 and 59 of 59; only p3a and p3b, excluded, absent);
  the E221 labels equal blind-e221's committed classes at 733 of 733 (MASK 392).

**verify-mask-ceiling: HOLDS WITH FIXES** (02:44-03:25 PST; desk; numerical jobs single-threaded in slots at a 1-minute load of 2.3 or
less). The frozen record holds; two readings of it do not.

- Re-derived by its own code: E221 from its nine raw session files (811 runs, 733 cases, equal to blind-e221's case table and to the
  lane's points); the MASK class (975 points, scope 888; 4,311 of 4,311 equal; blind-e221's class at 733 of 733); the 14 geometric
  features at 458 of 458 configurations (largest difference 2.2e-16) and Fp and Fs at 55 configurations from MM1-v3.1's walk (exact); the
  base against blind-e221's committed errors (at most 3.4e-6).
- Its own forest (written from the declaration, not importing `rf_core`) on the declared families, MASK points without a twin, MM1-v3.2
  -> its own (frozen): LOSO 12.25% -> 5.70% (5.78%), LOEO 9.58% -> 7.69% (7.73%), LOCO 9.48% -> 5.45% (5.43%), LOMO 10.50% -> 7.42%
  (7.36%). No frozen prediction sits at the +-0.5 clip.
- K1 passes even on strict folds (LOSO-strict 8.68% <= 11.03%, LOEO-strict 7.84% <= 8.62%, LOCO-strict 7.89% <= 8.54%, LOMO 7.36% <=
  9.45%): "meets the keep rule" stands.
- The MASK residual is the placement's: it repeats across the three E221 cards at r 0.994-0.999 (the placement holds 0.990 of the
  variance; a card deviates from the placement mean by 1.05% rms). Card, clock, governor, die, the sampler's window and the run order do
  not explain it (reading 7 below).

## Read the README with these corrections

The README and the declaration are not edited. Where they say otherwise, these readings stand.

1. **The E221 footing looks up repeated placements** (verify-mask-ceiling, high). The README's "E221 footing" (12.41% -> 5.63%, share
   explained 0.794; also in the 02:21:44 post) is held out by session, but E221 ran 130 of its 184 subset placements on all three cards:
   every LOSO test placement (308 of 308) has its arm, format and mask run on another card in that fold's training set, where MM1-v3.2's
   residual repeats at r 0.99. With those repeats taken out of training (LOSO-strict), the frozen learner reads 8.68% (n 318; the
   verifier's own forest 8.77%) and 8.55% on the 363 cases (share 0.53). Held out by mask, the 363 read 7.51% (share 0.63); E221 held out
   whole, 9.32% (n 347, share 0.43). LOCO carries the same repeats (724 of 888): LOCO-strict reads 9.48% -> 7.89% against the declared
   5.43%. **For a never-run mask read: LOMO 10.50% -> 7.36% (share 0.51); on the 363 cases LOMO 7.51% (share 0.63), LOSO-strict 8.55%
   (share 0.53) and E221 whole 9.32% (share 0.43)**, in place of "share explained 0.79". README section 3b flags the repeats; these are
   the figures.
2. **It is not a ceiling** (verify-mask-ceiling, high). On the same points and folds, from both lanes' per-point records, mask-mesh's
   frozen two-constant term (`../mesh/`, FROZEN.txt `487188c7...`) is better wherever no repeat of the test placement is in training:
   LOMO, MASK points without a twin (n 647): MM1-v3.2 10.45%, this reference 7.34%, mesh 6.53% (mesh closer at 347); the 363 held out by
   mask: 12.41%, 7.51%, 5.97%; E221 held out whole (n 347): 12.34%, 9.32%, 7.37%. The reference reads lower only where it can look up
   repeats: LOSO 5.78% against 5.92%, LOCO 5.58% against 6.55%. The 02:21 report's "mask-mesh's 5.97% is near it" set mesh's LOMO figure
   beside the reference's LOSO figure. Read 'mask-ceiling' as **a nonparametric reference on these 22 features**, not a ceiling or a
   bound. README section 3b's "a two-constant term from these features should not expect to beat the LOMO figure" holds only for these
   features: mesh's term, with one feature outside them (the L3's set alignment; its sets alone read 6.15%), beats it.
3. **K3's placebo cannot tell mechanism from recognition under LOSO** (verify-mask-ceiling, medium). The declared placebo permutes the
   features point by point, which also breaks the cross-card repeats. A placebo by configuration (one wrong feature vector a placement,
   kept on every card) reads 8.07-8.99% (median 8.59%, 20 draws, the verifier's forest) against the point-level 9.69-9.96% (frozen
   9.65-10.13%): about 1.3 points of LOSO's placebo gap is recognition alone. The real fit (5.70%) still beats it 20 of 20, and under LOMO
   the configuration-level placebo reads 9.27% and 9.16% against the real 7.36-7.42%. K3's PASS stands.
4. **New shapes** (verify-mask-ceiling, medium). With one shape held out at a time (137 folds) the MASK points go 9.50% -> 8.23% (n 975)
   and the 363 cases 12.41% -> 10.27% (share 0.31), and the reference is worse than MM1-v3.2 at 61 of 137 shapes: gemmL4x1x10 2.96% ->
   11.88%, gemmL1x16x6 3.31% -> 9.55%, gemmL2x4x16 6.79% -> 9.79%, gemmL2x1x16 3.76% -> 6.02%, gemmL2x4x24 2.31% -> 4.57%. It keeps a
   gain at gemmL4x6x2 (14.61% -> 5.53%) and gemmL3x4x6 (22.90% -> 16.65%). The reference applies to never-run masks only at shapes in its
   training set; at a new shape, read MM1-v3.2.
5. **K2 is vacuous for this form** (verify-mask-ceiling, low). The scope is a subset of the MASK class, so no non-MASK point can move:
   5.427% -> 5.427% holds by construction.
6. **Its domain** (verify-mask-ceiling, low). The clock feature is a two-level card-group indicator: the in-scope training clocks are
   about 600 MHz (429 points: aifoundry1 card 1 and aifoundry3 card 0) and about 799 MHz (459 points: aifoundry1 card 0 and aifoundry2
   card 0). The training shire counts are 1-6, 8-10, 12, 15, 16, 24 and 28. At another clock (a governor step) or shire count the trees
   fall on an arbitrary side of their splits.
7. **Alternative explanations, ruled out on E221** (verify-mask-ceiling, info). The residual repeats across three cards at 600 MHz
   pinned, about 800 MHz at low power and under the governor (r 0.994-0.999, slopes 0.89-1.11). Within a card the clock varies by at most
   0.08 MHz sd and the die by at most 0.6 C sd, and they correlate with the reference's held-out residual at most 0.30 in magnitude. The
   run index correlates across cards at only 0.18-0.77 (rank). The governed cards' window and whole-burst wall cycles differ by 1.85-1.89%
   rms a run, unrelated to the shire count (r -0.04 and 0.03). Held out by mask within E221, run conditions add nothing to the mask
   features (context alone 9.20%, with the run conditions 8.89%, with the mask features 8.67%, with both 8.68%; MM1-v3.2 12.52%). The
   repeat floor is at most 0.34%.
8. **Where it is worse** (verify-mask-ceiling, info). Held out by mask (frozen rows): PLD 2.31% -> 2.88%, PLE 3.14% -> 4.85%, E212 7.66%
   -> 8.46%. It gains most at one shire (13.11% -> 7.26%) and at 2-3 shires (11.12% -> 8.30%). The leakage under LOEO is small: 96 of 830
   test points have a repeat from another experiment, and strict LOEO reads 7.84% against the declared 7.73%.
9. **Re-running the fit from this folder takes a recipe** (check-mask-ceiling, low). README section 7 says to set `MASK_CEILING_LANE` to
   a folder holding `work/lab` and the `work/` inputs. As landed, `scripts/r01_holdout.py` and `scripts/r02_placebo.py` refuse to run (4
   of their 9 pins): they pin `work/base.npz`, which is not landed; they pin the as-run sha256 of `scripts/f01_features.py`,
   `scripts/e01_base.py` and `scripts/d01_points.py` (`da86122b...`, `ddd1620a...` and `21e57b98...`, FROZEN.txt's "as run"), while
   the landed copies are the scrubbed ones; and they read `work/`, while this folder holds `inputs/`. The recipe: (1) copy `inputs/` to
   `work/`; (2) re-make `work/base.npz` with `scripts/e01_base.py`, `work/lab` a checkout of the lab at cfd7e641 (check-mask-ceiling: byte
   for byte, sha256 `c19c3a64...`); (3) restore the three as-run scripts by putting back the one lane-path line `SCRUB.json` records as
   replaced in each (the as-run sha256 holds only with the lane's own folder in that line, which is not given here; elsewhere, those three
   pins have to be relaxed by hand).
10. **The composition's evidence** (check-mask-ceiling, info). The declaration's section 6 cites AF4's frozen E220 forecasts, while
    `scripts/c01_af4.py` shows its C2 on E222's and E224's frozen forecasts (326 rows). The cited E220 file was checked as well (op time
    equal to MM1-v3.2's at 306 of 306 rows, every number equal off gemmLnc at 260 of 260): the declared statement holds.
11. **The scan words** (check-mask-ceiling, nit). `scripts/h01_freeze.py` builds its public-text scan words from split literals, one of
    them the owner's public handle in two parts; the same pattern is on the repository in `../../v3.3-cands/posimb/scripts/l01_land.py`
    (Q234's judged land). It is a frozen file and lands byte for byte.

## What the reference cannot say (verify-mask-ceiling)

New shapes (reading 4); clocks other than about 600 and 800 MHz, and shire counts outside its training set (reading 6); other kernels
(rgm211, gemmLnc), MB x NB = 1 and the whole chip, all out of its scope by construction; the counter's mean (MM1-v3.2's own); energy and
transistor switches beyond MM1-v3.2's W law at the new op time; and why a placement is slow (a forest gives no mechanism; mesh's set
alignment does, and beats it held out by mask).

## For the next blind day (the verifiers' advice; no point is chosen here)

- For never-run masks, its figures are LOMO 7.36% overall and 7.51% on E221's 363 cases, and only at shapes in its training set; at a new
  shape the 363 read 10.27% with each shape held out.
- Future keep rules should put the placebo on LOMO, or permute by configuration.

## NOT RUN

- check-mask-ceiling: the permutation-importance and group drop-out refits (REPORTED; re-read only); placebo draws but the identity draw
  and draws 0, 1 and 99; the LOMO placebo; `scripts/d01_points.py` (E224's and E221's points cross-checked instead).
- verify-mask-ceiling: the permutation-importance and group drop-out refits (the feature ranking stays REPORTED as the lane gave it);
  point-level placebo draws beyond 3; leave one placement out over every placement (LOSO-strict, LOMO and leave one shape out bound it);
  `scripts/d01_points.py`'s readers for experiments other than E221.
- This lane re-ran no number. It copied the folder, checked its hashes against the posted ones, added the lane's kept first FROZEN.txt
  write and this note, ran the public-text scans and committed.

SPDX-License-Identifier: Apache-2.0
