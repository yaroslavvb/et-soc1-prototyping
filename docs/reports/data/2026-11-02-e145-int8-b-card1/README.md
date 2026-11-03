# E145: int8's B side on a second card (aifoundry1 card 1, 600 MHz) - the registered verdict stays INCONCLUSIVE because card 1's minion rail spikes to its running maximum; without those samples (post hoc) B's odd − even, +36.1 [+31.8, +40.5] fJ, would clear the line; the A control reproduces card 0; card 0's per-position B prices predict card 1's

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 12, "int8 at gate level"**, the part [E138](../2026-11-02-e138-int8-b-rail/README.md) left open: "whether the chip Booth-recodes B,
as a registered verdict" (E138-R1 INCONCLUSIVE, its interval's low end 0.2 fJ short of the line). Q138 (the owner's words, Mon 2 Nov 2026
~18:40 PST: "feel free to settle any unanswered questions regarding horace's power model", with Q137's goal, "to be able to predict the
power requirement and heat generation of various kinds of numeric computations as accurately as possible").*

*Mon 2 Nov 2026 (week 45), lane `a1c1-e145-int8-b`. Pre-registered in `18e5a7d2` (committed 19:21:21 PST and pushed by commit_lab before the
box setup at 19:21:59, before the claim at 19:23:20 and the first device access at 19:23:40):
[`tools/claims-v3/e145/README.md`](../../../../tools/claims-v3/e145/README.md), frozen numbers in
[`predictions-e145.json`](../../../../tools/claims-v3/e145/predictions-e145.json). No amendment. aifoundry1 card 1 at 600 MHz in every sample;
`ettelem config` read 38 times (the session's start, 19:23:40, and end, 20:10:39, and both ends of the stop-path test, the smoke and every
block): TDP 65 W, threshold 65 °C, 600 MHz, 499 mV, all alike, never set. **Every device-management command sent was a read** (nine kinds,
two of them PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows); no write of any kind, no `--reset-ms`
(`since_reset_ms` −1 in all 26,916 samples). Card session 19:23:40–20:10:39 PST, **47.0 of the 50 card-minutes allowed**; the stop-path
test, the smoke and **16 blocks (13 B, 3 A)** ran, every one `ok` (the budget rule stopped before 14523, as projected). Collected and scored
on the Intel at about 20:13 PST by the registered `collect_e145.sh`, unchanged.*

