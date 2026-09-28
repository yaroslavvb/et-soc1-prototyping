# DV2: experiments on the DVFS-heat connection (design, revision 2)

Revision 1 was written at about 22:45 PDT on 27 Sep 2026. This revision was written at about 23:40 PDT, from
revision 1 and the adversarial review `CRITIQUE.md` in this directory. Every critique point is accepted, modified or
rebutted in §16. What development fixes, how it decides, and the exact run list for tonight are in `PREREG-DEV.md`.
Nothing here touched a card.

**Sources.**
- The three reviews (`review-pages.md`, `review-governor.md`, `review-heat.md`).
- The firmware the cards run: BL2 0.20.0 at `ffca4cbb4`, copied here as `tpm_may2024.c` (`TPM`).
- The pages worktree `/home/yaroslavvb/claude/et-soc1-pages5` (`P5/`), read only.
- The heat-placement worktree `/home/yaroslavvb/claude/et-soc1-heat` (`W/`) and its scratch data (`HP/` =
  `../heatplace/`), including the frozen `W/tools/claims-v3/hp/a2/PREREG-A2.md` (`A2`).
- New numbers:
  - `dv2_sim.py`: aifoundry2's own flips-to-temperature model;
  - `retro/`: a zero-card retrospective on the committed aifoundry2 clock-change telemetry (§2.2). Its scripts and
    outputs are `retro.py`/`retro.out`, `dwell.py`/`dwell.out`, `hot800.py`/`hot800.out` and
    `idlespread.py`/`idlespread.out`.

**The owner's method applies.**
- Theories and numeric predictions come first.
- All iteration happens on the development card.
- Validation is then frozen and not iterated.

**The owner's questions.**
- (1) Does DVFS act on the average temperature, or on one hot shire?
- (2) Can the same computation run longer before throttling in some chip locations?

---

## 0. In brief

- **The default plan changes no threshold.** Raising aifoundry2's software threshold (D1) is a global-state change the
  owner has not approved. It is now a question for the owner (§4.3). Without a yes, clock-step work runs only when
  aifoundry2 rests at a reading of 64 or less by itself (the NAT branches, §4.1).
  - aifoundry2 read 62 at 14:37 on 27 Sep. Otherwise it has read 66-67 all evening.
  - A watcher (Z1) checks every 10 minutes and can start a native session when a cool window opens.
- **Part of the mechanism is already answered, at zero card time (§2.2).** The committed telemetry holds 275 clock
  changes on aifoundry2.
  - All 85 climbs went up in one call. 700 MHz was never seen in two consecutive 10 Hz samples, and 50 climbs showed
    no 700 sample at all. HEAD's one point per pass cannot produce a climb with no 700 sample.
  - In 69 of 70 descents, 700 MHz was held for 0.4-0.5 s. That is the 0.40 s thermal loop, not HEAD's one pass.
  - Every measurable down-step came within 0.3 s after the host mean first read 66 (63 of 63). The other 7 came
    before the host saw 66.
  - Every up-step while hunting came from a reading of 64-66 (102 of 102; 90 at 65).
  - So new card time goes to the owner's two questions: G1 (the trigger) and G4 (placement). The mechanism items
    (G2, G3) become host-level replications, with bands frozen now from these data. Their SP-timed parts are set in
    development.
- **G1 answers the owner's first question** on the card. The theory is H-mean: the integer mean of the 34 shire
  sensors, compared as `> thr`. The alternative is H-max: the hottest sensor.
  - The existing data cannot separate them, because no committed sample at 800 MHz has a valid windowed high (0 of
    361).
  - G1 uses three observables: the timing of the down-step against the mean and against the high (A2's TRIG-A
    definitions); the temperature the SP prints when it steps; and a demonstration that a shire can read 2 °C or more
    above the threshold while the clock holds 800 MHz.
- **G4 answers the owner's second question.** It measures, at equal power, the ratio of time spent at 800 MHz before
  the first throttle for perimeter against interior placement.
  - The prediction comes from theory: aifoundry2's own heat-only ratio at 600 MHz (C1m, measured tonight on the
    pinned card) diluted by the clock's uniform adder (ADD, measured in-session).
  - Three outcomes are distinguished: diluted (PASS), undiluted, and none (both FAIL).
- **Validation is honest about the cards.** No second card has a free governor. So governor items get a **replication
  on aifoundry2** in later sessions under a frozen PREREG-DV2, not a validation on another card. The owner is asked
  whether that is acceptable.
  - aifoundry3 gets only a read-only state check tonight (Z2).
  - aifoundry1-c1 is not touched tonight.
- **Safety additions.**
  - A check after every run that the clock is back at 600 MHz, with an ABORT-LATCH branch.
  - A gate before every run.
  - No forced restore past the card lock, ever.
  - The power run is sized to 68-72 W under the 73 W cap.

---

## 1. What changed from revision 1

