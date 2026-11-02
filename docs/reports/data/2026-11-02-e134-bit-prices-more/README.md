# E134: one A bit's price is its base word's; B's accumulator swing starts at bit 8 (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 15, "Smaller, and carried": its single-bit sentence, "the other positions, other base words, A's low bits (R2) and the sign on the rail (R4) stay undecided" ([E102](../2026-11-01-e102-balanced-bit-prices/README.md)). E134 answers the first three in part. The sign on the rail was not run.*

*Mon 2 Nov 2026 (week 45), Q136, lane `a3-e134-bit-prices`, critic 12 of Q134's final critic. Pre-registered in lab `af56740a` (committed 11:48:32 PST, pushed by 11:48:39, before the reservation and the first launch): [`tools/claims-v3/e134/README.md`](../../../../tools/claims-v3/e134/README.md), with the frozen numbers in `predictions-e134.json`, the 57 tiles in `e134/`, the scorer and its self-test, and the RTL bench's frozen counts in [`bench/`](bench/). No amendment. aifoundry3 card 0 at 600 MHz, 522.0 mV mean. The card was read at 11:50:46 (TDP 0 W, 65 °C, max_power, 600 MHz, 523 mV) and at 12:29:19 (the same, 522 mV), under the card lock and `timeout 10`, at both ends of every block too; nothing was ever set. **Every device command sent was a read** (§ Device commands sent): no write of any kind, no `--reset-ms`, no firmware-revisions query, no residency read.*

*The day's card post in `#community-lab` (message `1566837317765963987`) was rewritten at 11:49:28 PST to add "using aifoundry3 for 1 h, until ~12:50 PST" and at 12:29:58 to drop it, keeping aifoundry2's clause word for word. Smoke 13401, 11:50:46–11:51:20. Queue 11:51:33–12:29:19, ending with the session-end read: **38.6 card-minutes** of the registered 40. Nine blocks (A 13410–13413, B 13420–13424), 435 runs, none failed a run gate. The budget rule stopped before the fifth A block, as projected.*

**What ran.** fp32 trains (no heater, a 0.2 s gap, 4.86 s a run), every item between reads of its own zero:
- **A blocks:** the A side on two base words, bits 0–7, both layouts. W79 = `0x3fbd207c` is E79's and E102's word; W67 = `0x3fbbc9e4` is E67's, and its all-in tiles are E67's own dumped files.
- **B blocks:** B bits 6–16, both layouts, with bits 7 and 8 read twice.

**The registered train gate set aside the first A block**, 13410: its `aq` zero read −0.306 and +0.300 W off its line. So the A rules rest on **three kept A blocks (13411–13413), the registered minimum** (t = 4.30); the B rules rest on five. A price is a step over the item's own zero (board `p_raw`, no temperature term, dips removed), divided by its designed flips an op and the run's rate. Intervals are 95% over blocks. All numbers are from [`scored.json`](scored.json) › `primary`, with the arms in `arms`. The tables are [`results.md`](results.md).

## Results

**In plain words.** On one card, in one train, the same A bit costs very different amounts on two base words:
- bit 5: 315 fJ a flip on E67's word against 105 fJ on E79's, 3.0×;
- bit 6: 284 against 131 fJ, 2.2×;
- bit 4: the other way, 120 against 262 fJ.

At bits 0–3 and 7 the two words read within 0.13 W of each other. The differences are the same in the balanced layout, and on both words, at all eight low bits, an all-in flip costs what a balanced one does (ratios 0.90–1.21). So the word acts on the flip itself, through the multiplier, and not through the accumulators. It is where the fixed RTL bench, with its structural Booth recoder on A, said it would be, and in its direction, at about 0.65–0.71 of its size. Where a flip moves a radix-4 digit between zero-or-positive and negative (a negated, sign-extended partial-product row of B = 1.0), it is dear; where it moves the digit among 0, +1 and +2, it is cheap (a reading, below). **E67's and E102's A lists were each their own word's.** On B, E79's words, the accumulators' swing is nothing at bits 6 and 7 and starts at bit 8, exactly where the real accumulators' frozen counts say the two all-in sums first part. It then grows with the counted bits. The all-in/balanced ratio runs 1.06, 1.00, 1.32, 1.88, 2.23, 3.09 … 6.03 from bit 6 to bit 16; E102 on card 1 read 1.05, 3.20 and 5.78 at bits 6, 11 and 16.

