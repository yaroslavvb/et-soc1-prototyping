# M12: M10 refitted POST HOC on E182 - held out on E178's 40 kinds it halves M10's error (0.122 to 0.068 W rms; int8 0.184 to 0.092, fp32 0.091 to 0.041; fp16 not better, 0.054 to 0.061), reads his pair at +0.047 W inside E178's +0.053 [+0.022, +0.085] (M10 +0.186, outside), and removes pool 8's class S bias (+0.18 to -0.05 W on aifoundry3) without cutting its scatter; its forecasts for 14 candidate trains of a next one-number run are frozen (05:07:07 PST)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q157): no card, device command, card session, lab box, post or deploy. The
rules, [`REFIT.md`](REFIT.md), were committed alone first (`d5eb87b5`, git 04:56:09 PST), before the fitter, the held-out scorer and the
candidates' forecasts existed as committed files; its [dated note 1](REFIT.md.dated-note-1.md) corrects one candidate word before any
forecast of it. **Everything here is post hoc** (fitted after E182's data); the held-out rows were never fitted but were seen before the
rules were written (REFIT.md section 6). **Nothing is registered.** It answers the card day critic's rank 5 (Sun 8 Nov) and serves the kinds
page's [section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "a power model across kinds",
for the owner's ask of Thu 5 Nov 2026, about 19:30 PST: "here's a matrix filled with one number, and here's a matrix filled with another
number, and they require different number of transistor flips, therefore they will use different power, and I have a model which actually
tracks it down."*

**M10 stays frozen.** M12 is the lab's next free model name (no `M12` model exists in `AGENT.md`'s index or `docs/findings/`). It changes
M10 only for held-word tiles (every lane's A word and B word one value, or one side two values one bit apart); every other tile is M10.

## The model and its fit (post hoc; [`fit-m12.txt`](fit-m12.txt), [`m12.json`](m12.json))

    int8 one-number tiles   D8 = c8 + R (k_walk F_walk + k_scp F_scp) + beta_A h_A + beta_B h_B
    float held-word tiles   Df = P10 + c_f + gamma_A pc_A + gamma_B pc_B        (P10 = M10 frozen; fp16 takes fp32's terms)

F_walk is the accumulator's walk (E178's flip model: storage, read and write data), F_scp the scratchpad's read data alternating A and B
chunks, flips an op; h the popcount a byte; pc the 32-bit words' popcounts. Fitted by weighted least squares on E182's committed rows
only: int8 on its 20 kinds-pass means and trains T1-T4, fp32 on its 4 kinds' D - P10 and trains T5 and T6.

| term | M12 | se | what it replaces |
|---|---:|---:|---|
| int8 k_walk, fJ a walk flip | **1.239** | 0.139 | one price for every flip: M10's line over E182's kinds 7.04 fJ, E182-W-int8's measured 3.79 |
| int8 k_scp, fJ an A/B switching flip | **12.87** | 1.74 | (the same single price) |
| int8 beta_A, W a held 1-bit a byte | **+0.00839** | 0.00023 | M10 0 |
| int8 beta_B | **+0.00986** | 0.00023 | M10 +0.0157 (B only) |
| int8 c8, W over zeros | +1.6820 | 0.0144 | the level offset |
| fp32 gamma_B - gamma_A (placement), W a held bit | **+0.010253** | 0.000129 | M10 0 |
| fp32 gamma_A / gamma_B | +0.00303 / +0.01328 | 0.00086 each | M10 0 |
| fp32 c_f, W | -0.0114 | 0.0239 | the level offset |

- **Why two int8 flip prices** (found in exploration of E182's own rows, before REFIT.md): one price cannot hold both his pair's train
  (a walk-only difference at fixed held bits, T1 +0.0470 W) and the kinds passes' spread. Fitted to the kinds alone one price is 2.75 fJ
  and forecasts T1 at +0.082 W (arm M12-KO); fitted jointly it is 1.26 fJ (arm M12-1K). Priced apart, the walk costs 1.239 fJ a flip and
  the scratchpad's A/B switching about 10 times as much, and the kinds-pass residual sd falls to 0.036 W, near the passes' own noise. The
  task's "per-flip price near 3.79 fJ" is E182-W-int8's single slope, which mixes the two classes and B's held bits.
- **In sample:** every int8 train within 1.9 se (T4 -1.86); T5 and T6 at +0.02 and +0.57 se; the fp32 kinds within 0.03 W.

## Held out (post hoc; [`heldout-m12.md`](heldout-m12.md), [`heldout-m12.json`](heldout-m12.json))

Residual e = measured D - model, W; 95% = the row's t interval over its passes with 1.96 x the model's se. The paired difference is
rms(M12) - rms(M10) with a bootstrap over the group's rows (2,000 draws).

| rows (never fitted) | M10 rms (bias) | M12 rms (bias) | M12 centred rms | 0 inside M12's 95% | rms(M12) - rms(M10) [95%] |
|---|---|---|---:|---:|---|
| **E178 int8, 13 kinds** | 0.184 (-0.160) | **0.092** (-0.089) | 0.025 (M10 0.091) | 6 of 13 (M10 2) | **-0.092 [-0.145, -0.038]** |
| **E178 fp32, 14 kinds** | 0.091 (+0.083) | **0.041** (+0.027) | 0.031 (M10 0.036) | 14 of 14 (M10 6) | **-0.050 [-0.067, -0.032]** |
| E178 fp16, 13 kinds (F16-SAME, an extrapolation) | 0.054 (+0.029) | 0.061 (-0.058) | 0.021 (M10 0.046) | 12 of 13 (M10 11) | +0.007 [-0.026, +0.034] |
| **E178, all 40** | 0.122 (-0.014) | **0.068** (-0.038) | 0.056 (M10 0.121) | 32 of 40 (M10 19) | **-0.054 [-0.083, -0.024]** |
| pool 8 class S, aifoundry3 (E171), 10 new tiles | 0.254 (+0.184) | 0.181 (-0.048) | 0.175 (M10 0.176) | 6 of 10 (M10 3) | -0.073 [-0.158, +0.034] |
| the same, the 8 priority-1 tiles | 0.273 (+0.195) | 0.192 (-0.029) | 0.190 | 5 of 8 (M10 2) | -0.081 [-0.174, +0.046] |
| the same, its 3 re-run single-bit tiles | 0.316 (-0.059) | 0.352 (-0.184) | 0.300 | 0 of 3 (M10 1) | +0.036 [-0.132, +0.125] |
| class S, card 1 (E172, secondary), 10 new | 0.236 (+0.156) | 0.179 (-0.067) | 0.166 | 7 of 10 (M10 5) | -0.057 [-0.164, +0.049] |

- **His pair, E178-H-int8 (int8 5s - 4s):** measured +0.0532 W [+0.0217, +0.0848]; **M12 +0.0470 (se 0.0032), inside**; M10 +0.1857,
  outside; M12-1K +0.0476; M12-KO +0.0821.
- **int8:** M12 gets the shape (centred rms 0.025 against M10's 0.091: 85s read -0.029 against M10's -0.354, 127s -0.088 against -0.271),
  not the level: every E178 int8 kind reads about 0.09 W under it, E178's session level against E182's. The one-price arms keep the shape
  (0.026, 0.028) but sit 0.06 W further down (M12-1K -0.159, M12-KO -0.148), because E178's int8 kinds have almost no A/B switching.
  **Arm M12-S1** (each session's own random int8 anchor; chosen after a look, REFIT.md section 6, reported only) moves the level by -0.074 W
  and reads 0.029 W rms (bias -0.015, 12 of 13 inside): post hoc in the strong sense, a candidate for registration, not a result.
- **fp32:** the placement and held-bit terms carry E178's one-number kinds: M10's +0.08 W bias falls to +0.03, every kind inside.
- **fp16:** fp32's terms per held bit of the 32-bit word (F16-SAME) give the right shape (centred 0.021 against 0.046) but a level 0.06 W too
  high; fp16 without held-bit terms (F16-NOHB) reads 0.061 W (+0.040). fp16 is not carried by E182; the fp16 swap H16 below tests it blind.
- **Class S:** adding B's held 1-bits (the base word's popcount, mean over the two words) moves M10's class bias from +0.184 to -0.048 W
  on aifoundry3 and from +0.156 to -0.067 W on card 1, but the tile-to-tile scatter (centred rms 0.17-0.19 W) stays: the class's misses are not a held-bit level,
  and the rms difference is not resolved. The A = 0x40080727 tile and the re-runs read worse (fp32.b_onebit_b20_one -0.58 W).
- **Gain against offset** (REFIT.md section 4's words, reported): GAIN for M10's int8 (-0.0031 W of rms [-0.0042, -0.0019]), fp32 (-0.0006)
  and fp16 (-0.0007) and for M12's fp32 (-0.00007); OFFSET for M12's fp16 (+0.0001). **Every difference is under 0.004 W, about a tenth
  or less of a row's own 95% half-width (0.03-0.3 W), so the two forms are practically the same on these rows** (within a format the
  predicted levels span only 1.6-2.2 W in int8 and 8.2-8.4 W in the floats). The stated rule's bootstrap resamples rows but holds each row's
  measured value fixed, so it reads which form fits these realized values, not whether the gap is a gain beyond the noise: a defect of the
  rule, disclosed here, not changed. M10's int8 "GAIN" reflects its too-steep int8 prices (its misses grow with P), which M12 corrects by
  its prices, not by a gain.
- **Card 1's SRAM factor** (E184 arm B, 1.41205 times the reading, E184-M NOT RESOLVED, load-dependent): carried in `m12.json` as a
  reported candidate, **never applied**.

## Candidate kinds for a next one-number run, frozen ([`candidates-m12.md`](candidates-m12.md), [`FREEZE-m12.md`](FREEZE-m12.md))

**Frozen Sun 8 Nov 2026 05:07:07 PST, `candidates-m12.json` sha256 e97a2ae4fb27d6d161d1fd209f13a7fad91c10c1455a86b984625862fb734907; a
candidate for the next registration, not registered.** Operand words only; aifoundry3, s = 1, E182's rates. Each train at E182's train
noise (half-width 0.0051 W at 32 units, se 0.0025 W).

| train | first - second (A word / B word) | M12, W (se) | M10, W | power if M12 | separation (se) |
|---|---|---:|---:|---:|---:|
| H16, the fp16 swap | (3c00 / 3fff) - (3fff / 3c00), 20 bits a word moved | **+0.2051** (0.0026) | 0 | 1.00 | 57 |
| S23, fp32 swap | (1.0 / 3f80ffff) - (3f80ffff / 1.0), 16 bits | +0.1640 (0.0021) | 0 | 1.00 | 51 |
| S15, fp32 swap | (1.0 / 3f8000ff) - (3f8000ff / 1.0), 8 bits | +0.0820 (0.0010) | 0 | 1.00 | 30 |
| Q63-sign, int8 | (-1 / -63) - (1 / 63) | **+0.0292** (0.0017) | -0.0471 | 1.00 | 25 |
| Q63-swap, int8 | (1 / 63) - (63 / 1) | +0.0073 (0.0016) | +0.0785 | 0.78 | 24 |
| B23-B15, fp32 B side | (1.0 / 3f80ffff) - (1.0 / 3f8000ff) | +0.1405 (0.0069) | +0.0343 | 1.00 | 14.5 |
| B15-B7, fp32 B side | (1.0 / 3f8000ff) - (1.0 / 1.0) | +0.1261 (0.0069) | +0.0199 | 1.00 | 14.5 |
| Q3-sign, int8 | (-1 / -3) - (1 / 3) | +0.1080 (0.0021) | +0.0785 | 1.00 | 9.0 |
| Q3-swap, int8 | (1 / 3) - (3 / 1) | +0.0015 (0.0003) | +0.0157 | 0.08 | 5.6 |
| A23-A15, fp32 A side | (3f80ffff / 1.0) - (3f8000ff / 1.0) | +0.0585 (0.0069) | +0.0343 | 1.00 | 3.3 |
| A15-A7, fp32 A side | (3f8000ff / 1.0) - (1.0 / 1.0) | +0.0441 (0.0069) | +0.0199 | 1.00 | 3.3 |
| EB, equal popcount, B side | (1.0 / 3ff80000) - (1.0 / 3f80000f), four high against four low mantissa bits | -0.0023 (0.0000) | -0.0023 | 0.13 | 0 |
| EA, its A-side mirror | (3ff80000 / 1.0) - (3f80000f / 1.0) | -0.0023 (0.0000) | -0.0023 | 0.13 | 0 |
| X8, int8 across products | (1 / 63) - (1 / 3) | +0.1510 (0.0137) | +0.1553 | 1.00 | 0.3 |

- **What each tests blind:** H16 the fp16 rule (M10 says 0, M12 +0.205 W); S15, S23 and T5 together the placement term's linearity in
  the bits moved (8, 16, 23); B and A the two sides' slopes apart (M12's B side 4.4 times its A side); Q3 and Q63 beta_A and beta_B at new
  products, where M10's B-only price gives the other sign on Q63-sign; EB and EA a popcount term against a position-dependent one (M12 and
  M10 agree on -0.002 W; at this noise a position effect of about +-0.007 W would be read with power 0.8); X8 does not separate the
  models.
