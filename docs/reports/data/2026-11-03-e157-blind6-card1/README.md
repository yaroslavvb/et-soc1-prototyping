# E157: blind pool 6 on aifoundry1 card 1 - every one of the session's 3,170 launches computed bit-exact C; M8 predicts a new kind's power to 0.39 / 0.10 / 0.33 W rms (fp32 FAILS P1), unbiased on its footing, 29 of 30 inside its bands, the die's rise to 0.12-0.18 °C, but no better than M6; K1's six pool-5 tiles reproduce E142 within Welch's interval on 5 of 6 and within 0.05 W on 3 (K1 FAILS) (Q139, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds". It bears on three ranks of Q138's final critic: **rank 2** (M8 scored on a sixth blind pool on
both 600 MHz cards; this is card 1's half, E153 is aifoundry3's), **rank 5** (the card term and a card's scale from cheap reads, § 7: scored
after E153's commit) and **rank 14** (no file tile's C had ever been checked; the complaint was first written in E78's README, § Joins and traps,
[`../2026-10-31-e78-kinds-energy-matrix/README.md`](../2026-10-31-e78-kinds-energy-matrix/README.md)). Tue 3 Nov 2026 (week 45), Q139
resumed, lane `a1c1-e157-blind6`. Pre-registered in **`01676499`** ([`tools/claims-v3/e157/README.md`](../../../../tools/claims-v3/e157/README.md),
committed and pushed 16:17:57 PST) before the claim (16:19:48) and the first launch (the smoke's, 16:20:31; the stop-path test before it
launched nothing). The model is Q139(m)'s M8 ([`m8.json`](../2026-11-03-q139m-model/m8.json), `122da8b6`); the pool, [blind pool 6](../../../../tools/claims-v3/kinds/blind6/README.md)
(50 tiles by a designer who never saw M8), and M8's, M7's and M6's frozen card-1 predictions
([`predictions-blind6-aifoundry1c1.json`](../../../../tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry1c1.json)) were committed by
Q139(x) in `d98d2e34` (05:39:23 PST), an ancestor of the registration. **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), 600 MHz in
every one of 27,115 samples; `ettelem config` read 14 times (the session's start, 16:20:11, and end, 17:06:21, and both ends of the stop-path
test, the smoke and every pass): TDP 65 W, threshold 65 °C, 600 MHz, 499 mV in every read, never set. **Every device-management command sent
was a read** (nine kinds, two of them the PMIC voltage-register reads the owner's rule of 2 November 2026 allows); no write
(`since_reset_ms` −1 in every sample). Card session 16:20:11–17:06:21 PST, **46.2 of the 55 card-minutes allowed**: the stop-path test
15702, the smoke 15701 and four passes, 15710–15713 (665, 675, 658, 674 s); three kept (15711 set aside by E78's pass gate).*

*Scored since (a dated note, Tue 3 Nov 2026, 17:27 PST; desk only; the first commit of this README, `fb2e5c6e`, 17:22:53, said X1, X2, S1
and S2 were handed on): E153 committed its primary reduction of pool 6 on aifoundry3 at 17:25:43 (`8e18eb67`), three minutes after this
lane's reduction and first commit. The registered `score_e157.py`, unchanged, was then run on this directory with `--e153` on that file
(E153's C check excluded no tile): [`scored-e153.json`](scored-e153.json), [`results-e153.md`](results-e153.md),
[`posthoc/score_with_e153.sh`](posthoc/score_with_e153.sh). Every other verdict is identical to `scored.json`'s. **X1 PASS**: card 1's float
D over aifoundry3's on 25 tiles, median **0.9632 [0.9613, 0.9659]**, holds M8's 0.9616 (M7's 0.9711 lies outside); **X2 PASS**: int8, 16 tiles,
0.9681 [0.9534, 0.9783]; **S1 PASS**: the zeros level's predicted 0.9707 is +0.78% from the measured ratio; **S2 PASS**: 0.9610, −0.74%. § 7
gives the reading and its sensitivity: on the registered footing the card term and the cheap-read scale hold to 1%; across this card's
reduction arms the float ratio moves 0.954–0.973, so X1 fails on three of five arms and S1 on two.*

**In plain words.** M8 is the lab's newest model of how much power a matmul draws (watts over the same kernel on zeros) and how far the die
warms (over a 4.5 s run), from the numbers it multiplies; on this card it carries a measured card term (card 1 draws 0.9616 times what
aifoundry3 draws on the same tiles). Here it predicted 50 tiles it had never seen, written by someone who never saw it, on the lab's second
600 MHz card. **The launches' results were right**: every one of the session's 3,170 launches, in every pass and the smoke, stored a C equal
bit for bit to the reference arithmetic, on all 1,024 minions, including the first silicon reads of int8's 32-bit wraparound, full-range
int8 operands, fp16 exponents spread wider than anything read before and twelve tiles cut from two public models. So no row here is
biased by a silent kernel error, and the six pool-5 tiles re-run computed the right C on the kernel that measured pool 5 (the rest of pool
5's rows are covered by that inference, not by a read of their own C). **Power**: M8 errs 0.39 W rms on fp32 (above what its nested score allows: P1
FAILS), 0.10 W on fp16 and 0.33 W on int8, about 2% of a float kind's switching watts and 7% of an int8 kind's; it is unbiased on its own
footing (+0.002 W on the floats), and 29 of the 30 priority-1 tiles sit inside its 95% bands. **It is not better than M6**, the model two
refits older: over the 30 priority-1 tiles M8's rms is 0.040 W larger (95% interval −0.013 to +0.128 W, not resolved), and on the E142 footing
it is resolved worse. What M8 added works where it was aimed and costs elsewhere: its C-register term reads the two C-candidate tiles to
0.09 W where M6 errs 0.32 W, and the twelve real tiles are its best case (0.15 W rms, 12 of 12 inside); its near-whole-byte int8 discount
over-corrects whole-line flip-flops (`int8.b_line_55_aa` +1.36 W, `int8.a_zeros_b_lineflip` +0.78 W measured over predicted), and its refit
reads exponent-heavy fp32 tiles about 0.3 W low. One single-bit tile (`fp32.b_onebit_b20_third`, B's mantissa bit 20 toggling in a third of
the lanes) draws 1.09 W less than every model says. **Heat**: the die's rise over a run is read to 0.18 / 0.18 / 0.12 °C rms, half the nested
score on the floats. **K1**: the six pool-5 tiles came back within the reproducibility E142's own spread predicts on five of six; `int8.gray_a`
read 0.19 W (4.4%) lower than in E142's session, outside Welch's ±0.15 W, so K1 FAILS as registered, and three of six moved more than the
critic's 0.05 W.

## Results

**1. The registered verdicts** (`scored.json` › `primary.rules` and `c_rules`; the arms › `arms.<name>.rules`). The primary is Q139(u)'s one
footing (card 1's frozen leakage slope 0.3134 W/°C, E82 A2's dips removed once), three kept passes (15710, 15712, 15713); 15711 was set aside
by E78's own gate (`fp16.zeros departs +0.384 W from its straight line`). The C check took no tile out of the scored set: all 50 are scored.

| rule | set | reading | interval or threshold | verdict | arms where it differs |
|---|---|---|---|---|---|
| **E157-PC** | every pool-6 launch in the kept passes (1,500) | 1,500 PASS, 0 ROUNDING, 0 UNMODELLED, 0 FAIL, 0 unrecorded (every pass: 2,024 of 2,024) | every launch a bit-exact PASS | **PASS** | — |
| **E157-PCa** | E78's six anchors and the tie, the session (820) | 820 PASS | the same | **PASS** | — |
| **E157-K1C** | K1's six tiles, the session, the smoke's included (246) | 246 PASS; the critic's literal "exact or within rounding": PASS | the same | **PASS** | — |
| **E157-K1D** | K1, \|D_E157 − D_E142\| on Q139(u)'s footing | within 0.05 W: 3 of 6 (`fp32.b_exp_busy_a_const` −0.172, `int8.gray_a` −0.187, `int8.b_line_zero_one` +0.137 W outside) | all six within 0.05 W | **FAIL** | (E142's own footing: the same 3 outside) |
| **E157-K1W** | K1, Welch's same-card 95% | 5 of 6 inside (`int8.gray_a` −0.187 W outside ±0.152 W) | all six inside | **FAIL** | (E142's own footing: the same tile, ±0.167 W) |
| **E157-K1** / **K1′** | K1C AND K1D / K1C AND K1W | | | **FAIL** / **FAIL** | |
| **E157-P1** | power, priority-1 fp32 (12) | rms **0.386 W** | ≤ 0.302 (2.5–97.5%: 0.096–0.302) | **FAIL** | none (0.387–0.421 W in every arm) |
| **E157-P2** | power, priority-1 fp16 (6) | rms **0.098 W** | ≤ 0.289 | **PASS** | — |
| **E157-P3** | power, priority-1 int8 (12) | rms **0.327 W** | ≤ 0.360 | **PASS** | — |
| **E157-B1** | bias, priority-1 floats (18) | mean(measured − M8) **+0.002 W** | −0.098 to +0.078 | **PASS** | E142's own footing FAIL LOW (+0.151); the session's own slope FAIL HIGH (−0.157) |
| **E157-B2** | bias, priority-1 int8 (12) | **−0.033 W** | −0.135 to +0.135 | **PASS** | — |
| **E157-C1** | power coverage, priority 1 (30) | **29 of 30** inside (`fp32.b_onebit_b20_third` outside) | ≥ 26 | **PASS** | — |
| **E157-M1** | M8 against M6, priority 1 (30) | rms(M8) − rms(M6) **+0.040 W** | 95% −0.013 to +0.128 | **NOT RESOLVED** | E142's own footing **WORSE** (+0.086 [+0.021, +0.178]) |
| **E157-M2** | M8 against M7 (30) | **+0.009 W** | −0.043 to +0.084 | **NOT RESOLVED** | — |
| **E157-H1** | die rise, priority-1 fp32 | rms **0.180 °C** | ≤ 0.501 (below 0.219: better than the nested score says) | **PASS** | — |
| **E157-H2** | die rise, priority-1 fp16 | **0.183 °C** | ≤ 0.571 | **PASS** | — |
| **E157-H3** | die rise, priority-1 int8 | **0.123 °C** | ≤ 0.201 | **PASS** | — |
| **E157-H4** | heat coverage, priority 1 | **29 of 30** (`int8.bheld_bit1` outside) | ≥ 26 | **PASS** | — |
| **E157-R1** | the 12 real tiles against the pool's own non-real tiles | rms **0.146 W** (the pool's own 0.420 W) | ≤ 0.641 (below 0.175) | **PASS** | — |
| **E157-R2** | the 12 real tiles inside M8's band | **12 of 12** | all | **PASS** | the session's own slope FAIL (`fp32.real_smol_softmax_v_causal`) |
| **E157-X1, X2, S1, S2** | the card term and card 1's scale from cheap reads | not scored at reduction time (E153's reduction did not exist yet); scored at 17:27 on E153's commit (`scored-e153.json`): X1 0.9632 [0.9613, 0.9659], X2 0.9681 [0.9534, 0.9783], S1 +0.78%, S2 −0.74% | holds 0.9616; within 1% | **PASS ×4** (§ 7) | X1 FAIL on E142's own footing, the session's slope and 0.2955; S1 FAIL at the session's slope and 0.3320 |

