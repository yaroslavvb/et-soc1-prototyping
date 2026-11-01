# Q133(b): the bench's power model refitted on thirteen experiments, scored by nested leave-one-kind-out, frozen as M5, with frozen predictions for a blind pool

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): item 6, "the power model's open cases".*

*Sun 1 Nov 2026 (week 44), Q133(b), desk only: no card was opened and nothing was measured in watts here. Every watt comes from a
committed experiment, named where it is used. It builds on Q132(b)'s M4 ([`../2026-11-01-q132-rtl-bench/`](../2026-11-01-q132-rtl-bench/README.md)
§ 11) and E103's blind test of it ([`../2026-11-01-e103-model-blind-test/`](../2026-11-01-e103-model-blind-test/README.md)). The pool it predicts,
[`tools/claims-v3/kinds/blind3/`](../../../../tools/claims-v3/kinds/blind3/README.md), was committed in `a9167033` before any of M4's files were
opened here; E115 scores it on a card.*

## Results

**One extension earns its place, and it is a small one.** Pricing the adder and normaliser per float format, with everything else as M4 has it, is the form leave-one-kind-out picks, in 150 of 151 outer folds: **nested rms 0.201 W over 283 float rows (151 kinds, thirteen experiments, two cards), against 0.211 W for M4's own form refitted on the same rows and 0.215 W for M4 as frozen.** fp16's adder toggle comes out cheaper than fp32's, 1.50 ± 0.05 against 1.62 ± 0.04 fJ. None of the other terms the open cases suggested pays for itself out of kind: the gate's switching (gated lanes, E93, E94), the A side's bus bits (the A side with a busy partner, E103-R8), register bits that change, or a full stage split. **int8 keeps I3's form** (nested 0.262 W over 78 rows; every extension is worse). **Frozen as M5** (`m5.json`, sha256 `c19f2c7b…`). Its predictions and M4's for the blind pool's 25 tiles are frozen too; the two models differ by at most 0.20 W on any tile, so E115 will test the open cases themselves more than it tells M5 from M4.

**1. Leave-one-kind-out, floats** (283 rows from thirteen experiments on two cards, 151 kinds; rms of D − prediction, W;
[`loko.json`](loko.json)):

