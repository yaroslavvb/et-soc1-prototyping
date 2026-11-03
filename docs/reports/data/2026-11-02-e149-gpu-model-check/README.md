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

## Corrections after verification

*Mon 2 Nov 2026 (week 45), about 21:40 PST, at the desk: no GPU call, no Modal app, no card. An independent verifier
re-derived E149 from the committed logs (the spend to the cent; the order of registration, amendments, freeze and calls;
the cap test over every sample; all five derived JSON files rebuilt with zero differences; every registered number and
verdict) and found three major faults and eleven minor ones. I checked each against the committed files, and all hold;
one more slip turned up in this pass (C14). The wrong sentences are replaced in place below, the larger ones marked
"corrected after verification", so this README reads as corrected. **No frozen file, data file, registered number,
rule or verdict changed**: `model-e149.json`, `predictions-e149.json`, `reduce-stage1.json`, `reduce-stage2.json`,
`score-e149.json` and the registration's text are as committed, and a dated note was appended to
[`E149.md`](../../../../tools/gpu/e149/E149.md). The new numbers come from [`posthoc_e149.py`](posthoc_e149.py) (post
hoc, no verdicts) into [`posthoc.txt`](posthoc.txt) and [`posthoc.json`](posthoc.json), by the section (§) named.*

- **C1, major: board B's 0.143 °C/W is a fit bent by its slot's drift, not the board's gain.** Inside one 180 s randn
  hold at 319–329 W, B's die read 53.0 °C at 90 s, 57.9 °C at 150 s and 56.0 °C at 180 s; the fit absorbs that with a
  +7.5 °C initial-transient term and a 40 s pole. Model-free steps on the same holds read **0.098–0.112 °C/W on B** and
  0.092–0.098 on A, beside A's fit of 0.094 (§2); their ratio A/B, 0.87–0.94, sits inside H4's 0.8–1.25. **H4 stays
  FAILS as registered** (the fits' ratio, 0.66). So "the boards differ (an 80GB and a 40GB part)" and the A100's
  "0.094–0.143 °C/W" go: the die rises about 0.1 °C per board W on both boards. E135's two boards fit too poorly to quote
  as gains (1.7 and 3.3 °C rms; on its board B the slow pole all but vanishes, r₂ 0.001; §12), so "0.067–0.143 °C/W over
  four boards" goes too.
- **C2, major: y carries each window's own leakage, and the blind heat path counts it twice.** The fast pole (τ₁ ≤ 0.2 s,
  r₁ 0.060 °C/W) settles inside a window's 1.5 s settle, so a zeros cell's die runs 9.3 °C below its bracketing
  references (the slope of that difference on the watts, 0.062 °C/W, is r₁; §4). y is watts over zeros with each window
  at its own fast-pole temperature, not "at the reference's thermal state" as E149.md puts it: random bf16's 154.7 W
  carries 17–25 W of leakage (11–16%; λr₁ 0.106 on board B, 0.156 on A, 0.131 pooled). **So the per-flip prices are upper
  bounds on switching energy by that share**: bf16's mantissa 115 fJ is about 97–103 fJ without it, fp16's 148 fJ
  125–132 fJ, int8's 136–149 fJ 115–133 fJ (§10). The registered blind heat path adds λ × the whole simulated rise on top
  of G1's y, which already holds the fast pole's part: over the 34 blind holds its power ran 34.0 W above the measured,
  12.9 W of it G1's own error and 21.1 W (sd 11.5) the path's construction (§5). Post hoc, with no verdict, the
  registered 3.77 °C rms becomes **2.53–2.68 °C** without the double count (three ways of removing it), 1.43 °C with each
  kind's measured y in place of G1's, and **1.06–1.16 °C** with both; the measured power (H2) gives 1.39 °C. **So most of
  the blind 3.8 °C is the power path (G1's error, and the double count that compounds it); the heat model and the slot
  set a floor of about 1.1–1.4 °C** (about 1.1 °C on board A, 2.0–2.3 °C on board B, whose slot drifted). This README
  had named the slot's cooling the largest remaining term. E150, which would reuse this frozen path, should state the
  double count in its registration and score a corrected arm beside the registered one.
- **C3, major: only "not lag 1" is confirmed; which pairing the A100 pays for is open.** R4b fails, so neighbours along K
  are not the A100's pairing. Stage 1's lag scan prefers a K-lag of 32, but blind the lag-32 form does no better than lag
  1: 24.0 against 24.7 W rms, closer on 10 of 17 kinds, and 17.5 against 16.1 W without the checkerboard (§7). Adding
  the row direction helped (G3 13.5 W without the checkerboard; G4 12.8 W, unstable on stage 1). Nothing here reads which
  operands meet on a wire, so "a GPU's operands meet on a wire a tensor-core K-step (16–32 elements) or a row apart" and
  "the lag scan and the checkerboard put it at K-steps of 16–32 elements" go.
- **C4.** P3's 16 of 17 sit inside bands of ±47 W (bf16), ±93 W (fp16) and ±22 W (int8), 30%, 60% and 14% of the span,
  wide because G1's own nested errors were (§8).
- **C5.** R1b's 50% arm clears its 2-SE bar by 0.008 W (7.888 against 7.880 W; the 75% arm +16.1 ± 3.4 W against 6.9), and
  B1 holds narrowly (slope 0.918 against a floor of 0.9; 7.33 against 7.74 W) (§8). This README said "just" for both; the
  margins are now given.
- **C6.** A kind's watts in the stage-2 table and bullets are y, over the same GEMM on zeros: the checkerboard cost
  135.9 W over zeros while the board drew 320.2 W (§9).
- **C7.** The hottest stage-1 kind averaged 341 W; the hottest single windows drew 355.7 W (a cell) and 355.9 W (a
  reference), 44 W under the 400 W limit, so V0 is unaffected (§1).
- **C8.** G4's 12.8 W and 10.9 W are the best of seven registered forms, picked after scoring, from a fit whose stage-1
  nested error ran to 94–321 W; G1's 24.7 W is the registered result.
- **C9.** Item 2 is **narrowed**, not answered: E149 adds power by kind under the cap, at a fixed 1410 MHz, for one GPU
  model. None of item 2's open parts (a lower cap, his board and an H100, other shapes, an ET-SoC-1 GEMM limited the same
  way) is touched.
