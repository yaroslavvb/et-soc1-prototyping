# Dated note 1 to 'MM1-v3.2 + mesh': its two checks, its freeze line, and how to read the README with them

*Sat 21 Nov 2026 (week 47), Pacific time. Written by land-cands4 (round Q238) from 03:36 PST. Desk only. No E223 or E226 datum and no
E226 file was opened, and no E226 point was chosen: the next blind day is registered after these freezes. Every number below comes from
the two checks named, which ran on committed data (GitHub main cfd7e641) and on this folder; each keeps the label its check gave it
(desk, post hoc, held out, REPORTED). This note changes no file of the folder: the README, the declaration, the code, the outputs and the
frozen record are committed byte for byte as mask-mesh left them.*

## What is committed here, and its freeze line

- **The folder** is mask-mesh's land, byte for byte: 52 files, `SHA256SUMS` among them (sha256 `bf6d5fb75e109658...`, 51 of 51 OK),
  written at 02:03:37 PST but the README and `SHA256SUMS` (02:05:52 PST), before either check began (check-mask-mesh at 02:07 PST).
- **The frozen record** `FROZEN.txt` (in the land as frozen; the lane's FROZEN.txt byte for byte) is final at **02:03:37 PST**, before
  any E223 or E226 datum. Its freeze line is the CORRECTION post **#1.30.1.2.1.1.1.1.1.1.2** on the owner's coordination thread at
  **02:23:42 PST**:

      487188c7f0ddce244f09abb05aeca4427e69d4be9133e87154863cdc4abec425  FROZEN.txt

  The first post, at 02:03:18 PST (#1.30.1.2.1.1.1.1.1.1, "FROZEN 02:02:13"), named `3d4942fa...`: the lane's first FROZEN.txt write,
  which `scripts/m04_freeze.py` rewrote at 02:03:37 after an edit to itself. That earlier record was not kept, so `3d4942fa...` names no
  file here (check-mask-mesh, medium; resolved by the correction, verify-mask-mesh). By the file times, no file FROZEN.txt names was
  written after 01:58:52 PST but `scripts/m04_freeze.py`. This commit is a later record, not the freeze line.
- **How to read FROZEN.txt.** Its 47 hash lines give each file's path in the lane's desk folder, as run, and its sha256 as run. Here the
  files sit where `scripts/m04_freeze.py`'s own copy map put them: `work/fit/<f>` and `work/<f>` -> `out/<f>`;
  `work/e224b/data-e224b.json` -> `out/inputs/data-e224b.json`; `work/fit/m03.log` -> `logs/fit-m03.log`; `work/fit-run1/m03.log` ->
  `logs/fit-run1-m03.log`; the declaration, the scripts and the other logs under their own names. 40 of the 47 are byte-equal here. The
  other 7 (`scripts/run.sh`, `s00_snapshot.sh`, `s00b_snapshot_more.sh`, `s00c_snapshot_e214src.sh`, `s01_reduce_e224b.sh`,
  `x01_e221_look.py` and `logs/m03-run1.log`) are landed with the box's paths written as placeholders (`SCRUB.json`), and each gives its
  as-run sha256 back when the placeholders are put back. Not named in FROZEN.txt, by design: `README.md` (written after the freeze;
  sha256 `85c465dc...`, as check-mask-mesh read it), `SCRUB.json`, `SHA256SUMS`, `out/inputs/lab-SNAPSHOT.txt` (the snapshot's record,
  which gained one line, E214's source, at 01:58:23 PST after the declaration's hash: README section 8) and FROZEN.txt itself.
- **The declaration** `DECLARED-mesh.md` (sha256 `f9e5a8681b87db6d...`) was hashed at 01:39:07 PST with the declared code and inputs
  (`DECLARED.sha256.json`), before any fit: the fit's first run started at 01:39:15 PST and checks the declared hashes at its start.
- **Added by this lane** (new files, listed in `SHA256SUMS-note1`): this note.

## The two checks

**check-mask-mesh: HOLDS WITH FIXES** (02:07-02:24 PST; desk; `/usr/bin/python3` 3.12.3, numpy 1.26.4; every numerical job
single-threaded in the round's CPU slots, one at a time). Its one fix was to the posted line, not to the candidate.

- FROZEN.txt's 47 lines equal the lane's files; the land's `SHA256SUMS` 51 of 51; `SCRUB.json`'s 8 files reversible to their as-run
  sha256; 50 of 50 landed files equal their lane source.
- The declaration came before the fit: hashed at 01:39:07; the fit's first run started at 01:39:15 and asserts the declaration's and the
  code's hashes at its start; the 13 declared code files equal FROZEN.txt's; 17 of 18 declared inputs are equal now (the snapshot's
  record gained one line at 01:58:23, after the fit's re-run ended at 01:57:31, as the lane disclosed).
- The fit and the held-out record, re-run by its own caller on its own snapshot of tools/matmul/mm1 at cfd7e641 (identical to the
  lane's): `out/params-mesh.json`, `out/holdout-mesh.json` and `out/points-scored-mesh.json` byte-equal; `out/fit-mesh.json` and the fit's
  log (69 of 69 lines) equal but for their times.
- 20 held-out predictions by its own code (8 leave one mask out, 4 leave one session out, 4 leave one experiment out, 4 leave one card
  out): largest relative difference 2.2e-16 (0.0 in sample).
- The keep rule on the lane's own numbers: K1 5.9746% (<= 11.409%), K2 LOSO 5.979%, LOEO 7.378% and LOCO 6.060% (each below MM1-v3.2),
  K3 +0.00064 points of the 0.05 allowed, K4 the placebo beaten 100 of 100 (9.93-11.89%, median 11.14%): KEPT.
- AF4: the composition holds by construction. The scope rule agrees three ways at 4,311 of 4,311 points; no scope point is gemmLnc (none
  of the 89 gemmLnc points is at a subset mask); AF4's frozen E220 cooperative rows carry MM1-v3.2's W at 260 of 260.

**verify-mask-mesh: HOLDS WITH FIXES** (02:24-03:20 PST; desk; numpy 1.26.4, scipy 1.11.4; numerical jobs single-threaded in slots under
a 4 GB cap). Its fixes are to the record, not to the frozen candidate.

- Re-derived by its own code, all equal: the features, by its own L3 simulation over the committed walk's own stream
  (`walk_v31.chip_steps`, not the lane's generator) with the pool bases it read from the 8 traced simulator runs (C, A, B back to back, 8
  of 8): 600 of 600 configurations, largest difference 0.0. The point table: E105-E219 3,231 of 3,231 and E220 156 of 156 against the
  committed tables; E221's 811 runs against the raw session records and its 733 cases; E222 70 of 70; E224 arm A 62 of 62 and arm B 59 of
  59, arm B by its own run of E208's reducer (`out/inputs/data-e224b.json` byte-equal). The constants a_set 0.737781 and a_hop 0.826568
  (7 starts and a 51 x 61 grid find the same minimum). Every held-out op time to 2.1e-10. K1-K3: KEPT. The declared placebo, draw for
  draw, beaten 100 of 100.
- The mechanism survives the tests the lane did not run. A stratified placebo, permuting only within the same shape and shire count, is
  beaten 100 of 100 (7.69-9.41%, median 8.68%): which shires collide carries the signal, not the mask size alone. 98.9% of the lead's
  MM1-v3.2 error variance lies between configurations (108 configurations on three cards); within one configuration across the cards the
  sd is 1.18%; no clock step on any aifoundry2 lead run; run order, die and clock correlate with the term's residual at r <= 0.29. On the
  NoC rail the collision shires use more energy per op than the time ratio explains in 13 of 14 comparisons (1.16-1.80 against
  1.14-1.27), which fits extra miss traffic.

## Read the README with these corrections

The README and the declaration are not edited. Where they say otherwise, these readings stand.

1. **Outside E221 the term is a tie that over-speeds** (verify-mask-mesh, medium). On MASK points outside E221 without a twin, each
   experiment held out: 7.109% -> 6.897% (n 556), the bias -0.24 -> -2.45 points, and the term is closer than MM1-v3.2 by more than 1
   point at 102 points and farther by more than 1 point at 102. E206-E214's subset points get worse (7.01% -> 7.39%, n 277); E215-E224's
   improve (7.39% -> 6.48%, n 251). a_set fitted on E221 alone is 0.868, on the other experiments alone 0.428; with each shape held out
   the lead reads 6.37% (with gemmL2x6x10 out, a_set 0.528 and a_hop 1.40). The form was designed on E221's residuals (the declaration's
   section 0), and K3 reads non-MASK points only, so no declared rule saw this. Read the README's held-out record as *post hoc, strongest
   at E221's own placements*. Where it works outside E221 is at E221's shapes in E214 and E217 (gemmL2x6x10 at 0xc, 0x88, 0x90 and
   0x110; gemmL1x12x8 at 0x44): +11% to +16% -> +0.7% to +3.4%.
2. **The B-side misses go beyond gemmL4x8x4** (verify-mask-mesh, medium). README section 5 names gemmL4x8x4 at small masks (and
   gemmL1x16x4 at 0x1). The 15 worst points outside E221 are all B-only moves (dA 0, dB -0.38 to -0.45) at KB 4-8 and small masks:
   also gemmL2x4x8 int8 at 0xf (E212, three cards), gemmL4x4x8 int8 at 0xff and gemmL12x4x8 at 0xff00 (E214). MM1-v3.2 reads -1% to -6%
   there, the term -11% to -18%; E206, held out, goes 6.03% -> 10.25% (bias -8.7). An A-only control cuts the bias outside E221 to -1.39
   (6.72%) but loses the lead (7.62%); a B-only control reads 8.27% on the lead.
3. **The B cap binds** (verify-mask-mesh, low). In row half 1 MM1-v3.2's B fresh share has median 0.0007 (B was just fetched), so the
   declared B move is capped there at 481 of 1,193 scope points (267 of 351 lead points): B receives a median 0.50 of the requested move.
   README section 4's reading of a_set below 1 ("the walk's L3 model over-states the card's miss changes by about a quarter") holds for
   A only; a_set is not the mechanism's own scale on B.
4. **The L3 geometry is not pinned** (verify-mask-mesh, low). Refitted with 8 other L3 geometries or pool layouts, the lead's
   leave-one-mask-out rms reads 5.97-6.74%: B pool +4 MiB 5.973%, +2 MiB 5.986%, C last 6.004%, 2-way / 16 MiB 6.076%, B +1 MiB 6.077%,
   8-way / 4 MiB 6.196%, no C stores 6.242%, 16-way / 2 MiB 6.744%, against the declared 5.975% (B +4 MiB with a lower in-sample cost,
   4.1397 against 4.1491). Every variant's features are <= 0 at all 458 configurations. The data support a set-conflict mechanism, not
   the documented 4-way 8 MiB decode or the back-to-back pools in particular: read both as *assumed*, as README section 2 labels them.
5. **The calibration** (verify-mask-mesh, low; REPORTED). The set model's full-chip miss shares and MM1-v3.2's fitted full-chip fresh
   shares agree in shape (r 0.92 for A, 0.89 for B) but not in level (rms difference 0.17 and 0.26; for example gemmL1x8x12's A share is
   0.89 in MM1-v3.2 against 0.24 in the set model). The term applies the set model's differences to MM1-v3.2's map.
6. **K3 is diluted** (verify-mask-mesh, low). Of K3's 2,341 non-MASK points the term changes 193 (1.508% -> 1.536%, each experiment held
   out); the rest it cannot move.
7. **"posimb beside" sets blind against post hoc** (verify-mask-mesh, low). README section 5's table sets posimb's frozen, blind errors
   (from blind-e221's case table) against this term's post hoc leave-one-mask-out errors (re-read equal: 12.33% against 6.04% on 351
   cases). The fair comparator is mask-posimb's refit beside this folder (`../posimb-mask/`: 8.13% on E221's 363 MASK cases by leave one
   session out, also post hoc).
8. **It cannot slow a subset** (the lane's own finding, confirmed by verify-mask-mesh). Every feature is <= 0 at all 458 subset
   configurations in all 9 geometries, so the masks where the card is 10-19% slower than MM1-v3.2 (8-31 shires with fewer than four
   column groups) stay as they were: PLN 13.39% -> 13.64%.
9. **The record** (check-mask-mesh, low). The lane's progress log and result do not record the first freeze run (02:02:13) or the edit of
   `scripts/m04_freeze.py` before the second run (02:03:37); what changed in it is unknown, as the earlier copy was not kept.
   `scripts/t03_call_from_land.py` and its log were written in the lane's folder after the freeze (02:04:01); they are not in FROZEN.txt
   and not here. `scripts/m04_freeze.py` hashes every script of the lane's folder, so it must not be re-run there: it would write a new
   FROZEN.txt.
10. **The labels** (check-mask-mesh, info). The lane's rule labels every non-MASK E221 case 'OTHER'; the literal labels agree with
    decl-e221's at 392 cases, and the MASK flag at 733 of 733, as README section 4 states.

## What the term cannot say (verify-mask-mesh)

Why the cards are slower at 8-31-shire masks with fewer than four column groups; anything about energy (it moves no watt, though the NoC
data show extra traffic); which L3 geometry and pool bases the cards have; rgm211, gemmLnc or run_gemm (out of its scope); the counter's
mean (not scored); and whether its E221-scale a_set holds at new shapes, where the evidence says it is about halved.

## For the next blind day (the verifier's advice; no point is chosen here)

- Shapes unlike E221's (KB 4-8, NB 4-8, small masks) and collision-set pairs at equal shire count, the term scored against MM1-v3.2
  there.
- The alternative geometries' forecasts printed at the day's points before its freeze, so the day can separate them where they disagree.
- A later declaration should guard the non-lead MASK points; a later form should take B's set-model change per row half and cap it
  there, or filter the L2.

## NOT RUN

- check-mask-mesh (left to the verifier, who ran them): the point table, the features from the walk, E224 arm B's reduction.
- verify-mask-mesh: a joint refit with MM1-v3.2's constants; a trace of the card's pool bases or of a collision pair; E105-E219 and E220
  from raw data (equality to the committed tables only); AF4's frozen E220 rows re-made numerically (by construction only); the
  counter's mean.
- This lane re-ran no number. It copied the folder, checked its hashes against the posted ones, added this note, ran the public-text
  scans and committed.

SPDX-License-Identifier: Apache-2.0
