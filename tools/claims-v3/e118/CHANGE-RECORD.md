# ET-SOC1 change record — E118, E72's two-clock price on a second card (aifoundry1 card 0)

> **How this record was made.** Drafted at the desk by the workflow's governor-preparation lane (Sun 1 Nov 2026,
> 13:07 PST; corrected after an independent verification at 14:12 PST; no card opened for it). Taken over by E118's
> run agent and committed **with the pre-registration** (`tools/claims-v3/e118/`), before the card claim. Items marked
> **⟨RUN AGENT⟩** are live gates, filled with timestamps at gate time and committed as the GO **before** the one write;
> the set log and the handoff are filled after the session and committed with the data
> (`docs/reports/data/2026-11-01-e118-two-clock-card0/`). Unfilled = **UNKNOWN**, never PASS. Where the session's plan
> differs from the draft (the order, the telemetry profile, the ring dumps, the guard, the launch reading), the
> pre-registration README's departures D1–D10 govern, and this record says so where it matters. This is the **first
> governor move on this card**, and its host has two cards on one driver: read § "Two cards, one CLI" first.

Filled from `templates/change-record.md` of the ET-SoC-1 firmware rebuild / OTA field manual (private). Every gate
carries **PASS / FAIL / UNKNOWN / N-A** with a timestamp and its evidence.

**What this operation is** (runbook § 1): *authorized live observation* plus **one** *non-persistent management
write*, `DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26), 65 → **0** W and back to 65 W, exactly E72's on aifoundry2.
**Lowering is the safe direction.** The threshold is not written; no clock command; no OTA, flash, PMIC command,
reset, driver/PCIe action.

## The question (the kinds page § 11, the final critic's replicates; "E72's second card")

E72 (27 Oct) priced a flipped operand bit on **one** card at two clocks and found the price follows V², not the
clock: 79.18 ± 3.09 fJ at 600 MHz / 0.518 V against 121.27 ± 0.61 at 800 MHz / 0.617 V on aifoundry2 (the registered
V1 PASS; it fails at three of four *matched* leakage slopes, E72's correction). E118 repeats it on a second card,
aifoundry1 card 0: the 600 MHz arm from the TDP-0 pin, its **own** 800 MHz beside it — E60's card-0 rows of 20 Oct
(800 MHz, 603.9 mV, 10 passes, 229 of 230 runs kept: `lq` **102.490 ± 4.418 fJ** per designed flipped bit, board;
rail 91.915 fJ; leakage auto fit 0.327 W/°C; `docs/reports/data/2026-10-20-bitflip-ladder/hl.json`, `reduce.txt`) —
plus a short same-session 800 MHz control, because card 0's firmware on 20 Oct is not on record (E84). This answers
[the kinds page § 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) where it
lists E72's second card as the owner's call; the call was made on 1 Nov.

## Identity / authorization

- **Record ID:** `E118-pin600-a1c0-2026-11-01`. Local stamps PST (UTC−8).
- **Operator / owner / reviewer:** an AI Foundry agent of the Q133 governor workflow on the Intel, over ssh; the
  lab's owner; no independent reviewer of the run (a limitation).
- **Authorization:** the owner's OK of Sun 1 Nov 2026, about 12:30 PST, for E118 as a governor move (static TDP level
  and software threshold only) on aifoundry1 card 0, conditional on reading the firmware maintainer's posted
  guidelines first. **Read in full on 1 Nov, 13:54–14:01 PST** (every post of his in the lab's Discord channel and in
  the owner's direct messages with him, each from its start, and in the lab's other technical channels since 1 Sep;
  258 posts): the field manual and no deviation from its gates (20 Oct); firmware changes stay with him, because
  firmware failures can brick a box (7 Oct); a wedged card or host is recovered by a host soft reboot and then an
  AC-outlet cycle through the lab's power switch (Aug–Sep), which once left a host stuck until someone went to the lab
  (7–8 Oct); known firmware bugs, a thermal loop on a hot card among them. None addresses the governor or forbids
  this operation; a lowered TDP is one RAM byte, not a firmware change (rule 8). **Re-read by E118's run agent on
  1 Nov at 14:48:54–14:48:55 PST**, read-only in the same way, for anything posted since: no post of his in either
  place that day (the direct-message thread's newest message is of 27 Oct), so the reading above is current at the
  claim. The field manual's `AGENTS.md`, hosts-and-recovery guide, runbook and change-record template were read by the
  run agent the same afternoon.
- **Allowed:** live observation [x] · **one volatile write of card 0's static TDP level to 0 W, and its restore [x]**
  · anything on card 1 [ ] · OTA [ ] · resets [ ] · host reboot [ ] · driver/PCI [ ] (a module unload on this host
  takes both cards) · AC cycle [ ] · SPI [ ] · PMIC write [ ] · PMIC firmware-management or slot query [ ] · clock
  command [ ] · threshold write [ ] · `--reset-ms` [ ] (not used, as in E72).
- **Host:** `aifoundry1`. **Live, 14:50:39 PST (PASS):** up 6 d 0 h 48 m (booted about 26 Oct 15:02 PDT), the
  driver module `et_soc1` loaded with a use count of 0; the run's `et-lab-manifest` is saved with every pass.
- **Card 0, expected** (E84's committed identity reads, 31 Oct 2026 15:42:00 PDT,
  `docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/ident/`): PCI `0000:01:00.0`, device 0, `/dev/et0_mgmt`;
  release **1.4.0**, BL1 **0.22.0**, BL2 **0.22.0**, PMIC **1.6.1**, minions **0.25.1**; module uptime then 5 d 0 h
  40 m (the service processor up since about 26 Oct 15:02 PDT, the host's boot).
- **Firmware identities: by continuity, not re-queried.** The revisions query E84 used is a PMIC command at
  et-platform `836a4ab`: its handler writes the PMIC's firmware-management command register twice, `ACTIVE_SLOT` then
  `VERSION` (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974, 2531-2557, 2581-2600`), so it is not
  sent again. Card 0's module uptime (`DM_CMD_GET_MODULE_UPTIME`, service-processor RAM,
  `thermal_pwr_mgmt.c:1451-1455`) must show no reset since before 15:42 PDT on 31 Oct; an image takes effect only
  through a reset, so an unbroken uptime carries E84's identity; a shorter uptime is a **NO-GO**. **Live, 14:50:39.729
  PST (PASS):** `ettelem-e118 uptime` 6 d 0 h 49 m = 8,689 min, against E84's 7,240 min plus the 1,448.7 min since
  its read = 8,688.7 (minute resolution): no service-processor reset since E84's read, so card 0 runs the image E84
  identified (release 1.4.0, BL1/BL2 0.22.0, PMIC 1.6.1, minions 0.25.1). `ettelem-e118` opened `/dev/et0_mgmt` at
  PCI `0000:01:00.0` (its device-layer banner, checked in code).
