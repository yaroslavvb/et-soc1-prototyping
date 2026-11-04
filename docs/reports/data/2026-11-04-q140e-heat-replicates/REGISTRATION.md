# Q140(e) registration: the heat replicates' frozen predictions, one duty convention, the level and the rules (desk, Wed 4 Nov 2026)

*Written Wed 4 Nov 2026 (week 45), about 02:15-02:40 PST, on the Intel, desk only: no card, no device command, no ssh to a lab box, no
Discord, no Modal, no archive. It is committed through `commit_lab.sh` **before any prediction, fit or score of this lane is computed**.
The predictions it names are computed afterwards by `predict_q140e.py` in this directory, with the frozen code imported unchanged after a
sha256 check. Machine-readable copy: [`registration.json`](registration.json).*

*It answers Q139's final critic, **rank 3**, "Heat over minutes from the bits, a second session per card", and the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**items 9** (a steady state for heat), **8** (the heat path between sessions) and **6** (the power model). Its inputs are Q139(e)'s frozen
composition (`455c46c1`, amendment A1 `e224a3f8`), E154 (`d037d82a`, corrections `d37c787e`), E161 (`0158efd6`, corrections `d0704105`),
Q138(t)'s frozen chain and Q140(l)'s M9 aifoundry2 part (`5b98bd5c`, corrections `5c98c0c5`). The card runs it freezes for are **E166**
(aifoundry3) and **E167** (aifoundry2), the planned card half of Q140; they need the owner's word and are not run tonight.*

## What the lane read before writing this

Disclosed so the order is clear. Before this registration the lane read: the critic's rank 3 and faults 2 and 6; Q139(e)'s README, code and
frozen JSON; E154's and E161's READMEs, corrections and scorers; Q140(l)'s README, `predict_m9_a2.py`, `m9_a2.json` and its corrections C1
(which already give, post hoc and linear, E161 G1Q's plateau error under Q140(l)'s two die-law options: +0.51 °C with option (a), +0.22 °C
with option (b), at the kernel duty). It also read, from E154's and E161's committed launch records, the kernel duty this registration
defines (below), to fix the definition: E154 0.9611-0.9618 on the natural-chain holds and 0.7916 on K_S, E161 0.9696 (G1Q) and 0.9702
(G2Q). Those are the harnesses' schedules, read from records; nothing was fitted or predicted.

## R1. One duty convention for both cards: the kernel duty from the launch records

- **Definition.** A hold's kernel duty is the time inside kernel launches over the hold's span, from the harness's launch records alone,
  never from telemetry: d = Σ (t_end − t_start) over every kernel-launch record of the hold's work processes, the per-process calibration
  launch included, divided by (end of the hold's last process − start of its first process).
  - aifoundry3 (E97's harness, as E154 ran it): the records are `runs.jsonl` (one per dispatch, the `launch` = −1 calibration record
    included); the processes are `marks.jsonl`'s `launch` marks of the hold's block.
  - aifoundry2 (E144b's harness, as E161 ran it): the records are `launches.jsonl`'s `sparsity` entries of the HOLD's work processes (the
    `launch` = −1 entry included); the processes are those work records (as `corrections_e161.py` and `reduce_e161.work_processes` read
    them).
- **How each card's composition uses it.** On aifoundry3 the frozen chain integrates the records one by one (E154's registered arm E
  machinery, `score_e144.s_on_grid` and `closed_on_grid`): each record is on at the item's frozen S. On aifoundry2 the composition's
  switching part is scaled by d, with E161's corrections C1 formula: the board that drives the chain is L(T) + d (board(f, T) − L(T)), L(T) =
  P_ref + 0.442 (T − T_rest), the idle board at die T. The trip clock at duty d is E161 C1's: the held board P_t = P_ref + (65.9 − T_rest)/R,
  the in-work board P_w = L_t + (P_t − L_t)/d, the clock where the in-work board meets P_w. At d = 1 both reduce to Q139(e)'s frozen code.
