# The ET-SoC-1 service processor's thermal governor, read from source (research task 1)

Scope: how the service processor (SP) firmware decides to change the minion clock and voltage, and the power state,
on thermal grounds. The source is read at the four versions the cards run or come closest to. The repo's own
observations of the governor are summarised at the end. No card was touched.

Path abbreviations:
- `ETP` = `/home/yaroslavvb/claude/et-soc1-prototyping/external/et-platform`, HEAD `836a4ab` (2026-07-17).
- `BL2` = `ETP/device-bootloaders/src/ServiceProcessorBL2`.
- `REPO` = `/home/yaroslavvb/claude/et-soc1-pages`, branch `pages-v3b` at `305fe0d`.
- `@X` = the file as of commit X (`git show X:<path>`). Copies of the governor files at each version are in
  `heatplace/src/<commit>/` in this scratchpad.

---

## 0. The answer

**Voltage-frequency scaling responds to the average, not to any one sensor.** The only temperature the software
governor compares with its threshold comes from `pvt_get_minion_avg_temperature()`. That function takes the
integer mean of the `current` readings of the **34 minion-shire temperature sensors** (shires 0–33, which include
the master and spare shires). Each sensor's reading is first truncated to whole °C. Sensors whose sample is
flagged as a fault are left out (`BL2/driver/pvt_controller.c:1274-1301`, `:567-585`, `:618-643`; the file is
identical in all four versions apart from its licence header).

The test is strict: `mean > 65`, where 65 is `TEMP_THRESHOLD_SW_MANAGED`. It is the same in every version
(`BL2/include/thermal_pwr_mgmt.h:41`; `@ffca4cbb4 …thermal_pwr_mgmt.c:668`; `@HEAD …thermal_pwr_mgmt.c:884`).

The firmware has **no per-sensor path and no maximum-temperature path** that can change the clock:
- The per-sensor maximum (`minshire_high`) is computed only to be reported to the host.
- `max_temp` is never written in any version.
- The on-die sensors' hardware interrupt block is never enabled.
- The one hardware trip is a **PMIC** alarm at 75 °C on the PMIC's own "system temperature" register, not on the
  die sensors. It forces a 300 MHz "safe" state.

Sections 2 and 5 give the details.

---

## 1. Which source matches which card

| Card | Release (BL / PMIC / minion) | Closest public source for BL2 | Governor generation |
|---|---|---|---|
| aifoundry2, aifoundry3 | 1.3.1 (0.20.0 / 1.5.0 / 0.23.0) | `ffca4cbb4` = `cafe03fc3^`, "Close development of version 0.20.0", 2024-05-17 | old (THERMAL_DOWN loop) |
| aifoundry1 card 1 | 1.2.0 (0.18.0 / 1.3.0 / 0.22.0) | `da192816a`, "Close development of version 0.18.0", 2024-03-27 | old, with hard-coded 50 MHz steps |
| aifoundry1 card 0 | 1.4.1 (0.21.2 / 1.6.1 / 0.24.0) | `50310b06b`, "Close development of version 0.21.0", 2024-09-25. **0.21.1 and 0.21.2 are not in the public history** | new (refactor `60b40c10f`) |

Sources for the table:
- Versions per card: `REPO/docs/findings/14-card-behaviour.md:149` and `REPO/docs/reports/data/2026-09-25-claims-v3/firmware.md:7-17`.
- Version commits: `git log -- device-bootloaders` (`ETP/device-bootloaders/CHANGELOG.md:21,41,62`). The CHANGELOG
  goes from `[Unreleased]` to `[0.21.0]`, with no 0.21.1 or 0.21.2 (`CHANGELOG.md:9-21`).
- `60b40c10f` (2024-09-24) is an ancestor of `50310b06b`. `7c6049087` (2024-10-10) and `478275330` (2024-11-26)
  are not (`git merge-base --is-ancestor`).

History of `thermal_pwr_mgmt.c` around the cards' builds (`git log -- …/thermal_pwr_mgmt.c`):

| Commit | Date | Change | In which cards' builds |
|---|---|---|---|
| `266a57184` | 2023-12-07 | "multiple fixes to DVFS algorithm for stability" | all four |
| `a342db9d2` | 2024-05-17 | "remove hardcoded freq volt values" (moves stepping to VMIN-LUT points) | 0.20.0 and later, not 0.18.0 |
| `8d81bd343` | 2024-06-07 | over-power and over-temperature events | 0.21.0 only |
| `a31928492` | 2024-08-28 | reduce operating point | 0.21.0 only |
| `e024210bc` | 2024-09-05 | "Fix go to power safe state" | 0.21.0 only |
| `f48cbbb80` | 2024-09-05 | power threshold values | 0.21.0 only |
| `60b40c10f` | 2024-09-24 | "Dvfs fixes and refactoring" (removes the THERMAL_* states) | 0.21.0 only |
| `7c6049087` | 2024-10-10 | thermal monitor retry | after 0.21.0 |
| `478275330` | 2024-11-26 | "Fix conversion in check_power_throttle_condition" | after 0.21.0 |

