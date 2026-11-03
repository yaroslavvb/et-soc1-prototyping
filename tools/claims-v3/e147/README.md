# E147: single-bit prices at the open positions, in E134's frame, with M6's frozen per-flip prediction scored (Q138, aifoundry3 card 0, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, before the reservation of aifoundry3 and before any card has run one
of E147's 64 new tiles, in Q138 (lane `a3-e147-bit-prices`). **It answers the open positions of item 15 of the kinds page's
section 11**, "Smaller, and carried", whose single-bit sentence ends: "Open, in both layouts: B bits 1–5, 17–19, 21, 24–26
and 28–29; A bits 8–10, 12–15, 17–19, 21, 24–26 and 28–29 on E102's word, and above bit 7 on any other; other words; the
sign on the rail (R4); and E102-R2's bit-22 cell on a second card"
([horace-kinds-of-numbers § 11, item 15](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open);
[E134](../../../docs/reports/data/2026-11-02-e134-bit-prices-more/README.md), the run that left them, and its frame,
[`../e134/README.md`](../e134/README.md)). E147 runs every listed position in both layouts on both sides, and four A
positions above bit 7 on a second word (W67), as many as fit at the frame's registered precision inside the card budget
(§ Card budget). The sign on the rail and E102-R2's bit-22 cell are not run. Q138's goal, the owner's words of that day:
to predict the power requirement and heat generation of numeric computations as accurately as possible; so every item
also scores **M6's frozen per-flip prediction** ([Q137(m)](../../../docs/reports/data/2026-11-02-q137m-model/README.md)) at
a position no model was fitted on. The frozen numbers are in [`predictions-e147.json`](predictions-e147.json), written by
[`make_predictions_e147.py`](make_predictions_e147.py) and [`predict_m6_e147.py`](predict_m6_e147.py) from the committed
files they name, each with its sha256. Any change after this commit goes in Amendments, dated, before the data it touches.
Card: **aifoundry3 card 0 only**, 600 MHz as its boot-time TDP of 0 latches it, TDP 0 / threshold 65 °C as read, never set.
**E147 writes nothing and sends no write command of any kind**: no governor move, no TDP, threshold or clock set, no
reset, no `--reset-ms` (so not even the one write the owner's rules allow), no firmware-revisions query, no residency read.
Every device-management command it sends is a read, classified from the firmware source below (§ Device commands sent).*

## The question

E134 priced single bits in trains, each item between reads of its own zero, on aifoundry3: on B the all-in layout's
accumulator swing starts at bit 8 and grows to 6× at bit 16 while the balanced price stays flat (83–113 fJ); on A the flip
alone is the price at the low bits and depends on the base word, where the fixed bench's Booth recoder puts it. E102 had
read ten positions on aifoundry1 card 1. **Thirty positions an operand per layout are still unread in both layouts on
any card** (E134's correction C2). They are the ones a model for whole numbers has to cover: the top of the mantissa,
where E65's all-in list reaches 2.8–4.2 W a bit, the exponent, which E102 found reverses the layouts (balanced dearer), and
B's lowest bits. E147 measures each in both layouts in one session, with E134's frame unchanged but for one registered line
(the meter-dip line, below), and asks three things of them:

1. **The table.** Every position's price per flipped bit, all-in and balanced, on each side: the per-position table a next
   model uses. Reported for every item, with its interval.
2. **Do the mechanisms E134 and E102 found carry to these positions?** B's swing absent below bit 8 (R1); the exponent's
   reversal on both sides (R2, R3); A's word effect above bit 7, in the bench's direction (R4) and in E134's digit reading
   (R5).
3. **Does M6 predict single bits where nothing was fitted?** M6's fit left out every single-bit ladder (E134's included);
   post hoc it reads E134's 54 single-bit steps to 0.098 W rms (M5 0.093, the bench 0.148; `m6_on_e134` below, from
   committed files). M1 scores its frozen steps at E147's 68 new items against its own claimed accuracy.

## The tiles

73 fp32 tiles in the host's `--values file:` layout (2,048 bytes), written by [`make_e147.py`](make_e147.py) with E102's own
generator functions (`tools/claims-v3/kinds/make_e102.py`, `make_hlp.py`), as E134's: `e147/tiles/fp32/<name>.bin`, manifest
[`e147/e147-tiles.json`](e147/e147-tiles.json) (each tile's sha256, its halves', its designed flips, its Booth digit changes
and digit class, and its real-accumulator counts).

