# E79 — the fp16 and int8 single-bit price lists (Q130, aifoundry3, 2026-10-31)

*Pre-registered in [`tools/claims-v3/hlp/README.md`](../../../../tools/claims-v3/hlp/README.md) with
[`predictions.json`](../../../../tools/claims-v3/hlp/predictions.json), committed as **`2a72d352`** at
**09:24:58 PDT — 1 min 56 s before the card was claimed** (09:26:54 PDT, from the Discord message's own
snowflake, id `1566126330142007489`) **and 3 min 24 s before the first measured launch** (09:28:22 PDT, pass
7910's `block_begin`). Amendments A1–A3 as `e66f7c1a` (09:31:52) and `270d2108` (09:32:31) during pass 7910; **A4 as `4216f1fb` at
09:49:45 PDT, after pass 7910 and 12 min 41 s before block B's first launch**. A5–A8 as `23197287`. Card runs 2026-10-31, 09:27–10:3x PDT, on
**aifoundry3 card 0 only**, whose governor is latched at 600 MHz by its boot-time TDP of 0, so every number here
is a 600 MHz, 521.9 mV number — the same card, clock and voltage as E65's fp32 B-side scan and E67's A-side scan,
which is the point. Claimed in `#community-lab` at 09:26:54 PDT and released after the last pass.*

## Why it ran

The Horace hub's Status item 9 is "**fp16 and int8**". E65 priced all 32 bit positions of an **fp32 B** operand
(83–1,008 fJ per flipped bit) and E67 all 32 of **A** (153–1,440 fJ), on this card. The blog's claim — that the
*kind* of number you multiply sets the power — had nothing to say about the two formats a real inference workload
uses. This runs the same Hamming ladder on **fp16** (`TensorFMA16A32`) and **int8** (`TensorIMA8A32`), both
operand sides, every bit position, with the zeros and constant-operand anchors, a 2-bit and a 4-bit additivity
rung per format against E70's law, a layout control, and an **fp32 tie** at E65's dearest position so the port
can be checked against a published number on the same silicon.

## Results

Card aifoundry3 card 0, 546 / 546 / 318 cycles per fp32 / fp16 / int8 multiply-add, 600 MHz, 521.9 mV, TDP 0. Passes kept [7910, 7911, 7913, 7915, 7920, 7921, 7922, 7923]; runs kept 348 of 480; leakage slope 0.0834 W/°C. **15 registered rules passed, 10 failed, 0 were not scored**; every failure is in the scored table below.

Ten passes ran; **two were set aside by the registered drift gate** — 7912 (`anchor_pi` drift 0.411 W) and 7914 (0.527 W), against the 0.3 W bar, each with **zero** failed runs — and **no single run failed any gate** in the whole experiment. Amendment A8 added 7914 and 7915 after 7912 dropped out, and only one of the two survived, so the fp16 and int8 full lists rest on **four** kept passes and the order probe's shared items on up to eight. Nothing was reinstated and no pass was chosen after the fact.

**1. The fp16 price list is fp32's compressed into ten mantissa bits, and its exponent is cheap.** A flipped bit of an fp16 **B** operand costs **205 fJ** at mantissa bit 0 and **494 fJ [465, 523]** at mantissa bit 9, rising monotonically (Spearman ρ = 1.000, P1a PASS); on the **A** side 355 to **620 fJ** at bit 9. The five exponent bits cost 64–83 fJ and the sign bit 34 fJ — **cheaper than every mantissa bit**, which inverts fp32's order, where the exponent (174 fJ mean) sat *above* the flat low-mantissa floor (109 fJ). The reason is arithmetic: fp32's floor ran from the LSB to thirteen bits below the significand MSB, and fp16's mantissa is only ten bits deep, so **all of it is in the rising regime** (P1c PASS). The width prediction holds: the dearest fp16 significand bit is 0.470 of this run's fp32 tie, against the 11/24 = 0.458 the significand widths imply (P2b PASS), and 0.431 on the A side against E67's 1,440 fJ (P2a PASS). What **fails** is the registered *span*: fp16's mantissa runs only 2.41× end to end against the ≥ 3.0 registered and fp32's own 9.2× (P1b FAIL) — a ten-bit array has less room to be steep in than a twenty-three-bit one, which the registration did not allow for.

**1b. Why the cheap exponent is only half a result.** Every number in Result 1 is in the `jg` construction, which Result 5 shows is a composite. There is a mechanism that would make an exponent flip cheap *in that construction specifically*: with A = 1.0 the product is B, so flipping one exponent bit leaves the two C accumulators a lane alternates between related by a **power of two** — in fp32 they then share their mantissa bits and differ in the exponent field alone, and the result bus barely swings, where a mantissa flip makes them differ in many low bits. The balanced layouts were only run at the dearest *mantissa* position, so **this experiment cannot separate the two**: the exponent and sign prices are reported as `jg` all-in numbers and a balanced-layout exponent scan is left open. It is the cheapest follow-up E79 names.

**2. The port reproduces E65 on the same silicon.** The fp32 tie `b32_22` reads **1052 fJ [984, 1120]** against E65's published **1,008 ± 21 fJ** at the same position, card, clock and voltage (P7 PASS). That is what licenses every cross-format comparison here. The minion-rail arm sits at 0.79–0.81 of the board arm on every item, inside Q129's measured rail ratio 0.825 [0.787, 0.856].

**3. int8 is faster because it has twice the units, and the card said so through its power.** Every int8 B rung in the registered `jg` layout reads **0.012 W** above its zero where the identical construction reads 4.536 W in fp16 and 4.830 W in fp32. The public RTL says why: `VPU_NUM_TIMA 2` integer tensor units a lane (`rtl/inc/vpu_defines.vh:210`, instantiated at `vpu_lane.v:408`), each with `TIMA_INT8_MUL_NUM 4` int8 multipliers on one 32-bit operand (`rtl/inc/tima_defines.vh:8`, `tima/tima_top.v` `F2_PROD`), so **8 lanes × 2 units × 4 multipliers = 64 int8 multiply-adds a cycle** and 16,384 / 64 = **256** cycles of work, against the float path's one unit a lane with a single-bit B column selector (`vpu_tensorfma.v:282`), 16 MACs a cycle, **512**. That is the first mechanism this repo has for the measured **546 / 546 / 318**, and it leaves the 28-cycle difference between the two fixed overheads (62 and 34) unexplained. Both column halves therefore issue in the *same* cycle in int8, so a (lane, unit) pair always drives the same C column and a flip on the column-half boundary never alternates in time. The `kg` layout, which carries the flip on the line-group parity instead, does alternate: it is the int8 B list below (amendments A4 and A6).

**4. The int8 price list, and its sign bit.** Per flipped **B** bit, 27 fJ at bit 0 to **86 fJ [56, 116]** at bit 5; per flipped **A** bit, 86 to **152 fJ** at bit 7. The seven magnitude bits are nearly **flat** — an int8 multiplier has no exponent and no long carry chain, so a flip anywhere in the magnitude toggles about the same share of a small array — and the dear bit is the **two's-complement MSB**, which carries weight 128 *and* the sign correction. On the A side it is 152 fJ against 78 fJ at bit 6. So the rise P3a looked for is not there (FAIL on the kg list, FAIL as registered on the jg one), while the sign bit is the dear one on the side that resolves. **The int8 B list is only weakly resolved** and is reported as such: its whole step is about 0.1 W (the `kg` layout flips at 1/16 the rate of the 546-cycle formats' `jg` one), it has four passes, and its intervals overlap across most positions, so the *ordering* of its positions is not established — only the level is. The **A** side carries the int8 shape: seven magnitude positions inside 71–92 fJ and the MSB at 152 ± 5 fJ. The registered width test P8 reads 0.081 against [0.15, 0.60] (FAIL) — **by construction**, because it divides a balanced-accumulator int8 price by a *composite* fp32 one; the like-for-like comparison is in Result 5 and lands on 0.33.