- **C10.** The functions' timeouts cap the spend at **$8.66** with A1's smoke S2 (900 s + 900 s + 2 × 3,300 s + 2 × 2,700 s
  at $2.2586 an hour); the registration's $8.08 was written before S2 existed, and by the same arithmetic is $8.09 (§11).
- **C11.** The heat model's per-board errors with measured power over the 17 blind kinds are 1.07 and 2.32 °C; the 1.04 and
  2.29 °C quoted first included the randn hold, which is not blind (§6).
- **C12.** The post hoc heat checks the first README cited from the lane's scratch (`heat_resid.py`, `e135_heat.py`) are
  committed as `posthoc_e149.py` §3 and §12, unchanged in method; their numbers reproduce.
- **C13.** `summary.md` converts each field's centre coefficient to fJ. For bf16's exponent its 176 fJ lies outside the
  five bits the ladders flipped (bits 7–11), where G1s's per-position values run −1 to 201 fJ, mean 100 fJ (§10); no
  exponent price is quoted here.
- **C14 (found in this pass).** The blind holds' measured rises run −0.2 to 13.0 °C (`score-e149.json` `heat.rows`); the
  Results said 0–15 °C.

## Results

**Under its 400 W cap an A100's power follows the operand bits the way the ET-SoC-1's model says, in kind: changes of
bits, not ones; zeros by what they stop switching; a random sign costs and a fixed one does not. But the operands whose
bits are counted as "consecutive" are not the ET-SoC-1's.** The ET-SoC-1 model's pairing, neighbours along K, fails on
the GPU (R4b). Which pairing the A100 pays for is open: stage 1's lag scan prefers a K-lag of 32, but blind the lag-32
form does no better than lag 1 (24.0 against 24.7 W rms; 17.5 against 16.1 W without the checkerboard), and only the
forms that add the row direction did better. *(Corrected after verification, C3: this said a GPU's operands meet on a
wire a tensor-core K-step, 16–32 elements, or a row apart.)*

