# E147: every open single-bit position priced in both layouts; the swing plateaus at 6× on B, the exponent reverses on both sides, and M6 predicts the new positions to 0.21 W (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 15, "Smaller, and carried": its single-bit sentence's open list, "B bits 1–5, 17–19, 21, 24–26 and 28–29; A bits 8–10, 12–15, 17–19, 21, 24–26 and 28–29 on E102's word, and above bit 7 on any other" ([E134](../2026-11-02-e134-bit-prices-more/README.md), the run that left them, correction C2). E147 runs every listed position in both layouts, and four A positions above bit 7 on a second word. The sign on the rail and E102-R2's bit-22 cell were not run.*

*Mon 2 Nov 2026 (week 45), Q138, lane `a3-e147-bit-prices`, on the owner's words of that evening: "feel free to settle any unanswered questions regarding horace's power model", with that day's goal, to predict the power and heat of numeric computations as accurately as possible. Pre-registered in lab `c41c3905` (committed 20:12:58 PST, pushed by 20:13:02, before the reservation and the first launch): [`tools/claims-v3/e147/README.md`](../../../../tools/claims-v3/e147/README.md), with the frozen numbers in `predictions-e147.json`, the 73 tiles in `e147/`, the scorer and its self-test, and the fixed RTL bench's counts and M6's frozen predictions in [`bench/`](bench/). No amendment. aifoundry3 card 0 at 600 MHz, 521.9 mV mean. The card was read at 20:15:26 (TDP 0 W, 65 °C, max_power, 600 MHz, 523 mV) and at 20:56:59 (the same, 522 mV), under the card lock and `timeout 10`, at both ends of every block, the smoke and both stop tests too: 23 reads, all alike; nothing was ever set. **Every device command sent was a read** (§ Device commands sent): no write of any kind, no `--reset-ms`, no firmware-revisions query, no residency read.*

*The day's card post in `#community-lab` (message `1566837317765963987`) was rewritten at 20:14:50 PST from "using aifoundry1 card 1 for 1.5 h, until ~20:53 PST [doc] — released" to "using aifoundry3 for 1 h, until ~21:14 PST [doc]" (a first attempt at 20:14 was refused with exit 7: another lane had appended " — released" at 20:11; the post was re-read and the text rebuilt), and at 20:57:44 to drop that clause, keeping aifoundry1 card 1's and aifoundry2's clauses word for word (both still held, so no " — released"). Smoke 14701, 20:15:25–20:15:59; stop test 14702 and 14703, 20:16:08–20:16:29; queue 20:16:50–20:56:59, ending with the session-end read: **41.6 card-minutes** of the registered 45. Eight blocks (A 14710–14713, B 14720–14723), 468 runs, none failed a run gate, none set aside.*

**What ran.** fp32 trains (no heater, a 0.2 s gap, 4.83 s a run), every item between reads of its own zero, each bit's two layouts paired (E147 change 2):
- **A blocks:** W79 = `0x3fbd207c` (E79's, E102's, E134's word) at bits 8–10, 12–15, 17–19, 21, 24–26 and 28–29, and W67 = `0x3fbbc9e4` (E67's) at 9, 17, 18 and 19, both layouts.
- **B blocks:** E79's eight B words at bits 1–5, 17–19, 21, 24–26 and 28–29, both layouts, and E134's `bj_16` and `bp_16` as the session link.

A price is a step over the item's own zero (board `p_raw`, no temperature term, the meter's dips removed at the registered 2 W line), divided by its designed flips an op and the run's rate. Intervals are 95% over the four kept blocks of each kind (t = 3.18). All numbers are from [`scored.json`](scored.json) › `primary`, with the arms in `arms`; the tables are [`results.md`](results.md). The items' 95% half-widths run 0.013–0.218 W, median 0.049 W.

## Results

**In plain words.** One flipped bit costs what its place in the number says, and the lab's model mostly knows it:
- **On B, a low mantissa bit is the flip alone:** 90–102 fJ in both layouts at bits 1–5.
- **High on B, the two accumulators part:** at bits 17–21 the all-in layout costs 693–989 fJ a flip, the balanced one 110–164. The ratio sits at 6.05–6.66×, level with bit 16 (6.84 here, 6.03 in E134): a plateau.
- **The exponent turns it around on both sides:** at bits 24–29 the balanced layout costs 1.8–3.7× the all-in one (all-in / balanced 0.30–0.57 on B, 0.27–0.54 on A).
- **On A the word still matters above bit 7, in the Booth recoder's direction:** W79 is dearer at 9 and 17 by 0.21 and 0.28 W, and W67 at 18 by 0.80 W. Where both words make the same digit changes (bit 19) the difference is −0.16 [−0.36, +0.04] W, unresolved.

**M6, the lab's power model, frozen before the run and never fitted on a single bit, predicts the 68 new items to 0.210 W rms** (bias −0.089 W), inside its own claimed 0.245 W (M1 HOLDS). It does well on the mantissa (0.153 W rms over 48 items, bias −0.018). It over-prices the exponent: 0.307 W rms over 20 items, bias −0.259 W; the card pays 0.82 of M6's watts there. On E134's single bits, post hoc, it had read 0.098 W.

