# REVIEW 2: the ET-SoC-1 thermal/DVFS governor, read exactly, and what the three cards show

Written 2026-09-27, ~22:00 PDT, for the next set of DVFS/heat experiments. Read-only: firmware source, the pages
worktree, the heat-placement worktree and scratch data. No card was touched and nothing was committed.

Every statement carries a source reference. Three other marks are used:
- **[data]**: a measurement already on disk, with its path.
- **[computed here]**: arithmetic or a parse done for this review, with its inputs.
- **[inference]**: my reasoning. It is not source text and has not been measured.

## Citation key

| Tag | Meaning |
|---|---|
| `C:` | et-platform `ffca4cbb4` (= `cafe03fc3^`, "Close development of version 0.20.0", 2024-05-17). This is BL2 0.20.0, the closest public source to the 1.3.1 cards (aifoundry2, aifoundry3). Paths are under `device-bootloaders/src/ServiceProcessorBL2/` unless stated. `C:tpm` = `services/thermal_pwr_mgmt.c`, byte-identical to `HP/tpm-may2024.c` (checked with `diff`) |
| `O:` | et-platform `da192816a` (BL2 0.18.0, 2024-03-27), the closest source to aifoundry1-c1 (release 1.2.0). `O:tpm` as above. Copies are in `HP/src/da192816a/` (checked with `cmp`) |
| `H:` | et-platform `836a4ab` (HEAD, 2026-07-17). **For this review, `353f20e` is the same source.** `git diff --stat 353f20e 836a4ab -- device-bootloaders et-trace et-driver device-api device-minion-runtime` lists only five `get_git_*.py`/`movelus_pll_csv_to_h.py` script lines [computed here] |
| `API:` | `d5da8c642:device-api/include/management-api/device_mgmt_api_spec.h`, the last device-api commit before 0.20.0 closed. The `DM_CMD` numbering is identical to `H:` (`diff` of the `DM_CMD_*=N` lists is empty [computed here]). `APIr:` = `…/device_mgmt_api_rpc_types.h` at the same commit |
| `MM:` | `9e61967f1^:device-minion-runtime/src/MasterMinion/`, master-minion runtime 0.23.0 (the 1.3.1 cards'). 0.22.0 (`b4aa2454d`) has the same heartbeat lines |
| `ET:` | `H:et-trace/include/et-trace/`. The card-era trace encoder is not in the tree |
| `DRV:` | `H:et-driver/et-soc1-pcie.c` |
| `R/` | `/home/yaroslavvb/claude/et-soc1-pages5` (branch `pages-v5`, `b083d80`) |
| `W/` | `/home/yaroslavvb/claude/et-soc1-heat` (branch `heat-placement`; `tools/claims-v3/hp/` is untracked working-tree code) |
| `HP/` | `…/scratchpad/heatplace/` (`firmware.md`, `CRITIQUE.md`, `DESIGN2.md`, `derive_feasibility.out` = `dfo:N`, `dev/`) |

Which source runs on which card:
- aifoundry2 and aifoundry3: release 1.3.1, BL2 0.20.0 (`R/docs/reports/data/2026-09-25-claims-v3/firmware.md:5-17`).
- aifoundry1-c1: release 1.2.0, BL2 0.18.0 (`R/docs/findings/14-card-behaviour.md:154`).

The pages' firmware statements are made at `353f20e`, as `R/docs/reports/sources/dvfs-leakage.body.html:85-87,474-487` and
`R/docs/reports/sources/limits-of-observability.body.html:330` say. That is the rewritten governor (`60b40c10f`,
2024-09-24), **not** what the cards run.

---

## 0. The answer in brief

1. **The temperature input is the mean, never one sensor.** Every version compares one number with the threshold:
   `pvt_get_minion_avg_temperature()`.
   - It is the integer mean of the **34 minion-shire sensors**. Each reading is first truncated to whole °C, and
     sensors whose sample is flagged as a fault are left out (`C:driver/pvt_controller.c:572-590,623-648,1279-1306`).
   - The test is strict: `mean > 65` (`C:include/thermal_pwr_mgmt.h:46`; `C:tpm:668`; `O:tpm:590`; `H:tpm:884`).
   - With all 34 sensors valid, the trip is `Σ floor(T_i) ≥ 2244` [computed here].
   - There is no per-sensor path, no maximum path and no PVT alarm interrupt (§6).
2. **On the cards' build (0.20.0), the thermal response is a loop, not one step per pass.**
   - Once the mean reads 66 or more, the service processor (SP) steps the minion clock down one VMIN-LUT point.
   - It then sleeps 1000 FreeRTOS ticks, re-reads the mean, and repeats until the mean reads 65 or less
     (`C:tpm:2316-2361`).
   - On exit it sends the clock to the **boot point** (600 MHz), not back up (`C:tpm:2366-2369,2446-2449,1975-1979`).
   - On the next pass the power branch climbs straight back to 800 MHz, provided a kernel runs and board power is
     under 65 W (`C:tpm:876-887,2229-2236`).
   - There is no hysteresis. Neither the trigger nor this loop checks whether a kernel is running.
3. **One thermal-loop period is about 0.40 s, not 1 s.**
   - The SP's heartbeat is `vTaskDelay(100000)` ticks, and it prints every 40.10 s in the SP's µs clock. So one tick
     is 401 µs [computed here from the 22 Sep aifoundry2 ring].
   - E10's paired down-steps are 0.4–0.5 s apart, which agrees [data].
4. **The SP learns that a kernel started or ended only at master-minion heartbeats, about 1.05 s apart** [computed here
   from aifoundry3's 22 Sep ring]. This explains E10's 0.39–0.99 s delay before the first clock change.
5. **aifoundry3's 0 W TDP does more than pin the clock: it disables the governor.**
   - The first kernel after boot enters a POWER_DOWN loop that can never exit, so the power task spins for ever
     (`C:tpm:2173-2256,1788-1791`).
   - The first time the mean exceeds 65 °C, the state latches in THERMAL_DOWN and the SP goes silent (`C:tpm:668-679,844-845`).
   - From then on nothing, not even the PMIC safe path, can act.
   - All of this fits what aifoundry3 showed on 22 and 27 September (§4) [inference from source + data].
6. **aifoundry1-c1 (1.2.0) has an inactive governor.**
   - The SP's own per-pass clock minimum and maximum read 600/600 in all 359,657 samples over 15.4 h, including die
     means up to 88 °C [computed here].
   - A live 0.18.0 governor would have stepped the clock to 550 MHz there (`O:tpm:590-602,1769-1779`).
   - Whether active power management is off or the governor is latched cannot be told read-only; §5 gives the one
     query that narrows it.
7. **No firmware path limits die temperature at the bottom operating point.**
   - The PMIC's 75 °C alarm reads the PMIC's own "system temperature" register. That register read 0 in every one of
     281,951 V3 samples on all three cards [computed here].
   - Die means of 103 °C (aifoundry2) and 115 °C (card 0) drew no response (`dfo:29`; `R/docs/findings/14-card-behaviour.md:202-205`).
   - The lab's 90 °C cap is the only real guard.
8. **Three tool findings for tonight** (§9):
   - `sptrace_events.py` stops parsing at the first binary power-status record, and the governor writes one at every
     clock change.
   - `ettelem --reset-ms` silently disables the SP's per-pass statistics trace, and the change persists.
   - At INFO, with a 10 Hz sampler, the 4 KB SP ring holds well under a second of history.

---

## 1. The governor's inputs

### 1.1 Temperature (the same in all three versions)

**Sensors.**
- The firmware defines 5 PVT controllers × 8 sensors (`C:include/bl2_pvt_controller.h:25,30`).
- It enables TS0–7 on PVT0–3 and TS0–2 on PVT4 (`ts_disable_mask` 0x00 and 0xF8, `C:driver/pvt_controller.c:148-154`).
- Minion shire i maps to PVT i/8, TS i%8 (`:650-662`).
- There are 34 minion shires (`PVTC_MINION_SHIRE_NUM 34`, `bl2_pvt_controller.h:80`), and TS 34 is the I/O shire's
  (`:444-445`).
- The PVT driver is identical in `C:`, `O:` and `H:` apart from the licence header (`diff` [computed here]; `HP/firmware.md:68-70`).

**Conversion.**
- Run mode 1 uses fixed G/H/CAL5 = 57400/249400/4096, with no per-die fuse calibration (`bl2_pvt_controller.h:102,162,167,172`).
- The conversion is `(G + (H·N)/CAL5 − H/2) / 1000` in `int` arithmetic, so it truncates to whole °C (`pvt_controller.c:572-590`).
- A sample flagged as a fault returns an error, and the mean leaves it out (`:633-637`, `:1288-1293`).

**The governor's number.**
- `pvt_get_minion_avg_temperature()` sums `current` over shires 0–33 and divides by the valid count in integer
  arithmetic (`:1279-1306`).
- The I/O shire (TS34) is not included.
- The hardware samples continuously, so each call reads the latest conversion (`HP/firmware.md:97-98`).

**Where each version reads it.**
- 0.20.0 and 0.18.0 call it fresh:
  - in the device-management (dm) pass (`C:tpm:656`; `O:tpm:578`);
  - at thermal-loop entry and on every loop iteration (`C:tpm:2308,2357`);
  - at the entry of the power loop (`C:tpm:2152`).
- HEAD compares `g_pmic_power_reg.soc_temperature` (`H:tpm:867`). That variable is written by the pass (`H:tpm:698`)
  **and** by every host `GET_MODULE_CURRENT_TEMPERATURE` (`H:tpm:754`).
- In 0.20.0 the host query also writes `soc_temperature` (`C:tpm:731`), but nothing in the governor reads it
  [source: its only other reader is `dump_power_globals`, `C:tpm:2518-2526`].

### 1.2 Power

- **0.20.0 trigger: the PMIC's instantaneous input power.** Each pass reads the average into `op_stats.system.power.avg`
  (`C:tpm:788-796`), then overwrites the same local with `pmic_read_instantaneous_soc_power()` (`:798-807`). The tests
  at `:862` (`> TDP`) and `:876` (`< TDP`) use the instantaneous value.
- The PMIC registers are `PMIC_I2C_INPUT_POWER_ADDRESS` (instantaneous, `C:driver/pmic_controller.c:1259-1263`) and
  `PMIC_I2C_AVERAGE_PWR_ADDRESS` (average, `:2253-2257`).
- **0.20.0 loop exits: the PMIC average,** re-read every iteration (`C:tpm:2155,2219,2229-2246`).
- **HEAD:** the trigger uses `op_stats.system.power.avg`, the PMIC average (`H:tpm:869-870,898,910`).
- 0.18.0 matches 0.20.0 (`O:tpm:710,720,784,798,2006,2070`).

### 1.3 Thresholds, TDP and active power management (APM)

- **Defaults at boot:**
  - software threshold 65 °C (`TEMP_THRESHOLD_SW_MANAGED`, `C:include/thermal_pwr_mgmt.h:46`);
  - TDP 65 W (`:53`), set in `init_thermal_pwr_mgmt_service()` (`C:tpm:1738-1743`; `H:tpm:1672-1677`);
  - APM on (`C:tpm:1700`; `O:tpm:1601`; `H:tpm:1625`).
- **APM is turned off at boot if the VMIN LUT is invalid** (0.20.0 and HEAD: `C:tpm:1703-1723`; `H:tpm:1628-1648`).
  0.18.0 has no such check (`O:tpm:1596-1634`).
- **Accepted ranges:**
  - TDP accepts 0–75 W and rejects values above `POWER_THRESHOLD_HW_CATASTROPHIC` = 75 (`C:tpm:537-552`;
    `C:include/bl2_pmic_controller.h:267`).
  - The threshold accepts any `uint8` (`C:tpm:599-604`).
  - The APM flag stores any value (`C:tpm:486-491`). The thermal trigger tests it for truth (`:670`); the power branch
    tests `== ACTIVE_POWER_MANAGEMENT_TURN_ON` (1) (`:844`; `API:301-302`).
- All of these live in RAM and are lost at an SP reset.

### 1.4 Whether a kernel is running (MM state)

- The master minion sends `MM2SP_EVENT_HEARTBEAT` carrying `KW_Get_Kernel_State()` (`MM:src/services/sp_iface.c:81-105`,
  `:91`). The SP stores it (`C:rtos_task/command_dispatcher.c:477-481` → `C:tpm:3240-3244`).
- Heartbeats come every `SP_IFACE_MM_HEARTBEAT_INTERVAL(100)` software-timer ticks (`MM:src/services/sp_iface.c:1090`).
  The timer tick is one PU-timer period of 1,000,000 counts (`MM:src/services/sw_timer.c:207`, `:118-147`).
- The source comment says that counter runs at 1 MHz (`MM:include/services/sw_timer.h:29-38`), which would make the
  heartbeat 100 s.
- **The card says about 1.05 s.** In aifoundry3's 22 Sep ring, consecutive state events (throttle-down at a kernel's
  start, idle at its end) are separated by 1.037, 1.044, 1.046, 1.050 and 1.063 s, or by 2.100 and 2.129 s. The one
  exception is 0.78 s, which is one pass short [computed here: `W/tools/claims-v3/hp/sptrace_events.py events
  R/docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin`].
- *Inference:* the PU timer counts at about 95 MHz, not 1 MHz. Either way, the SP sees a kernel start or end only at
  the next heartbeat plus up to one pass. That is 0–1.05 s plus up to 0.13 s on aifoundry2, which matches E10's
  "first change 0.39–0.99 s after launch" (`R/docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`
  `.transition_summary.first_change_s`).
- HEAD guards `mm_state` with a mutex and reacts to busy→idle directly (`H:tpm:160-164,3110-3124`).

---

## 2. The 0.20.0 governor (aifoundry2 and aifoundry3), exactly

### 2.1 States and tasks

**States** (`API:285-291`): POWER_IDLE 0, THERMAL_IDLE 1, POWER_UP 2, POWER_DOWN 3, THERMAL_DOWN 4, POWER_SAFE 5,
THERMAL_SAFE 6. They live in `g_soc_power_reg.power_throttle_state` (`C:tpm:181`).

**Three code paths write the state:**
- **The dm task.** Every pass it runs the temperature update, the PMB stats, the power update (which holds the power
  branch), the frequencies and the other statistics. It then logs the operating-point stats and sleeps
  `pdMS_TO_TICKS(DM_TASK_DELAY_MS=10)` (`C:rtos_task/dm_task.c:199-276`; `C:include/config/mgmt_build_config.h:432`).
- **The power-management task** (`TT_TASK`) waits for a notification, reads the state and runs one handler
  (`C:tpm:2404-2458`).
- **The PMIC interrupt callback** (`C:tpm:2480-2497`).

Both tasks run at priority 2 (`mgmt_build_config.h:430,434`), with preemption on (`FreeRTOSConfig.h:92`). Time
slicing is the FreeRTOS default [inference: the config does not set `configUSE_TIME_SLICING`].

**Measured pass time with nothing polling:** 133 ms on aifoundry2, 135 ms on card 1, 224 ms on aifoundry3.
- A 10 Hz sampler lengthens it to 159–162, 162 and 266 ms (`dvfs.json .v3.sp_pass_ms`).
- Most of the pass is busy-waiting in I2C transfers (`US_DELAY_GENERIC(1000)`, `C:driver/i2c_controller.c:244,325`).

### 2.2 Every transition, with its line

| Where | Condition | Action | Source |
|---|---|---|---|
| dm pass | `T > sw_thr` **and** `state < THERMAL_DOWN` **and** APM true. **No MM-state test** | log CRITICAL `Thermal throttle down event, current temperature: T, threshold: 65`; `state = THERMAL_DOWN`; notify | `C:tpm:668-679` |
| dm pass (power branch) | gate: `APM == 1` **and** `state < THERMAL_DOWN` | — | `C:tpm:844-845` |
| ↳ | MM idle and `state != POWER_IDLE` | CRITICAL `Power idle state event, current pwr P_mW  tdp level TDP_mW`; `state = POWER_IDLE` | `:848-860` |
| ↳ | MM busy, `P_inst > TDP` and `state < POWER_DOWN` | CRITICAL `Power throttle down event, current pwr …  tdp level: …`; `state = POWER_DOWN` | `:862-873` |
| ↳ | MM busy, `P_inst < TDP` and `state < POWER_UP` | CRITICAL `Power throttle up event, …`; `state = POWER_UP` | `:876-887` |
| power task | on wake, if `state` changed | INFO `Power Throttle event received. throttle_state: N`, then dispatch | `:2414-2456` |
| THERMAL_DOWN | `thermal_throttling(4)`: while `T > 65` **and** `state ≤ 4`, reduce one LUT point, `vTaskDelay(pdMS_TO_TICKS(1000))`, re-read T | on exit (if `state ≤ 4`): `state = THERMAL_IDLE`, CRITICAL `Thermal idle state event, current temperature T, threshold 65`; THERMAL_DOWN residency += duration | `:2289-2383` (loop `:2316-2361`, delay `:2354`, exit `:2366-2374`, residency `:2382`) |
| THERMAL_IDLE or POWER_IDLE | `power_throttling(POWER_IDLE)` → `go_to_idle_state()` | clock to `vmin_lut[0]` (the boot point) | `:2446-2449,2190-2196,1975-1979`; `C:driver/flashfs.c:2162-2165` |
| POWER_UP | loop with **no delay**: increase one point, re-read the PMIC **average**; exit when `avg > TDP` or the clock is at the LUT maximum | climbs to the top in one call | `:2173-2236` |
| POWER_DOWN | loop with no delay: reduce one point, re-read the average; exit when `avg < 1.05·TDP` (68.25 W) or the clock == 300 MHz | may spin at the bottom point (§4) | `:2238-2246`; macro `:289` |
| PMIC interrupt | over-temperature or over-power bit | `state = THERMAL_SAFE` or `POWER_SAFE`; notify | `:2480-2497` |
| THERMAL_SAFE | `go_to_safe_state()`, then **return** without clearing the state | terminal (§6) | `:2302-2306` |
| POWER_SAFE | `power_throttling(POWER_SAFE)` | terminal (§6) | `:2147-2150,2198-2203,2238-2246` |

**Consequences:**
- **Priority.** Nothing the dm task writes can leave states 4, 5 or 6: every dm-task write requires `state < 4`
  (`:669,845`). Only the thermal loop's exit (`:2366-2368`) returns 4 → 1. **Nothing returns 5 or 6**; the full writer
  list is at `C:tpm:678,858,871,885,1699,2368,2486,2490` (`grep`).
- **Latch paths into THERMAL_DOWN** [source; the consequence is inference]:
  - (a) the power task never gets to run `thermal_throttling` (§4);
  - (b) a failure inside the loop:
    - a PMIC read error `return`s at `:2324-2329`;
    - so does a failed operating-point change at `:2335-2341`;
    - either one leaves the state at 4 with no exit line and no residency update.
- **No hysteresis.** Entry is `> 65` (`:668`) and exit `≤ 65` (`:2316`). The only damping is the loop period.
- **The thermal loop blocks everything else.** While it runs, the power task sleeps inside it and the dm task is gated
  out, so no step-up, idle or power event can happen until the mean reads ≤ 65 at a loop check. Only a PMIC
  interrupt changes the state (`:2317`).

### 2.3 Operating-point changes

**Steps.**
- Up and down move to the next or previous entry of the flash VMIN LUT that equals the current frequency
  (`C:tpm:1899-1954`; `C:driver/flashfs.c:2370-2404`).
- At index 0 the "previous" point is the same frequency (`flashfs.c:2396-2397`).
- If the current frequency is not in the LUT, both steps log ERROR `Failed to find input frequency in vmin lut` and
  keep the clock (`C:tpm:1906-1911,1945-1950`).
- aifoundry2's points are 600/700/800 MHz at 0.517/0.568/0.618 V (`dvfs.json .operating_points`).

**`set_minion_operating_point()`** (`C:tpm:1781-1877`):
- It returns `STATUS_SUCCESS` without acting when the new frequency equals the current one (`:1788-1791`).
- It rounds to 25 MHz (`:1794-1797`).
- It sets the minion voltage and then the L2 voltage **before** the PLL, in both directions (`:1801-1840`).
- It then programs the PLL (`:1842-1862`) and updates the frequency register (`:1863`).
- It writes a binary `TRACE_TYPE_POWER_STATUS` record (`:1868`).
- It logs CRITICAL `new OP: Freq %d MNN voltage %d SRM voltage %d` (`:1870-1875`).
- **So every real clock change leaves two trace entries, whatever the log level.** The string is CRITICAL; the binary
  record is not gated by the event mask (`ET:encoder.h:917-929`).

**The frequency register** that `Get_Minion_Frequency()` reads (`C:services/perf_mgmt.c:232-235`) has three writers:
- the governor (`:256-259`);
- the PLL helpers (`C:driver/minion_configuration.c:424,722`);
- **every host `DM_CMD_GET_ASIC_FREQUENCIES`**, which re-reads the PLL (`perf_mgmt.c:281-292`).

### 2.4 Timing

**FreeRTOS tick.**
- The config assumes a 4 MHz `mtime` and 1000 Hz ticks (`FreeRTOSConfig.h:95-96`), so one tick is 4000 raw counts.
- The SP µs timer divides raw counts by 10 when SP PLL0 runs at 1000 MHz, the "100 %" setting (`C:driver/timer.c:28-42,120-129`).
- The heartbeat `vTaskDelay(100000)` (`C:common/main.c:471-476`; `MAIN_DEFAULT_TIMEOUT_MSEC 100000`,
  `mgmt_build_config.h:415`) appears every **40.10 s** in the trace's µs timestamps. Twelve intervals read 40.000–40.116 s
  (`R/docs/reports/data/2026-09-22-cards/sptrace-aifoundry2.bin`; one more in `V3 raw/aifoundry2/tel/p3/gov/sp1.bin`)
  [computed here].
- So **1 tick = 401 µs of SP time**, and PLL0 is at 100 %.

**Derived periods:**
- the thermal loop's `vTaskDelay(1000)` is **0.40 s** plus the loop body;
- `DM_TASK_DELAY_MS` is 4 ms.

**Independent check on host time [data]:** E10's thermal pairs (800→700 then 700→600) are 0.4–0.5 s apart at a 10 Hz
sampler: transitions 9→10, 12→13, 15→16, 18→19, 21→22, 27→28 and 31→32 in `dvfs.json .transitions[].t`.

What is not established: whether the SP's µs is a true µs. That needs a fit of SP timestamps against host times.

### 2.5 What the E10 transitions look like under this machine

The 36 transitions are in `dvfs.json .transitions` [data]. Their numbering is used below.

- **Every 600→700 up-step is followed by 700→800 one sample (0.1 s) later.** There are five such pairs: 3→4, 7→8,
  23→24, 25→26 and 29→30. The clock never stays at 700 on the way up: this is the POWER_UP loop caught mid-climb
  (`C:tpm:2173-2236`).
- **Down-steps come in pairs 0.4–0.5 s apart**, which is one loop period. The second step is either:
  - a reduce, if the mean is still > 65; or
  - the **exit to the boot point**, if the mean is ≤ 65.
- **The six "unattributed (reading ≤ 65 °C)" steps** at 64–65 °C (18, 19, 21, 22, 27, 28) are what the exit predicts:
  - 700→600 at a mean of 65 is the loop's return to `vmin_lut[0]`;
  - an immediate 600→800 follows on the next pass when a kernel runs: 19 → 20 after 0.1 s, 22 → 23/24 after 0.1–0.2 s.
- **The 800→600 single steps:**
  - Step 2 (64 °C, 39 W) is either an MM-idle reset or a thermal loop that found the mean ≤ 65 on its first re-read
    and exited straight to the boot point.
  - Step 6 (87.5 W) is the POWER_DOWN loop stepping twice within one sample [inference].
- **34→35→36** (800→700→600 within 0.1 s at 87.8 W) is the POWER_DOWN loop stepping with no delay.

This replaces `dvfs-leakage.body.html:205`, "The 353f20e source does not explain that", and the "unattributed"
reading, with a source-level explanation [inference, consistent with every transition].

---

## 3. HEAD (`353f20e` ≡ `836a4ab`), the governor the pages describe

- **One function per pass,** `check_power_throttle_conditions()` (`H:tpm:864-926`), called from the dm task
  (`H:rtos_task/dm_task.c:267`). Its inputs:
  - `T = soc_temperature` (`:867`);
  - `P = PMIC average` (`:869-870`);
  - the clock and the LUT minimum and maximum (`:872-874`).
- **The whole governor requires `APM == ON` and the master minion busy** (`:879-880`). An idle die gets no thermal
  response at all.
- **Test order** (`:884-920`):
  - `T > 65` and `f > f_min`: request POWER_DOWN (logs a thermal line);
  - else `P > TDP` and `f > f_min`: request POWER_DOWN;
  - else `P < TDP` and `f < f_max`: request POWER_UP.
  - At `f_min` the power tests are skipped while `T > 65`, and nothing is logged.
- **One LUT point per request, and a request can come every pass.** There is no thermal loop and no `DELTA_TEMP`
  delay; `DELTA_TEMP_UPDATE_PERIOD` is defined but unused (`H:include/thermal_pwr_mgmt.h:86`; `grep`). The guard bands
  are defined and unused (`H:tpm:217,223`).
- **Operating-point changes:**
  - Up: voltage first, then frequency. Down: frequency first, then voltage (`H:tpm:1813-1849`).
  - Each change logs CRITICAL `New OP: …` (`:1858-1863`) and writes a power-status record (`:1856`).
- **The power task takes requests as notification bits,** with priority SAFE > IDLE > DOWN > UP. It ignores DOWN while
  in SAFE, and it can step up out of SAFE (`H:tpm:2244-2279,1937-1941`).
- **Idle:** the master minion's busy→idle transition logs INFO `Power idle state event` with no numbers and requests
  POWER_IDLE (`H:tpm:3114-3120`).
- **PMIC interrupt:** POWER_SAFE (`H:tpm:2317-2323`). The safe state really sets 300 MHz (`H:tpm:2007-2010`).
- **TDP 0 under HEAD:** the clock steps down to `f_min` and then stops logging. Nothing spins and nothing latches
  (`:898-899`).

**The trace strings on the cards are the 0.20.0 strings**, not HEAD's:
- aifoundry3's 22 Sep ring prints `Power idle state event, current pwr 26030  tdp level 0`, with numbers, at CRITICAL
  (`C:tpm:853-855` vs `H:tpm:3117`).
- The same ring prints `Power throttle down event, current pwr 35380  tdp level: 0` in mW (`C:tpm:866-868`)
  (`R/docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin`).

**What the pages get wrong for the cards** (DVFS page §1 pseudocode, `dvfs-leakage.body.html:88-101`;
`R/docs/findings/16-dvfs-and-leakage.md:31-48`):
1. The card's thermal trigger does not require a busy master minion.
2. The card's power trigger is instantaneous; the page says average (the page's §8 already notes this).
3. The card's thermal response is a loop with a 0.4 s step and an exit to the boot point; the page says one point per
   pass.
