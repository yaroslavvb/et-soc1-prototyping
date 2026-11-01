# E97 results (score_e97.py)

Part A passes [9710, 9711]; 81906 samples, all 34 sensors in 81906; reference phase -35.4 deg

## Part A: every block, the pass as the unit (t(0.975, n - 1) x SE over passes), the lap beside

| block | kind vs ref | W (E78/E86) | laps | P fund (W) | T fund (C) | H (C/W) by pass | r board [95%, pass] | r board [95%, lap] | r minion [95%, pass] | r minion [95%, lap] | 2 s rise (C) +-pass | c0 / c1 | step2 per W | minion share | die mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f32zero | fp32.zeros vs idle | S 1.986 | 4 | 1.263 | 0.281 | 0.2276, 0.2175 | 1.130 [0.762, 1.498] | 1.130 [1.067, 1.194] | 1.073 [0.863, 1.284] | 1.073 [1.034, 1.113] | 0.258 +- 0.012 | 0.259 / 0.257 | 0.1301 | 0.853 | 52.46 |
| f16zero | fp16.zeros vs idle | S 1.987 | 4 | 1.238 | 0.264 | 0.2110, 0.2150 | 1.082 [0.871, 1.292] | 1.082 [1.038, 1.126] | 1.006 [0.922, 1.089] | 1.006 [0.992, 1.019] | 0.259 +- 0.012 | 0.255 / 0.262 | 0.1301 | 0.872 | 52.28 |
| f32sp90 | fp32.sparse90 vs idle | S 2.509 | 4 | 1.615 | 0.352 | 0.2198, 0.2158 | 1.106 [0.893, 1.319] | 1.106 [1.060, 1.152] | 1.031 [0.821, 1.241] | 1.031 [0.991, 1.072] | 0.338 +- 0.043 | 0.338 / 0.338 | 0.1348 | 0.869 | 53.36 |
| f32arbz | fp32.a_randn_b_zeros vs idle | S 2.574 | 4 | 1.637 | 0.364 | 0.2253, 0.2197 | 1.130 [0.878, 1.382] | 1.130 [1.051, 1.209] | 1.050 [0.860, 1.241] | 1.050 [1.003, 1.097] | 0.337 +- 0.005 | 0.338 / 0.336 | 0.1309 | 0.872 | 52.62 |
| f32azbr | fp32.a_zeros_b_randn vs idle | S 2.839 | 4 | 1.701 | 0.370 | 0.2130, 0.2221 | 1.105 [0.766, 1.443] | 1.105 [1.046, 1.163] | 1.012 [0.736, 1.288] | 1.012 [0.953, 1.072] | 0.360 +- 0.035 | 0.371 / 0.349 | 0.1267 | 0.885 | 54.93 |
| f16sp90 | fp16.sparse90 vs idle | S 3.380 | 4 | 2.102 | 0.458 | 0.2220, 0.2137 | 1.107 [0.789, 1.424] | 1.107 [1.038, 1.175] | 1.018 [0.839, 1.196] | 1.018 [0.991, 1.045] | 0.435 +- 0.095 | 0.435 / 0.435 | 0.1286 | 0.881 | 54.24 |
| f16wsp90 | fp16.wsparse90 vs idle | S 2.643 | 4 | 1.669 | 0.359 | 0.2095, 0.2207 | 1.093 [0.693, 1.492] | 1.093 [1.028, 1.157] | 1.009 [0.792, 1.225] | 1.009 [0.965, 1.052] | 0.349 +- 0.068 | 0.353 / 0.344 | 0.1319 | 0.878 | 53.69 |
| f16arbz | fp16.a_randn_b_zeros vs idle | S 2.669 | 4 | 1.648 | 0.362 | 0.2197, 0.2194 | 1.115 [0.944, 1.286] | 1.115 [1.060, 1.170] | 1.045 [1.027, 1.063] | 1.045 [1.013, 1.077] | 0.342 +- 0.072 | 0.341 / 0.343 | 0.1282 | 0.864 | 52.43 |
| f16azbr | fp16.a_zeros_b_randn vs idle | S 2.713 | 4 | 1.694 | 0.373 | 0.2198, 0.2203 | 1.118 [0.946, 1.290] | 1.118 [1.057, 1.178] | 1.032 [0.902, 1.162] | 1.032 [1.011, 1.053] | 0.356 +- 0.07 | 0.356 / 0.356 | 0.1311 | 0.878 | 52.68 |
| i8azbf | int8.a_zeros_b_full vs idle | S 2.900 | 4 | 1.782 | 0.395 | 0.2199, 0.2234 | 1.126 [0.921, 1.331] | 1.126 [1.066, 1.185] | 1.003 [0.831, 1.176] | 1.003 [0.975, 1.031] | 0.377 +- 0.022 | 0.379 / 0.374 | 0.1299 | 0.909 | 53.90 |
| i8afbz | int8.a_full_b_zeros vs idle | S 3.115 | 4 | 1.896 | 0.411 | 0.2140, 0.2197 | 1.101 [0.851, 1.352] | 1.101 [1.051, 1.151] | 0.987 [0.807, 1.166] | 0.987 [0.954, 1.019] | 0.396 +- 0.009 | 0.397 / 0.396 | 0.1273 | 0.905 | 54.30 |
| i8wsp90 | int8.wsparse90 vs idle | S 3.079 | 4 | 1.949 | 0.422 | 0.2157, 0.2178 | 1.101 [0.919, 1.282] | 1.101 [1.063, 1.139] | 0.992 [0.941, 1.043] | 0.992 [0.965, 1.019] | 0.405 +- 0.054 | 0.406 / 0.403 | 0.1314 | 0.900 | 53.07 |
| i8sp90 | int8.sparse90 vs idle | S 3.763 | 4 | 2.331 | 0.515 | 0.2231, 0.2191 | 1.123 [0.908, 1.337] | 1.123 [1.076, 1.170] | 1.014 [0.974, 1.054] | 1.014 [0.980, 1.048] | 0.490 +- 0.003 | 0.484 / 0.495 | 0.1301 | 0.898 | 53.78 |
| i8ones | int8.ones vs idle | S 4.146 | 4 | 2.640 | 0.578 | 0.2165, 0.2212 | 1.111 [0.885, 1.338] | 1.111 [1.064, 1.159] | 1.010 [0.986, 1.033] | 1.010 [0.988, 1.031] | 0.544 +- 0.017 | 0.548 / 0.540 | 0.1313 | 0.892 | 54.85 |
| i8wsp50 | int8.wsparse50 vs int8.zeros | D 3.142 | 4 | 1.963 | 0.413 | 0.2096, 0.2125 | 1.072 [0.883, 1.261] | 1.072 [0.954, 1.189] | 0.997 [0.851, 1.144] | 0.997 [0.957, 1.037] | 0.392 +- 0.294 | 0.369 / 0.414 | 0.1246 | 0.871 | 54.98 |
| i8high | int8.highbit vs int8.zeros | D 3.233 | 4 | 1.947 | 0.422 | 0.2158, 0.2179 | 1.101 [0.919, 1.283] | 1.101 [1.032, 1.170] | 1.006 [0.967, 1.045] | 1.006 [0.994, 1.017] | 0.432 +- 0.015 | 0.390 / 0.475 | 0.1336 | 0.887 | 54.43 |
| i8tern | int8.ternary vs int8.zeros | D 5.186 | 4 | 3.103 | 0.651 | 0.2111, 0.2088 | 1.066 [0.887, 1.246] | 1.066 [1.000, 1.133] | 0.989 [0.915, 1.062] | 0.989 [0.968, 1.009] | 0.639 +- 0.119 | 0.612 / 0.667 | 0.1233 | 0.874 | 55.55 |
| i8pos | int8.pos vs int8.zeros | D 6.171 | 4 | 3.806 | 0.796 | 0.2099, 0.2082 | 1.062 [0.891, 1.233] | 1.062 [1.024, 1.100] | 1.001 [0.984, 1.018] | 1.001 [0.995, 1.007] | 0.760 +- 0.256 | 0.733 / 0.787 | 0.1232 | 0.860 | 56.68 |
| i8sort | int8.sorted vs int8.zeros | D 6.588 | 4 | 4.014 | 0.846 | 0.2087, 0.2130 | 1.071 [0.857, 1.285] | 1.071 [1.026, 1.116] | 0.999 [0.947, 1.051] | 0.999 [0.990, 1.008] | 0.775 +- 0.006 | 0.775 / 0.774 | 0.1176 | 0.869 | 56.49 |
| f16wsp50 | fp16.wsparse50 vs fp16.zeros | D 7.058 | 4 | 4.220 | 0.893 | 0.2131, 0.2102 | 1.075 [0.886, 1.264] | 1.075 [1.032, 1.118] | 0.997 [0.972, 1.022] | 0.997 [0.989, 1.004] | 0.926 +- 0.134 | 0.826 / 1.026 | 0.1312 | 0.874 | 55.86 |
| f32sp50 | fp32.sparse50 vs fp32.zeros | D 7.302 | 4 | 4.372 | 0.921 | 0.2082, 0.2131 | 1.070 [0.841, 1.299] | 1.070 [1.027, 1.113] | 0.996 [0.928, 1.064] | 0.996 [0.972, 1.020] | 0.937 +- 0.16 | 0.845 / 1.029 | 0.1283 | 0.871 | 55.34 |
| f32neg1 | fp32.neg_ones vs fp32.zeros | D 8.143 | 4 | 5.015 | 1.061 | 0.2152, 0.2079 | 1.074 [0.789, 1.360] | 1.074 [1.020, 1.129] | 0.996 [0.858, 1.134] | 0.996 [0.970, 1.022] | 1.072 +- 0.154 | 0.979 / 1.165 | 0.1317 | 0.874 | 56.08 |
| f16neg1 | fp16.neg_ones vs fp16.zeros | D 8.382 | 4 | 5.064 | 1.063 | 0.2098, 0.2103 | 1.067 [0.903, 1.231] | 1.067 [1.020, 1.114] | 0.995 [0.958, 1.031] | 0.995 [0.981, 1.008] | 1.064 +- 0.063 | 0.973 / 1.155 | 0.1269 | 0.870 | 56.71 |
| f16ones | fp16.ones vs fp16.zeros | D 8.448 | 4 | 5.021 | 1.072 | 0.2130, 0.2144 | 1.085 [0.914, 1.257] | 1.085 [1.035, 1.136] | 1.008 [0.999, 1.016] | 1.008 [0.999, 1.017] | 1.062 +- 0.185 | 0.977 / 1.146 | 0.1257 | 0.873 | 56.57 |
| f32pi | fp32.pi vs fp32.zeros | D 8.470 | 4 | 5.072 | 1.078 | 0.2127, 0.2127 | 1.080 [0.915, 1.245] | 1.080 [1.031, 1.130] | 1.001 [0.951, 1.050] | 1.001 [0.989, 1.012] | 1.080 +- 0.145 | 0.989 / 1.170 | 0.1275 | 0.875 | 56.53 |
| i8r0up | int8.real_l0_mlp_up vs int8.zeros | D 6.291 | 4 | 3.834 | 0.810 | 0.2115, 0.2111 | 1.073 [0.908, 1.238] | 1.073 [1.030, 1.117] | 0.999 [0.909, 1.089] | 0.999 [0.986, 1.012] | 0.770 +- 0.162 | 0.742 / 0.798 | 0.1223 | 0.870 | 57.21 |
| i8r6dn | int8.real_l6_mlp_down vs int8.zeros | D 5.748 | 4 | 3.472 | 0.728 | 0.2092, 0.2101 | 1.065 [0.900, 1.230] | 1.065 [1.020, 1.110] | 0.991 [0.949, 1.032] | 0.991 [0.982, 0.999] | 0.703 +- 0.053 | 0.649 / 0.757 | 0.1222 | 0.871 | 56.56 |
| i8r6qk | int8.real_l6_attn_qk vs int8.zeros | D 5.543 | 4 | 3.375 | 0.719 | 0.2137, 0.2125 | 1.082 [0.912, 1.252] | 1.082 [1.031, 1.134] | 1.007 [0.957, 1.057] | 1.007 [0.998, 1.016] | 0.653 +- 0.17 | 0.642 / 0.664 | 0.1178 | 0.871 | 55.88 |
| f32randn | fp32.randn vs fp32.zeros | D 24.725 | 4 | 15.275 | 3.007 | 0.1993, 0.1945 | - | - | - | - | 2.848 +- 0.102 | 2.749 / 2.947 | 0.1152 | 0.810 | 60.61 |

