# Adversarial critique of the heat-placement design (DESIGN.md)

Written 2026-09-27. Read-only: DESIGN.md, `firmware.md`, `observability.md`, `feasibility.md`, `derive_feasibility.out`, `placements.py`, `design_sets.py`, the repo and the firmware source. No card was touched, and nothing is committed.

## Citation key

The key is DESIGN.md's (`R/`, `V3/`, `FW:`, `FW18:`, `ETP`, `dfo:N`), plus:

| Tag | Meaning |
|---|---|
| `D:N` | DESIGN.md, line N |
| `TPM:N` | `heatplace/tpm-may2024.c`, line N. It is byte-identical to `FW:services/thermal_pwr_mgmt.c` (D:15) |
| `FW18h` / `FW18c` | `git show da192816a:device-bootloaders/src/ServiceProcessorBL2/include/thermal_pwr_mgmt.h` / `services/thermal_pwr_mgmt.c` in `ETP`. Copies are in `heatplace/src/da192816a/`, and both matched `cmp` here |
| **[computed here]** | Arithmetic or a parse done in this task. The inputs are cited |
| **[inference]** | My reasoning, not a measurement or source text |

---

## 0. Verdict

The design has the right structure: a paired within-block design, a governor-input proxy, a strict start, a pre-registration hash and outcome words. Its answer to Q2 ("X %, 99 % CI", D:146) survives every problem below. Five problems would still make the verdict machinery report something false or empty:

1. **TRIG-B probably cannot work on either card it relies on** (§1). On aifoundry3, the source predicts that the governor latches silent after the first crossing of 65 °C since boot. On aifoundry1 card 1, the telemetry shows a governor that never acts. Under §3.5, a None on any validation card makes an item INSUFFICIENT (D:436), so TRIG-B is INSUFFICIENT by construction.
2. **A `SIGN` item "fails" whenever its 99 % CI includes 0** (D:101, D:148-149). An underpowered run is then reported as a refutation. §2.1 gives a three-way rule.
3. **The design is underpowered where it matters** (§2.2). Tier S cannot reach ±δ at any block count the design allows [computed here]. The κ bands of ±0.05 and ±0.03 are below the method's own precision.
4. **Censored pairs are dropped** (D:91), and the drop is informative. It biases `L(PER16/INT16)` toward 0, exactly on the hypothesis under test.
5. **The H6 superposition identity is false as stated** (D:154). `--per-shire 16` runs minions 0–15 of each shire, not "half of each minion".

Each is fixable before any card time. Every fix is listed in §5.

---

## 1. The trace test (TRIG-B) and the governor's state on the two cards whose clock is fixed

### 1.1 aifoundry3: the governor probably latches in `THERMAL_DOWN` [inference from source]

**The power loop cannot exit.**
- aifoundry3's firmware TDP is 0 W (`R/docs/findings/14-card-behaviour.md:151`), and its 600 MHz is the bottom of its VMIN table (`14-card-behaviour.md:181-183`).
- At every kernel start, the dm task sets `POWER_DOWN` (TPM:862-872), and the power task runs `power_throttling(POWER_DOWN)` (TPM:2438-2440).
- That loop exits only when the PMIC average is below 1.05 × TDP, which is 0 mW, or when the clock equals 300 MHz (TPM:2238-2246, macro at TPM:289).
- At the bottom point, `reduce_minion_operating_point` asks for the same frequency. `set_minion_operating_point` then returns `STATUS_SUCCESS` without acting (TPM:1788-1791, :1899-1914), so no error ends the loop.
- So the power task never returns. It spins on PMIC reads.

**The state then sticks.**
- The dm task still writes the state. That is why the 22 September dump alternates `Power throttle down` and `Power idle` lines (D:114).
- The first time the mean exceeds 65 °C, the dm task logs one `Thermal throttle down event` and sets `THERMAL_DOWN` (TPM:668-679).
- Only `thermal_throttling()` sets `THERMAL_IDLE` (TPM:2366-2374), and it runs in the stuck power task.
- Both the thermal trigger and the power branch require `state < THERMAL_DOWN` (TPM:669, :845).
- So from then until the SP reboots, aifoundry3 logs **no governor line of any kind**: no thermal event, and no launch marker.

