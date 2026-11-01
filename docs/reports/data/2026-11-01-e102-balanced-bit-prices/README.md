# E102: single-bit prices in a balanced layout, the A side, and int8's B side (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132, the first half of item 12 of the kinds page's section 11. Pre-registered in `47060961` (committed 01:25:56 PST and pushed by 01:26:02, before the claim and the first launch):
[`tools/claims-v3/kinds/E102.md`](../../../../tools/claims-v3/kinds/E102.md), frozen numbers in `predictions-e102.json`, tiles and counts in `e102/e102.json`, the scorer `score_e102.py` and its self-test in the same commit, the RTL bench's counts of the frozen tiles in [`bench/`](bench/).
aifoundry1 card 1 (`V3_DEVICE=1`) at 600 MHz, 499.0 mV mean; TDP 65, threshold 65 °C, 600 MHz and 499 mV read under the card lock at both ends of the smoke and of every block, and again at 02:22:17 PST; never set. Nothing was written to the card, and no `--reset-ms` was sent.
Claim `1566383041881055233` in #community-lab, posted 01:26:59 PST ("for 1.5 h, until ~02:56 PST"), released at 02:22 PST by editing it (55 min). Smoke 10201 from 01:27 PST. Queue 01:33:02–02:21:04 PST, 2,882 s, inside the registered 3,400 s.*

**What ran.** 72 tiles built on E79's own base words (`fp32.bj_22`, `bp_22`, `fp16.bj_*`, `bp_9` and every int8 single are byte-identical to the tile E79's host dumped). Twelve blocks, 470 runs, none failed a gate:
**G** (10210–12), E78's launch at 58 °C after 59 °C and 2 s quiet, for steps near or above 2 W and four ties; **T** (10220–23), a train of float runs with no heater and a 0.2 s gap, 4.86 s a run against the gate's 6.7 s; **I** (10230–34), the same in int8.
**Two runs were skipped by the launch rule** (the reading came back to 59 °C during the quiet: `fp32.bj_31` in 10210, `fp32.bp_23` in 10211), and **the trains' own gate set pass 10223 aside** (a zero read 0.277 W off the line through its neighbours on the rail, limit 0.25 W; § Departures). So the primary reduction keeps G 3, T 3, I 5, and those two items have two passes. A price is a step over the item's own zero (a constant-operand tile, interpolated in time) divided by the item's own designed flips per op and the run's rate, per pass; intervals are 95% over passes, t(0.975, n−1) × SE. Board and minion rail are both printed; the rail is the registered primary arm except where named. Numbers below are from `scored.json` › `primary` unless a section of [`check_e102.txt`](check_e102.txt) is named.

## Results

**In plain words.** A low mantissa bit costs the same whether or not the accumulators are balanced: E65's and E67's low floor is the flip itself, not a composite. The composite appears between bits 11 and 16 and reaches about 6× at the top of the B-side mantissa. By the frozen counts on real accumulators, that is because a low-bit difference is rounded away inside a large sum and never makes two accumulators differ. A balanced mantissa flip costs about the same at every position (87–164 fJ on B). At the exponent and the sign the order reverses: the balanced layout is 2–5× dearer, because the aligner or the adder's add/subtract now moves. int8's B list resolves on the rail: odd bits cost 2.9× even bits, E79's shape, on a second card. **The fixed RTL bench, frozen before the data, called all of the float shape; it undercounts int8's single bits, as a behavioural `*` must.**

**1. The ratio depends on position.** Per flipped bit, all-in (E65's and E67's constructions) over balanced, fp32 (`check_e102.txt` [C], [G]). `all-in` and `balanced` are board fJ, primary reduction, from the block the item is listed in.

