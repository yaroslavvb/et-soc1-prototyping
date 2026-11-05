# Q142(p): pool 8's registration for M10 - the one frozen predictor, term b by the convergence rule on every float tile, term a's anchors protocol with its a-priori arm and check anchors, the rate per format, aifoundry2 and card 0 decided by a rule stated first, pool 8's scoring rules in blind7's form with the level-or-gain test and its power, and a hash list of every input; written before the predictor or any pool-8 output exists

*Wed 4 Nov 2026 (week 45), written about 22:50-23:12 PST and committed at the time git records, on the Intel, desk only: no card, no device command, no lab box, no post in the
lab's channel, no Modal, no archive. It answers the Q142 critic's `m10` field, items (2)-(7), and its `next` **ranks 2 and 3**
(pool 8's frozen predictor, and M10's D carried to aifoundry2 and card 0 by a registered step or M9's part named there), for the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** (a power
model across kinds), with items 8 and 9 (heat). The owner's goal, in his words of 2 November 2026: to predict the power requirement
and heat generation of numeric computations as accurately as possible.*

**Written and committed before:** the pool-8 predictor (`docs/reports/data/2026-11-05-q142p-pool8-predictor/`, the next commit);
pool 8 itself (no `tools/claims-v3/kinds/blind8/` tile, manifest or count exists in git at this commit, and this lane never read the
designer's scratch or design file); any prediction for any pool-8 tile. Everything below is fixed now. A departure is a dated
amendment file beside this one, committed before the output it touches. [`POOL8-SHA256SUMS`](POOL8-SHA256SUMS) holds the sha256 of
every file the predictor will read, and [`POOL8-SHA256SUMS-62`](POOL8-SHA256SUMS-62) the 62 inputs no earlier hash list named.

**M10 and M9 are not changed.** M10 is `docs/reports/data/2026-11-04-q142m-m10/` as committed (`6829c9ba`, with `d1581099` and
`c996d135`): `m10.json` (sha256 `37b7fa86…`) holds every parameter, and `m10-s7.json` supersedes its `entered` and `heat_chain_gain`
as M10's primary, and nothing else (REGISTRATION.md's A2). M9 is `1f244140` / `8dfafae3`, its aifoundry2 part `5b98bd5c` / `245caffe`
/ `5c98c0c5`. No price, card term, band, rule or verdict of either changes here. This file only says how they are applied to pool 8 and
scored there.

## 0. What was read before this was written (disclosed), and what was computed

