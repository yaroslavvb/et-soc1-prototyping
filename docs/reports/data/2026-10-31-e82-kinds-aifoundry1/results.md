# E82 results — aifoundry1 card 1, 600 MHz, 498.7 mV (E78's rules, scored by score_e78.py unchanged)

Passes kept [8211, 8212, 8213, 8214, 8215] (5); runs kept 320 of 450; leakage slope 0.2414 W/°C (auto); idle level 33.105 W; cycles per op {'fp32': 546.001, 'fp16': 546.001, 'int8': 318.0}.

Passes set aside by the registered gates: [{'pass': 8210, 'why': ['fp16.randn spans 1.246 W']}, {'pass': 8216, 'why': ['fp32.randn spans 1.072 W', 'int8.full spans 1.034 W']}]

**Tally (registered rules, primary leak slope):** 23 pass, 4 fail, 0 inconclusive, 0 not scored.

- arm `leak0.545`: {'PASS': 21, 'FAIL': 5, 'INCONCLUSIVE': 1, 'NOT SCORED': 0}
- arm `leak0.3803`: {'PASS': 21, 'FAIL': 5, 'INCONCLUSIVE': 1, 'NOT SCORED': 0}
- arm `leak0`: {'PASS': 23, 'FAIL': 3, 'INCONCLUSIVE': 1, 'NOT SCORED': 0}

## The matrix

D = switching power over the type's own zeros (paired, interpolated zeros); S = over the idle bracket; pJ from S at the measured op rate. 95% intervals from the between-pass scatter.

### fp32

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 2 | 0.000 | 82244 | 24.059 | 0.279 | 24.059 | 25.873 | 0.270 | 23084 | 5.636 | 2.818 | 3.40 | 20.163 | 5 |
| randn | 1 | 0.000 | 82214 | 23.987 | 0.106 | 23.987 | 25.819 | 0.167 | 23034 | 5.623 | 2.812 | 3.41 | 20.029 | 5 |
| randn_large | 2 | 0.000 | 84896 | 23.974 | 0.356 | 23.974 | 25.762 | 0.184 | 22987 | 5.612 | 2.806 | 3.35 | 19.990 | 5 |
| randn_sorted | 1 | 0.000 | 60856 | 22.561 | 0.818 | 22.561 | 24.482 | 0.831 | 21834 | 5.331 | 2.665 | 3.14 | 19.009 | 5 |
| uniform01 | 2 | 0.000 | 77842 | 22.031 | 0.088 | 22.031 | 23.848 | 0.140 | 21277 | 5.195 | 2.597 | 3.08 | 18.327 | 5 |
| fp16grid | 2 | 0.000 | 43136 | 19.223 | 0.177 | 19.223 | 21.020 | 0.156 | 18753 | 4.578 | 2.289 | 2.74 | 16.209 | 4 |
| bf16trunc | 1 | 0.000 | 34980 | 17.623 | 0.112 | 17.623 | 19.462 | 0.138 | 17358 | 4.238 | 2.119 | 2.53 | 14.967 | 5 |
| pow2 | 1 | 0.000 | 25414 | 13.708 | 0.044 | 13.708 | 15.519 | 0.283 | 13844 | 3.380 | 1.690 | 2.05 | 11.789 | 5 |
| smallint | 1 | 0.118 | 19806 | 13.659 | 0.103 | 13.659 | 15.514 | 0.048 | 13843 | 3.380 | 1.690 | 2.03 | 11.751 | 5 |
| nn_like | 1 | 0.508 | 80426 | 12.735 | 0.185 | 12.735 | 14.582 | 0.218 | 13006 | 3.175 | 1.588 | 1.99 | 10.976 | 5 |
| pi | 2 | 0.000 | 0 | 8.209 | 0.203 | 8.209 | 9.943 | 0.107 | 8871 | 2.166 | 1.083 | 1.44 | 7.135 | 5 |
| neg_ones | 2 | 0.000 | 0 | 7.980 | 0.195 | 7.980 | 9.913 | 0.068 | 8844 | 2.159 | 1.080 | 1.29 | 7.006 | 5 |
| ones | 1 | 0.000 | 0 | 7.918 | 0.427 | 7.918 | 9.698 | 0.553 | 8651 | 2.112 | 1.056 | 1.37 | 7.040 | 5 |
| sparse50 | 1 | 0.774 | 74550 | 6.760 | 0.464 | 6.760 | 8.625 | 0.465 | 7694 | 1.878 | 0.939 | 1.11 | 6.093 | 5 |
| a_zeros_b_randn | 2 | 1.000 | 55798 | 0.723 | 0.091 | 0.723 | 2.684 | 0.060 | 2394 | 0.585 | 0.292 | 0.37 | 0.690 | 5 |
| a_randn_b_zeros | 1 | 1.000 | 27920 | 0.631 | 0.051 | 0.631 | 2.494 | 0.182 | 2226 | 0.543 | 0.272 | 0.35 | 0.565 | 5 |
| sparse90 | 1 | 0.992 | 17780 | 0.620 | 0.164 | 0.620 | 2.456 | 0.130 | 2192 | 0.535 | 0.268 | 0.34 | 0.565 | 4 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.000 | 1.841 | 0.113 | 1643 | 0.401 | 0.201 | 0.00 | 0.000 | 5 |

