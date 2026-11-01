E114 readme numbers (desk, after the data; decides nothing). Times are the Intel's local clock (PST).
results.json sha256 2a4a11334d13, reduce.txt sha256 c1c082ec36b9, predictions-e114.json sha256 91731cedb7b6

== A. The session
session start 14:18:26, end 14:39:43, exit 0 (done), card_min 21.3, runs 15 of 15
marks by kind: {"logins": 1, "config_start": 1, "sampler_start": 15, "use_count_baseline": 15, "sampler_stop": 15}
sampler stops: 15, ending 'rc 0': 15
E114 smoke: die at the gate [46.0, 47.0] C, board [18.18, 18.59] W
E84 smoke: die at the gate [48.0, 50.0, 50.0] C, board [18.94, 19.12, 19.1] W
E114 first run: die at the gate [47.0] C, board [18.64] W
E84 first run: die at the gate [49.0] C, board [18.9] W
cooling gates: held 0.1-0.1 s, die at the gate 47.0-57.0 C, all reached: True
run start to next run start: 84.2-86.9 s (median 85.15)
launch processes: 135, rc 0: 135
ettelem config after every run: ['{"tdp_w": 65, "temp_threshold_c": 65}']
  session start read: tdp 65 W, threshold 65 C, 600 MHz, 519 mV
  session end read: tdp 65 W, threshold 65 C, 600 MHz, 519 mV
  final-143947.out: first line '2026-11-01 14:39:47 PST'; config lines ['{"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":519}']
  ident-141810.out: first line '2026-11-01 14:18:10 PST'; config lines ['{"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":519}']

== B. The cells (results.json cells)
fp16/zeros: n 3, runs ['SUS-00-fp16-zeros-r1', 'SUS-00-fp16-zeros-r2', 'SUS-00-fp16-zeros-r3']
   rate         mean 24.286 sd 0.3146 ci95 0.7817 pi95 1.5634 runs [24.363, 23.94, 24.555], E84 24.354, E84 - mean 0.068, inside pi95 True
   mhz          mean 791.9 sd 9.329 ci95 23.1764 pi95 46.3527 runs [794.0, 781.7, 800], E84 794.1, E84 - mean 2.2, inside pi95 True
   mhz_nonramp  mean 797.7 sd 3.9837 ci95 9.8969 pi95 19.7938 runs [800, 793.1, 800], E84 794.1, E84 - mean -3.6, inside pi95 True
   w            mean 28.69 sd 0.591 ci95 1.4683 pi95 2.9366 runs [28.73, 28.08, 29.26], E84 29.6, E84 - mean 0.91, inside pi95 True
   die          mean 53.5 sd 0.8185 ci95 2.0335 pi95 4.067 runs [53.3, 52.8, 54.4], E84 56.0, E84 - mean 2.5, inside pi95 True
   limits ['none', 'none', 'none'] (E84 none); ramp share [0.034, 0.065, 0.0] (E84 0.0); die max [54, 53, 55] (E84 57); die at the gate [54.0, 51.0, 57.0]; idle W [20.25, 19.37, 21.1]; PMIC average [28.67, 28.14, 29.16]
   counts {'800': 372, 'thermal': 0, 'power': 0, 'ramp': 13, 'other': 0, 'n': 385}
   counts {'800': 348, 'thermal': 0, 'power': 0, 'ramp': 25, 'other': 14, 'n': 387}
   counts {'800': 386, 'thermal': 0, 'power': 0, 'ramp': 0, 'other': 0, 'n': 386}
   rate ci95 as a share of the mean: 3.22%; E84 off the mean by +0.28%
