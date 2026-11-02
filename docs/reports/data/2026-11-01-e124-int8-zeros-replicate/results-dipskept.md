# E109 results (score_e109.py)

Passes scored: 12411, 12413.

| quantity | fp32 | int8 |
|---|---|---|
| U = S(zeros) − S(m0): the lanes, W | +1.382 ± 0.177 | +0.422 ± 0.054 |
| P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W | +0.042 ± 0.266 | +0.173 ± 0.680 |
| e_op, pJ an op | +39.500 ± 250.624 | +98.291 ± 386.076 |
| D(k8), W | +0.140 ± 1.225 | +0.057 ± 1.118 |
| R = D(r8) − D(k8), W | +0.032 ± 0.223 | +0.005 ± 1.541 |
| r_B, pJ a B half-line read | +1.044 ± 7.273 | +1.149 ± 30.901 |
| U8 = D(k8) − D(m0k8), W | +1.480 ± 1.314 | +0.305 ± 0.492 |
| U8 − U × uops ratio, W | +0.142 ± 1.481 | -0.099 ± 0.441 |

| the gap | W |
|---|---|
| G | +0.534 ± 0.148 |
| G_lane | -0.961 ± 0.231 |
| G_op | +0.145 ± 1.024 |
| G_rest | +1.349 ± 1.403 |

| item 15 | W |
|---|---|
| R7 | +0.033 ± 0.664 |
| T_plus | +0.243 ± 0.471 |
| T_minus | +0.276 ± 0.193 |
| R8 | +0.656 ± 1.624 |
| L_gated | +2.038 ± 1.801 |
| L_live | +13.210 ± 1.406 |
| X | +5.244 ± 0.441 |
| D_a_nz_b_randn | +12.103 ± 1.422 |
| D_pi | +7.966 ± 1.847 |

| rule | verdict |
|---|---|
| R1_ops | INCONCLUSIVE |
| R2_lanes | LANES-OPPOSE |
| R3_per_time | INCONCLUSIVE |
| R0_answer | MIXED |
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
| R7_sign_unseen | INCONCLUSIVE |
| R8_gated_transport | INCONCLUSIVE |
| R10 fp32.randn D | PASS (session 23.918683107682863, E78 23.987 ± 0.6) |
| R10 fp16.randn D | PASS (session 21.466373234566216, E78 21.442 ± 0.6) |
| R10 int8.full D | PASS (session 7.0094301217652655, E78 6.869 ± 0.3) |
| R10 anchor_pi D | PASS (session 7.965905000000001, E78 8.095 ± 0.5) |
| R10 fp32.a_zeros_b_randn D | PASS (session 0.8983500000000078, E78 0.723 ± 0.25) |
| R10 gap G (S) | PASS (session 0.5335499999999957, E78 0.561 ± 0.2) |
| R10 fp32.a_nz_b_randn D | PASS (session 12.103362378835676, E78 12.114 ± 0.5) |

Each reading at the measured rates, rms error over the eight item-11 arms (W): H_reads 0.612, H_ops 1.127, H_bench 0.410