### fp16

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 2 | 0.000 | 91126 | 21.621 | 0.157 | 21.594 | 23.502 | 0.109 | 20962 | 2.559 | 1.279 | 2.98 | 17.998 | 5 |
| randn | 1 | 0.000 | 84416 | 21.442 | 0.185 | 21.490 | 23.304 | 0.230 | 20792 | 2.538 | 1.269 | 2.95 | 18.140 | 5 |
| randn_sorted | 1 | 0.000 | 61846 | 20.236 | 0.142 | 20.295 | 22.065 | 0.153 | 19682 | 2.403 | 1.201 | 2.72 | 16.968 | 5 |
| pair_half_zero | 1 | 0.000 | 72796 | 19.785 | 0.108 | 19.880 | 21.672 | 0.189 | 19333 | 2.360 | 1.180 | 2.84 | 16.706 | 5 |
| uniform01 | 2 | 0.000 | 77948 | 18.818 | 0.163 | 18.894 | 20.688 | 0.184 | 18456 | 2.253 | 1.126 | 2.79 | 16.005 | 5 |
| fp8grid | 2 | 0.000 | 42486 | 17.477 | 0.106 | 17.566 | 19.434 | 0.161 | 17335 | 2.116 | 1.058 | 2.56 | 14.943 | 5 |
| nn_like | 1 | 0.195 | 84348 | 16.899 | 0.442 | 16.945 | 18.785 | 0.319 | 16758 | 2.046 | 1.023 | 2.39 | 14.493 | 5 |
| smallint | 2 | 0.004 | 35980 | 16.359 | 0.333 | 16.431 | 18.148 | 0.367 | 16189 | 1.976 | 0.988 | 2.28 | 14.091 | 5 |
| sparse50 | 1 | 0.414 | 71590 | 13.113 | 0.029 | 13.282 | 15.036 | 0.126 | 13413 | 1.637 | 0.819 | 2.00 | 11.317 | 5 |
| neg_ones | 2 | 0.000 | 0 | 8.085 | 0.061 | 8.129 | 9.913 | 0.121 | 8842 | 1.079 | 0.540 | 1.41 | 7.021 | 5 |
| ones | 1 | 0.000 | 0 | 8.062 | 0.029 | 8.038 | 9.843 | 0.064 | 8781 | 1.072 | 0.536 | 1.64 | 6.985 | 5 |
| wsparse50 | 1 | 0.760 | 73444 | 6.828 | 0.144 | 6.812 | 8.740 | 0.093 | 7798 | 0.952 | 0.476 | 1.18 | 5.999 | 5 |
| sparse90 | 2 | 0.961 | 18412 | 1.354 | 0.085 | 1.431 | 3.218 | 0.063 | 2871 | 0.350 | 0.175 | 0.63 | 1.203 | 5 |
| a_zeros_b_randn | 2 | 1.000 | 55806 | 0.761 | 0.098 | 0.844 | 2.585 | 0.126 | 2306 | 0.281 | 0.141 | 0.00 | 0.719 | 5 |
| wsparse90 | 2 | 0.990 | 18192 | 0.654 | 0.111 | 0.692 | 2.505 | 0.154 | 2235 | 0.273 | 0.136 | 0.12 | 0.594 | 5 |
| a_randn_b_zeros | 2 | 1.000 | 28096 | 0.624 | 0.155 | 0.603 | 2.434 | 0.180 | 2171 | 0.265 | 0.132 | 0.15 | 0.560 | 5 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.055 | 1.873 | 0.067 | 1671 | 0.204 | 0.102 | 0.03 | 0.000 | 5 |

