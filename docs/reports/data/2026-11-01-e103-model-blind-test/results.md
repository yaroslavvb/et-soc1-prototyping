# E103 results

Passes kept: [10310, 10311, 10312]; set aside: []; leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}

| rule | verdict | dips_kept | gates_off | auto | leak0.1994 | leak0.3803 | leak0.545 | leak0 | numbers |
|---|---|---|---|---|---|---|---|---|---|
| E103-R1 | **PASS** | PASS | PASS | PASS | PASS | PASS | INCONCLUSIVE | INCONCLUSIVE | {'n': 23, 'rms_w': 0.314, 'rms_lo95': 0.197, 'rms_hi95': 0.425, 'bias_w': -0.053} |
| E103-R2 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {'gap_w': 3.646, 'lo95': 2.142, 'hi95': 5.435, 'n': 23, 'rms_model_w': 0.314, 'rms_null_w': 3.96} |
| E103-R3 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {'gap_w': 1.462, 'lo95': 0.324, 'hi95': 2.567, 'n': 23, 'rms_model_w': 0.314, 'rms_null_w': 1.775} |
| E103-R4 | **PASS** | INCONCLUSIVE | PASS | INCONCLUSIVE | PASS | INCONCLUSIVE | INCONCLUSIVE | PASS | {'n': 7, 'rms_w': 0.365, 'rms_lo95': 0.2, 'rms_hi95': 0.524, 'bias_w': 0.147} |
| E103-R5 | **PASS** | INCONCLUSIVE | PASS | PASS | PASS | PASS | INCONCLUSIVE | PASS | {'gap_w': 0.542, 'lo95': 0.07, 'hi95': 0.99, 'n': 7, 'rms_model_w': 0.365, 'rms_null_w': 0.907} |
| E103-R6 | **PASS** | PASS | PASS | PASS | PASS | PASS | INCONCLUSIVE | PASS | {'gap_w': 0.265, 'lo95': 0.162, 'hi95': 0.364, 'n': 23, 'rms_model_w': 0.314, 'rms_null_w': 0.579} |
| E103-R7 | **PASS** | INCONCLUSIVE | PASS | PASS | PASS | INCONCLUSIVE | FAIL | FAIL | {'n': 30, 'fraction': 0.833} |
| E103-R8 | **UNRESOLVED** | UNRESOLVED | UNRESOLVED | PERSISTS | UNRESOLVED | PERSISTS | PERSISTS | UNRESOLVED | {'n': 5, 'mean_measured_over_predicted': 0.947, 'halfwidth': 0.037} |
| E103-R9 | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'n': 5, 'mean_measured_minus_predicted_w': 0.151, 'halfwidth_w': 0.382, 'M2_same': 0.598} |
| E103-S1 | **PASS** | PASS | PASS | PASS | PASS | PASS | FAIL | FAIL | {} |

