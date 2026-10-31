# E78 results — aifoundry3 card 0, 600 MHz, 521.7 mV

Passes kept [7810, 7811, 7812, 7813, 7814, 7815] (6); runs kept 388 of 388; leakage slope 0.1994 W/°C (auto); idle level 25.911 W; cycles per op {'fp32': 546.001, 'fp16': 546.001, 'int8': 318.0}.

**Tally (registered rules, primary leak slope):** 28 pass, 2 fail, 0 inconclusive, 0 not scored.

- arm `leak0.3803`: {'PASS': 28, 'FAIL': 2, 'INCONCLUSIVE': 0, 'NOT SCORED': 0}
- arm `leak0`: {'PASS': 28, 'FAIL': 2, 'INCONCLUSIVE': 0, 'NOT SCORED': 0}

## The matrix

D = switching power over the type's own zeros (paired, interpolated zeros); S = over the idle bracket; pJ from S at the measured op rate. 95% intervals from the between-pass scatter.

### fp32

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 2 | 0.000 | 82244 | 24.764 | 0.463 | 24.764 | 26.661 | 0.472 | 23786 | 5.807 | 2.904 | 3.16 | 19.986 | 6 |
| randn | 1 | 0.000 | 82214 | 24.725 | 0.082 | 24.725 | 26.701 | 0.054 | 23823 | 5.816 | 2.908 | 3.16 | 19.794 | 6 |
| randn_large | 2 | 0.000 | 84896 | 24.711 | 0.084 | 24.711 | 26.657 | 0.096 | 23779 | 5.806 | 2.903 | 3.02 | 19.780 | 6 |
| randn_sorted | 1 | 0.000 | 60856 | 23.384 | 0.376 | 23.384 | 25.378 | 0.362 | 22639 | 5.527 | 2.764 | 2.99 | 18.956 | 6 |
| uniform01 | 2 | 0.000 | 77842 | 22.646 | 0.093 | 22.646 | 24.636 | 0.055 | 21975 | 5.365 | 2.683 | 2.87 | 18.151 | 6 |
| fp16grid | 2 | 0.000 | 43136 | 19.624 | 0.065 | 19.624 | 21.546 | 0.092 | 19224 | 4.693 | 2.347 | 2.61 | 15.990 | 6 |
| bf16trunc | 1 | 0.000 | 34980 | 18.136 | 0.046 | 18.136 | 20.144 | 0.082 | 17969 | 4.387 | 2.193 | 2.38 | 14.818 | 6 |
| smallint | 1 | 0.118 | 19806 | 14.079 | 0.058 | 14.079 | 16.023 | 0.132 | 14296 | 3.490 | 1.745 | 1.98 | 11.577 | 6 |
| pow2 | 1 | 0.000 | 25414 | 13.985 | 0.159 | 13.985 | 15.984 | 0.218 | 14258 | 3.481 | 1.741 | 2.00 | 11.472 | 6 |
| nn_like | 1 | 0.508 | 80426 | 13.036 | 0.066 | 13.036 | 15.034 | 0.057 | 13413 | 3.275 | 1.637 | 1.93 | 10.737 | 6 |
| pi | 2 | 0.000 | 0 | 8.470 | 0.113 | 8.470 | 10.397 | 0.152 | 9274 | 2.264 | 1.132 | 1.16 | 7.131 | 6 |
| ones | 1 | 0.000 | 0 | 8.257 | 0.221 | 8.257 | 10.288 | 0.208 | 9179 | 2.241 | 1.121 | 1.20 | 7.048 | 6 |
| neg_ones | 2 | 0.000 | 0 | 8.143 | 0.408 | 8.143 | 10.116 | 0.435 | 9025 | 2.203 | 1.102 | 1.08 | 7.045 | 6 |
| sparse50 | 1 | 0.774 | 74550 | 7.302 | 0.063 | 7.302 | 9.243 | 0.147 | 8245 | 2.013 | 1.006 | 1.00 | 6.149 | 6 |
| a_zeros_b_randn | 2 | 1.000 | 55798 | 0.810 | 0.065 | 0.810 | 2.839 | 0.039 | 2533 | 0.618 | 0.309 | 0.17 | 0.687 | 6 |
| a_randn_b_zeros | 1 | 1.000 | 27920 | 0.616 | 0.122 | 0.616 | 2.574 | 0.169 | 2295 | 0.560 | 0.280 | -0.08 | 0.552 | 6 |
| sparse90 | 1 | 0.992 | 17780 | 0.577 | 0.073 | 0.577 | 2.509 | 0.138 | 2238 | 0.546 | 0.273 | 0.13 | 0.499 | 6 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.000 | 1.986 | 0.059 | 1772 | 0.433 | 0.216 | 0.06 | 0.000 | 6 |