| model | what it adds | all | fp32 | fp16 | card a3 | card c1 |
|---|---|---:|---:|---:|---:|---:|
| M4 / I3 as frozen, no refit | (in-sample on E78's kinds) | 0.215 | 0.209 | 0.222 | 0.186 | 0.233 |
| `F0_M4` | M4's form, refitted | 0.211 | 0.222 | 0.199 | 0.183 | 0.229 |
| `F1_split` | adder priced apart | 0.213 | 0.221 | 0.204 | 0.185 | 0.231 |
| `F2_stages` | every stage priced apart | 0.208 | 0.223 | 0.189 | 0.174 | 0.228 |
| `F3_split_fft` | adder apart, register bits that change | 0.215 | 0.223 | 0.206 | 0.187 | 0.233 |
| `F4_M4_abits` | A side's bus bits | 0.214 | 0.224 | 0.201 | 0.184 | 0.232 |
| `F5_split_abits` | adder apart, A side's bus bits | 0.216 | 0.225 | 0.204 | 0.185 | 0.235 |
| `F6_split_abits_gtr` | adder apart, A bits, gate switching | 0.214 | 0.225 | 0.201 | 0.184 | 0.233 |
| `F7_M4_gtr` | the gate's switching | 0.209 | 0.222 | 0.194 | 0.178 | 0.228 |
| `F8_stages_abits_gtr` | stages, A bits, gate switching | 0.208 | 0.221 | 0.193 | 0.180 | 0.226 |
| `F9_stages_gtr` | stages, gate switching | 0.208 | 0.223 | 0.188 | 0.174 | 0.228 |
| `F10_add_by_format` | adder priced per format | 0.198 | 0.209 | 0.186 | 0.176 | 0.212 |
| `F11_core_by_format` | core priced per format | 0.199 | 0.211 | 0.186 | 0.178 | 0.213 |
| `F12_core_by_format_gtr` | core per format, gate switching | 0.200 | 0.212 | 0.184 | 0.176 | 0.215 |
| **nested: the choice of form included** | picks `F10_add_by_format` 150, `F12_core_by_format_gtr` 1 | **0.201** | **0.213** | **0.186** | **0.177** | **0.216** |

**int8** (78 rows, 44 kinds):

| model | what it adds | all | int8 | card a3 | card c1 |
|---|---|---:|---:|---:|---:|
| M4 / I3 as frozen, no refit | (in-sample on E78's kinds) | 0.243 | 0.243 | 0.190 | 0.274 |
| `I0_I3` | I3's form, refitted | 0.253 | 0.253 | 0.219 | 0.273 |
| `I1_fft` | register bits that change | 0.256 | 0.256 | 0.219 | 0.279 |
| `I2_abits` | A side's bus bits | 0.258 | 0.258 | 0.223 | 0.280 |
| `I3_gtr` | the gate's switching | 0.254 | 0.254 | 0.217 | 0.277 |
| `I4_abits_bbits` | A and B bus bits | 0.263 | 0.263 | 0.216 | 0.291 |
| **nested: the choice of form included** | picks `I0_I3` 42, `I4_abits_bbits` 1, `I3_gtr` 1 | **0.262** | **0.262** | **0.219** | **0.288** |

**Reading it.** The per-format adder buys 0.010 W on the nested score against M4's form refitted, most of it on card 1
(0.229 → 0.216 W) and in fp16 (0.199 → 0.186 W). Against M4 as frozen, group by group (`loko.json` › `row_errors`,
`by_experiment`; M5's figure is its nested error, M4's its frozen one): better on E103's tiles (0.280 against 0.312 W), on E103's
five A-side tiles (0.170 against 0.260 W), on the real tensors of E86, E91 and E95 (0.196 against 0.246 W, 37 rows) and on fp16's
sign tiles (E92 0.239 against 0.306 W, E104 0.296 against 0.363 W); worse on fp32's sign tiles (E92 0.231 against 0.203 W, E104
0.263 against 0.218 W), on E106 (0.133 against 0.077 W) and on E94's draws (0.197 against 0.175 W). Plain leave-one-kind-out numbers per form are reported beside the nested one for reference; the best of them (0.198 W) is optimistic by construction, and the nested 0.201 W is the figure to quote. M4 as frozen is in-sample on E78's 33 kinds and its card scale came from E82, so its 0.215 W flatters it a little on those rows.

**2. M5, frozen.** [`m5.json`](m5.json), sha256 `c19f2c7bc098b5a8969694b6563784d57bf88e7336fe97ac2afe769b0c63e2da`, written by [`fit_m5.py`](fit_m5.py) (sha256 `e02116913042291bac41a4431bf880f00a4249bddf50c649c66feb267d77decb`).
Floats, form `F10_add_by_format`: mult **1.555 ± 0.024 fJ**, add32 **1.620 ± 0.037 fJ**, add16 **1.498 ± 0.052 fJ**, bus **7.567 ± 0.840 fJ**, rest **2.415 ± 0.096 fJ**, clk **1.054 ± 0.004 fJ**; fit rms 0.187 W over 283 rows; card-1 scale 0.9711 ± 0.0013. int8, form `I0_I3`: nets_nobus **3.261 ± 0.211 fJ**, bus **14.035 ± 3.081 fJ**, clk **1.945 ± 0.170 fJ**; fit rms 0.227 W over 78 rows; card-1 scale 0.9735 ± 0.0029.
D = rate × Σ constant × (count − the type's zeros' count), in W over the type's own zeros at 600 MHz on aifoundry3 card 0; on
aifoundry1 card 1, times the scale. The interval pools, nested leave-one-kind-out errors by format and card: floats fp16|a3 0.165 W (n 52), fp16|c1 0.198 W (n 81), fp32|a3 0.186 W (n 65), fp32|c1 0.231 W (n 85);
int8 int8|a3 0.219 W (n 32), int8|c1 0.288 W (n 46). M4's own float form refitted on all the rows reads core 1.604, bus 7.904, other nets 2.256, clocked bit 1.056 fJ (on E78
alone, M4 as frozen: 1.624, 7.533, 2.222, 1.066 fJ); int8's I3 refitted on all the rows is M5's int8 (on E78 alone: 3.123,
16.57, 1.820 fJ). `mult` is the multiplier's nets, `add32`/`add16` the adder and normaliser's in fp32/fp16 rows, `rest` every
other net of the VPU but the lane operand bus (`bus`), `clk` a clocked register bit.

**3. The largest nested misses** (D, W; D − prediction for the nested procedure, and for M4 as frozen):

