# Heat placement, research task 2: what the host can observe, and what is known spatially

Scope: read-only; no card was touched. Sources and the short names used in the citations:

- `PAGES` = `/home/yaroslavvb/claude/et-soc1-pages` (branch `pages-v3b`, HEAD `305fe0d`).
- `ETP` = `/home/yaroslavvb/claude/et-soc1-prototyping/external/et-platform`, checked out at `836a4ab60`.
  `SPBL2` = `ETP/device-bootloaders/src/ServiceProcessorBL2`. The two files that matter here,
  `services/thermal_pwr_mgmt.c` and `driver/pvt_controller.c`, are **byte-identical between `353f20e` (the source
  the findings quote) and this checkout**: `git diff 353f20e HEAD` on both files is empty. So line numbers below hold
  for both.
- `CARDFW` = `git show cafe03fc3^:device-bootloaders/src/ServiceProcessorBL2/...`. This is the closest source to the
  cards' firmware, release 1.3.1 with BL2 0.20.0, per `PAGES/docs/reports/data/2026-09-25-claims-v3/firmware.md:5-17`.
  I extracted its `thermal_pwr_mgmt.c` to `heatplace/tpm-may2024.c`, and the `CARDFW …:NNN` line numbers refer to
  that copy. Between `cafe03fc3^` and `353f20e`, `pvt_controller.c` and `bl2_pvt_controller.h` differ only by a
  licence-header change (`git diff --stat`: +4 and −14 lines), so the same functions sit about 5 lines lower in `CARDFW`.
- `PRM` = *ET Programmer's Reference Manual* (PDF page numbers, checked with `pdftotext -f N -l N`). `DS` = *ET
  Preliminary Datasheet Rev 1.0*. Both are in `et-soc1-prototyping/external/et-man/`.
- "Computed here" marks a number I derived in this task from committed data or code. The script or method is given
  in each case, and none of these numbers was published before.

---

## 0. Answers in brief

