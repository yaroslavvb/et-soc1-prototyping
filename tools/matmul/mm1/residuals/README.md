# MM1 residuals, Tue 17 Nov 2026: every miss of the lab's matmul models on data they did not fit (POST HOC)

**Label: post hoc.** This folder pools every residual of MM1-v0, MM1-v1 and MM1-v2 on matmul data that each model did not fit. It
looks for misses that repeat, and asks what MM1-v3 must add. The work is desk arithmetic on committed forecasts and committed
measured records, done after all of the data existed. **No group, threshold or term below was registered before any datum.** Each
figure keeps the label of its set:
- *BLIND*: the forecast was frozen before the data existed;
- *UNREAD*: a frozen model made the forecast after the data existed, without reading it;
- *HELD OUT*: the model was refitted without that experiment (LOEO) or card (LOCO). This is post hoc model selection, never blind.

Nothing here was measured anew, and nothing here forecasts a future run. It serves the owner's matmul focus of Mon 16 Nov 2026: one
model for a matmul's clock cycles, energy and transistor switches, from the sizes and the operations.

## 1. The sets

| set | model | label | data (commit) | forecasts (commit, sha256 checked) | points |
|---|---|---|---|---|---|
| v0-E206A | MM1-v0 | BLIND | E206 arm A, aifoundry3 card 0, 600 MHz (`d7e4f35e`) | `tools/matmul/mm1/v0/mm1_v0_e206.csv` (`5759fb7b...`) | 119 |
| v0-E206B | MM1-v0 | BLIND | E206 arm B, aifoundry1 card 1, 600 MHz (`79340bfa`; scores `f155c8ca`) | `v0/forecasts-e206-armB.csv` (`e35a06cb`, `1edf61ff...`) | 113 |
| v1-E206B | MM1-v1 | BLIND | E206 arm B (`79340bfa`) | `v1/forecasts-e206-armB.csv` (`d3f031d1`, `3f934002...`) | 113 |
| v1-E207 | MM1-v1 | BLIND | E207, aifoundry3 card 0 (`867f6a3f`; scores `f5c53145`) | `v1/out/mm1_v1_blind_day.csv` (`25d2e74e`, `90dffe94...`) | 53 |
| v1-E208 | MM1-v1 | UNREAD | E208's six sessions (`e99209a5`, `eed9624f`, `d40b6fe8`, `76fb5344`, `7693a23c`, `c2d6536c`) | `v2/out/unread_e208.csv` (`3ca4b717`, `d5757c82...`) | 401 runs |
| v0-E208 | MM1-v0 | UNREAD | the same runs | the same file | 401 runs |
| v2-E207 | MM1-v2 | BLIND | E207 (`867f6a3f`; scored `030ffa42`) | `v2/forecasts-e207.csv` (`4e518735`, `873360bb...`) | 53 |
| v2-LOEO | MM1-v2 | HELD OUT (LOEO) | 13 experiments, E105-E208, as MM1-v2's fit tabled them | `v2/out/points_time_v2.csv`, `points_energy_v2.csv` (`3ca4b717`) | 1,072 |
| v2-LOCO | MM1-v2 | HELD OUT (LOCO) | the same | the same | 1,072 |

- **E208's seventh session**, a2c0-S1r (`5d99fe17`), has no forecast of its own: the UNREAD forecasts depend on each run's measured
  clock and volts. It enters only as the repeat floor (section 6) and as a side check: its 80 runs, set against S1's UNREAD forecasts
  of the same arms, give MM1-v1 an rms of 8.94% in wall cycles (S1 itself: 8.88%) and 4.92% in W over idle given the seconds (S1:
  4.95%). **The models' misses repeat from session to session; they are not noise.**
- **Not pooled** (no lab forecast exists, and this lane ran no predictor): MM1-v2 on E206 arm B, which it never read, and E212's
  three committed sessions.

## 2. How it was computed

The code is the lab's own, written for this folder. It uses the standard library only and imports nothing from MM1, the kits, the
reducers or the ledger. Each forecast and data file is read only after its sha256 matches a pin, and every pin passed (23 of 23).
Each pin is the value that the file's freeze record, its folder's `SHA256SUMS`, or its experiment's registration list gives.

```
/usr/bin/python3 -I -B tools/matmul/mm1/residuals/build_residuals.py --lab . --out <dir>
/usr/bin/python3 -I -B tools/matmul/mm1/residuals/analyze_residuals.py --rows <dir>/residual-rows.json --out <dir> --date 2026-11-17
```

