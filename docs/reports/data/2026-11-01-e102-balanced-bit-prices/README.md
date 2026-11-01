# E102: single-bit prices in a balanced layout, the A side, and int8's B side (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132, the first half of item 12 of the kinds page's section 11. Pre-registered in `47060961` (committed 01:25:56 PST and pushed by 01:26:02, before the claim and the first launch):
[`tools/claims-v3/kinds/E102.md`](../../../../tools/claims-v3/kinds/E102.md), frozen numbers in `predictions-e102.json`, tiles and counts in `e102/e102.json`, the scorer `score_e102.py` and its self-test in the same commit, the RTL bench's counts of the frozen tiles in [`bench/`](bench/). Amendment A1 `f4c07ead` (02:42:26 PST), written after session 1's data was read and before any data it adds.
aifoundry1 card 1 (`V3_DEVICE=1`) at 600 MHz, 499.0 mV mean; TDP 65, threshold 65 °C, 600 MHz and 499 mV read under the card lock at both ends of both smokes and of every block, and at the end of each session (02:22:17, 03:08:30 PST); never set. Nothing was written to the card, and no `--reset-ms` was sent.*

*Session 1: claim `1566383041881055233`, posted 01:26:59 PST ("for 1.5 h, until ~02:56 PST"), released 02:22 PST by editing it (55 min); smoke 10201 at 01:27; queue 01:33:02–02:21:04, 2,882 s, inside the registered 3,400 s. Session 2 (A1): claim `1566404932167270421`, posted 02:53:58 PST ("for 0.5 h, until ~03:23 PST"), after E103's post read released and `et-who` read clean; released 03:08 PST (14.7 min); smoke 10202 at 02:54:06; queue 02:54:39–03:08:00, 801 s, inside A1's 860 s.*

**What ran.** 72 tiles built on E79's own base words (`fp32.bj_22`, `bp_22`, `fp16.bj_*`, `bp_9` and every int8 single are byte-identical to the tile E79's host dumped). Eighteen blocks, 576 runs, none failed a run gate:
**G** (10210–13), E78's launch at 58 °C after 59 °C and 2 s quiet, for steps near or above 2 W and four ties, and **10214**, a short G of the six items R3 and R4's B leg read; **T** (10220–23), a train of float runs with no heater and a 0.2 s gap, 4.86 s a run against the gate's 6.7 s; **I** (10230–34), the same in int8; **R** (10240–43), A1's train with an own zero within three runs of every item.
**The launch rule skipped four runs** (the reading came back to 59 °C during the quiet: `fp32.bj_31` in 10210, `fp32.bp_23` in 10211, `fp32.hq_e64` and `fp16.zeros` in 10213). **The trains' own gate set aside T pass 10223** (0.277 W against 0.25) **and R blocks 10241, 10242, 10243** (0.258, 0.355, 0.294 W), § Departures. So the primary keeps G 5, T 3, I 5, R 1. A price is a step over the item's own zero (a constant-operand tile, interpolated in time) divided by the item's own designed flips per op and the run's rate, per pass; intervals are 95% over passes, t(0.975, n−1) × SE. Board and minion rail are both printed; the rail is the registered primary arm except where named. Numbers below are from `scored.json` › `primary` unless a section of [`check_e102.txt`](check_e102.txt) is named.

## Results

**In plain words.** A low mantissa bit costs the same whether or not the accumulators are balanced: E65's and E67's low floor is the flip itself, not a composite. The composite appears between bits 11 and 16 and reaches about 6× at the top of the B-side mantissa. By the frozen counts on real accumulators, that is because a low-bit difference is rounded away inside a large sum and never makes two accumulators differ. A balanced mantissa flip costs about the same at every position (87–164 fJ on B). At the exponent and the sign the order reverses: the balanced layout is 2–5× dearer, because the aligner or the adder's add/subtract now moves. int8's B list resolves on the rail: odd bits cost 2.9× even bits, E79's shape, on a second card. **The fixed RTL bench, frozen before the data, called all of the float shape; it undercounts int8's single bits, as a behavioural `*` must.** Along the way E102 found a fault in two lab tools that other lanes' models rest on: up to 5.5 W on E92's fp16 tiles, whose "frozen" sums are not frozen (§ A fault).

**1. The ratio depends on position.** Per flipped bit, all-in (E65's and E67's constructions) over balanced, fp32 (`check_e102.txt` [C], [G]). `all-in` and `balanced` are board fJ, primary reduction, from the block the item is listed in (T for steps under about 2 W, G above; ratios at 16 and 20 are gate over train).