### fp16

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 2 | 0.000 | 91126 | 22.209 | 0.086 | 22.207 | 24.131 | 0.092 | 21528 | 2.628 | 1.314 | 2.82 | 18.046 | 6 |
| randn | 1 | 0.000 | 84416 | 22.162 | 0.054 | 22.138 | 24.102 | 0.030 | 21504 | 2.625 | 1.312 | 2.80 | 17.789 | 6 |
| randn_sorted | 1 | 0.000 | 61846 | 20.748 | 0.426 | 20.705 | 22.695 | 0.415 | 20244 | 2.471 | 1.236 | 2.69 | 17.053 | 6 |
| pair_half_zero | 1 | 0.000 | 72796 | 20.122 | 0.569 | 20.105 | 22.091 | 0.542 | 19707 | 2.406 | 1.203 | 2.55 | 16.535 | 6 |
| uniform01 | 2 | 0.000 | 77948 | 19.426 | 0.086 | 19.393 | 21.371 | 0.109 | 19064 | 2.327 | 1.164 | 2.60 | 15.775 | 6 |
| fp8grid | 2 | 0.000 | 42486 | 18.052 | 0.126 | 18.005 | 19.978 | 0.090 | 17823 | 2.176 | 1.088 | 2.29 | 14.731 | 6 |
| nn_like | 1 | 0.195 | 84348 | 17.602 | 0.118 | 17.511 | 19.480 | 0.226 | 17383 | 2.122 | 1.061 | 2.23 | 14.378 | 6 |
| smallint | 2 | 0.004 | 35980 | 17.000 | 0.302 | 16.960 | 18.926 | 0.235 | 16883 | 2.061 | 1.030 | 2.25 | 14.056 | 6 |
| sparse50 | 1 | 0.414 | 71590 | 13.196 | 0.540 | 13.180 | 15.220 | 0.575 | 13576 | 1.657 | 0.829 | 1.83 | 11.104 | 6 |
| ones | 1 | 0.000 | 0 | 8.448 | 0.082 | 8.410 | 10.376 | 0.081 | 9256 | 1.130 | 0.565 | 1.09 | 7.111 | 6 |
| neg_ones | 2 | 0.000 | 0 | 8.382 | 0.133 | 8.384 | 10.355 | 0.103 | 9239 | 1.128 | 0.564 | 1.17 | 7.033 | 6 |
| wsparse50 | 1 | 0.760 | 73444 | 7.058 | 0.035 | 7.089 | 9.090 | 0.091 | 8109 | 0.990 | 0.495 | 1.00 | 5.965 | 6 |
| sparse90 | 2 | 0.961 | 18412 | 1.410 | 0.113 | 1.414 | 3.380 | 0.086 | 3015 | 0.368 | 0.184 | 0.37 | 1.208 | 6 |
| a_zeros_b_randn | 2 | 1.000 | 55806 | 0.782 | 0.063 | 0.758 | 2.713 | 0.054 | 2420 | 0.295 | 0.148 | 0.53 | 0.630 | 6 |
| wsparse90 | 2 | 0.990 | 18192 | 0.743 | 0.111 | 0.672 | 2.643 | 0.109 | 2358 | 0.288 | 0.144 | 0.27 | 0.592 | 6 |
| a_randn_b_zeros | 2 | 1.000 | 28096 | 0.659 | 0.080 | 0.714 | 2.669 | 0.085 | 2381 | 0.291 | 0.145 | 0.21 | 0.558 | 6 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | -0.009 | 1.987 | 0.052 | 1773 | 0.216 | 0.108 | -0.06 | 0.000 | 6 |