| side | word | tiles | held operand | flips an op | source |
|---|---|---|---|---:|---|
| A | W79 `0x3fbd207c` (E79's, E102's, E134's) | zero `aq`; `aj_<j>` (E67's construction, flip = i & 1) and `ap_<j>` (E102's balanced A layout, flip = (i XOR g) & 1) at **8–10, 12–15, 17–19, 21, 24–26, 28–29** | B = 1.0 | 2,048 / 1,920 | `aq` E102's byte for byte; 32 new |
| A | W67 `0x3fbbc9e4` (E67's) | zero `a67q`; `a67j_<j>` and `a67p_<j>` at **9, 17, 18, 19** | B = 1.0 | 2,048 / 1,920 | `a67q` and `a67j_9`, `_17`, `_18`, `_19` are **E67's own tiles**, byte for byte the files E67's host dumped on this card; 4 new |
| B | E79's eight B words | zero `hq`; `bj_<j>` (E65's construction, flip = hi(j)) and `bp_<j>` (E79's balanced `jgp`) at **1–5, 17–19, 21, 24–26, 28–29**; and `bj_16`, `bp_16` | A = 1.0 | 4,096 / 3,968 | `hq` E102's; `bj_16`, `bp_16` E134's, byte for byte (the session link); 28 new |

Every exponent flip lowers an exponent of 127 (to 125, 123, 119, 95 or 63): no infinity, NaN, subnormal or zero word
(`make_e147.py --check` asserts it, with E134's checks: the designed counts, the quiet operand never flips, every item
differs from its own zero in its own bit of its own operand alone, the balanced layouts give every accumulator the same
products and the all-in layouts two sets, and every reused tile equals the file it reuses).

**Why these four W67 positions, chosen from the words alone before any count.** E134 read one A bit's price on two words
and found it follows the radix-4 Booth digit the flip changes: dear where the flip moves a digit between zero-or-positive
and negative, cheap where the digit stays on its side. `make_e147.digit_class` reads that class from each word's bits
(`e147-tiles.json` › `a67_choice`). Above bit 7, at the positions W79 runs here, the two words' classes differ at three:
**bit 9** (W79 crosses, W67 does not: the reading says W79 dearer), **17** (the same) and **18** (W67 crosses, W79 does not:
W67 dearer); and at **19** both words make the same two digit changes (d9 −1 → +1, d10 0 → −1), so the reading says the
same price. Four is the most W67 positions the card budget holds at four blocks of each kind (§ Card budget).

## What runs

| | E134 (the frame) | E147 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type fp32 --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions | the same | E78's protocol |
| protocol | trains: `--preheat 0 --target 200 --quiet-s 0.2 --burnin 0` | the same | |
| blocks | A 55 runs, B 43; pairs drawn at random | **A** (14710–14719): 3 settling runs (never used), then W79's 32 items in four segments of four pairs and W67's 8 in one, the W67 segment's place drawn: each `[z p p z p p z p p z p p z]` with the segment's own zero: **68 runs**. **B** (14720–14729): 3 settling runs of `hq`, then `hq` between every pair of the 30 B items: **49 runs**. **Every pair is a bit's two layouts** (its all-in and balanced twins, the order inside the pair drawn, the pairs shuffled: E147 change 2) | every item's nearest zero read on each side is its own zero (`e147_common.check_order`, asserted for all 20 block numbers); twins share their two zero reads, so a bit's swing and ratio are read inside one stretch of a train. The self-test (below) found that with E134's random pairs, E147's B blocks, which hold steps of 3–4.5 W, put the carry-over of a large step on random neighbours: the swing's half-width at B's low bits was 0.12–0.15 W at four blocks; with twins it is 0.07–0.10 W, and the word contrasts' 0.11–0.15 W falls to 0.07–0.10 W |
| order | `Random("E134\|aifoundry3\|<pass>")` | `Random("E147\|aifoundry3\|<pass>")`, `e147_common.pass_order` | |
| sequence | A B A B A B A B B A | **14710 (A) 14720 (B) 14711 (A) 14721 (B) 14712 (A) 14722 (B) 14713 (A) 14723 (B)**; the budget rule decides how many run | three kept blocks of each kind after the sixth; the fourth of each is the margin against a set-aside |
| smoke | 7 items, 2 s each | **14701**: `aq`, `aj_19`, `a67q`, `a67j_9`, `hq`, `bj_21` (the largest B step), `bp_26`, 2 s each, after the session-start config read; read for cycles per op (546), the tile dumps and the board level only | |
| stop test | — | **14702** (board) and **14703** (die), after the smoke, before the queue: § Stops | E139's stop never read a sample |
| primary reduction | E78's `reduce_e78.py` **unchanged** via the wrapper with E82 A2's dips removed at a **4 W** line; `score`: the board's `p_raw` over [t0+1 s, t0+3 s), no temperature term, minus the item's own zero interpolated in time, over designed flips × the run's rate | the same, **with the dip line at 2 W** (`reduce_e147.py --drop-dips --dip-w 2.0`, E147 change 1) | E134's correction C1: two 3–4 W meter dips under the 4 W line set aside its first A block and widened its R2, and "a re-run that would decide it needs a dip rule, registered first, that catches 2–4 W dips"; at 2 W E134's own blocks all pass, every B number is unchanged and 22 more samples go of 22,560 |
| arms (reported) | rail, p80, dips kept, gates off | the same, plus **E134's 4 W line** (the frame arm) | a verdict that moves at an arm is marked arm-sensitive |
| gates | E78's per-run and pass gates; the train gate (a zero's interior read > 0.25 W off its neighbours' line sets the block aside) | the same | |
| stops | die ≥ 70 °C, board ≥ 65 W | the same, each read from the live sampler file before every launch (§ Stops) | |
| config reads | `ettelem config` under the card lock, `timeout 10`, at both ends of every block and the smoke, and the session-end read | the same, and at both ends of each stop test | the brief's §17 |
| data | raw `~/aifoundry/build/claims-v3/aifoundry3/kinds/p134<nn>/` | raw `kinds/p147<nn>/`, `kinds-smoke/p14701`, `kinds-stoptest/p1470[23]`, logs `build/e147-logs/`; results `docs/reports/data/2026-11-02-e147-bit-prices-rest/` | |

**What is E78's and E134's, byte for byte.** `run_e147.py`, `reduce_e147.py` and `run_e147.sh setup` check
`tools/claims-v3/lib.sh` `033d0776…`, `kinds/e78_common.py` `c58923a5…`, `kinds/run_e78.py` `f3efd783…`, `kinds/reduce_e78.py`
`6a158cee…` and `kinds/kinds.json` `9586568f…` (E134's and E130's registered values, asserted equal by
`make_predictions_e147.py`) against `predictions-e147.json` › `harness.reused_unchanged_sha256` and refuse on any difference.
`e147_common.install()` replaces `load_items` (E78's items plus E147's 73 tiles) and `pass_order` on the shared
`e78_common` module in memory, then `run_e78.main()` / `reduce_e78.main()` run as they are. Ported from E134 with marked
changes: `e147_common.py`, `run_e147.py`, `block_e147.sh`, `queue_e147.sh`, `run_e147.sh`, `reduce_e147.py` (the dip line),
`collect_e147.sh`; `score_e147.py` is E134's `Book`, unchanged, with E147's rules. Binaries: the tree's own, no rebuild, the
two E134 registered and ran (`sparsity_host` `20e760c2…`, `ettelem` `16037641…`); `run_e147.sh setup` checks both hashes.

## Device commands sent

*His rule of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send,
classified from the firmware source of the running build, READ or WRITE; the only write allowed is the statistics reset,
and **E147 does not send it**.* aifoundry3 reports release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0 (E79); the source read is
the open et-platform tree at `836a4ab`, the version-matched public revision. Paths are under
`device-bootloaders/src/ServiceProcessorBL2/`. The sending code is E134's, unchanged (lib.sh, the same `ettelem` binary,
`block_e147.sh`'s config reads and sampler call as `block_e134.sh`'s, `queue_e147.sh`'s one session-end read as
`queue_e134.sh`'s; the stop tests are blocks with the same reads), so the list is E134's, which its run and its verifier
confirmed:

| # | command | sent by | firmware path at `836a4ab` | what it touches | class |
|---|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config` (each block's and stop test's start and end, the smoke, the session-end read) | `services/thermal_pwr_mgmt.c:613` | copies one byte of SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | `ettelem config` | `thermal_pwr_mgmt.c:665` | copies SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | `ettelem config` | `thermal_pwr_mgmt.c:551` | copies SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` (10 Hz) | `services/perf_mgmt.c:276` → `driver/io_pll.c:932` | PLL register reads, stored in SP RAM | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | `thermal_pwr_mgmt.c:1142` → `driver/pmic_controller.c:1473`, `:254` `i2c_read` | PVT reads and **two PMIC voltage-register reads** | **READ**, a PMIC voltage read, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample`; lib.sh `drain_mgmt` only after a sampler fails to start twice or ignores SIGTERM for 30 s | `thermal_pwr_mgmt.c:984` | copies SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` → `thermal_pwr_mgmt.c:2780` | copies SP RAM; resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; lib.sh `die_c` | `thermal_pwr_mgmt.c:732` | PVT reads, cached in SP RAM | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` | `thermal_pwr_mgmt.c:1010` → `pmic_controller.c:1473` | **nine PMIC voltage-register reads** | **READ**, PMIC voltage reads, allowed by his rule of 2 Nov |

**Never sent by E147** (each checked in the code that runs): `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset (`ettelem`
sends it only with `--reset-ms` > 0; `block_e147.sh:120`, the one `start_sampler` call, passes the output file and the
duration and nothing else, and lib.sh's `die_c` / `clock_mhz` call `ettelem sample --seconds 1 --every-ms 500` literally);
`DM_CMD_SET_DM_TRACE_CONFIG` (`ettelem loglevel`, which nothing calls); `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`; any
residency read; any `DM_CMD_SET_*`; any governor, TDP, threshold or clock set; any reset, power cycle, PCIe, driver, firmware
or OTA operation. **The host program** (`sparsity_host`) opens the ops node only (`workloads/sparsity/host/main.cpp:172`
`createPcieDeviceLayer(true, false)`): no management command. Helpers that open no device node: `et-who` / `et-holders`,
`et-lab-manifest`, `flock`, `timeout`, `ps`, `who`. The `ettelem` binary is `build/ettelem/ettelem` `16037641…`, built from
lab commit `de262730`'s `tools/ettelem/ettelem.cpp`, whose `config()`, `sample()`, `Dm::get()` and `Dm::resetStats()` are
byte-identical to the reviewed source's (E134's correction C6).

**The preflight checker, Q136(w)'s [`tools/claims-v3/dmcmd_audit.py`](../dmcmd_audit.py)** (unchanged since `32e9c109`,
sha256 `f29e91ca…`, table `50168632…`), on `tools/claims-v3/e147/` (every file), `lib.sh`, `run_e78.py`, `e78_common.py` and
`reduce_e78.py`, run from the top of the lab repository ([`dmcmd-audit.txt`](dmcmd-audit.txt)):
- with no allow-list and no exception: **NO-GO, 1 disallowed**: the nine READs above, PMIC access on `GET_ASIC_VOLTAGE` and
  `GET_MODULE_VOLTAGE` only (reads), and the conditional `STATS_RESET` at `lib.sh:154` (`start_sampler` forwards `"$@"`),
  exactly as for E134;
- with the reviewed exception, `--except 'tools/claims-v3/lib.sh:154:STATS_RESET=block_e147.sh:120, the only start_sampler
  call E147 makes, passes the output file and the duration and nothing else, so no --reset-ms is forwarded'`: **GO, 0
  disallowed**;
- with `--deny-pmic-read` too: NO-GO on the voltage-read lines only, as it should be (the reads his rule allows).

**Verdict before the first launch: GO.** No disallowed or unclassified write is in the list. **The build caveat binds as
for E130 and E134:** aifoundry3 runs a thermal firmware build that is not public, so each READ's class rests on `836a4ab`'s
handlers. If `run_e147.sh setup` finds either binary's sha256 changed, or the session-start config read or the smoke's
telemetry comes back in another form than E134's run recorded (an error code, a missing field), the list does not describe
what would run: that is NO-GO, and the session stops there.

## Stops

E147 runs no heater, no anchor and no random tile: every run is a constant-operand fp32 tile or one bit away from one, at
most about 4.5 W above its own zero (E65's all-in list at bit 21, 4.16 W; the bench's largest step here is in
`predictions-e147.json`). E134 read at most 40.81 W on the board and 62 °C on the die on this card in the same frame.
Registered stops, with margin: **a die reading ≥ 70 °C** ends the block (E78's `--max-c`; its second check at 80 °C reads
the minion shires' PVT average) and **a board reading ≥ 65 W** at any of E78's pre-launch reads writes the block's STOP file
and ends it with E78's exit 6 (`run_e147.py`). Either stop ends the queue. Nothing in E147 drives the card toward the PMIC's
over-power or over-temperature limits; no power cycle, reset or outlet cycle is part of any path.

**Both stops read live samples.** `run_e78.py`'s `reading()` takes the newest line of `--tel-live`, which `block_e147.sh`
points at the sampler's own output while it is being written (`$OUT/telemetry.jsonl.raw`; lib.sh copies it to
`telemetry.jsonl` only when the sampler stops), before every launch, and stops the pass when that line is older than 3 s.
The die stop reads that line's minion-shire reading; the board stop wraps the same `last_sample()` call, so it reads the
same line's `board_w`, and it logs the first line it reads (its age and board watts) in every block's `runner.err`. (E139's
65 W stop watched `telemetry.jsonl`, written only at a pass's end, and never read a sample.)

**The stop test, registered, run once in the session after the smoke and before the queue.** Two blocks with one item
(`hq`), each a full block (config reads, sampler, the card lock) with one line moved below what the card reads at idle:
**14702** the board line at 1 W (`E147_STOPTEST=board`, refused above 30 W) and **14703** the die line at 20 °C
(`--max-c 20`). Each must end the runner at its first pre-launch reading, before any launch: exit 6, the stop's own line in
`STOP` ("E147 board-power stop: board_w … W >= 1.0 W"; "die reading … C … >= cap 20.0 C"), no `run` mark and no record,
and for the board test a first line at most 3 s old. `block_e147.sh --stoptest` writes the verdict to `stoptest.json`. **If
either fails, the queue does not start** (NO-GO: the registered stops would not be known to act).

## The frozen predictions

Each item's step over its own zero, board W on this card. **M6** is Q137(m)'s frozen model (`m6.json` `87c17e08…`),
computed mechanically by [`predict_m6_e147.py`](predict_m6_e147.py) from the bench's counts of E147's tiles and the tiles'
bytes, as `predict_blind4.py` computes blind pool 4's: D(item) − D(own zero), at M6's rate. **M5** the same way (reported).
**bench** is E134's model: the fixed RTL bench (Q132(b)'s `vpu_top`, `-fno-dfg`) run on E147's tiles on the Intel
([`docs/reports/data/2026-11-02-e147-bit-prices-rest/bench/`](../../../docs/reports/data/2026-11-02-e147-bit-prices-rest/bench/),
0 accumulator mismatches; its counts of `aq` and `hq` equal E134's), at E92's frozen coefficients, scale 1. **position-only**
is E67's list (A, W67's word, all-in) or E65's (B), at the item's bit, scaled to its designed flips. The **count model**
prices the real accumulators' parted bits (B's swing only, reported).

