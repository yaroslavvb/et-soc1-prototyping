# E151: int8's B side on aifoundry3 card 0, the rail filter registered first - R1 RECODED: B's odd − even, +39.2 [+33.2, +45.2] board-equivalent fJ, clears the 30.68 fJ line (BOOTH ON B, with E130's A verdicts on this card); the filter removed nothing; per-position B prices carry across days and cards to 9-10% against 36-37% for one price

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 12, "int8 at gate level"**, and **rank 11 of Q138's final critic** (Tue 3 Nov 2026): "the registered verdict on B's recoder (E145
again with a spike filter registered first, or on aifoundry3) ... E145's design on aifoundry3, its rail filter written first. Rule: R1's
interval clears the 30.68 fJ line." It follows [E138](../2026-11-02-e138-int8-b-rail/README.md) (R1 INCONCLUSIVE, 0.2 fJ short) and
[E145](../2026-11-02-e145-int8-b-card1/README.md) (R1 INCONCLUSIVE on card 1 because its rail glitched). Q139, the owner's words of Mon 2 Nov
2026, about 18:40 PST: "feel free to settle any unanswered questions regarding horace's power model", with Q137's goal, "to be able to
predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible".*

*Tue 3 Nov 2026 (week 45), lane `a3-e151-int8-b`. Pre-registered in `a81541a3` (committed 04:27:20 PST and pushed by commit_lab by
04:27:23, before the claim at 04:29:33 and the first device access at 04:29:52):
[`tools/claims-v3/e151/README.md`](../../../../tools/claims-v3/e151/README.md), frozen numbers and the rail filter's test in
[`predictions-e151.json`](../../../../tools/claims-v3/e151/predictions-e151.json). No amendment. aifoundry3 card 0 at 600 MHz in every
sample; `ettelem config` read 28 times (the session's start, 04:29:52, and end, 05:03:25, and both ends of the stop-path test, the smoke
and every block): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV, all 28 alike, never set. **Every device-management command sent
was a read** (nine kinds, two of them PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows); no write of any
kind, no `--reset-ms` (`since_reset_ms` −1 in all 19,259 samples). Card session 04:29:51-05:03:25 PST, **33.6 of the 35 card-minutes
allowed**; the stop-path test, the smoke and **11 blocks (10 B, 1 A)** ran, every one `ok`; the registered train gate set two B blocks
aside, so **8 B blocks are kept**. Collected and scored on the Intel at about 05:06 PST by the registered `collect_e151.sh`, unchanged, on
the raw copy in this directory.*

## Results

**In plain words.** Two of the four gate-level versions of the chip's int8 multiplier recode the B operand in Booth digits (they predict
B's odd − even contrast at +54.8 to +66.2 fJ a flipped bit, and its odd bits at about 4.3× its even bits); two do not (+0.5 to +1.2 fJ,
about 1.07×). The registered test asks which side of the midpoint, 30.68 fJ, the card's interval falls. On aifoundry3 E130 and E138 had
read +33.2 and +35.9 with intervals reaching just below the line, and card 1's rail glitches spoiled E145's try. E151 wrote down the
glitch filter first, tested it on E145's data (it marks E145's 15 glitch samples and nothing else, and on E145's data it would have read
RECODED), and ran the same B tiles ten more times on aifoundry3. **On the minion rail B's odd − even reads +39.2 [+33.2, +45.2]
board-equivalent fJ over the 8 kept blocks: the interval clears the line, so the registered primary R1 reads RECODED**, and with this
card's A side as E130 registered it (A not recoded, A's sign step rising) **R4 reads BOOTH ON B**. The filter removed no sample (this
card's rail has never glitched: 0 in today's 19,259 and in 628,575 earlier samples), so the reading is the same with it off. The size
still matches neither netlist group: B's odd bits cost what Booth on B predicts (77.5 board-equivalent fJ against the Booth netlists'
78.1-78.5) and its even bits about twice as much (38.3 against about 18), so the ratio is 2.02 [1.80, 2.30], not 4.3 (R1n and R1q:
NEITHER (BETWEEN), as on every earlier session). **For predicting power**, per-position B prices hold out of sample: card 0's earlier
sessions predict today's to 9% rms (one price: 36%), and card 1's prices under the same filter predict card 0's to 10% (one price: 37%).

