# Heat placement and the thermal governor: experiment design

Design task of the heat-placement workflow. Written 2026-09-27 from the repository and the three research notes next to
this file (`firmware.md`, `observability.md`, `feasibility.md`). No card was touched, and nothing here has run. Every
number given as a prediction below is fixed **now, before any data**. The development rounds may change only what
§2.8 lists.

## Citation key

| Tag | Meaning |
|---|---|
| `R/` | `/home/yaroslavvb/claude/et-soc1-pages`, branch `pages-v3b` at `305fe0d` |
| `V3/` | `R/docs/reports/data/2026-09-25-claims-v3/` (the version-3 three-card campaign) |
| `ETP` | `/home/yaroslavvb/claude/et-soc1-prototyping/external/et-platform`, HEAD `836a4ab` |
| `FW:` | `git show cafe03fc3^:device-bootloaders/src/ServiceProcessorBL2/<file>` in `ETP`. This is the closest source to the 1.3.1 cards (aifoundry2, aifoundry3), per `V3/firmware.md:15-17`. `FW:services/thermal_pwr_mgmt.c` is byte-identical to `tpm-may2024.c` next to this file (`cmp`, checked here) |
| `FW18:` | The same path at `da192816a` (BL2 0.18.0), the closest source to aifoundry1 card 1's release 1.2.0 (`firmware.md:44`) |
| `MAN/` | `/home/yaroslavvb/claude/et-soc1-prototyping/external/et-man/` |
| `firmware.md`, `observability.md`, `feasibility.md` | The research notes in this directory, cited by line |
| `Dn` (`dfo:N`) | A derived number from `derive_feasibility.py`, output line N of `derive_feasibility.out` in this directory |
| `design_sets.py` / `.json` | Written here. It derives the placement masks below from `placements.py`, which carries the latency map `MARTY` of `R/workloads/nocbench/analyze.py:50-60` and the inferred die frame of `observability.md:262-284` |
| **[inference]** | My reasoning, not a measurement or source text |
| **[computed here]** | Derived in this task; the method is given |

---

## 0. The design on one page

**The owner's first question, from source.** Voltage-frequency scaling kicks in on the **average**, not on one sensor.
- The only temperature the thermal test reads is `pvt_get_minion_avg_temperature()` (`FW:services/thermal_pwr_mgmt.c:656,668`).
- That function is the integer mean over the 34 minion-shire sensors, `PVTC_MINION_SHIRE_NUM` (`FW:driver/pvt_controller.c:1279-1305`; `FW:include/bl2_pvt_controller.h:80`).
- Each sensor is already truncated to whole °C (`FW:driver/pvt_controller.c:582`).
- The test is `mean > 65` (`FW:services/thermal_pwr_mgmt.c:668`; `FW:include/thermal_pwr_mgmt.h:46`).
- No per-sensor or maximum path can change the clock (`firmware.md:272-286`).

The experiment adds **on-card** evidence from two tests:
- **TRIG-B, on the development card, no clock needed.** It uses the firmware's own `Thermal throttle down event` log line, which prints the value it compared (`FW:services/thermal_pwr_mgmt.c:672-674`, `LOG_LEVEL_CRITICAL`).
- **TRIG-A, on aifoundry2 when its die is cool.** It checks the clock against the hottest sensor.

**The second question** is whether the same work placed at the edges runs longer before the trigger fires than the same work in the centre. The design compares the **same 512 minions**:
- the 16 interior shires (INT16, `--shires 0x6477f412`);
- the 16 perimeter shires, the edges and corners (PER16, `0x9b880bed`);
- the same work spread over all 32 shires (UNI32, `--per-shire 16`);
- two checkerboards (CHK16E/O), for a linearity check.

Smaller groups test the memory-strip side against the bare die edge and the centre, and the map orientation. The observable is the time for the governor's own input (`temp_c.minshire[0]`) to first read 66 from a fixed start. For the cards whose clock cannot move, that is the event on which the thermal test fires (`feasibility.md:200-217`).

**Cards** (`feasibility.md:287-295`):
- **Development:** aifoundry3.
- **Validation:** aifoundry1 card 1, and aifoundry2 only on days when its die rests at ≤ 62 °C.
- **Excluded:** aifoundry1 card 0 (`feasibility.md:165-169`).

**Two run lengths.**
- **Tier S:** one launch of at most 10 s per run, from a start just below the threshold. This keeps the lab's rule as written (`R/CLAUDE.md:73`; `R/AGENT.md:153`).
- **Tier L:** a chain of 2 s launches, at most 150 s per run, from a lower start. This is the regime where "run longer" means tens of seconds. **It needs the owner's explicit yes (O1).** The campaign plan says "a chain of 9 s launches holds the card just as long and is not a way around the rule" (`V3/PLAN3.md:1072, 1136`), although the campaign's own V3-IDLE heater chained 2 s launches for up to 900 s (`R/tools/claims-v3/idle/block.sh:59`; E44, `R/docs/findings/03-experiments.md:1317`).

**Rounds.**
- R0 is a dry run and a smoke run.
- R1 scouts Tier S, the trace and the map.
- R2 runs Tier L if O1 allows it, otherwise more Tier S.
- R3 is a four-block rehearsal of the frozen protocol.
- Then the pre-registration file is written and hashed, and the validation blocks run with **no iteration** (§3.6).
- Card time is about 5 h on aifoundry3, about 3 h on aifoundry1 card 1, and about 1 h on aifoundry2 spread over at least 3 cool mornings. Budget three to eight times that in wall-clock (`R/docs/findings/14-card-behaviour.md:131-132`).

**The owner must decide before any card time (§6):**
- O1: chains in Tier L.
- O2: the service processor's log level set to WARNING, its boot default, for the trace test.
- O3: waiting for aifoundry2's cool mornings.

---

## 1. Theories and hypotheses

### 1.0 Shared definitions (fixed now)

**Unit.** One **block** is one run of each placement in the block's set, in an order shuffled by a seed logged in the block (the V3 practice, `R/docs/findings/03-experiments.md:41-43`). Contrasts are paired within a block. A card's value is the mean of the block-level contrasts with a two-sided 99% Student t interval (df = blocks − 1: 9.925, 5.841, 4.604, 4.032 for df 2–5; `V3/PLAN3.md:572-574`). Samples and launches inside a run are never the unit (`V3/README.md:15-20`).

**Per-run observables**, all from the 10 Hz `ettelem sample --every-ms 100 --reset-ms 1000` output (fields: `R/tools/ettelem/ettelem.cpp:136-170`; `observability.md:101-116`):