**1. B: the flip alone below bit 8, a 6× plateau at the top of the mantissa, and the exponent reversed** (E79's B words; the swing is all-in − balanced × 4096/3968, board W; in brackets each item's frozen M6 step):

| bit | all-in, fJ | balanced, fJ | ratio per flip | **swing, W** | M6 swing | bench swing | all-in W (M6) | balanced W (M6) |
|---:|---|---|---|---|---:|---:|---|---|
| 1 | 102 [96, 109] | 100 [93, 107] | 1.02 [0.97, 1.08] | **+0.010 [-0.014, +0.034]** | +0.000 | +0.000 | 0.469 [0.439, 0.500] (0.567) | 0.445 [0.415, 0.476] (0.549) |
| 2 | 92 [88, 96] | 90 [85, 96] | 1.02 [0.95, 1.08] | **+0.006 [-0.020, +0.032]** | +0.000 | -0.000 | 0.420 [0.402, 0.439] (0.446) | 0.401 [0.377, 0.425] (0.431) |
| 3 | 100 [80, 120] | 94 [84, 105] | 1.06 [0.89, 1.24] | **+0.028 [-0.046, +0.102]** | +0.000 | -0.000 | 0.460 [0.368, 0.552] (0.450) | 0.419 [0.372, 0.466] (0.436) |
| 4 | 95 [91, 98] | 99 [90, 107] | 0.96 [0.91, 1.02] | **-0.018 [-0.043, +0.007]** | +0.000 | -0.000 | 0.435 [0.419, 0.452] (0.448) | 0.439 [0.401, 0.477] (0.434) |
| 5 | 100 [90, 111] | 101 [95, 106] | 1.00 [0.89, 1.11] | **-0.001 [-0.053, +0.050]** | +0.000 | +0.000 | 0.461 [0.413, 0.508] (0.453) | 0.448 [0.424, 0.471] (0.438) |
| 17 | 693 [678, 709] | 114 [90, 138] | 6.06 [5.11, 7.52] | **+2.658 [+2.606, +2.711]** | +2.344 | +2.262 | 3.183 [3.112, 3.254] (2.951) | 0.508 [0.401, 0.615] (0.589) |
| 18 | 732 [706, 757] | 110 [86, 133] | 6.66 [5.66, 8.19] | **+2.854 [+2.814, +2.894]** | +2.626 | +2.531 | 3.358 [3.243, 3.474] (3.167) | 0.489 [0.385, 0.593] (0.524) |
| 19 | 807 [773, 842] | 128 [98, 158] | 6.30 [5.12, 8.21] | **+3.118 [+2.927, +3.310]** | +2.725 | +2.623 | 3.706 [3.548, 3.864] (3.407) | 0.569 [0.436, 0.703] (0.660) |
| 21 | 989 [957, 1021] | 164 [129, 198] | 6.05 [4.89, 7.81] | **+3.792 [+3.518, +4.066]** | +3.626 | +3.487 | 4.543 [4.395, 4.692] (4.428) | 0.728 [0.575, 0.880] (0.776) |
| 24 | 178 [153, 203] | 520 [471, 569] | 0.34 [0.31, 0.37] | **-1.570 [-1.715, -1.424]** | -1.767 | -2.026 | 0.817 [0.704, 0.930] (0.903) | 2.312 [2.094, 2.531] (2.586) |
| 25 | 153 [133, 173] | 518 [501, 535] | 0.30 [0.26, 0.34] | **-1.675 [-1.803, -1.546]** | -1.941 | -2.183 | 0.704 [0.613, 0.795] (0.755) | 2.304 [2.228, 2.381] (2.612) |
| 26 | 195 [184, 207] | 475 [467, 482] | 0.41 [0.38, 0.44] | **-1.282 [-1.370, -1.194]** | -1.651 | -1.924 | 0.897 [0.844, 0.950] (1.015) | 2.110 [2.076, 2.144] (2.583) |
| 28 | 232 [223, 241] | 447 [434, 460] | 0.52 [0.49, 0.55] | **-0.990 [-1.085, -0.895]** | -1.132 | -1.430 | 1.064 [1.021, 1.107] (1.515) | 1.990 [1.933, 2.047] (2.564) |
| 29 | 244 [235, 253] | 429 [421, 438] | 0.57 [0.54, 0.60] | **-0.850 [-0.918, -0.781]** | -0.937 | -1.242 | 1.120 [1.077, 1.163] (1.571) | 1.909 [1.870, 1.948] (2.429) |
| 16 (E134 link) | 599 [571, 627] | 88 [67, 109] | 6.84 [5.27, 9.40] | **+2.349 [+2.126, +2.573]** | +2.026 | +1.951 | 2.752 [2.621, 2.882] (2.603) | 0.390 [0.296, 0.483] (0.559) |


