# E88 results (scored by score_e88.py)

Passes kept: [8810, 8811, 8812, 8814, 8815]; set aside: [{'pass': 8813, 'why': ['fp16.zeros departs -0.297 W from its straight line']}]; tally {'PASS': 29, 'FAIL': 3, 'INCONCLUSIVE': 0, 'not scored': 0}

| contrast | what | D (W) ±95% | S (W) ±95% | pJ/MAC | predicted (W) |
|---|---|---|---|---|---|
| F32 | the clocked lane: constant operands, a frozen accumulator | 7.922 ± 0.181 | 7.910 ± 0.199 | 1.7254 | 7.56 [6.48, 8.65] |
| W32 | an all-equal accumulator walking (+1 a micro-op) against frozen | 0.100 ± 0.311 | 0.112 ± 0.149 | 0.0217 | 0.36 [-0.89, 1.62] |
| M32 | random positive operands, result frozen, against constants | 8.614 ± 0.175 | 8.746 ± 0.239 | 1.8759 | 9.72 [8.16, 11.27] |
| R32 | the same operands, the result walking against frozen | 5.042 ± 0.193 | 4.846 ± 0.123 | 1.0979 | 5.02 [3.45, 6.58] |
| R32bus | frozen accumulators that differ from each other against equal ones | 3.801 ± 0.168 | 3.664 ± 0.090 | 0.8279 | 4.75 [3.26, 6.24] |
| R32sum | walking against frozen-but-different accumulators | 1.241 ± 0.106 | 1.181 ± 0.156 | 0.2703 | 0.26 [-1.00, 1.52] |
| M32s | random signs only, result frozen, against constants | 2.524 ± 0.185 | 2.527 ± 0.319 | 0.5496 | 0.24 [-1.01, 1.50] |
| R32s | random signs, the result walking against frozen | 2.259 ± 0.158 | 2.324 ± 0.251 | 0.4920 | 3.69 [2.26, 5.12] |
| X32 | E78's random tile against r_walk (signs and the k = 0 slice) | 2.241 ± 0.173 | 2.273 ± 0.112 | 0.4879 | 1.48 [0.23, 2.74] |
| F16 | the clocked lane: constant operands, C frozen at 0 | 7.955 ± 0.143 | 7.931 ± 0.131 | 0.8662 | 7.53 [6.41, 8.65] |
| W16 | an all-equal accumulator walking (+2 a micro-op) against frozen | 0.014 ± 0.127 | -0.049 ± 0.069 | 0.0015 | 0.51 [-0.69, 1.71] |
| M16 | random operands, dot products cancel, against constants | 6.190 ± 0.168 | 6.221 ± 0.115 | 0.6742 | 5.64 [3.97, 7.30] |
| R16 | the same A, the result walking against cancelled | 6.289 ± 0.208 | 6.381 ± 0.046 | 0.6850 | 7.36 [5.56, 9.16] |
| A16 | two ways of freezing: absorbed against cancelled | 0.388 ± 0.111 | 0.344 ± 0.209 | 0.0422 | 0.13 [-1.07, 1.32] |
| R16abs | the same operands, walking against absorbed | 5.901 ± 0.144 | 6.037 ± 0.232 | 0.6426 | 7.23 [5.43, 9.03] |
| F8 | the clocked lane: constant operands, C frozen at 0 | 1.710 ± 0.135 | 1.698 ± 0.101 | 0.0542 | 1.36 [0.61, 2.11] |
| W8 | an all-equal accumulator walking (+4 a micro-op) against frozen | -0.231 ± 0.249 | -0.177 ± 0.194 | -0.0073 | 0.17 [-0.64, 0.99] |
| M8 | random operands, the four products cancel, against constants | 3.145 ± 0.212 | 3.240 ± 0.102 | 0.0997 | 2.12 [0.56, 3.69] |
| R8 | the same A, the result walking against cancelled | 1.809 ± 0.263 | 1.820 ± 0.282 | 0.0574 | 3.07 [1.46, 4.67] |

