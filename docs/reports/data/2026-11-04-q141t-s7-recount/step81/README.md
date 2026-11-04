# Q141(t), step 3: the convergence rule's 81-point step on the 10 calibration tiles above the bound at 27

*Wed 4 Nov 2026 (week 45), bench 10:02:28-11:19:56 PST, on the Intel, desk only (no card, device command, lab box, Discord,
Modal or archive). Registered in [`../REGISTRATION.md`](../REGISTRATION.md) section 4 (`0830f65b`, before any count), under
Q140(m)'s [RECOUNT-RULE.md](../../2026-11-04-q140m-m9/recount-rule/RECOUNT-RULE.md) sections 4-5 (`b4444dd4`). It answers the
Q140 final critic's `desk_next` 10, under its open **rank 4** (the bench's counting against a missing single-bit price), for the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6**. Committed
after the arm ([`../README.md`](../README.md), `67d5e44f`).*

## Results

**1. Two of the ten tiles meet the bound at 81 points; eight do not.** N\* is still not determined. Figures are from
[`recount-rule.json`](recount-rule.json) and [`recount-rule.txt`](recount-rule.txt), written by `recount_rule.py`'s `main()`
unchanged; the summary is [`summary81.txt`](summary81.txt).
- `cal_third_b17` reaches e(81) = 0.062 W and `cal_w67_b17` 0.060 W.
- The other eight read 0.100-0.221 W: `cal_pi_b20` 0.1004, `cal_w79_b20` 0.108, `cal_w67_b20` 0.115, `cal_w79_b21` 0.120,
  `cal_w67_b21` 0.140, `cal_third_b20` 0.147, `cal_pi_b21` 0.154 and `cal_third_b21` 0.221.
- With the six tiles that met the bound at 9 or 27 points, **8 of the 16 calibration tiles** now meet it. The eight above it are
  all bit 20 or bit 21 tiles.

| tile | e(9) | e(27) | e(81) | e(27)/e(81) | first N meeting 0.10 W | 3pt − 81 (W) | projected N (planning) |
|---|---:|---:|---:|---:|---|---:|---:|
| `fp32.cal_third_b17` | 0.267 | 0.102 | 0.062 | 1.65 | 81 | +0.411 | — |
| `fp32.cal_third_b20` | 0.508 | 0.267 | 0.147 | 1.82 | not yet | +1.013 | 175 |
| `fp32.cal_third_b21` | 0.978 | 0.389 | 0.221 | 1.76 | not yet | −0.024 | 395 |
| `fp32.cal_w79_b20` | 0.526 | 0.173 | 0.108 | 1.61 | not yet | +0.903 | 95 |
| `fp32.cal_w79_b21` | 0.479 | 0.209 | 0.120 | 1.74 | not yet | +0.775 | 118 |
| `fp32.cal_w67_b17` | 0.165 | 0.114 | 0.060 | 1.90 | 81 | +0.349 | — |
| `fp32.cal_w67_b20` | 0.370 | 0.201 | 0.115 | 1.74 | not yet | +0.875 | 108 |
| `fp32.cal_w67_b21` | 0.491 | 0.267 | 0.140 | 1.90 | not yet | +0.672 | 159 |
| `fp32.cal_pi_b20` | 0.653 | 0.198 | 0.100 | 1.97 | not yet | −0.172 | 82 |
| `fp32.cal_pi_b21` | 0.429 | 0.260 | 0.154 | 1.69 | not yet | −0.468 | 192 |

How to read the table:
- e(N) is in W of D at M9's frozen float prices: RECOUNT-RULE.md section 2's larger of the sample and interleaved standard errors.
- "3pt − 81" is the bench's three-point average minus its 81-point average at those prices.
- "projected N" is the 1/√N law's N for the bound (planning only, never in place of counts).

**2. From 27 to 81 points, the error falls as the 1/√N law says.**
- e(27)/e(81) is 1.61-1.97, median 1.76, where the law gives 1.73. From 9 to 27 points the ratio was 1.28-3.30.
- So the projections are now better grounded. They put 7 of the 8 tiles under the bound by 243 points, the rule's cap. The
  exception is `cal_third_b21`, projected at 395.
