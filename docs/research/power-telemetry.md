# ET-SoC-1 power telemetry: what exists, how to read it, how fine it gets

Research notes, 2026-09-19. Everything here comes from reading source and manuals. Nothing was run against a card.
Paths are relative to the repo root. `EP` = `external/et-platform`. Firmware citations are for the lab card's
et-platform commit **353f20e** (Dec 2025). `git diff --stat 353f20e HEAD` shows **no changes** under
`device-bootloaders/src/ServiceProcessorBL2`, `device-api`, `devicemanagement`, `devicelayer`,
`device-management-application`, `et-driver` or `etsoc-hal`. Only version scripts changed, so the line numbers hold at
both commits. `PRM` is `external/et-man/txt/ET Programmer's Reference Manual.txt` (cited by file line). `CARD` is
`external/et-man/ET-PCIe-Dev-Card-V3.pdf`; its power-tree figures are images, so the text version misses them.

## TL;DR

* **The finest energy data the card has:** three power rails measured by the PMIC:
  **VDD_MNN (minion cores), VDD_NOC (mesh) and VDD_SRAM (shire-cache SRAM, the L2/L3/scratchpad arrays)**. Each
  reports Vout, Iout, Pout, Vin, Iin, Pin and temperature as current/min/max/average. On top of that there is total
  board input power (12 V) at 10 mW resolution. The DDR, Maxion, PCIe, logic and VDDQ rails have regulators whose
  voltage can be set, but **no current or power reading reaches the SP**.
* **Per-rail values reach the host only as avg/min/max.** You get them through `DM_CMD_GET_SP_STATS` (what
  et-powertop shows), or through the SP-stats trace buffer, which gets one timestamped record per SP sampling-loop
  pass. That loop runs every 10 ms plus the time it spends on about 100 I2C transactions. My estimate is 20–40 Hz;
  measure it from the trace timestamps.
* **Where the ~7 Hz limit comes from:** the host script. `et-power-log.sh` starts a new `dev_mngt_service` process for
  every sample and then sleeps 100 ms. The SP returns a cached value (`DM_CMD_GET_MODULE_POWER` does no I2C at request
  time), and that cache refreshes once per SP loop pass. The PMIC's own ADC/averaging window is undocumented: the
  PMIC firmware (ATSAMD20 MCU) is not in the repo.
* **Energy per workload, per rail:** reset the stats (`dev_mngt_service -t SPST:reset`), run the workload, then read
  the per-rail `*_power_avg` values. If the PMIC "average" is a cumulative mean since reset, this gives energy
  directly. If it is a moving window, use the stats trace as a time series instead. Either way you get about three
  rails, at best tens of ms apart.
* **No hardware gives you energy per event.** No on-die power estimator, no energy counters, no per-shire current.
  To get pJ per L1/L2/L3/DRAM access or per DRAM activate, do regression. Run microbenchmarks that drive one event
  class, count events with the PMU/shire-cache/memshire counters, and fit ΔE_rail = Σ n_i·e_i. Separate static from
  dynamic energy by sweeping V and f with DM commands, with the DVFS governor off.
* **To sample faster than the SP can,** measure the 12 V input outside the card, with a PCIe riser/interposer power
  meter or a probe on the LTC4218 IMON node. That gives only the board total.

## 1. Sensors on the card and chip

### 1.1 Board power tree (CARD p.2–4 images; CARD text lines 50–89)

| Rail (net) | Regulator | Feeds | Telemetry visible to firmware |
|---|---|---|---|
| 12 V input | LTC4218 hot-swap + 1 mΩ Kelvin shunt; IMON → PMIC MCU ADC | whole card (slot 12 V, or ATX AUX via jumper; 88 W max) | **Board input power**, `pmic_i2c.input_power` (reg 0x04) and `average_pwr` (reg 0x05), 16-bit, 10 mW/LSB |
| VDD_MNN, 400 mV nominal, 120 A, 48 W max | TI TPSM831D31 phase A (3-phase) | all minion cores (compute + master shires) | **PMBus: V/I/P in and out, temperature** (PMB stats, MINION) |
| VDD_NOC, 400 mV nominal, 40 A, 16 W max | TPSM831D31 phase B (1-phase) | mesh/NoC | **PMBus V/I/P/temperature** (PMB stats, NOC) |
| VDD_SRAM, 750 mV, 20 A/15 W in figure | LTM4680 (V3 text; the figure shows TPSM846C23) | shire-cache SRAM arrays (L2/L3/SCP) | **PMBus V/I/P/temperature** (PMB stats, SRAM) |
| VDD_DDR, 875 mV, 4.4 W max | TDK FS1406 µPOL | LPDDR4 controllers (memshires) | voltage set-point only |
| VDD_MXN, 850 mV | FS1406 | Maxion cores | set-point only |
| VDD_LOGIC, 750 mV | FS1406 | PCIe analog, IO shire, eMMC/USB logic | set-point only ("PCIE_LOGIC") |
| VDD_1P5, 1.5 V | FS1406 | PCIe PHY VPH | set-point only ("PCIE") |
| VDD_QLP, 620 mV | FS1406 | LPDDR4x VDDQ (IO) | set-point only ("VDDQLP") |
| VDD_Q, 1.1 V | FS1406 | LPDDR4x VDDQ/VDD2 (DRAM core) | set-point only ("VDDQ") |
| 3.3 V, 1.8 V, 1.8 V standby LDOs | FS1406 / TPS79901 | USB, eMMC, flash, PLLs, PVT sensors, PMIC MCU | none |

