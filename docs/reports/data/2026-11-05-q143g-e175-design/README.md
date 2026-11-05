# Q143(g): E175's tiles drawn and kept by the registered rule, and their M10-carried and M9 predictions on aifoundry2 frozen - 16 governed kinds across 727-794 MHz predicted inside the 82 W admission and 8 pinned, before any kit or session

*Thu 5 Nov 2026 (week 45), desk only: no card, no device command, no lab box, no post, no Modal, no archive. The work ran from the registration's
commit (`c50ff493`, 12:16:51 PST: [`tools/claims-v3/e175/E175.md`](../../../../tools/claims-v3/e175/E175.md), its generator, bench driver and power
script, with a 40-file hash list) to this directory's commit, with dated note A1 between them (lab `0e56a875`, 12:54:59 PST: the stream continued
past its cap for the pinned set only, before any candidate past 63 existed). **No E175 tile, count or prediction existed before the registration's
commit**, and nothing here
reads a measurement or a model's error: the stream comes from a seed nobody chose, and the selection reads only the frozen predictor's predictions.
The pool-8 card day (E171-E174) ran on the boxes meanwhile; nothing of it was read. It answers the earlier critics' rank "aifoundry2's governed
line" (the Q142(h2)/(a2)/(r3) critic's `next` rank 7) on the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): pool 8 left P8-A2-G, Bg, F1 and W1 NOT
SCORED with 3 governed tiles. The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of numeric
computations as accurately as possible. Where it ran: the bench counts on the mini (Q141(t2)'s recorded build, as M10 and Q142(x) used it, checked
against its record; one chunk at a time, 4 jobs, each call capped); everything else on the Intel, Python through the round's local slot, one job
at a time.*

## Results