*Corrected after verification (a dated note, Mon 2 Nov 2026, about 21:00 PST): six faults, none of which changes a number, rule or verdict,
are corrected in [§ Corrections after verification](#corrections-after-verification-mon-2-nov-2026) at the end; the text between is as
first committed. The main ones: E145 tests whether card 0's per-position B prices carry over to a second card, a term no frozen model
carries, and it does not test M7's J8 (C1). 20% is the registered cross-card figure and 7% the post-hoc one (C2). Four spike samples fell
in three runs (C3). And card 1 gives no live hottest-shire reading, so the die is read as the shires' mean, at most 56 °C (C4).*

## Results

**In plain words.** Two of the four gate-level versions of the chip's int8 multiplier recode the B operand (Booth on B) and predict B's
odd bits at about 4.3× its even bits; two do not and predict about 1.07×. On aifoundry3 the card sat in between, at about 1.9×, and the
registered test of which side of the midpoint it falls on missed by 0.2 fJ. E145 ran the same 13 B tiles thirteen more times on a second
card, aifoundry1 card 1, with A's single bits beside them as the control. **The A control came out exactly as on card 0** (A's odd and
even bits alike, −2.1 [−9.4, +5.1] fJ; A's sign bit +66.8 [+63.0, +70.7] fJ dearer with a dense B: C1 REPRODUCES), and **B's odd − even
reads +36.0 board-equivalent fJ, card 0's +35.9 to a tenth**, but its interval is **[+9.8, +62.2]**, six times wider than planned, so
**the registered primary R1 reads INCONCLUSIVE** again, R1n IN BOOTH ON B's BAND (only because the interval is that wide) and R1q
NEITHER (BETWEEN), 1.81 [1.17, 3.30]. **The width is the meter, not the chip**: card 1's minion rail now and then reports its running
maximum, 34.50 W, for one or two samples (15 of the 16 blocks' 26,469 samples; 8 of 18,959 in E137's card-1 blocks this afternoon; none
of 31,491 on aifoundry3), and three such samples fell inside the rail windows of three B runs, each raising that run's rail reading by 0.5–2 W while
the board did not move. **Post hoc, labelled, never a verdict:** with those samples removed (E82 A2's dip rule mirrored), B's odd − even
is **+36.1 [+31.8, +40.5]** (2.00 [1.81, 2.23]), whose low end clears the 30.68 fJ line: it would read RECODED, and with the A control,
BOOTH ON B. **For predicting power the answer travels between cards**: card 0's frozen per-position B prices predict card 1's to 20%
rms as registered (9.9 rail fJ; one price: 39%), and to **7%** without the spikes (3.1 rail fJ; one price 35%); A's prices to 2%.

**1. The registered verdicts** (primary: the minion rail's `rail_raw` over each item's own zero, ÷ flips × rate, ÷ c_rb 0.81; 13 B and 3
A blocks kept, none set aside; [`results.md`](results.md), [`scored.json`](scored.json) › `primary.verdicts`):

| rule | what | primary (rail) | board | board p80 | rail, dips kept | rail, gates off | expected |
|---|---|---|---|---|---|---|---|
| **E145-R1** | B odd − even vs T_B 30.68 | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE ✓ |
| E145-R1n | in either group's band? | **IN BOOTH ON B's BAND** | NEITHER (BETWEEN) | NEITHER (BETWEEN) | IN BOOTH ON B's BAND | IN BOOTH ON B's BAND | NEITHER (BETWEEN) ✗ |
| E145-R1q | B odd / even, no scale | **NEITHER (BETWEEN)** | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) ✓ |
| E145-R2 | A odd − even vs T_A 27.58 | **FLAT** | FLAT | FLAT | FLAT | FLAT | FLAT ✓ |
| E145-R3 | A's sign step vs T_S 18.07 | **RISES** | RISES | RISES | RISES | RISES | RISES ✓ |
| **E145-C1** | the control | **REPRODUCES card 0** | the same | the same | the same | the same | REPRODUCES ✓ |
| **E145-R4** | which multiplier, card 1 alone | **INCONCLUSIVE between BOOTH ON B / NO BOOTH** | the same | the same | the same | the same | the same ✓ |
| E145-R5 | A's sign, word 2 / word 1 | **HOLDS** (1.03 [0.99, 1.08]) | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS ✓ |
| E145-R6 | B's sign, word 2 / word 1 | **FAILS (BELOW)** (0.65 [0.57, 0.73]) | FAILS (BELOW) | FAILS (BELOW) | FAILS (BELOW) | FAILS (BELOW) | FAILS (BELOW) ✓ |
| E145-N | each netlist on E130's three separators | **all four EXCLUDED** (`booth`, `booth_tree` by A's sign step; `booth_swap` by all three; `plain` by B's odd − even and A's sign step) | all four EXCLUDED | all four | all four | all four | all four EXCLUDED, by B's odd − even (✗ for the Booth pair) |