- **Which d.** The registered primary of each replicate runs on **the session's own launch records** (aifoundry3: every record; aifoundry2:
  each hold's own d), so both cards' arm E carry the measured schedule, as E154's arm E did. The planned value, frozen here and reported
  beside as "the plan", is the previous session's: per aifoundry3 hold, E154's records for the same kind laid out as described in R5;
  per aifoundry2 hold, E161's d for the same hold.
- **Known bias, stated now.** On aifoundry2 a process's first 0.15-0.2 s, before its first kernel launch, draws 36-39 W, not the idle board
  (E161 corrections C1); the convention counts it as idle. It is registered as the critic named it, not tuned.

## R2. The in-work level on aifoundry2: M9's zeros-level shift, with one die law

- **Which terms carried in Q140(l).** T1 (the cap plateau, 2.52 W over a 64.60 W relation cap), T2 (a same-session zeros-anchor level,
  β 0.648) and T3 (a die-start term, k_T 0.395 W/°C from 54.38 °C) carried by its registered rule; T4 (s(f) at n = 2 from the voltage
  reads) was kept by the rule's letter on 0.002 W and is nil.
- **Registered here (Q140(l)'s option (a)).** The in-work board of an aifoundry2 hold is Q139(e)'s composition with M8's level replaced by
  M9's: board9(f, T) = board8(f, T) + ΔL(f), with ΔL(f) = [B9(f) + c9 s9(f)] − [B8(f) + c8 s8(f)] + β δ_t at f = 600, 700, 800 MHz
  (linear between, as Q139(e)'s `board`), c8 = M8's c for the tile (Q139(e)'s `c_of`), c9 = M9's c_zeros[t] + g × D with D the same M8 D600
  from the bits, and δ_t M9's fallback zeros offset for the tile's format (`m9_a2.json` `fallback_delta_w`), because E167's design runs no
  zeros anchor. So the term used is **T2**, through M9's refit relation (which carries T4).
- **The die law is the composition's own, and only one:** Q139(e)'s 0.442 W/°C from its 56.0 °C reference die, which is also the leakage
  law that closes Q138(t)'s chain on aifoundry2. **T3 (k_T) is not used:** it is a burst-start law fitted on starts of 45-56 °C, the holds'
  plateaus sit 6-10 °C above that, it would replace the chain's frozen closure law (0.442) and change the closed loop's gain, and E159's
  three zeros holds read flat (0.06 W over starts of 52-57 °C) where a start-die term at k_T predicts a 2.0 W spread. **T1 is not used:** the
  holds' boards sit under the cap except in G2Q's first minute, where the governor's terms stay Q139(e)'s (M8's 65.2 W cap on the in-work
  board, one 100 MHz step a second on the whole-degree reading).
- **Disclosed:** the choice was made knowing Q140(l)'s post hoc C1, where option (b) (M9 whole) reads E161's G1Q closer (+0.22 against
  +0.51 °C at the kernel duty). It rests on the reasons above, not on that reading.
- **The arms.** E167's primary (arm E) uses M9's level (a) at the session's own d. Reported beside: M8's level at the same d ("the duty
  convention alone", the amendment's form) and M8's level at continuous work (Q139(e) as frozen). If E167's card session also runs zeros
  anchors on E80's harness, a reported arm recomputes δ with them through `predict_m9_a2.session_delta`, mechanically.
- **aifoundry3:** Q140(l)'s part is aifoundry2's only. E166's S stays M8's frozen S (Q139(e)'s `S_table_W`).

## R3. The scoring window ends at the last process; the trajectory starts at the first

- **Plateau:** the mean over [b − 300 s, b), b = the end of the hold's last process (from the launch records), of the measured die and of
  the predicted die, each as a rise over the hold's anchor (aifoundry3: the 34-sensor mean over the last 120 s of the rest before the hold,
  as E154; aifoundry2: the REST file's last 120 s of raw firmware samples, die and board, as E161). On aifoundry2 the predicted plateau is
  the frozen trajectory's mean over the same window (E161 read the 800 MHz fixed point; D3), and in the trip regime the trip rule's 65.9 °C.
- **Trajectory:** checkpoints measured from the start of the hold's first process, 5 s means (one launch cycle on K_S): 60, 120, 180, 300,
  450, 600 s on aifoundry3's 10-minute holds; 60, 120, 180, 300, 450, 600, 750 s on aifoundry2's 13-minute holds; 60, 120, 180, 300, 450,
  600, 900, 1200, 1500 s on the long hold; each one that ends before b, plus "end", the 5 s (one cycle) ending 0.5 s before b
  (`score_e144.traj`'s form). The checkpoints' rms is over all of them.
- **Arm A** (the chain on the measured board) is read on the same windows.

## R4. The rules: the critic's rank 3, registered as the decision

- **RK3-a, aifoundry3 (E166):** the critic's per-hold rule on **3 or more of the 4 replicate holds** K_S, K_Q, K_L and K_O (K_O's window
  is the first 600 s of the long hold, R5). Per hold: |arm E plateau error| ≤ the hold's critic scale **and** arm E's checkpoints' rms ≤ the
  same scale. The scales are Q139(e)'s frozen `critic_scale_C`, √(0.18² + (0.87 σ_S)²): K_S 0.278, K_Q 0.369, K_L 0.574, K_O 0.277 °C.
- **RK3-b, aifoundry2 (E167):** G1Q (`int8.b_line_zero_ff`): |arm E plateau error| ≤ 1.0 °C **and** arm E's checkpoints' rms ≤ 1.0 °C.
- **RK3-c, both:** given the watts, every large rise within ±1.5%: on every hold of E166 and of E167 whose measured plateau rise over its
  anchor is 10 °C or more, |arm A plateau error| / measured rise ≤ 0.015. "Both sessions" is read as E166 and E167, the new session on each
  card. Expected large rises: K_S, K_O's window and the long hold on aifoundry3; G1Q and G2Q on aifoundry2.
- **Rank 3 is answered on the replicates** if all three hold; each is reported on its own, with the number of holds inside.
- **Readout note, registered with RK3-b and RK3-c:** where an aifoundry2 REST reads one whole degree in every sample of its last 120 s, each
  reading is also given over the anchor's ±0.5 °C (E161's C2). A verdict that changes inside that interval is reported beside as "not
  resolved by the readout"; the registered verdict is the reading as is.
- **Carried, secondary (as E154 and E161 registered them, now on this convention's primary):** per aifoundry3 hold, Q139(e)'s band verdicts
  (PASS |pe| ≤ band_95_C and rms ≤ band_95_C; FAIL |pe| > fail_beyond_C; else INCONCLUSIVE) with its frozen bands (K_S 0.599 / 1.30,
  K_Q 0.941 / 1.882, K_L 1.446 / 2.892, K_O 0.688 / 1.376 °C); G1Q's band 3.149 / 6.297 °C and its clock share at ≥ 790 MHz over the window
  (PASS ≥ 0.90, FAIL < 0.75); G2Q's trip rule (PASS within ±0.60 °C of 65.9 in the trip regime, FAIL outside ±1.20 or the other regime) and
  its clock from the bits at the trip (PASS within ±35 MHz, FAIL outside ±70). Arm A's frozen bands (score_e144's) are reported.
- **The session figures, reported:** the rms of the four replicate holds' arm E plateau errors (aifoundry3), G1Q's error (aifoundry2),
  E − A per hold, M7's and M6's S (aifoundry3) and M7's c (aifoundry2) through the same composition, and E153's measured S (aifoundry3).

## R5. The designs, inside E154's 76 and E161's 40 card-minutes

**E166, aifoundry3 card 0, 600 MHz pinned, nothing set** (E154's harness; 73.0 minutes of plan; the smoke and its five stop tests come on
top, 1.4 minutes in E154, so about 74.4 of 76):

| step | min | item | pattern |
|---|---|---|---|
| R0 | 5.0 | rest | the room: the 34-sensor mean over its last 120 s |
| K_S | 10.0 | `fp32.real_smol_softmax_v_causal` | 7 dispatches (`--seconds 3.20`) once every 4.37 s (R0 ≤ 51.5 °C), 4.97 s (51.5-53.0 °C); above 53.0 °C K_S is a rest (E154's room rule) |
| R2 | 3.5 | rest | |
| K_Q | 10.0 | `int8.real_qwen_w8a8_v` | E97's natural chain |
| R3 | 3.5 | rest | |
| K_L | 10.0 | `int8.b_line_zero_ff` | natural chain |
| R4 | 3.5 | rest | |
| **K_OL** | **25.0** | `fp32.a_onebit_b5_third` | natural chain; **its first 600 s are K_O's replicate window**, the whole hold is the long large-rise hold |
| R5 | 2.5 | rest | the long hold's cool-down |

- **Why this shape (departure D1).** E154's 72.5-minute plan plus a 25-minute hold does not fit 76 minutes, so **H_M is not run** (E97's
  H1 replicate; it is not one of the four holds rank 3 names), and K_S starts from a rested die. The long hold is K_O extended because K_O
  is the pool-6 kind with an 11-12 °C rise that runs back to back (K_S, the other, is duty-cycled for its 67.5 °C peak line and would pass
  it over 25 minutes), and it was E154's last hold, so the three before it start as in E154.
- **K_O's replicate window (D2):** the first 600 s of K_OL, its b the end of the last process that ends at or before 600 s after the first
  process's start.
- **The planned records** (the plan's kernel duty): each hold's E154 records for the same item, at their offsets from E154's hold start; K_S
  at a 4.97 s period re-lays E154's K_S launches at that spacing; K_OL repeats E154's K_O block of launches every 600 s and keeps the
  launches that end by 1500 s.
- **The long hold's room rule:** K_OL runs its 25 minutes if its frozen in-launch peak (34-sensor mean) at R0's room, interpolated in this
  lane's table, is at or under 67.5 °C (H_H's line); otherwise it ends at the last whole launch before the plan's first crossing at that
  room, its K_O window still scored. The live stops are Q138(t)'s, unchanged: no launch at a firmware reading ≥ 70 °C; a hold ends at ≥ 72 °C
  or ≥ 65 W; the session at ≥ 74 °C.
- **No registered subset (D5):** the full design runs, or the session does not start.

**E167, aifoundry2 card 0, its own governor (65 W / 65 °C), nothing set** (E161's design unchanged; E161 used 35.07 of 40 card-minutes):
SMOKE, the die and board stop tests, E98's 15-minute no-launch rest, **G1Q** (REST 2 min, then 93 back-to-back 8 s processes of
`int8.b_line_zero_ff`, 13 min), END 2 min, the 15-minute rest, **G2Q** (REST 2 min, then 91 processes of `fp32.real_smol_softmax_v_causal`,
13 min), END2 2 min. **Section 22's power rule:** the 82 W admission value is M8's peak rule unchanged (Q140(l) registered that no level
term loosens it): G1Q 53.33 W and G2Q 68.15 W at 95% in Q139(e)'s frozen table, both under 82 W. Stops: E161's (a hold ends at a reading
≥ 72 °C or ≥ 80 W on three consecutive samples, tested in the smoke).

## R6. The long hold: looking for a slow stage

Q138(t)'s chain has no stage slower than 120 s on either card (its 250, 500 and 1000 s poles have zero weight), so beyond 10 minutes it
predicts almost no further growth; a slower stage would show as growth the chain does not have.
- **Readings (registered):** arm E's and arm A's plateau over the long hold's window and their checkpoints to 1500 s; its band by Q139(e)'s
  form, 1.96 √(0.18² + (G σ_S)²), with G = d(plateau)/dS on the long window (computed by the code), and its verdict by Q139(e)'s rule.
- **The slow-stage reading:** G_A = arm A's plateau error over the long hold's window minus arm A's plateau error over K_O's window, both
  over the same anchor (the rest before K_OL), in °C.
  - **SLOW STAGE SEEN** if G_A ≥ +0.15 °C; **NOT SEEN** if −0.15 °C < G_A ≤ +0.05 °C; **INCONCLUSIVE** if +0.05 < G_A < +0.15 °C;
    **LATE OVERSHOOT** if G_A ≤ −0.15 °C.
  - Reported with it: arm A's error at every checkpoint from 600 s on, its least-squares slope over 600 s → end (°C per 10 min), and arm
    A's cool-down rms over R5.
  - **The confound, stated now:** with no inlet thermometer, a room that drifts upward during K_OL reads as a slow stage. A SEEN verdict
    means "a slow stage or a room drift"; NOT SEEN excludes both at this size.
- **Scenarios, reported, never a verdict:** the chain plus one extra parallel stage at τ_s = 600, 1200 or 2400 s, its resistance set so that
  the closed loop's rise over K_O's window grows by f, the mean of E154's arm A plateau error over the measured rise on its three large rises
  (H_M, K_S, K_O; `scored.json`); each scenario's G_A for K_OL on the plan. They say what size of G_A a slow stage of E154's size would give.

## R7. What is computed after this commit, and what is post hoc

Computed by `predict_q140e.py` after this commit (frozen, then committed before any E166 or E167 claim):
1. **Reproduction first:** the frozen code reproduces Q139(e)'s committed aifoundry2 numbers, its duty-1 trajectory exactly, E161 C1's
   fixed point and trip clock at the kernel duty, Q140(l) C1's level shift, and E154's registered arm E predictions on E154's own records.
   If any check fails, nothing else is computed.
2. **Amendment A2 to Q139(e)'s predictions (dated, the old ones unchanged):** E154's design (H_M included) and E161's two holds re-predicted
   for the duty convention only (M8's level), at the planned d, on the windows of R3.
3. **E166's frozen predictions:** the design of R5 at rooms 49.5-53.0 °C (51.2 nominal), M8's S with M7's and M6's beside, each hold's
   trajectory, plateau, peak and band, the long hold's trajectory to 1500 s, the slow-stage scenarios, and the room rules' tables.
4. **E167's frozen predictions:** G1Q and G2Q at rest dies of 44-48 °C and at E161's measured anchors, for M9's level (a) at d (the primary),
   M8's level at d and M8's at continuous work; the regime, plateau, trajectory, clock, peak and the fixed points.
5. **Post hoc, labelled, never a verdict:** the convention, the windows and the level read on E154's and E161's committed data (sessions
   already seen; E161's d is its own), including the critic's rank-3 rules as they would have read there.

## Departures, dated now (Wed 4 Nov 2026, before any prediction of this lane)

- **D1** H_M is not run and K_S starts from a rested die (R5).
- **D2** K_O's replicate is the first 600 s of the 25-minute K_OL (R5).
- **D3** on aifoundry2 the predicted plateau is the frozen trajectory's mean over the window, which ends at the last process, and "end"
  joins the checkpoints, so both cards are read one way (E161 used the 800 MHz fixed point, a window ending at the HOLD file's last sample
  5.9 s after the last process, and no "end").
- **D4** E167's level uses M9's fallback zeros offset (E167 runs no zeros anchor).
- **D5** no registered subset.

## Device commands

None: this lane opens no device and runs nothing on any box. E166 and E167 each list and classify theirs with
`tools/claims-v3/dmcmd_audit.py` before their first launch.
