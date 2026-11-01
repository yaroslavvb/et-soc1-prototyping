# E109 results (score_e109.py)

Passes scored: 10910, 10911.

| quantity | fp32 | int8 |
|---|---|---|
| U = S(zeros) − S(m0): the lanes, W | +1.486 ± 0.767 | +0.409 ± 0.334 |
| P = D(m0k8) − D(m0): the op rate ×1.9 with no lanes, W | +0.001 ± 0.532 | +0.071 ± 0.235 |
| e_op, pJ an op | +0.747 ± 500.649 | +40.045 ± 132.602 |
| D(k8), W | -0.125 ± 1.346 | +0.101 ± 0.737 |
| R = D(r8) − D(k8), W | +0.222 ± 1.522 | -0.044 ± 0.840 |
| r_B, pJ a B half-line read | +6.779 ± 45.501 | -0.568 ± 20.451 |
| U8 = D(k8) − D(m0k8), W | +1.361 ± 0.047 | +0.439 ± 0.836 |
| U8 − U × uops ratio, W | -0.079 ± 0.797 | +0.048 ± 0.515 |

| the gap | W |
|---|---|
| G | +0.622 ± 0.340 |
| G_lane | -1.077 ± 0.434 |
| G_op | +0.076 ± 0.817 |
| G_rest | +1.623 ± 0.723 |

| item 15 | W |
|---|---|
| R7 | +0.029 ± 0.102 |
| T_plus | +0.256 ± 0.571 |
| T_minus | +0.285 ± 0.673 |
| R8 | +0.526 ± 0.476 |
| L_gated | +2.012 ± 0.292 |
| L_live | +13.774 ± 0.137 |
| X | +5.321 ± 0.505 |
| D_a_nz_b_randn | +12.573 ± 0.232 |
| D_pi | +8.453 ± 0.643 |

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
| R8_gated_transport | INCONCLUSIVE |
| R10 fp32.randn D | PASS (session 24.927399642824234, E78 24.725 ± 0.6) |
| R10 fp16.randn D | PASS (session 22.403695568230827, E78 22.162 ± 0.6) |
| R10 int8.full D | PASS (session 7.163597609583201, E78 7.056 ± 0.3) |
| R10 anchor_pi D | PASS (session 8.453157654127486, E78 8.360 ± 0.5) |
| R10 fp32.a_zeros_b_randn D | PASS (session 0.7815012554143248, E78 0.810 ± 0.25) |
| R10 gap G (S) | PASS (session 0.6218609369557657, E78 0.619 ± 0.2) |

Each reading at the measured rates, rms error over the eight item-11 arms (W): H_reads 0.665, H_ops 1.198, H_bench 0.462
