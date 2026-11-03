# E138: int8's B side on the minion rail - E130's B list again, the rail as the registered primary (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 12, "int8 at gate level", the part [E130](../2026-11-02-e130-int8-netlists/README.md) left open (does the int8 multiplier
recode B?). Mon 2 Nov 2026 (week 45), Q137. Pre-registered in `07f59099` (pushed 15:32:57 PST), before the claim and before any E138
run: [`tools/claims-v3/e138/README.md`](../../../../tools/claims-v3/e138/README.md). aifoundry3 card 0 at 600 MHz in every sample;
`ettelem config` read at the session's start (15:35:13, the smoke's), at both ends of the smoke and of every block, and once at the
queue's end (16:03:23): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV, all 21 reads alike, never set. **Every
device-management command sent was a read** (nine kinds, two of them PMIC voltage-register reads, which the owner's rule of 2
November 2026 allows); no write of any kind, no `--reset-ms` (`since_reset_ms` −1 in all 16,082 samples). Card session
15:35:13–16:03:23 PST, **28.2 of the 30 card-minutes allowed**; the smoke and nine of the ten registered B blocks ran (the budget rule
stopped before 13819, as projected).*

**In plain words.** Two gate-level versions of the chip's int8 multiplier recode the B operand in Booth digits and predict B's odd
bits at about 4.3× its even bits; two do not recode B and predict 1.05–1.10×. E130 found the card in between on its board meter, too
noisy to say which side of the registered line it fell. E138 read the same 14 single-bit tiles nine more times with the minion rail
as the registered meter. **On the rail B's odd bits cost 1.91× [1.71, 2.16] its even bits, and the odd − even contrast is +35.9
[+30.5, +41.4] board-equivalent fJ a flipped bit**: far from both groups (the no-recoder netlists' +0.5–1.2, the Booth netlists'
+54.8–66.2), so **neither structure's B list fits the card** (R1n and R1q both NEITHER, as frozen). Against the midpoint line
T_B = 30.68 the interval's low end falls 0.2 fJ short, so **the registered primary R1 reads INCONCLUSIVE** and R4 stays "between
Booth on B and no Booth", as I expected; pooled with E130's six rail blocks (reported only) it would read RECODED. **For predicting
power the answer is usable now**: B's bits need a price per position, or at least a parity weight of about 1.9, not one price.

## Results

**Nine B blocks kept** (13810–13818), **306 of 306 runs**, none failing a run gate (600 MHz, 318 cycles an op, every dumped tile
equal to its registered sha256), none set aside by the train gate ([`results.md`](results.md), [`scored.json`](scored.json)).

**1. The registered verdicts** (primary: the minion rail's `rail_raw` over each item's own zero, ÷ flips × rate, ÷ c_rb 0.81):

| rule | primary (rail) | board (E130's primary) | board p80 | rail, dips kept | rail, gates off | expected |
|---|---|---|---|---|---|---|
| E138-R1: B odd − even vs T_B 30.68 | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| E138-R1n: in either group's band? | **NEITHER (BETWEEN)** | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) |
| E138-R1q: odd / even, no scale | **NEITHER (BETWEEN)** | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) | NEITHER (BETWEEN) |
| E138-R4: which multiplier | **INCONCLUSIVE between BOOTH ON B / NO BOOTH** | the same | the same | the same | the same | the same |

No verdict is arm-sensitive. Every frozen expectation was met.

**2. The numbers** (95% over blocks; `scored.json` › `primary`, `arms`, `pool_with_e130`):

| reading | n | value | 95% | the groups' frozen bands |
|---|---:|---:|---|---|
| **rail: B odd − even, board-equivalent fJ** | 9 | **+35.9** | [+30.5, +41.4] | Booth on B [54.8, 66.2]; no recoder [0.5, 1.2] |
| rail: the same in rail fJ | 9 | +29.1 | [+24.7, +33.6] | |
| **rail: B odd / even** | 9 | **1.91** | [1.71, 2.16] | Booth on B [4.16, 4.39]; no recoder [1.05, 1.09] |
| board: B odd − even | 9 | +32.5 | [+17.0, +48.0] | |
| board: B odd / even | 9 | 1.88 | [1.40, 2.62] | |
| pool, E130's 6 + E138's 9 rail blocks, board-equivalent (reported) | 15 | +34.8 | [+31.6, +38.1] | reads RECODED against T_B |
| E130's rail arm, for comparison | 6 | +33.2 | [+29.6, +36.7] | |