The dips-kept arm keeps one pass (E78's gates set three aside on the meter's dips: `fp32.randn spans 2.026 W`, `fp16.randn spans 2.445 W`,
`anchor_pi drifts +0.687 W`, as E142 saw), so it scores nothing. The anchor gates relaxed (all four passes kept) and the slope's interval
(0.2955, 0.3320 W/°C) change none of the verdicts scored at reduction time; they do move X1, S1 and S2 (§ 7).

**2. Power, the three models on the same tiles** (measured − predicted, W; `scored.json` › `primary.reported`; [`posthoc/posthoc.txt`](posthoc/posthoc.txt) (d)):

| | fp32 rms (bias), 12 | fp16 rms (bias), 6 | int8 rms (bias), 12 | priority 1, 30: rms (bias) | all 44 non-anchor: rms (bias) | real, 12 | inside 95% (30 / 44) |
|---|---|---|---|---|---|---|---|
| **M8** (scored) | **0.386** (−0.014) | **0.098** (+0.032) | **0.327** (−0.033) | **0.323** (−0.012) | 0.366 (+0.022) | 0.146 | 29 / 40 |
| M7 (frozen, beside) | 0.395 (−0.143) | 0.136 (−0.099) | 0.285 (−0.118) | 0.314 (−0.124) | 0.319 (−0.091) | 0.184 | 29 / 42 |
| M6 (frozen, beside) | 0.377 (−0.160) | 0.134 (−0.060) | 0.222 (−0.153) | **0.283** (−0.137) | **0.274** (−0.114) | 0.160 | 29 / 41 |