**The existing data does not decide it.**
- aifoundry3 was reset on 25 September (`14-card-behaviour.md:213-215`), then heated to 90 °C in V3 (dfo:14-16). If the latch is real, it has already happened.
- The only dump with governor lines, 22 September, was taken on a die at 55.8 °C (`R/docs/reports/data/2026-09-22-cards/cards-report.json`, `launch.aifoundry3.T` = 55.77). So it cannot show whether a thermal line ever prints.
- No committed `.bin` holds a `Thermal … event` line [computed here: `strings` over all 212 `docs/reports/data/**.bin`; only `sptrace-aifoundry3.bin` holds governor lines, 26 down and 27 idle].
- aifoundry3's SP pass is 224 ms, against 133 ms on aifoundry2, which runs the same 0.20.0 build (`03-experiments.md:1232-1233`). A spinning power task would explain the difference. That is suggestive, not proof.
- D:115's reading, that V3 saw nothing because of INFO flooding, is right for V3's dumps. Each held 42–45 host-request lines (`Host_Iface` and `pc_vq`), plus the config queries and no governor line [computed here: a ring parse of `V3/raw/aifoundry3/tel/p*/gov/sp*.bin`]. So those dumps cannot tell the two explanations apart either.

**Consequences.**
- R1a's probe (D:334) would see 0 lines.
- D-trace (D:347) would drop TRIG-B for the wrong stated reason.
- The B-pos alignment by launch marker (D:121) has no markers.
- D:45's wording, "that is the event on which the thermal test fires", is false on this card. On aifoundry3, `t66` is when the test *would* fire on a card whose governor acts.

### 1.2 aifoundry1 card 1: the governor evidently does not act

- In 0.18.0, an up-request steps 50 MHz up to 700 MHz, and a thermal reduce steps 50 MHz down to 300 MHz (FW18h:56-58; FW18c:1769-1811; loop exits at FW18c:2082-2094).
- Card 1 read 600 MHz in all 359,657 samples. Its since-boot maximum is 600 (dfo:5).
- Those samples include 11,446 below 65 °C at 45–63 W, where it should have stepped up. They also include readings up to 88 °C (dfo:18-20), where a thermal reduce should have stepped down.
- Neither happened. The simplest reading is that `active_power_management` is off [inference]. The thermal trigger needs it (FW18c:592).
- So TRIG-B on card 1 is almost surely None.
- By D:436, a None on any validation card makes the whole item INSUFFICIENT. With card 1 as the primary validation card, TRIG-B cannot PASS.

### 1.3 The B-neg and B-pos rules would not discriminate even on a card that logs

**B-neg does not re-arm H1′.**
- The trigger logs only on entry, when `state < THERMAL_DOWN` (TPM:669).
- A max-keyed firmware would still be in `THERMAL_DOWN` when a Tier S run starts at the 64 °C edge. At idle the high sits 1–2 °C above the mean (`observability.md:163-167`), so it reads 65–66 there. With the max at 66, H1′ never left the loop.
- H1′ then predicts **0** events in the control window, the same as H1 (compare D:118-119).
- **Fix.** A control window counts only if the windowed high read ≤ 65 for ≥ 1 s (≥ 3 passes) immediately before it.
- **Better.** Use the exit event. The loop's `Thermal idle state event` (TPM:2372) should fall within ±1 pass of the host mean's first reading of 65 on the way down under H1. Under H1′, it falls when the high reads ≤ 65. Every approach from above gives one such event, with no heating needed.

**The coverage proof depends on H1.**
- D:117 proves ring coverage by the run's launch marker.
- A card stuck in `THERMAL_DOWN`, which is H1′'s case, logs no launch marker (TPM:845). So the H1′-favouring windows are the ones discarded.
- **Fix.** Prove coverage without reference to either hypothesis. Require the newest entry of the previous dump to reappear in this one: the ring overlapped, so nothing was lost.

