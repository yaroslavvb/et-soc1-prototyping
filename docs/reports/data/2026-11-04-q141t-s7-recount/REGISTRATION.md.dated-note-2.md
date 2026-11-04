# Amendment A1 beside REGISTRATION.md (Wed 4 Nov 2026, about 12:15 PST; Q141(t)'s fix pass)

*Written and committed **before any pool-7 data**. No data of any E163-E169 run exists: at 12:12 PST `origin/main` held no data
directory for E163-E169 and no run output under `tools/claims-v3/e163/` or `e164/`, only their registrations and kits. So this
correction to a committed registration is a dated amendment, made now, before the data it touches.*

*REGISTRATION.md (`0830f65b`) and its first dated note (`67d5e44f`) stay as committed. The arm's frozen numbers (`arm-s7.json`), the
scorer `score_s7arm.py` and its self-test stay frozen too. A1 fixes two faults the lane's verifier found in the scorer's readings
(A1-1, A1-2). It also adds one reported reading (A1-3), found while writing R5's known-answer tests. It is applied by a new file,
[`score_s7arm_a1.py`](score_s7arm_a1.py), which imports `score_s7arm.py` unchanged. Its self-test is
[`selftest-score-s7arm-a1.txt`](selftest-score-s7arm-a1.txt) (PASS).*

## A1-1. R5 is read only where R2-R4 are, and only over all four bit-20 tiles

- **Section 3 registers** two things:
  - "At least 5 of the 7 S7 tiles need a measured D, else R2-R5 are 'not read'";
  - R5 over "the four fp32 bit-20 S7 tiles ... with 3 degrees of freedom", read "if p < 0.05 (χ² > 7.815)".
- **What `score_s7arm.py` does:** its `r5()` reads R5 whenever 3 of the 4 bit-20 tiles are measured, whatever the S7 count, and
  at 2 df when one is missing. So with only the four bit-20 tiles measured (4 of 7), R2-R4 come out "not read" but R5 is read (the
  self-test's T1 c shows the frozen function doing it).
- **The rule from now on**, per card:
  - R5 is read only if the card's R2-R4 are read (at least 5 of the 7 S7 tiles measured) **and** all four bit-20 tiles are
    measured. It is then `score_s7arm.r5()`'s output, unchanged: four tiles, 3 df, read at p < 0.05.
  - Otherwise R5 is "not read", with the reason.
  - **R5-3, a named departure.** Where R2-R4 are read and exactly 3 of the 4 bit-20 tiles are measured, the same statistic over
    the three (2 df) is reported beside the "not read", for information only. It is never read as a base-word price.

## A1-2. Heat gets the same R1 and R2 as power

- **Section 3 registers** "the same R1 and R2 on M9's dT_win at 3 and 27 points".
- **What `score_s7arm.py` does:**
  - per tile: the measured rise ± se, dT3, dT27, r3 and r27;
  - per card: only rms and mean at 3 and 27 points.

  So it has no k ± u, no 2σ flag, no check of the run's prediction, no bootstrap interval and no pooled reading.
- **R1, per tile and card,** adds:
  - **k_dT = dT3 − dT27 ± u_dT**, with u_dT = g × u. Here g is M7's frozen coefficient on S for the card (`m7.json` `heat.coef`,
    `3a210f2b`): 0.11855 °C/W on aifoundry3 and 0.11511 on card 1. M9 carries M7's heat law dT_win = g × S. S − D does not
    depend on the counts, so the counting error in the rise is g × u.
  - **σ_dT = √(u_dT² + se²)**, and the flag |r27| ≤ 2σ_dT ("inside its counting and measurement error"). The heat band is much
    wider than σ_dT, so this flag will often read "no".
  - **The run's M9 dT_win prediction**, where its rows carry one, checked against dT3. A difference above 0.0005 °C is flagged.