* The **PMIC** is an Atmel/Microchip **ATSAMD20** MCU ("PMIC Micro", CARD p.2). It talks to the regulators over I2C
  and to the SP over the SP's `spio_i2c0`. Its UART goes to the card's FTDI "USB Console" (CARD p.2; `ET
  Introduction.txt` lines 67–78). Its firmware is not in the repo. The only interface definition is
  `EP/device-bootloaders/src/ServiceProcessorBL2/include/pmic_hal.h` lines 72–263.
* The FS1406 µPOLs support I2C, but the PMIC firmware exposes only their voltage registers (0x18–0x1f, 0x20–0x31).
  It exposes no current or power readback for them. Ranges are in `bl2_pmic_controller.h` lines 133–244.
* **Per-minion-group voltage:** the PMIC has `MINION_G1..G17_VOLTAGE` registers (0x21–0x31; `pmic_get/set_minion_group_voltage`
  in `bl2_pmic_controller.h` lines 464–477). There is still only **one** VDD_MNN current sensor, so this gives no
  per-group power.

### 1.2 PMIC register-level data (SP side)

`EP/device-bootloaders/src/ServiceProcessorBL2/driver/pmic_controller.c`:

* I2C0 at **400 kHz** (`setup_pmic`, line 477–481). Every access runs in a FreeRTOS critical section with 3 retries
  (`get_pmic_reg`, lines 254–310).
* `pmic_read_instantaneous_soc_power`: 2 bytes from reg 0x04, units 10 mW (lines 1352–1356).
* `pmic_read_average_soc_power`: 2 bytes from reg 0x05, 10 mW (lines 2385–2389). The averaging window is undocumented.
* `pmic_get_pmb_stats` (lines 1827–1935) writes a "snapshot" command (0x43) to reg 0x15. It then does **84 reads of 4
  bytes**: 3 rails × 7 quantities (V_OUT, A_OUT, W_OUT, V_IN, A_IN, W_IN, DEG_C) × {current, min, max, average},
  each masked to 16 bits (`PMB_STATS_MASK`, line 91). `pmic_reset_pmb_stats` writes 0x47 (lines 1801–1806;
  `pmic_hal.h` lines 737–738). The enums and struct are in `bl2_pmic_controller.h` lines 23–93. Units, going by
  et-powertop: **W_OUT in mW** (`et-top.cc` lines 794–796). The PMIC firmware defines the V/A units.
* `pmic_hal.h` line 1786–1789 describes a selector format for PMB reads (component / value type / output type). The
  PMIC could therefore return one chosen value, but the SP never uses it.

### 1.3 On-die PVT (PRM §1.6, lines 550–580; §15.2.3.21–25, lines 12552 ff.)

* 5 Moortec PVT controllers at `0x00_5400_0000 + n·0x1_0000` (PRM Table 1-6). They hold **36 temperature sensors**
  (one per minion/IO shire), **36 process detectors** (ring oscillators) and **8 voltage monitors × 16 channels**.
  A voltage monitor measures a local supply voltage. **None of them measures current or power.**
* Firmware configuration (`include/bl2_pvt_controller.h`): TS at 12-bit resolution in RUN_1 mode, VM at 14-bit in
  RUN_0 mode, 100 MHz APB clock divided ÷12. They sample continuously
  (`driver/pvt_controller.c` lines 538–565, `pvt_init` line 1083–1102). The SP reads the latest sample plus the
  hardware hi/lo registers.