fp16/ones: n 3, runs ['SUS-01-fp16-ones-r1', 'SUS-01-fp16-ones-r2', 'SUS-01-fp16-ones-r3']
   rate         mean 24.3737 sd 0.0221 ci95 0.055 pi95 0.11 runs [24.399, 24.364, 24.358], E84 24.395, E84 - mean 0.0213, inside pi95 True
   mhz          mean 794.8 sd 0.7 ci95 1.739 pi95 3.4781 runs [795.6, 794.5, 794.3], E84 795.6, E84 - mean 0.8, inside pi95 True
   mhz_nonramp  mean 800 sd 0.0 ci95 0.0 pi95 0.0 runs [800, 800, 800], E84 800, E84 - mean 0, inside pi95 True
   w            mean 45.9233 sd 0.4236 ci95 1.0524 pi95 2.1047 runs [45.78, 46.4, 45.59], E84 46.72, E84 - mean 0.7967, inside pi95 True
   die          mean 62.1667 sd 1.0786 ci95 2.6796 pi95 5.3591 runs [61.7, 63.4, 61.4], E84 63.9, E84 - mean 1.7333, inside pi95 True
   limits ['none', 'none', 'none'] (E84 none); ramp share [0.026, 0.031, 0.031] (E84 0.026); die max [63, 64, 62] (E84 65); die at the gate [50.0, 57.0, 51.0]; idle W [19.17, 21.14, 19.2]; PMIC average [45.25, 45.93, 45.1]
   counts {'800': 375, 'thermal': 0, 'power': 0, 'ramp': 10, 'other': 0, 'n': 385}
   counts {'800': 372, 'thermal': 0, 'power': 0, 'ramp': 12, 'other': 0, 'n': 384}
   counts {'800': 374, 'thermal': 0, 'power': 0, 'ramp': 12, 'other': 0, 'n': 386}
   rate ci95 as a share of the mean: 0.23%; E84 off the mean by +0.09%
fp16/randn: n 3, runs ['SUS-02-fp16-randn-r1', 'SUS-02-fp16-randn-r2', 'SUS-02-fp16-randn-r3']
   rate         mean 19.7293 sd 0.3645 ci95 0.9055 pi95 1.811 runs [20.15, 19.508, 19.53], E84 19.107, E84 - mean -0.6223, inside pi95 True
   mhz          mean 657.2667 sd 13.5149 ci95 33.5757 pi95 67.1513 runs [672.8, 648.2, 650.8], E84 631.9, E84 - mean -25.3667, inside pi95 True
   mhz_nonramp  mean 657.2667 sd 13.5149 ci95 33.5757 pi95 67.1513 runs [672.8, 648.2, 650.8], E84 631.9, E84 - mean -25.3667, inside pi95 True
   w            mean 52.36 sd 1.4294 ci95 3.5512 pi95 7.1024 runs [53.99, 51.32, 51.77], E84 49.04, E84 - mean -3.32, inside pi95 True
   die          mean 65.5 sd 0.0 ci95 0.0 pi95 0.0 runs [65.5, 65.5, 65.5], E84 65.8, E84 - mean 0.3, inside pi95 False
   limits ['thermal', 'thermal', 'thermal'] (E84 thermal); ramp share [0.0, 0.0, 0.0] (E84 0.0); die max [66, 67, 66] (E84 67); die at the gate [47.0, 55.0, 55.0]; idle W [18.65, 20.41, 20.42]; PMIC average [53.17, 50.36, 50.64]
   counts {'800': 60, 'thermal': 326, 'power': 0, 'ramp': 0, 'other': 0, 'n': 386}
   counts {'800': 17, 'thermal': 369, 'power': 0, 'ramp': 0, 'other': 0, 'n': 386}
   counts {'800': 16, 'thermal': 370, 'power': 0, 'ramp': 0, 'other': 0, 'n': 386}
   rate ci95 as a share of the mean: 4.59%; E84 off the mean by -3.15%
