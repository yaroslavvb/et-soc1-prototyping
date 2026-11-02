== session: passes [12110, 12111, 12112, 12113] | leak {'mode': '0.1994', 'k_w_per_c': 0.1994, 'n_runs': -1} | clock 600 MHz | v_mean 521.7 mV
idle level (W, launch reading): {'mean': 25.90647257017544, 'se': 0.0047473169972994025, 'n': 4, 'ci95': 0.015105962685406699}
runs 158 kept 158 failed []
dip samples removed per pass: {'p12110': 17, 'p12111': 12, 'p12112': 10, 'p12113': 5}
cycles per op: {'fp32': 546.001, 'fp16': 546.001, 'int8': 318.0}

== the table: per tile, D over the type's zeros, S over idle, pJ/MAC from S, dT over the window, Drail (from e121.json > items)
tile | gated | D | S | pJ/MAC (S) | dT | Drail | n
anchor_pi | 0.0 | 8.423 ± 0.093 | 10.451 ± 0.038 | 2.276 ± 0.009 | 0.84 | 7.16 | 4
fp16.a_dnr_b_randn | 0.0 | 13.269 ± 0.109 | 15.263 ± 0.231 | 1.662 ± 0.026 | 1.85 | 11.03 | 4
fp16.a_nz_b_randn | 0.0 | 12.785 ± 0.059 | 14.827 ± 0.138 | 1.614 ± 0.015 | 1.97 | 10.62 | 4
fp16.a_randn_b_nz | 0.0 | 12.117 ± 0.067 | 14.114 ± 0.175 | 1.537 ± 0.020 | 1.86 | 10.05 | 4
fp16.dnr_both | 0.0 | 9.524 ± 0.058 | 11.497 ± 0.072 | 1.252 ± 0.007 | 1.55 | 7.93 | 4
fp16.nz_both | 0.0 | 8.183 ± 0.188 | 10.112 ± 0.080 | 1.101 ± 0.009 | 1.07 | 6.94 | 4
fp16.randn | 0.0 | 22.139 ± 0.098 | 24.128 ± 0.032 | 2.628 ± 0.003 | 2.78 | 17.89 | 4
fp16.zeros | 1.0 | 0.000 ± 0.000 | 1.984 ± 0.096 | 0.216 ± 0.011 | 0.02 | 0.00 | 4
fp32.a_dnr_b_randn | 0.0 | 13.223 ± 0.056 | 15.191 ± 0.038 | 3.309 ± 0.007 | 1.78 | 10.85 | 4
fp32.a_nz_b_randn | 0.0 | 12.439 ± 0.052 | 14.444 ± 0.091 | 3.145 ± 0.018 | 1.61 | 10.49 | 4
fp32.a_randn_b_dnr | 0.0 | 13.699 ± 0.117 | 15.687 ± 0.107 | 3.417 ± 0.025 | 1.50 | 11.35 | 4
fp32.a_randn_b_nz | 0.0 | 12.832 ± 0.040 | 14.800 ± 0.110 | 3.223 ± 0.025 | 1.99 | 10.59 | 4
fp32.a_zeros_b_randn | 1.0 | 0.722 ± 0.145 | 2.635 ± 0.055 | 0.574 ± 0.012 | 0.40 | 0.64 | 4
fp32.dn1_both | 0.0 | 8.389 ± 0.100 | 10.314 ± 0.152 | 2.245 ± 0.033 | 1.01 | 7.05 | 4
fp32.dnr_both | 0.0 | 9.739 ± 0.052 | 11.702 ± 0.086 | 2.550 ± 0.019 | 1.55 | 8.19 | 4
fp32.nz_both | 0.0 | 8.232 ± 0.190 | 10.107 ± 0.201 | 2.201 ± 0.044 | 1.00 | 6.97 | 4
fp32.randn | 0.0 | 24.741 ± 0.045 | 26.674 ± 0.056 | 5.809 ± 0.011 | 3.09 | 19.78 | 4
fp32.sparse50 | 0.77417 | 7.331 ± 0.047 | 9.338 ± 0.112 | 2.034 ± 0.023 | 1.04 | 6.16 | 4
fp32.sparse50_mask | 0.485107 | 13.146 ± 0.183 | 15.106 ± 0.189 | 3.290 ± 0.042 | 1.84 | 10.92 | 4
fp32.zeros | 1.0 | 0.000 ± 0.000 | 1.978 ± 0.146 | 0.431 ± 0.032 | 0.03 | 0.00 | 4
int8.a_3of4_b_full | 0.0 | 5.877 ± 0.195 | 8.450 ± 0.283 | 0.268 ± 0.009 | 1.00 | 5.02 | 4
int8.a_zeros_b_full | 1.0 | 0.243 ± 0.150 | 2.762 ± 0.083 | 0.088 ± 0.003 | 0.22 | 0.32 | 3
int8.b_pairs_alt | 0.0 | 5.691 ± 0.126 | 8.202 ± 0.082 | 0.260 ± 0.003 | 1.00 | 4.84 | 4
int8.b_pairs_rtl | 0.5 | 4.272 ± 0.147 | 6.856 ± 0.110 | 0.217 ± 0.003 | 0.75 | 3.66 | 4
int8.b_unpaired | 0.0 | 5.710 ± 0.122 | 8.300 ± 0.101 | 0.263 ± 0.003 | 0.75 | 4.85 | 4
int8.full | 0.0 | 7.120 ± 0.055 | 9.722 ± 0.043 | 0.308 ± 0.001 | 0.98 | 5.91 | 4
int8.zeros | 1.0 | 0.000 ± 0.000 | 2.521 ± 0.093 | 0.080 ± 0.003 | 0.37 | 0.00 | 4

