# E97 — the rest of the heat column, and a measured steady state (Q132, aifoundry3 card 0, 2026-11-01)

*Pre-registered in [`tools/claims-v3/e97/E97.md`](../../../../tools/claims-v3/e97/E97.md) with [`predictions-e97.json`](../../../../tools/claims-v3/e97/predictions-e97.json), scorer, self-test and desk checks, committed as **`49de6d33`** and pushed at **01:16:49 PST**, 74 minutes before the card was claimed in `#community-lab` (02:30:39 PST, message `1566399064692752435`) and the first device access (a read-only `ettelem config`, 02:30:42). No amendment was written. Card runs **02:30:42–06:48:24 PST on aifoundry3 card 0 only**: the probe and smokes 9701–9702 (to 02:33:05), then the detached queue, 02:33:35–06:44:13: Part A passes **9710** (02:33:36–03:41:53) and **9711** (03:41:53–04:50:11), Part B pass **9720** (04:50:11–06:44:13), and a closing read-only `ettelem config` (06:48:24). 600 MHz in every sample; 520–523 mV; TDP 0 and threshold 65 °C at every read; nothing set; no statistics reset. **Released at about 06:59 PST** by an edit of the same post, read back as `<ai> Claude says: using aifoundry3 for 5 h, until ~07:15 PST doc — released (edited)`.*

> **What this is.** E78's heat column resolved only the kinds above about 12 W of switching. E89 read the die's 34 sensors as raw codes and measured seven of the 32 kinds below that; the other 25 stayed *S × 0.118 °C/W*, and no steady-state rise had been measured. **Part A** runs E89's harness, byte for byte, on those 25 kinds and E86's three int8 GPT-2 tiles, beside fp32 random, two passes. **Part B** holds three kinds about 30 minutes from a rested die, on the same sensors, with the idle read before and after. This is item 8 of the kinds page's section 11.

## Results

**107 PASS, 36 INCONCLUSIVE, 8 FAIL of 151 registered verdicts, with the independent pass as the unit in Part A** ([`scored.json`](scored.json) `tally`). **Six of the eight FAILs were predicted** (the lab's thermal model and E73's gain do not describe this die: E97-B2a, B2b ×3 each). **Two were not: E97-B1 on H1 and H3, the steadiness test**: the die wandered during the holds, apparently with the room (result 4). The 36 inconclusive cells are the pass as the unit, n = 2 at t = 12.706 (E97-R2 22, R5 11, R4 2) and E97-R6: scored as E89 scored them, with the lap as the unit, 112 of the 113 cells of R1, R2, R4 and R5 PASS and one is inconclusive (R5, fp32 zeros). All 58 blocks and all three holds passed their gates: 794 block launches with no failure, every one of the 11,246 kernel records at 546 or 318 cycles per op ([`e97.json`](e97.json) `gates`).

**1. Heat per watt on all 28: every point inside the registered band, 1.06–1.13 times fp32 random per board watt and within 7% per minion-rail watt on 27 of 28; with the pass as the unit, most of the intervals are too wide to confirm the bands.** Each kind is switched once a minute against its type's zeros, or, if its E78 D is under 2 W, against idle. H = the die's fundamental over the board's; r = H / H of fp32 random ([`results.md`](results.md), [`e97.json`](e97.json) `blocks`). Per board watt the point r is 1.082–1.130 against idle (mean 1.110) and 1.062–1.101 against zeros (mean 1.075), the same two levels E89 found (1.11; 1.04–1.07). Per minion-rail watt, **now registered**, it is 0.989–1.008 against zeros (mean 0.999) and 0.987–1.073 against idle (mean 1.020). The one point outside [0.93, 1.07] is fp32 zeros, 1.073 (lap interval [1.034, 1.113]), so E97-R6 reads INCONCLUSIVE. **With the pass as the unit, most of these band tests cannot resolve:** the reference's two passes read 0.1993 and 0.1945 °C/W, which alone is ±15% at t = 12.706: R2 PASS 6, INCONCLUSIVE 22; R4 PASS 26, INCONCLUSIVE 2; R5 PASS 17, INCONCLUSIVE 11. None is wholly outside. The session tie holds: H_ref 0.1969 against E89's 0.1979 °C/W (E97-R3 PASS). Every kind's heat was detected, with the pass as the unit (E97-R1 PASS ×29).

