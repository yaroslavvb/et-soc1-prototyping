# Q141(t): pool 7's single high bits recounted at 27 launch points, registered as a reported arm before any count

*Wed 4 Nov 2026 (week 45), about 09:10 PST, on the Intel, desk only: no card is claimed, no device command is sent, no lab box,
Discord, Modal or archive is touched. Written and committed **before any of the counts it names exists** and **before any pool-7
measurement exists**. It answers the Q140 final critic's open **rank 4** ("single high bits: the bench's counting vs a missing
price") through its `desk_next` 6 (this arm) and 10 (the convergence rule's 81-point step), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** (a new kind's power,
predicted blind).*

## 0. What it descends from, and what exists now

- **Pool 7**, `tools/claims-v3/kinds/blind7/`: lab `75802201` (03:27:39 PST) with Q140(x)'s dated notes `3c9bb2ba` (04:18:24 PST).
  Its 61 tiles, the bench's three-point counts `counts-blind7.json` (sha256 `07499225…`) and the frozen predictions
  `predictions-blind7-aifoundry3.json` (`303dc5b9…`) and `predictions-blind7-aifoundry1c1.json` (`22fe64be…`).
- **M9**, `docs/reports/data/2026-11-04-q140m-m9/`: frozen `1f244140` (01:12:04 PST), registered `8dfafae3`; `m9.json` (`322dd739…`),
  `predict_blind7.py` (`32b5cdac…`), `fit_m9.py` (`0b3f1074…`).
- **The convergence rule**, `docs/reports/data/2026-11-04-q140m-m9/recount-rule/`: registered `b4444dd4` (01:53:26 PST), the 27-point
  pilot `b85ca0f9` (02:37:55 PST). At 27 points 6 of its 16 calibration tiles meet the bound and 10 do not (`recount-rule.txt`).
- **Q140(x)'s notes check** `A1_2` (`docs/reports/data/2026-11-04-q140x-blind7-notes/notes-check.json`): pool 7's
  `fp32.b_onebit_b20_pi` is byte for byte M9's bench tile `fp32.cal_pi_b20`, whose committed 27 points put the three-point D
  0.311 ± 0.198 W low.
- **No pool-7 measurement exists.** Checked by `git log origin/main` at 09:05 PST: no `tools/claims-v3/e163/`, `e164/`, no
  `docs/reports/data/*e163*` or `*e164*`, and no commit after `3c9bb2ba` touches pool 7. No count of any pool-7 tile at more
  than the bench's three points exists, except `fp32.b_onebit_b20_pi` through its byte twin above.

## 1. The arm

**Name:** `M9_27pt`, "M9's frozen prices on 27-point counts". **Reported only.** It never replaces E163's or E164's primary, never
enters their registered rules, and carries no verdict on M9. **M9's frozen predictions stay primary**, unchanged.

**Tiles (8):** pool 7's class S, its seven priority-1 tiles `fp32.b_onebit_b20_one`, `fp32.b_onebit_b20_full`,
`fp32.b_onebit_b20_pi`, `fp32.b_onebit_b20_seventh`, `fp32.b_onebit_b22_third`, `fp16.b_onebit_b9_one`, `fp16.b_onebit_b8_pi`
("S7" below), and beside them the priority-2 b20-on-1/3 tile `fp32.b_onebit_b20_third_a1p5`, never in S7.

**Cards:** aifoundry3 (E163) and aifoundry1 card 1 (E164), the two 600 MHz cards.

**Counts come from the tiles' bytes only.** For each of the 8 tiles, the bench (`rtl-sim/fma_toggle_v2`'s `run_kinds.py`, unchanged)
counts all 27 points of RECOUNT-RULE.md section 1 (n_j = int(ops (2j + 1) / 54), j = 0-26, ops = 0.5 × 600e6 / 546): the 24 new
ones and the three standard ones again.
- **The build:** Q133(b)'s, whose seven files must hash as `../2026-11-04-q140m-m9/bench-check/bench-sha256.txt` (checked by
  [`bench_s7.py`](bench_s7.py) before it starts).
- **The tiles:** pool 7's files, which must hash as its `MANIFEST` (also checked).
- **The run:** 4 jobs at `nice -n 10` (section 26: this lane's bench may use 4 cores).
- **C** is checked against software at every point (`check_mismatch`). A point with a mismatch stops the arm: nothing is frozen.

**Two determinism checks, registered expectations.** A failure of either stops the arm (nothing is frozen) and is reported.
- **D1:** each tile's three standard points reproduce its committed `counts-blind7.json` row exactly: `vpu`, `unit`, `ff` and
  every other counted field.
- **D2:** `fp32.b_onebit_b20_pi`'s 27 points reproduce its byte twin `fp32.cal_pi_b20`'s committed 27 points exactly
  (`bench-check/counts-cal.json` plus `recount-rule/counts-pilot27.json`).

**The 27-point launch average, and the arm's predictions.** Each tile's row `mean` is run_kinds.py's own `mean_rows` over its 27
points. Its `points` keep the three standard ones, so that `fit_m9`'s launch-shape candidate `lq1` is computed as frozen: it
asserts three points. `lq1` is in none of M9's, M8's, M7's or M6's kept forms, so it enters no prediction. Every other feature of
the frozen code reads the row's `mean` (the bench's stage counts and clocked bits) or the tile's bytes.

