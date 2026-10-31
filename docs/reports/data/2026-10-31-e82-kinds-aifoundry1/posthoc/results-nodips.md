# E82 results — aifoundry1 card 1, 600 MHz, 498.7 mV (E78's rules, scored by score_e78.py unchanged)

Passes kept [8210, 8211, 8212, 8213, 8214, 8215, 8216] (7); runs kept 450 of 450; leakage slope 0.2541 W/°C (auto); idle level 33.094 W; cycles per op {'fp32': 546.001, 'fp16': 546.001, 'int8': 318.0}.

**Tally (registered rules, primary leak slope):** 24 pass, 3 fail, 0 inconclusive, 0 not scored.


## The matrix

D = switching power over the type's own zeros (paired, interpolated zeros); S = over the idle bracket; pJ from S at the measured op rate. 95% intervals from the between-pass scatter.

### fp32

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 2 | 0.000 | 82244 | 24.167 | 0.080 | 24.167 | 25.992 | 0.074 | 23192 | 5.662 | 2.831 | 3.33 | 20.131 | 7 |
| randn | 1 | 0.000 | 82214 | 24.002 | 0.065 | 24.002 | 25.845 | 0.042 | 23057 | 5.629 | 2.815 | 3.34 | 19.982 | 7 |
| randn_large | 2 | 0.000 | 84896 | 23.962 | 0.143 | 23.962 | 25.776 | 0.087 | 22998 | 5.615 | 2.807 | 3.25 | 19.833 | 7 |
| randn_sorted | 1 | 0.000 | 60856 | 22.787 | 0.151 | 22.787 | 24.668 | 0.140 | 22003 | 5.372 | 2.686 | 3.09 | 19.056 | 7 |
| uniform01 | 2 | 0.000 | 77842 | 21.953 | 0.136 | 21.953 | 23.831 | 0.100 | 21260 | 5.190 | 2.595 | 2.99 | 18.290 | 7 |
| fp16grid | 2 | 0.000 | 43136 | 19.155 | 0.106 | 19.155 | 20.968 | 0.093 | 18704 | 4.566 | 2.283 | 2.75 | 16.145 | 6 |
| bf16trunc | 1 | 0.000 | 34980 | 17.606 | 0.072 | 17.606 | 19.440 | 0.088 | 17341 | 4.234 | 2.117 | 2.56 | 14.926 | 7 |
| smallint | 1 | 0.118 | 19806 | 13.665 | 0.080 | 13.665 | 15.522 | 0.058 | 13851 | 3.382 | 1.691 | 2.03 | 11.741 | 7 |
| pow2 | 1 | 0.000 | 25414 | 13.658 | 0.051 | 13.658 | 15.480 | 0.196 | 13811 | 3.372 | 1.686 | 2.00 | 11.732 | 7 |
| nn_like | 1 | 0.508 | 80426 | 12.720 | 0.114 | 12.720 | 14.569 | 0.146 | 12996 | 3.173 | 1.586 | 1.99 | 10.913 | 7 |
| pi | 2 | 0.000 | 0 | 8.181 | 0.123 | 8.181 | 9.963 | 0.091 | 8889 | 2.170 | 1.085 | 1.36 | 7.155 | 7 |
| ones | 1 | 0.000 | 0 | 8.051 | 0.156 | 8.051 | 9.821 | 0.136 | 8760 | 2.139 | 1.069 | 1.36 | 7.014 | 7 |
| neg_ones | 2 | 0.000 | 0 | 7.943 | 0.143 | 7.943 | 9.898 | 0.045 | 8829 | 2.155 | 1.078 | 1.34 | 6.999 | 7 |
| sparse50 | 1 | 0.774 | 74550 | 7.029 | 0.183 | 7.029 | 8.909 | 0.125 | 7947 | 1.940 | 0.970 | 1.00 | 6.064 | 7 |
| a_zeros_b_randn | 2 | 1.000 | 55798 | 0.720 | 0.057 | 0.720 | 2.644 | 0.102 | 2358 | 0.576 | 0.288 | 0.36 | 0.679 | 7 |
| a_randn_b_zeros | 1 | 1.000 | 27920 | 0.643 | 0.043 | 0.643 | 2.506 | 0.113 | 2236 | 0.546 | 0.273 | 0.32 | 0.563 | 7 |
| sparse90 | 1 | 0.992 | 17780 | 0.598 | 0.114 | 0.598 | 2.450 | 0.100 | 2185 | 0.534 | 0.267 | 0.24 | 0.562 | 6 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.000 | 1.846 | 0.071 | 1647 | 0.402 | 0.201 | 0.00 | 0.000 | 7 |

