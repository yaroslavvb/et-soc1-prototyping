== passes: [14210, 14211, 14212, 14213, 14214] set aside: [] leak: {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}
== verdicts (primary) and arm sensitivity
  E142-P1: PASS | rms 0.169 W n 9 interval [0.093, 0.366] below False | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'FAIL', 'relaxed': 'PASS'}
  E142-P2: PASS | rms 0.149 W n 8 interval [0.085, 0.294] below False | arms {'auto': 'FAIL', 'dips_kept': 'FAIL', 'leak0.1994': 'PASS', 'leak0.3803': 'FAIL', 'leak0': 'FAIL', 'relaxed': 'PASS'}
  E142-P3: PASS | rms 0.251 W n 7 interval [0.115, 0.416] below False | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'PASS', 'relaxed': 'PASS'}
  E142-B1: PASS | bias +0.050 W n 17 interval [-0.090, +0.105] | arms {'auto': 'FAIL HIGH', 'dips_kept': 'PASS', 'leak0.1994': 'FAIL LOW', 'leak0.3803': 'FAIL HIGH', 'leak0': 'FAIL LOW', 'relaxed': 'PASS'}
  E142-B2: PASS | bias -0.038 W n 7 interval [-0.161, +0.214] | arms {'auto': 'FAIL HIGH', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'PASS', 'relaxed': 'PASS'}
  E142-C1: PASS | 30 of 30 (low end 26); outside [] | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'FAIL', 'relaxed': 'PASS'}
  E142-M1: NOT RESOLVED | d -0.003 W [-0.042, +0.025] n 24 | arms {'auto': 'NOT RESOLVED', 'dips_kept': 'NOT RESOLVED', 'leak0.1994': 'NOT RESOLVED', 'leak0.3803': 'NOT RESOLVED', 'leak0': 'NOT RESOLVED', 'relaxed': 'NOT RESOLVED'}
  E142-M2: NOT RESOLVED | d -0.054 W [-0.148, +0.024] n 24 | arms {'auto': 'NOT RESOLVED', 'dips_kept': 'NOT RESOLVED', 'leak0.1994': 'NOT RESOLVED', 'leak0.3803': 'BETTER', 'leak0': 'NOT RESOLVED', 'relaxed': 'NOT RESOLVED'}
  E142-H1: PASS | rms 0.167 C n 9 interval [0.195, 0.509] below True | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'PASS', 'relaxed': 'PASS'}
  E142-H2: PASS | rms 0.162 C n 8 interval [0.181, 0.524] below True | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'PASS', 'relaxed': 'PASS'}
  E142-H3: PASS | rms 0.139 C n 7 interval [0.067, 0.211] below False | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'PASS', 'relaxed': 'PASS'}
  E142-H4: PASS | 29 of 30 (low end 26); outside ['int8.a_word_flipflop'] | arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'PASS', 'relaxed': 'PASS'}
  E142-X1: NOT SCORED | E141's reduction of pool 5 on aifoundry3 was not given (handed on) | arms {'auto': 'NOT SCORED', 'dips_kept': 'NOT SCORED', 'leak0.1994': 'NOT SCORED', 'leak0.3803': 'NOT SCORED', 'leak0': 'NOT SCORED', 'relaxed': 'NOT SCORED'}
  E142-X2: NOT SCORED | E141's reduction of pool 5 on aifoundry3 was not given (handed on) | arms {'auto': 'NOT SCORED', 'dips_kept': 'NOT SCORED', 'leak0.1994': 'NOT SCORED', 'leak0.3803': 'NOT SCORED', 'leak0': 'NOT SCORED', 'relaxed': 'NOT SCORED'}