* The VM channels cover, per minion shire, vdd_sram, vdd_noc and vdd_mnn; per memshire, vdd_ms and vdd_noc; and also
  the IO shire, the PShire and 2 external analog inputs (`bl2_pvt_controller.h` structs). Erratum 5.1 (Errata lines
  3014–3029): the "NoC" VMs on memshires 4–7 actually measure the memshire supply.
* **SP-only:** PRM Table 15-37 (lines ~11425–11429) gives R_SP_PVTn access to the SP only. Neither PCIe nor the
  minions can read the PVT controllers. The host gets aggregates only: the average/low/high minion-shire temperature
  and voltage, and IO-shire values.
* Useful as a per-shire thermal map and as a local-voltage check (IR drop under load). It is not an energy measure.

### 1.4 On-die power estimators

None. Neither the PRM, the firmware nor the Erbium RTL in `external/core-et` contains an activity-based power model
or energy counter. `DP_per_Mhz 15` in `thermal_pwr_mgmt.c` line 210 is an unused placeholder.

## 2. How the host reads each value

The host reaches all power data through **`/dev/et<N>_mgmt`**, which is single-open (driver
`EP/et-driver/et-soc1-pcie.c` lines 1137–1153 return `-EBUSY`). The path is libDM → DM command → SP → cached globals.
The driver exports no power sysfs or hwmon files. Its sysfs groups are only err_stats, mem_stats, ops_vq_stats and
soc_reset.

### 2.1 The SP sampling loop (where the numbers come from)

`EP/device-bootloaders/src/ServiceProcessorBL2/rtos_task/dm_task.c` lines 196–277, task priority 2:

1. `update_module_current_temperature()`: PVT
2. `update_pmb_stats(false)`: the 84+1 I2C transactions above
3. `update_module_soc_power()` (`services/thermal_pwr_mgmt.c` lines 794–862): PVT voltages, then `get_module_voltage`
   (9 PMIC reads), `average_pwr`, and `input_power` → `g_pmic_power_reg.soc_pwr_10mW`. It copies the PMB
   **w_out.average/min/max** of each rail into `op_stats`. **The PMB "current" (instantaneous) values are read but
   not used.**
4. frequencies, uptime, MM stats, DRAM BW (a stub that returns 16, `services/perf_mgmt.c` lines 70–88)
5. `check_power_throttle_conditions()` (DVFS)
6. `dm_log_operating_point_stats()` appends the 128-byte `op_stats_t` to the **SP stats trace buffer** (lines 301–312)
7. `vTaskDelay(DM_TASK_DELAY_MS)` with **`DM_TASK_DELAY_MS = 10`** (`include/config/mgmt_build_config.h` line 427)

Estimated period: 10 ms of delay plus about 95 I2C transactions at 400 kHz. A 4-byte read is about 65 bit-times ≈
160 µs, so roughly 15–25 ms for I2C before PMIC clock stretching. That puts the loop at about 25–50 ms, or 20–40 Hz.
I have not measured this. The trace timestamps below give the real value.

### 2.2 DM commands and tools