| bit | field | B all-in, fJ | B balanced, fJ | **B ratio, board** | B ratio, rail | bench, frozen | A all-in, fJ | A balanced, fJ | **A ratio, board** | A ratio, rail | bench, frozen |
|---:|---|---:|---:|---|---|---:|---:|---:|---|---|---:|
| 0 | mant | 133 [114, 152] | 152 [96, 208] | **0.87** [0.55, 1.57] | 0.92 [0.60, 1.49] | 1.00 | 176 [90, 262] | 137 [42, 232] | **1.29** [0.99, 2.45] | 1.12 [0.83, 2.41] | 1.00 |
| 6 | mant | 119 [82, 156] | 113 [106, 120] | **1.05** [0.70, 1.43] | 1.01 [0.67, 1.73] | 1.00 | 113 [75, 151] | 105 [17, 193] | **1.07** [0.74, 4.63] | 1.02 (unbounded) | 1.00 |
| 11 | mant | 279 [263, 295] | 87 [76, 98] | **3.20** [2.92, 3.56] | 2.46 [2.27, 2.68] | 2.79 | 481 [383, 580] | 332 [306, 358] | **1.45** [1.20, 1.68] | 1.37 [1.02, 1.80] | 1.29 |
| 16 | mant | 614 [563, 665] | 105 [68, 142] | **5.86** [4.28, 9.09] | 5.82 [3.75, 12.51] | 4.35 | 594 [527, 660] | 83 [72, 95] | **7.14** [5.99, 8.57] | 7.93 [6.46, 9.46] | 4.27 |
| 20 | mant | 871 [791, 951] | 164 [105, 224] | **5.31** [3.83, 8.39] | 5.09 [3.25, 11.35] | 4.63 | 1,021 [871, 1,170] | 317 [268, 366] | **3.22** [2.60, 4.00] | 3.59 [2.38, 6.30] | 3.05 |
| 22 | mant | 1,091 [1,043, 1,139] | 142 [125, 159]; gate 188 [112, 264] | **5.80** [4.30, 9.33] (gate/gate) | 5.91 [4.58, 8.32] | 6.81 | 1,405 [1,277, 1,533] | 597 [438, 755]; gate 649 [511, 787] | **2.16** [1.78, 2.73] (gate/gate) | 2.19 [1.79, 2.96] | 1.97 |
| 23 | exp | 205 [136, 275] | 465 [325, 605] (2 passes) | **0.45** | 0.46 | 0.28 | 210 [155, 265] | 408 [355, 461] | **0.52** | 0.53 | 0.41 |
| 27 | exp | 140 [83, 197] | 473 [432, 513] | **0.30** | 0.28 | 0.16 | 143 [48, 237] | 461 [431, 490] | **0.31** | 0.38 | 0.20 |
| 30 | exp | 181 [162, 200] | 382 [312, 453] | **0.47** | 0.44 | 0.41 | 182 [152, 211] | 462 [433, 492] | **0.39** | 0.38 | 0.41 |
| 31 | sign | 94 [−390, 578] (2 passes; a bound) | 537 [450, 624] | **0.18** | 0.19 | 0.25 | 129 [37, 221] | 711 [594, 827] | **0.18** | 0.20 | 0.19 |

**E102-R1, the rule the brief named: POSITION**, on both arms. At bits 0 and 6 the upper bounds are below the registered 4 (rail 1.49 and 1.73), and at bit 22 the lower bound is above it (rail 4.58). The page's implied 5–7× holds at bits 16–22 and not below: it is 1× at 0 and 6 and 3× at 11. **E102-R2, the same on A: INCONCLUSIVE** on both arms, on one cell: at bit 6, `ap_6`'s rail step is itself a bound (0.167 [−0.051, 0.384] W), so the rail's ratio is unbounded, and the board's upper bound is 4.63 against the rule's 4. Every other A cell reads like B's (with the pass the gate set aside and the warm-up fitted, post hoc, labelled, [M]: board 1.17 [0.71, 1.93] and 0.88 [0.50, 1.68] at bits 0 and 6; not a verdict).

