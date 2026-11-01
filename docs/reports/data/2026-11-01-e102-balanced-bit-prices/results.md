# E102 results (written by score_e102.py)

Passes kept: {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]}. Set aside by E78's gates: []. By the trains' own gate: [{'pass': 10223, 'why': [('fp32.aq', 0.277)]}]. Runs kept 470 of 470; clock 600 MHz; 499.0 mV; primary leakage slope {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}.

## Rules

| rule | verdict (primary arm) | arm | registered expectation | board arm | rail arm |
|---|---|---|---|---|---|
| E102-R1 | **POSITION** | rail | POSITION | POSITION | POSITION |
| E102-R2 | **INCONCLUSIVE** | rail | POSITION | INCONCLUSIVE | INCONCLUSIVE |
| E102-R3 | **NOT SCORED** | rail | INVERTED | NOT SCORED | NOT SCORED |
| E102-R4 | **INCONCLUSIVE** | rail | CONFIRMED | INCONCLUSIVE | INCONCLUSIVE |
| E102-R5 | **INCONCLUSIVE** |  |  |  |  |
| E102-R6 | **INCONCLUSIVE** | rail |  | CONFIRMED | INCONCLUSIVE |
| E102-R7 | **CONFIRMED** | board | CONFIRMED | CONFIRMED | CONFIRMED |
| E102-R8 | **BENCH-LEVEL** | rail | open: E79's list with no temperature term says E79-LEVEL (55 fJ board), the bench says BENCH-LEVEL (16 at the float coefficients, 31 at its int8 fit) | RESOLVED-BETWEEN | BENCH-LEVEL |
| E102-R9 | **SHAPE** | rail | open: E79's list with no temperature term says SHAPE (+0.25 W on the rail), the bench says FLAT (0.00 W) | INCONCLUSIVE | SHAPE |
| E102-R10 | **RISE** | rail | open: the bench says RISE (+0.06 W on the rail, all of it the MSB), E79's list says FLAT (-0.01 W) | INCONCLUSIVE | RISE |
| E102-R11 | **CONFIRMED** | rail |  | INCONCLUSIVE | CONFIRMED |
| E102-R12 | **REPORTED** | rail |  |  |  |
| E102-S1 | **PASS** |  |  |  |  |

Tally: {"POSITION": ["E102-R1"], "INCONCLUSIVE": ["E102-R2", "E102-R4", "E102-R5", "E102-R6"], "NOT SCORED": ["E102-R3"], "CONFIRMED": ["E102-R7", "E102-R11"], "BENCH-LEVEL": ["E102-R8"], "SHAPE": ["E102-R9"], "RISE": ["E102-R10"], "REPORTED": ["E102-R12"], "PASS": ["E102-S1"]}

## Every price