| tile | group | D, W (95%) | M [95%] | M2 | Mall | Q130(n) | flop | gate law |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fp16.h_a_all` | A side (named weak spot) | 12.39 ± 0.32 | 12.48 [12.10, 12.86] | 12.81 | 12.48 | 16.32 | 11.08 | 21.49 |
| `fp16.x_e_s` | combinations | 23.49 ± 0.17 | 23.42 [23.04, 23.79] | 23.33 | 23.41 | 21.47 | 26.08 | 21.49 |
| `fp16.e_ab` | exponent spread | 13.32 ± 0.33 | 13.68 [13.28, 14.08] | 13.19 | 13.67 | 16.40 | 13.47 | 21.49 |
| `fp16.f_hi1` | fp16's two elements | 15.85 ± 0.23 | 15.93 [15.56, 16.30] | 15.80 | 15.93 | 17.40 | 15.66 | 21.49 |
| `fp16.g_bcol500` | gate share (named weak spot) | 11.79 ± 0.17 | 12.02 [11.66, 12.38] | 11.83 | 12.02 | 9.75 | 11.61 | 10.75 |
| `fp16.g_relu_shift15` | gate share, operands moving on closed lanes | 4.24 ± 0.20 | 4.13 [3.77, 4.49] | 3.34 | 4.14 | 2.74 | 4.25 | 3.27 |
| `fp16.c_near8` | near-cancelling sums | 17.75 ± 0.32 | 17.55 [17.14, 17.97] | 17.37 | 17.55 | 13.75 | 17.23 | 21.49 |
| `fp16.o_a_maxflip_1` | order | 11.31 ± 0.26 | 11.37 [10.98, 11.77] | 11.65 | 11.38 | 14.67 | 10.37 | 21.49 |
| `fp16.s_arow_adds` | sign structure: moving sums, adder rarely alternates | 19.42 ± 0.40 | 19.52 [19.14, 19.91] | 19.40 | 19.52 | 21.78 | 18.99 | 21.49 |
| `fp16.t_10_1` | truncated mantissas | 18.51 ± 0.11 | 18.53 [18.15, 18.91] | 18.52 | 18.52 | 20.94 | 17.96 | 21.49 |
| `fp32.z_dn_ab` | -0.0 and denormal words | 9.42 ± 0.26 | 9.48 [9.11, 9.86] | 9.19 | 9.50 | 23.19 | 16.78 | 24.00 |
| `fp32.h_a_all_pi` | A side (named weak spot) | 14.31 ± 0.29 | 14.81 [14.35, 15.27] | 15.45 | 14.81 | 17.72 | 14.53 | 24.00 |
| `fp32.h_a_lo_pi` | A side (named weak spot) | 10.52 ± 0.33 | 10.71 [10.30, 11.11] | 11.15 | 10.71 | 15.05 | 11.81 | 24.00 |
| `fp32.o_a_maxflip_4_pi` | A's order (named weak spot, E60's pair) | 10.32 ± 0.16 | 10.53 [10.14, 10.91] | 10.96 | 10.53 | 14.53 | 11.86 | 24.00 |
| `fp32.x_e_g` | combinations | 14.79 ± 0.40 | 14.17 [13.81, 14.53] | 13.86 | 14.17 | 11.77 | 14.16 | 12.75 |
| `fp32.x_s_t` | combinations | 17.18 ± 0.21 | 17.02 [16.64, 17.39] | 16.96 | 17.01 | 15.10 | 17.41 | 24.00 |
| `fp32.e_a` | exponent spread | 10.71 ± 0.06 | 10.69 [10.31, 11.06] | 10.62 | 10.69 | 12.09 | 11.02 | 24.00 |
| `fp32.g_bcol500` | gate share (named weak spot) | 14.28 ± 0.04 | 14.04 [13.66, 14.41] | 13.78 | 14.04 | 10.74 | 13.26 | 12.00 |
| `fp32.g_relu_shift15` | gate share, operands moving on closed lanes | 3.06 ± 0.43 | 3.05 [2.70, 3.41] | 2.36 | 3.07 | 2.15 | 3.60 | 2.06 |
| `fp32.c_near_rand` | near-cancelling sums | 19.15 ± 0.62 | 18.26 [17.56, 18.96] | 17.80 | 18.26 | 16.23 | 20.55 | 24.00 |
| `fp32.s_abs` | sign structure: moving sums, adder rarely alternates | 22.35 ± 0.27 | 22.44 [22.00, 22.87] | 22.93 | 22.44 | 23.79 | 22.39 | 24.00 |
| `fp32.s_bhalf_alt` | sign structure: moving sums, the adder alternates each cycle | 23.91 ± 0.29 | 23.46 [23.05, 23.87] | 23.79 | 23.46 | 22.82 | 23.66 | 24.00 |
| `fp32.t_4_23` | truncated mantissas | 20.17 ± 0.56 | 19.73 [19.33, 20.13] | 19.53 | 19.73 | 18.16 | 20.64 | 24.00 |
| `int8.i_arow500` | gate share and zero bytes | 4.18 ± 0.57 | 4.30 [3.74, 4.87] | 4.07 | 4.29 | 3.44 |  | 3.42 |
| `int8.i_bpair875` | gate share and zero bytes | 2.02 ± 0.51 | 1.81 [1.26, 2.36] | 1.96 | 1.81 | 0.86 |  | 0.85 |
| `int8.i_a127_bfull` | one side busy, the other still | 2.43 ± 0.71 | 3.16 [2.25, 4.07] | 2.21 | 3.14 | 1.76 |  | 6.84 |
| `int8.i_afull_b127` | one side busy, the other still | 6.16 ± 0.28 | 6.36 [5.80, 6.93] | 6.34 | 6.36 | 7.86 |  | 6.84 |
| `int8.i_w2_2` | operand widths | 5.30 ± 0.40 | 5.46 [4.83, 6.08] | 5.77 | 5.46 | 5.74 |  | 6.81 |
| `int8.i_w8_1` | operand widths | 5.44 ± 0.70 | 5.83 [5.26, 6.41] | 5.93 | 5.84 | 6.02 |  | 6.84 |
| `int8.i_sort_a` | order | 6.23 ± 0.72 | 5.87 [5.28, 6.46] | 5.55 | 5.87 | 6.29 |  | 6.84 |

## Every model

- floats (n = 23): M rms 0.314 W, bias -0.053; M2 rms 0.579 W, bias -0.112; Mall rms 0.314 W, bias -0.050; q130n rms 3.960 W, bias +0.884; gate_law rms 7.427 W, bias +4.981; flop rms 1.775 W, bias +0.441
- fp32 (n = 13): M rms 0.392 W, bias -0.137; M2 rms 0.702 W, bias -0.135; Mall rms 0.393 W, bias -0.133; q130n rms 4.674 W, bias +1.014; gate_law rms 8.550 W, bias +5.898; flop rms 2.190 W, bias +0.885
- fp16 (n = 10): M rms 0.162 W, bias +0.056; M2 rms 0.360 W, bias -0.082; Mall rms 0.161 W, bias +0.057; q130n rms 2.768 W, bias +0.715; gate_law rms 5.642 W, bias +3.787; flop rms 1.006 W, bias -0.137
- int8 (n = 7): M rms 0.365 W, bias +0.147; M2 rms 0.381 W, bias +0.009; Mall rms 0.362 W, bias +0.144; q130n rms 0.907 W, bias +0.030; gate_law rms 1.942 W, bias +0.954

| group | n | M rms (W) | M bias (W) | Q130(n) rms (W) |
|---|---:|---:|---:|---:|
| near-cancelling sums | 2 | 0.646 | -0.544 | 3.501 |
| exponent spread | 2 | 0.250 | +0.167 | 2.384 |
| fp16's two elements | 1 | 0.084 | +0.084 | 1.553 |
| gate share (named weak spot) | 2 | 0.237 | -0.010 | 2.890 |
| gate share, operands moving on closed lanes | 2 | 0.079 | -0.059 | 1.243 |
| A side (named weak spot) | 3 | 0.311 | +0.258 | 3.982 |
| order | 2 | 0.259 | -0.145 | 2.378 |
| sign structure: moving sums, adder rarely alternates | 2 | 0.099 | +0.099 | 1.960 |
| truncated mantissas | 2 | 0.310 | -0.212 | 2.222 |
| combinations | 3 | 0.371 | -0.284 | 2.416 |
| A's order (named weak spot, E60's pair) | 1 | 0.211 | +0.211 | 4.218 |
| sign structure: moving sums, the adder alternates each cycle | 1 | 0.450 | -0.450 | 1.087 |
| -0.0 and denormal words | 1 | 0.062 | +0.062 | 13.769 |
| one side busy, the other still | 2 | 0.533 | +0.464 | 1.293 |
| gate share and zero bytes | 2 | 0.171 | -0.042 | 0.970 |
| operand widths | 2 | 0.298 | +0.273 | 0.511 |
