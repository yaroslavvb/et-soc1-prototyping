# ET-SOC1 change record — E69, the governor knob test (aifoundry2 card 0)

Filled from `templates/change-record.md` of Roman's ET-SoC-1 firmware rebuild / OTA field manual
(`reference/etsoc1-firmware-field-manual/`, evidence through 12 Oct 2026, compiled 21 Oct UTC). Every gate
carries **PASS / FAIL / UNKNOWN / N-A** with a timestamp and its evidence. **UNKNOWN is not PASS.** Where a
gate is marked N-A the reason is written out; "not applicable" is never used to hide a missing check.

**What this operation is, in the field manual's own classification** (runbook § 1): *authorized live
observation* plus two *state-changing management writes that are not persistent*. The two writes are
`DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26) and `DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS` (22). It is **not**
an OTA, a build, a flash, a PMIC operation, a reset or a driver/PCIe action, and nothing in this record
authorises any of those. The whole of gates G1–G3 (recovery before risk, candidate provenance, preserving the
next update) exists for persistent writes; the parts that still bind here are restated under
"Restore before risk", which is this operation's analogue of G1.

---

## Identity / authorization

- **Record ID / UTC and local:** `E69-knob-2026-10-27`. Opened 2026-10-27 **20:54 UTC / 13:54 PDT**
  (Tue, ISO week 44). Timezone of all local stamps: America/Los_Angeles, PDT (UTC−7).
- **Operator:** an AI Foundry agent (`a2-e69-knob`) in the Q129 workflow, on the Intel (`Intel-mbp`), working
  over ssh. **Hardware owner / authoriser:** the lab's owner (Yaroslav Bulatov). **Independent reviewer:**
  none for the run itself — stated as a limitation, not a pass; the pre-registration
  ([`README.md`](README.md)) is the reviewable artefact and was committed and pushed before the first card
  access. **Recovery operator:** none on site; see "Restore before risk".
- **Explicit authorization reference and scope:** the owner, Tue 27 Oct 2026 ~13:40 PDT: *"Feel free to move
  the governor, by following the instructions of Roman in Discord"*, with Roman's field manual attached, and
  Roman's own words: *"it is extremely important to make sure your agents don't deviate from many gates
  described there -- otherwise bad things will happen."* Scope as relayed in the workflow brief: aifoundry2
  card 0; the static TDP level and the software temperature threshold; **no** OTA, flashing, PMIC commands,
  card resets, PCIe recovery, driver reloads or clock commands. The field manual's rule 0.1 ("no deployment
  implicit in research permission") is honoured by doing none of those.
- **Approved window / stop time / affected users:** the afternoon of 27 Oct 2026, bounded by the runner's
  110 card-minute cap. One card, one host; no other card is touched. Affected service on the host: the
  owner's own lab dashboard reader (below) pauses itself while the card lock is held.
- **Allowed:** offline build [x — the prediction tool, read-only] · live observation [x] · **volatile
  management writes to the two governor fields [x]** · OTA [ ] · SoC reset [ ] · PMIC reset [ ] ·
  driver/PCI changes [ ] · AC cycle [ ] · external SPI [ ] · PMIC write [ ]
- **OTP / fuses / keys / security-policy change: prohibited, and none is reachable from the two commands
  used** (see rule 8 below). **PASS**
- **Host/machine identity:** `aifoundry2`, Ubuntu 24.04 family, kernel **7.0.0-38-generic**
  (`#38~24.04.4-Ubuntu SMP PREEMPT_DYNAMIC Mon Sep 14 16:37:11 UTC`), 11th Gen Intel Core i5-11600, 12
  threads, 63 GiB. Read 13:55 PDT with `et-lab-manifest`. Host up 22 h 41 m at 13:54 (boot
  `42dcb8e5-a96f-45a5-8edc-78c987be4073`). **PASS**