On all 44 non-anchor tiles M8 minus M6 is +0.092 W (95% −0.000 to +0.201; reported). M6 and M7 read about 0.12-0.14 W high on this footing,
M8 near zero: each model is nearly unbiased on the footing it was fitted on (on E142's own footing, 0.2414 W/°C, M6's bias is −0.020 W and M8's
+0.105), so the bias is the footing's and the scatter is the models'.

**3. Where M8 gains and loses: by the pool's case** (non-anchor tiles, rms (bias), W; [`posthoc/posthoc.txt`](posthoc/posthoc.txt) (c)):

| case | tiles | M8 | M7 | M6 | the tiles that carry it (measured − M8) |
|---|---:|---|---|---|---|
| C, the C-register candidate (busy operands, still accumulator) | 2 | **0.094** (−0.086) | 0.229 | 0.322 | M8's new float term works where it was aimed |
| R, real tiles (W8A8 projections, attention, two public models) | 12 | **0.146** (−0.019) | 0.184 | 0.160 | `fp32.real_smol_softmax_v_causal` −0.34, `int8.real_qwen_w8a8_v` −0.27 |
| W, seeded weights | 2 | 0.082 | 0.119 | 0.113 | |
| E, exponent-heavy | 10 | 0.293 (**+0.204**) | 0.217 | **0.167** | `fp32.exp_a_pow2wide_b_randn` +0.71, `exp_a_walk_fixedmant` +0.33, `exp_b_alt_shift` +0.32, `exp_only_narrow2` +0.26: M8 reads fp32 exponent work about 0.3 W low |
| L, whole-line int8 flip-flops | 4 | **0.717** (+0.363) | 0.422 | 0.340 | `int8.b_line_55_aa` **+1.36** (outside its band), `int8.b_line_zero_ff` +0.37: M8's near-whole-byte discount (`bsat`) over-corrects |
| Z, zeros' transport | 4 | 0.449 (+0.281) | 0.234 | 0.224 | `int8.a_zeros_b_lineflip` +0.78 (M8 −0.33 W, measured +0.46; M6 within 0.04), `fp32.negzero_a_b_complement` +0.43 |
| S, single bits | 5 | 0.533 (−0.326) | 0.600 | 0.542 | `fp32.b_onebit_b20_third` **−1.09** (every model, outside every band), `fp16.b_onebit_b6_third` −0.46 |
| B, int8 B bit positions | 5 | 0.304 (−0.290) | 0.383 | 0.267 | `int8.bheld_bit4` −0.43, `bheld_bit1` −0.31, `bheld_bit7` −0.31: every model reads int8's held-B tiles about 0.3 W high |