**The B-pos threshold sits inside H1′'s region.**
- "Mean reads ≥ 65 within ±0.5 s" (D:121) counts an event at mean 65 as H1-consistent.
- H1′ fires when the high first reaches 66, which happens at a mean of 62–65 (the high sits 1–4 °C above the mean: `observability.md:163-167`).
- **Fix.** Use ≥ 66, and also require the printed T to equal the host mean within ±1.

**The SP timestamps have no known rate.**
- The ring stores a u64 timestamp per entry (`R/tools/ettelem/parse_sptrace_voltage.py:14-18`). Its tick rate is not established: `firmware.md:304-331` argues that even the FreeRTOS tick may be 0.4 ms rather than 1 ms.
- ±0.5 s alignment over a 3–120 s run needs the rate.
- **Fix.** Fit rate and offset per dump from ≥ 2 governor markers whose host times are known. The heater prints per-launch `t_start_ms` and `t_end_ms` in host epoch ms (`V3/raw/aifoundry3/tel/p1/gov/runs.jsonl`). The sampler's `t_ms` uses the same host clock (`R/tools/ettelem/ettelem.cpp:138`).

### 1.4 Fix: probe before asking for O2, with no state change

V3 left every card at INFO (`R/tools/claims-v3/tel/block.sh:183-186, 408`). At INFO, the power task also logs `Power Throttle event received. throttle_state: N` (TPM:2421).

In R0, on aifoundry3 and on card 1 (`ET_DEVICES=1`), with no sampler open:
1. Run one ≤ 2 s heater launch under `hold10`.
2. Run `ettelem sptrace` immediately, with no `config` query in between.

The outcomes:
- (a) `Power throttle down/up` lines **and** `event received: 2|3` lines: the power task is alive, the card is not latched, and TRIG-B is feasible.
- (b) Power lines without `received` lines: the power task is stuck, and the latch will occur at the first crossing of 65 °C.
- (c) No governor line at all: the card is latched, or APM is off.

This costs about 10 s of card time per card, changes nothing and needs no O2. Ask for O2 only if (a) holds. Register TRIG-B per card, never on a card that gave (b) or (c). That leaves aifoundry2 on cool mornings as the realistic on-card test of Q1, and §0 of the report should say so (compare D:35-37).

---

## 2. Decision rules that pass or fail by variance

### 2.1 SIGN items have no None (D:101)

- "Holds if the interval excludes 0 on the predicted side, fails otherwise" makes low power a refutation.
- D:147-150 repeats the rule: "H2 falsified by an interval that includes 0".
- D:540 then says INSUFFICIENT means "not tested". But a SIGN item can never be INSUFFICIENT except with fewer than 3 blocks (D:104).

**Fix.** A SIGN item:
- **holds** if the CI excludes 0 on the predicted side;
- **fails** if the CI excludes 0 on the other side, **or** lies wholly inside ±δ (the effect is shown to be negligible);
- is **None** otherwise.

This applies to H2, H3, H5, H7, H8, H9, H10 and H12.

### 2.2 Power: most EQUIV and κ items cannot reach their bands [computed here]

**Tier S `t66`.**
- The launch state scatters by SD 0.11 °C on aifoundry2 at 80 °C (`03-experiments.md:45-46`) and by 0.178 °C on aifoundry3 at 55.8 °C (`cards-report.json`, `launch.aifoundry3.T_sd`).
- Tier S must add 1.03 °C (D:273). So each run's `t66` has a coefficient of variation of at least 0.11/1.03 to 0.178/1.03, which is 11–17%. This is before sampling, pass quantisation (224 ms) and `t0` jitter (155–264 ms board refresh: `03-experiments.md:1235-1236`).
- The paired log-ratio SD is then ≥ √2 × that, 15–24%.
- The 99% half-width is t/√n × SD: 2.059 × SD at 5 blocks (t = 4.604) and 1.237 × SD at 8 blocks (t = 3.499).
- That gives **0.31–0.50 at 5 blocks and 0.19–0.30 at 8**, against δ = 0.095.
- EQUIV on Tier S `L` needs a paired SD ≤ 0.046 at 5 blocks, or ≤ 0.077 at 8. D-blocks (D:354) cannot reach that.