- **Card asset / serial / revision / form factor / DRAM:** read fresh at **13:56:26 PDT** through
  `dev_mngt_service -n 0`: manufacturer `Esperanto`; part number `0x11345663`; module revision `0x2211ab44`;
  serial = a lot id, wafer `0x08`, X `0x0a`, Y `0x05` (the lot id is in the session's own queries and is not
  reproduced here); form factor `PCIE (0x1)`;
  DDR **32 GB**; ASIC revision **597**; module uptime **0 d 22 h 43 m** (so the SP has not reset since the
  host booted, and the governor's RAM fields are the boot defaults). **PASS**
- **PCI domain:BDF ↔ device number ↔ node:** `0000:02:00.0` ↔ device 0 ↔ `/dev/et0_mgmt` (mode 0666) and
  `/dev/et0_ops`; link **16.0 GT/s PCIe x8**; `Kernel driver in use: ET`. One card on this host; no second
  card shares the driver or root port here (contrast aifoundry1, where unload affects both). **PASS**
- **Firmware identities, read fresh 13:56:26 PDT** (`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`):
  release **1.4.0**; BL1 **0.22.0**; BL2 **0.22.0**; PMIC **1.5.0**; Master / Worker / Machine Minion
  **0.25.1**. **PASS** — and a correction worth recording: `docs/findings/14-card-behaviour.md` still lists
  this card as release 1.3.1 / BL2 0.20.0 / minion 0.23.0, which was true before the 10 Oct thermal-v2
  update. The findings file's card table is **stale for aifoundry2** and is corrected by this reading.
- **Host module / kernel / tools, separately identified:** driver `et-soc1` version string `0.20.0`,
  srcversion `47D26A305A0428B29FB7FC4`, file `/lib/modules/7.0.0-38-generic/updates/dkms/et-soc1.ko`
  sha256 `3ae3759cf857874e65396b8638f914fac4592c9c91797f9d7906145ea3292546`, DKMS registered for both
  7.0.0-34 and 7.0.0-38. `CONFIG_PCI_P2PDMA=y`. `/opt/et/bin/dev_mngt_service` sha256 begins
  `a3d4c722d9505aa9`; `/opt/et/lib/libetrt.so` `f5d1bfb14038b103`; `/opt/et/lib/libdeviceLayer.a`
  `786fc7650bf74375`. Experiment tools: `ettelem` (hpl build)
  `77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5`; heater `sparsity_host`
  `7adadf4f1ce331cc028c317561933d6d3209da0f0326b0ce9a124b39b15ac0d2`; kernel `sparsity.elf`
  `990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24`. The driver's **version string is not
  the firmware's**: 0.20.0 names the host module, the card runs BL2 0.22.0. **PASS**
- **Other affected cards / root-port devices / outlet loads:** none. No work on aifoundry1 or aifoundry3 is
  part of this experiment. **PASS**
- **Existing guest / session / volatile contents:** no Maxion guest, no packet endpoint, no resident
  Linux/9front on this card (no `/dev/et0_*` holder at 13:54, `et-who`: *"No process holds an ET-SoC-1 device
  node or card lock"*). **PASS**
- **Locks / guards / monitors / CI / services, and how races are excluded:** **PASS**, with the mechanism
  written out because the field manual (hosts § 8) warns that *telemetry and DM do not coexist on a
  single-open management node*:
  - `et-usaged` (root) watches who holds the cards; read-only, no device node. It reported `"holds": []`.
  - The owner's own **lab dashboard collector** (`live-collector.py` in his home on the host) reads each card's temperature with
    `ettelem temp --if-free` about once a second. Its own header states, and its code shows
    (`lock_inodes()`, the `/run/lock/etsoc-shire0.lock` probe, exit 3 = "lock taken, opened nothing"), that
    it **probes the card lock immediately before opening the management node and opens nothing if anyone
    holds it**. So holding `flock -n /run/lock/etsoc-shire0.lock` for the whole session keeps it off the
    node, which is exactly what `run_knob.py` does. **Nothing is killed**: the coordination is the lock the
    collector already honours. Its sibling `keeper.py tick` deploys the dashboard page and never opens a card.
  - A GitHub Actions runner is active on the host but ran nothing on the card in this window.
  - **Dated health flag, recorded not dismissed:** at host uptime 81,805 s (**≈13:58 PDT today**) the kernel
    log shows six `ET 0000:02:00.0: Error Event Detected / Level Critical / SP Runtime Error / Runtime Error
    Count Beyond Threshold: 1…6` — the SP's accumulated runtime-error events draining into the host log in
    one burst, the first six since the 26 Oct 15:13 boot — and at 81,924 s the owner's own `lab-monitor`
    segfaulted inside `libDM.so`. `lab-monitor` is **not running now** and has no systemd unit, so it was a
    one-off reader. Precedent: `docs/findings/14-card-behaviour.md` records the same syndrome and notes that
    the first five occurrences (20, 22, 25 Sep) *"did not stop the card, so the event need not be the hang's"*.
    Management reads answered normally before and after (13:56 identity, 13:56 config, a 2 s sampler).
    **Consequence for this record:** the `SMOKE` block runs first and must pass before the registered
    session; any **new** `Error Event Detected` line during the session is treated as an abort; the kernel log
    is read before the first set and after the last run and both are kept with the data. The error-event
    queue itself is **not** drained by this experiment (`DM_CMD_GET_DEVICE_ERROR_EVENTS` is never sent),
    because popping it is a state change and `dmesg` already carries what the driver printed.

## Current state (each item dated, not copied from an old README)

- **Kernel / config / P2PDMA; loaded module / srcversion / params:** above; module parameters directory holds
  no settable parameter. Read 13:55–13:56 PDT. **PASS**
- **Management application identity / digest:** `/opt/et/bin/dev_mngt_service`, digest above; `ettelem` is the
  repo's own tool at the hash above, built 23 Oct for E64. **PASS**
- **SoC firmware BL1 / BL2 / Minion identities and evidence:** above, 13:56:26 PDT. **PASS**
- **Current physical active / passive bank and how identified:** **UNKNOWN**, and deliberately left so: bank
  identification needs flash reads, which are a different authorization and a disturbance of programming
  state (field manual, hosts § 2). **This gate is not needed here and the UNKNOWN is not bypassed**: the
  operation performs no flash access at all (rule 8 below), so neither bank can change.
- **Priority / boot-counter state and supported accounting:** **N-A** — not read, and not read for the same
  reason. The field manual warns that boot-status probing itself generated an error event on old fleet
  firmware; with no persistent write in this operation there is nothing for boot accounting to protect.
- **Actual config version / offset / persistent assets / Vmin / nonpersistent policy:** not read from flash.
  What *is* read, and is the thing this experiment changes, is the firmware's **RAM** copy of the two
  governor fields (next item). The on-flash asset-config region is untouched; see rule 8.
- **PMIC runtime slot / configured next-boot slot / version / hash / board encoding:** PMIC firmware
  **1.5.0** from the revisions read; slots and board encoding **not read** (PMIC console/probe is not
  established for this fleet — field manual, hosts § 4 — and no PMIC command is sent). **N-A for this
  operation**: no PMIC write path is reachable from either command (rule 8).
- **PCIe / link / BAR / DM / ops / thermal / clock / TDP baseline, read 13:56:26 PDT:**
  link 16.0 GT/s x8; management and ops nodes present and answering; `ettelem config` →
  **`{"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power",
  "minion_mhz": 600, "minion_mv": 519}`**; driver's static view (`etcfg`-equivalent fields from
  `dev_mngt_service`) TDP 65 W, minion boot frequency 600 MHz, CM shire mask `0xffffffff`.
  **These are the originals to restore: TDP 65 W, software threshold 65 °C.** **PASS**
- **Live query allowlist; unsafe queries intentionally omitted:** allowed — `GET_MODULE_*` identity,
  `GET_MODULE_FIRMWARE_REVISIONS`, `GET_ASIC_CHIP_REVISION`, `GET_MODULE_UPTIME`, `GET_MODULE_POWER`,
  `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES`, `GET_SP_STATS`, `GET_MODULE_STATIC_TDP_LEVEL`,
  `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_MODULE_RESIDENCY_THROTTLE_STATES`, and
  the SP trace-ring extraction `ettelem sptrace` (a BAR read of a management-accessible region; the SP writes
  no log line for it). Omitted on purpose — `SET_STATS_RUN_CONTROL` / `ettelem --reset-ms` (it silently
  disables the SP statistics trace and resets PVT latches), any trace reset or trace run-control write,
  `GET_DEVICE_ERROR_EVENTS` (pops a queue), `GET_FIRMWARE_BOOT_STATUS`, `GET_FUSED_PUBLIC_KEYS`, every
  `MDI_*`, `SET_FREQUENCY`, `SET_MODULE_VOLTAGE`, `SET_MODULE_ACTIVE_POWER_MANAGEMENT`,
  `SET_THROTTLE_POWER_STATE_TEST`, `MM_RESET`, `RESET_ETSOC`, and all firmware-update commands. **PASS**

## Rule 8 — no incidental board-data change (the gate this operation turns on)

Field manual rule 8: *"Protect per-card configuration/Vmin, DRAM training, PCIe configuration,
VaultIP/certificates, and layout."* The brief's binding form: **before any set, read the firmware source of
the exact running build and show that the two SET paths do not write flash or configuration data.** The known
counter-example is real: on BL2 **0.18.0** `pwr_svc_set_module_voltage` called
`flash_fs_set_vmin_lut_boot_voltages()`, which erases and reprograms the 4 KB asset-config sector — so on that
build a *voltage* set silently became the card's boot voltage (`docs/findings/05-claims.md`, the NV row;
added `5f5c37abf`, removed `dd8927ce5`). A command that looks volatile is not automatically volatile.