**4b. One thing in the int8 B list that is not established, and should be chased.** Its seven magnitude positions alternate: the odd ones (1, 3, 5) average **73 fJ** and the even ones (0, 2, 4, 6) **37 fJ**, a ratio of **1.98**, and bit 3's interval [64, 81] is disjoint from both its neighbours'. That is the shape a **radix-4 Booth recoder** gives: its digits cover (b1,b0,b−1), (b3,b2,b1), (b5,b4,b3), (b7,b6,b5), so every odd-indexed bit enters **two** digits and every even-indexed bit **one**. It is suggestive and **not established** — four passes, a 0.1 W step, and no such alternation in the fp16 B list (205, 224, 253, 294, 322, 344, 371, 372, 467, 491 fJ) or the int8 A list, which a recoder on the same operand should also show. It is the first thing a follow-up should re-measure, at these positions and with more passes.

**5. Most of a single-bit "price" measured this way is not the flip — and the order probe says so in all three formats.** The same single-bit flip was run in three layouts at the dearest position of each format. `jg` is E65's and E67's construction: the flip sits on the column-half boundary, so the two C accumulators a lane alternates between accumulate *different* products and diverge. `jgp` flips the same bit at 97% of the same rate but swaps the halves with the line-group parity, and `kg` carries the flip on the line-group parity alone at 1/31 of the rate; in both, every column sees the same mix, so the accumulators stay equal.

| format | `jg` ΔW | `jg` fJ/bit | `jgp` ΔW | `jgp` fJ/bit | `kg` ΔW | `kg` fJ/bit | `jgp`/`jg` ΔW |
|---|---|---|---|---|---|---|---|
| fp32 | 4.830 | 1052 | 0.669 | 150 | 0.023 | 159 | 0.136 |
| fp16 | 4.536 | 494 | 0.781 | 88 | 0.038 | 134 | 0.175 |
| int8 | 0.012 | 0 | 0.088 | 3 | 0.097 | 49 | 0.286 |