| tile | D | nested | M4 frozen |
|---|---:|---:|---:|
| `fp32.c_near_rand` (E103) | 19.15 | +0.74 | +0.89 |
| `fp32.w_h_add` (E104) | 12.39 | -0.65 | -0.50 |
| `fp16.w_h_add` (E104) | 12.49 | -0.59 | -0.58 |
| `fp32.x_e_g` (E103) | 14.79 | +0.56 | +0.62 |
| `fp32.s_bhalf_alt` (E103) | 23.91 | +0.47 | +0.45 |
| `fp32.sparse50` (E82) | 6.76 | -0.47 | -0.33 |
| `fp32.r_walk` (E92) | 21.91 | -0.47 | -0.52 |
| `fp32.w_h_add` (E92) | 12.97 | -0.45 | -0.29 |
| `int8.r_cancel` (E88) | 4.86 | +0.85 | +0.76 |
| `int8.i_a127_bfull` (E103) | 2.43 | -0.79 | -0.72 |
| `int8.smallint` (E78) | 6.00 | -0.54 | -0.34 |
| `int8.i_w8_1` (E103) | 5.44 | -0.53 | -0.39 |
| `int8.smallint` (E82) | 5.89 | -0.47 | -0.27 |
| `int8.signs` (E90) | 5.47 | -0.46 | -0.24 |
| `int8.a_3of4_b_full` (E93) | 5.80 | +0.43 | +0.44 |
| `int8.ternary` (E82) | 5.01 | -0.43 | -0.19 |

**4. A set neither model was fitted on, post hoc for both: E102's single-bit prices** (aifoundry1 card 1, each over its own
zero; [`check-e102.json`](check-e102.json), [`check_e102.py`](check_e102.py)):

| E102 group | n | M5 rms (bias) | M4 rms (bias) | measured / predicted, M5 · M4 |
|---|---:|---:|---:|---:|
| fp32 B balanced | 11 | 0.260 (+0.150) | 0.227 (+0.124) | 0.861 · 0.882 |
| fp32 B all-in | 10 | 0.230 (+0.076) | 0.207 (+0.019) | 0.987 · 1.014 |
| fp32 A balanced | 11 | 0.130 (+0.096) | 0.129 (+0.095) | 0.902 · 0.904 |
| fp32 A all-in | 10 | 0.254 (+0.126) | 0.238 (+0.106) | 0.874 · 0.882 |
| fp16 balanced | 8 | 0.100 (-0.051) | 0.101 (-0.035) | 1.022 · 1.008 |
| fp16 all-in | 6 | 0.230 (+0.108) | 0.241 (+0.095) | 0.940 · 0.937 |
| int8 B | 13 | 0.102 (-0.066) | 0.101 (-0.064) | 1.170 · 1.148 |

**5. The open cases of item 6, one by one** (the list E103 left, with what this lane did about each):

- **fp32 where signs alternate on moving sums.** Tried: the adder priced apart (`F1`), per format (`F10`), the core per format (`F11`). Per format wins, but it moves fp16, not fp32: fp32's moving-sum misses stay, `fp32.c_near_rand` +0.74 W and `fp32.s_bhalf_alt` +0.47 W nested (M4 +0.89, +0.45), E103's sign tiles 0.39 W rms with a −0.27 W bias (the model low). **Narrowed for fp16, open for fp32.** The pool carries three fp32 tiles whose per-op sum is exactly 0, ~0 by rounding, or 2^-12 of a product, and two fp16 ones.
- **Exponents spread under a gate.** `fp32.x_e_g` stays +0.56 W low (M4 +0.62 W); neither the gate's switching nor a stage split removes it. **Open;** the pool has three such tiles.
- **Gated kinds.** With E93's 15 float tiles (negative zeros, denormals, masked zeros) counted and in the fit, the gated rows read 0.166 W nested (M4 as frozen 0.172 W), and E103's gated tiles 0.280 W (M4 0.317 W). The gate's switching (`gtr`) adds nothing out of kind (`F7` 0.209 against `F0` 0.211 W; `F12` 0.200 against `F11` 0.199 W). **Narrowed:** the bench's counts already carry what gating does; the pool tests the same gated fraction three ways (steady, every cycle, A every two cycles).
- **The A side with a busy partner (R8).** An A-side bus-bits term makes every form worse (`F4` 0.214, `F5` 0.216 W). On E103's five A-side tiles M5's nested errors read 0.170 W rms, +0.07 W bias, against M4's 0.260 W, +0.21 W; on E102's single-bit A ladders (not fitted) both models read 0.87-0.90 of the measured price, as before (§ 4). **Narrowed on E103's tiles, open on the ladders;** the pool has an exact busy/quiet twin (`a_lo8_b_randn`, `a_lo8_b_pi`) and A sides held down a column in fp32 and int8.
- **The zero level and idle.** Not modelled: D is over the type's zeros. The pool's `fp32.z_single` (one live lane-cycle an op, predicted 0.01 W) and `int8.z_diag` (1.85 W) test the model's low end; int8 zeros' 0.61 W is E109's.
- **The memory path's own term.** The bench has no scratchpad or dcache (Q132(b) § 14), so no form can have it. The pool's `m_bpair_eq` and `m_blines_eq` move B's in-lane alternation and its line-to-line bits apart: the bench prices the alternation at +8.4 W; a card reading far from that would locate the path's own cost.
- **Another clock, voltage or stream.** No clock or voltage is set in Q133. The pool's `int8.st_f32bytes` runs an fp32 tile's words through int8's stream.
- **A new card without a scale.** The frozen predictions come on a `new` footing (aifoundry3's constants, the interval widened by one card's step) and as ratios to the session's own random anchor; which card runs them is E115's choice.
- **A pool written by someone else.** Half met: no Agent tool, so the pool's designer was this lane, before it read the model (the pool's README, § The independence protocol).
- **A physical reading of the constants.** As an equivalent only, in § What this cannot say.

