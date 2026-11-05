# Q142(p): pool 8's one frozen predictor - M10 primary with M9 beside, on any pool in pool 7's form and on four cards; every self-test passes: M10's committed in-sample predictions for pool 7's 104 rows to 1.4e-14 W, its held-out predictions to 5.0e-7 W (they are stored to 1e-6 W), the heat-over-minutes primary factor exactly 1.0, refusal without the convergence rule's counts, Q140(l)'s aifoundry2 part and E170's card term field for field, M9's committed pool-7 predictions exactly, and an end-to-end pass

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, a power model across kinds, with items 8 and 9 (heat). It answers the Q142 critic's `m10` field, items (2)-(7), and its
`next` ranks 2 and 3. The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of
numeric computations as accurately as possible.*

*Wed 4 Nov 2026 (week 45), desk only on the Intel: no card, no device command, no lab box, no post in the lab's channel, no Modal, no
archive. **Registered first:** [`../../../../tools/claims-v3/m10/POOL8-REGISTRATION.md`](../../../../tools/claims-v3/m10/POOL8-REGISTRATION.md)
(`3e97f583`, 23:11:53 PST), with its numbers (`pool8-registration.json`) and hash lists (`POOL8-SHA256SUMS`, 209 files;
`POOL8-SHA256SUMS-62`), before this directory existed; then its dated note A1
([`POOL8-REGISTRATION.md.dated-note-1.md`](../../../../tools/claims-v3/m10/POOL8-REGISTRATION.md.dated-note-1.md), `8a8fa34c`, 23:26:44).
The pool's designer committed its design file afterwards (`153b720f`, 23:22:03); this lane never read it or the designer's scratch.
**No pool 8 exists here and nothing here predicts any pool-8 tile**: the next round's (x) lane runs this predictor on the pool.*

## What it is

[`predict_pool8.py`](predict_pool8.py), standard library and numpy 1.26. It reads M10's `m10.json` and `m10-s7.json` through
`predict_m10_s7.py`, M9's `m9.json`, Q140(l)'s aifoundry2 part through `e165_common.m9a2()`, and E170's card term through
`e170_common.pred_card0`, after checking every input against `POOL8-SHA256SUMS` and M10's own lists. Nothing is fitted.

| mode | what it does |
|---|---|
| `predict <pool> <card> --counts …` | the frozen file per card (aifoundry3, aifoundry1c1, aifoundry2, aifoundry1c0): per tile M10's D per unit rate (s = 1), at the stated rate, its band, the pass-1 coefficient for the scale, the three-point arm, the 4.5 s rise; M9 beside; on the governed cards M10's and M9's D carried through Q140(l)'s part at the fallback and T_ref, card 0's burst D through κ0, and the 82 W flag. **Exit 3 and nothing written** if a float tile's counts do not reach its convergence-rule N or the anchors' roles cannot be read |
| `plan <pool> --counts …` | per float tile: the N reached, e(N) and the launch points the next step needs (the bench work for the mini) |
| `scale <predictions> <reduction>` | the session's float scale from its scale anchors' items only (M10's own float anchors it ran, and pool 8's) |
| `primary <predictions> <reduction> <scale>` | M10's primary at each tile's measured rate × the scale; the a-priori arm (s = 1), the pass-1 arm, the three-point arm, M9 at the same and at the nominal rate, the 4.5 s heat |
| `burst <predictions> --anchors … --die-starts …` | the governed bursts recomputed with the session's zeros-anchor reads and each tile's die starts (E165's and E170's form); on card 0, M10's rise at 0.2415 °C per board W |
| `heat-minutes <rise> …` | a hold's chain rise × 1.0 (the primary) and × 1.032 (the arm) |
| `intervals <predictions>` | P8-P1-P3's bootstrap lines at the pool's own n |
| `selftest` | T1-T9 below |

## Results: the self-test ([`selftest-pool8.json`](selftest-pool8.json), [`selftest-pool8.txt`](selftest-pool8.txt))

| test | what it checks | reading |
|---|---|---|
| T1 | the heat-over-minutes primary factor is `chain_gain_primary` = 1.0, never `predict_m10.chain_gain()`; the arm 1.03199 | 1.0 and 1.03199; on the nine large rises the primary's plateau errors equal arm A's committed ones within 8.9e-16 °C, the arm's equal e − 0.03199 P within 2.1e-15 °C; the registered 4.5 s band rms equal `heldout-m10.json`'s |
| T2 | pool 7's 104 rows in sample: features through the chain, the S tiles' N-point counts by this file's own convergence rule, each session's scale by this file's code | within **1.4e-14 W** of `rows-m10.json`'s `M10_insample_pred_w`; the 8 S tiles reach M10's N with e(N) equal within 6e-16 W |
| T3 | pool 7's 52 kinds held out: each kind's fold re-derived by `fit_m10.Fit10.fit(k)`, its prices, card term and session scales fed to this file's formula | within **5.0e-7 W** of the committed held-out predictions (D − `err_w`, stored to 1e-6 W) and within 7e-15 W of the fitter's own |
| T4 | refusal | b20_one with three points: refused (needs N = 9); to 27 points: refused at e(27) 0.142 W (needs 81); to 81: N 81, e 0.0954 W, as M10 read it; three random fp32 anchors with no check: refused, and accepted with a roles file; nothing written |
| T5 | aifoundry2: M9's path through Q140(l)'s part on pool 7 | all 61 tiles' `M9.a2_q140l` blocks identical field for field to `predictions-blind7-aifoundry2.json` |
| T6 | card 0: M9's path through `e170_common.pred_card0` on E170's committed reads; M10's c2 on E170's measured boards | all 39 tiles' primary blocks identical; k 0.24149 → 0.2415, the leave-one-tile-out rms 0.33852 → 0.3385 °C, as `heldout-m10.json` |
| T7 | M9 at 600 MHz on pool 7, both cards | D, its band and the 4.5 s rise equal `predictions-blind7-aifoundry3.json` and `-aifoundry1c1.json` exactly after their rounding |
| T8 | every repo file the self-test opens or imports is in `POOL8-SHA256SUMS` or this directory's [`SHA256SUMS`](SHA256SUMS), and each hashes as listed | 222 files opened or imported, none unlisted; the 209 and this directory's 16 entries hash as listed |
| T9 (added, A1-5) | end to end: `predict` → `scale` → `primary` on E163's and E164's committed reductions; `burst` on E170's reads | scales 1.009905 / 1.010244 (m10.json 1.00991 / 1.01024); primaries within 1.8e-15 / 7.1e-15 W of M10's in-sample; card 0's M9 blocks identical on 10 tiles, M10's rise at 0.2415 °C/W; pool 7's zeros anchors keep each format's own points |