A counts file holds these 8 rows and pool 7's other 53 committed rows unchanged. The frozen `predict_blind7.py` is run on it, as a
script, unchanged, for `aifoundry3` and `aifoundry1c1`, into `arm/`. That gives M9's D, its 95% band, S and the 4.5 s die rise,
with M9's frozen prices, card term (`card1_scale_by_format`, 0.9616 on card 1) and band rule. M8's, M7's and M6's figures on the
same counts come out beside them: they are reported, not part of the arm.

**Checks on the predictions:**
- the other 53 tiles' predictions must equal the frozen files' exactly;
- the frozen predictor re-run on the committed counts must rewrite the frozen files byte for byte (checked before this file:
  both cards, JSON and Markdown identical).

**The arm's frozen numbers per tile and card** (in `arm-s7.json`, committed with the predictions):
- P3: M9's frozen primary D;
- P27: the arm's D;
- **k = P3 − P27**, the three-point count's error at M9's prices, known before any card data;
- u = s × e(27), its 1-s.e. counting error (s = 1 on aifoundry3, 0.9616 on card 1).

## 2. Convergence, by the registered rule

e(9) and e(27) per tile come from RECOUNT-RULE.md section 2's code: `recount_rule.py`'s `points`, `prices`, `point_w` and `err`,
imported unchanged, at M9's frozen float prices (fp16's adder at `add16`). The bound is e(N) ≤ 0.10 W.
- **Reported per tile:** e(9), e(27), met or not, and the three-point minus N-point difference at the rule's stage prices. That
  difference leaves out the `clk` term that P3 − P27 includes, so both are reported.
- **Check:** the same per-tile code, applied to the 16 calibration tiles' committed counts, must reproduce `recount-rule.json`'s
  by-N figures.

**A tile above the bound at 27** is reported with its e(27) as the arm's remaining counting error. The arm stays at N = 27 for every
tile: there is no stepping here.

**Departures from RECOUNT-RULE.md section 6, named:**
- **(a) Timing.** Section 6 planned to recount pool 7's float tiles *after pool 7 had scored M9*. This recount runs *before any
  pool-7 data*, on the Q140 critic's `desk_next` 6, as a reported arm. M9's primary and its inputs are unchanged, so its blind
  score is untouched.
- **(b) N is fixed at 27 for all 8 tiles.** They are not stepped from 9 while e(N) > 0.10 W, so the arm is one estimator across
  the class.
- **(c) The three standard points are counted again**, as checks D1 and D2. Section 1 says a recount need not.

## 3. The readings (reported; no verdict on M9, no PASS or FAIL)

Per card (E163 on aifoundry3, E164 on aifoundry1 card 1) and per tile i:
- From the run's rows, in E153's and E157's scored form: D_i (`power_rows[model][tile].measured`), and se_i = sd_i / √n_passes.
  The reduced form `items[tile].D` {mean, se, n} is read the same way.
- **r3_i = D_i − P3_i** is the primary's error. **r27_i = D_i − P27_i** is the arm's error, "the price part". So r3 = r27 − k.
- σ_i = √(u_i² + se_i²).

