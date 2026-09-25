# Firmware on the cards (queried 2026-09-25 07:25, both cards, read-only management commands)

Command: /opt/et/bin/dev_mngt_service -m <cmd> -n 0 -u 5000

| | aifoundry2 | aifoundry3 |
|---|---|---|
| Firmware release revision | 1.3.1 | 1.3.1 |
| BL1 / BL2 (service processor) | 0.20.0 / 0.20.0 | 0.20.0 / 0.20.0 |
| PMIC firmware | 1.5.0 | 1.5.0 |
| Master / worker / machine minion | 0.23.0 each | 0.23.0 each |
| ASIC revision | 597 | 597 |
| Module revision (asset output) | 0x2211ab44 | 0x2211ab44 |

Mapping to external/et-platform history:
- device-bootloaders 0.20.0 development: 11b0b6966 (2024-04-29) .. cafe03fc3 (2024-05-17, "Start development of version 0.21.0")
- device-minion-runtime 0.23.0 development: d68f7af93 (2024-03-27) .. 9e61967f1 (2024-05-17, "0.24.0")
=> the cards run a build of about mid-May 2024; closest source: cafe03fc3^ (both components).

The findings read the governor at 353f20e (2025-12-28). Between cafe03fc3 and 353f20e, thermal_pwr_mgmt.c has 9 commits
(685+/805-): 8d81bd343 over-power/over-temperature events (2024-06-07), a31928492 reduce operating point (2024-08-28),
e024210bc power safe state, f48cbbb80 power threshold values (2024-09-05), 60b40c10f DVFS fixes and refactoring
(2024-09-24), 7c6049087 thermal monitor retry (2024-10-10), 444e4e124 voltage validation, 478275330
check_power_throttle_condition conversion (2024-11-26), f67ae338c licensing. performance.c 1 commit, dm_task.c 2.
So every R3 (governor-from-source) statement must be re-checked against cafe03fc3^, not 353f20e.
Identical firmware on both cards => the cards' different governor behaviour (aifoundry3 pinned at 600 MHz, TDP 0 W)
is configuration (flashed TDP), not firmware version.

## The governor in the cards' build (cafe03fc3^, thermal_pwr_mgmt.c; extracted to fw-may2024/)

- Thresholds as in 353f20e: TEMP_THRESHOLD_SW_MANAGED 65, POWER_THRESHOLD_SW_MANAGED 65 (W), catastrophic 75/75,
  DM_TASK_DELAY_MS 10, POWER_GUARDBAND_SCALE_FACTOR 5.
- **Power trigger uses the instantaneous SoC power.** update_module_soc_power() (l.788-806) reads
  pmic_read_average_soc_power() into op_stats.system.power.avg, then overwrites the same local soc_pwr_10mW with
  pmic_read_instantaneous_soc_power(); the tests at l.862 (> tdp: POWER_DOWN) and l.876 (< tdp: POWER_UP) use that
  instantaneous value. In 353f20e check_power_throttle_conditions() uses op_stats.system.power.avg (the PMIC average).
  => "the loop's power input is pmic_read_average_soc_power()" (05-claims l.167) is the newer source, not the cards.
- Once in a power throttle state, the power-throttling routine steps the operating point and re-reads the AVERAGE:
  POWER_UP ends when avg > tdp or at max frequency; POWER_DOWN/SAFE ends when avg < 1.05 x tdp
  (UPPER_POWER_THRESHOLD_GUARDBAND, l.2241) or at the safe frequency. So a guardband exists on exit from a step-down.
- Thermal priority: the power branch runs only while power_throttle_state < THERMAL_DOWN (l.845), as in 353f20e.
- Thermal: enter THERMAL_DOWN when the minion average temperature > 65 (l.668, strict, no dead band); the thermal
  loop reduces the operating point while temp > 65, sleeping DELTA_TEMP_UPDATE_PERIOD between steps, then goes to
  THERMAL_IDLE.
- Idle: mm_state == IDLE -> POWER_IDLE -> go_to_idle_state() = set_minion_operating_point(boot freq) (l.1975), as claimed.
- TDP 0 (aifoundry3): instantaneous > 0 always -> POWER_DOWN whenever state < POWER_DOWN; < 0 never -> no step up. The
  claim holds in the cards' build too.