**6. The frozen predictions for the pool.** [`tools/claims-v3/kinds/blind3/predictions-blind3.json`](../../../../tools/claims-v3/kinds/blind3/predictions-blind3.json),
sha256 `5f28091a2878d5167aa4402286a1419cca2b78ebe4fbc0b3f34bda35a31f925a`, from [`predict_blind3.py`](predict_blind3.py) (sha256 `a1877bac4e1ec7e501438504dac06a44762171790e6fe3757cd9095f71c41367`) on the bench's counts of the 25 tiles
(`counts-blind3.json`, sha256 `428d0a3815ae66e7be84312e21a8763f276f2a1e8483dd5b17b27e823595684b`). Every tile's accumulators match
software at all three launch points except `fp16.s_wpair0`'s, where 5 of 256 words differ at each point: fp16's window-model
residue on near-cancelling sums, which `run_kinds.py` names as what an fp16 mismatch counts and Q132(b) Result 3 describes, so
its count stands with that flag (its bench run starts from software's accumulators, which may differ from the RTL's in low
bits). The 31 training tiles: 0 mismatches. The pool's README carries the table; the contrasts built into the pool:

| contrast | what it isolates | M5 | M4 |
|---|---|---:|---:|
| `g_blanes_alt` − `g_blanes_steady` (fp32) | gate switching every cycle against a steady gate, same gated fraction | +0.78 | +0.73 |
| `a_lo8_b_randn` − `a_lo8_b_pi` (fp32) | the same A side with a busy and a quiet partner | +11.55 | +11.36 |
| `m_blines_eq` − `m_bpair_eq` (fp32) | B alternating in-lane with no line changes, against lines changing with no in-lane alternation | +8.38 | +8.31 |
| `s_drift12` − `s_pair0` (fp32) | a sum that drifts up against one that returns to 0 | +0.06 | +0.08 |
| `s_bridge` − `s_pair0` (fp32) | a sum that climbs and walks back against one that returns every step | +0.68 | +0.65 |
| `x_logu_s50` − `x_logu_bsteady` (fp32) | exponents spread: a random 50% word gate against a steady lane gate | -5.61 | -5.62 |
| `s_wpair0` − `s_inword0` (fp16) | fp16: cancelling across k-groups against inside the two-term update | +4.76 | +4.68 |

## How it was done

**The rows.** Every tile that the RTL bench (`rtl-sim/fma_toggle_v2`, the real `vpu_top`, Q132(b)) has counted and a card has
measured as D, W over the type's own zeros at 600 MHz: E78, E86, E90, E92 and E95 on aifoundry3 card 0; E82, E88, E91, E93,
E94, E103, E104 and E106 on aifoundry1 card 1. Later sessions' anchors (`randn`, `full`, `zeros`, the pi tie) are left out:
they are E78's kinds again, kept only in E78 and E82, where they are the matrix. A row's counts are found by the sha256 of the
tile it ran, so a tile that two experiments ran (E92's, E104's and E106's shared sign tiles; E86's tiles in E91) uses one
count. 31 tiles had no count: E93's 17, E104's 11 and E106's 3. This lane counted them on the Intel with the same bench
([`counts-q133b-train.json`](counts-q133b-train.json)), after checking that the Intel's build reproduces Q132(b)'s
`counts-v2.json` **exactly** on 11 kinds at all three launch points, every stage, clocked bit, register toggle, valid slot and
check word ([`repro-check.json`](repro-check.json), `counts-repro.json`): Verilator 5.052 (conda-forge), `-fno-dfg`, core-et
`b38a1a31`, Q132(b)'s `train_maps.py` maps rebuilt for this binary.

