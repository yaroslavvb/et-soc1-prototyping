# E145: int8's B side on a second card - E138's B design on aifoundry1 card 1, the minion rail as the registered primary, A's single bits as the control (Q138)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, before the claim of aifoundry1 card 1 and before any E145 run, in Q138 (the
owner's words that evening: "feel free to settle any unanswered questions regarding horace's power model", with Q137's goal, "to be able
to predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible"). **It
answers item 12 of the kinds page's section 11**, "int8 at gate level", the part E138 left open: whether the chip Booth-recodes B, as a
registered verdict ([horace-kinds-of-numbers § 11, item 12](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open);
E138's data README, [`2026-11-02-e138-int8-b-rail`](../../../docs/reports/data/2026-11-02-e138-int8-b-rail/README.md): R1 INCONCLUSIVE,
its interval's low end 0.2 fJ short of the line). Card: **aifoundry1 card 1 only** (`V3_DEVICE=1`, its own lock `etsoc-shire1.lock`),
600 MHz in every sample since 25 Sep, TDP 65 W / threshold 65 °C as read, never set. **E145 sends no write command of any kind** (§ Device
commands sent). Any change after this commit goes in Amendments, dated, before the data it touches.*

## What it does to predicting power and heat

The power model prices an int8 multiply by the bits that flip in its operands (fJ per flipped bit, per operand). On card 0 (aifoundry3),
E130 found A's bits priced alike at every position and E138 found B's priced by position: odd bits about 1.9× the even ones, so one
price per B bit misses a second session's per-bit prices by 29% rms and a price per position by 7%. **The term E145 tests is that
per-position B price, on a second card**: card 0's frozen per-bit prices (E130's and E138's 15 B blocks pooled, E130's 4 A blocks;
`predictions-e145.json` › `card0_prices_rail_fJ`, computed by this freeze from committed data, before any card-1 int8 single bit
exists) predict card 1's per-bit prices of bits 0–6 under three models, flat (one price), parity (an odd and an even price) and per
position. **The out-of-sample error it reports** (registered here, computed by `score_e145.py` › `cross_card`, never a verdict) is each
model's rms in rail fJ and as a share of card 1's mean, for B and for A: before = the flat B price the model carries now, after = card
0's per-position prices. It matters for kinds whose flips sit on a few B bit positions (small integers, sign patterns, few-level
quantised weights), not for uniform random int8. Heat: E145 measures no heat term; the die is recorded per block and heat follows
power through the die-rise-per-board-watt term (Q137(m)'s M6), so it changes the heat prediction only through this power term.

## Why a second card, and how many blocks

E138's rail read B's odd − even at **+35.9 [+30.5, +41.4]** board-equivalent fJ over nine blocks, against the registered line T_B =
30.68 (the midpoint between the Booth-on-B netlists' +54.8–66.2 and the no-recoder netlists' +0.5–1.2): INCONCLUSIVE by 0.2 fJ. Its
rail block scatter was **5.77 rail fJ** (7.13 board-equivalent) a block, 2.1× E130's. A verdict on one card is also a verdict on one
card's meter: E145 repeats E138's B design on aifoundry1 card 1 with enough blocks for the interval to clear the line at E138's scatter,
and E130's A design beside it as the control (§ The control).

**Precision, before the data** (`predictions-e145.json` › `precision`; half-width = t(0.975, n − 1) × 7.13 / √n, board-equivalent fJ):

| kept B blocks | 9 | 10 | 11 | **12** | 13 | 14 |
|---|---:|---:|---:|---:|---:|---:|
| half-width | 5.48 | 5.10 | 4.79 | **4.53** | 4.31 | 4.12 |
| R1 RECODED needs a mean of at least | 36.2 | 35.8 | 35.5 | **35.2** | 35.0 | 34.8 |

The 50 card-minutes hold about **12 B blocks and the 3 A blocks** (card 1 runs a 4 s train run in about 4.6 s, E137; a B block of 34 runs
about 185–200 s, an A block of 25 about 140–160 s), so the **expected half-width is ±4.5 board-equivalent fJ** (±3.7 rail fJ). At E138's
mean (+35.9) the interval would clear the line (low end 31.4); at card 0's two-session pool (+34.8) it would fall 0.4 short; at E130's
(+33.2) 2.5 short. **R1 RECODED is therefore about even odds**, FLAT is far (the mean would have to fall below 26.2), and the outcome
also depends on the session's own scatter (at E130's, 2.77 rail fJ, twelve blocks give ±2.2 and RECODED would need only 32.9).

