# Q140(l) registration: aifoundry2's level and session terms, with the clock-voltage term

*Wed 4 Nov 2026 (week 45), about 00:10-00:55 PST, on the Intel. Desk only: no card, no device command, no ssh, nothing
from the private archive. Written and committed **before any fit, score or prediction of this lane was computed**.
It answers Q139's final critic's **rank 2** ("aifoundry2's level and session terms ... desk-testable now leave one
session out on E80/E83/E143/E160") and **rank 8** ("fit s(f) jointly with the session term ... leave one session out"),
on the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)
items 6 (a power model across kinds), 8 and 9 (heat over minutes, through the level) and 1 (the large GEMM, through
the level). The owner's goal, 2 November 2026: to predict the power requirement and heat generation of numeric
computations as accurately as possible.*

## What was read before this registration, and what was not computed

Read: the committed READMEs and result files of E80, E83, E143, E160 (with E160's corrections, `42ba850f`), E159 and
E161; M7 (`docs/reports/data/2026-11-02-q138m-model/`), M8 (`docs/reports/data/2026-11-03-q139m-model/`, frozen in
`122da8b6`), Q139(s)'s chain and voltage reads (`docs/reports/data/2026-11-03-q139s-clock-voltage/`), Q139(u)'s footing,
Q139(e)'s composition, and Q139's final critic's report with its desk check of the exponent on E160. The four
sessions' raw cell listings were printed (each cell's measured burst clocks, board watts and die starts per run, with
no model prediction beside them). So the sizes of the shared offsets the committed READMEs quote were known: the
governed board about +1.1 W over the model in E143 and E160, the pinned board 0.8-1.5 W under it, the zeros anchors
1.1-2.7 W under M8's 800 MHz zeros level, the die-start slope of 0.37-0.39 W per °C inside E143 and E160, and the
governed clock's mean error -4.96 MHz (E143, M7) and +2.82 / +5.17 MHz (E160, M7 / M8).

Not computed before this commit: any fit, any leave-one-session-out prediction, any score of a candidate term, and
any score of M7 or M8 on E80 or E83 by session. The candidate terms are the four the critic and Q140's brief name. Their
forms below are fixed here, and no other term or form is tried.

## Data (committed; nothing re-run)

| session | data dir | cells | zeros anchors (inputs, never scored) | runs per cell |
|---|---|---:|---|---:|
| E80 (31 Oct) | `2026-10-31-e80-kinds-speed` | 18 | `fp16/zeros`, `int8/zeros` (no fp32 anchor) | 2 |
| E83 (31 Oct) | `2026-10-31-e83-kinds-speed-rest` | 38 | `fp32/zeros`, `fp16/zeros`, `int8/zeros` | 2 |
| E143 (2 Nov) | `2026-11-02-e143-blind5-aifoundry2` | 39 (36 pool-5 tiles, 3 session-link cells) | `b5-{fp32,fp16,int8}.anchor_zeros` | 3 |
| E160 (3 Nov) | `2026-11-03-e160-blind6-aifoundry2` | 50 (48 pool-6 tiles, 2 replicates) | `b6-{fp32,fp16,int8}.anchor6_zeros` | 3 |

- **Measured, per cell:** the burst clock and board power as committed in each `results.json` › `cells` (`burst_mhz`,
  `burst_w`: the mean over the cell's burst runs, every run counted as registered, idle-status runs included). **Per
  run:** `burst_mhz`, `burst_w` and `die_start` (E80/E83: `runs` with `block` BURST and `kind` the cell; E143/E160:
  the cell's `*_runs` lists, one entry per pass).
- **Scored cells:** every cell except the zeros anchors: E80 16, E83 35, E143 36, E160 47 (134 in all), provided it has
  a measured D (below). A cell without one is dropped and listed.
- **D (the primary input):** the measured D on aifoundry3 at 600 MHz on Q139(u)'s footing (`items[key].D.mean`):
  E78's rows (`2026-11-03-q139u-footing/reduced/e78-footing.json`, key `<type>.<kind>`) for E80's and E83's kinds and
  for the session-link and replicate cells (`k-<type>-<kind>`); E141's rows (`…/reduced/e141-footing.json`, key = the
  tile's name) for E143's pool-5 tiles; E153's registered primary (`2026-11-03-e153-blind6-aifoundry3/e153.json`, the
  same footing, 0.2056 W/°C) for E160's pool-6 tiles. The relation is fitted and scored on measured D in every arm, so
  the arms differ only in aifoundry2's relation, which is what this lane tests. (M8's aifoundry2 configurations were
  fitted the same way, on E78's and E141's footing rows.)
- **Groups (fixed for every arm and every fold):** a cell is *governed* if M8 as frozen (below) predicts its burst clock
  below 795 MHz from its primary D, else *pinned*.

## The base relation, and the two reference lines