**Blind, on 17 kinds measured on two boards the fit never saw, the toggle model in the ET-SoC-1's form (G1) predicts
power to 24.7 W rms, 16% of the 154.7 W from zeros to random bf16, biased high by 13.0 W.** So its registered accuracy
rules **fail** (P1: rms ≤ 15.5 W; P2: |bias| ≤ 7.7 W), while its coverage and its two comparisons **hold**: 16 of 17
kinds inside its frozen 90% band (P3, the checkerboard outside; the bands are ±47 W in bf16, ±93 W in fp16 and ±22 W in
int8, wide because G1's own nested errors were), 2.6 times better than power as density alone (G0, 63.7 W; P4), and
better than static bits (S1, 33.8 W; P5). **The best of the seven registered forms, picked after scoring, is G4, a K-lag
of 16 plus the row direction: it predicts the same 17 kinds to 12.8 W rms (8.2% of the span)**, and 10.9 W with A2's
board anchor; G1 plus the result path (G2) reads 17.7 W with the smallest bias (−2.4 W). G4 is a registered comparison,
not yet a stable model: on stage 1 its leave-one-kind-out error ran to 94–321 W, because its row and K-lag counts nearly
coincide on kinds random along rows (below, "The models"). *(Corrected after verification, C8: G4 was called "the best
registered form" without saying it was picked after scoring.)*

**Heat: the A100's die rises about 0.1 °C per board W at steady state**: 0.094 °C/W on stage 1's board A by its fit
(0.092–0.098 by model-free steps), and 0.098–0.112 °C/W on board B by model-free steps, where B's own fit reads 0.143
because it absorbs a drift of that slot's cooling (the frozen pooled model reads 0.116). About half of it comes at once
(within 0.2 s, the fit's grid edge) and the rest with a 13 s time constant on board A (32 s pooled). *(Corrected after
verification, C1: this gave 0.094 and 0.143 °C/W as the two boards' gains, and a 13–40 s time constant.)* **A 30 s
hold's rise on a new board is predicted to 1.4 °C rms from its measured power and to 3.8 °C rms end to end from the
bits**, against rises of −0.2 to 13 °C: both heat accuracy rules **fail** (H1, H2), the band's coverage **holds** (H3, 14
of 17), and H4 **fails** as registered (the two fits' ratio 0.66; the model-free steps' ratio is 0.87–0.94). **Most of
the end-to-end error is the power path, not the slot**: G1's power error, and the frozen path's second count of the
leakage y already carries. Post hoc, without the double count the same G1 reads 2.5–2.7 °C rms, and with each kind's
measured y as well 1.06–1.16 °C, against 1.39 °C from the measured power (H2). One board's die did wander ±2–3 °C at
nearly constant power over minutes, so the slot sets the floor: about 1.1 °C on board A and 2.0–2.3 °C on board B.
*(Corrected after verification, C2: this said heat on a rented GPU is a property of its slot as much as of the data.)*

| what is predicted, held-out kinds, new boards | before E149 | after E149 | source |
|---|---|---|---|
| **power of a new kind, A100, under the cap** | no GPU model; density alone (G0) **63.7 W** rms, bias +37.0 | the registered primary, the ET-SoC-1 form (G1): **24.7 W**, bias −13.0, 16 of 17 inside bands of ±22–93 W; the best of seven registered comparisons, picked after scoring (G4, stage-1 nested error 94–321 W): 12.8 W, and 10.9 W with a board anchor | `score-e149.json` `models`, `secondary_board_scale`; `posthoc.txt` §7, §8 |
| **heat of a new kind**, die rise over a 30 s hold | none for the A100 (E135's logs fit poorly, 1.7 and 3.3 °C rms) | **3.8 °C** rms end to end (post hoc 2.5–2.7 °C without the path's double count); **1.4 °C** from measured power (1.07 and 2.32 °C on the two boards) | `score-e149.json` `heat`, `heat_holds`; `posthoc.txt` §5, §6 |
| die rise per board W, steady | — | **0.094 °C/W** on board A (its fit; 0.092–0.098 by model-free steps), **0.098–0.112 °C/W** on board B (model-free steps; its fit's 0.143 absorbs the slot's drift); τ ≤ 0.2 s and 13 s (board A); leakage 1.8–2.6 W/°C | `model-e149.json` `heat`; `posthoc.txt` §2 |

Every number in this section comes from `score-e149.json` (the blind scores and rules), `model-e149.json` (the frozen
fit) and `reduce-stage1.json` / `reduce-stage2.json` (the measured watts), except those named post hoc or model-free,
which come from `posthoc.txt`; `summarize_e149.py` prints the tables below from the first four.

## Stage 1: what an A100's power follows, under its cap

**Every one of stage 1's 404 cell windows ran at 1410 MHz in every 100 ms sample with no clock-event reason bit** (the
hottest kind averaged 341 W; the hottest single windows drew 355.7 W, a cell, and 355.9 W, a reference, 44 W under the
limit; `posthoc.txt` §1), so the watts below read the data, not the cap (V0 **HOLDS**: 92 of 92 kinds valid on both boards;
`model-e149.json` `rules_stage1.V0`). **At that clock the data never changed the speed**: bf16 ran 157.1 TFLOPS over
all 52 kinds (0.7% spread), fp16 108.7 TFLOPS and int8 148.2 TOPS at 1024³ (`reduce-stage1.json` `kinds.*.tflops`).
In bf16 at 2048³, zeros drew 181.5 W, a constant 1.0 matrix 203.9 W and random normal 338.5 W
(`kinds["bf16.<kind>"].p_abs`). Below, y is watts over the same GEMM on zeros, ± SE over the valid replicates (2 passes ×
2 boards), from `reduce-stage1.json` `kinds.*.y`, `se`. Each window's die sits at its own fast-pole temperature (a zeros
cell runs 9.3 °C below its references), so about 11–16% of y is the leakage of the die's own warming within the window
(`posthoc.txt` §4; C2).

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
  just at its 2-SE bar, which it clears by 0.008 W, and 16.1 ± 3.4 W at 75%; 39 W at 90%): a scattered zero still flips
  its neighbours' bits.
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
  (86 W); the six waves rise from b = 1 to b = 16 (72, 80, 83, 88, 91 W) and dip at 64. On stage 1 the lag scan picks
  **K-lag 32** (`lag_scan`): G1's form at lag 32 reads a pooled nested error of 19.4 W against 34.9 W at lag 1. Stage 2
  did not confirm it: blind, lag 32 predicted no better than lag 1 (below). Which operand pairs the A100's circuits see
  in turn is not read here. *(Corrected after verification, C3: this said the operands that meet one after another on
  a wire are a tensor-core K-step or a row apart.)*
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
  per flip of one operand's bit at one multiply-add: the same order as the ET-SoC-1's 118–136 fJ per flipped bit. They
  are upper bounds on switching energy: y carries the die's own fast-pole leakage (λr₁ 0.11–0.16), and without it they
  read about 97–103, 125–132 and 115–133 fJ (`posthoc.txt` §10; C2). `summary.md` converts each field's centre
  coefficient; bf16's exponent figure there (176 fJ) lies outside the five bits the ladders flipped, where the
  per-position values run −1 to 201 fJ (C13).