== reported per model (priority-1 rms / bias per format; 30 non-anchor rms / bias; coverage)
  M7: fp32 rms 0.169 bias +0.067; fp16 rms 0.149 bias +0.030; int8 rms 0.251 bias -0.038; all30 rms 0.211 bias +0.001; inside 30/30 outside []
     heat: fp32 rms 0.167 bias +0.094; fp16 rms 0.162 bias +0.134; int8 rms 0.139 bias -0.053; inside 29/30 outside ['int8.a_word_flipflop']
  M6: fp32 rms 0.162 bias +0.106; fp16 rms 0.170 bias -0.034; int8 rms 0.248 bias -0.051; all30 rms 0.211 bias -0.003; inside 29/30 outside ['int8.powerlaw_w']
     heat: fp32 rms 0.163 bias +0.090; fp16 rms 0.147 bias +0.119; int8 rms 0.138 bias -0.058; inside 30/30 outside []
  M5: fp32 rms 0.228 bias +0.045; fp16 rms 0.249 bias +0.104; int8 rms 0.259 bias -0.080; all30 rms 0.254 bias -0.010; inside 27/30 outside ['fp16.wideexp_bgate_alt', 'fp32.wideexp48_bgate_alt', 'int8.powerlaw_w']
  arm auto (leak 0.40773717381689395): M7 fp32 rms 0.349 bias -0.335; fp16 rms 0.394 bias -0.375; int8 rms 0.296 bias -0.179; inside 27/30; passes [14210, 14211, 14212, 14213, 14214] set aside []
  arm dips_kept (leak 0.2414): M7 fp32 rms 0.290 bias +0.144; fp16 rms 0.315 bias -0.095; int8 rms 0.261 bias +0.054; inside 30/30; passes [14210, 14211] set aside [{'pass': 14212, 'why': ['anchor_pi drifts -0.705 W']}, {'pass': 14213, 'why': ['fp32.randn spans 1.638 W']}, {'pass': 14214, 'why': ['anchor_pi drifts +1.034 W']}]
  arm leak0.1994 (leak 0.1994): M7 fp32 rms 0.252 bias +0.194; fp16 rms 0.192 bias +0.128; int8 rms 0.227 bias +0.005; inside 30/30; passes [14210, 14211, 14213, 14214] set aside [{'pass': 14212, 'why': ['int8.zeros departs +0.253 W from its straight line']}]
  arm leak0.3803 (leak 0.3803): M7 fp32 rms 0.288 bias -0.269; fp16 rms 0.332 bias -0.308; int8 rms 0.284 bias -0.156; inside 28/30; passes [14210, 14211, 14212, 14213, 14214] set aside []
  arm leak0 (leak 0.0): M7 fp32 rms 0.719 bias +0.676; fp16 rms 0.642 bias +0.612; int8 rms 0.302 bias +0.173; inside 21/30; passes [14210, 14211, 14213, 14214] set aside [{'pass': 14212, 'why': ['int8.zeros departs +0.271 W from its straight line']}]
  arm relaxed (leak 0.2414): M7 fp32 rms 0.169 bias +0.067; fp16 rms 0.149 bias +0.030; int8 rms 0.251 bias -0.038; inside 30/30; passes [14210, 14211, 14212, 14213, 14214] set aside []
== both-card reference arm: {'E142-P1': 'PASS', 'E142-P2': 'PASS', 'E142-P3': 'PASS'}
== heat at the measured run length (registered reported arm): {"T_run_median_s": {"fp32": 4.461, "fp16": 4.468, "int8": 4.399}, "rms_c": {"fp32": 0.13134169839697699, "fp16": 0.11027900620529787, "int8": 1.285986464792601}, "bias_c": {"fp32": -0.0141419083244771, "fp16": 0.033543509396581295, "int8": 0.5667435422987993}, "coverage": {"verdict": "PASS", "inside": 28, "n": 30, "share": 0.9333333333333333, "binomial_low_2p5": 26, "outside": ["int8.a_word_flipflop", "int8.b_line_zero_one"]}}
   post hoc a_run_mark_duration: T_run {'fp32': 4.5975, 'fp16': 4.603, 'int8': 4.522} rms {'fp32': 0.43833836825115347, 'fp16': 0.45416860418899824, 'int8': 0.1377928179260285} bias {'fp32': 0.4085303075371217, 'fp16': 0.45033716722576866, 'int8': -0.02392150382614494} inside 30/30 left out []
   post hoc b_registered_formula_items_over_5s_left_out: T_run {'fp32': 4.46, 'fp16': 4.468, 'int8': 4.3915} rms {'fp32': 0.13134169839697699, 'fp16': 0.11027900620529787, 'int8': 0.17587350402938265} bias {'fp32': -0.0141419083244771, 'fp16': 0.033543509396581295, 'int8': -0.15587008808639743} inside 28/28 left out ['fp16.anchor_zeros', 'fp32.anchor_zeros', 'int8.a_word_flipflop', 'int8.anchor_zeros', 'int8.b_line_zero_one']
