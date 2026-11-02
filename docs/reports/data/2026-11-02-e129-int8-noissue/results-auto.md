# E129 results (score_e129.py)

Reduction carrying the verdicts: primary; passes scored: 12910, 12911, 12912 (3).

| quantity | fp32 | int8 |
|---|---|---|
| U = -D(m0): issuing on zeros, W | +1.441 ± 0.104 | +0.446 ± 0.160 |
| e_op, pJ an op | +80.189 ± 43.236 | +77.231 ± 91.764 |
| S(m0) over idle, W | +0.089 ± 0.175 | +1.665 ± 0.069 |
| S(m0r1) over idle, W | +1.153 ± 0.112 | +2.019 ± 0.389 |
| D(m0r1) over the format's zeros, W | -0.400 ± 0.109 | -0.137 ± 0.294 |

| the gap and the one-row arm | W |
|---|---|
| G | +0.702 ± 0.102 |
| G_lane | -0.994 ± 0.099 |
| G_op | +0.059 ± 0.137 |
| G_rest | +1.637 ± 0.231 |
| N | +1.576 ± 0.124 |
| N1 | +0.865 ± 0.357 |
| N_minus_N1 | +0.710 ± 0.419 |
| e_op_diff_at_r1_rate_w | -0.029 ± 0.581 |

| rule | verdict |
|---|---|
| R1_ops | NOT-SCORED (fewer than 6 kept passes) |
| R2_lanes | LANES-OPPOSE |
| R3_per_time | PASS |
| R0_answer | PER-TIME |
| Y1_no_issue | PASS |
| Y2_per_op_ceiling | PASS |
| R6 m0.fp32.zeros | PASS (measured 544.001, predicted 544.0) |
| R6 m0.int8.zeros | PASS (measured 318.001, predicted 318.0) |
| R6 m0k8.fp32.zeros | PASS (measured 280.001, predicted 280.0) |
| R6 m0k8.int8.zeros | PASS (measured 166.0, predicted 166.0) |
| R6 m0r1.fp32.zeros | PASS (measured 62.0, predicted 62.0) |
| R6 m0r1.int8.zeros | PASS (measured 62.0, predicted 62.0) |
| V0_equal_rate | EQUAL-RATE |
| V1_one_row | INCONCLUSIVE |
| V2 bench at its constants, the card's order (TenC read at one frozen address in fp32 too) | N1 ABOVE (range [0.07043672644496139, 0.13992703362604592]) |
| V2 bench at its constants, from reset (TenC's reads int8's alone) | CONSISTENT (range [0.3961682523580256, 0.7934000095727048]) |
| V2 the TIMA controls alone at the cards' issue price (17.2 fJ a clocked bit, Q136(c) result 5b), 95% | CONSISTENT (range [0.4922961043131007, 1.4642113913290822]) |
| V2 all of N goes with work done every cycle (the r1/m0 ratio of the TIMA controls' or TenC's reads a second) | N1 BELOW (range [1.4069721206973385, 1.580784681655587]) |
| R10 m0.fp32.zeros | PASS (session -1.4405268780268419, reference -1.4566617816089789 ± 0.3) |
| R10 m0.int8.zeros | PASS (session -0.4464128654344061, reference -0.40143939858918287 ± 0.3) |
| R10 m0k8.fp32.zeros | PASS (session -1.355478080637243, reference -1.3596035258436814 ± 0.3) |
| R10 m0k8.int8.zeros | PASS (session -0.3103179788012653, reference -0.2528385147140835 ± 0.3) |
| R10 anchor_pi | PASS (session 8.21971715927751, reference 8.120581437908497 ± 0.5) |
| R10 gap G (S) | PASS (session 0.7019722222222265, reference 0.5477633333333316 ± 0.2) |
| R10 no-issue gap N (S) | PASS (session 1.5759024044786258, reference 1.5665500000000012 ± 0.5) |