**1. The registered verdicts** (primary: the minion rail's `rail_raw` over each item's own zero, ÷ flips × rate, ÷ c_rb 0.81, the board's
dips and the rail's glitches removed; 8 B and 1 A blocks kept; [`results.md`](results.md), [`scored.json`](scored.json) › `primary.verdicts`):

| rule | what | primary (rail, filtered) | board | board p80 | rail, filter off | rail, dips kept | rail, gates off | expected |
|---|---|---|---|---|---|---|---|---|
| **E151-R1** | B odd − even vs T_B 30.68 | **RECODED** | INCONCLUSIVE | INCONCLUSIVE | RECODED | RECODED | RECODED | INCONCLUSIVE ✗ |
| E151-R1n | in either group's band? | **NEITHER (BETWEEN)** | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) ✓ |
| E151-R1q | B odd / even, no scale | **NEITHER (BETWEEN)** | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) ✓ |
| **E151-R4** | which multiplier (E138-R4's rule, E130's A verdicts) | **BOOTH ON B** | INCONCLUSIVE between BOOTH ON B / NO BOOTH | the same | BOOTH ON B | BOOTH ON B | BOOTH ON B | INCONCLUSIVE between BOOTH ON B / NO BOOTH ✗ |
| E151-R6 | B's sign, word 2 / word 1 | **FAILS (BELOW)** (0.61 [0.51, 0.71]) | HOLDS | HOLDS | FAILS (BELOW) | FAILS (BELOW) | FAILS (BELOW) | FAILS (BELOW) ✓ |
| E151-R2, R3, C1, R4s, R5, N | the in-session A control (one A block kept) | **NOT SCORED** | NOT SCORED | NOT SCORED | NOT SCORED | NOT SCORED | NOT SCORED | NOT SCORED ✓ |

