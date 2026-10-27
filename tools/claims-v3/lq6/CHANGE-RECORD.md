# ET-SOC1 change record — E72, the 600 MHz pin (aifoundry2 card 0)

Filled from `templates/change-record.md` of Roman's ET-SoC-1 firmware rebuild / OTA field manual
(`reference/etsoc1-firmware-field-manual/`, evidence through 12 Oct 2026, compiled 21 Oct UTC). Every
gate carries **PASS / FAIL / UNKNOWN / N-A** with a timestamp and its evidence. **UNKNOWN is not PASS.**

**What this operation is, in the field manual's classification** (runbook § 1): *authorized live
observation* plus **one** *state-changing management write that is not persistent* —
`DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26), set to 0 W and back to 65 W. It is **not** an OTA, a build, a
flash, a PMIC operation, a reset, a driver/PCIe action, and **not a clock command**
(`DM_CMD_SET_FREQUENCY` is never sent). Nothing here authorises any of those. Gates G1–G3 of the manual
exist for persistent writes; the parts that bind here are restated under "Restore before risk".

**Relationship to E69's record** (`tools/claims-v3/knob/CHANGE-RECORD.md`, signed off 14:42 PDT today,
the same card, the same host, the same firmware, the same management binaries). Where E69's evidence is
a property of the *build* or the *host* it is cited and re-used, because it is hours old and nothing
between the two sessions could change it. Where it is a property of the *card's live state* —
ownership, the governor's values, module uptime, the error-event count — it is **read fresh** and E69's
reading is used only as the "before" to compare against. The two differences in substance: E72 writes
**one** field, not two, and the value it writes (**0**) is below E69's own coded bound of 30 W, so the
value's own safety is argued from the source here and not inherited.

---

## Identity / authorization

- **Record ID / UTC and local:** `E72-pin600-2026-10-27`. Opened 2026-10-27 **22:28 UTC / 15:28 PDT**
  (Tue, ISO week 44). All local stamps America/Los_Angeles, PDT (UTC−7).
- **Operator:** an AI Foundry agent (`a2-e72-600mhz`) in the Q129 workflow, on the Intel (`Intel-mbp`),
  over ssh. **Hardware owner / authoriser:** the lab's owner. **Independent reviewer:** none for the run
  itself — stated as a limitation, not a pass; the pre-registration ([`README.md`](README.md)) and the
  frozen [`predictions.json`](predictions.json) are the reviewable artefacts and are committed and
  pushed before the first card access. **Recovery operator:** none on site; see "Restore before risk".
- **Explicit authorization reference and scope:** the owner, Tue 27 Oct 2026 ~13:40 PDT: *"Feel free to
  move the governor, by following the instructions of Roman in Discord"*, with the field manual attached,
  and Roman's own words: *"it is extremely important to make sure your agents don't deviate from many
  gates described there -- otherwise bad things will happen."* Scope as relayed in the workflow brief:
  aifoundry2 card 0; the static TDP level and the software temperature threshold; **no** OTA, flashing,
  PMIC commands, card resets, PCIe recovery, driver reloads or clock commands — and, naming E72
  specifically, *"The 600 MHz replicate (E72) gets its clock only through the governor (TDP 0 latches it
  at the floor under load, exactly aifoundry3's boot policy), and is restored like any governor move."*
  E72 uses **one** of the two authorised fields and sends none of the prohibited commands.
- **Approved window / stop time / affected users:** the afternoon of 27 Oct 2026. The deadline watchdog
  writes the original TDP back after 75 min whatever happens to this session. One card, one host; no
  other card is touched. Affected service: the owner's own lab dashboard collector, which pauses itself
  while the card lock is held (mechanism below) and is never signalled or killed.
- **Allowed:** offline build [x — the prediction tool, read-only] · live observation [x] · **one
  volatile management write to the static TDP level [x]** · OTA [ ] · SoC reset [ ] · PMIC reset [ ] ·
  driver/PCI changes [ ] · AC cycle [ ] · external SPI [ ] · PMIC write [ ] · **clock command [ ]**
- **OTP / fuses / keys / security-policy change: prohibited, and none is reachable from the one command
  used** (rule 8 below). **PASS**
- **Host/machine identity:** `aifoundry2`. Re-read fresh at gate time (`uptime`, `et-lab-manifest`);
  E69's reading of 13:55 PDT today — Ubuntu 24.04 family, kernel 7.0.0-38-generic, 11th Gen Intel Core
  i5-11600, 12 threads, 63 GiB, boot id `42dcb8e5-a96f-45a5-8edc-78c987be4073` — stands as the "before".
  Re-read **14:59:39 PDT**: `aifoundry2`, host up **23 h 46 m**, load 0.58, four idle shell logins and no
  other user's device process. **PASS**
- **Card asset / serial / revision / form factor / DRAM:** re-read fresh by `gov_e72.py gates`
  (`DM_CMD_GET_MODULE_*`); E69's 13:56:26 PDT reading is the "before" (Esperanto, part `0x11345663`,
  module revision `0x2211ab44`, form factor PCIE, DDR 32 GB, ASIC revision 597; the lot id stays in the
  session's own queries and is not reproduced in the public repo). **Module uptime is re-read, and it
  must still show no service-processor reset since the host booted** — if the SP had reset, E69's
  restored values would be boot defaults rather than a real write and the "originals" would need
  re-establishing. Re-read **14:59:39 PDT** by `gov_e72.py gates`: **module uptime 0 d 23 h 46 m**, so
  the service processor has not reset since the host booted on 26 Oct and E69's restored values are a
  real write rather than a reboot's defaults. **PASS**
- **PCI domain:BDF ↔ device number ↔ node:** `0000:02:00.0` ↔ device 0 ↔ `/dev/et0_mgmt`, `/dev/et0_ops`;
  link 16.0 GT/s PCIe x8; driver in use `ET`. One card on this host, so no second card shares the driver
  or root port (contrast aifoundry1, where a module unload affects both). Re-checked fresh.
- **Firmware identities:** re-read fresh (`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`). E69's 13:56:26 PDT
  reading is the "before": release **1.4.0**, BL1 **0.22.0**, BL2 **0.22.0**, PMIC **1.5.0**, Master /
  Worker / Machine Minion **0.25.1**. A different reading at gate time is a **NO-GO**, because the rule-8
  source read below is pinned to BL2 0.22.0. Re-read **14:59:39 PDT**: release **1.4.0**, BL1 **0.22.0**,
  BL2 **0.22.0**, PMIC **1.5.0**, minions **0.25.1** — equal to E69's reading, so the rule-8 source read
  applies. **PASS**
  *(Standing correction, from E69: `docs/findings/14-card-behaviour.md`'s card table still says 1.3.1 /
  BL2 0.20.0 / minion 0.23.0 for this card, which was true before the 10 Oct thermal-v2 update. The
  0.20.0 in the host manifest is the **host driver's** version, not the firmware's.)*
- **Host module / kernel / tools, separately identified:** driver `et-soc1` version string `0.20.0`,
  srcversion `47D26A305A0428B29FB7FC4`; `/opt/et/bin/dev_mngt_service` sha256 begins `a3d4c722d9505aa9`;
  `/opt/et/lib/libdeviceLayer.a` `786fc7650bf74375` (E69, 13:55 PDT). E72's own experiment binaries are
  **E60's**, not E69's: `build/ettelem/ettelem` (lib.sh's sampler), `build/sparsity/host/sparsity_host`
  and the heater, with their digests recorded in each pass's `manifest.txt` and the operand set's hashes
  in each pass's `gen.sha256`. **The operand files are checked byte for byte against E60's published
  `gen.sha256`** by `run_e72.sh setup`, so the 600 MHz rungs and the 800 MHz rungs they are compared
  against are literally the same bytes. Run **14:59:40 PDT**: **59 of 59 operand files byte-identical to
  E60's published hashes, 0 missing**; the 60th line of E60's `gen.sha256` is `manifest.json`, which
  **differs and is expected to** — `make_hl.py` has gained item families since E60 (E70's `alq_`/`aq_` A-side
  ladder among them), so the manifest has grown while every `tiles/*.bin` and `srcs/*.bin` E60 ran is
  unchanged. `make_hl.py --check` re-derived every designed flip count from the files. **PASS**
- **Other affected cards / root-port devices / outlet loads:** none. No work on aifoundry1 or aifoundry3
  is part of E72. **PASS**
- **Existing guest / session / volatile contents:** checked fresh — no Maxion guest, no packet endpoint,
  no resident Linux/9front on this card. `et-who` at **14:59:39 PDT**: *"No process holds an ET-SoC-1
  device node or card lock."* The card lock was free and `gov_e72.py gates` took it exclusively for the
  reads. **PASS**
- **Locks / guards / monitors / CI / services, and how races are excluded:** the mechanism is E69's and
  is unchanged, re-stated because the field manual (hosts § 8) warns that *telemetry and DM do not
  coexist on a single-open management node*:
  - `et-usaged` (root) is read-only and opens no device node.
  - The owner's **lab dashboard collector** reads each card's temperature with `ettelem temp --if-free`
    about once a second; its code probes `/run/lock/etsoc-shire0.lock` immediately before opening the
    management node and opens nothing if anyone holds it (exit 3 = "lock taken, opened nothing"). So
    holding the lock keeps it off the node. **Nothing is killed**: the coordination is the lock the
    collector already honours. Its sibling `keeper.py tick` never opens a card.
  - **E72 holds the lock in two different ways, and this is a departure from E69 worth naming.** E69 held
    the lock for a whole session. E72's measurement harness is E60's `hl/block.sh`, which takes the lock
    **per pass** — so `gov_e72.py` takes the lock for the gate reads and for the single set, **releases
    it**, the passes then take and release it themselves, and the restore takes it again (waiting up to
    180 s for a pass to finish). Between passes the collector may read the card's temperature while
    TDP 0 is set. That is a read of two sensors; it writes nothing and cannot move the governor. The
    exposure it buys is that the pin outlives any one lock holder, which is why the **deadline watchdog**
    exists.
  - A GitHub Actions runner is active on the host; it ran nothing on the card in E69's window and is
    re-checked at gate time.
  - **Dated health flag, recorded not dismissed:** E69 recorded six `ET 0000:02:00.0: Error Event
    Detected / Level Critical / SP Runtime Error` lines at ≈13:58 PDT and 234 by 14:42, every one the
    same syndrome with the count simply climbing, and concluded the count tracks telemetry volume
    (10 Hz sampling for ~20 card-minutes) and not the knob. `docs/findings/14-card-behaviour.md` records
    the same syndrome from September and that it did not stop the card. **Consequence for E72:** the
    kernel log is read before the first set and after the last run and both are kept with the data; a
    line of any **other** description, an AER error, a link error or an all-ones read is an abort. The
    error-event queue is **not** drained (`DM_CMD_GET_DEVICE_ERROR_EVENTS` is never sent: popping it is a
    state change).

## Current state (each item dated at gate time, not copied from an old README)

- **Kernel / config / P2PDMA; loaded module / srcversion / params:** as above; re-read at gate time.
- **Management application identity / digest:** `/opt/et/bin/dev_mngt_service` at the digest above.
- **SoC firmware BL1 / BL2 / Minion identities and evidence:** re-read at gate time; must equal E69's.
- **Current physical active / passive bank and how identified:** **UNKNOWN**, deliberately, exactly as in
  E69. Bank identification needs flash reads, which are a different authorization and disturb programming
  state (field manual, hosts § 2). **The UNKNOWN is not bypassed**: the operation performs no flash
  access at all (rule 8), so neither bank can change.
- **Priority / boot-counter state and supported accounting:** **N-A** — not read, for the same reason;
  the manual warns boot-status probing itself generated an error event on old fleet firmware, and with no
  persistent write there is nothing for boot accounting to protect.
- **Actual config version / offset / persistent assets / Vmin / nonpersistent policy:** not read from
  flash. What **is** read is the service processor's **RAM** copy of the vmin LUT, through
  `DM_CMD_GET_VMIN_LUT` — and that read is itself shown to be RAM-only below, because E72 needs the
  frequency floor before it writes anything.
- **PMIC runtime slot / configured next-boot slot / version / hash / board encoding:** PMIC firmware
  **1.5.0** from the revisions read; slots and board encoding **not read** (no PMIC console, probe or
  programmer route is established for this fleet — field manual, hosts § 4) and **no PMIC command is
  sent**. **N-A for this operation**: no PMIC write path is reachable from the one command used (rule 8).
- **PCIe / link / BAR / DM / ops / thermal / clock / TDP baseline:** read fresh by `gov_e72.py gates`
  into `gov.jsonl` `{"event": "original"}`. **The gate refuses to proceed unless `ettelem config` reads
  `tdp_w: 65` and `temp_threshold_c: 65`** — the values E69 restored and read back at 14:42 PDT — and
  unless the vmin-LUT floor reads **600 MHz**.
  **Read 14:59:39 PDT, under the card lock:** `{"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3,
  "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 519}`. **Both governor fields are at
  their originals. These are the values to restore: TDP 65 W, software threshold 65 °C.** **PASS**
  **vmin LUT, read the same second** (`DM_CMD_GET_VMIN_LUT`, parsed against
  `ESPERANTO_VMIN_LUT_SINGLE_POINT_t`, 18 bytes a point, the minion pair first): **three non-zero minion
  points — 600, 700 and 800 MHz** — and eight zero points. So
  `mnn_frequency_min_limit = 600` and `mnn_frequency_max_limit = 800`, which is also exactly the
  600 → 700 → 800 stepping E69 read out of the governor's own log. **The pin lands on 600 MHz and can go
  no lower. PASS** — this gate was UNKNOWN on the first attempt (the tool writes the LUT to a binary file
  rather than to stdout, so the text parse found nothing) and was resolved by parsing the binary; the raw
  LUT stays out of the public repo as per-card calibration data and only the frequency points are
  published.
- **Live query allowlist; unsafe queries intentionally omitted:** allowed — `GET_MODULE_*` identity,
  `GET_MODULE_FIRMWARE_REVISIONS`, `GET_ASIC_CHIP_REVISION`, `GET_MODULE_UPTIME`, `GET_MODULE_POWER`,
  `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_FREQUENCIES`, `GET_MODULE_STATIC_TDP_LEVEL`,
  `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, and — **new in E72, with its own source
  argument below** — `GET_VMIN_LUT`. Omitted on purpose: `SET_STATS_RUN_CONTROL` / `ettelem --reset-ms`
  (it silently disables the SP statistics trace and resets PVT latches), any trace reset or run-control
  write, `GET_DEVICE_ERROR_EVENTS` (pops a queue), `GET_FIRMWARE_BOOT_STATUS`, `GET_FUSED_PUBLIC_KEYS`,
  every `MDI_*`, **`SET_FREQUENCY`**, **`SET_VMIN_LUT`**, `SET_MODULE_VOLTAGE`,
  `SET_MODULE_ACTIVE_POWER_MANAGEMENT`, `SET_THROTTLE_POWER_STATE_TEST`, `MM_RESET`, `RESET_ETSOC`, and
  every firmware-update command. **PASS**

## Rule 8 — no incidental board-data change (the gate this operation turns on)

Field manual rule 8: *"Protect per-card configuration/Vmin, DRAM training, PCIe configuration,
VaultIP/certificates, and layout."* The brief's binding form: **before any set, read the firmware source
of the exact running build and show that the SET path does not write flash or configuration data.** The
counter-example is real: on BL2 **0.18.0** `pwr_svc_set_module_voltage` called
`flash_fs_set_vmin_lut_boot_voltages()`, which erases and reprograms the 4 KB asset-config sector, so on
that build a *voltage* set silently became the card's boot voltage (`docs/findings/05-claims.md`, the NV
row). A command that looks volatile is not automatically volatile.

**Source read.** The card reports BL1/BL2 **0.22.0**. The et-platform copy on the Intel, commit
`836a4ab600e93c3059bb58c898edbc37744cd8d0` (2026-07-17), declares `project(EsperantoBootLoader VERSION
0.22.0)` in `device-bootloaders/CMakeLists.txt:4`. Files read out of the git objects (`git show HEAD:…`)
because the working tree is partly checked out.

**Finding 1 — the one set path writes one RAM byte and nothing else. PASS.** This is E69's finding for
the same command on the same build, re-verified here for the value E72 uses:

| Step | Source at BL2 0.22.0 | What it does |
|---|---|---|
| dispatch | `services/thermal_power_monitor.c:966-971` | reads the level out of the command buffer, calls the handler |
| handler | `thermal_power_monitor.c:392-415` `pwr_svc_set_module_tdp_level` | calls `update_module_tdp_level`, fills the response header, pushes the response. No other call. |
| setter | `services/thermal_pwr_mgmt.c:576-591` | `if (tdp > POWER_THRESHOLD_HW_CATASTROPHIC) return INVALID;` **else** one `Log_Write` and one assignment `g_pmic_power_reg.module_tdp_level = tdp` |
| the target | `thermal_pwr_mgmt.c:143-144` | `volatile struct pmic_power_reg_t g_pmic_power_reg __attribute__((section(".data")))` — plain service-processor `.data` RAM, not a memory-mapped window, not flash. Lost at an SP reset. |

**The value 0 specifically.** `POWER_THRESHOLD_HW_CATASTROPHIC` is 75 and
`POWER_THRESHOLD_SW_MANAGED` — the boot default — is 65 (`include/thermal_pwr_mgmt.h:48,60`;
`bl2_pmic_controller.h:262`). The **only** value-dependent branch on the path is `tdp > 75`, so 0 takes
the same single-assignment else-branch as 45 or 65 did in E69; there is **no lower bound and no special
case for 0** anywhere on the path. 0 is also the value the firmware itself can hold legitimately: it is
aifoundry3's standing policy. **PASS**

**Finding 2 — nothing on that path can reach flash or the PMIC. PASS.** The only writers of flash in the
BL2 0.22.0 tree are in `driver/flashfs.c` (`flash_fs_write_partition`, `flash_fs_erase_partition`,
`flash_fs_set_part_number`, `flash_fs_set_vmin_lut`, `flash_fs_write_config_region`,
`flash_fs_increment_*_boot_count`), and their only call sites are `common/main.c:488` and
`rtos_task/flash_fs.c:121` (the boot counter), `services/asset_track.c:87` (`flash_fs_set_vmin_lut`,
reached only by the VMIN-LUT **set** command, which E72 never sends), `services/asset_track_mgmt.c:39`
(the part number) and `services/firmware_update.c:752` (the OTA's config copy). `thermal_pwr_mgmt.c`
touches `flash_fs_*` data only to **read** `…persistent_config.vmin_lut[0]` (lines 1630, 2490). No PMIC
write either: the docstring claims the value is "set in PMIC" and the code sends the PMIC nothing — the
only `pmic_set_voltage` calls in the file are in the operating-point path (lines 3021, 3056), which this
command never enters. *The stale docstring is itself the trap rule 8 exists to catch.*

**Finding 3 — `DM_CMD_GET_VMIN_LUT`, the one query E72 adds, is a RAM read. PASS.** The field manual
warns that *"flash-read … SPI reading changes power/programming mode"*, so a query with "LUT" in its name
needs the same treatment as a write. `rtos_task/command_dispatcher.c:139` → `services/asset_track.c:196`
→ `asset_svc_getvminlut` (`:74`) → `flash_fs_get_vmin_lut` (`driver/flashfs.c:2073`), whose whole body is
one `memcpy` out of `sg_flash_fs_bl2_info.asset_config_data.persistent_config.vmin_lut` — the service
processor's in-RAM copy of the config, populated at boot. **No SPI controller call, no erase, no
programming mode.** Its sibling `flash_fs_set_vmin_lut` (`:2082`) *is* a full erase-and-reprogram of the
config sector, which is why `DM_CMD_SET_VMIN_LUT` is on the prohibited list above.

**Finding 4 — what the pin does to the governor, and that it is reversible without a reset. PASS.**
`check_power_throttle_conditions` (`thermal_pwr_mgmt.c:866-928`) compares an **unsigned** mW average
against `tdp_level_mW`: at 0 the power-**down** branch is true under any load and the power-**up** branch
(`avg < tdp`) is unreachable. The down branch is gated on `f > minion_min_frequency`
(`= vmin_lut_limits.mnn_frequency_min_limit`, set at `:1597`), and `reduce_minion_operating_point…`
(`:1888`) only ever steps to the LUT's previous point, so the clock lands on the floor and stops. The
throttle task treats **`POWER_UP` as always allowed from any state** (`:2267-2270`), so the first
governor pass after the original 65 W is written back has `avg < 65000` and `f < f_max` and steps up —
which is what E69 observed when it restored a 45 W cap and saw 10 power-down / 12 power-up events in the
return burst. **There is no firmware latch.** aifoundry3's pin is a boot-time policy that re-writes 0,
which is what the manual's note about *"a stale success marker stopped the guard from reapplying"*
describes.
**Correction to E69, recorded:** E69's hazard note says the power-down loop's exit "needs averaged board
power under 1.05 × TDP". In this build `UPPER_POWER_THRESHOLD_GUARDBAND` and
`LOWER_POWER_THRESHOLD_GUARDBAND` (`:212-223`) are **defined and never used** — the comparison is bare.
Same conclusion, simpler mechanism.
**Side effect, named not hidden:** `get_power_state()` (`:405-415`) classifies any power above the TDP
level as `POWER_STATE_MAX_POWER`, so while TDP 0 is set the reported power state reads `max_power` and
the max-power **residency counter** accumulates. That is accounting in the same `.data` RAM; it is read
by `GET_MODULE_POWER_STATE` and `GET_POWER_RESIDENCY` and drives nothing. It returns to normal when the
original TDP is restored.

**Residual uncertainty, stated plainly.** The field manual warns (runbook § 7) that *"same semantic
0.22.0 is not sufficient to distinguish BL2 builds"*, and the card exposes no build git hash through any
query this record allows. So the source read establishes the behaviour of **a** BL2 0.22.0, not provably
of the exact binary. Two things reduce the residual: the BL2 **0.20.0** review of the same set path
reached the identical conclusion — RAM only, *"all of these live in RAM and are lost at an SP reset"*
(`docs/reports/data/2026-09-28-dvfs2-aifoundry2/plan/review-governor.md` § 1.3, § 8) — so both plausible
builds agree; and E69 set this field seven times on this card today with 23 commands, every one rc 0 and
zero read-back mismatches, with the firmware revisions unchanged afterwards. **Rule 8: PASS, with the
build-identity residual named.**

## Restore before risk (this operation's G1)

- **What can go wrong, and what survives it:** the only state changed is one RAM byte. An SP reset, a
  card reset or a power cycle restores the default (65 W) by itself. The "recovery artefact" is the
  number **65** plus the command that writes it, recorded in this file, in `gov.jsonl`
  `{"event": "original"}` and in `{"event": "set"}`'s `before`. **PASS**
- **Exact independent recovery path:** none beyond the above is needed for this field, and **none is
  available for anything worse**: no PMIC console, probe or programmer route is established for this
  fleet (field manual, hosts § 4), `/dev/mtd0` on these hosts is host BIOS and not card SPI, and the
  owner's rules forbid a card reset here. **This is the operation's binding limitation**, and it is why
  E72 writes one non-persistent field, never raises the cap, sends no clock command, and arms a deadline
  watchdog. Recorded as a **limitation, not a PASS.**
- **Full SPI backup / PMIC backup / protected-region baseline:** **N-A** — no flash or PMIC byte is
  written or read (rule 8, findings 2 and 3). No backup is taken and none is claimed.
- **Power-loss / partial-write plan:** a power loss during the set loses only the RAM byte and the SP's
  boot default returns. No retry chain, no reset and no slot work exists in this operation.
- **How the restore is executed and proved:** `gov_e72.py restore` takes the card lock (waiting up to
  180 s for a measurement pass to finish), writes 65 W, reads `ettelem config` back and records
  `{"event": "restore", "ok", "before", "after", "original"}`. A read-back that is not equal to **both**
  originals (TDP 65 W **and** threshold 65 °C) makes the stage exit non-zero and leaves the watchdog
  armed. `run_e72.sh back` then runs a short burst at the restored settings, which must show the clock
  stepping above the floor.
- **The pin cannot outlive the session:** `gov_e72.py pin` arms a detached watchdog **before** it sends
  the set. The watchdog waits for a `release` file or 75 min, then takes the card lock with
  `flock -w 120` and writes 65 W back, logging the result. It writes one value, never resets, never
  raises the cap, and is the reason the per-pass lock pattern is acceptable.
- **If the restore fails or the card stops answering:** stop; **keep the card claim**; write it up; alert
  the owner with `notify.py --unblock`. **Do not reset the card**, even though a reset would restore the
  default, and do not retry blindly (field manual rule 11).
- **Automatic fallback status:** **N-A** (nothing persistent is written, so there is nothing to fall back
  to).

## Candidate and build provenance

**N-A in full: there is no candidate artefact.** No image is built, composed, staged, hashed for release
or written. The only software this operation introduces is host-side and in the public repo:
`predict_e72.py`, `predictions.json`, `gov_e72.py`, `run_e72.sh`, `reduce_e72.py`, this record and
[`README.md`](README.md), all committed and pushed **before the first card access**. The measurement
binaries and the operand files are **E60's own**, unchanged, and the operands are checked byte for byte
against E60's published `gen.sha256`. The one command sent is the stock `dev_mngt_service`'s.

## Immediate release gate (G4)

- **Identity / ownership rechecked at:** immediately before the set, inside the card lock, by
  `gov_e72.py pin` (it re-reads `ettelem config` and refuses unless **both** fields are at their
  originals). Timestamps in `gov.jsonl`.
- **No guest / SDK / Minion / DMA / monitor conflict:** `et-who` empty; the dashboard collector held off
  by the card lock it already honours; no second card on the host.
- **Unique receipt directory:** `docs/reports/data/2026-10-27-e72-600mhz/`, one subdirectory per pass; no
  reused trace filename, no wildcard deletion, no mutable `current-*` pointer.
- **Capture ready before the first set:** `block.sh` starts its 10 Hz sampler before each pass's first
  launch; no `--reset-ms` is ever sent, so the SP statistics trace and the PVT latches are untouched.
- **Exact approved command and environment:**
  `dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 0 -u 5000` and the same with `-l 65`,
  under `LD_LIBRARY_PATH=/opt/et/lib`, each wrapped in `timeout 20` and each followed by
  `ettelem config`. **No reset is planned or permitted. No clock or voltage command is sent.**
- **Bounds enforced in code, not only in prose:** `gov_e72.py` writes only the literal values 0 and 65
  (`TDP_PIN_W`, `ORIG_TDP_W`); it refuses to run if the threshold is not 65 °C and refuses to continue if
  a set moved the threshold; the vmin-LUT floor must read 600 MHz; the pass stops at a 78 °C reading
  (lib.sh) and the session aborts and restores above **85 W** board (E69's bound, not raised).
- **GO / NO-GO / UNKNOWN:** **GO**, 2026-10-27 **15:06 PDT**, on the gates above, with the two standing residuals
  (build identity; no independent hardware recovery path for this fleet) and E69's dated health flag.
- **Operator releasing this operation:** the owner's authorization of 27 Oct 2026 for the governor on
  this card, naming E72's TDP-0 pin specifically, recorded verbatim above. No "it built, therefore run
  it" step exists here.

## Set log — every set and read-back, with timestamps

The machine-readable record is `gov.jsonl` in the data directory: one line per event — `original`,
`identity`, `vmin_floor`, `watchdog_armed`, `set` (with `asked`, `before`, `after`, the command's argv,
rc and an ISO-millisecond timestamp) and `restore`. Filled from it after the session:

| Item | Value |
|---|---|
| Originals read under the lock, before any set | 2026-10-27 **14:59:39 PDT** — TDP **65 W**, software threshold **65 °C**, power state `low_power`, 600 MHz, 519 mV |
| vmin-LUT minion frequency floor | **600 MHz** (points 600 / 700 / 800), read 14:59:39 PDT |
| Watchdog armed (before the set) | 15:01:31.999 PDT, 4,500 s deadline, detached |
| Sets sent | **two**: `-l 0` at **15:01:32.038 PDT** (read back `tdp_w: 0`, threshold still 65 °C) and `-l 65` at **15:24:07.531** (read back `tdp_w: 65`, threshold 65 °C) |
| Command exit statuses | **both rc 0** |
| **Read-back mismatches** | **0** — each set was followed by `ettelem config` and compared field by field; the session also refuses to continue if a set moved the threshold |
| Restore | 15:24:07.531 PDT, **`ok: true`**, equal to the originals; `release` written, watchdog logged *"released by the session, nothing to do"* |
| Independent read-back after the last run | 15:24:48 PDT, a separate `ettelem config`: TDP **65 W**, threshold **65 °C**, `low_power`, 600 MHz, 519 mV |

## Activation and acceptance

- **Separate reset approval / type:** **none sought and none performed.** The field takes effect on the
  next governor pass (about 0.24 s) with no reset; that is the whole point of using it.
- **Host reinit / PCI mapping / card re-identified:** no reset, so no re-enumeration; the card's identity
  is re-read after the last run.
- **New running firmware identity:** unchanged by construction; re-read after the last run.
- **PMIC runtime and next-boot state:** unchanged; no PMIC command sent.
- **Configuration / clock / TDP policy checks:** `ettelem config` after the set, after the restore, and
  the per-sample clock gate inside every pass's reduction.
- **Fresh management / thermal / error results:** the end queries; the kernel log before the first set
  and after the last run, both kept with the data.
- **Hardware-mode evidence:** every launch is a real PCIe device process (`sparsity_host` with the card's
  own kernel ELF); there is no SYSEMU path in this harness.

## Outbound OTA / fallback qualification

**N-A: no OTA is performed, so nothing about the card's update path is exercised, changed or claimed.**

## Final handoff

- **Retained firmware / module / PMIC / bank state:** unchanged, re-read 15:24:48 PDT — release **1.4.0**,
  BL1 **0.22.0**, BL2 **0.22.0**, PMIC **1.5.0**, Master / Worker / Machine Minion **0.25.1**; driver
  `et-soc1` srcversion `47D26A305A0428B29FB7FC4`. No bank was read or written.
- **Governor fields at handoff: TDP 65 W, software threshold 65 °C — equal to the originals.** The
  threshold was never written at all. Read back twice: by the restore itself at 15:24:07.531 (`ok: true`)
  and by an independent `ettelem config` at 15:24:48. **Module uptime 1 d 0 h 12 m**, so the service
  processor never reset: the restored value is a real write, not a reboot's default.
- **The back check.** One short burst at the restored settings (`e72back-smoke/p901`, 15:24:07 → 15:24:31)
  stepped the clock **600 → 700 → 800 MHz** — 114 samples at 600, 2 at 700, 98 at 800, voltage to 619 mV,
  board to 59.7 W. Against the pinned smoke's **215 of 215 samples at 600 MHz**, that is the governor's
  power-up branch working the moment the cap was back, with no reset. **G3: PASS.**
- **Guest / excluded memory / packet / core state:** none existed and none was created.
- **Error events across the whole operation:** the host kernel log's `Error Event Detected` count was
  **234 before the first set and 234 after the last run — E72 added none.** No AER, no link error, no
  all-ones read. One new line of another kind, recorded not hidden: `ET 0000:02:00.0: Mgmt: Tried to open
  same device multiple times` at host uptime 85,783 s (≈15:03 PDT), which is **this session's own**
  `gov_e72.py status` poll running while a measurement pass held the card lock and the single-open
  management node. The poll returned `null`, nothing else happened, and the lesson is not to poll the
  governor during a pass.
- **Card lock and claim:** the lock was taken per stage (gates, the set, each pass, the restore) and is
  free at handoff — `et-who`: *"No process holds an ET-SoC-1 device node or card lock."* The
  `#community-lab` claim (`1564760469741510737`, 14:59:27 PDT) is released after the data README is
  pushed.
- **Services restored:** the dashboard collector resumes by itself; it was never stopped, signalled or
  killed. The deadline watchdog exited cleanly without acting.
- **Logs / artefacts:** `docs/reports/data/2026-10-27-e72-600mhz/`, all committed to the public repo,
  including `gov.jsonl` with every governor event's argv, rc and millisecond timestamp.
- **Unresolved risks / prohibited next actions:** the build-identity residual on rule 8 (the card exposes
  no BL2 git hash through an allowed query); the absence of any independent hardware recovery path for
  this fleet; no independent reviewer saw the run. Prohibited without fresh authorization: raising the
  TDP level above the card's default, lowering the software threshold below a pattern's die temperature,
  `SET_FREQUENCY`, `SET_VMIN_LUT`, touching active power management, and every reset, PMIC, flash and OTA
  operation. **One thing E72 establishes that a future session may want:** aifoundry3's 600 MHz pin is a
  boot-time policy writing TDP 0, not a firmware latch, so writing its TDP back would un-pin it — that is
  a *different card* and needs its own authorization and its own change record.
- **Signoff:** 2026-10-27 **22:50 UTC / 15:50 PDT** (Tue, ISO week 44). Operator: the AI Foundry agent
  `a2-e72-600mhz`. Independent reviewer: **none** — stated as a limitation of this record, not as a pass.
  The governor is at its defaults, the card is healthy and stepping normally, the firmware is untouched,
  and no flash, PMIC, reset, driver, PCIe, clock or voltage action was performed at any point.