1. **The thermal trigger is the average of the 34 minion-shire sensors, not any single sensor.** This holds in the
   cards' build (`CARDFW thermal_pwr_mgmt.c:656-680`) and in `353f20e` (`SPBL2/services/thermal_pwr_mgmt.c:695-699,
   866, 884`). The average is the integer mean of 34 readings, each already truncated to whole °C
   (`SPBL2/driver/pvt_controller.c:567-585, 1274-1301`). The test is `mean > 65`, with the threshold at
   `include/thermal_pwr_mgmt.h:41`. No code path reads a single shire's temperature for DVFS. A second trigger does
   exist: a PMIC over-temperature interrupt at a 75 °C set point moves the governor to `THERMAL_SAFE`
   (`CARDFW thermal_pwr_mgmt.c:2484-2486`; `SPBL2/driver/pmic_controller.c:505-506`;
   `SPBL2/include/bl2_pmic_controller.h:281`). That interrupt is the PMIC's own "system temperature" register
   (`pmic_controller.c:725-741`), not the die sensors, and which physical sensor it reads is not established.
2. **The host reads the exact number the governor tests.** `ettelem sample` `temp_c.minshire[0]` comes from the same
   integer mean (`thermal_pwr_mgmt.c:747-757` → `pvt_controller.c:1303-1340`). So "time until DVFS kicks in" can be
   read on every card as the first busy sample with `minshire[0] ≥ 66`, even on aifoundry3, whose clock cannot move
   (§1).
3. **The stock firmware gives no per-shire temperature.** The host gets the following spatial scraps (§3):
   - windowed **peak-hold max and min** over the 34 sensors, which say how hot the hottest sensor got and how cool
     the coolest one stayed, but not where either one is;
   - the **I/O shire's own sensor**, one fixed location in the non-compute corner of the grid. It reads +0/+1 °C
     against the mean at idle and −1/0 °C under an all-shire load (computed here);
   - **per-shire voltages** in the DEBUG trace, which carry current, not temperature. A leakage-based temperature
     proxy from them would sit about 1,000× below their 1 mV resolution (computed here).
4. **Nothing spatial has been measured about heat spreading on this chip.** The only thermal model is lumped: six RC
   stages, 1.47 °C/W, one card in one chassis (`PAGES/docs/findings/11-thermal-model.md:29-31, 134-135`). Every
   earlier reduced-core run spread the cores over all 32 shires (`PAGES/tools/ettelem/run_horace_long.sh:63`). The one
   spatial fact on record: under an all-shire load the hottest sensor rises 2–4 °C above the mean (§4.4).
5. **Placement is easy.** Use `--shires <32-bit mask>` on `sparsity_host` (TensorFMA) or `enercat_host`, plus
   `--per-shire N` or `--minions <mask>`. A shire of 32 minions running fp32 random-data TensorFMA adds about 0.85 W
   (§5). The candidate groups are in §6. In the die frame, three physical grid corners hold compute shires S0, S11
   and S31. The fourth corner is the I/O or PCIe shire.

---

## 1. What the governor reads (the "average or one sensor" question, from source)

| Fact | Source |
|---|---|
| Each sensor's value is converted as `(57400 + 249400·code/4096 − 124700)/1000` in C integer arithmetic, so every per-shire value is truncated to whole °C before any averaging. | `SPBL2/driver/pvt_controller.c:567-585`; constants in `SPBL2/include/bl2_pvt_controller.h:157,162,167` |
| `pvt_get_minion_avg_temperature()` returns the integer mean over `PVTC_MINION_SHIRE_NUM` = 34 sensors, skipping only faulted samples. The 34 are the 32 compute shires, the master and the spare. | `pvt_controller.c:1274-1301`; `bl2_pvt_controller.h:75`; the brief's HTML, `PAGES/docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:786` |
| **Cards' build.** On every pass, `update_module_current_temperature()` takes that mean. If `mean > sw_temperature_c` (65) and the state is below `THERMAL_DOWN`, it logs `"Thermal throttle down event, current temperature: %u, threshold: %d"` and enters `THERMAL_DOWN`. | `CARDFW thermal_pwr_mgmt.c:652-680`; threshold defined at `CARDFW include/thermal_pwr_mgmt.h:46` |
| **Cards' build.** The thermal loop steps the operating point down, sleeps `DELTA_TEMP_UPDATE_PERIOD` = 1,000 ms, re-reads the **mean**, and repeats while `mean > 65`. It then logs `"Thermal idle state event, current temperature %u, threshold %u"`. | `CARDFW thermal_pwr_mgmt.c:2308-2383`; `CARDFW include/thermal_pwr_mgmt.h:87` |
| **`353f20e`.** `check_power_throttle_conditions()` tests `g_pmic_power_reg.soc_temperature > 65`, and that variable is set only from the mean. | `thermal_pwr_mgmt.c:695-699` (per pass), `:754` (host query), `:864-925` (governor) |
| **The host's query returns the same mean.** `minshire_avg` is the mean, `minshire_high` and `minshire_low` are the max and min of the per-sensor peak-hold registers, and the I/O shire's sensor is reported separately. `pmic_sys` is the mean again. | `thermal_pwr_mgmt.c:733-769` |
| **A catastrophic path exists.** The PMIC temperature alarm is set to 75 at init. A PMIC OV_TEMP interrupt sets `POWER_THROTTLE_STATE_THERMAL_SAFE`. The PMIC's temperature is the "System Temperature register of PMIC", not the Moortec sensors. | `pmic_controller.c:503-506, 725-748, 1311-1323`; `bl2_pmic_controller.h:278-281`; `CARDFW thermal_pwr_mgmt.c:2480-2497` |
| **The host can change the threshold.** `DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS` writes `sw_temperature_c` with no bounds check. This is a card-configuration change, which the lab reserves for the admin. | `SPBL2/services/thermal_power_monitor.c:977-981, 493-501`; `thermal_pwr_mgmt.c:638-643`; `PAGES/docs/findings/14-card-behaviour.md:211` |

The empirical side is consistent with a mean-based trigger, but no test separated mean from max:

- In E10, aifoundry2 hunted around a whole-degree mean of 65/66 °C (`PAGES/docs/findings/16-dvfs-and-leakage.md:72-77`).
- The first clock change comes 0.39–0.99 s after a launch (`16-dvfs-and-leakage.md:88-91`).
- Computed here: in the superseded 23 September reruns on aifoundry2 (`PAGES/docs/reports/data/2026-09-23-reruns-aifoundry2/*/telemetry.jsonl.gz`),
  the clock stayed at 700–800 MHz for up to 0.7 s while the host read a mean of 66 °C. That is 49–106 such samples
  per pass, in stretches of at most 0.7 s: the governor's lag, not a contradiction.
- No committed telemetry has a peak-hold rise at a clock above 600 MHz. I scanned every `*.jsonl*` under
  `docs/reports/data`. The E10 cold-start telemetry was committed compacted, with no low or high field
  (`2026-09-21-horace-aifoundry2/cold1/telemetry.jsonl.gz`). So no data shows directly that a single hot sensor above
  65 °C failed to trigger. The source settles the question; the data neither confirms nor contradicts it.

What this means for which cards can show the onset:

| Card | Config | Can the clock show DVFS onset? | Source |
|---|---|---|---|
| aifoundry2 | TDP 65 W, threshold 65 °C, 600/700/800 MHz; idles 73–80 °C when warm, 62–63 °C after a night | Only from a die below 65 °C. Warm, it already sits at 600 MHz. | `14-card-behaviour.md:44-46, 150-153`; `tel.json` TEL-G a2 config |
| aifoundry3 | TDP 0 W from a boot service, clock pinned at 600 MHz, idles 55–57 °C | **No**: the clock never moves. Use the mean crossing 65 °C as the proxy. | `14-card-behaviour.md:150-153, 166-176` |
| aifoundry1 card 1 | firmware 1.2.0, TDP 65 W, threshold 65 °C, idles 57–62 °C at 600 MHz, peaked about 71 °C under smoke tests | Yes: it idles below the threshold. Its 1.2.0 governor source has not been read. | `14-card-behaviour.md:147-154`; `tel.json` TEL-G a1c1 `config_seen` |
| aifoundry1 card 0 | overheats (98–117 °C) | Not usable | `14-card-behaviour.md:197-203` |

---

## 2. What the host can read during a placement run

`ettelem sample` issues six management commands per sample, about 22 ms in total, and runs at 10 Hz by default.
The management node allows one opener at a time, so start the sampler once and leave it running
(`14-card-behaviour.md:89, 97-98`; `PAGES/tools/ettelem/ettelem.cpp:3-19`).

The service processor (SP) runs one pass every 133.2 ms on aifoundry2, 134.8 ms on aifoundry1 card 1 and
224.1–224.5 ms on aifoundry3. A 10 Hz ettelem adds 26.6 ms to aifoundry2's pass (`PAGES/docs/findings/03-experiments.md:1232-1236`).

| Field (ettelem JSON) | Command | Spatial content | Resolution and caveat | Source |
|---|---|---|---|---|
| `temp_c.minshire[0]` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | mean of 34 sensors = **the governor's input** | whole °C; sub-degree by step timing (≈0.03 °C on repeated runs) | `ettelem.cpp:136,160-161`; `14-card-behaviour.md:85, 103-112` |
| `temp_c.minshire[1]`, `[2]` | same | **min and max over the 34 sensors** of each sensor's hardware peak-hold since the last stats reset; anonymous | whole °C; single hardware samples, so noise can add | `pvt_controller.c:618-643, 1303-1340`; brief HTML `:832` |
| `temp_c.ioshire` [cur, low, high] | same | **one fixed sensor** (TS34, I/O shire) with its own peak-hold | whole °C | `thermal_pwr_mgmt.c:758-768`; `ettelem.cpp:160-161` |
| `temp_c.pmic` | same | = the mean (not a PMIC sensor) | – | `thermal_pwr_mgmt.c:737-745`; `05-claims.md:37` |
| `sp.minion_c` [avg, min, max] | `DM_CMD_GET_SP_STATS` | the SP's statistics of the mean since reset; avg is a 5-sample CMA | whole °C | `thermal_pwr_mgmt.c:695-705, 238, 251-262` |
| `sp.system_c` | same | always 0 (TODO in firmware) | – | `thermal_pwr_mgmt.c:703-704`; brief HTML `:830` |
| `mhz.minion`, `sp.minion_mhz` [avg, min, max] | `DM_CMD_GET_ASIC_FREQUENCIES`, SP stats | chip-wide clock, "the only reliable way to catch the governor" | 10 Hz samples | `ettelem.cpp:170`; `14-card-behaviour.md:87` |
| launch-implied GHz = `cycles_max / wall_s` | host output (`sparsity_host` runs.jsonl, `enercat_host` ENERCAT line) | chip-wide clock, averaged per launch (≈0.4–0.5 s) | exact cycles | e.g. `2026-09-21-horace-aifoundry2/cold1/runs.jsonl` (cycles_max 292,948,606 in 0.4887 s = 0.599 GHz, computed here); catalogue `implied_ghz_min/max` fields in `2026-09-23-energy-manual/catalogue.json` `bursts` |
| `board_w` | `DM_CMD_GET_MODULE_POWER` | none | 10 mW; refreshed once per SP pass | `05-claims.md:42` |
| `sp.minion_w`, `sram_w`, `noc_w` | SP stats | none | the PMIC's running average, τ ≈ 1.15–1.22 s | `14-card-behaviour.md:84`; `19-observability-and-the-unmetered.md:17-20` |
| `die_mv.*` | `DM_CMD_GET_ASIC_VOLTAGE` | PVT averages across shires | 1 mV; the minion rail sags 0.08 mV per W (a2, a3), 0.055 (a1c1) | `PAGES/docs/research/power-telemetry.md:138`; power-temperature HTML `:356-358` |
| SP trace: governor lines | `ettelem sptrace` | thermal lines print the **mean** and the threshold; power lines print "current pwr … tdp level" | 4 KB ring. The V3 check found **no** governor line on aifoundry2 (≥68 °C) or aifoundry3 in any pass, so the trace cannot time the onset reliably. | `CARDFW thermal_pwr_mgmt.c:674, 2372`; `thermal_pwr_mgmt.c:890, 903, 915`; `tel.json` `.items[TEL-G]` (`down_lines` 0, `governor_lines` 0) |
| SP trace at DEBUG: `MS nn Voltage [mV]: VDD_MNN …` | `ettelem loglevel debug` + `sptrace` | **per-shire** minion, SRAM and NoC voltages (now, low, high) | 1 mV; the 4 KB dump holds all 34 shires only when it catches a whole pass (22 of 27 dumps in the V3 check) | `pvt_controller.c:25-55`; `PAGES/tools/ettelem/parse_sptrace_voltage.py:1-30`; power-temperature HTML `:380` |
| SP stats trace (SPST) | `dev_mngt_service -t SPST:extract` | per pass, `op_stats_t` holds temperature (the mean's CMA, min and max), power, voltage and frequency for minion, SRAM, NoC and system | 1 MB ring of 152-byte records: 6,898 records, ≈15.3 min at 133.2 ms (computed here) | `ETP/et-trace/include/et-trace/layout.h:466-491`; `SPBL2/rtos_task/dm_task.c:301-317`; `PAGES/tools/claims-v3/tel/tel_util.py:15-20, 29-30` |

Resets. `ettelem sample --reset-ms R` sends `DM_CMD_SET_STATS_RUN_CONTROL` with `RESET_COUNTER`. That call reaches
`Thermal_Pwr_Mgmt_Init_OP_Stats()`, which calls `pvt_hilo_reset()` and so clears the peak-hold registers of all 35
temperature sensors, the I/O shire's included. The source path is `ettelem.cpp:59-67` →
`SPBL2/services/performance.c:572-575` → `thermal_pwr_mgmt.c:2805-2828` → `pvt_controller.c:1029-1040, 1071-1081`,
and the same path exists in the cards' build (`CARDFW performance.c:578-581`, `thermal_pwr_mgmt.c:2986`).

On the cards, the reset clears the peak-hold (`tel.json` TEL-R `R1_reset_resets_peak_hold: true`). Two side effects:

- The reset also restarts the rails' running average, with f(1 s) = 0.93 (`05-claims.md:441`).
- In the cards' build, the power branch's exit test reads that average (`firmware.md:37-39`).

So keep board power under 65 W, or do not reset during an onset measurement.

The governor also resets the clock to the boot point when the master minion goes idle. Only back-to-back launches keep
the DVFS state (`16-dvfs-and-leakage.md:63-65`).

---

## 3. Is there any per-shire temperature signal the host can read?

### 3.1 No direct path in the stock firmware

- **The firmware can read each shire** (`pvt_get_min_shire_ts_sample`, `pvt_controller.c:645-657`), but every host
  command reduces the readings to the mean, max, min and the I/O sensor (`thermal_pwr_mgmt.c:733-769`).
- **The per-shire DEBUG temperature print is unreachable.** The print `"MS %2d Temp [C]: %d [%d, %d]"` exists
  (`pvt_controller.c:1183-1214`). It is reached only through `pvt_print_temperature_sampled_values()` and `pvt_print_all()`
  (`:1256-1272, 1380-1391`), which **nothing calls** in this checkout or in `cafe03fc3^` (`git grep`).
  `pvt_get_and_print()` (`:1573`) has no caller either. In the V3 check the DEBUG dumps held **0** `Temp [C]` lines
  on every card (`tel.json` TEL-Q `captures.*.temp_lines`).
- **The debug path cannot reach the sensors.** `DM_CMD_MDI_READ_MEM` reads only firmware data and stack ranges,
  through a minion hart (`SPBL2/services/minion_debug.c:601-622, 174-183`).
- **Neither kernels nor the host can reach the sensors.** The PVT register regions are accessible to the Service
  Processor only, not to Minion cores, Maxion cores, the peripheral unit or PCIe (PRM Table 15-37, p. 400; addresses
  in PRM Table 1-6, p. 18, `0x00_5400_0000 + n·0x1_0000`).
- **No DM command returns a spatial temperature.** `ETP`'s `DM_CMD_*` enum has no such command.
  `DM_CMD_GET_MODULE_MAX_TEMPERATURE` returns `g_soc_power_reg.max_temp` (`thermal_pwr_mgmt.c:1380-1383`), and
  nothing in the tree assigns that variable (grep).
- **The process detectors are configured with measurement disabled** (`19-observability-and-the-unmetered.md:61-63`).

### 3.2 Partial spatial signals available today

**(a) Windowed hot-spot and cold-spot magnitude.** Reset the stats every R ms, for example with `--reset-ms 1000`.
Then `minshire[2]` is the hottest sensor's maximum within the window and `minshire[1]` the coolest sensor's minimum.
Both are whole degrees, and neither says which shire.

Measured under an all-shire 7 s random-data burst: at each rise the high sat 2–4 °C above the mean, 3 or 4 °C in 68%
(aifoundry2), 61% (aifoundry3) and 83% (aifoundry1 card 1) of rises. It ended load windows 2–3 °C above the SP's
maximum of the mean, and idle windows 1–2 °C above it. The low sat 1–2 °C under the minimum
(`05-claims.md:442`; `tel.json` `.items[TEL-R].per_card.*.passes[].windows[]` `rise_excess`,
`end_high_minus_spmax`, `end_low_minus_spmin`).

For a placement run, (high − mean) per window measures how concentrated the heat is. A concentrated block should lift
it above the 2–4 °C of a uniform load, and the noise floor is about 1–2 °C.

**(b) The I/O shire's sensor as a fixed probe.** TS34 is read individually. The I/O shire sits in the non-compute
corner: at mesh (0,4) or (0,5), which one is uncertain (brief HTML `:786`; heat-per-mm HTML `:1127`).

Computed here, from the three 20 September aifoundry2 logs (`2026-09-20-power-aifoundry2/{thermal,horace,horace2}-telemetry.jsonl`,
`ioshire[0] − minshire[0]`):

| Log | Idle (board < 40 W): 0 / +1 | All-shire load (board > 50 W): −1 / 0 / +1 |
|---|---|---|
| thermal | 245 / 702 samples | 247 / 316 / 2 samples |
| horace | 50 / 74 | 28 / 182 / 3 |
| horace2 | 571 / 396 | 48 / 55 / 0 |

So the I/O shire runs slightly warm of the mean at idle and slightly cool of it under a uniform minion load. Its peak
also stayed lower: 83 against the minion high of 87 in the first `thermal` sample.

A block beside the I/O shire (S20, S28, S29, S5) against the farthest block (S2, S10, S11, S19) should move the
difference `io − mean` in opposite directions. That makes it the only host-visible **located** temperature signal.
Its whole-degree resolution needs step-timing or many repeats.

**(c) Per-shire voltages: a check of where the current flows, not a thermometer.**

- The DEBUG map gives each shire's VDD_MNN in whole mV.
- The idle map is not a fixed per-monitor offset: under a 7 s all-shire load each shire's deviation changed with
  sd 1.6–1.9 mV (aifoundry2, aifoundry3) and 2.7 mV (aifoundry1 card 1) (power-temperature HTML `:396-406`;
  `tel.json` TEL-Q `Q4_t`).
- The V3 status was INSUFFICIENT or FAIL: complete 34-shire captures were rare (`tel.json` TEL-Q captures).
- Under a *partial* load it has never been captured. It could confirm the logical-to-physical placement, since the
  droop should concentrate on the loaded shires' `MS nn` lines, if MS nn = logical shire nn, which the repo assumes
  (brief HTML `:786`).

As a leakage-based temperature proxy it is hopeless. Estimate, computed here:

- Idle minion rail: 11.05 W at 73 °C (`16-dvfs-and-leakage.md:140`), so about 0.33 W and about 0.63 A per shire at
  0.518 V.
- Leakage grows e^(ΔT/36) (`11-thermal-model.md:18`), so a +3 °C local rise adds about 9%, about 0.055 A.
- The chip-wide sag is 0.08 mV/W (power-temperature HTML `:358`), about 0.04 mV/A at 0.52 V.
- The result is about 0.002 mV, three orders of magnitude below the 1 mV step. Even a 30× worse local impedance stays
  invisible.

**(d) Board power as a leakage-convexity signal.** Also too small. Estimate, computed here: a +6 °C block on 4 of 34
shires, with the rest −0.8 °C, gives a variance of ≈4.8 °C². The extra leakage ≈ ½·23.3 W·4.8/36² ≈ 0.04 W. The best
repeatability is 0.03–0.08 W (`14-card-behaviour.md:128-129`), and 0.04 W sustained heats the die by only about 0.1 °C
at 3.1 °C/W (`11-thermal-model.md:103-106`).

**(e) Temporal reconstruction of the mean.** Step timing recovers the mean to about 0.03 °C; the flip model
predicts power (`14-card-behaviour.md:103-114`; brief HTML `:923`). Both sharpen the mean only.

### 3.3 What would give a real map

Firmware options A, B and C, all of which should export the raw 12-bit code (brief HTML `:874-876`):

- A: add a 35-entry `shire_temps` array to the SP stats trace buffer;
- B: add a new DM command;
- C: call `pvt_print_temperature_sampled_values()` each pass and parse the trace like the voltage map.

Every option needs a rebuilt BL2. The images are signature-checked against an OTP key hash, and whether these cards
accept a rebuilt image is untested (brief HTML `:884`). The same need is ladder rung 12, "needs a signed image"
(`19-observability-and-the-unmetered.md:128`).

---

## 4. Spatial facts

### 4.1 The die

| Fact | Source |
|---|---|
| 570 mm²; about 25.6 mm E–W × 22.2 mm N–S | heat-per-mm HTML `:1025` (`D.inputs.die_mm2`, `die_w_mm`, `die_h_mm`) |
| Tile pitch 3.73 mm (x) × 3.70 mm (y); a hop is 3.72 mm | `PAGES/docs/findings/20-heat-per-mm.md:30-33` |
| 8 × 6 mesh stops: 34 minion shires, 1 PCIe, 1 I/O, 8 memory shires. With only four memory shires per side, the grid's corners are unoccupied (44 stops). | DS ch. 4, p. 21 |
| Memory shires: four on the west side, four on the east | PRM §1.5, p. 17; DS p. 30 |
| Each memory shire and its LPDDR4x PHY strip is about 1.76 mm wide (1.74–1.80); PCIe and I/O are in the top row of the to-scale drawing | heat-per-mm HTML `:1025` (`memshire_w_mm`), `:1139` |
| One temperature sensor per minion and I/O shire, "at same location as PD/VM". The manual counts 36 sensors. The PCIe shire has none, so 35 are live. | PRM §1.6, p. 17; brief HTML `:730`; `19-observability-and-the-unmetered.md:61` |
| Package thermal data: "will be included in a future release" | DS §9.1, p. 32 |
| `research/geometry/` (the die-plot measurements the page cites) is **not in either checkout** | `ls` of both trees |

The inner 6 × 6 grid spans 22.4 × 22.2 mm, about 87% of the die (computed here from the numbers above). Heat reaching
the memory strips or the empty corners reaches no sensor that enters the mean.

### 4.2 Logical shire ID → mesh position → die

- **Logical to mesh.** A kernel's logical shire is `hart >> 6` (`PAGES/workloads/enercat/kernel/enercat.c:132`),
  the index the `--shires` mask uses. marty1885's map, `MARTY` and `EMPTY` in `PAGES/workloads/nocbench/analyze.py:50-60`,
  places each logical shire on the 6 × 6 grid, x across and y down. A from-scratch latency search recovered it in
  12 of 12 restarts on every pass of **all three cards** (`05-claims.md:412`;
  `PAGES/docs/reports/data/2026-09-25-claims-v3/results/lat.json` `.items[LAT-N2].per_card.*.passes[].search_same_as_marty`). The non-compute cells are (0,3), (0,4), (0,5) and (5,3),
  and (5,3) routes traffic (`analyze.py:50-51, 60`).
- **Memory shires in the map frame.** MS0–3 sit at (1..4, −1), MS4–7 at (1..4, 6)
  (`PAGES/docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json` `decomp.ms_pos`). MS2's position is a
  tie-break (memory anatomy HTML `:773-775`).
- **Map to die.** "The map is the die turned a quarter": in the map the memory shires sit above and below the grid,
  on the die they sit west and east (`PAGES/docs/et-soc1-notes.md:102-106`; memory anatomy HTML `:775-777`).
  **Inferred here**, combining that with the PCIe and I/O shires in the die's top row at inner columns 5–6
  (heat-per-mm HTML `:1122-1127`) and (0,4) and (0,5) being I/O or PCIe (brief HTML `:786`):
  - die row r = map x, where r = 0 is the edge with I/O and PCIe;
  - die inner column c = map y + 1, where c = 0 is the west memory strip (MS0–3) and c = 7 the east (MS4–7).

  This is a transpose of the map, so distances are unchanged. The N/S labels are the drawing's; a mirror would not
  change any corner, edge or centre class below.

**Die-frame grid.** 34 of these 36 tiles have a sensor in the mean. M/S is the master or spare shire (in the mean);
IO/PCIe is the I/O shire, reported separately, or PCIe, which has no sensor.

| | c1 (west, beside MS strip) | c2 | c3 | c4 | c5 | c6 (east, beside MS strip) |
|---|---|---|---|---|---|---|
| **r0 (N die edge)** | **S0** (corner) | S8 | S3 | M/S | IO/PCIe | IO/PCIe (corner) |
| r1 (MS0 · MS4) | S24 | S16 | S4 | S12 | S20 | S28 |
| r2 (MS1 · MS5) | S9 | S1 | S13 | S21 | S29 | S5 |
| r3 (MS2 · MS6) | S25 | S17 | S14 | S22 | S30 | S6 |
| r4 (MS3 · MS7) | S2 | S10 | S18 | S26 | S15 | S7 |
| **r5 (S die edge)** | **S11** (corner) | S19 | S27 | M/S | S23 | **S31** (corner) |

Generated by `heatplace/placements.py` from `MARTY`. Rows r1–r4 of c1 and c6 border a memory shire; r0 and r5 lie on
the bare die edge, because the grid's 6 × 3.70 mm equals the die height (heat-per-mm HTML `:1025`).

So the compute **corners** are S0, S11 and S31. The fourth corner is IO/PCIe. The **centre** 2 × 2 is S13, S21, S14,
S22. The master and spare sensors, which count in the mean, sit mid-edge at (r0, c4) and (r5, c4).

### 4.3 What is known about heat spreading (all of it lumped)

- The model has six stages, τ = 1.5, 4, 60, 150, 400 and 2,500 s, with R = 0.106, 0.050, 0.234, 0.136, 0.860 and
  0.081 °C/W, 1.47 °C/W in total (`11-thermal-model.md:29-31`). The slow resistances are "not physics"
  (`:84-90`). The network belongs to one card in one chassis and does not transfer: aifoundry3 "sheds heat visibly
  faster" (`:134-135`; `12-heat-management.md:71-73`).
- Leakage is 12.6 + 23.3·e^((T−80)/36) W, 0.65 W/°C at 80 °C. The leakage loop gives 3.1 °C per sustained watt after
  10 min, against 1.2 °C open-loop (`11-thermal-model.md:18, 96-106`). The flip budget is about 3.1 W sustained at
  82 °C in the room of 21 September (`12-heat-management.md:57-63`).
- A 2D model needs lateral conductances and per-cell capacitances that only per-shire readings could fit (brief
  HTML `:894`). None exist.
- **No placement experiment has been run.**
  - Every reduced-core run used all 32 shires, with `--shires 0xffffffff --per-shire N`
    (`run_horace_long.sh:62-63`; `horace_long.sched`).
  - "Equal flip power gives equal heating regardless of where the flips come from" is about which transistors
    switch, not where on the die (`12-heat-management.md:49-51`).
  - The Horace spread runs are the uniform baseline: randn on 256 minions (8 per shire) went from 80 to 90 °C in
    276 and 315 s, on 128 minions it held 81–82 °C for 10 min, on 1,024 it took 19–26 s (`12-heat-management.md:20, 31, 35`).

### 4.4 The one spatial number on record

Under a uniform all-shire load, the hottest sensor sat 2–4 °C above the mean at each rise, and the coolest 1–2 °C
under the SP's minimum (§3.2 a).

### 4.5 Heat per millimetre (distance costs)

This matters only if a heater moves data. A random byte costs 1.58–2.34 pJ per hop on the loaded mesh
(`20-heat-per-mm.md:107`). TensorFMA on L1-scratchpad tiles and `enercat` register patterns use no mesh after setup
(`10-data-dependent-power.md:13-15`), so their NoC power stays the same wherever they are placed.

---

## 5. Placing a workload on a subset of shires

**`sparsity_host`**, from `workloads/sparsity` (TensorFMA, the Horace heater):

- `--shires <mask>` with `--per-shire N` runs hart 0 of minions 0…N−1 of every shire in the mask
  (`PAGES/workloads/sparsity/host/main.cpp:275-283, 996-997`; `kernel/sparsity.c:557`).
- `--stop-file` ends a long run cleanly. Raise `--budget`, which defaults to 8 s
  (`12-heat-management.md:123-127`; `main.cpp:980`).
- The long-run form is in `run_horace_long.sh:62-63`: `--test fma --type fp32 --pattern none --values randn --shires <mask>
  --per-shire 32 --seconds S --budget S+30 --stop-file F`.

**`enercat_host`**, from `workloads/enercat` (per-instruction patterns):

- `--shires <mask>`, `--minions <32-bit per-shire mask>` and `--harts 1|2`. The defaults are
  `--shires 0xffffffff`, `--harts 2`, `--seconds 4` and `--budget 9.5` (`PAGES/workloads/enercat/host/main.cpp:104-108, 503-511`).
- The kernel returns early for shires not in the mask and minions not in `--minions`. Tensor modes use one hart
  (`kernel/enercat.c:131-145`).
- Its `ops_per_s` assumes 600 MHz (`main.cpp:452`). Use `cycles_max` and `wall_s` if the clock moves.

**Heat per shire (fp32, random data, 600 MHz, over idle):**

- TensorFMA random normal on 1,024 minions: 63.40 W at 80 °C against 36.29 W idle, **+27.1 W, about 0.85 W per
  shire of 32 minions** (`10-data-dependent-power.md:39, 41`). The flip model gives 27.2 W
  (`12-heat-management.md:20`).
- Power is linear in active minions: 25.6 mW per minion at 256 and 512 active, 27.0 at 1,024
  (`16-dvfs-and-leakage.md:160-162`). So a 4-shire group adds about 3.3 W and an 8-shire group about 6.6 W.
- The hottest `enercat` patterns (catalogue, 32 shires, 2 harts, random operands; computed here as the mean of 3
  passes of `over_idle_w` in `2026-09-23-energy-manual/catalogue.json` `bursts`):
  - aifoundry2: `fmsub.ps` 26.1 W, `fnmsub.ps` 26.1, `fnmadd.ps` 25.7, `flog.ps` 25.7, `fmadd.ps` 24.8;
  - aifoundry3: 26.0, 25.4, 25.5, 24.8 and 25.1 W respectively.

**Lab rules that bind here:**

- "Never hold a device for more than 10 s" (`PAGES/AGENT.md:153`). A run to the threshold holds the device for
  minutes, as the Horace long runs did, so it needs the owner's explicit approval and the card lock.
- Preheating to 76 °C keeps the clock at 600 MHz, and `mhz.minion` must be checked in every sample
  (`14-card-behaviour.md:60-62`).
- Do not change TDP, clocks or the thermal threshold without the admin (`14-card-behaviour.md:211-216`).

**Timescale for a spread placement.** Computed here with `tools/ettelem/predict_heat.py --model
2026-09-21-horace-aifoundry2/model.json --toggles …/toggles_all.json --pattern randn --cap 66`. This is aifoundry2's
lumped model at 600 MHz; the network does not transfer to other cards.

| Active minions (spread over 32 shires) | Start 62 °C | Start 58 °C |
|---|---|---|
| 128 | 66 °C after 213 s | 461 s |
| 256 | 66 s (65.8 °C at 60 s) | 172 s |
| 512 | 18 s | 60 s |
| 1,024 | 3 s | 17 s |

Below 62 °C the model's idle die warms on its own: its idle equilibrium is 62 °C at 26.7 W
(`11-thermal-model.md:62-63`).

Sensitivity, computed here. Near 66 °C the 256-minion curve climbs about 0.04 °C/s, so a 0.5 °C placement effect on
the mean moves the crossing by about 11 s. Weaker heaters give larger time shifts but longer holds.

---

## 6. Candidate placements

Masks are over logical shire IDs (bit n = shire n) for `--shires`. Every group uses 32 minions per shire unless noted.
Features come from the die-frame grid in §4.2, computed by `heatplace/placements.py`:

- "N/S edge": tiles on the bare die edge;
- "mem strip": tiles bordering a memory shire;
- "by IO": tiles adjacent to an IO/PCIe tile;
- "hops→ctr": mean Manhattan distance to the die centre;
- "hops→IO": mean distance to the nearer IO/PCIe tile;
- "free nbrs": in-grid neighbours outside the group, a crude measure of spreading room.

| Group | Shires | `--shires` | Die rows × cols | N/S edge | mem strip | by IO | hops→ctr | hops→IO | free nbrs | ≈W over idle |
|---|---|---|---|---|---|---|---|---|---|---|
| B4-NW corner | 0, 8, 16, 24 | `0x01010101` | r0–1 × c1–2 | 2 | 1 | 0 | 4.0 | 4.0 | 4 | 3.3 |
| B4-SW corner | 2, 10, 11, 19 | `0x00080c04` | r4–5 × c1–2 | 2 | 1 | 0 | 4.0 | **8.0** | 4 | 3.3 |
| B4-SE corner | 7, 15, 23, 31 | `0x80808080` | r4–5 × c5–6 | 2 | 1 | 0 | 4.0 | 4.5 | 4 | 3.3 |
| B4-NE, by I/O+PCIe (the true corner is the I/O or PCIe tile) | 5, 20, 28, 29 | `0x30100020` | r1–2 × c5–6 | 0 | 2 | 2 | 3.0 | **1.5** | 6 | 3.3 |
| B4-W mid (memory side) | 1, 9, 17, 25 | `0x02020202` | r2–3 × c1–2 | 0 | 2 | 0 | 2.5 | 6.0 | 6 | 3.3 |
| B4-E mid (memory side; overlaps B4-NE) | 5, 6, 29, 30 | `0x60000060` | r2–3 × c5–6 | 0 | 2 | 0 | 2.5 | 2.5 | 6 | 3.3 |
| **B4-centre** | 13, 14, 21, 22 | `0x00606000` | r2–3 × c3–4 | 0 | 0 | 0 | **1.0** | 4.0 | **8** | 3.3 |
| B8-W band | 1, 2, 9, 10, 16, 17, 24, 25 | `0x03030606` | r1–4 × c1–2 | 0 | 4 | 0 | 3.0 | 6.0 | 8 | 6.6 |
| **B8-centre band** | 4, 12, 13, 14, 18, 21, 22, 26 | `0x04647010` | r1–4 × c3–4 | 0 | 0 | 0 | 1.5 | 4.0 | 12 | 6.6 |
| B8-E band | 5, 6, 7, 15, 20, 28, 29, 30 | `0x701080e0` | r1–4 × c5–6 | 0 | 4 | 2 | 3.0 | 2.5 | 8 | 6.6 |
| B8-mid rows | 1, 13, 14, 17, 21, 22, 29, 30 | `0x60626002` | r2–3 × c2–5 | 0 | 0 | 0 | 1.5 | 4.0 | 12 | 6.6 |
| B8-NW quadrant | 0, 1, 3, 4, 8, 9, 16, 24 | `0x0101031b` | r0–2 × c1–3, minus S13 | 3 | 2 | 0 | 3.25 | 4.0 | 6 | 6.6 |
| B8-SE quadrant | 6, 7, 15, 22, 23, 26, 30, 31 | `0xc4c080c0` | r3–5 × c4–6, minus M/S | 2 | 2 | 0 | 3.0 | 4.1 | 7 | 6.6 |
| B8-four corners, 2 each | 0, 8, 11, 19, 20, 23, 28, 31 | `0x90980901` | the four corners | 6 | 1 | 2 | **4.25** | 4.5 | 14 | 6.6 |
| C16-even checkerboard (`--per-shire 16`) | 1, 4, 5, 7, 8, 10, 11, 14, 20, 21, 23, 24, 25, 26, 27, 30 | `0x4fb04db2` | (r+c) even | 4 | 4 | 1 | 2.9 | 4.6 | 55 | 6.6 |
| C16-odd checkerboard (`--per-shire 16`) | 0, 2, 3, 6, 9, 12, 13, 15, 16, 17, 18, 19, 22, 28, 29, 31 | `0xb04fb24d` | (r+c) odd | 4 | 4 | 1 | 2.9 | 4.3 | 54 | 6.6 |
| Uniform baseline (Horace) | all 32, `--per-shire 8` | `0xffffffff` | everywhere | – | – | – | – | – | – | ≈6.6 (flip model 6.8 W, `12-heat-management.md:31`) |

The 256-minion groups are B8, C16 and the baseline. They hold total power fixed while the areal density varies 4× and
the position varies. The B4 groups are the same 2 × 2 shape in different positions. The W versus centre versus E bands
compare memory-strip sides against the middle at equal shape.

The pair with the most contrast for the I/O-sensor signal is B4-NE (1.5 hops, about 5.6 mm) against B4-SW (8 hops,
about 30 mm).

---

## 7. What the observables imply for the experiment (inferences, not measurements)

- **The trigger is the mean, so placement can shift "time to DVFS" only through the mean of 34 sensor readings.** I
  can see three routes.
  1. **Sensor coverage.** Heat that spreads into the memory strips, the empty corners or the PCIe tile reaches no
     sensor in the mean. That would make edge and corner placements read cooler, so they would trip later for the
     same watts. This is the owner's prediction, but for a sensing reason, not better cooling.
  2. **A non-uniform heatsink.** Unknown: no package or cooler data exists (DS §9.1).
  3. **Leakage convexity.** About 0.04 W (§3.2 d), too small to matter.

  A single hot shire above 65 °C does not trip the governor by itself.
- **Observable predictions per placement:**
  - the time to the first busy sample with `minshire[0] ≥ 66` (all cards);
  - the first down-step in `mhz.minion` or the launch-implied GHz (aifoundry2 cool, aifoundry1 card 1);
  - (high − mean) per reset window (concentration);
  - `ioshire − mean` (proximity to the I/O corner);
  - `board_w` (leakage, a null check).
- **Card roles.** aifoundry1 card 1 idles below 65 °C, so the onset is directly visible there.
  - aifoundry2 needs a cool start. Once it is warm it sits at 600 MHz.
  - aifoundry3 cannot show onset in its clock, but the mean-crossing proxy is identical there.
  - The lumped model says the three cards' thermal networks differ, so compare placements within a card, never
    absolute times across cards.

---

## 8. Not established or open

- Which physical sensor the PMIC's 75 °C "system temperature" alarm reads.
- Aifoundry1 card 1's governor. Its firmware 1.2.0 source was not read.
- Whether TS n and `MS nn` are logical shire n. The repo assumes it (brief HTML `:786`) and has not tested it. A
  partial-load DEBUG voltage capture could.
- The I/O and PCIe order at (0,4) and (0,5), and the master and spare order at (0,3) and (5,3) (brief HTML `:786`;
  heat-per-mm HTML `:1127`).
- Where each sensor sits inside its tile.
- Any lateral thermal conductance or per-tile capacitance.
- Whether raising the SP log level to DEBUG perturbs the governor's pass timing (not measured).