**Tier L `t66`.**
- The launch state contributes only 2–3.5% (0.11–0.178 over the 5.03 °C to add, from S = 60).
- Heatsink history is the unbounded term: the same work took 107 s against 162–167 s from the same reading (`12-heat-management.md:52-55`). §3.1 gives fixes.

**κ.**
- The step-timing method recovers the rise to about 0.03 °C on repeated runs (`14-card-behaviour.md:110`). That is 2–3% of a Tier S rise of 1–1.5 °C, before the error from fitting the network on a few 2 s preheat segments.
- A paired SD of 4–7% gives a 5-block half-width of 0.08–0.14. The H4 band of ±0.05 (D:144) and the H6 band of ±0.03 (D:155) are below that.

**Fixes.**
- (i) Add a pre-data power step to R1. From R1's run-level scatter, compute the projected half-width at the validation block count for every registered item.
- (ii) Any EQUIV item whose projection exceeds its band becomes "reported, not tested" *before* the prediction is registered. It is not left to end as INSUFFICIENT.
- (iii) Base D-blocks on the pooled SD from R1–R3 blocks with identical parameters, not on R3's df-3 estimate alone. Let it choose n up to a card-time cap, not only 5 or 8.
- (iv) Allow the owner to set δ to 20%, if 10% is not what a scheduler needs.

### 2.3 Informative censoring (D:91, D:348)

- Dropping a pair when either run is censored removes exactly the pairs in which the placement that trips later ran out the clock. That biases `L` toward 0.
- D-S tolerates 20% censoring.
- **Fix.** Use `ln(min(t66, C))` with a fixed cap C for every pair. This is a restricted-time contrast: conservative, with no selection.
- Also report the sign-count test with censored-high runs ranked as longest.
- Set the tier parameters so that censoring stays ≤ 5%.

### 2.4 Other rules

- **§3.3's fallback** "neither → EQUIV" (D:409) registers a null prediction for an item whose development CI may centre on +25%. Register "reported, not tested" whenever the development CI is wider than 2δ.
- **H11 passes vacuously** if no SIGN item is registered (D:413, D:537). Mark H11 "not tested" then.
- **H13's band of ±0.5 W** (D:204) is 3.8% of 13.1 W. That lets a power-driven bias of up to ln 1.038 = 0.037, or 39% of δ, into `L` while H13 "holds" [computed here]. Report the power-normalised `L` for every pair, not only when H13 fails (D:205).
- **The κ fit gate** is rms ≤ 0.4 °C of centred residuals (D:84). A perfect model on whole-degree readings gives 0.29. So the gate admits a systematic misfit of √(0.4² − 0.289²) ≈ 0.28 °C, about 25% of a Tier S rise [computed here]. Gate instead on the share of samples where the predicted floor equals the reading (for example ≥ 95%). Also state how the network's initial state is set: simulate the whole block from its start, using measured `board_w`.
- **Multiplicity.** V3's standard says "picking the best of many configurations is corrected for" (`V3/README.md:18`). The design has about 15 items per card at 99%. That is acceptable, but the report should state the family size.

---

## 3. Confounds

### 3.1 Heating history (the largest)

- **No burn-in.** The lab's strict start includes "Burn in a few cycles first, so the heatsink reaches its periodic state" (`14-card-behaviour.md:126`). §2.3 and §4.2 omit it (D:264-279, D:472-487). The first run of every block starts from a colder heatsink. Fix: 1–2 discarded preheat-and-approach cycles at the start of each block.
- **Carryover in Tier L.** A placement that trips later runs longer before its stop, and so puts more energy into the 60–400 s stages. The next run then starts at the same reading but on a hotter heatsink (`12-heat-management.md:52-55`). The effect under test thus feeds into its successor's noise. Fix: a carryover-balanced order (a Williams square for INT16, PER16 and UNI32), with the predecessor recorded.
- **A covariate thrown away.** "Reported, not used to correct" (D:278) wastes a valid pre-treatment covariate: the time between the host mean's 65 and 64 falling edges. It measures the cooling rate at launch, which is the heatsink state. Pre-register one adjustment on it, and report both the adjusted and unadjusted contrasts.