== rise per board W: {'c_per_w': 0.11974689274709384, 'n': 30, 'M7_card1': 0.1151065674167393}
== pool anchors:
  fp16.anchor_randn: measured D 21.364 M7 21.240 error +0.125 inside True dT 2.790
  fp16.anchor_zeros: measured D -0.015 M7 0.000 error -0.015 inside True dT -0.090
  fp32.anchor_randn: measured D 24.166 M7 23.779 error +0.386 inside True dT 3.194
  fp32.anchor_zeros: measured D -0.031 M7 0.000 error -0.031 inside True dT 0.000
  int8.anchor_full: measured D 6.929 M7 6.811 error +0.118 inside True dT 1.130
  int8.anchor_zeros: measured D 0.034 M7 0.000 error +0.034 inside True dT 0.010
== E78 anchors D (this session): {'fp32.randn': ('24.060', [24.156, 24.206, 24.007, 23.875, 24.057]), 'fp16.randn': ('21.533', [21.549, 21.515, 21.449, 21.611, 21.539]), 'int8.full': ('6.937', [6.888, 7.14, 6.858, 6.843, 6.955])}
   E131 fp32.randn: 23.963 over 4 passes
   E131 fp16.randn: 21.467 over 4 passes
   E131 int8.full: 6.891 over 4 passes
