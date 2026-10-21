#!/usr/bin/env python3
"""V3-DTF (E61) reduction -- the pre-registered analysis of README.md (the plan) §8, with the §9
decision rules applied and a verdict printed per claim row.

    python3 tools/claims-v3/dtf/reduce_dtf.py <pass dir> [<pass dir> ...] \
        --manifest <manifest.json> --out dtf.json [--txt reduce.txt] [--csv runs.csv] \
        [--leak auto|<W per C>] [--exclude <card>:<item> ...] [--cam-stats <json>] \
        [--primary-card aifoundry3] [--busy-mhz 800]

A pass dir is `<data>/<card>/dtf/p<N>/` (or `dtf-smoke/p1/`, `dtf-cam/p<N>/`) holding `runs.jsonl`,
`marks.jsonl`, `telemetry.jsonl[.gz]`, `configs.json`, `block.json`, `run.log` -- exactly what
`run_dtf.py` writes.  Smoke dirs are summarised and never enter the analysis; `dtf-cam` dirs carry
family 7 only.

What it does, by the plan's own numbering
-----------------------------------------
§8.1 per run: board power over the window -- seconds 1-3 after the first launch on the pinned card
     (aifoundry3); on a governor-free card E60's amendment A2 window (the 2 s starting 0.5 s after
     the clock first reads the card's busy clock, never before second 1, the run rejected if the
     clock has not arrived by second 1.5) -- corrected to the launch reading with the card's fitted
     leakage slope (`p80 = p_raw - k (T_window - T_launch)`).  Minion rail over seconds 2-4.  Raw
     [1,3) and [1,4) kept as checks.  One run's launch records are one value.
§8.2 gates, per run: one clock, the card's own; die voltage within +-3 mV of the pass median; an
     on-protocol launch within 0.5 C of the target; `ok == true` on every launch record;
     `participants == participants_expected`; `harts` and the shire mask as the manifest states
     them; and the ec RATE gate computed from each ENERCAT record's own `ops / cycles_max /
     participants` (instructions per cycle per participating hart) for the launches inside the power
     window -- 0.5% against the item's own family zero rung in the same pass, 0.2% between the
     members of any matched pair group (the manifest's `pair` links, closed transitively, so a
     3- or 4-member group gates as one).  A pair group that fails has its subtraction VOIDED in
     that pass, not reported.
§8.3 within a block, every item minus its own family zero, read from the manifest's `zero` field.
§8.4 slopes: per-pass least squares on designed flips per second with a free intercept over the
     h >= 1 / L >= 1 rungs (the h0 -> h1 step reported separately); the (card, pass) is the unit of
     replication, so the mean over passes with the SE from their between-pass scatter, reported both
     plain and robust (MAD x 1.4826).  Capacitances and electrons come from the MINION RAIL leg,
     with the board figure printed beside it and labelled board; both the 1/2 CV^2 and the CV^2
     conventions are printed (the page's confusion of them is claim S8).
§8.5 the joint fit, descriptive: e_in, e_out, e_cell, e_carry, e_addr and w (changed 32-bit
     words/s) over X, N, V, B, gate, C and A together, on the per-pass deltas so the per-group
     intercept drops out, with the condition number, per-coefficient VIFs and a statement of which
     family identifies which coefficient.  No joint-fit SE is quoted for a coefficient identified
     by a single contrast; a coefficient whose family was cut reads `not identified`.
§8.6 the zero-word term: `d1n`/`d1nz` is primary and its functional form (a constant offset per op
     vs a slope difference per flip) is fitted before it is applied anywhere; B's (B-A)-(D-C),
     `d3`/`d3p` and `m_solid_z`/`m_phase0` are replications with a heterogeneity check, never pooled.
§8.7 across cards: per-flip energies against E60's measured per-bit ties and against V^2.
§8.8 E-D7: board W vs E as an equality test (tier 1); the camera's statistics passed through from
     `--cam-stats` and labelled exploratory (tier 2).
§8.9 set-aside, scaled: a pass is set aside when more than 5% of its runs fail a gate (floor 2
     runs), or when `anchor_pi`'s fitted drift exceeds 0.3 W per 5 minutes of pass length (or 3x
     the between-pass drift SD, whichever is larger).  An item excluded by name under the A3 rule
     counts toward neither.  Set-aside passes are reported and not replaced.
§8.10 duplicates: an item run twice in a pass is averaged before the between-pass SE is taken and
     its within-pass repeat spread is reported.
§8.11 every derived quantity is written with its central value, SE, rail leg, pass count and
     identifying family -- the gap in E60's `hl.json` that forced anchors to be cited from
     `reduce.txt`.
§9   the decision rules: a two-sided t on the between-pass scatter with df = passes - 1, the
     3-sigma-equivalent quantile (|t| >= 4.53 at 8 passes, not the number 3), five confirmatory
     coefficients Holm-corrected at alpha = 0.05, thresholds in fJ or SE units, both arms satisfied
     -> OPEN, and an SE above one third of a rule's separation -> under-resolved, not scored.

Departures from the plan, as instructed for tonight's build
-----------------------------------------------------------
* The on-silicon register dump (plan §7 proof 6) is NOT implemented, so the determinism row rests on
  the rate gate, `ok`, `participants` and the off-card proofs; any `DUMP` lines that do appear in a
  `run.log` are counted and reported, never required.
* Mode numbers are 300-309 (`df.c2.fand` 300, `.for` 301, `.fadd` 302, `.fxor` 303, `df.un1a.fnot`
  304, `df.un1b.fnot` 305, `df.addr.a0/a1/a3/a5` 306-309); this file reads the pattern from the
  manifest's `op` and never hard-codes a mode id.
* `anchor_pi` runs first, middle and last, so the drift statistic is a fitted W/min over its
  positions rather than first-minus-last.

Corrections applied by the wf2 cross-check (Wed 21 Oct 2026, 01:3x PDT, before any measured pass).
The original is `wf2/reduce/reduce_dtf.py`; this copy differs only in these eight places, each marked
`# XCHK` in the code:
  1. `op` in the manifest is the `--pattern` name (E60's `run_hl.py:218` passes `it["op"]` straight to
     `--pattern`), so on a DF shape it reads `df.c2.for`, not `for.pi`.  GATE_DEPTH was keyed by the bare
     opcode, so `gate_depth_rank` was None for every gate item and the C33/C37 CONFIRMED arm ("spreads
     >= 3 SE AND ranks by gate depth") could never fire.  Added `opcode_of()` and keyed the table by it.
  2. `identifiable_coefs()` required two items to carry the SAME `op`.  Family V's arms are
     `df.un1a.fnot` / `df.un1b.fnot` and family A's rungs are `df.addr.a0/a1/a3/a5`, so the only pair that
     identifies e_cell and every pair that identifies e_addr were rejected and the joint fit withheld both
     as NOT IDENTIFIED.  It now compares the normalised opcode.
  3. The gate ladder took every nonzero h rung, so on aifoundry3 `d2D_h16` entered the same spread as the
     three h = 32 opcodes.  §4 registers the contrast at IDENTICAL designed counts; it is now read at the
     one h the three opcodes share, and a missing shared rung is a warning.
  4. §10 tier 1's half-die arm compared against a hard [1.33, 1.42] W.  §5.0 rule 2 widens every target by
     the statistic's own 3-SE-equivalent window; the strict reading is reported beside it.
  5. A ladder whose zero rung is a DIFFERENT opcode now says so: `ain`'s zero in E60 was `ain_h0`
     (`reduce_hl.py:30-31`) and the E61 lists contain no `ain_h0`, so an `ain_h8 - xin_h0` slope carries
     alpha(fand) - alpha(fxor) and is not the 28.10 fJ tie.  It is also named in `missing`.
  6. The zero-word primary now says so when it falls back to h = 0 or h = 32, the rungs §4 calls unclean.
  7. e_carry says when the e_out it imported came from a one-rung bridge (and so carries the §5.1 term).
  8. §8.7's registered 0.88-0.99 band and the symmetric +-12% reading are separate fields, not OR-ed into
     one flag; and the dead first assignment of `whole_card_per_s` is gone.

Amendment A2 (README, Wed 21 Oct 2026 01:05 PDT, after pass 1's gate output and before any family V or
family A energy was read) and the fixes the real data forced.  Each is marked `# A2` or `# FIX` in the
code; this file is the one the analysis runs from.
  A2.1 EVERY RATE GATE COMPARES RUNS OF ONE MODE.  Pass 1 showed the issue rate is fixed by the mode,
     not the data: constant in h to 1e-4 within a mode and identical on all three cards (0.5814 ops per
     cycle per hart for modes 202/300/302/306-308, 0.6088 for 177/179/191/301/303/309, 0.7356 for 304,
     0.7574 for 305, 0.3731 per hart for R's `--harts 2` arms).  So the 0.5%-against-the-family-zero
     gate fires only when the rung and its zero carry the same mode, and the 0.2% matched-pair gate is
     computed on pair groups SPLIT BY MODE -- no group may span two opcodes.  A cross-mode zero is
     reported as a rate ratio, never gated, and an item the manifest marks `rate_confounded` (d5_a5) is
     excluded by name from its ladder and reported beside it, exactly as amendment A3 excludes an item.
  A2.2 A VOID IS LOCAL.  A pair group that fails the 0.2% gate has THAT SUBTRACTION voided in that pass
     and nothing else: its runs stay in every other quantity.  Before this fix a d1a/d1b void (2.96%
     apart by code, which is what A2 reclassifies) deleted both arms' runs from the whole card, and
     family V, the V ladders and e_cell all read "absent / NOT IDENTIFIED" on data that passed every
     per-run gate.
  A2.3 FAMILY V.  Each arm is reduced against its OWN zero rung (`d1b_h*` against `d1b_h0`, no longer
     `d1a_h0`), both ladders are fitted on the regressor the two arms share (port+result bits/s, equal
     at every h by construction), and the cell price is the DIFFERENCE OF THE TWO MODES' PER-FLIP
     SLOPES, 1B minus 1A, over h = 16 and 32, rescaled by (port+result bits)/(cell bits) = 2 from the
     manifest's own counts.  Each arm's free intercept absorbs its own alpha and the registered
     0.125 address bits/op the two shapes differ by, so neither enters the slope.  The 0.2% pair gate
     between `d1a` and `d1b` is replaced by each mode's own within-mode rate gate.  The cross-mode watt
     difference d1b - d1a is still printed, labelled rate-confounded, and is not the estimator.
  A2.4 FAMILY A.  The ladder is `a0`, `a1`, `a3` -- the rungs that share one rate -- fitted as ONE
     cross-mode ladder (A2 registers it as such), with `a5` (mode 309, 4.7% faster by code) reported
     beside it as rate-confounded and outside the slope; the one-sided rule is read on the matched
     ladder.  `d5n_a0/a3` is the live regime's own ladder.
  A2.5 `participants_expected` is 1,024 x harts, so family R's two-hart arms expect 2,048 -- read from
     the manifest, which carries the corrected value (`--manifest manifest-a2.json`).
  FIX.6 A pass dir with no `block.json` is an UNFINISHED pass and is skipped by name, with its own line,
     rather than failing later on a half-written telemetry file.
  FIX.7 The launch-reading gate is skipped on a block that ran with NO PREHEAT (`args.preheat == 0`,
     which is the `dtf-cam` block of §10(a): "no heater and no anchor").  Its `--target` is the runner's
     never-wait sentinel (200 C), so the gate was failing all 80 family-7 runs on |55 - 200| > 0.5 and
     tier 1's W-vs-E equality -- the one arm of E-D7 that carries a verdict -- read "not evaluated".
     The realised launch spread is reported in place of the gate.
  FIX.8 A unit's pass ids, pass count and registered pass count are written BEFORE any early return, so
     a block that keeps no run still reports "passes [1, 2, 3, 4] (registered 4)", never "passes None
     (registered None)".
  FIX.9 `n_passes` registered per card follows amendment A1 (12 / 14 / 12, not §6's 8 / 10 / 9), with
     §6's original counts kept beside them.

Corrections applied by the wf4 reconciliation (Wed 21 Oct 2026, 02:4x PDT, after the measured passes
and before any verdict was published).  The input is `wf3/final/reduce_dtf.py`; every change below is
marked `# RECON n` in the code and nothing else differs.  1-9 are the reconciler's MUST FIX list, 10-13
its SHOULD FIX list, 14-16 its CONTEXT notes, which are carried as VISIBLE TEXT in the rows they bear on.
  RECON 1  The 2 x 2 bridge mixed modes in ONE rate denominator: the (B+D)-(A+C) rungs were fitted
     against x = 16h x rate(d2B), but the (D-C) half runs on mode 301, 4.71-4.73% faster than d2B's
     mode 300.  The denominator is now per mode, x = 8h*r300 + 8h*r301, which A2.1 requires of every
     cross-mode quantity.  `slope_over`/`slope_over_rail` take a LIST of (bits, rate item) pairs for
     exactly this.  It moves e_out and everything downstream of it (e_carry, tier 1's load).
  RECON 2  The §8.9 set-aside threshold was off by one run: `nf > max(2, 0.05 n)` needs 3 failures,
     while the plan says "more than 5% of its runs fail a gate (floor 2 runs)" -- 2 of 38 = 5.26% IS a
     set-aside.  Now `nf >= 2 and nf > 0.05 n`, which sets aside aifoundry1-c0 p6 and p7.
  RECON 3  The joint fit's condition number was computed on the RAW pooled design, whose count columns
     are ~1e13-1e14 beside an intercept of 1.0, so it read "rank-deficient" on a design whose VIFs are
     0.9-2.1 -- a scaling artefact.  It is now computed on a COLUMN-SCALED design restricted to the
     columns actually present (a column of zeros, e.g. family A absent on aifoundry1-c0, is dropped
     rather than read as a 1e33 condition number), with the raw value kept beside it, and C56's basis
     follows its registered rule: the JOINT-FIT e_out, with the raw 2 x 2 reported beside it and the
     changed-word term that separates them named.
  RECON 4  e_carry now uses its REGISTERED estimator (§4 family C): slope per carry node - e_out(add),
     with e_out(add) from `d3z` -- the same opcode, the same shape, the same pass -- as d3z's per-bit
     slope minus e_in from the SAME c2 shape's `d2A`, "never imported from fand/for".  The old route
     (minus family B's e_out) is printed as an alternative, as is the d3z-minus-e_in(fxor) form.
  RECON 5  A LEAKAGE-SLOPE SENSITIVITY ARM.  §8.1 registers the card's own fitted slope; E60 fitted
     0.203 / 0.442 / 0.327 W/C on whole-degree sensor steps.  Tonight's fit is 0.033-0.040 W/C on
     aifoundry3, so every quantity is now reported at the fitted slope (primary), at k = 0 and at E60's
     slope.  The per-flip prices barely move; the N-ladder intercept does, which decides §5.1's
     R1/R2/R3 row, so that row prints both.
  RECON 6  ONE ORDERING of §9 rule 4 in every row: the under-resolved test runs BEFORE the arms,
     everywhere (it was arms-first for e_addr and conditional for the Miller and zero-word rows).
  RECON 7  C46's REFUTED arm was firing on an exclusion from the WRONG SIDE.  The registered arm is a
     CEILING against a 0-2 fJ prior; a slope far ABOVE 32 fJ/bit cannot refute 32 fJ/bit from below.
     The row now reads "not measurable as registered", the exclusion is one-sided DOWNWARD only, the
     measured ladder is reported descriptively, and the per-op constant that three separately emitted
     kernels (modes 306-308) can differ by -- which no single free intercept removes -- is QUANTIFIED
     from the absolute power of same-rate zero rungs and printed in the row.
  RECON 8  e_cell's "scales with h" condition is TESTED, not asserted: the rate-free per-cell-bit step
     at h = 16 against the one at h = 32, with the ratio and its SE, plus the watt-difference growth
     against the 2.0 a proportional law needs.
  RECON 9  The cross-card tie for the 5.3 fnot target is the MEASURED e_in ratio, not E60's 1.216, with
     both the no-origin and the with-origin reading printed, and the 3-SE widening stated whenever
     "INSIDE" holds only because of it.
  RECON 10 The IPC table compares every shape against the REGISTERED 0.5791 (S10's own number), with
     tonight's mode-179 reference beside it; mode 179's own +5.1% build shift now leads the S10 row.
  RECON 11 C14/C64 prints both d2A rungs (h = 16 and h = 32) and both fit forms (with-origin, and the
     two-rung free-intercept slope) and says the arm sits at the interval's edge.
  RECON 12 C47 names the SIGN REVERSAL (Spearman over the pass-averaged levels, and the per-pass rho
     with its SE) and says on which card the complement control exists at all.
  RECON 13 §8.6's replications are pooled ACROSS CARDS (d3p - d3 on aifoundry1-c0, m_solid_z on
     aifoundry2), each labelled with its card, and the term quoted is the form the §8.6 fit prefers.
  RECON 14 C33/C37 says how many passes its spread rests on against the card's pass count, and that
     the measured order is not gate depth.
  RECON 15 The method choices are stated in one block: family A with and without the origin, the
     cross-card tie from the no-origin and with-origin e_in, and the half-die load three ways.
  RECON 16 C13 says which families the 0.2% matched-pair gate could run on at all, and that its
     CONFIRMED arm rests on the objdump walk, the ten sys_emu runs and 0 DUMP lines -- no silicon dump.

Corrections applied by the wf5 reduction (Wed 21 Oct 2026, 04:4x PDT) after the wf4 fix verifier
re-derived every changed quantity from `runs.csv` alone and found the reduction still wrong in
places.  The input is `wf4/fix/reduce_dtf.py`; every change below is marked `# VER n` in the code and
nothing else differs.  1-3 are the verifier's MUST FIX list, 4-6 its SHOULD FIX list, 7-12 its MINOR
list; the last entry is the physics skeptic's finding, carried as visible text in the row it bears on.
  VER 1  THE CHANGED-WORD PRICE AND THE CHANGED-WORD COUNT ARE NOW READ ON THE SAME §5.1 READING.
     The build counted dw = changed_words(R2) = 16 words/op (8 source + 8 result on every nonzero
     d1nz rung) and priced each word at intercept / src_words = intercept / 8, which is R1's price
     against R2's count and doubles the term.  §5.1 states ONE price -- E60's +0.273 W = 48.0 fJ per
     changed word -- and lets the reading set the count, which is exactly why its own table reads
     +0.137 W for `d1nz_h32 - d1nz_h0` under R1 and +0.273 W under R2.  One helper, `word_price_W`,
     now serves both places that use it.  Consequences: `B_bridge_R2_correction_W` is the intercept
     itself, 0.2283 W (§5.1: "the bridge is biased by exactly +0.273 W, and only under reading R2"),
     not twice it; the d3z leg's R2 term is 2.507 fJ/flip, not 5.013; `e_carry_R2_corrected` is
     3.482 +- 0.742 fJ with |t| 2.40 against 1.7 and the 3.850 window, so it reads CONFIRMED-ours
     like the primary, and C54's basis no longer says the row's verdict depends on the term.
  VER 2  C14 / C64 IS REPORTED, NOT SCORED.  README §5.2: "d2A cannot both supply e_in(fand) and be
     tested against it: the A/C arms are registered as the MEASUREMENT of e_in(fand)/e_in(for), and
     the C14/C64 equivalence to E60's one-rung 28.10 fJ is dropped as a decision (reported as
     agreement or disagreement, not scored)."  The row carried a CONFIRMED verdict on d2A's
     delta / 8h landing in [26.0, 30.2] fJ; it now carries the agreement, the direction, and no score.
  VER 3  C56 SAYS WHAT THE JOINT-FIT-MINUS-RAW GAP IS, instead of asserting it IS the §5.1
     changed-word term.  The gap is 3.952 fJ/flip, which on the bridge's own per-mode denominator
     (256 x r300 + 256 x r301 = 1.8645e14 bits/s) is 0.7369 W; the R2 term priced per VER 1 is
     0.2283 W = 1.224 fJ/flip, about 31% of it.  The remaining 0.509 W separates two estimators and
     is not explained by changed words -- which is a finding, not an identity.
  VER 4  §8.6'S FOUR REPLICATIONS ARE NOT POOLED.  §8.6: "four different opcodes at different count
     magnitudes are not pooled into one indicator -- a heterogeneous set is reported as
     opcode-dependent."  `replications_pooled_across_cards` was True; it is now False (they are
     GATHERED across cards, each labelled with its card and opcode, and nothing is averaged), the
     whole heterogeneity result is computed and printed -- every pairwise |t| against the
     3-sigma-equivalent quantile plus Cochran's Q on k - 1 df -- and when it fires the row states the
     README's OPEN arm: the set is OPCODE-DEPENDENT.  The inverse-variance mean is printed only as
     Q's centre and is read by nothing.
  VER 5  THE C14 ROW SAYS WHERE ITS ANSWER MOVES WITH THE LEAKAGE SLOPE.  At E60's 0.203 W/C the
     same estimator reads 25.567 +- 0.230 fJ -- below [26.0, 30.2], inside only after its own 3-SE
     widening -- against 26.112 +- 0.132 fJ at the fitted slope.  The row prints all three slopes
     with each one's reading, so the agreement is visibly a statement about the slope as well.
  VER 6  "N of the M registered passes present" read as data loss.  Every registered pass dir exists
     and was read; the shortfall is §8.9 setting passes aside and not replacing them.  The line now
     reads "N of M KEPT; K SET ASIDE (see the pass block)" and says no dir is missing.
  VER 7  e_cell's RECON 8 scaling test HAS NO POWER here: the paired difference is -0.186 +- 0.341
     fJ/bit, |t| 0.54 against a 3.850 window, so proportionality (difference 0) and the measured
     -16.4% are both inside 3 SE.  "proportional within 3 SE: True" and "nothing shows it scaling
     with h" were the same non-result stated as if they disagreed; the condition is now reported as
     UNTESTED rather than satisfied or failed.
  VER 8  C79's MARGIN.  The step is 0.0875 +- 0.0600 W = 0.2348 +- 0.161 pJ/op and the REFUTED arm is
     a hard 0.5 pJ/op boundary, 1.65 SE away -- well inside the statistic's own 3-SE window, so the
     OPEN band is not excluded and the verdict rests on the point value.  Printed with the 3-SE upper
     bound.
  VER 9  THE LADDER-INTERCEPT ROW NAMES WHICH OPEN IT IS.  It is OPEN because more than one reading
     is inside 3 SE -- a fourth case the §9 partition does not name -- while the registered OPEN arm
     (X and N intercepts disagreeing per changed word) does NOT fire: X - N per changed source word
     is -0.00891 +- 0.00515 W, |t| 1.73 against 3.850.  That statistic is now printed in the row.
  VER 10 C22's MARGIN.  rho = 1.1170 +- 0.0243 on 8 passes: 1.000 is excluded at |t| 4.82, 106% of
     the 4.530 threshold, so the arm fires on a thin margin -- an SE 6% larger would read OPEN.
  VER 11 C58's FOUR-PASS CAVEAT.  The W-vs-E half is the §10(a) dtf-cam block, 4 passes, below §9's
     own 6-pass floor for a confirmatory item, where the 3-sigma-equivalent quantile is 9.22: the arm
     could not have detected a 3 W asymmetry, so "equal within 3 SE" is an absence of evidence at low
     resolution, not an equality.
  VER 12 C33's SPREAD IS READ ON §8.4'S UNIT OF REPLICATION.  The SE was cross-item,
     sqrt(se_min^2 + se_max^2) over two items' own between-pass SEs, which treats legs measured in
     the same pass as independent samples.  The PAIRED per-pass statistic is now computed two ways
     (the fixed max-vs-min pair, and per-pass max - min), the row reads the paired one, and the
     cross-item number is printed beside it.  All three fire the same arm on tonight's data.
  SKEPTIC  WHY THERE ARE TWO ISSUE-RATE LEVELS AT ALL, carried in the S10 / C16 / C59 row: the
     physics skeptic (wf4/skeptic) found the level follows the LOOP HEAD'S ADDRESS MOD 32.  This file
     re-derives it rather than quoting it when the objdump is on disk (`--dis`, default
     `<dtf>/proof/dis-a2.txt`): the c2 family's four opcodes pin the map one-to-one and the four
     df.addr kernels agree as a count.  It is an instruction-FETCH alignment effect, which is why
     A2.1 found the rate fixed by the mode and not by h, identical on all three cards, and why the
     same mode shifted +5.1% between builds.  Reported, never a gate.

Python 3.8+, numpy only.
"""
import argparse
import csv
import datetime
import gzip
import io
import json
import math
import os
import re
import sys
from collections import defaultdict

import numpy as np

E_CHARGE = 1.602176634e-19

# ---- §9.1 the statistic -------------------------------------------------------------------------
THREE_SIGMA_P = 0.0027          # a "3 SE" window means this two-sided t quantile, never the number 3
HOLM_ALPHA = 0.05               # §9.2, within the confirmatory family only
# §9.2 the five confirmatory coefficients, in the plan's order
CONFIRMATORY = ["e_cell", "e_carry", "e_addr", "phase_term", "zero_word_term"]

# §5 / §9.3 the registered anchors (E60, aifoundry3, 600 MHz, 0.5218 V, board energy, quoted from
# docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt lines 31-34 -- never from hl.json, §8.11)
E60 = {
    "e_in_fxor_fJ": 20.83, "e_in_fxor_se_fJ": 0.10, "e_in_fxor_rail_fJ": 16.28,
    "e_in_interval_fJ": (19.7, 20.9),
    "e_out_interval_fJ": (30.00, 31.17), "e_out_se_fJ": 0.17,
    "e_in_fand_fJ": 28.10, "e_in_fand_se_fJ": 0.70, "e_in_fand_interval_fJ": (26.0, 30.2),
    "e_sum_fnot_interval_fJ": (52.00, 53.10),      # E60's measurement and E46's model-free leg
    "rate_per_hart": 0.5791, "rate_card_per_s": 3.558e11,
    "intercept_W": 0.273, "intercept_fJ_per_op": 767.3, "intercept_fJ_per_changed_word": 48.0,
    "leak_W_per_C": {"aifoundry3": 0.203, "aifoundry2": 0.442, "aifoundry1-c0": 0.327},
    "per_bit_tie": {"aifoundry3": 1.0, "aifoundry2": 1.376, "aifoundry1-c0": 1.216},
    "v2_tie": {"aifoundry3": 1.0, "aifoundry2": 1.402, "aifoundry1-c0": 1.339},
    # FIX.9 amendment A1 (21 Oct 00:58 PDT, on elapsed time alone): aifoundry3 12 passes, aifoundry1
    # card 0 12, aifoundry2 14 electrical passes (plus the 4-pass dtf-cam block, §10(a)).
    "n_passes": {"aifoundry3": 12, "aifoundry2": 14, "aifoundry1-c0": 12},
    "n_passes_prereg_s6": {"aifoundry3": 8, "aifoundry2": 10, "aifoundry1-c0": 9},
}
# A2.1 the issue rate pass 1 measured per mode, ops per cycle per participating hart -- constant in h
# to 1e-4 within a mode and identical on all three cards.  Reported against the measured rate; never a
# gate (the gate is each mode against its own zero rung).
A2_MODE_IPC = {202: 0.5814, 300: 0.5814, 302: 0.5814, 306: 0.5814, 307: 0.5814, 308: 0.5814,
               177: 0.6088, 179: 0.6088, 191: 0.6088, 301: 0.6088, 303: 0.6088, 309: 0.6088,
               304: 0.7356, 305: 0.7574}
A2_MODE_IPC_HARTS2 = 0.3731     # R's two `fand.pi --harts 2` arms, per hart
# the page's numbers that §9 scores against
PAGE = {"e_out_fJ": 44.38, "e_in_fJ": 6.52, "e_carry_fJ": 14.2, "e_addr_fJ": 32.0,
        "zero_gate_pJ_per_op": 8.94, "miller_dW": 0.275, "half_die_W": 2.2, "ipc": 1.0}
PRIOR = {"e_cell_fJ": (0.3, 3.0), "e_carry_fJ": (0.0, 4.0), "e_addr_fJ": (0.0, 2.0)}

# §4 family M: k_adj per item, the convention stated in the plan ("per flipping wire, (2 x anti-phase
# neighbours + 1 x static neighbours) / 2, summed over flipping bits and divided by their count, with
# no wrap at the word boundary").  Used ONLY if the manifest carries no k_adj for the item, and the
# fallback is printed when it fires.
K_ADJ_FALLBACK = {"m_phase0": 0.031, "m_nib": 0.969, "m_nib_c": 0.969, "m_pair": 1.469,
                  "m_byte": 1.719, "m_solid_z": 0.000}
# §4 family gate: the registered gate-depth order of the three matched opcodes.  XCHK 1: keyed by the
# OPCODE, which `opcode_of` reads out of the manifest's `op` -- and `op` is the `--pattern` name, which on a
# DF shape is `df.c2.for`, not `for.pi`.
GATE_DEPTH = {"for": 1, "fxor": 2, "fadd": 3}
MNEMONICS = ("fand", "for", "fxor", "fadd", "fnot", "fmadd", "fmul", "fsll", "fswizz", "fbcx", "iadd", "st")



def _rel(p):
    """A path inside the repository as a repository-relative path (E60's hl.json convention); others unchanged."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap = os.path.abspath(p)
    return os.path.relpath(ap, root) if ap.startswith(root + os.sep) else ap

def opcode_of(op):
    """XCHK 1: the opcode a pattern name carries -- `df.c2.for` -> 'for', `for.pi` -> 'for',
    `fmadd.ps` -> 'fmadd'.  A pattern whose segments name no opcode (`df.addr.a0`, whose body is
    `fxor.pi f(8+i), fR, fR`) returns its shape prefix (`df.addr`), which is equal across that family's
    rungs -- which is all any caller here needs."""
    if not op:
        return None
    parts = str(op).split(".")
    for seg in parts:
        if seg in MNEMONICS:
            return seg
    return ".".join(parts[:-1]) if len(parts) > 1 else str(op)

PINNED_CARDS = ("aifoundry3",)   # the only clock-pinned card (600 MHz by its boot service)


# =================================================================================================
# small numerics (numpy only -- no scipy on the lab boxes)
# =================================================================================================
def _betacf(a, b, x, itmax=300, eps=3e-16):
    """Continued fraction for the incomplete beta function (modified Lentz)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-300:
        d = 1e-300
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-300:
            d = 1e-300
        c = 1.0 + aa / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-300:
            d = 1e-300
        c = 1.0 + aa / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1.0 - x) / b


def t_p_two(t, df):
    """Two-sided p for Student's t: P(|T| > |t|) = I_{df/(df+t^2)}(df/2, 1/2)."""
    if df is None or df < 1 or t is None or not np.isfinite(t):
        return None
    t = abs(float(t))
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(p_two, df):
    """The |t| whose two-sided p is p_two, by bisection (no scipy)."""
    if df is None or df < 1:
        return None
    lo, hi = 0.0, 1.0
    while t_p_two(hi, df) > p_two and hi < 1e7:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_p_two(mid, df) > p_two:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    out = []
    for line in op(path, "rt"):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def clean(v):
    return [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]


def mean_se(v):
    v = clean(v)
    if not v:
        return None, None, 0
    m = float(np.mean(v))
    return m, (float(np.std(v, ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None), len(v)


def mad_se(v):
    """§8.4 the robust leg: MAD x 1.4826 across passes, as an SE of the mean."""
    v = clean(v)
    if len(v) < 2:
        return None
    med = float(np.median(v))
    mad = float(np.median([abs(x - med) for x in v]))
    return 1.4826 * mad / math.sqrt(len(v))


def fit_line(x, y):
    """Least squares y = a + b x; returns (a, b, resid_rms) or None."""
    x, y = np.asarray(clean(x), float), np.asarray(clean(y), float)
    if len(x) != len(y) or len(x) < 2 or np.ptp(x) == 0:
        return None
    X = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(c[0]), float(c[1]), float(np.sqrt(np.mean((y - X @ c) ** 2)))


def spearman(x, y):
    """Spearman rho, average ranks for ties."""
    def rank(v):
        v = np.asarray(v, float)
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), float)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
            i = j + 1
        return r
    if len(x) < 3:
        return None
    rx, ry = rank(x), rank(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    den = math.sqrt(float((rx * rx).sum()) * float((ry * ry).sum()))
    return float((rx * ry).sum() / den) if den else None


def units(e_j, v):
    """§8.4: both conventions printed, since conflating them is claim S8's own error."""
    if e_j is None or v in (None, 0):
        return {}
    c_half = 2.0 * e_j / v ** 2          # E = 1/2 C V^2
    c_full = e_j / v ** 2                # E = C V^2
    return {"fJ": e_j * 1e15,
            "C_fF_halfCV2": c_half * 1e15, "electrons_halfCV2": c_half * v / E_CHARGE,
            "C_fF_CV2": c_full * 1e15, "electrons_CV2": c_full * v / E_CHARGE}


def fmt(x, n=3):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else ("%.*f" % (n, x))


# =================================================================================================
# the manifest
# =================================================================================================
class Manifest(object):
    def __init__(self, path):
        raw = json.load(open(path))
        self.path = path
        self.seed = raw.get("seed")
        self.modes = raw.get("modes") or {}
        self.items = {}
        for it in raw.get("items", []):
            self.items[it["name"]] = it
        self.warnings = []
        # §8.2 matched-pair groups: the `pair` links closed transitively, so a 3- or 4-member group
        # (the four B cells at one h, the three gate-ladder opcodes) gates as one.
        parent = {n: n for n in self.items}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for n, it in self.items.items():
            q = it.get("pair")
            for other in ([q] if isinstance(q, str) else (q or [])):
                if other in parent:
                    ra, rb = find(n), find(other)
                    if ra != rb:
                        parent[ra] = rb
                elif other:
                    self.warnings.append("manifest: %s pairs with %r, which is not an item" % (n, other))
        groups = defaultdict(list)
        for n in self.items:
            groups[find(n)].append(n)
        # A2.1: NO PAIR GROUP MAY SPAN TWO OPS.  The 0.2% gate asks two runs of one mode to retire at
        # the same rate; across modes the rate is a property of the compiled case (d1a/d1b are 2.96%
        # apart by code, d5_a5 4.7%), so a cross-mode group would void by construction.  Every group is
        # split by mode -- the manifest's own field, falling back to the normalised opcode -- and each
        # `pair` link that crossed a mode is named, because that link is what A2 reclassifies.
        self.pair_links_crossing_mode = []
        split = []
        for members in groups.values():
            if len(members) < 2:
                continue
            bymode = defaultdict(list)
            for n in members:
                bymode[self.mode_key(n)].append(n)
            if len(bymode) > 1:
                self.pair_links_crossing_mode.append(
                    {"declared_group": sorted(members),
                     "split_into": [sorted(v) for _, v in sorted(bymode.items(), key=lambda kv: str(kv[0]))],
                     "modes": dict((str(k), sorted(v)) for k, v in bymode.items())})
                self.warnings.append(
                    "manifest: the `pair` links join %s into one group across modes %s; A2 splits it by "
                    "mode, so the 0.2%% pair gate never compares two opcodes and each arm is reduced "
                    "against its own zero rung"
                    % (sorted(members), sorted(str(k) for k in bymode)))
            for _, v in sorted(bymode.items(), key=lambda kv: str(kv[0])):
                if len(v) > 1:
                    split.append(sorted(v))
        self.pair_group = {}
        for members in split:
            key = "+".join(members)
            for n in members:
                self.pair_group[n] = key
        self.groups = dict(("+".join(m), m) for m in split)

    def mode_key(self, name):
        """A2.1: the identity a rate gate may compare within -- the manifest's `mode` when it carries
        one (manifest-a2.json does for every item), else the normalised opcode, else the pattern."""
        it = self.get(name)
        if it.get("mode") is not None:
            return int(it["mode"])
        return opcode_of(it.get("op")) or ("item:" + name)

    def same_mode(self, a, b):
        return self.mode_key(a) == self.mode_key(b)

    def rate_confounded(self, name):
        """A2.4: an item the amendment puts outside its family's registered ladder because its mode
        retires at another rate (d5_a5, mode 309, 4.7% faster by code).  Reported beside the ladder."""
        return bool(self.get(name).get("rate_confounded"))

    def get(self, name):
        return self.items.get(name, {})

    def counts(self, name):
        return (self.get(name).get("counts") or {})

    def c(self, name, key):
        v = self.counts(name).get(key)
        return 0.0 if v is None else float(v)

    def designed_flips(self, name):
        """port + result bits per 256-bit op -- the quantity e_in and e_out price (§8.4)."""
        return self.c(name, "vs1") + self.c(name, "vs2") + self.c(name, "result")

    def changed_words(self, name, reading="R2"):
        """§5.1: R1 counts changed 32-bit SOURCE words, R2 any changed word on any bus."""
        return self.c(name, "src_words") + (self.c(name, "res_words") if reading == "R2" else 0.0)

    def zero_of(self, name):
        return self.get(name).get("zero")

    def family(self, name):
        return self.get(name).get("family")

    def by_family(self, fam):
        return sorted(n for n, it in self.items.items() if it.get("family") == fam)

    def k_adj(self, name):
        it = self.get(name)
        for key in ("k_adj", "kadj", "delta"):
            if it.get(key) is not None and (key != "delta" or it.get("family") == "M"):
                return float(it[key]), key
        if name in K_ADJ_FALLBACK:
            return K_ADJ_FALLBACK[name], "plan-fallback"
        return None, None


# =================================================================================================
# §8.1 per run
# =================================================================================================
def experiment_of(d, blk):
    exp = (blk or {}).get("exp")
    if exp:
        return str(exp)
    parts = os.path.normpath(d).split(os.sep)
    for p in reversed(parts):
        if p.startswith("dtf") or p.startswith("hl"):
            return p
    return "dtf"


def resolve_card(d):
    """configs.json, then block.json, then the path -- the window rule depends on which card it is,
    so this must not fall back to 'governor-free' just because configs.json is missing."""
    for f, key in (("configs.json", "card"), ("block.json", "card")):
        pth = os.path.join(d, f)
        if os.path.exists(pth):
            try:
                v = json.load(open(pth)).get(key)
            except ValueError:
                v = None
            if v:
                return str(v)
    return os.path.basename(os.path.dirname(os.path.dirname(os.path.normpath(d))))


def runs_of_pass(d, man, gov_free=False, busy_mhz=800, card_hint=None):
    """One list of run records for one pass dir; the window, rail, gates' raw inputs and the
    ENERCAT rate are all computed here (§8.1, §8.2)."""
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    notes = []
    if not tel:
        return [], None, ["%s: no telemetry" % d]
    t = np.array([s["t_ms"] for s in tel], float)
    P = np.array([s["board_w"] for s in tel], float)
    rail = np.array([s["sp"]["minion_w"][0] for s in tel], float)
    mhz = np.array([s["mhz"]["minion"] for s in tel], float)
    mv = np.array([s["die_mv"]["minion"] for s in tel], float)
    T = np.array([float(s["temp_c"]["minshire"][0]) for s in tel], float)
    # temp_c.minshire = [current mean over the 34 minion shires, peak-hold low, peak-hold high]
    # (tools/ettelem/host_temp_fields.py).  Its spread is §10's one on-die check, and because the
    # docstring is ambiguous about whether the extremes are across shires or over time, the
    # comparison is also the test of which it is.
    try:
        Tlo = np.array([float(s["temp_c"]["minshire"][1]) for s in tel], float)
        Thi = np.array([float(s["temp_c"]["minshire"][2]) for s in tel], float)
    except (IndexError, KeyError, TypeError, ValueError):
        Tlo = Thi = None
    recs = load_jsonl(os.path.join(d, "runs.jsonl"))
    marks = [m for m in load_jsonl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"]
    cfg_path = os.path.join(d, "configs.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    target = (cfg.get("args") or {}).get("target")
    # FIX.7: --preheat 0 means the block ran with no heater (§10(a)'s dtf-cam block), so there is no
    # launch reading and `target` is the runner's never-wait sentinel.
    preheat = (cfg.get("args") or {}).get("preheat")
    contiguous = bool((cfg.get("args") or {}).get("contiguous"))
    blk_path = os.path.join(d, "block.json")
    blk = json.load(open(blk_path)) if os.path.exists(blk_path) else {}
    card = cfg.get("card") or (blk or {}).get("card") or card_hint \
        or os.path.basename(os.path.dirname(os.path.dirname(d)))
    exp = experiment_of(d, blk)
    # DUMP lines, if the on-silicon dump was ever enabled (it is NOT tonight -- departure 1)
    n_dump = 0
    log = os.path.join(d, "run.log")
    if os.path.exists(log):
        for line in open(log, "rt", errors="replace"):
            if line.startswith("DUMP"):
                n_dump += 1
    by = defaultdict(list)
    for r in recs:
        by[(r.get("block"), r["item"], r.get("pos", 0), r.get("attempt", 1))].append(r)
    out = []
    for m in marks:
        key = (m.get("block"), m["item"], m.get("pos", 0), m.get("attempt", 1))
        rr = sorted(by.get(key, []), key=lambda r: r["t_start_ms"])
        if not rr:
            notes.append("%s: no launch record for %s pos %s" % (d, m["item"], m.get("pos")))
            continue
        it = man.get(m["item"])
        kind = rr[0].get("kind") or it.get("kind") or "ec"
        t0 = rr[0]["t_start_ms"]
        lo = t0 + 1000.0
        ramp_ms = None
        if gov_free:
            # E60 amendment A2: start 0.5 s after the clock first reads the busy clock, never before second 1
            at = np.where((t >= t0) & (t <= t0 + 4000) & (mhz == busy_mhz))[0]
            if len(at):
                ramp_ms = float(t[at[0]] - t0)
                lo = max(t0 + 1000.0, t[at[0]] + 500.0)
            else:
                ramp_ms = float("inf")
        hi = lo + 2000.0
        w = (t >= lo) & (t < hi)
        w14 = (t >= t0 + 1000) & (t < t0 + 4000)
        wr = (t >= lo + 1000) & (t < min(lo + 3000, rr[-1]["t_end_ms"]))   # the rails are 1 s running averages
        tr = (t >= max(t0 + 800, lo - 200)) & (t <= rr[-1]["t_end_ms"])
        if w.sum() < 5:
            notes.append("%s: %s pos %s has %d telemetry samples in its window" % (d, m["item"], m.get("pos"), w.sum()))
            continue
        body = [r for r in rr if r.get("launch", 0) >= 0] if kind == "fma" else rr
        work = 0.0
        ipcs, participants, harts_seen, masks, ok_all = [], set(), set(), set(), True
        for r in rr:
            if not r.get("ok", False):
                ok_all = False
            if r.get("participants") is not None:
                participants.add(int(r["participants"]))
            if r.get("harts") is not None:
                harts_seen.add(int(r["harts"]))
            if r.get("shire_mask_used"):
                masks.add(str(r["shire_mask_used"]).lower())
        for r in body:
            dur = max(1.0, r["t_end_ms"] - r["t_start_ms"])
            ov = max(0.0, min(r["t_end_ms"], hi) - max(r["t_start_ms"], lo))
            n = (r["iters"] * r.get("minions", 1024)) if kind == "fma" else (r.get("ops") or 0)
            work += n * ov / dur
            # §8.2 the ec rate gate: each record's OWN exact device counts, per participating hart,
            # for the launches lying inside the power window.  Never the prorated `rate`, which
            # moves with the window edges.
            if ov > 0 and kind != "fma":
                cm, pa, ops = r.get("cycles_max"), r.get("participants"), r.get("ops")
                if cm and pa and ops:
                    ipcs.append(float(ops) / float(cm) / float(pa))
        rec = {"card": card, "exp": exp, "dir": d,
               "pass": m.get("block") if m.get("block") is not None else blk.get("pass"),
               "item": m["item"], "pos": m.get("pos", 0), "attempt": m.get("attempt", 1),
               "kind": kind, "family": it.get("family"), "op": it.get("op") or rr[0].get("pattern"),
               "start_c": m.get("start_c"), "on_protocol": m.get("on_protocol"), "target": target,
               "preheat": preheat, "contiguous": contiguous,
               "t_start_ms": t0, "t_mid_ms": 0.5 * (lo + hi), "launches": len(rr),
               "p_raw": float(P[w].mean()), "p_raw14": float(P[w14].mean()) if w14.sum() else None,
               "t_win": float(T[w].mean()),
               "peak_spread_c": (float((Thi[w] - Tlo[w]).mean()) if Thi is not None and w.sum() else None),
               "rail": float(rail[wr].mean()) if wr.sum() else None,
               "mhz": sorted(set(int(x) for x in mhz[w])), "mv": float(mv[w].mean()),
               "rate": work / ((hi - lo) / 1000.0),      # prorated instructions/s (fma: minion-ops/s)
               "ipc": float(np.mean(ipcs)) if ipcs else None,
               "ipc_n": len(ipcs),
               "cycles_per_op": float(np.mean([r["cycles_per_op"] for r in body
                                               if r.get("cycles_per_op")]))
                                if kind == "fma" and any(r.get("cycles_per_op") for r in body) else None,
               "participants": sorted(participants), "harts": sorted(harts_seen),
               "shire_mask_used": sorted(masks), "ok_records": ok_all,
               "ramp_ms": ramp_ms, "window_start_s": (lo - t0) / 1000.0,
               "n_dump_lines": n_dump,
               "_tP": (T[tr].tolist(), P[tr].tolist())}
        out.append(rec)
    return out, card, notes


def leak_slope(runs):
    """W per C from the within-run drift of runs whose reading rises >= 1 C after second 0.8
    (21 Sep's method, as E60 used it)."""
    ks = []
    for r in runs:
        T_, P_ = r["_tP"]
        if len(T_) > 10 and max(T_) - min(T_) >= 1:
            ks.append(float(np.polyfit(T_, P_, 1)[0]))
    return (float(np.median(ks)), len(ks)) if ks else (0.4, 0)


# =================================================================================================
# per-pass series and derived quantities
# =================================================================================================
def combo(val, p, terms, key):
    """sum(coef * val[pass][item][key]); None if any term is missing."""
    s = 0.0
    for coef, name in terms:
        v = val.get(p, {}).get(name, {})
        if v.get(key) is None:
            return None
        s += coef * v[key]
    return s


def per_op_bits(val, p, terms):
    """designed flips per second for the same terms (the denominator of a per-bit price)."""
    s = 0.0
    for coef, bits, name in terms:
        v = val.get(p, {}).get(name, {})
        if v.get("rate") is None:
            return None
        s += coef * bits * v["rate"]
    return s


def stat(series):
    """series: list of (pass, value) -> the §8.4 between-pass statistic."""
    passes = [p for p, _ in series]
    vals = [v for _, v in series]
    m, se, n = mean_se(vals)
    return {"value": m, "se": se, "se_robust": mad_se(vals), "median": float(np.median(vals)) if vals else None,
            "n_passes": n, "passes": passes, "per_pass": vals}


def with_t(d, df=None):
    """Attach the §9.1 statistic: t on the between-pass scatter, df = passes - 1."""
    n = d.get("n_passes") or 0
    dof = df if df is not None else (n - 1 if n >= 2 else None)
    d["df"] = dof
    if d.get("value") is not None and d.get("se"):
        d["t"] = d["value"] / d["se"]
        d["p_two"] = t_p_two(d["t"], dof)
        d["t_crit_3sigma"] = t_crit(THREE_SIGMA_P, dof) if dof else None
        d["abs_t_ge_3sigma"] = (abs(d["t"]) >= d["t_crit_3sigma"]) if d.get("t_crit_3sigma") else None
    else:
        d["t"] = d["p_two"] = d["t_crit_3sigma"] = d["abs_t_ge_3sigma"] = None
    return d


def derived(val, passes, terms, bits_terms=None, family=None, identified_by=None, unit="W",
            v_rail=None, notes=None, scale=1.0, skip_passes=None):
    """One derived quantity, board and rail, with value, SE, pass list and identifying family (§8.11).

    terms:       [(coef, item), ...] -- the contrast, in watts, on per-pass pass-means.
    bits_terms:  [(coef, bits_per_op, item), ...] -- the per-second denominator; None keeps watts.
    skip_passes: A2.2 -- the passes in which THIS subtraction's matched-pair group failed the 0.2%
                 gate.  The void is local: those passes leave this quantity and nothing else.
    """
    skip = set(skip_passes or ())
    out = {"unit": unit, "family": family, "identified_by": identified_by,
           "terms": ["%+g*%s" % (c, n) for c, n in terms], "notes": list(notes or [])}
    if skip:
        out["voided_passes"] = sorted(skip)
        out["notes"].append("§8.2 / A2.2: pass(es) %s left this subtraction because their matched-pair "
                            "group failed the 0.2%% rate gate; their runs stay in every other quantity"
                            % sorted(skip))
    for leg, key in (("board", "p80"), ("rail", "rail")):
        ser = []
        for p in passes:
            if p in skip:
                continue
            y = combo(val, p, terms, key)
            if y is None:
                continue
            if bits_terms:
                den = per_op_bits(val, p, bits_terms)
                if not den:
                    continue
                y = y / den
            ser.append((p, y * scale))
        s = with_t(stat(ser))
        if bits_terms and v_rail:
            # §8.4: the capacitance and electron count come from the RAIL leg; the board leg's are
            # printed only so the 1.33x board/rail ratio is visible, never for planning.
            s.update(units(s["value"], v_rail))
            s["units_from"] = "rail (quote these)" if leg == "rail" else "board (reference only)"
        out[leg] = s
    for k in ("value", "se", "se_robust", "median", "t", "df", "p_two", "t_crit_3sigma",
              "abs_t_ge_3sigma", "n_passes", "passes"):
        out[k] = out["board"].get(k)
    out["rail_value"] = out["rail"]["value"]
    out["rail_se"] = out["rail"]["se"]
    if bits_terms:
        out["fJ"] = None if out["value"] is None else out["value"] * 1e15
        out["se_fJ"] = None if out["se"] is None else out["se"] * 1e15
        out["rail_fJ"] = None if out["rail_value"] is None else out["rail_value"] * 1e15
    return out


def ladder(val, passes, names, zero, bits_of, key="p80"):
    """§8.4: per-pass least squares of (item - zero) on designed flips/s with a FREE INTERCEPT over
    the nonzero rungs.  Three fit forms are kept apart on purpose, because they are not the same
    estimator and E60's two published anchors come from two of them (§5.2):

      multi      >= 2 nonzero rungs in the pass, free intercept  -- the plan's registered §8.4 fit.
                 On E60's own xin ladder this returns 19.78 fJ with a +0.269 W intercept: the 19.7
                 end of the registered e_in interval, and the intercept E60 quotes as +0.273 W.
      single     exactly one nonzero rung: the slope through the zero, reported separately so a
                 pass that ran a subset is never averaged into the multi-rung slope.
      zero_point every pass, with the (0, 0) point included and a free intercept -- E60's own ec
                 fit (reduce_hl.py:338-348).  On E60's xin ladder this returns 20.835 +- 0.105 fJ,
                 which IS the 20.83 +- 0.10 anchor, so it is the form that ties E61 to E60's scale.
    """
    out = {"multi": {}, "single": {}, "zero_point": {}, "intercept": {}, "intercept_zero_point": {},
           "resid": [], "used": {}}
    for p in passes:
        xs, ys = [], []
        for n in names:
            vp, vz = val.get(p, {}).get(n, {}), val.get(p, {}).get(zero, {})
            if vp.get(key) is None or vz.get(key) is None or vp.get("rate") is None:
                continue
            xs.append(bits_of(n) * vp["rate"])
            ys.append(vp[key] - vz[key])
        out["used"][p] = len(xs)
        if len(xs) >= 2:
            f = fit_line(xs, ys)
            if f:
                out["intercept"][p] = f[0]
                out["multi"][p] = f[1]
                out["resid"].append(f[2])
        elif len(xs) == 1 and xs[0]:
            out["single"][p] = ys[0] / xs[0]
        if xs:
            f = fit_line([0.0] + xs, [0.0] + ys)
            if f:
                out["intercept_zero_point"][p] = f[0]
                out["zero_point"][p] = f[1]
    return out


# the regressor each family's ladder is fitted against (§8.4); everything else is port+result bits
# A2.3: family V is NOT keyed on `cell` here.  Under A2 each V arm is a ladder against its OWN zero
# rung, and 1A's cell count is 0 at every h, so a cell regressor leaves 1A with no rung at all and
# prices 1B's whole port+result energy as if it were cells.  The regressor the two arms SHARE is
# port+result bits (16h in both, by construction), and e_cell is the difference of the two slopes
# rescaled by (port+result)/(cell) = 2 -- computed in family_estimates from the manifest's counts.
REGRESSOR = {"C": "carry", "A": "addr"}


def regressor_bits(man, name, zero):
    """Delta of the family's own regressor between a rung and its zero, per 256-bit op."""
    fam = man.family(name)
    kind = REGRESSOR.get(fam)
    if kind is None:
        return man.designed_flips(name) - man.designed_flips(zero), "port+result bits/op"
    return man.c(name, kind) - man.c(zero, kind), kind + " bits/op"


def pp_of(d, leg="board"):
    """{pass: value} for a derived quantity, so quantities measured in the same pass can be
    combined pass by pass instead of through a quadrature SE."""
    if not d:
        return {}
    s = d.get(leg) or {}
    return dict(zip(s.get("passes") or [], s.get("per_pass") or []))


def pp_stat(series_map, family=None, identified_by=None, unit="J/flip", v_rail=None, notes=None,
            rail_map=None):
    """Wrap a {pass: value} map (and optionally its rail twin) as a derived entry."""
    out = {"unit": unit, "family": family, "identified_by": identified_by, "notes": list(notes or [])}
    for leg, m in (("board", series_map), ("rail", rail_map or {})):
        s = with_t(stat(sorted(m.items())))
        if v_rail and unit.startswith("J"):
            s.update(units(s["value"], v_rail))
            s["units_from"] = "rail (quote these)" if leg == "rail" else "board (reference only)"
        out[leg] = s
    for k in ("value", "se", "se_robust", "median", "t", "df", "p_two", "t_crit_3sigma",
              "abs_t_ge_3sigma", "n_passes", "passes"):
        out[k] = out["board"].get(k)
    out["rail_value"] = out["rail"]["value"]
    out["rail_se"] = out["rail"]["se"]
    if unit.startswith("J"):
        out["fJ"] = None if out["value"] is None else out["value"] * 1e15
        out["se_fJ"] = None if out["se"] is None else out["se"] * 1e15
        out["rail_fJ"] = None if out["rail_value"] is None else out["rail_value"] * 1e15
    return out


def pp_combine(a, b, op):
    """{pass: f(a,b)} over the passes both quantities have."""
    return dict((p, op(a[p], b[p])) for p in sorted(set(a) & set(b)))


# =================================================================================================
# the physics skeptic's loop-head-alignment finding (wf4/skeptic)
# =================================================================================================
# A2.1 measured the issue rate as a property of the MODE, not of the data: 0.5814 ops per cycle per
# hart for modes 202/300/302/306-308 and 0.6088 for 177/179/191/301/303/309, constant in h to 1e-4
# within a mode and identical on all three cards.  A2 left WHY open.  The physics skeptic's answer,
# from the objdump of the same binary the campaign ran, is instruction-fetch alignment: the level is
# set by the LOOP HEAD'S ADDRESS MOD 32.  That is checked here rather than quoted, when the
# disassembly is on disk.
DIS_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "docs", "reports", "data", "2026-10-21-dtf", "proof", "enercat-df-aifoundry2.dis.txt")
SKEPTIC_CITE = "E61's physics review"
_DIS_RX = re.compile(r"^\s+([0-9a-f]{6,16}):\s+([0-9a-f ]+?)\s{2,}(\S+)\s*(.*)$")
# the c2 shape's four opcodes -> the mode ids §7 assigns them (the file never hard-codes a mode id
# for a measurement; this map exists only to join the disassembly to A2_MODE_IPC)
_C2_MODE = {"fand.pi": 300, "for.pi": 301, "fadd.pi": 302, "fxor.pi": 303}
_ADDR_MODES = (306, 307, 308, 309)


def loop_head_alignment(path=None):
    """Join every long vector loop's head address to the issue rate A2.1 measured for its mode.

    Returns None when the disassembly is not on disk, in which case the finding is carried as an
    external one with its citation.
    """
    path = path or DIS_DEFAULT
    if not path or not os.path.exists(path):
        return None
    ins = []
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = _DIS_RX.match(line.rstrip("\n"))
                if m:
                    ins.append((int(m.group(1), 16), m.group(3), m.group(4).strip()))
    except Exception as exc:
        return {"error": "%s: %s" % (type(exc).__name__, exc), "path": path}
    if not ins:
        return {"error": "no instruction lines parsed", "path": path}

    def isvec(mn):
        return (".pi" in mn) or (".ps" in mn)

    runs, i = [], 0
    while i < len(ins):
        if isvec(ins[i][1]):
            j = i
            while j + 1 < len(ins) and isvec(ins[j + 1][1]):
                j += 1
            if j - i + 1 >= 24:
                runs.append((i, j))
            i = j + 1
        else:
            i += 1
    c2, addr, other = {}, [], []
    for a, b in runs:
        head, mn, ops = ins[a]
        parts = [x.strip() for x in ops.split(",")]
        rec = {"head": "0x%x" % head, "mod32": head % 32, "mod16": head % 16, "mod64": head % 64,
               "mnemonic": mn, "n_vector_ops": b - a + 1, "first_operands": ops}
        if mn in _C2_MODE and len(parts) == 3 and parts[2] == "ft7":
            c2[_C2_MODE[mn]] = rec                      # the c2 shape: third operand pinned to ft7
        elif mn == "fxor.pi" and len(parts) == 3 and parts[1] == parts[2]:
            addr.append(rec)                            # df.addr.a*: vs2 == vs1, index-only work
        else:
            other.append(rec)
    out = {"source": path, "cite": SKEPTIC_CITE, "n_long_vector_loops": len(runs),
           "c2_by_mode": c2, "addr_heads": addr,
           "how": "maximal runs of >= 24 packed-vector instructions are the unrolled loop bodies; the "
                  "run's first address is the loop head. The c2 family is identified by its pinned "
                  "third operand (ft7) and its opcode, which fixes its mode; the four df.addr kernels "
                  "are identified by vs2 == vs1 (index-only work) and are counted, not named, since "
                  "the emission order does not label them."}
    # the c2 family decides the mapping: four modes, four heads, two rates
    lev = {}
    for mode, rec in sorted(c2.items()):
        r = A2_MODE_IPC.get(mode)
        rec["measured_ops_per_cycle_per_hart"] = r
        if r is not None:
            lev.setdefault(rec["mod32"], set()).add(round(r, 4))
    out["rate_by_head_mod32_from_c2"] = dict((k, sorted(v)) for k, v in sorted(lev.items()))
    out["one_rate_per_residue"] = bool(lev and all(len(v) == 1 for v in lev.values()))
    out["residues_distinct"] = bool(len(lev) >= 2
                                    and len(set(tuple(sorted(v)) for v in lev.values())) == len(lev))
    fast = sorted((sorted(v)[0], k) for k, v in lev.items())
    out["fast_residue"] = (fast[-1][1] if fast else None)
    out["slow_residue"] = (fast[0][1] if fast else None)
    out["fast_rate"] = (fast[-1][0] if fast else None)
    out["slow_rate"] = (fast[0][0] if fast else None)
    # the address family: a COUNT check, because the heads cannot be named a0/a1/a3/a5 from the bytes
    if addr and out["fast_residue"] is not None:
        heads_fast = sum(1 for r in addr if r["mod32"] == out["fast_residue"])
        heads_slow = sum(1 for r in addr if r["mod32"] == out["slow_residue"])
        modes_fast = sum(1 for m in _ADDR_MODES
                         if A2_MODE_IPC.get(m) is not None
                         and abs(A2_MODE_IPC[m] - out["fast_rate"]) < 5e-4)
        modes_slow = sum(1 for m in _ADDR_MODES
                         if A2_MODE_IPC.get(m) is not None
                         and abs(A2_MODE_IPC[m] - out["slow_rate"]) < 5e-4)
        out["addr_count_check"] = {
            "heads_at_the_fast_residue": heads_fast, "heads_at_the_slow_residue": heads_slow,
            "modes_at_the_fast_rate": modes_fast, "modes_at_the_slow_rate": modes_slow,
            "agrees": bool(heads_fast == modes_fast and heads_slow == modes_slow),
            "note": "the four df.addr kernels cannot be matched one-to-one to modes 306-309 from the "
                    "bytes alone, so this is a COUNT match: how many heads sit at each residue "
                    "against how many of the four modes run at each rate."}
    out["finding"] = (
        "the two issue-rate levels follow the loop head's address mod 32: heads at %s (mod 32) issue "
        "%s ops per cycle per hart and heads at %s issue %s, a %s%% difference with nothing in the "
        "data changing -- an instruction-FETCH alignment effect, measured off the same binary the "
        "campaign ran (physics skeptic, %s)"
        % (out.get("fast_residue"), out.get("fast_rate"), out.get("slow_residue"),
           out.get("slow_rate"),
           ("%.2f" % (100.0 * (out["fast_rate"] / out["slow_rate"] - 1.0)))
           if (out.get("fast_rate") and out.get("slow_rate")) else "n/a",
           SKEPTIC_CITE)) if out.get("one_rate_per_residue") else (
        "the loop heads were parsed but the residue-to-rate map is not one-to-one here; the finding "
        "is carried as external (physics skeptic, %s)" % SKEPTIC_CITE)
    return out


LOOP_HEAD = {}


# =================================================================================================
# one card
# =================================================================================================
def analyse_card(card, R, man, args, missing, leak_override=None):
    C = {"card": card, "n_runs": len(R)}
    gov_free = card not in PINNED_CARDS
    # RECON 5: `leak_override` runs the SAME reduction at another leakage slope, which is how the
    # sensitivity arm is built.  §8.1 registers the card's own FITTED slope, and E60 fitted
    # 0.203 / 0.442 / 0.327 W/C on whole-degree sensor steps; tonight's fit is far smaller, so every
    # quantity is reported at the fitted slope (primary), at k = 0, and at E60's slope.
    if leak_override is not None:
        k, nk = float(leak_override), -2
    else:
        k, nk = leak_slope(R) if args.leak == "auto" else (float(args.leak), -1)
    clocks = [r["mhz"][0] for r in R if len(r["mhz"]) == 1]
    clock = int(np.median(clocks)) if clocks else None
    for r in R:
        base = r["start_c"] if r["start_c"] is not None else r["t_win"]
        r["p80"] = r["p_raw"] - k * (r["t_win"] - base)
    C["clock_mhz"] = clock
    C["gov_free"] = gov_free
    C["leak_W_per_C"] = k
    C["leak_runs"] = nk
    C["leak_is_fallback"] = (nk == 0)
    C["leak_is_override"] = (nk == -2)              # RECON 5
    C["leak_E60_W_per_C"] = E60["leak_W_per_C"].get(card)
    C["leak_qualifying_run_pct"] = (100.0 * nk / len(R)) if (nk and nk > 0 and R) else None

    # ---- §8.2 gates, per run
    nopass = [r for r in R if r["pass"] is None]
    if nopass:
        missing.append("%s: %d run(s) carry no pass number (no `block` in marks.jsonl and no `pass` "
                       "in block.json) and are dropped: %s"
                       % (card, len(nopass), sorted({r["item"] for r in nopass})))
        R = [r for r in R if r["pass"] is not None]
        C["n_runs"] = len(R)
        if not R:
            C["note"] = "every run on this card lacks a pass number"
            return C, []
    pass_ids = sorted({r["pass"] for r in R})
    # FIX.8: the unit's pass ids are written here, before any gate can empty the set, so a block that
    # keeps no run still reports its passes instead of "passes None (registered None)".
    C["pass_ids_seen"] = pass_ids
    C["passes"] = list(pass_ids)
    C["n_passes"] = len(pass_ids)
    exp_name = str(R[0].get("exp") or "dtf") if R else "dtf"
    C["n_passes_registered"] = 4 if "cam" in exp_name else E60["n_passes"].get(card)
    C["n_passes_prereg_s6"] = E60["n_passes_prereg_s6"].get(card)
    # FIX.7: a block that ran with NO PREHEAT has no launch reading to be on-protocol against.  §10(a)
    # runs the dtf-cam block "with no heater and no anchor", and its `--target` is the runner's
    # never-wait sentinel, so the gate would reject every run on |start_c - 200| > 0.5.
    no_preheat = all(r.get("preheat") == 0 for r in R) and any(r.get("preheat") is not None for r in R)
    C["launch_gate_applied"] = not no_preheat
    if no_preheat:
        sc = clean([r["start_c"] for r in R])
        C["launch_gate_skipped"] = {
            "reason": "this block ran with --preheat 0 (no heater): §10(a)'s contiguous dtf-cam block. "
                      "Its --target %s is the runner's never-wait sentinel, not a launch reading, so "
                      "the on-protocol launch gate does not apply and the realised spread is reported "
                      "instead." % (sorted({r.get("target") for r in R}) or None),
            "start_c_min": (min(sc) if sc else None), "start_c_max": (max(sc) if sc else None),
            "start_c_mean": (float(np.mean(sc)) if sc else None),
            "on_protocol_all": all(bool(r.get("on_protocol")) for r in R)}
    med_mv = dict((p, float(np.median([r["mv"] for r in R if r["pass"] == p]))) for p in pass_ids)
    for r in R:
        why = []
        it = man.get(r["item"])
        if clock is not None and r["mhz"] != [clock]:
            why.append("clock %s" % (r["mhz"],))
        if r.get("ramp_ms") is not None and (not np.isfinite(r["ramp_ms"]) or r["ramp_ms"] > 1500):
            why.append("ramp %s ms" % fmt(r["ramp_ms"], 0))
        if abs(r["mv"] - med_mv.get(r["pass"], r["mv"])) > 3:
            why.append("die_mv.minion %.1f vs the pass median %.1f (>3 mV)"
                       % (r["mv"], med_mv.get(r["pass"], float("nan"))))
        if not no_preheat:          # FIX.7: no launch reading on a --preheat 0 block
            if not r["on_protocol"] or r["start_c"] is None or r["target"] is None \
                    or abs(r["start_c"] - r["target"]) > 0.5:
                why.append("launch %s (target %s)" % (r["start_c"], r["target"]))
        elif not r["on_protocol"]:
            why.append("the runner marked this launch off-protocol")
        if not r["ok_records"]:
            why.append("a launch record is not ok")
        exp_p = it.get("participants_expected")
        if exp_p is not None and r["participants"] and r["participants"] != [int(exp_p)]:
            why.append("participants %s expected %s" % (r["participants"], exp_p))
        exp_h = it.get("harts")
        if exp_h is not None and r["harts"] and r["harts"] != [int(exp_h)]:
            why.append("harts %s expected %s" % (r["harts"], exp_h))
        exp_m = it.get("shires")
        if exp_m and r["shire_mask_used"]:
            want = str(exp_m).lower()
            if want.startswith("0x") and r["shire_mask_used"] != [want]:
                why.append("shire mask %s expected %s" % (r["shire_mask_used"], want))
        r["fail"] = why
    # the ec RATE gate: 0.5% against the item's own family zero rung in the same pass.
    # A2.1: it fires ONLY when the rung and its zero carry the same mode.  Across modes the rate is a
    # property of the compiled case, so the comparison is reported as a ratio and never gated; and an
    # item the manifest marks `rate_confounded` is outside its ladder by name, so it is not gated at all.
    cross = {}
    rc_seen = set()
    for p in pass_ids:
        zipc = {}
        for n in {r["item"] for r in R if r["pass"] == p}:
            v = [r["ipc"] for r in R if r["pass"] == p and r["item"] == n and r["ipc"] is not None]
            if v:
                zipc[n] = float(np.mean(v))
        for r in R:
            if r["pass"] != p or r["ipc"] is None:
                continue
            n = r["item"]
            z = man.zero_of(n)
            if not (z and z != n and z in zipc and zipc[z]):
                continue
            ratio = r["ipc"] / zipc[z]
            if man.rate_confounded(n):
                rc_seen.add(n)
                cross.setdefault((n, z), []).append(ratio)
                r["rate_confounded"] = True
                continue
            if not man.same_mode(n, z):
                cross.setdefault((n, z), []).append(ratio)
                continue
            if abs(ratio - 1.0) > 0.005:
                r["fail"].append("rate %.5f vs zero %s %.5f (>0.5%%, same mode %s)"
                                 % (r["ipc"], z, zipc[z], man.mode_key(n)))
    C["rate_gate"] = {
        "within_mode_only": True,
        "cross_mode_ratios_reported_not_gated": dict(
            ("%s/%s" % (n, z), {"mode": str(man.mode_key(n)), "zero_mode": str(man.mode_key(z)),
                                "mean_ratio": float(np.mean(v)), "n_passes": len(v),
                                "pct": (float(np.mean(v)) - 1.0) * 100.0,
                                "rate_confounded_by_name": man.rate_confounded(n)})
            for (n, z), v in sorted(cross.items())),
        "rate_confounded_items": sorted(rc_seen),
        "note": "A2: every rate gate compares runs of ONE mode.  A cross-mode ratio is printed because "
                "the rate is fixed by the compiled case (0.5814 / 0.6088 / 0.7356 / 0.7574 ops per "
                "cycle per hart by mode, constant in h to 1e-4), not by the data; an item marked "
                "rate_confounded is excluded from its family's ladder by name and reported beside it, "
                "as amendment A3 excludes an item -- it is not a gate failure."}
    # §6 amendment A3, pre-registered: an item whose clock gate fails in >= 3 of the first 5 passes
    # is excluded by name from the analysis AND from the pass-rejection count.
    first5 = pass_ids[:5]
    clock_fails = defaultdict(set)
    for r in R:
        if r["pass"] in first5 and any(f.startswith("clock") or f.startswith("ramp") for f in r["fail"]):
            clock_fails[r["item"]].add(r["pass"])
    excluded = set(n for n, ps in clock_fails.items() if len(ps) >= 3)
    for spec in (args.exclude or []):
        cn, _, nm = spec.partition(":")
        if nm and cn in (card, "*"):
            excluded.add(nm)
    C["excluded_a3"] = sorted(excluded)
    C["excluded_a3_detail"] = dict((n, sorted(clock_fails[n])) for n in sorted(excluded) if n in clock_fails)
    Ra = [r for r in R if r["item"] not in excluded]

    # §8.2 matched-pair rate gate at 0.2%, per pass per group; a failure VOIDS THAT SUBTRACTION.
    # A2.1: `man.groups` is already split by mode, so no group spans two opcodes.
    # A2.2: the void is LOCAL.  It removes that pass from that pair group's own subtraction and from
    # nothing else -- the runs stay in every other quantity.  (Deleting the runs outright is what made
    # family V read "absent" on data that passed every per-run gate.)
    voids = []
    voided_group_passes = defaultdict(set)      # gkey -> {pass}
    for p in pass_ids:
        for gkey, members in man.groups.items():
            got = {}
            for n in members:
                v = [r["ipc"] for r in Ra if r["pass"] == p and r["item"] == n and r["ipc"] is not None]
                if v:
                    got[n] = float(np.mean(v))
            if len(got) < 2:
                continue
            lo, hi = min(got.values()), max(got.values())
            if lo and (hi / lo - 1.0) > 0.002:
                voids.append({"pass": p, "group": gkey, "ipc": got, "spread": hi / lo - 1.0,
                              "mode": str(man.mode_key(sorted(got)[0])),
                              "scope": "this group's own subtraction in this pass only; the runs stay "
                                       "in every other quantity (A2)"})
                voided_group_passes[gkey].add(p)
    C["pair_gate_voids"] = voids
    C["pair_groups"] = dict((k, {"members": v, "mode": str(man.mode_key(v[0]))})
                            for k, v in sorted(man.groups.items()))
    C["pair_links_crossing_mode"] = list(man.pair_links_crossing_mode)
    void_keys = set()                           # A2.2: no run is dropped by a void any more

    # ---- §8.9 set-aside, scaled
    drift_rows = {}
    for p in pass_ids:
        rp = [r for r in Ra if r["pass"] == p]
        pis = [r for r in rp if man.family(r["item"]) == "anchor" and not r["fail"]]
        if len(pis) >= 2:
            x = [(r["t_mid_ms"] - min(q["t_mid_ms"] for q in pis)) / 60000.0 for r in pis]
            y = [r["p80"] for r in pis]
            f = fit_line(x, y)
            span_min = max(x) - min(x)
            drift_rows[p] = {"W_per_min": f[1] if f else None, "span_min": span_min,
                             "n_anchor": len(pis),
                             "W_per_5min": (f[1] * 5.0) if f else None,
                             "first_last_W": y[-1] - y[0]}
        else:
            drift_rows[p] = {"W_per_min": None, "span_min": None, "n_anchor": len(pis),
                             "W_per_5min": None, "first_last_W": None}
    dvals = clean([d["W_per_5min"] for d in drift_rows.values()])
    drift_sd = float(np.std(dvals, ddof=1)) if len(dvals) > 1 else None
    drift_thresh = max(0.3, 3.0 * drift_sd) if drift_sd else 0.3
    set_aside = []
    for p in pass_ids:
        rp = [r for r in Ra if r["pass"] == p]
        nf = sum(1 for r in rp if r["fail"])
        # RECON 2: §8.9 reads "more than 5% of its runs fail a gate (floor 2 runs)" -- a CONJUNCTION,
        # not max(2, 5%).  The old `nf > max(2, 0.05 n)` needed 3 failures in a 38-run pass, so 2 of
        # 38 = 5.26% was kept.  The floor is on the COUNT (>= 2 runs), the test on the FRACTION.
        frac_thresh = 0.05 * len(rp)
        d5 = drift_rows[p]["W_per_5min"]
        why = []
        if nf >= 2 and nf > frac_thresh:
            why.append("%d of %d runs failed a gate (%.2f%% > 5%%, and >= the 2-run floor)"
                       % (nf, len(rp), 100.0 * nf / len(rp)))
        if d5 is not None and abs(d5) > drift_thresh:
            why.append("anchor drift %.3f W/5min (>%.3f)" % (d5, drift_thresh))
        if why:
            set_aside.append({"pass": p, "why": why, "failed_runs": nf, "runs": len(rp),
                              "fail_pct": (100.0 * nf / len(rp)) if rp else None,
                              "rule": "RECON 2: > 5% of the pass's runs AND >= 2 runs (§8.9)",
                              "drift_W_per_5min": d5})
    bad_passes = {x["pass"] for x in set_aside}
    C["drift"] = drift_rows
    C["drift_between_pass_sd_W_per_5min"] = drift_sd
    C["drift_threshold_W_per_5min"] = drift_thresh
    C["passes_set_aside"] = set_aside

    G = [r for r in Ra if not r["fail"] and r["pass"] not in bad_passes
         and (r["pass"], r["item"]) not in void_keys]
    C["gates"] = {"runs": len(R), "runs_after_a3": len(Ra), "kept": len(G),
                  "failed": [[r["pass"], r["item"], r["pos"], r["fail"]] for r in Ra if r["fail"]],
                  "fail_rate": (sum(1 for r in Ra if r["fail"]) / float(len(Ra))) if Ra else None}
    # A2.2: the local void map, read by family_estimates so a voided pair group loses that pass from
    # its OWN subtraction and from nothing else.
    C["voided_group_passes"] = dict((k, sorted(v)) for k, v in sorted(voided_group_passes.items()))
    if not G:
        C["note"] = "no run survived the gates on this card"
        return C, []

    v_rail = float(np.mean([r["mv"] for r in G])) / 1000.0
    C["v_mean"] = v_rail
    C["n_dump_lines"] = int(max(r["n_dump_lines"] for r in G))

    # ---- §8.3 / §8.10 one value per (pass, item); duplicates averaged, their spread reported
    val = defaultdict(dict)
    dup = {}
    KEYS = ("p80", "p_raw", "p_raw14", "rail", "rate", "ipc", "mv", "t_win", "peak_spread_c")
    for p in sorted({r["pass"] for r in G}):
        for item in sorted({r["item"] for r in G if r["pass"] == p}):
            rr = [r for r in G if r["pass"] == p and r["item"] == item]
            e = {}
            for key in KEYS:
                vv = clean([r[key] for r in rr])
                e[key] = float(np.mean(vv)) if vv else None
            e["n_runs"] = len(rr)
            val[p][item] = e
            if len(rr) > 1:
                dup.setdefault(item, []).append(max(r["p80"] for r in rr) - min(r["p80"] for r in rr))
    passes = sorted(val)
    C["passes"] = passes
    C["n_passes"] = len(passes)
    # (C["n_passes_registered"] was set above the gates -- cam-aware -- and is not overwritten here)
    C["dup_repeat_spread_W"] = dict((n, {"mean": float(np.mean(v)), "max": float(max(v)), "n": len(v)})
                                    for n, v in sorted(dup.items()))

    # ---- per-item table: absolute and (item - its family zero)
    items = {}
    for name in sorted({i for p in passes for i in val[p]}):
        it = man.get(name)
        z = man.zero_of(name)
        e = {"family": it.get("family"), "op": it.get("op"), "h": it.get("h"), "L": it.get("L"),
             "zero": z, "zero_word": it.get("zero_word"), "dup": it.get("dup"),
             "counts": it.get("counts"), "ops_per_iter": it.get("ops_per_iter")}
        for key in ("p80", "p_raw", "p_raw14", "rail", "rate", "ipc", "peak_spread_c"):
            m_, se, n = mean_se([val[p][name].get(key) for p in passes if name in val[p]])
            e[key], e[key + "_se"], e["n_passes"] = m_, se, n
        if z and z != name:
            for key in ("p80", "rail"):
                ser = [(p, val[p][name][key] - val[p][z][key]) for p in passes
                       if name in val[p] and z in val[p]
                       and val[p][name].get(key) is not None and val[p][z].get(key) is not None]
                s = with_t(stat(ser))
                e["d_" + key] = s["value"]
                e["d_" + key + "_se"] = s["se"]
                e["d_" + key + "_se_robust"] = s["se_robust"]
                e["d_" + key + "_n"] = s["n_passes"]
                e["d_" + key + "_t"] = s["t"]
            if e.get("d_p80") is not None and e.get("rate"):
                bits, reg = regressor_bits(man, name, z)
                e["regressor_bits_per_op"], e["regressor"] = bits, reg
                e["d_fJ_per_op"] = e["d_p80"] / e["rate"] * 1e15
                if bits:
                    e["d_fJ_per_regressor_bit"] = e["d_p80"] / (bits * e["rate"]) * 1e15
        items[name] = e
    C["items"] = items

    # ---- the IPC of every shape against mode 179's (§9, claim S10) -- reported, never a gate
    ipc_by_shape = {}
    for name, e in items.items():
        if e.get("ipc") is None:
            continue
        key = ("%s / ops_per_iter %s / harts %s" % (e.get("op"), e.get("ops_per_iter"),
                                                    man.get(name).get("harts") or 1)
               if e.get("op") else "NOT IN THE MANIFEST (%s)" % name)
        ipc_by_shape.setdefault(key, []).append((name, e["ipc"]))
    ref = [v for n, v in ipc_by_shape.get("fxor.pi / ops_per_iter 64 / harts 1", [])
           if n.startswith("xin")]
    ipc_ref = float(np.mean(ref)) if ref else None
    # RECON 10: S10 registers the comparison against mode 179's 0.5791 -- E60's number, the one the
    # claim is about -- not against tonight's own mode 179.  Comparing against tonight's reference
    # hides the finding (mode 179 itself shifted +5.1% between builds) and flags the wrong shapes:
    # every shape that merely shares tonight's 0.6088 reads 0.0% and looks matched, while the three
    # that actually sit at 0.5814 read -4.5% and look anomalous.  Both columns are now written, with
    # the REGISTERED one carrying the flag.
    ipc_reg = E60["rate_per_hart"]

    def _ipc_row(vs, key=""):
        m_ = float(np.mean([v for _, v in vs]))
        # RECON 10: the registered 0.5791 is a ONE-HART number (E60 measured 0.3665 per hart on its
        # two-hart arms), so a harts-2 shape is compared against that instead and carries its own
        # flag; comparing it with the one-hart reference printed a meaningless -35%.
        h2 = "harts 2" in str(key)
        ref_ = 0.3665 if h2 else ipc_reg
        return {"ipc": m_, "items": len(vs), "harts": 2 if h2 else 1,
                "reference_used": ref_,
                "reference_name": ("E60's own two-hart 0.3665 per hart" if h2
                                   else "the REGISTERED one-hart 0.5791"),
                "vs_registered_0_5791_pct": (m_ / ipc_reg - 1) * 100.0,
                "vs_its_own_reference_pct": (m_ / ref_ - 1) * 100.0,
                "flag_gt_1pct": bool(abs(m_ / ref_ - 1) > 0.01),
                "vs_tonights_mode179_pct": ((m_ / ipc_ref - 1) * 100.0) if ipc_ref else None,
                "flag_gt_1pct_vs_tonights_mode179": (bool(abs(m_ / ipc_ref - 1) > 0.01)
                                                     if ipc_ref else None)}

    C["ipc"] = {"reference_mode179_fxor_rot2": ipc_ref, "E60_reference": ipc_reg,
                "registered_reference_used_for_the_flag": ipc_reg,
                "mode179_build_shift_pct": ((ipc_ref / ipc_reg - 1) * 100.0) if ipc_ref else None,
                "note": "instructions per cycle per PARTICIPATING hart, from each ENERCAT record's "
                        "own ops / cycles_max / participants inside the power window; the harts-2 "
                        "arms are listed separately because E60 measured 0.3665 per hart there. "
                        "RECON 10: the flag is against the REGISTERED 0.5791 (S10's own number), with "
                        "tonight's mode-179 reading printed beside it.",
                "shapes": dict((k, _ipc_row(vs, k)) for k, vs in sorted(ipc_by_shape.items()))}

    # ---- §8.4 the ladders: one per (family, op, zero) with its own registered regressor
    C["ladders"] = {}
    groups = defaultdict(list)
    for name in items:
        z = man.zero_of(name)
        if not z or z == name or z not in items:
            continue
        # A2.4: family A's three matched rungs are three MODES that share one rate, and A2 registers
        # them as one ladder, so family A groups by its zero rung alone and the rate-confounded rung
        # (d5_a5, mode 309) is kept out by name and reported beside the ladder.
        if items[name]["family"] == "A":
            if man.rate_confounded(name):
                continue
            groups[("A", "df.addr", z)].append(name)
            continue
        groups[(items[name]["family"], items[name]["op"], z)].append(name)
    for (fam, op, z), names in sorted(groups.items(), key=lambda kv: str(kv[0])):
        names = sorted(names, key=lambda n: (man.get(n).get("h") or 0, man.get(n).get("L") or 0,
                                             man.get(n).get("delta") or 0, n))
        bits_of = dict((n, regressor_bits(man, n, z)[0]) for n in names)
        rungs = [n for n in names if bits_of[n]]
        # A ladder must be zero-word-homogeneous with its own zero rung, or the zero-operand term
        # rides on the slope: that is exactly how ain_h32 (E60 amendment A1), d3p_L29 and
        # m_solid_z are built, and each is reported on its own below.
        zw0 = bool(man.get(z).get("zero_word"))
        mismatch = [n for n in rungs if bool(man.get(n).get("zero_word")) != zw0]
        dropped, inhomogeneous = [], []
        if mismatch and len(mismatch) < len(rungs):
            dropped = mismatch
            rungs = [n for n in rungs if n not in dropped]
        elif mismatch:
            # every rung mismatches its zero (family 7's hi-vs-lo, family Z's one-vs-zero): the
            # contrast IS the zero-word step, so it is kept and labelled rather than emptied
            inhomogeneous = mismatch
        if not rungs:
            continue
        reg = regressor_bits(man, rungs[0], z)[1]
        LB = ladder(val, passes, rungs, z, lambda n: bits_of[n])
        LR = ladder(val, passes, rungs, z, lambda n: bits_of[n], key="rail")
        key = "%s|%s|%s" % (fam, op, z)
        form = "multi" if LB["multi"] else "single"
        ent = {"family": fam, "op": op, "zero": z, "regressor": reg, "rungs": rungs,
               "excluded_zero_word_mismatch": dropped,
               "zero_word_inhomogeneous": inhomogeneous,
               "n_rungs": len(rungs), "bits_per_op": bits_of,
               "fit_form": form, "rungs_used_per_pass": LB["used"],
               "first_rung_step_W": with_t(stat(
                   [(p, val[p][rungs[0]]["p80"] - val[p][z]["p80"]) for p in passes
                    if rungs[0] in val[p] and z in val[p]
                    and val[p][rungs[0]].get("p80") is not None and val[p][z].get("p80") is not None])),
               "first_rung": rungs[0],
               "residual_rms_W": float(np.mean(LB["resid"])) if LB["resid"] else None}
        # A2: a ladder's modes, and whether it is a single-mode ladder (every rate gate is within one
        # mode) or the one cross-mode ladder the amendment registers (family A's a0/a1/a3, equal rate).
        ent["modes"] = sorted({str(man.mode_key(n)) for n in rungs} | {str(man.mode_key(z))})
        ent["single_mode"] = (len(ent["modes"]) == 1)
        if fam == "A":
            ent["a2_note"] = ("A2.4: a0, a1 and a3 are three modes that share one rate (0.5814 ops per "
                              "cycle per hart, 1e-4 apart), so the amendment registers them as ONE "
                              "ladder; a5 (mode 309, 4.7% faster by code) is outside the slope and "
                              "reported beside it as rate-confounded")
            ent["rate_confounded_excluded"] = sorted(n for n in man.by_family("A")
                                                     if man.rate_confounded(n) and n in items)
        elif fam == "V":
            ent["a2_note"] = ("A2.3: each V arm is a ladder against its OWN zero rung, fitted on the "
                              "regressor the two arms share (port+result bits/s, 16h in both); e_cell "
                              "is the DIFFERENCE of the two slopes, not this slope")
        # XCHK 5: E60 subtracted ain_h0 from the ain ladder (reduce_hl.py:30-31).  The E61 lists have no
        # ain_h0, so if the manifest points the ain items at xin_h0 the slope carries alpha(fand)-alpha(fxor)
        # and is not the 28.10 fJ tie.  Any such ladder is named rather than quietly compared with E60.
        z_op = man.get(z).get("op")
        if z_op and op and opcode_of(z_op) != opcode_of(op):
            ent["zero_rung_other_opcode"] = z_op
            C.setdefault("warnings", []).append(
                "ladder %s: its zero rung %s is a %s item, so this slope carries alpha(%s) - alpha(%s) and is "
                "NOT a matched-opcode price (E60 subtracted the same opcode's own h0 rung)"
                % (key, z, z_op, opcode_of(op), opcode_of(z_op)))
        ent["slope"] = pp_stat(LB[form], family=fam, identified_by=key, unit="J/flip",
                               v_rail=v_rail, rail_map=LR[form],
                               notes=["§8.4: free intercept over the %d nonzero rungs" % len(rungs)
                                      if form == "multi" else
                                      "one nonzero rung in each pass: the slope through its zero"])
        for other, note in (("single", "passes that ran a single nonzero rung: the slope through "
                                       "its zero, kept apart from the multi-rung fit"),
                            ("zero_point", "E60's own ec fit: the (0,0) point included and a free "
                                           "intercept -- the form its published anchors came from")):
            if LB[other] and other != form:
                ent["slope_" + other] = pp_stat(LB[other], family=fam, identified_by=key,
                                                unit="J/flip", v_rail=v_rail, rail_map=LR[other],
                                                notes=[note])
        if LB["multi"] and LB["single"]:
            C.setdefault("warnings", []).append(
                "ladder %s: %d pass(es) ran >=2 nonzero rungs and %d ran exactly one; the two fit "
                "forms are reported separately and never averaged"
                % (key, len(LB["multi"]), len(LB["single"])))
        ent["intercept_W"] = pp_stat(LB["intercept"], family=fam, unit="W", v_rail=v_rail,
                                     rail_map=LR["intercept"],
                                     identified_by="%s: the §8.4 free intercept" % key)
        ent["intercept_zero_point_W"] = pp_stat(LB["intercept_zero_point"], family=fam, unit="W",
                                                v_rail=v_rail, rail_map=LR["intercept_zero_point"],
                                                identified_by="%s: the intercept of E60's own ec fit" % key)
        C["ladders"][key] = ent
    return C, (val, passes, items, v_rail, G)


# =================================================================================================
# the per-family estimates (§8.5 / §8.6 / §9's quantities)
# =================================================================================================
def family_estimates(C, man, val, passes, items, v_rail, card, missing, label=None):
    label = label or card
    D = {}
    C["derived"] = D
    F = {}
    C["families"] = F
    # §10(a): the dtf-cam block is its own experiment and carries family 7 only, so "family X absent"
    # there is the design, not a gap.  `missing` keeps the electrical units' gaps only.
    electrical = ("cam" not in str(C.get("experiment") or "")) and ("[" not in str(label))
    if not electrical:
        missing = []        # kept on the unit instead of in the global list, below
        C["families_absent_by_design"] = (
            "this unit is the §10(a) dtf-cam block: four contiguous passes of family 7 only, with no "
            "heater and no anchor, so every other family is absent BY DESIGN -- those lines are kept "
            "on this unit as `absent_by_design_notes`, not in WHAT IS MISSING")
    clock = C.get("clock_mhz") or 600
    # §5.4: the watt-stated R1/R2/R3 readings are the pinned card's; on an 800 MHz card they scale
    # by that card's measured per-bit tie x the clock ratio.
    w_scale = E60["per_bit_tie"].get(card, 1.0) * (clock / 600.0)

    # A2.2: the local void map -- {pair-group key: [passes voided]}, written by analyse_card.  A void
    # reaches ONLY the subtraction between members of that group, and only in that pass.
    VOIDED = C.get("voided_group_passes") or {}

    def voided_for(*names):
        """the passes in which these items' own matched-pair group failed the 0.2% gate"""
        out = set()
        for gkey, ps in VOIDED.items():
            members = set(man.groups.get(gkey) or [])
            if sum(1 for n in names if n in members) >= 2:
                out |= set(ps)
        return out

    def have(*names):
        return all(n in items for n in names)

    # VER 1 (the fix verifier's MUST FIX 1): §5.1's intercept is ONE price per changed 32-bit word --
    # E60's +0.273 W = 48.0 fJ per changed word over rot2's 16 words/op -- and the READING fixes the
    # COUNT, not the price.  So a correction that counts words under reading R2 must divide the
    # measured intercept by the SAME rung's R2 word count (16 for every nonzero d1nz rung: 8 source
    # + 8 result), never by its source-word count alone (8, which is R1's count).  Pricing an R2
    # count at intercept/8 doubles the term, which is what the wf4 build did: §5.1 predicts +0.273 W
    # for `d1nz_h32 - d1nz_h0` under R2 and +0.137 W under R1, both at 48 fJ/word.
    def word_price_W(reading="R2", ref="d1nz_h32"):
        """{W per changed word, words/op of the reference rung} at the N ladder's own intercept."""
        z = man.zero_of(ref)
        wn = man.changed_words(ref, reading) - (man.changed_words(z, reading) if z else 0.0)
        if not wn:
            wn = 16.0 if reading == "R2" else 8.0
        iv = (D.get("intercept_N_W") or {}).get("value")
        return ((iv / wn) if iv is not None else None), wn

    def contrast(terms, bits_terms=None, **kw):
        kw.setdefault("v_rail", v_rail)
        kw.setdefault("skip_passes", voided_for(*[n for _, n in terms]))
        return derived(val, passes, terms, bits_terms, **kw)

    def per_bit(item, zero, bits, **kw):
        kw.setdefault("unit", "J/flip")
        return contrast([(1, item), (-1, zero)], [(1, bits, item)], **kw)

    def find_ladder(fam, op=None, zero=None):
        for key in sorted(C.get("ladders", {})):
            L = C["ladders"][key]
            if L["family"] == fam and (op is None or L["op"] == op) and (zero is None or L["zero"] == zero):
                return key, L
        return None, None

    def hs(prefix):
        """the rungs present for a name prefix, smallest first; the rung variable is h, else L,
        else delta (family A's register-index Hamming distance)"""
        out = []
        for n in items:
            if n.startswith(prefix):
                it = man.get(n)
                v = it.get("h")
                if v is None:
                    v = it.get("L")
                if v is None:
                    v = it.get("delta")
                if v is not None:
                    out.append((float(v), n))
        return sorted(out)

    def xval(p, bits, rate_item):
        """RECON 1: the per-second denominator of one rung.  `rate_item` is EITHER one item name,
        whose own rate prices the whole rung, OR a list of (bits_per_op, item) pairs, one per MODE
        the rung spans -- which is what A2.1 requires of a cross-mode combination like the 2 x 2
        bridge, whose (B-A) half runs on mode 300 and whose (D-C) half runs on mode 301, 4.7%
        faster.  `bits` is then None and the pairs carry the counts."""
        if isinstance(rate_item, (list, tuple)):
            s = 0.0
            for b_, nm_ in rate_item:
                rt = val.get(p, {}).get(nm_, {}).get("rate")
                if not rt or not b_:
                    return None
                s += b_ * rt
            return s or None
        rt = val.get(p, {}).get(rate_item, {}).get("rate")
        if not rt or not bits:
            return None
        return bits * rt

    def slope_over(rungs_xy, free_intercept=True):
        """rungs_xy: [(key, bits_per_op, terms, rate item or [(bits, item), ...])] -> {pass: slope}"""
        sl, inter = {}, {}
        for p in passes:
            xs, ys = [], []
            for _, bits, terms, rate_item in rungs_xy:
                y = combo(val, p, terms, "p80")
                x = xval(p, bits, rate_item)            # RECON 1
                if y is None or x is None:
                    continue
                xs.append(x)
                ys.append(y)
            if len(xs) >= 2:
                f = fit_line(xs, ys)
                if f:
                    inter[p], sl[p] = f[0], f[1]
            elif len(xs) == 1 and xs[0]:
                inter[p], sl[p] = 0.0, ys[0] / xs[0]
        return sl, inter

    def slope_over_rail(rungs_xy):
        sl = {}
        for p in passes:
            xs, ys = [], []
            for _, bits, terms, rate_item in rungs_xy:
                y = combo(val, p, terms, "rail")
                x = xval(p, bits, rate_item)            # RECON 1
                if y is None or x is None:
                    continue
                xs.append(x)
                ys.append(y)
            if len(xs) >= 2:
                f = fit_line(xs, ys)
                if f:
                    sl[p] = f[1]
            elif len(xs) == 1 and xs[0]:
                sl[p] = ys[0] / xs[0]
        return sl

    # ---------------------------------------------------------------- family X: the campaign ties
    kx, Lx = find_ladder("X", "fxor.pi")
    if Lx:
        D["e_in_fxor"] = dict(Lx["slope"])
        D["e_in_fxor"]["identified_by"] = ("family X, the xin ladder (mode 179), %d rungs, the "
                                           "plan's §8.4 fit (%s form)" % (Lx["n_rungs"], Lx["fit_form"]))
        D["e_in_fxor"]["family"] = "X"
        D["e_in_fxor"]["E60_fJ"] = E60["e_in_fxor_fJ"]
        D["e_in_fxor"]["E60_interval_fJ"] = list(E60["e_in_interval_fJ"])
        D["e_in_fxor"]["notes"] = list(D["e_in_fxor"].get("notes") or []) + [
            "§5.2: e_in is an INTERVAL [19.7, 20.9] fJ because the two defensible fits differ -- "
            "this one is the ladder fit that also produces the intercept (E60: 19.71 fJ); "
            "e_in_fxor_E60fit below is the fit E60's 20.83 +- 0.10 anchor came from"]
        if Lx.get("slope_zero_point"):
            D["e_in_fxor_E60fit"] = dict(Lx["slope_zero_point"])
            D["e_in_fxor_E60fit"]["family"] = "X"
            D["e_in_fxor_E60fit"]["identified_by"] = ("family X, the xin ladder with E60's own ec fit "
                                                      "((0,0) included): the form the 20.83 +- 0.10 fJ "
                                                      "anchor came from, so this is the cross-campaign tie")
            D["e_in_fxor_E60fit"]["E60_fJ"] = E60["e_in_fxor_fJ"]
            D["e_in_fxor_E60fit"]["E60_rail_fJ"] = E60["e_in_fxor_rail_fJ"]
        D["intercept_X_W"] = Lx["intercept_W"]
        D["intercept_X_W"]["family"] = "X"
        D["intercept_X_W"]["identified_by"] = ("the xin ladder's §8.4 free intercept (E60 quotes "
                                               "+0.273 W = 48.0 fJ per changed 32-bit source word)")
    else:
        missing.append("%s: no xin ladder -- e_in(fxor) and the X tie are not identified" % label)
    # e_in(fand): ain_h8 is the tie; ain_h32 is E60 amendment A1's excluded zero-word corner
    ain = [n for _, n in hs("ain_") if n != "ain_h32" and (man.get(n).get("h") or 0) >= 1]
    ain_zero = man.zero_of(ain[0]) if ain else None
    if ain and ain_zero in items:
        rr = [(n, man.designed_flips(n) - man.designed_flips(ain_zero),
               [(1, n), (-1, ain_zero)], n) for n in ain]
        sl, inter = slope_over(rr)
        D["e_in_fand"] = pp_stat(sl, family="X", unit="J/flip", v_rail=v_rail,
                                 rail_map=slope_over_rail(rr),
                                 identified_by="family X, the ain ladder (mode 177) %s" % ain,
                                 notes=["ain_h32 excluded: at h=32 its x is the all-zero word "
                                        "(E60 amendment A1)"])
        D["e_in_fand"]["E60_fJ"] = E60["e_in_fand_fJ"]
        D["e_in_fand"]["E60_interval_fJ"] = list(E60["e_in_fand_interval_fJ"])
        # XCHK 5: the same check on the quantity itself, so it reaches `missing` and the verdict reader.
        z_op_a, op_a = man.get(ain_zero).get("op"), man.get(ain[0]).get("op")
        if z_op_a and op_a and opcode_of(z_op_a) != opcode_of(op_a):
            D["e_in_fand"]["zero_rung_other_opcode"] = z_op_a
            D["e_in_fand"]["notes"].append(
                "its zero rung is %s (%s), not an %s rung, so this slope carries alpha(%s) - alpha(%s): it is "
                "NOT comparable with E60's 28.10 +- 0.70 fJ, which came from ain_h8 - ain_h0"
                % (ain_zero, z_op_a, opcode_of(op_a), opcode_of(op_a), opcode_of(z_op_a)))
            missing.append("%s: the ain ladder has no same-opcode zero rung (its zero is %s, a %s item), so "
                           "e_in(fand) carries alpha(fand) - alpha(%s) and the 28.10 fJ E60 tie is not "
                           "measured. One extra item (ain_h0) closes it."
                           % (label, ain_zero, z_op_a, opcode_of(z_op_a)))
    if "ain_h32" in items:
        _a32 = items["ain_h32"]
        _pred = None
        if D.get("e_in_fand", {}).get("value") is not None and _a32.get("rate"):
            _bits = man.designed_flips("ain_h32") - man.designed_flips(man.zero_of("ain_h32") or "ain_h32")
            _pred = D["e_in_fand"]["value"] * _bits * _a32["rate"]
        D["ain_h32_zero_word_corner_W"] = {"unit": "W", "family": "X",
                                           "identified_by": "ain_h32 - its zero (the deliberate zero-word corner)",
                                           "value": items["ain_h32"].get("d_p80"),
                                           "se": items["ain_h32"].get("d_p80_se"),
                                           "rail_value": items["ain_h32"].get("d_rail"),
                                           "rail_se": items["ain_h32"].get("d_rail_se"),
                                           "n_passes": items["ain_h32"].get("d_p80_n"),
                                           "passes": None,
                                           "fJ_per_op": (_a32["d_p80"] / _a32["rate"] * 1e15)
                                           if _a32.get("d_p80") is not None and _a32.get("rate") else None,
                                           "predicted_from_e_in_fand_W": _pred,
                                           "excess_over_fit_W": (_a32["d_p80"] - _pred)
                                           if (_pred is not None and _a32.get("d_p80") is not None) else None,
                                           "excess_over_fit_fJ_per_op": ((_a32["d_p80"] - _pred) / _a32["rate"] * 1e15)
                                           if (_pred is not None and _a32.get("d_p80") is not None
                                               and _a32.get("rate")) else None,
                                           "note": "the deliberate zero-word corner (x = the all-zero "
                                                   "word at h = 32): the excess over the ain fit is the "
                                                   "statistic E60's amendment A1 could only label"}

    # ---------------------------------------------------------------- family N: fnot, the zero word, the intercept
    kn, Ln = find_ladder("N", zero="d1nz_h0")
    kn2, Ln2 = find_ladder("N", zero="d1n_h0")
    for tag, Lx_ in (("d1nz", Ln), ("d1n", Ln2)):
        if Lx_:
            s = dict(Lx_["slope"])
            s["family"] = "N"
            s["identified_by"] = "family N, the %s ladder (mode 202), %d rungs" % (tag, Lx_["n_rungs"])
            D["half_sum_fnot_%s" % tag] = s
            pp = pp_of(Lx_["slope"])
            D["e_sum_fnot_%s" % tag] = pp_stat(dict((p, 2 * v) for p, v in pp.items()),
                                               family="N", unit="J/flip", v_rail=v_rail,
                                               rail_map=dict((p, 2 * v) for p, v in pp_of(Lx_["slope"], "rail").items()),
                                               identified_by="2 x the %s ladder slope = e_in + e_out for fnot.pi" % tag,
                                               notes=["one read port and one result word per op; "
                                                      "E60's anchor interval is [%.2f, %.2f] fJ"
                                                      % E60["e_sum_fnot_interval_fJ"]])
    if Ln and Ln["intercept_W"].get("value") is None:
        # §5.1's three-way discriminator is the d1nz ladder's FREE intercept, which needs >= 2
        # nonzero rungs in a pass.  With one rung the fit goes through the zero and there is no
        # intercept to read -- reported as not identified, never as n/a +- n/a.
        D["intercept_N_W"] = {
            "unit": "W", "family": "N", "value": None, "se": None, "not_identified": True,
            "identified_by": "the d1nz ladder's free intercept (§5.1's discriminator)",
            "n_rungs": Ln.get("n_rungs"), "fit_form": Ln.get("fit_form"),
            "note": "the d1nz ladder has %s nonzero rung(s) here, so its fit goes through the zero "
                    "and carries NO free intercept: §5.1's R1/R2/R3 discriminator is NOT IDENTIFIED "
                    "on this card and the §5.1 corrections are taken from the card that has the "
                    "three-rung ladder (§6 gives aifoundry3 four N rungs and aifoundry1 c0 three)"
                    % Ln.get("n_rungs")}
        missing.append("%s: the d1nz ladder has %s nonzero rung(s), so it has no free intercept and "
                       "§5.1's R1/R2/R3 reading is NOT IDENTIFIED here"
                       % (label, Ln.get("n_rungs")))
    if Ln and Ln["intercept_W"].get("value") is not None:
        D["intercept_N_W"] = dict(Ln["intercept_W"])
        D["intercept_N_W"]["family"] = "N"
        D["intercept_N_W"]["identified_by"] = "the d1nz ladder's free intercept (§5.1's discriminator)"
        iv, ise = Ln["intercept_W"].get("value"), Ln["intercept_W"].get("se")
        dof = Ln["intercept_W"].get("df")
        readings = {}
        for nm, w in (("R1_changed_source_word", 0.137), ("R2_any_changed_word", 0.273),
                      ("R3_result_leaves_zero", 0.000)):
            tgt = w * w_scale
            t = (iv - tgt) / ise if (iv is not None and ise) else None
            readings[nm] = {"target_W": tgt, "t": t, "p_two": t_p_two(t, dof) if t is not None else None,
                            "within_3sigma": (abs(t) < t_crit(THREE_SIGMA_P, dof))
                            if (t is not None and dof) else None}
        F["N_intercept_readings"] = {"scale_vs_600MHz_pinned": w_scale, "readings": readings,
                                     "matched": [k for k, v in readings.items() if v.get("within_3sigma")]}
        # the X vs N cross-check: per changed SOURCE word (16 words/op in rot2, 8 in the unary
        # shape) -- §9's registered OPEN arm for the ladder-intercept row, read on R1's count because
        # that is the count the two shapes share a definition of (VER 1 keeps count and price on one
        # reading; here both legs are source words, so the statistic is self-consistent).
        if D.get("intercept_X_W", {}).get("value") is not None and iv is not None:
            wx = man.c("xin_h32", "src_words") or 16.0
            wn = man.c("d1nz_h32", "src_words") or 8.0
            a = pp_of(D["intercept_X_W"])
            b = pp_of(D["intercept_N_W"])
            F["intercept_per_changed_word_W"] = {
                "reading": "R1 (changed SOURCE words): xin changes %g per op, d1nz %g" % (wx, wn),
                "registered_arm": "§9, the ladder-intercept row: \"the X and N intercepts disagree "
                                  "by > 3 SE after scaling by their word counts -> reported as "
                                  "shape-dependent\"",
                "X_words_per_op": wx, "N_words_per_op": wn,
                "X": with_t(stat(sorted(dict((p, v / wx) for p, v in a.items()).items()))),
                "N": with_t(stat(sorted(dict((p, v / wn) for p, v in b.items()).items()))),
                "X_minus_N": with_t(stat(sorted(pp_combine(a, b, lambda x, y: x / wx - y / wn).items()))),
            }
    # §8.6 the zero-word term: d1n - d1nz at equal h, primary, with its functional form
    zw = {}
    for h, n in hs("d1n_"):
        nz = n.replace("d1n_", "d1nz_")
        if nz in items and n in items:
            zw[h] = contrast([(1, n), (-1, nz)], family="N", unit="W",
                             identified_by="d1n_h%g - d1nz_h%g (matched designed counts)" % (h, h))
            zw[h]["h"] = h
            rate = items[n].get("rate")
            zw[h]["fJ_per_op"] = (zw[h]["value"] / rate * 1e15) if (zw[h]["value"] is not None and rate) else None
            zw[h]["se_fJ_per_op"] = (zw[h]["se"] / rate * 1e15) if (zw[h]["se"] is not None and rate) else None
            zw[h]["flips_per_op"] = man.designed_flips(n)
    F["zero_word_by_h"] = zw
    if zw:
        clean_h = [h for h in zw if h not in (0.0, 32.0)] or sorted(zw)
        hprim = max(clean_h)        # §4: the h=8 and h=16 rungs are the clean ones
        D["zero_word_term"] = dict(zw[hprim])
        D["zero_word_term"]["identified_by"] = "family N primary, h = %g (§8.6)" % hprim
        if hprim in (0.0, 32.0):            # XCHK 6
            D["zero_word_term"]["notes"] = list(D["zero_word_term"].get("notes") or []) + [
                "h = %g is NOT one of §4's clean rungs" % hprim]
            missing.append("%s: the zero-word primary falls on h = %g, which §4 names as not clean (at h = 32 "
                           "d1n's result is the zero word every other op; at h = 0 nothing flips). The clean "
                           "rungs are h = 8 and h = 16, and neither ran in both arms on this card."
                           % (label, hprim))
        D["zero_word_term"]["family"] = "N"
        # the functional form, fitted before it is applied anywhere (§8.6)
        forms = {}
        for nm in ("constant_per_op", "per_flip", "both"):
            res, coefs = [], []
            for p in passes:
                xs, ys = [], []
                for h in sorted(zw):
                    n = "d1n_h%g" % h
                    nz = "d1nz_h%g" % h
                    y = combo(val, p, [(1, n), (-1, nz)], "p80")
                    rt = val.get(p, {}).get(n, {}).get("rate")
                    if y is None or not rt:
                        continue
                    row = []
                    if nm in ("constant_per_op", "both"):
                        row.append(rt)
                    if nm in ("per_flip", "both"):
                        row.append(man.designed_flips(n) * rt)
                    xs.append(row)
                    ys.append(y)
                if len(xs) > len(xs[0]) if xs else False:
                    A = np.asarray(xs, float)
                    b = np.asarray(ys, float)
                    c, *_ = np.linalg.lstsq(A, b, rcond=None)
                    res.append(float(np.sqrt(np.mean((b - A @ c) ** 2))))
                    coefs.append([float(x) for x in c])
            if res:
                terms = ([] + (["fJ_per_op"] if nm in ("constant_per_op", "both") else [])
                         + (["fJ_per_flip"] if nm in ("per_flip", "both") else []))
                mu = [float(np.mean([c[i] for c in coefs])) for i in range(len(coefs[0]))]
                se = [mean_se([c[i] for c in coefs])[1] for i in range(len(coefs[0]))]
                forms[nm] = {"resid_rms_W": float(np.mean(res)), "terms": terms,
                             "coef": mu, "coef_se": se,
                             "coef_fJ": [x * 1e15 for x in mu],
                             "coef_se_fJ": [(x * 1e15 if x is not None else None) for x in se],
                             "n_passes": len(res), "n_params": len(coefs[0])}
        if forms:
            one = dict((k, v) for k, v in forms.items() if v["n_params"] == 1)
            F["zero_word_functional_form"] = {
                "fits": forms,
                "preferred_single_term": min(one, key=lambda k: one[k]["resid_rms_W"]) if one else None,
                "note": "E60's own evidence favours the slope form (xio 30.00 vs xnz 31.17 fJ is "
                        "-3.8% per result bit); 'both' nests the two single-term fits"}

    # ---------------------------------------------------------------- family V: the register-file cell bit
    # A2.3: each arm against its OWN zero rung, both fitted on the regressor the two arms share
    # (port+result bits/s, 16h in both at every h), and e_cell = the DIFFERENCE of the two per-flip
    # slopes rescaled by (port+result bits)/(cell bits), which the manifest's counts make exactly 2.
    # The 0.2% cross-mode pair gate is replaced by each mode's own within-mode rate gate (A2), and each
    # arm's free intercept absorbs its own alpha and the 0.125 address bits/op the shapes differ by.
    pairs = []
    for h, n in hs("d1b_"):
        a = n.replace("d1b_", "d1a_")
        if a in items:
            pairs.append((h, a, n))
    arm_rungs, arm_slope, arm_inter = {}, {}, {}
    for tag, pre in (("1A", "d1a_"), ("1B", "d1b_")):
        rg = [(h, n) for h, n in hs(pre) if h and man.designed_flips(n) > 0]
        z = man.zero_of(rg[0][1]) if rg else None
        if not rg or z not in items:
            continue
        arm_rungs[tag] = {"zero": z, "rungs": [n for _, n in rg],
                          "mode": str(man.mode_key(rg[0][1])),
                          "h": [h for h, _ in rg]}
        rr_arm = [(n, man.designed_flips(n) - man.designed_flips(z), [(1, n), (-1, z)], n)
                  for _, n in rg]
        arm_slope[tag], arm_inter[tag] = slope_over(rr_arm)
        arm_rungs[tag]["rail_slope"] = slope_over_rail(rr_arm)
        arm_rungs[tag]["slope"] = pp_stat(
            arm_slope[tag], family="V", unit="J/flip", v_rail=v_rail,
            rail_map=arm_rungs[tag]["rail_slope"],
            identified_by="family V arm %s (%s), %d rung(s) against its own zero %s, on port+result bits/s"
                          % (tag, arm_rungs[tag]["mode"], len(rr_arm), z),
            notes=["A2.3: the regressor is the port+result count the two arms share (16h in both), so "
                   "the two slopes differ only by the cell term"])
    if "1A" in arm_rungs and "1B" in arm_slope:
        hcommon = sorted(set(arm_rungs["1A"]["h"]) & set(arm_rungs["1B"]["h"]))
        # the rescale, from the manifest: cell bits per port+result bit, checked constant across h
        ratios = set()
        for h in hcommon:
            n = "d1b_h%g" % h
            pr = man.designed_flips(n) - man.designed_flips(arm_rungs["1B"]["zero"])
            cl = man.c(n, "cell") - man.c(arm_rungs["1B"]["zero"], "cell")
            if pr:
                ratios.add(round(cl / pr, 6))
        scale = (1.0 / ratios.pop()) if len(ratios) == 1 and ratios else None
        if ratios:
            C.setdefault("warnings", []).append(
                "family V: the cell-to-port+result ratio is not constant across h (%s), so the slope "
                "difference cannot be rescaled to a per-cell-bit price by one factor" % sorted(ratios))
        diff = pp_combine(arm_slope["1B"], arm_slope["1A"], lambda a_, b_: a_ - b_)
        diff_rail = pp_combine(arm_rungs["1B"]["rail_slope"], arm_rungs["1A"]["rail_slope"],
                               lambda a_, b_: a_ - b_)
        F["V_arms"] = arm_rungs
        F["V_slope_difference_per_portresult_bit"] = pp_stat(
            diff, family="V", unit="J/flip", v_rail=v_rail, rail_map=diff_rail,
            identified_by="slope(1B) - slope(1A), both per port+result flip against their own zeros",
            notes=["the quantity A2 registers; e_cell below is this x %s = (port+result bits)/(cell bits)"
                   % fmt(scale, 3)])
        if scale and hcommon:
            D["e_cell"] = pp_stat(
                dict((p, v * scale) for p, v in diff.items()), family="V", unit="J/flip", v_rail=v_rail,
                rail_map=dict((p, v * scale) for p, v in diff_rail.items()),
                identified_by="family V only (A2.3): [slope(1B, mode %s) - slope(1A, mode %s)] x %s, "
                              "each slope against its own zero rung over h = %s"
                              % (arm_rungs["1B"]["mode"], arm_rungs["1A"]["mode"], fmt(scale, 3),
                                 ", ".join(fmt(h, 0) for h in hcommon)),
                notes=["energy per flipped register-file CELL bit; the bitline and wordline drive is "
                       "common-mode and invisible here (§4) -- a null says the cell flip is cheap, it "
                       "is NOT credited to e_out",
                       "prior 0.3-3 fJ (1/2 CV^2 on a few fF at 0.52 V)",
                       "A2.3: each arm carries its own free intercept, so alpha(mode) and the "
                       "registered 0.125 address bits/op the two shapes differ by stay out of the "
                       "slope -- and the slope is invariant to WHICH constant rung each arm is "
                       "referenced to, which is why reading `zero` from the manifest is safe here",
                       "the cross-mode watt difference d1b - d1a is printed below as rate-confounded "
                       "and is NOT this estimator"])
            D["e_cell"]["prior_fJ"] = list(PRIOR["e_cell_fJ"])
            D["e_cell"]["h_rungs"] = list(hcommon)
            D["e_cell"]["scale_portresult_per_cell_bit"] = scale
            D["e_cell"]["scales_with_h"] = bool(len(hcommon) >= 2)
            if len(hcommon) < 2:
                D["e_cell"]["notes"].append(
                    "ONE shared nonzero rung (h = %s): the §9 CONFIRMED arm also asks the difference to "
                    "SCALE with h, which this card cannot show" % hcommon)
                missing.append("%s: family V has one shared nonzero rung (h = %s), so e_cell cannot be "
                               "shown to scale with h and the §9 CONFIRMED arm is unavailable; the value "
                               "is reported as a bound" % (label, hcommon))
    if pairs:
        F["V_pairs"] = {}
        for h, a, n in pairs:
            d = contrast([(1, n), (-1, a)], family="V", unit="W",
                         identified_by="%s - %s (CROSS-MODE: %s vs %s)"
                                       % (n, a, man.mode_key(n), man.mode_key(a)))
            d["h"] = h
            d["cell_bits_per_op"] = man.c(n, "cell") - man.c(a, "cell")
            d["rate_confounded"] = True
            d["note"] = ("A2: the two arms are different modes (0.7574 vs 0.7356 ops per cycle per "
                         "hart, 2.96% apart by code), so this watt difference carries the rate step "
                         "and is reported, never used as the cell price")
            if d["cell_bits_per_op"] and items[n].get("rate"):
                d["fJ_per_cell_bit_rate_confounded"] = d["value"] / (d["cell_bits_per_op"] * items[n]["rate"]) * 1e15 \
                    if d["value"] is not None else None
            # The rate-free form of the same rung: each arm's OWN h-step taken to J per op at that
            # arm's own rate, then differenced.  This is the per-op cell energy at this h and is the
            # per-rung companion to the slope (at h = 0 it is zero by construction, so it is skipped).
            za, zb = man.zero_of(a), man.zero_of(n)
            pp = {}
            if h and za in items and zb in items:
                for p in passes:
                    vb_, vz_b = val.get(p, {}).get(n, {}), val.get(p, {}).get(zb, {})
                    va_, vz_a = val.get(p, {}).get(a, {}), val.get(p, {}).get(za, {})
                    if any(x.get("p80") is None for x in (vb_, vz_b, va_, vz_a)):
                        continue
                    if not vb_.get("rate") or not va_.get("rate"):
                        continue
                    pp[p] = ((vb_["p80"] - vz_b["p80"]) / vb_["rate"]
                             - (va_["p80"] - vz_a["p80"]) / va_["rate"])
            if pp:
                d["per_op_J_cell_step"] = with_t(stat(sorted(pp.items())))
                d["per_op_fJ"] = (d["per_op_J_cell_step"]["value"] * 1e15
                                  if d["per_op_J_cell_step"]["value"] is not None else None)
                if d["cell_bits_per_op"] and d["per_op_fJ"] is not None:
                    d["fJ_per_cell_bit_this_rung"] = d["per_op_fJ"] / d["cell_bits_per_op"]
                d["per_op_note"] = ("each arm's own h-step in J/op at its own rate, then differenced: "
                                    "rate-free, and the per-rung companion to the A2.3 slope")
            if pp:
                d["_cell_step_pp"] = dict(pp)          # RECON 8: kept for the scaling test below
            F["V_pairs"]["h%g" % h] = d
            if h == 0:
                D["e_cell_h0_null_W"] = dict(d)
                D["e_cell_h0_null_W"]["identified_by"] = (
                    "the V arms at h = 0, where every designed count is zero in both: a per-op energy "
                    "difference here is the two SHAPES' intercept difference (alpha + 0.125 addr "
                    "bits/op), which each arm's free intercept removes from e_cell -- under A2 this is "
                    "reported, and it is no longer the §9 'h = 0 shows a non-zero difference' arm, "
                    "which was written for the cross-mode paired estimator")
                D["e_cell_h0_null_W"]["a2_demoted"] = True
    # RECON 8: §9's CONFIRMED arm for e_cell asks the difference to SCALE with h ("and scales with h
    # (the h = 16 rung)").  The wf3 build asserted it from the fact that a slope was fitted over two
    # rungs at all, which is not a test.  Here the rate-free per-cell-bit step at h = 16 is tested
    # AGAINST the one at h = 32, pass by pass: proportionality in h means the per-BIT price is the
    # same at both rungs (ratio 1) and the per-OP step doubles (growth 2.0).
    if F.get("V_pairs"):
        rungs = {}
        for hk, d_ in F["V_pairs"].items():
            hv = d_.get("h")
            if not hv or not d_.get("_cell_step_pp") or not d_.get("cell_bits_per_op"):
                continue
            rungs[hv] = (d_["_cell_step_pp"], float(d_["cell_bits_per_op"]))
        hh = sorted(rungs)
        if len(hh) >= 2:
            lo_h, hi_h = hh[0], hh[-1]
            lo_pp, lo_bits = rungs[lo_h]
            hi_pp, hi_bits = rungs[hi_h]
            per_bit_lo = dict((p, v / lo_bits * 1e15) for p, v in lo_pp.items())
            per_bit_hi = dict((p, v / hi_bits * 1e15) for p, v in hi_pp.items())
            need = hi_bits / lo_bits if lo_bits else None
            s_lo = with_t(stat(sorted(per_bit_lo.items())))
            s_hi = with_t(stat(sorted(per_bit_hi.items())))
            # RECON 8: the TEST is the PAIRED DIFFERENCE of the two rungs' per-bit prices against
            # zero.  A mean of per-pass RATIOS is not usable here: the denominator is one pass's own
            # h = 16 step, a sub-watt difference of two cross-mode items that can come out near zero,
            # so the ratio's between-pass scatter is dominated by those passes and the statistic reads
            # 0.43 +- 0.51 where the ratio of the MEANS is 0.84.  The ratio of means and the per-op
            # growth are reported with delta-method SEs beside the difference.
            diff_pb = pp_combine(per_bit_hi, per_bit_lo, lambda a, b: a - b)
            s_di = with_t(stat(sorted(diff_pb.items())))

            def _ratio_of_means(num, den):
                a_, sa_ = num.get("value"), num.get("se")
                b_, sb_ = den.get("value"), den.get("se")
                if a_ is None or b_ is None or not b_:
                    return {"value": None, "se": None}
                r_ = a_ / b_
                se_ = (abs(r_) * math.sqrt((sa_ / a_) ** 2 + (sb_ / b_) ** 2)
                       if (sa_ and sb_ and a_) else None)
                return {"value": r_, "se": se_,
                        "how": "ratio of the two means, SE by the delta method (the per-pass ratio is "
                               "unstable: its denominator can approach zero)"}

            s_ra = _ratio_of_means(s_hi, s_lo)
            s_op_lo = with_t(stat(sorted(dict((p, v * 1e15) for p, v in lo_pp.items()).items())))
            s_op_hi = with_t(stat(sorted(dict((p, v * 1e15) for p, v in hi_pp.items()).items())))
            s_gr = _ratio_of_means(s_op_hi, s_op_lo)
            prop = None
            if s_di.get("value") is not None and s_di.get("se") and s_di.get("df"):
                prop = bool(abs(s_di["value"]) / s_di["se"] < (t_crit(THREE_SIGMA_P, s_di["df"]) or 9e9))
            F["e_cell_scaling_test"] = {
                "rung_low_h": lo_h, "rung_high_h": hi_h,
                "fJ_per_cell_bit_at_low_h": s_lo, "fJ_per_cell_bit_at_high_h": s_hi,
                "per_bit_difference_high_minus_low": s_di,        # the test
                "per_bit_ratio_high_over_low": s_ra,
                "fJ_per_op_at_low_h": s_op_lo, "fJ_per_op_at_high_h": s_op_hi,
                "per_op_growth_high_over_low": s_gr,
                "per_op_growth_a_proportional_law_needs": need,
                "proportional_within_3SE": prop,
                "test": "the paired per-pass difference of the two rungs' per-cell-bit prices against "
                        "zero, at the 3-SE-equivalent quantile",
                "per_bit_change_pct": ((s_ra["value"] - 1.0) * 100.0
                                       if s_ra.get("value") is not None else None),
                "how": "each arm's own h-step in J per op at its OWN rate, differenced (rate-free), "
                       "divided by that rung's cell bits per op, then h = %g against h = %g pass by "
                       "pass. A proportional law needs the per-bit DIFFERENCE = 0 (equivalently the "
                       "ratio = 1) and the per-op growth = %s." % (hi_h, lo_h, fmt(need, 2)),
                "note": "RECON 8: this is the TEST §9 registers, not the fact that a two-rung slope "
                        "could be fitted. A per-bit price that falls with h means the cell term is "
                        "not proportional to the designed cell count, and the CONFIRMED arm's second "
                        "condition is NOT met."}
    if not pairs and "e_cell" not in D:
        missing.append("%s: family V absent -- e_cell is NOT IDENTIFIED" % label)
    elif pairs and "e_cell" not in D:
        # §6 runs family V on aifoundry1 card 0 as the h = 32 PAIR ALONE, with no h = 0 rung, and
        # registers the 0.2% pair gate as its only rate gate.  A2 replaces that gate with each mode's
        # own within-mode one and makes the cell price a difference of per-flip SLOPES -- which needs
        # each arm's own zero rung.  Without one the A2 estimator does not exist on this card; the
        # rate-free per-rung step is the only reading left, and it is a bound, not e_cell.
        have_arms = sorted(arm_rungs)
        bound = None
        for hk, d_ in sorted((F.get("V_pairs") or {}).items()):
            if d_.get("fJ_per_cell_bit_this_rung") is not None:
                bound = (hk, d_["fJ_per_cell_bit_this_rung"])
        D["e_cell_not_identified"] = {
            "unit": "J/flip", "family": "V", "value": None, "se": None, "not_identified": True,
            "identified_by": "family V (A2.3) needs each arm's OWN zero rung",
            "arms_with_a_zero_rung": have_arms,
            "rate_free_per_rung_bound_fJ_per_cell_bit": (bound[1] if bound else None),
            "rate_free_per_rung_bound_at": (bound[0] if bound else None),
            "note": "family V ran here as the h = 32 pair alone (§6), with no h = 0 rung for either "
                    "arm, so A2.3's slope difference cannot be formed and e_cell is NOT IDENTIFIED on "
                    "this card. The cross-mode watt difference is rate-confounded (0.7574 vs 0.7356 "
                    "ops per cycle per hart); the rate-free per-rung step above is a BOUND. The "
                    "decision rests on the pinned card, where §6 registers it anyway."}
        missing.append("%s: family V ran as the h = 32 pair alone with no h = 0 rung for either arm, "
                       "so A2.3's per-flip slope difference cannot be formed and e_cell is NOT "
                       "IDENTIFIED here (arms with a zero rung: %s). The cross-mode d1b - d1a watt "
                       "difference is rate-confounded and is reported as a bound only; the decision "
                       "rests on aifoundry3, where §6 registers it." % (label, have_arms or "none"))

    # ---------------------------------------------------------------- family B: the 2x2 bridge
    cells = ("d2A", "d2B", "d2C", "d2D")
    per_cell_h = {}
    for c in cells:
        per_cell_h[c] = set(float(h) for h, n in hs(c + "_"))
    bh = []
    if all(per_cell_h[c] for c in cells):
        common = set(per_cell_h[cells[0]])
        for c in cells[1:]:
            common &= per_cell_h[c]
        bh = sorted(h for h in common if h)      # the nonzero rungs all four cells share
    if bh:
        def cellname(c, h):
            return "%s_h%g" % (c, h)

        def z4(c):
            return man.zero_of(cellname(c, bh[0])) or ("%s_h0" % c)

        rr, rr_old = [], []
        for h in bh:
            terms = []
            for c, sgn in (("d2B", +1), ("d2D", +1), ("d2A", -1), ("d2C", -1)):
                terms += [(sgn, cellname(c, h)), (-sgn, z4(c))]
            # RECON 1: the denominator is PER MODE.  The (B-A) half is 8h result bits/op at d2B's
            # mode (300, fand), the (D-C) half 8h at d2D's mode (301, for), and mode 301 issues
            # 4.71-4.73% faster, so one rate for both legs overstates e_out by +2.36%.
            rr.append((h, None, terms, [(8.0 * h, cellname("d2B", h)), (8.0 * h, cellname("d2D", h))]))
            rr_old.append((h, 16.0 * h, terms, cellname("d2B", h)))
        sl, inter = slope_over(rr)
        sl_old, _ = slope_over(rr_old)
        D["e_out_bridge"] = pp_stat(sl, family="B", unit="J/flip", v_rail=v_rail,
                                   rail_map=slope_over_rail(rr),
                                   identified_by="family B, the 2x2: [(B+D)-(A+C)] / (8h r300 + 8h r301), "
                                                 "%d rungs (RECON 1: each leg at its OWN mode's rate)" % len(rr),
                                   notes=["alpha(opcode) cancels; carries the +16w term under §5.1 "
                                          "reading R2 only",
                                          "RECON 1: the rate denominator is per mode (A2.1). The old "
                                          "single-rate form, 16h x rate(d2B), reads 2.36% higher and "
                                          "is printed as e_out_bridge_one_rate_superseded",
                                          "E60's interval is [%.2f, %.2f] fJ; the page says %.2f fJ"
                                          % (E60["e_out_interval_fJ"][0], E60["e_out_interval_fJ"][1],
                                             PAGE["e_out_fJ"])])
        D["e_out_bridge"]["E60_interval_fJ"] = list(E60["e_out_interval_fJ"])
        D["e_out_bridge"]["page_fJ"] = PAGE["e_out_fJ"]
        # RECON 1: the superseded single-rate form, kept so the 2.36% is visible, never scored
        if sl_old:
            D["e_out_bridge_one_rate_superseded"] = pp_stat(
                sl_old, family="B", unit="J/flip", v_rail=v_rail,
                identified_by="SUPERSEDED (RECON 1): [(B+D)-(A+C)] / 16h x rate(d2B), one mode's rate "
                              "for both legs -- reported only so the size of the error is visible",
                notes=["mode 301 (the D-C leg) issues 4.71-4.73% faster than mode 300, so this form "
                       "reads +2.36% high; A2.1 requires a per-mode denominator"])
            _a, _b = D["e_out_bridge"].get("fJ"), D["e_out_bridge_one_rate_superseded"].get("fJ")
            D["e_out_bridge"]["one_rate_form_fJ"] = _b
            D["e_out_bridge"]["one_rate_form_excess_pct"] = \
                (100.0 * (_b - _a) / _a) if (_a and _b is not None) else None
        D["e_out_bridge"]["n_rungs"] = len(rr)
        D["e_out_bridge"]["h_rungs"] = list(bh)
        D["e_out_bridge"]["intercept_removed"] = bool(len(rr) >= 2)
        if len(rr) < 2:
            # §5.1: with one nonzero rung the fit goes through the zero, so the free intercept that
            # absorbs the +16 changed-words/op term is gone and this value carries it under reading
            # R2 (+0.273 W on a 5.678 W quantity = 4.8%, 3-11 SE).  e_out is then quoted from the
            # §8.5 joint fit, which carries changed words as its own regressor.
            D["e_out_bridge"]["carries_changed_word_term"] = True
            D["e_out_bridge"]["notes"] = list(D["e_out_bridge"].get("notes") or []) + [
                "ONE nonzero rung (%s): the slope goes through its zero, so the changed-word term is "
                "NOT removed and this raw combination is biased under §5.1 reading R2. Quote the "
                "§8.5 joint-fit e_out instead." % bh]
            missing.append("%s: family B's 2x2 has one nonzero rung (%s), so the raw bridge does not "
                           "remove the §5.1 changed-word term; e_out is quoted from the joint fit "
                           "alone" % (label, bh))
        hmax = max(bh)
        # the R2 correction, printed beside the raw combination (§5.1)
        bridge_raw = contrast([t for c, s in (("d2B", 1), ("d2D", 1), ("d2A", -1), ("d2C", -1))
                               for t in ((s, cellname(c, hmax)), (-s, z4(c)))],
                              family="B", unit="W",
                              identified_by="(B+D)-(A+C) at h=%g, raw watts" % hmax)
        dw = sum(man.changed_words(cellname(c, hmax)) * s - man.changed_words(z4(c)) * s
                 for c, s in (("d2B", 1), ("d2D", 1), ("d2A", -1), ("d2C", -1)))
        F["B_bridge_raw_W"] = bridge_raw
        F["B_bridge_R2_changed_words_per_op"] = dw
        # VER 3: the bridge's OWN per-second denominator (RECON 1: per mode), so a watt difference on
        # this combination can be stated in fJ per flip and the other way round.
        _den = []
        for p in passes:
            x_ = xval(p, None, [(8.0 * hmax, cellname("d2B", hmax)),
                                (8.0 * hmax, cellname("d2D", hmax))])
            if x_:
                _den.append(x_)
        F["B_bridge_denominator_bits_per_s"] = (float(np.mean(_den)) if _den else None)
        F["B_bridge_denominator_how"] = (
            "%g x rate(%s) + %g x rate(%s) -- RECON 1, each leg at its own mode's rate"
            % (8.0 * hmax, cellname("d2B", hmax), 8.0 * hmax, cellname("d2D", hmax)))
        if D.get("intercept_N_W", {}).get("value") is not None and items.get(cellname("d2B", hmax), {}).get("rate"):
            # VER 1: the price is the intercept per R2 changed word (16 words/op on the N rung), not
            # per source word (8).  The bridge changes dw = 16 words/op, so the correction is the
            # intercept itself -- §5.1's own statement, "the bridge is biased by exactly +0.273 W,
            # and only under reading R2".  At intercept/8 it read twice that.
            per_word, wn_ref = word_price_W("R2")
            F["B_bridge_R2_price_per_changed_word_W"] = per_word
            F["B_bridge_R2_price_read_on"] = (
                "the N ladder's fitted intercept / %g changed 32-bit words per op (reading R2: 8 "
                "source + 8 result on every nonzero d1nz rung). §5.1 prices ONE word at 48 fJ and "
                "lets the reading set the count, which is why its R1 and R2 rows are +0.137 W and "
                "+0.273 W, not +0.137 W and +0.546 W (VER 1)" % wn_ref)
            F["B_bridge_R2_correction_W"] = dw * per_word
            F["B_bridge_R2_corrected_W"] = (bridge_raw["value"] - dw * per_word) \
                if bridge_raw["value"] is not None else None
        # (B-A) - (D-C) = 2 g_op + g_res  (NOT "2 x the zero-operand effect")
        g = contrast([(1, cellname("d2B", hmax)), (-1, z4("d2B")), (-1, cellname("d2A", hmax)), (1, z4("d2A")),
                      (-1, cellname("d2D", hmax)), (1, z4("d2D")), (1, cellname("d2C", hmax)), (-1, z4("d2C"))],
                     family="B", unit="W",
                     identified_by="(B-A)-(D-C) at h=%g = 2 g_op + g_res (§4)" % hmax)
        rate = items[cellname("d2B", hmax)].get("rate")
        g["fJ_per_op"] = (g["value"] / rate * 1e15) if (g["value"] is not None and rate) else None
        D["zero_word_bridge_2gop_gres"] = g
        # the within-opcode decompositions
        for nm, c, bits_c, note in (("e_in_fand_d2A", "d2A", 8.0, "d2A's result is static 0: a pure read-port price"),
                                    ("e_in_for_d2C", "d2C", 8.0, "d2C's result is static all-ones: a pure read-port price")):
            n = cellname(c, hmax)
            D[nm] = per_bit(n, z4(c), bits_c * hmax, family="B",
                            identified_by="%s - %s, / %g bits" % (n, z4(c), bits_c * hmax),
                            notes=[note])
        # RECON 11: C14/C64 is decided at the resolution limit against the 26.0 fJ edge of E60's fand
        # interval, so EVERY rung and EVERY defensible fit form of d2A is reported, not just the h32
        # delta/8h the row quotes.  A per-bit price that moves between rungs is itself the finding.
        d2a_rungs, d2a_pp = {}, {}
        for hh in bh:
            nm_ = cellname("d2A", hh)
            d_ = per_bit(nm_, z4("d2A"), 8.0 * hh, family="B",
                         identified_by="%s - %s, / %g bits (one rung, through its zero)"
                                       % (nm_, z4("d2A"), 8.0 * hh),
                         notes=["RECON 11: one of the rungs C14/C64 can be read on"])
            d2a_rungs["h%g" % hh] = d_
            d2a_pp[hh] = pp_of(d_)
        F["e_in_fand_d2A_by_rung"] = d2a_rungs
        rr_a = [(nm, 8.0 * hh, [(1, cellname("d2A", hh)), (-1, z4("d2A"))], cellname("d2A", hh))
                for hh, nm in [(h_, cellname("d2A", h_)) for h_ in bh]]
        if len(rr_a) >= 2:
            sl_a, int_a = slope_over(rr_a)
            D["e_in_fand_d2A_free_intercept"] = pp_stat(
                sl_a, family="B", unit="J/flip", v_rail=v_rail, rail_map=slope_over_rail(rr_a),
                identified_by="RECON 11: d2A's %d-rung slope with a FREE INTERCEPT (the plan's §8.4 "
                              "fit form), h = %s" % (len(rr_a), ", ".join(fmt(x, 0) for x in bh)),
                notes=["a different estimator from delta/8h at one rung: this one lets the shape's "
                       "own offset out of the slope"])
        # E60's own ec form: the (0, 0) point included with a free intercept
        zp = {}
        for p in passes:
            xs, ys = [0.0], [0.0]
            for hh in bh:
                y = combo(val, p, [(1, cellname("d2A", hh)), (-1, z4("d2A"))], "p80")
                x = xval(p, 8.0 * hh, cellname("d2A", hh))
                if y is None or x is None:
                    continue
                xs.append(x)
                ys.append(y)
            if len(xs) >= 3:
                f_ = fit_line(xs, ys)
                if f_:
                    zp[p] = f_[1]
        if zp:
            D["e_in_fand_d2A_with_origin"] = pp_stat(
                zp, family="B", unit="J/flip", v_rail=v_rail,
                identified_by="RECON 11: d2A with (0,0) ADDED as a data point and a FREE intercept "
                              "(the form `ladder()` calls E60's ec fit)",
                notes=["at 1:2 rung spacing (8h bits at h = 16 and 32, one rate) the three points "
                       "(0,0), (x, y16), (2x, y32) are equally spaced, and a free-intercept least "
                       "squares through equally spaced x returns exactly (y32 - y0)/(x32 - x0) -- the "
                       "endpoint slope. So this form AGREES with the one-rung delta/8h by algebra, "
                       "not by measurement, and it is the no-intercept fit below that differs"])
        # the other with-origin reading: least squares FORCED THROUGH the origin, no intercept at all
        # (sum x y / sum x^2).  This is a genuinely different estimator from the one above and is the
        # one that weights the h = 16 rung, so it is the one that shows the rungs disagreeing.
        zo = {}
        for p in passes:
            sxy = sxx = 0.0
            m_ = 0
            for hh in bh:
                y = combo(val, p, [(1, cellname("d2A", hh)), (-1, z4("d2A"))], "p80")
                x = xval(p, 8.0 * hh, cellname("d2A", hh))
                if y is None or x is None:
                    continue
                sxy += x * y
                sxx += x * x
                m_ += 1
            if m_ >= 2 and sxx:
                zo[p] = sxy / sxx
        if zo:
            D["e_in_fand_d2A_through_origin"] = pp_stat(
                zo, family="B", unit="J/flip", v_rail=v_rail,
                identified_by="RECON 11: d2A by least squares FORCED THROUGH THE ORIGIN over h = %s "
                              "(no intercept: sum(xy)/sum(x^2))"
                              % ", ".join(fmt(x, 0) for x in bh),
                notes=["a third defensible form, and the one that actually weights both rungs; it "
                       "differs from the endpoint slope exactly because the per-bit price is not "
                       "constant in h"])
        for nm, hi, lo, note in (("e_out_fand_BA", "d2B", "d2A",
                                  "both fand.pi: the opcode and alpha cancel, but this diagonal "
                                  "CARRIES the changed-result-word term (+8 words/op under §5.1 "
                                  "reading R2) -- e_out is quoted from the 2x2, where it cancels"),
                                 ("e_out_for_DC", "d2D", "d2C",
                                  "both for.pi: same caveat as e_out_fand_BA")):
            D[nm] = contrast([(1, cellname(hi, hmax)), (-1, z4(hi)), (-1, cellname(lo, hmax)), (1, z4(lo))],
                             [(1, 8.0 * hmax, cellname(hi, hmax))], unit="J/flip", family="B",
                             identified_by="(%s - %s) at h=%g / %g bits" % (hi, lo, hmax, 8 * hmax),
                             notes=[note])
        # §10 tier 1: the result-path load, whole card and per half-die
        half = contrast([(1, cellname("d2B", hmax)), (-1, z4("d2B")), (-1, cellname("d2A", hmax)), (1, z4("d2A")),
                         (1, cellname("d2D", hmax)), (-1, z4("d2D")), (-1, cellname("d2C", hmax)), (1, z4("d2C"))],
                        family="B", unit="W", scale=0.5,
                        identified_by="1/2[(B-A)+(D-C)] at h=%g = 8h e_out, whole card (§10 tier 1)" % hmax)
        D["result_path_load_W"] = half
        D["half_die_result_path_load_W"] = dict(half)
        for k in ("value", "se", "se_robust", "rail_value", "rail_se"):
            if D["half_die_result_path_load_W"].get(k) is not None:
                D["half_die_result_path_load_W"][k] = D["half_die_result_path_load_W"][k] / 2.0
        D["half_die_result_path_load_W"]["identified_by"] = "half of the whole-card result-path load"
        D["half_die_result_path_load_W"]["target_W"] = [1.33, 1.42]
        D["half_die_result_path_load_W"]["page_W"] = PAGE["half_die_W"]
        # the h = 0 intercepts: alpha(opcode) per cell (the OPEN arm of C56...)
        F["B_h0_intercepts_W"] = {}
        for i, a in enumerate(cells):
            for b in cells[i + 1:]:
                za, zb = z4(a), z4(b)
                if za in items and zb in items:
                    F["B_h0_intercepts_W"]["%s-%s" % (a, b)] = contrast(
                        [(1, za), (-1, zb)], family="B", unit="W",
                        identified_by="%s - %s, nothing flipping in either" % (za, zb))
    else:
        missing.append("%s: family B's 2x2 is incomplete -- e_out from the bridge is NOT IDENTIFIED" % label)

    # ---------------------------------------------------------------- family gate: the three-opcode ladder
    # XCHK 3: §4 registers the gate contrast at IDENTICAL designed counts, so it is read at the one h the
    # three opcodes share (h = 32 in every registered list).  Taking every nonzero rung put d2D_h16 beside
    # d2D_h32 in the same min-to-max spread, where the extremes can be a within-opcode step at another h
    # rather than the gate contrast, and gave the depth ranking two entries at rank 1.
    gate_cand = []
    for n in sorted(items):
        if man.family(n) == "gate" or n.startswith(("d2X_", "d3z_", "d2D_")):
            h = man.get(n).get("h")
            if h:
                gate_cand.append((float(h), n))
    by_op = defaultdict(set)
    for h, n in gate_cand:
        by_op[opcode_of(items[n].get("op"))].add(h)
    shared = set.intersection(*by_op.values()) if by_op else set()
    gate_h = max(shared) if shared else (max(h for h, _ in gate_cand) if gate_cand else None)
    gate_items = sorted(n for h, n in gate_cand if gate_h is not None and h == gate_h)
    if gate_cand and not shared:
        C.setdefault("warnings", []).append(
            "gate ladder: the three opcodes share no h rung (%s), so the spread is read at h = %s and is "
            "NOT a matched-count contrast"
            % (dict((k, sorted(v)) for k, v in by_op.items()), fmt(gate_h, 0)))
    if gate_items:
        F["gate_ladder"] = {}
        for n in gate_items:
            z = man.zero_of(n)
            if z not in items:
                continue
            bits = man.designed_flips(n) - man.designed_flips(z)
            d = per_bit(n, z, bits, family="gate",
                        identified_by="%s - %s / %g port+result bits" % (n, z, bits),
                        notes=["x2 below is e_in + e_out for this opcode at matched counts"])
            d["op"] = items[n].get("op")
            d["gate_depth_rank"] = GATE_DEPTH.get(opcode_of(items[n].get("op")))   # XCHK 1
            d["e_sum_fJ"] = None if d.get("fJ") is None else 2 * d["fJ"]
            d["e_sum_se_fJ"] = None if d.get("se_fJ") is None else 2 * d["se_fJ"]
            F["gate_ladder"][n] = d
        vals = [(v["op"], v["e_sum_fJ"], v["e_sum_se_fJ"], n) for n, v in F["gate_ladder"].items()
                if v.get("e_sum_fJ") is not None]
        if len(vals) >= 2:
            lo = min(vals, key=lambda x: x[1])
            hi = max(vals, key=lambda x: x[1])
            se = math.sqrt((lo[2] or 0) ** 2 + (hi[2] or 0) ** 2) or None
            dof = min([F["gate_ladder"][n].get("df") or 1 for _, _, _, n in vals])
            F["gate_spread"] = {
                "min": {"op": lo[0], "item": lo[3], "e_sum_fJ": lo[1]},
                "max": {"op": hi[0], "item": hi[3], "e_sum_fJ": hi[1]},
                "spread_fJ": hi[1] - lo[1], "se_fJ": se,
                "t": ((hi[1] - lo[1]) / se) if se else None,
                "t_crit_3sigma": t_crit(THREE_SIGMA_P, dof) if dof else None,
                "monotone_in_depth": None}
            ranked = sorted([(F["gate_ladder"][n].get("gate_depth_rank"), v)
                             for _, v, _, n in vals if F["gate_ladder"][n].get("gate_depth_rank")])
            if len(ranked) >= 3:
                F["gate_spread"]["monotone_in_depth"] = all(ranked[i][1] <= ranked[i + 1][1]
                                                            for i in range(len(ranked) - 1))
            F["gate_spread"]["by_depth"] = ranked
            # RECON 14: the order with the OPCODE named, and the pass count the spread itself rests
            # on (the smaller of the two legs'), so the row can say both.
            F["gate_spread"]["by_depth_named"] = sorted(
                [(F["gate_ladder"][n_].get("gate_depth_rank"), v_, op_)
                 for op_, v_, _, n_ in vals if F["gate_ladder"][n_].get("gate_depth_rank")])
            F["gate_spread"]["by_value_named"] = [
                (op_, v_) for op_, v_, _, n_ in sorted(vals, key=lambda x: x[1])]
            F["gate_spread"]["n_passes"] = min(
                [F["gate_ladder"][n_].get("n_passes") or 0 for _, _, _, n_ in vals]) or None
            F["gate_spread"]["df"] = dof
            F["gate_spread"]["h"] = gate_h                      # XCHK 3
            F["gate_spread"]["matched_counts"] = bool(shared)
            # VER 12 (the fix verifier's MINOR): the SE above is CROSS-ITEM -- sqrt(se_lo^2 + se_hi^2)
            # over two items' own between-pass SEs -- which treats the two legs as independent
            # samples.  §8.4 makes the (card, pass) the unit of replication, so the registered
            # statistic is the between-pass scatter of the SPREAD itself, pass by pass.  Both are
            # reported; the paired one is the §8.4 reading.
            _pp = {}
            for _, _, _, n_ in vals:
                m_ = pp_of(F["gate_ladder"][n_])
                if m_:
                    _pp[n_] = dict((p_, 2.0 * v_ * 1e15) for p_, v_ in m_.items())   # e_sum, fJ
            _common = None
            for m_ in _pp.values():
                _common = set(m_) if _common is None else (_common & set(m_))
            _common = sorted(_common or [])
            F["gate_spread"]["cross_item_se_fJ"] = se
            F["gate_spread"]["cross_item_t"] = F["gate_spread"]["t"]
            F["gate_spread"]["se_basis"] = (
                "VER 12: `spread_fJ` / `se_fJ` / `t` above are the CROSS-ITEM reading "
                "(sqrt(se_min^2 + se_max^2)); `paired_*` below is §8.4's own unit of replication, the "
                "between-pass scatter of the per-pass spread. The paired one is the statistic §8.4 "
                "registers, and the row reads it.")
            if len(_common) >= 2 and len(_pp) >= 2:
                _fix_hi, _fix_lo = hi[3], lo[3]
                _pair = dict((p_, _pp[_fix_hi][p_] - _pp[_fix_lo][p_]) for p_ in _common)
                _pstat = with_t(stat(sorted(_pair.items())))
                _maxmin = dict((p_, max(m_[p_] for m_ in _pp.values())
                                - min(m_[p_] for m_ in _pp.values())) for p_ in _common)
                _mstat = with_t(stat(sorted(_maxmin.items())))
                F["gate_spread"]["paired_fixed_pair"] = {
                    "items": [_fix_hi, _fix_lo], "ops": [hi[0], lo[0]],
                    "spread_fJ": _pstat.get("value"), "se_fJ": _pstat.get("se"),
                    "se_robust_fJ": _pstat.get("se_robust"),
                    "t": _pstat.get("t"), "df": _pstat.get("df"),
                    "t_crit_3sigma": _pstat.get("t_crit_3sigma"),
                    "ge_3SE": _pstat.get("abs_t_ge_3sigma"),
                    "n_passes": _pstat.get("n_passes"),
                    "how": "the SAME two opcodes differenced inside each pass, then the mean and the "
                           "SE from the between-pass scatter (§8.4)"}
                F["gate_spread"]["paired_per_pass_max_minus_min"] = {
                    "spread_fJ": _mstat.get("value"), "se_fJ": _mstat.get("se"),
                    "se_robust_fJ": _mstat.get("se_robust"),
                    "t": _mstat.get("t"), "df": _mstat.get("df"),
                    "t_crit_3sigma": _mstat.get("t_crit_3sigma"),
                    "ge_3SE": _mstat.get("abs_t_ge_3sigma"),
                    "n_passes": _mstat.get("n_passes"),
                    "how": "max - min over the three opcodes INSIDE each pass (the extreme pair may "
                           "differ between passes), then the between-pass scatter"}
                F["gate_spread"]["paired_se_fJ"] = _pstat.get("se")
                F["gate_spread"]["paired_t"] = _pstat.get("t")
        # the fnot leg, stated as one-port/one-gate vs two-port/one-gate
        if D.get("e_sum_fnot_d1nz", {}).get("fJ") is not None:
            F["fnot_leg"] = {
                "e_sum_fnot_fJ": D["e_sum_fnot_d1nz"]["fJ"], "se_fJ": D["e_sum_fnot_d1nz"].get("se_fJ"),
                "E60_e_in_plus_e_out_fJ": E60["e_in_fxor_fJ"] + E60["e_out_interval_fJ"][1],
                "E60_interval_fJ": list(E60["e_sum_fnot_interval_fJ"]),
                "reading": "one-port/one-gate (fnot.pi) against two-port/one-gate (fxor.pi); a "
                           "d1nz value ABOVE xnz means a second read port is cheap per bit"}

    # ---------------------------------------------------------------- family C: the carry ladder
    kc, Lc = find_ladder("C", zero="d3_L0")
    if Lc:
        sl_pp = pp_of(Lc["slope"])
        D["e_out_add_plus_e_carry"] = dict(Lc["slope"])
        D["e_out_add_plus_e_carry"]["family"] = "C"
        D["e_out_add_plus_e_carry"]["identified_by"] = \
            "family C, d3 against carry nodes/s (result and carry move together: slope = e_out(add) + e_carry)"
        # RECON 4: the REGISTERED estimator.  §4 family C: "e_carry exists only as slope/8 -
        # e_out(add), with e_out(add) from `d3z` -- the same opcode, the same shape, the same pass --
        # NEVER imported from fand/for."  So e_out(add) is built here from d3z's own per-flip slope
        # (port+result bits, which is e_in + e_out for the add shape) minus e_in read off the SAME c2
        # shape's d2A (static result, so a pure read-port price).  The two older routes -- importing
        # family B's e_out, and subtracting e_in(fxor) from the rot2 X family -- are kept beside it
        # as alternatives and never enter the decision.
        eo_add_reg = {}
        if "d3z_h32" in items and D.get("e_in_fand_d2A", {}).get("value") is not None:
            z = man.zero_of("d3z_h32")
            if z in items:
                s_d3z = per_bit("d3z_h32", z, man.designed_flips("d3z_h32") - man.designed_flips(z))
                pp_d3z = pp_of(s_d3z)
                ein_fand = pp_of(D["e_in_fand_d2A"])
                F["d3z_half_sum_per_portresult_bit"] = s_d3z
                if pp_d3z and ein_fand:
                    eo_add_reg = pp_combine(pp_d3z, ein_fand, lambda a, b: 2 * a - b)
                    F["e_out_add_registered"] = pp_stat(
                        eo_add_reg, family="C", unit="J/flip", v_rail=v_rail,
                        rail_map=pp_combine(pp_of(s_d3z, "rail"), pp_of(D["e_in_fand_d2A"], "rail"),
                                            lambda a, b: 2 * a - b),
                        identified_by="RECON 4, the REGISTERED e_out(add): 2 x d3z's per-(port+result)-bit "
                                      "slope - e_in from the SAME c2 shape's d2A, pass by pass",
                        notes=["§4 family C registers this and forbids importing e_out from fand/for",
                               "d3z is fadd.pi on the c2 shape: its per-flip slope over port+result "
                               "bits is (e_in + e_out)/2 for the ADD opcode, so twice it minus "
                               "e_in(fand) from d2A is e_out(add) with alpha and the shape's own "
                               "offset removed by each leg's own zero rung"])
        eo_B = pp_of(D.get("e_out_bridge", {}))
        if eo_add_reg and sl_pp:
            D["e_carry"] = pp_stat(pp_combine(sl_pp, eo_add_reg, lambda a, b: a - b),
                                   family="C", unit="J/flip", v_rail=v_rail,
                                   rail_map=pp_combine(pp_of(Lc["slope"], "rail"),
                                                       pp_of(F.get("e_out_add_registered", {}), "rail"),
                                                       lambda a, b: a - b),
                                   identified_by="family C only, and only given e_out(add): the d3 slope "
                                                 "per carry node - the REGISTERED e_out(add) from d3z "
                                                 "(RECON 4), pass by pass",
                                   notes=["energy per bit position of carry propagation "
                                          "(RIPPLE-EQUIVALENT): on a parallel-prefix adder the "
                                          "toggling-node count for a carry over L positions is not L (§4)",
                                          "RECON 4: e_out(add) comes from d3z -- the same opcode, the "
                                          "same shape, the same pass -- and is NOT imported from "
                                          "fand/for, which §4 forbids. The imported-from-B route is "
                                          "printed as e_carry_alt_from_B."])
        elif eo_B and sl_pp:
            D["e_carry"] = pp_stat(pp_combine(sl_pp, eo_B, lambda a, b: a - b),
                                   family="C", unit="J/flip", v_rail=v_rail,
                                   rail_map=pp_combine(pp_of(Lc["slope"], "rail"),
                                                       pp_of(D.get("e_out_bridge", {}), "rail"),
                                                       lambda a, b: a - b),
                                   identified_by="FALLBACK: d3 slope - e_out from family B's 2x2 (the "
                                                 "registered d3z route needs d3z and d2A in the same pass)",
                                   notes=["RECON 4: this is NOT the registered estimator. §4 asks for "
                                          "e_out(add) from d3z; d3z or d2A is missing on this unit, so "
                                          "the family-B import is used and said out loud."])
        # RECON 4, the part the synthetic campaign exposed: the registered d3z leg is a ONE-RUNG
        # slope through its own zero (§6 gives the gate family h = 0 and h = 32 only), and d3z_h0 has
        # NO changed result word while d3z_h32 has 8 -- so the leg carries the §5.1 changed-word term
        # under reading R2, exactly as XCHK 7 says of a one-rung bridge.  With 48 fJ per changed word
        # planted, the synthetic registered route returns e_carry = 1.70 - 2 x 8 x 48 / 512 = 0.20 fJ,
        # which is what it does return (0.262 +- 0.111).  The correction is computed here from the
        # measured N intercept and printed beside the primary; the primary stays the registered form.
        if eo_add_reg and "d3z_h32" in items:
            z3 = man.zero_of("d3z_h32")
            dw3 = (man.changed_words("d3z_h32", "R2") - man.changed_words(z3, "R2")) if z3 else 0.0
            bits3 = man.designed_flips("d3z_h32") - (man.designed_flips(z3) if z3 else 0.0)
            ipp = pp_of(D.get("intercept_N_W", {}))
            # VER 1: dw3 is an R2 count (16 words/op), so the price must be the intercept per R2
            # changed word -- intercept/16, not intercept/8.  At intercept/8 this term read 5.013
            # fJ/flip instead of 2.507 and flipped C54's corrected reading from CONFIRMED-ours to
            # REFUTED-both on nothing but the mismatched reading.
            _, wn_ = word_price_W("R2")
            corr = {}
            if dw3 and bits3 and ipp:
                for p in passes:
                    rN = val.get(p, {}).get("d1nz_h32", {}).get("rate") or \
                         val.get(p, {}).get("d1nz_h0", {}).get("rate")
                    r3 = val.get(p, {}).get("d3z_h32", {}).get("rate")
                    if p not in ipp or not rN or not r3:
                        continue
                    # J per changed word, from the N ladder's own intercept at its own rate
                    per_word_J = ipp[p] / (rN * wn_)
                    corr[p] = 2.0 * dw3 * per_word_J / bits3
            F["e_out_add_registered_R2_term"] = {
                "changed_words_per_op_delta": dw3, "regressor_bits_per_op": bits3,
                "fJ_per_flip": (float(np.mean(list(corr.values()))) * 1e15) if corr else None,
                "n_passes": len(corr),
                "words_per_op_the_price_is_read_on": wn_,
                "W_per_changed_word": (word_price_W("R2")[0]),
                "note": "RECON 4 / §5.1 reading R2: d3z_h0 changes %g 32-bit word(s) per op and "
                        "d3z_h32 changes %g, so the one-rung slope through the zero does NOT remove "
                        "the changed-word term and e_out(add) carries +2 x %g words / %g bits of it. "
                        "Priced at the N ladder's own fitted intercept divided by %g changed words "
                        "per op -- VER 1: the COUNT and the PRICE are read on the SAME §5.1 reading "
                        "(R2 counts 8 source + 8 result = 16 words on every nonzero d1nz rung; "
                        "intercept/8 would be R1's price against R2's count and doubles the term)."
                        % (man.changed_words(z3, "R2") if z3 else 0.0,
                           man.changed_words("d3z_h32", "R2"), dw3, bits3, wn_)}
            if corr:
                F["e_out_add_registered_R2_corrected"] = pp_stat(
                    pp_combine(eo_add_reg, corr, lambda a, b: a - b),
                    family="C", unit="J/flip", v_rail=v_rail,
                    identified_by="the registered e_out(add) with the §5.1 R2 changed-word term "
                                  "removed at the N ladder's measured intercept (RECON 4)")
                D["e_carry_R2_corrected"] = pp_stat(
                    pp_combine(sl_pp, pp_combine(eo_add_reg, corr, lambda a, b: a - b),
                               lambda a, b: a - b),
                    family="C", unit="J/flip", v_rail=v_rail,
                    identified_by="e_carry with the §5.1 R2 changed-word term removed from the d3z "
                                  "leg (RECON 4); the PRIMARY above is the registered form, uncorrected",
                    notes=["the C ladder itself carries no changed-word term (d3_L and d3_L0 change "
                           "the same 8 source and 8 result words), so the whole correction sits on "
                           "the d3z leg"])
                D["e_carry"]["notes"] = list(D["e_carry"].get("notes") or []) + [
                    "RECON 4 / §5.1: the d3z leg is ONE rung through its own zero and that zero has "
                    "%g fewer changed result word(s) per op, so this value carries the changed-word "
                    "term under reading R2 (+%s fJ/flip at the measured intercept). The corrected "
                    "value is D['e_carry_R2_corrected']; both are reported and the verdict is stated "
                    "for both." % (dw3, fmt((F.get("e_out_add_registered_R2_term") or {})
                                            .get("fJ_per_flip"), 2))]
                D["e_carry"]["carries_changed_word_term"] = True
        if D.get("e_carry"):
            D["e_carry"]["page_fJ"] = PAGE["e_carry_fJ"]
            D["e_carry"]["ours_fJ"] = 1.7
            D["e_carry"]["prior_fJ"] = list(PRIOR["e_carry_fJ"])
            D["e_carry"]["e_out_add_route"] = ("registered (d3z - e_in from d2A)" if eo_add_reg
                                               else "fallback (family B 2x2)")
            if (not eo_add_reg) and D.get("e_out_bridge", {}).get("carries_changed_word_term"):   # XCHK 7
                D["e_carry"]["notes"].append(
                    "the imported e_out came from a ONE-RUNG bridge, so it carries the §5.1 changed-word "
                    "term and that bias propagates straight into e_carry")
                D["e_carry"]["carries_changed_word_term"] = True
        elif sl_pp:
            missing.append("%s: e_out(add) unavailable (neither d3z+d2A nor family B's 2x2) -- "
                           "e_carry is NOT IDENTIFIED" % label)
        # the alternatives, printed and never scored (RECON 4)
        if eo_B and sl_pp:
            D["e_carry_alt_from_B"] = pp_stat(
                pp_combine(sl_pp, eo_B, lambda a, b: a - b), family="C", unit="J/flip", v_rail=v_rail,
                identified_by="ALTERNATIVE (RECON 4): d3 slope - e_out from family B's 2x2, which §4 "
                              "forbids as the estimator (a different opcode and shape)",
                notes=["printed so the route the wf3 build used stays visible; the registered route is "
                       "D['e_carry']"])
        if "d3z_h32" in items and D.get("e_in_fxor", {}).get("value") is not None:
            z = man.zero_of("d3z_h32")
            if z in items:
                s = per_bit("d3z_h32", z, man.designed_flips("d3z_h32") - man.designed_flips(z))
                pp = pp_of(s)
                ein = pp_of(D["e_in_fxor"])
                F["e_out_add_from_d3z_minus_ein_fxor"] = pp_stat(
                    pp_combine(pp, ein, lambda a, b: 2 * a - b),
                    family="gate", unit="J/flip", v_rail=v_rail,
                    identified_by="ALTERNATIVE: 2 x d3z half-sum - e_in(fxor) from the rot2 X family",
                    notes=["RECON 4: this subtracts e_in from a DIFFERENT shape and opcode, so it "
                           "carries alpha(fxor) - alpha(fadd) and the shapes' offset difference; "
                           "reported, never used in the e_carry decision"])
        # §4 / §9: the L vs L log2 L curvature as the adder-topology test
        rows = []
        for Lv, n in hs("d3_L"):
            if n in items and items[n].get("d_p80") is not None and Lv:
                rows.append((Lv, items[n]["d_p80"], items[n].get("d_p80_se")))
        if len(rows) >= 3:
            Ls = np.array([r[0] for r in rows], float)
            ys = np.array([r[1] for r in rows], float)
            fits = {}
            for nm, xcol in (("linear_L", Ls), ("sublinear_L_log2L", Ls * np.log2(np.maximum(Ls, 1.0)))):
                X = np.vstack([np.ones_like(xcol), xcol]).T
                c, *_ = np.linalg.lstsq(X, ys, rcond=None)
                fits[nm] = {"intercept_W": float(c[0]), "slope": float(c[1]),
                            "resid_rms_W": float(np.sqrt(np.mean((ys - X @ c) ** 2)))}
            X = np.vstack([np.ones_like(Ls), Ls, Ls * np.log2(np.maximum(Ls, 1.0))]).T
            c, *_ = np.linalg.lstsq(X, ys, rcond=None)
            fits["both"] = {"coef": [float(x) for x in c],
                            "resid_rms_W": float(np.sqrt(np.mean((ys - X @ c) ** 2)))}
            F["C_curvature"] = {"rungs_L": [r[0] for r in rows], "dW": [r[1] for r in rows],
                                "fits": fits,
                                "preferred": min(("linear_L", "sublinear_L_log2L"),
                                                 key=lambda k: fits[k]["resid_rms_W"])}
        # RECON 7 (built here because family A reads it): the plausible size of the per-op constant
        # that three SEPARATELY EMITTED kernels can differ by, which no single free intercept in a
        # cross-mode ladder removes.  Measured from the ABSOLUTE board power of the zero rungs -- the
        # items whose every designed count is zero -- grouped by the mode's issue rate, so a
        # same-rate pair differs only in which kernel was emitted.  Converted to the A ladder's own
        # units with §9 rule 3's factor (1 fJ per address bit = 0.00356 W).
        zrows = []
        for nm_ in sorted(items):
            if man.designed_flips(nm_) or (items[nm_].get("p80") is None):
                continue
            if man.family(nm_) == "anchor":
                continue
            zrows.append({"item": nm_, "mode": str(man.mode_key(nm_)),
                          "op": (man.get(nm_) or {}).get("op"),
                          "ipc": items[nm_].get("ipc"), "p80_W": items[nm_].get("p80"),
                          "p80_se_W": items[nm_].get("p80_se")})
        if len(zrows) >= 2:
            byipc = defaultdict(list)
            for r_ in zrows:
                if r_["ipc"] is not None:
                    byipc[round(r_["ipc"], 3)].append(r_)
            # the A ladder's own zero rung names the rate the comparison has to be made AT, and the
            # A rungs themselves are excluded from the spread -- using them would be circular, since
            # the ladder IS their difference.  So the headline is the spread among the zero rungs of
            # OTHER families at that same issue rate: items that flip nothing, issue at the same
            # rate, and differ only in which kernel the build emitted.
            a_zero = None
            for nm_ in sorted(items):
                if man.family(nm_) == "A" and not man.designed_flips(nm_):
                    a_zero = nm_
                    break
            a_ipc = round(items.get(a_zero, {}).get("ipc") or 0, 3) if a_zero else None
            samerate = []
            for k_, rs_ in sorted(byipc.items()):
                ps = [x["p80_W"] for x in rs_ if x["p80_W"] is not None]
                oth = [x for x in rs_ if x["p80_W"] is not None and man.family(x["item"]) != "A"]
                po = [x["p80_W"] for x in oth]
                if len(ps) < 2:
                    continue
                samerate.append({
                    "ipc": k_, "items": [x["item"] for x in rs_],
                    "modes": sorted({x["mode"] for x in rs_}),
                    "W_min": min(ps), "W_max": max(ps), "spread_W": max(ps) - min(ps),
                    "spread_fJ_per_addr_bit_equiv": (max(ps) - min(ps)) / 0.00356,
                    "items_outside_family_A": [x["item"] for x in oth],
                    "spread_W_outside_family_A": (max(po) - min(po)) if len(po) >= 2 else None,
                    "spread_fJ_per_addr_bit_equiv_outside_family_A":
                        ((max(po) - min(po)) / 0.00356) if len(po) >= 2 else None,
                    "is_the_A_ladder_rate": bool(a_ipc is not None and k_ == a_ipc)})
            head = next((g for g in samerate if g.get("is_the_A_ladder_rate")
                         and g.get("spread_W_outside_family_A") is not None), None)
            F["per_op_constant_between_kernels"] = {
                "zero_rungs": zrows, "same_rate_groups": samerate,
                "family_A_zero_rung": a_zero, "family_A_ladder_ipc": a_ipc,
                "headline_group": (head or {}).get("items_outside_family_A"),
                "largest_same_rate_spread_W": (head or {}).get("spread_W_outside_family_A"),
                "largest_same_rate_spread_fJ_per_addr_bit_equiv":
                    (head or {}).get("spread_fJ_per_addr_bit_equiv_outside_family_A"),
                "widest_group_any_rate_W": max([g["spread_W"] for g in samerate]) if samerate else None,
                "headline_basis": "the spread among the zero rungs of OTHER families at the A "
                                  "ladder's own issue rate (%s, from %s). Family A's own rungs are "
                                  "excluded: the ladder is their difference, so including them would "
                                  "be circular. The widest group at any rate is printed too, but it "
                                  "mixes kernel bodies (fmadd against fxor) and is not the "
                                  "comparison."
                                  % (a_ipc, a_zero),
                "conversion": "§9 rule 3: 1 fJ per address bit = 0.00356 W over the A ladder "
                              "(delta 1.75 -> 11.75)",
                "note": "RECON 7: two zero rungs at the SAME issue rate flip nothing, so their board "
                        "powers differ only by the per-op constant of two separately emitted kernels. "
                        "That spread, read in the A ladder's own units, is the size of the term "
                        "family A's cross-mode slope cannot separate from e_addr -- and it is large "
                        "enough to account for the whole measured slope."}
        if "d3p_L29" in items and "d3_L29" in items:
            d = contrast([(1, "d3p_L29"), (-1, "d3_L29")], family="C", unit="W",
                         identified_by="d3p_L29 - d3_L29: the page-exact design's zero operand (replication)")
            rate = items["d3p_L29"].get("rate")
            d["fJ_per_op"] = (d["value"] / rate * 1e15) if (d["value"] is not None and rate) else None
            F["zero_word_replication_fadd"] = d
    else:
        missing.append("%s: family C absent -- e_carry is NOT IDENTIFIED" % label)

    # ---------------------------------------------------------------- family M: the Miller set
    mnames = [n for n in sorted(items) if man.family(n) == "M" or n.startswith("m_")]
    if mnames:
        ref = "xin_h16" if "xin_h16" in items else man.zero_of(mnames[0])
        F["M_reference"] = ref
        F["M_items"] = {}
        for n in mnames:
            k, src = man.k_adj(n)
            if src == "plan-fallback":
                C.setdefault("warnings", []).append(
                    "k_adj for %s taken from the plan's §4 table (the manifest carries none)" % n)
            d = contrast([(1, n), (-1, ref)], family="M", unit="W",
                         identified_by="%s - %s (matched designed counts)" % (n, ref)) \
                if ref in items else {}
            if d:
                d["k_adj"] = k
                d["k_adj_source"] = src
                d["zero_word"] = man.get(n).get("zero_word")
                rate = items[n].get("rate")
                d["fJ_per_op"] = (d["value"] / rate * 1e15) if (d["value"] is not None and rate) else None
            F["M_items"][n] = d
        if "m_pair" in items and "m_nib" in items:
            D["phase_term"] = contrast([(1, "m_pair"), (-1, "m_nib")], family="M", unit="W",
                                       identified_by="m_pair - m_nib at matched occupancy and counts "
                                                     "(registered target 0 W; the page says +%.3f W)"
                                                     % PAGE["miller_dW"])
            D["phase_term"]["page_W"] = PAGE["miller_dW"]
        if "m_nib" in items and "m_nib_c" in items:
            F["M_complement_control"] = contrast(
                [(1, "m_nib"), (-1, "m_nib_c")], family="M", unit="W",
                identified_by="m_nib - m_nib_c, an exact bitwise-complement pair at one k_adj level "
                              "(a capacitive effect is complement-symmetric)")
        # Spearman rho over the distinct k_adj levels, the complement pair averaged
        lev = defaultdict(list)
        for nm_, d in F["M_items"].items():
            if d and d.get("k_adj") is not None and d.get("value") is not None \
                    and not man.get(nm_).get("zero_word"):
                lev[round(d["k_adj"], 4)].append((nm_, pp_of(d)))
        if len(lev) >= 3:
            ks = sorted(lev)
            # one value per (level, pass): the complement pair at a level is averaged, as §9 asks
            lev_pp = {}
            for k_ in ks:
                common = None
                for _, m_ in lev[k_]:
                    common = set(m_) if common is None else (common & set(m_))
                lev_pp[k_] = dict((p, float(np.mean([m_[p] for _, m_ in lev[k_]])))
                                  for p in sorted(common or []))
            ys = [float(np.mean(list(lev_pp[k_].values()))) if lev_pp[k_] else None for k_ in ks]
            steps = []
            for i in range(len(ks) - 1):
                st = with_t(stat(sorted(pp_combine(lev_pp[ks[i + 1]], lev_pp[ks[i]],
                                                   lambda a, b: a - b).items())))
                steps.append({"from": ks[i], "to": ks[i + 1], "dW": st["value"], "se": st["se"],
                              "t": st["t"], "df": st["df"], "t_crit_3sigma": st["t_crit_3sigma"],
                              "ge_3SE": ge_zero(abs(st["value"] or 0.0), st["se"], st["df"]),
                              "n_passes": st["n_passes"]})
            sp = with_t(stat(sorted(pp_combine(lev_pp[ks[-1]], lev_pp[ks[0]],
                                               lambda a, b: a - b).items())))
            # RECON 12: the sign matters more than the magnitude here, so the per-PASS Spearman is
            # computed too: rho over the four levels within each pass, then the mean and its SE.
            # A pass-averaged rho of -1 could be one outlier; a per-pass mean of -0.57 +- 0.23 is not.
            common_p = None
            for k_ in ks:
                common_p = set(lev_pp[k_]) if common_p is None else (common_p & set(lev_pp[k_]))
            rhos = []
            for p_ in sorted(common_p or []):
                r_ = spearman(ks, [lev_pp[k_][p_] for k_ in ks])
                if r_ is not None:
                    rhos.append(r_)
            rho_pp = with_t(stat(sorted(zip(sorted(common_p or []), rhos)))) if rhos else None
            F["M_levels"] = {"k_adj": ks, "dW": ys, "n_levels": len(ks),
                             "spearman_rho": spearman(ks, [y for y in ys if y is not None])
                             if all(y is not None for y in ys) else None,
                             "spearman_rho_per_pass": rho_pp,          # RECON 12
                             "monotone_wrong_direction": (
                                 bool(spearman(ks, [y for y in ys if y is not None]) is not None
                                      and spearman(ks, [y for y in ys if y is not None]) <= -0.9)
                                 if all(y is not None for y in ys) else None),
                             "steps": steps,
                             "whole_spread": {"dW": sp["value"], "se": sp["se"], "t": sp["t"],
                                              "df": sp["df"], "t_crit_3sigma": sp["t_crit_3sigma"],
                                              "ge_3SE": ge_zero(abs(sp["value"] or 0.0), sp["se"],
                                                                sp["df"]),
                                              "n_passes": sp["n_passes"]},
                             "items_per_level": dict((k_, [nm_ for nm_, _ in lev[k_]]) for k_ in ks),
                             "zero_word_items_excluded": [nm_ for nm_ in F["M_items"]
                                                          if man.get(nm_).get("zero_word")]}
        if "m_solid_z" in items and "m_phase0" in items:
            d = contrast([(1, "m_solid_z"), (-1, "m_phase0")], family="M", unit="W",
                         identified_by="m_solid_z - m_phase0: the page-exact zero-word item against a "
                                       "zero-free item at matched counts (replication; confounded by "
                                       "construction either way)")
            rate = items["m_solid_z"].get("rate")
            d["fJ_per_op"] = (d["value"] / rate * 1e15) if (d["value"] is not None and rate) else None
            F["zero_word_replication_miller"] = d
    else:
        missing.append("%s: family M absent -- the phase term is NOT IDENTIFIED" % label)

    # ---------------------------------------------------------------- family A: the address ladder
    for tag, pre in (("gated", "d5_a"), ("live", "d5n_a")):
        rungs = [(dv, n) for dv, n in hs(pre)]
        z = None
        for dv, n in rungs:
            zz = man.zero_of(n)
            if zz in items:
                z = zz
                break
        # A2.4: the registered ladder is the rungs that share one rate (a0, a1, a3).  a5 (mode 309) is
        # excluded by name and reported beside it, exactly as amendment A3 excludes an item.
        nz_all = [n for dv, n in rungs if n != z and (man.c(n, "addr") - man.c(z, "addr") if z else 0)]
        nz = [n for n in nz_all if not man.rate_confounded(n)]
        rc = [n for n in nz_all if man.rate_confounded(n)]
        if z and nz:
            rr = [(n, man.c(n, "addr") - man.c(z, "addr"), [(1, n), (-1, z)], n) for n in nz]
            sl = slope_over(rr)[0]
            d = pp_stat(sl, family="A", unit="J/flip", v_rail=v_rail, rail_map=slope_over_rail(rr),
                        identified_by="family A only, the %s regime: the A2 ladder %s against address "
                                      "bits/s, zero %s" % (tag, nz, z),
                        notes=["the common 1.75 destination-cycle bits cancel in the delta",
                               "the family's resolution is ~20 fJ/bit against a 0-2 fJ prior: this is a "
                               "one-sided exclusion of the page's %g fJ x 3 ports, not a measurement (§9)"
                               % PAGE["e_addr_fJ"],
                               "A2.4: a0/a1/a3 are three modes that share one rate to 1e-4, which is "
                               "why the amendment registers them as one ladder%s"
                               % (("; %s is excluded as rate-confounded and reported beside it" % rc)
                                  if rc else "")])
            d["page_fJ"] = PAGE["e_addr_fJ"]
            d["prior_fJ"] = list(PRIOR["e_addr_fJ"])
            d["rungs"] = list(nz)
            d["rate_confounded_excluded"] = list(rc)
            d["modes"] = sorted({str(man.mode_key(n)) for n in nz} | {str(man.mode_key(z))})
            D["e_addr" if tag == "gated" else "e_addr_live"] = d
        for n in rc:
            bits = man.c(n, "addr") - man.c(z, "addr")
            e = per_bit(n, z, bits, family="A",
                        identified_by="%s - %s / %g address bits (RATE-CONFOUNDED, outside the A2 "
                                      "ladder)" % (n, z, bits),
                        notes=["A2.4: mode %s retires at another rate (0.6088 against the ladder's "
                               "0.5814 ops per cycle per hart, 4.7%% apart by code), so this rung "
                               "carries the rate step as well as the address bits and is REPORTED "
                               "BESIDE the ladder, never inside the slope" % man.mode_key(n)])
            e["rate_confounded"] = True
            e["delta"] = man.get(n).get("delta")
            F.setdefault("A_rate_confounded_beside_the_ladder", {})[n] = e
    if "e_addr" in D and "e_addr_live" in D:
        a, b = pp_of(D["e_addr"]), pp_of(D["e_addr_live"])
        F["A_gated_minus_live_slope"] = pp_stat(pp_combine(a, b, lambda x, y: x - y), family="A",
                                                unit="J/flip", v_rail=v_rail,
                                                identified_by="gated slope - live slope: a difference "
                                                              ">= 3 SE means data-path gating reaches the "
                                                              "address path and the zero-data ladder is a "
                                                              "LOWER bound (§9)")
    for dv in (0.0, 3.0):
        a, b = "d5_a%g" % dv, "d5n_a%g" % dv
        if a in items and b in items:
            F.setdefault("A_gated_minus_live_levels_W", {})["delta%g" % dv] = contrast(
                [(1, a), (-1, b)], family="A", unit="W",
                identified_by="%s - %s at matched register-index distance" % (a, b))
    if "e_addr" not in D:
        missing.append("%s: family A absent -- e_addr is NOT IDENTIFIED, the page's 32 fJ x 3 ports "
                       "stands unscored" % label)

    # ---------------------------------------------------------------- family Z: the zero gate
    if "d6_one" in items and "d6_zero" in items:
        d = contrast([(1, "d6_one"), (-1, "d6_zero")], family="Z", unit="W",
                     identified_by="d6_one - d6_zero (mode 191, every designed count zero in both)")
        rate = items["d6_one"].get("rate")
        d["pJ_per_op"] = (d["value"] / rate * 1e12) if (d["value"] is not None and rate) else None
        d["se_pJ_per_op"] = (d["se"] / rate * 1e12) if (d["se"] is not None and rate) else None
        d["page_pJ_per_op"] = PAGE["zero_gate_pJ_per_op"]
        d["ours_pJ_per_op"] = 0.147
        D["zero_gate_step"] = d
    else:
        missing.append("%s: family Z absent -- the zero-gate step is not evaluated on silicon "
                       "(S3's desk refutation stands alone)" % label)

    # ---------------------------------------------------------------- family R: reconciliation
    def perop(hi, lo):
        """(P(hi) - P(lo)) / ops per second -> J per op, pass by pass (rate-free by construction)."""
        out = {}
        for p in passes:
            y = combo(val, p, [(1, hi), (-1, lo)], "p80")
            r1 = val.get(p, {}).get(hi, {}).get("rate")
            r2 = val.get(p, {}).get(lo, {}).get("rate")
            if y is None or not r1 or not r2:
                continue
            out[p] = y / (0.5 * (r1 + r2))
        return out

    if have("r_and_r1", "r_and_c1") and have("r_and_r2", "r_and_c2"):
        d1 = perop("r_and_r1", "r_and_c1")
        d2 = perop("r_and_r2", "r_and_c2")
        D["rho_harts2_over_harts1"] = pp_stat(pp_combine(d2, d1, lambda a, b: a / b if b else float("nan")),
                                              family="R", unit="ratio",
                                              identified_by="family R: (harts-2 per-op delta)/(harts-1 "
                                                            "per-op delta) for fand.pi, random - const",
                                              notes=["1.000 if operand sharing survives interleaving; "
                                                     "1.12-1.14 if interleaving destroys it (§5.3)"])
        F["R_perop_fand_J"] = {"harts1": with_t(stat(sorted(d1.items()))),
                               "harts2": with_t(stat(sorted(d2.items())))}
    if have("r_not_r1", "r_not_c1"):
        dn = perop("r_not_r1", "r_not_c1")
        F["R_perop_fnot_J"] = with_t(stat(sorted(dn.items())))
        iN = pp_of(D.get("intercept_N_W", {}))
        rate = items["r_not_r1"].get("rate")
        if iN and rate:
            # N's intercept is a watt figure at the N shape's own rate; take it to fJ/op pass by pass
            iN_perop = {}
            for p, w in iN.items():
                rt = val.get(p, {}).get("d1nz_h32", {}).get("rate") or rate
                iN_perop[p] = w / rt
            net = pp_combine(dn, iN_perop, lambda a, b: (a - b) / 95.556)
            D["e_sum_fnot_from_R"] = pp_stat(net, family="R", unit="J/flip", v_rail=v_rail,
                                             identified_by="(r_not_r1 - r_not_c1) per op, minus family N's "
                                                           "measured intercept, / 95.556 (§5.3)",
                                             notes=["target [%.2f, %.2f] fJ; unsubtracted the same delta "
                                                    "reads 60.03 fJ under R2 and 56.01 under R1"
                                                    % E60["e_sum_fnot_interval_fJ"]])
            D["e_sum_fnot_from_R"]["E60_interval_fJ"] = list(E60["e_sum_fnot_interval_fJ"])
            D["e_sum_fnot_from_R"]["unsubtracted_fJ"] = (
                (float(np.mean(list(dn.values()))) / 95.556) * 1e15) if dn else None
    if have("r_not_r1", "r_not_c1") and not pp_of(D.get("intercept_N_W", {})):
        missing.append("%s: family R's fnot leg ran but family N's d1nz ladder did not, so the "
                       "intercept cannot be subtracted on the same card; unsubtracted the delta "
                       "reads ~60 fJ under R2 and would spuriously refute the operand law (§5.3)"
                       % label)
    if not any(k in items for k in ("r_and_r1", "r_not_r1")):
        missing.append("%s: family R absent -- rho and the model-free fnot leg are not evaluated" % label)

    # ---------------------------------------------------------------- family 7: the spatial halves
    ph_rows = dict((nm_, {"peak_spread_c": items[nm_].get("peak_spread_c"),
                          "se": items[nm_].get("peak_spread_c_se"),
                          "family": items[nm_].get("family")})
                   for nm_ in sorted(items)
                   if items[nm_].get("peak_spread_c") is not None
                   and (items[nm_].get("family") == "7" or nm_ in ("d2B_h32", "d2D_h32", "xin_h32")))
    if ph_rows:
        F["peak_hold_spread_c"] = {
            "rows": ph_rows,
            "note": "§10's one on-die check: temp_c.minshire's peak-hold (high - low) should WIDEN "
                    "when 512 minions run loud and 512 idle, against a whole-card loud run. "
                    "Resolution is whole degrees, and the whole-card reference (d2B_h32 / xin_h32) "
                    "lives in the electrical unit, not the dtf-cam one, so this is read across "
                    "units and is EXPLORATORY."}
    if have("d7w_hi", "d7e_hi"):
        D["dipole_W_vs_E_board_W"] = contrast(
            [(1, "d7w_hi"), (-1, "d7e_hi")], family="7", unit="W",
            identified_by="d7w_hi - d7e_hi, board power (§10 tier 1: the real content of dP_card == 0)")
        for side in ("w", "e"):
            hi, lo = "d7%s_hi" % side, "d7%s_lo" % side
            if have(hi, lo):
                F.setdefault("dipole_side_amplitude_W", {})[side] = contrast(
                    [(1, hi), (-1, lo)], family="7", unit="W",
                    identified_by="%s - %s at the same shire mask" % (hi, lo),
                    notes=["the lo arm holds a zero word (plan §4) and the hi arm does not, so this "
                           "amplitude CONTAINS the zero-word step; tier 1's own statistic is the "
                           "W-vs-E equality of the two hi arms, where it cancels"])
    if not electrical:
        C["absent_by_design_notes"] = list(missing)
    return D, F


# =================================================================================================
# §8.5 the joint fit (descriptive)
# =================================================================================================
JOINT_FAMILIES = ("X", "N", "V", "B", "gate", "C", "A")
JOINT_COEFS = ["e_in", "e_out", "e_cell", "e_carry", "e_addr", "w"]
IDENTIFIED_BY = {"e_in": "X (and ain); collinear with e_out inside N and V",
                 "e_out": "B's 2x2 (one contrast)",
                 "e_cell": "V only (one contrast)",
                 "e_carry": "C only, and only given e_out(add) (one contrast)",
                 "e_addr": "A only (one contrast)",
                 "w": "N's and X's intercepts"}
SINGLE_CONTRAST = {"e_out", "e_cell", "e_carry", "e_addr"}


def identifiable_coefs(man, items):
    """§8.5: which coefficients the item set on this card can actually separate.  A coefficient
    whose identifying contrast is absent is reported as NOT IDENTIFIED, never as a fitted zero --
    without this, a least squares over family N alone (where the port and result counts are equal
    at every h, so e_in and e_out are perfectly collinear) hands back an arbitrary split of the two
    and a verdict would be read off it.

    The test is structural: a coefficient is identified when two items of the same family and the
    same opcode differ in ITS count and in no other priced count.  Address bits are ignored except
    for e_addr itself (family V's two arms differ by 0.125 address bits per op, 0.05% of the
    signal, which the plan registers and the manifest carries).
    """
    ok = dict((k, False) for k in JOINT_COEFS)
    pairs = dict((k, None) for k in JOINT_COEFS)
    names = sorted(items)
    for i, a in enumerate(names):
        ia = man.get(a)
        for b in names[i + 1:]:
            ib = man.get(b)
            # XCHK 2: the same family and the same OPCODE, not the same pattern name.
            if ia.get("family") != ib.get("family") \
                    or opcode_of(ia.get("op")) != opcode_of(ib.get("op")):
                continue
            d = {}
            for k in ("vs1", "vs2", "result", "cell", "carry", "addr", "src_words", "res_words"):
                d[k] = man.c(a, k) - man.c(b, k)
            port = d["vs1"] + d["vs2"]
            if port and not d["result"] and not d["cell"] and not d["carry"]:
                ok["e_in"], pairs["e_in"] = True, pairs["e_in"] or [a, b]
            if d["result"] and not port and not d["cell"] and not d["carry"]:
                ok["e_out"], pairs["e_out"] = True, pairs["e_out"] or [a, b]
            if d["cell"] and not port and not d["result"] and not d["carry"]:
                ok["e_cell"], pairs["e_cell"] = True, pairs["e_cell"] or [a, b]
            if d["carry"] and not port and not d["cell"]:
                pairs["e_carry"] = pairs["e_carry"] or [a, b]
            if d["addr"] and not port and not d["result"] and not d["cell"] and not d["carry"]:
                ok["e_addr"], pairs["e_addr"] = True, pairs["e_addr"] or [a, b]
            if (d["src_words"] or d["res_words"]) and not port and not d["result"] \
                    and not d["cell"] and not d["carry"]:
                ok["w"], pairs["w"] = True, pairs["w"] or [a, b]
    # §4: e_carry exists only as (the C slope) - e_out(add), so it needs e_out as well
    ok["e_carry"] = bool(pairs["e_carry"]) and ok["e_out"]
    # w is also identified by the ladder intercepts (X 16 changed words/op against N's 8)
    if not ok["w"]:
        wc = set()
        for nm in items:
            if man.family(nm) in ("X", "N") and man.zero_of(nm):
                wc.add(man.changed_words(nm, "R1"))
        ok["w"] = len(wc) >= 2
    return ok, pairs


def joint_fit(man, val, passes, items, v_rail, reading="R2"):
    def row(n, z, rate):
        dv = lambda k: man.c(n, k) - man.c(z, k)
        return [(dv("vs1") + dv("vs2")) * rate, dv("result") * rate, dv("cell") * rate,
                dv("carry") * rate, dv("addr") * rate,
                (man.changed_words(n, reading) - man.changed_words(z, reading)) * rate]

    names = [n for n in sorted(items)
             if man.family(n) in JOINT_FAMILIES and man.zero_of(n) and man.zero_of(n) != n]
    ident, ident_pairs = identifiable_coefs(man, items)
    pooled_X, pooled_y, per_pass = [], [], []
    for p in passes:
        X, y = [], []
        for n in names:
            z = man.zero_of(n)
            vp, vz = val.get(p, {}).get(n, {}), val.get(p, {}).get(z, {})
            if vp.get("p80") is None or vz.get("p80") is None or not vp.get("rate"):
                continue
            X.append(row(n, z, vp["rate"]) + [1.0])
            y.append(vp["p80"] - vz["p80"])
        if len(y) > len(JOINT_COEFS) + 1:
            A, b = np.asarray(X, float), np.asarray(y, float)
            keep = [j for j in range(A.shape[1]) if np.ptp(A[:, j]) > 0 or j == A.shape[1] - 1]
            c, *_ = np.linalg.lstsq(A[:, keep], b, rcond=None)
            full = {}
            for i, j in enumerate(keep):
                full[(JOINT_COEFS + ["intercept_W"])[j]] = float(c[i])
            full["_resid_rms_W"] = float(np.sqrt(np.mean((b - A[:, keep] @ c) ** 2)))
            full["_n_rows"] = len(y)
            per_pass.append((p, full))
            pooled_X += X
            pooled_y += y
    if not per_pass:
        return {"note": "too few item rows for the joint fit", "n_passes": 0}
    out = {"reading_for_w": reading, "n_passes": len(per_pass),
           "rows_per_pass": int(np.median([f["_n_rows"] for _, f in per_pass])),
           "items": names, "identified_by": IDENTIFIED_BY, "coefs": {},
           "identifiable": ident, "identifying_pair": ident_pairs}
    for name in JOINT_COEFS + ["intercept_W"]:
        ser = [(p, f[name]) for p, f in per_pass if name in f]
        s = with_t(stat(ser))
        if name == "intercept_W":
            out["coefs"][name] = s
            continue
        if not ident.get(name):
            # §8.5: never a fitted zero, and never a number read off a collinear design
            out["coefs"][name] = {"value": None, "fJ": None, "se": None, "se_fJ": None,
                                  "not_identified": True, "se_quoted": False,
                                  "identified_by": IDENTIFIED_BY.get(name),
                                  "note": "NOT IDENTIFIED on this card: no pair of items differs in "
                                          "this count alone, so the least squares value (%s fJ) is "
                                          "an artefact of the collinearity and is withheld"
                                          % fmt((s.get("value") or 0) * 1e15, 2),
                                  "withheld_lstsq_fJ": (s.get("value") or 0) * 1e15,
                                  "n_passes": s.get("n_passes"), "passes": s.get("passes")}
            continue
        if s.get("value") is None:
            # the structural test said the pair exists, but every per-pass design matrix dropped this
            # column: the identifying pair's rungs are not BOTH in the fit (on aifoundry1 c0 family V
            # ran as the h = 32 pair with no zero rung, so no row carries a cell count).  Never n/a.
            out["coefs"][name] = {
                "value": None, "fJ": None, "se": None, "se_fJ": None, "not_identified": True,
                "se_quoted": False, "identified_by": IDENTIFIED_BY.get(name),
                "note": "NOT IN THE DESIGN on this card: the identifying pair exists in the manifest "
                        "(%s) but no fitted row carries this count -- its rungs have no zero rung "
                        "inside the kept set -- so the column was dropped from every per-pass fit"
                        % (ident_pairs.get(name) or "-"),
                "n_passes": 0, "passes": []}
            continue
        s.update(units(s["value"], v_rail))
        s["fJ"] = None if s["value"] is None else s["value"] * 1e15
        s["se_fJ"] = None if s["se"] is None else s["se"] * 1e15
        s["identified_by"] = IDENTIFIED_BY.get(name)
        if name in SINGLE_CONTRAST and name != "e_out":
            s["se_quoted"] = False
            s["se_note"] = "identified by one contrast: §8.5 forbids quoting a joint-fit SE here; " \
                           "use the family estimate"
        else:
            s["se_quoted"] = True
        out["coefs"][name] = s
    if pooled_X:
        A = np.asarray(pooled_X, float)
        out["resid_rms_W"] = float(np.mean([f["_resid_rms_W"] for _, f in per_pass]))
        try:
            out["condition_number_raw_design"] = float(np.linalg.cond(A))
        except Exception:
            out["condition_number_raw_design"] = None
        # RECON 3: the condition number that means anything here is the one on a COLUMN-SCALED design
        # restricted to the columns actually present.  The raw design's count columns are ~1e13-1e14
        # per second beside an intercept of 1.0, so np.linalg.cond on it reports 1e15-1e16 on a design
        # whose VIFs are 0.9-2.1 -- a units artefact, not collinearity.  And a column of all zeros (a
        # family absent on this card, e.g. A on aifoundry1 c0, which every per-pass fit already drops)
        # sends the raw number to 1e33; it is dropped here too, by name.
        colnames = JOINT_COEFS + ["intercept_W"]
        present, absent = [], []
        for j, nm_ in enumerate(colnames):
            if float(np.max(np.abs(A[:, j]))) > 0:
                present.append(j)
            else:
                absent.append(nm_)
        if present:
            As = A[:, present].astype(float)
            norms = np.sqrt((As ** 2).sum(axis=0))
            norms[norms == 0] = 1.0
            try:
                out["condition_number"] = float(np.linalg.cond(As / norms))
            except Exception:
                out["condition_number"] = None
        else:
            out["condition_number"] = None
        out["condition_number_basis"] = (
            "column-scaled (each column divided by its 2-norm) over the %d columns present of %d; "
            "columns all zero on this card are dropped: %s. The raw-design number is kept beside it "
            "and is a units artefact (counts per second against an intercept of 1.0)."
            % (len(present), len(colnames), ", ".join(absent) or "none"))
        out["columns_absent_from_the_design"] = absent
        vif = {}
        for j, name in enumerate(JOINT_COEFS):
            if np.ptp(A[:, j]) == 0:
                vif[name] = None
                continue
            others = [k for k in range(A.shape[1]) if k != j]
            B = A[:, others]
            c, *_ = np.linalg.lstsq(B, A[:, j], rcond=None)
            resid = A[:, j] - B @ c
            ss = float(np.sum((A[:, j] - A[:, j].mean()) ** 2))
            r2 = 1.0 - float(np.sum(resid ** 2)) / ss if ss else None
            vif[name] = (1.0 / (1.0 - r2)) if (r2 is not None and r2 < 1 - 1e-12) else None
        out["vif"] = vif
    # §8.5 asks for the condition number; a degenerate one is said out loud, because every
    # coefficient in such a fit is a ratio of two nearly-equal numbers.
    # RECON 3: the degeneracy flag is read off the SCALED condition number (and a scaled design is
    # ill-conditioned above ~1e8, not 1e12, since the scaling removes the units).  The flag no longer
    # fires on a design whose only problem was that its columns are counts per second.
    cn = out.get("condition_number")
    cn_raw = out.get("condition_number_raw_design")
    out["design_is_degenerate"] = bool(cn is None or not np.isfinite(cn) or cn > 1e8)
    if out["design_is_degenerate"]:
        out["degenerate_note"] = (
            "the pooled design's COLUMN-SCALED condition number is %s over %s rows per pass and %d "
            "coefficients + an intercept: the design is RANK-DEFICIENT or near it, so every "
            "coefficient here is descriptive only (§8.5) and no §9 decision may rest on this card's "
            "joint fit (raw-design number, a units artefact: %s)"
            % (fmt(cn, 3) if cn is not None and np.isfinite(cn) else "non-finite",
               out.get("rows_per_pass"), len(JOINT_COEFS),
               fmt(cn_raw, 3) if cn_raw is not None and np.isfinite(cn_raw) else "non-finite"))
    else:
        out["well_conditioned_note"] = (
            "RECON 3: the column-scaled condition number is %s over %s rows per pass (raw design %s, a "
            "units artefact of counts-per-second columns beside an intercept of 1.0), and the VIFs "
            "below are the collinearity statement that matters"
            % (fmt(cn, 3), out.get("rows_per_pass"),
               fmt(cn_raw, 3) if cn_raw is not None and np.isfinite(cn_raw) else "non-finite"))
    out["known_collinearities"] = [
        "N and V have equal port and result counts at every h: e_in and e_out are perfectly "
        "collinear WITHIN them",
        "C's carry and result counts differ by a constant 8, so they are collinear once a free "
        "intercept is present",
    ]
    return out


# =================================================================================================
# §8.7 across cards, §9.2 Holm
# =================================================================================================
def across_cards(cards):
    ref = cards.get("aifoundry3")
    out = {}
    for card, C in cards.items():
        e = {"clock_mhz": C.get("clock_mhz"), "v_mean": C.get("v_mean"),
             "E60_per_bit_tie": E60["per_bit_tie"].get(card), "E60_v2_tie": E60["v2_tie"].get(card)}
        if ref and ref.get("v_mean") and C.get("v_mean"):
            e["v2_ratio_measured"] = (C["v_mean"] / ref["v_mean"]) ** 2
        for key in ("e_in_fxor", "e_out_bridge", "e_sum_fnot_d1nz"):
            a = (C.get("derived") or {}).get(key, {})
            b = (ref.get("derived") or {}).get(key, {}) if ref else {}
            e[key + "_fJ"] = a.get("fJ")
            e[key + "_rail_fJ"] = a.get("rail_fJ")
            if a.get("fJ") and b.get("fJ"):
                e[key + "_ratio_to_a3"] = a["fJ"] / b["fJ"]
                tie = E60["per_bit_tie"].get(card)
                if tie and card != "aifoundry3":
                    rel = (a["fJ"] / b["fJ"]) / tie
                    e[key + "_vs_E60_tie"] = rel
                    # XCHK 8: the registered band and the symmetric reading, reported separately -- the
                    # `or` silently widened §8.7's 0.88-0.99 to 0.88-1.12.
                    e[key + "_inside_E60_band"] = bool(0.88 <= rel <= 0.99)
                    e[key + "_inside_pm12pct"] = bool(abs(rel - 1) < 0.12)
            if a.get("rail_fJ") and b.get("rail_fJ"):
                e[key + "_rail_ratio_to_a3"] = a["rail_fJ"] / b["rail_fJ"]
        out[card] = e
    out["_band"] = ("E60 read card-to-card agreement inside a 0.88-0.99 band (§8.7); `_inside_pm12pct` is "
                    "the symmetric +-12% reading, reported beside it and never merged with it")
    return out


def holm(cards, primary):
    """§9.2: the five confirmatory coefficients, Holm-corrected within the family at alpha = 0.05."""
    C = cards.get(primary) or {}
    D = C.get("derived") or {}
    rows = []
    for name in CONFIRMATORY:
        d = D.get(name)
        if not d or d.get("t") is None:
            rows.append({"coef": name, "present": bool(d), "t": None,
                         "note": "not identified on %s" % primary if not d else "no between-pass SE"})
            continue
        rows.append({"coef": name, "present": True, "t": d["t"], "df": d.get("df"),
                     "n_passes": d.get("n_passes"), "value": d.get("value"),
                     "fJ": d.get("fJ"), "se_fJ": d.get("se_fJ")})
    live = [r for r in rows if r.get("t") is not None]
    live.sort(key=lambda r: -abs(r["t"]))
    k = len(live)
    rejected = True
    for i, r in enumerate(live):
        m = k - i
        r["holm_rank"] = i + 1
        r["alpha"] = HOLM_ALPHA / m
        r["t_crit_holm"] = t_crit(r["alpha"], r["df"]) if r.get("df") else None
        r["p_two"] = t_p_two(r["t"], r["df"]) if r.get("df") else None
        if not rejected:
            r["holm"] = "not tested (a higher rank failed; Holm stops)"
            continue
        ok = (r["t_crit_holm"] is not None and abs(r["t"]) >= r["t_crit_holm"])
        r["holm"] = "significant at alpha=0.05 family-wise" if ok else "not significant"
        rejected = ok
    elsewhere = {}
    for name in CONFIRMATORY:
        if (C.get("derived") or {}).get(name):
            continue
        for other in sorted(cards):
            if other == primary:
                continue
            d = (cards[other].get("derived") or {}).get(name)
            if d and d.get("value") is not None:
                elsewhere.setdefault(name, []).append(other)
    return {"primary_card": primary, "family": CONFIRMATORY, "alpha": HOLM_ALPHA,
            "n_in_family_tested": k, "rows": rows, "identified_only_elsewhere": elsewhere,
            "note": "the decision rests on the pinned card (§6), so Holm runs there; a coefficient "
                    "identified only on another card is named in identified_only_elsewhere and its "
                    "verdict row says which card scored it. Everything outside this family of five "
                    "is EXPLORATORY and labelled so (§9.2)"}


# =================================================================================================
# §9 the decision rules, one verdict per claim row
# =================================================================================================
# §9.4: an item whose SE exceeds one third of its rule's separation is UNDER-RESOLVED, not scored.
SEPARATION_fJ = {"e_cell": 0.3,                       # the prior's lower edge vs a null
                 "e_carry": PAGE["e_carry_fJ"] - 1.7,  # 14.2 (page) vs 1.7 (ours)
                 "e_addr": PAGE["e_addr_fJ"],          # 32 (page) vs a 0-2 prior
                 "e_out_bridge": PAGE["e_out_fJ"] - E60["e_out_interval_fJ"][1]}


def w3(se, df):
    """the 3-sigma-equivalent half-width of a quantity with this SE and df (§9.1)"""
    if not se or not df:
        return None
    tc = t_crit(THREE_SIGMA_P, df)
    return tc * se if tc else None


def in_interval(v, se, df, lo, hi):
    w = w3(se, df) or 0.0
    return None if v is None else bool(lo - w <= v <= hi + w)


def near(v, se, df, target):
    """|v - target| inside the 3-sigma-equivalent window"""
    if v is None or not se or not df:
        return None
    return bool(abs(v - target) / se < t_crit(THREE_SIGMA_P, df))


def excludes(v, se, df, target):
    """target excluded at >= 3 SE"""
    if v is None or not se or not df:
        return None
    return bool(abs(v - target) / se >= t_crit(THREE_SIGMA_P, df))


def ge_zero(v, se, df):
    if v is None or not se or not df:
        return None
    return bool(v / se >= t_crit(THREE_SIGMA_P, df))


def under_resolved(key, se_fJ):
    sep = SEPARATION_fJ.get(key)
    if sep is None or se_fJ is None:
        return None
    return bool(se_fJ > sep / 3.0)


def verdicts(cards, man, primary, missing):
    C = cards.get(primary) or {}
    D = C.get("derived") or {}
    F = C.get("families") or {}
    J = C.get("joint_fit") or {}
    out = []

    def row(claims, quantity, verdict, basis, **kw):
        e = {"claims": claims, "quantity": quantity, "verdict": verdict, "basis": basis,
             "card": primary}
        e.update(kw)
        out.append(e)
        return e

    def pick(key, cardlist=None):
        """the first card that carries this derived quantity, primary first"""
        order = [primary] + [c for c in sorted(cards) if c != primary]
        for c in (cardlist or order):
            d = (cards.get(c, {}).get("derived") or {}).get(key)
            if d and d.get("value") is not None:
                return c, d
        return None, None

    def fam_of(c, key):
        return ((cards.get(c, {}).get("families") or {}).get(key))

    def measured_tie(card, key="e_in_fxor"):
        """RECON 9: THIS campaign's per-bit tie between a card and the pinned one -- the ratio of the
        two cards' own e_in, measured tonight -- not E60's 1.376 / 1.216 from last night."""
        ref = (cards.get("aifoundry3", {}).get("derived") or {}).get(key) or {}
        a = (cards.get(card, {}).get("derived") or {}).get(key) or {}
        if a.get("fJ") and ref.get("fJ"):
            return a["fJ"] / ref["fJ"]
        return None

    # RECON 6: §9 rule 4 has ONE ordering in this file -- the under-resolved test runs FIRST, in every
    # row, before any CONFIRMED / REFUTED arm is evaluated.  The wf3 build tested the arms first for
    # e_addr and made the under-resolved branch conditional on an arm for the Miller and zero-word
    # rows, so the same rule decided three rows in three different orders.
    RULE4_ORDER = ("§9 rule 4, one ordering (RECON 6): the under-resolved test (SE > one third of the "
                   "rule's separation) is evaluated BEFORE the arms in every row; if it fires the row "
                   "is not scored. Only then are the arms read, and two arms satisfied -> OPEN with "
                   "the realised SE reported.")

    # ---- C13 C15 determinism -------------------------------------------------------------------
    gate_fails, rate_fails, mono, rc_items = 0, 0, [], set()
    for c, Cc in cards.items():
        for p, item, pos, why in (Cc.get("gates", {}).get("failed") or []):
            gate_fails += 1
            if any(w.startswith("rate ") or w.startswith("participants") or "not ok" in w for w in why):
                rate_fails += 1
        rc_items |= set((Cc.get("rate_gate") or {}).get("rate_confounded_items") or [])
        # A2.1: the monotonicity check is WITHIN ONE MODE, over rungs whose designed counts actually
        # differ.  Across modes the rate is a property of the compiled case, and family A's four rungs
        # have every data count exactly zero, so a cross-mode read of this test would flag the
        # a5 mode step as "the rate moves with the designed count" when no count moves at all.
        byfam = defaultdict(list)
        for n, e in (Cc.get("items") or {}).items():
            if e.get("ipc") is not None and e.get("zero"):
                byfam[(c, e.get("family"), e.get("zero"), str(man.mode_key(n)))].append(
                    (man.designed_flips(n), e["ipc"], n))
        for key, pts in byfam.items():
            xs = [x for x, _, _ in pts]
            ys = [y for _, y, _ in pts]
            if len(pts) < 3 or len(set(xs)) < 3:
                continue
            spread = (max(ys) / min(ys) - 1.0) if min(ys) else None
            rho = spearman(xs, ys)
            if spread is not None and spread > 0.005 and rho is not None and abs(rho) >= 0.9:
                mono.append({"card": key[0], "family": key[1], "zero": key[2], "mode": key[3],
                             "items": [n for _, _, n in pts],
                             "designed_flips": xs, "ipc": ys,
                             "rate_spread": spread, "spearman": rho})
    n_void = sum(len(Cc.get("pair_gate_voids") or []) for Cc in cards.values())
    n_kept = sum((Cc.get("gates") or {}).get("kept") or 0 for Cc in cards.values())
    n_ec = sum(1 for Cc in cards.values() for e in (Cc.get("items") or {}).values()
               if e.get("ipc") is not None)
    if not n_kept or not n_ec:
        v = "not run"
        basis = ("no kept run carries an ec rate (%d run(s) kept, %d item(s) with a rate), so the "
                 "determinism gates have nothing to score" % (n_kept, n_ec))
    elif mono:
        v = "REFUTED"
        basis = "a family's measured rate moves monotonically with the designed count: %s" % mono
    elif rate_fails == 0:
        v = "CONFIRMED"
        # RECON 16: say what the 0.2% matched-pair gate could run on at all.  A2 splits every pair
        # group by mode, and the manifest's `pair` links only ever joined items within N, V and M --
        # families B and gate carry no pair link, so "0 voids" there is "the gate never ran", not
        # "the gate passed".  And the CONFIRMED arm's other three legs are off-card.
        fams_with_groups, fams_without = set(), set()
        for c_, Cc in cards.items():
            gm = Cc.get("pair_groups") or {}
            in_group = set()
            for g in gm.values():
                for m_ in (g.get("members") or []):
                    in_group.add(m_)
            for nm_ in (Cc.get("items") or {}):
                f_ = man.family(nm_)
                (fams_with_groups if nm_ in in_group else fams_without).add(str(f_))
        fams_without -= fams_with_groups
        basis = ("no run failed the within-mode rate / ok / participants gates on any card; %d "
                 "pair-group subtraction(s) voided by the 0.2%% gate%s. "
                 "RECON 16: the 0.2%% matched-pair gate RAN on famil%s %s and NEVER RAN on famil%s %s "
                 "-- those have no `pair` link in the manifest (and A2 splits every group by mode), so "
                 "their zero voids mean the gate was never applicable, not that it passed. "
                 "The rest of this arm is OFF-CARD and stays visible: the objdump walk against "
                 "enercat_df.inc on every new mode, the ten sys_emu runs of §7 proof 4, and %s DUMP "
                 "line(s) in any run.log -- there is NO on-silicon register dump tonight (§7 proof 6 "
                 "is not implemented), so a corruption that leaves op count and participants intact is "
                 "outside the evidence."
                 % (n_void,
                    ("; %s excluded by name as rate-confounded (A2.4) and reported beside its ladder"
                     % sorted(rc_items)) if rc_items else "",
                    "ies" if len(fams_with_groups) != 1 else "y", sorted(fams_with_groups) or "none",
                    "ies" if len(fams_without) != 1 else "y", sorted(fams_without) or "none",
                    {c_: Cc.get("n_dump_lines") for c_, Cc in cards.items()}))
    else:
        v = "OPEN"
        basis = "%d run(s) failed a within-mode rate / ok / participants gate" % rate_fails
    row("C13 C15", "determinism of the designed flip counts", v, basis,
        monotone_checks=mono, pair_gate_voids=n_void, runs_kept=n_kept, items_with_a_rate=n_ec,
        rate_confounded_excluded_by_name=sorted(rc_items),
        a2_note="A2: every rate gate compares runs of ONE mode, since pass 1 showed the issue rate is "
                "fixed by the compiled case and not by the data (constant in h to 1e-4 within a mode, "
                "identical on all three cards).  A cross-mode ratio is reported, never gated.",
        caveat="the on-silicon register dump (plan §7 proof 6) was NOT implemented tonight, so this "
               "row rests on the ec rate gate, ok, participants and the off-card proofs "
               "(make_dtf.py --check, the objdump walk, sys_emu, the smoke block). DUMP lines seen: %s"
               % {c: Cc.get("n_dump_lines") for c, Cc in cards.items()},
        exploratory=False)

    # ---- C33 C37 the gate ladder ---------------------------------------------------------------
    gs = F.get("gate_spread")
    if not gs:
        row("C33 C37", "the gate ladder (OR / XOR / ADD at matched counts and port count)",
            "not run", "the gate family is absent on %s" % primary, exploratory=False)
    else:
        # VER 12: the row reads §8.4's PAIRED statistic when it exists, with the cross-item one
        # named beside it, because the two are different estimators of the same spread.
        _gp = gs.get("paired_fixed_pair") or {}
        _gm = gs.get("paired_per_pass_max_minus_min") or {}
        _use = _gp if _gp.get("t") is not None else gs
        spread_sig = (_use.get("t") is not None and _use.get("t_crit_3sigma") is not None
                      and abs(_use["t"]) >= _use["t_crit_3sigma"])
        marg = ("|t| = %s against the 3-sigma-equivalent %s"
                % (fmt(abs(_use.get("t") or 0.0), 3), fmt(_use.get("t_crit_3sigma"), 3))
                + (" -- VER 12: read on §8.4's PAIRED per-pass statistic, %s - %s differenced inside "
                   "each pass, %s +- %s fJ over %s passes. The cross-item reading the wf4 build used, "
                   "sqrt(se_min^2 + se_max^2), gives %s +- %s fJ and |t| = %s; the per-pass max - min "
                   "gives %s +- %s fJ and |t| = %s. All three fire the same arm here"
                   % (_gp.get("ops", ["?", "?"])[0], _gp.get("ops", ["?", "?"])[1],
                      fmt(_gp.get("spread_fJ"), 3), fmt(_gp.get("se_fJ"), 3), _gp.get("n_passes"),
                      fmt(gs.get("spread_fJ"), 3), fmt(gs.get("cross_item_se_fJ"), 3),
                      fmt(abs(gs.get("cross_item_t") or 0.0), 2),
                      fmt(_gm.get("spread_fJ"), 3), fmt(_gm.get("se_fJ"), 3),
                      fmt(abs(_gm.get("t") or 0.0), 2))
                   if _gp.get("t") is not None else ""))
        if spread_sig and gs.get("monotone_in_depth"):
            v, b = "CONFIRMED", "the three opcodes spread >= 3 SE and rank by gate depth (%s)" % marg
        elif spread_sig:
            v, b = "OPEN", ("spread >= 3 SE (%s) but NOT monotone in depth (%s): reported as "
                            "opcode-dependent, not gate-depth-dependent"
                            % (marg, ", ".join("depth %g -> %s fJ" % (r, fmt(y, 2))
                                               for r, y in (gs.get("by_depth") or []))))
        elif spread_sig is False:
            v = "REFUTED"
            b = ("the three opcodes agree within 3 SE (%s) -> the one-gate price is a wire-and-SRAM "
                 "price, not a gate price" % marg)
            if (_use.get("t") is not None and _use.get("t_crit_3sigma")
                    and abs(_use["t"]) >= 0.9 * _use["t_crit_3sigma"]):
                b += (". The margin is thin -- %s%% of the window -- and the order is %s, so even a "
                      "slightly larger spread would read OPEN (opcode-dependent), never CONFIRMED"
                      % (fmt(100.0 * abs(_use["t"]) / _use["t_crit_3sigma"], 1),
                         "monotone in depth" if gs.get("monotone_in_depth") else
                         "NOT monotone in gate depth (" + ", ".join(
                             "depth %g -> %s fJ" % (r, fmt(y, 2))
                             for r, y in (gs.get("by_depth") or [])) + ")"))
        else:
            v, b = "OPEN", "no between-pass SE for the spread"
        # RECON 14: the row is decided on the spread's OWN pass count, which is smaller than the
        # card's -- the three opcodes share one h rung and not every pass ran all three -- and the
        # measured order is named, because "OR < ADD < XOR" is not a gate-depth order (depth 1, 3, 2).
        npass_spread = gs.get("n_passes")
        npass_card = C.get("n_passes")
        order_txt = ", ".join("%s (depth %g) %s fJ" % (o_, r_, fmt(y_, 2))
                              for r_, y_, o_ in (gs.get("by_depth_named") or [])) \
            or ", ".join("depth %g -> %s fJ" % (r_, fmt(y_, 2)) for r_, y_ in (gs.get("by_depth") or []))
        ctx14 = ("RECON 14: this row rests on %s pass(es) (the card has %s) -- the three opcodes are "
                 "read at the ONE h they share (XCHK 3) and the statistic is the between-pass scatter "
                 "of THAT contrast. The measured order is %s; that order is NOT gate depth (for = 1, "
                 "fxor = 2, fadd = 3), so even a significant spread reads opcode-dependent, never "
                 "gate-depth-dependent."
                 % (npass_spread, npass_card, order_txt or "not resolved"))
        if (_use.get("t") is not None and _use.get("t_crit_3sigma")):
            ctx14 += (" The margin is |t| = %s of the %s window = %s%% (VER 12: on §8.4's paired "
                      "per-pass statistic; the cross-item reading gives |t| = %s)."
                      % (fmt(abs(_use["t"]), 2), fmt(_use["t_crit_3sigma"], 2),
                         fmt(100.0 * abs(_use["t"]) / _use["t_crit_3sigma"], 1),
                         fmt(abs(gs.get("cross_item_t") or 0.0), 2)))
            # RECON 14: which arm fires turns on the pass count, because the 3-sigma-equivalent
            # quantile falls steeply with df (5.96 at 7 passes, 4.53 at 8, 3.85 at 12).  §6 registered
            # 8 passes here and amendment A1 delivered 12; the registered count would read the other
            # way, and that has to be visible rather than left to the reader to notice.
            _alt = []
            for _np in (7, 8, 9, 10, 12, 14):
                _tc = t_crit(THREE_SIGMA_P, _np - 1)
                if _tc:
                    _alt.append((_np, _tc, "OPEN (spread >= 3 SE)" if abs(_use["t"]) >= _tc
                                 else "REFUTED (spread < 3 SE)"))
            _flips = len({c_ for _, _, c_ in _alt}) > 1
            _tmin = min((b_ for _, b_, _ in _alt), default=None)
            _tmax = max((b_ for _, b_, _ in _alt), default=None)
            ctx14 += (" How close is it to the other arm? The 3-sigma-equivalent quantile falls with "
                      "df (%s at 14 passes to %s at 7), so holding tonight's |t| = %s fixed the arm "
                      "reads: %s. %s §6 registered %s passes on this card and amendment A1 delivered "
                      "%s. Note this sensitivity moves the QUANTILE only -- the realised SE, and so "
                      "|t| itself, also depends on which passes ran, so a REFUTED reading of this row "
                      "needs a smaller realised spread-to-scatter ratio than tonight's, not just "
                      "fewer passes."
                      % (fmt(_tmin, 2), fmt(_tmax, 2), fmt(abs(_use["t"]), 2),
                         "; ".join("%d passes -> |t| >= %s -> %s" % (a_, fmt(b_, 2), c_)
                                   for a_, b_, c_ in _alt),
                         ("So the verdict TURNS ON the pass count at tonight's |t|."
                          if _flips else
                          "So at tonight's |t| the verdict does NOT turn on the pass count: the same "
                          "arm fires at every registered count."),
                         E60["n_passes_prereg_s6"].get(primary), E60["n_passes"].get(primary)))
        row("C33 C37", "an inverter is cheap: 2 FETs vs 10-12", v, b,
            spread=gs, fnot_leg=F.get("fnot_leg"),
            spread_statistic_read=("§8.4 paired per-pass (VER 12)" if _gp.get("t") is not None
                                   else "cross-item quadrature (no paired reading available)"),
            paired_spread_fJ=_gp.get("spread_fJ"), paired_spread_se_fJ=_gp.get("se_fJ"),
            paired_spread_t=_gp.get("t"), paired_spread_n_passes=_gp.get("n_passes"),
            cross_item_spread_fJ=gs.get("spread_fJ"),
            cross_item_spread_se_fJ=gs.get("cross_item_se_fJ"),
            cross_item_spread_t=gs.get("cross_item_t"),
            n_passes_the_spread_rests_on=npass_spread, n_passes_on_the_card=npass_card,
            context=ctx14,
            note="the fnot-vs-fxor leg is reported SEPARATELY as one-port/one-gate vs "
                 "two-port/one-gate; the registered conclusion is a bound on the total gate "
                 "contribution, never an attribution to FET count",
            exploratory=False)

    # ---- C61 C62 I-22 the register-file cell bit -----------------------------------------------
    cc, dcell = pick("e_cell")
    if not dcell:
        row("C61 C62 I-22", "energy per flipped register-file cell bit", "not run",
            "family V is absent: e_cell is NOT IDENTIFIED", exploratory=False)
    else:
        se_fJ = dcell.get("se_fJ")
        ur = under_resolved("e_cell", se_fJ)
        # A2.3: "scales with h" is read on the two arms' own ladders -- the slope is fitted over the
        # shared nonzero rungs, so a slope that exists at all over h = 16 AND 32 IS the scaling test;
        # the per-rung check below is the h = 32 against h = 16 step of each arm's own delta.
        # RECON 8: the "scales with h" condition is TESTED on the h = 16 rung against h = 32, not
        # asserted from the fact that a two-rung slope could be fitted at all.
        scales = fam_of(cc, "e_cell_scaling_test")
        VA = (cards[cc].get("families") or {}).get("V_arms") or {}
        if scales:
            scales = dict(scales)
            scales["ge_3SE"] = scales.get("proportional_within_3SE")
            scales["superseded_wf3_reading"] = (
                "the wf3 build set this condition TRUE whenever the slope was fitted over two rungs, "
                "which tests nothing: a slope exists whatever the two rungs say")
        null = (cards[cc].get("derived") or {}).get("e_cell_h0_null_W") or {}
        # A2.3: the h = 0 arm of §9 was written for the cross-mode paired estimator (d1b_h0 - d1a_h0).
        # Under A2 that difference is the two SHAPES' intercept difference at two different issue rates,
        # which each arm's own free intercept removes from the slope, so it is reported, not a gate.
        null_bad = False
        above = ge_zero(dcell.get("value"), dcell.get("se"), dcell.get("df"))
        below = (dcell.get("fJ") is not None and se_fJ
                 and (PRIOR["e_cell_fJ"][0] - dcell["fJ"]) / se_fJ >= (t_crit(THREE_SIGMA_P, dcell["df"]) or 9e9))
        big = dcell.get("fJ") is not None and dcell["fJ"] >= 10.0
        if ur:                                              # RECON 6: under-resolved FIRST
            v, b = "under-resolved", ("SE %.3f fJ exceeds one third of the rule's %.2f fJ separation "
                                      "(§9.4)" % (se_fJ or float('nan'), SEPARATION_fJ["e_cell"]))
            # RECON 8: not scored is not not reported -- the scaling test still goes in the basis.
            if scales and scales.get("per_bit_difference_high_minus_low"):
                _sd = scales["per_bit_difference_high_minus_low"]
                # VER 7: the test HAS NO POWER here.  The paired difference is 0.54 SE from zero
                # against a 3.85 window, so the data cannot tell proportionality (difference 0) from
                # the measured -16%: "proportional within 3 SE: True" and "nothing shows it scaling"
                # are the SAME non-result, and neither is evidence.
                _sdt = (scales.get("per_bit_difference_high_minus_low") or {})
                b += (". For the record, RECON 8's scaling test, which VER 7 reads as HAVING NO "
                      "POWER HERE: the per-cell-bit price is %s +- %s fJ at h = %s and %s +- %s fJ "
                      "at h = %s, a paired difference of %s +- %s fJ/bit (%s%% change, ratio of "
                      "means %s) where a law proportional to the designed cell count needs zero, "
                      "and the per-op step grows %sx where it needs %sx. That difference is |t| = "
                      "%s against the %s 3-sigma-equivalent window, so BOTH readings survive: "
                      "proportionality (a difference of exactly 0) is inside 3 SE and so is the "
                      "measured %s%% change, which is why `proportional_within_3SE` prints True. The "
                      "test therefore neither supports nor denies scaling with h -- it does not "
                      "discriminate at this resolution, so the CONFIRMED arm's second condition is "
                      "UNTESTED, not satisfied and not failed. The wf3 build recorded it as "
                      "SATISFIED without testing it at all, and the wf4 build read the same "
                      "non-result as 'nothing here shows the cell term scaling with h'; neither is "
                      "evidence either way."
                      % (fmt((scales.get("fJ_per_cell_bit_at_low_h") or {}).get("value"), 3),
                         fmt((scales.get("fJ_per_cell_bit_at_low_h") or {}).get("se"), 3),
                         fmt(scales.get("rung_low_h"), 0),
                         fmt((scales.get("fJ_per_cell_bit_at_high_h") or {}).get("value"), 3),
                         fmt((scales.get("fJ_per_cell_bit_at_high_h") or {}).get("se"), 3),
                         fmt(scales.get("rung_high_h"), 0),
                         fmt(_sd.get("value"), 3), fmt(_sd.get("se"), 3),
                         fmt(scales.get("per_bit_change_pct"), 1),
                         fmt((scales.get("per_bit_ratio_high_over_low") or {}).get("value"), 3),
                         fmt((scales.get("per_op_growth_high_over_low") or {}).get("value"), 3),
                         fmt(scales.get("per_op_growth_a_proportional_law_needs"), 2),
                         fmt(abs(_sdt.get("t") or 0.0), 2), fmt(_sdt.get("t_crit_3sigma"), 2),
                         fmt(scales.get("per_bit_change_pct"), 1)))
        elif big:
            v, b = "OPEN", "e_cell >= 10 fJ: the cell, not the bus, dominates e_out and E60's split needs re-reading"
        elif null_bad:
            v, b = "OPEN", "the h=0 rung shows a non-zero difference: the two shapes differ for a reason other than cells"
        elif above and (scales or {}).get("ge_3SE"):
            v, b = "CONFIRMED", ("e_cell >= 3 SE above zero AND the per-cell-bit price is the same at "
                                 "h = %s and h = %s within 3 SE (paired difference %s +- %s fJ/bit, "
                                 "ratio of means %s), so it scales with h (RECON 8)"
                                 % (fmt((scales or {}).get("rung_low_h"), 0),
                                    fmt((scales or {}).get("rung_high_h"), 0),
                                    fmt(((scales or {}).get("per_bit_difference_high_minus_low") or {}).get("value"), 3),
                                    fmt(((scales or {}).get("per_bit_difference_high_minus_low") or {}).get("se"), 3),
                                    fmt(((scales or {}).get("per_bit_ratio_high_over_low") or {}).get("value"), 3)))
        elif above and scales and scales.get("ge_3SE") is False:
            _sr = (scales.get("per_bit_ratio_high_over_low") or {})
            _sd = (scales.get("per_bit_difference_high_minus_low") or {})
            v = "OPEN"
            b = ("e_cell is >= 3 SE above zero, but the second CONFIRMED condition FAILS the test "
                 "RECON 8 added: the per-cell-bit price is %s +- %s fJ at h = %s and %s +- %s fJ at "
                 "h = %s, a paired difference of %s +- %s fJ/bit (ratio of means %s, %s%% change) "
                 "where proportionality needs zero, and the per-op step grows %sx where it needs %sx. "
                 "So the difference is real and is NOT proportional to the designed cell count -- "
                 "reported, not scored as CONFIRMED."
                 % (fmt((scales.get("fJ_per_cell_bit_at_low_h") or {}).get("value"), 3),
                    fmt((scales.get("fJ_per_cell_bit_at_low_h") or {}).get("se"), 3),
                    fmt(scales.get("rung_low_h"), 0),
                    fmt((scales.get("fJ_per_cell_bit_at_high_h") or {}).get("value"), 3),
                    fmt((scales.get("fJ_per_cell_bit_at_high_h") or {}).get("se"), 3),
                    fmt(scales.get("rung_high_h"), 0),
                    fmt(_sd.get("value"), 3), fmt(_sd.get("se"), 3),
                    fmt(_sr.get("value"), 3), fmt(scales.get("per_bit_change_pct"), 1),
                    fmt((scales.get("per_op_growth_high_over_low") or {}).get("value"), 3),
                    fmt(scales.get("per_op_growth_a_proportional_law_needs"), 2)))
        elif below:
            v, b = "REFUTED", ("e_cell < 0.3 fJ/bit at >= 3 SE: the cell flip is below the 1/2 CV^2 "
                               "prior, and the write's energy is dominated by the common-mode bitline "
                               "drive, which this contrast cannot see at all")
        else:
            v, b = "OPEN", "neither arm fires"
        row("C61 C62 I-22", "energy per flipped register-file cell bit", v, b, card=cc,
            value_fJ=dcell.get("fJ"), se_fJ=se_fJ, rail_fJ=dcell.get("rail_fJ"),
            n_passes=dcell.get("n_passes"), scaling=scales, h0_null=null, prior_fJ=PRIOR["e_cell_fJ"],
            scaling_test_ran=bool(scales), method=RULE4_ORDER,
            sensitivity=((cards[cc].get("leak_sensitivity") or {}).get("rows") or {}).get("e_cell"),
            confirmatory=True, exploratory=False)

    # ---- C56 C57 C63 C64 C86 e_out, the bridge -------------------------------------------------
    # RECON 3: the registered rule for this row names "the joint-fit e_out (with w fitted)", so the
    # joint fit is the basis whenever it is identified, with the raw 2 x 2 reported BESIDE it and the
    # term that separates them named.  The wf3 build quoted the joint fit but also carried a
    # "rank-deficient, no §9 decision may rest on this joint fit" flag read off the RAW design's
    # condition number -- a units artefact -- so the row's number and the row's own caveat disagreed.
    ejoint = (J.get("coefs") or {}).get("e_out") or {}
    draw = D.get("e_out_bridge") or {}
    src = ejoint if ejoint.get("fJ") is not None else draw
    if ejoint.get("not_identified") and not draw.get("fJ"):
        src = {}
    if not src.get("fJ"):
        row("C56 C57 C63 C64 C86", "e_out (the input/output bridge)", "not run",
            "family B's 2x2 is incomplete on %s" % primary, exploratory=False)
    else:
        lo, hi = E60["e_out_interval_fJ"]
        isE60 = in_interval(src["fJ"], src.get("se_fJ"), src.get("df"), lo, hi)
        isPage = near(src["fJ"], src.get("se_fJ"), src.get("df"), PAGE["e_out_fJ"])
        # §9's OPEN column for this row names "the h = 0 intercepts differ by more than 3 SE between
        # cells" beside "neither interval", so it is a registered OPEN condition, not a note: every
        # differing pair is collected, and §9 rule 4's precedence is applied below rather than
        # silently dropped.  Which pairs differ matters for the reading: the 2 x 2 cancels
        # alpha(opcode) by construction, so a CROSS-opcode difference is the design working, while a
        # WITHIN-opcode one (d2A vs d2B, or d2C vs d2D) would mean the cells differ for another reason.
        h0bad = None
        h0diff, h0_within, h0_cross = {}, [], []
        _opc = {"d2A": "fand", "d2B": "fand", "d2C": "for", "d2D": "for"}
        for k_, d_ in sorted((F.get("B_h0_intercepts_W") or {}).items()):
            if ge_zero(abs(d_.get("value") or 0.0), d_.get("se"), d_.get("df")):
                h0bad = k_
                h0diff[k_] = {"W": d_.get("value"), "se": d_.get("se"), "t": d_.get("t"),
                              "t_crit_3sigma": d_.get("t_crit_3sigma")}
                a_, _, b_ = k_.partition("-")
                (h0_within if _opc.get(a_) == _opc.get(b_) else h0_cross).append(k_)
        # §5.0 rule 2: a registered interval is read WIDENED by the statistic's own 3-SE-equivalent
        # window, so the basis says both -- the point value and whether it needed the widening.
        strict = (src["fJ"] is not None and lo <= src["fJ"] <= hi)
        wid = w3(src.get("se_fJ"), src.get("df")) or 0.0
        if isE60 and not isPage:
            v = "CONFIRMED"
            b = ("the joint-fit e_out lands in E60's [%.2f, %.2f] fJ -> E60 confirmed through a "
                 "second, independent kernel (%s +- %s fJ, %s)"
                 % (lo, hi, fmt(src["fJ"], 2), fmt(src.get("se_fJ"), 3),
                    "inside the interval itself" if strict else
                    "inside it only once widened by its own 3-SE-equivalent window of +-%s fJ "
                    "(§5.0 rule 2); the point value is %s the interval"
                    % (fmt(wid, 2), "below" if src["fJ"] < lo else "above")))
            b += ("; the raw (B+D)-(A+C) combination reads %s +- %s fJ, %s fJ lower, and §5.1 is why "
                  "e_out is quoted from the fit that carries changed words as a regressor"
                  % (fmt(draw.get("fJ"), 2), fmt(draw.get("se_fJ"), 2),
                     fmt((ejoint.get("fJ") or 0) - (draw.get("fJ") or 0), 2))) \
                if (draw.get("fJ") is not None and src is ejoint) else ""
        elif isPage and not isE60:
            v, b = "REFUTED", "the joint-fit e_out lands on the page's %.2f fJ -> the page stands and E60 is wrong" % PAGE["e_out_fJ"]
        elif isPage and isE60:
            v, b = "OPEN", "both arms satisfied (§9.4 precedence): the realised SE is %s fJ" % fmt(src.get("se_fJ"))
        else:
            v, b = "OPEN", "neither interval"
        confirmed_arm = (v == "CONFIRMED")
        if h0diff and v in ("CONFIRMED", "REFUTED"):
            # §9 rule 4: two arms satisfied -> OPEN, and the realised SE is reported.
            b = ("§9 rule 4 precedence: the %s arm is satisfied -- %s -- AND the registered OPEN "
                 "condition \"the h = 0 intercepts differ by more than 3 SE between cells\" fires on "
                 "%s. %s So the row is OPEN, and the number above is reported, not scored."
                 % (v, b, ", ".join("%s = %s +- %s W (t %s vs %s)"
                                    % (k_, fmt(x["W"], 4), fmt(x["se"], 4), fmt(x["t"], 2),
                                       fmt(x["t_crit_3sigma"], 2))
                                    for k_, x in sorted(h0diff.items())),
                    ("Every differing pair is CROSS-opcode (%s) and the two within-opcode pairs agree, "
                     "so the measured pattern is alpha(fand) - alpha(for) -- exactly the term the 2 x 2 "
                     "cancels by construction (§4), which is why the arm's number still landed."
                     % ", ".join(h0_cross)) if (h0_cross and not h0_within) else
                    ("A WITHIN-opcode pair differs (%s): the four cells are not matched for a reason "
                     "other than opcode, which the 2 x 2 does NOT cancel." % ", ".join(h0_within))))
            v = "OPEN"
        if draw.get("carries_changed_word_term") and src is draw:
            v = "OPEN"
            b = ("the raw bridge has one nonzero rung, so the §5.1 changed-word term is not removed "
                 "and no joint-fit e_out is available to replace it: not scored")
        # RECON 6: §9 rule 4's under-resolved test runs FIRST here too.
        ur_o = under_resolved("e_out_bridge", src.get("se_fJ"))
        if ur_o:
            v = "under-resolved"
            b = ("SE %s fJ exceeds one third of the rule's %.2f fJ separation (the page's %.2f against "
                 "the top of E60's interval, %.2f) (§9.4, RECON 6: tested before the arms)"
                 % (fmt(src.get("se_fJ"), 3), SEPARATION_fJ["e_out_bridge"], PAGE["e_out_fJ"],
                    E60["e_out_interval_fJ"][1]))
        # RECON 3: the basis names its own source and the raw 2 x 2 beside it.
        # VER 3 (the fix verifier's MUST FIX 3): it no longer asserts that the gap between the two IS
        # the §5.1 changed-word term.  The gap is measured here in both units -- fJ per flip and watts
        # on the bridge's OWN per-mode denominator -- and the R2 term, priced consistently (VER 1), is
        # stated as the share of it that the term can account for.  The remainder is unexplained by
        # §5.1 and is a difference between two estimators (a 7-regressor pooled fit against a 2 x 2
        # difference of four cells), which is a finding, not an identity.
        _c56_both = (ejoint.get("fJ") is not None and draw.get("fJ") is not None)
        _gap_fJ = ((ejoint.get("fJ") - draw.get("fJ")) if _c56_both else None)
        _bden = F.get("B_bridge_denominator_bits_per_s")
        _gap_W = ((_gap_fJ * 1e-15 * _bden) if (_gap_fJ is not None and _bden) else None)
        _r2W = F.get("B_bridge_R2_correction_W")
        _r2fJ = ((_r2W / _bden * 1e15) if (_r2W is not None and _bden) else None)
        _r2share = ((100.0 * _r2W / _gap_W) if (_r2W is not None and _gap_W) else None)
        _c56_gap = {"joint_fit_fJ": ejoint.get("fJ"), "raw_bridge_fJ": draw.get("fJ"),
                    "gap_fJ_per_flip": _gap_fJ, "gap_W": _gap_W,
                    "bridge_denominator_bits_per_s": _bden,
                    "bridge_denominator_how": F.get("B_bridge_denominator_how"),
                    "R2_changed_word_term_W": _r2W, "R2_changed_word_term_fJ_per_flip": _r2fJ,
                    "R2_changed_words_per_op": F.get("B_bridge_R2_changed_words_per_op"),
                    "R2_term_as_pct_of_the_gap": _r2share,
                    "note": "VER 3: the gap is REPORTED, not identified with the §5.1 term. §5.1 "
                            "predicts the raw bridge is biased by exactly the intercept under reading "
                            "R2, and that term accounts for part of this gap; the rest separates two "
                            "estimators and is not explained by changed words."}
        b += ("" if not _c56_both else
              " || RECON 3, the two readings side by side: the registered basis is the JOINT-FIT "
              "e_out, %s +- %s fJ (VIF %s, column-scaled condition number %s over %s rows per pass), "
              "and the raw 2 x 2 reads %s +- %s fJ. VER 3, what the gap IS: the joint fit sits %s fJ "
              "per flip %s the raw combination, which on the bridge's own per-mode denominator (%s = "
              "%s bits/s) is %s W. The §5.1 R2 changed-word term is a PART of that gap, not the whole "
              "of it: the raw combination changes %s 32-bit word(s) per op and §5.1 prices them at the "
              "ladder intercept, %s W = %s fJ per flip, which is %s%% of the gap. The remaining %s W "
              "is the difference between two estimators -- a pooled 7-regressor fit against a 2 x 2 "
              "difference of four cells -- and is not accounted for by changed words. %s"
              % (fmt(ejoint.get("fJ"), 2), fmt(ejoint.get("se_fJ"), 3),
                 fmt((J.get("vif") or {}).get("e_out"), 2), fmt(J.get("condition_number"), 3),
                 J.get("rows_per_pass"),
                 fmt(draw.get("fJ"), 2), fmt(draw.get("se_fJ"), 3),
                 fmt(abs(_gap_fJ or 0.0), 3),
                 ("above" if (_gap_fJ or 0) > 0 else "below"),
                 F.get("B_bridge_denominator_how") or "8h r300 + 8h r301",
                 ("%.4e" % _bden) if _bden else "n/a",
                 fmt(_gap_W, 4),
                 fmt(F.get("B_bridge_R2_changed_words_per_op"), 0),
                 fmt(_r2W, 4), fmt(_r2fJ, 3), fmt(_r2share, 1),
                 fmt(((_gap_W - _r2W) if (_gap_W is not None and _r2W is not None) else None), 4),
                 ("The raw bridge's own rate denominator was corrected by RECON 1 (each leg at its "
                  "own mode's rate), which moved it %s%% down from the single-rate form."
                  % fmt(draw.get("one_rate_form_excess_pct"), 2))
                 if draw.get("one_rate_form_excess_pct") is not None else ""))
        row("C56 C57 C63 C64 C86", "e_out, from the 2x2 bridge with w fitted", v, b,
            under_resolved=ur_o, method=RULE4_ORDER,
            raw_bridge_rate_denominator="per mode, 8h x r(mode 300) + 8h x r(mode 301) -- RECON 1",
            raw_bridge_one_rate_form_fJ=draw.get("one_rate_form_fJ"),
            raw_bridge_one_rate_excess_pct=draw.get("one_rate_form_excess_pct"),
            joint_fit_condition_number_raw_design=J.get("condition_number_raw_design"),
            joint_fit_condition_number_basis=J.get("condition_number_basis"),
            joint_fit_design_is_degenerate=J.get("design_is_degenerate"),
            sensitivity=((C.get("leak_sensitivity") or {}).get("rows") or {}).get("e_out_bridge"),
            confirmed_arm_satisfied=confirmed_arm,
            h0_intercepts_differing=h0diff, h0_differing_within_opcode=h0_within,
            h0_differing_cross_opcode=h0_cross,
            bridge_n_rungs=draw.get("n_rungs"), bridge_intercept_removed=draw.get("intercept_removed"),
            bridge_carries_changed_word_term=draw.get("carries_changed_word_term"),
            joint_minus_raw_fJ=_gap_fJ, joint_minus_raw_gap=_c56_gap,
            joint_fit_fJ=ejoint.get("fJ"), joint_fit_se_fJ=ejoint.get("se_fJ"),
            quoted_from=("the §8.5 joint fit (§5.1: it carries changed 32-bit words/s as a regressor)"
                         if src is ejoint else "the raw 2x2 combination (no joint fit available)"),
            strict_reading_in_interval=(src["fJ"] is not None and lo <= src["fJ"] <= hi),
            three_sigma_widening_fJ=w3(src.get("se_fJ"), src.get("df")),
            joint_fit_condition_number=J.get("condition_number"),
            joint_fit_vif_e_out=(J.get("vif") or {}).get("e_out"),
            raw_combination_fJ=draw.get("fJ"), raw_combination_se_fJ=draw.get("se_fJ"),
            rail_fJ=src.get("rail_fJ"), E60_interval_fJ=[lo, hi], page_fJ=PAGE["e_out_fJ"],
            h0_intercepts_differ=h0bad,
            R2_reading=F.get("N_intercept_readings", {}).get("matched"),
            R2_corrected_W=F.get("B_bridge_R2_corrected_W"),
            raw_W=(F.get("B_bridge_raw_W") or {}).get("value"),
            exploratory=False)

    # ---- C65, refuted by design ----------------------------------------------------------------
    row("C65", "A vs C measures the NMOS/PMOS Miller skew", "REFUTED",
        "by design, whatever the data: (B-A)-(D-C) = 2 g_op + g_res, so the A-vs-C difference "
        "carries the held-value and zero-result effects, and A and C also differ in opcode. "
        "Reported as an AND/OR/clamp-polarity contrast, never as device polarity.",
        measured_2gop_gres=(D.get("zero_word_bridge_2gop_gres") or {}).get("value"),
        measured_fJ_per_op=(D.get("zero_word_bridge_2gop_gres") or {}).get("fJ_per_op"),
        exploratory=False)

    # ---- C14 C64 d2A's read-port price ---------------------------------------------------------
    da = D.get("e_in_fand_d2A") or {}
    if not da.get("fJ"):
        row("C14 C64", "zero gate outputs, zero pipeline latches, zero writeback wires flip",
            "not run", "d2A is absent on %s" % primary, scored=False, exploratory=False)
    else:
        lo, hi = E60["e_in_fand_interval_fJ"]
        inside = in_interval(da["fJ"], da.get("se_fJ"), da.get("df"), lo, hi)
        wdt = w3(da.get("se_fJ"), da.get("df")) or 0.0
        # VER 2 (the fix verifier's MUST FIX 2): this row is NOT SCORED.  README §5.2 registers the
        # A/C arms as the MEASUREMENT of e_in(fand)/e_in(for) -- "d2A cannot both supply e_in(fand)
        # and be tested against it" -- and drops the C14/C64 equivalence to E60's one-rung 28.10 fJ
        # "as a decision (reported as agreement or disagreement, not scored)".  The wf4 build scored
        # it CONFIRMED on d2A's delta/8h landing in [26.0, 30.2] fJ, which is the §9 table's row read
        # without §5.2's overriding sentence.  The arms below are kept as the DIRECTION of the
        # agreement, with no verdict attached.
        v = "not scored"
        agree = "AGREEMENT" if inside else "DISAGREEMENT"
        if inside:
            _dir = ("lands in E60's fand interval [%.1f, %.1f] fJ: %s +- %s fJ, %s"
                    % (lo, hi, fmt(da["fJ"], 3), fmt(da.get("se_fJ"), 3),
                       "inside the interval itself" if lo <= da["fJ"] <= hi else
                       "inside it only once widened by its own 3-SE-equivalent window of +-%s fJ "
                       "(§5.0 rule 2); the point value is %s the interval"
                       % (fmt(wdt, 2), "below" if da["fJ"] < lo else "above")))
        elif da["fJ"] > hi + wdt:
            _dir = ("EXCEEDS the interval by >= 3 SE (%s +- %s fJ against [%.1f, %.1f]), which would "
                    "read as the write port, wordline or precharge cycling with the data unchanged"
                    % (fmt(da["fJ"], 3), fmt(da.get("se_fJ"), 3), lo, hi))
        else:
            _dir = ("FALLS SHORT by >= 3 SE (%s +- %s fJ against [%.1f, %.1f]), which would read as "
                    "for/fand read-port prices differing from fxor's by more than the interval allows"
                    % (fmt(da["fJ"], 3), fmt(da.get("se_fJ"), 3), lo, hi))
        b = ("REPORTED, NOT SCORED (VER 2, README §5.2): the A/C arms are registered as the "
             "MEASUREMENT of e_in(fand) / e_in(for), so d2A cannot both supply e_in(fand) and be "
             "tested against it, and the equivalence to E60's one-rung 28.10 +- 0.70 fJ is dropped as "
             "a decision -- reported as agreement or disagreement. The reading is %s: d2A's "
             "delta / 8h %s. d2C (for.pi, the same shape with a static all-ones result) reads %s fJ, "
             "so the two read-port prices agree with each other, which is the premise the bridge's "
             "e_out rests on and is the part of this row that carries weight."
             % (agree, _dir, fmt((D.get("e_in_for_d2C") or {}).get("fJ"), 3)))
        # RECON 11: this arm is decided AT THE EDGE of the interval, so every rung and every fit
        # form is printed and the margin is named.
        rungs = F.get("e_in_fand_d2A_by_rung") or {}
        forms = {"one rung, delta / 8h (the row's own form)": da,
                 "(0,0) added + free intercept (= the endpoint slope by algebra)":
                     D.get("e_in_fand_d2A_with_origin"),
                 "forced through the origin, no intercept":
                     D.get("e_in_fand_d2A_through_origin"),
                 "two rungs, free intercept (§8.4's form)": D.get("e_in_fand_d2A_free_intercept")}
        rtxt = ", ".join("%s %s +- %s fJ" % (k_, fmt((v_ or {}).get("fJ"), 3),
                                             fmt((v_ or {}).get("se_fJ"), 3))
                         for k_, v_ in sorted(rungs.items()) if (v_ or {}).get("fJ") is not None)
        ftxt = "; ".join("%s = %s +- %s fJ" % (k_, fmt((v_ or {}).get("fJ"), 3),
                                               fmt((v_ or {}).get("se_fJ"), 3))
                         for k_, v_ in sorted(forms.items()) if (v_ or {}).get("fJ") is not None)
        # VER 5 (the fix verifier's SHOULD FIX): this is one of the two rows the leakage-slope arm
        # MOVES, and it moves the ANSWER, not just the number -- so the row says where it lands at
        # each slope rather than leaving the reader to divide the sensitivity line by the SE.
        _lsrow = (((C.get("leak_sensitivity") or {}).get("rows") or {}).get("e_in_fand_d2A")) or {}
        _leak_txt = None
        _leak_arms = {}
        for _nm, _lbl in (("fitted", "the fitted slope %s W/C (PRIMARY, §8.1)"
                           % fmt((C.get("leak_sensitivity") or {}).get("k_W_per_C", {}).get("fitted"), 3)),
                          ("zero", "k = 0"),
                          ("E60", "E60's %s W/C"
                           % fmt((C.get("leak_sensitivity") or {}).get("k_E60_W_per_C"), 3))):
            _r = _lsrow.get(_nm) or {}
            if _r.get("value") is None:
                continue
            _df = (_r.get("n_passes") - 1) if _r.get("n_passes") else da.get("df")
            _w = w3(_r.get("se"), _df) or 0.0
            _strict = (lo <= _r["value"] <= hi)
            _wide = ((lo - _w) <= _r["value"] <= (hi + _w))
            _leak_arms[_nm] = {"fJ": _r["value"], "se_fJ": _r.get("se"), "3SE_widening_fJ": _w,
                               "in_strict_interval": _strict,
                               "in_interval_after_3SE_widening": _wide,
                               "reading": ("AGREEMENT" if _wide else "DISAGREEMENT")}
            _leak_arms[_nm]["label"] = _lbl
        if _leak_arms:
            _leak_txt = ("VER 5, the leakage-slope arm MOVES THIS ROW'S ANSWER, not only its number: "
                         + "; ".join(
                             "at %s, %s +- %s fJ -- %s the strict [%.1f, %.1f] and %s it once widened "
                             "by its own 3-SE window of +-%s fJ (%s)"
                             % (_leak_arms[_k]["label"], fmt(_leak_arms[_k]["fJ"], 3),
                                fmt(_leak_arms[_k]["se_fJ"], 3),
                                "INSIDE" if _leak_arms[_k]["in_strict_interval"] else "OUTSIDE",
                                lo, hi,
                                "INSIDE" if _leak_arms[_k]["in_interval_after_3SE_widening"] else "OUTSIDE",
                                fmt(_leak_arms[_k]["3SE_widening_fJ"], 3),
                                _leak_arms[_k]["reading"])
                             for _k in ("fitted", "zero", "E60") if _k in _leak_arms)
                         + ". §8.1 registers the card's own FITTED slope, so the reading above is the "
                           "fitted one; the E60-slope reading is reported beside it and is not the "
                           "row's answer. Since the row is reported rather than scored (VER 2), the "
                           "agreement is a statement about the slope choice as well as about the data.")
        edge_d = (da["fJ"] - lo) if da.get("fJ") is not None else None
        ctx11 = ("RECON 11: the arm sits AT THE EDGE. The quoted value is %s +- %s fJ against an "
                 "interval that opens at %.1f fJ -- %s fJ above it, %s SE. Every rung: %s. Every fit "
                 "form: %s. The rungs disagree by more than the quoted SE, so 'inside the interval' "
                 "is a statement about WHICH rung and WHICH fit form were chosen, not only about the "
                 "data; that choice is listed in the method block."
                 % (fmt(da.get("fJ"), 3), fmt(da.get("se_fJ"), 3), lo, fmt(edge_d, 3),
                    fmt((edge_d / da["se_fJ"]) if (edge_d is not None and da.get("se_fJ")) else None, 2),
                    rtxt or "only one", ftxt or "only one"))
        row("C14 C64", "d2A: the read-port price with a static result", v, b,
            scored=False, reported_as=agree,
            not_scored_because="README §5.2: the A/C arms ARE the measurement of e_in(fand) / "
                               "e_in(for), so the equivalence to E60's 28.10 fJ is reported as "
                               "agreement or disagreement, never scored (VER 2)",
            margin=_leak_txt, leak_arm_by_slope=_leak_arms,
            value_fJ=da["fJ"], se_fJ=da.get("se_fJ"), rail_fJ=da.get("rail_fJ"),
            E60_interval_fJ=[lo, hi], e_in_for_d2C_fJ=(D.get("e_in_for_d2C") or {}).get("fJ"),
            by_rung=dict((k_, {"fJ": (v_ or {}).get("fJ"), "se_fJ": (v_ or {}).get("se_fJ"),
                               "n_passes": (v_ or {}).get("n_passes")})
                         for k_, v_ in sorted(rungs.items())),
            by_fit_form=dict((k_, {"fJ": (v_ or {}).get("fJ"), "se_fJ": (v_ or {}).get("se_fJ")})
                             for k_, v_ in sorted(forms.items()) if v_),
            fJ_above_the_lower_edge=edge_d, context=ctx11,
            sensitivity=((C.get("leak_sensitivity") or {}).get("rows") or {}).get("e_in_fand_d2A"),
            exploratory=False)

    # ---- C54 C67 C68 C87 the carry price -------------------------------------------------------
    cc, dcar = pick("e_carry")
    if not dcar:
        row("C54 C67 C68 C87", "energy per bit position of carry propagation (ripple-equivalent)",
            "not run", "family C or e_out(add) is absent: e_carry is NOT IDENTIFIED",
            confirmatory=True, exploratory=False)
    else:
        se_fJ = dcar.get("se_fJ")
        ur = under_resolved("e_carry", se_fJ)
        isPage = near(dcar["fJ"], se_fJ, dcar["df"], PAGE["e_carry_fJ"])
        isOurs = near(dcar["fJ"], se_fJ, dcar["df"], 1.7)
        pageExcluded = excludes(dcar["fJ"], se_fJ, dcar["df"], PAGE["e_carry_fJ"])
        if ur:                                              # RECON 6: under-resolved FIRST
            v, b = "under-resolved", "SE %s fJ exceeds one third of the 12.5 fJ separation (§9.4)" % fmt(se_fJ)
        elif isPage and not isOurs:
            v, b = "CONFIRMED-page", "e_carry lands on the page's 14.2 fJ +- 3 SE"
        elif isOurs and pageExcluded:
            v, b = "CONFIRMED-ours", "e_carry lands on 1.7 fJ +- 3 SE and 14.2 fJ is excluded at >= 3 SE"
        elif isPage and isOurs:
            v, b = "OPEN", "both arms satisfied (§9.4 precedence)"
        else:
            v, b = "REFUTED-both", "neither 14.2 nor 1.7 fJ holds"
        cur = (cards[cc].get("families") or {}).get("C_curvature") or {}
        # RECON 4: say which e_out(add) the number rests on, and print the two alternatives, so the
        # registered route and the route the wf3 build used are both visible.
        _eoa = fam_of(cc, "e_out_add_registered") or {}
        _alt = (cards[cc].get("derived") or {}).get("e_carry_alt_from_B") or {}
        _alt2 = fam_of(cc, "e_out_add_from_d3z_minus_ein_fxor") or {}
        b += (" || RECON 4, the registered estimator: e_out(add) comes from d3z -- the same opcode, "
              "the same shape, the same pass -- as 2 x its per-(port+result)-bit slope minus e_in from "
              "the SAME c2 shape's d2A, giving e_out(add) = %s +- %s fJ, and e_carry = the d3 slope "
              "per carry node (%s +- %s fJ) minus it. §4 forbids importing e_out from fand/for; that "
              "route reads e_carry = %s +- %s fJ and is printed as e_carry_alt_from_B, and the "
              "d3z-minus-e_in(fxor) route (a different shape and opcode) reads e_out(add) = %s fJ."
              % (fmt(_eoa.get("fJ"), 2), fmt(_eoa.get("se_fJ"), 3),
                 fmt(((cards[cc].get("derived") or {}).get("e_out_add_plus_e_carry") or {}).get("fJ"), 2),
                 fmt(((cards[cc].get("derived") or {}).get("e_out_add_plus_e_carry") or {}).get("se_fJ"), 3),
                 fmt(_alt.get("fJ"), 2), fmt(_alt.get("se_fJ"), 3), fmt(_alt2.get("fJ"), 2)))
        _r2 = (cards[cc].get("derived") or {}).get("e_carry_R2_corrected") or {}
        _r2t = fam_of(cc, "e_out_add_registered_R2_term") or {}
        if _r2.get("fJ") is not None:
            _isP2 = near(_r2["fJ"], _r2.get("se_fJ"), _r2.get("df"), PAGE["e_carry_fJ"])
            _isO2 = near(_r2["fJ"], _r2.get("se_fJ"), _r2.get("df"), 1.7)
            _exP2 = excludes(_r2["fJ"], _r2.get("se_fJ"), _r2.get("df"), PAGE["e_carry_fJ"])
            _v2 = ("CONFIRMED-ours" if (_isO2 and _exP2) else
                   ("CONFIRMED-page" if (_isP2 and not _isO2) else
                    ("OPEN (both arms)" if (_isP2 and _isO2) else "REFUTED-both")))
            b += (" || RECON 4 / §5.1, and this one is NOT cosmetic: the d3z leg is ONE rung through "
                  "its own zero, and that zero changes %g fewer 32-bit word(s) per op (0 against %g), "
                  "so the registered e_out(add) carries the changed-word term under reading R2 -- "
                  "+%s fJ/flip priced at the N ladder's own fitted intercept -- exactly as XCHK 7 "
                  "says of a one-rung bridge. Corrected for it, e_out(add) = %s fJ and e_carry = "
                  "%s +- %s fJ, which reads %s: 1.7 fJ is %sinside 3 SE (|t| %s) and 14.2 fJ is %s "
                  "(|t| %s), against the %s window. %s Both readings are reported; the primary is "
                  "the registered form (%s fJ, verdict %s), because §4 registers the estimator and "
                  "§5.1's reading is itself an OPEN row in this file. VER 1: the term is priced at "
                  "the intercept per R2 changed word (%g words/op), which is the reading dw is "
                  "counted on -- the wf4 build priced it per SOURCE word (8) against an R2 count of "
                  "16, doubling it to %s fJ/flip and flipping this corrected reading to REFUTED-both "
                  "on nothing but the mismatched reading."
                  % (_r2t.get("changed_words_per_op_delta") or 0,
                     _r2t.get("changed_words_per_op_delta") or 0,
                     fmt(_r2t.get("fJ_per_flip"), 2),
                     fmt(((cards[cc].get("families") or {})
                          .get("e_out_add_registered_R2_corrected") or {}).get("fJ"), 2),
                     fmt(_r2["fJ"], 2), fmt(_r2.get("se_fJ"), 3), _v2,
                     "" if _isO2 else "NOT ",
                     fmt(abs(_r2["fJ"] - 1.7) / _r2["se_fJ"] if _r2.get("se_fJ") else None, 2),
                     "excluded" if _exP2 else "not excluded",
                     fmt(abs(_r2["fJ"] - PAGE["e_carry_fJ"]) / _r2["se_fJ"] if _r2.get("se_fJ") else None, 2),
                     fmt(t_crit(THREE_SIGMA_P, _r2.get("df")) if _r2.get("df") else None, 2),
                     ("So the row's verdict DOES NOT depend on whether that term is removed: the "
                      "registered form and the R2-corrected form give the SAME verdict."
                      if _v2 == v else
                      "So the row's verdict DEPENDS on whether that term is removed."),
                     fmt(dcar["fJ"], 2), v,
                     (_r2t.get("words_per_op_the_price_is_read_on") or 16.0),
                     fmt((_r2t.get("fJ_per_flip") or 0.0) * 2.0, 2)))
        row("C54 C67 C68 C87", "\"about 14 fJ per carry stage\"", v, b, card=cc,
            value_fJ=dcar["fJ"], se_fJ=se_fJ, rail_fJ=dcar.get("rail_fJ"),
            page_fJ=PAGE["e_carry_fJ"], ours_fJ=1.7, curvature=cur,
            e_carry_R2_corrected_fJ=_r2.get("fJ"), e_carry_R2_corrected_se_fJ=_r2.get("se_fJ"),
            e_carry_R2_corrected_verdict=_v2,
            verdict_depends_on_the_R2_term=bool(_v2 != v),
            e_out_add_R2_term=_r2t,
            e_out_add_route=dcar.get("e_out_add_route"),
            e_out_add_registered_fJ=_eoa.get("fJ"), e_out_add_registered_se_fJ=_eoa.get("se_fJ"),
            e_carry_alt_from_family_B_fJ=_alt.get("fJ"),
            e_carry_alt_from_family_B_se_fJ=_alt.get("se_fJ"),
            e_out_add_from_d3z_minus_ein_fxor_fJ=_alt2.get("fJ"),
            method=RULE4_ORDER,
            sensitivity=((cards[cc].get("leak_sensitivity") or {}).get("rows") or {}).get("e_carry"),
            unit_note=("the L vs L log2 L fit prefers %s; on a parallel-prefix adder 'per carry "
                       "stage' is refuted AS A UNIT whatever the number" % cur.get("preferred"))
            if cur else None,
            confirmatory=True, exploratory=False)

    # ---- C47 C55 C69-C73 C88 the Miller law ----------------------------------------------------
    lev = F.get("M_levels")
    ph = D.get("phase_term")
    if not lev and not ph:
        row("C47 C55 C69-C73 C88", "the Miller wire law (k_adj at fixed k)", "not run",
            "family M is absent on %s" % primary, confirmatory=True, exploratory=False)
    else:
        steps = (lev or {}).get("steps") or []
        step_sig = all(s.get("ge_3SE") for s in steps) if steps else None
        rho = (lev or {}).get("spearman_rho")
        # RECON 12: the complement control exists only on the card whose list carries m_nib_c
        # (§6 gives it to aifoundry2 alone), so the row has to say WHERE it was measured, not read
        # "absent" as "agrees".
        comp, comp_card = F.get("M_complement_control") or {}, primary
        if not comp.get("value"):
            for c_ in sorted(cards):
                cc_ = (cards[c_].get("families") or {}).get("M_complement_control") or {}
                if cc_.get("value") is not None:
                    comp, comp_card = cc_, c_
                    break
        comp_ok = None
        if comp.get("value") is not None:
            comp_ok = not bool(ge_zero(abs(comp["value"]), comp.get("se"), comp.get("df")))
        whole = (lev or {}).get("whole_spread") or {}
        spread = whole.get("dW")
        spread_sig = whole.get("ge_3SE")
        ur_m = (whole.get("se") is not None and whole["se"] > PAGE["miller_dW"] / 3.0)
        rho_pp = (lev or {}).get("spearman_rho_per_pass") or {}
        if ur_m:                                            # RECON 6: under-resolved FIRST, always
            v = "under-resolved"
            b = ("the spread's SE %s W exceeds one third of the %.3f W the page's law predicts "
                 "(§9.4), by %s%%" % (fmt(whole.get("se"), 4), PAGE["miller_dW"],
                                      fmt(100.0 * (whole["se"] / (PAGE["miller_dW"] / 3.0) - 1.0), 1)))
            if spread is not None and rho is not None:
                b += ("; for the record the realised spread is %s +- %s W (t %s against the %s window) "
                      "and Spearman rho is %s over %d levels -- the sign is %s the page's law, so "
                      "nothing here supports it even unscored"
                      % (fmt(spread, 4), fmt(whole.get("se"), 4), fmt(whole.get("t"), 2),
                         fmt(whole.get("t_crit_3sigma"), 2), fmt(rho, 2), lev["n_levels"],
                         "OPPOSITE to" if rho < 0 else "with"))
        elif rho is not None and rho >= 0.90 and step_sig and comp_ok:
            v, b = "CONFIRMED", "Spearman rho %.2f over %d distinct k_adj levels, every step >= 3 SE, and the complement pair agrees" % (rho, lev["n_levels"])
        elif spread_sig is False:
            v, b = "REFUTED", ("the whole spread is < 3 SE -> the design did not deliver k_adj and "
                               "nothing about C_gnd vs C_adj can be read from it")
        elif comp_ok is False:
            v, b = "OPEN", ("the complement pair differs by > 3 SE -> not capacitive; reported as a "
                            "pattern-dependent effect of unknown origin")
        else:
            v, b = "OPEN", "neither arm fires cleanly"
        # RECON 12: name the sign reversal and where the complement control lives.
        ctx12 = ("RECON 12: the four k_adj levels are MONOTONE IN THE WRONG DIRECTION. Spearman rho "
                 "over the pass-averaged levels is %s, and the per-pass rho is %s +- %s over %s "
                 "pass(es) -- so this is not one outlier pass. The whole spread is %s +- %s W, and "
                 "the page's law predicts +%.3f W: more adjacency reads LESS power, by %s W. "
                 "A REFUTED verdict here means only 'the design did not deliver k_adj'; it must not "
                 "be read as support for the law%s. The complement control (m_nib vs m_nib_c) exists "
                 "%s -- %s -- because §6 puts m_nib_c on that card's list alone."
                 % (fmt(rho, 3), fmt(rho_pp.get("value"), 3), fmt(rho_pp.get("se"), 3),
                    rho_pp.get("n_passes"), fmt(spread, 4), fmt(whole.get("se"), 4),
                    PAGE["miller_dW"],
                    fmt(abs((spread or 0.0) - PAGE["miller_dW"]), 4),
                    (", and the arm fired at %s%% of its threshold, a thin margin"
                     % fmt(100.0 * abs(whole["t"]) / whole["t_crit_3sigma"], 1))
                    if (whole.get("t") and whole.get("t_crit_3sigma")) else "",
                    ("only on %s" % comp_card) if comp.get("value") is not None else "on NO card",
                    ("%s +- %s W over %s pass(es), %s"
                     % (fmt(comp.get("value"), 4), fmt(comp.get("se"), 4), comp.get("n_passes"),
                        "complement-symmetric within 3 SE" if comp_ok else
                        ("NOT complement-symmetric" if comp_ok is False else "not evaluated")))
                    if comp.get("value") is not None else "so the CONFIRMED arm's second condition "
                                                          "cannot be evaluated at all"))
        row("C47 C55 C69-C73 C88", "the Miller wire law at matched occupancy and counts", v, b,
            levels=lev, whole_spread=whole, every_step_ge_3SE=step_sig, under_resolved=ur_m,
            spearman_rho_pass_averaged=rho, spearman_rho_per_pass=rho_pp,
            monotone_wrong_direction=(lev or {}).get("monotone_wrong_direction"),
            complement_control_card=(comp_card if comp.get("value") is not None else None),
            context=ctx12, method=RULE4_ORDER,
            sensitivity=((C.get("leak_sensitivity") or {}).get("rows") or {}).get("phase_term"),
            phase_term_W=(ph or {}).get("value"), phase_term_se=(ph or {}).get("se"),
            phase_term_page_W=PAGE["miller_dW"], complement_control=comp,
            m_solid_z=F.get("zero_word_replication_miller"),
            note="bit index = physical wire adjacency is an ASSUMPTION, stated in the result, not "
                 "discovered later; the page-exact m_solid_z point is reported only after the "
                 "N-measured zero-word correction and is confounded by construction either way",
            confirmatory=True, exploratory=False)

    # ---- C46 C74 C75 C76 C89 the address path --------------------------------------------------
    cc, dad = pick("e_addr")
    if not dad:
        row("C46 C74 C75 C76 C89", "the 5-bit address bus, predecoder and wordline drivers",
            "not run", "family A is absent: e_addr is NOT IDENTIFIED and the page's 32 fJ x 3 ports "
                       "stands unscored", confirmatory=True, exploratory=False)
    else:
        se_fJ = dad.get("se_fJ")
        ur = under_resolved("e_addr", se_fJ)
        exc = excludes(dad["fJ"], se_fJ, dad["df"], PAGE["e_addr_fJ"])
        # RECON 7: the registered REFUTED arm, "the ladder's slope excludes 32 fJ/bit at >= 3 SE", was
        # written as a CEILING against a 0-2 fJ prior -- the page says the address path costs 32 fJ a
        # bit and the question was whether silicon is cheaper.  A slope FAR ABOVE 32 cannot refute 32
        # from below: it says the ladder is measuring something else.  So the exclusion counts only
        # DOWNWARD, and an exclusion from above makes the row "not measurable as registered".
        exc_down = bool(exc and dad["fJ"] is not None and dad["fJ"] < PAGE["e_addr_fJ"])
        exc_up = bool(exc and dad["fJ"] is not None and dad["fJ"] > PAGE["e_addr_fJ"])
        konst = fam_of(cc, "per_op_constant_between_kernels") or {}
        # the A ladder's own signal in watts, so the kernel-constant spread can be stated as a
        # FRACTION of it rather than compared to a per-bit slope in the wrong units
        _sig = None
        _la = None
        for _k2, _L2 in ((cards[cc].get("ladders")) or {}).items():
            if _L2.get("family") == "A" and _L2.get("zero") == "d5_a0":
                _la = _L2
                break
        if _la and dad.get("value") is not None:
            _rg = [abs(x) for x in (_la.get("regressor_span") or [])] or None
            _it = (cards[cc].get("items") or {})
            _r = (_it.get("d5_a3", {}) or {}).get("rate") or (_it.get("d5_a0", {}) or {}).get("rate")
            _b = None
            for _n2 in ("d5_a3", "d5_a1"):
                if _it.get(_n2, {}).get("regressor_bits_per_op"):
                    _b = max(_b or 0, _it[_n2]["regressor_bits_per_op"])
            if _r and _b:
                _sig = dad["value"] * _b * _r
        # §9 rule 5: name the side.  Tonight the slope is far ABOVE the page's 32 fJ/bit and ~180x the
        # 0-2 fJ prior, so the exclusion refutes the page's number without supporting anything: a
        # quantity this large is not the address path, it is the per-op difference between three
        # different compiled modes (A2.4), which a single free intercept cannot remove.
        side = None
        if dad["fJ"] is not None:
            side = "above" if dad["fJ"] > PAGE["e_addr_fJ"] else "below"
        if ur:                                              # RECON 6: under-resolved FIRST
            v, b = "under-resolved", "SE %s fJ exceeds one third of the 32 fJ separation (§9.4)" % fmt(se_fJ)
            # RECON 7: the row is not scored, and the reading still has to be said, because the wf3
            # build DID score it -- as REFUTED, on an exclusion from the wrong side.
            b += (". RECON 7, for the record: the measured slope is %s +- %s fJ/bit, %sx the page's "
                  "%g fJ/bit and %sx the 0-2 fJ prior's ceiling, so 32 fJ/bit is excluded FROM ABOVE "
                  "(|t| = %s against the %s window). The registered REFUTED arm is a CEILING test -- "
                  "the page claims 32 fJ a bit and the question was whether silicon is cheaper -- so "
                  "an exclusion from above does not answer it and the exclusion is read ONE-SIDED "
                  "DOWNWARD ONLY. Read as 'NOT MEASURABLE AS REGISTERED', with the ladder reported "
                  "descriptively. The wf3 build read this row as REFUTED on that upward exclusion."
                  % (fmt(dad["fJ"], 1), fmt(se_fJ, 1), fmt(dad["fJ"] / PAGE["e_addr_fJ"], 1),
                     PAGE["e_addr_fJ"], fmt(dad["fJ"] / 2.0, 0),
                     fmt(abs(dad["fJ"] - PAGE["e_addr_fJ"]) / se_fJ if se_fJ else None, 1),
                     fmt(t_crit(THREE_SIGMA_P, dad.get("df")) if dad.get("df") else None, 2)))
            if konst.get("largest_same_rate_spread_W") is not None:
                b += (" And on whether it can be e_addr at all: A2.4 fits a0/a1/a3 as ONE "
                      "cross-mode ladder, and those are modes 306/307/308 -- three SEPARATELY "
                      "EMITTED kernels that share one issue rate to 1e-4 but not necessarily one "
                      "per-op constant, which a single free intercept cannot remove (it removes a "
                      "common offset, not a mode-dependent one). Measured size of such a constant: "
                      "zero rungs flip nothing, so two at the SAME issue rate differ only in which "
                      "kernel the build emitted. At the A ladder's own rate (%s) the zero rungs of "
                      "the OTHER families -- %s -- span %s W = %s fJ per address bit on this ladder "
                      "(§9 rule 3: 0.00356 W per fJ/bit), which is %s%% of the ladder's own signal "
                      "of %s W and %s%% of its %s fJ/bit slope. So a kernel-to-kernel constant of "
                      "the size measured ELSEWHERE accounts for part of the slope, not all of it -- "
                      "and it cannot be subtracted, because the A rungs' own spread (%s W over %s) "
                      "is the ladder itself and using it would be circular. The slope is therefore "
                      "an UPPER BOUND on e_addr with an unresolved per-op term inside it, which is "
                      "why no CONFIRMED arm is registered and why this number must not be read as "
                      "e_addr."
                      % (fmt(konst.get("family_A_ladder_ipc"), 4),
                         ", ".join(konst.get("headline_group") or []) or "none",
                         fmt(konst.get("largest_same_rate_spread_W"), 4),
                         fmt(konst.get("largest_same_rate_spread_fJ_per_addr_bit_equiv"), 1),
                         fmt(100.0 * (konst.get("largest_same_rate_spread_W") or 0) / _sig, 0)
                         if _sig else "n/a", fmt(_sig, 3),
                         fmt(100.0 * (konst.get("largest_same_rate_spread_fJ_per_addr_bit_equiv") or 0)
                             / dad["fJ"], 0) if dad.get("fJ") else "n/a",
                         fmt(dad["fJ"], 1),
                         fmt(next((g.get("spread_W") for g in (konst.get("same_rate_groups") or [])
                                   if g.get("is_the_A_ladder_rate")), None), 4),
                         ", ".join(next((g.get("items") for g in (konst.get("same_rate_groups") or [])
                                         if g.get("is_the_A_ladder_rate")), []) or [])))
        elif exc_down:
            v = "REFUTED"
            b = ("the ladder's slope excludes %g fJ/bit at >= 3 SE FROM BELOW (%s +- %s fJ/bit) -> "
                 "the page's \"32 fJ x 3 ports\" is refuted in the direction the arm was written for, "
                 "and the wordline claim is refuted either way, since the same wordline count is "
                 "asserted at every delta"
                 % (PAGE["e_addr_fJ"], fmt(dad["fJ"], 1), fmt(se_fJ, 1)))
        elif exc_up:
            v = "not measurable as registered"
            b = ("RECON 7: the measured slope is %s +- %s fJ/bit -- %sx the page's %g fJ/bit and %sx "
                 "the 0-2 fJ prior's ceiling -- so 32 fJ/bit is excluded FROM ABOVE. The registered "
                 "REFUTED arm is a CEILING test (the page claims 32 fJ a bit; the question was whether "
                 "silicon is cheaper), and an exclusion from above does not answer it: it says this "
                 "ladder is not measuring the address path. The exclusion is therefore read ONE-SIDED "
                 "DOWNWARD ONLY, the row is not scored, and the ladder is reported descriptively."
                 % (fmt(dad["fJ"], 1), fmt(se_fJ, 1), fmt(dad["fJ"] / PAGE["e_addr_fJ"], 1),
                    PAGE["e_addr_fJ"], fmt(dad["fJ"] / 2.0, 0)))
            if konst.get("largest_same_rate_spread_W") is not None:
                b += (" And on whether it can be e_addr at all: A2.4 fits a0/a1/a3 as ONE "
                      "cross-mode ladder, and those are modes 306/307/308 -- three SEPARATELY "
                      "EMITTED kernels that share one issue rate to 1e-4 but not necessarily one "
                      "per-op constant, which a single free intercept cannot remove (it removes a "
                      "common offset, not a mode-dependent one). Measured size of such a constant: "
                      "zero rungs flip nothing, so two at the SAME issue rate differ only in which "
                      "kernel the build emitted. At the A ladder's own rate (%s) the zero rungs of "
                      "the OTHER families -- %s -- span %s W = %s fJ per address bit on this ladder "
                      "(§9 rule 3: 0.00356 W per fJ/bit), which is %s%% of the ladder's own signal "
                      "of %s W and %s%% of its %s fJ/bit slope. So a kernel-to-kernel constant of "
                      "the size measured ELSEWHERE accounts for part of the slope, not all of it -- "
                      "and it cannot be subtracted, because the A rungs' own spread (%s W over %s) "
                      "is the ladder itself and using it would be circular. The slope is therefore "
                      "an UPPER BOUND on e_addr with an unresolved per-op term inside it, which is "
                      "why no CONFIRMED arm is registered and why this number must not be read as "
                      "e_addr."
                      % (fmt(konst.get("family_A_ladder_ipc"), 4),
                         ", ".join(konst.get("headline_group") or []) or "none",
                         fmt(konst.get("largest_same_rate_spread_W"), 4),
                         fmt(konst.get("largest_same_rate_spread_fJ_per_addr_bit_equiv"), 1),
                         fmt(100.0 * (konst.get("largest_same_rate_spread_W") or 0) / _sig, 0)
                         if _sig else "n/a", fmt(_sig, 3),
                         fmt(100.0 * (konst.get("largest_same_rate_spread_fJ_per_addr_bit_equiv") or 0)
                             / dad["fJ"], 0) if dad.get("fJ") else "n/a",
                         fmt(dad["fJ"], 1),
                         fmt(next((g.get("spread_W") for g in (konst.get("same_rate_groups") or [])
                                   if g.get("is_the_A_ladder_rate")), None), 4),
                         ", ".join(next((g.get("items") for g in (konst.get("same_rate_groups") or [])
                                         if g.get("is_the_A_ladder_rate")), []) or [])))
        else:
            v, b = "OPEN", "32 fJ/bit is not excluded at >= 3 SE"
        _Lad = None
        for _k, _L in (cards[cc].get("ladders") or {}).items():
            if _L.get("family") == "A" and _L.get("zero") == "d5_a0":
                _Lad = _L
                break
        row("C46 C74 C75 C76 C89", "energy per toggled register-index bit", v, b, card=cc,
            exclusion_one_sided="downward only (RECON 7): an exclusion from above is read as "
                                "'not measurable as registered', never as REFUTED",
            excluded_from_below=exc_down, excluded_from_above=exc_up,
            per_op_constant_between_kernels=konst, method=RULE4_ORDER,
            measured_ladder_descriptive={
                "gated_slope_fJ_per_bit": dad.get("fJ"), "gated_se_fJ": se_fJ,
                "live_slope_fJ_per_bit": ((cards[cc].get("derived") or {})
                                          .get("e_addr_live") or {}).get("fJ"),
                "note": "reported DESCRIPTIVELY (RECON 7): these are per-op differences between three "
                        "compiled modes plus whatever address energy there is, not e_addr"},
            sensitivity=((cards[cc].get("leak_sensitivity") or {}).get("rows") or {}).get("e_addr"),
            value_fJ=dad["fJ"], se_fJ=se_fJ, rail_fJ=dad.get("rail_fJ"), side_of_32fJ=side,
            times_the_prior_ceiling=(dad["fJ"] / 2.0) if dad["fJ"] is not None else None,
            ladder_rungs=dad.get("rungs"), ladder_modes=dad.get("modes"),
            rate_confounded_excluded=dad.get("rate_confounded_excluded"),
            rate_confounded_rung=(cards[cc].get("families") or {}).get("A_rate_confounded_beside_the_ladder"),
            ladder_free_intercept_W=((_Lad or {}).get("intercept_W") or {}).get("value"),
            live_regime_fJ=((cards[cc].get("derived") or {}).get("e_addr_live") or {}).get("fJ"),
            gated_minus_live=(cards[cc].get("families") or {}).get("A_gated_minus_live_slope"),
            gated_minus_live_at_matched_delta=(cards[cc].get("families") or {}).get("A_gated_minus_live_levels_W"),
            note="no CONFIRMED arm is registered: the family's resolution is ~20 fJ/bit against a "
                 "0-2 fJ prior, so this is a one-sided exclusion, not a measurement. The wordline "
                 "claim is refuted either way, since the same wordline count is asserted at every "
                 "distance. A gated-vs-live difference >= 3 SE means data-path gating reaches the "
                 "address path and the zero-data ladder is a LOWER bound -- read that from the "
                 "MATCHED-DELTA pair (d5_a0/d5n_a0 and d5_a3/d5n_a3), not from the slope difference, "
                 "whose two fits have different forms (the gated ladder is a 2-rung free-intercept "
                 "fit, the live one a single rung through its zero).",
            a2_note="A2.4: the ladder is a0/a1/a3, the three modes that share one rate to 1e-4; a5 "
                    "(mode 309) is excluded by name as rate-confounded and reported beside it. Every "
                    "rung has EVERY data count exactly zero, so the whole step is a per-op difference "
                    "between compiled modes plus whatever address energy there is -- the free "
                    "intercept removes a common offset, not a mode-dependent one. That is why no "
                    "CONFIRMED arm exists and why this number must not be read as e_addr.",
            confirmatory=True, exploratory=False)

    # ---- C79 C80 C90 the zero gate -------------------------------------------------------------
    cc, dz = pick("zero_gate_step")
    if not dz:
        row("C79 C80 C90", "the zero-gate step (d6_one - d6_zero)", "not run",
            "family Z is absent: S3's desk refutation (61x) stands alone", exploratory=False)
    else:
        pj = dz.get("pJ_per_op")
        sep = w3(dz.get("se_pJ_per_op"), dz.get("df")) or 0.0
        ur_g = (dz.get("se_pJ_per_op") is not None and dz["se_pJ_per_op"] > 2.0 / 3.0)
        if pj is None:
            v, b = "OPEN", "no per-op value"
        elif ur_g:
            v, b = "under-resolved", ("SE %s pJ/op exceeds one third of the 2.0 pJ/op separation "
                                      "between the arms (§9.4)" % fmt(dz.get("se_pJ_per_op"), 3))
        elif pj >= PAGE["zero_gate_pJ_per_op"] - sep and pj >= 2.5:
            v, b = "CONFIRMED", "the step is >= 2.5 pJ/op (the page's +8.94 pJ minus 3 SE)"
        elif pj <= 0.5:
            v, b = "REFUTED", ("<= 0.5 pJ/op -> the page's +8.94 pJ is refuted on silicon as well as "
                               "in the catalogue; this reads as \"a null, <= 0.1 W\", not as a "
                               "measurement of 0.147 pJ")
        else:
            v, b = "OPEN", "0.5-2.5 pJ/op"
        # VER 8: this arm is read on the POINT VALUE against a hard 0.5 pJ/op boundary, so the margin
        # decides it and has to be visible.  The boundary is well inside the statistic's own 3-SE
        # window, which means the OPEN band (0.5-2.5 pJ/op) is not excluded.
        _sep = dz.get("se_pJ_per_op")
        _marg = None
        if pj is not None and _sep:
            _tcg = t_crit(THREE_SIGMA_P, dz.get("df")) or 0.0
            _wg = _tcg * _sep
            _marg = ("VER 8, the margin: the step is %s +- %s pJ/op (%s +- %s W) and the REFUTED arm "
                     "is a hard boundary at 0.5 pJ/op, which is %s SE away -- well inside this "
                     "statistic's own 3-SE-equivalent window of +-%s pJ/op (|t| >= %s at %s passes). "
                     "So the verdict rests on the POINT VALUE: the OPEN band 0.5-2.5 pJ/op is NOT "
                     "excluded (its lower edge sits inside the window, which reaches %s pJ/op), while "
                     "the page's %s pJ/op is excluded at %s SE. Read it as \"a null, <= 0.1 W\" with "
                     "an upper bound of %s pJ/op at 3 SE, not as a 3-SE exclusion of the OPEN band."
                     % (fmt(pj, 4), fmt(_sep, 4), fmt(dz.get("value"), 4), fmt(dz.get("se"), 4),
                        fmt(abs(0.5 - pj) / _sep, 2), fmt(_wg, 3), fmt(_tcg, 2),
                        dz.get("n_passes"), fmt(pj + _wg, 3),
                        fmt(PAGE["zero_gate_pJ_per_op"], 2),
                        fmt(abs(PAGE["zero_gate_pJ_per_op"] - pj) / _sep, 1),
                        fmt(pj + _wg, 3)))
        row("C79 C80 C90", "the zero-gate step", v, b, card=cc, under_resolved=ur_g,
            margin=_marg,
            pJ_per_op=pj, se_pJ_per_op=dz.get("se_pJ_per_op"), W=dz.get("value"),
            pJ_per_op_3SE_upper_bound=((pj + (t_crit(THREE_SIGMA_P, dz.get("df")) or 0.0)
                                        * dz["se_pJ_per_op"])
                                       if (pj is not None and dz.get("se_pJ_per_op")) else None),
            SE_to_the_0p5_boundary=((abs(0.5 - pj) / dz["se_pJ_per_op"])
                                    if (pj is not None and dz.get("se_pJ_per_op")) else None),
            page_pJ_per_op=PAGE["zero_gate_pJ_per_op"], ours_pJ_per_op=0.147, exploratory=False)

    # ---- C58 C83 C84 C91 the dipole ------------------------------------------------------------
    cc, dd = pick("dipole_W_vs_E_board_W")
    half = None
    for c_ in [primary] + sorted(cards):
        h = (cards.get(c_, {}).get("derived") or {}).get("half_die_result_path_load_W")
        if h and h.get("value") is not None:
            half = (c_, h)
            break
    if not dd and not half:
        row("C58 C83 C84 C91", "the half-die dipole (tier 1)", "not run",
            "neither family 7 nor family B is present", exploratory=False)
    else:
        eq = near(dd.get("value"), dd.get("se"), dd.get("df"), 0.0) if dd else None
        hv = half[1]["value"] if half else None
        # XCHK 4: §5.0 rule 2 -- a registered interval is read widened by the statistic's own
        # 3-SE-equivalent window.  The hard interval is 0.09 W wide against a ~0.03 W per-item SE on the
        # pinned card, so the arm was unreachable; both readings are reported.
        hok_strict = (1.33 <= hv <= 1.42) if hv is not None else None
        hok = in_interval(hv, half[1].get("se"), half[1].get("df"), 1.33, 1.42) if hv is not None else None
        if eq and hok:
            v = "CONFIRMED"
            b = ("W and E board power are equal within 3 SE (%s +- %s W on %s, 4 contiguous passes) "
                 "and the half-die result-path load lands in [1.33, 1.42] W (%s +- %s W on %s, %s)"
                 % (fmt((dd or {}).get("value"), 4), fmt((dd or {}).get("se"), 4), cc,
                    fmt(hv, 4), fmt(half[1].get("se"), 4), half[0],
                    "inside the interval itself" if hok_strict else
                    "inside it only once widened by its own 3-SE-equivalent window of +-%s W "
                    "(§5.0 rule 2, XCHK 4); the point value is BELOW 1.33 and the page's %s W is "
                    "excluded either way"
                    % (fmt(w3(half[1].get("se"), half[1].get("df")), 3), PAGE["half_die_W"])))
        elif eq is False:
            v, b = "REFUTED", ("the W and E board readings differ by more than 3 SE -> the halves are "
                               "not electrically symmetric, so a constant-total-power dipole is not "
                               "available at all")
        else:
            arms = []
            arms.append("W-vs-E equality: %s" % ("equal within 3 SE" if eq else
                                                 ("not evaluated" if eq is None else "unequal")))
            arms.append("half-die load %s W against [1.33, 1.42]"
                        % ("not measured" if hv is None else fmt(hv, 3)))
            v, b = "OPEN", "one arm of tier 1 is outside its window -- " + "; ".join(arms)
        # RECON 15: the half-die load is reported THREE WAYS, because three defensible readings of
        # the same number exist and the arm's answer differs between them: (a) half of the measured
        # 1/2[(B-A)+(D-C)] combination, which is what this row quotes; (b) e_out x 256 bits/op x rate
        # / 2, the plan's own spelling of the target, which depends on WHICH e_out (the joint fit's or
        # the raw bridge's, now RECON-1-corrected); (c) the strict [1.33, 1.42] W interval against the
        # same number widened by its own 3-SE window (§5.0 rule 2).
        _hv = half[1] if half else {}
        _rate = None
        for c_ in ([half[0]] if half else []):
            _it = (cards.get(c_, {}).get("items") or {})
            for nm_ in ("d2B_h32", "d2B_h16"):
                if _it.get(nm_, {}).get("rate"):
                    _rate = _it[nm_]["rate"]
                    break
        three = {"a_measured_half_of_the_combination_W": _hv.get("value"),
                 "a_se_W": _hv.get("se")}
        for lbl, eo_ in (("b_from_joint_fit_e_out_W", (J.get("coefs") or {}).get("e_out") or {}),
                         ("b_from_raw_bridge_e_out_W", D.get("e_out_bridge") or {})):
            three[lbl] = ((eo_.get("value") * 256.0 * _rate / 2.0)
                          if (eo_.get("value") is not None and _rate) else None)
        three["c_strict_interval_W"] = [1.33, 1.42]
        three["c_in_strict_interval"] = hok_strict
        three["c_in_interval_after_3SE_widening"] = hok
        three["c_3SE_widening_W"] = w3(_hv.get("se"), _hv.get("df")) if _hv else None
        three["note"] = ("RECON 15: (a) is the quoted number; (b) is the plan's own spelling of the "
                         "target, e_out x 256 bits/op x rate / 2, which moves with the e_out chosen; "
                         "(c) is the strict interval against the 3-SE-widened reading. The arm reads "
                         "the same only if all three agree, and they do not have to.")
        ctx15h = ("RECON 15: the half-die load three ways -- measured half-combination %s +- %s W; "
                  "from the joint-fit e_out %s W; from the RECON-1-corrected raw bridge %s W; strict "
                  "[1.33, 1.42] W %s, after its own 3-SE widening of +-%s W %s."
                  % (fmt(three.get("a_measured_half_of_the_combination_W"), 4), fmt(three.get("a_se_W"), 4),
                     fmt(three.get("b_from_joint_fit_e_out_W"), 4),
                     fmt(three.get("b_from_raw_bridge_e_out_W"), 4),
                     "INSIDE" if hok_strict else "OUTSIDE", fmt(three.get("c_3SE_widening_W"), 3),
                     "INSIDE" if hok else "OUTSIDE"))
        # VER 11: the W-vs-E half of this row is measured on the §10(a) dtf-cam block, which is
        # FOUR contiguous passes -- below §9's own 6-pass floor for a confirmatory item -- and at four
        # passes the 3-sigma-equivalent quantile is 9.22, so the equality arm cannot detect an
        # asymmetry of several watts.  Say what it could and could not have seen.
        _cav58 = None
        if dd and dd.get("se"):
            _tc58 = t_crit(THREE_SIGMA_P, dd.get("df")) or 0.0
            _cav58 = ("VER 11, the four-pass caveat on the W-vs-E half: it is measured on the §10(a) "
                      "dtf-cam block, %s pass(es) -- BELOW §9's own 6-pass floor for a confirmatory "
                      "item (\"a genuine 4-pass SE there would be ~1.6x larger ... which is why the "
                      "floor is 6 passes\") -- and at that pass count the 3-sigma-equivalent quantile "
                      "is %s, not 4.53. The reading is %s +- %s W, so \"equal within 3 SE\" means only "
                      "that an asymmetry smaller than %s W was not detected: this arm could not have "
                      "seen a %s W difference, let alone the page's own dipole. It is an absence of "
                      "evidence at low resolution, not an equality."
                      % (dd.get("n_passes"), fmt(_tc58, 2), fmt(dd.get("value"), 4),
                         fmt(dd.get("se"), 4), fmt(_tc58 * dd["se"], 2), fmt(_tc58 * dd["se"], 1)))
        row("C58 C83 C84 C91", "tier 1: dP_card == 0 and the half-die result-path load", v, b,
            caveat=_cav58,
            W_vs_E_n_passes=(dd or {}).get("n_passes"),
            W_vs_E_t_crit_3sigma=(t_crit(THREE_SIGMA_P, dd.get("df"))
                                  if (dd and dd.get("df")) else None),
            W_vs_E_detectable_at_3SE_W=((t_crit(THREE_SIGMA_P, dd.get("df")) or 0.0) * dd["se"]
                                        if (dd and dd.get("se")) else None),
            pass_floor_for_a_confirmatory_item=6,
            half_die_three_ways=three, context=ctx15h,
            card=(dd and cc) or (half and half[0]),
            W_minus_E_board_W=(dd or {}).get("value"), W_minus_E_se=(dd or {}).get("se"),
            half_die_W=hv, half_die_target_W=[1.33, 1.42], page_W=PAGE["half_die_W"],
            half_die_se_W=(half[1].get("se") if half else None),
            half_die_in_window_strict=hok_strict,       # XCHK 4
            half_die_in_window_3se=hok,
            side_amplitudes=(cards.get(cc, {}).get("families") or {}).get("dipole_side_amplitude_W")
            if cc else None,
            tier2="EXPLORATORY, no CONFIRMED/REFUTED arm (§9): the lobe's displacement is reported "
                  "with its permutation p-value; if it does not move ~11 mm the result is the "
                  "voltage regulators, per the thermal hub's own control",
            exploratory=False)

    # ---- C22 C23 C26 the operand law and hart interleaving -------------------------------------
    cc, drho = pick("rho_harts2_over_harts1")
    cc2, dfnot = pick("e_sum_fnot_from_R")
    if not drho:
        row("C22 C23 C26", "rho = (harts-2 per-op delta)/(harts-1 per-op delta) for fand.pi",
            "not run", "family R's fand arms are absent", exploratory=False)
    else:
        one = near(drho["value"], drho.get("se"), drho.get("df"), 1.000)
        destroyed = (in_interval(drho["value"], drho.get("se"), drho.get("df"), 1.119, 1.140))
        if one and not destroyed:
            v, b = "CONFIRMED", ("rho is within 3 SE of 1.000 -> operand sharing SURVIVES "
                                 "interleaving, confirming §0.2 point 2 and the forward agreement "
                                 "of E46 with E60")
        elif destroyed and not one:
            v, b = "REFUTED", ("rho is within 3 SE of 1.12-1.14 -> interleaving destroys sharing, "
                               "the catalogue's split is unidentifiable from --harts 2 data, and the "
                               "page's 6.81:1 is the full-interleave reading by coincidence")
        elif one and destroyed:
            v, b = "OPEN", "both arms satisfied (§9.4 precedence)"
        else:
            v, b = "OPEN", "rho lies between the hypotheses: partial interleaving, fraction quoted"
        frac = None
        if drho.get("value") is not None:
            frac = (drho["value"] - 1.0) / (1.1295 - 1.0)
        # VER 10: both of this row's arms are "within 3 SE of" a point, so the verdict turns on how
        # far 1.000 is from the measurement -- state it.
        _rmarg = None
        if drho.get("value") is not None and drho.get("se"):
            _tcr = t_crit(THREE_SIGMA_P, drho.get("df")) or 0.0
            _t1 = abs(drho["value"] - 1.000) / drho["se"]
            _t12 = abs(drho["value"] - 1.1295) / drho["se"]
            _rmarg = ("VER 10, the margin: rho = %s +- %s W/W on %s passes, so the CONFIRMED arm's "
                      "1.000 is %s SE away and is excluded at %s%% of the %s 3-sigma-equivalent "
                      "threshold, while the REFUTED arm's 1.12-1.14 band is %s SE away (its centre "
                      "1.1295) and is NOT excluded. The arm fires, but on a margin of %s SE past the "
                      "threshold, not comfortably: a realised SE %s%% larger would put 1.000 back "
                      "inside and read OPEN (partial interleaving, fraction %s)."
                      % (fmt(drho["value"], 4), fmt(drho.get("se"), 4), drho.get("n_passes"),
                         fmt(_t1, 2), fmt(100.0 * _t1 / _tcr, 1) if _tcr else "n/a", fmt(_tcr, 2),
                         fmt(_t12, 2), fmt(_t1 - _tcr, 2) if _tcr else "n/a",
                         fmt(100.0 * (_t1 / _tcr - 1.0), 1) if _tcr else "n/a", fmt(frac, 3)))
        # §8.7: E60's [52.00, 53.10] fJ anchor is the PINNED card's (600 MHz, 0.5218 V).  Family R
        # runs only on aifoundry1 card 0 by the §6 lists (800 MHz, 0.604 V), so the comparison goes
        # through that card's measured per-bit tie; both readings are printed, and the raw one alone
        # would spuriously put the model-free fnot leg outside its target.
        # RECON 9: the tie is THIS campaign's measured e_in ratio for that card against the pinned
        # one, not E60's 1.216 / 1.376 from last night.  Both fit forms are reported (§5.2 keeps them
        # apart on purpose), E60's number is kept beside them, and the ratio of the two is checked
        # against §8.7's own 0.88-0.99 card-to-card band.
        tie_meas = measured_tie(cc2) if cc2 else None                  # the no-origin ladder fit
        tie_meas_origin = measured_tie(cc2, "e_in_fxor_E60fit") if cc2 else None
        tie_E60 = E60["per_bit_tie"].get(cc2) if cc2 else None
        tie = tie_meas if tie_meas else (tie_E60 or 1.0)
        tie_ratio = (tie_meas / tie_E60) if (tie_meas and tie_E60) else None
        tgt_lo, tgt_hi = E60["e_sum_fnot_interval_fJ"]
        tgt_scaled = (tgt_lo * tie, tgt_hi * tie)
        fn_in_raw = (in_interval((dfnot or {}).get("fJ"), (dfnot or {}).get("se_fJ"),
                                 (dfnot or {}).get("df"), tgt_lo, tgt_hi) if dfnot else None)
        fn_in_tied = (in_interval((dfnot or {}).get("fJ"), (dfnot or {}).get("se_fJ"),
                                  (dfnot or {}).get("df"), *tgt_scaled) if dfnot else None)
        if dfnot and dfnot.get("fJ") is not None:
            _strict = (tgt_scaled[0] <= dfnot["fJ"] <= tgt_scaled[1])
            _wid = w3(dfnot.get("se_fJ"), dfnot.get("df")) or 0.0
            b += ("; the model-free fnot leg reads %s +- %s fJ on %s, against E60's [%.2f, %.2f] fJ "
                  "scaled by THIS campaign's MEASURED per-bit tie x%s (RECON 9: measured, not E60's "
                  "x%s) to [%.1f, %.1f] -- %s. The page's 128-flip model would read 39.6 fJ and is "
                  "excluded either way"
                  % (fmt(dfnot["fJ"], 2), fmt(dfnot.get("se_fJ"), 2), cc2, tgt_lo, tgt_hi,
                     fmt(tie, 3), fmt(tie_E60, 3), tgt_scaled[0], tgt_scaled[1],
                     ("INSIDE the scaled interval itself, so the real operand law of §0.2 is confirmed"
                      if (fn_in_tied and _strict) else
                      ("INSIDE only once the interval is widened by this statistic's own "
                       "3-SE-equivalent window of +-%s fJ (§5.0 rule 2) -- the POINT VALUE is %s the "
                       "scaled interval, so the leg confirms the law only under the widening, which "
                       "this basis now says out loud"
                       % (fmt(_wid, 2), "below" if dfnot["fJ"] < tgt_scaled[0] else "above"))
                      if fn_in_tied else
                      "OUTSIDE even tie-scaled and widened, so the operand law is not confirmed on "
                      "this leg")))
            b += ("; the tie itself: measured %s (no-origin ladder fit) and %s (with-origin, E60's "
                  "own ec form) against E60's %s, a ratio of %s -- %s §8.7's registered 0.88-0.99 "
                  "card-to-card band, so the scaling is a reported method choice, not a check that "
                  "passed"
                  % (fmt(tie_meas, 3), fmt(tie_meas_origin, 3), fmt(tie_E60, 3), fmt(tie_ratio, 3),
                     "INSIDE" if (tie_ratio is not None and 0.88 <= tie_ratio <= 0.99)
                     else "OUTSIDE"))
        row("C22 C23 C26", "the operand law and hart interleaving", v, b, card=cc,
            margin=_rmarg,
            rho_SE_to_1p000=((abs(drho["value"] - 1.000) / drho["se"]) if drho.get("se") else None),
            rho_SE_to_1p1295=((abs(drho["value"] - 1.1295) / drho["se"]) if drho.get("se") else None),
            rho_t_crit_3sigma=t_crit(THREE_SIGMA_P, drho.get("df")) if drho.get("df") else None,
            rho=drho["value"], rho_se=drho.get("se"), interleave_fraction=frac,
            rho_card=cc, fnot_leg_card=cc2,
            fnot_leg_fJ=(dfnot or {}).get("fJ"), fnot_leg_se_fJ=(dfnot or {}).get("se_fJ"),
            fnot_leg_target_fJ=list(E60["e_sum_fnot_interval_fJ"]),
            fnot_leg_target_tie_scaled_fJ=list(tgt_scaled), fnot_leg_per_bit_tie=tie,
            fnot_leg_per_bit_tie_source="measured this campaign (RECON 9)" if tie_meas else "E60",
            fnot_leg_tie_measured_no_origin=tie_meas,
            fnot_leg_tie_measured_with_origin=tie_meas_origin,
            fnot_leg_tie_E60=tie_E60, fnot_leg_tie_measured_over_E60=tie_ratio,
            fnot_leg_tie_ratio_inside_E60_band=(bool(tie_ratio is not None and 0.88 <= tie_ratio <= 0.99)
                                                if tie_ratio is not None else None),
            fnot_leg_strict_in_scaled_interval=((tgt_scaled[0] <= dfnot["fJ"] <= tgt_scaled[1])
                                                if (dfnot and dfnot.get("fJ") is not None) else None),
            fnot_leg_3SE_widening_fJ=(w3((dfnot or {}).get("se_fJ"), (dfnot or {}).get("df"))
                                      if dfnot else None),
            fnot_leg_in_target_raw=fn_in_raw, fnot_leg_in_target=fn_in_tied,
            fnot_leg_unsubtracted_fJ=(dfnot or {}).get("unsubtracted_fJ"),
            note="separately, (r_not_r1 - r_not_c1) - N's intercept, / 95.556, landing in "
                 "[52.00, 53.10] x the card's per-bit tie +- 3 SE confirms the real operand law and "
                 "refutes the page's 128-flip model (which would read 39.6 fJ)",
            exploratory=False)

    # ---- S10 C16 C59 the rate ------------------------------------------------------------------
    rates = {}
    for c_, Cc in cards.items():
        r = (Cc.get("ipc") or {}).get("reference_mode179_fxor_rot2")
        if r:
            rates[c_] = {"ipc_per_hart": r,                                   # XCHK 8
                         "whole_card_per_s": r * 1024 * (Cc.get("clock_mhz") or 600) * 1e6}
    allnear = all(abs(v["ipc_per_hart"] - E60["rate_per_hart"]) <= 0.01 for v in rates.values()) if rates else None
    # RECON 10: mode 179's own build shift is the finding this row leads with.  The same mode ran
    # 0.5791 ops/cycle/hart in E60's build and 0.6088-0.6089 in tonight's, on all three cards -- a
    # +5.1% shift with no data change at all -- and the shapes that look anomalous depend entirely on
    # which reference is used.  Against the REGISTERED 0.5791, the anomalies are mode 179 itself at
    # +5.1%, un1a (mode 304) at +27.0% and un1b (mode 305) at +30.8%.
    shift_pct = {}
    for c_, Cc in cards.items():
        r_ = (Cc.get("ipc") or {}).get("mode179_build_shift_pct")
        if r_ is not None:
            shift_pct[c_] = round(r_, 3)
    flagged = {}
    for c_, Cc in cards.items():
        for k_, v_ in sorted(((Cc.get("ipc") or {}).get("shapes") or {}).items()):
            if v_.get("flag_gt_1pct"):
                flagged.setdefault(k_, {})[c_] = round(v_.get("vs_its_own_reference_pct") or 0.0, 2)
    # The registered REFUTED arm is "0.579 +- 0.01 on all three cards".  Tonight every card reads
    # 0.6088-0.6089, so that arm does not fire exactly -- and the reason is §7's own registered
    # finding (the same mode runs at a different rate in a different build), not a rate instability.
    # The page's 1.0 IPC is refuted at any of these numbers, and the basis says both.
    pagemul = (float(np.mean([v["ipc_per_hart"] for v in rates.values()])) / PAGE["ipc"]) if rates else None
    # The physics skeptic's finding (wf4/skeptic), re-derived here from the objdump of the binary the
    # campaign ran whenever that file is on disk: the two issue-rate LEVELS A2.1 measured are set by
    # the LOOP HEAD'S ADDRESS MOD 32.  That is what makes the rate a property of the mode -- constant
    # in h to 1e-4 within a mode and identical on all three cards -- and it is why A2.1 had to gate
    # every rate within one mode.  It also explains the one shift this row leads with: mode 179 ran
    # 0.5791 in E60's build and 0.6088 in tonight's with no data change, which is a relink moving a
    # loop head across a fetch boundary, not a rate instability.
    _lh = LOOP_HEAD or {}
    _lh_txt = None
    if _lh.get("one_rate_per_residue"):
        _lh_txt = (
            "WHY THERE ARE TWO LEVELS AT ALL (the physics skeptic, %s -- re-derived here from %s, "
            "not quoted): the level follows the LOOP HEAD'S ADDRESS MOD 32. Over the %d long packed-"
            "vector loops in the binary, the c2 family's four opcodes pin the map one-to-one -- %s -- "
            "so heads at %s (mod 32) issue %s ops per cycle per hart and heads at %s issue %s, a "
            "%s%% difference with NOTHING in the data changing. %s This is an instruction-FETCH "
            "alignment effect: it is why A2.1 found the rate fixed by the mode rather than by h, why "
            "it is identical on all three cards, why every rate gate had to be computed within one "
            "mode, and why the same mode can shift between builds (mode 179's +5.1%% above is a "
            "relink moving its head across a fetch boundary). It is reported, never a gate: §9's own "
            "row says each shape's IPC is a REPORTED quantity."
            % (_lh.get("cite"), _lh.get("source"), _lh.get("n_long_vector_loops") or 0,
               "; ".join("mode %d (%s) head %s, mod 32 = %d, %s ops/cycle/hart"
                         % (m_, r_.get("mnemonic"), r_.get("head"), r_.get("mod32"),
                            r_.get("measured_ops_per_cycle_per_hart"))
                         for m_, r_ in sorted((_lh.get("c2_by_mode") or {}).items())),
               _lh.get("fast_residue"), _lh.get("fast_rate"),
               _lh.get("slow_residue"), _lh.get("slow_rate"),
               ("%.2f" % (100.0 * (_lh["fast_rate"] / _lh["slow_rate"] - 1.0)))
               if (_lh.get("fast_rate") and _lh.get("slow_rate")) else "n/a",
               (("The four df.addr kernels cannot be named a0/a1/a3/a5 from the bytes, so they are a "
                 "COUNT check and it agrees: %d head(s) at the fast residue and %d at the slow, "
                 "against %d of modes 306-309 at the fast rate and %d at the slow."
                 % ((_lh.get("addr_count_check") or {}).get("heads_at_the_fast_residue") or 0,
                    (_lh.get("addr_count_check") or {}).get("heads_at_the_slow_residue") or 0,
                    (_lh.get("addr_count_check") or {}).get("modes_at_the_fast_rate") or 0,
                    (_lh.get("addr_count_check") or {}).get("modes_at_the_slow_rate") or 0))
                if (_lh.get("addr_count_check") or {}).get("agrees") else
                ("The df.addr count check did NOT agree, so only the c2 family's one-to-one map is "
                 "claimed here." if _lh.get("addr_count_check") else ""))))
    elif _lh.get("finding"):
        _lh_txt = "EXTERNAL FINDING: " + _lh["finding"]
    else:
        _lh_txt = ("EXTERNAL FINDING (the physics skeptic, see the wf4/skeptic folder): the two "
                   "issue-rate levels follow the loop head's address mod 32 -- instruction-fetch "
                   "alignment, not the data. The disassembly was not available to this run, so the "
                   "finding is carried by citation and not re-derived.")
    row("S10 C16 C59", "the whole-card instruction rate", "REFUTED" if allnear else ("not run" if not rates else "OPEN"),
        ("the measured rate is %s per hart on every card, 0.579 +- 0.01, not the page's 1.0 IPC"
         % {c: round(v["ipc_per_hart"], 4) for c, v in rates.items()}) if allnear else
        ("RECON 10, the finding first: MODE 179 ITSELF SHIFTED BETWEEN BUILDS. The same mode -- same "
         "pattern, same designed counts -- ran 0.5791 ops per cycle per hart in E60's build and %s in "
         "tonight's, %s, on every card, with no change to the data it touches. So the registered "
         "REFUTED arm ('0.579 +- 0.01 on all three cards') does not fire on its exact number, and the "
         "reason is a build-level issue-rate change, not a rate instability. Measured %s per hart; the "
         "page's 1.0 IPC is refuted at %sx either way. Every shape in this file is now compared "
         "against the REGISTERED 0.5791 (RECON 10: the wf3 build compared against TONIGHT's mode 179, "
         "which hid this shift and flagged the three 0.5814 shapes instead). Shapes off the registered "
         "reference by more than 1%%: %s."
         % ({c: round(v["ipc_per_hart"], 4) for c, v in rates.items()},
            ("+%s%%" % fmt(max(shift_pct.values()), 2)) if shift_pct else "+5.1%",
            {c: round(v["ipc_per_hart"], 4) for c, v in rates.items()}, fmt(pagemul, 3),
            flagged or "none")
         if rates else "no ec rate was recorded"),
        finding=_lh_txt, loop_head_alignment=_lh,
        rates=rates, page_ipc=PAGE["ipc"], measured_over_page_ipc=pagemul,
        E60_reference_ipc=E60["rate_per_hart"],
        mode179_build_shift_pct=shift_pct,
        shapes_off_the_registered_reference_gt_1pct=flagged,
        reference_used_for_the_flag="the REGISTERED 0.5791 (RECON 10)",
        whole_card_per_s={c: v["whole_card_per_s"] for c, v in rates.items()},
        a2_mode_ipc_registered=A2_MODE_IPC,
        per_shape={c: (Cc.get("ipc") or {}).get("shapes") for c, Cc in cards.items()},
        note="each new shape's measured IPC is REPORTED against mode 179's 0.5791 whenever it "
             "differs by more than 1% -- a reported quantity, not a gate",
        exploratory=False)

    # ---- E60's own corner: zero-word gating ----------------------------------------------------
    dzw = D.get("zero_word_term")
    if not dzw:
        row("E60's corner", "zero-operand gating (d1n - d1nz at equal h)", "not run",
            "family N's paired arms are absent on %s" % primary, confirmatory=True, exploratory=False)
    else:
        sig = ge_zero(abs(dzw.get("value") or 0.0), dzw.get("se"), dzw.get("df"))
        # the 2% bound: against the matched delta of the same rung
        hprim = dzw.get("h")
        matched = None
        nm = "d1nz_h%g" % hprim if hprim is not None else None
        if nm and nm in (C.get("items") or {}) and (C["items"][nm].get("d_p80") is not None):
            matched = abs(C["items"][nm]["d_p80"])
        bounded = (matched and dzw.get("value") is not None
                   and abs(dzw["value"]) + (w3(dzw.get("se"), dzw.get("df")) or 0) < 0.02 * matched)
        reps = {}

        # RECON 13: §8.6 registers FOUR replications and §9's OPEN arm is "the four replications are
        # heterogeneous".  Two of them do not exist on the pinned card at all -- d3p_L29 is on
        # aifoundry1 c0's list and m_solid_z on aifoundry2's (§6) -- so the wf3 build ran the
        # heterogeneity check on two members and called it the four.  They are pooled ACROSS CARDS
        # here, each labelled with the card it came from, since the comparison is in fJ per op and
        # §8.7 already makes per-flip energies comparable between cards through the measured tie.
        def _rep(label, d_, rate_item, card_=None):
            if not d_ or d_.get("value") is None:
                return
            card_ = card_ or primary
            rt = ((cards.get(card_, {}).get("items") or {}).get(rate_item, {}) or {}).get("rate")
            reps[label] = {"W": d_.get("value"), "se_W": d_.get("se"), "card": card_,
                           "n_passes": d_.get("n_passes"),
                           "fJ_per_op": (d_["value"] / rt * 1e15) if rt else d_.get("fJ_per_op"),
                           "se_fJ_per_op": (d_["se"] / rt * 1e15) if (rt and d_.get("se")) else None,
                           "opcode": (man.get(rate_item) or {}).get("op")}

        def _rep_anycard(label, famkey, rate_item):
            """the first card that has this replication at all, primary first (RECON 13)"""
            for c_ in [primary] + [x for x in sorted(cards) if x != primary]:
                d_ = ((cards.get(c_, {}).get("families") or {}).get(famkey) or {})
                if d_.get("value") is not None:
                    _rep("%s [%s]" % (label, c_), d_, rate_item, card_=c_)
                    return c_
            return None

        _rep("B 2 g_op + g_res (fand/for) [%s]" % primary, D.get("zero_word_bridge_2gop_gres"), "d2B_h32")
        _card_fadd = _rep_anycard("fadd (d3p - d3)", "zero_word_replication_fadd", "d3p_L29")
        _card_mill = _rep_anycard("miller (m_solid_z - m_phase0)", "zero_word_replication_miller",
                                  "m_solid_z")
        _rep("N primary (d1n - d1nz) [%s]" % primary, dzw,
             "d1n_h%g" % hprim if hprim is not None else "d1n_h16")
        # the spread of the replications against their SEs, in fJ per op -- four opcodes at four
        # rates are not comparable as watts (§8.6), and a heterogeneous set is reported as
        # opcode-dependent rather than pooled into one indicator
        het = []
        keys = sorted(reps)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b_ = reps[keys[i]], reps[keys[j]]
                if a.get("fJ_per_op") is None or b_.get("fJ_per_op") is None \
                        or not a.get("se_fJ_per_op") or not b_.get("se_fJ_per_op"):
                    continue
                t = ((a["fJ_per_op"] - b_["fJ_per_op"])
                     / math.sqrt(a["se_fJ_per_op"] ** 2 + b_["se_fJ_per_op"] ** 2))
                het.append({"pair": [keys[i], keys[j]], "t": t, "unit": "fJ/op"})
        # VER 4: §8.6's "spread of the four against their SEs" is reported in full -- every
        # pairwise t against the 3-sigma-equivalent quantile AND Cochran's Q on k - 1 df -- and
        # NOTHING is pooled into one indicator.  The members are four different opcodes at four
        # different count magnitudes on three cards; a weighted mean of them would be the pooling
        # §8.6 forbids, so none is formed.
        _tc_het = t_crit(THREE_SIGMA_P, dzw.get("df")) or 9e9
        for h_ in het:
            h_["t_crit_3sigma"] = (None if _tc_het >= 9e9 else _tc_het)
            h_["ge_3SE"] = bool(abs(h_["t"]) >= _tc_het)
        hetero = any(h_["ge_3SE"] for h_ in het) if het else None
        _Q, _Qdf, _wm = None, None, None
        _mem = [(k_, reps[k_]) for k_ in sorted(reps)
                if reps[k_].get("fJ_per_op") is not None and reps[k_].get("se_fJ_per_op")]
        if len(_mem) >= 2:
            _w = [1.0 / (d_["se_fJ_per_op"] ** 2) for _, d_ in _mem]
            _y = [d_["fJ_per_op"] for _, d_ in _mem]
            _wm = sum(wi * yi for wi, yi in zip(_w, _y)) / sum(_w)
            _Q = sum(wi * (yi - _wm) ** 2 for wi, yi in zip(_w, _y))
            _Qdf = len(_mem) - 1
            # No p is attached to Q: §8.6 names the statistic as "the spread of the four against
            # their SEs", which is the pairwise t list below, and Q is printed as its one-number
            # summary.  The decision arm is the pairwise comparison, not a chi-square tail.
        het_result = {
            "members_fJ_per_op": dict((k_, {"fJ_per_op": d_.get("fJ_per_op"),
                                            "se_fJ_per_op": d_.get("se_fJ_per_op"),
                                            "card": d_.get("card"), "opcode": d_.get("opcode"),
                                            "n_passes": d_.get("n_passes")})
                                      for k_, d_ in _mem),
            "pairwise": het,
            "t_crit_3sigma": (None if _tc_het >= 9e9 else _tc_het),
            "pairs_over_3SE": [h_["pair"] for h_ in het if h_.get("ge_3SE")],
            "cochran_Q": _Q, "cochran_Q_df": _Qdf,
            "inverse_variance_weighted_mean_fJ_per_op": _wm,
            "weighted_mean_is_not_the_estimate":
                "VER 4 / §8.6: the weighted mean is printed ONLY as the centre the Q statistic is "
                "taken about. It is NOT an estimate and nothing downstream reads it: four opcodes at "
                "four count magnitudes are not pooled into one indicator.",
            "heterogeneous": hetero,
            "reading": ("the set is OPCODE-DEPENDENT (README §8.6 and §9's registered OPEN arm): the "
                        "replications disagree by more than their own SEs allow, so there is no one "
                        "zero-word term to apply across opcodes" if hetero else
                        ("the four replications agree within 3 SE, so a single zero-word term is "
                         "consistent with all of them -- still reported per opcode, not pooled"
                         if hetero is False else "not evaluable: fewer than two members carry an SE")),
            "how": "each replication in fJ per op at its own item's measured rate (§8.6 forbids "
                   "comparing them as watts), every pair as a two-sample t on the between-pass SEs, "
                   "against the 3-sigma-equivalent quantile at df = passes - 1"}
        F["zero_word_heterogeneity"] = het_result
        ur_z = (matched and dzw.get("se") is not None and dzw["se"] > 0.02 * matched / 3.0)
        # RECON 13: the term §8.6 applies is the one its own form fit prefers, so quote that
        # coefficient rather than the raw watt difference at one rung.
        _ff = F.get("zero_word_functional_form") or {}
        _pref = _ff.get("preferred_single_term")
        _pf = ((_ff.get("fits") or {}).get(_pref) or {}) if _pref else {}
        _term = None
        if _pf.get("coef_fJ"):
            _term = {"form": _pref, "terms": _pf.get("terms"),
                     "coef_fJ": _pf.get("coef_fJ"), "coef_se_fJ": _pf.get("coef_se_fJ"),
                     "resid_rms_W": _pf.get("resid_rms_W"), "n_passes": _pf.get("n_passes"),
                     "note": "RECON 13: this is the TERM the §8.6 fit prefers and the one applied "
                             "anywhere the zero-word correction is used -- not the single-rung watt "
                             "difference the row's headline quotes"}
        if ur_z:                                            # RECON 6: under-resolved FIRST, always
            v, b = "under-resolved", ("SE %s W exceeds one third of the rule's separation (2%% of the "
                                      "%s W matched delta) (§9.4)"
                                      % (fmt(dzw.get("se"), 4), fmt(matched, 3)))
        elif sig and not hetero:
            v, b = "CONFIRMED", ("d1n - d1nz >= 3 SE at equal h -> a real zero-operand discount; every "
                                 "page design leaning on an all-zero operand (E-D1b, E-D2 A, E-D3, "
                                 "E-D4 pattern 1, E-D7) is confounded by it")
        elif sig is False and bounded:
            v, b = "REFUTED", ("< 3 SE and bounded below 2% of the matched delta -> E60's ain_h32 "
                               "anomaly was the ladder's sublinearity, not a zero-word skip, and the "
                               "corner closes")
        elif hetero:
            v, b = "OPEN", ("the replications are heterogeneous: reported as opcode-dependent, not "
                            "pooled (§8.6, §9's OPEN arm)")
        else:
            v, b = "OPEN", "between the arms"
        # VER 4: the heterogeneity arm is about the REPLICATION SET, a different quantity from the N
        # primary this row's under-resolved test is read on, so it is stated in its own right at
        # whatever verdict the primary takes.  §9's OPEN column for this row names it explicitly
        # ("or the four replications are heterogeneous -> reported as opcode-dependent, not pooled").
        _rep_set = None
        if het:
            _rep_set = ("VER 4, the replication set, NOT POOLED (§8.6): %d replication(s) across %d "
                        "card(s), each in fJ per op at its own rate -- %s. The heterogeneity check "
                        "FIRES: %s of %d pair(s) differ by >= 3 SE (%s), Cochran's Q = %s on %d df "
                        "about an inverse-variance mean of %s fJ/op that is printed only as Q's "
                        "centre and is read by nothing. So the set is reported as OPCODE-DEPENDENT, "
                        "the README's registered OPEN arm, and no single zero-word term is applied "
                        "across opcodes."
                        % (len(het_result["members_fJ_per_op"]),
                           len({d_.get("card") for d_ in het_result["members_fJ_per_op"].values()}),
                           "; ".join("%s = %s +- %s fJ/op [%s, %s]"
                                     % (k_, fmt(d_.get("fJ_per_op"), 2),
                                        fmt(d_.get("se_fJ_per_op"), 2), d_.get("card"),
                                        d_.get("opcode"))
                                     for k_, d_ in sorted(het_result["members_fJ_per_op"].items())),
                           len(het_result["pairs_over_3SE"]), len(het),
                           "; ".join("%s vs %s |t| %s"
                                     % (h_["pair"][0], h_["pair"][1], fmt(abs(h_["t"]), 2))
                                     for h_ in het if h_.get("ge_3SE")) or "none",
                           fmt(het_result.get("cochran_Q"), 1), het_result.get("cochran_Q_df") or 0,
                           fmt(het_result.get("inverse_variance_weighted_mean_fJ_per_op"), 1)))
            if not hetero:
                _rep_set = _rep_set.replace(
                    "The heterogeneity check FIRES",
                    "The heterogeneity check does NOT fire").replace(
                    "So the set is reported as OPCODE-DEPENDENT, the README's registered OPEN arm, "
                    "and no single zero-word term is applied across opcodes.",
                    "The set is still reported member by member and is not pooled into one "
                    "indicator (§8.6).")
            b += " || " + _rep_set
        ctx13 = ("RECON 13 as VER 4 corrects it: the four replications §8.6 registers are GATHERED "
                 "across cards -- two of them are not on the pinned card's list at all, d3p_L29 "
                 "lives on %s and m_solid_z on %s (§6), so a heterogeneity check run on the primary "
                 "card alone would have two members, not four -- and they are NOT POOLED into one "
                 "indicator. Each is labelled with its card and its opcode and compared in fJ per op, "
                 "never as watts (§8.6). Members gathered (not pooled): %s. The TERM applied wherever "
                 "this correction is used is the form the §8.6 fit prefers, and it comes from the N "
                 "PRIMARY alone, never from the replications: %s = %s +- %s fJ/op%s."
                 % (_card_fadd or "no card", _card_mill or "no card",
                    ", ".join(sorted(reps)) or "none",
                    _pref or "not fitted",
                    fmt((_term or {}).get("coef_fJ", [None])[0] if _term else None, 2),
                    fmt((_term or {}).get("coef_se_fJ", [None])[0] if _term else None, 2),
                    (", against the single-rung headline of %s fJ/op at h = %s"
                     % (fmt(dzw.get("fJ_per_op"), 2), fmt(hprim, 0)))
                    if dzw.get("fJ_per_op") is not None else ""))
        row("E60's corner", "the zero-operand (zero-word) term", v, b, under_resolved=ur_z,
            W=dzw.get("value"), se_W=dzw.get("se"), fJ_per_op=dzw.get("fJ_per_op"), h=hprim,
            matched_delta_W=matched, replications=reps, heterogeneity_t=het,
            replications_pooled_across_cards=False,            # VER 4: §8.6 forbids pooling
            replications_gathered_across_cards=True,
            replication_set=_rep_set, heterogeneity=het_result,
            replication_set_heterogeneous=hetero,
            replication_set_reading=het_result.get("reading"),
            replication_cards={"fadd": _card_fadd, "miller": _card_mill},
            applied_term=_term, context=ctx13, method=RULE4_ORDER,
            sensitivity=((C.get("leak_sensitivity") or {}).get("rows") or {}).get("zero_word_term"),
            functional_form=F.get("zero_word_functional_form"),
            confirmatory=True, exploratory=False)

    # ---- the ladder intercept ------------------------------------------------------------------
    ir = F.get("N_intercept_readings")
    if not ir:
        row("the ladder intercept", "family N's fitted intercept against R1 / R2 / R3", "not run",
            "family N's d1nz ladder is absent on %s" % primary, exploratory=False)
    else:
        matched = ir.get("matched") or []
        xn = F.get("intercept_per_changed_word_W") or {}
        shape_dep = ge_zero(abs((xn.get("X_minus_N") or {}).get("value") or 0.0),
                            (xn.get("X_minus_N") or {}).get("se"),
                            (xn.get("X_minus_N") or {}).get("df"))
        if len(matched) == 1 and not shape_dep:
            v, b = "CONFIRMED", "the intercept matches exactly one reading, %s; the §5.1 corrections are applied under it" % matched[0]
        elif not matched:
            v, b = "REFUTED", ("it matches none of the three -> the sublinearity is not a "
                               "per-changed-word effect; every §5.1 target is reported at both its "
                               "base and its R2 value, and the bridge's e_out is quoted from the "
                               "joint fit alone")
        elif shape_dep:
            v, b = "OPEN", "the X and N intercepts disagree by > 3 SE after scaling by their word counts: shape-dependent"
        else:
            # VER 9: name WHICH OPEN this is.  §9's partition for this row gives CONFIRMED (exactly
            # one reading inside 3 SE), REFUTED (none) and one registered OPEN arm -- "the X and N
            # intercepts disagree by > 3 SE after scaling by their word counts -> shape-dependent".
            # Two readings inside 3 SE is a FOURTH case the partition does not name, which §9 rule 5
            # ("every rule partitions the real line") asks to be said out loud rather than folded
            # into the registered arm.
            v = "OPEN"
            _xm = (xn.get("X_minus_N") or {})
            b = ("OPEN for a reason the §9 partition does NOT name (VER 9): MORE THAN ONE of the "
                 "three readings is inside 3 SE -- %s -- because the measured intercept %s +- %s W "
                 "sits between R1's 0.137 W and R2's 0.273 W and the realised SE covers both. That "
                 "is not the registered OPEN arm. The REGISTERED arm is the X-vs-N disagreement per "
                 "changed word, and it does NOT fire: X per changed source word %s +- %s W against N "
                 "per changed source word %s +- %s W, a difference of %s +- %s W, |t| %s against the "
                 "%s 3-sigma-equivalent window (%s), so the two shapes' intercepts AGREE once scaled "
                 "by their word counts (%g words/op in rot2, %g in the unary shape) and nothing here "
                 "is shape-dependent. Consequence, as §5.1 directs: every §5.1 target is reported at "
                 "both its R1 and its R2 value and the bridge's e_out is quoted from the joint fit."
                 % (matched,
                    fmt((D.get("intercept_N_W") or {}).get("value"), 4),
                    fmt((D.get("intercept_N_W") or {}).get("se"), 4),
                    fmt((xn.get("X") or {}).get("value"), 5), fmt((xn.get("X") or {}).get("se"), 5),
                    fmt((xn.get("N") or {}).get("value"), 5), fmt((xn.get("N") or {}).get("se"), 5),
                    fmt(_xm.get("value"), 5), fmt(_xm.get("se"), 5),
                    fmt(abs(_xm.get("t") or 0.0), 2), fmt(_xm.get("t_crit_3sigma"), 2),
                    "does not fire" if not shape_dep else "FIRES",
                    xn.get("X_words_per_op") or 16.0, xn.get("N_words_per_op") or 8.0))
        # RECON 5: this is the row the leakage slope actually decides, so it prints BOTH slopes.
        LS = C.get("leak_sensitivity") or {}
        bys = LS.get("N_intercept_by_slope") or {}
        if bys:
            b += ("; RECON 5, the leakage-slope arm: §8.1 corrects each run with the card's own "
                  "FITTED slope, and E60 fitted %s W/C on this card, an order of magnitude larger "
                  "(the die sensor steps in whole degrees, so only %s%% of runs qualify for the "
                  "within-run drift fit). The intercept and therefore THIS ROW move with that choice: "
                  "%s. The per-flip prices do not (see leak_sensitivity). The verdict above is read at "
                  "the FITTED slope, which §8.1 registers; the reading at E60's slope is reported "
                  "beside it and is not scored."
                  % (fmt(LS.get("k_E60_W_per_C"), 3), fmt(LS.get("k_fitted_qualifying_pct"), 0),
                     "; ".join("k = %s W/C -> intercept %s +- %s W, matches %s"
                               % (fmt((LS.get("k_W_per_C") or {}).get(nm_), 3),
                                  fmt((bys.get(nm_) or {}).get("intercept_W"), 4),
                                  fmt((bys.get(nm_) or {}).get("se_W"), 4),
                                  ((bys.get(nm_) or {}).get("matched") or "NONE"))
                               for nm_ in ("fitted", "zero", "E60") if nm_ in bys)))
        row("the ladder intercept", "E60's +0.273 W, per changed word", v, b,
            open_arm=("the registered OPEN arm (X and N intercepts disagree by > 3 SE per changed "
                      "word) FIRES" if shape_dep else
                      ("UNNAMED by the §9 partition: more than one reading is inside 3 SE, while the "
                       "registered OPEN arm (X vs N per changed word) does not fire"
                       if len(matched) > 1 else None)),
            X_minus_N_per_changed_source_word_W=(xn.get("X_minus_N") or {}).get("value"),
            X_minus_N_per_changed_source_word_se_W=(xn.get("X_minus_N") or {}).get("se"),
            X_minus_N_t=(xn.get("X_minus_N") or {}).get("t"),
            X_minus_N_t_crit_3sigma=(xn.get("X_minus_N") or {}).get("t_crit_3sigma"),
            registered_open_arm_fires=bool(shape_dep),
            intercept_N_W=(D.get("intercept_N_W") or {}).get("value"),
            intercept_N_se=(D.get("intercept_N_W") or {}).get("se"),
            intercept_X_W=(D.get("intercept_X_W") or {}).get("value"),
            by_leakage_slope=bys, leak_k_fitted=C.get("leak_W_per_C"),
            leak_k_E60=LS.get("k_E60_W_per_C"),
            leak_k_fitted_from_n_runs=LS.get("k_fitted_from_n_runs"),
            leak_primary="the fitted slope (§8.1)",
            sensitivity=(LS.get("rows") or {}).get("intercept_N_W"),
            readings=ir, per_changed_word=xn, exploratory=False)

    # ---- RECON 15: the method choices, stated once, in one place ------------------------------
    # Several numbers above are one of two or three defensible readings of the same data.  §5.2 keeps
    # the fit forms apart on purpose, so the choice has to be visible rather than implied by whichever
    # field a row happened to read.
    _ladA = None
    for _k, _L in (C.get("ladders") or {}).items():
        if _L.get("family") == "A" and _L.get("zero") == "d5_a0":
            _ladA = _L
            break
    if _ladA is None:
        for _c in sorted(cards):
            for _k, _L in ((cards[_c].get("ladders")) or {}).items():
                if _L.get("family") == "A" and _L.get("zero") == "d5_a0":
                    _ladA = _L
                    break
            if _ladA:
                break
    _A_no = ((_ladA or {}).get("slope") or {})
    _A_or = ((_ladA or {}).get("slope_zero_point") or {})
    _ties = {}
    for _c in sorted(cards):
        if _c == "aifoundry3" or "[" in _c:
            continue
        _t1, _t2 = measured_tie(_c), measured_tie(_c, "e_in_fxor_E60fit")
        _tE = E60["per_bit_tie"].get(_c)
        _ties[_c] = {"measured_no_origin": (round(_t1, 4) if _t1 else None),
                     "measured_with_origin": (round(_t2, 4) if _t2 else None),
                     "E60": _tE,
                     "measured_over_E60": (round(_t1 / _tE, 4) if (_t1 and _tE) else None),
                     "inside_the_0.88_0.99_band": (bool(0.88 <= _t1 / _tE <= 0.99)
                                                   if (_t1 and _tE) else None)}
    _hw = None
    for _c in [primary] + sorted(cards):
        _h = (cards.get(_c, {}).get("derived") or {}).get("half_die_result_path_load_W")
        if _h and _h.get("value") is not None:
            _hw = (_c, _h)
            break
    mrow = {
        "family_A_with_or_without_the_origin": {
            "free_intercept_fJ_per_bit": _A_no.get("fJ"), "free_intercept_se_fJ": _A_no.get("se_fJ"),
            "with_origin_fJ_per_bit": _A_or.get("fJ"), "with_origin_se_fJ": _A_or.get("se_fJ"),
            "chosen": "the FREE-INTERCEPT fit (the plan's §8.4 form), because every A rung has every "
                      "data count exactly zero and the intercept is the only thing that can absorb "
                      "the kernels' common per-op offset",
            "note": "the two differ by %s fJ/bit, far more than either SE, which is itself the "
                    "reason C46 is read as 'not measurable as registered' (RECON 7)"
                    % fmt(abs((_A_or.get("fJ") or 0) - (_A_no.get("fJ") or 0)), 1)},
        "the_cross_card_tie": {
            "ties": _ties,
            "chosen": "THIS campaign's measured e_in ratio from the NO-ORIGIN ladder fit (RECON 9), "
                      "with the with-origin reading and E60's published tie printed beside it",
            "note": "E60's 20.83 +- 0.10 fJ anchor came from the WITH-ORIGIN form (§5.2), so a tie "
                    "built from no-origin fits is self-consistent within this campaign but is not "
                    "E60's number; both are reported wherever a target is tie-scaled"},
        "the_half_die_load": {
            "card": (_hw[0] if _hw else None),
            "three_ways": "see the C58 row's half_die_three_ways: (a) half the measured "
                          "1/2[(B-A)+(D-C)] combination, (b) e_out x 256 bits/op x rate / 2 from the "
                          "joint fit and from the RECON-1-corrected raw bridge, (c) the strict "
                          "[1.33, 1.42] W interval against the same number widened by its own 3-SE "
                          "window (§5.0 rule 2, XCHK 4)",
            "chosen": "(a) as the quoted number, with (b) and (c) printed; the arm's answer is stated "
                      "for the strict reading AND the widened one"},
        "the_leakage_slope": {
            "primary": "the card's own FITTED slope (§8.1)",
            "arms": "k = 0 and E60's fitted slope for the card, on every quantity -- see each card's "
                    "leak_sensitivity block and the ladder-intercept row",
            "chosen": "fitted, as registered; the arm exists because tonight's fit and E60's differ "
                      "by an order of magnitude and the N-ladder intercept moves with it"},
        "rule_4_ordering": RULE4_ORDER,
        "e_out_for_C56": "the joint-fit e_out, which the registered rule names, with the raw 2 x 2 "
                         "beside it (RECON 3)",
        "e_out_add_for_e_carry": "from d3z, the same opcode and shape and pass, minus e_in from the "
                                 "same c2 shape's d2A, as §4 registers (RECON 4); the family-B import "
                                 "is printed as an alternative, and because d3z has one nonzero rung "
                                 "the registered form carries the §5.1 changed-word term, so the "
                                 "R2-corrected value is printed beside it and the verdict stated for "
                                 "both",
        "d2A_rung_and_fit_form_for_C14": "the h = 32 delta / 8h, as the row's own rule spells it, with "
                                         "every rung and every fit form printed because the arm sits "
                                         "at the interval's edge (RECON 11)",
    }
    # RECON 15: this is NOT a claim row -- it carries no arm and no verdict -- so it leaves the §9
    # list and main() lifts it into its own section.  Keeping it in `verdicts` would have made
    # "every §9 row carries a verdict" false by construction.
    out.append({"claims": "method", "not_a_claim_row": True,
                "quantity": "the choices this reduction made where more than one reading is "
                            "defensible",
                "verdict": None, "card": primary,
                "basis": "RECON 15: stated so a reader can tell a method choice from a measurement. "
                         "Each entry names the alternatives, the one chosen and why.",
                "method_choices": mrow, "exploratory": False})
    return out


# =================================================================================================
# reduce.txt
# =================================================================================================
def report(res, man):
    L = []
    w = L.append
    w("V3-DTF (E61) reduction -- %s" % res["meta"]["generated"])
    w("manifest %s (%d items, seed %s)" % (res["meta"]["manifest"], res["meta"]["n_manifest_items"],
                                           res["meta"]["seed"]))
    w("pass dirs: %d (%s); primary card %s" % (len(res["meta"]["dirs"]),
                                               ", ".join(res["meta"]["experiments"]),
                                               res["meta"].get("primary_card")))
    w("§9.1 a \"3 SE\" window is the two-sided t quantile at p = %.4f on the between-pass scatter, "
      "df = passes - 1:" % THREE_SIGMA_P)
    w("     " + ",  ".join("%d passes |t| >= %s" % (k, fmt(t_crit(THREE_SIGMA_P, k - 1), 2))
                           for k in (4, 6, 8, 9, 10)))
    w("§9.2 the confirmatory five (%s) are Holm-corrected at alpha = %s; everything else is "
      "exploratory." % (", ".join(CONFIRMATORY), HOLM_ALPHA))
    w("Departures from the plan for tonight's build: " + "; ".join(res["meta"]["departures"]))
    w("")
    if res.get("missing"):
        w("== WHAT IS MISSING (%d) ==" % len(res["missing"]))
        for m in res["missing"]:
            w("  - %s" % m)
        w("")
    if res.get("smoke"):
        w("== smoke blocks (not in the analysis) ==")
        for c, s in sorted(res["smoke"].items()):
            w("  %-22s %d runs, cold start_c %s, ok %s, participants %s, items %s"
              % (c, s["n_runs"], s["start_c"], s["all_ok"], s["participants"], ",".join(s["items"])))
        w("")
    for card in sorted(res["cards"]):
        C = res["cards"][card]
        g = C.get("gates") or {}
        w("=" * 100)
        w("== %s: %s MHz, %s mV, passes %s (registered %s), runs kept %s/%s, leak %s W/C (%s; E60 %s)"
          % (card, C.get("clock_mhz"), fmt((C.get("v_mean") or 0) * 1000, 1), C.get("passes"),
             C.get("n_passes_registered"), g.get("kept"), g.get("runs"),
             fmt(C.get("leak_W_per_C")),
             "%s runs%s" % (C.get("leak_runs"), " -- FALLBACK, no run drifted >= 1 C"
                            if C.get("leak_is_fallback") else ""),
             C.get("leak_E60_W_per_C")))
        if C.get("note"):
            w("   !! %s" % C["note"])
            continue
        if C.get("excluded_a3"):
            w("   amendment A3, excluded by name: %s %s" % (C["excluded_a3"], C.get("excluded_a3_detail")))
        if C.get("passes_set_aside"):
            for s in C["passes_set_aside"]:
                w("   pass %s SET ASIDE: %s" % (s["pass"], "; ".join(s["why"])))
        else:
            w("   no pass set aside (threshold: >5%% of runs AND >=2 runs failing a gate [RECON 2], "
              "or drift >%s W/5min)"
              % fmt(C.get("drift_threshold_W_per_5min")))
        if C.get("pair_gate_voids"):
            for v in C["pair_gate_voids"]:
                w("   pair gate VOID: pass %s group %s spread %.4f%%" % (v["pass"], v["group"], 100 * v["spread"]))
        rg = C.get("rate_gate") or {}
        if rg.get("rate_confounded_items"):
            w("   A2.4 excluded by name as rate-confounded (reported beside its ladder, NOT a gate "
              "failure): %s" % ", ".join(rg["rate_confounded_items"]))
        for k, v in sorted((rg.get("cross_mode_rate_ratios_reported_not_gated") or {}).items()):
            w("   A2.1 cross-mode rate ratio, REPORTED not gated: %-22s mode %s vs %s  %+.3f%% over "
              "%d pass(es)%s"
              % (k, v.get("mode"), v.get("zero_mode"), v.get("pct"), v.get("n_passes"),
                 "  <-- rate-confounded by name" if v.get("rate_confounded_by_name") else ""))
        if C.get("launch_gate_skipped"):
            lg = C["launch_gate_skipped"]
            w("   FIX.7 the launch-reading gate does NOT apply here: %s" % lg["reason"])
            w("        realised start_c %s-%s C (mean %s), every launch on-protocol: %s"
              % (fmt(lg.get("start_c_min"), 0), fmt(lg.get("start_c_max"), 0),
                 fmt(lg.get("start_c_mean"), 1), lg.get("on_protocol_all")))
        for pl in (C.get("pair_links_crossing_mode") or []):
            w("   A2.1 the manifest's `pair` link %s crosses modes %s: SPLIT by mode, so the 0.2%% "
              "gate never compares two opcodes"
              % (pl.get("declared_group"), sorted(pl.get("modes") or {})))
        w("   gate failures: %d of %d runs after A3 (%.2f%%)"
          % (len(g.get("failed") or []), g.get("runs_after_a3") or 0,
             100 * (g.get("fail_rate") or 0.0)))
        if g.get("failed"):
            for p, item, pos, why in g["failed"][:40]:
                w("     pass %s %-12s pos %-3s %s" % (p, item, pos, "; ".join(why)))
            if len(g["failed"]) > 40:
                w("     ... %d more" % (len(g["failed"]) - 40))
        if C.get("dup_repeat_spread_W"):
            w("   within-pass repeat spread (§8.10): " +
              ", ".join("%s %.3f W (max %.3f)" % (n, v["mean"], v["max"])
                        for n, v in sorted(C["dup_repeat_spread_W"].items())))
        ipc = C.get("ipc") or {}
        if ipc.get("reference_mode179_fxor_rot2"):
            w("   IPC per shape (reference mode 179 = %.4f, E60 %.4f):"
              % (ipc["reference_mode179_fxor_rot2"], E60["rate_per_hart"]))
            for k, v in sorted((ipc.get("shapes") or {}).items()):
                w("     %-42s %.4f  %s%s"
                  % (k, v["ipc"],
                     ("%+.2f%%" % v["vs_mode179_pct"]) if v.get("vs_mode179_pct") is not None else "n/a",
                     "   <-- >1%, reported (§9)" if v.get("flag_gt_1pct") else ""))
        w("   -- derived quantities (value, SE, rail, passes, identifying family) --")
        for name in sorted(C.get("derived") or {}):
            d = C["derived"][name]
            if d.get("not_identified"):
                # §8.5 / §8.11: a quantity whose identifying contrast is absent is named, with its
                # reason and any bound, and never printed as "n/a +- n/a".
                w("     %-26s NOT IDENTIFIED  [%s]" % (name.replace("_not_identified", ""),
                                                       d.get("family")))
                w("%s why: %s" % (" " * 33, d.get("note") or d.get("identified_by")))
                for bk, lbl in (("rate_free_per_rung_bound_fJ_per_cell_bit", "bound, fJ per cell bit"),
                                ("n_rungs", "nonzero rungs in the ladder")):
                    if d.get(bk) is not None:
                        w("%s %s: %s" % (" " * 33, lbl, fmt(d[bk], 3)))
                continue
            if d.get("unit", "").startswith("J"):
                w("     %-26s %9s +- %-7s fJ   rail %8s fJ  (%s)  n=%s  [%s]"
                  % (name, fmt(d.get("fJ"), 3), fmt(d.get("se_fJ"), 3), fmt(d.get("rail_fJ"), 3),
                     ("rail %s fF / %s e- (1/2CV^2), %s fF (CV^2)"
                      % (fmt((d.get("rail") or {}).get("C_fF_halfCV2"), 1),
                         fmt((d.get("rail") or {}).get("electrons_halfCV2"), 0),
                         fmt((d.get("rail") or {}).get("C_fF_CV2"), 1)))
                     if (d.get("rail") or {}).get("C_fF_halfCV2") else "no rail leg",
                     d.get("n_passes"), d.get("family")))
                if d.get("t") is not None:
                    w("%s t = %.2f (df %s, 3-sigma |t| >= %s, p = %s)%s"
                      % (" " * 33, d["t"], d.get("df"), fmt(d.get("t_crit_3sigma"), 2),
                         fmt(d.get("p_two"), 6),
                         "  robust SE %s fJ" % fmt((d.get("se_robust") or 0) * 1e15, 3)
                         if d.get("se_robust") else ""))
            else:
                extra = ""
                for k in ("fJ_per_op", "pJ_per_op", "excess_over_fit_fJ_per_op", "ratio"):
                    if d.get(k) is not None:
                        extra = "  %s %s" % (k, fmt(d[k], 4))
                w("     %-26s %9s +- %-8s %-6s rail %8s   n=%s  [%s]%s"
                  % (name, fmt(d.get("value"), 4), fmt(d.get("se"), 4), d.get("unit"),
                     fmt(d.get("rail_value"), 4), d.get("n_passes"), d.get("family"), extra))
                if d.get("t") is not None:
                    w("       %st = %.2f (df %s, 3-sigma window |t| >= %s, p = %s)"
                      % (" " * 26, d["t"], d.get("df"), fmt(d.get("t_crit_3sigma"), 2),
                         fmt(d.get("p_two"), 5)))
        if C.get("ladders"):
            w("   -- the ladders (§8.4), one per family/opcode/zero --")
            for k in sorted(C["ladders"]):
                Ld = C["ladders"][k]
                w("     %-26s %-18s %s form, %d rung(s) %s"
                  % (k, Ld["regressor"], Ld["fit_form"], Ld["n_rungs"], Ld["rungs"]))
                w("        first rung %s: %s +- %s W"
                  % (Ld.get("first_rung"), fmt((Ld.get("first_rung_step_W") or {}).get("value"), 4),
                     fmt((Ld.get("first_rung_step_W") or {}).get("se"), 4)))
                w("        slope %9s +- %-8s fJ   intercept %9s +- %-8s W   resid rms %s W"
                  % (fmt((Ld.get("slope") or {}).get("fJ"), 3),
                     fmt((Ld.get("slope") or {}).get("se_fJ"), 3),
                     fmt((Ld.get("intercept_W") or {}).get("value"), 4),
                     fmt((Ld.get("intercept_W") or {}).get("se"), 4),
                     fmt(Ld.get("residual_rms_W"), 4)))
                if Ld.get("slope_zero_point"):
                    w("        E60's own ec fit ((0,0) included): %s +- %s fJ"
                      % (fmt(Ld["slope_zero_point"].get("fJ"), 3),
                         fmt(Ld["slope_zero_point"].get("se_fJ"), 3)))
                if Ld.get("slope_single"):
                    w("        single-rung passes (slope through the zero): %s +- %s fJ"
                      % (fmt(Ld["slope_single"].get("fJ"), 3),
                         fmt(Ld["slope_single"].get("se_fJ"), 3)))
                if Ld.get("excluded_zero_word_mismatch"):
                    w("        excluded (zero-word mismatch with the zero rung): %s"
                      % Ld["excluded_zero_word_mismatch"])
                if Ld.get("zero_word_inhomogeneous"):
                    w("        NB: every rung's zero-word flag differs from the zero rung's, so this "
                      "slope CONTAINS the zero-word step (%s)" % Ld["zero_word_inhomogeneous"])
        if C.get("warnings"):
            for x in sorted(set(C["warnings"])):
                w("   !! %s" % x)
        F = C.get("families") or {}
        LS = C.get("leak_sensitivity") or {}
        if LS.get("rows"):
            w("   -- RECON 5 the leakage-slope arm (primary: %s) --" % LS.get("primary"))
            w("     k W/C: fitted %s (from %s run(s), %s%% of them) | zero 0.000 | E60 %s"
              % (fmt((LS.get("k_W_per_C") or {}).get("fitted"), 4), LS.get("k_fitted_from_n_runs"),
                 fmt(LS.get("k_fitted_qualifying_pct"), 0), fmt(LS.get("k_E60_W_per_C"), 3)))
            w("     %-32s %17s %11s %11s   %s"
              % ("quantity", "fitted", "k=0", "E60", "E60-fitted, in SE"))
            for k_, r_ in sorted(LS["rows"].items()):
                w("     %-32s %9s+-%-7s %11s %11s   %s  %s"
                  % (k_, fmt((r_.get("fitted") or {}).get("value"), 3),
                     fmt((r_.get("fitted") or {}).get("se"), 3),
                     fmt((r_.get("zero") or {}).get("value"), 3),
                     fmt((r_.get("E60") or {}).get("value"), 3),
                     fmt(r_.get("E60_minus_fitted_in_SE"), 2),
                     "MOVES" if r_.get("moves") else ""))
            w("     quantities the arm MOVES (>= 1 SE): %s"
              % (", ".join(LS.get("quantities_the_arm_moves") or []) or "none"))
            for nm_, rr_ in sorted((LS.get("N_intercept_by_slope") or {}).items()):
                w("     N intercept at k=%-6s %8s +- %-7s W   matches %s"
                  % (nm_, fmt(rr_.get("intercept_W"), 4), fmt(rr_.get("se_W"), 4),
                     rr_.get("matched") or "NONE"))
        if F.get("e_cell_scaling_test"):
            t_ = F["e_cell_scaling_test"]
            w("   -- RECON 8 e_cell's scaling test (h = %s against h = %s) --"
              % (fmt(t_.get("rung_low_h"), 0), fmt(t_.get("rung_high_h"), 0)))
            w("     fJ per cell bit: %s +- %s at h%s | %s +- %s at h%s  -> paired difference %s +- %s "
              "(ratio of means %s, %s%%), proportional within 3 SE: %s"
              % (fmt((t_.get("fJ_per_cell_bit_at_low_h") or {}).get("value"), 3),
                 fmt((t_.get("fJ_per_cell_bit_at_low_h") or {}).get("se"), 3),
                 fmt(t_.get("rung_low_h"), 0),
                 fmt((t_.get("fJ_per_cell_bit_at_high_h") or {}).get("value"), 3),
                 fmt((t_.get("fJ_per_cell_bit_at_high_h") or {}).get("se"), 3),
                 fmt(t_.get("rung_high_h"), 0),
                 fmt((t_.get("per_bit_difference_high_minus_low") or {}).get("value"), 3),
                 fmt((t_.get("per_bit_difference_high_minus_low") or {}).get("se"), 3),
                 fmt((t_.get("per_bit_ratio_high_over_low") or {}).get("value"), 3),
                 fmt(t_.get("per_bit_change_pct"), 1), t_.get("proportional_within_3SE")))
            w("     per-op step: %s +- %s fJ at h%s -> %s +- %s fJ at h%s, a growth of %sx where a "
              "proportional law needs %sx"
              % (fmt((t_.get("fJ_per_op_at_low_h") or {}).get("value"), 3),
                 fmt((t_.get("fJ_per_op_at_low_h") or {}).get("se"), 3), fmt(t_.get("rung_low_h"), 0),
                 fmt((t_.get("fJ_per_op_at_high_h") or {}).get("value"), 3),
                 fmt((t_.get("fJ_per_op_at_high_h") or {}).get("se"), 3), fmt(t_.get("rung_high_h"), 0),
                 fmt((t_.get("per_op_growth_high_over_low") or {}).get("value"), 3),
                 fmt(t_.get("per_op_growth_a_proportional_law_needs"), 2)))
        if F.get("per_op_constant_between_kernels"):
            k_ = F["per_op_constant_between_kernels"]
            w("   -- RECON 7 the per-op constant between separately emitted kernels --")
            for g in (k_.get("same_rate_groups") or []):
                w("     ipc %-7s%s %s" % (fmt(g.get("ipc"), 4),
                                          "(the A ladder's rate)" if g.get("is_the_A_ladder_rate")
                                          else "                     ",
                                          ", ".join(g.get("items") or [])))
                w("        all of them    spread %8s W = %8s fJ per address bit"
                  % (fmt(g.get("spread_W"), 4), fmt(g.get("spread_fJ_per_addr_bit_equiv"), 1)))
                if g.get("spread_W_outside_family_A") is not None:
                    w("        outside fam A  spread %8s W = %8s fJ per address bit   (%s)"
                      % (fmt(g.get("spread_W_outside_family_A"), 4),
                         fmt(g.get("spread_fJ_per_addr_bit_equiv_outside_family_A"), 1),
                         ", ".join(g.get("items_outside_family_A") or [])))
            w("     HEADLINE (the comparison that is not circular): %s W = %s fJ/address bit, over %s"
              % (fmt(k_.get("largest_same_rate_spread_W"), 4),
                 fmt(k_.get("largest_same_rate_spread_fJ_per_addr_bit_equiv"), 1),
                 ", ".join(k_.get("headline_group") or []) or "nothing"))
            w("     %s" % k_.get("headline_basis"))
        if F.get("N_intercept_readings"):
            r = F["N_intercept_readings"]
            w("   -- §5.1 the intercept's mechanism (scale vs the pinned card: %.3f) --" % r["scale_vs_600MHz_pinned"])
            for k, v in sorted(r["readings"].items()):
                w("     %-26s target %7s W   t %8s   inside 3 SE: %s"
                  % (k, fmt(v["target_W"], 3), fmt(v["t"], 2), v["within_3sigma"]))
            w("     matched: %s" % (r["matched"] or "NONE"))
        if F.get("zero_word_functional_form"):
            z = F["zero_word_functional_form"]
            w("   -- §8.6 the zero-word functional form --")
            for k, v in sorted(z["fits"].items()):
                w("     %-18s resid rms %8s W  %s" % (k, fmt(v["resid_rms_W"], 4),
                   ", ".join("%s %s +- %s" % (t, fmt(c, 2), fmt(e, 2))
                             for t, c, e in zip(v.get("terms") or [], v.get("coef_fJ") or [],
                                                v.get("coef_se_fJ") or []))))
            w("     preferred single term: %s" % z.get("preferred_single_term"))
        if F.get("gate_spread"):
            gs = F["gate_spread"]
            w("   -- the gate ladder (e_in + e_out per opcode, matched counts and port count) --")
            for n, d in sorted((F.get("gate_ladder") or {}).items()):
                w("     %-12s %-9s %9s +- %-7s fJ   depth rank %s"
                  % (n, d.get("op"), fmt(d.get("e_sum_fJ"), 2), fmt(d.get("e_sum_se_fJ"), 2),
                     d.get("gate_depth_rank")))
            w("     spread %s fJ (t %s, 3-sigma |t| >= %s), monotone in depth: %s"
              % (fmt(gs.get("spread_fJ"), 2), fmt(gs.get("t"), 2), fmt(gs.get("t_crit_3sigma"), 2),
                 gs.get("monotone_in_depth")))
        if F.get("V_arms") or F.get("V_pairs"):
            w("   -- family V (A2.3): each arm's per-flip slope against its OWN zero, then the "
              "difference --")
            ni = (C.get("derived") or {}).get("e_cell_not_identified")
            if ni:
                w("     e_cell NOT IDENTIFIED here: %s" % ni["note"])
                if ni.get("rate_free_per_rung_bound_fJ_per_cell_bit") is not None:
                    w("     rate-free per-rung BOUND at %s: %s fJ per cell bit"
                      % (ni.get("rate_free_per_rung_bound_at"),
                         fmt(ni["rate_free_per_rung_bound_fJ_per_cell_bit"], 3)))
            for tag in ("1A", "1B"):
                a_ = ((F.get("V_arms") or {}).get(tag) or {})
                s_ = a_.get("slope") or {}
                if s_:
                    w("     %-3s mode %-4s zero %-8s h %-12s slope %9s +- %-7s fJ per port+result bit"
                      % (tag, a_.get("mode"), a_.get("zero"),
                         ",".join(fmt(x, 0) for x in (a_.get("h") or [])),
                         fmt(s_.get("fJ"), 3), fmt(s_.get("se_fJ"), 3)))
            sd = F.get("V_slope_difference_per_portresult_bit") or {}
            ec = (C.get("derived") or {}).get("e_cell") or {}
            if sd:
                w("     1B - 1A  %9s +- %-7s fJ per port+result bit  x %s (= port+result bits / cell "
                  "bits) -> e_cell %s +- %s fJ per CELL bit"
                  % (fmt(sd.get("fJ"), 3), fmt(sd.get("se_fJ"), 3),
                     fmt(ec.get("scale_portresult_per_cell_bit"), 1), fmt(ec.get("fJ"), 3),
                     fmt(ec.get("se_fJ"), 3)))
            for hk, d_ in sorted((F.get("V_pairs") or {}).items()):
                w("     cross-mode (rate-confounded, reported only): d1b - d1a at %-4s %8s +- %-7s W"
                  "   | rate-free per-rung step %s fJ/op = %s fJ per cell bit"
                  % (hk, fmt(d_.get("value"), 4), fmt(d_.get("se"), 4),
                     fmt(d_.get("per_op_fJ"), 1), fmt(d_.get("fJ_per_cell_bit_this_rung"), 3)))
        if F.get("A_rate_confounded_beside_the_ladder"):
            w("   -- family A (A2.4): the rate-confounded rung, beside the ladder, never inside it --")
            for n, d_ in sorted(F["A_rate_confounded_beside_the_ladder"].items()):
                w("     %-8s delta %-3s %9s +- %-7s fJ per address bit   (mode retires at another rate)"
                  % (n, d_.get("delta"), fmt(d_.get("fJ"), 2), fmt(d_.get("se_fJ"), 2)))
        if F.get("A_gated_minus_live_levels_W"):
            w("   -- family A: gated minus live at MATCHED register-index distance (§9's own arm) --")
            for k, d_ in sorted(F["A_gated_minus_live_levels_W"].items()):
                w("     %-8s %8s +- %-7s W   t %7s (3-sigma |t| >= %s)"
                  % (k, fmt(d_.get("value"), 4), fmt(d_.get("se"), 4), fmt(d_.get("t"), 2),
                     fmt(d_.get("t_crit_3sigma"), 2)))
        if F.get("M_levels"):
            m = F["M_levels"]
            w("   -- family M: %d distinct k_adj levels (reference %s) --" % (m["n_levels"], F.get("M_reference")))
            for k, y in zip(m["k_adj"], m["dW"]):
                w("     k_adj %6.3f   dW %8s W" % (k, fmt(y, 4)))
            w("     Spearman rho %s over %d levels; whole spread %s +- %s W (t %s, 3-sigma |t| >= %s)"
              % (fmt(m.get("spearman_rho"), 3), m["n_levels"],
                 fmt((m.get("whole_spread") or {}).get("dW"), 4),
                 fmt((m.get("whole_spread") or {}).get("se"), 4),
                 fmt((m.get("whole_spread") or {}).get("t"), 2),
                 fmt((m.get("whole_spread") or {}).get("t_crit_3sigma"), 2)))
            for st in m["steps"]:
                w("       step %6.3f -> %6.3f  %8s +- %-8s W  t %7s  >= 3 SE: %s"
                  % (st["from"], st["to"], fmt(st["dW"], 4), fmt(st["se"], 4), fmt(st["t"], 2),
                     st.get("ge_3SE")))
        if F.get("C_curvature"):
            cu = F["C_curvature"]
            w("   -- family C: the L vs L log2 L topology test --")
            for k, v in sorted(cu["fits"].items()):
                w("     %-20s resid rms %s W" % (k, fmt(v["resid_rms_W"], 4)))
            w("     preferred: %s" % cu.get("preferred"))
        J = C.get("joint_fit") or {}
        if J.get("coefs"):
            w("   -- §8.5 the joint fit (descriptive; reading %s for w), %d rows/pass, cond %s --"
              % (J.get("reading_for_w"), J.get("rows_per_pass") or 0, fmt(J.get("condition_number"), 1)))
            if J.get("design_is_degenerate"):
                w("     !! %s" % J.get("degenerate_note"))
            elif J.get("well_conditioned_note"):
                w("     %s" % J.get("well_conditioned_note"))
            for k in JOINT_COEFS + ["intercept_W"]:
                d = (J["coefs"] or {}).get(k)
                if not d:
                    w("     %-12s NOT IDENTIFIED (its family was cut)" % k)
                    continue
                if k == "intercept_W":
                    w("     %-12s %9s +- %-7s W   n=%s" % (k, fmt(d.get("value"), 4), fmt(d.get("se"), 4),
                                                           d.get("n_passes")))
                elif d.get("not_identified"):
                    w("     %-12s NOT IDENTIFIED -- %s" % (k, d.get("note")))
                else:
                    se = fmt(d.get("se_fJ"), 3) if d.get("se_quoted") else "(not quoted)"
                    w("     %-12s %9s +- %-11s fJ  VIF %6s  n=%s  identified by %s"
                      % (k, fmt(d.get("fJ"), 3), se, fmt((J.get("vif") or {}).get(k), 1),
                         d.get("n_passes"), d.get("identified_by")))
            for s in J.get("known_collinearities") or []:
                w("     collinearity: %s" % s)
    w("=" * 100)
    if res.get("across_cards"):
        w("== §8.7 across cards ==")
        for c, e in sorted(res["across_cards"].items()):
            if c.startswith("_"):
                continue
            w("  %-22s V %s mV, V^2 ratio %s (E60 %s); e_in %s fJ (ratio to a3 %s, E60 tie %s); "
              "e_out %s fJ%s" % (c, fmt((e.get("v_mean") or 0) * 1000, 1), fmt(e.get("v2_ratio_measured"), 3),
                                 e.get("E60_v2_tie"), fmt(e.get("e_in_fxor_fJ"), 2),
                                 fmt(e.get("e_in_fxor_ratio_to_a3"), 3), e.get("E60_per_bit_tie"),
                                 fmt(e.get("e_out_bridge_fJ"), 2),
                                 "" if e.get("e_in_fxor_inside_pm12pct") is not False else
                                 "   <-- OUTSIDE E60's card-to-card band (ratio/tie %s)"
                                 % fmt(e.get("e_in_fxor_vs_E60_tie"), 3)))
        w("  %s" % res["across_cards"].get("_band"))
    H = res.get("holm") or {}
    if H.get("rows"):
        w("")
        w("== §9.2 the confirmatory family, Holm-corrected at alpha = %s on %s ==" % (H["alpha"], H["primary_card"]))
        for r in H["rows"]:
            if r.get("t") is None:
                w("  %-16s %s" % (r["coef"], r.get("note")))
            else:
                w("  %-16s t %7s (df %s) rank %s, alpha %s, |t| >= %s -> %s"
                  % (r["coef"], fmt(r["t"], 2), r.get("df"), r.get("holm_rank"), fmt(r.get("alpha"), 4),
                     fmt(r.get("t_crit_holm"), 2), r.get("holm")))
        w("  everything else in this file is EXPLORATORY and labelled so (§9.2)")
    w("")
    w("== §9 verdicts ==")
    for v in res.get("verdicts") or []:
        w("  %-22s %-18s %s" % (v["claims"], v["verdict"], v["quantity"]))
        w("      basis: %s" % v["basis"])
        # (`replication_set` is in the basis already and stays a JSON-only field, so it is not
        #  printed twice.)
        for k in ("context", "finding", "margin", "open_arm",
                  "not_scored_because", "caveat", "note", "unit_note", "tier2", "method"):
            if v.get(k):
                w("      %s: %s" % (k, v[k]))
        if v.get("sensitivity"):
            s_ = v["sensitivity"]
            w("      leak arm (RECON 5): fitted %s | k=0 %s | E60 %s %s%s"
              % (("%s +- %s" % (fmt((s_.get("fitted") or {}).get("value"), 3),
                                fmt((s_.get("fitted") or {}).get("se"), 3))) if s_.get("fitted") else "n/a",
                 fmt((s_.get("zero") or {}).get("value"), 3) if s_.get("zero") else "n/a",
                 fmt((s_.get("E60") or {}).get("value"), 3) if s_.get("E60") else "n/a",
                 (s_.get("fitted") or {}).get("unit") or "",
                 ("   <-- MOVES: E60 - fitted = %s = %s SE"
                  % (fmt(s_.get("E60_minus_fitted"), 3), fmt(s_.get("E60_minus_fitted_in_SE"), 2)))
                 if s_.get("moves") else "   (within 1 SE)"))
        if v.get("method_choices"):
            for k_, x_ in sorted(v["method_choices"].items()):
                if isinstance(x_, dict):
                    w("      %s:" % k_)
                    for k2, x2 in sorted(x_.items()):
                        w("         %-28s %s" % (k2, x2))
                else:
                    w("      %-30s %s" % (k_, x_))
    M = res.get("method_choices") or {}
    if M.get("method_choices"):
        w("")
        w("== RECON 15 the method choices (not a claim row: no arm, no verdict) ==")
        w("  %s" % M.get("basis"))
        for k_, x_ in sorted(M["method_choices"].items()):
            if isinstance(x_, dict):
                w("  %s:" % k_)
                for k2, x2 in sorted(x_.items()):
                    w("     %-30s %s" % (k2, x2))
            else:
                w("  %-32s %s" % (k_, x_))
    w("")
    w("Every capacitance and electron count above is from the MINION RAIL leg (§8.4); board figures "
      "are labelled board energy per flip.  Both the 1/2 CV^2 and the CV^2 conventions are printed, "
      "since conflating them is the page's own claim S8.")
    return "\n".join(L) + "\n"


# =================================================================================================
# main
# =================================================================================================
# RECON 5 --------------------------------------------------------------------------------------
# §8.1 corrects each run to its launch reading with "the card's fitted leakage slope (E60 fitted
# 0.203 / 0.442 / 0.327 W/C)".  Both pipelines fit 0.033-0.040 W/C on aifoundry3 -- the sensor steps
# in whole degrees, so only ~23% of runs qualify for the within-run drift fit at all -- so the
# registered number and the measured one are an order of magnitude apart and the choice has to be
# shown, not made silently.  Per-flip prices are differences of items measured seconds apart and
# barely move; the LADDER INTERCEPT is an absolute watt level and moves a lot, which is exactly the
# quantity §5.1's R1/R2/R3 row is decided on.
LEAK_SENSITIVE_KEYS = [
    ("e_in_fxor", "J/flip"), ("e_in_fxor_E60fit", "J/flip"), ("e_in_fand", "J/flip"),
    ("e_in_fand_d2A", "J/flip"), ("e_in_for_d2C", "J/flip"),
    ("e_out_bridge", "J/flip"), ("e_out_fand_BA", "J/flip"), ("e_out_for_DC", "J/flip"),
    ("e_cell", "J/flip"), ("e_carry", "J/flip"), ("e_addr", "J/flip"), ("e_addr_live", "J/flip"),
    ("e_sum_fnot_d1nz", "J/flip"), ("e_out_add_plus_e_carry", "J/flip"),
    ("intercept_N_W", "W"), ("intercept_X_W", "W"), ("zero_word_term", "W"),
    ("phase_term", "W"), ("zero_gate_step", "W"), ("result_path_load_W", "W"),
    ("half_die_result_path_load_W", "W"), ("dipole_W_vs_E_board_W", "W"),
]


def leak_sensitivity(card_name, R, man, args, C_primary, key):
    """Re-run the reduction at k = 0 and at E60's slope and table every quantity that moves."""
    arms = {"fitted": C_primary}
    want = [("zero", 0.0)]
    e60k = E60["leak_W_per_C"].get(card_name)
    if e60k:
        want.append(("E60", float(e60k)))
    for nm, kk in want:
        sink = []
        try:
            C2, rest2 = analyse_card(card_name, R, man, args, sink, leak_override=kk)
            if rest2:
                v2, p2, i2, vr2, _ = rest2
                family_estimates(C2, man, v2, p2, i2, vr2, card_name, sink, label=key)
            arms[nm] = C2
        except Exception as exc:                       # never let an arm break the primary result
            arms[nm] = {"error": "%s: %s" % (type(exc).__name__, exc)}
    # the primary numbers must be the fitted-slope ones: analyse_card rewrote r["p80"] in place, so
    # recompute it at the primary slope before anything else reads these runs again.
    kprim = C_primary.get("leak_W_per_C")
    if kprim is not None:
        for r in R:
            base = r["start_c"] if r["start_c"] is not None else r["t_win"]
            if r.get("p_raw") is not None and r.get("t_win") is not None and base is not None:
                r["p80"] = r["p_raw"] - kprim * (r["t_win"] - base)
    out = {"k_W_per_C": dict((nm, (c.get("leak_W_per_C") if isinstance(c, dict) else None))
                             for nm, c in arms.items()),
           "k_fitted_from_n_runs": C_primary.get("leak_runs"),
           "k_fitted_qualifying_pct": C_primary.get("leak_qualifying_run_pct"),
           "k_E60_W_per_C": e60k,
           "primary": "fitted (§8.1: the card's own fitted slope)",
           "note": "RECON 5: §8.1 registers the card's fitted slope and names E60's 0.203 / 0.442 / "
                   "0.327 W/C; the two differ by an order of magnitude on aifoundry3 because the die "
                   "sensor steps in whole degrees, so only a minority of runs qualify for the "
                   "within-run drift fit. Every row below is the SAME estimator at three slopes.",
           "rows": {}}
    for name, unit in LEAK_SENSITIVE_KEYS:
        row, seen = {}, False
        for nm in ("fitted", "zero", "E60"):
            c = arms.get(nm)
            d = ((c or {}).get("derived") or {}).get(name) if isinstance(c, dict) else None
            if not d or d.get("value") is None:
                row[nm] = None
                continue
            seen = True
            scale = 1e15 if str(unit).startswith("J") else 1.0
            row[nm] = {"value": d["value"] * scale, "se": (d["se"] * scale) if d.get("se") else None,
                       "n_passes": d.get("n_passes"), "unit": "fJ" if scale != 1.0 else "W"}
        if not seen:
            continue
        a_, b_ = row.get("fitted"), row.get("E60")
        row["E60_minus_fitted"] = ((b_["value"] - a_["value"]) if (a_ and b_) else None)
        row["E60_minus_fitted_in_SE"] = (((b_["value"] - a_["value"]) / a_["se"])
                                         if (a_ and b_ and a_.get("se")) else None)
        row["moves"] = bool(row["E60_minus_fitted_in_SE"] is not None
                            and abs(row["E60_minus_fitted_in_SE"]) >= 1.0)
        out["rows"][name] = row
    out["quantities_the_arm_moves"] = sorted(k for k, v in out["rows"].items() if v.get("moves"))
    out["quantities_the_arm_leaves_alone"] = sorted(k for k, v in out["rows"].items()
                                                    if not v.get("moves"))
    # the §5.1 R1/R2/R3 reading at each slope -- the row the arm actually decides
    rr = {}
    for nm in ("fitted", "zero", "E60"):
        c = arms.get(nm)
        ir = ((c or {}).get("families") or {}).get("N_intercept_readings") if isinstance(c, dict) else None
        if not ir:
            continue
        d = ((c.get("derived") or {}).get("intercept_N_W") or {})
        rr[nm] = {"intercept_W": d.get("value"), "se_W": d.get("se"), "n_passes": d.get("n_passes"),
                  "matched": ir.get("matched"),
                  "t": dict((k2, v2.get("t")) for k2, v2 in (ir.get("readings") or {}).items())}
    out["N_intercept_by_slope"] = rr
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+", help="pass dirs: <data>/<card>/dtf/p<N>/ etc")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True, help="dtf.json")
    ap.add_argument("--txt", default=None, help="reduce.txt (default: beside --out)")
    ap.add_argument("--csv", default=None, help="runs.csv")
    ap.add_argument("--leak", default="auto", help="auto, or a W-per-C slope to use on every card")
    ap.add_argument("--exclude", action="append", default=[],
                    help="<card>:<item> or *:<item>, excluded by name (amendment A3 and later amendments)")
    ap.add_argument("--cam-stats", default=None,
                    help="JSON from the camera reduction; passed through as EXPLORATORY tier 2")
    ap.add_argument("--dis", default=None,
                    help="objdump listing of the binary the campaign ran (default: "
                         "<data>/../proof/dis-a2.txt); used ONLY to check the physics skeptic's "
                         "loop-head-alignment finding in the S10 rate row")
    ap.add_argument("--primary-card", default="aifoundry3")
    ap.add_argument("--busy-mhz", type=int, default=800)
    ap.add_argument("--quiet", action="store_true", help="write the files, print nothing")
    a = ap.parse_args(argv)

    man = Manifest(a.manifest)
    missing = list(man.warnings)
    allruns, smoke, experiments, notes = [], {}, set(), []
    unfinished = []
    for d in a.dirs:
        if not os.path.isdir(d):
            missing.append("pass dir %s does not exist" % d)
            continue
        # FIX.6: `block.json` is written by block.sh when the pass ENDS, so a dir without one is a
        # pass still running (tonight: aifoundry3 p9-p12 and aifoundry2 p14, to ~02:15 PDT).  Its
        # runs.jsonl and telemetry are half-written, so it is skipped by name, never half-reduced.
        bj = os.path.join(d, "block.json")
        if not os.path.exists(bj):
            unfinished.append(d)
            missing.append("pass dir %s has no block.json: the pass had not finished when this "
                           "reduction ran, so it is SKIPPED (it is not a failed pass)" % d)
            continue
        try:
            st = (json.load(open(bj)) or {}).get("status")
        except ValueError:
            st = None
        if st and str(st) != "ok":
            unfinished.append(d)
            missing.append("pass dir %s: block.json status %r (not 'ok'), so the pass is SKIPPED "
                           "and reported, never reduced" % (d, st))
            continue
        card_ = resolve_card(d)
        gov_free = card_ not in PINNED_CARDS
        rs, card_, nn = runs_of_pass(d, man, gov_free=gov_free, busy_mhz=a.busy_mhz,
                                     card_hint=card_)
        if card_ not in PINNED_CARDS and card_ not in E60["per_bit_tie"]:
            missing.append("%s: card name %r is not one of the three registered cards; it is treated "
                           "as governor-free (E60 amendment A2's window rule)" % (d, card_))
        notes += nn
        if not rs:
            missing.append("%s yielded no run" % d)
            continue
        exp = rs[0]["exp"]
        experiments.add(exp)
        if "smoke" in exp:
            s = smoke.setdefault(card_, {"n_runs": 0, "items": [], "start_c": [], "all_ok": True,
                                         "participants": set(), "ipc": {}})
            s["n_runs"] += len(rs)
            for r in rs:
                s["items"].append(r["item"])
                s["start_c"].append(r["start_c"])
                s["all_ok"] = s["all_ok"] and r["ok_records"]
                s["participants"].update(r["participants"])
                if r["ipc"] is not None:
                    s["ipc"][r["item"]] = r["ipc"]
            continue
        key = card_ if ("cam" not in exp) else "%s [%s]" % (card_, exp)
        for r in rs:
            r["unit_key"] = key
        allruns += rs
    for c, s in smoke.items():
        s["items"] = sorted(set(s["items"]))
        s["participants"] = sorted(s["participants"])
        s["start_c"] = sorted(set(x for x in s["start_c"] if x is not None))

    res = {"meta": {"generated": datetime.datetime.now().isoformat(timespec="seconds"),
                    "manifest": _rel(a.manifest), "n_manifest_items": len(man.items),
                    "seed": man.seed, "modes": man.modes,
                    "dirs": [_rel(x) for x in a.dirs],
                    "experiments": sorted(experiments),
                    "unfinished_pass_dirs_skipped": [_rel(x) for x in unfinished],
                    "leak": a.leak, "excluded_by_name": a.exclude,
                    "three_sigma_p": THREE_SIGMA_P, "holm_alpha": HOLM_ALPHA,
                    "confirmatory_family": CONFIRMATORY,
                    "plan": "tools/claims-v3/dtf/README.md §8-§9",
                    "departures": [
                        "the on-silicon register dump (§7 proof 6) is not implemented",
                        "modes are 300-309",
                        "anchor_pi runs first, middle and last, so the drift statistic is a fitted W/min"]},
           "smoke": smoke, "notes": notes, "cards": {}, "missing": missing}
    if not allruns:
        missing.append("no measured pass survived loading: nothing to reduce")
        res["verdicts"] = []
        json.dump(res, open(a.out, "w"), indent=1, default=float)
        txt = a.txt or os.path.join(os.path.dirname(os.path.abspath(a.out)), "reduce.txt")
        text = report(res, man)
        open(txt, "w").write(text)
        if not a.quiet:
            sys.stdout.write(text)
        return 0

    rows_csv = []
    for key in sorted({r["unit_key"] for r in allruns}):
        R = [r for r in allruns if r["unit_key"] == key]
        card_name = R[0]["card"]
        C, rest = analyse_card(card_name, R, man, a, missing)
        C["unit_key"] = key
        C["experiment"] = R[0]["exp"]
        res["cards"][key] = C
        if rest:
            val, passes, items, v_rail, G = rest
            family_estimates(C, man, val, passes, items, v_rail, card_name, missing, label=key)
            # RECON 5: the leakage-slope sensitivity arm.  The same reduction is re-run at k = 0 and
            # at E60's fitted slope for this card, and every quantity the arm MOVES is tabled with
            # all three readings.  The arms are thrown away afterwards; only the table survives, and
            # the primary (fitted-slope) numbers above are untouched.
            C["leak_sensitivity"] = leak_sensitivity(card_name, R, man, a, C, key)
            if a.leak != "auto":
                C["leak_sensitivity"]["note_primary"] = (
                    "--leak %s was given on the command line, so the PRIMARY column is that slope, "
                    "not a per-card fit" % a.leak)
            C["joint_fit"] = joint_fit(man, val, passes, items, v_rail, reading="R2")
            C["joint_fit_R1"] = joint_fit(man, val, passes, items, v_rail, reading="R1")
            # §6: the pass floor for any confirmatory item
            if "[" not in key:
                if C.get("n_passes", 0) < 6:
                    missing.append("%s: only %d surviving pass(es) -- every confirmatory item on "
                                   "this card is a BOUND ONLY (the §6 floor is 6)"
                                   % (key, C.get("n_passes", 0)))
                if C.get("n_passes_registered") and C.get("n_passes", 0) < C["n_passes_registered"]:
                    # VER 6: "present" reads as data loss.  Every registered pass dir exists and was
                    # read; the shortfall is §8.9 setting passes aside, which §8.9 also says are
                    # reported and NOT replaced.  Say which, and where to read why.
                    _sa = [x["pass"] for x in (C.get("passes_set_aside") or [])]
                    missing.append(
                        "%s: %d of the %d registered passes KEPT; %d SET ASIDE%s (§8.9: reported and "
                        "not replaced -- see the pass block for each one's reason). No pass dir is "
                        "missing: all %d were read."
                        % (key, C.get("n_passes", 0), C["n_passes_registered"], len(_sa),
                           (" (%s)" % _sa) if _sa else "",
                           C["n_passes_registered"]))
        # (FIX.8: n_passes / n_passes_registered are written inside analyse_card, above its gates, so a
        # unit that kept no run still reports them; nothing is overwritten with None here.)
        for r in R:
            rows_csv.append(dict((k, (json.dumps(r.get(k)) if isinstance(r.get(k), (list, dict))
                                      else r.get(k)))
                                 for k in ("card", "unit_key", "exp", "pass", "item", "pos", "attempt",
                                           "kind", "family", "op", "start_c", "on_protocol", "p_raw",
                                           "p_raw14", "p80", "t_win", "rail", "mv", "mhz", "rate",
                                           "ipc", "ipc_n", "cycles_per_op", "participants", "harts",
                                           "ramp_ms", "window_start_s", "launches", "fail")))

    # items in the manifest that never ran anywhere
    seen = {r["item"] for r in allruns} | set(n for s in smoke.values() for n in s["items"])
    never = sorted(n for n in man.items if n not in seen)
    if never:
        byfam = defaultdict(list)
        for n in never:
            byfam[man.family(n)].append(n)
        for fam in sorted(byfam, key=lambda x: str(x)):
            missing.append("family %s: %d manifest item(s) never ran: %s"
                           % (fam, len(byfam[fam]), ", ".join(byfam[fam])))

    measured = dict((k, v) for k, v in res["cards"].items() if "[" not in k)
    res["across_cards"] = across_cards(measured)
    primary = a.primary_card if a.primary_card in res["cards"] else (sorted(measured)[0] if measured else
                                                                     sorted(res["cards"])[0])
    res["meta"]["primary_card"] = primary
    res["holm"] = holm(res["cards"], primary)
    # the physics skeptic's loop-head-alignment finding, checked against the disassembly if it is
    # there; the S10 rate row reads it out of LOOP_HEAD.
    global LOOP_HEAD
    LOOP_HEAD = loop_head_alignment(a.dis) or {}
    res["loop_head_alignment"] = LOOP_HEAD or {
        "source": a.dis or DIS_DEFAULT, "cite": SKEPTIC_CITE, "checked_here": False,
        "finding": "EXTERNAL (physics skeptic, %s): the two issue-rate levels A2.1 measured follow "
                   "the loop head's address mod 32 -- an instruction-fetch alignment effect, not "
                   "anything about the data. The disassembly was not on disk here, so this run "
                   "carries the finding by citation rather than re-deriving it." % SKEPTIC_CITE}
    _v = verdicts(res["cards"], man, primary, missing)
    # RECON 15: the method block is not a claim row; it gets its own key and its own section.
    res["method_choices"] = next((x for x in _v if x.get("not_a_claim_row")), None)
    res["verdicts"] = [x for x in _v if not x.get("not_a_claim_row")]
    if a.cam_stats and os.path.exists(a.cam_stats):
        res["camera_tier2_exploratory"] = json.load(open(a.cam_stats))
        res["camera_tier2_exploratory"]["_note"] = \
            "EXPLORATORY (§9, §10 tier 2): no CONFIRMED/REFUTED arm; the statistic is a " \
            "permutation-calibrated double difference with a per-pass per-pixel linear time trend " \
            "removed, and the lobe must move ~11 mm or the camera is watching the power stages"
    elif a.cam_stats:
        missing.append("--cam-stats %s does not exist: tier 2 is not reported" % a.cam_stats)
    for r in allruns:
        r.pop("_tP", None)
    res["runs"] = allruns
    res["missing"] = missing

    json.dump(res, open(a.out, "w"), indent=1, default=float)
    txt_path = a.txt or os.path.join(os.path.dirname(os.path.abspath(a.out)), "reduce.txt")
    text = report(res, man)
    open(txt_path, "w").write(text)
    if a.csv and rows_csv:
        keys = list(rows_csv[0])
        with open(a.csv, "w", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=keys)
            wr.writeheader()
            wr.writerows(rows_csv)
    if not a.quiet:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