## Stage 2, blind: 17 held-out kinds on two new boards

Measured after the freeze (`e929b00f`, 20:14:46 PST) in run `e149-20261102-r2` (20:15–20:40 PST): unit A an
A100-SXM4-80GB, unit B an A100-SXM4-40GB, neither one of stage 1's boards (`reduce-stage2.json` `units.*.static`). Every
operand's sha256 matched the predictions' (`do_score` asserts it), and every window held 1410 MHz with no reason bit
(the hottest kind, the power law, averaged 345 W; the hottest single window drew 353.6 W). y is watts over each
format's zeros, measured ± SE over 2 passes × 2 boards (`reduce-stage2.json` `kinds`), not the board's watts (the
checkerboard's 135.9 W is over zeros; the board drew 320.2 W; `posthoc.txt` §9); the predictions are
`predictions-e149.json` `kinds.*.pred`.

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

- **The checkerboard is what neither pairing along K gets.** Its zeros alternate along K and along the rows. Counting
  flips between neighbours along K (G1) predicts 214.6 W, between elements 32 apart (G1s) 65.9 W; it cost **135.9 W**
  over zeros (the board drew 320.2 W), so each misses by 70–79 W, in opposite directions. The form with a K-lag of 16
  plus the rows (G4) came within 13 W (149.3 W) and G1 plus the result path (G2) within 14 W (122.4 W). It is G1's one
  kind outside its band. Without it, lag 1 predicts the other 16 kinds better than lag 32 (G1 16.1 W rms, G1s 17.5 W),
  and the forms with the row direction better still (G3 13.5 W, G4 12.7 W; `posthoc.txt` §7). *(Corrected after
  verification, C3 and C6: this was headed "the checkerboard decides the pairing", and said it "drew" 135.9 W.)*
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
81% reached in 30 s, 1.77 °C rms over 39,024 samples. Board by board, the fits read: unit A (80GB) **0.094 °C/W**, τ₂
12.7 s, 0.71 °C rms; unit B (40GB) 0.143 °C/W, τ₂ 40.0 s, 2.25 °C rms. **B's fit is not B's gain** *(corrected after
verification, C1)*: inside one 180 s randn hold at 319–329 W its die read 53.0 °C at 90 s, 57.9 °C at 150 s and 56.0 °C
at 180 s, a drift of the slot's cooling that the fit absorbs with a +7.5 °C initial-transient term and a long pole.
Model-free steps on the same holds read **0.098–0.112 °C/W on B** and 0.092–0.098 on A, beside A's fit; and between 45 s
and 90 s after the step down to zeros B's die fell 0.66 °C, where its own 40 s fit has it fall 3.0 °C (`posthoc.txt` §2). The pooled model, which carries B's drift too, is
the frozen one and is scored as registered. A model fitted on one board predicts the other's 30 s rises to 1.0–1.2 °C
rms (`heat.cross`). **Leakage at the held reference load: 2.6 and 1.8 W per °C** (`heat.leakage`), so a 10 °C warmer
die costs about 20 W at the same data and clock.

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
(H2 **FAILS**, ≤ 0.6 °C): 1.07 °C on board A and 2.32 °C on board B over the 17 blind kinds, B's die running hotter than
the pooled model (`score-e149.json` `heat_holds`; `posthoc.txt` §6; C11). 14 of 17 rises fall inside the frozen heat
band (H3 **HOLDS**), which was wide (±4.8 °C in bf16) because it carries G1's power band. A2's anchor (each board's randn
hold) scales the blind rises by 0.72 and 0.93 and reads 2.35 °C rms.

**Most of the blind error is the power path** *(added after verification, C2; post hoc, no verdict)*. y already carries
each window's own fast-pole leakage (λr₁ = 0.131 of it, pooled), and the blind path adds λ × the whole simulated rise on
top, so the fast pole's part is counted twice. Over the 34 blind holds the path's power ran 34.0 W above the measured:
12.9 W of it G1's own error and 21.1 W (sd 11.5) the path's construction. Removing the double count (y × (1 − λr₁),
y ÷ (1 + λr₁), or λ times the slow pole's rise only) gives **2.53–2.68 °C rms** from the same frozen G1; each kind's
measured y in place of G1's gives 1.43 °C, and both together **1.06–1.16 °C**, against 1.39 °C from the measured power
(`posthoc.txt` §5). So the heat model and the slot set a floor of about 1.1–1.4 °C (about 1.1 °C on board A, 2.0–2.3 °C
on board B), and G1's power error and the double count, which compounds it, make up the rest.

## What this does to predicting power and heat

**Section 11 item 6 ("a power model across kinds"), on a GPU: narrowed.** The terms of the ET-SoC-1's model, operand
bit changes by field and side, a gate term for zeros and a sign term, **measured** on an A100 under its cap: every
ladder rule of the model's structure holds there (R1a, R1b, R2, R3a, R3b, R4a; R1b and B1 just), and the per-flip
prices come out at the ET-SoC-1's order (about 115–150 fJ per mantissa or magnitude flip of one operand at one
multiply-add, at the measured rate; upper bounds on switching energy, since 11–16% of y is the die's own leakage:
about 97–133 fJ without it). **Tested**: the model's pairing of operands, neighbours along K, **fails** on the GPU
(R4b); what replaces it is not settled, since the lag-32 form chosen on stage 1 predicted the blind kinds no better than
lag 1 and only the forms with the row direction did better. **Out-of-sample error, power** (17 held-out kinds, two new
boards): **before**, no model, and density alone 63.7 W rms (41% of the zeros-to-random span); **after**, 24.7 W (16%)
for the ET-SoC-1 form, the registered primary; the best of seven registered comparisons, picked after scoring (G4,
stage-1 nested error 94–321 W), 12.8 W (8.2%) and 10.9 W (7%) with a board anchor. **Heat**: the A100's die rise per
board W, about 0.1 °C/W (0.094 on board A; 0.098–0.112 on board B by model-free steps), and its time constants (≤ 0.2 s
and 13 s on board A) **measured** for the first time; a new kind's 30 s rise **before**: no A100 model; **after**: 3.8 °C
rms end to end, 1.4 °C rms from measured power. **Corrected** (post hoc): the frozen path counts the fast pole's leakage
twice; without that it reads 2.5–2.7 °C end to end and 1.06–1.16 °C from measured y, so the end-to-end heat error is
mostly the power path, and the heat model and the slot set a floor of about 1.1–1.4 °C. *(Corrected after
verification, C1–C3, C8: this called the pairing corrected to K-steps of 16–32 elements, gave 0.094–0.143 °C/W, set G4
beside G1 unlabelled, and named the slot the largest remaining term.)*

**For E150**, which would reuse the frozen model and heat path on a cheaper GPU: re-choose the sizes by A1's rule, state
the double count in its registration, and score a corrected heat arm (y × (1 − λr₁), or λ times the slow pole's rise
only) beside the registered one.

**Section 11 item 2 ("a GPU measured the same way"): narrowed, not answered.** E135 measured power at the cap; E149 holds
1410 MHz in every window and adds power and die temperature by kind under the cap, at 2048³ (bf16) and 1024³ (fp16,
int8), for one GPU model. Item 2's open parts are untouched: a lower cap (it needs a host that allows `nvidia-smi -pl`;
Modal's container refused it), his board and an H100, other GEMM shapes, and an ET-SoC-1 GEMM limited the same way. *(Corrected after verification, C9: this said "its
under-the-cap part: answered for one GPU model".)*

## Against the ET-SoC-1

| | ET-SoC-1 (its resident loop, the kinds harness) | A100 (cuBLAS GEMM under its cap, E149) |
|---|---|---|
| what costs | operand bits changing between consecutive micro-ops; flips share wires (E70) | the same: changes, not ones (R2); flips do not add (k = 1 → 3: twice the changes, 1.6× the watts; which wires, not read, C3) |
| which operands are consecutive | the micro-op stream along K (PRM 9.4 order) | not neighbours along K (R4b fails); a K-lag of 32 did no better blind, forms with the row direction did; open (C3) |
| zeros | gated lanes, a gate's state change ~158 fJ (M6's `gtr`) | blocks save more than scattered zeros (R1b); zeros in B save more than in A |
| signs | a random sign's ~5 W (fp32), held signs free | a random sign +43 W at constant magnitude, a fixed negative +0.8 ± 1.9 W (R3a, R3b) |
| A against B | A pays about two thirds of B's price per flip (E113, E125) | bf16: A's flips cost about twice B's; int8: B's random costs more than A's |
| per flip | 118–136 fJ per flipped bit (whole board) | about 115–150 fJ per operand-bit flip at one multiply-add (G1s, whole board over zeros) — same order, not like for like; upper bounds, 11–16% of it the die's own leakage (C2) |
| speed at a fixed clock | data-independent | data-independent (0.6–2.6% spread over every kind) |
| blind power error | M5 0.36 W, M6 0.41 W rms (E140, 600 MHz) | G1, the registered primary, 24.7 W rms (16% of the span); G4, the best of seven comparisons picked after scoring, 12.8 W (C8) |

