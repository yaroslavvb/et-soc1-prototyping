# Q138(t): the die's step response over minutes, frozen for E144 (desk, Mon 2 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 9, "A steady state for heat", and item 8, "The heat path drifts between sessions". It answers the page's "After Q137, the next
steps" (2): "a long hold scored against a frozen step response". Desk only: no card, no device command, nothing set. Everything here
comes from committed raw telemetry (E89, E97, E111, E133) and E78's switching powers. E144 is scored against these files as they are
committed, and must check that this commit is on origin before its claim.*

## What this changes for predicting heat

| What is predicted | Before (M6 and the lab's chains) | After (this frozen chain, out of sample at the desk) | Source |
|---|---|---|---|
| **aifoundry3: the die through a 15–30 min hold, given its board trace** | M6 quotes a plateau only, about 0.9 °C per board W. Used as an instantaneous rule, it gives rms **1.5–11.6 °C** over E97's holds, −4.3 to −13.0 °C at 60 s. E89's frozen chain (E97's registration): **0.72–0.78 °C** | **0.47–0.66 °C** rms over each hold, leaving that hold and its cool-down out of the fit. Plateau errors **−0.40 to +0.82 °C**, cool-downs **0.12–0.33 °C** | [`fit.txt`](fit.txt), [`cv-q138t.json`](cv-q138t.json) `a3` |
| **aifoundry2: the same, governed** | M6's 0.673 °C per board W, instantaneous: **1.9–5.1 °C** rms. One pole of 89 s (E111's asymptote beside): **0.91–1.21 °C**, up to 5.4 °C off in the first minutes | Fitted on one day and scored on the other: **0.44–1.16 °C** rms, plateau errors **−0.48 to +1.16 °C**. The whole-degree rest reading alone carries ±0.5 °C | `cv-q138t.json` `a2` |
| **aifoundry3: a plateau from the planned power only** (E78's S × duty, closed through the idle law) | the plateau coefficient × an assumed board rise: no number without the board's watts | E97's three holds come out **0.3–1.0 °C** under, which is **in sample** for the chain: E97 trained it | `predictions-e144.json` `aifoundry3.backcheck_on_E97` |

**So:** the term this lane measures and freezes is the time-resolved heat path, a five-stage chain per card from board watts to the die.
M6 had only a plateau coefficient. On minutes-long holds this cuts the die's error from 1.5–11.6 °C (the plateau rule used as a
trajectory) to about 0.5–0.7 °C on aifoundry3 and 0.4–1.2 °C on aifoundry2, both out of sample. The error that remains is mostly the
plateau moving 0.3–0.8 °C with nothing changed (E97 result 4), and on aifoundry2 the whole-degree rest reading. **E144 is the blind
test:** these numbers are desk estimates on data the lab already had.

## Results first

**1. aifoundry3 card 0, 600 MHz.** The chain was fitted by NNLS on a τ grid of 1–1000 s, with each session's rest die as a free
intercept. Training data: E89's two passes and E97's whole session, Part A then Part B (4.2 h, 10 Hz, the 34 raw codes). NNLS kept
five stages ([`model-q138t.json`](model-q138t.json) `a3`):

| τ (s) | 1 | 3 | 10 | 60 | 120 | total |
|---|---|---|---|---|---|---|
| R (°C per board W) | 0.0866 | 0.0322 | 0.0520 | 0.1634 | 0.5353 | **0.8695** |

The open loop reaches 13% of the plateau at 2 s, 40% at 30 s, 56% at 60 s, 75% at 2 min, 95% at 5 min and 99.6% at 10 min. Its t63 is
79 s and its t90 224 s. E97's H1 measured 45% at 60 s and 90% at 5 min (E97-B6). That share is the closed loop's: the leakage climb
lengthens the approach, and the chain reproduces it (H1's measured t63 is 119 s, the closed loop's 119 s; [`selftest-score.txt`](selftest-score.txt)).
No stage slower than 120 s was selected. A stage slower than about 10 minutes that adds under about 3% is not resolved (E97's own
caveat), and the plateau's moves of up to 0.8 °C sit inside the errors above.

**2. aifoundry2 card 0, governed.** The same fit on E111's and E133's sessions (E98's probe series, its hold of 39, H-F32 and H-I8;
the firmware's whole-degree reading) gives `a2`:

| τ (s) | 1 | 3 | 10 | 60 | 120 | total |
|---|---|---|---|---|---|---|
| R (°C per board W) | 0.0736 | 0.0660 | 0.0389 | 0.3429 | 0.1416 | **0.663** |

That is t63 50 s and t90 153 s: 68% at 60 s, 85% at 2 min and 98% at 5 min. It is faster than aifoundry3, as E111 found post hoc (60% at
76 s, everything by 5–6 minutes). Each day's fit reads the other day: fitted on E111 the total is 0.670, fitted on E133 0.658. The
coefficient does not drift between those sessions. The errors do, and the anchor's whole degree is most of them.

**3. The short run, tied to the long one.** The aifoundry3 chain gives **0.114 °C per board W 2 s after a step**. E97's direct 2 s rises
are 0.121–0.135 °C per W of S, and E89's chain gives 0.110. At 4.5 s it gives 0.161. M6's 0.118 °C per board W is read over E78's 4 s
window after a heater to 59 °C, which is not a step from rest, so the two are reported side by side and not reconciled.

**4. The full chain (arm b).** On aifoundry3, the switching power is E78's S for the kind × the planned launch pattern, plus E97's
pooled idle law (`P = 0.006175 T² − 0.36659 T + 25.999`, fitted on rests from 50.5 to 64.8 °C), closed through the chain. The loop
gain works out to 0.28 at 55 °C, 0.35 at 62 °C and 0.39 at 66 °C, which E97 derived as 0.36–0.44 at 62–70 °C. On aifoundry2, the
planned board trace is the mean of E111's and E133's same-kind holds, and for fp32 the governor's trip comes from E133: a die whose
floor plateau would read under 66 is pinned at 65.9 °C.

## E144's holds (the design this freezes)

**aifoundry3 card 0** (E97's Part B harness, `run_e97b.py`: back-to-back launches on 1,024 minions, 600 MHz pinned, nothing set). One
session of **75.9 card-minutes**, inside 80:

| step | min | kind (E78's S, W) | launch pattern | S × share (W) | (b) rise at 60 s / 2 min / 5 min / 10 min (°C) | (b) plateau rise, last 300 s (°C) | per board W | (c) fixed point (°C), t63 / t90 closed (s) | absolute at a 50.6 °C rest: plateau, peak (°C) |
|---|---|---|---|---|---|---|---|---|---|
| R0 | 10 | rest (E97's slope rule, cap 10) | — | — | — | — | — | — | — |
| **H_L** | 13 | int8 −1s (4.176) | E97's natural chain (share 0.966) | 4.03 | 2.18 / 3.07 / 4.21 / 4.61 | **4.61** | 0.861 | **4.67**, 110 / 298 | 55.2, 55.3 |
| R1 | 9 | rest | — | — | cool-down 2.44 at 60 s, 0.42 at 5 min | — | — | — | — |
| **H_M** | 13 | int8 full (9.648), **E97's H1 again** | natural chain | 9.32 | 5.01 / 7.11 / 9.93 / 11.02 | **11.02** | 0.851 | **11.34**, 119 / 323 | 61.7, 61.9 |
| R2 | 9 | rest | — | — | cool-down 5.89 at 60 s, 0.92 at 5 min | — | — | — | — |
| **H_H** | 13 | fp32 random (26.701) | 3.2 s of compute every 7.0 s (share 0.457) | 12.21 | 6.63 / 9.35 / 13.14 / 14.70 | **14.71** | 0.844 | **15.31**, 125 / 339 | 65.6, **67.5** |
| R3 | 9 | rest | — | — | cool-down 7.79 at 60 s, 1.11 at 5 min | — | — | — | — |

- **The registered subset** (if the gates leave under 80 card-minutes; at most 45): R0 for 8 min, then H_H for 13, R1 for 9, H_L for 13
  and R2 for 2, which is 44.9 minutes. Its own predictions are frozen in `aifoundry3.subset`: H_H 15.01 °C, and H_L 4.21 °C over a rest
  that still carries H_H's tail.
- **H_H in a warm room:** at 3.2 s per 7.0 s if the rest die before it is at most 51.5 °C (34-sensor mean, last 120 s); at 2.6 s
  (share 0.371) between 51.5 and 53.0 °C, predicted 12.3–12.5 °C; not run above 53.0 °C (`aifoundry3.H_H_warm_room`). Every plateau's
  dependence on the rest die is frozen in `plateau_rise_C_by_rest_die`, at 49.5, 50.6, 51.5 and 52.5 °C.
- **Why these kinds:** three distinct powers (S × share 4.0, 9.3 and 12.2 W), all measured before in E78. int8 full is E97's H1 again,
  so this card's plateau gets a second session (item 8 on aifoundry3). fp32 random is the best-measured S (±0.05 W) and was held
  before (E97's H3). Duty-cycled at 7 s, it also tests the fast stages, which set the short-run rule. Full-duty fp32 random has no
  plateau under this card's stop (E97: 78 °C in 221 s), so it is held only duty-cycled.

**aifoundry2 card 0** (E133's harness, `run_e133.py`: its own governor, 65 W / 65 °C, nothing set; E98's rest rule before each step).
**38 card-minutes**, inside 40: G1 = REST (2 min) + H-I8 (15 min), END (2), then G2 = REST (2) + H-F32 (15), END2 (2).

| hold | kind, clock | (b) rise at 60 s / 2 min / 5 min / 10 min (°C) | (b) plateau rise (°C), at board rise (W) | (c) t63 / t90 (s) | absolute at a 44.0 °C rest |
|---|---|---|---|---|---|
| **G1** | int8 −1s, 800 MHz (never trips: E111/E133 plateaus 56.4–59.0 °C) | 6.63 / 8.95 / 11.46 / 12.02 | **11.83**, 17.84 | 50 / 153 (open) | 55.8 °C |
| **G2** | fp32 random, governed | — | at the floor: **21.49** (0.663 × E111's 32.42 W). **Plateau = max(rest + 21.49, 65.9 °C)** | — | **65.9 °C, at the trip.** The regime changes at a rest die of 44.41 °C |

The trip rule checks out on the two earlier sessions. E111 rested at 45.5 °C, which puts the floor at 67.0 °C, and it measured
67.26 °C at the floor. E133 rested at 44.0 °C, which puts the floor at 65.5 °C, under the trip, so the rule says 65.9 °C at the trip,
and it measured 65.91 °C at the trip.

## Frozen rules (`predictions-e144.json` › `rules`)

| arm | aifoundry3 | aifoundry2 |
|---|---|---|
| **(a) the heat model alone**: the chain on the session's measured board trace, run from its first rest and anchored on the measured die over the last 120 s of the rest before each hold | PASS: rms over the hold ≤ 0.80 °C and \|plateau error\| ≤ 1.00 °C. FAIL: rms > 1.60 or \|plateau error\| > 2.00. Otherwise INCONCLUSIVE. Cool-down rms over 540 s reported, ≤ 0.60 °C read as PASS | PASS: rms ≤ 1.20 °C and \|plateau error\| ≤ 1.30. FAIL: > 2.20 or > 2.40 |
| **(b) the full chain**: the planned power only | PASS: every checkpoint from 60 s to the end within ±1.30 °C of `rise_C_by_s`, and the plateau rise within ±1.30. FAIL: the plateau outside ±2.60 | G1: ±1.30 PASS, ±2.40 FAIL. G2: plateau within ±0.60 °C of the trip rule, in the predicted regime: PASS. Outside ±1.20, or in the other regime with the rest die more than 0.5 °C from its edge: FAIL |
| **(c) plateaus and time constants** | rise per board W over the last 300 s: PASS in [0.80, 0.94], FAIL wholly outside [0.74, 1.00]. Linearity (H_H/H_L, H_M/H_L per board W): PASS in [0.92, 1.08], FAIL outside [0.85, 1.15]. t63 from rest over the closed loop's: PASS in 0.75–1.33×, FAIL outside 0.5–2×. **The replicate:** H_M's rise per board W at 600 s over E97's H1 at 600 s (0.898): PASS in [0.94, 1.06], FAIL outside [0.88, 1.12]. The chain predicts 0.849, a ratio of 0.946 | G1 per board W: PASS in [0.62, 0.74]. t63: PASS in 0.75–1.33× of 50 s |

The bands are the desk's out-of-sample errors widened by about 1.2–1.6×, and their floors are the plateau moves E97 and E111 saw (up to
0.8 and 1 °C). [`score_e144.py`](score_e144.py) applies the (a) and (c) rules and (b)'s plateau rule mechanically, using `fit_q138t.score_hold`. Its
self-test on E97 and E133 checks the scorer, not the model, because the chain trained on that data.

**Stops** (`rules.stops`):
- aifoundry3: no launch starts at a firmware reading ≥ 70 °C (E140's die stop). A hold ends at any sample ≥ 72 °C or board ≥ 65 W
  (E140's board guard), and the session ends at ≥ 74 °C.
- Every planned peak sits at least 2 °C under 70 at a 50.6 °C rest. H_H's in-launch peak is 67.5 °C on the 34-sensor mean, which the
  firmware reads about 1 °C lower; the warm-room rule above keeps that margin.
- aifoundry2: the governor's own settings, never set. A hold ends at a reading ≥ 72 °C or ≥ 93 W on 3 samples (E133's 80 °C / 93 W,
  with the die tightened). E133's sessions never reached either.
- Nothing here approaches a PMIC over-power or over-temperature limit: the owner's rules of 2 Nov 2026.

## What this cannot say

- **One training session per card for the long holds.** E97 is aifoundry3's only long-hold session. The leave-one-hold-out scores share
  its room, so a session-out error on aifoundry3 is unmeasured, and E144 gives the first.
- **The plateau moved 0.3–0.8 °C** in E97 and about 1 °C in E111/E133 with nothing changed. The model has no term for that, so it
  sets the floor of every band.
- **The aifoundry2 anchor is a whole degree:** a rest that reads one integer throughout leaves ±0.5 °C. A W-derived rest die (E98's
  proxy) was not used here.
- **The leakage law** is fitted to 64.8 °C and carried by its quadratic to H_H's 65–68 °C.
- **(b) on aifoundry3 reads low on E97's own holds** (−0.3 to −1.0 °C, in sample). The chain's total, 0.870, is a compromise between
  E89's session (0.80 on its means) and E97's (0.88–0.92). It was frozen as fitted, not tuned to E97's plateaus.
- **No inlet thermometer:** the rest die is the room's proxy, as in items 8 and 9.

## Device commands sent

None: this lane opened no device and ran nothing on any box. E144 lists and classifies its own before its first launch, with
`tools/claims-v3/dmcmd_audit.py`. The harnesses named above sent only READs in their sessions: E97 sent `ettelem config`, `sample`
without `--reset-ms`, and aifoundry3's command 74 group 0, whose class E144 must state against the non-public thermal build. E133's
table is in its README.

## Departures

- **D1, time:** about 90 minutes at the desk against the brief's 60.
- **D2, the high hold:** the brief's example "random fp32" is held only duty-cycled (share 0.457), because full duty reaches this card's
  stop with no plateau (E97-B10).
- **D3, the aifoundry2 full chain:** the planned power is the earlier holds' mean board trace, not a switching table plus a law. No
  800 MHz S table exists for aifoundry2, and E111 found the int8 hold's board W rising about 1.07 W per °C, not E64's 0.442.

## How to reproduce

```bash
python3 docs/reports/data/2026-11-02-q138t-heat-model/fit_q138t.py > docs/reports/data/2026-11-02-q138t-heat-model/fit.txt          # ~70 s
python3 docs/reports/data/2026-11-02-q138t-heat-model/predict_e144.py > docs/reports/data/2026-11-02-q138t-heat-model/predictions-e144.txt
python3 docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py --self-test > docs/reports/data/2026-11-02-q138t-heat-model/selftest-score.txt
# E144: score_e144.py a3 <E144 pass dir> ; score_e144.py a2 <G1 step dir> <G2 step dir>
```

numpy 1.26.4, Python 3.9 (the desk's system Python).

## Files

| file | what |
|---|---|
| `heat_q138t.py` | the model: loaders, the chain, NNLS, the anchor, the laws, the closed loop with the governor's trip, plateau and t63 helpers |
| `fit_q138t.py`, `fit.txt` | the fits, the before arms, leave-one-hold-out (aifoundry3) and session-out (aifoundry2) |
| `model-q138t.json` | **frozen**: both chains (`R_full_grid` on `tau_grid_s`), fit rms, P_ref, aifoundry2's switching power per hold |
| `cv-q138t.json` | every out-of-sample row above |
| `predict_e144.py`, `predictions-e144.json`, `predictions-e144.txt` | **frozen**: E144's design, arms (b) and (c), the rules and stops |
| `score_e144.py`, `selftest-score.txt` | the scorer and its self-test (in sample: it checks the code) |