- **A first registration's subset** by separation, about 65 card-minutes of trains at E182's train lengths (int8 8.3 min, fp32 9.7): H16,
  S23, Q63-sign, Q63-swap, B23-B15, A23-A15 and EB.
- **Checks:** the bench's zeros rows and fp32.ones equal E178's committed counts to the net; `check_mismatch` 0 at every point; the flip model
  reproduces E182's committed flips for three of its kinds; the swap pairs' bench nets are equal, so M10's swap differences are exactly 0.

## The labels

- **Post hoc:** every M12 parameter, every in-sample figure and every held-out residual. **Held out:** E178's 40 kinds and his pair, pool 8's
  class S on both cards, never fitted. **Reported:** every arm, the gain/offset words and card 1's SRAM factor. **Forecast, frozen:** the
  candidates (blind only once a registration commits them before its first datum). **Registered:** nothing. **Blind:** nothing here.

## What it does to predicting power

- **A held 1-bit costs on both operand sides in int8, at about 0.0084 (A) and 0.0099 (B) W a bit a byte, and the int8 flips are priced by
  class:** the accumulator's walk at about 1.2 fJ a flip, the operands' A/B switching on the scratchpad read data at about 13 fJ. With those
  prices M12 carries E178's int8 shape held out (centred rms 0.025 W against M10's 0.091) and his pair (+0.047 against +0.053 measured).