### int8

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 1 | 0.000 | 69312 | 7.056 | 0.059 | 7.667 | 9.648 | 0.081 | 5010 | 0.306 | — | 1.01 | 5.943 | 6 |
| gauss_q | 1 | 0.000 | 69544 | 6.598 | 0.069 | 7.202 | 9.161 | 0.135 | 4757 | 0.290 | — | 1.00 | 5.548 | 6 |
| sorted | 1 | 0.000 | 53346 | 6.588 | 0.073 | 7.206 | 9.170 | 0.118 | 4763 | 0.291 | — | 1.00 | 5.500 | 6 |
| pos | 1 | 0.000 | 61096 | 6.171 | 0.206 | 6.761 | 8.733 | 0.207 | 4536 | 0.277 | — | 1.00 | 5.239 | 6 |
| smallint | 1 | 0.000 | 70526 | 6.003 | 0.142 | 6.615 | 8.628 | 0.096 | 4481 | 0.273 | — | 1.00 | 5.118 | 6 |
| sparse50 | 1 | 0.070 | 53480 | 5.463 | 0.146 | 6.085 | 8.061 | 0.126 | 4187 | 0.256 | — | 1.00 | 4.593 | 6 |
| ternary | 1 | 0.008 | 58798 | 5.186 | 0.051 | 5.790 | 7.727 | 0.097 | 4013 | 0.245 | — | 1.00 | 4.371 | 6 |
| highbit | 2 | 0.000 | 8664 | 3.233 | 0.036 | 3.841 | 5.853 | 0.068 | 3039 | 0.186 | — | 0.83 | 2.746 | 6 |
| wsparse50 | 1 | 0.644 | 48766 | 3.142 | 0.056 | 3.770 | 5.743 | 0.088 | 2983 | 0.182 | — | 0.83 | 2.710 | 6 |
| neg_ones | 1 | 0.000 | 0 | 1.628 | 0.169 | 2.237 | 4.176 | 0.134 | 2169 | 0.132 | — | 0.81 | 1.448 | 6 |
| ones | 1 | 0.000 | 0 | 1.561 | 0.069 | 2.170 | 4.146 | 0.078 | 2153 | 0.131 | — | 1.00 | 1.356 | 6 |
| sparse90 | 2 | 0.822 | 12144 | 1.145 | 0.057 | 1.743 | 3.763 | 0.083 | 1955 | 0.119 | — | 0.83 | 0.949 | 6 |
| wsparse90 | 2 | 0.980 | 16316 | 0.538 | 0.051 | 1.155 | 3.079 | 0.069 | 1599 | 0.098 | — | 0.37 | 0.454 | 6 |
| a_full_b_zeros | 2 | 1.000 | 65248 | 0.497 | 0.085 | 1.130 | 3.115 | 0.034 | 1618 | 0.099 | — | 0.33 | 0.391 | 6 |
| a_zeros_b_full | 2 | 1.000 | 4140 | 0.305 | 0.070 | 0.913 | 2.900 | 0.062 | 1506 | 0.092 | — | 0.48 | 0.253 | 6 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.612 | 2.605 | 0.028 | 1353 | 0.083 | — | 0.22 | 0.000 | 6 |

## E78's registered rules