**1. The word sets an A bit's price** (all-in, board W over the own zero; the bench's frozen prediction in brackets):

| bit | W79 `aj`, W | W67 `a67j`, W | **W67 − W79, W** | bench | W67 − W79, balanced, W | W79, fJ a flip | W67, fJ a flip |
|---:|---|---|---|---:|---|---|---|
| 0 | 0.374 (0.469) | 0.352 (0.490) | −0.021 [−0.116, +0.074] | +0.021 | +0.042 [−0.238, +0.322] | 163 [140, 185] | 153 [124, 183] |
| 1 | 0.745 (1.062) | 0.787 (1.148) | +0.042 [+0.005, +0.079] | +0.086 | +0.033 [−0.026, +0.091] | 325 [311, 338] | 343 [321, 364] |
| 2 | 0.382 (0.419) | 0.382 (0.519) | +0.001 [−0.084, +0.085] | +0.100 | +0.016 [−0.068, +0.101] | 166 [143, 189] | 166 [147, 186] |
| 3 | 0.721 (0.912) | 0.843 (1.004) | +0.123 [+0.037, +0.209] | +0.092 | +0.010 [−0.363, +0.382] | 314 [279, 348] | 367 [365, 370] |
| 4 | 0.602 (0.771) | 0.275 (0.266) | **−0.327 [−0.412, −0.242]** | −0.505 | −0.325 [−0.452, −0.198] | 262 [245, 280] | 120 [97, 142] |
| 5 | 0.240 (0.277) | 0.722 (0.955) | **+0.482 [+0.445, +0.519]** | +0.678 | +0.439 [+0.300, +0.578] | 105 [83, 126] | 315 [302, 327] |
| 6 | 0.301 (0.281) | 0.652 (0.805) | **+0.351 [+0.172, +0.530]** | +0.524 | +0.367 [+0.324, +0.409] | 131 [53, 210] | 284 [245, 323] |
| 7 | 0.281 (0.343) | 0.324 (0.380) | +0.044 [−0.004, +0.091] | +0.037 | +0.009 [−0.234, +0.251] | 122 [100, 144] | 141 [128, 155] |

- **E134-R5, the bench's word differences: AGREES** (registered). At the four bits where the bench put W67 − W79 at 0.10 W or more (2, 4, 5, 6), the three that resolve (4, 5, 6) have the bench's sign, and bit 2 reads +0.001 [−0.084, +0.085] against the bench's +0.100. Measured over bench, post hoc: 0.65, 0.71 and 0.67 at bits 4, 5 and 6.
- **E134-R2, the word at bit 6: INCONCLUSIVE** (registered). W67 − W79 is +0.351 [+0.172, +0.530] W; it clears zero, but its lower end is below the registered WORD line of 0.262 W (half the bench's +0.524). It is not SAME either (that needs the interval inside ±0.10 W). The width is W79's bit-6 item: `aj_6` reads 0.301 [0.121, 0.481] W on three blocks. Post hoc, labelled, no verdict: the balanced twin reads +0.367 [+0.324, +0.409] W, and with the set-aside block back in (the gates-off arm, four blocks) the all-in contrast reads +0.364 [+0.261, +0.467], 0.001 W under the line.
- Over the 16 all-in A items the bench's frozen prediction reads **0.169 W rms** (bias −0.132), and the position-only null, E67's own list on this card applied to both words, reads **0.310 W** (−0.224). On W79's 16 items: 0.145 against 0.374 W.

**2. A's low bits are the flip alone, on both words** (all-in / balanced per flipped bit; E102-R2's question on a second card):