### 3.2 The whole-degree mean at a fixed start edge [inference]

- `t66` counts integer crossings of 34 truncated sensors: Σ floor(T_i) from 2,209 to ≥ 2,244 (D:273; `firmware.md:100`).
- A 16-shire placement gets its +35 from the fractional parts of *its own* 16 sensors.
- Those fractional parts are fixed by each sensor's uncalibrated offset (`firmware.md:87-93`) and the reproducible profile at the edge. The ±0.11 °C common shift dithers them only weakly.
- The result is a reproducible, placement-specific bias of about ±1–2 sensor-degrees in 35 (3–6% of `t66` in Tier S). It does not transfer across cards, because their offsets differ.
- Fix: alternate the start edge by block, S ∈ {63, 64} (Tier S) or {59, 60} (Tier L), balanced, to dither the fractional parts. The bias is about 5× smaller in Tier L (+171).

### 3.3 Not the same work, or not the same minions

**Intra-tile position.**
- `--per-shire N` runs minions 0…N−1 (`R/workloads/sparsity/host/main.cpp:275-283`). UNI32 at 16 heats minions 0–15 of each shire; INT16 at 32 heats whole tiles.
- ½(INT16@32 + PER16@32) is "every minion at half intensity". It is not UNI32@16. So H6's identity (D:154) and "the same 512 minions" (D:39) are false.
- The sensor's place inside the tile is unknown (`observability.md:454`). So SPREAD-t (UNI32 against INT16) confounds spreading with where in each tile the heat sits.
- Fix for H6: use set identities that hold exactly. Either INT16@16 + PER16@16 = UNI32@16, or INT16@32 + PER16@32 = ALL@32. For SPREAD-t, add a UNI32 hi-half variant (minions 16–31, via `enercat_host --minions 0xffff0000`: `observability.md:335-337`) and average the two halves.
- CHK16E and CHK16O serve only H6 (D:155). Drop them, which saves 2 of the 7 Tier S runs per block, or apply the same fix.

**Work.**
- "Same seconds" (D:244) is not "same operations" if per-minion throughput differs between 16 and 32 active minions per shire.
- The heater prints `iters`, `cycles_per_op` and `ghz` per launch (`V3/raw/aifoundry3/tel/p1/gov/runs.jsonl`). Add ops per minion as a precondition item beside H13.

**NoC.** The heater is not a NoC confound.
- Every minion starts the kernel. Unselected shires and minions return at once (`R/workloads/sparsity/kernel/sparsity.c:553-557`), so launch traffic is equal across placements.
- TensorFMA on scratchpad data uses no mesh after setup (`observability.md:316-318`).
- Say so in the design, with the citation.

### 3.4 Idle offsets and `t0`

- `t0` requires `board_w` ≥ `W_idle` + 3 W (D:81). B4NE and B4SW add only 3.3 W (D:257-258), so `t0`, and with it `ι`'s windows, is unreliable exactly where `ι` is measured.
- **Fix.** Take `t0` from the heater's first measured launch, `t_start_ms`, in host epoch ms (`runs.jsonl`). Keep the `board_w` threshold as a check.
- `W_idle` is taken while the die is still falling, with leakage decaying. That is equal across placements, so it is only a caveat.

### 3.5 Airflow and fan: symmetric groups cannot see the likeliest heatsink effect