int8/zeros: n 3, runs ['SUS-03-int8-zeros-r1', 'SUS-03-int8-zeros-r2', 'SUS-03-int8-zeros-r3']
   rate         mean 82.7907 sd 0.4719 ci95 1.1725 pi95 2.3449 runs [82.254, 82.977, 83.141], E84 83.709, E84 - mean 0.9183, inside pi95 True
   mhz          mean 787.1 sd 3.5 ci95 8.6952 pi95 17.3904 runs [783.1, 788.6, 789.6], E84 794.6, E84 - mean 7.5, inside pi95 True
   mhz_nonramp  mean 797.9667 sd 3.5218 ci95 8.7494 pi95 17.4989 runs [793.9, 800, 800], E84 800, E84 - mean 2.0333, inside pi95 True
   w            mean 29.7433 sd 0.1665 ci95 0.4137 pi95 0.8274 runs [29.61, 29.93, 29.69], E84 30.87, E84 - mean 1.1267, inside pi95 False
   die          mean 54.2667 sd 0.2082 ci95 0.5172 pi95 1.0343 runs [54.2, 54.5, 54.1], E84 56.9, E84 - mean 2.6333, inside pi95 False
   limits ['none', 'none', 'none'] (E84 none); ramp share [0.062, 0.062, 0.057] (E84 0.031); die max [55, 55, 55] (E84 57); die at the gate [57.0, 56.0, 54.0]; idle W [21.0, 20.68, 20.33]; PMIC average [29.5, 29.87, 29.65]
   counts {'800': 348, 'thermal': 0, 'power': 0, 'ramp': 24, 'other': 12, 'n': 384}
   counts {'800': 361, 'thermal': 0, 'power': 0, 'ramp': 24, 'other': 0, 'n': 385}
   counts {'800': 364, 'thermal': 0, 'power': 0, 'ramp': 22, 'other': 0, 'n': 386}
   rate ci95 as a share of the mean: 1.42%; E84 off the mean by +1.11%
int8/full: n 3, runs ['SUS-04-int8-full-r1', 'SUS-04-int8-full-r2', 'SUS-04-int8-full-r3']
   rate         mean 83.4667 sd 0.323 ci95 0.8024 pi95 1.6049 runs [83.094, 83.64, 83.666], E84 83.078, E84 - mean -0.3887, inside pi95 True
   mhz          mean 792.7333 sd 2.7209 ci95 6.7597 pi95 13.5193 runs [789.6, 794.5, 794.1], E84 788.7, E84 - mean -4.0333, inside pi95 True
   mhz_nonramp  mean 800 sd 0.0 ci95 0.0 pi95 0.0 runs [800, 800, 800], E84 800, E84 - mean 0, inside pi95 True
   w            mean 43.64 sd 0.2425 ci95 0.6024 pi95 1.2048 runs [43.36, 43.78, 43.78], E84 44.42, E84 - mean 0.78, inside pi95 True
   die          mean 60.3667 sd 0.1155 ci95 0.2869 pi95 0.5737 runs [60.3, 60.3, 60.5], E84 62.8, E84 - mean 2.4333, inside pi95 False
   limits ['none', 'none', 'none'] (E84 none); ramp share [0.057, 0.031, 0.034] (E84 0.062); die max [61, 61, 61] (E84 64); die at the gate [51.0, 50.0, 51.0]; idle W [19.27, 19.04, 19.27]; PMIC average [42.81, 43.34, 43.38]
   counts {'800': 364, 'thermal': 0, 'power': 0, 'ramp': 22, 'other': 0, 'n': 386}
   counts {'800': 373, 'thermal': 0, 'power': 0, 'ramp': 12, 'other': 0, 'n': 385}
   counts {'800': 374, 'thermal': 0, 'power': 0, 'ramp': 13, 'other': 0, 'n': 387}
   rate ci95 as a share of the mean: 0.96%; E84 off the mean by -0.47%

== C. The ratios (results.json rho) and the rules
rho fp16: 1.2312 +- 0.0605 [1.1707, 1.2917], pairs [(1, 1.20908, 121.2), (2, 1.22719, 133.5), (3, 1.2573, 149.2)], ratio of means {'ratio': 1.231, 'se_delta': 0.016}, E84 1.2746
   95% prediction interval for one pass pair: 1.1102 to 1.3522; E84's single pair 1.2746 inside