| bit | field | B all-in, fJ | B balanced, fJ | **B ratio, board** | B ratio, rail | bench, frozen | A all-in, fJ | A balanced, fJ | **A ratio, board** | A ratio, rail | bench, frozen |
|---:|---|---:|---:|---|---|---:|---:|---:|---|---|---:|
| 0 | mant | 133 [114, 152] | 152 [96, 208] | **0.87 [0.55, 1.57]** | 0.92 [0.60, 1.49] | 1.00 | 176 [90, 262] | 137 [42, 232] | **1.29 [0.99, 2.45]** | 1.12 [0.83, 2.41] | 1.00 |
| 6 | mant | 119 [82, 156] | 113 [106, 120] | **1.05 [0.70, 1.43]** | 1.01 [0.67, 1.73] | 1.00 | 113 [75, 151] | 105 [17, 193] | **1.07 [0.74, 4.63]** | 1.02 (unbounded) | 1.00 |
| 11 | mant | 279 [263, 295] | 87 [76, 98] | **3.20 [2.92, 3.56]** | 2.46 [2.27, 2.68] | 2.79 | 481 [383, 580] | 332 [306, 358] | **1.45 [1.20, 1.68]** | 1.37 [1.02, 1.80] | 1.29 |
| 16 | mant | 606 [568, 643] | 105 [68, 142] | **5.78 [4.22, 8.97]** | 5.81 [3.76, 12.47] | 4.35 | 591 [555, 627] | 83 [72, 95] | **7.10 [6.07, 8.41]** | 7.96 [6.86, 9.13] | 4.27 |
| 20 | mant | 871 [830, 913] | 164 [105, 224] | **5.31 [3.86, 8.36]** | 5.11 [3.28, 11.37] | 4.63 | 1,003 [907, 1,099] | 317 [268, 366] | **3.17 [2.59, 3.90]** | 3.63 [2.48, 6.33] | 3.05 |
| 22 | mant | 1,087 [1,060, 1,115] | 142 [125, 159]; gate 176 [121, 231] | **6.17 [4.80, 8.79]** (gate/gate) | 5.90 [5.11, 6.97] | 6.81 | 1,366 [1,224, 1,507] | 597 [438, 755]; gate 636 [554, 719] | **2.15 [1.92, 2.42]** (gate/gate) | 2.20 [1.96, 2.53] | 1.97 |
| 23 | exp | 200 [169, 231] | 474 [453, 495] | **0.42 [0.33, 0.51]** | 0.44 [0.38, 0.50] | 0.28 | 210 [155, 265] | 408 [355, 461] | **0.52 [0.43, 0.59]** | 0.53 [0.36, 0.69] | 0.41 |
| 27 | exp | 144 [123, 165] | 476 [455, 497] | **0.30 [0.26, 0.34]** | 0.30 [0.26, 0.33] | 0.16 | 143 [48, 237] | 461 [431, 490] | **0.31 [0.10, 0.53]** | 0.38 [0.13, 0.61] | 0.20 |
| 30 | exp | 175 [154, 196] | 383 [346, 420] | **0.46 [0.40, 0.52]** | 0.43 [0.38, 0.48] | 0.41 | 182 [152, 211] | 462 [433, 492] | **0.39 [0.35, 0.43]** | 0.38 [0.24, 0.49] | 0.41 |
| 31 | sign | 118 [51, 185] | 542 [510, 575] | **0.22 [0.10, 0.32]** | 0.24 [0.15, 0.39] | 0.25 | 129 [37, 221] | 711 [594, 827] | **0.18 [0.05, 0.32]** | 0.20 [0.18, 0.23] | 0.19 |

**E102-R1, the rule the brief named: POSITION**, on both arms. At bits 0 and 6 the upper bounds are below the registered 4 (rail 1.49 and 1.73), and at bit 22 the lower bound is above it (rail 5.11). The page's implied 5–7× holds at bits 16–22 and not below: it is 1× at 0 and 6 and 3× at 11. **E102-R2, the same on A: INCONCLUSIVE** on both arms, on one cell: at bit 6, `ap_6`'s rail step in T is itself a bound (0.167 [−0.051, 0.384] W), so the rail's ratio is unbounded, and the board's upper bound is 4.63 against the rule's 4. A1 tried to decide it and **did not** (§ What amendment A1 settled): its rule is NOT SCORED. Post hoc, labelled, no verdict, A1's four blocks read 0.95 [0.74, 1.29] and 0.99 [0.79, 1.29] on the rail at bits 0 and 6 ([Q]).

The A list is not monotonic, and the bench said so first: 7.1× at bit 16, 3.2× at 20, 2.2× at 22 against its frozen 4.3, 3.1, 2.0. A is the Booth multiplier, so `ap_22` and `ap_20` move partial products in a balanced layout too (bench: multiplier stage 0.71 M of 0.83 M net toggles an op at bit 22), and they depend on the one base word's neighbouring bits. Over all ten positions Spearman(bench, measured) is 0.96 on B and 1.00 on A ([G]).

