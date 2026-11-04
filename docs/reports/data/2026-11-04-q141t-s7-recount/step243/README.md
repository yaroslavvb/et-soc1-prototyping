# Q141(t2): the convergence rule's 243-point step on the 8 calibration tiles above the bound at 81 points

*Wed 4 Nov 2026 (week 45), counts 13:27-14:08 PST on the mini, desk only (no card, device command, lab box, Discord, Modal or archive). Registered in [`../REGISTRATION-step243.md`](../REGISTRATION-step243.md) (`9496466c`, 13:26:09 PST, before any 243-point count), under Q140(m)'s [RECOUNT-RULE.md](../../2026-11-04-q140m-m9/recount-rule/RECOUNT-RULE.md) sections 4-5 (`b4444dd4`) and Q141(t)'s [`../REGISTRATION.md`](../REGISTRATION.md) section 4. It answers the Q141 final critic's `desk_next` 4, under the Q140 final critic's open **rank 4** (the bench's counting against a missing single-bit price), for the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6**. Reported only: no frozen prediction, price, card term, band or rule changes.*

## Results

**1. 7 of the 8 tiles meet the bound at 243 points; 1 does not (`fp32.cal_third_b21`). N\* is not reached by uniform points at the cap (243).** Figures are from [`recount-rule.json`](recount-rule.json) and [`recount-rule.txt`](recount-rule.txt), written by `recount_rule.py`'s `main()` unchanged; the summary is [`summary243.txt`](summary243.txt).
- With the 8 tiles that met the bound at 9, 27 or 81 points, **15 of the 16 calibration tiles** now meet it.
- `main()` itself prints "N* = not yet determined". At the cap, as REGISTRATION-step243.md section 3 registered, that reads "not reached by uniform points": 243 is the rule's cap, so `recount-rule.json`'s `next_step` ("count ... at 3 x their N") does not apply.

| tile | e(9) | e(27) | e(81) | e(243) | e(81)/e(243) | outcome | mean at 243 (W) | 3pt − 243 (W) |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| `fp32.cal_third_b21` | 0.978 | 0.389 | 0.221 | 0.125 | 1.77 | **above the bound at the cap** | 5.543 | −0.032 |
| `fp32.cal_pi_b21` | 0.429 | 0.260 | 0.154 | 0.092 | 1.67 | met at 243 | 4.347 | −0.284 |
| `fp32.cal_third_b20` | 0.508 | 0.267 | 0.147 | 0.088 | 1.66 | met at 243 | 4.584 | +1.049 |
| `fp32.cal_w67_b21` | 0.491 | 0.267 | 0.140 | 0.084 | 1.68 | met at 243 | 4.828 | +0.514 |
| `fp32.cal_w79_b21` | 0.479 | 0.209 | 0.120 | 0.072 | 1.68 | met at 243 | 4.680 | +0.778 |
| `fp32.cal_w67_b20` | 0.370 | 0.201 | 0.115 | 0.064 | 1.81 | met at 243 | 4.390 | +0.933 |
| `fp32.cal_w79_b20` | 0.526 | 0.173 | 0.108 | 0.061 | 1.77 | met at 243 | 4.123 | +0.944 |
| `fp32.cal_pi_b20` | 0.653 | 0.198 | 0.100 | 0.055 | 1.82 | met at 243 | 4.220 | −0.157 |

How to read the table:
- e(N) is in W of D at M9's frozen float prices: RECOUNT-RULE.md section 2's larger of the sample and interleaved standard errors.
- "3pt − 243" is the bench's three-point average minus its 243-point average at those prices.
- The bound is e(N) ≤ 0.10 W. 243 is the rule's cap, so a tile above the bound there gets no N = 729 step.

**2. `fp32.cal_third_b21` stays above the bound, so the registered fallback F1 applies.** It is carried as **5.543 ± 0.125 W**: its 243-point mean, with e(243) as its known 1-s.e. counting error (`summary243.json` `F1_known_counting_error`).
- Its e(243) is the sample error (0.1247 W); the interleaved one reads 0.0623 W.
- The 1/√N law put it at about 0.128 W before the counts (REGISTRATION-step243.md section 3), with N = 395 to meet the bound; it now projects at 379 points (planning only).
- No uniform count beyond 243 is made, and RECOUNT-RULE.md section 6's recount is capped at 243 (REGISTRATION-step243.md section 4.1).
- F2, a stratified estimator, is **not run**. It needs its own registration first, with the four conditions of REGISTRATION-step243.md section 4.2.

**3. From 81 to 243 points the error falls as the 1/√N law says.** e(81)/e(243) is 1.66-1.82, median 1.72, where the law gives 1.73 ([`readings-243.txt`](readings-243.txt), G2).
- G1: the 81-point mean minus the 243-point mean has z rms **0.79** over 8 tiles against its expected spread under the rule's own model, and |z| > 2 on 0. So e(81) was a fair 1-s.e. error for the 81-point average.

**4. What the three-point count costs on these tiles (G3).** At 243 points the bench's three-point average errs by −0.284 to +1.049 W at M9's prices on the 8 bit-20 and bit-21 tiles. That is the size of the counting part in every model's rows on such tiles.
- G4, the arm's `fp32.b_onebit_b20_pi` (byte twin `cal_pi_b20`), aifoundry3: k = −0.157 ± 0.055 W at 243 points, beside −0.311 ± 0.198 at 27 (frozen) and −0.172 ± 0.100 at 81. M9's frozen D 12.093 W would read 12.249 W on 243-point counts.
- G4, the arm's `fp32.b_onebit_b20_pi` (byte twin `cal_pi_b20`), card 1: k = −0.150 ± 0.053 W at 243 points, beside −0.299 ± 0.190 at 27 (frozen) and −0.166 ± 0.097 at 81. M9's frozen D 11.628 W would read 11.779 W on 243-point counts.
  On this tile the frozen 27-point k is 0.155 W larger in size than the 243-point one, 0.78 of its own u: inside its stated error. The arm stays as frozen, at 27 points: this is a reading for E163 and E164 beside it, not an amendment.
- G5, pool 6's `fp32.b_onebit_b20_third` (twin `cal_third_b20`): the three-point error is +1.049 ± 0.088 W at 243 points. M9's nested error on it, −0.718 W on aifoundry3 and −0.996 W on card 1, becomes +0.331 W and +0.013 W with the 243-point average (post hoc: M9 was fitted on that row).
  As at 81 points, on card 1 the whole pool-6 miss is counting. On aifoundry3 the correction overshoots, so the two cards read this tile about 0.32 W apart after M9's card term (not registered).

**5. The two builds agree, and C is right at every point.**
- B1: the mini's build read the same 156 files as the Intel's, byte for byte (Verilator's own content hashes; [`build-record-mini.json`](build-record-mini.json), [`build-record-intel.json`](build-record-intel.json)).
- B2: 16 of 16 committed points, re-counted on the mini, are identical in every field ([`check-b2-mini.json`](check-b2-mini.json)).
- B3: the new point n0 272464 of `cal_third_b21`, counted on both builds, is identical in every field (1 of 1, [`check-b3.json`](check-b3.json); the Intel 23.6 s on one core at nice 10, the mini 6.6 s).
- D243: the step's own count of that point (part 1 of `cal_third_b21`) equals B3's on both builds (1 of 1 and 1 of 1; [`check-d243-intel.json`](check-d243-intel.json), [`check-d243-mini.json`](check-d243-mini.json)).
- C was checked against software at every point: 0 mismatches over 1,296 points (the run records' `check_mismatch_points`).

**6. Bench time.** 1,296 points in 2,420 s of wall time over 16 chunks on the mini at 4 jobs, 7.5 s a point on one core (13:27:32-14:08:12 PST, 0.68 h). The Q141 critic's estimate, about 3.1 bench-hours, used the 34.4 s a point that the 81-point step measured on the Intel at nice 20.

## What it does to predicting power and heat

- **The term:** the bench's single-bit counting, the input of the next model's single-bit price.
- **How many points a refit needs:** uniform launch points reach the 0.10 W bound on 15 of the 16 calibration tiles by 243 points, but not on `fp32.cal_third_b21`. So N\* is not reached by uniform points, and the rule's cap, 243, is the recount's cap. A refit's single-bit term fitted on uniform counts carries the known counting error on the tiles above the bound, never a smaller figure.
- **What a three-point count costs:** on bit-20 and bit-21 tiles it errs by −0.284 to +1.049 W at M9's prices, against M9's nested float error of 0.193 W. The counting part is first order for single high bits.
- **What it leaves alone:** no frozen prediction, band, rule or verdict changes. M9 stays primary, and the arm stays at 27 points.
- **Heat:** through M7's law (g = 0.11855 °C/W on aifoundry3) a counting error of e moves the 4.5 s rise by g × e: 0.015 °C for `fp32.cal_third_b21`'s e(243), too small to matter for these tiles' heat prediction.

## What was registered and what happened

- **As registered (REGISTRATION-step243.md):**
  - 16 chunks, one part of one tile each, in the registered order, part 1 before part 2: 16 of 16 ran and returned all 81 points;
  - 162 new points a tile, 1,296 in all, on the mini's build at 4 jobs, each chunk under a memory cap (6 GB) and a time cap (420 s);
  - B1 and B2 before the registration, B3 after it and before any chunk, all passed;
  - e(N) and N\* by `recount_rule.py`'s `main()` unchanged ([`run_recount_rule_243.py`](run_recount_rule_243.py)), and the readings G1-G5 ([`readings_243.py`](readings_243.py)).
- **Every count after the registration ran the committed driver**: each run record's `driver_sha256` is 092d02e6a6a6… (1 value over the 16 chunks and B3).
- **Departure, named:** B2 (13:17:47-13:18:20 PST, before the registration) ran `bench_243.py` as staged at 13:15 PST. That copy differs from the committed file only in one docstring line and in the run record's `driver_sha256` field, which it did not yet write. B2's counts are unaffected: they are identical to the Intel's in every field.
- **Niceness:** the chunks ran at nice 20 on the mini (the cap's nice 19 plus the driver's +10, capped at 20); the Intel's B3 point at nice 10, on one core.

## Files

| file | what |
|---|---|
| `counts-cal243-<tile>-p<k>.json`, `-run.json`, `bench-cal243-<tile>-p<k>.log` | run_kinds.py's counts, the run record and the log of each chunk (16) |
| `recount-rule.json`, `recount-rule.txt` | `main()`'s output over the 16 calibration tiles at 9, 27, 81 and 243 points |
| `summary243.json`, `summary243.txt` | each tile's outcome, N\*, F1's figures, the bench time |
| `readings-243.json`, `readings-243.txt` | G1-G5 |
| `counts-b3-intel.json`, `counts-b3-mini.json` (with `-run.json`), `bench-b3-*.log`, `check-b3.json` | B3 |
| `point-third_b21-272464-chunk.json`, `check-d243-intel.json`, `check-d243-mini.json` | D243, through [`extract_point.py`](extract_point.py) |
| `build-record-*.json`, `counts-b2-mini*.json`, `check-b2-mini.json` | B1 and B2 (committed with the registration) |
| `bench_243.py`, `compare_points.py`, `run_recount_rule_243.py`, `readings_243.py`, `selftest_step243.py`, `selftest-step243.txt` | the step's code and its self-test (committed with the registration) |

## Re-run

From the top of the tree, with a build of `rtl-sim/fma_toggle_v2` whose four unbuilt inputs hash as Q140(m)'s `bench-check/bench-sha256.txt` (on another machine than the Intel, record it first and pass the record):

```
D=docs/reports/data/2026-11-04-q141t-s7-recount/step243
python3 -B $D/bench_243.py record-build <bench build> <record.json>
python3 -B $D/bench_243.py run <bench build> $D/counts-cal243-third_b21-p1.json --tiles fp32.cal_third_b21 --part 1/2 \
    --build-record <record.json> --jobs 4
# ... the other 15 chunks in REGISTRATION-step243.md section 1's order, then:
python3 -B $D/run_recount_rule_243.py
python3 -B $D/readings_243.py
```
