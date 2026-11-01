# E115 results (written by score_e115.py)

Passes kept: [11510, 11511, 11512]; set aside: []; leak {'mode': 'auto', 'k_w_per_c': 0.23062500000000857, 'n_runs': 97}; arm: dips removed (E82 A2)

| rule | verdict | anchor footing | nodips_leak0.1994 | nodips_leak0.3803 | nodips_leak0 | gates_off | numbers |
|---|---|---|---|---|---|---|---|
| E115-R1 | **FAIL** | PASS | FAIL | FAIL | FAIL | FAIL | {'n': 16, 'rms_w': 0.2905, 'bias_pred_minus_meas_w': -0.0238, 'rms_M4_w': 0.3206, 'interval': [0.1349, 0.2876]} |
| E115-R2 | **PASS** | PASS | PASS | PASS | PASS | PASS | {'n': 6, 'rms_w': 0.3433, 'bias_pred_minus_meas_w': 0.2017, 'rms_M4_w': 0.3938, 'interval': [0.1243, 0.4323]} |
| E115-R3 | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | FAIL | INCONCLUSIVE | {'n': 25, 'inside': 18, 'fraction': 0.72} |
| E115-R4 | **FAIL** | FAIL | FAIL | FAIL | INCONCLUSIVE | FAIL | {'n': 7, 'inside': 4, 'fraction': 0.5714} |
| E115-R5 | **UNRESOLVED** | M5 BETTER | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | {'gap_w': 0.0301, 'lo95': -0.0049, 'hi95': 0.0742, 'n': 16, 'rms_M5_w': 0.2905, 'rms_M4_w': 0.3206} |
| E115-S1 | **PASS** | PASS | PASS | FAIL | FAIL | PASS | {} |