| bit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| W79 | 1.21 [0.78, 3.65] | 0.98 [0.90, 1.06] | 1.03 [0.92, 1.13] | 0.99 [0.85, 1.14] | 0.93 [0.78, 1.16] | 0.90 [0.51, 1.81] | 1.17 [0.41, 2.18] | 1.05 [0.69, 1.64] |
| W67 | 1.00 [0.59, 1.86] | 0.99 [0.88, 1.11] | 0.98 [0.76, 1.29] | 1.14 [0.75, 2.39] | 0.91 [0.70, 1.13] | 0.98 [0.95, 1.02] | 1.01 [0.87, 1.14] | 1.17 (unbounded) |

- **E134-R1: POSITION** (registered): both of E102-R2's low-bit cells, bits 0 and 6 on W79, have upper bounds below 4 (3.65 and 2.18). That is the low half of E102-R2, which E102 left INCONCLUSIVE and its amendment could not score. Here it is decided on a second card, with E102's own tiles. Bit 22, E102-R2's other cell, was not run.
- **E134-R3: FLIP** (registered): W67 at bit 6, where its word makes the flip dear, reads 1.01 [0.87, 1.14]. The extra cost is the same per flip in both layouts, so it is not the accumulators' swing. The real-sum counts say the sums do not part at any A bit run here, on either word (0 result-path bits an op over the zero, `e134/e134-tiles.json` › `exact`).

**3. B: the swing starts at bit 8, where the sums part, and grows with the parted bits** (E79's B words; the swing is all-in − balanced × 4096/3968, in board W):

| bit | all-in, fJ | balanced, fJ | ratio per flip | **swing, W** | bench | real-sum result bits an op, all-in over balanced |
|---:|---|---|---|---|---:|---:|
| 6 | 106 [99, 112] | 100 [97, 104] | 1.06 [0.96, 1.16] | +0.026 [−0.017, +0.069] | −0.000 | 0 |
| 7 | 97 [89, 105] | 97 [86, 108] | 1.00 [0.91, 1.10] | **−0.000 [−0.044, +0.043]** | −0.000 | 0 |
| 8 | 133 [126, 139] | 100 [92, 109] | 1.32 [1.22, 1.45] | **+0.149 [+0.106, +0.192]** | +0.139 | 4,551 |
| 9 | 156 [149, 164] | 83 [71, 95] | 1.88 [1.60, 2.26] | +0.336 [+0.258, +0.414] | +0.266 | 9,263 |
| 10 | 208 [199, 216] | 93 [88, 98] | 2.23 [2.05, 2.43] | +0.527 [+0.471, +0.583] | +0.481 | 13,921 |
| 11 | 283 [275, 291] | 92 [87, 97] | 3.09 [2.92, 3.28] | +0.879 [+0.839, +0.919] | +0.759 | 21,947 |
| 12 | 313 [306, 320] | 95 [92, 97] | 3.30 [3.21, 3.41] | +1.001 [+0.969, +1.034] | +0.934 | 27,246 |
| 13 | 419 [408, 429] | 100 [96, 105] | 4.17 [3.92, 4.44] | +1.461 [+1.400, +1.521] | +1.216 | 36,595 |
| 14 | 482 [469, 495] | 113 [103, 123] | 4.26 [3.89, 4.70] | +1.694 [+1.615, +1.773] | +1.460 | 41,812 |
| 15 | 542 [536, 548] | 101 [99, 104] | 5.34 [5.19, 5.51] | +2.023 [+1.990, +2.055] | +1.630 | 55,015 |
| 16 | 608 [590, 625] | 101 [95, 106] | 6.03 [5.65, 6.46] | +2.327 [+2.237, +2.416] | +1.951 | 64,954 |

- **E134-R4: AT 8** (registered). Bit 7's swing lies inside ±0.10 W (−0.000 [−0.044, +0.043]) and bit 8's lower bound is above zero (+0.149 [+0.106, +0.192]). The frozen counts named the two bits before the data: the last bit at which the two all-in sums stay equal, and the first at which they part. The self-test gave this rule 38 of 40 at five B blocks.
- The balanced price is flat, 83–113 fJ a flip at every bit from 6 to 16 (E102, card 1: 87–176). The all-in price rises from 97 to 608 fJ. **Positions 7–10 and 12–15 are measured here for the first time in both layouts.**
- The bench predicted the swing's onset and shape. It falls short at the top by about 15% (measured over bench 1.07–1.26 from bit 8 up, post hoc). Over the 22 B items it reads 0.116 W rms. E65's all-in list (a fresh word at each bit, another protocol) lies within 0.20 W of E134's all-in items at every bit from 6 to 16, post hoc; applied to the balanced items too it reads 0.836 W rms, as it must, having no balanced layout.
- **The ratio replicates E102 on a second card:** 1.06 against 1.05 at bit 6, 3.09 against 3.20 at bit 11, 6.03 against 5.78 at bit 16.

**4. The session against E67: E134-S1 PASS** (registered). E67's own eight tiles read within their bands of E67's list on this card, eight of eight. The bands are wide because E67's own errors are (2 × its s.e. reaches 0.48 W), and E134 reads below E67 on the same tiles by 0.18 W on average (bias −0.181 W on W67's list): at bit 6, 0.652 against E67's 0.990 ± 0.224 W. So E67's 0.99 W at bit 6, the number that started this, was high. The word effect is real, but smaller than E67 against E102 suggested (+0.351 W here, not +0.73).