- **R2, per card and pooled:**
  - n, and the rms and mean of r3 and of r27;
  - Δrms = rms(r27) − rms(r3) and mean(r27), each with a 95% percentile interval from power R2's paired bootstrap over tiles,
    unchanged (`score_s7arm.boot`: 20,000 draws; seed 141 on aifoundry3, 142 on card 1, 143 pooled; the pooled draw carries both
    cards' rows of a tile together);
  - at least 5 of the 7 S7 tiles with a measured rise, else "not read".
- Heat has no R3 or R4, as registered.

## A1-3. R5m, reported beside R5: does the scatter exceed M9's ordinary error?

**What R5 measures.** R5's σ_i holds only counting and measurement error (σ_i² = u_i² + se_i²). It leaves out M9's own per-tile
price error, about 0.20 W rms on fp32: M9's frozen band pool (`m9.json` `interval_pool_by_format_card`) gives 0.2001 W on aifoundry3
and 0.2112 W on card 1. So R5 reads M9's ordinary per-tile error as a base-word price.

**How often, from the self-test's T4** (20,000 draws a world, fixed seeds, se 0.03 W a tile):

| world (no base-word price unless named) | R5 aifoundry3 | R5 card 1 | R5m aifoundry3 | R5m card 1 |
|---|---:|---:|---:|---:|
| equal σ, the exact χ²(3) case (a known answer: 5%) | 0.0505 | 0.0522 | — | — |
| the arm's σ, counting and measurement only | 0.0679 | 0.0671 | 0.0008 | 0.0006 |
| plus M9's ordinary error | **0.3590** | **0.3900** | **0.0546** | **0.0633** |
| plus M9's ordinary error and a 0.6 W price on one of the four tiles | 0.7638 | 0.7945 | 0.3382 | 0.3271 |

How to read the table:
- **M9's ordinary error** is one draw per tile, independently, from M9's nested fp32 errors on that card (`rows-m9.json`, `1f244140`:
  241 rows on aifoundry3, 171 on card 1). If the four tiles' errors share a common part, R5 removes it with their mean, so both rates
  would come out lower.
- **Counting and measurement only:** R5 reads a little above 5% there because the registered statistic centres on the unweighted
  mean. Its expected χ² is 3.27, not 3.

**R5m.** It is the same statistic on the same tiles under A1-1's gate, with the card's M9 fp32 band pool rms m added in quadrature to
each σ_i:
- χ² = Σ (r27_i − mean)² / (σ_i² + m²), on 3 df, read at p < 0.05, and reported on r3 beside it;
- in the R5-3 case, the 2-df statistic is reported with m too, never read.

**What it changes:** a reading only.
- R5 stays as registered, with A1-1's gate.
- R5m is reported beside it and never replaces it.
- Records quote a READ of R5 with its 36-39% rate when no base-word price exists. R5m is the reading that separates a base-word
  price from M9's ordinary error, at about 5.5-6.3% when none exists and about 33% for a 0.6 W one.

## What does not change

- The arm's numbers: P3, P27, k and u per tile and card (`arm-s7.json`), and the hand-off files `arm/arm27-<card>.json`.
- M9's frozen predictions, primary on every tile.
- R1 (power), R2-R4 per card and pooled, and R6. They are `score_s7arm.py`'s output, unchanged.
- `score_s7arm.py` and its self-test. Both stay frozen, and the self-test still gives PASS when re-run (T0).
- E163's and E164's registrations, rules and scorers.
- No verdict on M9. Every reading of the arm stays reported only.

## The wrapper and its self-test

**The wrapper.** `score_s7arm_a1.py` refuses to score if any of these differ from their committed bytes: `score_s7arm.py`,
`arm-s7.json`, `m9.json`, `m7.json`, or E153's or E157's `scored.json`. Its `--selftest` runs in about 16 s on one core and gives
**PASS**:
- **T0:** the ten frozen inputs hash as committed. `score_s7arm.py --selftest`, re-run in the same process, gives PASS with its text
  identical to the committed one.
- **T1:** R5's gate and values, on seven known-answer cases per card:
  - everything measured;
  - a base-word pattern at 1.02 × and at 0.98 × 7.815;
  - 4 of 7 S7 tiles measured;
  - 5 of 7 with three bit-20 tiles (R5-3);
  - 6 of 7;
  - 5 of 7 with two bit-20 tiles.

  The statistics equal an independent sum to 1e-9, and the p values equal the closed forms at 3 and 2 df to 1e-9.
- **T2:** R6's known answers, unchanged by A1:
  - a1p5's r27 set to +0.25 W, against pool 6's committed +0.064 W on aifoundry3 (−0.251 W on card 1), with the ± of the two σ;
  - a1p5 missing: R6 not read;
  - a1p5 alone: R6 read, R2-R5 not read.
- **T3:** heat.
  - The law: dT = g × S to the rounding on all 16 tile-cards, and k_dT = g × k.
  - R1's new fields, and R2's intervals per card and pooled.
  - The gate: rises on only 4 of 7 S7 tiles give "not read".
  - The prediction flag.
- **T4:** the rates in the table above.
- **T5:** the route through E163's and E164's own scorers.
  - A simulated E163 session goes through `score_e163.run` with `arm/arm27-aifoundry3.json`. A simulated E164 session goes through
    `score_e164.run` with `arm/arm27-aifoundry1c1.json` as its `--s-recount`. Each comes from that run's own committed self-test
    simulator.
  - Both scored forms are read: E163's under `primary.primary`, E164's under `primary`.
  - All 8 tiles are read on each card. The run's M9 predictions equal P3 and dT3.
  - E163 reports 8 `reported_arm27` rows and E164 8 `reported_s_recount_arm` tiles, at the files' values.

**How to run it:** README.md.dated-note.md § 2 gives the three routes by which E163's and E164's results reach the arm.
