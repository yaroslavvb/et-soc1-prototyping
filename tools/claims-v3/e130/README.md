# E130: which int8 multiplier - Q136(a)'s single-bit set on aifoundry3, each netlist's frozen prediction scored (Q136, aifoundry3 card 0, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, before the claim of aifoundry3 and before any card has run one of
these 26 tiles, in Q136 (lane `a3-e130-int8-netlists`, critic 8 of Q134's final critic). **It answers item 12 of the kinds
page's section 11**, "int8 at gate level", its first open point, which multiplier
([horace-kinds-of-numbers § 11, item 12](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)).
The predictions it scores were frozen by [Q136(a)](../../../docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/README.md)
in lab commit `d64ea98c` (07:48 PST; its corrections `8ab2ed9d` change no frozen number), and are copied here number for number
by [`make_predictions_e130.py`](make_predictions_e130.py) into [`predictions-e130.json`](predictions-e130.json), which also holds
the thresholds, bands, rules and the sha256 of every file the run uses. Any change after this commit goes in Amendments, dated,
before the data it touches. Card: **aifoundry3 card 0 only**, 600 MHz as its boot-time TDP of 0 latches it, TDP 0 / threshold
65 °C as read, never set. **E130 writes nothing and sends no write command of any kind**: no governor move, no TDP, threshold
or clock set, no reset, no `--reset-ms` (so not even the one write Q136 allows), no firmware-revisions query, no residency read;
every device-management command it sends is a read, classified from the firmware source below (§ Device commands sent).*

## The question

Q133(a) mapped the int8 multiply-add of the public RTL (`$signed(a) * $signed(b)`) to gates four ways: `booth_tree` and
`booth` recode B (radix-4 Booth on the second operand, as Yosys does for `x * y`), `booth_swap` recodes A, `plain` recodes
neither. On E79's and E102's single bits the card's B list alternated (odd bits about 2.8× its even bits, at E79's base words,
on two cards) and its A list did not, which fits a recoder on B; E78's kind-level watts fit `booth_swap` best. Neither was
registered. Q136(a) chose 26 new tiles on new base words and froze each netlist's prediction for every one. **E130 runs them and
asks which of the three groups the card is: Booth on B, Booth on A, or no Booth** (`booth` and `booth_tree` are not separable
by single bits at zero delay, Q136(a) result 3), and scores each netlist's prediction.

## The tiles

Q136(a)'s 26 int8 tiles, **byte for byte, used in place**: `tools/claims-v3/kinds/e130/tiles/int8/<tile>.bin` (2,048 bytes,
the host's `--values file:` layout), manifest `tools/claims-v3/kinds/e130/e130.json` (sha256 `bcbced62…`, checked before any
run); [`e130-items.json`](e130-items.json) copies every field and adds each half's sha256, which E78's tile check needs.

| side | tiles | held operand | flips an op per item |
|---|---|---|---:|
| B (E79's `kg` layout: B's bit flips on the line-group parity) | zero `hb1`; `b1_0` … `b1_7` at base word B1 | A = 1 | 1,024 |
| | zero `hb2`; `b2_7` (the sign at word B2) | A = 1 | 1,024 |
| | zero `hb1d`; `b1d_7` (the sign at B1, dense held operand) | A = 0x55 | 1,024 |
| A (E79's A layout: A's bit alternates down the rows) | zero `ha1`; `a1_0` … `a1_7` at base word A1 | B = 1 | 8,192 |
| | zero `ha2`; `a2_7` | B = 1 | 8,192 |
| | zero `ha1d`; `a1d_7` | B = 0x55 | 8,192 |