| item | block | flips/op | board ΔW over own zero | board fJ per flipped bit [95%] | rail ΔW | rail fJ [95%] | n | bound? (board, rail) | E79, or the published list, or that list over the ratio | bench (map) | e88+flops |
|---|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| fp16.aj_9 | G | 4096 | 2.800 [2.537, 3.062] | 610 [552, 668] | 2.320 [2.141, 2.500] | 505 [465, 545] | 3 | False, False | 600 | 711 | 690 |
| fp16.aj_12 | T | 4096 | 0.507 [0.142, 0.871] | 110 [31, 190] | 0.431 [0.156, 0.705] | 94 [34, 154] | 3 | False, False | 71 | 54 | 111 |
| fp16.ap_9 | G | 3840 | 1.052 [1.018, 1.087] | 244 [236, 253] | 0.827 [0.782, 0.872] | 192 [181, 203] | 3 | False, False | 107 | 298 | 103 |
| fp16.ap_9 | T | 3840 | 1.196 [1.037, 1.355] | 278 [241, 315] | 0.948 [0.911, 0.985] | 220 [212, 229] | 3 | False, False | 107 | 298 | 103 |
| fp16.ap_12 | T | 3840 | 0.966 [0.720, 1.211] | 224 [167, 281] | 0.747 [0.703, 0.791] | 173 [163, 184] | 3 | False, False | 13 | 166 | 179 |
| fp16.bj_0 | G | 8192 | 1.963 [1.803, 2.123] | 214 [196, 231] | 1.580 [1.394, 1.765] | 172 [152, 192] | 3 | False, False | 198 | 206 | 275 |
| fp16.bj_9 | G | 8192 | 4.714 [4.117, 5.311] | 513 [448, 578] | 3.728 [3.527, 3.929] | 406 [384, 428] | 3 | False, False | 478 | 492 | 731 |
| fp16.bj_12 | T | 8192 | 0.630 [0.376, 0.884] | 69 [41, 96] | 0.520 [0.259, 0.781] | 57 [28, 85] | 3 | False, False | 62 | 49 | 111 |
| fp16.bj_15 | G | 8192 | 0.656 [0.446, 0.866] | 71 [49, 94] | 0.506 [0.420, 0.592] | 55 [46, 65] | 3 | False, False | 33 | 61 | 111 |
| fp16.bp_0 | T | 7936 | 0.960 [0.553, 1.366] | 108 [62, 154] | 0.746 [0.585, 0.908] | 84 [66, 102] | 3 | False, False | 35 | 95 | 58 |
| fp16.bp_9 | G | 7936 | 0.972 [0.675, 1.270] | 109 [76, 143] | 0.743 [0.599, 0.887] | 84 [67, 100] | 3 | False, False | 85 | 105 | 133 |
| fp16.bp_9 | T | 7936 | 1.047 [0.531, 1.563] | 118 [60, 176] | 0.748 [0.389, 1.107] | 84 [44, 124] | 3 | False, False | 85 | 105 | 133 |
| fp16.bp_12 | T | 7936 | 1.630 [1.268, 1.991] | 183 [143, 224] | 1.288 [1.096, 1.480] | 145 [123, 166] | 3 | False, False | 11 | 170 | 183 |
| fp16.bp_15 | G | 7936 | 2.225 [1.983, 2.467] | 250 [223, 277] | 1.750 [1.608, 1.892] | 197 [181, 213] | 3 | False, False | 6 | 258 | 461 |
| fp32.aj_0 | T | 2048 | 0.404 [0.207, 0.602] | 176 [90, 262] | 0.310 [0.241, 0.380] | 135 [105, 166] | 3 | False, False | 194 | 198 | 114 |
| fp32.aj_6 | T | 2048 | 0.260 [0.172, 0.348] | 113 [75, 151] | 0.181 [0.060, 0.302] | 79 [26, 131] | 3 | False, False | 419 | 119 | 114 |
| fp32.aj_11 | T | 2048 | 1.104 [0.879, 1.330] | 481 [383, 580] | 0.855 [0.671, 1.039] | 372 [292, 453] | 3 | False, False | 533 | 462 | 292 |
| fp32.aj_16 | G | 2048 | 1.363 [1.210, 1.516] | 594 [527, 660] | 1.144 [0.942, 1.345] | 498 [410, 586] | 3 | False, False | 795 | 522 | 750 |
| fp32.aj_20 | G | 2048 | 2.343 [2.000, 2.686] | 1021 [871, 1170] | 1.916 [1.552, 2.280] | 835 [676, 993] | 3 | False, False | 1064 | 1252 | 1234 |
| fp32.aj_22 | G | 2048 | 3.226 [2.932, 3.520] | 1405 [1277, 1533] | 2.598 [2.331, 2.865] | 1132 [1015, 1248] | 3 | False, False | 1378 | 1548 | 1298 |
| fp32.aj_23 | T | 2048 | 0.483 [0.356, 0.609] | 210 [155, 265] | 0.409 [0.265, 0.552] | 178 [115, 241] | 3 | False, False | 269 | 180 | 197 |
| fp32.aj_27 | T | 2048 | 0.327 [0.110, 0.545] | 143 [48, 237] | 0.310 [0.100, 0.519] | 135 [43, 226] | 3 | False, False | 224 | 115 | 176 |
| fp32.aj_30 | T | 2048 | 0.417 [0.349, 0.485] | 182 [152, 211] | 0.299 [0.172, 0.426] | 130 [75, 186] | 3 | False, False | 170 | 227 | 398 |
| fp32.aj_31 | T | 2048 | 0.297 [0.086, 0.507] | 129 [37, 221] | 0.255 [0.245, 0.264] | 111 [107, 115] | 3 | False, False | 237 | 134 | 176 |
| fp32.ap_0 | T | 1920 | 0.295 [0.090, 0.499] | 137 [42, 232] | 0.259 [0.096, 0.422] | 120 [44, 196] | 3 | False, False | 28 | 199 | 114 |
| fp32.ap_6 | T | 1920 | 0.227 [0.037, 0.416] | 105 [17, 193] | 0.167 [-0.051, 0.384] | 77 [-23, 178] | 3 | False, True | 60 | 119 | 114 |
| fp32.ap_11 | T | 1920 | 0.715 [0.660, 0.771] | 332 [306, 358] | 0.584 [0.502, 0.665] | 271 [233, 309] | 3 | False, False | 76 | 360 | 114 |
| fp32.ap_16 | T | 1920 | 0.179 [0.154, 0.204] | 83 [72, 95] | 0.135 [0.126, 0.144] | 63 [59, 67] | 3 | False, False | 114 | 122 | 115 |
| fp32.ap_20 | T | 1920 | 0.682 [0.576, 0.788] | 317 [268, 366] | 0.501 [0.292, 0.710] | 233 [136, 330] | 3 | False, False | 152 | 411 | 149 |
| fp32.ap_22 | G | 1920 | 1.397 [1.101, 1.693] | 649 [511, 787] | 1.110 [0.756, 1.464] | 516 [351, 680] | 3 | False, False | 197 | 787 | 143 |
| fp32.ap_22 | T | 1920 | 1.284 [0.942, 1.626] | 597 [438, 755] | 0.997 [0.667, 1.327] | 463 [310, 616] | 3 | False, False | 197 | 787 | 143 |
| fp32.ap_23 | T | 1920 | 0.878 [0.765, 0.991] | 408 [355, 461] | 0.726 [0.663, 0.789] | 337 [308, 367] | 3 | False, False | 38 | 437 | 375 |
| fp32.ap_27 | T | 1920 | 0.992 [0.929, 1.055] | 461 [431, 490] | 0.769 [0.620, 0.917] | 357 [288, 426] | 3 | False, False | 32 | 563 | 365 |
| fp32.ap_30 | T | 1920 | 0.995 [0.930, 1.060] | 462 [433, 492] | 0.740 [0.659, 0.821] | 344 [306, 382] | 3 | False, False | 24 | 561 | 586 |
| fp32.ap_31 | T | 1920 | 1.529 [1.280, 1.778] | 711 [594, 827] | 1.194 [1.004, 1.384] | 555 [466, 644] | 3 | False, False | 34 | 695 | 2024 |
| fp32.bj_0 | T | 4096 | 0.609 [0.522, 0.695] | 133 [114, 152] | 0.541 [0.454, 0.627] | 118 [99, 137] | 3 | False, False | 132 | 185 | 114 |
| fp32.bj_6 | T | 4096 | 0.545 [0.375, 0.714] | 119 [82, 156] | 0.477 [0.427, 0.528] | 104 [93, 115] | 3 | False, False | 80 | 92 | 114 |
| fp32.bj_11 | T | 4096 | 1.281 [1.208, 1.354] | 279 [263, 295] | 1.045 [0.969, 1.121] | 228 [211, 244] | 3 | False, False | 232 | 250 | 375 |
| fp32.bj_16 | G | 4096 | 2.819 [2.585, 3.054] | 614 [563, 665] | 2.250 [2.037, 2.463] | 490 [444, 537] | 3 | False, False | 591 | 536 | 879 |
| fp32.bj_20 | G | 4096 | 3.999 [3.633, 4.364] | 871 [791, 951] | 3.219 [2.940, 3.498] | 701 [640, 763] | 3 | False, False | 840 | 812 | 1276 |
| fp32.bj_22 | G | 4096 | 5.009 [4.784, 5.233] | 1091 [1043, 1139] | 3.955 [3.878, 4.033] | 861 [845, 878] | 3 | False, False | 1021 | 1020 | 1406 |
| fp32.bj_23 | G | 4096 | 0.943 [0.623, 1.263] | 205 [136, 275] | 0.780 [0.524, 1.037] | 170 [114, 226] | 3 | False, False | 168 | 153 | 215 |
| fp32.bj_27 | G | 4096 | 0.644 [0.383, 0.904] | 140 [83, 197] | 0.491 [0.367, 0.615] | 107 [80, 134] | 3 | False, False | 108 | 94 | 176 |
| fp32.bj_30 | G | 4096 | 0.831 [0.746, 0.916] | 181 [162, 200] | 0.672 [0.567, 0.777] | 146 [123, 169] | 3 | False, False | 156 | 211 | 398 |
| fp32.bj_31 | G | 4096 | 0.431 [-1.792, 2.653] | 94 [-390, 578] | 0.452 [0.449, 0.455] | 98 [98, 99] | 2 | True, False | 119 | 140 | 176 |
| fp32.bp_0 | T | 3968 | 0.675 [0.426, 0.925] | 152 [96, 208] | 0.569 [0.405, 0.734] | 128 [91, 165] | 3 | False, False | 19 | 185 | 114 |
| fp32.bp_6 | T | 3968 | 0.502 [0.471, 0.533] | 113 [106, 120] | 0.457 [0.296, 0.619] | 103 [66, 139] | 3 | False, False | 12 | 92 | 114 |
| fp32.bp_11 | T | 3968 | 0.388 [0.338, 0.437] | 87 [76, 98] | 0.412 [0.361, 0.463] | 93 [81, 104] | 3 | False, False | 33 | 90 | 113 |
| fp32.bp_16 | T | 3968 | 0.466 [0.302, 0.630] | 105 [68, 142] | 0.375 [0.175, 0.574] | 84 [39, 129] | 3 | False, False | 84 | 123 | 112 |
| fp32.bp_20 | T | 3968 | 0.730 [0.465, 0.995] | 164 [105, 224] | 0.613 [0.276, 0.950] | 138 [62, 214] | 3 | False, False | 120 | 175 | 202 |
| fp32.bp_22 | G | 3968 | 0.837 [0.499, 1.176] | 188 [112, 264] | 0.648 [0.462, 0.834] | 146 [104, 188] | 3 | False, False | 146 | 150 | 202 |
| fp32.bp_22 | T | 3968 | 0.630 [0.555, 0.706] | 142 [125, 159] | 0.532 [0.361, 0.703] | 120 [81, 158] | 3 | False, False | 146 | 150 | 202 |
| fp32.bp_23 | G | 3968 | 2.070 [1.441, 2.699] | 465 [325, 605] | 1.650 [0.439, 2.862] | 371 [100, 642] | 2 | False, False | 24 | 546 | 481 |
| fp32.bp_27 | G | 3968 | 2.101 [1.919, 2.283] | 473 [432, 513] | 1.685 [1.486, 1.884] | 379 [335, 423] | 3 | False, False | 15 | 568 | 450 |
| fp32.bp_30 | G | 3968 | 1.701 [1.386, 2.015] | 382 [312, 453] | 1.481 [1.297, 1.665] | 333 [292, 374] | 3 | False, False | 22 | 508 | 619 |
| fp32.bp_31 | G | 3968 | 2.388 [2.002, 2.775] | 537 [450, 624] | 2.178 [1.048, 3.307] | 490 [235, 744] | 3 | False, False | 17 | 566 | 1214 |
| int8.bk_0 | I | 1024 | -0.057 [-0.242, 0.128] | -29 [-123, 65] | 0.039 [0.027, 0.051] | 20 [14, 26] | 5 | True, False | 33 | 11 | — |
| int8.bk_1 | I | 1024 | 0.161 [0.091, 0.231] | 82 [46, 117] | 0.121 [0.088, 0.153] | 61 [45, 78] | 5 | False, False | 73 | 9 | — |
| int8.bk_2 | I | 1024 | 0.084 [0.032, 0.136] | 43 [16, 69] | 0.058 [0.028, 0.088] | 29 [14, 45] | 5 | False, False | 29 | 11 | — |
| int8.bk_3 | I | 1024 | 0.179 [0.071, 0.286] | 91 [36, 145] | 0.119 [0.102, 0.135] | 60 [52, 68] | 5 | False, False | 89 | 12 | — |
| int8.bk_4 | I | 1024 | 0.094 [0.046, 0.143] | 48 [23, 72] | 0.037 [0.002, 0.071] | 19 [1, 36] | 5 | False, False | 37 | 10 | — |
| int8.bk_5 | I | 1024 | 0.186 [0.124, 0.248] | 94 [63, 126] | 0.142 [0.125, 0.158] | 72 [63, 80] | 5 | False, False | 96 | 12 | — |
| int8.bk_6 | I | 1024 | 0.102 [0.061, 0.143] | 52 [31, 73] | 0.080 [0.036, 0.124] | 41 [18, 63] | 5 | False, False | 61 | 10 | — |
| int8.bk_7 | I | 1024 | 0.197 [0.159, 0.235] | 100 [81, 119] | 0.151 [0.133, 0.168] | 76 [67, 85] | 5 | False, False | 22 | 48 | — |
| int8.bk_0f | I | 4096 | 0.301 [0.207, 0.396] | 38 [26, 50] | 0.231 [0.184, 0.278] | 29 [23, 35] | 5 | False, False | 56 | 11 | — |
| int8.bk_15 | I | 3072 | 0.200 [0.154, 0.246] | 34 [26, 42] | 0.141 [0.120, 0.161] | 24 [20, 27] | 5 | False, False | 33 | 10 | — |
| int8.bk_2a | I | 3072 | 0.364 [0.259, 0.469] | 62 [44, 79] | 0.277 [0.268, 0.285] | 47 [45, 48] | 5 | False, False | 86 | 10 | — |
| int8.bk_f0 | I | 4096 | 0.418 [0.338, 0.499] | 53 [43, 63] | 0.295 [0.259, 0.331] | 37 [33, 42] | 5 | False, False | 54 | 21 | — |
| int8.bk_ff | I | 8192 | 0.540 [0.359, 0.721] | 34 [23, 46] | 0.468 [0.437, 0.498] | 30 [28, 32] | 5 | False, False | 55 | 16 | — |