| rule | cell | statistic | verdict |
|---|---|---|---|
| E78-R1 | Q130(c) fp32 (15 kinds) | rho 0.941 | **PASS** |
| E78-R1 | Q130(c) fp16 (14 kinds) | rho 0.948 | **PASS** |
| E78-R1 | Q130(c) int8 (13 kinds) | rho 0.867 | **PASS** |
| E78-R1 (secondary) | q130b_r2_A fp32 | rho 0.974 | PASS |
| E78-R1 (secondary) | q130b_r2_A fp16 | rho 0.978 | PASS |
| E78-R1 (secondary) | q130b_r2_A int8 | rho 0.912 | PASS |
| E78-R1 (secondary) | q130b_r2_B fp32 | rho 0.974 | PASS |
| E78-R1 (secondary) | q130b_r2_B fp16 | rho 0.978 | PASS |
| E78-R1 (secondary) | q130b_r2_B int8 | rho 0.934 | PASS |
| E78-R2 | Q130(c) fp32 (15 kinds) | rms 2.270 W (bound 2.0) | **FAIL** |
| E78-R2 | Q130(c) fp16 (14 kinds) | rms 1.757 W (bound 2.0) | **PASS** |
| E78-R2 | Q130(c) int8 (13 kinds) | rms 1.054 W (bound 1.0) | **FAIL** |
| E78-R2 (secondary) | q130b_r2_A fp32 | rms 1.826 W | PASS |
| E78-R2 (secondary) | q130b_r2_A fp16 | rms 1.868 W | PASS |
| E78-R2 (secondary) | q130b_r2_A int8 | rms 7.845 W | FAIL |
| E78-R2 (secondary) | q130b_r2_B fp32 | rms 1.826 W | PASS |
| E78-R2 (secondary) | q130b_r2_B fp16 | rms 1.408 W | PASS |
| E78-R2 (secondary) | q130b_r2_B int8 | rms 8.511 W | FAIL |
| E78-R3a | fp32.a_randn_b_zeros/randn | 0.025 [0.020, 0.030] | **PASS** |
| E78-R3a | fp32.a_zeros_b_randn/randn | 0.033 [0.030, 0.035] | **PASS** |
| E78-R3a | fp16.a_randn_b_zeros/randn | 0.030 [0.026, 0.033] | **PASS** |
| E78-R3a | fp16.a_zeros_b_randn/randn | 0.035 [0.032, 0.038] | **PASS** |
| E78-R3a | int8.a_full_b_zeros/full | 0.071 [0.058, 0.083] | **PASS** |
| E78-R3a | int8.a_zeros_b_full/full | 0.043 [0.034, 0.053] | **PASS** |
| E78-R3b | fp32.sparse90/randn | 0.023 [0.020, 0.026] | **PASS** |
| E78-R3b | fp16.sparse90/randn | 0.064 [0.059, 0.069] | **PASS** |
| E78-R3b | int8.sparse90/full | 0.162 [0.154, 0.170] | **PASS** |
| E78-R3c | fp32.randn_small/randn | 1.002 [0.981, 1.022] | **PASS** |
| E78-R3c | fp32.randn_large/randn | 0.999 [0.997, 1.002] | **PASS** |
| E78-R3e | fp32.randn - fp32.randn_sorted | 1.341 [1.006, 1.676] | **PASS** |
| E78-R3e | fp16.randn - fp16.randn_sorted | 1.414 [1.016, 1.812] | **PASS** |
| E78-R3e | int8.full - int8.sorted | 0.468 [0.368, 0.568] | **PASS** |
| E78-R3f | int8.neg_ones - int8.ones | 0.067 [-0.050, 0.184] | **PASS** |
| E78-R3f | fp32.neg_ones - fp32.ones | -0.113 [-0.521, 0.295] | **INCONCLUSIVE** |
| E78-R3f | fp16.neg_ones - fp16.ones | -0.067 [-0.221, 0.087] | **PASS** |
| E78-R3i | fp16.sparse50 - fp16.wsparse50 | 6.138 [5.606, 6.670] | **PASS** |
| E78-R3i | int8.sparse50 - int8.wsparse50 | 2.322 [2.154, 2.489] | **PASS** |
| E78-R3d | fp16grid−bf16trunc, randn−fp16grid | 1.488, 5.101 W | **PASS** |
| E78-R3g | fp16 pair_half_zero/randn | 0.908 [0.883, 0.933] | **PASS** |
| E78-R3h | sparse50/random fp32<fp16<int8 | 0.295, 0.595, 0.774 | **PASS** |
| E78-R4 | fp32.ones | 8.257 vs 8.217 ± 0.6 | **PASS** |
| E78-R4 | fp32.pi | 8.470 vs 8.496 ± 0.6 | **PASS** |
| E78-R4 | fp32.randn | 24.725 vs 24.659 ± 1.0 | **PASS** |
| E78-R4 | fp16.ones | 8.448 vs 8.736 ± 0.8 | **PASS** |
| E78-R4 | int8.ones | 1.561 vs 1.834 ± 0.6 | **PASS** |
| E78-R4 | pi_builtin_vs_file | -0.067 vs 0 ± 0.25 | **PASS** |