The A list is not monotonic, and the bench said so first: 7.1× at bit 16, 3.2× at 20, 2.2× at 22 against its frozen 4.3, 3.1, 2.0. A is the Booth multiplier, so `ap_22` and `ap_20` move partial products in a balanced layout too (bench: multiplier stage 0.71 M of 0.83 M net toggles an op at bit 22), and they depend on the one base word's neighbouring bits. Over all ten positions Spearman(bench, measured) is 0.96 on B and 1.00 on A ([G]).

**2. Balanced mantissa flips are nearly flat; what rises is the accumulators' swing.** B-side balanced: 152, 113, 87, 105, 164, 142 fJ at bits 0, 6, 11, 16, 20, 22 (a factor of 1.9), where the all-in list runs 133 to 1,091 ([O]). E79's one point, 150 fJ on aifoundry3, is the level of the whole list. Counted on the real accumulators ([I], `e102/e102.json` › `exact`, frozen before the data): `jg`'s C read changes 0 bits an op over the zero at bits 0 and 6, 10,952 at 11, 32,492 at 16, 48,892 at 20, 49,908 at 22. Those are the positions where the ratio leaves 1. **So E65's floor from the LSB to about bit 9, and its rise above it, read as one mechanism: where the sum still registers the difference** (a reading: the count is the desk's and C was not read back; § Interpretation).

**3. What a composite is, now that E92 has priced the adder's flops.** **E102-R7 CONFIRMED** on both arms: at E92's frozen 6.68 fJ per flop bit, the adder's flops carry **22%, 24% and 29%** of the all-in excess at bits 16, 20 and 22 (board; 0.51, 0.78, 1.27 W of 2.34, 3.25, 4.36 W; band 0.15–0.50). If the flops carried it all they would cost 23–31 fJ a bit. So a composite price is: the flip's own path, about 100–150 fJ at any mantissa position; plus the swing between two sums that differ, in the bits where they differ, of which the adder's flops at E92's price are about a quarter. The frozen bench puts the rest in the normaliser and adder nets beyond those flops, the C register file, the exponent path and the multiplier (at bit 22, 2.30 M net toggles an op over the zero: adder and normaliser 1.34 M, multiplier 0.22 M, C register file 0.15 M, exponent 0.15 M).

**4. The exponent and the sign reverse.** Balanced − all-in, watts, rail [board] ([C]):

| | fp32 B bit 23 | fp32 B bit 27 | fp32 B sign | fp32 A bit 23 | fp32 A bit 27 | fp32 A sign | fp16 B sign |
|---|---|---|---|---|---|---|---|
| rail | +0.871 [0.770, 0.972], 2 passes | **+1.195** [1.008, 1.381] | +1.817 [−3.6, 7.2], 2 passes | **+0.318** [0.199, 0.436] | **+0.459** [0.261, 0.657] | **+0.939** [0.758, 1.120] | **+1.244** [1.037, 1.451] |
| board | +1.116 [0.124, 2.108] | +1.458 [1.378, 1.537] | +1.903 [1.247, 2.559] | +0.395 [0.345, 0.446] | +0.664 [0.419, 0.909] | +1.233 [0.905, 1.560] | +1.569 [1.433, 1.705] |

**E102-R3: NOT SCORED**, as the rule requires: the launch rule skipped `bp_23` once, so that leg has two passes. **E102-R4: INCONCLUSIVE**: its fp32 A and fp16 B legs are CONFIRMED above their floors, and its fp32 B leg is not scored for the same reason (`bj_31`). No leg is refuted. Every point estimate in both rules' cells is the sign the registration predicted, and nothing reads like a mantissa's composite (ratios 0.18–0.53). This answers E79's result 1b: an exponent flip is cheap in `jg` because the product and the accumulator it lands on move together, so the aligned operand does not change (0 flop-bit changes over the zero, frozen). In a balanced layout the product alternates against a sum that does not, and the aligner shifts every micro-op (about 156,000–166,000 flop-bit changes an op). A balanced sign makes the sum cancel, so the adder alternates (2,048 alternations an op, E92's mechanism). So "all-in / balanced" is a discount only for the mantissa. **Which price a workload pays at an exponent or sign bit depends on whether its sums follow its products.**