4. The card's climb goes to the top in one call; the page says one point per pass.
5. The card's safe state is terminal and cosmetic (§6).
6. A zero TDP latches the card's governor (§4); under HEAD it would merely pin the clock.

The hub's caveat "the older source has not been re-read" (`limits-of-observability.body.html:330`) is now out of date.

---

## 4. What a 0 W TDP does on 0.20.0 (aifoundry3)

The lab service sends `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL 0` and then `DM_CMD_SET_FREQUENCY 600,400` at every boot
(`R/docs/reports/data/2026-09-25-aifoundry1/facts.md:205-213`). What follows is read from source; the last column
says what has been seen.

| Step | Source | Seen on the card |
|---|---|---|
| Every pass: `P_inst > 0` → power state `MAX_POWER` | `C:tpm:839,300-303` | `ettelem config` → `max_power` (`HP/dev/aifoundry3/hp/p801/config.json`) |
| First kernel: MM busy, `P > 0`, `state < 3` → CRITICAL `Power throttle down`, `state = POWER_DOWN` | `:862-873` | 26 such lines on 22 Sep |
| Power task: reduce at 600 MHz = `vmin_lut[0]` → same frequency → returns success without acting | `:1899-1914`; `flashfs.c:2396-2397`; `:1788-1791` | — |
| Exit test `avg < 1.05 × 0` or `f == 300` is never true, so **the power task spins for ever**, doing an I2C PMIC read each iteration | `:2219,2238-2246` | aifoundry3's pass is 224 ms against 133 ms on aifoundry2, same release (`dvfs.json .v3.sp_pass_ms`) [consistent with an equal-priority task spinning; not proof] |
| Kernel end: MM idle, `state != 0` → CRITICAL `Power idle state event`, `state = 0`. The power task never services it | `:848-860` | down/idle lines alternate, 27 idle and 26 down, **no `event received` or `new OP` line** (`dvfs.json .sptrace_events`) |
| The mean first exceeds 65 °C (idle or busy) → CRITICAL `Thermal throttle down`, `state = 4` | `:668-679` | not in any committed ring (22 Sep die at 55.8 °C) |
| From then on every dm write needs `state < 4` → **latched: no governor line of any kind, ever** | `:669,845` | 27 Sep R0 probe: at 53 °C, INFO level, one 2 s launch, no sampler → **0 new entries** (`HP/dev/aifoundry3/hp/p801/class.json`); all dev dumps show host lines only (`p801/p0.bin`, `p1.bin`, `p901/sp-1.bin`) [computed here] |
| A PMIC interrupt sets 5/6 and notifies, but the spinning loop never checks → **the safe path is dead too** | `:2173-2256,2480-2497` | — [inference] |
| The clock stays at 600 MHz whatever the temperature | — | 600 MHz in all 62,053 dev samples, means up to 68 °C (`HP/dev/aifoundry3/hp/p*/tel-*.jsonl.gz`) [computed here]; 600 MHz up to a 90 °C mean in V3 (`dfo:3,14-16`) |