Every arm uses M8's aifoundry2 relation (`m8.json` › `aifoundry2`): levels L(f) = B(f) + c·s(f) at f = 600, 700, 800
MHz with B = 25.4556 / 28.2433 / 33.6096 W and s = 1 / 1.40819 / 1.90517; c = c_zeros[t] + g·D with c_zeros = 1.440 (fp32),
1.394 (fp16), 2.123 (int8) W and g = 1/1.01865; the burst clock f = E83's dither of the levels about a cap W with
σ = 2.75 W (`tools/claims-v3/e119/make_predictions_e119.py` `dither`, unchanged); the board at the clock = the levels
interpolated at f (M8's `p_at`). A cell's prediction is the mean over its runs of each run's prediction.

- **R7, M7 as frozen:** W = 65.580 W. Its cap was fitted on E80's and E83's bursts, so R7 is in sample on E80 and E83
  (for the cap) and blind on E143 and E160.
- **R8, M8 as frozen:** W = 65.20 W. Its cap was fitted on E80's, E83's and E143's, so R8 is blind on E160 only.
- **A0, the base:** M8's form with W refitted in each fold on the three training sessions (stage S2 below). Every
  candidate is tested against A0 or against the configuration kept so far, never against R7 or R8.

## The candidate terms (exactly these four)

- **T1, a cap level: the capped tiles' plateau over the cap.** The board of a run is raised by Δcap·π, where
  π = Φ((L(800) − W)/σ) is the run's chance of being capped under the dither (Φ the normal CDF, L(800) the run's level at
  800 MHz with every shift of the configuration). One fitted number, Δcap. It changes the board, never the clock.
- **T2, a same-session zeros-anchor level.** The session's own zeros anchors give, per format t, δ(t) = the mean over
  the anchor's runs at a measured clock of 795 MHz or more of [burst_w − L(800; c_zeros[t])], each run's die start
  referred by T3's slope when T3 is in the configuration (− k_T·(T_start − T_ref)). Every run of every non-anchor cell
  of format t in that session has its levels at all three operating points shifted by β·δ(t). A format with no anchor
  run at 800 MHz in the session (E80's fp32) takes the mean of the session's other formats' δ. One fitted number, β.
  It changes the clock (the governor holds the cap against the shifted levels) and the board.
- **T3, a die-start term.** Every run's levels at all three points are shifted by k_T·(T_start − T_ref), T_start the
  run's own whole-degree die reading at the burst's start, T_ref the mean die start of the fold's training runs
  (non-anchor cells). One fitted number, k_T.
- **T4, s(f) at n = 2 from the voltage reads, fitted jointly with the session terms kept.** s(f) = (V_f/V_600)² f/600
  with V the aifoundry2 PVT busy means of Q139(s)'s `voltage-reads.json.gz`, the held-out session's data dir left out
  (`fit_clock_voltage.voltage_table`, `pvt_busy_mean_mv`); B(f) refitted on E64's committed rows with that s
  (`Chain.fit_B`), c_zeros from E64's zeros runs (as Q139(s)'s arm A2), g = 1/xfer with xfer = (V_600,aifoundry3 /
  V_600,aifoundry2)² from the same reads; then every stage of the configuration it is added to is refitted under this
  chain (W, and Δcap, β, k_T as kept). **The exponent is never fitted, and n = 2.28 is never used.**

## Fitting, in each fold (the three training sessions' non-anchor cells only)

- **S1a (T3 in):** k_T = the least-squares slope of r = burst_w − L(800) (the base levels, no shift) on T_start, with
  one free intercept per training session, over the runs of the training cells grouped *pinned* whose measured burst
  clock is 795 MHz or more.
- **S1b (T2 in):** each training session's δ(t) from its anchors (with S1a's k_T if T3 is in); β = the least-squares
  slope through the origin of [r − k_T·(T_start − T_ref)] (the bracket's second part only if T3 is in) on δ(t) of the
  run's session and format, over the same runs.
- **S2 (always):** W = the value on 55.0, 55.1, … 75.0 W that minimizes the sum over training cells of (measured cell
  clock − predicted cell clock)², all training cells, governed and pinned (M8's `fit_cap` with γ = 0).
- **S3 (T1 in):** Δcap = the least-squares slope through the origin of the training cells' board residual (measured −
  predicted after S1-S2) on the cell's mean π, over all training cells.
- **The held-out session** is then predicted with these numbers and its own anchors' δ (computed with the fold's k_T)
  and its own runs' die starts. No number is taken from the held-out session except its zeros-anchor reads and its die
  starts, which are inputs.

## What is scored (per held-out session, and pooled)

Error = measured − predicted, per scored cell. For each held-out session h ∈ {E80, E83, E143, E160}, with each session
predicted by the fold that held it out:

- **G**: the governed clock, rms and mean (MHz), over h's governed cells;
- **Bg**: the governed board, rms and mean (W);
- **Bp**: the pinned board, rms and mean (W);
- reported beside them: the pinned clock (rms, mean), and the clock and board over all of h's cells.

**Pooled** = the same over all 134 held-out cells of the four sessions together.

## The rule (registered)