## Registered against happened

| rule | registered | happened, primary arm | verdict, primary | rail | board p80 | dips kept | gates off |
|---|---|---|---|---|---|---|---|
| E134-R1 A's low bits, W79 | POSITION if upper < 4 at bits 0 and 6 | 1.21 [0.78, 3.65]; 1.17 [0.41, 2.18] | **POSITION** | INCONCLUSIVE (bit 6 unbounded) | POSITION | NOT SCORED | POSITION |
| E134-R2 the word at bit 6 | WORD if lower ≥ 0.262 W; SAME inside ±0.10 W | +0.351 [+0.172, +0.530] | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | NOT SCORED | INCONCLUSIVE (+0.364 [+0.261, +0.467]) |
| E134-R3 W67 bit 6, all-in / balanced | FLIP inside [0.5, 2.0); SWING lower ≥ 2 | 1.01 [0.87, 1.14] | **FLIP** | FLIP | FLIP | NOT SCORED | INCONCLUSIVE (1.16 [0.77, 2.27]) |
| E134-R4 B's swing onset | AT 8: bit 7 inside ±0.10 W, bit 8 lower > 0 | −0.000 [−0.044, +0.043]; +0.149 [+0.106, +0.192] | **AT 8** | AT 8 | AT 8 | INCONCLUSIVE | AT 8 |
| E134-R5 the bench's word differences | AGREES: resolved bits on the bench's side, at least half resolve | 3 of 4 resolve, all with the bench | **AGREES** | DISAGREES (bit 2: −0.056 [−0.071, −0.041]) | AGREES | NOT SCORED | AGREES |
| E134-S1 E67's tiles against E67's list | PASS if 6 of 8 in band | 8 of 8 | **PASS** | FAIL (4 of 8) | PASS | NOT SCORED | PASS |

**Expected, frozen: R1 POSITION, R2 WORD, R3 FLIP, R4 AT 8, R5 AGREES, S1 PASS. Five came out as expected; R2 did not reach WORD and reads INCONCLUSIVE.** Every verdict moves at some arm but R2's, and they are marked arm-sensitive:
- **Dips kept:** with the board meter's dips left in, the train gate sets aside six of the nine blocks (a dip moves a zero read by up to 0.9 W). That is why the registered primary removes them (E82 A2); the A rules then have no blocks.
- **The rail:** it reads about 0.8 of the board. S1 compares it with E67's board watts and fails; R1's bit-6 ratio is unbounded there; and R5's bit 2 resolves the other way, by 0.056 W against the bench's 0.10.
- **Gates off:** this puts the set-aside block back, and R3's upper bound reaches 2.27.