| What | Command / tool | Per-rail? | Notes |
|---|---|---|---|
| Board power, "instantaneous" | `DM_CMD_GET_MODULE_POWER` (33) | no, total | Returns the cached `soc_pwr_10mW` (`thermal_power_monitor.c` lines 142–165, `get_module_soc_power` returns the global). 10 mW units. |
| Per-rail power/voltage/temperature/frequency avg/min/max, plus system power avg/min/max | `DM_CMD_GET_SP_STATS` (60) | **yes: minion, sram, noc, system** | `services/performance.c` lines 404–465; struct `get_sp_stats_t` in `EP/device-api/include/management-api/device_mgmt_api_rpc_types.h` lines 402 ff. Rail power in mW, system power in 10 mW. Rail avg/min/max come from the PMIC PMB stats. System min/max are the SP's min/max of instantaneous values since reset. `dev_mngt_service -m` has no case for it, so use et-powertop or your own libDM client. |
| Reset those stats, and the PMIC PMB stats | `DM_CMD_SET_STATS_RUN_CONTROL` (62) with `STATS_TYPE_SP`, `RESET_COUNTER` (\|`RESET_TRACEBUF`) | – | RESET_COUNTER → `Thermal_Pwr_Mgmt_Init_OP_Stats()` → `update_pmb_stats(true)` → PMIC reset command 0x47 (`performance.c` lines 546–575; `thermal_pwr_mgmt.c` line 2846). CLI: `dev_mngt_service -n 0 -t SPST:reset` sets both bits (`dev_mngt_service.cc` lines 2294–2312). |
| **Time series of per-rail stats** | SP stats trace buffer: `ETSOC1_IOCTL_EXTRACT_TRACE_BUFFER`, type `TRACE_BUFFER_SP_STATS` | yes | 1 MB ring (`EP/et-common-libs/include/system/layout.h` line 283). The driver copies it out of BAR memory (`et-soc1-pcie.c` lines 980–1060). Entry = 16 B header (`cycle` = SP µs ticks, `trace.c` line 39) + 8 B custom header + 128 B `op_stats_t` (`EP/et-trace/include/et-trace/layout.h` lines 321–326, 463–490) = 152 B, so about 6,900 records before it wraps (`encoder.h` lines 566–571). CLI: `dev_mngt_service -n 0 -t SPST:extract` writes the raw `dev0_sp_stats` file plus a decode in `dev0_traces.txt`. et-powertop dumps it too. |
| Rail voltage set-points | `DM_CMD_GET_MODULE_VOLTAGE` (31) | 9 rails | PMIC registers (`thermal_pwr_mgmt.c` lines 1010–1110), 8-bit codes; see the conversions below. Note the SP handler for `GET_ASIC_VOLTAGE` also fills the header with the `GET_MODULE_VOLTAGE` id (`thermal_power_monitor.c` line 205). |
| Measured on-die voltages | `DM_CMD_GET_ASIC_VOLTAGE` (32) | minion/sram/noc/ddr/maxion/ioshire | PVT averages across shires, in mV. |
| Temperatures | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | IO shire, and minion-shire avg/low/high | `pmic_sys` is actually the PVT minion average (`thermal_pwr_mgmt.c` lines 732–745). |
| Frequencies | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | minion/noc/memshire/ddr/pcie/io | L2/SRAM frequency equals the minion frequency (`perf_mgmt.c` lines 201–207). |
| et-powertop | `EP/device-management-application/src/et-top.cc` | shows the SP stats | Polls `DM_CMD_GET_SP_STATS` every `kUpdateDelayMS = 1000` ms by default (`et-top.hpp` line 46). `DELAY` argument, `-b` batch mode. "ETSOC" = minion + sram + noc + a **hard-coded 3.75 W "OTHER"** (`kOtherPower`, `et-top.hpp` line 48; `et-top.cc` lines 780–797). |

### 2.3 Where the ~7 Hz comes from, and how fast you can go

* `scripts/et-power-log.sh` launches `dev_mngt_service` per sample: process start, libDM init, mgmt open/close,
  about 15 ms. Then it runs `sleep 0.1`. That makes about 115–150 ms per sample, or 7–8 Hz. **The limit is on the
  host.**
* A persistent client (C++ against `libDM`, holding the mgmt node open and calling `serviceRequest` in a loop) gets
  a round trip of a few ms. It still sees new values only once per SP loop pass, about 25–50 ms (estimated), so the
  ceiling is about 20–40 Hz. The response header carries the device latency in µs (`FILL_RSP_HEADER`), and
  `dev_mngt_service` prints it.
* **Better: take the SP stats trace instead of polling.** Reset it, run the workload (up to about 6,900 loop passes
  fit before the ring wraps), then extract once. You get every loop pass with a µs timestamp and nothing is
  dropped. Its limits: the per-rail fields are PMIC **avg/min/max**, not instantaneous values, and the record holds
  **no instantaneous board power**. Board power appears only as system.avg (PMIC average register) and system
  min/max.
* Other limits: the PMIC ADC and averaging behaviour, and the regulators' telemetry update rates. The LTM4680-class
  ADC loop is on the order of 100 ms and TPSM831D31 telemetry is similar. I have not checked either against the
  datasheets. None of this is visible from the repo.
* Faster sampling needs **SP firmware changes**: a smaller `DM_TASK_DELAY_MS`, a fast loop reading only
  `input_power` and the three `W_OUT.current` values through the PMB selector, and logging those into the stats
  buffer. That means reflashing SP firmware, which is out of scope for the shared lab cards.
* **External measurement** is the only way to kHz rates: a PCIe riser with 12 V current sensing, or a scope on the
  LTC4218 IMON net (`IMON_P12V_CE`, 1.24 V at 15 A, CARD p.4). It measures board total only. The FT232R on
  aifoundry2 (`/dev/ttyUSB0`) is probably not the card's multi-channel FTDI, and I did not touch it. The PMIC console
  UART on the card's micro-USB could be explored, but its command set is unknown.