Each item differs from its own zero in the chosen bit alone (`make_e130.py --check`). Expected steps: 0.015–0.27 W on the B list,
0.6–5.1 W on the A list (Q136(a)'s table).

## What runs

| | E79 / E102 (the lists this builds on) | E130 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type int8 --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions | the same | E78's protocol |
| protocol | E79: heat to 59 °C, launch at 58 °C (its B list did not survive the leakage slope); E102 int8 block I: a **train** (no heater, no launch reading, 0.2 s between runs) | **trains only**: E102's block I options `--preheat 0 --target 200 --quiet-s 0.2 --burnin 0`, run_e78.py's own | in a train a pair two runs apart is in one thermal state; E102's int8 train read 0.019 W a run on its card's rail, its single bits resolved where E79's did not |
| blocks | — | **B** (13010–13019): 4 settling runs of `hb1` (never used), then `hb1` between every pair of the 14 hb1 items (`b1_0` … `b1_5` twice each, `b1_6` and `b1_7` once), shuffled; `[hb2 b2_7 hb2]` and `[hb1d b1d_7 hb1d]` each inserted after one `hb1` read and followed by another: 34 runs. **A** (13020–13029): 3 settling runs of `ha1`, then `ha1` between the groups (two of `a1_0` … `a1_6` three times, the seventh, `a1_7`), shuffled; `[ha2 a2_7 ha2]` and `[ha1d a1d_7 ha1d]` inserted the same way: 25 runs | every item has its own zero immediately before and after it (`e130_common.check_order`, asserted for all 20 block numbers); B's six contrast bits get two reads a block because the B list is where the precision is short (Q136(a)'s note on E79's per-item half-widths) |
| order | — | `Random("E130\|aifoundry3\|<pass>")`, `e130_common.pass_order` | |
| sequence | — | **13010 (B) 13020 (A) 13011 (B) 13021 (A) 13012 (B) 13022 (A) 13013 (B) 13023 (A) 13014 (B) 13015 (B)**; the budget rule decides how many run | every rule has its three kept blocks of each kind after the sixth; the fourth A is the A rules' margin against a set-aside; the last two B buy resolution |
| smoke | — | **13001**: `hb1`, `b1_1`, `b1_7`, `ha1`, `a1_1`, `a1_7`, `ha1d`, `a1d_7`, 2 s each, after the session-start config read; read for cycles per op (318), the tile dumps and the board level only, before any block | |
| primary reduction | — | E78's `reduce_e78.py` **unchanged** via `reduce_e130.py --drop-dips` (E82 A2's dips, E127's primary on this card), leakage `auto`: its per-run gates and per-run table; then `score_e130.py`: the **board's `p_raw`** (mean over [t0+1 s, t0+3 s), **no temperature term**, E102's trains) minus the item's own zero interpolated in time, over designed flips × the run's rate | the predictions are in board fJ on this card (Q136(a)'s k is fitted on E78's board watts here) |
| arms (reported) | — | the minion rail (`rail_raw`); the board with E78's temperature term (`p80` at the auto slope); dips kept; gates off (E78's pass gates and the train gate) | a verdict that moves at an arm is marked arm-sensitive |
| gates | — | E78's per-run gates (600 MHz, ±3 mV, records ok, cycles per op within 0.5% of 318, ≥ 15 window samples, duty ≥ 0.97, the tile the host dumps equal to the registered sha256) and pass gates (failed runs, configuration); **the train gate**: a zero's interior read more than 0.25 W off the line through its neighbours on the board sets the block aside (E102's gate, on the primary's meter) | |
| stops | — | **die ≥ 70 °C** (E78's `--max-c`, lowered from 78) and **board ≥ 65 W** (`run_e130.py`, E127's stop) end the block and the queue | § Stops |
| config reads | — | `ettelem config` under the card lock, `timeout 10`, at both ends of every block and the smoke, and once more when the queue ends (the session-end read) | §17 of the brief |
| data | — | raw: aifoundry3 `~/aifoundry/build/claims-v3/aifoundry3/kinds/p130<nn>/`, logs `build/e130-logs/`; results `docs/reports/data/2026-11-02-e130-int8-netlists/` | |

**What is E78's, byte for byte.** `run_e130.py`, `reduce_e130.py` and `run_e130.sh setup` check `tools/claims-v3/lib.sh`
`033d0776…`, `kinds/e78_common.py` `c58923a5…`, `kinds/run_e78.py` `f3efd783…`, `kinds/reduce_e78.py` `6a158cee…` and
`kinds/kinds.json` `9586568f…` against `predictions-e130.json` › `harness.reused_unchanged_sha256` and refuse on any difference.
`e130_common.install()` replaces `load_items` (E78's items plus the 26 tiles) and `pass_order` on the shared `e78_common` module
in memory, then `run_e78.main()` / `reduce_e78.main()` run as they are. New, ported with marked changes from E127's card side
(this card, this morning) and E102's trains: `e130_common.py`, `run_e130.py`, `block_e130.sh`, `queue_e130.sh`, `run_e130.sh`,
`reduce_e130.py`, `collect_e130.sh`; new: `score_e130.py` (E102's `Book` for trains, ported), `selftest_e130.py`,
`make_predictions_e130.py`. Binaries: the tree's own, no rebuild, the two E127 classified this morning (`sparsity_host`
`20e760c2…`, `ettelem` `16037641…`); `run_e130.sh setup` checks both hashes.

## Device commands sent

*His rule of Mon 2 Nov 2026 (Q136): every device-management command a run's harness, sampler, host program and helpers send,
classified from the firmware source of the running build, READ or WRITE; the only write allowed in Q136 is the statistics
reset, and **E130 does not send it**.* aifoundry3 reports release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0 (E79); the source read is
the open et-platform tree at `836a4ab`, the version-matched public revision (BL2 0.22.0; the card exposes no BL2 hash, so this
reads *a* 0.22.0). Paths are under `device-bootloaders/src/ServiceProcessorBL2/`. The sending code is E127's, unchanged (lib.sh,
the same `ettelem` binary, `block_e130.sh`'s config reads and sampler call as `block_e127.sh`'s), so the list is E127's:

| # | command | sent by | firmware path at `836a4ab` | what it touches | class |
|---|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config` (each block's start and end, the smoke, the session-end read) | `services/thermal_pwr_mgmt.c:613` | copies one byte of SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | `ettelem config` | `thermal_pwr_mgmt.c:665` | copies SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | `ettelem config` | `thermal_pwr_mgmt.c:551` | copies SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` (10 Hz) | `services/perf_mgmt.c:276` → `driver/io_pll.c:932` | PLL register reads, stored in SP RAM | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | `thermal_pwr_mgmt.c:1142` → `driver/pmic_controller.c:1473`, `:254` `i2c_read` | PVT reads and **two PMIC voltage-register reads** | **READ** — a PMIC voltage read, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample`; lib.sh `drain_mgmt` (`dev_mngt_service -m DM_CMD_GET_MODULE_POWER`) only after a sampler fails to start twice or ignores SIGTERM for 30 s | `thermal_pwr_mgmt.c:984` | copies SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` → `thermal_pwr_mgmt.c:2780` | copies SP RAM; resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; lib.sh `die_c` (a 1 s sample at each block's start and end) | `thermal_pwr_mgmt.c:732` | PVT reads; the value read is cached in SP RAM | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` | `thermal_pwr_mgmt.c:1010` → `pmic_controller.c:1473` | **nine PMIC voltage-register reads** | **READ** — PMIC voltage reads, allowed by his rule of 2 Nov |

**Never sent by E130** (each checked in the code that runs): `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset (`ettelem`
sends it only with `--reset-ms` > 0; `block_e130.sh`'s one `start_sampler` call passes the output file and the duration and
nothing else, and lib.sh's `die_c` / `clock_mhz` call `ettelem sample --seconds 1 --every-ms 500` literally);
`DM_CMD_SET_DM_TRACE_CONFIG`; `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (it writes the PMIC's firmware-management register; no E130
tool calls it, and E79's harness, which does, is not used); any residency read; any `DM_CMD_SET_*`. **The host program**
(`sparsity_host`) opens the ops node only (`workloads/sparsity/host/main.cpp:172` `createPcieDeviceLayer(true, false)`): its
commands go to the master minion's runtime (the compatibility check, DMA writes of its own kernel, tiles and arguments into its
own device-DRAM buffers, the launch, DMA reads of its results and `--dump-tiles`, an abort only on a kernel timeout), none a
management command. Helpers that open no device node: `et-who` / `et-holders`, `et-lab-manifest`, `flock`, `timeout`, `ps`, `who`.

**The preflight checker, Q136(w)'s `tools/claims-v3/dmcmd_audit.py` as committed in `96e24891`** (run from a copy of that
revision and its table, sha256 `9bc2444e…` and `1321ebca…`), on `run_e130.py`, `block_e130.sh`, `queue_e130.sh`, `run_e130.sh`,
`e130_common.py`, `reduce_e130.py`, `score_e130.py`, `collect_e130.sh`, `lib.sh`, `run_e78.py` and `e78_common.py`: the nine reads
above at 36 send sites, PMIC access on `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` only (reads), and one **conditional** write
it cannot rule out from text, `SET_STATS_RUN_CONTROL` at `lib.sh:154` (`start_sampler` forwards `"$@"`), exactly as for E127.
Cleared by reading the call: `block_e130.sh` calls `start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900))` and nothing else. The
working tree's uncommitted revision of the checker (another lane's work in progress when this was written, sha256 `bc57bffe…`)
additionally flags six lines it cannot resolve; each was read and none sends a command: `lib.sh:86` is the process-name pattern
`DEV_COMM` (a `ps` regex), `lib.sh:95` and `:214` are `wait_free`'s loop and the dry-run stub of `ours_running`, and
`block_e130.sh:102` is `timeout 10 "$ETTELEM" config`, `ETTELEM=build/ettelem/ettelem`, the stock binary whose hash `setup`
checks. Both outputs are kept with the data (`logs/dmcmd_audit_e130*.txt`).