## The ratio all-in / balanced, per flipped bit

| list | bit | board ratio [95%] | rail ratio [95%] | pairing |
|---|---:|---|---|---|
| fp32 B | 0 | 0.87 [0.55, 1.57] | 0.92 [0.60, 1.49] | paired |
| fp32 B | 6 | 1.05 [0.70, 1.43] | 1.01 [0.67, 1.73] | paired |
| fp32 B | 11 | 3.20 [2.92, 3.56] | 2.46 [2.27, 2.68] | paired |
| fp32 B | 16 | 5.86 [4.28, 9.09] | 5.82 [3.75, 12.51] | gate over train |
| fp32 B | 20 | 5.31 [3.83, 8.39] | 5.09 [3.25, 11.35] | gate over train |
| fp32 B | 22 | 5.80 [4.30, 9.33] | 5.91 [4.58, 8.32] | paired |
| fp32 A | 0 | 1.29 [0.99, 2.45] | 1.12 [0.83, 2.41] | paired |
| fp32 A | 6 | 1.07 [0.74, 4.63] | 1.02 [—, —] | paired |
| fp32 A | 11 | 1.45 [1.20, 1.68] | 1.37 [1.02, 1.80] | paired |
| fp32 A | 16 | 7.14 [5.99, 8.57] | 7.93 [6.46, 9.46] | gate over train |
| fp32 A | 20 | 3.22 [2.60, 4.00] | 3.59 [2.38, 6.30] | gate over train |
| fp32 A | 22 | 2.16 [1.78, 2.73] | 2.19 [1.79, 2.96] | paired |

