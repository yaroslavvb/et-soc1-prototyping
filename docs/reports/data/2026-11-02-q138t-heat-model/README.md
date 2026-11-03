# Q138(t): the die's step response over minutes, frozen for E144 (desk, Mon 2 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 9, "A steady state for heat", and item 8, "The heat path drifts between sessions". It answers the page's "After Q137, the next
steps" (2): "a long hold scored against M6's frozen step response". Desk only: no card, no device command, nothing set. Everything here
comes from committed raw telemetry (E89, E97, E111, E133) and E78's switching powers. E144 is scored against these files as they are
committed **with amendment A1** (below, committed after the verifier's report and before E144's claim), and must check that the A1
commit is on origin before its claim.*

## Corrections after verification, and amendment A1 (Mon 2 Nov 2026, about 20:30 PST, before E144's claim)

The verifier re-ran every script byte for byte and re-derived both chains and every E144 number with its own code; they hold. What it
found wrong was the "before" the gain was measured against, the out-of-sample framing, H_H's share in E144's design, and the scorer.
**C1–C9 correct the desk text in place** (the text at `f5473428` is in git). **Amendment A1 changes no frozen number, band or stop** in
`predictions-e144.json` or `model-q138t.json`: it adds what they lacked, in [`amendment-a1.json`](amendment-a1.json) (written by
[`amend_a1.py`](amend_a1.py); its printout is [`amendment-a1.txt`](amendment-a1.txt)), and [`score_e144.py`](score_e144.py) now applies
every frozen rule.

