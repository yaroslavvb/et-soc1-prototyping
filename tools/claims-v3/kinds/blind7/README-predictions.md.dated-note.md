# Dated note beside README-predictions.md: aifoundry2's frozen predictions carry no session read, and the recompute takes each tile's own die starts (Q141(g), Wed 4 Nov 2026)

*Written Wed 4 Nov 2026 (week 45), PST, at the desk on the Intel, by Q141(g) (E165's registration), after this directory's gate commit `75802201` and
its dated notes A1 (`3c9bb2ba`), and before any pool-7 claim, launch, measurement or score. It is a new file. [`README-predictions.md`](README-predictions.md)
and every other file here stay byte-identical: `SHA256SUMS` 91 of 91 OK, and `make_blind7.py --check` reads "63 built files, 92 pool files, 0 problems",
with this file listed beside the pool (18 files beside it). No number, band, rule, prediction or verdict changes.*

**The complaint.** Q140's final critic (the readiness critic of Wed 4 Nov 2026, its fault 4; the records round Q141(r) carries it into the lab's
records) found two things about the aifoundry2 half of this directory:

1. **All 61 of M9's frozen aifoundry2 predictions were computed with no session read.** Every tile's `M9.a2_q140l` block in
   [`predictions-blind7-aifoundry2.json`](predictions-blind7-aifoundry2.json) reads `"die_start_source": "T_ref 54.38 C (none given)"` and
   `"delta_source": "fallback (no zeros-anchor read)"`: the die-start term and the session's zeros level sit at their defaults. Under the cap the
   governed clock moves about −2.4 MHz per °C of die start (`d_mhz_per_c_die_start`: −2.33 to −2.51 MHz/°C on 11 of the 12 governed tiles that run on
   aifoundry2, −1.68 on `fp32.exp_b_alt_nib`, the one nearest 795 MHz) and about −3.9 MHz per W of the session's anchor offset
   (`d_mhz_per_w_of_delta`), so a burst that starts 2 °C warmer than 54.38 °C moves
   a governed tile's predicted clock by about 4.8 MHz, more than the 4 MHz line of Q139's critic, rank 2.
2. **The recompute command in § Commands passes one die start to every tile.** The line under "after E165's zeros anchors run" gives
   `predict_blind7.py ... --a2-session <anchors.json> [--a2-die-start <C>]`, and one `--a2-die-start` value goes to every tile as its only die start
   (`predict_blind7.py` line 285: `ds = [a.a2_die_start]`, passed as `die_starts=ds` for each tile).
   The frozen code, `predict_m9_a2.burst(D, t, anchors, die_starts, D_band_hw)`
   ([`predict_m9_a2.py`](../../../../docs/reports/data/2026-11-04-q140l-a2-session-terms/predict_m9_a2.py), `420b887e…`), takes each tile's own
   bursts' die starts, one per burst, and averages its prediction over them.

**What E165 scores instead** (registered in [`../../e165/E165.md`](../../e165/E165.md), committed with this note, before any E165 data): E165's
primary is M9's aifoundry2 part **recomputed per tile through `predict_m9_a2.burst`, called unchanged**, with the session's own zeros-anchor reads
(every counted burst of pool 7's three `anchor7_zeros` tiles; the frozen code counts those at 795 MHz or more) and **each tile's own counted bursts'
die starts** ([`../../e165/score_e165.py`](../../e165/score_e165.py) › `predict`). The frozen `M9.a2_q140l` block is scored beside it, as frozen. The
governed and pinned groups stay this file's (`M9.a2_q140l.group`). Called with no session read, the same code reproduces every frozen `M9.a2_q140l`
field on all 61 tiles (1,586 fields, 0 differ: [`../../e165/predictions-e165.json`](../../e165/predictions-e165.json) › `recheck_frozen_block`), so
the recompute is this directory's own code path with the two inputs filled in. **The § Commands line with `--a2-die-start` is not E165's primary**; it
stays as written, as a record of what Q140(x) handed over.

**What it does to predicting power and heat.** Nothing is fitted or re-frozen. It decides which prediction of M9's aifoundry2 part the blind test
reads: the one the model defines (the day's zeros level and each burst's die start as inputs), not the fallback at a reference die. The before is
Q140(l)'s end-to-end held-out error with blind D (E160: 3.68 MHz / 0.66 W / 0.80 W; E143: 5.12 / 0.86 / 0.87); the after is E165's blind score.

SPDX-License-Identifier: Apache-2.0