- **Ordering:** after Q133's E114 (card 0) **and** E112 (card 1) have both ended — never two sessions on aifoundry1.
  Desk reading 13:00:10 PST: card 1 busy with our own E112 block (started about 12:55); card 0 free.

## Two cards, one CLI — the coordination this card needs and aifoundry2 did not

- **The stock `dev_mngt_service` opens both cards' management nodes even when `-n 0` selects one** (E84's identity
  reads say so and held both locks for their one firmware read). So **every** `dev_mngt_service` call in E118 —
  `GET_VMIN_LUT`, the two RAM GETs if read that way, the set, the restore, the watchdog's restore — runs with **both**
  `/run/lock/etsoc-shire0.lock` and `/run/lock/etsoc-shire1.lock` held non-blocking for that one call, card 1 idle
  (`et-who` lines for `/dev/et1_*` and `lock:etsoc-shire1.lock` empty; no CI job; no other user's process), and a
  refusal if either lock is taken. `ettelem` opens one card and needs card 0's lock only (E84).
- **The dashboard collector** runs here too (`live-collector.py`, the same sha256 `58e7dc1b9f755be3…` as aifoundry2's,
  13:00:10 PST): it reads each card with `ettelem temp --if-free` (two GETs, neither reaching the PMIC) and opens
  nothing on a card whose lock is held. Holding both locks during a CLI call keeps it off both nodes; between calls it
  may read either card's temperature (a read).
- **lib.sh** refuses aifoundry1 without `V3_DEVICE`; run with `V3_DEVICE=0` / `ET_DEVICES=0`. The host's lab tree is
  an rsynced copy with no git: sync the run's files in, build with `--clean-first`, `nice -j4`, into a build dir no
  other block uses; keep disk small (one pool with the system).
- **This card's third limit:** its PMIC's 75 W over-power alarm drops it to a 300 MHz safe state (E84, fp32 random
  data at 800 MHz, 72–75 W on the board; 177 events, the card stayed up). At the 600 MHz pin the ladder draws about
  half its 800 MHz power (E60's card-0 rungs at 800 MHz: `lq_h0` 45.2 W, `lq_h2` 47.2 W, `lq_h8` 50.9 W, p80,
  `hl.json`), so the alarm is far away; a **300 MHz reading while pinned is an abort** (it would mean something other
  than the pin acted). In the 800 MHz control, **no fp32 `randn` heater and no `anchor_randn`**: E60's heater probe on
  this card logged 33 300 MHz episodes, 30 matching the alarm's cycle (E84 correction C6); approach the launch gate
  with `anchor_pi` or `lq_h8`.

## Current state

- **Originals on card 0 by the RAM GETs: must read TDP 65, threshold 65** (E84 read exactly that at 15:42:00 and
  16:06:52 PDT on 31 Oct, with `low_power`, 600 MHz, 519 mV), else NO-GO. **Live, 14:50:39 PST (PASS):**
  `ettelem-e118 config` (the TDP, threshold, power-state and frequency GETs; no voltage GET) read **TDP 65 W,
  threshold 65 °C, `low_power`, 600 MHz**, under card 0's lock (`gov.jsonl` event `original`).
- **Tools (live):** `ettelem-e118` sha256 `a8481df7673891a811d588c60040987de9543411bb4002344256d221ef5afcac`, built
  14:48 PST from `tools/claims-v3/e118/ettelem-e118/` at the pre-registration `28e625c9`; the stock CLI
  `/opt/et/bin/dev_mngt_service`; the sparsity host and kernel E60 ran (`e0fbecce…`, `990807f4…`); the host's shared
  harness byte-identical to the repository (README "Checked before the claim").
- **Exclusivity (live, 14:50:39–14:51:09 PST, PASS):** `et-who` shows no line for `/dev/et0_*`, `/dev/et1_*` or either
  lock file; no other user's device process and no CI job (`Runner.Worker`; the runner's listener is idle); the
  module's use count 0; the dashboard collector running with the same sha256 `58e7dc1b9f755be3` and its lock check
  (it opens nothing on a card whose lock is held); the `#community-lab` claim posted at **14:50:28.709 PST**, message
  `1566585247326535741` ("using aifoundry1 card 0 for 1 h, until ~15:50 PST"), after E114 had released card 0
  (14:40 PST) and finished (its result at 14:49 PST).