**4. Every tile** (W and °C; measured is the mean over three kept passes; **out** = outside M8's frozen 95% band):

| tile | prio | case | D measured, W (sd, 3 passes) | M8 D [95%] | − M8 | − M7 | − M6 | die rise measured, °C | M8 rise [95%] | − M8 |
|---|---|---|---|---|---:|---:|---:|---:|---|---:|
| `fp32.a_onebit_b5_third` | 1 | S | 8.964 (0.193) | 9.08 [8.64, 9.52] | -0.120 | -0.157 | -0.103 | 1.34 | 1.25 [0.57, 1.94] | +0.09 |
| `fp32.a_zeros_b_complement` | 1 | Z | 1.422 (0.255) | 1.48 [1.02, 1.93] | -0.055 | -0.069 | -0.305 | 0.00 | 0.38 [-0.31, 1.06] | -0.38 |
| `fp32.b_onebit_b12_third` | 1 | S | 9.554 (0.105) | 9.47 [9.04, 9.91] | +0.080 | +0.015 | +0.041 | 1.48 | 1.30 [0.61, 1.98] | +0.19 |
| `fp32.b_onebit_b20_third` | 1 | S | 12.132 (0.109) | 13.22 [12.78, 13.66] **out** | -1.089 | -1.208 | -1.119 | 1.72 | 1.73 [1.04, 2.42] | -0.01 |
| `fp32.bf16_wideexp` | 1 | E | 18.696 (0.134) | 18.67 [18.22, 19.13] | +0.022 | -0.199 | -0.253 | 2.65 | 2.36 [1.67, 3.04] | +0.29 |
| `fp32.exp_a_walk_fixedmant` | 1 | E | 12.465 (0.223) | 12.14 [11.70, 12.58] | +0.326 | +0.181 | +0.165 | 1.40 | 1.60 [0.92, 2.29] | -0.20 |
| `fp32.exp_b_alt_shift` | 1 | E | 15.747 (0.128) | 15.43 [14.98, 15.88] | +0.317 | +0.120 | +0.182 | 2.13 | 1.98 [1.30, 2.67] | +0.15 |
| `fp32.exp_only_narrow2` | 1 | E | 14.677 (0.226) | 14.42 [13.97, 14.86] | +0.262 | +0.136 | +0.148 | 1.83 | 1.87 [1.18, 2.55] | -0.03 |
| `fp32.negzero_a_b_complement` | 1 | Z | 16.464 (0.223) | 16.03 [15.57, 16.49] | +0.435 | +0.210 | -0.299 | 2.15 | 2.05 [1.37, 2.74] | +0.10 |
| `fp32.real_qwen_dequant_q` | 1 | R real | 19.531 (0.180) | 19.51 [19.07, 19.95] | +0.018 | -0.097 | +0.014 | 2.60 | 2.45 [1.77, 3.14] | +0.15 |
| `fp32.real_smol_softmax_v_causal` | 1 | R real | 12.827 (0.070) | 13.17 [12.73, 13.61] | -0.341 | -0.405 | -0.330 | 1.69 | 1.72 [1.04, 2.41] | -0.03 |
| `fp32.signexp_invert_b` | 1 | E | 16.402 (0.157) | 16.42 [15.96, 16.88] | -0.018 | -0.244 | -0.057 | 2.24 | 2.10 [1.41, 2.78] | +0.14 |
| `fp32.a_onebit_b16_half` | 2 | S | 9.266 (0.095) | 9.31 [8.87, 9.75] | -0.043 | -0.106 | -0.082 | 1.00 | 1.28 [0.59, 1.96] | -0.28 |
| `fp32.c_absorbed` | 2 | C | 19.072 (0.176) | 19.20 [18.75, 19.64] | -0.124 | -0.247 | -0.362 | 2.28 | 2.42 [1.73, 3.10] | -0.13 |
| `fp32.exp_a_pow2wide_b_randn` | 2 | E | 19.137 (0.114) | 18.43 [17.98, 18.88] **out** | +0.710 | +0.498 | +0.207 | 2.39 | 2.33 [1.64, 3.01] | +0.06 |
| `fp32.real_qwen_softmax_v` | 2 | R real | 23.381 (0.031) | 23.32 [22.88, 23.77] | +0.057 | -0.044 | -0.003 | 2.83 | 2.89 [2.21, 3.58] | -0.06 |
| `fp32.anchor6_randn` | 2 (anchor) | 0 | 23.939 (0.107) | 23.78 [23.34, 24.22] | +0.160 | +0.052 | +0.014 | 3.17 | 2.94 [2.26, 3.63] | +0.22 |
| `fp32.anchor6_zeros` | 2 (anchor) | 0 | -0.048 (0.080) | 0.00 [-0.43, 0.43] | -0.048 | -0.048 | -0.048 | -0.02 | 0.21 [-0.48, 0.89] | -0.22 |
| `fp16.e5m2grid_wide` | 1 | E | 17.196 (0.044) | 17.23 [16.85, 17.62] | -0.039 | -0.223 | -0.254 | 2.40 | 2.19 [1.50, 2.88] | +0.21 |
| `fp16.exp_b_alt_shift` | 1 | E | 15.084 (0.102) | 14.93 [14.55, 15.31] | +0.152 | -0.002 | +0.130 | 1.72 | 1.92 [1.23, 2.62] | -0.21 |
| `fp16.exp_only_narrow2` | 1 | E | 15.413 (0.057) | 15.30 [14.92, 15.68] | +0.115 | +0.004 | +0.018 | 2.00 | 1.97 [1.27, 2.66] | +0.03 |
| `fp16.real_qwen_qk` | 1 | R real | 18.258 (0.037) | 18.28 [17.90, 18.66] | -0.024 | -0.142 | -0.107 | 2.07 | 2.31 [1.62, 3.00] | -0.24 |
| `fp16.real_smol_qk` | 1 | R real | 20.826 (0.107) | 20.74 [20.36, 21.11] | +0.090 | -0.028 | -0.034 | 2.77 | 2.59 [1.90, 3.28] | +0.17 |
| `fp16.real_smol_softmax_v` | 1 | R real | 16.774 (0.122) | 16.88 [16.50, 17.25] | -0.103 | -0.201 | -0.115 | 2.30 | 2.15 [1.46, 2.84] | +0.15 |
| `fp16.a_zeros_b_complement` | 2 | Z | 1.421 (0.127) | 1.46 [1.07, 1.86] | -0.040 | -0.054 | -0.132 | 0.20 | 0.37 [-0.32, 1.06] | -0.17 |
| `fp16.b_onebit_b6_third` | 2 | S | 11.779 (0.075) | 12.24 [11.86, 12.62] **out** | -0.459 | -0.548 | -0.444 | 1.35 | 1.61 [0.92, 2.31] | -0.26 |
| `fp16.c_absorbed` | 2 | C | 19.054 (0.051) | 19.10 [18.72, 19.48] | -0.047 | -0.209 | -0.277 | 2.47 | 2.40 [1.71, 3.10] | +0.06 |
| `fp16.exp_a_walk_fixedmant` | 2 | E | 12.221 (0.030) | 12.02 [11.65, 12.40] | +0.197 | +0.079 | +0.059 | 1.72 | 1.59 [0.90, 2.28] | +0.13 |
| `fp16.real_qwen_dequant_v` | 2 | R real | 21.167 (0.100) | 21.04 [20.66, 21.42] | +0.130 | +0.010 | -0.050 | 2.67 | 2.63 [1.94, 3.32] | +0.04 |
| `fp16.anchor6_randn` | 2 (anchor) | 0 | 21.187 (0.021) | 21.23 [20.85, 21.61] | -0.040 | -0.153 | -0.214 | 2.83 | 2.65 [1.96, 3.34] | +0.18 |
| `fp16.anchor6_zeros` | 2 (anchor) | 0 | -0.098 (0.084) | 0.00 [-0.37, 0.37] | -0.098 | -0.098 | -0.098 | 0.00 | 0.20 [-0.49, 0.90] | -0.20 |
| `int8.a_word_zero_one` | 1 | L | 2.511 (0.312) | 2.75 [2.05, 3.45] | -0.236 | -0.192 | -0.106 | 0.33 | 0.58 [0.31, 0.86] | -0.25 |
| `int8.a_zeros_b_lineflip` | 1 | Z | 0.457 (0.081) | -0.33 [-1.67, 1.01] | +0.782 | +0.409 | -0.035 | 0.13 | 0.23 [-0.04, 0.51] | -0.10 |
| `int8.b_line_zero_ff` | 1 | L | 3.633 (0.079) | 3.26 [2.08, 4.44] | +0.375 | +0.028 | -0.360 | 0.67 | 0.64 [0.37, 0.92] | +0.02 |
| `int8.b_line_zero_full` | 1 | L | 4.025 (0.157) | 4.07 [3.37, 4.78] | -0.049 | +0.058 | -0.042 | 0.67 | 0.74 [0.46, 1.01] | -0.07 |
| `int8.bheld_bit1` | 1 | B | 5.633 (0.051) | 5.95 [5.17, 6.73] | -0.314 | -0.414 | -0.261 | 0.67 | 0.95 [0.68, 1.23] **out** | -0.29 |
| `int8.bheld_bit4` | 1 | B | 5.203 (0.059) | 5.63 [4.86, 6.40] | -0.428 | -0.521 | -0.375 | 1.00 | 0.92 [0.64, 1.19] | +0.08 |
| `int8.bheld_bit7` | 1 | B | 4.996 (0.163) | 5.30 [4.55, 6.05] | -0.306 | -0.401 | -0.258 | 0.92 | 0.88 [0.60, 1.15] | +0.04 |
| `int8.powerlaw_df4_pc` | 1 | W | 6.439 (0.057) | 6.50 [5.81, 7.19] | -0.060 | -0.127 | -0.132 | 1.00 | 1.02 [0.74, 1.29] | -0.02 |
| `int8.real_qwen_w8a8_gate` | 1 | R real | 6.413 (0.033) | 6.47 [5.78, 7.16] | -0.056 | -0.097 | -0.101 | 1.00 | 1.01 [0.74, 1.29] | -0.01 |
| `int8.real_qwen_w8a8_v` | 1 | R real | 6.168 (0.204) | 6.44 [5.75, 7.13] | -0.269 | -0.346 | -0.357 | 1.00 | 1.01 [0.73, 1.28] | -0.01 |
| `int8.real_smol_w8a8_down` | 1 | R real | 5.278 (0.177) | 5.23 [4.54, 5.92] | +0.050 | +0.084 | +0.111 | 0.98 | 0.87 [0.60, 1.15] | +0.11 |
| `int8.real_smol_w8a8_q` | 1 | R real | 6.404 (0.177) | 6.29 [5.60, 6.99] | +0.110 | +0.108 | +0.085 | 1.00 | 0.99 [0.72, 1.27] | +0.01 |
| `int8.b_line_55_aa` | 2 | L | 7.229 (0.192) | 5.87 [4.65, 7.08] **out** | +1.364 | +0.818 | +0.565 | 1.00 | 0.94 [0.67, 1.22] | +0.06 |
| `int8.bflip_bit2_w` | 2 | B | 1.931 (0.135) | 2.08 [1.34, 2.81] | -0.147 | -0.222 | -0.144 | 0.63 | 0.51 [0.23, 0.78] | +0.13 |
| `int8.bflip_bit5_w` | 2 | B | 1.826 (0.230) | 2.08 [1.35, 2.81] | -0.253 | -0.282 | -0.243 | 0.67 | 0.51 [0.23, 0.78] | +0.16 |
| `int8.powerlaw_df15_pt` | 2 | W | 2.467 (0.246) | 2.57 [1.87, 3.27] | -0.099 | -0.110 | -0.090 | 0.67 | 0.56 [0.29, 0.84] | +0.10 |
| `int8.real_qwen_w8a8_down` | 2 | R real | 6.016 (0.170) | 5.91 [5.21, 6.61] | +0.105 | +0.147 | +0.108 | 0.68 | 0.95 [0.67, 1.22] | -0.27 |
| `int8.anchor6_full` | 2 (anchor) | 0 | 6.826 (0.120) | 6.76 [6.06, 7.45] | +0.069 | -0.002 | +0.036 | 1.00 | 1.05 [0.77, 1.32] | -0.05 |
| `int8.anchor6_zeros` | 2 (anchor) | 0 | 0.034 (0.136) | 0.00 [-0.67, 0.67] | +0.034 | +0.034 | +0.034 | 0.00 | 0.27 [-0.01, 0.54] | -0.27 |

The pool's own anchors agree with E78's built-in ones: its zeros tiles read −0.048 / −0.098 / +0.034 W over E78's zeros (fp32 / fp16 / int8),
its random tiles 23.94 / 21.19 / 6.83 W against E78's `fp32.randn` 23.77, `fp16.randn` 21.34, `int8.full` 6.82 W in the same passes.

**5. Heat** (measured − M8, °C): bias +0.038 (fp32), +0.020 (fp16), −0.040 (int8) on the priority-1 tiles; M7 (whose law M8 carries) and M6
read alike (0.17–0.18 / 0.18 / 0.13 °C rms). The rise per board W over the 44 non-anchor tiles is **0.1160 °C/W** against M8's 0.1151
(+0.8%; `primary.reported_rise_per_board_w`). int8's rises are the readout's whole degrees (0.33–1.00 °C), so H3's 0.123 °C is mostly
quantisation. **Heat at the measured run length** (reported): the registered arm as written reads int8 at 1.06 °C rms, because 18 items'
median "run length" (5.8–8.9 s; 12 of them pool-6 tiles) spans the heater's pass after a cool tile; with E142's rule (items over 5.0 s left out, as M7's heat rows do;
[`posthoc/posthoc.txt`](posthoc/posthoc.txt) (a), post hoc), H2's run-length term reads **0.130 / 0.172 / 0.183 °C** (fp32 / fp16 / int8,
11 / 6 / 8 tiles) against 0.180 / 0.183 / 0.123 °C at the frozen 4.5 s: better on fp32, worse on int8, as on E142.

