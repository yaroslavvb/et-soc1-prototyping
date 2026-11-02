# ET-SOC1 change record — E120, E77 redesigned: the rail at one temperature, at two rail voltages (aifoundry2)

Filled from `templates/change-record.md` of the ET-SoC-1 firmware rebuild / OTA field manual (private; kept with the
operator's notes and on the lab boxes, not in this repository). Every gate carries **PASS / FAIL / UNKNOWN / N-A** with
its time and evidence; **UNKNOWN is never PASS**. The desk gates follow E77's record of the same operation on the same
card today ([E77's CHANGE-RECORD.md](../2026-11-01-e77-rail-one-temperature/CHANGE-RECORD.md), drafted by the Q133 desk
lane and verified), each re-checked by this run's agent; the live gates are filled at gate time, timestamped, and
committed as the GO **before** the first write. Local stamps are PST (UTC−8).

**What this operation is** (the manual's runbook § 1): *authorized live observation* plus **one** *non-persistent
management write*, `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26), 65 → **0** W and back to 65 W — the TDP-0 pin E72 and E77
used on this card (27 Oct; today 17:35–17:55 PST). **Lowering is the safe direction.** The threshold is not written. It
is not an OTA, build, flash, PMIC command, reset, driver or PCIe action, and **not a clock command**
(`DM_CMD_SET_FREQUENCY` is never sent).

## Identity / authorization

- **Record ID:** `E120-twovolt-2026-11-01`. **Operator:** an AI Foundry agent of the Q134 workflow, on the lab's owner's
  behalf, over ssh. **Reviewer:** none independent of the run (a limitation). **Hardware owner:** the lab's owner.
  **Recovery operator:** the owner and the lab's firmware maintainer, never this run (G1).
- **Authorization, and its scope:** the owner's OK of Sun 1 Nov 2026, about 12:30 PST, for E77 as a governor move (the
  static TDP level and the software threshold only), conditional on reading the firmware maintainer's posted guidelines
  first; and his ask of about 19:05 PST the same day to confirm results while the cards are available, under which the
  workflow named E120 as E77 redesigned: **the same operation on the same card**, TDP 65 → 0 → 65 W on aifoundry2.
  Nothing beyond that write is authorized or sent. **The maintainer's guidelines:** his posts were read in full by the
  Q133 desk lane (13:54–14:01 PST, 258 posts, paraphrased privately): the field manual and no deviation from its gates
  (20 Oct); firmware changes stay with him, because firmware failures can brick a box (7 Oct); a wedged card or host is
  recovered by a host soft reboot and then an AC-outlet cycle through the lab's power switch (Aug–Sep), which once left
  this host stuck until someone went to the lab (7–8 Oct); known firmware bugs, a thermal loop on a hot card among them.
  None addresses the governor or forbids this operation; a lowered TDP is one RAM byte, not a firmware change (rule 8).
  **This run's agent** read that paraphrase, then the manual's four files itself in full (`AGENTS.md`,
  `docs/hosts-and-recovery.md`, `docs/runbook.md`, `templates/change-record.md`; about 20:29 PST), and checked for newer
  posts of the maintainer since 14:17 PST in `#community-lab` and in the owner's direct messages at 20:30:50 PST: none.
  ⟨RUN: re-checked within minutes of the claim: see "Live gates"⟩
- **Allowed:** offline build [ ] · live observation [x] · **one volatile write of the static TDP level to 0 W and its
  restore to 65 W [x]** · OTA [ ] · SoC reset [ ] · PMIC reset [ ] · driver/PCI changes [ ] · AC cycle [ ] · external
  SPI [ ] · PMIC write [ ] · PMIC firmware-management or slot query [ ] · clock command [ ] · threshold write [ ] ·
  statistics reset [ ] (allowed in general by the owner's ruling of 31 October 2026; not used, so that the rails stay the
  PMIC's own running average, the ledger's footing, and the governor's average is not restarted).
  **OTP/fuses/keys/security policy: prohibited, untouched.**
- **Approved window:** one session on aifoundry2, starting after Q134's E119 released the card (its claim edited
  "— released" at 20:12:15 PST; `et-who` free at 20:20:50 and 20:40:53 PST) and no later than 22:30 PST, ending (restore
  included) by 23:30 PST; at most 50 card-minutes. Affected users: anyone wanting aifoundry2 in the window, told by the
  day's one `#community-lab` post.
- **Host / card / node:** `aifoundry2`, one card, `0000:02:00.0` ↔ device 0 ↔ `/dev/et0_mgmt`, `/dev/et0_ops`.
  ⟨RUN: re-read from sysfs, `uptime`, `et-who`⟩. Other cards sharing the driver or root port: none (one card).
- **Firmware identities: by continuity, not re-queried.** Expected release 1.4.0, BL1/BL2 0.22.0, PMIC 1.5.0, minions
  0.25.1: E69's revisions read, 13:56:26 PDT on 27 Oct, with the service processor up since the host's 26 Oct boot. The
  revisions query is **not** sent: at et-platform `836a4ab` it writes the PMIC's firmware-management command register
  twice (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974, 2531-2557, 2581-2600`), a PMIC command.
  ⟨RUN: `DM_CMD_GET_MODULE_UPTIME` (service-processor RAM) must exceed the minutes since 13:56:26 PDT on 27 Oct; an image
  takes effect only through a reset, so an unbroken uptime carries the identity. Shorter is **NO-GO**⟩. Host uptime at
  20:40:53 PST: 6 d 6 h 27 m (the 26 Oct boot).
- **Ordering on the card:** after E119 (released 20:11:16 PST). E117 did not run. Never two sessions on the card.
- **Locks / monitors / races:** the owner's dashboard collector (`live-collector.py`, 3 processes at 20:40:53 PST)
  reads temperatures with `ettelem temp --if-free` (two GETs, neither reaching the PMIC) and opens nothing while
  `/run/lock/etsoc-shire0.lock` is held. **One runner holds the lock for the whole session**; the gate reads and the
  smoke take it for their own short holds before. The management node allows one opener, so the sampler is stopped for
  every set and every query, and the governor is never polled during a pass. ⟨RUN: the collector's hash at gate time⟩

## Current state

- ⟨RUN⟩ kernel, module srcversion and hash, tool hashes (`gates.json`, `session.json`). **The tools are E77's own
  binaries, checked by SHA-256 before anything opens the card** (20:40:53 PST: heater `7adadf4f1ce331cc…`, kernel
  `990807f483cd57aa…`, `ettelem-e77` `21e7bf77e631eb7e…`, all equal to E77's `session.json`; `ettelem-e77 profile`
  reads `no-PMIC-read`). The runner refuses to start otherwise.
- **The originals by the two RAM GETs** (`DM_CMD_GET_MODULE_STATIC_TDP_LEVEL`, `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS`,
  through `ettelem-e77 config`): **must read 65 and 65** (the boot defaults, `thermal_pwr_mgmt.c:1672-1676`), else NO-GO.
  E119 read 65 W / 65 °C at 20:11:16 PST. ⟨RUN⟩
- **vmin-LUT floor:** `DM_CMD_GET_VMIN_LUT` (a copy from the service processor's RAM, `driver/flashfs.c:2073`), parsed
  in code from the file the vendor tool writes; the floor must be **600 MHz**, else NO-GO (E72 and E77 read
  600 / 700 / 800 on this card). ⟨RUN⟩
- Bank / boot counters: UNKNOWN, deliberately (they need flash access) / N-A. PMIC slots: not read (a PMIC command).

### What each planned query asks of the card (et-platform `836a4ab`)

- **Sent, no PMIC access:** `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`,
  `GET_ASIC_FREQUENCIES`, the TDP, threshold and power-state GETs, `GET_MODULE_UPTIME`, `GET_VMIN_LUT`,
  `GET_MODULE_RESIDENCY_THROTTLE_STATES` **for raw states 1, 2 and 3 only** (POWER_UP, POWER_DOWN, POWER_SAFE on BL2
  0.22.0, `device_mgmt_api_spec.h:280-285`), and the ring dump, which is no DM command: two driver ioctls copying the
  service processor's trace region. **Raw state 4 is never asked:** it is no state on 0.22.0, and each read logged two
  ERROR lines on the service processor and pushed two `SP Runtime Error` events to the host (E77 F1, all 22 of E77's).
- **Not sent (the no-PMIC-read profile):** `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` (PMIC voltage-register reads),
  which the stock samplers send; `ettelem-e77` is built without them and without any set.
- **Also omitted:** the revisions query, `SET_STATS_RUN_CONTROL`, trace resets, `GET_DEVICE_ERROR_EVENTS`,
  `GET_FIRMWARE_BOOT_STATUS`, every `MDI_*`, every `SET_*` but the one TDP write, resets, firmware-update commands, every
  PMIC command.
- **Classification (runbook § 1):** the ring dump is an *active diagnostic* in the manual's table (trace extraction hung
  old firmware on this host, 7 Oct). On this card's thermal-v2 build it has run in every governor and kinds session since
  October (E77 took eleven today, E119 more tonight) without a fault; it is kept, as E77 kept it, because the return
  check needs it.

## Rule 8 — no incidental board-data change (desk: PASS at the version-matched source; build-identity residual named)

Unchanged from E77's record, re-read by this run's agent: at et-platform `836a4ab600e93c3059bb58c898edbc37744cd8d0`
(BL2 0.22.0), the TDP set is dispatched at `services/thermal_power_monitor.c:966-971`, handled at `:392-415`, and set at
`services/thermal_pwr_mgmt.c:576-591` (refuse `tdp > 75`, else one `Log_Write` and the assignment to a `volatile`
struct in `.data`, service-processor RAM, `thermal_pwr_mgmt.c:143-144`). The value 0 takes the plain assignment. No
flash writer is reachable from the set path (the six writers are in `driver/flashfs.c`, called from outside it only at
boot, the boot count, the VMIN-LUT set, the part number and the OTA config copy); no PMIC write is on it. The set path is
byte-identical across the public 0.22.0 line. **Residual:** no BL2 hash is exposed, and the card runs a thermal build
flashed in October that adds to `836a4ab`; the first version of the raw-temperature patch the maintainer posted on 7 Oct
touches neither set path, and its second version, the boot-counter fix beneath it and the binary are unread. Same
footing as E72 and E77 on this card (zero read-back mismatches in both). **Read as byte-exact provenance, rule 8 would be
UNKNOWN and this run NO-GO; the owner's operational definition (the source at the revision matching the reported
versions) and E69/E72/E77's accepted standard make it PASS.** Stated, not hidden.

**What the pin does at 0.22.0:** `check_power_throttle_conditions` (`thermal_pwr_mgmt.c:864-926`) compares the average
power with the TDP and no guardband; at 0 the power-down branch is true under any load, gated on the clock being above
the LUT floor, so the clock walks to 600 MHz and stops; it acts only while the master minion is busy (`:880`); writing
65 W back releases it on the next busy pass — measured on this card today: 600 → 700 → 800 MHz within 4.1 s of E77's
restore, two fresh throttle-ups in the ring.

## Recovery established BEFORE risk (G1)

- **Exact independent recovery path:** none this run may take (a limitation, not a PASS). The worst plausible case is
  E72's and E77's: a pin restored by one write. No card reset, no retry chain. The maintainer's posted recovery for a
  wedged card (a host soft reboot, then an AC-outlet cycle through the lab's power switch) is a reset and power action
  outside the owner's governor OK, takes the host from every user, and once left this host stuck at its BIOS screen until
  an on-site visit (7–8 Oct): it is the owner's and the maintainer's to take, never this run's. If the restore fails or
  the card stops answering: stop, keep the claim, write it up, alert the owner (`notify.py --unblock`), never reset or
  reboot.
- **What changes:** one service-processor RAM byte; the artefact to restore is the number 65 and its command.
- **Deadline watchdog,** armed **before** the set: if the session has not written `release` within 75 min (or by
  23:25 PST, if sooner), it takes `flock -w 120` on the card lock, writes 65 W (`timeout 20`, `-u 5000`), reads the GETs
  back and logs. One value; it never resets and never raises.
- SPI / PMIC backups, rollback artefact, bank selection, automatic fallback, power-loss plan: **N-A** (nothing is
  written to flash, the PMIC or any bank; a power loss leaves the boot default, 65 W).
- **Outage escalation (G1's last item):** none is approved or planned; the run stops instead.

## Candidate and build provenance (G2)

**N-A** for firmware (no image). Host-side tools, all in this repository and pushed before the claim: the runner
`tools/claims-v3/e120/run_e120.py`, its protocol, `predict_e120.py` and `predictions.json`, `reduce_e120.py`,
`e120.sh`, this record and the README; E77's binaries reused unchanged (hashes above). Code bounds: the runner writes
only the literal values 0 and 65, refuses any other value and never sends a threshold write.

## Preserve the next update (G3)

**N-A** (no image changes). What G3 asks of a governor move in E69's mapping — that the governor be shown to work
afterwards — is the return burst below, now checked on ring entries newer than the dump before it.

## Immediate release gate (G4) — the plan

- **Exact commands:** `dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 0 -u 5000` and the same with
  `-l 65`, under `LD_LIBRARY_PATH=/opt/et/lib`, each in `timeout 20` and followed by the two RAM GETs.
- **The ladder** (fp32 randn; per-shire hart counts; 4 s launches; the median of the 10 Hz board samples and the raw
  rails over [t1 − 1.5, t1]): arm A (TDP 0, 600 MHz) 992 / 736 / 512 / 256 harts; arm B (own governor, 800 MHz) 416 /
  288 / 160 / 32 harts; five passes per arm of two rounds.
- **One temperature:** every launch of both arms passes the same die gate (preheat to 56 °C; launch at ≤ 55 °C once the
  minion rail has settled, ≥ 6 s after the last device process; re-heat under 52 °C).
- **Order:** gate reads (their own hold of the lock) → the smoke → the session: arm B passes 1–2 (no move) → the GO file
  (after the GO commit) → watchdog → **set 0 W**, read back (TDP 0, threshold 65) → arm A passes 1–5 (every measurement
  launch must read 600 MHz throughout, else the session aborts and restores) → the 8 s settling rung → **restore 65 W**,
  read back, `release` → the return burst (one 4 s launch of 416 harts: the clock must reach 800 MHz, and the ring dumped
  after it must hold a throttle-up entry newer than the previous dump) → arm B passes 3–5 → closing reads (the two RAM
  GETs, uptime).
- **Abort — the envelope's words, as written:** **any single 10 Hz board reading ≥ 85 W** (not expected: E77's highest
  was 70.7 W, an arm-B heater; its kept launches reached 58.05 W, and E120's top rungs are smaller than E77's); die ≥
  72 °C on any reading (the die mean; the high-water latch at 80 °C); any clock other than 600 MHz in an arm-A launch; a
  DM rc ≠ 0 or a read-back mismatch; a management timeout; a device process outliving `timeout 10`. Every abort restores
  in the session's `finally`.
- **Card time:** 80 launches plus gates: about 38 card-minutes estimated, at most 50 (the session cuts at 46); the post's
  clause `for 1 h`.
- **GO / NO-GO:** desk **GO-READY** (as E77's). ⟨RUN: GO only when every live item reads as required, recorded in a
  commit made before the set⟩

## Live gates (filled at gate time)

⟨RUN⟩

## Set log, activation, final handoff

⟨RUN: as E77's record — originals, LUT floor, watchdog armed, both sets with argv/rc/ms timestamps, read-backs, restore,
the return burst and its fresh ring entries, module uptime after, error-event counts before and after, the telemetry
profile used, the post's edits read back. Outbound OTA: **N-A**. Signoff UTC and PST.⟩

## Template mapping

| template section | here |
|---|---|
| Identity / authorization | above; live items at gate time |
| Current state | above, with the query table |
| Recovery before risk (G1) | above: no independent path this run may take, a watchdog, restore before risk |
| Candidate and build provenance (G2) | N-A for firmware; the host tools are in this repository, E77's binaries by hash |
| Immediate release gate (G4) | above |
| Update record — one attempt | N-A (no update) |
| Activation and acceptance | N-A (no reset, nothing flashed); the return burst stands in for "the governor works afterwards" |
| Outbound OTA / fallback | N-A: **Outbound OTA: N-A. Automatic fallback: N-A** (nothing written to a bank) |
| Final handoff | after the run |