## The heat column: the 2 s rise over idle (C), with E78's S x 0.118 beside

| kind | block | S (W) | 2 s rise over idle (C) | +-95% (lap) | how | S x 0.118 (C) | ratio |
|---|---|---|---|---|---|---|---|
| fp32.zeros | f32zero | 1.986 | 0.258 | 0.004 | measured over idle | 0.234 | 1.102 |
| fp16.zeros | f16zero | 1.987 | 0.259 | 0.007 | measured over idle | 0.234 | 1.103 |
| fp32.sparse90 | f32sp90 | 2.509 | 0.338 | 0.008 | measured over idle | 0.296 | 1.143 |
| fp32.a_randn_b_zeros | f32arbz | 2.574 | 0.337 | 0.003 | measured over idle | 0.304 | 1.109 |
| fp16.wsparse90 | f16wsp90 | 2.643 | 0.349 | 0.014 | measured over idle | 0.312 | 1.118 |
| fp16.a_randn_b_zeros | f16arbz | 2.669 | 0.342 | 0.011 | measured over idle | 0.315 | 1.087 |
| fp16.a_zeros_b_randn | f16azbr | 2.713 | 0.356 | 0.01 | measured over idle | 0.320 | 1.111 |
| fp32.a_zeros_b_randn | f32azbr | 2.839 | 0.360 | 0.021 | measured over idle | 0.335 | 1.074 |
| int8.a_zeros_b_full | i8azbf | 2.900 | 0.377 | 0.005 | measured over idle | 0.342 | 1.101 |
| int8.wsparse90 | i8wsp90 | 3.079 | 0.405 | 0.009 | measured over idle | 0.363 | 1.113 |
| int8.a_full_b_zeros | i8afbz | 3.115 | 0.396 | 0.002 | measured over idle | 0.368 | 1.079 |
| fp16.sparse90 | f16sp90 | 3.380 | 0.435 | 0.014 | measured over idle | 0.399 | 1.090 |
| int8.sparse90 | i8sp90 | 3.763 | 0.490 | 0.012 | measured over idle | 0.444 | 1.102 |
| int8.ones | i8ones | 4.146 | 0.544 | 0.008 | measured over idle | 0.489 | 1.113 |
| int8.wsparse50 | i8wsp50 | 5.743 | 0.731 | 0.077 | derived: 0.392 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 0.678 | 1.079 |
| int8.highbit | i8high | 5.853 | 0.772 | 0.078 | derived: 0.432 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 0.691 | 1.118 |
| int8.ternary | i8tern | 7.727 | 0.979 | 0.062 | derived: 0.639 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 0.912 | 1.074 |
| int8.real_l6_attn_qk | i8r6qk | 8.182 | 0.993 | 0.033 | derived: 0.653 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 0.965 | 1.028 |
| int8.real_l6_mlp_down | i8r6dn | 8.296 | 1.042 | 0.1 | derived: 0.703 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 0.979 | 1.065 |
| int8.pos | i8pos | 8.732 | 1.100 | 0.072 | derived: 0.760 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 1.030 | 1.067 |
| int8.real_l0_mlp_up | i8r0up | 8.836 | 1.110 | 0.069 | derived: 0.770 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 1.043 | 1.064 |
| fp16.wsparse50 | f16wsp50 | 9.090 | 1.185 | 0.185 | derived: 0.926 over fp16 zeros + 0.259 (E97 f16zero, measured over idle) | 1.073 | 1.104 |
| int8.sorted | i8sort | 9.170 | 1.115 | 0.006 | derived: 0.775 over int8 zeros + 0.340 (E89 i8zero, measured over idle) | 1.082 | 1.030 |
| fp32.sparse50 | f32sp50 | 9.243 | 1.195 | 0.171 | derived: 0.937 over fp32 zeros + 0.258 (E97 f32zero, measured over idle) | 1.091 | 1.096 |
| fp32.neg_ones | f32neg1 | 10.116 | 1.331 | 0.173 | derived: 1.072 over fp32 zeros + 0.258 (E97 f32zero, measured over idle) | 1.194 | 1.115 |
| fp16.neg_ones | f16neg1 | 10.355 | 1.322 | 0.168 | derived: 1.064 over fp16 zeros + 0.259 (E97 f16zero, measured over idle) | 1.222 | 1.082 |
| fp16.ones | f16ones | 10.376 | 1.320 | 0.157 | derived: 1.062 over fp16 zeros + 0.259 (E97 f16zero, measured over idle) | 1.224 | 1.078 |
| fp32.pi | f32pi | 10.396 | 1.338 | 0.168 | derived: 1.080 over fp32 zeros + 0.258 (E97 f32zero, measured over idle) | 1.227 | 1.091 |

