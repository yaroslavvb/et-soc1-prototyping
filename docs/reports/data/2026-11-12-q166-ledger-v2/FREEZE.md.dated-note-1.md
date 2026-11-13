# FREEZE.md, dated note 1 (Thu 12 Nov 2026, PST): two sentences of the freeze corrected, nothing frozen changed

*Written by Q166's fix lane (fix-q166) on its verifier's findings (verify-calc), after the scores. [`FREEZE.md`](FREEZE.md),
[`frozen-v2.json`](frozen-v2.json), [`predictions-v2.json`](predictions-v2.json) and [`SHA256SUMS-freeze`](SHA256SUMS-freeze)
stay byte for byte as frozen; this note sits beside them. Every figure below is post hoc and is in
[`posthoc-v2.json`](posthoc-v2.json), written by `tools/ledger/posthoc_ledger_v2.py` from the frozen model.*

**1. "No constant was fitted to any of the seven loads" is false.** Three of the frozen constants come from the scored
loads' own rows:
- `w_set` (0.70, band 0.55-0.83) is the mean of E101's ratios 0.705, 0.550 and 0.834 (its R5 and R5b arms);
- the L2 stream price (`mem_paths.l2_stream`) is E101's post hoc path cost, 2.15 nJ an op on zeros and 7.70 on random;
- M10's D, the data's price per op, was fitted on E86's and E95's rows, each kind predicted with its own kind left out.

`frozen-v2.json` labels the first two "post hoc (E101): E101 is IN SAMPLE", and the scores call E101's L2-streamed cells in
sample and E86's and E95's "M10 held out by kind". So the facts were disclosed; the sentence contradicted them. Read it
as: no constant was fitted to E39, E37 or E59; E101 is in sample for `w_set` and the L2 stream price; E86 and E95 are
held out only by kind.

**2. "Two rules were set during the desk build after arithmetic that put v2 beside E101's `mmp64` arm"** is true, but the
freeze did not draw its consequence. The first rule, a hart's time priced once (`awake_rule`), halves the misses of the
loads it touches, and those loads stream from DRAM as `mmp64` does:
- E101's two `mmp64` cells are **post hoc for the awake rule**. They read +18.6% (zeros) and +5.7% (random) with it, and
  +36.0% and +16.4% without it. The frozen label "held out for every price it uses" stays in `predictions-v2.json`;
  the scores now carry the corrected label.
- E37 is the same mmbench benchmark streaming from DRAM, so its prediction **depends on the rule**. It reads +13.0 to
  +14.0% an op with the rule, and +27.3 to +28.0% without it (2.40 W rms against v1's 2.14).
- E101's held-out-by-price score is the 7 loop cells only, 3.2% rms. The first scorer's figure, 7.1% rms over 9 cells,
  mixed in the two DRAM cells and is superseded.

The second rule (E136's cooperative loads move 384 B a minion-op beyond the L2) is E136's own desk count, frozen before
E136 ran. It moves no other load.

SPDX-License-Identifier: Apache-2.0
