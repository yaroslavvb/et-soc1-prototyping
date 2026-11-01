# E106 results

Passes kept: [10610, 10611, 10612]; set aside: []; leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}

| rule | verdict | dips_kept | gates_off | auto | leak0.1994 | leak0.3803 | leak0.545 | leak0 | numbers |
|---|---|---|---|---|---|---|---|---|---|
| E106-R1 | **PASS** |  |  |  |  |  |  |  | {'reads': 40, 'n_off': 0, 'n_unread': 0} |
| E106-R2 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {} |
| E106-R3 | **ABOUT HALF** | INCONCLUSIVE | ABOUT HALF | ABOUT HALF | ABOUT HALF | ABOUT HALF | ABOUT HALF | INCONCLUSIVE | {'share': 0.557, 'ci95': 0.074, 'n': 3, 'M': 0.546, 'held_w': 2.668, 'held_ci95_w': 0.21, 'band': [0.35, 0.65]} |
| E106-R4 | **ABOUT HALF** | ABOUT HALF | ABOUT HALF | ABOUT HALF | ABOUT HALF | ABOUT HALF | ABOUT HALF | INCONCLUSIVE | {'share': 0.445, 'ci95': 0.113, 'n': 3, 'M': 0.458, 'held_w': 2.091, 'held_ci95_w': 0.442, 'band': [0.3, 0.7]} |
| E106-R5 | **LITTLE** | INCONCLUSIVE | LITTLE | LITTLE | LITTLE | LITTLE | LITTLE | LITTLE | {'share': 0.187, 'ci95': 0.04, 'n': 3, 'M': 0.224, 'held_w': 0.887, 'held_ci95_w': 0.369, 'band': [0.3, 0.7]} |
| E106-R6 | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | ALIKE | {'difference': -0.112, 'ci95': 0.073, 'n': 3, 'band': 0.15} |
| E106-R7 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {'rms_w': 0.076, 'n': 10, 'bias_w': 0.008, 'worst': (0.10995064100234675, 'fp32.c_abs'), 'inside_95': 10} |
| E106-S1 | **PASS** | PASS | PASS | PASS | PASS | FAIL | FAIL | FAIL | {} |

## The read-back

| tile | n | minions agreeing | off rtl | off manual | off frozen | equals | card C00 / C08 | words on the card |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `fp16.c_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4f800000 / 4f800000 | 1 |
| `fp16.c_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 53fa0000 / 53fa0000 | 1 |
| `fp16.c_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 57c33080 / 57c33080 | 1 |
| `fp16.c_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 588452f0 / 588452f0 | 1 |
| `fp16.ones` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42800000 / 42800000 | 1 |
| `fp16.ones` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 46fa0000 / 46fa0000 | 1 |
| `fp16.ones` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4ac33080 / 4ac33080 | 1 |
| `fp16.ones` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b8452f0 / 4b8452f0 | 1 |
| `fp16.signs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 41400000 / c0800000 | 15 |
| `fp16.signs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 45bb8000 / c4fa0000 | 15 |
| `fp16.signs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 49926460 / c8c33080 | 15 |
| `fp16.signs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a467c68 / c98452f0 | 15 |
| `fp16.x_c` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42000000 / 42000000 | 1 |
| `fp16.x_c` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 467a0000 / 467a0000 | 1 |
| `fp16.x_c` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a433080 / 4a433080 | 1 |
| `fp16.x_c` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b0452f0 / 4b0452f0 | 1 |
| `fp16.x_s` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42000000 / 42000000 | 1 |
| `fp16.x_s` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 467a0000 / 467a0000 | 1 |
| `fp16.x_s` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a433080 / 4a433080 | 1 |
| `fp16.x_s` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b0452f0 / 4b0452f0 | 1 |
| `fp16.z_ss` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4f800000 / 4f800000 | 1 |
| `fp16.z_ss` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 53fa0000 / 53fa0000 | 1 |
| `fp16.z_ss` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 57c33080 / 57c33080 | 1 |
| `fp16.z_ss` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 588452f0 / 588452f0 | 1 |
| `fp32.c_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.c_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.c_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.c_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.ones` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42000000 / 42000000 | 1 |
| `fp32.ones` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 467a0000 / 467a0000 | 1 |
| `fp32.ones` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a433080 / 4a433080 | 1 |
| `fp32.ones` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b0452f0 / 4b0452f0 | 1 |
| `fp32.s_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.s_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.s_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.s_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.signs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c0800000 / 00000000 | 11 |
| `fp32.signs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c4fa0000 / 00000000 | 11 |
| `fp32.signs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c8c33080 / 00000000 | 11 |
| `fp32.signs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c98452f0 / 00000000 | 11 |

## The contrasts, per pass, t intervals

| contrast | measured, W | n | M4 [95%] |
|---|---:|---:|---:|
| `fp32.step` | 4.792 ± 0.421 | 3 | 4.80 ± 0.55 |
| `fp16.step` | 4.716 ± 1.118 | 3 | 4.85 ± 0.55 |
| `fp32.held` | 2.668 ± 0.210 | 3 | 2.62 ± 0.55 |
| `fp16.held_z` | 2.091 ± 0.442 | 3 | 2.22 ± 0.50 |
| `fp16.held_x` | 0.887 ± 0.369 | 3 | 1.09 ± 0.49 |
| `fp32.rest` | 2.124 ± 0.509 | 3 | 2.18 ± 0.78 |
| `fp16.rest_z` | 2.625 ± 1.058 | 3 | 2.63 ± 0.74 |

## The shares of the step, per pass

| held tile | share | n | M4 |
|---|---:|---:|---:|
| `fp32.s_abs` | 0.557 ± 0.074 | 3 | 0.546 |
| `fp16.z_ss` | 0.445 ± 0.113 | 3 | 0.458 |
| `fp16.x_s` | 0.187 ± 0.040 | 3 | 0.224 |

## The tiles

| tile | group | D, W (95%) | M4 [95%] | D - M4 |
|---|---|---:|---:|---:|
| `fp16.c_abs` | held baseline | 8.15 ± 0.05 | 8.04 [7.67, 8.42] | +0.10 |
| `fp16.ones` | the +1 side of the step | 8.15 ± 0.32 | 8.07 [7.70, 8.44] | +0.08 |
| `fp16.signs` | the +-1 side of the step | 12.87 ± 0.80 | 12.92 [12.50, 13.34] | -0.06 |
| `fp16.x_c` | held baseline | 8.18 ± 0.30 | 8.07 [7.70, 8.44] | +0.11 |
| `fp16.x_s` | held, both operands' signs moving | 9.06 ± 0.54 | 9.16 [8.78, 9.53] | -0.09 |
| `fp16.z_ss` | held, both operands' signs moving | 10.24 ± 0.49 | 10.27 [9.89, 10.64] | -0.03 |
| `fp32.c_abs` | held baseline | 7.95 ± 0.15 | 8.06 [7.68, 8.43] | -0.11 |
| `fp32.ones` | the +1 side of the step | 8.07 ± 0.45 | 8.08 [7.70, 8.45] | -0.01 |
| `fp32.s_abs` | held, both operands' signs moving | 10.61 ± 0.32 | 10.68 [10.23, 11.12] | -0.06 |
| `fp32.signs` | the +-1 side of the step | 12.86 ± 0.17 | 12.88 [12.46, 13.29] | -0.01 |