- **In fp32 a held 1-bit on B's side costs about 4.4 times one on A's** (0.0133 against 0.0030 W a bit); with that, E178's 14 fp32 kinds
  read 0.041 W rms held out, every one inside, against M10's 0.091.
- **What it does not do:** carry a session's int8 level between sessions (E178's sit 0.09 W under E182's), carry fp16 (an extrapolation that
  overshoots), or cut class S's tile-to-tile scatter. Gain and offset are not told apart on one-number rows.

## What ran, and the files

- **Where:** the fits, the held-out scorer, the candidates' stages, the checks and the self-test on the Intel through the round's local slot,
  one job at a time, `/usr/bin/python3` 3.9.6 (numpy 1.26.4 for M10's feature chain only); the toggle bench on the mini through the batch-work
  door (`run_remote --host mini --max-gb 4 --timeout 900`, 4 workers), 05:03:09-05:05:19 PST, the recorded build (`Vtb` sha256 `a740318c...`).
- **Re-run:** `fit_m12.py --check`, `heldout_m12.py --check` and `candidates_m12.py check` each reproduce their outputs byte for byte;
  `selftest_m12.py` (synthetic data) 10 of 10 PASS ([`logs/selftest-m12.txt`](logs/selftest-m12.txt)).
- **Files:** `REFIT.md` and `SHA256SUMS-m12-rules` (`d5eb87b5`); `REFIT.md.dated-note-1.md`; `m12_common.py`; `fit_m12.py`, `m12.json`,
  `fit-m12.txt`; `heldout_m12.py`, `heldout-m12.json`, `heldout-m12.md`; `selftest_m12.py`, `logs/selftest-m12.txt`; `candidates_m12.py`,
  `kinds-m12.json`, `tiles/` (18 new tiles), `bench/bench_m12.sh`, `bench/counts-m12.json`, `candidates-m12.json`, `candidates-m12.md`,
  `FREEZE-m12.md`; this README; [`SHA256SUMS-m12`](SHA256SUMS-m12) (every file but itself and this README).

## Disclosures

- **Seen before the rules:** E178's per-kind levels, both sessions' anchors and pool 8's class S rows were displayed while learning the
  files' layouts (REFIT.md section 6); arm M12-S1 was added after that look.
- **One word corrected before its forecast:** REFIT.md's CEQ high-mantissa word 0x3ff00000 (popcount 10) is 0x3ff80000 (popcount 11) by
  the rule's own words (dated note 1); the two tiles staged with the wrong word were removed before the bench ran.
- **The gain/offset rule's defect** (above): its interval holds the measured values fixed.

## What remains

- A verifier of this directory; the records round (02-05, the indexes, the kinds page's item 6) with M12 as post hoc.
- A registration that takes the candidates (or a subset) with its own rules, kit and readiness critic; M12-S1's session anchor registered
  as a rule before any int8 level is quoted across sessions; an fp16 one-number set to fit fp16's terms; class S's scatter, still open.

SPDX-License-Identifier: Apache-2.0
