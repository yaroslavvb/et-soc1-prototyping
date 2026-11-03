# E149: the ET-SoC-1's power model checked on a GPU, an A100 under its cap

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6, "a power model across kinds"**, asked on a GPU, and the part of **item 2, "a GPU measured the same way"**, that
[E135](../2026-11-02-e135-a100-kinds/README.md) left: E135 measured the A100 at its 400 W cap, where power reads the
cap; here it runs under the cap, where power reads the data.*

*Mon 2 Nov 2026 (week 45), Q138. The owner's words that evening: "all cards are available, feel free to settle any
unanswered questions regarding horace's power model using mordast, runs on aifoundry and modal for sanity checks on GPUs
(don't exceed $20 on modal)", with Q137's goal, "to be able to predict the power requirement and heat generation of
various kinds of numeric computations as accurately as possible". Pre-registered in `afc11eac`
([`tools/gpu/e149/E149.md`](../../../../tools/gpu/e149/E149.md): both stages' kinds, the model form, the rules, a
selftest), pushed at 19:23:52 PST before any GPU call; amendment A1 (`670c1e50`, `125d9133`) after two declared smokes
and before the first stage-1 call; A2 and A3 (a board-scaled secondary arm for stage 2, and a seventh model, G4) written while
stage 1 ran and pushed in `dd226347` before any of its data was fetched; the freeze, `e929b00f`, before stage 2's first
call. Modal workspace `yaroslavvb`, app `e149-gpu-model-check`.*

## Results

**Under its 400 W cap an A100's power follows the operand bits the way the ET-SoC-1's model says, in kind: changes of
bits, not ones; zeros by what they stop switching; a random sign costs and a fixed one does not. But the operands whose
bits are counted as "consecutive" are not the ET-SoC-1's.** The ET-SoC-1 model's pairing, neighbours along K, fails on
the GPU (R4b): a GPU's operands meet on a wire a tensor-core K-step (16–32 elements) or a row apart.

**Blind, on 17 kinds measured on two boards the fit never saw, the toggle model in the ET-SoC-1's form (G1) predicts
power to 24.7 W rms, 16% of the 154.7 W from zeros to random bf16, biased high by 13.0 W.** So its registered accuracy
rules **fail** (P1: rms ≤ 15.5 W; P2: |bias| ≤ 7.7 W), while its coverage and its two comparisons **hold**: 16 of 17
kinds inside its frozen 90% band (P3, the checkerboard outside), 2.6 times better than power as density alone (G0, 63.7
W; P4), and better than static bits (S1, 33.8 W; P5). **The best registered form, G4, a K-lag of 16 plus the row
direction, predicts the same 17 kinds to 12.8 W rms (8.2% of the span)**, and 10.9 W with A2's board anchor; G1 plus the
result path (G2) reads 17.7 W with the smallest bias (−2.4 W).

**Heat: the A100's die rises 0.094 and 0.143 °C per board W at steady state on the two stage-1 boards** (0.116 pooled),
about half of it at once (within 0.2 s, the fit's grid edge) and the rest with a 13–40 s time constant (32 s
pooled), so 81% of it within 30 s. **A 30 s hold's rise on a new board is predicted to 1.4 °C rms from its measured
power and to 3.8 °C rms end to end from the bits**, against rises of 0–15 °C: both heat accuracy rules **fail** (H1, H2),
the band's coverage **holds** (H3, 14 of 17), and the two stage-1 boards' coefficients differ by more than the registered
ratio (H4 **fails**, 0.66). Cloud boards differ in cooling, and one board's die wandered ±2–3 °C at constant power
over minutes (post hoc), so heat on a rented GPU is a property of its slot as much as of the data.

| what is predicted, held-out kinds, new boards | before E149 | after E149 | source |
|---|---|---|---|
| **power of a new kind, A100, under the cap** | no GPU model; density alone (G0) **63.7 W** rms, bias +37.0 | ET-SoC-1 form (G1) **24.7 W**, bias −13.0; best registered form (G4) **12.8 W**; G4 with a board anchor **10.9 W** | `score-e149.json` `models`, `secondary_board_scale` |
| **heat of a new kind**, die rise over a 30 s hold | none for the A100 (post hoc on E135's boards, 0.067–0.097 °C/W at 1.7–3.3 °C fits) | **3.8 °C** rms end to end, **1.4 °C** from measured power (1.0 and 2.3 °C on the two boards) | `score-e149.json` `heat`, `heat_holds` |
| die rise per board W, steady | — | **0.094 / 0.143 °C/W** (two boards), τ ≤ 0.2 s and 13–40 s, leakage 1.8–2.6 W/°C | `model-e149.json` `heat` |

Every number in this section comes from `score-e149.json` (the blind scores and rules), `model-e149.json` (the frozen
fit) and `reduce-stage1.json` / `reduce-stage2.json` (the measured watts); `summarize_e149.py` prints the tables below
from them.

## Stage 1: what an A100's power follows, under its cap

**Every one of stage 1's 404 cell windows ran at 1410 MHz in every 100 ms sample with no clock-event reason bit** (the
hottest drew 341 W), so the watts below read the data, not the cap (V0 **HOLDS**: 92 of 92 kinds valid on both boards;
`model-e149.json` `rules_stage1.V0`). **At that clock the data never changed the speed**: bf16 ran 157.1 TFLOPS over
all 52 kinds (0.7% spread), fp16 108.7 TFLOPS and int8 148.2 TOPS at 1024³ (`reduce-stage1.json` `kinds.*.tflops`).
In bf16 at 2048³, zeros drew 181.5 W, a constant 1.0 matrix 203.9 W and random normal 338.5 W
(`kinds["bf16.<kind>"].p_abs`). Below, y is watts over the same GEMM on zeros, ± SE over the valid replicates (2 passes ×
2 boards), from `reduce-stage1.json` `kinds.*.y`, `se`.

| bf16 zeros | 0% | 25% | 50% | 75% | 90% | 100% |
|---|---:|---:|---:|---:|---:|---:|
| scattered | 154.7 ± 3.6 | 153.2 ± 3.8 | 127.6 ± 2.0 | 95.4 ± 2.3 | 68.2 ± 1.6 | 0.0 ± 0.6 |
| blocks of 64 along K | 154.7 ± 3.6 | 145.1 ± 4.0 | 119.7 ± 3.4 | 79.3 ± 2.6 | 29.2 ± 1.2 | 0.0 ± 0.6 |

One-sided 50% scattered: A only 149.4 ± 3.9, B only 136.9 ± 3.5. int8 scattered 0/25/50/75/90%: 84.0 ± 3.5, 78.0 ± 3.5, 67.3 ± 4.0, 47.7 ± 3.0, 33.5 ± 1.8; blocks 50%: 62.6 ± 2.3. fp16 50%/75% scattered 97.8 ± 0.9 / 67.2 ± 0.9, 50% blocks 89.1 ± 1.2.

| Hamming ladder from the base 1.0 (k flips per element) | base | rungs |
|---|---:|---|
| bf16 mantissa (7 bits), k = 1, 2, 3, 5, 7 | 18.7 ± 2.0 | 68.8 ± 1.8, 90.3 ± 2.6, 100.2 ± 2.4, 99.0 ± 2.3, 25.7 ± 0.5 |
| bf16 exponent (low 5 bits), k = 1, 2, 3, 5 | 18.7 ± 2.0 | 66.1 ± 1.2, 72.7 ± 2.8, 70.6 ± 1.2, 14.7 ± 1.4 |
| bf16 sign, p = 0.10, 0.25, 0.50 | 18.7 ± 2.0 | 36.0 ± 1.1, 49.5 ± 1.3, 60.3 ± 2.1 |
| fp16 mantissa (10 bits), k = 1, 3, 5, 7, 10 | 12.0 ± 0.9 | 51.4 ± 0.8, 82.2 ± 1.1, 93.7 ± 1.1, 85.0 ± 0.8, 18.8 ± 1.4 |
| fp16 exponent (low 3 bits), k = 1, 2, 3 | 12.0 ± 0.9 | 35.1 ± 1.2, 32.8 ± 0.4, 7.5 ± 1.3 |
| fp16 sign, p = 0.25, 0.50; A only 0.50 | 12.0 ± 0.9 | 29.4 ± 1.3, 35.1 ± 0.6, 33.0 ± 1.2 |
| int8 bits 1–7 from 1, k = 1, 2, 3, 5, 7 | 3.6 ± 1.0 | 47.9 ± 2.1, 69.5 ± 3.4, 76.9 ± 3.1, 79.6 ± 3.8, 9.4 ± 0.8 |
| int8 p = 0.5 in bits 1–3, 4–6, 7; bit 7 on A only | 3.6 ± 1.0 | 39.3 ± 2.0, 39.8 ± 2.9, 21.1 ± 1.8, 15.4 ± 0.5 |

Single positions (p = 0.5), bf16 mantissa bits 0, 3, 6: 44.7 ± 2.0, 40.7 ± 0.4, 38.5 ± 1.2; exponent bits 0, 4: 37.1 ± 1.1, 45.0 ± 1.3; fp16 mantissa bits 0, 5, 9: 23.6 ± 1.2, 28.0 ± 1.1, 23.0 ± 0.5. One-sided bf16 mantissa k = 3 A / B: 65.8 ± 1.5 / 42.7 ± 2.1; exponent k = 2 A / B: 62.9 ± 1.7 / 40.2 ± 1.7; fp16 mantissa k = 5 on A: 55.6 ± 1.0; int8 random on A / B: 40.8 ± 1.3 / 58.9 ± 3.3.

| bf16 signs, magnitude 1.5 | fixed + | A −, B + | random both | random A | random B | abs(randn), fixed + | same, random signs |
|---|---:|---:|---:|---:|---:|---:|---:|
| y | 22.0 ± 0.4 | 22.8 ± 1.9 | 65.1 ± 1.8 | 58.3 ± 1.6 | 32.7 ± 1.0 | 128.4 ± 4.6 | 157.1 ± 3.2 |

| bf16 order | sorted along K | the same values shuffled | magnitudes sorted, random signs | sorted along M/N | sorted along K, rolled |
|---|---:|---:|---:|---:|---:|
| y | 103.2 ± 2.5 | 156.2 ± 4.0 | 128.7 ± 3.9 | 94.4 ± 2.4 | 143.0 ± 2.9 |

| square wave along K, block b | 1 | 2 | 4 | 8 | 16 | 64 |
|---|---:|---:|---:|---:|---:|---:|
| y | 72.2 ± 3.0 | 80.0 ± 2.4 | 82.7 ± 1.9 | 88.4 ± 3.2 | 90.6 ± 1.8 | 85.6 ± 2.8 |

What these say, in the ET-SoC-1 model's terms (the rules are `model-e149.json` `rules_stage1`):

- **Power follows bit flips, not ones** (R2 **HOLDS** in all four ladders). From the constant 1.0, flipping k random
  mantissa bits per element raises bf16's power by 50 W at k = 1 and 81 W at k = 3, and when every element has all
  seven flipped (a constant again, 1.9921875) it falls back to 7 W over the base. The exponent's low bits (+52 W at k = 3,
  −4 W all flipped), fp16's mantissa (+82, +7) and int8's bits 1–7 (+73, +6) do the same. The few watts the all-flipped
  constants keep are what a value's ones cost; the rest is flips.
