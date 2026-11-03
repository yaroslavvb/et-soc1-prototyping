# E159: a large GEMM's sustained power and governed clock, G3's blind test on three new shapes, under aifoundry2's own governor

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 1**
("Where a large GEMM falls") and **item 6** (the power model). It answers **rank 3 of Q138's final critic**: *"A large GEMM's sustained power and governed
clock on aifoundry2 ... Register G3 (P0's power, closed through the frozen chain and the trip rule) for 2-3 new GEMM shapes held 80-120 s in fp32 random,
int8 full and zeros, with the predictions frozen first. Rules: sustained clock within 15 MHz, board within 2 W, window die within 1 °C. Score the chain on
the measured trace beside it (registered this time) and E136's law as the old arm."* G3 is [Q139(q)'s](../2026-11-03-q139q-gemm-g3/README.md). Q139 continues
the owner's ask of 2 November 2026: *"feel free to settle any unanswered questions regarding horace's power model"*, with Q137's goal, *"to be able to
predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible"*.*

*Tue 3 Nov 2026 (week 45), Q139. **Frozen first:** Q139(q)'s design and predictions at `91def7c4` (04:16:13 PST; its corrections `ea38c8c3`, 05:08:35,
changed no frozen file; `score_e159.py check` OK on all 28 files at about 05:20, at 05:31 and again in the reduction). **Pre-registered** in `d8badb73`
([`tools/claims-v3/e159/E159.md`](../../../../tools/claims-v3/e159/E159.md): the protocol written from the frozen design, the reduction, a self-test, a toy-card
dry run of the whole queue and the device-command audit), committed at 05:31:46 PST and pushed by 05:32:04, before the claim (05:32:57-05:33:21) and the
first card touch (05:33:58). **aifoundry2 card 0 under its own governor**: `ettelem config` read 65 W / 65 °C (low_power, 600 MHz, 519 mV) at the queue's
start and end and after every run; nothing was set, no statistics reset, no firmware-revisions query, no residency read, **no WRITE command of any kind**
([Device commands sent](#device-commands-sent)). E136's binary, unchanged (its sha256 checked before every session). The card post was the day's single
post in #community-lab, message `1567153765390487573`, rewritten at 05:33 PST to "using aifoundry2 for 1 h, until ~06:33 PST" (it had read "— released")
and at 05:55 PST to drop that clause, the two other cards' clauses kept word for word. **18.95 card-minutes** (05:33:58 to 05:52:55 PST): the smoke, the two
stop-path tests and one session of ten runs (17.8 min), none refused, none cut, no stop fired.*

## The answer

**Blind, on nine sustained holds of three GEMM shapes nobody had run, G3 reads the governed clock to 8.7 MHz, the board to 1.94 W and the window die to
0.99 °C rms. E136's law, the old arm, reads them to 41.2 MHz, 3.99 W and 1.35 °C.** G3's rms is below the law's on all three quantities, the registered
comparison. **As registered, though, G3 FAILS all three rules**, because a rule passes only when every hold is inside its band: the clock is inside 15 MHz
on 8 of 9 holds, the board inside 2 W on 5 of 9, the window die inside 1 °C on 6 of 9 ([`results.json`](results.json) `all_scored`). On the registered
subset (the six fp32 random and int8 full holds) it is 5 of 6 on each, and one hold misses all three: `H1` fp32 random.

- **The governor holds fp32 random at the trip, as G3 says.** `H2` and `H3` fp32 random held their window die at 65.55 and 65.66 °C (G3: 65.49, 65.50) at
  697.7 and 649.7 MHz (G3: 708.0, 663.6), with the board within 0.6 W of G3. E136's law called them 781 and 739 MHz at 62.06 W: 84-89 MHz and 7.6-8.1 W
  off. The clock falls with the shape's power, about 50 MHz from `H2` to `H3`, as G3 predicted.
- **`H1` fp32 random's power level was 7.2 W under P0.** Its first second at 800 MHz drew 49.9 W against P0(800)'s 57.1 W. So its board ran 3.7 W under G3,
  its die never reached the trip (62.1 °C), and its clock read 784.5 MHz, 15.5 MHz under G3's 800 (91.5% of its window's samples at 800 MHz). The
  registered attribution calls the clock and board misses **P0's level** (the first second more than 4 W from P0(800)), and the die miss the power path
  (the chain on the measured trace reads that window to +0.87 °C).
- **Zeros: G3 is 2.4-2.5 W high on all three shapes**, and its window die 1.0-1.6 °C high. The first second sat 1.5-2.1 W under P0(800), inside the
  attribution's 4 W band, so by the registered rule the board miss is not P0's level. Given each hold's first second the zeros' board error falls to 0.3-0.8 W
  (post hoc). The chain on the measured trace reads the zeros' die to within 0.5 °C, so the die miss is the power path.
- **Heat given the watts is right on every hold.** Q138(t)'s frozen chain, run on the measured board trace, reads all nine window dies within 1 °C, 0.41 °C
  rms [0.21, 0.58] (post hoc interval). Every die miss of G3 is the power path, not heat.
- **int8 full is inside every band on every shape** (clock 0 to −5.7 MHz, board −1.10 to +0.79 W, die −0.74 to +0.82 °C).

| hold | measured: MHz, board W, window die °C | **G3** (frozen, from the hold's own start) | G3 error | inside 15 MHz / 2 W / 1 °C | E136's law | E136's law error | chain on the measured trace: die (error) | p800 − P0(800) |
|---|---|---|---|---|---|---|---|---|
| H1-fp32-randn | 784.5, 55.25, 62.09 | **800.0, 58.93, 63.46** | −15.5, −3.68, −1.37 | **no** / **no** / **no** | 799.8, 57.07, 59.55 | −15.4, −1.82, +2.54 | 61.22 (+0.87) | −7.21 W |
| H1-int8-full | 800.0, 43.81, 59.78 | **800.0, 44.90, 60.52** | +0.0, −1.10, −0.74 | yes / yes / yes | 800.0, 44.62, 58.93 | +0.0, −0.81, +0.85 | 60.01 (−0.23) | −1.25 W |
| H2-fp32-randn | 697.7, 54.46, 65.55 | **708.0, 53.83, 65.49** | −10.3, +0.62, +0.06 | yes / yes / yes | 781.3, 62.06, 65.42 | −83.7, −7.60, +0.13 | 65.53 (+0.02) | −1.29 W |
| H2-int8-full | 794.3, 45.75, 60.95 | **800.0, 45.46, 60.57** | −5.7, +0.29, +0.38 | yes / yes / yes | 800.0, 45.16, 59.15 | −5.7, +0.59, +1.80 | 60.83 (+0.12) | +0.47 W |
| H3-fp32-randn | 649.7, 54.00, 65.66 | **663.6, 54.04, 65.50** | −13.8, −0.04, +0.16 | yes / yes / yes | 738.5, 62.06, 65.50 | −88.8, −8.06, +0.16 | 65.52 (+0.14) | +3.48 W |
| H3-int8-full | 795.4, 47.10, 61.88 | **800.0, 46.31, 61.06** | −4.6, +0.79, +0.82 | yes / yes / yes | 800.0, 45.98, 59.49 | −4.6, +1.12, +2.39 | 61.35 (+0.53) | +2.15 W |
| H1-fp32-zeros | 794.9, 35.98, 55.54 | **800.0, 38.43, 57.16** | −5.1, −2.45, −1.62 | yes / **no** / **no** | 800.0, 38.45, 55.98 | −5.1, −2.47, −0.44 | 56.03 (−0.50) | −1.54 W |
| H2-fp32-zeros | 794.3, 36.04, 54.00 | **800.0, 38.52, 55.38** | −5.7, −2.49, −1.38 | yes / **no** / **no** | 800.0, 38.23, 54.37 | −5.7, −2.19, −0.37 | 54.15 (−0.15) | −2.09 W |
| H3-fp32-zeros | 794.9, 36.03, 53.98 | **800.0, 38.46, 54.96** | −5.1, −2.43, −0.97 | yes / **no** / yes | 800.0, 38.12, 53.95 | −5.1, −2.09, +0.04 | 53.69 (+0.30) | −1.70 W |

Errors are measured − predicted. The window is the in-kernel samples of the last 40 s of work; the die is the firmware's whole-degree minion-shire mean.
Sources: [`results.json`](results.json) `rows` (`meas`, `pred`, `err`, `attribution`), printed in [`reduce.txt`](reduce.txt).

| arm (measured − predicted, nine holds; the registered subset of six in brackets) | clock, MHz rms (mean) | inside 15 MHz | board, W rms (mean) | inside 2 W | window die, °C rms (mean) | inside 1 °C |
|---|---|---|---|---|---|---|
| **G3** (the primary) | **8.7 (−7.3)** [9.9] | 8 of 9 [5 of 6] | **1.94 (−1.16)** [1.62] | 5 of 9 [5 of 6] | **0.99 (−0.52)** [0.74] | 6 of 9 [5 of 6] |
| G3 at Q138(t)'s constants (0.442 W/°C, 65.9 °C) | 14.5 (+4.9) [17.4] | 7 of 9 [4 of 6] | 3.08 (−2.37) [2.90] | 4 of 9 [4 of 6] | 1.61 (−1.20) [1.54] | 4 of 9 [4 of 6] |
| **E136's law** (the old arm) | 41.2 (−23.8) [50.3] | 6 of 9 [3 of 6] | 3.99 (−2.59) [4.62] | 4 of 9 [4 of 6] | 1.35 (+0.79) [1.64] | 6 of 9 [3 of 6] |
| Q138(t)'s chain on the measured trace (heat given the watts) | — | — | — | — | 0.41 (+0.12) [0.43] | 9 of 9 [6 of 6] |
| G3 given the hold's first second (diagnostic, no verdict) | 10.9 (−5.3) [12.9] | 6 of 9 [3 of 6] | 1.45 (+0.14) [1.72] | 8 of 9 [5 of 6] | 0.86 (+0.13) [0.99] | 8 of 9 [5 of 6] |

Sources: `results.json` `all_scored.summary` and `registered_subset.summary`.

**Intervals** (post hoc, [`posthoc.txt`](posthoc.txt) §1, 95% bootstrap over the nine holds): G3 clock [5.2, 11.5] MHz, board [1.09, 2.60] W, die [0.64, 1.26] °C;
E136's law [5.3, 64.0] MHz, [1.59, 5.87] W, [0.51, 1.88] °C. With nine holds the paired gain (the law's rms minus G3's) is resolved only for the die on
the registered subset ([0.43, 1.29] °C); for the clock it is +32.5 MHz [−0.1, 53.5] and for the board +2.05 W [−0.65, 4.32] over all nine, because on the
int8 and zeros holds both arms say 800 MHz and nearly the same watts. On the three fp32 random holds, where the arms differ, E136's law misses by 71.0 MHz,
6.48 W and 1.47 °C rms and G3 by 13.4 MHz, 2.16 W and 0.80 °C (§2).

## Registered against what happened

| rule (Q139(q)'s, `predictions-e159.json` `rules`) | registered | what happened |
|---|---|---|
| clock within 15 MHz, every scored hold | G3 PASSES when every hold is inside | **FAIL (8 of 9)**; the subset FAIL (5 of 6): `H1` fp32 random −15.5 MHz |
| board within 2 W, every scored hold | the same | **FAIL (5 of 9)**; the subset FAIL (5 of 6): `H1` fp32 random −3.68 W, the three zeros −2.43 to −2.49 W |
| window die within 1 °C, every scored hold | the same | **FAIL (6 of 9)**; the subset FAIL (5 of 6): `H1` fp32 random −1.37 °C, `H1` and `H2` zeros −1.62, −1.38 °C |
| G3 beats E136's law on a quantity when its rms is lower | per quantity | **G3 beats it on all three**: 8.7 vs 41.2 MHz, 1.94 vs 3.99 W, 0.99 vs 1.35 °C (the subset: 9.9 vs 50.3, 1.62 vs 4.62, 0.74 vs 1.64) |
| the chain on the measured trace, scored the same way | reported beside G3 | 0.41 °C rms, **9 of 9 inside 1 °C** |
| attribution: a clock or board miss with p800 more than 4 W from P0(800) is P0's level | per hold | `H1` fp32 random: **P0's level** (−7.21 W); the zeros' board misses: not P0's level by the rule (−1.54 to −2.09 W) |
| attribution: a die miss with the chain inside 1 °C is the power path | per hold | **every die miss is the power path** (chain +0.87, −0.50, −0.15 °C on the three) |
| R0: every check of C ok | a failure labels every verdict | **PASS**: 2,215 kernel records, every one ok (the smoke's four checks of C exact) |
| a hold cut by a stop or not run is not scored | listed | none cut, none refused: all nine holds complete (12 processes each) |

So the critic's rank-3 test, as registered, is **a FAIL of G3 on every quantity**, with the misses on one fp32 random shape (`H1`, P0's level) and on zeros'
board (2.4-2.5 W, every shape alike). It is also **a clear gain over E136's law**: the law's misses on the fp32 random holds are five times G3's in clock
and three times in board power.

## What E159 does to predicting power and heat

- **The term tested** is a governed large GEMM's sustained power and clock path: G3 (Q139(q)) takes the burst law P0 as the power at each clock, an
  effective leakage constant of 0.1 W/°C, the burst cap's dither and the governor's hold at 65.5 °C, closed through Q138(t)'s frozen heat chain. Its two
  constants were chosen post hoc on 56 earlier runs; E159 is their blind test.
- **Out-of-sample error before → after, blind** (nine holds; the registered subset of six in brackets): **clock 41.2 → 8.7 MHz rms** [50.3 → 9.9],
  **board 3.99 → 1.94 W** [4.62 → 1.62], **window die 1.35 → 0.99 °C** [1.64 → 0.74]. "Before" is E136's law (a fitted sustained cap, 60.83 W, and a two-
  parameter die law); "after" is G3. Q139(q)'s post hoc nested figures were 10.8 MHz, 1.86 W and 0.72 °C. Blind, the clock and board errors are at that
  level; the die error is a little larger.
- **The constants hold up blind.** G3 at Q138(t)'s constants (0.442 W/°C, 65.9 °C) reads E159 at 14.5 MHz, 3.08 W and 1.61 °C. The effective k = 0.1
  W/°C and the 65.5 °C trip beat them on every quantity, as they did post hoc.
- **Heat given the watts carries to a large GEMM, blind.** The chain on the measured trace: 0.41 °C rms, every hold inside 1 °C (post hoc on the 56
  earlier runs: 0.39-0.63 °C). Every die miss is the power path.
- **What remains is P0's per-shape level, and a few MHz in the clock mapping.**
  - **The level.** `H1`'s first second sat 7.2 W under P0 (`H1` streams 92 fresh lines an op; P0's line law priced it near `D8`'s and `F6`'s). The
    zeros sat 1.5-2.1 W under it on all three shapes. E158 found P0 high on zeros by 2.7-4.4 W on other shapes ([its README](../2026-11-03-e158-l3-retention/README.md) R7).
  - **Given the first second** (the diagnostic): board 1.45 W and die 0.86 °C, but clock 10.9 MHz, as Q139(q)'s C1 said it would be.
  - **The clock mapping.** Two things are missing:
    - a held fp32 random hold reads 10-14 MHz under G3 (`H2`, `H3`);
    - an unheld hold averages about 795 MHz, not 800. About 3% of its in-kernel samples sit at 600-700 MHz, and most runs of them start 0.2-0.3 s into a
      process, which fits the clock ramping back after the gap between processes (post hoc, `posthoc.txt` §3, §3b).

  The next model term is P0's level per shape (zeros included) and the governor's clock in and between processes.

## The stops, and their test on live samples

The session's stops were Q139(q)'s:
- `abs_stop_c` 76 °C on one sample;
- `board_cap_w` 85 W on three samples in a row (the brief's rule for aifoundry2: at most 85 W);
- the admission limit 82 W at each hold's frozen predicted peak. Every peak was at most 76.63 W, so every hold ran as designed, none duty-cycled or dropped;
- the peak lock 82 W.

Before the session the queue ran **both stops on live samples**:
- **stoptest-board** (`board_cap_w` 30 W; one 6 s burst of `H1` fp32 zeros over a 22 W rest) tripped **63 ms after the third live sampler line over 30 W,
  while the work launch ran, and the launch ended 281 ms after the trip**;
- **stoptest-die** (`abs_stop_c` 30 °C) tripped **56 ms after the first live line, before any launch**.

Both ended with exit 4 and passed the queue's registered check (`aifoundry2/queue.jsonl` `stoptest_detail`, `stoptest_check`; `posthoc.txt` §6).

## Device commands sent

*Q136's rule ("take more care for writing commands"), kept in Q137-Q139.* The classified list is [`E159.md`](../../../../tools/claims-v3/e159/E159.md)
"Device commands sent", frozen in `d8badb73`. It is classified from et-platform `836a4ab` (aifoundry2's BL2 0.22.0) and was checked by Q136(w)'s
`dmcmd_audit.py` before the claim ([`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e159/logs/dmcmd-audit.txt)): 19 send sites, every one READ, GO, the
same 19 as E158's. There is one reviewed exception: the residency read that run_e119.py rewrites to raw states 1-3, which this `ettelem` refuses before it
opens the device. **E159 sent no WRITE.**

What the session's records count (`posthoc.txt` §6):

| sent | how often | class |
|---|---|---|
| `ettelem sample` (`GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`) | 11,317 samples | READ; 11 PMIC voltage-register reads each, the owner's allowed read-only PMIC voltage reads of 2 November 2026 |
| `ettelem config` (three RAM getters, the ASIC voltage and PLL reads) | after each of the 15 recorded runs, at each session's start and end, and in the queue's two snapshots | READ |
| `ettelem sptrace` | after each of the 15 runs | READ (an MMIO copy, nothing sent to the SP) |
| the residency read | 15 times answered rc 2 | NOT SENT |
| statistics reset, firmware-revisions query, any set | none | — |
| `sparsity_host` (rgm136) | opens the ops node only: the kernel load, the DMA of the tiles and C, the launches | not device management |

## Safety

- **Board:** the session's highest reading was 76.1 W, in `H3` fp32 random (its predicted peak 76.63 W; E136's `g2k`, the same levels, peaked at 76.09 W).
  That is 8.9 W under the 85 W stop and 5.9 W under the 82 W design limit.
- **Die:** the mean's highest was 66 °C, 10 °C under the 76 °C stop.
- **The hottest-sensor field** read 70 °C at every sample, the SP's running maximum carried from before the session, as in E158 (70 °C) and E146 (69 °C).
- **No stop fired** in the session; no hold was refused admission and no peak lock was set.
- **The session's rest reading** (R, 30 s, idle): 21.74 W, die 45.17 °C.
- **The card afterwards:** free at 05:52:55 PST. et-who at 05:54:17 showed no device node or lock held, and no E159 process remained.
- **Other users:** none was logged in at any of the 169 checks (`aifoundry2/idle_logins.jsonl`: `other_users` 0 throughout).

## Departures and notes

- **What E159 added to Q139(q)'s design, as registered** (`E159.md`; none touches a hold): the smoke, the session's 30 s rest reading as its first run (the
  first hold's anchor), the admission estimates at the frozen peaks with limit and lock at 82 W, and the reduction's cut-hold filter and per-session scoring.
- **The holds' starts differ from the frozen nominal starts.** `H1` fp32 random was the session's first hold and started at 46 °C, after the rest reading. The
  zeros holds started at 52-57 °C. The registered primary is computed from each hold's own measured start, so the nominal tables (`predictions-e159.txt`)
  are context only. Measured against them (`posthoc.txt` §5), `H2` and `H3` fp32 random sit within 0.3 MHz of the gate57 nominal clocks (697.4, 649.4 MHz).
  That is not the scored prediction.
- **One session, nine holds.** The unit of replication is the hold; each ran once. The intervals are over holds (post hoc); none is between sessions.
- **The release's read-back.** The release rewrite saved at 05:55 PST, and the rendered post showed it at once. The day-plan's raw text still showed the
  claim in two reads (05:55:29, 05:55:56), so the release script reported "not confirmed". A read-only dry run of the edit box at 05:57:16, with
  EXPECT_TEXT set to the released text, matched: Discord holds the released text. A lane that builds EXPECT_TEXT from that plan field until it refreshes gets
  exit 7 (changed since read), never a wrong save.
- **Every time above is PST.** The registration says "about 05:30 PST": it was committed at 05:31:46.

## What E159 says about the page and the model

- **Section 11 item 1 and item 6, rank 3:** blind, a governed large GEMM's sustained clock, board and die follow from its burst levels, the frozen heat
  chain and the governor's trip to 8.7 MHz, 1.9 W and 1.0 °C rms, five times better than E136's law in clock on the shapes the governor holds. The rules
  fail on one shape's power level (`H1`, P0 7.2 W high) and on zeros' level (2.4-2.5 W high on every shape). The heat path is not the problem: given the
  watts the die is right to 0.41 °C on every hold. **The open part is P0's per-shape level.** It needs the L3's retention and set mapping (rank 7, E158), and
  zeros' level is about 2 W lower than P0 says. The open part also includes the governor's clock between processes.
- **For the "How well" table:** a governed large GEMM's sustained clock, blind: 41 MHz (E136's law) → 8.7 MHz (G3). Its board: 4.0 → 1.9 W. Its window die:
  1.35 → 0.99 °C. Heat given the watts: 0.41 °C.

**For the post, in short sentences.** Each names its card and clock.
- On aifoundry2, under its own governor, a large matrix multiply of random fp32 numbers is held at a die temperature of about 65.5 °C, and its clock falls
  to whatever power keeps it there. For two new shapes that was 698 and 650 MHz. A model built from each shape's short-burst power and the chip's heat path
  predicted 708 and 664 MHz before the run (`results.json` `rows`).
- Over nine new sustained runs, that model was within 8.7 MHz, 1.9 W and 1.0 °C rms. The older rule, a fixed sustained power cap, was off by 41 MHz and
  4.0 W (`results.json` `all_scored.summary`).
- Given the measured watts, the chip's heat path predicted every run's die temperature to within 1 °C (0.41 °C rms) (`chain_on_measured`).
- What the model gets wrong is the power level of some shapes. One 80 MB shape drew 7 W less in its first second than the burst law said, and multiplying
  zeros drew about 2.4 W less on every shape (`posthoc.txt` §4).
- int8 multiplies stayed at 800 MHz and were predicted within 1.1 W and 0.8 °C (`posthoc.txt` §2).

## Files

| file | what |
|---|---|
| [`results.json`](results.json), [`reduce.txt`](reduce.txt) | `tools/claims-v3/e159/reduce_e159.py`, the registered reduction: Q139(q)'s frozen scorer (`score_e159.py`'s hash check, then `e159_g3.score` unchanged) per session, cut holds left out (none); the verdicts over all nine holds and over the subset; the attribution; R0; the safety record |
| [`posthoc_e159.py`](posthoc_e159.py), [`posthoc.txt`](posthoc.txt), [`posthoc.json`](posthoc.json) | labelled, post hoc: intervals, by kind, the clock inside each window and where its dips fall, P0's first-second level, the nominal numbers beside the measured, the session (stop tests, rest reading, gates, commands counted, card time) |
| `aifoundry2/` | the queue's records: `queue.jsonl`, `status.json`, `admission.json`, `idle_logins.jsonl` (counts only), `snapshot-*.json`, `config-*.txt`, `sensors-*.json`, `history-before.jsonl` |
| `aifoundry2/smoke/`, `stoptest-board/`, `stoptest-die/`, `s1/` | each session: `runs.jsonl`, `marks.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz`, `sp/`, `session.json`, `e159.json`, `manifest.txt`, `queries.jsonl`, `run.log`, `end.json`; plus `smoke.out`, `stoptest-*.out`, `s1.out` |
| `logs/` | the queue's output (`queue.out`) and its start script |

The registration, the protocol and the code are in [`tools/claims-v3/e159/`](../../../../tools/claims-v3/e159/README.md). The design and the frozen
predictions are in [`../2026-11-03-q139q-gemm-g3/`](../2026-11-03-q139q-gemm-g3/README.md).

```bash
/usr/bin/python3 tools/claims-v3/e159/reduce_e159.py docs/reports/data/2026-11-03-e159-gemm-sustained/aifoundry2 \
    --out docs/reports/data/2026-11-03-e159-gemm-sustained/results.json > docs/reports/data/2026-11-03-e159-gemm-sustained/reduce.txt
cd docs/reports/data/2026-11-03-e159-gemm-sustained && /usr/bin/python3 posthoc_e159.py > posthoc.txt
```