**5. fp16 reads the same way** ([N]): all-in over balanced 1.98 [1.38, 3.45] at bit 0, **4.70 [3.90, 6.13]** at bit 9 (E79 on aifoundry3: 5.6), 0.37 [0.20, 0.62] at exponent bit 12, 0.29 [0.21, 0.35] at the sign; on A, 2.49 [2.30, 2.68] at bit 9, 0.49 [0.11, 1.10] at bit 12. The bench's frozen ratios: 2.18, 4.70, 0.29, 0.24; 2.39, 0.33. fp16 bit 0 is already 2×, where fp32 bit 0 is 1×, because fp16's whole mantissa sits high in the 32-bit sum. Balanced fp16: 108, 118 (gate 109), 183, 250 fJ on B at 0, 9, 12, 15; 278 (gate 244), 224 on A at 9, 12.

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
- **E102-R8: BENCH-LEVEL as registered, and that label needs its footnote.** `bk_ff`, all eight bits flipping together, is **29.7 [27.7, 31.6] rail-fJ per flipped bit** (board 34 [23, 46], RESOLVED-BETWEEN), under the registered 35. But the singles average **47 [38, 57] rail-fJ**, E79's level, not the bench's. **E102-R11 CONFIRMED** only that `bk_ff` adds up from its nibbles (−0.058 [−0.144, 0.027] W); against its eight singles it is **0.63 [0.53, 0.77]**. So the rule's premise, that all eight bits read the singles' level, fails: flips share their cost. The bench undercounts a single flip 4–5× (10 against 47 rail-equivalent at the float coefficients, about 2× at its int8 fit, and the shape not at all). That is expected of the RTL's behavioural `$signed(a) * $signed(b)` (`tima/tima_top.v:89`): the bench sees the product, not partial products.

**7. The leakage slope no longer moves it.** The trains read no temperature, because E79's B level moved with the reading's whole-degree steps, not with the card ([`desk_noise_e102.txt`](../../../../tools/claims-v3/kinds/desk_noise_e102.txt)). Reduced E79's way, with each run's own reading in the train, `bk_ff` stays a coefficient at every slope, 29–34 fJ (`results.md`), but single bits still move: 3 of 8 become bounds at 0.2414, 0.3803 and 0.545 W/°C, and bit 6 goes 52 → 1 fJ at 0.545 ([F]). With no temperature term, 1 of 8 on the board and 0 of 8 on the rail. Leakage's feedback on a train's pair is at most 7% (0.545 W/°C × 0.13 °C/W), stated, not corrected.

**8. The models** (`results.md`; board, rms over each list, watts; frozen before the data):

| list | the page's ratio | bench `nets_map` | E65/E67/E79's published list | e88+flops on real sums | e88+flops as E92 counted |
|---|---:|---:|---:|---:|---:|
| fp32 B balanced (11) | 1.229 | **0.254** | | 0.970 | 0.980 |
| fp32 B all-in (10) | | 0.238 | **0.213** | 0.916 | 1.481 |
| fp32 A balanced (11) | 0.779 | **0.197** | | 0.983 | 0.969 |
| fp32 A all-in (10) | | **0.210** | 0.292 | 0.301 | 0.618 |
| fp16 balanced (8) | 1.080 | **0.147** | | 0.769 | 0.778 |
| fp16 all-in (6) | | 0.247 | **0.219** | 0.886 | 1.604 |