### int8

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 1 | 0.000 | 69312 | 6.869 | 0.099 | 7.459 | 9.290 | 0.127 | 4826 | 0.295 | — | 1.25 | 6.018 | 5 |
| gauss_q | 1 | 0.000 | 69544 | 6.499 | 0.045 | 7.077 | 8.951 | 0.093 | 4650 | 0.284 | — | 1.14 | 5.666 | 4 |
| sorted | 1 | 0.000 | 53346 | 6.416 | 0.112 | 6.992 | 8.814 | 0.156 | 4579 | 0.279 | — | 1.29 | 5.548 | 5 |
| pos | 1 | 0.000 | 61096 | 5.986 | 0.135 | 6.598 | 8.411 | 0.161 | 4370 | 0.267 | — | 1.05 | 5.315 | 5 |
| smallint | 1 | 0.000 | 70526 | 5.885 | 0.136 | 6.595 | 8.302 | 0.121 | 4313 | 0.263 | — | 1.01 | 5.208 | 5 |
| sparse50 | 1 | 0.070 | 53480 | 5.293 | 0.170 | 5.907 | 7.760 | 0.212 | 4031 | 0.246 | — | 1.01 | 4.710 | 5 |
| ternary | 1 | 0.008 | 58798 | 5.013 | 0.190 | 5.598 | 7.398 | 0.182 | 3844 | 0.235 | — | 1.00 | 4.416 | 5 |
| highbit | 2 | 0.000 | 8664 | 3.094 | 0.145 | 3.763 | 5.538 | 0.201 | 2877 | 0.176 | — | 0.84 | 2.766 | 5 |
| wsparse50 | 1 | 0.644 | 48766 | 2.925 | 0.288 | 3.502 | 5.355 | 0.263 | 2782 | 0.170 | — | 0.94 | 2.690 | 5 |
| neg_ones | 1 | 0.000 | 0 | 1.727 | 0.082 | 2.415 | 4.169 | 0.090 | 2166 | 0.132 | — | 1.00 | 1.512 | 5 |
| ones | 1 | 0.000 | 0 | 1.559 | 0.086 | 2.145 | 3.948 | 0.134 | 2051 | 0.125 | — | 0.79 | 1.346 | 5 |
| sparse90 | 2 | 0.822 | 12144 | 1.133 | 0.060 | 1.775 | 3.492 | 0.102 | 1814 | 0.111 | — | 0.83 | 0.990 | 5 |
| wsparse90 | 2 | 0.980 | 16316 | 0.462 | 0.080 | 1.086 | 2.860 | 0.087 | 1486 | 0.091 | — | 0.88 | 0.437 | 5 |
| a_full_b_zeros | 2 | 1.000 | 65248 | 0.362 | 0.164 | 0.983 | 2.828 | 0.101 | 1469 | 0.090 | — | 0.42 | 0.407 | 5 |
| a_zeros_b_full | 2 | 1.000 | 4140 | 0.335 | 0.093 | 0.946 | 2.786 | 0.082 | 1447 | 0.088 | — | 0.51 | 0.347 | 5 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.592 | 2.402 | 0.060 | 1248 | 0.076 | — | 0.21 | 0.000 | 5 |