**2. Balanced mantissa flips are nearly flat; what rises is the accumulators' swing.** B-side balanced: 152, 113, 87, 105, 164, 142 fJ at bits 0, 6, 11, 16, 20, 22 (a factor of 1.9), where the all-in list runs 133 to 1,087 ([O]). E79's one point, 150 fJ on aifoundry3, is the level of the whole list. Counted on the real accumulators ([I], `e102/e102.json` › `exact`, frozen before the data): `jg`'s C read changes 0 bits an op over the zero at bits 0 and 6, 10,952 at 11, 32,492 at 16, 48,892 at 20, 49,908 at 22. Those are the positions where the ratio leaves 1. **So E65's floor from the LSB to about bit 9, and its rise above it, read as one mechanism: where the sum still registers the difference** (a reading: the count is the desk's and C was not read back; § Interpretation).

**3. What a composite is, now that E92 has priced the adder's flops.** **E102-R7 CONFIRMED** on both arms: at E92's frozen 6.68 fJ per flop bit, the adder's flops carry **22%, 24% and 29%** of the all-in excess at bits 16, 20 and 22 (board; 0.51, 0.78, 1.27 W of 2.30, 3.25, 4.34 W; band 0.15–0.50). If the flops carried it all they would cost 23–30 fJ a bit. So a composite price is: the flip's own path, about 100–150 fJ at any mantissa position; plus the swing between two sums that differ, in the bits where they differ, of which the adder's flops at E92's price are about a quarter. The frozen bench puts the rest in the normaliser and adder nets beyond those flops, the C register file, the exponent path and the multiplier (at bit 22, 2.30 M net toggles an op over the zero: adder and normaliser 1.34 M, multiplier 0.22 M, C register file 0.15 M, exponent 0.15 M).

**4. The exponent and the sign reverse.** Balanced − all-in, watts ([C]; passes in brackets):

| | fp32 B bit 23 (4) | fp32 B bit 27 (5) | fp32 B sign (4) | fp32 A bit 23 (3) | fp32 A bit 27 (3) | fp32 A sign (3) | fp16 B sign (4) |
|---|---|---|---|---|---|---|---|
| rail | **+0.909** [0.815, 1.003] | **+1.164** [1.079, 1.248] | +1.579 [0.867, 2.291] | **+0.318** [0.199, 0.436] | **+0.459** [0.261, 0.657] | **+0.939** [0.758, 1.120] | **+1.250** [1.140, 1.360] |
| board | +1.193 [0.989, 1.397] | +1.457 [1.379, 1.534] | **+1.849** [1.718, 1.980] | +0.395 [0.345, 0.446] | +0.664 [0.419, 0.909] | +1.233 [0.905, 1.560] | +1.562 [1.488, 1.637] |

**E102-R3: INVERTED**, on both arms, with A1's two G blocks; session 1 could not score it. **E102-R4: INCONCLUSIVE** on the rail, CONFIRMED on the board: the fp32 A and fp16 B legs clear their floors on both arms, and the fp32 B leg is +1.579 W with a lower bound of 0.867 against the floor of 1.0 on the rail, because the rail read `bp_31` at 2.70 W in one pass and 1.82–2.01 W in the others ([E]); on the board its interval is +1.849 [1.718, 1.980]. No leg is refuted, and the registered primary is the rail, so R4 stays INCONCLUSIVE. Nothing reads like a mantissa's composite (ratios 0.18–0.53). This answers E79's result 1b: an exponent flip is cheap in `jg` because the product and the accumulator it lands on move together, so the aligned operand does not change (0 flop-bit changes over the zero, frozen). In a balanced layout the product alternates against a sum that does not, and the aligner shifts every micro-op (about 139,000–166,000 flop-bit changes an op). A balanced sign makes the sum cancel, so the adder alternates (2,048 alternations an op, E92's mechanism). So "all-in / balanced" is a discount only for the mantissa. **Which price a workload pays at an exponent or sign bit depends on whether its sums follow its products.**

**5. fp16 reads the same way** ([N]): all-in over balanced 2.02 [1.40, 3.53] at bit 0, **4.59 [4.06, 5.31]** at bit 9 (E79 on aifoundry3: 5.6), 0.37 [0.20, 0.62] at exponent bit 12, 0.28 [0.24, 0.32] at the sign; on A, 2.53 [2.39, 2.68] at bit 9, 0.49 [0.11, 1.10] at bit 12. The bench's frozen ratios: 2.18, 4.70, 0.29, 0.24; 2.39, 0.33. fp16 bit 0 is already 2×, where fp32 bit 0 is 1× (a reading: fp16's whole mantissa sits high in the 32-bit sum). Balanced fp16: 108, 118 (gate 112), 183, 248 fJ on B at 0, 9, 12, 15; 278 (gate 239), 224 on A at 9, 12.

**6. int8's B side resolves on the rail, and E79's list stands on a second card.** Line-boundary flips, 1,024 an op per bit, the most the stream allows.

| | bit 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (MSB) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **rail fJ per flip** [95%] | **20** [14, 26] | **61** [45, 78] | **29** [14, 45] | **60** [52, 68] | **19** [1, 36] | **72** [63, 80] | **41** [18, 63] | **76** [67, 85] |
| board fJ per flip [95%] | −29 [−123, 65], a bound | 82 [46, 117] | 43 [16, 69] | 91 [36, 145] | 48 [23, 72] | 94 [63, 126] | 52 [31, 73] | 100 [81, 119] |
| E79, aifoundry3, no temperature term, frozen | 33 | 73 | 29 | 89 | 37 | 96 | 61 | 22 |
| bench, floats' k and a; int8 fit, frozen | 11; 21 | 9; 18 | 11; 22 | 12; 24 | 10; 20 | 12; 24 | 10; 20 | 48; 96 |

- **E102-R12:** all 8 positions are coefficients on the rail, 7 of 8 on the board. Median half-width 15 rail-fJ against the ±29 registered (board 32 against ±70): the int8 train's rail read 0.019 W a run, half of E93's 0.041 ([B]).
- **E102-R9: SHAPE.** `bk_2a` − `bk_15`, three odd bits against three even, +0.136 [0.111, 0.161] W on the rail (above the +0.10 W rule; board +0.164 [0.088, 0.240], INCONCLUSIVE). From the singles, bits 1, 3, 5 cost **2.85× [1.89, 6.09]** bits 0, 2, 4 ([F]). So E79's result 4b is real, and it was the temperature correction, not the card, that erased it: E79's magnitude positions rank the same here (Spearman 0.96 on the board over bits 0–6). Bit 7 is the exception: E79's 22 fJ was one bad reading of a list with an sd of 0.24 W there; here it is the dearest position.
- **E102-R10: RISE.** `bk_f0` − `bk_0f` +0.064 [0.048, 0.079] W on the rail, the bench's frozen +0.06 W, but not for the bench's reason: it prices bit 7 at 4.7× bit 6, and the list has it at 1.9× bit 6 and level with bit 5. Board +0.117 [−0.024, 0.257], INCONCLUSIVE.
- **E102-R8: BENCH-LEVEL as registered, and that label needs its footnote.** `bk_ff`, all eight bits flipping together, is **29.7 [27.7, 31.6] rail-fJ per flipped bit** (board 34 [23, 46], RESOLVED-BETWEEN), under the registered 35. But the singles average **47 [38, 57] rail-fJ**, E79's level, not the bench's. **E102-R11 CONFIRMED** only that `bk_ff` adds up from its nibbles (−0.058 [−0.144, 0.027] W); against its eight singles it is **0.63 [0.53, 0.77]**. So the rule's premise, that all eight bits read the singles' level, fails: flips share their cost. The bench undercounts a single flip 4–5× at the float coefficients and about 2× at its int8 fit, and does not show the shape at all. That is expected of the RTL's behavioural `$signed(a) * $signed(b)` (`tima/tima_top.v:89`): the bench sees the product, not partial products.