**For experiment design:**
- aifoundry3 is a **fixed-clock control with a dead governor.** Its clock does not depend on temperature, and it
  answers nothing about the trigger.
- The "STUCK vs LATCHED" question in `HP/DESIGN2.md:280` is settled for the current boot: aifoundry3 was taken past
  65 °C many times on 27 Sep (`HP/dev/queue-hp-aifoundry3*.log`, "first66 +…").
- One read-only confirmation remains: throttle residency (§7.2). The prediction is POWER_DOWN = 0 and THERMAL_DOWN = 0
  since boot, because neither loop has ever exited.

---

## 5. What differs on 1.2.0 (aifoundry1-c1, BL2 0.18.0)

**What is the same:**
- the trigger (`O:tpm:590-602`);
- the power-branch gate (`:766-767`) and the idle, down and up branches (`:770,784,798`);
- the thermal loop (`:2139-2232`: loop `:2166`, delay `:2204`, exit `:2218-2224`, residency `:2232`);
- the task and the interrupt callback (`:2254`, `:2330-2347`);
- the constants 65 °C, 65 W, 1000 ticks and the 5 % guard band (`O:include/thermal_pwr_mgmt.h:75,82,100,106`).

**What differs:**
- **Steps are fixed at 50 MHz, clamped to 300–700 MHz** (`O:include/thermal_pwr_mgmt.h:56-58`; `O:tpm:1769-1811`).
  The clock can never reach 800 MHz, and the loop exits compare against these constants (`:2081-2082,2092`).
