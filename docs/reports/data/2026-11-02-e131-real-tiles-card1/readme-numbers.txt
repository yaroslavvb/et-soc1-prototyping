== A. The session
   11:14:46 p13110 starts at T0+45 s (projected 560 s)
   11:25:38 p13110 rc=0 (652 s)
   11:25:48 p13111 starts at T0+707 s (projected 652 s)
   11:36:08 p13111 rc=0 (620 s)
   11:36:18 p13112 starts at T0+1337 s (projected 652 s)
   11:45:25 p13112 rc=0 (547 s)
   11:45:35 p13113 starts at T0+1894 s (projected 652 s)
   11:55:02 p13113 rc=0 (567 s)
   11:55:12 budget: stopping before p13114 (now T0+2471 s, projected 652 s, would end T0+3123 s > T0+2640 s)
   11:55:12 e131: done, 4 passes, at T0+2471 s
   config-session-start: {"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":500} at 2026-11-02T11:14:01-08:00
   config-session-end: {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499} at 2026-11-02T11:55:12-08:00
   p13110: ok, 651 s, die 50 -> 55 C; 53 runs, 79 heater launches (13 before the burn-ins, 66 at the runs: 1.25 a run)
      config start {"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":499}
      config end   {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
   p13111: ok, 620 s, die 53 -> 56 C; 53 runs, 69 heater launches (13 before the burn-ins, 56 at the runs: 1.06 a run)
      config start {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
      config end   {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
   p13112: ok, 546 s, die 54 -> 55 C; 53 runs, 52 heater launches (7 before the burn-ins, 45 at the runs: 0.85 a run)
      config start {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
      config end   {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
   p13113: ok, 567 s, die 53 -> 56 C; 53 runs, 57 heater launches (10 before the burn-ins, 47 at the runs: 0.89 a run)
      config start {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
      config end   {"tdp_w":65,"temp_threshold_c":65,"power_state":1,"power_state_name":"managed_power","minion_mhz":600,"minion_mv":499}
   e131-smoke-p13101: ok, 45 s, die 48 -> 50 C; 7 runs, 0 heater launches (0 before the burn-ins, 0 at the runs: 0.00 a run)
      config start {"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":499}
      config end   {"tdp_w":65,"temp_threshold_c":65,"power_state":3,"power_state_name":"low_power","minion_mhz":600,"minion_mv":499}
   dips removed per pass (primary): {'p13110': 34, 'p13111': 33, 'p13112': 30, 'p13113': 32}
   primary: passes [13110, 13111, 13112, 13113], runs kept 212 of 212, set aside [], leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}, clock 600 MHz, mean minion voltage 498.6 mV, idle 33.035 W

== B. Each claim beside E95 on aifoundry3 (its dips-removed arm, five passes, and its registered primary, four)
   C1: E131 FAIL; E95 dips-removed arm FAIL; E95 primary FAIL; arm-sensitive False; at the arms {'auto': 'FAIL', 'dips_kept': 'FAIL', 'leak0.1994': 'FAIL', 'leak0.3803': 'FAIL', 'leak0': 'NOT SCORED', 'leak0.545': 'FAIL'}
   C2: E131 PASS; E95 dips-removed arm PASS; E95 primary INCONCLUSIVE; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C3a: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C3b: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C4: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C5: E131 INCONCLUSIVE; E95 dips-removed arm INCONCLUSIVE; E95 primary INCONCLUSIVE; arm-sensitive True; at the arms {'auto': 'INCONCLUSIVE', 'dips_kept': 'INCONCLUSIVE', 'leak0.1994': 'INCONCLUSIVE', 'leak0.3803': 'INCONCLUSIVE', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C6: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C7: E131 INCONCLUSIVE; E95 dips-removed arm INCONCLUSIVE; E95 primary UNDER-RESOLVED; arm-sensitive False; at the arms {'auto': 'INCONCLUSIVE', 'dips_kept': 'INCONCLUSIVE', 'leak0.1994': 'INCONCLUSIVE', 'leak0.3803': 'INCONCLUSIVE', 'leak0': 'NOT SCORED', 'leak0.545': 'INCONCLUSIVE'}
   C8: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive True; at the arms {'auto': 'PASS', 'dips_kept': 'INCONCLUSIVE', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C9: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C10: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C11: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive True; at the arms {'auto': 'PASS', 'dips_kept': 'INCONCLUSIVE', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C12: E131 PASS; E95 dips-removed arm PASS; E95 primary PASS; arm-sensitive False; at the arms {'auto': 'PASS', 'dips_kept': 'PASS', 'leak0.1994': 'PASS', 'leak0.3803': 'PASS', 'leak0': 'NOT SCORED', 'leak0.545': 'PASS'}
   C1 cells, E131 / E95 dips removed:
      gpt2/fp32: 0.9830 ± 0.0052 INCONCLUSIVE / 0.9873 ± 0.0035 PASS
      gpt2/fp16: 0.9563 ± 0.0094 FAIL / 0.9562 ± 0.0060 FAIL
      bert/fp32: 0.9898 ± 0.0080 PASS / 0.9942 ± 0.0029 PASS
      bert/fp16: 0.9918 ± 0.0146 INCONCLUSIVE / 0.9964 ± 0.0020 PASS
      vit/fp32: 0.9974 ± 0.0144 PASS / 0.9985 ± 0.0043 PASS
      vit/fp16: 0.9817 ± 0.0107 INCONCLUSIVE / 0.9862 ± 0.0063 INCONCLUSIVE
   C2 fp32: 0.9883 ± 0.0076 / 0.9916 ± 0.0038
   C2 fp16: 0.9766 ± 0.0026 / 0.9795 ± 0.0046
   C6: +2.949 ± 0.193 W / +3.128 ± 0.137 W
   C8: +0.677 ± 0.123 W / +0.832 ± 0.087 W
   C11: -0.120 ± 0.223 W / -0.009 ± 0.024 W
   C4 vgg16_fc2: +0.1455 ± 0.0099 / +0.1392 ± 0.0065
   C4 resnet18_l3c1: +0.0640 ± 0.0050 / +0.0609 ± 0.0035
   C4 t5small_l0_down: +0.0864 ± 0.0117 / +0.0950 ± 0.0040
   C5 int8/resnet18_l3c1: D 4.310 ± 0.179 W, (a) 3.5207, (c) 5.7319, nearer a / E95 D 4.356 ± 0.158 nearer a
   C5 int8/vgg16_fc2: D 3.896 ± 0.167 W, (a) 2.6337, (c) 4.694, nearer c / E95 D 3.884 ± 0.136 nearer c
   C7 int8/gpt2_l6_down_p9999: -0.009 ± 0.326 W / E95 -0.058 ± 0.335
   C7 int8/gpt2_l6_down_per_token: -0.012 ± 0.092 W / E95 +0.000 ± 0.273
   C7 int8/gpt2_l6_down_p999: +0.135 ± 0.383 W / E95 +0.014 ± 0.183
   C9 D 19.726 ± 0.225 W / E95 20.180 ± 0.081
   C10 r 0.8898 ± 0.0115 / E95 0.8857 ± 0.0066
   C12 23 of 25 / E95 23 of 25
   C3b fp32: slope/L 0.949 (per pass 0.949 ± 0.006) / E95 0.955
   C3b fp16: slope/L 0.937 (per pass 0.937 ± 0.037) / E95 0.929

== C. The cross-card rows (carrying reading against E95's dips-removed arm)
   fp32: 11 tiles; r(card 1) - r(aifoundry3): median -0.0024, max |diff| 0.0102; card 1's r half-widths median 0.0080, max 0.0144; D ratio a3/c1 median 1.0227 (0.8845-1.0279, every row incl. the random kind)
   fp16: 10 tiles; r(card 1) - r(aifoundry3): median -0.0027, max |diff| 0.0091; card 1's r half-widths median 0.0075, max 0.0146; D ratio a3/c1 median 1.0227 (1.0090-1.0297, every row incl. the random kind)
   int8: 12 tiles; r(card 1) - r(aifoundry3): median -0.0006, max |diff| 0.0181; card 1's r half-widths median 0.0242, max 0.0376; D ratio a3/c1 median 1.0312 (0.9970-1.0657, every row incl. the random kind)
   X4 median 1.0238, IQR [1.0224080652550676, 1.0279332223628452], per type {'fp32': 1.023103022004492, 'fp16': 1.0243261853360854, 'int8': 1.0331506768657397}
   X1 [('fp32', 1.0), ('fp16', 1.0), ('int8', 0.9835)]; X5 33 of 33
   at the arms: {'auto': {'E131-X1': 'PASS', 'E131-X4': 'PASS', 'E131-X5': 'PASS'}, 'dips_kept': {'E131-X1': 'PASS', 'E131-X4': 'PASS', 'E131-X5': 'PASS'}, 'leak0.1994': {'E131-X1': 'PASS', 'E131-X4': 'PASS', 'E131-X5': 'PASS'}, 'leak0.3803': {'E131-X1': 'PASS', 'E131-X4': 'PASS', 'E131-X5': 'PASS'}, 'leak0': {'E131-X1': 'NOT SCORED', 'E131-X4': 'NOT SCORED', 'E131-X5': 'NOT SCORED'}, 'leak0.545': {'E131-X1': 'PASS', 'E131-X4': 'FAIL', 'E131-X5': 'PASS'}}
   arm auto: leak 0.4008; cross {'E131-X1': 'PASS', 'E131-X4': 'PASS', 'E131-X5': 'PASS'}
   arm leak0.545: leak 0.5450; cross {'E131-X1': 'PASS', 'E131-X4': 'FAIL', 'E131-X5': 'PASS'}
   arm leak0.1994: leak 0.1994; cross {'E131-X1': 'PASS', 'E131-X4': 'PASS', 'E131-X5': 'PASS'}

== D. Beside E112(b)'s two kept passes on this card (reported)
   fp32: r(E131) - r(E112b): median -0.0014, max |diff| 0.0091 (11 tiles); D(E131 auto arm) - D(E112b): median +0.016 W, range -0.132 to +0.101 W (12 rows)
   fp16: r(E131) - r(E112b): median +0.0021, max |diff| 0.0093 (10 tiles); D(E131 auto arm) - D(E112b): median +0.065 W, range -0.078 to +0.197 W (11 rows)
   int8: r(E131) - r(E112b): median -0.0036, max |diff| 0.0337 (12 tiles); D(E131 auto arm) - D(E112b): median -0.017 W, range -0.182 to +0.138 W (13 rows)

== E. The slope
   fp32.randn: D at 0.2414 23.963 W, at auto (0.4008) 23.451 W, difference +0.512 W
   fp16.randn: D at 0.2414 21.467 W, at auto (0.4008) 21.047 W, difference +0.420 W
   int8.full: D at 0.2414 6.891 W, at auto (0.4008) 6.701 W, difference +0.189 W
   fp32.r2_vgg16_fc2: D at 0.2414 7.694 W, at auto (0.4008) 7.542 W, difference +0.152 W
   int8.r2_vgg16_fc2: D at 0.2414 3.896 W, at auto (0.4008) 3.710 W, difference +0.186 W
   auto slopes on card 1: E131 0.4008, E112(b) 0.4172 W/C; E95 dips removed on aifoundry3 0.2989
   the leakage-0 arm keeps [13110, 13112]; set aside [{'pass': 13111, 'why': ['int8.zeros departs -0.253 W from its straight line']}, {'pass': 13113, 'why': ['fp16.zeros departs -0.403 W from its straight line']}]

== F. The session tie to E82's card-1 cells (reported)
   fp32.randn: 23.963 ± 0.131 W against 23.987: -0.024 W (band ±0.5) PASS
   fp16.randn: 21.467 ± 0.118 W against 21.442: +0.025 W (band ±0.5) PASS
   anchor_pi: 8.154 ± 0.080 W against 8.095: +0.059 W (band ±0.5) PASS
   int8.full: 6.891 ± 0.130 W against 6.869: +0.022 W (band ±0.25) PASS

== G. Checks: idle consistency 0.082 W; rail tau 1.0 s; duty 0.9957-0.9964; carry-over 0.0046 W/W, SE 0.0007, n 208