- Airflow across the heatsink would cool the upstream edge more than the downstream one: a *linear* gradient. That is H3's own mechanism (D:142).
- INT16, PER16, MEM8 (W and E strips), EDGE8 (N and S edges) and the checkerboards are all symmetric about the centre. A linear gradient cancels in every one of their contrasts.
- **Fix.** Add one antisymmetric pair per axis, from `placements.py`'s die frame [computed here]:
  - W12 `0x03076616` = {1, 2, 4, 9, 10, 13, 14, 16, 17, 18, 24, 25} against E12 `0x747090e0` = {5, 6, 7, 12, 15, 20, 21, 22, 26, 28, 29, 30}. These are r1–r4 × c1–c3 against c4–c6.
  - N12 `0x31313232` = {1, 4, 5, 9, 12, 13, 16, 20, 21, 24, 28, 29} against S12 `0x4646c4c4` = {2, 6, 7, 10, 14, 15, 17, 18, 22, 25, 26, 30}. These are rows r1–r2 against r3–r4.
  - Each group is 12 shires with 4 memory-side tiles and a centre distance of 2.5. E12 and N12 each hold 2 tiles beside I/O.
- **Airflow can also change mid-session.** "The lab's airflow changed and the die fell 12 °C" (`14-card-behaviour.md:272`; `03-experiments.md:256`). Bracket every block with the same reference run (UNI32 first and last). Void a block whose two reference `t66` values differ by more than a pre-set margin, or whose `W_idle` shifts by more than a set amount.

### 3.6 The power branch against the thermal branch

- **aifoundry3.** See §1.1: the power branch probably locks the governor.
- **Card 1.** See §1.2: no branch acts.
- **aifoundry2 when cool (H12, TRIG-A).**
  - 256 minions at 800 MHz stay under 65 W (D:193-195), so power steps up, then thermal steps down. That part is sound.
  - But one `--seconds 7` process is about 14 kernel launches of 0.5 s each (`main.cpp:560-578`, `iters·0.5/wall` at :567; the V3 runs show 0.493 s launches with 1–2 ms gaps).
  - TRIG-A's "no kernel boundary within ±1 pass" (D:128) would then exclude about 54% of all time (2 × 133 ms / 493 ms) [computed here], or, if it means process boundaries, would miss an idle blip between launches.
  - **Fix.** Classify by step size instead. An idle or boot reset goes 800 → 600 in one change (`go_to_idle_state`, TPM:1975-1979). A thermal reduce goes one point, 800 → 700 (TPM:1899-1914), and the loop's second step waits `DELTA_TEMP_UPDATE_PERIOD` (TPM:2354).
  - E10 shows both kinds: 800 → 600 at 6.09 s and 0.94 s, and 800 → 700 elsewhere (dfo:22-28).

**H12's resolution** [inference from dfo:22-27].
- 256 random-data minions at 800 MHz add about 12.5 W over idle (D:193-195 × 25.6 mW). That sits between E10's full-chip zeros (39 W at the step, first down-step at 5.6–6.1 s) and ones (56 W, 1.3–1.5 s).
- Expect `t_down` of about 2–3 s. The up-step itself comes at 0.5–1.1 s, which leaves 1–2 s at 800 MHz. A 10% placement effect is then about 1 SP pass (133 ms).
- **Fix.** Use 128 minions per placement (`--per-shire 8` on 16 shires; UNI32 at 4) to push `t_down` toward 4–5 s, inside the 7 s launch.
- H12 also changes the regime (256 minions at 800 MHz, against 512 at 600) while predicting the sign from aifoundry3 (D:197). Label it exploratory.

### 3.7 Regime dependence of `t66` ratios [inference]

- Tier L runs until the mean approaches 66 °C. How close 66 °C lies to the placement's steady state decides how `t66` responds. Near the asymptote, a few-percent change in coupling changes `t66` by tens of percent, and ambient drift does too.
- The design gives no estimate of aifoundry3's steady state for 13.1 W (L16) or 6.6 W (L8).
- A lower bound on its closed-loop gain is (90 − 56) / (74.6 − 25.1) ≈ 0.69 °C/W. That uses the 90 °C cap reached at 74.6 W (dfo:14-16) and the 25.1 W idle at 56 °C (`cards-report.json`, `idle.aifoundry3`) [computed here].
- Derive the steady-state gain from V3-IDLE's committed heat and cool curves before R2. This costs zero card time, and it decides whether L8 can reach 66 °C from 62 °C at all (D-L8, D:353).
- `ln(t66)` ratios are specific to the regime and the card. κ in watts is the quantity that transfers. H11's per-card statement should rest on κ's sign, not on the magnitude of `t66`.