The self-test's rates are in the registration (§ Precision, `selftest.txt`).

## What it changes

- **Item 15's single-bit sentence.** On aifoundry3:
  - "other base words" is answered on A, for bits 0–7 and two words: the price of one A bit depends on its word, as the bench's Booth recoder says. That is registered as R5 AGREES; the bit-6 cell R2 alone is INCONCLUSIVE at its line.
  - "A's low bits (R2)" is decided for bits 0 and 6: POSITION, about 1×, on a second card.
  - "the other positions" is answered on B for bits 7–10 and 12–15, which now have both layouts, and the swing's onset is placed at bit 8 (R4 AT 8).

  Still open: the other fp32 positions (17–21, 23–30 and the A side above bit 7, in both layouts), a second B word set, other A words beyond two, the sign on the rail, and bit 22's half of E102-R2. Proposed replacement for the sentence: *"Single-bit prices: on B the composite all-in price starts at bit 8, where the two accumulators first part, and grows with the parted bits to 6× at bit 16, on two cards (E102, E134); the balanced price is flat at 83–176 fJ. On A the flip alone is the price at the low bits (about 1× in both layouts), and it depends on the base word: one bit costs up to 3× more on one word than another, where the bench's Booth recoder puts it (E134, one card, two words, bits 0–7). Open: the other positions above bit 16 and on A above bit 7, other words, and the sign on the rail (R4)."*
- **The kinds page's single-bit price lists** need the word attached to any A-side number: E67's list is W67's and E102's is W79's. "A bit's price on A" without its word is not a property of the chip. B-side numbers carry over between words (E65's list, a fresh word at each bit, agrees with E134's all-in B items within 0.20 W at every bit from 6 to 16, post hoc).
- **Item 6 (a model for every kind):** the fixed bench, frozen, predicts both lists on tiles it never saw: 0.169 W rms over the 16 A all-in items, 0.116 W over the 22 B items. On A it overstates the word effect by about 1.5× (measured over bench 0.65–0.71), the same direction and size E113 read post hoc ("the bench counts an A flip 1.2–1.7× too high against a B flip"). On B it understates the swing by about 15%.
- **E67's bit 6 (0.99 W)** reads 0.652 [0.564, 0.741] W on the same tile here. E67's list is high on this card by 0.18 W on average, against a train with each item's own zero beside it (S1 passes only on E67's own wide errors).

## Interpretation (labelled: a reading, not measured)

- **Why the word matters on A.** A is the operand the multiplier recodes in radix 4 (`txfma_f1.v:113-114`), so each digit selects 0, ±B or ±2B. With B = 1.0, a negative digit's row is the complement of B's bits, sign-extended across the row; a positive digit's row is one bit.
  - The dear flips here move a digit between zero-or-positive and negative: W79's bit 4 (digit 2: 0 → −1), W67's bit 5 (digit 2: −2 → 0, digit 3: 0 → −1) and W67's bit 6 (digit 3: 0 → −1).
  - The cheap ones stay on one side: W79's bits 5 and 6 (digit 3: +2 → +1), W67's bit 4 (digit 2: −2 → −1).
  - Bits 0, 1 and 3 change a sign on both words, and read alike.

  That is the bench's structure, and the card follows it in sign at every bit that resolves. The silicon's netlist is not public; this says the card behaves like that structure, not that it is it.
- **Why B's swing starts at 8.** In the all-in layout the two accumulators a lane alternates between receive products that differ in bit j of B's significand. Late in a launch a sum is about 2²³ times a product, so the sum keeps only the products' top bits. By the real-accumulator counts, a difference at bit 7 or below is rounded away at every addition, and the two sums stay equal; from bit 8 it survives and the sums part (E102's reading, now placed to the bit and tested).

## Device commands sent