- **Flips do not add**: at k = 1 neighbouring operands differ in 1.7 mantissa bits on average (per operand), at k = 3
  in 3.4; twice the changes cost 1.6 times the watts (50 W and 81 W), so the price per flip falls as flips multiply, as
  on the ET-SoC-1 (E70's shared wires) and in Gregersen et al.'s A100 ladder (the lab's reduction, Q130(e) §2).
- **Zeros save what they stop switching** (R1a **HOLDS** in bf16 and int8): 25% scattered zeros save 1.5 W, 50% 27 W,
  75% 59 W, 90% 87 W in bf16. **Zeros in blocks save more than scattered zeros** (R1b **HOLDS**: 7.9 W more at 50%,
  just at its 2-SE bar, and 16.1 W at 75%; 39 W at 90%): a scattered zero still flips its neighbours' bits.
  Zeros in B save more than zeros in A (50% on B alone −17.8 W, on A alone −5.3 W).
- **A random sign costs, a fixed one does not** (R3a, R3b **HOLD**): at constant magnitude 1.5, random signs on both
  operands cost 43.1 W more than all positive; A negative and B positive costs +0.8 W ± 1.9.
- **The left operand's flips cost about twice the right's**: mantissa k = 3 on A alone +47 W, on B alone +24 W; the
  exponent +44 against +22 W; a random sign +36 against +11 W. (On the ET-SoC-1 it is the other way round: A pays about
  two thirds of B's price per flip, E113, E125.) Which operand cuBLAS feeds to which port is not known here.
- **Order matters, but not along K alone** (R4a **HOLDS**): randn sorted along K costs 53 W less than the same values
  shuffled; sorted along M (A) and N (B) instead, 62 W less; sorted along K and each row rolled out of step, only 13 W
  less. So most of what sorting saves comes from neighbouring rows holding similar values at the same k.
- **The ET-SoC-1 model's pairing, consecutive operands along K, is not the A100's** (R4b **FAILS**). The period-2 square
  wave (b = 1, all seven bits flip between every pair of neighbours along K) costs 72 W, *less* than the period-128 one
  (86 W); the six waves rise from b = 1 to b = 16 (72, 80, 83, 88, 91 W) and dip at 64. On a GPU the operands that meet
  one after another on a wire are a tensor-core K-step or a row apart, and the lag scan picks **K-lag 32** (`lag_scan`):
  G1's form at lag 32 reads a pooled nested error of 19.4 W against 34.9 W at lag 1.
- **The two boards agree** (B1 **HOLDS**, just): board B's y on board A's has a slope of 0.918 (limit 0.9–1.1) and an
  rms difference of 7.33 W against a 7.74 W limit; random bf16 read 160.7 W over zeros on board A (an 80GB part) and
  148.8 W on board B (a 40GB part).

## The models, fitted on stage 1 and frozen

Nested = leave-one-kind-out, rms in W (`model-e149.json` `models.<model>.<format>.rms_in`, `rms_loko`; `lag_scan`, `lag_scan_G4`).

| model | bf16 in · nested | fp16 in · nested | int8 in · nested |
|---|---|---|---|
| G0 | 53.65 · 54.33 | 41.58 · 42.93 | 33.76 · 35.16 |
| G1 | 22.90 · 28.61 | 5.55 · 56.30 | 6.44 · 13.64 |
| G1s (lag 32) | 17.73 · 20.03 | 3.71 · 22.96 | 5.76 · 11.95 |
| G2 | 18.58 · 23.54 | 5.27 · 54.09 | 6.37 · 14.28 |
| G3 | 9.34 · 30.58 | 3.26 · 768.00 | 4.59 · 1536.41 |
| G4 (lag 16) | 8.39 · 94.46 | 3.42 · 321.35 | 5.60 · 315.25 |
| S1 | 35.84 · 45.16 | 29.31 · 188.91 | 12.09 · 28.29 |

Lag scan (G1's form at K-lag s; pooled nested rms over the three formats, W): s = 1: 34.91, s = 2: 33.13, s = 4: 32.65, s = 8: 30.51, s = 16: 27.82, s = 32: 19.43.

- **The registered primary, G1 (the ET-SoC-1 form, lag 1), predicts stage 1's kinds to 28.6 W (bf16), 56.3 W (fp16)
  and 13.6 W (int8) out of kind**, against 54.3, 42.9 and 35.2 W for density alone (G0). Its worst misses are the square
  waves and the rolled sort (bf16) and fp16's one-sided arms, where two fp16 rows set the A − B term.
- **G1s, the same form at K-lag 32, is the best frozen predictor on stage 1**: 20.0, 23.0 and 12.0 W. Its misses are
  the square waves at b = 2–16, which have no flips at lag 32 at all and still cost 80–91 W: the row direction carries
  them.
- **The forms with the row direction (G3, G4) fit stage 1 best in sample (8–9 W in bf16) and worst out of kind**
  (hundreds of watts): for kinds random along rows, the row-direction and K-lag counts are nearly the same numbers, so
  unregularised least squares trades huge opposite coefficients, and the few kinds that separate them (the sorts and the
  square waves) cannot pin both. That is a finding about this design, reported as found (post hoc, no verdict).
- The coefficients are predictors, not a price list (several are negative). Read physically, G1s's flips of a mantissa
  bit cost about 115 fJ (bf16), 148 fJ (fp16), and an int8 magnitude bit 136–149 fJ at the measured multiply-add rate,
  per flip of one operand's bit at one multiply-add: the same order as the ET-SoC-1's 118–136 fJ per flipped bit.

## Stage 2, blind: 17 held-out kinds on two new boards

Measured after the freeze (`e929b00f`, 20:14:46 PST) in run `e149-20261102-r2` (20:15–20:40 PST): unit A an
A100-SXM4-80GB, unit B an A100-SXM4-40GB, neither one of stage 1's boards (`reduce-stage2.json` `units.*.static`). Every
operand's sha256 matched the predictions' (`do_score` asserts it), and every window held 1410 MHz with no reason bit
(the hottest, the power law, drew 345 W). y is watts over each format's zeros, measured ± SE over 2 passes × 2 boards
(`reduce-stage2.json` `kinds`); the predictions are `predictions-e149.json` `kinds.*.pred`.

| kind | measured y ± SE | G1 | G1s | G0 | S1 | G2 | G3 | G4 | G1 band | inside |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| bf16.checker | 135.9 ± 2.4 | 214.6 | 65.9 | 19.8 | 67.9 | 122.4 | 216.1 | 149.3 | ±47.1 | no |
| bf16.gelu_w | 146.4 ± 3.9 | 160.0 | 146.8 | 79.1 | 130.7 | 162.9 | 158.4 | 157.9 | ±47.1 | yes |
| bf16.lowrank | 151.0 ± 2.6 | 159.4 | 153.9 | 79.1 | 135.4 | 165.0 | 158.8 | 159.0 | ±47.1 | yes |
| bf16.onebit | 30.8 ± 1.0 | 18.6 | 30.6 | 19.0 | 4.9 | 2.8 | 16.6 | 16.5 | ±47.1 | yes |
| bf16.pi | 17.0 ± 1.2 | 35.3 | 39.8 | 79.1 | 44.8 | 63.3 | 27.2 | 27.3 | ±47.1 | yes |
| bf16.powerlaw | 161.4 ± 3.1 | 189.5 | 201.1 | 79.1 | 131.2 | 162.5 | 189.4 | 190.4 | ±47.1 | yes |
| bf16.rand | 118.0 ± 1.4 | 107.8 | 110.8 | 78.7 | 77.5 | 107.7 | 114.1 | 116.8 | ±47.1 | yes |
| bf16.randn (seen) | 151.3 ± 3.6 | 158.7 | 153.3 | 79.1 | 135.6 | 165.1 | 158.2 | 158.3 | ±47.1 | yes |
| bf16.sortrand | 86.4 ± 2.6 | 67.1 | 95.5 | 78.9 | 77.4 | 89.3 | 83.2 | 95.7 | ±47.1 | yes |
| bf16.sparse75 | 89.4 ± 1.8 | 94.6 | 96.6 | 4.9 | 34.0 | 100.1 | 93.2 | 94.0 | ±47.1 | yes |
| bf16.sparse_neg | 105.2 ± 1.8 | 109.3 | 130.0 | 19.7 | 38.2 | 91.2 | 115.5 | 117.5 | ±47.1 | yes |
| bf16.ternary | 77.1 ± 1.8 | 102.2 | 99.4 | 35.1 | 64.3 | 49.9 | 91.7 | 89.0 | ±47.1 | yes |
| bf16.twos | 10.2 ± 1.0 | 35.3 | 39.8 | 79.1 | 4.0 | 10.3 | 27.2 | 27.3 | ±47.1 | yes |
| fp16.gelu_w | 117.7 ± 0.7 | 136.9 | 132.4 | 48.0 | 101.3 | 136.2 | 138.3 | 132.1 | ±92.6 | yes |
| fp16.rand | 98.4 ± 1.1 | 114.5 | 111.2 | 48.0 | 54.0 | 110.6 | 114.0 | 109.2 | ±92.6 | yes |
| int8.q_gelu_w | 80.4 ± 1.7 | 90.0 | 89.4 | 46.6 | 77.2 | 87.9 | 88.4 | 88.6 | ±22.4 | yes |
| int8.ternary | 65.2 ± 2.0 | 76.3 | 77.8 | 22.0 | 78.6 | 71.8 | 80.5 | 77.8 | ±22.4 | yes |
| int8.twos | 4.1 ± 1.3 | 3.4 | 4.8 | 49.5 | -4.0 | 2.3 | 1.8 | 5.6 | ±22.4 | yes |

| model | rms | bias | worst | n |
|---|---:|---:|---:|---:|
| G0 | 63.71 | 37.01 | 116.18 | 17 |
| G1 | 24.66 | -12.95 | 78.69 | 17 |
| G1s | 24.03 | -7.72 | 70.08 | 17 |
| G2 | 17.74 | -2.44 | 46.38 | 17 |
| G3 | 23.43 | -12.93 | 80.15 | 17 |
| G4 | 12.76 | -9.36 | 28.94 | 17 |
| S1 | 33.82 | 22.19 | 68.00 | 17 |

- **The checkerboard decides the pairing.** Its zeros alternate along K and along the rows. Counting flips between
  neighbours along K (G1) predicts 214.6 W, between elements 32 apart (G1s) 65.9 W; it drew **135.9 W**, and the form
  with a K-lag of 16 plus the rows (G4) came within 13 W (149.3 W). It is G1's one kind outside its band.
- **Constants and the result path.** All-π drew 17.0 W and all-twos 10.2 W over zeros. G1 and G1s give every constant
  the same 35–40 W (no flips, all products nonzero). Static bits (S1) and the accumulator term (G2) know twos are cheap
  (4.0, 10.3 W) but overshoot π (44.8, 63.3 W): what separates constants is not settled by stage 1's few constants.
- **Wide exponents and sparse ternary are over-predicted by the flip forms**: the power law (161.4 W measured; G1 189.5,
  G1s 201.1, G2 162.5) and ternary (77.1 W; G1 102.2, G2 49.9).
- **Real-model-like operands land well**: post-GELU activations against LLM-like weights 146.4 W (G1 160.0, G1s 146.8);
  in fp16 117.7 W (G1 136.9); int8-quantized 80.4 W (G1 90.0). Low rank 151.0 W (G1 159.4). Uniform values sorted along K
  86.4 W (G1 67.1, G1s 95.5).
- **G1 reads high on both new boards** (bias −15.2 W on the 80GB part, −10.7 W on the 40GB one): A2's anchor says these
  boards' random bf16 drew 0.94 and 1.02 of stage 1's watts over zeros, which explains part of it (G1 22.9 W rms, bias
  −10.7, scaled).

## Heat

**The A100's die, fitted on both stage-1 sessions** (`model-e149.json` `heat`): a fast part that follows power within
the 0.2 s grid edge and a slow pole; pooled **0.116 °C per board W** at steady state (r₁ 0.060 + r₂ 0.056), τ₂ 31.8 s,
81% reached in 30 s, 1.77 °C rms over 39,024 samples. Board by board: unit A (80GB) **0.094 °C/W**, τ₂ 12.7 s, 0.71 °C
rms; unit B (40GB) **0.143 °C/W**, τ₂ 40.0 s, 2.25 °C rms. A model fitted on one board predicts the other's 30 s rises
to 1.0–1.2 °C rms (`heat.cross`). **Leakage at the held reference load: 2.6 and 1.8 W per °C** (`heat.leakage`), so a
10 °C warmer die costs about 20 W at the same data and clock.

| hold (30 s after 15 s of zeros) | measured rise °C | blind | with measured power | band |
|---|---:|---:|---:|---:|
| bf16.checker | 12.95 | 23.11 | 11.63 | ±4.78 |
| bf16.gelu_w | 11.85 | 15.75 | 11.72 | ±4.78 |
| bf16.lowrank | 12.50 | 15.93 | 12.31 | ±4.78 |
| bf16.onebit | 3.00 | 1.08 | 1.97 | ±4.78 |
| bf16.pi | 2.45 | 3.18 | 0.92 | ±4.78 |
| bf16.powerlaw | 13.00 | 19.10 | 13.01 | ±4.78 |
| bf16.rand | 11.50 | 10.29 | 9.51 | ±4.78 |
| bf16.sortrand | 8.50 | 5.10 | 5.78 | ±4.78 |
| bf16.sparse75 | 6.50 | 8.98 | 6.52 | ±4.78 |
| bf16.sparse_neg | 9.05 | 10.64 | 7.98 | ±4.78 |
| bf16.ternary | 5.50 | 10.57 | 6.04 | ±4.78 |
| bf16.twos | -0.20 | 2.30 | -0.61 | ±4.78 |
| fp16.gelu_w | 11.40 | 13.73 | 9.43 | ±8.90 |
| fp16.rand | 8.00 | 10.70 | 6.82 | ±8.90 |
| int8.q_gelu_w | 8.50 | 9.71 | 6.12 | ±2.78 |
| int8.ternary | 7.00 | 8.58 | 5.31 | ±2.78 |
| int8.twos | 0.00 | -0.51 | -0.90 | ±2.78 |

**The blind rise** (G1's frozen power through the frozen heat model, from the pre-hold's measured zeros) reads **3.78
°C rms**, bias −2.16 °C (H1 **FAILS**, ≤ 0.8 °C registered): the checkerboard alone, predicted at 214.6 W, is predicted
to rise 23.1 °C against 12.95 °C. **With each hold's measured power the heat model reads 1.39 °C rms**, bias +1.06 °C
(H2 **FAILS**, ≤ 0.6 °C): 1.04 °C on board A and 2.29 °C on board B, whose die ran hotter than the pooled model
(`score-e149.json` `heat_holds`). 14 of 17 rises fall inside the frozen heat band (H3 **HOLDS**), which was wide (±4.8
°C in bf16) because it carries G1's power band. A2's anchor (each board's randn hold) scales the blind rises by 0.72 and
0.93 and reads 2.35 °C rms.

## What this does to predicting power and heat

**Section 11 item 6 ("a power model across kinds"), on a GPU: narrowed.** The terms of the ET-SoC-1's model, operand
bit changes by field and side, a gate term for zeros and a sign term, **measured** on an A100 under its cap: every
ladder rule of the model's structure holds there (R1a, R1b, R2, R3a, R3b, R4a), and the per-flip prices come out at the
ET-SoC-1's order (about 115–150 fJ per mantissa or magnitude flip of one operand at one multiply-add, at the measured
rate). **Tested**: the model's pairing of operands, neighbours along K, is **corrected** for the GPU (R4b fails; the lag
scan and the checkerboard put it at K-steps of 16–32 elements plus the row direction). **Out-of-sample error, power**
(17 held-out kinds, two new boards): **before**, no model, and density alone 63.7 W rms (41% of the zeros-to-random
span); **after**, 24.7 W (16%) for the ET-SoC-1 form and 12.8 W (8.2%) for the best registered GPU form, 10.9 W (7%)
with a board anchor. **Heat**: the A100's die rise per board W (0.094–0.143 °C/W) and its time constants (≤ 0.2 s and
13–40 s) **measured** for the first time; a new kind's 30 s rise **before**: no A100 model; **after**: 3.8 °C rms end to
end, 1.4 °C rms from measured power, with the board's own slot the largest remaining term.

**Section 11 item 2 ("a GPU measured the same way"), its under-the-cap part: answered for one GPU model.** E135
measured power at the cap; E149 holds 1410 MHz in every window and reads the data's watts at 2048³ (bf16) and 1024³
(fp16, int8). Still open: a lower cap (needs root on the GPU), another GPU model (E150, the optional lane), other GEMM
shapes.

## Against the ET-SoC-1

| | ET-SoC-1 (its resident loop, the kinds harness) | A100 (cuBLAS GEMM under its cap, E149) |
|---|---|---|
| what costs | operand bits changing between consecutive micro-ops; flips share wires (E70) | the same: changes, not ones (R2); flips share wires (k = 1 → 3: twice the changes, 1.6× the watts) |
| which operands are consecutive | the micro-op stream along K (PRM 9.4 order) | K-steps 16–32 apart and neighbouring rows (R4b fails at lag 1; G4 best blind) |
| zeros | gated lanes, a gate's state change ~158 fJ (M6's `gtr`) | blocks save more than scattered zeros (R1b); zeros in B save more than in A |
| signs | a random sign's ~5 W (fp32), held signs free | a random sign +43 W at constant magnitude, a fixed negative +0.8 ± 1.9 W (R3a, R3b) |
| A against B | A pays about two thirds of B's price per flip (E113, E125) | bf16: A's flips cost about twice B's; int8: B's random costs more than A's |
| per flip | 118–136 fJ per flipped bit (whole board) | about 115–150 fJ per operand-bit flip at one multiply-add (G1s, whole board over zeros) — same order, not like for like |
| speed at a fixed clock | data-independent | data-independent (0.6–2.6% spread over every kind) |
| blind power error | M5 0.36 W, M6 0.41 W rms (E140, 600 MHz) | G1 24.7 W, G4 12.8 W rms (16% and 8% of the span) |

The two kernels differ (a resident loop on one tile against a streaming GEMM), so the table sets kernel against kernel
(E135's correction C1), and no chip-level contrast is drawn from the size of an error.

## Registered against what happened

| rule | registered | measured | verdict |
|---|---|---|---|
| V0 | ≥ 90% of stage-1 kinds valid on each board | 92 of 92 on both | **HOLDS** |
| R1a | no resolved rise along the scattered zero ladder (bf16, int8) | none | **HOLDS** (both) |
| R1b | blocks < scattered at 50% and 75%, resolved | +7.9 W (bar 7.9) and +16.1 W (bar 6.9) | **HOLDS** |
| R2 | middle rung up, all-flipped constant back below half (four ladders) | bf16 mant +81.4 / +7.0, exp +51.9 / −4.0, fp16 mant +81.7 / +6.8, int8 +73.3 / +5.8 W | **HOLDS** (all four) |
| R3a | random sign > fixed, resolved | +43.1 ± 1.9 W | **HOLDS** |
| R3b | fixed negative ≈ fixed positive | +0.8 ± 1.9 W (limit 4.3) | **HOLDS** |
| R4a | sorted along K < shuffled, resolved | sorted 53.0 ± 4.7 W below | **HOLDS** |
| R4b | the ET form's lag: period-2 wave > period-128, resolved | the period-2 wave 13.4 ± 4.1 W below | **FAILS** |
| B1 | boards agree: slope 0.9–1.1, rms ≤ 5% of S | slope 0.918, 7.33 W (limit 7.74) | **HOLDS** |
| P1 | G1 blind rms ≤ 0.10 S (15.5 W) | 24.7 W | **FAILS** |
| P2 | G1's absolute bias ≤ 0.05 S (7.7 W) | −13.0 W | **FAILS** |
| P3 | ≥ 13 of 17 inside G1's 90% band | 16 of 17 | **HOLDS** |
| P4 | G1 rms ≤ 0.7 × G0's | 24.7 against 63.7 W | **HOLDS** |
| P5 | G1 rms < S1's | 24.7 against 33.8 W | **HOLDS** |
| H1 | blind hold rise rms ≤ 0.8 °C | 3.78 °C | **FAILS** |
| H2 | with measured power, rms ≤ 0.6 °C | 1.39 °C | **FAILS** |
| H3 | ≥ 13 of 17 rises inside the heat band | 14 of 17 | **HOLDS** |
| H4 | the two stage-1 boards' die rise per W within 0.8–1.25 | 0.66 | **FAILS** |

Sources: `model-e149.json` `rules_stage1`, `score-e149.json` `rules`. 12 of the 18 rules hold (R1a counted once for its two
formats, R2 once for its four ladders); R4b, P1, P2, H1, H2 and H4 fail.

## How it ran

- **Two declared smokes, then two stages, each stage on two boards at once** (units A and B, two Modal containers
  started together, each on its own A100). Stage 1 (run `e149-20261102-r1`) measured the 92 fit kinds and the heat
  holds; its containers then built stage 2's 21 kinds with the NVML sampler stopped, only to compute their features.
  The models were fitted, frozen and pushed with their predictions; stage 2 (run `e149-20261102-r2`) then measured the
  held-out kinds on two boards the fit never saw, and checked every operand's sha256 against the predictions'.
- **Sizes**: bf16 at 2048³ as registered; fp16 and int8 at 1024³ by A1's rule (at 2048³ cuBLAS runs them at 230
  TFLOPS and 303 TOPS and they reach the cap).
- **A window**: back-to-back GEMMs of one kind, 5 s for a cell and 3 s for the bracketing reference (bf16 randn); the
  power is the mean of the 100 ms NVML readings after 1.5 s (cell) or 1.0 s (reference). y = cell − mean of its two
  references − the same for its format's zeros in that pass: watts over zeros at 1410 MHz, at the reference's thermal
  state. A window counts only if the SM clock read 1410 MHz in every sample and no clock-event reason bit was set (V0).
- **Reads only.** Every command sent to the GPU is an NVML getter or `nvidia-smi -q`; nothing was set.

## Departures, dated

- **D1 = A1 (19:29 and 19:34 PST, before stage 1).** fp16 and int8 run at 1024³, chosen by a rule written before the
  size smoke S2 ran (`sizes-s2.json`): at 2048³ they reach the cap (S0). bf16 stays at 2048³.
- **D2 = A2 (19:35 PST, before any stage-1 data was read).** A board-scaled secondary arm for stage 2 (no verdict).
- **D3 = A3 (19:40 PST, before any stage-1 data was fetched).** One more registered comparison, G4.
- **D4, the boards.** Modal served stage 1's unit A with an A100-SXM4-80GB and unit B with an A100-SXM4-40GB, both
  billed as `A100-40GB`; the two smokes ran on 40GB boards. Both variants have the 400 W limit and 1410 MHz.

## Post hoc (no verdicts)

- **Why the row-direction forms explode out of kind** (G3, G4 nested 30–1,536 W on stage 1): for kinds random along
  rows the row and K-lag counts are nearly equal, so least squares trades huge opposite coefficients, pinned only by the
  sorts and the square waves; int8 has nothing to separate them. G4's good blind score (12.8 W) comes from blind kinds
  that mostly do not separate them either, plus the checkerboard, which does. A design with more row-against-K kinds
  (rows sorted, K shuffled; K sorted, rows shuffled; per-row phase against shared phase) or a constrained fit would pin
  the split; neither ran here.
- **The square waves** have no lag-32 flips at b ≤ 16 and still cost 72–91 W, about what their row-direction flips (3.4
  per operand at any b, from the random phase per row) and a few K-steps predict; they rise with b to 16 and dip at 64.
- **One board's die wandered**: on stage 1's unit B the heat model's residual moved between −3.5 and +2.1 °C in
  two-minute bins at nearly constant power (48.5 °C at 263 W, then 55.7 °C at 279 W); unit A's stayed within ±0.4 °C
  (`heat_resid.py` in the lane's scratch; the samples are `logs/e149-20261102-r1/B/samples/`). A shared multi-GPU
  server's inlet or fans are the likely cause; nothing here measured them.
- **E135's boards, the same heat fit** (post hoc, its committed logs): 0.097 and 0.067 °C per board W with τ₂ 20 and
  80 s, at 1.7 and 3.3 °C rms, its long idle cooling waits making the poor fits: the A100 coefficient spans 0.067–0.143
  °C/W over four boards.
- **Single positions**: bf16's mantissa bits 0, 3 and 6 each flipped at p = 0.5 cost 44.7, 40.7 and 38.5 W (low bits a
  little dearer), exponent bits 0 and 4 37.1 and 45.0 W, fp16's mantissa bits 0, 5, 9 23.6, 28.0, 23.0 W.

## What this cannot say

- It is a predictor in the ET-SoC-1 model's form, not the A100's circuit: which operand pairs meet on which wire is set by
  cuBLAS's kernel and the tensor cores' dataflow, which nothing here reads; the lag and row comparisons say only which
  counting predicts best.
- One GPU model (A100-SXM4, 40GB and 80GB parts, four boards), one library (cuBLAS 12.4.5.8 through torch 2.5.1), square
  K-contiguous operands at two sizes, 1410 MHz only; fp16 and int8 run at 1024³, where their kernels draw under the cap,
  so their watts are not bf16's kernel's.
- Board power is NVML's reading (every 100 ms, updating every 0.1–0.2 s, E135 C10); the die temperature is whole degrees.
- The heat model is linear and two-pole; the cloud slots' cooling is neither measured nor controlled.

## Cost

**Metered $4.48** (`billing.json`: `modal billing report --for today --show-resources --json`, read 20:42 PST, app
`e149-gpu-model-check` only): stage 1 $2.52, stage 2 $1.73, smoke S0 $0.11, smoke S2 $0.13; the GPU line $4.17 = 7,144
GPU-seconds at $2.10/h. The ledger of function-seconds from the Volume's `STARTED`/`DONE` (`ledger.json`): 7,101 s, $4.45
at the registered rate. Projected $5.19, ceiling from the timeouts $8.08, E149's cap $11 (stop at $10). Against the
owner's $20 for GPU checks: E135's $3.62 plus E149's $4.48 = $8.10 (E150, if it runs, adds its own). No container is
left running; the Volume `e149-gpu-model-check` (about 2 MB, every log committed here) remains.

## Files

| path | what |
|---|---|
| `logs/<run>/<unit>/` | every run as the Volume holds it: `steps/NNN_<label>.json.gz` (each step's record: the plan entry, every window's host times, calls and GPU time), `samples/NNN.jsonl.gz` (every 100 ms NVML sample), `features-<set>.json.gz` (each kind's operand-bit features and the sha256 of its two operands), `plan.json`, `STARTED`, `DONE` |
| `reduce-stage1.json`, `.txt` | stage 1's windows reduced (`analyze_e149.py reduce`): d and y per window, validity, y per kind and per board |
| `model-e149.json` | **the frozen models** (`analyze_e149.py fit`): G0, S1, G1, G1s, G2, G3, G4 per format, coefficients, in-sample and nested (leave-one-kind-out) errors, the lag scan, the bands, the heat model, the leakage slope, stage 1's rules |
| `predictions-e149.json`, `.txt` | the frozen predictions for stage 2's kinds (`analyze_e149.py predict`), from stage 1's feature records |
| `reduce-stage2.json`, `.txt` | stage 2's windows and holds reduced |
| `score-e149.json`, `.txt` | the blind scores and rules P1-P5, H1-H4 (`analyze_e149.py score`) |
| `sizes-s2.json` | amendment A1's size rule applied to S2 (`choose_sizes_e149.py`) |
| `ledger.json`, `billing.json` | GPU-seconds per call (`ledger_e149.py`) and the metered bill by app |
| `summary.md` | the tables above, printed by `summarize_e149.py` from the JSON files |
| `fit-stage1.txt`, `predictions-e149.txt` | the fit's and the predictions' printed summaries |
