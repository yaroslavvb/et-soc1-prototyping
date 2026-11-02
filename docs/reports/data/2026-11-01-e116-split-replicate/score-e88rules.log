# E88 results (scored by score_e88.py)

Passes kept: [11611, 11612, 11613, 11614]; set aside: [{'pass': 11610, 'why': ['int8.zeros departs -0.316 W from its straight line']}]; tally {'PASS': 28, 'FAIL': 3, 'INCONCLUSIVE': 1, 'not scored': 0}

| contrast | what | D (W) ±95% | S (W) ±95% | pJ/MAC | predicted (W) |
|---|---|---|---|---|---|
| F32 | the clocked lane: constant operands, a frozen accumulator | 8.386 ± 0.116 | 8.345 ± 0.134 | 1.8263 | 7.56 [6.48, 8.65] |
| W32 | an all-equal accumulator walking (+1 a micro-op) against frozen | 0.026 ± 0.020 | 0.097 ± 0.120 | 0.0056 | 0.36 [-0.89, 1.62] |
| M32 | random positive operands, result frozen, against constants | 8.855 ± 0.112 | 8.900 ± 0.162 | 1.9287 | 9.72 [8.16, 11.27] |
| R32 | the same operands, the result walking against frozen | 5.032 ± 0.147 | 5.005 ± 0.126 | 1.0961 | 5.02 [3.45, 6.58] |
| R32bus | frozen accumulators that differ from each other against equal ones | 3.889 ± 0.106 | 3.835 ± 0.122 | 0.8472 | 4.75 [3.26, 6.24] |
| R32sum | walking against frozen-but-different accumulators | 1.143 ± 0.150 | 1.170 ± 0.126 | 0.2489 | 0.26 [-1.00, 1.52] |
| M32s | random signs only, result frozen, against constants | 2.627 ± 0.218 | 2.628 ± 0.223 | 0.5722 | 0.24 [-1.01, 1.50] |
| R32s | random signs, the result walking against frozen | 2.134 ± 0.153 | 2.182 ± 0.122 | 0.4648 | 3.69 [2.26, 5.12] |
| X32 | E78's random tile against r_walk (signs and the k = 0 slice) | 2.471 ± 0.113 | 2.457 ± 0.122 | 0.5383 | 1.48 [0.23, 2.74] |
| F16 | the clocked lane: constant operands, C frozen at 0 | 8.376 ± 0.065 | 8.382 ± 0.187 | 0.9121 | 7.53 [6.41, 8.65] |
| W16 | an all-equal accumulator walking (+2 a micro-op) against frozen | 0.018 ± 0.072 | 0.034 ± 0.173 | 0.0019 | 0.51 [-0.69, 1.71] |
| M16 | random operands, dot products cancel, against constants | 6.361 ± 0.145 | 6.346 ± 0.262 | 0.6928 | 5.64 [3.97, 7.30] |
| R16 | the same A, the result walking against cancelled | 6.508 ± 0.242 | 6.522 ± 0.163 | 0.7087 | 7.36 [5.56, 9.16] |
| A16 | two ways of freezing: absorbed against cancelled | 0.410 ± 0.133 | 0.382 ± 0.273 | 0.0447 | 0.13 [-1.07, 1.32] |
| R16abs | the same operands, walking against absorbed | 6.097 ± 0.173 | 6.141 ± 0.287 | 0.6640 | 7.23 [5.43, 9.03] |
| F8 | the clocked lane: constant operands, C frozen at 0 | 1.678 ± 0.176 | 1.702 ± 0.136 | 0.0532 | 1.36 [0.61, 2.11] |
| W8 | an all-equal accumulator walking (+4 a micro-op) against frozen | -0.104 ± 0.113 | -0.201 ± 0.295 | -0.0033 | 0.17 [-0.64, 0.99] |
| M8 | random operands, the four products cancel, against constants | 3.402 ± 0.151 | 3.342 ± 0.056 | 0.1079 | 2.12 [0.56, 3.69] |
| R8 | the same A, the result walking against cancelled | 1.964 ± 0.326 | 1.979 ± 0.160 | 0.0623 | 3.07 [1.46, 4.67] |