| kind (S low to high) | against | E78's W | die fundamental at 1/60 Hz (°C) | r per board W [95%, pass] | r per minion-rail W [95%, pass] | 2 s rise over what it ran against (°C) | **2 s rise over idle (°C)** ±95% (lap) | S × 0.118 (°C) | ratio |
|---|---|---|---|---|---|---|---|---|---|
| fp32 zeros | idle | S 1.99 | 0.281 | 1.130 [0.762, 1.498] | 1.073 [0.863, 1.284] | 0.258 | **0.258** ± 0.004 | 0.234 | 1.10 |
| fp16 zeros | idle | S 1.99 | 0.264 | 1.082 [0.871, 1.292] | 1.006 [0.922, 1.089] | 0.259 | **0.259** ± 0.007 | 0.234 | 1.10 |
| fp32 sparse90 | idle | S 2.51 | 0.352 | 1.106 [0.893, 1.319] | 1.031 [0.821, 1.241] | 0.338 | **0.338** ± 0.008 | 0.296 | 1.14 |
| fp32 a_randn_b_zeros | idle | S 2.57 | 0.364 | 1.130 [0.878, 1.382] | 1.050 [0.860, 1.241] | 0.337 | **0.337** ± 0.003 | 0.304 | 1.11 |
| fp16 wsparse90 | idle | S 2.64 | 0.359 | 1.093 [0.693, 1.492] | 1.009 [0.792, 1.225] | 0.349 | **0.349** ± 0.014 | 0.312 | 1.12 |
| fp16 a_randn_b_zeros | idle | S 2.67 | 0.362 | 1.115 [0.944, 1.286] | 1.045 [1.027, 1.063] | 0.342 | **0.342** ± 0.011 | 0.315 | 1.09 |
| fp16 a_zeros_b_randn | idle | S 2.71 | 0.373 | 1.118 [0.946, 1.290] | 1.032 [0.902, 1.162] | 0.356 | **0.356** ± 0.010 | 0.320 | 1.11 |
| fp32 a_zeros_b_randn | idle | S 2.84 | 0.370 | 1.105 [0.766, 1.443] | 1.012 [0.736, 1.288] | 0.360 | **0.360** ± 0.021 | 0.335 | 1.07 |
| int8 a_zeros_b_full | idle | S 2.90 | 0.395 | 1.126 [0.921, 1.331] | 1.003 [0.831, 1.176] | 0.377 | **0.377** ± 0.005 | 0.342 | 1.10 |
| int8 wsparse90 | idle | S 3.08 | 0.422 | 1.101 [0.919, 1.282] | 0.992 [0.941, 1.043] | 0.405 | **0.405** ± 0.009 | 0.363 | 1.11 |
| int8 a_full_b_zeros | idle | S 3.12 | 0.411 | 1.101 [0.851, 1.352] | 0.987 [0.807, 1.166] | 0.396 | **0.396** ± 0.002 | 0.368 | 1.08 |
| fp16 sparse90 | idle | S 3.38 | 0.458 | 1.107 [0.789, 1.424] | 1.018 [0.839, 1.196] | 0.435 | **0.435** ± 0.014 | 0.399 | 1.09 |
| int8 sparse90 | idle | S 3.76 | 0.515 | 1.123 [0.908, 1.337] | 1.014 [0.974, 1.054] | 0.490 | **0.490** ± 0.012 | 0.444 | 1.10 |
| int8 ones | idle | S 4.15 | 0.578 | 1.111 [0.885, 1.338] | 1.010 [0.986, 1.033] | 0.544 | **0.544** ± 0.008 | 0.489 | 1.11 |
| int8 wsparse50 | zeros | D 3.14 | 0.413 | 1.072 [0.883, 1.261] | 0.997 [0.851, 1.144] | 0.392 | **0.731** ± 0.077 (sum) | 0.678 | 1.08 |
| int8 highbit | zeros | D 3.23 | 0.422 | 1.101 [0.919, 1.283] | 1.006 [0.967, 1.045] | 0.432 | **0.772** ± 0.078 (sum) | 0.691 | 1.12 |
| int8 ternary | zeros | D 5.19 | 0.651 | 1.066 [0.887, 1.246] | 0.989 [0.915, 1.062] | 0.639 | **0.979** ± 0.062 (sum) | 0.912 | 1.07 |
| int8 GPT-2 l6 attention | zeros | D 5.54 | 0.719 | 1.082 [0.912, 1.252] | 1.007 [0.957, 1.057] | 0.653 | **0.993** ± 0.033 (sum) | 0.965 | 1.03 |
| int8 GPT-2 l6 MLP down | zeros | D 5.75 | 0.728 | 1.065 [0.900, 1.230] | 0.991 [0.949, 1.032] | 0.703 | **1.042** ± 0.100 (sum) | 0.979 | 1.06 |
| int8 pos | zeros | D 6.17 | 0.796 | 1.062 [0.891, 1.233] | 1.001 [0.984, 1.018] | 0.760 | **1.100** ± 0.072 (sum) | 1.030 | 1.07 |
| int8 GPT-2 l0 MLP up | zeros | D 6.29 | 0.810 | 1.073 [0.908, 1.238] | 0.999 [0.909, 1.089] | 0.770 | **1.110** ± 0.069 (sum) | 1.043 | 1.06 |
| fp16 wsparse50 | zeros | D 7.06 | 0.893 | 1.075 [0.886, 1.264] | 0.997 [0.972, 1.022] | 0.926 | **1.185** ± 0.185 (sum) | 1.073 | 1.10 |
| int8 sorted | zeros | D 6.59 | 0.846 | 1.071 [0.857, 1.285] | 0.999 [0.947, 1.051] | 0.775 | **1.115** ± 0.006 (sum) | 1.082 | 1.03 |
| fp32 sparse50 | zeros | D 7.30 | 0.921 | 1.070 [0.841, 1.299] | 0.996 [0.928, 1.064] | 0.937 | **1.195** ± 0.171 (sum) | 1.091 | 1.10 |
| fp32 −1 | zeros | D 8.14 | 1.061 | 1.074 [0.789, 1.360] | 0.996 [0.858, 1.134] | 1.072 | **1.331** ± 0.173 (sum) | 1.194 | 1.11 |
| fp16 −1 | zeros | D 8.38 | 1.063 | 1.067 [0.903, 1.231] | 0.995 [0.958, 1.031] | 1.064 | **1.322** ± 0.168 (sum) | 1.222 | 1.08 |
| fp16 ones | zeros | D 8.45 | 1.072 | 1.085 [0.914, 1.257] | 1.008 [0.999, 1.016] | 1.062 | **1.320** ± 0.157 (sum) | 1.224 | 1.08 |
| fp32 π | zeros | D 8.47 | 1.078 | 1.080 [0.915, 1.245] | 1.001 [0.951, 1.050] | 1.080 | **1.338** ± 0.168 (sum) | 1.227 | 1.09 |
| fp32 randn, the reference | zeros | D 24.72 | 3.007 | 1 | 1 | 2.848 | 3.11 (sum) | 3.15 | E78 measured 3.16 ± 0.08 |