The two kernels differ (a resident loop on one tile against a streaming GEMM), so the table sets kernel against kernel
(E135's correction C1), and no chip-level contrast is drawn from the size of an error.

## Registered against what happened

| rule | registered | measured | verdict |
|---|---|---|---|
| V0 | ≥ 90% of stage-1 kinds valid on each board | 92 of 92 on both | **HOLDS** |
| R1a | no resolved rise along the scattered zero ladder (bf16, int8) | none | **HOLDS** (both) |
| R1b | blocks < scattered at 50% and 75%, resolved | +7.888 W (bar 7.880) and +16.1 W (bar 6.9) | **HOLDS** (just, at 50%) |
| R2 | middle rung up, all-flipped constant back below half (four ladders) | bf16 mant +81.4 / +7.0, exp +51.9 / −4.0, fp16 mant +81.7 / +6.8, int8 +73.3 / +5.8 W | **HOLDS** (all four) |
| R3a | random sign > fixed, resolved | +43.1 ± 1.9 W | **HOLDS** |
| R3b | fixed negative ≈ fixed positive | +0.8 ± 1.9 W (limit 4.3) | **HOLDS** |
| R4a | sorted along K < shuffled, resolved | sorted 53.0 ± 4.7 W below | **HOLDS** |
| R4b | the ET form's lag: period-2 wave > period-128, resolved | the period-2 wave 13.4 ± 4.1 W below | **FAILS** |
| B1 | boards agree: slope 0.9–1.1, rms ≤ 5% of S | slope 0.918, 7.33 W (limit 7.74) | **HOLDS** |
| P1 | G1 blind rms ≤ 0.10 S (15.5 W) | 24.7 W | **FAILS** |
| P2 | G1's absolute bias ≤ 0.05 S (7.7 W) | −13.0 W | **FAILS** |
| P3 | ≥ 13 of 17 inside G1's 90% band | 16 of 17 (bands ±47 / ±93 / ±22 W in bf16 / fp16 / int8) | **HOLDS** |
| P4 | G1 rms ≤ 0.7 × G0's | 24.7 against 63.7 W | **HOLDS** |
| P5 | G1 rms < S1's | 24.7 against 33.8 W | **HOLDS** |
| H1 | blind hold rise rms ≤ 0.8 °C | 3.78 °C | **FAILS** |
| H2 | with measured power, rms ≤ 0.6 °C | 1.39 °C | **FAILS** |
| H3 | ≥ 13 of 17 rises inside the heat band | 14 of 17 | **HOLDS** |
| H4 | the two stage-1 boards' die rise per W within 0.8–1.25 | 0.66 (the fits; model-free steps 0.87–0.94, post hoc, C1) | **FAILS** |

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
  references − the same for its format's zeros in that pass: watts over zeros at 1410 MHz, each window at its own
  fast-pole temperature and the pass's slow thermal state, so y carries about 11–16% leakage (C2; the registration says
  "at the reference's thermal state"). A window counts only if the SM clock read 1410 MHz in every sample and no
  clock-event reason bit was set (V0).
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
  (`posthoc_e149.py` §3, the lane's `heat_resid.py` committed after verification; the samples are
  `logs/e149-20261102-r1/B/samples/`). A shared multi-GPU server's inlet or fans are the likely cause; nothing here
  measured them. It is also why B's own fit reads 0.143 °C/W (C1).
