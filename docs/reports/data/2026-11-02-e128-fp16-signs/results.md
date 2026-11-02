# E128 results

Passes kept: [12810, 12811]; set aside: []; leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}

| rule | verdict | dips_kept | gates_off | auto | leak0.1994 | leak0.3803 | leak0.545 | leak0 | numbers |
|---|---|---|---|---|---|---|---|---|---|
| E128-R1 | **PASS** |  |  |  |  |  |  |  | {'reads': 76, 'n_off': 0, 'n_unread': 0} |
| E128-R3 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'fp32.share_het_m': '1.021 ± 1.053 (M4 1.054)'} |
| E128-R4 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'fp32.share_walk_m': '-0.021 ± 1.053 (M4 -0.054)'} |
| E128-R5 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'fp32.design_m': '0.066 ± 1.011 (M4 0.09)'} |
| E128-R6 | **MOST** | NOT SCORED | MOST | MOST | MOST | MOST | MOST | MOST | {'fp32.share_het_z': '0.954 ± 0.041 (M4 0.964)'} |
| E128-R7 | **MOST** | NOT SCORED | MOST | MOST | MOST | MOST | MOST | MOST | {'fp16.share_het_z': '1.006 ± 0.119 (M4 1.045)'} |
| E128-R8 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | MOST | {'fp16.share_het_m': '0.926 ± 0.307 (M4 1.042)'} |
| E128-R9 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'fp16.share_walk_m': '0.074 ± 0.307 (M4 -0.042)'} |
| E128-R10 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | 1.55x HOLDS | 1.55x HOLDS | 1.55x HOLDS | INCONCLUSIVE | INCONCLUSIVE | {'alt_walk_ratio': '1.727 ± 0.162 (M4 1.543)'} |
| E128-R12 | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'formats_m': '-0.095 ± 0.746 (M4 -0.012)'} |
| E128-R2 | **PASS** | NOT SCORED | PASS | PASS | PASS | PASS | PASS | PASS | {} |
| E128-R11 | **PASS** | NOT SCORED | PASS | PASS | PASS | PASS | INCONCLUSIVE | PASS | {'rms_w': 0.225, 'n': 19, 'bias_w': 0.104, 'worst': (0.6507275465549824, 'fp16.w_h_add'), 'inside_95': 19, 'new_rms_w': 0.158, 'new_n': 6, 'new_bias_w': 0.053, 'new_inside_95': 6} |
| E128-S1 | **PASS** | NOT SCORED | PASS | PASS | PASS | FAIL | FAIL | FAIL | {} |
| E128-X | **INCONCLUSIVE** | NOT SCORED | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | {'tally': {'INCONCLUSIVE': 9, 'PASS': 5, 'UNRESOLVED': 2}} |
| E128-P | **1.55x HOLDS** | NOT SCORED | 1.55x HOLDS | 1.55x HOLDS | 1.55x HOLDS | 1.55x HOLDS | 1.55x HOLDS | 1.55x HOLDS | {'mean': 1.587, 'ci95': 0.147, 'n': 10} |

## The cross-session rules (E122's form)