- **The 243-point step for the eight would cost about 3.1 bench-hours** at 4 jobs, at this step's 34.4 s a point on one core.
- If `cal_third_b21` stays above the bound at 243, RECOUNT-RULE.md section 4 applies: the next model carries its e(N) as a known
  error on rows like it, or registers another estimator first (for instance, points stratified by C's state, from `accum.c`).

**3. Post hoc: e(27) is a fair error, so the arm's u holds.** This is [`posthoc_e_check.py`](posthoc_e_check.py), not registered;
output [`posthoc-e-check.txt`](posthoc-e-check.txt).
- On the ten tiles, the 27-point mean minus the 81-point mean is z = d / √(e(27)² − e(81)²) of its expected spread under the rule's
  own model.
- z has rms 0.87, and no |z| exceeds 2. e(27) is about right, if anything slightly conservative, as a 1-s.e. error of a 27-point
  average.
- So the arm's per-tile u = e(27) (`../arm-s7.json`) is a fair uncertainty for its counting part k.

**4. Post hoc: two byte twins move at 81 points.** Neither changes anything frozen.
- **Pool 6's `fp32.b_onebit_b20_third`** (twin `cal_third_b20`):
  - The three-point count's error is **+1.013 ± 0.147 W** at 81 points; it was +0.784 ± 0.267 at 27.
  - M9's nested error on it, −0.718 W on aifoundry3 and −0.996 W on card 1, becomes **+0.295 W and −0.022 W** with the 81-point
    average (`recount-rule.txt`'s post hoc lines).
  - So on card 1 the whole pool-6 miss is counting. On aifoundry3 the correction overshoots by about 0.3 W: the two cards read
    this tile about 0.3 W apart after M9's card term.
- **Pool 7's `fp32.b_onebit_b20_pi`**, one of the arm's own tiles, through its twin `cal_pi_b20`:
  - At 81 points its counting part reads **k = −0.172 ± 0.100 W** on aifoundry3 (−0.166 ± 0.097 on card 1). The arm froze it at
    −0.311 ± 0.198 at 27 points; the move is 0.82 of its expected spread.
  - The arm stays as frozen, at 27 points for every tile. This 81-point figure is for reading E163's and E164's result on that tile
    beside the arm.

## What it does to predicting power and heat

- **The term:** the bench's single-bit counting, as the input of the next model's single-bit price.
- **How many points a refit needs:** at 81 points, half of the 16 calibration tiles are within the rule's 0.10 W. The bit-20 and
  bit-21 tiles still carry 0.10-0.22 W.
- **What a three-point count costs:** the error falls as 1/√N. On the bit-20 and bit-21 tiles the three-point count errs by −0.47
  to +1.01 W at M9's prices (the table's last-but-one column). That is the size of the counting part in every model's rows on such
  tiles.
- **What it does not change:** no frozen prediction, band, rule or verdict changes. The arm (`../arm-s7.json`) stays at 27 points.

## What was registered and what happened

- **As registered (REGISTRATION.md section 4):**
  - five runs of two tiles, in the listed order;
  - 54 new points a tile (540 in all);
  - the same bench build (hash-checked by the driver);
  - C checked at every point: 0 mismatches over 540 points (`counts-cal81-<n>-run.json`);
  - e(N) and N\* by `recount_rule.py`'s `main()` unchanged, its output directory pointed here
    ([`run_recount_rule.py`](run_recount_rule.py)).
- **Bench time:** every pair started inside the 1.5 h cap (the last at +3,870 s). The step took 4,648 s, or 1.29 bench-hours.
- **`main()`'s cost lines are absent here.** It reads a `pilot-run.json` beside its output, which this directory does not have. So
  `summary81.json` gives this step's own bench time instead.
- **Before the counts**, the wrapper was checked on the committed counts alone. It reproduced the committed `recount-rule.json` and
  the first 40 lines of its `.txt` exactly, apart from those cost keys.
- **Departures**, both in `../REGISTRATION.md.dated-note.md`:
  - the bench ran through `../bench_s7_run.py`, because `bench_s7.py`'s run record crashed on `os.nice(0)`;
  - the session reniced it to nice 20 (gentler than the brief's 10), so `counts-cal81-<n>-run.json` read `nice_of_driver` 20.

## Files

| file | what |
|---|---|
| `counts-cal81-<n>.json`, `bench-cal81-<n>.log`, `counts-cal81-<n>-run.json` | run_kinds.py's counts, its log and the run record of pair n = 1-5 |
| `run_recount_rule.py` | `recount_rule.py`'s `main()` unchanged, output here, plus `summary81.json` / `.txt` |
| `recount-rule.json`, `recount-rule.txt` | `main()`'s output over the 16 calibration tiles at 9, 27 and 81 points |
| `summary81.json`, `summary81.txt` | e(9), e(27), e(81), e(27)/e(81), N\*, this step's bench time, the 243-point cost |
| `posthoc_e_check.py`, `posthoc-e-check.json`, `.txt` | post hoc: e(27) against the 27-to-81 move; the arm's b20_pi at 81 points |

## Re-run

From the top of the tree, with a build of `rtl-sim/fma_toggle_v2` whose seven files hash as Q140(m)'s
`bench-check/bench-sha256.txt`:

```
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/bench_s7_run.py <bench build> cal81 \
    docs/reports/data/2026-11-04-q141t-s7-recount/step81/counts-cal81-1.json --tiles fp32.cal_third_b17,fp32.cal_third_b20 --jobs 4
# ... pairs 2-5 in REGISTRATION.md section 4's order, then:
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/step81/run_recount_rule.py
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/step81/posthoc_e_check.py
```
