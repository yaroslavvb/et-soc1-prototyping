# Q140(x)'s dated notes after verification: the numbers behind them

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6**. Q139's final critic, **ranks 1, 4 and 2** (M9 on a seventh blind pool, the paired-anchor card scale, aifoundry2's session terms). Written Wed 4 Nov 2026 (week 45) from 04:03 PST by Q140(x)'s fix pass, desk only, on the Intel. No card was opened, no device command was sent and nothing was measured, fitted or scored.*

This directory holds the check behind the four dated notes, A1-1 to A1-4, added to
[`tools/claims-v3/kinds/blind7/README-predictions.md`](../../../../tools/claims-v3/kinds/blind7/README-predictions.md#dated-notes-after-verification-a1)
after its gate commit `75802201` (03:27:39 PST), its verification, and before any pool-7 claim, launch, measurement or
score. The notes are inserted lines only. Every other file of blind pool 7's directory is unchanged: the pool, the counts,
the predictions (`.json` and `.md`), the 82 W list and rank 4's rule.

## Results

[`notes_check.py`](notes_check.py) reads git objects only, at the gate and at a later commit. It writes [`notes-check.json`](notes-check.json).

- **A1-1, aifoundry2's `.md`.** `predictions-blind7-aifoundry2.md`'s "M9 MHz" and "M9 board W" columns equal M9's top-level
  `burst_mhz` and `burst_board_w` on 61 of 61 rows. Those fields are M9's D through M8's frozen relation. The registered
  primary is `M9.a2_q140l`, and the `.md` reads against it:
  - on the 18 governed tiles, 1.63 to 2.50 MHz low and 0.68 to 1.98 W low;
  - on the 43 pinned ones, 0 to 0.83 MHz low and 0.20 to 0.99 W high.

  The peaks agree to 0.005 W, and so do all 61 of the 82 W flags. README-predictions.md's own table equals `M9.a2_q140l` on
  61 of 61 rows (`A1_1`).
- **A1-2, a byte twin.**
  - The twin: pool 7's `fp32.b_onebit_b20_pi` and M9's bench-calibration tile `fp32.cal_pi_b20` (committed in `1f244140`)
    share sha256 `af4296a2…8def10`.
  - The scan: the tree holds 10,928 two-kilobyte blobs outside pool 7's directory, 1,071 of them all zeros, at both
    commits. This is the only whole-tile repeat of a pool-7 tile other than the zeros.
  - The bytes: both are A = 1.0 and B = π with bit 20 set in columns 8-15.
  - The recount: M9's committed 27-point recount puts the three-point launch average 0.311 ± 0.198 W below the 27-point
    one at M9's prices (`recount-rule.txt` line 32).
  - M9's frozen D for the tile: 12.093 W on aifoundry3 and 11.628 W on card 1. Neither `fit_m9.py` nor `predict_blind7.py`
    reads the calibration counts (`A1_2`).
- **A1-3, aifoundry2's nested errors.** These are Q140(l)'s committed corrections, C4. With the selection nested, the held-out
  errors are:
  - governed clock 5.12 / 6.90 MHz;
  - governed board 0.93 / 0.89 W;
  - pinned board 0.92 / 0.88 W.

  The registered figures are 5.00 / 0.89 / 0.75. The bands' rule on the nested errors gives the widths below (`A1_3`):

  | band | frozen | nested |
  |---|---|---|
  | governed clock | 9.65 MHz | 9.77-11.97 MHz |
  | governed board | 1.85 W | 1.84-2.06 W |
  | pinned clock | 15.35 MHz | 15.20-15.35 MHz |
  | pinned board | 1.26 W | 1.48-1.75 W |
- **A1-4, the order stamps.** By the clone's reflog:
  - `HEAD` was `c9aaf179` from 02:46:04 to 02:49:40 PST;
  - `origin/main` was `c9aaf179` from 02:46:15 to 02:50:04.

  So the lane's "HEAD = origin/main = c9aaf179" check ran between 02:46:15 and 02:49:40, not at its 02:50:38 stamp. The
  reflog is a local record. The commit times are in the git objects (`A1_4`).

## What this does to predicting power and heat

Nothing is fitted, measured or scored, and no frozen prediction, band or rule changes. The notes correct what the gate
tells its scorers in three ways.

- **E165 reads the right prediction.** It scores M9's registered aifoundry2 part, `M9.a2_q140l`. The `.md`'s M9 columns
  differ from it by up to 2.5 MHz and 2.0 W.
- **aifoundry2's honest out-of-sample error is the nested one** (from M7 as frozen):
  - governed clock 6.25 → 5.1-6.9 MHz;
  - governed board 1.62 → 0.89-0.93 W;
  - pinned board 1.52 → 0.88-0.92 W.

  The frozen pinned-board band may under-cover.
- **One blind pool-7 tile carries a known counting component.** On `fp32.b_onebit_b20_pi`, about +0.31 ± 0.20 W
  (measured minus M9) is expected from M9's own recount.

The error after is what E163, E164 and E165 measure on the frozen files.

## Commands

```
python3 -B docs/reports/data/2026-11-04-q140x-blind7-notes/notes_check.py . 75802201 <a later commit> > docs/reports/data/2026-11-04-q140x-blind7-notes/notes-check.json
```

The later commit used here is named in `notes-check.json` (`A1_2.scan`).

SPDX-License-Identifier: Apache-2.0