- **E147-R1, B's low bits: FLAT** (registered). The mean swing over bits 1–5 is +0.005 [−0.017, +0.027] W, inside ±0.10 W, and no bit's lower bound reaches 0.10 W (the widest, bit 3, +0.028 [−0.046, +0.102]). With E134-R4 (none at 6 and 7, +0.149 W at 8) the swing is absent at every B bit below 8, as the frozen real-sum counts say (0 result-path bits an op over the zero at bits 1–5).
- **E147-R2, B's exponent: INVERTED** (registered): all-in / balanced 0.34, 0.30, 0.41, 0.52, 0.57 at bits 24, 25, 26, 28, 29, every upper bound below 1 (the highest 0.60). E102 read 0.42, 0.30 and 0.46 at 23, 27 and 30 on aifoundry1 card 1.
- **At the top of the mantissa the ratio stops climbing:** 6.06, 6.66, 6.30, 6.05 at bits 17, 18, 19, 21, and 6.84 at 16 here (E134 6.03; E102 5.31 at 20, 6.17 at 22, card 1). The balanced price stays flat: 90–101 fJ at 1–5 and 110–164 fJ at 17–21 (E134: 83–113 at 6–16).
- **The card's swing at the top is 9–19% above the bench's and 5–14% above M6's:** measured over bench 1.18, 1.13, 1.19, 1.09 at 17, 18, 19, 21 (E134 read 1.07–1.26 at 8–16); over M6 1.13, 1.09, 1.14, 1.05.
- **E147-S1, the session link: PASS** (registered). E134's `bj_16` reads 2.752 W against E134's 2.789, and `bp_16` 0.390 against 0.448 (bands ±0.697 and ±0.150 W). E65's B all-in list, from another protocol with a fresh word at each bit, predicts the 14 new all-in items to 0.154 W rms, the best of the four frozen models there (`models.B_allin`).

**2. A on W79: no swing at bits 8 and 9, a rising and uneven one from bit 10, and the exponent reversed** (all-in − balanced × 2048/1920, board W):

| bit | all-in, fJ | balanced, fJ | ratio per flip | swing, W | M6 swing | all-in W (M6) | balanced W (M6) |
|---:|---|---|---|---|---:|---|---|
| 8 | 115 [98, 133] | 108 [97, 120] | 1.06 [0.86, 1.30] | +0.016 [-0.037, +0.069] | -0.001 | 0.265 [0.225, 0.305] (0.270) | 0.233 [0.209, 0.258] (0.254) |
| 9 | 352 [319, 386] | 355 [342, 368] | 0.99 [0.91, 1.07] | -0.005 [-0.069, +0.059] | -0.001 | 0.809 [0.733, 0.885] (0.789) | 0.763 [0.735, 0.791] (0.740) |
| 10 | 248 [235, 261] | 114 [99, 129] | 2.18 [1.95, 2.46] | +0.309 [+0.277, +0.340] | +0.280 | 0.570 [0.540, 0.601] (0.555) | 0.246 [0.213, 0.279] (0.258) |
| 12 | 349 [338, 359] | 173 [134, 211] | 2.02 [1.66, 2.59] | +0.405 [+0.317, +0.492] | +0.330 | 0.801 [0.777, 0.825] (0.641) | 0.371 [0.288, 0.454] (0.291) |
| 13 | 666 [630, 702] | 378 [356, 400] | 1.76 [1.70, 1.83] | +0.661 [+0.606, +0.716] | +0.568 | 1.530 [1.446, 1.613] (1.730) | 0.814 [0.767, 0.861] (1.089) |
| 14 | 501 [473, 529] | 147 [122, 173] | 3.40 [2.94, 4.02] | +0.811 [+0.746, +0.875] | +0.525 | 1.149 [1.085, 1.213] (0.858) | 0.317 [0.263, 0.372] (0.312) |
| 15 | 756 [712, 800] | 350 [320, 381] | 2.16 [2.06, 2.27] | +0.931 [+0.873, +0.988] | +0.789 | 1.735 [1.633, 1.837] (1.646) | 0.754 [0.687, 0.821] (0.803) |
| 17 | 785 [765, 805] | 325 [314, 337] | 2.41 [2.35, 2.49] | +1.056 [+1.017, +1.094] | +0.992 | 1.803 [1.756, 1.849] (1.835) | 0.700 [0.675, 0.725] (0.790) |
| 18 | 797 [775, 820] | 144 [118, 170] | 5.55 [4.77, 6.67] | +1.500 [+1.452, +1.549] | +1.470 | 1.830 [1.780, 1.881] (1.753) | 0.309 [0.253, 0.365] (0.266) |
| 19 | 1097 [1050, 1144] | 342 [332, 351] | 3.21 [3.01, 3.42] | +1.734 [+1.611, +1.858] | +2.163 | 2.519 [2.411, 2.626] (2.987) | 0.735 [0.715, 0.755] (0.773) |
| 21 | 1017 [961, 1073] | 217 [183, 250] | 4.69 [3.92, 5.74] | +1.838 [+1.657, +2.020] | +2.207 | 2.336 [2.208, 2.464] (2.587) | 0.467 [0.395, 0.538] (0.356) |
| 24 | 193 [181, 206] | 518 [496, 540] | 0.37 [0.34, 0.41] | -0.745 [-0.817, -0.672] | -0.752 | 0.444 [0.416, 0.472] (0.522) | 1.114 [1.068, 1.161] (1.194) |
| 25 | 168 [157, 179] | 624 [611, 637] | 0.27 [0.26, 0.28] | -1.046 [-1.069, -1.023] | -1.222 | 0.386 [0.361, 0.411] (0.403) | 1.343 [1.315, 1.371] (1.523) |
| 26 | 213 [207, 218] | 590 [568, 611] | 0.36 [0.34, 0.38] | -0.865 [-0.916, -0.814] | -1.110 | 0.488 [0.475, 0.501] (0.582) | 1.268 [1.223, 1.314] (1.586) |
| 28 | 249 [233, 265] | 511 [487, 534] | 0.49 [0.47, 0.50] | -0.600 [-0.626, -0.574] | -0.653 | 0.572 [0.536, 0.608] (0.833) | 1.099 [1.048, 1.149] (1.393) |
| 29 | 266 [238, 293] | 489 [476, 502] | 0.54 [0.49, 0.60] | -0.513 [-0.577, -0.449] | -0.534 | 0.610 [0.547, 0.672] (0.880) | 1.052 [1.025, 1.079] (1.325) |