Both scripts ran from the lab's top at GitHub main `a90105da`, under `/usr/bin/python3` 3.12.3 with `-I -B`. Two runs gave
`residuals-2026-11-17.csv`, `.json` and `.md` byte for byte the same.

**The measured values** use the registered definitions.
- **E206 and E207.** A point is the mean of its kept pass-1 and pass-2 runs.
  - cycles an op on the wall = mean(cycles_gemm) / ops a minion;
  - the counter's mean = mean(cycles_per_op);
  - t = mean(t_gemm_s);
  - W over idle = mean(p_work − p_rest);
  - J over idle = mean((p_work − p_rest) t);
  - J at rest = mean(p_work t).
- **E208.** Each run's primary view, as the registered reducer gives it.
- **Cross-check.** The measured columns of `unread_e208.csv` equal this reduction to 2.5e-4, which is the CSV's rounding.

**Errors.** e = forecast / measured − 1, for seven quantities:
- cycles an op, on the wall and as the counter's mean;
- seconds a GEMM;
- J over idle, given the measured seconds and with the seconds forecast;
- J with the card at rest, given the measured seconds and with the seconds forecast.

Given the measured seconds, each model's W is its own affine form, W_g = A + (W_f − A) t_f / t_meas:
- A is MM1-v0's awake power × minions / 1,024, or MM1-v1's and MM1-v2's `W_affine_A_W` column;
- E208's UNREAD rows carry the scorer's given-seconds W.

J at rest uses the run's measured rest power, as the lab's scorers did. As in the lab's scorers, the J-over-idle percentages count only
points at 3 W over idle and above.

**The pools.**
- **Each set.**
- **Each model**, over its out-of-sample sets:
  - MM1-v0: E206 arm A, arm B and E208;
  - MM1-v1: arm B, E207 and E208;
  - MM1-v2: E207 and its LOEO folds.
- **The frontier.** Each measured experiment counts once, seen by the newest model that did not fit it:
  - E206 arm A: MM1-v2's LOEO fold;
  - arm B: MM1-v1, BLIND;
  - E207: MM1-v2, BLIND;
  - E208: MM1-v2's LOEO fold;
  - E105-E190: MM1-v2's LOEO folds.

LOCO is reported apart: it measures how a model transfers to a card it never saw.

**The groups.** Two kinds:
- every value of seven dimensions: data kind, shire-mask class, K-block class, format, the lines' place (inside the L3 ≤ 32 MB, the
  knee 33-70 MB, past it), card and clock class;
- the named misses of section 4.

For each group, in each pool:
- n points and n clusters (a cluster is one case on one card, where a case is a shape, format and mask);
- the mean error (size and sign) and its rms;
- a cluster bootstrap of the mean (2,000 resamples) with its 95% interval;
- its share of the pool's mean square error.

**Verdict on the frontier, per measured experiment.**
- *SYSTEMATIC*: the miss is material (at least 2% in time or 3% in energy, about 5× and 2.5× the repeat floors). Its interval excludes
  zero with one sign in two or more experiments and the other sign in none. Alternatively, the pooled interval excludes zero and three or
  more experiments share the sign.
- *ONE EXPERIMENT*, *MIXED SIGN*, *SMALL* (significant but under the material size), *FIXED SINCE MM1-v0* and *NOT BORNE OUT* cover
  the other cases.

**"With and without"** is a least-squares fit of e on an intercept and the named misses.
- The rms is given with the misses' fitted offsets removed, and with each cluster left out of its own fit (cross-validated, "cv"):
  that is the honest figure.
- Share explained = 1 − rms_after² / rms².

## 3. Each model's rms, with and without the systematic misses

| pool | cycles an op, wall: rms → named misses removed (cv) | share explained | J over idle given t: rms → removed (cv) | share explained | J at rest given t: rms → removed (cv) |
|---|---|---|---|---|---|
| MM1-v0 (E206 A, B, E208) | 9.28% → 6.58% | 50% | 11.46% → 4.80% | 82% | 2.27% → 1.44% |
| MM1-v1 (E206 B, E207, E208) | 6.90% → 4.10% | 65% | 9.77% → 4.53% | 78% | 2.05% → 1.46% |
| MM1-v2 (E207, LOEO folds) | 5.37% → 3.89% | 48% | 6.51% → 5.75% | 22% | 2.03% → 1.98% |
| the frontier (newest model per experiment) | 5.31% → 3.90% | 46% | 7.17% → 5.80% | 35% | 2.04% → 1.94% |