| reading | what it reports |
|---|---|
| **R1**, per tile | D ± se, P3, P27, k ± u, r3 and r27. A flag says whether \|r27\| ≤ 2σ: "inside its counting and measurement error". The run's M9 `pred`, where its rows carry one, is checked against P3. A mismatch is flagged. |
| **R2**, the class S7 | Per card and pooled. n; rms(r3) and rms(r27); mean(r3) and mean(r27). Δrms = rms(r27) − rms(r3), and mean(r27), each with a 95% percentile interval from a paired bootstrap over tiles: 20,000 draws; seed 141 on aifoundry3, 142 on card 1, 143 pooled. The pooled bootstrap draws tiles and carries both cards' rows of a tile together. **At least 5 of the 7 S7 tiles need a measured D**, else R2-R5 are "not read". |
| **R3**, the counting share | 1 − Σ r27² / Σ r3² over S7: the share of the primary's squared S-class error the 27-point counts remove. It is negative if they add to it. |
| **R4**, the split | **PRICE** (a missing price on the S class) if mean(r27)'s interval excludes 0 and \|mean(r27)\| > 0.10 W, the recount bound. **COUNT** (the count carries the S class's miss) if Δrms's interval lies below 0 and \|mean(r27)\| ≤ 0.10 W. **COUNT+PRICE** if Δrms's interval lies below 0 and PRICE holds. Otherwise **NOT SEPARATED** at this precision. |
| **R5**, base words | Over the four fp32 bit-20 S7 tiles (1.0, 0x3FFFFFFF, pi, 1/7): χ² = Σ (r27_i − their mean)² / σ_i², with 3 degrees of freedom. A **base-word-dependent price** is read if p < 0.05 (χ² > 7.815). The same statistic on r3 is reported beside it. |
| **R6**, A = 1.5 | r3 and r27 of `fp32.b_onebit_b20_third_a1p5`, beside pool 6's `fp32.b_onebit_b20_third` (the same B half, A = 1.0) on the same card. For the pool-6 tile, D comes from E153 and E157; P3 and P27 come from the same machinery on its byte twin `cal_third_b20`'s committed 27 points. This is post hoc for the pool-6 half, because M9 was fitted on those rows. The difference of the two r27 is reported ± √(σ² + σ²). |
| **Heat** | Where the run's rows carry the measured 4.5 s rise (`heat_rows`), the same R1 and R2 on M9's dT_win at 3 and 27 points. |

**Missing tiles.** A tile the run sets aside, or one whose C check fails (excluded by the run's own rules), is left out and named.
The run's own rules decide which passes count; this arm only reads the rows they leave.

## 4. The 81-point step (the Q140 critic's `desk_next` 10; RECOUNT-RULE.md sections 4-5)

This step follows the registered stepping rule: a tile with e(N) > 0.10 W is counted at 3N; one that meets the bound is not
counted further; the cap is N = 243.
- **Tiles:** the 10 calibration tiles above the bound at 27: `cal_third_b17`, `cal_third_b20`, `cal_third_b21`, `cal_w79_b20`,
  `cal_w79_b21`, `cal_w67_b17`, `cal_w67_b20`, `cal_w67_b21`, `cal_pi_b20` and `cal_pi_b21`.
- **Points:** the 54 points of N = 81 that N = 27 does not hold, for each tile.
- **Bench:** the same build, checks, jobs and niceness as § 1.
- **Order:** five runs of two tiles each, in the order listed, so a stopped run loses at most one pair.
- **Bench time:** up to about 1.5 bench-hours from the step's start. A pair that cannot start inside that is not counted, and is
  named.
- **e(81) and N\*:** computed by `recount_rule.py`'s `main()`, unchanged, on `counts-cal.json`, `counts-pilot27.json` and this step's
  counts, with its output directory pointed at `step81/`. N\* is the largest first-N meeting the bound over the 16 tiles. It is
  "not yet" while any tile is above the bound; then the tiles above it are named, with their 1/√N projections (planning only, never
  in place of counts) and the cost of the 243-point step.
- **Commit:** its own commit, after the arm's.

## 5. What it does to predicting power and heat

- **The term tested:** the bench's launch average (counting) against a missing single-bit price, on the S class.
- **What it makes scorable:** E163's and E164's S-class blind errors can be split into counting and price. That is the question
  Q140(m) left open (its correction C1: the three-point count errs by up to about 1 W on high single bits).
- **What it does not change:** no frozen prediction, band, rule or verdict changes. M9 stays primary on every tile, and E163's and
  E164's registrations are their own.
- **Heat:** the arm's die rise moves with its D, through M7's heat law (which M9 carries). It is reported beside the primary's.
- **Error before and after:** none yet. The S class's blind error under M9 exists only after E163 and E164. This arm's
  three-point corrections k, frozen now, are the size of the counting part before any data.

## 6. Files

**Committed with this registration:**
- this file;
- [`bench_s7.py`](bench_s7.py), the bench driver behind the build and tile hash checks.

**Committed with the arm, before any pool-7 data** (each a new file in this directory):
- the 27-point counts and their run record;
- the builder `make_arm_s7.py`, its counts file, `arm/predictions-*.json` and `.md`, and `arm-s7.json`;
- the convergence table `recount-s7.json` and `.txt`;
- the scorer `score_s7arm.py`, with its self-test output on E153's and E157's committed data. The self-test must reproduce, for
  M8 as registered then: each committed power row's error and inside flag; the P1-P3 and C1 verdicts from their rows against
  their committed intervals and bounds; and E153's committed S-class reading. Then the arm machinery on pool 6's two byte twins,
  post hoc.

**The 81-point step:** `step81/`, its own commit.
