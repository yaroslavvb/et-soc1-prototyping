# E128: a random sign's rest in fp16, and the part that goes with the sums changing (aifoundry1 card 1, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 5, "Where a random sign's ~5 W goes"**, as it reads at `fbb682f9393b` ("Still open: fp16's rest, which is not located; the part that goes with the sums changing, which needs a held and a walking tile matched in alternations, a card run; the fp16/fp32 moving-sum ratio, not resolved"). Q134's final critic, item 4.*

*Mon 2 Nov 2026 (week 45), Q136. **Registered, not yet run.** The registration is [`tools/claims-v3/e128/E128.md`](../../../../tools/claims-v3/e128/E128.md), with its frozen numbers in [`predictions-e128.json`](../../../../tools/claims-v3/e128/predictions-e128.json), the tiles and every expected accumulator in `e128/e128.json`, the scorer and its self-test. The results, written results-first, replace this paragraph after the session.*

## Device commands sent

Every command the run sends to the card, classified from the source of the running build (card 1: firmware 1.2.0, BL2 0.18.0; the public et-platform 0.18.0 line, `169a17566` to `da192816a`, every function on these paths the same at both ends). The full reading, with the source lines, is [`desk/dmcmd-e128.txt`](desk/dmcmd-e128.txt), from [`desk/dmcmd-e128.py`](desk/dmcmd-e128.py); E128.md § Device commands sent gives the reasons. **The run sends no WRITE.**

| # | sent by | command (id) | class |
|---|---|---|---|
| 1 | `ettelem config` | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25): copies the TDP from SP RAM | READ |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21): copies the threshold from SP RAM | READ |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23): copies the power state from SP RAM | READ |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53): reads the PLL registers | READ |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32): reads the PVT voltage monitors and two PMIC voltage registers (I2C read) | READ (a PMIC voltage read, allowed) |
| 6 | `ettelem sample` | `DM_CMD_GET_MODULE_POWER` (33): copies the board power from SP RAM | READ |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60): copies the SP's statistics, no reset | READ |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27): reads the PVT temperature sensors | READ |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31): reads nine PMIC voltage registers (I2C read) | READ (a PMIC voltage read, allowed) |

READ: the handler writes only its response, its log line and the SP's RAM copy of the value it read; no register's content, flash, configuration, counter or PMIC register. An I2C read sends the register's address in the bus's write phase, and a failed read soft-resets the SP's own I2C controller (an error path, not the PMIC). **Not sent:** the statistics reset (`DM_CMD_SET_STATS_RUN_CONTROL`, 62), the SP log level (`DM_CMD_SET_DM_TRACE_CONFIG`, 67), the trace buffer, the vendor tool `dev_mngt_service`, the firmware-revisions query (14), a raw state-4 residency read, any governor or other set. E128's blocks call the telemetry reader only through `tools/claims-v3/e128/ettelem_guard.sh`, which passes `config` and `sample --seconds --every-ms` and refuses anything else before the device opens, and they replace `lib.sh`'s queue drain (the vendor tool) by a refusal. The workload hosts (`sparsity_host`, E104's read-back host) open only the ops node and send the Master Minion's device-ops commands (DMA writes and reads of device DRAM, kernel launches, the API check, an abort on a 6 s overrun): the workload itself, no device-management command. `et-lab-manifest`, `et-holders` and `et-who` read sysfs and `fuser` and never open a device node.