**1. The stream: 64 candidates by the registered rule, then 32 more by dated note A1, none refused by the generator.** `make_e175_pool.py draw` (the
registration's file, sha256 in `SHA256SUMS-e175-registration`) on `/usr/bin/python3` 3.9.6 with numpy 1.26.4, seed `0xbd33bd555026eb2e` from lab
`4576fb90`: candidates 0-63, 32 fp32 and 32 fp16, from pool 8's twelve float families, each with its truncation m
([`candidates/stream-e175.json`](candidates/stream-e175.json)). The registered 64 gave 16 governed (the four strata full at candidate 24) but only 7
of the 8 pinned, so [dated note A1](../../../../tools/claims-v3/e175/E175.md.dated-note-A1.md) (lab `0e56a875`, 12:54:59 PST, committed before any
candidate past 63 existed) continued the same stream for the pinned set only: `make_e175_pool_a1.py draw` appended candidates 64-95 by the same
function, seed and streams (18 fp32, 14 fp16; [`candidates/stream-e175-a1.json`](candidates/stream-e175-a1.json), candidates 0-63 copied by value).
Every candidate passes make_blind8's `tile_refusal` and `class_check` (class U), and none equals any of the 584 committed tile files under
`tools/claims-v3/kinds/` or another candidate (the tiles under [`candidates/tiles/`](candidates/tiles/)).

**2. The bench: every counted candidate met the convergence rule at N = 9.** The three zeros anchors and candidates in stream order, at the nine
points of N = 9 (which hold the three standard points), C checked at every point, 0 mismatches: 720 points in 5 chunks of 16 candidates (candidates 0-15: 144 points in 381.7 s, candidates 16-31: 144 points in 452.0 s, candidates 32-47: 144 points in 441.6 s, candidates 48-63: 144 points in 421.2 s, candidates 64-79: 144 points in 403.9 s; 2100 s of wall in all at 4 jobs). The build check first: candidate 0's point
at n0 30525 counted on the mini's build and on the Intel's hashed build is identical in every field ([`bench/check-b1.json`](bench/check-b1.json)).
The frozen predictor's `plan` then reads every counted float tile complete at N = 9, e(9) at most 0.058 W (the bound is 0.10 W)
([`predict-candidates/plan.json`](predict-candidates/plan.json)).

**3. The predictions of every counted candidate** (`predict_pool8_a2.py predict <candidates> aifoundry2`, exit 0, never `predict_pool8.py`), with the
counts and pool 8's committed counts of the three zeros anchors: [`predict-candidates/predictions-pool8-aifoundry2.json`](predict-candidates/predictions-pool8-aifoundry2.json)
and its `.md` table. Every counted candidate is committed with its predictions, kept or not.

**4. The selection** (`make_e175_pool_a1.py select`: the registered `select` over candidates 0-63 unchanged, then A1's continuation for the pinned
set only; predictions only): the stream read 80 candidates and **FILLED (A1)** at candidate 65: **16 governed** (8 fp32, 8 fp16; four strata of 4/4/4/4; predicted 727.9-793.8 MHz) and **8 pinned**; 11 candidates over 82 W replaced by the next draw (0 at 83.388 W, 1 at 82.197 W, 19 at 82.237 W, 33 at 83.866 W, 40 at 82.598 W, 42 at 84.58 W, 48 at 85.572 W, 49 at 82.367 W, 51 at 83.914 W, 57 at 85.577 W, 59 at 83.045 W); 30 governed spares kept out because their stratum was full ([`design-e175.json`](design-e175.json), one record per candidate with its outcome). Candidates 66-79 were counted and predicted past the stop (the last chunk's width) and 80-95 drawn by A1 but never counted; both are committed and change nothing.

**5. The pool and its frozen predictions.** `build` wrote [`tools/claims-v3/e175/pool/`](../../../../tools/claims-v3/e175/pool/) (the three zeros
anchors and the 24 kept tiles, `e175.json` in pool 7's JSON form, `SHA256SUMS`); `check` re-derives every tile from the stream and its label from
its bytes: "checked 27 tiles: 0 problems" ([`pool-check.txt`](pool-check.txt)). `predict` on the pool wrote
[`tools/claims-v3/e175/frozen/predictions-pool8-aifoundry2.json`](../../../../tools/claims-v3/e175/frozen/predictions-pool8-aifoundry2.json) (and
`.md`; the predictor's own file name), and its blocks equal the candidates' field for field: "pool-vs-candidates: the pool's 27 tiles (the design's 27: True), 378 fields, 0 differ from the candidates' predictions" ([`pool-vs-candidates.txt`](pool-vs-candidates.txt)).
**No tile in the pool is over 82 W**: the highest larger 95% upper peak kept is 81.527 W.

| set | stratum | tile | family, m | M10 D600 W | M10 MHz | M10 board W | M9 MHz | M9 board W | M10 rise C | upper peak W (larger) |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| governed | 1 | `fp32.e5c05_expo_t8_06469f` | expo, 8 | 21.410 | 734.6 | 67.12 | 734.3 | 67.12 | 6.39 | 80.16 |
| governed | 1 | `fp32.e5c09_uniform_t6_dad136` | uniform, 6 | 22.131 | 727.9 | 67.11 | 727.5 | 67.11 | 6.39 | 81.53 |
| governed | 1 | `fp32.e5c10_ar_i_t10_adc630` | ar_i, 10 | 20.562 | 742.8 | 67.12 | 742.2 | 67.12 | 6.39 | 78.61 |
| governed | 1 | `fp16.e5c18_lognorm_t2_38ac9e` | lognorm, 2 | 21.437 | 734.6 | 67.12 | 733.5 | 67.12 | 6.39 | 80.19 |
| governed | 2 | `fp16.e5c03_ar_k_t4_5b8e8e` | ar_k, 4 | 19.275 | 756.3 | 67.10 | 755.6 | 67.11 | 6.39 | 76.03 |
| governed | 2 | `fp16.e5c06_rowscale_t5_6d624f` | rowscale, 5 | 19.805 | 750.8 | 67.12 | 749.4 | 67.12 | 6.39 | 77.15 |
| governed | 2 | `fp16.e5c17_bimodal_t5_a9b319` | bimodal, 5 | 19.000 | 759.3 | 67.09 | 758.0 | 67.09 | 6.38 | 75.61 |
| governed | 2 | `fp16.e5c24_grid_t1_cdcbf7` | grid, 1 | 19.242 | 756.7 | 67.10 | 755.3 | 67.11 | 6.39 | 76.08 |
| governed | 3 | `fp32.e5c07_expo_t16_2700b2` | expo, 16 | 18.285 | 766.7 | 67.00 | 766.0 | 67.01 | 6.37 | 74.37 |
| governed | 3 | `fp16.e5c08_ar_k_t6_6dd6a1` | ar_k, 6 | 18.574 | 763.9 | 67.04 | 763.2 | 67.05 | 6.38 | 74.71 |
| governed | 3 | `fp16.e5c21_bimodal_t5_b1c552` | bimodal, 5 | 18.551 | 764.1 | 67.04 | 763.1 | 67.05 | 6.38 | 74.73 |
| governed | 3 | `fp32.e5c22_ar_i_t15_f64ec4` | ar_i, 15 | 18.589 | 763.3 | 67.05 | 762.3 | 67.06 | 6.38 | 75.01 |
| governed | 4 | `fp16.e5c02_ar_k_t10_5a2fd3` | ar_k, 10 | 15.369 | 793.8 | 64.27 | 793.6 | 64.34 | 5.99 | 68.67 |
| governed | 4 | `fp32.e5c11_grid_t21_b0b91b` | grid, 21 | 16.073 | 788.8 | 65.44 | 788.6 | 65.48 | 6.15 | 70.19 |
| governed | 4 | `fp32.e5c13_bimodal_t22_48a100` | bimodal, 22 | 15.359 | 793.7 | 64.32 | 793.7 | 64.33 | 6.00 | 68.81 |
| governed | 4 | `fp32.e5c15_mixture_t21_2c53f6` | mixture, 21 | 16.706 | 783.3 | 66.18 | 782.8 | 66.22 | 6.26 | 71.41 |
| pinned | - | `fp16.e5c04_sparse_t4_3d3b51` | sparse, 4 | 10.098 | 800.0 | 54.18 | 800.0 | 54.33 | 4.58 | 58.88 |
| pinned | - | `fp32.e5c12_tdist_t23_f74165` | tdist, 23 | 14.684 | 796.8 | 63.07 | 796.7 | 63.12 | 5.82 | 67.59 |
| pinned | - | `fp32.e5c14_ar_k_t22_a444f5` | ar_k, 22 | 14.211 | 798.2 | 62.13 | 798.2 | 62.13 | 5.69 | 66.67 |
| pinned | - | `fp16.e5c16_sparse_t1_9f47b2` | sparse, 1 | 10.243 | 800.0 | 54.46 | 800.0 | 54.57 | 4.62 | 59.12 |
| pinned | - | `fp32.e5c29_sparse_t19_93b1d2` | sparse, 19 | 11.977 | 800.0 | 57.78 | 800.0 | 57.89 | 5.08 | 62.57 |
| pinned | - | `fp16.e5c32_sparse_t2_42cc31` | sparse, 2 | 10.128 | 800.0 | 54.24 | 800.0 | 54.37 | 4.58 | 58.92 |
| pinned | - | `fp32.e5c50_ar_k_t22_16d78b` | ar_k, 22 | 14.921 | 795.9 | 63.52 | 795.8 | 63.54 | 5.88 | 68.00 |
| pinned | - | `fp32.e5c65_sparse_t5_254f07` | sparse, 5 | 5.700 | 800.0 | 46.02 | 800.0 | 46.06 | 3.44 | 50.75 |

At the fallback (the session's zeros level not yet read) and T_ref (54.38 °C): every governed tile sits at the governor's plateau, about 67.1 W, and
the kind of number sets the clock; the pinned tiles run at 800 MHz and their board follows D. M10 carried and M9's part on M9's D differ on the board by a median 0.011 W over the 24 kept tiles (at most 0.151 W) and on the clock by a median 0.36 MHz (at most 1.36 MHz): E175-A2-M1's paired test has little room to resolve them, as E173.md expected for pool 8. At scoring, `burst` recomputes every block
with the session's own zeros-anchor reads and each tile's die starts; the groups stay the frozen file's.

## What it does to predicting power and heat

Nothing is measured. The design gives aifoundry2's governed clock line its first blind test with enough tiles: 16 new kinds whose predicted
governed clocks span 727.9-793.8 MHz, four to a stratum, against rank 2's lines (E175-A2-G: rms ≤ 4.0 MHz and |mean| ≤ 2.0 MHz; E175-A2-Bg) and
Q140(l)'s held-out figures (F1, W1), with 8 new pinned kinds in the same session (Bp, F2, W2), so that rank 2 (E175-A2-R2) can read PASS on blind
kinds for the first time. **Before:** the governed clock's only blind score is M9's part on pool 7 (E165: 3.03 MHz rms, 12 tiles); M10 carried was
never scored on a governed tile (pool 8: 3). **The power at this design** (the registration's `design-power-e175.txt`): G passes in 31.5% of draws
if M10 carried errs as Q140(l)'s held-out cells did, in 91.0% if as E165's blind errors did; R2 in 23.1% and 31.9%.

## Checks

- The registration's 40-file list passes after this lane, and so do the lists the predictor checks (its `SHA256SUMS` 16, `SHA256SUMS-a2` 9,
  POOL8-SHA256SUMS 209): every `predict` and `plan` here checked them before reading anything.
- Every bench run record carries the committed driver's sha256 (`bench_e175.py`, `1abe25b1…`) and the bench manifest's (`00c8225c…`).
- No file here holds a home path or a private network address (the public-text scan before the commit).

## Registered, and what happened

- **As registered** (E175.md, "The design" and "The predictions"): the stream by the committed generator and seed; the counts in stream order by the
  convergence rule, the mini's build checked against the Intel's on one point first; the frozen predictor on the candidates; the selection by the
  frozen predictions only (the 82 W admission with the next draw replacing a tile over it; four strata of 4; 8 pinned; the stream stopped where the
  sets filled); the pool built and checked; `predict` on the pool equal to the candidates' field for field; one commit before any kit.
- **Disclosed:**
  - Before the registration's commit, the generator ran once on its test seed (`draw --test`, a directory named TEST in the lane's scratch) and the
    power script once into the scratch; both are named in E175.md.
  - After the first chunk's counts (candidates 0-15), `plan` and `predict` ran once on those 16 into the lane's scratch (12:27 PST), as a test of the
    pipeline; the registered rule reads the stream in order and nothing was changed after it. The committed outputs are the runs on candidates
    0-79.
  - The bench counted candidates in chunks of 16 (0-15, 16-31, 32-47, 48-63, 64-79); the selection's rule makes the extra candidates beyond the stop index
    change nothing, and they are committed with their predictions.
  - **Dated note A1** was written after the registered stream's 64 predictions were read (their groups and peaks only: 46 governed, 11 over 82 W, 7
    pinned) and before any candidate past 63 existed. It changes only which candidate, if any, becomes the eighth pinned tile; the governed set is
    the registered rule's 16, and no rule, line, minimum, stop, admission or power figure changes.

## What this cannot say

- **Nothing here is measured.** These are predictions; the test needs E175's session on aifoundry2 under its own governor, after E173, kitted and
  passed by a readiness critic.
- **The selection reads the predictions:** a kind the models misplace (governed as pinned, or under 82 W as over) is sorted by its prediction, as
  E175.md says.
- **Term b's counts are the bench's** (one minion's vector unit in Verilator), and e(N) is priced at M9's float prices.

## Files

| file | what |
|---|---|
| `README.md` | this file |
| `candidates/stream-e175.json`, `candidates/stream-e175-a1.json`, `candidates/tiles/`, `candidates/e175.json` | the registered stream (64 candidates, their streams, parameters and sha256), A1's continued stream (96), the tiles, the manifest of the zeros anchors and candidates 0-79 the predictor read |
| `bench/manifest-bench.json`, `bench/manifest-bench-a1.json`, `bench/counts-e175-{s1,a1}-c*.json` (+ `-run.json`, `bench-*.log`), `bench/counts-b1-*.json`, `bench/check-b1.json` | the bench's manifests (candidates 0-63; A1's 64-95), the counts, their run records and logs, the build check |
| `predict-candidates/plan.json`, `predict-candidates/predictions-pool8-aifoundry2.json` (+ `.md`), `predict-candidates/predict.log` | the frozen predictor's plan and predictions on the counted candidates |
| `design-e175.json` | the selection: every candidate's outcome, the strata, the governed and pinned sets |
| `pool-check.txt`, `predict-pool.log`, `pool-vs-candidates.txt` | the pool's check, the predictor on the pool, the field-for-field comparison |
| `SHA256SUMS` | the sha256 of every file of this commit, from the repo top (this directory, the pool and the frozen predictions) |
| `../../../../tools/claims-v3/e175/pool/`, `../../../../tools/claims-v3/e175/frozen/` | the pool (27 tiles, `e175.json`, `SHA256SUMS`) and its frozen predictions on aifoundry2 |

## Re-run

From the top of the tree (the Intel's `/usr/bin/python3`, numpy 1.26):

```
python3 -B tools/claims-v3/e175/make_e175_pool.py draw --out <new dir>          # the registered stream, byte for byte
python3 -B tools/claims-v3/e175/make_e175_pool_a1.py draw --stream <dir>/stream-e175.json --out <dir>     # A1's continuation
python3 -B tools/claims-v3/e175/make_e175_pool_a1.py manifest --stream <dir>/stream-e175-a1.json --upto 80 --out <dir>
python3 -B docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py predict <dir> aifoundry2 --counts <each bench/counts-e175-{s1,a1}-c*.json> \
  --counts docs/reports/data/2026-11-05-q142x-pool8-freeze/bench/counts-x-s1-f03.json --counts docs/reports/data/2026-11-05-q142x-pool8-freeze/bench/counts-x-s1-i04.json --out <out>
python3 -B tools/claims-v3/e175/make_e175_pool_a1.py select --stream <dir>/stream-e175-a1.json --predictions <out>/predictions-pool8-aifoundry2.json --upto 80 --out <file>
python3 -B tools/claims-v3/e175/make_e175_pool_a1.py check --out tools/claims-v3/e175/pool
```

## Compute

- **The mini:** 6 bench calls, one at a time, 4 jobs at most (the build check's one point capped at 4 GB and 240 s; the 5 chunks at 6 GB and 900 s each): 721 points in all, 2108 s of wall (2.92 s a point at 4 jobs). No lab box was used, and no sign-in link appeared.
- **The Intel:** short jobs through the round's local slot, one at a time: the draw, the Intel's one bench point (25.5 s on one core at nice 10), the
  plans and predicts, the selection, the build and check. Beside them: git, hashing, the public-text scan and bounded copies to and from the mini.

SPDX-License-Identifier: Apache-2.0