## The 2 s step by cycle and baseline (reported, E89 C6): cycle 0 follows the 20 s lead-in, whose last launch ends at its end; cycle 1 follows a 30 s half, whose chain ends about 1.5 s early

| block | E89's line over the last 5 s: c0 / c1 | a line over [-8, -2) s, before that gap: c0 / c1 | a quadratic over the last 20 s: c0 / c1 |
|---|---|---|---|
| f32zero | 0.259 / 0.257 | 0.263 / 0.266 | 0.256 / 0.253 |
| f16zero | 0.255 / 0.262 | 0.257 / 0.269 | 0.253 / 0.263 |
| f32sp90 | 0.338 / 0.338 | 0.341 / 0.341 | 0.323 / 0.333 |
| f32arbz | 0.338 / 0.336 | 0.338 / 0.336 | 0.336 / 0.328 |
| f32azbr | 0.371 / 0.349 | 0.372 / 0.356 | 0.322 / 0.344 |
| f16sp90 | 0.435 / 0.435 | 0.443 / 0.440 | 0.421 / 0.426 |
| f16wsp90 | 0.353 / 0.344 | 0.360 / 0.344 | 0.340 / 0.339 |
| f16arbz | 0.341 / 0.343 | 0.346 / 0.341 | 0.344 / 0.335 |
| f16azbr | 0.356 / 0.356 | 0.365 / 0.358 | 0.361 / 0.351 |
| i8azbf | 0.379 / 0.374 | 0.390 / 0.376 | 0.340 / 0.363 |
| i8afbz | 0.397 / 0.396 | 0.412 / 0.394 | 0.363 / 0.384 |
| i8wsp90 | 0.406 / 0.403 | 0.407 / 0.402 | 0.404 / 0.393 |
| i8sp90 | 0.484 / 0.495 | 0.488 / 0.485 | 0.467 / 0.478 |
| i8ones | 0.548 / 0.540 | 0.557 / 0.544 | 0.504 / 0.527 |
| i8wsp50 | 0.369 / 0.414 | 0.374 / 0.312 | 0.431 / 0.366 |
| i8high | 0.390 / 0.475 | 0.367 / 0.307 | 0.459 / 0.388 |
| i8tern | 0.612 / 0.667 | 0.588 / 0.531 | 0.679 / 0.597 |
| i8pos | 0.733 / 0.787 | 0.730 / 0.651 | 0.766 / 0.712 |
| i8sort | 0.775 / 0.774 | 0.771 / 0.728 | 0.823 / 0.747 |
| f16wsp50 | 0.826 / 1.026 | 0.833 / 0.756 | 0.862 / 0.887 |
| f32sp50 | 0.845 / 1.029 | 0.864 / 0.777 | 0.894 / 0.893 |
| f32neg1 | 0.979 / 1.165 | 0.993 / 0.911 | 1.017 / 1.024 |
| f16neg1 | 0.973 / 1.155 | 0.999 / 0.899 | 1.007 / 1.014 |
| f16ones | 0.977 / 1.146 | 0.993 / 0.909 | 1.037 / 1.012 |
| f32pi | 0.989 / 1.170 | 1.007 / 0.924 | 1.032 / 1.036 |
| i8r0up | 0.742 / 0.798 | 0.740 / 0.674 | 0.795 / 0.732 |
| i8r6dn | 0.649 / 0.757 | 0.676 / 0.588 | 0.703 / 0.663 |
| i8r6qk | 0.642 / 0.664 | 0.650 / 0.605 | 0.715 / 0.629 |
| f32randn | 2.749 / 2.947 | 2.779 / 2.706 | 2.798 / 2.782 |

## Part B: the holds

| hold | item | s | end | launches | idle before/after (C) | die at end (C) | dT (C) +- bound | dP board (W) | rise per board W [bound] | per minion W | per S_eff | slope (C/min) | leak share | loop gain | closure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | int8.full | 1800 | time | 244 | 50.559 / 50.629 | 62.40 | 11.80 +- 0.05 | 13.12 | 0.899 [0.894, 0.904] | 1.156 | 1.267 | -0.1016 | 0.298 | 0.363 | 0.99 |
| H2 | fp32.ones | 900 | time | 126 | 50.559 / 50.629 | 63.78 | 13.17 +- 0.04 | 14.30 | 0.921 [0.918, 0.925] | 1.201 | 1.329 | -0.0069 | 0.313 | 0.388 | 0.991 |
| H3 | fp32.randn | 1800 | time | 257 | 50.629 / 50.663 | 70.37 | 19.72 +- 0.03 | 22.49 | 0.877 [0.868, 0.885] | 1.205 | 1.318 | 0.0252 | 0.334 | 0.441 | 1.001 |