Per set, wall cycles and then J over idle given t, each as rms → removed (cv), with the share explained:

| set | wall cycles | J over idle |
|---|---|---|
| v0-E206A | 9.00 → 7.87 (23%) | 8.42 → 5.74 (54%) |
| v0-E206B | 9.20 → 8.05 (23%) | 14.07 → 7.04 (75%) |
| v1-E206B | 4.57 → 3.59 (38%) | 11.86 → 6.19 (73%) |
| v1-E207 | 5.44 → 4.08 (44%) | 5.41 → 3.84 (50%) |
| v1-E208 | 7.59 → 4.24 (69%) | 9.57 → 3.78 (84%) |
| v0-E208 | 9.39 → 5.68 (63%) | 11.39 → 3.52 (90%) |
| v2-E207 | 4.67 → 3.59 (41%) | 4.82 → 4.01 (31%) |
| v2-LOEO | 5.41 → 3.85 (49%) | 6.59 → 5.83 (22%) |
| v2-LOCO | 5.50 → 3.99 (47%) | 10.07 → 7.75 (41%) |

`residuals-2026-11-17.md` section 3 gives the other quantities and the rms of the points outside every named miss.

## 4. The systematic misses, with readings and the terms they ask for

Each miss is on the frontier's pooled residuals. Its primary quantity is wall cycles for a time miss (T) and J over idle given t for an
energy miss (E). The share of the MSE is the share of the frontier's mean square error in that quantity.