**7. The leakage slope no longer moves it.** The trains read no temperature, because E79's B level moved with the reading's whole-degree steps, not with the card ([`desk_noise_e102.txt`](../../../../tools/claims-v3/kinds/desk_noise_e102.txt)). Reduced E79's way, with each run's own reading in the train, `bk_ff` stays a coefficient at every slope, 29–34 fJ (`results.md`), but single bits still move: 3 of 8 become bounds at 0.2414, 0.3803 and 0.545 W/°C, and bit 6 goes 52 → 1 fJ at 0.545 ([F]). With no temperature term, 1 of 8 on the board and 0 of 8 on the rail. Leakage's feedback on a train's pair is at most 7% (0.545 W/°C × 0.13 °C/W), stated, not corrected.

**8. The models** (`results.md`; board, rms over each list, watts; frozen before the data):

| list | the page's ratio | bench `nets_map` | E65/E67/E79's published list | e88+flops on real sums | e88+flops as E92 counted |
|---|---:|---:|---:|---:|---:|
| fp32 B balanced (11) | 1.240 | **0.243** | | 0.963 | 0.974 |
| fp32 B all-in (10) | | 0.223 | **0.202** | 0.923 | 1.487 |
| fp32 A balanced (11) | 0.776 | **0.201** | | 0.980 | 0.966 |
| fp32 A all-in (10) | | **0.235** | 0.294 | 0.302 | 0.618 |
| fp16 balanced (8) | 1.074 | **0.153** | | 0.772 | 0.781 |
| fp16 all-in (6) | | 0.255 | **0.218** | 0.889 | 1.596 |

The bench's frozen prediction beats every alternative on the balanced lists and ties the published lists on the all-in ones, on a card and a base it never saw, at about the board's noise. For int8 B (13 items, rail): int8 fit 0.077, E79's list 0.091, the float coefficients 0.134, E88's model 0.142 W.