== this session's card scale (D here over E93's D on card 1), post hoc
fp32.randn 1.0306
fp16.randn 1.0255
int8.full 1.0225
anchor_pi 1.0421

== reported (score_e93.reported's block on this session)
minus_zero_premium_w | fp32 both sides, over zeros: 8.232 ± 0.190 (n 4)
minus_zero_premium_w | fp16 both sides, over zeros: 8.183 ± 0.188 (n 4)
minus_zero_premium_w | fp32 A side, over its +0 mirror in the same pass: 11.717 ± 0.119 (n 4)
denormal_vs_minus_zero_w | fp32 both: 1.507 ± 0.138 (n 4)
denormal_vs_minus_zero_w | fp32 constant: 0.156 ± 0.152 (n 4)
denormal_vs_minus_zero_w | fp32 A side: 0.784 ± 0.104 (n 4)
denormal_vs_minus_zero_w | fp32 B side: 0.867 ± 0.137 (n 4)
denormal_vs_minus_zero_w | fp16 both: 1.341 ± 0.143 (n 4)
denormal_vs_minus_zero_w | fp16 A side: 0.484 ± 0.144 (n 4)
booth_asymmetry_w | fp32: 0.393 ± 0.089 (n 4)
booth_asymmetry_w | fp16: -0.668 ± 0.119 (n 4)
int8_unit_costs_w | gated: 1.424 ± 0.327 (n 4)
int8_unit_costs_w | live_zero_b: 4.299 ± 0.244 (n 4)
int8_unit_costs_w | share_of_full_b_pairs_rtl: 0.600 ± 0.024 (n 4)
int8_unit_costs_w | share_of_full_b_unpaired: 0.802 ± 0.018 (n 4)
constant_vs_minus_zero_w (anchor_pi - fp32.nz_both): 0.190 ± 0.156 (n 4)
sparse_mask_w: 5.815 ± 0.148 (n 4)

== post hoc: the same numbers on card 1 (E93's scored.json > reported) beside
E93 booth_asymmetry_w | fp32: 0.308 ± 0.158 (n 5)
E93 booth_asymmetry_w | fp16: -0.755 ± 0.158 (n 5)
E93 int8_unit_costs_w | gated: 1.548 ± 0.314 (n 5)
E93 int8_unit_costs_w | live_zero_b: 4.045 ± 0.303 (n 5)
E93 int8_unit_costs_w | share_of_full_b_pairs_rtl: 0.611 ± 0.023 (n 5)
E93 int8_unit_costs_w | share_of_full_b_unpaired: 0.791 ± 0.026 (n 5)

== post hoc: int8's gate law on the half-gated tile, this session (E93 result 8's form)
b_pairs_rtl - (0.5 full + 0.5 a_zeros_b_full), same pass: 0.545 ± 0.149 (n 3)
b_pairs_rtl / full, same pass: 0.600 ± 0.024 (n 4)
b_pairs_rtl - E93's frozen point x int8 scale (3.61 x 1.027062 = 3.709): 0.564 ± 0.147 (n 4)

== post hoc: R5's pieces, fp32, this session
a_randn_b_nz - a_nz_b_randn: 0.393 ± 0.089 (n 4)
fp16 twin a_randn_b_nz - a_nz_b_randn: -0.668 ± 0.119 (n 4)

== post hoc: denormal fraction per raw bit (fJ), fp32 both sides: (dnr_both - dn1_both) / (70,976 bits x 1.125e9 /s)
fJ per raw denormal bit: 16.911 ± 1.001 (n 4)

== arms: passes kept and set aside (scored.json > arms)
dips_kept kept [12112, 12113] set aside [{'pass': 12110, 'why': ['fp16.randn spans 1.155 W']}, {'pass': 12111, 'why': ['int8.full spans 1.027 W']}] | gate NOT SCORED {'NOT SCORED': 24} | X NOT SCORED {'NOT SCORED': 24} | tie PASS | same as E93 0 of 24
auto kept [12110, 12111, 12112, 12113] set aside [] | gate PASS {'PASS': 23, 'FAIL': 1} | X PASS {'PASS': 23, 'INCONCLUSIVE': 1} | tie PASS | same as E93 24 of 24
leak0.2414 kept [12110, 12111, 12112, 12113] set aside [] | gate PASS {'PASS': 23, 'FAIL': 1} | X PASS {'PASS': 23, 'INCONCLUSIVE': 1} | tie PASS | same as E93 24 of 24
leak0.3803 kept [12110, 12111, 12113] set aside [{'pass': 12112, 'why': ['int8.zeros departs -0.270 W from its straight line']}] | gate INCONCLUSIVE {'PASS': 22, 'FAIL': 1, 'UNRESOLVED': 1} | X PASS {'PASS': 20, 'INCONCLUSIVE': 3, 'UNRESOLVED': 1} | tie FAIL | same as E93 23 of 24
leak0.545 kept [12110, 12111] set aside [{'pass': 12112, 'why': ['int8.zeros departs -0.396 W from its straight line']}, {'pass': 12113, 'why': ['int8.zeros departs -0.277 W from its straight line']}] | gate NOT SCORED {'NOT SCORED': 24} | X NOT SCORED {'NOT SCORED': 24} | tie FAIL | same as E93 0 of 24
leak0 kept [12110, 12111, 12112, 12113] set aside [] | gate PASS {'PASS': 23, 'FAIL': 1} | X PASS {'PASS': 23, 'INCONCLUSIVE': 1} | tie FAIL | same as E93 24 of 24
auto slope: {'mode': 'auto', 'k_w_per_c': 0.1553235294117689, 'n_runs': 103}

== skipped runs (E78's launch-reading rule), from the raw marks
12110 [('int8.a_zeros_b_full', 17, 59.0), ('fp16.zeros', 19, 59.0)]
12111 []
12112 []
12113 []

== post hoc: D here over E93's D, every cell E93 read at 4 W or more (the session's own card scale, cell by cell)
22 cells: median 1.0302, range 1.0039 (int8.b_pairs_rtl) to 1.0574 (fp32.sparse50); within 1.5% of E82's 1.031: 18 of 22

== post hoc: largest |difference| in the session tie against E78 (scored.json > primary > tie_e78)
(0.08884826141929159, 'fp32.a_zeros_b_randn')