- **E147-R3, A's exponent: INVERTED** (registered): 0.37, 0.27, 0.36, 0.49, 0.54 at bits 24, 25, 26, 28, 29 (E102, card 1: 0.52, 0.31, 0.39 at 23, 27, 30).
- **The A side's swing starts at bit 10, post hoc, no verdict.** At 8 and 9 the two layouts cost the same (1.06 [0.86, 1.30] and 0.99 [0.91, 1.07]). From 10 the all-in layout is dearer, by +0.309 W at 10 and +1.838 W at 21. The frozen real-sum counts give 0 result-path bits an op at 8, 1,024 at 9 and 7,360 at 10 (all-in over balanced), so on A the swing shows at the first bit where they pass a few thousand, as on B (4,551 at bit 8). M6 put the swing at −0.001, −0.001 and +0.280 W at 8, 9 and 10.
- **A's ratio is uneven, as E102 found on card 1** (7.1 at 16, 3.2 at 20, 2.2 at 22). Here it runs 2.18, 2.02, 1.76, 3.40, 2.16, 2.41, 5.55, 3.21, 4.69 from bit 10 to 21. The balanced A price follows the Booth digit, post hoc: on W79 it is 108–217 fJ where the flip keeps every digit on its side (8, 10, 12, 14, 18, 21) and 325–378 fJ where it moves one across zero (9, 13, 15, 17, 19); on W67, 145–147 fJ at 9 and 17 (same side) against 316 and 611 fJ at 19 and 18 (across). A reading, § Interpretation.

