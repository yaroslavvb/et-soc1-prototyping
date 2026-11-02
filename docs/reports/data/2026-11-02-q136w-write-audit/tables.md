## A. Every command the lab's code can send, classified from et-platform `836a4ab` (BL2 0.22.0)

Handler paths are under `device-bootloaders/src/ServiceProcessorBL2/`. *Sites* counts the lines in this repository's tracked code that can send the command (inventory.json); *where* names the files with the most.

| Id | Command | Class | PMIC | Handler at `836a4ab` | Side effects | Sites | Where |
|---|---|---|---|---|---|---|---|
| 14 | `GET_MODULE_FIRMWARE_REVISIONS` | **WRITE** | write | services/firmware_update.c:862-915; :903 pmic_get_fw_version -> driver/pmic_controller.c:952-974 -> pmic_get_active_boot_slot :2531-2557 (set_pmic_reg(PMIC_I2C_FW_MGMTCMD_ADDRESS 0x16, ACTIVE_SLOT 7) at :2543, data read at :2549) and pmic_fw_update_subcommand :2581-2600 (set_pmic_reg(0x16, VERSION 5 | slot) at :2587, data read at :2591) | - | 7 | `tools/claims-v3/e114/run_e114.sh`, `tools/claims-v3/hlp/run_e79.sh`, `tools/claims-v3/kspeed/e84/run_e84.sh`, `tools/claims-v3/lq6/gov_e72.py` and 3 more |
| 22 | `SET_MODULE_TEMPERATURE_THRESHOLDS` | **WRITE** | none | services/thermal_power_monitor.c:493-521 -> services/thermal_pwr_mgmt.c:638-643 (RAM, no range check in the SP; libDM refuses outside 20-125 C) | - | 1 | `tools/claims-v3/knob/run_knob.py` |
| 26 | `SET_MODULE_STATIC_TDP_LEVEL` | **WRITE** | none | services/thermal_power_monitor.c:392-415 -> services/thermal_pwr_mgmt.c:576-591 (refuses > 75 W, else one INFO log and the RAM assignment) | - | 11 | `tools/claims-v3/e118/gov_e118.py` ×4, `tools/claims-v3/e120/run_e120.py` ×2, `tools/claims-v3/e77/run_e77.py` ×2, `tools/claims-v3/lq6/gov_e72.py` ×2 and 1 more |
| 35 | `SET_MODULE_VOLTAGE` | **WRITE** | write | services/thermal_power_monitor.c:294-316 -> services/thermal_pwr_mgmt.c:3008-3048 -> pmic_set_voltage (:3021; driver/pmic_controller.c:1586) | - | 2 | `tools/claims-v3/nv/block.sh`, `tools/claims-v3/nv/stubs/stub-dms` |
| 52 | `RESET_ETSOC` | **WRITE** | write | services/firmware_update.c:1125 -> :45-105: if the PMIC firmware was updated, pmic_force_power_off_on() (a power cycle, driver/pmic_controller.c:2272); else the PMIC watchdog is armed (pmic_enable_wdog_timeout_reset, pmic_set_wdog_timeout_time) and pmic_force_reset() (:2298) | - | 2 | `tools/lab/et-reset` ×2 |
| 62 | `SET_STATS_RUN_CONTROL` | **WRITE** | write | services/performance.c:546-636. With type SP and control RESET_COUNTER: Thermal_Pwr_Mgmt_Init_OP_Stats (:575 -> services/thermal_pwr_mgmt.c:2805-2880): the RAM op_stats re-initialised, pvt_hilo_reset() (:2828, writes the PVT controllers' high/low latches, driver/pvt_controller.c:1071-1081), PMIC reads (temperature :2838, PMB stats, average power :2874) and update_pmb_stats(true) (:2846 -> :1334-1350 -> driver/pmic_controller.c:1801-1805: set_pmic_reg(PMB_RW 0x15, 0x47), the PMIC's stats reset). And any control word WITHOUT bit 0 (TRACE_ENABLE) switches the SP's device-statistics trace OFF (performance.c:556-564 -> services/trace.c:654-661); Trace_Init at boot leaves it on. | - | 31 | `tools/claims-v3/tel/block.sh` ×4, `tools/claims-v3/dv2/dv2lib.sh` ×3, `tools/claims-v3/hp/a2/hplib.sh` ×3, `tools/claims-v3/hp/hplib.sh` ×3 and 12 more |
| 67 | `SET_DM_TRACE_CONFIG` | **WRITE** | none | services/trace.c:474-479 -> :183-207 (sets the SP trace's event and filter masks and the SP log level, RAM; it stays until the next boot or set) | - | 7 | `tools/claims-v3/tel/block.sh` ×4, `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/hp/a2/hplib.sh`, `tools/claims-v3/hp/hplib.sh` |
| 3 | `GET_ASIC_CHIP_REVISION` | **READ** | none | services/asset_track.c:39 -> services/asset_track_mgmt.c:52 -> driver/bl2_otp.c:141 -> shared/common/src/sp_otp.c:1394 (OTP read) | - | 2 | `tools/claims-v3/hlp/run_e79.sh`, `tools/claims-v3/lq6/gov_e72.py` |
| 21 | `GET_MODULE_TEMPERATURE_THRESHOLDS` | **READ** | none | services/thermal_power_monitor.c:438 -> services/thermal_pwr_mgmt.c:665-669 (RAM: g_soc_power_reg.temperature_threshold) | - | 108 | `tools/claims-v3/e114/run_e114.sh` ×4, `tools/claims-v3/kspeed/e84/run_e84.sh` ×4, `tools/claims-v3/cat/block.sh` ×2, `tools/claims-v3/e107/block_e107.sh` ×2 and 66 more |
| 23 | `GET_MODULE_POWER_STATE` | **READ** | none | services/thermal_power_monitor.c:48 -> services/thermal_pwr_mgmt.c:551-555 (RAM) | - | 104 | `tools/claims-v3/e114/run_e114.sh` ×4, `tools/claims-v3/kspeed/e84/run_e84.sh` ×4, `tools/claims-v3/cat/block.sh` ×2, `tools/claims-v3/e107/block_e107.sh` ×2 and 65 more |
| 25 | `GET_MODULE_STATIC_TDP_LEVEL` | **READ** | none | services/thermal_power_monitor.c:339 -> services/thermal_pwr_mgmt.c:613-617 (RAM: g_pmic_power_reg.module_tdp_level) | - | 106 | `tools/claims-v3/e114/run_e114.sh` ×4, `tools/claims-v3/kspeed/e84/run_e84.sh` ×4, `tools/claims-v3/cat/block.sh` ×2, `tools/claims-v3/e107/block_e107.sh` ×2 and 65 more |
| 27 | `GET_MODULE_CURRENT_TEMPERATURE` | **READ** | none | services/thermal_power_monitor.c:545 -> services/thermal_pwr_mgmt.c:732-773 (PVT register reads, driver/pvt_controller.c:618-643, 659-664, 1274-1340) | refreshes the SP's own RAM copy of the die temperature (g_pmic_power_reg.soc_temperature, thermal_pwr_mgmt.c:754) with the value just read, as its own task does every pass | 61 | `tools/claims-v3/lib.sh` ×3, `tools/claims-v3/nv/block.sh` ×3, `scripts/mmbench-power.py` ×2, `tools/claims-v3/tau/block.sh` ×2 and 45 more |
| 29 | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | **READ** | none | services/thermal_power_monitor.c:596-618 -> services/thermal_pwr_mgmt.c:1477-1502 (RAM copies) | a raw state outside 0-3 (the enum at device-api/include/management-api/device_mgmt_api_spec.h:278-286) takes the default branch: two ERROR log lines (thermal_pwr_mgmt.c:1499 and thermal_power_monitor.c:607), so two SP_RUNTIME_ERROR events and two counts on the SP's error counter per state read (E77's F1; Q134(a): 4,228 events = 2 x 2,114 invalid-state reads on aifoundry2) | 5 | `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/e120/run_e120.py`, `tools/claims-v3/e77/run_e77.py`, `tools/claims-v3/hpl/run_hpl.py` and 1 more |
| 30 | `GET_MODULE_UPTIME` | **READ** | none | services/thermal_power_monitor.c:698 -> services/thermal_pwr_mgmt.c:1451-1455 (RAM, updated by the SP's task, :1406-1426) | - | 11 | `tools/claims-v3/nv/block.sh` ×2, `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/e114/run_e114.sh`, `tools/claims-v3/e118/gov_e118.py` and 6 more |
| 31 | `GET_MODULE_VOLTAGE` | **READ** | read (9 register reads) | services/thermal_power_monitor.c:243 -> services/thermal_pwr_mgmt.c:1010-1140: nine pmic_get_voltage calls (DDR, L2 cache, Maxion, Minion, PCIe, NoC, PCIe logic, VDDQLP, VDDQ) -> driver/pmic_controller.c:1473-1500 -> get_pmic_reg (:254-300, an I2C register read) | refreshes the SP's RAM copy g_pmic_power_reg.module_voltage with the values read | 53 | `tools/claims-v3/lib.sh` ×3, `tools/claims-v3/nv/block.sh` ×3, `tools/claims-v3/tau/block.sh` ×2, `tools/ettelem/run_vf_cold.sh` ×2 and 41 more |
| 32 | `GET_ASIC_VOLTAGE` | **READ** | read (2 register reads) | services/thermal_power_monitor.c:192 -> services/thermal_pwr_mgmt.c:1142-1222: PVT voltage-monitor reads, then pmic_get_voltage(VDDQLP) and (VDDQ) at :1213 and :1215 | refreshes the SP's RAM copy g_soc_power_reg.asic_voltage | 159 | `tools/claims-v3/e114/run_e114.sh` ×4, `tools/claims-v3/kspeed/e84/run_e84.sh` ×4, `tools/claims-v3/e120/run_e120.py` ×3, `tools/claims-v3/e77/run_e77.py` ×3 and 106 more |
| 33 | `GET_MODULE_POWER` | **READ** | none | services/thermal_power_monitor.c:142 -> services/thermal_pwr_mgmt.c:984-988 (RAM copy the SP's task keeps from the PMIC) | - | 79 | `tools/claims-v3/lib.sh` ×5, `tools/claims-v3/tau/block.sh` ×4, `tools/claims-v3/nv/block.sh` ×3, `tools/claims-v3/hlc/run_hlc.py` ×2 and 53 more |
| 53 | `GET_ASIC_FREQUENCIES` | **READ** | none | services/performance.c:41 -> services/perf_mgmt.c:276- -> driver/io_pll.c:907-960 (PLL register reads) | refreshes the SP's RAM copy of the clocks (get_soc_perf_reg()->asic_frequency) | 167 | `tools/claims-v3/e114/run_e114.sh` ×4, `tools/claims-v3/kspeed/e84/run_e84.sh` ×4, `tools/claims-v3/e120/run_e120.py` ×3, `tools/claims-v3/e77/run_e77.py` ×3 and 109 more |
| 60 | `GET_SP_STATS` | **READ** | none | services/performance.c:404-466 -> services/thermal_pwr_mgmt.c:2780-2784 (a copy of the RAM op_stats the SP's task keeps) | - | 50 | `tools/claims-v3/lib.sh` ×3, `tools/claims-v3/nv/block.sh` ×2, `tools/claims-v3/tau/block.sh` ×2, `tools/ettelem/run_vf_cold.sh` ×2 and 39 more |
| 69 | `GET_SHIRE_CACHE_CONFIG` | **READ** | none | driver/bl2_cache_control.c:880 -> driver/flashfs.c:1937-1945 (RAM copy) | - | 1 | `workloads/memhier/run_energy.py` |
| 73 | `GET_VMIN_LUT` | **READ** | none | services/asset_track.c:74 -> driver/flashfs.c:2073-2080 (RAM copy of the persistent config) | - | 9 | `tools/claims-v3/e118/gov_e118.py` ×2, `tools/claims-v3/e120/run_e120.py` ×2, `tools/claims-v3/e77/run_e77.py` ×2, `tools/claims-v3/lq6/gov_e72.py` and 2 more |
| 74 | `GET_ASIC_PVT_SAMPLES` | **UNCLASSIFIED** | unknown | not in 836a4ab: command 74 exists only in the maintainer's raw-temperature patch, whose source is not public | - | 0 | none |
| - | `TRACE_EXTRACT` (no DM command) | **READ** | none | dev_mngt_service -t <type>:extract and ettelem sptrace: no DM command; two driver ioctls (ETSOC1_IOCTL_GET_TRACE_BUFFER_SIZE, ETSOC1_IOCTL_EXTRACT_TRACE_BUFFER) copy a trace region over PCIe (devicelayer/src/DevicePcie.cpp:822-835; et-driver/et-soc1-pcie.c:1021-1077, et_ioread) | - | 12 | `tools/claims-v3/tel/block.sh` ×3, `tools/claims-v3/dv2/dv2lib.sh`, `tools/claims-v3/e120/run_e120.py`, `tools/claims-v3/e77/run_e77.py` and 6 more |
| - | `ETCFG` (no DM command) | **READ** | none | tools/etcfg: ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION, a read-only driver ioctl (tools/etcfg/etcfg.c:28) | - | 1 | `tools/claims-v3/tel/block.sh` |
| - | `SYSFS_WRITE` (no DM command) | **WRITE** | none | a write into /sys (driver or PCI attributes: reset, remove, rescan, power, link). Never in a run. | - | 1 | `tools/lab/host-recovery/et-boot-check` |
| - | `HOST_REBOOT` (no DM command) | **WRITE** | none | reboot, shutdown, poweroff, systemctl reboot|poweroff|kexec, or an outlet cycle: takes every card on the host. Never (the owner's rules of 2 Nov 2026). | - | 1 | `tools/lab/host-recovery/et-boot-check` |

## B. The ettelem variants: what each subcommand sends

| Variant (source) | Subcommand | Sends | Source lines | Note |
|---|---|---|---|---|
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; with `--reset-ms`: `SET_STATS_RUN_CONTROL` | 165-167 |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `temp` | `GET_MODULE_CURRENT_TEMPERATURE`, `GET_MODULE_POWER` | 214 |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | 118-121 |  |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `loglevel` | `SET_DM_TRACE_CONFIG` | 250-259 | every word but 'debug' sets INFO (3) |
| `ettelem` (`tools/ettelem/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 261-266 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; with `--reset-ms`: `SET_STATS_RUN_CONTROL` | 143-145 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | 96-99 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `loglevel` | `SET_DM_TRACE_CONFIG` | 220-230 |  |
| `ettelem-hp` (`tools/claims-v3/hp/ettelem-hp/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 232-237 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; with `--reset-ms` or `--reset-once-file`: `SET_STATS_RUN_CONTROL` | 205-207 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE` | 157-160 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `residency` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | 114-128 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `uptime` | `GET_MODULE_UPTIME` | 130-137 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `threshold` | `GET_MODULE_TEMPERATURE_THRESHOLDS` | 139-144 | 'threshold set' is refused before the node opens (:267-279) |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `loglevel` | `SET_DM_TRACE_CONFIG` | 345-356 |  |
| `ettelem-dv2` (`tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 357-363 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `sample` | `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES` | 169-170 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `config` | `GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES` | 137-139 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `residency` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | 86-94 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `uptime` | `GET_MODULE_UPTIME` | 126 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `sptrace` | `TRACE_EXTRACT` | 260-266 |  |
| `ettelem-e77` (`tools/claims-v3/e77/ettelem-e77/ettelem.cpp`) | `profile` | nothing | 207 | prints its list; opens nothing |
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
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:186` | ettelem loglevel; variant ettelem/ettelem-dv2/ettelem-e118 |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:316` | ettelem loglevel; variant ettelem/ettelem-dv2/ettelem-e118 |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:379` | ettelem loglevel; variant ettelem/ettelem-dv2/ettelem-e118 |
| `SET_DM_TRACE_CONFIG` | WRITE | `tools/claims-v3/tel/block.sh:408` | ettelem loglevel; variant ettelem/ettelem-dv2/ettelem-e118 |
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
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2/block.sh:97` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2/block.sh:98` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118 |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:49` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:50` | reset option passed on; --reset-once-file : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2/dv2lib.sh:296` | reset option passed on; --reset-once-file        : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2v/block.sh:99` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/dv2v/block.sh:100` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118 |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/e100/run_e100.py:124` | ettelem sample; variant ettelem |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hlc/run_hlc.py:1176` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hlc/run_hlc.py:1209` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hm/run_hm.py:1164` | ettelem sample; variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hm/run_hm.py:1197` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:62` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:63` | reset option passed on; --reset-ms    : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hp/a2/hplib.sh:394` | reset option passed on; --reset-ms            : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hp/hplib.sh:67` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hp/hplib.sh:68` | reset option passed on; --reset-ms    : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/hp/hplib.sh:420` | reset option passed on; --reset-ms            : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/lib.sh:154` | ettelem sample; variant ettelem; forwarded arguments may carry --reset-ms |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/oh/ohlib.sh:50` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/oh/ohlib.sh:51` | reset option passed on; --reset-ms    : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/oh/ohlib.sh:361` | reset option passed on; --reset-ms            : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/oh/prereg.py:74` | ettelem sample; variant ettelem |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/tel/block.sh:185` | dev_mngt_service -t; SPST:enable |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/tel/block.sh:194` | dev_mngt_service -t; SPST:enable |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/tel/block.sh:361` | reset option passed on; --reset-ms 1000: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/claims-v3/tel/block.sh:397` | reset option passed on; --reset-ms 600000: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/ettelem/deconv.py:55` | reset option passed on; --reset-ms since_reset_ms: a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/lab/motd-aifoundry1:21` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/lab/motd-aifoundry2:17` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SET_STATS_RUN_CONTROL` | WRITE | `tools/lab/motd-aifoundry3:14` | reset option passed on; --reset-ms : a sampler wrapper forwards it |
| `SYSFS_WRITE` | WRITE | `tools/lab/host-recovery/et-boot-check:148` | sysfs; echo cold > /sys/kernel/reboot/mode && echo pci > /sys/kernel/reboot/type |

## D. Reads with a side effect that blocks a launch

| Site | Command | Tag | Detail |
|---|---|---|---|
| `tools/claims-v3/dv2/dv2lib.sh:177` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem-dv2; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/e120/run_e120.py:740` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | RESIDENCY_STATES_UNRESOLVED | variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp; states not literal on the line |
| `tools/claims-v3/e77/run_e77.py:686` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp; raw states 2 3 4 (raw 4 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/hpl/run_hpl.py:622` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |
| `tools/claims-v3/knob/run_knob.py:658` | `GET_MODULE_RESIDENCY_THROTTLE_STATES` | SP_ERROR_LOG | variant ettelem/ettelem-dv2/ettelem-e118/ettelem-e77/ettelem-hp; raw states 2 3 4 5 6 (raw 4 5 6 is no state at BL2 0.22.0: 2 SP Runtime Errors each) |

*Table: 92 commands (READ 46, UNCLASSIFIED 1, UNSUPPORTED 5, WRITE 40); inventory: 1599 files scanned, 133 with a send site, 1079 records.*