- **The voltage is computed linearly from the boot point** in steps (`O:driver/minion_configuration.c:1030-1056`), not
  read from a LUT.
- **There is no VMIN-LUT validation,** so APM is on at every boot (`O:tpm:1596-1634`).
- **The safe state really changes the PLL to 300 MHz** whenever the clock is elsewhere (`O:tpm:1858-1885`, test at `:1867`).

**What the card shows [computed here, from `R/docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1/**/*.jsonl.gz`]:**
- `sp.minion_mhz` min/max = **600/600 in all 359,657 samples**, from `t_ms` 1790384302898 to 1790439730055 (15.4 h).
- That field is the minimum and maximum of the frequency register at every dm pass since the last statistics reset
  (`C:tpm:912-918`). It therefore catches any change that lasts one pass (135 ms), and a thermal step would last at
  least 0.4 s.
- Over the same period:
  - `dfo:5`: 14,295 busy samples at ≤ 65 °C, of which 11,446 were at 45–63 W. A live governor would have stepped up to
    650/700 MHz there.
  - `dfo:18-20`: means up to 88 °C. A live governor would have stepped down to 550 MHz or lower.
  - `dfo:18`: board readings up to 86.13 W, with no 300 MHz safe state either.

**So the governor on card 1 is inactive.** The source leaves two candidates:
- (a) APM is off, set by some host (no log line is written for it: `C:services/thermal_power_monitor.c:99-124` has
  only an error log);
