# Dated note 2 beside REGISTRATION.md (Fri 6 Nov 2026, week 45, about 03:12 PST): a governed fall costs less than the term says; a reported catch-up arm, before any governed session

*This note sits beside [`REGISTRATION.md`](REGISTRATION.md) and its [dated note 1](REGISTRATION.md.dated-note-1.md) and changes
nothing in them. `dipterm.py`, every parameter, rule and arm, `score_dipterm.py`, `score_dipterm_v2.py` and the hash lists
`SHA256SUMS` and `SHA256SUMS-1` stay as committed (`7a099fb9`, `fe4fdf92`). It follows the post hoc study (`006c85eb`) and comes
before any session the term governs: none has run.*

## What the post hoc study found (POST HOC, E173-E175)

The study is [`2026-11-06-q145b-dips-posthoc/`](../../../docs/reports/data/2026-11-06-q145b-dips-posthoc/README.md), results 3 and
4. Each fall's pass was set against the same tile's passes with no fall:
- **A pinned fall** costs what the term says:
  - aifoundry2: 48.0, 50.0, 20.4, 47.1 and 47.1 MHz measured, against 48.5, 51.1, 19.6, 47.8 and 47.7 MHz from the term;
  - card 0: within 0.2-4.6 MHz on six falls.
- **A governed fall costs less.** E175's three governed falls cost 24.2, 21.7 and 27.0 MHz, against the term's 32.4, 37.5 and
  39.2 MHz. That is 0.749, 0.579 and 0.687 of the term's cost, **0.67 on average**.
  - This is the power arm's catch-up, which the registration states it leaves out: after a dip the filtered power is lower, and the
    clock holds 800 MHz longer.
  - On the board, the same falls cost 4.09, 2.14 and 3.58 W measured, against 4.21, 4.86 and 4.93 W from the term.
- **On E175 the seq arm makes G worse** (4.49 to 5.15 MHz rms, mean +0.12 to +1.97). Three things add up:
  - the over-stated governed cost;
  - the session's first fall came at burst 68 of 126, so half the session carried the count's expected loss on every pass;
  - with every fallen pass dropped, G reads mean +1.18 MHz.

  The last suggests that the governed predictor already carries part of an average loss, because it was fitted on bursts that
  dipped. That is a **hypothesis**, not registered here: a mean of +1.18 MHz over 16 tiles at 4 MHz rms is about one standard error.

## The amendment: one reported arm, seq-gc

[`score_dipterm_v3.py`](score_dipterm_v3.py) is v2 unchanged, plus the arm **seq-gc**.
- **What it is:** the seq arm, with every governed pass's expected clock and board deficits multiplied by **K_GC = 0.67**. A
  governed pass is a counted pass of a tile in the run's own governed set (`score.reported.tiles` > `group` or `set`). Every other
  pass is unchanged.
- **K_GC is post hoc,** fitted on those three falls. Its first test is blind, on the next governed session that keeps the gaps.
- **Its standing:** seq-gc is **REPORTED** beside DT-G and DT-Bp, never a verdict. DT-G and DT-Bp stay registered on the seq arm,
  as REGISTRATION.md section 3 gives them.
- **What would promote it:** if seq-gc reads a lower DT-G rms than seq on that blind session, a later dated amendment may promote it
  before a second governed session. One session decides nothing more than that.

A governed session's registration names `score_dipterm_v3.py` and this note's list [`SHA256SUMS-2`](SHA256SUMS-2), and scores the
arms none, count, seq and seq-gc.

## Files

| file | what |
|---|---|
| `REGISTRATION.md.dated-note-2.md` | this note |
| [`score_dipterm_v3.py`](score_dipterm_v3.py) | the scorer, v3: v2 plus the reported arm seq-gc |
| [`SHA256SUMS-2`](SHA256SUMS-2) | this note and v3, plus every file `SHA256SUMS-1` lists and `SHA256SUMS-1` itself, all unchanged |

SPDX-License-Identifier: Apache-2.0