Two things follow, and the second is a correction the chain has to carry. **(a)** `jgp` and `kg` differ **31-fold in designed flip count** and give the *same* per-bit price within their intervals, which is what a real per-flip energy should do. **(b)** `jg` gives 6–7× more at the same count as `jgp`, in **fp32 as much as in fp16** — so this is not an fp16 quirk, and **E65's and E67's published fp32 lists measure the same composite**: the flip plus the result path swinging between two diverging accumulators. The registered layout control fails on exactly this (P6_fp16 FAIL, ratio 0.175; the fp32 control `b32p_22` reads 0.136). The multi-bit rungs say the same from the other side: one flipped fp16 bit 4.536 W, two 5.228 W, four 6.260 W, so the **marginal** cost of a further flipped fp16 bit is **56.2 ± 12.7 fJ** against the 494 fJ its single-bit rung reports — E67's amendment A13 algebra (`T + e·n·rate`) with `T` dominant. **So this experiment reports two numbers for every position, never one**: the all-in step in the `jg`/A-side construction, which is what E65 and E67 published and what a workload actually pays when that bit starts alternating against a constant partner, and the balanced-accumulator price from `jgp`/`kg`, which is the closest thing here to the energy of the flip itself. **The width law holds on both footings**: at the dearest significand position the balanced price runs 150 fJ (fp32) → 88 fJ (fp16) → 49 fJ (int8), ratios 0.58 and 0.33 against the 0.458 and 0.333 the significand widths imply.

**6. Zeros are worth several times more in fp16 than in int8.** Replacing a constant nonzero operand with an all-zero tile saves **8.736 ± 0.054 W** in fp16 and **1.834 ± 0.113 W** in int8 — a factor of **4.76**. Both are paired per pass and need no idle bracket (amendment A7). That is Q130(g)'s RTL reading measured on silicon: one 32-bit zero test, one mask for the float unit and both integer units, so a gated word is worth one fp32 number, two fp16 or four int8, and the price of a zero falls as the format narrows. The registered idle-bracketed form of the same test is P4, which reads 0.204 for fp16 (FAIL) and 3.797 for int8 (FAIL) against a 0.20 bar; that bracket is the second before each launch and in a dense pass it still carries the previous run's tail, which is why A7 reports the paired form.

## The tables — card aifoundry3, 600 MHz, 521.9 mV

Passes kept [7910, 7911, 7913, 7915, 7920, 7921, 7922, 7923] (8); runs kept 348 of 480; leakage slope 0.0834 W/°C from 310 runs; cycles per op {'fp16': 546.0024000000001, 'fp32': 546.0024000000001, 'int8': 318.00149999999996}.
Passes set aside: [{'pass': 7912, 'failed_runs': 0, 'pi_drift_W': 0.410499999999999}, {'pass': 7914, 'failed_runs': 0, 'pi_drift_W': 0.5274999999999963}].

### fp16, B side (A = 1.0), jg layout

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | mantissa | 1.881 ± 0.010 | **205** | [204, 206] | 1503.72 | 4.9e+06 | 4 |
| 1 | mantissa | 2.053 ± 0.032 | **224** | [220, 227] | 1641.30 | 5.35e+06 | 4 |
| 2 | mantissa | 2.344 ± 0.061 | **255** | [249, 262] | 1873.90 | 6.1e+06 | 4 |
| 3 | mantissa | 2.705 ± 0.050 | **295** | [289, 300] | 2162.63 | 7.05e+06 | 4 |
| 4 | mantissa | 2.948 ± 0.052 | **321** | [315, 327] | 2357.01 | 7.68e+06 | 4 |
| 5 | mantissa | 3.073 ± 0.310 | **334** | [301, 368] | 2455.57 | 8e+06 | 4 |
| 6 | mantissa | 3.429 ± 0.062 | **373** | [367, 380] | 2741.36 | 8.93e+06 | 4 |
| 7 | mantissa | 3.543 ± 0.960 | **386** | [281, 490] | 2833.14 | 9.23e+06 | 4 |
| 8 | mantissa | 3.956 ± 1.106 | **431** | [310, 551] | 3162.13 | 1.03e+07 | 4 |
| 9 | mantissa | 4.536 ± 0.268 | **494** | [465, 523] | 3626.17 | 1.18e+07 | 8 |
| 10 | exponent | 0.653 ± 0.040 | **71** | [67, 76] | 521.84 | 1.7e+06 | 4 |
| 11 | exponent | 0.616 ± 0.063 | **67** | [60, 74] | 492.31 | 1.6e+06 | 4 |
| 12 | exponent | 0.588 ± 0.033 | **64** | [60, 68] | 470.03 | 1.53e+06 | 4 |
| 13 | exponent | 0.762 ± 0.061 | **83** | [76, 90] | 609.31 | 1.98e+06 | 4 |
| 14 | exponent | 0.699 ± 0.268 | **76** | [47, 105] | 559.19 | 1.82e+06 | 4 |
| 15 | sign | 0.313 ± 0.516 | **34** | [-22, 90] | 249.87 | 8.14e+05 | 4 |

Significand Spearman ρ(bit, price) = **1.000**; span over the kept significand positions **2.4×** (205–494 fJ).

