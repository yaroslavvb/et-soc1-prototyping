# TAU pre-registration: the rails' filter, per card and rail, and what deconvolution recovers

Written 2026-09-28, before any TAU block ran on a card; revised the same night after review, still before any card
pass (the changes are listed at the end). Status: **draft for development** on aifoundry1's card 1.
It is frozen before validation: `sha256sum tools/claims-v3/tau/PREREG.md > tools/claims-v3/tau/PREREG.sha256`, and
`LOCK.sha256` over the block's files (README.md, "Freeze"). Every number the decision code uses is in `prereg.json`;
`reduce.py report` scores each item PASS, FAIL or NO-DATA over the pooled full, ok passes of one card and gives each
theory's verdict on that card.

## What the committed data already say (offline, no card)

`offline.py` over 5,956 bursts with at least 4 s of idle before them: the 23 September catalogue and enercat sessions
(aifoundry2, aifoundry3) and the version-3 full catalogue (25-26 September; aifoundry2, aifoundry3, aifoundry1's
card 1). Each burst is a square of true power between its kernel timestamps; each channel is fitted with per-burst
baseline, drift, step and previous-burst tail, and a tau and delay shared by the card's bursts (`offline.json`).

| Card | Channel | bursts | tau, one pass late (s) | residual | fixed-delay fit: tau, d (s) | per-burst tau, IQR | rise / fall | by session |
|---|---|---|---|---|---|---|---|---|
| aifoundry2 | minion | 922 | 1.06 (extra d +0.00) | 1.1% | 1.06, 0.15 | 1.05-1.08 | 1.06 / 1.06 | 23 Sep 1.06, v3 1.05 |
| aifoundry2 | SRAM | 299 | 1.02 (+0.02) | 1.1% | 1.03, 0.16 | 1.00-1.03 | 1.03 / 1.02 | 1.03, 1.02 |
| aifoundry2 | NoC | 127 | 1.05 (+0.00) | 1.2% | 1.05, 0.14 | 1.04-1.06 | 1.05 / 1.05 | 1.06, 1.07 |
| aifoundry2 | board_avg | 1,447 | 1.08 (no lag) | 0.9% | 1.08, 0.00 | 1.08-1.09 | 1.09 / 1.08 | 1.09, 1.09 |
| aifoundry3 | minion | 921 | 1.04 (-0.01) | 1.0% | 1.04, 0.25 | 1.03-1.10 | 1.04 / 1.04 | 1.04, 1.05 |
| aifoundry3 | SRAM | 299 | 1.03 (+0.00) | 1.1% | 1.02, 0.27 | 1.02-1.08 | 1.03 / 1.02 | 1.03, 1.04 |
| aifoundry3 | NoC | 119 | 1.04 (-0.02) | 1.0% | 1.03, 0.25 | 1.03-1.10 | 1.04 / 1.04 | 1.04, 1.02 |
| aifoundry3 | board_avg | 1,362 | 1.05 (no lag) | 0.8% | 1.05, 0.00 | 1.04-1.06 | 1.05 / 1.05 | 1.07, 1.05 |
| aifoundry1-c1 | minion | 459 | 1.06 (-0.01) | 0.8% | 1.08, 0.14 | 1.06-1.07 | 1.06 / 1.07 | v3 only |
| aifoundry1-c1 | **SRAM** | 141 | **0.53** (+0.03) | 1.4% | 0.52, 0.20 | 0.52-0.55 | 0.53 / 0.53 | |
| aifoundry1-c1 | NoC | 83 | 1.07 (-0.02) | 0.8% | 1.07, 0.14 | 1.06-1.10 | 1.07 / 1.07 | |
| aifoundry1-c1 | board_avg | 673 | 1.11 (no lag) | 0.7% | 1.11, -0.01 | 1.10-1.11 | 1.11 / 1.10 | |

Tau does not move with the step (minion rail: the same tau for 5-10, 10-15 and 15-30 W steps on every card) or with
the burst's kind (aifoundry1-c1's SRAM rail: 0.54-0.58 s for each of its 14 kinds of burst; aifoundry3's: 1.02-1.06).
The fixed delay equals the SP pass under a 10 Hz sampler (E41: 156, 263 and 158 ms), and with the rails taken one
pass late the extra delay is 0.00 +- 0.03 s everywhere; `board_avg_w` needs no delay. The single-parameter fit
that the pages quote (tau 1.15-1.22 s, `catalogue.json` `rail_filter`) had folded that pass into tau.
aifoundry1-c1's SRAM rail is the exception on both counts: its extra delay is +0.03 s and its fixed-delay fit's d is
0.20 s against a 0.158 s pass (0.042 s over, near the 0.05 s band), so its delay items are centred on those values.

