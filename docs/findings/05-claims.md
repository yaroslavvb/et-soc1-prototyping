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
older build (R3), so what the card runs may differ. Terms are defined in [README.md](README.md#terms).

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
| Board power resolution / refresh | 10 mW, refreshed every 133 ms | M | E5 | `tools/ettelem/ettelem.cpp`, `DM_CMD_GET_MODULE_POWER` |
| Firmware governor thresholds | 65 °C software, 65 W TDP; 75 °C / 75 W catastrophic | X | R3 (source at `353f20e`; the cards' trace strings match an older build) | `external/et-platform` at `353f20e`, `ServiceProcessorBL2/include/thermal_pwr_mgmt.h` and `bl2_pmic_controller.h` |

## Data-dependent power (all at 80 °C, 1,024 minions, 600 MHz, 9.18 TFLOPS)

Full table in [10-data-dependent-power.md](10-data-dependent-power.md); every value is
`DATA/horace3.json` → `patterns.<name>.p80`, with `p80_sd` beside it.

| Claim | Value | Kind | Source |
|---|---|---|---|
| Zeros | **38.29 W ± 0.03** (5 runs) | M | E9 |
| Ones | **46.73 W ± 0.07** (5 runs) | M | E9 |
| π everywhere | 46.96 W ± 0.02 | M | E9 |
| Random normal | **63.40 W ± 0.08** (5 runs, 5 different random matrices) | M | E9 |
| Random uniform [0,1) | 61.29 W ± 0.04 | M | E9 |
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
| Slope of board power under load, E5 load step (20 Sep, 75–87 °C, 600 MHz) | about **0.8 W/°C** board (0.80 from 5 s after launch, 0.76–0.78 from 1–3 s), 0.40 minion rail | M, F | E5 (`docs/reports/data/2026-09-20-power-aifoundry2/summary.json`, `thermal.series`, least squares) |
| Slope of board power under load, first uncontrolled Horace session (20 Sep, 22 runs at 79–90 °C; superseded by the two rows above) | 0.78 W/°C board, 0.38 minion rail | F | E7 |
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
| A different afternoon session, published model, nothing fitted on it | median 2%, worst 68% (the DFT pair), 5-minute run off by 0.2 °C | P | E17 afternoon |
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
| Equal flip power gives equal heating | ones on 1,024 cores (10.7 W) and random on 384 cores (10.2 W): 107–167 s against 119 s | M | E12 |

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
| Peak board power at 800 MHz on random data | 87.8 W, for an instant before the governor stepped down | M | E10 |
| The resulting speed gap, zeros vs random | **about 25%** | M | E10 |

## The DVFS loop and leakage suppression

`DATA2` means `docs/reports/data/2026-09-22-dvfs-aifoundry2/`; `DATA2/dvfs.json` holds the computed tables.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Governor thresholds | 65 °C software, 65 W TDP, checked once per ~133 ms management pass (the 10 ms is the sleep at the end of each pass) | X | R3 | `thermal_pwr_mgmt.h`, `mgmt_build_config.h` (`DM_TASK_DELAY_MS`) |
| The loop's power input is a **measurement**, not an activity estimate | `pmic_read_average_soc_power()` over I2C | X | R3 | `services/thermal_pwr_mgmt.c`, `update_module_soc_power()` |
| The loop has **no hysteresis** | in the `353f20e` source both guardband macros are defined and never used; the older governor the cards' logs point to does use the power guardband, and the thermal test has no dead band in either | X | R3 | `thermal_pwr_mgmt.c` lines 212–223; no other reference in the tree |
| Thermal branch has priority over the power branch | plain `if`, power branch unreachable above 65 °C | X | R3 | `check_power_throttle_conditions()` |
| Clock returns to the boot point when the master minion idles | — | X | R3 | `go_to_idle_state_and_update_pwr_status()` |
| Operating points | 600 MHz / 0.517 V, 700 / 0.568, 800 / 0.618 | M | E10 | `DATA/cold1/telemetry.jsonl.gz`, `mhz.minion` with `die_mv.minion` |
| Clock transitions observed | **36** (18 up, 18 down) in 7 cool-start runs | M | E10 | `DATA2/dvfs.json`, `transitions` |
| Down-steps by cause | 7 thermal-only, 4 thermal+power, 7 unattributed (reading ≤65 °C, 34–56 W), **0 power-only** | M | E10 | same, field `why` |
| Voltage moved with frequency in every transition | true | M | E10 | same, `mv0`/`mv1` |
| First clock change after a launch | 0.39–0.99 s | M | E10 | same, `transition_summary.first_change_s` |
| Thermal hunting on ones from a 64 °C die | 7 clock changes in 2.4 s, 800 MHz peaks 1.6 s apart, then 600 MHz | M | E10 | `DATA2/dvfs.json`, `traces` |
| Per-minion sleep and isolation exist in the open (Erbium) RTL | `pwr_ctrl_min_nsleepin` / `nsleepout` / `isolate` | X | R2 | `rtl/shire/neigh/neigh_top.v`, `neigh_top_pwrstub.v` |
| …and are tied off in the open configuration | `nsleepin='1`, `isolate='0` | X | R2 | `rtl/cpu_subsystem/cpu_subsystem_top.v`, with the comment "this ifce is not used" |
| …and no firmware line drives them | none | X | R3 | whole-tree search; only `PWR_CTRL` hits are eMMC bus voltage |
| **No array wake-up latency** after up to 27 ms idle | L1 0, L2 −11 (a slow no-idle baseline, not the idle), L3 0, DRAM +10.5 cycles (row closure) | M | E18 | `DATA2/wakeup/`, and `DATA2/dvfs.json` → `wakeup` |
| Idle board power after about 20.6 h with no workload (E18's 4.9 s probe aside) | **31.79 ± 0.04 W at 73.0 °C** | M | E19 | `DATA2/idle_20h.jsonl.gz` |
| …predicted by the model fitted a day earlier | 31.78 W, error **+0.01 W** | P | E17 → E19 | `DATA2/dvfs.json` → `idle_check` |
| Idle rails | minion 11.05 W, SRAM 2.00 W, mesh 3.64 W, 15.10 W on no sensor | M | E19 | same |
| Leakage share of an idle card at 80 °C | **64%** | F | E17 | `DATA2/dvfs.json` → `leak_fraction` |
| Leakage share of a random-data matmul at 80 °C | **36%** | F | E17 | same |
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
| aifoundry1's kernel module `srcversion` | `1383B256EB24A0A53F04CC7` against `47D26A305A0428B29FB7FC4` | M | E21 | `/sys/module/et_soc1/srcversion` on each machine |
| aifoundry1's cards | 2, both on the bus, **neither usable**: `Error unable to evaluate compatibility!` | M | E21 | reproduce with `lspci` and any `libDM.so` client |
| aifoundry3 launch temperature, strict session | **55.77 ± 0.18 °C** | M | E20 | `DATA3/horace3.json`, `thermal.model_T_at_launch` |
| aifoundry3 idle board power under those runs | 25.1 W | M | E20 | `DATA3/horace3.json`, `patterns.*.p_before` |
| Switching power, zeros / random normal, aifoundry3 | **1.89 W / 24.86 W** over idle (aifoundry2: 1.96 / 27.11) | M | E20 | `DATA3/cards.json`, `rows[*]` |
| aifoundry2 model applied to aifoundry3 unchanged | 1.38 W rms, 2.32 W worst, a consistent 8% overestimate | P | E17 → E20 | `DATA3/cards.json`, `model_error` |
| …after one scale factor | scale **0.924**, residual **0.20 W rms** over 1.9–25 W | F | E20 | `DATAC/cards-report.json`, `scale`, `rms_scaled` |
| …calibrating that factor on one run, predicting the other seven | 0.36 W rms median, 1.53 W worst; 0.27 W if calibrated on random data | P | E20 | `DATA3/transfer.json` |
| Die voltage, aifoundry3 vs aifoundry2 | 523 mV vs 518 mV at the same 600 MHz, so \(V^2f\) predicts 2% **more**, not 8% less | M | E20, E21 | `DATAC/config.json`, `DATA3/telemetry.jsonl.gz` |
| aifoundry2's idle law extrapolated onto aifoundry3, 7–14 °C below its 64–88 °C fitted range | **+0.73 W** mean error out of 25 W, over 50–57 °C | P | E17 → E20 | `DATA3/leakage_crosscard.json` |

## One contended global atomic (E22, E23)

`DATAH` means `docs/reports/data/2026-09-22-hotline-aifoundry2/`.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Host shire's share of a contended atomic | **1.004** of an even split; whole chip within 0.998–1.004 | M | E22 | `DATAH/hotline.json`, `fairness` |
| Same, line homed in shire 7, 15 or 31 | 1.001, 1.000, 1.000 | M | E22 | same |
| Cost of one contended atomic | **10.00 cycles**, about 60 M/s for the whole chip | M | E22 | `DATAH/hotline.json`, `placement` |
| Same work on 32 lines, one per shire | 0.31 cycles, 1,919 M/s — **32×** | M | E22 | same |
| Uncontended remote global-atomic round trip | 216 cycles | M | E22 | `DATAH/sweep.jsonl`, the one-remote-minion row |
| Host shire's own memory operations while hammered | **192–384 total**, 0.01–0.05% of its uncontended rate | M | E23 | `DATAH/hotline.json`, `local` |
| …and it does not grow with time | identical at 5, 10, 40 and 100 ms windows | M | E23 | `DATAH/hotline.json`, `context.window_independence` |
| Remote requesters needed to flip it | **24** (20 leaves the host at 98.9%) | M | E23 | `DATAH/hotline.json`, `requesters` |
| Pacing that restores the host | 10,000 cycles → host 54%, hammering shires 96% | M | E23 | `DATAH/hotline.json`, `pace` |
| Energy, contended vs spread | **23.6 vs 1.4 nJ per atomic**, 17× (first run; the E29 reruns give 19.8 [16.9–23.6] vs 1.16 [1.01–1.37] nJ, below: quote those) | M | E23 | `DATAH/power.json` |
| 1,024 minions stalled on a contended line | 1.41 W over idle | M | E23 | same |
| Chip-wide barrier | 4,997 cycles | M | E23, R4 | `nocbench --test barrier --scope chip` |
| A global atomic through the scratchpad self ID `0x7F` | kernel bus error | M | E22 | reproduce with `--home scpself:0` |
| The arbitration rule and its erratum | `l3_yield_priority` does not fix the same-address case | X | R1 | ET-SoC Errata 4.1 `RTLMIN-6207`, 4.2 `RTLMIN-6214`, both Postponed |
| Ivan's 6% | **not reproduced**; his code was not run | X | R11 | [17-hot-line.md](17-hot-line.md) |

## On-chip relay: shire-to-shire against main memory (E24, E25)

`DATAO` means `docs/reports/data/2026-09-22-onchip-aifoundry2/`.

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
| Cost of hop distance across the mesh | **no bandwidth cost**: 593 GB/s at the next shire by ID (3.5 mesh hops on average), 733 at 16 shire IDs (2.1 hops); energy per hop is in the E31/E32 rows | M | E25 | `DATAO/onchip.json`, `distance` |
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
| DRAM through the L1 write-back path, `fsw.ps` | 247 / 345 pJ/B at 26.6 GB/s | M | E26 | pattern `st_stream` |
| Leakage correction applied to the bursts | median 0.7 W, max 1.8 W over E26's bursts (E27, which the manual uses: 0.40 / 1.80 W on aifoundry2, 0.16 / 0.78 W on aifoundry3) | F | E26, E17 | `leak_correction_w` per entry |
| aifoundry3 / aifoundry2 over 56 entries | median **0.949**, range 0.87–1.01 | M | E26 | both card blocks |
| Dense fp32 matmul at 80 °C, rebuilt from the tables | 63.1 W (fixed 12.6 + leakage 23.3 + the flip model's 27.2 W) against 63.9 measured (E15; E9's random normal is 63.4); 57% static | D (a decomposition: the flip model was fitted to E9 and E12 on the same card, so this is a consistency check, not a prediction) | A15 §7 | `docs/energy-manual/07-composition.md` |
| The relay, priced from the byte tables with the rows it uses | DRAM 90–133 vs 105.7 [99.5–111.0]; own scratchpad 4.3–7.1 vs 3.99, a little below; next shire at 3.5 hops 5.1–11.2 vs 8.59 [7.78–9.21] | P (out of sample, made after the measurement) | A15 §7, E25, E29 | `DATAK`: `tload/dram`, `tstore/dram`, `l1fill/stride32`, `tstore/scp`, `wire/hop3`, `wire/hop4` |

## The comprehensive catalogue and the fine grain (E27, E28)

`DATAK` means `docs/reports/data/2026-09-23-energy-manual/catalogue.json`; every configuration is a key of
`cards.<host>.summary` with mean, sd, se, min, max and n over passes, and every burst is in `bursts.<host>`.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Instructions that execute in U-mode | 161; 13 trap (divide, square root, sine, reciprocal square root, 64-bit float conversion, the cycle CSR) | M | E27 | `workloads/enercat/enercat_modes.json`; the trap list in `docs/energy-manual/03a-every-instruction.md` |
| Pass-to-pass standard error | median 1.9%, 90th percentile 6.1% (aifoundry2) | M | E27 | `DATAK`, `se` of every entry |
| Cross-card ratio over 386 configurations | median **0.950**, 10–90% 0.906–0.987 | M | E27 | `DATAK`, `cross_card` |
| Cheapest and dearest instruction | `fence` 4.6 pJ; `amoaddg.d` 1,486 pJ (aifoundry2; 4.5 and 1,393 pJ pooled over both cards) | M | E27 | `DATAK`, `combined` |
| Energy of one mesh hop per byte (board) | **0.70 [0.64–0.75] pJ/B on zeros, 1.74 [1.67–1.81] on random data**, both cards, fitted over 1–8 hops (aifoundry2 alone 0.750 / 1.812; over 1–6 hops 0.89 / 2.29, in line with E31–E32) | F (straight line through 7 measured points) | E27 | `DATAK`, `cards.*.wire` |
| Data-dependent energy of the mesh (random − zeros), per bit per hop | 131 [129–133] fJ over 1–8 hops (174 / 155 on the two cards over 1–6): flips between flits plus ones carried, split in the E31/E32 rows | F | E27 | difference of the two slopes |
| Mesh rail alone, per hop | 1.29 pJ/B, fitted over 1–8 hops like the board figure above (over 1–6 hops the same points give 1.51; Heat per millimetre gives 1.50 on a loaded mesh and 1.1 on free links; quote those) | F | E27 | `04a-fine-grain.md`, "the mesh rail alone" |
| Filling a 64 B line from scratchpad into the L1 | 101 pJ zeros, 205 pJ random pooled over both cards (aifoundry2 211, aifoundry3 199 on random data); 1.6 and 3.2 pJ/B, about three quarters of the tensor load's 2.0 and 4.2 pJ/B | M (difference of strides) | E27 | `DATAK`, `combined`, `l1fill/stride32/*` against `l1fill/stride64/*` |
| DRAM row hit vs row miss | no difference within ±5 pJ/B | M | E28 | `DATAK`, `dramrow2/*` |
| L3 read by tensor load through the mesh | 7.9 / 19.7 pJ/B zeros / random at 1072 GB/s | M | E27 (mislabelled row experiment) | `DATAK`, `dramrow/stride8K/*` |
| Rail split, scalar and vector arithmetic | 79–82% minion rail, ~18% unmetered | M | E27 | `DATAK`, `rails_over_w` |
| Rail split, scratchpad six hops away | 49% mesh, 25% SRAM, 8% minions | M | E27 | same |
| Rail split, DRAM read | 70% on no metered rail | M | E27, E28 | same |
| SRAM rail at idle | 1.60 W at 67 °C, 2.63 W at 82 °C (aifoundry2); 1.90 W at 51 °C (aifoundry3) | M | E27 | `DATAK`, `sram_leakage.curve` |
| The rails' response to a step | first-order, τ ≈ 1 s; min and max are since reset | M | E27 | `telemetry.jsonl.gz` around any burst |
| Neighbourhoods reading the shire's scratchpad | 3.8–4.2 pJ/B | M | E27 | `DATAK`, `neigh/*` |

## Confidence bars, the reruns and the unmetered remainder (E29, E30)

`RERUNS` is `docs/reports/data/2026-09-23-energy-manual/reruns.json`; `UNMET` is `unmetered_fit.json` beside it.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Catalogue bars, half the range over 3 passes × 2 cards | median ±5.6%, 90th percentile ±11.5% | M | E29 | `DATAK`, `combined` |
| Relay through DRAM / next shire / own scratchpad | 105.7 [99.5–111.0] / 8.6 [7.8–9.2] / 3.99 pJ/B, n = 8 | M | E29 | `RERUNS`, `relay_pj_per_byte` |
| Contended hot line | 19.8 nJ [16.9–23.6], n = 7; spread over 32 lines 1.16 [1.01–1.37] | M | E29 | `RERUNS`, `hotline_nj_per_op` |
| Levels at 600 MHz: L1 / L2 / L3 / DRAM | 0.77 / 2.51 / 10.5 / 122 pJ/B, both cards, n = 6 | M | E29 | `RERUNS`, `levels_pj_per_byte` |
| Rings at 600 MHz: pair / shire / xshire1 | 0.67 / 2.08 / 14.9 pJ/B, n = 6 | M | E29 | `RERUNS`, `rings_pj_per_byte` |
| Cool-card reruns contaminated by the governor | 700–800 MHz in 5–25% of the samples of most bursts; the whole attempt was discarded | M | E29 | `docs/reports/data/2026-09-23-reruns-aifoundry2/`, `mhz.minion` |
| s ↔ s+16 rings starve the service processor | sample latency (six management commands) 22 → 150 ms; board reading held; energy read 45% low | M | E29 | `-aifoundry2-warm/rl-pass*/telemetry.jsonl.gz`, `took_ms` |
| Unmetered W = delivery loss + DRAM term | 0.196·minion + 0.050·SRAM + 0.286·NoC W + 73 pJ/B; rms 0.35 W (a2; 1.1 W on its DRAM configurations); 0.177, 0.064, 0.264, 68 (a3); the idle 15 W is not split | F (4 coefficients over 392 + 386 configuration means) | E30 | `UNMET`; `python3 tools/ettelem/fit_unmetered.py` reproduces it exactly |
| DDR rail droop per off-rail DRAM watt | 0.84 mV/W, rms 0.36 mV; idle 767 mV; heavy mesh and scratchpad traffic also droops it 1–1.7 mV | F | E30 | `UNMET`, `ddr_droop`; `tools/ettelem/fit_unmetered.py` gives 0.87 mV/W, within 3% (its busy and idle windows are its own) |
| Minion rail IR drop per watt | 0.068 mV/W | F | E30 | `UNMET`, `ddr_droop.minion_ir_drop_mv_per_w`; the script gives 0.070 (within 3%) |
| The PMIC meters three regulators; seven rails have no telemetry | minion, NoC, SRAM (w_out forwarded; v/a/w in and a_out read and dropped) | R | R13 | `pmic_controller.c`, `bl2_pmic_controller.h` |
| Moortec PVT: 35 temperature sensors, 125 voltage points, 35 process detectors (of 40 slots) | host sees averages; per-shire voltage in the DEBUG trace; PDs disabled | R | R13 | `bl2_pvt_controller.h`, `pvt_controller.c` |

## Heat per millimetre (E31, E32)

`WIRE` is `docs/reports/data/2026-09-24-wire-energy/wire.json`; `WREP` is `report.json` beside it. Loaded-mesh
coefficients are the second run's model (`model.v2`) over 1–6 hops; free-link numbers are `disjoint_flows.*.wsep_d1_4`.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| One mesh hop | **3.72 mm** (3.64–3.74); x 3.73, y 3.70 | A (estimate from the die plot) | R14 | `WREP`, `inputs.hop_mm`; `research/geometry/pitch.json` |
| A random bit per mm, free links, 0.485 V | **36.2 fJ** on the mesh rail (24.6 data + 11.7 fixed); 46.7 on board power (32.7 + 14.0) | M, F (slopes) | E32 | `WREP`, `headline["uncontended/noc_rail"]`, `["uncontended/board"]` |
| A random bit per mm, loaded mesh | **50.4 fJ** mesh rail (30.6 + 19.8); 72.9 board (46.1 + 26.8) | F (3-term model) | E32 | `WREP`, `headline["v2/noc_rail"]`, `["v2/board"]` |
| Per bit differing from the previous flit, per hop (*a*) | 98 [92–103] fJ mesh rail; 151 [139–162] board | F | E32 | `WIRE`, `model.v2.*.toggle_fj_per_bit_transition_hop` |
| Per one carried, per hop (*b*) | 129 [127–133] fJ mesh rail; 192 [180–205] board | F | E32 | `WIRE`, `model.v2.*.ones_fj_per_one_bit_hop` |
| The same from the first run's repeated image | *a* 95, *b* 131 fJ on the mesh rail | F | E31 | `WIRE`, `model.v1.noc_rail` |
| Ones from complements (¾ against ¼) | 132 [125–138] fJ per one per hop, mesh rail | M | E32 | `WIRE`, `complement_test.noc_pj_per_byte` |
| Contention over 1–4 hops, mesh rail | data 119 against 91 fJ per bit per hop; the rest 76 against 43 | M | E32 | `WIRE`, `disjoint_flows.noc_pj_per_byte.wu`, `.wsep_d1_4` |
| Link sharing in the all-pairs set | 0 / 22 / 32 / 55 / 72% of link-hops at 1 / 2 / 3 / 4 / 6 hops (XY routing) | M (from the recorded maps) | E32 | `WIRE`, `checks.link_sharing` |
| All ones against random, per hop | 7–9% more (both meters); 36–37% less in total at one hop | M | E32 | `WIRE`, `configs["wu/p1/hop*"]` against `["wu/p0.5/hop*"]` |
| 256 B blocks against 16–128 B | +0.41 pJ/B per hop (mesh rail), +0.76 (board): 54% and 69% of every bit flipping | M | E31 | `WIRE`, `checks.alt256` |
| Board coefficients without the leakage correction | 4–9% higher; mesh rail unchanged | M | E31, E32 | `WIRE`, `sensitivity.no_leak_correction` |
| Mesh rail data cost scaled to 0.9 V | 85–105 fJ per random bit·mm (× 3.44, constant C, full swing) | F, A (the scaling) | E32 | `WREP`, `scaled["0.9"]` |
| y-only three-hop pairs starve the meter on aifoundry2 | telemetry reads 0.8–1.6 s instead of 22 ms; 6 bursts dropped | M | E31 | `WIRE`, `dropped.aifoundry2` |
| A killed sampler poisons the management queue | every later opener crashes with `std::bad_function_call` until one `dev_mngt_service` call drains it | M | E32 | [14-card-behaviour.md](14-card-behaviour.md), "Traps" |
| Dally's figure | "~100fJ/b-mm on-chip": no voltage, process or data activity; CACM 2020 in a 14 nm paragraph; AHA 2023 beside "~0.5V" | X | R14 | `research/SYNTHESIS.md` §1d |
| Keckler et al. 2011, 40 nm, 0.9 V | 121 fJ per random bit·mm (310 pJ / 256 b / 10 mm) | X | R14 | same, §1e |
| A plain repeated 7 nm wire, 0.485 V | 12–24 fJ per random bit·mm (200–400 fF/mm) | A (first principles) | R14 | `research/lit/first-principles-estimate.md` |

## Ridge points (derived; no card time)

Peak compute divided by each level's measured bandwidth, at 600 MHz on 1,024 minions. Kind `D`: arithmetic on
measured numbers, not a new measurement. The bandwidths are the 2026-09-18 reports' (reproduced within 0.2% by the
2026-09-23 reruns on both cards); the energy balance points use the energy manual's data
(`docs/reports/data/2026-09-23-energy-manual/manual.json`). Recompute every row with `python3 scripts/ridge-points.py`.
Values are FLOP (int8: OP) per byte fetched, fp32 / fp16 / int8.

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Tensor peak per minion-cycle | **16 / 32 / 128** ops (9.83 TFLOP/s, 19.7 TFLOP/s, 78.6 TOP/s on 1,024 minions at 600 MHz) | X | Minion VPU Specification §2; matmul report | `scripts/ridge-points.py`, `PEAK` |
| Ridge, own shire (L2 or L2 scratchpad) | **4 / 8 / 32** at 4.0 B per minion-cycle (2.46 TB/s); 2 / 4 / 16 at the banks' 256 B per shire-cycle | D | memory-hierarchy streaming probes | `docs/reports/data/2026-09-18-memhier-aifoundry2/energy*/runs.jsonl`, configs `l2`, `scp-local` |
| Ridge, L3 or another shire's scratchpad | **10 / 20 / 80** at 0.96–0.98 TB/s | D | same, configs `l3`, `scp-remote`, 600 MHz launches only | same file, `implied_ghz` 0.59–0.61 |
| Ridge, DRAM | **130 / 259 / 1,036** at 76 GB/s | D | same, config `dram`; 76 GB/s on both cards in the 23 September reruns (the sparsity report's shorter probe read 72 on aifoundry3) | same file; `docs/reports/data/2026-09-18-sparsity-aifoundry3/tload-dram-all.jsonl` |
| Ridge, host over PCIe Gen4 x8 | **624 / 1,248 / 4,993** at 15.75 GB/s | A | datasheet §1; never measured | — |
| Intensity of one full-size TensorFMA | **4 / 8 / 16** per byte (2 KB of A and B per op) | D | PRM ch. 9 | `scripts/ridge-points.py`, `OP_BYTES` |
| Smallest DRAM-resident C block that is compute-bound | about **520 × 520** (fp32, fp16), **1,040 × 1,040** (int8) | D | H/e ≥ ridge, H the harmonic mean of the block's sides, e = bytes per element | the report's "What it takes to reach them" |
| Energy balance, fp32: FLOP per byte at which moving a byte costs as much energy as the arithmetic | L1 0.27, own shire 0.87, other shire 2.3, L3 3.6, DRAM **42** (random fp32 at 2.89 pJ per FLOP over idle) | D | energy manual §3.2 (tensor unit), §4.2 (levels) | `docs/reports/data/2026-09-23-energy-manual/manual.json` (`tensor.bars`, reruns) |

Two corrections to earlier reports came out of this, both verified in the raw data:

- The memory-hierarchy report's bandwidth column averages launches taken at 600–800 MHz. At 600 MHz the cycle
  counters give **2.45 TB/s** for L2 and **128 B per shire-cycle**, not the 2.80 TB/s and "about 144 B/cycle" printed
  there.
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
  62–80 °C.
- **Whether the taped-out ET-SoC-1 ever drives its sleep transistors.** The chip-level netlist is not in the
  open drop; the tie-off is a fact about the Erbium configuration, and the card only shows that nothing
  observable uses them.
- **Why aifoundry3's flashed TDP is 0 W**, and whether it was ever something else. The value was traced to
  `g_pmic_power_reg.module_tdp_level` and no further.
- **Whether the 8% switching-power gap between the two cards is silicon, package or board regulator.**
  Separating those needs a third working card, which aifoundry1 is not.
- **Per-flip energies outside the tensor unit and the mesh links** (E11–E17, E31–E32), and the split of the
  unsensed 15 W of idle. E30 attributes the unmetered part of what a workload adds above idle (delivery losses plus
  a DRAM term, fitted over configuration means) and meters DRAM by droop; the idle 12–15 W and the DRAM term's split
  below its regulator stay inferred.
- **Whether the heat-per-mm "ones" cost is resting-at-zero logic or precharged structures**, and how a hop's
  energy splits between router and wire (E31, E32). The mesh rail's meter gain has not been checked independently,
  and whether the links are low-swing, which the V² scaling assumes they are not, is unknown.
- **Whether the DRAM controller closes pages** or the row activation is merely small; E28 cannot tell.
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
- **Which firmware build the cards run.** Their trace strings match service-processor firmware older than
  et-platform commit `60b40c10f` (24 September 2024); the governor was read at `353f20e` (R3).
