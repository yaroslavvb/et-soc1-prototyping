# E98 data: does the heat path's drift follow the room? One night on aifoundry2 (Q132, Sun 1 Nov 2026)

aifoundry2 card 0, under its own governor, at five points of one night: a rest of at least 15 min, the same nine sustained runs in the same order, then a 5.5 min hold of int8 neg_ones. **Nothing was set on the card**: TDP and threshold read 65 W and 65 °C at all 59 reads, every run's and both ends of every probe ([`checks.txt`](checks.txt) K10). The sampler ran without `--reset-ms`. It addresses item 9 of the kinds page's section 11: the heat path drifts between sessions, about 3 W at the trip between 23 and 31 October, with no room or inlet reading.

The pre-registration is [`tools/claims-v3/kspeed/e98/`](../../../../tools/claims-v3/kspeed/e98/README.md) (`c8e84226`, pushed 00:38:20 PDT, before the claim and the first launch), with amendments A1 (`52087494`, 01:02 PDT, while P1 ran, before any of its numbers were read) and A2 (`9b1c09f5`, 01:24 PDT, after P1 alone). The card was claimed in `#community-lab` at 00:39:10 PDT and released by editing the same post at 07:21 PST. Clocks went back at 02:00 PDT, so every time here is also UTC; the raw records are epoch ms.

| session | UTC | box clock | card min | what |
|---|---|---|---|---|
| `smoke/` | 07:39:24–07:40:06 | 00:39 PDT | 0.7 | 20 s idle, three 2 s launches; not analysed |
| `P1/` | 08:00:00–08:21:28 | 01:00 PDT | 21.5 | complete |
| `P2/` | 09:30:00–09:37:55 | 01:30 PST | 7.9 | **stopped by the other-user rule**, exit 3 (§ What was registered) |
| `P3/` | 11:40:00–12:00:59 | 03:40 PST | 21.0 | complete |
| `P6/` | 13:55:00–14:16:06 | 05:55 PST | 21.1 | complete |
| `P7/` | 14:40:00–15:00:57 | 06:40 PST | 20.9 | complete |

## Results first

### 1. The plain answer: the night supports the room reading in direction and rough rate, and does not establish the room as the cause

**The frozen verdict is E98-V `PARTLY`**: the hold follows the rest die (`SUPPORTS`), and the line follows it faster than the desk's 0.25 (`ABOVE_TARGET`).