R1, R4 and R6 move only at the two board arms, the noisier meter (the board read B's odd − even +29.6 [+12.4, +46.8], E138's board arm
+32.5 [+17.0, +48.0]: E138's registration explains why the rail is the primary). Every rail arm, the gates-off arm with all ten B blocks
included, reads RECODED.

**2. The numbers** (95% over blocks, exact t; `scored.json` › `primary`, `arms`, `pools`, `reported`):

| reading | n | value | 95% | card 0 before (E138 / E130) and card 1 (E145, filtered) |
|---|---:|---:|---|---|
| **rail: B odd − even, board-equivalent fJ** | 8 | **+39.2** | **[+33.2, +45.2]** | +35.9 [+30.5, +41.4] / +33.2 [+29.6, +36.7]; card 1 +36.1 [+31.8, +40.5] |
| rail: the same in rail fJ | 8 | +31.8 | [+26.9, +36.6] | |
| rail: B odd / even | 8 | 2.02 | [1.80, 2.30] | 1.91 [1.71, 2.16] / 1.79 [1.68, 1.92]; card 1 2.00 [1.81, 2.23] |
| board: B odd − even | 8 | +29.6 | [+12.4, +46.8] | +32.5 [+17.0, +48.0] / +33.8 [+11.0, +56.7] |
| rail, gates off (all 10 B blocks) | 10 | +38.5 | [+33.7, +43.3] | |
| rail: B's sign, word 2 / word 1 (R6) | 8 | 0.61 | [0.51, 0.71] | E138 0.69; card 1 0.65 [0.57, 0.73] |
| the A block, A odd − even, board-equivalent (reported; one block) | 1 | −2.7 | — | E130's four rail blocks −4.5, +0.7, +0.3, +1.2 (−0.6 [−4.7, +3.6]) |
| the A block, A's sign step (B = 0x55 − B = 1), board-equivalent (reported) | 1 | +64.6 | — | E130's four rail blocks 61.8-63.0 (+62.2 [+61.3, +63.1]); E130's board primary +67.8 [+58.8, +76.8] |
| c_rb at which R1 would change (reported) | | RECODED at c_rb ≤ 0.877, FLAT at ≥ 1.194 | | the frozen 0.81 and today's B-based scale 0.861 [0.688, 1.120] both read RECODED; E130's A-based 0.811 [0.756, 0.872] |
| pool, card 0's three sessions (E130 6 + E138 9 + E151 8 rail B blocks; reported) | 23 | +36.4 | [+33.5, +39.2] | RECODED (reported only) |
| pool, two cards (E151 8 + E145 13 under E151's filter; reported) | 21 | +37.3 | [+34.0, +40.6] | RECODED (reported only) |
| pool, all four sessions (reported) | 36 | +36.3 | [+34.0, +38.5] | RECODED (reported only) |

**3. The rail filter on today's data** ([`rail-census.json`](rail-census.json); registered in `railfilter_e151.py` before the run). It
marked **0 of 19,259 samples** (F1 0, F2 0) in the stop test, the smoke and the eleven blocks; the running-maximum field read 38.375 W in
every sample and the rail 6.52-14.35 W ([`telemetry.json`](telemetry.json)), so F2 could not fire, and the filter-off arm is identical to
the primary to the last digit (`reported.rail_filter_moved`: mean shift 0.0). The smoke gate's live check passed (205 distinct rail values
in 342 samples, 5-95% 6.52-12.38 W, longest constant run 3, the filter marking none). So on this card the registered filter is a guard,
and the verdict does not rest on it.

**4. Per bit** (rail fJ, primary; card 0 before = E130's and E138's 15 B blocks and E130's 4 A blocks; card 1 = E145 under E151's filter;
both frozen in `predictions-e151.json`):

| bit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (sign) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **E151, B** | **13.2** | **60.9** | **36.0** | **60.0** | **43.9** | **67.5** | **48.3** | **80.7** |
| card 0 before, B | 20.1 | 56.7 | 32.7 | 64.4 | 45.2 | 61.6 | 47.5 | |
| card 1 (filtered), B | 16.7 | 55.9 | 30.0 | 59.9 | 41.1 | 59.6 | 44.8 | |
| **E151, A (one block)** | **70.2** | **60.0** | **59.6** | **67.6** | **68.6** | **64.4** | **62.8** | **119.6** |
| card 0 before, A | 68.2 | 61.1 | 59.7 | 67.0 | 67.7 | 66.1 | 63.4 | |

The alternation on B repeats a fourth time: odd bits 1, 3, 5 at 60-68 rail fJ (75-83 board-equivalent, the Booth netlists' 78), even bits
0, 2, 4, 6 rising 13, 36, 44, 48 (16-60 board-equivalent, about twice the Booth netlists' even bits). A is flat at every position.

**5. What it does to predicting power and heat** (registered, reported; `scored.json` › `cross_session_card0`, `cross_card_from_card1_filtered`).
Frozen per-bit prices of bits 0-6 predicting today's, rms in rail fJ and as a share of today's mean (B 47.1 rail fJ, A 64.7):

| model of the operand's flips | B, from card 0's earlier sessions (day to day) | B, from card 1 under the filter (card to card) | A, from card 0's E130 | A, from card 1 |
|---|---:|---:|---:|---:|
| flat (one price for every bit: M5's and M6's shape) | 17.2 (36%) | 17.4 (37%) | 3.9 (6%) | 3.9 (6%) |
| parity (an odd and an even price: nearest M7's J8 shape) | 10.6 (22%) | 11.0 (23%) | 3.9 (6%) | 3.9 (6%) |
| **per position** (each bit's own price) | **4.3 (9%)** | **4.7 (10%)** | **1.2 (2%)** | **1.6 (2%)** |
| today's mean over the predictor's | 1.004 | 1.071 | 1.000 | 1.006 |

**The term tested: the int8 per-flip price by B bit position, out of sample on a new day and from another card.** One price per B bit
misses today's per-bit prices by 36-37%; a price per position by 9-10%, from either predictor; on A one price is already good to 6% and per
position to 2%. Out of sample, before → after: **B 36% → 9% (day to day on card 0) and 37% → 10% (card 1 → card 0)**. Card 0's scale held
to 0.4% across days; card 1's prices run 7% below card 0's. **R1 RECODED says why the term is structural**: B is recoded (Booth on B,
with E130's A side), so the per-position price is a property of the multiplier and not of these tiles, which is why it carries between
cards and sessions. No frozen model (M5, M6, M7) carries per-position B prices yet; M8 (Q139(m)) is where the term goes. It matters for
kinds whose flips sit on a few B bit positions (small integers, few-level quantised weights, sign patterns); for uniform random int8 every
bit flips alike and the models agree on the mean. **Heat**: E151 measures no heat term; the die read 49-55 °C (`minshire[0]`, the shires'
mean) at 22.7-32.8 W on the board, and the prediction of heat moves only through this power term and the die rise per board watt (0.87 °C
per W on this card, Q138(t)).

**6. Post hoc, labelled, never a verdict: the contrast stepped within the session** ([`posthoc/halves.txt`](posthoc/halves.txt) from
[`posthoc/halves_e151.py`](posthoc/halves_e151.py), written after the data were scored). The kept blocks' B odd − even reads, in session
order, 29.2, 28.6, 25.7, 23.6, then 38.1, 37.7, 38.1, 33.3 rail fJ: the first four average 26.8 and the last four 36.8 (Welch t 5.8). The
shift is not one scale: b1_3 rose 12.9 rail fJ while b1_4 and b1_0 fell 10.6 and 7.4, the other bits within 5. Neither E138 (t −0.3)
nor E145 (t −0.2) shows such a split, the two set-aside blocks read 31.4 and 26.3 (gates off), and the die, the board's range and the
rail's range were flat from the second block on (52-54 °C, 23.6-29.4 W, 6.9-11.5 W). The cause is unknown. The per-block sd, 5.82 rail fJ,
equals E138's 5.77, so the precision plan held; the first half alone would read about +33 [+28, +38] (inconclusive) and the second about
+45 [+41, +50] (recoded). The registered verdict is the session's, as registered, and the reported pool of card 0's three sessions (+36.4
[+33.5, +39.2], 23 blocks) also clears the line.

## Registered against what happened

| | registered | happened |
|---|---|---|
| blocks | the sequence 15110 ... 15119, 15130, 15120, ...; the budget rule decides; ten B and one A expected | **10 B (15110-15119) and 1 A (15130)**, B blocks 177-178 s, A 134 s; 15120 not started (projected past T0 + 2,055 s) |
| card time | ≤ 35 min | 33.6 min (2,014 s from the session-start read to the end read) |
| kept blocks | every block that passes the gates | **8 B** and 1 A: E130's registered train gate set aside 15110 (an `hb1` interior read −0.334 W off its line on the board) and 15116 (−0.370 and +0.266 W); the gates-off arm keeps all ten and reads +38.5 [+33.7, +43.3], RECODED |
| precision | ±5.10 at 10 kept B blocks at E138's block sd (±5.96 at 8) | **±6.01** at 8 kept blocks: the per-block sd was 5.82 rail fJ (E138's 5.77) |
| the meter | the rail live and clean on this card, checked again in the smoke | the smoke gate PASSED (live, and the filter marking none); no glitch in any block |
| stops | board ≥ 45 W, `minshire[0]` ≥ 68 °C, on live samples, by the main path and an in-run watcher; the path tested first | board at most 32.76 W (the A block), `minshire[0]` at most 55 °C; no stop; **the stop-path test fired all three on their first live reading** (the die stop on a sample read 0.078 s after it was taken, the board stop 0.114 s, the watcher 0.039 s, all from `telemetry.jsonl.raw`, no launch) |
| smoke gate | 318 cycles an op, 600 MHz, dumps equal their sha256, config 0/65/600, `since_reset_ms` −1, board below the stop, the rail live and clean | PASS on every part (`logs/session.log`) |
| frozen expectation | R1 INCONCLUSIVE (RECODED's simulated chance about 0.37 at card 0's pooled mean and E138's scatter), R1n and R1q NEITHER, R4 INCONCLUSIVE, R6 FAILS (BELOW), the A rules NOT SCORED, the filter removing nothing; per position < parity < flat, per position about 3-5 rail fJ, flat 13-15 | **R1 RECODED and R4 BOOTH ON B, against the expectation**: today's mean (+39.2) was higher than card 0's earlier sessions (+33.2, +35.9), not its scatter lower. Everything else as expected; per position 4.3 and 4.7 rail fJ as expected, flat 17.2 and 17.4 (36-37%), worse than the expected 13-15 |
| departures | — | none in the run. **D1** (analysis): § 6 and `posthoc/` were written after the data were scored; they change no verdict. |

## Device commands sent

As registered ([`tools/claims-v3/e151/README.md`](../../../../tools/claims-v3/e151/README.md) § Device commands sent, classified from
et-platform `836a4ab`, BL2 0.22.0's handlers; aifoundry3 runs a non-public thermal build first flashed on 7 Oct 2026, E130's A1 residual):
`ettelem config` through E128's `ettelem_guard.sh` (GET_MODULE_STATIC_TDP_LEVEL 25, GET_MODULE_TEMPERATURE_THRESHOLDS 21,
GET_MODULE_POWER_STATE 23, GET_ASIC_FREQUENCIES 53, GET_ASIC_VOLTAGE 32) 28 times; `ettelem sample --seconds --every-ms 100` through the
guard (GET_MODULE_POWER 33, GET_SP_STATS 60, GET_MODULE_CURRENT_TEMPERATURE 27, GET_MODULE_VOLTAGE 31, GET_ASIC_VOLTAGE 32,
GET_ASIC_FREQUENCIES 53) at 10 Hz in the stop-path test, the smoke and every block, 19,259 samples; `lib.sh`'s `die_c` (`ettelem sample
--seconds 1 --every-ms 500`, the same six commands) at both ends of every block. **All nine kinds are READs**, the two voltage commands
being PMIC voltage-register reads (two and nine a call), which the owner's rule of 2 November 2026 allows. Never sent: the statistics
reset (`since_reset_ms` −1 in every sample), any SET_*, the firmware-revisions query, a residency read, `dev_mngt_service` (the drain is
refused), any governor, TDP, threshold or clock set, any reset. On the box the session's preflight (`preflight_e151.sh`, Q136(w)'s checker)
read **GO, 32 send sites, 0 disallowed** at 04:29:51 before any device opened ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt));
the registration's run: NO-GO without the reviewed `lib.sh:154` exception, GO with it.

## Card and post

`et-who` at 04:06:42 and 04:27:39 (no-device setup), 04:29:14 (before the claim), 04:29:51 (the launch) and 05:03:25 (the session's end):
no process held a device node or card lock. Other users' idle logins were present on the host throughout, with no device process of
theirs (D1 of the harness: an idle login does not block). **The day's one card post in #community-lab**: no card post was dated Tue 3 Nov
at 04:29:21 (Mon 2 Nov's `1566837317765963987`, finished, was not touched), so this lane created it with `post.mjs` (staged, checked,
sent): message **`1567153765390487573`** at 04:29:33 PST, "<ai> **Claude says:** using aifoundry3 for 1 h, until ~05:29 PST [doc](<…>)".
Another lane added its aifoundry1 card 1 clause at 05:00. At 05:04:03, the session over, the aifoundry3 clause was dropped (EXPECT_TEXT,
dry run, then save), every other word kept: the post now reads "<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~05:30 PST
[doc](<…>)" ([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).

## What it changes

- **Item 12 (critic rank 11)**: **the structural verdict is registered: B is recoded** (E151-R1 RECODED, R4 BOOTH ON B with E130's A
  verdicts on this card), the first registered test of the four sessions (E130, E138, E145, E151) to clear the line, with the rail filter
  written first. It is one session's verdict, and § 6's step inside it is unexplained; the reported pools over three and four sessions also
  clear it. What stays open is the size: no frozen netlist reproduces the B list (R1n, R1q NEITHER), because the even bits cost about 2×
  Booth on B's zero-delay count. Why is the private half of rank 11 (the archive's glitch-aware count, Q139(v)), not this run.
- **The power model**: int8's per-flip term should carry B's per-position prices; out of sample they predict a new day on card 0 to 9%
  and card 0 from card 1 to 10%, against 36-37% for one price and 22-23% for an odd/even pair (M7's J8 shape); A's one price holds to 6%.
  M8 (Q139(m)) can take the per-position B prices as measured in four sessions on two cards.
- **The meter**: aifoundry3's rail stays clean (0 glitches in 19,259 more samples); the filter is now registered code
  (`tools/claims-v3/e151/railfilter_e151.py`) any later rail reading on card 1 can import.

## Files

`results.md`, `scored.json` (the scorer's output: every rule at every arm, the pools, the scales, the two out-of-sample tables),
`e151.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction), the arms (`e151-filteroff.*`, `e151-dipskept.*`,
`e151-gatesoff.*`, `runs-filteroff.csv`, `runs-dipskept.csv`, `runs-gatesoff.csv`), `score.log`, `rail-census.json` (the filter on every
block), `telemetry.json` (each block's extremes), `code.sha256`; `posthoc/` (labelled, after the data: `halves_e151.py`, `halves.txt`);
`logs/` (the session log with the stop-path test, the smoke gate and every block's lines, the queue, the session's config reads, the box's
preflight, the binaries' sha256, `push-and-claim-times.txt`, `dry/` the no-device dry runs); `aifoundry3/e151/p151*`,
`aifoundry3/e151-smoke/p15101`, `aifoundry3/e151-stoptest/p15102` (raw: per-run records, telemetry, tile dumps, manifests, the stop
test's STOP lines).
