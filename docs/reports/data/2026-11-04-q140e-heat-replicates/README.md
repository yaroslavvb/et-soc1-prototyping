# Q140(e): the heat replicates' frozen predictions - one duty convention, aifoundry2's in-work level from M9, the critic's rank-3 rules, and a 25-minute hold to look for a slow stage (desk, Wed 4 Nov 2026)

*It answers Q139's final critic, **rank 3**, "Heat over minutes from the bits, a second session per card", and the kinds page's
[section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 9** (a steady
state for heat), **item 8** (the heat path between sessions) and **item 6** (the power model). It is the desk half of Q140's planned
**E166** (aifoundry3) and **E167** (aifoundry2), which need the owner's word and do not run tonight. The owner's mandate: his words of
2 November 2026 ("settle any unanswered questions regarding horace's power model"), with his goal "to be able to predict the power
requirement and heat generation of various kinds of numeric computations as accurately as possible".*

*Desk only, Wed 4 Nov 2026, about 02:10-03:00 PST, on the Intel: no card, no device command, no ssh to a lab box, no Discord, no Modal, no
archive. **Registered first:** [`REGISTRATION.md`](REGISTRATION.md) and [`registration.json`](registration.json), commit **`11174d20`**
(02:23:53 PST), before any prediction, fit or score of this lane was computed. The frozen predictions follow from
[`predict_q140e.py`](predict_q140e.py), which imports the frozen code unchanged after checking 26 inputs' sha256 and runs five reproduction
checks before anything else. Nothing is refitted.*

*(Dated note, Wed 4 Nov 2026.) The registration's header and `registration.json` say it was written "about 02:15-02:40 PST". That runs past
its own commit at 02:23:53 PST: it was written about 02:15-02:23 PST. The frozen files are left as committed.*

## Results first

**Frozen for the two replicate sessions** ([`predictions-q140e.json`](predictions-q140e.json), [`predictions-q140e.txt`](predictions-q140e.txt)):

1. **One duty convention for both cards** (R1). A hold's kernel duty is the time in every kernel-launch record of its work processes, the
   per-process calibration launch included, over the span from its first process's start to its last process's end. It is read from the
   launch records alone. E154's harness gives **0.9611-0.9618** on the natural-chain holds and **0.7916** on K_S. E161's gives **0.9696**
   (G1Q) and **0.9702** (G2Q). Each replicate's primary runs on its own records, so both cards' arm E now carry the measured schedule, as
   E154's already did.
2. **aifoundry2's in-work level from Q140(l)** (R2). T1, T2 and T3 carried in Q140(l), and T4 is nil. Used here: **T2's zeros-level
   shift through M9's refit relation**, −0.99 W on both hold tiles (−0.991 W at 800 MHz on G1Q's tile, −0.98 W on G2Q's). It is applied on
   Q139(e)'s board with **one die law, the composition's own 0.442 W/°C from 56.0 °C**, which also closes the chain. **k_T (T3) and the
   cap plateau (T1) are not used.**
3. **The scoring window ends at the hold's last process** (R3). On aifoundry2 that moves it 5.9 s earlier, and the predicted plateau becomes
   the trajectory's mean over the window rather than the fixed point. On aifoundry3 it moves 0.02-0.18 s (1.9 s on K_S).
4. **The critic's rank-3 rules, registered as the decision** (R4):
   - RK3-a: the critic's per-hold rule (plateau and checkpoints' rms within √(0.18² + (0.87 σ_S)²)) on **3 or more of 4** aifoundry3 holds;
   - RK3-b: **G1Q within 1.0 °C, its trajectory 1.0 °C rms or less**;
   - RK3-c: **given the watts, every rise of 10 °C or more within ±1.5%** in E166 and in E167.
5. **The designs** (R5).
   - **E166 is 73.0 minutes of plan** inside E154's 76: K_S from rest, K_Q, K_L, then **K_OL**, `fp32.a_onebit_b5_third` held **25 minutes**.
     K_OL's first 600 s are K_O's replicate window. H_M is not run (D1).
   - **E167 is E161's design** unchanged, 35.1 of 40 card-minutes. Its peaks are 53.3 and 68.2 W at 95% by M8's peak rule, under 82 W.