- **For it.** When aifoundry2 idled warmer, its line read higher, its hold hotter and fp16 ones slower. All are in the predicted direction, at rates like those between the sessions of 23–31 October. aifoundry1's two cards, its NIC and its NVMe fell with aifoundry2's rest die, each at about its nine-day relation (§5).
- **Against leaning on it.** Every registered slope is one contrast, P1 against P3, P6 and P7 (P1's leverage is 0.94). The hold moved **2.2 °C per °C of rest die**, and its interval holds both the room's 1.12 and a changed path's 2.08, so **the sharp discriminator did not discriminate**. On the brief's 60 s rest reading, or on the raw history die, R1 and R2 both read `INCONCLUSIVE`. And other experiments were heating the same room unevenly (§4).

| rule | verdict | what the data say ([`results.json`](results.json), [`reduce.txt`](reduce.txt)) |
|---|---|---|
| **E98-R0** the rest die's own fall, and the gate | **INSIDE_BAND; gate OK** | **0.233 W = 1.01 °C**, first to last (expected 0.437 W = 1.89 °C; band 0.1–0.9 W). Range 1.01 °C against the gate's 0.75. Five probes counted, four for the line and the hold. `R0` |
| **E98-R1** the 76 s line on the rest die, against 0 and 0.25 | **ABOVE_TARGET** | **0.502 [0.305, 0.700]**, n 4, 2 df. `R1.fit`. Above the frozen 0.25; the interval overlaps the desk's corrected free-intercept fit, 0.336 ± 0.073, 95% about 0.02–0.65 ([desk README](../2026-11-01-q132-governor-desk/README.md), C2). Don't lean on its width: §2 |
| **E98-R2** the hold's die on the rest die, against 1.00–1.25 and 0.25 | **SUPPORTS** | **2.19 [0.47, 3.90]**, n 4, 2 df. `R2.fit`. It reaches the band and lies wholly above 0.25, but the estimate sits by the path's 2.08 and the interval holds both |
| **E98-V** the room's reading | **PARTLY** | R2 `SUPPORTS`, R1 `ABOVE_TARGET`, as registered. `V` |
| E98-S1 the fine line on rest W, against 0 and 0.60 | INCONCLUSIVE | 0.38 W/W [−2.24, 3.00]. `S1.fit` |
| E98-S2 the hold's fine W on rest W, against 1.91–2.39 and 0.60 | SUPPORTS | **4.30 W/W [1.69, 6.91]**. `S2.fit`. Estimate above the band and by the path's 3.97; holds both. Two instruments agree: the fine W says the same as the die (§3) |
| E98-S3 the from-rest run: fine W against 0 and 2.14; line against 0 and 0.89 | INCONCLUSIVE, twice | W 1.77 [−1.47, 5.02]; line 1.16 [−0.87, 3.19]; five probes, P2 included. `S3` |
| E98-S4 fp16 ones at the trip: clock against 0 and −12 MHz/°C; W against 0 and −1 W/°C | SUPPORTS; INCONCLUSIVE | **−17.5 MHz/°C [−29.2, −5.7]**; −1.60 W/°C [−3.26, +0.05]. `S4` |

**Beside the rules, labelled** (`arms`):

| reading | R1 | R2 | as they would read |
|---|---|---|---|
| the registered rest: 20 min of watts | 0.502 [0.305, 0.700] | 2.19 [0.47, 3.90] | ABOVE_TARGET, SUPPORTS |
| the brief's 60 s rest reading | 0.241 [−0.709, 1.191] | 1.25 [−2.53, 5.02] | INCONCLUSIVE, INCONCLUSIVE |
| the raw history die | 0.441 [−0.052, 0.934] | 1.81 [−1.40, 5.02] | INCONCLUSIVE, INCONCLUSIVE |
| R1 with dips left out | 0.503 [0.274, 0.732] | | ABOVE_TARGET |

### 2. The night, probe by probe, and what the slopes rest on

| probe | rest W, 20 min | raw rest die | 60 s W | a2 NIC | a1 NIC | the line | hold die | hold fine W | fp16 ones MHz, W | int8 full MHz |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P1 | 22.110 | 46.87 | 22.038 | 44.36 | 53.87 | 39.803 | 60.42 | 41.40 | 771.4, 52.37 | 773.4 |
| P2 | 22.066 | 46.67 | 22.203 | 44.43 | 53.43 | – | – | – | – | – |
| P3 | 21.897 | 46.09 | 21.764 | 43.92 | 52.75 | 39.331 | 58.05 | 40.41 | 789.9, 54.18 | 793.6 |
| P6 | 21.949 | 46.20 | 21.802 | 43.57 | 52.89 | 39.397 | 58.80 | 40.57 | 783.8, 53.62 | 783.9 |
| P7 | 21.877 | 45.68 | 21.990 | 43.57 | 52.77 | 39.310 | 58.49 | 40.47 | 787.1, 53.72 | 800.0 |

(`probes[].rest_w`, `rest20`, `rest60`, `R1.per_probe`, `hold`; `S4.per_probe`; K12.) Expected rest W at the freeze, in order: 22.105, 22.018, 21.801, 21.703, 21.668 (K8). **The room fell between P2 and P3 and then stayed flat**, so the night gave one step, not a slope. E96's reading between them (22.145 W, 46.79 °C at 10:05 UTC, [its README §5](../2026-11-01-e96-real-tensors-speed/README.md)) puts the step after 10:05 UTC.

**Every slope is that one step.** P1's leverage in R1 and R2 is 0.94; P3, P6 and P7 span only 0.31 °C of rest die (K1). The contrast, P1 minus the mean of the three: rest die +0.877 °C (W-derived), +0.878 °C (raw history); line +0.457 °C; hold die +1.973 °C; hold ioshire +1.859 °C; hold fine W +0.919 W; fp16 ones −15.5 MHz, −1.47 W (K1).

**R1's narrow interval is not to be trusted.** With 2 df it rests on a residual scatter of 0.036 °C a probe. On the eight positions' own scatter, 0.063 °C, the same slope reads [0.159, 0.845], which holds 0.25 and excludes 0. On the registered planning noise, 0.15 °C, it reads [−0.313, 1.317], which holds both (K2). **So the fair reading of R1 is "positive, about 0.5, not shown to differ from the desk's 0.25–0.35"**, whatever `ABOVE_TARGET` says. The hold's scatter among the later probes is 0.375 °C, as planned (0.40).

### 3. The hold is not a steady reading, and it grows apart during the hold

Both instruments agree on the contrast: 1.97 °C on the die, and 0.92 W of fine W is +2.08 °C at E64's 0.442 W/°C (inside the holds W per °C reads 0.39–0.62, median 0.456; K1). But the desk's "close to steady" was wrong. After 15 minutes of hotter runs, the die **falls** through the hold on P3, P6 and P7 (first minute to fifth: 59.37 to 58.00, 59.93 to 58.79, 59.74 to 58.67 °C) and stays flat on P1 (60.58 to 60.65 °C) (K9). So:

- In the hold's **first minute** P1 reads +0.90 °C above the later probes, about **1:1** with the rest die's +0.877.
- By its **fifth minute** P1 reads +2.16 °C.

The extra degree arrives during the hold, on one probe. Three readings fit it, and the night cannot choose:

1. the room warmed during P1, unread (§4);
2. the path's resistance was higher, the 2.08 reading;
3. chance: one contrast, 0.4 °C of scatter a probe.

The hold's registered sanity range (die 60–64.5 °C, W 40–43.5) was also wrong for the same reason. Three holds read 58.05–58.80 °C, and two read just under 40 W. That range decides nothing.

### 4. What else ran in the room

The design took the night's cooling as the only thing moving. It was not. Share of each box's rows with a card held (K11):

| probe | aifoundry1, work | aifoundry3, work | both at the hold's end | hold die |
|---|---:|---:|---|---:|
| P1 | 0.95 | 0.67 | yes (1.00, 0.90) | 60.42 |
| P3 | 0.00 | 1.00 | aifoundry3 only | 58.05 |
| P6 | 0.60 | 1.00 | aifoundry3 only | 58.80 |
| P7 | 0.00 | 0.20 | neither | 58.49 |

P1 is the one probe with both other boxes running at its hold's end. Nothing read the room during P1's hold: aifoundry1's rows are blank while either card is held. So a warmer room during P1 from the other experiments is a live reading of P1's extra degree, and it would be a room effect but not the night's cooling. P3's hold, the coolest, fell at the night's lowest point: aifoundry1's idle die and NIC fell through that probe (47.0 to 46.0 °C, 52.75 to 52.20 °C; K5), and K4's 30-minute table has its minimum at 12:00 UTC.

### 5. The rest die's fall is shared, at the nine-day relation

| reading, over each probe's rest window | C per C of a2's rest die: nine days (desk) | the night, n 5 |
|---|---:|---|
| a1 card 0 die | 0.89 | 0.81 [0.32, 1.29] |
| a1 card 1 die | 1.10 | 1.05 [0.01, 2.09] |
| a1 card 1 W (W per C) | 0.48 | 0.41 [0.14, 0.68] |
| a1 card 0 W (W per C) | 0.22 | 0.20 [0.07, 0.33] |
| a1 NIC | 0.92 | 1.07 [0.60, 1.53] |
| a1 NVMe | 0.91 | 0.79 [0.01, 1.58] |
| a2 NVMe | 0.85 | 0.88 [0.43, 1.32] |
| a2 NIC | 0.90 | 0.80 [−0.05, 1.65] |

(`proxies`, K13.) Every interval on the other box excludes 0 and holds the nine-day value. **So what fell at rest was not this card alone: it is the shared signal the desk named.** That answers refutation 4 of the registration: the other boxes did fall. aifoundry3 had rows in only two counted probes, its card busy, so it is not scored. The line and the hold against a1's NIC, labelled: 0.431 [0.335, 0.528] and 1.89 [0.70, 3.08]. Both carry the same step.

### 6. The gate's reason for 0.25 is wrong, and A2 with it

A2, written after P1, reasoned that the runs the gate never held (indexes 1–4) should read 0.89 and the held ones (indexes 5–8) 0.25, so about 0.62 pooled. **The pooled number came out near that, 0.50, and the split came out the reverse:**

| arm | A2 expected | on the 20 min rest | on the 60 s rest |
|---|---:|---|---|
| held, indexes 5–8 | 0.25 | **1.02 [0.79, 1.25]** | 0.39 [−1.74, 2.52] |
| unheld, indexes 1–4 | 0.89 | **0.11 [−0.41, 0.63]** | 0.13 [−0.13, 0.40] |

(`arms`, K3.) So the desk's untested reason for "0.25 and not 1", a gate's anchor, does not stand. The held runs are the ones that follow about 1:1. At the trip the die is pinned and the line moves through W, which leaves no whole-degree noise (rms 0.03 °C). My reading, post hoc: the card there has settled against its limit, while the early runs of a series from a cold card are still warming. By position, K8 shows no steady growth: +0.46, +0.39, −0.15, −0.13 °C on indexes 1–4 and +0.79, +1.14, +0.57, +1.06 °C on indexes 5–8.

**An early run follows the state just before it, not the 20-minute mean** (post hoc, K3). With P2's runs included, five probes:

- the fine W of indexes 1–3 follows the **60 s** rest W at 0.678 W/W [0.505, 0.851], rms 0.015 W;
- on the 20 min rest W the same reads 0.70 [−1.08, 2.47], rms 0.089 W;
- the from-rest run's line on the 60 s rest reads **0.887 [0.433, 1.342]**, against the registered 0.89 for a linear system, though that registered rule was on the 20 min reading and came back inconclusive.

So the 20 min reading was the better one for the end of a probe and the worse one for its start, and a registered "rest" needs both.

### 7. Across sessions: the night sits on the line the earlier sessions draw

Post hoc, K6 and K12, against each session's raw rest die. Sessions differ in history, E64 has much of the leverage, and E96 reads a little low, as its own README says (+0.03 per °C on its four kinds, one point, about 1 σ).

| quantity | fit | points |
|---|---|---|
| fp16 ones' clock | **−13.8 MHz/°C [−18.8, −8.7]** | E64, E80, P1, P3, P6, P7 |
| fp16 ones' board W | **−1.24 W/°C [−1.78, −0.69]** | the same |
| mean line of int8 full and fp32 randn | 0.41 °C/°C [0.23, 0.59]; without E64 0.58 [0.20, 0.96]; the five earlier sessions alone 0.38 [0.11, 0.65] | E64, E80, E83, E87, E96, P1, P3, P6, P7 |
| int8 full's clock | −9.3 MHz/°C [−13.7, −5.0]; without E64 **−13.7 [−22.8, −4.7]** | the same nine |

**Item 9's 3 W is in this.** E64 to E80, fp16 ones gained 3.93 W over 3.70 °C of rest die, −1.06 W/°C; the night's step reads −1.68 W/°C, and the fit −1.24. **The rest die's difference is big enough to account for the drift between those sessions without any change of the path. That does not show there was none.**

**Which side of the trip int8 full lands on follows the rest die.** E87 §4 found single runs on either side "whatever the data". In the night's four probes its clock orders with the raw rest die, 800.0, 793.6, 783.9, 773.4 MHz at 45.68, 46.09, 46.20, 46.87 °C, with E80's 793.4 at 45.58 °C, E83's 786.5 at 46.42 °C and E87's 774.7 at 47.15 °C beside them. E96's four runs in one session, 777–795 MHz, show how much scatter stays.

## What was registered, and what happened

**P2, under the frozen rules.** At 01:37:54 PST, 17 s into P2's sixth run (int8 sparse50), the runner's other-user check found another lab user logged in on the box and ended the session between two launch processes (exit 3). No other process had touched the card. The queue had found nobody at 01:30. Under the queue's registered rule exit 3 goes on to the next probe, and P3 ran on time. **P2's rest reading and its four finished runs (indexes 0–3) are kept, and it counts where the frozen rules let it:**

- R0's range and first-to-last fall, as a counted rest;
- E98-S3, which needs only the from-rest run.

**It does not count for R1, S1, R2, S2 or S4:** it has 3 of the 8 gated runs against the rule's 6, no hold, and no trip kind. So R1 and R2 ran on four probes, the gate's minimum, as A1 said one lost probe would leave. P2 was not re-run, because no slot allowed it. Its loss cost one early point at about P1's rest die, which is exactly where a second point was wanted.

| registered | happened |
|---|---|
| seven probes, then five by A1 (P4, P5 dropped for E101's slot) | five started, four complete |
| P1 "as soon as it may be, expected 01:05 PDT", P2 90 min later | T = 01:00 PDT (20 min after the smoke), P2 01:30 PST |
| the rest: at least 15 min, no busy row | met by every probe: 19.9, 36.2, 24.7, over 40, 23.9 min (`rest20.since_busy_min`) |
| the only other users under this claim: E100, E96 (slots frozen), E101 (A1) | as such. They ran in their slots, and their busy rows are in the history |
| same binaries in every probe | yes (`binaries_same_in_every_probe`) |
| the queue launches nothing inside a slot; no ssh needed; stops itself by 07:15 PST | as such; it ended at 07:00:57 PST with `done` |
| restart between probes (A1) | the first queue ended on `QUEUE-STOP` after P1 with a recorded skip of P2 and a `queue_end`; the second ran P2–P7 |
| planning noise a probe: line 0.15 °C, hold 0.40 °C, fine line 0.05 W, hold W 0.13 W | measured 0.036–0.063 °C, 0.375 °C, 0.079 W rms, 0.078 W rms |
| dips flagged, kept in | windows: 1 of 40 sustained runs, all four holds (5 in all; K7). R1 unchanged without them |
| the release after collection | **departure**: released at 07:21 PST before collection, on the coordinator's word, since E105 was waiting for the card. Collection followed at once, read-only |

**Departures from the brief, named before the data in the registration:** the primary rest reading is 20 min of watts, not the last 60 s; the from-rest run is not in the line. §1 shows what the first one was worth: on the brief's own reading every slope rule reads `INCONCLUSIVE`.

**What one night could not do, as the registration said.** It cannot separate the room from anything else on the same schedule. Fans and inlet air were not read. Command 74, the fine sensor reading, was never sent to this card: no record of it there, and not in this brief.

## What it fills, and what it changes

**Item 9 is narrowed, not closed.** What's left: an inlet thermometer, the one reading all of this lacks; and the same test on a night with nothing else running in the room and more than one warm probe.

**For the blog, each sentence with its source:**

- The card's rest temperature moved about 1 °C during the night, and the other box's two cards moved with it ([`checks.txt`](checks.txt) K13).
- At the thermal limit, the same matmul on the same card ran at 771 MHz at 01:00 and 784–790 MHz later that night, when it idled about 0.9 °C cooler ([`results.json`](results.json) `S4.per_probe`).
- Across 23 October to 1 November that speed falls about 14 MHz for each °C the card idles warmer, and that rate is enough to account for the 3 W between the sessions of 23 and 31 October (K6). It rests on few points, and it does not show that nothing else changed.
- Whether random int8 trips the thermal limit at all tends to follow how warm the card idles; one session's own runs still scatter 777–795 MHz (K12).
- A held 41 W load read 2 °C hotter on the warm probe; **we cannot say whether that was the room alone**, because the night gave one warm probe, with other experiments running beside it (`R2`, K9, K11).

**Not to be said from this directory:** "the room causes the drift" as a finding; "the hold follows the room 1:1"; "0.25 per °C" as a measurement; "the gate is why the slope is under 1"; any number here as more than one contrast of four probes on one night.

## Card state

aifoundry2 card 0 free at 07:21:12 PST (`et-who`: no process holds a device node or card lock), the queue ended at 07:00:57 PST. The last config read (P7's `snapshot-end.json`) reads TDP 65 W, threshold 65 °C. **Nothing was set, so nothing was restored.** The run directories remain on the box in `~/claude/et-soc1-prototyping/build/e98/`.

## Files

**A login was removed.** The other-user mark names who was logged in. It was replaced by `<another lab user>` in `queue.out`, `queue.jsonl`, `P2/end.json`, `P2/run.log`, `P2/marks.jsonl` and `P2/run.out`, before the reduction ran; every file here, compressed ones too, was searched for it and read back after.

| file | what |
|---|---|
| `P1/`, `P2/`, `P3/`, `P6/`, `P7/`, `smoke/` | the raw sessions (telemetry and launches gzipped): `session.json`, `e98.json`, `kspeed.json`, `runs.jsonl`, `queries.jsonl`, `marks.jsonl`, `tel/`, `sp/`, `logs/`, `manifest.txt`, `run.out`, and the queue's `snapshot-*.json`, `sensors-*.json`, `config-*.txt` |
| `queue.jsonl`, `queue.out`, `queue-first.out`, `status.json` | the queue's own record, both queues, epoch ms and zone |
| `schedule.json`, `schedule-a1.json`, `slots.txt`, `slots-a1.txt` | the night's schedule, before and after A1 |
| `history/<box>-2026-11-01.jsonl.gz` | the three boxes' own 5 s history, 07:00–15:30 UTC, numbers only |
| `results.json`, `reduce.txt` | the registered reduction |
| `checks.py`, `checks.txt` | post-hoc checks K1–K13, labelled, deciding nothing |

The three slots: E100 1793521800–1793524200 (01:30 PDT–01:10 PST), E96 1793527500–1793532000 (02:05–03:20 PST), E101 1793535600–1793540100 (04:20–05:35 PST).

Reproduce from the top of the repository:

```bash
python3 tools/claims-v3/kspeed/e98/reduce_e98.py docs/reports/data/2026-11-01-e98-heat-path-drift --out /tmp/results.json > /tmp/reduce.txt
python3 docs/reports/data/2026-11-01-e98-heat-path-drift/checks.py
```
