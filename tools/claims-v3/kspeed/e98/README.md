# V3-KSPEED E98: does the heat path's drift follow the room? One night of probes on aifoundry2 (Q132)

*Pre-registered Sun 1 Nov 2026 (week 44), about 00:35 PDT, before the `#community-lab` claim and before the first launch. This commit freezes
the design, the numbers ([`predictions.json`](predictions.json)), the scorer ([`reduce_e98.py`](reduce_e98.py), self-test
[`selftest.txt`](selftest.txt)) and the decision rules. Any change after it goes in Amendments at the end, dated, before the data it touches. Every
time in this experiment is epoch ms: the box's clock goes back at 02:00 PDT tonight.*

**The ask** (the owner, Sat 31 Oct 2026, about 23:30 PDT): *"Continue closing issues which are still open in
https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers … and run proper experiments on aifoundry."* This is item 9 of that page's section 11:
the heat path drifts between sessions, about 3 W at the trip between 23 and 31 October, with no room or inlet reading.

**The hypothesis, post hoc and untested.** A desk reading of four sessions (lane Q132(g),
[`docs/reports/data/2026-11-01-q132-governor-desk/`](../../../../docs/reports/data/2026-11-01-q132-governor-desk/)) says the drift tracks the room at
rest: the 76 s line `die - 0.4573 W` moved **+0.25 ± 0.07 °C per °C of rest die** across E64, E80, E83 and E87 (n = 4, E80 the common baseline). The
four sessions fell where they fell in the room's daily cycle; nobody chose it. E98 chooses: the same kinds, in the same order, under the same gate, at
seven points of one night while the room cools. **Nothing is set on the card.** Its governor stays at 65 W / 65 °C as read.

**The expected effect is small, and the rules may come back inconclusive.** The night's fall is about 1.9 °C of rest die, so about −0.47 °C of line on
the desk's slope, on a 1 °C die reading. Below, the power estimate says how often each verdict comes up. An inconclusive result is a result, and it
will be reported as one.

## Design

**Card and instrument.** aifoundry2, card 0, release 1.4.0 / BL2 0.22.0 as read on 27 October, TDP 65 W, threshold 65 °C. Each probe is one session
of [`run_e98.py`](run_e98.py), which is E80's and E87's runner, `run_kspeed.py` over E64's `run_hpl.py`, imported unchanged: the card lock for the
session, the other-user checks before every launch process, `timeout 10`, the sampler without `--reset-ms`, the trace ring, residencies and `ettelem
config` after every run, the stops at 85 °C and at 97 W on three samples, and the end of the session unless TDP and threshold read 65. The binaries are
the box's `build/sparsity_t2` and `build/ettelem-hpl`, E80's and E87's. The tiles are Q130(s)'s, checked against `kinds.json`.

**One probe** ([`protocol.json`](protocol.json), about 23.5 card-minutes, capped at 28), the same in all seven. The order is fixed by design, low power to
high, so that every run has the same history in every probe:

| block | what | window read |
|---|---|---|
| rest | at least 15 min with no launch, the lock free, nothing of ours on the card | the 20 min of the box's own 5 s history before the probe |
| `REST` | no launch: the 10 Hz sampler on the idle card for 120 s (a run with zero processes, which `run_hpl.py` handles as it stands) | the last 60 s |
| `SUS` 0 | fp32 zeros, **from the rest** (not in the line, rule S3) | last 40 s of nine 8 s processes, about 76 s |
| `SUS` 1–8 | fp16 zeros, int8 zeros, int8 neg_ones, int8 sparse50, fp16 ones, int8 full, fp32 randn, fp16 ones: **the gated line**, each from a die reading ≤ 57 °C (E80's, E83's and E87's gate and shape) | last 40 s |
| `HOLD` | int8 neg_ones, 39 back-to-back 8 s processes, about 5.5 min, from ≤ 57 °C | last 120 s |
| beside | `sensors -j`, `uptime` and `ettelem config` (non-blocking lock, `timeout 10`) at both ends; `et-lab-manifest` per session | |

*Why these kinds.* fp16 zeros, int8 zeros, fp32 randn, int8 full and fp16 ones are the kinds the desk's slope came from, so the test is like with like. The
zeros and neg_ones sit far below the trip at 35–41 W, sparse50 at the top of the unclamped range (49 W), fp16 ones and int8 full at the trip, and fp32
randn on the 600 MHz floor. fp16 ones runs twice because the speed a reader cares about is there.

*Why the hold is int8 neg_ones.* The desk lane's spec offered fp32 zeros or this. A room shift moves every state by the same degrees whatever its watts, and a
change of the path's resistance moves each state in proportion to its watts, so the hotter hold separates them better: 41 W against 22 W at rest. It
reads 60 °C at 76 s (E80), so it stays under the trip.

**The queue** ([`queue_e98.py`](queue_e98.py)) runs detached on the box and needs no ssh. It holds no lock between probes. It takes a probe's start from
epoch ms, requires the 15 min of rest on the box's own history (no row with a die over 55 °C or a board over 26 W, no two rows running with the card held), a
free lock and nobody else logged in, and otherwise waits, bounded by that probe's latest start. It stops itself at **07:15 PST**: the session's stop-file
at −120 s, its SIGTERM at −30 s, never a device process signalled. Nothing was set, so nothing is restored.

**The night's schedule.** P1 as soon as it may be, at least 15 min after the smoke, expected 01:05 PDT. Rest readings, with `T` that moment:

| | rest reading starts | clock |
|---|---|---|
| P1 | `T`, expected 08:05 UTC | 01:05 PDT |
| **slot E100** | `T` + 30 to `T` + 70 min, expected 08:35–09:15 UTC | 01:35 PDT–01:15 PST |
| P2 | `T` + 90 min, latest start 09:41 UTC | 01:35 PST |
| **slot E96** | 10:05–11:20 UTC | 02:05–03:20 PST |
| P3, P4, P5, P6, P7 | 11:40, 12:25, 13:10, 13:55, 14:40 UTC | 03:40, 04:25, 05:10, 05:55, 06:40 PST |

**The card's only other users under this one claim are E100 and E96**: E100, the idle-reset test (int8 zeros, about 20 card-minutes), and E96, real tensors'
speed (about 60 card-minutes). They get the two slots above, each ending 20 min before E98's next rest reading, with the gap around E96 at least 90 min. The
queue launches nothing inside a slot. Exact epoch seconds go in `~/claude/work/q132-a2-slots.txt` on the box, written by
[`make_schedule_e98.py`](make_schedule_e98.py) when the queue starts, and in the data README. Whatever they do on the card shows in the box's
history, and the rest rule reads it. One post in `#community-lab` covers all three.

**Etiquette.** The claim follows this commit. A dry run, then a smoke (one 20 s idle read and three 2 s launches, block `SMOKE`), then the queue. **No governor move, no TDP, threshold or clock set, no reset of any kind.**

**What is not read.** The fans: not readable without loading a kernel module (`it87`), not done mid-run; they were left at full duty on 6 October. Inlet air: no sensor. The room itself: no sensor, which is the point of the proxies. **Command 74**, the 34 raw sensors E89 read at 0.06 °C on aifoundry3's firmware build: no record of it ever being sent to this card, and E98 does not try, so the die stays a whole-degree reading here. Hence the fine readings on watts below. `acpitz`, `sar`, the CPU package under load, outside air and the camera's thermistors are left out for the reasons in the desk lane's spec.

## The readings

- **The rest die.** Primary: aifoundry2's idle board W over the 20 min of its own 5 s history before the probe's first snapshot, a row within 10 min after a busy one left out, and the die derived as **W / 0.2315** (the desk's fit over 2,182 5-minute bins, r 0.978). Slopes need only its differences. A whole-degree die cannot resolve a 2 °C night, and watts can.
- **Departure from the brief, named.** The brief's rest reading is the last 60 s. It is taken and every rule is reported on it too (`arms`), but it is not primary, because of what the box's history showed before this freeze ([`desk/rest_window.txt`](desk/rest_window.txt), [`desk/cycle.txt`](desk/cycle.txt)): 1-minute means scatter 0.075 W about a 2 h mean, against 0.040 W for 15–30 min means; a 15-minute mean predicts the idle card's next 20 min at 0.054 W rms, against 0.073 W for 1 minute; and **all four idle cards on three boxes share a cycle of about 19.5 min**, amplitude 0.011–0.025 W over nine days. A window near that period averages it out. Without 60 history rows the 60 s reading stands in, and the probe says so.
- **The line.** For each gated run, `die - 0.4573 W` over its last 40 s, E64's window, with k frozen at the desk's pooled within-session slope. Each kind's runs are averaged first, then the probe's mean over the kinds, with each kind's mean over the probes taken out so a missing run cannot move a probe. `reduce_hpl.run_metrics`, unchanged, computes the same two numbers, and the scorer refuses a disagreement.
- **The hold.** Die, ioshire, board W and clock over its last 120 s.
- **Fine readings, because the die is whole degrees.** At a fixed 800 MHz a kind's board W moves only with temperature, so **W is a thermometer with 0.01 W steps**. A run's fine W is the mean of its 800 MHz samples, leaving out each idle-reset dip and the 3 s after it, and it exists only with at least 70% of the window left. The fine line is the mean fine W of fp16 zeros, int8 zeros and int8 neg_ones.
- **Idle-reset dips** (the 800 to 600 MHz drop with no 700 sample, E80's A1) are flagged, named and **kept in** the registered numbers. Dip-free arms sit beside them.
- **Each probe also records** gate holds, `die_start`, the time since the previous launch, the trace ring and `ettelem config`.

## Frozen predictions

**Why 1 for the hold, and why more than 1.** A room shift moves the whole heat path's reference, so at any fixed work the die moves 1:1, times the leakage feedback `1 / (1 - R dP/dT)`, with R = 0.4573 °C/W. That gain is 1.12 at rest (0.2315 W/°C) and 1.25 on the hold (E64's 0.442 W/°C). So:

| quantity | if the room is the cause | if the path's resistance moved instead | if it follows no better than the line |
|---|---|---|---|
| hold die per °C of rest die | **1.12**, band **1.00–1.25** | 2.08 (each state moves with its own watts, 41 W against 22.1 W) | 0.25 |
| hold fine W per W of rest W | **2.14**, band **1.91–2.39** | 3.97 | 0.60 |

**From-rest run (SUS 0).** A run from a full rest carries no gate's anchor, so a linear system predicts the same 1:1 in its die: **0.89** in the line's units (1.12 × (1 − 0.4573 × 0.442)), **2.14** W per W on its fine W. **Gated runs** start from a fixed die reading, which is the desk's suggested reason their slope is 0.25 and not 1: **0.25** in the line and **0.60** W per W on the fine line (0.25 / 0.798 × 0.442 / 0.2315). This position effect is a prediction of the room reading in its own right.

**At the trip** (from E64 to E80, the desk's figures): fp16 ones **−12 MHz** and **−1 W** per °C of rest die, on a run-to-run spread of 21–23 MHz.

**The rest die's own fall.** Nine-day hour means give the night's shape; tonight sat at 22.12 W, 46.6 °C, NIC 44.3 °C and NVMe 37.5 °C at about 00:05 PDT, below those means. From P1 to P7: **−0.44 W = −1.9 °C**. The seven whole nights on record fell 0.47 ± 0.35 W, from −0.04 to 0.88 W, so two of seven barely fell.

| probe | rest reading | rest W | rest die, change from 00:05 PDT (°C) | NIC at rest | line, change on 0.25 | hold die, change on 1.12 |
|---|---|---|---|---|---|---|
| P1 | 08:05 UTC | 22.105 | −0.06 | 44.16 | −0.02 | −0.07 |
| P2 | 09:35 | 22.018 | −0.44 | 43.89 | −0.11 | −0.50 |
| P3 | 11:40 | 21.801 | −1.38 | 43.19 | −0.35 | −1.55 |
| P4 | 12:25 | 21.748 | −1.61 | 42.98 | −0.40 | −1.80 |
| P5 | 13:10 | 21.726 | −1.70 | 42.85 | −0.43 | −1.91 |
| P6 | 13:55 | 21.703 | −1.80 | 42.74 | −0.45 | −2.02 |
| P7 | 14:40 | 21.668 | −1.95 | 42.60 | −0.49 | −2.19 |

The hold's absolute values are a sanity range only: die 60–64.5 °C, board 40–43.5 W.

## Decision rules (frozen; `reduce_e98.py` implements them)

**The probe is the unit of replication.** Every slope is OLS over the probes that count, with a 95% t interval on n − 2 degrees of freedom. **A probe counts** when no history row in the 15 min before it shows a busy card (else it is reported and left out), for the line with at least 6 of the 8 gated runs, for the hold when all 39 of its processes ran and none failed.

- **E98-R0, the rest die's own fall.** First minus last counted probe against the 0.1–0.9 W band. It is also **the gate: fewer than 4 counted probes, or a rest-die range under 0.75 °C, makes every slope rule UNDER-RESOLVED.** A night that does not cool tests nothing.
- **E98-R1, the 76 s line against the rest die**, against 0 and 0.25:
  `SUPPORTS` (the interval excludes 0 and holds 0.25); `INCONCLUSIVE` (holds both); `BELOW_TARGET` (holds 0, excludes 0.25); `POSITIVE_BELOW_TARGET` (above 0, below 0.25); `ABOVE_TARGET` (above 0.25); `OPPOSITE` (below 0).
- **E98-R2, the hold's die against the rest die**, the sharp discriminator, against the band 1.00–1.25 and 0.25:
  `SUPPORTS` (reaches the band, lies wholly above 0.25); `INCONCLUSIVE` (reaches the band and 0.25); `BELOW_BAND` (wholly under 1.00); `ABOVE_BAND` (wholly over 1.25).
- **E98-V, the room's reading:**
  `SUPPORTED` if R1 and R2 both read `SUPPORTS`; `PARTLY` if R2 reads `SUPPORTS` and R1 reads `INCONCLUSIVE`, `POSITIVE_BELOW_TARGET` or `ABOVE_TARGET` (the hold follows the room; the line's rate is not established or differs from the desk's); `REFUTED` if R2 reads `BELOW_BAND` or `ABOVE_BAND`, or R1 reads `BELOW_TARGET` or `OPPOSITE`; `INCONCLUSIVE` otherwise; `UNDER-RESOLVED` if R0's gate fails.

**What would refute the room reading**, in order of force:

1. The hold does not follow: R2 wholly under 1.00. Whatever moved the rest die did not move a held, near-steady die with it, so it was not the room.
2. The hold moves more than the rest: R2 wholly over 1.25, with 2.08 as the path's prediction. That is a change of the path, or some cause other than the room.
3. The line does not follow at the desk's rate: R1 holds 0 and excludes 0.25. The room may move the rest die, but the desk's slope does not carry within a night, so E64's +1.12 °C needs another cause.
4. Reported, not a verdict: the other boxes' idle readings do not fall with aifoundry2's. Then the fall is this box's own.

**Secondary rules, on watts** (each the same partition, and UNDER-RESOLVED under R0's gate):

- **E98-S1, the fine line** against rest W, against 0 and 0.60 W/W.
- **E98-S2, the hold's fine W** against rest W, against the band 1.91–2.39 W/W and 0.60, with 3.97 as the path's value. `hold_calibration` also reads W against the die inside each hold, as a check on E64's 0.442 W/°C, which these constants lean on.
- **E98-S3, the from-rest run**: its fine W against 0 and 2.14 W/W, and its line against 0 and 0.89.
- **E98-S4, the trip**: fp16 ones' mean clock and board W against the rest die, against 0 and −12 MHz/°C, −1 W/°C. Expected inconclusive: 16 MHz per probe from run scatter alone.

**Beside the rules, labelled, never a verdict:** every rule on the 60 s reading; on the raw history die; dips left out; unclamped kinds only; each position alone; hold on ioshire. **Proxies:** aifoundry2's NIC and NVMe at rest, and on the other boxes a1c0 die, a1c1 die, a1c1 W, a3 W, and their NIC and NVMe, each with the line and the hold against it and it against the rest die. An other-box row counts only with its card not held, a die, W under the idle bar (a1c0 22, a1c1 34, a3 27 W) and load under 2, with either card held blanking aifoundry1. Other lanes run a3 and a1c1 tonight, so holes are expected, and a proxy needs rows in at least 4 counted probes. `~/live/history/<UTC date>.jsonl` from all three boxes is collected at the end.

## What the noise allows

Planning noise per probe: line 0.15 °C (one run's 0.42 °C rms about E87's line, over 8 runs); hold die 0.40 °C (0.29 for the whole-degree reading, 0.28 for the 19.5 min cycle in a 2 min window); fine line 0.05 W; hold W 0.13 W. From [`predictions.json`](predictions.json) `power`, 20,000 seeded draws per row, seven probes on the night's shape:

| night's fall | R1 half-width | R1 if the slope is 0.25 | R1 if it is 0 | R2 half-width | R2 if the slope is 1.12 | R2 if it is 0.25 |
|---|---|---|---|---|---|---|
| 2 °C | ±0.20 | SUPPORTS 68%, INCONCLUSIVE 27% | BELOW_TARGET 68%, INCONCLUSIVE 27% | ±0.53 | SUPPORTS 89%, INCONCLUSIVE 9% | BELOW_BAND 81%, INCONCLUSIVE 18% |
| 1.5 °C | ±0.27 | SUPPORTS 45%, INCONCLUSIVE 50% | BELOW_TARGET 45%, INCONCLUSIVE 50% | ±0.71 | SUPPORTS 69%, INCONCLUSIVE 29% | BELOW_BAND 58%, INCONCLUSIVE 41% |
| 1 °C | ±0.41 | SUPPORTS 23%, INCONCLUSIVE 73% | BELOW_TARGET 23%, INCONCLUSIVE 72% | ±1.07 | SUPPORTS 37%, INCONCLUSIVE 60% | BELOW_BAND 30%, INCONCLUSIVE 67% |

So a true 0.25 is called `SUPPORTS` only about two nights in three, even at the full fall. **The planning noise is an estimate. If it is wrong, so is this table, and the verdicts stand as scored.**

**What one night cannot do.** It cannot separate the room from anything else that falls on the same schedule, such as the building's own cycle. It tests the rest die's relation to the line and the hold, inside one night, on one card. It does not test the 23 October session itself.

## What a result fills

It closes, narrows or leaves open item 9 of the kinds page's section 11, and it gives the blog one sentence on whether a speed measured at 20:00 and one measured at noon differ because the room did. The data goes to [`docs/reports/data/2026-11-01-e98-heat-path-drift/`](../../../../docs/reports/data/2026-11-01-e98-heat-path-drift/).

## Files

| file | what |
|---|---|
| `protocol.json`, `protocol-dry.json`, `make_protocol_e98.py` | one probe's blocks; the dry run's short shape |
| `run_e98.py` | one probe's session: `run_kspeed.py`, imported unchanged |
| `queue_e98.py`, `make_schedule_e98.py` | the night's detached queue; its schedule and the slots file |
| `make_predictions_e98.py`, `predictions.json`, `predictions.txt` | the frozen numbers and the power estimate |
| `reduce_e98.py`, `selftest_e98.py`, `selftest.txt` | the scorer, and its test on hand-made intervals and planted nights |
| `desk/rest_window.py`, `desk/cycle.py` and their `.txt` | why the rest reading is a 20 min mean (post hoc, on the boxes' own history, before this freeze) |

## Amendments

- **A1 (Sun 1 Nov 2026, about 01:02 PDT; written while P1 ran, before any of P1's numbers had been read, and committed before P2).** It drops two probes for a third other user of the card. **No rule, target, band, gate, noise figure, protocol, `predictions.json` or `reduce_e98.py` changes.**

  *What changes.*

  1. **P4 and P5 are dropped.** P1, P2, P3, P6 and P7 stay at their registered times, so the first and last probes are as far apart as before.
  2. **A third slot, E101:** epoch **1793535600** to **1793540100**, 12:20–13:35 UTC, **04:20–05:35 PST**. It opens 16 min after P3's expected end and closes 20 min before P6's rest reading. **E101, a real matmul kind by kind under this card's own governor, is the third other user of the card under this one claim**, beside E100 and E96. No second post. ([`amendment-1.json`](amendment-1.json), `~/claude/work/q132-a2-slots.txt` on the box.)
  3. **P3's latest start moves from 12:10 to 11:56 UTC** (03:56 PST), so it ends before that slot.
  4. **How the running queue learns this.** It reads its schedule once, so it is stopped between probes: `QUEUE-STOP` touched while P1 ran, which ends that queue after P1 (its `queue.jsonl` will show a `skip` of P2 and a `queue_end`), and a new queue starts on [`make_schedule_a1_e98.py`](make_schedule_a1_e98.py)'s schedule, P2, P3, P6, P7, with the three slots. P1 is untouched. The queue's code is the same.

  *Why.* The coordinator's reason: the final critic of the previous round ranks "a real matmul, kind by kind" first among what the post still lacks, and only this card's governor can give its speed.

  *What it costs.* Five probes, not seven: 3 degrees of freedom, not 5. One lost probe leaves 4, the gate's minimum (2 df); two lost makes every slope rule UNDER-RESOLVED. A true 0.25 is now called `SUPPORTS` about one night in two, even at the full fall. On the frozen planning noise and the night's shape ([`amendment-1.txt`](amendment-1.txt), 20,000 seeded draws a row; seven probes in brackets):

  | night's fall | R1 half-width | R1 if the slope is 0.25 | R1 if it is 0 | R2 half-width | R2 if the slope is 1.12 | R2 if it is 0.25 |
  |---|---|---|---|---|---|---|
  | 2 °C | ±0.27 (±0.20) | SUPPORTS 48%, INCONCLUSIVE 47% | BELOW_TARGET 49%, INCONCLUSIVE 47% | ±0.72 (±0.54) | SUPPORTS 71%, INCONCLUSIVE 28% | BELOW_BAND 61%, INCONCLUSIVE 38% |
  | 1.5 °C | ±0.36 (±0.27) | SUPPORTS 30%, INCONCLUSIVE 65% | BELOW_TARGET 31%, INCONCLUSIVE 64% | ±0.96 (±0.72) | SUPPORTS 48%, INCONCLUSIVE 49% | BELOW_BAND 41%, INCONCLUSIVE 58% |
  | 1 °C | ±0.54 (±0.41) | SUPPORTS 16%, INCONCLUSIVE 80% | BELOW_TARGET 16%, INCONCLUSIVE 80% | ±1.44 (±1.09) | SUPPORTS 25%, INCONCLUSIVE 72% | BELOW_BAND 22%, INCONCLUSIVE 76% |

  *A fix to the text above, found while writing this.* "What the noise allows" gives R2's half-widths as ±0.53, ±0.71 and ±1.07, from an earlier draft of the schedule; `predictions.json`, which is what was frozen, says ±0.54, ±0.72 and ±1.09. The table is left as committed.

- **A2 (Sun 1 Nov 2026, about 01:25 PDT; written after P1, the only probe so far, whose numbers had been read; one probe shows no slope, and no later probe exists).** It adds two labelled arms and says what P1 shows about the gate. **No rule, target, band, gate, noise figure, protocol, `predictions.json` or verdict changes.** R1 is scored as frozen.

  *What P1 shows.* In the fixed order, low power first, the gate never acted on the first four gated runs: indexes 1–4 started at a die of 50–54 °C with 0 s held. Only indexes 5–8 and the hold were held (1.4, 17.0, 19.6, 26.1 and 18.4 s). E80, E83 and E87 ran their sustained runs after a block of bursts, on a warm card, so this README's "the gated line" overstates what the order does. Those four kinds also read well below the same kinds in those sessions: fp16 zeros 53.2 °C at 34.0 W, against 58.0 °C at 35.8 W in E87. Heat carries over, and every probe has the same history, so the comparison across probes stands. Their line values are not comparable with the earlier sessions'.

  *What that does to the expectation, stated before the data.* The desk's untested reason for 0.25 is the gate's anchor. A run the gate does not touch has no anchor, so on that same reasoning it should behave like the from-rest run, 0.89 in the line's units. If indexes 1–4 read 0.89 and the three kinds of indexes 5–8 read 0.25, the pooled R1 over 7 kinds reads **0.62**. So **under the room reading the registered R1 should now come out above 0.25**, `ABOVE_TARGET`, or `SUPPORTS` where its interval still holds 0.25. With R2 `SUPPORTS`, E98-V calls `ABOVE_TARGET` `PARTLY`, as registered. Hold R1's result against this paragraph. A reading near 0.25 on all eight would count against this reasoning, not for the desk's.

  *What is added.* Two arms in [`reduce_e98.py`](reduce_e98.py), neither a verdict: `R1_unanchored_idx1to4_A2`, set against 0.89, and `R1_anchored_idx5to8_A2`, set against 0.25. `gate.held_s` is reported per run, so a run that crosses from held to not held between probes is visible.