- **Kernel log before (whole log since boot, read on the host):** card 0 (`0000:01:00.0`) lines 714, of which
  `Error Event Detected` 701 (the last at host uptime 520,656 s, about 14:40 PST, during E114), `Tried to open same
  device` 0; AER lines 21 (whole log).
- **SP trace ring before the pin:** 8,192 bytes, sha256 `4df35ccf1b0f3612647e435cfa63d43283722908c1a040227d9c20e1255ec630`,
  14:50:39.774 PST (read only, card 0's lock).
- **vmin-LUT floor:** `DM_CMD_GET_VMIN_LUT` (both locks held; a copy from service-processor RAM,
  `driver/flashfs.c:2073`), parsed **in code** from the binary file; the floor must be **600 MHz**, else NO-GO.
  **Live, 14:50:39 PST (PASS):** three non-zero minion points, **600, 700, 800 MHz**, floor 600 (the file's digest is
  in `gov.jsonl`; only the frequencies are published, never the per-card voltage calibration).
- Bank / boot counters: UNKNOWN (deliberately) / N-A. PMIC slots: not read (a PMIC command).

### What each planned query asks of the PMIC (et-platform `836a4ab`; corrected after verification)

- **No PMIC access:** the TDP, threshold and power-state GETs, `GET_MODULE_POWER`, `GET_MODULE_UPTIME`, `GET_SP_STATS`
  (RAM: `thermal_pwr_mgmt.c:984-988`, `:1451-1455`; `services/performance.c:420-466`), `GET_MODULE_CURRENT_TEMPERATURE`
  (on-die PVT, `thermal_pwr_mgmt.c:732-773`), `GET_ASIC_FREQUENCIES` (PLL registers, `services/perf_mgmt.c:276-`),
  `GET_VMIN_LUT` (RAM copy).
- **PMIC voltage-register reads, no write:** `GET_ASIC_VOLTAGE` reads VDDQLP and VDDQ from the PMIC besides its PVT
  values (`thermal_pwr_mgmt.c:1212-1216` → `pmic_get_voltage` → `get_pmic_reg`, `pmic_controller.c:1473-1500`), sent
  by **`ettelem config`** and **every `ettelem sample` sample**; `GET_MODULE_VOLTAGE`, nine such reads
  (`thermal_pwr_mgmt.c:1010-1120`), sent by every `ettelem sample` sample.
- **A PMIC command, not sent:** `GET_MODULE_FIRMWARE_REVISIONS` (above).
- **Telemetry profile: the no-PMIC-read profile** (README D1; no ruling that the stock reads are allowed was recorded
  before the claim, so the default holds). The workflow's brief says "no PMIC read"; the lab's
  standing rule says "no PMIC commands except the samplers' statistics reset"; the stock samplers make the register
  reads above on every call, as every lab run since September has.
  - **Default, the no-PMIC-read profile:** originals and read-backs by the two RAM GETs; a 10 Hz sampler built with
    `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` off. **For E118 it moves the voltage source**: E60's and E72's reducer
    (`tools/claims-v3/hl/reduce_hl.py:98`) reads the minion voltage from `die_mv` (the PVT value `GET_ASIC_VOLTAGE`
    returns), uses it to drop runs more than 3 mV from their pass median and to convert prices, and E60's 603.9 mV and
    E84's 519 mV are that source. Without it, both clocks take the SP statistics' `sp.minion_mv`, read in this session
    (the 800 MHz control and the pinned passes), the reducer is re-pointed to it, and V1 and G2 are re-frozen from it
    before the claim, as a dated departure. Only ratios enter V1, so the two sources' offset largely cancels.
  - **The stock profile** (exactly E72's design) only with the orchestrator's recorded ruling that those reads are
    not the forbidden "PMIC read", cited here.
- Omitted in either profile: the revisions query, `SET_STATS_RUN_CONTROL` / `--reset-ms`, trace resets,
  `GET_DEVICE_ERROR_EVENTS`, `GET_FIRMWARE_BOOT_STATUS`, every `MDI_*`, every `SET_*` but the one TDP write, resets,
  firmware-update commands, every PMIC command, and anything addressed to card 1.

## Rule 8 (desk: PASS, build-identity residual named)

At et-platform `836a4ab600e93c3059bb58c898edbc37744cd8d0` (2026-07-17; `device-bootloaders/CMakeLists.txt:4`
declares `project(EsperantoBootLoader VERSION 0.22.0)`), read from the git objects at 12:44 PST: the TDP set is
dispatched at `services/thermal_power_monitor.c:966-971`, handled at `:392-415`, and set at
`services/thermal_pwr_mgmt.c:576-591` — one assignment to `g_pmic_power_reg.module_tdp_level`, a `volatile` struct in
`.data`, service-processor RAM (`:143-144`). The value 0 takes the plain assignment (the only check is `tdp > 75`). No
flash writer is reachable (the six writers are in `driver/flashfs.c`, called from outside it only at `main.c:488`,
`rtos_task/flash_fs.c:121`, `asset_track.c:87`, `asset_track_mgmt.c:39`, `firmware_update.c:752`); no PMIC write on
the path; the set path is byte-identical across the public 0.22.0 line (`ce7297156` → `836a4ab`). **Residual
(narrowed after verification):** no BL2 hash is exposed; this card's image is its own (its PMIC family differs from
aifoundry2's), recorded in the maintainer's field manual as a thermal build on `836a4ab` (the first or second version
of the raw-temperature work). The first version of that patch, posted by the maintainer on 7 Oct, only adds (a new
read command, its handler, one dispatcher case after the set cases, one route) and touches neither set path nor
`thermal_pwr_mgmt.c`; the second version, the boot-counter fix beneath it and the binary itself are unread. It reports
the same BL2 0.22.0 as aifoundry2 and the same governor behaviour (E84 A1). Same footing as E72, on a card where
nothing has been set before.

**The pin and its release** are E72 finding 4, re-read at `836a4ab`: the power-down branch at TDP 0 is true under any
busy load and stops at the LUT floor (`thermal_pwr_mgmt.c:864-926`, `:880`, `:1597`); `POWER_UP` is always allowed
(`:2269`), so writing 65 W back releases it on the next busy pass (measured on aifoundry2, E72; **unmeasured on this
card** until G3 below).

## Restore before risk (G1)

- One RAM byte changes; the artefact is the number 65 and its command (this file, `gov.jsonl`, the watchdog).
- **No independent recovery path this run may take** (a limitation, not a PASS): no PMIC console or probe for this
  fleet, and on this host a driver unload or PCIe action would take **both** cards. The maintainer's posted recovery
  for a wedged card (a host soft reboot, then an AC-outlet cycle through the lab's power switch) is a reset/power
  action outside the owner's governor OK and takes both cards and every user of the host; it is the owner's and the
  maintainer's to take, never this run's. Worst plausible case is E72's: a pin restored by one write. If the restore
  fails or card 0 stops answering: stop, keep the claim, write it up, `notify.py --unblock`, never reset or reboot,
  never touch card 1.
- **Deadline watchdog** armed **before** the set: `release` file or **75 min**, then `flock -w 120` on **both**
  locks, write 65 W to card 0 (`-n 0`, `timeout 20`, `-u 5000`), read card 0's TDP GET back, log. One value; never
  resets, never raises, never addresses card 1.
- SPI / PMIC backups: N-A.

## Candidate and build provenance

N-A (no image). Host-side tools in the public repo, pushed before the claim: E72's `gov_e72.py` adapted for this
host (`NODE 0`, **both** lock paths taken for every CLI call, the identity read cut to uptime, the LUT floor parsed in
code, a ring dump after the return burst), E60's `hl/block.sh` under `V3_DEVICE=0` (and, in the default profile, the
sampler's two voltage GETs off and `reduce_hl.py` on `sp.minion_mv`), `predict_e118.py`, `predictions.json`, this
record, the README. **Operands:** checked byte for byte against E60's committed card-0 list `gen-a1.sha256` (it
contains every tile of `gen.sha256` that E72 checked, plus the `xnz_` sources), so the 600 MHz rungs are the bytes
card 0 ran at 800 MHz.

## Immediate release gate (G4) — the plan

- **Exact commands** (both locks held for each; `LD_LIBRARY_PATH=/opt/et/lib`; each in `timeout 20`, then card 0's
  two RAM GETs): `dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l 0 -u 5000`, and the same with
  `-l 65`. Code bounds: only the literal values 0 and 65; any threshold drift is a stop.
- **Order (as pre-registered, README "Protocol"; the 800 MHz control moved after the restore, D6):** gate reads
  (uptime, originals, LUT floor, `et-who` both cards, the SP ring before the pin) → the GO committed → watchdog →
  **set 0 W**, read back (TDP 0, threshold 65) → pinned smoke (every sample 600 MHz) → launch-reading probe (D7) →
  **600 MHz passes**: E72's 20 items (`anchor_pi`, `anchor_ones`, `anchor_zeros`, `anchor_randn`,
  `lq_h{0,1,2,4,8,12,16,23}`, `lb_h{0,1,2,4,8,12,16,23}`), 5 planned, 3 the minimum, cut order E72's → SP ring dump →
  **restore 65 W**, read back, `release` → **return burst** (block.sh's smoke, `anchor_pi`, `lq_h8`) and an **SP ring
  dump after it** → **800 MHz control at the card's own 65 W**: `anchor_pi`, `lq_h0`, `lq_h2`, `lq_h8`, 3 passes
  planned (2 the minimum), 4 s runs, the `pi` heater (D8), a 300 MHz sample voids the run → closing reads (config,
  uptime, `et-who` both cards, kernel-log kinds).
- **Abort — the envelope's words, as written, enforced by `guard_e118.py` on every sample (D9):** **any single 10 Hz
  board reading ≥ 85 W** (not expected: the control
  stays near 45–51 W and the pinned passes lower, so E69's "3 consecutive samples" form is not needed); die ≥ 72 °C on
  any reading (card 0 ran 52–53 °C under 8 minutes of sgemm bursts after its fan swap, AGENT.md § 4); a 300 MHz
  reading while pinned; any clock other than 600 MHz in a pinned run (voids it, E60's gate); a DM rc ≠ 0 or read-back
  mismatch; a management timeout; any activity appearing on card 1; a kernel-log line other than the known syndromes.
- **Card time:** gates 5 min, control about 9 min, pin and passes about 23 min (E72's 22.6), restore and return 3 min,
  closing 2 min: **about 45 min**; the claim `using aifoundry1 card 0 for 1 h, until ~HH:MM PST`.
- **GO / NO-GO: GO**, Sun 1 Nov 2026 14:5x PST, by E118's run agent: every live item above read as expected (G0
  identity by continuity, originals 65 W / 65 °C, LUT floor 600 MHz, exclusivity, the claim posted), the telemetry
  profile is settled (no-PMIC-read), rule 8 PASS at the version-matched source with its named residual, the envelope
  and the stop rules are in code (`guard_e118.py`, `HL_MAX_C=72`, `gov_e118.py`'s allowlist of two commands and two
  values). Recorded in this commit, made **before** the one write. Card-time cap: 45 minutes from the first gate read
  (14:50:39 PST), so every card step ends by **15:35:39 PST**.

## Frozen predictions (the run's predict tool freezes them before the claim)

Frozen by `predict_e118.py` into `tools/claims-v3/e118/predictions.json` before the claim, in the no-PMIC-read
profile's source on **both** sides: V₈₀₀ = **0.60387 V** (`sp.minion_mv[0]` over E60's card-0 kept runs; the PVT
source gives 0.60387 too, 0.0015 mV apart, the same 229 runs kept), V₆₀₀ = **0.519 V** expected (card 0 read 519 mV
at 600 MHz in both sources on 31 Oct, E84); (V₆₀₀/V₈₀₀)² = **0.73867**; × 600/800 = **0.55400**. So the re-freeze
leaves the stock numbers unchanged to the third decimal; the README's table is the full registered set (V1m, V1,
V2–V6, C1, G1–G3).

| | what | predicted (stock profile) | band | PASS if |
|---|---|---:|---|---|
| **V1** | `lq` h2→h8, board, fJ per designed flipped bit, 600 MHz | **75.71** | 68.14–83.28 | inside, and outside the alternative's band |
| | *the alternative (energy scaled with f too)* | *56.78* | *51.10–62.46* | *the hypothesis V1 refutes* |
| **V1m** | the same at **matched** leakage slopes on both sides (E72's correction: the primary form) | **77.605** at 0 W/°C; **73.939** at 0.3273 W/°C | ±10 % | inside at both: PASS; one: PARTIAL |
| **C1** | the 800 MHz control against E60's 20 Oct rows | `lq_h2`, `lq_h8` over `lq_h0` within ±10 % of E60's 1.912 W and 5.672 W | — | inside (else the comparison is against today's control, said so) |
| **G1** | the pin | 600 MHz in **100 %** of samples; **zero** `Power throttle up` while TDP 0 is set | — | exactly that |
| **G2** | the pinned voltage (`sp.minion_mv[0]`) | 0.519 V | 0.516–0.522 | inside |
| **G3** | the restore | 65 W / 65 °C read back; the return burst reaches ≥ 700 MHz **with ≥ 1 `Power throttle up` in the ring dump** | — | both halves (E72 left the second UNMEASURED) |

E60's card-0 board SE is 4.3 % (against 0.5 % on aifoundry2), so V1's band is wide but the two hypotheses' bands do
not overlap.

## Set log, activation, final handoff

The machine-readable record is `session/gov.jsonl` in the data directory
(`docs/reports/data/2026-11-01-e118-two-clock-card0/`): one line per event with argv, rc and millisecond timestamps;
`session/steps.jsonl` and `session/session.log` order the session; `session/guard.jsonl` is the envelope guard's log.
Filled from them after the session (all times PST, UTC−8):

| Item | Value |
|---|---|
| Originals, read before any set (card 0's lock) | **14:50:39.730** — TDP **65 W**, threshold **65 °C**, `low_power`, 600 MHz (`ettelem-e118 config`: the TDP, threshold, power-state and frequency GETs) |
| vmin-LUT floor (both locks) | **600 MHz**, points 600 / 700 / 800, parsed in code at 14:50:39.730 (file digest `5bdceb58…` in `gov.jsonl`; the calibration bytes are not copied) |
| SP ring before the pin | 14:50:39.774, 8,192 bytes, `4df35ccf…` |
| The GO | commit `f37fa285`, pushed 14:51:51 PST, before the write |
| Watchdog armed (before the set) | **14:52:00.933**, 4,500 s deadline, detached |
| Sets sent (both locks held for each) | **two**: `-l 0` at **14:52:00.933** (read back TDP **0**, threshold 65 °C, `low_power`, 600 MHz; the read opened `/dev/et0_mgmt` at `0000:01:00.0`) and `-l 65` at **15:12:37.217** (read back TDP **65**, threshold **65 °C**) |
| Command exit statuses | both **rc 0**; `gov_e118.py` could send only these two values of this one command |
| Read-back mismatches | **0**; the threshold read 65 °C at every read |
| Restore | 15:12:37.241, **`ok: true`**; `release` written; the watchdog logged *"released by the session, nothing to do"* at 15:12:41 and exited |
| Read-back after the restore | 15:12:37.279: TDP 65 W, 65 °C, 600 MHz, power state `max_power`. *The power state is not a knob: the firmware re-derives it each service-processor pass from the SoC power against the TDP (`thermal_pwr_mgmt.c` `get_power_state`, called at `:859`), and this read came 38 ms after the write, before the next pass, so it still showed the pinned era's state; the closing read below shows it re-derived* |
| Return burst (normal stepping) | 15:12:38–15:13:01, `anchor_pi`, `xin_h16`, `lq_h8`, `anchor_pi` (block.sh's smoke): clocks **600 → 700 → 800 MHz** (117 / 2 / 97 samples) |
| SP ring after the pinned passes / after the burst | 15:12:37.182 and 15:13:01.483; between the dump before the pin and the dump after the pinned passes **zero** new entries (covered); between that dump and the one after the burst exactly **one**, `Power throttle up event, current pwr 23370  tdp level: 65000` |
| The 800 MHz control | 15:13:02–15:17:23, three passes at the card's own 65 W / 65 °C, the `pi` heater, launch at 57 °C after 58 °C |
| Closing read-back | **15:17:33.805**: TDP **65 W**, threshold **65 °C**, `low_power`, 600 MHz — **equal to the originals** in every field read |
| Module uptime | 8,689 min at the gates, 8,711 min after the restore, 8,716 min at the close: no service-processor reset at any point |
| Card 1 | untouched: no `et-who` line for `/dev/et1_*` or its lock before (14:50:39) or after (15:17:51); our tools opened card 0 only, except the three stock-CLI calls (LUT read, set, restore), each with both locks held |
| Kernel log, card 0 | `Error Event Detected` **701 before and 701 after**; `Tried to open same device` 0 and 0; AER lines 21 and 21. By wall-clock window (dmesg stamps): 120 such lines fell inside the previous session on this card (14:18:10–14:39:48), **0** inside E118 (14:50:39–15:17:34) |
| Envelope | never approached: highest single board reading **52.75 W** (the 800 MHz control), highest die reading **61 °C**; the guard tripped **0** times; no 300 MHz reading |
| Telemetry profile | **no-PMIC-read** throughout (`ettelem-e118`, sha256 `a8481df7…`): no `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, statistics reset or revisions query was sent |
| Card time | first card read 14:50:39, last 15:17:33.8: **26.9 card-minutes** of the 45 allowed |

Activation and outbound OTA: **N-A** (no image, no reset). **Final handoff:** card 0 at TDP 65 W / 65 °C, its own
governor stepping normally (shown by the burst and by the control's 800 MHz runs), no process of ours on the host, the
watchdog gone, card 1 untouched. The claim's release edit is recorded in the data README.

## Corrections after verification (Sun 1 Nov 2026, desk only, nothing run)

| # | What the draft said | What it says now |
|---|---|---|
| 1 | The maintainer's guidelines are the manual and a requirement not to deviate from its gates | Read in full (258 posts): also firmware kept with him, the posted recovery procedure and its 7 Oct failure, known firmware bugs. The verdict, re-issued, stays GO-READY |
| 2 | The revisions read among the CLI calls; card 0's identity re-read fresh | Not sent (a PMIC command); identity by continuity from E84's read and an unbroken uptime; a list of what each planned query asks of the PMIC, the profile choice, and what the default profile changes for E118's voltages |
| 3 | Abort at board ≥ 85 W on 3 consecutive samples | Any single reading ≥ 85 W, the envelope as written |
| 4 | Residual: the thermal build's additions are in no source the lab holds | Narrowed by the patch's first version, read 1 Nov |
| 5 | Rule 8 "exactly E117's record" | Stated here in full, since E117 may never run |
| 6 | Timestamps "13:xx PST" | The real times of each desk read |
