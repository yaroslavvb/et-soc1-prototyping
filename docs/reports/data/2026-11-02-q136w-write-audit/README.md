# Q136(w): every device command the lab can send, classified READ or WRITE from the firmware source

*Mon 2 Nov 2026 (week 45), desk only: no card, host or lock was touched, nothing was posted. It answers the owner's
words of that morning, *"continue the experiments but don't do any power cycles, read only PMIC voltage reads should be
fine, take more care for writing commands"*, and item 13 of Q134's final critic ("Owed before the post leans on Q134":
the instructions to send the firmware-revisions query that were still unannotated, and E69's and E72's change records'
"no PMIC command sent").*

## Results

1. **Every command, classified from source.** [`tools/claims-v3/dmcmd_table.json`](../../../../tools/claims-v3/dmcmd_table.json)
   classifies all 92 device-management commands of et-platform `836a4ab` (BL2 0.22.0, the build all four lab cards report
   since 27–31 October), each with its handler's file and lines: **46 READ, 40 WRITE, 5 UNSUPPORTED** (no handler: the
   service processor logs an error and may never reply) **and 1 UNCLASSIFIED** (command 74, which exists only in the
   maintainer's raw-temperature patch). Every command the lab sends but command 74 is traced to the register level; the
   rest are classified at their handler (`depth` in the table says which).
2. **What the lab's code can send.** [`dmcmd_audit.py`](../../../../tools/claims-v3/dmcmd_audit.py) over every tracked code
   file under `tools/`, `scripts/` and `workloads/` (1,599 files, [`scanned-files.txt`](scanned-files.txt)) finds 133 files
   with a send site and 1,079 sites ([`inventory.json`](inventory.json); per command in [`tables.md`](tables.md)): **22 DM
   commands** — 14 READ, 7 WRITE, 1 UNCLASSIFIED — plus two driver reads with no DM command (the trace extract and
   `etcfg`) and two host writes (in the boot-time recovery service). No host program sends a DM command: no workload's C++
   includes the management library, and the vendor runtime they link (et-platform's `esperanto-tools-libs`) has no
   `serviceRequest`.
3. **The writes, and what they reach** (sites: [`tables.md`](tables.md) § C):

   | Command | Reaches | Sent by | Under the owner's rules of 2 Nov |
   |---|---|---|---|
   | `GET_MODULE_FIRMWARE_REVISIONS` | **the PMIC**: writes its firmware-management command register twice (ACTIVE_SLOT, then VERSION), reads the answers (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`, writes at `:2543`, `:2587`) | 6 scripts: `tel/block.sh:332`, `hlp/run_e79.sh:49`, `kspeed/e84/run_e84.sh:64`, `lq6/gov_e72.py:156`, `e114/run_e114.sh:52`, `nv/block.sh:536` (and NV's selftest stand-in `nv/stubs/stub-dms`, which opens no card) | **NO-GO** (a PMIC command, though named GET) |
   | `SET_STATS_RUN_CONTROL` (the statistics reset, `ettelem sample --reset-ms`) | **the PMIC** (its stats reset, `set_pmic_reg(PMB_RW 0x15, 0x47)`, `driver/pmic_controller.c:1801-1805`), the PVT controllers' high/low latches (`pvt_hilo_reset`, `services/thermal_pwr_mgmt.c:2828`), the SP's RAM statistics, and — because the lab's control word 2 lacks TRACE_ENABLE — the SP stats trace, switched off (`services/performance.c:556-564`) | 31 sites: every `--reset-ms` sampler and its wrappers (`lib.sh:154`, `dv2lib.sh`, `hplib.sh`, `ohlib.sh`, …) and `dev_mngt_service -t SPST:enable` (`tel/block.sh:185, 194`) | **allowed** (the owner's ruling of 31 October 2026) |
   | `SET_MODULE_STATIC_TDP_LEVEL`, `SET_MODULE_TEMPERATURE_THRESHOLDS` | the governor's two RAM fields (`services/thermal_pwr_mgmt.c:576-591`, `:638-643`); no flash or PMIC write at this build | the governor-move runners of E69 (`knob/run_knob.py`), E72 (`lq6/gov_e72.py`), E77, E118, E120 | only with the owner's authorization for that run; none in Q136 |
   | `SET_DM_TRACE_CONFIG` (`ettelem loglevel`) | the SP trace's event mask and log level (`services/trace.c:183-207`), kept until the next boot or set; the boot default is WARNING, which the stock `ettelem` cannot restore (it maps every word but `debug` to INFO) | `tel/block.sh` ×4, `dv2/dv2lib.sh:172`, `hp/hplib.sh:172`, `hp/a2/hplib.sh:167` | **NO-GO** in Q136 (a write) |
   | `SET_MODULE_VOLTAGE` | **the PMIC**: a regulator set (`services/thermal_pwr_mgmt.c:3008-3048` → `pmic_set_voltage`) | `nv/block.sh:198` (and its stand-in); NV never ran on a card | **NO-GO** |
   | `RESET_ETSOC` | **a reset through the PMIC**: `pmic_force_power_off_on()` (a power cycle) after a PMIC update, else the PMIC watchdog armed and `pmic_force_reset()` (`services/firmware_update.c:45-105`) | the lab's `tools/lab/et-reset` (the lab admin's tool, run by hand) | **never** (no power cycles, no resets) |
   | host: `systemctl reboot` and `/sys/kernel/reboot/*` | the host | `tools/lab/host-recovery/et-boot-check:148-149`, the boot-time service installed on all three hosts on 26 Oct, which reboots a host cold by itself when a card's link trained badly after a boot | never in a run; it acts only after a boot |

   **No write in the lab's code reaches flash or persistent configuration.** Every flash or NVM writer of the firmware
   (`SET_FIRMWARE_UPDATE`, `SET_VMIN_LUT`, `SET_MODULE_PART_NUMBER`, `SET_SHIRE_CACHE_CONFIG`, `SET_FRU`, the
   certificate and counter sets) has no site. **A second GET writes the PMIC**: `GET_FRU` sets the PMIC's FRU command and
   offset registers before each byte it reads (`driver/pmic_controller.c:2412-2467`); the lab never sends it.
4. **The reads that reach the PMIC are reads**: `GET_ASIC_VOLTAGE` makes two PMIC voltage-register reads
   (`services/thermal_pwr_mgmt.c:1213, 1215`) and `GET_MODULE_VOLTAGE` nine (`:1010-1140`), each an I2C register read with
   no write (`driver/pmic_controller.c:254-300, 1473-1500`). The stock `ettelem config` sends the first and every stock
   `ettelem sample` both: allowed by the owner's rule of 2 November.
5. **Reads with a side effect.** A residency read of a raw throttle state BL2 0.22.0 does not have (raw 4–6: its states
   are 0 IDLE, 1 UP, 2 DOWN, 3 SAFE) takes the error branch twice (`services/thermal_pwr_mgmt.c:1499`,
   `services/thermal_power_monitor.c:607`), and every ERROR log line increments the SP's runtime-error counter and sends one
   `SP_RUNTIME_ERROR` event to the host (`services/log.c:240-249, 414-436`; `RT_ERROR_THRESHOLD` 0): two events a state
   read, as E77's F1 and Q134(a) counted. Four lines still ask raw 4–6: `dv2/dv2lib.sh:177`, `hpl/run_hpl.py:622`,
   `knob/run_knob.py:658` (2 3 4 5 6) and `e77/run_e77.py:686` (2 3 4); E119 patches run_hpl's at run time and E120
   checks its states in code. Any command that fails leaves the same counter and event behind. The other side effects are
   benign: the temperature, voltage and clock GETs refresh the SP's own RAM copy of what they read, every command logs one
   INFO line once a run has raised the log level, and a failed PMIC read soft-resets the SP's own I2C master (not the
   PMIC).
6. **The firmware-revisions query was a PMIC write in every build the lab ran.** The two `set_pmic_reg` calls are in the
   public source at every BL2 version from 0.18.0 to 0.22.0 (version-bump commits `169a17566`, `29950410d`, `11b0b6966`,
   `cafe03fc3`, `ce7297156`; [`fwver_history.txt`](fwver_history.txt)), so September's sends on BL2 0.18.0, 0.20.0 and
   0.21.2 were PMIC commands too. The sends: [05-claims.md](../../../findings/05-claims.md), "Q134", lists every run
   (E69, E72, E79, E82, E84, E114, the version-3 check and the 25 September aifoundry1 fix); the cards answered normally
   each time. On aifoundry1 the query no longer even tells the two cards apart (both report release 1.4.0 / BL2 0.22.0
   since 31 Oct). Identity comes from module-uptime continuity (E77, E118, E120); a per-die identifier with no write
   exists, `GET_MODULE_SERIAL_NUMBER` (the ECID, a memory-mapped eFuse read, `driver/bl2_otp.c:252-263`), never sent on a
   lab card — compare it inside a run and never commit its value.
7. **E89's sampler is NO-GO until classified.** `tools/claims-v3/e89/pvt_sample.py` sends command 74
   (`GET_ASIC_PVT_SAMPLES`) through raw ioctls; it is not in the public source, so it cannot be classified here. Its own
   header calls group 0 a read and group 6 (the latch reset) a write, and it refuses any group but 0 and 4.

## The preflight checker

`tools/claims-v3/dmcmd_audit.py` (stdlib only; tests in [`test_dmcmd_audit.py`](../../../../tools/claims-v3/test_dmcmd_audit.py),
38 of 38 pass). A runner calls it on its own files before the first launch:

```bash
python3 tools/claims-v3/dmcmd_audit.py --allow SET_STATS_RUN_CONTROL tools/claims-v3/eNNN/ tools/claims-v3/lib.sh
python3 tools/claims-v3/dmcmd_audit.py --markdown --allow SET_STATS_RUN_CONTROL tools/claims-v3/eNNN/   # README section
```

- **What it finds**: `DM_CMD_` names; `dev_mngt_service`'s `-o` codes and `-t` trace operations (only after the tool's own
  word, up to a pipe); `ettelem` subcommands, each mapped through its variant's reviewed table (the variant from the
  binary's path, or the variable that holds it, else all five); the statistics reset (`--reset-ms`, `--reset-once-file`,
  or forwarded arguments that may carry one); residency states (the integers right after `residency`); raw ioctl
  clients' numeric codes; `et-reset`, sysfs and `setpci` writes, module loads and reboots. Comments and Python docstrings
  are skipped; Markdown and JSON are not scanned. A file whose SHA-256 matches a reviewed source in the table (the five
  `ettelem` variants, the two raw clients) is taken from the table, so dead code there (e118's unreachable
  `SET_DM_TRACE_CONFIG`, `:373`) does not count.
- **Exit 3 (NO-GO)** on a WRITE not in `--allow`, an UNSUPPORTED or UNCLASSIFIED command or one named at run time
  (`DYNAMIC`), a residency read of raw 4–6 (`SP_ERROR_LOG`) or with states it cannot see (`RESIDENCY_STATES_UNRESOLVED`),
  and, with `--deny-pmic-read`, a PMIC register read. Exit 0 is GO, 2 a usage error.
- **Reviewed exceptions**: `--except FILE:LINE:NAME=REASON` waives one finding on one line, for code the run never
  executes as written, and prints the reason with the verdict and in the README section. E126's chain, the first Q136
  runner, is GO with one: `hpl/run_hpl.py:622`'s raw 2–6, which E119's `run_e119.py:41-53` replaces with raw 1 2 3 at run
  time, and which the `ettelem-dv2` build then refuses before it opens the node.
- **Its limits**: it reads text, so a command assembled across functions or files is listed as a `WRAPPER` line for a
  person to read (the literal names at the call sites are what it classifies), and prose inside a Python string value
  counts. It over-reports rather than under-reports; a false NO-GO is cleared by reading the line, or by a reviewed
  exception with its reason, never by widening `--allow`.

## Dated notes (part 2 of the ask)

Each note says what the query writes, how many times its run sent it, and what to use instead. **No existing line was
edited or moved**: each note is appended after a file's last line, so every `file:line` citation elsewhere still holds.
Five files keep their bytes because a run record pins their hash (`code.sha256`, a start log); their notes sit beside them.

| File (lines the note covers) | Where the note is |
|---|---|
| `tools/claims-v3/kspeed/e84/run_e84.sh` (62–67) | appended (shell comment) |
| `tools/claims-v3/lq6/gov_e72.py` (156; and its TDP sets at 175, 203) | appended (Python comment) |
| `tools/claims-v3/nv/block.sh` (536; and its voltage set at 198) | appended (shell comment) |
| `tools/claims-v3/tel/block.sh` (332; its loglevel and SPST writes) and `tools/claims-v3/tel/README.md` (47) | **beside them**, [`block.sh.dated-note.md`](../../../../tools/claims-v3/tel/block.sh.dated-note.md): both are pinned by the nine TEL passes' `code.sha256` |
| `tools/claims-v3/hlp/run_e79.sh` (49) | **beside it**, [`run_e79.sh.dated-note.md`](../../../../tools/claims-v3/hlp/run_e79.sh.dated-note.md) (pinned by E79's `code.sha256`), and in the hlp README |
| `tools/claims-v3/e114/run_e114.sh` (50–54) | **beside it**, [`run_e114.sh.dated-note.md`](../../../../tools/claims-v3/e114/run_e114.sh.dated-note.md) (pinned by E114's `logs/e114-start.json`) |
| `tools/claims-v3/hlp/README.md` (131–132), `tools/claims-v3/nv/README.md` (101) | appended |
| `docs/reports/data/2026-09-30-without-heatsink/LOWCLOCK-PLAN.md` (484, 624; a plan that never ran) | appended |
| `docs/reports/data/2026-09-25-claims-v3/PLAN3.md` (849) | in that directory's [README](../2026-09-25-claims-v3/README.md) (PLAN3.md is pinned by the passes' `code.sha256` and that README's hash list), which now also notes the TEL arm's nine sends |
| `docs/getting-started.md` (595) | after its table |
| E69's change record `tools/claims-v3/knob/CHANGE-RECORD.md` (130–133, 140–141, 357) and E72's `tools/claims-v3/lq6/CHANGE-RECORD.md` (152–155, 179–180, 371) | appended: "no PMIC command sent" did not hold; "unchanged" stands |
| beyond the critic's list: `docs/reports/data/2026-09-25-aifoundry1/README.md` (the 25 September fix's two sends) | appended |

Not edited: the two published 25 September pages that give the query as a check
(`docs/reports/2026-09-25-aifoundry1-fix.html:168`, `2026-09-25-aifoundry1-troubleshooting.html:280-281`), because each must
equal its spacesheep mirror; the aifoundry1 README's note names them.

## AGENT.md (part 4)

Section 5 gains "Device commands: the owner's three rules of 2 November 2026" (no power cycles and nothing that risks one;
read-only PMIC voltage-register reads allowed; every command classified before the first launch, a disallowed or
unclassified write NO-GO), with one changelog entry; the oldest of then 16 entries moved verbatim to
[`docs/agent-changelog-archive.md`](../../../agent-changelog-archive.md).

## What it does not settle

- **The running binaries are unhashed.** The classification holds at the version-matched public source (gov-prep's rule-8
  standard); a card running another build needs its own audit (the table's `source.caveat`).
- **Command 74** waits for the patch's source.
- **The PMIC's own firmware** answers the firmware-management subcommands and is not in the public source: "the two writes
  select two queries and nothing else" is the service processor's side only.
- **The statistics reset's two extra writes** (the PVT latches and the SP stats trace off) are inside what the owner
  allowed on 31 October, which named the reset, not its parts; whether that covers them is his to say if it matters.

## Files

`README.md` (this), `tables.md` (generated by `make_tables.py` from the table and the inventory), `inventory.json` (the
checker's output over `scanned-files.txt`), `fwver_history.txt` (the revisions query's PMIC writes at each BL2 version
bump, from `fwver_history.sh`). The tool, its table and its tests are in `tools/claims-v3/`.

## Device commands sent

None: this is desk work. No card, lock or host was touched.