| rule | what | statistic ±95% | test | verdict |
|---|---|---|---|---|
| H1-fp32 | a constant's accumulator walk costs at most 1 W in fp32: the constant level is the clocked lane | 0.026 ± 0.020 | le 1.0 | **PASS** |
| H1-fp16 | the same in fp16 | 0.018 ± 0.072 | le 1.0 | **PASS** |
| H1-int8 | the same in int8 (at most 0.5 W) | -0.104 ± 0.113 | le 0.5 | **PASS** |
| H2-fp32 | the result path costs at least 2 W of fp32 random data with the operands held identical | 5.032 ± 0.147 | ge 2.0 | **PASS** |
| H2-fp16 | the same in fp16 (cancellation) | 6.508 ± 0.242 | ge 2.0 | **PASS** |
| H2-int8 | the same in int8, at least 1 W | 1.964 ± 0.326 | ge 1.0 | **PASS** |
| H3-fp32 | operand bits cost at least 4 W in fp32 with the result frozen | 8.855 ± 0.112 | ge 4.0 | **PASS** |
| H3-fp16 | at least 2 W in fp16 | 6.361 ± 0.145 | ge 2.0 | **PASS** |
| H3-int8 | at least 0.5 W in int8 | 3.402 ± 0.151 | ge 0.5 | **PASS** |
| H4-signs-mult | random signs alone cost at most 1 W with the result frozen (fp32) | 2.627 ± 0.218 | le 1.0 | **FAIL** |
| H4-signs-result | random signs cost at least 2 W more when the result walks (fp32) | 2.134 ± 0.153 | ge 2.0 | **INCONCLUSIVE** |
| H5-bus-share | at least 0.6 of the fp32 result path is the C read and result bus swinging between different accumulators (frozen-but-different over walking, both against frozen-and-equal) | 0.773 ± 0.025 | ge 0.6 | **PASS** |
| H6-two-freezes | fp16: an absorbed and a cancelled result cost the same within 1 W | 0.410 ± 0.133 | abs_le 1.0 | **PASS** |
| P-F32 | the E82-fitted model's F32: 7.56 W within +-1.09 W | 8.386 ± 0.116 | band [6.478, 8.649] | **PASS** |
| P-W32 | the E82-fitted model's W32: 0.37 W within +-1.26 W | 0.026 ± 0.020 | band [-0.89, 1.621] | **PASS** |
| P-M32 | the E82-fitted model's M32: 9.72 W within +-1.56 W | 8.855 ± 0.112 | band [8.159, 11.272] | **PASS** |
| P-R32 | the E82-fitted model's R32: 5.02 W within +-1.56 W | 5.032 ± 0.147 | band [3.453, 6.581] | **PASS** |
| P-R32bus | the E82-fitted model's R32bus: 4.75 W within +-1.49 W | 3.889 ± 0.106 | band [3.262, 6.243] | **PASS** |
| P-R32sum | the E82-fitted model's R32sum: 0.26 W within +-1.26 W | 1.143 ± 0.150 | band [-0.996, 1.525] | **PASS** |
| P-M32s | the E82-fitted model's M32s: 0.24 W within +-1.25 W | 2.627 ± 0.218 | band [-1.012, 1.496] | **FAIL** |
| P-R32s | the E82-fitted model's R32s: 3.69 W within +-1.43 W | 2.134 ± 0.153 | band [2.262, 5.124] | **FAIL** |
| P-X32 | the E82-fitted model's X32: 1.48 W within +-1.26 W | 2.471 ± 0.113 | band [0.225, 2.74] | **PASS** |
| P-F16 | the E82-fitted model's F16: 7.53 W within +-1.12 W | 8.376 ± 0.065 | band [6.408, 8.649] | **PASS** |
| P-W16 | the E82-fitted model's W16: 0.50 W within +-1.20 W | 0.018 ± 0.072 | band [-0.695, 1.705] | **PASS** |
| P-M16 | the E82-fitted model's M16: 5.64 W within +-1.66 W | 6.361 ± 0.145 | band [3.972, 7.301] | **PASS** |
| P-R16 | the E82-fitted model's R16: 7.36 W within +-1.80 W | 6.508 ± 0.242 | band [5.563, 9.156] | **PASS** |
| P-A16 | the E82-fitted model's A16: 0.13 W within +-1.20 W | 0.410 ± 0.133 | band [-1.07, 1.324] | **PASS** |
| P-R16abs | the E82-fitted model's R16abs: 7.23 W within +-1.80 W | 6.097 ± 0.173 | band [5.432, 9.031] | **PASS** |
| P-F8 | the E82-fitted model's F8: 1.36 W within +-0.75 W | 1.678 ± 0.176 | band [0.608, 2.11] | **PASS** |
| P-W8 | the E82-fitted model's W8: 0.17 W within +-0.82 W | -0.104 ± 0.113 | band [-0.642, 0.99] | **PASS** |
| P-M8 | the E82-fitted model's M8: 2.12 W within +-1.57 W | 3.402 ± 0.151 | band [0.558, 3.689] | **PASS** |
| P-R8 | the E82-fitted model's R8: 3.07 W within +-1.61 W | 1.964 ± 0.326 | band [1.456, 4.675] | **PASS** |

