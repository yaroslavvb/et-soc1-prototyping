# Q136(w): every device command the lab can send, classified READ or WRITE from the firmware source

*Mon 2 Nov 2026 (week 45), desk only: no card, host or lock was touched, nothing was posted. It answers the owner's
words of that morning, *"continue the experiments but don't do any power cycles, read only PMIC voltage reads should be
fine, take more care for writing commands"*, and item 13 of Q134's final critic ("Owed before the post leans on Q134":
the instructions to send the firmware-revisions query that were still unannotated, and E69's and E72's change records'
"no PMIC command sent"). Corrected after verification the same day: the checker, its table, the inventory and this
README changed, and no frozen record did ([Corrections after verification](#corrections-after-verification)).*

## Results

1. **Every command, classified from source.** [`tools/claims-v3/dmcmd_table.json`](../../../../tools/claims-v3/dmcmd_table.json)
   classifies all 92 device-management commands of et-platform `836a4ab` (the public source of BL2 0.22.0, the version
   all four lab cards report since 27–31 October), each with its handler's file and lines: **46 READ, 40 WRITE, 5
   UNSUPPORTED** (no handler: the service processor logs an error and may never reply) **and 1 UNCLASSIFIED** (command
   74, which exists only in the maintainer's raw-temperature patch). Every command the lab sends but command 74 is traced
   to the register level; the rest are classified at their handler (`depth` in the table says which).
   **The basis is the nearest public source, and on aifoundry3 it is known to differ.** No card exposes a BL2 hash, so
   each runs *a* 0.22.0. aifoundry3's is a non-public build: the thermal firmware build first flashed there on 7 October,
   which answers command 74 (absent from `836a4ab`) and whose answer changed from whole degrees (7 Oct) to raw sensor
   codes (31 Oct) while the card reported release 1.4.0 / BL2 0.22.0
   ([14-card-behaviour.md](../../../findings/14-card-behaviour.md), "A finer reading exists on aifoundry3's firmware
   build"; [E89's README](../2026-10-31-e89-heat-low-power/README.md), "Joins and traps"). For aifoundry3 a command
   present in both is classified from `836a4ab`'s handler, which that build may not share: a residual every aifoundry3
   lane carries (Q136: E127, E130, E132, E134), as the table's `source.caveat` says.
2. **What the lab's code can send.** [`dmcmd_audit.py`](../../../../tools/claims-v3/dmcmd_audit.py) over every tracked code
   file under `tools/`, `scripts/` and `workloads/` (1,599 files, [`scanned-files.txt`](scanned-files.txt)) finds 132 files
   with a send site and 950 records, 874 of them at a line and the rest reviewed sources taken from the table
   ([`inventory.json`](inventory.json); per command in [`tables.md`](tables.md)): **22 DM commands** — 14 READ, 7 WRITE, 1
   UNCLASSIFIED — plus two driver reads with no DM command (the trace extract and `etcfg`) and two host writes (in the
   boot-time recovery service). No host program sends a DM command: no workload's C++ includes the management library,
   and the vendor runtime they link (et-platform's `esperanto-tools-libs`) has no `serviceRequest`. **The code kept with
   the records under `docs/`** (445 files at the audit's commit: a run's generated scripts as they ran, page tools, desk
   scripts; [`docs-scanned-files.txt`](docs-scanned-files.txt), [`inventory-docs.json`](inventory-docs.json),
   [`tables.md`](tables.md) § F) **sends no command outside those 22**: three generated `watchdog.sh` copies (E77, E118,
   E120) restore the TDP with `SET_MODULE_STATIC_TDP_LEVEL` and read `ettelem config`, two page tools (`measure.sh`,
   `etpower.py`) sample, and the other eight files only name commands in strings. They are records, not runners.
3. **The writes, and what they reach** (sites: [`tables.md`](tables.md) § A2 and § C):

   | Command | Reaches | Sent by | Under the owner's rules of 2 Nov |
   |---|---|---|---|
   | `GET_MODULE_FIRMWARE_REVISIONS` | **the PMIC**: writes its firmware-management command register twice (ACTIVE_SLOT, then VERSION), reading an answer after each (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`, writes at `:2543`, `:2587`, reads at `:2549`, `:2591`) | 6 scripts: `tel/block.sh:332`, `hlp/run_e79.sh:49`, `kspeed/e84/run_e84.sh:64`, `lq6/gov_e72.py:156`, `e114/run_e114.sh:52`, `nv/block.sh:536` (and NV's selftest stand-in `nv/stubs/stub-dms`, which opens no card) | **NO-GO** (a PMIC command, though named GET) |
   | `SET_STATS_RUN_CONTROL`, type 1, control 2: **the statistics reset** (`ettelem sample --reset-ms`; the checker's `STATS_RESET`) | **the PMIC**, two writes: its stats reset (`set_pmic_reg(PMB_RW 0x15, 0x47)`, `driver/pmic_controller.c:1801-1805`), then the snapshot command before the stats are read back (`0x15 := 0x43`, `:1827-1832`, which the SP's own task also sends every pass, `rtos_task/dm_task.c:215`); the PVT controllers' high/low latches (`pvt_hilo_reset`, `services/thermal_pwr_mgmt.c:2828`); the SP's RAM statistics; and — because control 2 lacks TRACE_ENABLE — the SP stats trace, switched off (`services/performance.c:556-564`) | 29 sites: every `--reset-ms` sampler and its wrappers (`lib.sh:154`, `dv2lib.sh`, `hplib.sh`, `ohlib.sh`, …) | **allowed** (the owner's ruling of 31 October 2026) |
   | `SET_STATS_RUN_CONTROL`, type 1, control 1 (`dev_mngt_service -t SPST:enable`; the checker's `SPST_TRACE_CONTROL`) | the SP's device-statistics trace, switched on (`services/performance.c:556-564`); no counter reset, no PMIC access | `tel/block.sh:185, 194` (the TEL arm of the version-3 check, 25–26 Sep: `spst_enable`, and `restore` after a reset segment) | **NO-GO** in Q136: a write that is not the ruled reset. So are `-t SPST:reset` (control 7: the counters, the trace buffer and the PMIC's stats reset) and `-t MMST:…` (type 2, the Master Minion's statistics), which the lab never sends |
   | `SET_MODULE_STATIC_TDP_LEVEL`, `SET_MODULE_TEMPERATURE_THRESHOLDS` | the governor's two RAM fields (`services/thermal_pwr_mgmt.c:576-591`, `:638-643`); no flash or PMIC write at this build | the governor-move runners of E69 (`knob/run_knob.py`), E72 (`lq6/gov_e72.py`), E77, E118, E120, and the deadline watchdogs they write out | only with the owner's authorization for that run; none in Q136 |
   | `SET_DM_TRACE_CONFIG` (`ettelem loglevel`) | the SP trace's event mask and log level (`services/trace.c:183-207`), kept until the next boot or set; the boot default is WARNING, which the stock `ettelem` cannot restore (it maps every word but `debug` to INFO) | `tel/block.sh` ×4, `dv2/dv2lib.sh:172`, `hp/hplib.sh:172`, `hp/a2/hplib.sh:167` | **NO-GO** in Q136 (a write) |
   | `SET_MODULE_VOLTAGE` | **the PMIC**: a regulator set (`services/thermal_pwr_mgmt.c:3008-3048` → `pmic_set_voltage`) | `nv/block.sh:198` (and its stand-in); NV never ran on a card | **NO-GO** |
   | `RESET_ETSOC` | **a reset through the PMIC**: `pmic_force_power_off_on()` (a power cycle) after a PMIC update, else the PMIC watchdog armed and `pmic_force_reset()` (`services/firmware_update.c:45-105`) | the lab's `tools/lab/et-reset` (the lab admin's tool, run by hand) | **never** (no power cycles, no resets) |
   | host: `systemctl reboot` and `/sys/kernel/reboot/*` | the host | `tools/lab/host-recovery/et-boot-check:148-149`, the boot-time service installed on all three hosts on 26 Oct, which reboots a host cold by itself when a card's link trained badly after a boot | never in a run; it acts only after a boot |

   **No write in the lab's code reaches flash or persistent configuration.** Every flash or NVM writer of the firmware
   (`SET_FIRMWARE_UPDATE`, `SET_VMIN_LUT`, `SET_MODULE_PART_NUMBER`, `SET_SHIRE_CACHE_CONFIG`, `SET_FRU`, the
   certificate and counter sets) has no site. **A second GET writes the PMIC**: `GET_FRU` writes three FRU command and
   offset registers once, then reads the FRU bytes (`driver/pmic_controller.c:2412-2445`); the lab never sends it.
   **Two automatic reboot paths stand on all three hosts** (installed 26 October, at the owner's request after the lab's
   power cut; [`tools/lab/host-recovery/README.md`](../../../../tools/lab/host-recovery/README.md)): et-boot-check
   cold-reboots a host once after a boot when a card's link trained badly, and `kernel.panic = 10`
   ([`lab-panic.conf`](../../../../tools/lab/host-recovery/lab-panic.conf), installed as
   `/etc/sysctl.d/60-lab-panic-reboot.conf`) reboots a host 10 s after any kernel panic, after which et-boot-check runs
   too. Neither is a command a run sends. A run cannot set off the first; it could set off the second, through a driver
   fault that panics the kernel. Both stand beside the owner's rule of no power cycles.
4. **The reads that reach the PMIC are reads**: `GET_ASIC_VOLTAGE` makes two PMIC voltage-register reads
   (`services/thermal_pwr_mgmt.c:1213, 1215`) and `GET_MODULE_VOLTAGE` nine (`:1010-1140`), each an I2C register read with
   no write (`driver/pmic_controller.c:254-300, 1473-1500`). The stock `ettelem config` sends the first and every stock
   `ettelem sample` both: allowed by the owner's rule of 2 November.
5. **Reads with a side effect.** A residency read of a raw throttle state BL2 0.22.0 does not have (raw 4–6: its states
   are 0 IDLE, 1 UP, 2 DOWN, 3 SAFE) takes the error branch twice (`services/thermal_pwr_mgmt.c:1499`,
   `services/thermal_power_monitor.c:607`), and every ERROR log line increments the SP's runtime-error counter and sends one
   `SP_RUNTIME_ERROR` event to the host (`services/log.c:240-249, 414-436`; `RT_ERROR_THRESHOLD` 0): two events a state
   read, as E77's F1 and Q134(a) counted. Five lines still ask raw 4–6: `dv2/dv2lib.sh:177`, `dv2/z2.sh:73` (through its
   `run` wrapper, which the first pass missed), `hpl/run_hpl.py:622` and `knob/run_knob.py:658` (2 3 4 5 6), and
   `e77/run_e77.py:686` (2 3 4); E119 patches run_hpl's at run time and E120 checks its states in code. Any command that
   fails leaves the same counter and event behind. The other side effects are benign: the temperature, voltage and clock
   GETs refresh the SP's own RAM copy of what they read, every command logs one INFO line once a run has raised the log
   level, and a failed PMIC read soft-resets the SP's own I2C master (not the PMIC).
6. **The firmware-revisions query was a PMIC write in every build the lab ran.** The two `set_pmic_reg` calls are in the
   public source at every BL2 version from 0.18.0 to 0.22.0 (version-bump commits `169a17566`, `29950410d`, `11b0b6966`,
   `cafe03fc3`, `ce7297156`; [`fwver_history.txt`](fwver_history.txt)), so September's sends on BL2 0.18.0, 0.20.0 and
   0.21.2 were PMIC commands too. The sends: [05-claims.md](../../../findings/05-claims.md), "Q134", lists every run
   (E69, E72, E79, E82, E84, E114, the version-3 check and the 25 September aifoundry1 fix); the cards answered normally
   each time. The runs used it as an identity read; because it writes the PMIC, a card's identity now comes from
   module-uptime continuity (E77, E118, E120). A per-die identifier with no write exists, `GET_MODULE_SERIAL_NUMBER` (the
   ECID, a memory-mapped eFuse read, `driver/bl2_otp.c:252-263`), never sent on a lab card — compare it inside a run and
   never commit its value.
7. **E89's sampler is NO-GO until classified.** `tools/claims-v3/e89/pvt_sample.py` sends command 74
   (`GET_ASIC_PVT_SAMPLES`) through raw ioctls; it is not in the public source, so it cannot be classified here. Its own
   header calls group 0 a read and group 6 (the latch reset) a write, and it refuses any group but 0 and 4.

## The preflight checker

`tools/claims-v3/dmcmd_audit.py` (stdlib only; tests in [`test_dmcmd_audit.py`](../../../../tools/claims-v3/test_dmcmd_audit.py),
55 of 55 pass). A runner calls it on its own files before the first launch:

```bash
python3 tools/claims-v3/dmcmd_audit.py --allow STATS_RESET tools/claims-v3/eNNN/ tools/claims-v3/lib.sh
python3 tools/claims-v3/dmcmd_audit.py --markdown --allow STATS_RESET tools/claims-v3/eNNN/ tools/claims-v3/lib.sh   # README section
```

- **What it finds**: `DM_CMD_` names; `dev_mngt_service`'s `-o` codes and `-t` trace operations (only after the tool's own
  word, up to a pipe, with every operation of a `TYPE:op,op` argument); every `ettelem` call on a line, its binary resolved
  through the table's reviewed build directories (from the path on the line, the variable that holds it, a file the
  script sources, or the binaries its file names) and its subcommand looked up in that variant's reviewed table; the
  statistics reset (`--reset-ms`, `--reset-once-file`, or forwarded arguments that may carry one); residency states (the
  integers right after `residency`); wrappers that pass their own arguments to `ettelem` (a shell function, a Python
  def), whose calls in the same file are classified through them; raw ioctl clients' numeric codes; `et-reset`, sysfs
  and `setpci` writes, module loads and reboots. Comments and Python docstrings are skipped; Markdown and JSON are not
  scanned; messages (`echo`, `print`, a word inside a longer string) do not make a call. A file whose SHA-256 matches a
  reviewed source in the table (the five `ettelem` variants, the two raw clients) is taken from the table, so dead code
  there (e118's unreachable `SET_DM_TRACE_CONFIG`, `:373`) does not count, and a call through a program that is among the
  scanned files (E128's guard, say) is classified at that program's own lines.
- **`SET_STATS_RUN_CONTROL` is named by its form**, because its forms write different things ([`tables.md`](tables.md)
  § A2): `STATS_RESET` (type 1, control 2) is the reset the owner ruled on, and the only allowed write in Q136;
  `SPST_TRACE_CONTROL`, `SPST_RESET` and `MMST_CONTROL` are `dev_mngt_service -t SPST:/MMST:` operations; a send whose form
  the checker cannot see (the command's name in code, `-o 62`) keeps the command's name and is never allowed.
  `--allow SET_STATS_RUN_CONTROL` is read as `STATS_RESET`, and the checker says so.
- **Exit 3 (NO-GO)** on a WRITE not in `--allow`; an UNSUPPORTED or UNCLASSIFIED command or one named at run time
  (`DYNAMIC`); an `ettelem` build outside every reviewed build directory (`UNREVIEWED_VARIANT`), one the checker cannot
  resolve (`VARIANT_UNRESOLVED`: a binary set in a protocol, a host config or the environment), or a subcommand the
  matched build lacks (`UNKNOWN_SUBCOMMAND`); a residency read of raw 4–6 (`SP_ERROR_LOG`) or with states it cannot see
  (`RESIDENCY_STATES_UNRESOLVED`); and, with `--deny-pmic-read`, a PMIC register read. Exit 0 is GO, 2 a usage error.
  The three `ettelem` reasons are never cleared by `--allow`: `--variant-source KEY=SOURCE` names the source a binary was
  built from (KEY its build directory or program name, or `unresolved`), and is taken only when that file's SHA-256 equals
  a reviewed variant's.
- **Reviewed exceptions**: `--except FILE:LINE:NAME=REASON` waives one finding on one line, for code the run never
  executes as written, and prints the reason with the verdict and in the README section. E126's chain, the first Q136
  runner, is GO with one: `hpl/run_hpl.py:622`'s raw 2–6, which E119's `run_e119.py:41-53` replaces with raw 1 2 3 at run
  time, and which the `ettelem-dv2` build then refuses before it opens the node. Re-run with the corrected checker on the
  Q136 runners' files: E126 GO with that exception; E133 GO with its two; E127, E128 and E130 NO-GO only on the
  conditional reset at `lib.sh:154` (`start_sampler` forwards `"$@"`). Each block's one `start_sampler` call passes the
  output file and the duration and nothing else (`block_e127.sh:105`, `block_e128.sh:96`, `block_e130.sh:106`), which
  E127's and E130's READMEs record, and E128's guard `ettelem_guard.sh` refuses `--reset-ms` before the node opens.
- **Its limits**: it reads text. A command assembled across files, a wrapper defined in one file and called from another,
  and an unknown subcommand inside a command kept in a string are beyond it; a heredoc in another language is read as
  the shell around it; prose that names a reviewed subcommand next to `ettelem` is listed as what a reviewed build would
  send. It errs toward NO-GO on what it cannot see — an unresolved build, an unreviewed one, an unknown subcommand — and a
  forwarded subcommand is a `WRAPPER` line for a person to read (§ E). A false NO-GO is cleared by reading the line
  (`--except` with its reason, or `--variant-source`), never by widening `--allow`.

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
[`docs/agent-changelog-archive.md`](../../../agent-changelog-archive.md). The corrections after verification add a second
entry (rule 3: aifoundry3's build, `STATS_RESET`, the `ettelem` reasons) and move the next oldest the same way.

## What it does not settle

- **The running binaries are unhashed**, and no card exposes a BL2 hash. The classification holds at the version-matched
  public source (gov-prep's rule-8 standard); aifoundry3 runs a build known to differ from it (Result 1), and a card
  running another build needs its own audit (the table's `source.caveat`).
- **Command 74** waits for the patch's source.
- **The PMIC's own firmware** answers the firmware-management subcommands and is not in the public source: "the two writes
  select two queries and nothing else" is the service processor's side only.
- **The statistics reset's other parts** (the PVT latches, the 0x43 snapshot write and the SP stats trace off) are
  inside what the owner allowed on 31 October, which named the reset, not its parts; whether that covers them is his to
  say if it matters. The snapshot write is the one the SP's own task sends every pass.
- **The checker's reach** is text (its limits, above): it errs toward NO-GO on what it cannot see, and the inventory
  lists 20 sites in 5 files whose `ettelem` build is set at run time (§ E: E77's and E120's runners, two older runners
  and the lab dashboard's sampler, whose host config names the stock build).

## Corrections after verification

Mon 2 Nov 2026, after the lane's verifier (desk only; no card, host or lock touched). Each fault, and what changed:

1. **The allow token was too wide.** `--allow SET_STATS_RUN_CONTROL` passed every form of that command, so
   `dev_mngt_service -t SPST:enable` (control 1), `-t SPST:reset` (control 7) and `-t MMST:…` (type 2) were GO, and
   Result 3 counted `tel/block.sh:185, 194` among the "allowed" statistics-reset sites. Now the forms have their own names
   (`STATS_RESET` is the ruled one), Result 3 lists the two TEL lines as a NO-GO write, and the TEL sidecar note carries
   an appended correction (its checker line had used the old token). Tests: `TestForms`.
2. **The checker under-reported**, against this README's sentence that it "over-reports rather than under-reports"
   (withdrawn). It dropped an unknown `ettelem` subcommand without a word, and read a binary outside every reviewed build
   by the reviewed builds' meaning (`build/ettelem-e999/ettelem threshold set 70` became a GET). Now `UNKNOWN_SUBCOMMAND`,
   `UNREVIEWED_VARIANT` and `VARIANT_UNRESOLVED` are NO-GO, and `--variant-source` binds a build to a reviewed source by
   hash. Checking the inventory record by record turned up four more gaps, all fixed. Only the first `ettelem` call on a
   line was read. A `-t TYPE:op,op` argument lost the operations after its comma. A shell function that forwards its
   arguments hid its calls, so `dv2/z2.sh:73`'s residency raw 2–6 was missed. Calls inside a script a Python runner
   writes out were missed, so the deadline watchdogs of `lq6/gov_e72.py:203` and `e118/gov_e118.py:209` (an
   `ettelem config` read beside their TDP restore) were not counted. The table now maps `build/ettelem-hpl/` (E64's
   runners' sampler) to `ettelem-dv2`, its documented source. The inventory changed from 1,079 records in 133 files to
   950 in 132. It lost 174 records from 34 printed messages (32 `echo`, 2 `print`), which were never sends. It gained
   45: `z2.sh`'s 9, 20 `VARIANT_UNRESOLVED` sites, 2 forwarding wrappers, the two watchdogs' 9 reads and 5 reads in
   prose. The corrected checker was run on the verifier's 15 probe files and gives the expected verdict on each. Tests:
   `TestVariants`, `TestWrappers`; 55 in all.
3. **The basis was overstated.** Result 1, AGENT.md section 5 and the table called `836a4ab` "the build all four cards
   report". Now each says it is the public source of the version they report, and that aifoundry3's build is non-public
   and differs (command 74).
4. **The statistics reset's PMIC writes were listed as one.** It makes two (the 0x47 reset, then the 0x43 snapshot):
   the table's row and Result 3 now say so.
5. **GET_FRU** writes its three FRU command and offset registers once, not "before each byte it reads".
6. **Result 6** said the revisions query "no longer even tells the two [aifoundry1] cards apart"; its PMIC field still
   does (1.3.0 against 1.6.1). The clause is gone: identity comes from uptime because the query is a write.
7. **A second automatic reboot path**, `kernel.panic = 10`, sits beside et-boot-check on all three hosts (Result 3).
8. **The inventory's scope** is now stated, and the code kept under `docs/` was scanned too (Result 2, § F).
9. **Cosmetic**: the stray `# #` line in the three appended code notes is now `#` (comments only; nothing pins those
   files).

## Files

`README.md` (this), `tables.md` (generated by `make_tables.py` from the table and both inventories), `inventory.json` (the
checker's output over `scanned-files.txt`, `--files-from`), `inventory-docs.json` (the same over `docs-scanned-files.txt`,
the tracked code files under `docs/` at the audit's commit), `fwver_history.txt` (the revisions query's PMIC writes at
each BL2 version bump, from `fwver_history.sh`). The tool, its table and its tests are in `tools/claims-v3/`.

## Device commands sent

None: this is desk work. No card, lock or host was touched.