*His rule of Mon 2 Nov 2026 (Q136): every device-management command the run's harness, sampler, host program and helpers sent, classified from the firmware source (et-platform `836a4ab`, BL2 0.22.0; paths under `device-bootloaders/src/ServiceProcessorBL2/`), as [the registration](../../../../tools/claims-v3/e134/README.md#device-commands-sent) listed them before the first launch. Every one sent was a READ.*

| # | command | sent by, in this session | firmware path at `836a4ab` | class |
|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config`: 21 reads (two for each of the nine blocks and the smoke, and the session-end read) | `services/thermal_pwr_mgmt.c:613` (copies SP RAM) | READ |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | the same reads | `thermal_pwr_mgmt.c:665` (copies SP RAM) | READ |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | the same reads | `thermal_pwr_mgmt.c:551` (copies SP RAM) | READ |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` (10 Hz, ten sampler runs: one per block and the smoke) | `services/perf_mgmt.c:276` → `driver/io_pll.c:932` (PLL register reads) | READ |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | `thermal_pwr_mgmt.c:1142` → `driver/pmic_controller.c:1473`, `:254` `i2c_read` (two PMIC voltage-register reads) | READ, a PMIC voltage read, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample` (lib.sh's `drain_mgmt`, which sends it after a sampler fails to start twice, was not needed: every sampler started) | `thermal_pwr_mgmt.c:984` (copies SP RAM) | READ |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` → `thermal_pwr_mgmt.c:2780` (copies SP RAM, resets nothing) | READ |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; lib.sh `die_c` at each block's start | `thermal_pwr_mgmt.c:732` (PVT reads, cached in SP RAM) | READ |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` | `thermal_pwr_mgmt.c:1010` → `pmic_controller.c:1473` (nine PMIC voltage-register reads) | READ, PMIC voltage reads, allowed by his rule of 2 Nov |

