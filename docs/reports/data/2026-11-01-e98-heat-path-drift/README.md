# E98 data: does the heat path's drift follow the room? One night on aifoundry2 (Q132, Sun 1 Nov 2026)

aifoundry2 card 0, under its own governor, at five points of one night: a rest of at least 15 min, the same nine sustained runs in the same order, then a 5.5 min hold of int8 neg_ones. **Nothing was set on the card**: TDP and threshold read 65 W and 65 °C at all 59 reads, every run's and both ends of every probe ([`checks.txt`](checks.txt) K10). The sampler ran without `--reset-ms`. It addresses item 9 of the kinds page's section 11: the heat path drifts between sessions, about 3 W at the trip between 23 and 31 October, with no room or inlet reading.

The pre-registration is [`tools/claims-v3/kspeed/e98/`](../../../../tools/claims-v3/kspeed/e98/README.md) (`c8e84226`, pushed 00:38:20 PDT, before the claim and the first launch), with amendments A1 (`52087494`, 01:02 PDT, while P1 ran, before any of its numbers were read) and A2 (`9b1c09f5`, 01:24 PDT, after P1 alone). The card was claimed in `#community-lab` at 00:39:10 PDT and released by editing the same post at 07:21 PST. Clocks went back at 02:00 PDT, so every time here is also UTC; the raw records are epoch ms. An independent verifier reproduced every registered number byte for byte and found that two post-hoc headlines overreached. The wrong sentences are corrected in place and listed at the end (Corrections after verification). No frozen file, data file, registered number or verdict changed.

| session | UTC | box clock | card min | what |
|---|---|---|---|---|
| `smoke/` | 07:39:24–07:40:06 | 00:39 PDT | 0.7 | 20 s idle, three 2 s launches; not analysed |
| `P1/` | 08:00:00–08:21:28 | 01:00 PDT | 21.5 | complete |
| `P2/` | 09:30:00–09:37:55 | 01:30 PST | 7.9 | **stopped by the other-user rule**, exit 3 (§ What was registered) |
| `P3/` | 11:40:00–12:00:59 | 03:40 PST | 21.0 | complete |
| `P6/` | 13:55:00–14:16:06 | 05:55 PST | 21.1 | complete |
| `P7/` | 14:40:00–15:00:57 | 06:40 PST | 20.9 | complete |

## Results first

### 1. The plain answer: in direction, yes; the rate is not established, and neither is the room as the cause

**The frozen verdict is E98-V `PARTLY`**: the hold follows the rest die (`SUPPORTS`), and the line follows it faster than the desk's 0.25 (`ABOVE_TARGET`).