== per tile (M7 power; error = measured - M7):
  fp16.anchor_randn                  p2a meas 21.364 sd 0.113 M7 21.240 err +0.125 in True | M6 err +0.052 M5 err +0.128 | dT 2.790 pred 2.650 err +0.140 in True
  fp16.anchor_zeros                  p2a meas -0.015 sd 0.153 M7 0.000 err -0.015 in True | M6 err -0.015 M5 err -0.015 | dT -0.090 pred 0.205 err -0.295 in True
  fp16.exp_only                      p2  meas 15.822 sd 0.077 M7 15.935 err -0.114 in True | M6 err -0.120 M5 err -0.199 | dT 2.210 pred 2.039 err +0.171 in True
  fp16.pair_cancel_asign             p1  meas 16.093 sd 0.172 M7 16.339 err -0.247 in True | M6 err -0.367 M5 err -0.193 | dT 2.190 pred 2.086 err +0.104 in True
  fp16.pair_nearcancel               p1  meas 21.322 sd 0.175 M7 21.167 err +0.155 in True | M6 err +0.077 M5 err +0.164 | dT 2.700 pred 2.642 err +0.058 in True
  fp16.real_pythia_ln2_up            p1  meas 21.591 sd 0.177 M7 21.450 err +0.141 in True | M6 err +0.076 M5 err +0.139 | dT 2.750 pred 2.674 err +0.076 in True
  fp16.real_pythia_qk                p1  meas 20.568 sd 0.047 M7 20.491 err +0.076 in True | M6 err +0.053 M5 err +0.077 | dT 2.660 pred 2.564 err +0.096 in True
  fp16.real_pythia_softmax_v         p1  meas 16.700 sd 0.088 M7 16.851 err -0.151 in True | M6 err -0.083 M5 err -0.146 | dT 2.220 pred 2.145 err +0.075 in True
  fp16.sparse24_aligned              p1  meas 12.459 sd 0.070 M7 12.417 err +0.042 in True | M6 err -0.209 M5 err +0.024 | dT 1.978 pred 1.634 err +0.344 in True
  fp16.sparse24_straddled            p1  meas 21.272 sd 0.140 M7 21.065 err +0.206 in True | M6 err +0.177 M5 err +0.175 | dT 2.738 pred 2.630 err +0.108 in True
  fp16.wideexp_bgate_alt             p1  meas 13.088 sd 0.085 M7 13.069 err +0.018 in True | M6 err +0.003 M5 err +0.596 | dT 1.922 pred 1.710 err +0.212 in True
  fp32.anchor_randn                  p2a meas 24.166 sd 0.108 M7 23.779 err +0.386 in True | M6 err +0.336 M5 err +0.306 | dT 3.194 pred 2.944 err +0.250 in True
  fp32.anchor_zeros                  p2a meas -0.031 sd 0.120 M7 0.000 err -0.031 in True | M6 err -0.031 M5 err -0.031 | dT 0.000 pred 0.207 err -0.207 in True
  fp32.b_exp_busy_a_const            p2  meas 15.114 sd 0.136 M7 15.136 err -0.022 in True | M6 err +0.058 M5 err -0.176 | dT 2.041 pred 1.949 err +0.092 in True
  fp32.block_sparse_k4               p2  meas 12.245 sd 0.117 M7 12.416 err -0.172 in True | M6 err -0.005 M5 err -0.199 | dT 1.540 pred 1.636 err -0.096 in True
  fp32.e4m3grid_gelu_w               p1  meas 16.359 sd 0.160 M7 16.249 err +0.110 in True | M6 err +0.116 M5 err -0.039 | dT 2.080 pred 2.077 err +0.003 in True
  fp32.exp_only_both                 p1  meas 15.317 sd 0.204 M7 15.338 err -0.020 in True | M6 err -0.075 M5 err -0.197 | dT 2.060 pred 1.972 err +0.088 in True
  fp32.gray_stream                   p1  meas 16.111 sd 0.292 M7 16.193 err -0.082 in True | M6 err +0.048 M5 err -0.094 | dT 1.900 pred 2.071 err -0.171 in True
  fp32.lowrank2_w                    p2  meas 24.070 sd 0.168 M7 23.797 err +0.273 in True | M6 err +0.225 M5 err +0.184 | dT 3.060 pred 2.946 err +0.114 in True
  fp32.real_pythia_gelu_down         p1  meas 21.759 sd 0.151 M7 21.646 err +0.113 in True | M6 err +0.215 M5 err +0.035 | dT 2.890 pred 2.698 err +0.192 in True
  fp32.real_pythia_ln1_q             p1  meas 21.500 sd 0.109 M7 21.442 err +0.058 in True | M6 err +0.136 M5 err -0.014 | dT 2.620 pred 2.675 err -0.055 in True
  fp32.sorted_k                      p1  meas 22.468 sd 0.088 M7 22.358 err +0.110 in True | M6 err +0.123 M5 err +0.081 | dT 2.936 pred 2.780 err +0.156 in True
  fp32.wideexp48_bgate_alt           p1  meas 14.701 sd 0.119 M7 14.688 err +0.012 in True | M6 err +0.004 M5 err +0.542 | dT 2.010 pred 1.898 err +0.112 in True
  fp32.wideexp48_bgate_kblk          p1  meas 12.816 sd 0.118 M7 12.947 err -0.131 in True | M6 err +0.015 M5 err -0.192 | dT 1.970 pred 1.697 err +0.273 in True
  fp32.wideexp48_dense               p1  meas 25.353 sd 0.204 M7 24.916 err +0.437 in True | M6 err +0.368 M5 err +0.286 | dT 3.324 pred 3.075 err +0.249 in True
  int8.a_word_flipflop               p1  meas 3.236 sd 0.159 M7 3.429 err -0.193 in True | M6 err -0.105 M5 err -0.281 | dT 0.370 pred 0.663 err -0.293 in False
  int8.anchor_full                   p2a meas 6.929 sd 0.169 M7 6.811 err +0.118 in True | M6 err +0.154 M5 err +0.163 | dT 1.130 pred 1.052 err +0.078 in True
  int8.anchor_zeros                  p2a meas 0.034 sd 0.251 M7 0.000 err +0.034 in True | M6 err +0.034 M5 err +0.034 | dT 0.010 pred 0.268 err -0.258 in True
  int8.b_line_flipflop_nogate        p1  meas 6.176 sd 0.177 M7 6.177 err -0.001 in True | M6 err -0.266 M5 err -0.255 | dT 0.990 pred 0.979 err +0.011 in True
  int8.b_line_zero_one               p1  meas 3.287 sd 0.183 M7 3.854 err -0.567 in True | M6 err -0.512 M5 err -0.494 | dT 0.800 pred 0.712 err +0.088 in True
  int8.block_sparse_a                p2  meas 4.248 sd 0.169 M7 4.202 err +0.046 in True | M6 err +0.029 M5 err +0.000 | dT 0.800 pred 0.752 err +0.048 in True
  int8.gray_a                        p1  meas 4.261 sd 0.135 M7 4.251 err +0.009 in True | M6 err +0.014 M5 err -0.026 | dT 0.600 pred 0.758 err -0.158 in True
  int8.powerlaw_w                    p2  meas 5.625 sd 0.182 M7 6.207 err -0.582 in True | M6 err -0.608 M5 err -0.593 | dT 1.000 pred 0.983 err +0.017 in True
  int8.real_pythia_w8a8_down         p1  meas 6.225 sd 0.227 M7 6.025 err +0.200 in True | M6 err +0.167 M5 err +0.174 | dT 0.850 pred 0.962 err -0.112 in True
  int8.real_pythia_w8a8_up           p1  meas 6.130 sd 0.175 M7 5.980 err +0.149 in True | M6 err +0.144 M5 err +0.131 | dT 1.000 pred 0.957 err +0.043 in True
  int8.sorted_k                      p1  meas 5.995 sd 0.168 M7 5.855 err +0.140 in True | M6 err +0.198 M5 err +0.188 | dT 0.989 pred 0.942 err +0.047 in True
