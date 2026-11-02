# E109 results (score_e109.py)

Passes scored: 12410, 12411, 12412, 12413.

| quantity | fp32 | int8 |
|---|---|---|
| U = S(zeros) − S(m0): the lanes, W | +1.457 ± 0.187 | +0.394 ± 0.199 |
| P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W | +0.101 ± 0.143 | +0.137 ± 0.253 |
| e_op, pJ an op | +94.789 ± 135.053 | +77.996 ± 143.652 |
| D(k8), W | +0.060 ± 0.245 | +0.112 ± 0.184 |
| R = D(r8) − D(k8), W | +0.066 ± 0.111 | -0.060 ± 0.264 |
| r_B, pJ a B half-line read | +2.196 ± 3.565 | -0.540 ± 7.021 |
| U8 = D(k8) − D(m0k8), W | +1.416 ± 0.233 | +0.369 ± 0.190 |
| U8 − U × uops ratio, W | +0.005 ± 0.362 | -0.008 ± 0.372 |

| the gap | W |
|---|---|
| G | +0.561 ± 0.029 |
| G_lane | -1.063 ± 0.299 |
| G_op | +0.044 ± 0.396 |
| G_rest | +1.580 ± 0.696 |

| item 15 | W |
|---|---|
| R7 | +0.093 ± 0.148 |
| T_plus | +0.187 ± 0.111 |
| T_minus | +0.281 ± 0.057 |
| R8 | +0.689 ± 0.220 |
| L_gated | +2.145 ± 0.241 |
| L_live | +13.492 ± 0.220 |
| X | +5.297 ± 0.247 |
| D_a_nz_b_randn | +12.316 ± 0.084 |
| D_pi | +8.195 ± 0.063 |

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
| R10 fp32.randn D | PASS (session 24.056469827187502, E78 23.987 ± 0.6) |
| R10 fp16.randn D | PASS (session 21.625172334799156, E78 21.442 ± 0.6) |
| R10 int8.full D | PASS (session 7.02063021608826, E78 6.869 ± 0.3) |
| R10 anchor_pi D | PASS (session 8.19527454274721, E78 8.095 ± 0.5) |
| R10 fp32.a_zeros_b_randn D | PASS (session 0.8759162206759612, E78 0.723 ± 0.25) |
| R10 gap G (S) | PASS (session 0.5605208333333327, E78 0.561 ± 0.2) |
| R10 fp32.a_nz_b_randn D | PASS (session 12.315813838100066, E78 12.114 ± 0.5) |

Each reading at the measured rates, rms error over the eight item-11 arms (W): H_reads 0.630, H_ops 1.142, H_bench 0.424