The input is square in the averaged channels but not in `board_w`. `board_w` (the board's input power, not averaged)
jumps to 95-97% of its step within 0.25 s and then creeps up during a burst (`offline.py --drift`, the 15-40 W
steps: median 1.1 %/s on aifoundry3, 2.1 %/s on aifoundry1-c1, 1.9 %/s on aifoundry2; p10-p90 0.8-1.5, 0.0-2.4 and
0.2-2.3 %/s), and after it a 1.4-3.5% tail decays over seconds: the die warms and leaks more. The deconvolved rails
and `board_avg_w` show no such creep (their in-burst slope is 0.000-0.003 /s of the step, against board_w's
0.012-0.021 /s), which is why the first-order fits leave only 1% and rise and fall agree. `board_w`'s creep bounds any
creep of the rails' true power (a rail's watts are part of the board's) and is the check of the input's squareness
(P4d).

Undoing it (`deconv.py`, each card's own tau; the square's step, baseline and edges from the fit):

| | raw reading | exact inverse | Gaussian 0.1 s | Gaussian 0.2 s | TV 0.03 W |
|---|---|---|---|---|---|
| plateau (mean over the burst's middle) | -24 to -30% (-13% a1c1 SRAM) | within 0.2% | within 0.1% | within 0.3% | within 0.4% |
| energy within 1 s of the burst | -10 to -13% | within 0.3% | within 0.3% | within 0.3% | within 0.3% |
| 10-90% rise | 2.2-2.5 s | 0.2-0.3 s | 0.3-0.4 s | 0.5-0.6 s | 0.2-0.3 s |
| scatter away from the edges (of the step) | | 5-11% | 1.6-3.9% | 1.0-2.2% | 0.5-1.4% |
| noise gain (over the reading's own scatter) | | 5.7-7.3 at a 263 ms pass, 10-13 at 157 ms (4.8 for tau 0.53 s) | 1.6-3.7 | 1.0-2.1 | 0.6-1.4 |
| 50% crossing against the kernel's edges | +0.6 to +0.9 s | +0.01 to +0.03 s | +0.01 to +0.02 s | +0.01 to +0.02 s | 0.00 to +0.03 s |
| full-window rms error (of the step) | 0.32-0.40 | 0.12-0.17 | **0.089-0.113: the smallest on 8 of 12 channels, within 0.002 of TV 0.1 W on aifoundry2's four** | 0.11-0.12 | 0.09-0.12 |

The white-noise gain of the exact inverse is sqrt(1 + a^2)/(1 - a) = 9.6 at a 157 ms pass, 5.7 at 263 ms and 4.9 for
tau 0.53 s; the measured gains are close (the pass times' own jitter adds a little). The full-window error is set by
the edges: each pass's time is known to +-50 ms at 10 Hz, which alone leaves about 0.09 of the step. The published
split (last 0.6 s / 0.94) of the catalogue's 3.2 s bursts errs by -1.8 to -4.3% on the rails of every card but
aifoundry1-c1's SRAM rail, where it errs by +5.5% (the 0.94 assumes tau near 1.1 s). Chosen: **Gaussian 0.1 s** as
the default (`deconv.py --sigma 0.1`: linear, no prior on the signal's shape); TV at 0.03 W for square bursts.

## Theories

- **T1 (first order).** Each rail reading and `board_avg_w` is a linear, time-invariant first-order average of its
  channel's power: one tau describes rise and fall at any step size, leaving about 1% of the step.
- **T2 (tau per card and rail).** The PMIC's averaging sets tau: 1.02-1.06 s on every rail of the 1.3.1-firmware cards
  (PMIC firmware 1.5.0), 1.06-1.07 s on aifoundry1-c1's minion and NoC rails and **0.53 s on its SRAM rail** (PMIC
  firmware 1.3.0); `board_avg_w` 1.05-1.11 s. The values of the table hold on a new block.
- **T3 (one pass late).** The service processor publishes the rails it read on its previous pass, so they are one SP
  pass late (plus the small offline extra delay of each rail, 0.00 +- 0.03 s), whatever the pass; `board_avg_w` is
  current. Rival: a fixed latency (the same delay at any pass).
- **T4 (the inverse works).** With the frozen tau of the table (not refitted), the deconvolved rails are square:
  plateau and energy within about 2% of the step for 2.0, 3.2 and 4.0 s bursts, edges within about 0.1 s of the
  kernel's, scatter away from the edges about 5% of the step; and the published split errs as the filter predicts
  (about -20% for a 2 s burst, where the deconvolved plateau does not).

## Predictions (prereg.json; the bands are the calibrated ones, below)

For the card the block runs on (aifoundry1-c1 in development, aifoundry3 in validation, aifoundry2 later), pooled over
its full, ok passes, from the bursts under the 10 Hz sampler unless stated:

| Item | Prediction | Theory |
|---|---|---|
| P0 | the SP pass is E41's: aifoundry3 0.263 / 0.321 s at 10 / 20 Hz, aifoundry1-c1 0.158 / 0.188, aifoundry2 0.156 / 0.187 (+-0.02) | (context) |
| P1 | tau of each rail (one pass late) and of `board_avg_w` (no lag) = the table's value for that card (+-0.06 s; aifoundry1-c1 SRAM +-0.08; aifoundry3 SRAM +-0.065) | T2 |
| P2a | the one-pass fit's extra delay = the offline value of that card and rail (`extra_d_s`: -0.01, 0.00, -0.02 s on aifoundry3; -0.01, **+0.03**, -0.02 on aifoundry1-c1) (+-0.05 s) | T3 |
| P2b | the fixed-delay fit's d = the pass this block measured + that extra delay, for each rail (+-0.05 s) | T3 |
| P2c | `board_avg_w`'s fixed delay is 0 (+-0.05 s) | T3 |
| P3 | under the 20 Hz sampler, the fixed-delay d = the 20 Hz pass this block measured + the extra delay, for each rail (+-0.05 s) | T3 against the rival |
| P3b | pooled over the three rails: mean d(20 Hz) - d(10 Hz) = pass(20 Hz) - pass(10 Hz), within half the predicted shift (aifoundry3: 0.058 +- 0.029 s, so the rival's 0 fails; aifoundry1-c1: 0.030 +- 0.015) | T3 against the rival |
| P4a | residual rms of the one-pass fit <= 1.5% of the step (aifoundry1-c1 SRAM 2.5%, aifoundry3 SRAM 1.6%) | T1 |
| P4b | rise and fall tau fitted apart (sum of squares over the bursts) agree: +-0.06 s (aifoundry3: minion 0.09, SRAM 0.115, NoC 0.085; aifoundry1-c1 NoC 0.07) | T1 |
| P4c | minion tau from the 20 W bursts (M) = from the 10 W bursts (H) (+-0.06 s; aifoundry3 0.065) | T1 |
| P4d | `board_w`'s in-burst drift on the M bursts (per s, of the step) is within the card's offline range (aifoundry3 0.0081-0.0148, aifoundry1-c1 0-0.0244, aifoundry2 0.0016-0.0234) | (context: the T1 "untested" rule) |
| P5a-e | deconvolved (frozen tau, Gaussian 0.1 s), per burst length 2.0 / 3.2 / 4.0 s: plateau within 2% of the step, energy within 2%, both 50% crossings within 0.1 s, scatter away from the edges <= 6% of the step, plateau within 2% of the step of a free-tau fit; wider where calibrated (below: up to 3.7% for plateaus of 2 s bursts, 4.7% for P5e, 0.12 s for edges, 8% for scatter) | T4 |
| P6 | the published split's error for 2.0 / 3.2 / 4.0 s bursts: [-28, -14]%, [-8, +2]%, [-4, +7]% on every rail but aifoundry1-c1's SRAM: [-6, +7]%, [-1, +12]%, [0, +13]% | T4 |

## Decision rules

- The unit of replication is the pass and the card, never the bursts inside one pass. Only full passes whose
  `block.json` says ok are pooled (`report` refuses others; a failed pass is re-run, its attempt set aside). Per-pass
  fits are reported beside the pooled ones.
- An item passes when its statistic is inside its band, compared after rounding to 4 decimals (a value on the 0.01 s
  grid at the band's edge passes).
- A theory **survives** on a card when every item that decides it there passes; it is **falsified** when one fails;
  **incomplete** when one is NO-DATA (the item is re-run or reported missing; NO-DATA is never a pass).
- **T3 is decided on aifoundry3 only**, where the 20 Hz pass is 58 ms longer (P3b's band is 29 ms, the midpoint
  between T3 and the rival). On aifoundry1's card 1 (a 30 ms shift) and on aifoundry2 (31 ms) every T3 item (P2a-c,
  P3, P3b) is computed and reported but decides nothing; the report says "reported only".
- **T1 untested, not falsified**: if a T1 item fails on a card whose P4d drift is above the top of that card's
  offline range, T1 is reported as untested there (the input was less square than in the offline data, where T1
  held), not as falsified. A T1 failure with P4d inside the range falsifies T1.
- A failed prediction is reported as failed. Development may change the block (README.md, "Development log") until the
  freeze; after it, nothing that `LOCK.sha256` covers changes, and any change to the plan is an amendment written
  before the data it touches.
- If T3 fails and the fixed delay holds, `deconv.LAG` becomes a per-card delay; if T1 is falsified on a channel, that
  channel gets a second pole; if T2's values move, `deconv.CARD_TAU` takes the validation card's fits.

## Calibration (simulated replicates, before any card data)

The prior bands were population medians over hundreds of offline bursts applied to 3-12 bursts per item, with all 96
items required to pass: in review, true theories failed on 3 to 5 of 6 simulated replicates at card-level noise.
`calibrate.py` now sets the bands so that a true theory fails on at most 5% of replicates per card, and checks that
the rival still fails.

- **The simulated card** (`stubs/stub-common.py`, used by the dry-run stubs and by `stubs/simulate.py`): the offline
  tau of each channel, the rails one SP pass late plus the offline extra delay (aifoundry1-c1's SRAM +0.03 s), the
  pass under each sampler rate, board_w's in-burst creep at the offline median, the enercat loop's burst lengths
  (2.0, 3.2, 4.0 s), block.sh's timeline (first line 0.30-0.45 s after launch, burst 1.5 s later plus 0.70-0.76 s of
  setup, a random SP phase per window), and white noise per SP pass set so that the simulated fit residual equals the
  card's offline residual (`calibrate.py match`; where the simulator's own residual, from the pass-time quantisation,
  is already larger, as on aifoundry1-c1's minion and board_avg, none is added). Noise level k: the residual is k
  times the offline one.
- **A replicate** is three full passes with the real pass numbers (so the real seeded burst orders), pooled and scored
  by `reduce.py`'s own code. Set A (bands): 40 replicates per card at k = 1.25. Set B (evaluation, fresh seeds): 40 at
  k = 1.0 and 40 at k = 1.25 per card, and on aifoundry3 the rival (the rails a fixed 0.263 s late) at k = 1.0 and 1.25.
- **The band of an item** deciding theory T (n items deciding T on the card: T1 9, T2 4, T3 11 on aifoundry3, T4 69)
  is the larger of its prior band and |mean| + z sd_up (one-sided items: mean + z sd_up; P6's ranges joined with
  mean +- z sd_up), with z the normal quantile of 1 - 0.05 / (2n) (one-sided 1 - 0.05 / n) and sd_up the replicates'
  sd times 1.186 (the upper 95% bound of an sd from 40 replicates), rounded outward. P3b stays at the midpoint (the
  true replicates need 0.0287 s on aifoundry3, inside 0.029). Of 96 items, 29 widened on aifoundry3 and 8 on
  aifoundry1-c1 (`prereg.json` `calibrated`, with each item's mean and sd):

| Widened (prior -> aifoundry3 / aifoundry1-c1) | |
|---|---|
| P1 SRAM | 0.06 -> 0.065 / (0.08) |
| P4a SRAM | 0.015 -> 0.016 / (0.025) |
| P4b minion, SRAM, NoC | 0.06 -> 0.09, 0.115, 0.085 / 0.06, 0.06, 0.07 (the simulated rise tau comes out 0.02-0.03 s above the fall tau on aifoundry3's 263 ms pass) |
| P4c | 0.06 -> 0.065 / 0.06 |
| P5a plateau, 2.0 s | 0.02 -> 0.024-0.037 / 0.02-0.025 |
| P5b energy, SRAM 2.0 s | 0.02 -> 0.022 / 0.02 |
| P5c edges, NoC 2.0 and 4.0 s | 0.10 -> 0.11, 0.12 / 0.10 |
| P5d scatter (six items) | 0.06 -> 0.065-0.08 / 0.06 |
| P5e plateau vs free fit (ten items on aifoundry3, six on aifoundry1-c1) | 0.02 -> 0.026-0.047 / 0.024-0.043 |

- **Result** (`calib.json`), the rate at which each theory is falsified on fresh replicates:

| Replicates (40 each) | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| aifoundry3, true, k = 1.0: prior bands / calibrated | 0 / 0 | 0 / 0 | 0 / 0 | 0.175 / **0** |
| aifoundry3, true, k = 1.25: prior / calibrated | 0.175 / **0** | 0 / 0 | 0 / 0 | 0.55 / **0** |
| aifoundry1-c1, true, k = 1.0: prior / calibrated | 0 / 0 | 0 / 0 | (reported) | 0.025 / **0** |
| aifoundry1-c1, true, k = 1.25: prior / calibrated | 0 / 0 | 0 / 0 | (reported) | 0.10 / **0** |
| aifoundry3, rival (fixed 0.263 s), k = 1.0: calibrated | 0 | 0.025 | **1.0** (P3b alone 40 of 40) | 0 |
| aifoundry3, rival, k = 1.25: calibrated | 0 | 0 | **1.0** (P3b alone 40 of 40) | 0 |

  0 of 40 bounds the false-fail rate below 7.2% (95%), 0 of 80 per card below 3.7%; the rival fails T3 on 80 of 80
  (power above 96%, 95% bound), on P3b alone. The dry runs through block.sh and the stubs agree: three passes of each
  profile score 96 of 96 with every theory surviving, the rival's three passes fail T3 only (P3b and P3 on the SRAM
  rail), and the block-run residuals are about 5% above the simulator's (the stubs' wall-clock jitter), inside the
  k = 1.25 margin. The cost is sensitivity: on
  aifoundry3, P4b now detects a rise-fall difference only above 0.085-0.115 s, and P5 plateaus of 2 s bursts are
  judged to 3.4-3.7% (the 2 s bursts are few: three per pooled block per kind). On aifoundry1-c1 (a 158 ms pass) most
  prior bands already held.
- The calibration assumes the card's noise is white per pass and scales with the step (the offline residual, as a
  fraction of the 9 W catalogue steps, applied to the block's 8-20 W steps): if the noise is partly a fixed number of
  watts, the real residuals are smaller and the bands conservative. It does not model the post-burst leakage tail of
  board_w in the rails (the deconvolved offline rails show none). aifoundry2 has no calibration yet: its amendment
  adds one.

## Plan and card time

Development on aifoundry1's card 1 (firmware 1.2.0, 600 MHz): a smoke (ten idle 3 s sampler windows back to back,
which measure the sampler's start latency and failure rate, then two short bursts: about 1 min of card time); the
full passes only if the smoke is ok with no failed start and every first line under about 1 s. Then passes 1-3
(about 2.3 min of card time each, 2 min apart; each starts only if its idle window's die mean is at most 72 C).
Freeze. Validation on aifoundry3 (firmware 1.3.1, pinned at 600 MHz): a smoke and passes 101-103. aifoundry2 (passes
201-203) only after DV2 ends, and after an amendment adds a heat step (its governor leaves 600 MHz on a cool die),
its own start temperature, a D burst that does not starve its sampler, and its calibration. About 8 min of card time
per card (at most 10 with repeated windows).

## Revisions before any card pass (2026-09-28, after review)

- Bands calibrated on simulated replicates (above); P3b pooled over the three rails with its band at the midpoint;
  P4b by sum of squares over the bursts (the median over 12 bursts on a 0.01 s grid was coarse and noisy); every
  comparison rounded to 4 decimals (0.06000000000000005 had failed a 0.06 band).
- P2a, P2b and P3 centred on each rail's offline extra delay (aifoundry1-c1's SRAM +0.03 s), and T3 decided on
  aifoundry3 only (the draft's "every item passes" had conflicted with "T3 is decided on aifoundry3").
- P4d and the T1 "untested" rule added; the offline creep of board_w (and its absence in the averaged channels)
  written down; the simulated card given board_w's creep, the rails' extra delays and matched noise.
- The bursts' order is seeded per pass (the 20 Hz windows and the 10 W burst were always last, on the warmest die);
  each pass starts at a die mean of at most 72 C and records its start and end die temperature.
- The block: 10 s for a first line and 6 sampler tries (a slow start was being stopped at 3 s), late starts repeated
  without a burst, each start latency logged, a ten-window smoke; on aifoundry1 two failed starts or a SIGKILL write
  tau/STOP (no drain is possible there); a smoke on the validation card needs the freeze; only an ok pass counts as
  done; `deconv.passes` uses each sampler segment's own interval (a global median would have moved every 10 Hz pass
  time 25 ms late once the 20 Hz samples were the majority); `build/enercat` (with the g3log fix) instead of
  `enercat_v2`; `et-who --check` after the block.