## The meter

**Card 1's telemetry reports the minion rail.** Checked before this registration on committed data: E137's card-1 blocks of this
afternoon (`docs/reports/data/2026-11-02-e137-fp16-sign-rest/aifoundry1-c1/e137/p13711/telemetry.jsonl.gz`) carry `sp.minion_w` in every
sample, live (1,644 distinct values in 2,777 samples, 9.48–34.50 W, following the load); E82 re-fitted its lag at 1.00 s on this card
(E58 1.08 s; aifoundry3 0.95 s), and E137 used it post hoc. So **the registered primary is E138's**: the minion rail's `rail_raw` (E78's
mean over [t0+2 s, t0+4 s)) over each item's own zero interpolated in time, ÷ designed flips × rate, **÷ c_rb = 0.81** (E78's frozen
rail-per-board constant) = board-equivalent fJ. The smoke gate checks the rail again, live (≥ 20 distinct values, a 5–95% range ≥ 1.0 W,
no 30 identical samples in a row). **If it fails, no block runs**: the board's `p_raw` as primary would need about 60 B blocks (E138's
board arm scattered 20.2 fJ a block: ±5.2 needs n ≈ 60, about three card-hours), beyond the 50 card-minutes, so E145 would report NOT
RUN rather than a board session that cannot decide. Card 1's own scale is not assumed: A's single bits measure it in the same session
(§ The control), reported beside the frozen 0.81.

## What runs