1. A term **carries on a quantity Q** (Q = G, Bg or Bp, each its rms) if, against the configuration it is added to,
   Q's held-out rms is lower in **at least 3 of the 4 held-out sessions** AND Q's **pooled** held-out rms is lower.
   "Lower" is strict; an unchanged value is not lower.
2. A term is **kept** if it carries on at least one of G, Bg, Bp, and it raises none of the other pooled rms by more
   than 0.15 MHz (G) or 0.03 W (Bg, Bp), about 2% of their size.
3. **Order (forward):** T1, T2, T3, T4, each tested against the configuration kept so far, starting from A0. T4 is
   tested on the configuration kept after T1-T3 (so with whichever session terms carried; if none carried, alone, and
   it is said so).
4. **The terms kept are M9's aifoundry2 part**, refitted by S1-S3 on all four sessions and frozen in `m9_a2.json`. If no
   term is kept, M9's aifoundry2 part is M8's as frozen (W = 65.20 W, M8's c_zeros, g, B, s), said so in the README.

## What is frozen with M9's aifoundry2 part

- `m9_a2.json`: the relation, the kept terms and their numbers fitted on all four sessions (T_ref then = the mean die
  start of all four sessions' non-anchor runs), and, for a session with no zeros-anchor read, the **fallback δ(t)** =
  the mean of the four sessions' δ(t) (E80 has no fp32 anchor, so fp32's is the mean of three).
- **Bands:** per predicted group (governed: predicted clock below 795 MHz; pinned), the 95th percentile of |held-out
  error| of the final configuration over the four sessions' held-out cells, for the clock and for the board; the burst
  D (board less the format's zeros board at its own clock) takes the board's band. The die rise over a burst keeps M8's
  burst heat law and band unchanged, applied to the predicted board.
- **The peak rule for the 82 W admission stop stays M8's, unchanged** (P800(c) + 1.94 W expected, P800(c at D's band
  top) + 2.95 W at 95%, with no level shift): a level term must not loosen a safety stop that was validated without it.
- **The prediction code** `predict_m9_a2.py`: per tile (format, D at 600 MHz on aifoundry3's footing), with the session's
  own zeros-anchor reads as input (per format, the anchor runs' burst_w, burst_mhz, die_start) or, without them, the
  fallback δ; and each run's die start, or a nominal one (T_ref by default) with the sensitivity per °C printed. It
  prints the clock, board, burst D, die rise, their bands and M8's peak, and the change per watt of δ, so a blind
  protocol can freeze its predictions before the anchors run and recompute them mechanically after. Nothing in it
  refits. A self-test checks it reproduces the fit's own predictions.

## Reported, never a verdict

- R7 and R8 per held-out session beside every arm (the "against M7 and M8 as frozen" comparison), and A0's W per fold.
- Each term alone against A0 (marginal), beside the forward steps.
- The final configuration against R7 and R8 per session: the paired difference in each rms, 95% interval by a bootstrap
  over cells inside the session (2,000 draws, seed 140). These intervals hold no session term.
- The critic's rank-2 targets on the final configuration's held-out numbers: G rms at most 4 MHz with |mean| at most
  2 MHz; |mean| of Bg and of Bp at most 0.5 W; Bp rms at most 1.0 W.
- **Reproduction checks** (they test the code, not the model): R7 with M7's blind D on E143's 36 registered tiles and
  E143's registered groups must give E143-F1/W1/F2/W2 (6.629 MHz, 1.601 W, 1.007 MHz, 1.184 W); R8 with M8's blind D on
  E160's 48 and E160's registered groups must give E160-F1/W1/F2/W2 (6.72 MHz, 1.39 W, 3.89 MHz, 1.73 W), to the
  predictions' rounding (0.1 MHz, 0.01 W). If either fails, the code is wrong and is fixed before any arm is scored.
- **End to end, blind D** (E143 with M7's frozen D, `tools/claims-v3/e143/predictions-e143.json`; E160 with M8's,
  `tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json`; their non-anchor registered tiles): R7, R8, A0 and
  the final configuration's fold.
- **Checks (the critic's): E159's zeros GEMMs and E161's first hold.** E159's three fp32 zeros holds (`results.json`
  `rows`, measured window board 35.98-36.04 W against G3's 38.43-38.52 W) and E161's G1Q (M8's 800 MHz board at the
  measured die by Q139(e)'s 0.442 W/°C law, 0.911 W over the board inside the kernel launches at 790 MHz or more,
  `corrections.txt`): what M9's level terms (the fallback δ, no anchors ran there) would change in each miss.
- The parameters per fold (their stability), and the cells without a measured D, if any.

## Never

- the exponent n = 2.28 or any fitted exponent; any term or form not listed above;
- a number from a held-out session other than its zeros-anchor reads and its die starts;
- a refit after this lane's scores are seen (a later change is a new registration);
- pool 7 (`desk-q140b-pool7`) or anything from it; any card, device command, ssh, Discord, Modal, or the private archive.