## E78's registered rules

| rule | cell | statistic | verdict |
|---|---|---|---|
| E78-R1 | Q130(c) fp32 (15 kinds) | rho 0.934 | **PASS** |
| E78-R1 | Q130(c) fp16 (14 kinds) | rho 0.948 | **PASS** |
| E78-R1 | Q130(c) int8 (13 kinds) | rho 0.867 | **PASS** |
| E78-R1 (secondary) | q130b_r2_A fp32 | rho 0.971 | PASS |
| E78-R1 (secondary) | q130b_r2_A fp16 | rho 0.987 | PASS |
| E78-R1 (secondary) | q130b_r2_A int8 | rho 0.923 | PASS |
| E78-R1 (secondary) | q130b_r2_B fp32 | rho 0.971 | PASS |
| E78-R1 (secondary) | q130b_r2_B fp16 | rho 0.987 | PASS |
| E78-R1 (secondary) | q130b_r2_B int8 | rho 0.945 | PASS |
| E78-R2 | Q130(c) fp32 (15 kinds) | rms 2.470 W (bound 2.0) | **FAIL** |
| E78-R2 | Q130(c) fp16 (14 kinds) | rms 1.987 W (bound 2.0) | **PASS** |
| E78-R2 | Q130(c) int8 (13 kinds) | rms 1.071 W (bound 1.0) | **FAIL** |
| E78-R2 (secondary) | q130b_r2_A fp32 | rms 1.592 W | PASS |
| E78-R2 (secondary) | q130b_r2_A fp16 | rms 1.602 W | PASS |
| E78-R2 (secondary) | q130b_r2_A int8 | rms 7.915 W | FAIL |
| E78-R2 (secondary) | q130b_r2_B fp32 | rms 1.592 W | PASS |
| E78-R2 (secondary) | q130b_r2_B fp16 | rms 1.214 W | PASS |
| E78-R2 (secondary) | q130b_r2_B int8 | rms 8.586 W | FAIL |
| E78-R3a | fp32.a_randn_b_zeros/randn | 0.026 [0.024, 0.029] | **PASS** |
| E78-R3a | fp32.a_zeros_b_randn/randn | 0.030 [0.026, 0.034] | **PASS** |
| E78-R3a | fp16.a_randn_b_zeros/randn | 0.029 [0.022, 0.036] | **PASS** |
| E78-R3a | fp16.a_zeros_b_randn/randn | 0.035 [0.031, 0.040] | **PASS** |
| E78-R3a | int8.a_full_b_zeros/full | 0.053 [0.029, 0.076] | **PASS** |
| E78-R3a | int8.a_zeros_b_full/full | 0.049 [0.035, 0.062] | **PASS** |
| E78-R3b | fp32.sparse90/randn | 0.026 [0.019, 0.033] | **PASS** |
| E78-R3b | fp16.sparse90/randn | 0.063 [0.059, 0.068] | **PASS** |
| E78-R3b | int8.sparse90/full | 0.165 [0.157, 0.173] | **PASS** |
| E78-R3c | fp32.randn_small/randn | 1.003 [0.993, 1.013] | **PASS** |
| E78-R3c | fp32.randn_large/randn | 0.999 [0.982, 1.017] | **PASS** |
| E78-R3e | fp32.randn - fp32.randn_sorted | 1.426 [0.578, 2.274] | **PASS** |
| E78-R3e | fp16.randn - fp16.randn_sorted | 1.206 [1.003, 1.409] | **PASS** |
| E78-R3e | int8.full - int8.sorted | 0.452 [0.298, 0.607] | **PASS** |
| E78-R3f | int8.neg_ones - int8.ones | 0.168 [0.055, 0.282] | **PASS** |
| E78-R3f | fp32.neg_ones - fp32.ones | 0.062 [-0.403, 0.527] | **INCONCLUSIVE** |
| E78-R3f | fp16.neg_ones - fp16.ones | 0.023 [-0.029, 0.075] | **PASS** |
| E78-R3i | fp16.sparse50 - fp16.wsparse50 | 6.285 [6.132, 6.438] | **PASS** |
| E78-R3i | int8.sparse50 - int8.wsparse50 | 2.368 [1.957, 2.778] | **PASS** |
| E78-R3d | fp16grid−bf16trunc, randn−fp16grid | 1.625, 4.755 W | **PASS** |
| E78-R3g | fp16 pair_half_zero/randn | 0.923 [0.911, 0.935] | **PASS** |
| E78-R3h | sparse50/random fp32<fp16<int8 | 0.282, 0.612, 0.771 | **PASS** |
| E78-R4 | fp32.ones | 7.918 vs 8.996 ± 1.0 | **FAIL** |
| E78-R4 | fp32.randn | 23.987 vs 26.662 ± 1.5 | **FAIL** |
| E78-R4 | pi_builtin_vs_file | -0.099 vs 0 ± 0.25 | **PASS** |