R1n is **arm-sensitive** (NEITHER on the board, whose interval is narrower than the rail's here) and so is E145-N's reason for the Booth
pair. The dips-kept arm set block 14510 aside by the train gate (a board dip in an `hb1` read, −0.369 W off its line) and keeps 12 B
blocks. R1, R1q, R2–R6 and C1 read the same at every arm.

**2. The numbers** (95% over blocks, exact t; `scored.json` › `primary`, `arms`, `reported`, `pools`):

| reading | n | value | 95% | card 0 (E138 / E130) |
|---|---:|---:|---|---|
| **rail: B odd − even, board-equivalent fJ** | 13 | **+36.0** | **[+9.8, +62.2]** | +35.9 [+30.5, +41.4] / +33.2 [+29.6, +36.7] |
| rail: B odd / even | 13 | 1.81 | [1.17, 3.30] | 1.91 [1.71, 2.16] / 1.79 [1.68, 1.92] |
| board: B odd − even | 13 | +31.5 | [+13.4, +49.6] | +32.5 [+17.0, +48.0] / +33.8 [+11.0, +56.7] |
| rail: A odd − even, board-equivalent | 3 | −2.1 | [−9.4, +5.1] | E130 board −1.7 [−6.6, +3.2] |
| rail: A's sign, B = 0x55 − B = 1, board-equivalent | 3 | +66.8 | [+63.0, +70.7] | E130 board +67.8 [+58.8, +76.8] |
| card 1's rail/board scale, A bits 0–6 (reported) | 3 | 0.791 | [0.692, 0.919] | E130 0.811 [0.756, 0.872]; frozen 0.81 |
| card 1's rail/board scale, B bits 0–6 (reported) | 13 | 0.924 | [0.744, 1.138] | E138 0.90 |
| R1 read at card 1's A-based scale (reported) | 13 | +36.9 | [+10.0, +63.7] | INCONCLUSIVE |
| pool, card 0's 15 + card 1's 13 rail B blocks (reported) | 28 | +35.4 | [+24.0, +46.7] | INCONCLUSIVE; card 0 alone +34.8 [+31.5, +38.1], RECODED (reported, as E138's C5) |

**3. Why the interval is wide: card 1's rail reports its running maximum** ([`posthoc/rail-spikes.json`](posthoc/rail-spikes.json), from
[`posthoc_e145.py`](../../../../tools/claims-v3/e145/posthoc_e145.py); post hoc). A spike is a sample whose rail reading is more than 4 W
above both samples two steps away (E82 A2's board-dip rule, mirrored):

| session | card | samples | spikes | of them at the running maximum (`sp.minion_w[2]`) |
|---|---|---:|---:|---:|
| **E145** | aifoundry1 card 1 | 26,469 (the 16 blocks) | **15** | **15** (34.50 W, against about 13.5 W around them) |
| E137 (15:38–16:11 PST today) | aifoundry1 card 1 | 18,959 | 8 | 8 |
| E138 | aifoundry3 card 0 | 15,741 | 0 | 0 |
| E130 | aifoundry3 card 0 | 15,750 | 0 | 0 |

Of E145's 15, four fell inside a run's rail window [t0+2 s, t0+4 s): two in `b1d_7`'s run of block 14515 (its price read 1,130 rail fJ
there against 54–80 in the other twelve blocks), one in a `b1_4` run of 14518 (308 against 26–55), one in a `b1_1` run of 14522 (309
against 40–67); the board in those runs read as usual. The other eleven fell outside every rail window. So two blocks' B odd − even read
−60.3 and +109.6 rail fJ, against 22.2–38.7 in the other eleven, and the per-block sd came out at **35.1 rail fJ, 6.1× E138's 5.77**;
without the spikes it is **5.85**, E138's.

**4. Post hoc without the spikes** (labelled; [`posthoc/results-posthoc.md`](posthoc/results-posthoc.md), [`posthoc/scored-posthoc.json`](posthoc/scored-posthoc.json);
E145's reducer with its dip filter also dropping the 15 spike samples, E78's reduction and E145's scorer unchanged; **no verdict**):

| reading | n | value | 95% | would read |
|---|---:|---:|---|---|
| **rail: B odd − even, board-equivalent fJ** | 13 | **+36.1** | **[+31.8, +40.5]** | R1 RECODED, R1n NEITHER (BETWEEN) |
| rail: B odd / even | 13 | 2.00 | [1.81, 2.23] | R1q NEITHER (BETWEEN) |
| which multiplier (R4 with R2 FLAT, R3 RISES) | | | | BOOTH ON B; every netlist EXCLUDED by B's odd − even and A's sign step |
| c_rb at which the reading changes | | | RECODED at c_rb ≤ 0.838, FLAT at ≥ 1.069 | the frozen 0.81 and card 1's A-based 0.791 both read RECODED |
| pool with card 0's 15 blocks | 28 | +35.4 | [+32.9, +37.9] | RECODED (reported) |

So on two cards and three sessions the contrast sits at +33 to +36 board-equivalent fJ (2.0× and 1.8–1.9× on the ratio), the precision
plan was right for a clean rail (±4.4 here against ±4.31 planned at 13 blocks), and the line would be cleared by a session whose spike
filter is registered before its data. That reading is not E145's verdict.

**5. Per bit** (rail fJ, primary; card 0 = E130's and E138's 15 B blocks, E130's 4 A blocks, frozen in `predictions-e145.json`):

| bit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (sign) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| card 1, B (registered) | 16.7 | 76.1 | 30.0 | 59.9 | 61.5 | 59.6 | 44.8 | 77.0 |
| card 1, B (spikes removed, post hoc) | 16.7 | 55.9 | 30.0 | 59.9 | 41.1 | 59.6 | 44.8 | 77.0 |
| card 0, B | 20.1 | 56.7 | 32.7 | 64.4 | 45.2 | 61.6 | 47.5 | 82.7 (E138) |
| card 1, A | 70.7 | 62.1 | 59.8 | 65.1 | 66.3 | 64.3 | 62.1 | 119.7 |
| card 0, A | 68.2 | 61.1 | 59.7 | 67.0 | 67.7 | 66.1 | 63.4 | |

The alternation on B repeats on the second card bit for bit (spikes removed: odd 1, 3, 5 at 56–60; even 0, 2, 4, 6 rising 17, 30, 41,
45), and A is flat at every position on both cards.

**6. What it does to predicting power and heat** (registered, reported; `scored.json` › `cross_card`). Card 0's frozen prices of bits 0–6
predicting card 1's, rms in rail fJ and as a share of card 1's mean:

| model of the operand's flips | B, registered | B, spikes removed (post hoc) | A, registered |
|---|---:|---:|---:|
| flat (one price for every bit: what the power model carries now) | 19.3 (39%) | 15.4 (35%) | 3.3 (5%) |
| parity (an odd and an even price) | 13.9 (28%) | 8.9 (20%) | 3.3 (5%) |
| **per position** (card 0's price of each bit) | **9.9 (20%)** | **3.1 (7%)** | **1.6 (2%)** |
| card 1's mean over card 0's | 1.06 | 0.94 | 0.99 |

**The term tested: the int8 per-flip price by operand bit position, on a card it was not measured on.** Out of sample, one price per B
bit misses card 1's per-bit prices by 35–39% and card 0's per-position prices by 20% as registered and 7% without the rail's spikes (the
7% equals E138's same-card test); on A one price is already good to 5%, per position to 2%. Q138(m)'s M7 adds E138-priced B flips to its
int8 form (J8, `3a210f2b`): this is the first test of such prices on another card, and they hold, to the card-to-card scale (0.94–1.06). For a kind
whose flips sit on a few low B bits (small integers, few-level quantised weights) that is the size of the error a flat term carries; for
uniform random int8 every bit flips alike and the models agree on the mean. **Heat**: E145 measures no heat term; the die read 51–56 °C as
the shires' mean (the hottest shire 65 °C) at 35.8–39.5 W on the board ([`telemetry.json`](telemetry.json)), and the prediction of heat
moves only through this power term and M6's die rise per board watt.

## Registered against what happened

| | registered | happened |
|---|---|---|
| blocks | the sequence 14510 14530 14511 … 14523, the budget rule decides; about 12 B and 3 A | **13 B (14510–14522) and 3 A (14530–14532)**, B blocks 176–177 s, A 133 s; 14523 not started (projected past T0 + 2,910 s) |
| card time | ≤ 50 min | 47.0 min (2,819 s from the session-start read to the end read) |
| precision | ±4.53 at 12 kept B blocks (±4.31 at 13) at E138's block sd | **±26.2**: the per-block sd was 35.1 rail fJ, 6.1× E138's, from three rail spikes (§ 3); ±4.4 without them |
| the meter | the rail live on card 1, checked again in the smoke | the smoke gate PASSED (206 distinct values, 8.81–14.87 W, no constant run over 3); the spikes, one or two samples at a time, are not what the gate tested |
| stops | board ≥ 60 W, hottest shire ≥ 72 °C, on live samples; the path tested first | board at most 39.45 W, hottest shire 65 °C (the shires' mean 51–56 °C); no stop; **the stop-path test fired both stops on their first reading** (the die stop on a sample read 0.025 s after it was taken, the board stop on one read 0.108 s after, both from `telemetry.jsonl.raw`, no launch) |
| smoke gate | 318 cycles an op, 600 MHz, dumps equal their sha256, config 65/65/600, the rail live | PASS on every part (`logs/session.log`) |
| frozen expectation | R1 INCONCLUSIVE, R1n and R1q NEITHER, R2 FLAT, R3 RISES, C1 REPRODUCES, R4 INCONCLUSIVE B/none, R5 HOLDS, R6 FAILS (BELOW), every netlist EXCLUDED by B's odd − even; per position < parity < flat | all as expected except **R1n (IN BOOTH ON B's BAND)** and the reason the two Booth-on-B netlists are excluded (A's sign step, not B's odd − even): both from the wide interval. Out of sample per position < parity < flat as expected; per position 20% (expected about 10%), flat 39% (expected about 29%) |
| departures | — | none in the run. **D1** (analysis): § 3–4 and `posthoc/` were written after the data were scored; they change no verdict. **D2** (wording): the registration's "card 1 idles near 31 W" — the stop test read 29.49–30.22 W at idle |

## Device commands sent

As registered ([`tools/claims-v3/e145/README.md`](../../../../tools/claims-v3/e145/README.md) § Device commands sent, classified from
et-platform `836a4ab`, BL2 0.22.0, the build card 1 reports): `ettelem config` through E128's `ettelem_guard.sh` (GET_MODULE_STATIC_TDP_LEVEL
25, GET_MODULE_TEMPERATURE_THRESHOLDS 21, GET_MODULE_POWER_STATE 23, GET_ASIC_FREQUENCIES 53, GET_ASIC_VOLTAGE 32) 38 times; `ettelem sample
--seconds --every-ms 100` through the guard (GET_MODULE_POWER 33, GET_SP_STATS 60, GET_MODULE_CURRENT_TEMPERATURE 27, GET_MODULE_VOLTAGE 31,
GET_ASIC_VOLTAGE 32, GET_ASIC_FREQUENCIES 53) at 10 Hz in the stop-path test, the smoke and every block, 26,916 samples; **all READs**, the two
voltage commands being PMIC voltage-register reads (two and nine a call). Never sent: the statistics reset (`since_reset_ms` −1 in every
sample), any SET_*, the firmware-revisions query, a residency read, `dev_mngt_service` (the drain is refused). On the box the session's
preflight (`preflight_e145.sh`, Q136(w)'s checker) read **GO, 32 send sites, 0 disallowed** at 19:23:40 before any device opened
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); the registration's run on every E145 file: NO-GO without the reviewed `lib.sh:154`
exception, GO with it.

## Card and post

`et-who` at 19:04:38, 19:21:59 and 19:23:39 (before the launch) and 20:10:39 and 20:10:44 (after the session): no process held a device node
or card lock. Other users' idle logins were present on the host throughout, with no device process of theirs (D1 of the harness: an idle
login does not block). The day's one card post in #community-lab (message 1566837317765963987) read "… using aifoundry3 for 1 h, until
~17:40 PST [doc](…) — released" and was rewritten at 19:23:20 PST (EXPECT_TEXT, dry run, then save) to "<ai> **Claude says:** using
aifoundry1 card 1 for 1.5 h, until ~20:53 PST [doc](<…>)", the only card held; at 20:11:26 PST, the session over, " — released" was
appended (it was still the only clause), every word kept ([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).

## What it changes

- **Item 12**: the structural verdict is still not registered. On a second card the A side repeats card 0's (no recoder on A) and B's
  odd − even repeats card 0's mean (+36.0 against +35.9 and +33.2), but card 1's rail spikes left the registered interval too wide to
  decide; post hoc it clears the line (+36.1 [+31.8, +40.5]), so the next registered test needs only the spike filter written first (or
  aifoundry3's spike-free rail) and about 13 B blocks. Neither group's B list fits either card (R1q NEITHER on both).
- **The power model**: int8's per-flip term should carry B's per-position prices (M7's J8 form adds E138's); card 0's predict a second
  card's to 7% (20% with the spikes) against 35–39% for one price, and A's one price holds to 5%. The card-to-card scale of these prices
  is 0.94–1.06.
- **The meter**: card 1's minion rail occasionally reports its running maximum (34.50 W) for one or two samples (15 in the blocks' 26,469
  samples here, 8 in E137's 18,959); aifoundry3's does not (0 in 31,491). Every rail reading on card 1 needs that filter (E137's post-hoc rail figures on
  card 1 were read without it).

## Files

`results.md`, `scored.json` (the scorer's output: every rule at every arm, the pools, the scales, the cross-card table), `e145.json`,
`runs.csv`, `reduce.txt`, `reduce.log` (the primary reduction), the arms (`e145-dipskept.*`, `e145-gatesoff.*`, `runs-dipskept.csv`,
`runs-gatesoff.csv`), `score.log`, `telemetry.json` (each block's extremes, `telemetry_max_e145.py`), `code.sha256`; `posthoc/` (labelled,
after the data: `rail-spikes.json`, `e145-posthoc.json`, `runs-posthoc.csv`, `reduce-posthoc.txt`, `results-posthoc.md`, `scored-posthoc.json`,
from `posthoc_e145.py`); `logs/` (the session log with the stop-path test, the smoke gate and every block's lines, the queue, the session's
config reads, the box's preflight, the dry runs, the binaries' sha256, `push-and-claim-times.txt`); `aifoundry1-c1/kinds/p145*`,
`kinds-smoke/p14501`, `kinds-stoptest/p14502` (raw: per-run records, telemetry, tile dumps, manifests, the stop test's STOP lines).

## Corrections after verification (Mon 2 Nov 2026)

*A dated note, written at about 21:00 PST on the Intel. An independent verifier re-derived the results from the committed files:
`reduce_e145.py` and `score_e145.py` reproduce `scored.json` to 1e-9, and `posthoc_e145.py` reproduces `posthoc/` exactly. It also confirmed
that every command sent was a read. The text above is left as first committed; where it disagrees with these notes, the notes hold. No
frozen file, number, rule, prediction or verdict changed.*

- **C1 (§ 6 and What it changes): E145 does not test M7's J8.** § 6 says M7 "adds E138-priced B flips to its int8 form (J8, `3a210f2b`):
  this is the first test of such prices on another card, and they hold". What it changes says "(M7's J8 form adds E138's)" of B's
  per-position prices. Neither is so. M7's int8 form `J8_b138` adds one feature, b_even + 1.91 b_odd: a two-level shape built on E138's
  odd/even ratio, priced at −23.4 ± 9.8 fJ in the fit to board power. M7's README says the negative sign "corrects the bench's own B
  count ... it is not E138's price" ([Q138(m)](../2026-11-02-q138m-model/README.md) § 2). What E145 tests is whether card 0's int8 price
  list by B bit position carries over to a second card. No frozen model (M5, M6 or M7) carries that term:
  - The before is the one-price row, the shape of M5's and M6's int8 forms, which have no term for B's bit position.
  - The row nearest J8's two-level shape is parity. J8 itself is not scored here.
  - E138's 1.91 ratio does lie inside card 1's 1.81 [1.17, 3.30] (2.00 [1.81, 2.23] post hoc).

  | card 0's B prices predicting card 1's bits 0–6 (rms rail fJ, share of card 1's mean) | registered | post hoc, card 1's 15 spike samples removed |
  |---|---:|---:|
  | one price (the before: M5's and M6's shape) | 19.3 (39%) | 15.4 (35%) |
  | parity: an odd and an even price (nearest J8's shape) | 13.9 (28%) | 8.9 (20%) |
  | per position (the after: no frozen model carries it) | 9.9 (20%) | 3.1 (7%) |

  (`scored.json` › `cross_card.B`, `posthoc/scored-posthoc.json` › `cross_card.B`.)
- **C2 (§ 6 and What it changes): the registered figures come first.** § 6's "one price per B bit misses card 1's per-bit prices by 35–39%"
  mixes the registered 39% with the post-hoc 35%, and What it changes leads with the post-hoc 7%. As registered, the per-position prices
  miss by 20% against 39% for one price. Post hoc, an analysis chosen after the data, the figures are 7% against 35%. § 5's per-bit list in
  words ("odd 1, 3, 5 at 56–60; even 0, 2, 4, 6 rising 17, 30, 41, 45") is the spikes-removed row, as it says. As registered, bit 1 reads
  76.1 rail fJ and bit 4 reads 61.5.
- **C3 (Results and Registered against what happened): four spike samples in three runs, about 1.0 W each.** The Results paragraph says
  "three such samples fell inside the rail windows of three B runs, each raising that run's rail reading by 0.5–2 W", and the precision
  row says "three rail spikes". § 3 has it right: four samples fell in three B runs' rail windows, two in `b1d_7`'s run of 14515 and one
  each in `b1_4`'s run of 14518 and `b1_1`'s run of 14522. They raised those runs' `rail_raw` by 2.09 W (the pair), 1.05 W and 1.03 W
  (`runs.csv` against `posthoc/runs-posthoc.csv`): about 1.0 W a sample.
- **C4 (the status, § 6 and Registered against what happened): there is no live hottest-shire reading on this card.** "Hottest shire
  65 °C" is not a reading of E145's die:
  - In `temp_c.minshire` only the mean moved (51–56 °C). The low and high entries read 46 and 65 °C in all 26,916 samples.
  - At `836a4ab` the firmware fills them from the temperature sensors' latched sample low and high (`smpl_hilo`). It reads them in
    `pvt_controller.c`'s `pvt_get_ts_data`, takes them over the shires in `pvt_get_minion_avg_low_high_temperature`, and never clears
    them. On aifoundry3 the high entry reads 87 °C in every sample of E138.
  - So the die read at most 56 °C as the shires' mean, and the hottest shire is not known. The latch bounds it at 65 °C only if the
    hardware updates the latch on every conversion, which the source does not show.
  - The registered die stop (any minion-shire reading ≥ 72 °C) took the largest entry, which was the latched 65 °C throughout. It was at
    least a stop on the mean, and a stop on the hottest shire only if the latch updates. The stop-path test's die stop fired on that
    constant 65 °C at its test threshold of 1 °C: it proved the path on live sample lines, not a live shire reading.
  - The margins hold: the mean at most 56 °C against 72 °C, the board 39.45 W against the 60 W stop. `telemetry.json` ›
    `hottest_shire_c_max` is the same latch.
- **C5 (Device commands sent): one sender was left out.** `lib.sh`'s `die_c` (`lib.sh:102–103`) runs `ettelem sample --seconds 1
  --every-ms 500` through the guard (`block_e145.sh` sets `ETTELEM` to `ettelem_guard.sh`). `block_begin` and `block_end` call it
  (`lib.sh:188`, `:196`), twice a block, 36 calls in all (the 18 `block.json` files' `die_c_start` and `die_c_end`). It sends the
  sampler's six READ commands: GET_MODULE_POWER 33, GET_SP_STATS 60, GET_MODULE_CURRENT_TEMPERATURE 27, GET_MODULE_VOLTAGE 31,
  GET_ASIC_VOLTAGE 32 and GET_ASIC_FREQUENCIES 53. The box's preflight lists `lib.sh:103` with all six as READ
  ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)). Their samples are parsed for the die reading and not written to
  `telemetry.jsonl`, so the 26,916 samples are the 10 Hz sampler's alone. No class changes.
- **C6 (§ 6 and What it changes): the scale is three figures, not a range.** "The card-to-card scale (0.94–1.06)" mixes B as registered
  (1.06), B post hoc (0.94) and A (0.99) (`cross_card` › `card1_over_card0_mean`). Registered against what happened is right that the
  frozen cross-card sizes were missed: per position about 10% was expected and 20% came out; one price about 29% was expected and 39% came
  out. Only the order per position < parity < flat held.

**What the corrections do to predicting power and heat.** Nothing is refitted, and every out-of-sample error above stands. What changes is
the term E145 bears on: the int8 price list by B bit position. It carries over to a second card (one price 39% → per position 20% as
registered; 35% → 7% post hoc), and no frozen model carries it yet. E145 is not a test of M7's J8. Heat: no heat term was measured, and
the die is read here only as the shires' mean.
