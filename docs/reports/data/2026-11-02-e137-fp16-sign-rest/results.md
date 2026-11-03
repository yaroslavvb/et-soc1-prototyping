# E137 results

Reading: **S1** (set-aside rule); passes ['13711', '13712', '13713', '13714', '13715', '13716']; S1 kept ['13711', '13712', '13713', '13714', '13715', '13716']; set aside [{'pass': 13710, 'why': ['int8.zeros departs +0.279 W from its straight line']}]; leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}

| rule | verdict | quantity | measured | n | M4 | arm-sensitive at |
|---|---|---|---:|---:|---:|---|
| E137-R1 | **MOST** | `fp16.share_het_m` | 1.001 ± 0.055 | 6 | 1.042 | — |
| E137-R2 | **ALMOST NONE** | `fp16.share_walk_m` | -0.001 ± 0.055 | 6 | -0.042 | dips_kept, leak0 |
| E137-R3 | **MOST** | `fp16.share_het_z` | 1.026 ± 0.053 | 6 | 1.045 | — |
| E137-R4 | **INCONCLUSIVE** | `fp16.design_m` | -0.026 ± 0.103 | 6 | -0.004 | leak0.3803 |
| E137-R5 | **PASS** | `fp16.step` | 4.802 ± 0.173 W | 6 | E108 4.981 | — |
| E137-R6 | **PASS** | rms(D − M4), 8 items | 0.130 W, bias +0.089 W | | | — |
| E137-R7 | **PASS** | M4's seven sign contrasts | rms 0.125 W, 0 outside | | | — |
| E137-R8 | **INCONCLUSIVE** | against E128's two passes | share_het_m INCONCLUSIVE (d +0.075, h 0.312); share_walk_m INCONCLUSIVE (d -0.075, h 0.312); share_het_z INCONCLUSIVE (d +0.020, h 0.130) | | | — |
| E137-S1 | **PASS** | session tie | fp32.randn 23.97 (24.00 ± 0.5); fp16.randn 21.57 (21.49 ± 0.5); anchor_pi 8.17 (8.14 ± 0.5); int8.full 6.94 (6.84 ± 0.25) | | | leak0, leak0.545 |

## Every quantity, per pass, t intervals

| quantity | form | measured | n | M4 ± half95 | per pass |
|---|---|---:|---:|---:|---|
| `fp16.step` | contrast | 4.802 ± 0.173 | 6 | 4.854 ± 0.55 | 4.921, 4.672, 4.737, 4.929, 4.573, 4.981 |
| `fp16.held_z` | contrast | 2.022 ± 0.230 | 6 | 2.201 ± 0.50 | 2.255, 2.047, 1.735, 2.216, 1.780, 2.101 |
| `fp16.rest_vs_z` | contrast | 2.780 ± 0.149 | 6 | 2.653 ± 0.74 | 2.667, 2.625, 3.002, 2.713, 2.793, 2.880 |
| `fp16.Bz_het` | contrast | 3.692 ± 0.119 | 6 | 3.532 ± 0.58 | 3.623, 3.771, 3.884, 3.587, 3.649, 3.636 |
| `fp16.Bz_walk` | contrast | -0.091 ± 0.189 | 6 | -0.153 ± 0.64 | -0.054, -0.175, -0.305, 0.150, 0.078, -0.240 |
| `fp16.Bz_rest` | contrast | 3.600 ± 0.131 | 6 | 3.379 ± 0.60 | 3.569, 3.596, 3.579, 3.736, 3.726, 3.396 |
| `fp16.Bm_het` | contrast | 3.321 ± 0.130 | 6 | 3.398 ± 0.52 | 3.392, 3.155, 3.284, 3.466, 3.418, 3.210 |
| `fp16.Bm_walk` | contrast | 0.002 ± 0.193 | 6 | -0.136 ± 0.52 | -0.133, 0.028, 0.337, -0.186, -0.051, 0.020 |
| `fp16.Bm_rest` | contrast | 3.323 ± 0.166 | 6 | 3.262 ± 0.52 | 3.259, 3.183, 3.621, 3.280, 3.367, 3.230 |
| `fp16.held_alt` | contrast | 0.371 ± 0.219 | 6 | 0.134 ± 0.57 | 0.231, 0.617, 0.600, 0.121, 0.231, 0.425 |
| `fp16.walk_alt` | contrast | 0.277 ± 0.195 | 6 | 0.117 ± 0.60 | 0.310, 0.413, -0.042, 0.457, 0.360, 0.165 |
| `fp16.share_z` | ratio | 0.421 ± 0.038 | 6 | 0.453 | 0.458, 0.438, 0.366, 0.450, 0.389, 0.422 |
| `fp16.share_het_z` | ratio | 1.026 ± 0.053 | 6 | 1.045 | 1.015, 1.049, 1.085, 0.960, 0.979, 1.071 |
| `fp16.share_het_m` | ratio | 1.001 ± 0.055 | 6 | 1.042 | 1.041, 0.991, 0.907, 1.057, 1.015, 0.994 |
| `fp16.share_walk_m` | ratio | -0.001 ± 0.055 | 6 | -0.042 | -0.041, 0.009, 0.093, -0.057, -0.015, 0.006 |
| `fp16.rest_ratio_m` | ratio | 1.196 ± 0.039 | 6 | 1.230 | 1.222, 1.212, 1.206, 1.209, 1.205, 1.122 |
| `fp16.design_m` | diff | -0.026 ± 0.103 | 6 | -0.004 | 0.026, -0.058, -0.178, 0.097, 0.036, -0.077 |

