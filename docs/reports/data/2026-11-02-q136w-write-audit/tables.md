## A. Every command the lab's code can send, classified from et-platform `836a4ab` (BL2 0.22.0)

Handler paths are under `device-bootloaders/src/ServiceProcessorBL2/`. *Sites* counts the lines in this repository's tracked code that can send the command (inventory.json); *where* names the files with the most.

| Id | Command | Class | PMIC | Handler at `836a4ab` | Side effects | Sites | Where |
|---|---|---|---|---|---|---|---|
| 14 | `GET_MODULE_FIRMWARE_REVISIONS` | **WRITE** | write | services/firmware_update.c:862-915; :903 pmic_get_fw_version -> driver/pmic_controller.c:952-974 -> pmic_get_active_boot_slot :2531-2557 (set_pmic_reg(PMIC_I2C_FW_MGMTCMD_ADDRESS 0x16, ACTIVE_SLOT 7) at :2543, data read at :2549) and pmic_fw_update_subcommand :2581-2600 (set_pmic_reg(0x16, VERSION 5 | slot) at :2587, data read at :2591) | - | 7 | `tools/claims-v3/e114/run_e114.sh`, `tools/claims-v3/hlp/run_e79.sh`, `tools/claims-v3/kspeed/e84/run_e84.sh`, `tools/claims-v3/lq6/gov_e72.py` and 3 more |
| 22 | `SET_MODULE_TEMPERATURE_THRESHOLDS` | **WRITE** | none | services/thermal_power_monitor.c:493-521 -> services/thermal_pwr_mgmt.c:638-643 (RAM, no range check in the SP; libDM refuses outside 20-125 C) | - | 1 | `tools/claims-v3/knob/run_knob.py` |
| 26 | `SET_MODULE_STATIC_TDP_LEVEL` | **WRITE** | none | services/thermal_power_monitor.c:392-415 -> services/thermal_pwr_mgmt.c:576-591 (refuses > 75 W, else one INFO log and the RAM assignment) | - | 11 | `tools/claims-v3/e118/gov_e118.py` ×4, `tools/claims-v3/e120/run_e120.py` ×2, `tools/claims-v3/e77/run_e77.py` ×2, `tools/claims-v3/lq6/gov_e72.py` ×2 and 1 more |
| 35 | `SET_MODULE_VOLTAGE` | **WRITE** | write | services/thermal_power_monitor.c:294-316 -> services/thermal_pwr_mgmt.c:3008-3048 -> pmic_set_voltage (:3021; driver/pmic_controller.c:1586) | - | 2 | `tools/claims-v3/nv/block.sh`, `tools/claims-v3/nv/stubs/stub-dms` |
| 52 | `RESET_ETSOC` | **WRITE** | write | services/firmware_update.c:1125 -> :45-105: if the PMIC firmware was updated, pmic_force_power_off_on() (a power cycle, driver/pmic_controller.c:2272); else the PMIC watchdog is armed (pmic_enable_wdog_timeout_reset, pmic_set_wdog_timeout_time) and pmic_force_reset() (:2298) | - | 2 | `tools/lab/et-reset` ×2 |
| 62 | `SET_STATS_RUN_CONTROL` | **WRITE** | write | services/performance.c:546-636. With type SP and control RESET_COUNTER: Thermal_Pwr_Mgmt_Init_OP_Stats (:575 -> services/thermal_pwr_mgmt.c:2805-2880): the RAM op_stats re-initialised, pvt_hilo_reset() (:2828, writes the PVT controllers' high/low latches, driver/pvt_controller.c:1071-1081), PMIC reads (temperature :2838, average power :2874) and update_pmb_stats(true) (:2846 -> :1334-1350), which makes two PMIC writes: pmic_reset_pmb_stats (driver/pmic_controller.c:1801-1805: set_pmic_reg(PMB_RW 0x15, 0x47, 1 byte), the PMIC's stats reset), then pmic_get_pmb_stats (:1827-1832: set_pmic_reg(PMB_RW 0x15, 0x43 = PMIC_I2C_PMB_STATS_SNAPSHOT_VALUE, 4 bytes, include/pmic_hal.h:737), the snapshot command, before it reads the PMB stats back; the SP's own DM task sends that snapshot write every pass anyway, rtos_task/dm_task.c:215, update_pmb_stats(false)). And any control word WITHOUT bit 0 (TRACE_ENABLE) switches the SP's device-statistics trace OFF (performance.c:556-564 -> services/trace.c:654-661); Trace_Init at boot leaves it on. With type MM (2) the control goes to the Master Minion instead (performance.c:579-599 -> interface/mm_iface.c:413-450). | - | 31 | `STATS_RESET`: `tools/claims-v3/dv2/dv2lib.sh` ×3, `tools/claims-v3/hp/a2/hplib.sh` ×3, `tools/claims-v3/hp/hplib.sh` ×3, `tools/claims-v3/oh/ohlib.sh` ×3 and 12 more; `SPST_TRACE_CONTROL`: `tools/claims-v3/tel/block.sh` ×2 |
| 67 | `SET_DM_TRACE_CONFIG` | **WRITE** | none | services/trace.c:474-479 -> :183-207 (sets the SP trace's event and filter masks and the SP log level, RAM; it stays until the next boot or set) | - | 7 | `tools/claims-v3/tel/block.sh` ×4, `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/hp/a2/hplib.sh`, `tools/claims-v3/hp/hplib.sh` |
| 3 | `GET_ASIC_CHIP_REVISION` | **READ** | none | services/asset_track.c:39 -> services/asset_track_mgmt.c:52 -> driver/bl2_otp.c:141 -> shared/common/src/sp_otp.c:1394 (OTP read) | - | 2 | `tools/claims-v3/hlp/run_e79.sh`, `tools/claims-v3/lq6/gov_e72.py` |
| 21 | `GET_MODULE_TEMPERATURE_THRESHOLDS` | **READ** | none | services/thermal_power_monitor.c:438 -> services/thermal_pwr_mgmt.c:665-669 (RAM: g_soc_power_reg.temperature_threshold) | - | 82 | `tools/claims-v3/lq6/gov_e72.py` ×3, `tools/claims-v3/e114/run_e114.sh` ×2, `tools/claims-v3/e118/gov_e118.py` ×2, `tools/claims-v3/e120/run_e120.py` ×2 and 67 more |
| 23 | `GET_MODULE_POWER_STATE` | **READ** | none | services/thermal_power_monitor.c:48 -> services/thermal_pwr_mgmt.c:551-555 (RAM) | - | 78 | `tools/claims-v3/e114/run_e114.sh` ×2, `tools/claims-v3/e118/gov_e118.py` ×2, `tools/claims-v3/e120/run_e120.py` ×2, `tools/claims-v3/e77/run_e77.py` ×2 and 65 more |
| 25 | `GET_MODULE_STATIC_TDP_LEVEL` | **READ** | none | services/thermal_power_monitor.c:339 -> services/thermal_pwr_mgmt.c:613-617 (RAM: g_pmic_power_reg.module_tdp_level) | - | 80 | `tools/claims-v3/lq6/gov_e72.py` ×3, `tools/claims-v3/e114/run_e114.sh` ×2, `tools/claims-v3/e118/gov_e118.py` ×2, `tools/claims-v3/e120/run_e120.py` ×2 and 65 more |
| 27 | `GET_MODULE_CURRENT_TEMPERATURE` | **READ** | none | services/thermal_power_monitor.c:545 -> services/thermal_pwr_mgmt.c:732-773 (PVT register reads, driver/pvt_controller.c:618-643, 659-664, 1274-1340) | refreshes the SP's own RAM copy of the die temperature (g_pmic_power_reg.soc_temperature, thermal_pwr_mgmt.c:754) with the value just read, as its own task does every pass | 57 | `tools/claims-v3/lib.sh` ×3, `scripts/mmbench-power.py` ×2, `tools/claims-v3/nv/block.sh` ×2, `tools/ettelem/run_vf_cold.sh` ×2 and 43 more |
| 29 | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | **READ** | none | services/thermal_power_monitor.c:596-618 -> services/thermal_pwr_mgmt.c:1477-1502 (RAM copies) | a raw state outside 0-3 (the enum at device-api/include/management-api/device_mgmt_api_spec.h:278-286) takes the default branch: two ERROR log lines (thermal_pwr_mgmt.c:1499 and thermal_power_monitor.c:607), so two SP_RUNTIME_ERROR events and two counts on the SP's error counter per state read (E77's F1; Q134(a): 4,228 events = 2 x 2,114 invalid-state reads on aifoundry2) | 6 | `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/dv2/z2.sh`, `tools/claims-v3/e120/run_e120.py`, `tools/claims-v3/e77/run_e77.py` and 2 more |
| 30 | `GET_MODULE_UPTIME` | **READ** | none | services/thermal_power_monitor.c:698 -> services/thermal_pwr_mgmt.c:1451-1455 (RAM, updated by the SP's task, :1406-1426) | - | 12 | `tools/claims-v3/nv/block.sh` ×2, `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/dv2/z2.sh`, `tools/claims-v3/e114/run_e114.sh` and 7 more |
| 31 | `GET_MODULE_VOLTAGE` | **READ** | read (9 register reads) | services/thermal_power_monitor.c:243 -> services/thermal_pwr_mgmt.c:1010-1140: nine pmic_get_voltage calls (DDR, L2 cache, Maxion, Minion, PCIe, NoC, PCIe logic, VDDQLP, VDDQ) -> driver/pmic_controller.c:1473-1500 -> get_pmic_reg (:254-300, an I2C register read) | refreshes the SP's RAM copy g_pmic_power_reg.module_voltage with the values read | 49 | `tools/claims-v3/lib.sh` ×3, `tools/claims-v3/nv/block.sh` ×2, `tools/ettelem/run_vf_cold.sh` ×2, `tools/lab/dashboard/collect.py` ×2 and 39 more |
| 32 | `GET_ASIC_VOLTAGE` | **READ** | read (2 register reads) | services/thermal_power_monitor.c:192 -> services/thermal_pwr_mgmt.c:1142-1222: PVT voltage-monitor reads, then pmic_get_voltage(VDDQLP) and (VDDQ) at :1213 and :1215 | refreshes the SP's RAM copy g_soc_power_reg.asic_voltage | 128 | `tools/claims-v3/e120/run_e120.py` ×3, `tools/claims-v3/e77/run_e77.py` ×3, `tools/claims-v3/knob/run_knob.py` ×3, `tools/claims-v3/lib.sh` ×3 and 104 more |
| 33 | `GET_MODULE_POWER` | **READ** | none | services/thermal_power_monitor.c:142 -> services/thermal_pwr_mgmt.c:984-988 (RAM copy the SP's task keeps from the PMIC) | - | 75 | `tools/claims-v3/lib.sh` ×5, `tools/claims-v3/tau/block.sh` ×3, `tools/claims-v3/hlc/run_hlc.py` ×2, `tools/claims-v3/hm/run_hm.py` ×2 and 51 more |
| 53 | `GET_ASIC_FREQUENCIES` | **READ** | none | services/performance.c:41 -> services/perf_mgmt.c:276- -> driver/io_pll.c:907-960 (PLL register reads) | refreshes the SP's RAM copy of the clocks (get_soc_perf_reg()->asic_frequency) | 137 | `tools/claims-v3/e120/run_e120.py` ×3, `tools/claims-v3/e77/run_e77.py` ×3, `tools/claims-v3/knob/run_knob.py` ×3, `tools/claims-v3/lib.sh` ×3 and 108 more |
| 60 | `GET_SP_STATS` | **READ** | none | services/performance.c:404-466 -> services/thermal_pwr_mgmt.c:2780-2784 (a copy of the RAM op_stats the SP's task keeps) | - | 46 | `tools/claims-v3/lib.sh` ×3, `tools/ettelem/run_vf_cold.sh` ×2, `tools/lab/dashboard/collect.py` ×2, `tools/lab/dashboard/remote.sh` ×2 and 37 more |
| 69 | `GET_SHIRE_CACHE_CONFIG` | **READ** | none | driver/bl2_cache_control.c:880 -> driver/flashfs.c:1937-1945 (RAM copy) | - | 1 | `workloads/memhier/run_energy.py` |
| 73 | `GET_VMIN_LUT` | **READ** | none | services/asset_track.c:74 -> driver/flashfs.c:2073-2080 (RAM copy of the persistent config) | - | 9 | `tools/claims-v3/e118/gov_e118.py` ×2, `tools/claims-v3/e120/run_e120.py` ×2, `tools/claims-v3/e77/run_e77.py` ×2, `tools/claims-v3/lq6/gov_e72.py` and 2 more |
| 74 | `GET_ASIC_PVT_SAMPLES` | **UNCLASSIFIED** | unknown | not in 836a4ab: command 74 exists only in the maintainer's raw-temperature patch, whose source is not public | - | 0 | none |
| - | `VARIANT_UNRESOLVED` (no DM command) | **UNCLASSIFIED** | unknown | an ettelem call whose binary the checker cannot resolve to a reviewed build directory (a variable set outside the scanned files, or a program that is not among them): its sends are listed as the reviewed variants', but which build runs is not visible. NO-GO until the runner names the source with --variant-source (KEY 'unresolved', a build directory or a program name; the source's sha256 must equal a reviewed variant's) or a person reads the line and records a reviewed --except. Never allowed by --allow. | - | 20 | `tools/claims-v3/e120/run_e120.py` ×8, `tools/claims-v3/e77/run_e77.py` ×8, `tools/lab/dashboard/remote.sh` ×2, `tools/claims-v3/hlc/run_hlc.py` and 1 more |
| - | `TRACE_EXTRACT` (no DM command) | **READ** | none | dev_mngt_service -t <type>:extract and ettelem sptrace: no DM command; two driver ioctls (ETSOC1_IOCTL_GET_TRACE_BUFFER_SIZE, ETSOC1_IOCTL_EXTRACT_TRACE_BUFFER) copy a trace region over PCIe (devicelayer/src/DevicePcie.cpp:822-835; et-driver/et-soc1-pcie.c:1021-1077, et_ioread) | - | 13 | `tools/claims-v3/tel/block.sh` ×3, `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/dv2/z2.sh`, `tools/claims-v3/e120/run_e120.py` and 7 more |
| - | `ETCFG` (no DM command) | **READ** | none | tools/etcfg: ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION, a read-only driver ioctl (tools/etcfg/etcfg.c:28) | - | 1 | `tools/claims-v3/tel/block.sh` |
| - | `SYSFS_WRITE` (no DM command) | **WRITE** | none | a write into /sys (driver or PCI attributes: reset, remove, rescan, power, link). Never in a run. | - | 1 | `tools/lab/host-recovery/et-boot-check` |
| - | `HOST_REBOOT` (no DM command) | **WRITE** | none | reboot, shutdown, poweroff, systemctl reboot|poweroff|kexec, or an outlet cycle: takes every card on the host. Never (the owner's rules of 2 Nov 2026). | - | 1 | `tools/lab/host-recovery/et-boot-check` |

## A2. The forms of `SET_STATS_RUN_CONTROL` (62): only `STATS_RESET` is the ruled statistics reset

| Form | Type, control | Sent by | What it writes | PMIC | Sites | Where |
|---|---|---|---|---|---|---|
| `STATS_RESET` | 1, 2 | ettelem sample --reset-ms N (N > 0) and --reset-once-file in the reviewed variants that take them (tools/ettelem/ettelem.cpp:91-97, tools/claims-v3/hp/ettelem-hp/ettelem.cpp:69-76, tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp:88-95: in[2] = {1 SP stats, 2 RESET_COUNTER}), and a reset option passed on to a sampler wrapper | The statistics reset, the one form the owner's ruling of 31 Oct 2026 allows: the SP's RAM statistics re-initialised, the PVT controllers' high/low latches re-armed (thermal_pwr_mgmt.c:2828), two PMIC writes (PMB_RW 0x15 := 0x47, the PMIC's stats reset, pmic_controller.c:1801-1805; then 0x15 := 0x43, the snapshot command, :1827-1832), and the SP stats trace switched off (control 2 lacks TRACE_ENABLE, performance.c:556-564). | write | 29 | `tools/claims-v3/dv2/dv2lib.sh` ×3, `tools/claims-v3/hp/a2/hplib.sh` ×3, `tools/claims-v3/hp/hplib.sh` ×3, `tools/claims-v3/oh/ohlib.sh` ×3 and 12 more |
| `SPST_TRACE_CONTROL` | 1, 1 (enable, to_uart, to_memory) or 0 (disable) | dev_mngt_service -t SPST:enable|disable|to_uart|to_memory (device-management-application/src/dev_mngt_service.cc doTraceOperation: enable is on unless the last of enable/disable is disable) | Switches the SP's device-statistics trace on (control 1) or off (control 0) through Trace_Run_Control_SP_Dev_Stats (performance.c:556-564); resets no counter and touches no PMIC. Not the ruled statistics reset: NO-GO in Q136. | none | 2 | `tools/claims-v3/tel/block.sh` ×2 |
| `SPST_RESET` | 1, 7 (6 with disable) | dev_mngt_service -t SPST:reset (with or without enable or disable): RESET_TRACEBUF | RESET_COUNTER, plus TRACE_ENABLE unless disabled | The counters reset (the same Thermal_Pwr_Mgmt_Init_OP_Stats as STATS_RESET: the PVT latches, the PMIC's stats reset and snapshot) plus the SP stats trace buffer reset (Trace_Reset_SP_Dev_Stats_Buffer) and the trace switched on (off with disable). Not the form the owner ruled on: NO-GO in Q136. | write | 0 | none |
| `MMST_CONTROL` | 2, per the operations | dev_mngt_service -t MMST:enable|disable|reset|to_uart|to_memory | Forwarded to the Master Minion's firmware as SP2MM_CMD_MM_STATS_RUN_CONTROL (performance.c:579-599 -> interface/mm_iface.c:413-450): its statistics trace and counters; the Master Minion's handler is not in the service processor's source and was not read. NO-GO in Q136. | none | 0 | none |
| `SET_STATS_RUN_CONTROL` (form not visible) | - | the command's name in code, -o 62, a raw client's 62 | never allowed | - | 0 | none |

## B. The ettelem variants: what each subcommand sends

| Variant (source) | Subcommand | Sends | Source lines | Note |
|---|---|---|---|---|
| `ettelem` | *build directories* | `build/ettelem/`, `live/ettelem-build/` | |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; with `--reset-ms`: `STATS_RESET` | 165-167 |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `temp` | `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER` | 214 |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | 118-121 |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `loglevel` | `SET_DM_TRACE_CONFIG` | 250-259 | every word but 'debug' sets INFO (3) |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 261-266 |  |
| `ettelem-hp` | *build directories* | `build/ettelem-hp/` | |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; with `--reset-ms`: `STATS_RESET` | 143-145 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | 96-99 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `loglevel` | `SET_DM_TRACE_CONFIG` | 220-230 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 232-237 |  |
| `ettelem-dv2` | *build directories* | `build/ettelem-dv2/`, `build/ettelem-e84/`, `build/ettelem-hpl/` | | build/ettelem-hpl/ holds this source, built for E64 (23 Oct 2026) and reused by later runs (E69, E80, E87, E98, E111, E119 and E126 among them; tools/claims-v3/hpl/README.md:54; tools/claims-v3/e126/E126.md:72, binary sha256 77a46171...); the source has not changed since 28 Sep 2026 (commit 8eb0e384) |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; with `--reset-ms` or `--reset-once-file`: `STATS_RESET` | 205-207 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | 157-160 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `residency` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | 114-128 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `uptime` | `GET_MODULE_UPTIME` | 130-137 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `threshold` | `GET_MODULE_TEMPERATURE_THRESHOLDS` | 139-144 | 'threshold set' is refused before the node opens (:267-279) |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `loglevel` | `SET_DM_TRACE_CONFIG` | 345-356 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 357-363 |  |
| `ettelem-e77` | *build directories* | `build/ettelem-e77/` | |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES` | 169-170 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES` | 137-139 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `residency` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | 86-94 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `uptime` | `GET_MODULE_UPTIME` | 126 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 260-266 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `profile` | nothing | 207 | prints its list; opens nothing |
| `ettelem-e118` | *build directories* | `build/ettelem-e118/` | |  |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES` | 217-221 | --reset-ms and --reset-once-file are refused at parse time (:325-329) |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES` | 168-170 |  |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `residency` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | 125-139 |  |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `uptime` | `GET_MODULE_UPTIME` | 141-148 |  |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `threshold` | `GET_MODULE_TEMPERATURE_THRESHOLDS` | 150-155 |  |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 378-384 |  |
| `ettelem-e118` (`tools/claims-v3/e118/ettelem-e118/ettelem.cpp`) | `loglevel` | nothing | 345-348 | refused before the node opens; the SET_DM_TRACE_CONFIG at :373 is unreachable |

## C. Every write site in the lab's code

| Command | Class | Site | Detail |
|---|---|---|---|
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/e114/run_e114.sh:52` | name |
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/hlp/run_e79.sh:49` | name |
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/kspeed/e84/run_e84.sh:64` | name |
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/lq6/gov_e72.py:156` | name |
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/nv/block.sh:536` | name |
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/nv/stubs/stub-dms:128` | name |
| `GET_MODULE_FIRMWARE_REVISIONS` | WRITE | `tools/claims-v3/tel/block.sh:332` | name |
| `HOST_REBOOT` | WRITE | `tools/lab/host-recovery/et-boot-check:149` | host; systemctl --no-block reboot |
| `RESET_ETSOC` | WRITE | `tools/lab/et-reset:83` | name |
| `RESET_ETSOC` | WRITE | `tools/lab/et-reset:112` | name |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:172` | ettelem loglevel; variant ettelem-dv2 |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:167` | ettelem loglevel; variant ettelem-hp |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/hp/hplib.sh:172` | ettelem loglevel; variant ettelem-hp |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:186` | ettelem loglevel; variant ettelem |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:316` | ettelem loglevel; variant ettelem |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:379` | ettelem loglevel; variant ettelem |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:408` | ettelem loglevel; variant ettelem |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e118/gov_e118.py:162` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e118/gov_e118.py:164` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e118/gov_e118.py:198` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e118/gov_e118.py:209` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e120/run_e120.py:945` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e120/run_e120.py:999` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e77/run_e77.py:891` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/e77/run_e77.py:945` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/knob/run_knob.py:76` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/lq6/gov_e72.py:175` | name |
| `SET_MODULE_STATIC_TDP_LEVEL` | WRITE | `tools/claims-v3/lq6/gov_e72.py:203` | name |
| `SET_MODULE_TEMPERATURE_THRESHOLDS` | WRITE | `tools/claims-v3/knob/run_knob.py:76` | name |
| `SET_MODULE_VOLTAGE` | WRITE | `tools/claims-v3/nv/block.sh:198` | name |
| `SET_MODULE_VOLTAGE` | WRITE | `tools/claims-v3/nv/stubs/stub-dms:81` | name |
| `SPST_TRACE_CONTROL` | WRITE | `tools/claims-v3/tel/block.sh:185` | dev_mngt_service -t; SPST:enable: DM_CMD_SET_STATS_RUN_CONTROL type 1, control 1 |
| `SPST_TRACE_CONTROL` | WRITE | `tools/claims-v3/tel/block.sh:194` | dev_mngt_service -t; SPST:enable: DM_CMD_SET_STATS_RUN_CONTROL type 1, control 1 |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2/block.sh:97` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2/block.sh:98` | ettelem sample; variant ettelem-dv2 |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:49` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:50` | reset option passed on; --reset-once-file : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:296` | reset option passed on; --reset-once-file        : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2v/block.sh:99` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/dv2v/block.sh:100` | ettelem sample; variant ettelem-dv2 |
| `STATS_RESET` | WRITE | `tools/claims-v3/e100/run_e100.py:124` | ettelem sample; variant ettelem/ettelem-dv2 |
| `STATS_RESET` | WRITE | `tools/claims-v3/hlc/run_hlc.py:1176` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp |
| `STATS_RESET` | WRITE | `tools/claims-v3/hlc/run_hlc.py:1209` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hm/run_hm.py:1164` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp |
| `STATS_RESET` | WRITE | `tools/claims-v3/hm/run_hm.py:1197` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:62` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:63` | reset option passed on; --reset-ms    : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:394` | reset option passed on; --reset-ms            : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hp/hplib.sh:67` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hp/hplib.sh:68` | reset option passed on; --reset-ms    : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/hp/hplib.sh:420` | reset option passed on; --reset-ms            : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/lib.sh:154` | ettelem sample; variant ettelem; forwarded arguments may carry --reset-ms |
| `STATS_RESET` | WRITE | `tools/claims-v3/oh/ohlib.sh:50` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/oh/ohlib.sh:51` | reset option passed on; --reset-ms    : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/oh/ohlib.sh:361` | reset option passed on; --reset-ms            : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/oh/prereg.py:74` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp |
| `STATS_RESET` | WRITE | `tools/claims-v3/tel/block.sh:361` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/claims-v3/tel/block.sh:397` | reset option passed on; --reset-ms 600000: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/ettelem/deconv.py:55` | reset option passed on; --reset-ms since_reset_ms: a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/lab/motd-aifoundry1:21` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/lab/motd-aifoundry2:17` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `STATS_RESET` | WRITE | `tools/lab/motd-aifoundry3:14` | reset option passed on; --reset-ms : a sampler wrapper forwards it to ettelem sample |
| `SYSFS_WRITE` | WRITE | `tools/lab/host-recovery/et-boot-check:148` | sysfs; echo cold > /sys/kernel/reboot/mode && echo pci > /sys/kernel/reboot/type |

## D. Reads with a side effect that blocks a launch

| Site | Command | Tag | Detail |
|---|---|---|---|
| `tools/claims-v3/dv2/dv2lib.sh:177` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem-dv2; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/dv2/z2.sh:73` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem-dv2; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/e120/run_e120.py:740` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | RESIDENCY_STATES_UNRESOLVED | variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp; states not literal on the line |
| `tools/claims-v3/e77/run_e77.py:686` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp; raw states 2 3 4 (raw 4 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/hpl/run_hpl.py:622` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem-dv2; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/knob/run_knob.py:658` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem-dv2; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |

## E. ettelem calls whose build the checker cannot see, and wrappers a person reads

A binary chosen at run time (a protocol's or a host config's path, an environment variable) is `VARIANT_UNRESOLVED`, NO-GO until the runner names its source with `--variant-source` (the source's sha256 must equal a reviewed variant's); a line that forwards its arguments (`"$@"`, `*args`) or takes the command from a variable is a `WRAPPER` for a person to read, and its calls in the same file are classified through it.

| Site | Tag | Detail |
|---|---|---|
| `scripts/mmbench-power.py:60` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `tools/claims-v3/dv2/z2.sh:66` | `WRAPPER` | ettelem (arguments forwarded); the subcommand comes from '$@': classified at the call sites of run |
| `tools/claims-v3/e118/gov_e118.py:166` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `tools/claims-v3/e120/run_e120.py:523` | `VARIANT_UNRESOLVED` | ettelem profile; binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:628` | `VARIANT_UNRESOLVED` | ettelem sample; binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:673` | `WRAPPER` | ettelem (arguments forwarded); the subcommand comes from '*args': classified at the call sites of tool |
| `tools/claims-v3/e120/run_e120.py:673` | `VARIANT_UNRESOLVED` | ettelem (arguments forwarded); binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:683` | `VARIANT_UNRESOLVED` | ettelem config (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:694` | `VARIANT_UNRESOLVED` | ettelem uptime (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:711` | `VARIANT_UNRESOLVED` | ettelem sptrace (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:740` | `VARIANT_UNRESOLVED` | ettelem residency (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e120/run_e120.py:999` | `VARIANT_UNRESOLVED` | ettelem config; binary from '{self.ettelem!r}' ('{self.ettelem!r}': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:495` | `VARIANT_UNRESOLVED` | ettelem profile; binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:595` | `VARIANT_UNRESOLVED` | ettelem sample; binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:640` | `WRAPPER` | ettelem (arguments forwarded); the subcommand comes from '*args': classified at the call sites of tool |
| `tools/claims-v3/e77/run_e77.py:640` | `VARIANT_UNRESOLVED` | ettelem (arguments forwarded); binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:650` | `VARIANT_UNRESOLVED` | ettelem config (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:661` | `VARIANT_UNRESOLVED` | ettelem uptime (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:678` | `VARIANT_UNRESOLVED` | ettelem sptrace (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:686` | `VARIANT_UNRESOLVED` | ettelem residency (wrapper call tool); binary from 'tool' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/e77/run_e77.py:945` | `VARIANT_UNRESOLVED` | ettelem config; binary from '{self.ettelem!r}' ('{self.ettelem!r}': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/hlc/run_hlc.py:1176` | `VARIANT_UNRESOLVED` | ettelem sample; binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/hlp/run_e79.sh:52` | `WRAPPER` | dev_mngt_service -m; command from '$c': classified at the call sites that name it |
| `tools/claims-v3/hm/run_hm.py:1164` | `VARIANT_UNRESOLVED` | ettelem sample; binary from 'self.ettelem' ('self.ettelem': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/claims-v3/knob/run_knob.py:825` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `tools/claims-v3/knob/run_knob.py:856` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `tools/claims-v3/lq6/gov_e72.py:99` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `tools/lab/dashboard/remote.sh:459` | `VARIANT_UNRESOLVED` | ettelem sample; binary from '$bin' ('$bin': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `tools/lab/dashboard/remote.sh:469` | `VARIANT_UNRESOLVED` | ettelem sample; binary from '$bin' ('$bin': no binary path the checker can see): which build runs is not visible; its sends are listed as the reviewed variants' |
| `workloads/memhier/run_energy.py:42` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `workloads/memhier/run_energy.py:55` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `workloads/nocbench/run_energy.py:56` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `workloads/nocbench/run_energy.py:69` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `workloads/sparsity/run_energy.py:53` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |
| `workloads/sparsity/run_energy.py:64` | `WRAPPER` | dev_mngt_service -m; command from 'cmd': classified at the call sites that name it |

## F. Code kept with the records under docs/ (copies of what ran, page tools, desk scripts)

`dmcmd_audit.py` over the 445 tracked code files under `docs/` (docs-scanned-files.txt, inventory-docs.json). These are records, not runners: a run's generated scripts as they ran, a page's example tools, and desk scripts that name commands in strings. *Sends* marks the files that run something.

| File | Commands | Sends |
|---|---|---|
| `docs/reports/2026-10-08-how-energy-is-measured/etpower.py` | `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER`, `GET_SP_STATS` | yes |
| `docs/reports/2026-10-08-how-energy-is-measured/measure.sh` | `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER`, `GET_MODULE_VOLTAGE`, `GET_SP_STATS` | yes |
| `docs/reports/data/2026-09-30-without-heatsink/lowclock_calc.py` | `SET_FREQUENCY` | no: names the commands in strings (read by hand) |
| `docs/reports/data/2026-10-31-e83-kinds-speed-rest/corrections-check.py` | `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER`, `GET_MODULE_VOLTAGE`, `GET_SP_STATS` | no: names the commands in strings (read by hand) |
| `docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/corrections-check.py` | `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER`, `GET_MODULE_VOLTAGE`, `GET_SP_STATS` | no: names the commands in strings (read by hand) |
| `docs/reports/data/2026-10-31-e85-camera-kinds/corrections-check.py` | `SET_STATS_RUN_CONTROL` | no: names the commands in strings (read by hand) |
| `docs/reports/data/2026-11-01-e113-a-side-saturation/corrections-check.py` | `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`, `GET_MODULE_POWER_STATE`, `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_VOLTAGE`, `SET_STATS_RUN_CONTROL` | no: names the commands in strings (read by hand) |
| `docs/reports/data/2026-11-01-e114-card0-replicates/corrections-check.py` | `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`, `GET_MODULE_FIRMWARE_REVISIONS`, `GET_MODULE_POWER_STATE`, `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS` | no: names the commands in strings (read by hand) |
| `docs/reports/data/2026-11-01-e118-two-clock-card0/session/watchdog.sh` | `GET_ASIC_FREQUENCIES`, `GET_MODULE_POWER_STATE`, `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `SET_MODULE_STATIC_TDP_LEVEL` | yes |
| `docs/reports/data/2026-11-01-e120-rail-redesign/raw/watchdog.sh` | `GET_ASIC_FREQUENCIES`, `GET_MODULE_POWER_STATE`, `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `SET_MODULE_STATIC_TDP_LEVEL` | yes |
| `docs/reports/data/2026-11-01-e77-rail-one-temperature/raw/watchdog.sh` | `GET_ASIC_FREQUENCIES`, `GET_MODULE_POWER_STATE`, `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `SET_MODULE_STATIC_TDP_LEVEL` | yes |
| `docs/reports/sources/dvfs-leakage.script.js` | `RESET_ETSOC` | no: names the commands in strings (read by hand) |
| `docs/reports/sources/power-temperature.script.js` | `GET_ASIC_VOLTAGE`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER`, `GET_MODULE_POWER_STATE`, `GET_MODULE_VOLTAGE`, `GET_SP_STATS`, `SET_DM_TRACE_CONFIG`, `SET_FREQUENCY` | no: names the commands in strings (read by hand) |

*The files that send use no command outside those the lab's runners send.*

*Table: 92 commands (READ 46, UNCLASSIFIED 1, UNSUPPORTED 5, WRITE 40); inventory: 1599 files scanned, 132 with a send site, 950 records (874 at a line, the rest from reviewed sources taken from the table); docs/: 445 files, 13 with a record.*