**Verdict before the first launch: GO.** No disallowed or unclassified write is in the list; the only PMIC accesses are the
voltage-register reads his rule of Mon 2 Nov allows. If `run_e130.sh setup` finds either binary's sha256 changed, the list does
not describe what would run: that is NO-GO, and the run stops there.

## Stops

E130 runs no heater, no anchor and no float tile: every run is an int8 tile at most 5.1 W above its own zero (`a1d_7`), and
the trains keep the die near its idle level. E127's passes on this card this morning, with fp32 random anchors and a heater,
read at most 53.84 W on the board and 62 °C on the die. Registered stops, with margin: **a die reading ≥ 70 °C** (or a PMIC
reading ≥ 80 °C) ends the block (E78's `--max-c`, lowered to 70 in `block_e130.sh`), and **a board reading ≥ 65 W** at any of
E78's pre-launch reads writes the block's STOP file and ends it with E78's exit 6 (`run_e130.py`, E127's wrapper unchanged).
Either stop ends the queue. Nothing in E130 drives the card toward the PMIC's over-power or over-temperature limits; no power
cycle, reset or outlet cycle is part of any path.

## The frozen predictions and the thresholds

fJ per flipped bit at each netlist's own k, the mean of Q136(a)'s three launch points, `nets_map` (`nets_hier` beside); each
netlist's **band** is the hull of its two merges, each widened by twice k's relative jackknife s.e. (a ratio is not widened).