| Name | Definition |
|---|---|
| `t0` | Kernel start: the first sample with `board_w` ≥ `W_idle` + 3 W, where `W_idle` is the median `board_w` over the 2 s before the (first) measured launch. The board value refreshes every 155.5–264 ms under a 10 Hz sampler (`R/docs/findings/03-experiments.md:1235-1236`, TEL-S) |
| **`t66`** (primary) | The first sample with `temp_c.minshire[0]` ≥ 66, minus `t0`. This is the governor's own input (`firmware.md:107-115`) crossing its own trip, `mean > 65`. It is censored at the end of the measured launch (Tier S) or at the chain cap (Tier L) |
| `sw_W` | The median of (`board_w` − `W_idle`) from `t0` + 1 s to the end of the measured launch (Tier S), or to `t66` (Tier L). This is switching power over idle, the only cross-card-comparable power (`R/AGENT.md`, §6 "Cards are compared on switching power") |
| `κ` (secondary, model-based) | Coupling gain: the scalar g that best reproduces the run's whole-degree readings from `t0` − 2 s to the launch end + 10 s, through a Foster network fitted to the same block's all-shire preheat segments with measured `board_w` as input. It uses the step-timing method of `R/docs/findings/14-card-behaviour.md:103-112` and the network fit of `R/tools/ettelem/flip_thermal_model.py` step 1 (taus `:30`, `nnls` `:56`). g = 1 means "these watts move the governor's input as much as uniform watts do". Fit gate: rms (continuous prediction − reading − 0.5) ≤ 0.4 °C on the fit segments, otherwise κ = None |
| `Δhot` | Concentration. For each 1 s reset window w, h_w = max(`minshire[2]`) − max(`minshire[0]`) in w. `Δhot` is the mean h_w over the last 3 windows of the measured launch minus the mean over the 3 windows before `t0`. Peak-hold semantics: `firmware.md:121-130`. Under uniform load the high rises 3–4 °C above the mean in 61–83% of rises (`R/docs/findings/05-claims.md:442`) |
| `ι` | I/O-sensor proximity signal: the mean of (`temp_c.ioshire[0]` − `minshire[0]`) over the last 3 s of the launch, minus the same over the 2 s before `t0`. The I/O sensor is not in the mean (`FW:driver/pvt_controller.c` loop to 33; `firmware.md:104-105`) and sits in the non-compute corner (`observability.md:172-189`) |
| clock check | `mhz.minion` in every sample of the measured window equals the card's expected clock: 600 MHz on aifoundry3 (`dfo:3`) and aifoundry1 card 1 (`dfo:5`). aifoundry2's cool runs are defined in §1.6 |
| trace events | From `ettelem sptrace` read right after the run (§2.4): every `Thermal throttle down event, current temperature: T, threshold: 65` (`FW:services/thermal_pwr_mgmt.c:674`), `Thermal idle state event` (`:2372`), `Power throttle down/up event` (`:867, :881`) and `Power idle state event` (`:854`), each with its u64 timestamp (ring format: `R/tools/ettelem/parse_sptrace_voltage.py:14-18`) |

**Contrasts**, for placements A and B in one block:
- For times: `L(A/B)` = ln(t66_A / t66_B). A pair with either run censored is dropped from `L`.
- For `κ`: the difference κ_A − κ_B.
- For `Δhot` and `ι`: the difference.

**Practical band, fixed now:** δ = ln 1.10 = 0.0953. A placement "runs longer" in a sense that matters to a scheduler only if it runs at least 10% longer before the trigger. **[choice made here; not from data]**

**Item result on one card:**

| Prediction type | holds | fails | None |
|---|---|---|---|
| `SIGN+` / `SIGN−` | the 99% interval excludes 0 on the predicted side | otherwise | — |
| `EQUIV` | the 99% interval lies inside [−δ, +δ] (or the stated band) | the interval lies wholly outside the band | the interval straddles the band's edge |

Fewer than 3 kept blocks also gives None (the V3 standard: `V3/README.md:15-20`).

### 1.1 The trigger: mean or one sensor

**H1 (mean).** The governor's thermal decision uses the integer mean of the 34 shire sensors.
**H1′ (max, the alternative).** It uses the hottest sensor.

- **Basis.** Source (§0). The host's `temp_c.minshire[0]` is the same function (`firmware.md:107-115`; `FW:services/thermal_pwr_mgmt.c:709-735`). The hottest sensor's peak-hold is only reported (`firmware.md:121-130, 272-274`). No committed data separates the two rules (`observability.md:76-79`).
- **Measurement 1: TRIG-B, the trace test.** Runs on aifoundry3 in development, aifoundry1 card 1 in validation, and aifoundry2 when cool. It needs O2.
  - At the boot-default log level WARNING (`FW:services/log.c:60`), the ring keeps only CRITICAL, ERROR and WARNING lines (`log.c:227`). The governor's event lines are CRITICAL (`FW:services/thermal_pwr_mgmt.c:672-674, 866-868, 2371-2373`). The host's own request lines are INFO (`FW:rtos_task/command_dispatcher.c:254`).
  - That this works on the cards is shown by the 22 September aifoundry3 dump. It holds only governor lines: 26 `Power throttle down event` and 27 `Power idle state event` [computed here: `strings -n 8 R/docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin`].
  - The V3 dumps, taken at INFO, hold 22–24 `Host_Iface: Received DM request` lines each and no governor line [computed here: `strings` of `V3/raw/<card>/tel/p1/gov/sp1.bin`]. `R/tools/claims-v3/tel/block.sh:183-186, 316, 408` sets and restores INFO. This is why V3's TEL-G saw nothing (`R/docs/findings/03-experiments.md:1238-1239`).
  - aifoundry1 card 1's 0.18.0 has the same default and the same line (`FW18:services/log.c:60`; `FW18:services/thermal_pwr_mgmt.c:596`).
  - **B-neg (the discriminating part).** A *control window* is a stretch of ≥ 1 s (≥ 4 service-processor passes on aifoundry3, 224 ms each; `R/docs/findings/03-experiments.md:1232-1233`) in which, in every sample, the windowed high reads ≥ 67 and the mean reads ≤ 64. The ring must provably cover the window: the run's first launch marker (`Power … event`) is present.
    - H1 predicts 0 thermal events in every control window.
    - H1′ predicts ≥ 1 event in the window, printed with T ≥ 66, because the hottest sensor is then ≥ 66 > 65.
    - Control windows arise naturally in Tier S: at the 64 °C start the high sits 1–2 °C above the mean at idle and 3–4 °C above it under load (`observability.md:163-167`).
  - **B-pos (consistency).** Each event is aligned to host time through the nearest launch marker; on aifoundry3, each kernel start logs `Power throttle down event` (`firmware.md:376-379`). H1 predicts that the host's mean reads ≥ 65 within ±0.5 s of the event in ≥ 90% of events. H1′ predicts that most events fall while the host's mean reads ≤ 64.
  - **Rule.** holds if there are ≥ 5 control windows with 0 events in all of them **and** B-pos is ≥ 90% with ≥ 5 events. fails if ≥ 2 control windows hold an event, or B-pos is < 50%. Otherwise None.
  - The card logging no governor line at all gives None. This is a real possibility on aifoundry1 card 1: its clock never rises (`dfo:5`), which could mean active power management is off (`feasibility.md:147-153`); the trigger needs it (`FW18` same logic, `firmware.md:136-138`).
- **Measurement 2: TRIG-A, the clock test.** Runs on aifoundry2 when cool only (§1.6). It needs no O2.
  - For each run with `--reset-ms 1000`, find:
    - `t_hi` = the first sample at 800 MHz whose windowed high reads ≥ 66;
    - `t_m` = the first sample whose mean reads ≥ 66;
    - `t_down` = the first 800 → lower step with no kernel boundary within ±1 pass.
  - Runs with `t_m − t_hi` ≥ 1.5 s separate the two rules.
  - H1 predicts `t_down − t_m` ∈ [−0.3, +1.2] s. The slack covers one 133 ms pass, sampler phase, and E10's down-steps seen at sampler readings of 64–67 (`firmware.md:340-342`).
  - H1′ predicts `t_down − t_hi` ∈ [−0.3, +1.2] s.
  - **Rule.** holds if ≥ 80% of the separating runs fit H1 and ≤ 1 fits H1′, with ≥ 5 separating runs over ≥ 3 cool periods. fails if ≥ 50% fit H1′. Otherwise None.
