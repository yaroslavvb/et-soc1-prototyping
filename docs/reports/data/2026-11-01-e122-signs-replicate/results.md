# E122 results: E108's rules on aifoundry3 card 0 (score_e108.write_md unchanged; references substituted for this card)

Passes kept: [12210, 12211, 12212, 12213]; set aside: []; leak {'mode': '0.1994', 'k_w_per_c': 0.1994, 'n_runs': -1}

| rule | verdict | dips_kept | gates_off | auto | leak0.2414 | leak0.3803 | leak0.545 | leak0 | numbers |
|---|---|---|---|---|---|---|---|---|---|
| E108-R1 | **PASS** |  |  |  |  |  |  |  | {'reads': 96, 'n_off': 0, 'n_unread': 0} |
| E108-R3 | **ALIKE** | ALIKE | ALIKE | ALIKE | ALIKE | ALIKE | ALIKE | INCONCLUSIVE | {'formats_z': '0.035 ± 0.051 (M4 0.036)'} |
| E108-R4 | **ABSORBED HIGHER** | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | ABSORBED HIGHER | {'design_fp32': '0.152 ± 0.058 (M4 0.129)'} |
| E108-R5 | **PRICED ALIKE** | INCONCLUSIVE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | PRICED ALIKE | {'A_vs_B_priced': '0.018 ± 0.178 (M4 -0.001)'} |
| E108-R6 | **NOTHING MEASURABLE / NOTHING MEASURABLE** | NOTHING MEASURABLE / SUBTRACTS | NOTHING MEASURABLE / NOTHING MEASURABLE | NOTHING MEASURABLE / NOTHING MEASURABLE | NOTHING MEASURABLE / NOTHING MEASURABLE | INCONCLUSIVE / NOTHING MEASURABLE | INCONCLUSIVE / NOTHING MEASURABLE | NOTHING MEASURABLE / NOTHING MEASURABLE | {'fp32.A_on_B_held': '-0.217 ± 0.262 (M4 -0.208)', 'fp32.A_on_B_walk': '-0.328 ± 0.038 (M4 -0.386)'} |
| E108-R7 | **MOST** | MOST | MOST | MOST | MOST | MOST | MOST | MOST | {'fp32.share_het': '1.177 ± 0.054 (M4 1.162)'} |
| E108-R12 | **MOST** | MOST | MOST | MOST | MOST | MOST | MOST | MOST | {'fp32.share_het_z': '0.954 ± 0.036 (M4 0.964)'} |
| E108-R8 | **RISES / RISES** | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | RISES / RISES | {'fp32.ex_over_sg': '0.611 ± 0.367 (M4 0.628)', 'fp32.mx_over_ex': '1.938 ± 0.309 (M4 1.699)'} |
| E108-R9 | **FALLS** | FALLS | FALLS | FALLS | FALLS | FALLS | FALLS | FALLS | {'fp32.alt_ratio': '0.501 ± 0.032 (M4 0.43)'} |
| E108-R10 | **1.55x HOLDS** | INCONCLUSIVE | 1.55x HOLDS | 1.55x HOLDS | 1.55x HOLDS | INCONCLUSIVE | INCONCLUSIVE | 1.55x HOLDS | {'alt_walk_ratio': '1.490 ± 0.149 (M4 1.543)'} |
| E108-R2 | **PASS** | PASS | PASS | PASS | PASS | PASS | PASS | PASS | {} |
| E108-R11 | **PASS** | PASS | PASS | PASS | PASS | PASS | INCONCLUSIVE | PASS | {'rms_w': 0.14, 'n': 25, 'bias_w': 0.031, 'worst': (0.37560375468950546, 'fp16.w_h_add'), 'inside_95': 25} |
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
| `fp32.step` | contrast | 4.921 ± 0.136 | 4 | 4.936 ± 0.56 | the sign step, fp32 |
| `fp16.step` | contrast | 4.901 ± 0.153 | 4 | 4.993 ± 0.56 | the sign step, fp16 |
| `fp32.held_z` | contrast | 1.923 ± 0.242 | 4 | 2.058 ± 0.60 | random B signs on zero products, the sum held (E104's z_s), fp32 |
| `fp16.held_z` | contrast | 2.084 ± 0.011 | 4 | 2.264 ± 0.51 | random B signs on zero products, the sum held (E104's z_s), fp16 |
| `fp32.held_abs` | contrast | 2.675 ± 0.434 | 4 | 2.694 ± 0.56 | random signs on both sides, absorbed, the sum held (E88's s_abs), fp32 |
| `fp16.held_zss` | contrast | 2.113 ± 0.064 | 4 | 2.287 ± 0.51 | random signs on both sides, zero products, the sum held (E106's z_ss), fp16 |
| `fp32.rest_vs_z` | contrast | 2.998 ± 0.200 | 4 | 2.878 ± 0.82 | the step less the zero-product held part, fp32 |
| `fp16.rest_vs_z` | contrast | 2.816 ± 0.151 | 4 | 2.729 ± 0.76 | the step less the zero-product held part, fp16 |
| `fp32.rest_vs_abs` | contrast | 2.246 ± 0.332 | 4 | 2.243 ± 0.80 | the step less the absorbed held part (E106's rest), fp32 |
| `fp32.A_held` | contrast | 1.226 ± 0.263 | 4 | 1.211 ± 0.52 | A's random signs, B +1, absorbed |
| `fp32.B_held` | contrast | 2.892 ± 0.271 | 4 | 2.901 ± 0.57 | B's random signs, A +1, absorbed |
| `fp32.A_step` | contrast | 2.011 ± 0.068 | 4 | 2.126 ± 0.53 | A's random signs, B +1, walking, over all +1 |
| `fp32.B_step` | contrast | 5.052 ± 0.073 | 4 | 5.208 ± 0.55 | B's random signs, A +1, walking, over all +1 |
| `fp32.AB_step` | contrast | 4.723 ± 0.090 | 4 | 4.822 ± 0.55 | both sides' random signs (s_walk), walking, over all +1 |
| `fp32.A_rest` | contrast | 0.894 ± 0.096 | 4 | 0.938 ± 0.54 | A's signs: walking less held |
| `fp32.B_rest` | contrast | 2.269 ± 0.054 | 4 | 2.329 ± 0.62 | B's signs: walking less held |
| `fp32.rest` | contrast | 2.157 ± 0.230 | 4 | 2.150 ± 0.61 | both: walking less held, the draws matched (E88's R32s) |
| `fp32.A_on_B_held` | contrast | -0.217 ± 0.262 | 4 | -0.208 ± 0.62 | A's signs added to B's, held |
| `fp32.A_on_B_walk` | contrast | -0.328 ± 0.038 | 4 | -0.386 ± 0.56 | A's signs added to B's, walking |
| `fp32.abs_vs_zero` | contrast | 0.969 ± 0.042 | 4 | 0.843 ± 0.65 | the same B stream and k = 0 slice: absorbed +-1 products against zero products |
| `fp32.Bz_het` | contrast | 3.089 ± 0.169 | 4 | 3.058 ± 0.67 | zero products, B's signs: held at b_B_w's sums over held at z_s's equal ones |
| `fp32.Bz_walk` | contrast | 0.149 ± 0.116 | 4 | 0.114 ± 0.60 | B's signs walking over held at the same sums at every op's end |
| `fp32.Bz_rest` | contrast | 3.238 ± 0.082 | 4 | 3.172 ± 0.64 | B's signs walking over held on zero products: the rest for B's signs, zero-product baseline |
| `fp32.het_sg` | contrast | -0.012 ± 0.210 | 4 | 0.173 ± 0.59 | held accumulators that differ in sign, over s_abs's equal ones |
| `fp32.het_ex` | contrast | 0.599 ± 0.441 | 4 | 0.801 ± 0.59 | held accumulators that differ in sign and exponent |
| `fp32.het_mx` | contrast | 2.537 ± 0.153 | 4 | 2.499 ± 0.59 | held accumulators that differ as s_walk's do |
| `fp32.ex_over_sg` | contrast | 0.611 ± 0.367 | 4 | 0.628 ± 0.57 | the exponents misaligned, over sign only |
| `fp32.mx_over_ex` | contrast | 1.938 ± 0.309 | 4 | 1.699 ± 0.56 | the mantissas too, over sign and exponent |
| `fp32.walk_given_het` | contrast | -0.379 ± 0.080 | 4 | -0.349 ± 0.56 | the sums walking, over held accumulators that differ as s_walk's do |
| `fp32.alt_held` | contrast | 4.369 ± 0.220 | 4 | 4.101 ± 0.70 | alternating against a fixed product sign, held (E92's pair) |
| `fp32.alt_walk` | contrast | 2.188 ± 0.157 | 4 | 1.764 ± 1.29 | alternating against a fixed product sign, walking, the same magnitudes (E104's pair) |
| `fp16.alt_walk` | contrast | 3.254 ± 0.240 | 4 | 2.722 ± 0.91 | alternating against a fixed product sign, walking (E104's pair) |
| `fp32.walk_fixed` | contrast | 3.981 ± 0.092 | 4 | 4.145 ± 0.90 | the sums walking at a fixed product sign, over held |
| `fp32.share_z` | ratio | 0.391 ± 0.044 | 4 | 0.417 | fp32's held share, zero products, one session |
| `fp16.share_z` | ratio | 0.425 ± 0.013 | 4 | 0.453 | fp16's held share, zero products, one session |
| `fp32.share_abs` | ratio | 0.543 ± 0.076 | 4 | 0.546 | fp32's held share, absorbed products (E106's design) |
| `fp16.share_zss` | ratio | 0.431 ± 0.019 | 4 | 0.458 | fp16's held share, zero products with A's signs (E106's design) |
| `fp32.share_het` | ratio | 1.177 ± 0.054 | 4 | 1.162 | how much of the rest held accumulators that differ as s_walk's do carry |
| `fp32.share_het_z` | ratio | 0.954 ± 0.036 | 4 | 0.964 | zero products: how much of B's rest held accumulators at b_B_w's own sums carry |
| `fp32.alt_ratio` | ratio | 0.501 ± 0.032 | 4 | 0.430 | the alternation's price walking over held, fp32 |
| `alt_walk_ratio` | ratio | 1.490 ± 0.149 | 4 | 1.543 | E104-R6: fp16 over fp32, walking |
| `fp32.A_over_B_held` | ratio | 0.423 ± 0.060 | 4 | 0.417 | A's held cost over B's |
| `formats_z` | diff | 0.035 ± 0.051 | 4 | 0.036 | the like for like: fp16's zero-product share less fp32's |
| `design_fp32` | diff | 0.152 ± 0.058 | 4 | 0.129 | fp32's held share, absorbed less zero products, one session |
| `design_fp16` | diff | 0.006 ± 0.011 | 4 | 0.005 | fp16's held share, A's sign bits moving on the zeros less still |
| `A_vs_B_priced` | diff | 0.018 ± 0.178 | 4 | -0.001 | A's held cost less B's scaled by their alternations (0.4177) |

## The tiles

| tile | group | D, W (95%) | M4 [95%] | D - M4 |
|---|---|---:|---:|---:|
| `fp16.c_abs` | held baseline | 8.37 ± 0.04 | 8.27 [7.89, 8.66] | +0.10 |
| `fp16.m_h_sub` | product sign alternating, walking | 16.33 ± 0.04 | 16.17 [15.60, 16.74] | +0.16 |
| `fp16.ones` | the +1 side of the step | 8.42 ± 0.07 | 8.30 [7.91, 8.68] | +0.12 |
| `fp16.signs` | the +-1 side of the step | 13.32 ± 0.12 | 13.29 [12.86, 13.73] | +0.02 |
| `fp16.w_h_add` | fixed product sign, walking | 13.07 ± 0.27 | 13.45 [12.73, 14.16] | -0.38 |
| `fp16.z_s` | held, zero products, B's signs | 10.45 ± 0.04 | 10.54 [10.15, 10.92] | -0.08 |
| `fp16.z_ss` | held, zero products, both signs | 10.48 ± 0.05 | 10.56 [10.18, 10.94] | -0.08 |
| `fp32.b_A_f` | A's signs, held | 9.54 ± 0.02 | 9.50 [9.10, 9.89] | +0.04 |
| `fp32.b_A_w` | A's signs, walking | 10.43 ± 0.08 | 10.43 [10.04, 10.83] | -0.00 |
| `fp32.b_B_f` | B's signs, held | 11.20 ± 0.13 | 11.19 [10.72, 11.65] | +0.02 |
| `fp32.b_B_w` | B's signs, walking | 13.47 ± 0.09 | 13.52 [13.11, 13.93] | -0.04 |
| `fp32.b_B_z` | B's signs, zero products, held at b_B_w's sums | 13.32 ± 0.07 | 13.40 [12.94, 13.86] | -0.08 |
| `fp32.c_abs` | held baseline | 8.31 ± 0.25 | 8.29 [7.90, 8.67] | +0.03 |
| `fp32.c_ex_f` | held, C differs in sign and exponent | 11.59 ± 0.28 | 11.78 [11.37, 12.19] | -0.19 |
| `fp32.c_mx_f` | held, C differs as s_walk's does | 13.52 ± 0.09 | 13.48 [13.07, 13.88] | +0.04 |
| `fp32.c_sg_f` | held, C differs in sign | 10.98 ± 0.12 | 11.15 [10.73, 11.58] | -0.18 |
| `fp32.h_add` | fixed product sign, held | 8.92 ± 0.11 | 9.11 [8.73, 9.50] | -0.19 |
| `fp32.h_sub` | product sign alternating, held | 13.29 ± 0.15 | 13.21 [12.62, 13.81] | +0.08 |
| `fp32.m_h_sub` | product sign alternating, walking | 15.09 ± 0.13 | 15.02 [14.02, 16.02] | +0.07 |
| `fp32.ones` | the +1 side of the step | 8.42 ± 0.08 | 8.31 [7.92, 8.69] | +0.11 |
| `fp32.s_abs` | held, absorbed, both signs | 10.99 ± 0.21 | 10.98 [10.53, 11.43] | +0.01 |
| `fp32.s_walk` | s_abs walking | 13.14 ± 0.09 | 13.13 [12.72, 13.54] | +0.01 |
| `fp32.signs` | the +-1 side of the step | 13.34 ± 0.09 | 13.24 [12.82, 13.67] | +0.10 |
| `fp32.w_h_add` | fixed product sign, walking | 12.90 ± 0.17 | 13.26 [12.43, 14.09] | -0.35 |
| `fp32.z_s` | held, zero products, B's signs | 10.23 ± 0.15 | 10.34 [9.85, 10.84] | -0.11 |

**The same verdict as E108 on card 1:** 11 of 13; differing: {'E108-R10': {'e122': '1.55x HOLDS', 'e108': 'INCONCLUSIVE'}, 'E108-R6': {'e122': 'NOTHING MEASURABLE / NOTHING MEASURABLE', 'e108': 'INCONCLUSIVE / NOTHING MEASURABLE'}}.

## The cross-card rules: **PASS** {'PASS': 24, 'INCONCLUSIVE': 2}

| X rule | E122 | E108 × scale | difference | ± h | w | verdict | at the arms |
|---|---|---|---|---|---|---|---|
| X-fp32.step | 4.921 ± 0.136 | 4.798 × 1.0300 = 4.942 | -0.021 | 0.354 | 0.75 | **PASS** | same at all |
| X-fp16.step | 4.901 ± 0.153 | 4.981 × 1.0332 = 5.147 | -0.246 | 0.190 | 0.75 | **PASS** | same at all |
| X-fp32.held_z | 1.923 ± 0.242 | 1.985 × 1.0300 = 2.045 | -0.122 | 0.285 | 0.75 | **PASS** | same at all |
| X-fp16.held_z | 2.084 ± 0.011 | 2.124 × 1.0332 = 2.195 | -0.110 | 0.170 | 0.75 | **PASS** | same at all |
| X-fp32.held_abs | 2.675 ± 0.434 | 2.480 × 1.0300 = 2.554 | +0.121 | 0.545 | 0.75 | **PASS** | leak0.3803 INCONCLUSIVE; leak0 INCONCLUSIVE |
| X-fp32.Bz_het | 3.089 ± 0.169 | 2.907 × 1.0300 = 2.994 | +0.094 | 0.210 | 0.75 | **PASS** | same at all |
| X-fp32.Bz_rest | 3.238 ± 0.082 | 2.998 × 1.0300 = 3.088 | +0.149 | 0.152 | 0.75 | **PASS** | same at all |
| X-fp32.het_mx | 2.537 ± 0.153 | 2.532 × 1.0300 = 2.608 | -0.071 | 0.337 | 0.75 | **PASS** | same at all |
| X-fp32.rest | 2.157 ± 0.230 | 2.235 × 1.0300 = 2.302 | -0.144 | 0.288 | 0.75 | **PASS** | dips_kept INCONCLUSIVE |
| X-fp32.ex_over_sg | 0.611 ± 0.367 | 0.633 × 1.0300 = 0.652 | -0.041 | 0.444 | 0.75 | **PASS** | same at all |
| X-fp32.mx_over_ex | 1.938 ± 0.309 | 1.739 × 1.0300 = 1.791 | +0.146 | 0.385 | 0.75 | **PASS** | same at all |
| X-fp32.alt_held | 4.369 ± 0.220 | 4.160 × 1.0300 = 4.285 | +0.083 | 0.504 | 0.75 | **PASS** | leak0.545 INCONCLUSIVE; leak0 INCONCLUSIVE |
| X-fp32.alt_walk | 2.188 ± 0.157 | 2.002 × 1.0300 = 2.062 | +0.125 | 0.661 | 0.75 | **INCONCLUSIVE** | same at all |
| X-fp16.alt_walk | 3.254 ± 0.240 | 3.144 × 1.0332 = 3.249 | +0.006 | 0.296 | 0.75 | **PASS** | leak0.545 INCONCLUSIVE |
| X-fp32.A_on_B_held | -0.217 ± 0.262 | -0.255 × 1.0300 = -0.263 | +0.046 | 0.587 | 0.75 | **PASS** | leak0.545 INCONCLUSIVE |
| X-fp32.A_on_B_walk | -0.328 ± 0.038 | -0.269 × 1.0300 = -0.278 | -0.051 | 0.196 | 0.75 | **PASS** | same at all |
| X-A_vs_B_priced | 0.018 ± 0.178 | -0.031 × 1.0300 = -0.032 | +0.050 | 0.392 | 0.75 | **PASS** | same at all |
| X-fp32.share_z | 0.391 ± 0.044 | 0.414 × 1.0000 = 0.414 | -0.024 | 0.057 | 0.15 | **PASS** | same at all |
| X-fp16.share_z | 0.425 ± 0.013 | 0.426 × 1.0000 = 0.426 | -0.001 | 0.040 | 0.15 | **PASS** | same at all |
| X-fp32.share_abs | 0.543 ± 0.076 | 0.517 × 1.0000 = 0.517 | +0.026 | 0.102 | 0.15 | **PASS** | leak0.3803 INCONCLUSIVE |
| X-formats_z | 0.035 ± 0.051 | 0.012 × 1.0000 = 0.012 | +0.022 | 0.055 | 0.15 | **PASS** | same at all |
| X-design_fp32 | 0.152 ± 0.058 | 0.103 × 1.0000 = 0.103 | +0.049 | 0.068 | 0.15 | **PASS** | same at all |
| X-fp32.share_het | 1.177 ± 0.054 | 1.133 × 1.0000 = 1.133 | +0.045 | 0.105 | 0.15 | **PASS** | dips_kept INCONCLUSIVE; auto INCONCLUSIVE; leak0.3803 INCONCLUSIVE; leak0.545 INCONCLUSIVE; leak0 INCONCLUSIVE |
| X-fp32.share_het_z | 0.954 ± 0.036 | 0.970 × 1.0000 = 0.970 | -0.016 | 0.038 | 0.15 | **PASS** | leak0.545 INCONCLUSIVE |
| X-fp32.alt_ratio | 0.501 ± 0.032 | 0.485 × 1.0000 = 0.485 | +0.016 | 0.188 | 0.3 | **PASS** | same at all |
| X-alt_walk_ratio | 1.490 ± 0.149 | 1.615 × 1.0000 = 1.615 | -0.125 | 0.503 | 0.6 | **INCONCLUSIVE** | leak0 PASS |