- **E135's boards, the same heat fit** (`posthoc_e149.py` §12, its committed logs): 0.097 and 0.067 °C per board W with
  τ₂ 20 and 80 s, at 1.7 and 3.3 °C rms (on its board B the slow pole all but vanishes, r₂ 0.001), its long idle cooling
  waits making the poor fits: too poor to quote as gains. *(Corrected after verification, C1: this said the A100
  coefficient spans 0.067–0.143 °C/W over four boards.)*
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
- y is watts over zeros with each window at its own fast-pole temperature, so it carries 11–16% leakage, and the
  registered blind heat path counts that part again (C2).

## Cost

**Metered $4.48** (`billing.json`: `modal billing report --for today --show-resources --json`, read 20:42 PST, app
`e149-gpu-model-check` only): stage 1 $2.52, stage 2 $1.73, smoke S0 $0.11, smoke S2 $0.13; the GPU line $4.17 = 7,144
GPU-seconds at $2.10/h. The ledger of function-seconds from the Volume's `STARTED`/`DONE` (`ledger.json`): 7,101 s, $4.45
at the registered rate. Projected $5.19, ceiling from the timeouts $8.66 with A1's smoke S2 (`posthoc.txt` §11; the
registration's $8.08 was written before S2 existed: C10), E149's cap $11 (stop at $10). Against the
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
| `posthoc_e149.py`, `posthoc.txt`, `posthoc.json` | added after verification, post hoc and labelled (no verdicts): the hottest windows, board B's fit against model-free steps, the heat residual by two-minute bins, the leakage inside y, the blind heat path's double count and its variants, the heat errors by board, the blind errors by model, the bands and narrow rules, y beside the board's watts, the per-flip coefficients by bit position, the timeouts' ceiling, E135's boards' heat fit. Run: `python posthoc_e149.py` (numpy) |
