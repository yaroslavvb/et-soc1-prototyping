# Q133(b): the bench's power model refitted on thirteen experiments, scored by nested leave-one-kind-out, frozen as M5, with frozen predictions for a blind pool

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): item 6, "the power model's open cases".*

*Sun 1 Nov 2026 (week 44), Q133(b), desk only: no card was opened and nothing was measured in watts here. Every watt comes from a
committed experiment, named where it is used. It builds on Q132(b)'s M4 ([`../2026-11-01-q132-rtl-bench/`](../2026-11-01-q132-rtl-bench/README.md)
§ 11) and E103's blind test of it ([`../2026-11-01-e103-model-blind-test/`](../2026-11-01-e103-model-blind-test/README.md)). The pool it predicts,
[`tools/claims-v3/kinds/blind3/`](../../../../tools/claims-v3/kinds/blind3/README.md), was committed in `a9167033` before any of M4's files were
opened here; E115 scores it on a card.*

*Corrected after verification the same afternoon, at the desk, with no card touched and nothing re-run on a card (§ [Corrections after verification](#corrections-after-verification-sun-1-nov-2026), C1–C8). An independent verifier reproduced every number, the freeze and the predictions; what did not hold is how they were described. The model search was widened after its first results had been read, which this page did not say, and "one extension earns its place" did not follow from the numbers. No frozen file changed: `m5.json`, `predictions-blind3.json` and the counts are as committed in `64b4124e`, and they stay E115's blind predictions. The contrasts' 95% intervals are added as a dated addendum before E115's claim ([`contrasts-blind3.json`](../../../../tools/claims-v3/kinds/blind3/contrasts-blind3.json)).*

## Results

**M5 is M4's form refitted on thirteen experiments, with the adder priced per float format; whether that last term helps is not shown here, and E115 decides.** The fit prices an fp16 adder toggle 7.5% below an fp32 one: 1.498 against 1.620 fJ, a difference of 0.122 ± 0.030 fJ (1 s.e., jackknife by kind), so the parameter itself is resolved. Its value for prediction is not. The term was added after the first fit's results had been read (C1). With it, the nested leave-one-kind-out procedure reads **0.201 W rms over 283 float rows** (151 kinds, thirteen experiments, two cards; 95% bootstrap over kinds 0.180–0.222 W), against 0.211 W for M4's own form refitted on the same rows and 0.215 W for M4 as frozen. That 0.011 W gain over M4's form refitted is one a paired bootstrap over kinds cannot tell from zero (95% CI −0.028 to +0.007 W, C2). The procedure as first run, with only the forms written before any fit, scores 0.214 W on the same rows, worse than M4's form refitted (C1). On the 27 float rows counted only after the forms had changed it reads 0.194 W against 0.195 W for M4's form refitted. On E102's single-bit prices, the one set neither model was fitted on, M5 is no better than M4 (§ 4). And on E103's A side, the real tensors and E104's fp16 tiles, where M5 beats M4 as frozen most, most of the gain is already there when M4's own form is refitted on the thirteen experiments (§ 1). None of the other terms the open cases suggested helps measurably out of kind (each within 0.003 W of M4's form refitted, or worse): the gate's switching (gated lanes, E93, E94), the A side's bus bits (the A side with a busy partner, E103-R8), register bits that change, or a full stage split. **int8 keeps I3's form, refitted** (nested 0.262 W over 78 rows, 95% 0.210–0.320 W; every extension is worse), and the refit buys nothing measurable out of sample: on the 63 int8 rows M4 never saw, M4 as frozen reads 0.256 W against 0.270 W for M5's nested procedure (§ 1, C4). **Frozen as M5** (`m5.json`, sha256 `c19f2c7b…`). Its predictions and M4's for the blind pool's 25 tiles are frozen too; the two models differ by at most 0.20 W on any tile, so E115 will test the open cases themselves more than it tells M5 from M4.

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
| `F9_stages_gtr` † | stages, gate switching | 0.208 | 0.223 | 0.188 | 0.174 | 0.228 |
| `F10_add_by_format` † | adder priced per format | 0.198 | 0.209 | 0.186 | 0.176 | 0.212 |
| `F11_core_by_format` † | core priced per format | 0.199 | 0.211 | 0.186 | 0.178 | 0.213 |
| `F12_core_by_format_gtr` † | core per format, gate switching | 0.200 | 0.212 | 0.184 | 0.176 | 0.215 |
| **nested: the choice of form included** | picks `F10_add_by_format` 150, `F12_core_by_format_gtr` 1 | **0.201** | **0.213** | **0.186** | **0.177** | **0.216** |
| nested over `F0`–`F8` only, post hoc (C1) | the forms written before any fit ran; picks `F2_stages` 149, `F8` 2 | 0.214 | | | | |

† Added after the first fit's results had been read (C1, § Order). The first fit, with `F0`–`F8` only, on the 258 float rows counted by then and with E91's three anchor rows kept, read nested 0.216 W against 0.215 W for `F0`. Rerun on these 283 rows, `F0`–`F8` alone read 0.214 W; with E91's anchors kept as well, 0.220 W, and the full set with E91's anchors 0.203 W (`corrections-check.txt` C1). Bootstrap over kinds, 95%: nested 0.201 [0.180, 0.222] W, fp32 0.213 [0.182, 0.246], fp16 0.186 [0.161, 0.213] (C7).

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

The refit of int8 buys nothing measurable out of sample (C4). M4 as frozen is in-sample only on E78's 15 int8 rows. On the 63 it never saw, it reads 0.256 W, against 0.270 W for M5's nested procedure and 0.258 W for I3's form refitted under plain leave-one-kind-out. On the 48 rows outside both E78 and E82 (whose card scale it took) it reads 0.278 W, against 0.285 and 0.270 W. So "int8 keeps I3" holds, and freezing the refitted constants rather than M4's own is a choice, not a measured gain. The nested rms, 95% bootstrap over kinds: 0.262 [0.210, 0.320] W (C7).

**Reading it.** The nested score sits 0.011 W below M4's form refitted (0.201 against 0.211 W), most of it on card 1
(0.229 → 0.216 W) and in fp16 (0.199 → 0.186 W). A paired bootstrap over kinds puts that difference at −0.011 W, 95% CI
−0.028 to +0.007 W, with 12% of resamples at zero or above: not resolved (C2). Group by group (`loko.json` › `row_errors`;
`corrections-check.txt` C2), M5's figure is its nested error, M4's form refitted its plain leave-one-kind-out error and M4's
its frozen one, rms in W:

| group | n | M5, nested | M4's form refitted | M4 as frozen |
|---|---:|---:|---:|---:|
| E103, all | 23 | 0.280 | 0.326 | 0.312 |
| E103's A-side tiles | 5 | 0.170 | 0.179 | 0.260 |
| real tensors (E86, E91, E95) | 37 | 0.196 | 0.211 | 0.246 |
| fp16 sign tiles, E92 | 10 | 0.239 | 0.276 | 0.306 |
| fp16 sign tiles, E104 | 11 | 0.296 | 0.315 | 0.363 |
| fp32 sign tiles, E92 | 24 | 0.231 | 0.212 | 0.203 |
| fp32 sign tiles, E104 | 9 | 0.263 | 0.201 | 0.218 |
| E106 | 10 | 0.133 | 0.108 | 0.077 |
| E94's draws | 45 | 0.197 | 0.204 | 0.175 |
| all fp32 | 150 | 0.213 | 0.222 | 0.209 |
| all fp16 | 133 | 0.186 | 0.199 | 0.222 |
| floats outside E78 and E82 | 217 | 0.212 | 0.223 | 0.232 |

On E103's A side, the real tensors and E104's fp16 tiles, where M5 beats M4 as frozen most, most of the gain is already there
with M4's own form refitted on the thirteen experiments, and the per-format term adds the rest. On E92's fp16 sign tiles the
two share it, and on E103 as a whole the term does the work (M4's form refitted reads 0.326 W there, worse than M4 as frozen).
On fp32's sign tiles and E106, M4's form refitted does better than M5. Over all fp32 rows M5 (0.213 W) is no better than M4 as frozen (0.209 W): its whole
edge is in fp16. Plain leave-one-kind-out numbers per form are reported beside the nested one for reference; the best of them (0.198 W) is optimistic by construction, and the nested 0.201 W is the figure to quote. M4 as frozen is in-sample on E78's 33 kinds and its card scale came from E82, so its 0.215 W flatters it a little on those rows: on the 217 float rows outside E78 and E82 it reads 0.232 W.

**2. M5, frozen.** [`m5.json`](m5.json), sha256 `c19f2c7bc098b5a8969694b6563784d57bf88e7336fe97ac2afe769b0c63e2da`, written by [`fit_m5.py`](fit_m5.py) (sha256 `e02116913042291bac41a4431bf880f00a4249bddf50c649c66feb267d77decb`).
Floats, form `F10_add_by_format`: mult **1.555 ± 0.024 fJ**, add32 **1.620 ± 0.037 fJ**, add16 **1.498 ± 0.052 fJ**, bus **7.567 ± 0.840 fJ**, rest **2.415 ± 0.096 fJ**, clk **1.054 ± 0.004 fJ**; fit rms 0.187 W over 283 rows; card-1 scale 0.9711 ± 0.0013. int8, form `I0_I3`: nets_nobus **3.261 ± 0.211 fJ**, bus **14.035 ± 3.081 fJ**, clk **1.945 ± 0.170 fJ**; fit rms 0.227 W over 78 rows; card-1 scale 0.9735 ± 0.0029. Every ± here is one standard error, jackknife by kind; a 95% interval is about 1.96 times it (add32 ± 0.073, add16 ± 0.102 fJ; C7). Six constants and the card-1 scale are fitted for the floats, three and a scale for int8.
D = rate × Σ constant × (count − the type's zeros' count), in W over the type's own zeros at 600 MHz on aifoundry3 card 0; on
aifoundry1 card 1, times the scale. The interval pools, nested leave-one-kind-out errors by format and card: floats fp16|a3 0.165 W (n 52), fp16|c1 0.198 W (n 81), fp32|a3 0.186 W (n 65), fp32|c1 0.231 W (n 85);
int8 int8|a3 0.219 W (n 32), int8|c1 0.288 W (n 46). M4's own float form refitted on all the rows reads core 1.604, bus 7.904, other nets 2.256, clocked bit 1.056 fJ (on E78
alone, M4 as frozen: 1.624, 7.533, 2.222, 1.066 fJ); int8's I3 refitted on all the rows is M5's int8 (on E78 alone, M4 as
frozen: 3.092, 16.737, 1.795 fJ; this page said 3.123, 16.57, 1.820 until the corrections, C8). `mult` is the multiplier's nets, `add32`/`add16` the adder and normaliser's in fp32/fp16 rows, `rest` every
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

So on the one set neither model was fitted on, M5 is no better than M4: worse in three of the four fp32 groups (by 0.016–0.033 W), level within 0.002 W in fp32 A balanced, fp16 balanced and int8, and better only in fp16 all-in, by 0.012 W on 6 rows. M4's form refitted on all the rows, without the per-format term, reads 0.225, 0.212, 0.123, 0.237, 0.100, 0.243 W on the six float groups: the term makes all four fp32 groups worse against it, by 0.007–0.035 W, and helps only fp16 all-in (`corrections-check.txt` C2). Post hoc for every model.

**5. The open cases of item 6, one by one** (the list E103 left, with what this lane did about each):

- **fp32 where signs alternate on moving sums.** Tried: the adder priced apart (`F1`), per format (`F10`), the core per format (`F11`); the last two were added after the first fit's results had been read (C1). Per format reads best, by an amount not resolved (C2), and it moves fp16, not fp32: fp32's moving-sum misses stay, `fp32.c_near_rand` +0.74 W and `fp32.s_bhalf_alt` +0.47 W nested (M4 +0.89, +0.45), E103's sign tiles 0.39 W rms with a −0.27 W bias (the model low). **Narrowed for fp16, open for fp32.** The pool carries three fp32 tiles whose per-op sum is exactly 0, ~0 by rounding, or 2^-12 of a product, and two fp16 ones.
- **Exponents spread under a gate.** `fp32.x_e_g` stays +0.56 W low (M4 +0.62 W); neither the gate's switching nor a stage split removes it. **Open;** the pool has three such tiles.
- **Gated kinds.** With E93's 15 float tiles (negative zeros, denormals, masked zeros) counted and in the fit, the gated rows read 0.166 W nested (M4 as frozen 0.172 W), and E103's gated tiles 0.280 W (M4 0.317 W). The gate's switching (`gtr`) adds nothing out of kind (`F7` 0.209 against `F0` 0.211 W; `F12` 0.200 against `F11` 0.199 W). **Narrowed:** the bench's counts already carry what gating does; the pool tests the same gated fraction three ways (steady, every cycle, A every two cycles).
- **The A side with a busy partner (R8).** An A-side bus-bits term makes every form worse (`F4` 0.214, `F5` 0.216 W). On E103's five A-side tiles M5's nested errors read 0.170 W rms, +0.07 W bias, against M4's 0.260 W, +0.21 W, and 0.179 W for M4's own form refitted, so most of that gain is the refit (C2); on E102's single-bit A ladders (not fitted) both models read 0.87-0.90 of the measured price, as before (§ 4). **Narrowed on E103's tiles, open on the ladders;** the pool has an exact busy/quiet twin (`a_lo8_b_randn`, `a_lo8_b_pi`) and A sides held down a column in fp32 and int8.
- **The zero level and idle.** Not modelled: D is over the type's zeros. The pool's `fp32.z_single` (one live lane-cycle an op, predicted 0.01 W) and `int8.z_diag` (1.85 W) test the model's low end; int8 zeros' 0.61 W is E109's.
- **The memory path's own term.** The bench has no scratchpad or dcache (Q132(b) § 14), so no form can have it. The pool's `m_bpair_eq` and `m_blines_eq` move B's in-lane alternation and its line-to-line bits apart. The bench prices `m_blines_eq` − `m_bpair_eq` at +8.38 W, 95% [+7.82, +8.94] W on aifoundry3's footing (the two tiles' frozen half-widths in quadrature, a dated addendum: [`contrasts-blind3.json`](../../../../tools/claims-v3/kinds/blind3/contrasts-blind3.json), C5), and all of it is compute and the operand bus: 2.99 W multiplier, 2.05 W adder, 2.61 W other nets, 0.74 W bus. Only `m_bpair_eq`'s B lines change (3,552 bits an op against 0), while `m_blines_eq`'s B half-lines change about twice as often (3,680 against 1,776). So a card reading below the interval would fit a cost for B lines that change, a reading above it a cost for half-lines that change, and either could instead be compute the bench misprices. The earlier wording here, "a card reading far from that would locate the path's own cost", read one way and had no interval.
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
bits). The 31 training tiles: 0 mismatches. The pool's README carries the table; the contrasts built into the pool, W on aifoundry3's footing, with the 95% intervals added after verification as a dated addendum before E115's claim ([`contrasts-blind3.json`](../../../../tools/claims-v3/kinds/blind3/contrasts-blind3.json) and `.md`, from [`contrasts_blind3.py`](contrasts_blind3.py): the two tiles' frozen half-widths in quadrature, C5):

| contrast | what it isolates | M5 | M5, 95% (added) | M4 |
|---|---|---:|---:|---:|
| `g_blanes_alt` − `g_blanes_steady` (fp32) | gate switching every cycle against a steady gate, same gated fraction | +0.78 | [+0.23, +1.34] | +0.73 |
| `a_lo8_b_randn` − `a_lo8_b_pi` (fp32) | the same A side with a busy and a quiet partner | +11.55 | [+10.97, +12.12] | +11.36 |
| `m_blines_eq` − `m_bpair_eq` (fp32) | B alternating in-lane with no line changes, against lines changing with no in-lane alternation | +8.38 | [+7.82, +8.94] | +8.31 |
| `s_drift12` − `s_pair0` (fp32) | a sum that drifts up against one that returns to 0 | +0.06 | [−0.50, +0.63] | +0.08 |
| `s_bridge` − `s_pair0` (fp32) | a sum that climbs and walks back against one that returns every step | +0.68 | [+0.12, +1.24] | +0.65 |
| `x_logu_s50` − `x_logu_bsteady` (fp32) | exponents spread: a random 50% word gate against a steady lane gate | -5.61 | [−6.16, −5.06] | -5.62 |
| `s_wpair0` − `s_inword0` (fp16) | fp16: cancelling across k-groups against inside the two-term update | +4.76 | [+4.26, +5.26] | +4.68 |

On pairs of training kinds in one experiment, type and card, that stand-in is about right rather than conservative: the float pairs' nested errors are uncorrelated on average (rms of the difference / rms of the two in quadrature = 1.000) and 95.5% of 1,680 differences fall inside it; int8's are positively correlated (0.914) and 97.7% of 353 fall inside (`corrections-check.txt` C5). Applying the tiles' own formula to the difference, so the constants' share cancels, gives nearly the same, ±0.49–0.57 W against the stand-in's ±0.50–0.57 W: the pools dominate both.

## How it was done

**The rows.** Every tile that the RTL bench (`rtl-sim/fma_toggle_v2`, the real `vpu_top`, Q132(b)) has counted and a card has
measured as D, W over the type's own zeros at 600 MHz: E78, E86, E90, E92 and E95 on aifoundry3 card 0; E82, E88, E91, E93,
E94, E103, E104 and E106 on aifoundry1 card 1. Later sessions' anchors (`randn`, `full`, `zeros`, the pi tie) are left out:
they are E78's kinds again, kept only in E78 and E82, where they are the matrix. Until 11:17:14 PST the code kept E91's three
anchor rows as an exception (fp32 `randn` 23.39 W, fp16 `randn`, int8 `full`); the exception was removed after the first
fit's results had been read (C1). Kept, they move the nested float score from 0.201 to 0.203 W and the fp32 card-1 interval
pool from 0.231 to 0.237 W; int8's nested score reads 0.260 W with E91's `full` (`corrections-check.txt` C1). A row's counts are found by the sha256 of the
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
extensions. Eight (`F1`–`F8`) were written before any fit ran, each adding what the brief named for an open case: the adder
priced apart from the multiplier (signs: E88, E92, E104, E106); register bits that change; the gate's switching, `gtr`
(gated lanes: E93, E94); the A side's bus bits (the A side with a busy partner, E103-R8); and the whole stage split. Four were
added after the first fit's results had been read: the stage split with gate switching (`F9`, 11:12:23 PST), and the adder or
the core priced per float format (`F10`–`F12`, 11:16:09, 24 s after that fit's largest misses were printed, among them fp16
alternation tiles the model over-predicted by 0.45–0.54 W). `F10` is M5's form. int8: I3 (M4's int8 form) and four
extensions, all written before any fit. No form was dropped; `F9`–`F12` were added, and E91's anchors removed, after the
first fit's results were read (C1, § Order). All are in `loko.json`.

**Kinds and the card.** A held-out kind is every row of one tile rule, on both cards and in every experiment:
byte-identical tiles share a kind, and E90's and E94's re-draws join their rule (so `fp32.randn` holds E78's, E82's and E94's
four draws). Card 1's rows are put on card 0's footing by one scale per family, model-free: E82's kinds against E78's same
tiles, Σ D82·D78 / Σ D78², recomputed inside every fold without the held-out kind.

**Nested leave-one-kind-out.** For each kind: hold it out; on the rest, score every form by leave-one-kind-out; refit the
best on the rest; predict the held-out kind. The outer errors score the whole procedure, the choice of form included, on kinds
it never saw. The same inner step on all the rows chose the frozen form, and its constants are fitted on all the rows.
Plain leave-one-kind-out per form is reported beside it, for reference: picking the best of those numbers is optimistic,
which is why the nested figure is the one to quote. The nested score covers the choice among `F0`–`F12`; it cannot cover
the choice of `F0`–`F12` itself, which was widened after a look (C1). So 0.201 W is not a registered score; E115's is.

**The interval** for a frozen prediction: t(0.975, n − 2) × √(pool² + x′Cx + m²), pool = the rms of the nested outer errors on
that format and card, C = the constants' jackknife covariance by kind, m = the standard error over the tile's three launch
points; on card 1 the scale's jackknife error is added, and for a card with no scale of its own the a3 figure is widened by
|1 − card-1 scale| × D in quadrature (one card's step taken as the spread of cards: a guess, labelled as one).

## What this cannot say

- **Nothing here is a new measurement.** M5's constants are fitted on what the cards already read; whether they generalise is
  E115's question, on tiles the fit never saw.
- **The search was widened after a look, so its score is not a registered one** (C1). M5's own form, the adder priced per
  format, was added after the first fit's results and misses had been read, and E91's anchors were dropped then too. Run as
  first written, the procedure scores 0.214 W (0.220 W with E91's anchors), worse than M4's form refitted. Whether the
  per-format term helps prediction is unresolved here (C2); E115's pool was written before it and decides.
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
| [`corrections-check.py`](corrections-check.py), [`corrections-check.txt`](corrections-check.txt) | every number the corrections cite (C1–C8), from committed files; C1 reruns `fit_m5.py`'s own code with the first fit's forms and row rule. Post hoc, at the desk |
| [`contrasts_blind3.py`](contrasts_blind3.py) | the contrasts' 95% intervals, a dated addendum to the frozen predictions: writes the pool's `contrasts-blind3.json` and `.md` |
| `../../../../tools/claims-v3/kinds/blind3/` | the pool (`a9167033`), its counts, the frozen predictions and the contrasts' intervals |

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
# the corrections, after verification: their checks, and the contrasts' intervals
python3 docs/reports/data/2026-11-01-q133b-power-model/corrections-check.py > docs/reports/data/2026-11-01-q133b-power-model/corrections-check.txt
python3 docs/reports/data/2026-11-01-q133b-power-model/contrasts_blind3.py
```

## Order (PST, Sun 1 Nov 2026)

1. 10:40 brief read; 10:42 `git log` subjects (they name M4's headline form, and E103's worst miss); 10:44 no Agent tool in this
   session, so the brief's fallback: the pool before the model.
2. 10:45-10:52 the kinds machinery only; the pool generated and hashed (`blind3.json` `60dfbf12…`); novelty checked.
3. **10:53:35 the pool committed and pushed, `a9167033`.** Only then were M4's files opened: Q132(b)'s README and
   `predict_m4.py`, E103's README, E106's.
4. 10:55-10:58 the bench built on the Intel; 10:58-11:00 its maps; 11:02-11:14 the reproduction check, exact.
   *Added after verification (C1), from the session's own record; this list left them out:* 11:01:42 `fit_m5.py` written,
   with `F0`–`F8` and E91's three anchor rows kept. 11:05:47 the first fit launched, on the 258 float and 75 int8 rows counted
   by then; 11:10:07 its results read: nested 0.216 W against 0.215 W for `F0`, `F7` picked in 120 of 124 folds. 11:12:23 `F9`
   added. 11:15:45 that fit's largest misses printed. 11:16:09 `F10`–`F12` added. 11:17:14 E91's anchor exception removed.
5. 11:14 the pool's tiles counted; then the 31 training tiles (11:35-12:00). *Added (C1):* 11:36:20-11:37:56 a second fit,
   `F0`–`F12` on the 256 float and 74 int8 rows then counted: nested 0.207 W, `F10` picked in 119 of 124 folds.
6. 12:01:48 the fit and the freeze; 12:04 the predictions; this commit (`64b4124e`, pushed 12:06:41), before E115's claim.
7. *After verification:* the corrections below, `corrections-check.py` and the contrasts' intervals (`contrasts_blind3.py`,
   the pool's `contrasts-blind3.json`), committed before E115's claim, with no frozen file changed.

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier read the pool, the model, the predictions and this page the same afternoon. It reran `make_blind3.py --check`, `fit_m5.py` and `predict_blind3.py` from a clean copy, and read this lane's own session record. Every number, sha256 and prediction reproduces; the pool's order and independence hold as stated. What did not hold is how the model's search and its gain were described. I checked each of its seven faults against the committed files in [`corrections-check.py`](corrections-check.py) and [`corrections-check.txt`](corrections-check.txt), and all seven hold. One wording it proposed reads the memory-path pair one way where the tiles' bits say both (C5), and I found one more error myself (C8). **No frozen file changed:** `m5.json`, `predictions-blind3.json` and `.md`, both counts files, `rows.json`, `loko.json`, `fit-output.txt`, `check-e102.*` and the three scripts are as committed in `64b4124e`, and they stay E115's blind predictions.

| | what was wrong | what changed |
|---|---|---|
| C1 (major) | **The model search changed after its first results had been read, and this page did not say so.** The first fit (11:05:47, read 11:10:07) had `F0`–`F8` and kept E91's three anchor rows; it read nested 0.216 W against 0.215 W for `F0`, so no extension helped. `F9` was added at 11:12:23, and `F10`–`F12` (the adder and the core per format, M5's form among them) at 11:16:09, 24 s after that fit's largest misses were printed, fp16 alternation tiles over-predicted by 0.45–0.54 W among them. E91's exception was removed at 11:17:14. "No form was dropped after a look" left that out, and the lane's blog line called the test "honest". Rerun on the committed rows: `F0`–`F8` alone 0.214 W against 0.211 W for `F0`; with E91's anchors kept 0.220 W; the full set with E91's anchors 0.203 W, fp32 card-1 pool 0.237 W. On the 27 float rows counted after the change: 0.194 W against 0.195 W for `F0` | § Order 4–5 give the steps with times. The forms and rows paragraphs, the table's † and its `F0`–`F8` row, and a new caveat say what was added after the look, and what E91's anchors do. The sentence reads "No form was dropped; `F9`–`F12` were added, and E91's anchors removed, after the first fit's results were read". The frozen `m5.json` and predictions stand, as blind predictions for E115 |
| C2 (major) | **"One extension earns its place" did not follow.** The 0.011 W nested gain over M4's form refitted has a paired-bootstrap 95% CI of −0.028 to +0.007 W (P(no gain) 0.12). On E102, the one set neither model was fitted on, M5 is no better than M4 and worse in three fp32 groups, and the term makes all four fp32 groups worse against M4's form refitted. Most of what the page credited to M5 against frozen M4 (E103's A side 0.179 / 0.170 / 0.260 W, real tensors 0.211 / 0.196 / 0.246 W, E104 fp16 0.315 / 0.296 / 0.363 W: M4's form refitted / M5 / M4 frozen) is the refit of M4's own form. M5 is worse than M4's form refitted on fp32's sign tiles and on E106. The parameter is resolved: add32 − add16 = 0.122 ± 0.030 fJ, z 4.0 | The headline says what M5 is, that the term was added after a look and that its value for prediction is not shown: E115 decides. "Reading it" carries the three-column table; § 4 adds the comparison with M4's form refitted; § 5 drops "wins" |
| C3 (minor) | **The lane's blog lines** (in its return, not on this page): "six fitted constants" left out the card scale; the 0.2 W is fp32/fp16 only, int8 0.26 W; "the chip's public RTL" against this page's caveat that core-et is a later revision; rows run 0.58–24.76 W, not 2–25 W; the kinds were picked by chasing misses; the misses list left out `w_h_add` (0.45–0.65 W over-predicted) and `int8.r_cancel` (+0.85 W, int8's largest) and the ladders M4 already misses (E60's low bits near 1 W, E70's spread 0.369 W; Q132(b) § 11) | The blog lines are rewritten in the lane's return. Here, § 2 says six constants and a scale |
| C4 (minor) | **int8's refit was implied to beat M4 out of sample.** On the 63 int8 rows M4 never saw it reads 0.256 W against 0.270 W for M5's nested procedure and 0.258 W for I3 refitted; on the 48 outside E78 and E82, 0.278 against 0.285 and 0.270 W | One paragraph under the int8 table |
| C5 (minor) | **The memory-path contrast was read one way and had no interval,** and none of the seven contrasts had a frozen 95% interval. Of the +8.38 W, 2.99 W is the multiplier, 2.05 W the fp32 adder, 2.61 W other nets and 0.74 W the bus. The verifier proposed "only a shortfall points at the memory path". The tiles' bits say both ways: only `m_bpair_eq`'s B lines change (3,552 bits an op against 0), but `m_blines_eq`'s B half-lines change about twice as often (3,680 against 1,776), so an excess would fit a half-line-wide path | The intervals are frozen now, before E115's claim, as a dated addendum: [`contrasts-blind3.json`](../../../../tools/claims-v3/kinds/blind3/contrasts-blind3.json) and `.md`, from [`contrasts_blind3.py`](contrasts_blind3.py). Each is the two tiles' frozen half-widths in quadrature, on a new card a3's widened by one card's step on the contrast. On pairs of training kinds this stand-in is about right, not conservative (C5 of the check). § 5 and § 6 read the pair both ways, with compute as the alternative |
| C6 (minor) | **The pool README's Order item 4 was rewritten in place in `64b4124e`,** not appended | Its original line is restored there, with a dated note below it giving the time and the sha |
| C7 (minor) | **The ± were not labelled,** and read as 95% where they are one jackknife standard error; the rms figures had no interval | § 2 says one s.e. and gives 1.96× for the adder's two prices; the bootstrap 95% intervals over kinds are given: floats 0.201 [0.180, 0.222], fp32 0.213 [0.182, 0.246], fp16 0.186 [0.161, 0.213], int8 0.262 [0.210, 0.320] W |
| C8 (mine, not the verifier's) | **§ 2 quoted int8's I3 on E78 alone as 3.123, 16.57, 1.820 fJ.** Refitted on E78's 15 rows it reads 3.092, 16.737, 1.795 fJ, M4 as frozen, as `predictions-blind3.json`'s refit check already showed (3.8e-16) | § 2 corrected |
