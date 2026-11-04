## Device commands sent

Checked with `tools/claims-v3/dmcmd_audit.py` against `dmcmd_table_e144.json` (et-platform `836a4ab`, BL2 0.22.0); allow-list: none. Verdict: **GO**.

| Command | Class | PMIC | Sites | Verdict |
|---|---|---|---|---|
| `STATS_RESET` | WRITE | write | 1 | EXCEPTED |
| `GET_ASIC_FREQUENCIES` | READ | none | 6 | ok |
| `GET_ASIC_PVT_SAMPLES` | READ | none | 1 | ok |
| `GET_ASIC_VOLTAGE` | READ | read | 6 | ok |
| `GET_MODULE_CURRENT_TEMPERATURE` | READ | none | 5 | ok |
| `GET_MODULE_POWER` | READ | none | 7 | ok |
| `GET_MODULE_POWER_STATE` | READ | none | 1 | ok |
| `GET_MODULE_STATIC_TDP_LEVEL` | READ | none | 1 | ok |
| `GET_MODULE_TEMPERATURE_THRESHOLDS` | READ | none | 1 | ok |
| `GET_MODULE_VOLTAGE` | READ | read | 4 | ok |
| `GET_SP_STATS` | READ | none | 5 | ok |

- Excepted after review `tools/claims-v3/lib.sh:154` `STATS_RESET`: STATS_RESET: E154 never calls lib.sh's start_sampler (block_e154.sh starts E89's pvt_sample.py), and ettelem_guard.sh refuses --reset-ms before the device opens