### fp16, A side (B = 1.0)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | mantissa | 1.631 ± 0.183 | **355** | [315, 395] | 2608.39 | 8.5e+06 | 4 |
| 1 | mantissa | 1.152 ± 0.489 | **251** | [144, 358] | 1842.33 | 6e+06 | 4 |
| 2 | mantissa | 2.093 ± 0.190 | **456** | [415, 497] | 3346.45 | 1.09e+07 | 4 |
| 3 | mantissa | 1.357 ± 0.779 | **296** | [126, 466] | 2171.19 | 7.07e+06 | 4 |
| 4 | mantissa | 2.203 ± 0.534 | **480** | [363, 596] | 3522.37 | 1.15e+07 | 4 |
| 5 | mantissa | 1.876 ± 0.280 | **408** | [347, 470] | 2998.83 | 9.77e+06 | 4 |
| 6 | mantissa | 2.535 ± 0.157 | **552** | [518, 586] | 4053.23 | 1.32e+07 | 4 |
| 7 | mantissa | 2.303 ± 0.743 | **502** | [340, 664] | 3683.74 | 1.2e+07 | 4 |
| 8 | mantissa | 2.391 ± 0.169 | **521** | [484, 558] | 3824.15 | 1.25e+07 | 4 |
| 9 | mantissa | 2.847 ± 0.214 | **620** | [573, 667] | 4552.26 | 1.48e+07 | 4 |
| 10 | exponent | 0.431 ± 0.204 | **94** | [49, 138] | 688.40 | 2.24e+06 | 4 |
| 11 | exponent | 0.373 ± 0.164 | **81** | [45, 117] | 596.51 | 1.94e+06 | 4 |
| 12 | exponent | 0.337 ± 0.262 | **73** | [16, 131] | 538.31 | 1.75e+06 | 4 |
| 13 | exponent | 0.427 ± 0.050 | **93** | [82, 104] | 683.02 | 2.23e+06 | 4 |
| 14 | exponent | 0.422 ± 0.267 | **92** | [34, 150] | 674.62 | 2.2e+06 | 4 |
| 15 | sign | 0.327 ± 0.258 | **71** | [15, 128] | 523.61 | 1.71e+06 | 4 |

Significand Spearman ρ(bit, price) = **0.855**; span over the kept significand positions **2.5×** (251–620 fJ).

### int8, B side (A = 1), jg layout - does not alternate (A4)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | magnitude | 0.046 ± 0.067 | **1** | [-1, 4] | 10.65 | 3.47e+04 | 4 |
| 1 | magnitude | -0.119 ± 0.286 | **-4** | [-13, 5] | -27.77 | -9.05e+04 | 4 |
| 2 | magnitude | -0.065 ± 0.368 | **-2** | [-14, 10] | -15.15 | -4.94e+04 | 4 |
| 3 | magnitude | 0.069 ± 0.103 | **2** | [-1, 5] | 16.06 | 5.23e+04 | 4 |
| 4 | magnitude | 0.044 ± 0.083 | **1** | [-1, 4] | 10.31 | 3.36e+04 | 4 |
| 5 | magnitude | 0.078 ± 0.125 | **2** | [-2, 6] | 18.05 | 5.88e+04 | 4 |
| 6 | magnitude | 0.012 ± 0.082 | **0** | [-2, 3] | 2.78 | 9.06e+03 | 8 |
| 7 | MSB (sign) | 0.028 ± 0.115 | **1** | [-3, 5] | 6.51 | 2.12e+04 | 4 |

Significand Spearman ρ(bit, price) = **0.286**; span over the kept significand positions **-0.6×** (-4–2 fJ).

### int8, B side (A = 1), kg layout - the int8 B price list (A4)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | magnitude | 0.053 ± 0.025 | **27** | [15, 40] | 199.02 | 6.48e+05 | 4 |
| 1 | magnitude | 0.121 ± 0.087 | **62** | [17, 106] | 452.03 | 1.47e+06 | 4 |
| 2 | magnitude | 0.062 ± 0.027 | **31** | [17, 45] | 229.28 | 7.47e+05 | 4 |
| 3 | magnitude | 0.143 ± 0.017 | **72** | [64, 81] | 530.88 | 1.73e+06 | 4 |
| 4 | magnitude | 0.080 ± 0.017 | **40** | [32, 49] | 297.06 | 9.68e+05 | 4 |
| 5 | magnitude | 0.169 ± 0.059 | **86** | [56, 116] | 628.52 | 2.05e+06 | 4 |
| 6 | magnitude | 0.097 ± 0.043 | **49** | [27, 71] | 360.94 | 1.18e+06 | 4 |
| 7 | MSB (sign) | 0.033 ± 0.321 | **17** | [-146, 180] | 122.98 | 4.01e+05 | 4 |

Significand Spearman ρ(bit, price) = **0.500**; span over the kept significand positions **3.2×** (27–86 fJ).

### int8, A side (B = 1)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 0 | magnitude | 1.359 ± 0.112 | **86** | [79, 93] | 632.35 | 2.06e+06 | 4 |
| 1 | magnitude | 1.181 ± 0.428 | **75** | [48, 102] | 549.77 | 1.79e+06 | 4 |
| 2 | magnitude | 1.128 ± 0.324 | **71** | [51, 92] | 524.76 | 1.71e+06 | 4 |
| 3 | magnitude | 1.390 ± 0.041 | **88** | [86, 91] | 646.98 | 2.11e+06 | 4 |
| 4 | magnitude | 1.452 ± 0.042 | **92** | [89, 95] | 675.61 | 2.2e+06 | 4 |
| 5 | magnitude | 1.324 ± 0.070 | **84** | [79, 88] | 616.18 | 2.01e+06 | 4 |
| 6 | magnitude | 1.227 ± 0.208 | **78** | [65, 91] | 571.03 | 1.86e+06 | 4 |
| 7 | MSB (sign) | 2.399 ± 0.077 | **152** | [147, 157] | 1116.33 | 3.64e+06 | 4 |

Significand Spearman ρ(bit, price) = **0.143**; span over the kept significand positions **1.3×** (71–92 fJ).

