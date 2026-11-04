# Q140(m), fix pass: the convergence rule for the bench's launch average, registered before any recount

*Wed 4 Nov 2026 (week 45), about 02:00 PST, on the Intel, desk only (no card, no device command, no lab box, Discord, Modal or
archive). Written after M9's freeze (`1f244140`, [`../README.md`](../README.md)) and after the verification of Q140(m), which found that the
nine-point launch average the bench check used is itself not converged (the README's dated correction C1). Written and committed
**before any bench count at more than nine launch points exists**. It answers that finding and the Q139 final critic's open
**rank 1** (the base-word term for single bits), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6**.*

**What it does not touch.** M9 stays as frozen in `1f244140`. Its training rows and its predictions for pool 7 use the bench's
three launch points, as [`../M9-REGISTRATION.md`](../M9-REGISTRATION.md) registered. That registration's § 8 stays as committed:
this file is a new registration for a later recount, not an amendment of it, and it changes no fit, score, band or prediction.

**Read before writing this:** the committed nine-point counts of the 16 calibration tiles (`../bench-check/counts-cal.json`), the
verifier's reading of them, and `e(9)` for each tile, computed with the code below (it is printed in § 5). No count at 27 points
existed when this was written.

## 1. The estimator

The bench counts one op at op index n0 of a 0.5 s launch at 600 MHz, with C at its value there (`rtl-sim/fma_toggle_v2`,
`run_kinds.py`). A tile's launch average at N points is the mean over the midpoints of N equal parts of the launch:
n_j = int(ops (2j + 1) / 2N), ops = 0.5 × 600e6 / 546, for N = 3^m. Each set holds the one before (the bench's three points are
among the nine, the nine among the 27), so a step counts only the new points. The bench is deterministic: a point counted again
gives the same counts (the bench check reproduced pool 6's committed three points exactly).

## 2. The error of an N-point average, in watts

Each point is priced at **M9's frozen float prices** (`../m9.json`), with the stage mapping of `../benchcheck_m9.py`: multiplier at
`mult`, adder_norm at `add32` (fp32) or `add16` (fp16), lane_operand_bus at `bus`, every other stage at `rest`, and the exponent
stage at `rest` + `xstage`, times the type's op rate. That gives W of D per point. Two estimates of the N-point mean's error:

- se_sample(N) = the sd of the N points (ddof 1) / √N;
- se_interleaved(N) = the sd of the three interleaved N/3-point rules' means (points j ≡ 0, 1, 2 mod 3) / √3.

**e(N) = the larger of the two.** The code is [`recount_rule.py`](recount_rule.py), committed with this file.

## 3. The bound

**e(N) ≤ 0.10 W of D.** That is about half of M9's nested float error over every row (0.193 W) and of the Q139 critic's bound
for pool 6 without its six named misses (0.17-0.19 W). A single-bit term fitted on counts whose launch average carries more than
that would partly fit the bench's quadrature rather than the card.

## 4. The calibration set, and N*

- **The set:** the 16 single-bit calibration tiles of M9's bench check (`../bench-check/cal-tiles.json`: four base words, bits 12,
  17, 20 and 21).
- **Stepping:** each tile starts at N = 9 (counted). A tile with e(N) > 0.10 W is counted at 3N; one that meets the bound is not
  counted further. The cap is N = 243.
- **N\*** = the largest of the 16 tiles' first N meeting the bound. It is undetermined while any tile has not met it.
- **If a tile does not meet the bound at 243**, uniform launch points cannot give its launch average to 0.10 W at an affordable
  cost. The next model then either carries that tile's e(N) as a known error on rows like it, or registers another estimator
  before using one, for instance points stratified by C's state computed in software (`accum.c` gives C at any op index for free).

## 5. Tonight's step: the sizing pilot

- **Tiles:** the 14 with e(9) > 0.10 W ([`pilot-tiles.txt`](pilot-tiles.txt)). The two that meet it at nine, `cal_w79_b12` (0.095 W)
  and `cal_pi_b12` (0.078 W), are not counted further.
- **e(9) per tile**, W (se_sample / se_interleaved): third b12 0.121 / 0.114, b17 0.219 / 0.267, b20 0.376 / 0.508, b21 0.711 /
  0.978; w67 b12 0.099 / 0.105, b17 0.165 / 0.158, b20 0.319 / 0.370, b21 0.479 / 0.491; w79 b17 0.139 / 0.014, b20 0.327 / 0.526,
  b21 0.393 / 0.479; π b17 0.123 / 0.109, b20 0.407 / 0.653, b21 0.429 / 0.421.
- **Points:** the 18 new ones of N = 27 ([`points27-new.txt`](points27-new.txt)), 252 in all.
- **Bench:** the same build as the bench check (its seven files hash as `../bench-check/bench-sha256.txt`, checked before the
  run), at nice 10 with **3 jobs**, so the lane stays within 4 cores with one left for everything else. C is checked against
  software at every point (`check_mismatch` 0, else `recount_rule.py` stops).
- **Outputs:** `counts-pilot27.json`, `pilot-run.json` (wall time, jobs, points), and `recount-rule.json` / `.txt` written by
  `recount_rule.py`.
- **If 27 points do not bring every tile under the bound**, N* stays undetermined. The next step is the 81-point count of the tiles
  still above it, run by the recount lane before its recount. The 1/√N law's projection (N × (e(N) / 0.10)²) is reported for
  planning only, never in place of counts, beside the measured ratio e(9)/e(27) (√3 = 1.73 under that law).

## 6. The recount this sizes (not run here)

The recount covers:
- the 45 counted tiles behind the 77 float rows of M9's whose whole-VPU nets spread over 10% between the bench's three points
  ([`recount-set.json`](recount-set.json));
- E147's 70 tiles (`../../2026-11-02-e147-bit-prices-rest/bench/counts-e147.json`), items and zeros;
- pool 7's float tiles, after pool 7 has scored M9.

**Each recount tile is counted from 9 points and tripled while its own e(N) > 0.10 W, never beyond N\***. A tile above the bound at
N* is reported with its e(N*). The cost is the sum over tiles of (N_tile − 3) points × the pilot's measured seconds a point / the
jobs. The single-bit term fitted on the recount is the next model's, registered separately before any fit.

## 7. What is reported (no verdict on M9)

- Per calibration tile: e(9), e(27) and the ratio between them; N*, or "not yet" with the tiles still above the bound; the 1/√N
  projection (planning); the cost a tile at 9, 27, 81 and 243 points.
- **Post hoc:** pool 6's two twins of calibration tiles (`fp32.b_onebit_b20_third`, `fp32.b_onebit_b12_third`), M9's error with the
  three-point launch average replaced by the largest N counted, ± e(N). Both on M9's nested error and on the frozen form's own
  leave-one-kind-out error, whose prices are the ones the correction uses. On b12_third the nested error comes from another form
  (the one holding `lq1`), so only the frozen form's figure is like for like there.
