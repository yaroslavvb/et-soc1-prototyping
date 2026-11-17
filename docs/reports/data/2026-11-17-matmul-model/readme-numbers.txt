  1 PASS | A *shire* is a group of 32 minions | found | docs/et-soc1-notes.md @ 51e2da3f5
  2 PASS | it runs two *harts* | found | docs/et-soc1-notes.md @ 51e2da3f5 | two harts a minion: 64 harts / 32 minions
  3 PASS | the band of footprints just past the 32 MB L3 (33-70 MB) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
  4 PASS | 192 cache lines | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
  5 PASS | on 265 blind GEMM points | 265 | numbers.json: timing.sim_ratio.all.n
  6 PASS | the card took 8 to 34 times the simulator's step count (median 24; | 8, 34, 24 | numbers.json: timing.sim_ratio.all.min, timing.sim_ratio.all.max, timing.sim_ratio.all.median
  7 PASS | the counts come from a law fitted to 11 simulator runs | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
  8 PASS | (12 micro-loop configurations, 18 registered readings within 2 cycles, one card) | 12, 18 | docs/reports/data/2026-11-02-e129-int8-noissue/results.md, docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt, docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt (readings 18, passing within 2 cycles 18, configurations 12)
  9 PASS | filled 17 to 99% of each op (median 39%) | 17, 99, 39 | numbers.json: timing.tensor_share.all.min, timing.tensor_share.all.max, timing.tensor_share.all.median
 10 PASS | **4.7 to 9.5%** rms in cycles | 4.7, 9.5 | numbers.json: blind_summary.mm1_cyc_min, blind_summary.mm1_cyc_max
 11 PASS | **3.2 to 11.9%** in joules over idle | 3.2, 11.9 | numbers.json: blind_summary.mm1_jo3_min, blind_summary.mm1_jo3_max
 12 PASS | against **17.1 to 23.0%** | 17.1, 23.0 | numbers.json: blind_summary.F1_cyc_min, blind_summary.F1_cyc_max
 13 PASS | **18.4 to 31.0%** for F1 | 18.4, 31.0 | numbers.json: blind_summary.F1_jo3_min, blind_summary.F1_jo3_max
 14 PASS | **52.7 to 82.0%** for F2 | 52.7, 82.0 | numbers.json: blind_summary.F2_jo3_min, blind_summary.F2_jo3_max
 15 PASS | MM1's cycles error rose from 3-4% on the old kernel to 8-9% on the new one | 3-4, 8-9 | numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)
 16 PASS | The low end in cycles, 4.7%, is arm B | 4.7 | numbers.json: blind.E206B.models.v1.cyc_mean.rms_pct
 17 PASS | MM1-v2 read 5.0% and MM1-v1 5.9% | 5.0, 5.9 | numbers.json: blind.E207.models.v2.cyc_mean.rms_pct, blind.E207.models.v1.cyc_mean.rms_pct
 18 PASS | to **1.9%** of the data-dependent power | 1.9 | numbers.json: switch.routes.R1.rms_over_D_pct
 19 PASS | against 16 to 47% for the bit-flip prices and 20% for the nearest measured kind | 16, 47, 20 | numbers.json: switch.routes.R3L.rms_over_D_pct, switch.routes.R3.rms_over_D_pct, switch.routes.R4.rms_over_D_pct
 20 PASS | to about **0.4%** in cycles | 0.4 | numbers.json: repeat.E208.cyc_op_mean.rms_pct
 21 PASS | **1.2%** in joules over idle | 1.2 | numbers.json: repeat.E208.J_op.rms_pct
 22 PASS | at or before 09:48:24 PST | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 23 PASS | I want you to focus on the matte mold most of all, | found | tools/matmul/mm1/v0/README.md @ 2d1413f56 | the quote, whole, as committed
 24 PASS | The ET-SoC-1 has 1,088 minions in 34 shires (32 compute shires, a master and a spare) | found | docs/et-soc1-notes.md @ 51e2da3f5
 25 PASS | the lab's kernels use 1,024 of them, in 32 shires of 32 | found | docs/findings/05-claims.md @ d5beec9bf
 26 PASS | the chip shares a 32 MB L3 | found | docs/et-soc1-notes.md @ 51e2da3f5
 27 PASS | run at a fixed 600 MHz (aifoundry3 card 0 | found | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/README.md @ d7e4f35e8
 28 PASS | aifoundry1 card 1 in the tests below | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md @ 79340bfac
 29 PASS | about 800 MHz in E208's GEMMs | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 30 PASS | M = 1,024·MB, N = 512·NB, K = 512·KB·w (w = 1, 2, 4 for fp32, fp16, int8) | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 31 PASS | each minion does 64·MB·NB·KB | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 32 PASS | 4,096 multiply-adds in fp32, 8,192 in fp16 and 16,384 in int8 | 4,096, 8,192, 16,384 | tools/claims-v3/e206/points-e206.json
 33 PASS | asks for 192 cache lines, 64 of A and 128 of B | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 34 PASS | x50 = 39.7 MB and s = 4.53 MB | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 35 PASS | 527.48 cycles + 0.0176 µs in fp32 and fp16, and 283.03 cycles + 0.0146 µs in int8 | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 36 PASS | 529 and 270 cycles | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 37 PASS | scale with (V / 0.517 V)² | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 38 PASS | 58.9, 245.1 and 794.7 pJ | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 39 PASS | 501.2, 1,150.2 and 1,298.6 pJ | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 40 PASS | "one transistor gate, one fin, charged or discharged by a net transition" | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 41 PASS | 6,144 × 3,072 × 3,072, fp32, random data, all 32 shires | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 42 PASS | | 0 / 115.98 / 76.02 | | 0, 115.98, 76.02 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: lines_L2, lines_L3, lines_F)
 43 PASS | | 1,173.8 | | 1,173.8 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: cycles_per_op_mean)
 44 PASS | | 1,161.2 | | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 45 PASS | | 27.34 | | 27.34 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: seconds_per_gemm)
 46 PASS | 26.78 / 26.77 (two runs) | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 47 PASS | | 528.7 | | 528.7 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: J_over_idle_per_gemm)
 48 PASS | 519.8 (mean of 529.8 and 509.8) | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 49 PASS | counted 4.1 to 6.2 × 10^15 | 4.1, 6.2 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: switches_counted_lo, switches_counted_hi)
 50 PASS | estimated 3.4 / 8.5 / 14.9 × 10^15 | 3.4, 8.5, 14.9 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: switches_estimated_lo, switches_estimated_central, switches_estimated_hi)
 51 PASS | own two runs (529.8 against 509.8) | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 52 PASS | fitted on 769 GEMM time points | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 53 PASS | 682 energy points | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 54 PASS | from 11 earlier experiments | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 55 PASS | (888 time and 791 energy points) | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 56 PASS | (1,072 time and 964 energy points) | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 57 PASS | cycles 4.70% for MM1-v1 against 5.91% for MM1-v0's form refitted | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 58 PASS | 5.41% for MM1-v2 against 5.70% for MM1-v1's form refitted | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 59 PASS | (769, 888 and 1,072 points) | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179 | 769 and 888 by the checks above
 60 PASS | so MM1-v0's 5.54% | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 61 PASS | "a post hoc desk fit on 11 sys_emu runs of rgm136 ... the simulator has no timing, its steps are instructions" | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
 62 PASS | 46.625 steps an op + 24.25 a C-tile row | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
 63 PASS | with + 92 a launch in MM1's column | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 64 PASS | about 5 steps for each stack load | found | tools/claims-v3/e211/KIT.md @ 2b7f261f8
 65 PASS | rgm136's loop runs 36 instructions an op and 47.742 steps | found | tools/claims-v3/e211/KIT.md @ 2b7f261f8
 66 PASS | **265 points** of E206's two arms and E207 | 265 | numbers.json: timing.sim_ratio.all.n
 67 PASS | (161 distinct configurations | 161 | numbers.json: timing.sim_ratio.distinct_configurations
 68 PASS | **8.2 to 33.9 times** | 8.2, 33.9 | numbers.json: timing.sim_ratio.all.min, timing.sim_ratio.all.max
 69 PASS | **median 24.0** | 24.0 | numbers.json: timing.sim_ratio.all.median
 70 PASS | (quartiles 19.4 and 29.4 | 19.4, 29.4 | numbers.json: timing.sim_ratio.all.q1, timing.sim_ratio.all.q3
 71 PASS | all 32 shires took 537.98 cycles an op in fp32 and 388.02 in int8 | 537.98, 388.02 | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/scores-e206-A.json
 72 PASS | rgm211's compiled loop takes 32.762 steps an op against rgm136's 47.742 (31 instructions against 36) | found | tools/claims-v3/e211/KIT.md @ 2b7f261f8
 73 PASS | where only the compiled code differs, ran 3-6% fast | 3-6 | tools/matmul/mm1/v2/score-e211.json controls (x01, x02 in ln)
 74 PASS | plus one constant of 7.75 cycles set on the card in E109 | found | docs/reports/data/2026-11-03-e155-int8-floor-rows/corrections-numbers.txt @ 93637c7f9
 75 PASS | **18 of 18 registered readings within 2 cycles** | 18, 18 | docs/reports/data/2026-11-02-e129-int8-noissue/results.md, docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt, docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt (readings 18, passing within 2 cycles 18, configurations 12)
 76 PASS | all with zeros data on aifoundry1 card 1 | found | tools/claims-v3/e129/E129.md @ 167e24cc0
 77 PASS | 12 micro-loop configurations, all with zeros data | 12 | docs/reports/data/2026-11-02-e129-int8-noissue/results.md, docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt, docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt (readings 18, passing within 2 cycles 18, configurations 12)
 78 PASS | within 2 cycles | found | tools/claims-v3/e129/E129.md @ 167e24cc0
 79 PASS | 544.0 forecast against 544.001 measured in fp32 | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 80 PASS | 318.0 against 318.001 in int8 | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 81 PASS | 62.0 against 62.0 for an op with one row of A | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 82 PASS | 527.48 cycles + 0.0176 µs is 538 cycles in fp32 at 600 MHz | 538 | numbers.json: timing.floor_at_600_fp32_e119
 83 PASS | the card measured 537.98 at `gemmL1x1x1` | 537.98 | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/scores-e206-A.json
 84 PASS | **546** (E101's resident loop, the RTL bench's reach, which E206 registered as its floor) and 544 | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
 85 PASS | and 544 (the bench's m0 loop) | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 86 PASS | **538** (E119's law with B streamed, at 600 MHz) | 538 | numbers.json: timing.floor_at_600_fp32_e119
 87 PASS | and **529**, the floor MM1 never goes under | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 88 PASS | In int8 the same roles are taken by 318, 292 and 270 | 318, 292, 270 | tools/claims-v3/e206/E206.md; tools/matmul/mm1/v0/README.md (283.03 + 0.0146 µs x 600 MHz = 291.79)
 89 PASS | filled **17 to 99%** of each op on the card | 17, 99 | numbers.json: timing.tensor_share.all.min, timing.tensor_share.all.max
 90 PASS | **median 39%**, over **285 blind points** | 39, 285 | numbers.json: timing.tensor_share.all.median, timing.tensor_share.all.n
 91 PASS | (546 or 318 cycles, the scorers' registered readings) it filled 21 to 101%, median 40%, over 265 points; 12 of | 546, 318, 21, 101, 40, 265, 12 | numbers.json timing.tensor_share_registered; tools/claims-v3/e206/E206.md
 92 PASS | Over the floor with B through the tile buffer (529 or 270 cycles) | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 93 PASS | Near 99% sit the ops whose tiles stay in the L2 | 99 | numbers.json: timing.tensor_share.all.max
 94 PASS | "gives instructions and bytes, never the level that served a line" | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 95 PASS | read joules over idle **18.4 to 31.0%** rms | 18.4, 31.0 | numbers.json: blind_summary.F1_jo3_min, blind_summary.F1_jo3_max
 96 PASS | Its miss is a scale, not a shape: about a quarter low in every family on E207 | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
 97 PASS | which lost to MM1-v1's full-chip lines on every fold | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 98 PASS | read **52.7 to 82.0%** rms | 52.7, 82.0 | numbers.json: blind_summary.F2_jo3_min, blind_summary.F2_jo3_max
 99 PASS | "+94% to +160% at the long-K points ... against -19% to -42% at one K block" | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
100 PASS | its byte convention, which counts every shire's request | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
101 PASS | the same models read 6.5 to 10.1% (F1) and 16.4 to 18.3% (F2) | 6.5, 10.1, 16.4, 18.3 | numbers.json (F1 and F2 jr_g over the tests that price it)
102 PASS | | 119 (108 never on this card, 95 never on any) | | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
103 PASS | | 113 (85 never on this card) | | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
104 PASS | | 113 (85 | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
105 PASS | | 53, 47 distinct cases (all never run on any card at both freezes) | | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
106 PASS | | 45, 41 time cases (all never on this card) | | found | tools/claims-v3/e209/E209.md @ d7b574f5f
107 PASS | | 26 (rgm211's 12 never run on any card) | | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
108 PASS | `2d1413f5` (Mon 13:35:10) | 13:35:10 | git log 2d1413f5 (the commit's own time, PST)
109 PASS | `eb2f7ac2` (Mon 16:01:50) | 16:01:50 | git log eb2f7ac2 (the commit's own time, PST)
110 PASS | `e35a06cb` (Mon 20:13:57) | 20:13:57 | git log e35a06cb (the commit's own time, PST)
111 PASS | `d3f031d1` (21:18:46) | 21:18:46 | git log d3f031d1 (the commit's own time, PST)
112 PASS | `25d2e74e` (Mon 21:14:55) | 21:14:55 | git log 25d2e74e (the commit's own time, PST)
113 PASS | `4e518735` (Tue 02:06:29) | 02:06:29 | git log 4e518735 (the commit's own time, PST)
114 PASS | `3ca4b717` (Tue 01:44:45) | 01:44:45 | git log 3ca4b717 (the commit's own time, PST)
115 PASS | `1393a649` (Tue 07:59:17) | 07:59:17 | git log 1393a649 (the commit's own time, PST)
116 PASS | `89aa0c94` (Tue 08:12:53) | 08:12:53 | git log 89aa0c94 (the commit's own time, PST)
117 PASS | | Mon 16 Nov 16:53:22 | | found | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/README.md @ d7e4f35e8
118 PASS | | Tue 17 Nov 00:13:26 | | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md @ 79340bfac
119 PASS | | Tue 17 Nov 07:06:44 | | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
120 PASS | | Tue 17 Nov 10:30:44 | | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
121 PASS | | Tue 17 Nov 13:21:20 | | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
122 PASS | ROW E206 arm A / MM1-v0 | README ['9.5 (-2.8)', '9.0 (-2.6)', '8.4 (-5.6)', '9.2 (-6.0)', '2.6 (-1.7)'] | numbers.json ['9.5 (-2.8)', '9.0 (-2.6)', '8.4 (-5.6)', '9.2 (-6.0)', '2.6 (-1.7)'] | committed table: none (desk) | numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)
123 PASS | ROW E206 arm A / F1 | README ['18.7 (+10.1)', '16.0 (+6.5)', '21.6 (-17.3)', '19.4 (-12.0)', '7.8 (-6.4)'] | numbers.json ['18.7 (+10.1)', '16.0 (+6.5)', '21.6 (-17.3)', '19.4 (-12.0)', '7.8 (-6.4)'] | committed table: none (desk) | numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)
124 PASS | ROW E206 arm A / F2 | README ['-', '-', '82.0 (+35.2)', '82.0 (+35.2)', '18.3 (+7.5)'] | numbers.json ['-', '-', '82.0 (+35.2)', '82.0 (+35.2)', '18.3 (+7.5)'] | committed table: none (desk) | numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)
125 PASS | ROW E206 arm B / MM1-v0 | README ['9.8 (-2.9)', '9.2 (-2.7)', '14.1 (+6.1)', '13.9 (+5.2)', '2.4 (+0.8)'] | numbers.json ['9.8 (-2.9)', '9.2 (-2.7)', '14.1 (+6.1)', '13.9 (+5.2)', '2.4 (+0.8)'] | committed {'cyc_mean': '9.8 (-2.9)', 't': '9.2 (-2.7)', 'jr_g': '2.4 (+0.8)'} (agree) | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
126 PASS | ROW E206 arm B / MM1-v1 | README ['4.7 (-1.6)', '4.6 (-0.8)', '11.9 (+5.4)', '12.0 (+5.2)', '2.1 (+0.7)'] | numbers.json ['4.7 (-1.6)', '4.6 (-0.8)', '11.9 (+5.4)', '12.0 (+5.2)', '2.1 (+0.7)'] | committed {'cyc_mean': '4.7 (-1.6)', 't': '4.6 (-0.8)', 'jr_g': '2.1 (+0.7)'} (agree) | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
127 PASS | ROW E206 arm B / F1 | README ['19.2 (+10.7)', '16.4 (+6.8)', '21.7 (-17.3)', '19.2 (-11.7)', '6.5 (-5.3)'] | numbers.json ['19.2 (+10.7)', '16.4 (+6.8)', '21.7 (-17.3)', '19.2 (-11.7)', '6.5 (-5.3)'] | committed {'cyc_mean': '19.2 (+10.7)', 't': '16.4 (+6.8)', 'jr_g': '6.5 (-5.3)'} | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
128 PASS | ROW E206 arm B / F2 | README ['-', '-', '79.2 (+37.1)', '78.6 (+36.4)', '16.4 (+7.6)'] | numbers.json ['-', '-', '79.2 (+37.1)', '78.6 (+36.4)', '16.4 (+7.6)'] | committed {'cyc_mean': '-', 't': '-', 'jr_g': '16.4 (+7.6)'} (agree) | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
129 PASS | ROW E207 / MM1-v1 | README ['5.9 (-2.4)', '5.7 (-2.6)', '5.4 (-2.1)', '5.8 (-2.4)', '2.1 (-0.7)'] | numbers.json ['5.9 (-2.4)', '5.7 (-2.6)', '5.4 (-2.1)', '5.8 (-2.4)', '2.1 (-0.7)'] | committed {'cyc_mean': ('5.93', '-2.37'), 't': ('5.66', '-2.62'), 'jo_g3': ('5.42', '-2.11'),  | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
130 PASS | ROW E207 / MM1-v2 | README ['5.0 (-0.9)', '4.8 (-1.1)', '4.8 (-0.7)', '5.2 (-0.9)', '1.9 (-0.2)'] | numbers.json ['5.0 (-0.9)', '4.8 (-1.1)', '4.8 (-0.7)', '5.2 (-0.9)', '1.9 (-0.2)'] | committed {'cyc_mean': ('5.01', '-0.86'), 't': ('4.81', '-1.12'), 'jo_g3': ('4.82', '-0.71'),  | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
131 PASS | ROW E207 / F1 | README ['21.1 (+18.5)', '18.0 (+13.9)', '25.3 (-24.4)', '16.4 (-13.8)', '9.2 (-8.6)'] | numbers.json ['21.1 (+18.5)', '18.0 (+13.9)', '25.3 (-24.4)', '16.4 (-13.8)', '9.2 (-8.6)'] | committed {'cyc_mean': ('21.10', '+18.51'), 't': ('17.97', '+13.89'), 'jo_g3': | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
132 PASS | ROW E207 / F2 | README ['-', '18.0 (+13.9)', '52.7 (+25.8)', '52.7 (+25.7)', '17.5 (+8.4)'] | numbers.json ['-', '18.0 (+13.9)', '52.7 (+25.8)', '52.7 (+25.7)', '17.5 (+8.4)'] | committed {'cyc_mean': '-', 't': ('17.97', '+13.89'), 'jo_g3': ('52.74', '+25.84'), 'jo_f3': ('52. | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
133 PASS | ROW E209 / MM1-v1 | README ['10.9 (-5.6)', '8.6 (-4.3)', '5.7 (+2.5)', '7.4 (-0.6)', '2.7 (+1.0)'] | numbers.json ['10.9 (-5.6)', '8.6 (-4.3)', '5.7 (+2.5)', '7.4 (-0.6)', '2.7 (+1.0)'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
134 PASS | ROW E209 / MM1-v2 | README ['7.6 (-3.7)', '6.8 (-2.6)', '5.5 (+2.6)', '6.9 (+1.0)', '2.8 (+1.3)'] | numbers.json ['7.6 (-3.7)', '6.8 (-2.6)', '5.5 (+2.6)', '6.9 (+1.0)', '2.8 (+1.3)'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
135 PASS | ROW E209 / F1@800 | README ['23.0 (+16.6)', '19.6 (+11.8)', '31.0 (-14.6)', '32.0 (-4.4)', '10.1 (-5.8)'] | numbers.json ['23.0 (+16.6)', '19.6 (+11.8)', '31.0 (-14.6)', '32.0 (-4.4)', '10.1 (-5.8)'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
136 PASS | ROW E209 / F2@800 | README ['-', '-', '-', '43.7 (-22.5)', '-'] | numbers.json ['-', '-', '-', '43.7 (-22.5)', '-'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
137 PASS | ROW E211, rgm211's 12 points / MM1-v1 | README ['8.2 (+2.5)', '8.0 (+2.5)', '3.2 (-0.5)', '3.4 (-0.3)', '1.6 (-0.3)'] | numbers.json ['8.2 (+2.5)', '8.0 (+2.5)', '3.2 (-0.5)', '3.4 (-0.3)', '1.6 (-0.3)'] | committed {'cyc_mean': '8.2 (+2.5)', 't': '8.0 (+2.5)', 'jo_g3': '3.2 (-0.5)', 'jo_f3': '3.4 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
138 PASS | ROW E211, rgm211's 12 points / MM1-v2 | README ['8.9 (+4.0)', '8.8 (+4.0)', '3.2 (+0.6)', '3.6 (+1.0)', '1.5 (+0.2)'] | numbers.json ['8.9 (+4.0)', '8.8 (+4.0)', '3.2 (+0.6)', '3.6 (+1.0)', '1.5 (+0.2)'] | committed {'cyc_mean': '8.9 (+4.0)', 't': '8.8 (+4.0)', 'jo_g3': '3.2 (+0.6)', 'jo_f3': '3.6 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
139 PASS | ROW E211, rgm211's 12 points / F1 | README ['17.1 (+10.1)', '14.4 (+7.8)', '18.4 (-16.2)', '11.2 (-10.7)', '8.4 (-7.1)'] | numbers.json ['17.1 (+10.1)', '14.4 (+7.8)', '18.4 (-16.2)', '11.2 (-10.7)', '8.4 (-7.1)'] | committed {'cyc_mean': '17.1 (+10.1)', 't': '14.4 (+7.8)', 'jo_g3': '18.4 (-16.2 | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
140 PASS | ROW E211, rgm211's 12 points / F2 | README ['-', '-', '-', '30.8 (+21.6)', '-'] | numbers.json ['-', '-', '-', '30.8 (+21.6)', '-'] | committed {'cyc_mean': '-', 't': '-', 'jo_g3': '-', 'jo_f3': '30.8 (+21.6)', 'jr_g': '-'} (agree) | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
141 PASS | ROW E211, rgm211's 12 points / NC (the chip-lines null) | README ['24.7 (+18.2)', '23.4 (+16.0)', '-', '-', '-'] | numbers.json ['24.7 (+18.2)', '23.4 (+16.0)', '-', '-', '-'] | committed {'cyc_mean': '24.7 (+18.2)', 't': '23.4 (+16.0)', 'jo_g3': '-', 'jo_f3': '-', 'jr_g': '-'} (agree) | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
142 PASS | ROW E211, the 12 rgm136 twins / MM1-v1 | README ['3.5 (-0.0)', '3.7 (+0.8)', '2.5 (-0.1)', '2.7 (+0.0)', '1.2 (-0.1)'] | numbers.json ['3.5 (-0.0)', '3.7 (+0.8)', '2.5 (-0.1)', '2.7 (+0.0)', '1.2 (-0.1)'] | committed {'cyc_mean': '3.5 (-0.0)', 't': '3.7 (+0.8)', 'jo_g3': '2.5 (-0.1)', 'jo_f3': '2.7 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
143 PASS | ROW E211, the 12 rgm136 twins / MM1-v2 | README ['2.7 (+0.3)', '2.9 (+1.2)', '2.7 (+1.1)', '2.9 (+1.3)', '1.2 (+0.4)'] | numbers.json ['2.7 (+0.3)', '2.9 (+1.2)', '2.7 (+1.1)', '2.9 (+1.3)', '1.2 (+0.4)'] | committed {'cyc_mean': '2.7 (+0.3)', 't': '2.9 (+1.2)', 'jo_g3': '2.7 (+1.1)', 'jo_f3': '2.9 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
144 PASS | | the same schedule five hours apart (E208, aifoundry2 card 0) | 0.41 | 0.38 | 1.16 | | 0.41, 0.38, 1.16 | numbers.json: repeat.E208.cyc_op_mean.rms_pct, repeat.E208.T_op_us.rms_pct, repeat.E208.J_op.rms_pct
145 PASS | | the two runs of each point in one day (E206's arms, E207) | 0.04 to 0.19 | 0.04 to 0.16 | 1.0 to 1.8 | | 0.04, 0.19, 0.04, 0.16, 1.0, 1.8 | numbers.json repeat.within_day
146 PASS | time at every point (119 and 113) | 119, 113 | numbers.json: blind.E206A.models.v0.cyc_mean.n, blind.E206B.models.v1.cyc_mean.n
147 PASS | (101 for MM1-v0 on arm A, 98 for both MM1 versions on arm B) | 101, 98, 98 | numbers.json: blind.E206A.models.v0.jo_g3.n, blind.E206B.models.v1.jo_g3.n, blind.E206B.models.v0.jo_g3.n
148 PASS | arm B's MM1-v1 reads 14.3% (n 105) and arm A's MM1-v0 9.8% (n 109) | 14.3, 105, 9.8, 109 | numbers.json: blind.E206B.models.v1.jo_g.rms_pct, blind.E206B.models.v1.jo_g.n, blind.E206A.models.v0.jo_g.rms_pct, blind.E206A.models.v0.jo_g.n
149 PASS | XREF: 14.30% (n 105) committed | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab | arm B's committed all-points table
150 PASS | MM1-v1 reads 0.21 W rms on arm B's 7 and MM1-v0 0.31 W on arm A's 8 | 0.21, 7, 0.31, 8 | numbers.json: blind.E206B.under_3W.v1.rms_w, blind.E206B.under_3W.v1.n, blind.E206A.under_3W.v0.rms_w, blind.E206A.under_3W.v0.n
151 PASS | (46 for MM1-v2, 50 for MM1-v1, 47 for F1, 46 for F2) | 46, 50, 47, 46 | numbers.json: blind.E207.models.v2.jo_g3.n, blind.E207.models.v1.jo_g3.n, blind.E207.models.F1.jo_g3.n, blind.E207.models.F2.jo_g3.n
152 PASS | time per case over the 47 cases | 47 | numbers.json: blind.E207.n.cases_scored
153 PASS | time per case over the 41 cases | 41 | numbers.json: blind.E209.n_cases
154 PASS | (45 for MM1-v2, 39 for MM1-v1, 42 for F1@800 and F2@800; no E209 point read under 3 W) | 45, 39, 42, 42, no | numbers.json: blind.E209.models.v2.jo_g3.n, blind.E209.models.v1.jo_g3.n, blind.E209.models.F1.jo_g3.n, blind.E209.models.F2.jo_f3.n, blind.E209.n_points_under_3W_measured
155 PASS | on the scorer's own footing, the rms of ln, it reads 82.2% | 82.2 | numbers.json: blind.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct
156 PASS | every point above 3 W | 3 | numbers.json: blind.E211.W_min_measured
157 PASS | 24 of its 119 points are bridges from experiments in MM1-v0's own fit | 24, 119 | numbers.json: blind.E206A.subsets.ran_before_any_card.n, blind.E206A.n_points
158 PASS | (11 of them on aifoundry3 itself) | 11 | numbers.json (119 - the 108 never on aifoundry3)
159 PASS | On the 95 points never run on any card MM1-v0 read **10.2% (-2.9)** in cycles and **10.4%** in joules over idl | 95, 10.2, -2.9, 10.4, 8.8 | numbers.json: blind.E206A.subsets.never_any_card.n, blind.E206A.subsets.never_any_card.models.v0.cyc_mean.rms_pct, blind.E206A.subsets.never_any_card.models.v0.cyc_mean.bias_pct, blind.E206A.subsets.never_any_card.models.v0.jo_g.rms_pct, blind.E206A.subsets.never_any_card.models.v0.jo_g3.rms_pct
160 PASS | on the 24 bridges, 6.2% and 7.1% | 24, 6.2, 7.1 | numbers.json: blind.E206A.subsets.ran_before_any_card.n, blind.E206A.subsets.ran_before_any_card.models.v0.cyc_mean.rms_pct, blind.E206A.subsets.ran_before_any_card.models.v0.jo_g.rms_pct
161 PASS | On the 85 points never run on card 1, MM1-v1 read 4.7% in cycles and 15.5% in joules over idle (n 77) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
162 PASS | MM1-v0 already carried an awake power of 3.660 W for it | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
163 PASS | its 53 points never ran on any card before MM1-v1 and MM1-v2 were frozen | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
164 PASS | at 05:30 and 06:16 PST | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
165 PASS | at 45 points never run on that card | found | tools/claims-v3/e209/E209.md @ d7b574f5f
166 PASS | (4 of them in both models' fit, 3 run in E207 before the freeze, 5 never run) | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
167 PASS | its 12 rgm136 twins | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
168 PASS | at least 90% of its cases or points sit within twice MM1-v1's larger held-out error | found | tools/claims-v3/e207/E207.md @ 3649245b7
169 PASS | 13 to 16% per case in cycles and seconds | found | tools/claims-v3/e207/E207.md @ 3649245b7 | T1 and T3 at 13% (E207.md section 7 table)
170 PASS | 15 to 16% per point in joules over idle | found | tools/claims-v3/e207/E207.md @ 3649245b7
171 PASS | 5% and 13% with the card at rest | found | tools/claims-v3/e207/E207.md @ 3649245b7 | the E3 and E4 rows of E207.md section 7
172 PASS | T1 45/47, T2 44/47, T3 45/47 | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
173 PASS | E1 50/53, E2 48/53, E3 51/53, E4 50/53 | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
174 PASS | 39 to 8 (exact sign test p 5.5e-06 | 5.539621596994948e-06 -> 5.5e-06 | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
175 PASS | H2 on the counter's mean 45 to 2 | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
176 PASS | H3 and H4 against F2 on joules over idle 47 to 2 each | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
177 PASS | (7/0/0 against F1, 8/0/0 against F2) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
178 PASS | closer at 24 cases against 18, p 0.44 | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
179 PASS | (30 against 11, p 0.0043) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
180 PASS | but the family-level check does not confirm it (TOO FEW; NOT DECIDED) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
181 PASS | 62 of 62 runs in 26.16 card-minutes | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
182 PASS | first card command 10:30:44 PST, 8 h 46 min after | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
183 PASS | 29 shapes, three formats, four data kinds, five shire counts | found | tools/claims-v3/e209/E209.md @ d7b574f5f
184 PASS | 15,675 of 15,675 samples carry it (600 MHz 11,545, 700 MHz 131, 800 MHz 3,999) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
185 PASS | it stepped inside every device process | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
186 PASS | 19% in cycles and seconds, 14% and 15% in joules over idle, 5% and 13% with the card at rest | found | tools/claims-v3/e209/E209.md @ d7b574f5f
187 PASS | pass when at least 90% of cases or points sit within twice MM1-v2's larger held-out error | found | tools/claims-v3/e209/E209.md @ d7b574f5f
188 PASS | T1m, T1c, T2m, T2c, T3m and T3c PASS at 39 of 41 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
189 PASS | E1 PASS 45/45, E2m 42/45, E2c 41/44, E3 43/45, E4m 42/45, E4c 41/44 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
190 PASS | K1 (the clock forecast) PASS 44/45 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
191 PASS | XREF: E209 rules in the scorer's output | all present | scored-e209.json rules and head_to_head | every count above equals scored-e209.json's rules
192 PASS | wall cycles **7.2%**, MM1-v1 9.3%, F1@800 18.1% | 7.2, 9.3, 18.1 | numbers.json: blind.E209.registered_summaries_ln.v2_m cycles wall.rms_ln_pct, blind.E209.registered_summaries_ln.v1_m cycles wall.rms_ln_pct, blind.E209.registered_summaries_ln.F1 cycles wall.rms_ln_pct
193 PASS | seconds **5.4%** (45 points), MM1-v1 5.6% (39) | 5.4, 45, 5.6, 39 | numbers.json: blind.E209.registered_summaries_ln.v2 J over idle given t.rms_ln_pct, blind.E209.registered_summaries_ln.v2 J over idle given t.n, blind.E209.registered_summaries_ln.v1 J over idle given t.rms_ln_pct, blind.E209.registered_summaries_ln.v1 J over idle given t.n
194 PASS | F2@800 with its seconds 82.2% | 82.2 | numbers.json: blind.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct
195 PASS | (+0.0158, 95% [+0.0037, +0.0293] in ln) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
196 PASS | the sign test reads 17 against 11 (p 0.345: NOT DECIDED) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
197 PASS | the families split 2 against 2 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
198 PASS | The subsets carry 67% of the summed difference | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
199 PASS | (H5, 38 against 3, p 1.05e-08) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
200 PASS | (H6, 35 against 5, p 1.38e-06) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
201 PASS | (e39) ran 24% more cycles than MM1-v2 forecast | 23.96 -> 24 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
202 PASS | `gemmL3x1x5` fp32 (e15) 19% | 19.34 -> 19 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
203 PASS | failed T2's 19% band by 0.03 points | 19, 0.03 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/posthoc-note15-e209.json (T2m: e42 0.19034 against the band 0.19)
204 PASS | The stride step at NB 8 measured 1.297 against MM1-v2's 1.187 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
205 PASS | int8 at one K block (e07) ran 1.158 times MM1-v2's wall cycles | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
206 PASS | real int8 tiles saved 9.0% of the joules against MM1-v2's 2.7% | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
207 PASS | 38 of 38 runs and the smoke in 17.99 card-minutes | found | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/README.md @ 38aaf004e
208 PASS | (13%, 16% and 13% in cycles and seconds; 15%, 16%, 5% and 13% in joules), PASS at 90% of rgm211's 12 points | found | tools/claims-v3/e211/E211.md @ 1393a6493
209 PASS | **T1 11/12, T2 12/12, T3 11/12, E1 12/12, E2 12/12, E3 11/12, E4 12/12: PASS** | found | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt @ 8f44b3800 | E211's registered scorer output, committed beside its data
210 PASS | ran 2.9% and 5.8% fewer wall cycles on rgm211 | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
211 PASS | (tolerance 0.01 in ln) | found | tools/claims-v3/e211/E211.md @ 1393a6493
212 PASS | (the two controls differ by 0.031 in ln) | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
213 PASS | W1, the ratio rule, reads FAIL 5/10 | found | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt @ 8f44b3800 | E211's registered scorer output, committed beside its data
214 PASS | MM1 BETTER (10/1/1, p 0.0117) | 0.01171875 -> 0.0117 | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt @ 8f44b3800 | E211's registered scorer output, committed beside its data
215 PASS | (frozen 5 h 8 min before the first card command; | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
216 PASS | its wall cycles read **8.9%** rms (+4.0), MM1-v1 8.1%, F1 14.5%, NC 23.5% | 8.9, 4.0, 8.1, 14.5, 23.5 | numbers.json: blind.E211.sets.rgm211_12.v2.cyc_wall.rms_pct, blind.E211.sets.rgm211_12.v2.cyc_wall.bias_pct, blind.E211.sets.rgm211_12.v1.cyc_wall.rms_pct, blind.E211.sets.rgm211_12.F1.cyc_wall.rms_pct, blind.E211.sets.rgm211_12.NC.cyc_wall.rms_pct
217 PASS | on the 12 rgm136 twins MM1-v2 read 2.9% and MM1-v1 3.7% | 2.9, 3.7 | numbers.json: blind.E211.sets.twins_12.v2.cyc_wall.rms_pct, blind.E211.sets.twins_12.v1.cyc_wall.rms_pct
218 PASS | (3.2% for both versions; F1 18.4%) | 3.2, 3.2, 18.4 | numbers.json: blind.E211.sets.rgm211_12.v2.jo_g3.rms_pct, blind.E211.sets.rgm211_12.v1.jo_g3.rms_pct, blind.E211.sets.rgm211_12.F1.jo_g3.rms_pct
219 PASS | The ratio rgm211 / rgm136 over 10 pairs, rms of ln: MM1-v2 0.074, MM1-v1 0.065, F1 0.128, NC 0.126, N0 (no wal | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
220 PASS | but its cycles error rose from 3-4% to 8-9% | 3-4, 8-9 | numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)
221 PASS | MM1-v0 closer than F1 at **89 of 119** points in cycles | 89, 119 | numbers.json: blind.E206A.h2h.v0<F1:cyc_mean.closer, blind.E206A.h2h.v0<F1:cyc_mean.n
222 PASS | **96 of 109** in joules over idle; closer than F2 at **104 of 109** | 96, 109, 104, 109 | numbers.json: blind.E206A.h2h.v0<F1:jo_g.closer, blind.E206A.h2h.v0<F1:jo_g.n, blind.E206A.h2h.v0<F2:jo_g.closer, blind.E206A.h2h.v0<F2:jo_g.n
223 PASS | MM1-v1 closer than F1 at **87 of 113** in cycles and **85 of 105** in joules over idle; closer than F2 at **99 | 87, 113, 85, 105, 99, 105 | numbers.json: blind.E206B.h2h.v1<F1:cyc_mean.closer, blind.E206B.h2h.v1<F1:cyc_mean.n, blind.E206B.h2h.v1<F1:jo_g.closer, blind.E206B.h2h.v1<F1:jo_g.n, blind.E206B.h2h.v1<F2:jo_g.closer, blind.E206B.h2h.v1<F2:jo_g.n
224 PASS | XREF: 87 of 113 (committed) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab | arm B's committed head to head
225 PASS | XREF: 85 of 105 / 99 of 105 (committed) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
226 PASS | MM1-v1 was closer than MM1-v0 at 69 of 113 in cycles | 69, 113 | numbers.json: blind.E206B.h2h.v1<v0:cyc_mean.closer, blind.E206B.h2h.v1<v0:cyc_mean.n
227 PASS | The same 85-run schedule | found | docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/README.md @ 5d99fe172
228 PASS | repeated to **0.41%** rms in cycles an op | 0.41 | numbers.json: repeat.E208.cyc_op_mean.rms_pct
229 PASS | 0.38% on the slowest minion | 0.38 | numbers.json: repeat.E208.cyc_op_max.rms_pct
230 PASS | 0.38% in seconds | 0.38 | numbers.json: repeat.E208.T_op_us.rms_pct
231 PASS | **1.19%** in watts over idle | 1.19 | numbers.json: repeat.E208.dP_w.rms_pct
232 PASS | **1.16%** in joules over idle | 1.16 | numbers.json: repeat.E208.J_op.rms_pct
233 PASS | (0.72% with the die corrected to 50 C, post hoc) | 0.72 | numbers.json: repeat.E208.J_op_c50.rms_pct
234 PASS | XREF: 0.409% committed | found | docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.md @ 5d99fe172 | E208's committed repeat table
235 PASS | XREF: 1.163% committed | found | docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.md @ 5d99fe172
236 PASS | differed by 0.04 to 0.19% rms in cycles and 1.0 to 1.8% in joules over idle | 0.04, 0.19, 1.0, 1.8 | numbers.json repeat.within_day
237 PASS | MM1's blind errors are 3 to 23 times the session repeat | 3, 23 | numbers.json: blind_summary.over_repeat_min, blind_summary.over_repeat_max
238 PASS | rgm136 unchanged, 74 arms on three cards | found | tools/claims-v3/e208/E208.md @ d005dc530
239 PASS | 221 arms and an anchor in 10 sessions | found | tools/claims-v3/e212/E212.md @ c83a29d13
240 PASS | is in progress: seven of ten sessions are committed | seven | docs/reports/data/2026-11-17-e212-mmsweep2-* (a1c0-S1, a1c0-S2, a1c1-S1, a1c1-S2, a1c1-S3, a1c1-S4, a2c0-S1)
241 PASS | XREF: every sealed sha256 in its registration | all present | tools/claims-v3/sealed-e206/e206-freeze-lines.md, tools/claims-v3/sealed-e206/e206-freeze-lines-2.md, tools/claims-v3/sealed-e207/e207-freeze-lines.md, tools/claims-v3/e208/E208.md, tools/claims-v3/sealed-e209/e209-freeze-lines.md, tools/claims-v3/sealed-e210/e210-freeze-lines.md, tools/claims-v3/sealed-e211/e211-freeze-lines.md, tools/claims-v3/e212/E212.md, docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S2/README.md | each sha256 prefix of the table found in the file that registers it
242 PASS | nine fp32 operand patterns never run in a GEMM, at two shapes | found | tools/claims-v3/e210/E210.md @ 7b59f7191
243 PASS | random minus zeros: 29.78 W and 20.53 W | found | tools/claims-v3/e210/E210.md @ 7b59f7191
244 PASS | the time equality PASS in all 20 cases | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
245 PASS | B5 (R1 within 5% of D | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b | 0.05 D = 5% of D
246 PASS | PASS 13 of 13 | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
247 PASS | the nearest measured kind (H1, 10 to 1) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
248 PASS | the raw bit-flip price (H2, 12 to 0) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
249 PASS | the bit-flip price with one scale (H3, 10 to 0) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
250 PASS | UNDECIDED (4 to 0 with 1 tie; 5 cases, too few to decide, as registered) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
251 PASS | R1's error is **0.481 W rms, 1.87% of D** | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
252 PASS | against 3.849 W (16.19%) for the scaled bit flips, 5.128 W (19.71%) for the nearest kind, 5.575 W (21.22%, 5 c | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
253 PASS | sits within 0.8% of the calibrated one | 0.8 | numbers.json switch.kappa (scores-e210-A.json)
254 PASS | (S1 1.6767 × 10^16 switches a J against 1.6733 × 10^16; S2 1.6235 against 1.6367 × 10^16) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
255 PASS | H1 is UNDECIDED (6 to 1, 1 tie) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
256 PASS | 142 of 171 runs, when the card-time rule stopped new runs at 85.01 card-minutes | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md @ 6689d68f6
257 PASS | the die gate made each run about 35 s, not the planned 26 | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
258 PASS | 9 of the 13 test cases are scored on 2 of 3 blocks | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
259 PASS | committed data put ones at about 0.31 of D where the count says about 0.05 | found | tools/claims-v3/e210/E210.md @ 7b59f7191
260 PASS | (M a multiple of 1,024, N of 512, K of a block) | found | tools/claims-v3/e209/E209.md @ d7b574f5f
261 PASS | E211 shows a recompiled kernel's cycles drift 8-9% | 8-9 | numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)
262 PASS | MM1-v2's energy reads 10.13% against 9.15% for MM1-v1's form | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
263 PASS | and MM1-v1's 14.2-42.1% | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
264 PASS | missed the int8 saving by 6 points | 6 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/posthoc-note15-e209.json (e35/e01: measured 0.910, MM1-v2 0.973)
265 PASS | On arm B's 14 all-zero points | 14 | numbers.json: blind.E206B.classes.data kind: zeros.n
266 PASS | joules over idle **27.8%** rms (**+25.7%** bias) | 27.8, 25.7 | numbers.json: blind.E206B.classes.data kind: zeros.jo_g.v1.rms_pct, blind.E206B.classes.data kind: zeros.jo_g.v1.bias_pct
267 PASS | MM1-v0 33.7% (+31.4%) | 33.7, 31.4 | numbers.json: blind.E206B.classes.data kind: zeros.jo_g.v0.rms_pct, blind.E206B.classes.data kind: zeros.jo_g.v0.bias_pct
268 PASS | where F1 read 13.5% | 13.5 | numbers.json: blind.E206B.classes.data kind: zeros.jo_g.F1.rms_pct
269 PASS | closer at 13 of the 14 | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
270 PASS | XREF: zeros committed | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab | arm B's committed class row
271 PASS | watts over idle +21.2% (42 runs | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
272 PASS | (2.406 W at 1,024 minions against MM1-v1's 3.257 W) | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
273 PASS | the subset points of 3 W and above read 7.0% for MM1-v1 | 7.0 | numbers.json: blind.E206B.classes.subset (mask < 32 shires).jo_g3.v1.rms_pct
274 PASS | the 7 under 3 W (1, 4 or 8 shires, 0.31 to 2.78 W over idle) read -0.05 to +0.39 W off, MM1-v1 high at 6 of th | 7, 1, 4, 8, 0.31, 2.78, -0.05, +0.39, 6, +0.18, +0.22 | numbers.json blind.E206B.under_3W_detail
275 PASS | +62% and +43% at the two smallest | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
276 PASS | -14.0% (mask 0x3) and -10.2% (0xfff) in wall cycles; MM1-v2's contention on the DRAM stream alone moved them t | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
277 PASS | 3x6x4 fp32 on 12 shires (0xfff) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
278 PASS | +13.3%: on that mask | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
279 PASS | faster than on 2 or on 24 shires | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
280 PASS | On E209 the one shire 0x80000000 ran 24% over MM1-v2 | 23.96 -> 24 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
281 PASS | MM1-v2 was closer than MM1-v1 at 6 of the 9 subset points | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
282 PASS | E209's step at NB 8 measured 1.297 against MM1-v2's 1.187 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
283 PASS | int8 at one K block ran 1.158 times MM1-v2's wall cycles on E209 (e07) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
284 PASS | and -14.0% on E207 (n01) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
285 PASS | -18.4% (E207's n02, int8) and -13.6% (n03, fp32) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
286 PASS | int8 inside the L3 ran 6.3 to 6.6% more cycles than fp32 | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
287 PASS | rgm211's controls ran 3-6% fast, and MM1's cycles error there was 8-9% | 3-6, 8-9 | tools/matmul/mm1/v2/score-e211.json
288 PASS | (e44, 788.9 MHz measured against 764.1 forecast) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
289 PASS | two of 55 runs whose capped state MM1-v2 read wrong | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1 | 55 - 53 = 2
290 PASS | about 16 minutes in all | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179

CHECKS: 290 run, 0 FAIL
NUMBERS OF README.md NO CHECK COVERS (208: dates, times, ids, section numbers, counts named in the text; for a reader to judge):
  line 1: 1,
  line 3: 17 2026 47
  line 8: 3.12
  line 15: 1
  line 25: 2026 11 17 1
  line 30: 1
  line 32: 2
  line 35: 3
  line 39: 4
  line 40: 3
  line 47: 5
  line 50: 6
  line 53: 6 1, 8,
  line 56: 1
  line 58: 16 2026,
  line 69: 2
  line 72: 05
  line 77: 2
  line 81: 4
  line 90: 32
  line 93: 1 1
  line 95: 1 2
  line 96: 2
  line 98: 1
  line 99: 1 1
  line 101: 2
  line 104: 2
  line 105: 3
  line 110: 4
  line 111: 5
  line 115: 7
  line 116: 5
  line 119: 0 600
  line 120: 2026 11 17
  line 131: 4
  line 133: 4 7 16 2026
  line 136: 17 2026
  line 139: 5.1
  line 140: 0
  line 141: 4
  line 143: 3
  line 145: 2 2
  line 148: 11
  line 150: 7,
  line 151: 2
  line 160: 4
  line 171: 6
  line 178: 3
  line 180: 4
  line 181: 3
  line 183: 6,
  line 184: 4.1
  line 189: 4
  line 198: 0, 600
  line 199: 1, 600
  line 200: 0, 600
  line 201: 0, 800, 800
  line 202: 0, 600
  line 204: 3 3
  line 206: 3
  line 235: 1, 7
  line 237: 3
  line 239: 3
  line 240: 3
  line 243: 800
  line 244: -100
  line 252: 1
  line 253: 1
  line 254: 2
  line 258: 1
  line 267: 7
  line 268: 06,
  line 269: 2,
  line 281: 7
  line 282: 15,
  line 287: 15
  line 289: 0,
  line 290: 800 800
  line 292: 15
  line 299: 0
  line 302: 7
  line 304: 1,
  line 305: 3
  line 308: 12
  line 310: 3
  line 312: 3
  line 324: 0
  line 326: 600
  line 327: 3
  line 341: 8
  line 351: 5
  line 353: 4 4
  line 357: 0,
  line 370: 1 4
  line 375: 1
  line 378: 6
  line 380: 5 5
  line 390: 0
  line 391: 5
  line 400: 1
  line 401: 1
  line 402: 1 1
  line 403: 1 1
  line 409: 6,
  line 416: 15
  line 420: 7
  line 429: 2026 11 16 2026 11 17
  line 430: 2026 11 17
  line 431: 15 2026 11 17
  line 432: 2026 11 17
  line 433: 2026 11 17
  line 434: 2026 11 17
  line 435: 2026 11 02 2026 11 02 2026 11 03
  line 441: 9
  line 442: 10 9,
  line 443: 2026 11 16
  line 444: 2026 11 17
  line 445: 2026 11 17
  line 446: 2026 11 17
  line 447: 1
  line 448: 2026 11 17
  line 449: 2026 11 17
  line 451: 2026 11 17
  line 452: 2026 11 17
  line 453: 2026 11 17
  line 456: 4
  line 464: 1 5
  line 468: 2026 11 17
  line 470: 2.0
interpreter: /usr/bin/python3 3.12.3