| X rule | against | E128 | ref × s | difference | ± h | w | verdict | dips_kept | gates_off | auto | leak0.1994 | leak0.3803 | leak0.545 | leak0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X108-alt_walk_ratio | E108 (aifoundry1 card 1, this card) | 1.727 ± 0.162 | 1.614 × 1.0000 = 1.614 | +0.113 | 0.507 | 0.6 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X122-alt_walk_ratio | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 1.727 ± 0.162 | 1.490 × 1.0000 = 1.490 | +0.237 | 0.220 | 0.6 | **PASS** |  | PASS | PASS | PASS | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X108-fp32.alt_walk | E108 (aifoundry1 card 1, this card) | 1.963 ± 0.835 | 2.002 × 1.0000 = 2.002 | -0.039 | 1.042 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X122-fp32.alt_walk | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 1.963 ± 0.835 | 2.188 × 0.9709 = 2.124 | -0.161 | 0.849 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | PASS | PASS | INCONCLUSIVE |
| X108-fp16.alt_walk | E108 (aifoundry1 card 1, this card) | 3.389 ± 1.124 | 3.144 × 1.0000 = 3.144 | +0.245 | 1.136 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | PASS |
| X122-fp16.alt_walk | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 3.389 ± 1.124 | 3.254 × 0.9678 = 3.150 | +0.240 | 1.147 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | PASS |
| X108-fp32.share_het_z | E108 (aifoundry1 card 1, this card) | 0.954 ± 0.041 | 0.970 × 1.0000 = 0.970 | -0.016 | 0.043 | 0.15 | **PASS** |  | PASS | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| X122-fp32.share_het_z | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 0.954 ± 0.041 | 0.954 × 1.0000 = 0.954 | +0.000 | 0.055 | 0.15 | **PASS** |  | PASS | PASS | PASS | PASS | INCONCLUSIVE | PASS |
| X108-fp32.Bz_het | E108 (aifoundry1 card 1, this card) | 2.909 ± 1.506 | 2.907 × 1.0000 = 2.907 | +0.002 | 1.511 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X122-fp32.Bz_het | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 2.909 ± 1.506 | 3.089 × 0.9709 = 2.999 | -0.090 | 1.515 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X108-fp32.Bz_rest | E108 (aifoundry1 card 1, this card) | 3.049 ± 1.710 | 2.998 × 1.0000 = 2.998 | +0.051 | 1.715 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X122-fp32.Bz_rest | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 3.049 ± 1.710 | 3.238 × 0.9709 = 3.143 | -0.094 | 1.712 | 0.75 | **INCONCLUSIVE** |  | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| X108-fp32.step | E108 (aifoundry1 card 1, this card) | 4.656 ± 0.404 | 4.798 × 1.0000 = 4.798 | -0.142 | 0.514 | 0.75 | **PASS** |  | PASS | PASS | PASS | PASS | PASS | PASS |
| X122-fp32.step | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 4.656 ± 0.404 | 4.921 × 0.9709 = 4.778 | -0.122 | 0.425 | 0.75 | **PASS** |  | PASS | PASS | PASS | PASS | PASS | PASS |
| X108-fp16.step | E108 (aifoundry1 card 1, this card) | 4.697 | 4.981 × 1.0000 = 4.981 | — | — | 0.75 | **UNRESOLVED** |  | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| X122-fp16.step | E122 (aifoundry3 card 0), divided by E82's per-type card scale | 4.697 | 4.901 × 0.9678 = 4.743 | — | — | 0.75 | **UNRESOLVED** |  | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |

## The pooled moving-sum ratio: **1.55x HOLDS**, 1.587 ± 0.147 over 10 passes; inverse-variance arm 1.710 ± 0.024 (INCONCLUSIVE)

| session | mean | se |
|---|---:|---:|
| E108 | 1.614 | 0.151 |
| E122 | 1.490 | 0.047 |
| E128 | 1.727 | 0.013 |

## The read-back