| rule | what | statistic ±95% | test | verdict |
|---|---|---|---|---|
| H1-fp32 | a constant's accumulator walk costs at most 1 W in fp32: the constant level is the clocked lane | 0.100 ± 0.311 | le 1.0 | **PASS** |
| H1-fp16 | the same in fp16 | 0.014 ± 0.127 | le 1.0 | **PASS** |
| H1-int8 | the same in int8 (at most 0.5 W) | -0.231 ± 0.249 | le 0.5 | **PASS** |
| H2-fp32 | the result path costs at least 2 W of fp32 random data with the operands held identical | 5.042 ± 0.193 | ge 2.0 | **PASS** |
| H2-fp16 | the same in fp16 (cancellation) | 6.289 ± 0.208 | ge 2.0 | **PASS** |
| H2-int8 | the same in int8, at least 1 W | 1.809 ± 0.263 | ge 1.0 | **PASS** |
| H3-fp32 | operand bits cost at least 4 W in fp32 with the result frozen | 8.614 ± 0.175 | ge 4.0 | **PASS** |
| H3-fp16 | at least 2 W in fp16 | 6.190 ± 0.168 | ge 2.0 | **PASS** |
| H3-int8 | at least 0.5 W in int8 | 3.145 ± 0.212 | ge 0.5 | **PASS** |
| H4-signs-mult | random signs alone cost at most 1 W with the result frozen (fp32) | 2.524 ± 0.185 | le 1.0 | **FAIL** |
| H4-signs-result | random signs cost at least 2 W more when the result walks (fp32) | 2.259 ± 0.158 | ge 2.0 | **PASS** |
| H5-bus-share | at least 0.6 of the fp32 result path is the C read and result bus swinging between different accumulators (frozen-but-different over walking, both against frozen-and-equal) | 0.754 ± 0.018 | ge 0.6 | **PASS** |
| H6-two-freezes | fp16: an absorbed and a cancelled result cost the same within 1 W | 0.388 ± 0.111 | abs_le 1.0 | **PASS** |
| P-F32 | the E82-fitted model's F32: 7.56 W within +-1.09 W | 7.922 ± 0.181 | band [6.478, 8.649] | **PASS** |
| P-W32 | the E82-fitted model's W32: 0.37 W within +-1.26 W | 0.100 ± 0.311 | band [-0.89, 1.621] | **PASS** |
| P-M32 | the E82-fitted model's M32: 9.72 W within +-1.56 W | 8.614 ± 0.175 | band [8.159, 11.272] | **PASS** |
| P-R32 | the E82-fitted model's R32: 5.02 W within +-1.56 W | 5.042 ± 0.193 | band [3.453, 6.581] | **PASS** |
| P-R32bus | the E82-fitted model's R32bus: 4.75 W within +-1.49 W | 3.801 ± 0.168 | band [3.262, 6.243] | **PASS** |
| P-R32sum | the E82-fitted model's R32sum: 0.26 W within +-1.26 W | 1.241 ± 0.106 | band [-0.996, 1.525] | **PASS** |
| P-M32s | the E82-fitted model's M32s: 0.24 W within +-1.25 W | 2.524 ± 0.185 | band [-1.012, 1.496] | **FAIL** |
| P-R32s | the E82-fitted model's R32s: 3.69 W within +-1.43 W | 2.259 ± 0.158 | band [2.262, 5.124] | **FAIL** |
| P-X32 | the E82-fitted model's X32: 1.48 W within +-1.26 W | 2.241 ± 0.173 | band [0.225, 2.74] | **PASS** |
| P-F16 | the E82-fitted model's F16: 7.53 W within +-1.12 W | 7.955 ± 0.143 | band [6.408, 8.649] | **PASS** |
| P-W16 | the E82-fitted model's W16: 0.50 W within +-1.20 W | 0.014 ± 0.127 | band [-0.695, 1.705] | **PASS** |
| P-M16 | the E82-fitted model's M16: 5.64 W within +-1.66 W | 6.190 ± 0.168 | band [3.972, 7.301] | **PASS** |
| P-R16 | the E82-fitted model's R16: 7.36 W within +-1.80 W | 6.289 ± 0.208 | band [5.563, 9.156] | **PASS** |
| P-A16 | the E82-fitted model's A16: 0.13 W within +-1.20 W | 0.388 ± 0.111 | band [-1.07, 1.324] | **PASS** |
| P-R16abs | the E82-fitted model's R16abs: 7.23 W within +-1.80 W | 5.901 ± 0.144 | band [5.432, 9.031] | **PASS** |
| P-F8 | the E82-fitted model's F8: 1.36 W within +-0.75 W | 1.710 ± 0.135 | band [0.608, 2.11] | **PASS** |
| P-W8 | the E82-fitted model's W8: 0.17 W within +-0.82 W | -0.231 ± 0.249 | band [-0.642, 0.99] | **PASS** |
| P-M8 | the E82-fitted model's M8: 2.12 W within +-1.57 W | 3.145 ± 0.212 | band [0.558, 3.689] | **PASS** |
| P-R8 | the E82-fitted model's R8: 3.07 W within +-1.61 W | 1.809 ± 0.263 | band [1.456, 4.675] | **PASS** |