| tile | open case | prio | D, W (95%) | **M5 [95%]** | D − M5 | M4 | D − M4 | F0r |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fp16.a_mant_b_randn` | a-side-busy-partner | 1 | 21.65 ± 0.06 | **21.78** [21.43, 22.14] | -0.13 | 21.97 | -0.32 | 21.92 |
| `fp32.a_colconst_b_randn` ⚠ | a-side-busy-partner | 2 | 22.69 ± 0.05 | **23.17** [22.72, 23.61] | -0.48 | 23.15 | -0.46 | 23.07 |
| `fp32.a_lo8_b_pi` | a-side-busy-partner | 1 | 10.58 ± 0.12 | **10.68** [10.29, 11.07] | -0.10 | 10.82 | -0.23 | 10.72 |
| `fp32.a_lo8_b_randn` | a-side-busy-partner | 1 | 22.29 ± 0.44 | **22.23** [21.80, 22.65] | +0.06 | 22.18 | +0.12 | 22.10 |
| `int8.a_colconst_b_full` ⚠ | a-side-busy-partner | 2 | 2.42 ± 0.10 | **3.17** [2.50, 3.84] | -0.75 | 3.30 | -0.87 | 3.17 |
| `int8.a_low2_b_full` | a-side-busy-partner | 1 | 4.70 ± 0.26 | **4.82** [4.29, 5.36] | -0.13 | 4.87 | -0.17 | 4.82 |
| `int8.st_f32bytes` | another-stream | 2 | 6.86 ± 0.11 | **6.69** [6.22, 7.16] | +0.16 | 6.63 | +0.23 | 6.69 |
| `fp16.x_logu_s50` | exponents-spread-gate | 1 | 7.63 ± 0.10 | **7.71** [7.35, 8.07] | -0.08 | 7.69 | -0.06 | 7.72 |
| `fp32.x_logu_bsteady` ⚠ | exponents-spread-gate | 2 | 13.12 ± 0.07 | **13.88** [13.49, 14.26] | -0.76 | 13.82 | -0.70 | 13.78 |
| `fp32.x_logu_s50` | exponents-spread-gate | 1 | 8.10 ± 0.10 | **8.27** [7.88, 8.66] | -0.16 | 8.20 | -0.09 | 8.22 |
| `fp16.g_blanes_alt` ⚠ | gated-kinds | 2 | 13.13 ± 0.20 | **12.44** [12.08, 12.80] | +0.69 | 12.46 | +0.68 | 12.48 |
| `fp32.g_arows_alt` | gated-kinds | 1 | 13.48 ± 0.12 | **13.29** [12.90, 13.69] | +0.19 | 13.24 | +0.25 | 13.22 |
| `fp32.g_blanes_alt` ⚠ | gated-kinds | 1 | 14.47 ± 0.14 | **14.00** [13.60, 14.40] | +0.48 | 13.94 | +0.54 | 13.94 |
| `fp32.g_blanes_steady` ⚠ | gated-kinds | 1 | 12.47 ± 0.12 | **13.22** [12.83, 13.60] | -0.74 | 13.21 | -0.74 | 13.16 |
| `int8.g_awords_alt` | gated-kinds | 1 | 4.45 ± 0.32 | **4.71** [4.24, 5.17] | -0.26 | 4.69 | -0.24 | 4.71 |
| `int8.g_bpairs_steady` | gated-kinds | 1 | 3.55 ± 0.26 | **3.76** [3.30, 4.21] | -0.20 | 3.71 | -0.16 | 3.76 |
| `fp32.m_blines_eq` | memory-path | 1 | 24.77 ± 0.06 | **24.80** [24.40, 25.20] | -0.03 | 24.79 | -0.02 | 24.70 |
| `fp32.m_bpair_eq` | memory-path | 1 | 16.39 ± 0.08 | **16.42** [16.03, 16.80] | -0.03 | 16.48 | -0.09 | 16.38 |
| `fp16.s_inword0` | signs-moving-sums | 1 | 16.49 ± 0.07 | **16.68** [16.34, 17.02] | -0.19 | 16.88 | -0.39 | 16.80 |
| `fp16.s_wpair0` ⚠ (flag) | signs-moving-sums | 1 | 21.86 ± 0.15 | **21.44** [21.08, 21.81] | +0.41 | 21.56 | +0.30 | 21.51 |
| `fp32.s_bridge` | signs-moving-sums | 1 | 25.67 ± 0.11 | **25.32** [24.93, 25.72] | +0.35 | 25.27 | +0.40 | 25.19 |
| `fp32.s_drift12` | signs-moving-sums | 1 | 24.78 ± 0.24 | **24.70** [24.30, 25.11] | +0.07 | 24.71 | +0.07 | 24.61 |
| `fp32.s_pair0` | signs-moving-sums | 1 | 25.00 ± 0.14 | **24.64** [24.25, 25.03] | +0.36 | 24.62 | +0.38 | 24.54 |
| `fp32.z_single` | zero-level | 1 | -0.06 ± 0.05 | **0.01** [-0.36, 0.39] | -0.08 | 0.01 | -0.08 | 0.01 |
| `int8.z_diag` | zero-level | 1 | 1.81 ± 0.22 | **1.85** [1.39, 2.31] | -0.04 | 1.88 | -0.07 | 1.85 |

| contrast | measured, W (95%) | **M5 [95%]** | verdict | M4 |
|---|---:|---:|---|---:|
| fp32.g_blanes_alt - fp32.g_blanes_steady | +2.00 ± 0.09 | **+0.78** [+0.23, +1.34] | ABOVE | +0.73 |
| fp32.a_lo8_b_randn - fp32.a_lo8_b_pi | +11.71 ± 0.48 | **+11.55** [+10.97, +12.12] | INSIDE | +11.36 |
| fp32.m_blines_eq - fp32.m_bpair_eq | +8.39 ± 0.12 | **+8.38** [+7.82, +8.94] | INSIDE | +8.31 |
| fp32.s_drift12 - fp32.s_pair0 | -0.22 ± 0.29 | **+0.06** [-0.50, +0.63] | INSIDE | +0.08 |
| fp32.s_bridge - fp32.s_pair0 | +0.67 ± 0.20 | **+0.68** [+0.12, +1.24] | INSIDE | +0.65 |
| fp32.x_logu_s50 - fp32.x_logu_bsteady | -5.01 ± 0.08 | **-5.61** [-6.16, -5.06] | ABOVE | -5.62 |
| fp16.s_wpair0 - fp16.s_inword0 | +5.37 ± 0.21 | **+4.76** [+4.26, +5.26] | ABOVE | +4.68 |

## Reported (no verdict)

- floats, priority 1 (n = 16): M5 rms 0.291 W, bias -0.024; M4 rms 0.321 W, bias -0.002; F0r rms 0.324 W, bias -0.053
- floats, all (n = 19): M5 rms 0.373 W, bias +0.009; M4 rms 0.384 W, bias +0.024; F0r rms 0.377 W, bias -0.024
- fp32, priority 1 (n = 12): M5 rms 0.305 W, bias -0.031; M4 rms 0.329 W, bias -0.042; F0r rms 0.340 W, bias -0.096
- fp16, priority 1 (n = 4): M5 rms 0.241 W, bias -0.003; M4 rms 0.295 W, bias +0.117; F0r rms 0.271 W, bias +0.077
- fp32, all (n = 14): M5 rms 0.371 W, bias +0.062; M4 rms 0.378 W, bias +0.047; F0r rms 0.376 W, bias -0.008
- fp16, all (n = 5): M5 rms 0.376 W, bias -0.141; M4 rms 0.401 W, bias -0.041; F0r rms 0.381 W, bias -0.070
- int8 (n = 6): M5 rms 0.343 W, bias +0.202; M4 rms 0.394 W, bias +0.214; F0r rms 0.343 W, bias +0.202
- every tile (n = 25): M5 rms 0.366 W, bias +0.055; M4 rms 0.387 W, bias +0.070; F0r rms 0.369 W, bias +0.030
- per_format_term: gap +0.0336 W [-0.0035, +0.0782], n 16
- refit: gap -0.0035 W [-0.0349, +0.0238], n 16
- int8_M5_vs_M4: gap +0.0505 W [-0.0143, +0.0920], n 6

| open case | n | mean D − M5, W (95% over tiles) | rms M5 | rms M4 | inside |
|---|---:|---:|---:|---:|---|
| a-side-busy-partner | 6 | -0.252 ± 0.315 | 0.372 | 0.443 | 4 of 6 |
| another-stream | 1 | +0.163 ± — | 0.163 | 0.226 | 1 of 1 |
| exponents-spread-gate | 3 | -0.336 ± 0.921 | 0.452 | 0.410 | 2 of 3 |
| gated-kinds | 6 | +0.025 ± 0.554 | 0.483 | 0.489 | 3 of 6 |
| memory-path | 2 | -0.029 ± 0.033 | 0.029 | 0.068 | 2 of 2 |
| signs-moving-sums | 5 | +0.201 ± 0.317 | 0.304 | 0.333 | 4 of 5 |
| zero-level | 2 | -0.059 ± 0.225 | 0.062 | 0.074 | 2 of 2 |