| tile | n | minions agreeing | off rtl | off manual | off frozen | equals | card C00 / C08 | words on the card |
|---|---:|---:|---:|---:|---:|---|---|---:|
| `fp16.b_B_w` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c0800000 | 11 |
| `fp16.b_B_w` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c4fa0000 | 11 |
| `fp16.b_B_w` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c8c33080 | 11 |
| `fp16.b_B_w` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c98452f0 | 11 |
| `fp16.b_B_wm` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42100000 / 42200000 | 11 |
| `fp16.b_B_wm` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 468ca000 / 469c4000 | 11 |
| `fp16.b_B_wm` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a5b9690 / 4a73fca0 | 11 |
| `fp16.b_B_wm` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b14dd4e / 4b2567ac | 11 |
| `fp16.b_B_z` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c0800000 | 11 |
| `fp16.b_B_z` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c4fa0000 | 11 |
| `fp16.b_B_z` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c8c33080 | 11 |
| `fp16.b_B_z` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 00000000 / c98452f0 | 11 |
| `fp16.b_B_zm` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42100000 / 42200000 | 11 |
| `fp16.b_B_zm` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 468ca000 / 469c4000 | 11 |
| `fp16.b_B_zm` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a5b9690 / 4a73fca0 | 11 |
| `fp16.b_B_zm` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b14dd4e / 4b2567ac | 11 |
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
| `fp32.b_B_w` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c1400000 / 40800000 | 8 |
| `fp32.b_B_w` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c5bb8000 / 44fa0000 | 8 |
| `fp32.b_B_w` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c9926460 / 48c33080 | 8 |
| `fp32.b_B_w` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | ca467c68 / 498452f0 | 8 |
| `fp32.b_B_wm` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 41f00000 / 41600000 | 8 |
| `fp32.b_B_wm` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 466a6000 / 45dac000 | 8 |
| `fp32.b_B_wm` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a36fd78 / 49aaca70 | 8 |
| `fp32.b_B_wm` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4af81b82 / 4a679124 | 8 |
| `fp32.b_B_z` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c1400000 / 40800000 | 8 |
| `fp32.b_B_z` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c5bb8000 / 44fa0000 | 8 |
| `fp32.b_B_z` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | c9926460 / 48c33080 | 8 |
| `fp32.b_B_z` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | ca467c68 / 498452f0 | 8 |
| `fp32.b_B_zm` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 41f00000 / 41600000 | 8 |
| `fp32.b_B_zm` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 466a6000 / 45dac000 | 8 |
| `fp32.b_B_zm` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a36fd78 / 49aaca70 | 8 |
| `fp32.b_B_zm` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4af81b82 / 4a679124 | 8 |
| `fp32.c_abs` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 72000000 / 72000000 | 1 |
| `fp32.c_abs` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 767a0000 / 767a0000 | 1 |
| `fp32.c_abs` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7a433080 / 7a433080 | 1 |
| `fp32.c_abs` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 7b0452f0 / 7b0452f0 | 1 |
| `fp32.m_h_sub` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 46f23000 / 467a0000 | 2 |
| `fp32.m_h_sub` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4abd16fc / 4a433080 | 2 |
| `fp32.m_h_sub` | 500000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b6c82e0 / 4af42400 | 2 |
| `fp32.ones` | 2 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 42000000 / 42000000 | 1 |
| `fp32.ones` | 1000 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 467a0000 / 467a0000 | 1 |
| `fp32.ones` | 199874 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4a433080 / 4a433080 | 1 |
| `fp32.ones` | 541999 | 1024 | 0 | 0 | 0 | rtl, manual, fl | 4b0452f0 / 4b0452f0 | 1 |
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
| `fp32.step` | contrast | 4.656 ± 0.404 | 2 | 4.799 ± 0.55 | the sign step, fp32 |
| `fp32.held_z` | contrast | 1.846 ± 1.819 | 2 | 2.001 ± 0.58 | random B signs on zero products, the sum held (E104's z_s), fp32 |
| `fp32.rest_vs_z` | contrast | 2.810 ± 2.223 | 2 | 2.798 ± 0.80 | the step less the zero-product held part (the step's rest), fp32 |
| `fp32.Bz_het` | contrast | 2.909 ± 1.506 | 2 | 2.973 ± 0.65 | E108's design, fp32: held at b_B_w's sums over held at z_s's equal ones |
| `fp32.Bz_walk` | contrast | 0.140 ± 0.204 | 2 | 0.111 ± 0.58 | E108's design, fp32: walking over held at the same sums at every op's end (alternations differ) |
| `fp32.Bz_rest` | contrast | 3.049 ± 1.710 | 2 | 3.084 ± 0.62 | E108's design, fp32: B's rest on zero products |
| `fp32.Bm_het` | contrast | 3.666 ± 1.004 | 2 | 3.536 ± 0.62 | matched, fp32: the accumulators differing (held at b_B_wm's sums over z_s's equal ones) |
| `fp32.Bm_walk` | contrast | -0.056 ± 3.743 | 2 | -0.180 ± 0.56 | matched, fp32: the sums changing (walking over held at the same op-end sums, the same alternations) |
| `fp32.Bm_rest` | contrast | 3.610 ± 2.739 | 2 | 3.356 ± 0.61 | matched, fp32: B's rest on zero products |
| `fp32.held_alt` | contrast | -0.757 ± 2.511 | 2 | -0.563 ± 0.59 | two held tiles with differing accumulators, fp32: E108's design over the matched one (other alternation counts and other C words) |
| `fp32.walk_alt` | contrast | -0.560 ± 1.029 | 2 | -0.271 ± 0.55 | two walking tiles, fp32: E108's design over the matched one (other alternation counts, A's sign, other sums) |
| `fp32.alt_walk` | contrast | 1.963 ± 0.835 | 2 | 1.715 ± 1.25 | alternating against a fixed product sign, walking, the same magnitudes (E104's pair), fp32 |
| `fp16.step` | contrast | 4.697 | 1 | 4.854 ± 0.55 | the sign step, fp16 |
| `fp16.held_z` | contrast | 2.084 ± 0.728 | 2 | 2.201 ± 0.50 | random B signs on zero products, the sum held (E104's z_s), fp16 |
| `fp16.rest_vs_z` | contrast | 2.556 | 1 | 2.653 ± 0.74 | the step less the zero-product held part (the step's rest), fp16 |
| `fp16.Bz_het` | contrast | 3.476 ± 0.640 | 2 | 3.532 ± 0.58 | E108's design, fp16: held at b_B_w's sums over held at z_s's equal ones |
| `fp16.Bz_walk` | contrast | -0.020 ± 0.405 | 2 | -0.153 ± 0.64 | E108's design, fp16: walking over held at the same sums at every op's end (alternations differ) |
| `fp16.Bz_rest` | contrast | 3.456 ± 1.045 | 2 | 3.379 ± 0.60 | E108's design, fp16: B's rest on zero products |
| `fp16.Bm_het` | contrast | 3.064 ± 0.236 | 2 | 3.398 ± 0.52 | matched, fp16: the accumulators differing (held at b_B_wm's sums over z_s's equal ones) |
| `fp16.Bm_walk` | contrast | 0.247 ± 1.079 | 2 | -0.136 ± 0.52 | matched, fp16: the sums changing (walking over held at the same op-end sums, the same alternations) |
| `fp16.Bm_rest` | contrast | 3.311 ± 0.843 | 2 | 3.262 ± 0.52 | matched, fp16: B's rest on zero products |
| `fp16.held_alt` | contrast | 0.412 ± 0.877 | 2 | 0.134 ± 0.57 | two held tiles with differing accumulators, fp16: E108's design over the matched one (other alternation counts and other C words) |
| `fp16.walk_alt` | contrast | 0.144 ± 0.203 | 2 | 0.117 ± 0.60 | two walking tiles, fp16: E108's design over the matched one (other alternation counts, A's sign, other sums) |
| `fp16.alt_walk` | contrast | 3.389 ± 1.124 | 2 | 2.646 ± 0.88 | alternating against a fixed product sign, walking, the same magnitudes (E104's pair), fp16 |
| `fp32.share_z` | ratio | 0.397 ± 0.425 | 2 | 0.417 | fp32's held share, zero products, one session |
| `fp32.share_het_z` | ratio | 0.954 ± 0.041 | 2 | 0.964 | E108's design, fp32: how much of B's rest held accumulators at b_B_w's sums carry (E108-R12's form) |
| `fp32.share_het_m` | ratio | 1.021 ± 1.053 | 2 | 1.054 | matched, fp32: how much of B's rest goes with the accumulators differing |
| `fp32.share_walk_m` | ratio | -0.021 ± 1.053 | 2 | -0.054 | matched, fp32: how much of B's rest goes with the sums changing |
| `fp32.rest_ratio_m` | ratio | 1.285 ± 0.042 | 2 | 1.199 | fp32: B's rest on zero products (matched) over the step's rest |
| `fp16.share_z` | ratio | 0.456 | 1 | 0.453 | fp16's held share, zero products, one session |
| `fp16.share_het_z` | ratio | 1.006 ± 0.119 | 2 | 1.045 | E108's design, fp16: how much of B's rest held accumulators at b_B_w's sums carry (E108-R12's form) |
| `fp16.share_het_m` | ratio | 0.926 ± 0.307 | 2 | 1.042 | matched, fp16: how much of B's rest goes with the accumulators differing |
| `fp16.share_walk_m` | ratio | 0.074 ± 0.307 | 2 | -0.042 | matched, fp16: how much of B's rest goes with the sums changing |
| `fp16.rest_ratio_m` | ratio | 1.321 | 1 | 1.230 | fp16: B's rest on zero products (matched) over the step's rest |
| `fp32.design_m` | diff | 0.066 ± 1.011 | 2 | 0.090 | fp32: the matched share less E108's design's share, one session |
| `fp16.design_m` | diff | -0.080 ± 0.188 | 2 | -0.004 | fp16: the matched share less E108's design's share, one session |
| `formats_m` | diff | -0.095 ± 0.746 | 2 | -0.012 | the location's like for like: fp16's matched share less fp32's |
| `formats_z` | diff | 0.093 | 1 | 0.036 | the held share's like for like (E108-R3's quantity), one session |
| `alt_walk_ratio` | ratio | 1.727 ± 0.162 | 2 | 1.543 | E104-R6 / E108-R10: fp16 over fp32, walking |

## The tiles

| tile | group | D, W (95%) | M4 [95%] | D - M4 |
|---|---|---:|---:|---:|
| `fp16.b_B_w` | E108's design in fp16: B's signs walking | 13.67 ± 1.00 | 13.62 [13.14, 14.10] | +0.05 |
| `fp16.b_B_wm` | matched: B's signs walking, alternations as z_s | 13.53 ± 0.79 | 13.51 [13.12, 13.89] | +0.02 |
| `fp16.b_B_z` | E108's design in fp16: held, zero products, at b_B_w's sums | 13.69 ± 0.59 | 13.78 [13.33, 14.22] | -0.08 |
| `fp16.b_B_zm` | matched: held, zero products, at b_B_wm's sums | 13.28 ± 0.29 | 13.64 [13.26, 14.02] | -0.36 |
| `fp16.c_abs` | held baseline | 8.13 ± 0.78 | 8.04 [7.67, 8.42] | +0.09 |
| `fp16.m_h_sub` | product sign alternating, walking | 15.81 ± 0.95 | 15.72 [15.16, 16.28] | +0.09 |
| `fp16.ones` | the +1 side of the step | 8.14 ± 0.29 | 8.07 [7.70, 8.44] | +0.07 |
| `fp16.w_h_add` | fixed product sign, walking | 12.42 ± 2.07 | 13.07 [12.38, 13.77] | -0.65 |
| `fp16.z_s` | held, zero products, B's signs, equal accumulators | 10.22 ± 0.05 | 10.24 [9.87, 10.62] | -0.03 |
| `fp32.b_B_w` | E108's: B's signs walking | 12.94 ± 0.89 | 13.14 [12.74, 13.54] | -0.20 |
| `fp32.b_B_wm` | matched: B's signs walking, alternations as z_s | 13.50 ± 0.14 | 13.41 [13.02, 13.81] | +0.09 |
| `fp32.b_B_z` | E108's: held, zero products, at b_B_w's sums | 12.80 ± 1.10 | 13.03 [12.58, 13.48] | -0.23 |
| `fp32.b_B_zm` | matched: held, zero products, at b_B_wm's sums | 13.56 ± 3.61 | 13.59 [13.18, 14.01] | -0.03 |
| `fp32.c_abs` | held baseline | 8.05 ± 0.78 | 8.06 [7.68, 8.43] | -0.01 |
| `fp32.m_h_sub` | product sign alternating, walking | 14.41 ± 2.67 | 14.60 [13.64, 15.57] | -0.20 |
| `fp32.ones` | the +1 side of the step | 8.15 ± 0.03 | 8.08 [7.70, 8.45] | +0.08 |
| `fp32.signs` | the +-1 side of the step | 12.81 ± 0.43 | 12.88 [12.46, 13.29] | -0.07 |
| `fp32.w_h_add` | fixed product sign, walking | 12.44 ± 1.84 | 12.89 [12.08, 13.70] | -0.45 |
| `fp32.z_s` | held, zero products, B's signs, equal accumulators | 9.89 ± 2.60 | 10.06 [9.57, 10.54] | -0.16 |
