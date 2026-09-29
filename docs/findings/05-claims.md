# Claim index: every number, and where it came from

If a number from this work turns up somewhere else — in a summary, a slide, another agent's answer — this is
where to check it. Each row gives the value, how it was obtained, the experiment or resource it came from, and
the file and field that hold the evidence.

**Kind:** `M` measured on the card · `S` simulated from RTL · `F` fitted to measurements · `P` predicted by a
model before it was measured · `D` derived: arithmetic on measured numbers, no new measurement · `R` read from
source code (firmware or RTL) · `X` external source · `A` assumption. Combined kinds (e.g. `M, F`) mean a measured
input and a fitted slope; `P→M` is a prediction later measured.

Where a later session re-measured a number, the older row says so and points to the newer one; quote the newer.
Rows that cite R3 for the governor describe the firmware source at `353f20e`; the cards' own trace strings match an
older build (R3), so what the card runs may differ. Since 28 September the section "The governor on the cards' own
build, and DV2" has the cards' builds read from source and E51's development data, "Heat placement" E52's, and
"The effect of overheating" E53's pre-registered verdicts and the re-read record;
rows marked **dev** there are development data, not validated. Terms are defined in [README.md](README.md#terms).

Paths are relative to the repository root. `DATA` means `docs/reports/data/2026-09-21-horace-aifoundry2/`,
`DATA2` means `docs/reports/data/2026-09-22-dvfs-aifoundry2/`, `DATA3` means
`docs/reports/data/2026-09-22-horace-aifoundry3/` and `DATAC` means `docs/reports/data/2026-09-22-cards/`.

---

## The card and its operating point

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Minion core voltage under load, on die | **516–518 mV** | M | E9 | `DATA/strict/telemetry.jsonl.gz`, field `die_mv.minion`, every sample of every run |
| Minion rail set point | 520 mV | M | E9 | same file, `reg_mv.minion` |
| Minion clock under load | **600 MHz** | M | E9, E12, E15, E16 | same file, `mhz.minion`; constant in every sample of E9, E12, E15 and E16 (launched at 80 °C); below about 68 °C it can lift mid-burst (E29) |
| The other operating points | 700 MHz at 568 mV, **800 MHz at 618 mV** (as in the DVFS rows below) | M | E10 | `DATA/cold1/telemetry.jsonl.gz`, `mhz.minion` with `die_mv.minion` |
| Minions used by these workloads | 1,024 (32 shires × 32) of 1,088 on the chip | M | E9 | `DATA/strict/runs.jsonl`, field `minions` |
| Cycles per 16×16×16 fp32 `TensorFMA` | **546.001**, identical for every data pattern | M | E9 | `DATA/strict/runs.jsonl`, `cycles_per_op` |
| Same, fp16 / int8 | 546 / 318 (A and B in the L1 scratchpad; the matmul benchmark's loop, with B streamed through TenB, takes 529 / 280) | M | E15, R4 | `DATA/ablation/runs.jsonl` |
| Arithmetic rate at 600 MHz | **9.18 TFLOPS** (4.59 × 10¹² multiply-adds per second) | M | E9 | `DATA/horace3.json`, `patterns.*.tflops` |
| Idle board power at 80 °C | **36.3 W** | M | E9 | `DATA/horace3.json`, `patterns.*.p_before` |
| Idle board power at 62 °C, after a night idle | **26.7 W** | M | E10 | `DATA/cold1/telemetry.jsonl.gz` before the first launch |
| Die temperature resolution | whole degrees (one number, the mean of 34 minion-shire sensors) | M | E5 | any `telemetry.jsonl.gz`, `temp_c.minshire[0]` |
| Temperature field `pmic_sys` repeats the minion-shire mean | 3,679 of 3,681 samples on 20 Sep (the other two differ by 1 °C) | M, R | E5, E7, E8; R3 (`get_module_current_temperature`) | `docs/reports/data/2026-09-20-power-aifoundry2/*-telemetry.jsonl`, `temp_c.pmic` against `temp_c.minshire[0]` |
| Peak-hold low of the minion-shire sensors, 20 Sep | 62 °C in all 3,681 samples (the SP's minimum of the mean: 63 °C) | M | E5, E7, E8 | same files, `temp_c.minshire[1]`, `sp.minion_c[1]` |
| Peak-hold high less the SP's maximum of the mean, 20 Sep | 3 °C after every rise (84/87 … 90/93); 2 °C for 1.5–3 s after each record in the load step, up to 27 s in Horace | M, R | E5, E7, E8; R3 (`Thermal_Pwr_Mgmt_Init_OP_Stats` resets both, via `pvt_hilo_reset`) | same files, `temp_c.minshire[2]` − `sp.minion_c[2]` |
| The same fields on both cards | low = the SP's minimum of the mean − 1 °C in every sample (41 logs, 174,233 + 172,176 samples, 20–24 Sep); at each of 9 rises the high read 3 °C above the mean (4 °C once); on aifoundry2 each of the mean's 6 new records was followed by a rise of the high (settled 3 °C above the SP maximum); on aifoundry3 2 of 3 were, and after the 61 °C record the high did not move for the remaining 444 s of the log (the hottest shire then at most 2 °C above the mean; settled 2 °C) | M, R | every committed ettelem log, E5–E32 | `tools/ettelem/host_temp_fields.py` → `HOST_TEMP.cards` |
| Per-shire on-die voltage at idle, 34 minion shires (20 Sep) | minion rail 517–521 mV now, lows 513 (shires 0, 1, 2, 18) to 520, highs to 522; SRAM 703–707; mesh 483–486 | M | E6 | `docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json` (= `summary.json` `shires`), regenerated byte for byte from `raw/sp1.bin` by `tools/ettelem/parse_sptrace_voltage.py` |
| Board power resolution / refresh | 10 mW; a new value once per service-processor pass, which a poller lengthens: under ettelem at 10 Hz every 155.5–157 ms on aifoundry2, 156.5–158.5 on aifoundry1's card 1 and 262.5–264 on aifoundry3; with nothing polling the pass is 133.2, 134.8 and 224.1–224.5 ms (E41, rows in "Version 3" below). Before E41 this row said 133 ms on aifoundry2 and about 250 ms on aifoundry3 (cause not established) | M | E5, E20, E27, E41 | `tools/ettelem/ettelem.cpp`, `DM_CMD_GET_MODULE_POWER`; `V3R/tel.json`, `.items[item=TEL-S].per_card.<card>.passes[]` and `[item=TEL-P1]`; how often `board_w` changes in any `telemetry.jsonl.gz` of each card |
| The rails' running average (the PMIC's) | a step reaches 55–57% after 1 s and 83–84% after 2 s, τ ≈ 1.15–1.22 s (aifoundry2 57% / 84%, τ 1.15 s over 242 bursts; aifoundry3 55% / 83%, τ 1.22 s over 229) | M | E27 | `docs/reports/data/2026-09-23-energy-manual/catalogue.json`, `rail_filter` (fall after the board's step-down; bursts with more than 8 W on the minion rail and 4 s of idle either side) |
| Firmware governor thresholds | 65 °C software, 65 W TDP; 75 °C / 75 W catastrophic (the PMIC's own alarm thresholds; it does not act on the die's temperature on these cards: "The governor on the cards' own build, and DV2" below) | X | R3 (source at `353f20e`; the cards' trace strings match an older build) | `external/et-platform` at `353f20e`, `ServiceProcessorBL2/include/thermal_pwr_mgmt.h` and `bl2_pmic_controller.h` |

## Data-dependent power (all at the launch temperature, 81 °C as read and 80.96 °C by the thermal network; 1,024 minions, 600 MHz, 9.18 TFLOPS)

Full table in [10-data-dependent-power.md](10-data-dependent-power.md); every value is
`DATA/horace3.json` → `patterns.<name>.p80`, with `p80_sd` beside it.

| Claim | Value | Kind | Source |
|---|---|---|---|
| Zeros | **38.29 W ± 0.03** (5 runs) | M | E9 |
| Ones | **46.73 W ± 0.07** (5 runs) | M | E9 |
| π everywhere | 46.96 W ± 0.02 | M | E9 |
| Random normal | **63.40 W ± 0.08** (5 runs, 5 different random matrices) | M | E9 |
| Random uniform [0,1) | 61.29 W ± 0.04 (5 runs) | M | E9 |
| Spread, zeros to random normal | **25.1 W at identical FLOPs** | M | E9 |
| Heating per 10¹² FLOPs: zeros / ones / random | **< 8 / 26.8 / 75.9 m°C**; zeros is a bound, not a measurement: its rise stays below the whole-degree sensor's resolution (about 0.5 °C), and the thermal network driven by the measured power puts it at about 5 m°C (the fitted 1.3 is not used) | M (ones, random); bound (zeros) | E9 (`mC_per_tflop_fit`) |
| Board energy per FLOP, run average (`p_mean`): zeros / ones / random | 4.17 / 5.21 / 7.27 pJ | M | E9 (`pj_per_flop`) |
| Same, over the idle card, run average | **0.22 / 1.26 / 3.31 pJ** | M | E9 (`pj_per_flop_over_idle`) |
| Random normal, at the launch temperature (`p80`) | 6.9 pJ board, 2.95 over idle | M | E9 |
| −0.0 is not gated: costs like ones | 46.71 W against 38.23 W for +0.0 | M | E15 | 
| Rails: random − zeros, late in the run | 21.5 W of 29.6 W on the minion rail, 1.0 W on SRAM + mesh, ~7 W on no rail: ~4.4 W of it regulator delivery loss by the E30 fit (4.2 W on the minion rail), ~2.6 W unattributed | M | E9 (`rails_late`), E30 |

## Switching activity from the RTL (per `TensorFMA32` op, per minion)

`DATA/toggles.json` and `DATA/structured_toggles.json`; fields `mean.ff_clocked`, `mean.nets`,
`mean.by_block`, `mean.bus`, `mean.lane_valid`.

| Claim | Value | Kind | Source |
|---|---|---|---|
| Multiply-adds not gated: zeros / ones / random | 0 / 4,096 / 4,096 of 4,096 | S | E11 |
| Register bits clocked: zeros / ones / random | 0.025 M / 2.47 M / 2.47 M | S | E11 |
| Net toggles: zeros / ones / random | ~0 / 0.031 M / **87.4 M** | S | E11 |
| Share of random data's toggles in the multiplier tree | **85%** | S | E11 |
| Every simulated multiply-add matches software | 8,192 of 8,192 | S | E11 | 

## The model (fitted; see [11-thermal-model.md](11-thermal-model.md))

All in `DATA/model.json`, printed in `DATA/model.txt`.

| Claim | Value | Kind | Source |
|---|---|---|---|
| Fixed power (not leakage, not switching) | 12.6 W | F | E17 |
| Leakage at 80 °C | **23.3 W**, as 23.257 · e^((T−80)/36) | F | E17 (`power.A_leak_at_80`, `power.T_L`) |
| Leakage slope at 80 °C | **0.65 W/°C** | F | E17 (`power.lambda_at_80`) |
| The idle law's fit error | **0.205 W rms per idle sample** (against the reading smoothed over 3 s; the samples lie at 64–67 and 81–88 °C). Not the same basis as the DVFS page's 0.02–0.06 W, which is the refit's error on the sample-weighted bin means (`DATA2/dvfs.json` `leak_split`, `rms_W`). Corrected 28 September: the Horace page had called the 0.20 W "over bins" | F | E17 (`power.rms_idle`, `tools/ettelem/flip_thermal_model.py`) |
| Slope of board power under load, E5 load step (20 Sep, 600 MHz) | about **0.8 W/°C** board at 75–87 °C on aifoundry2 (0.76 / 0.80 / 0.82 / 0.89 for fits starting 1 / 5 / 10 / 20 s after launch; 0.77 / 0.79 / 0.80 / 0.84 without the seconds that hold a launch gap), 0.40 minion rail; a least-squares line through the idle law over the 5 s fit's seconds gives 0.69 | M, F | E5 (`docs/reports/data/2026-09-20-power-aifoundry2/summary.json`, `thermal.series` and `thermal.gaps`, least squares; `tools/ettelem/summarize_power_session.py`) |
| Drift of busy power within the hot 7 s runs of the strict protocol | **0.807 W/°C** on aifoundry2 (14 runs at 82–86 °C, standard error 0.013); aifoundry3 0.547 W/°C (7 runs at 57–61 °C, standard error 0.145: not pinned down) | M, F | E9, E20 (`DATA/horace3.json` and `DATA3/horace3.json` → `leak_w_per_c`; `DATA/report.json` 0.807; recomputed run by run by `tools/ettelem/summarize_power_session.py` → `docs/reports/data/2026-09-20-power-aifoundry2/summary.json` `context.busy_drift_cards`) |
| Slope of board power under load, first uncontrolled Horace session (20 Sep, 22 run averages from 30 runs at 79–90 °C; superseded by the rows above) | 0.78 W/°C board, 0.38 minion rail | F | E7 |
| Tensor state machines, all 1,024 minions | 1.85 W | F | E17 |
| Energy per register bit clocked | **3.18 fJ** | F | E17 (`power.e_fJ.ffclk`) |
| Energy per net toggle in the multiplier tree | 0.025 fJ | F | E17 |
| Energy per other net toggle in the unit | **0.80 fJ** | F | E17 |
| Energy per operand-word bit outside the unit | 15.5 fJ | F | E17 |
| Thermal resistance, total | **1.47 °C/W** | F | E17 (`R_total`) |
| Thermal stages | 0.106 @1.5 s, 0.050 @4 s, 0.234 @60 s, 0.136 @150 s, 0.860 @400 s, 0.081 @2,500 s °C/W | F | E17 (`taus`, `R`) |
| Leakage loop gain at 80 °C | **0.95**; passes 1 at 82 °C | F | E17 (`loop_gain_at_80`) |
| Degrees per sustained watt, with leakage feedback | 0.25 @10 s, 0.62 @1 min, 3.12 @10 min | F | E17 (`step_closed`) |
| Power-model error, fitted to 14 patterns | 0.32 W rms | F | E9 (`power_model.models`) |
| Power-model error, leave-one-out | **0.50 W rms** | F | E9 (`loo_rms`) |
| Sustainable switching power before runaway | **about 3 W** at 82 °C, at the fitted 22.8 °C intercept of 21 September's session; less in a warmer room | F | E17, corroborated by E12 |

## Predictions made before measurement

| Claim | Value | Kind | Source |
|---|---|---|---|
| 14 structured matrices, board power predicted from their tiles | **0.92 W rms**, 10 of 14 within 0.6 W (11 within 0.75 W) | P→M | E14 → E15; `DATA/structured_predictions_before.json` (`made_at` 2026-09-21T13:08:33) vs `DATA/ablation.json` |
| Worst structured miss (DFT cos/sin pair) | predicted 47.0 W, measured 49.8 W | P→M | same |
| Six earlier patterns predicted from the 09-20 data | 1.3 W rms for the two model forms that split the toggle count; 2.7 and 4.2 W for the two that do not | P→M | `DATA/predictions_before.json` (06:50:12) vs E9 |

## Held-out validation of the temperature model

`DATA/validation_timesplit.json`, `DATA/validation_afternoon.json`; summaries in the matching `.txt`.

| Claim | Value | Kind | Source |
|---|---|---|---|
| Time to 90 °C, runs **not** in the fit | median error **9%**, worst 23%, 6 of 7 within 20% | P | E17 time split |
| Ten-minute runs, runs not in the fit | end temperature **3.8 °C rms**, biased hot; 2 of 5 wrongly predicted to reach 90 °C | P | E17 time split |
| A separate session that afternoon, published model, nothing fitted on it | median 2%, worst 68% (the DFT pair), 5-minute run off by 0.2 °C | P | E17 afternoon |
| Same session, first-half model | median 7%, worst 65% | P | E17 afternoon |
| Time to 90 °C, in-sample (the number first published, now labelled as a fit) | 12% median | F | E17 (`per_run_summary`) |

## Long runs: time from 80 °C to 90 °C

`DATA/long.json`, field `dur` with `reason: "cap"`. Full table in
[12-heat-management.md](12-heat-management.md).

| Claim | Value | Kind | Source |
|---|---|---|---|
| Random normal, 1,024 minions | **19, 20, 20, 26 s** (4 runs) | M | E12 |
| Ones, 1,024 minions | **107, 162, 167 s** (3 runs) | M | E12 |
| Zeros, 1,024 minions | never; die **cools** to 76–78 °C in 10 min (3 runs) | M | E12 |
| Random normal on 128 minions | never; holds 81–82 °C for 10 min | M | E12 |
| Fewer minions buy time far more than in proportion | random normal on 768 / 512 / 256 minions: **35, 84, 276 and 315 s** (one run each, two at 256), against 19–26 s on 1,024: removing three quarters of the flips buys more than ten times the time | M | E12 |
| Equal flip power, similar heating | ones on 1,024 minions and random normal on 384 switch 10.7 and 10.2 W by the flip counts (the model, not a measurement); 107–167 s (three runs) against 119 s (one run): consistent with equal heating, not a test of it | M (times), F (watts) | E12, E17 |

## Ablations (7 s, 80 °C start, `DATA/ablation.json`)

| Claim | Value | Kind | Source |
|---|---|---|---|
| Integer spin loop (four adds and a branch) on 1,024 minions | +1.46 W over idle, **1.4 mW per core**, 8.1 pJ per instruction (E27's faster `addi` loop, A15 §2: 2.1 mW on one hart, 3.4 mW on both) | M | E15 |
| Energy per multiply-add over idle: int8 / fp16 / fp32, random data | **0.32 / 2.70 / 6.02 pJ** | M | E15 |
| Power is linear in active cores | 25.6 mW per minion at 256 and 512 active, 26.2 at 768 and 27.0 at 1,024: linear to within 5%; a line through zero fits 26.5 mW | M | E15 |
| TensorLoad from L2 SRAM | +6.2 W at 2.4 TB/s → 0.3 pJ per bit | M | E15 |
| TensorLoad from LPDDR4x | +10.7 W at 75 GB/s → 142 pJ/B, **18 pJ per bit** end to end (ablation, buffer never written; the E29 level is 122 pJ/B, tensor loads on known data 91–129) | M | E15 |
| Effective switched capacitance per minion, random fp32 | 0.168 nF (Esperanto's design target was 0.04 nF) | F | E15 with R6 |

## The speed effect (cool die)

`DATA/cold1.json`, `cold2.json`.

| Claim | Value | Kind | Source |
|---|---|---|---|
| Zeros from a 62–63 °C die | **11.38 and 11.81 TFLOPS**, 5–6 s of the 7 s run at 800 MHz | M | E10 |
| Random normal from a 63–64 °C die | **9.29–9.33 TFLOPS**, under 0.3 s at 800 MHz | M | E10 |
| Ones | 9.66–9.73 TFLOPS | M | E10 |
| Peak board power at 800 MHz on random data | 87.8 W, for an instant before the governor stepped down (cold2, run 0) | M | E10 (`DATA/vf.json`, `randn800_peak`, from `tools/ettelem/build_vf.py`) |
| The resulting speed gap, zeros vs random | **about 25%** | M | E10 |

## The DVFS loop and leakage suppression

`DATA2` means `docs/reports/data/2026-09-22-dvfs-aifoundry2/`; `DATA2/dvfs.json` holds the computed tables.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Governor thresholds | 65 °C software, 65 W TDP, checked once per management pass, ~133 ms on aifoundry2 with nothing polling (135 ms on aifoundry1's card 1, 224 ms on aifoundry3: E41; the 10 ms is the sleep at the end of each pass) | X | R3 | `thermal_pwr_mgmt.h`, `mgmt_build_config.h` (`DM_TASK_DELAY_MS`) |
| The loop's power input is a **measurement**, not an activity estimate | `pmic_read_average_soc_power()` over I2C | X | R3 | `services/thermal_pwr_mgmt.c`, `update_module_soc_power()` |
| The loop has **no hysteresis** | in the `353f20e` source both guardband macros are defined and never used; the older governor the cards' logs point to does use the power guardband, and the thermal test has no dead band in either | X | R3 | `thermal_pwr_mgmt.c` lines 212–223; no other reference in the tree |
| Thermal branch has priority over the power branch | plain `if`, power branch unreachable above 65 °C | X | R3 | `check_power_throttle_conditions()` |
| Clock returns to the boot point when the master minion idles | — | X | R3 | `go_to_idle_state_and_update_pwr_status()` |
| Operating points | 600 MHz / 0.517 V, 700 / 0.568, 800 / 0.618 | M | E10 | `DATA/cold1/telemetry.jsonl.gz`, `mhz.minion` with `die_mv.minion` |
| Clock transitions observed | **36** (18 up, 18 down) in 7 cool-start runs | M | E10 | `DATA2/dvfs.json`, `transitions` |
| Down-steps by cause | 7 thermal-only, 4 thermal+power, 7 unattributed (reading ≤65 °C, 34–56 W), **0 power-only** | M | E10 | same, field `why` |
| Voltage moved with frequency in every transition | true | M | E10 | same, `mv0`/`mv1` |
| First clock change after a launch | 0.39–0.99 s | M | E10 | same, `transition_summary.first_change_s` |
| The governor over two days on aifoundry2 (E10's cool starts, 21 Sep, and E29's discarded cool passes, 23 Sep) | 275 clock changes, the voltage following in every one; the first change a median 0.73 s after a block starts (0.14–2.01 s over 31 starts); up-steps at die readings of 62–66 °C; where the clock was above 600 MHz at a block's end (15 of 31), it settled at 600 MHz a median 1.02 s later (0.54–1.39); the board meter lags an up-step by a median 0.3 s (0–0.5 s, 44 up-steps). Descriptive, one card | M | E10, E29 | `DATA2/dvfs.json`, `governor_days` (`changes`, `voltage_tracks_strictly`, `first_change_s`, `up_T`, `reset`, `meter_lag_s`), written by `tools/ettelem/analyze_dvfs.py` |
| Thermal hunting on ones from a 64 °C die | 7 clock changes in 2.4 s, 800 MHz peaks 1.6 s apart, then 600 MHz | M | E10 | `DATA2/dvfs.json`, `traces` |
| Per-minion sleep and isolation exist in the open (Erbium) RTL | `pwr_ctrl_min_nsleepin` / `nsleepout` / `isolate` | X | R2 | `rtl/shire/neigh/neigh_top.v`, `neigh_top_pwrstub.v` |
| …and are tied off in the open configuration | `nsleepin='1`, `isolate='0` | X | R2 | `rtl/cpu_subsystem/cpu_subsystem_top.v`, with the comment "this ifce is not used" |
| …and no firmware line drives them | none | X | R3 | whole-tree search; only `PWR_CTRL` hits are eMMC bus voltage |
| **No array wake-up latency** after up to 27 ms idle | L1 0, L2 −11 (a slow no-idle baseline, not the idle), L3 0, DRAM +10.5 cycles (row closure) | M | E18 | `DATA2/wakeup/`, and `DATA2/dvfs.json` → `wakeup` |
| Idle board power after about 20.6 h with no workload (E18's 4.9 s probe aside) | **31.79 ± 0.04 W at 73.0 °C** | M | E19 | `DATA2/idle_20h.jsonl.gz` |
| …predicted by the model fitted a day earlier | 31.78 W, error **+0.01 W** | P | E17 → E19 | `DATA2/dvfs.json` → `idle_check` |
| Idle rails | minion 11.05 W, SRAM 2.00 W, mesh 3.64 W, 15.10 W on no sensor | M | E19 | same |
| Leakage share of an idle card at 80 °C | **55–80%** (20–29 W of the idle law's 35.9 W; 65%, 23.3 W, in the best fit; a range since version 3, decision D3) | F | E17 | `DATA2/dvfs.json` → `leak_fraction.idle_80c_law` (`idle_80c` for the measured denominator) |
| Leakage share of a random-data matmul at 80 °C | **31–45%** (36% in the best fit) | F | E17 | same |
| Kanter's reference range for leakage | 5–30%, ~20% common | X | R9 | the private notes of the conversation (R9); not published |

## The three machines (E20, E21)

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Static TDP the **service processor** reports | **65 W on aifoundry2, 0 W on aifoundry3** | M | E21 | `DATAC/config.json`; reproduce with `ettelem config` |
| Static TDP the **driver** reports | 65 W on all three machines | M | E21 | `DATAC/driver_config.json`; reproduce with `tools/etcfg` |
| Consequence in the firmware | at a TDP of 0 the step-down test `avg > tdp` is always true and the step-up test `avg < tdp` never is | X | R3 | `ServiceProcessorBL2/services/thermal_pwr_mgmt.c`, `check_power_throttle_conditions()` |
| aifoundry3's governor log, one 8 KB window | **26 throttle-down events, 0 throttle-up**, each printing `tdp level: 0` | M | E21 | `DATAC/sptrace-aifoundry3.bin`, readable with `strings` |
| Power state the firmware reports | `max_power` on aifoundry3 at 23 W, `managed_power` on aifoundry2 | M | E21 | `DATAC/config.json`; `get_power_state()` returns `MAX_POWER` iff power > TDP |
| Minion clock ever seen above 600 MHz | aifoundry2 yes (700, 800); **aifoundry3 never seen** (10 Hz telemetry) | M | E10, E20, E21 | `DATA/cold1/telemetry.jsonl.gz`; `DATA3/telemetry.jsonl.gz`, `mhz.minion` constant at 600 |
| aifoundry1's kernel module `srcversion` | `1383B256EB24A0A53F04CC7` against `47D26A305A0428B29FB7FC4` (**not the cause**, corrected 25 Sep: the module's version string was empty; 14-card-behaviour.md) | M | E21 | `/sys/module/et_soc1/srcversion` on each machine |
| aifoundry1's cards | 2, both on the bus, **neither usable** until 25 Sep: `Error unable to evaluate compatibility!` (both work since the module rebuild of 25 Sep) | M | E21 | reproduce with `lspci` and any `libDM.so` client |
| aifoundry3 launch temperature, strict session | **55.77 ± 0.18 °C** | M | E20 | `DATA3/horace3.json`, `thermal.model_T_at_launch` |
| aifoundry3 idle board power under those runs | 25.1 W | M | E20 | `DATA3/horace3.json`, `patterns.*.p_before` |
| Switching power, zeros / random normal, aifoundry3 | **1.89 W / 24.86 W** over idle (aifoundry2: 1.96 / 27.11). Re-measured on three cards by E38 (26 Sep, 4 runs each, registered values): zeros / random normal 0.75 / 24.66 W on aifoundry3, 1.85 / 27.18 on aifoundry2, 1.15 / 27.82 on aifoundry1-c1; Sparse compute quotes those since 28 Sep (its row in "Version 3") | M | E20, E38 | `DATA3/cards.json`, `rows[*]`; three cards: `docs/reports/data/2026-09-25-claims-v3/results/abla.runs.json` (`switching` of the kept `fp32_zeros`, `fp32_randn` runs), as `DATAE/manual.json` `tensor.per_card_rows` |
| aifoundry2 model applied to aifoundry3 unchanged | 1.38 W rms, 2.32 W worst; it overestimates every pattern, by 3 to 10% (8% by least squares) | P | E17 → E20 | `DATA3/cards.json`, `model_error`; `DATA3/transfer.json`, `ratio_a3_to_model` |
| …after one scale factor | scale **0.924**, residual **0.20 W rms** over 1.9–25 W | F | E20 | `DATAC/cards-report.json`, `scale`, `rms_scaled` |
| …calibrating that factor on one operand pattern's runs, predicting the other seven patterns | 0.36 W rms median, 0.93 W rms worst (calibrated on zeros; largest single error 1.53 W); 0.27 W rms calibrated on random normal | P | E20 | `DATA3/transfer.json` (`median_rms`, `worst_rms`, `worst_single`, `loo_scale_rms`), written by `tools/ettelem/transfer_cards.py` |
| Die voltage, aifoundry3 vs aifoundry2 | 523 mV vs 518 mV at the same 600 MHz, so \(V^2f\) predicts 2% **more**, not 8% less | M | E20, E21 | `DATAC/config.json`, `DATA3/telemetry.jsonl.gz` |
| aifoundry2's idle law extrapolated onto aifoundry3, 7–14 °C below its 64–88 °C fitted range (over every idle session of 22–24 Sep: +0.61 W, sd 0.05, over 16 sessions on aifoundry3, against −0.18 W, sd 0.10, over 25 on aifoundry2, `DATA2/dvfs.json` `idle_sessions.summary`; E44 re-measured it on three cards, "Version 3" below) | **+0.73 W** out of 25 W, the mean of the four temperature bins over 50–57 °C (the 50 °C bin is 22 samples of pre-session idle; +0.68 W weighted by samples); **+0.69 W** over 55–57 °C with the model's own idle rule | P | E17 → E20 | `DATA3/leakage_crosscard.json` (`mean_offset_W`, `mean_offset_W_by_sample`, `model_rule`), written by `tools/ettelem/transfer_cards.py` |

## One contended global atomic (E22, E23)

`DATAH` means `docs/reports/data/2026-09-22-hotline-aifoundry2/`. These rows are the 22 September session's. Since
26 September `DATAH/hotline.json` holds the three cards' version-3 passes instead (04-artifacts.md, A13), so the
`hotline.json` fields named here are in the file as committed before then (`git show 299fac8:<path>`), or from E22's
command over `DATAH/sweep.jsonl`; the three-card values are in "Version 3: the three-card check" below (row "One hot
line, repeated").

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Host shire's share of a contended atomic | **1.004** of an even split; whole chip within 0.998–1.004 | M | E22 | `DATAH/hotline.json`, `fairness` |
| Same, line homed in shire 7, 15 or 31 | 1.001, 1.000, 1.000 | M | E22 | same |
| Cost of one contended atomic | **10.00 cycles**, about 60 M/s for the whole chip | M | E22 | `DATAH/hotline.json`, `placement` |
| Same work on 32 lines, one per shire | 0.31 cycles, 1,919 M/s — **32×** | M | E22 | same |
| Uncontended remote global-atomic round trip | 216 cycles (216.2 = 6,000,000 / 27,755) | M | E22 | `DATAH/sweep.jsonl`, the one-remote-minion row; `DATAH/hotline.json`, `context.remote_atomic_latency_cycles` |
| Host shire's own memory operations while hammered | **192–384 total**, 0.01–0.05% of its uncontended rate | M | E23 | `DATAH/hotline.json`, `local` |
| …and it does not grow with time | identical at 5, 10, 40 and 100 ms windows | M | E23 | `DATAH/context.json` → `hotline.json` `context.window_independence`; hand-kept: the 5, 40 and 100 ms runs are in no raw data file |
| Remote requesters needed to flip it | 21–24 in the first run (20 leave the host at 98.9%, 24 stop it; N × 10 < 216 puts the edge at 22); superseded by "One hot line, repeated" (E36) below: the edge is **exactly 22** on every card (21 leave the host at 95.6–95.7%, 22–24 at 0.02%); quote that | M | E23, E36 | `DATAH/hotline.json`, `requesters` |
| Pacing that restores the host | 10,000 cycles → host 54%, hammering shires 96% | M | E23 | `DATAH/hotline.json`, `pace` |
| Energy, contended vs spread | **23.6 vs 1.4 nJ per atomic**, 17× (first run; the E29 reruns give 19.8 [16.9–23.6] vs 1.16 [1.01–1.37] nJ, below: quote those) | M | E23 | `DATAH/power.json` |
| 1,024 minions stalled on a contended line | 1.41 W over idle (first run); about 1.2 W pooled over the reruns, 1.19 [1.01–1.41] W, n = 7 | M | E23, E29 | `DATAH/power.json`; `docs/reports/data/2026-09-23-energy-manual/reruns.json`, `hotline_over_idle_w.contended` |
| Chip-wide barrier | **4,995 cycles** with one minion per shire, **5,018** with all 1,024 (the earlier 4,997 was hand-entered and is in no raw file) | M | E34, R4 | `docs/reports/data/2026-09-18-nocbench-aifoundry2/barrier-chip1.jsonl` and `barrier-chip32.jsonl`, `cycles_per_iter_mean` |
| A global atomic through the scratchpad self ID `0x7F` | kernel bus error | M | E22 | reproduce with `--home scpself:0` |
| The arbitration rule and its erratum | `l3_yield_priority` does not fix the same-address case | X | R1 | ET-SoC Errata 4.1 `RTLMIN-6207`, 4.2 `RTLMIN-6214`, both Postponed |
| Ivan's 6% | **not reproduced**; his code was not run | X | R11 | [17-hot-line.md](17-hot-line.md) |

## On-chip relay: shire-to-shire against main memory (E24, E25)

`DATAO` means `docs/reports/data/2026-09-22-onchip-aifoundry2/`. These rows are the 22 September session's (E25). Since
26 September `DATAO/onchip.json` holds the three cards' version-3 pass means (04-artifacts.md, A14; its `power` block is
still this session's), so the `headline`, `size`, `bigsize`, `intensity` and `distance` fields named here are in the
file as committed before then (`git show 299fac8:<path>`), or from E25's command over `DATAO/sweep.jsonl`; the
three-card values are in "Version 3: the three-card check" below (row "On-chip relay, repeated (E25)").

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Multi-stage relay, intermediate in DRAM | **48.4 GB/s** | M | E25 | `DATAO/onchip.json`, `headline` |
| …in the next shire's scratchpad | **592.9 GB/s**, 12.3× | M | E25 | same |
| …in the shire's own scratchpad | **1,483.7 GB/s**, 30.7× | M | E25 | same |
| Same on aifoundry3 | 12.4× and 31.2× | M | E25 | `docs/reports/data/2026-09-22-onchip-aifoundry3/sweep.jsonl` |
| Energy per byte moved | **104.8 / 8.9 / 4.25 pJ** for DRAM / next shire / own (first run; the E29 bars, below: 105.7 [99.5–111.0] / 8.6 [7.8–9.2] / 3.99) | M | E25 | `DATAO/onchip.json`, `power` |
| Power over idle, all three media | 4.34 / 4.42 / 5.30 W — within a watt | M | E25 | same |
| DRAM floor past the L3 | 47.9 GB/s at 32 MB per buffer, 53.4 at 256 MB | M | E25 | `DATAO/onchip.json`, `bigsize` |
| The same relay below the L3 | DRAM 281–411 GB/s; hand-off buys 1.0–1.4× | M | E25 | `DATAO/onchip.json`, `size` |
| Where the advantage runs out | 1.5× at 256 adds per element: about 32 flops per byte moved (64 per byte read) | M | E25 | `DATAO/onchip.json`, `intensity` |
| Which shire receives the slab | moves the bandwidth by up to a quarter over the five ring offsets tried: 593 GB/s at the next shire by ID (3.5 mesh hops on average, longest hand-off 10) to 733 at 16 shire IDs (2.1, longest 6); it falls with the longest hand-off (r = −0.99 on both cards; −0.32 and −0.30 against the mean hop count), the stage time growing about 3,200–3,300 cycles per hop of it; a correlation over five offsets, not a controlled test. Energy per hop is in the E31/E32 rows | M | E25 | `DATAO/onchip.json`, `distance[].by_card`, `distance[].longest` |
| A shire reading what another wrote to its scratchpad | works by tensor store and by vector stores; 0 wrong words of 1,024 blocks | M | E24 | `DATAO/sweep.jsonl`, group `probe` |
| Offset 0 of a shire's scratchpad | **faults** | M | E24 | reproduce with `--stage-bytes` and `scp_a = 0` |
| A 2D systolic array of TensorSend cells | hangs a hart permanently; not attempted | X | R12, `docs/et-soc1-notes.md` | one ready flag per minion, not per partner |

## The energy catalogue (E26)

The instruction and byte rows here are the first edition, superseded by E27 below, which is what the published
energy manual prints; quote E27 (for example `fmadd.ps` on random data 55.9 [53.5–58.1] pJ; the vector lane
6.3–6.4 pJ with the instruction's issue taken out, against the tensor unit's 5.8; a leakage correction of 0.40 W median and 1.80 W max on
aifoundry2). They are kept as measured. The last two rows, the manual's compositions (A15 §7), are current.

`DATAE` means `docs/reports/data/2026-09-23-energy-manual/`. Every entry below has a `pj_per_op` or
`pj_per_byte` field in `DATAE/enercat.json` under `cards.aifoundry2` and `cards.aifoundry3`, with its raw
and leakage-corrected power, both bracketing idles and the die temperature.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| An awake minion, one hart, `addi` loop | 2.0 mW; both harts 3.2 mW (first edition; superseded by E27: **2.14 / 3.43 mW** on aifoundry2, 5.5 [5.3–5.8] and 7.2 [6.7–7.7] pJ per instruction pooled over both cards; quote those) | M | E26 | `DATAE/enercat.json`, pattern `spin` |
| Scalar `add`, zeros / constant / random | 6.6 / 6.9 / 9.6 pJ | M | E26 | pattern `iadd` |
| Scalar `fadd.s` | 23.2 / 23.5 / 26.1 pJ | M | E26 | pattern `fadd_s` |
| 8-lane `fmadd.ps` | 27.8 / 28.3 / **59.4** pJ | M | E26 | pattern `fmadd_ps` |
| 8-lane `fadd.pi` | 13.0 / 13.3 / 20.5 pJ | M | E26 | pattern `iadd_pi` |
| 8-lane `fexp.ps` | 105 / 104 / 167 pJ, at ¼ the issue rate | M | E26 | pattern `fexp_ps` |
| `fdiv.ps`, `fsqrt.ps` | trap | M | E26 | run `--pattern fdiv_ps` |
| A vector multiply-add lane vs a tensor multiply-add, random data | 6.5 pJ over the awake core vs 6.0 pJ (E26 / E15; the manual's E27 figures: 6.3–6.4 pJ with the instruction's issue taken out, vs 5.8 [5.2–6.0]) | M | E26, E15 | `pj_per_op_vs_spin` of `fmadd_ps`; `ablation.json` |
| L1 hit, `flw.ps` / `fsw.ps`, zeros / random | 0.36 / 0.54 and 0.47 / 0.78 pJ/B | M | E26 | patterns `ld_l1`, `st_l1` |
| Own scratchpad, tensor load / store | 2.0 / 4.2 and 4.4 / 8.0 pJ/B | M | E26 | patterns `tload`, `tstore` with `scp` |
| DRAM, tensor load / store | **94 / 134** and **87 / 140** pJ/B | M | E26 | patterns `tload`, `tstore` |
| DRAM through the L1 write-back path, `fsw.ps` | 247 / 345 pJ/B at 26.9 GB/s | M | E26 | pattern `st_stream` |
| Leakage correction applied to the bursts | median 0.7 W, max 1.8 W over E26's bursts (E27, which the manual uses: 0.40 / 1.80 W on aifoundry2, 0.16 / 0.78 W on aifoundry3) | F | E26, E17 | `leak_correction_w` per entry |
| aifoundry3 / aifoundry2 over 56 entries | median **0.949**, range 0.87–1.01 | M | E26 | both card blocks |
| Dense fp32 matmul at 80 °C, rebuilt from the tables | 63.1 W (fixed 12.6 + leakage 23.3 + the flip model's 27.2 W) against 63.9 measured (E15; E9's random normal is 63.4); 57% static | D (a decomposition: the flip model was fitted to E9 and E12 on the same card, so this is a consistency check, not a prediction) | A15 §7 | `docs/energy-manual/07-composition.md` |
| The relay, priced from the byte tables with the rows it uses | DRAM 90–133 vs 105.7 [99.5–111.0]; own scratchpad 4.3–7.1 vs 3.99, a little below; next shire at 3.5 hops 5.1–11.2 vs 8.59 [7.78–9.21] | P (out of sample, made after the measurement) | A15 §7, E25, E29 | `DATAK`: `tload/dram`, `tstore/dram`, `l1fill/stride32`, `tstore/scp`, `wire/hop3`, `wire/hop4` |

## The comprehensive catalogue and the fine grain (E27, E28)

`DATAK` means `docs/reports/data/2026-09-23-energy-manual/catalogue-23sep.json`, E27's catalogue (it was
`catalogue.json` until 26 September, when that name passed to E46's version-3 catalogue on three cards; the two
cards' values here are 23 September's, and E45 and E46 re-measured them: "Version 3" below); every configuration is a key of
`cards.<host>.summary` with mean, sd, se, min, max and n over passes, and every burst is in `bursts.<host>`.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Instructions that execute in U-mode | 161; 13 trap (divide, square root, sine, reciprocal square root, 64-bit float conversion, the cycle CSR) | M | E27 | `workloads/enercat/enercat_modes.json`; the trap list in `docs/energy-manual/03a-every-instruction.md` |
| Pass-to-pass standard error | median 1.9%, 90th percentile 6.1% (aifoundry2) | M | E27 | `DATAK`, `se` of every entry |
| Cross-card ratio over 386 configurations | median **0.950**, 10–90% 0.906–0.987 | M | E27 | `DATAK`, `cross_card` |
| Cheapest and dearest instruction | `fence` 4.6 pJ; `amoaddg.d` 1,486 pJ (aifoundry2; 4.5 and 1,393 pJ pooled over both cards). Superseded by E46 (three cards, 3 passes each, random data): cheapest `fence` and `auipc`, **4.5 [3.9–5.5] and 5.3 [5.0–5.9] pJ**; dearest the global atomics `amoaddg.w` and `.d`, **1,313 [1,240–1,431] and 1,450 [1,313–1,591] pJ** (about 1,380 for the two, the energy manual's figure); `fence` against `nop` is within noise (the Version 3 row) | M | E27, E46 | `DATAK`, `combined`; three cards: `docs/reports/data/2026-09-23-energy-manual/manual.json`, `catalogue.combined["fence/random/h2"]` (and `auipc`, `amoaddg.w`, `amoaddg.d`), `mean`, `lo`, `hi` |
| Energy of one mesh hop per byte (board) | **0.70 [0.64–0.75] pJ/B on zeros, 1.74 [1.67–1.81] on random data**, both cards, fitted over 1–8 hops (aifoundry2 alone 0.750 / 1.812; over 1–6 hops 0.89 / 2.29, in line with E31–E32). Since 26 Sep (E46, three cards): **0.67** [0.62–0.73] on zeros, **1.80** [1.72–1.91] on random data, the mean of the cards' fits over 1–8 hops (a2 0.660 / 1.779, a3 0.620 / 1.722, a1c1 0.727 / 1.910). Per 64-byte line 43 and 115 pJ, as Memory anatomy §1 and §6 give them. Quote these. | F (straight line through 7 measured points) | E27, E46 | `DATAK`, `cards.*.wire`; three cards: `DATAE/catalogue.json`, `cards.<card>.wire.<zeros\|random>.slope_pj_per_byte_per_hop` |
| Data-dependent energy of the mesh (random − zeros), per bit per hop | 131 [129–133] fJ over 1–8 hops (174 / 155 on the two cards over 1–6): flips between flits plus ones carried, split in the E31/E32 rows | F | E27 | difference of the two slopes |
| Mesh rail alone, per hop | 1.29 pJ/B, fitted over 1–8 hops like the board figure above (over 1–6 hops the same points give 1.51; Heat per millimetre gives 1.50 on a loaded mesh and 1.1 on free links; quote those) | F | E27 | `04a-fine-grain.md`, "the mesh rail alone" |
| Filling a 64 B line from scratchpad into the L1 | 101 pJ zeros, 205 pJ random pooled over both cards (aifoundry2 211, aifoundry3 199 on random data); 1.6 and 3.2 pJ/B, about three quarters of the tensor load's 2.0 and 4.2 pJ/B. Version 3 (E45): the ratio on random data is a2 0.77, a3 0.80, a1c1 0.83, so roughly 70–90% of a tensor load's cost, and not separable from equal on aifoundry2 (its interval includes 1; the Version 3 row) | M (difference of strides) | E27, E45 | `DATAK`, `combined`, `l1fill/stride32/*` against `l1fill/stride64/*` |
| DRAM row hit vs row miss | no difference within ±5 pJ/B (version 3: no pattern differs at 99% on any of the three cards; an activation of about 30 pJ/B on zeros, or 50 on random data, would have shown: energy manual §4a); these 32-hart loads cost 14–21% more per byte than the two cards' tensor loads at 76 GB/s (26–30% on zeros; 13–20% and 22–26% against aifoundry2's own) | M | E28 | `DATAK`, `dramrow2/*` |
| L3 read by tensor load through the mesh | 7.9 / 19.7 pJ/B zeros / random at 1072 GB/s. Since 26 Sep (E46): **8.06** [7.44–9.19] / **20.3** [18.7–22.9] pooled. Per card: a2 7.6 / 19.3, a3 7.5 / 18.8, a1c1 9.0 / 22.8. Random data 2.5× zeros on every card. Rails (random): SRAM 39 / 39 / 28%, mesh 39% on each card. Quote these. | M | E27 (mislabelled row experiment), E46 | `DATAK`, `dramrow/stride8K/*`; three cards: `DATAE/catalogue.json`, `combined["dramrow/stride8K/<d>"]`; `cards.<card>.summary[...]` `.pj_per_byte`, `.rails_over_w`, `.over_idle_w` |
| Rail split, scalar and vector arithmetic | 79–82% minion rail, ~18% unmetered | M | E27 | `DATAK`, `rails_over_w` |
| Rail split, scratchpad six hops away | 49% mesh, 25% SRAM, 8% minions. Since 26 Sep (E46), random data: mesh 50 / 50 / 52%, SRAM 26 / 26 / 20%, minions 8 / 7 / 8%, no metered rail 17 / 17 / 20% (a2 / a3 / a1c1). At 1 and 3 hops the mesh share is 27–28% and 39–40%. Quote these. | M | E27, E46 | same; three cards: `DATAE/catalogue.json`, `cards.<card>.summary["wire/hop<N>/random"]` |
| Rail split, own scratchpad tensor load, random data (E46, three cards) | SRAM 69 / 68 / 49%, cores 24 / 23 / 21%, no metered rail 7 / 9 / 29% (a2 / a3 / a1c1). On a1c1 the unmetered power rises 0.54 W per SRAM-rail watt, against 0.034 and 0.043 on the others. L1 hits (`flw.ps`): cores 80 / 82 / 87%. | M | E46 | `DATAE/catalogue.json`, `cards.<card>.summary["tload/scp/random"]`, `["flw.ps/random/h2"]`; `UNMET` `<card>.coef.sram` |
| Rail split, DRAM read | 70% on no metered rail (E28's row reads: 67–71% on random data, 73–75% on zeros); of a tensor load's 129 pJ/B from DRAM, the E30 fit puts 73 in the DDR PHY, the I/O rail and the chips. Since 26 Sep (E46), a DRAM tensor load on random data: no metered rail 69 / 70 / 68%, mesh 18 / 18 / 21%, SRAM 11 / 11 / 10%, cores 2 / 0 / 1% (a2 / a3 / a1c1). The fit's DRAM term is **72.7 / 72.7 / 81.6** pJ per DRAM byte. Quote these. | M | E27, E28, E30, E46 | same; `UNMET`; three cards: `DATAE/catalogue.json`, `cards.<card>.summary["tload/dram/random"]`; `UNMET` `<card>.coef.dram_pj_per_byte` |
| SRAM rail at idle | 1.60 W at 67 °C, 2.63 W at 82 °C (aifoundry2); 1.90 W at 51 °C (aifoundry3) | M | E27 | `DATAK`, `sram_leakage.curve` |
| The rails' response to a step | roughly first-order: 55–57% of a step after 1 s, 83–84% after 2 s (τ ≈ 1.15–1.22 s); min and max are since reset. The rail split divides by 0.94, kept as published | M | E27 | `DATAK`, `rail_filter` |
| The sampler slowed by DRAM reads (aifoundry2) | a median of 23–206 ms per six-command sample over a burst of tensor loads or row walks from DRAM (683 ms at most), against 21–22 ms for every other burst and on aifoundry3; 3 of 1,176 bursts over 60 ms, all kept: in them the NoC rail reads up to 0.5 W below the same configuration's other passes, and dropping them moves the E30 DRAM term from 72.9 to 71.8 pJ/B (under one standard error). Their board watts stand to aifoundry3's as the rest of the catalogue's do: aifoundry3 ÷ aifoundry2 0.94–0.99 for these configurations, 0.91–0.99 for the middle 80% of all | M | E27 | `DATAK`, `bursts.aifoundry2[*].sampler_median_ms`, `sampler_max_ms`, `cross_card`; the hub's `power.sampler`, written by `tools/ettelem/sync_hub_data.py` |
| Neighbourhoods reading the shire's scratchpad | 3.8–4.2 pJ/B | M | E27 | `DATAK`, `neigh/*` |

## Confidence bars, the reruns and the unmetered remainder (E29, E30)

`RERUNS` is `docs/reports/data/2026-09-23-energy-manual/reruns.json`; `UNMET` is `unmetered_fit.json` beside it. These
rows are 23 September's (two cards). Since 26 September both files are rebuilt from the version-3 check (the relay,
rings and levels from E43's passes; the fit over E46's catalogue on three cards), so the fields named here are in
them as committed before then (`git show 299fac8:<path>`); the three-card values are in "Version 3" below and in the
energy manual.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Catalogue bars, half the range over 3 passes × 2 cards | median ±5.6%, 90th percentile ±11.5% | M | E29 | `DATAK`, `combined` |
| Relay through DRAM / next shire / own scratchpad | 105.7 [99.5–111.0] / 8.6 [7.8–9.2] / 3.99 pJ/B, n = 8 | M | E29 | `RERUNS`, `relay_pj_per_byte` |
| Contended hot line | 19.8 nJ [16.9–23.6], n = 7; spread over 32 lines 1.16 [1.01–1.37] | M | E29 | `RERUNS`, `hotline_nj_per_op` |
| Levels at 600 MHz: L1 / L2 / L3 / DRAM | 0.77 / 2.51 / 10.5 / 122 pJ/B, both cards, n = 6 (23 September). Since 26 September (E43, three cards, 6 passes each): L1 **0.75** [0.62–0.88] (a2 0.77, a3 0.75, a1c1 0.72), L2 **3.11** [1.42–4.99] (2.64, 2.83, 3.86), L3 **14.7** [7.1–20.5] (12.3, 13.5, 18.4), DRAM **114.6** [89.0–141.3] (111.5, 105.6, 126.6) pJ/B; quote these | M | E29, E43 | `RERUNS`, `levels_pj_per_byte` (`git show 299fac8:` for the two-card values); three cards: `levels_pj_per_byte.<level>.mean`, `lo`, `hi`, `per_card` |
| Rings at 600 MHz: pair / shire / xshire1 | 0.67 / 2.08 / 14.9 pJ/B, n = 6 | M | E29 | `RERUNS`, `rings_pj_per_byte` |
| Cool-card reruns contaminated by the governor | 700–800 MHz in 5–25% of the samples of most bursts; the whole attempt was discarded | M | E29 | `docs/reports/data/2026-09-23-reruns-aifoundry2/`, `mhz.minion` |
| s ↔ s+16 rings starve the service processor (aifoundry2) | sample latency (six management commands) 22 → 76–146 ms, the median in each of three passes (22 ms on aifoundry3); the board value changes 1.4–2.4 times a second against 5–6 in the other rings, none held over 0.84 s; energy read 33–45% low over three passes (39% on their mean) against aifoundry3. Superseded in part by E43 (25–26 Sep): the ring starved the sampler on all three cards, aifoundry3 included (medians 63–141 ms), and was dropped | M | E29, E43 | `-aifoundry2-warm/rl-pass*/telemetry.jsonl.gz` (`took_ms`, `board_w`); `reruns.json` `dropped` |
| Unmetered W = delivery loss + DRAM term | 0.196·minion + 0.050·SRAM + 0.286·NoC W + 73 pJ/B; rms 0.35 W (a2; 1.1 W on its DRAM configurations, about a quarter of their unmetered power); 0.177, 0.064, 0.264, 68 (a3; 1.3 W on its DRAM configurations); the idle 15 W is not split. The DRAM residual has a pattern: stores through the L1 1.3–2.7 W above the fit (their line reads are not counted), random data above, zeros and constants below. The 18–20% delivery loss moves about 1.2 points per 1% of rail scale. Since 26 Sep (E46's catalogue, three cards): minion 0.188 / 0.181 / 0.102, SRAM 0.034 / 0.043 / 0.540, NoC 0.291 / 0.294 / 0.205, DRAM 72.7 / 72.7 / 81.6 pJ/B (a2 / a3 / a1c1). The regulators' delivery loss is 10–19% of the minion rail by card; Memory anatomy says so since 28 Sep (it had said 18–20%). | F (4 coefficients over 392 + 386 configuration means) | E30, E46 | `UNMET` (`<card>.per_config`, `rms_dram_w`), written by `python3 tools/ettelem/fit_unmetered.py`; three cards: `UNMET` `<card>.coef` |
| DDR rail droop per off-rail DRAM watt | **0.87 mV/W** (0.029 mV per watt of anything else) on aifoundry2, 0.835 (0.013) on aifoundry3's own telemetry; since 26 September, on E46's catalogue, 0.86, 0.87 and 1.01 mV/W (0.034, 0.024, 0.099) on aifoundry2, aifoundry3 and aifoundry1's card 1 (the hub's data, `power.checks.droop.<card>`); rms 0.37 mV over 386 configurations; idle 767 mV; 1 mV ≈ 1.2 W of DRAM; traffic with no DRAM access (mesh, scratchpad, L3 reads through the mesh) also droops it, by up to about 2 mV (2.2 mV for L3 reads), a phantom of up to about 2 W of DRAM | F | E30 | `UNMET`, `ddr_droop` (with `per_config`), regenerated by `tools/ettelem/fit_unmetered.py` on 2026-09-25; the inline fit first published said 0.84 mV/W and rms 0.36 mV |
| Minion rail IR drop per watt | 0.070 mV/W on aifoundry2 (0.137 on aifoundry3's own telemetry); since 26 September 0.053, 0.061 and 0.028 on aifoundry2, aifoundry3 and aifoundry1's card 1 | F | E30, E46 | `UNMET`, `ddr_droop.minion_ir_drop_mv_per_w` (the inline fit said 0.068) |
| The PMIC meters three regulators; seven rails have no telemetry | minion, NoC, SRAM (w_out forwarded; v/a/w in and a_out read and dropped) | R | R13 | `pmic_controller.c`, `bl2_pmic_controller.h` |
| Moortec PVT: 35 temperature sensors, 125 voltage points, 35 process detectors (of 40 slots) | host sees averages; per-shire voltage in the DEBUG trace; PDs disabled | R | R13 | `bl2_pvt_controller.h`, `pvt_controller.c` |

## Heat per millimetre (E31, E32)

`WIRE` is `docs/reports/data/2026-09-24-wire-energy/wire.json`; `WREP` is `report.json` beside it. Loaded-mesh
coefficients are the second run's model (`model.v2`) over 1–6 hops; free-link numbers are `disjoint_flows.*.wsep_d1_4`.
E42, the third run, re-measured the free-link cost, the link sharing, all ones against random and the four-hop step on
three cards (`wire3.json` beside `WIRE`): "Version 3" below.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| One mesh hop | **3.72 mm** (3.64–3.74); x 3.73, y 3.70 | A (estimate from the die plot) | R14 | `WREP`, `inputs.hop_mm`; `research/geometry/pitch.json` |
| A random bit per mm, free links, 0.485 V | **36.2 fJ** on the mesh rail (24.6 data + 11.7 fixed); 46.7 on board power (32.7 + 14.0). E42 (three cards): the board total is resolved on each card (46.7, 44.4, 51.1 fJ; the Version 3 row), its split into data and fixed parts is not resolved per card with the leakage correction | M, F (slopes) | E32, E42 | `WREP`, `headline["uncontended/noc_rail"]`, `["uncontended/board"]` |
| A random bit per mm, loaded mesh | **50.4 fJ** mesh rail (30.6 + 19.8); 72.9 board (46.1 + 26.8) | F (3-term model) | E32 | `WREP`, `headline["v2/noc_rail"]`, `["v2/board"]` |
| Per bit differing from the previous flit, per hop (*a*) | 98 [92–103] fJ mesh rail; 151 [139–162] board | F | E32 | `WIRE`, `model.v2.*.toggle_fj_per_bit_transition_hop` |
| Per one carried, per hop (*b*) | 129 [127–133] fJ mesh rail; 192 [180–205] board | F | E32 | `WIRE`, `model.v2.*.ones_fj_per_one_bit_hop` |
| The same from the first run's repeated image | *a* 95, *b* 131 fJ on the mesh rail | F | E31 | `WIRE`, `model.v1.noc_rail` |
| Ones from complements (¾ against ¼) | 132 [125–138] fJ per one per hop, mesh rail | M | E32 | `WIRE`, `complement_test.noc_pj_per_byte` |
| Contention over 1–4 hops, mesh rail | data 119 against 91 fJ per bit per hop; the rest 76 against 43 | M | E32 | `WIRE`, `disjoint_flows.noc_pj_per_byte.wu`, `.wsep_d1_4` |
| Link sharing in the all-pairs set | 0 / 22 / 32 / 55 / 72% of link-hops at 1 / 2 / 3 / 4 / 6 hops (XY routing) | M (from the recorded maps) | E32 | `WIRE`, `checks.link_sharing` |
| All ones against random, per hop | 7–9% more (both meters); 36–37% less in total at one hop | M | E32 | `WIRE`, `configs["wu/p1/hop*"]` against `["wu/p0.5/hop*"]` |
| 256 B blocks against 16–128 B | +0.41 pJ/B per hop (mesh rail), +0.76 (board), pooled: 54% and 69% of every bit flipping. Per card, as the page gives it: mesh rail 55% (aifoundry2) and 53% (aifoundry3) of a full flip; board 67% and 71%, not resolved from a full flip | M | E31 | `WIRE`, `checks.alt256`; per card `patterns["alt:<n>"].<meter>.slope.per_card` against `model.v1.<meter>.toggle_fj_per_bit_transition_hop.per_card` (`heat-per-mm.script.js`, `flip256`) |
| Board coefficients without the leakage correction | 4–9% higher; mesh rail unchanged | M | E31, E32 | `WIRE`, `sensitivity.no_leak_correction` |
| Mesh rail data cost scaled to 0.9 V | 85–105 fJ per random bit·mm (× 3.44, constant C, full swing) | F, A (the scaling) | E32 | `WREP`, `scaled["0.9"]` |
| y-only three-hop pairs starve the meter on aifoundry2 | telemetry reads 0.8–1.6 s instead of 22 ms; 6 bursts dropped | M | E31 | `WIRE`, `dropped.aifoundry2` |
| A killed sampler poisons the management queue | every later opener crashes with `std::bad_function_call` until one `dev_mngt_service` call drains it | M | E32 | [14-card-behaviour.md](14-card-behaviour.md), "Traps" |
| Dally's figure | "~100fJ/b-mm on-chip" (AHA 2023 slide 8; Hot Chips 2023, spoken); CACM 2020 "100fJ/bit-mm" twice, in a cost model whose arithmetic and memory are "in 14 nm" and which says "Communication energy remains roughly constant" across technology at a supply "held constant". No statement names a process, voltage or counting; the quoted one is most likely the 14 nm model's | X, A (the 14 nm reading is an inference) | R14 | `research/DALLY-NODES.md` §1–2 |
| Its ancestors | 313 at 0.13 µm, 1.2 V (2002–04); 110 fJ/bit-mm at 32 nm, 0.6 V (DARPA 2008: C V² with 300 fF/mm); ~100 on a slide labelled 28 nm (SC10 2010 to 2017; its 2009 version labels the buses 1 mm and 10 mm per 64-bit word, 391); 121 per random bit at 40 nm, 0.9 V (Keckler et al. 2011; ½CV² and ¼CV² of the 2008 study's 600 fF/mm repeated wire) | X, A | R14 | same |
| Dally on a 5 nm network-on-chip | "Energy ~50fJ/bit-mm" for upper-layer NoC wires; "going through the router is a fraction of this energy" (NOCS 2022 keynote, 14:10–15:48) | X | R14 | same |
| His group's scaling of a wire, 28 → 7 nm | ×0.46 (nominal 0.90 → 0.70 V: ×0.60 voltage, ×0.76 the rest) (Villa et al., SC14, Table II) | X | R14 | `WREP` `wire_scaling` |
| The rule at this mesh's 0.485 V | 22–29 fJ per bit·mm (100 at 28 or 14 nm, SC14 to 7 nm, V² to 0.485 V); 24 from the 5 nm figure if made at 0.70 V; measured 25–31 data, 37–53 in all | A | E32, E42, R14 | `research/lit/dally_gap.py` |
| Other measured meshes at 0.485 V | Piton (IBM 32 nm SOI, 1.0 V): 24–26 data + 11–12 fixed fJ per bit·mm; Raw (IBM 0.15 µm, 1.8 V): 24; 410–450 fF/mm switched against this mesh's 420–530 | X, A | R14 | `WREP` `literature` (mesh); dally_gap.py |
| The explanations' sizes | voltage ÷2.1–3.4; counting up to ÷4; a hop's routers, clock and headers ×1.5–1.7; contention +49–61%; meter ×1.3–1.5; ones 57% of a random bit's data cost; the node apart from voltage ×0.76–0.93 | A | E32, E42, R14 | page §7; dally_gap.py |
| Keckler et al. 2011, 40 nm, 0.9 V | 121 fJ per random bit·mm (310 pJ / 256 b / 10 mm) | X | R14 | same, §1e |
| A plain repeated 7 nm wire, 0.485 V | 12–24 fJ per random bit·mm (200–400 fF/mm) | A (first principles) | R14 | `research/lit/first-principles-estimate.md` |

## Memory hierarchy (E33, 18 Sep, aifoundry2)

`DATAMH` means `docs/reports/data/2026-09-18-memhier-aifoundry2/`; `MH` is the `memhier-data` JSON that
`workloads/memhier/analyze.py --embed` writes into `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`. E36 and
E43 repeated the chases and the levels on three cards: "Version 3" below.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Load-to-use latency, L1 / L2 read buffer / L2 and local scratchpad | 5.25 / 36 / 47 cycles | M | E33 | `DATAMH/chase-dram.jsonl`, `cycles_per_load` at 256 B / 1 KB / 64 KB; `MH`, `plateaus` |
| L3 | 159–169 cycles at 600 MHz (by requesting shire: 169.0, 160.7, 159.3, 168.9 from shires 0, 7, 24, 31) | M | E33 | `MH`, `plateaus.L3["600"]`, `l3_by_requester` |
| DRAM | 287–297 cycles (479–495 ns) at 600 MHz; 352–368 cycles in the chases the governor ran at 800 MHz | M | E33 | `MH`, `plateaus.DRAM` |
| Latency models | DRAM 86.3 cycles + 344.8 ns; L3 72.2 cycles + 61.4 ns + 20 ns per mesh hop; another shire's scratchpad 65.95 cycles + 56.48 ns + 20.00 ns per hop | F | E33 | `MH`, `fits`, `scp_model` |
| Bandwidth at 600 MHz, 1,024 minions | L1 6.2 TB/s, L2 2.45, own scratchpad 2.46, L3 0.98, another shire's scratchpad 0.96, DRAM 76 GB/s (the reruns: within 0.3%, both cards, 23 September; E43's passes on three cards, 26 September: every level within 0.41% in every pass, the largest L3 on aifoundry3; the memory-hierarchy page rounds both to 1%) | M | E33, E29, E43 | `DATAMH/energy*/runs.jsonl`, launches at 600 MHz; `scripts/ridge-points.py`, `memhier_levels()` (`gbps_600`), `rerun_levels()`; three cards: `docs/reports/data/2026-09-25-claims-v3/raw/<card>/rl/p<k>/B/runs.jsonl`, the median GB/s of each level's launches at 0.59–0.61 GHz per pass, against the same `gbps` |
| Energy per byte by level | The page quotes the energy manual's three-card levels (E43, 26 Sep): L1 0.75 [0.62–0.88], L2 3.11 [1.42–4.99], own scratchpad 2.25 / 4.40 (zeros / random), another shire's 5.10 / 11.8, L3 14.7 [7.1–20.5], DRAM 114.6 [89.0–141.3] pJ/B. First measured 18 Sep on aifoundry2, two runs, board power against a ~27.0 W median idle with the governor free: L1 1.8, L2 4.3, local scratchpad 2.8, remote 6.3, L3 10.8, DRAM 148 pJ/B. The page keeps this as one note; the values did not change on 28 Sep, only the wording. | M | E43 (E33) | `docs/reports/data/2026-09-23-energy-manual/reruns.json`, `levels_pj_per_byte`, `levels_by_contents_pj_per_byte` (`MH` `energy_levels`); first: `DATAMH/energy*/results.json` |

## On-chip communication (E34, 18 Sep, aifoundry2)

`DATANOC` means `docs/reports/data/2026-09-18-nocbench-aifoundry2/`; `NOC` is the `nocbench-data` JSON that
`workloads/nocbench/analyze.py --embed` writes into `docs/reports/2026-09-18-et-soc1-on-chip-communication.html`. E36
repeated the round trips, credits and barriers, and E43 the rings, on three cards: "Version 3" below.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| TensorSend round trip inside a shire, 32 B | 68 cycles on a fast-network pair, 114 elsewhere | M | E34 | `DATANOC/intra-pingpong{,-s24}.jsonl`; `NOC`, `primitives.tree_hop`, `other_hop` |
| Round trip between shires, 32 B | 150 + 12.02 cycles per mesh hop, worst residual 1.1 cycles, over all 496 pairs | M, F | E34 | `DATANOC/matrix-pingpong.jsonl`; `NOC`, `matrices["matrix-pingpong"]` (`a`, `b`, `worst`) |
| Same with 1 KB messages | 12.0 cycles per hop up to 5 hops, 36.0 beyond | M, F | E34 | `DATANOC/matrix-pingpong-c32.jsonl`; `NOC`, `matrices["matrix-pingpong-c32"].knee` |
| The shire map recovered from latency alone | marty1885's layout, in 12 of 12 restarts of the search | D | E34 | `NOC`, `matrices["matrix-pingpong"].search.restarts` |
| Shire barrier; 32-minion allreduce | 237 cycles; 432 cycles | M | E34 | `DATANOC/barrier-shire{1,32}.jsonl`, `allreduce-c1.jsonl`; `NOC`, `primitives` |
| Allreduce of 32 B over 1,024 minions | 1,368 cycles (2.28 µs) | M | E34 | `DATANOC/xallreduce-c1.jsonl`; `NOC`, `allreduce` |
| Chip barrier | 4,995 cycles with one minion per shire, 5,018 with all 1,024 | M | E34 | `DATANOC/barrier-chip{1,32}.jsonl`, `cycles_per_iter_mean` |
| Energy per byte of messaging, on three cards (26 Sep; On-chip communication's values since 28 Sep) | 0.69 pJ/B on pairs, 2.16 around a neighbourhood, 2.22 around a shire, 3.66 with 128 B messages; across the mesh 9.2 + 1.75 pJ/B per mean hop over the five 1 KB rings every card kept, the three cards together (9.1 + 1.78 on aifoundry2, 8.0 + 1.73 on aifoundry3, 10.4 + 1.74 on aifoundry1's card 1). Was 0.67 pJ/B on pairs, 2.1 in a neighbourhood or a shire ring, 9.3 + 1.7 pJ/B per mean hop across the mesh (E29, two cards, 23 Sep); the 18 September runs (aifoundry2, two runs, no leakage correction) gave 0.8–2.3 inside a shire and 13–20 across the mesh (10.0 + 1.9 per hop), 2–13% above these, and are superseded (the page keeps them as one note) | M, F | E43 (E29, E34's rings) | `docs/reports/data/2026-09-23-energy-manual/reruns.json`, `rings_pj_per_byte`; `NOC`, `reruns.rings`, `reruns.mesh_fit`, `reruns.mesh_fit_per_card`, `reruns.first_vs_rerun` |
| Watts over idle of the message rings, and of the same cores spinning (26 Sep; the page's chart and table since 28 Sep) | 1.37–2.47 W per ring, the mean of its passes on three cards (s ↔ s+16: aifoundry3's three passes of 23 Sep); spinning with no messages 2.45 W (2.50 on aifoundry2, 2.41 on aifoundry3, 2.42 on aifoundry1's card 1). Was 1.56–2.53 W per ring and 2.71 W spinning on 18 Sep (aifoundry2, two runs, against a local idle on a cooling card), superseded | M | E43 (E34) | `NOC`, `reruns.over_idle_w`, `reruns.spin_over_idle_w`: `workloads/nocbench/analyze.py` re-reduces the V3-RL passes `reruns.json` names (`docs/reports/data/2026-09-25-claims-v3/raw/<card>/rl/p<k>/A`, `tools/ettelem/analyze_reruns.py` `reduce_dir`, the same burst rule) |

## Version 3: the three-card check (E35–E47, 25–26 Sep; E48 after it)

`V3R` is `docs/reports/data/2026-09-25-claims-v3/results/`. Each row gives a value per card, aifoundry2 (a2),
aifoundry3 (a3) and aifoundry1's card 1 (a1c1), with its 99% t interval over independent passes (E38's intervals are
corrected for its 19 sub-tests, E40's are 99.75%), and the item's outcomes: **registered**, over a2 and a3 as PLAN3
pre-registered them, and **all cards**, over the three. A FAIL means the prediction failed and the page takes the
measured value, per card; REPORTED means shown, not tested, on that card. How the check ran, and what each item tests:
[03-experiments.md](03-experiments.md), "Version 3 of the claims check" and E35–E47. Where a row here re-measures an
older row's quantity, quote this one with its per-card values; the older sections that were re-measured point here
(the refresh, the idle law, the catalogue, the reruns and the fit, the hot line, the relay, heat per millimetre, the
memory hierarchy and on-chip communication). Every catalogue
entry per card, and pooled over the cards, is in `V3R/catfull.json`, `.configs["<configuration>"]` (E46).

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| L3 hit latency against mesh hops (from shire 0, re-referenced to the pass's L1 hit) | slope a2 11.99 [11.96–12.02], a3 11.99 [11.96–12.02], a1c1 11.99 [11.96–12.02] cycles per hop; intercept 110.5 [110.3–110.7], 110.5 [110.3–110.7], 110.6 [110.4–110.8] cycles; within ±4 cycles of 110 + 12·hops for 99.97%, 99.65%, 99.36% of lines (99%, 5 passes each); PASS on all three | M, F | E35 | `V3R/mem.json`, `[item=MEM-P1].per_card.<card>.tests.P1_l3_slope`, `.P1_l3_intercept`, `.P1_l3_within4_frac` (`mean`, `ci99`) |
| DRAM latency against the 19 September model (constant 91, memory-shire positions, not refitted) | within ±3 cycles for a2 97.0% [96.6–97.4], a3 92.9% [91.9–94.0], a1c1 94.4% [91.8–97.1] of lines; median residual 0.2, 0.8, 0.0 cycles; from requesters 7, 24, 31: L3 within ±4 for 99.5–99.9%, DRAM within ±3 for 90.7–95.8% (99%, 5 passes each); PASS on all three | M | E35 | `V3R/mem.json`, `[item=MEM-P2].per_card.<card>.tests.P2_dram_within3_frac`, `.P2_dram_median_resid`; `[item=MEM-X2].per_card.<card>.tests.X2_s{7,24,31}_{l3_within4,dram_within3}_frac` |
| Ladder medians, L2 / L3 / DRAM | L2 49 cycles on every card; L3 a2 170.8 [169.9–171.7], a3 170.6 [169.5–171.7], a1c1 171.2 [170.3–172.1]; DRAM 304.6 [294.9–314.3], 304.6 [294.0–315.2], 303.0 [292.6–313.4] cycles (99%, 5 passes each); MEM-P8 FAIL on all three (the DRAM intervals leave the 303–315 band; the row-open fraction and non-open excess reach below theirs) | M | E35 | `V3R/mem.json`, `[item=MEM-P8].per_card.<card>.tests.P8_ladder_L2`, `.P8_ladder_L3`, `.P8_ladder_MEM`, `.P8b_open_frac_diff`, `.P8c_nonopen_resid` |
| DRAM bank timing (bits) | back-to-back row conflict a2 +36.9 [35.4–38.4], a3 +37.4 [31.3–43.5], a1c1 +36.5 [35.2–37.8] cycles; sequential same row −11, other row issued after +10, other bank 0.1 / 0 / 0 (99%, 5 passes each); CARD-DIFFERENT (a3's conflict interval leaves the 32–48 band) | M | E35 | `V3R/mem.json`, `[item=MEM-P4].per_card.<card>.tests.P4_row_conflict_extra`, `.P4_seq_col`, `.P4_seq_row`, `.P4_seq_bank` |
| DRAM refresh and open rows | period 2,325.4 cycles and largest extra wait 208 cycles on every card (a3 208.4 [207.3–209.5]); closed − open cluster means a2 6.0 [4.4–7.6], a3 5.34 [5.23–5.46], a1c1 6.56 [6.15–6.97] cycles (10–13 predicted); locked-loop slowest load 317–320, 318–442, 320–321 cycles per pass (under 250 predicted); pairs with no refresh between that hit the open row 0.258 [0.206–0.311], 0.263 [0.234–0.291], 0.357 [0.337–0.378] (≥ 0.98 predicted), across a refresh 0.0003 or less; MEM-P5 and MEM-P6 FAIL on all three | M | E35 | `V3R/mem.json`, `[item=MEM-P5].per_card.<card>.tests.P5_refresh_period`, `.P5_max_extra`, `.P5b_closed_minus_open`, `.P5_locked_max.values`; `[item=MEM-P6].per_card.<card>.tests.P6r_hit_no_refresh`, `.P6r_hit_refresh` |
| The cycle counter's late carry (`hpmcounter3`) | a read is 128 short after each wrap of the 7-bit pre-counter until one adder, shared round-robin by twelve counters, folds the overflow in: a 12-cycle window in RTL simulation, 0–10 and 0–9 in two launches on aifoundry2 (19 Sep); in E35 the raw pair differences take only 10, 138 and −118 in every launch on every card, but the one-window rule has exceptions in 8, 15 and 13 of 15 launches (a2, a3, a1c1): MEM-R1 FAIL on all three. `fixcyc()` in `workloads/memprobe/kernel/memprobe.c` corrects it | S (RTL), M | E2, E1, E35 | `rtl-sim/pmu_carry/`; `V3R/mem.json`, `[item=MEM-R1].per_card.<card>` (`diffs`, `exceptions`) |
| No cache level wakes up after idle (the E18 probe) | no level shows a shift ≥ 5 cycles common to ≥ 18 of 20 lines after 16M idle cycles, in 3 of 3 probes on each of a2, a3, a1c1; L2 60–61 cycles with no idle, 49–50 after 16M cycles; MEM-W PASS on all three | M | E35 | `V3R/mem.json`, `[item=MEM-W].per_card.<card>.decision`, `.passes.p<k>.P5_lines_ge5`, `.passes.p<k>.P3_L2_noidle_idle16M` |
| Memory anatomy's energies (§1, §6, the DRAM tile; since 28 Sep) | the energy manual's L1 0.54 pJ/B (`flw.ps`, random; 0.39 on zeros), L2 3.11, L3 14.7, DRAM 114.6 pJ/B, i.e. 34 pJ per 64 bytes from the L1 and 199 pJ, 0.94 nJ and 7.3 nJ per 64-byte line from the L2, L3 and DRAM. DRAM tensor loads cost 94.6 on zeros and 132.6 on random data. The row walks cost 155.9 / 158.5 / 156.4 pJ/B (row hit / row miss / sequential, random), and no pattern differs at 99% on any card. Was E1's (19 Sep, aifoundry2, two 6 s runs per pattern, rail trace against the level before each run): 46 pJ per L1 load; 183 pJ per L2 hit, 112 of it SRAM; 541 pJ per local L3 hit on the trace (306 SRAM, 120 NoC; 643 on the host log); 59 pJ per line per mesh hop (0.9 pJ/B); 5.1 nJ per DRAM load (67% unmetered, 79 pJ/B; 5.9 nJ and 92 pJ/B on the host log). The host log read 14–25% above the trace in all 12 runs, and the page still says so. | M | E43, E45, E46 (E1) | `docs/reports/data/2026-09-23-energy-manual/reruns.json`, `levels_pj_per_byte`; `DATAE/catalogue.json`, `combined[...]`; `manual.json` `v3.catalogue.dram_rows.<card>.<d>.anova_p`; E1: `docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json` `power` |
| The memory-levels page's rail splits (since 28 Sep) | as Memory anatomy §6 splits them (E46): an L1 hit (`flw.ps`, random) 80 / 82 / 87% on the minion rail, 2% SRAM, 1% or less mesh, 17 / 15 / 9% on no metered rail; the same arrays as an L2 read, read as the own scratchpad (no L2 hit has a three-card split), 69 / 68 / 49% SRAM, 24 / 23 / 21% minion, 7 / 9 / 29% on no metered rail; an L3 read through the mesh (random) 1,233 / 1,203 / 1,461 pJ per 64 B line, 39 / 39 / 28% SRAM, 39% mesh, 7 / 6 / 7% minion, 14 / 16 / 27% on no metered rail (a2 / a3 / a1c1); a mesh hop 115 pJ per line on random data and 43 on zeros; the L2 path's SRAM share at full bandwidth 115–165 mW per shire. Were E1's (19 Sep, aifoundry2; facts `l1.e-19sep`, `l2.e.rails`, `l3.energy-per-load`, the last two citing `workloads/memprobe/report_template.html:1091-1096`, which no longer hold them): an L1 `ld` 56.5 pJ at the board (40.7 minion); an L2 hit 112 SRAM / 64 minion / 2 NoC of 183 pJ; a local L3 hit 643 pJ (306 SRAM, 120 mesh, 110 minion) and 59 pJ per line per hop (47 of it mesh); the L2's SRAM share 145 mW per shire (61%) | M, D | E46 (E1) | `docs/reports/data/2026-09-28-memory-levels/facts.json` `facts["l1:l1.e-rails"]` (was `l1.e-19sep`), `["l2:l2.e.rails"]`, `["l3:l3.energy-per-load"]`, `["l3:l3.wire-energy"]`, `["l2:l2.e.shire"]`, written by its `build_facts.py` from `DATAE/manual.json` `catalogue.cards.<card>.summary["flw.ps/random/h2" \| "tload/scp/random" \| "dramrow/stride8K/random"]` (`rails_over_w`, `over_idle_w`, `pj_per_byte`) and `.wire.<d>.slope_pj_per_byte_per_hop`; E1: `docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json` `power` |
| Load-to-use latency, L1 / read buffer / L2 and local scratchpad; hart 1 | 5.25 / 36.00 / 47.00 cycles (per-pass ranges 5.247–5.259, 35.998–36.006, 46.998–47.024); hart 1 39.0 and 50.0; in every pass of a2, a3 and a1c1 (3 passes each); registered PASS, all cards PASS | M | E36 | `V3R/lat.json`, `.items[item=LAT-M1].per_card.<card>.passes[]` (`L1`, `RB`, `L2`, `hart1`) |
| L3 and DRAM latency by requesting shire | L3 (4 MB) 168.8–168.9 / 160.6–160.7 / 159.1–159.2 / 168.8–168.9 cycles from shires 0 / 7 / 24 / 31; DRAM (256 MB) 296.6–297.1 from 0 and 31, 287.2–288.8 from 7 and 24; every pass on every card. Requester effect L3(0) − L3(24): a2 9.69 [9.67–9.72], a3 9.71 [9.69–9.72], a1c1 9.73 [9.70–9.76] cycles (99%, 3 passes each); PASS, all cards PASS | M | E36 | `V3R/lat.json`, `.items[item=LAT-M2].per_card.<card>.passes[]` (`L3`, `DRAM`), `.requester_effect_ci99` |
| Another shire's scratchpad | 99.84 + 12.00 cycles per mesh hop (MARTY map): all 124 points within 1 cycle in every pass; row-0 slope a2 11.9995–11.9999, a3 12.0016–12.0020, a1c1 11.9977–11.9982; a→b equals b→a within 0.032 cycles; PASS, all cards PASS | M, F | E36 | `V3R/lat.json`, `.items[item=LAT-M3].per_card.<card>.passes[]` (`frac_within_1`, `row0_slope`, `worst_resid`, `a_to_b_minus_b_to_a`) |
| TensorSend round trip between shires; credits | 32 B: 149.96–150.08 + 12.012–12.023 cycles per hop over 496 pairs, worst residual 1.07–1.45, MARTY's map in 12 of 12 search restarts in every pass; 1 KB: 11.99–12.01 per hop to 5 hops, 36.00–36.05 beyond; credits 140.19–140.29 + 14.42–14.44 per hop (predicted 148 ± 3 + 12.2 ± 0.2); blocking credit in a shire 119.5–119.9; every pass on every card; LAT-N2 FAIL on the credits, all cards FAIL | M, F | E36 | `V3R/lat.json`, `.items[item=LAT-N2].per_card.<card>.passes[]` (`pingpong_fit`, `search_same_as_marty`, `c32_slope_to5`, `c32_slope_beyond5`, `credit_fit`, `blocking_credit_in_shire`) |
| Barriers and allreduces | shire barrier a2 232.53–232.55, a3 232.56, a1c1 232.61–232.65 cycles (predicted 237 ± 1); 32-minion allreduce 444.06–444.31 on all three (432 ± 2); 1,024-minion allreduce a2 1,393.3–1,393.4, a3 1,392.9–1,393.2, a1c1 1,392.6–1,393.0 (1,368 ± 10); chip barrier, one minion per shire / all 1,024: a2 4,990.1–4,990.8 / 5,012.3–5,012.7, a3 4,987.8–4,988.1 / 5,010.0–5,010.3, a1c1 4,975.5–4,978.1 / 4,998.1–4,999.6 (inside 4,995 ± 25 / 5,018 ± 25); 3 passes each; LAT-N1 and N4 FAIL, all cards FAIL | M | E36 | `V3R/lat.json`, `.items[item=LAT-N1].per_card.<card>.passes[]` (`shire_barrier`, `allreduce32`); `.items[item=LAT-N4].per_card.<card>.passes[]` (`allreduce_1024`, `chip_barrier`) |
| Allreduce of 1 KB (32 registers), the same passes | 32 minions a2 1,354.05–1,354.12, a3 1,354.10–1,354.16, a1c1 1,354.13–1,354.16 cycles; 1,024 minions a2 3,231.30–3,240.16 (median 3,236.33), a3 3,234.44–3,249.95 (3,243.35), a1c1 3,232.97–3,244.70 (3,244.27); 3 passes each, reported (no registered prediction); the chip diagram's broadcast flow quotes 1,354 and 3,236–3,244 | M | E36 | `docs/reports/data/2026-09-25-claims-v3/raw/<card>/lat/p*/noc/allreduce-c32.jsonl`, `xallreduce-c32.jsonl` (`cycles_per_iter`, one-tree rows); On-chip communication's embedded `nocbench-data` `.v3.cards.<card>.allreduce["32"]` (the medians) |
| Tensor cycles per op in the sparsity kernels | fp32/fp16 546.02–546.05, int8 318.02–318.04, TenB 529.05–529.09, row mask 544.02–544.04, all 1,024 minions 546.06–546.13, at every sparsity and pattern; fp16 pair result "math" at 50% and 100%; every pass on every card; PASS, all cards PASS | M | E36 | `V3R/lat.json`, `.items[item=LAT-S1].per_card.<card>.passes[]` (`"546.0"`, `"318.0"`, `"529.1"`, `"544.0"`, `"546.1"`: each pass's lowest and highest; `fp16_pair_result`) |
| One hot line, repeated (E22–E23) | stopped host 384–392 atomics per window (295–296 at N = 24) on every card; host at 95.5–95.7% of its alone rate with 21 requesters, 0.02% with 22–24; paced at P = 10,000 the host keeps a2 54.5% [44.2–64.8], a3 56.8% [53.0–60.6], a1c1 56.8% [51.7–61.8] (99%, 3 passes); 31 requesters, one per shire, leave the host at 100% (predicted ≤ 1%); LAT-H FAIL, all cards FAIL | M | E36 | `V3R/lat.json`, `.items[item=LAT-H].per_card.<card>.sub` (`P1a_stopped_scp_counts`, `P2_edge`, `P3_pacing.magnitudes["10000"]`, `P5_pollers`) |
| On-chip relay, repeated (E25) | next shire over DRAM a2 12.42×, a3 12.25×, a1c1 12.42×; own scratchpad over DRAM 31.18 / 30.78 / 31.19× (pass means, 3 / 2 / 3 passes); bandwidth against the longest hand-off Spearman ρ −0.963, permutation p 0 in 100,000 shuffles (a2, a1c1); offsets d and 32 − d differ by up to 2.7% (a2) and 2.6% (a1c1), registered 2%; LAT-R INSUFFICIENT (a3 has 2 passes), all cards INSUFFICIENT | M | E36 | `V3R/lat.json`, `.items[item=LAT-R].per_card.<card>` (`v.headline_hop_over_dram`, `v.headline_own_over_dram`, `i`, `iv.worst_mirror_rel`) |
| mmbench cycles per op and rate, three cards | fp32 and fp16 529.001 cycles per op, int8 280.35–280.37, in every kept launch of 4 passes on a2, a3 and a1c1; pass values 9.5105–9.5119 TFLOPS fp32, 19.018–19.022 fp16, 71.766–71.775 TOPS int8; every launch exact (92, 96, 93 launches); registered PASS, all cards PASS | M | E37 | `V3R/mmb.json`, `.items[item=MMB-a].per_card.<card>.<workload>.cycles_per_op_mean_based`; `[item=MMB-b].per_card.<card>.<workload>.tflops_pass_values`, `.exactness` |
| mmbench board watts over idle, fp32 / fp16 / int8 from the L2 / fp32 from DRAM | a2 25.7 [24.2–27.2] / 26.7 [25.1–28.4] / 27.9 [26.6–29.3] / 8.8 [8.1–9.5] W (die 80 °C, idle 33.3 W); a3 24.4 [23.8–25.0] / 25.5 [24.8–26.2] / 26.3 [26.0–26.6] / 8.4 [8.2–8.5] (62 °C, 26.0 W); a1c1 27.2 [26.6–27.9] / 28.6 [28.3–28.9] / 33.1 [32.6–33.5] / 8.9 [8.5–9.3] (75–76 °C, 41.8 W); 99%, 4 passes each; a3/a2 0.94–0.95; registered PASS, a1c1 reported | M | E37 | `V3R/mmb.json`, `.items[item=MMB-c].per_card.<card>.<workload>` (`mean`, `ci99`, `die_c_mean`, `idle_before_w`), `.cross` |
| Board GFLOP/s per W, L2 matmul, fp32 / fp16 / int8 | a2 161 [148–174] / 316 [290–342] / 1,172 [1,110–1,235]; a3 189 [179–199] / 370 [346–395] / 1,377 [1,307–1,446]; a1c1 138 [136–139] / 270 [269–272] / 958 [949–966]; 99%, 4 passes; a3 1.17 × a2 in each mode (Welch p ≤ 1.2 × 10⁻⁴), the card at its operating temperature; the A100's int8 lead 1.33 / 1.13 / 1.63 | M (the lead D, against the A100's 1,560 GOP/s per W) | E37 | `V3R/mmb.json`, `.items[item=MMB-d].per_card.<card>.<workload>.ci99`, `.cross`; `[item=MMB-e].per_card.<card>.a100_lead` |
| The Matmul efficiency page's energies (since 28 Sep) | the rows above, per card: with tiles in L2 50.4–74.9 W of board power over idles of 25.9–41.9 W; 138–189 GFLOP/s per W fp32, 270–370 fp16, 958–1,377 GOP/s int8; ET ÷ A100 datasheet (SXM4, peak ÷ TDP) 2.82–3.87× fp32 (CUDA cores), 0.35–0.47× fp16, 0.61–0.88× int8. Was the first run's (R4: 18 Sep, aifoundry2, one session, 12 s per workload from a 71 °C die): 56.6–61.7 W over a 30.6 W idle, 168 / 321 / 1,162 per W, 3.45× the A100's fp32 figure; the page keeps it as one note | M, D (the ratios) | E37 (R4) | `V3R/mmb.json`, `[item=MMB-c]`, `[item=MMB-d]`; the page's `trace-data` `.v3` (`scripts/mmbench-report-data.py`, which prints the three-card summary the tables quote); the first run: `docs/reports/data/2026-09-18-aifoundry2/results.json` |
| Private int8 tiles against the shared pool | private 511.94 cycles per op (4.00 B per minion-cycle) against shared 280.47–280.48 (7.30 B), every kept launch, 4 passes on each of a2, a3, a1c1; private fp32 and fp16 529.003 (none above 560); registered and all cards PASS | M | E37 | `V3R/mmb.json`, `.items[item=MMB-X1/c].per_card.<card>["private-int8"]`, `[item=MMB-X1/a].per_card.<card>["shared-int8"]`, `[item=MMB-X1/b]` |
| Load step: busy slope and DRAM phase | busy board slope a2 1.02 [0.67–1.36] W/°C (predicted 0.7–0.9: FAIL), a3 0.61 [0.49–0.74] (0.3–0.6: FAIL), a1c1 1.13 [1.05–1.22] (reported); DRAM-phase remainder 6.2 [1.7–10.7] / 4.61 [4.52–4.70] / 6.7 [3.1–10.2] W (all cards PASS); 99%, 4 passes | M, F (slope) | E37 | `V3R/mmb.json`, `.items[item=MMB-T/P1].per_card.<card>` (`mean`, `ci99`), `[item=MMB-T/P4-remainder]` |
| Minion-rail droop per watt of minion-rail rise | a2 0.080 [0.019–0.142], a3 0.083 [0.022–0.144], a1c1 0.055 [0.054–0.056] mV/W; 99%, 4 passes; all cards PASS (interval excludes 0) | M, F | E37 | `V3R/mmb.json`, `.items[item=MMB-T/P6].per_card.<card>` |
| Energy per MAC over idle, random operands, int8 / fp16 | a2 0.313 [0.297–0.330] / 2.661 [2.635–2.686] pJ; a3 0.262 [0.238–0.287] / 2.410 [2.303–2.517]; a1c1 0.309 [0.261–0.357] / 2.70 [2.49–2.91] (4 runs each; intervals corrected for 19 sub-tests, alpha 0.01/19); fp32 over int8 18.9 [18.3–19.5], 20.5 [19.0–22.0], 19.6 [17.9–21.5]. Registered PASS, all cards PASS (a1c1: the ratio tested, the pJ reported) | M | E38 | `V3R/abla.json`, `[item=ABL-T5].per_card.<card>.subtests[0..2].ci`; a1c1's pJ at `.per_card.aifoundry1-c1.reported.vs_aifoundry2_values[0..1].ci` |
| Operand anchors, fp32 matmul over its all-zeros run | ones: a2 8.52 [7.70–9.34], a3 8.09 [7.33–8.86], a1c1 9.00 [7.33–10.66] W; random: 25.33 [24.49–26.17], 23.91 [23.51–24.30], 26.66 [24.85–28.48] W (corrected, 4 runs). Registered PASS; a1c1 reported | M | E38 | `V3R/abla.json`, `[item=ABL-T8].per_card.<card>.subtests[0..1].ci`; a1c1 `.vs_aifoundry2_values.subtests[0..1].ci` |
| Negative zero | −0.0 over +0.0: a2 +8.36 [7.21–9.52], a3 +8.05 [7.62–8.48], a1c1 +8.85 [7.93–9.77] W; −0.0 − ones: −0.15 [−0.80–0.50], −0.04 [−1.14–1.06], −0.14 [−1.44–1.15] W (corrected, 4 runs): "costs like ones" shown within ±1 W on a2 only. Registered CARD-DIFFERENT, all cards CARD-DIFFERENT | M | E38 | `V3R/abla.json`, `[item=ABL-T1].per_card.<card>.subtests[0..1].ci` |
| The integer loop (spin) over idle | a2 1.51 [0.58–2.44], a3 0.40 [−0.07–0.86], a1c1 0.73 [−0.68–2.14] W (corrected, 4 runs); predicted 1.46 / 1.35 W. Registered CARD-DIFFERENT (excludes 0 on a2 only); a1c1 reported. These carry each card's launch-temperature offset (C2, the row below): at the die temperature of each launch 0.8–1.6 / 1.3–1.9 / 0.0–0.8 W over C2's two readings | M | E38 | `V3R/abla.json`, `[item=ABL-T6].per_card.<card>.subtests[0].ci`; a1c1 `.vs_aifoundry2_values.subtests[0].ci`; at launch `docs/reports/data/2026-09-21-horace-aifoundry2/lowpower-report.json`, `.v3.cards.<card>.configs.spin` (`dyn_at_launch`, `dyn_at_launch_step`) |
| Switching per active minion, 1,024 against 256 minions | ratio a2 1.094 [0.753–1.590], a3 1.239 [1.104–1.390], a1c1 1.246 [1.013–1.532] against [0.98, 1.10]; line through 256/512/1,024 minions 0.027 / 0.026 / 0.029 W per minion, intercept −0.95 / −1.77 / −2.11 W (corrected, 4 runs per point). Registered CARD-DIFFERENT, all cards CARD-DIFFERENT | M, F | E38 | `V3R/abla.json`, `[item=ABL-T7].per_card.<card>.subtests[0].ci`, `.subtests[1].fit` |
| Flip model refitted per card, leave-one-out | rms a2 1.008, a3 0.906, a1c1 0.966 W over 14 fp32 patterns (registered threshold on a3 ≤ 0.6 W: FAIL); a3's four energies 3.02 fJ per register bit clocked, 0.032 per multiplier-tree net toggle, 0.557 per other net toggle in the unit, 27.8 per operand-word bit outside the unit (E17's terms: 3.18, 0.025, 0.80, 15.5 on aifoundry2) | F | E38 | `V3R/abla.json`, `[item=ABL-R].per_card.<card>.refit_switching` (`loo_rms`, `fJ_per_event`) |
| Launch-temperature offset of the registered ablation values (post-data note C2, revised 26 Sep) | The registered switching values of V3-ABL-A and V3-ABL-B use a fixed reference launch (80.9 °C on a2 and a1c1, 55.8 °C on a3), but the runs launched at whole-degree readings of 80–81, 57–58 and 80 °C. At the die temperature of each launch they move by: V3-ABL-A (E38) a2 0.62 W high to 0.15 W low, a3 0.91–1.43 W low, a1c1 0.73 W high to 0.05 W low; V3-ABL-B (E39) a2 0.49 high to 0.29 low, a3 0.81–1.34 low, a1c1 0.73 high to 0.05 low. The first figure reads the whole-degree reading as the die temperature; the second puts the die 0.96 °C above it (a launch on a downward step of the reading, as on 21 September); the reading cannot tell them apart. So most of a3's registered deficit is the reference offset, not the card: at the same die temperature a3 switches 0.958–0.969 of a2 over the Horace patterns (registered 0.895; the catalogue's independent 0.972), and a1c1 1.004 (registered 1.009). Flip-model scales: registered 0.986 / 0.882 / 0.995, at launch 0.956–0.994 / 0.926–0.952 / 0.959–0.997. The registered outcomes stand; a page quoting a registered ablation value gives its at-launch range | M | E38, E39 | `docs/reports/data/2026-09-25-claims-v3/AMENDMENTS.md`, C2 and "C2, revised the same day"; `V3R/abla.runs.json`, `V3R/ablb.runs.json` (`t_launch`, `params_by_card`); `docs/reports/data/2026-09-21-horace-aifoundry2/cards-v3.json`, `.ratio_to_ref`, `.at_launch.ratio_to_ref`, `.at_launch_step.ratio_to_ref`, `.fit.<card>.scale`, `.at_launch.fit.<card>.scale`, `.at_launch_step.fit.<card>.scale`; `lowpower-report.json`, `.v3.cards.<card>` (`at_launch_offset_w`, `at_launch_step_offset_w`) |
| Cycles per tensor op at 1,024 minions (sparsity kernel), B in the L1 / streamed through TenB | fp16 546.00 / 529.00; int8 318.00 / **270.00** (the TenB int8 rate had never been measured), in every timed launch (33 per configuration per card, 3 runs) on a2, a3 and a1c1; card means within 0.0002 cycle. Registered PASS, all cards PASS | M | E39 | `V3R/ablb.json`, `[item=ABLB-2a].per_card.<card>.configs.<cfg>` (`min`, `max`, `mean`), `.cross_card_abs_diff` |
| Streaming B through TenB instead of holding it in the L1, over-idle power | int8 random: a2 +6.55 [5.97–7.14], a3 +6.04 [3.65–8.43], a1c1 +7.53 [6.77–8.29] W; int8 ones: +2.72 [1.01–4.43], +2.40 [1.71–3.10], +2.67 [0.01–5.33] W (99%, within-block pairs, 3 blocks); fp16 random +2.27 / +2.20 / +2.66 W (reported). Registered PASS, all cards PASS. "The difference is the kernel" kept: E37's mmbench int8 over idle exceeds this kernel's int8 random with B in the L1 by +18.02 [16.98–19.06] W on a2 and +18.03 [17.39–18.67] W on a3 (Welch, one-sided α 0.01; the clause needs > 10 W on each card), from the second reduction with V3-MMB's pass values (AMENDMENTS.md, "Implementation note (26 Sep 2026, after the first reduction)") | M | E39 | `V3R/ablb.json`, `[item=ABLB-2b].per_card.<card>.int8_randn_tenb_minus_l1`, `.int8_ones_tenb_minus_l1`; `.kernel_clause.per_card.<card>.welch` (`point`, `lo`, `hi`), `.kernel_clause.status` |
| Sparse fma: dense against all-zero A, over idle | dense a2 17.51 [16.91–18.11], a3 15.53 [15.11–15.96], a1c1 17.30 [17.01–17.60] W; zeros 2.47 [1.23–3.71], 1.03 [0.42–1.64], 1.39 [1.22–1.56] W; saving 0.859 [0.786–0.932], 0.934 [0.895–0.972], 0.920 [0.910–0.930] (99%, 3 blocks; registered band 0.80–0.92 on each card). Registered FAIL, all cards FAIL: quote per card | M | E39 | `V3R/ablb.json`, `[item=ABLB-3ab].per_card.<card>` (`dense_W`, `zero_W`, `saving`) |
| Over-idle power per unit of useful-slot fraction (six fma points) | a2 14.97 [14.80–15.15], a3 14.50 [12.99–16.00], a1c1 15.78 [15.33–16.24] W (99%, per-block slopes, 3 blocks); rms of the line 0.28 / 0.18 / 0.32 W. Registered PASS; a1c1 reported | M, F | E39 | `V3R/ablb.json`, `[item=ABLB-3c].per_card.<card>.slope`, `.fit_on_block_means.rms`; a1c1 under `.vs_aifoundry2_values` |
| Energy per gemv layer over idle, skip-0 / skip-90 / skip-99 | a2 67.5 [65.9–69.1] / 18.6 [11.9–25.3] / 5.9 [0.9–10.8] µJ at 81.4 °C; a3 55.5 [31.5–79.5] / 11.9 [3.1–20.8] / 3.3 [1.4–5.2] µJ at 58.4 °C; a1c1 75.4 [59.6–91.2] / 16.2 [15.4–17.0] / 4.5 [−0.3–9.4] µJ at 80.3 °C (99%, 3 blocks); a3 predicted 70 / 19 / 7. Registered FAIL (stated per card, never CARD-DIFFERENT) | M | E39 | `V3R/ablb.json`, `[item=ABLB-3e].per_card.<card>.configs.<gemv-skip-N>.uJ_above_idle`, `.die_c_at_launch_window`; `.band_checks` |
| Zero-skipping gemv: the gating alone (gemv-dense-0 − gemv-dense-90, same kernel) | a2 +1.66 [0.65–2.68], a3 +1.59 [1.05–2.14], a1c1 +1.75 [0.72–2.78] W (99%, within-block pairs, 3 blocks); 16.9 / 19.0 / 15.9% of dense-0's over-idle power; predicted +0.3 to +1.5 W. Registered PASS, all cards PASS | M | E39 | `V3R/ablb.json`, `[item=ABLB-3f].per_card.<card>.dense0_minus_dense90`, `.gating_pct_of_dense0` |
| The Sparse compute page's power figures (since 28 Sep) | this page's loop (operands −3…3, V3-ABL-B): the rows above, per card, every run at 1.10–1.12 × 10⁹ ops/s with launch gaps (was 1.12–1.13, the first run's); the saving dense → all-zero A with busy and idle power at the same die temperature, over note C2's two readings, 86–90% on a2, 86–88% on a3 and **92–96%** on a1c1 (the page said 91–96% for a1c1, what the runs' dropout-rule metric `switching` gives; V3-ABL-B's registered metric is `dyn`). The same loop on other operands, A and B alike (V3-ABL-A, four 7 s runs per card, reduced as the energy manual's §3.2): all zeros +1.9 / +0.8 / +1.2 W, all ones +10.4 / +8.8 / +10.1 W, random normal +27.2 / +24.7 / +27.8 W over idle; 0.40 / 0.16 / 0.25, 2.26 / 1.93 / 2.21 and 5.92 / 5.37 / 6.06 pJ per multiply-add (a2 / a3 / a1c1); zero-skip saves **82–92%** of the loop's power above idle against all ones and **93–97%** against random normal data (78–95% and 92–98% at the same die temperature); these registered values read from 0.53 W high to 0.25 W low on a2, 0.94–1.46 W low on a3 and from 0.73 W high to 0.05 W low on a1c1 (C2). Were: the Horace experiment's session on aifoundry3 (22 Sep, E20) +1.9 / +9.7 / +24.9 W, 0.41 / 2.1 / 5.4 pJ per multiply-add, 81–92% saved; and the page's first run (18 Sep, aifoundry3, two 4 s runs against a 24.6–24.7 W idle, no temperature control) 17.3 → 2.4 W (86% saved), 3.8 pJ per multiply slot dense, the integer loop 1.7 W, 8 rows masked 9.2 W, 70 / 19 / 7.1 µJ per layer over idle at 0 / 90 / 99% zeros, and the gating alone 12% (9.4 → 8.3 W, the masked kernel at 0%); the page keeps the first run as one note | M, D (the savings) | E39, E38 (first run R4; later runs E20) | the page's `sparsity-data` `.v3.energy.<card>.configs.<cfg>` (`above_idle_w`, `pj_slot`, `per_s`, `at_die_w`) and `.v3.operands.<card>` (`patterns.<zeros\|ones\|randn>.above_idle_w`, `.pj_mac`, `.at_die_w`; `c2_reads_high_w`), written by `workloads/sparsity/analyze.py` from `V3R/ablb.runs.json` and `V3R/abla.runs.json`, which prints the values the text quotes; the first run: `.energy`, from `docs/reports/data/2026-09-18-sparsity-aifoundry3/energy-*/results.json` |
| Is aifoundry3's lower switching the card or its temperature? | not separated: the card hypothesis (hot − cool inside ±0.5 W for fp32 uniform and randn) fails on a2, a3 and a1c1; registered FAIL, all cards FAIL. Pages say "the card or its temperature" | M | E40 | `V3R/x5.json`, `[item=X5].verdict`, `.outcome`, `.all_cards.verdict` |
| Hot − cool switching, fp32 randn, 1,024 minions (launch a2 83.3 against 76.7 °C, a3 65.0 against 57.6, a1c1 83.0 against 76.0) | a2 +1.20 W [+0.26, +2.15], a3 +1.97 [+1.47, +2.46], a1c1 −6.36 [−49.36, +36.63] (Welch 99.75%, 3 against 3 runs); fp16 randn a2 +0.93 [−0.71, +2.58], a3 +0.67 [−19.61, +20.95] (reported) | M | E40 | `V3R/x5.json`, `[item=X5].per_card.<card>.tests.fp32_randn.ci_hot_minus_cool` (`point`, `lo`, `hi`), `.tests.fp16_randn.ci_hot_minus_cool`; launch temperatures `.launch_temperatures.<arm>.measured_launch_c.mean` |
| fp32 randn switching power over idle at each launch temperature | a2 hot 27.68 [26.98–28.38], cool 26.48 [26.23–26.73] W; a3 hot 26.72 [26.25–27.20], cool 24.75 [24.50–25.01] W (99%, 3 runs each); a1c1 hot 20.60 [−1.29–42.49], cool 26.97 [25.30–28.63] W | M | E40 | `V3R/x5.json`, `[item=X5].per_card.<card>.switching_by_arm.hi.fp32_randn` (and `.lo.fp32_randn`) |
| Service-processor pass, quiet (no poller) | a2 133.2 ms in every pass (every quiet segment 133.2–133.6); a1c1 134.8; a3 224.1–224.5 (predicted ≥ 230: FAIL); 3 passes each | M | E41 | `V3R/tel.json`, `.items[item=TEL-P1].per_card.<card>.passes[].Q_ms`, `.quiet_segment_medians`; `[item=TEL-P5].per_card.aifoundry3.passes[].Q_ms` |
| How much a poller lengthens the SP pass | a2: single-command poll +0.8 ms every pass; ettelem 10 Hz +26.6 ms (one-sided 99% lower bound 21.6); voltage loop +12.4 [8.4–16.4] ms; a1c1 +0.4, +27.6, +11.6 (reported); a3 under ettelem 10 Hz 265.9–266.5 ms against 224.1–224.5 quiet | M | E41 | `V3R/tel.json`, `.items[item=TEL-P2]`, `[item=TEL-P3].per_card.<card>` (`passes[].diff_ms`, `diff_one_sided_99_lower_ms`), `[item=TEL-P4].per_card.<card>.t99`, `[item=TEL-P5]` |
| Board-value refresh seen by each poller (0.1 s poll / ettelem 10 Hz / ettelem 20 Hz) | a2 126–134.5 / 155.5–157 / 186.5–187 ms; a3 223–224 / 262.5–264 / 319.5–322; a1c1 133.5–139 / 156.5–158.5 / 188–188.5 (3 passes each); P_H − P_L a3 39.8 [36.5–43.1] ms, a2 24.7 [−6.9–56.2], a1c1 20.7 [−1.0–42.4] (99%); registered and all cards CARD-DIFFERENT | M, F (refresh fits) | E41 | `V3R/tel.json`, `.items[item=TEL-S].per_card.<card>.passes[]` (`P_L`, `P_H`, `P_H2`), `.H_minus_L_t99` |
| `ettelem --reset-ms` and the rails' running average | 1 s reset windows cycle 0–1,000 ms and read flat (max − min 0.47–0.66 W) 8 s after a burst on every pass of a2 and a3 (registered PASS; a1c1 fails one pass, all cards CARD-DIFFERENT); the reset restarts the average: median f(1 s) 0.934 (a2, 9 bursts), 0.93 (a3, 7), 0.93 (a1c1, 8), against 0.45–0.68 predicted (FAIL on every card) | M | E41 | `V3R/tel.json`, `.items[item=TEL-P6].per_card.<card>.passes[]` (`late_windows_max_minus_min_w`, `since_reset`), `[item=TEL-P7].per_card.<card>.median_f1` |
| Peak-hold high against the SP's maximum of the mean | at the end of each load window 2 or 3 °C on every card, pass medians 2 or 3 (disagreeing: WITHIN-NOISE); rises 3–4 °C above the mean in 68% (a2), 61% (a3), 83% (a1c1) of rises (≥ 80% predicted); registered and all cards FAIL | M | E41 | `V3R/tel.json`, `.items[item=TEL-R].per_card.<card>` (`R2`, `R3_share_3_or_4`, `passes[].windows[].end_high_minus_spmax`) |
| Governor configuration and trace, per card | a3: TDP 0 W, 65 °C, `max_power` in 3 of 3 passes, no throttle-down or idle event in `sp1.bin` after five launches (≥ 5 predicted); a2: 65 W, 65 °C, `managed_power`, no governor line; a1c1: 65 W, 65 °C, `managed_power` (reported); firmware / PMIC 1.3.1 / 1.5.0 (a2, a3), 1.2.0 / 1.3.0 (a1c1); driver TDP 65 W, boot 600 MHz on all; registered CARD-DIFFERENT | M | E41 | `V3R/tel.json`, `.items[item=TEL-G].per_card.<card>.passes[]` (`config`, `down_lines`, `idle_lines_old_format`, `fw`, `driver`), `.all_cards.firmware` |
| A random bit per mm, free links (V3) | mesh rail a2 36.1 [35.2–37.0], a3 35.8 [35.1–36.5], a1c1 38.1 [26.3–49.9] fJ; board power 46.7 [40.3–53.1], 44.4 [41.9–46.9], 51.1 [47.8–54.5] fJ (99%, 6 passes each); registered PASS, all cards PASS | M, F (slopes) | E42 | `V3R/wire.json`, `.items[item=WIRE-P1-16/P11a]` and `[item=WIRE-P1-16/P11b]`, `.per_card.<card>.mean`, `.lo99`, `.hi99` |
| Sharing a link, mesh rail, per bit per hop over 1–4 hops | data part a2 31.7 [24.2–39.2], a3 35.1 [14.8–55.3], a1c1 44.9 [1.7–88.1] fJ; fixed part 33.8 [31.4–36.2], 33.0 [31.6–34.4], 42.3 [40.9–43.6] fJ (6 passes); registered PASS both; all cards CARD-DIFFERENT (data part: a1c1's mean outside 16–40) and PASS (fixed part) | M, F | E42 | `V3R/wire.json`, `.items[item=WIRE-P1-16/P1]`, `[item=WIRE-P1-16/P2]`, `.per_card.<card>` |
| Board power, free links, per bit per hop over 1–4 hops | data part a2 110 [80–139], a3 110 [90–130], a1c1 128 [110–147] fJ; fixed part 64 [38–90], 55 [43–68], 62 [43–81] fJ (6 passes); PASS on every card | M, F | E42 | `V3R/wire.json`, `.items[item=WIRE-P1-16/P3]`, `[item=WIRE-P1-16/P4]`, `.per_card.<card>` |
| All ones against random data | per hop, mesh rail, a2 +9.6 [8.1–11.0]%, a3 +8.1 [0.5–15.8]%, a1c1 +12.3 [0.2–24.4]% (PASS); board power +5.8 [−0.6–12.3]%, +5.2 [−6.1–16.4]%, +8.7 [−0.9–18.3]% (FAIL: not established); at one hop all ones cost 35.2 [34.1–36.4]%, 35.7 [33.7–37.8]%, 36.7 [35.6–37.8]% less than random on the mesh rail (PASS) | M | E42 | `V3R/wire.json`, `.items[item=WIRE-P1-16/P6a]`, `[…/P6b]`, `[…/P12]`, `.per_card.<card>.mean` (fractions) |
| The four-hop step, mesh rail | above the line through 1, 2, 3 and 6 hops: random a2 6.5 [5.0–7.9]%, a3 8.0 [2.7–13.4]%, a1c1 7.9 [2.3–13.5]%; all ones 14.5 [12.2–16.8]%, 15.2 [14.5–15.8]%, 15.4 [14.2–16.6]% (PASS on every card); link-disjoint flows at four hops 0.1, 0.6, 0.4% off their line (inside ±3%) | M | E42 | `V3R/wire.json`, `.items[item=WIRE-P1-16/P7a]`, `[…/P7c]`, `[…/P14a]`, `.per_card.<card>` (fractions) |
| Board power's free-link fixed part: at most how much could be per second (heat-75) | a2 84% [49–118], a3 93% [67–120], a1c1 104% [71–137] (99%, 6 passes; the first write-up's 98% pooled the two cards of 24 September, 97% and 115% card by card in PLAN3.md's heat-75 row); descriptive, and every upper bound is above 50%, so "cannot rule out that most of the board's fixed part is per second" stands; on the mesh rail the bound is 27% | D | E42 | `V3R/wire.json`, `.items[item=WIRE-P1-16/P13].per_card.<card>` (`mean`, `lo99`, `hi99`) |
| The fill, byte for byte | 12 of 12 dump launches (4 fills × 3) match their expected words on each card; the store kernel on a DRAM slice, not the scratchpad image | M | E42 | `V3R/wire.json`, `.items[item=WIRE-FILL].per_card.<card>.matched`, `.by_fill` |
| Ring energy per mesh hop, five 1 KB cross-shire rings (V3) | a2 1.78 [1.31–2.25], a3 1.73 [0.48–2.97], a1c1 1.74 [0.95–2.53] pJ/B per mean hop (99%, 6 passes each); no pair of cards differs; pooled 1.75 (the page gives ±50%); registered PASS (the predicted card difference failed), all cards PASS | M, F (slopes) | E43 | `V3R/rl.json`, `.items[item=RL-a].per_card.<card>.mean`, `.ci99`, `.pooled_mean`, `.all_cards.pooled` |
| The relay (V3): through DRAM / to the next shire / in the own scratchpad | a2 111.3 [104.8–117.9] / 8.61 [7.79–9.43] / 4.05 [3.74–4.37] pJ/B; a3 107.5 [103.4–111.6] / 8.27 [7.68–8.87] / 4.11 [3.81–4.42]; a1c1 129.9 [124.3–135.5] / 9.89 [9.47–10.31] / 4.86 [4.62–5.09] (99%, 6 passes); DRAM ÷ next shire 12.9, 13.0, 13.1×, no card differs (pooled 12.97); relay DRAM: a3 ÷ a2 0.966 (99% 0.912–1.023), a1c1 differs from both (all cards CARD-DIFFERENT). The own-scratchpad relay against its card's catalogue low edge (a2 4.37 and a3 4.30 pJ/B from the 23 September catalogue, a1c1 5.04 from its own, E46): at the low edge on every card, not below it at 99% (measured − edge a2 −0.32 [−0.79, +0.16], a3 −0.19 [−0.50, +0.13], a1c1 −0.18 [−0.41, +0.04]); RL-f registered FAIL, all cards FAIL (second reduction, with a1c1's low edge) | M | E43 | `V3R/rl.json`, `.items[item=RL-d, part=relay DRAM / next shire].per_card.<card>.relay_pj_per_byte.{dram,hop,scp}`, `.ratio_geo_mean`; `[item=RL-d, part=relay DRAM a3/a2].ratio_a3_over_a2`, `.all_cards`; `[item=RL-f].per_card.<card>` (`measured`, `low_edge_mean`, `welch_measured_minus_low`), `.all_cards` |
| L1 level at 600 MHz (V3) | a2 0.77 [0.61–0.92], a3 0.75 [0.58–0.92], a1c1 0.72 [0.62–0.82] pJ/B (6 passes); no pair differs, pooled 0.759; E29's a2 − a3 difference did not recur (registered PASS, prediction failed) | M | E43 | `V3R/rl.json`, `.items[item=RL-g, part=L1 level a2 - a3].per_card.<card>`, `.pooled_mean`, `.welch` |
| Own scratchpad level by its contents | after a zeros prefill a2 2.11 [1.81–2.41], a3 2.10 [1.84–2.36], a1c1 2.55 [2.22–2.87] pJ/B; after random 4.13 [4.08–4.17], 4.04 [3.54–4.54], 5.03 [4.78–5.28] (3 passes each); a3 − a2 at equal contents −0.012 [−0.199, +0.174] (zeros), −0.084 [−0.575, +0.407] (random): the card difference is the contents; a1c1 lies above both (all cards CARD-DIFFERENT) | M | E43 | `V3R/rl.json`, `.items[item=RL-h, part=scp-local level follows the prefill].per_card.<card>.{zeros,random}`; `[item=RL-h, part=a3 - a2 at equal contents].welch_a3_minus_a2` |
| Small messages (`--count 4` against 32) cost more | shire-c4 − shire a2 1.51 [0.66–2.37], a3 1.34 [0.71–1.98], a1c1 1.47 [1.13–1.82] pJ/B; xshire1-c4 − xshire1 6.08 [3.46–8.69], 4.88 [1.90–7.86], 6.40 [2.98–9.82] (6 passes); decided on a3, PASS; above 0 on every card | M | E43 | `V3R/rl.json`, `.items[item=RL-c, part=shire-c4 - shire]`, `[item=RL-c, part=xshire1-c4 - xshire1]`, `.per_card.<card>` |
| Rings against spinning; the s ↔ s+16 ring's starved sampler | nocbench spin − ring over idle: pair a2 0.45 [0.05–0.85], a3 0.32 [0.06–0.59], a1c1 0.42 [0.11–0.73] W; xshire1, 2, 4, 6, 8 between 0.38 and 1.18 W, above 0 on every card; neigh and shire include 0 on a2 and a3 (a1c1's shire ring −0.32 [−0.57, −0.07] W); xshire16 dropped in all 18 passes, sampler median 63–141 ms on the three cards | M | E43 | `V3R/rl.json`, `.items[item=RL-X3, part=(a) spin - <ring>].per_card.<card>.mean`, `.ci99`; `.dropped_bursts[*].sampler_median_ms` |
| Balance points against the ridge (FLOP per byte at which the byte and the FLOP cost the same) | L3, random, against the spec ridge 3.0: a2 3.97 [2.39–5.61], a3 4.63 [2.72–6.59], a1c1 6.08 [3.48–8.84]; another shire's scratchpad, random, against 3.0: 2.52 [1.38–3.69], 2.79 [1.63–3.97], 3.19 [0.79–5.74]; in-shire TensorSend ring, zeros, against the measured ridge 8.78: 10.43 [7.41–15.86], 25.45 [18.66–37.56], 19.66 [14.45–28.53] (byte side 99% t over 9 passes on a2 and a3, 3 of them 23 Sep, 6 on a1c1; FLOP side over E38's 4 blocks). A verdict needs both registered cards' intervals on one side of the ridge; a2's overlap it in all three, so "ranges overlap: no verdict"; RL-X4 registered FAIL, all cards FAIL (second reduction, with E38's FLOP side) | M | E43 | `V3R/rl.json`, `.items[item=RL-X4, part=<part>].per_card.<card>` (`balance_point`, `balance_ci`, `side`), `.all_cards.sides` |
| aifoundry3's idle against aifoundry2's idle law, 55–84 °C | +1.01 [0.95–1.07] W, residual slope 0.036 [0.031–0.041] W/°C (a3, 99%, 3 cycles); a1c1 +10.07 [9.73–10.40] W, slope 0.237 [0.228–0.246] (reported); registered FAIL (predicted +0.3 to +0.9 W) | M | E44 | `V3R/idle.json`, `.items[item=IDLE-a].per_card.<card>.offset_W`, `.resid_slope_W_per_C` |
| aifoundry2's idle against its own law | cycle mean +0.04 [−0.15–0.22] W (99%, 3 cycles, bins 67–83 °C); over 70–85 °C +0.01 [−0.12–0.15] W; registered FAIL (predicted −0.23 ± 0.3 W) | M | E44 | `V3R/idle.json`, `.items[item=IDLE-b].per_card.aifoundry2.info_cycle_offset_W`; `.items[item=IDLE-k].per_card.aifoundry2.law_resid_70_85_W` |
| Unsensed idle slope (board − three rails), 74–88 °C | a2 0.100 [0.056–0.145] W/°C; a1c1 0.162 [0.081–0.244] (reported); metered rails 75–80 °C a2 0.525 [0.498–0.551], a1c1 0.767 [0.758–0.776] (99%, 3 cycles); registered PASS | M, F (slopes) | E44 | `V3R/idle.json`, `.items[item=IDLE-c].per_card.<card>.unsensed_slope_W_per_C_74_88`, `.info_metered_rail_slope_W_per_C_75_80` |
| SRAM rail at idle | slope a3 0.066 [0.062–0.069] W/°C, a1c1 0.051 [0.046–0.057] (99%, 3 cycles); a3 at least 0.93 W above aifoundry2's SRAM law in every bin 55–84 °C; registered PASS | M, F (slopes) | E44 | `V3R/idle.json`, `.items[item=IDLE-e].per_card.<card>.sram_slope_W_per_C`, `.excess_over_a2_sram_law_by_bin` |
| Unsensed idle power at 70 °C | a3 13.69 [13.56–13.83] W, a1c1 17.46 [17.31–17.62] (99%, 3 cycles); a2 14.81 (one cycle with a 70 °C bin); registered PASS | M | E44 | `V3R/idle.json`, `.items[item=IDLE-f].per_card.<card>.unsensed_70C_W` |
| aifoundry3 under a back-to-back random-data heater | the die peaks at 90 °C in 3 of 3 cycles (after 126, 131 and 150 two-second bursts); registered FAIL (predicted a plateau of 60–66 °C) | M | E44 | `V3R/idle.json`, `.items[item=IDLE-0].per_card.aifoundry3.tmax_per_cycle`; `V3/raw/aifoundry3/idle/p*/marks.jsonl` (`heat_end`) |
| Busy leakage share at 80 °C (A80 / 63.9 W) | not identified on a2: best T_L 32, 32, 16 °C; shares within 0.005 W rms of the best span 0.17–0.80 over 3 cycles; Kanter's 30% not established; registered FAIL | M, F | E44 | `V3R/idle.json`, `.items[item=IDLE-k].per_card.aifoundry2.per_cycle[*].share_range`, `.decision_busy_leakage_above_Kanter_30pct` |
| The catalogue's temperature coefficient (30-configuration panel, hot against cool passes) | a2 +0.48 [0.07–0.90] %/°C over ΔT 14.4 °C (4 v 4 passes); a3 +0.30 [0.18–0.42] over 10.6 °C (3 v 3); a1c1 +0.35 [−0.11–0.81] over 6.2 °C (4 v 4, not established); registered FAIL: "temperature", not "the card", on a2 and a3 | M, F | E45 | `V3R/cat.json`, `.items[item=CAT-a].per_card.<card>.beta_pct_per_c`, `.dT_c` |
| Cool aifoundry3 / warm aifoundry2 over the panel | 0.985 [0.977–0.993] (a3 at 58.8–60.4 °C, a2 at 76.2–76.6 °C busy; 3 v 4 passes); a1c1 warm / a2 warm 0.999 [0.984–1.014] (reported); registered FAIL (predicted 0.951 ± 0.015; 23 Sep 0.953 [0.943–0.964]) | M | E45 | `V3R/cat.json`, `.items[item=CAT-b].per_card.ratio`, `.per_card.aifoundry1-c1.ratio_vs_aifoundry2_W`, `.committed_23sep.ratio` |
| DRAM row walks (seq, rowhit, rowmiss) over a DRAM tensor load | zeros: a2 +21.7 [11.6–31.8], a3 +27.1 [22.9–31.4], a1c1 +24.9 [9.9–40.0] pJ/B; random: a2 +21.4 [−26.2–69.0], a3 +24.7 [13.8–35.5], a1c1 +22.1 [14.9–29.3] pJ/B (99%; 3, 6 and 3 passes); the three patterns indistinguishable (ANOVA p 0.056–0.95); registered CARD-DIFFERENT | M | E45 | `V3R/cat.json`, `.items[item=CAT-c].per_card.<card>.<zeros\|random>.rows_minus_tload`, `.anova` |
| A tensor store to DRAM against a tensor load, random | a2 +8.35 [−47.35–64.05], a3 +7.32 [−1.94–16.58], a1c1 +14.51 [−2.75–31.77] pJ/B (99%; 3, 6, 3 passes): not distinguished from 0 on any card; registered FAIL (predicted +3.2 ± 3 on a3) | M | E45 | `V3R/cat.json`, `.items[item=CAT-e].per_card.<card>.tstore_minus_tload` |
| L1 fill per byte / tensor load from the scratchpad per byte, random | a2 0.77 [≈0.43–1.11], a3 0.80 [≈0.66–0.94], a1c1 0.83 [≈0.69–0.97] (approximate 99%; 3, 6, 3 passes); registered CARD-DIFFERENT | M | E45 | `V3R/cat.json`, `.items[item=CAT-f].per_card.<card>.ratio`, `.ratio_ci99_approx` |
| fence − nop, per instruction | zeros: a2 −0.82 [−1.39 to −0.25], a3 −0.87 [−1.24 to −0.50], a1c1 −1.00 [−1.46 to −0.54] pJ/op; random: a2 −1.31 [−3.29 to 0.66], a3 −0.87 [−1.28 to −0.46], a1c1 −1.25 [−1.90 to −0.60] (99%); registered as "expected within noise", reported | M | E45 | `V3R/cat.json`, `.items[item=CAT-f].per_card.<card>.fence_vs_nop_expected_within_noise` |
| The catalogue, aifoundry3 against aifoundry2 (pass-level median over 392 configurations) | a3 / a2 0.976 [0.961–0.990] (99%, 3 v 3 passes), registered PASS (23 Sep: 0.950); a1c1 / a2 0.967 [0.950–0.985] (reported) | M | E46 | `V3R/catfull.json`, `.items[item=CF-GAP].per_card.<card>.vs_aifoundry2` |
| Each configuration's ratio to aifoundry2, median and 10–90% | a3 0.972 (0.916–1.004), a1c1 0.962 (0.902–1.141), n = 392 each | M | E46 | `V3R/catfull.json`, `.ratios.per_card` |
| Pass-to-pass standard error, median / 90th percentile over configurations | a2 2.1% / 5.7%, a3 1.4% / 3.6%, a1c1 1.5% / 4.1% (3 passes each; 23 Sep a2 1.9% / 6.1%, a3 1.2% / 3.6%) | M | E46 | `V3R/catfull.json`, `.items[item=CF-REP].per_card.<card>.median_pct`, `.p90_pct` |
| The catalogue re-run against 23 Sep, per configuration | new ÷ committed: a2 median 0.999 (10–90% 0.932–1.095, n = 392), a3 1.023 (0.967–1.091, n = 386) | M | E46 | `V3R/catfull.json`, `.vs_committed_23sep` |
| Coverage | all 392 configurations kept in 3 of 3 passes on each card: 1,176 bursts, 0 dropped, 0 missing launches, every sample at 600 MHz; CF-COVER PASS on all cards | M | E46 | `V3R/catfull.json`, `.items[item=CF-COVER].per_card.<card>`, `.idle_clock.<card>` |

### Gathers, scatters and packed atomics (E48, 26 Sep, three cards)

`GS` is `docs/reports/data/2026-09-25-claims-v3/results/gs.json`; `GSF` is `gs-full.json` beside it. Values are pooled
over the three cards' pass values (`[min–max]` over the nine), at 1,024 minions and 600 MHz; "random" is one random
word on each line of a 4 KB tile, the tiles in a scrambled order (03-experiments.md, E48). Energies are over each
card's own idle. E48 ran after the campaign's blocks on the same three cards under its own rules
(`tools/claims-v3/gs/README.md`, fixed before data), so its tested items carry one all-cards outcome, decided per card.
Since 27 September the energy manual (§3.1, 4.3, 4.4, 6), the memory hierarchy ("Irregular access"), the influence
page (S3, K3, K6) and the hub's chart of events carry these, from `manual.json` `gs` (the same pooling); §3.1's bold
figures pool a2 and a3 only (`GSF.combined_catalogue`, the README's rule for rows beside the catalogue), with a1c1 beside.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Word gather (`fgw.ps`), random, by where the table lives | L1 (512 B per hart) 452 G elements/s, 12.8 [11.9–14.6] pJ each; L2 (4 KB) 27.4 G/s, 354 [330–392] pJ; own scratchpad (16 KB) 27.4 G/s, 368 [344–400] pJ; a scratchpad 2 hops away 10.2 G/s, 903 [843–1010] pJ; DRAM (256 KB) 1.19 G/s, 9.8 [9.2–10.3] nJ | M | E48 | `GS`, `.items[item=GS-RATE].pooled["gs/E/fgw.ps/<table>/rand/random/h2/mff/n1024"]` (`elements_per_s`, `pj_per_element`); per card in `.per_card` |
| Word scatter (`fscw.ps`), random | L1 452 G/s, 14.7 [13.9–15.5] pJ; L2 23.5 G/s, 732 [677–814] pJ; DRAM 0.42 G/s, 23.8 [22.2–25.3] nJ | M | E48 | same, `gs/E/fscw.ps/...` |
| The model's tests | L1 gather 10.89 cycles per instruction per minion on every card (7–12 registered: PASS); L2 and scratchpad 1.15× the two-miss-handler bound of 23.9 G/s, a second hart adding 0.05% or less (PASS); DRAM 76.4 GB/s of lines on every card (57–95: PASS); `fgwl.ps` with both harts of a minion 1.03× one hart (1.6–2.4 predicted: FAIL on every card) | M, P→M | E48 | `GS`, `.items[item=GS-L1]`, `[item=GS-MH]`, `[item=GS-DRAM]`, `[item=GS-UC]` (`per_card.<card>`) |
| Exactness | 159 of 159 verify launches per card passed; 2,937 timed launches per card ended with `gsc_progress` 0 on every hart; lane 7 wins when every lane scatters to one word (1,152 of 1,152) | M | E48 | `GS`, `.items[item=GS-CHECK]`, `[item=GS-CONFLICT]` |
| Updates per second and energy per update | gather + `fadd.ps` + scatter: L1 139 G/s at 0.036 nJ, L2 or scratchpad 18.2 G/s at 0.80–0.85 nJ, DRAM 0.42 G/s at 22 nJ; `famoaddl.pi` on a shire table 12.7 G/s at 0.39 nJ; `famoaddg.pi` on a chip table 2.8 G/s at 1.7 nJ; scalar `amoaddl.w` 12.8 G/s at 0.27 nJ, `amoaddg.w` 2.8 G/s at 1.1 nJ | M | E48 | `GS`, `.items[item=GS-ADD].rows[]` |
| The cards against aifoundry2 | rates 1.000 (10–90%: 0.9998–1.0001, 157 configurations); energy per element aifoundry3 0.965 (0.937–0.994), aifoundry1's card 1 1.085 (0.933–1.148), 100 configurations | M | E48 | `GS`, `.items[item=GS-CARD].ratios` |
| Validation across machines | every tested item decided per card, on three cards in three machines (aifoundry2, aifoundry3, aifoundry1's card 1), three passes each: GS-L1, GS-MH, GS-DRAM, GS-CHECK PASS on each; GS-UC FAIL on each | M | E48 | `GS`, `.items[item=<GS-…>].outcomes` |
| Scalar loads and stores on the same 64 offsets (`flw`, `fsw`) | `flw`: L1 403 G/s, 14.0 [13.4–14.5] pJ; L2 27.5 G/s, 336 [315–369] pJ; own scratchpad 27.5 G/s, 351 pJ; DRAM 1.19 G/s, 9.2 [8.6–9.9] nJ. `fsw`: L1 402 G/s, 25.5 pJ; L2 23.6 G/s, 774 pJ | M | E48 | `GS`, `.items[item=GS-RATE].pooled["gs/E/flw/<table>/rand/random/h2/mff/n1024"]`, `…/fsw/…` |
| The 32 B-block forms (`fg32w.ps`, `fsc32w.ps`; one access per instruction, lanes permuted in the block) | `fg32w.ps` from the L1 1,786 G elements/s at 3.8 pJ (3.9× the rate and 0.30× the energy of `fgw.ps`), L2 424 G/s at 22.6 pJ, DRAM 19.1 G/s at 540 pJ; `fsc32w.ps` L1 1,809 G/s at 4.8 pJ | M | E48 | same, `gs/E/fg32w.ps/…`, `gs/E/fsc32w.ps/…` |
| The L1-bypassing forms | `fgwl.ps` from the L2 19.6 G/s at 350 [327–381] pJ (0.72× `fgw.ps`); `fgwg.ps` from the home L3 6.46 G/s at 1.53 nJ, from DRAM 1.17 G/s at 9.6 nJ, from a scratchpad 2 hops away 7.43 G/s at 966 pJ; `fscwl.ps` into the L2 14.5 G/s at 429 pJ; `fscwg.ps` into DRAM 0.50 G/s at 19.5 nJ | M | E48 | same, `gs/E/fgwl.ps/…`, `fgwg.ps`, `fscwl.ps`, `fscwg.ps` |
| A gather's cost per line and per instruction, from the L2 | 104 pJ per instruction plus 338 pJ per line it fetches (least squares over the seven patterns, 0.5–8 lines per instruction, random data); one or two lines take about one L2 latency (53.0 / 49.7 minion-cycles), eight lines four rounds (176–180) | D (fit on M) | E48 | `GSF`, `.combined["gs/E/fgw.ps/dram-4K/<pattern>/random/h2/mff/n1024"]` (`pj_per_element`, `cpi_med`); `manual.json` `gs` |
| Masked lanes | from the L1 a gather takes 10.9 minion-cycles an instruction with 8, 4 or 1 lanes active (102, 82, 69 pJ an instruction); from the L2 90.2 and 13.5 cycles with 4 and 1 lanes (179.7 with 8) | M | E48 | `GS`, `.items[item=GS-RATE].pooled["gs/E/fgw.ps/dram-{512B,4K}/rand/random/h2/m{ff,0f,01}/n1024"]` |
| Element size | `fgh.ps` and `fgb.ps` cost what `fgw.ps` costs per element and per cycle (L1 13.0 and 12.5 against 12.8 pJ; L2 355 against 354 pJ) | M | E48 | same, `gs/E/fg{h,b}.ps/…` |
| One minion against the chip | one minion's rate (both harts) × 1,024 predicts the chip's within 2%: L1 451 against 452 G/s, L2 27.9 against 27.4, a scratchpad 2 hops away 10.1 against 10.2 | M | E48 | `GSF`, `.combined["gs/R/fgw.ps/<table>/rand/random/h2/mff/nM1"]` against `gs/E/…/n1024` |
| A gap | the word gather from 64 KB per hart has energy on aifoundry3 only (9.2 nJ): on aifoundry2 and aifoundry1's card 1 every energy burst of it was dropped by the pre-registered clock rule (one launch per burst at an implied 0.594 GHz, just under 0.595–0.605; telemetry 600 MHz); the rule was not relaxed | M | E48 | `GSF`, `.cards.<card>.dropped` |

## The host link (E50, 27 Sep, three cards)

aifoundry2 / aifoundry3 / aifoundry1-c1, each the mean of five runs (a run's value is the median of its repeats).
`PCIE` means `docs/reports/data/2026-09-27-pcie/pcie.json`.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Negotiated link | **16.0 GT/s x8** on every card in every run: 15.75 GB/s per direction after 128b/130b coding | M | E50 | `PCIE` `hosts.<card>.link_speed`, `.link_width`; `meta.link_gbs` |
| Host to card, DMA-only, 256 MB | **12.47 / 12.60 / 12.46 GB/s** (79–80% of the link figure) | M | E50, P1 | `PCIE` `bw.<card>.h2d.dma[bytes=268435456].gbs` |
| Card to host, DMA-only, 256 MB | **10.54 / 10.41 / 10.41 GB/s**; fastest at 16 MB (11.75 / 10.99 / 10.69), slowest above it at 64 MB | M | E50, P2, P3 (failed: the slower direction) | `PCIE` `bw.<card>.d2h.dma[]` |
| A program's staged copy, 256 MB | to the card **7.15 / 5.20 / 7.79 GB/s**, back 6.53 / 4.78 / 6.97; 98–100% of 1/(1/DMA + 1/memcpy) with the hosts' memcpy at 17.4 / 9.2 / 21.4 GB/s | M, D | E50, P4a, P4b (failed on aifoundry3) | `PCIE` `bw.<card>.<dir>.staged[]`, `hostcopy.<card>[]` |
| Half the DMA-only rate (n½), to the card | **2.0 / 2.1 / 2.2 MB** per copy | M | E50, P5 | `PCIE` `n_half_log2.<card>.h2d_dma` |
| Empty kernel on 32 shires | launched and waited for **566 / 556 / 565 µs**; queued, **103.6 / 103.7 / 104.1 µs** each; the difference 463 / 452 / 461 µs, mostly the runtime's 500 µs idle poll (`ResponseReceiver.cpp:21-22`) | M, R | E50, P8, P9a, P9b | `PCIE` `launch.<card>.single_us."32"`, `.b2b_us."32"`, `predictions[id=P9b]` |
| Empty kernel on one shire, queued; what the other 31 shires add | **91.2 / 92.2 / 92.4 µs** each on one shire; the 32-shire figure less this, 12.4 / 11.4 / 11.6 µs (11.4–12.4), the multicast's own part not separated | M, D | E50 | `PCIE` `launch.<card>.b2b_us."1"`, `.b2b_us."32"` |
| A 4 KB copy after a random 0–1 ms gap | **377 / 379 / 411 µs** on average (the four variants) | M | E50 | `PCIE` `lat.<card>.sporadic.<variant>.mean_us` |
| Two host-to-card DMA commands in flight against one at a time | **0.49** on every card (both directions at once: 1.35–1.38 times the faster one) | M | E50, P11 (failed: registered with two in flight), P12 | `PCIE` `derived.<card>.h2d_two_in_flight_over_one`, `.duplex_ser_over_faster_ser` |
| The predictions | 31 verdicts passed, 8 failed (P3, P4a, P4b, P11), 5 inconclusive (P6, P7: the back-to-back round trips, which kept a fixed variant order) | P→M | E50 | `docs/reports/data/2026-09-27-pcie/PREREG.md`; `PCIE` `predictions[]` |

## The governor on the cards' own build, and DV2 (E51, 28 Sep; development, not validated)

`DV2` means `docs/reports/data/2026-09-28-dvfs2-aifoundry2/`; `V3` means `docs/reports/data/2026-09-25-claims-v3/`.
`recount_v3.py` is `tools/claims-v3/dv2/recount_v3.py` (run from the repository root). Source rows cite et-platform
`ffca4cbb4` (= `cafe03fc3^`, BL2 0.20.0, the closest public source to release 1.3.1) and `da192816a` (BL2 0.18.0,
release 1.2.0), `device-bootloaders/src/ServiceProcessorBL2/`. **dev** = E51's development data: it chose the
frozen validation's parameters and tests nothing; the validation (`DV2/plan/PREREG-VAL.md`) has not run.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| The temperature the governor compares, every build | the integer mean of the 34 minion-shire sensors, each truncated to whole °C (the I/O shire not included), tested as `mean > 65`; no per-sensor or hottest-sensor path to the clock | R | R3 at `353f20e`, `ffca4cbb4`, `da192816a` | `driver/pvt_controller.c` (`pvt_get_minion_avg_temperature`); `services/thermal_pwr_mgmt.c` |
| 0.20.0's thermal response | no busy test; a blocking loop: one table point down, sleep 1,000 ticks, re-read the mean, repeat while above 65; the power branch, the idle reset included, locked out meanwhile; exit to the boot point, then a one-call climb to the top on the next pass if busy and under the TDP; the power trigger is the PMIC's instantaneous reading | R | R3 at `ffca4cbb4` | `services/thermal_pwr_mgmt.c` (`update_module_current_temperature`, `thermal_throttling`, `power_throttling`) |
| 0.18.0 (aifoundry1's card 1) | the same loop, with fixed 50 MHz steps between 300 and 700 MHz | R | R3 at `da192816a` | `include/thermal_pwr_mgmt.h`, `services/thermal_pwr_mgmt.c` |
| aifoundry1's card 1 never raises its clock (corrects "launched warm" on three pages) | 600 MHz in all 318,667 samples of the three-card check, and the SP's own clock minimum and maximum 600/600 in every one (a statistics reset does not clear them, so they reach back before the check), although 9,461 were busy at 45–65 W (45 W or more, under the 65 W TDP) at a mean of 64 °C or less; its 65 blocks started at 56–69 °C (median 62 °C). The same counts as the DVFS page's; E48's gathers-and-scatters passes, filed in the same tree, are left out | M | E35–E46 | `recount_v3.py cool-busy` over `V3/raw/aifoundry1-c1/` (gs/ left out; `--with-gs` adds E48: 359,687 and 11,612); `dvfs.json` `v3.sp_readouts` |
| aifoundry2's die above 90 °C with nothing acting | the mean passed 90 °C in 8 version-3 telemetry files (12,176 samples), every sample at 600 MHz; catalogue hot pass 11 (26 Sep, 02:26–02:31 PDT): mean 90–103 °C, above 90 °C in 2,565 of 2,567 samples, hottest sensor up to 106 °C, board up to 86.9 W (83.6 W at the first 103 °C sample), no safe state | M | E45 | `recount_v3.py over90`, `recount_v3.py pass`; `V3/raw/aifoundry2/cat/p11/` |
| The PMIC system temperature the SP reads | the SP reads the PMIC's temperature only when it starts or resets its statistics (`thermal_pwr_mgmt.c:2995–3001`, under the note "PMIC is currently reporting system temperature as 0") and feeds the statistic's minimum and maximum a literal 0 on every other pass (`:663–664`), so `sp.system_c` is not a per-sample reading of the PMIC. In the three-card check it read 0 on all three cards (its 653 non-zero triples are (0, 65535, 0), a reset's initial minimum): the PMIC gave 0 at each reset; the samples say nothing more. The evidence that nothing acts on the die's temperature is the telemetry (the row above) | R, M | R3 at `ffca4cbb4`; E35–E46 | `services/thermal_pwr_mgmt.c`; `recount_v3.py systemc` (994,077 samples, gs/ left out) |
| The mean, not the hottest sensor, while busy (**dev**) | the clock held 800 MHz for ≥ 1.0 s after the hottest sensor read ≥ 67 °C in 12 of 12 runs (up to 69 °C); of 5 runs where the hottest sensor led the mean to 66 °C by ≥ 1.5 s, 4 stepped 0.1–0.2 s after the host's mean read 66, none within −0.3…+0.6 s of the hottest sensor's 66 | M | E51 | `DV2/reductions/dev-idle.json` items `G1-H`, `G1-T`; `DV2/raw/p6038/runs.jsonl` |
| The mean, not the hottest sensor, at idle (**dev**) | at 01:00:00 the mean read 64 °C and the hottest sensor 66 °C; no thermal entry until 01:08:11 | M | E51 | `DV2/raw/p1003/`, `DV2/dv2.json` |
| The 0.20.0 loop on the card (**dev**) | thermal episodes under 60 s last k × 0.4053 s to within 1.43 ms (17 of 17, k = 0–3: 16 on the idle card, 1 at a session start); 18 of 20 thermal entries follow the SP's own idle line | M | E51 | the SP trace-ring dumps `DV2/raw/p1*/sp.bin`, `DV2/dv2.json` (`lines`) |
| Climbs and descents (**dev**) | 57 of 57 climbs show at most one 700 MHz sample (33 none); 26 of 26 descents stay 0.3–0.7 s at 700 MHz (median 0.5 s) | M | E51 | `DV2/reductions/dv2-dev.json`, `host_bands` |
| No hysteresis (**dev**) | every entry line printed 66 °C and every exit line 65 °C (20 each); 82 of 82 up-steps while hunting from a reading ≤ 66 °C (79 ≤ 65), none ≥ 67 | M | E51 | `DV2/dv2.json`; `DV2/reductions/dv2-dev.json`, `host_bands.G2-U` |
| Latency (**dev**) | launch to the first 800 MHz sample: median 0.9 s, at most 1.11 s (14 launches); kernel end to 600 MHz: 0.00–1.15 s (9 runs) | M | E51 | `DV2/reductions/dev-idle.json` items `G3-L`, `G3-I` |
| Placement against the first throttle, 192 minions at 800 MHz from 62 °C (**dev**) | interior (INT16@12) 3.60 and 3.90 s; perimeter (PER16@12) 5.00 s and more than 6.95 s (censored at the kernel's end): 1.4 and ≥ 1.8 times as long; mean log ratio 0.45 over 2 blocks, above the 0.28 ± 0.10 predicted from aifoundry3's couplings (the inputs are frozen as numbers in `DV2/plan/prereg-val.json`; aifoundry3's placement runs behind them are E52's development blocks, `docs/reports/data/2026-09-28-heat-placement/reductions/dev-r3.json` items `PLACE-t` and `SPREAD`) | M, P | E51 | `DV2/raw/p6038/runs.jsonl` (`obs.trip_s`); `DV2/reductions/dev-idle.json` item `G4` |
| Recovery (**dev**) | 20 of 20 exits (19 on the idle card, 1 at a session start) followed by the SP's idle line, 17 of them one pass later (0.119–0.131 s) | M | E51 | `DV2/dv2.json` |
| Time in the thermal state | aifoundry2 at 00:40 on 28 Sep: 747,342 s of thermal-down in 9 d 5 h 36 min of uptime (8.65 of 9.23 days; longest stay 184,180 s), power-up 23.05 s. aifoundry3 at 00:33: power-up, power-down, thermal-down, power-safe all 0 after 2 d 8 h (**dev**, one reading) | M | E51 | `DV2/raw/p1001/z1.json` (`residency`, `uptime`); `DV2/raw-aifoundry3/z2.json` (aifoundry3's query) |
| aifoundry2's idle reading overnight (**dev**) | 59–72 °C on a 10–30 minute scale; idle power 25.7 W at 59 °C, 31.1 W at 72 °C | M | E51 | `DV2/raw/p1*/z1.json` (`reading_c`, `board_w`) |
| aifoundry2's Master Minion hung | 02:50:53 PDT, 28 Sep: lift 2 (a stream of short kernels, launched 0.6 s after lift 1 ended) ran its 14 ms calibration kernel at 02:50:53.746, 21 ms after the host first read the idle reset's 600 MHz; it returned ok and measured 0.77 GHz; the next kernel never completed (board back at 26 W, clock 600 MHz); the next two launches failed with "Couldn't use the HPSQ. Perhaps the Master Minion is hanged?"; an SP runtime-error event, the counter's sixth, at 02:50:57.6 ± 0.07 s (the first five, 20–25 Sep, did not stop the card); the SP still answered (02:52: 600 MHz, 25.9 W, 60 °C). Cause not established | M | E51 | `DV2/raw/ALERT-MM-HANG.json`, `DV2/raw/p6041/` (`launches.jsonl`, `heater-1-pre.out.gz`, `tel-1.jsonl.gz`), `DV2/raw/p1111/z1.json`; `DV2/incident/` (`kernel_events.py`); `DV2/dv2.json` `incident` |
| aifoundry2's Master Minion restored | 28 Sep, owner-approved: the sysfs per-card reset at 06:39 re-attached the device (kernel log 06:39:28) but not the Master Minion (launches at 06:40 and 06:47 failed with the same HPSQ message); the management reset (`DM_CMD_RESET_ETSOC`) at 08:32:45 recovered it ("Device is resetting" 08:32:46.5–51.5, the device back 08:32:52); at 08:33 a test on 1 minion ran 3 launches of 0.487 s, each ok, at 0.599 GHz (the device held 1.65 s) | M | E51 (its incident) | `DV2/incident/recovery.txt` |

## Heat placement (E52, 27–28 Sep; development, calibration and the frozen validation on aifoundry1's card 1)

`HP` means `docs/reports/data/2026-09-28-heat-placement/`; `dev-r3` is `HP/reductions/dev-r3.json` (`reduce.py --dev`
on `HP/raw/aifoundry3`, reproduced byte for byte), `.dev.items[<item>]`. **dev** = development data on aifoundry3: it
chose the frozen validation's parameters and predictions and tests nothing; **cal** = card 1's calibration on a
workload that is never tested; **val c1** = the frozen validation on aifoundry1's card 1 (`HP/val.json`,
`reduce.py --val` on `HP/raw/aifoundry1-c1`, reproduced byte for byte; its words PASS, FAIL, INSUFFICIENT are final).
t66 is the time from the first launch to the first 10 Hz sample with the host's mean at
66 °C (the governor's trip), from the same falling start edge; L = ln(t66 A / t66 B); intervals are 99% t over blocks.
Only signs transfer between cards: the dev and val c1 sizes are each card's own.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| The same 512 minions on the perimeter take longer to the trip than on the interior, Tier L from 61 °C (**dev**) | PER16@32 against INT16@32: L = 0.479 [0.409, 0.550], 1.62 [1.51–1.73] times as long, longer in 9 of 9 blocks; means 87.8 s and 54.4 s; UNI32@16 (all 32 shires, 16 minions each) 76.5 s, L against the interior 0.339 [0.243, 0.435] | M | E52 | `dev-r3` items `PLACE-t`, `SPREAD`; the blocks' `runs.jsonl` |
| At equal power and work (**dev**) | switching power over idle 14.02 (interior), 13.81 (perimeter), 13.87 W (spread); perimeter less interior −0.21 [−0.38, −0.05] W, inside ±0.5 W; work equal to within 0.002%; power-corrected L_P 0.464 [0.400, 0.529] | M | E52 | `dev-r3` `PLACE-t.power_w`, `.work`, `.L_P` |
| The same, Tier S: one 7 s launch from 64 °C (**dev**) | L = 0.581 [0.454, 0.708], 1.79 times as long, 6 of 6 blocks; means 1.70 and 0.95 s | M | E52 | `dev-r3` item `PLACE-tS` |
| The hottest sensor's lead over the mean (**dev**) | grew 1 °C less by the crossing with the perimeter work than with the interior work, in each of 9 Tier L blocks (whole degrees); concentrated against spread work (CONC, Tier S) 0.11 [−0.30, 0.52] °C, no measurable lift | M | E52 | `dev-r3` `PLACE-t.dhot`, item `CONC` |
| The I/O sensor and work beside it (**dev**) | 0.67 [0.37, 0.97] °C warmer rise with 128 minions by the I/O corner (B4NE) than in the far corner (B4SW), Tier S | M | E52 | `dev-r3` item `MAP` |
| Half power never reaches the trip on aifoundry3 (**dev**) | 256 minions from 64 °C: five of six placements (INT16@16, PER16@16, CEN8, EDGE8, MEM8) did not read 66 °C within 150 s; UNI32@16 (512) did in 21.3 s. L8 and G8 dropped by the rule D-L8 | M | E52 | `HP/raw/aifoundry3/hp/p2301/`; `python3 HP/reductions/dl8_check.py HP/raw/aifoundry3 2301` |
| aifoundry1's card 1 heats faster than aifoundry3 (**cal**) | 768-minion chains from 61 °C: median t66 11.7 s against aifoundry3's 27.0 s (its R3 calibration chains); from 60 °C 17.2 s, where card 1's start edge settled; run-to-run spread of ln t66 0.101 against 0.047 (ratio 2.15) | M | E52 | `HP/reductions/v0.json`; `HP/raw/aifoundry1-c1/hp/p5501/`, `p5502/`; `tools/claims-v3/hp/prereg/prereg.json` `cv` |
| No on-card test of the governor's input here | the probes read SILENT on aifoundry3 (latched) and card 1 (its clock never moves); aifoundry2 rested at 67 and 66 °C (27 Sep 16:51, 18:52), inside its thermal loop: NOT OBSERVABLE. What the governor compares rests on the source and E51 (the rows above) | M, R | E52 | `HP/raw/*/hp/p801/probe.json`, `HP/raw/aifoundry2/hp/a2/p*/a2.json` |
| Registered for card 1 | PLACE-t and PLACE-tS, both SIGN+ (the perimeter lasts longer), 5 blocks each, with POWER ±0.5 W and WORK ±1% equivalence on their pair; κ, CONC, MAP and every L8/G8 item reported, not tested | P | E52 | `tools/claims-v3/hp/prereg/PREREG.md` (SHA-256 `a1bdc4e42c88c875f53afe112141df95bfac13370243650cf99b6b93c53ff890`) |
| Short bursts: the perimeter lasts longer on card 1 too (**val c1**, PLACE-tS **PASS**) | one 7 s launch from 64 °C: L = 0.715 [0.546, 0.883], 2.04 [1.73–2.42] times as long (means 2.56 and 1.25 s), in 5 of 5 blocks; WORK PASS (within 0.009%); POWER waived (departure 37, for aifoundry3's sub-second interior runs; card 1's crossed in 1.14–1.41 s, so a value exists: −0.27 [−0.42, −0.13] W, reported) | P→M | E52 | `HP/val.json` `.validation.items["PLACE-tS"]`; `HP/heat.json` `val_blocks` |
| Sustained heating on card 1 (**val c1**, PLACE-t, primary: **INSUFFICIENT**) | chains from 60 °C capped at 150 s: L = 0.198 [−0.423, 0.819], 1.22 [0.66–2.27] times; 7 of PLACE-t's 10 runs (10 of all 15 Tier L runs) never read 66 °C within 150 s, three of five blocks had both runs cut off (L = 0); the two blocks that decided had the perimeter longer (over 150 against 110.2 s; 142.6 against 72.1 s), none the interior. POWER −0.20 [−0.71, 0.32] W INSUFFICIENT; WORK PASS | P→M | E52 | `HP/val.json` `.validation.items["PLACE-t"]`, `["PLACE-t/POWER"]`; `HP/heat.json` `val_blocks.summary.L16` |
| Transfer of development's signs, H11 (**val c1**) | INSUFFICIENT (PLACE-t INSUFFICIENT, PLACE-tS PASS); by DESIGN2's frozen table no theory survived and none was refuted: H2 undecided (PLACE-t INSUFFICIENT); H3 and H4 not registered (the table needs PLACE-t registered SIGN− or EQUIV; it was registered SIGN+); H13 INSUFFICIENT, H1/H1′ not tested on a card | P→M | E52 | `HP/val.json` `.validation.items.H11`; `HP/plan/DESIGN2.md` "Theories survived" |
| Card 1's calibration chains were slower in the validation (**val c1**, reported) | 768-minion chains from 60 °C in the Tier L blocks 17.6–27.3 s (median 22.8 s, 6 chains) against 17.2–20.5 s (median 17.2 s) at V0; session 2's six Tier L runs were all cut off at 150 s | M | E52 | `HP/heat.json` `val_blocks.summary.L16.cal_t66`, `.by_session`; `HP/reductions/v0.json` |

## The effect of overheating (E53, 28 Sep; pre-registered, aifoundry3 and aifoundry1's card 1)

`OH` means `docs/reports/data/2026-09-28-overheating/`; `red/` its `reductions/` (`tools/claims-v3/oh/reduce.py --all`
under PREREG SHA-256 `1b34d189…` (amendment 2; the original freeze `8d620b64…` at 10:11 PDT, before any OH-1 or OH-2
block); `extras.json` is `OH/extras.py`, descriptive, no verdict); `an/` its `analysis/` (the existing record, re-read by
`OH/scripts/*.py`, no card time). Temperatures are the host's whole-degree readings: the mean of the 34 minion-shire
sensors, and the hottest single sensor in each 1 s window (a peak-hold reset every second, anonymous). **val** = a
registered verdict; the page is "The effect of overheating".

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| The registered verdicts | 20 of 21 PASS; card 1's OH2-b INSUFFICIENT (it never passed a 76 °C mean); card 1's OH2-d growth not testable | M | E53 | `red/verdicts.json`; the per-card count: `OH/overheat.json` `verdicts` |
| The hottest sensor at the 0.20.0 rule's point | mean 65 °C: hottest 66–68 °C (median 67); mean 66 °C (the first reading `mean > 65` acts on): 67–69 °C (median 68); both cards, 136 windows. A statistic of the sensors: neither card's governor acts (aifoundry3's is latched by its zero TDP; card 1's 0.18.0 build never moves its clock) | M | E53 | `red/extras.json` `near_65` |
| Concentrating the load does not widen the gap (**val**, OH1-a/b/c PASS) | one shire at full load (32 minions, about 0.9 W) median +1 to +2 °C (max +2); central 2 × 2 block +2 (max +3); idle +1 to +2; largest in all 677 OH-1 windows +3 | M | E53 | `red/oh1.json` `by_card_cond`, `OH1-a` |
| The gap under the whole-chip heater (**val**, OH2-d) | at most +3 inside heater launches; aifoundry3's median +2 at 60–70 °C, +3 at 80–85 °C; over all 3,631 OH-2 windows +4 17 times (aifoundry3 12, card 1 5), never +5 | M | E53 | `red/oh2.json` `OH2-d`, `dhot_all_windows` |
| No wrong result hot (**val**, OH2-a PASS) | 663 exact-checked launches (342 in the verdict blocks, 321 in the stopped attempts; 1,395 compared records): 0 wrong, 0 tensor-error CSRs, 0 not ok, 0 void; hottest an 81 °C mean with a sensor at 84 °C (aifoundry3); 30 launches at 80–85 °C (95% upper bound 0.1 per launch); the DRAM relay checked to 81 °C (before: 66 °C) | M | E53 | `red/oh2.json` `OH2-a`, `by_bin`, `hottest_checked`; `red/oh2-aborted.json`; `red/extras.json` `totals` |
| The same work per cycle hot (**val**, OH2-b on aifoundry3 PASS) | all 18 kernel metrics (fma fp32/fp16/int8 sweeps, GEMV, mmbench int8/fp32, DRAM and mesh relays) at an 80–85 °C mean within 0.052% of rest (limit 0.1%); card 1 at 70–80 °C (not registered): 17 of 18 within 0.1%, the DRAM relay −0.39% inside its 0.75% rest spread | M | E53 | `red/oh2.json` `OH2-b`; `red/extras.json` `warm_vs_rest` |
| The clock does not move with heat (**val**, OH2-c PASS) | the heater's implied clock 0.5994–0.5995 GHz and 546.001 cycles per op in every 5 °C band, 50–85 °C (aifoundry3), 55–80 °C (card 1) | M | E53 | `red/oh2.json` `OH2-c` |
| DRAM refresh stays at 1× hot (**val**, OH2-e PASS) | 2,325.4 minion cycles at die means of 52, 54, 73 and 75 °C, as programmed (3,616 DFI clocks at 933 MHz) with derating off | M, R | E53 | `red/oh2.json` `OH2-e`; `etsoc-hal/src/memshire_ddr_init_functions.c:4441-4443, 4686-4688` at `836a4ab60` |
| The supply does not sag with heat | minion rail on the die 523 → 520 mV (aifoundry3), 499 → 498 mV (card 1) from 50–55 °C to the hottest band; SRAM 698 → 697 and 751 mV; NoC 484 → 483 and 486 mV | M | E53 | `red/oh2.json` `die_mv_by_band` |
| The idle laws still hold (**val**, OH3-a/b PASS) | E53's idle board power per degree within 0.20 W (aifoundry3, 60–77 °C) and 0.22 W (card 1, 60–70 °C) of E44's laws; refitted leakage doubling 19.4 °C (aifoundry3), 25.0 °C (card 1) | M, F | E53 | `red/oh3.json` |
| aifoundry1's card 0 after its September overheating | its service processor's standing statistics (never reset): maximum mean 119 °C, a sensor peak-hold of 123 °C, I/O shire 118 °C, board maximum 75.24 W; now 60–63 °C and 17.0–18.5 W at 300 MHz and 398–399 mV (5,353 guard samples), against 18.6–18.8 W reported before the episode at a die temperature not recorded (a loose comparison). Supersedes "115–117 °C" as its highest reading (that was the host's reading on 25 Sep) | M | E53 | `OH/raw/aifoundry1-c1/oh/p*/guard.jsonl.gz` (`sp.minion_c[2]`, `temp_c.minshire[2]`, `temp_c.ioshire[2]`, `sp.board_max_w`); `OH/overheat.json` `card0` |
| The highest readings on record, per card | aifoundry2 a 103 °C mean with a 106 °C sensor (catalogue pass 11, 26 Sep, 600 MHz, nothing tripped); aifoundry3 90/93; card 1 88/91; card 0 119/123 | M | E36–E46, E52, E53 | `an/max_temps.json` (1,979,875 samples) |
| Correctness across the September record | 151,984 launches joined to telemetry, 5,927 with results checked; the only wrong results are two DRAM relay launches at 65–66 °C on aifoundry2 during an 800 → 600 MHz step (23 Sep); aifoundry2's mmbench checks passed to a 97 °C mean; the catalogue's 91–103 °C pass completed but checks no arithmetic | M | E23–E52 | `an/correct_vs_temp.json` (E53's directory left out: its reducer covers it) |
| The heater's cycles per op before E53 | 546.001 (546.001–546.002) in every bin from 40 to 101 °C on three cards; the catalogue's hot passes (88–96 °C) against warm (76–77 °C): median 0.00%, range −0.08 to +0.10% over 30 configurations | M | E36–E46 | `an/timing_vs_temp.json` |
| Where idle leakage plus a full random matmul would reach the card's 88 W input (**derived, extrapolated**) | a die mean of about 90 °C (card 1), 102 °C (aifoundry3), 106 °C (aifoundry2): each card's E44 law plus the 27.2 W flip-count estimate (12-heat-management.md) against the 88 W 12 V input (docs/research/power-telemetry.md); the laws extrapolate to 77, 88 and 120 W idle at 116 °C | D | E44 | `OH/overheat.json` `idle.<card>.t_matmul_88w`, `an/idle_vs_temp.json` |
| An hour hot, in wear | at 0.7–0.9 eV an hour at 117 °C ages the chip like 25–61 h at 65 °C or 6.4–10.9 h at 85 °C; aifoundry2's 106 °C sensor 13–28 times the 65 °C rate | D, X | JESD47 note a (Arrhenius) | `an/derived.json` `af_pairs` |
| The firmware's thermal limits (BL2 0.20.0, aifoundry2 and aifoundry3; it acts on aifoundry2 only, aifoundry3's is latched; card 1 runs 0.18.0 and card 0 0.21.2: 14-card-behaviour.md) | throttle while the integer mean of 34 truncated shire sensors > 65 °C ("early indication"), one point per pass down to the lowest point, nothing below; a PMIC alarm at 75 °C and 75 W on the PMIC's own "system temperature" (a note says it reads 0; the statistic is fed a literal 0), whose handler sets the frequency register to 300 MHz and reprograms the PLL only if the voltage lookup fails; no shutdown path; the 52 °C "expected average temperature" is a default reset value, not a limit; per-sensor calibration fuses not read; process detectors `MEASUREMENT_DISABLED`, no reader | R | — | et-platform `ffca4cbb4`: `include/thermal_pwr_mgmt.h:31-32, 43-46, 66`; `services/thermal_pwr_mgmt.c:656-679, 663-664, 2001-2034, 2995`; `include/bl2_pmic_controller.h:261-282`; `driver/pvt_controller.c:1279-1306`; `include/bl2_pvt_controller.h:100-102, 127` |
| The PMIC's 75 W threshold did not act | aifoundry2's board reached 86.9 W in the 90–103 °C catalogue pass 11 at 600 MHz, with no safe state | M | E36–E46 | `an/derived.json` `a2_p11`; 14-card-behaviour.md "Nothing limits the die's temperature" |
| A swing to 120 °C against one to 65 °C (both from 25 °C), in package fatigue (**derived**) | 5.6–7.6 times the damage per cycle (Coffin-Manson, exponent 2 for solder joints in JESD47I Annex A, 2.35 for the package in RAMP §3.4) | D, X | — | `an/derived.json` `coffin_manson` |
| Outside limits, for comparison | throttle points 95–110 °C (Ryzen 7000 95, i9-13900K 100, RX 5700 hotspot 110, Jetson Orin 99/103, shutdown 104.5/105); THERMTRIP near 125 °C; JESD47 qualification 1,000 h at Tj ≥ 125 °C, 0 of 231 may fail; LPDDR4X standard grade 85 °C case; simulated 7 nm crossover (ZTC) about 0.53 V | X | the page's sources | `OH/sources.json` |

Corrections this work makes (the page carries them): the host has **no per-sensor temperature series** (E51 and E52 recorded
the mean, anonymous peak-holds and the I/O-shire sensor, not 34 sensors at 10 Hz); "card 0 throttled 10 times" has no
source (the 10 in 14-card-behaviour.md, "Selecting one card on a two-card host", counts aborted `dev_mngt_service`
processes); the catalogue's 91–103 °C launches "completed", they were not arithmetic-checked; the SRAM rail is 0.70–0.75 V
by card, not 0.705 V everywhere; the 75 °C PMIC alarm reads the PMIC's own temperature, not the die, and on 0.20.0 its
handler does not reprogram the PLL; the 52 °C in the firmware header is a default reset value, not an expected die
temperature; E53's two cards do not throttle at any temperature (aifoundry3 latched, card 1 on 0.18.0), so its mean-65
numbers are sensor statistics, and "nothing limits the die at 600 MHz" holds for the 0.20.0 and 0.18.0 cards, not for
card 0 (1.4.1), which dropped to 300 MHz after 115–117 °C.

## Ridge points (derived; no card time)

Peak compute divided by each level's measured bandwidth, at 600 MHz on 1,024 minions. Kind `D`: arithmetic on
measured numbers, not a new measurement. The bandwidths are the 2026-09-18 reports' (reproduced within 0.3% by the
2026-09-23 reruns on both cards, the rl-pass runs the energy manual pools); the energy balance points use the energy manual's data
(`docs/reports/data/2026-09-23-energy-manual/manual.json`). Recompute every row with `python3 scripts/ridge-points.py`.
Values are FLOP (int8: OP) per byte fetched, fp32 / fp16 / int8.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Tensor peak per minion-cycle | **16 / 32 / 128** ops (9.83 TFLOP/s, 19.7 TFLOP/s, 78.6 TOP/s on 1,024 minions at 600 MHz) | X | Minion VPU Specification §2; matmul report | `scripts/ridge-points.py`, `PEAK` |
| Ridge, own shire (L2 or L2 scratchpad) | **4 / 8 / 32** at 4.0 B per minion-cycle (2.46 TB/s); 2 / 4 / 16 at the banks' 256 B per shire-cycle | D | memory-hierarchy streaming probes | `docs/reports/data/2026-09-18-memhier-aifoundry2/energy*/runs.jsonl`, configs `l2`, `scp-local` |
| Ridge, L3 or another shire's scratchpad | **10 / 20 / 80** at 0.96–0.98 TB/s | D | same, configs `l3`, `scp-remote`, 600 MHz launches only | same file, `implied_ghz` 0.59–0.61 |
| Ridge, DRAM | **130 / 259 / 1,036** at 76 GB/s | D | same, config `dram`; 76 GB/s on both cards in the 23 September reruns (the sparsity report's shorter probe read 72 on aifoundry3) | same file; `docs/reports/data/2026-09-18-sparsity-aifoundry3/tload-dram-all.jsonl` |
| Ridge, host over PCIe Gen4 x8 | **624 / 1,248 / 4,993** at 15.75 GB/s, the link figure; at the host-to-device DMA rate measured on 27 September (12.46–12.60 GB/s, E50), **780–789 / 1,560–1,578 / 6,242–6,314** | X; D on E50 | the link figure: 16 GT/s × 8 lanes × 128/130 ÷ 8 (datasheet §1: Gen4 x8); the measured rate: E50 (the ridge page still quotes only the link figure) | `docs/reports/data/2026-09-27-pcie/pcie.json`, `bw.<card>.h2d.dma[bytes=268435456].gbs.mean`; the chip diagram's fact `ridge.levels` (`docs/reports/data/2026-09-27-chip-diagram/build_facts.py`) |
| Intensity of one full-size TensorFMA | **4 / 8 / 16** per byte (2 KB of A and B per op) | D | PRM ch. 9 | `scripts/ridge-points.py`, `OP_BYTES` |
| Smallest DRAM-resident C block that is compute-bound | about **520 × 520** (fp32, fp16), **1,040 × 1,040** (int8) | D | H/e ≥ ridge, H the harmonic mean of the block's sides, e = bytes per element | the report's "What it takes to reach them" |
| Energy balance, fp32: FLOP per byte at which moving a byte costs as much energy as the arithmetic | L1 0.15 (`flw.ps` against `fmadd.ps`, random data), own shire 0.87, other shire 2.3, L3 3.6, DRAM **42** (random fp32 at 2.89 pJ per FLOP over idle; on all-zero operands, 0.21 pJ, mostly the awake-core floor, every level from the shire outward lies above its time ridge) | D | energy manual §3.2 (tensor unit), §4.1 (the L1 row), §4.2 (levels) | `docs/reports/data/2026-09-23-energy-manual/manual.json` (`tensor.bars`, reruns; `catalogue.combined`: `flw.ps/random/h2`, `fmadd.ps/random/h2`, `tload/*`); the page's `ridge-data` `energy` |

Two corrections to earlier reports came out of this, both verified in the raw data:

- The memory-hierarchy report's first version averaged launches taken at 600–800 MHz (2.80 TB/s for L2, "about 144
  B/cycle"). At 600 MHz the cycle counters give **2.45 TB/s** and **128 B per shire-cycle**, which that report now
  prints.
- The **128,000 MB/s** DRAM figure the runtime reports is a placeholder constant in the service-processor firmware
  (`device-bootloaders/src/ServiceProcessorBL2/include/mem_controller.h`), not a measurement or a configured rate.

## External numbers (not measured here)

| Claim | Value | Kind | Source |
|---|---|---|---|
| A100: transistors, die, process, TDP | 54.2 B, 826 mm², TSMC 7 nm, 400 W SXM4 | X | R7 |
| A100: memory bandwidth | 1,555 GB/s, HBM2 (40 GB); 1,935–2,039 GB/s for the 80 GB HBM2e part | X | R7 |
| A100: maximum boost clock | 1,410 MHz | X | R7 |
| A100 matmul measured by Horace He | 257 TFLOPS random / 295 TFLOPS zeros, bf16, 330 W limit, 88 W idle | X | R8 |
| A100 energy per FLOP | 1.28 pJ per bf16 FLOP (330 W / 257 TFLOPS); against this card 5.4× better than its fp32 (6.96 pJ) and 2.6× than its fp16 (3.3 pJ); the A100's fp32 CUDA-core datasheet figure (19.5 TFLOPS at 400 W) is 20.5 pJ | D | R7, R8, E15 |
| A100 clock under Horace He's 330 W cap | 1,160–1,410 MHz, probably about 1,230 (257 of 312 peak TFLOPS needs at least 1,160) | D, A | R7, R8 |
| **A100 core voltage** | **0.85 V** | **A** | **Assumption.** Not published. 0.75 V is nominal for 7 nm per R6; GPUs run above nominal at full clock. The range 0.75–0.95 V changes the V² ratio from 2.1× to 3.3× |
| ET-SoC-1: transistors, die, mask layers | over 24 B, 570 mm², 89 layers | X | R6 |
| ET-SoC-1: memory | 256-bit LPDDR4x, 137 GB/s per chip | X | R6 |
| Esperanto's modelled chip power vs voltage | 275 W highest, 164 W @0.75 V, 118 W @0.67 V, ~20 W @0.4 V, 8.5 W @0.3 V | X | R6 — **modelled, with cores re-synthesised per voltage point**, not measured |
| Esperanto's per-core design target | 10 mW at 1 GHz, 0.425 V, 0.04 nF | X | R6 |

## Numbers that are *not* established

- **Anything about this chip at 0.4 V.** This card's firmware offers 600, 700 and 800 MHz at 0.52–0.62 V and
  nothing lower. Esperanto's 20 W headline is at an operating point never exercised here.
- **Per-FLOP efficiency on the workload the chip was designed for** (int8 with sparse memory access) against a
  GPU. The int8 arithmetic is 19× cheaper than fp32 here (E15), but no GPU comparison was run for it.
- **Anything requiring modified firmware:** per-event PMU counters on silicon, SRAM ECC error counts, the
  UltraSoC debug fabric. See Q7 in [02-requests.md](02-requests.md).
- **The thermal network in any other chassis.** 1.47 °C/W is this card in this desktop box, which idles at
  62–80 °C, and the flip budget built on it is also that day's room: the model's ambient is 22.8 °C, and each degree
  warmer takes 0.68 W (1/1.47) off it (Horace §8).
- **Whether the taped-out ET-SoC-1 ever drives its sleep transistors.** The chip-level netlist is not in the
  open drop; the tie-off is a fact about the Erbium configuration, and the card only shows that nothing
  observable uses them.
- ~~**Why aifoundry3's flashed TDP is 0 W.**~~ Answered on 2026-09-25: it is not flashed; a boot service on
  aifoundry3 sets it at every boot (14-card-behaviour.md).
- **Whether the 8% switching-power gap between the two cards is silicon, package or board regulator.**
  Separating those needs a third working card: aifoundry1's card 1 works since 25 September, and the version-3
  campaign measured it. It did not settle the question: E40's hot-against-cool test reads "not separated" on every
  card, and E45 puts the catalogue's temperature coefficient at +0.48 [0.07–0.90] %/°C on aifoundry2 and +0.30
  [0.18–0.42] on aifoundry3, which the registered rule reads as temperature, not the card.
- **Per-flip energies outside the tensor unit and the mesh links** (E11–E17, E31–E32), and the split of the
  unsensed 15 W of idle. E30 attributes the unmetered part of what a workload adds above idle (delivery losses plus
  a DRAM term, fitted over configuration means) and meters DRAM by droop; the idle 12–16 W (12–13 W on aifoundry3 at
  51–56 °C, 14–16 W on aifoundry2 at 66–82 °C) and the DRAM term's split below its regulator stay inferred.
- **Whether the heat-per-mm "ones" cost is resting-at-zero logic or precharged structures**, and how a hop's
  energy splits between router and wire (E31, E32). The mesh rail's meter gain has not been checked independently,
  and whether the links are low-swing, which the V² scaling assumes they are not, is unknown.
- **Whether a refresh or another stream's access closed each hart's row between its visits, or the activation is
  merely small**; E28 cannot tell. (The controller runs an open-page policy: rows close at a refresh or at another
  row's access, not on a timer; E1.)
- **Any table at 700 or 800 MHz.** The V²f ratios say what to expect; nothing was re-measured there.
- **A relay whose working set exceeds the 80 MB of scratchpad.** That is where on-chip hand-off would be the
  only option rather than the faster one; the flow control for it was not built.
- **Why Ivan's 6% differs from both of our numbers.** His code was not run.
- **Whether a hot line makes its shire measurably hotter.** The thermal telemetry is one chip-wide mean.
- **aifoundry3's thermal network.** Its heatsink is visibly faster than aifoundry2's, and no heat-then-cool
  characterisation was run on it. Do not apply aifoundry2's 1.47 °C/W to it.
- ~~**Whether the governor's power branch behaves as written.**~~ **Established on 2026-09-22 (E21):** on
  aifoundry3 it logs a throttle-down at every kernel start and can never step up, on a die 15 °C below the thermal
  threshold.
- **Why aifoundry3's board and rail readings change only about every 250 ms**, against 133 ms on aifoundry2: its
  service-processor loop or its PMIC. E41 narrows it to the loop's length, not why: with no poller aifoundry3's
  service-processor pass takes 224.1–224.5 ms, against 133.2 ms on aifoundry2 and 134.8 ms on aifoundry1's card 1.
- **Exactly which firmware build the cards run.** Their trace strings match service-processor firmware older than
  et-platform commit `60b40c10f` (24 September 2024); release 1.3.1's BL2 0.20.0 has `ffca4cbb4` as its closest
  public source, and E51's development data fit that build's governor, but the build itself is not in the tree and
  the validation has not run.
- **What hung aifoundry2's Master Minion** (28 September, E51). A launch during the governor's idle reset is a
  hypothesis only.
- **Whether the perimeter's longer time to the trip holds on another card in sustained heating** (E52). It held on
  aifoundry1's card 1 in short bursts (PLACE-tS PASS); the sustained test (PLACE-t) is INSUFFICIENT: 7 of its 10 runs
  (10 of all 15 Tier L runs) did not reach 66 °C within the 150 s cap, and 3 of its 5 blocks had both runs cut off. A test with longer chains, or a start edge chosen so card 1's
  512-minion runs cross, would be a new pre-registration, not a re-analysis.
- **Why the perimeter lasts longer** (E52). The die's edges may shed heat faster, or the 34 sensors of the mean may see
  less of heat made beside the edges and the unsensed I/O and PCIe cells; the host reads only the whole-degree mean and
  two unnamed extremes, which cannot tell these apart.
- **Whether aifoundry1's card 1 has active power management off or a latched governor.** Both explain a clock that
  never rises; the power-up residency since boot would narrow it.
- **The version-3 items that stayed INSUFFICIENT (E35–E47).** Each lacks the kept passes or cycles it needs on a card:
  - **The relay sweep's shape on aifoundry3 (E36, LAT-R).** aifoundry3 kept 2 of 3 relay passes (four of its relay
    host processes exited with code 139), so the ranking by the longest hand-off and the per-card ratios are untested
    there; on aifoundry2 and aifoundry1's card 1 the item fails anyway, on the mirrored offsets (d and 32 − d 2.7% and
    2.6% apart against 2%) (`V3R/lat.json`, `.items[item=LAT-R]`).
  - **The per-shire idle voltage pattern as a per-monitor offset (E41, TEL-Q).** aifoundry2 and aifoundry1's card 1
    have two complete idle captures each, not three; aifoundry3 fails three of the item's parts (its pass-to-pass sd's
    99% upper bound is 1.72 mV against ≤ 0.5). The offset sentence is dropped. The pattern's pass-to-pass correlation
    is exactly 1.0 wherever it was computed, so the captures may repeat one reading (`V3R/tel.json`,
    `.items[item=TEL-Q]`).
  - **Whether the s ↔ s+16 ring draws less than spinning (E43, RL-X3).** Its sampler starved on all three cards
    (median 63–141 ms against the 60 ms rule), so its burst was dropped in all 18 passes (`V3R/rl.json`,
    `dropped_bursts`).
  - **aifoundry2's idle split at 73 °C (E44, IDLE-d).** Only two of the three short cycles cooled to 73 °C: minion
    11.07 [10.69–11.46], SRAM 1.99 [1.95–2.03], mesh 3.62 [3.42–3.83], unsensed 15.05 [14.56–15.54] W over those two
    (`V3R/idle.json`, `.items[item=IDLE-d]`).
  - **The idle law's leakage split and slow shape (E44, IDLE-L).** The overnight long-cooling passes never ran on any
    card, so aifoundry2's T_L, A80 and slope at 80 °C and aifoundry3's slope at 56 °C and offset are untested
    (`V3R/idle.json`, `.items[item=IDLE-L]`, `long_passes_used` empty).
  - Decided since the first reduction: RL-X4 (no verdict, FAIL), RL-f on all three cards (FAIL: at the low edge) and
    ABLB-2b's kernel clause ("the difference is the kernel" kept) were first reduced without inputs from E37, E38 and
    E46; the second reduction supplied them (AMENDMENTS.md, "Implementation note (26 Sep 2026, after the first
    reduction)"), and their values are in the Version 3 rows above.
