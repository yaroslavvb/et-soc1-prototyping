# V3-HLF: the heat path's time constants (E73, Q129)

*Pre-registered Tue 27 Oct 2026 (week 44), before the first card pass. This commit freezes the design,
the predictions, the analysis code and the decision rules; any change after it goes in Amendments at
the end, dated, before the data it touches.*

**The ask** (the owner, through the Q129 brief, Tue 27 Oct 2026): *"E73, the thermal camera lock-in at
a further frequency on aifoundry2 (the coda's heat-path time constants, Levels tab). E63 ran the top
rung (lq_h23) against its zero at 0.05 Hz (194 ± 9 mK, heat 87 degrees behind); Q126 added a 0.15 Hz
transfer point. Add 0.02 Hz (and 0.01 Hz if time allows) so a two-pole heat-path model can be fitted
across the frequencies. … Use E63's pipeline (tools/claims-v3/hlc) with per-stretch shutter offsets,
and pair each block with a reference rung nearby (the camera's gain drifts with temperature)."*

## The question

The back of aifoundry2's board answers a switched load like a low-pass filter: E63 put 4.02 W of
flipping bits on it at 0.05 Hz and read 119 ± 13 mK, with the heat **99° behind** the watts. Q126 read
the same fit's third harmonic and got a second point, H(0.15 Hz) = 18.4 ± 5.4 mK/W at 151°.

Two points, one of them at the noise floor in every single block, do not fix a heat path. Worse, they
**cannot**, in a specific and interesting way:

* A lag of 99° at 0.05 Hz is already **more than one pole can give** (90° is a single pole's limit), so
  the path is not one pole.
* But the magnitude falls only to 0.343 ± 0.104 of itself between 0.05 and 0.15 Hz, which is a *shallow*
  roll-off. A two-pole model forced to give 99° at 0.05 Hz can reach a ratio of at most **0.304** — and
  it gets there only by sending one pole to infinity, which is not a heat path at all. The measurement
  sits 0.37 SE *above* that ceiling.

So one picture says *one pole and a transport delay* and the other says *two poles pushed against their
own boundary*, and the data that exists cannot separate them. They differ in the **low-frequency group
delay**: 13.5 s against 7.5 s. That is read off the **phase**, which is the one quantity the camera's
drifting gain cannot touch. E73 goes and measures it, an octave and a half below where anyone has looked.

## Design

**Card and instrument, as they are. Nothing is changed on either.** aifoundry2, governor untouched —
read fresh at 15:38 PDT under the card lock and left alone: `tdp_w 65, temp_threshold_c 65,
power_state low_power, minion 600 MHz / 519 mV`, which are the values E72 restored and read back at
15:24 the same afternoon. **No governor command, no clock command, no PMIC, no reset, no firmware
action of any kind is part of E73.** The Thermal Master P3 behind the card, recorded on aifoundry2 from
the phone's lossless `/stream.raw.z` by E62's `record_cam.py`; the camera's settings are not changed,
so the public live page stays as it is. A 95 s camera-only recording at 15:44 PDT, with no card
involved, found the stream healthy (2,377 packets, 25.01 fps, 0 gaps, 11 shutter events = 6.9 a
minute, which is E63's rate) and the **view in the same place**: the scene registers against E62's
reference at a shift of (−1, −1) full-resolution pixels, (0, 0) binned, peak correlation 0.94, so the
template is kept, not rolled.

**Kernel, operands and geometry: E63 amendment A1's, unchanged.** The Horace kernel
(`sparsity_host --test fma --type fp32 --pattern none --values file:<tiles>`), E60's own operand files
`lq_h23` (the top rung, 94,208 designed B bit flips per op per minion) and `lq_h0` (its zero), 6
minions in each of the 32 shires (**192 harts**), one launch per phase of `--seconds 8.5 --budget 9.5`
under `timeout 10`, idled out to a **10 s dwell**. A1's geometry, not session 1's, because A1 is the
one that held 800 MHz through all five of E63's rules.

**The only thing E73 changes is how many of those 10 s phases make up a half period.**

| Block | Phases an arm | Lap | f₀ | Laps (warm-up) | Analysed |
|---|---|---|---|---|---|
| `E73-REF1` | 1 | 20 s | **0.05 Hz** | 15 (3) | 4.0 min |
| `E73-F25` | 2 | 40 s | **0.025 Hz** | 12 (2) | 6.7 min |
| `E73-REF2` | 1 | 20 s | **0.05 Hz** | 15 (3) | 4.0 min |
| `E73-F10` | 5 | 100 s | **0.01 Hz** | 11 (1) | 16.7 min |
| `E73-REF3` | 1 | 20 s | **0.05 Hz** | 15 (3) | 4.0 min |

248 launches, 43.3 min of card time by the runner's own estimate, caps 52 card-min / 65 wall-min.

**Why 0.025 and not the 0.02 the ask names — a departure, stated here.** A half period has to be a
whole number of launches, because `timeout 10` caps a device hold at 10 s (`AGENT.md` §4) and the
alternative — keeping two launches an arm and stretching the idle tail from ~1.1 s to 4 s to reach 25 s
— walks straight into the one hazard E63 measured: with idle gaps before launches the governor's
idle-reset drops the clock to 600 MHz for about a second in roughly 1 launch in 45, *at any load*.
Lengthening the gap four-fold to chase a round number would trade a known-good geometry for an unknown
one. On a 10 s dwell the ladder lands on **0.05/N Hz**: 0.05, 0.025, 0.0167, 0.0125, 0.01. E73 takes
0.025 and 0.01, which bracket 0.02, and keeps E63's launch geometry *exactly*, which is what makes
E63's own 0.05 Hz number a valid anchor rather than a near-miss.

**The references, and why a third of the session goes to them.** The camera's gain drifts with its own
temperature — E63 watched it fall 59 → 42 mK/W over an hour. Each new frequency is therefore bracketed
by a 0.05 Hz block of the **same rung pair**: REF1 F25 REF2 F10 REF3. The three references are fitted
with a straight line in time, every block is corrected to the session's mid-time by that line, and the
line's own uncertainty at each block's time goes into that block's error. A ratio to 0.05 Hz is then a
ratio between two numbers taken minutes apart on the same camera.

**The harmonics come free.** The two arms differ only inside their launch windows and the idle tail is
identical in both, so the difference drive is odd in the half period and carries **only odd harmonics**
of f₀; the common on-pattern carries the even ones and cannot leak into f₀. Reading the odd harmonics
out of the same fit — which is what Q126 did to get 0.15 Hz — turns five blocks into **nine
frequencies** on one 0.005 Hz grid:

| f / Hz | 0.01 | 0.025 | 0.03 | 0.05 | 0.07 | 0.075 | 0.09 | 0.125 | 0.15 |
|---|---|---|---|---|---|---|---|---|---|
| from | F10 k1 | F25 k1 | F10 k3 | **REF k1 *and* F10 k5** | F10 k7 | F25 k3 | F10 k9 | F25 k5 | REF k3 |

0.05 Hz is measured **twice over, by two different routes**, which is rule R5.

**The shutter, planned around, exactly as E63.** Every stretch between two shutter events gets a free
offset and the signal is read only from the variation inside the stretches; nothing is ever bridged.
This costs signal at low frequency and costs it in a calculable way — a stretch of 7 s spans 126° of a
20 s cycle but only 25° of a 100 s one — but the signal grows as the frequency falls, and the two
roughly cancel: that is why F10 is given 16.7 minutes against REF's 4.0.

## The analysis code

`lockin_hlf.py` **imports E63's frozen `lockin_hlc` and calls its `analyse_block` verbatim.** Exactly
three of its module functions are replaced, each because a half period of N launches breaks an
assumption that only held for N = 1, and **each reduces to the original at N = 1**:

1. `block_laps` — `len(ps) == 2` becomes `len(ps) == 2N`. The lap still runs from its first phase's
   planned start to its last phase's planned end, so the phase `phi`, the bin selection and `f_hz` are
   untouched.
2. `design` — the drift spline's knot spacing was the constant `KNOT_S = 40 s`, which is **2 laps** at
   E63's 20 s lap but would be 0.4 of a lap at 100 s, where a cubic spline could absorb the signal. It
   is now 2 lap periods for every block, which is E63's own ratio. The shared third-harmonic pair
   becomes one pair per harmonic in {3, 5, 7, 9}.
3. `steady_steps` — arm A is phase indices 0…N−1 and arm B is N…2N−1, and the step is the median over
   all of arm A's steady windows minus the median over all of arm B's.

`harmonics_block` is new, and is the point: it keeps the shared odd-harmonic coefficients the registered
fit computes and throws away, for the camera ROI **and** for the board power out of the same fit, and
forms H(kf₀) = Z_k(camera)/Z_k(board) in mK per watt. Numerator and denominator come from the same
frames and the same fit, so the drive's own shape divides out. Errors are jackknifed over laps, the
same lap dropped from both, which is the convention Q126 established.

**Regression test, run before this commit** (aifoundry2, E63 session 2's own RED, `--harmonics 3
--knot-laps 2.0`, which makes the patched code bit-for-bit E63's): `E63-TOP` 118.7 ± 13.0 mK at 96°,
p = 5 × 10⁻⁵, board step 4.020 W, H(f) 47.8 mK/W at 100°; `E63-NULL` SE 5.04 at −101°; `E63-MID`
36.3 ± 3.3 at 101°; `E63-TOP2` 103.8 ± 21.8 at 104°. Every one of those is the registered
`s2/analysis/lockin.json` number, and the H(f) is Q126's `h3-rails.json` row to three figures.

## Predictions (frozen with this commit, `predictions.json`)

Two rivals, each with **two** free parameters fitted to the two existing points, and nothing fitted to
E73 data:

| | shape | fitted to | τ | predicts |
|---|---|---|---|---|
| **M1** | one pole × a transport delay | the magnitude ratio 0.343 (τ) and the 99.1° lag at f (T_d) | τ = **12.19 s**, T_d = **1.32 s** | arg H(3f) = 156.3° (measured 150.6°) |
| **M2** | two poles | the two measured lags, 99.1° and 150.6° | τ₁ = τ₂ = **3.73 s** | ratio 0.178 (measured 0.343 ± 0.104, 1.6 SE) |

Group delay **13.51 s** against **7.47 s**. Where that lands:

| f / Hz | M1 \|H\|/H(0.05) | M1 lag | M2 \|H\|/H(0.05) | M2 lag |
|---|---|---|---|---|
| **0.010** | **3.14** | **42.2°** | **2.25** | **26.4°** |
| 0.025 | 1.84 | 74.3° | 1.63 | 60.8° |
| 0.030 | 1.59 | 80.7° | 1.49 | 70.3° |
| 0.050 | 1.00 | 99.1° | 1.00 | 99.1° |
| 0.090 | 0.57 | 124.5° | 0.44 | 129.3° |

In millikelvin on the camera, on E63 A1's own 4.02 W step and 52.7 mK/W: F10's fundamental is predicted
at **378 mK (M1)** or **271 mK (M2)**, on an expected SE of 40–50 mK; F25's at 225 or 217 mK.

## Decision rules (frozen; scored by `fit_hlf.py`)

- **R1 — detected at 0.01 Hz.** `E73-F10`'s ROI fundamental is ≥ 3 SE from zero with sign-flip
  p ≤ 0.01, **and** its board fundamental is ≥ 5 SE. Otherwise the 0.01 Hz point is a non-detection and
  R3/R4 are not scored.
- **R2 — the reference line.** The three 0.05 Hz blocks' |H| agree with a weighted straight line in
  time within 3 SE each. That line is what every ratio to 0.05 Hz is taken against; its slope is the
  session's gain drift.
- **R3 — the heat path is low-pass.** |H(0.025)|/|H_ref| > 1 and |H(0.01)|/|H_ref| > |H(0.025)|/|H_ref|,
  each by at least 1 SE. A flat or falling ratio refutes the picture E63 built.
- **R4 — the group delay. This rule has no PASS by design.** The measured lag at 0.01 Hz is compared
  with M1's 42.2° and M2's 26.4°, and the surviving model is named at 2 SE. **Both may fail**, and if
  both fail that is the result.
- **R5 — 0.05 Hz twice over.** `E73-F10`'s fifth harmonic agrees with the reference line's H(0.05)
  within 3 SE of the complex difference.
- **R6 — hold.** At least 95% of the in-launch telemetry samples (from 1.5 s into each launch) of every
  block's analysed laps read ≥ 790 MHz, and every block's die mean stays under 65 °C. The per-launch
  one-second dips are counted and reported **without a verdict** — E63's lesson is that a per-launch
  gate fails on the governor's idle-reset dip at any load.
- **Inclusion.** A transfer point enters the across-frequency fit only when its board amplitude is
  ≥ 5 SE. Points that fail it are published with their errors and left out of the fit.

Then, and only then, the deliverable: `fit_hlf.py` fits **P1** (one pole), **P1D** (one pole and a
delay), **P2** (two poles) and **P2D** (two poles and a delay) to every included point by weighted
complex least squares with one real positive gain — a complex gain would absorb a phase offset and
hollow out the comparison — and reports χ², reduced χ², AIC and the Δχ² = 1 interval of each time
constant.

## Safety and etiquette

E63 A1's caps, unchanged: `abs_stop_c 80 °C`, `board_cap_w 70 W` on two consecutive samples,
`sampler_stale_s 3`. The heaviest arm sat at ~40 W and a 60–61 °C die in E63. `run_hlc.py` takes
`/run/lock/etsoc-shire0.lock` for every launch, refuses a real session on any host but aifoundry2,
holds every launch under `timeout 10`, and stops on a `STOP` file in the RUNDIR. The card was claimed
in `#community-lab` before the first launch and released after the last. **No governor, clock, PMIC,
reset, PCIe or driver action occurs anywhere in this experiment**; the governor was read, once, and
left alone.

## Files

| File | What |
|---|---|
| `make_protocol_e73.py`, `protocol-e73.json` | the ladder: five blocks, 248 launches |
| `predict_e73.py`, `predictions.json` | the drive's own spectrum, M1 and M2, the rules |
| `lockin_hlf.py` | E63's lock-in with the three named generalisations, plus the kept harmonics |
| `fit_hlf.py` | the reference line, the transfer table, the four model fits, the rules scored |
| `run_e73.sh` | stage the frozen code on aifoundry2, check, go, watch |

## Amendments

*None to the design or the analysis: the session of Tue 27 Oct 2026, 15:57–16:40 PDT, ran the protocol
above and was scored by the frozen `fit_hlf.py`. The entries below are after-the-data notes, dated, and
they change no registered number.*

- **Wed 28 Oct 2026 — the frozen copy on the card host is one edit behind this commit, with no
  numerical effect.** `run_e73.sh stage` copied `lockin_hlf.py` at 15:52 Tue; the committed file carries
  a 15:53 edit whose whole content is the seven lines that let it find `lockin_hlc.py` in either layout
  (the repo's sibling `hlc/`, or the subdirectory the staging builds). On 28 Oct the lock-in and the fit
  were re-run on aifoundry2 from the same RED with the **committed** file: `lockin.json` came back
  byte-identical (sha256 `d29e801f…`), `fit.txt` identical, all five `*-maps.npz` identical, `fit.json`
  different only in the input path it records.
- **Wed 28 Oct 2026 — `posthoc/fit_priors.py`, post hoc and no verdict.** The registered fit uses E73's
  own points with one gain. This script adds the two anchors the pre-registration names (E63 A1's
  0.05 Hz and Q126's 0.15 Hz) to the same fit under a second gain, with a circular error for the pooled
  anchors, and profiles the Δχ² = 1 interval of the group delay and of the zero-frequency gain, which
  the frozen script reports as point values. Both added choices were made after the data were seen; the
  conclusion is the same as the registered fit's. See
  [`docs/reports/data/2026-10-27-e73-camera-frequencies`](../../../docs/reports/data/2026-10-27-e73-camera-frequencies/README.md)
  § Departures, items 3 and 4.
- **Wed 28 Oct 2026 — files.** `reduce_e73.sh` (the reduction in order, run on the card host) and
  `posthoc/fit_priors.py` are committed with the data; they were written during and after the session
  and are not part of what the predictions were frozen against.