| miss | size and sign, 95% interval | points / clusters | share of the MSE | by experiment (bias %, * interval excludes zero) | verdict |
|---|---|---|---|---|---|
| E1 zero data on aifoundry1 card 1 | **+23.1%** [+20.3, +26.2] | 32 / 28 | **31.1%** | E206 B +25.7*, E208 +21.1* (MM1-v0 +31.4*, +26.6*) | SYSTEMATIC |
| T1a int8 1x1x1 at about 800 MHz | **+33.4%** (no spread) | 4 / 2 | 12.8% | E208 +33.4 (every run) | CONSISTENT, TOO FEW CLUSTERS |
| T8 run_gemm shared arms (c4s, c8s, c16s) | +5.6% [+5.1, +6.0] | 120 / 24 | 10.7% | E206 A +3.9*, B +3.5*, E105-E190 +5.8* | SYSTEMATIC |
| T2 the knee, narrow N (NB 1, 33-70 MB) | **−9.6%** [−12.1, −7.0] | 32 / 24 | 8.5% | E208 −10.7*, E206 B −5.9 (2 points) | ONE EXPERIMENT |
| T4 int8 inside the L3, KB ≥ 2 | **−5.7%** [−6.5, −4.6] | 59 / 35 | 5.5% | E206 A −7.2*, B −5.6*, E207 −7.3*, E208 −4.6*, older −6.0* | SYSTEMATIC |
| T1b int8 at one K block, MB × NB ≥ 2 | **−9.3%** [−11.6, −6.7] | 22 / 10 | 5.4% | −10.8, −11.3, −12.2, −9.4*, −6.9 (all five experiments) | SYSTEMATIC |
| T6 subsets past the L3 or at the knee | +6.1% [+2.8, +9.5] | 26 / 26 | 2.8% | E206 A +14.1* (v2's E206 fold), B +1.0, E207 +1.3 | SYSTEMATIC (one fold) |
| E6 one K block, MB × NB ≥ 2 | **−5.0%** [−7.9, −2.1] | 44 / 21 | 2.0% | E206 A −11.4*, B −5.1*, E207 −12.0*, E208 −2.8*, older −2.9 | SYSTEMATIC |
| T7a power-of-two NB (8, 16), MB 1, KB 4-8 | −4.5% [−5.2, −3.7] | 28 / 15 | 1.7% | E208 −4.3*, E105-E190 −5.1*, three others −2.7 to −3.9 | SYSTEMATIC |
| E4 deep K (KB ≥ 16), data not zero | +3.8% [+1.9, +6.0] | 50 / 36 | 1.3% | E206 A +4.3*, B +8.6*, E208 +5.9*, E207 +1.1 | SYSTEMATIC |
| E7 narrow masks (8 shires or fewer) | +5.1% [+2.9, +7.4] | 18 / 16 | 0.8% | E206 B +5.7*, E208 +4.8*, E206 A +4.8 | SYSTEMATIC |
| T7b power-of-two NB, MB 1, KB ≥ 12 | +8.0% [+7.1, +8.6] | 3 / 3 | 0.6% | +8.6, +7.1, +8.4 (one shape on three cards) | SYSTEMATIC (n 3) |
| T1c fp32 or fp16 at one K block, MB × NB ≥ 2 | −2.7% [−5.0, −0.6] | 26 / 11 | 0.5% | E206 B −6.2*, the rest −1.5 to −4.1 | SYSTEMATIC (small) |

**E1. Card 1's zero-data power.**
- Every model over-forecasts all-zero operands on aifoundry1 card 1 by 21-31%: MM1-v0, MM1-v1 and MM1-v2's E208 fold, in E206 arm B
  and in E208.
- On the other cards, the same kind pools within 2% for MM1-v2's folds: aifoundry3 card 0 +1.9%, the governed cards −0.2%.
- **Reading.** The tensor unit's zero-data clock gating, or operand isolation, saves more on card 1 than its random-data anchor and
  the models' one zero/random ratio allow. This is the gated base that E210's switch test probes on aifoundry3 card 0.
- MM1-v2 as frozen fits it on E208's card-1 runs. Its E208 fold, without them, misses by +21.1%. It has never been tested blind.
  Arm B's 14 zero points, which MM1-v2 never read, are a ready UNREAD check.
- **Term.** A per-card zero-data factor ζ_card = D_zeros / D_random: one constant a card. In the switch route, the same idea is a
  per-card ungated base. **Identified by:** E212's card-1 sessions (zeros, ones and the patterns) and E210 for the switch route.

**T1a. A one-K-block latency carried in microseconds.**
- int8 gemmL1x1x1 runs 389.7 cycles at 600 MHz and 392.5 cycles at 800 MHz.
- MM1-v1, and MM1-v2 in its E208 fold, forecast 524 cycles at 800 MHz, +33.4% in every run.
- **Reading.** The extra time at one K block, the L2 time, is fixed in cycles, not in microseconds.
- MM1-v2 as frozen already carries "L2 time in cycles": its card-out fold reads +0.7%. **MM1-v3 keeps that form; no new constant.**
  **Identified by:** E209 (aifoundry2 card 0 under its governor, MM1-v2 BLIND).

**T1b and T1c, E6. The C-block switch at one K block.**
- At KB = 1 with more than one C block, every model is too fast:
  - int8 by 9.3% (−6.9 to −12.2% in all five experiments);
  - fp32 and fp16 by 2.7%.
- The same points use 5% more energy than forecast (E6; 3x5x1 at E207 −12%).
- **Reading.**
  - Time: with no K loop to hide it, each C block's operand fetch is exposed. The fetch is a larger share of int8's shorter tensor op
    (283 against 527 cycles).
  - Energy: at KB = 1, C is written once per K block, so C's bytes per op are the largest. MM1 prices no C store, and in 3x5x1, C is 30
    of the 41 MB footprint.
- **Terms.** Time: an exposed switch time, τ_sw cycles per C block (one constant, or two with the format). Energy: a price per C line
  stored at its serving level (one or two constants).
- **Identified by:** E212's K-block-edge ladder (`mech-KB`: KB 1, 2, 3 at several MB × NB, int8 and fp32).

**T4. int8 inside the L3.**
- At KB ≥ 2, int8 runs 4.6-7.3% more cycles than MM1-v1 and MM1-v2 forecast, in every frontier experiment. MM1-v0 was within 1.5%.
- MM1-v1 and MM1-v2 put int8 and fp32 at the same memory-bound time for the same lines. At E207's shared shapes, int8 measured 6.3-6.6%
  more than fp32.
- **Reading.** The L3-served stream overlaps imperfectly with int8's shorter tensor op, so T = max(Tc, Tm) is optimistic when Tc and Tm
  are close.
- **Term.** A soft maximum T = (Tc^p + Tm^p)^(1/p), or an overlap loss κ·min(Tc, Tm). One constant covers T4 and the time part of T1b.
- **Identified by:** int8 against fp32 at matched lines inside the L3 (E212's `mech-LN` memory-line rungs; E209's int8 points).

**T2. The knee for narrow N.**
- For NB = 1 shapes at 33-70 MB (the 1x1x12-16 K ladder, 4x1x4), the models are 10% too fast.
- MM1-v2's fold reads 1x1x10 at +8% and 1x1x12 at −14%: a step between 32 and 38 MB that the logistic retention on A+B+C smooths over.
  All three models use that retention form; MM1-v0's midpoint is 50.7 MB and its width 8.75 MB.
- **Reading.** Retention depends on the reuse distance of the re-read stream (A's row panel), not on the whole footprint.
- **Term.** A per-stream retention edge (two constants: the edge and its width).
- **Identified by:** E212's deep-K ladder (`mech-DK`) at NB 1, MB 1-4. Only E208 shows the miss so far; E206's two points agree in sign
  for MM1-v1.

**T7a and T7b. The stride step.**
- Power-of-two NB at MB 1 is 4.5% too fast at KB 4-8 and 8% too slow at KB ≥ 12.
- At KB ≥ 12 every such shape measures the DRAM-bound plateau (about 1,437 cycles at 600 MHz) and shows no stride penalty, yet the
  models' stride rule applies one.
- **Term.** A conflict-miss fraction on B's retention that saturates once the stream is DRAM-bound: one or two constants.
- **Identified by:** E212's memory-line rungs (NB 7/8/9, 15/16/17 across KB 4-16) and E211. E211's rgm211 moves the far stream from B
  to A, so the step should move with it.

**T6. The subsets' DRAM contention.**
- MM1-v2's subset term, contention on the DRAM stream, rests on E206's subset points alone. Its E206 fold over-forecasts those points
  by 14.1%.
- BLIND on arm B (MM1-v1) and E207 (MM1-v2), the subsets are within 1-2%.
- **Term.** The contention term exists (one constant). It needs a second identifying set: E212's shire-mask ladder (`mech-MK`, 1-24
  shires past the L3).

**E4. Deep-K DRAM energy.**
- Shapes at KB ≥ 16 use 4-9% less energy than forecast on aifoundry1 card 1 and aifoundry2 card 0, and in MM1-v2's folds on
  aifoundry3 card 0.
- **Reading.** One operand streams from DRAM in long sequential runs, and one fresh-line price overprices them: open-row hits and
  prefetch make such lines cheaper.
- **Term.** A DRAM line price that falls with the stream's run length, or a separate price for sequential lines: one constant.
- **Identified by:** E212's deep-K ladder (`mech-DK`) and memory-line rungs.

**E7. Narrow masks' energy.**
- With 8 shires or fewer, the card draws about 5% less than forecast (+5.7% on arm B, +4.8% on E208).
- **Reading.** The line prices are full-chip averages, but a narrow mask's lines cross fewer mesh hops to their serving L3 slices.
- **Term.** A line price scaled by the active fraction of the mesh: one constant.
- **Identified by:** E212's shire-mask ladder (`mech-MK`).

**T8. The run_gemm shared arms.**
- The shared arms gemmc4s, gemmc8s and gemmc16s are 5.6% too slow.
- These are run_gemm's calibrating arms, not rgm136. The arms' classes are assigned by name, and one class constant covers them.
- **Term.** One constant, refit on committed data (E105-E169, E206); no card time is needed.

## 5. What is not a miss for the current models

- **T3, the knee at NB ≥ 2**: +0.2% pooled; the experiments disagree in sign.
- **T5, subsets inside the L3**: −0.4%, small. MM1-v1's and MM1-v2's mask terms fixed MM1-v0's −12.6%.
- **E2 and E3, zero data on aifoundry3 and on the governed cards**: small or fixed since MM1-v0, which read −9.8% and −4.3%.
- **E5, L3-served energy at full chip**: mixed sign. aifoundry3 reads −6.6% and −4.4%; the older experiments read +1.3%. This is a
  per-card, per-campaign offset, not a shape term.
- **E8, the knee in energy**: mixed sign.
- **E9, ones data**: MM1-v0 and MM1-v1 forecast no energy for it, and MM1-v2's LOEO table carries none. It is not testable here.
- **T9, the governor's steps.** Given each run's measured clock, the 800 MHz runs other than int8 1x1x1 read −0.7% (−2.1% in E208):
  small. Every aifoundry2 forecast here used the run's measured clock, so whether a model can forecast the clock itself (MM1-v2's
  governor model) is **NOT TESTED** here. E209 is that test.