| statistic | `booth_tree` | `booth` | `booth_swap` | `plain` | threshold |
|---|---|---|---|---|---|
| **B: odd (1, 3, 5) − even (0, 2, 4)** | 60.3; 60.7 [54.9, 66.2] | 60.3; 60.6 [54.8, 66.0] | 0.5; 0.8 [0.5, 0.9] | 0.8; 1.1 [0.7, 1.2] | **T_B = 30.68** (between 1.11 and 60.26) |
| **A: odd − even** | 0.5; 1.1 [0.4, 1.2] | −1.0; 0.8 [−1.1, 0.8] | 86.0; 50.6 [48.3, 89.9] | 4.5; 2.9 [2.6, 5.0] | **T_A = 27.58** (between 4.54 and 50.62) |
| **A sign: B = 0x55 − B = 1** (`a1d_7` − `a1_7`) | 31.9; 49.4 [29.1, 53.9] | 34.3; 47.6 [31.2, 51.9] | −8.2; 4.2 [−8.6, 4.4] | 53.4; 34.1 [30.4, 59.1] | **T_S = 18.07** (between 4.22 and 31.92) |
| B odd / even | 4.39; 4.27 | 4.30; 4.16 | 1.05; 1.07 | 1.07; 1.10 | reported |
| A odd / even | 1.01; 1.04 | 0.98; 1.03 | 2.52; 2.62 | 1.10; 1.13 | reported |
| A sign, word 2 / word 1 (`a2_7` / `a1_7`) | 1.000; 1.010 | 1.007; 1.007 | 1.009; 0.990 | 1.011; 1.003 | shared band [0.990, 1.011] |
| B sign, word 2 / word 1 (`b2_7` / `b1_7`) | 1.026; 1.018 | 1.022; 1.015 | 1.014; 1.008 | 1.015; 1.010 | shared band [1.008, 1.026] |

Every item's prediction and band, both merges, are in `predictions-e130.json` › `netlists.<netlist>.items` (Q136(a)'s README
has the table). Each threshold is the midpoint between the two groups' nearest predictions over both merges, computed by
`make_predictions_e130.py` from the frozen numbers; each netlist's own predictions fall on its group's side of all three
(asserted there).

## Decision rules