The PVT driver (`pvt_controller.c`, `bl2_pvt_controller.h`) is **identical in all four versions** apart from the
licence header (`diff` against HEAD: one hunk each). So the temperature computation in section 2 holds for every
card.

---

## 2. The temperature the governor compares (all versions)

**Sensors.** The PRM says there are 36 temperature sensors, "1 TS in each minion/IO Shire to measure temp at
same location as PD/VM", on five PVT controllers (PRM §1.6, p. 1-11, Table 1-6). The firmware:
- declares 5 controllers with 8 sensors each (`bl2_pvt_controller.h:20,25`);
- enables TS 0–7 on PVT0–3 and TS 0–2 on PVT4 (`ts_disable_mask` 0x00 and 0xF8, `pvt_controller.c:143-149`), which
  is 35 sensors;
- maps minion shire *i* to PVT *i*/8, TS *i*%8 (`pvt_controller.c:645-657`);
- defines 34 minion shires (`PVTC_MINION_SHIRE_NUM 34`, `bl2_pvt_controller.h:75`) and uses sensor 34 (PVT4 TS2)
  for the I/O shire (`PVTC_IOSHIRE_TS_PD_ID = 34`, `bl2_pvt_controller.h:440`).

The chip has 34 minion shires: 32 run kernels, plus the master and the spare (`REPO/docs/findings/README.md:97-98`).

**Conversion.** Every sensor uses the same nominal equation, with no per-sensor fuse calibration. Run mode 1
"doesn't need calibration" (`bl2_pvt_controller.h:95-97`), and the parameters are G = 57400, H = 249400,
CAL5 = 4096 (`:157,162,167`). The code computes `(G + (H·N)/CAL5 − H/2) / 1000` in `int`, so each reading is
truncated to whole °C (`pvt_controller.c:567-585`). With the 12-bit resolution (`bl2_pvt_controller.h:92`), one
count is 249.4/4096 ≈ 0.061 °C. The eFuses do hold "Thermal Sensor Calibration Values" for 35 sensors (PRM
§15.2.3.17, Table 15-48, bits 1568–2687), but this firmware never reads them. The PVT driver has no reference to
eFuses or calibration apart from that comment.

**Averaging.** `pvt_get_minion_avg_temperature()` loops over shires 0–33, adds `sample.current` for every sensor
whose sample has no `SAMPLE_FAULT`, and divides by the number of valid sensors in `int`, which truncates
(`pvt_controller.c:1274-1301`; the fault check is at `:628-633`). Sensors are sampled continuously in hardware,
starting at `pvt_init()` (`:1083-1105`, `:1102`).

So the governor's T is `floor( Σ floor(T_i) / n )`, and the trip `T > 65` means `Σ floor(T_i) ≥ 66·n`, which is
2,244 with n = 34. *Inference:* if the fractional parts are spread evenly, the trip falls at a true sensor mean of
about 66.5 °C.

**What is left out.** The I/O-shire sensor (TS 34) and the unused TS 35 are not in the mean (the loop stops at 33,
`pvt_controller.c:1281`).