### 3.8 aifoundry1: card 0 beside card 1

**Confound and hazard.**
- Card 0 has a cooling fault. It once sat at 115–117 °C and drew 66–71 W *idle* at 600 MHz before dropping to 300 MHz (`14-card-behaviour.md:197-204`).
- Card 1's heating warms the shared air (`idle/block.sh:216`). Nothing in the design watches card 0, and reading it needs the owner's approval (`feasibility.md:284`).
- A card-0 excursion would drift card 1's baseline inside a block, which the within-block pairing does not remove. It could also go unnoticed as a safety event.

**Fixes.**
- (a) Add to O3 a 1 s card-0 die reading at the start and end of each card-1 session.
- (b) A proxy stop rule, if (a) is refused. End the session if card 1's `W_idle`, or its idle reading at the block edge, rises by more than a set amount from the session's first block.
- (c) Keep the design's ≤ 25 min entries, ≥ 15 min apart (D:384).

**Card 1's parameters are undefined.**
- D:398 freezes S, S_L, S_L8 and the preheat targets "per card", but gives no rule for card 1. Card 1 heats about 4–6× faster (dfo:18 against dfo:14-16).
- Copying aifoundry3's S_L puts card 1 in a different regime. Scouting placements on card 1 would be development on a validation card.
- **Fix.** Pre-register a calibration run on card 1 that uses only the preheat workload, which is not a registered placement. Scale S_L by the D-L16 criterion from that run.

### 3.9 H7 (CONC) and H10 (MAP)

**H7.**
- `minshire[2]` is the maximum over 34 uncalibrated sensors (`firmware.md:87-93`). So Δhot mostly measures whether the placement heats the sensor with the largest offset.
- The pairing does not remove that (compare D:168). The offset sensor lies in exactly one of INT16 and PER16, and at half density in UNI32.
- **Fix.** Register CONC as ½[Δhot(INT16) + Δhot(PER16)] − Δhot(UNI32). The offset sensor then enters every term once. Report the INT16 and PER16 split separately.

**H10.**
- `ι` over 3 s of whole-degree readings on a 3.3 W, 7 s load gives per-run values of roughly −1, 0 or +1.
- **Fix.** Add ≥ 3 B4 repeats per block, or use the I/O sensor's own windowed peak-hold, `ioshire[2]` (`observability.md:105`), whose sample-to-sample noise dithers the whole degrees.
- H10 tests only where the I/O sensor sits. The memory-strip sides come from memprobe's `ms_pos` (`observability.md:259-261`), not from H10. So "if H10 fails, 'N/S edge' becomes unverified" (D:185) overstates what H10 carries, and also what its holding would prove.

### 3.10 Hypotheses the observables cannot falsify

- **H5.** The leakage-convexity term is about 0.04 W (D:159; `observability.md:211-214`), about 0.3% of 13.1 W. H5 "fails" by power, not by evidence. Register it as not testable.
- **H6 at ±0.03.** Below κ's precision (§2.2), and the identity is wrong (§3.3).
- **M1 against M2.** Already conceded (D:584). But H3's airflow motivation is also untestable with symmetric groups (§3.5).
- **H1 against H1′ without O2, or on latched or APM-off cards.** Source only (D:586). §1 shows this probably covers aifoundry3 and card 1 *with* O2 too.

---

## 4. Card time, safety and the lab rules