- **For it.** When aifoundry2 idled warmer, its line read higher, its hold hotter and fp16 ones slower, all in the predicted direction. A card on aifoundry1 that never ran fell with aifoundry2's rest die (§5).
- **The rate is not established.** The line and the hold came out about twice the room's registered rates (0.50 against 0.25, 2.19 against 1.12), on one contrast. On the trip kinds, like for like, the night reads 0.94 [0.50, 1.38] against the five earlier sessions' 0.38 [0.11, 0.65]; at 0.94 E64's line would sit 3.5 °C above E80's, and it sits 1.28 °C above. The rest die's own noise adds about ±32% at 1 σ to every ratio, and no interval here carries it ([`corrections-check.txt`](corrections-check.txt) C2).
- **Against leaning on it.** Every registered slope is one contrast, P1 against P3, P6 and P7 (P1's leverage is 0.94). The hold moved **2.2 °C per °C of rest die**, and its interval holds both the room's 1.12 and a changed path's 2.08, so **the sharp discriminator did not discriminate**. Both numbers assume one R for rest and hold, so 2.19 does not lean to the path (C11). On the brief's 60 s rest reading, or on the raw history die, R1 and R2 both read `INCONCLUSIVE`. **E96**, the only other warm session of the night, at the same rest die as P1, does not repeat P1's lead on the trip kinds: 41.13 against 41.75 °C on the same two kinds, in a different run order, 1.8 σ (C10). Other experiments ran beside P1's hold, with no detectable effect on this card's idle reading (§4).

| rule | verdict | what the data say ([`results.json`](results.json), [`reduce.txt`](reduce.txt)) |
|---|---|---|
| **E98-R0** the rest die's own fall, and the gate | **INSIDE_BAND; gate OK** | **0.233 W = 1.01 °C**, first to last (expected 0.437 W = 1.89 °C; band 0.1–0.9 W). Range 1.01 °C against the gate's 0.75. Five probes counted, four for the line and the hold. `R0` |
| **E98-R1** the 76 s line on the rest die, against 0 and 0.25 | **ABOVE_TARGET** | **0.502 [0.305, 0.700]**, n 4, 2 df. `R1.fit`. Above the frozen 0.25; the interval overlaps the desk's corrected free-intercept fit, 0.336 ± 0.073, 95% about 0.02–0.65 ([desk README](../2026-11-01-q132-governor-desk/README.md), C2). The label is not a finding: §2 |
| **E98-R2** the hold's die on the rest die, against 1.00–1.25 and 0.25 | **SUPPORTS** | **2.19 [0.47, 3.90]**, n 4, 2 df. `R2.fit`. It reaches the band and lies wholly above 0.25. The interval also holds the path's 2.08, and those two numbers assume one R, so the estimate does not lean to the path (C11) |
| **E98-V** the room's reading | **PARTLY** | R2 `SUPPORTS`, R1 `ABOVE_TARGET`, as registered. `V` |
| E98-S1 the fine line on rest W, against 0 and 0.60 | INCONCLUSIVE | 0.38 W/W [−2.24, 3.00]. `S1.fit` |
| E98-S2 the hold's fine W on rest W, against 1.91–2.39 and 0.60 | SUPPORTS | **4.30 W/W [1.69, 6.91]**. `S2.fit`. The interval holds the band and the path's 3.97. Two instruments agree: the fine W says the same as the die (§3) |
| E98-S3 the from-rest run: fine W against 0 and 2.14; line against 0 and 0.89 | INCONCLUSIVE, twice | W 1.77 [−1.47, 5.02]; line 1.16 [−0.87, 3.19]; five probes, P2 included. `S3` |
| E98-S4 fp16 ones at the trip: clock against 0 and −12 MHz/°C; W against 0 and −1 W/°C | SUPPORTS; INCONCLUSIVE | **−17.5 MHz/°C [−29.2, −5.7]**; −1.60 W/°C [−3.26, +0.05]. `S4`. The clock's width has R1's problem: a residual of 2.2 MHz against the registered 16 MHz a probe, ±87 on that. On the raw die it reads −14.6 [−38.4, +9.2], on the 60 s rest −9.4 [−40.6, +21.8], both `INCONCLUSIVE` (C3) |

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

(`probes[].rest_w`, `rest20`, `rest60`, `R1.per_probe`, `hold`; `S4.per_probe`; K12.) Expected rest W at the freeze, in order: 22.105, 22.018, 21.801, 21.703, 21.668 (K8). **The rest die and aifoundry1's idle readings fell between P2 and P3 and then stayed flat**, so the night gave one step, not a slope. The room itself was not read. E96's reading between them (22.145 W, 46.79 °C at 10:05 UTC, [its README §5](../2026-11-01-e96-real-tensors-speed/README.md)) puts the step after 10:05 UTC.

*Dated note, Sun 1 Nov 2026, from the records (Q132(o)). Post hoc; no verdict changes.* **E97's second plateau move sits inside P6's rest window.** P6's 20 min rest runs 05:35:00–05:55:00 PST (`probes[].rest20.window_end_ms`). Between 05:39–05:41 and 05:44–05:46 PST, E97's two windows, aifoundry2's idle reading goes 45.79 to 47.00 °C (+1.21 °C, whole-degree readings), its board +0.28 W, its NIC +0.30 °C, with no row held and the CPU about 1%, and it is back by 05:50; aifoundry3's die moved +0.573 °C in the same windows, on a hold ([E97's `corrections-check.txt`](../2026-11-01-e97-heat-low-power-steady/corrections-check.txt) [C2]). So "stayed flat" holds for the 20 min means, not inside P6's window. Leaving out 05:42–05:49, P6's rest reads 21.874 W against 21.949 W, −0.32 °C of rest die, the contrast below reads 0.985 against 0.877 °C, and, as a sensitivity and not a verdict, R1 reads 0.458 against 0.502 and R2 1.93 against 2.19. One move, cause not established. ([`p6-rest-note.py`](p6-rest-note.py), [`p6-rest-note.txt`](p6-rest-note.txt), from `history/aifoundry2-2026-11-01.jsonl.gz`.)

**Every slope is that one step.** P1's leverage in R1 and R2 is 0.94; P3, P6 and P7 span only 0.31 °C of rest die (K1). The contrast, P1 minus the mean of the three: rest die +0.877 °C (W-derived), +0.878 °C (raw history); line +0.457 °C; hold die +1.973 °C; hold ioshire +1.859 °C; hold fine W +0.919 W; fp16 ones −15.5 MHz, −1.47 W (K1).

Dropping any later probe leaves R1 0.50–0.53 and R2 1.98–2.51. Dropping P1 leaves R1 0.29, R2 1.48 and S4 −14 on an x range of 0.31 °C, the same sign in noise. **Being first is not a carryover artefact: its sign is opposite.** aifoundry2's last work before P1 ended 4.6 h earlier (E87, 03:25 UTC), apart from the smoke. P3 followed 70 min of E96 by 25 min, P6 43 min of E101 by 52 min, P7 21 min of P6 by 24 min, and carryover would lift those. P2, not first and after E100, repeats the direction on the runs it has: its line leads by +1.56, +1.14, +0.62 °C on indexes 0–2, against P1's +0.73, +0.46, +0.39. But the trip kinds and the hold, which carry the slope, were read warm once. So the direction stands and the rate does not (C12).

**R1's narrow interval is not to be trusted, and `ABOVE_TARGET` is not a finding.** With 2 df it rests on a residual scatter of 0.036 °C a probe. On the eight positions' own scatter, 0.089 °C a probe (a lower bound, since positions within a probe are not independent), the same slope reads [0.018, 0.987], which holds 0.25 and only just excludes 0 (C4). On the registered planning noise, 0.15 °C, it reads [−0.313, 1.317], which holds both (K2). The label also sits near its edge: with every sample of the window R1 reads [0.270, 0.732], still above 0.25, and at k = 0.40 it reads [0.245, 0.709], `SUPPORTS`, which would make E98-V `SUPPORTED`, though the sessions' own k run 0.435–0.470 (E69's 0.57 rests on four runs). Frozen is frozen. **So the fair reading of R1 is "positive, about 0.5, not shown to differ from the desk's 0.25–0.35"**, whatever `ABOVE_TARGET` says. The hold's scatter among the later probes is 0.375 °C, as planned (0.40).

### 3. The hold is not a steady reading, and it grows apart during the hold

Both instruments agree on the contrast: 1.97 °C on the die, and 0.92 W of fine W is +2.08 °C at E64's 0.442 W/°C (inside the holds W per °C reads 0.39–0.62, median 0.456; K1). But the desk's "close to steady" was wrong. After 15 minutes of hotter runs, the die **falls** through the hold on P3, P6 and P7 (first minute to fifth: 59.37 to 58.00, 59.93 to 58.79, 59.74 to 58.67 °C) and stays flat on P1 (60.58 to 60.65 °C) (K9). So:

- In the hold's **first minute** P1 reads +0.90 °C above the later probes, against the rest die's +0.877. That is not a clean 1:1 reading: P1's runs before the hold drew 1.3 W less (52.4 against 53.5–53.8 W) and had about 30 s more gate cooling (82.5 against 49–58 s), so its first-minute lead is, if anything, understated (C8).
- By its **fifth minute** P1 reads +2.16 °C.

The extra degree arrives during the hold, on one probe. Three readings fit it, and the night cannot choose:

1. the room warmed during P1, only partly read (§4);
2. the path's resistance was higher;
3. chance: one contrast, 0.4 °C of scatter a probe.

The numbers do not choose either. The room's 1.12 and the path's 2.08 use the 76 s R, 0.4573 °C/W, for both a rest of hours and a 5.5 min hold, and the loop grows with time. With R 1.1 at rest and 0.65 in the hold they read 1.05 and 1.94; with 1.47 in both, 1.88 and 3.49 (C11).

The hold's registered sanity range (die 60–64.5 °C, W 40–43.5) was also wrong for the same reason. Three holds read 58.05–58.80 °C, and two read just under 40 W. That range decides nothing.

### 4. What ran beside it

The design took the night's cooling as the only thing moving. Other experiments ran beside it (C5). Beside P1: E94 on aifoundry1 card 1 (41 W mean, about +11 W over idle) and E99 on aifoundry3 (33–35 W, about +11 W). Beside P3: E97 on aifoundry3 (29–31 W, about +7 W). Beside P6: E97 (44–46 W, about +21 W) and, for part of its work, an aifoundry1 run. At P7's end, nothing. Share of each box's rows with a card held (K11):

| probe | aifoundry1, work | aifoundry3, work | both at the hold's end | hold die |
|---|---:|---:|---|---:|
| P1 | 0.95 | 0.67 | yes (1.00, 0.90) | 60.42 |
| P3 | 0.00 | 1.00 | aifoundry3 only | 58.05 |
| P6 | 0.60 | 1.00 | aifoundry3 only | 58.80 |
| P7 | 0.00 | 0.20 | neither | 58.49 |

P1 is the one probe with both other boxes running at its hold's end. **The boxes' own history shows no detectable effect on this card's idle reading, and bounds it at about half of P1's extra degree; the best estimate is about 0.** Over nine days plus the night (176 rested 60 min differences of aifoundry2's idle W, with the hour of day), aifoundry1 running moves it −0.18 W [−0.50, +0.14] and aifoundry3 running −0.10 W [−0.21, +0.01]. Those upper limits are +0.60 °C and +0.05 °C of rest die, against an extra 1.10 °C (C5). The hold's order does not follow it either: P3, with aifoundry3 on, reads 58.05 °C, below P7, with neither, at 58.49 °C.

No other box read the room during P1's hold, since aifoundry1's rows are blank while either card is held. aifoundry2's own NIC and NVMe did read through it. P1 minus the later probes: NIC +0.67 °C at rest and +1.20 °C at the hold's end, NVMe +0.77 and +1.00 °C. The card's extra 0.9 W is worth only about +0.05 °C at the NIC, so about half a degree of the die's extra 1.1 °C shows at box level (C6). It is self-heated, and one contrast, but it is a partial reading.

P3's hold, the coolest, fell at the lowest point of aifoundry1's idle readings: aifoundry1's idle die and NIC fell through that probe (47.0 to 46.0 °C, 52.75 to 52.20 °C; K5), and K4's 30-minute table has its minimum at 12:00 UTC.

### 5. The rest die's fall is shared, with a card on another box that never ran

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

(`proxies`, K13.) The estimates sit at the nine-day relation, but those intervals rest on rows not clean of aifoundry1's own run: the registered filter has no skip after busy, and all 173 of its rows counted for P1 lie within 15 min after a run of its own ended at 07:45:30 UTC. With a 15 min skip P1 has none and P6 too few, so n is 3: a1 card 0 die 0.88, a1 NIC 0.92, a1 card 1 W 0.45, and every interval holds 0 (C7).

**The claim holds on better ground.** aifoundry1's card 0 was never held all night (0 of 6,025 rows). On clean rows it read 18.66 W, 47.8 °C at 06:00–07:00 UTC and 18.635 W, 47.67 °C at P2, then 18.42–18.46 W, 47.0 °C at P3 and P7. P3's rows follow a longer run of that box by less time than P2's, 90 min ended 32 min before against 39 min ended 51 min before, so its own heat works against the fall. **So what fell at rest was not this card alone, and it is unlikely to be this card's own state or E96's use of it.** That answers refutation 4 of the registration: the other box did fall. aifoundry3 had rows in only two counted probes, its card busy, so it is not scored. The line and the hold against a1's NIC, labelled: 0.431 [0.335, 0.528] and 1.89 [0.70, 3.08]. Both carry the same step.

### 6. The gate's reason for 0.25 is not supported, and A2's split came out reversed

A2, written after P1, reasoned that the runs the gate never held (indexes 1–4) should read 0.89 and the held ones (indexes 5–8) 0.25, so about 0.62 pooled. **The pooled number came out near that, 0.50, and the split's point estimates came out the reverse:**

| arm | A2 expected | on the 20 min rest | on the 60 s rest |
|---|---:|---|---|
| at or near the trip, indexes 5–8 (A2's "held") | 0.25 | **1.02 [0.79, 1.25]** | 0.39 [−1.74, 2.52] |
| early, indexes 1–4 (A2's "unheld") | 0.89 | **0.11 [−0.41, 0.63]** | 0.13 [−0.13, 0.40] |

(`arms`, K3.) So the desk's untested reason for "0.25 and not 1", a gate's anchor, **is not supported**: these are arms of 2 df, with the interval §2 says not to trust. "Held" was also a misnomer: index 5 was held 0–1.4 s in every probe, and indexes 5–6 did not trip on P3 and P7 (C8). The runs at or near the trip are the ones that read about 1:1 here. At the trip the die is pinned and the line moves through W, which leaves no whole-degree noise (rms 0.03 °C). My reading, post hoc: the card there has settled against its limit, while the early runs of a series from a cold card are still warming. By position, K8 shows no steady growth: +0.46, +0.39, −0.15, −0.13 °C on indexes 1–4 and +0.79, +1.14, +0.57, +1.06 °C on indexes 5–8.

**An early run follows the state just before it, not the 20-minute mean** (post hoc, K3). With P2's runs included, five probes:

- the fine W of indexes 1–3 follows the **60 s** rest W at 0.678 W/W [0.505, 0.851], rms 0.015 W;
- on the 20 min rest W the same reads 0.70 [−1.08, 2.47], rms 0.089 W;
- the from-rest run's line on the 60 s rest reads **0.887 [0.433, 1.342]**, against the registered 0.89 for a linear system, though that registered rule was on the 20 min reading and came back inconclusive.

So the 20 min reading was the better one for the end of a probe and the worse one for its start, and a registered "rest" needs both.

### 7. Across sessions: the same size as E64 to E80, and every comparison leans on E64

Post hoc, K6 and K12, against each session's raw rest die. Sessions differ in history, E64 has much of the leverage, and E96 reads a little low, as its own README says (+0.03 per °C on its four kinds, one point, about 1 σ).

| quantity | fit | points |
|---|---|---|
| fp16 ones' clock | −13.8 MHz/°C [−18.8, −8.7]; **E64's leverage is 0.91** | E64, E80, P1, P3, P6, P7 |
| fp16 ones' clock, **without E64** | **−9.5 MHz/°C [−28.2, +9.1]** | E80, P1, P3, P6, P7 |
| fp16 ones' board W | −1.24 W/°C [−1.78, −0.69] | E64, E80, P1, P3, P6, P7 |
| fp16 ones' board W, **without E64** | **−0.78 W/°C [−2.77, +1.21]** | E80, P1, P3, P6, P7 |
| fp16 ones, E64 to E80 alone | −12.0 MHz/°C, −1.06 W/°C | the two sessions that are the 3 W |
| fp16 ones, the night alone | −14.6 MHz/°C [−38.4, +9.2], −1.29 W/°C [−4.00, +1.41] | P1, P3, P6, P7 |
| mean line of int8 full and fp32 randn | 0.41 °C/°C [0.23, 0.59]; without E64 0.58 [0.20, 0.96]; the five earlier sessions alone 0.38 [0.11, 0.65]; **the night alone 0.94 [0.50, 1.38]** | E64, E80, E83, E87, E96, P1, P3, P6, P7 |
| int8 full's clock | −9.3 MHz/°C [−13.7, −5.0]; without E64 **−13.7 [−22.8, −4.7]** | the same nine |

**Item 9's 3 W.** E64 to E80, fp16 ones gained 3.93 W over 3.70 °C of rest die. The night's step, about −15.5 MHz over 0.88 °C of rest die, one probe against three, is the same size as E64 to E80's −12 MHz/°C. **Whether the rest die accounts for the 3 W is not shown: every session that says so is measured against E64.** Without E64 the fit holds 0 (C1). The rest die is also read on the same card, so a change of the path would raise it too (22 W × ΔR). E69, held out of these fits, points the same way: +25.5 MHz and +2.51 W on fp32 ones for a rest die 2.6 °C cooler, −9.8 MHz/°C and −0.96 W/°C, but again against E64.

**Which side of the trip int8 full lands on tends to follow the rest die.** E87 §4 found single runs on either side "whatever the data". In the night's four probes its clock orders with the raw rest die, 800.0, 793.6, 783.9, 773.4 MHz at 45.68, 46.09, 46.20, 46.87 °C, with E80's 793.4 at 45.58 °C, E83's 786.5 at 46.42 °C and E87's 774.7 at 47.15 °C beside them. E96 breaks the order: 789.4 MHz at 46.79 °C, above E83 and P6, and its four runs in one session span 777–795 MHz.

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

**Item 9 is narrowed, not closed.** What stays open:

- **The cause.** An inlet thermometer is the one reading all of this lacks.
- **A probe at E64's own idle die, on a warm day.** The nine-day hour means reach 49.1–49.6 °C at 16:00–20:00 PDT, against 46.1 °C at 11:00: a 3.5 °C range, against the night's 1.0 °C. It takes a warm day, since 31 October's evening only reached 47.15 °C. Does fp16 ones fall back to about 737 MHz and 49 W? It is the only test of E64 itself, and every number here leans on E64 or on P1 (C13).
- **More than one warm probe with the full series, on a night with the other boxes quiet.** Whether P1's lead on the trip kinds and the hold repeats at all is unknown.
- **The fans**, unread.

**What a reader may be told, each with its source:**

- By morning aifoundry2's card idled about 1 °C cooler (22.11 to 21.88 W), and a card on another box that never ran fell by about as much (47.67 to 47.0 °C) between the same probes ([`results.json`](results.json) `probes[].rest_w`; [`corrections-check.txt`](corrections-check.txt) C7).
- On the warmest of four probes, fp16 ones ran 771 MHz, against 784–790 MHz on the three cooler ones. One probe against three, near the thermal limit (`S4.per_probe`, C9).
- That step is the same size as the one between 23 and 31 October (−12 MHz per °C of idle die), which does not show that one caused the other (C1).
- A held 41 W load read 2 °C hotter on that probe, and we cannot tell the room from the heat path (`R2`, K9, C11).
- The cause is not measured: no inlet thermometer.

**May not be said from this directory:** "the room causes the drift"; "1:1"; "0.25 per °C" or "0.50 per °C" or "2.19 per °C" as a rate; "14 MHz per °C across sessions" without saying that E64 carries it; "enough to account for the 3 W" or "without any change of the path"; "the night sits on the line" unqualified; "other experiments heated the room"; "at the thermal limit" of all those runs; "the gate is, or is not, why"; anything beyond this card.

**Wording for the kinds page, for the integration step** (this lane edits neither):

- **§4, at most one sentence, after the die line:** "That line's height moves with how warm the card idles: on one night of aifoundry2 the warmest of four probes sat 0.46 °C above the other three for 0.88 °C of idle die ([E98]); one contrast, cause not measured." Its existing "cause is not measured" stays, as does "the line belongs to the card".
- **§11 item 9, kept open and narrowed:** "The heat path drifts between sessions: about 3 W at the trip between 23 and 31 Oct. One night on aifoundry2 (E98, four of a planned seven probes complete; two dropped for another experiment, one stopped by another user's login): the idle die fell 1 °C with another box's, and the warmest probe ran slower and hotter, in the direction a warmer room predicts. It is one warm probe, the frozen verdict is PARTLY, and the hold's rate cannot tell room from path. Needs an inlet thermometer, a probe at 23 Oct's idle die, and more than one warm probe."

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
| `checks.py`, `checks.txt` | post-hoc checks K1–K13, labelled, deciding nothing; left as committed, with K2's positional line and K6's fp16 ones rows superseded by the check below |
| `p6-rest-note.py`, `p6-rest-note.txt` | added 1 Nov 2026 by the records (Q132(o)), post hoc, deciding nothing: E97's second move in P6's rest window (§2's dated note) |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind Corrections after verification: every number that section quotes, from committed files (standard library only) |

The three slots: E100 1793521800–1793524200 (01:30 PDT–01:10 PST), E96 1793527500–1793532000 (02:05–03:20 PST), E101 1793535600–1793540100 (04:20–05:35 PST).

Reproduce from the top of the repository:

```bash
python3 tools/claims-v3/kspeed/e98/reduce_e98.py docs/reports/data/2026-11-01-e98-heat-path-drift --out /tmp/results.json > /tmp/reduce.txt
python3 docs/reports/data/2026-11-01-e98-heat-path-drift/checks.py
python3 docs/reports/data/2026-11-01-e98-heat-path-drift/corrections-check.py
```

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E98 after the data commit (`f988909f`). It reproduced `results.json`, `reduce.txt`, `checks.txt` and the self-test byte for byte from a clean export, recomputed the registered numbers from the raw telemetry with its own parser, and found the registration, the harness and the public text clean. Its verdict was holds-with-fixes: two post-hoc headlines overreached, and the rest is wording or a small number. Each fault was checked against the committed data and corrected above, desk only: no card was touched, nothing was re-run, and **no frozen file, data file, registered number or verdict changed.** Every number below is printed by [`corrections-check.py`](corrections-check.py) into [`corrections-check.txt`](corrections-check.txt), under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Major: "enough to account for the 3 W … without any change of the path" is circular.** The −13.8 MHz/°C fit is drawn through the 3 W: E64's leverage in it is 0.91, and E64 and E80 are the 3 W. Without E64: −9.5 MHz/°C [−28.2, +9.1], −0.78 W/°C [−2.77, +1.21], both holding 0. §7 printed a without-E64 row for the line and for int8 full, not for this. The registered W rule, S4, read `INCONCLUSIVE`. And the rest die is read on the same card, so a change of the path would raise it too | §7 gains the rows; its heading changes. The sentence now says the night's step is the same size as E64 to E80's, and that whether the rest die accounts for the 3 W is not shown. E69's fair support is added, with its dependence on E64 |
| C2 | **Major: "in direction and rough rate, yes" softened the frozen outcome.** The line and the hold came out about twice the room's registered rates; the trip kinds read 0.94 [0.50, 1.38] in the night against 0.38 [0.11, 0.65] before it; at 0.94 E64's line would sit 3.5 °C above E80's, and it sits 1.28 °C above. The rest die's own noise puts ±32% at 1 σ on every ratio | §1: "in direction, yes; the rate is not established" |
| C3 | S4's width has R1's problem and carried no warning: a residual of 2.2 MHz against the registered 16 MHz a probe, ±87 on that | §1's row carries the warning and both other readings: −14.6 [−38.4, +9.2] on the raw die, −9.4 [−40.6, +21.8] on the 60 s rest, both `INCONCLUSIVE` |
| C4 | R1's positional interval used rms over n: `checks.py` K2's 0.063 °C should be 0.089 °C on n − 2. Correct: [0.018, 0.987], not [0.159, 0.845]. The label also sits near its edge: [0.270, 0.732] on every sample, [0.245, 0.709] at k = 0.40, which would read `SUPPORTS` | §2. `ABOVE_TARGET` is scored as frozen and is not cited as a finding |
| C5 | **"Other experiments were heating the same room unevenly" was stated as fact, with no size.** The boxes' history shows no detectable effect on this card's idle reading | §1 and §4 say what ran beside each probe, and give the size: upper limits +0.60 °C and +0.05 °C of rest die against an extra 1.10 °C, about half at most, best estimate about 0 |
| C6 | "Nothing read the room during P1's hold" was too strong. aifoundry2's own NIC and NVMe read through it: NIC +0.67 °C at rest, +1.20 °C at the hold's end; NVMe +0.77, +1.00 °C | §4 gives them as a partial, self-heated reading |
| C7 | "Every interval on the other box excludes 0" rests on rows not clean of aifoundry1's own run. With a 15 min skip n is 3 and every interval holds 0 | §5 says so, and rests the claim on better ground: aifoundry1's card 0 was never held, and it fell on clean rows |
| C8 | Words that outran the evidence. "The room fell": the room was not read. "Wrong", "does not stand": the point estimates are reversed on arms of 2 df, so "not supported". "Held": index 5 was held 0–1.4 s and indexes 5–6 did not trip on P3 and P7. "+0.90 °C, about 1:1": P1's runs before the hold drew 1.3 W less and had about 30 s more gate cooling. "Follows the rest die": E96 reads 789.4 MHz at 46.79 °C, above E83 and P6. K12's heading promises the limit and prints only the clock; the limits are in K3 and C8 | §2, §3, §6, §7 |
| C9 | "At the thermal limit": the 784–790 MHz average index 5 and index 8, and index 5 did not trip on P3 or P7. Index 8 alone, at the trip in all four: 765 against 782–786 MHz | The reader's sentence says "near the thermal limit" |
| C10 | E96 belongs in "against". It is the only other warm session of the night, at the same rest die as P1 (46.79 against 46.87 °C), starting 35 min after P2 began, and on the same two trip kinds it reads 41.13 against P1's 41.75 °C. A different run order, 1.8 σ, so not a refutation, but P1's lead on the trip kinds has no replicate and this is the nearest try | §1 |
| C11 | The discriminator's 1.12 and 2.08 assume one R, the 76 s R for a rest of hours and a 5.5 min hold. With R 1.1 at rest and 0.65 in the hold they read 1.05 and 1.94; with 1.47 in both, 1.88 and 3.49 | §1 and §3: "the estimate sits by the path's 2.08" is withdrawn, since 2.19 does not lean to the path |
| C12 | Added from the verifier's checks: leave-one-out, and why being first is not carryover | §2 |
| C13 | Added: a new open test, a probe at E64's own idle die on a warm day, 16:00–20:00 PDT. The reader's sentences, the may-not list and the wording for the kinds page's §4 and §11 item 9 are the verifier's, with the sources added | What it fills |

**Not taken as written, each checked against the data:**

- **"Roughly a third to a half of P1's extra degree."** The upper limits are 0.60 °C from aifoundry1 alone, 55% of the extra 1.10 °C, and 0.65 °C with aifoundry3, 60%. So the text says "about half at most". The best estimate of about 0 stands.
- **"P3 and P6 had E97 (31 W, about +8 W)."** That holds for P3 (29–31 W). Beside P6, E97 read 44–46 W, about +21 W, and an aifoundry1 run overlapped P6's work. The hold's order still does not follow it: P3 58.05, P7 58.49, P6 58.80 °C.
- **Small numbers differ from the verifier's in the last digit**, because this check uses the runs' unrounded values: −9.5 [−28.2, +9.1] for [−28.0, +9.1], 0.94 [0.50, 1.38] for 0.93 [0.51, 1.35], [0.018, 0.987] for [0.017, 0.987], 1.3 W for 1.2 W. None changes a reading.

The verifier did not check the committed raw files against the box's originals, or `thin_history.py`'s cut against the box's full history; neither does this check.
