# E152: the float B-lane gate's price per flip as a dose ladder, 1, 2, 4 and 8 lanes switching at fixed data (Q139, aifoundry3 card 0, 600 MHz)

*Pre-registered Tue 3 Nov 2026 (week 45), on the Intel, before the reservation of aifoundry3 and before any card has run one of
E152's nine ladder tiles, in Q139 (lane `a3-e152-gate-dose`). **It answers the tail of item 6 of the kinds page's section 11**,
"A power model across kinds" ([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
the list as live at `8ec9ead107aa`), and **Q138's final critic's open rank 12**: "Physical readings of M7's constants and the gate's
price ... Open: what spends the gate's price per flip, its linearity ...", whose next test is "a registered dose ladder of gate flips
per op at fixed data (1, 2, 4 and 8 lanes switching) with the price frozen from E127. Rule: linear within 10%." It builds on
[E127](../../../docs/reports/data/2026-11-02-e127-b-gate/README.md) (its design, its harness, its frozen price) and its registration
[`../e127/README.md`](../e127/README.md). The owner's goal for this work, his words of 2 November 2026: to predict the power
requirement and heat generation of numeric computations as accurately as possible. The frozen numbers are in
[`predictions-e152.json`](predictions-e152.json) (table: [`predictions-e152.md`](predictions-e152.md)), written by
[`make_predictions_e152.py`](make_predictions_e152.py) from the committed files it names, each checked by sha256. Any change after
this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry3 card 0 only**, 600 MHz as its boot-time TDP
of 0 latches it, TDP 0 / threshold 65 °C as read, never set. **E152 writes nothing and sends no write command of any kind**: no
governor move, no TDP, threshold or clock set, no reset, no `--reset-ms` (so not even the one write the owner's rules allow), no
firmware-revisions query, no residency read. Every device-management command it sends is a read (§ Device commands sent).*

## The question

E127 held the operand data still (every product exactly zero, the B operand bus moving the same 4,096 bits an op) and moved
only the float B lanes' zero gate. Switching every lane's gate every cycle, against holding four lanes off, cost **+1.275 ± 0.094 W**
(its Q2, `q_chk` − `q_steady`, five passes), about 0.28 pJ for every time one lane's gate turned on or off, of which the power
model then (M5) priced 0.47 W. That is **one dose**, 4,096 flips an op, so E127's README lists as open "whether the price is linear
in flips (one dose)". The models since price the gate with one constant per flip: M7's `gtr` 145.5 fJ, M8's 140.7 ± 14.7 fJ
(jackknife), plus bench toggle terms that move with the gate (M8's whole price at E127's pair is 235.3 fJ a flip). **A constant per
flip is only right if the cost is linear in flips.** If part of it is spent whenever *any* lane flips (a shared enable, valid or
clock path), a kernel whose zeros switch one lane at a time pays more per flip than the constant says, and one that switches all
eight pays less; if lanes switching together cost more than apart (a supply or crowding effect), the reverse.

E152 asks two things, with everything else held:

1. **Is the gate's cost linear in the number of lanes switching?** Five doses, 0, 1, 2, 4 and 8 lanes whose gate flips every cycle.
   Rule R1: every intermediate dose within 10% of the full-scale contrast of the ladder's own straight line.
2. **Does E127's price carry?** The ladder's price per flip (one slope through all its tiles) against E127's frozen price, ±10% (R2).

## The tiles

All 2,048 bytes in the host's `--values file:` layout (A then B, 1,024 bytes each), written by [`make_e152.py`](make_e152.py)
(`--check` rebuilds them and asserts every rule below on the bytes) into [`tiles/fp32/`](tiles/fp32/), described in
[`e152-tiles.json`](e152-tiles.json) (rules, sha256 of each file and half, the design figures), hashes in [`SHA256SUMS`](SHA256SUMS).
The stream is `make_kinds.issue_streams` (the kinds README § 1): for each B line k, for each A row i, two micro-ops h = 0, 1; A's
word is broadcast and lane l carries B[k][8h + l], so inside a B line a lane alternates between its two words for 32 micro-ops,
and its gate flips at every micro-op boundary exactly when one of the two is zero and the other is not.

**Quiet, as E127's quiet tiles.** Every A word is fp32 1.0 (`0x3F800000`); every live B word is the denormal `0x00000001` or
`0x00000002`, which is not zero, so the lane is live (the gate compares raw words: E93 R3, E121 on this card), and which is flushed
before the multiplier (PRM § 3.4; `txfma_f0.v`), so every product is 0 and C never moves. Lane roles per B line: **S0** switching,
live on h = 0 only (words `0x1`, `0`); **S1** switching, live on h = 1 only (`0`, `0x1`); **L** steady and live (`0x1`, `0x2`);
**O** steady and off. A steady lane is live in one half of the B lines (0–7 or 8–15) and off in the other.

**Held in every ladder tile** (asserted): the B operand bus moves exactly **4,096 changed bits an op** (E127's quiet figure); A never
moves; **every lane is live in exactly half of all micro-ops**, so lane position cannot enter as a share of live lane-cycles (E127's
Q5 lane-position contrast, +0.135 W, cannot move a ladder contrast); **no micro-op has all eight lanes off**, so E127's all-off
part (its Q3) never enters; four lanes live in every micro-op, two of them lanes 0–3 (all but the single-lane tiles: their live
count is 5 / 4 in lines 0–7 and 4 / 3 in lines 8–15, average 4). **Gate flips an op above `gd0`'s 16 are exactly 510 × n.**

| tile | n | what it is | flips/op | above gd0 | boundaries with a flip | live/micro-op | sha256 (12) |
|---|---:|---|---:|---:|---:|---|---|
| `fp32.gd0` | 0 | L on lanes 0,1,4,5 in lines 0–7 and on 2,3,6,7 in 8–15; no lane switches inside a line | 16 | 0 | 2 | 4 | `3d7d91ca6903` |
| `fp32.gd1a` | 1 | lane 0 S0; L on 1,4,5,6 in lines 0–7, on 2,3,7 in 8–15 | 526 | 510 | 512 | 3–5 | `6133b7f990d5` |
| `fp32.gd1b` | 1 | `gd1a` mirrored (lane l → 7 − l): lane 7 switching | 526 | 510 | 512 | 3–5 | `56cafcd25f52` |
| `fp32.gd1h` | 1\* | lanes 0 S0 and 1 S1 in lines 0–7 only (lane 0 live in 8–11, lane 1 in 12–15): one lane's flips on half the boundaries, at four live everywhere | 528 | 512 | 258 | 4 | `f3807f7e72fe` |
| `fp32.gd2a` | 2 | lanes 0 S0, 1 S1; L on 2,4,5 in lines 0–7, on 3,6,7 in 8–15 | 1,036 | 1,020 | 512 | 4 | `7802275df2ed` |
| `fp32.gd2b` | 2 | `gd2a` mirrored: lanes 7 S0, 6 S1 | 1,036 | 1,020 | 512 | 4 | `3d16553474ee` |
| `fp32.gd4a` | 4 | lanes 0,4 S0; 1,5 S1; L on 2,6 in lines 0–7, on 3,7 in 8–15 | 2,056 | 2,040 | 512 | 4 | `414cad6f3e4a` |
| `fp32.gd4b` | 4 | `gd4a` mirrored: lanes 7,3 S0; 6,2 S1 | 2,056 | 2,040 | 512 | 4 | `e4bfb5e09ab1` |
| `fp32.gd8` | 8 | lanes 0,1,4,5 S0; 2,3,6,7 S1: every lane flips every cycle | 4,096 | 4,080 | 512 | 4 | `75d4e6129458` |
| `fp32.q_steady` | (0) | **E127's tile, byte for byte**: lanes 0–3 off all launch, 4–7 live | 0 | −16 | 0 | 4 | `6c5ccd2ffe96` |
| `fp32.q_chk` | (8) | **E127's tile, byte for byte**: every lane flips every cycle, lanes 0–3 live on h = 0 | 4,096 | 4,080 | 512 | 4 | `b038cd64953c` |

Each intermediate dose has **two lane assignments** (the mirror pairs), so a lane-specific cost averages out of the dose and the pair's
difference reports it. `gd1h` is the single-lane dose at a constant live count, and it puts one lane's worth of flips on 258
boundaries against `gd1a`'s 512: a cost spent per *boundary* with any flip would make `gd1a` dearer than `gd1h`; a cost per *flip*
would not. The two bridge tiles are E127's own, so this session re-measures the contrast the price is frozen from (S2).

## What runs

| | E127 (the last run of this design, this card) | E152 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type fp32 --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet | the same | E78's protocol, the footing M7's and M8's constants were fitted on |
| items | E127's 13 tiles, E78's six anchors three times, the tie twice: 33 runs (35 launches) | **E152's 11 tiles, E78's six anchors three times, the tie twice: 31 runs** (33 launches; two `anchor_pi` burn-ins open each pass) | the question |
| order | `Random("E127\|aifoundry3\|<pass>")`, dealt round-robin into three segments, each with the six anchors, reshuffled | `Random("E152\|aifoundry3\|<pass>")`, the same dealing (4, 4, 3 tiles) | `e152_common.pass_order` |
| passes | 12710–12714, five kept | **15210–15215 planned (six); the budget rule decides; at least three kept to score** | precision (§ Precision) |
| smoke | 12701, eight 2 s runs | **15201**: `anchor_pi`, `gd0`, `gd1a`, `gd8`, `q_chk`, `fp32.zeros`, `fp32.randn`, 2 s each, no preheat, read for cycles per op (546) | — |
| stop test | — | **15202** (board) and **15203** (die), after the smoke, before the queue (§ Stops) | the stops must be known to act on live samples |
| primary reduction | E78's `reduce_e78.py` unchanged, dips removed by E82 A2's definition, leakage `auto` | **the same** (`reduce_e152.py --drop-dips`) | E127's primary on this card |
| arms (reported) | dips kept; leakage 0.1994, 0.3803 and 0; gates off | the same | a verdict that moves at an arm is marked arm-sensitive |
| stops | die 70 °C, board 65 W | the same, both read from the live sampler file before every launch | § Stops |
| telemetry | lib.sh's `ettelem` directly | **every config and sample read through E128's guard** (`tools/claims-v3/e128/ettelem_guard.sh`: `config` and `sample --seconds --every-ms` only, anything else refused before the device opens), and lib.sh's `drain_mgmt` replaced by a refusal | E151's hardening |
| config reads | `ettelem config` at both ends of every block, under the card lock, `timeout 10`, and the session-end read | the same, and at both ends of each stop test | §17 of the brief |
| data | raw `kinds/p127<nn>/` | raw `~/aifoundry/build/claims-v3/aifoundry3/kinds/p152<nn>/`, `kinds-smoke/p15201`, `kinds-stoptest/p1520[23]`, logs `build/e152-logs/`; results `docs/reports/data/2026-11-03-e152-gate-dose/` | — |

**What is E78's and E127's, byte for byte.** `run_e152.py`, `reduce_e152.py` and `run_e152.sh setup` check `tools/claims-v3/lib.sh`
`033d0776…`, `kinds/e78_common.py` `c58923a5…`, `kinds/run_e78.py` `f3efd783…`, `kinds/reduce_e78.py` `6a158cee…`, `kinds/kinds.json`
`9586568f…` (E127's registered values) and E128's guard `c2c4ab76…` against `predictions-e152.json` › `harness.reused_unchanged_sha256`,
and E127's two tiles against their committed sha256, and refuse on any difference. `e152_common.install()` replaces `load_items` (E78's
items plus E152's 11 tiles) and `pass_order` on the shared `e78_common` module in memory, then `run_e78.main()` / `reduce_e78.main()` run
as they are: every run gate (600 MHz, ±3 mV, launch at 58 °C after 2.0 s quiet, records ok, cycles per op within 0.5% of 546, ≥ 15 window
samples, duty ≥ 0.97, the tile the host dumps equal to the item's registered sha256), every pass gate, the interpolation of fp32's zeros
and **D = p80 − Ẑ_fp32(t0)** are E78's own. Ported from E127 with marked changes: `e152_common.py`, `run_e152.py`, `block_e152.sh`,
`queue_e152.sh`, `run_e152.sh`, `reduce_e152.py`, `collect_e152.sh`; new: `make_e152.py`, `score_e152.py`, `make_predictions_e152.py`,
`selftest_e152.py`, `preflight_e152.sh`. Binaries: the tree's own, no rebuild, the two E127 registered and ran (`sparsity_host`
`20e760c2…`, `ettelem` `16037641…`); `run_e152.sh setup` checks both hashes.

## Device commands sent

*His rule of Mon 2 Nov 2026 (Q136; Q139 keeps it): every device-management command a run's harness, sampler, host program and helpers
send, classified from the firmware source of the running build, READ (no write anywhere) or WRITE (any register, flash, configuration,
counter or PMIC write); the only write allowed is the statistics reset, and E152 does not send it.* aifoundry3 reports release 1.4.0,
BL1 and BL2 0.22.0, PMIC 1.5.0; the source read is the open et-platform tree at `836a4ab` (BL2 0.22.0), the revision Q133's governor desk
and every Q136-Q139 lane used. Paths are under `device-bootloaders/src/ServiceProcessorBL2/`.

| # | command | sent by | when | firmware path at `836a4ab` | class |
|---|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | `ettelem config` (through E128's guard) | each block's start and end; the session-end read | `services/thermal_pwr_mgmt.c:613-617`, a copy of SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | `ettelem config` | as 1 | `thermal_pwr_mgmt.c:665-669`, SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` (23) | `ettelem config` | as 1 | `thermal_pwr_mgmt.c:551-555`, SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`; `ettelem sample` | as 1; every sample (10 Hz) | `services/perf_mgmt.c:276` → `driver/io_pll.c:907-960`, PLL register reads | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`; `ettelem sample` | as 4 | `thermal_pwr_mgmt.c:1142-1222`: PVT reads and **two PMIC voltage-register reads** (`pmic_controller.c:1473-1500`) | **READ** — PMIC voltage reads, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` (33) | `ettelem sample` (the 10 Hz sampler; lib.sh's `die_c`, a 1 s sample at each block's ends) | every sample | `thermal_pwr_mgmt.c:984-988`, SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` (60) | `ettelem sample` | every sample | `thermal_pwr_mgmt.c:2780-2784`, SP RAM; resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `ettelem sample` | every sample | `thermal_pwr_mgmt.c:732-773`, PVT register reads | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` (31) | `ettelem sample` | every sample | `thermal_pwr_mgmt.c:1010-1140`, **nine PMIC voltage-register reads** | **READ** — PMIC voltage reads, allowed |

**Never sent** (each checked in the code that runs): `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset (`ettelem` sends it only with
`--reset-ms` > 0; no E152 call passes it, and E128's guard refuses it before the device opens); lib.sh's `drain_mgmt`
(`dev_mngt_service -m DM_CMD_GET_MODULE_POWER`, a read; replaced by a refusal in `block_e152.sh`); `DM_CMD_SET_DM_TRACE_CONFIG`; the
firmware-revisions query; any residency read; any `DM_CMD_SET_*`. **The host program** (`sparsity_host`, the workload and E78's heater)
opens the ops node only (DMA write and read lists into its own buffers, kernel launches, an abort only on a kernel timeout): no
management command. **Host-side helpers that open no device node:** `et-who` / `et-holders`, `et-lab-manifest`, `flock`, `timeout`.

**The checker** `tools/claims-v3/dmcmd_audit.py` (unchanged), on every file the session runs (`preflight_e152.sh`: E152's card files,
`lib.sh`, E128's guard, E78's runner and common module, the workload's host source): **NO-GO** without an exception, at the one
conditional site E130's A1 reviewed (`lib.sh:154`, where `start_sampler` forwards extra arguments that could carry `--reset-ms`), and
with that reviewed exception **GO, 32 send sites, 0 disallowed** ([`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt),
[`dmcmd-audit.txt`](dmcmd-audit.txt)); the desk files send nothing (GO, 0 sites, [`dmcmd-audit-desk.txt`](dmcmd-audit-desk.txt)).
`run_e152.sh setup` and `smoke` run the same preflight on the box and open no device on anything but GO. **Residual (E127's C4,
E130's A1, E151's):** aifoundry3 runs the thermal firmware build flashed on 7 October 2026, whose source is not held, so these classes
rest on `836a4ab`'s handlers and on these nine reads' unchanged behaviour on this card (its replies since 7 October, `since_reset_ms`
−1). **Verdict before the first launch: GO.** If `run_e152.sh setup` finds either binary's sha256 changed, this list does not describe
what would run: NO-GO.

## Stops

E152 runs E127's quiet design at 4–6 W of D and E78's anchors, the hottest items. E127's five passes on this card read at most
**53.84 W** board and **62 °C** on the die; E151 this morning read at most 32.76 W and 55 °C. Registered stops, with margin: **a die
reading ≥ 70 °C** ends the pass (E78's `--max-c`; its second check at 80 °C reads the minion shires' PVT average, not a PMIC sensor:
E127's C5), and **a board reading ≥ 65 W** at any of E78's pre-launch reads writes the pass's STOP file and ends it with E78's exit 6
(`run_e152.py` `guard_board_power`; the self-test checks it fires at 65.0 W and not at 64.9 W). Either stop ends the queue. The PMIC
over-power alarm that aifoundry1's card 0 showed sits at 75 W (E84); nothing in E152 comes near it or risks a power cycle.

**Both stops read live samples.** `run_e78.py`'s reading takes the newest line of `--tel-live`, which `block_e152.sh` points at the
sampler's own output while it is being written (`$OUT/telemetry.jsonl.raw`; lib.sh copies it to `telemetry.jsonl` only when the
sampler stops), before every launch, and stops the pass when that line is older than 3 s. The die stop reads that line's minion-shire
reading; the board stop wraps the same `last_sample()` call, so it reads the same line's `board_w`, and it logs the first line it reads
(its age and board watts) in each block's `runner.err`.

**The stop test, registered (E147's), run once in the session after the smoke and before the queue.** Two blocks with one item
(`gd0`), each a full block (config reads, sampler, the card lock) with one line moved below what the card reads at idle: **15202** the
board line at 1 W (`E152_STOPTEST=board`; `run_e152.py` refuses a line at or above 30 W) and **15203** the die line at 20 °C (`--max-c
20`). Each must end the runner at its first pre-launch reading, before any launch: exit 6, the stop's own line in `STOP`, no `run` mark
and no record, and for the board test a first line at most 3 s old. `block_e152.sh --stoptest` writes the verdict to `stoptest.json`.
**If either fails, `run_e152.sh go` refuses to start the queue** (NO-GO: the registered stops would not be known to act).

## The frozen predictions

**The price, from E127's committed reading alone** (`docs/reports/data/2026-11-02-e127-b-gate/scored.json`, sha256 in
`predictions-e152.json` › `price`): per pass, Q2 − ½ Q5 (`q_chk` − `q_steady`, net of half the lane-position contrast, because
`q_chk` has half its live lane-cycles on lanes 0–3 and `q_steady` none, while every ladder tile has half; E127's correction C2), over
4,096 flips an op at fit_m5's op rate, 1.12111 × 10⁹ ops a second (600 MHz / 546 cycles × 1,024 minions × 0.9963), t(4) over E127's five
passes: **p\* = 262.9 fJ a flip [246.5, 279.4]** (whole: the contrast the card measured, not a price beyond any model). Unnetted, Q2
alone: 277.7 [257.2, 298.1] fJ (an arm, reported).

| dose n | flips above gd0 | **C(n) predicted, E127's price [95%]** | M8, linear bench | M8, gtr only | M7, linear bench |
|---|---:|---:|---:|---:|---:|
| 1 | 510 | **+0.150** [+0.141, +0.160] W | +0.135 | +0.080 | +0.138 |
| 2 | 1,020 | **+0.301** [+0.282, +0.320] | +0.269 | +0.161 | +0.276 |
| 4 | 2,040 | **+0.601** [+0.564, +0.639] | +0.538 | +0.322 | +0.551 |
| 8 | 4,080 | **+1.203** [+1.127, +1.278] = C8\* | +1.076 | +0.643 | +1.102 |

C(n) = D(dose n) − D(`gd0`). **The models' columns are reported, never a verdict.** E152's nine new tiles have no bench counts (the RTL
bench was not run for them: the Intel's bench was busy with another lane's pool), so M8 and M7 are given two ways: "gtr only" (their
gate term alone, `gtr` × the flips: M8 140.7 fJ, M7 145.5) and "linear bench" (their whole price per flip at E127's pair × the flips,
assuming their bench toggle terms scale with the flips: M8 235.3 fJ, M7 240.9, M6 247.9). The whole prices come from the committed
predictor, `docs/reports/data/2026-11-03-q139m-model/predict_blind6.py`, run unchanged on E127's two tiles and E127's bench counts
(`m8-bridge/`: M8 reads `q_steady` 4.683 W and `q_chk` 5.764 W, a Q2 of +1.081 W, against E127's measured 4.718 / 5.993 W and +1.275 W).
M8's C-register feature counts flips for these quiet tiles (`c_end` 3,968 an op on `q_chk`), as if the denormal products were not
flushed; at M8's 6.4 fJ that is about 0.03 W, inside its band.

**Other frozen numbers.** `gd0` − `q_steady`: **+0.072 W** (half of E127's Q5, if lane position adds per live lane-cycle, plus `gd0`'s
16 flips at p\*); `gd8` − `q_chk`: **0** (the same flips and per-lane live share, another instantaneous pattern); the mirror pairs: 0;
`gd1h` − mean(`gd1a`, `gd1b`): +0.0005 W (two more flips). The session tie: E127's dips-removed `fp32.randn` 24.77, `fp16.randn` 22.20,
`anchor_pi` 8.49 W (±0.50) and `int8.full` 7.08 W (±0.25); the bridge: E127's Q2, +1.275 W (±0.25).

## Decision rules

All on the primary reduction (E78's, dips removed by E82 A2, leakage `auto`, E78's gates). **Fewer than 3 kept passes: every rule NOT
SCORED**, and the gates-off arm is then the reading reported, labelled as that arm. A tile with fewer than 3 kept passes is left out and
named; a dose whose tile is left out is UNRESOLVED. Per kept pass: a dose's D is the mean of its tiles' D (n = 1: `gd1a`, `gd1b`; 2:
`gd2a`, `gd2b`; 4: `gd4a`, `gd4b`); C(n) = D(n) − D(`gd0`); **δ(n) = C(n) − (n / 8) C(8)**, the departure from the ladder's own straight
line through `gd0` and `gd8` (the flips above `gd0` are exactly 510 n). Means over passes; 95% intervals t(n − 1) × sd / √n.

| rule | what | verdicts |
|---|---|---|
| **E152-R1** | **linear within 10% (the primary)**: τ = 0.10 × C8\* = **0.120 W** | **LINEAR** if every \|δ(n)\| + its half-width ≤ τ (n = 1, 2, 4); **NONLINEAR** if some \|δ(n)\| − its half-width > τ; else **INCONCLUSIVE**. **NOT SCORED** unless C(8)'s low end ≥ 0.25 × C8\* (0.30 W): a ladder whose top is not resolved has no shape to test. The sign of Σ δ is reported: positive = concave (low doses dearer per flip, a shared part), negative = convex |
| **E152-R2** | **E127's price carries**: the ladder's price per flip, the least-squares slope of D on the designed flips an op over the eight ladder tiles (`gd0`, `gd1a`, `gd1b`, `gd2a`, `gd2b`, `gd4a`, `gd4b`, `gd8`) inside each pass, over the op rate | **CARRIES** if its interval lies inside p\* × [0.9, 1.1] = [236.6, 289.2] fJ; **MISSES** if it lies wholly outside; else **INCONCLUSIVE**. If R1 is not LINEAR the slope is a compromise, and the result says so |
| **E152-S1** | the session tie against E127 on this card (its dips-removed reading): `fp32.randn`, `fp16.randn`, `anchor_pi` (±0.50 W), `int8.full` (±0.25 W) | all inside: PASS; a failure means the session moved, never a verdict |
| **E152-S2** | the bridge: this session's `q_chk` − `q_steady` against E127's +1.275 W, ±0.25 W | PASS / FAIL; a failure means the gate's price moved between sessions, which R2 then reads beside |

**Why these lines, before the data.** "Linear within 10%" is read the way an instrument's linearity is: the largest departure of an
intermediate dose from the straight line through the ends, as a share of full scale. A share of each dose's own contrast cannot be
resolved at the low doses (C(1) is 0.15 W, measured to about ±0.06 W), so a rule written that way would read INCONCLUSIVE by
construction. The line is through the ladder's own ends, so a session offset in the price cannot fail R1; R2 tests the price
separately. τ is fixed from E127's frozen C8\*, not the session's own C(8), so it cannot move with the data. The R1 floor (C(8)'s low end
≥ 0.30 W) keeps a flat ladder (no gate cost at all) from reading LINEAR.

**Reported, never a verdict** (`scored.json` › `primary`, `results.md`): every tile's D; every dose's C(n), its price per flip and its
δ(n) / C(8) with a delta-method interval; the least-squares line of C(n) on n over n = 1, 2, 4, 8 and its intercept (a share spent
whenever any lane flips); the mirror pairs (lane assignment); `gd1h` against `gd1a`/`gd1b` (per boundary or per flip); `gd0` −
`q_steady` and `gd8` − `q_chk` (the ladder's balanced lanes against E127's tiles); each dose against E127's, M8's and M7's predictions;
the ladder's price against M8's and M7's per-flip constants.

**What I expect, frozen so it can be wrong:** **R1 LINEAR**: a lane's gate flip spends its price in that lane's own clock-gate enable and
clock branch, so the cost adds over lanes; a shared part (an enable, valid or clock path common to the eight lanes) would bend the ladder
concave, and I do not expect one. **R2 CARRIES**, with INCONCLUSIVE likely if this session's level moves by more than about 4% (the
slope's planned half-width is about 5% of p\* at six passes). S1 PASS, S2 PASS; the mirror pairs and `gd1h` within 0.1 W of their
partners; `gd0` − `q_steady` about +0.07 W; `gd8` − `q_chk` about 0.

**The statement the page gets, decided now.** R1 LINEAR: "the float B-lane gate's cost is linear in the lanes switching to within 10% of
its full scale, from one lane to eight: a constant per flip (M7's and M8's `gtr` form) is the right shape, and it extrapolates by flip
count". R1 NONLINEAR: "it is not: the first lanes switching cost X per flip and the last Y; a constant per flip fitted at the top dose
mispredicts kernels whose zeros switch fewer lanes by Z". INCONCLUSIVE is stated as such, with the departures and their intervals.
**Only tiles that ran are scored. No tile is dropped, re-drawn or added after the first pass, and no price, line or band changes.**

## Precision, before the data

From E127's quiet contrasts' per-pass spread (Q1–Q5: tile noise σ ≈ 0.048 W after the common part cancels, taken as independent between
tiles; `predictions-e152.json` › `precision_before_data`), the planned 95% half-widths are, at six / five / four kept passes: δ(1)
0.057 / 0.068 / 0.087 W, δ(2) 0.053 / 0.063 / 0.081 W, δ(4) 0.050 / 0.060 / 0.076 W, and the price 13 / 15 / 20 fJ (5 / 6 / 8% of p\*).
So against τ = 0.120 W, a straight ladder reads LINEAR at six passes when every |δ| ≤ about 0.06 W, and at four passes only when every
|δ| ≤ about 0.03–0.04 W; a ladder bent by a shared part of 30% of full scale (δ(1) ≈ +0.32 W) reads NONLINEAR at any of them.

## What the rules cannot say

One card, the card M7's and M8's constants are mostly from; one clock; one format (fp32); one data regime (quiet: the products zero,
the operand bus fixed). Linearity in flips is necessary for a per-flip constant to carry to other kernels, not sufficient for it to carry
to other clocks or cards: the price's scaling with clock and voltage is E72's and E118's (V² held on two cards) and the card term is
M8's; E152 tests neither. "The gate's cost" is everything that changes with the gate pattern at equal operand bits (a lane's clock gate
and branch, the gate's enable logic, the valid pipeline, the write-back mask), and E152 cannot tell those apart, only whether they add
over lanes. The single-lane tiles' live count varies (3–5 a micro-op, average 4); `gd1h` holds it at 4. The quiet tiles rest on the
denormal flush (the manual, the RTL and E93's and E127's power readings; no result is read back). The models' ladder columns rest on
an assumption (their bench terms scale with the flips) or on one term; they are reported, never scored.

## Self-test

[`selftest_e152.py`](selftest_e152.py) writes synthetic aifoundry3 passes with E78's own generator (`kinds/selftest_e78.make_pass`) after
installing E152's items and order, reduces them as `collect_e152.sh` does and scores them, in six worlds: **linear** (the ladder at p\*:
R1 LINEAR, R2 CARRIES, S1 and S2 PASS), **shared** (35% of C8\* spent whenever any lane flips: R1 NONLINEAR, concave), **convex** (C ∝
n²: R1 NONLINEAR, convex), **half** (the ladder at p\*/2: R1 LINEAR, R2 MISSES), **null** (no gate cost: R1 NOT SCORED, R2 MISSES) and
**dips** (meter dips injected: the primary removes them and keeps every pass, R1 LINEAR); it checks that three kept passes score and two
do not, that the board-power stop fires at 65.0 W and not at 64.9 W, and that a stop-test line of 30 W is refused.
[`selftest.txt`](selftest.txt): **24 of 24**. Nothing there is a measurement.

## Card budget

**At most 40 card-minutes**, from the session-start config read (the smoke's) to the session-end read, the smoke, the stop test and the
heating gates included. Expected about 34: the smoke about 1 min, the stop test about 1 min, then six passes of about 5.2 min (33
launches at E127's 8.4–10.4 s a launch) with 15 s between. `queue_e152.sh` starts a pass only if its projected end (the longest measured
pass; 360 s until the first ends) is inside **2,160 s** of the session start and before **11:20 PST**; a pass in flight is never cut. No
session starts after 10:30 PST; every run ends by 11:30 PST. It starts only with `et-who` clean on card 0, no other lane holding the
card, and the day's post in `#community-lab` rewritten to carry this reservation (`using aifoundry3 for 1 h, until ~HH:MM PST`).

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__ tools/claims-v3/e152/` to
`aifoundry3:aifoundry/tools/claims-v3/e152/` (E127's tiles, E128's guard and the checker are there since E127, E151). On aifoundry3,
from `~/aifoundry`:

```bash
bash tools/claims-v3/e152/run_e152.sh setup     # no device access: hashes, the preflight (GO), binaries, tiles, plan, a V3_DRY pass, the queue's stub test
# -> read #community-lab, then rewrite the day's post to add "using aifoundry3 for 1 h, until ~HH:MM PST"
bash tools/claims-v3/e152/run_e152.sh smoke     # the preflight again, the session-start config read (TDP 0, threshold 65), seven 2 s runs; cycles/op 546
bash tools/claims-v3/e152/run_e152.sh stoptest  # the board and die stops on live samples, no launch; both must pass
bash tools/claims-v3/e152/run_e152.sh go        # detached; refuses unless both stop tests passed; the budget rule decides; ends with the session-end read
bash tools/claims-v3/e152/run_e152.sh wait      # bounded waits only
```

Then copy `build/claims-v3/aifoundry3/kinds/p152*`, `kinds-smoke/p15201`, `kinds-stoptest/p1520*` and `build/e152-logs/` to the Intel and
run `PY=<python with numpy> nice -n 10 bash tools/claims-v3/e152/collect_e152.sh 'p152[1-9][0-9]' <copy>`; copy
`build/e152-out/2026-11-03-e152-gate-dose/` to `docs/reports/data/`, write its README (results first; registered against happened;
departures dated; linking section 11 item 6 and the critic's rank 12; what it does to predicting power and heat), push, and drop the
clause from the day's post.

## Files

All in `tools/claims-v3/e152/`: `README.md` (this), `predictions-e152.json` and `.md` and `make_predictions_e152.py` (the freeze),
`m8-bridge/` (M8's, M7's and M6's frozen predictions of E127's two tiles, by the committed predictor, and its manifest), `make_e152.py`,
`e152-tiles.json`, `SHA256SUMS` and `tiles/fp32/` (the tiles), `e152_common.py` (the items, the order, `install()`), `run_e152.py`
(run_e78.py unchanged with E152's items, the board-power stop and the stop-test line), `block_e152.sh`, `queue_e152.sh`, `run_e152.sh`
(the card side), `preflight_e152.sh` and `dmcmd-audit*.txt` (the device-command check), `reduce_e152.py` (reduce_e78.py unchanged,
labelled arms), `score_e152.py` (every rule), `collect_e152.sh`, `selftest_e152.py` and `selftest.txt`. Their sha256 are in
`predictions-e152.json` › `harness`. Data: `docs/reports/data/2026-11-03-e152-gate-dose/`.

## Amendments

*(none yet)*

*Note added after the run (not an amendment: no procedure, prediction or rule changed), Tue 3 Nov 2026, 06:2x PST: § Decision rules
gives R2's band as [236.6, 289.2] fJ; the frozen value the scorer uses is 0.9 × 262.9449 = 236.650 fJ (236.7 at one decimal) in
`predictions-e152.json` › `price`. The result: [`docs/reports/data/2026-11-03-e152-gate-dose/`](../../../docs/reports/data/2026-11-03-e152-gate-dose/README.md).*
