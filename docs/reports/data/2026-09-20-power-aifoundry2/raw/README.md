# Raw records of 20 September, recovered 25 September

These files were written on 20 September 2026 by the E5 and E6 runs on aifoundry2 and stayed in that machine's
build tree (`build/pershire/` and `build/thermal1/`, file times 21:20 and 21:12 local). They were not committed with the
session. They are copied here unchanged.

| File | From | What it is | Read by |
|---|---|---|---|
| `sp1.bin` | `build/pershire/sp1.bin` | `ettelem sptrace` dump of the service processor's 4 KB trace ring at DEBUG level: one complete pass of `MS nn Voltage [mV]` lines for all 34 minion shires | `tools/ettelem/parse_sptrace_voltage.py sp1.bin` reproduces `../per-shire-voltage-idle.json` byte for byte |
| `sp2.bin`, `sp3.bin` | `build/pershire/` | the next two dumps, about 0.3 s apart, each holding a later pass | their current readings differ from `sp1.bin`'s in 6 and 7 of the 102 cells, by 1 mV; every low and high is the same (`--compare ../per-shire-voltage-idle.json`; `summary.json` → `voltage_repeat`) |
| `thermal-loads.log` | `build/thermal1/loads.log` | one line per load process of the E5 load step: 8 `MMBENCH` (fp32, 1,024 minions, 5 launches of 100,000 iterations each) and 4 `MEMPROBE` (`dram_seq`, 11 timed launches each) | `tools/ettelem/summarize_power_session.py` → `summary.json` `thermal.loads` |

`run_thermal.sh` cut each load line at 200 (matmul) or 160 (DRAM) characters, so the per-launch start and end times,
wall times and rates are not in `thermal-loads.log`; the script now keeps the lines whole. The same run's
`telemetry.jsonl` and `phases.jsonl` are byte-identical to the committed `../thermal-telemetry.jsonl` and
`../thermal-phases.jsonl`, so they are not copied again.

SHA-256 (`sha256sum -c` format):

    761ecf45ea470e35cce287808dc08132d29afd97b2592b756b8e3396844ffef9  sp1.bin
    92381a0d1b77206b450f36beca6c3ea769feb40665bf0d871378b9db140cf527  sp2.bin
    d4081e72a9097c9b653b6a1996625a2f43f81e0d2b758e28b5302f87e28fbde3  sp3.bin
    07e4a56fd6559fc0c798b2d84152e65b090b19714944a6f9ddaadc601252519d  thermal-loads.log