rho int8: 0.9919 +- 0.0048 [0.9871, 0.9967], pairs [(1, 0.98989, -6.5), (2, 0.99207, -5.9), (3, 0.99373, -4.5)], ratio of means {'ratio': 0.9919, 'se_delta': 0.0039}, E84 1.0076
   95% prediction interval for one pass pair: 0.9823 to 1.0015; E84's single pair 1.0076 OUTSIDE
E114-R1: PASS | {"scored": 5, "inside": 5, "need": 4, "verdict": "PASS", "expected": "PASS"}
   ['fp16/zeros', 3, 24.286, 1.5634, 24.354, 0.068, 'inside']
   ['fp16/ones', 3, 24.3737, 0.11, 24.395, 0.0213, 'inside']
   ['fp16/randn', 3, 19.7293, 1.811, 19.107, -0.6223, 'inside']
   ['int8/zeros', 3, 82.7907, 2.3449, 83.709, 0.9183, 'inside']
   ['int8/full', 3, 83.4667, 1.6049, 83.078, -0.3887, 'inside']
E114-R2: PASS | {"rho16": 1.2312, "ci95": 0.0605, "lo": 1.1707, "hi": 1.2917, "n_pairs": 3, "bar": 1.15, "verdict": "PASS", "expected": "PASS", "e84": 1.2746}
E114-R3: WRONG | {"rho8": 0.9919, "ci95": 0.0048, "lo": 0.9871, "hi": 0.9967, "n_pairs": 3, "bar": 0.02, "reading": "SLOWER", "expected": "SAME_WITHIN_BAR", "verdict": "WRONG", "e84": 1.0076}
E114-R4: PASS | {"runs": 15, "mismatches": [], "verdict": "PASS", "expected": "PASS"}
E114-S1 fp16: {"rho_card0": 1.2312, "rho_aifoundry2": 1.3114, "se_card0": 0.0141, "se_aifoundry2": 0.0056, "df": 2, "delta": -0.0802, "ci95": 0.0653, "lo": -0.1455, "hi": -0.0149, "bar": 0.05, "reading": "DIFFERENT", "expected": "DIFFERENT (card 0 lower: its random fp16 draws less power and throttles less, while both cards' zeros sit near the 800 MHz cap; at three pairs the interval may not resolve it)"}
E114-S1 int8: {"rho_card0": 0.9919, "rho_aifoundry2": 1.0093, "se_card0": 0.0011, "se_aifoundry2": 0.006, "df": 2, "delta": -0.0174, "ci95": 0.0264, "lo": -0.0438, "hi": 0.009, "bar": 0.02, "reading": "INCONCLUSIVE", "expected": "INCONCLUSIVE"}

== D. aifoundry2 beside (predictions-e114.json aifoundry2_pool, from E80/E83/E87/E96 results.json)
fp16: zeros 24.474 sd 0.1647 n 4; heavy 18.6623 sd 0.1215 n 6; ratio of means 1.3114
int8: zeros 83.5343 sd 0.6091 n 4; heavy 82.7608 sd 1.1095 n 8; ratio of means 1.0093
card 0 minus aifoundry2 in rate, the four ratio kinds:
  fp16 zeros 24.286 vs 24.474 (-0.77%); heavy 19.7293 vs 18.6623 (+5.72%)
  int8 zeros 82.7907 vs 83.5343 (-0.89%); heavy 83.4667 vs 82.7608 (+0.85%)

== E. Heat path (context): each run's die minus E84's die line at its board W
{"n": 15, "runs": [-1.941, -1.654, -2.089, -2.135, -1.839, -0.672, -0.434, -1.506, -2.326, -2.289, -1.792, -2.049, -0.886, -1.287, -2.089], "mean": -1.6659, "sd": 0.5948, "ci95": 0.3294, "pi95": 1.3177, "line": {"a_c": 41.78, "b_c_per_w": 0.4753, "n_runs": 13, "what": "die = a + b x board W over E84's 13 sustained runs (per-run sus_w_mean, sus_die_mean), E84 corrections-check C1"}, "e114_own_line": {"a_c": 39.361, "b_c_per_w": 0.4941, "n": 15}}