- (b) the state latched ≥ 4 early after boot, through the thermal loop's error returns (`O:tpm:2163,2178,2190`).

The pass time (135 ms, like aifoundry2) rules out a spinning power task [inference]. It does not decide between (a) and
(b).

**The one read-only discriminator:** the POWER_UP throttle residency since boot (§7.2).
- More than 0 means the governor climbed at least once after boot, so it was alive and has been disabled since.
- 0 means it never climbed since boot, which fits APM off from the start.

---

## 6. Every other path that can change the clock, and the hardware trip

**Master minion idle.** Only through the power branch, so only while `state < 4` (`C:tpm:848-860`). Its target is
`vmin_lut[0]` (`flashfs.c:2162-2165`).

**The PMIC alarm.**
- `setup_pmic()` writes the PMIC's temperature alarm = 75 °C and power alarm = 75 W (encoded `75 << 2`), and enables
  all PMIC interrupts (`C:driver/pmic_controller.c:480-516`, `:490,493,496`; constants at
  `C:include/bl2_pmic_controller.h:267,272`; called at `C:common/main.c:152`).
- The allowed temperature range is 55–75 (`pmic_controller.c:1201-1212`; `bl2_pmic_controller.h:277,282`).
- The interrupt service routine (ISR) calls the governor callback and sends the host a FATAL/UNCORRECTABLE `PMIC_ERROR`
  event (`pmic_controller.c:699-731`).
- The temperature the PMIC reports is `PMIC_I2C_SYSTEM_TEMP_ADDRESS` (`:1234-1236`). The source itself says "PMIC is
  currently reporting system temperature as 0" (`C:tpm:2995`).

**What the cards show [computed here]:**
- `sp.system_c[0]`, the PMIC temperature captured at each statistics reset (`C:tpm:2996-3001`), was **0 in all V3
  samples:** 93,605 on aifoundry2, 82,001 on aifoundry3 and 106,345 on card 1 (also `dfo:2,4,6`).