**A, W79, each item's step, W** (`predictions-e147.json` › `items` › `pred_W`; M6's price per flip in fJ beside it):

| bit | `aj` M6 | `aj` M6 fJ | `aj` bench | `aj` position-only | `ap` M6 | `ap` M6 fJ | `ap` bench | swing (aj − ap × 2048/1920): M6 | bench | real-sum result bits an op, all-in over balanced |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 0.270 | 117 | 0.309 | 0.376 | 0.254 | 118 | 0.290 | -0.001 | -0.001 | 0 |
| 9 | 0.789 | 344 | 0.940 | 0.754 | 0.740 | 344 | 0.882 | -0.001 | -0.001 | 1,024 |
| 10 | 0.555 | 242 | 0.585 | 0.851 | 0.258 | 120 | 0.298 | +0.280 | +0.267 | 7,360 |
| 12 | 0.641 | 279 | 0.671 | 0.970 | 0.291 | 135 | 0.333 | +0.330 | +0.315 | 9,872 |
| 13 | 1.730 | 753 | 1.895 | 2.003 | 1.089 | 506 | 1.266 | +0.568 | +0.545 | 14,576 |
| 14 | 0.858 | 374 | 0.884 | 1.471 | 0.312 | 145 | 0.356 | +0.525 | +0.505 | 23,668 |
| 15 | 1.646 | 717 | 1.772 | 2.444 | 0.803 | 373 | 0.948 | +0.789 | +0.761 | 29,006 |
| 17 | 1.835 | 799 | 1.958 | 1.504 | 0.790 | 367 | 0.935 | +0.992 | +0.960 | 25,012 |
| 18 | 1.753 | 764 | 1.738 | 2.481 | 0.266 | 123 | 0.304 | +1.470 | +1.414 | 45,946 |
| 19 | 2.987 | 1301 | 3.038 | 2.669 | 0.773 | 359 | 0.915 | +2.163 | +2.062 | 48,802 |
| 21 | 2.587 | 1127 | 2.504 | 2.629 | 0.356 | 166 | 0.383 | +2.207 | +2.095 | 40,806 |
| 24 | 0.522 | 227 | 0.393 | 0.611 | 1.194 | 555 | 1.172 | -0.752 | -0.857 | -668 |
| 25 | 0.403 | 176 | 0.303 | 0.359 | 1.523 | 708 | 1.553 | -1.222 | -1.353 | 879 |
| 26 | 0.582 | 253 | 0.440 | 0.662 | 1.586 | 737 | 1.607 | -1.110 | -1.274 | 8,275 |
| 28 | 0.833 | 363 | 0.628 | 0.730 | 1.393 | 647 | 1.347 | -0.653 | -0.809 | 10,837 |
| 29 | 0.880 | 383 | 0.667 | 0.875 | 1.325 | 616 | 1.279 | -0.534 | -0.698 | 6,741 |