## Each frozen model's error over each list, watts

| list | arm | model | rms | mean (measured − predicted) | n |
|---|---|---|---:|---:|---:|
| fp32 B balanced | board | bench_hier2 | 0.188 | 0.146 | 11 |
| fp32 B balanced | board | bench_map | 0.254 | -0.140 | 11 |
| fp32 B balanced | board | e79_measured | 0.134 | 0.085 | 2 |
| fp32 B balanced | board | e88 | 0.660 | 0.146 | 11 |
| fp32 B balanced | board | e88_flops | 0.980 | -0.395 | 11 |
| fp32 B balanced | board | e88_flops_exact | 0.970 | -0.410 | 11 |
| fp32 B balanced | board | ratio_hypothesis | 1.229 | 0.882 | 11 |
| fp32 B balanced | rail | bench_hier2 | 0.210 | 0.163 | 11 |
| fp32 B balanced | rail | bench_map | 0.196 | -0.069 | 11 |
| fp32 B balanced | rail | e79_measured | 0.086 | 0.064 | 2 |
| fp32 B balanced | rail | e88 | 0.491 | 0.162 | 11 |
| fp32 B balanced | rail | e88_flops | 0.715 | -0.276 | 11 |
| fp32 B balanced | rail | e88_flops_exact | 0.706 | -0.288 | 11 |
| fp32 B balanced | rail | ratio_hypothesis | 1.049 | 0.759 | 11 |
| fp32 B all-in | board | all_in_list | 0.213 | 0.148 | 10 |
| fp32 B all-in | board | bench_hier2 | 0.478 | 0.397 | 10 |
| fp32 B all-in | board | bench_map | 0.238 | 0.108 | 10 |
| fp32 B all-in | board | e79_measured | 0.319 | 0.319 | 1 |
| fp32 B all-in | board | e88 | 1.044 | -0.809 | 10 |
| fp32 B all-in | board | e88_flops | 1.481 | -1.226 | 10 |
| fp32 B all-in | board | e88_flops_exact | 0.916 | -0.643 | 10 |
| fp32 B all-in | rail | all_in_list | 0.148 | 0.122 | 10 |
| fp32 B all-in | rail | bench_hier2 | 0.367 | 0.324 | 10 |
| fp32 B all-in | rail | bench_map | 0.163 | 0.089 | 10 |
| fp32 B all-in | rail | e79_measured | 0.157 | 0.157 | 1 |
| fp32 B all-in | rail | e88 | 0.841 | -0.653 | 10 |
| fp32 B all-in | rail | e88_flops | 1.206 | -0.991 | 10 |
| fp32 B all-in | rail | e88_flops_exact | 0.765 | -0.519 | 10 |
| fp32 A balanced | board | bench_hier2 | 0.282 | 0.224 | 11 |
| fp32 A balanced | board | bench_map | 0.197 | -0.152 | 11 |
| fp32 A balanced | board | e88 | 0.805 | 0.235 | 11 |
| fp32 A balanced | board | e88_flops | 0.969 | -0.016 | 11 |
| fp32 A balanced | board | e88_flops_exact | 0.983 | 0.004 | 11 |
| fp32 A balanced | board | ratio_hypothesis | 0.779 | 0.648 | 11 |
| fp32 A balanced | rail | bench_hier2 | 0.209 | 0.159 | 11 |
| fp32 A balanced | rail | bench_map | 0.185 | -0.146 | 11 |
| fp32 A balanced | rail | e88 | 0.649 | 0.168 | 11 |
| fp32 A balanced | rail | e88_flops | 0.791 | -0.035 | 11 |
| fp32 A balanced | rail | e88_flops_exact | 0.802 | -0.019 | 11 |
| fp32 A balanced | rail | ratio_hypothesis | 0.606 | 0.502 | 11 |
| fp32 A all-in | board | all_in_list | 0.292 | -0.191 | 10 |
| fp32 A all-in | board | bench_hier2 | 0.352 | 0.283 | 10 |
| fp32 A all-in | board | bench_map | 0.210 | -0.070 | 10 |
| fp32 A all-in | board | e88 | 0.520 | -0.223 | 10 |
| fp32 A all-in | board | e88_flops | 0.618 | -0.406 | 10 |
| fp32 A all-in | board | e88_flops_exact | 0.301 | -0.067 | 10 |
| fp32 A all-in | rail | all_in_list | 0.235 | -0.155 | 10 |
| fp32 A all-in | rail | bench_hier2 | 0.282 | 0.229 | 10 |
| fp32 A all-in | rail | bench_map | 0.177 | -0.057 | 10 |
| fp32 A all-in | rail | e88 | 0.424 | -0.181 | 10 |
| fp32 A all-in | rail | e88_flops | 0.504 | -0.330 | 10 |
| fp32 A all-in | rail | e88_flops_exact | 0.235 | -0.055 | 10 |
| fp16 balanced | board | bench_hier2 | 0.345 | 0.334 | 8 |
| fp16 balanced | board | bench_map | 0.147 | 0.034 | 8 |
| fp16 balanced | board | e79_measured | 0.256 | 0.254 | 2 |
| fp16 balanced | board | e88 | 0.509 | 0.436 | 8 |
| fp16 balanced | board | e88_flops | 0.778 | 0.027 | 8 |
| fp16 balanced | board | e88_flops_exact | 0.769 | -0.027 | 8 |
| fp16 balanced | board | ratio_hypothesis | 1.080 | 0.886 | 8 |
| fp16 balanced | rail | bench_hier2 | 0.244 | 0.228 | 8 |
| fp16 balanced | rail | bench_map | 0.112 | -0.015 | 8 |
| fp16 balanced | rail | e79_measured | 0.133 | 0.133 | 2 |
| fp16 balanced | rail | e88 | 0.387 | 0.311 | 8 |
| fp16 balanced | rail | e88_flops | 0.640 | -0.021 | 8 |
| fp16 balanced | rail | e88_flops_exact | 0.636 | -0.065 | 8 |
| fp16 balanced | rail | ratio_hypothesis | 0.843 | 0.675 | 8 |
| fp16 all-in | board | all_in_list | 0.219 | 0.184 | 6 |
| fp16 all-in | board | bench_hier2 | 0.453 | 0.414 | 6 |
| fp16 all-in | board | bench_map | 0.247 | 0.055 | 6 |
| fp16 all-in | board | e79_measured | 0.219 | 0.184 | 6 |
| fp16 all-in | board | e88 | 1.237 | -0.832 | 6 |
| fp16 all-in | board | e88_flops | 1.604 | -1.125 | 6 |
| fp16 all-in | board | e88_flops_exact | 0.886 | -0.614 | 6 |
| fp16 all-in | rail | all_in_list | 0.157 | 0.142 | 6 |
| fp16 all-in | rail | bench_hier2 | 0.349 | 0.328 | 6 |
| fp16 all-in | rail | bench_map | 0.178 | 0.037 | 6 |
| fp16 all-in | rail | e79_measured | 0.157 | 0.142 | 6 |
| fp16 all-in | rail | e88 | 1.024 | -0.681 | 6 |
| fp16 all-in | rail | e88_flops | 1.323 | -0.919 | 6 |
| fp16 all-in | rail | e88_flops_exact | 0.751 | -0.504 | 6 |
| int8 B | board | bench_hier2 | 0.180 | 0.148 | 13 |
| int8 B | board | bench_int8fit | 0.113 | 0.082 | 13 |
| int8 B | board | bench_map | 0.179 | 0.147 | 13 |
| int8 B | board | e79_measured | 0.121 | -0.042 | 13 |
| int8 B | board | e88 | 0.187 | 0.157 | 13 |
| int8 B | rail | bench_hier2 | 0.135 | 0.113 | 13 |
| int8 B | rail | bench_int8fit | 0.077 | 0.059 | 13 |
| int8 B | rail | bench_map | 0.134 | 0.113 | 13 |
| int8 B | rail | e79_measured | 0.091 | -0.041 | 13 |
| int8 B | rail | e88 | 0.142 | 0.120 | 13 |

