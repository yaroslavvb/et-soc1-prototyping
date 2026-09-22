# Claim index: every number, and where it came from

If a number from this work turns up somewhere else — in a summary, a slide, another agent's answer — this is
where to check it. Each row gives the value, how it was obtained, the experiment or resource it came from, and
the file and field that hold the evidence.

**Kind:** `M` measured on the card · `S` simulated from RTL · `F` fitted to measurements · `P` predicted by a
model before it was measured · `X` external source · `A` assumption.

Paths are relative to the repository root. `DATA` means `docs/reports/data/2026-09-21-horace-aifoundry2/`,
`DATA2` means `docs/reports/data/2026-09-22-dvfs-aifoundry2/`, `DATA3` means
`docs/reports/data/2026-09-22-horace-aifoundry3/` and `DATAC` means `docs/reports/data/2026-09-22-cards/`.

---

## The card and its operating point

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Minion core voltage under load, on die | **516–518 mV** | M | E9 | `DATA/strict/telemetry.jsonl.gz`, field `die_mv.minion`, every sample of every run |
| Minion rail set point | 520 mV | M | E9 | same file, `reg_mv.minion` |
| Minion clock under load | **600 MHz** | M | E9, E12, E15, E16 | same file, `mhz.minion`; constant in every sample of every session above 65 °C |
| The other operating points | 700 MHz at 570 mV, **800 MHz at 618–620 mV** | M | E10 | `DATA/cold1/telemetry.jsonl.gz`, `mhz.minion` with `die_mv.minion` |
| Minions used by these workloads | 1,024 (32 shires × 32) of 1,088 on the chip | M | E9 | `DATA/strict/runs.jsonl`, field `minions` |
| Cycles per 16×16×16 fp32 `TensorFMA` | **546.001**, identical for every data pattern | M | E9 | `DATA/strict/runs.jsonl`, `cycles_per_op` |
| Same, fp16 / int8 | 546 / 318 | M | E15, R4 | `DATA/ablation/runs.jsonl` |
| Arithmetic rate at 600 MHz | **9.18 TFLOPS** (4.59 × 10¹² multiply-adds per second) | M | E9 | `DATA/horace3.json`, `patterns.*.tflops` |
| Idle board power at 80 °C | **36.3 W** | M | E9 | `DATA/horace3.json`, `patterns.*.p_before` |
| Idle board power at 62 °C, after a night idle | **26.7 W** | M | E10 | `DATA/cold1/telemetry.jsonl.gz` before the first launch |
| Die temperature resolution | whole degrees (one number, the mean of 34 minion-shire sensors) | M | E5 | any `telemetry.jsonl.gz`, `temp_c.minshire[0]` |
| Board power resolution / refresh | 10 mW, refreshed every 133 ms | M | E5 | `tools/ettelem/ettelem.cpp`, `DM_CMD_GET_MODULE_POWER` |
| Firmware governor thresholds | 65 °C software, 65 W TDP; 75 °C / 75 W catastrophic | X | R3 | `external/et-platform` at `353f20e`, `ServiceProcessorBL2/include/thermal_pwr_mgmt.h` and `bl2_pmic_controller.h` |

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
| Heating per 10¹² FLOPs: zeros / ones / random | **1.3 / 26.8 / 75.9 m°C** | M | E9 (`mC_per_tflop_fit`) |
| Board energy per FLOP: zeros / ones / random | 4.17 / 5.21 / 7.27 pJ | M | E9 (`pj_per_flop`) |
| Same, over the idle card | **0.22 / 1.26 / 3.31 pJ** | M | E9 (`pj_per_flop_over_idle`) |
| −0.0 is not gated: costs like ones | 46.71 W against 38.23 W for +0.0 | M | E15 | 
| Rails: random − zeros, late in the run | 21.5 W of 29.6 W on the minion rail, 1.0 W on SRAM + mesh, ~7 W on no rail (regulator loss) | M | E9 (`rails_late`) |

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
| Leakage slope measured directly under load, 09-20 | 0.78 W/°C board, 0.38 minion rail | M | E5, E7 |
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
| Sustainable switching power before runaway | **about 3 W** at 82 °C | F | E17, corroborated by E12 |

## Predictions made before measurement

