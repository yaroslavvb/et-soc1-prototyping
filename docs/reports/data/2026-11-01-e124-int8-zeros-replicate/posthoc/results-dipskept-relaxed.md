# E109 results (score_e109.py)

Passes scored: 12410, 12411, 12413.

| quantity | fp32 | int8 |
|---|---|---|
| U = S(zeros) − S(m0): the lanes, W | +1.440 ± 0.252 | +0.458 ± 0.159 |
| P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W | +0.073 ± 0.146 | +0.227 ± 0.266 |
| e_op, pJ an op | +69.280 ± 137.195 | +128.654 ± 150.893 |
| D(k8), W | +0.059 ± 0.424 | +0.075 ± 0.231 |
| R = D(r8) − D(k8), W | +0.089 ± 0.250 | +0.009 ± 0.302 |
| r_B, pJ a B half-line read | +2.839 ± 7.852 | +1.560 ± 6.296 |
| U8 = D(k8) − D(m0k8), W | +1.425 ± 0.349 | +0.306 ± 0.096 |
| U8 − U × uops ratio, W | +0.031 ± 0.560 | -0.133 ± 0.171 |

| the gap | W |
|---|---|
| G | +0.538 ± 0.034 |
| G_lane | -0.982 ± 0.101 |
| G_op | +0.170 ± 0.227 |
| G_rest | +1.349 ± 0.274 |

| item 15 | W |
|---|---|
| R7 | +0.054 ± 0.159 |
| T_plus | +0.226 ± 0.117 |
| T_minus | +0.280 ± 0.043 |
| R8 | +0.671 ± 0.324 |
| L_gated | +2.111 ± 0.473 |
| L_live | +13.330 ± 0.584 |
| X | +5.319 ± 0.333 |
| D_a_nz_b_randn | +12.170 ± 0.399 |
| D_pi | +8.011 ± 0.410 |

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
| R10 fp32.randn D | PASS (session 23.921987879926817, E78 23.987 ± 0.6) |
| R10 fp16.randn D | PASS (session 21.30827477611365, E78 21.442 ± 0.6) |
| R10 int8.full D | PASS (session 7.031127198271361, E78 6.869 ± 0.3) |
| R10 anchor_pi D | PASS (session 8.010806666666666, E78 8.095 ± 0.5) |
| R10 fp32.a_zeros_b_randn D | PASS (session 0.8969980285015898, E78 0.723 ± 0.25) |
| R10 gap G (S) | PASS (session 0.5375088888888844, E78 0.561 ± 0.2) |
| R10 fp32.a_nz_b_randn D | PASS (session 12.169758252557116, E78 12.114 ± 0.5) |

Each reading at the measured rates, rms error over the eight item-11 arms (W): H_reads 0.631, H_ops 1.141, H_bench 0.428