**3. The word above bit 7** (W67 − W79, board W, paired by block; the digit classes are each word's at that bit, from the words alone, before any count):

| bit | classes W67 / W79 | **W67 − W79, all-in, W** | bench | M6 | reading | W67 − W79, balanced, W | bench | W67 all-in, fJ | W79 all-in, fJ | W67 ratio per flip |
|---:|---|---|---:|---:|---|---|---:|---|---|---|
| 9 | same / cross | **-0.210 [-0.297, -0.124]** | -0.436 | -0.310 | W79 dearer | -0.446 [-0.508, -0.384] | -0.612 | 261 [250, 272] | 352 [319, 386] | 1.77 [1.56, 2.06] |
| 17 | same / cross | **-0.278 [-0.320, -0.236]** | -0.364 | -0.234 | W79 dearer | -0.389 [-0.424, -0.353] | -0.607 | 664 [657, 670] | 785 [765, 805] | 4.59 [4.21, 5.06] |
| 18 | cross / same | **+0.801 [+0.717, +0.885]** | +1.145 | +0.824 | W67 dearer | +1.005 [+0.852, +1.157] | +1.600 | 1146 [1123, 1169] | 797 [775, 820] | 1.88 [1.77, 2.00] |
| 19 | cross / cross | **-0.163 [-0.364, +0.038]** | -0.178 | -0.192 | the same | -0.055 [-0.217, +0.107] | +0.072 | 1026 [971, 1081] | 1097 [1050, 1144] | 3.25 [2.63, 4.29] |

- **E147-R4, the bench's word differences above bit 7: AGREES** (registered). At bits 9, 17 and 18 the difference resolves with the bench's sign, at 0.48, 0.76 and 0.70 of its size (E134: 0.65–0.71 at bits 4–6); bit 19 does not resolve. M6 put them at 0.68, 1.19 and 0.97 of what the card read.
- **E147-R5, E134's digit-class reading: INCONCLUSIVE** (registered, and expected). The three signed bits have the reading's signs and all resolve; but at bit 19, where both words make the same two digit changes, the difference is −0.163 [−0.364, +0.038] W: neither inside the ±0.10 W band nor wholly outside it. The bench said −0.178 W there and M6 −0.192. On the rail arm R5 reads HOLDS, so it is arm-sensitive.
- E67's four tiles above bit 7, reported: 0.599, 1.524, 2.631 and 2.356 W at 9, 17, 18, 19 against E67's 0.754, 1.504, 2.481 and 2.669 W on this card, all inside E134-S1's bands.

**4. M6 at the new positions: E147-M1 HOLDS** (registered; board W over each list; measured − model):

| list | n | M6 rms (bias) | M5 rms (bias) | bench rms (bias) | position-only rms (bias) |
|---|---:|---|---|---|---|
| new_items | 68 | 0.210 (-0.089) | 0.214 (-0.106) | 0.226 (-0.085) | 0.993 (-0.300) |
| A_W79_allin | 16 | 0.194 (-0.064) | 0.216 (-0.095) | 0.192 (-0.055) | 0.329 (-0.221) |
| A_W79_balanced | 16 | 0.160 (-0.086) | 0.151 (-0.084) | 0.199 (-0.143) | 1.086 (-0.529) |
| A_W67 | 8 | 0.203 (-0.086) | 0.235 (-0.122) | 0.311 (-0.200) | 0.855 (-0.578) |
| B_allin | 14 | 0.213 (-0.031) | 0.200 (-0.072) | 0.184 (+0.102) | 0.154 (+0.076) |
| B_balanced | 14 | 0.271 (-0.182) | 0.268 (-0.167) | 0.267 (-0.177) | 1.697 (-0.347) |
| mantissa_new | 48 | 0.153 (-0.018) | 0.161 (-0.042) | 0.211 (-0.059) | 1.084 (-0.608) |
| exponent_new | 20 | 0.307 (-0.259) | 0.307 (-0.259) | 0.258 (-0.150) | 0.732 (+0.438) |
| B_link | 2 | 0.159 (-0.011) | 0.113 (-0.039) | 0.197 (+0.022) | 1.638 (-1.179) |

- **The rule:** M6's rms over the 68 new items is 0.210 W against its own nested 0.245 W for fp32 on aifoundry3. 66 of 68 lie inside its one-row band (±0.480 W). Its largest misses are all over-predictions: `bp_28` −0.574, `bp_29` −0.521, `bp_26` −0.472, `aj_19` −0.469, `bj_28` −0.451, `bj_29` −0.450, `a67j_19` −0.440, `ap_26` −0.318 W.
- **Per flip:** M6's price is off by 72 fJ rms (bias −30 fJ), a median 11% of the measured price. By list: B all-in 46 fJ rms, B balanced 61, A all-in on W79 85, A balanced on W79 74, W67 90.
- **Mantissa against exponent:** on the 48 mantissa items M6 reads 0.153 W rms (bias −0.018), level with E134's single bits post hoc (0.098 W over 54). On the 20 exponent items it reads 0.307 W (bias −0.259): the card's exponent steps are 0.82 of M6's. M5 is the same there (0.307), and the bench is closer (0.258, bias −0.150).
- **Against the other frozen models**, over all 68: M5 0.214 W, the bench at E92's coefficients 0.226 W, the position-only lists 0.993 W. M6, M5 and the bench are within 0.016 W of each other; what they share is the exponent's over-pricing.

## Registered against happened

| rule | primary | rail | board_p80 | dips_4w | dips_kept | gates_off |
|---|---|---|---|---|---|---|
| E147-R1 | **FLAT** | FLAT | FLAT | FLAT | INCONCLUSIVE | FLAT |
| E147-R2 | **INVERTED** | INVERTED | INVERTED | INVERTED | INVERTED | INVERTED |
| E147-R3 | **INVERTED** | INVERTED | INVERTED | NOT SCORED | NOT SCORED | INVERTED |
| E147-R4 | **AGREES** | AGREES | AGREES | NOT SCORED | NOT SCORED | AGREES |
| E147-R5 | **INCONCLUSIVE** | HOLDS | INCONCLUSIVE | NOT SCORED | NOT SCORED | INCONCLUSIVE |
| E147-M1 | **HOLDS** | FAILS | HOLDS | NOT SCORED | NOT SCORED | HOLDS |
| E147-S1 | **PASS** | FAIL | PASS | PASS | PASS | PASS |

**Expected, frozen: R1 FLAT, R2 INVERTED, R3 INVERTED, R4 AGREES, R5 INCONCLUSIVE, M1 HOLDS, S1 PASS. All seven came out as expected.** Every verdict on the primary holds on the p80 arm and with the gates off. The arms that move a verdict:
- **E134's own 4 W dip line** (the frame arm): the train gate sets aside A blocks 14710 and 14711, whose `aq` zero reads fall −0.287 and −0.294 W off their lines (2–4 W meter dips under that line, E134's correction C1's mechanism). With two A blocks left, R3, R4, R5 and M1 are NOT SCORED. At the registered 2 W line (E147 change 1) all eight blocks pass: 179 dip samples removed against 143 at 4 W, of 23,735.
- **Dips kept:** the gate sets aside all four A blocks and one B block. R1 reads INCONCLUSIVE; the A rules are NOT SCORED.
- **The rail** reads about 0.8 of the board. S1 compares it with E134's board watts and fails, and M1 compares it with M6's board watts and fails (the expected failure of a scale, not a test). R5 reads HOLDS there: bit 19's difference is narrower on the rail.

## What it does to predicting power and heat

- **The term measured:** the price of one flipped bit at every fp32 position item 15 left open, by side, layout and word. With E134's and E102's positions, every fp32 position now has both layouts on at least one card. This is the per-position table a next model reads: [`scored.json`](scored.json) › `primary.prices` (W and fJ per flip, with intervals) and `statistics` (ratios and swings).
- **The term tested, blind:** M6's per-flip prediction at the new positions. Out of sample, M6 claimed 0.245 W rms for fp32 tiles on this card (nested leave-one-kind-out), and post hoc it read E134's single bits to 0.098 W. At E147's 68 new positions it reads **0.210 W** (M1 HOLDS). The error is not spread evenly: 0.153 W on the mantissa and **0.307 W on the exponent**, where every model frozen here over-prices the steps (M6 by 0.26 W, 18%).
- **The correction it points to (a reading, not refitted here):** M6's exponent-field terms (`a_exp` 3.2 ± 8.8 fJ, `b_exp` −1.3 ± 4.5 fJ per flip, both unresolved) and its bench counts give the exponent flips about 1.2× their measured cost. A refit that weighs E147's 20 exponent items would take that bias out; how much of the 0.307 W it removes out of sample is for the next model's nested score, not this one. The B swing at the top of the mantissa runs 5–14% above M6's.
- **Heat:** nothing measured here. The steps are at most 4.5 W in 4.8 s trains, and the die read 51–64 °C over the session; E147 makes no heat claim. The power term these prices feed is the one M6's heat term multiplies (0.118 °C per board W over a 4.5 s run, Q137(m)).

## What it changes

- **Item 15's single-bit sentence.** Its open list is answered at every listed position on aifoundry3, in both layouts, and above bit 7 on a second word at four positions. Proposed replacement, a reading for the integration lane: *"Single-bit prices, every fp32 position in both layouts on at least one card (E102, E134, E147): on B a low mantissa bit costs the flip alone (90–152 fJ in both layouts at bits 0–7); from bit 8, where the two accumulators first part, the all-in price grows to a plateau of about 6× the balanced one at bits 16–22. At the exponent the order reverses on both sides: the balanced layout costs 1.8–3.7× the all-in one. On A the flip alone is the price at bits 0–9; above, the all-in layout is 1.5–7× dearer, unevenly (E102, E147), and the price depends on the base word, in the Booth recoder's direction, below bit 8 and at 9, 17 and 18 (E134, E147; one card, two words). M6, frozen, predicts single bits at positions never fitted to 0.21 W rms, the exponent's 0.31 W the largest part (E147). Open: other words, the sign on the rail, and E102-R2's bit-22 cell on a second card."*
- **The kinds page's single-bit price lists** gain both layouts at the 30 positions (B and A on W79) and four on W67. The B-side all-in list carries over between protocols (E65's list predicts the new all-in items to 0.154 W). The A-side numbers need their word attached, above bit 7 as below.
- **Item 6 (a model for every kind):** M6's error on single bits doubles from E134's positions (bits 0–16, post hoc) to E147's (0.098 → 0.210 W), and the exponent is where. The bench, frozen, also falls short of the B swing at the top by about 15% (1.09–1.19 here, 1.07–1.26 in E134) and over-states the A word effect (the card reads 0.48–0.76 of it).