**Source read.** The card reports BL1/BL2 **0.22.0**. The et-platform copy on the Intel
(the private door's et-platform clone, commit `836a4ab600e93c3059bb58c898edbc37744cd8d0`, 2026-07-17) declares
`project(EsperantoBootLoader VERSION 0.22.0)` in `device-bootloaders/CMakeLists.txt:4`, and its
`CHANGELOG.md` shows 0.22.0 as the unreleased version after 0.21.0 (2024-09-25). That is the revision
matching the card's reported version. The working tree is partly checked out, so the files were read straight
out of the git objects with `git show HEAD:<path>`.

**Finding — both set paths write one RAM word and nothing else. PASS.**

| Step | Source at BL2 0.22.0 | What it does |
|---|---|---|
| dispatch | `services/thermal_power_monitor.c:966-971` (`DM_CMD_SET_MODULE_STATIC_TDP_LEVEL`), `:976-980` (`…TEMPERATURE_THRESHOLDS`) | reads the field out of the command buffer, calls the handler below |
| handler (TDP) | `thermal_power_monitor.c:392-415` `pwr_svc_set_module_tdp_level` | calls `update_module_tdp_level`, fills the response header, pushes the response. No other call. |
| handler (threshold) | `thermal_power_monitor.c:494-521` `pwr_svc_set_module_temp_thresholds` | calls `update_module_temperature_threshold`, two `Log_Write`s, response. No other call. |
| setter (TDP) | `services/thermal_pwr_mgmt.c:576-591` | rejects `tdp > POWER_THRESHOLD_HW_CATASTROPHIC` (75), else one assignment: `g_pmic_power_reg.module_tdp_level = tdp` |
| setter (threshold) | `thermal_pwr_mgmt.c:638-643` | one assignment: `g_soc_power_reg.temperature_threshold.sw_temperature_c = sw_threshold`. No range check at all. |
| the two targets | `thermal_pwr_mgmt.c:143-144` | `volatile struct soc_power_reg_t g_soc_power_reg __attribute__((section(".data")));` and `volatile struct pmic_power_reg_t g_pmic_power_reg __attribute__((section(".data")));` — **plain service-processor `.data` RAM**, not a memory-mapped window, not flash. Lost at an SP reset. |

**And nothing on those paths can reach flash.** The only writers of flash in the whole BL2 0.22.0 tree live in
`driver/flashfs.c` (`flash_fs_write_partition`, `flash_fs_erase_partition`, `flash_fs_set_part_number`,
`flash_fs_set_vmin_lut`, `flash_fs_write_config_region`, `flash_fs_increment_*_boot_count`). Searching every
other file in `src/ServiceProcessorBL2` for calls to them finds exactly four call sites, none of them on
either set path: `common/main.c:488` and `rtos_task/flash_fs.c:121` (the boot counter),
`services/asset_track.c:87` (`flash_fs_set_vmin_lut`, reached only by the VMIN-LUT asset command),
`services/asset_track_mgmt.c:39` (the part number), and `services/firmware_update.c:752`
(`flash_fs_write_config_region`, the OTA's config copy). `thermal_pwr_mgmt.c` touches `flash_fs_*` data only
to **read** `…persistent_config.vmin_lut[0]`, the boot operating point, at lines 1630 and 2490. The 0.18.0
hazard is absent from this build: 0.22.0's `pwr_svc_set_module_voltage` (`thermal_power_monitor.c:294-316`)
calls only `Thermal_Pwr_Mgmt_Set_Validate_Voltage` — and that command is not used here anyway.
**No PMIC write either:** the two docstrings claim the values are "set in PMIC", but the code does not send
anything to the PMIC; the only `pmic_set_voltage` calls in the file are in the operating-point path
(`thermal_pwr_mgmt.c:3021, 3056`), which these commands never enter. *The stale docstring is itself the trap
rule 8 exists to catch: the comment claims a PMIC write the implementation does not perform.*

**Residual uncertainty, stated plainly.** The field manual warns (runbook § 7) that *"same semantic 0.22.0 is
not sufficient to distinguish BL2 builds"*, and the card exposes no build git hash through any command this
record allows. So the source read establishes the behaviour of **a** BL2 0.22.0, not provably of the exact
binary on the card. Two things reduce the residual: (1) the BL2 **0.20.0** review of the same two paths
reached the identical conclusion — RAM only, "all of these live in RAM and are lost at an SP reset"
(`docs/reports/data/2026-09-28-dvfs2-aifoundry2/plan/review-governor.md` § 1.3, § 8, citing
`C:tpm:537-552`, `:599-604`) — so the two builds that could plausibly be running agree; (2) the Esperanto
archive's own user documentation for these knobs describes them as runtime settings, and its own ticket
one of their tickets records a test that set the TDP level and never restored it, with the level persisting in
the running firmware until changed — a volatile, sticky RAM field, not a flashed one. **Rule 8: PASS, with
the build-identity residual named.**

## Restore before risk (this operation's G1)

- **What can go wrong, and what survives it:** the only state changed is two RAM words. An SP reset, a card
  reset or a power cycle restores both defaults by itself. So the "recovery artefact" is the pair of numbers
  recorded above (**65 W, 65 °C**) plus the command that writes them, and they are recorded in three places:
  this file, `gov.jsonl` `{"event": "original"}`, and `end.json` `governor_original`. **PASS**
- **Exact independent recovery path:** none beyond the above is needed for the two fields, and **none is
  available for anything worse**: no PMIC console, probe or programmer route is established for this fleet
  (field manual, hosts § 4), `/dev/mtd0` on these hosts is host BIOS and not card SPI, and the owner's rules
  forbid a card reset here. **This is the operation's binding limitation**, and it is why the experiment does
  only non-persistent writes, never raises the cap, and drops every cell that could trap a governor loop.
  Recorded as a **limitation, not a PASS.**
- **Full SPI backup / PMIC backup / protected-region baseline:** **N-A** — no flash or PMIC byte is written or
  read (rule 8 above). No backup is taken and none is claimed.
- **Power-loss / partial-write plan:** a power loss during either set loses only the RAM word, and the SP's
  boot defaults return. No retry chain, no reset, no slot work exists in this operation.
- **How the restore is executed and proved:** `run_knob.py` sends both originals in the session's `finally`
  — on success, on an abort and on an unexpected exception — then reads `ettelem config` back and writes
  `{"event": "restore", "ok", "original", "after"}`. A read-back that is not equal turns the session's exit
  into an error. The `BACK` block then runs one 6 s `randn` burst at the restored settings and its governor
  log must show normal stepping and the default TDP.
- **If the restore fails or the card stops answering:** stop; **keep the card claim**; write it up; alert the
  owner with `notify.py --unblock`. **Do not reset the card**, even though a reset would restore the
  defaults, and do not retry blindly (field manual rule 11).
- **Automatic fallback status:** **N-A** (nothing persistent is written, so there is nothing to fall back to).

## Candidate and build provenance

**N-A in full: there is no candidate artefact.** No image is built, composed, staged, hashed for release or
written. The only software this operation introduces is host-side and in the public repo: `run_knob.py`,
`predict_knob.py`, `protocol.json`, `predictions.json`, this record and `README.md`, all committed and pushed
**before the first card access**. The frozen predictions' sha256 is
`2894d77827640a3d280215984f7fab0974c461f22884cb58118344ee6b8c358e` (`predictions.json`). The two
commands sent are the stock `dev_mngt_service`'s own, at the digest recorded above.

## Immediate release gate (G4)

- **Identity / ownership rechecked at:** immediately before the first set, inside the card lock, by
  `run_knob.py` (`check_others`, `modcount`, and `read_config` writing `gov.jsonl` `{"event": "original"}`).
  Timestamps in `gov.jsonl`.
- **No guest / SDK / Minion / DMA / monitor conflict:** `et-who` empty; `et-usaged` `"holds": []`; the
  dashboard collector held off by the card lock it already honours; no second card on the host.
- **Unique receipt directory:** `docs/reports/data/2026-10-27-e69-governor-knob/` with one subdirectory per
  session; no reused trace filename, no wildcard deletion, no mutable `current-*` pointer.
- **Capture ready before the first set:** the 10 Hz sampler starts before each run's gate; the SP trace ring
  is dumped after **every** run (it holds only about 67 entries, so a dump per run is the only way to keep the
  governor's own lines); no `--reset-ms` is ever sent.
- **Exact approved command and environment:** `dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0
  -l <W> -u 5000` and `… -m DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS -n 0 -e <C> -u 5000`, under
  `LD_LIBRARY_PATH=/opt/et/lib`, each wrapped in `timeout 20`, each followed by `ettelem config`.
  **No reset is planned or permitted.**
- **Bounds enforced in code, not only in prose:** `GOV_TDP_MIN_W/MAX_W = 30/65`, `GOV_THR_MIN_C/MAX_C =
  60/70` in `run_knob.py`, checked in `Run.check()` (so the planner refuses a bad protocol before the card is
  opened) and again in `set_governor()`. Abort at a die mean ≥ 72 °C or board power ≥ 85 W on 3 consecutive
  samples.
- **GO / NO-GO / UNKNOWN:** **GO**, on the gates above, with the two named residuals (build identity; no
  independent hardware recovery path) and the dated health flag of ≈13:58 PDT.
- **Operator releasing this operation:** the owner's authorization of 27 Oct 2026 for this exact pair of
  commands on this card, recorded verbatim above. No "it built, therefore run it" step exists here.

## Set log — every set and read-back, with timestamps

The machine-readable record is `gov.jsonl` in the session directory: one line per event, `original`, `set`
(with `asked`, `before`, `after`, and each command's argv, rc and ISO timestamp) and `restore`. The table
below is filled from it after the session.

| # | Local time (PDT) | Event | Asked | Read back | rc |
|---|---|---|---|---|---|
| — | — | *filled from `gov.jsonl` after the session* | — | — | — |

## Activation and acceptance

- **Separate reset approval / type:** **none sought and none performed.** The two fields take effect on the
  next governor pass (about 0.24 s) with no reset; that is the whole point of using them.
- **Host reinit / PCI mapping / card re-identified:** no reset, so no re-enumeration; the card's identity is
  re-read in the session's end queries.
- **New running firmware identity:** unchanged by construction; re-read after the last run.
- **PMIC runtime and next-boot state:** unchanged; no PMIC command sent.
- **Configuration / clock / TDP policy checks:** `ettelem config` after **every** run (the runner aborts the
  session if it drifts from that run's own target), plus the restore read-back and the `BACK` burst.
- **Fresh management / thermal / error results:** the end queries; the kernel log read before the first set
  and after the last run, both kept with the data.
- **Hardware-mode evidence:** every launch is a real PCIe device process (`sparsity_host` with the card's own
  kernel ELF); there is no SYSEMU path in this harness.

## Outbound OTA / fallback qualification

**N-A: no OTA is performed, so nothing about the card's update path is exercised, changed or claimed.** The
card's outbound OTA status is exactly what it was before this session, which this record does not establish
either way.

## Final handoff

- **Retained firmware / module / PMIC / bank state:** unchanged (release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0,
  minions 0.25.1; driver `et-soc1` srcversion `47D26A305A0428B29FB7FC4`).
- **Governor fields at handoff:** *filled after the session from `end.json` `governor_restore`; the target is
  TDP 65 W and threshold 65 °C, equal to the originals.*
- **Guest / excluded memory / packet / core state:** none existed and none was created.
- **Card lock and claim:** the lock is released only after the restore has been read back; the Discord claim
  in `#community-lab` is released after the data README is pushed.
- **Services restored:** the dashboard collector resumes by itself the moment the card lock is released; it
  was never stopped, signalled or killed.
- **Logs / artefacts:** the session directory under `docs/reports/data/2026-10-27-e69-governor-knob/`, all
  committed to the public repo.
- **Unresolved risks / prohibited next actions:** the build-identity residual on rule 8 (the card exposes no
  BL2 git hash through an allowed query) and the absence of any independent hardware recovery path for this
  fleet. Prohibited next actions without fresh authorization: raising the TDP level above the card's default,
  setting it to 0 or near a pattern's 600 MHz draw, lowering the threshold below a pattern's 600 MHz die,
  touching active power management, and every reset, PMIC, flash and OTA operation.
- **Signoff:** *filled at the end of the session with the UTC/local timestamp and the restore read-back.*