**The host sees the same number.** Both `temp_c.minshire[0]` and `temp_c.pmic` in the repo's telemetry are this
mean. `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (`thermal_power_monitor.c:545, 982`) calls
`get_module_current_temperature()` (`thermal_pwr_mgmt.c:732-773`), which:
- fills `pmic_sys` with `pvt_get_minion_avg_temperature()`, not with the PMIC's reading (`:737-745`);
- fills `minshire_avg`, `minshire_high` and `minshire_low` from `pvt_get_minion_avg_low_high_temperature()`
  (`:747-757`; `pvt_controller.c:1303-1340`).

This matches the repo's claim that `pmic_sys` repeats the minion-shire mean (`REPO/docs/findings/05-claims.md:37`),
and `ettelem` prints `minshire` as `[avg, low, high]` (`REPO/tools/ettelem/ettelem.cpp:160-161`).

A side effect: the host query also writes `g_pmic_power_reg.soc_temperature` (`thermal_pwr_mgmt.c:754`). In the
HEAD and 0.21 governor, the thermal test reads that variable (`:867`), so a host query refreshes the governor's
input between passes. It is the same quantity, only more recent.

**`minshire_high` is a high-water mark, not the current maximum.** It is the maximum over sensors of each sensor's
hardware `SMPL_HI` register (`pvt_controller.c:637-640, 1322-1323`). That register is cleared only by
`pvt_hilo_reset()` (`:1029-1081`). The reset runs in `Thermal_Pwr_Mgmt_Init_OP_Stats()` (`thermal_pwr_mgmt.c:2828`),
which is called at start-up (`dm_task.c:174`) and by `DM_CMD_SET_DM_STATS_RUN_CONTROL` with
`STATS_CONTROL_RESET_COUNTER` (`performance.c:573-576`). `ettelem sample --reset-ms` sends that reset
(`ettelem.cpp:59-66`).

In the repo's data the stats were never reset (`since_reset_ms` = −1), so `high` sits at a stale value. On
aifoundry2 it reads 93 °C and `low` reads 60 °C for hours (`2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz`: every
sample is `[73, 60, 93]`).

---

## 3. The governor on aifoundry2 and aifoundry3 (BL2 0.20.0, `@ffca4cbb4`)

aifoundry1 card 1 (0.18.0, `@da192816a`) has the same logic line for line in `update_module_current_temperature`,
`update_module_soc_power`, `thermal_throttling`, `thermal_power_task_entry` and `pmic_isr_callback` (`diff` shows
no differences). The step functions and the `power_throttling` exit tests differ; see the end of this section.

**The sampling loop.** The device-management task repeats forever:
1. `update_module_current_temperature()`;
2. PMB stats;
3. `update_module_soc_power()`;
4. frequencies and other statistics;
5. `vTaskDelay(pdMS_TO_TICKS(DM_TASK_DELAY_MS))` with `DM_TASK_DELAY_MS` = 10 (`@ffca4cbb4 dm_task.c:199-275`;
   `mgmt_build_config.h:432`).

Measured pass time: 133 ms on aifoundry2 and aifoundry1 card 1, and 224 ms on aifoundry3, when quiet
(`REPO/…/2026-09-22-dvfs-aifoundry2/dvfs.json` `v3.sp_pass_ms.*.quiet_ms`). The pass time is dominated by busy-wait
I2C delays (`US_DELAY_GENERIC(1000)`, `i2c_controller.c:239,320`).

**Governor states.** `POWER_IDLE` 0, `THERMAL_IDLE` 1, `POWER_UP` 2, `POWER_DOWN` 3, `THERMAL_DOWN` 4, `POWER_SAFE` 5,
`THERMAL_SAFE` 6 (`@d5da8c642 device-api/include/management-api/device_mgmt_api_spec.h:285-291`; the device API as
of April 2024. The enum was replaced on 2024-09-13 by `1ec1d77dd`). The dm task writes the next state into
`g_soc_power_reg.power_throttle_state`, and the power-management task acts on it (`thermal_pwr_mgmt.c:2404-2458`).

**The thermal trigger**, checked on every pass (`thermal_pwr_mgmt.c:651-688`):
```
T = pvt_get_minion_avg_temperature()                          # l.656
if T > sw_threshold(65) and state < THERMAL_DOWN and active_power_management:   # l.668-670
    log "Thermal throttle down event, current temperature: %u, threshold: %d"   # l.673
    state = THERMAL_DOWN; notify power task                    # l.678-679
```
**There is no check of whether the master minion is busy**, so an idle card above 65 °C enters `THERMAL_DOWN` as
well. Compare the power branch below, which does look at `mm_state`.

**The thermal loop** (`thermal_throttling`, `:2289-2383`):
```
T = pvt_get_minion_avg_temperature()                          # l.2308
while T > 65 and state <= THERMAL_DOWN:                        # l.2316-2317
    reduce_minion_operating_point()   # one VMIN-LUT point down # l.2334
    vTaskDelay(pdMS_TO_TICKS(DELTA_TEMP_UPDATE_PERIOD))  # 1000 # l.2354; thermal_pwr_mgmt.h:87
    T = pvt_get_minion_avg_temperature()                      # l.2357