**9. The session tied.** E102-S1 PASS: `fp32.randn` −0.04 W, `fp16.randn` +0.14 W, `anchor_pi` −0.11 W, `int8.full` +0.09 W from E82's dips-removed values (FAIL only at the 0.545 and 0 W/°C arms, which carry another slope than E82's, as in E86, E90 and E93). **E102-R5 INCONCLUSIVE**: 4 of 6 ties to E79 CONFIRMED (`bj_22` 1,087 [1,060, 1,115] fJ against 1,021 carried over; `fp16.bj_9` 512 [478, 546]; the ratios 6.2 [4.8, 8.8] and 4.6 [4.1, 5.3]), 2 INCONCLUSIVE (`bp_22` 176 [121, 232], `fp16.bp_9` 112 [93, 131], over their bands' upper edges), 0 REFUTED. Checks: cycles per op 546.001 / 546.001 / 318.0; duty 0.996; 154 meter-dip samples removed over eighteen blocks; rail lag re-fitted 0.95 s; carry-over +0.0005 ± 0.0016 W/W.

**10. What the trains gave, and what they did not.** In int8 they did what they were for. A float train is not steady: the die reads about 57 °C at its first run and 61–62 °C at its last ([J]), and its zeros rise along a curve of about 2 W amplitude, τ about 45 s ([M]). Straight lines through the zeros under-read the first quarter. And the rail, the registered primary, remembers the previous run's step: +0.078 W per W ([`desk_a1_e102.txt`](../../../../tools/claims-v3/kinds/desk_a1_e102.txt)). So for floats the registered primary arm was the worse one, and R1's verdict stands on both. **E102-R6 INCONCLUSIVE on the rail** (train − gate pooled over four items −0.035 [−0.188, 0.119] W against ±0.15), CONFIRMED on the board (−0.005 [−0.178, 0.168] against ±0.30). The train and the gate read the same within those intervals; item by item, `fp16.ap_9` differs by +0.112 [0.048, 0.176] W on the rail.

## What amendment A1 settled

A1 (`f4c07ead`, E102.md § Amendments) added 13.4 min of queue, because session 1's launch skips left R3 and R4 unscored, and tried a real fix for R2. The registered scorer ran unchanged over all kept G passes; no threshold moved.

| rule | session 1 (three G blocks) | with A1 |
|---|---|---|
| **R3** | NOT SCORED (`bp_23` two passes) | **INVERTED**, rail and board |
| **R4** | INCONCLUSIVE (fp32 B not scored; A, fp16 CONFIRMED) | **INCONCLUSIVE** on the rail (fp32 B +1.579 [0.867, 2.291] against 1.0); CONFIRMED on the board, all three legs |
| R5 | INCONCLUSIVE, 4 / 2 / 0 | the same, narrower |
| R6 | INCONCLUSIVE on the rail by 0.004 W | INCONCLUSIVE on the rail (lower bound −0.188 against −0.15) |
| R7 | CONFIRMED | CONFIRMED |
| **R2** | INCONCLUSIVE on T | **INCONCLUSIVE on T, unchanged** |
| **R2a** (A1's reading of R2 on a dense train) | | **NOT SCORED**: the gate set aside three of its four blocks |

**R2a failed on a fault in my amendment, not on the card.** The fix itself held: an own zero within three runs of every item. But only the first R block opened with settling reads. The other three started after the gap between blocks (about 18 s idle), and a run's rail window after an idle gap is not settled: each block's first zero read sits 0.7–0.9 W under its next ([P]; 10240's own five settling reads show it, 18.27, 18.98, 19.07, 19.22, 19.28). The registered gate then read the second zero as 0.258–0.355 W off the line, and set those blocks aside. The amendment said the gate applies, so it applies: R2a is not scored, and **R2 stays INCONCLUSIVE**.

**Post hoc, labelled, no verdict** ([Q]): drop what the idle gap touches (a block's first read, and the pair only it brackets), and the same gate's largest departure is 0.078 W. Over the four blocks: rail 0.95 [0.74, 1.29] at bit 0 and 0.99 [0.79, 1.29] at bit 6, board 0.97 [0.77, 1.22] and 1.00 [0.82, 1.26]; balanced 132 and 90 rail-fJ. T's reads, with the warm-up fitted ([M]), say the same. So the A-side low bits read as 1× by every look I have, and no registered rule has said so. About 5 card-minutes of R blocks with a settling read in each would score it; A1's 15 minutes were spent.

## A fault in two lab tools: `make_e88` and `make_e92` start an op from C = fl((n−1) S)

**The fault.** `make_e88.simulate` and `make_e92.sign_counts` count an op from C = fl((n−1) S), S being one op's exact sum: the accumulator a launch would hold if it rounded only once, at the end. Their docstrings call that exact for integer and absorbed designs. It is not exact for fp16's absorbed designs, and it is not exact wherever two sums are equal or differ only by how they got there, because a real accumulation rounds at every addition. **On the 86 float tiles E88's fit and items, E90 and E92 rest on, it moves the model by up to 5.5 W on fp16 and 2.1 W the other way on fp32.** Every number here compares the two starts through one code path at the same four op indices, gate included. The watts are the two parts of the model the start moves, E88's price per result-bus bit and E92's per flop bit ([`fault_fl_ns_e102.txt`](../../../../tools/claims-v3/kinds/fault_fl_ns_e102.txt)).

| where | what the start misses | those parts of the model, start → real sums |
|---|---|---|
| **E92's fp16 tiles with subtracting and adding lanes side by side:** `h_sub`, `c_alt`, `hh_sub`, `hl_sub`, `s_abs` | fp16's accumulate rounds toward zero (`vpu_tensorfma.v:693`; `fp16_model.py`, which `fcheck_unit.py` checks against the RTL's `txfma_top`). So an absorbed product that subtracts takes one ulp off the sum at every micro-op, and one that adds takes none (`fp16_model.py` and `txfma_top` both read 0x57ffffff from C = 2^49 and ±1 products). The start holds those sums frozen and equal. By `accum.c` they part: `h_sub`'s two halves read 4.29e14 and 3.76e14 at op 199,875, and its C read, result bus and store move 89,084 bits an op, not 748 (104,888, not 272, at E92's own launch length). | **+5.54 W** on `h_sub` and `c_alt` (4.16 → 9.70 W at E88's 51.8 fJ per result bit), +5.06 on `hh_sub` and `hl_sub`, +4.37 on `s_abs` |
| **Near-identical fp32 operands:** E102's all-in low mantissa | A difference below the sum's rounding never reaches the sum. The start multiplies it by n−1, so it has two sums parting that stay equal. | **−2.07 W** at bit 6, where this run's whole step is 0.54 W (next table) |
| **One magnitude, mixed signs, products that round:** E90's `fp32.pm_pi` | The order of the signs decides the rounding, so sums the start holds equal are not. | +0.70 W |
| **The other 80 tiles** | | at most 0.12 W (`fp16.randn_small` −0.12, `fp32.r_het` −0.10, `fp16.uniform01` +0.10); 0.00 on integer sums and on fp32's absorbed designs |

E102's all-in fp32 B list over its zero, the second row:

| bit | C read + result bus + store, an op | adder flop bits | those parts of the model | whole step measured: E102 (board); E65 |
|---:|---:|---:|---:|---:|
| 0 | 15,538 → 0 | 31,900 → 12,288 | 0.96 → **0.09** W | 0.61 W; 0.63 W |
| 6 | 37,978 → 0 | 53,380 → 12,288 | 2.16 → **0.09** W | 0.54 W; 0.38 W |
| 11 | 57,823 → 21,888 | 72,282 → 37,037 | 3.22 → **1.29** W | 1.28 W; 1.10 W |
| 16 | 78,408 → 64,824 | 96,846 → 80,427 | 4.36 → **3.61** W | 2.78 W; 2.79 W |
| 20 | 94,907 → 97,142 | 124,329 → 123,656 | 5.33 → **5.43** W | 4.00 W; 3.97 W |
| 22 | 94,932 → 99,641 | 175,987 → 187,746 | 5.72 → **6.03** W | 4.99 W; 4.63 W |

It is gone by bit 20, where the sums really do part. e88+flops's frozen error on E102's all-in lists falls from 1.49 to 0.92 W (fp32 B) and from 1.60 to 0.89 W (fp16) on real sums (result 8).

**What it does to E92's fp16 reading: its watts stand, and "frozen" does not.** E92's own contrasts tell the two starts apart. Post hoc, at fp32's prices (E92's frozen 6.68 fJ per flop bit, the 30.0 fJ per result bit it read from fp32's moving sums), with nothing fitted on fp16 ([`fault_e92_fp16_e102.txt`](../../../../tools/claims-v3/kinds/fault_e92_fp16_e102.txt)):

| fp16, W on aifoundry3 | measured, dips removed | the two parts, from the start | from real sums |
|---|---:|---:|---:|
| `h_sub` − `h_add` (same operands) | 6.81 ± 0.25 | 3.79 | **7.88** |
| `c_alt` − `c_abs` (same operands) | 7.26 ± 0.21 | 4.34 | **8.43** |
| `h_allsub` − `h_add` (same operands) | 0.15 ± 0.20 | 0.02 | **0.04** |
| `hh_sub` − `c_abs` | 6.40 ± 0.42 | 3.55 | **6.96** |
| `hl_sub` − `c_abs` | 5.50 ± 0.24 | 2.22 | **5.63** |
| `s_abs` − `c_abs` | 4.59 ± 0.12 | 2.34 | **5.22** |
| `signs` − `s_abs` | 0.39 ± 0.20 | 2.49 | **−0.38** |
| `hh_sub` + `hl_sub` − `h_sub` − `c_abs` | 4.61 ± 0.51 | 1.71 | **4.43** |

Over all ten contrasts in the file, rms 2.55 W from the start and **0.68 W from real sums** (2.53 and 0.53 at 16 op indices). Real sums read 1.1–1.2 W high on the two alternating contrasts with the same operands, and miss `signs` − `s_abs` by 0.77 W, so this shows the shape and the size; it is not a model. E92's own post-hoc fit, the same tiles, the same D, only the start changed ([`fault_refit_e102.txt`](../../../../tools/claims-v3/kinds/fault_refit_e102.txt); the control through this code reads as E92's own fit does):

| "four prices + flops" | fp16, start | **fp16, real sums** | fp32, start | fp32, real sums |
|---|---:|---:|---:|---:|
| rms; leave-one-out, W | 0.486; 0.578 | **0.239; 0.297** | 0.286; 0.322 | 0.271; 0.306 |
| E86's real tiles, held out, rms W | 0.526 | **0.169** | 0.193 | 0.204 |
| fJ per result bit | 5.5 | **33.7** | 26.3 | 26.0 |
| fJ per adder-flop bit | 10.8 | **4.8** | 7.7 | 7.6 |
| at 16 op indices: rms; result; flop | 0.481; 5.9; 10.8 | 0.229; 34.3; 5.0 | 0.288; 26.5; 7.6 | 0.273; 26.2; 7.6 |

So, as readings (the counts are the RTL's arithmetic; **C was read back on no card**, and the harness's `result` field is "unchecked"):

- E92 says fp16's moving part is 5.8 fJ per result bit against fp32's 30.0, and calls the gap unexplained. The bits were miscounted. Refit, the prices are 33.7 and 26.0 fJ.
- E92 says about 92% of fp16's sign step remains with the sum frozen. `fp16.s_abs`'s sum is not frozen: all 256 accumulators leave the start's value, onto nine distinct words. So that share does not separate fp16's mechanisms.
- E92 says `hh_sub` and `hl_sub` each cost 75–88% of `h_sub`, so they do not add. All three share one walk, with one result-bus count, because an absorbed product that subtracts costs one ulp, high or low. At fp32's prices that gives hh + hl − both at +4.43 W against the measured +4.61 ± 0.51 (E92's adder-bit count said +1.77).
- E92 says fp16's alternation is dearer, 1.55× fp32's. fp16's `h_sub` − `h_add` exceeds fp32's by 2.42 W, and the walk alone is priced at 2.7–3.3 W at fp32's 30.0 fJ. In E92's alternations model the price falls from 740 to 291 fJ an alternation (fp32 851).

**Who else rests on it.** E103-R3's null is that fit, with its counts on E103's tiles from the start ([`fault_e103_null_e102.txt`](../../../../tools/claims-v3/kinds/fault_e103_null_e102.txt), E103's own D, M and bootstrap). With both from real sums the null reads 1.694 W, not 1.775, over the 23 float tiles, and 0.723 W, not 1.006, on fp16's 10, against the model's 0.162. **R3 still passes**: the gap is +1.380 [+0.242, +2.522] W. Without the denormal tile, where E103 says "PASS, narrowly", the null reads 0.705 W, not 0.913, against the model's 0.320, and the gap is +0.385 [+0.202, +0.571] W, not +0.593 [+0.255, +0.944]. E103's verdicts are its lane's to re-read; this only sizes them.

**What stands.** E88's fit: at most 0.12 W on any of its tiles. E92's flop price and its fp32 fit (result 26.3 → 26.0, flop 7.7 → 7.6 fJ). E92's R8 premium (`wr_h_sub` − `wr_h_add` flops 156,772 → 156,559). E90, but for `pm_pi`. int8, whose sums are integers. The RTL bench, which starts from `accum.c`'s sums: a reading, that is one reason it called this list, and fp16's hh/hl overlap, where the stream model did not.

**What to use.** For any float tile, `fault_fl_ns_e102.counts`: real sums, the gate honoured, and for fp16 `step=fp16_model.model`. `make_e102.exact_counts` has real sums and no gate, which E102's tiles do not need. Not done: reading C back after a launch of `fp16.h_sub`, which is what would settle this on a card (the RTL bench's README asks for the same read-back: its fp16 reference is a model read off the RTL, not silicon), and refitting E88 on real sums.

**Three smaller things beside it.**

1. `make_e92.sign_counts` ignores the zero gate: flops on `fp32.nn_like` 327,599 against 168,911 with it (+1.19 W at E92's price), on `fp16.nn_like` 372,106 against 299,137 (+0.55 W). E92's own tiles have no zero word, and `posthoc_fit_e92.py` already honours the gate.
2. On integer sums a count depends on where its op indices fall against powers of two. `w_h_sub`'s result bus is 127,365 at 16 op indices over make_e88's launch of 533,000, 137,190 at 4 (+0.46 W at E88's price), and 109,025 at 16 over make_e92's 542,000 (−0.85 W for a launch 1.7% longer). `w_h_add` moves with it, so the 16-against-4 change cancels in E92's `w_h` contrast, and the launch change moves that contrast by +0.21 W. So one such tile's absolute count is good to about 1 W at best.
3. The two counted ops add as `make_e88` does, in ordinary rounding, not fp16's. With fp16's own arithmetic `h_sub` reads 96,498 bits and 602,950 flops, not 89,084 and 600,240; `s_abs` 79,726 bits, not 71,292; `randn` barely moves (127,018, not 127,011). So the real-sum counts above are 8–12% low on the walking tiles (`fault_e92_fp16_e102.txt` part C).

*Corrected on the way:* a first version of this comparison set `simulate`'s count (gated, 16 op indices) against `exact_counts`'s (ungated, 4) and read +2.6 W on `nn_like`. That was items 1 and 2, not the start. And a first draft of this section, on 19 tiles and never committed, said at most 0.04 W outside E102's list: it had not reached E92's fp16 tiles. Widening the list to every tile is what found them.

## Registered against happened

| rule | registered | happened, primary arm | verdict, primary arm | other arm |
|---|---|---|---|---|
| E102-R1 B ratio by position | POSITION: upper bound < 4 at bits 0, 6; lower ≥ 4 at 22 | rail 0.92 [0.60, 1.49], 1.01 [0.67, 1.73]; 5.90 [5.11, 6.97] | **POSITION** | board POSITION |
| E102-R2 A ratio by position | POSITION: the same, lower ≥ 1.2 at 22 | rail 1.12 [0.83, 2.41], 1.02 unbounded; 2.20 [1.96, 2.53] | **INCONCLUSIVE** | board INCONCLUSIVE (bit 6 upper 4.63) |
| E102-R2a (A1) the same, on R | POSITION | 1 block kept of 4 | **NOT SCORED** | board NOT SCORED |
| E102-R3 exponent inverts | INVERTED: balanced − all-in lower > 0 at 23, 27 | +0.909 [0.815, 1.003]; +1.164 [1.079, 1.248] | **INVERTED** | board INVERTED |
| E102-R4 sign alternates | three legs above floors | fp32 B lower 0.867 against 1.0; fp32 A, fp16 B CONFIRMED | **INCONCLUSIVE** | board CONFIRMED |
| E102-R5 ties to E79 (board) | inside bands | 4 CONFIRMED, 2 INCONCLUSIVE, 0 REFUTED | **INCONCLUSIVE** | |
| E102-R6 train = gate | pooled inside ±0.15 W rail | −0.035 [−0.188, 0.119] | **INCONCLUSIVE** | board CONFIRMED |
| E102-R7 flops' share (board) | in [0.15, 0.50] at 16, 20, 22 | 0.22, 0.24, 0.29 | **CONFIRMED** | rail CONFIRMED |
| E102-R8 int8 level | open | 29.7 [27.7, 31.6] rail-fJ | **BENCH-LEVEL** (< 35); see result 6 | board RESOLVED-BETWEEN |
| E102-R9 odd/even | open | +0.136 [0.111, 0.161] W | **SHAPE** | board INCONCLUSIVE |
| E102-R10 rise | open | +0.064 [0.048, 0.079] W | **RISE** | board INCONCLUSIVE |
| E102-R11 additivity | inside ±0.15 W | −0.058 [−0.144, 0.027] | **CONFIRMED** | board INCONCLUSIVE |
| E102-R12 singles | reported | 8 of 8; ±15 against ±29 rail-fJ | reported | board 7 of 8; ±32 against ±70 |
| E102-S1 session tie | within bands | all four inside | **PASS** | FAIL at 0.545, 0 only |

**Of the eleven registered rules with a verdict: 6 decided as registered or expected (R1, R3, R7, R11 and the open R9, R10), R8 decided with the footnote in result 6, 4 INCONCLUSIVE (R2, R4, R5, R6), none refuted.** A1's own R2a is not scored. No verdict moves at any registered arm (dips kept, E78's gates off, each slope, `check_e102.txt` [C]), and S1 fails only at 0.545 and 0.

## Interpretation (labelled: a reading, not measured)

- **Rounding.** A real fp32 accumulation adds a product to a sum about 2²³ times its size late in a launch, so only the product's top bits reach the sum. Two addends that differ below that round to the same increment, so the sums stay identical. This is `accum.c`'s behaviour, the bench's and the desk's, and it fits the card: ratio 1 where the count says the sums are equal, and rising where it says they part. E102 did not read C back.
- **The int8 list's shape looks like a radix-4 recoder on B.** An odd bit enters two digits and an even bit one, which predicts about 2×; a mask's cost then follows the digits it touches rather than its bits: 0x15 3 of 3 (measured 1.05 of its singles), 0x2A 4 of 6 (0.73). It predicts too little for the nibble masks (0.50 against 0.69, 0.72) and for `bk_ff` (0.42 against 0.63), and bit 6 is above its even neighbours ([F]; written after the data). The public RTL says only `*`; which gates the netlist has is not something E102 can see, and no public source was found to settle it.

## What it changes

- **Item 12's first half: closed for fp32 B's position question, for the B-side exponent (R3), and for int8 B on this card; narrowed for fp32 A's low bits (R2 undecided, every look reads 1×) and for the sign (R4: board yes, rail short of its floor on one leg).** Left open: those two rules, and every position not run.
- **The page's "the other 30 positions as composites" has to go.** Measured: 1× at bits 0 and 6, 3× at 11, about 6× at 16–22 on B; on A about 1× at 0, 6, 11, then 7, 3, 2× at 16, 20, 22. E65's and E67's prices at the low mantissa are the flip.
- **E79's "a bit price travels as a pair" holds, but the pair's meaning changes with the field:** at the exponent and sign, the balanced half is the dearer, and a different composite.
- **E79's result 4b and its int8 B list stand**, at no temperature term, on a second card; the withdrawn "at E71's slope the pattern vanishes" was the reading.
- **E92's fp16 reading has to be looked at again** (§ A fault): its watts stand, its "frozen" and its unexplained 5.8 against 30.0 fJ do not. E102 does not edit E92's record.
- **E92's fp16 reading has to be looked at again** (§ A fault): its watts stand, its "frozen" and its unexplained 5.8 against 30.0 fJ do not. E102 does not edit E92's record.
- **Item 6 (a model for every kind):** the bench, frozen, predicts single-bit steps on tiles and a card it never saw at 0.15–0.26 W rms in fp32 and fp16. int8 needs more than the bench's `*`.

## Caveats

One card, one clock, 499 mV. **One base word per side**: on A a ratio depends on the word's neighbouring bits, so A's non-monotonic list is this word's. Ten of 32 fp32 positions, six of fp16's on two sides, and nothing is interpolated here. Three kept passes in T (t = 4.30), four or five in G, so a board interval in T is wide. A ratio across protocols (bits 16 and 20) inherits R6's unresolved ±0.2 W. The train's own-zero interpolation under-reads the first quarter of a float train, which raises T's steps by a few hundredths of a watt on average (compare `primary` with [M]). A rail price is about 0.80 of a board price here (23 steps of 1 W or more, 0.71–0.87, [K]). The counts are the desk's and the bench's: C was not read back.

## Departures and disclosures

1. **The trains' own gate fired twice on what it was not meant to catch.** It was registered as about 5σ on a steady train. A float train is not steady: the same read departs +0.19 W in passes 10220–22 and +0.277 W in 10223 ([A]), and R's first reads depart as § What amendment A1 settled says. The gate ran as registered each time. Nothing was reinstated; [D], [M] and [Q] show what it would add, labelled.
2. **A1 was written after session 1's numbers were read.** Its G blocks are driven by a gate outcome, its thresholds are R2's, and it moves no rule; but it is not blind, and its readers should know.
3. **10214 is a short G** (six items, not the registered list), as A1 says, so that a repeated skip could not leave R3 and R4 short again. Its reads count in the G means for those items only.
4. **The launch rule skipped four runs in G** (E78's rule, unchanged: the reading rose back above the target during the quiet). Registered consequence: that item has one pass fewer.
5. **The rail as primary was chosen on E93's low-power gate noise**, and registered before anyone had seen a float train; see result 10. In int8 it was right.
6. **Budget.** The brief said about 45 card-minutes, 57 were registered, session 1 took 55 and its queue 48. A1 was limited to 15, and took 14.7 from claim to release.
7. **E82's anchors ran once in each full G block and not in a train**, against the brief's "in every pass", as registered: a random tile in a train is a heater.
8. **No interim look at power.** The waits read the queue log, pace, clocks and records. Both smokes were read for cycles per op, dumps and config only.
9. **The collection ran on the mini** (`collect_e102.sh`, unchanged, numpy through `uv`, with the glob `p102[1-4][0-9]`), because the Intel was overloaded. Its paths in the committed text files were then rewritten to the raw data's committed location; no number changed. `check_e102.py` and `score_e102a1.py` run on the committed result.
10. **E102.md's bench predictions** use the Q132(b) lane's bench and maps as built on the mini at 01:44 PDT; the back-test's counts of E65's, E67's and E79's tiles are that lane's (`bench/backtest-hl-hlp.json` records their sha256; `bench/distill_backtest.py`).
11. **Post hoc, labelled, no rule depends on them:** `check_e102.py` sections [D], [E]'s means, [F]'s digit counts, [L] (an independent crude reading from raw telemetry: median board and mean rail, which matches the scored steps within their intervals except where the warm-up lifts the crude flat zero: `bp_22` 0.909 against 0.630 W, `bp_11` 0.665 against 0.388 W), [M] and [Q].

## Files

`README.md`; `e102.json`, `runs.csv`, `reduce.txt` (the primary reduction); the arms `e102-dipskept`, `e102-gatesoff`, `e102-auto`, `e102-leak0.1994 / 0.3803 / 0.545 / 0` (`.json`, `runs-*.csv`, `reduce-*.txt`); `scored.json`, `results.md` (every rule, price, ratio, model and arm); `scored-a1.json`, `results-a1.md` (R2a); `check_e102.py`, `check_e102.txt`; `code.sha256`; `logs/` (the queue logs, dry runs, final config reads); `bench/` (`counts-e102.json`, `backtest-hl-hlp.json`, `distill_backtest.py`, frozen with the registration); `aifoundry1-c1/kinds/p102*` (raw blocks: telemetry, marks, records, tile dumps, config reads, code hashes; the smokes as `kinds-smoke-p10201`, `-p10202`). The tiles, registration and code: `tools/claims-v3/kinds/` (`E102.md`, `e102/`, `predictions-e102.json`, `make_e102.py`, `make_predictions_e102.py`, `e102_common.py`, `run_e102.py`, `block_e102.sh`, `queue_e102.sh`, `run_e102.sh`, `reduce_e102.py`, `score_e102.py`, `collect_e102.sh`, `selftest_e102.py`, `desk_noise_e102.py`; A1's `e102a1_common.py`, `block_e102a1.sh`, `queue_e102a1.sh`, `score_e102a1.py`, `selftest_e102a1.py`, `desk_a1_e102.py`; the fault's `fault_fl_ns_e102`, `fault_refit_e102`, `fault_e92_fp16_e102`, `fault_e103_null_e102`, each `.py` and `.txt`).
