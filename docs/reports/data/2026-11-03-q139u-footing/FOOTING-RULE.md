# Q139(u): one reduction footing, the rule (written and committed before any row is re-read)

*Written Tue 3 Nov 2026 (week 45), about 04:05 PST, on the Intel, before this lane computed anything on any kinds row or
on any pass's telemetry. It answers Q138's final critic's open rank 1 (the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6) and the desk part of
rank 5 (E142's registered X1/X2 scored on one footing). What was read before writing it: the reducers' code
(`tools/claims-v3/kinds/reduce_e78.py`, `reduce_e82.py`, `posthoc_dips_e82.py`, `tools/claims-v3/e141/reduce_e141.py`,
`tools/claims-v3/e143/reduce_e143.py`), the row assembly (`fit_m5.assemble`, `m6_rows.py`), Q138(m)'s README and the
critic's text. No row, no pass, no reduced JSON value was opened.*

## Why a footing at all

M7's 247 aifoundry3 float training rows were reduced at leakage slopes of 0.140-0.296 W/°C, each session fitting its own,
and under two rules for the board meter's dips (kept in 154 rows, removed in 93). The blind tests E140-E142 were reduced
at their own sessions' slopes. In E78's reduction a run's D is
`D = P_raw - Z_raw - k (dT_run - dT_zeros)`, the window's die rise over the launch reading times the slope, so D moves
with k by about 0.12 °C per board W x Δk x D: 2% of a 20 W float kind for Δk = 0.16 W/°C, the size of the whole model
error. One footing means one k per card and one dip rule, applied to every training row and every test alike.

## The choice: (a) one leakage slope per card from its idle rests, not (b) the die temperature as a model input

1. **Identification.** In a kinds run the window's die rise is set by the run's own power (about 0.12 °C per board W over a
   4.5 s run), so a temperature term fitted jointly with the per-flip prices is nearly collinear with D itself: its slope
   trades against every price and the card scale. An idle rest has no switching, so the slope it gives is independent of
   the bits.
2. **One number, frozen before new data.** (a) gives one constant per card, applied to every training row and every test
   session, and frozen before a new session exists. (b) would make every prediction carry a die-temperature input that a
   blind prediction must itself predict.
3. **Like for like.** M7's form is kept as it is, so M7u is M7's form refitted on one footing, nothing else.
4. **No new reduction code.** Every kinds reducer already takes the slope as a parameter (`--leak <k>`), so each
   experiment's own registered reducer runs unchanged.

## F1. The leakage slope, per card

For each card c (aifoundry3 card 0; aifoundry1 card 1), **k_c is the common slope of board power on die temperature over
that card's idle rests, pooled over all its sessions:**

- **an idle rest** is the reducer's own idle bracket before each run: mean `board_w` and mean die reading
  (`temp_c.minshire[0]`, the reducer's T) over [t0 - 1.2 s, t0 - 0.2 s), t0 the run's first launch record, as
  `reduce_e78.runs_of_pass` computes them, on the telemetry with the dips removed (F2);
- **a rest counts** if it is valid by the reducer's idle test (at least 8 samples; starting at least 0.8 s after the
  previous device process ended; its mean die reading within 1.5 °C of the run's launch reading) and its run passes
  every per-run gate that does not depend on k (clock 600 MHz, the voltage band, the launch protocol, records ok, cycles
  per op, window samples and gaps, duty, the tile dump). Pass gates are not applied: they depend on k;
- **the sessions** are every pass directory read by the primary reduction of any experiment that contributes rows to M7's
  637 or to E140, E141 or E142 (its JSON's `dirs`), on that card;
- **the fit** is ordinary least squares of the rest's board W on its die reading with one intercept per pass and one
  slope per card (only the within-pass relation measures leakage: a pass's idle level also moves with the room and the
  board). Its interval is a bootstrap over passes (2,000 draws, seed 139);
- **frozen** in `footing.json`. Later lanes on these two cards (pool 6) use the frozen k_c and never refit it on their own
  sessions.

## F2. The board meter's dips: E82 amendment A2's rule, everywhere

Drop telemetry sample i when `board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W`, on every pass of both cards, before
any reduction or rest fit reads the telemetry (E82 A2's definition; `reduce_e141.drop_dips`'s code).

## F3. Everything else is each experiment's registered reduction, unchanged

Each experiment's own registered reducer (the wrapper its primary JSON names) runs unchanged on dip-filtered copies of
the same pass directories with `--leak k_c` and `--no-refit` (the rail's lag re-fit is an instrument check that does not
enter D). Its per-run gates, pass gates, zeros interpolation, `D = p80 - Zhat_type(t0)` and statistics are its own.
Whatever passes its gates keep at this footing are used; nothing is chosen after the fact. An experiment left with no
kept pass is left out of M7u and named; a row whose experiment and key have no D at the footing is left out and named.

## F4. aifoundry2 (E143)

E143's governed bursts and the bursts M7's aifoundry2 term was fitted on (E80, E83) share E80's burst reduction: board W
as sampled, no leakage term, D the burst W less the same pass's zeros burst. That is already one footing. F2 is applied
as a check: A2's dips are counted in every counted burst's sampled window; if any are found, E143 is re-scored with them
removed, else it stands as committed.

## The analysis, fixed here (all of it post hoc)

1. `rows-m7u.json`: M7's 637 rows (Q138(m)'s assembly: the same keys, tiles and features) with D, its se and the window
   rise from the F1-F3 reduction; rows lost are named.
2. **M7u**: M7's frozen forms (the float and int8 forms `m7.json` names, its card term as M7 defines it) refitted on
   `rows-m7u.json`; nested leave-one-kind-out as `fit_m7.py` runs it, with M5's, M6's and M7's forms on the same folds.
3. E140, E141 and E142 re-reduced under F1-F3 and re-scored: (i) the frozen predictions (M7, M6, M5) against the
   re-reduced measurements; (ii) M7u's predictions (for E140, M7u refitted without E140's rows; for E141 and E142, M7u on
   all rows) against them: rms, bias against B1 (floats) and B2 (int8) as each lane registered them, and coverage with M7's
   frozen band half-widths.
4. E142's registered X1/X2 (`tools/claims-v3/e142/score_e142.py`) on the re-reduced E141 and E142, against M7's frozen
   card scales and against M7u's.
5. **The decisive reading (the critic's), reported either way:** the blind float bias inside B1's band on both 600 MHz
   cards, and X1's measured ratio inside its interval.
6. `reduce_footing.py`: F1-F3 as functions (the dip filter, the rests, the slope fit, the re-reduction driver, the frozen
   k_c) for later lanes to import.