Instrument checks (E78-R5): {"idle_consistency": {"median_abs_w": 0.06360348107096492, "ok": true}, "rail_tau": {"median_s": 0.95, "ok": true}, "duty": {"min": 0.9958708852700753, "max": 0.9967051424482122, "ok": true}, "carryover": {"slope_w_per_w": 0.0007712691941556166, "se": 0.0009081902072256213, "n": 382, "ok": true}, "tie_dump": {"ok": true}}

## Q130(c), scored as its README and A1 say

- C-R1 fp32: out of sample 0.533 inside the frozen 95% (need 0.7) → **FAIL**; R1-A1 0.733 → PASS; E78's secondary (intervals overlap) 0.600; all kinds 0.611 → FAIL
- C-R1 fp16: out of sample 0.857 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.857 → PASS; E78's secondary (intervals overlap) 0.857; all kinds 0.882 → PASS
- C-R1 int8: out of sample 0.846 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.846 → PASS; E78's secondary (intervals overlap) 0.923; all kinds 0.875 → PASS
- C-R2 fp32: rho 0.941 → **PASS** (all kinds 0.950)
- C-R2 fp16: rho 0.948 → **PASS** (all kinds 0.960)
- C-R2 int8: rho 0.867 → **FAIL** (all kinds 0.908)
- C-R3 fp16: sparse50 − wsparse50 6.138 W → **PASS**
- C-R3 int8: sparse50 − wsparse50 2.322 W → **PASS**; favours frozen
- C-R4: int8 ones − zeros 1.561 W → **PASS**
- C-R6: → **PASS** (random sign patterns against a constant (A1.6), not a product-sign price)
- C-R9: fp32 a_randn_b_zeros 0.616 W (pass 7810, run first: 0.528) → selects the **gate** arm

## Q130(b) r2, errors in watts above fp32 zeros

- variant A fp32: rms 1.672 W, mean error -1.019 W, |z| ≤ 2 for 0.222 of 18
- variant A fp16: rms 1.748 W, mean error -1.326 W, |z| ≤ 2 for 0.176 of 17
- variant A int8: rms 8.042 W, mean error 6.245 W, |z| ≤ 2 for 0.000 of 16
- variant B fp32: rms 1.672 W, mean error -1.019 W, |z| ≤ 2 for 0.222 of 18
- variant B fp16: rms 1.287 W, mean error -0.839 W, |z| ≤ 2 for 0.235 of 17
- variant B int8: rms 8.659 W, mean error 6.841 W, |z| ≤ 2 for 0.000 of 16
- g per format on E78's anchors: {"fp32": {"g_w_per_live_slot_cycle_s": 1.7984470349512697e-12, "ratio_to_fp32": 1.0}, "fp16": {"g_w_per_live_slot_cycle_s": 1.839937436825462e-12, "ratio_to_fp32": 1.0230701272085652}, "int8": {"g_w_per_live_slot_cycle_s": 1.979547947207311e-13, "ratio_to_fp32": 0.11006984963896634}}