## 6. The floor: what the card repeats to

E208's session repeat, committed in `5d99fe17`, is the same 85-run schedule on aifoundry2 card 0, five hours apart. It gives the rms of
repeat / first − 1 over the single-run arms:
- cycles (wall) 0.383%;
- cycles (the counter's mean) 0.409%;
- seconds 0.384%;
- W over idle 1.194%;
- J over idle 1.163%;
- J over idle die-corrected to 50 C 0.716%.

J at rest, from the matched runs here (desk), repeats to 1.369%.

| pool | cycles (wall): rms / floor | J over idle given t: rms / floor | J at rest given t: rms / floor |
|---|---|---|---|
| MM1-v0 | 9.28 / 0.38 (24×) | 11.46 / 1.16 (9.8×) | 2.27 / 1.37 (1.7×) |
| MM1-v1 | 6.90 / 0.38 (18×) | 9.77 / 1.16 (8.4×) | 2.05 / 1.37 (1.5×) |
| MM1-v2 | 5.37 / 0.38 (14×) | 6.51 / 1.16 (5.6×) | 2.03 / 1.37 (1.5×) |
| frontier | 5.31 / 0.38 (14×) | 7.17 / 1.16 (6.2×) | 2.04 / 1.37 (1.5×) |

- **Model error dominates everywhere but J at rest.** The floor is 0.5% of the frontier's mean square error in cycles and 2.6% in J
  over idle.
- With the named misses removed (cv), the frontier still sits at 10× the cycles floor (3.90%) and 5× the J floor (5.80%).
- J with the card at rest is within 1.5× of its floor, because the rest power dominates it.

## 7. Two continuous checks

- **The die temperature.** In E208, where the die at a run's start spans 48-56 C, MM1-v1's J over idle error (data not zero) falls
  0.59% per C [−1.06, −0.20], 11% of that error's variance.
  - The lab's own die correction is +0.48% of power per C, and MM1-v0 and MM1-v1 carry no die term.
  - **Term:** W × (1 + λ (T_die − T_ref)), one constant, already measured. The other sets span 2-5 C and show nothing.
- **Experiment offsets.** Each measured experiment's mean error holds 17% of the frontier's J over idle mean square error and 6% of its
  cycles.
  - The experiments' means scatter by 3.0% rms in energy (unweighted, 15 experiments; for example E105 −4.2%, E107 +3.1%, E190 −4.1%,
    E208 +3.1%, arm B +5.4%).
  - No size or operation can forecast a campaign's offset (die, baseline, the card's state), so it bounds what any shape term can reach
    in J over idle.

