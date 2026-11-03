# E142: blind pool 5 on aifoundry1 card 1 - M7 holds on the second card: power 0.17 / 0.15 / 0.25 W rms (fp32 / fp16 / int8), no resolved bias, 30 of 30 inside its bands, the die's rise to 0.14-0.17 °C; not resolved better than M6 or M5 (Q138, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 6**,
"a power model across kinds", and the first of its "After Q137, the next steps in order" (a refit "tested on a fifth pool written by someone
else, on a second card"). Mon 2 Nov 2026 (week 45), Q138. Pre-registered in `962748e7` (committed and pushed 20:48:24 PST), before the claim
(20:50:12) and the first launch (the smoke's first run, 20:51:11; the stop-path test before it launched nothing): [`tools/claims-v3/e142/README.md`](../../../../tools/claims-v3/e142/README.md). The model is
Q138(m)'s M7 ([`m7.json`](../2026-11-02-q138m-model/m7.json), `3a210f2b`, 19:21 PST); the pool, [blind pool 5](../../../../tools/claims-v3/kinds/blind5/README.md)
(36 tiles by a designer who never saw M7), and M7's, M6's and M5's frozen card-1 predictions
([`predictions-blind5-aifoundry1c1.json`](../../../../tools/claims-v3/kinds/blind5/predictions-blind5-aifoundry1c1.json)) were committed by
Q138(x) in `dac39d97` (20:24:02 PST), an ancestor of the registration. aifoundry1 card 1 at 600 MHz in every one of 26,259 samples;
`ettelem config` read 16 times (the session's start, 20:50:52, and end, 21:35:48, and both ends of the stop-path test, the smoke and every
pass): TDP 65 W, threshold 65 °C, 600 MHz, 499 mV in every read, never set. **Every device-management command sent was a read** (nine kinds,
two of them the PMIC voltage-register reads the owner's rule of 2 November 2026 allows); no write (`since_reset_ms` −1 in every sample). Card
session 20:50:51–21:35:48 PST, **44.9 of the 50 card-minutes allowed**: the stop-path test 14202, the smoke 14201 and five passes,
14210–14214 (507–525 s each), all kept.*

*Corrected after verification (a dated note, Mon 2 Nov 2026, about 22:30 PST; desk only: no card opened, no device command, nothing
re-run). An independent verifier re-derived every registered number and verdict from the committed raw passes and confirmed that every
command sent was a read. It found five faults, none of which changes a measured number, a rule, a prediction or a verdict. Each is corrected
in place, marked "corrected after verification, C<n>", and listed in
[§ Corrections after verification](#corrections-after-verification-mon-2-nov-2026) at the end; the numbers they quote are printed by
[`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt). The main one, C1: on these 30
tiles M6 is as unbiased as M7 and covers 29 of 30 inside narrower bands, so E142 does not show that M7's wider bands or its bias correction
gain anything over M6 on card 1. The 30-of-30 against 19-of-25 contrast this README drew compared two pools, two cards and two reduction
rules. The registration ([`tools/claims-v3/e142/`](../../../../tools/claims-v3/e142/README.md), `962748e7`) is frozen and unchanged.*

*Scored since (a dated note, Tue 3 Nov 2026, about 05:20 PST; desk only; the text below, written before E141's reduction existed, is unchanged): X1 and X2 were scored post hoc by Q139(c) in lab `22f8d1f9`, with the registered `score_e142.py --e141` on E141's committed reduction (`0531494f`). **X1 FAILS**: the median of card 1's float D over aifoundry3's, 21 tiles, 0.982 [0.980, 0.996] against M7's 0.9711. **X2 PASSES**: int8, 9 tiles, 0.981 [0.969, 1.005] against 0.9735. The float ratio moves about 0.95–0.99 over the two cards' leakage-corrected reduction arms (0.93–1.02 only with one card's leakage left uncorrected), so the card term cannot be tested to 1% until the footing is one ([Q139(c)](../2026-11-03-q139c-critic-checks/README.md), check (b)). Where this README says X1 and X2 are not scored (the results table, the before/after table, § 7, the registered-against-happened table and What it changes), it describes the record as this lane reduced it.*

**In plain words.** M7 is the lab's model that predicts how much power a matmul draws (watts over the same kernel on zeros) and how far the
die warms (in a 4.5 s run) from the numbers it multiplies. On this card it also carries a card term: card 1 draws 0.971 times what aifoundry3
does for the same floats. E142 ran 36 kinds of numbers that nobody fitted, written by an independent designer, on the second card, one
whose earlier runs M7 was fitted on: new kinds, not new hardware *(added after verification, C2)*. **M7
predicted their power to 0.17 W rms on fp32, 0.15 W on fp16 and 0.25 W on int8, with no resolved bias, and all 30 scored tiles fell inside
its 95% bands; it predicted the die's rise to 0.17, 0.16 and 0.14 °C, 29 of 30 inside.** Every registered rule that could be scored passed.
But M7 is not resolved better than M6, the model it replaced (the same rms over the 30 tiles, 0.211 W, the same near-zero bias, and 29 of 30
inside M6's narrower bands; corrected after verification, C1), or than M5 (0.254 W; the difference has an interval that includes zero). The
clearest gain over M5 is on the clock-gate tiles, which M5 under-predicts by 0.54–0.60 W, outside its bands, and M7 gets within 0.02 W
*(corrected after verification, C5: this said "the one visible gain")*. The power figures hold at the registered leakage slope (the frame of M7's card-1 training rows); at the session's own
fitted slope every D reads about 0.35 W lower and M7 would be too high.

## Results

**All five passes kept on the registered primary** (E78's `reduce_e78.py` unchanged through `reduce_e142.py`: leakage frozen at 0.2414 W/°C,
the board meter's launch-gap dips removed, E78's run and pass gates, card 1's 65/65 config gate): 280 runs, none failing a run gate; the tie
drifted +0.13, +0.23, −0.16, +0.38 and +0.26 W across the five passes (gate 0.60). Every tile has five kept passes
([`results.md`](results.md), [`scored.json`](scored.json); numbers printed by [`readme-numbers.py`](readme-numbers.py) →
[`readme-numbers.txt`](readme-numbers.txt)).

**1. The registered verdicts** (`scored.json` › `primary.rules`; arms › `arms.<name>.rules`):

| rule | quantity | set | reading | interval | verdict | arms where it differs |
|---|---|---|---|---|---|---|
| **E142-P1** | power, fp32 | 9 priority-1 tiles | rms **0.169 W** | 0.093–0.366 | **PASS** | leak 0 (FAIL) |
| **E142-P2** | power, fp16 | 8 | rms **0.149 W** | 0.085–0.294 | **PASS** | auto, dips kept, leak 0.3803, leak 0 (FAIL) |
| **E142-P3** | power, int8 | 7 | rms **0.251 W** | 0.115–0.416 | **PASS** | none |
| **E142-B1** | bias, floats | 17 | mean(measured − M7) **+0.050 W** | −0.090 to +0.105 | **PASS** | auto and 0.3803 (FAIL HIGH), 0.1994 and 0 (FAIL LOW) |
| **E142-B2** | bias, int8 | 7 | **−0.038 W** | −0.161 to +0.214 | **PASS** | auto (FAIL HIGH) |
| **E142-C1** | power coverage | 30 non-anchor tiles | **30 of 30** inside M7's 95% bands | ≥ 26 | **PASS** | leak 0 (FAIL, 21) |
| **E142-M1** | M7 against M6 | 24 priority-1 | rms(M7) − rms(M6) **−0.003 W** | −0.042 to +0.025 | **NOT RESOLVED** | none |
| **E142-M2** | M7 against M5 | 24 | **−0.054 W** | −0.148 to +0.024 | **NOT RESOLVED** | leak 0.3803 (BETTER) |
| **E142-H1** | die rise, fp32 | 9 | rms **0.167 °C** | 0.195–0.509 | **PASS** (below the interval: better than the nested score says) | none |
| **E142-H2** | die rise, fp16 | 8 | rms **0.162 °C** | 0.181–0.524 | **PASS** (below) | none |
| **E142-H3** | die rise, int8 | 7 | rms **0.139 °C** | 0.067–0.211 | **PASS** | none |
| **E142-H4** | heat coverage | 30 | **29 of 30** inside (`int8.a_word_flipflop` outside, 0.37 against 0.66 °C) | ≥ 26 | **PASS** | none |
| **E142-X1**, **X2** | the card term | — | — | — | **NOT SCORED**: E141 (pool 5 on aifoundry3) has not run; handed on with the code (`score_e142.py --e141`) *(scored post hoc since: X1 FAIL, X2 PASS; the dated note at the top)* | — |

The frozen expectation was P1–P3 PASS, B1 PASS or FAIL HIGH, B2 PASS, C1 PASS, M1 and M2 NOT RESOLVED, H1–H4 PASS: it was met. The
likeliest misses named in advance mostly were not misses: the wide-exponent gate tiles read +0.012, −0.131 and +0.018 W from M7, the fp16
pairs that cancel −0.247 and +0.155 W; of int8's whole-line flip-flops, `b_line_flipflop_nogate` read −0.001 W and **`b_line_zero_one`
−0.567 W, the largest priority-1 miss** (inside its ±0.67 W band). Arm-sensitive: P1, P2, B1, B2, C1 and M2 move at some leakage arm (§ 6);
no heat rule moves.

**2. Power, the three models on the same tiles** (measured − predicted, W; `scored.json` › `primary.reported`):

| | fp32 rms (bias), 9 | fp16 rms (bias), 8 | int8 rms (bias), 7 | 30 non-anchor rms (bias) | inside its own 95% band |
|---|---|---|---|---|---|
| **M7** (scored) | **0.169** (+0.067) | **0.149** (+0.030) | **0.251** (−0.038) | **0.211** (+0.001) | **30 of 30** |
| M6 (frozen, beside) | 0.162 (+0.106) | 0.170 (−0.034) | 0.248 (−0.051) | 0.211 (−0.003) | 29 of 30 (`int8.powerlaw_w`) |
| M5 (frozen, beside) | 0.228 (+0.045) | 0.249 (+0.104) | 0.259 (−0.080) | 0.254 (−0.010) | 27 of 30 (`fp32.wideexp48_bgate_alt`, `fp16.wideexp_bgate_alt`, `int8.powerlaw_w`) |

**Where they differ.** The two tiles that alternate the clock gate beside wide exponents: M5 under-predicts them by **+0.542 W**
(`fp32.wideexp48_bgate_alt`) and **+0.596 W** (`fp16.wideexp_bgate_alt`), outside its bands; M7 reads +0.012 and +0.018, M6 +0.004 and +0.003.
That is the gate's switching (M7's `gtr`, M6's per-flip gate terms), which M5 lacks, and the largest model disagreement Q138(x) had flagged
(0.55 and 0.59 W). On int8's whole-line flip-flop without the gate (`b_line_flipflop_nogate`), M7 reads −0.001 W where M6 and M5 read −0.27
and −0.26 W (M7's `b138`, E138's B-bit ratio): a 0.25–0.27 W gain on one tile, inside both older models' bands *(added after verification,
C5)*. M7's largest errors: `int8.powerlaw_w` −0.582 W (a priority-2 test; M6 −0.608 and M5 −0.593,
outside both their bands), `int8.b_line_zero_one` −0.567, `fp32.wideexp48_dense` +0.437, `fp32.anchor_randn` +0.386 (the pool's own random
anchor), `fp32.lowrank2_w` +0.273. By case (M7, non-anchor): the whole-line / whole-word flip-flops −0.254 W mean (rms 0.346, 3 tiles), the
seeded realistic weights −0.155 (rms 0.455, 2), every other case within ±0.09 W mean.

**3. Every tile** (W and °C; measured is the mean over five kept passes):

| tile | prio | D measured, W (sd, 5 passes) | M7 D [95%] | − M7 | − M6 | − M5 | die rise measured, °C | M7 rise [95%] | − M7 |
|---|---|---|---|---:|---:|---:|---:|---|---:|
| `fp32.e4m3grid_gelu_w` | 1 | 16.359 (0.160) | 16.249 [15.55, 16.95] | +0.110 | +0.116 | -0.039 | 2.080 | 2.08 [1.39, 2.76] | +0.003 |
| `fp32.exp_only_both` | 1 | 15.317 (0.204) | 15.338 [14.62, 16.06] | -0.020 | -0.075 | -0.197 | 2.060 | 1.97 [1.29, 2.66] | +0.088 |
| `fp32.gray_stream` | 1 | 16.111 (0.292) | 16.193 [15.50, 16.88] | -0.082 | +0.048 | -0.094 | 1.900 | 2.07 [1.39, 2.76] | -0.171 |
| `fp32.real_pythia_gelu_down` | 1 | 21.759 (0.151) | 21.646 [20.95, 22.34] | +0.113 | +0.215 | +0.035 | 2.890 | 2.70 [2.01, 3.38] | +0.192 |
| `fp32.real_pythia_ln1_q` | 1 | 21.500 (0.109) | 21.442 [20.75, 22.14] | +0.058 | +0.136 | -0.014 | 2.620 | 2.67 [1.99, 3.36] | -0.055 |
| `fp32.sorted_k` | 1 | 22.468 (0.088) | 22.358 [21.66, 23.06] | +0.110 | +0.123 | +0.081 | 2.936 | 2.78 [2.09, 3.47] | +0.156 |
| `fp32.wideexp48_bgate_alt` | 1 | 14.701 (0.119) | 14.688 [13.97, 15.41] | +0.012 | +0.004 | +0.542 (outside) | 2.010 | 1.90 [1.21, 2.58] | +0.112 |
| `fp32.wideexp48_bgate_kblk` | 1 | 12.816 (0.118) | 12.947 [12.26, 13.64] | -0.131 | +0.015 | -0.192 | 1.970 | 1.70 [1.01, 2.38] | +0.273 |
| `fp32.wideexp48_dense` | 1 | 25.353 (0.204) | 24.916 [24.20, 25.63] | +0.437 | +0.368 | +0.286 | 3.324 | 3.08 [2.39, 3.76] | +0.249 |
| `fp32.b_exp_busy_a_const` | 2 | 15.114 (0.136) | 15.136 [14.43, 15.84] | -0.022 | +0.058 | -0.176 | 2.041 | 1.95 [1.26, 2.63] | +0.092 |
| `fp32.block_sparse_k4` | 2 | 12.245 (0.117) | 12.416 [11.73, 13.10] | -0.172 | -0.005 | -0.199 | 1.540 | 1.64 [0.95, 2.32] | -0.096 |
| `fp32.lowrank2_w` | 2 | 24.070 (0.168) | 23.797 [23.10, 24.50] | +0.273 | +0.225 | +0.184 | 3.060 | 2.95 [2.26, 3.63] | +0.114 |
| `fp32.anchor_randn` | 2 anchor | 24.166 (0.108) | 23.779 [23.08, 24.48] | +0.386 | +0.336 | +0.306 | 3.194 | 2.94 [2.26, 3.63] | +0.250 |
| `fp32.anchor_zeros` | 2 anchor | -0.031 (0.120) | 0.000 [-0.68, 0.68] | -0.031 | -0.031 | -0.031 | 0.000 | 0.21 [-0.48, 0.89] | -0.207 |
| `fp16.pair_cancel_asign` | 1 | 16.093 (0.172) | 16.339 [15.73, 16.95] | -0.247 | -0.367 | -0.193 | 2.190 | 2.09 [1.39, 2.78] | +0.104 |
| `fp16.pair_nearcancel` | 1 | 21.322 (0.175) | 21.167 [20.56, 21.78] | +0.155 | +0.077 | +0.164 | 2.700 | 2.64 [1.95, 3.33] | +0.058 |
| `fp16.real_pythia_ln2_up` | 1 | 21.591 (0.177) | 21.450 [20.84, 22.06] | +0.141 | +0.076 | +0.139 | 2.750 | 2.67 [1.98, 3.37] | +0.076 |
| `fp16.real_pythia_qk` | 1 | 20.568 (0.047) | 20.491 [19.88, 21.10] | +0.076 | +0.053 | +0.077 | 2.660 | 2.56 [1.87, 3.25] | +0.096 |
| `fp16.real_pythia_softmax_v` | 1 | 16.700 (0.088) | 16.851 [16.25, 17.46] | -0.151 | -0.083 | -0.146 | 2.220 | 2.15 [1.45, 2.84] | +0.075 |
| `fp16.sparse24_aligned` | 1 | 12.459 (0.070) | 12.417 [11.80, 13.03] | +0.042 | -0.209 | +0.024 | 1.978 | 1.63 [0.94, 2.33] | +0.344 |
| `fp16.sparse24_straddled` | 1 | 21.272 (0.140) | 21.065 [20.45, 21.68] | +0.206 | +0.177 | +0.175 | 2.738 | 2.63 [1.94, 3.32] | +0.108 |
| `fp16.wideexp_bgate_alt` | 1 | 13.088 (0.085) | 13.069 [12.43, 13.71] | +0.018 | +0.003 | +0.596 (outside) | 1.922 | 1.71 [1.02, 2.40] | +0.212 |
| `fp16.exp_only` | 2 | 15.822 (0.077) | 15.935 [15.31, 16.56] | -0.114 | -0.120 | -0.199 | 2.210 | 2.04 [1.35, 2.73] | +0.171 |
| `fp16.anchor_randn` | 2 anchor | 21.364 (0.113) | 21.240 [20.63, 21.85] | +0.125 | +0.052 | +0.128 | 2.790 | 2.65 [1.96, 3.34] | +0.140 |
| `fp16.anchor_zeros` | 2 anchor | -0.015 (0.153) | 0.000 [-0.60, 0.60] | -0.015 | -0.015 | -0.015 | -0.090 | 0.20 [-0.49, 0.90] | -0.295 |
| `int8.a_word_flipflop` | 1 | 3.236 (0.159) | 3.429 [2.79, 4.07] | -0.193 | -0.105 | -0.281 | 0.370 | 0.66 [0.39, 0.94] | -0.293 **(outside)** |
| `int8.b_line_flipflop_nogate` | 1 | 6.176 (0.177) | 6.177 [5.49, 6.87] | -0.001 | -0.266 | -0.255 | 0.990 | 0.98 [0.70, 1.25] | +0.011 |
| `int8.b_line_zero_one` | 1 | 3.287 (0.183) | 3.854 [3.18, 4.53] | -0.567 | -0.512 | -0.494 | 0.800 | 0.71 [0.44, 0.99] | +0.088 |
| `int8.gray_a` | 1 | 4.261 (0.135) | 4.251 [3.55, 4.95] | +0.009 | +0.014 | -0.026 | 0.600 | 0.76 [0.48, 1.03] | -0.158 |
| `int8.real_pythia_w8a8_down` | 1 | 6.225 (0.227) | 6.025 [5.38, 6.67] | +0.200 | +0.167 | +0.174 | 0.850 | 0.96 [0.69, 1.24] | -0.112 |
| `int8.real_pythia_w8a8_up` | 1 | 6.130 (0.175) | 5.980 [5.33, 6.63] | +0.149 | +0.144 | +0.131 | 1.000 | 0.96 [0.68, 1.23] | +0.043 |
| `int8.sorted_k` | 1 | 5.995 (0.168) | 5.855 [5.19, 6.52] | +0.140 | +0.198 | +0.188 | 0.989 | 0.94 [0.67, 1.22] | +0.047 |
| `int8.block_sparse_a` | 2 | 4.248 (0.169) | 4.202 [3.56, 4.84] | +0.046 | +0.029 | +0.000 | 0.800 | 0.75 [0.48, 1.03] | +0.048 |
| `int8.powerlaw_w` | 2 | 5.625 (0.182) | 6.207 [5.55, 6.86] | -0.582 | -0.608 (outside) | -0.593 (outside) | 1.000 | 0.98 [0.71, 1.26] | +0.017 |
| `int8.anchor_full` | 2 anchor | 6.929 (0.169) | 6.811 [6.16, 7.46] | +0.118 | +0.154 | +0.163 | 1.130 | 1.05 [0.78, 1.33] | +0.078 |
| `int8.anchor_zeros` | 2 anchor | 0.034 (0.251) | 0.000 [-0.63, 0.63] | +0.034 | +0.034 | +0.034 | 0.010 | 0.27 [-0.01, 0.54] | -0.258 |

**4. Heat** (measured − M7, °C): bias +0.094 (fp32), +0.134 (fp16), −0.053 (int8) on the priority-1 tiles; the rise per board W through the
origin over the 30 tiles is **0.1197 °C/W against M7's 0.1151** on card 1 (`reported_rise_per_board_w`). The one tile outside its band,
`int8.a_word_flipflop`, rose 0.37 °C against 0.66 predicted. The die reads in whole degrees, so a 4.5 s int8 rise lands near 0.5 or 1.0 °C;
that floor is inside M7's reference. The pool's zeros tiles rose 0.00 / −0.09 / 0.01 °C against M7's 0.21 / 0.21 / 0.27 °C (the zeros' S
times 0.115 °C/W: a constant the readout cannot see over 4.5 s; anchors are not in the scored sets). **Heat at the measured run length**
(registered as reported): see § Post hoc, P2 — the registered formula gives three int8 tiles a 7.1–7.2 s "run" that spans a heater launch.

**5. What it does to predicting power and heat** (the before/after the owner's goal asks for):

| | before: M7's nested leave-one-kind-out on card-1 rows (`loko-m7.json`) | after: blind pool 5, card 1, primary | M6 on the same tiles (frozen, beside; column added after verification, C1) | blind record before M7 (E140, pool 4, aifoundry3: another pool, card and reduction rule) |
|---|---:|---:|---:|---:|
| power, fp32 | 0.214 W rms | **0.169 W** (bias +0.067) | 0.162 W (+0.106) | M6 0.50 W (bias −0.38), M5 0.44 |
| power, fp16 | 0.188 W | **0.149 W** (+0.030) | 0.170 (−0.034) | M6 0.25, M5 0.15 |
| power, int8 | 0.255 W | **0.251 W** (−0.038) | 0.248 (−0.051) | M6 0.37, M5 0.37 |
| power, the 30 non-anchor tiles | — | 0.211 W (+0.001) | 0.211 W (−0.003) | — |
| power, 95% bands | 47 of 50 pool rows (a calibration, not a test) | **30 of 30** (100%); mean half-width 0.70 / 0.62 / 0.66 W | 29 of 30 (97%); 0.43 / 0.39 / 0.56 W | M6 19 of 25 (76%; the meter's dips kept, two of four passes; 21 of 25 with the dips removed) |
| heat, fp32 / fp16 / int8 | 0.352 / 0.355 / 0.141 °C | **0.167 / 0.162 / 0.139 °C** | 0.163 / 0.147 / 0.138 °C | M6 0.18 / 0.27 / 0.21 °C |
| heat, 95% bands | — | **29 of 30** | 30 of 30 | M6 24 of 25 |
| the card term (0.9711 floats, 0.9735 int8) | 0.175 W rms on 92 paired float kinds | not separable without E141 (X1/X2 handed on) *(scored post hoc since: X1 FAIL, X2 PASS; the dated note at the top)* | — | — |

So: **on the second card, M7's stated error bars can be quoted for new kinds** (power within its nested rms per format, no resolved bias,
bands that covered every tile; heat about half its card-1 nested rms on the floats), with two qualifications. (i) M7 is not shown better than
M6 on these tiles, nor than M5 beyond the gate tiles. On pool 5 and card 1 M7 and M6 cannot be told apart in rms (0.211 against 0.211 W over
the 30 tiles; M1 −0.003 W [−0.042, +0.025]), in bias (+0.001 against −0.003 W) or in coverage (M7 30 of 30 inside bands 1.6 times wider on
the floats and 1.2 times on int8; M6 29 of 30, its one miss `int8.powerlaw_w` at 1.09 of its half-width). Heat reads the same (M6 0.163 /
0.147 / 0.138 °C, 30 of 30). M6's pool-4 miscalibration did not recur here, so E142 does not show that M7's wider bands or its bias
correction were needed on card 1. The pool-4 figures differ from this primary in pool, card and reduction rule: E140's primary kept the
meter's dips, fitted its leakage (0.286 W/°C) and kept two of four passes (21 of 25 inside and a −0.15 W bias with the dips removed), where
E142's removes the dips, freezes the leakage at 0.2414 W/°C and kept five of five. E141, the same pool on aifoundry3, is the test that
can separate them. It was committed at 22:18 PST (`0531494f`), while this correction was written, and had not been verified; its README
reports M6's bands covering 22 of 30 there, against M7's 28 *(corrected after verification, C1: this said "its gain is the bands (30 of 30
against M6's 19 of 25 on pool 4) and the absence of E140's one-sided bias, not a smaller rms")*. (ii) Card 1's D depends on the leakage slope at the 0.3–0.4 W level (§ 6). The bands may be
conservative here (30 of 30 where 28.5 is expected): rule B sized k on the pools' adversarial rows (3.18 floats, 2.48 int8).

**6. The footing and the leakage slope** (reported). The pool's own anchors: `fp32.anchor_randn` 24.166 W against M7's 23.779 (+0.386,
inside), `fp16.anchor_randn` 21.364 (+0.125), `int8.anchor_full` 6.929 (+0.118); its zeros tiles read −0.031 / −0.015 / +0.034 W over E78's
built-in zeros (a zeros tile and the built-in zeros cost the same within 0.04 W). E78's own anchors this session: `fp32.randn` 24.060 W,
`fp16.randn` 21.533, `int8.full` 6.937, against E131's 23.963, 21.467 and 6.891 on this card this morning (E131 `e131.json`): the session sits
0.05–0.10 W above E131. **The leakage slope moves every D**: the primary is frozen at 0.2414 W/°C, E82's own slope on this card and the
registered primary of 11 of the 13 card-1 experiments in M7's rows (E82 by its own fit; E93, E94, E102, E103, E104, E106, E108, E128, E131,
E137; E88 and E91 used their own `auto` slopes, 0.315 and 0.422). The session's own fitted slope (`auto`) is 0.408 W/°C; there M7 reads too high by 0.34 W (fp32), 0.38
(fp16) and 0.18 (int8) and B1 FAILS HIGH, as at 0.3803; at 0.1994 and 0 W/°C it reads too low and B1 FAILS LOW. With the dips kept, E78's
pass gates set aside three of five passes (the tie drifting −0.705 and +1.034 W, `fp32.randn` spanning 1.638 W: the meter dips E82 A2 removes)
and the two kept passes give fp16 0.315 W (P2 FAIL). With the anchor and tie gates relaxed, nothing changes (no pass was set aside).

**7. The card term** (X1, X2): NOT SCORED *(scored post hoc since, Tue 3 Nov 2026: X1 FAIL, X2 PASS; the dated note at the top)*. E141, the same pool on aifoundry3 card 0, had not run when this lane reduced. When E141's committed
reduction exists, `PY=<python with numpy> bash tools/claims-v3/e142/collect_e142.sh <raw root> <E141's reduction json>` (or
`score_e142.py --e142 e142.json --e141 <its reduction>`) scores them as registered: the median D(card 1) / D(aifoundry3) over the float tiles
with D ≥ 5 W (int8 ≥ 1 W) against 0.9711 (0.9735), with a bootstrap interval over tiles. Without it, card 1's blind error above is M7's
aifoundry3 footing and the card term together.

## Registered against what happened

| | registered | happened |
|---|---|---|
| passes | 14210–14213, 14214 if it fits (2,940 s from T0); at least 2 kept | **five ran** (525, 522, 522, 516, 507 s), **all kept**; the fifth started at T0 + 2,180 s with 525 s projected |
| card time | ≤ 50 min, first device access to the closing read | **44.9 min** (20:50:51–21:35:48 PST) |
| stop-path test | the guard's die and board stops and the in-run watcher each fire on a live sample (≤ 2.0 s old), no launch | **PASS**: 0.033, 0.027 and 0.054 s old (`logs/session.log`, `aifoundry1-c1/e142-stoptest-p14202/`) |
| smoke gate | records ok, cycles per op within 0.5%, 600 MHz, config 65 W / 65 °C / 600 MHz, dumped pool tiles equal their sha256, `since_reset_ms` −1, board below the stop | **PASS** (every item; board 29.71–58.49 W, shire mean 51–57 °C) |
| stops | board ≥ 66 W or a minion-shire field ≥ 72 °C (main path and in-run watcher); `--max-c 72` | **no stop**: board at most 62.09 W (p99.9 61.67–61.89 per pass), shire mean at most 63 °C (the field named `pmic` holds the same shire average, 63 °C: it is not the PMIC's temperature), the shire field's high-water latch 65 °C throughout (`telemetry-max.json`). No telemetry field reads the PMIC's own temperature, which its 75 °C over-temperature alarm compares, so that margin is not measured; the guard against over-temperature was the 72 °C die stop *(corrected after verification, C3: this said "PMIC 63 °C")* |
| config reads | 65 W / 65 °C / 600 MHz | **all 16 reads** 65 W, 65 °C, 600 MHz, 499 mV; `power_state` read 1 (managed) in 13 and 3 (low power) in 3 (read only; nothing set) |
| expectation | P1–P3, B2, C1, H1–H4 PASS; B1 PASS or FAIL HIGH; M1, M2 NOT RESOLVED | **met** |
| X1, X2 | scored if E141's reduction exists | NOT SCORED (E141 not yet run) *(scored post hoc since: X1 FAIL, X2 PASS; the dated note at the top)* |

## Departures and post hoc

**Departures** (none touches a registered rule, prediction or reading):
- **D1** (during the session, labelled): at 21:00:51 PST, after pass 14210 had ended on the box, the lane copied that pass to the Intel and ran
  `reduce_e142.py` on it alone, then `score_e142.py` on a copy holding that pass twice, to test the pipeline on real output before the session
  ended. Only the return codes and key names were read, and the reducer's last three log lines were printed (two int8 zeros rows). The
  queue's passes were fixed by the budget rule, which never reads a reduction; no pass was added or dropped.
- **D2**: the collector's Python on the Intel was a virtual environment with numpy 2.5.3 (the box runs numpy 1.26.4); the reduction's
  arithmetic is numpy's mean, polyfit and interpolation.
- **D3**: the first collection (21:36:38) read the passes from the lane's scratch copy, so the reductions' `dirs` carried a Mac path; it was
  redone at 21:40:10 from a repository-relative copy (`build/e142-raw/`), with the same verdicts, and only the second is committed.

**Post hoc** (written after the registered scoring was read; never a verdict; [`tools/claims-v3/e142/posthoc_e142.py`](../../../../tools/claims-v3/e142/posthoc_e142.py) →
[`posthoc/runlength-posthoc.json`](posthoc/runlength-posthoc.json)):
- **P1, the leakage slope** is § 6 above (the registered arms, read after the fact).
- **P2, heat at the measured run length.** The registered reported arm reads each tile's run length as `fit_m6.heat_rows` does (the next
  run's `prev_end_ms` less this run's `t0_ms`). For a cool int8 tile the next device process is often a heater launch, so three int8 tiles
  (`a_word_flipflop`, `b_line_zero_one`, `anchor_zeros`) read 7.1–7.2 s, and the arm's int8 rms is 1.29 °C: an artefact of the formula, not of
  the model. M7's own heat rows leave such items out (`HEAT_TRUN_MAX`, 5.0 s). With that rule, H2's run-length term at the measured lengths
  (median 4.46 / 4.47 / 4.39 s) reads **0.131 / 0.110 / 0.176 °C** (fp32 / fp16 / int8), 28 of 28 inside, against 0.167 / 0.162 / 0.139 °C at
  the frozen 4.5 s: better on the floats, worse on int8. Read from the run marks instead (each run's own process time, 4.52–4.60 s), the same
  term moves the other way (0.438 / 0.454 / 0.138 °C): **the ST term is not a run-length law** (Q138(m) C8: fitted over 0.14 s of run length),
  so the frozen 4.5 s prediction is the one to quote.

## Device commands sent

As registered (the registration's § Device commands sent, classified from et-platform `836a4ab`): `ettelem config` at the session's ends and
both ends of the stop-path test, the smoke and every pass (16 reads), `ettelem sample --seconds --every-ms 100` through E128's guard in every
block: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**,
GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all READs**, the two in bold PMIC voltage-register
reads (allowed). Never sent: the statistics reset (`since_reset_ms` −1 in all 26,259 samples), any SET_*, the firmware-revisions query, a
residency read, `dev_mngt_service` (the drain was replaced by a refusal and no refusal line appears in the logs). The host program
(`sparsity_host` `e0fbecce…`, the heater the same binary) opens the ops node only. The checker on the box before any device opened:
**GO**, 32 send sites, 0 disallowed, with the reviewed `lib.sh:154` exception ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt));
NO-GO without it (the registration's `dmcmd-audit-noexcept.txt`). `check_e142.py` on the box: HARNESS OK, 59 files (E78's card code, E128's
guard, Q136(w)'s checker and table, the host source, E142's card files, the pool and its 36 tiles, the two binaries).

**The `ettelem` binary predates the source its sends were classified from** *(added after verification, C4)*. The table classifies
`ettelem` from `tools/ettelem/ettelem.cpp` at `efa3e8cd` (4 Oct, sha256 `a6cf931b…`). The binary that ran, `8008f96f…`
([`logs/binaries.sha256`](logs/binaries.sha256)), was already on aifoundry1 on 28 Sep
([`2026-09-28-heat-placement/…/p5501/binaries.json`](../2026-09-28-heat-placement/raw/aifoundry1-c1/hp/p5501/binaries.json)), so it was
built from an earlier revision. It writes `since_reset_ms`, which first appears at `4845a60e` (23 Sep). Every revision from `4845a60e` to
`efa3e8cd` requests the same six reads in `sample` and the same five in `config`, sends the statistics reset only when `resetMs > 0`
(both calls in `sample` guarded), and defaults `resetMs` to 0. `git diff 4845a60e efa3e8cd -- tools/ettelem/ettelem.cpp` changes only comments and usage
text, signal handling, and the `temp` subcommand with its `--if-free` lock probe, which E128's guard refuses. So the classification
holds. The residual stays: no running binary is hashed against its source (Q136(w)'s
[What it does not settle](../2026-11-02-q136w-write-audit/README.md): "The running binaries are unhashed").

## Card and post

`et-who` at the session's start (20:50:51) and end (21:35:48): no process held an ET-SoC-1 device node or card lock. Never two of our sessions on aifoundry1 (card 0 unused). The day's one post (message 1566837317765963987) read at 20:49:54
`<ai> **Claude says:** using aifoundry3 for 1 h, until ~21:14 PST [doc](…)`; at 20:50:12 PST it was rewritten under the discord lock with
`EXPECT_TEXT` (dry run, then save) to add this card's clause, `using aifoundry1 card 1 for 1.5 h, until ~22:20 PST [doc](…)`; at 21:36:18,
with aifoundry3 still held, this card's clause was dropped and the aifoundry3 clause kept word for word (the plan's cached source still named
an aifoundry2 clause the edit box no longer held, so `EXPECT_TEXT` refused once and the text was rebuilt from the edit box). The full texts:
[`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt).

## What it changes

- **Item 6 on the kinds page**: answered for the second card. M7's power and heat predictions, frozen before the run, held on 36 blind
  tiles on aifoundry1 card 1 (power 0.17 / 0.15 / 0.25 W rms, no resolved bias, 30 of 30 inside its bands; heat 0.17 / 0.16 / 0.14 °C,
  29 of 30). Still open there: the same pool on aifoundry3 (E141) and on aifoundry2 under its governor (E143), and the card term itself (X1,
  X2, once E141 exists; scored post hoc since: X1 FAIL, X2 PASS, the dated note at the top).
- **The model**: no gain of M7 over M6 is resolved on these tiles, in rms (−0.003 W), bias (+0.001 against −0.003 W) or coverage (30 and 29
  of 30, M6's bands the narrower) *(corrected after verification, C1)*, nor over M5 (−0.054 W, interval through zero). The clearest term the
  card shows at work is the clock gate's switching (M5's +0.54 / +0.60 W misses, outside its bands); M7's `b138` shows a 0.25–0.27 W gain on
  one int8 tile, inside M6's and M5's bands *(corrected after verification, C5: this said "the one term the card shows doing work")*.
  `int8.b_line_zero_one` and `int8.powerlaw_w` (−0.57, −0.58 W,
  every model too high) are the next int8 cases to look at.
- **The method**: on card 1 the leakage slope is a ±0.35 W systematic on D (frozen 0.2414 against the session's 0.408 W/°C); a model scored on
  card 1 must name its slope, as here. The in-run watcher and the stop-path test (live samples, 0.03–0.05 s old) are the stops a kinds pass
  should carry on this card.
- **Records to add** (integration lanes): 03-experiments (E142), 05-claims (item 6 on the second card), 14-card-behaviour (the session's
  fitted leakage slope 0.408 W/°C on card 1 again; the post-hoc run-length artefact of the heater in `fit_m6.heat_rows`' formula). Added
  after verification: 05-claims, that E142 shows no M7 gain over M6 in rms, bias or coverage (C1); 14-card-behaviour, that the board's
  62.09 W is above the highest card-1 reading that file gives (61.30 W), still 13 W under the firmware's 75 W over-power set point, so card
  1's alarm stays untested, and that the PMIC's own temperature was again unread (C3).

## Files

- The registration and code: `tools/claims-v3/e142/` (`README.md`, `predictions-e142.json`, the box files, `reduce_e142.py`,
  `collect_e142.sh`, `score_e142.py`, `selftest_e142.py`, `telemetry_max_e142.py`, `posthoc_e142.py`).
- Here: `e142.json`, `runs.csv`, `reduce.txt`, `reduce.log` (the primary); `e142-auto.json`, `e142-dipskept.json`, `e142-leak0.1994.json`,
  `e142-leak0.3803.json`, `e142-leak0.json`, `e142-relaxed.json` and their `runs-*.csv`, `reduce-*.{txt,log}` (the arms); `scored.json`,
  `results.md`, `score.log` (the rules); `telemetry-max.json`; `readme-numbers.py`, `readme-numbers.txt`; `posthoc/runlength-posthoc.json`;
  `code.sha256`; added after verification, `corrections-numbers.py` and `corrections-numbers.txt` (the numbers C1–C5 quote).
- Raw: `aifoundry1-c1/e142/p14210` … `p14214` (each pass's runs, marks, plan, telemetry, configs, manifest, run log, code and binaries'
  sha256), `aifoundry1-c1/e142-smoke-p14201/`, `aifoundry1-c1/e142-stoptest-p14202/`; `logs/` (the box's session log, queue log,
  preflight, binaries, the session's config reads, the box setup and dry runs, the order of events).

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier re-derived E142 from the committed files. The reductions (the primary and six arms) and the scoring, rerun from the
raw passes, are identical on every numeric leaf (numpy 2.5.3; with numpy 1.26.4 the largest difference is 1e-14). The blind protocol's order,
isolation and byte identity hold, the box ran the registered code, no registered file changed after `962748e7`, and every device command
sent was a read. Its five faults are corrected above, in place. None changes a measured number, a rule, a prediction or a verdict. The
numbers below are printed by [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt),
from this directory's `scored.json` and `telemetry-max.json`, the registration's `predictions-e142.json`, E140's `scored.json` and
`scored-nodips.json`, `m7.json`, 14-card-behaviour.md and git.

- **C1 (major): M7 against M6.** § 5 (i) said M7's gain over M6 "is the bands (30 of 30 against M6's 19 of 25 on pool 4) and the absence of
  E140's one-sided bias, not a smaller rms". E142's own same-tile comparison does not show that. On the 30 non-anchor tiles, M7 and M6 read:
  - the same rms: 0.211 and 0.211 W (M1 −0.003 W [−0.042, +0.025]);
  - the same near-zero bias: +0.001 and −0.003 W (`scored.json` › `primary.reported.<model>.power_all_nonanchor`);
  - coverage that passes for both: M7 30 of 30, M6 29 of 30 (the rule needs 26). M6's one miss is `int8.powerlaw_w`, at 1.09 of its
    half-width; M7's largest error is 0.89 of its own.

  M7's bands are the wider ones: 1.64, 1.58 and 1.19 times M6's on fp32, fp16 and int8 (mean 95% half-widths 0.70 / 0.62 / 0.66 W against
  0.43 / 0.39 / 0.56; `predictions-e142.json` › `tiles.*.<model>.D_95`). Heat reads the same: M6 0.163 / 0.147 / 0.138 °C with 30 of 30
  inside, against M7's 0.167 / 0.162 / 0.139 with 29 of 30. M6's pool-4 miscalibration did not recur here.

  The 19 of 25 is E140's primary: pool 4 on aifoundry3, with the meter's dips kept, its leakage fitted (`auto`, 0.286 W/°C) and two of four
  passes kept. With the dips removed it reads 21 of 25 and a −0.152 W bias (E140 `scored-nodips.json`). E142's primary removes the dips,
  freezes the leakage at 0.2414 W/°C and kept five of five passes. So that contrast mixed pool, card and reduction rule, and the test that
  can separate them is E141, the same pool on aifoundry3. E141's result was committed at 22:18 PST (`0531494f`), while this was written, and
  had not been verified. Its README reports M6's bands covering 22 of 30 on that card, against M7's 28 (its § 2). Comparing the two cards is
  left to the integration lanes, once E141 is verified.

  Corrected in place: the plain words, § 5's table (a column for M6 on the same tiles; the E140 column labelled with its rules), § 5 (i)
  and § What it changes. In the lane's result, the prediction effect and the third blog point are corrected the same way.
- **C2 (minor): "a second chip", "about 1% of a 20 W load".** The lane's first blog point read as a test on unseen hardware. M7 was fitted
  on this card's rows: from 13 card-1 experiments (§ 6), with its card-1 scale 0.9711 for the floats and 0.9735 for int8 (`m7.json` ›
  `families.*.card1_scale_by_format`). So E142 tests new kinds, not new hardware. And 1% holds for the floats only:
  - fp32 0.169 W rms on 12.8–25.4 W, 0.9% of the mean D;
  - fp16 0.149 W on 12.5–21.6 W, 0.8%;
  - int8 0.251 W on 3.2–6.2 W, 5.0% of the mean D (4.0–7.8% of the largest and smallest).

  The plain words now say "new kinds, not new hardware". The blog point is corrected in the lane's result.
- **C3 (minor): "PMIC 63 °C".** The stops row reported the telemetry field named `pmic` as the PMIC's temperature. That field is the minion
  shires' PVT average (14-card-behaviour.md, the `temp_c.pmic` row; E127 C5, E128 C6). Here it equals the shire mean's maximum, 63 °C, in
  every block (`telemetry-max.json` › `blocks.*.pmic_c_max`, `shire_mean_c_max`). No telemetry field reads the PMIC's own temperature, which
  its 75 °C over-temperature alarm compares, so the margin to that alarm is not measured. The guard against over-temperature was the
  registered 72 °C die stop (the hottest-shire latch read 65 °C throughout). Corrected in the stops row.

  For the records, too: the board's 62.09 W is above the highest card-1 reading 14-card-behaviour.md gives (61.30 W), still 13 W under
  the firmware's 75 W over-power set point, so card 1's alarm stays untested.
- **C4 (minor): the `ettelem` binary.** § Device commands sent did not say that the binary that ran (`8008f96f…`, on the box by 28 Sep)
  predates the source its sends were classified from (`efa3e8cd`, 4 Oct, sha256 `a6cf931b…`). The classification holds for every source
  revision the binary can come from (`4845a60e` onward: the same reads, the reset only when `resetMs > 0`, `resetMs` 0 by default).
  The residual, that no running binary is hashed against its source, is Q136(w)'s. Added to § Device commands sent.
- **C5 (minor): "the one term".** The plain words called the gate tiles "the one visible gain over M5", and § What it changes and the lane's
  result called gate switching "the one term the card shows doing work". But § 2 also shows M7's `b138` moving `int8.b_line_flipflop_nogate`
  from −0.266 and −0.255 W (M6, M5) to −0.001 W, inside both older models' bands. Corrected: the clearest term at work is gate switching
  (outside M5's bands), and M7's `b138` shows a 0.25–0.27 W gain on one int8 tile, inside M6's and M5's bands.
