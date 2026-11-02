# ET-SOC1 change record — E77, the rail at one temperature, at two rail voltages (aifoundry2)

Filled from `templates/change-record.md` of the ET-SoC-1 firmware rebuild / OTA field manual (private; kept with the
operator's notes and on the lab boxes, not in this repository). Every gate carries **PASS / FAIL / UNKNOWN / N-A** with
its time and evidence; **UNKNOWN is never PASS**. Desk gates were drafted by the Q133 desk lane on Sun 1 Nov 2026
(13:05 PST, corrected after an independent verification at 14:11 PST) and are carried here by the run agent, who
re-checked each; the live gates are filled at gate time, timestamped, and committed as the GO **before** the first
write. Local stamps are PST (UTC−8).

**What this operation is** (the manual's runbook § 1): *authorized live observation* plus **one** *non-persistent
management write*, `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26), 65 → **0** W and back to 65 W — the TDP-0 pin E72 used on
this card on 27 Oct. **Lowering is the safe direction.** The threshold is not written. It is not an OTA, build, flash,
PMIC command, reset, driver or PCIe action, and **not a clock command** (`DM_CMD_SET_FREQUENCY` is never sent).

## Identity / authorization

- **Record ID:** `E77-twovolt-2026-11-01`. **Operator:** an AI Foundry agent of the Q133 governor workflow, on the lab's
  owner's behalf, over ssh. **Reviewer:** none independent of the run (a limitation); the desk packet had an
  adversarial verification before the run. **Hardware owner:** the lab's owner. **Recovery operator:** the owner and the
  lab's firmware maintainer, never this run (G1).
- **Authorization, and its scope:** the owner's OK of Sun 1 Nov 2026, about 12:30 PST, for E77 as a governor move (the
  static TDP level and the software threshold only), one of three named runs, conditional on reading the firmware
  maintainer's posted guidelines first. **Read in full on 1 Nov, 13:54–14:01 PST** (every post of his in the lab's
  Discord channel and in the owner's direct messages with him, each from its start, and in the lab's other technical
  channels since 1 Sep; 258 posts): the field manual and no deviation from its gates (20 Oct); firmware changes stay with
  him, because firmware failures can brick a box (7 Oct); a wedged card or host is recovered by a host soft reboot and
  then an AC-outlet cycle through the lab's power switch (Aug–Sep), which once left this host stuck until someone went to
  the lab (7–8 Oct); known firmware bugs, a thermal loop on a hot card among them. None addresses the governor or forbids
  this operation; a lowered TDP is one RAM byte, not a firmware change (rule 8). ⟨RUN: re-checked for any newer post of
  his in `#community-lab` and the direct messages just before the claim: see "Live gates"⟩
- **Allowed:** offline build [ ] · live observation [x] · **one volatile write of the static TDP level to 0 W and its
  restore to 65 W [x]** · OTA [ ] · SoC reset [ ] · PMIC reset [ ] · driver/PCI changes [ ] · AC cycle [ ] · external
  SPI [ ] · PMIC write [ ] · PMIC firmware-management or slot query [ ] · clock command [ ] · threshold write [ ] ·
  statistics reset [ ] (allowed in general by the owner's ruling of 31 October 2026; not used, so that the rails stay the
  PMIC's own running average, τ ≈ 1.06 s, the ledger's footing, and the governor's average is not restarted).
  **OTP/fuses/keys/security policy: prohibited, untouched.**
- **Approved window:** one session on aifoundry2, starting after Q133's E111 has released the card and no later than
  18:00 PST, ending (restore included) by 19:00 PST; at most 50 card-minutes. Affected users: anyone wanting aifoundry2
  in the window, told by the one-line `#community-lab` claim.
- **Host / card / node:** `aifoundry2`, one card, `0000:02:00.0` ↔ device 0 ↔ `/dev/et0_mgmt`, `/dev/et0_ops`.
  ⟨RUN: re-read from sysfs, `uptime`, `et-who`⟩. Other cards sharing the driver or root port: none (one card).
- **Firmware identities: by continuity, not re-queried.** Expected release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions
  0.25.1: E69's revisions read, 13:56:26 PDT on 27 Oct, with the service processor up since the host's 26 Oct boot.
  The revisions query is **not** sent again: at et-platform `836a4ab` it writes the PMIC's firmware-management command
  register twice (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974, 2531-2557, 2581-2600`), a PMIC
  command. ⟨RUN: `DM_CMD_GET_MODULE_UPTIME` (service-processor RAM, `thermal_pwr_mgmt.c:1451-1455`) must exceed the
  minutes since 13:56:26 PDT on 27 Oct; an image takes effect only through a reset, so an unbroken uptime carries the
  identity. Shorter is **NO-GO**⟩
- **Ordering on the card:** after Q133's E111 has released aifoundry2. E117 did not run (its desk verdict was NO-GO,
  pending an owner decision on its outage risk), so nothing of E117's precedes this. Never two sessions on the card.
- **Locks / monitors / races:** the owner's dashboard collector (`live-collector.py`) reads temperatures with
  `ettelem temp --if-free` (two GETs, neither reaching the PMIC) and opens nothing while `/run/lock/etsoc-shire0.lock`
  is held. **One runner holds the lock for the whole session** (E69's structure); the gate reads take it for their own
  short hold before. The management node allows one opener, so the sampler is stopped for every set and every query,
  and the governor is never polled during a pass. ⟨RUN: the collector's state and hash at gate time⟩

## Current state

- ⟨RUN⟩ kernel, module srcversion and hash, tool hashes (`gates.json`, `session.json`).
- **The originals by the two RAM GETs** (`DM_CMD_GET_MODULE_STATIC_TDP_LEVEL`, `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS`,
  through `ettelem-e77 config`): **must read 65 and 65** (the boot defaults, `thermal_pwr_mgmt.c:1672-1676`), else NO-GO.
  ⟨RUN⟩
- **vmin-LUT floor:** `DM_CMD_GET_VMIN_LUT` (a copy from the service processor's RAM, `driver/flashfs.c:2073`, E72
  finding 3), **parsed in code** from the binary file the vendor tool writes (14 points of 18 bytes, the minion frequency
  the first little-endian 16-bit word of each; only the frequency points are published, the file stays on the host as
  per-card calibration data). The floor must be **600 MHz** (E72 read 600 / 700 / 800 on this card), else NO-GO. E72's
  harness wrote `floor_mhz: null` and proceeded; that gap is closed here. ⟨RUN⟩
- Bank / boot counters: UNKNOWN, deliberately (they need flash access) / N-A. PMIC slots: not read (a PMIC command).

### What each planned query asks of the card (et-platform `836a4ab`)

- **Sent, no PMIC access:** `GET_MODULE_POWER` (a RAM copy, `thermal_pwr_mgmt.c:984-988`), `GET_SP_STATS` (RAM,
  `services/performance.c:420-466`), `GET_MODULE_CURRENT_TEMPERATURE` (on-die PVT, `thermal_pwr_mgmt.c:732-773`),
  `GET_ASIC_FREQUENCIES` (PLL registers, `services/perf_mgmt.c:276-`), the TDP, threshold and power-state GETs and
  `GET_MODULE_UPTIME` (RAM), `GET_MODULE_RESIDENCY_THROTTLE_STATES` (RAM), `GET_VMIN_LUT` (a RAM copy), and the ring
  dump, which is no DM command at all: two driver ioctls copying the service processor's trace region by MMIO
  (`et-driver/et-soc1-pcie.c:719-720, 1021-`).
- **Not sent (the no-PMIC-read profile):** `GET_ASIC_VOLTAGE` (it reads two PMIC voltage registers besides its PVT
  values, `thermal_pwr_mgmt.c:1212-1216` → `pmic_get_voltage` → `get_pmic_reg`) and `GET_MODULE_VOLTAGE` (nine such
  reads, `:1010-1120`), which the stock samplers send with every sample and the stock `config` with every call. The
  tool `ettelem-e77` is built without them and without any set; its `profile` command lists what it can send. E77's
  inputs (board power, the service processor's rails and `sp.minion_mv`, the die, the clock) are all still read.
- **Also omitted:** the revisions query, `SET_STATS_RUN_CONTROL`, trace resets, `GET_DEVICE_ERROR_EVENTS` (it pops a
  queue), `GET_FIRMWARE_BOOT_STATUS`, every `MDI_*`, every `SET_*` but the one TDP write, resets, firmware-update
  commands, every PMIC command.

## Rule 8 — no incidental board-data change (desk: PASS at the version-matched source; build-identity residual named)

At et-platform `836a4ab600e93c3059bb58c898edbc37744cd8d0` (2026-07-17; `device-bootloaders/CMakeLists.txt:4` declares
`project(EsperantoBootLoader VERSION 0.22.0)`), read from the git objects at 12:44 PST: the TDP set is dispatched at
`services/thermal_power_monitor.c:966-971`, handled at `:392-415` (`pwr_svc_set_module_tdp_level`), and set at
`services/thermal_pwr_mgmt.c:576-591` (`update_module_tdp_level`: refuse `tdp > 75`, else one `Log_Write` and
`g_pmic_power_reg.module_tdp_level = tdp`), a `volatile` struct in `.data`, service-processor RAM
(`thermal_pwr_mgmt.c:143-144`). **The value 0:** the only check is `tdp > 75`, so 0 takes the plain assignment —
aifoundry3's boot service writes it at every boot. **No flash writer is reachable:** the six writers are all in
`driver/flashfs.c`, called from outside it only at `common/main.c:488`, `rtos_task/flash_fs.c:121` (boot count),
`services/asset_track.c:87` (VMIN-LUT set), `services/asset_track_mgmt.c:39` (part number) and
`services/firmware_update.c:752` (OTA config copy); **no PMIC write** on the path (the only `pmic_set_*` in the two
thermal files is the operating-point path's `pmic_set_voltage`, `thermal_pwr_mgmt.c:3021, 3056`). **The set path is
byte-identical across the whole public 0.22.0 line** (`ce7297156` → `836a4ab`; four commits touch the two files and
leave both setters and handlers unchanged). **Residual:** no BL2 hash is exposed, and the lab's cards run thermal
builds flashed 7–10 October that add to `836a4ab`. The first version of the raw-temperature patch, posted by the lab's
firmware maintainer on 7 Oct, only adds (a new read command, its handler, one dispatcher case after the set cases, one
route) and touches neither set path nor `thermal_pwr_mgmt.c`; its second version, which the image recorded for this card
carries, the boot-counter fix beneath it, and the binary itself are unread. Same footing as E72 on this card, which set
the same field with zero read-back mismatches. **Read as byte-exact provenance, rule 8 would be UNKNOWN and this run
NO-GO; the owner's operational definition (the source at the revision matching the reported versions) and E69/E72's
accepted standard make it PASS.** Stated, not hidden.

**What the pin does at 0.22.0** (E72 finding 4, re-read at `836a4ab`): `check_power_throttle_conditions`
(`thermal_pwr_mgmt.c:864-926`) compares `avg_soc_pwr_mW > tdp_level_mW` with no guardband; at 0 the power-down branch is
true under any load, gated on `minion_curr_frequency > minion_min_frequency` (the LUT floor, `:1594-1597`), so the clock
walks to 600 MHz and stops; it acts only while the master minion is busy (`get_mm_state() != MM_STATE_IDLE`, `:880`);
`POWER_UP` is always allowed (`:2266-2269`), so writing 65 W back releases it on the next busy pass — measured on this
card: 600 → 700 → 800 MHz inside one 6 s launch, no reset (E72). Side effect, harmless: while TDP 0 is set the
power-state label reads `max_power` (`:403-415`) and its residency accumulates.

## Recovery established BEFORE risk (G1)

- **Exact independent recovery path:** none this run may take (a limitation, not a PASS). The worst plausible case is
  E72's: a pin restored by one write. No card reset, no retry chain. The maintainer's posted recovery for a wedged card
  (a host soft reboot, then an AC-outlet cycle through the lab's power switch) is a reset and power action outside the
  owner's governor OK, takes the host from every user, and once left this host stuck at its BIOS screen until an on-site
  visit (7–8 Oct): it is the owner's and the maintainer's to take, never this run's. If the restore fails or the card
  stops answering: stop, keep the claim, write it up, alert the owner (`notify.py --unblock`), never reset or reboot.
- **What changes:** one service-processor RAM byte; the artefact to restore is the number 65 and its command (this
  file, `gov.jsonl`, the watchdog script).
- **Deadline watchdog,** armed **before** the set: if the session has not written `release` within 75 min (or by
  18:55 PST, if sooner), it takes `flock -w 120` on the card lock, writes 65 W (`timeout 20`, `-u 5000`), reads the GETs
  back and logs. One value; it never resets and never raises.
- SPI / PMIC backups, rollback artefact, bank selection, automatic fallback, power-loss plan: **N-A** (nothing is
  written to flash, the PMIC or any bank; a power loss leaves the boot default, 65 W, `thermal_pwr_mgmt.c:1672-1676`).
- **Outage escalation (G1's last item):** none is approved or planned; the run stops instead.

## Candidate and build provenance (G2)

**N-A** for firmware (no image). Host-side tools, all in this repository and pushed before the claim: the runner
`tools/claims-v3/e77/run_e77.py`, its protocol, `predict_e77.py` and `predictions.json`, `reduce_e77.py`, the
telemetry tool `tools/claims-v3/e77/ettelem-e77/` (built on the host into `build/ettelem-e77`, its sha256 recorded at
gate time), this record and the README. Code bounds: the runner writes only the literal values 0 and 65, refuses any
other value and never sends a threshold write.

## Preserve the next update (G3)

**N-A** (no image changes; the updater, dispatcher, flash filesystem and PMIC paths are untouched). What G3 asks of a
governor move in E69's mapping — that the governor be shown to work afterwards — is the return burst below.

## Immediate release gate (G4) — the plan

- **Exact commands:** `dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 0 -u 5000` and the same with
  `-l 65`, under `LD_LIBRARY_PATH=/opt/et/lib`, each in `timeout 20` and followed by the two RAM GETs (`ettelem-e77
  config`: the GETs' TDP, not the boot-time DIR copy that a static "TDP (W)" line shows, `config/dir_regs.c:320-325`).
- **The ladder** (`E77-PLAN.md`; fp32 randn held fixed; per-shire hart counts; 4 s launches; the median of the 10 Hz
  board samples and the raw rails over [t1 − 1.5, t1]):

  | rung | arm A, 600 MHz (TDP 0) | predicted minion W | arm B, 800 MHz (own governor) | predicted minion W |
  |---|---|---|---|---|
  | 1 | 1,024 harts (32/shire) | 22.40 | 544 (17/shire) | 22.36 |
  | 2 | 768 (24/shire) | 16.69 | 416 (13/shire) | 16.90 |
  | 3 | 544 (17/shire) | 11.69 | 288 (9/shire) | 11.44 |
  | 4 | 288 (9/shire) | 5.98 | 160 (5/shire) | 5.98 |

- **One temperature:** every launch of both arms passes the same die gate (preheat to 59 °C; launch at ≤ 58 °C once
  the minion rail has settled, ≥ 6 s after the last device process; the README's departure 3).
- **Order:** gate reads (uptime, originals, LUT floor; their own hold of the lock) → the GO committed → the session:
  arm B passes 1–2 (no move) → watchdog → **set 0 W**, read back (TDP 0, threshold 65) → arm A passes 1–3 (every
  measurement launch must read 600 MHz throughout, else the session aborts and restores) → the 8 s settling rung →
  **restore 65 W**, read back, `release` → the return burst (one 4 s launch of 544 harts: the clock must reach 800 MHz,
  and the ring dumped after it must hold a throttle-up line; E72's G3 was PARTIAL for want of that dump) → arm B pass 3
  → closing reads (the two RAM GETs, uptime).
- **Abort — the envelope's words, as written:** **any single 10 Hz board reading ≥ 85 W** (not expected: arm A's top
  rung and heater are about 51 W at 600 MHz, and arm B's loads model to 66–70 W at most, its heater being 768 harts
  because the full card at 800 MHz reads 82–85 W); die ≥ 72 °C on any reading (the die mean; the high-water latch,
  which is not a live reading, at 80 °C, E69 A1); any clock other than 600 MHz in an arm-A launch; a DM rc ≠ 0 or a
  read-back mismatch; a management timeout; a device process outliving `timeout 10`. Every abort restores in the
  session's `finally`.
- **Card time:** 72 launches plus the gates: about 35 card-minutes, at most 50 (the runner cuts at 47); the claim
  `for 1 h`.
- **GO / NO-GO:** desk **GO-READY**. ⟨RUN: GO only when every live item reads as required, recorded in a commit made
  before the set⟩

## Live gates (filled at gate time, Sun 1 Nov 2026)

The gate reads ran 17:26:26.822–17:26:29.025 PST under the card lock (`raw/gates.json`), the smoke 17:26:37–17:26:51
PST (`raw/smoke/smoke.json`), both with no write. Telemetry profile: **no-PMIC-read**, `ettelem-e77` built on the host
at 16:04 PST, sha256 `21e7bf77e631eb7e…`; runner `run_e77.py` sha256 `fe316bdf53d7defa…` (= amendment A2's commit);
heater `build/sparsity_t2` host `7adadf4f1ce331cc…`, kernel `990807f483cd57aa…`.

| gate | read | verdict |
|---|---|---|
| G0 host and card | `aifoundry2`, kernel 7.0.0-38-generic, host up since 2026-10-26 15:13:03 PDT; card `0000:02:00.0`, PCIe 16.0 GT/s x8 (`et-lab-manifest`, `raw/manifest-gates.txt`); `et_soc1` 0.20.0, srcversion `47D26A305A0428B29FB7FC4`, module sha256 `3ae3759cf857874e…`; `dev_mngt_service` sha256 `a3d4c722d9505aa9…` | PASS |
| G0 identity by continuity | module uptime **6 d 3 h 13 m = 8,833 min** at 17:26:28 PST, against **7,470 min** since E69's revisions read (27 Oct 13:56:26 PDT), and equal to the host's own uptime: no service-processor reset since, so that read (release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions 0.25.1) still names the running image. The revisions query was not sent | PASS |
| originals, the two RAM GETs | **TDP 65 W, threshold 65 °C**, `low_power`, 600 MHz (idle) | PASS |
| vmin-LUT floor, parsed in code | minion points **600 / 700 / 800 MHz**, 11 zero points; the file's sha256 `c9359513ce4d3769…` is the one E72 read on 27 Oct (`2026-10-27-e72-600mhz/vmin-lut.json`), so the LUT is unchanged; the file stays on the host | PASS |
| exclusivity | `et-who`: "No process holds an ET-SoC-1 device node or card lock."; module use count 0; no other login (17:25:51 PST); Q133's E111 released aifoundry2 at 17:25 PST (its claim edited); this run's claim, message `1566624449086628034`, posted 17:26:15 PST: "using aifoundry2 for 1 h, until ~18:25 PST" | PASS |
| collector | 3 `live-collector.py` processes, sha256 `58e7dc1b9f755be3…` (the desk's record); it opens nothing while the lock is held | PASS |
| ring before | `sptrace` rc 0: 18 throttle-up lines (E111's runs), no throttle-down, no PMIC-alarm or POWER_SAFE line | recorded |
| residencies before | POWER_UP cumulative 4,702 s; POWER_DOWN 0; the THERMAL_DOWN read returned rc −5 (an error code; no service-processor log line in the smoke's ring) | recorded |
| host kernel log before | 666 "Error Event" lines in the buffer at 17:26 PST (`raw/logs/kernlog-before.txt`) | recorded |
| smoke (no write) | PASS: launch rc 0, 7 kernel records, 118 complete samples, no PMIC fields in any line, clocks 600 / 700 / 800 MHz (the ring: idle at "Freq 600 MNN 520", then "Power throttle up" to 700 and 800 MHz, MNN 570 and 620), board at most 35.67 W, die 46–48 °C, high-water latch at most 51 °C | PASS |
| the maintainer's newest posts | none since 14:00 PST in `#community-lab` (4 messages) or in the direct messages (none), read 16:04:26 PST, read-only, masked, stdout only | PASS |

**GO**, recorded in this commit before the first write. The session started at 17:26:59 PST and runs arm B's first two
passes at the card's own settings; by amendment A2 it writes nothing until the file `GO` exists in its run directory,
created after this commit is pushed.

## Set log, activation, final handoff (filled from `raw/gov.jsonl`, `raw/end.json`, `raw/watchdog.log`)

| time (PST, Sun 1 Nov 2026) | event | read-back (the two RAM GETs) |
|---|---|---|
| 17:27:01.303 | the session's original read, card lock held since 17:26:59 | TDP **65** W, threshold **65** °C, `low_power`, 600 MHz; module uptime 6 d 3 h 14 m |
| 17:27:01–17:35:30 | arm B passes 1–2 at the card's own settings (23 of 24 launches; one gate not reached) | — |
| 17:28:42 | `GO` created on the host, after the GO commit `724a5473` was pushed (17:28:33) | — |
| 17:35:34.965 | deadline watchdog armed, pid 399540, deadline 18:50:34 | — |
| 17:35:34.974 → .991 | **set** `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 0 -u 5000`, rc 0 | 17:35:34.999: TDP **0** W, threshold **65** °C |
| 17:35:34–17:54:32 | arm A passes 1–3 at the pin (32 of 36 launches; four gates not reached); every measurement launch read 600 MHz (the abort never fired) | — |
| 17:55:06 | the 8 s settling rung: its gate was not reached (the preheat to 59 °C, 8 heater launches), so it did not run | — |
| 17:55:10.848 → .863 | **restore** `... -l 65 ...`, rc 0 | 17:55:10.871: TDP **65** W, threshold **65** °C (power-state label `max_power`, the known side effect of the pin) |
| 17:55:15 | the watchdog read `release` and exited: "released by the session, nothing to do" | — |
| 17:55:11–17:55:21 | **the return burst** (544 harts, 4 s): clock **600 → 700 → 800 MHz**; its ring holds 12 "Power throttle up" lines | after it: TDP 65 W, threshold 65 °C, `low_power`, 600 MHz |
| 17:55:21–17:59:21 | arm B pass 3 (12 of 12 launches) | — |
| 17:59:25.679 | **closing read**, then the lock released | TDP **65** W, threshold **65** °C, `low_power`, 600 MHz; module uptime 6 d 3 h 46 m (no service-processor reset) |

- **One field written, twice:** the TDP to 0 and back to 65; the threshold never. Nothing else was sent but the reads
  listed above. The pin lasted 19 min 36 s.
- **Envelope:** the highest board reading of the session was 70.7 W (an arm-B heater launch on 768 harts); the highest
  in a kept measurement launch 58.05 W; no die mean reached 72 °C (launch readings 53–55 °C); no safety stop.
- **Host kernel log:** 22 ET error events in the window, all the known `SP Runtime Error` / `Count 0` syndrome, two per
  management burst between passes, none inside a pass (`raw/kernel-events.txt`).
- **Card time:** 32.44 card-minutes in the session (exit 0, "done"), plus the gate reads and the smoke (under 1 min).
- Activation and acceptance (reset, re-identification, new firmware): **N-A**, nothing was flashed or reset.
  **Outbound OTA: N-A. Automatic fallback: N-A.**

## Final handoff

- **Retained state:** firmware, module and PMIC untouched; the governor at its original **65 W / 65 °C**, read back at
  17:55:10 and again at 17:59:25; the card idle at 600 MHz; no service-processor reset (uptime continuous).
- **Locks and monitors:** the card lock released at the session's end; the owner's collector resumes by itself (it was
  never stopped); the watchdog exited after `release`.
- **Logs and artefacts:** the run directory as `raw/` beside this file (telemetry gzipped; the box's tree path written
  `<tree>`); the vmin-LUT file stays on the host as per-card calibration data.
- **Unresolved risks:** none from the operation. The run's own findings (the arms' operating-point step) are in the
  README.
- **Signoff:** the run agent, Sun 1 Nov 2026, 18:0x PST (02:0x UTC Mon 2 Nov); no independent reviewer.

## Template mapping

| template section | here |
|---|---|
| Identity / authorization | above; live items at gate time |
| Current state | above; the PMIC query table is this run's addition |
| Recovery before risk (G1) | above: no independent path this run may take, a watchdog, restore before risk |
| Candidate and build provenance (G2) | N-A for firmware; the host tools are in this repository |
| Immediate release gate (G4) | above |
| Update record — one attempt | N-A (no update) |
| Activation and acceptance | N-A (no reset, nothing flashed); the return burst stands in for "the governor works afterwards" |
| Outbound OTA / fallback | N-A: **Outbound OTA: N-A. Automatic fallback: N-A** (nothing written to a bank) |
| Final handoff | above |
