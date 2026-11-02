# E127: frozen predictions (M5 and M4, aifoundry3 card 0, a3 footing)

Written by `make_predictions_e127.py`. D in W over the type's own zeros at 600 MHz. The commit holding this file is the freeze; no card had run a new E127 tile.

| tile | family | b-bus bits/op | gate flips/op | live lanes/micro-op | **M5 [95%]** | M4 [95%] | M5 clk term | M5 bus term |
|---|---|---:|---:|---|---:|---:|---:|---:|
| `fp16.g_blanes_alt` | bridge | 70,112 | 4,096 | [0, 8] | **12.44** [12.08, 12.80] | 12.46 [12.10, 12.82] | 3.92 | 1.18 |
| `fp16.g_blanes_steady` | random | 29,446 | 0 | [4] | **11.95** [11.60, 12.30] | 12.03 [11.66, 12.39] | 4.78 | 0.54 |
| `fp16.q_alt` | quiet | 4,096 | 4,096 | [0, 8] | **4.55** [4.22, 4.89] | 4.56 [4.21, 4.92] | 4.00 | 0.14 |
| `fp16.q_chk` | quiet | 4,096 | 4,096 | [4] | **5.48** [5.15, 5.82] | 5.50 [5.14, 5.86] | 4.85 | 0.14 |
| `fp16.q_steady` | quiet | 4,096 | 0 | [4] | **4.97** [4.64, 5.31] | 5.03 [4.67, 5.38] | 4.85 | 0.04 |
| `fp32.g_blanes_alt` | bridge | 73,024 | 4,096 | [0, 8] | **14.00** [13.60, 14.40] | 13.94 [13.57, 14.30] | 3.93 | 1.22 |
| `fp32.g_blanes_chk` | random | 73,024 | 4,096 | [4] | **14.93** [14.53, 15.33] | 14.87 [14.51, 15.24] | 4.78 | 1.22 |
| `fp32.g_blanes_steady` | bridge | 28,066 | 0 | [4] | **13.22** [12.83, 13.60] | 13.21 [12.84, 13.58] | 4.78 | 0.52 |
| `fp32.q_alt` | quiet | 4,096 | 4,096 | [0, 8] | **4.51** [4.14, 4.88] | 4.53 [4.17, 4.88] | 4.00 | 0.14 |
| `fp32.q_blk` | quiet | 4,096 | 128 | [0, 8] | **4.15** [3.77, 4.52] | 4.19 [3.83, 4.54] | 4.02 | 0.05 |
| `fp32.q_chk` | quiet | 4,096 | 4,096 | [4] | **5.44** [5.07, 5.82] | 5.46 [5.11, 5.82] | 4.86 | 0.14 |
| `fp32.q_steady` | quiet | 4,096 | 0 | [4] | **4.98** [4.60, 5.35] | 5.03 [4.67, 5.39] | 4.86 | 0.04 |
| `fp32.q_steady_hi` | quiet | 4,096 | 0 | [4] | **4.97** [4.60, 5.35] | 5.02 [4.67, 5.38] | 4.86 | 0.04 |

| contrast | isolates | **M5 [95%]** | M4 | M5 terms (W) |
|---|---|---:|---:|---|
| `B1: fp32.g_blanes_alt - fp32.g_blanes_steady` | random data: every lane flipping each cycle against lanes 0-3 held off (E115's registered contrast, unequal bus) | **+0.78** [+0.23, +1.34] | +0.73 | mult +0.27, bus +0.69, rest +0.68, clk -0.86 |
| `B2: fp32.g_blanes_chk - fp32.g_blanes_alt` | random data, equal operand bus and products: four live lanes in every micro-op against all-off / all-live micro-ops | **+0.93** [+0.37, +1.50] | +0.94 | rest +0.08, clk +0.86 |
| `B3: fp32.g_blanes_chk - fp32.g_blanes_steady` | random data: every lane flipping each cycle with four live per micro-op, against lanes 0-3 held off | **+1.72** [+1.16, +2.27] | +1.66 | mult +0.27, bus +0.69, rest +0.76 |
| `Q1: fp32.q_alt - fp32.q_steady` | data held still, equal bus bits: every lane flipping each cycle (all-off / all-live micro-ops) against lanes 0-3 held off | **-0.47** [-1.00, +0.06] | -0.50 | bus +0.10, rest +0.29, clk -0.86 |
| `Q2: fp32.q_chk - fp32.q_steady` | data held still: every lane flipping each cycle with four live per micro-op, against lanes 0-3 held off | **+0.46** [-0.06, +0.99] | +0.44 | bus +0.10, rest +0.36 |
| `Q3: fp32.q_alt - fp32.q_chk` | data held still, equal flipping: all-off / all-live micro-ops against four live in every micro-op | **-0.93** [-1.46, -0.40] | -0.94 | rest -0.08, clk -0.86 |
| `Q4: fp32.q_blk - fp32.q_steady` | data held still: lanes off and on in 32-cycle stretches against lanes 0-3 held off | **-0.83** [-1.36, -0.30] | -0.84 | rest +0.01, clk -0.84 |
| `Q5: fp32.q_steady_hi - fp32.q_steady` | data held still: lanes 4-7 held off against lanes 0-3 held off (lane position) | **-0.00** [-0.53, +0.52] | -0.00 |  |
| `F1: fp16.g_blanes_alt - fp16.g_blanes_steady` | fp16, random data: every lane flipping each cycle against lanes 0-3 held off | **+0.49** [-0.01, +0.99] | +0.43 | mult +0.09, add16 -0.01, bus +0.65, rest +0.62, clk -0.86 |
| `F2: fp16.q_alt - fp16.q_steady` | fp16, data held still: every lane flipping each cycle (all-off / all-live) against lanes 0-3 held off | **-0.42** [-0.90, +0.05] | -0.46 | bus +0.10, rest +0.33, clk -0.86 |
| `F3: fp16.q_chk - fp16.q_steady` | fp16, data held still: every lane flipping each cycle, four live per micro-op, against lanes 0-3 held off | **+0.51** [+0.03, +0.98] | +0.47 | bus +0.10, rest +0.41 |