Instrument checks (E78-R5): {"idle_consistency": {"median_abs_w": 0.06894912598180891, "ok": true}, "rail_tau": {"median_s": 1.0, "ok": true}, "duty": {"min": 0.9958385243252744, "max": 0.996476076014819, "ok": true}, "carryover": {"slope_w_per_w": 0.0018067013390389824, "se": 0.0010648166399507366, "n": 315, "ok": true}, "tie_dump": {"ok": true}}

## Q130(c), scored as its README and A1 say

- C-R1 fp32: out of sample 0.400 inside the frozen 95% (need 0.7) → **FAIL**; R1-A1 0.600 → FAIL; E78's secondary (intervals overlap) 0.533; all kinds 0.500 → FAIL
- C-R1 fp16: out of sample 0.857 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.857 → PASS; E78's secondary (intervals overlap) 0.857; all kinds 0.882 → PASS
- C-R1 int8: out of sample 0.846 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.846 → PASS; E78's secondary (intervals overlap) 1.000; all kinds 0.875 → PASS
- C-R2 fp32: rho 0.934 → **PASS** (all kinds 0.946)
- C-R2 fp16: rho 0.948 → **PASS** (all kinds 0.960)
- C-R2 int8: rho 0.867 → **FAIL** (all kinds 0.908)
- C-R3 fp16: sparse50 − wsparse50 6.285 W → **PASS**
- C-R3 int8: sparse50 − wsparse50 2.368 W → **PASS**; favours frozen
- C-R4: int8 ones − zeros 1.559 W → **PASS**
- C-R6: → **PASS** (random sign patterns against a constant (A1.6), not a product-sign price)
- C-R9: fp32 a_randn_b_zeros 0.631 W (pass 7810, run first: —) → selects the **gate** arm

## Q130(b) r2, errors in watts above fp32 zeros

- variant A fp32: rms 1.460 W, mean error -0.638 W, |z| ≤ 2 for 0.389 of 18
- variant A fp16: rms 1.488 W, mean error -1.053 W, |z| ≤ 2 for 0.176 of 17
- variant A int8: rms 8.114 W, mean error 6.337 W, |z| ≤ 2 for 0.000 of 16
- variant B fp32: rms 1.460 W, mean error -0.638 W, |z| ≤ 2 for 0.389 of 18
- variant B fp16: rms 1.116 W, mean error -0.566 W, |z| ≤ 2 for 0.294 of 17
- variant B int8: rms 8.736 W, mean error 6.932 W, |z| ≤ 2 for 0.000 of 16
- g per format on E78's anchors: {"fp32": {"g_w_per_live_slot_cycle_s": 1.7242440205526671e-12, "ratio_to_fp32": 1.0}, "fp16": {"g_w_per_live_slot_cycle_s": 1.7558627045468609e-12, "ratio_to_fp32": 1.0183377083622185}, "int8": {"g_w_per_live_slot_cycle_s": 1.976978023631013e-13, "ratio_to_fp32": 0.11465767026394198}}