- **Falsified by.** Any thermal event printed during a clean control window, or the clock stepping down with the hottest sensor rather than the mean. Either would mean the running firmware differs from the source read.

### 1.2 Placement: the owner's hypothesis, its reverse, and the null

- **H2 (owner: the edges trip later).** The same work on the perimeter (PER16) reaches `t66` later than in the interior (INT16). Prediction `SIGN+` on `L(PER16/INT16)`. Two mechanisms predict the same sign:
  - (M1) the heatsink cools the die's edges and corners better;
  - (M2) sensor coverage: heat from edge tiles spreads partly into regions with no sensor in the mean. Those are the memory strips, about 1.76 mm wide beside columns c1 and c6; the bare N/S die edge; and the I/O and PCIe tiles. The 6 × 6 grid covers about 87% of the die (`observability.md:239-249, 421-431`).

  The host cannot tell M1 from M2 (§5.2).
- **H3 (reverse: the centre trips later).** For example, if the fan's airflow or the heat spreader favours the centre. Prediction `SIGN−` on the same contrast.
- **H4 (null: the mean-rise rate depends on total power only).**
  - |`L(PER16/INT16)`| stays inside ±δ (`EQUIV`), and κ_PER − κ_INT stays inside ±0.05.
  - Basis: a sensor mean over a uniform grid tracks the die average, which in a lumped network depends on total power only (`feasibility.md:235-244`). "Equal flip power gives equal heating regardless of where the flips come from" (`R/docs/findings/12-heat-management.md:49-51`); that statement is about which transistors switch, not where (`observability.md:302-305`).
- **Decision.** H2 and H4 are not exclusive: a small but significant effect can hold both. The report states the combination. "Edges run X% longer, 99% CI [a, b]" is the answer whatever the verdicts.
- **Falsified by.**
  - H2: an interval that includes 0 or lies below it.
  - H3: an interval that includes 0 or lies above it.
  - H4: an interval wholly outside ±δ.

### 1.3 Spreading and linearity

- **H6 (linearity, superposition).** The minion map of UNI32 at 16 per shire is exactly half of INT16 at 32 plus half of PER16 at 32, and also half of each checkerboard at 32. In a linear thermal system with placement-independent power per minion, the responses superpose.
  - Prediction `EQUIV`, band ±0.03: κ_UNI − ½(κ_INT + κ_PER) and κ_UNI − ½(κ_CHKE + κ_CHKO).
  - Model-free check, reported: `t66_UNI` lies between `t66_INT` and `t66_PER` in ≥ 2/3 of blocks.
- **H5 (spreading helps beyond placement).** Spreading the same work over more shires delays the trip beyond superposition, through leakage convexity (hot regions leak more) or hot-spot feedback.
  - Prediction `SIGN+` on the residual κ_UNI − ½(κ_INT + κ_PER) < 0. A lower gain means a later trip.
  - The prior is against it. The leakage-convexity term is estimated at about 0.04 W, below the 0.03–0.08 W repeatability (`observability.md:211-214`).
- **H5 and H6 are exclusive on that residual.** INT16 against UNI32 alone (`L(UNI32/INT16)`) is reported as the owner's "spread against concentrate" number.
- **Falsified by.** H6: a residual wholly outside ±0.03. H5: a residual interval that includes 0 or is positive.

### 1.4 Hot spots: what a one-sensor governor would do (the counterfactual)

**H7 (concentration).** A concentrated placement lifts the hottest sensor above the mean more than a spread one.
- Prediction `SIGN+` on `Δhot(INT16) − Δhot(UNI32)`. [inference: INT16 puts twice the areal power density on half the tiles]
- It has **no DVFS consequence under H1**. It measures how much earlier a max-keyed governor would fire: counterfactual lead ≈ `Δhot` difference / the mean's rise rate at `t66`, computed and labelled as a counterfactual.
- **Caveat.** The firmware applies no per-sensor calibration (`firmware.md:87-93`), so part of any high − mean excess is a fixed sensor offset. The paired difference between placements removes the part common to both.
- **Falsified by.** An interval that includes 0 or lies below it. That would mean the chip spreads heat laterally faster than the sensors can see concentration at the tile scale.

### 1.5 Where on the edge, and the map check (8- and 4-shire groups)

The masks come from `design_sets.json`. Each 8-shire group is 256 minions (32 per shire).

**H8 (memory side).** Tiles beside a memory strip (MEM8, `0x130002e4`: shires 2, 5, 6, 7, 9, 24, 25, 28) couple less to the mean than centre tiles (CEN8, `0x04647010`: 4, 12, 13, 14, 18, 21, 22, 26). Prediction `SIGN+` on `L(MEM8/CEN8)` and `SIGN−` on κ_MEM − κ_CEN.

**H9 (bare edge).** Tiles on the bare N/S die edge (EDGE8, `0x88880909`: 0, 3, 8, 11, 19, 23, 27, 31) couple less than centre tiles. The same prediction on EDGE8 against CEN8.
- MEM8 and EDGE8 together are exactly PER16 [computed here: `design_sets.py` asserts it].
- No order between MEM8 and EDGE8 is predicted; the order is reported.

**H10 (map check).** Heat beside the I/O and PCIe corner warms the I/O sensor relative to the mean more than heat in the far corner.
- Prediction `SIGN+` on `ι(B4NE) − ι(B4SW)`. B4NE is `0x30100020`, shires 5, 20, 28, 29, about 1.5 hops from I/O. B4SW is `0x00080c04`, shires 2, 10, 11, 19, 8 hops away (`observability.md:397, 395, 416-417`).
- Each is 128 minions in a 7 s Tier S launch; `t66` is not used.
- **Why it matters.** Every "corner", "edge" and "centre" label rests on the latency map (`MARTY`), which a fresh search recovered in 12 of 12 restarts on every pass of all three cards (`R/docs/findings/05-claims.md:412`; `V3/results/lat.json` `.items[item=LAT-N2].per_card.*.passes[].search_same_as_marty`). The rotation into the die frame is inferred (`observability.md:262-270`).
- If H10 fails, the INT/PER split is still interior against perimeter of the latency grid, but "beside I/O" and "N/S edge" become unverified.

### 1.6 Across cards, and the clock itself

**H11 (transfer).** Every contrast that holds on aifoundry3 holds with the same sign on the validation cards. Magnitudes are per card, because the thermal networks differ (`R/docs/findings/11-thermal-model.md:134-135`). §3.3 turns this into per-item predictions.