| Critique | Change in this revision |
|---|---|
| R1 (1) | D1 is a question for the owner (§4.3, verbatim). The default plan is "D1 no". Every D1 result is labelled "at a software threshold of thr* (raised from 65), one card" |
| R2, R3 (2) | The watchdog polls the session every 30 s, never forces past the lock, and alerts instead. Z1 checks `temp_threshold_c` every cycle. The dry tests include SIGKILL (§4.4) |
| R4 (3) | There is one set path only: `ettelem-dv2 threshold set`, interlocked. `dev_mngt_service` is never used for a set |
| R5 (4) | The gate runs before every run. A foreign user means an immediate restore and the end of the session. No other queue of ours runs on aifoundry2 while `pending.json` exists |
| R6 (5), C7 | New risk (§14): the error-return latch in the thermal loop. After every run the clock must read 600 MHz within 3 s, or ABORT-LATCH. The D1 session starts with Z3 set: no EXIT at R0 ≥ 66 means LATCHED, and the session stops |
| R7 (6) | The P-run is UNI32@20 (640 minions, about 68.5 W at 800 MHz). The 73 W cap is kept, with no 90 W exception. At most 3 P-runs, at the end of a session only |
| R8 (7) | Z3 set comes first, at INFO. WARNING is set only after ALIVE is shown (A2's O2 rule) |
| C1 (8) | S = R0 + 2 or more: D1 uses thr* = R0 + 5 (at most 73), K = R0 + 6, S = K − 4. The native branches follow the same rule (§4.1). Edge slope and time since the last heating are recorded per run |
| C2 (9) | A fixed 4-block cycle replaces the shuffle: INT and PER are adjacent in every block, in ABBA order, with B4C and UNI in ABBA (§5.5). P-runs come at the session end, with ≥ 10 min rest after any P-run. Lifted pairs are matched |
| C4 (10) | One statistics reset per run, during the edge wait, and none after t0. It needs a new one-shot reset (`--reset-once-file`). Two development runs with periodic resets check the climb (reported) |
| C5 (11) | L_P (power-adjusted) is reported beside L. P_U is measured in-session (the ADD run). The DIL point uses aifoundry2's own measured couplings (C1m) |
| C6 (12) | Each T-run is one launch. Development picks (N, K − S) so that the trip falls inside the launch. A run with no trip is censored, never chained |
| C8, V2 (13) | C1 becomes C1m: @32 at 600 MHz, a time scale matched to t800, run on a rested card. The aifoundry1-c1 validation is dropped (HP owns that claim) |
| P1, F8 (14) | G4 has a three-way rule: FAIL when the 99% CI lies wholly outside the band, on either side. The band half-width splits the distances to "undiluted" and "none". n_val is sized for that rule (8-16 blocks). "H-max ≥ 0.8" is dropped |
| P2-P6 (15) | G5 is reported only. G6 keeps its two real tests. Z1 tests line content. Z2 is conditioned on uptime. G1's hot hold is a demonstration. G1(e) is dropped |
| F1-F7, P7 (16) | Each mechanism item is split into a source ordering frozen now, host bands frozen now from the retrospective (§2.2), and SP-time bands set in development. G3(a) becomes loop quantisation. G3(c) is restricted to launch-to-first-800. G3(d) is widened to 1.6 s. G2(c) takes the "PUP or ENTER, never neither" form. Uptime is not an anchor: the fit uses OP lines plus an optional marker (DM 36) |
| V1, V3 (17) | "Replication on aifoundry2" is the term, and the owner is asked. Replication may span up to 3 pre-booked sessions. A2 is cited; its TRIG-A definitions are reused, with the fit window narrowed from +1.2 to +0.6 s on the §2.2 evidence |
| B1-B5 (18) | Tonight: Z2 on aifoundry3, the Z1 watcher, the retrospective (done), C1m, and a native session only if a cool window opens. D1, if approved, is T-only. The tooling reuses A2's code as a copy; about 3 h |
| #19, #20 | §13 adds the findings-14 correction ("at 65", with the counts). No host builds or reductions on aifoundry2 during a session |

---

## 2. What is fixed before any run

### 2.1 The governor the cards run (0.20.0; TPM line numbers; re-checked by the critique)

**Input.**
- The governor reads `floor(Σ floor(T_i) / n)` over the 34 minion-shire sensors, with faulted sensors dropped, and
  compares it strictly: `> thr`.
- There is no per-sensor, maximum or interrupt path.
- The PMIC alarm reads a register that has read 0 in all 281,951 V3 samples.

**Entry.** On any dm pass (133 ms quiet, 156-162 ms under a 10 Hz sampler) where the mean is > thr, the state is < 4
and APM is on, the SP does two things, with **no busy test** (TPM:668-679):
- it logs CRITICAL `Thermal throttle down event, current temperature: X, threshold: thr` (ENTER);
- it sets state 4.

**Thermal loop** (TPM:2289-2383).
- Reduce one VMIN-LUT point, then `vTaskDelay(1000 ticks)` (0.40 s), then re-read the mean and the threshold
  (TPM:2316), while mean > thr.
- A reduce at 600 MHz is a silent no-op (TPM:1788-1791).
- **Exit.** It logs CRITICAL `Thermal idle state event, current temperature X, threshold thr` (EXIT), sets state 1 and
  goes to 600 MHz (TPM:2366-2374, 2446-2449).
- While the loop runs, the power branch is gated out (TPM:845).
- **Error returns.** A failed PMIC-average read (TPM:2323-2329) or a failed operating-point change (TPM:2335-2341)
  `return`s without leaving state 4. The governor then latches at its current clock (§14).

**Power branch** (TPM:844-887; loops TPM:2171-2267).
- Idle with state ≠ 0: PIDLE, then state 0.
- Busy, P_inst > TDP and state < 3: PDN. The loop reduces with no delay until the PMIC average is < 1.05·TDP, or the
  clock reaches 300 MHz. There is no re-climb until idle or a thermal episode.
- Busy, P < TDP and state < 2: PUP. It climbs with no delay to 800 MHz, or until avg > TDP.
- Every real clock change writes a binary `TRACE_TYPE_POWER_STATUS` record and a CRITICAL `new OP` line
  (TPM:1868-1875).

**Latency.** The SP learns that a kernel started or ended at a master-minion heartbeat, about 1.05 s apart.
- E10: the first change came 0.14-2.01 s after a launch (median 0.73, n = 31).
- The idle reset came up to 1.39 s after a block end (n = 15, median 1.02; `dvfs.json .governor_days`).

**The pages' source differs** (HEAD `353f20e`, DVFS page §1):
- one point per pass, with no loop and no delay;
- the thermal branch acts only while busy;
- it re-climbs when P < TDP.

### 2.2 What the existing data already show (the retrospective; zero card time)

**Data.** Eight committed aifoundry2 sessions: `P5/docs/reports/data/2026-09-21-horace-aifoundry2/cold1,cold2` and
`2026-09-23-reruns-aifoundry2/hotline-pass2,3,4` and `relay-pass1,2,4`.
- 10 Hz host telemetry, with no statistics resets (`since_reset_ms` −1 or absent).
- 275 clock changes: 50 × 600→800, 35 × 600→700, 35 × 700→800, 70 × 800→700, 70 × 700→600, 15 × 800→600.
- The counts agree with `dvfs.json .governor_days`.

| # | Observation | Count | 0.20.0 predicts | HEAD predicts |
|---|---|---|---|---|
| RA | **Climbs.** 700 is seen in one sample (the dwell is at most 0.11 s), or not at all | 35 one-sample, 50 with no 700 sample, 0 with two or more (85 climbs) | a one-call climb: the two OPs about I2C-time apart | a 700 dwell of one pass (0.156 s). At 10 Hz, 700 is seen in every climb, and in two samples in about 56% |
| RB | **Descents.** The 700 dwell in 800→700→600 | 0.4-0.5 s in 69 of 70 (one at 0.1 s) | one loop period, 0.40 s plus the body | 0.13-0.16 s |
| RC | **Down-step lag.** From the first host sample in the same 800 MHz span with the mean ≥ 66, to the 800→700 step | 0.1 s (32), 0.2 s (22), 0.3 s (9). In 7 the step came before any host 66. None later than 0.3 s | within one pass of the SP's mean first reading ≥ 66 | the same |
| RD | **Up-step reading.** The host reading before an up-step, 23 Sep (hunting) | 65 (90), 66 (11), 64 (1). None at ≥ 67 (n = 102) | exit at a mean ≤ 65, then a PUP within one pass (a reading of 66 at the host sample is staleness) | HEAD's thermal branch never lowers at ≤ 65, and re-climbs on P < TDP |
| RE | **After a 700→600 step,** the time to the next up-step | 0.1-0.2 s (9), 0.5-0.6 (20), 0.8-1.1 (5), 1.3-1.4 (8), 1.8 (1), 3.3-4.1 (3), 7-41 s (19, the next launch), none (5) | k loop periods of about 0.45 s after the reduce (the silent no-ops at 600) | a climb within one pass after the mean falls |
| RF | **A windowed high at 800 MHz** | 0 of 361 samples at 800 have a valid windowed high | — | — |
| RG | **Idle spread,** high − mean, 57 idle samples at a mean of 68 (A2's documentation data) | 1 °C (33), 2 °C (24) | — | — |

**What this settles.**
- RA and RB already separate the two sources on aifoundry2 at the host level. RA alone excludes HEAD's climb: 50
  climbs with no 700 sample cannot occur with a one-pass dwell.
- RC is what H-mean predicts. RF says why it cannot exclude H-max: no high was recorded.
- RD corrects findings 14's "lift below about 68 °C": the lift comes at 65, or at 66 by one host sample.
- RE is the loop quantisation that critique F1 described.

**How these data are used.**
- They are development data.
- The host-level bands of G2 and G3 (§6) are frozen now from them.
- A replication in a new session tests the same bands.
- SP-timed bands (ENTER → OP, EXIT → OP) need rings with clock changes, which only a new session gives. They are set
  in development.

### 2.3 The cards tonight

| Card | Governor | Rest | Role in DV2 |
|---|---|---|---|
| aifoundry2 (fw 1.3.1) | free. TDP 65 W, threshold 65. At a reading ≥ 66 it sits in the thermal loop, silent (A2 probe 16:51: SILENT) | 67 at 16:51, 66 at 18:52. Over the week 62-74: 62 at 14:37 and 69 at 14:49 on 27 Sep | development: C1m and Z1 tonight; NAT if a cool window opens; D1 only on the owner's yes. Replication in later sessions |
| aifoundry3 (fw 1.3.1) | TDP 0 from a lab service: a stuck POWER_DOWN loop, 600 MHz in every sample, SP pass 224 ms | 53 | Z2 read only, tonight after R3 (free since about 22:20) |
| aifoundry1-c1 (fw 1.2.0) | never above 600 MHz in 359,657 samples (inactive: APM off, or latched) | 56-64 | not tonight (HP V0 and validation). After 08:00 on 28 Sep: Z2 only, if the owner gives the slot |
| aifoundry1 card 0 | — | — | never addressed |

### 2.4 Heat numbers the predictions use (`review-heat.md`; `dv2_sim.out`; `a2_heat_sim.out`)

- **800 MHz adds 6.9 W** at idle (`vf.json`, 21 Sep). This is re-measured in-session by ADD, because leakage grows
  with temperature.
- Random fp32 costs 26 mW per minion at 600 MHz, and 1.9× that (49 mW) at 800.
  - Board power at 800 MHz is about 35.3 + 0.049·N W at 66 °C, plus about 1.8 W at 70 °C.
  - N = 128: about 43 W. N = 192: about 46 W. UNI32@20 (640): about 68.5 W.
- **Time to trip** at 800 MHz from S = K − 4:
  - the model gives 13-18 s (N = 128) and 7.4-11 s (N = 192);
  - E10's calibration (the model runs 2-3× slow in the first seconds) gives about 4-7 s and 3-5 s.
- **C1m's time scale** (@32 at 600 MHz, 13.3 W): from rest 66-67, the model takes 5-13 s to rise 3-4 readings. That
  matches t800.
- **Heat-only placement on aifoundry3** (`HP/dev/dev-r3.json`, 600 MHz):
  - L(PER16@32 / INT16@32) = +0.48 [0.41, 0.55] (tier L);
  - L = +0.58 on the short tier;
  - L(UNI32@16 / INT16@32) = +0.34 [0.24, 0.44];
  - PER drew 0.21 W less than INT, CI [−0.38, −0.05].
- **Dilution with aifoundry3's couplings** (`dv2_sim.out`): L(PER/INT) at 800 MHz ≈ 0.24 (N = 128) and 0.29
  (N = 192). This is replaced at the freeze by aifoundry2's own C1m couplings and the in-session P_U.

---

## 3. Theories (the summary will report which survive)

| # | Theory | Items |
|---|---|---|
| TH1 | **The governor acts on the integer mean of the 34 shire sensors**, not on the hottest sensor, and not on power below the TDP. A shire can sit ≥ 2 °C above the threshold at full clock | G1 (T, X, H) |
| TH2 | **The cards run the 0.20.0 governor, not HEAD.** The signs: the 0.40 s blocking loop, the one-call climb, the exit to 600, no busy test, and no re-climb after a power drop | G2, G3, G7, Z3 (and RA, RB, RE already) |
| TH3 | **No hysteresis.** Entry at reading thr + 1, exit at reading thr | G2-U, G2-E |
| TH4 | **Launch and end latency come from the MM heartbeat** (about 1.05 s) plus one pass | G3-L, G3-I |
| TH5 | **Placement delays the first throttle through the mean, diluted.** L800 ≈ ln((κ_U·P_U + P_x) / (κ_U·P_U + κ_P·P_x)), where κ_P = e^−L600(PER/INT) and κ_U = e^−L600(UNI/INT) come from C1m, P_U from ADD, and P_x from the run | G4, C1m, ADD |
| TH6 | **The delay buys a small amount of work** (reported only) | G5 |
| TH7 | **Recovery is thermal, and the loop blocks the idle reset** | G6 |
| TH8 | **Card states.** aifoundry3 is stuck in its power loop (all residencies 0). aifoundry2 is in the thermal loop when warm, not latched. **Decided by** an EXIT line: Z3's set in a D1 session, a natural dip seen by Z1, or a NAT probe that climbs. aifoundry1-c1: POWER_UP residency against uptime | Z1, Z2, Z3 |

---

## 4. Session branches, global state and safety

### 4.1 Branches (decided on R0, the session's first 1 s reading after the gate)

K is the trip reading (thr + 1). S is the start edge, the falling S+1 → S of the host mean. The rule S ≥ R0 + 2
keeps the edge out of aifoundry2's slow last degree (critique C1).

| Branch | R0 | thr | K | S | Items possible |
|---|---|---|---|---|---|
| NAT-4 | ≤ 60 | 65 (native) | 66 | 62 (K − 4) | G1, G4, ADD, G6; G7 at the end |
| NAT-3 | 61 | 65 | 66 | 63 (K − 3) | G1, G4, ADD, G6 |
| NAT-2 | 62 | 65 | 66 | 64 (K − 2) | G1, ADD; G4 reported only (t800 about 2-3 s) |
| NAT-1 | 63-64 | 65 | 66 | 65 (the 66 → 65 edge) | G1-H and G1-X only, ADD |
| **D1** (owner's yes only) | 62-68 | thr* = R0 + 5 (≤ 73) | R0 + 6 | R0 + 2 (K − 4) | all G items. It replaces NAT-2 and NAT-1 when approved |
| LOOP | ≥ 66, no D1 | 65 | — | — | C1m (heat-only; the governor pins 600 MHz); Z reads |
| WARM | 65, or ≥ 69 under D1 | — | — | — | Z reads only |

- **Probe.** A2's R0 probe (one 2 s UNI32@4 launch with no sampler, and dumps before and after) must say ALIVE before
  any NAT branch runs. If it says SILENT at R0 ≤ 64, that is evidence of a latch: record it, run no heat, and alert the
  owner.
- **The gate on each edge.** The edge of every run is gated on the branch still holding. If the rest drifts so that the
  mean cannot fall to S within 300 s twice in a row, the session ends.

### 4.2 Global state: found, set, restored, verified (one table in every session log)

| State | Found (expected) | Set by DV2 | Restored | Verified by |
|---|---|---|---|---|
| software threshold | 65 | only in D1: thr* through T2's interlocked path | 65 at the end, by the trap, or by the watchdog | `ettelem config` `temp_threshold_c`; Z1 every cycle |
| SP log level | INFO (V3 and HP left it) | WARNING, only after ALIVE is shown (A2's O2 rule) | the level found | a dump after the restore |
| SP statistics trace | disabled (every `--reset-ms` sends control 2) | not changed: control 2 keeps it as found | — | recorded |
| TDP, APM, clocks, voltages | 65 W, on, governor-owned | never | — | `ettelem config` at the start and end |
| governor state | loop (warm) or idle | no command. Only heat and the threshold move it | — | Z3 lines, the post-run clock check |

### 4.3 D1: the question for the owner (to relay verbatim; no D1 until the owner answers yes)

> DV2 asks one decision. May aifoundry2's software thermal threshold be raised from 65 °C to (rest reading + 5),
> at most 73 °C, in SP RAM only, for one development session of at most 90 minutes of card time, and restored to 65
> at the end?
>
> **What it buys.** Clock-step experiments, meaning your two questions (average or one shire; placement and time to
> throttle), on a card that otherwise allows them only when it rests at 64 °C or less by itself. Tonight it rests at
> 66-67.
>
> **Risks.**
> 1. If a firmware error hits inside the thermal loop, the governor can latch at 700 or 800 MHz until an SP reset. That
>    has happened 0 times in 275 clock changes so far. The session checks the clock after every run. If it is not back
>    at 600 MHz, the session stops all heat, restores 65 and alerts you.
> 2. If the session dies, a watchdog restores 65 within about a minute, under the card lock. If another user holds the
>    card, it does not force: it waits and alerts you.
> 3. Every result is labelled "at a software threshold of N (raised from 65), one card".
>
> **Without your yes:** no threshold change. Clock-step work waits for a natural cool window.
>
> **Also:** (a) Governor items can be repeated only on aifoundry2, since no other card has a free governor. Is a
> replication on aifoundry2 in later sessions acceptable in place of validation on another card? (b) Native sessions
> set the SP log level to WARNING (the boot default) only after the card shows it is out of its thermal loop, and
> restore it at the end. That is your O2 rule from the A2 session. Say no to keep INFO; then the tests that need SP
> lines are not registered. (c) aifoundry1-c1: may a read-only residency query (Z2, about 1 min) run after 08:00 on 28
> Sep, after the heat validation?

### 4.4 Safety (every session; enforced by the dv2 scripts)

- **Gate.** `et-who`, `who` and the process scan (lib.sh `others_present`, `ours_running`) run before the session,
  **before every run**, and between launches (`hp_between`). The card lock (`flock /run/lock/etsoc-shire0.lock`) is
  held for the whole session.
  - A foreign user or device process means the session ends at once.
  - In D1 the threshold is restored first, under our held lock.
  - The scripts refuse to start while `pending.json` exists without a live session, or while any queue of ours runs on
    aifoundry2.
- **Caps** (hplib's watcher, unchanged):
  - stop the heater and the session at a mean or high ≥ 90;
  - end the run after 2 samples at mean ≥ 80, high ≥ 85 or board ≥ 73 W. This holds in every run kind; there is no
    P-run exception.
- **Process limits.**
  - Every device process ≤ 10 s (`hold10`).
  - Chains of lifts plus the run's launch ≤ 4 × 7 + 8 s.
  - C1m chains ≤ 3 × 7 s.
  - Everything is ≤ 150 s with telemetry running.
- **Post-run clock check (R6).** After every heating run, the host samples must read 600 MHz within 3 s of the kernel
  end, and stay at 600 for the rest of the tail. Every dump is also scanned for `failed to set operating point` and
  `failed to get soc power`.
  - On a failure: **ABORT-LATCH**. Stop all heat, restore 65 if it was raised (harmless either way), end the session,
    and write `ALERT-LATCH` for the orchestrator to relay to the owner.
  - Never reset the card.
- **Threshold restore (D1 only; T3).**
  1. `pending.json` ({found: 65, set: thr*, level_found, session pid, t}) is written before the set command.
  2. The set goes only through `ettelem-dv2 threshold set N`, which refuses unless `DV2_THR_OK=1`, `pending.json`
     exists and 66 ≤ N ≤ 73.
  3. It is read back at once. A mismatch restores 65 and aborts.
  4. An EXIT trap restores the threshold and the level on normal exit and on SIGTERM.
  5. A detached watchdog (`setsid`, started before the set) polls the session pid every 30 s. When the pid is gone and
     `pending.json` remains, it runs the gate, takes the lock with a blocking `flock -w 600`, restores 65 and the level,
     verifies them and deletes `pending.json`. If the gate fails or the lock stays held by someone else, it **never
     forces**: it writes `ALERT-THRESHOLD`, leaves the card alone and retries every 5 min.
  6. Z1 reads `temp_threshold_c` every cycle. A value ≠ 65 with no live session starts the same restore path. A value
     ≠ 65 with no `pending.json` means someone else changed it: alert only, never touch.
  7. The threshold is never set on aifoundry3 or aifoundry1.
- **Host.** No builds, no reductions and no heavy jobs on aifoundry2 while a session runs, because the host shares the
  card's air. `ettelem-dv2` is built before the first session.

---

## 5. Run kinds, placements and order

### 5.1 T-run (the first-trip run: G1, G4, G6, G2/G3 events)

1. Gate check. Start the 10 Hz sampler with **no periodic reset**, plus the watcher with the caps.
2. If the mean reads < S + 1: lifts. These are 7 s UNI32@4 launches, at most 4, and discarded. The run records
   `lifted`.
3. **Reset.** While the mean reads S + 1, touch the sampler's `--reset-once-file`. This gives one statistics reset, so
   from here the high and the SP's max are "since this reset", and monotone while heating.
4. Wait for the falling S + 1 → S edge (cap 300 s, else void). Record the edge slope (dT/dt over the 20 s before) and
   the time since the last heating.
5. **One launch** of the run's placement: randn fp32 FMA, `--seconds 7` (development may choose 8: PREREG-DEV DEV-2),
   under `hold10`, with a stop file that the watcher writes 2.0 s after the first host sample at 700 MHz. The trip must
   fall inside the launch; otherwise the run is censored at the kernel end.
6. A 10 s tail. Stop the sampler, **then** `sptrace` (a BAR read), then the post-run clock check.

### 5.2 ADD run (the clock's uniform adder P_U, per session)

- One T-run shaped launch of **1 shire × 1 minion** (mask 0x00000001, per-shire 1) from the session's S edge.
- P_U = mean board W over [t_up + 0.3, t_up + 2.3] s (at 800) minus the mean over [t0 − 2.0, t0] s (idle, 600).
- The 1-minion switching (≤ 0.05 W) is ignored.
- Two ADD runs per session: the first and the last run of the session.

### 5.3 P-run (G7; optional; only at the end of a session; at most 3)

- UNI32@20 (640 minions, mask 0xffffffff, per-shire 20): about 68.5 W at 800 MHz.
- One 7 s launch from the S edge. The sampler runs with no reset at all.
- The 73 W cap applies.
- Rest ≥ 10 min after each P-run.
- Development confirms 66-72 W in the first 0.3 s at 800 MHz, or drops G7.

### 5.4 C1m run (heat-only placement at the pinned floor; LOOP branch only)

- **Placements.** INT16@32, PER16@32 and UNI32@16: 512 minions each, about 13.3 W at 600 MHz.
- **Start.** The falling edge E + 1 → E, with E = R0 + 2. The governor is in its loop throughout, so every sample
  must read 600 MHz, else the run is void.
- **Statistic.** t_c = the time from t0 to the first sample with a mean ≥ E + 4. That is the same 4-reading rise as G4.
- **Launches.** 7 s launches under `hold10`, at most 3, censored at the chain end. The launch gaps are identical across
  placements, and the loop keeps the clock pinned across them.
- One statistics reset per run at E + 1, as in 5.1.
- **Order.** 4 blocks in the rows (INT, PER, UNI), (UNI, PER, INT), (PER, INT, UNI), (UNI, INT, PER): each placement
  first or last twice, and INT/PER in ABBA order.

### 5.5 T-block order (a fixed 4-block cycle, repeated)

| Block mod 4 | Order |
|---|---|
| 1 | B4C@32, INT, PER, UNI32@4 |
| 2 | UNI32@4, PER, INT, B4C@32 |
| 3 | PER, INT, UNI32@4, B4C@32 |
| 4 | INT, PER, B4C@32, UNI32@4 |

- INT and PER are adjacent in every block.
- INT comes first in blocks 1 and 4, PER in blocks 2 and 3 (ABBA).
- The pair is preceded by a run in blocks 1 and 2, and by the rest in blocks 3 and 4, once for each order.
- B4C comes before UNI in blocks 1 and 4, and after it in blocks 2 and 3.
- INT and PER are INT16@N and PER16@N, with N fixed by development (8 or 12 per shire; 128 or 192 minions).
- Rest ≥ 5 min between blocks, and ≥ 10 min after any P-run.
- A G4 pair counts only if both runs are lifted or neither is.

### 5.6 Placements (`W/tools/claims-v3/hp/placements.json`, copied to `dv2/placements.json`)

- INT16 0x6477f412, PER16 0x9b880bed, B4C 0x00606000, UNI32 0xffffffff.
- New entries: INT16@12, PER16@12, UNI32@20 and ADD1 (0x00000001 @1).

---

## 6. Items

Each item gives:
- the source ordering, frozen now;
- the host bands, frozen now from §2.2;
- what development sets.

**Outcome words** are V3's: PASS, FAIL and INSUFFICIENT. "Not observable" counts as INSUFFICIENT.

### Z-items (read-only; no global change)

**Z1 WATCH (aifoundry2, all night; TH8, and the cool-window detector).**
- **Every 10 min:**
  1. the gate, then `flock -n` (skip the cycle if the lock is held);
  2. `ettelem sptrace` (a BAR read, which adds no lines);
  3. `ettelem-dv2 residency` and `uptime`;
  4. `ettelem config` (threshold check, §4.4);
  5. one 1 s `ettelem sample --reset-ms 1000`.
- The host logs `sensors -j` every 60 s. About 5 s of card time per cycle.
- **Predictions (P4 form)**, over dumps whose overlap with the previous dump is shown:
  - (a) every EXIT prints X ≤ thr, and every ENTER prints X = thr + 1;
  - (b) every EXIT on an idle card is followed by a PIDLE within 0.3 s (SP);
  - (c) no `new OP` line appears in an interval with no kernel of ours;
  - (d) THERMAL_DOWN cumulative changes between two cycles only if the dumps between them hold an EXIT.
- **Pass.** (a)-(d) hold in 100% of the lines seen. One violation fails.
- **Outputs.**
  - A reading ≤ 64 raises COOL. The NAT auto-start (PREREG-DEV run 6) evaluates it.
  - An EXIT seen with no heat of ours decides TH8 for aifoundry2 (LOOP, not LATCHED).
  - The ambient log is a covariate only.

**Z2 RESID (aifoundry3 tonight; aifoundry2 in every Z1 cycle; aifoundry1-c1 after 08:00 only with the owner's slot).**
- `DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES` (29) with the raw 0.20.0 states 2-6 (0.18.0 uses the same numbering).
- `DM_CMD_GET_MODULE_UPTIME` (30), which has minute resolution.
- `ettelem config`.
- **Predictions.**
  - aifoundry3: POWER_DOWN = THERMAL_DOWN = POWER_UP = SAFE = 0 (the stuck power loop never exits).
  - aifoundry2: POWER_UP > 0 if the SP booted before 21 Sep 06:46 (E10's climbs). THERMAL_DOWN is unchanged between
    cycles whose dumps hold no EXIT.
  - aifoundry1-c1: no prediction (a discriminator). POWER_UP = 0 means APM was off from boot, or the governor latched
    before any climb. POWER_UP > 0 means it climbed and was disabled later.
- **Rule for aifoundry1-c1.** The tool refuses unless `ET_DEVICES=1` and `V3_DEVICE=1` are set and the device's PCI
  address matches card 1's as recorded in hp's aifoundry1 configuration. It runs no heat, so it needs no card-0
  guard.

**Z3 THR-RT (D1 only; TH2, TH8).**
- **Set.** At R0 ≥ 66, an EXIT `current temperature R, threshold thr*` within 2 s, then a PIDLE.
  - No EXIT within 2 s means LATCHED: restore 65, stop, no G work.
  - At R0 62-65 the card is not in the loop. No line is expected; the probe decides ALIVE.
- **Restore** at a rest ≥ 66: an ENTER `current temperature R, threshold: 65` within 2 s, **on an idle card**. That is
  the missing busy test, directly.
- Record the THERMAL_DOWN jump, which dates the last idle ENTER.

### G-items (aifoundry2 only)

**Standard per-run observables** (A2's TRIG-A definitions, reused; host 10 Hz; high = since the run's one reset):
- `t_up`: the first sample at 800 MHz;
- `t_m`: the first sample with the mean ≥ K;
- `t_spm`: the first sample with `sp.minion_c` max ≥ K;
- `t_hi`: the first sample at 800 with the high ≥ K;
- `t_hi2`: the first sample at 800 with the high ≥ K + 1;
- `t_down`: the first one-point 800 → 700 step. A single 800 → 600 change is an idle reset and is excluded.
- From the ring: ENTER's X and its host-mapped time.

**G1 TRIG: what the step compares (TH1; the owner's first question; A2's TRIG-A and TRIG-B are the frozen
predecessors).**
- **G1-T (timing).**
  - A run is separating if (a) t_m − t_hi ≥ 1.5 s, or (b) the high already reads ≥ K + 1 at t_up and the clock holds
    800 for ≥ 0.5 s.
  - It fits H-mean if t_down ∈ [t_m − 0.3, t_m + 0.6] s, or under (b). It fits H-max if t_down ∈ [t_hi − 0.3,
    t_hi + 0.6] s.
  - The upper bound is narrowed from A2's +1.2 s on RC: 63 of 63 measurable lags were ≤ 0.3 s.
  - **PASS** if ≥ 6 separating runs over ≥ 3 blocks, ≥ 80% fit H-mean, and ≤ 1 fits H-max. **FAIL** if ≥ 50% fit
    H-max. Otherwise INSUFFICIENT.
- **G1-X (printed value; registered only at WARNING).**
  - Every ENTER prints X = K.
  - In separating runs the host high within ±0.5 s of ENTER is ≥ K + 1.
  - **PASS** if ≥ 5 separating ENTERs, all print K, and ≥ 90% show the high ≥ K + 1. **FAIL** if any ENTER prints
    X ≥ K + 1 while the host mean reads ≤ K − 1.
- **G1-H (hot hold; a demonstration, reported).**
  - Per run, report the maximum of (high − thr) at samples where the clock reads 800 and stays at 800 for ≥ 1.0 s
    after.
  - It counts only with a rise of ≥ 2 °C in the high since t0. Development checks the idle spread against RG.
  - This is the owner-facing sentence: "a shire read X °C above the threshold while the clock held 800 MHz".
  - One hold at ≥ thr + 2 is inconsistent with H-max. It is reported, not scored.
- **Pages.** Spatial brief (#bottleneck); DVFS §1 and its terms box; the hub; findings 14 and 19.

**G2 STEP (TH2, TH3).**
- **Host bands, frozen now from §2.2.** Each holds on all runs of the session, ≥ 20 events.
  - G2-C (climbs): ≥ 95% show 700 in at most one sample, and ≥ 25% show no 700 sample (RA: 100%, 59%). HEAD: 0% with
    no 700 sample.
  - G2-D (descents): the 700 dwell of an 800→700→600 pair lies in [0.3, 0.7] s in ≥ 90% (RB: 69 of 70). HEAD:
    0.13-0.16 s.
  - G2-U (up-steps while hunting): the preceding reading is ≤ thr + 1 in 100%, ≤ thr in ≥ 80%, and never ≥ thr + 2
    (RD: 102 of 102, 91 of 102, 0).
- **SP orderings (frozen now; registered at WARNING).**
  - G2-E: every EXIT while a kernel runs is followed within one pass by a PUP (then the climb OPs) or an ENTER, never
    by neither (F5).
  - G2-X: an EXIT at 700 MHz is followed by OP 700→600, never 700→800. That is the exit to the boot point.
  - G2-N: no down-step at a host mean ≤ K − 2.
  - SP-time bands (EXIT → OP, the two climb OPs, ENTER → OP) are set in development (PREREG-DEV D6), and PASS within
    them.
- **Pass.** Each sub-item PASS/FAIL on its own rule. FAIL if ≥ 10% of events deviate, or on one violation of an
  ordering. INSUFFICIENT below the event count.
- **Pages.** DVFS §1 (#the-loop-as-built, rewritten for 0.20.0) and §2 (#attrib: the "unattributed" steps are loop
  exits); DVFS §8 Q1 and Q2; findings 14 and 16.

**G3 LAT (TH2, TH4).**
- **G3-Q (loop quantisation).** Within an episode, every OP and the EXIT fall at k × P_loop + body after the ENTER
  (SP). P_loop and the body band are set in development from the rings. The source says 1000 ticks = 0.401 s. Host
  form: RE's clusters.
- **G3-L (launch → first 800, host).** Median ∈ [0.4, 1.0] s, and all ≤ 2.2 s (E10: 0.14-2.01 s, median 0.73).
- **G3-I (kernel end → 600, with no episode running, host).** ∈ [0, 1.6] s (E10: ≤ 1.39 s). Inside an episode there
  is no PIDLE before the EXIT (at WARNING).
- **G3-H (heartbeat, SP).** The gaps between a launch's PUP and its end-of-launch PIDLE cluster at k × [1.00, 1.10] s.
  Development confirms the period.
- **SP clock → host** (not an item).
  - A lower-envelope fit of OP lines against the first host sample showing that clock, plus an optional DM 36 marker
    at run start and end (it writes one power-status record and changes nothing: TPM:2087-2112).
  - `GET_MODULE_UPTIME` is not an anchor: it has minute resolution.
  - A residual > 100 ms voids that session's SP-timed parts.
- **Pages.** DVFS §1 and §2 (#gov-sum); hub timing table; findings 16.

**G4 PLACE-D: does placement delay the first throttle? (TH5; the owner's second question).**
- **Statistic.** Per block, L = ln(t800(PER16@N) / t800(INT16@N)).
  - t800 = SP (first ENTER − the climb's last OP) when the ring holds both; else host (t_down − t_up).
  - Censored runs enter as the kernel end (flagged). A block with both runs censored is dropped.
- **Also reported.** L_P = L + ln(P_x,PER / P_x,INT), where P_x = board W over [t_up + 0.3, t_up + 2.3] minus ADD's
  800 MHz board W. The verdict is given on L and on L_P.
- **Prediction (theory; computed at the freeze from development inputs, never from development's L).**
  - L_pred = ln((κ_U·P_U + P_x) / (κ_U·P_U + κ_P·P_x)), with κ_P, κ_U from C1m, P_U from ADD, and P_x the mean of INT
    and PER.
  - The prior, with aifoundry3's couplings and 6.9 W: 0.24 (N = 128), 0.29 (N = 192).
  - The alternatives: **undiluted**, L = L600 (C1m's PER/INT); and **none**, L = 0.
- **Band.** L_pred ± b, with b = min(0.15, (L600 − L_pred)/2, L_pred/2). If b < 0.05, G4 is registered as a sign
  test only: PASS if the CI lies wholly above 0, FAIL if it lies wholly within ±0.05.
- **Rule** (A2's precedence form, both sides):
  - **PASS** if the 99% CI of the block mean lies wholly inside the band;
  - **FAIL** if it lies wholly outside the band, on either side;
  - INSUFFICIENT otherwise.
- **n_val.** The smallest n in [8, 16] with t(0.995, n−1)·SD_dev/√n ≤ b. If n = 16 still misses, n_val = 16, and the
  expected power is stated in PREREG-DV2.
- **Assumption stated.** Linear superposition carries the ratio from @32 (C1m) to @8 or @12. HP's LIN item was never
  tested.
- **Pages.** heat-per-mm (a new section); DVFS (a new §, "Where the heat is placed"); findings 20; a chip-diagram
  annotation; Horace §6.

**G5 WORK (TH6; reported only).** W-runs (four launches of the pair, 30 s) are not in tonight's plan. If a later
session has time after its T-blocks, it reports work(PER)/work(INT) with its CI. G, the clock trace's mean over 600
MHz, is labelled descriptive arithmetic, not a comparison with a pinned run.

**G6 REC (TH7).**
- G6-M: the model's t_rec (aifoundry2's model from the run's start, measured load power and duration) lies within ×2
  of the measured EXIT time in ≥ 70% of runs.
- G6-B (at WARNING): no PIDLE between the kernel end and the EXIT (100%), and a PIDLE ≤ 0.3 s (SP) after the EXIT
  (≥ 90%).
- t_rec itself is reported.
- **Pages.** DVFS §1; power-temperature §2; the energy manual.

**G7 PWR (TH2; optional).**
- (c) is frozen now: after the PDN, no OP above 600 until an ENTER or the kernel end, in ≥ 90% of P-runs. HEAD
  re-climbs at about 50 W < 65 W.
- (a) PDN after the climb and (b) the two-step spacing get bands set in development (F6).
- At most 3 P-runs per session.
- **Pages.** DVFS §3 (#the-same-firmware-on-three-cards) and §1.

**C1m PLACE-600 (development input for TH5; reported).**
- L600(PER/INT) and L600(UNI/INT) on aifoundry2, with their CIs and power (L_P), from 4 blocks.
- **Reported transfer check** against aifoundry3's 0.48 [0.41, 0.55]. Not registered: HP owns the cross-card claim,
  and DV2 reads none of HP's validation data before its freeze.
- **Pages.** heat-per-mm (a third card's ratio); spatial brief.

**Dropped.** G8 CORR (not tonight). G1(e) (cannot fail). "H-max ≥ 0.8" in G4 (not derived at @8).

---

## 7. Why these runs separate the theories

**Trigger.**
- B4C@32 puts 1.6 W of 800 MHz switching on each of 4 central shires, so its high rises within about 1-2 s. The mean
  needs about 4-7 s to reach K.
- H-mean and H-max therefore put the step seconds apart in the same run (G1-T).
- The printed X shows which number was compared (G1-X).
- A hold at ≥ thr + 2 is impossible under H-max (G1-H).

**Placement.**
- INT16@N and PER16@N have equal minions and nearly equal power (L_P corrects the rest). Only where the heat lands
  differs.
- C1m measures the pure placement effect on the same card, and ADD the uniform adder.
- So the diluted, undiluted and null outcomes are three separate numbers.

**Source.** RA and RB already separate 0.20.0 from HEAD at the host level. G2-E, G2-X, G3-Q, G7(c) and Z3's idle ENTER
add SP-level signatures.

**A raised threshold as a stand-in** (D1 only, if approved).
- The comparison, loop and branches are unchanged, and the constant is re-read every pass (TPM:668, 2316).
- The geometry (S = K − 4) is the same as NAT-4.
- Leakage is about 1.8 W higher at 70 than at 65. Absolute bands carry that; ratios and timings do not.

---

## 8. Tonight, in outline (the exact list is PREREG-DEV §4)

1. **Now to about 00:30, no card.** Build T2 (ettelem-dv2) and T5 (the watcher). Dry tests with V3_DRY=1.
2. **About 00:30, aifoundry3.** Z2, read-only, about 1 min. Only `tools/claims-v3/dv2/` is copied to `~/nekko`, and
   `build/ettelem-dv2` is built there. `hp/` and `lib.sh` there are never touched.
3. **About 00:40 to 08:00, aifoundry2.** Z1 every 10 min. The host sensor log every 60 s.
4. **00:30-02:30, no card.** T4 (the session script, a copy of A2's code plus the fixes). Dry tests of every branch,
   plus the SIGKILL and latch scenarios.
5. **About 02:30-03:40, aifoundry2, LOOP branch only.** C1m development, 12 runs. It is skipped if Z1 saw a reading
   ≤ 64 in the previous 60 min.
6. **About 03:40 to 07:45, aifoundry2.** A NAT session auto-starts at the first Z1 reading ≤ 64 that the probe confirms
   ALIVE. At most one session tonight, ≤ 60 min of card time.
7. **Only on the owner's yes, aifoundry2.** One D1 development session: T-only blocks, ADD, and P at the end,
   ≤ 90 min of card time, ending by 08:00.
8. **aifoundry1-c1.** Nothing tonight.

T1 (the ring parser) and T6 (the reducer) do not block card work. Dumps are kept raw.

---

## 9. Tooling (a new `W/tools/claims-v3/dv2/`; `hp/`, `hp/a2/`, `lib.sh` and `queue.sh` untouched)

| # | Tool | Built from | Test before any card use |
|---|---|---|---|
| T1 | `sptrace2.py`: walks the ring by `payload_size`, with `hart_id`/`type` from the header; decodes `TRACE_TYPE_POWER_STATUS` (28 bytes); patterns for ENTER, EXIT, PUP, PDN, PIDLE, `new OP`, the two error strings, `event received`; dump-overlap coverage | `hp/a2/sptrace_events.py` | the committed rings reproduce the old parser; a synthetic ring with power-status records at odd offsets; first real test on the first dev dump with a clock change |
| T2 | `ettelem-dv2`: `residency` (raw states 2-6), `uptime`, `marker` (DM 36), `threshold get`, `threshold set N` (interlocked, §4.4), `sample --reset-once-file F` | `hp/ettelem-hp/ettelem.cpp` (its `Dm::get` helper) | build; `--help`; the refusals of the set path; a dry stub |
| T3 | `thr.sh`: set, restore, watchdog, verify (only if D1 is approved) | new | V3_DRY: a normal end, SIGTERM, **SIGKILL** of the session (restore within 60 s), a failed read-back, the lock held by a fake other user (no force, an alert) |
| T4 | `session.sh` + `dv2lib.sh`: the branch table, the probe, the T/ADD/P/C1m kinds, the 4-block cycle, the per-run gate, the one-shot reset, the stop file after the first 700, the post-run clock check and ABORT-LATCH, the O2 level handling | copies of `hp/a2/block.sh`, `hplib.sh`, `hplib.py` (sampler, watcher, caps, edges, lifts, `hp_single`, `hp_probe`, `hp_level_*`) | V3_DRY=1 with the simulator given the 0.40 s loop, the one-call climb, the exit to 600, the 1.05 s heartbeat and a configurable threshold, at `HP_DRY_REST` = 60, 61, 62, 64, 66 and 70; a simulated latch (the clock stays at 800) must end in ABORT-LATCH |
| T5 | `watch.sh`: Z1 cycles, the threshold check, COOL detection, the host `sensors -j` log, the NAT auto-start (enabled only once T4's dry tests pass) | new, with lib.sh's gate | V3_DRY; one real read-only cycle |
| T6 | `reduce_dv2.py`: per-run observables, the SP→host fit, the items' statistics, `--dev` → `dv2-dev.json`, `--val --prereg` → `verdicts-dv2.json` | `hp/a2/reduce_a2.py`, `hp/reduce.py` | synthetic runs with planted effects (H-mean vs H-max, L = 0.24 vs 0.48 vs 0, a 0.40 s loop vs one per pass); the retrospective files reproduce §2.2 |

**Estimate.** About 3 h in total: T2 and T5 about 1 h; T4 about 1.5 h, because most of it is A2's tested code; T1
and T6 about 1.5 h, running after card work starts.

---

## 10. From development to the freeze; replication

- Development (PREREG-DEV) fixes the parameters and bands listed there.
- `prereg_dv2.py` then writes `PREREG-DV2.md`, `prereg-dv2.json` and `PREREG-DV2.sha256`, and records the hash in
  `docs/findings/03-experiments.md` under the new E-number.
- **The freeze needs ≥ 4 development T-blocks** at one branch (D1 or NAT-4/3), **and** C1m **and** ≥ 2 ADD runs. Until
  then, governor items stay in development.
- **Replication on aifoundry2** (the owner is asked; §4.3a):
  - it runs over up to 3 pre-booked sessions until n_val blocks are complete;
  - a block with fewer than its 4 runs is dropped by the frozen rule;
  - no file, binary or parameter changes between sessions; `session.sh` refuses a pass (9xxx) whose hashes differ from
    PREREG-DV2's lock;
  - replication runs under the branch that development used. A NAT development may be replicated under D1 only if
    PREREG-DV2 registers both, with thr-relative bands; D1 results are always labelled.
- **Theory verdicts.** A theory **survives** if every registered item under it passes. It **falls** if any fails.
  Otherwise it is **untested**. The limits are stated: one card and one chassis for governor items, and the branch that
  ran.

---

## 11. Validation, card by card (honest classification)

| Item | Needs the governor? | Development | Test |
|---|---|---|---|
| G1, G2, G3, G4, G6, G7 | yes | aifoundry2 (NAT or D1) | **replication on aifoundry2**, later sessions. No second card has a free governor |
| G2/G3 host bands | yes | the committed 21-23 Sep data (§2.2) | the replication's sessions |
| Z3 | yes | the D1 session's start and end | each D1 replication session |
| Z1 | the idle loop | all night | continues; a prediction per line |
| Z2 | reads state | — (source predictions) | aifoundry3 tonight; aifoundry2 every cycle; aifoundry1-c1 after 08:00 if the owner allows |
| C1m | no | aifoundry2 (development input) | reported only. HP validates the cross-card placement ratio on aifoundry1-c1 |

---

## 12. What each outcome changes on the pages

| Item | If it passes | If it fails | Pages and anchors |
|---|---|---|---|
| G1 | "Throttling reacts to the average of 34 sensors. A shire read X °C above the threshold while the clock held 800 MHz" | "one sensor" (with data) | spatial brief (#bottleneck, lede); DVFS §1 and its terms box ("on-die thermal sensor" → mean of 34); hub; findings 14, 19 |
| G2, G3, Z3 (and RA-RE now) | §1 rewritten for the 0.20.0 loop: 0.40 s steps, exit to 600, then a one-call climb, no busy check, the idle reset blocked | the cards run something closer to HEAD: keep §1 and record the timing | DVFS §1, §2 (#gov-sum, #attrib), §8 (Q1, Q2); findings 14, 16; hub (#firmware-caveat) |
| G4 | "At equal power, perimeter work runs e^L = N× as long at 800 MHz before the first throttle: the heat-only effect diluted by the clock's own uniform P_U W" | undiluted, or none (with the CI) | heat-per-mm; DVFS (a new §); findings 20; chip diagram; Horace §6 |
| G6 | "After a throttle the card needs Z s idle before a kernel can run at 800 MHz; the idle reset waits for the mean" | as measured | DVFS §1; power-temperature §2; energy manual |
| G7 | "The power branch drops with no delay and holds 600 MHz for the rest of the kernel" | it re-climbs (HEAD-like) | DVFS §3, §1 |
| Z2 | aifoundry3 stuck in its power loop; aifoundry1-c1 APM off from boot, or disabled later | the latch reading is wrong: say so | DVFS §3; findings 14; hub TEL-P5 |
| Z1 | aifoundry2's warm rest is inside the thermal loop; the crossings timeline | — | DVFS §1; findings 14 |
| C1m | aifoundry2's own placement ratio at 600 MHz | reported | heat-per-mm; spatial brief |

D1 results carry "at a software threshold of thr* (raised from 65), one card" on every sentence. All clock-dependent
sentences carry "one card, one room".

---

## 13. Page corrections that need no experiment (for the page pass now)

- **B2.** Horace §6, why-low-power §5 and power-temperature §2 say aifoundry1-c1 "was launched warm". It was cool and
  under the TDP (11,446 samples at ≤ 64 °C and 45-63 W), and it never left 600 MHz. Its build is 0.18.0.
- **B3.** The DVFS pseudocode and its terms box should say "the integer mean of 34 truncated shire sensors, `> 65`, no
  hot-spot path". Add the PMIC 75 °C / 75 W alarm, which reads an always-zero register.
- **B4.** aifoundry2 ran at a 91-103 °C mean (high 106) in V3 catalogue pass 11 with no response. Add it as no-trip
  evidence, and flag it against the 90 °C rule.
- **B5.** 01-resources' "PMIC reading" argument is circular.
- **B6-B7.** Qualify aifoundry3's latch reading and the power-branch sentence now. Z2 and G7 settle them later.
- **B8-B12.**
  - findings 16 is stale;
  - E19's command strips `dvfs.json`;
  - the idle-law rms is quoted without its basis;
  - "no run varies the voltage" should read "varies the voltage alone";
  - the hub's "not re-read" caveat;
  - the 3-4% cross-reference;
  - aifoundry2 now rests at 66-67.
- **New (§2.2, critique #19).**
  - Findings 14's "lift below about 68 °C" → "the lift comes at a reading of 65: 90 of 102 up-steps on 23 Sep came
    from 65, 11 from 66 (one host sample stale), 1 from 64, none from 67 or more".
  - The DVFS page may cite RA and RB now as host-level evidence for the 0.20.0 loop, with "one card".

---

## 14. Risks, not established, and rejected routes

**Risks.**
- **The error-return latch** (TPM:2323-2341). A failed PMIC read or operating-point change inside the thermal loop
  leaves state 4 at the current clock until an SP reset, which is forbidden.
  - At 800 MHz the idle card would carry +6.9 W, and so rest much hotter.
  - Rate: 0 in 275 changes.
  - Mitigation: the post-run clock check, ABORT-LATCH, and an alert. Never a reset.
- **POWER_SAFE (5)** is terminal on 0.20.0 if the PMIC alarm fired. It has not, even at 87.8 W (E10) or 145 samples
  ≥ 75 W on 26 Sep. The 73 W cap keeps DV2 away from it.
- **The rest drifts mid-session.** Edges then time out: two in a row end the session, and blocks run short
  (INSUFFICIENT). D1's thr* is set once, at the session start.
- **No cool window tonight.** Then there is no clock-step data unless the owner approves D1. C1m, Z1, Z2 and the
  retrospective still run.
- **The ring at INFO** holds under 1 s under a sampler. G1-X, G2-E/X/N, G3-Q/H and G6-B are registered only when
  WARNING was set (O2).
- **The one-shot reset** is new code. The sampler's `since_reset_ms` must show exactly one reset per run, before t0;
  otherwise the run is void.
- **The periodic-reset effect on climbs** (C4) is untested. DV2 avoids periodic resets during governor action.
  Development reports 2 runs with them.

**Not established (and not tested here).**
- The physical position of each sensor.
- Whether the SP statistics trace is readable.
- What the PMIC alarms compare.
- Why aifoundry2's rest jumps. Z1's ambient log is a first look.
- Superposition across densities (G4's assumption).

**Rejected.**
- Lowering aifoundry2's idle clock or voltage. An off-LUT frequency breaks the step lookup, and it is a global change.
- Toggling APM.
- Raising aifoundry3's TDP (the stuck loop read it once).
- aifoundry1-c1 as a governor card.
- Resets, firmware, driver or fan changes.
- Heating aifoundry2 to provoke a response above the threshold (103 °C, no trip).
- A forced restore past the card lock.
- `dev_mngt_service` for any set.
- A 90 W P-run cap.
- Chained T-runs.

---

## 15. Files

- `DESIGN.md` (this file) and `PREREG-DEV.md` (development: what it fixes, how it decides, tonight's run list).
- `CRITIQUE.md` (the review; its responses are §16 here).
- `dv2_sim.py`/`.out`; `a2_heat_sim.py`/`.out`.
- `retro/`: the §2.2 scripts and outputs.
- Inputs: `review-*.md`; `tpm_may2024.c`; `HP/dev/dev-r3.json`; `W/tools/claims-v3/hp/a2/PREREG-A2.md`.

---

## 16. Responses to the critique (every point)

A = accepted, M = accepted in modified form, R = rebutted.

**§1 Card rules and global state**

- **R1 (A).**
  - D1 is a question to the owner (§4.3), carrying R6's risk.
  - "D1 no" is the plan until a yes.
  - Every D1 result is labelled.
- **R2 (A).** The watchdog runs the gate, waits on the lock (`flock -w 600`) and never forces. When it cannot act it
  alerts and retries.
- **R3 (A).**
  - The watchdog polls every 30 s and restores within about 1 min of the session's death.
  - Z1 reads the threshold every cycle.
  - T3's dry tests include SIGKILL.
  - The EXIT trap is kept for normal exit and SIGTERM.
- **R4 (A).** T2's interlocked path only. The set is bounded to 66-73.
- **R5 (A).**
  - The gate runs before every run.
  - A foreign user means an immediate restore under our lock, then the end of the session.
  - The scripts refuse while `pending.json` exists without a live session.
  - The orchestrator keeps our other queues off aifoundry2 while it exists.
- **R6 (A).** The error-return latch and POWER_SAFE are in §14. The post-run clock check and ABORT-LATCH are in §4.4.
  The risk is stated in the D1 question.
- **R7 (A).** The P-run is UNI32@20 at about 68.5 W. The 73 W cap is kept, at most 3 P-runs, at the session end.
  G7(a) and (b) get development bands.
- **R8 (A).** Z3's set comes first, at INFO. WARNING only after ALIVE is shown. The level found is restored.
- **R9 (M).**
  - The device-1 guard and the PCI identity check are adopted for Z2 on aifoundry1-c1.
  - DV2 runs no heat on aifoundry1-c1, so no card-0 guard is needed: DV2 never addresses card 0, not even read-only.
  - The slot is asked of the owner (§4.3c).
- **R10 (A).** One global-state table per session (§4.2). The statistics trace is kept as found (control 2).

**§2 Confounds**

- **C1 (A).** S ≥ R0 + 2 in every branch: D1 uses thr* = R0 + 5, capped at 73, and the NAT branches follow the table
  in §4.1.
  - The critique's "COOL-native at R0 ≤ 60, or K − 3 at 61" is NAT-4 and NAT-3.
  - NAT-2 and NAT-1 are added, for G1 only.
  - The edge slope and time since the last heating are recorded as covariates.
- **C2 (M).**
  - A fixed 4-block cycle, not a textbook Williams square: with a 4-block cycle, a Williams square cannot also keep
    INT and PER adjacent in every block. The cycle keeps them adjacent, balances their order (ABBA) and what precedes
    the pair (run or rest), and balances B4C against UNI.
  - Lifted pairs are matched.
  - P-runs come at the end, with a ≥ 10 min rest.
- **C3 (A).** The host ambient log, W_idle and the rest reading per block are covariates. No builds or reductions on
  aifoundry2 during sessions.
- **C4 (A).** One reset per run, at S + 1, through a new `--reset-once-file`, since ettelem's `--reset-ms` resets
  periodically. Development reports 2 runs with periodic resets. They are never used for G1 or G4.
- **C5 (A).**
  - L_P is reported with a verdict on both L and L_P.
  - P_U is measured by ADD in every session.
  - The "±0.3 W" claim is removed. Power is measured.
- **C6 (A).** Single-launch T-runs. Development picks (N, K − S) so that the trip falls inside the launch. No trip
  means censored.
- **C7 (A).**
  - Z3's set is the first D1 action, with the LATCHED branch.
  - In NAT branches the ALIVE probe plays that role.
  - TH8's wording now names the deciding observation.
- **C8 (A).** C1m at @32 (600 MHz, about 13 W), with a 4-reading rise matched to G4, on a rested card (the LOOP
  branch). The superposition assumption is stated.
- **C9 (A).** No change needed. Lifts are counted in the chain.

**§3 Rules that cannot fail or cannot pass**

- **P1 (A).** G4 has the two-sided rule, and the band half-width splits the distances to the alternatives. n_val is
  8-16, sized for it.
- **P2 (A).** G5 is reported only. G is labelled descriptive.
- **P3 (A).** G6 keeps G6-M and G6-B. The rest is reported.
- **P4 (A).** Z1 tests line content, (a)-(d).
- **P5 (A).** Z2's aifoundry2 prediction is conditioned on uptime.
- **P6 (A).** G1-H is a demonstration. G1(e) is dropped.
- **P7 (A).** Every mechanism item is split into a source ordering (frozen now), host bands (frozen now from §2.2) and
  SP-time bands (set in development).

**§4 Firmware and data contradictions**

- **F1 (A).** G3(a) is replaced by G3-Q, loop quantisation. RE confirms it on the host.
- **F2 (A).** G3-H is restricted to PUP → PIDLE gaps within one launch.
- **F3 (A).** G3-I is [0, 1.6] s.
- **F4 (A).** The EXIT → OP, climb-OP and ENTER → OP bands are set in development. Only the orderings are frozen now.
- **F5 (A).** G2-E: "PUP or ENTER, never neither".
- **F6 (A).** G7(b)'s band is set in development. The load is sized per R7.
- **F7 (A).** Uptime is used for Z2 only. The fit uses OP lines plus the optional DM 36 marker.
- **F8 (A).** H-max is dropped from G4. G1 settles the trigger.
- **F9 (A).** Z3's set prediction applies only at R0 ≥ 66. The THERMAL_DOWN jump is reported.

**§5 Validation independence and existing data**

- **V1 (A).** "Replication on aifoundry2" throughout. The owner is asked. It may span up to 3 pre-booked sessions,
  with a frozen rule for dropped blocks.
- **V2 (A).**
  - C1's aifoundry1-c1 validation is dropped.
  - C1m is development input and a reported comparison.
  - DV2 reads none of HP's validation data before its freeze.
- **V3 (A).**
  - A2 is cited.
  - TRIG-A's definitions are reused: t_up, t_hi, t_m, the one-point t_down that excludes 800 → 600, and separating
    runs (a) and (b).
  - One change, justified by RC: the fit window's upper bound goes from +1.2 to +0.6 s.
- **§5.1 (A, done).** The retrospective is in §2.2, extended from the critique's 4 files to all 8 aifoundry2 files
  with clock changes.
  - It confirms the critique's numbers.
  - One refinement: the critique's "46 of 46 up-steps at 65" holds for hotline-pass2 and pass4. Over all six 23 Sep
    files it is 90 of 102 at 65, 11 at 66 and 1 at 64, with none at ≥ 67. That matches `dvfs.json .governor_days
    .up_T`.

**§6 Budget and feasibility**

- **B1 (M).**
  - The estimate is about 3 h, not 3-5 h, because T4 is a copy of A2's tested code: sampler, watcher, caps, edges,
    lifts, the single launch, the probe and the level handling.
  - T1 and T6 do not block card work.
  - Tonight's first card work needs only T2 and T5, as the critique says.
- **B2 (A).** Development blocks are T-only, about 8-12 min each. W is dropped from tonight, and P is optional at the
  end.
- **B3 (A).** C1m runs on a rested card (the LOOP branch) at the matched density, never after G blocks.
- **B4 (M).**
  - C1m still runs tonight, but only in the LOOP branch, and only if Z1 saw no reading ≤ 64 in the previous 60 min.
  - Reason: aifoundry2 has not read ≤ 60 all week, so NAT-4 is unlikely.
  - C1m's 13 W pulses of 5-20 s recover within minutes, not the 10-15 min of a W-run.
  - Without C1m, G4 would have no same-card undiluted reference.
- **B5 (A).** Z2 on aifoundry3 is standalone: it does not source `../lib.sh` or hp code there, runs from the copied
  `dv2/` only, and uses raw states 2-6.

**§7 Checklist 1-20.** All accepted: 1-18 as above, 19 in §13, and 20 in §4.4 (Host). Items 9 (C2) and 18 (B1, B4)
are accepted in modified form, for the reasons given.

**Rebutted outright.** None. Three points are modified (C2, B1, B4) and one is extended (R9: DV2 avoids card 0
entirely).