### fp32 tie, B side (A = 1.0), jg layout

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 22 | mantissa | 4.830 ± 0.314 | **1052** | [984, 1120] | 7723.45 | 2.52e+07 | 8 |
### fp32, B side, jgp layout (A4 order probe)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 22 | mantissa | 0.669 ± 0.037 | **150** | [142, 159] | 1103.33 | 3.59e+06 | 4 |
### fp32, B side, kg layout (A4 order probe)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 22 | mantissa | 0.023 ± 0.070 | **159** | [-328, 645] | 1163.61 | 3.79e+06 | 4 |
### fp16, B side, jgp layout (the registered control)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 9 | mantissa | 0.781 ± 0.262 | **88** | [58, 117] | 644.82 | 2.1e+06 | 8 |
### fp16, B side, kg layout (A4 order probe)

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 9 | mantissa | 0.038 ± 0.060 | **134** | [-75, 342] | 982.56 | 3.2e+06 | 4 |
### int8, B side, jgp layout

| bit | field | ΔW over the zero | fJ per flipped bit | 95% | fF | electrons | passes |
|---|---|---|---|---|---|---|---|
| 6 | magnitude | 0.088 ± 0.047 | **3** | [1, 4] | 21.02 | 6.85e+04 | 8 |
### The order probe: the same flip in three layouts (amendment A4)

The dW ratios divide by no designed count, so they are order-free.

| format | jg dW | jgp dW | kg dW | jgp/jg | kg/jg |
|---|---|---|---|---|---|
| fp16 | 4.536 | 0.781 | 0.038 | 0.175 | 0.008 |
| int8 | 0.012 | 0.088 | 0.097 | 0.286 | 0.604 |
| fp32 | 4.830 | 0.669 | 0.023 | 0.136 | 0.005 |

### The marginal price of a further flipped bit (amendment A4)

| format | from | dW per extra flipped bit | marginal fJ per bit | 95% | passes |
|---|---|---|---|---|---|
| fp16 | b16m2 - b16m4 | 0.516 | 56.2 | ± 12.7 | 4 |
| int8 | b8m2 - b8m4 | 0.035 | 1.1 | ± 1.3 | 4 |

### Switching over the idle bracket

A7: the **zeros − h0** column is paired per pass and needs no idle bracket, so it is the robust statement of what zeros buy. The idle-bracketed columns are kept because P4 is registered on them; the bracket is the second before each launch and in a dense pass it can still carry the previous run's tail, which is why its spread is wide.

| format | zeros − h0 (W, idle-free) | 95% | idle bracket W | h0 switching W | zeros switching W | zeros / h0 |
|---|---|---|---|---|---|---|
| fp16 | **-8.736** | ± 0.054 | 25.951 ± 0.141 | 9.581 ± 1.608 | 1.923 | 0.2037 |
| int8 | **-1.834** | ± 0.113 | 27.210 ± 3.707 | 2.473 ± 2.190 | 1.311 | 3.7974 |
| fp32 | **—** | ± 0.000 | 26.032 ± 0.000 | 10.516 ± 0.055 | — | — |

### Additivity (E70's law at low Hamming weight)

| rung | bits | ΔW | sum of its own single-bit ΔW ratio | 95% | fJ per bit |
|---|---|---|---|---|---|
| b16m2 | [8, 9] | 5.228 | 0.615 | ± 0.072 | 285 |
| b16m4 | [6, 7, 8, 9] | 6.260 | 0.404 | ± 0.036 | 170 |
| b8m2 | [5, 6] | 0.101 | 0.637 | ± 2.056 | 2 |
| b8m4 | [3, 4, 5, 6] | 0.172 | 0.596 | ± 1.772 | 1 |

### The layout control (the issue order)

| control | primary | bit | control fJ | primary fJ | ratio | 95% |
|---|---|---|---|---|---|---|
| b16p_9 | b16_9 | 9 | 88 | 494 | 0.181 | ± 0.062 |
| b8p_6 | b8_6 | 6 | 3 | 0 | 4.119 | ± 9.013 |
| b32p_22 | b32_22 | 22 | 150 | 1052 | 0.140 | ± 0.012 |

### The registered rules, scored