**The features** are Q132(b)'s: rate (ops/s, chip-wide) × the per-op counts less the type's zeros (`counts-v2.json`), by stage of
the whole VPU (`nets_map`: multiplier, adder and normaliser, lane operand bus, exponent and operand, control, result path),
clocked register bits and register bits that change. Three come from the tile bytes through `make_kinds`' stream: the A side's
and the B side's operand-bus bits an op, and `gtr`, how many of the eight gate bits change state between consecutive
micro-ops of an accumulate op (the lane's gate switching on and off).

**The forms** (`FORMS` in [`fit_m5.py`](fit_m5.py)). Floats: M4 itself (core, bus, other nets, clocked bits), and twelve
extensions, each adding what the brief named for an open case: the adder priced apart from the multiplier, overall or per
format (signs: E88, E92, E104, E106); register bits that change; the gate's switching, `gtr` (gated lanes: E93, E94); the A
side's bus bits (the A side with a busy partner, E103-R8); and the whole stage split. int8: I3 (M4's int8 form) and four
extensions. No form was dropped after a look: all are in `loko.json`.

**Kinds and the card.** A held-out kind is every row of one tile rule, on both cards and in every experiment:
byte-identical tiles share a kind, and E90's and E94's re-draws join their rule (so `fp32.randn` holds E78's, E82's and E94's
four draws). Card 1's rows are put on card 0's footing by one scale per family, model-free: E82's kinds against E78's same
tiles, Σ D82·D78 / Σ D78², recomputed inside every fold without the held-out kind.

**Nested leave-one-kind-out.** For each kind: hold it out; on the rest, score every form by leave-one-kind-out; refit the
best on the rest; predict the held-out kind. The outer errors score the whole procedure, the choice of form included, on kinds
it never saw. The same inner step on all the rows chose the frozen form, and its constants are fitted on all the rows.
Plain leave-one-kind-out per form is reported beside it, for reference: picking the best of those numbers is optimistic,
which is why the nested figure is the one to quote.

**The interval** for a frozen prediction: t(0.975, n − 2) × √(pool² + x′Cx + m²), pool = the rms of the nested outer errors on
that format and card, C = the constants' jackknife covariance by kind, m = the standard error over the tile's three launch
points; on card 1 the scale's jackknife error is added, and for a card with no scale of its own the a3 figure is widened by
|1 − card-1 scale| × D in quadrature (one card's step taken as the spread of cards: a guess, labelled as one).

## What this cannot say

- **Nothing here is a new measurement.** M5's constants are fitted on what the cards already read; whether they generalise is
  E115's question, on tiles the fit never saw.
- **The rows are not independent.** Kinds were picked by people chasing the model's misses (E103 picked where it disagreed
  most), so the nested score is an estimate for kinds like these, not for any data. Real tensors (E86, E91, E95) are the
  closest thing to unpicked rows.
- **Card 1's sessions differ among themselves by a few percent:** fp32 `randn` read 23.39 W in E91, 23.99 W in E82 and
  24.11-24.30 W on E94's four draws (`e91.json`, `e82.json`, `e94.json` › `D`). One scale per card cannot hold that; a
  session's own anchor can, which is why the predictions also come as ratios to the anchor.