state = THERMAL_IDLE; log "Thermal idle state event …"        # l.2366-2374
```
- **Step size:** one VMIN-LUT point. `flash_fs_get_vmin_lut_minion_previous_frequency_point()` returns the previous
  table entry, or the same frequency at index 0, so the loop does nothing at the bottom point (`@ffca4cbb4
  driver/flashfs.c:2389-2404`). The table has 11 slots (`NUMBER_OF_VMIN_LUT_POINTS`,
  `…/shared/common/include/service_processor_BL2_data.h:87`). On aifoundry2 the observed points are 600 MHz at
  0.517 V, 700 at 0.568 and 800 at 0.618 (`dvfs.json` `operating_points`; `16-dvfs-and-leakage.md:20`).
- Frequencies are rounded to multiples of 25 MHz (`thermal_pwr_mgmt.c:1794-1797`; `MODE_FREQUENCY_STEP_SIZE 25`,
  `ETP/etsoc-hal/include/hwinc/lvdpll_defines.h:66`; `USE_FCW_FOR_LVDPLL 0`, `mgmt_build_config.h:369`).
- Voltage moves with frequency. The minion and L2 voltages are set **before** the PLL, going up and going down
  (`:1801-1849`). HEAD changed the order for down-steps (section 4).
- **No hysteresis.** Entry and exit use the same `> 65` (`:668, :2316`).
- **On exit the clock returns to the idle point.** State `THERMAL_IDLE` makes the task call
  `power_throttling(POWER_IDLE)` → `go_to_idle_state()` (`:2446-2449, :2190-2196, :1975-1979`). That sets
  `flash_fs_get_mnn_boot_freq()` = `vmin_lut[0].mnn.freq`, the bottom table point (`@ffca4cbb4 flashfs.c:2162-2165`).
- **While the loop runs, nothing else acts.** The power-management task sleeps inside the loop, and the power
  branch needs `state < THERMAL_DOWN` (`:845`). A hot idle card therefore stays in this loop for as long as the mean
  reads above 65, re-reading every period and doing nothing at the bottom point. This fits aifoundry2 resting at
  73 °C with all 1,112 strict-protocol launches at 600 MHz (`16-dvfs-and-leakage.md:52-56`). It also fits the SP
  traces holding no governor lines for aifoundry2 (`dvfs.json` `v3.governor.aifoundry2.governor_lines` = 0;
  `strings` of `REPO/…/2026-09-22-cards/sptrace-aifoundry2*.bin`).

**The power branch**, run on every pass only when `active_power_management` is on and `state < THERMAL_DOWN`
(`:844-845`):
```
P = pmic_read_instantaneous_soc_power()        # l.798-806; the average is read at l.788 into op_stats only
if mm_state == IDLE:    if state != POWER_IDLE: state = POWER_IDLE     # l.848-860
elif P > TDP and state < POWER_DOWN:           state = POWER_DOWN     # l.862-872
elif P < TDP and state < POWER_UP:             state = POWER_UP       # l.876-886
```
`power_throttling()` (`:2133-2268`) then steps **in a loop with no delay** until its exit test holds, re-reading the
PMIC **average** each time (`:2219`):
- UP exits when the average exceeds TDP or at the maximum frequency (`:2229-2236`);
- DOWN or SAFE exits when the average is below 1.05 × TDP = 68.25 W, or at 300 MHz (`:2238-2246`,
  `UPPER_POWER_THRESHOLD_GUARDBAND`, `thermal_pwr_mgmt.h:81`).

So **an up-step climbs to the top point in one go**. This matches the repo's observation of 600→800 MHz within one
100 ms sample (`16-dvfs-and-leakage.md:88-91`). *Inference:* at the bottom point the reduce is a no-op, so a DOWN
episode whose average stays above 68.25 W would spin until the power falls.

**Priority.** Thermal outranks power: power requests are accepted only below `THERMAL_DOWN`. The PMIC safe states
outrank everything (5 and 6 are the highest values).

**Card 1 (0.18.0) differences.** Down and up steps are fixed at 50 MHz between 300 and 700 MHz
(`@da192816a thermal_pwr_mgmt.h:56-58`; `thermal_pwr_mgmt.c:1769-1811`). The loop exits compare against those
constants. The trigger, the loop, the thresholds and `DELTA_TEMP_UPDATE_PERIOD` are the same (`@da192816a
thermal_pwr_mgmt.c:590, 2166, 2204, 2218`; `thermal_pwr_mgmt.h:75, 106`).

---

## 4. The governor on aifoundry1 card 0 (BL2 0.21.x; closest public source `@50310b06b`, equal to HEAD except one line)

`check_power_throttle_conditions()` runs once per dm pass (`@50310b06b dm_task.c:211-280`;
`thermal_pwr_mgmt.c:853-915`; HEAD `:864-926`):
```
T = soc_temperature (the same 34-sensor mean);  P = op_stats.system.power.avg (the PMIC average)
if active_power_management and get_mm_state() != IDLE:         # HEAD l.879-880 — only while a kernel runs
    if T > 65:  if f > f_min: request POWER_DOWN               # l.884-894 (at f_min: nothing, power tests skipped)
    elif P > TDP and f > f_min: request POWER_DOWN             # l.898-907
    elif P < TDP and f < f_max: request POWER_UP               # l.910-919
