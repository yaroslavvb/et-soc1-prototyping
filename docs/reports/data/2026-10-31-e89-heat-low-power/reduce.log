# E89 results (reduce_e89.py)

passes: [8910, 8911]; samples 22976, with all 34 sensors 1.0000, floor(mean of 34) == firmware mean 0.9809; reference phase -35.2 deg

| block | kind vs ref | E78 W | laps | P fund (W) | P fund / (2/pi) E78 W | T fund (C) +-95% | H (C/W) +-95% | r = H/H_ref [95%] | T fund, whole-degree mean (C) +-95% | step2 (C) +-95% | step2/W | swing30 (C) +-95% | sensor corr with ref |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| i8full | int8.full vs int8.zeros | 7.056 | 4 | 4.327 | 0.963 | 0.899 +- 0.026 | 0.2077 +- 0.0042 | 1.050 [1.019, 1.080] | 0.883 +- 0.151 | 0.863 +- 0.073 | 0.1223 | 1.891 +- 0.106 | 1.0 |
| i8gauss | int8.gauss_q vs int8.zeros | 6.598 | 4 | 4.066 | 0.968 | 0.837 +- 0.015 | 0.2060 +- 0.0092 | 1.041 [0.989, 1.092] | 0.828 +- 0.066 | 0.820 +- 0.151 | 0.1243 | 1.743 +- 0.057 | 0.999 |
| i8small | int8.smallint vs int8.zeros | 6.003 | 4 | 3.703 | 0.969 | 0.776 +- 0.021 | 0.2095 +- 0.0069 | 1.059 [1.017, 1.100] | 0.825 +- 0.063 | 0.725 +- 0.073 | 0.1207 | 1.614 +- 0.054 | 0.999 |
| i8sp50 | int8.sparse50 vs int8.zeros | 5.463 | 4 | 3.408 | 0.980 | 0.718 +- 0.024 | 0.2107 +- 0.0028 | 1.065 [1.038, 1.091] | 0.699 +- 0.229 | 0.673 +- 0.078 | 0.1232 | 1.476 +- 0.035 | 0.999 |
| i8neg1 | int8.neg_ones vs int8.zeros | 1.628 | 4 | 1.126 | 1.086 | 0.232 +- 0.011 | 0.2064 +- 0.0147 | 1.043 [0.965, 1.120] | 0.347 +- 0.418 | 0.222 +- 0.026 | 0.1361 | 0.461 +- 0.013 | 0.996 |
| i8zero | int8.zeros vs idle | 2.605 | 4 | 1.634 | 0.985 | 0.360 +- 0.008 | 0.2202 +- 0.0082 | 1.113 [1.065, 1.160] | 0.411 +- 0.207 | 0.340 +- 0.006 | 0.1304 | 0.671 +- 0.028 | 0.999 |
| f32ones | fp32.ones vs fp32.zeros | 8.257 | 4 | 5.089 | 0.968 | 1.071 +- 0.023 | 0.2104 +- 0.0046 | 1.063 [1.031, 1.095] | 1.058 +- 0.199 | 1.059 +- 0.164 | 0.1282 | 2.169 +- 0.037 | 1.0 |
| f32randn | fp32.randn vs fp32.zeros | 24.725 | 4 | 15.321 | 0.973 | 3.032 +- 0.056 | 0.1979 +- 0.0041 | 1.000 [0.971, 1.029] | 3.028 +- 0.067 | 2.920 +- 0.194 | 0.1181 | 6.225 +- 0.035 | 1.0 |

## Verdicts

| rule | cell | measured | band | verdict |
|---|---|---|---|---|
| E89-R0 | per-sensor reading (command 74) | share_with_34 1.0000, share_floor_mean_eq_firmware 0.9809 | share_with_34 >= 0.99 and floor(mean) == firmware in >= 0.95 | **PASS** |
| E89-R1 | i8full | T_fund_C 0.8987, ci95 0.0260, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | i8gauss | T_fund_C 0.8371, ci95 0.0149, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | i8small | T_fund_C 0.7755, ci95 0.0213, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | i8sp50 | T_fund_C 0.7180, ci95 0.0239, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | i8neg1 | T_fund_C 0.2318, ci95 0.0112, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | i8zero | T_fund_C 0.3597, ci95 0.0081, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | f32ones | T_fund_C 1.0706, ci95 0.0234, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R1 | f32randn | T_fund_C 3.0317, ci95 0.0563, n_laps 4 | 95% lower bound > 0 | **PASS** |
| E89-R2 | i8full | r 1.050 [1.019, 1.080] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R2 | i8gauss | r 1.041 [0.989, 1.092] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R2 | i8small | r 1.059 [1.017, 1.100] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R2 | i8sp50 | r 1.065 [1.038, 1.091] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R2 | i8neg1 | r 1.043 [0.965, 1.120] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R2 | i8zero | r 1.113 [1.065, 1.160] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R2 | f32ones | r 1.063 [1.031, 1.095] | 95% interval inside [0.8, 1.25] | **PASS** |
| E89-R3 | f32randn | H 0.1979, ci95 0.0041 | 95% interval overlaps [0.141, 0.264] degC/W | **PASS** |
| E89-R4 | i8full | r 1.035 [0.924, 1.147] | 95% interval inside [0.7, 1.43] | **PASS** |
| E89-R4 | i8gauss | r 1.052 [0.846, 1.259] | 95% interval inside [0.7, 1.43] | **PASS** |
| E89-R4 | i8small | r 1.022 [0.898, 1.146] | 95% interval inside [0.7, 1.43] | **PASS** |
| E89-R4 | i8sp50 | r 1.043 [0.904, 1.183] | 95% interval inside [0.7, 1.43] | **PASS** |
| E89-R4 | i8neg1 | r 1.153 [0.998, 1.307] | 95% interval inside [0.7, 1.43] | **PASS** |
| E89-R4 | i8zero | r 1.104 [1.028, 1.180] | 95% interval inside [0.7, 1.43] | **PASS** |
| E89-R4 | f32ones | r 1.086 [0.902, 1.269] | 95% interval inside [0.7, 1.43] | **PASS** |

Tally: {'PASS': 24}