| Claim | Value | Kind | Source |
|---|---|---|---|
| 14 structured matrices, board power predicted from their tiles | **0.92 W rms**, 11 of 14 within 0.6 W | P→M | E14 → E15; `DATA/structured_predictions_before.json` (`made_at` 2026-09-21T13:08:33) vs `DATA/ablation.json` |
| Worst structured miss (DFT cos/sin pair) | predicted 47.0 W, measured 49.8 W | P→M | same |
| Six earlier patterns predicted from the 09-20 data | 1.3 W rms for the two model forms that split the toggle count; 2.8 and 4.2 W for the two that do not | P→M | `DATA/predictions_before.json` (06:50:12) vs E9 |

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
| Integer spin loop on 1,024 minions | +1.46 W over idle, **1.4 mW per core**, 8.1 pJ per instruction | M | E15 |
| Energy per multiply-add over idle: int8 / fp16 / fp32, random data | **0.32 / 2.70 / 6.02 pJ** | M | E15 |
| Power is linear in active cores | 25.6 mW per minion at 256, 512 and 768; 27.0 at 1,024 | M | E15 |
| TensorLoad from L2 SRAM | +6.2 W at 2.4 TB/s → 0.3 pJ per bit | M | E15 |
| TensorLoad from LPDDR4x | +10.7 W at 75 GB/s → **18 pJ per bit** end to end | M | E15 |
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
| Governor thresholds | 65 °C software, 65 W TDP, checked every 10 ms | X | R3 | `thermal_pwr_mgmt.h`, `mgmt_build_config.h` (`DM_TASK_DELAY_MS`) |
| The loop's power input is a **measurement**, not an activity estimate | `pmic_read_average_soc_power()` over I2C | X | R3 | `services/thermal_pwr_mgmt.c`, `update_module_soc_power()` |
| The loop has **no hysteresis** | both guardband macros defined and never used | X | R3 | `thermal_pwr_mgmt.c` lines 212–223; no other reference in the tree |
| Thermal branch has priority over the power branch | plain `if`, power branch unreachable above 65 °C | X | R3 | `check_power_throttle_conditions()` |
| Clock returns to the boot point when the master minion idles | — | X | R3 | `go_to_idle_state_and_update_pwr_status()` |
| Operating points | 600 MHz / 0.517 V, 700 / 0.568, 800 / 0.618 | M | E10 | `DATA/cold1/telemetry.jsonl.gz`, `mhz.minion` with `die_mv.minion` |
| Clock transitions observed | **36** (18 up, 18 down) in 7 cool-start runs | M | E10 | `DATA2/dvfs.json`, `transitions` |
| Down-steps by cause | 7 thermal-only, 4 thermal+power, 7 kernel-boundary, **0 power-only** | M | E10 | same, field `why` |
| Voltage moved with frequency in every transition | true | M | E10 | same, `mv0`/`mv1` |
| First clock change after a launch | 0.39–0.99 s | M | E10 | same, `transition_summary.first_change_s` |
| Limit-cycle period on constant data | about 2 s | M | E10 | `DATA2/dvfs.json`, `traces` |
| Per-minion sleep and isolation exist in the RTL | `pwr_ctrl_min_nsleepin` / `nsleepout` / `isolate` | X | R2 | `rtl/shire/neigh/neigh_top.v`, `neigh_top_pwrstub.v` |
| …and are tied off in the open configuration | `nsleepin='1`, `isolate='0` | X | R2 | `rtl/cpu_subsystem/cpu_subsystem_top.v`, with the comment "this ifce is not used" |
| …and no firmware line drives them | none | X | R3 | whole-tree search; only `PWR_CTRL` hits are eMMC bus voltage |
| **No array wake-up latency** after up to 27 ms idle | L1 0, L2 −11, L3 0, DRAM +10 cycles | M | E18 | `DATA2/wakeup/`, and `DATA2/dvfs.json` → `wakeup` |
| Idle board power after 20.4 h | **31.79 ± 0.04 W at 73.0 °C** | M | E19 | `DATA2/idle_20h.jsonl.gz` |
| …predicted by the model fitted a day earlier | 31.78 W, error **+0.01 W** | P | E17 → E19 | `DATA2/dvfs.json` → `idle_check` |
| Idle rails | minion 11.05 W, SRAM 2.00 W, mesh 3.64 W, 15.10 W on no sensor | M | E19 | same |
| Leakage share of an idle card at 80 °C | **64%** | F | E17 | `DATA2/dvfs.json` → `leak_fraction` |
| Leakage share of a random-data matmul at 80 °C | **36%** | F | E17 | same |
| Kanter's reference range for leakage | 5–30%, ~20% common | X | R9 | the brief at R9 |

