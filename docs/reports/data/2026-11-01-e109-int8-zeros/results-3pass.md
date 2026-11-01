# E109 results (score_e109.py)

Passes scored: 10910, 10911, 10912.

| quantity | fp32 | int8 |
|---|---|---|
| U = S(zeros) − S(m0): the lanes, W | +1.507 ± 0.175 | +0.419 ± 0.079 |
| P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W | +0.040 ± 0.199 | +0.089 ± 0.093 |
| e_op, pJ an op | +37.867 ± 187.337 | +50.700 ± 52.671 |
| D(k8), W | -0.108 ± 0.273 | +0.120 ± 0.166 |
| R = D(r8) − D(k8), W | +0.212 ± 0.301 | -0.066 ± 0.191 |
| r_B, pJ a B half-line read | +6.517 ± 8.968 | -0.970 ± 4.356 |
| U8 = D(k8) − D(m0k8), W | +1.359 ± 0.011 | +0.450 ± 0.170 |
| U8 − U × uops ratio, W | -0.101 ± 0.182 | +0.048 ± 0.101 |

| the gap | W |
|---|---|
| G | +0.600 ± 0.115 |
| G_lane | -1.088 ± 0.096 |
| G_op | +0.055 ± 0.184 |
| G_rest | +1.633 ± 0.148 |

| item 15 | W |
|---|---|
| R7 | +0.022 ± 0.037 |
| T_plus | +0.205 ± 0.247 |
| T_minus | +0.226 ± 0.284 |
| R8 | +0.593 ± 0.306 |
| L_gated | +2.101 ± 0.386 |
| L_live | +13.871 ± 0.417 |
| X | +5.429 ± 0.475 |
| D_a_nz_b_randn | +12.590 ± 0.088 |
| D_pi | +8.442 ± 0.135 |

| rule | verdict |
|---|---|
| R1_ops | FAIL |
| R2_lanes | LANES-OPPOSE |
| R3_per_time | PASS |
| R0_answer | PER-TIME |
| R4_b_reads | NOT-RESOLVED, H_reads CONSISTENT |
| R5 fp32 | INCONCLUSIVE |
| R5 int8 | PASS |
| R6 m0.fp32.zeros | PASS (measured 544.001, predicted 544.0) |
| R6 k8.fp32.zeros | PASS (measured 282.001, predicted 282.0) |
| R6 r8.fp32.zeros | PASS (measured 290.001, predicted 290.0) |
| R6 m0k8.fp32.zeros | PASS (measured 280.001, predicted 280.0) |
| R6 m0.int8.zeros | PASS (measured 318.001, predicted 318.0) |
| R6 k8.int8.zeros | PASS (measured 166.0, predicted 166.0) |
| R6 r8.int8.zeros | PASS (measured 190.0, predicted 190.0) |
| R6 m0k8.int8.zeros | PASS (measured 166.0, predicted 166.0) |
| R6 m0.fp32.a_zeros_b_randn | PASS (measured 544.001, predicted 544.0) |
| R6 m0.fp32.a_nz_b_randn | PASS (measured 544.001, predicted 544.0) |
| R7_sign_unseen | PASS |
| R8_gated_transport | FAIL |
| R10 fp32.randn D | PASS (session 24.798183083593102, E78 24.725 ± 0.6) |
| R10 fp16.randn D | PASS (session 22.292858530423263, E78 22.162 ± 0.6) |
| R10 int8.full D | PASS (session 7.139641232622261, E78 7.056 ± 0.3) |
| R10 anchor_pi D | PASS (session 8.441887092339002, E78 8.360 ± 0.5) |
| R10 fp32.a_zeros_b_randn D | PASS (session 0.7980360499302558, E78 0.810 ± 0.25) |
| R10 gap G (S) | PASS (session 0.60019170837229, E78 0.619 ± 0.2) |

Each reading at the measured rates, rms error over the eight item-11 arms (W): H_reads 0.666, H_ops 1.193, H_bench 0.463