The bench's frozen prediction beats every alternative on the balanced lists and ties the published lists on the all-in ones, on a card and a base it never saw, at about the board's noise. For int8 B (13 items, rail): int8 fit 0.077, E79's list 0.091, the float coefficients 0.134, E88's model 0.142 W. `make_e88`'s and `make_e92`'s start, C = fl((n−1) S), which their files call exact for integer and absorbed designs, overcounts `jg` on a random significand (`bj_6`: 20,009 C-read bits an op against 0 on real sums, [I]); real sums cut e88+flops's all-in error by about 40% and leave it well behind the bench.

**9. The session tied.** E102-S1 PASS: `fp32.randn` −0.05 W, `fp16.randn` +0.14 W, `anchor_pi` −0.13 W, `int8.full` +0.07 W from E82's dips-removed values (FAIL only at the 0.545 and 0 W/°C arms, which carry another slope than E82's, as in E86, E90 and E93). **E102-R5 INCONCLUSIVE**: 4 of 6 ties to E79 CONFIRMED (`bj_22` 1,091 [1,043, 1,139] fJ against 1,021 carried over; `fp16.bj_9` 513; both ratios), 2 INCONCLUSIVE (`bp_22` 188 [112, 264], `fp16.bp_9` 109 [76, 143]: wide intervals over the band's edge at three G passes), 0 REFUTED. Checks: cycles per op 546.001 / 546.001 / 318.0; duty 0.996; 124 meter-dip samples removed over twelve blocks; rail lag re-fitted 0.95 s; carry-over −0.0007 ± 0.0018 W/W.

**10. What the trains gave, and what they did not.** In int8 they did what they were for. A float train is not steady: the die reads about 57 °C at its first run and 61–62 °C at its last ([J]), and its zeros rise along a curve of about 2 W amplitude, τ about 45 s ([M]). Straight lines through the zeros under-read the first quarter. And the rail, the registered primary, remembers the previous run's step in a train: about the zeros' curve its scatter is 0.10 W a run, against the board's 0.04–0.09 W ([M]). So for floats the registered primary arm was the worse one, and R1's verdict stands on both. **E102-R6 INCONCLUSIVE on the rail by 0.004 W** (train − gate pooled over four items −0.026 [−0.205, 0.154] W against ±0.15), CONFIRMED on the board (−0.025 [−0.229, 0.178] against ±0.30). The train and the gate read the same within those intervals; item by item, `fp16.ap_9` differs by +0.122 [0.064, 0.180] W on the rail.

## Registered against happened

| rule | registered | happened, primary arm | verdict, primary arm | other arm |
|---|---|---|---|---|
| E102-R1 B ratio by position | POSITION: upper bound < 4 at bits 0, 6; lower ≥ 4 at 22 | rail 0.92 [0.60, 1.49], 1.01 [0.67, 1.73]; 5.91 [4.58, 8.32] | **POSITION** | board POSITION |
| E102-R2 A ratio by position | POSITION: the same, lower ≥ 1.2 at 22 | rail 1.12 [0.83, 2.41], 1.02 unbounded; 2.19 [1.79, 2.96] | **INCONCLUSIVE** | board INCONCLUSIVE (bit 6 upper 4.63) |
| E102-R3 exponent inverts | INVERTED: balanced − all-in lower > 0 at 23, 27 | bit 23 two passes; bit 27 +1.195 [1.008, 1.381] | **NOT SCORED** | board NOT SCORED |
| E102-R4 sign alternates | three legs above floors | fp32 B not scored; fp32 A, fp16 B CONFIRMED | **INCONCLUSIVE** | board the same |
| E102-R5 ties to E79 (board) | inside bands | 4 CONFIRMED, 2 INCONCLUSIVE, 0 REFUTED | **INCONCLUSIVE** | |
| E102-R6 train = gate | pooled inside ±0.15 W rail | −0.026 [−0.205, 0.154] | **INCONCLUSIVE** | board CONFIRMED |
| E102-R7 flops' share (board) | in [0.15, 0.50] at 16, 20, 22 | 0.22, 0.24, 0.29 | **CONFIRMED** | rail CONFIRMED |
| E102-R8 int8 level | open | 29.7 [27.7, 31.6] rail-fJ | **BENCH-LEVEL** (< 35); see result 6 | board RESOLVED-BETWEEN |
| E102-R9 odd/even | open | +0.136 [0.111, 0.161] W | **SHAPE** | board INCONCLUSIVE |
| E102-R10 rise | open | +0.064 [0.048, 0.079] W | **RISE** | board INCONCLUSIVE |
| E102-R11 additivity | inside ±0.15 W | −0.058 [−0.144, 0.027] | **CONFIRMED** | board INCONCLUSIVE |
| E102-R12 singles | reported | 8 of 8; ±15 against ±29 rail-fJ | reported | board 7 of 8; ±32 against ±70 |
| E102-S1 session tie | within bands | all four inside | **PASS** | FAIL at 0.545, 0 only |

**Of the eleven rules with a verdict: 5 decided as registered or expected (R1, R7, R11 and the open R9, R10), R8 decided with the footnote in result 6, 4 INCONCLUSIVE (R2, R4, R5, R6), 1 NOT SCORED (R3), none refuted.** No verdict moves at any registered arm (dips kept, E78's gates off, each slope, `check_e102.txt` [C]), and S1 fails only at 0.545 and 0.

**What would finish them.** R3 and R4 want one more G block (5.6 min), which reads `bp_23` and `bj_31` a third time; R2 wants T blocks with the warm-up handled. Neither was run: a run for them needs its own dated amendment and claim.

## Interpretation (labelled: a reading, not measured)

- **Rounding.** A real fp32 accumulation adds a product to a sum about 2²³ times its size late in a launch, so only the product's top bits reach the sum. Two addends that differ below that round to the same increment, so the sums stay identical. This is `accum.c`'s behaviour, the bench's and the desk's, and it fits the card: ratio 1 where the count says the sums are equal, and rising where it says they part. E102 did not read C back.
- **The int8 list's shape looks like a radix-4 recoder on B.** An odd bit enters two digits and an even bit one, which predicts about 2×; a mask's cost then follows the digits it touches rather than its bits: 0x15 3 of 3 (measured 1.05 of its singles), 0x2A 4 of 6 (0.73). It predicts too little for the nibble masks (0.50 against 0.69, 0.72) and for `bk_ff` (0.42 against 0.63), and bit 6 is above its even neighbours ([F]; written after the data). The public RTL says only `*`; which gates the netlist has is not something E102 can see, and no public source was found to settle it.

## What it changes

- **Item 12's first half: closed for fp32 B, for int8 B on this card; narrowed for fp32 A and for the exponent and sign**, whose point estimates all read as predicted but whose rules R2, R3, R4 are not decided as registered. Left open: those three rules, and every position not run.
- **The page's "the other 30 positions as composites" has to go.** Measured: 1× at bits 0 and 6, 3× at 11, about 6× at 16–22 on B; on A about 1× at 0, 6, 11, then 7, 3, 2× at 16, 20, 22. E65's and E67's prices at the low mantissa are the flip.
- **E79's "a bit price travels as a pair" holds, but the pair's meaning changes with the field:** at the exponent and sign, the balanced half is the dearer, and a different composite.
- **E79's result 4b and its int8 B list stand**, at no temperature term, on a second card; the withdrawn "at E71's slope the pattern vanishes" was the reading.
- **Item 6 (a model for every kind):** the bench, frozen, predicts single-bit steps on tiles and a card it never saw at 0.15–0.25 W rms in fp32 and fp16. int8 needs more than the bench's `*`.

## Caveats

One card, one clock, 499 mV. **One base word per side**: on A a ratio depends on the word's neighbouring bits, so A's non-monotonic list is this word's. Ten of 32 fp32 positions, six of fp16's on two sides, and nothing is interpolated here. Three passes in G and T (t = 4.30), so an interval on the board is wide. `bj_31` and `bp_23` rest on two passes. A ratio across protocols (bits 16 and 20) inherits R6's unresolved ±0.2 W. The train's own-zero interpolation under-reads the first quarter of a float train, which raises T's steps by a few hundredths of a watt on average (compare `primary` with [M]). A rail price is about 0.80 of a board price here (23 steps of 1 W or more, 0.71–0.91, [K]). The counts are the desk's and the bench's: C was not read back.

## Departures and disclosures

1. **The trains' own gate fired on what it was not meant to catch.** It was registered as about 5σ on a steady train. A float train is not steady: the same read departs +0.19 W in passes 10220–22 and +0.277 W in 10223 ([A]). The gate ran as registered, and 10223 is out of the primary, which cost T its fourth pass. Nothing was reinstated; [D] and [M] show what it would add, labelled.
2. **The launch rule skipped two runs in G** (E78's rule, unchanged: the reading rose back above the target during the quiet), and they landed on two items two rules need. Registered consequence: not scored. Not re-run.
3. **The rail as primary was chosen on E93's low-power gate noise**, and registered before anyone had seen a float train; see result 10. In int8 it was right.
4. **Budget.** The brief said about 45 card-minutes; 57 were registered; the card session took 55, the queue 48. G took 336–344 s, T 285–286 s, I 132–133 s.
5. **E82's anchors ran once in each G block and not in a train**, against the brief's "in every pass", as registered: a random tile in a train is a heater.
6. **No interim look at power.** The waits read the queue log, pace, clocks and records. The post-claim smoke was read for cycles per op, dumps and config only.
7. **The collection ran on the mini** (`collect_e102.sh`, unchanged, numpy through `uv`), because the Intel was overloaded. Its paths in the committed text files were then rewritten to the raw data's committed location; no number changed. `check_e102.py` runs on the committed result.
8. **E102.md's bench predictions** use the Q132(b) lane's bench and maps as built on the mini at 01:44 PDT; the back-test's counts of E65's, E67's and E79's tiles are that lane's (`bench/backtest-hl-hlp.json` records their sha256; `bench/distill_backtest.py`).
9. **Post hoc, labelled, no rule depends on them:** `check_e102.py` sections [D], [E], [F]'s digit counts, [L] (an independent crude reading from raw telemetry: median board and mean rail, which matches the scored steps within their intervals except where the warm-up lifts the crude flat zero: `bp_22` 0.909 against 0.630 W, `bp_11` 0.665 against 0.388 W) and [M].

## Files

`README.md`; `e102.json`, `runs.csv`, `reduce.txt` (the primary reduction); the arms `e102-dipskept`, `e102-gatesoff`, `e102-auto`, `e102-leak0.1994 / 0.3803 / 0.545 / 0` (`.json`, `runs-*.csv`, `reduce-*.txt`); `scored.json`, `results.md` (every rule, price, ratio, model and arm); `check_e102.py`, `check_e102.txt`; `code.sha256`; `logs/` (the queue log, dry runs, the final config read); `bench/` (`counts-e102.json`, `backtest-hl-hlp.json`, `distill_backtest.py`, frozen with the registration); `aifoundry1-c1/kinds/p102*` (raw blocks: telemetry, marks, records, tile dumps, config reads, code hashes; the smoke as `kinds-smoke-p10201`). The tiles, registration and code: `tools/claims-v3/kinds/` (`E102.md`, `e102/`, `predictions-e102.json`, `make_e102.py`, `make_predictions_e102.py`, `e102_common.py`, `run_e102.py`, `block_e102.sh`, `queue_e102.sh`, `run_e102.sh`, `reduce_e102.py`, `score_e102.py`, `collect_e102.sh`, `selftest_e102.py`, `desk_noise_e102.py`).
