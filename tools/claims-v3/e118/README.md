# E118 — E72's two-clock price on a second card: aifoundry1 card 0 at 600 MHz (static TDP 0) and at its own 800 MHz

*Pre-registered Sun 1 Nov 2026 (week 44), PST, **before the card claim and before any card access** for this
experiment. Request Q133 (the Horace project). Card **aifoundry1 card 0** (PCI `0000:01:00.0`, `/dev/et0_*`). Any
change after this commit goes in "Amendments" at the end, dated, before the data it touches.*

**It answers** [the kinds page's section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 15**, "E72 on a second card, which needs a governor move" (the Horace hub's older item 5), now that the owner
has given the governor OK.

## The question

E72 (27 Oct, aifoundry2) priced a flipped B mantissa bit on **one** card at two clocks — the static TDP level set to
0 W pins the clock at the vmin-LUT floor, 600 MHz — and found the price follows the voltage, not the clock: **79.18 ±
3.09 fJ** at 600 MHz / 0.518 V against **121.27 ± 0.61** at 800 MHz / 0.617 V. The clock-scaling alternative was
excluded at 3.4 SE or more in every reduction; the exponent was bracketed at **1.60–2.92**, not pinned to 2
(`docs/reports/data/2026-10-27-e72-600mhz/README.md`). One card is one card. E118 repeats E72 on **aifoundry1 card
0**: its 600 MHz from the same governor write, its **own** 800 MHz beside it — E60's card-0 rows of 20 Oct (800 MHz,
603.9 mV, 10 passes, `lq` **102.490 ± 4.418 fJ**, `docs/reports/data/2026-10-20-bitflip-ladder/hl.json`) — and a
same-session 800 MHz control, because this card's firmware on 20 Oct is not on record.

The prediction, as in E72: **the price follows V², not the clock.**

## How the clock is set (one governor field; no clock command)

`DM_CMD_SET_MODULE_STATIC_TDP_LEVEL` (26) on card 0, 65 → **0** W, then back to 65 W: exactly E72's write, the safe
direction. At BL2 0.22.0 (et-platform `836a4ab`, `services/thermal_pwr_mgmt.c:864-926`) a TDP of 0 makes the
power-down branch true under any busy load and the power-up branch unreachable, and the down branch stops at the LUT
floor; `POWER_UP` is always allowed (`:2269`), so writing 65 back releases it on the next busy pass (E72: 600 → 700 →
800 MHz in one launch, no reset). **The threshold is never written. No clock, PMIC, firmware, OTA, flash, reset, PCIe
or driver action.** The field manual's gates are in [`CHANGE-RECORD.md`](CHANGE-RECORD.md) (PASS / FAIL / UNKNOWN per
gate; UNKNOWN is never PASS), committed with the data.

**Authorization:** the owner's OK of Sun 1 Nov 2026 (about 12:30 PST) for governor moves — the static TDP level and
the software threshold only — for three named runs, E118 among them, on the condition that the firmware maintainer's
posted guidelines are read first. They were (the change record says what was read and when). None of them addresses
the governor; a TDP write is one service-processor RAM byte, not a firmware change (rule 8, the change record).

## Protocol (E72's, with the departures below)

E60's harness: `block_e118.sh` (= `hl/block.sh` with two lines changed, D1 and D8) → E60's `run_hl.py` unchanged; one
pass = one replicate; 4 s runs on 1,024 minions; `anchor_pi` first and last in every pass, two unrecorded burn-ins,
the rest shuffled on the pass number; the card lock held for the pass; `timeout 10` on every device process; the
10 Hz sampler for the whole pass.