**H12 (the DVFS consequence; aifoundry2 cool only).** The placement that reaches `t66` later also keeps 800 MHz longer before the first thermal down-step.
- **Runs.** Single 7 s launches from a resting die ≤ 62–63 °C (E10's method: `R/tools/ettelem/run_horace_cold.sh:18-33`), at 256 minions: INT16 and PER16 at `--per-shire 16`, UNI32 at 8.
- **Why 256.** It keeps board power well under the 65 W TDP at 800 MHz, so that the power branch stays out:
  - 800 MHz is about 1.9× the dynamic power at 600 MHz (`feasibility.md:217`);
  - random data on 1,024 minions at 800 MHz drew 87.6 W and triggered power steps (`dfo:23`; `firmware.md:345-349`).
- **Observable.** `t_down`, as in TRIG-A, censored at 7 s. In E10, full-chip zeros at 36–39 W stepped down at 5.6–6.1 s (`dfo:22,26`).
- **Prediction.** The same sign as the aifoundry3 result for `L(PER16/INT16)` (§3.3), applied to `ln(t_down_PER / t_down_INT)`.
- **Falsified by.** An interval that includes 0 or has the opposite sign, while `t66` on the same runs has the predicted sign. That would mean the clock does not follow the governor input's timing, a contradiction with H1.

### 1.7 Preconditions (checks, not theories)

**H13 (equal work, equal power).**
- Board switching power is linear in active minions: 25.6 mW per minion at 256 and 512 active (`R/docs/findings/16-dvfs-and-leakage.md:160-162`). That was measured with all 32 shires active; 16 active shires is untested.
- Prediction `EQUIV`, band ±0.5 W, on `sw_W(A) − sw_W(B)` for every registered pair.
- If this fails for a pair, the pair's `t66` item is decided on the power-normalised `L + ln(sw_W_A / sw_W_B)`, and the report says so. [inference: early in the rise, t66 ∝ 1/P]

**P-clk.** Every measured sample is at the card's expected clock. A run failing this is void (§3.4).

### 1.8 What I expect before any data [inference, stated so it can be wrong]

- H1 holds wherever it can be tested, because the running code logs the compared value.
- H4 holds at δ = 10%. H2 shows at most a few-percent effect through M2.
- H6 holds. H5 fails.
- H7 holds, with a `Δhot` difference of 1–2 °C.
- H10 holds.

If so, the answer to the owner is: "the governor watches the average, so placement barely changes how long work runs before throttling; placement changes only the hot spot, which the governor ignores".

---

## 2. Development on ONE card: aifoundry3

### 2.1 Why aifoundry3

- It idles at 55–57 °C, below the 65 °C threshold (`R/docs/findings/14-card-behaviour.md:152`). So a rising mean crosses the governor's real threshold from below.
- The all-shire heater takes it from 56–58 °C to above 65 °C in 20.8–34.5 s (`dfo:14-16`).
- It cooled from 90 °C to 54–55 °C within 900 s. All 407 heater processes exited 0 (`dfo:14-17`).
- There is no neighbour card and no DVFS confound: its clock read 600 MHz in all 397,813 campaign samples (`dfo:3`).
- It logged governor lines at the boot-default level on 22 September (§1.1).
- Costs:
  - Its service-processor pass is 224 ms, the coarsest (`R/docs/findings/03-experiments.md:1232-1233`).
  - A demo service can launch on it without the lock (`R/docs/findings/14-card-behaviour.md:274-276`).
  - Approaching a start temperature near its idle is slow: 225–364 s to reach 55 °C (`V3/AMENDMENTS.md:857-863`).

### 2.2 Workloads and placements

**Heater.** The TensorFMA heater that every V3 block used (`R/tools/claims-v3/lib.sh:42`, `HEATER`):

```
hold10 $HEATER --test fma --type fp32 --pattern none --values randn --shires <mask> --per-shire <n> --seconds <s> --seed 1
```

- `--shires` and `--per-shire` select hart 0 of minions 0 … n−1 of each shire in the mask (`R/workloads/sparsity/host/main.cpp:275-283, 996-997`).
- "Same work" means the same pattern, the same number of active minions and the same seconds, so the same number of TensorFMA operations at the same 600 MHz.
- The runtime log-level race is fixed in this host (`main.cpp:48, 962`).

| Name | `--shires` | `--per-shire` | Minions | Die frame (`observability.md:275-288`) | Est. switching power (25.6 mW/minion) | Used in |
|---|---|---|---|---|---|---|
| INT16 | `0x6477f412` | 32 | 512 | interior 4 × 4 (r1–r4 × c2–c5) | ≈ 13.1 W | S, L16, cool (at 16) |
| PER16 | `0x9b880bed` | 32 | 512 | the perimeter ring: 8 memory-side + 8 N/S-edge tiles, incl. corners S0, S11, S31 | ≈ 13.1 W | S, L16, cool (at 16) |
| UNI32 | `0xffffffff` | 16 | 512 | everywhere | ≈ 13.1 W | S, L16, cool (at 8) |
| CHK16E | `0x4fb04db2` | 32 | 512 | (r + c) even | ≈ 13.1 W | S |
| CHK16O | `0xb04fb24d` | 32 | 512 | (r + c) odd | ≈ 13.1 W | S |
| MEM8 | `0x130002e4` | 32 | 256 | beside the memory strips | ≈ 6.6 W | L8 |
| EDGE8 | `0x88880909` | 32 | 256 | bare N/S die edge | ≈ 6.6 W | L8 |
| CEN8 | `0x04647010` | 32 | 256 | centre band | ≈ 6.6 W | L8 |
| B4NE | `0x30100020` | 32 | 128 | beside I/O and PCIe | ≈ 3.3 W | S (ι only) |
| B4SW | `0x00080c04` | 32 | 128 | the far corner | ≈ 3.3 W | S (ι only) |
| preheat | `0xffffffff` | 24 | 768 | everywhere | ≈ 20 W | before every run |

- Masks and set identities: `design_sets.json` [computed here]. INT16 ∪ PER16 = all 32 shires; MEM8 ∪ EDGE8 = PER16.
- The preheat uses 768 minions, not 1,024, so that aifoundry1 card 1 stays under the 73 W board cap. Its all-shire heater drew 86.2 W (`dfo:18`). The same recipe is used on every card.

### 2.3 Start condition: the strict start, approached from above

Every run starts at the same **falling edge** of the governor's own reading. This is the strict-start method (`R/docs/findings/03-experiments.md:31-43`; launch-state spread ± 0.11 °C, `:45-46`):
1. If the mean is below the preheat target, run 2 s preheat bursts until it reads ≥ the target, at most 30 bursts.
2. Idle, the card open only to the sampler, until the mean first reads S on the way down.
3. Launch.

| Tier | Start edge S | Preheat target | Why |
|---|---|---|---|
| S | 65 → **64** | 68 | At this edge Σ floor(T_i) has just fallen below 34 × 65 = 2,210. The trip needs Σ ≥ 2,244 (`firmware.md:100-102`), so each run must add the same +35 sensor-degrees, +1.03 °C of mean [computed here] |
| L16 | 61 → **60** (R2 may move it to 59–62) | 62 | 6 °C below the trip, about 3–5 °C above aifoundry3's idle |
| L8 | 63 → **62** (R2 may move it to 61–63) | 64 | the 256-minion groups have half the power |

- The runner waits at most 600 s for the edge; otherwise the run is void.
- It records the time spent approaching and the preheat bursts as covariates. They are reported, not used to correct.
- The heat carried over between runs is the largest scatter source: the same workload took 107 s against 162–167 s from the same reading (`R/docs/findings/12-heat-management.md:52-55`). The fixed preheat-then-edge recipe plus shuffled blocks is the V3 answer to that (`03-experiments.md:41-43`).

### 2.4 Sampler, resets, trace

- **Sampler.** One 10 Hz sampler per run, `ettelem sample --every-ms 100 --reset-ms 1000`, running from the run's preheat to its end.
  - Started with lib's `start_sampler`, which retries and drains once (`lib.sh:146-162`).
  - Stopped with SIGTERM only (`lib.sh:163-176`).
  - The live die reading comes from the sampler's own output, never from a second opener (`idle/block.sh:113-124`).
  - The resets clear the peak-hold registers (`observability.md:118-129`), restart the rails' running average (f(1 s) = 0.93, `R/docs/findings/05-claims.md:441`) and change the shared min/max that other users see (`V3/PLAN3.md:856`). Hence the other-user check before each block. On aifoundry1 card 1 a reset window failed once (`R/docs/findings/03-experiments.md:1237-1238`); a failed-reset window is dropped from `Δhot`.
- **Trace (only with O2).**
  - At block start, before the first sampler: `ettelem-hp loglevel warning`, then an `sptrace` of the idle ring.
  - After each run, once its sampler has stopped: `sptrace` → `trace-rNN.bin`.
  - At block end: restore the level found at block start. It is inferred from the first dump: host-request lines mean INFO (`FW:rtos_task/command_dispatcher.c:254`). If nothing but governor lines, restore WARNING.
  - The ring is 4 KB (`parse_sptrace_voltage.py:14-17`), about 58 lines of about 70 bytes. At WARNING a run adds 2 lines per launch on aifoundry3 plus 1–2 thermal lines. A Tier S run of ≤ 20 preheat bursts fits. For Tier L chains only the last ≈ 25 launches survive; the thermal event at the crossing is 2 launches before the stop, so it is kept.
  - At the 600 MHz floor the thermal loop logs nothing more, because `set_minion_operating_point` returns early when the frequency is unchanged (`FW:services/thermal_pwr_mgmt.c:1788-1791`).

### 2.5 Run specifications

- **Tier S run.** Strict start at S = 64, then one `--seconds 7` launch of the placement. The process takes ≈ 7.7 s: aifoundry3's 2 s heater processes take a median 2,706 ms (`dfo:17`). The runner is `hold10`, and E10 used 7 s the same way (`run_horace_cold.sh:30-32`). Then 10 s of idle with the sampler running, for `κ`, and the sampler stop and trace.
- **Tier L run (O1 only).**
  - Strict start at S_L, then back-to-back 2 s launches of the placement.
  - The chain stops 2 launches after the live mean first reads ≥ 66, or at the chain cap of 150 s (≈ 55 launches). Stopping soon after the crossing keeps the die near 67 °C and shortens the next approach (`feasibility.md:269`).
  - Then the sampler stop and trace.
  - The median gap between aifoundry3's processes is 22 ms (`dfo:17`). The gap overhead is identical across placements, so `t66` is wall time from `t0`. The busy-time version is reported.

### 2.6 Blocks and repeats

**Tier S block.** Seven runs in a shuffled order: INT16, PER16, UNI32, CHK16E, CHK16O, B4NE, B4SW.

**Tier L block.** Six runs:
- L16: INT16, PER16, UNI32 from S_L;
- L8: MEM8, EDGE8, CEN8 from S_L8;
- shuffled within each half, the halves' order alternating by block.

Each registered contrast is a within-block pair. The V3 floor is ≥ 3 independent repeats per card (`V3/README.md:15-20`). Development uses 3 blocks per round and 4 in R3; validation uses 5 per card (df 4).

### 2.7 Safety stops (enforced in `block.sh`, read from the live sampler)

The firmware gives no protection above its 600 MHz floor: aifoundry2 ran at a 103 °C mean (high 106) at 600 MHz (`dfo:29`), and the PMIC's 75 °C alarm reads a register that stays at 0 (`dfo:4`; `FW:services/thermal_pwr_mgmt.c:2995`, per `feasibility.md:69-71`). So the script enforces:
- **Stop launching and end the run** if, for 2 consecutive samples, the mean reads ≥ 80, the windowed high reads ≥ 85, or `board_w` reads ≥ 73 W.
  - The protocol itself never needs more than about 68–70 °C.
  - These caps sit inside the precedents: E12's 90 °C / 73 W (`R/docs/findings/03-experiments.md:249-252`); V3-IDLE's 88–90 °C (`idle/block.sh:13-15`).
- **The preheat stops** at the target, at 30 bursts, or at 80 °C.
- **Abort the block** (the V3 exit codes, `idle/block.sh:134-143`):
  - on 3 consecutive heater exits ≠ 0 (exit 1);
  - if another user, a foreign device process, or a rise in the `et_soc1` use count appears (exit 3, the card left closed; `idle/block.sh:73-111, 181-183, 205-210`);
  - if the sampler goes stale for more than 3 s (exit 1).
- **Every device process** runs under `hold10` (`lib.sh:99-100`). There is no TDP, threshold, clock, reset, firmware or driver change (`R/AGENT.md:155`).
- **The log-level change** is the one state change, and only with O2.

### 2.8 Rounds: content, decision rules fixed now, what may change, card minutes

| Round | Content | Card min (est.) |
|---|---|---|
| **R0** | `V3_DRY=1` run of each block type, then `--smoke`: sampler, 2 preheat bursts, one 2 s launch of INT16, `sptrace`, `reduce.py --check-pass` (`R/AGENT.md:234-242`) | 3 |
| **R1** Tier S scouting | (a) Trace probe (O2): WARNING, idle `sptrace`, 3 preheat bursts, `sptrace`. It must show ≥ 3 `Power throttle down` lines and 0 `Host_Iface` lines. (b) UNI32 twice at S = 64. (c) 3 Tier S blocks | ≈ 50 |
| **R2** Tier L scouting (O1), else 3 more Tier S blocks | (a) UNI32 twice at S_L = 60; CEN8 twice at S_L8 = 62. (b) 3 Tier L blocks | ≈ 90 (Tier S: ≈ 40) |
| **R3** rehearsal | 4 blocks of the exact protocol the pre-registration will freeze (Tier S, plus Tier L if kept), run by the same code | ≈ 160 |
| **Total** | about 5 h of card time; 15–40 h wall-clock, on ≥ 2 sessions via `queue.sh` | ≈ 300 |

Per-run time estimates [inference]:
- Tier S: preheat 3–6 bursts, an approach of 20–120 s (median 63 s on aifoundry2: `14-card-behaviour.md:131`) and a 7 s launch, so about 2 min per run and 14 min per block.
- Tier L: an approach of 1–3 min and a chain of 40–150 s, so about 4 min per run and 25 min per block.

**Decision rules between rounds (fixed now):**
- **D-trace (after R1a).**
  - If the probe shows governor lines at WARNING, TRIG-B is kept.
  - If it shows host-request lines at WARNING, the level command did not take: TRIG-B is dropped and the level restored.
  - If it shows no line at all, TRIG-B is dropped.
- **D-S (after R1).** Tier S `t66` stays a registered observable only if ≤ 20% of INT16 and PER16 runs are censored at 7 s. Otherwise, in Tier S:
  - `κ` replaces `t66` for H2–H4;
  - `t66` is reported only;
  - B-neg and B-pos (TRIG-B), H6, H7, H10 and H13 are unaffected.
- **D-L16 (after R2a).** S_L is set so that UNI32's median `t66` lies in 40–120 s, with a median approach ≤ 180 s. If `t66` < 40 s, lower S_L by 1 (not below 59). If > 120 s or censored, raise it by 1 (not above 62).
- **D-L8.** If CEN8 is censored at 150 s from S_L8 in both scouting runs even at 63, the L8 half is dropped and H8 and H9 are INSUFFICIENT by design.
- **D-blocks (after R3).** The number of validation blocks is 5. It is raised to 8 only if R3's 99% half-width on `L(PER16/INT16)` exceeds δ at 4 blocks and 8 blocks would bring it under δ, scaling by t/√n.

**What may change between rounds:**
- S, S_L and S_L8 within the ranges above;
- preheat targets within ±2 °C;
- the chain cap within 100–150 s;
- dropping (never adding) placements or a tier;
- the number of blocks;
- code fixes that change no observable definition.

**What may not change:**
- the observables of §1.0 and their definitions;
- δ and the item bands;
- the unit, the statistic and the direction of any hypothesis.

Development data are never pooled into validation. R3 is pooled with earlier development blocks only if their parameters are identical.

---

## 3. Validation on the other cards (predictions frozen, no iteration)

### 3.1 Cards

**aifoundry1 card 1 (primary).**
- It idles below the threshold, at 56–57 °C after cooling (`dfo:18-20`).
- It heats fast: 61 → above 65 °C in 5.4 s with all shires (`dfo:18`). Tier S therefore crosses well inside 7 s.
- It has a different firmware, 1.2.0 (`firmware.md:44`), and a different chassis.
- Practicalities:
  - `V3_DEVICE=1`, `ET_DEVICES=1`, lock `etsoc-shire1` (`lib.sh:22-28, 183-186`).
  - Card 0 must hold no process and no lock holder for the whole block (`feasibility.md:281-285`).
  - Each validation block is split into its Tier S half and its Tier L half, two queue entries of ≤ 20–25 min, at least 15 min apart, to limit heating of the shared chassis air (`idle/block.sh:216`).
  - Abort on a CI job (`lib.sh:59-60`).
- TRIG-B there may come out None if the card logs no governor line (§1.1).

**aifoundry2 (conditional).** Only the DVFS items: TRIG-A, H12 and TRIG-B under O2.
- **Gate.** A 1 s die reading after ≥ 6 h with no launch reads ≤ 62 °C (`feasibility.md:180-182`). The V3-COOL waiting script polls with the card otherwise closed (`V3/PLAN3.md:1021`).
- **Each cool period is one block:** INT16 at 16, PER16 at 16 and UNI32 at 8, each twice, in a shuffled order. Each run waits until the mean reads ≤ 63 °C, as E10 did, 0–62 s between runs (`feasibility.md:104`). `--reset-ms 1000` is on.
- **Stopping.** At least 3 cool periods are required. If none comes within 7 days of the first validation block, aifoundry2's items are INSUFFICIENT: the same rule as V3-COOL's "if no cool period comes within a week, stop" (`V3/PLAN3.md:1035`).
- Its warm state (67–99 °C in the campaign, `dfo:7`) is not used: it would test only the placement ranking at 80 °C, not DVFS.

### 3.2 How predictions are frozen

After R3 and before the first validation block, write `PREREG.md` and `prereg.json`. The proposed home is `R/docs/reports/data/2026-09-2x-heatplace/`; committing is the owner's call. The files hold:
1. Every item of §1 with its card set, placements, prediction type (`SIGN+`, `SIGN−` or `EQUIV`), band and rule, chosen by the rule of §3.3.
2. The frozen parameters per card: S, S_L, S_L8, preheat targets, chain cap, placements kept, number of blocks, seeds (block seed = 1000 × card index + pass), and the void and re-run rules of §3.4.
3. aifoundry3's development values per item, with their 99% intervals, marked "reported, not tested".
4. The sha256 of `hp/reduce.py`, `hp/hplib.py`, `hp/sptrace_events.py`, `hp/block.sh` and `hp/placements.json`.

`params-val-<card>.json` carries the sha256 of `PREREG.md`. `block.sh` with `HP_ROUND=val` refuses to start if the file, or any hashed code file, differs. This follows V3's "committed before the first run" with recorded hashes (`V3/README.md:3-5, 28`).

### 3.3 How the development result becomes each validation prediction (the rule is fixed now)

For each item with a contrast, look at aifoundry3's R3 result (plus identical earlier blocks):
- 99% interval excludes 0 → the validation prediction is the same sign (`SIGN+` or `SIGN−`).
- Interval inside the item's equivalence band → `EQUIV`.
- Neither → `EQUIV`, the null, the conservative default for an effect not shown.

TRIG-B is predicted "holds" (H1) on every card whatever the development result, because that prediction comes from source.

H11 is not a separate test: it holds when every registered sign item passes on every validation card.

Magnitudes are not predicted across cards, because the networks differ (`11-thermal-model.md:134-135`). Each card's magnitude is reported with its interval.

### 3.4 Repeats, voids and re-runs (pre-registered)

- aifoundry1 card 1: 5 blocks (8 if D-blocks said so), on ≥ 2 different days or sessions ≥ 4 h apart. aifoundry2: ≥ 3 cool periods.
- **A run is void** if any of these holds:
  - its heater exited ≠ 0 (aifoundry3's old-binary crash signature is 1.08 s: `14-card-behaviour.md:304-318`);
  - a measured sample is off the expected clock;
  - its start edge was not reached within 600 s;
  - the sampler had a gap > 1 s in the measured window;
  - a safety stop fired.
- A void run is re-run once, at the end of its block, in the same position of the pair. A second void drops that placement from the block, and its pairs from `L`.
- **A block is kept** if every registered pair in it is complete.
- **Aborted blocks** (intrusion, exit 3) are re-queued whole. Their data are kept on disk and never used.

### 3.5 Outcome words (as in the version-3 check)

For each item, over the validation cards only, from holds/fails/None per card:
- **PASS** if it holds on every validation card;
- **FAIL** if it fails on every one;
- **CARD-DIFFERENT** if it holds on some and fails on others, with per-card values;
- **INSUFFICIENT** if any validation card gives None: fewer than 3 kept blocks, the observable unavailable (no trace lines, no cool period), or an `EQUIV` interval straddling its band.

This is `card_verdicts` of `R/tools/claims-v3/idle/reduce.py:454-463`, reused. aifoundry3's values are REPORTED, as V3 did for cards not registered for an item (`idle/reduce.py:30-36`). A failed prediction is reported as failed (`R/AGENT.md:249-253`).

### 3.6 No iteration after validation

- Once the first validation block starts, the code and parameters stay as hashed.
- A reducer bug found later is fixed as an amendment written before rerunning the reducer, with both outcomes shown (the V3 amendments practice: `R/AGENT.md:249-253`; `V3/AMENDMENTS.md`).
- No placement, band, start temperature or card is added, dropped or re-chosen after validation data exist.
- No validation run is repeated except under §3.4.

### 3.7 Card minutes (validation)

| Card | Content | Est. |
|---|---|---|
| aifoundry1 card 1 | 5 × (Tier S ≈ 12 min + Tier L ≈ 20 min); it heats faster than aifoundry3 | ≈ 160 min |
| aifoundry2 | ≥ 3 cool periods × 6 runs × ≈ 1.5 min, plus a 1 s gate reading every few hours | ≈ 30–45 min |

---

## 4. Code to write (the version-3 framework: `R/AGENT.md:221-253`)

### 4.1 Files: new directory `R/tools/claims-v3/hp/`, experiments `hp-r0` … `hp-r3`, `hp-val`, `hp-cool`

| File | What |
|---|---|
| `hp/block.sh <pass> [--smoke]` | One block (env `HP_ROUND=r1\|r2\|r3\|val\|cool`, `HP_TIER=S\|L`). It sources `../lib.sh` and reuses `idle/block.sh`'s intrusion machinery (`modcount`, `scan_procs`, `foreign_procs`, `abort`, `live_reading`: `idle/block.sh:68-143`). Flow in §4.2 |
| `hp/hplib.py` | Loads and validates `params-<round>[-<card>].json`. It builds the shuffled run list (seeded), checks the PREREG hash in `val` mode, reads the live die and high from the sampler file for the stop tests, and runs the post-run checks: clock, heater rc, sampler gaps, edge reached |
| `hp/placements.json` | Frozen masks and features, generated by `hp/placements.py`, a copy of `placements.py` + `design_sets.py` from this directory, with its set identities asserted |
| `hp/params-r1.json` … `params-val-aifoundry1-c1.json`, `params-cool.json` | Per-round and per-card parameters (§2.3–2.8) |
| `hp/sptrace_events.py` | Governor lines from an SP ring dump, ordered by timestamp. It imports `ring_entries` from `R/tools/ettelem/parse_sptrace_voltage.py` and parses the five CRITICAL formats of §1.0. `--self-test`: on `R/docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin` it must find 26 throttle-down and 27 idle-state lines |
| `hp/reduce.py` | Per-run observables (§1.0), including the κ fit with `flip_thermal_model.py`'s `nnls` and `lowpass`, imported unchanged; per-block contrasts; per-card intervals; items and outcome words (`card_verdicts`). `--check-pass <dir>` for smoke; `--dev` prints the §2.8 decision-rule outputs; `--prereg prereg.json --out hp.json` for validation |
| `hp/README.md` | Rules and departures from this design, written before any data (the `gs/README.md` pattern: `R/AGENT.md:230-232`) |
| `schedule-hp-aifoundry3.txt`, `-aifoundry1-c1.txt`, `-aifoundry2.txt` | Queue schedules for `queue.sh` (`R/AGENT.md:243-248`) |
| `R/tools/ettelem/ettelem.cpp` (O2 only) | `loglevel warning` → filter 2. Today anything but `debug` maps to INFO, 3 (`ettelem.cpp:201`), so `warning` would silently set INFO. The level values are `ETP/et-trace/include/et-trace/encoder.h:208-214`, consistent with `ettelem.cpp:201`'s INFO 3 / DEBUG 4. It is built into **`build/ettelem-hp/`**, never `build/ettelem/`, which the campaign's blocks use (`R/AGENT.md:192-198`), and used only for `loglevel` |

### 4.2 `block.sh` flow for one block

1. **The card must be free.** Run `others_present` and `ours_running`, check the `et_soc1` count, and on aifoundry1 check card 0 (holders, lock) (`lib.sh:62-97`; `idle/block.sh:145-151`). If not free, exit 3.
2. **Begin.** `block_begin hp-<round> <pass>` takes the card lock and writes `code.sha256` (`lib.sh:179-192`). In `val`, verify the PREREG hash. Write `block.json`-style `plan.json`: the seed, the run order and the parameters.
3. **Log level (O2).** `ettelem-hp sptrace` idle dump → infer the level found; `ettelem-hp loglevel warning`.
4. **For each run in the plan:**
   - Start the sampler (`--reset-ms 1000`).
   - Preheat and edge-wait, reading the die from the sampler.
   - Mark `run_start`.
   - Launch: Tier S is one 7 s launch; Tier L is the chain with the live stop rule (mean ≥ 66, then 2 more launches) and the cap. The safety tests run before every launch.
   - Mark `run_end`.
   - Stop the sampler with SIGTERM.
   - With O2, `sptrace trace-rNN.bin`.
   - gzip, then post-run checks, then void → re-run queue.
   - Write `runs.jsonl`: placement, mask, per-shire, `t_start`/`t_end`, rc, edge wait, preheat bursts and void reason.
5. **End.** Restore the log level; `reduce.py --check-pass`; `block_end ok|fail`.

Output per block, in `build/claims-v3/<card>/hp-<round>/p<pass>/`:
- `plan.json`, `runs.jsonl`, `marks.jsonl`;
- `telemetry-rNN.jsonl.gz`, `trace-rNN.bin`, `heater.out.gz`;
- `check.json`, `block.json`, `code.sha256`.

### 4.3 Reducer items

| Item | Hypotheses | Tier and card | Statistic |
|---|---|---|---|
| TRIG-B | H1 vs H1′ | S, L (aifoundry3, aifoundry1 card 1; aifoundry2 cool) | control-window event counts; B-pos share |
| TRIG-A | H1 vs H1′ | cool (aifoundry2) | share of separating runs fitting each rule |
| PLACE-t | H2 / H3 / H4 | L16 (primary), S (if D-S kept `t66`) | `L(PER16/INT16)` |
| PLACE-κ | H2 / H3 / H4 | S, L16 | κ_PER − κ_INT |
| SPREAD-t | owner's "spread vs concentrate" | L16, S | `L(UNI32/INT16)` (reported with a `SIGN`/`EQUIV` prediction per §3.3) |
| LIN | H6 vs H5 | S | two superposition residuals on κ |
| CONC | H7 | S | `Δhot(INT16) − Δhot(UNI32)` |
| MEM, EDGE | H8, H9 | L8 | `L(MEM8/CEN8)`, `L(EDGE8/CEN8)`; κ differences |
| MAP | H10 | S | `ι(B4NE) − ι(B4SW)` |
| DVFS-PLACE | H12 | cool (aifoundry2) | ln(`t_down` PER/INT) |
| POWER | H13 | all | `sw_W` differences |

### 4.4 From items to the owner's two questions, and to "which theories survived"

**Q1: "does DVFS kick in on the average temperature or on one sensor?"**
- The answer comes first from source (§0, cited).
- Then it gets its on-card support: TRIG-B on aifoundry3 (development) and aifoundry1 card 1, and TRIG-A and TRIG-B on aifoundry2 when cool.
- Wording template: "The governor compares the mean of the 34 shire sensors (source). On <cards>, the firmware's own throttle event fired only when the mean read 66 °C, never in <n> windows where the hottest sensor read ≥ 67 °C with the mean ≤ 64 °C (TRIG-B <outcome>)."

**Q2: "does placement let the same computation run longer before DVFS kicks in?"**
- The primary number is PLACE-t: "edges vs centre: <X>% (99% CI) longer to the trip on <card>". PLACE-κ says why in watts.
- SPREAD-t, MEM and EDGE refine it.
- CONC gives the counterfactual: "a one-sensor governor would fire <Y> s earlier for the concentrated placement".
- DVFS-PLACE shows the clock consequence on aifoundry2.
- MAP qualifies the geometry.

**Theories survived.** The reducer emits one line per theory:

| Theory | Survived if |
|---|---|
| H1 (mean trigger) | TRIG-B and TRIG-A PASS (CARD-DIFFERENT gives per card) |
| H1′ (max trigger) | the same items FAIL in H1′'s direction |
| H2 (owner: edges later) | PLACE-t is registered `SIGN+` and PASSes (PLACE-κ agreeing) |
| H3 (centre later) | the same items, registered `SIGN−` |
| H4 (null) | PLACE-t is `EQUIV` and PASSes (the result can say "H2 survived at +4%, and H4 too: below the 10% bar") |
| H5 / H6 | LIN |
| H7 | CONC |
| H8 / H9 | MEM / EDGE |
| H10 | MAP |
| H11 | every registered `SIGN` item PASS |
| H12 | DVFS-PLACE |

INSUFFICIENT means "not tested", never "survived".

---

## 5. Risks, and what host observables cannot answer

### 5.1 Risks

1. **The 10 s rule decides the design (O1).**
   - Without chains, Tier S alone probes only the seconds after a start 1 °C below the trip.
   - On aifoundry3 the 512-minion placements may not add +1.03 °C within 7 s. The heater with all shires takes 21–35 s for +8 °C (`dfo:14-16`) [inference: about 0.1–0.2 °C/s for half the minions]. That is why D-S exists.
   - The owner's question about running *longer* then gets only a seconds-scale answer.
2. **Effect below resolution.**
   - The lumped physics predicts a small placement effect (§1.8).
   - The start state scatters by ± 0.11 °C (`03-experiments.md:45-46`), which is about ± 0.5–1 s of `t66` at 0.1–0.2 °C/s.
   - Timing is quantised to one service-processor pass: 224 ms on aifoundry3, 135 ms on aifoundry1 card 1 (`03-experiments.md:1232-1233`).
   - An EQUIV interval that straddles δ ends as INSUFFICIENT, not as a null.
3. **Heatsink history** (`12-heat-management.md:52-55`) and **room drift**: the die once fell 12 °C under an unchanged workload (`14-card-behaviour.md:272-273`). Mitigations: fixed preheat and edge, shuffled blocks, sessions on ≥ 2 days, covariates recorded.
4. **Power per placement.**
   - Minion power linearity was measured only with all 32 shires active (`16-dvfs-and-leakage.md:160-162`).
   - Shire-to-shire process variation is unmeasured.
   - H13 checks this, and the power-normalised contrast takes over if needed.
5. **Uncalibrated sensors.** The firmware reads no fuse calibration (`firmware.md:87-93`; PRM Table 15-48 per `firmware.md:91-92`). The "hottest sensor" may be a fixed offset. CONC and TRIG-B's control windows use the high only relative to the same card and block.
6. **The map.** The die orientation is inferred (`observability.md:262-270`, `:450-453`). MAP checks it partly.
7. **The trace test (O2).**
   - The log level is service-processor state that V3 changed to INFO (`tel/block.sh:183-186`). Setting WARNING restores the boot default (`FW:services/log.c:60`), but it is still a change, and it is restored at block end.
   - The ring is 4 KB.
   - aifoundry1 card 1 may log nothing.
8. **Other users.**
   - A demo service on aifoundry3 can launch without the lock (`14-card-behaviour.md:274-276`).
   - CI runners run on aifoundry1 and aifoundry2 (`lib.sh:59-60`).
   - The `--reset-ms` resets change shared min/max that other viewers see (`V3/PLAN3.md:856`).
   - Card 0 shares aifoundry1's chassis and must stay idle (`feasibility.md:281-285`).
9. **aifoundry2's cool gate** is calendar-bound. It passed once in the repo's history of five days (E10: `feasibility.md:107-113`). H12 and TRIG-A may end INSUFFICIENT.
10. **The research notes disagree on one point.** `observability.md:87` says aifoundry1 card 1's clock *can* show onset. Its telemetry says otherwise: 600 MHz in all 359,657 samples, including 11,446 samples at 58–64 °C and 45–63 W, and a since-boot maximum of 600 (`dfo:5`; `feasibility.md:147-153`). This design follows the data: no clock observable on that card.
11. **Builds in use.** Never rebuild into a build directory the campaign queue uses, and never deploy onto a host whose queue runs (`R/AGENT.md:192-204`). `ettelem-hp` gets its own directory.

### 5.2 What host observables cannot answer

- **Where the heat is.** No per-shire temperature reaches the host:
  - the service processor alone can access the sensor registers (`MAN/ET Programmer's Reference Manual.pdf` Table 15-37, p. 400);
  - the per-shire print has no caller (`FW:driver/pvt_controller.c:1204, 1410`; `observability.md:140-154`);
  - exposing per-shire temperatures needs a rebuilt, possibly signed, service-processor image (`observability.md:219-229`), which the lab rules forbid (`R/AGENT.md:155`).

  So "the corners are *better cooled*" (M1) cannot be told apart from "edge heat escapes into unsensed silicon" (M2). Both move the mean the same way (§1.2). The experiment answers the scheduler's question, "does the governor's input rise more slowly", not the physics question of why.
- **Mean against max, on cards whose clock cannot move.**
  - Without O2, the host has no way to see the governor's decision on aifoundry3 or aifoundry1 card 1. The mean-against-max answer there rests on the source alone, plus the host reading being the same function (`firmware.md:107-115`).
  - With O2 it rests on the running firmware's own log line: still indirect, but it comes from the binary on the card, not from source reading.
  - A clock-level test exists only on aifoundry2 on a cool day (TRIG-A).
- **The throughput cost of the step.** It appears only on aifoundry2 when cool. On aifoundry3 and aifoundry1 card 1 the governor may decide to step down, but it is already at its 600 MHz floor (`feasibility.md:60-64`), so the "run longer before DVFS" answer there is in terms of the decision time, not lost operations.
- **Long horizons.**
  - Even with O1, a Tier L chain lasts at most 150 s.
  - The 400 s thermal stage holds most of the resistance (`11-thermal-model.md:29-31`).
  - Placement effects at the minutes-to-steady-state scale stay untested. They are V3-LONG's territory (E47, not run: `03-experiments.md:1415-1425`).
- **The hardware trip.** The PMIC's 75 °C path reads a register that stays at 0 (`dfo:4`), and every cap here sits far below 75 °C on the mean. That path is not exercised and not tested.
- **Other operating points and patterns.** All placements run random-data fp32 TensorFMA at 600 MHz. aifoundry2's cool runs use 800 MHz. Nothing is claimed for other patterns or clocks.

---

## 6. Owner decisions needed before any card time

| # | Decision | Default if not given |
|---|---|---|
| **O1** | May a run chain back-to-back 2 s launches for up to 150 s (Tier L)? The rule is `R/CLAUDE.md:73`; its restatement for time-to-cap measurements is `V3/PLAN3.md:1072, 1136` and owner decision D1 (`V3/README.md:23`). The precedent is V3-IDLE's accepted 2 s heater chains of up to 900 s (`idle/block.sh:59`) | **No**: Tier S only, and the placement question is answered at the seconds scale |
| **O2** | May a block set the service processor's log level to WARNING, its boot default (`FW:services/log.c:60`), through `ettelem-hp loglevel warning`, and restore the level it found at the end? And may `ettelem.cpp` get that one-line change, built into `build/ettelem-hp/`? | **No**: TRIG-B is dropped, and the mean-against-max question on aifoundry3 and aifoundry1 card 1 rests on source only |
| **O3** | May aifoundry2 be polled with a 1 s die reading every few hours, for up to 7 days, waiting for a cool morning (the V3-COOL pattern)? And may aifoundry1 card 1 be used with card 0 idle? | aifoundry2 items INSUFFICIENT; validation on aifoundry1 card 1 only |
| O4 | Where the pre-registration lives and whether it is committed (§3.2). The experiment number: E50 is the next free one after E49 (`03-experiments.md:1427`); E48 is taken by V3-GS (`R/tools/claims-v3/gs/README.md:3-10`) | Scratchpad plus hash only; no commit |