## The three machines (E20, E21)

| Claim | Value | Kind | Source | Verify at |
|---|---|---|---|---|
| Static TDP the **service processor** reports | **65 W on aifoundry2, 0 W on aifoundry3** | M | E21 | `DATAC/config.json`; reproduce with `ettelem config` |
| Static TDP the **driver** reports | 65 W on all three machines | M | E21 | `DATAC/driver_config.json`; reproduce with `tools/etcfg` |
| Consequence in the firmware | at a TDP of 0 the step-down test `avg > tdp` is always true and the step-up test `avg < tdp` never is | X | R3 | `ServiceProcessorBL2/services/thermal_pwr_mgmt.c`, `check_power_throttle_conditions()` |
| aifoundry3's governor log, one 8 KB window | **26 throttle-down events, 0 throttle-up**, each printing `tdp level: 0` | M | E21 | `DATAC/sptrace-aifoundry3.bin`, readable with `strings` |
| Power state the firmware reports | `max_power` on aifoundry3 at 23 W, `managed_power` on aifoundry2 | M | E21 | `DATAC/config.json`; `get_power_state()` returns `MAX_POWER` iff power > TDP |
| Minion clock ever seen above 600 MHz | aifoundry2 yes (700, 800); **aifoundry3 no** | M | E10, E20, E21 | `DATA/cold1/telemetry.jsonl.gz`; `DATA3/telemetry.jsonl.gz`, `mhz.minion` constant at 600 |
| aifoundry1's kernel module `srcversion` | `1383B256EB24A0A53F04CC7` against `47D26A305A0428B29FB7FC4` | M | E21 | `/sys/module/et_soc1/srcversion` on each machine |
| aifoundry1's cards | 2, both on the bus, **neither usable**: `Error unable to evaluate compatibility!` | M | E21 | reproduce with `lspci` and any `libDM.so` client |
| aifoundry3 launch temperature, strict session | **55.77 ± 0.18 °C** | M | E20 | `DATA3/horace3.json`, `thermal.model_T_at_launch` |
| aifoundry3 idle board power under those runs | 25.1 W | M | E20 | `DATA3/horace3.json`, `patterns.*.p_before` |
| Switching power, zeros / random normal, aifoundry3 | **1.89 W / 24.86 W** over idle (aifoundry2: 1.96 / 27.11) | M | E20 | `DATA3/cards.json`, `rows[*]` |
| aifoundry2 model applied to aifoundry3 unchanged | 1.38 W rms, 2.32 W worst, a consistent 8% overestimate | P | E17 → E20 | `DATA3/cards.json`, `model_error` |
| …after one scale factor | scale **0.924**, residual **0.20 W rms** over 1.9–25 W | F | E20 | `DATAC/cards-report.json`, `scale`, `rms_scaled` |
| …calibrating that factor on one run, predicting the other seven | 0.36 W rms median, 1.53 W worst; 0.27 W if calibrated on random data | P | E20 | `DATA3/transfer.json` |
| Die voltage, aifoundry3 vs aifoundry2 | 523 mV vs 518 mV at the same 600 MHz, so \(V^2f\) predicts 2% **more**, not 8% less | M | E20, E21 | `DATAC/config.json`, `DATA3/telemetry.jsonl.gz` |
| aifoundry2's idle law extrapolated onto aifoundry3, 25 °C below its fitted range | **+0.73 W** mean error out of 25 W, over 50–57 °C | P | E17 → E20 | `DATA3/leakage_crosscard.json` |

## External numbers (not measured here)

| Claim | Value | Kind | Source |
|---|---|---|---|
| A100: transistors, die, process, TDP | 54.2 B, 826 mm², TSMC 7 nm, 400 W SXM4 | X | R7 |
| A100: HBM2e bandwidth | 1,555 GB/s | X | R7 |
| A100: maximum boost clock | 1,410 MHz | X | R7 |
| A100 matmul measured by Horace He | 257 TFLOPS random / 295 TFLOPS zeros, 330 W limit, 88 W idle | X | R8 |
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
- **aifoundry3's thermal network.** Its heatsink is visibly faster than aifoundry2's, and no heat-then-cool
  characterisation was run on it. Do not apply aifoundry2's 1.47 °C/W to it.
- ~~**Whether the governor's power branch behaves as written.**~~ **Established on 2026-09-22 (E21):** it
  fires exactly as written, continuously, on aifoundry3, on a die 15 °C below the thermal threshold.