| | E138 (aifoundry3, `07f59099`) | E145 (aifoundry1 card 1) | why |
|---|---|---|---|
| tiles | Q136(a)'s 26 int8 tiles, in place | **the same 26, byte for byte** (`tools/claims-v3/kinds/e130/`; `e130-items.json` copied unchanged, sha256 checked) | no new prediction is needed |
| B blocks | 13810–13818 (nine ran), E130's B design (34 runs: 4 settling `hb1`, `hb1` between every pair of the 14 hb1 items, the two sign triples) | **14510–14529**, the same design, each order seeded `Random("E145\|aifoundry1-c1\|<pass>")` | more blocks on a second card |
| A blocks | none (E130's A side was decided) | **14530–14532, E130's A design** (25 runs: 3 settling `ha1`, `ha1` between the groups of A's bits, the two A sign triples) | the control |
| sequence | B only | **14510 14530 14511 14512 14513 14531 14514 14515 14516 14532 14517 … 14523** (A second, sixth and tenth; the budget rule decides how many run) | the control spread over the session, its three blocks early enough to run |
| a run | E78's `sparsity_host --test fma --type int8 --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, trains (`--preheat 0 --target 200 --quiet-s 0.2 --burnin 0`) | the same | E130's protocol |
| primary | the rail, board-equivalent at 0.81 | the same | § The meter |
| reduction and gates | E78's `reduce_e78.py` unchanged via `reduce_e138.py --drop-dips`; E78's run and pass gates; E130's train gate (a zero's interior read > 0.25 W off its neighbours' line, on the board's `p_raw`) | the same code via `reduce_e145.py`, whose one change is E137's: E78's configuration gate accepts card 1's reads (TDP 65, threshold 65) where it accepts aifoundry3's (0, 65) | card 1's TDP is 65 W |
| scorer | `score_e138.py` (imports `score_e130.py`) | **`score_e145.py`**, importing `score_e138.py` and so `score_e130.py` unchanged (sha256 in `predictions-e145.json` › `harness`); E130's R2–R6 and its netlist test on this session's A and B blocks; the exact t beyond n − 1 = 10 (E130's table approximates there, E138's C5) | one scorer for all three sessions |
| arms (reported) | board `p_raw`, board `p80`, rail dips kept, rail gates off | the same | a verdict that moves at an arm is marked arm-sensitive |
| smoke | 13801: E130's eight 2 s runs | **14501**, the same eight, after the stop-path test **14502** | cycles per op 318, tile dumps, the clock, the rail |
| budget | 1,740 s (30 card-minutes) | **3,000 s (50 card-minutes) from the session-start config read**, 90 s reserved for the end read; a block starts only if the longest block of its kind so far (first estimates B 200 s, A 160 s) ends inside it and before 23:30 PST | the brief's ≤ 50 card-minutes; no session starts after 23:00, every run ends by 23:50 |
| stops | die ≥ 70 °C (first shire), board ≥ 65 W | **board ≥ 60 W, any minion-shire reading ≥ 72 °C, both on live samples**; `run_e78`'s own cap 72 °C (shire mean; PMIC 82 °C) | § Stops |
| raw | `build/claims-v3/aifoundry3/kinds/p138*` | `~/nekko/build/claims-v3/aifoundry1-c1/kinds/p145*`, `build/e145/`; results `docs/reports/data/2026-11-02-e145-int8-b-card1/` | |

**No warm-up block**, as E138: every kept block counts. Card 1's session-level files come from E137's harness (the session script, the
telemetry guard, the queue's budget anchored on T0), ported, each change marked in the file.

## The control

A's single bits run beside B's because on A the four netlists and card 0 agree on what a correct measurement shows: A's odd and even
bits cost the same (no recoder on A; E130 −1.7 [−6.6, +3.2] fJ, FLAT), and A's sign bit costs more when B is dense (E130 +67.8
[+58.8, +76.8], RISES). On card 1 they test three things the B list cannot: that the rail on this card does not make an odd/even
alternation of its own (a FLAT A side is a negative control for B's alternation); that the card shows a structural effect it should (A's
sign step, a positive control); and the card's own rail-per-board scale, from A's bits 0–6, whose steps (1.1–3.5 W) the board resolves
(E130 on card 0: 0.811 [0.756, 0.872]). E145-C1 scores the first two; the scale is reported.

## Stops

**Every stop reads live samples.** `run_e78.py` reads the newest line of the block's running sampler file, `telemetry.jsonl.raw` (which
`lib.sh`'s `start_sampler` writes one line a sample while `ettelem sample` runs), before every launch and every 0.1 s while it waits
between runs; it refuses a line older than its stale limit. `run_e145.py` wraps that read (E137's guard, copied): a line with
**`board_w` ≥ 60 W**, or **any minion-shire reading ≥ 72 °C**, writes the pass's STOP file (which the host program and the runner
watch) and ends the pass with EXIT_HOT; the queue then stops. The message records the line's `t_ms` and its age when read. Margin: E137's
fp32 anchors on this card read at most 60.4 W on the board (E128 59.79 W, no shire above 65 °C); int8's single-bit trains on card 0 read
at most 31.67 W (E138's smoke) and 55 °C, and card 1 idles near 31 W, so the trains should stay under about 40 W, 20 W below the stop and
35 W below the PMIC's 75 W alarm. **The stop path is tested on the card before any launch** (E139's 65 W stop watched a file written
only at the pass's end and never read a sample): pass 14502 starts the sampler, then runs `run_e145.py` twice with the die stop at
1.0 °C and then the board stop at 1.0 W; each must end on its first reading with EXIT_HOT and a STOP line naming its stop and a sample
read at most 2.0 s after it was taken, from `telemetry.jsonl.raw`, with no launch made. If either fails, nothing else runs. Also: the
STOP files (`build/e145/STOP`, `build/claims-v3/STOP`, `build/kinds-STOP`); another user's device process, a device node or this card's
lock held by anyone else (D1: an idle login does not block on aifoundry1); `timeout 10` on every device process.

## Device commands sent

*The owner's rule of Mon 2 Nov 2026: every device-management command the run's harness, sampler, host program and helpers send,
classified READ or WRITE from the firmware source of the running build; read-only PMIC voltage reads are allowed and no write but the
statistics reset, and **E145 does not send the reset**.* Card 1 reports release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.3.0 since 31 Oct 2026
(E82 A1, E128 C1), so the version-matched source is et-platform `836a4ab` (Q136(w)'s table, `tools/claims-v3/dmcmd_table.json`). Every
telemetry call goes through E128's `tools/claims-v3/e128/ettelem_guard.sh` unchanged (it admits `ettelem config` with no argument and
`ettelem sample --seconds <n> --every-ms <n>` only, and refuses anything else before the device opens), and `lib.sh`'s drain is
replaced by a refusal, so the vendor tool is never run. The list is E137's on this card:

| sent by | command (id) | what the service processor does (BL2 0.22.0) | class |
|---|---|---|---|
| `ettelem config` (session start and end; both ends of every block) | GET_MODULE_STATIC_TDP_LEVEL (25) | RAM copy | READ |
| | GET_MODULE_TEMPERATURE_THRESHOLDS (21) | RAM copy | READ |
| | GET_MODULE_POWER_STATE (23) | RAM copy | READ |
| | GET_ASIC_FREQUENCIES (53) | PLL register reads | READ |
| | GET_ASIC_VOLTAGE (32) | PVT reads and **two PMIC voltage-register reads** (allowed) | READ |
| `ettelem sample --seconds --every-ms 100` (each block's sampler, 10 Hz) | GET_MODULE_POWER (33) | RAM copy the SP keeps from the PMIC | READ |
| | GET_SP_STATS (60) | RAM copy of the SP's op stats | READ |
| | GET_MODULE_CURRENT_TEMPERATURE (27) | PVT register reads | READ |
| | GET_MODULE_VOLTAGE (31) | **nine PMIC voltage-register reads** (allowed) | READ |
| | GET_ASIC_VOLTAGE (32), GET_ASIC_FREQUENCIES (53) | as above | READ |

**All nine are READs.** Never sent: SET_STATS_RUN_CONTROL (no `--reset-ms` anywhere), any SET_*, the firmware-revisions query, any
residency read, `dev_mngt_service`. The host program `sparsity_host` opens the ops node only (DMA to device DRAM, kernel launches);
`et-who`, `et-holders` and `et-lab-manifest` read host state (`/proc`, lock files, sysfs) and open no device node. **The checker,
`tools/claims-v3/dmcmd_audit.py`** (unchanged), on every E145 file, `lib.sh`, the guard, E78's runner, common module and reducer, the
two imported scorers and the workload's host source: **NO-GO** without an exception, at the one conditional site E130's A1 reviewed
(`lib.sh:154`, `start_sampler` forwards `"$@"`, which might carry `--reset-ms`); with the reviewed exception (`block_e145.sh`'s only
`start_sampler` call passes the output file and the duration and nothing else, and the guard refuses `--reset-ms`) **GO, 32 send sites,
0 disallowed** ([`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt), [`dmcmd-audit.txt`](dmcmd-audit.txt)). `session_e145.sh` runs
the same check on the box (`preflight_e145.sh`) and opens no device unless it reads GO. **Verdict before the first launch: GO.**

## The frozen numbers

From E138's registration (`predictions-e138.json`, sha256 in `predictions-e145.json` › `source`; E130's and Q136(a)'s numbers), nothing
refitted:

| | value | from |
|---|---|---|
| T_B | **30.68** board fJ | E130, the midpoint between the groups' nearest predictions |
| T_A, T_S | **27.58**, **18.07** board fJ | E130 |
| c_rb | **0.81** | E78's frozen rail-per-board constant |
| Booth on B's band, B odd − even | **[54.79, 66.18]** board fJ | the hull of `booth`'s and `booth_tree`'s frozen bands |
| no recoder on B, B odd − even | **[0.49, 1.23]** board fJ | the hull of `booth_swap`'s and `plain`'s |
| Booth on B, B odd / even | **[4.164, 4.394]** | the same hulls of the ratio |
| no recoder on B, B odd / even | **[1.047, 1.095]** | |
| the four netlists' bands on E130's three separators | as frozen | `predictions-e145.json` › `netlists` |
| card 0's per-bit rail prices, B bits 0–6 | 20.1, 56.7, 32.7, 64.4, 45.2, 61.6, 47.5 rail fJ (mean 46.9; odd 60.9, even 36.4) | E130's 6 and E138's 9 B blocks, computed by this freeze |
| card 0's per-bit rail prices, A bits 0–6 | 68.2, 61.1, 59.7, 67.0, 67.7, 66.1, 63.4 rail fJ (mean 64.7) | E130's 4 A blocks |

## Decision rules

On the primary over kept blocks; a statistic is E130's per-block combination, its 95% interval t(n − 1) × sd / √n over blocks; a ratio
is Fieller's, paired. **Fewer than 3 kept blocks of a kind: that kind's rules NOT SCORED.**

| rule | what | verdicts |
|---|---|---|
| **E145-R1** (the registered primary) | is B recoded? B's odd (1, 3, 5) − even (0, 2, 4), board-equivalent fJ, against T_B | **RECODED** if the low end ≥ 30.68; **FLAT** if the high end ≤ 30.68; else **INCONCLUSIVE** |
| **E145-R1n** | the same interval against the two groups' bands | IN BOOTH ON B's BAND / IN NO RECODER's BAND / NEITHER (BETWEEN, ABOVE, BELOW) / INCONCLUSIVE if both |
| **E145-R1q** | B's odd / even on the rail (no unit, no c_rb) against the ratio bands | as R1n; NOT SCORED if unbounded |
| **E145-R2** (control) | A's odd − even against T_A | RECODED / FLAT / INCONCLUSIVE |
| **E145-R3** (control) | A's sign, B = 0x55 − B = 1, against T_S | RISES / FLAT / INCONCLUSIVE |
| **E145-C1** (the control) | does card 1's A side read as card 0's (R2 FLAT, R3 RISES)? | **REPRODUCES card 0** if both; **DIFFERS from card 0** if R2 RECODED or R3 FLAT; else INCONCLUSIVE |
| **E145-R4** | which multiplier on card 1 alone: E130-R4's rule on (R1, R2, R3) | BOOTH ON B / BOOTH ON A / NO BOOTH (with "n of 3 rules decided") / INCONCLUSIVE between … / NONE OF THE FOUR |
| E145-R5, E145-R6 | the shared predictions (sign bit, word 2 / word 1, in the shared band) | HOLDS / FAILS (ABOVE, BELOW) |
| E145-N | each netlist's frozen prediction on E130's three separators | SURVIVES / EXCLUDED by … |

**Reported, never a verdict:** every rule at every arm; the pools of card 1's B blocks with card 0's (E130's six, E138's nine), and card 0
alone; card 1's own rail/board scale from A's bits 0–6 and from B's (Fieller), and R1 read at the A-based scale; the c_rb at which R1's
reading would change; every item's rail, board-equivalent and board fJ; card 0's per-bit prices predicting card 1's (flat, parity, per
position; B and A); the telemetry's extremes per block.

## What I expect, frozen so it can be wrong

R1 **INCONCLUSIVE** (about even odds against RECODED; § Precision), R1n and R1q **NEITHER (BETWEEN)**, R2 FLAT, R3 RISES, C1 REPRODUCES
card 0, R4 **INCONCLUSIVE between BOOTH ON B / NO BOOTH**, R5 HOLDS, R6 **FAILS (BELOW)** (as card 0's rail: E138's b2_7 / b1_7 = 0.69,
E130's rail arm FAILS), every netlist EXCLUDED by B's odd − even. Out of sample: per position < parity < flat on B, per position about 5
rail fJ (about 10% of card 1's mean), flat about 13 (about 29%); on A flat and per position alike.

**The statement the page gets, decided now.** R1 RECODED with R1n and R1q NEITHER: "on a second card B's odd − even clears the line, so
the multiplier's B side is recoded in a way neither frozen netlist reproduces: its odd bits cost what Booth on B predicts, its even bits
about twice". R1 INCONCLUSIVE: "two cards, three sessions, the line not cleared by a registered test; the structural question stays
open, the prediction is answered by per-position prices". R1 FLAT: "the second card reads B's alternation below the line". Each with
its c_rb dependence (the flip points and the A-based scale). **No tile, threshold, band or rule changes after this commit; only blocks
that ran are scored.**

## What the rules cannot say

One clock, E130's base words, a second card of the same chip. The conversion to board fJ is E78's constant, measured on aifoundry3; card
1's own scale is reported, not used, because a scale measured in-session would carry its own ±7% into R1 (E130's A-based scale) and
make the line harder to clear. The rail's lag (about 1.0 s on this card) carries into the next read; the trains' paired zeros take most
of it out, as on card 0. Card 1's board meter reads launch gaps (E82 A2): the primary removes those dips before the board-based train
gate reads them, and the gates-off arm shows what the gate moved. The netlists are Q133(a)'s, at zero delay.

## Protocol (for this lane)

1. **Desk, before this commit:** `selftest_e145.py` (`selftest-e145.txt`): the scorer gives back E138's rail numbers (+35.95 [+30.47,
   +41.42], 1.91 [1.71, 2.16], R1 INCONCLUSIVE, R1n and R1q NEITHER) and E130's (+33.15 [+29.56, +36.75] board-equivalent, A FLAT and
   RISES, A's scale 0.811 [0.756, 0.872]) on their own pass numbers; the stop guard fires on a live line at 1 W and 1 °C and passes it at
   60 W / 72 °C; the gate passes a correct stop test and fails a stale or a launched one. The checker as above.
2. **On the box, no device opened** (after this commit is on origin/main; files rsynced to `aifoundry1:nekko/` at the same paths): the
   harness check (`check_e145.py`), the tiles (`e145_common.py --verify`), the preflight, dry runs of a B, an A and the smoke block, the
   queue's budget rule on stub blocks.
3. **Claim:** the day's one post in `#community-lab` rewritten with `using aifoundry1 card 1 for 1.5 h, until ~HH:MM PST` beside the
   clauses held then; `et-who` free on card 1.
4. **Session:** `E145_T0=$(date +%s) setsid nohup bash tools/claims-v3/e145/session_e145.sh` on the box: the check, the preflight, the
   start config read, the stop-path test, the smoke and its gate, the queue, the end config read.
5. **Collect** on the Intel: `collect_e145.sh` over a copy of the blocks; the README results first.

## Files

`README.md` (this), `make_predictions_e145.py` → `predictions-e145.json` (the freeze, with every file's sha256), `e130-items.json`
(E130's, unchanged), `e145_common.py`, `run_e145.py`, `block_e145.sh`, `queue_e145.sh`, `session_e145.sh`, `preflight_e145.sh`,
`check_e145.py`, `smoke_gate_e145.py` (the card files), `reduce_e145.py`, `score_e145.py`, `collect_e145.sh`, `telemetry_max_e145.py`,
`selftest_e145.py` → `selftest-e145.txt` (the desk files), `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`.

## Amendments

*(none)*