| rest | ends | s | idle (C) | above the starting idle (C) | within 1 / 0.5 / 0.2 / 0.1 C of the starting idle after (s) |
|---|---|---|---|---|---|
| R0 | slope | 832 | 50.55835482010187 | 0.0 | 284.98200011253357 / 374.98200011253357 / 464.98200011253357 / 524.9820001125336 |
| R1 | level | 600 | 50.62903045055913 | 0.07067563045725933 | 345.03700017929077 / 435.03700017929077 / 495.03700017929077 / 525.0370001792908 |
| R2 | level | 900 | 50.66277590762868 | 0.10442108752680923 | 374.9800000190735 / 464.9800000190735 / 524.9800000190735 / 554.9800000190735 |

Decisions: chain: H2 for 15 min on H1, R1, H3, R3 (98.9 min left)


## Verdicts

| rule | cell | unit | measured | band | verdict | predicted | trend |
|---|---|---|---|---|---|---|---|
| E97-R0 | the per-sensor reading (Part A and Part B) | samples | samples 150295, share_with_34 1.0000, share_eq 0.9832 | share_with_34 >= 0.99, share_eq >= 0.95 | **PASS** | PASS |  |
| E97-R1 | f32zero | pass | T_fund_C 0.2810, lo 0.2185, hi 0.3435 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32zero | lap | T_fund_C 0.2810, lo 0.2705, hi 0.2916 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16zero | pass | T_fund_C 0.2637, lo 0.2365, hi 0.2909 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16zero | lap | T_fund_C 0.2637, lo 0.2555, hi 0.2719 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32sp90 | pass | T_fund_C 0.3516, lo 0.3207, hi 0.3826 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32sp90 | lap | T_fund_C 0.3516, lo 0.3453, hi 0.3580 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32arbz | pass | T_fund_C 0.3640, lo 0.2771, hi 0.4510 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32arbz | lap | T_fund_C 0.3640, lo 0.3501, hi 0.3780 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32azbr | pass | T_fund_C 0.3701, lo 0.2719, hi 0.4683 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32azbr | lap | T_fund_C 0.3701, lo 0.3555, hi 0.3847 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16sp90 | pass | T_fund_C 0.4579, lo 0.3629, hi 0.5528 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16sp90 | lap | T_fund_C 0.4579, lo 0.4340, hi 0.4817 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16wsp90 | pass | T_fund_C 0.3589, lo 0.2551, hi 0.4628 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16wsp90 | lap | T_fund_C 0.3589, lo 0.3439, hi 0.3740 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16arbz | pass | T_fund_C 0.3617, lo 0.3379, hi 0.3855 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16arbz | lap | T_fund_C 0.3617, lo 0.3491, hi 0.3743 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16azbr | pass | T_fund_C 0.3728, lo 0.3451, hi 0.4005 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16azbr | lap | T_fund_C 0.3728, lo 0.3541, hi 0.3915 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8azbf | pass | T_fund_C 0.3949, lo 0.3413, hi 0.4485 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8azbf | lap | T_fund_C 0.3949, lo 0.3768, hi 0.4130 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8afbz | pass | T_fund_C 0.4112, lo 0.3325, hi 0.4899 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8afbz | lap | T_fund_C 0.4112, lo 0.3959, hi 0.4266 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8wsp90 | pass | T_fund_C 0.4225, lo 0.4094, hi 0.4356 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8wsp90 | lap | T_fund_C 0.4225, lo 0.4130, hi 0.4320 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8sp90 | pass | T_fund_C 0.5153, lo 0.4912, hi 0.5394 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8sp90 | lap | T_fund_C 0.5153, lo 0.5029, hi 0.5278 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8ones | pass | T_fund_C 0.5778, lo 0.5675, hi 0.5880 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8ones | lap | T_fund_C 0.5778, lo 0.5718, hi 0.5837 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8wsp50 | pass | T_fund_C 0.4126, lo 0.3490, hi 0.4763 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8wsp50 | lap | T_fund_C 0.4126, lo 0.3950, hi 0.4303 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8high | pass | T_fund_C 0.4218, lo 0.4042, hi 0.4394 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8high | lap | T_fund_C 0.4218, lo 0.4123, hi 0.4314 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8tern | pass | T_fund_C 0.6513, lo 0.6510, hi 0.6515 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8tern | lap | T_fund_C 0.6513, lo 0.6355, hi 0.6670 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8pos | pass | T_fund_C 0.7958, lo 0.7670, hi 0.8246 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8pos | lap | T_fund_C 0.7958, lo 0.7719, hi 0.8197 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8sort | pass | T_fund_C 0.8463, lo 0.7860, hi 0.9066 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8sort | lap | T_fund_C 0.8463, lo 0.8151, hi 0.8774 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16wsp50 | pass | T_fund_C 0.8931, lo 0.8364, hi 0.9497 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16wsp50 | lap | T_fund_C 0.8931, lo 0.8763, hi 0.9099 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32sp50 | pass | T_fund_C 0.9209, lo 0.8383, hi 1.0035 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32sp50 | lap | T_fund_C 0.9209, lo 0.8952, hi 0.9466 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32neg1 | pass | T_fund_C 1.0606, lo 0.8831, hi 1.2381 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32neg1 | lap | T_fund_C 1.0606, lo 1.0182, hi 1.1031 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16neg1 | pass | T_fund_C 1.0635, lo 1.0335, hi 1.0934 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16neg1 | lap | T_fund_C 1.0635, lo 1.0475, hi 1.0794 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16ones | pass | T_fund_C 1.0724, lo 1.0717, hi 1.0731 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f16ones | lap | T_fund_C 1.0724, lo 1.0476, hi 1.0971 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32pi | pass | T_fund_C 1.0782, lo 1.0371, hi 1.1194 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32pi | lap | T_fund_C 1.0782, lo 1.0517, hi 1.1048 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8r0up | pass | T_fund_C 0.8100, lo 0.7617, hi 0.8584 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8r0up | lap | T_fund_C 0.8100, lo 0.7827, hi 0.8374 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8r6dn | pass | T_fund_C 0.7278, lo 0.7277, hi 0.7280 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8r6dn | lap | T_fund_C 0.7278, lo 0.7170, hi 0.7387 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8r6qk | pass | T_fund_C 0.7190, lo 0.6910, hi 0.7469 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | i8r6qk | lap | T_fund_C 0.7190, lo 0.6934, hi 0.7446 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32randn | pass | T_fund_C 3.0071, lo 2.9840, hi 3.0301 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R1 | f32randn | lap | T_fund_C 3.0071, lo 2.9365, hi 3.0777 | 95% lower bound > 0 | **PASS** | PASS |  |
| E97-R2 | f32zero | pass | r 1.1301, se 0.0289, df 1, lo 0.7623, hi 1.4979 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f32zero | lap | r 1.1301, se 0.0200, df 3, lo 1.0666, hi 1.1937 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16zero | pass | r 1.0816, se 0.0165, df 1, lo 0.8714, hi 1.2918 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f16zero | lap | r 1.0816, se 0.0138, df 3, lo 1.0376, hi 1.1256 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f32sp90 | pass | r 1.1060, se 0.0168, df 1, lo 0.8926, hi 1.3194 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f32sp90 | lap | r 1.1060, se 0.0144, df 3, lo 1.0600, hi 1.1520 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f32arbz | pass | r 1.1301, se 0.0198, df 1, lo 0.8782, hi 1.3819 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f32arbz | lap | r 1.1301, se 0.0247, df 3, lo 1.0515, hi 1.2086 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f32azbr | pass | r 1.1048, se 0.0266, df 1, lo 0.7663, hi 1.4433 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f32azbr | lap | r 1.1048, se 0.0184, df 3, lo 1.0462, hi 1.1634 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16sp90 | pass | r 1.1065, se 0.0250, df 1, lo 0.7887, hi 1.4244 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f16sp90 | lap | r 1.1065, se 0.0215, df 3, lo 1.0381, hi 1.1749 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16wsp90 | pass | r 1.0925, se 0.0315, df 1, lo 0.6926, hi 1.4925 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f16wsp90 | lap | r 1.0925, se 0.0201, df 3, lo 1.0285, hi 1.1566 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16arbz | pass | r 1.1149, se 0.0135, df 1, lo 0.9440, hi 1.2859 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f16arbz | lap | r 1.1149, se 0.0172, df 3, lo 1.0601, hi 1.1698 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16azbr | pass | r 1.1178, se 0.0135, df 1, lo 0.9460, hi 1.2896 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f16azbr | lap | r 1.1178, se 0.0189, df 3, lo 1.0575, hi 1.1781 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8azbf | pass | r 1.1257, se 0.0161, df 1, lo 0.9206, hi 1.3309 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8azbf | lap | r 1.1257, se 0.0187, df 3, lo 1.0661, hi 1.1854 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8afbz | pass | r 1.1013, se 0.0197, df 1, lo 0.8507, hi 1.3519 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8afbz | lap | r 1.1013, se 0.0157, df 3, lo 1.0514, hi 1.1512 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8wsp90 | pass | r 1.1008, se 0.0143, df 1, lo 0.9192, hi 1.2823 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8wsp90 | lap | r 1.1008, se 0.0120, df 3, lo 1.0626, hi 1.1389 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8sp90 | pass | r 1.1228, se 0.0169, df 1, lo 0.9085, hi 1.3372 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8sp90 | lap | r 1.1228, se 0.0147, df 3, lo 1.0761, hi 1.1696 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8ones | pass | r 1.1115, se 0.0178, df 1, lo 0.8850, hi 1.3379 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8ones | lap | r 1.1115, se 0.0149, df 3, lo 1.0640, hi 1.1589 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8wsp50 | pass | r 1.0719, se 0.0148, df 1, lo 0.8833, hi 1.2605 | [0.8, 1.25] | **INCONCLUSIVE** | PASS | ['cubic: PASS'] |
| E97-R2 | i8wsp50 | lap | r 1.0719, se 0.0369, df 3, lo 0.9545, hi 1.1894 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8high | pass | r 1.1013, se 0.0143, df 1, lo 0.9195, hi 1.2831 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8high | lap | r 1.1013, se 0.0216, df 3, lo 1.0324, hi 1.1701 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8tern | pass | r 1.0664, se 0.0141, df 1, lo 0.8866, hi 1.2461 | [0.8, 1.25] | **PASS** | PASS | ['linear: INCONCLUSIVE', 'cubic: INCONCLUSIVE'] |
| E97-R2 | i8tern | lap | r 1.0664, se 0.0210, df 3, lo 0.9995, hi 1.1333 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8pos | pass | r 1.0619, se 0.0135, df 1, lo 0.8907, hi 1.2330 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8pos | lap | r 1.0619, se 0.0120, df 3, lo 1.0236, hi 1.1001 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8sort | pass | r 1.0708, se 0.0169, df 1, lo 0.8566, hi 1.2850 | [0.8, 1.25] | **INCONCLUSIVE** | PASS | ['cubic: PASS'] |
| E97-R2 | i8sort | lap | r 1.0708, se 0.0141, df 3, lo 1.0261, hi 1.1155 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16wsp50 | pass | r 1.0750, se 0.0149, df 1, lo 0.8860, hi 1.2640 | [0.8, 1.25] | **INCONCLUSIVE** | PASS | ['linear: PASS'] |
| E97-R2 | f16wsp50 | lap | r 1.0750, se 0.0135, df 3, lo 1.0322, hi 1.1179 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f32sp50 | pass | r 1.0698, se 0.0180, df 1, lo 0.8407, hi 1.2989 | [0.8, 1.25] | **INCONCLUSIVE** | PASS | ['cubic: PASS'] |
| E97-R2 | f32sp50 | lap | r 1.0698, se 0.0136, df 3, lo 1.0266, hi 1.1130 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f32neg1 | pass | r 1.0744, se 0.0225, df 1, lo 0.7892, hi 1.3597 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | f32neg1 | lap | r 1.0744, se 0.0170, df 3, lo 1.0204, hi 1.1285 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16neg1 | pass | r 1.0668, se 0.0129, df 1, lo 0.9026, hi 1.2310 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16neg1 | lap | r 1.0668, se 0.0147, df 3, lo 1.0200, hi 1.1136 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f16ones | pass | r 1.0853, se 0.0135, df 1, lo 0.9136, hi 1.2570 | [0.8, 1.25] | **INCONCLUSIVE** | PASS | ['cubic: PASS'] |
| E97-R2 | f16ones | lap | r 1.0853, se 0.0158, df 3, lo 1.0350, hi 1.1356 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | f32pi | pass | r 1.0801, se 0.0130, df 1, lo 0.9148, hi 1.2454 | [0.8, 1.25] | **PASS** | PASS | ['linear: INCONCLUSIVE', 'cubic: INCONCLUSIVE'] |
| E97-R2 | f32pi | lap | r 1.0801, se 0.0155, df 3, lo 1.0307, hi 1.1295 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8r0up | pass | r 1.0733, se 0.0130, df 1, lo 0.9085, hi 1.2381 | [0.8, 1.25] | **PASS** | PASS | ['linear: INCONCLUSIVE'] |
| E97-R2 | i8r0up | lap | r 1.0733, se 0.0137, df 3, lo 1.0296, hi 1.1169 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8r6dn | pass | r 1.0647, se 0.0130, df 1, lo 0.8997, hi 1.2298 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8r6dn | lap | r 1.0647, se 0.0142, df 3, lo 1.0195, hi 1.1099 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R2 | i8r6qk | pass | r 1.0823, se 0.0134, df 1, lo 0.9122, hi 1.2523 | [0.8, 1.25] | **INCONCLUSIVE** | PASS |  |
| E97-R2 | i8r6qk | lap | r 1.0823, se 0.0161, df 3, lo 1.0309, hi 1.1336 | [0.8, 1.25] | **PASS** | PASS |  |
| E97-R4 | f32zero | pass | r 1.1292, se 0.0051, df 1, lo 1.0644, hi 1.1940 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32zero | lap | r 1.1292, se 0.0236, df 3, lo 1.0542, hi 1.2041 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16zero | pass | r 1.1299, se 0.0051, df 1, lo 1.0645, hi 1.1953 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16zero | lap | r 1.1299, se 0.0248, df 3, lo 1.0511, hi 1.2087 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32sp90 | pass | r 1.1706, se 0.0121, df 1, lo 1.0175, hi 1.3238 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32sp90 | lap | r 1.1706, se 0.0251, df 3, lo 1.0908, hi 1.2504 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32arbz | pass | r 1.1363, se 0.0035, df 1, lo 1.0918, hi 1.1809 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32arbz | lap | r 1.1363, se 0.0231, df 3, lo 1.0628, hi 1.2099 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32azbr | pass | r 1.1002, se 0.0090, df 1, lo 0.9863, hi 1.2142 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32azbr | lap | r 1.1002, se 0.0300, df 3, lo 1.0046, hi 1.1958 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16sp90 | pass | r 1.1165, se 0.0194, df 1, lo 0.8699, hi 1.3632 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16sp90 | lap | r 1.1165, se 0.0252, df 3, lo 1.0365, hi 1.1966 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16wsp90 | pass | r 1.1449, se 0.0177, df 1, lo 0.9195, hi 1.3704 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16wsp90 | lap | r 1.1449, se 0.0270, df 3, lo 1.0588, hi 1.2310 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16arbz | pass | r 1.1134, se 0.0186, df 1, lo 0.8766, hi 1.3502 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16arbz | lap | r 1.1134, se 0.0250, df 3, lo 1.0339, hi 1.1928 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16azbr | pass | r 1.1380, se 0.0180, df 1, lo 0.9089, hi 1.3670 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16azbr | lap | r 1.1380, se 0.0252, df 3, lo 1.0577, hi 1.2182 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8azbf | pass | r 1.1274, se 0.0060, df 1, lo 1.0515, hi 1.2033 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8azbf | lap | r 1.1274, se 0.0233, df 3, lo 1.0533, hi 1.2016 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8afbz | pass | r 1.1049, se 0.0037, df 1, lo 1.0575, hi 1.1523 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8afbz | lap | r 1.1049, se 0.0224, df 3, lo 1.0335, hi 1.1762 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8wsp90 | pass | r 1.1405, se 0.0123, df 1, lo 0.9842, hi 1.2969 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8wsp90 | lap | r 1.1405, se 0.0245, df 3, lo 1.0626, hi 1.2185 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8sp90 | pass | r 1.1294, se 0.0032, df 1, lo 1.0887, hi 1.1701 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8sp90 | lap | r 1.1294, se 0.0244, df 3, lo 1.0519, hi 1.2069 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8ones | pass | r 1.1400, se 0.0042, df 1, lo 1.0864, hi 1.1937 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8ones | lap | r 1.1400, se 0.0236, df 3, lo 1.0649, hi 1.2151 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8wsp50 | pass | r 1.0821, se 0.0640, df 1, lo 0.2684, hi 1.8958 | [0.7, 1.43] | **INCONCLUSIVE** | PASS |  |
| E97-R4 | i8wsp50 | lap | r 1.0821, se 0.0704, df 3, lo 0.8581, hi 1.3061 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8high | pass | r 1.1603, se 0.0046, df 1, lo 1.1021, hi 1.2184 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8high | lap | r 1.1603, se 0.0700, df 3, lo 0.9375, hi 1.3831 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8tern | pass | r 1.0701, se 0.0160, df 1, lo 0.8672, hi 1.2731 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8tern | lap | r 1.0701, se 0.0389, df 3, lo 0.9464, hi 1.1939 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8pos | pass | r 1.0692, se 0.0285, df 1, lo 0.7068, hi 1.4315 | [0.7, 1.43] | **INCONCLUSIVE** | PASS |  |
| E97-R4 | i8pos | lap | r 1.0692, se 0.0384, df 3, lo 0.9471, hi 1.1912 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8sort | pass | r 1.0211, se 0.0029, df 1, lo 0.9838, hi 1.0584 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8sort | lap | r 1.0211, se 0.0207, df 3, lo 0.9554, hi 1.0868 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16wsp50 | pass | r 1.1392, se 0.0133, df 1, lo 0.9697, hi 1.3087 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16wsp50 | lap | r 1.1392, se 0.0750, df 3, lo 0.9005, hi 1.3780 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32sp50 | pass | r 1.1137, se 0.0153, df 1, lo 0.9192, hi 1.3083 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32sp50 | lap | r 1.1137, se 0.0678, df 3, lo 0.8980, hi 1.3295 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32neg1 | pass | r 1.1433, se 0.0133, df 1, lo 0.9746, hi 1.3120 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32neg1 | lap | r 1.1433, se 0.0622, df 3, lo 0.9452, hi 1.3414 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16neg1 | pass | r 1.1020, se 0.0060, df 1, lo 1.0260, hi 1.1779 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16neg1 | lap | r 1.1020, se 0.0590, df 3, lo 0.9141, hi 1.2898 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16ones | pass | r 1.0911, se 0.0153, df 1, lo 0.8971, hi 1.2851 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f16ones | lap | r 1.0911, se 0.0553, df 3, lo 0.9150, hi 1.2672 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32pi | pass | r 1.1066, se 0.0121, df 1, lo 0.9523, hi 1.2609 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | f32pi | lap | r 1.1066, se 0.0585, df 3, lo 0.9205, hi 1.2927 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8r0up | pass | r 1.0622, se 0.0178, df 1, lo 0.8358, hi 1.2886 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8r0up | lap | r 1.0622, se 0.0366, df 3, lo 0.9458, hi 1.1787 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8r6dn | pass | r 1.0614, se 0.0070, df 1, lo 0.9727, hi 1.1500 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8r6dn | lap | r 1.0614, se 0.0519, df 3, lo 0.8961, hi 1.2266 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8r6qk | pass | r 1.0226, se 0.0211, df 1, lo 0.7546, hi 1.2907 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R4 | i8r6qk | lap | r 1.0226, se 0.0261, df 3, lo 0.9396, hi 1.1057 | [0.7, 1.43] | **PASS** | PASS |  |
| E97-R5 | f32zero | pass | r 1.0734, se 0.0166, df 1, lo 0.8629, hi 1.2839 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f32zero | lap | r 1.0734, se 0.0123, df 3, lo 1.0343, hi 1.1125 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f16zero | pass | r 1.0055, se 0.0066, df 1, lo 0.9219, hi 1.0891 | [0.9, 1.11] | **PASS** | PASS | ['cubic: INCONCLUSIVE'] |
| E97-R5 | f16zero | lap | r 1.0055, se 0.0042, df 3, lo 0.9920, hi 1.0190 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32sp90 | pass | r 1.0313, se 0.0165, df 1, lo 0.8212, hi 1.2414 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f32sp90 | lap | r 1.0313, se 0.0127, df 3, lo 0.9908, hi 1.0718 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32arbz | pass | r 1.0500, se 0.0150, df 1, lo 0.8595, hi 1.2405 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f32arbz | lap | r 1.0500, se 0.0148, df 3, lo 1.0029, hi 1.0972 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32azbr | pass | r 1.0120, se 0.0217, df 1, lo 0.7363, hi 1.2877 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f32azbr | lap | r 1.0120, se 0.0187, df 3, lo 0.9525, hi 1.0715 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16sp90 | pass | r 1.0178, se 0.0140, df 1, lo 0.8395, hi 1.1961 | [0.9, 1.11] | **INCONCLUSIVE** | PASS | ['linear: PASS'] |
| E97-R5 | f16sp90 | lap | r 1.0178, se 0.0084, df 3, lo 0.9909, hi 1.0446 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16wsp90 | pass | r 1.0085, se 0.0171, df 1, lo 0.7918, hi 1.2253 | [0.9, 1.11] | **INCONCLUSIVE** | PASS | ['linear: PASS'] |
| E97-R5 | f16wsp90 | lap | r 1.0085, se 0.0136, df 3, lo 0.9654, hi 1.0517 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16arbz | pass | r 1.0450, se 0.0014, df 1, lo 1.0266, hi 1.0633 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16arbz | lap | r 1.0450, se 0.0101, df 3, lo 1.0127, hi 1.0773 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16azbr | pass | r 1.0320, se 0.0102, df 1, lo 0.9025, hi 1.1615 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f16azbr | lap | r 1.0320, se 0.0066, df 3, lo 1.0109, hi 1.0531 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8azbf | pass | r 1.0032, se 0.0136, df 1, lo 0.8306, hi 1.1758 | [0.9, 1.11] | **INCONCLUSIVE** | PASS | ['cubic: PASS'] |
| E97-R5 | i8azbf | lap | r 1.0032, se 0.0088, df 3, lo 0.9751, hi 1.0313 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8afbz | pass | r 0.9868, se 0.0141, df 1, lo 0.8073, hi 1.1663 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | i8afbz | lap | r 0.9868, se 0.0102, df 3, lo 0.9544, hi 1.0192 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8wsp90 | pass | r 0.9919, se 0.0040, df 1, lo 0.9410, hi 1.0428 | [0.9, 1.11] | **PASS** | PASS | ['linear: INCONCLUSIVE', 'cubic: INCONCLUSIVE'] |
| E97-R5 | i8wsp90 | lap | r 0.9919, se 0.0086, df 3, lo 0.9647, hi 1.0191 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8sp90 | pass | r 1.0139, se 0.0032, df 1, lo 0.9735, hi 1.0544 | [0.9, 1.11] | **PASS** | PASS | ['linear: INCONCLUSIVE', 'cubic: INCONCLUSIVE'] |
| E97-R5 | i8sp90 | lap | r 1.0139, se 0.0107, df 3, lo 0.9798, hi 1.0481 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8ones | pass | r 1.0095, se 0.0018, df 1, lo 0.9862, hi 1.0328 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8ones | lap | r 1.0095, se 0.0068, df 3, lo 0.9879, hi 1.0311 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8wsp50 | pass | r 0.9972, se 0.0115, df 1, lo 0.8507, hi 1.1438 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | i8wsp50 | lap | r 0.9972, se 0.0126, df 3, lo 0.9572, hi 1.0372 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8high | pass | r 1.0057, se 0.0031, df 1, lo 0.9667, hi 1.0447 | [0.9, 1.11] | **PASS** | PASS | ['linear: INCONCLUSIVE', 'cubic: INCONCLUSIVE'] |
| E97-R5 | i8high | lap | r 1.0057, se 0.0037, df 3, lo 0.9940, hi 1.0173 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8tern | pass | r 0.9886, se 0.0058, df 1, lo 0.9154, hi 1.0619 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8tern | lap | r 0.9886, se 0.0065, df 3, lo 0.9678, hi 1.0095 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8pos | pass | r 1.0007, se 0.0013, df 1, lo 0.9838, hi 1.0176 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8pos | lap | r 1.0007, se 0.0019, df 3, lo 0.9948, hi 1.0066 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8sort | pass | r 0.9990, se 0.0041, df 1, lo 0.9474, hi 1.0506 | [0.9, 1.11] | **PASS** | PASS | ['linear: INCONCLUSIVE'] |
| E97-R5 | i8sort | lap | r 0.9990, se 0.0029, df 3, lo 0.9899, hi 1.0081 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16wsp50 | pass | r 0.9969, se 0.0020, df 1, lo 0.9718, hi 1.0220 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16wsp50 | lap | r 0.9969, se 0.0023, df 3, lo 0.9894, hi 1.0044 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32sp50 | pass | r 0.9959, se 0.0054, df 1, lo 0.9278, hi 1.0640 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32sp50 | lap | r 0.9959, se 0.0076, df 3, lo 0.9717, hi 1.0201 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32neg1 | pass | r 0.9958, se 0.0109, df 1, lo 0.8577, hi 1.1339 | [0.9, 1.11] | **INCONCLUSIVE** | PASS |  |
| E97-R5 | f32neg1 | lap | r 0.9958, se 0.0081, df 3, lo 0.9701, hi 1.0215 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16neg1 | pass | r 0.9945, se 0.0028, df 1, lo 0.9583, hi 1.0307 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16neg1 | lap | r 0.9945, se 0.0043, df 3, lo 0.9808, hi 1.0083 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16ones | pass | r 1.0078, se 0.0007, df 1, lo 0.9994, hi 1.0163 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f16ones | lap | r 1.0078, se 0.0028, df 3, lo 0.9988, hi 1.0168 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32pi | pass | r 1.0007, se 0.0039, df 1, lo 0.9513, hi 1.0500 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | f32pi | lap | r 1.0007, se 0.0036, df 3, lo 0.9893, hi 1.0120 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8r0up | pass | r 0.9994, se 0.0071, df 1, lo 0.9093, hi 1.0894 | [0.9, 1.11] | **PASS** | PASS | ['linear: INCONCLUSIVE'] |
| E97-R5 | i8r0up | lap | r 0.9994, se 0.0041, df 3, lo 0.9863, hi 1.0125 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8r6dn | pass | r 0.9906, se 0.0033, df 1, lo 0.9491, hi 1.0321 | [0.9, 1.11] | **PASS** | PASS | ['cubic: INCONCLUSIVE'] |
| E97-R5 | i8r6dn | lap | r 0.9906, se 0.0027, df 3, lo 0.9819, hi 0.9993 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8r6qk | pass | r 1.0070, se 0.0040, df 1, lo 0.9566, hi 1.0574 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R5 | i8r6qk | lap | r 1.0070, se 0.0029, df 3, lo 0.9980, hi 1.0161 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-R3 | f32randn | pass | H 0.1969, spread 0.0047, E89 0.1979 | [0.188, 0.2078] | **PASS** | PASS |  |
| E97-R6 | all blocks | pass | min 0.9868, max 1.0734, sd 0.0202, n 28 | [0.93, 1.07] | **INCONCLUSIVE** | PASS |  |
| E97-R7 | the 25 kinds | lap | median 1.1005, share_in_wide_band 1.0000, min 1.0301, max 1.1427, n 25 | [1.0, 1.2] | **PASS** | PASS |  |
| E97-B0 | H1 | one hold | samples 18000, rate_hz 10.0000, clock_600_share 1.0000, off_600_samples 0, mv_min 522.0000, mv_max 523.0000, launch_failures 0, launches 244, cycles_per_op_off 0, records 3831, with_34_share 1.0000, ok True | gates | **PASS** | PASS |  |
| E97-B0 | H2 | one hold | samples 9000, rate_hz 10.0000, clock_600_share 1.0000, off_600_samples 0, mv_min 522.0000, mv_max 522.0000, launch_failures 0, launches 126, cycles_per_op_off 0, records 1890, with_34_share 1.0000, ok True | gates | **PASS** | PASS |  |
| E97-B0 | H3 | one hold | samples 18000, rate_hz 10.0000, clock_600_share 1.0000, off_600_samples 0, mv_min 520.0000, mv_max 523.0000, launch_failures 0, launches 257, cycles_per_op_off 0, records 2494, with_34_share 1.0000, ok True | gates | **PASS** | PASS |  |
| E97-B1 | H1 | one hold | slope_C_per_min -0.1016, window_s 600.0000, why_end time | |slope| <= 0.02 | **FAIL** | PASS |  |
| E97-B2a | H1 | one hold | R_ol 0.8993, lo 0.8944, hi 0.9043 | [1.25, 1.7] | **FAIL** | FAIL |  |
| E97-B2b | H1 | one hold | R_ol 0.8993, lo 0.8944, hi 0.9043 | [0.217, 0.35] | **FAIL** | FAIL |  |
| E97-B2c | H1 | one hold | R_ol 0.8993, lo 0.8944, hi 0.9043 | [0.7, 1.05] | **PASS** | PASS |  |
| E97-B1 | H2 | one hold | slope_C_per_min -0.0069, window_s 300.0000, why_end time | |slope| <= 0.02 | **PASS** | PASS |  |
| E97-B2a | H2 | one hold | R_ol 0.9212, lo 0.9177, hi 0.9247 | [1.25, 1.7] | **FAIL** | FAIL |  |
| E97-B2b | H2 | one hold | R_ol 0.9212, lo 0.9177, hi 0.9247 | [0.217, 0.35] | **FAIL** | FAIL |  |
| E97-B2c | H2 | one hold | R_ol 0.9212, lo 0.9177, hi 0.9247 | [0.7, 1.05] | **PASS** | PASS |  |
| E97-B1 | H3 | one hold | slope_C_per_min 0.0252, window_s 600.0000, why_end time | |slope| <= 0.02 | **FAIL** | PASS |  |
| E97-B2a | H3 | one hold | R_ol 0.8767, lo 0.8680, hi 0.8854 | [1.25, 1.7] | **FAIL** | FAIL |  |
| E97-B2b | H3 | one hold | R_ol 0.8767, lo 0.8680, hi 0.8854 | [0.217, 0.35] | **FAIL** | FAIL |  |
| E97-B2c | H3 | one hold | R_ol 0.8767, lo 0.8680, hi 0.8854 | [0.7, 1.05] | **PASS** | PASS |  |
| E97-B3 | H3/H1 | one hold | ratio 0.9748, lo 0.9638, hi 0.9859 | [0.85, 1.15] | **PASS** | PASS |  |
| E97-B4 | H3/H1 | one hold | ratio 1.0422, lo 1.0316, hi 1.0528 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-B3 | H2/H1 | one hold | ratio 1.0243, lo 1.0175, hi 1.0312 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-B4 | H2/H1 | one hold | ratio 1.0388, lo 1.0328, hi 1.0449 | [0.9, 1.11] | **PASS** | PASS |  |
| E97-B5 | H3/H1 | one hold | ratio 1.0396, lo 1.0346, hi 1.0447, pred_ratio 1.0590 | [1.02, 1.25] | **PASS** | PASS |  |
| E97-B6 | H1 by 60 s | one hold | share 0.4533, lo 0.4513, hi 0.4554 | [0.33, 0.57] | **PASS** | PASS |  |
| E97-B6 | H1 by 300 s | one hold | share 0.9024, lo 0.8983, hi 0.9065 | [0.77, 0.97] | **PASS** | PASS |  |
| E97-B7 | 51-58 | one hold | slope 0.3080, lo 0.3066, hi 0.3106, n_coolings 3 | [0.288, 0.352] | **PASS** | PASS |  |
| E97-B7 | 58-62 | one hold | slope 0.3812, lo 0.3812, hi 0.3812, n_coolings 1 | [0.3423, 0.4183] | **PASS** | PASS |  |
| E97-B8 | H1 leak share | one hold | share 0.2978, dP_leak_W 3.9090 | [0.224, 0.384] | **PASS** | PASS |  |
| E97-B8 | H1 loop gain | one hold | loop_gain 0.3634, k_W_per_C 0.4041 | [0.256, 0.456] | **PASS** | PASS |  |
| E97-B9 | H1 | one hold | closure 0.9895 | [0.85, 1.15] | **PASS** | PASS |  |
| E97-B8 | H2 leak share | one hold | share 0.3131, dP_leak_W 4.4755 | [0.228, 0.388] | **PASS** | PASS |  |
| E97-B8 | H2 loop gain | one hold | loop_gain 0.3880, k_W_per_C 0.4212 | [0.264, 0.464] | **PASS** | PASS |  |
| E97-B9 | H2 | one hold | closure 0.9908 | [0.85, 1.15] | **PASS** | PASS |  |
| E97-B8 | H3 leak share | one hold | share 0.3338, dP_leak_W 7.5073 | [0.263, 0.423] | **PASS** | PASS |  |
| E97-B8 | H3 loop gain | one hold | loop_gain 0.4405, k_W_per_C 0.5025 | [0.344, 0.544] | **PASS** | PASS |  |
| E97-B9 | H3 | one hold | closure 1.0013 | [0.85, 1.15] | **PASS** | PASS |  |
| E97-B10 | H3 | one hold | stop_s 221.3090, die_c 78.0000 | [150.0, 480.0] | **PASS** | PASS |  |