**A, the word above bit 7, W67 − W79, W** (`contrasts_pred_W`; the reading is E134's digit class, from the words alone):

| bit | W67 class | W79 class | reading | all-in: bench | all-in: M6 | all-in: position-only | balanced: bench | balanced: M6 | `a67j` E67 measured (this card) |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 9 | same | cross | W79 dearer | -0.436 | -0.310 | +0.000 | -0.612 | -0.505 | 0.754 ± 0.382 |
| 17 | same | cross | W79 dearer | -0.364 | -0.234 | +0.000 | -0.607 | -0.503 | 1.504 ± 0.313 |
| 18 | cross | same | W67 dearer | +1.145 | +0.824 | +0.000 | +1.600 | +1.324 | 2.481 ± 0.389 |
| 19 | cross | cross | the same | -0.178 | -0.192 | +0.000 | +0.072 | +0.078 | 2.669 ± 0.240 |

**B, each item's step, W, and the swing** (all-in minus balanced × 4096/3968):

| bit | `bj` M6 | `bj` M6 fJ | `bj` bench | `bj` E65 (position-only) | `bp` M6 | `bp` M6 fJ | `bp` bench | swing: M6 | bench | count model | real-sum result bits an op, all-in over balanced |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.567 | 123 | 0.531 | 0.512 | 0.549 | 123 | 0.514 | +0.000 | +0.000 | +0.000 | 0 |
| 2 | 0.446 | 97 | 0.433 | 0.406 | 0.431 | 97 | 0.419 | +0.000 | -0.000 | +0.000 | 0 |
| 3 | 0.450 | 98 | 0.438 | 0.482 | 0.436 | 98 | 0.425 | +0.000 | -0.000 | +0.000 | 0 |
| 4 | 0.448 | 98 | 0.436 | 0.484 | 0.434 | 98 | 0.422 | +0.000 | -0.000 | +0.000 | 0 |
| 5 | 0.453 | 99 | 0.441 | 0.461 | 0.438 | 99 | 0.427 | +0.000 | +0.000 | +0.000 | 0 |
| 17 | 2.951 | 643 | 2.870 | 2.838 | 0.589 | 132 | 0.589 | +2.344 | +2.262 | +3.682 | 67,973 |
| 18 | 3.167 | 690 | 3.074 | 3.152 | 0.524 | 118 | 0.526 | +2.626 | +2.531 | +4.595 | 84,856 |
| 19 | 3.407 | 742 | 3.304 | 3.717 | 0.660 | 148 | 0.660 | +2.725 | +2.623 | +4.426 | 81,974 |
| 21 | 4.428 | 964 | 4.277 | 4.161 | 0.776 | 175 | 0.765 | +3.626 | +3.487 | +5.238 | 91,758 |
| 24 | 0.903 | 197 | 0.692 | 0.794 | 2.586 | 581 | 2.634 | -1.767 | -2.026 | -1.275 | 1,337 |
| 25 | 0.755 | 164 | 0.580 | 0.684 | 2.612 | 587 | 2.676 | -1.941 | -2.183 | -1.354 | 1,127 |
| 26 | 1.015 | 221 | 0.780 | 0.867 | 2.583 | 581 | 2.620 | -1.651 | -1.924 | -0.949 | 8,496 |
| 28 | 1.515 | 330 | 1.154 | 0.952 | 2.564 | 576 | 2.503 | -1.132 | -1.430 | -0.299 | 16,911 |
| 29 | 1.571 | 342 | 1.202 | 1.061 | 2.429 | 546 | 2.368 | -0.937 | -1.242 | -0.678 | 8,719 |
| 16 (link) | 2.603 | 567 | 2.534 | 2.794 | 0.559 | 126 | 0.564 | +2.026 | +1.951 | +3.521 | 64,954 |

From these, frozen: **R4's bits** (bench |W67 − W79| ≥ 0.10 W) are [9, 17, 18, 19]; **R5's** signed bits {'9': -1, '17': -1, '18': 1} and its same-change bit 19; **M1's line** 0.2448 W over 68 new items; M6's one-row band ±0.4799 W (reported).

**M6 before this run, post hoc on committed files** (`m6_on_e134`: M6's frozen steps for E134's 54 items, from E134's
committed counts, against E134's measured steps, `scored.json` › `primary`; M6 was frozen after E134's data was public, but
its fit left out E134's rows): rms 0.098 W (bias −0.034) over all 54; A all-in 0.107, A balanced 0.105, B all-in 0.107, B
balanced 0.057. M5 0.093; the bench at E92's coefficients 0.148.

## Decision rules

All on the primary (board `p_raw`, own zeros, dips removed at the 2 W line, E78's gates and the train gate) over kept
blocks. A contrast is a per-block combination of items' W, paired inside each block; its 95% interval is t(n − 1) × sd / √n
over blocks. A ratio is the ratio of the per-block means of two items' fJ per flipped bit, with its 95% Fieller interval,
paired. The swing is all-in minus balanced × 4096/3968 (B) or × 2048/1920 (A). **A rule that reads a kind of block with
fewer than 3 kept blocks of that kind is NOT SCORED.**

| rule | what | verdicts |
|---|---|---|
| **E147-R1** | B's low bits carry no accumulator swing: the swing's watts at B bits 1–5, their mean (paired by block: the registered contrast) and each bit's | **FLAT** if the mean's interval lies inside ±0.10 W and no bit's lower bound exceeds 0.10 W; **SWING** if the mean's or any bit's lower bound > 0.10 W; else INCONCLUSIVE |
| **E147-R2** | B's exponent reverses the layouts: all-in / balanced per flipped bit at B bits 24, 25, 26, 28, 29 | **INVERTED** if every upper bound < 1; **NOT INVERTED** if any lower bound ≥ 1; else INCONCLUSIVE |
| **E147-R3** | A's exponent reverses the layouts on W79: the same at A bits 24, 25, 26, 28, 29 | as R2 |
| **E147-R4** | the bench's word differences above bit 7 (E134-R5's form): W67 − W79, all-in, at every bit of 9, 17, 18, 19 where the bench puts it at 0.10 W or more (`rules.E147-R4.bits`) | **AGREES** if every bit whose interval excludes zero has the bench's sign and at least half of the bits resolve; **DISAGREES** if any resolved bit has the other sign; else INCONCLUSIVE |
| **E147-R5** | E134's digit-class reading above bit 7: W67 − W79, all-in, negative at 9 and 17 and positive at 18 (the words' classes, above), and inside ±0.10 W at 19 (the same digit changes on both words) | **HOLDS** if every resolved signed bit has the reading's sign, at least two of the three resolve, and bit 19's interval lies inside ±0.10 W (E134-R2's SAME band); **FAILS** if a resolved signed bit has the other sign or bit 19's interval lies wholly outside ±0.10 W; else INCONCLUSIVE |
| **E147-M1** | **M6's frozen step at every new position**: rms of measured − M6 over E147's 68 new items (both sides, both layouts, both words), board W | **HOLDS** if the rms ≤ 0.245 W, M6's own nested rms for fp32 on aifoundry3 (`m6.json`); **FAILS** if above; NOT SCORED under 3 kept blocks of either kind or fewer than 34 items |
| **E147-S1** | the session link: E134's `bj_16` and `bp_16`, byte for byte, against E134's primary values (2.789 and 0.448 W) | **PASS** if both lie within max(0.15 W, 25% of E134's value, 2 × E134's s.e.) of it; else FAIL |

**Reported, never a verdict** (`scored.json`, `results.md`): every item's W and fJ per flip with its interval and blocks —
**the per-position table**; every ratio all-in / balanced; every swing, on both sides, beside the count model, the bench
and M6; every word difference, all-in and balanced; each frozen model's rms and bias over each list (all new items, the
mantissa and exponent positions apart, each side and layout); M6's largest misses; M6's per-flip price (fJ) against the
measured one; E67's four tiles above bit 7 against E67's list (E134-S1's bands); the zeros' scatter about their
neighbours' line; each verdict at every arm.

**Why these lines, before the data.** R1's band is E134-R4's ±0.10 W "none" band; its SWING line asks for a lower bound
clear of that band, so a small carry-over cannot read as a swing. It reads the five bits' mean because the hypothesis is the
same at each (the real sums part at no bit below 8: 0 result-path bits an op over the zero at bits 1–5, frozen), and the
self-test showed that requiring all five intervals inside the band at four blocks almost never decides; each bit still
guards SWING. R2's and R3's line is 1, the layouts' parity: E102 read
0.30–0.52 at three exponent bits on each side, so INVERTED says the reversal holds at every exponent bit run. R4 is E134-R5
unchanged, at the bits the bench says should move (all four here). R5 tests the reading E134 drew post hoc, at positions
chosen for it before any count. At bit 19 the reading (the same digit changes, so the same price) and the bench (−0.18 W)
part, so R5 can tell them apart: its band is E134-R2's SAME band, ±0.10 W. M1's line
is the accuracy M6 claims for a kinds tile on this card; a single-bit step is a difference of two rows of one session, so
M6 should do at least as well. S1 keeps E134-S1's bands.

**What I expect, frozen so it can be wrong:** R1 FLAT; R2 INVERTED; R3 INVERTED; R4 AGREES; R5 INCONCLUSIVE (the bench
puts bit 19 at −0.18 W, and E134 found the bench's word differences 0.65–0.71 of the card's, so about −0.12 W: between the
reading's 0 and the band's edge); M1 HOLDS; S1 PASS.

**The statement the page gets, decided now.** R1 FLAT with E134's R4: "on B the swing is absent below bit 8 and present
from 8". R2 and R3 INVERTED: "at every exponent bit run, on both sides, the balanced layout is dearer than all-in, so an
exponent's price depends on whether a workload's sums follow its products (E102's reading, at every exponent bit run)".
R4 AGREES: "above bit 7 too, one A bit's price is its word's, in the bench's direction". R5 HOLDS: "and the digit a flip
changes sets it: where both words make the same digit changes they cost the same"; R5 FAILS: "the digit class is not the
whole story: the same digit changes cost differently on two words (by X W at bit 19)".
M1 HOLDS: "M6, never fitted on single bits, predicts their steps at new positions to X W rms"; FAILS: "M6 misses single
bits at new positions by X W rms, beyond the 0.245 W it claims; its largest misses are …". INCONCLUSIVE is stated as such
with the intervals. **Only tiles that ran are scored. No tile is dropped, re-drawn or added after the first block, and no
prediction, threshold, band or rule changes.**

## Precision, before the data

[`selftest_e147.py`](selftest_e147.py) builds per-run tables on the real block orders and sequence (each item at its truth
over its own zero, E134's simulated run unchanged: a warm-up curve of 2 W amplitude and τ = 45 s from each block's start, a
random walk of 0.01 W a run, a carry-over of 5% of the previous run's step, white noise σ) and scores them with
`score_e147.py`. Worlds: **bench** (every item at the bench's step), **m6** (every item at M6's), **position** (A items at
E67's list for their bit, the same on both words: the word does nothing), **scaled** (the bench with A's word differences
at E134's measured 0.67 of the bench's and B's swing 1.15 × the bench's), and **bench_c3**, the bench world at a 3%
carry-over: E134's own board read **2.8 ± 0.8% per W of the preceding step** in its zero reads, post hoc
([`carry_e134.py`](carry_e134.py), on E134's committed `runs.csv`), and E147's B blocks hold steps of 3–4.5 W, so the
carry-over is the noise that grows most here. [`selftest.txt`](selftest.txt), 40 sessions a world:

| blocks kept | world | σ, W a run | R1 | R2 | R3 | R4 | R5 | M1 | S1 | median half-widths, W (word contrast; B swing 1–5; B swing 17–21; A item; B item) | median M1 rms, W |
|---|---|---:|---|---|---|---|---|---|---|---|---:|
| A4 B4 (the budget's expectation) | bench | 0.025 | FLAT 40 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 28, FAILS 12 | HOLDS 40 | PASS 40 | 0.077; 0.094; 0.163; 0.064; 0.089 | 0.139 |
| A4 B4 (the budget's expectation) | bench | 0.035 | FLAT 38, INCONCLUSIVE 2 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 31, FAILS 9 | HOLDS 40 | PASS 40 | 0.096; 0.099; 0.182; 0.077; 0.111 | 0.140 |
| A4 B4 (the budget's expectation) | m6 | 0.025 | FLAT 40 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 25, FAILS 15 | HOLDS 40 | PASS 40 | 0.071; 0.095; 0.175; 0.062; 0.095 | 0.044 |
| A4 B4 (the budget's expectation) | m6 | 0.035 | FLAT 33, INCONCLUSIVE 6, NOT SCORED 1 | INVERTED 39, NOT SCORED 1 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 28, FAILS 12 | HOLDS 39, NOT SCORED 1 | PASS 39, NOT SCORED 1 | 0.094; 0.119; 0.189; 0.078; 0.114 | 0.047 |
| A4 B4 (the budget's expectation) | position | 0.025 | FLAT 40 | INVERTED 40 | INCONCLUSIVE 37, NOT INVERTED 3 | INCONCLUSIVE 40 | INCONCLUSIVE 40 | FAILS 40 | PASS 40 | 0.090; 0.095; 0.165; 0.070; 0.094 | 0.639 |
| A4 B4 (the budget's expectation) | position | 0.035 | FLAT 36, INCONCLUSIVE 4 | INVERTED 40 | INCONCLUSIVE 34, NOT INVERTED 6 | INCONCLUSIVE 37, AGREES 2, DISAGREES 1 | INCONCLUSIVE 38, FAILS 1, HOLDS 1 | FAILS 40 | PASS 40 | 0.112; 0.108; 0.181; 0.084; 0.111 | 0.639 |
| A4 B4 (the budget's expectation) | scaled | 0.025 | FLAT 38, INCONCLUSIVE 2 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 38, FAILS 2 | HOLDS 40 | PASS 40 | 0.077; 0.099; 0.190; 0.064; 0.112 | 0.191 |
| A4 B4 (the budget's expectation) | scaled | 0.035 | FLAT 32, INCONCLUSIVE 6, NOT SCORED 2 | INVERTED 38, NOT SCORED 2 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 37, HOLDS 3 | HOLDS 38, NOT SCORED 2 | PASS 38, NOT SCORED 2 | 0.096; 0.119; 0.220; 0.078; 0.129 | 0.191 |
| A4 B4 (the budget's expectation) | reading | 0.025 | FLAT 39, NOT SCORED 1 | INVERTED 39, NOT SCORED 1 | INVERTED 40 | AGREES 37, DISAGREES 3 | HOLDS 23, INCONCLUSIVE 17 | HOLDS 39, NOT SCORED 1 | PASS 39, NOT SCORED 1 | 0.074; 0.095; 0.175; 0.066; 0.094 | 0.140 |
| A4 B4 (the budget's expectation) | reading | 0.035 | FLAT 34, INCONCLUSIVE 6 | INVERTED 40 | INVERTED 40 | AGREES 39, DISAGREES 1 | INCONCLUSIVE 29, HOLDS 11 | HOLDS 40 | PASS 40 | 0.106; 0.112; 0.189; 0.080; 0.113 | 0.142 |
| A4 B4 (the budget's expectation) | bench_c3 | 0.025 | FLAT 40 | INVERTED 40 | INVERTED 40 | AGREES 40 | FAILS 21, INCONCLUSIVE 19 | HOLDS 40 | PASS 40 | 0.072; 0.067; 0.103; 0.054; 0.068 | 0.132 |
| A4 B4 (the budget's expectation) | bench_c3 | 0.035 | FLAT 39, INCONCLUSIVE 1 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 31, FAILS 9 | HOLDS 40 | PASS 40 | 0.091; 0.084; 0.125; 0.069; 0.083 | 0.133 |
| A3 B3 | bench | 0.025 | FLAT 36, INCONCLUSIVE 3, NOT SCORED 1 | INVERTED 39, NOT SCORED 1 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 31, FAILS 9 | HOLDS 39, NOT SCORED 1 | PASS 39, NOT SCORED 1 | 0.110; 0.127; 0.281; 0.090; 0.134 | 0.140 |
| A3 B3 | bench | 0.035 | FLAT 31, INCONCLUSIVE 6, NOT SCORED 3 | INVERTED 37, NOT SCORED 3 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 38, FAILS 2 | HOLDS 37, NOT SCORED 3 | PASS 37, NOT SCORED 3 | 0.144; 0.156; 0.306; 0.116; 0.157 | 0.142 |
| A3 B3 | m6 | 0.025 | FLAT 35, INCONCLUSIVE 5 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 28, FAILS 12 | HOLDS 40 | PASS 40 | 0.098; 0.135; 0.276; 0.092; 0.135 | 0.048 |
| A3 B3 | m6 | 0.035 | FLAT 24, NOT SCORED 11, INCONCLUSIVE 5 | INVERTED 29, NOT SCORED 11 | INVERTED 39, NOT SCORED 1 | AGREES 39, NOT SCORED 1 | INCONCLUSIVE 34, FAILS 5, NOT SCORED 1 | HOLDS 28, NOT SCORED 12 | PASS 29, NOT SCORED 11 | 0.148; 0.168; 0.294; 0.110; 0.177 | 0.049 |
| A3 B3 | position | 0.025 | FLAT 36, NOT SCORED 2, INCONCLUSIVE 2 | INVERTED 38, NOT SCORED 2 | INCONCLUSIVE 40 | INCONCLUSIVE 38, DISAGREES 2 | INCONCLUSIVE 40 | FAILS 38, NOT SCORED 2 | PASS 38, NOT SCORED 2 | 0.146; 0.137; 0.277; 0.100; 0.136 | 0.640 |
| A3 B3 | position | 0.035 | FLAT 30, NOT SCORED 6, INCONCLUSIVE 4 | INVERTED 34, NOT SCORED 6 | INCONCLUSIVE 36, NOT INVERTED 4 | INCONCLUSIVE 38, DISAGREES 2 | INCONCLUSIVE 39, FAILS 1 | FAILS 34, NOT SCORED 6 | PASS 34, NOT SCORED 6 | 0.181; 0.168; 0.274; 0.121; 0.165 | 0.639 |
| A3 B3 | scaled | 0.025 | FLAT 31, NOT SCORED 8, INCONCLUSIVE 1 | INVERTED 32, NOT SCORED 8 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 39, HOLDS 1 | HOLDS 32, NOT SCORED 8 | PASS 32, NOT SCORED 8 | 0.108; 0.134; 0.306; 0.089; 0.158 | 0.190 |
| A3 B3 | scaled | 0.035 | FLAT 28, INCONCLUSIVE 7, NOT SCORED 5 | INVERTED 35, NOT SCORED 5 | INVERTED 39, NOT SCORED 1 | AGREES 39, NOT SCORED 1 | INCONCLUSIVE 39, NOT SCORED 1 | HOLDS 34, NOT SCORED 6 | PASS 35, NOT SCORED 5 | 0.155; 0.155; 0.319; 0.110; 0.165 | 0.191 |
| A3 B3 | reading | 0.025 | FLAT 35, INCONCLUSIVE 3, NOT SCORED 2 | INVERTED 38, NOT SCORED 2 | INVERTED 40 | AGREES 37, DISAGREES 3 | INCONCLUSIVE 29, HOLDS 11 | HOLDS 38, NOT SCORED 2 | PASS 38, NOT SCORED 2 | 0.102; 0.128; 0.273; 0.090; 0.140 | 0.143 |
| A3 B3 | reading | 0.035 | FLAT 21, INCONCLUSIVE 14, NOT SCORED 5 | INVERTED 35, NOT SCORED 5 | INVERTED 39, NOT SCORED 1 | AGREES 38, NOT SCORED 1, DISAGREES 1 | INCONCLUSIVE 31, HOLDS 8, NOT SCORED 1 | HOLDS 34, NOT SCORED 6 | PASS 35, NOT SCORED 5 | 0.155; 0.155; 0.296; 0.114; 0.163 | 0.144 |
| A3 B3 | bench_c3 | 0.025 | FLAT 38, INCONCLUSIVE 2 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 32, FAILS 8 | HOLDS 40 | PASS 40 | 0.103; 0.099; 0.172; 0.077; 0.103 | 0.132 |
| A3 B3 | bench_c3 | 0.035 | FLAT 36, INCONCLUSIVE 4 | INVERTED 40 | INVERTED 40 | AGREES 40 | INCONCLUSIVE 37, FAILS 3 | HOLDS 40 | PASS 38, FAIL 2 | 0.144; 0.121; 0.193; 0.101; 0.121 | 0.134 |

**What it says.** At four blocks of each kind, in every world but one, R1 reads FLAT (32–40 of 40), R2 and R3 INVERTED and
R4 AGREES (40 of 40), M1 HOLDS and S1 PASSES (37–40 of 40, the rest NOT SCORED where a simulated meter step set a block
aside). In the position world, where the word does nothing, M1 FAILS (M6's rms 0.64 W) and R4 never AGREES (37–40
INCONCLUSIVE), so those rules can tell the worlds apart. **R5 is the rule short of power:** with bit 19 at the bench's
−0.18 W it reads INCONCLUSIVE or FAILS, and in the reading world, where bit 19 costs the same on both words, it HOLDS in
11–23 of 40 at four blocks. At three blocks every interval widens by about 1.4×. An INCONCLUSIVE R5 is a likely outcome and
will be stated as such. Nothing there is a measurement. E134's own measured noise: the zeros' scatter about their
neighbours' line 0.055 W rms (`carry_e134.py`), its per-item 95% half-widths 0.01–0.18 W at three to five blocks.

## What the rules cannot say

One card, one clock, one session. Two A words, one B word set; W67 at four positions. The bench's Booth structure is the
open RTL's, not the silicon's netlist (not public). A train's step has no temperature term: an item's own self-heating inside
its window is in its step, and at E147's largest steps (about 4 W) the next run inherits some of it (the self-test's 5%
carry-over; E134's board carried 2.8% of a step into the next read; E102 found leakage's feedback at most 7% of a step),
which the paired zero reads absorb only in part; `carry_e134.py` run on E147's own table reads its size, post hoc. M6 predicts D on the kinds harness's footing (launch at a fixed die
reading, E78's temperature term); a train's step is on the board's raw watts, and the p80 arm is reported beside. The sign
on the rail (E102-R4) and E102-R2's bit-22 cell are not run.

## Card budget

**At most 45 card-minutes**, from the session-start config read (the smoke's) to the session-end read. Expected about 41:
the smoke and the stop test about 1.3 min, an A block about 5.8 min (68 runs at 4.83 s, E134's measured rate, with E134's
16 s of block overhead), a B block about 4.2 min (49 runs). `queue_e147.sh` starts a block only if its projected end (the
longest measured block of its kind; A 360 s and B 265 s until one has ended) is inside **2,640 s** of the session start
and before **23:45 PST**; a block in flight is never cut. No session starts after 23:00 PST; every run ends by 23:50 PST.
It starts only with `et-who` clean on card 0, no other lane holding the card, and the day's post in `#community-lab`
rewritten to carry this reservation.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__` `tools/claims-v3/e147/` (its tiles in
`e147/`) to the same path under `aifoundry3:aifoundry/`. On aifoundry3, from `~/aifoundry`:

```bash
bash tools/claims-v3/e147/run_e147.sh setup     # no device access: hashes, binaries, tiles, orders, dry runs of an A and a B block, the queue's stub test
# -> read #community-lab, then rewrite the day's post to add "using aifoundry3 for 1 h, until ~HH:MM PST"
bash tools/claims-v3/e147/run_e147.sh smoke     # the session-start config read (TDP 0, threshold 65), seven 2 s runs; cycles/op 546
bash tools/claims-v3/e147/run_e147.sh stoptest  # the board and die stops on live samples, no launch; both must pass
bash tools/claims-v3/e147/run_e147.sh go        # detached; the budget rule decides; the queue ends with the session-end read
bash tools/claims-v3/e147/run_e147.sh wait      # bounded waits only
```

Then copy `build/claims-v3/aifoundry3/kinds/p147*`, `kinds-smoke/p14701`, `kinds-stoptest/p1470*` and `build/e147-logs/`
to the Intel and run `PY=<python with numpy> nice -n 10 bash tools/claims-v3/e147/collect_e147.sh 'p147[1-2][0-9]' <copy>`;
copy `build/e147-out/2026-11-02-e147-bit-prices-rest/` to `docs/reports/data/`, write its README (results first; registered
against happened; departures dated; linking section 11 item 15; what it does to predicting power and heat), push, and drop
the clause from the day's post.

## Files

All in `tools/claims-v3/e147/`: `README.md` (this), `predictions-e147.json` and `make_predictions_e147.py` (the freeze),
`predict_m6_e147.py` (M6's and M5's frozen steps), `make_e147.py` and `e147/` (the tiles, `e147-tiles.json`, `sha256.txt`),
`e147_common.py` (the items, the orders, `install()`), `run_e147.py` (run_e78.py unchanged with E147's items, and the
board-power stop), `block_e147.sh`, `queue_e147.sh`, `run_e147.sh` (the card side), `reduce_e147.py` (reduce_e78.py
unchanged, the 2 W dip line), `score_e147.py` (every rule), `collect_e147.sh`, `selftest_e147.py`, `selftest.txt`,
`dmcmd-audit.txt`; two design inputs read post hoc from E134's committed files, `m6_on_e134.py` (M6 on E134's steps) and
`carry_e134.py` (the board's carry-over in E134's trains). Their sha256 are in `predictions-e147.json` › `harness`. The bench's counts and M6's predictions:
`docs/reports/data/2026-11-02-e147-bit-prices-rest/bench/` (`counts-e147.json`, `bench-e147.log`, `m6-e147.json`), frozen
with this registration.

## Amendments

*None yet. A change after this commit goes here, dated, before the data it touches.*
