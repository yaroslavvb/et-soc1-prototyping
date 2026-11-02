# E109 results (score_e109.py)

Passes scored: 12410, 12411, 12412, 12413.

| quantity | fp32 | int8 |
|---|---|---|
| U = S(zeros) − S(m0): the lanes, W | +1.457 ± 0.142 | +0.401 ± 0.199 |
| P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W | +0.097 ± 0.107 | +0.149 ± 0.285 |
| e_op, pJ an op | +91.485 ± 100.691 | +84.311 ± 161.663 |
| D(k8), W | +0.045 ± 0.226 | +0.112 ± 0.170 |
| R = D(r8) − D(k8), W | +0.084 ± 0.132 | -0.048 ± 0.239 |
| r_B, pJ a B half-line read | +2.718 ± 4.124 | -0.187 ± 6.462 |
| U8 = D(k8) − D(m0k8), W | +1.404 ± 0.195 | +0.365 ± 0.193 |
| U8 − U × uops ratio, W | -0.006 ± 0.315 | -0.020 ± 0.371 |

| the gap | W |
|---|---|
| G | +0.548 ± 0.037 |
| G_lane | -1.055 ± 0.240 |
| G_op | +0.060 ± 0.370 |
| G_rest | +1.543 ± 0.634 |

| item 15 | W |
|---|---|
| R7 | +0.084 ± 0.127 |
| T_plus | +0.207 ± 0.087 |
| T_minus | +0.291 ± 0.040 |
| R8 | +0.643 ± 0.192 |
| L_gated | +2.099 ± 0.250 |
| L_live | +13.395 ± 0.187 |
| X | +5.275 ± 0.208 |
| D_a_nz_b_randn | +12.229 ± 0.082 |
| D_pi | +8.121 ± 0.064 |

| rule | verdict |
|---|---|
| R1_ops | INCONCLUSIVE |
| R2_lanes | LANES-OPPOSE |
| R3_per_time | PASS |
| R0_answer | PER-TIME |
| R4_b_reads | NOT-RESOLVED, H_reads CONSISTENT |
| R5 fp32 | INCONCLUSIVE |
| R5 int8 | INCONCLUSIVE |
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
| R10 fp32.randn D | PASS (session 23.909961176591917, E78 23.987 ± 0.6) |
| R10 fp16.randn D | PASS (session 21.48622273873576, E78 21.442 ± 0.6) |
| R10 int8.full D | PASS (session 6.979732644772802, E78 6.869 ± 0.3) |
| R10 anchor_pi D | PASS (session 8.120581437908497, E78 8.095 ± 0.5) |
| R10 fp32.a_zeros_b_randn D | PASS (session 0.8493704851788397, E78 0.723 ± 0.25) |
| R10 gap G (S) | PASS (session 0.5477633333333316, E78 0.561 ± 0.2) |
| R10 fp32.a_nz_b_randn D | PASS (session 12.229315794680996, E78 12.114 ± 0.5) |

Each reading at the measured rates, rms error over the eight item-11 arms (W): H_reads 0.631, H_ops 1.142, H_bench 0.425