## 8. Cross-checks, gaps and what was not run

- **Cross-check.** 34 of 34 published figures recompute to their rounding from this code.
  - MM1-v0 BLIND on arm A: 9.0% wall cycles.
  - MM1-v1 on arm B: 4.7% counter mean, 14.3% J over idle on all 105 points.
  - E207 per case: MM1-v1 5.62%, MM1-v2 4.80%.
  - E208 UNREAD: 7.59% / 9.57% and 9.39% / 11.39%.
  - MM1-v2 LOEO: 5.41%.
- **Gaps.**
  - The held-out sets' measured values are MM1-v2's tables. They are re-derived here only for E206 arm A, to 1.3e-6.
  - LOEO and LOCO carry wall cycles and energy only, with no counter mean or seconds.
  - LOCO has no seconds-forecast energy.
  - T1a, T7b and some per-experiment cells have too few clusters for an interval; they are marked.
  - The verdict thresholds (2% and 3%) and the named groups were chosen after the data.
- **NOT RUN.**
  - Any predictor: no new forecast was made, MM1-v2 on arm B is unscored, and E212 is unscored.
  - Any switch count: no transistor-switch residual exists, because no switch count is measured.
  - The model session's own forecasts are not scored here.

## 9. Files

| file | what |
|---|---|
| `build_residuals.py` | step 1: pins, own reduction, every (set, point) row with its errors → `residual-rows.json` (not committed; it regenerates) |
| `analyze_residuals.py` | step 2: pools, groups, bootstrap, verdicts, joint fits, the floor → the three outputs below |
| `residuals-2026-11-17.csv` | 3,397 rows: set, label, card, clock, shape, format, kind, mask, place, measured, forecast, the seven errors, the named misses |
| `residuals-2026-11-17.json` | every table: summaries, cross-checks, named misses per pool, marginal groups, joint fits, floor, die and offset checks |
| `residuals-2026-11-17.md` | the tables in Markdown |
| `SHA256SUMS` | sha256 of every other file here |

SPDX-License-Identifier: Apache-2.0 (the scripts). Data and text: the lab's usual terms.