### fp16

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 2 | 0.000 | 91126 | 21.598 | 0.123 | 21.550 | 23.462 | 0.079 | 20928 | 2.555 | 1.277 | 3.00 | 18.076 | 7 |
| randn | 1 | 0.000 | 84416 | 21.490 | 0.058 | 21.518 | 23.368 | 0.048 | 20850 | 2.545 | 1.273 | 2.91 | 18.097 | 7 |
| randn_sorted | 1 | 0.000 | 61846 | 20.219 | 0.091 | 20.263 | 22.074 | 0.115 | 19691 | 2.404 | 1.202 | 2.74 | 16.936 | 7 |
| pair_half_zero | 1 | 0.000 | 72796 | 19.782 | 0.094 | 19.837 | 21.654 | 0.123 | 19317 | 2.358 | 1.179 | 2.85 | 16.700 | 7 |
| uniform01 | 2 | 0.000 | 77948 | 18.846 | 0.068 | 18.872 | 20.664 | 0.122 | 18433 | 2.250 | 1.125 | 2.76 | 15.970 | 7 |
| fp8grid | 2 | 0.000 | 42486 | 17.438 | 0.064 | 17.510 | 19.394 | 0.108 | 17299 | 2.112 | 1.056 | 2.59 | 14.923 | 7 |
| nn_like | 1 | 0.195 | 84348 | 17.010 | 0.104 | 17.027 | 18.875 | 0.104 | 16839 | 2.056 | 1.028 | 2.32 | 14.629 | 7 |
| smallint | 2 | 0.004 | 35980 | 16.437 | 0.077 | 16.494 | 18.236 | 0.090 | 16267 | 1.986 | 0.993 | 2.25 | 14.016 | 7 |
| sparse50 | 1 | 0.414 | 71590 | 13.081 | 0.042 | 13.214 | 14.978 | 0.113 | 13363 | 1.631 | 0.816 | 2.00 | 11.244 | 7 |
| neg_ones | 2 | 0.000 | 0 | 8.094 | 0.063 | 8.116 | 9.925 | 0.085 | 8854 | 1.081 | 0.540 | 1.29 | 7.050 | 7 |
| ones | 1 | 0.000 | 0 | 8.019 | 0.040 | 7.989 | 9.812 | 0.063 | 8753 | 1.068 | 0.534 | 1.57 | 6.966 | 7 |
| wsparse50 | 1 | 0.760 | 73444 | 6.832 | 0.093 | 6.785 | 8.724 | 0.097 | 7783 | 0.950 | 0.475 | 1.19 | 5.999 | 7 |
| sparse90 | 2 | 0.961 | 18412 | 1.348 | 0.056 | 1.382 | 3.197 | 0.059 | 2852 | 0.348 | 0.174 | 0.57 | 1.210 | 7 |
| a_zeros_b_randn | 2 | 1.000 | 55806 | 0.801 | 0.100 | 0.844 | 2.622 | 0.106 | 2339 | 0.286 | 0.143 | 0.03 | 0.743 | 7 |
| a_randn_b_zeros | 2 | 1.000 | 28096 | 0.646 | 0.102 | 0.617 | 2.475 | 0.137 | 2208 | 0.270 | 0.135 | 0.18 | 0.571 | 7 |
| wsparse90 | 2 | 0.990 | 18192 | 0.636 | 0.076 | 0.653 | 2.494 | 0.105 | 2225 | 0.272 | 0.136 | 0.09 | 0.587 | 7 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.033 | 1.890 | 0.068 | 1686 | 0.206 | 0.103 | -0.02 | 0.000 | 7 |

### int8

