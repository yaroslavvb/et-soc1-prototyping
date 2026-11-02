# E134: single-bit prices on a second base word and at more positions, and A's low bits (Q136, aifoundry3 card 0, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, before the reservation of aifoundry3 and before any card has run one of
E134's 36 new tiles, in Q136 (lane `a3-e134-bit-prices`, critic 12 of Q134's final critic). **It answers part of item 15 of the
kinds page's section 11**, "Smaller, and carried", whose single-bit sentence reads: "Single-bit prices are answered for what
ran, one card, one base word per side, ten of 32 positions; the other positions, other base words, A's low bits (R2) and the
sign on the rail (R4) stay undecided"
([horace-kinds-of-numbers § 11, item 15](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open);
[E102](../../../docs/reports/data/2026-11-01-e102-balanced-bit-prices/README.md), the run that left them). E134 takes three
of the four: other base words (on A), more positions (on B, and on A's low bits), and A's low bits. The sign on the rail is not
run here. The frozen numbers are in [`predictions-e134.json`](predictions-e134.json), written by
[`make_predictions_e134.py`](make_predictions_e134.py) from the committed files it names, each with its sha256. Any change
after this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry3 card 0 only**, 600 MHz as its
boot-time TDP of 0 latches it, TDP 0 / threshold 65 °C as read, never set. **E134 writes nothing and sends no write command of
any kind**: no governor move, no TDP, threshold or clock set, no reset, no `--reset-ms` (so not even the one write Q136
allows), no firmware-revisions query, no residency read. Every device-management command it sends is a read, classified
from the firmware source below (§ Device commands sent).*

## The question

A is the operand the fp32 multiplier Booth-recodes (radix 4, `txfma_f1.v:113-114`, E102's citation); B is the multiplicand
whose multiples the digits select. So a flip of one A bit changes one radix-4 digit (an even bit) or two (an odd bit), and
what that costs should depend on the bits around it: with B = 1.0, a digit going from 0 to −1 turns a partial-product row
from all zeros into a negated, sign-extended row, where 2 to 1 only moves one bit. **If that is right, an A bit's price is a
property of the position within its base word, not of the position.** The lab's two A lists disagree in a way that fits
this, but they were never run side by side:

- E67 (this card, Mon 26 Oct, the hart-ladder protocol, its own word W67 = `0x3fbbc9e4`) read A bit 6 at **0.990 W**
  (s.e. 0.224 W, n = 7), 430 fJ a flip: in W67, flipping bit 6 takes digit 3 from 0 to −1.
- E102 (aifoundry1 card 1, Sun 1 Nov, trains, E79's word W79 = `0x3fbd207c`) read A bit 6 at **113 fJ** a flip (about
  0.26 W): in W79, flipping bit 6 takes digit 3 from 2 to 1.

Card, protocol, session and word all differ between them. **E134 runs both words on one card, in one train, in both
layouts**, at all eight low A bits, so that only the word differs. The fixed RTL bench, which has the structural Booth
multiplier, makes a frozen prediction for every one of these tiles; the real-accumulator counts make another (they see the
sums, not the multiplier, so they price A's low bits the same on both words).

The same blocks decide **A's low bits**, E102's R2, which E102 left INCONCLUSIVE on one cell and whose amendment A1 could not
score: is the ratio all-in / balanced at bits 0 and 6 near 1 (the flip alone, POSITION) or near the 5–7× composite (CONSTANT)?

On **B**, E102 found the all-in / balanced ratio 1× at bit 6, 3.2× at bit 11 and 5.8× at bit 16, with nothing between. By
the real accumulators' counts (frozen, below) the two sums of the all-in layout part first at **bit 8**: no result-path
bit changes over the zero at bits 6 and 7, 4,542 an op at bit 8, rising to 64,824 at bit 16. **E134
runs every B position from 6 to 16 in both layouts and asks where the accumulators' swing starts.**

## The tiles

57 fp32 tiles in the host's `--values file:` layout (2,048 bytes), written by [`make_e134.py`](make_e134.py) with E102's own
generator functions (`tools/claims-v3/kinds/make_e102.py`, `make_hlp.py`): `e134/tiles/fp32/<name>.bin`, manifest
[`e134/e134-tiles.json`](e134/e134-tiles.json) (each tile's sha256, its halves', its designed flips, its Booth digit changes
and its real-accumulator counts).

| side | word | tiles | held operand | flips an op | source |
|---|---|---|---|---:|---|
| A | W79 `0x3fbd207c` (E79's, E102's) | zero `aq`; `aj_0` … `aj_7` (E67's construction, flip = i & 1) | B = 1.0 | 2,048 | `aq`, `aj_0`, `aj_6`: E102's tiles byte for byte; 5 new |
| | | `ap_0` … `ap_7` (E102's balanced A layout, flip = (i XOR g) & 1) | B = 1.0 | 1,920 | `ap_0`, `ap_6`: E102's; 6 new |
| A | W67 `0x3fbbc9e4` (E67's) | zero `a67q`; `a67j_0` … `a67j_7` | B = 1.0 | 2,048 | **E67's own tiles** (`aq_h0`, `abit_0` … `abit_7`), byte for byte the files E67's host dumped on this card |
| | | `a67p_0` … `a67p_7` (balanced, on E67's word) | B = 1.0 | 1,920 | new |
| B | E79's eight B words | zero `hq`; `bj_6` … `bj_16` (E65's construction, flip = hi(j)) | A = 1.0 | 4,096 | `hq`, `bj_6`, `bj_11`, `bj_16`: E102's; 8 new |
| | | `bp_6` … `bp_16` (E79's balanced `jgp`) | A = 1.0 | 3,968 | `bp_6`, `bp_11`, `bp_16`: E102's; 8 new |

`make_e134.py --check` rebuilds every tile and asserts: the designed counts; the quiet operand never flips; no 32-bit word is
zero (so the zero gate never acts); every item differs from its own zero in its own bit of its own operand alone; the
balanced layouts give every accumulator the same products and the all-in layouts two different sets; and every reused tile
equals the file it reuses (E102's committed tiles, E67's dumps in `docs/reports/data/2026-10-27-e67-a-side-bit-prices/aifoundry3/hl/p750/tiles/`).

The Booth digits (radix 4, b₋₁ = 0, k = 0 … 12) each low A bit changes, from `e134-tiles.json` (a reading of the recoder's
input; no rule reads it):

| bit | W79: digit (before → after) | W67: digit (before → after) |
|---:|---|---|
| 0 | d0: 0 → +1 | d0: 0 → +1 |
| 1 | d0: 0 → -2; d1: -1 → 0 | d0: 0 → -2; d1: +1 → +2 |
| 2 | d1: -1 → -2 | d1: +1 → 0 |
| 3 | d1: -1 → +1; d2: 0 → -1 | d1: +1 → -1; d2: -2 → -1 |
| 4 | d2: 0 → -1 | d2: -2 → -1 |
| 5 | d2: 0 → +2; d3: +2 → +1 | d2: -2 → 0; d3: 0 → -1 |
| 6 | d3: +2 → +1 | d3: 0 → -1 |
| 7 | d3: +2 → 0; d4: 0 → +1 | d3: 0 → +2; d4: +2 → +1 |

## What runs

| | E102 / E130 (what this builds on) | E134 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions | the same, fp32 | E78's protocol |
| protocol | E102's trains (T, R), E130's (aifoundry3) | **trains only**: `--preheat 0 --target 200 --quiet-s 0.2 --burnin 0`, run_e78.py's own options | a pair a run apart is in one thermal state; E102 A1: an own zero within three runs of every item, which this has within one |
| blocks | — | **A** (13410–13419): 3 settling runs (never used), then four segments, words alternating (the first drawn): each segment is one word's zero between four pairs of that word's items, `[z p p z p p z p p z p p z]`; every one of the 32 A items once: 55 runs. **B** (13420–13429): 3 settling runs of `hq`, then `hq` between every pair of B reads, shuffled until no pair holds one item twice: the 22 B items once, and E134-R4's two bits (7 and 8, both layouts) twice: 43 runs | every item's nearest zero read on each side is its own zero (`e134_common.check_order`, asserted for all 20 block numbers); **E102 A1's fault is designed out**: every block opens with settling reads, and the first read a rule uses is never a block's first |
| order | — | `Random("E134\|aifoundry3\|<pass>")`, `e134_common.pass_order` | |
| sequence | — | **13410 (A) 13420 (B) 13411 (A) 13421 (B) 13412 (A) 13422 (B) 13413 (A) 13423 (B) 13424 (B) 13414 (A)**; the budget rule decides how many run | every rule has its three kept blocks of each kind after the sixth; the fourth of each is the margin against a set-aside; a fifth B goes first because R4 is the rule short of precision (§ Precision); expected: four of each, perhaps a fifth B |
| smoke | — | **13401**: `aq`, `aj_6`, `a67q`, `a67j_6`, `hq`, `bj_8`, `bp_8`, 2 s each, after the session-start config read; read for cycles per op (546), the tile dumps and the board level only, before any block | |
| primary reduction | — | E78's `reduce_e78.py` **unchanged** via `reduce_e134.py --drop-dips` (E82 A2's dips), leakage `auto`: its per-run gates and per-run table; then `score_e134.py`: the **board's `p_raw`** (mean over [t0+1 s, t0+3 s), **no temperature term**, E102's and E130's trains) minus the item's own zero interpolated in time, over designed flips × the run's rate | the bench's predictions are in board watts on this card (E92's coefficients were fitted on E78's board watts here, scale 1) |
| arms (reported) | — | the minion rail (`rail_raw`); the board with E78's temperature term (`p80` at the auto slope); dips kept; gates off (E78's pass gates and the train gate) | a verdict that moves at an arm is marked arm-sensitive |
| gates | — | E78's per-run gates (600 MHz, ±3 mV, records ok, cycles per op within 0.5% of 546, ≥ 15 window samples, duty ≥ 0.97, the tile the host dumps equal to the registered sha256) and pass gates (failed runs, configuration); **the train gate**: a zero's interior read more than 0.25 W off the line through its two neighbouring reads of the same zero, on the board, sets the block aside (E102's and E130's gate) | |
| stops | — | **die ≥ 70 °C** (E78's `--max-c`; E78's second check at `--max-c` + 10 reads the minion shires' PVT average, a die reading, E130 A2) and **board ≥ 65 W** (`run_e134.py`, E127's and E130's stop) end the block and the queue | § Stops |
| config reads | — | `ettelem config` under the card lock, `timeout 10`, at both ends of every block and the smoke, and once more when the queue ends (the session-end read) | §17 of the brief |
| data | — | raw: aifoundry3 `~/aifoundry/build/claims-v3/aifoundry3/kinds/p134<nn>/`, logs `build/e134-logs/`; results `docs/reports/data/2026-11-02-e134-bit-prices-more/` | |

**What is E78's, byte for byte.** `run_e134.py`, `reduce_e134.py` and `run_e134.sh setup` check `tools/claims-v3/lib.sh`
`033d0776…`, `kinds/e78_common.py` `c58923a5…`, `kinds/run_e78.py` `f3efd783…`, `kinds/reduce_e78.py` `6a158cee…` and
`kinds/kinds.json` `9586568f…` (the values E130 registered, and the files on aifoundry3 at 11:37 PST today) against
`predictions-e134.json` › `harness.reused_unchanged_sha256` and refuse on any difference. `e134_common.install()` replaces
`load_items` (E78's items plus E134's 57 tiles) and `pass_order` on the shared `e78_common` module in memory, then
`run_e78.main()` / `reduce_e78.main()` run as they are. Ported with marked changes from E130's card side (itself E127's,
which ran on this card this morning): `e134_common.py`, `run_e134.py`, `block_e134.sh`, `queue_e134.sh`, `run_e134.sh`,
`reduce_e134.py`, `collect_e134.sh`; `score_e134.py` is E130's train `Book` with E134's rules. Binaries: the tree's own, no
rebuild, the two E127 classified this morning (`sparsity_host` `20e760c2…`, `ettelem` `16037641…`, both read on aifoundry3 at
11:37 PST); `run_e134.sh setup` checks both hashes.

## Device commands sent

*His rule of Mon 2 Nov 2026 (Q136): every device-management command a run's harness, sampler, host program and helpers send,
classified from the firmware source of the running build, READ or WRITE; the only write allowed in Q136 is the statistics
reset, and **E134 does not send it**.* aifoundry3 reports release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0 (E79); the source read is
the open et-platform tree at `836a4ab`, the version-matched public revision (BL2 0.22.0). Paths are under
`device-bootloaders/src/ServiceProcessorBL2/`. The sending code is E130's and E127's, unchanged (lib.sh, the same `ettelem`
binary, `block_e134.sh`'s config reads and sampler call as `block_e130.sh`'s, `queue_e134.sh`'s one session-end read as
`queue_e130.sh`'s), so the list is theirs:

| # | command | sent by | firmware path at `836a4ab` | what it touches | class |
|---|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config` (each block's start and end, the smoke, the session-end read) | `services/thermal_pwr_mgmt.c:613` | copies one byte of SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | `ettelem config` | `thermal_pwr_mgmt.c:665` | copies SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | `ettelem config` | `thermal_pwr_mgmt.c:551` | copies SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` (10 Hz) | `services/perf_mgmt.c:276` → `driver/io_pll.c:932` | PLL register reads, stored in SP RAM | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | `thermal_pwr_mgmt.c:1142` → `driver/pmic_controller.c:1473`, `:254` `i2c_read` | PVT reads and **two PMIC voltage-register reads** | **READ**, a PMIC voltage read, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample`; lib.sh `drain_mgmt` (`dev_mngt_service -m DM_CMD_GET_MODULE_POWER`) only after a sampler fails to start twice or ignores SIGTERM for 30 s | `thermal_pwr_mgmt.c:984` | copies SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` → `thermal_pwr_mgmt.c:2780` | copies SP RAM; resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; lib.sh `die_c` | `thermal_pwr_mgmt.c:732` | PVT reads; the value read is cached in SP RAM | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` | `thermal_pwr_mgmt.c:1010` → `pmic_controller.c:1473` | **nine PMIC voltage-register reads** | **READ**, PMIC voltage reads, allowed by his rule of 2 Nov |

**Never sent by E134** (each checked in the code that runs): `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset (`ettelem`
sends it only with `--reset-ms` > 0; `block_e134.sh:105`, the one `start_sampler` call, passes the output file and the
duration and nothing else, and lib.sh's `die_c` / `clock_mhz` call `ettelem sample --seconds 1 --every-ms 500` literally);
`DM_CMD_SET_DM_TRACE_CONFIG`; `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (it writes the PMIC's firmware-management register; no
E134 tool calls it, and E79's harness, which does, is not used); any residency read; any `DM_CMD_SET_*`; any governor, TDP,
threshold or clock set; any reset, power cycle, PCIe, driver, firmware or OTA operation. **The host program** (`sparsity_host`)
opens the ops node only (`workloads/sparsity/host/main.cpp:172` `createPcieDeviceLayer(true, false)`): its commands go to the
master minion's runtime (the compatibility check, DMA writes of its own kernel, tiles and arguments into its own device-DRAM
buffers, the launch, DMA reads of its results and `--dump-tiles`, an abort only on a kernel timeout), none a management
command. Helpers that open no device node: `et-who` / `et-holders`, `et-lab-manifest` (its header on aifoundry3: it reads
sysfs and files only, never `/dev/et*`), `flock`, `timeout`, `ps`, `who`.

**The preflight checker, Q136(w)'s [`tools/claims-v3/dmcmd_audit.py`](../dmcmd_audit.py) at `32e9c109`** (sha256 `f29e91ca…`,
table `50168632…`), on `tools/claims-v3/e134/` (every file), `lib.sh`, `run_e78.py`, `e78_common.py` and `reduce_e78.py`, run
from the top of the lab repository ([`dmcmd-audit.txt`](dmcmd-audit.txt)):
- with no allow-list and no exception: **NO-GO, 1 disallowed**: the nine READs above, PMIC access on `GET_ASIC_VOLTAGE` and
  `GET_MODULE_VOLTAGE` only (reads), and the conditional `STATS_RESET` at `lib.sh:154` (`start_sampler` forwards `"$@"`),
  exactly as for E130 (its amendment A1);
- with the reviewed exception, `--except 'tools/claims-v3/lib.sh:154:STATS_RESET=block_e134.sh:105, the only start_sampler
  call E134 makes, passes the output file and the duration and nothing else, so no --reset-ms is forwarded'`: **GO, 0
  disallowed**;
- with `--deny-pmic-read` too: NO-GO on the voltage-read lines only, as it should be (the reads his rule allows).

**Verdict before the first launch: GO.** No disallowed or unclassified write is in the list; the only PMIC accesses are the
voltage-register reads his rule of Mon 2 Nov allows. **The build caveat E130 A1 states binds here too:** aifoundry3 runs a
thermal firmware build that is not public, so each READ's class rests on `836a4ab`'s handlers and on their unchanged
behaviour since 7 Oct ([`dmcmd_table.json`](../dmcmd_table.json) › `source.caveat`). If `run_e134.sh setup` finds either
binary's sha256 changed, or the session-start config read or the smoke's telemetry comes back in another form than E127's
and E132's runs recorded (an error code, a missing field), the list does not describe what would run: that is NO-GO, and the
session stops there.

*Note added Mon 2 Nov 2026, after the run, from its verification (nothing above changed): "the same `ettelem` binary" is the path
`build/ettelem/`, hashed at setup (`16037641…`). That binary is built from lab commit `de262730`'s `tools/ettelem/ettelem.cpp`
(`ba9a0ac3…`), as E127 recorded, not from the `a6cf931b…` (`efa3e8cd`) that the table above and the checker read. Its `config()`,
`sample()`, `Dm::get()` and `Dm::resetStats()` are byte-identical to the reviewed source's, and its `Dm` opens the management node
only, so no class changes. The data README's correction C6.*

## Stops

E134 runs no heater, no anchor and no random tile: every run is a constant-operand fp32 tile or one bit away from one, at most
about 2.5 W above its own zero (the bench's largest step, `bj_16`). E127's passes on this card this morning, with fp32
random anchors and a heater, read at most 53.84 W on the board and 62 °C on the die. Registered stops, with margin: **a die
reading ≥ 70 °C** ends the block (E78's `--max-c`; its second check at 80 °C reads the minion shires' PVT average, a die
reading, as E130 A2 found), and **a board reading ≥ 65 W** at any of E78's pre-launch reads writes the block's STOP file and
ends it with E78's exit 6 (`run_e134.py`). Either stop ends the queue. Nothing in E134 drives the card toward the PMIC's
over-power or over-temperature limits; no power cycle, reset or outlet cycle is part of any path.

## The frozen predictions

Each item's step over its own zero, board W on this card; the bench at E92's frozen coefficients, scale 1 (its counts equal
E102's frozen counts on all twelve reused tiles: `make_predictions_e134.py` asserts it); the position-only null is E67's own
list on this card (A) or E65's (B), at the item's bit, scaled to its designed flips.

**A, all-in, W, and the word difference** (`predictions-e134.json` › `items`, `contrasts_pred_W`):

| bit | W79 `aj`: bench | W67 `a67j`: bench | W67 `a67j`: E67 measured | **W67 − W79, bench** | W67 − W79, position-only | W79 `ap` (balanced): bench | W67 `a67p`: bench |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.469 | 0.490 | 0.459 ± 0.241 | **+0.021** | +0.000 | 0.440 | 0.460 |
| 1 | 1.062 | 1.148 | 1.140 ± 0.240 | **+0.086** | +0.000 | 0.997 | 1.077 |
| 2 | 0.419 | 0.519 | 0.473 ± 0.201 | **+0.100** | +0.000 | 0.393 | 0.487 |
| 3 | 0.912 | 1.004 | 1.078 ± 0.182 | **+0.092** | +0.000 | 0.856 | 0.942 |
| 4 | 0.771 | 0.266 | 0.346 ± 0.237 | **-0.505** | +0.000 | 0.723 | 0.250 |
| 5 | 0.277 | 0.955 | 0.713 ± 0.083 | **+0.678** | +0.000 | 0.260 | 0.896 |
| 6 | 0.281 | 0.805 | 0.990 ± 0.224 | **+0.524** | +0.000 | 0.264 | 0.755 |
| 7 | 0.343 | 0.380 | 0.584 ± 0.221 | **+0.037** | +0.000 | 0.322 | 0.357 |

**B, W, and the swing** (all-in minus balanced × 4096/3968, the watts the accumulators' parting adds):

| bit | `bj`: bench | `bp`: bench | real-sum result bits an op, all-in over balanced | **swing: count model** | swing: bench | `bj`: E65 (another word per bit) |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 0.435 | 0.422 | 0 | **+0.000** | -0.000 | 0.381 |
| 7 | 0.429 | 0.416 | 0 | **+0.000** | -0.000 | 0.535 |
| 8 | 0.569 | 0.416 | 4,551 | **+0.244** | +0.139 | 0.524 |
| 9 | 0.685 | 0.406 | 9,263 | **+0.510** | +0.266 | 0.606 |
| 10 | 0.922 | 0.427 | 13,921 | **+0.760** | +0.481 | 0.965 |
| 11 | 1.183 | 0.411 | 21,947 | **+1.203** | +0.759 | 1.098 |
| 12 | 1.407 | 0.459 | 27,246 | **+1.480** | +0.934 | 1.566 |
| 13 | 1.748 | 0.516 | 36,595 | **+1.988** | +1.216 | 1.777 |
| 14 | 1.996 | 0.519 | 41,812 | **+2.267** | +1.460 | 2.157 |
| 15 | 2.167 | 0.520 | 55,015 | **+2.984** | +1.630 | 2.543 |
| 16 | 2.534 | 0.564 | 64,954 | **+3.521** | +1.951 | 2.794 |

The count model prices those bits at E88's fp32 result-bit coefficient and the flop bits at E92's 6.68 fJ; E102's correction C4
says that pair counts some toggles twice, so its level runs high (E102: 1.2 W against 0.89 W measured at bit 11 on card 1). Only
where it starts is used by a rule.

## Decision rules

All on the primary (board `p_raw`, own zeros, dips removed, E78's gates and the train gate) over kept blocks. A contrast is a
per-block combination of items' W, paired inside each block; its 95% interval is t(n − 1) × sd / √n over blocks. A ratio is the
ratio of the per-block means of two items' fJ per flipped bit, with its 95% Fieller interval, paired. **A rule that reads a kind
of block with fewer than 3 kept blocks of that kind is NOT SCORED.**

| rule | what | verdicts |
|---|---|---|
| **E134-R1** | A's low bits on W79 (E102-R2's low-bit half, on a second card): all-in / balanced per flipped bit at bits 0 and 6 | **POSITION** if the upper bound < 4 at both; **CONSTANT** if the lower bound ≥ 4 at both; else INCONCLUSIVE |
| **E134-R2** | **does a single A bit's price depend on its base word?** All-in at bit 6, W67 − W79, W | **WORD** if the lower bound ≥ 0.262 W (half the bench's +0.524 W); **SAME** if the interval lies inside ±0.10 W; else INCONCLUSIVE |
| **E134-R3** | where W67's bit-6 cost sits: all-in / balanced per flipped bit on W67 at bit 6 | **FLIP** if the interval lies inside [0.5, 2.0); **SWING** if the lower bound ≥ 2.0; else INCONCLUSIVE |
| **E134-R4** | where B's accumulator swing starts: the swing's watts at bit 7 (the counts' last quiet bit) and bit 8 (their first) | **AT 8** if bit 7's interval lies inside ±0.10 W and bit 8's lower bound > 0; **EARLIER** if bit 7's lower bound > 0; **LATER** if both lie inside ±0.10 W; else INCONCLUSIVE |
| **E134-R5** | the bench's word differences over A's low bits: at every bit where the bench puts W67 − W79 (all-in) at 0.10 W or more (bits 2, 4, 5 and 6) | **AGREES** if every bit whose interval excludes zero has the bench's sign and at least half of these bits resolve; **DISAGREES** if any resolved bit has the other sign; else INCONCLUSIVE |
| **E134-S1** | the session against E67: E67's own tiles (W67 all-in, bits 0–7) against E67's list on this card | **PASS** if at least 6 of 8 lie within max(0.15 W, 25% of E67's value, 2 × E67's own s.e.) of E67's value; else FAIL |

**Reported, never a verdict** (`scored.json`, `results.md`): every item's W and fJ with its interval and blocks; every ratio
all-in / balanced on both words and on B; every word difference, all-in and balanced; the swing's watts at every B bit beside
the count model and the bench; each frozen model's rms and bias over each list; the zeros' scatter about their neighbours'
line (the session's own noise); each verdict at every arm.

**Why these lines, before the data.** R1 keeps E102-R2's threshold (4, the page's implied composite) so the two cards read on
one scale. R2 asks the question at the bit where the lab's two lists disagree most and where the bench and E67-against-E102
agree that W67 is dearer; its WORD line is half the bench's difference, so a card that shows the effect at half the bench's
size still reads WORD, and its SAME band is the size of a train's per-item noise. R3's band says "the same price per flip in
both layouts" to within a factor of two, which is how E102 read A's low bits; a composite would be 4–7×. R4's two bits are
the frozen counts' own: the last bit at which the two all-in sums stay equal, and the first at which they part. R5 reads all
the bits the bench says should move, so it can contradict the bench where R2 alone could not.

**What I expect, frozen so it can be wrong:** R1 POSITION; R2 WORD; R3 FLIP; R4 AT 8; R5 AGREES; S1 PASS. That is: an A
bit's price is its word's (the Booth recoder), it is the flip's own path and not the accumulators' swing, and B's swing starts
where the real sums part.

**The statement the page gets, decided now.** WORD with FLIP: "on one card, in one session, the same A bit costs X× as much on
one base word as on another (Y fJ against Z fJ a flip at bit 6), the same in both layouts: an A bit's price belongs to its
place in its word, as a Booth-recoded operand's should, and the price lists of E67 and E102 are each their word's." SAME: "the
A side's price at a bit does not depend on the word, at these bits; E67's bit 6 was its session's." R4 AT 8: "on B the
accumulators' swing starts at bit 8, where the real sums first part, and grows with the bits that part." EARLIER or
LATER: the same sentence with the bit the card shows, and "the real-sum count does not place it". INCONCLUSIVE is stated as
such with the intervals. **Only tiles that ran are scored. No tile is dropped, re-drawn or added after the first block, and no
prediction, threshold, band or rule changes.**

## Precision, before the data

[`selftest_e134.py`](selftest_e134.py) builds per-run tables on the real block orders and sequence (each item at its truth over
its own zero, a warm-up curve of 2 W amplitude and τ = 45 s from each block's start, a random walk of 0.01 W a run, a carry-over
of 5% of the previous run's step, white noise σ) and scores them with `score_e134.py`. Worlds: **bench** (every item at the
bench's step), **position** (A items at E67's list for their bit, the same on both words), **later** (B's swing two bits late),
**earlier** (0.20 W of swing at bit 7). [`selftest.txt`](selftest.txt), 40 sessions a world:

| blocks kept | world | σ, W a run | R1 | R2 | R3 | R4 | R5 | S1 | median half-widths, W (R2; R4 bits 7, 8) |
|---|---|---:|---|---|---|---|---|---|---|
| A4 B5 (the budget's expectation) | bench | 0.025 | POSITION 40 | WORD 40 | FLIP 40 | AT 8 34, INCONCLUSIVE 5, EARLIER 1 | AGREES 40 | PASS 40 | 0.090; 0.039, 0.085 |
| A4 B5 (the budget's expectation) | bench | 0.035 | POSITION 40 | WORD 40 | FLIP 40 | AT 8 26, INCONCLUSIVE 13, EARLIER 1 | AGREES 40 | PASS 40 | 0.128; 0.057, 0.094 |
| A4 B5 (the budget's expectation) | position | 0.025 | POSITION 40 | SAME 24, INCONCLUSIVE 16 | FLIP 40 | AT 8 38, INCONCLUSIVE 2 | INCONCLUSIVE 30, DISAGREES 10 | PASS 40 | 0.071; 0.041, 0.088 |
| A4 B5 (the budget's expectation) | position | 0.035 | POSITION 40 | INCONCLUSIVE 28, SAME 12 | FLIP 40 | AT 8 27, INCONCLUSIVE 12, EARLIER 1 | INCONCLUSIVE 30, DISAGREES 10 | PASS 40 | 0.099; 0.050, 0.097 |
| A4 B5 (the budget's expectation) | later | 0.025 | POSITION 40 | WORD 40 | FLIP 40 | INCONCLUSIVE 27, LATER 13 | AGREES 40 | PASS 40 | 0.096; 0.033, 0.093 |
| A4 B5 (the budget's expectation) | later | 0.035 | POSITION 40 | WORD 40 | FLIP 40 | INCONCLUSIVE 26, LATER 12, EARLIER 2 | AGREES 40 | PASS 40 | 0.107; 0.045, 0.101 |
| A4 B5 (the budget's expectation) | earlier | 0.025 | POSITION 40 | WORD 40 | FLIP 40 | EARLIER 40 | AGREES 40 | PASS 40 | 0.082; 0.043, 0.084 |
| A4 B5 (the budget's expectation) | earlier | 0.035 | POSITION 40 | WORD 40 | FLIP 40 | EARLIER 40 | AGREES 40 | PASS 40 | 0.123; 0.053, 0.092 |
| A4 B4 | bench | 0.025 | POSITION 40 | WORD 40 | FLIP 40 | INCONCLUSIVE 26, AT 8 14 | AGREES 40 | PASS 40 | 0.102; 0.050, 0.129 |
| A4 B4 | bench | 0.035 | POSITION 39, INCONCLUSIVE 1 | WORD 39, INCONCLUSIVE 1 | FLIP 40 | INCONCLUSIVE 24, AT 8 16 | AGREES 40 | PASS 40 | 0.098; 0.070, 0.118 |
| A4 B4 | position | 0.025 | POSITION 40 | SAME 25, INCONCLUSIVE 15 | FLIP 40 | INCONCLUSIVE 21, AT 8 19 | INCONCLUSIVE 23, DISAGREES 17 | PASS 40 | 0.069; 0.048, 0.115 |
| A4 B4 | position | 0.035 | POSITION 40 | INCONCLUSIVE 27, SAME 13 | FLIP 40 | INCONCLUSIVE 27, AT 8 13 | INCONCLUSIVE 32, DISAGREES 8 | PASS 40 | 0.086; 0.064, 0.124 |
| A4 B4 | later | 0.025 | POSITION 40 | WORD 40 | FLIP 40 | INCONCLUSIVE 37, LATER 3 | AGREES 40 | PASS 40 | 0.080; 0.059, 0.124 |
| A4 B4 | later | 0.035 | POSITION 40 | WORD 40 | FLIP 40 | INCONCLUSIVE 35, LATER 5 | AGREES 40 | PASS 40 | 0.106; 0.072, 0.133 |
| A4 B4 | earlier | 0.025 | POSITION 40 | WORD 40 | FLIP 40 | EARLIER 40 | AGREES 40 | PASS 40 | 0.083; 0.050, 0.107 |
| A4 B4 | earlier | 0.035 | POSITION 40 | WORD 39, INCONCLUSIVE 1 | FLIP 40 | EARLIER 40 | AGREES 40 | PASS 40 | 0.115; 0.070, 0.128 |
| A3 B3 | bench | 0.025 | POSITION 39, INCONCLUSIVE (a ratio is unbounded) 1 | WORD 39, INCONCLUSIVE 1 | FLIP 40 | INCONCLUSIVE 39, AT 8 1 | AGREES 40 | PASS 40 | 0.114; 0.063, 0.197 |
| A3 B3 | bench | 0.035 | POSITION 34, INCONCLUSIVE 6 | WORD 33, INCONCLUSIVE 7 | FLIP 40 | INCONCLUSIVE 36, EARLIER 3, AT 8 1 | AGREES 40 | PASS 40 | 0.148; 0.077, 0.219 |
| A3 B3 | position | 0.025 | POSITION 40 | INCONCLUSIVE 26, SAME 14 | FLIP 40 | INCONCLUSIVE 38, EARLIER 2 | INCONCLUSIVE 33, DISAGREES 7 | PASS 40 | 0.091; 0.061, 0.222 |
| A3 B3 | position | 0.035 | POSITION 39, INCONCLUSIVE 1 | INCONCLUSIVE 30, SAME 10 | FLIP 40 | INCONCLUSIVE 37, AT 8 2, EARLIER 1 | INCONCLUSIVE 30, DISAGREES 10 | PASS 40 | 0.149; 0.099, 0.257 |
| A3 B3 | later | 0.025 | POSITION 39, INCONCLUSIVE 1 | WORD 38, INCONCLUSIVE 2 | FLIP 40 | INCONCLUSIVE 40 | AGREES 40 | PASS 40 | 0.122; 0.088, 0.211 |
| A3 B3 | later | 0.035 | POSITION 33, INCONCLUSIVE 7 | WORD 31, INCONCLUSIVE 9 | FLIP 40 | INCONCLUSIVE 39, EARLIER 1 | AGREES 40 | PASS 40 | 0.163; 0.088, 0.229 |
| A3 B3 | earlier | 0.025 | POSITION 39, INCONCLUSIVE 1 | WORD 37, INCONCLUSIVE 3 | FLIP 40 | EARLIER 39, INCONCLUSIVE 1 | AGREES 40 | PASS 40 | 0.102; 0.064, 0.231 |
| A3 B3 | earlier | 0.035 | POSITION 36, INCONCLUSIVE 3, NOT SCORED 1 | WORD 32, INCONCLUSIVE 7, NOT SCORED 1 | FLIP 39, NOT SCORED 1 | EARLIER 39, INCONCLUSIVE 1 | AGREES 39, NOT SCORED 1 | PASS 39, NOT SCORED 1 | 0.152; 0.098, 0.213 |

**What it says.** In the bench's world R1, R2, R3, R5 and S1 read as expected in 40 of 40 sessions at four A blocks. In the position-only world R2 never reads WORD and R5 never reads AGREES (it reads DISAGREES in 5–10 of 40), so the A rules can tell the two worlds apart. **R4 is the rule short of power:** its onset bit's swing, 0.139 W by the bench, reads AT 8 in 38 of 40 sessions at five B blocks and σ = 0.025 W (28 at 0.035), but in only 13–18 of 40 at four and almost never at three; it reads EARLIER whenever bit 7 carries 0.20 W, and LATER is hard to show (5–17 of 40). That is why the fifth B block runs before the fifth A, and why the gap between blocks is 2 s: the budget then expects four A and five B blocks. An INCONCLUSIVE R4 is a likely outcome and will be stated as such.

Nothing there is a measurement.

## What the rules cannot say

One card, one clock, one session. Two A words, one B word set; a WORD verdict says the price moved with the word at these
bits on this card, and the Booth reading is the bench's structure, not the silicon's netlist (the ET-SoC-1's multiplier is not
public; the bench is the open RTL's). The position-only null is E67's list measured in another protocol on this card (its
standard errors are 0.02–0.22 W). A train's step has no temperature term: an item's own self-heating inside its window is in
its step (at most a few hundredths of a watt at these steps). The rail lags the board by about 1 s and remembers part of the
previous run's step (E102 A1: +0.078 W per W), so the rail arm carries some of a large step into the next read; the board is
the primary for that reason too. The sign on the rail (E102-R4) is not run.

## Card budget

**At most 40 card-minutes**, from the session-start config read (the smoke's) to the session-end read. Expected about 35–39: the
smoke about 0.7 min, an A block about 4.7 min (55 runs at E102's 4.86 s, with about 15 s of block overhead), a B block about
3.7 min (43 runs). `queue_e134.sh` starts a block only if its projected end (the longest measured block of its kind; A 300 s
and B 240 s until one has ended) is inside **2,340 s** of the session start and before **15:50 PST**; a block in flight is
never cut. No session starts after 15:00 PST; every run ends by 16:00 PST. It starts only with `et-who` clean on card 0, no
other lane holding the card, and the day's post in `#community-lab` rewritten to carry this reservation (§15 of the brief).

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__` `tools/claims-v3/e134/` (its tiles in
`e134/`) to the same path under `aifoundry3:aifoundry/`. On aifoundry3, from `~/aifoundry`:

```bash
bash tools/claims-v3/e134/run_e134.sh setup     # no device access: hashes, binaries, tiles, orders, dry runs of an A and a B block, the queue's stub test
# -> read #community-lab, then rewrite the day's post to add "using aifoundry3 for 1 h, until ~HH:MM PST"
bash tools/claims-v3/e134/run_e134.sh smoke     # the session-start config read (TDP 0, threshold 65), seven 2 s runs; cycles/op 546
bash tools/claims-v3/e134/run_e134.sh go        # detached; the budget rule decides; the queue ends with the session-end read
bash tools/claims-v3/e134/run_e134.sh wait      # bounded waits only
```

Then copy `build/claims-v3/aifoundry3/kinds/p134*`, `kinds-smoke/p13401` and `build/e134-logs/` to the Intel and run
`PY=<python with numpy> nice -n 10 bash tools/claims-v3/e134/collect_e134.sh 'p134[1-2][0-9]' <copy>`; copy
`build/e134-out/2026-11-02-e134-bit-prices-more/` to `docs/reports/data/`, write its README (results first; registered against
happened; departures dated; linking section 11 item 15), push, and drop the clause from the day's post.

## Files

All in `tools/claims-v3/e134/`: `README.md` (this), `predictions-e134.json` and `make_predictions_e134.py` (the freeze),
`make_e134.py` and `e134/` (the tiles, `e134-tiles.json`, `sha256.txt`), `e134_common.py` (the items, the orders, `install()`),
`run_e134.py` (run_e78.py unchanged with E134's items, and the board-power stop), `block_e134.sh`, `queue_e134.sh`,
`run_e134.sh` (the card side), `reduce_e134.py` (reduce_e78.py unchanged), `score_e134.py` (every rule), `collect_e134.sh`,
`selftest_e134.py`, `selftest.txt`, `dmcmd-audit.txt`. Their sha256 are in `predictions-e134.json` › `harness`. The bench's
counts: `docs/reports/data/2026-11-02-e134-bit-prices-more/bench/counts-e134.json` (frozen with this registration).

## Amendments

*None yet. A change after this commit goes here, dated, before the data it touches.*

*A note added after the run (not an amendment: no procedure, prediction, rule or stop changed), Mon 2 Nov 2026, from the run's
verification: one under § Device commands sent (the `ettelem` binary's source). The data README's § Corrections after verification
lists every correction.*