| format | part | D (W) ±95% | share of the total ±95% | pJ/MAC |
|---|---|---|---|---|
| fp32 | total (fp32.r_walk) | 22.273 ± 0.129 | 1 | |
| fp32 | i_clocked_lane | 8.386 ± 0.116 | 0.377 ± 0.004 | 1.8263 ± 0.0252 |
| fp32 | iii_operand_multiplier | 8.855 ± 0.112 | 0.398 ± 0.006 | 1.9287 ± 0.0243 |
| fp32 | ii_result_path | 5.032 ± 0.147 | 0.226 ± 0.006 | 1.0961 ± 0.0321 |
| fp16 | total (fp16.r_walk) | 21.244 ± 0.154 | 1 | |
| fp16 | i_clocked_lane | 8.376 ± 0.065 | 0.394 ± 0.003 | 0.9121 ± 0.0071 |
| fp16 | iii_operand_multiplier | 6.361 ± 0.145 | 0.299 ± 0.009 | 0.6928 ± 0.0158 |
| fp16 | ii_result_path | 6.508 ± 0.242 | 0.306 ± 0.009 | 0.7087 ± 0.0263 |
| int8 | total (int8.r_walk) | 7.046 ± 0.212 | 1 | |
| int8 | i_clocked_lane | 1.678 ± 0.176 | 0.239 ± 0.045 | 0.0532 ± 0.0056 |
| int8 | iii_operand_multiplier | 3.402 ± 0.151 | 0.482 ± 0.053 | 0.1079 ± 0.0048 |
| int8 | ii_result_path | 1.964 ± 0.326 | 0.279 ± 0.039 | 0.0623 ± 0.0103 |

Arms: dips-kept {'PASS': 26, 'FAIL': 3, 'INCONCLUSIVE': 3, 'not scored': 0}; leak0.545 {'PASS': 28, 'FAIL': 3, 'INCONCLUSIVE': 1, 'not scored': 0}; leak0.3803 {'PASS': 28, 'FAIL': 3, 'INCONCLUSIVE': 1, 'not scored': 0}; leak0 {'PASS': 29, 'FAIL': 3, 'INCONCLUSIVE': 0, 'not scored': 0}
Verdicts that move between arms: {'H1-fp32': {'dips-kept': 'INCONCLUSIVE'}, 'H5-bus-share': {'dips-kept': 'INCONCLUSIVE'}, 'H4-signs-result': {'leak0': 'PASS'}}