Tally: {'primary': {'PASS': 107, 'INCONCLUSIVE': 36, 'FAIL': 8}, 'lap_unit_beside': {'PASS': 112, 'INCONCLUSIVE': 1}, 'by_rule_primary': {'E97-R0': {'PASS': 1}, 'E97-R1': {'PASS': 29}, 'E97-R2': {'INCONCLUSIVE': 22, 'PASS': 6}, 'E97-R4': {'PASS': 26, 'INCONCLUSIVE': 2}, 'E97-R5': {'INCONCLUSIVE': 11, 'PASS': 17}, 'E97-R3': {'PASS': 1}, 'E97-R6': {'INCONCLUSIVE': 1}, 'E97-R7': {'PASS': 1}, 'E97-B0': {'PASS': 3}, 'E97-B1': {'FAIL': 2, 'PASS': 1}, 'E97-B2a': {'FAIL': 3}, 'E97-B2b': {'FAIL': 3}, 'E97-B2c': {'PASS': 3}, 'E97-B3': {'PASS': 2}, 'E97-B4': {'PASS': 2}, 'E97-B5': {'PASS': 1}, 'E97-B6': {'PASS': 2}, 'E97-B7': {'PASS': 2}, 'E97-B8': {'PASS': 6}, 'E97-B9': {'PASS': 3}, 'E97-B10': {'PASS': 1}}}