```
- **One VMIN-LUT point per request, and a request can come every pass.** No thermal loop and no
  `DELTA_TEMP_UPDATE_PERIOD` (HEAD `:1887-1907, :1929-1959`).
- Up-steps set the voltage first, then the frequency. Down-steps set the frequency first, then the voltage
  (`:1813-1849`).
- Idle comes from the master minion's busy→idle transition, which requests `POWER_IDLE` and sets the bottom point
  (`:3108-3124, :1980-1985`).
- **With the master minion idle there is no thermal response at all.**
- Task priority for requests arriving together: SAFE, then IDLE, then DOWN, then UP. DOWN is ignored while in SAFE
  (`:2244-2271`).
- **0.21.0 has an overflow bug.** `avg_soc_pwr_mW` is `uint16_t` (`@50310b06b thermal_pwr_mgmt.c:858`), so board
  power above 65.535 W wraps to a small number and the test goes the wrong way (POWER_UP instead of POWER_DOWN).
  `478275330` fixed it on 2024-11-26 (HEAD `:869-871`). Whether 0.21.2 carries the fix is not established.

---

## 5. Every other path that can change the clock, and whether any per-sensor or maximum path exists

| Path | Input | Effect | Source |
|---|---|---|---|
| SW thermal | 34-sensor integer mean, `> sw_threshold` (65 by default) | one LUT point down; 0.20.0: repeated every `DELTA_TEMP` period until ≤ 65, then back to the bottom point | §3, §4 |
| SW power | board power (0.20.0: instantaneous; 0.21+: PMIC average) against TDP (65 W) | down or up; 0.20.0 loops until the average exit test | §3, §4 |
| Master minion idle | MM state | bottom LUT point (`vmin_lut[0]`) | `@ffca4cbb4 :848-860`; HEAD `:3108-3124` |
| **PMIC alarm (the hardware trip)** | the PMIC's own "System Temperature" register against 75 °C; board power against 75 W | 0.20.0: `THERMAL_SAFE` or `POWER_SAFE`; 0.21+: `POWER_SAFE`; either way `SAFE_STATE_FREQUENCY` 300 MHz; a FATAL `PMIC_ERROR` event goes to the host | `bl2_pmic_controller.h:262,281`; `pmic_controller.c:503-515` (thresholds written at boot, `main.c:552`); ISR callback `@ffca4cbb4 thermal_pwr_mgmt.c:2480-2497`, HEAD `:2317-2323`; handler HEAD `pmic_controller.c:725-750` |
| Host DM commands | `SET_MODULE_TEMPERATURE_THRESHOLDS` (any uint8, no range check), `SET_MODULE_STATIC_TDP_LEVEL`, `SET_MODULE_ACTIVE_POWER_MANAGEMENT`, `SET_FREQUENCY` | change the threshold or TDP, turn DVFS off, or pin the clock (the aifoundry3 clock guard uses the TDP and frequency commands) | `thermal_power_monitor.c:493-526, 958-985`; `14-card-behaviour.md:172-178` |
| Invalid VMIN LUT at boot | flash | DVFS off (`active_power_management = OFF`) | HEAD `thermal_pwr_mgmt.c:1628-1647` |

The PMIC temperature is not the die. `pmic_get_temperature()` reads `PMIC_I2C_SYSTEM_TEMP_ADDRESS`
(`pmic_controller.c:1327-1330`), and the source says "PMIC is currently reporting system temperature as 0"
(`thermal_pwr_mgmt.c:2837`). The allowed alarm range is 55–75 °C (`bl2_pmic_controller.h:286,291`). The sensor
behind it is PMIC firmware, which is not in the open source. The repo's telemetry does not record it, because
`temp_c.pmic` is the PVT mean (section 2).

**In 0.20.0 the safe state may not move the PLL.** `go_to_safe_state()` changes the frequency only if the voltage
lookup for 300 MHz *fails*, but it updates the reported frequency register either way (`@ffca4cbb4
thermal_pwr_mgmt.c:2010-2034`). `e024210bc` "Fix go to power safe state" replaced it on 2024-09-05. In 0.18.0 the
frequency change has no such condition (`@da192816a :1858-`, `diff`).

**No per-sensor or maximum-temperature trip exists in the SP firmware:**
- `minshire_high` (the maximum of the per-sensor high-water marks) is only returned to the host
  (`thermal_pwr_mgmt.c:756`).
- `g_soc_power_reg.max_temp` is read by `get_soc_max_temperature()` (HEAD `:1380-1384`) and `dump_power_globals()`,
  and is **never assigned** in 0.18.0, 0.20.0, 0.21.0 or HEAD (`git grep max_temp`). `DM_CMD_GET_MAX_TEMPERATURE`
  (`historical_extreme.c:138-165`) therefore reports the zero-initialised value.
- The PVT controllers have TS interrupt registers (`irq_en`, `irq_ts_mask`, …: `ETP/etsoc-hal/include/hwinc/sp_pvt0.h:57-90`;
  PRM Table 15-52). Nothing in `device-bootloaders` enables them: `pvt_configure_controller()` writes only the
  disable masks (`pvt_controller.c:362-372`), and `grep irq_en|PVTC_IRQ` finds nothing.
- No firmware path prints per-shire temperatures at run time. `pvt_print_min_shire_temperature_sampled_values()`
  and `pvt_get_and_print()` have no callers in `ETP` (`grep`). The per-shire *voltage* lines the repo used in E6 come
  from the `GET_MINION_VM` macro inside the per-pass power update (`pvt_controller.c:23-60, 1342`). The temperature
  averaging has no such log line.
- The datasheet has no thermal specification ("Package Thermal Information … will be included in a future
  release", Preliminary Datasheet §9.1, p. 33).

---

## 6. Periods and step sizes

| Item | 0.18.0 / 0.20.0 (card 1; aifoundry2 and aifoundry3) | 0.21.x (card 0) |
|---|---|---|
| Decision rate | every dm pass: 133 ms (a2, a1c1) or 224 ms (a3) quiet; 159 to 162 and 266 ms under E10 load (`dvfs.json` `v3.sp_pass_ms`) | every dm pass |
| Thermal step spacing | `DELTA_TEMP_UPDATE_PERIOD` = 1000 FreeRTOS ticks between steps (nominally 1 s; see §7) | one step per pass |
| Thermal step size | 0.20.0: one VMIN-LUT point (a2: 800→700→600); 0.18.0: 50 MHz, 300–700 MHz | one LUT point |
| Up-step | 0.20.0: climbs to the top in one call; 0.18.0: 50 MHz steps in one call | one LUT point per pass |
| Thermal threshold | `> 65` on the truncated mean, no dead band | the same |
| Power threshold | 65 W (instantaneous in); exit from DOWN below 68.25 W average | 65 W (average); 0.21.0 wraps above 65.535 W |
| Hard trips | PMIC 75 °C (PMIC's own sensor) and 75 W → 300 MHz | the same |

---

## 7. Observation (hypothesis, not established): the 1000-tick thermal delay lasts about 0.4 s on the cards

- FreeRTOS assumes a 4 MHz timer: `configCPU_CLOCK_HZ 4000000ULL /* mtime ticks at 4MHz for now */` and
  `configTICK_RATE_HZ 1000` (`ETP/device-bootloaders/external/FreeRTOSConfig/FreeRTOSConfig.h:95-96`, the same in
  all three builds). So one tick is 4,000 timer counts (`…/FreeRTOS/Source/portable/GCC/RISC-V/port.c:96`).
- The SP's own timer driver says the counter runs at 4 MHz only before SP PLL0 locks, and at 10 MHz with the PLL at
  100% (`BL2/driver/timer.c:23-36`, dividers at `:115-155`). The PLL frequency comes from ROM data
  (`ServiceProcessorBL1/src/bl1_main.c:229`), which the open source does not include.
- If the PLL runs at 100%, one tick lasts 0.4 ms and `vTaskDelay(pdMS_TO_TICKS(1000))` lasts about 0.4 s.
- **The evidence.** Under the 0.20.0 source, nothing can change the clock during that delay: the task sleeps, and
  the power branch is locked out. Yet E10's consecutive down-steps inside one episode are 0.4–0.5 s apart, at a
  10 Hz sampler:

  | Transitions | Times (s) |
  |---|---|
  | 8→9 | 1.11→1.61 |
  | 11→12 | 2.51→2.91 |
  | 14→15 | 1.09→1.59 |
  | 17→18 | 5.5→6.0 |
  | 20→21 | 6.9→7.3 |
  | 26→27 | 1.32→1.82 |
  | 30→31 | 3.12→3.62 |

  (`dvfs.json` `transitions[].t`). The median gap between changes over 239 changes is 0.4 s
  (`governor_days.change_gap_s`).
- What this changes: the thermal episode's pacing (one step about every 0.4 s, not 1 s) and the "no response"
  window after a trip.

---

## 8. What the repo observed, mapped onto this logic

**E10, 21 September, aifoundry2, seven cool-start runs, 36 clock transitions** (`16-dvfs-and-leakage.md:67-91`;
`dvfs.json` `transitions`, `transition_summary`). There were 18 up-steps and 18 down-steps. Voltage tracked frequency
in all of them (`transition_summary.voltage_tracks_frequency`).

Die temperature at each transition, as the 10 Hz sampler read it (`transitions[].T`):
- **Down-steps:** 64 °C once, 65 °C 6 times, 66 °C 7 times, 67 °C 4 times.
- **Up-steps:** 63 °C once, 64 °C 5 times, 65 °C 8 times, 66 °C 4 times.
- Over two days, all up-steps fell at 62–66 °C (`governor_days.up_T`).

The page attributes the 18 down-steps by cause (`transition_summary.by_cause`):
- **Thermal only (7):** the die read above 65 °C while the board drew 45–56 W.
- **Thermal and power (4):** random data at 800 MHz, 69–88 W.
- **Unattributed (7):** the sampler read 64–65 °C.
- **Power branch alone: 0.**

How the 0.20.0 source accounts for these:
- The unattributed steps are what the source predicts when the SP's own read, up to one pass earlier or later than
  the sampler's, was 66. In a 800→700→600 pair (17→18, 20→21, 26→27), the second step is either the loop's second
  reduce or the return to the bottom point on exit. Both come about 0.4 s later (§7).
- 18→19 (600→800 at +0.1 s) and 21→22→23 are exits to `THERMAL_IDLE`, then the bottom point, then `POWER_UP`
  climbing to the top on the next pass (§3).
- The single 800→600 step (transition 1, t = 5.95 s) can only be a return to the bottom point (MM idle or thermal
  exit). The source has no direct two-point down-step on the thermal or power path.
- 34→35 (800→700→600 in 0.1 s at 87.8 W) is the power loop stepping without delay.

**The clock "lifts to 700–800 MHz mid-burst below about 68 °C" (sampler reading).** For this reason measurements
are preheated to 76 °C (`14-card-behaviour.md:59-61`; `19-observability-and-the-unmetered.md:89-91`).

**The first change came 0.39–0.99 s after a launch** (`16-dvfs-and-leakage.md:88`). This is not fully explained by
the source. One consistent reading: when the SP's mean is above 65 at the launch, the card sits in the thermal loop
and waits one delay period before it can exit.

**A spread measurement already in the repo.** In E5 (20 September, a full-chip matmul load at 62–65 W, aifoundry2),
the high-water mark rose 87→88→89→90 while the mean read 84–85, 86 and 87. So each time it set a new record, **the
hottest minion-shire sensor read about 3 °C above the 34-sensor mean** (`2026-09-20-power-aifoundry2/thermal-telemetry.jsonl`,
samples 654, 702, 762: `minshire` = [85,62,88], [86,62,89], [87,62,90]; E5 in `03-experiments.md:115-139`). The
stale 93 °C high-water on aifoundry2 is likewise about 3 °C above the 90 °C mean that E7 reached
(`03-experiments.md:161-172`). The I/O-shire sensor reads within ±1 °C of the mean
(`2026-09-24-wire2-aifoundry2/telemetry.jsonl.gz`: `ioshire[0] − minshire[0]` ∈ {−1, 0, 1}).

**aifoundry3** logs a power throttle-down at every kernel start and never steps up, because a boot service sets its
TDP to 0 (`14-card-behaviour.md:166-178`). Its trace strings, `Power throttle down event, current pwr 35380  tdp
level: 0`, have the 0.20.0 format: the instantaneous power in mW (`@ffca4cbb4 thermal_pwr_mgmt.c:866-868`;
`REPO/…/2026-09-22-cards/sptrace-aifoundry3.bin`).

**aifoundry1 card 0 at 115 °C and its `low_power` state.** The observations (`14-card-behaviour.md:64-72, 197-203`;
`AMENDMENTS.md:48-49, 159-166`):
- It read 115–117 °C with nothing running and drew 66–71 W at 600 MHz, then "its firmware dropped it to 300 MHz".
- It idles at 300 MHz and 398 mV (18.6–18.8 W).

What the source says:
- **`low_power` is a label, not a governor state.** In 0.21+ `get_power_state()` returns `LOW_POWER` whenever board
  power is at or below 30 W (`SAFE_POWER_THRESHOLD_W`), `MAX_POWER` above TDP, and `MANAGED_POWER` otherwise
  (`@50310b06b thermal_pwr_mgmt.c:392-403`; HEAD `:403-414`; `thermal_pwr_mgmt.h:60`). The 0.20.0 macro compares
  milliwatts against the bare number 30, so it never reports low power (`@ffca4cbb4 :300-303`).
- **An idle die at 115 °C gets no software response** in the 0.21 governor, because it acts only while the master
  minion is busy (HEAD `:879-880`). The 75 W power alarm was not reached (66–71 W).
- The drop to 300 MHz is consistent with either of two paths:
  - (a) a PMIC over-temperature alarm, which sets `POWER_SAFE` = `SAFE_STATE_FREQUENCY` 300 MHz; or
  - (b) an MM-idle return to `vmin_lut[0]`, if card 0's table starts at 300 MHz. The amendments assume that
    (`AMENDMENTS.md:165`). The driver reported a boot clock of 600 MHz for both aifoundry1 cards
    (`2026-09-25-aifoundry1/facts.md:54-56`). That value is `Get_Minion_Frequency()` when the SP fills its
    registers (`BL2/config/dir_regs.c:323`), not necessarily `vmin_lut[0]`.
- Which of the two it was is **not established**. Only the SP trace from that moment would show it.

---

## 9. Instruments available for a placement experiment (from the source; nothing run)

- **The governor's input is exactly `temp_c.minshire[0]`**: the same function and the same truncation. The
  sampler and the SP read it at different instants, up to one pass apart.
- **The hottest sensor over a window, but not which sensor.** Reset the stats (`ettelem sample --reset-ms R`, which
  sends `DM_CMD_SET_DM_STATS_RUN_CONTROL` with the reset flag). `minshire[2]` then gives the maximum over the 34
  sensors of each sensor's peak since the reset, and `minshire[1]` the minimum (§2).
  - On 0.20.0 the reset does not touch the governor's inputs, which are `soc_temperature` and the instantaneous
    power (§3).
  - On 0.21+ it re-seeds `op_stats.system.power.avg` from a fresh PMIC average (HEAD `:2874-2880`), and the
    governor reads that value.
  - Whether a reset also affects the PMIC's running average is untested (`ettelem.cpp:59-60`).
- **The I/O-shire sensor** is available on its own (`ioshire[0]`).
- **No per-shire temperature readout exists** in these builds (§5). The trace-based method of E6 works only for
  voltages.
- **The clock itself** (`mhz.minion`) is the only reliable sign of a step (`14-card-behaviour.md:87`).

---

## 10. What the firmware implies for the placement hypothesis (inference, not tested)

1. **Only the 34-sensor mean matters for the software trip.** For the same total power, placement can change the
   time to the first thermal step only through `Σ_i ΔT_i` over all 34 sensors. That is the sum of the heat source's
   thermal coupling to every sensor, including the master and spare shires, which a user kernel never loads. A
   placement that is hotter locally but couples less to the sensor field as a whole would trip later. Hot-spot
   temperature alone is not the quantity to predict.
2. **The power branch is blind to placement.** Board power against 65 W does not care where the heat is, so the
   experiment must keep board power below 65 W at the top operating point. Otherwise power steps confound the
   result, as in E10's 4 "thermal+power" steps. A partial-chip load does that naturally. On 0.20.0 a cool start
   with P < 65 W jumps straight to the top point (§3), which gives a clean "run at 800 MHz until the first
   down-step" metric.
3. **The resolution is one whole degree on a truncated mean.** The trip is `Σ floor(T_i) ≥ 2244`, so time-to-trip
   has a quantisation floor set by how fast the mean crosses one degree. At the rates in E10 (first down-steps
   0.4–1.1 s after launch at 62–66 °C), a placement effect must move the crossing time by more than about one SP
   pass (133–160 ms) to be seen. A cool start several degrees below 65 lengthens the time to trip and makes a
   difference easier to resolve.
4. **Card differences that matter.**
   - aifoundry2 is usable, but it idles at about 73 °C and sits locked in the 0.20.0 thermal loop above 65 °C. It
     needs a start below 65 °C, which the repo reached only at 62–64 °C (E10).
   - aifoundry3 is useless for this: its TDP of 0 pins it at 600 MHz.
   - aifoundry1 card 1 runs the same logic with 50 MHz steps and a 700 MHz ceiling. It idles at 57–62 °C, below
     the threshold.
   - Card 0 must not carry sustained load.
5. **"One sensor over the limit" never triggers anything.** Under a uniform full-chip load the hottest sensor
   already reads about 3 °C above the mean (E5) and trips nothing on its own. A test that pushes one shire's sensor
   well above 65 while the mean stays at or below 65, with no clock change, would confirm the mean-only rule on the
   card. This is predicted from the source for every version.

---

## 11. Not established

- The source of 0.21.1 and 0.21.2 (card 0): whether they carry `7c6049087` and the `uint16_t` fix `478275330`.
- The SP PLL0 frequency on the cards, and so the real length of a FreeRTOS tick (§7 is an inference from E10's step
  spacing).
- What sensor the PMIC's "system temperature" reads, and whether a PMIC over-temperature alarm has ever fired on any
  card. The repo has no `PMIC_ERROR` event on record (`grep` of `REPO/docs`).
- Why card 0 dropped to 300 MHz at 115 °C: PMIC safe state or idle point (§8).
- The physical position of each minion shire's sensor. The PRM's sensor figure (§1.6) is not in the text extraction,
  and the firmware maps shire → sensor only by index (`pvt_controller.c:645-657`).
- The sensor-to-sensor spread under a *localised* load. The only spread in the repo is under a uniform full-chip
  load (about 3 °C, §8).