- If the PMIC's alarm compares that same register, **it can never fire on temperature** [inference].
- No response was seen at:
  - a 103 °C mean and a 106 °C hottest sensor on aifoundry2 at 600 MHz (`dfo:29`);
  - 115–117 °C on card 0 (`R/docs/findings/14-card-behaviour.md:202-205`).
- Board readings of 86–88 W (card 1 `dfo:18`; aifoundry2 E10 `dvfs.json .transitions[35].P`) did not trip the 75 W
  alarm into a visible safe state either. On card 1 a trip would have shown as 300 MHz (`O:tpm:1867-1885`).
- *Inference:* the power alarm uses a slower average or different units. It is not established.

**0.20.0's safe state is terminal and cosmetic.**
- `Minion_Get_Voltage_Given_Freq(300)` always succeeds, because the voltage is hard-coded
  (`C:driver/minion_configuration.c:1020-1037`).
- So `go_to_safe_state()` skips the PLL change, whose guard is `status != SUCCESS` (`C:tpm:2016`). It then sets the
  frequency register to 300 anyway (`:2034`).
- The state stays 5 or 6 for good (§2.2).
- A host `GET_ASIC_FREQUENCIES` then rewrites the register from the PLL (`perf_mgmt.c:285-292`).
- *Inference:* on 0.20.0 a PMIC alarm would freeze the governor at whatever clock it had, while briefly reporting
  300 MHz.

**Host commands.** Set out in §8.

**No per-sensor or maximum-temperature path:**
- `max_temp` is never assigned in `C:`, `O:` or `H:`; the only writes found are reads such as `C:tpm:1347` (`git grep "max_temp\s*="`).
- The PVT driver configures only the disable masks (`C:driver/pvt_controller.c:367-377`) and never enables any
  temperature-sensor interrupt (`grep -i irq` finds only the voltage-monitor high/low register names).
- The hottest sensor (`minshire_high`) is returned to the host only (`C:tpm:733`).

---

## 7. What the host can read

### 7.1 `ettelem` fields → governor variables (0.20.0)

`R/tools/ettelem/ettelem.cpp:119-175`; the handlers are in `C:services/thermal_power_monitor.c`,
`C:services/performance.c:412-442` and `C:services/perf_mgmt.c:281-292`.

| Field | Command | What it is | Governor relevance |
|---|---|---|---|
| `board_w` | `GET_MODULE_POWER` (33) | `g_pmic_power_reg.soc_pwr_10mW`: the **instantaneous** PMIC input power from the **last dm pass** (`C:tpm:805,949-953`; `thermal_power_monitor.c:147-170`) | **exactly the 0.20.0 power-trigger input** |
| `sp.board_avg_w` | `GET_SP_STATS` (60) | `op_stats.system.power.avg` = the PMIC average read that pass (`C:tpm:795`) | the loop-exit input (read fresh inside the loop) |
| `sp.board_min_w`, `max_w` | GET_SP_STATS | min and max of the instantaneous power over passes since the last reset (`:806`) | peak-power check |
| `sp.minion_c` | GET_SP_STATS | `[5-sample cumulative moving average, min, max]` of **the governor's own mean at each pass** since the reset (`:660-661`, `:318,331-346`) | `max ≥ 66` within a window means the SP itself read a trip value on some pass. **Better aligned with the trigger than `temp_c.minshire[0]`** |
| `sp.minion_mhz` | GET_SP_STATS | `[current, min, max]` of the frequency register at each pass since the reset (`:912-918`) | catches any clock excursion of one pass or longer, even between 10 Hz samples |
| `sp.system_c` | GET_SP_STATS | the PMIC temperature at the reset, then `CALC_MIN_MAX(…,0)` (`:664,2996-3001`) | reads 0 (§6) |
| `temp_c.minshire` | `GET_MODULE_CURRENT_TEMPERATURE` (27) | `[mean, lowest low-water, highest high-water]`, read **fresh at query time** (`C:tpm:724-735`; `pvt_controller.c:1308-1345`); the high and low marks run since the last `pvt_hilo_reset` (`C:tpm:2986`) | the same function as the governor's, at a different instant |
| `temp_c.pmic` | same | the mean again (`C:tpm:714-722`) | — |
| `temp_c.ioshire` | same | TS34 `[current, low, high]` (`:737-747`) | not in the mean |
| `mhz.minion` | `GET_ASIC_FREQUENCIES` (53) | the PLL, which **also rewrites the governor's frequency register** (`perf_mgmt.c:285-292`) | the only direct clock reading |
| `die_mv`, `reg_mv` | `GET_ASIC_VOLTAGE` (32), `GET_MODULE_VOLTAGE` (31) | PVT voltage monitors; PMIC set-points | the voltage tracks the step |
| `config` | `GET_MODULE_STATIC_TDP_LEVEL` (25), `GET_MODULE_TEMPERATURE_THRESHOLDS` (21), `GET_MODULE_POWER_STATE` (23) | TDP; `sw_temperature_c`; the power state from `GET_POWER_STATE` of the instantaneous power | the static configuration; **the throttle state itself is not readable** |

`--reset-ms` sends `SET_STATS_RUN_CONTROL {type 1, control 2}` (`ettelem.cpp:61-67`). That runs
`Thermal_Pwr_Mgmt_Init_OP_Stats()`, which does four things (`C:services/performance.c:578-581`; `C:tpm:2963-3043`):
- it resets `op_stats`;
- it resets the PVT high and low marks (`:2986`);
- it resets the PMIC's PMB statistics (`:3004`; `pmic_controller.c:1708-1713`);
- it re-seeds the averages.

On 0.20.0 none of these is a governor input. Whether the PMB reset also restarts the average `pmic_read_average_soc_power()`
returns, which the 0.20.0 loop exits read, is not established.

### 7.2 Reads that no tool issues yet (all read-only)

**`DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES` (29)** (`API:77`; handler `C:services/thermal_power_monitor.c:601-628,991-996`;
getter `C:tpm:1548-1579`).
- It takes a raw state number and returns `residency_t {cumulative, average, maximum, minimum}` in SP µs
  (`APIr:102-109,722-736`).
- The residency is updated **only when a loop exits:**
  - THERMAL_DOWN at the thermal loop's exit (`C:tpm:2382`);
  - POWER_UP, POWER_DOWN and POWER_SAFE at the power loop's exit (`:2267`, via `:1442-1465`).
- It accumulates since boot; nothing resets it.
- **Use it for the governor's state:**
  - THERMAL_DOWN cumulative grows by the length of each completed thermal episode. On aifoundry2 this gives the total
    time spent in the loop between two queries, with no log-level change.
  - It stays 0 on a latched card.
- Caveat: HEAD's enum is different (`H: device-api …spec.h:280-285`), so a HEAD-built CLI may refuse state 4. Send the
  raw number with `serviceRequest`.

**The SP statistics trace buffer.**
- Every dm pass writes a `TRACE_CUSTOM_TYPE_SP_OP_STATS` record: the whole `op_stats`, 128 B plus a header, with an SP
  µs timestamp (`C:rtos_task/dm_task.c:272,301-318`; `ET:layout.h:484-500`).