## Interpretation (labelled: a reading, not measured)

- **The B plateau.** In the all-in layout the two accumulators a lane alternates between receive products that differ in bit j of B. From bit 8 the difference survives rounding and the sums part (E134). By bit 16 it is a large part of every addition, so the parted bits stop growing much faster than the flipped bits do, and the ratio settles (real-sum result bits an op, all-in over balanced: 64,954 at 16, 67,973 at 17, 91,758 at 21, against 4,551 at 8 and 21,947 at 11).
- **The exponent's reversal.** With the products and their sums moving together (all-in), the aligned operand does not change and an exponent flip is cheap. In the balanced layout the product alternates against a sum that does not, so the aligner shifts every micro-op: the frozen counts give 139,000–181,000 flop-bit changes an op on B's balanced exponent items and 0 on the all-in ones. That is E102's reading, now at every exponent bit run.
- **The A balanced price follows the digit.** A is Booth-recoded, so a balanced A flip still changes one or two radix-4 digits of every partial product. The dear balanced positions (9, 13, 15, 17, 19 on W79; 18 and 19 on W67) are where a digit crosses zero; the cheap ones (8, 10, 12, 14, 18, 21 on W79; 9 and 17 on W67) are where every digit stays on its side, and the two sets do not overlap (108–217 against 316–611 fJ). E134 read the same in the all-in layout at bits 0–7; above bit 9 the all-in layout adds the swing on top.
- **Bit 19.** The two words make the same two digit changes there (d9 −1 → +1, d10 0 → −1), and the bench still puts them 0.18 W apart. The card reads −0.16 [−0.36, +0.04] W. A difference there would have to come from the rest of the product: the digits the flip does not change, and the carries they feed. Neither this run nor the bench separates that.