All on the primary (board `p_raw`, own zeros, dips removed, E78's gates and the train gate) over kept blocks. A statistic is a
per-block combination of the items' fJ, paired inside each block; its 95% interval is t(n − 1) × sd / √n over blocks. A ratio is
the ratio of the per-block means with its 95% Fieller interval, paired. **A rule that reads a kind of block with fewer than 3
kept blocks of that kind is NOT SCORED.**

| rule | what | verdicts |
|---|---|---|
| **E130-R1** | is B recoded? B's odd − even | **RECODED** if the interval's low end ≥ T_B; **FLAT** if its high end ≤ T_B; else INCONCLUSIVE |
| **E130-R2** | is A recoded? A's odd − even | **RECODED** if low end ≥ T_A; **FLAT** if high end ≤ T_A; else INCONCLUSIVE |
| **E130-R3** | does A's sign bit cost more with the dense held B? (it does where A is the multiplicand of every partial-product row, i.e. A not recoded) | **RISES** if low end ≥ T_S; **FLAT** if high end ≤ T_S; else INCONCLUSIVE |
| **E130-R4** | **which multiplier (the registered primary)**: Booth on B predicts (R1, R2, R3) = (RECODED, FLAT, RISES); Booth on A (FLAT, RECODED, FLAT); no Booth (FLAT, FLAT, RISES) | the group no decided rule contradicts: **BOOTH ON B**, **BOOTH ON A** or **NO BOOTH** if one is left with all three decided (with "(n of 3 rules decided)" if some are INCONCLUSIVE); **NONE OF THE FOUR** if none is left; **INCONCLUSIVE between …** if two or more; NOT SCORED if R1 or R2 is |
| **E130-R5** | the shared prediction, A: `a2_7` / `a1_7` | **HOLDS** if its interval overlaps the shared band [0.990, 1.011]; **FAILS** (ABOVE / BELOW) if not; NOT SCORED if unbounded |
| **E130-R6** | the shared prediction, B: `b2_7` / `b1_7` | as R5, band [1.008, 1.026] |
| **E130-N** | each netlist's frozen prediction | per netlist: **SURVIVES** if the card's interval overlaps its band on all three separators, else **EXCLUDED by** the ones it misses; every other statistic and all 20 items are reported CONSISTENT / ABOVE / BELOW against its bands, with each netlist's rms (both merges) and Spearman over each list |

**Reported, never a verdict** (`scored.json`, `results.md`): every item's fJ and W with its interval and blocks; every statistic
of the table above with every netlist's values; the odd/even ratios; B's and A's list means (levels, which carry k); B's sign
step with the dense held A (Q136(a): it separates nothing); the zeros' scatter about their neighbours' line (the session's own
noise); each verdict at every arm.

**Why these lines, before the data.** The midpoint treats an error in either group's amplitude alike, and every netlist's own
prediction sits on its group's side by at least 14 fJ (R3) to 30 fJ (R1). R4 asks for the group, not the netlist: `booth` and
`booth_tree` cannot be told apart here (at most 0.34 card half-widths, Q136(a)). R5 and R6 test a prediction all four share: a
FAIL says every netlist is wrong about the sign bit in the same way (item 12's "the sign bit is priced about twice the card's"),
a HOLDS is weak (it only fails to exclude). E-N scores levels too, which carry k (2–5% s.e.) and, on the A list, the merge
(`nets_hier` reads about half of `nets_map`); so a netlist EXCLUDED on a level while its group's shape holds is reported as such,
never folded into R4.

**What I expect, frozen so it can be wrong:** R1 RECODED, R2 FLAT, R3 RISES, so **R4 BOOTH ON B**; R5 and R6 HOLDS. E79 (this
card) and E102 (aifoundry1 card 1) read B's odd bits about 2.8× its even bits and A's list flat at E79's base words; E130's
words are new. Per netlist: `booth` and `booth_tree` SURVIVE, or are EXCLUDED only by B's amplitude (E79's odd − even, +40
board-fJ, was 0.7× the netlists' +60); `booth_swap` and `plain` EXCLUDED by B's odd − even.

**The statement the page gets, decided now.** BOOTH ON B: "on base words chosen and predicted before the card saw them, the
card's int8 single bits follow the netlists that Booth-recode B: B's odd bits cost X× its even bits, A's do not alternate, and
A's sign bit costs Y fJ more with a dense held B; the netlist that recodes A and the one with no recoder are excluded." BOOTH ON
A or NO BOOTH: the same sentence for that group, and "E79's and E102's B-list shape was the base word's, not the multiplier's".
NONE OF THE FOUR: "the card's int8 multiplier is none of Q133(a)'s four: …", naming what each rule read. INCONCLUSIVE is stated
as such with the intervals. **Only tiles that ran are scored. No tile is dropped, re-drawn or added after the first block, and no
prediction, threshold, band or rule changes.**

## Precision, before the data

[`selftest_e130.py`](selftest_e130.py) builds per-run tables on the real block orders and sequence (each item at its truth over
its own zero, a block-long drift curve of 0.3 W, a random walk of 0.01 W a run, white noise σ) and scores them with
`score_e130.py`. At the planning σ = 0.025 W a run ([`selftest.txt`](selftest.txt), 40 sessions a world): **R4 names the right
group in 40/40 sessions in the `booth_tree`, `booth_swap`, `plain` and both-recoded worlds**, and a wrong group in 0 of 200; the
separators' median half-widths are **9–10 fJ** (B's odd − even), **2.2 fJ** (A's odd − even) and **3.6–4.3 fJ** (A's sign step),
against distances from the thresholds of 30, 23 and 14 fJ. **The weak case is the one E79 suggests**: with B's odd − even at
the card's E79 amplitude (+40 fJ, 9 fJ above T_B), R1 reads RECODED in 25 of 40 sessions and INCONCLUSIVE in the rest (R4 then
"INCONCLUSIVE between BOOTH ON B / NO BOOTH"), never FLAT; at σ = 0.015 W 33 of 40, at 0.035 W 15 of 40
([`selftest-power.txt`](selftest-power.txt)). The checks also show the train gate setting aside a block with a 0.4 W zero glitch,
and R1 and R4 NOT SCORED on two B blocks: **12 of 12 checks pass**. Nothing there is a measurement.