- The buffer is 1 MB and restarts from the top when full (`H:et-common-libs/include/system/layout.h:283`;
  `ET:encoder.h:566-572`). That is about 7,000 passes, 15 minutes at 133 ms [inference].
- It is exposed as a management-accessible region (`C:config/dir_regs.c:203-212`).
- The host reads it with `getTraceBufferServiceProcessor(…, TraceBufferSPStats)` (`H:devicelayer/include/device-layer/IDeviceLayer.h:129-135`)
  → `ETSOC1_IOCTL_EXTRACT_TRACE_BUFFER` (`DRV:1021-1045`). That is a plain read of a PCIe BAR region; the SP writes no
  log line and no state changes.
- It gives **a per-pass record of the clock, the governor's mean statistics and the power, with SP timestamps**, so
  each step can be timed to the pass without a sampler loading the SP.
- It is enabled at boot (`ET:encoder.h:668`), but every `ettelem --reset-ms` has **disabled** it (§9.2). Untested on a
  card.

**`DM_CMD_GET_MODULE_UPTIME` (30)** is an SP-clock versus host-clock anchor (`C:services/thermal_power_monitor.c:703-750`).

### 7.3 The SP trace ring (`ettelem sptrace`)

**What it is.**
- A 4 KB ring (`H:et-common-libs/include/system/layout.h:268-269`), with µs timestamps (`C:services/trace.c:44`).
- Its default filter at boot is WARNING (`trace.c:279-280`).
- The level can be set through `DM_CMD_SET_DM_TRACE_CONFIG` (67) (`trace.c:188-210,479-482`).
- **V3 left all three cards at INFO**, and tonight's probes found INFO on aifoundry2 and aifoundry3
  (`HP/dev/aifoundry3/hp/p801/class.json`; `W/build/claims-v3/aifoundry2/hp/a2/p1/probe/class.json`).

**Governor lines** (`C:tpm`):

| Line | Level | Source |
|---|---|---|
| `Thermal throttle down event, current temperature: %u, threshold: %d` | CRITICAL | `:673-675` |
| `Thermal idle state event, current temperature %u, threshold %u` | CRITICAL | `:2371-2373` |
| `Power idle state event, current pwr %u  tdp level %u` | CRITICAL | `:853-855` |
| `Power throttle down event, current pwr %u  tdp level: %u` | CRITICAL | `:866-868` |
| `Power throttle up event, …` | CRITICAL | `:880-882` |
| `new OP: Freq %d MNN voltage %d SRM voltage %d` | CRITICAL | `:1870-1875` |
| binary `TRACE_TYPE_POWER_STATUS` (throttle state, power state, power in W, mean T, target f and V) | — | `:1868`; `ET:layout.h:399-426` |
| `Power Throttle event received. throttle_state: %d` | INFO | `:2421-2422` |
| `Failed to find input frequency in vmin lut…` | ERROR | `:1908,1947` |
| `…%d failed to set operating point` (the latch path) | ERROR | `:2337-2339` |
| `…Update module tdp level threshold to new level: %d` | INFO | `:546-548` |
| `SP Alive..` every 100,000 ticks | INFO | `main.c:473` |

- `DM_CMD_SET_THROTTLE_POWER_STATE_TEST` (36) writes one power-status record with the SP's current mean and PMIC
  average, and changes nothing else (`C:tpm:2087-2112`). **It is a marker that records the SP's own reading at a host-chosen
  instant.**
