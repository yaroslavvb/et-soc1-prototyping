# E108 results

Passes kept: [10810, 10811, 10812, 10813]; set aside: []; leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}

| rule | verdict | dips_kept | gates_off | auto | leak0.1994 | leak0.3803 | leak0.545 | leak0 | numbers |
|---|---|---|---|---|---|---|---|---|---|
| E108-R1 | **PASS** |  |  |  |  |  |  |  | {'reads': 96, 'n_off': 0, 'n_unread': 0} |
| E108-R3 | **ALIKE** | INCONCLUSIVE | ALIKE | ALIKE | ALIKE | ALIKE | ALIKE | INCONCLUSIVE | {'formats_z': '0.012 ± 0.022 (M4 0.036)'} |
| E108-R4 | **ABSORBED HIGHER** | INCONCLUSIVE | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | {'design_fp32': '0.103 ± 0.037 (M4 0.129)'} |
| E108-R5 | **PRICED ALIKE** | INCONCLUSIVE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | INCONCLUSIVE | {'A_vs_B_priced': '-0.031 ± 0.339 (M4 -0.001)'} |
| E108-R6 | **INCONCLUSIVE / NOTHING MEASURABLE** | INCONCLUSIVE / INCONCLUSIVE | INCONCLUSIVE / NOTHING MEASURABLE | INCONCLUSIVE / NOTHING MEASURABLE | INCONCLUSIVE / NOTHING MEASURABLE | INCONCLUSIVE / NOTHING MEASURABLE | INCONCLUSIVE / SUBTRACTS | INCONCLUSIVE / NOTHING MEASURABLE | {'fp32.A_on_B_held': '-0.255 ± 0.51 (M4 -0.202)', 'fp32.A_on_B_walk': '-0.269 ± 0.187 (M4 -0.376)'} |
| E108-R7 | **MOST** | INCONCLUSIVE | MOST | MOST | MOST | MOST | MOST | MOST | {'fp32.share_het': '1.133 ± 0.09 (M4 1.162)'} |
| E108-R12 | **MOST** | MOST | MOST | MOST | MOST | MOST | MOST | MOST | {'fp32.share_het_z': '0.970 ± 0.013 (M4 0.964)'} |
| E108-R8 | **RISES / RISES** | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | {'fp32.ex_over_sg': '0.633 ± 0.243 (M4 0.61)', 'fp32.mx_over_ex': '1.739 ± 0.223 (M4 1.652)'} |
| E108-R9 | **FALLS** | INCONCLUSIVE | FALLS | FALLS | FALLS | FALLS | FALLS | INCONCLUSIVE | {'fp32.alt_ratio': '0.485 ± 0.185 (M4 0.43)'} |
| E108-R10 | **INCONCLUSIVE** | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | 1.55x HOLDS | 1.55x HOLDS | INCONCLUSIVE | {'alt_walk_ratio': '1.614 ± 0.48 (M4 1.543)'} |
| E108-R2 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {} |
| E108-R11 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {'rms_w': 0.153, 'n': 25, 'bias_w': 0.083, 'worst': (0.4682448643760111, 'fp16.w_h_add'), 'inside_95': 25} |
| E108-S1 | **PASS** | PASS | PASS | PASS | PASS | FAIL | FAIL | FAIL | {} |

## The read-back