## The arms

| arm | passes kept | rule: verdict |
|---|---|---|
| dips kept | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 PASS |
| gates off | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 PASS |
| E79's way at 0.2414 (p80 in the trains) | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 PASS |
| E79's way at the session's auto slope | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 PASS |
| E79's way at 0.1994 | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 PASS |
| E79's way at 0.3803 | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 PASS |
| E79's way at 0.545 | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 FAIL |
| no temperature term in block G either (0) | {'G': [10210, 10211, 10212], 'T': [10220, 10221, 10222], 'I': [10230, 10231, 10232, 10233, 10234]} | R1 POSITION; R2 INCONCLUSIVE; R3 NOT SCORED; R4 INCONCLUSIVE; R5 INCONCLUSIVE; R6 INCONCLUSIVE; R7 CONFIRMED; R8 BENCH-LEVEL; R9 SHAPE; R10 RISE; R11 CONFIRMED; R12 REPORTED; S1 FAIL |

## int8's B side: bk_ff under each slope, the way E79 reduced it (board p80 in the train, the run's own whole-degree reading)

| arm | ΔW | fJ per flipped bit [95%] | bound? |
|---|---|---|---|
| dips kept | 0.540 [0.359, 0.721] | 34 [23, 46] | False |
| gates off | 0.540 [0.359, 0.721] | 34 [23, 46] | False |
| E79's way at 0.2414 (p80 in the trains) | 0.501 [0.274, 0.728] | 32 [17, 46] | False |
| E79's way at the session's auto slope | 0.519 [0.316, 0.723] | 33 [20, 46] | False |
| E79's way at 0.1994 | 0.508 [0.290, 0.726] | 32 [18, 46] | False |
| E79's way at 0.3803 | 0.478 [0.220, 0.737] | 30 [14, 47] | False |
| E79's way at 0.545 | 0.452 [0.153, 0.750] | 29 [10, 48] | False |
| no temperature term in block G either (0) | 0.540 [0.359, 0.721] | 34 [23, 46] | False |
