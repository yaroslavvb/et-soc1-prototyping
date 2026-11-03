# E156: E139's encoded memory term on a second card, with two new images (Q139, aifoundry1 card 1, 600 MHz)

*Pre-registered Tue 3 Nov 2026 (week 45), about 05:55 PST, on the Intel, by the Q139 lane `a1c1-e156-memory-images`. No card was opened for this
file (the host binary was built on aifoundry1 at 05:34 PST with no device opened). Frozen at the commit that adds it, before the day's card post
names aifoundry1 card 1 for E156 and before its first launch. Changes after that go in Amendments, dated, before the data they touch.*

*It answers the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 10, "The memory path"**, and **rank 15 of Q138's final critic**: "E139's encoded term on another card and other images", whose next test
is "E139's design on aifoundry1 card 1 with two new images. Rule: the frozen +0.185 W per image predicts within 0.05 W." It builds on
[E139](../../../docs/reports/data/2026-11-02-e139-memory-split-more-passes/README.md) (aifoundry3 card 0, Mon 2 Nov 16:04-16:41 PST, eight
headline passes: the encoded part pays, about 0.46 pJ an encoded 64-bit toggle, R4 PAYS and R3 ENCODED, both SETTLED) and on
[E132](../../../docs/reports/data/2026-11-02-e132-memory-split/README.md), whose design E139 ran unchanged ([E132's registration](../e132/README.md)).
Asked in Q139: the owner's words of Mon 2 Nov 2026, about 18:40 PST, to settle the open questions of Horace's power model, with the goal of
predicting the power and the heat of kinds of numeric computation as accurately as possible.*

## What it does to predicting power and heat

The power model prices a kernel's DRAM traffic by the bits it toggles: E110's raw prices on a 64-bit and a 256-bit path, E132's line-edge
placement, and since E139 **one encoded term**, about 0.46 pJ for every toggle the DRAM bus's *encoded* bytes (after read DBI) make between
consecutive 64-bit pieces of a line. That term was measured on one card and on the two image pairs it was fitted on; on those it predicts the
encoded residual to 0.028 W (E139's README, its table 3). E156 tests it **out of sample twice over**: on a second card (aifoundry1 card 1, whose
SRAM rail sits at 750 mV against aifoundry3's 700 and whose minion rail at 499 mV against 523), and on two image pairs no run has measured, each
predicted from its own encoded-toggle count and E139's frozen price before any pass. One pair keeps E139's 64-bit layout with new bytes, a new
count (+280 encoded 64-bit toggles a line, not +392) and a new raw level; the other keeps E139's bytes and moves the block edges to every 32 bits,
where E139's count is zero, so it asks **which width the encoded term lives at**. For random data the answer moves the term by about a factor of
two: a 64-bit count and a 32-bit count of a random line are nearly equal (56 and 60 byte edges a line), while their prices differ by 2x (0.46 and
0.93 pJ). The data README states each pair's error before (the model without an encoded term: the whole residual) and after (with E139's term),
and the term's error on this card's own E56 and E448. **For heat**, the term enters only through board power: 0.1-0.5 W times card 1's die rise per
board watt (M7's H2, 0.1151 C/W) is 0.01-0.06 C, below what the 4.5 s readout resolves, so E156 scores power only.

## The design: E139's family E on card 1, plus two new pairs

E139's design is E132's: E110's DRAM command (`enercat_host --pattern flw_pat --harts 1 --seconds 4 --window 240000000 --operands file:<img>
--stride 64 --slice-bytes 131072 --region 131072`: 1,024 harts each fetch one 64 B line per load from 128 MB in all), every image one 64 B line
repeated through the buffer, the runner `runitems.py` (shuffled order, `anchor_pi` first and last, two burn-in launches, a launch at 58 C after a
59 C preheat), the estimator, gates and pass rules of `reduce_e132.py`. **E156 keeps E132's family E, its ties and anchors byte for byte**
(`make_e156.py` checks each against E132's committed `gen.sha256`) and **adds two pairs** built the way E132 built `eh_64` / `el_64`: the image and
its encoded-quiet twin carry the same ones and the same raw toggles at every width, and differ in the encoded toggles (and in pins held high and
beat-level pin toggles, which the residual removes at the session's own prices, E132's formula).

| pair | image / twin | bytes, layout | raw r64 | Δe64 | Δe32 | Δe128 | Δt_enc | Δtx_enc | Δhi | as in |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `E56` | `eh_64` / `el_64` | 0x0F, 0x1F / lane 0 0x0F, 0x0E; lane 1 0x1F, 0x3F; 64-bit blocks | 56 | +392 | +196 | 0 | +98 | +14 | +32 | E132, E139 |
| `E448` | `vl_64` / `c3_64` | 0x0F, 0xF0 / 0x07, 0xF8; 64-bit blocks | 448 | +392 | +196 | 0 | +98 | +14 | +32 | E132, E139 |
| `E192` | `vl_128` / `c3_128` | as E448; 128-bit blocks | 192 | +168 | +84 | +336 | +42 | +14 | +32 | E132, E139 (reported there) |
| **`E7`** | **`e7_64` / `e2_64`** | **0x07, 0x1F / 0x0F, 0x1E; 64-bit blocks** | **112** | **+280** | +140 | 0 | +70 | +10 | **−32** | **new** |
| **`E32`** | **`eh_32` / `el_32`** | **E56's bytes; 32-bit blocks** | **0** | **0** | **+420** | 0 | +210 | +14 | +32 | **new** |

Counts are per 64 B line, from the bytes (`make_e156.py --check`, E99's encoder `dm/dm_enc.py` and E110's `features`; [`gen/counts.json`](../../../docs/reports/data/2026-11-03-e156-memory-images-card1/gen/counts.json)):
eW the encoded (9-pin: 8 DQ + DMI) toggles between consecutive W-bit pieces inside a line, t_enc the encoded pin toggles between beats, tx_enc
the encoded pin toggles from a line's last beat to the next line's first on a channel, hi the pins driven high. Both new pairs carry equal ones
(256 in `E7`'s, 288 in `E32`'s), equal raw toggles at every width and at the line edge, and one value per line (`check: 0 bad`).
**The residual** of every pair (x, y) is E132's: `E = (x − y) − (Δt_enc / 496) V16 − (Δhi / 192) Hp`, with `V16` = `dm_a44` − `dm_u4` (496 pin
toggles) and `Hp` = ½[(`c3_64` − `wl_64`) + (`c3_128` − `wl_128`)] (192 pins held high), both measured in the same pass. For E132's pairs the
coefficients are E132's exactly (the selftest, below).

**Per pass:** `anchor_pi` first and last, the 16 memory items once each (`dp_zeros`, `dm_u4`, `dm_l08`, `dm_a44`, `wl_64`, `vl_64`, `wl_128`,
`vl_128`, `c3_64`, `c3_128`, `eh_64`, `el_64`, `e7_64`, `e2_64`, `eh_32`, `el_32`) in runitems' shuffled order, two burn-in launches: 20 launches.
**Smoke 15601** (`anchor_pi`, `e7_64`, `eh_32`, `eh_64`, `c3_128`: E139's smoke with the two new images in place of the two family-A ones) and
E110's smoke gate unchanged. **Passes 15610-15619; 15610 is the registered warm-up, reported and never in the headline** (E132's 13210, E139's 13910).

## The frozen predictions ([`predictions-e156.json`](predictions-e156.json), printed in [`predictions-e156.txt`](predictions-e156.txt))

**The price is E139's** (its registered primary: eight headline passes on aifoundry3, the board meter's dips removed, leakage `auto`), the mean of
its two residuals per encoded 64-bit toggle at its line rate: **0.4630 pJ** (E56 0.4628, E448 0.4632; `e139.json` › `verdicts.R4_encoded_board`).
**A pair's prediction is price × count × this session's line rate** (`reduce_e132`'s `lines_per_s`, the headline mean over the session's DRAM runs;
E139's was 1.1729 × 10⁹ lines a second). The other readings put E139's same two residuals on another count, each priced so that it fits E56 and
E448 exactly; all five agree on E139's images and on `E7`, and differ on `E32` and `E192`:

| reading | count | price | `E56`, `E448` | `E192` | **`E7`** | **`E32`** |
|---|---|---:|---:|---:|---:|---:|
| **A (registered: E139's)** | Δe64 | 0.4630 pJ | 0.2129 | 0.0912 | **0.1521** | **0.0000** |
| B, a 32-bit path | Δe32 | 0.9260 pJ | 0.2129 | 0.0912 | 0.1521 | 0.4562 |
| C, the 64- and 128-bit paths | Δe64 + Δe128 | 0.4630 pJ | 0.2129 | 0.2737 | 0.1521 | 0.0000 |
| E, the pins mispriced | Δt_enc | 1.852 pJ | 0.2129 | 0.0912 | 0.1521 | 0.4562 |
| F, the line edge | Δtx_enc | 12.96 pJ | 0.2129 | 0.2129 | 0.1521 | 0.2129 |

(W, at E139's line rate; the scored values use this session's.) E139 read `E192` at +0.180 W [0.031, 0.329]: between A and C, not deciding.

## Rules (frozen in `predictions-e156.json` › `rules` and `decision`; scored by [`reduce_e156.py`](reduce_e156.py))

Every statistic is a within-pass contrast, its headline the mean over headline passes with a two-sided t interval on their scatter (E132's).
**Fewer than three headline passes: every rule NOT-SCORED.**

| rule | statistic | line | verdicts |
|---|---|---|---|
| **N1 (primary, the critic's rule)** | `E7` and `E32` against reading A's prediction | \|mean − prediction\| ≤ **0.05 W** for each | **PASS** if both, **FAIL** if either. Beside each: its 95% interval against prediction ± 0.05 W, read as decided inside, decided outside, or straddling |
| **C1** (E139's images on this card) | `E56` and `E448` against reading A's prediction | the same 0.05 W | PASS / FAIL; E132's R4 class reading (PAYS / NONE / ...) beside it, and each against E132's frozen +0.185 W |
| **N2** (the width, inside the session) | for each reading X and pair, per pass d_X = E_pair − k_X (E56 + E448)/2, k_X = the pair's count over E56's under X | X is consistent on a pair when the 95% interval of d_X contains 0 | the readings consistent on both `E32` and `E192`: `A ONLY`, ..., `SEVERAL: …`, `NONE`. Free of card 1's price (it compares the pairs with this card's own E56 and E448). Reported beside it: `E32` alone, `E192` alone, and `E7`'s d (k = 5/7 in every reading) |
| **D** (read DBI evident) | `Hp` on the board | E132's class at 0.10 W | **EVIDENT** (present), **NOT EVIDENT** (absent: every encoded prediction assumes read DBI on, as on aifoundry3), UNRESOLVED |

**Reported, not scored:** E139's ties on this card against aifoundry3 (`S64`, `S128`, `V16`, `V64`, `V128`, `U4z`, `Hp`, `RH64`, `RH128`, each
minus E139's); the price per encoded 64-bit toggle on this card from `E56`, `E448`, `E7`; the DDR die rail (`die_mv.ddr`) on every pair (`RE64`,
`RE448`, `RE128`, `RE7`, `RE32`) and every item over zeros, with E132's classes (moves ≤ −0.30 mV with the interval below 0, still inside ±0.30 mV);
where each contrast is paid (the three metered rails' sum, off); the warm-up pass; the leakage arms 0.2936 and 0.3803 W/C (E139's) and **0.3134
W/C (Q139(u)'s frozen idle slope for this card)** and the dips-kept arm; any verdict that moves at an arm is named.

**The estimator, gates and arms: E139's, unchanged** (`reduce_e156.py` copies `reduce_e132.main()`'s estimator line for line and imports E132's
helpers): per kept pass, each item's board power over [t0+1 s, t0+3 s), corrected to the launch reading with E81's `auto` leakage slope; the rails
raw over [t0+2 s, t0+4 s), never past the run; the DDR die rail over the board's window. Run gates: one clock, voltage within 3 mV of the pass
median, a launch within 0.5 C of 58 C after a 59 C preheat, the window's median `took_ms` ≤ 60 ms, an ok record, the rails present. A pass is set
aside at an `anchor_pi` drift above 0.3 W or more than a third of its memory runs failing a gate. **Primary arm: the board meter's dip samples
removed** (`dp/posthoc_dips.py`, E82 amendment A2's rule, defined on this card), as E139's primary.

**Precision, before the data.** E139's per-pass scatter (aifoundry3): `E56` 0.075 W, `E448` 0.101, `E192` 0.178; `E32`-like and `E7`-like
combinations of E139's own contrasts 0.073 and 0.072. At 0.075 W and six headline passes the 95% half-width is 0.079 W, and if the model is exactly
right each new pair's point error lands within 0.05 W with probability 0.90 (0.86 at five passes, 0.82 at four), so N1 PASS is about 0.8 likely
under a true model. `E32` separates A (0) from F (0.21 W) and from B and E (0.46 W) by more than its expected half-width; `E192` will not separate A
from C or F at six passes, so N2 is likely to read `SEVERAL: A,C` if A holds. **What I expect, frozen so it can be wrong:** C1 PASS and D EVIDENT
(the same DRAM clock, 933 MHz, and firmware line as aifoundry3); `E7` near +0.15 W; `E32` near 0; N1 PASS; N2 `SEVERAL: A,C`.

## What is reused unchanged, and what changes

Reused unchanged, with their sha256 frozen in `predictions-e156.json` › `harness` and checked by [`check_e156.py`](check_e156.py) on the box
before any device opens: `lib.sh`, `runitems.py`, `text_hash.sh`, E128's telemetry allow-list `e128/ettelem_guard.sh`, Q136(w)'s checker
`dmcmd_audit.py` and its table, E110's `smoke_gate_e110.py`, E99's `dm/build_host.sh` and `make_host_src.py`, the enercat and sparsity host
sources; in the reduction, `dp/posthoc_dips.py`, `reduce_hl.py`, `reduce_mf.py`, `reduce_e110.py`, `reduce_e132.py`. Departures from E139's
design, decided before any E156 data:

1. **Family A is left out** (the ten address-bit images `ab_0` … `ab_7`, `ab_x70`, `ab_rnd`): it serves E132's R2 and R5 (the interleaves,
   the line-edge price), which this run does not ask. Its ten runs a pass make room for the four new images and more passes in 40 card-minutes.
   None of E132's R1-R6 is scored as a rule here; the ties (R1's quantities), the DDR die rail classes (R3's and R6's) and R4's class reading
   (in C1) are reported.
2. **Card 1's harness, E155's** (this card, the same morning): `block_e156.sh` is E75's `mf/block.sh` with E155's changes: every telemetry call
   through `e128/ettelem_guard.sh`, `lib.sh`'s `drain_mgmt` replaced by a refusal (so `dev_mngt_service`, which opens every card's node, never
   runs), card 1 only (`V3_DEVICE=1`, `etsoc-shire1.lock`), **live-sample stops** in [`run_e156.py`](run_e156.py) (runitems.py unchanged, with
   E155's guard and in-run watcher: `board_w` ≥ **66 W**, any minion-shire field ≥ **72 C**, or a sampler line ≥ **1.5 s** old, read from the
   running sampler's `.raw` file, writes STOP and ends the pass; E139's own watcher read the closed file and never saw a sample, its C1) and
   runitems' die cap 70 C on `temp_c.minshire[0]` (E139's `MF_MAX_C`). **The stop path is tested before the smoke**: `block_e156.sh 15602 anchor_pi
   --stoptest` starts the sampler and runs the guard with the die stop at 1.0 C, the board stop at 1.0 W, the watcher at 1.0 W and the stale limit at
   0.0 s; each must end with exit 6 and a STOP line read from a live sample before any launch, or no smoke and no pass runs.
3. **The host is E99's source built on this box** ([`box-binaries.txt`](box-binaries.txt)): `dm/build_host.sh` unchanged wrote
   `build/enercat-e99/host/enercat_host` (`e2463274…`) from the lab's `main.cpp` (`3cad4adc…`, the file aifoundry3's E99 build read; the generated
   `main_e99.cpp`, `0386b8b5…`, is byte-identical to aifoundry3's); it launches `build/enercat-hl/kernel/enercat.elf`, whose disassembly hash
   (`a5743c3c…`) equals the kernel aifoundry3's E99 host launched for E132 and E139. The heater and drift anchor are this card's
   `build/sparsity/host/sparsity_host` (`e0fbecce…`, E142, E148 and E155's).
4. **The reducer** is new code around E139's estimator (`reduce_e156.py`): E132's contrasts are built from the images' counts, and the rules are
   E156's. [`selftest_e156.py`](selftest_e156.py) ([`selftest.txt`](selftest.txt)): **A**, on E139's committed passes it reproduces E139's
   `e139.json` to 1e-9 on all 17 shared contrasts in all six columns, the line rate and the headline passes; **B**, with the four new images aliased
   onto measured runs, `E7` and `E32` equal their formulas on every pass and every rule returns a verdict. SELFTEST PASS. Nothing there is a measurement.
5. **Budget and gates** (Q139's): at most 40 card-minutes from the session's first config read to its last; [`queue_e156.sh`](queue_e156.sh)
   starts a pass only if now + projected ≤ T0 + 2,400 − 150 s and its end is before 11:20 PST; projected is 330 s until a pass ends, then the longest
   measured; a pass in flight is never cut. [`session_e156.sh`](session_e156.sh) refuses to start after 10:30 PST; every run ends by 11:30 PST.
   Expected: about seven passes (the warm-up and six headline).

## Device commands sent

*The owner's rule of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send, classified from
the firmware source of the running build, READ or WRITE; read-only PMIC voltage reads are allowed; no governor move, no power cycle.* Card 1
reports release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.3.0 since 31 Oct 2026 (E129's dated note C1); the source read is et-platform **`836a4ab`**, the
version-matched revision of Q136(w)'s table (E148's and E155's audits of the same command set). Paths under
`device-bootloaders/src/ServiceProcessorBL2/`.

| # | command (id) | sent by | at `836a4ab` | class |
|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | `ettelem config` (the session's start and end), through the guard | `thermal_power_monitor.c:339` → `services/thermal_pwr_mgmt.c:613`, a copy from SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | `ettelem config` | `:438` → `thermal_pwr_mgmt.c:665`, SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` (23) | `ettelem config` | `:48` → `thermal_pwr_mgmt.c:551`, SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`, `ettelem sample` | `performance.c:41` → `driver/io_pll.c:907-960`, PLL register reads | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`, `ettelem sample` (the DDR die rail is this reply's PVT memory-shire reading) | `thermal_pwr_mgmt.c:1142`: PVT reads and two `pmic_get_voltage` I2C register reads | **READ**, PMIC voltage reads, allowed |
| 6 | `DM_CMD_GET_MODULE_POWER` (33) | `ettelem sample` (the 10 Hz sampler), `lib.sh`'s 1 s `die_c` reads at each block's start and end | `thermal_pwr_mgmt.c:984`, SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` (60) | `ettelem sample` | `performance.c:404` → `thermal_pwr_mgmt.c:2780`, SP RAM, resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `ettelem sample` | `thermal_pwr_mgmt.c:732`, PVT sensor reads | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` (31) | `ettelem sample` | `thermal_pwr_mgmt.c:1010`, nine `pmic_get_voltage` register reads | **READ**, PMIC voltage reads, allowed |
| — | `DM_CMD_SET_STATS_RUN_CONTROL` (62), a `--reset-ms` forwarded by `lib.sh:154` | conditional | **WRITE: never sent** (the reviewed exception: `block_e156.sh`'s one `start_sampler` call passes the file and the duration only, and `ettelem_guard.sh` refuses `--reset-ms`) |
| — | `dev_mngt_service` (`lib.sh`'s `drain_mgmt`) | — | **never sent**: replaced by a refusal in `block_e156.sh` |
| — | `enercat_host` (E99's, `build/enercat-e99`), `sparsity_host` (the heater and `anchor_pi`) | the workload | the Master Minion's device-ops (DMA of their own buffers, kernel launches), opening the ops node only (`workloads/enercat/host/main.cpp:147`, `workloads/sparsity/host/main.cpp:172`): not device-management commands |
| — | `et-who`, `et-holders` (through `sudo -n`), `et-lab-manifest`, `flock`, `timeout`, `ps`, `who` | helpers | sysfs and `fuser` reads; they open no device node |

**The run sends no WRITE.** Not sent: the statistics reset, the SP log level, `sptrace`, `dev_mngt_service`, the firmware-revisions query, a
residency read, any governor, TDP, threshold, clock or voltage set, any reset, power cycle, PCIe, driver, firmware or OTA work. **The checker**
(`tools/claims-v3/dmcmd_audit.py`, `f29e91ca…`, table `50168632…`) on every file the session runs or sources
([`preflight_e156.sh`](preflight_e156.sh), output [`dmcmd-audit.txt`](dmcmd-audit.txt)): **GO, 32 send sites, 0 disallowed, no WRITE allowed**, the
nine READs, PMIC access on `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` only (reads), with the one reviewed exception at `lib.sh:154`; GO on the Intel
and on the box (05:41 PST); the session runs it again on the box and opens no device unless it reads GO. **Residual:** the `ettelem` binary on this
box (`8008f96f…`, there since 28 Sep) predates the source its sends are classified from; the classification holds for every revision it can come
from (E142's C4). **Condition:** if the session-start config read or the smoke's telemetry comes back in another form than E155's (an error, a
missing field, `since_reset_ms` other than −1, a clock other than 600 MHz), the list may not describe what runs: the session is stopped there
(`build/e156/STOP`) and the result is NO-GO.

**Verdict before the first launch: GO**, on that condition.

## How to run it (aifoundry1, in `~/nekko`, card 1)

    # on the Intel, after this commit is on origin/main
    rsync -a --exclude __pycache__ tools/claims-v3/e156/ aifoundry1:nekko/tools/claims-v3/e156/
    rsync -a docs/reports/data/2026-11-03-e156-memory-images-card1/gen/ aifoundry1:nekko/build/e156-gen/
    # on the box: check_e156.py, preflight_e156.sh, the gen's sha256, a V3_DRY=1 block and stop test (no card)
    # -> rewrite the day's post to add "using aifoundry1 card 1 for 1 h, until ~HH:MM PST [doc](...)"
    E156_T0=$(date +%s) setsid nohup bash tools/claims-v3/e156/session_e156.sh > build/e156/session.out 2>&1 < /dev/null &
    # back on the Intel
    bash tools/claims-v3/e156/collect_e156.sh docs/reports/data/2026-11-03-e156-memory-images-card1
    PY=<python3 with numpy> bash tools/claims-v3/e156/reduce_e156.sh docs/reports/data/2026-11-03-e156-memory-images-card1

## Files

`README.md` (this), `make_e156.py` (the images and every count), `make_predictions_e156.py`, `predictions-e156.json` and `.txt` (the freeze:
prices, pairs, readings, rules, plan, stops, every hash), `reduce_e156.py` and `reduce_e156.sh` (the registered reduction), `selftest_e156.py` and
`selftest.txt`, `block_e156.sh`, `run_e156.py`, `session_e156.sh`, `queue_e156.sh`, `check_e156.py`, `preflight_e156.sh` and `dmcmd-audit.txt`,
`collect_e156.sh`, `box-binaries.txt`. The images: `docs/reports/data/2026-11-03-e156-memory-images-card1/gen/` (manifest, `srcs/`, `counts.json`,
`gen.sha256`).

## Amendments

*(none yet)*