- **O1 (Tier L chains).** The repo contradicts itself. PLAN3 says "a chain of 9 s launches … is not a way around the rule" (`V3/PLAN3.md:1072, 1136`), while V3-IDLE chained 2 s launches for up to 900 s (`idle/block.sh:59`). The design should not present V3-IDLE as the precedent that settles it (D:54, D:603). It should also tell the owner the likely consequence of "No": by §2.2, Tier S alone gives PLACE-t intervals of about ±30–50%. The Q2 answer is then an estimate with a wide CI, and every EQUIV verdict comes out not tested.
- **O2 (log level).** Ask only after §1.4 shows outcome (a). Three more points:
  - An intrusion abort (exit 3, "the card left closed", D:324) skips the restore, so the level stays at WARNING. Document that WARNING is the boot default (`FW:services/log.c:60`), and restore it at the next block's start.
  - The level inference (D:291) treats every dump that holds host-request lines as INFO. A DEBUG level (V3's `tel` blocks used it) would be restored wrongly. Detect `MS nn Voltage` lines → DEBUG.
  - The `ettelem.cpp` change (D:470) is a change to a repo tool. Keep it in `build/ettelem-hp/` as planned.
- **aifoundry2's gate.** "≥ 6 h with no launch" (D:389) cannot be verified on a card that CI and other users share (`lib.sh:59-60`). Gate on the reading plus `et-who` and the process scan only. Also, "waits until the mean reads ≤ 63" (D:390) is not a strict edge: the first run of a cool period starts from rest, the others from a falling die. Treat run 1 of each period as warm-up, and start the rest on the 64 → 63 falling edge.
- **Safety caps.** They are sound and far above the protocol's roughly 70 °C (D:318-320). The one unwatched hazard is card 0 (§3.8).
- **Card-time budget.** Dropping CHK16E, CHK16O, H5 and the H6 κ bands saves about 2 of the 7 Tier S runs per block. That pays for the burn-in (§3.1), the reference brackets (§3.5) and one antisymmetric pair per block. Net card time is about unchanged [inference, from D:340-341's roughly 2 min per Tier S run].

---

## 5. Fixes, in priority order

| # | Fix | Where |
|---|---|---|
| 1 | Run the R0 INFO-level probe on aifoundry3 and card 1 (one 2 s launch, then `sptrace`, with no sampler and no state change) before asking for O2. Register TRIG-B per card, and only where the probe shows a live power task | §1.4 |
| 2 | Three-way SIGN rule (holds, fails, None); fails only on the opposite sign or on a CI inside ±δ | §2.1 |
| 3 | A pre-registration power step from R1's scatter. Any item projected above its band becomes "reported, not tested". Base D-blocks on the pooled SD | §2.2 |
| 4 | Replace dropped censored pairs with `ln(min(t66, C))`, and target ≤ 5% censoring | §2.3 |
| 5 | H6 with exact set identities; a UNI32 hi-half variant for SPREAD-t; drop CHK16E and CHK16O | §3.3 |
| 6 | Burn-in cycles, a Williams order, and a pre-registered approach-time covariate | §3.1 |
| 7 | B-neg re-arm condition, an H-neutral coverage proof, B-pos at ≥ 66 with printed T equal to the host mean, a calibrated tick rate, and the exit-event test | §1.3 |
| 8 | `t0` from the heater's `t_start_ms`; TRIG-A classified by step size (800 → 600 against 800 → 700) | §3.4, §3.6 |
| 9 | W12/E12 and N12/S12 antisymmetric pairs; a reference bracket and void rule per block | §3.5 |
| 10 | Start edges alternated by block, to dither the truncation | §3.2 |
| 11 | CONC as ½(INT + PER) − UNI; more B4 repeats or `ioshire[2]` for MAP; soften H10's claim | §3.9 |
| 12 | A card-1 calibration rule; card-0 monitoring or a stop rule; aifoundry2's gate on the reading only, with run 1 as warm-up | §3.8, §4 |
| 13 | H12 at 128 minions, labelled exploratory; H5 labelled not testable; H11 "not tested" when no SIGN item is registered | §3.6, §3.10, §2.4 |
| 14 | aifoundry3's steady-state gain from V3-IDLE curves, before R2 | §3.7 |