## The items against M4 (R6)

| item | D, W | n | M4 [95%] | D − M4 |
|---|---:|---:|---:|---:|
| `fp16.b_B_w` | 13.832 ± 0.146 | 6 | 13.62 [13.14, 14.10] | +0.209 |
| `fp16.b_B_wm` | 13.554 ± 0.107 | 6 | 13.51 [13.12, 13.89] | +0.049 |
| `fp16.b_B_z` | 13.923 ± 0.177 | 6 | 13.78 [13.33, 14.22] | +0.147 |
| `fp16.b_B_zm` | 13.552 ± 0.109 | 6 | 13.64 [13.26, 14.02] | -0.089 |
| `fp16.c_abs` | 8.209 ± 0.193 | 6 | 8.04 [7.67, 8.42] | +0.167 |
| `fp16.ones` | 8.217 ± 0.163 | 6 | 8.07 [7.70, 8.44] | +0.148 |
| `fp16.signs` | 13.019 ± 0.094 | 6 | 12.92 [12.50, 13.34] | +0.096 |
| `fp16.z_s` | 10.231 ± 0.137 | 6 | 10.24 [9.87, 10.62] | -0.012 |

## M4's sign contrasts out of sample (R7)

| contrast | measured, W | M4 ± half95 | error | inside |
|---|---:|---:|---:|---|
| `fp16.step` | 4.802 ± 0.173 | 4.854 ± 0.55 | -0.052 | True |
| `fp16.Bz_het` | 3.692 ± 0.119 | 3.532 ± 0.58 | +0.159 | True |
| `fp16.Bz_walk` | -0.091 ± 0.189 | -0.153 ± 0.64 | +0.062 | True |
| `fp16.Bz_rest` | 3.600 ± 0.131 | 3.379 ± 0.60 | +0.221 | True |
| `fp16.Bm_het` | 3.321 ± 0.130 | 3.398 ± 0.52 | -0.078 | True |
| `fp16.Bm_walk` | 0.002 ± 0.193 | -0.136 ± 0.52 | +0.138 | True |
| `fp16.Bm_rest` | 3.323 ± 0.166 | 3.262 ± 0.52 | +0.061 | True |

## Arms (each on its own kept passes, S1 only)

| arm | passes | E137-R1 | E137-R2 | E137-R3 | E137-R4 | E137-R5 | E137-R6 | E137-R7 | E137-R8 | E137-S1 |
|---|---|---|---|---|---|---|---|---|---|---|
| dips_kept | 5 | MOST | INCONCLUSIVE | MOST | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| gates_off | 7 | MOST | ALMOST NONE | MOST | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| auto | 6 | MOST | ALMOST NONE | MOST | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| leak0.1994 | 6 | MOST | ALMOST NONE | MOST | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| leak0.3803 | 7 | MOST | ALMOST NONE | MOST | ALIKE | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| leak0.545 | 6 | MOST | ALMOST NONE | MOST | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | FAIL |
| leak0 | 5 | MOST | INCONCLUSIVE | MOST | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | FAIL |

## Pooled with E128's two passes (reported arm, no verdict of its own)

| quantity | pooled | n | bands, if scored |
|---|---:|---:|---|
| `fp16.share_het_m` | 0.982 ± 0.048 | 8 | MOST |
| `fp16.share_walk_m` | 0.018 ± 0.048 | 8 | ALMOST NONE |
| `fp16.share_het_z` | 1.021 ± 0.037 | 8 | MOST |
| `fp16.design_m` | -0.039 ± 0.073 | 8 | INCONCLUSIVE |
| `fp16.Bm_het` | 3.257 ± 0.133 | 8 |  |
| `fp16.Bm_walk` | 0.064 ± 0.165 | 8 |  |
| `fp16.Bm_rest` | 3.320 ± 0.116 | 8 |  |
| `fp16.Bz_rest` | 3.564 ± 0.111 | 8 |  |
| `fp16.step` | 4.787 ± 0.144 | 7 |  |