## 3. Voltage/frequency control (to separate static and dynamic energy)

All of these need the mgmt node.

* **DVFS governor is on by default** when the VMIN LUT is valid (`thermal_pwr_mgmt.c` lines 1622–1646). TDP = 65 W,
  temperature threshold = 65 °C (`thermal_pwr_mgmt.h`). While the MM reports "busy", it steps the minion frequency
  up or down through the VMIN LUT by comparing PMIC **average** power with TDP (`check_power_throttle_conditions`,
  lines 864–929). Minion and L2/SRAM voltages move with it (`set_minion_operating_point_and_update_pwr_status`, line
  1794 ff.). On MM idle it goes back to the boot frequency. This matches the 600→~850 MHz drift in
  `docs/et-soc1-notes.md`. **For energy work, turn it off:**
  `dev_mngt_service -m DM_CMD_SET_MODULE_ACTIVE_POWER_MANAGEMENT -p 0 -n 0`. Or pin the TDP with
  `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -l`.
* **Frequency:** `DM_CMD_SET_FREQUENCY` (37) with `-f <minion_MHz>,<noc_MHz>`. The CLI always sends both PLLs with
  `USE_STEP_CLOCK_TRUE` (`dev_mngt_service.cc` lines 771–796), so both frequencies must exist in the HPDPLL table
  (`EP/etsoc-hal/include/hwinc/hpdpll_modes_config.h`: 100 MHz reference, 100–1475 MHz in 25 MHz steps, plus a few
  others). The minion LVDPLL table covers 300–1400 MHz in 25 MHz steps. **This command does not change voltage.** Do
  that yourself: raise V before raising f. The DVFS limits are MNN 300–800 MHz and NOC 300–500 MHz
  (`thermal_pwr_mgmt.c` lines 115–126). No DM command sets the memshire or DDR frequency.
* **Voltage:** `DM_CMD_SET_MODULE_VOLTAGE` (35) with `-v MINION,<mV>` (also L2CACHE, NOC, DDR, MAXION, PCIE,
  PCIE_LOGIC, VDDQ, VDDQLP). It is checked against the PMIC limits and then against PVT
  (`Thermal_Pwr_Mgmt_Set_Validate_Voltage`, lines 3008–3055). Codes are mV = 250 + 5·code for
  MNN/SRAM/NOC/DDR/MXN. Firmware limits (`bl2_pmic_controller.h` lines 165–244): MNN 400–620, SRAM 660–850,
  NOC 400–600, DDR 700–870, MXN 600–870 mV. Boot defaults: MNN 500, SRAM 750, NOC 485, PCL 775, DDR 800, MXN 850 mV
  (`thermal_pwr_mgmt.h`). `DM_CMD_GET_VMIN_LUT` (73) returns the per-card V(f) table.
* **Static/dynamic separation recipe:** DVFS off, fixed workload. Sweep f at fixed V: P_rail = P_static(V,T) +
  C_eff·V²·f, so the slope in f gives C_eff and the intercept gives static power. Then sweep V at fixed f to get the
  shape of leakage in V. Hold temperature constant: board power creeps about 3 W over 12 s as the chip warms
  (`docs/getting-started.md` line 194). Log the PVT temperature with every point.
* **Clock/power gating per shire:** the ESRs exist. They are `shire_power_ctrl` (per-neighbourhood on/off/nsleep),
  `power_ctrl_neigh_nsleepin/isolation/nsleepout` (per minion), and `clk_gate_ctrl` (integer pipe, VPU, D$, neigh
  clock gates) (PRM lines 15258–15276, 15356–15358). They are **M-mode only** (`EP/et-common-libs/include/etsoc/isa/esr_defines.h`
  lines 634–751, `PRV_M`) and no firmware uses them. The SP deliberately initializes **all** 34 shires as a
  "workaround to get rid of a bug that causes huge excess current draw" (`driver/minion_configuration.c` lines
  581–590). Powering down unused shires is therefore not supported, and was apparently harmful. A kernel's shire
  mask only leaves the unused shires idle and clock-gated by hardware. Erratum 4.3 (Errata lines 2838–2867): the
  shire-cache perf cycle counter stops when SC clock gating kicks in, and the workaround (`esr_sc_clk_gate_disable`)
  **raises SC power**. Do not enable it while measuring energy.

## 4. Activity counters (for the regression side)

No energy counters. Event counters:

* **Minion PMU** (PRM §1.3.2, lines 373–495): 6 counters per hart pair per neighbourhood (`mhpmcounter3–8`). The
  events are cycles, retired instructions, D$ access/miss, L2 miss/evict requests, tensor load/store ops,
  TensorFMA/IMA ops, and the neighbourhood events ET-Link/icache/PTW. The firmware configures them at boot
  (`EP/device-minion-runtime/src/MachineMinion/src/main.c` lines 60–111; `hpmcounter3` = cycles). Errata 1.22/1.23:
  a PMU write can happen twice, and simultaneous reads from both harts can return wrong values.
* **Shire-cache perfmon**, per bank: a 40-bit cycle counter plus P0/P1 with qualifiers (PRM lines 14960–14990). The
  firmware default counts L2 reads and L2 writes (`EP/et-common-libs/include/etsoc/drivers/pmu/pmu.h` lines
  186–196). Erbium RTL (`external/core-et/rtl/inc/shire_cache_types.vh` lines 1277–1300) lists the event bits: tag
  hit/miss, dirty evict, rbuf L2/SCP hit, per opcode. The ET-SoC-1 encoding is only in an internal Google doc linked
  from pmu.h.
* **Memshire/DDRC perfmon**, per memshire: cycle counter plus P0/P1, with 64-bit `qual`/`qual2` (PRM lines
  15565–15585). The firmware counts mesh reads and writes (`PMU_MS_QUAL_ALL_MESH_READS/WRITES`). The DDRC exposes 24
  "perf_op" signals (`core-et/rtl/inc/memshire_defines.vh` line 129, `ddrc_trace_ctl.perf_op_sigs_mask`). In the
  Synopsys uMCTL2 these typically include activate, precharge, read, write and refresh, so **counting DRAM activates
  may be possible**. The mapping to qualifier bits is undocumented and would have to be found by experiment.
* Kernels read the SC and MS counters through syscalls (`SYSCALL_PMC_SC_SAMPLE*`, `SYSCALL_PMC_MS_SAMPLE*`;
  `MachineMinion/src/syscall.c` lines 131–140). The MM stats trace (`TRACE_BUFFER_MM_STATS`) carries averaged
  L2/DDR bandwidth.

## 5. Constraints

* The mgmt node is single-open. et-powertop, `dev_mngt_service`, et-testdrive and any power logger exclude one
  another. Launchers that open only the `_ops` node can run alongside.
* `SPST:reset` resets the shared stats and the PMIC PMB min/max/avg, which other users watching et-powertop will
  notice. Do not reset the SP (`DM_CMD_RESET_ETSOC`) or reflash firmware on lab cards.
* Changing V/f or DVFS changes the card for everyone. Restore the defaults afterwards: DVFS on (`-p 1`), TDP 65, and
  the LUT/boot voltages.
* Unknowns worth one experiment each:
  1. SP loop period: take `-t SPST:reset`, then 10 s later `-t SPST:extract`, and difference the `cycle` fields.
  2. PMB "average" semantics: reset, load a step workload, and see whether `minion_power_avg` converges like a
     cumulative mean (≈1/t) or like a moving window.
  3. Update rate of the PMIC `input_power` register: poll `GET_MODULE_POWER` from a persistent client at 100 Hz and
     look at the step size in time.

## 6. Recommended measurement setup (finest achievable without new firmware)

1. Turn DVFS off. Fix minion/NOC frequency and MNN/SRAM/NOC voltages. Wait for temperature to settle.
2. Per workload: `dev_mngt_service -n 0 -t SPST:reset`, run the workload (≥1–2 s, many loop passes), then
   `dev_mngt_service -n 0 -t SPST:extract`. Parse the 152-byte records (µs timestamps, per-rail W avg/min/max, V,
   °C, MHz). Or read `DM_CMD_GET_SP_STATS` once at the end from a small libDM client.
3. Energy per rail = mean rail power (minus the idle baseline at the same V/f/T) × busy time. Board total comes from
   the existing logger, which can run 3–5× faster as a persistent client, or from an external 12 V meter.
4. Attribute to events by regression across microbenchmarks. Minion-rail energy per FMA and per L1 access; SRAM-rail
   energy per L2/L3/SCP access (shire-cache counters); NoC-rail energy per mesh hop or byte (nocbench); DRAM energy
   = board − (MNN + SRAM + NOC) − the static "other" measured at idle, against memshire read/write (and possibly
   activate) counts. The DDR PHY/controller (VDD_DDR) and the DRAM (VDDQ/VDD2) have **no individual readout**, so
   DRAM energy exists only as that residual.