**6. K1 and the C check** (`scored.json` › `c_rules`, `k1`; [`ccheck/ccheck-session.txt`](ccheck/ccheck-session.txt), `ccheck-session.json.gz`).
Every launch of the session went through Q139(k)'s C-logging host (`4f0956ce…`, built on aifoundry1 from `main.cpp` `0f53a7d5…`) with the
power passes' kernel (`990807f4…`) and `--c-poison`, and was checked at the desk by `ccheck.py check` against `accum.c` (`dc47efbc…`):
**3,170 launches, 3,170 PASS** (fp32 1,226, fp16 852, int8 1,092): one distinct C over all 1,024 minions in every launch, equal bit for bit
to the RTL's arithmetic (int8 mod 2^32), no ROUNDING, no record missing. 36 of the 56 tiles carried first-read notes before the run
(`tools/claims-v3/e157/ccheck-domain.txt`), so these launches are the **first silicon reads** of: int8's 32-bit wraparound (int8 launches ran
890,165–915,884 ops, past the 750,000 at which 14 int8 tiles' words already wrap), full-range int8 operands (±127, −128) and int8 C over all 1,024 minions on
a file tile; fp32 exponent spreads up to 127 and fp16 up to 29 (E104 read 61 and 25); up to 945 distinct fp16 operand magnitudes (E104: 662);
and twelve real tiles' value distributions. All PASSED, so the reference's arithmetic holds there too. **K1's D** (W; E157 − E142 on each
footing; `k1` and [`posthoc/posthoc.txt`](posthoc/posthoc.txt) (b)):

