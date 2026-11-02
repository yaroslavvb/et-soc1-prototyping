# E127: the float B-lane gate held steady against switching it, at equal operand activity: results
Written by `tools/claims-v3/e127/score_e127.py` from `e127.json` (footing a3, the registered reading). Kept passes: [12710, 12711, 12712, 12713, 12714]; set aside: []; reducer arm: dips removed (E82 A2).

## Rules

| rule | verdict | what |
|---|---|---|
| E127-R1 | **PASS** | measured_w +1.956; ci95_w +0.064; excess_w +1.173 |
| E127-R2 | **GATE** | excess_w +1.154; excess_lo95 +1.050; excess_hi95 +1.257; line_w +0.587; reference_excess_w +1.173; ratio 0.98 [0.90, 1.06] |
| E127-R3 | **GATE** | excess_w +1.129; excess_lo95 +1.040; excess_hi95 +1.219; line_w +0.646; reference_excess_w +1.292; ratio 0.87 [0.76, 0.99] |
| E127-R4 | **PER-LANE** | excess_w +0.879; excess_lo95 +0.741; excess_hi95 +1.018; line_w +0.587; reference_excess_w +1.173; ratio 0.75 [0.62, 0.88] |
| E127-R4q | **PER-LANE** | excess_w +0.810; excess_lo95 +0.716; excess_hi95 +0.904; line_w +0.577; reference_excess_w +1.154; ratio 0.70 [0.66, 0.74] |
| E127-R5 | **SHORT** | excess_w +0.358; excess_lo95 +0.285; excess_hi95 +0.431; line_w +0.577; reference_excess_w +1.154; ratio 0.31 [0.23, 0.39] |
| E127-R6 | **PASS** | measured_w +0.135; ci95_w +0.100 |
| E127-S1 | **PASS** |  |

## Contrasts (W; measured is the mean over kept passes of D(plus) - D(minus) inside each pass, 95% t)

| contrast | measured | M5 [95%] | excess over M5 | M4 | verdict |
|---|---:|---:|---:|---:|---|
| `B1: fp32.g_blanes_alt - fp32.g_blanes_steady` | +1.956 +- 0.064 | +0.783 [+0.229, +1.337] | +1.173 [+1.110, +1.237] | +0.727 | ABOVE |
| `B2: fp32.g_blanes_chk - fp32.g_blanes_alt` | +0.639 +- 0.156 | +0.932 [+0.369, +1.496] | -0.294 [-0.449, -0.138] | +0.936 | INSIDE |
| `B3: fp32.g_blanes_chk - fp32.g_blanes_steady` | +2.595 +- 0.139 | +1.715 [+1.161, +2.269] | +0.879 [+0.741, +1.018] | +1.664 | ABOVE |
| `F1: fp16.g_blanes_alt - fp16.g_blanes_steady` | +1.783 +- 0.145 | +0.491 [-0.011, +0.993] | +1.292 [+1.147, +1.438] | +0.432 | ABOVE |
| `F2: fp16.q_alt - fp16.q_steady` | +0.705 +- 0.089 | -0.424 [-0.897, +0.049] | +1.129 [+1.040, +1.219] | -0.461 | ABOVE |
| `F3: fp16.q_chk - fp16.q_steady` | +1.338 +- 0.136 | +0.508 [+0.034, +0.982] | +0.830 [+0.694, +0.966] | +0.475 | ABOVE |
| `Q1: fp32.q_alt - fp32.q_steady` | +0.687 +- 0.104 | -0.467 [-0.996, +0.062] | +1.154 [+1.050, +1.257] | -0.501 | ABOVE |
| `Q2: fp32.q_chk - fp32.q_steady` | +1.275 +- 0.094 | +0.465 [-0.065, +0.994] | +0.810 [+0.716, +0.904] | +0.435 | ABOVE |
| `Q3: fp32.q_alt - fp32.q_chk` | -0.588 +- 0.051 | -0.932 [-1.461, -0.402] | +0.344 [+0.292, +0.395] | -0.936 | INSIDE |
| `Q4: fp32.q_blk - fp32.q_steady` | -0.472 +- 0.073 | -0.830 [-1.358, -0.301] | +0.358 [+0.285, +0.431] | -0.840 | INSIDE |
| `Q5: fp32.q_steady_hi - fp32.q_steady` | +0.135 +- 0.100 | -0.005 [-0.534, +0.524] | +0.140 [+0.040, +0.240] | -0.004 | INSIDE |