- **The bench sees three points of a launch.** A tile whose sums change regime inside a launch (`s_drift12` in the pool,
  E103's `c_near_rand`) is priced at those three points only.
- **int8 stays empirical.** Its multiply and adds are behavioural RTL with no nets inside, so I3's constants are fitting
  constants on the counts that exist, not prices.
- **The physical reading is a reading, and only of an equivalent.** At E78's 521.7 mV, an energy E per toggle is what charging
  C_eq = 2E/V² costs: M4's 1.62 fJ per core merged-net toggle is about 12 fF, its 7.5 fJ per operand-bus net about 55 fF, 2.2 fJ
  per other net about 16 fF, and 1.07 fJ per clocked register bit about 8 fF. The ratio is the readable part: a lane's operand
  bus costs about 4.6 core nets a toggle, the size of a long wire against a local one, and a clocked bit about two thirds of a
  core net. The absolute part is not: a merged net is a floor on wires (an open netlist counts 3,299 where the bench counts
  1,816), so none of these is the energy of a wire (Q132(b) § 6 forbids "fJ per wire"); the fit absorbs what a zero-delay
  simulation misses (glitches, the clock tree above the registers, the scratchpad); the RTL is core-et's later revision, not
  the ET-SoC-1's own; and card 1's scale, 0.97, is not (about 499 / 521.7)² = 0.91 (card 1 reads 498.6-498.8 mV in E91 and E106), so the constants do not move as V² alone
  between these two cards.
- **Not done here:** another clock or voltage (Q133 sets none), the zero level and idle (D is over the type's zeros), E101's
  GEMM stream, and any card run.

## Files

| file | what |
|---|---|
| [`fit_m5.py`](fit_m5.py) | the rows (every counted, measured tile), the features, the 13 float and 5 int8 forms, plain and nested leave-one-kind-out, the frozen fit; writes `loko.json`, `m5.json`, `rows.json` |
| [`fit-output.txt`](fit-output.txt) | its printed summary |
| [`loko.json`](loko.json) | every form's leave-one-kind-out rms by format and card, the nested score and its picks, every form's constants on all rows, the largest misses |
| [`m5.json`](m5.json) | **the freeze**: per family the form, constants (J), their jackknife covariance by kind, the card-1 scale and its error, the interval pools |
| [`rows.json`](rows.json) | the assembled rows: experiment, card, key, kind, tile sha256, D, rate, features |
| [`counts-q133b-train.json`](counts-q133b-train.json) | the bench's counts for the 31 measured tiles no counts file had (E93 17, E104 11, E106 3), named `<exp>_<tile>` |
| [`counts-repro.json`](counts-repro.json), [`repro-check.json`](repro-check.json) | the Intel's bench on 11 of E78's kinds, against Q132(b)'s `counts-v2.json`: identical |
| [`predict_blind3.py`](predict_blind3.py) | the frozen predictions for blind pool 3, from M5 and from M4 as frozen; writes the pool's `predictions-blind3.json` and `.md` |
| [`check_e102.py`](check_e102.py), [`check-e102.json`](check-e102.json), [`check-e102.txt`](check-e102.txt) | M5 and M4 on E102's single-bit prices |
| `../../../../tools/claims-v3/kinds/blind3/` | the pool (`a9167033`), its counts and the frozen predictions |

Rerun, from the tree's root, with a python that has numpy:

```
# the bench (rtl-sim/fma_toggle_v2, as its README says; here -j 6 for the Intel's six-core rule, which changes only Verilator's build parallelism)
make CORE_ET=../../external/core-et VERILATOR=<verilator 5.052> CXXOVERRIDE=/usr/bin/clang++ obj_vpu/Vtb accum settle_count
python3 train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds ../../tools/claims-v3/kinds --out maps --jobs 6
python3 run_kinds.py ... --only __none__ --extra-tiles <type>:<exp>_<name>:<path>,...   # the 31 tiles -> counts-q133b-train.json
python3 run_kinds.py ... --only __none__ --extra-tiles <type>:<kind>:tools/claims-v3/kinds/blind3/tiles/<type>/<kind>.bin,...   # -> counts-blind3.json
# the model
python3 docs/reports/data/2026-11-01-q133b-power-model/fit_m5.py > docs/reports/data/2026-11-01-q133b-power-model/fit-output.txt
python3 docs/reports/data/2026-11-01-q133b-power-model/predict_blind3.py
python3 docs/reports/data/2026-11-01-q133b-power-model/check_e102.py > docs/reports/data/2026-11-01-q133b-power-model/check-e102.txt
```

## Order (PST, Sun 1 Nov 2026)

1. 10:40 brief read; 10:42 `git log` subjects (they name M4's headline form, and E103's worst miss); 10:44 no Agent tool in this
   session, so the brief's fallback: the pool before the model.
2. 10:45-10:52 the kinds machinery only; the pool generated and hashed (`blind3.json` `60dfbf12…`); novelty checked.
3. **10:53:35 the pool committed and pushed, `a9167033`.** Only then were M4's files opened: Q132(b)'s README and
   `predict_m4.py`, E103's README, E106's.
4. 10:55-10:58 the bench built on the Intel; 10:58-11:00 its maps; 11:02-11:14 the reproduction check, exact.
5. 11:14 the pool's tiles counted; then the 31 training tiles.
6. 12:01:48 the fit and the freeze; 12:04 the predictions; this commit, before E115's claim.