| K1 tile | E157 D, Q139(u)'s footing (se, 3 passes) | E142 D (se, 5) | E157 − E142 | Welch half-width | inside Welch | within 0.05 W | on E142's own footing: − E142 |
|---|---|---|---:|---:|---|---|---:|
| `fp32.b_exp_busy_a_const` | 14.795 (0.058) | 14.967 (0.055) | −0.172 | 0.205 | yes | no | −0.184 |
| `fp32.real_pythia_ln1_q` | 21.325 (0.001) | 21.311 (0.047) | +0.014 | 0.130 | yes | yes | +0.025 |
| `fp16.sparse24_aligned` | 12.350 (0.082) | 12.316 (0.031) | +0.034 | 0.306 | yes | yes | +0.009 |
| `fp16.exp_only` | 15.634 (0.045) | 15.662 (0.028) | −0.028 | 0.153 | yes | yes | −0.044 |
| `int8.gray_a` | 4.024 (0.013) | 4.211 (0.055) | **−0.187** | 0.152 | **no** | no | −0.189 |
| `int8.b_line_zero_one` | 3.364 (0.065) | 3.227 (0.085) | +0.137 | 0.263 | yes | no | +0.078 |

The frame itself reproduced more tightly: E78's random anchors moved −0.061 / +0.017 / −0.040 W (`fp32.randn` / `fp16.randn` / `int8.full`)
and the idle level 33.059 W against 33.055, so the K1 differences are the tiles', at a session-to-session scatter of about 0.1–0.2 W (one of
six outside a 95% interval is what chance gives a quarter of the time). The C check rules out the cause the critic feared: those launches
computed the right C. **What it does to the rows**: rank 14's guard holds (no file-tile row on this card rests on a wrong computation), and
its reproducibility half fails by the critic's 0.05 W and on one tile by Welch's: a repeated pool-5 tile on this card reproduces to about
0.1–0.2 W, not 0.05.

**7. The card term (X1, X2) and card 1's scale from cheap reads (S1, S2)** (rank 5; scored at 17:27 PST, after E153's commit: the dated
note at the top; [`scored-e153.json`](scored-e153.json) › `primary.rules`). When this lane reduced, E153's committed primary reduction of
pool 6 on aifoundry3 did not exist (E153's session ran beside this one, from 16:21 PST), and the first commit of this README handed the four
rules on. E153 committed it at 17:25:43 (`8e18eb67`, its C check excluding no tile); the registered scorer, unchanged, then gave:

| rule | tiles (both cards, D ≥ 5 W floats, ≥ 1 W int8) | measured: median D(card 1) / D(aifoundry3) [95%] | prediction | verdict |
|---|---:|---|---|---|
| **E157-X1**, floats | 25 | **0.9632** [0.9613, 0.9659] | M8's card term 0.9616 (M7's 0.9711: outside) | **PASS** |
| **E157-X2**, int8 | 16 | **0.9681** [0.9534, 0.9783] | 0.9616 (M7's 0.9735: inside) | **PASS** |
| **E157-S1**, floats | X1's | 0.9632 | the zeros level, physical, frozen reads: **0.9707 (+0.78%)** | **PASS** (within 1%) |
| **E157-S2**, int8 | X2's | 0.9681 | **0.9610 (−0.74%)** | **PASS** |

Every other read and form, against the same measured ratios (floats / int8): V600² 0.9102 / 0.9011 (**−5.5% / −6.9%**: the physical
candidate fails on card 1 again), V600 fitted −8.8% / −19.6%, the zeros level fitted +2.6% / +0.9%, the leakage slope fitted +1.2% / −1.7%,
physical +31% / +29%, idle power physical +32% / +30%, fitted +41% / +85%. E153-CS1's reading (the measured median within 1% of M8's 0.9616)
holds for both families (+0.17%, +0.68%). **The sensitivity, reported** (the same rules at card 1's reduction arms, E153's primary fixed): the
float ratio is 0.9727 on E142's own footing, 0.9538 at the session's own slope, 0.9658 and 0.9608 at Q139(u)'s slope interval (0.2955,
0.3320 W/°C) and 0.9632 with the anchor gates relaxed, so X1 FAILS on three of the five scored arms and S1 on two (S2 on three, X2 on one).
So on the registered footing (Q139(u)'s on both cards) the card term and the zeros-level scale hold to better than 1%; the 1% itself is
narrower than what the footing alone moves (about ±1%), which is the critic's rank 1 again. And the read must be the frozen one: card 1's
zeros level re-read in this session (the pool's own fp32 zeros tile, 1.833 W of board over idle against the frozen 1.661 W from E142's
session, +10%) would put the scale at 1.071 (`primary.reported_card_scale_reread`), so a single session's zeros level is not a cheap read
stable to 1%. The idle level reproduced (33.06 W both days) but predicts nothing (+32%).

**8. The footing** (reported). The session's own fitted leakage slope is 0.390 W/°C (E142's session: 0.408), above Q139(u)'s frozen 0.3134
(interval 0.296–0.332). At the session's slope the floats read 0.157 W high (B1 FAIL HIGH) and at E142's 0.2414 0.151 W low (FAIL LOW):
the bias verdict still turns on the footing, as the critic said; the rms (P1–P3), coverage, heat and real-tile verdicts do not.