| rule | leg | what | test | measured | verdict |
|---|---|---|---|---|---|
| **P1a** | primary | fp16's B-side mantissa prices rise with position | Spearman rho(bit, fJ) over fp16 B bits 0-9 >= 0.60 | 1 | **PASS** |
| **P1a_A** | secondary | the same on the A side | Spearman rho(bit, fJ) over fp16 A bits 0-9 >= 0.60 | 0.8545 | **PASS** |
| **P1b** | primary | the fp16 mantissa spans a factor, as fp32's does | fJ(dearest fp16 B mantissa bit) / fJ(cheapest fp16 B mantissa bit whose price exceeds its own 95% half-width) >= 3.0 | 2.411 | **FAIL** |
| **P1c** | primary | fp16 has no flat floor: its whole 10-bit mantissa is in fp32's rising regime, because fp32's floor ran from the LSB to 13 bits below the significand MSB and fp16's mantissa is only 10 bits deep | fJ(fp16 B bit 5) > fJ(fp16 B bit 0) with the two 95% intervals disjoint | bit5_lo 300.7, bit0_hi 206, gap_fJ 94.69 | **PASS** |
| **P2b** | primary | fp16's dearest significand bit costs less than fp32's by roughly the significand-width ratio, B side | fJ(dearest fp16 B mantissa bit) / fJ(this run's b32_22) in [0.25, 0.80] | 0.4695 | **PASS** |
| **P2b_e65** | secondary | the same against E65's published fp32 number instead of this run's tie | fJ(dearest fp16 B mantissa bit) / 1008 in [0.25, 0.80] | 0.49 | **PASS** |
| **P2a** | primary | the same on the A side, against E67's published 1440 fJ | fJ(dearest fp16 A mantissa bit) / 1440 in [0.25, 0.80] | 0.4306 | **PASS** |
| **P3a** | primary | int8 prices rise toward the high bits | Spearman rho(bit, fJ) over int8 B bits 0-6 >= 0.60 | 0.2857 | **FAIL** |
| **P3a_A** | secondary | the same rise on the A side | Spearman rho(bit, fJ) over int8 A bits 0-6 >= 0.60 | 0.1429 | **FAIL** |
| **P3b** | primary | int8's sign bit 7 is not cheaper than bit 6 | fJ(int8 B bit 7) >= fJ(int8 B bit 6) - the 95% half-width of the per-pass paired difference | bit7_fJ 0.8867, bit6_fJ 0.3789, allowance_fJ 4.488 | **PASS** |
| **P4_fp16** | primary | the zeros rung costs at most 0.2x the h0 switching, fp16 | (P(z16) - P(idle)) / (P(h16q) - P(idle)) <= 0.20 | 0.2037 | **FAIL** |
| **P4_int8** | primary | the same for int8 | (P(z8) - P(idle)) / (P(h8q) - P(idle)) <= 0.20 | 3.797 | **FAIL** |
| **P5_fp16_2** | primary | two bits flipping together are sub-additive but not far from the sum (E70's saturating law at low Hamming weight) | dW(b16m2) / [dW(b16_8) + dW(b16_9)] in [0.55, 1.05] | 0.6146 | **PASS** |
| **P5_fp16_4** | primary | four bits share more | dW(b16m4) / sum of dW(b16_6..b16_9) in [0.35, 1.00] | 0.4043 | **PASS** |
| **P5_fp16_mono** | primary | the sharing grows with the Hamming weight | r4 <= r2 + 0.10 (fp16) | -0.2103 | **PASS** |
| **P5_int8_2** | primary | the same at two bits, int8 | dW(b8m2) / [dW(b8_5) + dW(b8_6)] in [0.55, 1.05] | 0.6374 | **PASS** |
| **P5_int8_4** | primary | the same at four bits, int8 | dW(b8m4) / sum of dW(b8_3..b8_6) in [0.35, 1.00] | 0.5963 | **PASS** |
| **P5_int8_mono** | primary | the same monotonicity, int8 | r4 <= r2 + 0.10 (int8) | -0.04105 | **PASS** |
| **P6_fp16** | primary | the registered issue order is the one the unit runs: the same flip in the group-parity layout costs the same per bit | fJ(b16p_9) / fJ(b16_9) in [0.80, 1.25] | 0.1808 | **FAIL** |
| **P6_int8** | primary | the same for int8 | fJ(b8p_6) / fJ(b8_6) in [0.80, 1.25] | 4.119 | **FAIL** |
| **P3a_kg** | A4 re-score | P3a on the layout that does alternate in int8 (amendment A4): int8 prices rise toward the high bits | Spearman rho(bit, fJ) over int8 B kg bits 0-6 >= 0.60 | 0.5 | **FAIL** |
| **P3b_kg** | A4 re-score | P3b on the kg layout: int8's sign bit 7 is not cheaper than bit 6 | fJ(int8 B kg bit 7) >= fJ(int8 B kg bit 6) - the 95% half-width of the difference | bit7_fJ 16.75, bit6_fJ 49.16, allowance_fJ 164.2 | **PASS** |
| **P8_kg** | A4 re-score | P8 on the kg layout: int8's dearest position costs about the 8/24 width ratio of fp32's | fJ(dearest int8 B kg position) / fJ(this run's b32_22) in [0.15, 0.60] | 0.08138 | **FAIL** |
| **P7** | primary | the port reproduces E65 on the same card at the one fp32 position it reruns | fJ(b32_22) in [756, 1260] (1008 fJ +- 25%) | 1052 | **PASS** |
| **P8** | primary | int8's dearest position costs about the 8/24 width ratio of fp32's | fJ(dearest int8 B position) / fJ(this run's b32_22) in [0.15, 0.60] | 0.002337 | **FAIL** |

15 passed, **10 failed**, 0 not scored, of 25.

### Sensitivity: every price at E71's measured idle slope 0.3803 W/°C

| list | bit | fitted-slope fJ | E71-slope fJ | change |
|---|---|---|---|---|
| fp16_a | 0 | 355 | 338 | -4.8% |
| fp16_a | 1 | 251 | 240 | -4.2% |
| fp16_a | 2 | 456 | 439 | -3.7% |
| fp16_a | 3 | 296 | 278 | -6.0% |
| fp16_a | 4 | 480 | 444 | -7.4% |
| fp16_a | 5 | 408 | 398 | -2.6% |
| fp16_a | 6 | 552 | 509 | -7.8% |
| fp16_a | 7 | 502 | 471 | -6.1% |
| fp16_a | 8 | 521 | 487 | -6.5% |
| fp16_a | 9 | 620 | 585 | -5.7% |
| fp16_a | 10 | 94 | 91 | -2.6% |
| fp16_a | 11 | 81 | 81 | +0.0% |
| fp16_a | 12 | 73 | 73 | +0.0% |
| fp16_a | 13 | 93 | 88 | -5.2% |
| fp16_a | 14 | 92 | 90 | -1.8% |
| fp16_a | 15 | 71 | 71 | +0.0% |
| fp16_b | 0 | 205 | 191 | -6.5% |
| fp16_b | 1 | 224 | 205 | -8.3% |
| fp16_b | 2 | 255 | 236 | -7.4% |
| fp16_b | 3 | 295 | 273 | -7.4% |
| fp16_b | 4 | 321 | 296 | -7.9% |
| fp16_b | 5 | 334 | 309 | -7.7% |
| fp16_b | 6 | 373 | 348 | -6.9% |
| fp16_b | 7 | 386 | 358 | -7.3% |
| fp16_b | 8 | 431 | 401 | -6.8% |
| fp16_b | 9 | 494 | 464 | -6.1% |
| fp16_b | 10 | 71 | 69 | -3.4% |
| fp16_b | 11 | 67 | 61 | -8.4% |
| fp16_b | 12 | 64 | 63 | -1.3% |
| fp16_b | 13 | 83 | 77 | -7.3% |
| fp16_b | 14 | 76 | 75 | -1.6% |
| fp16_b | 15 | 34 | 33 | -2.4% |
| fp16_b_jgp | 9 | 88 | 84 | -4.8% |
| fp16_b_kg | 9 | 134 | 134 | +0.0% |
| fp32_b | 22 | 1052 | 996 | -5.4% |
| fp32_b_jgp | 22 | 150 | 149 | -0.6% |
| fp32_b_kg | 22 | 159 | 159 | +0.0% |
| int8_a | 0 | 86 | 85 | -1.1% |
| int8_a | 1 | 75 | 74 | -1.3% |
| int8_a | 2 | 71 | 74 | +3.6% |
| int8_a | 3 | 88 | 87 | -1.1% |
| int8_a | 4 | 92 | 95 | +3.3% |
| int8_a | 5 | 84 | 83 | -1.1% |
| int8_a | 6 | 78 | 77 | -1.2% |
| int8_a | 7 | 152 | 151 | -0.6% |
| int8_b | 0 | 1 | -2 | -259.4% |
| int8_b | 1 | -4 | -4 | +6.2% |
| int8_b | 2 | -2 | -5 | +154.0% |
| int8_b | 3 | 2 | -1 | -145.3% |
| int8_b | 4 | 1 | -3 | -309.9% |
| int8_b | 5 | 2 | -1 | -153.2% |
| int8_b | 6 | 0 | -2 | -590.0% |
| int8_b | 7 | 1 | -5 | -676.6% |
| int8_b_jgp | 6 | 3 | -1 | -118.8% |
| int8_b_kg | 0 | 27 | 3 | -90.3% |
| int8_b_kg | 1 | 62 | 13 | -79.5% |
| int8_b_kg | 2 | 31 | 35 | +12.0% |
| int8_b_kg | 3 | 72 | 5 | -93.7% |
| int8_b_kg | 4 | 40 | 48 | +18.6% |
| int8_b_kg | 5 | 86 | 39 | -55.0% |
| int8_b_kg | 6 | 49 | 2 | -95.7% |
| int8_b_kg | 7 | 17 | -2 | -112.4% |


## What the card had to tell us about itself first

**The host's tile layout per format, read from its own source.** `workloads/sparsity/host/main.cpp` —
`makeTiles` packs the tiles and `fillValues`'s `file:` branch reads 1,024 raw A bytes then 1,024 raw B bytes
**in the chosen type's layout, before the per-type value code and for every `--type`**, so one tile file gives
any kind of number in any format with no rebuild:

```
E    = 1 (fp32) | 2 (fp16) | 4 (int8)          elements of B per column per 64 B line
K    = 16 * E                                  the tile's depth: 16 | 32 | 64
A[i][k]      at byte  i * 64 + k * size        16 lines of 64 B; A row i = line i
B[p*E+e][j]  at byte  p * 64 + (j * E + e) * size
```

For **fp16** the two K-terms of one column sit adjacent inside a 32-bit group; for **int8** the four do. One
32-bit word holds E elements **of one column**, not of one row — a tile written in the fp32 layout and fed to
`--type fp16` flips entirely different bits, which is why `make_hlp.py` packs by format and `--check` reads every
file back through the same layout.

**The card's own state, read only, at both ends of every pass.** `ettelem config` before and after each of the
ten passes (`config_start.json`, `config_end.json`) reads
`{"tdp_w":0,"temp_threshold_c":65,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}` — identical at
every read, so the governor stayed latched at 600 MHz by its boot-time TDP of 0 and nothing in E79 wrote a knob.
The **firmware**, which the Horace hub's Status item 7 says nobody re-read in Q129, was read once from the
read-only `DM_CMD_GET_*` queries (`ident/firmware.txt`): release **1.4.0**, BL1 **0.22.0**, BL2 **0.22.0**, PMIC
**1.5.0**, Master / Worker / Machine Minion **0.25.1**, ASIC revision **597**, module uptime 4 d 18 h 9 m, TDP
level 0, software temperature threshold 65 °C. That is **the same reading aifoundry2 gave E69 and E72**, so
Q129's throttle-wrap gate conclusion at BL2 0.22.0 covers this card too, and
`docs/findings/14-card-behaviour.md`'s three "aifoundry3 was not re-read" notes can close. E79 does not edit that
file: another lane owns it.

**The unit's own micro-op structure, measured rather than assumed.** The registered order is PRM 9.4's, as
`hl/make_hl.py` states it for fp32, generalised: for each B line group, for each A row, two micro-ops (C columns
0–7 then 8–15), lane *l* taking column *l* then column 8+*l* and A broadcast to all eight lanes. That holds for
the 546-cycle formats. **It does not hold for int8**, and pass 7910 said so: see Result 3.

## How a price is counted (the same rule E65 used)

A **designed flip** is an operand *element read* whose chosen bit differs from the previous read in the same
lane's stream, summed over the eight lanes and wrapped op to op — `make_hl.py:fma_flips`'s rule, parameterised by
format in `make_hlp.py:count_flips` and re-derived from every written file by `--check`. The price is

```
e  =  (P(item) - P(its own zero))  /  (designed flips per op  x  ops per second)
```

computed **per pass** and then averaged over passes, with the interval `t(0.975, n-1)` × the between-pass SE. The
unit of replication is the pass, never samples inside one burst. `P` is the mean board power over
[t0+1 s, t0+3 s) corrected to the launch reading with the card's leakage slope (21 Sep's `p80`), and the **idle
bracket** is the second before each launch, with the card idle at the same 58 °C reading.

| | designed flips per multiply-add, 8 lanes, one bit per flipping element read |
|---|---|
| **B side, `jg` layout** | 16 rows × K × 16 columns = **4,096** (fp32) · **8,192** (fp16) · 16,384 (int8, *never reached — Result 3*) |
| **B side, `kg` layout** | **128** (fp32) · **256** (fp16) · **1,024** (int8, the closed form its 318-cycle structure implies) |
| **A side** | half the B side: **2,048** (fp32) · **4,096** (fp16) · **8,192** (int8) |

The A side is half the B side in every format for E67's reason: the issue order holds an A word across both
micro-ops of a row, so an A word can only change every *second* cycle. The reduction divides each item by its
**own** manifest count, so every number here is per flipped bit on one footing.

## Amendments

A1–A3 and A4 are all dated and all written **before the data they touch**. None moves a registered band; A4 adds
items and reported quantities, exactly as E67's A13 and A14 did.

| | What | Commit |
|---|---|---|
| **A1** | four more passes of exactly the registered item list, because a pass took 4.5 min rather than the budgeted 12 | `e66f7c1a` |
| **A2** | `collect_e79.sh`, the plumbing that reduces every finished pass and runs the registered E71-slope sensitivity arm | `e66f7c1a` |
| **A3** | A1's four extra passes cut to two — the measured pace is 8.7 s a run, so eight passes would be ~82 card-minutes, past the registered 75. The budget is the binding constraint and does not move | `270d2108` |
| **A4** | the `kg` layout and `b8k_0`…`b8k_7` (the int8 B price list), `b32p_22`, `b32k_22` and `b16k_9` (the order probe), the order-probe and marginal blocks in the reduction, and the A4 re-scoring of P3a / P3b / P8 on the `kg` list beside the registered scoring on `jg`. Written after pass 7910, before any block-B data | `4216f1fb` |

## Files

| File | What |
|---|---|
| `hlp.json`, `runs.csv`, `reduce.txt` | `hlp/reduce_hlp.py` over every pass that finished |
| `hlp-leak0.3803.json`, `runs-leak0.3803.csv`, `reduce-leak0.3803.txt` | the registered sensitivity arm: every price re-reduced at E71's measured aifoundry3 idle slope 0.3803 W/°C instead of the fitted one |
| `results.md`, `scored.json` | `hlp/report_e79.py`: the tables below and every registered rule scored |
| `manifest.json` | the operand set `build/hlp-gen2`: every item, its designed flip counts re-derived from the files, and each item's own zero |
| `code.sha256` | `tools/claims-v3/lib.sh` and every `tools/claims-v3/hlp/` file as the box ran them |
| `ident/` | the card's identity, read only: `et-lab-manifest`, `ettelem config`, and the firmware revisions |
| `aifoundry3/hlp/p791x`, `p792x` | per pass: `block.json`, `configs.json`, `config_start.json`, `config_end.json`, `gen.sha256`, `manifest.txt` (`et-lab-manifest`), `marks.jsonl`, `run.log`, `runs.jsonl`, `code.sha256`, `telemetry.jsonl.gz`, `tiles/` (the tiles the host dumped, byte-compared against the generated set) |
| `logs/` | the two queue logs |

**Operand set and code.** `build/hlp-gen2`, generated and `--check`ed on the box before the first block-B launch;
**every one of the 62 operand files block A ran is byte-identical in it** (62 of 62, checked on the box). Block A
ran commit `2a72d352`'s `make_hlp.py`, `run_hlp.py` and `block.sh`; block B ran `4216f1fb`'s, whose only change to
block A's items is additive.