**The frozen numbers at the nominal anchors** (aifoundry3 at a 51.2 °C room; aifoundry2 at E161's anchors, 47.0 °C with 22.12 / 22.19 W):

| hold | what | Q139(e) as frozen | the duty convention alone (amendment A2) | **the registered primary** |
|---|---|---|---|---|
| K_S | plateau rise over its anchor | 11.37 (a rounded duty; A1 on the plan 11.72) | 11.73 (d 0.7916, after a 3.2 °C tail) | **14.78 from rest** (E166 runs it first; peak 66.96 °C) |
| K_Q | plateau rise | 6.21 (A1 6.09) | 6.08 (d 0.9618) | **6.10** (tail 4.39 °C) |
| K_L | plateau rise | 3.54 (A1 3.54) | 3.53 (d 0.9617) | **3.53** (tail 3.05 °C) |
| K_O | plateau rise, the 10-minute window | 11.21 (A1 11.20) | 11.16 (d 0.9611) | **11.16** (tail 1.88 °C) |
| **K_OL** | **plateau rise, the 25-minute hold's last 300 s** | — | — | **11.86** (peak 65.0 °C; band 0.73 °C) |
| G1Q | plateau, °C | 63.78 (the fixed point; 63.71 as the window mean) | 63.20 (d 0.9696) | **62.30** (M9's level at d; rise 15.30) |
| G2Q | the trip clock, MHz | 667.5 | 674.5 (d 0.9702) | **685.6** (M9's level at d; plateau the trip rule's 65.9 °C) |

**The long hold's frozen trajectory** (K_OL at 51.2 °C, the rise over its anchor, °C):
- 60 s: 4.92;
- 120 s: 7.23;
- 300 s: 10.34;
- 600 s: 11.57;
- 900 s: 11.82;
- 1200 s: 11.81;
- the end: 11.89.

The chain has no stage slower than 120 s, so it predicts the rise grows 0.70 °C from K_O's window (11.16) to the last 300 s (11.86) and then
stops. **The slow-stage reading** G_A is arm A's plateau error over the long window minus that over K_O's window. It reads SEEN at
+0.15 °C or more and NOT SEEN between −0.15 and +0.05 °C. The scenarios below give the scale, calibrated to E154's 3.78% deficit given the
watts:
- one extra stage at τ = 600 / 1200 / 2400 s gives **G_A +0.50 / +0.79 / +0.93 °C**;
- the same deficit as a gain error gives **+0.03 °C**.

So the hold tells a slow stage of E154's size from a gain error by a factor of 15 or more.

**Post hoc on the sessions already seen** ([`posthoc.txt`](posthoc.txt), [`posthoc.json`](posthoc.json); never a verdict). E161's duty is
its own, and M9's level never saw E161:
- **E161 G1Q:** the plateau error goes −0.90 °C (as registered) → −0.77 (the new window and plateau) → −0.26 (the duty alone) → **+0.64 °C**
  (the duty and M9's level). The trajectory's rms goes 1.04 → 1.05 → 0.65 → **0.50 °C**. So RK3-b would have passed, but not over the REST's
  whole-degree anchor: at −0.5 °C it reads +1.34 °C.
- **E161 G2Q:** the clock error goes +12.6 → +14.1 → +7.1 → **−4.0 MHz**.
- **E154:** the plateau errors move by 0.004 °C or less. RK3-a would have read **1 of 4** (K_L only).
- **RK3-c, given the watts:** E154's three large rises read **+3.1 / +3.5 / +4.6%** low and E161's G1Q **+2.3%**. Only G2Q, at −1.2%, is
  inside ±1.5%.

**So the replicates test two things.**
- Whether the chain's 2-5% deficit on large rises, given the watts, repeats on both cards in a second session.
- Whether the 25-minute hold puts it in a slow stage (G_A ≥ 0.15 °C) or in the chain's gain (G_A ≈ 0).

With M9's level, aifoundry2's power path is right to about 0.1 W inside the work. G1Q's remaining +0.64 °C (post hoc) is the heat path's
+0.37 °C given the watts, plus the convention's counting of process start-ups as idle.

## What this does to predicting power and heat (prediction_effect)

**The terms tested or corrected:**
- **the duty term:** the switching power is on only for the kernel duty from the launch records, on both cards;
- **aifoundry2's in-work level:** M9's T2 zeros-level shift through its refit relation, applied with the composition's one die law;
- **the scoring window:** it ends at the last process;
- **heat beyond 10 minutes:** the frozen chain's prediction for a 25-minute large rise, with the slow-stage reading registered to test it.

**Out-of-sample error, before** (as registered and scored):
- aifoundry3: E154 0.370 °C rms over four 10-minute plateau rises from the bits. 1 of 4 holds is inside the critic's per-hold rule. Given the
  watts, the large rises read 3.1-4.6% low.
- aifoundry2: E161 G1Q −0.90 °C, with its trajectory at 1.04 °C rms; G2Q's sustained clock +12.6 MHz.

**After: no out-of-sample error changes until E166 and E167 score.** What the new terms do to the same sessions, post hoc (E161's duty is
its own; M9's level is out of sample for E161):
- **aifoundry2:**
  - G1Q −0.90 → +0.64 °C;
  - G1Q's trajectory rms 1.04 → 0.50 °C;
  - G2Q's clock +12.6 → −4.0 MHz.
  The duty alone gives −0.26 °C and +7.1 MHz. Its closer plateau is M8's 0.9 W-high level cancelling the chain's low gain.
- **aifoundry3:** unchanged, 0.37 °C rms, because E154's arm E already ran on its realized records.

**The expected size of the replicates' errors** (the frozen bands):
- aifoundry3: 0.60-1.45 °C at 95% per hold, the critic's scales 0.28-0.57 °C, and the long hold 0.73 °C;
- aifoundry2: 3.15 °C on G1Q (the critic's rule 1.0 °C), and ±0.60 °C and ±35 MHz at the trip.

## Registered against post hoc, number by number

| # | what | status |
|---|---|---|
| 1 | the duty convention: its definition, which records, how each card's composition uses it, the session's own records as the primary | **registered** (R1, `11174d20`), before any prediction. The planned values 0.9611-0.9618 / 0.7916 / 0.9696 / 0.9702 were read from the records while writing it (disclosed there) |
| 2 | the level: option (a), T2 through M9's relation, the fallback δ, the one die law, T1 and T3 not used | **registered** (R2). It was chosen after reading Q140(l)'s post hoc C1, where option (b) reads E161 closer (disclosed) |
| 3 | the windows and checkpoints | **registered** (R3) |
| 4 | RK3-a, RK3-b, RK3-c, the readout note, the carried band verdicts | **registered** (R4) |
| 5 | E166's and E167's designs, the room rules, no subset | **registered** (R5); the room rules' tables computed after it |
| 6 | the slow-stage reading and its thresholds; the three extra-stage scenarios | **registered** (R6); the scenarios' numbers computed after it |
| 7 | the gain scenario (`gain_D6`) | **after the registration**, dated D6, reported only, before any E166 data |
| 8 | amendment A2 (E154's design and E161's holds at the duty convention alone) | computed after the registration, by registered definitions (R7.2) |
| 9 | E166's and E167's frozen numbers, bands and room-rule tables | computed after the registration (R7.3, R7.4) |
| 10 | every reading on E154's and E161's data ([`posthoc_q140e.py`](posthoc_q140e.py)) | **post hoc**, never a verdict (R7.5) |

## The duty convention (R1)

| session | hold | item | kernel duty d | E154's registered share (over the hold mark) | the hold mark's end minus the last process's end |
|---|---|---|---|---|---|
| E154 | H_M | `int8.full` | 0.9615 | 0.9613 | 0.183 s |
| E154 | K_S | `fp32.real_smol_softmax_v_causal` | 0.7916 | 0.7891 | 1.921 s |
| E154 | K_Q | `int8.real_qwen_w8a8_v` | 0.9618 | 0.9615 | 0.151 s |
| E154 | K_L | `int8.b_line_zero_ff` | 0.9617 | 0.9616 | 0.085 s |
| E154 | K_O | `fp32.a_onebit_b5_third` | 0.9611 | 0.9610 | 0.016 s |
| E161 | G1Q | `int8.b_line_zero_ff` | 0.9696 | (continuous work, 1) | 5.94 s |
| E161 | G2Q | `fp32.real_smol_softmax_v_causal` | 0.9702 | (continuous work, 1) | 5.96 s |

Both harnesses write a 20,000-iteration calibration launch at each process's start, and E161's corrections counted it (0.970). So the
convention counts every record. Without it, aifoundry3's natural holds read 0.9585-0.9603 and E161's 0.9683-0.9685.
- **On aifoundry3** the frozen chain integrates the records one by one, through E154's registered arm E machinery (`score_e144.s_on_grid`
  and `closed_on_grid`).
- **On aifoundry2** the switching part is scaled by d, with E161's corrections C1 formulas: the chain is driven by
  L(T) + d (board − L(T)) − P_ref; at the trip, P_w = L_t + (P_t − L_t)/d.
- **Known bias (stated in R1):** on aifoundry2 a process's first 0.15-0.2 s draws 36-39 W before its first kernel launch, and the convention
  counts that as idle.

## Amendment A2 to Q139(e): the duty convention alone (dated Wed 4 Nov 2026; Q139(e)'s predictions unchanged)

*Q139(e)'s `predict_q139e.py`, `predictions-q139e.json` and amendment A1 stay as committed (`455c46c1`, `e224a3f8`). This re-predicts E154's
design and E161's two holds for the duty convention only: M8's level, Q138(t)'s chain, on R3's windows. The values are in
`predictions-q140e.json` › `amendment_A2_duty_convention_alone`.*

**aifoundry3, E154's design (H_M included) at a 51.2 °C room, on E154's own records** (plateau rises over each hold's anchor, °C):

| hold | Q139(e) frozen (share) | A1, arm E on the plan | **A2, at the kernel duty** | carried-in tail | in-launch peak |
|---|---|---|---|---|---|
| H_M | 11.015 (0.9655) | 11.015 | **10.981** (0.9615) | 0.00 | 62.51 |
| K_S | 11.365 (0.7908, ran 0.773) | 11.722 | **11.732** (0.7916) | 3.20 | 67.01 |
| K_Q | 6.207 (0.9655) | 6.091 | **6.083** (0.9618) | 4.41 | 62.00 |
| K_L | 3.542 (0.9655) | 3.544 | **3.530** (0.9617) | 3.05 | 57.94 |
| K_O | 11.205 (0.9655) | 11.203 | **11.156** (0.9611) | 1.88 | 64.74 |

On aifoundry3 the convention moves the plan by −0.05 to +0.01 °C from A1, because E154's arm E already ran on records.

**aifoundry2, E161's holds at E161's anchors** (`by rest die` 44-48 °C in the JSON):

| hold | continuous work (Q139(e)) | at the kernel duty (A2) |
|---|---|---|
| G1Q (47.0 °C, 22.12 W) | fixed point 63.775 °C; the trajectory's window mean 63.705 | fixed point **63.265**; window mean **63.197** °C |
| G2Q (47.0 °C, 22.19 W) | trip; the clock 667.5 MHz | trip; the clock **674.5 MHz** |

The fixed point and the trip clock at d reproduce E161's corrections C1 exactly (63.265 °C, 674.464 MHz).

## E166: aifoundry3 card 0, 600 MHz pinned (frozen; `predictions-q140e.json` › `E166`)

| step | min | item | pattern | plan duty |
|---|---|---|---|---|
| R0 | 5.0 | rest (the room) | | |
| K_S | 10.0 | `fp32.real_smol_softmax_v_causal` | 7 dispatches every 4.37 s (room ≤ 51.5 °C), 4.97 s (51.5-53.0 °C), a rest above 53.0 °C | 0.7916 |
| R2 | 3.5 | rest | | |
| K_Q | 10.0 | `int8.real_qwen_w8a8_v` | natural chain | 0.9618 |
| R3 | 3.5 | rest | | |
| K_L | 10.0 | `int8.b_line_zero_ff` | natural chain | 0.9617 |
| R4 | 3.5 | rest | | |
| **K_OL** | **25.0** | `fp32.a_onebit_b5_third` | natural chain; its first 600 s are K_O's window | 0.9611 |
| R5 | 2.5 | rest (the long hold's cool-down) | | |

**Plateau rises from the bits (M8's S), by room** (°C; the in-launch peak, 34-sensor mean, in brackets):

| room (K_S period) | K_S | K_Q | K_L | K_O window | **K_OL** |
|---|---|---|---|---|---|
| 49.5 (4.37 s) | 14.41 (64.84) | 6.08 | 3.53 | 10.93 | 11.56 (62.91) |
| 50.6 (4.37 s) | 14.65 (66.21) | 6.09 | 3.53 | 11.07 | 11.75 (64.26) |
| **51.2 (4.37 s)** | **14.78 (66.96)** | **6.10** | **3.53** | **11.16** | **11.86 (65.00)** |
| 51.5 (4.37 s) | 14.84 (67.33) | 6.11 | 3.53 | 11.20 | 11.91 (65.37) |
| 52.5 (4.97 s) | 13.07 (66.67) | 6.80 | 3.53 | 11.34 | 12.09 (66.62) |
| 53.0 (4.97 s) | 13.17 (67.28) | 6.82 | 3.53 | 11.41 | 12.19 (67.24) |
| 53.5 (K_S a rest) | — | 10.65 (from rest) | 3.55 | 11.48 | 12.29 (67.87: over the line) |

- **Every planned in-launch peak is at or under 67.5 °C up to a 53.2 °C room.** Above about 53.25 °C, K_OL's room rule ends it early, at
  the last whole launch before the first crossing: at 53.3 °C after 758 s, at 53.4 °C after 636 s, at 53.5 °C after 567 s.
  - Up to 53.4 °C, K_O's window (the first 600 s) is complete and is scored.
  - Between 53.4 and 53.5 °C the crossing moves before 600 s. K_O's window is then incomplete, and K_O is not scored.
  - Above 53.0 °C, K_S is a rest (E154's room rule). The registered RK3-a counts a hold that did not run as not inside, so a room above
    53.0 °C leaves it at most 3 of 4.
  - So **E166 is worth starting only with R0's room at or under 53.0 °C**. That is a reading of the registered rules, not a new one.
- **The arms beside, at 51.2 °C** (the same chain and records):

  | hold | M8 | M7 | M6 | E153's measured S |
  |---|---|---|---|---|
  | K_S | 14.78 | 14.71 | 14.62 | 14.39 |
  | K_Q | 6.10 | 6.12 | 6.16 | 5.98 |
  | K_L | 3.53 | 3.89 | 4.34 | 4.11 |
  | K_O window | 11.16 | 10.99 | 10.79 | 11.06 |
  | K_OL | 11.86 | 11.68 | 11.46 | 11.75 |

- **Bands:**
  - the four replicate holds keep Q139(e)'s frozen ones: band / FAIL K_S 0.599 / 1.30, K_Q 0.941 / 1.882, K_L 1.446 / 2.892, K_O 0.688 /
    1.376 °C;
  - their critic scales are 0.278 / 0.369 / 0.574 / 0.277 °C;
  - K_OL's long window, by the same form: G = 1.344 °C per W, band **0.73 °C**, FAIL beyond 1.461 °C, critic scale 0.277 °C.
- **The plan's records** are E154's records for each item. K_S at 4.97 s re-lays E154's K_S launches, and K_OL repeats E154's K_O block
  every 600 s. The plan's K_OL ends at its last whole launch, 1494.1 s; the card's runner fills to the mark with a shortened last launch, as
  E154's did. The primary uses the realized records, so this enters no verdict.

## The long hold and the slow stage (R6)

Q138(t)'s chain has no stage slower than 120 s on either card: its 250, 500 and 1000 s poles have zero weight. Past 10 minutes it predicts
only the closed loop's last approach, +0.70 °C here, which is over by about 15 minutes. **K_OL's frozen trajectory at 51.2 °C** (the rise
over its anchor, °C):

| 60 s | 120 s | 180 s | 300 s | 450 s | 600 s | 900 s | 1200 s | end | K_O's window (300-600 s) | **K_OL's window (the last 300 s)** |
|---|---|---|---|---|---|---|---|---|---|---|
| 4.92 | 7.23 | 8.67 | 10.34 | 11.26 | 11.57 | 11.82 | 11.81 | 11.89 | 11.16 | **11.86** |

**What a slow stage would read** (reported scenarios, never a verdict; `E166_slow_stage_scenarios_reported`). Each is calibrated so that arm
A's error over K_O's window is E154's mean deficit given the watts, 3.78% of the rise (H_M 3.14%, K_S 3.54%, K_O 4.64%):

| scenario | extra R (°C/W) or gain | arm A, K_O window | arm A, K_OL window | **G_A** | registered reading |
|---|---|---|---|---|---|
| one stage, τ 600 s | 0.107 | +0.45 °C | +0.95 °C | **+0.50** | SEEN |
| one stage, τ 1200 s | 0.191 | +0.45 °C | +1.24 °C | **+0.79** | SEEN |
| one stage, τ 2400 s | 0.288 | +0.46 °C | +1.38 °C | **+0.93** | SEEN |
| a gain error, every R × 1.039 (D6) | γ 0.039 | +0.45 °C | +0.48 °C | **+0.03** | NOT SEEN |
| the chain as frozen (the check) | 0 | 0 | 0 | 0.000 | NOT SEEN |

The thresholds are SEEN at +0.15 °C or more, INCONCLUSIVE from +0.05 to +0.15, NOT SEEN from −0.15 to +0.05, and LATE OVERSHOOT at −0.15 °C
or less. They sit between the two cases. A slow stage of a third of E154's size or more reads SEEN, and a chain that is merely low reads
NOT SEEN. **The confound stays:** with no inlet thermometer, a room that warms during K_OL reads as a slow stage.

## E167: aifoundry2 card 0, its own governor (frozen; `predictions-q140e.json` › `E167`)

E161's design unchanged: SMOKE, the two stop tests, E98's 15-minute rest, G1Q (REST 2 min plus 93 × 8 s processes), END 2 min, the 15-minute
rest, G2Q (REST 2 min plus 91 × 8 s processes), END2 2 min. Plan d: 0.9696 / 0.9702. Spans: 782.97 / 770.97 s.

**At E161's anchors** (47.0 °C; 22.12 / 22.19 W):

| hold | arm | regime | plateau (°C) | rise | T800 fixed point | the clock | in-work board, window (W) | first step down |
|---|---|---|---|---|---|---|---|---|
| G1Q | **primary: M9's level at d** | 800 MHz | **62.30** | 15.30 | 62.36 | 800 MHz | 45.78 | none |
| G1Q | M8 at d (the convention alone) | 800 MHz | 63.20 | 16.20 | 63.27 | 800 MHz | 47.17 | none |
| G1Q | M8 continuous (Q139(e)) | 800 MHz | 63.71 | 16.71 | 63.78 | 800 MHz | 47.40 | none |
| G2Q | **primary** | trip | 65.9 (rule) | 18.9 | 78.68 | **685.6 MHz** | 51.02 | 63 s |
| G2Q | M8 at d | trip | 65.9 | 18.9 | 79.57 | 674.5 MHz | 50.86 | 45 s |
| G2Q | M8 continuous | trip | 65.9 | 18.9 | 80.57 | 667.5 MHz | 50.13 | 42 s |

- **G1Q's primary checkpoints** (rises over the REST, °C):
  - 60 s: 8.87;
  - 120 s: 11.79;
  - 180 s: 13.33;
  - 300 s: 14.65;
  - 450 s: 15.15;
  - 600 s: 15.30;
  - 750 s: 15.34;
  - the end: 15.35.
- **Over the REST's ±0.5 °C** the primary's rise moves to 15.10 / 15.50. **The primary puts G1Q in the trip regime above a rest die of
  49.97 °C** (at d, with M9's level; Q139(e)'s frozen table put that edge at about 49.4 °C).
- **By rest die, the primary:**
  - G1Q 58.68 / 59.88 / 61.08 / 62.28 / 63.47 °C at 44-48 °C;
  - G2Q at the trip, 720.7 / 710.4 / 700.0 / 685.2 / 670.3 MHz.
- **The 82 W rule:** M8's peak rule is unchanged (G1Q 53.33 W, G2Q 68.15 W at 95%). The primary's highest simulated in-work boards are
  45.8 and 65.3 W.

## Post hoc on E154 and E161 (`posthoc_q140e.py`; never a verdict)

**E154, aifoundry3** (R0's room 51.410 °C), on the convention's window. Every plateau figure equals the registered one to 0.004 °C or less;
K_O's checkpoints' rms differs for the reason in the finding below:

| hold | rise | arm E (M8) plateau error | checkpoints' rms | arm A plateau error, and its share of the rise |
|---|---|---|---|---|
| H_M | 11.21 | +0.193 | 0.18 | +0.352 (+3.14%) |
| K_S | 11.79 | +0.020 | 0.370 | +0.418 (+3.55%) |
| K_Q | 5.67 | −0.418 | 0.401 | +0.005 (+0.08%) |
| K_L | 4.02 | +0.492 | 0.450 | +0.073 (+1.80%) |
| K_O | 11.55 | +0.360 | **0.315** | +0.536 (+4.64%) |

- **RK3-a would have read 1 of 4** (K_L), as E154's C1 found. **RK3-c would have failed** on the three large rises, at 3.1-4.6%.
- **A finding about E154's registered scorer (no verdict changes).** K_O's registered checkpoints' rms, 0.344 °C, includes a 600 s
  checkpoint whose 5 s window runs 2.5 s into R5. In `score_e144.a3_session` K_O's span came out 600.001 s (the rest started 1 ms after the
  hold's end mark), so `traj` kept the 600 s checkpoint, which the other three holds did not. On R3's convention (each checkpoint ends
  before b) it is 0.315 °C. K_O is outside its 0.277 °C critic scale either way.

**E161, aifoundry2** (its own d; M9's level never saw E161), on the convention's window:

| hold | arm | plateau error | checkpoints' rms | clock error |
|---|---|---|---|---|
| G1Q | registered (Q139(e), continuous, the old window, the fixed point) | −0.898 | 1.044 | (share 0.952, PASS) |
| G1Q | M8 continuous, the convention's window and plateau | −0.770 | 1.053 | |
| G1Q | M8 at d | −0.262 | 0.651 | |
| G1Q | **M9's level at d (the new primary)** | **+0.636** | **0.504** | |
| G1Q | the primary over the REST's −0.5 / +0.5 °C | +1.336 / −0.065 | 0.63 / 0.42 | |
| G2Q | registered | −0.397 | 0.509 | +12.6 MHz |
| G2Q | M8 continuous / M8 at d / **primary** | −0.336 (the trip rule) | 0.48 / 0.59 / **0.31** | +14.1 / +7.1 / **−4.0 MHz** |

- **RK3-b would have passed** (+0.64 °C, 0.50 °C rms), but **not over the anchor's readout**: at −0.5 °C it reads +1.34 °C.
- **RK3-c:** G1Q's arm A reads +0.372 °C, **+2.33%** of its 15.9 °C rise (−0.8% to +5.3% over the REST's ±0.5 °C). G2Q's reads −1.16%. So
  RK3-c would have failed on aifoundry2 too, and the readout cannot resolve it there.
- **Why the duty alone reads G1Q closer than the primary:** M8's level is 0.91 W high inside the work (E161 C1). That cancels most of the
  chain's own +0.37 °C given the watts and the start-up power the convention counts as idle. With M9's level, the in-work board is within
  about 0.1 W of the measured one, so the remaining +0.64 °C is the heat path's.

## Departures (dated)

Registered with the plan, Wed 4 Nov 2026, before any prediction (REGISTRATION.md):
- **D1** H_M is not run, and K_S starts from a rested die. With them, E154's 72.5 minutes plus a 25-minute hold would not fit 76.
- **D2** K_O's replicate window is the first 600 s of the 25-minute K_OL.
- **D3** On aifoundry2 the predicted plateau is the trajectory's window mean (E161 used the fixed point). The window ends at the last
  process, and "end" joins the checkpoints.
- **D4** E167's level uses M9's fallback zeros offset, because E167 runs no zeros anchor.
- **D5** There is no registered subset.

Added after the registration, Wed 4 Nov 2026 about 03:00 PST, before any E166 or E167 data:
- **D6** The gain scenario (`gain_D6`) joins the reported slow-stage scenarios. It is the case the NOT SEEN threshold stands for, reported
  only.

## What this cannot say

- **No out-of-sample error moves tonight.** Every new figure on E154 or E161 is post hoc. E161's duty is its own.
- **The convention counts aifoundry2's process start-ups as idle**, at 36-39 W for 0.15-0.2 s each. That is part of G1Q's post hoc +0.64 °C,
  and the critic chose the convention.
- **On aifoundry2 the REST's whole-degree die is a ±0.5 °C anchor.** That is ±3% of a 16 °C rise, wider than RK3-c's ±1.5% and about the
  width of RK3-b's 1.0 °C. A verdict there may be "not resolved by the readout" (R4's note).
- **A slow stage cannot be told from a room that warms during K_OL** without an inlet thermometer.
- **The level arm rests on Q140(l)'s fallback zeros offset**, the mean of four sessions. A session's own offset has varied 1.35-1.74 W,
  which is ±0.13 W through β, about ±0.12 °C on G1Q.
- **E166 changes E154's sequence** (H_M dropped, K_S from rest). It replicates the four kinds and the frozen path, not E154's exact tails.

## How to reproduce

```bash
/usr/bin/python3 docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py --selftest      # the five reproduction checks only, ~5 s
/usr/bin/python3 docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py > docs/reports/data/2026-11-04-q140e-heat-replicates/predictions-q140e.txt   # ~1 min
/usr/bin/python3 docs/reports/data/2026-11-04-q140e-heat-replicates/posthoc_q140e.py > docs/reports/data/2026-11-04-q140e-heat-replicates/posthoc.txt           # ~10 s
```

numpy 1.26.4, Python 3.9 (the Intel's `/usr/bin/python3`); both outputs are byte-identical on a rerun.

**What the checks reproduce** (`predictions-q140e.json` › `checks`):
- Q139(e)'s `a2_closed` at d = 1, sample for sample (worst |diff| 0);
- its 46.0 °C table (62.545 °C; 681.6 MHz);
- E161 C1's kernel duty, fixed point and trip clock (0.9696 / 0.9702; 63.265 °C; 674.464 MHz);
- Q140(l) C1's level (−0.991009 W);
- E154's registered arm E rises, through the scorer's own path, to the third decimal; this lane's plan grid is within 0.006 °C of them.

**For E166's and E167's scorers:** the functions `a3_records`, `a2_records`, `kernel_duty`, `a3_arm_e_on_records`, `a3_read`, `a2_hold`,
`a2_closed_dl`, `a2_fixed_800`, `a2_trip_clock_dl` and `level_offsets` are importable. Each card lane registers its own scorer on them before
its claim.

## Device commands sent

None: this lane opened no device and ran nothing on any box. E166 and E167 each list and classify theirs with
`tools/claims-v3/dmcmd_audit.py` before their first launch.

## Files

| file | what |
|---|---|
| `REGISTRATION.md`, `registration.json` | **the registration** (`11174d20`, 02:23:53 PST): R1-R7 and departures D1-D5, committed before any prediction |
| `predict_q140e.py` | the frozen composition: the checks, amendment A2, E166's and E167's predictions, the scenarios, the room rules |
| `predictions-q140e.json`, `.txt` | **frozen**: everything above, with each hold's checkpoints by room or rest die |
| `posthoc_q140e.py`, `posthoc.json`, `posthoc.txt` | the post hoc readings on E154 and E161 (never a verdict) |