**9. What it does to predicting power and heat** (the before/after the owner's goal asks for):

| quantity (aifoundry1 card 1, 600 MHz, a kind never seen) | before (the claim tested) | after (E157, blind) |
|---|---|---|
| power, fp32 | M8 nested 0.198 W rms | **0.386 W** (P1 FAIL; M6 0.377, M7 0.395) |
| power, fp16 | M8 nested 0.170 W | **0.098 W** (M6 0.134) |
| power, int8 | M8 nested 0.238 W | **0.327 W** (M6 0.222) |
| power, the 30 priority-1 / all 44 new kinds | pool 5 on this card (E142, M7): 0.211 W over 30 | **0.323 / 0.366 W**, bias −0.012 / +0.022 W; M6 0.283 / 0.274 |
| M8 against M6 (the critic's rank 2, card 1's half) | nested, floats: −0.014 W [−0.026, −0.001] against M6 as frozen (resolved, in sample; mostly the footing refit, Q139(m)'s dated note) | **+0.040 W [−0.013, +0.128], NOT RESOLVED** (WORSE on E142's footing) |
| coverage of the 95% bands | not tested blind | **29 of 30** (C1 PASS), 40 of 44 non-anchor |
| real tiles (rank 8) | pool 5: one softmax-times-values tile 0.60 W off on aifoundry3 | **0.146 W rms, 12 of 12 inside** (R1, R2 PASS) |
| heat, the die's rise over 4.5 s | nested 0.352 / 0.355 / 0.141 °C; E142 0.167 / 0.162 / 0.139 | **0.180 / 0.183 / 0.123 °C** (H1–H4 PASS); 0.1160 °C/W against 0.1151 |
| validity of file-tile rows (rank 14) | no launch's C ever read on a file tile | **3,170 of 3,170 launches bit-exact**; K1's D reproduces to 0.1–0.2 W, not 0.05 (K1 FAIL) |
| the card term on pool 6 (rank 5) | E142's X1 failed post hoc (0.982 vs 0.9711); no cheap read within 1% in training | **M8's 0.9616 holds** (floats 0.9632, int8 0.9681); the zeros level predicts the scale to **+0.78% / −0.74%** (S1, S2 PASS), on the registered footing; footing-sensitive (0.954–0.973) |

The terms this tests: M8's two new ones and its footing refit. The C-register term earns its place (the two C tiles 0.094 W against M6's
0.322). The near-whole-byte int8 discount does not: it makes the whole-line tiles 0.72 W rms against M6's 0.34, and the zeros-transport tile
that tests it most directly misses by +0.78 W where M6 is within 0.04. The footing refit removed the bias on its own footing but did not
lower the scatter. **For an unseen kind on this card, the honest error now is about 0.3 W rms (2% of a float kind, 5–7% of an int8 kind),
with M6 as good as M8**; the heat over a run follows from the power to about 0.15 °C. Carried to another card through the card term, the
scale is the measured 0.9616 to 0.2% (floats) and 0.7% (int8) on pool 6, and the frozen zeros-level read predicts it to under 1%, on the one footing.

## Registered against what happened