## Secondary (reported, not a rule): E78-R2 with Q130(c) times the September mid-band factor

Factor 1.0695 (= 1 / 0.935; the midpoint of the registered card band (aifoundry3 = 0.935 x card 1): E78-R2 again with Q130(c)'s aifoundry3 predictions divided by 0.935, reported only).

- fp32: rms 3.320 W over 15 kinds (bound 2.0 W): outside
- fp16: rms 2.835 W over 14 kinds (bound 2.0 W): outside
- int8: rms 1.216 W over 13 kinds (bound 1.0 W): outside

## Cross-card rules (E82 card 1 against E78 aifoundry3)

Band for D(aifoundry3)/D(card 1): [0.88, 0.99]. Passes: E82 [8211, 8212, 8213, 8214, 8215], E78 [7810, 7811, 7812, 7813, 7814, 7815].

| rule | statistic | verdict |
|---|---|---|
| X1 fp32 | Spearman rho 0.995 over 17 of 17 kinds (≥ 0.9) | **PASS** |
| X1 fp16 | Spearman rho 0.997 over 16 of 16 kinds (≥ 0.9) | **PASS** |
| X1 int8 | Spearman rho 1.000 over 15 of 15 kinds (≥ 0.9) | **PASS** |
| X2a | point ratio inside the band for 0.000 of 32 kinds (≥ 0.8) | **FAIL** |
| X2b | 95% interval overlaps the band for 0.188 of 32 kinds (≥ 0.8) | **FAIL** |
| X3 | median ratio 1.031 (IQR 1.025–1.034, 32 kinds) | **FAIL** |

Slope-sensitive verdicts (move at a registered leakage arm): none.

- arm `own idle slopes (card 1 0.545, aifoundry3 0.3803)`: X1 PASS, X2a FAIL (0.000), X2b FAIL, X3 FAIL (median 1.053)
- arm `same slope 0.3803 on both`: X1 PASS, X2a FAIL (0.000), X2b FAIL, X3 FAIL (median 1.028)
- arm `no correction on both`: X1 PASS, X2a FAIL (0.000), X2b FAIL, X3 FAIL (median 1.021)

| kind | D card 1 (W) | ±95% | D aifoundry3 (W) | ±95% | ratio a3/c1 | ±95% | inside |
|---|---|---|---|---|---|---|---|
| fp16.fp8grid | 17.477 | 0.106 | 18.052 | 0.126 | 1.033 | 0.010 | False |
| fp16.neg_ones | 8.085 | 0.061 | 8.382 | 0.133 | 1.037 | 0.018 | False |
| fp16.nn_like | 16.899 | 0.442 | 17.602 | 0.118 | 1.042 | 0.028 | False |
| fp16.ones | 8.062 | 0.029 | 8.448 | 0.082 | 1.048 | 0.011 | False |
| fp16.pair_half_zero | 19.785 | 0.108 | 20.122 | 0.569 | 1.017 | 0.029 | False |
| fp16.randn | 21.442 | 0.185 | 22.162 | 0.054 | 1.034 | 0.009 | False |
| fp16.randn_small | 21.621 | 0.157 | 22.209 | 0.086 | 1.027 | 0.008 | False |
| fp16.randn_sorted | 20.236 | 0.142 | 20.748 | 0.426 | 1.025 | 0.022 | False |
| fp16.smallint | 16.359 | 0.333 | 17.000 | 0.302 | 1.039 | 0.028 | False |
| fp16.sparse50 | 13.113 | 0.029 | 13.196 | 0.540 | 1.006 | 0.041 | False |
| fp16.uniform01 | 18.818 | 0.163 | 19.426 | 0.086 | 1.032 | 0.010 | False |
| fp16.wsparse50 | 6.828 | 0.144 | 7.058 | 0.035 | 1.034 | 0.022 | False |
| fp32.bf16trunc | 17.623 | 0.112 | 18.136 | 0.046 | 1.029 | 0.007 | False |
| fp32.fp16grid | 19.223 | 0.177 | 19.624 | 0.065 | 1.021 | 0.010 | False |
| fp32.neg_ones | 7.980 | 0.195 | 8.143 | 0.408 | 1.021 | 0.057 | False |
| fp32.nn_like | 12.735 | 0.185 | 13.036 | 0.066 | 1.024 | 0.016 | False |
| fp32.ones | 7.918 | 0.427 | 8.257 | 0.221 | 1.043 | 0.063 | False |
| fp32.pi | 8.209 | 0.203 | 8.470 | 0.113 | 1.032 | 0.029 | False |
| fp32.pow2 | 13.708 | 0.044 | 13.985 | 0.159 | 1.020 | 0.012 | False |
| fp32.randn | 23.987 | 0.106 | 24.725 | 0.082 | 1.031 | 0.006 | False |
| fp32.randn_large | 23.974 | 0.356 | 24.711 | 0.084 | 1.031 | 0.016 | False |
| fp32.randn_small | 24.059 | 0.279 | 24.764 | 0.463 | 1.029 | 0.023 | False |
| fp32.randn_sorted | 22.561 | 0.818 | 23.384 | 0.376 | 1.036 | 0.041 | False |
| fp32.smallint | 13.659 | 0.103 | 14.079 | 0.058 | 1.031 | 0.009 | False |
| fp32.sparse50 | 6.760 | 0.464 | 7.302 | 0.063 | 1.080 | 0.075 | False |
| fp32.uniform01 | 22.031 | 0.088 | 22.646 | 0.093 | 1.028 | 0.006 | False |
| int8.full | 6.869 | 0.099 | 7.056 | 0.059 | 1.027 | 0.017 | False |
| int8.gauss_q | 6.499 | 0.045 | 6.598 | 0.069 | 1.015 | 0.013 | False |
| int8.smallint | 5.885 | 0.136 | 6.003 | 0.142 | 1.020 | 0.034 | False |
| int8.sorted | 6.416 | 0.112 | 6.588 | 0.073 | 1.027 | 0.021 | False |
| int8.sparse50 | 5.293 | 0.170 | 5.463 | 0.146 | 1.032 | 0.043 | False |
| int8.ternary | 5.013 | 0.190 | 5.186 | 0.051 | 1.035 | 0.041 | False |

Reported beside: {"zero_level_S_w": {"fp32": {"e82": 1.8410125313283217, "e78": 1.9858230735486515}, "fp16": {"e82": 1.8725380952380983, "e78": 1.9872138279205274}, "int8": {"e82": 2.40154285714286, "e78": 2.605255386405539}}, "idle_level_w": {"e82": 33.10457233918638, "e78": 25.911429884364832}, "v_mean": {"e82": 0.49871671875000007, "e78": 0.5216593258274552}, "leak_k": {"e82": 0.24142857142857624, "e78": 0.19940337259099877}, "passes": {"e82": [8211, 8212, 8213, 8214, 8215], "e78": [7810, 7811, 7812, 7813, 7814, 7815]}}

E78's rule verdicts on the two cards: 31 of 33 the same; differing: {"/E78-R4/fp32.ones/verdict": {"e82": "FAIL", "e78": "PASS"}, "/E78-R4/fp32.randn/verdict": {"e82": "FAIL", "e78": "PASS"}}