**2. The heat column has no E78 kind left to extrapolate.** With E89's seven, all 32 kinds at or below 12 W of S now rest on the fine reading: here 14 measured directly over idle and 11 as a sum (the rise over its type's zeros plus that zeros' rise over idle: fp32 and fp16 zeros 0.258 and 0.259 °C from this run, int8 zeros E89's 0.340 °C, assuming 2 s responses add), and E86's three int8 tiles as sums. **The extrapolation read low: measured over *S × 0.118* is 1.03–1.14 on the 25 kinds, median 1.10** (E97-R7 PASS), and 1.03–1.06 on the three tiles. Per watt of S the 2 s rise is 0.121–0.135 °C/W, median 0.129; on the 14 measured directly, 0.127–0.135. The check on the sum: fp32 random's derived 3.11 °C against E78's measured 3.16 ± 0.08 °C. **A sum carries a baseline dependence the direct cells do not:** see § Joins and traps.

**3. A measured steady state: about 0.9 °C per board watt on this card, and a third of the watts are leakage.** One hold per kind, so each ± is a bound on that hold (half the idle-before/after difference, and the last 300 s's scatter), not a replicated interval ([`e97.json`](e97.json) `holds.holds`; [`results.md`](results.md) § Part B):

| hold | launches, gaps, compute share | idle before → after (°C) | die, last 300 s (°C) | **rise (°C)** | board's rise (W) | **per board W** | per minion-rail W | per W of S × share | leakage's part of the board's rise | loop gain | closure |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **H1 int8 full**, 30 min | 244, 0.23 s, 0.965 | 50.56 → 50.63 | 62.40 | **11.80 ± 0.05** | 13.12 | **0.899** | 1.156 | 1.267 | 3.91 W, 0.30 | 0.36 | 0.99 |
| **H2 fp32 ones**, 15 min **chained on H1** | 126, 0.23 s, 0.963 | 50.56 → 50.63 | 63.78 | **13.17 ± 0.04** | 14.30 | **0.921** | 1.201 | 1.329 | 4.48 W, 0.31 | 0.39 | 0.99 |
| **H3 fp32 randn**, 30 min: natural to the stop, then reduced | 257 (31 natural, 226 reduced), 3.04 s, 0.560 | 50.63 → 50.66 | 70.37 | **19.72 ± 0.03** | 22.49 | **0.877** | 1.205 | 1.318 | 7.51 W, 0.33 | 0.44 | 1.00 |

- **Which prediction held.** The chain fitted to E89 on this card said 0.861 °C per board W: rises of 11.6, 12.5 and 19.6 °C; measured 11.8, 13.2 and 19.7 (E97-B2c PASS ×3). The lab's thermal model, 1.47 °C/W, is aifoundry2's in September, before the October cooling changes; E73's 0.25–0.30 °C/W is the camera on aifoundry2's back of the board. Neither describes this die's steady rise (E97-B2a, B2b FAIL ×3 each, as predicted), which does not refute either on its own card and place.
- **Linear in board power, not in switching power.** Rise per board W, H3 over H1, 0.975, H2 over H1, 1.024 (E97-B3 PASS); per minion-rail W 1.042 and 1.039 (E97-B4 PASS); per W of S at the compute share, H3 over H1 1.040, predicted 1.059 from leakage (E97-B5 PASS; 1.03 on H1's plateau before its bump, [windows]). The bounds under these ratios do not include the wander of result 4.
- **How much arrives when (H1).** 0.45 of the rise by 60 s and 0.90 by 5 minutes (E97-B6 PASS, against the frozen 0.45 and 0.87; the lab's model said 0.22 and 0.55, E73's one pole at least 0.90 by 60 s); 0.21 by 10 s, 0.32 by 30 s, 0.64 by 2 minutes, 0.99 by 10 minutes. **By 30 minutes nothing more arrives that this reading can separate from the wander of result 4.**
- **fp32 random at its natural chain reaches the lab's stop in 221 s from a rested die** (E97-B10 PASS; the frozen chain said 220 s). The firmware read 78 °C first at 216.5 s, the 34-sensor mean then 78.45 °C, the board 63.1 W, the die still climbing 4.1 °C a minute; hottest sensor 81.15 °C ([`posthoc.txt`](posthoc.txt) [stop], [peaks]). It has no measured steady state below the stop; the frozen chain with E71's leakage says it has none short of a runaway, which nothing here tests. In the reduced phase (3.5 s launches every 7 s, compute share 0.56) it settled 19.7 °C above idle.
- **Leakage's contribution.** From the pass's rests pooled, idle board power rises 0.40 W/°C at the H1 hold's 62.4 °C and 0.50 at H3's 70.4 °C. So leakage is 30%–33% of the board's rise (E97-B8 PASS ×6), owed 3.5, 4.1 and 6.6 °C of the rises; the loop gain is 0.36–0.44 at 62–70 °C. **The rest closes on E78's switching power:** (board's rise − leakage's part) / (S × share) = 0.99, 0.99, 1.00 (E97-B9 PASS ×3). The law reproduces E71 on this card: 0.308 W/°C over 51–58 °C (E71 0.320) and 0.381 over 58–62 °C (E71 0.3803) (E97-B7 PASS ×2). H3's hold sits 5.6 °C above the rests' top bin, so its leakage is carried; post hoc, board power in the reduced phase's 3 s gaps agrees with the carried law to 0.04 W at 69.25 °C ([`posthoc.txt`](posthoc.txt) [gaps]).
- **How long a rest takes.** To within 0.1 °C of the starting idle: 525 s after Part A, 525 s after H2, 555 s after H3 from 70 °C (30 s bins). The board to within 0.05 W of its final idle: 465–495 s. So on this card a rest to within 0.1 °C takes about 9 minutes after rises of 7–20 °C, not the 30–35 this registration allowed (departure D2).

**4. The holds did not sit still: the plateau wandered about ±0.4 °C, and the largest move lines up with a CPU burst on another box.** The frozen steadiness test fails on two of the three: slope over the last 10 minutes -0.102 °C/min on H1 and +0.025 on H3, against |0.02| (E97-B1 FAIL ×2; H2 -0.007, over 5 minutes, PASS). Post hoc ([`posthoc.txt`](posthoc.txt) [wander], [bump], [room]): H1's rise reached a plateau near 12.0 °C by minute 13, then rose to 12.8 °C at minute 19 with the tile and clock unchanged, and fell to 11.7 °C by minute 30. **That bump was the same on all 34 sensors: 0.790 °C, standard deviation 0.008 °C**, where the hold's own rise varies 11.2–12.5 °C across them; the board rose 0.33 W, what leakage alone gives for it (0.32 W). It began within a minute of a host-CPU burst on aifoundry1, 05:19–05:22 PST (whole-machine CPU use 37%, its CPU sensor 85 °C, the only burst of the session on any box), and NIC or NVMe sensors on all three boxes and aifoundry2's idle card moved with it. A second rise on H2, about 0.5 °C at 05:42–05:44, has NVMe and NIC moves on two boxes but no burst beside it. So the plateau wanders about ±0.4 °C, more than the bounds in the table: on other windows the rise per board W is 0.90–0.91 on H1 away from the bump and 0.94 on it, 0.90–0.92 on H2, 0.87–0.88 on H3 ([windows]). **Read the steady resistance as 0.87–0.92 °C per board W, not to three figures.** This is one event, read from timing: a coincidence with an air-handling cycle is not excluded.

**5. The reading.** All 150,295 samples carry 34 sensors (100%), and the firmware's integer mean rebuilt from the codes equals its `minshire_avg` in 98.3% (E97-R0 PASS). Command 74 group 0 still returns raw codes (probe, 1,960–2,004). No fault bit in any sample; the sensors' high latch never moved backwards and stayed at 2543 codes (87.5 °C), as in E89. With every shire loaded alike the per-sensor pattern at steady state correlates 0.994–0.995 with E89's at 1/60 Hz: sensor 0 coolest, sensor 30 warmest ([pattern]).

## What it changes

- **The kinds page's heat column.** The *italic ≈* cells go. Every E78 kind below 12 W gets the "2 s rise over idle" of the table above, marked measured or sum; E89's fp32 ones becomes a sum on a measured fp32 zeros, 1.32 °C. E86's three int8 tiles, 0.99–1.11 °C, leave their extrapolations too. **How many kinds stay extrapolated: none of E78's 51.** Still extrapolated: only E95's real2 tiles below 12 W, which were not run here; for those, S × 0.129 (the median measured here) is a better coefficient than 0.118, and that is an extrapolation.
- **Item 8, "heat below about 12 W".** Closed for E78's kinds and E86's tiles on this card, at the fine reading. "No steady-state rise is measured" no longer holds: three kinds are measured, each once, on one card. Still open: a replicate of any hold, another card, a steady state for fp32 random at full duty (it reaches the lab's stop first), and E95's tiles.
- **The page's section 4, leakage.** On this card, measured: loop gain 0.36–0.44 at 62–70 °C, leakage 30%–33% of the board's rise. Section 4's "about 0.5–0.6" takes the lab model's 1.47 °C/W; on this card's measured 0.87–0.92 and the idle law's 0.44 W/°C at 65.5 °C, the same arithmetic gives about 0.40 (post hoc). aifoundry2's steady resistance since the October cooling changes was not measured.
- **The page's "How fast."** E73's "63% in 17 s and 95% in 49 s" is the camera on the back of the board. On the die's own sensors: 32% by 30 s, 45% by 60 s, 90% by 5 minutes. A reader should not carry the camera's times to the die.
- **Item 9, "the heat path drifts, no room or inlet reading".** Narrowed, post hoc: the die's two largest moves came with moves on host sensors, and one 3-minute CPU burst on another box coincided with +0.79 °C on this die, uniform across the sensors. The hosts' NIC and NVMe sensors are a free, coarse stand-in for an inlet reading, though not a calibrated one.
- **For the next hold.** A rest needs about 10 minutes on this card, and a steady reading needs the room quiet or read beside it. `run_e97b.py` and `room_e97.py` are the harness.

## Registered against what happened

| registered ([`E97.md`](../../../../tools/claims-v3/e97/E97.md), [`predictions-e97.json`](../../../../tools/claims-v3/e97/predictions-e97.json)) | happened |
|---|---|
| registration, predictions, code and desk checks on origin/main before the claim and any device access | `49de6d33` pushed 01:16:49 PST; claim 02:30:39; first device access 02:30:42 |
| files copied to the box, setup with no device access | 02:30:09–02:30:22: reused files and 32 tiles verified, `dry A rc=0`, `dry B rc=0` ([`logs/e97-dry.log`](logs/e97-dry.log), [`logs/e97-dry-b.log`](logs/e97-dry-b.log)) |
| the probe: are command 74's readings raw codes? | 02:30:42: three ticks, status 0, 34 values, 1,960–2,004 codes at a 53 °C reading ([`logs/probe.out`](logs/probe.out)) |
| the smokes: two blocks of 10 s halves; a 65 s Part B pass with a forced stop | 02:30:43–02:33:05, both `ok`; the forced stop moved H1 to its reduced phase ([`logs/probe-smoke-session.out`](logs/probe-smoke-session.out)) |
| passes 9710, 9711: 29 blocks each, about 69 minutes | 68 minutes each; the orders as frozen; all 58 blocks passed every gate ([`e97.json`](e97.json) `gates`); all 63 tiles the host dumped equal their registered sha256 |
| Part B by the frozen plan: R0, H1, then by the time left | R0 ended on its slope at 832 s (cap 1,800), starting idle 50.558 °C. H1 30 min. **98.9 minutes left: "chain"** (H2 15 min on H1, the ≥ 65 branch; ≥ 135 would have been a full hold). R1 ended on its level at its 600 s minimum. H3 30 min: stop at 221 s, then reduced for 26 minutes. R2 ended on its level + 5 min at 900 s. **The queue ended 06:44:13, 29 minutes before the deadline** (D2) |
| every rule scored on the 34-sensor mean | 107 PASS, 36 INCONCLUSIVE, 8 FAIL. Predicted and not: E97-B1 on H1 and H3 (FAIL, predicted PASS), E97-R6 (INCONCLUSIVE, predicted PASS); R2, R4, R5's INCONCLUSIVE cells were allowed for at n = 2 |
| nothing set; session `ettelem config` at both ends | 02:30:42 and 06:48:24, and each pass's own two: TDP 0, 65 °C, 600 MHz, 523 mV ([`logs/config-session-start.json`](logs/config-session-start.json), [`logs/config-session-end.json`](logs/config-session-end.json)) |

## Departures (dated)

- **D1 — a chained H2 (the frozen branch; registered).** The brief asked for each kind held 30 minutes after a rest. H2 ran 15 minutes straight on H1, so it has no arrival shares, and its idle before is H1's. It is the same-power comparison the plan chose when time looked short; it was not short (D2).
- **D2 — the plan's time estimate was wrong, in the cautious direction (stated Sun 1 Nov, after the data).** The thresholds assumed rests of 30–35 minutes, from the lab's slow stages and the whole-degree history; the fine reading took about 9. At the decision 98.9 minutes were left; with what we now know H2 could have had its own rest and 30 minutes, and the session would still have ended by 07:13. The rule was frozen and was followed; 29 minutes of the window went unused.
- **D3 — a run-control backstop added at the start of the queue, 02:33:37 (not a measurement).** The run's brief asked that the queue stop by the deadline whatever happens, needing no ssh. [`logs/watchdog_e97.sh`](logs/watchdog_e97.sh) opens no device and would have touched the STOP files at 07:14:00 and sent SIGTERM to the block at 07:15:20; it exited when the queue ended ([`logs/watchdog.log`](logs/watchdog.log)).
- **D4 — E89's lap is beside the pass, not the other way round (registered).** Stated because it decides how R2 reads: the brief makes the independent pass the unit; n = 2 leaves 22 of 28 R2 cells inconclusive. A verdict's sensitivity to the trend's order (E89 C5) is marked in [`results.md`](results.md): 8 of R2's and 10 of R5's move between PASS and INCONCLUSIVE under a linear or cubic trend; none reaches FAIL.
- **D5 — desk compute and copies (stated Sun 1 Nov).** The Intel's load guard paused agent work for most of the session's end, so the registered reduction ran on the mini (Python 3.12, numpy 1.26.4), on a verified copy of the tree, and the release and closing reads came late: the card was free from 06:44:13, read at 06:48:24, released at about 06:59. Passes 9710 and 9711 were copied once each as they finished, at nice 19 and 3 MB/s, during the next pass; a planned copy of 9720 during its rests did not run, because the watcher was paused. Nothing on the card depended on the Intel.
- **D6 — idle logins (E78's D1).** Other lab users kept idle logins on aifoundry3; none held the card, a device node or the lock (`et-who` empty at 02:29, 02:30, 02:33 and 06:48).

## How it ran

On the Intel: origin/main contained `49de6d33`; `rsync` of `tools/claims-v3/e97/` to `aifoundry3:aifoundry/tools/claims-v3/`. On aifoundry3, from `~/aifoundry`, each step in a script file run by `ssh aifoundry3 'bash -s' < file`:

```bash
bash tools/claims-v3/e97/run_e97.sh setup        # 02:30:09, no device access
# 02:30:39  the #community-lab claim (one line)
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null   # 02:30:42, read only
bash tools/claims-v3/e97/run_e97.sh probe        # 02:30:42
bash tools/claims-v3/e97/run_e97.sh smoke        # 02:30:43-02:33:05
bash tools/claims-v3/e97/run_e97.sh go           # 02:33:35, detached; queue done 06:44:13
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null   # 06:48:24, read only
```

Nothing was reduced before the queue ended. Then, over a copy of the raw passes: `PY=<python with numpy> bash tools/claims-v3/e97/collect_e97.sh <raw> <history>`, which runs `reduce_e97.py`, `score_e97.py` and `room_e97.py`; `posthoc_e97.py` from this directory.

## Joins and traps

- **A sum's baseline.** Against zeros, E89's straight baseline makes cycle 1's 2 s step larger than cycle 0's, 1.07–1.24 times on the float kinds, because a 30 s half's chain ends 0.9–1.7 s early and its baseline ends falling (E89 C6; [`tools/claims-v3/e97/desk/c6_e89.txt`](../../../../tools/claims-v3/e97/desk/c6_e89.txt)). A quadratic baseline over the last 20 s removes it on the floats (1.00 on average) and lowers their rise over zeros by about 4%; on int8 it overshoots (0.89). Against idle there is no such effect (0.99). So the sums carry about ±5% beyond their ±, the direct cells do not ([`posthoc.txt`](posthoc.txt) [cycle]; [`results.md`](results.md) § The 2 s step).
- **r mixes frames.** Against idle, a launch's whole cost is in the swing, and the minion rail carries more of it (0.85–0.91 of the board's swing against 0.86–0.89 against zeros, 0.81 on fp32 random). Compare r within a frame; the over-idle cells are comparable across frames.
- **"Steady" here is a plateau.** The rise is read over a hold's last 300 s, with a room that moved ±0.4 °C. A stage slower than about 10 minutes that adds under about 3% of the rise is not resolved.
- **The bounds are one hold's**, not intervals over replicates, and they omit the room's wander. Quote ±0.4 °C or the range 0.87–0.92 °C per board W.
- **The 34-sensor mean is not a calibrated die temperature:** one conversion for every sensor, and the firmware's reading runs about 1 °C below it (E89).
- **The stop is the firmware's reading between launches:** it read 78 °C at 216.5 s and the runner saw it at 221.3 s. The hold's reduced phase began 1.5 s later, because the fast stages drop 3 °C within a launch gap; the die was never held above the stop.
- **Command 74's raw codes are this card's thermal build's** (E89's trap), and every launch runs on all 32 shires, so the per-sensor pattern says nothing about a kind run on part of the die.
- **The derived int8 cells use E89's int8 zeros**, from another session; the session tie on fp32 random is the only link between the two.

## Files

| file | what |
|---|---|
| `README.md` | this file |
| [`results.md`](results.md), [`scored.json`](scored.json), [`e97.json`](e97.json) | `score_e97.py`: every block, both units, the trend arms, the heat column, Part B, the verdicts |
| [`reducer/`](reducer/) | E89's reducer, byte for byte, on E97's blocks: `e89.json`, E89's rules with the lap as the unit in `scored.json`, the merged denominators |
| [`posthoc_e97.py`](posthoc_e97.py), [`posthoc.txt`](posthoc.txt) | **post hoc and descriptive:** the wander, the bump, the room, the gaps, the peaks, the rests, the cycle effect |
| [`room.txt`](room.txt), [`room/`](room/) | the three boxes' live history over the session (time, CPU use, load, host sensors, cards' free readings; no users), and each span's slopes |
| [`manifest.json`](manifest.json) | every file's sha256, the registration commit, the claim |
| [`reduce.log`](reduce.log), [`score.log`](score.log), [`code.sha256`](code.sha256) | the reduction's output, the code's hashes |
| `logs/` | the queue log, the dry runs, the probe, the session reads, the backstop and its log, the binaries' hashes |
| `aifoundry3/e97/p9710`, `p9711`, `p9720`, `aifoundry3/e97-smoke-p9701`, `p9702` | raw: `telemetry.jsonl.gz` (10 Hz, with the 34 codes), `runs.jsonl`, `marks.jsonl`, `run.log`, `configs.json`, `config_start/end.json`, `block.json`, `sampler.json`, `manifest.txt`, `code.sha256`, `gen.sha256`, `tiles/` |