- **Read:** M10 in full (REGISTRATION.md and A1-A4; README.md and notes 1-2; `m10.json`, `m10-s7.json`, `predict_m10.py`,
  `predict_m10_s7.py`, `fit_m10.py`, `section7_m10.py` and its outputs, `heldout-m10.json`, `rows-m10.json`, `a2-checks-m10.json`,
  `tables-m10.md`'s structure); RECOUNT-RULE.md and `recount_rule.py`; M9's aifoundry2 part (its REGISTRATION.md, `m9_a2.json`,
  `predict_m9_a2.py`, the fit's data section); E170's registration, A2 and `e170_common.py`; E163's, E164's and E165's registrations;
  `predict_blind7.py`; pool 7's manifest form (`blind7.json`) and counts form; the Q142 critic (`m10`, `next`, `accuracy_now`).
- **Computed before writing** (design only, committed beside this file as [`pool8/design_power.py`](pool8/design_power.py) →
  [`pool8/design-power.txt`](pool8/design-power.txt), standard library, committed rows only): the difference between two sessions on
  one card of the same float tiles, from E163's K14 re-runs (against E141 and E152) and E164's K7 repeats (against E157), and the power
  of § 7's level-or-gain test at the planned re-run count. **Post hoc, never a result:** E163's seven re-runs of E141's float tiles
  (D 15-23 W) read a level of +0.11 W and a gain of −0.13% of D when both are fitted, residual sd 0.029 W; E152's six (D 4.7-5.4 W)
  read +0.06 W on average. That is why § 7 registers a test that separates the two. Also run, to list the files the predictor's chain
  opens: M10's committed self-test (`predict_m10_s7.py selftest`, PASS, 104 rows within 1.4e-14 W, as committed) under a file trace.
- **Seen by accident, disclosed:** the round's shared local job log (one read of its tail) named the pool designer's scripts and two
  downloaded listings of public W8A8 checkpoints. Nothing of the pool's tiles, manifest or design was read, and nothing below depends
  on what pool 8 holds: every rule is written for any pool in pool 7's form.

## 1. The one frozen predictor (the `m10` field's item 2)

- **Files** (the next commit, new files only): `docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8.py` with its
  self-test, a README and a hash list of its own. Standard library and numpy 1.26 (the Intel's system python 3.9).
- **What it reads:** `m10.json` and `m10-s7.json` through `predict_m10_s7.py`'s loaders (`load_m10`, `load_s7`), after checking both
  files' sha256 against M10's `SHA256SUMS` and `SHA256SUMS-a2`; M9's `m9.json` for M9 beside; the files in `POOL8-SHA256SUMS`. It refuses
  to run if any listed file differs.
- **M10's 600 MHz D:** `predict_m10.d600(f, t, rate, card, m10, s)` unchanged: D = s × card term × rate × Σ price × feature, with
  `m10.json`'s pass-2 prices (`coef_J`) and card 1's term 0.9616 (both families). The float scale s is § 3's; int8's is 1 (term a did
  not enter for int8). Features: the frozen chain `predict_blind7.py` runs (`fit_m7.feats_from_counts`, `fit_m8.m8_extra`,
  `fit_m8.finish`, `fit_m9.m9_extra`, as `fit_m10.chain_feats` calls them), on § 2's counts.
- **M10's band:** `m10.json`'s rule as `fit_m10.py` calibrated it: half-width k √(pool² + c² xᵀCx), x = rate × features, C =
  `cov_J2`, c the card term, pool = `interval_pool_by_format_card[<t>|<card>].rms_w`, k = `band_k` (floats 2.002, int8 1.829); centred
  on the prediction, the session scale not in the width.
- **Heat over a 4.5 s run:** `predict_m10.rise_4p5s(S, T_run, card, m10)` with S = D + the format's zeros S on the card
  (`predict_blind5.zeros_S`, as M9 used it) and T_run = 4.5 s (the harness's run; the measured run length reported beside). Its band:
  M7's `band_k` (1.9497, the factor M9 carried) × M10's held-out rms of that law for the format on the card (`heldout-m10.json` ›
  `heat_c1` › `base_refit_loko`: aifoundry3 fp32 0.1739, fp16 0.1505, int8 0.1895 °C; card 1 0.3089, 0.3185, 0.1495 °C).
- **Heat over minutes:** the primary factor on Q138(t)'s chain is `predict_m10_s7.chain_gain_primary(s7)` = **1.0** (the chain
  unscaled); the reported arm is `predict_m10_s7.chain_gain_arm(m10, s7)` = **1.03199**. The predictor never calls
  `predict_m10.chain_gain()` for the primary. It applies the factor to a chain rise computed by Q138(t)'s frozen chain on a hold's
  measured board power (arm A, as E144's, E154's, E166's and E167's scorers computed it).
- **Card 0's 6 s burst rise:** `predict_m10.rise_card0_burst(P_board, m10)` = 0.2415 °C per board W over 21.5 W (term c2).
- **M9 beside, on the same tiles:** `m9.json` as frozen, by `predict_blind7.py`'s formula (D = card scale by format × rate × Σ price ×
  feature on the three-point counts; M9's band rule; M7's 4.5 s law at S = D + zeros S), at the same rate as M10 (§ 4).

**Its self-tests (registered now, run and committed with the predictor):**
- **T1, the primary factor:** `chain_gain_primary` returns exactly 1.0, `m10-s7.json` › `entered_primary.d` is null, and the arm's
  factor equals 1 + `m10.json`'s γ (1.03199). On the nine large rises of `heldout-m10.json` › `heat_d_chain_gain.holds`, the primary's
  plateau errors equal arm A's committed errors and the arm's equal e − 0.03199 P.
- **T2, pool 7 in sample:** for pool 7's 104 rows, the predictor's own path (features through the chain, the S tiles' N-point
  features from M10's committed counts, each session's float scale by § 3's code from that session's anchors) reproduces `rows-m10.json`
  › `M10_insample_pred_w` within **1e-9 W**.
- **T3, pool 7 held out:** for each of pool 7's 52 kinds, the predictor's D formula fed the fold's prices, card term and session scales
  (re-derived by `fit_m10.Fit10.fit(k)` for that kind's fold, unchanged) reproduces M10's committed held-out prediction of every row of
  the kind (D − `err_w`, the frozen variant: B+a+b floats, B int8) within **5e-7 W**: `rows-m10.json` stores `err_w` rounded to 1e-6 W,
  so 1e-9 W is reachable only on the full-precision in-sample column (T2).
- **T4, refusal:** a float tile whose counts do not reach its convergence-rule N (§ 2) gets no prediction, the run exits 3 and writes no
  predictions file; a pool whose random anchors' roles cannot be read (§ 3) is refused the same way.
- **T5, aifoundry2:** on pool 7, the predictor's M9 path through Q140(l)'s part reproduces `predictions-blind7-aifoundry2.json` ›
  `M9.a2_q140l` field by field; M10's carried D goes through the same call (§ 5).
- **T6, card 0:** on E170's committed session (its anchors and die starts, `results.json`), the predictor's M9 path through
  `e170_common.pred_card0` reproduces E170's committed primary per tile; M10's k on E170's measured boards reproduces `heldout-m10.json`
  › `heat_c2_card0_burst` (k 0.2415 on all tiles; the leave-one-tile-out rms 0.3385 °C).
- **T7, M9 at 600 MHz:** M9's D at the nominal rate reproduces `predictions-blind7-aifoundry3.json` and `-aifoundry1c1.json` ›
  `M9.D_w` for all 61 pool-7 tiles to their 1e-4 W rounding.
- **T8, the hash lists:** every repo file the self-test run opens or imports is named in `POOL8-SHA256SUMS` or the predictor's own list,
  and every named file hashes as listed.

## 2. Term b's input: the convergence rule on every float tile (item 3)

- **Every fp32 and fp16 tile of pool 8** (anchors, check anchors and re-runs included; never chosen by a designer's class label) is
  counted on the bench by RECOUNT-RULE.md §§ 1-4 (`b4444dd4`) exactly as M10's term b was: the bench's three standard points, then the
  nine points of N = 9, then 3N while e(N) > 0.10 W, up to N = 243; e(N) = `recount_rule.err` of `recount_rule.point_w` at **M9's frozen
  float prices** (`recount_rule.prices()`), the larger of the sample and interleaved estimates. A tile above the bound at 243 is carried
  at 243 with its e(243) stated.
- **The features** are `fit_m10.recount`'s: the N-point counts row is `run_kinds.mean_rows` over the N points with the three standard
  points as its `points`, passed through the chain unchanged; byte-derived features do not change.
- **int8 tiles** keep the bench's three standard points (e(N) is defined at the float prices only, and term b is a float term).
- **The predictor refuses a float tile without them:** if the points its own N needs are not all present (or any point has a
  `check_mismatch`, or one point appears twice with different counts), that tile gets no prediction, and the run exits 3 without writing
  a predictions file. Its `plan` mode prints, per float tile, the N reached, e(N) and the launch points the next step needs.
- **Committed points are reused by bytes:** a pool-8 tile whose bytes equal a pool-6, pool-7 or calibration tile's (sha256 of the whole
  file) takes that tile's committed points (the files `fit_m10.recount` reads, and M10's `bench/counts-m10-*.json`), each checked equal
  where a point is counted twice, as M10's byte-twin rule did.
- **Where they run:** on the mini (`run_remote --host mini`; the build Q141(t2) recorded, `-fno-dfg`), by the next round's (x) lane,
  after one new point agrees field by field with the Intel's build, as M10's term b did. C is checked at every point.

## 3. Term a's protocol: the session's own anchors (item 4)

- **Every pool-8 session at 600 MHz runs E78's random tiles** (`fp32.randn`, `fp16.randn`, `int8.full`) **and the pool's random
  anchors**, in every pass, with the zeros anchors.
- **The roles, from the manifest:** an anchor is a manifest tile with `anchor` true. A zeros anchor is one whose A and B tiles are all
  zero bytes. Every other anchor is a random anchor, and is a **check anchor** if the manifest says so (a field `anchor_role` or `role`
  equal to `check`, else a field `check` true, else `check` in its name), else a **scale anchor**. If a float format has three or more
  random anchors and none reads as a check anchor, the predictor refuses until a roles file (`--roles`, written by the (x) lane from the
  design file's own words and committed with the pool) names each one; a roles file never overrides a role the manifest states.
- **The scale:** s(σ) = `predict_m10.session_scale`'s statistic, unchanged: the median, over σ's float scale anchors, of measured D /
  (measured rate × card term × Σ pass-1 price × feature) (`m10.json` › `pass1_coef_J`). The scale anchors are the float anchors M10's
  own list names (`m10.json` › `families.float.session_scale.anchors`) that the session ran (E78's `fp32.randn` and `fp16.randn` in
  every session; pool 6's and pool 7's random anchors if a session re-runs them), with the features M10 read for them
  (`fit_m10.assemble_anchors`: E78's rows in `rows-m9.json`, pool 6's through the chain, pool 7's from Q140(x)'s frozen file), and pool
  8's own fp32 and fp16 scale anchors, with § 2's features. A pool-8 tile whose bytes equal an anchor of M10's list is that anchor.
  **The check anchors never enter s.** int8's anchors enter nothing (reported only).
- **Order, enforced by the code:** the predictor's `scale` mode reads only the anchors' items of the session's registered primary
  reduction (measured D and rate), writes s with its inputs and the reduction's sha256, and only then may the `primary` mode read any
  other tile. A session with no float scale anchor measured takes s = 1, M10's rule.
- **The a-priori arm:** M10 as frozen with s = 1 for every session (pass-2 prices), scored beside the primary on the same tiles. Reported
  beside both: M10's pass-1 prices with s = 1 (the variant without term a).

## 4. The rate per format (item 5)

- **The primary rate is the measured one:** each tile's `rate.mean` in the session's registered primary reduction (its launch records),
  as M10 was fitted and scored. M10's primary and M9 beside it both take it, so their comparison is like for like. Why: M10's prices
  are energy per op fitted at measured rates; at 600 MHz pinned the rate is set by the clock and the host's duty, not by the bits; and
  pool 8's sessions run the C-logging host, which runs about 0.3% below the nominal rate in every committed session (Q140(m) D1).
- **The stated rate, for everything frozen before a session runs:** nominal × (1 − δ), nominal = `fit_m5.RATE` (600 MHz / cycles per op
  × 1,024 × 0.9963), and δ per format and card the mean of the two committed C-logged sessions on that card (`a2-checks-m10.json` ›
  `rate` › `by_session_format`): **aifoundry3** (E153, E163) fp32 0.3355%, fp16 0.335%, int8 0.2275%; **card 1** (E157, E164) fp32
  0.346%, fp16 0.3445%, int8 0.276%. Why these: they are the sessions that ran pool 8's host, and int8's offset differs by card (0.23
  against 0.28%). The frozen file gives each tile's D per unit rate as well, so the primary at the measured rate is a product, not a
  refit. The stated-rate predictions are scored beside as an arm; M9 at the nominal rate (as registered for pool 7) is reported.
- **aifoundry2 and card 0** take the D at 600 MHz on aifoundry3's footing at the **nominal rate**, as `predict_blind7.py` gave M9's to
  Q140(l)'s part for pool 7, so the two models' carried D differ only in their prices and features.

## 5. aifoundry2 and card 0 (item 6, `next` rank 3): the rule, stated before anything is computed

**Rule E.** M10's D is carried through M9's aifoundry2 part, and on to card 0 through E170's relation, **as the primary there**, if
and only if both of these hold, each read from committed text and code with no number computed:
- **E-i.** The part takes the 600 MHz D only as an input: every parameter in `m9_a2.json` was fitted on measured D, not on any model's
  predicted D, so a different model of D changes no parameter of the part.
- **E-ii.** The carried D is defined by M10's own frozen rules with nothing new: `d600` on aifoundry3's footing (card term 1), at § 4's
  nominal rate, with term b's features, and s = 1 (M10's rule for a session with no anchor of the family: a governed burst session runs
  no 600 MHz anchor, so it has no s).

If both hold, M10 carried is the primary on aifoundry2 and card 0, and M9's part on M9's D is scored beside it on the same bursts.
If either fails, M9's part is the primary there, with M10 carried a reported arm.

**The reading.** E-i holds: Q140(l)'s registration (`245caffe`) says of D, "the measured D on aifoundry3 at 600 MHz on Q139(u)'s footing
… The relation is fitted and scored on measured D in every arm", and `fit_m9_a2.py` reads each cell's D from the footing reductions
(`e78-footing.json`, `e141-footing.json`, `e153.json`); M7's and M8's D enter only its reference lines. E-ii holds by § 3 and § 4.
**So M10 carried is the primary on aifoundry2 and on card 0.** Card 0's burst heat also changes: M10's k (term c2) replaces M9's.

**The exact step (no refit):**
- **aifoundry2:** `predict_m9_a2.burst(D10, t, anchors, die_starts, D_band_hw)`, imported through `e165_common.m9a2()` (its sha256 and
  `m9_a2.json`'s checked), with D10 = M10's carried D, D_band_hw = M10's 95% half-width on D at aifoundry3's footing and the nominal
  rate, `anchors` the session's zeros-anchor reads and `die_starts` the tile's counted bursts' die starts, exactly as E165 called it with
  M9's D. The frozen pre-run file holds the call with no anchors (the part's fallback) and T_ref (54.38 °C), with its sensitivities, and
  the scorer recomputes it with the session's reads, as E165 did. The 82 W admission: a tile is left out on aifoundry2 if the larger of
  M10's and M9's 95% upper peaks (`peak_board_hi95_w`, M8's peak rule as the part computes it) exceeds 82 W.
- **Card 0:** `e170_common.pred_card0(D10, t, anchors, die_starts, D_band_hw)` unchanged (κ0 = 0.9463; term e did not enter; the
  session's zeros level in full), then the die rise = `predict_m10.rise_card0_burst` on that predicted board (0.2415 °C/W over
  21.5 W). M9's rise (0.1400 °C/W) is computed beside on M9's predicted board.
- **Reported, never a verdict:** the carried D with s = the median of M10's committed float scales of the three aifoundry3 sessions whose
  measured D trained the part (E78, E141, E153; `m10.json` › `session_scales_training`), and M10 carried with M9's k on card 0.

## 6. What is predicted, per card

| card | per tile, M10 (primary and arms) | beside |
|---|---|---|
| aifoundry3, aifoundry1 card 1 (600 MHz) | D per unit rate at s = 1; D at the stated rate; the band; the pass-1 coefficient (for s); the 4.5 s die rise and band at the stated rate and s = 1; the three-point arm (floats); N, e(N) and 3pt − N | M9's D (per unit rate, at the stated and the nominal rate) with its band; M9's 4.5 s rise |
| aifoundry2 (its own governor, 6 s bursts) | the burst clock, board, burst D and die rise with their bands, at the fallback and T_ref, with the sensitivities; the peak and the 82 W flag | M9's part on M9's D, the same |
| aifoundry1 card 0 (its own governor, 6 s bursts) | M10 carried through Q140(l)'s part and E170's card term at the fallback (κ0 0.9463), the die rise at 0.2415 °C/W | M9 carried the same way, rise at 0.1400 °C/W |

Bands are 95%. Nothing is refitted; every number comes from the frozen files.

## 7. Pool 8's scoring rules (item 7 of the brief; blind7's form)

**Common to all.** A tile's measured value is its mean over the kept (600 MHz) or counted (governed) passes on the session's registered
primary reduction (600 MHz: Q139(u)'s footing, E78's `reduce_e78.py` with the card's frozen leakage slope, `--no-refit`, the dips
removed once, as E163 and E164; governed: E165's `collect`); a tile with fewer than 2 is left out and named; fewer than 2 kept passes
in all: every rule NOT SCORED. **A tile with any launch whose C check is not PASS leaves every scored set** (Q139(k)'s rule; ROUNDING,
UNMODELLED, FAIL and a missing record are not PASS), and every rule is also given over all tiles beside. "Bootstrap" = the 2.5-97.5%
range of the rms (or the mean) of n errors drawn with replacement from the reference errors, 20,000 draws: **PASS** at or below the
97.5% point. "Paired" = the 95% interval of rms(a) − rms(b) over the set's tiles drawn with replacement, 20,000 draws: **BETTER** if its
upper end < 0, **WORSE** if its lower end > 0, else **NOT RESOLVED**. Seeds: 80,000 plus the sum of the rule id's character codes.
"Coverage" = **PASS** if the number inside the band is at least the 2.5% point of Binomial(n, 0.95). A rule over fewer tiles than its
minimum is NOT SCORED.

**The sets, from the manifest's bytes and fields only.** A **re-run** is a tile whose bytes equal a pool-6 or pool-7 tile's (whole-file
sha256, against `blind6.json` and `blind7.json`); re-runs are scored apart (LG, RR), never in N1. **N1** = every other non-anchor tile
of priority 1 (all of them if the manifest gives no priority); F1 its floats, I1 its int8; per format its fp32, fp16 and int8 tiles.
**KA** = the float check anchors. The scale anchors and zeros anchors are inputs, never scored. Classes (the manifest's `case`), real
tiles (`real`) and aims are reported per class, never in a rule.

**At 600 MHz (each session on aifoundry3 or card 1; each session is scored alone; a card's two sessions pooled are reported):**

| rule | quantity | set (minimum) | line | verdict |
|---|---|---|---|---|
| **P8-KC** | the C check | every launch of every pool-8 tile in a kept pass | bit-exact PASS | PASS / FAIL (it decides the scored sets) |
| **P8-P1** | rms(D − M10 primary) | N1's fp32 (6) | bootstrap from M10's held-out errors of fp32 rows on this card (`rows-m10.json` › `err_w["B+a+b"]`; aifoundry3 260 rows, 0.2019 W; card 1 190, 0.2004 W) | PASS / FAIL; below the 2.5% point "better than held out says" |
| **P8-P2** | the same | N1's fp16 (4) | fp16's (133 rows, 0.1476 W / 154, 0.1651 W) | as P1 |
| **P8-P3** | the same | N1's int8 (6) | int8's (`err_w["B"]`; 114, 0.1696 W / 108, 0.1849 W) | as P1 |
| **P8-B1** | mean(D − M10 primary) | F1 (8) | the bootstrap of the mean, the same format mix | PASS inside; FAIL HIGH below (M10 predicts too much); FAIL LOW above |
| **P8-B2** | the same | I1 (6) | as B1 | as B1 |
| **P8-C1** | M10's 95% band | N1 (10) | coverage | PASS / FAIL |
| **P8-M1** (the primary comparison) | M10 primary against M9, both at the measured rate | N1 (10) | paired | BETTER / WORSE / NOT RESOLVED |
| **P8-M1f**, **P8-M1i** | the same | F1 (8), I1 (6) | paired | the same |
| **P8-A1** | the session-scale arm (primary) against the a-priori arm (s = 1) | F1 (8) | paired | the same |
| **P8-KA** | the check anchors: e_p = D − M10 primary, e_0 = D − M10 a priori | KA (1 in the session; 4 for the reading pooled over pool 8's 600 MHz sessions) | Σ e_p² < Σ e_0², and every \|e_p\| inside M10's 95% band | PASS / FAIL; NOT SCORED if s = 1 |
| **P8-H1**, **H2**, **H3** | rms(dT_win − M10's 4.5 s rise at its primary D) | N1's fp32 (6), fp16 (4), int8 (6) | bootstrap from a normal sample of 2,000 points (seeded `Random("P8|heat-reference|<card>|<t>")`) at M10's held-out heat rms of the format and card (§ 1) | PASS / FAIL |
| **P8-H4** | M10's 4.5 s heat band | N1 (10) | coverage | PASS / FAIL |
| **P8-LG** | the re-runs' level or gain (below) | RR | two F tests | GAIN / LEVEL / BOTH / NOT SEPARATED |
| **P8-G** | M10 generalises on this card | — | P1, P2, P3, B1, B2 and C1 PASS, and M1 not WORSE | PASS; FAIL if any FAILs or M1 is WORSE; else NOT SCORED |

**P8-LG, the level-or-gain test of the float excess** (the card-half critic's rank 3, the Q142 critic's rank 5). For each float re-run
tile i in session σ on card c: Δᵢ = D_σ,i − D_ref,i, D_ref,i = the tile's registered primary mean in its own earlier session on the same
card (pool 6's tiles: E153 on aifoundry3, E157 on card 1; pool 7's: E163, E164; Q139(u)'s footing on both sides). Group r = the
reference session; a group counts if it holds at least 4 tiles spanning at least 8 W of D_ref. Fit by least squares the full model
Δᵢ = a_r + g_r D_ref,i, the level model Δᵢ = a_r and the gain model Δᵢ = g_r D_ref,i. **F_slope** tests the level model against the
full one (all g_r = 0), **F_level** the gain model against it (all a_r = 0), each at 5% with (k, n − 2k) degrees of freedom (k groups,
n tiles; n − 2k at least 4, else NOT SCORED). Verdict: **GAIN** if F_slope rejects and F_level does not; **LEVEL** if F_level rejects and
F_slope does not; **BOTH** if both reject; **NOT SEPARATED** if neither, with the null model Δ = 0 tested beside (an F test against the
full model: "the sessions agree" or "they differ, the form unresolved"). Reported: each group's a_r and g_r with intervals; every tile's
Δ with its Welch interval (`pick6.welch`); the same fit of M10's primary errors against the re-runs' D; the re-runs' D against M10 in
sample.

**What the 600 MHz outcomes would mean.**
- **P1-P3 PASS:** M10's held-out error per format (0.20 / 0.15-0.17 / 0.17-0.18 W) is the size of its blind error on new kinds. **FAIL:**
  the held-out figures were optimistic: the terms were named from pool 7's misses and the entry rule read the errors it reports.
- **B1 FAIL LOW or HIGH:** a session-wide float excess the session's anchors did not remove (LOW: the card read above M10).
- **M1 BETTER:** M10 is resolved better than M9 on kinds neither has seen: its refit and its two power terms generalise on this card.
  **NOT RESOLVED:** not shown at this n. **WORSE:** M10's changes hurt new kinds. M1f carries terms a and b; M1i carries the int8 refit
  alone (M10's int8 form is M9's refitted), so M1i is expected NOT RESOLVED.
- **A1 BETTER:** the session's own anchors improve predictions of new float kinds: term a generalises. **NOT RESOLVED:** its gain is
  within this pool's noise. **WORSE:** the anchors carry their own draws' miss, not the session's.
- **KA PASS:** the scale read from the scale anchors carries to a random draw it never read. **FAIL:** it does not, so term a reads its
  own anchors more than the session.
- **LG GAIN:** the session's float excess grows with D, the form term a assumes: term a stays. **LEVEL:** a constant per session, which a
  scale read at the anchors' D (about 22-25 W) under-corrects below it and over-corrects above it: the next model reads a level (anchors at
  two D, or a footing term). **BOTH:** the next model needs both. **NOT SEPARATED:** the form stays open.
- **H1-H4:** whether M10's refitted 4.5 s law holds blind per card (card 1's law reads 0.31-0.32 °C held out for floats).
- **G PASS:** "on new kinds drawn by a designer who saw no model's errors, M10 predicted power on this card within its held-out error,
  with no resolved bias, its bands covering K of n, and no worse than M9". FAIL is stated with the rule that failed.

**Under aifoundry2's own governor (E165's form; groups fixed by the frozen file: governed if M10 carried predicts the burst below
795 MHz at the fallback and T_ref):**

| rule | quantity | set (minimum) | line or reference | verdict |
|---|---|---|---|---|
| **P8-A2-G** | burst clock, M10 carried | governed (8) | rms ≤ 4.0 MHz AND \|mean\| ≤ 2.0 MHz (rank 2's lines) | PASS / FAIL |
| **P8-A2-Bg** | board W | governed (8) | \|mean\| ≤ 0.5 W | PASS / FAIL |
| **P8-A2-Bp** | board W | pinned (8) | \|mean\| ≤ 0.5 W AND rms ≤ 1.0 W | PASS / FAIL |
| **P8-A2-R2** | rank 2 on M10 carried | — | G, Bg and Bp all PASS | PASS; FAIL if any FAILs; else NOT SCORED |
| **P8-A2-F1**, **F2** | burst clock | governed (8), pinned (8) | bootstrap from Q140(l)'s end-to-end clock errors (36 governed cells, 4.50 MHz; 42 pinned, 2.33 MHz; `tools/claims-v3/e165/predictions-e165.json` › `reference`) | PASS / FAIL |
| **P8-A2-W1**, **W2** | board W | governed (8), pinned (8) | the same cells' board errors (0.78 W, 0.82 W) | PASS / FAIL |
| **P8-A2-M1** | board W: M10 carried against M9's part on M9's D | all scored (10) | paired | BETTER / WORSE / NOT RESOLVED (the clock's reported beside) |
| **P8-A2-H1** | burst die rise (aifoundry2's own law, unchanged) | all scored (10) | bootstrap from the burst heat law's 112 residuals (0.6845 °C) | PASS / FAIL |

**On aifoundry1 card 0 (E170's form):**

| rule | quantity | set (minimum) | line or reference | verdict |
|---|---|---|---|---|
| **P8-C0-W** | board W, M10 carried through the card term | every scored tile (8) | bootstrap from Q140(l)'s 42 end-to-end pinned board errors (0.8214 W) | PASS / FAIL |
| **P8-C0-B** | the same errors | the same | \|mean\| ≤ 0.5 W AND rms ≤ 1.0 W | PASS / FAIL |
| **P8-C0-M1** | burst D: M10 carried against M9 carried | the same (10) | paired | BETTER / WORSE / NOT RESOLVED |
| **P8-C0-F** | burst clock | the same (8) | the 42 pinned clock errors (2.334 MHz) | bootstrap |
| **P8-C0-H1** | die rise, M10's 0.2415 °C/W on the predicted board | the same (8) | bootstrap from term c2's 39 leave-one-tile-out residuals on E170 (0.3385 °C) | PASS / FAIL |
| **P8-C0-HK** | die rise at the measured board: M10's k against M9's 0.1400 | the same (8) | paired | BETTER / WORSE / NOT RESOLVED |

**What the governed outcomes would mean.** A2-M1 or C0-M1 BETTER: M10's D (its refit and term b's counts) improves the governed bursts
through a part fitted on measured D, so the 600 MHz gains carry to other clocks and cards. NOT RESOLVED: the part's own error (0.8 W)
hides the D difference. C0-H1 PASS with HK BETTER: card 0's burst heat coefficient, fitted on one session, holds on a second.

**Heat over minutes (HM).** On any hold a pool-8 session runs: the chain's plateau rise P (Q138(t)'s frozen chain on the hold's measured
board, arm A), the primary 1.0 × P and the arm 1.032 × P; over the holds with a measured rise of at least 10 °C: d = rms(primary) −
rms(arm), paired: **PRIMARY BETTER** if the interval's upper end < 0, **ARM BETTER** if its lower end > 0, else **NOT RESOLVED**; NOT
SCORED under 4 such holds. Meaning: ARM BETTER says the chain's gain deficit is real on new holds; PRIMARY BETTER says the 3.2% fitted
a level of the six sessions it read (as E144 suggested). Pool 8's planned sessions hold nothing, so HM is expected NOT SCORED; the
registered level-against-gain test of heat (the critic's rank 4(i) and 6) needs holds at two or more rise levels per session and its
own registration.

## 8. Precision, before the data

- **P8-LG** (`pool8/design-power.txt`; 5,000 draws, seed 142, re-runs' D spread evenly over 5-25 W, one group). The noise of one tile's
  difference between two sessions on one card, after each committed set's own two-term fit, is **0.037 W** (17 tiles; the measurement
  errors alone would give 0.058 W). At **12 re-runs** and that noise, a true gain of 0.6% of D reads **GAIN in 80%** of draws (NOT
  SEPARATED 15%), 1.0% in 95%, 0.3% in 29%; a true level of +0.11 W reads **LEVEL in 87%**, 0.05 W in 30%; no difference reads NOT
  SEPARATED in 93%, with GAIN and LEVEL wrongly 2% each. At 1.5 times the noise: 48% (0.6%) and 60% (0.11 W). At 8 re-runs, 57% and 68%;
  at 16, 90% and 94%.
- **The other rules' intervals** depend on the pool's counts per set; the predictor's `intervals` mode prints them at the pool's own n
  from the references above (deterministic), and the (x) lane commits them with the predictions.

**What I expect, frozen so it can be wrong.** KC PASS. P2, P3 PASS; P1 PASS or FAIL (fp32 carries the single high bits). B1 PASS
(the scale removes the session excess) or FAIL LOW; B2 PASS. M1f BETTER if the pool holds tiles whose three-point count misses (term b),
else NOT RESOLVED; M1i NOT RESOLVED; M1 NOT RESOLVED or BETTER. A1 NOT RESOLVED or BETTER (term a's held-out gain was 0.006 W pooled;
on a session reading 0.6% high, as pool 7's did, about 0.1 W). KA PASS. LG LEVEL or NOT SEPARATED (post hoc, E163 against E141 read a
level). H1-H3 PASS on aifoundry3; on card 1 H1/H2 PASS or FAIL. G PASS or FAIL on P1. On aifoundry2: A2-G PASS or FAIL (rank 2's clock
line held for M9), A2-M1 NOT RESOLVED. On card 0: C0-W PASS, C0-M1 NOT RESOLVED or BETTER, C0-H1 PASS, C0-HK BETTER. HM NOT SCORED.

## 9. The hash lists (item 7 of the `m10` field)

- [`POOL8-SHA256SUMS-62`](POOL8-SHA256SUMS-62): exactly the 62 files M10's chain opens that neither the registration's 174 nor M10's 68
  named (`section7-m10.json` › `rerun.data_opened_not_in_either_hash_list`): `docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json`,
  `tools/claims-v3/e145/predictions-e145.json` and 60 tile files of pools 6 and 7, with the sha256 recorded there (each re-hashed equal
  at this commit).
- [`POOL8-SHA256SUMS`](POOL8-SHA256SUMS), **209 files**: every repo file the predictor's chain opens or imports (201, traced on M10's
  committed self-test and the loaders the predictor calls; the 62 among them), plus eight named: `m7.json` (M7's heat band factor),
  `a2-checks-m10.json` (§ 4's offsets), M10's `SHA256SUMS-a2`, Q140(l)'s `REGISTRATION.md` (rule E's reading), `RECOUNT-RULE.md`,
  `tools/claims-v3/e165/predictions-e165.json` (the A2 rules' reference) and this registration's design script and output. Paths are
  relative to the repo root (`shasum -a 256 -c` from there). [`pool8-registration.json`](pool8-registration.json) is this file's
  numbers, which the predictor reads.
- After this lane every earlier list must still pass: `blind7/SHA256SUMS` (91), `blind6/SHA256SUMS` (80), `frozen-sha256-e168.json` (9),
  `frozen-sha256-e168-scorer.txt` (18), `predict_q140e.py`'s 26, M10's registration's 174, M10's 68 and `SHA256SUMS-a2` (10).

## 10. The order of the freeze

1. This registration (one commit, new files only).
2. The predictor, its self-tests and their output, its README and hash list (the next commit, new files only).
3. The next round's (x) lane: pool 8 copied unchanged into `tools/claims-v3/kinds/blind8/`; the bench's three standard points for every
   tile and § 2's steps for every float tile, on the mini (the predictor's `plan` says which points); `predict` for aifoundry3,
   aifoundry1c1, aifoundry2 and aifoundry1c0; aifoundry2's tiles over 82 W marked; the intervals; one commit before any claim.
4. The card lanes' kits (E163's to E170's forms) read those predictions, and their registrations descend from this commit and step 3's.
5. Scoring: per session, `scale` from the anchors' items only, then `primary`, then the rules above.

## 11. What this cannot say

- **Term a needs the session's own anchors.** The primary is computed after the anchors run; the a-priori arm is the only prediction
  made before a session in full.
- **The level-or-gain test compares two sessions,** the new one and each re-run's reference. It says whether their difference is a
  level or a gain, not which session is "right".
- **aifoundry2 and card 0** test M10's D through a part fitted on measured D at 800 MHz; the part's own error (about 0.8 W on the board)
  limits what a D difference of a few tenths of a watt can show.
- **Card 0's burst heat (c2) rests on one session**; pool 8's card-0 session is its second.
- **Heat over minutes** is scored only if a hold runs.

## 12. Compute

Desk only. The design arithmetic and the file trace ran on the Intel through the round's local slot (one job each, under a minute,
nice 10); the predictor's self-tests run the same way. The bench counts are the (x) lane's, on the mini. No lab box is used tonight:
their sign-in checks are pending, and the round's rule keeps every job off them.