## Tiles (D over the type's zeros, W, 95% over kept passes)

| tile | family | D | M5 [95%] | D - M5 | inside | M4 | D - M4 |
|---|---|---:|---:|---:|---|---:|---:|
| `fp16.g_blanes_alt` | bridge | 13.279 +- 0.093 | 12.443 [12.085, 12.802] | +0.836 | no | 12.459 | +0.820 |
| `fp16.g_blanes_steady` | random | 11.496 +- 0.145 | 11.952 [11.601, 12.303] | -0.456 | no | 12.026 | -0.530 |
| `fp16.q_alt` | quiet | 5.469 +- 0.109 | 4.551 [4.216, 4.885] | +0.918 | no | 4.565 | +0.904 |
| `fp16.q_chk` | quiet | 6.102 +- 0.085 | 5.483 [5.147, 5.818] | +0.619 | no | 5.501 | +0.601 |
| `fp16.q_steady` | quiet | 4.764 +- 0.069 | 4.975 [4.640, 5.310] | -0.211 | yes | 5.026 | -0.262 |
| `fp32.g_blanes_alt` | bridge | 14.537 +- 0.067 | 13.999 [13.600, 14.397] | +0.538 | no | 13.937 | +0.600 |
| `fp32.g_blanes_chk` | random | 15.175 +- 0.130 | 14.931 [14.533, 15.329] | +0.244 | yes | 14.873 | +0.302 |
| `fp32.g_blanes_steady` | bridge | 12.581 +- 0.016 | 13.216 [12.830, 13.601] | -0.635 | no | 13.209 | -0.629 |
| `fp32.q_alt` | quiet | 5.405 +- 0.106 | 4.509 [4.135, 4.883] | +0.896 | no | 4.527 | +0.878 |
| `fp32.q_blk` | quiet | 4.246 +- 0.080 | 4.147 [3.773, 4.520] | +0.100 | yes | 4.187 | +0.059 |
| `fp32.q_chk` | quiet | 5.993 +- 0.116 | 5.441 [5.066, 5.816] | +0.552 | no | 5.463 | +0.530 |
| `fp32.q_steady` | quiet | 4.718 +- 0.045 | 4.976 [4.602, 5.350] | -0.258 | yes | 5.028 | -0.310 |
| `fp32.q_steady_hi` | quiet | 4.853 +- 0.094 | 4.972 [4.598, 5.346] | -0.118 | yes | 5.024 | -0.170 |

## Beside the primary

| reading | E127-R1 | E127-R2 | E127-R3 | E127-R4 | E127-R4q | E127-R5 | E127-R6 | E127-S1 |
|---|---|---|---|---|---|---|---|---|
| anchor footing | PASS | GATE | GATE | PER-LANE | PER-LANE | SHORT | PASS | PASS |
| dips_kept | INCONCLUSIVE | NOT SCORED | GATE | NOT SCORED | NOT SCORED | NOT SCORED | INCONCLUSIVE | PASS |
| leak0.1994 | PASS | GATE | GATE | PER-LANE | PER-LANE | SHORT | PASS | PASS |
| leak0.3803 | PASS | GATE | GATE | PER-LANE | PER-LANE | INCONCLUSIVE | INCONCLUSIVE | PASS |
| leak0 | PASS | GATE | GATE | PER-LANE | PER-LANE | SHORT | INCONCLUSIVE | FAIL |
| gates_off | PASS | GATE | GATE | PER-LANE | PER-LANE | SHORT | PASS | PASS |