**Corrections (the desk's text)**
- **C1 (major): the "before" misstated M6.** M6 froze a four-pole step response (Q137(m) `m6.json` `heat.step_response`: τ 1.005, 15.98,
  138.2 and 1500 s, weights 0.148, 0.010, 0.832 and 0.010) and a long-hold rule c × S × F(t), with c 0.9 °C per board W on aifoundry3
  and 0.675 on aifoundry2 (`predict_blind4.py`). The "1.5–11.6 °C" arm was an instantaneous 0.9 × ΔP rule that M6 never made. It is now
  labelled a plateau coefficient misused as a trajectory, and "M6 had only a plateau coefficient" is withdrawn. Against M6 as frozen
  (the table below, `amendment-a1.json` `A1_7_before_after`):
  - given the board's watts, the two are about even on E97's holds (mean rms 0.62 → 0.59 °C), and the chain's cool-downs are better;
  - from the planned power, M6 reads E97's plateaus 29–33% low (3.5–6.4 °C) and the closed chain 0.45–1.09 °C low, both in sample.
    The gain is the leakage loop, which M6 does not have.

  The section-11 quote above now reads "M6's frozen step response", as the kinds page has it.
- **C2 (major): "out of sample, 0.47–0.66 °C" was within one session.** It is leave-one-hold-out inside E97's session, and H1's fit keeps
  H2, which starts from H1's plateau. `fit.txt` already held two stricter designs, now quoted beside it. Every Part B hold left out gives
  0.36/0.50/1.33 °C rms (H3's plateau −1.36 °C). Session-out from E89's square waves alone (31 Oct, scored on E97 of 1 Nov) gives
  0.46/0.65/1.50 °C (H3's plateau −1.59 °C). By E144's own (a) band, both H3 scores read INCONCLUSIVE. Like for like (session-out against
  E89's own session-out chain, 0.78/0.73/0.72 °C), the new grid is better on H1 and H2 and worse on H3, the fp32 random hold.
  "A session-out error on aifoundry3 is unmeasured" is withdrawn.
- **C3: aifoundry2, per hold.** The gain over the one-pole model is uneven: 4 of 6 holds better, both of E111 W2's worse (1.16 and 1.06
  against 0.91 and 0.96 °C). The mean over six holds goes 0.99 → 0.79 °C, and M6's F(t) × 0.675 used as a chain reads 0.47–1.28 °C
  (mean 1.01). The "1.9–5.1 °C" arm is the same misused coefficient as C1's.
- **C4: R and the stages.** R has a design spread: on aifoundry3 0.866–0.958 °C per board W across the fit designs (leave one hold out
  0.866–0.898, every Part B hold out 0.944, E89 alone 0.958; frozen 0.8695), and on aifoundry2 0.658–0.670 (frozen 0.663). The stage split
  is not unique. A 19-point τ grid keeps 1, 5, 7, 90 and 120 s on aifoundry3, with R 0.867, t63 79.5 s and t90 215 s, and 1, 5, 7, 60 and
  90 s on aifoundry2 (R 0.663, t63 50.5 s). Read "a few stages between about 1 s and 2 min": R, t63 and the scores are stable, the stages are not.
- **C5: the short-run tie reconciles.** M6's 0.118 °C per board W is a reading over a 4.5 s run, and the chain's 0.161 is its value at
  the run's end. Read like for like, the chain's mean over a 4.5 s run is 0.109, and M6's own 0.9 × F(4.5 s) is 0.158. The gap is mostly a
  window mean against an end value (`A1_9_short_run`).
- **C6: G2's back-check used the wrong rest die.** 45.5 °C was E111's before/after mean idle. The rest die before its hold reads 45.0 °C,
  as the anchor and the scorer read it. With 45.0 the rule says 66.49 °C against 67.20 °C measured (last 300 s), +0.71 °C: INCONCLUSIVE by
  G2's own band. E133's trip case reads 65.82 against 65.90 °C, PASS. In the trip regime G2 tests the governor, not the chain (A1.3).
- **C7: the scorer.** As committed at `f5473428` it applied (a), (c)'s per-board-W and t63 bands, and (b)'s plateau band only. It had no
  aifoundry2 (b) or (c), no (b) checkpoints, no linearity, replicate or H_H', and its docstring's argument order contradicted its code. It
  is completed: every frozen rule, (b) as A1.2 reads it, and M6 beside every arm. Its self-test adds synthetic E144 sessions made by the
  frozen model, where every arm reads PASS and (b) gives back the frozen numbers within 0.0005 °C ([`selftest-score.txt`](selftest-score.txt)).
- **C8: two stale strings in the frozen rules** (left as frozen in the JSON, corrected in `A1_4_corrected_strings`):
  - (b)'s "why" said E97's holds "back-checked to −0.3 to +0.6 °C". The frozen back-check has the chain 0.33–1.04 °C under.
  - G1's "0.648–0.700 in four holds" are E133's registered coefficients. By the scorer's metric the earlier int8 holds read 0.710–0.747
    (last 300 s), or 0.685–0.689 over 600–900 s. The band [0.62, 0.74] stands, and its top sits inside that spread.
- **C9: aifoundry2's stop rationale.** "The PMIC alarm's 75 W is the SP's slow average, which the 65 W governor holds" was never verified
  on aifoundry2, because E117 did not run. Now it gives the record only. G2 repeats exactly the hold E111 and E133 ran: the same kind,
  harness and governor settings, nothing set. Those holds peaked at 88.04 and 88.65 W (65 and 322 samples over 85 W, none over 90 W) with no
  alarm. aifoundry2's PMIC over-power alarm configuration is unknown. The stops are unchanged.

**Amendment A1, for E144 (written before any E144 data)**
- **A1.1: H_H's launch pattern.** `sparsity_host` runs whole dispatches of 0.491 s, plus a 0.019 s calibration dispatch, while the time
  spent is under `--seconds`. So "3.2 s of compute per 7.0 s" cannot be recorded: at a 7.0 s period the choices are 2.97, 3.46 or 3.95 s
  (shares 0.424, 0.494 and 0.564). A1 keeps the frozen share instead of the period.
  - **H_H** runs duty-cycled from its first launch (`run_e97b.py` enters that phase only after a 78 °C stop, so E144's runner must start
    it there): `--seconds 3.20` (7 dispatches, 3.456 s recorded), one launch every **7.56 s**. That records **0.4571**, the frozen share.
    The frozen chain then gives a plateau rise of 14.708 °C (frozen 14.71) and a peak of 67.59 °C (frozen 67.54), so every frozen H_H
    number and stop margin stands.
  - **H_H'** (warm room) runs `--seconds 2.60` (6 dispatches, 2.965 s), one launch every **7.98 s**, recording 0.3716 (frozen 0.3714).
  - Had the period stayed at 7.0 s, the share would read 0.494, the plateau 16.06 °C (+1.35, past the ±1.30 band) and the peak 68.84 °C
    (`A1_1_launch_pattern.options_at_50.6C`).
- **A1.2: (b) at the realized pattern.** Arm (b) is scored against the frozen chain, closed through E97's law, run on the session's
  realized launch pattern: every dispatch record in `runs.jsonl` is on at its item's E78 S, from the measured rest die at R0's end. The
  frozen bands apply unchanged. The `f5473428` plan numbers are reported beside the verdict. The two agree when the run matches the plan
  (self-test: within 0.0005 °C), and the same reading scores H_H' and the subset.
- **A1.3: definitions.**
  - **The rest die**: aifoundry3, the 34-sensor mean over the last 120 s of the rest before the hold; aifoundry2, the firmware's
    whole-degree reading over the last 120 s of REST.
  - **G2's regime**: "floor" when at least 98% of the hold's last 300 s of samples read 600 MHz, else "trip" (E111 read 1.000, E133 0.887).
- **A1.6: M6 as frozen, the comparison arm**, computed mechanically from `m6.json` (`m6_comparison_arm`), with no verdict of its own.
  The scorer reports it beside each arm.
  - aifoundry3 (b): H_L 3.57, H_M 8.14 and H_H 10.56 °C, read as the frozen holds are read, carrying the earlier holds' tails. From a
    rested die, the verifier's figures are 3.57, 8.24 and 10.80 °C. The chain's are 4.61, 11.02 and 14.71 °C.
  - G1: 11.93 °C (the chain 11.83 °C).
  - G2: M6 has no governor term, so it gives the floor's rise only, rest + 21.88 °C.
- **A1.8: G1's t63 reference.** The frozen G1 t63 rule reads the die's t63 against the OPEN loop's 49.6 s. On aifoundry2 the board's watts
  climb with the die, so a die from rest is slower: the frozen model's own G1 reads 76.0 s (1.53×), and E133's and E111's int8 holds
  1.50× and 1.79×. So that rule is expected to read NOT PASS even when the model is right. It is kept and reported. Beside it, A1 adds the
  same band against the model's own 76.0 s (E133 0.98×, E111 1.17×, both inside).
- **What E144 must do:**
  - use these files at the A1 commit and check that the commit is on origin before the claim;
  - run H_H (or H_H') duty-cycled from its first launch as A1.1 says;
  - keep `run_e97b.py`'s `marks.jsonl` and `runs.jsonl` formats;
  - score with `score_e144.py a3 [<earlier dirs>] <pass dir>` and `score_e144.py a2 <G1 step> <G2 step>`.

## What this changes for predicting heat

*Rewritten by C1–C3 (the table at `f5473428` compared against a rule M6 never made).*

| What is predicted | Before | After (this frozen chain) | Source |
|---|---|---|---|
| **aifoundry3: the die through a 15–30 min hold, given its board trace** (arm a) | **M6 as frozen** (0.9 × its four-pole F(t)), in sample, since E97 set F: rms **0.64 / 0.31 / 0.91 °C** on E97's H1/H2/H3, plateau +0.04 / +0.44 / −0.14, cool-downs 0.63–1.07 °C. **E89's frozen chain** (session-out): 0.78 / 0.73 / 0.72 °C | Three designs. **Within the session** (leave one hold out): **0.66 / 0.64 / 0.47 °C**, plateau +0.40 / +0.82 / −0.40, cool-downs 0.12–0.33. **Every Part B hold out**: 0.36 / 0.50 / 1.33 (H3's plateau −1.36). **Session-out from E89's square waves**: 0.46 / 0.65 / 1.50 (H3's plateau −1.59) | [`fit.txt`](fit.txt), [`cv-q138t.json`](cv-q138t.json) `a3`; M6: `amendment-a1.json` `A1_7_before_after.aifoundry3` |
| **aifoundry3: a plateau from the planned power only** (arm b: E78's S × the launch pattern) | **M6 as frozen** (0.9 × S × F(t), no leakage loop): E97's plateaus **3.48 / 4.31 / 6.43 °C low** (29–33%) | The chain closed through the idle law: **0.51 / 1.09 / 0.45 °C low** at E97's realized pattern (0.47 / 1.04 / 0.33 as fixed points). Both arms in sample: E97 trained the chain and set M6's F | `A1_7_before_after.aifoundry3.b_on_E97_at_its_realized_pattern_in_sample`; `predictions-e144.json` `aifoundry3.backcheck_on_E97` |
| **aifoundry2: the die through a hold, governed, given its board trace** | **One pole** of 89 s: 0.91–1.21 °C (mean 0.99 over six holds). **M6's F(t) × 0.675** as a chain: 0.47–1.28 °C (mean 1.01) | Fitted on one day, scored on the other: **0.44 / 0.57 / 0.64 °C** (E111 → E133) and **1.16 / 1.06 / 0.87** (E133 → E111), mean **0.79**. Better on 4 of 6 holds, worse on E111 W2's two | `cv-q138t.json` `a2`; `A1_7_before_after.aifoundry2` |

*Not a before:* a plateau coefficient misused as an instantaneous trajectory (0.9 or 0.673 °C × ΔP) misses by 1.5–11.6 °C on aifoundry3
and 1.9–5.1 °C on aifoundry2 (`fit.txt`). No model made that rule, M6 included.

**So:** the term this lane measures and freezes is the time-resolved heat path, a chain per card from board watts to the die, closed
through the idle leakage law. Given the board's watts, it does about as well as M6's frozen step response on aifoundry3's long holds,
with better cool-downs:
- 0.5–0.7 °C rms within E97's session;
- 0.5–1.5 °C when trained on E89's square waves alone, the fp32 random hold the worst.

Its real gain is from the planned power. M6 reads E97's plateaus about 30% low because it has no leakage loop, and the closed chain reads
them 0.3–1.1 °C low, in sample. On aifoundry2 the mean error falls from 0.99 to 0.79 °C, unevenly. The error that remains is mostly the
plateau moving 0.3–0.8 °C with nothing changed (E97 result 4), and on aifoundry2 the whole-degree rest reading. **E144 is the blind test
of both models**, scored side by side under A1.

## Results first

**1. aifoundry3 card 0, 600 MHz.** The chain was fitted by NNLS on a τ grid of 1–1000 s, with each session's rest die as a free
intercept. Training data: E89's two passes and E97's whole session, Part A then Part B (4.2 h, 10 Hz, the 34 raw codes). NNLS kept
five stages on this grid ([`model-q138t.json`](model-q138t.json) `a3`). The split is not unique: a 19-point grid keeps other stages with
the same R and t63 (C4).

| τ (s) | 1 | 3 | 10 | 60 | 120 | total |
|---|---|---|---|---|---|---|
| R (°C per board W) | 0.0866 | 0.0322 | 0.0520 | 0.1634 | 0.5353 | **0.8695** |

Across the fit designs, R runs 0.866–0.958 (C4). The open loop reaches 13% of the plateau at 2 s, 40% at 30 s, 56% at 60 s, 75% at 2 min, 95% at 5 min and 99.6% at 10 min. Its t63 is
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
are 0.121–0.135 °C per W of S, and E89's chain gives 0.110. At 4.5 s it gives 0.161. M6's 0.118 °C per board W is a reading over the
kinds harness's 4.5 s run, and 0.161 is the chain's value at the run's end. Read like for like, the chain's mean over a 4.5 s run is
0.109, and M6's own 0.9 × F(4.5 s) is 0.158 (C5).

**4. The full chain (arm b).** On aifoundry3, the switching power is E78's S for the kind × the planned launch pattern, plus E97's
pooled idle law (`P = 0.006175 T² − 0.36659 T + 25.999`, fitted on rests from 50.5 to 64.8 °C), closed through the chain. The loop
gain works out to 0.28 at 55 °C, 0.35 at 62 °C and 0.39 at 66 °C, which E97 derived as 0.36–0.44 at 62–70 °C. On aifoundry2, the
planned board trace is the mean of E111's and E133's same-kind holds, and for fp32 the governor's trip comes from E133: a die whose
floor plateau would read under 66 is pinned at 65.9 °C.

## E144's holds (the design this freezes)

*Amended by A1.1, before E144's claim. H_H runs `--seconds 3.20` (7 dispatches, 3.456 s recorded) once every 7.56 s, duty-cycled from its
first launch, which records the frozen share of 0.457. H_H' runs `--seconds 2.60` once every 7.98 s (0.372). The numbers below stand at
those settings. "3.2 s of compute every 7.0 s" cannot be recorded with whole dispatches.*

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

The trip rule on the two earlier sessions, with the rest die read as the anchor and the scorer read it (corrected by C6; it said E111
rested at 45.5 °C, its before/after mean idle):
- E111 rested at 45.0 °C, which puts the floor at 66.49 °C. It measured 67.20 °C at the floor over the last 300 s, +0.71 °C:
  INCONCLUSIVE by G2's band.
- E133 rested at 44.0 °C, which puts the floor at 65.5 °C, under the trip, so the rule says 65.9 °C. It measured 65.82 °C at the trip:
  PASS.

In the trip regime, G2 tests the governor's hold, not the chain.

## Frozen rules (`predictions-e144.json` › `rules`)

*A1, before E144's claim, changes no band. A1.2 scores (b) on the realized launch pattern from the measured rest die. A1.3 defines the
rest die and G2's regime. A1.8 adds a closed-loop reference beside G1's t63. C8 corrects two "why" strings.*

| arm | aifoundry3 | aifoundry2 |
|---|---|---|
| **(a) the heat model alone**: the chain on the session's measured board trace, run from its first rest and anchored on the measured die over the last 120 s of the rest before each hold | PASS: rms over the hold ≤ 0.80 °C and \|plateau error\| ≤ 1.00 °C. FAIL: rms > 1.60 or \|plateau error\| > 2.00. Otherwise INCONCLUSIVE. Cool-down rms over 540 s reported, ≤ 0.60 °C read as PASS | PASS: rms ≤ 1.20 °C and \|plateau error\| ≤ 1.30. FAIL: > 2.20 or > 2.40 |
| **(b) the full chain**: the planned power only | PASS: every checkpoint from 60 s to the end within ±1.30 °C of `rise_C_by_s`, and the plateau rise within ±1.30. FAIL: the plateau outside ±2.60 | G1: ±1.30 PASS, ±2.40 FAIL. G2: plateau within ±0.60 °C of the trip rule, in the predicted regime: PASS. Outside ±1.20, or in the other regime with the rest die more than 0.5 °C from its edge: FAIL |
| **(c) plateaus and time constants** | rise per board W over the last 300 s: PASS in [0.80, 0.94], FAIL wholly outside [0.74, 1.00]. Linearity (H_H/H_L, H_M/H_L per board W): PASS in [0.92, 1.08], FAIL outside [0.85, 1.15]. t63 from rest over the closed loop's: PASS in 0.75–1.33×, FAIL outside 0.5–2×. **The replicate:** H_M's rise per board W at 600 s over E97's H1 at 600 s (0.898): PASS in [0.94, 1.06], FAIL outside [0.88, 1.12]. The chain predicts 0.849, a ratio of 0.946 | G1 per board W: PASS in [0.62, 0.74]. t63: PASS in 0.75–1.33× of 50 s |

The bands are the desk's out-of-sample errors widened by about 1.2–1.6×, and their floors are the plateau moves E97 and E111 saw (up to
0.8 and 1 °C). [`score_e144.py`](score_e144.py) applies every rule above mechanically, with (b) as A1.2 reads it and M6 as frozen beside
each arm. As committed at `f5473428` it applied only (a), (c)'s per-board-W and t63 bands, and (b)'s plateau band (C7). Its self-test runs
two parts:
- E97, E111 and E133, which checks the scorer, not the model, because the chain trained on that data;
- synthetic E144 sessions made by the frozen model, where every arm reads PASS. The one exception is G1's frozen t63 reading, for A1.8's
  reason.

The bands' expectations on the stricter designs: (a) on an fp32 random hold reads INCONCLUSIVE if the session-out error repeats (C2). The
replicate's own prediction, 0.946, sits at its PASS edge (0.94).

**Stops** (`rules.stops`):
- aifoundry3: no launch starts at a firmware reading ≥ 70 °C (E140's die stop). A hold ends at any sample ≥ 72 °C or board ≥ 65 W
  (E140's board guard), and the session ends at ≥ 74 °C.
- Every planned peak sits at least 2 °C under 70 at a 50.6 °C rest. H_H's in-launch peak is 67.5 °C on the 34-sensor mean, which the
  firmware reads about 1 °C lower; the warm-room rule above keeps that margin.
- aifoundry2: the governor's own settings, never set. A hold ends at a reading ≥ 72 °C or ≥ 93 W on 3 samples (E133's 80 °C / 93 W,
  with the die tightened). E133's sessions never reached either.
- The owner's rules of 2 Nov 2026 forbid anything that risks a power cycle. On aifoundry3 every hold stays inside the stops above. On
  aifoundry2 the record is all there is (C9). G2 repeats exactly the hold E111 and E133 ran, which peaked at 88.04 and 88.65 W, none over
  90 W, with no alarm. aifoundry2's PMIC over-power alarm configuration is unknown, because E117 did not run.

## What this cannot say

- **One long-hold session per card.** E97 is aifoundry3's only long-hold session, and its leave-one-hold-out scores share its room.
  Trained on E89's square waves alone (31 Oct), the chain scores E97 (1 Nov) at 0.46–1.50 °C rms, with H3's plateau 1.59 °C low (C2).
  E144 gives the first session-out score on long holds.
- **The plateau moved 0.3–0.8 °C** in E97 and about 1 °C in E111/E133 with nothing changed. The model has no term for that, so it
  sets the floor of every band.
- **The aifoundry2 anchor is a whole degree:** a rest that reads one integer throughout leaves ±0.5 °C. A W-derived rest die (E98's
  proxy) was not used here.
- **The leakage law** is fitted to 64.8 °C and carried by its quadratic to H_H's 65–68 °C.
- **(b) on aifoundry3 reads low on E97's own holds** (−0.3 to −1.0 °C, in sample). The chain's total, 0.870, is a compromise between
  E89's session (0.80 on its means) and E97's (0.88–0.92). It was frozen as fitted, not tuned to E97's plateaus. Across the fit designs
  it runs 0.866–0.958, with no interval beyond that spread (C4).
- **M6 is a fair comparison only on arm (b).** On arm (a), M6's F(t) was fitted to E97's own step fractions, so its 0.31–0.91 °C is in
  sample. Both models are blind on E144.
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
- **D4, after verification (Mon 2 Nov 2026, about 20:30 PST, before E144's claim):** corrections C1–C9 and amendment A1. A1.8 was found by
  the completed scorer's self-test. Every number in A1 comes from committed data that existed before the freeze; none comes from E144.

## How to reproduce

```bash
python3 docs/reports/data/2026-11-02-q138t-heat-model/fit_q138t.py > docs/reports/data/2026-11-02-q138t-heat-model/fit.txt          # ~70 s
python3 docs/reports/data/2026-11-02-q138t-heat-model/predict_e144.py > docs/reports/data/2026-11-02-q138t-heat-model/predictions-e144.txt
python3 docs/reports/data/2026-11-02-q138t-heat-model/amend_a1.py > docs/reports/data/2026-11-02-q138t-heat-model/amendment-a1.txt      # A1, ~95 s
python3 docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py --self-test > docs/reports/data/2026-11-02-q138t-heat-model/selftest-score.txt   # ~40 s
# E144: score_e144.py a3 [<earlier dirs of the session>] <E144 pass dir> ; score_e144.py a2 <G1 step dir> <G2 step dir> [--map <step>/<hold>=G1]
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
| `score_e144.py`, `selftest-score.txt` | the scorer, completed by A1 (C7): every frozen rule, (b) at the realized pattern, M6 beside each arm; its self-test (E97/E111/E133 in sample, plus synthetic E144 sessions from the frozen model) |
| `amend_a1.py`, `amendment-a1.json`, `amendment-a1.txt` | **amendment A1** (before E144's claim): H_H's and H_H''s launch settings and their predictions, (b)'s scoring, the rest die and G2's regime, the corrected strings, aifoundry2's peaks, M6's E144 predictions, the before/after restated, G1's closed t63 reference, the short-run tie |