**Not sent:**
- `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset: there is no `--reset-ms` anywhere, and `block_e134.sh:105`, the one `start_sampler` call, passes the output file and the duration only;
- `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`;
- any residency read;
- any `DM_CMD_SET_*`, or any governor, TDP, threshold or clock set;
- any reset, power cycle, PCIe, driver, firmware or OTA operation.

The host program, `sparsity_host`, opened the ops node only (`workloads/sparsity/host/main.cpp:172`, `createPcieDeviceLayer(true, false)`): no management command. `et-who` / `et-holders`, `et-lab-manifest`, `flock`, `timeout` and `ps` open no device node.

The preflight checker's three runs are in [`dmcmd-audit.txt`](../../../../tools/claims-v3/e134/dmcmd-audit.txt) (Q136(w)'s `dmcmd_audit.py` at `32e9c109`): NO-GO with no exception, which is the conditional at `lib.sh:154` alone; GO with the reviewed exception for `block_e134.sh:105`; and NO-GO under `--deny-pmic-read` on the voltage reads alone. aifoundry3 runs a thermal firmware build that is not public, so each READ's class rests on `836a4ab`'s handlers (E130 A1's caveat). The registered condition held: the session-start read and the smoke's telemetry came back in the form E127's and E132's runs recorded (the same fields; TDP 0 W, 65 °C, 600 MHz).

## Card conduct

| | |
|---|---|
| before | `et-who` at 11:37:35, 11:50:09 and 11:51:33: no process held an ET-SoC-1 device node or card lock. Other lab users' idle logins were present and did not block (E60's D1). The registration was on origin/main before the claim. |
| reservation | the day's post `1566837317765963987`, rewritten under `EXPECT_TEXT` and the Discord lock: dry run, `--save` at 11:49:28 PST, read back at 11:49 (aifoundry2's and aifoundry1 card 1's clauses kept word for word, aifoundry3's added) |
| session | the smoke's config read 11:50:46 to the session-end read 12:29:19: 38.6 card-minutes. Nine blocks of 282 s (A) and 224 s (B), as estimated. |
| readings | board at most 40.81 W (stop 65 W), die 50–62 °C (stop 70 °C); 600 MHz in every sample; cycles per op 546.001; duty ≥ 0.995; 143 meter-dip samples removed over nine blocks |
| end | the session-end read: TDP 0 W, 65 °C, max_power, 600 MHz, 522 mV; `et-who` clean at 12:29:19; nothing left running |
| release | the post rewritten at 12:29:58 to drop this card's clause, aifoundry2's kept word for word (it is still held, so no " — released"); read back at 12:29 |

## Departures and disclosures

1. **The train gate set aside A block 13410, and the A rules rest on the minimum of three blocks.** That was registered: the gate is E102's and E130's, a zero's interior read more than 0.25 W off its neighbours' line, and it acted on the first A block's `aq`. A fifth A block would have been the margin. The budget rule (registered, A 282 s projected) stopped before it at 2,313 s of the 2,340, so the A rules have t = 4.30. At three A blocks the self-test read R2 WORD in 33–39 of 40 sessions in the bench's world, with median half-widths of 0.114–0.148 W. Here the half-width is 0.179 W, and the effect is 0.67 of the bench's: R2 reads INCONCLUSIVE, as registered.
2. **The smoke's seven 2 s runs went through the reduction once at the desk at 11:52 PST** (`reduce_e134.py` on the smoke alone), to test the pipeline before the blocks. All seven failed the duty gate, as 2 s runs must against a 2 s window. Their board values were printed and none is used anywhere; no registered file changed after `af56740a` (`git diff af56740a` on `tools/claims-v3/e134/` and `bench/` is empty).
3. **The collection ran twice**, both times with the registered `collect_e134.sh` unchanged. The first ran over a scratch copy of the raw blocks on the Intel, and the folder paths it recorded were a desk machine's. The second, committed here, ran over the committed copy of the raw blocks, as E127's correction C1 did. The verdicts are identical; only those folder paths differ.
4. **No interim look at power during the queue:** the waits read the queue log's block ends only.
5. **Post hoc, labelled, no verdict:**
   - the measured-over-bench factors (0.65–0.71 on A's word differences, 1.07–1.26 on B's swing);
   - R2's balanced twin and its gates-off reading;
   - the digit reading in § Interpretation;
   - the comparison with E67's list beyond S1's registered bands;
   - the proposed sentence for item 15.

## Caveats

One card, one clock (600 MHz, 522 mV), one session. On A, two base words and bits 0–7 only; on B, one set of E79's eight words and bits 6–16. The A rules have three kept blocks. Both layouts drive the same multiplier, so "FLIP" says the cost is not the accumulators' swing, not where inside the multiply it is. The trains have no temperature term (E102's and E130's footing): an item's own self-heating is in its step, at most a few hundredths of a watt at these steps. The bench is the open RTL's, priced with E92's coefficients fitted on E78's kinds on this card; its counts were not read back on silicon. E67's list came from another protocol and session on this card. The sign on the rail (E102-R4) and E102-R2's bit-22 cell were not run.

## Files

- `README.md` (this).
- The primary reduction: `e134.json`, `runs.csv`, `reduce.txt`, `reduce.log`.
- The registered arms: `e134-dipskept.*`, `runs-dipskept.csv`, `e134-gatesoff.*`, `runs-gatesoff.csv`, `reduce-*.txt`, `reduce-*.log`.
- Every rule, price, ratio, contrast and model, every arm: `scored.json`, `results.md`, `score.log`.
- `code.sha256`.
- `logs/`: the queue log, both dry runs, the session's two config reads and their times, the binaries' sha256.
- `aifoundry3/kinds/p134*`: the nine raw blocks (telemetry, marks, records, tile dumps, config reads, manifests, code hashes), plus the smoke as `kinds-smoke-p13401`.
- `bench/`: `counts-e134.json` and `bench-e134.log`, the fixed RTL bench's counts of the 57 tiles, frozen with the registration.
- The tiles, registration and code: [`tools/claims-v3/e134/`](../../../../tools/claims-v3/e134/README.md).