| format | part | D (W) ±95% | share of the total ±95% | pJ/MAC |
|---|---|---|---|---|
| fp32 | total (fp32.r_walk) | 21.579 ± 0.152 | 1 | |
| fp32 | i_clocked_lane | 7.922 ± 0.181 | 0.367 ± 0.009 | 1.7254 ± 0.0393 |
| fp32 | iii_operand_multiplier | 8.614 ± 0.175 | 0.399 ± 0.009 | 1.8759 ± 0.0382 |
| fp32 | ii_result_path | 5.042 ± 0.193 | 0.234 ± 0.008 | 1.0979 ± 0.0420 |
| fp16 | total (fp16.r_walk) | 20.434 ± 0.175 | 1 | |
| fp16 | i_clocked_lane | 7.955 ± 0.143 | 0.389 ± 0.007 | 0.8662 ± 0.0156 |
| fp16 | iii_operand_multiplier | 6.190 ± 0.168 | 0.303 ± 0.009 | 0.6742 ± 0.0183 |
| fp16 | ii_result_path | 6.289 ± 0.208 | 0.308 ± 0.008 | 0.6850 ± 0.0226 |
| int8 | total (int8.r_walk) | 6.665 ± 0.145 | 1 | |
| int8 | i_clocked_lane | 1.710 ± 0.135 | 0.257 ± 0.021 | 0.0542 ± 0.0043 |
| int8 | iii_operand_multiplier | 3.145 ± 0.212 | 0.472 ± 0.035 | 0.0997 ± 0.0067 |
| int8 | ii_result_path | 1.809 ± 0.263 | 0.271 ± 0.036 | 0.0574 ± 0.0083 |

Arms: dips-kept {'PASS': 26, 'FAIL': 4, 'INCONCLUSIVE': 2, 'not scored': 0}; leak0.545 {'PASS': 29, 'FAIL': 3, 'INCONCLUSIVE': 0, 'not scored': 0}; leak0.3803 {'PASS': 29, 'FAIL': 3, 'INCONCLUSIVE': 0, 'not scored': 0}; leak0 {'PASS': 30, 'FAIL': 2, 'INCONCLUSIVE': 0, 'not scored': 0}
Verdicts that move between arms: {'H2-int8': {'dips-kept': 'INCONCLUSIVE'}, 'H4-signs-result': {'dips-kept': 'INCONCLUSIVE'}, 'P-R8': {'dips-kept': 'FAIL'}, 'P-R32s': {'leak0': 'PASS'}}