- **Capacity at INFO with a sampler:** every `ettelem sample` issues six commands, and each adds 2–4 INFO lines
  (`Host_Iface`, `pc_vq_process_pending_command`, the service's request and response lines). The V3 dumps hold 44–48
  host lines in the whole ring (`R/…/claims-v3/raw/*/tel/p*/gov/sp*.bin`) [computed here]. So **at 10 Hz the ring
  covers about 0.4–1 s** [inference], and any governor line older than that is overwritten.
- Trace dumps are BAR reads and add no lines (the R0 probes' `new_entries: 0`).
- **Not readable at all:** the throttle state, per-sensor temperatures, which sensor is hottest, and `max_temp`, which
  is never assigned (§6).

---

## 8. What the host can set, and whether any user can

Every command below travels over `/dev/et*_mgmt`, which is mode 0666 (`R/docs/findings/14-card-behaviour.md:199-200`).
The driver has no capability check on any management ioctl (`grep capable DRV:` finds nothing) [source]. **So any
logged-in user can send any of these; only the lab rules stop them.** Everything lives in RAM and returns to its
default at an SP reset.

| Command (API #) | Effect on 0.20.0 | Limits | Source |
|---|---|---|---|
| `SET_MODULE_TEMPERATURE_THRESHOLDS` (22) | `sw_temperature_c` = any `uint8` | none | `thermal_power_monitor.c:498-526,981-985`; `C:tpm:599-604` |
| `SET_MODULE_STATIC_TDP_LEVEL` (26) | TDP (W) | 0–75 | `:397-441,971-975`; `C:tpm:537-552` |
| `SET_MODULE_ACTIVE_POWER_MANAGEMENT` (24) | APM flag, any value; 0 turns both branches off | none | `:99-124,752-759`; `C:tpm:486-491,670,844` |
| `SET_FREQUENCY` (37) | programs the minion or NoC PLL directly, with no voltage change; the governor's register follows | the mode must exist | `:875-925`; `minion_configuration.c:424,1213-1222` |
| `SET_MODULE_VOLTAGE` (35) | sets a rail directly | PVT check only | `:299-321` |
| `SET_DM_TRACE_CONFIG` (67) | the SP log level | 0–4 | `C:services/trace.c:188-210` |
| `SET_DM_TRACE_RUN_CONTROL` (66) | enable, disable or reset the SP ring | — | `trace.c:131-186,470-473` |
| `SET_STATS_RUN_CONTROL` (62) | reset statistics; **enable or disable the SP statistics trace** | — | `C:services/performance.c:551-615` |
| `SET_THROTTLE_POWER_STATE_TEST` (36) | one trace marker | — | `C:tpm:2087-2112` |

To un-latch a governor you have to reset the SP. No command clears the state, and a card reset is forbidden by the
owner's rules.

---

## 9. Findings that affect tonight's tools

### 9.1 `sptrace_events.py` stops at the first power-status record

- The ring walker `break`s on the first entry that is not a string (`W/tools/claims-v3/hp/sptrace_events.py:75-85`).
- `_entry_at` requires a payload that is a multiple of 8 and holds printable text (`:61-72`).
- A power-status record is 16 + 12 = 28 bytes with `payload_size` 12 (`ET:layout.h:321-326,399-426`; `ET:encoder.h:917-929`).
  String entries are padded to 8 (`ET:encoder.h:750`), so everything after a power-status record is also 4 bytes out of alignment.
- **So on any card whose clock moves (aifoundry2 from a cool start), the parse loses every entry newer than the first
  clock change.** The `new OP` string is not in `PATTERNS` either (`:41-51`).
- It has not shown yet, because no committed ring contains a clock change. The encoder layout is HEAD's, so check it
  against a real dump before relying on it.
- **Fix:**
  - walk by `payload_size` using the header's `type` field; the 4 bytes the parser treats as unused are
    `hart_id` (u16) and `type` (u16), per `ET:layout.h:321-326`;
  - decode `TRACE_TYPE_POWER_STATUS`;
  - add `new OP`.

### 9.2 `ettelem --reset-ms` turns off the SP statistics trace

- `performance.c:562-569` enables the statistics trace only when `control & STATS_CONTROL_TRACE_ENABLE` (1) is set, and
  otherwise **disables** it (`API:443-446`).
- ettelem sends `control = 2` (`R/tools/ettelem/ettelem.cpp:62`; the same in `W/tools/claims-v3/hp/ettelem-hp/ettelem.cpp:70`).
- So every V3 and heat run with `--reset-ms` has left that trace disabled on every card. The boot default is enabled
  (`ET:encoder.h:668`).
- This is a global-state change that was never restored. It is trace-only and has no governor effect.
- **Fix:** send `control = 3`, which keeps the boot default. The same logic is in `O:` and `H:` (`H:…/performance.c:557-564`).

### 9.3 The ring at INFO

With the sampler running, CRITICAL governor lines survive less than about a second (§7.3). Two ways to keep them:
- run trace-based tests with **no sampler** and dump at most every 30 s, since only `SP Alive..` adds lines;
- or set WARNING and restore INFO afterwards (O2, only where allowed).

---

## 10. What the cards' behaviour shows, in one table

| Observation | Source | What it means under 0.20.0 |
|---|---|---|
| aifoundry2 rests at 66–80 °C; 73 °C after 20.6 h idle | `dvfs.json .idle_check`; `dfo:10-12`; a2 attempts rest 67 and 66 (`HP/a2-session1.log`, `a2-session2.log`) | above 65 at the SP, the governor sits in the thermal loop at 600 MHz with no lines; every launch runs at 600 |
| aifoundry2 R0 probe: SILENT, 0 new entries, INFO, rest 67 °C | `W/build/claims-v3/aifoundry2/hp/a2/p1/probe/probe.json` | LOOP: the loop blocks the power branch, so a launch adds no line (`C:tpm:845`) |
| Both a2 attempts WARM | `a2.json`; `a2-session2.log` | an on-card trigger test needs aifoundry2's mean to fall to ≤ 64 |
| E10: 36 transitions, climbs in one go, down-pairs 0.4–0.5 s apart, 6 "unattributed" at 64–65 °C | `dvfs.json .transitions` | the thermal loop, the exit to the boot point and the one-call climb (§2.5) |
| First change 0.39–0.99 s after launch; the idle reset 0.5–1.4 s after the host sees the kernel end | `dvfs.json .transition_summary`; `R/…/claims-v3/PLAN3.md:180` | the MM heartbeat, about 1.05 s, plus a pass (§1.4) |
| aifoundry3: down/idle alternation on 22 Sep, SILENT on 27 Sep, 600 MHz always, pass 224 ms | §4 | TDP 0: stuck power task, then latched |
| Card 1: SP min/max clock 600/600 over 15.4 h, up to an 88 °C mean | §5 | governor inactive (APM off or latched) |
| `sp.system_c` = 0 on all three cards | §6 | the PMIC temperature alarm is ineffective |
| Hot spot vs mean: the high sits 2–4 °C above the mean at rises, and ends windows 2–3 °C above the SP's max of the mean | `R/…/claims-v3/results/tel.json` TEL-R; `HP/observability.md:163-167` | a one-sensor rule would trip 2–4 °C earlier in mean terms; this is the size of effect a trigger test must resolve |
| Heat placement (aifoundry3): `L(PER16@32 / INT16@32) = 0.48`, so the perimeter takes e^0.48 ≈ 1.6× as long to heat the governor's input from 61 to 66 °C at equal power | `HP/dev/dev-r2.json .dev.items["PLACE-t"]` | placement changes time-to-trip only through Σ over the 34 sensors; to become "longer at 800 MHz" on aifoundry2 it needs a start ≤ 64 and P < 65 W |

---

## 11. What this means for the next DVFS/heat experiments

This section is inference, offered as design input.

**Only aifoundry2's governor acts.** Its trigger-level observables, in order of how little they change on the card:
1. `sp.minion_mhz` min/max and `sp.minion_c` max per 1 s window. These are the SP's own per-pass clock and mean, read
   through existing ettelem fields; nothing new to build.
2. Throttle residency, THERMAL_DOWN (4) and POWER_UP (2), read before and after each block. That is a new read-only
   query.
3. The SP statistics trace, which timestamps each pass. It must first be re-enabled with `control = 3`, the boot
   default.
4. Exit and entry lines in the SP ring: no sampler, or WARNING (O2).

**Sharp, testable predictions from source** (register them before looking):
- (P1) The first 800→700 step comes within one pass after the SP's own mean first reads ≥ 66. That is `sp.minion_c`
  max ≥ 66 in the same or the previous window, whatever the hottest sensor reads.
- (P2) A down-pair is spaced by one loop period, 0.40 s plus the body.
- (P3) When a loop exits at a mean ≤ 65 and a kernel is running, the clock is back at 800 within one pass. The duty
  cycle at 800 MHz during hunting is set by how long the mean stays at 65 or below.
- (P4) An idle card at 66 °C or above is in the loop and emits nothing. The exit line prints 65 at the host mean's
  first 65 on the way down.
- (P5) Every launch rides a heartbeat: the first step-up lags the launch by 0–1.05 s, spread uniformly, plus one pass.
- (P6) With the mean ≤ 64 and one shire's sensor ≥ 67, there is no step.

**Placement → time at 800 MHz on aifoundry2.**
- Start at ≤ 64 °C with `P < 65 W`, where 128–256 minions keep the power under 65 W.
- The quantity to predict is the time until Σ floor(T_i) ≥ 2244. The dev-r2 ratio of 1.6× is the aifoundry3 estimate
  of that time.

**aifoundry3 is a fixed-clock control, and card 1 behaves as fixed-clock too.** On both, only the heating half (t66)
can be measured.

---

## 12. Not established

- Whether the SP µs timer runs at true µs against host time, and the exact loop period on host time (§2.4). The card
  data give 401 µs per tick in SP time and 0.4–0.5 s on the host.
- The true period of the master-minion heartbeat. About 1.05 s in SP time is inferred from event spacing; the source
  comment implies 100 s.
- Card 1: APM off or latched. The POWER_UP residency would narrow it.
- aifoundry3: whether its latch dates from the first crossing of 65 °C after 25 Sep. The residency prediction is 0/0.
- What the PMIC alarms actually compare. PMIC firmware 1.5.0 and 1.3.0 is closed.
- Whether the card-era trace encoder packs power-status records as HEAD's does (§9.1). Whether the statistics trace
  region is readable on these cards (§7.2).
- The physical position of each sensor. The firmware maps shire → sensor only by index (`pvt_controller.c:650-662`).
