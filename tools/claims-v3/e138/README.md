# E138: int8's B side settled on the minion rail - E130's B list again, the rail as the registered primary (Q137, aifoundry3 card 0, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, before the claim of aifoundry3 and before any E138 run, in Q137 (the
owner's words that afternoon: "The overall goal is to be able to predict the power requirement and heat generation of various
kinds of numeric computations as accurately as possible"). **It answers item 12 of the kinds page's section 11**, "int8 at gate
level", the part E130 left open: whether the int8 multiplier recodes B
([horace-kinds-of-numbers § 11, item 12](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open);
E130's data README, [`2026-11-02-e130-int8-netlists`](../../../docs/reports/data/2026-11-02-e130-int8-netlists/README.md), its
"Open" list: "a follow-up would register the rail or many more B blocks as its primary"). Card: **aifoundry3 card 0 only**, 600 MHz
as its boot-time TDP of 0 latches it, TDP 0 / threshold 65 °C as read, never set. **E138 sends no write command of any kind**
(§ Device commands sent). Any change after this commit goes in Amendments, dated, before the data it touches.*

## What it does to predicting power and heat

The power model prices an int8 multiply by the bits that flip in its operands (fJ per flipped bit, per operand). E130 found A's
bits priced alike at every position (no recoder on A), and B's odd bits dearer than its even bits by an amount that sits between
the two gate-level structures Q136(a) froze. **The term E138 measures is the B operand's per-position price**: whether a model
needs one price for every B bit (flat, the no-recoder netlists), a price that alternates with bit parity at the Booth netlists'
4.2-4.4x, or a parity weight of its own (E130's rail: 1.79x). It matters for kinds whose flips sit on a few B bit positions
(small integers, sign patterns, quantised weights with few levels), not for uniform random int8, where every bit flips equally and
any of the three models gives the same mean. Heat follows power through the die-rise-per-board-watt term (Q137(m)'s M6); E138
changes the heat prediction only through that. **The out-of-sample error it reports** (registered here, computed by
`score_e138.py`, never a verdict): E130's rail per-bit prices of B bits 0-6 predicted from E138's under the flat, parity and
per-position models, each model's rms in rail fJ: a second session predicting the first, on the same card.

## Why E130's B side stayed open

E130's registered primary, the board's `p_raw`, read B's odd − even at +33.8 [+11.0, +56.7] fJ: the board meter's run-to-run
noise left a 46 fJ interval around a threshold, T_B = 30.68, that sits between the groups' predictions (Booth on B 54.8-66.2, no
recoder on B 0.5-1.2). The minion rail read the same contrast at +26.9 [+23.9, +29.8] rail fJ, eight times tighter, but as a
reported arm, and in rail fJ against board-fJ lines (E130's correction C1): at E78's frozen rail-per-board constant 0.81 it is
+33.2 [+29.6, +36.7] board-equivalent fJ, and it straddles T_B too. E138 makes the rail the registered primary, with the conversion
written down before the data, and adds the two readings that do not depend on where T_B sits.

## What runs

| | E130 (b259be11) | E138 | why |
|---|---|---|---|
| tiles | Q136(a)'s 26 int8 tiles, `tools/claims-v3/kinds/e130/`, used in place | **the same 26, byte for byte** (`e130-items.json` copied unchanged; sha256 checked) | no new prediction is needed |
| blocks | 6 B + 4 A (13010-13015, 13020-13023) | **B only: 13810-13819**, E130's B design (34 runs: 4 settling `hb1`, `hb1` between every pair of the 14 hb1 items, the two sign triples), each order seeded `Random("E138\|aifoundry3\|<pass>")` | the A side is decided (E130's R2 FLAT, R3 RISES at every arm) |
| a run | E78's `sparsity_host --test fma --type int8 --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, trains (`--preheat 0 --target 200 --quiet-s 0.2 --burnin 0`) | the same | E130's protocol |
| primary | the board's `p_raw` over each item's own zero | **the minion rail's `rail_raw`** (mean over [t0+2 s, t0+4 s), E78's reduction) over each item's own zero interpolated in time, ÷ designed flips × rate, **÷ c_rb = 0.81** (E78's `reduce_e78.py --c-rb` default, "frozen from E79") = board-equivalent fJ | the rail read B's contrast 8x tighter in E130 |
| reduction and gates | E78's `reduce_e78.py` unchanged via `reduce_e130.py --drop-dips`; E78's run and pass gates; the train gate (a zero's interior read > 0.25 W off its neighbours' line on the board) | the same code, ported to E138's pass numbers (`reduce_e138.py`, `e138_common.py`); the scorer is **E130's `score_e130.py` imported unchanged** (sha256 in `predictions-e138.json` › `harness.score_e130_sha256`), its `block_of` given E138's numbers | one scorer for both |
| arms (reported) | rail, p80, dips kept, gates off | **board** (`p_raw`, E130's primary), board `p80`, rail dips kept, rail gates off | a verdict that moves at an arm is marked arm-sensitive |
| smoke | 13001 | **13801**: E130's eight 2 s runs | cycles per op 318, tile dumps, the board level |
| budget | 1,740 s from the session-start read | **1,740 s (at most 30 card-minutes)**; E130's B blocks took 177-178 s, so about nine run (13810-13818); `queue_e138.sh` starts a block only if the longest B block so far fits in the budget and before 21:40 PST | the brief's ≈ 30 card-minutes |
| stops | die ≥ 70 °C, board ≥ 65 W | the same (E130's highest readings: 32.55 W, 55 °C) | |
| raw | `build/claims-v3/aifoundry3/kinds/p130*`, `build/e130-logs/` | `…/kinds/p138*`, `build/e138-logs/`; results `docs/reports/data/2026-11-02-e138-int8-b-rail/` | |

**No warm-up block.** E130's first B block read +75.9 board fJ against +16.5..+34.0 in the other five (post hoc, the board); on the
rail the same block read +23.1, inside the others' +24.2..+30.5, so the rail needs no set-aside rule and none is added: every kept
B block counts.

## Device commands sent

*The owner's rule of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send,
classified READ or WRITE from the firmware source; Q137 allows read-only PMIC voltage reads and no write but the statistics
reset, and **E138 does not send the reset**.* The sending code is E130's, ported with its pass numbers and names only (`lib.sh`
unchanged, the same `ettelem` binary `16037641…`, `block_e138.sh`'s config reads and its one `start_sampler` call as
`block_e130.sh`'s), so the list is E130's (its § Device commands sent, classified from et-platform `836a4ab`, BL2 0.22.0):
GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE (`ettelem config`: SP RAM copies);
GET_ASIC_FREQUENCIES (PLL register reads); **GET_ASIC_VOLTAGE** (`ettelem config` and `sample`: PVT reads and two PMIC
voltage-register reads); GET_MODULE_POWER, GET_SP_STATS (SP RAM copies); GET_MODULE_CURRENT_TEMPERATURE (PVT reads);
**GET_MODULE_VOLTAGE** (`ettelem sample`: nine PMIC voltage-register reads). **All nine are READs**; the two PMIC voltage reads are
the ones the owner's rule of 2 November 2026 allows. Never sent: SET_STATS_RUN_CONTROL (no `--reset-ms` anywhere), any
SET_*, the firmware-revisions query, any residency read. The host program opens the ops node only.

**The checker, `tools/claims-v3/dmcmd_audit.py`** (unchanged since `32e9c109`), from the repository root on `tools/claims-v3/e138/`,
`lib.sh`, `run_e78.py`, `e78_common.py`, `reduce_e78.py` and `e130/score_e130.py`: **NO-GO** without an exception, at the one
conditional site E130's A1 reviewed (`lib.sh:154`, `start_sampler` forwards `"$@"`, which might carry `--reset-ms`); with the
reviewed exception `block_e138.sh:106` (the only `start_sampler` call, which passes the output file and the duration and nothing
else) **GO, 31 send sites, 0 disallowed** ([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-except.txt`](dmcmd-audit-except.txt)).
E130's A1 caveat binds here unchanged: aifoundry3 runs a thermal firmware build first flashed on 7 Oct 2026 whose source is not
public, so the classes rest on `836a4ab`'s handlers and on these reads' unchanged behaviour on this card; if the session-start
`ettelem config` or the smoke's telemetry comes back in another form than E130's run recorded, it is NO-GO. **Verdict before the
first launch: GO.**

## The frozen numbers

From E130's registration (`predictions-e130.json`, sha256 in `predictions-e138.json` › `source`), nothing refitted:

| | value | from |
|---|---|---|
| T_B | **30.68** board fJ (24.85 rail fJ at c_rb 0.81) | E130, the midpoint between the groups' nearest predictions |
| c_rb | **0.81** | E78's frozen rail-per-board constant (E130's A bits 0-6 read 0.811 [0.756, 0.872], C1) |
| Booth on B's band, B odd − even | **[54.79, 66.18]** board fJ | the hull of `booth`'s and `booth_tree`'s frozen bands |
| no recoder on B, B odd − even | **[0.49, 1.23]** board fJ | the hull of `booth_swap`'s and `plain`'s |
| Booth on B's band, B odd / even | **[4.164, 4.394]** | the same hulls of the ratio |
| no recoder on B, B odd / even | **[1.047, 1.095]** | |
| E130's R2, R3 | FLAT, RISES | E130's registered primary, `b259be11` |

## Decision rules

On the primary over kept B blocks; a statistic is E130's per-block combination, its 95% interval t(n − 1) × sd / √n over blocks; a
ratio is Fieller's, paired. **Fewer than 3 kept B blocks: NOT SCORED.**

| rule | what | verdicts |
|---|---|---|
| **E138-R1** (the registered primary) | is B recoded? B's odd (1, 3, 5) − even (0, 2, 4), board-equivalent fJ, against T_B | **RECODED** if the low end ≥ 30.68; **FLAT** if the high end ≤ 30.68; else **INCONCLUSIVE** |
| **E138-R1n** | the same interval against the two groups' bands | **IN BOOTH ON B's BAND** / **IN NO RECODER's BAND** (overlaps that band only); **NEITHER (BETWEEN / ABOVE / BELOW)**; INCONCLUSIVE if it overlaps both |
| **E138-R1q** | B's odd / even on the rail (no unit, no c_rb) against the ratio bands | as R1n; NOT SCORED if unbounded |
| **E138-R4** | which multiplier: R1 with E130's R2 FLAT and R3 RISES | R1 RECODED: **BOOTH ON B**; FLAT: **NO BOOTH**; INCONCLUSIVE: **INCONCLUSIVE between BOOTH ON B / NO BOOTH** |

**Reported, never a verdict:** every rule at every arm; the pool of E130's six rail B blocks with E138's (E130's rail was seen
before this freeze, so the pool cannot be a registered test); the c_rb at which R1's reading would change; B's rail / board level
ratio; every item's rail and board fJ; the out-of-sample rms (§ What it does to predicting power and heat).

**What R1n and R1q settle that R1 may not.** T_B is a midpoint between two predictions the card may match neither of. R1n asks
whether the card's contrast is either group's, at the frozen scale; R1q asks the same with no scale at all. If both read NEITHER,
the statement is that neither structure's B list fits the card, whatever R1 reads: the multiplier's B side is a third thing.

## Precision, before the data

The self-test is E130's committed data scored by E138's code with E130's pass numbers (`score_e138.py --selftest-e130`): it gives
back E130's reported rail numbers exactly, +26.85 [+23.94, +29.76] rail fJ, **+33.15 [+29.56, +36.75] board-equivalent**, R1
INCONCLUSIVE, R1n and R1q NEITHER (BETWEEN), ratio 1.79 [1.68, 1.92], and its c_rb flip points 0.780 and 0.970 (E130's C1). With
nine kept blocks at E130's rail block sd (2.77 rail fJ), the half-width is about **2.1 rail fJ (2.6 board-equivalent)**: R1 reads
RECODED only if the mean stays above about 33.3 board-equivalent fJ, so at E130's mean (33.15) **R1 is close to even odds of
RECODED against INCONCLUSIVE**, and FLAT is far (the mean would have to fall 5 fJ). R1n and R1q are decided at any plausible
precision: the bands lie 20 fJ (and a ratio of 2.3) from E130's rail interval.

**What I expect, frozen so it can be wrong:** R1 INCONCLUSIVE, R1n NEITHER (BETWEEN), R1q NEITHER (BETWEEN), R4 INCONCLUSIVE
between BOOTH ON B / NO BOOTH; the board arm INCONCLUSIVE.

**The statement the page gets, decided now.** R1n and R1q NEITHER: "on two sessions of the same base words, B's odd bits cost about
X× its even bits on the rail: more than a multiplier without a recoder on B, half what the Booth-on-B netlists predict; the
model prices B's flips with a parity weight of its own". R1 RECODED or FLAT is stated with its c_rb dependence (the flip points).
**No tile, threshold, band or rule changes after this commit; only blocks that ran are scored.**

## What the rules cannot say

One card, one clock, E130's base words. The conversion to board fJ is E78's constant, measured on other tiles; B's own rail/board
level ratio was too wide in E130 (1.128 [0.883, 1.603]) to replace it. A rail-only verdict carries the rail's own lag (about 1 s,
E78's model) into the next read; the trains' paired zeros take most of it out. The netlists are Q133(a)'s, at zero delay.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__ tools/claims-v3/e138/` and
`tools/claims-v3/e130/score_e130.py` to the same paths under `aifoundry3:aifoundry/` (the tiles in `tools/claims-v3/kinds/e130/`
are there from E130). On aifoundry3, from `~/aifoundry`: `bash tools/claims-v3/e138/run_e138.sh setup` (no device access), the
day's post rewritten to add `using aifoundry3 for 1 h, until ~HH:MM PST [doc](<…>)`, then `run_e138.sh smoke`, `run_e138.sh go`,
`run_e138.sh wait` (bounded). Collect on the Intel: `PY=<python with numpy> nice -n 10 bash tools/claims-v3/e138/collect_e138.sh
'p138[1-2][0-9]' <copy>`.

## Files

`README.md` (this), `make_predictions_e138.py` → `predictions-e138.json` (the freeze, with every file's sha256),
`e130-items.json` (E130's, unchanged), `e138_common.py`, `run_e138.py`, `block_e138.sh`, `queue_e138.sh`, `run_e138.sh`,
`reduce_e138.py` (ports of E130's, pass numbers and names only), `score_e138.py` (new; imports E130's scorer), `collect_e138.sh`,
`dmcmd-audit.txt`, `dmcmd-audit-except.txt`.

## Amendments

*(none)*