**The scale.** R1's reading depends on c_rb, the rail-per-board constant (E78's frozen 0.81). At this session's interval R1 would
read RECODED at c_rb ≤ 0.804 and FLAT at c_rb ≥ 1.094 (`c_rb_flip_points`); B's own rail/board level ratio over bits 0–6 here is 0.90
(`scored.json` › `reported`), and E130's A bits read 0.811 [0.756, 0.872]. R1n and R1q do not move with the scale: R1q has none, and R1n
stays BETWEEN for any c_rb from 0.61 to 20 (the interval's ends against the two bands).

**3. Per bit** (rail fJ, primary; `results.md` has the board beside):

| B bit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (sign) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E138, rail fJ | 17.9 | 56.2 | 31.2 | 65.4 | 46.8 | 61.6 | 47.4 | 82.7 |
| E130, rail fJ | 23.4 | 57.5 | 35.1 | 62.8 | 42.9 | 61.7 | 47.7 | 81.8 |

The odd bits (1, 3, 5) sit at 56–65 fJ; the even bits rise with position (18, 31, 47, 47): the alternation is real and repeats
session to session, but its even side is not flat as a Booth recoder's would be, which is why the ratio lands at 1.9, not 4.3.

**4. What it does to predicting power and heat** (registered, reported; `scored.json` › `out_of_sample_e130`). E130's rail per-bit
prices of B bits 0–6 (mean 47.3 rail fJ) predicted from E138's:

| model of the B operand's flips | rms error, rail fJ | share of the mean |
|---|---:|---:|
| flat (one price for every B bit) | 13.6 | 29% |
| parity (an odd price and an even price) | 7.2 | 15% |
| per position (eight prices) | **3.2** | **7%** |

So a second session predicts the first to 7% per bit with per-position prices, against 29% with the flat price that the no-recoder
netlists imply. For a kind whose flips sit on a few low B bits (small integers, few-level quantised weights) that is the size of the
error a flat int8 per-flip term carries; for uniform random int8 every bit flips alike and the three models agree on the mean. Heat:
E138 measures no heat term; the die rose 50 → 55 °C over the session (trains, at most 31.67 W board), and the prediction of heat moves
only through this power term and M6's die-rise-per-watt.

## Registered against what happened

| | registered | happened |
|---|---|---|
| blocks | 13810–13819, the budget rule decides; about nine | nine (13810–13818), 177–178 s each; 13819 not started (projected past 1,740 s) |
| card time | ≤ 30 min | 28.2 min |
| precision | half-width about 2.6 board-equivalent fJ at E130's rail block sd (2.77 rail fJ) | **5.5**: this session's rail block sd was **5.77 rail fJ, 2.1× E130's**; the zeros' scatter about their neighbours was 0.023 W (E130's rail 0.035 W), so the spread is in the B items between blocks, not in the zeros |
| stops | die ≥ 70 °C, board ≥ 65 W | highest die 55 °C, board 31.67 W; no stop |
| A1's form check | config and telemetry as E130's | PASS (`logs/a1-form-check.txt`) |
| departures | — | **D1** (collection): the collector first ran on a scratch copy outside the repository, so its tables named Mac paths; it was run again, unchanged, on the raw copy inside this directory (`aifoundry3/`), which is what is committed. Same code, same numbers. **D2**: `run_e138.sh go` printed E130's stale label "B A B A …" for the sequence; the queue ran the registered B-only sequence (`logs/e138-queue.log`). Python for the collector: numpy through `uv` on the Intel, as for E130 |

## Device commands sent

As registered (the registration's § Device commands sent, E130's list): `ettelem config` (GET_MODULE_STATIC_TDP_LEVEL,
GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) 21 times; `ettelem sample`
(GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_MODULE_VOLTAGE) at 10 Hz;
**all READs**, the two voltage commands being PMIC voltage-register reads. Never sent: the statistics reset, any SET_*, the
firmware-revisions query, a residency read. The checker's outputs are in `logs/` (NO-GO without, GO with the reviewed `lib.sh:154`
exception, 31 sites). Residual, as E130's A1: aifoundry3's 7 Oct thermal build is not public.

## Card and post

`et-who` before the claim (15:34:36) and after the queue (16:03:23): no process held a device node or card lock. Other users' idle
logins were present throughout, with no device process of theirs. The day's one card post in #community-lab (message
1566837317765963987) read "… using aifoundry3 for 1 h, until ~13:35 PST [doc](…) — released" and was rewritten at 15:35:07 PST
(EXPECT_TEXT, dry run, then save) to "<ai> **Claude says:** using aifoundry3 for 1 h, until ~16:39 PST [doc](…)"; at 16:04:40 its
aifoundry3 clause was rewritten to "until ~17:10 PST" for E139, which followed on the same card.

## What it changes

- **Item 12**: the B side is answered for prediction (neither netlist group; a per-position B price), and stays open as a
  registered structural verdict (R1 INCONCLUSIVE, 0.2 fJ short of the line). The pool's RECODED is post-registration and is not a
  verdict. The A side stands as E130 left it (not recoded).
- **The power model**: int8's per-flip term should carry B's per-position prices (this card's eight, above) rather than one price;
  Q137(m)'s M6 is the place to test whether that lowers its int8 out-of-sample error on kinds.

## Files

`results.md`, `scored.json` (scorer output: every rule at every arm, the pool, the scale flip points, the out-of-sample table),
`e138.json`, `runs.csv`, `reduce.txt` (the primary reduction), the arms (`e138-dipskept.*`, `e138-gatesoff.*`), `code.sha256`,
`logs/` (queue, session reads, A1 check, dry runs, checker outputs), `aifoundry3/kinds/p1381*` and `aifoundry3/kinds-smoke/p13801`
(raw: per-run records, telemetry, tile dumps, manifests).