- **The session order:** gate reads → the GO committed → the watchdog armed → **TDP 0** and its read-back → a pinned
  smoke (every sample at 600 MHz, or the pin failed) → the launch-reading probe (D7) → **the 600 MHz passes** → SP
  ring dump → **restore TDP 65** and its read-back → **the return burst** (`anchor_pi`, `lq_h8`; block.sh's smoke at
  the card's own governor) → SP ring dump → **the 800 MHz control** → closing reads.
- **600 MHz items** (E72's registered 20, by name): `anchor_pi, anchor_ones, anchor_zeros, anchor_randn,
  lq_h{0,1,2,4,8,12,16,23}, lb_h{0,1,2,4,8,12,16,23}`. **Passes:** 5 planned, 3 the minimum. **Cut order** if the
  card-time cap would be passed: `lb_h16`, `lb_h12` and `anchor_zeros` out together, then passes, never below 3.
- **800 MHz control** (at the card's own 65 W / 65 °C): `anchor_pi, lq_h0, lq_h2, lq_h8`; 3 passes planned, 2 the
  minimum; **no fp32 `randn` heater and no `anchor_randn`** (D8).
- **Operands:** the files in the host's `build/hl-gen`, checked byte for byte against E60's committed card-0 list
  `docs/reports/data/2026-10-20-bitflip-ladder/gen-a1.sha256` before the claim, so both clocks run the bytes E60 ran.
- **Reduction:** [`reduce_e118.py`](reduce_e118.py) = E60's `reduce_hl.py` unmodified, with `gov_free` forced per half
  (E72's change: `--pinned` for the 600 MHz passes, `--free` for the control; the halves reduced separately) and the
  voltage taken from `sp.minion_mv[0]` (D1). Verdicts at the registered `--leak auto`, as E60 and E72 registered;
  V1m at matched slopes (below).
- **Card time:** at most **45 minutes** from the first gate read, and every card step, restores included, ends by
  **19:00 PST**. `session_e118.sh` starts a pass only if it and everything after it (restore, return burst, two
  control passes, closing reads: an 8-minute reserve) fit inside the cap.

## Departures from E72, each with its reason (all written before any card access)

- **D1 — the no-PMIC-read telemetry profile.** The workflow that runs E118 forbids any PMIC read. At `836a4ab` the
  stock sampler's `DM_CMD_GET_ASIC_VOLTAGE` reads two PMIC voltage registers (`thermal_pwr_mgmt.c:1212-1216`) and
  `DM_CMD_GET_MODULE_VOLTAGE` nine (`:1010-1120`), on every sample, and `ettelem config` sends the first. So every
  read here goes through [`ettelem-e118`](ettelem-e118/ettelem.cpp), `ettelem-dv2` with those two requests removed
  and every write refused (the statistics reset, `loglevel`, `threshold set`); its marker `E118-NO-PMIC-READ` is
  checked before use. The telemetry therefore has no `die_mv`, and E60's reducer reads its minion voltage (the 3 mV
  run gate, the unit conversions, V²) from **`sp.minion_mv[0]`** (the service processor's statistics, a RAM copy).
  On committed data the two sources agree in the reducer's own windows: **603.869 vs 603.867 mV** on E60's card-0
  passes (229 of 230 runs kept in both, the same price to 1e-6) and 517.92 vs 517.92 on E72's
  ([`predict_e118.py`](predict_e118.py) refuses to freeze if they differ by more than 0.5 mV or keep different runs).
  So V1's numbers are the stock profile's to the third decimal; the departure is the label.
- **D2 — identity by continuity.** No firmware-revisions query: at `836a4ab` its handler writes the PMIC's
  firmware-management command register (`services/firmware_update.c:903` → `driver/pmic_controller.c:952-974`). Card
  0's identity is E84's read of 31 Oct 2026 15:42:00 PDT (release 1.4.0, BL1/BL2 0.22.0, PMIC 1.6.1, minions
  0.25.1; module uptime 5 d 0 h 40 m), carried by a module uptime (a RAM read) showing no service-processor reset
  since; a shorter uptime is a NO-GO (`gov_e118.py gates`).
- **D3 — two cards, one CLI.** The stock `dev_mngt_service` opens both cards' management nodes whatever `-n` says, so
  each of its calls here (the vmin-LUT read, the set, the restore, the watchdog's restore) holds **both**
  `etsoc-shire0.lock` and `etsoc-shire1.lock`; `ettelem-e118` opens card 0 only (`ET_DEVICES=0`) under card 0's lock.
  `gov_e118.py` can send only two commands, `DM_CMD_GET_VMIN_LUT` and the TDP set with the literal 0 or 65.
- **D4 — the vmin-LUT floor in code.** E72's text parse found nothing (the CLI writes `dev0_vmin_lut.bin`); here the
  binary is parsed in code (18-byte points, the frequency the first little-endian 16-bit field) and the gate refuses
  unless the floor is 600 MHz. Only the frequencies and the file's digest are kept.
- **D5 — the SP trace ring is dumped** (read only, never reset) before the pin, after the last pinned pass and after
  the return burst, so G1's and G3's log halves are measured (E72 D1/D1b left both UNMEASURED). Events are attributed
  to the pin by difference between dumps (`tools/claims-v3/dv2/sptrace_events.py`); a ring that wrapped between two
  dumps leaves the half UNMEASURED.
- **D6 — the 800 MHz control comes after the restore.** The workflow's order (pin first). The control then also
  shows the release: it needs the card stepping to 800 MHz under load.
- **D7 — the launch reading.** E60's card-0 gate, **launch at 57 °C after 58 °C** (E72 used aifoundry2's 58/59).
  Card 0 is the coolest card (52–53 °C under 8 minutes of sgemm bursts), and at 600 MHz its heater draws far less
  than at 800, so a probe pass of one item at the pinned clock (`e118probe`, not analysed) tries 57/58, then 55/56,
  then 53/54, and the first reached is the gate for **every** 600 MHz pass; none reached = no measured pass. The
  control uses 57/58, falling back to 55/56 from the next pass if three runs in a row cannot reach it.
- **D8 — the control's heater is fp32 `pi`** ([`heater_pi.sh`](heater_pi.sh)): card 0's PMIC 75 W alarm trips on
  fp32 random data at 800 MHz (E84) and E60's heater probe on this card logged 33 300 MHz episodes (E84 C6). The
  600 MHz half keeps E60's `randn` heater (about half its 800 MHz power there).
- **D9 — the envelope, enforced in code.** [`guard_e118.py`](guard_e118.py) reads every 10 Hz sample of the running
  pass and stops it (the pass's STOP file, which every launch's `--stop-file` and `run_hl.py` honour) on **any single
  reading** of board ≥ 85 W or die ≥ 72 °C, or, while TDP 0 is set, a clock other than 600 MHz (a 300 MHz reading is
  the alarm's safe state). `run_hl.py`'s own cap is lowered from 78 to 72 °C. After a trip: restore, read back, no
  further launch.
- **D10 — rungs.** aifoundry1's operand set has no `lq_h3/h6`, `lb_h3/h6` (E72's D2 extras, built later on
  aifoundry2), so the 600 MHz half runs E72's registered 20 items exactly.

## Frozen predictions ([`predictions.json`](predictions.json), from `predict_e118.py`; sp source on both sides)

V₈₀₀ = **0.60387 V** (E60's card-0 kept runs), V₆₀₀ = **0.519 V** expected (card 0 read 519 mV at 600 MHz on 31 Oct
in both sources, E84); (V₆₀₀/V₈₀₀)² = **0.73867**; × 600/800 = **0.55400**. Every prediction is a formula in V,
re-evaluated at the voltage the pinned passes measure (E72 C2).

| | what | predicted | band | PASS if |
|---|---|---:|---|---|
| **V1m** (primary) | `lq` h2→h8 secant, board, fJ per designed flipped bit, **both sides at the same leakage slope**, E60 on its passes kept at both slopes (2, 3, 4, 5, 7, 8, 9, 10) | **77.605** at 0 W/°C; **73.939** at 0.3273 (E60's own fit on this card) | ±10 %: 69.84–85.37; 66.54–81.33 | inside at both slopes: PASS; at one: PARTIAL; at neither: FAIL |
| **V1** | the same at each side's own `--leak auto` (E72's registered form) | **75.706** | 68.14–83.28 | inside, **and** outside the alternative's band |
| | *the alternative: energy scaled with f too* | *56.780* | *51.10–62.46* | *the hypothesis V1 refutes; inside both bands = INCONCLUSIVE* |
| **V2** | the same on the minion rail (uncorrected, E72's caveat) | 67.895 | ±15 %: 57.71–78.08 | inside |
| **V3** | watts over `lq_h0`: `lq_h2`, `lq_h8` = E60's 1.912 / 5.672 W × f·V² | 1.0593 / 3.1425 W | ±10 % each | both inside (E72 missed `lq_h2` by 12.2 %) |
| **V4** | bend: full h ≥ 1 slope / h2→h8 secant | 1.3949 (mean of E72's 1.430 and E60 aifoundry3's 1.360) | 1.195–1.595 | inside |
| **V5** | `lb` full slope / `lq` full slope | 1.1104 (1.108, 1.113) | 0.960–1.260 | inside |
| **V6** | turn-on, `lb_h1`/`lq_h1` in watts | 3.172 (3.052, 3.291) | 1.903–4.441 | inside |
| **C1** | the 800 MHz control: `lq_h2`, `lq_h8` over `lq_h0` | E60's 1.912 / 5.672 W | ±10 % each | both inside; else V1 is also reported against today's control, said so |
| **G1** | the pin | 600 MHz in **100 %** of samples of every pinned launch; **zero** `Power throttle up` events between the ring before the pin and the ring after the last pinned pass | — | both halves |
| **G2** | the pinned voltage, mean `sp.minion_mv[0]` of the kept pinned runs | 0.519 V | 0.516–0.522 | inside |
| **G3** | the restore | 65 W / 65 °C read back; the return burst reaches ≥ 700 MHz; ≥ 1 `Power throttle up` between the ring after the pinned passes and the ring after the return burst | — | all three halves |
| V1s | *reported, not scored:* V1 against today's control instead of E60's rows | — | — | — |

E60's card-0 board SE is 4.3 % (aifoundry2's was 0.5 %), so the bands are wide, but the two hypotheses' bands do not
overlap.

## Decision rules

- **V1m is the result** (E72's correction: the matched form is the honest reading of "the same card at two operating
  points"); V1 is scored as E72 registered it and reported beside it. If a measurement lands in the alternative's band
  instead, that is reported as the registered hypothesis refuted; inside both bands is INCONCLUSIVE.
- **The unit of replication is the pass.** Fewer than 3 kept 600 MHz passes: V1, V1m, V2–V6 are NOT SCORED.
- **G1 is a gate, not a result.** One sample at any clock but 600 MHz in a pinned launch voids the run (E60's clock
  gate); a pin that does not hold (the smoke, or the guard) stops the session: restore, report blocked, no claim
  about V².
- **The envelope** (the owner's): TDP ≤ 75 W (only 0 and 65 are written); the threshold never written; stop at any
  single board reading ≥ 85 W or die reading ≥ 72 °C (not expected: E60's 800 MHz rungs on this card drew 45–51 W).
- **A failed restore or a card that stops answering:** stop; keep the claim; write it up; `notify.py --unblock`; never
  reset, reboot, rescan, unbind or reload, and never touch card 1. The watchdog (armed before the set, 75 minutes)
  keeps retrying the one restore write.

## Checked before the claim (no card access)

- **On aifoundry1, `run_e118.sh setup`, Sun 1 Nov 2026 14:48 PST:** `ettelem-e118` built against the host's `/opt/et`
  (sha256 `a8481df7673891a8…`), marker present, the host's device layer honours `ET_DEVICES`; `sample --reset-ms`,
  `loglevel` and `threshold set` refused (rc 2) without opening the card. The operand files: **59 of 59** of E60's
  card-0 list byte-identical (the 4 `xnz_` sources it also lists are not on the host and are not used here). The
  shared harness on the host matches this repository byte for byte (`hl/run_hl.py` `88411c6d…`, `hl/block.sh`
  `77efcefd…`, `lib.sh` `033d0776…`, `dv2/sptrace_events.py` `8cbb7df0…`). `run_hl --list`: 20 items, 21 runs a pass;
  the control 4 items, 5 runs. Both dry passes (`V3_DRY=1`) ran to the end with no device access. card 0 and card 1:
  no holder in `et-who`; no other user's device process or CI job.
- **The scorer on E72's committed passes** (`score_e118.py`, sp source, `E118_CARD=aifoundry2`) reproduces E72's
  published numbers: V1 **79.1757 ± 3.0855 fJ** (published 79.17567 ± 3.08546), V2 63.27, V₆₀₀ 0.51792 V, leak 0.0982
  W/°C, 125/125 runs kept, and the matched row at 0 W/°C **81.07 ± 3.57** (published 81.07 ± 3.57).

## Files

`predict_e118.py` → `predictions.json`; `gov_e118.py` (gates, the one write and its restore, the watchdog, the ring
dumps, read-backs); `session_e118.sh` (the detached session); `run_e118.sh` (setup / gates / session / status / wait /
final); `block_e118.sh`, `heater_pi.sh`, `guard_e118.py`; `ettelem-e118/` (the no-PMIC-read reader);
`reduce_e118.py` and `score_e118.py` (the registered reduction and the scoring of every rule above, G1 and G3 half by
half from the ring dumps); [`CHANGE-RECORD.md`](CHANGE-RECORD.md). Data:
`docs/reports/data/2026-11-01-e118-two-clock-card0/`.

## Amendments

*(none yet; anything after the pre-registration commit goes here, dated, before the data it touches)*