== errors by case (M7, non-anchor):
  1 fp16 pairs that cancel (E140 miss): n 2 mean -0.046 rms 0.206
  2 spread exponents beside gated zeros (E140 miss): n 4 mean +0.084 rms 0.228
  3 exponent-only activity (E140 miss): n 3 mean -0.052 rms 0.068
  5 real model (pythia-70m layer 0 forward): n 7 mean +0.084 rms 0.135
  6 whole-line / whole-word flip-flops (E140 miss): n 3 mean -0.254 rms 0.346
  7 few mantissa bits (E140 suspicion): n 1 mean +0.110 rms 0.110
  8 seeded realistic weights: n 2 mean -0.155 rms 0.455
  9 structured stream: n 8 mean +0.037 rms 0.120
== telemetry max: board 62.09 hottest shire 65
  e142/p14210: samples 5222 board 30.42-61.89 (p999 61.71) shire mean 53-63 hottest 65 pmic 63 mhz [600] since_reset [-1] rail@34.5 2
  e142/p14211: samples 5188 board 31.31-62.09 (p999 61.89) shire mean 55-63 hottest 65 pmic 63 mhz [600] since_reset [-1] rail@34.5 0
  e142/p14212: samples 5193 board 31.45-61.89 (p999 61.75) shire mean 55-63 hottest 65 pmic 63 mhz [600] since_reset [-1] rail@34.5 0
  e142/p14213: samples 5131 board 31.15-61.95 (p999 61.67) shire mean 54-63 hottest 65 pmic 63 mhz [600] since_reset [-1] rail@34.5 0
  e142/p14214: samples 5035 board 31.42-61.61 (p999 61.51) shire mean 55-63 hottest 65 pmic 63 mhz [600] since_reset [-1] rail@34.5 0