| tile | n | minions agreeing | off rtl | off manual | off frozen | equals | card C00 / C08 | words on the card |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `fp16.c_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4f800000 / 4f800000 | 1 |
| `fp16.c_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 53fa0000 / 53fa0000 | 1 |
| `fp16.c_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 57c33080 / 57c33080 | 1 |
| `fp16.c_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 588452f0 / 588452f0 | 1 |
| `fp16.m_h_sub` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 47723000 / 46fa0000 | 2 |
| `fp16.m_h_sub` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b3d16fc / 4ac33080 | 2 |
| `fp16.m_h_sub` | 500000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4bec82e0 / 4b742400 | 2 |
| `fp16.ones` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42800000 / 42800000 | 1 |
| `fp16.ones` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 46fa0000 / 46fa0000 | 1 |
| `fp16.ones` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4ac33080 / 4ac33080 | 1 |
| `fp16.ones` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b8452f0 / 4b8452f0 | 1 |
| `fp16.signs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 41400000 / c0800000 | 15 |
| `fp16.signs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 45bb8000 / c4fa0000 | 15 |
| `fp16.signs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 49926460 / c8c33080 | 15 |
| `fp16.signs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a467c68 / c98452f0 | 15 |
| `fp16.w_h_add` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 47723000 / c6fa0000 | 2 |
| `fp16.w_h_add` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b3d16fc / cac33080 | 2 |
| `fp16.w_h_add` | 500000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4bec82e0 / cb742400 | 2 |
| `fp16.z_s` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4f800000 / 4f800000 | 1 |
| `fp16.z_s` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 53fa0000 / 53fa0000 | 1 |
| `fp16.z_s` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 57c33080 / 57c33080 | 1 |
| `fp16.z_s` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 588452f0 / 588452f0 | 1 |
| `fp16.z_ss` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4f800000 / 4f800000 | 1 |
| `fp16.z_ss` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 53fa0000 / 53fa0000 | 1 |
| `fp16.z_ss` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 57c33080 / 57c33080 | 1 |
| `fp16.z_ss` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 588452f0 / 588452f0 | 1 |
| `fp32.b_A_f` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.b_A_f` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.b_A_f` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.b_A_f` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.b_A_w` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 40800000 / 40800000 | 6 |
| `fp32.b_A_w` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 44fa0000 / 44fa0000 | 6 |
| `fp32.b_A_w` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 48c33080 / 48c33080 | 6 |
| `fp32.b_A_w` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 498452f0 / 498452f0 | 6 |
| `fp32.b_B_f` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.b_B_f` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.b_B_f` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.b_B_f` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.b_B_w` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c1400000 / 40800000 | 8 |
| `fp32.b_B_w` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c5bb8000 / 44fa0000 | 8 |
| `fp32.b_B_w` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c9926460 / 48c33080 | 8 |
| `fp32.b_B_w` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | ca467c68 / 498452f0 | 8 |
| `fp32.b_B_z` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c1400000 / 40800000 | 8 |
| `fp32.b_B_z` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c5bb8000 / 44fa0000 | 8 |
| `fp32.b_B_z` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c9926460 / 48c33080 | 8 |
| `fp32.b_B_z` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | ca467c68 / 498452f0 | 8 |
| `fp32.c_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.c_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.c_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.c_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.c_ex_f` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 73000000 / 72800000 | 10 |
| `fp32.c_ex_f` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 777a0000 / 76fa0000 | 10 |
| `fp32.c_ex_f` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b433080 / 7ac33080 | 10 |
| `fp32.c_ex_f` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7c0452f0 / 7b8452f0 | 10 |
| `fp32.c_mx_f` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 73400000 / 72c00000 | 26 |
| `fp32.c_mx_f` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 77bb8000 / 773b8000 | 26 |
| `fp32.c_mx_f` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b926460 / 7b126460 | 26 |
| `fp32.c_mx_f` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7c467c68 / 7bc67c68 | 26 |
| `fp32.c_sg_f` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 2 |
| `fp32.c_sg_f` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 2 |
| `fp32.c_sg_f` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 2 |
| `fp32.c_sg_f` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 2 |
| `fp32.h_add` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / f2000000 | 2 |
| `fp32.h_add` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / f67a0000 | 2 |
| `fp32.h_add` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / fa433080 | 2 |
| `fp32.h_add` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / fb0452f0 | 2 |
| `fp32.h_sub` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.h_sub` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.h_sub` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.h_sub` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.m_h_sub` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 46f23000 / 467a0000 | 2 |
| `fp32.m_h_sub` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4abd16fc / 4a433080 | 2 |
| `fp32.m_h_sub` | 500000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b6c82e0 / 4af42400 | 2 |
| `fp32.ones` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42000000 / 42000000 | 1 |
| `fp32.ones` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 467a0000 / 467a0000 | 1 |
| `fp32.ones` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a433080 / 4a433080 | 1 |
| `fp32.ones` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b0452f0 / 4b0452f0 | 1 |
| `fp32.s_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.s_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.s_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.s_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.s_walk` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 41800000 / c1000000 | 11 |
| `fp32.s_walk` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 45fa0000 / c57a0000 | 11 |
| `fp32.s_walk` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 49c33080 / c9433080 | 11 |
| `fp32.s_walk` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a8452f0 / ca0452f0 | 11 |
| `fp32.signs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c0800000 / 00000000 | 11 |
| `fp32.signs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c4fa0000 / 00000000 | 11 |
| `fp32.signs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c8c33080 / 00000000 | 11 |
| `fp32.signs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c98452f0 / 00000000 | 11 |
| `fp32.w_h_add` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 46f23000 / c67a0000 | 2 |
| `fp32.w_h_add` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4abd16fc / ca433080 | 2 |
| `fp32.w_h_add` | 500000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b6c82e0 / caf42400 | 2 |
| `fp32.z_s` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.z_s` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.z_s` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.z_s` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |

## Every registered quantity, per pass, t intervals

| quantity | form | measured | n | M4 | what |
|---|---|---:|---:|---:|---|
| `fp32.step` | contrast | 4.798 ± 0.318 | 4 | 4.799 ± 0.55 | the sign step, fp32 |
| `fp16.step` | contrast | 4.981 ± 0.110 | 4 | 4.854 ± 0.55 | the sign step, fp16 |
| `fp32.held_z` | contrast | 1.985 ± 0.145 | 4 | 2.001 ± 0.58 | random B signs on zero products, the sum held (E104's z_s), fp32 |
| `fp16.held_z` | contrast | 2.124 ± 0.164 | 4 | 2.201 ± 0.50 | random B signs on zero products, the sum held (E104's z_s), fp16 |
| `fp32.held_abs` | contrast | 2.480 ± 0.320 | 4 | 2.619 ± 0.55 | random signs on both sides, absorbed, the sum held (E88's s_abs), fp32 |
| `fp16.held_zss` | contrast | 2.162 ± 0.234 | 4 | 2.224 ± 0.50 | random signs on both sides, zero products, the sum held (E106's z_ss), fp16 |
| `fp32.rest_vs_z` | contrast | 2.813 ± 0.316 | 4 | 2.798 ± 0.80 | the step less the zero-product held part, fp32 |
| `fp16.rest_vs_z` | contrast | 2.857 ± 0.233 | 4 | 2.653 ± 0.74 | the step less the zero-product held part, fp16 |
| `fp32.rest_vs_abs` | contrast | 2.319 ± 0.397 | 4 | 2.180 ± 0.78 | the step less the absorbed held part (E106's rest), fp32 |
| `fp32.A_held` | contrast | 1.111 ± 0.438 | 4 | 1.177 ± 0.50 | A's random signs, B +1, absorbed |
| `fp32.B_held` | contrast | 2.734 ± 0.296 | 4 | 2.821 ± 0.56 | B's random signs, A +1, absorbed |
| `fp32.A_step` | contrast | 1.980 ± 0.149 | 4 | 2.067 ± 0.51 | A's random signs, B +1, walking, over all +1 |
| `fp32.B_step` | contrast | 4.996 ± 0.270 | 4 | 5.064 ± 0.53 | B's random signs, A +1, walking, over all +1 |
| `fp32.AB_step` | contrast | 4.727 ± 0.351 | 4 | 4.688 ± 0.54 | both sides' random signs (s_walk), walking, over all +1 |
| `fp32.A_rest` | contrast | 0.857 ± 0.119 | 4 | 0.912 ± 0.52 | A's signs: walking less held |
| `fp32.B_rest` | contrast | 2.249 ± 0.277 | 4 | 2.264 ± 0.60 | B's signs: walking less held |
| `fp32.rest` | contrast | 2.235 ± 0.169 | 4 | 2.091 ± 0.59 | both: walking less held, the draws matched (E88's R32s) |
| `fp32.A_on_B_held` | contrast | -0.255 ± 0.510 | 4 | -0.202 ± 0.60 | A's signs added to B's, held |
| `fp32.A_on_B_walk` | contrast | -0.269 ± 0.187 | 4 | -0.376 ± 0.55 | A's signs added to B's, walking |
| `fp32.abs_vs_zero` | contrast | 0.749 ± 0.367 | 4 | 0.820 ± 0.63 | the same B stream and k = 0 slice: absorbed +-1 products against zero products |
| `fp32.Bz_het` | contrast | 2.907 ± 0.120 | 4 | 2.973 ± 0.65 | zero products, B's signs: held at b_B_w's sums over held at z_s's equal ones |
| `fp32.Bz_walk` | contrast | 0.091 ± 0.040 | 4 | 0.111 ± 0.58 | B's signs walking over held at the same sums at every op's end |
| `fp32.Bz_rest` | contrast | 2.998 ± 0.124 | 4 | 3.084 ± 0.62 | B's signs walking over held on zero products: the rest for B's signs, zero-product baseline |
| `fp32.het_sg` | contrast | 0.160 ± 0.337 | 4 | 0.168 ± 0.58 | held accumulators that differ in sign, over s_abs's equal ones |
| `fp32.het_ex` | contrast | 0.793 ± 0.478 | 4 | 0.778 ± 0.57 | held accumulators that differ in sign and exponent |
| `fp32.het_mx` | contrast | 2.532 ± 0.292 | 4 | 2.430 ± 0.58 | held accumulators that differ as s_walk's do |
| `fp32.ex_over_sg` | contrast | 0.633 ± 0.243 | 4 | 0.610 ± 0.55 | the exponents misaligned, over sign only |
| `fp32.mx_over_ex` | contrast | 1.739 ± 0.223 | 4 | 1.652 ± 0.54 | the mantissas too, over sign and exponent |
| `fp32.walk_given_het` | contrast | -0.298 ± 0.201 | 4 | -0.339 ± 0.55 | the sums walking, over held accumulators that differ as s_walk's do |
| `fp32.alt_held` | contrast | 4.161 ± 0.440 | 4 | 3.987 ± 0.68 | alternating against a fixed product sign, held (E92's pair) |
| `fp32.alt_walk` | contrast | 2.002 ± 0.623 | 4 | 1.715 ± 1.25 | alternating against a fixed product sign, walking, the same magnitudes (E104's pair) |
| `fp16.alt_walk` | contrast | 3.144 ± 0.168 | 4 | 2.646 ± 0.88 | alternating against a fixed product sign, walking (E104's pair) |
| `fp32.walk_fixed` | contrast | 3.980 ± 0.295 | 4 | 4.030 ± 0.88 | the sums walking at a fixed product sign, over held |
| `fp32.share_z` | ratio | 0.414 ± 0.036 | 4 | 0.417 | fp32's held share, zero products, one session |
| `fp16.share_z` | ratio | 0.427 ± 0.038 | 4 | 0.453 | fp16's held share, zero products, one session |
| `fp32.share_abs` | ratio | 0.517 ± 0.068 | 4 | 0.546 | fp32's held share, absorbed products (E106's design) |
| `fp16.share_zss` | ratio | 0.434 ± 0.054 | 4 | 0.458 | fp16's held share, zero products with A's signs (E106's design) |
| `fp32.share_het` | ratio | 1.133 ± 0.090 | 4 | 1.162 | how much of the rest held accumulators that differ as s_walk's do carry |
| `fp32.share_het_z` | ratio | 0.970 ± 0.013 | 4 | 0.964 | zero products: how much of B's rest held accumulators at b_B_w's own sums carry |
| `fp32.alt_ratio` | ratio | 0.485 ± 0.185 | 4 | 0.430 | the alternation's price walking over held, fp32 |
| `alt_walk_ratio` | ratio | 1.614 ± 0.480 | 4 | 1.543 | E104-R6: fp16 over fp32, walking |
| `fp32.A_over_B_held` | ratio | 0.404 ± 0.119 | 4 | 0.417 | A's held cost over B's |
| `formats_z` | diff | 0.012 ± 0.022 | 4 | 0.036 | the like for like: fp16's zero-product share less fp32's |
| `design_fp32` | diff | 0.103 ± 0.037 | 4 | 0.129 | fp32's held share, absorbed less zero products, one session |
| `design_fp16` | diff | 0.008 ± 0.061 | 4 | 0.005 | fp16's held share, A's sign bits moving on the zeros less still |
| `A_vs_B_priced` | diff | -0.031 ± 0.339 | 4 | -0.001 | A's held cost less B's scaled by their alternations (0.4177) |

## The tiles

| tile | group | D, W (95%) | M4 [95%] | D - M4 |
|---|---|---:|---:|---:|
| `fp16.c_abs` | held baseline | 8.07 ± 0.11 | 8.04 [7.67, 8.42] | +0.02 |
| `fp16.m_h_sub` | product sign alternating, walking | 15.75 ± 0.25 | 15.72 [15.16, 16.28] | +0.03 |
| `fp16.ones` | the +1 side of the step | 8.05 ± 0.05 | 8.07 [7.70, 8.44] | -0.02 |
| `fp16.signs` | the +-1 side of the step | 13.03 ± 0.14 | 12.92 [12.50, 13.34] | +0.11 |
| `fp16.w_h_add` | fixed product sign, walking | 12.61 ± 0.13 | 13.07 [12.38, 13.77] | -0.47 |
| `fp16.z_s` | held, zero products, B's signs | 10.19 ± 0.06 | 10.24 [9.87, 10.62] | -0.05 |
| `fp16.z_ss` | held, zero products, both signs | 10.23 ± 0.29 | 10.27 [9.89, 10.64] | -0.04 |
| `fp32.b_A_f` | A's signs, held | 9.19 ± 0.31 | 9.23 [8.85, 9.62] | -0.05 |
| `fp32.b_A_w` | A's signs, walking | 10.04 ± 0.33 | 10.14 [9.76, 10.53] | -0.10 |
| `fp32.b_B_f` | B's signs, held | 10.81 ± 0.26 | 10.88 [10.42, 11.33] | -0.07 |
| `fp32.b_B_w` | B's signs, walking | 13.06 ± 0.03 | 13.14 [12.74, 13.54] | -0.08 |
| `fp32.b_B_z` | B's signs, zero products, held at b_B_w's sums | 12.97 ± 0.07 | 13.03 [12.58, 13.48] | -0.06 |
| `fp32.c_abs` | held baseline | 8.08 ± 0.16 | 8.06 [7.68, 8.43] | +0.02 |
| `fp32.c_ex_f` | held, C differs in sign and exponent | 11.35 ± 0.23 | 11.45 [11.06, 11.85] | -0.11 |
| `fp32.c_mx_f` | held, C differs as s_walk's does | 13.09 ± 0.08 | 13.11 [12.71, 13.50] | -0.02 |
| `fp32.c_sg_f` | held, C differs in sign | 10.71 ± 0.22 | 10.84 [10.43, 11.26] | -0.13 |
| `fp32.h_add` | fixed product sign, held | 8.53 ± 0.13 | 8.86 [8.48, 9.23] | -0.33 |
| `fp32.h_sub` | product sign alternating, held | 12.69 ± 0.45 | 12.85 [12.27, 13.43] | -0.15 |
| `fp32.m_h_sub` | product sign alternating, walking | 14.52 ± 0.44 | 14.60 [13.64, 15.57] | -0.09 |
| `fp32.ones` | the +1 side of the step | 8.06 ± 0.24 | 8.08 [7.70, 8.45] | -0.02 |
| `fp32.s_abs` | held, absorbed, both signs | 10.55 ± 0.27 | 10.68 [10.23, 11.12] | -0.12 |
| `fp32.s_walk` | s_abs walking | 12.79 ± 0.21 | 12.77 [12.36, 13.17] | +0.02 |
| `fp32.signs` | the +-1 side of the step | 12.86 ± 0.08 | 12.88 [12.46, 13.29] | -0.02 |
| `fp32.w_h_add` | fixed product sign, walking | 12.51 ± 0.29 | 12.89 [12.08, 13.70] | -0.38 |
| `fp32.z_s` | held, zero products, B's signs | 10.06 ± 0.15 | 10.06 [9.57, 10.54] | +0.00 |