The stated rate (the registration's § 4) reads as registered: nominal less 0.3355% (fp32), 0.335% (fp16), 0.2275% (int8) on
aifoundry3 and 0.346%, 0.3445%, 0.276% on card 1.

## How the (x) lane uses it, in order (the registration's § 10)

1. Copy pool 8 unchanged into `tools/claims-v3/kinds/blind8/`.
2. On the mini (`run_remote --host mini`, the build Q141(t2) recorded, `-fno-dfg`, one point first checked against the Intel's
   build): the bench's three standard points for every tile (`run_kinds.py`'s defaults), then `plan` and the points it names for every
   float tile, repeated until `plan` reads every float tile complete (N = 9 first; tripled while e(N) > 0.10 W; at most 243). Committed
   points of a pool-6, pool-7 or calibration tile with the same bytes and type are reused, unless `--no-reuse`.
3. `predict` for aifoundry3, aifoundry1c1, aifoundry2 and aifoundry1c0; pass `--roles` only if the manifest does not state each random
   anchor's role and a format holds three or more of them (the predictor says so). Mark aifoundry2's tiles whose larger 95% upper peak
   (M10's or M9's) is over 82 W (`admission_82w_out`). Print `intervals` for both 600 MHz cards.
4. Commit the pool, the counts and every output in one commit before any claim.
5. After each session: `scale` (from the anchors only), then `primary`; on the governed cards, `burst` with the session's reads. The
   scoring rules are the registration's § 7.

## What this does to predicting power and heat

It makes M10's held-out figures testable blind, with nothing left to choose after the pool exists: the frozen file fixes M10's D per
op for every tile before a card runs, and the session's own anchors fix the only number read from the session (the float scale),
mechanically and before any scored tile is read. Before: M10 had no frozen predictor for a new pool (its own `predict_m10.py` names
pool 6's and 7's anchors and takes term b's counts from M10's directory), its heat-over-minutes factor could be read from
`predict_m10.chain_gain()` (the 1.032 arm), and aifoundry2 and card 0 had no M10 path at all. After: one file predicts all four
cards; the primary heat factor is asserted 1.0; term b runs on every float tile by its convergence rule, never by a class label;
M10's D reaches aifoundry2 and card 0 by registered rule E through parts fitted on measured D, so their governed bursts test M10 too.
The error figures this sets out to test are M10's held-out ones (floats 0.185 W, pool 7's 48 kinds 0.205 / 0.187 W; heat over
4.5 s 0.233 °C; card 0's bursts 0.34 °C; large rises 0.49 °C unscaled) against M9's blind 0.278 / 0.273 W. Pool 8 will say which.

## Departures and disclosures

- **Dated note A1** (committed before this directory): equal bytes count as the same tile only in the same format (found by this
  file's first development run of `plan` on pool 7, which merged fp32's points into fp16's zeros anchor); anchors never enter the
  re-run set; int8's three points are the bench's own; the scale's nominal-rate fallback mirrors `fit_m10.assemble_anchors`; T9 added;
  the registration's dateline (last written 23:10:31, committed 23:11:53). A1's own dateline says "about 23:26-23:30": it was last
  written at 23:26:28 and committed at 23:26:44, so its stated end also ran past the commit.
- **Development runs:** three passes of the self-test (23:21-23:24 PST) and one of a CLI smoke (`plan`, `heat-minutes` and `predict`
  on pool 7, which refuses as it should), all through the round's local slot, one job at a time, outputs only in the lane's scratch.
  The committed self-test is the run after the last code change.
- **The registration's T3 tolerance** is 5e-7 W, not 1e-9 W, because `rows-m10.json` stores the held-out errors rounded to 1e-6 W
  (registered in § 1); 1e-9 W holds against the fitter's own unrounded predictions (7e-15 W) and in T2.
- **Seen by accident** (the registration's § 0): the tail of the round's shared job log named the designer's scripts.

## Files

| file | what |
|---|---|
| `predict_pool8.py` | the predictor, its modes and its self-test |
| `selftest-pool8.json`, `selftest-pool8.txt` | the committed self-test: every reading, and the one-line summary |
| `SHA256SUMS` | this directory's list: the predictor, this README, the registration's files and the nine pool-7 anchor tiles the self-test reads (not the self-test's own output) |

## Re-run

From the top of the tree, with numpy 1.26: `python3 -B docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8.py selftest
--out <file>` (about 10 s); then `shasum -a 256 -c tools/claims-v3/m10/POOL8-SHA256SUMS` and `shasum -a 256 -c
docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS` (both lists' paths are relative to the top of the tree).