| kind | tier | gated | bus bits/op | D (W) | ±95% | D32 (W) | S over idle (W) | ±95% | pJ/op (S) | pJ/MAC (S) | pJ/flop (S) | ΔT window (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 1 | 0.000 | 69312 | 6.839 | 0.091 | 7.405 | 9.250 | 0.124 | 4805 | 0.293 | — | 1.21 | 6.020 | 7 |
| gauss_q | 1 | 0.000 | 69544 | 6.483 | 0.028 | 7.061 | 8.962 | 0.104 | 4656 | 0.284 | — | 1.10 | 5.672 | 6 |
| sorted | 1 | 0.000 | 53346 | 6.399 | 0.113 | 6.948 | 8.789 | 0.117 | 4566 | 0.279 | — | 1.20 | 5.576 | 7 |
| pos | 1 | 0.000 | 61096 | 5.967 | 0.088 | 6.539 | 8.360 | 0.168 | 4343 | 0.265 | — | 1.04 | 5.324 | 7 |
| smallint | 1 | 0.000 | 70526 | 5.880 | 0.082 | 6.552 | 8.299 | 0.076 | 4311 | 0.263 | — | 1.01 | 5.218 | 7 |
| sparse50 | 1 | 0.070 | 53480 | 5.235 | 0.131 | 5.851 | 7.733 | 0.137 | 4018 | 0.245 | — | 0.97 | 4.670 | 7 |
| ternary | 1 | 0.008 | 58798 | 4.990 | 0.143 | 5.581 | 7.373 | 0.125 | 3831 | 0.234 | — | 1.00 | 4.418 | 7 |
| highbit | 2 | 0.000 | 8664 | 3.152 | 0.064 | 3.764 | 5.558 | 0.104 | 2888 | 0.176 | — | 0.89 | 2.768 | 7 |
| wsparse50 | 1 | 0.644 | 48766 | 3.042 | 0.130 | 3.589 | 5.468 | 0.120 | 2841 | 0.173 | — | 0.96 | 2.689 | 7 |
| neg_ones | 1 | 0.000 | 0 | 1.679 | 0.083 | 2.358 | 4.135 | 0.082 | 2148 | 0.131 | — | 1.00 | 1.497 | 7 |
| ones | 1 | 0.000 | 0 | 1.559 | 0.066 | 2.124 | 3.954 | 0.082 | 2054 | 0.125 | — | 0.85 | 1.332 | 7 |
| sparse90 | 2 | 0.822 | 12144 | 1.132 | 0.043 | 1.745 | 3.512 | 0.075 | 1824 | 0.111 | — | 0.88 | 0.986 | 7 |
| wsparse90 | 2 | 0.980 | 16316 | 0.492 | 0.160 | 1.078 | 2.874 | 0.065 | 1493 | 0.091 | — | 0.77 | 0.453 | 7 |
| a_full_b_zeros | 2 | 1.000 | 65248 | 0.380 | 0.146 | 0.959 | 2.807 | 0.075 | 1458 | 0.089 | — | 0.30 | 0.436 | 7 |
| a_zeros_b_full | 2 | 1.000 | 4140 | 0.343 | 0.140 | 0.944 | 2.782 | 0.121 | 1446 | 0.088 | — | 0.39 | 0.374 | 7 |
| zeros | 1 | 1.000 | 0 | 0.000 | 0.000 | 0.576 | 2.416 | 0.038 | 1255 | 0.077 | — | 0.17 | 0.000 | 7 |

## E78's registered rules

| rule | cell | statistic | verdict |
|---|---|---|---|
| E78-R1 | Q130(c) fp32 (15 kinds) | rho 0.941 | **PASS** |
| E78-R1 | Q130(c) fp16 (14 kinds) | rho 0.942 | **PASS** |
| E78-R1 | Q130(c) int8 (13 kinds) | rho 0.867 | **PASS** |
| E78-R1 (secondary) | q130b_r2_A fp32 | rho 0.974 | PASS |
| E78-R1 (secondary) | q130b_r2_A fp16 | rho 0.987 | PASS |
| E78-R1 (secondary) | q130b_r2_A int8 | rho 0.940 | PASS |
| E78-R1 (secondary) | q130b_r2_B fp32 | rho 0.974 | PASS |
| E78-R1 (secondary) | q130b_r2_B fp16 | rho 0.987 | PASS |
| E78-R1 (secondary) | q130b_r2_B int8 | rho 0.962 | PASS |
| E78-R2 | Q130(c) fp32 (15 kinds) | rms 2.456 W (bound 2.0) | **FAIL** |
| E78-R2 | Q130(c) fp16 (14 kinds) | rms 1.980 W (bound 2.0) | **PASS** |
| E78-R2 | Q130(c) int8 (13 kinds) | rms 1.063 W (bound 1.0) | **FAIL** |
| E78-R2 (secondary) | q130b_r2_A fp32 | rms 1.590 W | PASS |
| E78-R2 (secondary) | q130b_r2_A fp16 | rms 1.592 W | PASS |
| E78-R2 (secondary) | q130b_r2_A int8 | rms 7.941 W | FAIL |
| E78-R2 (secondary) | q130b_r2_B fp32 | rms 1.590 W | PASS |
| E78-R2 (secondary) | q130b_r2_B fp16 | rms 1.208 W | PASS |
| E78-R2 (secondary) | q130b_r2_B int8 | rms 8.612 W | FAIL |
| E78-R3a | fp32.a_randn_b_zeros/randn | 0.027 [0.025, 0.029] | **PASS** |
| E78-R3a | fp32.a_zeros_b_randn/randn | 0.030 [0.028, 0.032] | **PASS** |
| E78-R3a | fp16.a_randn_b_zeros/randn | 0.030 [0.025, 0.035] | **PASS** |
| E78-R3a | fp16.a_zeros_b_randn/randn | 0.037 [0.033, 0.042] | **PASS** |
| E78-R3a | int8.a_full_b_zeros/full | 0.056 [0.034, 0.078] | **PASS** |
| E78-R3a | int8.a_zeros_b_full/full | 0.050 [0.030, 0.070] | **PASS** |
| E78-R3b | fp32.sparse90/randn | 0.025 [0.020, 0.030] | **PASS** |
| E78-R3b | fp16.sparse90/randn | 0.063 [0.060, 0.065] | **PASS** |
| E78-R3b | int8.sparse90/full | 0.165 [0.160, 0.171] | **PASS** |
| E78-R3c | fp32.randn_small/randn | 1.007 [1.003, 1.011] | **PASS** |
| E78-R3c | fp32.randn_large/randn | 0.998 [0.993, 1.004] | **PASS** |
| E78-R3e | fp32.randn - fp32.randn_sorted | 1.215 [1.110, 1.320] | **PASS** |
| E78-R3e | fp16.randn - fp16.randn_sorted | 1.271 [1.137, 1.405] | **PASS** |
| E78-R3e | int8.full - int8.sorted | 0.440 [0.258, 0.622] | **PASS** |
| E78-R3f | int8.neg_ones - int8.ones | 0.120 [0.003, 0.236] | **PASS** |
| E78-R3f | fp32.neg_ones - fp32.ones | -0.108 [-0.246, 0.030] | **PASS** |
| E78-R3f | fp16.neg_ones - fp16.ones | 0.075 [-0.013, 0.164] | **PASS** |
| E78-R3i | fp16.sparse50 - fp16.wsparse50 | 6.250 [6.137, 6.362] | **PASS** |
| E78-R3i | int8.sparse50 - int8.wsparse50 | 2.193 [1.982, 2.405] | **PASS** |
| E78-R3d | fp16grid−bf16trunc, randn−fp16grid | 1.565, 4.826 W | **PASS** |
| E78-R3g | fp16 pair_half_zero/randn | 0.921 [0.914, 0.927] | **PASS** |
| E78-R3h | sparse50/random fp32<fp16<int8 | 0.293, 0.609, 0.766 | **PASS** |
| E78-R4 | fp32.ones | 8.051 vs 8.996 ± 1.0 | **PASS** |
| E78-R4 | fp32.randn | 24.002 vs 26.662 ± 1.5 | **FAIL** |
| E78-R4 | pi_builtin_vs_file | -0.064 vs 0 ± 0.25 | **PASS** |

Instrument checks (E78-R5): {"idle_consistency": {"median_abs_w": 0.07605560689006063, "ok": true}, "rail_tau": {"median_s": null, "ok": false}, "duty": {"min": 0.995908931919145, "max": 0.9964345764290732, "ok": true}, "carryover": {"slope_w_per_w": 0.002011143085612559, "se": 0.0005484879733822783, "n": 443, "ok": true}, "tie_dump": {"ok": true}}

## Q130(c), scored as its README and A1 say

- C-R1 fp32: out of sample 0.467 inside the frozen 95% (need 0.7) → **FAIL**; R1-A1 0.667 → FAIL; E78's secondary (intervals overlap) 0.533; all kinds 0.556 → FAIL
- C-R1 fp16: out of sample 0.857 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.857 → PASS; E78's secondary (intervals overlap) 0.857; all kinds 0.882 → PASS
- C-R1 int8: out of sample 0.846 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.846 → PASS; E78's secondary (intervals overlap) 1.000; all kinds 0.875 → PASS
- C-R2 fp32: rho 0.941 → **PASS** (all kinds 0.950)
- C-R2 fp16: rho 0.942 → **PASS** (all kinds 0.955)
- C-R2 int8: rho 0.867 → **FAIL** (all kinds 0.908)
- C-R3 fp16: sparse50 − wsparse50 6.250 W → **PASS**
- C-R3 int8: sparse50 − wsparse50 2.193 W → **PASS**; favours zero_products_unsigned
- C-R4: int8 ones − zeros 1.559 W → **PASS**
- C-R6: → **PASS** (random sign patterns against a constant (A1.6), not a product-sign price)
- C-R9: fp32 a_randn_b_zeros 0.643 W (pass 7810, run first: —) → selects the **gate** arm

## Q130(b) r2, errors in watts above fp32 zeros

- variant A fp32: rms 1.458 W, mean error -0.662 W, |z| ≤ 2 for 0.333 of 18
- variant A fp16: rms 1.481 W, mean error -1.036 W, |z| ≤ 2 for 0.235 of 17
- variant A int8: rms 8.140 W, mean error 6.359 W, |z| ≤ 2 for 0.000 of 16
- variant B fp32: rms 1.458 W, mean error -0.662 W, |z| ≤ 2 for 0.333 of 18
- variant B fp16: rms 1.113 W, mean error -0.549 W, |z| ≤ 2 for 0.353 of 17
- variant B int8: rms 8.762 W, mean error 6.955 W, |z| ≤ 2 for 0.000 of 16
- g per format on E78's anchors: {"fp32": {"g_w_per_live_slot_cycle_s": 1.7534077829815952e-12, "ratio_to_fp32": 1.0}, "fp16": {"g_w_per_live_slot_cycle_s": 1.7464777383888619e-12, "ratio_to_fp32": 0.9960476709069073}, "int8": {"g_w_per_live_slot_cycle_s": 1.9771004389095205e-13, "ratio_to_fp32": 0.11275759455952371}}

## Secondary (reported, not a rule): E78-R2 with Q130(c) times the September mid-band factor

Factor 1.0695 (= 1 / 0.935; the midpoint of the registered card band (aifoundry3 = 0.935 x card 1): E78-R2 again with Q130(c)'s aifoundry3 predictions divided by 0.935, reported only).

- fp32: rms 3.300 W over 15 kinds (bound 2.0 W): outside
- fp16: rms 2.826 W over 14 kinds (bound 2.0 W): outside
- int8: rms 1.210 W over 13 kinds (bound 1.0 W): outside

## Cross-card rules (E82 card 1 against E78 aifoundry3)

Band for D(aifoundry3)/D(card 1): [0.88, 0.99]. Passes: E82 [8210, 8211, 8212, 8213, 8214, 8215, 8216], E78 [7810, 7811, 7812, 7813, 7814, 7815].

| rule | statistic | verdict |
|---|---|---|
| X1 fp32 | Spearman rho 1.000 over 17 of 17 kinds (≥ 0.9) | **PASS** |
| X1 fp16 | Spearman rho 0.994 over 16 of 16 kinds (≥ 0.9) | **PASS** |
| X1 int8 | Spearman rho 1.000 over 15 of 15 kinds (≥ 0.9) | **PASS** |
| X2a | point ratio inside the band for 0.000 of 32 kinds (≥ 0.8) | **FAIL** |
| X2b | 95% interval overlaps the band for 0.094 of 32 kinds (≥ 0.8) | **FAIL** |
| X3 | median ratio 1.030 (IQR 1.025–1.034, 32 kinds) | **FAIL** |

Slope-sensitive verdicts (move at a registered leakage arm): none.


| kind | D card 1 (W) | ±95% | D aifoundry3 (W) | ±95% | ratio a3/c1 | ±95% | inside |
|---|---|---|---|---|---|---|---|
| fp16.fp8grid | 17.438 | 0.064 | 18.052 | 0.126 | 1.035 | 0.008 | False |
| fp16.neg_ones | 8.094 | 0.063 | 8.382 | 0.133 | 1.035 | 0.018 | False |
| fp16.nn_like | 17.010 | 0.104 | 17.602 | 0.118 | 1.035 | 0.009 | False |
| fp16.ones | 8.019 | 0.040 | 8.448 | 0.082 | 1.054 | 0.011 | False |
| fp16.pair_half_zero | 19.782 | 0.094 | 20.122 | 0.569 | 1.017 | 0.029 | False |
| fp16.randn | 21.490 | 0.058 | 22.162 | 0.054 | 1.031 | 0.004 | False |
| fp16.randn_small | 21.598 | 0.123 | 22.209 | 0.086 | 1.028 | 0.007 | False |
| fp16.randn_sorted | 20.219 | 0.091 | 20.748 | 0.426 | 1.026 | 0.022 | False |
| fp16.smallint | 16.437 | 0.077 | 17.000 | 0.302 | 1.034 | 0.019 | False |
| fp16.sparse50 | 13.081 | 0.042 | 13.196 | 0.540 | 1.009 | 0.041 | False |
| fp16.uniform01 | 18.846 | 0.068 | 19.426 | 0.086 | 1.031 | 0.006 | False |
| fp16.wsparse50 | 6.832 | 0.093 | 7.058 | 0.035 | 1.033 | 0.015 | False |
| fp32.bf16trunc | 17.606 | 0.072 | 18.136 | 0.046 | 1.030 | 0.005 | False |
| fp32.fp16grid | 19.155 | 0.106 | 19.624 | 0.065 | 1.024 | 0.007 | False |
| fp32.neg_ones | 7.943 | 0.143 | 8.143 | 0.408 | 1.025 | 0.055 | False |
| fp32.nn_like | 12.720 | 0.114 | 13.036 | 0.066 | 1.025 | 0.011 | False |
| fp32.ones | 8.051 | 0.156 | 8.257 | 0.221 | 1.026 | 0.034 | False |
| fp32.pi | 8.181 | 0.123 | 8.470 | 0.113 | 1.035 | 0.021 | False |
| fp32.pow2 | 13.658 | 0.051 | 13.985 | 0.159 | 1.024 | 0.012 | False |
| fp32.randn | 24.002 | 0.065 | 24.725 | 0.082 | 1.030 | 0.004 | False |
| fp32.randn_large | 23.962 | 0.143 | 24.711 | 0.084 | 1.031 | 0.007 | False |
| fp32.randn_small | 24.167 | 0.080 | 24.764 | 0.463 | 1.025 | 0.019 | False |
| fp32.randn_sorted | 22.787 | 0.151 | 23.384 | 0.376 | 1.026 | 0.018 | False |
| fp32.smallint | 13.665 | 0.080 | 14.079 | 0.058 | 1.030 | 0.007 | False |
| fp32.sparse50 | 7.029 | 0.183 | 7.302 | 0.063 | 1.039 | 0.028 | False |
| fp32.uniform01 | 21.953 | 0.136 | 22.646 | 0.093 | 1.032 | 0.008 | False |
| int8.full | 6.839 | 0.091 | 7.056 | 0.059 | 1.032 | 0.016 | False |
| int8.gauss_q | 6.483 | 0.028 | 6.598 | 0.069 | 1.018 | 0.012 | False |
| int8.smallint | 5.880 | 0.082 | 6.003 | 0.142 | 1.021 | 0.028 | False |
| int8.sorted | 6.399 | 0.113 | 6.588 | 0.073 | 1.030 | 0.021 | False |
| int8.sparse50 | 5.235 | 0.131 | 5.463 | 0.146 | 1.044 | 0.038 | False |
| int8.ternary | 4.990 | 0.143 | 5.186 | 0.051 | 1.039 | 0.032 | False |

Reported beside: {"zero_level_S_w": {"fp32": {"e82": 1.846120595606663, "e78": 1.9858230735486515}, "fp16": {"e82": 1.8896379920389221, "e78": 1.9872138279205274}, "int8": {"e82": 2.415680672268907, "e78": 2.605255386405539}}, "idle_level_w": {"e82": 33.09372854149494, "e78": 25.911429884364832}, "v_mean": {"e82": 0.49871828395061724, "e78": 0.5216593258274552}, "leak_k": {"e82": 0.25411764705882567, "e78": 0.19940337259099877}, "passes": {"e82": [8210, 8211, 8212, 8213, 8214, 8215, 8216], "e78": [7810, 7811, 7812, 7813, 7814, 7815]}}

E78's rule verdicts on the two cards: 31 of 33 the same; differing: {"/E78-R3f/cells/fp32.neg_ones - fp32.ones/verdict": {"e82": "PASS", "e78": "INCONCLUSIVE"}, "/E78-R4/fp32.randn/verdict": {"e82": "FAIL", "e78": "PASS"}}