## Device commands sent

*His rule of Mon 2 Nov 2026: every device-management command the run's harness, sampler, host program and helpers sent,
classified from the firmware source (et-platform `836a4ab`, BL2 0.22.0; paths under
`device-bootloaders/src/ServiceProcessorBL2/`), as [the registration](../../../../tools/claims-v3/e147/README.md#device-commands-sent)
listed them before the first launch. Every one sent was a READ.*

| # | command | sent by, in this session | firmware path at `836a4ab` | class |
|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config`: 23 reads (two for each block, the smoke and each stop test, and the session-end read) | `services/thermal_pwr_mgmt.c:613` (copies SP RAM) | READ |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | the same reads | `thermal_pwr_mgmt.c:665` (copies SP RAM) | READ |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | the same reads | `thermal_pwr_mgmt.c:551` (copies SP RAM) | READ |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` (10 Hz, eleven sampler runs: one per block, the smoke and each stop test) | `services/perf_mgmt.c:276` → `driver/io_pll.c:932` (PLL register reads) | READ |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | `thermal_pwr_mgmt.c:1142` → `driver/pmic_controller.c:1473`, `:254` `i2c_read` (two PMIC voltage-register reads) | READ, a PMIC voltage read, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample` (lib.sh's `drain_mgmt` , which sends it after a sampler fails to start twice, was not needed: every sampler started) | `thermal_pwr_mgmt.c:984` (copies SP RAM) | READ |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` → `thermal_pwr_mgmt.c:2780` (copies SP RAM, resets nothing) | READ |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; lib.sh `die_c` at each block's start and end | `thermal_pwr_mgmt.c:732` (PVT reads, cached in SP RAM) | READ |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` | `thermal_pwr_mgmt.c:1010` → `pmic_controller.c:1473` (nine PMIC voltage-register reads) | READ, PMIC voltage reads, allowed by his rule of 2 Nov |

**Not sent:**
- `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset: there is no `--reset-ms` anywhere, and `block_e147.sh:120`, the one
  `start_sampler` call, passes the output file and the duration only (all 24,217 committed telemetry samples, the smoke's and the stop tests' included, read `since_reset_ms` −1);
- `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`; `DM_CMD_SET_DM_TRACE_CONFIG`;
- any residency read;
- any `DM_CMD_SET_*`, or any governor, TDP, threshold or clock set;
- any reset, power cycle, PCIe, driver, firmware or OTA operation.

The host program, `sparsity_host`, opened the ops node only (`workloads/sparsity/host/main.cpp:172`,
`createPcieDeviceLayer(true, false)`): no management command. `et-who` / `et-holders`, `et-lab-manifest`, `flock`, `timeout`
and `ps` open no device node. The binaries were the registered ones (`sparsity_host` `20e760c2…`, `ettelem` `16037641…`,
[`logs/binaries.sha256`](logs/binaries.sha256)); the `ettelem` binary is built from lab commit `de262730`'s source, whose
`config()`, `sample()`, `Dm::get()` and `Dm::resetStats()` are byte-identical to the reviewed source's (E134's correction
C6). The preflight checker's three runs are in [`dmcmd-audit.txt`](../../../../tools/claims-v3/e147/dmcmd-audit.txt)
(Q136(w)'s `dmcmd_audit.py`, unchanged since `32e9c109`): NO-GO with no exception, which is the conditional at `lib.sh:154`
alone; GO with the reviewed exception for `block_e147.sh:120`; and NO-GO under `--deny-pmic-read` on the voltage reads alone.
aifoundry3 runs a thermal firmware build that is not public, so each READ's class rests on `836a4ab`'s handlers (E130 A1's
caveat). The registered condition held: the session-start read and the smoke's telemetry came back in the form E134's run
recorded (the same fields; TDP 0 W, 65 °C, 600 MHz).

## Card conduct

| | |
|---|---|
| before | `et-who` at 18:57:58, 19:24:21, 20:13:19, 20:15:06 and 20:16:50: no process held an ET-SoC-1 device node or card lock. Other lab users' idle logins were present and did not block (E60's D1). The registration was on origin/main before the claim. |
| reservation | the day's post `1566837317765963987`, rewritten under `EXPECT_TEXT` and the Discord lock: a first dry run refused with exit 7 (the post had changed at 20:11), re-read, rebuilt, dry run, `--save` at 20:14:50 PST, read back (aifoundry1 card 1's released clause erased, aifoundry3's added) |
| session | the smoke's config read 20:15:26 to the session-end read 20:56:59: 41.6 card-minutes. A blocks 345–346 s, B blocks 253 s, as estimated (the budget's projection, A 360 and B 265 s, held throughout) |
| stops | the board stop's first line in every block and the smoke was 0.08 s old (`runner.err`); the stop test fired both stops on live samples before any launch: board 23.77 W ≥ 1.0 W and die 51.0 °C ≥ 20 °C, exit 6, no run, no record (`aifoundry3/kinds/kinds-stoptest-p1470[23]/stoptest.json`) |
| readings | board at most 43.67 W (stop 65 W), die 51–64 °C (stop 70 °C); 600 MHz in every sample; cycles per op 546.001; 179 meter-dip samples removed at the 2 W line over eight blocks |
| end | the session-end read: TDP 0 W, 65 °C, max_power, 600 MHz, 522 mV; `et-who` clean at 20:56:59; nothing left running |
| release | the post rewritten at 20:57:44 to drop this card's clause, aifoundry1 card 1's and aifoundry2's kept word for word (both still held, so no " — released"); read back at 20:57 |

## Departures and disclosures

1. **Two registered changes to E134's frame**, both in the registration before any data: the meter-dip line at 2 W instead of E82 A2's 4 W (E134's correction C1), and each bit's two layouts paired in the block order (the self-test, before any data, found E134's random pairs could not decide R1 once the B block holds 3–4.5 W steps). E134's own 4 W line is reported as the frame arm: under it, two A blocks are set aside and the A rules are NOT SCORED (§ Registered against happened).
2. **R1's and R5's lines were set after the self-test and the frozen predictions were computed, and before the commit and any card run.** R1 first required all five low-bit intervals inside ±0.10 W, which the self-test showed almost never decides at four blocks, so it reads their mean, with each bit guarding SWING. R5's band at bit 19 was ±0.15 W and became E134-R2's ±0.10 W SAME band; its expectation became INCONCLUSIVE once the bench's −0.18 W at bit 19 was known. Both changes are in the one registered commit; no data existed then.
3. **The collection ran once, over a verbatim copy of the box's raw directories in the lab tree's ignored `build/e147-raw/`**, so `runs.csv`'s `dir` column reads `build/e147-raw/kinds/p147<nn>`. The same blocks are committed here under `aifoundry3/kinds/`.
4. **No interim look at power during the queue:** the waits read the queue log's block ends only.
5. **Post hoc, labelled, no verdict:**
   - the measured-over-bench and measured-over-M6 factors (the B swing, the word differences);
   - the A swing's onset at bit 10 against the real-sum counts;
   - M6's split into mantissa and exponent items, and its per-flip errors;
   - the digit reading of the balanced A price, and § Interpretation;
   - E147's own carry-over, 2.3 ± 0.2% per W of the preceding step (`carry_e134.py` run on this table; its printed label says E134), against E134's 2.8 ± 0.8%;
   - the proposed sentence for item 15.

## Caveats

One card, one clock (600 MHz, 522 mV), one session, four kept blocks of each kind. On A, two base words, W67 at four positions; on B, one set of E79's eight words. The bench is the open RTL's, priced with E92's coefficients fitted on E78's kinds on this card; its counts were not read back on silicon. M6 predicts D on the kinds harness's footing (launch at a fixed die reading); a train's step is the board's raw watts, and the p80 arm (E78's temperature term at 0.0518 W/°C) gives every verdict the same. The trains have no temperature term: at E147's largest steps (about 4.5 W) the next read inherits about 2.3% of a step (post hoc), which the twin pairs and the zero reads absorb in part. The sign on the rail (E102-R4) and E102-R2's bit-22 cell were not run; nothing here measures heat.

## Files

- `README.md` (this).
- The primary reduction: `e147.json`, `runs.csv`, `reduce.txt`, `reduce.log`.
- The registered arms: `e147-dips4.*` (E134's 4 W line), `e147-dipskept.*`, `e147-gatesoff.*`, `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`.
- Every rule, price, ratio, swing, contrast and model, every arm: `scored.json`, `results.md`, `score.log`.
- `code.sha256`.
- `logs/`: the queue log, both dry runs, the session's two config reads and their times, the binaries' sha256.
- `aifoundry3/kinds/p147*`: the eight raw blocks (telemetry, marks, records, tile dumps, config reads, manifests, code hashes, `runner.err`), plus the smoke as `kinds-smoke-p14701` and the stop tests as `kinds-stoptest-p14702` and `-p14703`.
- `bench/`: `counts-e147.json` and `bench-e147.log`, the fixed RTL bench's counts of the 70 tiles it ran (0 mismatches), and `m6-e147.json`, M6's and M5's frozen steps, all frozen with the registration; `m6-e134-posthoc.json` and `.txt`, M6 on E134's items (post hoc, the "before").
- The tiles, registration and code: [`tools/claims-v3/e147/`](../../../../tools/claims-v3/e147/README.md).