| registered | happened |
|---|---|
| the claim and first launch after `01676499` (and `d98d2e34` before it) | 16:17:57 commit; 16:19:48 claim; 16:20:31 first launch; `git merge-base --is-ancestor d98d2e34 01676499` yes |
| `et-who` clean on card 1; never beside another of our sessions on aifoundry1 | clean at the claim, the launch and the end; card 0 idle throughout |
| stop-path test 15702: die, board, watcher each EXIT_HOT on a live sample | all three fired, on samples 0.035, 0.03 and 0.06 s old |
| smoke 15701 and its gate (with the C log's structure) | PASS: 60 launch records, 60 C records, one distinct C each, launch gaps 2–3 ms |
| passes 15710–15714 as the budget allows (expected 4), at least two kept | four ran (665, 675, 658, 674 s), all rc 0; the budget stopped p15714 (its projected end T0 + 3,445 s > 3,240 s); three kept (15711 set aside by E78's gate) |
| stops: board ≥ 66 W or a shire field ≥ 72 °C | none fired: board at most 61.10 W (p99.9 60.33–60.74 per pass), shire mean at most 63 °C, the shire field's high-water latch 65 °C throughout ([`telemetry-max.json`](telemetry-max.json)) |
| at most 55 card-minutes; no session after 21:00, every run ends by 22:00 PST | 46.2 card-minutes (16:20:11–17:06:21) |
| every measured launch C-logged and checked at the desk | 3,170 launches logged (the burn-in's included), all PASS |
| X1, X2, S1, S2 with E153's committed reduction | not committed when this lane reduced (17:08-17:20); committed 17:25:43; scored 17:27 with the registered code: PASS ×4 |

## Departures and post hoc

- **D1** (during the session, labelled): at 16:40 PST, after pass 15710 had ended on the box, this lane copied that pass to the Intel and ran
  `ccheck.py check` on its C log (780 launches, all PASS). No reduction was run or read until the session had ended; the queue's pass count
  is set by its budget rule alone.
- **D2** (an E78-protocol event): pass 15712's run #64 (`fp32.randn`, one of E78's three per-pass instances of that anchor) was skipped by
  E78's runner (launch reading not reached), so 15712 has 75 runs; the reduction interpolates the anchor from its other two instances. E153's
  amendment A1 (a tile with no launch in a kept pass is unmeasured, not a C failure) does not arise here: every pool-6 tile ran in every
  kept pass.
- **Post hoc** ([`posthoc/posthoc_e157.py`](posthoc/posthoc_e157.py) → [`posthoc/posthoc.txt`](posthoc/posthoc.txt), standard library,
  reproducible from this directory): (a) heat at the measured run length with E142's 5.0 s rule; (b) the anchors and K1 against E142 on both
  footings; (c) errors by case; (d) the 44 non-anchor tiles by format. [`posthoc/telemetry_max_e157.py`](posthoc/telemetry_max_e157.py) →
  [`telemetry-max.json`](telemetry-max.json), run on the raw copy. None is a verdict.
- The earlier attempt of this lane (06:35-06:55 PST) left only uncommitted files; the registration says what was re-checked and corrected
  before the commit.

## Device commands sent

*The owner's rules of Mon 2 Nov 2026.* As registered (`tools/claims-v3/e157/README.md`, § Device commands sent), classified at et-platform
`836a4ab` (BL2 0.22.0): `ettelem config` (14 reads: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) and `ettelem sample --seconds --every-ms 100` through E128's guard in every block (GET_MODULE_POWER,
GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES): every one a READ, the two voltage
commands the PMIC voltage-register reads the owner allows. Never sent: the statistics reset (`since_reset_ms` −1 in all 27,115 samples), any
SET_*, the firmware-revisions query, a residency read, `dev_mngt_service` (the drain was replaced by a refusal, and no refusal line appears).
The host programs (E78's `sparsity_host` as the heater, Q139(k)'s patched host for every measured launch) open the ops node only; the patch's
two additions are one more 1 MiB DMA read and write per launch. The box ran `preflight_e157.sh` before any device opened: **GO**, 32 send
sites, 0 disallowed ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)); `check_e157.py` HARNESS OK on 90 files before the session and
before every pass (`logs/session.log`, each pass's `binaries.sha256`).

## Card and post

aifoundry1 card 1, release 1.4.0 (BL2 0.22.0, as E156 read it this morning), 600 MHz, 499 mV; card 0 was not used. The day's one post in
`#community-lab` did not exist when this lane reserved (no card post dated 3 Nov: the earlier one, created 04:29, is gone, and was neither
re-created nor cited as live): this lane posted it, message **1567332504330051616**, 16:19:48 PST, `<ai> **Claude says:** using aifoundry1
card 1 for 1.5 h, until ~17:49 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`. By 16:24 the aifoundry3 and
aifoundry2 lanes had added their clauses. At the release (17:06:57–17:07, under the discord lock, `EXPECT_TEXT`, dry run, save) this card's
clause was dropped, the other two still held: `<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~17:51 PST [doc](<…>); using aifoundry2
for 1.5 h, until ~17:54 PST [doc](<…>)`, read back from the rendered message (edited 5:07 PM; the plan's cached source text lagged, as on
E142). Mon 2 Nov's post was not touched. [`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt) has the order of events.

## What it changes

- **Kinds page § 11, item 6** (and the "How well power and heat can be predicted" table): card 1's blind figure for a new kind becomes
  pool 6's: M8 0.39 / 0.10 / 0.33 W rms (fp32 / fp16 / int8), P1 FAIL, unbiased on its footing, 29 of 30 inside; **M8 is not better than M6
  on card 1** (+0.040 W, not resolved; worse on E142's footing), so "M8 beats M6" must not be quoted for this card. Heat over a run 0.12–0.18 °C.
- **Rank 2, card 1's half**: not met (M8 − M6 not resolved below zero). **Rank 14**: the C half closes (3,170 of 3,170 bit-exact, the
  first silicon reads of int8's wrap and full range, wide fp16 exponents and real tiles); the D half fails as written (K1 FAIL: 3 of 6 within
  0.05 W, 5 of 6 within Welch). **Rank 5**: on the registered footing M8's card term holds on pool 6 (X1, X2 PASS) and card 1's scale is predicted from its frozen zeros level to +0.78% / −0.74% (S1, S2 PASS, the critic's 1%); V² misses by −5.5%; the verdicts move with the footing (X1 fails on three of five arms), and the zeros level re-read today is 10% off its frozen value, so the predictor is not yet a session-independent cheap read.
- **For M9** (named, not fitted): drop or cap `bsat` (whole-line int8 L/Z cases), an exponent-field term for fp32 (E case +0.20 W bias),
  int8's held-B tiles (every model 0.3 W high), and B's high mantissa bits in fp32 (`fp32.b_onebit_b20_third`, −1.09 W in every model).
- **Records to add** (integration lanes): 03-experiments (E157), 05-claims (item 6 on card 1 with pool 6; rank 14's C half), 14-card-behaviour
  (the session, the K1 scatter of 0.1-0.2 W between days, the zeros level's +10%), 04-artifacts; the Horace hub's Log (a new entry) and Status.

## Files

| file | what |
|---|---|
| `e157.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the primary reduction (Q139(u)'s footing, 0.3134 W/°C, dips removed once) |
| `e157-e142footing.json`, `e157-auto.json`, `e157-dipskept.json`, `e157-leak0.2955.json`, `e157-leak0.3320.json`, `e157-relaxed.json` (with their `runs-*.csv`, `reduce-*.txt`, `.log`) | E142's own footing (0.2414) and the arms |
| `scored.json`, `results.md`, `score.log` | every rule, every arm, every tile (`score_e157.py`, as registered), at reduction time (X1, X2, S1, S2 NOT SCORED) |
| `scored-e153.json`, `results-e153.md`, `score-e153.log`, `posthoc/score_with_e153.sh` | the same scorer with `--e153` on E153's committed reduction (`8e18eb67`): X1, X2, S1, S2 scored, every other verdict identical |
| `ccheck/ccheck-session.txt`, `ccheck/ccheck-session.json.gz` | every launch's C verdict (gunzip the JSON before passing it to `score_e157.py --ccheck`) |
| `aifoundry1-c1/e157/p157{10..13}/`, `aifoundry1-c1/e157-smoke-p15701/`, `aifoundry1-c1/e157-stoptest-p15702/` | the raw passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `c-log.jsonl.gz`, configs, manifests, the dumped tiles, hashes, `STOP.*` |
| `logs/` | the session's log, the queue, the session config reads, the box's preflight, binaries, `push-and-claim-times.txt` |
| `telemetry-max.json`, `posthoc/` | reported extremes; post hoc readings (§ Departures and post hoc) |
| `code.sha256` | every file of the code that ran and reduced |

To reproduce from a copy of the raw passes (`e157/`, `e157-smoke/`, `e157-stoptest/`, `logs/`): `PY=<python with numpy> nice -n 10 bash
tools/claims-v3/e157/collect_e157.sh <copy> [<E153's e153.json> [<its C-excluded tiles>]]`.