## What the rules cannot say

One card, one clock. The netlists are Q133(a)'s, an open 7 nm library from the public RTL's later revision, at zero delay (no
glitches); the ET-SoC-1's own multiplier is not public, so a group verdict says which of these four structures the card's
single bits follow, not what the silicon's netlist is. `booth` against `booth_tree` stays open. k is a fitting constant (levels
carry it). A train's step has no temperature term: an item's own self-heating inside its window (up to about 0.12 W on the 5 W A
sign items at this card's leakage) is in its step, where E78's footing, on which k was fitted, corrects it; that moves A's sign
levels by about 2–3% and the contrasts much less. The rail lags the board by about 1 s (E78's model), so the rail arm carries some
of a large step into the next read; the board is the primary for that reason too.

## Card budget

**At most 30 card-minutes**, from the session-start config read (the smoke's) to the session-end read. Expected about 27: the
smoke about 1 min, a B block about 3 min (34 runs at E102's 4.8 s, with about 13 s of block overhead), an A block about 2.3 min.
`queue_e130.sh` starts a block only if its projected end (the longest measured block of its kind; B 200 s and A 160 s until one
has ended) is inside **1,740 s** of the session start and before **15:50 PST**; a block in flight is never cut. No session starts
after 15:00 PST; every run ends by 16:00 PST. It starts only with `et-who` clean on card 0, no other lane holding the card, and
the day's post in `#community-lab` rewritten to carry this reservation (§15 of the brief).

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__` `tools/claims-v3/e130/` and
`tools/claims-v3/kinds/e130/` to the same paths under `aifoundry3:aifoundry/`. On aifoundry3, from `~/aifoundry`:

```bash
bash tools/claims-v3/e130/run_e130.sh setup     # no device access: hashes, binaries, tiles, orders, dry runs of a B and an A block, the queue's stub test
# -> read #community-lab, then rewrite the day's post to add "using aifoundry3 for 0.5 h, until ~HH:MM PST"
bash tools/claims-v3/e130/run_e130.sh smoke     # the session-start config read (TDP 0, threshold 65), eight 2 s runs; cycles/op 318
bash tools/claims-v3/e130/run_e130.sh go        # detached; the budget rule decides; the queue ends with the session-end read
bash tools/claims-v3/e130/run_e130.sh wait      # bounded waits only
```

Then copy `build/claims-v3/aifoundry3/kinds/p130*`, `kinds-smoke/p13001` and `build/e130-logs/` to the Intel and run
`PY=python3 nice -n 10 bash tools/claims-v3/e130/collect_e130.sh 'p130[1-2][0-9]' <copy>`; copy
`build/e130-out/2026-11-02-e130-int8-netlists/` to `docs/reports/data/`, write its README (results first; registered against
happened; departures dated; linking section 11 item 12), push, and drop the clause from the day's post.

## Files

All in `tools/claims-v3/e130/`: `README.md` (this), `predictions-e130.json` and `make_predictions_e130.py` (the freeze),
`e130-items.json` (the tiles as items), `e130_common.py` (the items, the orders, `install()`), `run_e130.py` (run_e78.py unchanged
with E130's items, and the board-power stop), `block_e130.sh`, `queue_e130.sh`, `run_e130.sh` (the card side), `reduce_e130.py`
(reduce_e78.py unchanged), `score_e130.py` (every rule), `collect_e130.sh`, `selftest_e130.py`, `selftest.txt`,
`selftest-power.txt`. Their sha256 are in `predictions-e130.json` › `harness`. Tiles: `tools/claims-v3/kinds/e130/` (Q136(a)'s).
Data: `docs/reports/data/2026-11-02-e130-int8-netlists/`.

## Amendments

### A1 — Mon 2 Nov 2026 (week 45), 10:35 PST: § Device commands sent, the build the list cannot read, and the corrected checker's run (written before any E130 data)

*Written on the Intel by the pass that corrects this registration after its verification (lane `fix-a3-e130-int8-netlists`),
before any E130 claim, launch or data. No E130 session has run: every ssh of the first lane to aifoundry3 stopped at a Tailscale
check (09:02–09:53 PST), so nothing reached the box and no device command was sent. Nothing above is changed, and A1–A3 change
no tile, prediction, threshold, band, rule, stop value or budget. A later session's own amendment takes the next number.*

1. **The build the nine reads are classified from is not the build aifoundry3 runs.** § Device commands sent reads them in
   et-platform `836a4ab`, the public BL2 0.22.0. aifoundry3 runs the thermal firmware build first flashed there on 7 October
   2026, which answers command 74 (`DM_CMD_GET_ASIC_PVT_SAMPLES`, absent from `836a4ab`), whose answer changed from whole
   degrees (7 Oct) to raw sensor codes (31 Oct) while the card kept reporting release 1.4.0 / BL2 0.22.0, and whose source is
   not held ([14-card-behaviour](../../../docs/findings/14-card-behaviour.md), "A finer reading exists on aifoundry3's firmware
   build"; [E89](../../../docs/reports/data/2026-10-31-e89-heat-low-power/README.md), "Joins and traps";
   [`dmcmd_table.json`](../dmcmd_table.json) › `source.caveat`, which names E130 among the aifoundry3 lanes this binds). So on
   the running build the nine reads' class rests on `836a4ab`'s handlers, the nearest public source, which that build may not
   share, and on their unchanged behaviour: they are the stock telemetry `ettelem config` and `ettelem sample` send, which this
   card has answered normally since 7 October, E127's run on it this morning included ([E127's registration](../e127/README.md),
   the note under its § Device commands sent; [its data README](../../../docs/reports/data/2026-11-02-e127-b-gate/README.md),
   correction C4). **The verdict stays GO, on that condition:** if the session-start config read or the smoke's telemetry comes
   back in another form than E127's run recorded (an error code, a missing field), the list may not describe what runs: NO-GO,
   and the session stops there, as for a changed binary.
2. **HEAD's checker, run.** The working-tree checker that § Device commands sent called another lane's work in progress was
   Q136(w)'s corrected revision, committed in `32e9c109` (09:23 PST, after this registration; [`dmcmd_audit.py`](../dmcmd_audit.py)
   sha256 `f29e91ca…`, `dmcmd_table.json` `50168632…`, both unchanged since; run here at `34ec50b8`). From the repository root on
   the same eleven files it reads **NO-GO, 31 send sites, 1 disallowed**: the same nine READs, PMIC access on `GET_ASIC_VOLTAGE`
   and `GET_MODULE_VOLTAGE` only (reads), and the conditional `STATS_RESET` at `lib.sh:154` (`start_sampler` forwards `"$@"`),
   which it now calls NO-GO until a reviewed exception clears it; no `VARIANT_UNRESOLVED` or `UNKNOWN_SUBCOMMAND` line. With the
   reviewed exception its docstring prescribes, `--except 'tools/claims-v3/lib.sh:154:STATS_RESET=block_e130.sh:106, the only
   start_sampler call E130 makes, passes the output file and the duration and nothing else, so no --reset-ms is forwarded'`, it
   reads **GO, 0 disallowed**; on the whole `e130/` directory with `lib.sh`, `run_e78.py`, `e78_common.py` and `reduce_e78.py`,
   GO at the same 31 sites; with `--deny-pmic-read`, NO-GO on the eight voltage-read lines, as it should (the reads his rule
   allows). The 36 sites above counted the dry-run message at `block_e130.sh:102` as a send; the config read is at `:103`. A
   session runs the same command at its own commit and keeps both outputs with the data.

### A2 — same time: § Stops, the second temperature stop is a die reading

The registered "(or a PMIC reading ≥ 80 °C)" is not a PMIC reading. `run_e78.py` (lines 188–191) stops when `temp_c.pmic` ≥
`--max-c` + 10, and at `836a4ab` `get_module_current_temperature` (`services/thermal_pwr_mgmt.c:732`) fills that field
(`pmic_sys`) from `pvt_get_minion_avg_temperature`, the minion shires' PVT average, as E127's correction C5 found on this card
with the same runner (it equals `minshire[0]` in 16,149 of E127's 16,155 samples). So both of E130's temperature stops are die
readings (70 and 80 °C), E130 reads no PMIC temperature, and its margin to the PMIC's own over-power and over-temperature limits
rests on the board stop (65 W) and the die stop (70 °C), with every run at most 5.1 W above its own zero and E127's passes here
this morning at most 53.84 W and 62 °C. No stop value changes. On the running build the field's source carries A1's residual too.

### A3 — same time: four wording corrections, and how R5 and R6 are read (no rule changes)

1. **B's odd/even ratio** (§ The question, § What I expect). "About 2.8× … on two cards" is a post hoc rail reading with no
   temperature term: 2.84× for E79's singles on this card and 2.85× [1.89, 6.09] for E102's on aifoundry1 card 1
   ([E102's `corrections-check.txt`](../../../docs/reports/data/2026-11-01-e102-balanced-bit-prices/corrections-check.txt), [C7]).
   E79's own scored B list here, the one this registration copies (`predictions-e130.json` › `card_precision_e79.b_list_board_fJ`),
   reads **2.22×** (odd − even +40.2 board-fJ); E102's registered masks read 1.97× [1.69, 2.33] on the rail and 1.82× [1.48, 2.17]
   on the board, and [its correction C6](../../../docs/reports/data/2026-11-01-e102-balanced-bit-prices/README.md) says "2–3×".
   So: **about 2.2× on aifoundry3 (E79, board), 2–3× on aifoundry1 card 1 (E102, post hoc)**. The expectation's "+40 board-fJ,
   0.7× the netlists' +60" was already E79's list, and no threshold or rule uses the ratio.
2. **The zeros' place** (§ What runs, the blocks' why; [`e130_common.py`](e130_common.py)'s docstring, hash-frozen and left as
   it is). "Its own zero immediately before and after it" overstates. Every item's own zero is **the nearest zero read on each
   side**: the inserted sign items (two a block) and, in the A blocks, `a1_7` and one magnitude item stand alone between two
   reads of their own zero; the other items run in pairs between zero reads (13010 opens `hb1 b1_2 b1_4 hb1`), so for each item
   of a pair the zero on one side is two runs away. Over the 20 block numbers, 200 item places are in 100 pairs and 60 stand
   alone. That is what `check_order` asserts, and the step interpolates the zero in time, as designed.
3. **R5 and R6 can FAIL with every netlist right** (§ Why these lines, § Precision). The self-test checks R1–R4 only. In its own
   model, in each netlist's world (whose sign ratios lie inside the shared bands), at σ = 0.015, 0.025 and 0.035 W a run, 200
   sessions each, over two seed sets ([`selftest_r56_e130.py`](selftest_r56_e130.py), [`selftest-r56.txt`](selftest-r56.txt)):
   **R6 reads FAILS in 177 of 4,200 sessions (4.2%; 1.5–8.5% by world and σ, ABOVE and BELOW alike)** and **R5 in 49 of 4,200
   (1.2%; 0–5%, the most in `plain`'s world, all ABOVE: its A ratio, 1.0108, sits at the band's upper edge, 1.011)**. So a FAIL
   says "every netlist is wrong about the sign bit in the same way" only beside those rates, and the data README states them
   beside any R5 or R6 reading. The rules and bands are unchanged.
4. **The post and the start** (§ How to run it). The clause is `using aifoundry3 for 1 h, until ~HH:MM PST [doc](<…>)`: the 30
   card-minutes plus a margin for the reads, rounded up to the half hour (the brief's form), as the lane's tooling writes it;
   "for 0.5 h" was wrong. A session starts only after A1–A3 are on origin/main, shares card 0 in turn with Q136's other
   aifoundry3 lanes (§ Card budget), and probes aifoundry3 only through a script that kills the ssh at once on a login link and
   at 15 s, never through a pipe that buffers its output (the first lane's first probe, at about 09:02, ran about 2 minutes
   before it was stopped).
