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
 15 PASS | MM1's cycles error rose from 3-4% on the old kernel to 8-9% on the variant | 3-4, 8-9 | numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)
 16 PASS | E211's controls show the compiled code alone moves the cycles by 3-6% | 3-6 | tools/matmul/mm1/v2/score-e211.json controls (x01, x02 in ln)
 17 PASS | the registered comparison was UNDECIDED (5 cases) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
 18 PASS | for E207's four such points and passed, -6.0% to +7.1% | -6.0, +7.1 | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.json points b49-b52
 19 PASS | MM1-v2 prices no energy for a tile kind without a resident price on that card | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
 20 PASS | *Unread*: scored on data that existed before the forecast but that the model never read | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179 | the lab's own definition (MM1-v2's README)
 21 PASS | The low end in cycles, 4.7%, is arm B | 4.7 | numbers.json: blind.E206B.models.v1.cyc_mean.rms_pct
 22 PASS | MM1-v2 read 5.0% and MM1-v1 5.9% | 5.0, 5.9 | numbers.json: blind.E207.models.v2.cyc_mean.rms_pct, blind.E207.models.v1.cyc_mean.rms_pct
 23 PASS | to **1.9%** of the data-dependent power | 1.9 | numbers.json: switch.routes.R1.rms_over_D_pct
 24 PASS | against 16 to 47% for the bit-flip prices and 20% for the nearest measured kind | 16, 47, 20 | numbers.json: switch.routes.R3L.rms_over_D_pct, switch.routes.R3.rms_over_D_pct, switch.routes.R4.rms_over_D_pct
 25 PASS | to about **0.4%** in cycles | 0.4 | numbers.json: repeat.E208.cyc_op_mean.rms_pct
 26 PASS | **1.2%** in joules over idle | 1.2 | numbers.json: repeat.E208.J_op.rms_pct
 27 PASS | at or before 09:48:24 PST | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 28 PASS | I want you to focus on the matte mold most of all, | found | tools/matmul/mm1/v0/README.md @ 2d1413f56 | the quote, whole, as committed
 29 PASS | The ET-SoC-1 has 1,088 minions in 34 shires (32 compute shires, a master and a spare) | found | docs/et-soc1-notes.md @ 51e2da3f5
 30 PASS | the lab's kernels use 1,024 of them, in 32 shires of 32 | found | docs/findings/05-claims.md @ d5beec9bf
 31 PASS | the chip shares a 32 MB L3 | found | docs/et-soc1-notes.md @ 51e2da3f5
 32 PASS | run at a fixed 600 MHz (aifoundry3 card 0 | found | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/README.md @ d7e4f35e8
 33 PASS | aifoundry1 card 1 in the tests below | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md @ 79340bfac
 34 PASS | about 800 MHz in E208's GEMMs | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 35 PASS | M = 1,024·MB, N = 512·NB, K = 512·KB·w (w = 1, 2, 4 for fp32, fp16, int8) | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 36 PASS | each minion does 64·MB·NB·KB | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 37 PASS | 4,096 multiply-adds in fp32, 8,192 in fp16 and 16,384 in int8 | 4,096, 8,192, 16,384 | tools/claims-v3/e206/points-e206.json
 38 PASS | asks for 192 cache lines, 64 of A and 128 of B | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 39 PASS | x50 = 39.7 MB and s = 4.53 MB | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 40 PASS | 527.48 cycles + 0.0176 µs in fp32 and fp16, and 283.03 cycles + 0.0146 µs in int8 | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 41 PASS | 529 and 270 cycles | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 42 PASS | scale with (V / 0.517 V)² | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 43 PASS | 58.9, 245.1 and 794.7 pJ | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 44 PASS | 501.2, 1,150.2 and 1,298.6 pJ | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 45 PASS | "one transistor gate, one fin, charged or discharged by a net transition" | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 46 PASS | 6,144 × 3,072 × 3,072, fp32, random data, all 32 shires | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 47 PASS | | 0 / 115.98 / 76.02 | | 0, 115.98, 76.02 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: lines_L2, lines_L3, lines_F)
 48 PASS | | 1,173.8 | | 1,173.8 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: cycles_per_op_mean)
 49 PASS | | 1,161.2 | | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 50 PASS | | 27.34 | | 27.34 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: seconds_per_gemm)
 51 PASS | 26.78 / 26.77 (two runs) | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 52 PASS | | 528.7 | | 528.7 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: J_over_idle_per_gemm)
 53 PASS | 519.8 (mean of 529.8 and 509.8) | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 54 PASS | counted 4.1 to 6.2 × 10^15 | 4.1, 6.2 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: switches_counted_lo, switches_counted_hi)
 55 PASS | estimated 3.4 / 8.5 / 14.9 × 10^15 | 3.4, 8.5, 14.9 | tools/matmul/mm1/v2/forecasts-e207.csv @ 4e518735d (row b25: switches_estimated_lo, switches_estimated_central, switches_estimated_hi)
 56 PASS | own two runs (529.8 against 509.8) | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
 57 PASS | fitted on 769 GEMM time points | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 58 PASS | 682 energy points | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 59 PASS | from 11 earlier experiments | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 60 PASS | (888 time and 791 energy points) | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 61 PASS | (1,072 time and 964 energy points) | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 62 PASS | cycles 4.70% for MM1-v1 against 5.91% for MM1-v0's form refitted | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 63 PASS | 5.41% for MM1-v2 against 5.70% for MM1-v1's form refitted | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
 64 PASS | (769, 888 and 1,072 points) | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179 | 769 and 888 by the checks above
 65 PASS | so MM1-v0's 5.54% | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 66 PASS | "a post hoc desk fit on 11 sys_emu runs of rgm136 ... the simulator has no timing, its steps are instructions" | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
 67 PASS | 46.625 steps an op + 24.25 a C-tile row | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
 68 PASS | with + 92 a launch in MM1's column | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
 69 PASS | about 5 steps for each stack load | found | tools/claims-v3/e211/KIT.md @ 2b7f261f8
 70 PASS | rgm136's loop runs 36 instructions an op and 47.742 steps | found | tools/claims-v3/e211/KIT.md @ 2b7f261f8
 71 PASS | **265 points** of E206's two arms and E207 | 265 | numbers.json: timing.sim_ratio.all.n
 72 PASS | (161 distinct configurations | 161 | numbers.json: timing.sim_ratio.distinct_configurations
 73 PASS | **8.2 to 33.9 times** | 8.2, 33.9 | numbers.json: timing.sim_ratio.all.min, timing.sim_ratio.all.max
 74 PASS | **median 24.0** | 24.0 | numbers.json: timing.sim_ratio.all.median
 75 PASS | (quartiles 19.4 and 29.4 | 19.4, 29.4 | numbers.json: timing.sim_ratio.all.q1, timing.sim_ratio.all.q3
 76 PASS | all 32 shires took 537.98 cycles an op in fp32 and 388.02 in int8 | 537.98, 388.02 | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/scores-e206-A.json
 77 PASS | rgm211's compiled loop takes 32.762 steps an op against rgm136's 47.742 (31 instructions against 36) | found | tools/claims-v3/e211/KIT.md @ 2b7f261f8
 78 PASS | where only the compiled code differs, ran 3-6% fast | 3-6 | tools/matmul/mm1/v2/score-e211.json controls (x01, x02 in ln)
 79 PASS | plus one constant of 7.75 cycles set on the card in E109 | found | docs/reports/data/2026-11-03-e155-int8-floor-rows/corrections-numbers.txt @ 93637c7f9
 80 PASS | **18 of 18 registered readings within 2 cycles** | 18, 18 | docs/reports/data/2026-11-02-e129-int8-noissue/results.md, docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt, docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt (readings 18, passing within 2 cycles 18, configurations 12)
 81 PASS | all with zeros data on aifoundry1 card 1 | found | tools/claims-v3/e129/E129.md @ 167e24cc0
 82 PASS | 12 micro-loop configurations, all with zeros data | 12 | docs/reports/data/2026-11-02-e129-int8-noissue/results.md, docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt, docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt (readings 18, passing within 2 cycles 18, configurations 12)
 83 PASS | within 2 cycles | found | tools/claims-v3/e129/E129.md @ 167e24cc0
 84 PASS | 544.0 forecast against 544.001 measured in fp32 | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 85 PASS | 318.0 against 318.001 in int8 | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 86 PASS | 62.0 against 62.0 for an op with one row of A | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 87 PASS | 527.48 cycles + 0.0176 µs is 538 cycles in fp32 at 600 MHz | 538 | numbers.json: timing.floor_at_600_fp32_e119
 88 PASS | the card measured 537.98 at `gemmL1x1x1` | 537.98 | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/scores-e206-A.json
 89 PASS | **546** (E101's resident loop, the RTL bench's reach, which E206 registered as its floor) and 544 | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
 90 PASS | and 544 (the bench's m0 loop) | found | docs/reports/data/2026-11-02-e129-int8-noissue/results.md @ 07496b2b3
 91 PASS | **538** (E119's law with B streamed, at 600 MHz) | 538 | numbers.json: timing.floor_at_600_fp32_e119
 92 PASS | and **529**, the floor MM1 never goes under | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 93 PASS | In int8 the same roles are taken by 318, 292 and 270 | 318, 292, 270 | tools/claims-v3/e206/E206.md; tools/matmul/mm1/v0/README.md (283.03 + 0.0146 µs x 600 MHz = 291.79)
 94 PASS | filled **17 to 99%** of each op on the card | 17, 99 | numbers.json: timing.tensor_share.all.min, timing.tensor_share.all.max
 95 PASS | **median 39%**, over **285 blind points** | 39, 285 | numbers.json: timing.tensor_share.all.median, timing.tensor_share.all.n
 96 PASS | (546 or 318 cycles, the scorers' registered readings) it filled 21 to 101%, median 40%, over 265 points; 12 of | 546, 318, 21, 101, 40, 265, 12 | numbers.json timing.tensor_share_registered; tools/claims-v3/e206/E206.md
 97 PASS | Over the floor with B through the tile buffer (529 or 270 cycles) | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
 98 PASS | Near 99% sit the ops whose tiles stay in the L2 | 99 | numbers.json: timing.tensor_share.all.max
 99 PASS | "gives instructions and bytes, never the level that served a line" | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
100 PASS | read joules over idle **18.4 to 31.0%** rms | 18.4, 31.0 | numbers.json: blind_summary.F1_jo3_min, blind_summary.F1_jo3_max
101 PASS | Its miss is a scale, not a shape: about a quarter low in every family on E207 | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
102 PASS | which lost to MM1-v1's full-chip lines on every fold | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
103 PASS | read **52.7 to 82.0%** rms | 52.7, 82.0 | numbers.json: blind_summary.F2_jo3_min, blind_summary.F2_jo3_max
104 PASS | "+94% to +160% at the long-K points ... against -19% to -42% at one K block" | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
105 PASS | its byte convention, which counts every shire's request | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
106 PASS | the same models read 6.5 to 10.1% (F1) and 16.4 to 18.3% (F2) | 6.5, 10.1, 16.4, 18.3 | numbers.json (F1 and F2 jr_g over the tests that price it)
107 PASS | | 119 (108 never on this card, 95 never on any) | | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
108 PASS | | 113 (85 never on this card) | | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
109 PASS | | 113 (85 | found | tools/claims-v3/e206/E206.md @ eb2f7ac2f
110 PASS | | 53, 47 distinct cases (all never run on any card at both freezes) | | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
111 PASS | | 45, 41 time cases (all never on this card) | | found | tools/claims-v3/e209/E209.md @ d7b574f5f
112 PASS | | 26 (rgm211's 12 never run on any card) | | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
113 PASS | `2d1413f5` (Mon 13:35:10) | 13:35:10 | git log 2d1413f5 (the commit's own time, PST)
114 PASS | `eb2f7ac2` (Mon 16:01:50) | 16:01:50 | git log eb2f7ac2 (the commit's own time, PST)
115 PASS | `e35a06cb` (Mon 20:13:57) | 20:13:57 | git log e35a06cb (the commit's own time, PST)
116 PASS | `d3f031d1` (21:18:46) | 21:18:46 | git log d3f031d1 (the commit's own time, PST)
117 PASS | `25d2e74e` (Mon 21:14:55) | 21:14:55 | git log 25d2e74e (the commit's own time, PST)
118 PASS | `4e518735` (Tue 02:06:29) | 02:06:29 | git log 4e518735 (the commit's own time, PST)
119 PASS | `3ca4b717` (Tue 01:44:45) | 01:44:45 | git log 3ca4b717 (the commit's own time, PST)
120 PASS | `1393a649` (Tue 07:59:17) | 07:59:17 | git log 1393a649 (the commit's own time, PST)
121 PASS | `89aa0c94` (Tue 08:12:53) | 08:12:53 | git log 89aa0c94 (the commit's own time, PST)
122 PASS | | Mon 16 Nov 16:53:08 | | found | docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/README.md @ d7e4f35e8
123 PASS | | Tue 17 Nov 00:13:12 | | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md @ 79340bfac
124 PASS | | Tue 17 Nov 07:06:30 | | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/README.md @ 867f6a3f3
125 PASS | | Tue 17 Nov 10:30:44 | | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
126 PASS | | Tue 17 Nov 13:21:20 | | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
127 PASS | ROW E206 arm A / MM1-v0 | README ['9.5 (-2.8)', '9.0 (-2.6)', '8.4 (-5.6)', '9.2 (-6.0)', '2.6 (-1.7)'] | numbers.json ['9.5 (-2.8)', '9.0 (-2.6)', '8.4 (-5.6)', '9.2 (-6.0)', '2.6 (-1.7)'] | committed table: none (desk) | numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)
128 PASS | ROW E206 arm A / F1 | README ['18.7 (+10.1)', '16.0 (+6.5)', '21.6 (-17.3)', '19.4 (-12.0)', '7.8 (-6.4)'] | numbers.json ['18.7 (+10.1)', '16.0 (+6.5)', '21.6 (-17.3)', '19.4 (-12.0)', '7.8 (-6.4)'] | committed table: none (desk) | numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)
129 PASS | ROW E206 arm A / F2 | README ['-', '-', '82.0 (+35.2)', '82.0 (+35.2)', '18.3 (+7.5)'] | numbers.json ['-', '-', '82.0 (+35.2)', '82.0 (+35.2)', '18.3 (+7.5)'] | committed table: none (desk) | numbers.json (make_figures.py on d7e4f35e, 50476f31, 2d1413f5, eb2f7ac2)
130 PASS | ROW E206 arm B / MM1-v0 | README ['9.8 (-2.9)', '9.2 (-2.7)', '14.1 (+6.1)', '13.9 (+5.2)', '2.4 (+0.8)'] | numbers.json ['9.8 (-2.9)', '9.2 (-2.7)', '14.1 (+6.1)', '13.9 (+5.2)', '2.4 (+0.8)'] | committed {'cyc_mean': '9.8 (-2.9)', 't': '9.2 (-2.7)', 'jr_g': '2.4 (+0.8)'} (agree) | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
131 PASS | ROW E206 arm B / MM1-v1 | README ['4.7 (-1.6)', '4.6 (-0.8)', '11.9 (+5.4)', '12.0 (+5.2)', '2.1 (+0.7)'] | numbers.json ['4.7 (-1.6)', '4.6 (-0.8)', '11.9 (+5.4)', '12.0 (+5.2)', '2.1 (+0.7)'] | committed {'cyc_mean': '4.7 (-1.6)', 't': '4.6 (-0.8)', 'jr_g': '2.1 (+0.7)'} (agree) | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
132 PASS | ROW E206 arm B / F1 | README ['19.2 (+10.7)', '16.4 (+6.8)', '21.7 (-17.3)', '19.2 (-11.7)', '6.5 (-5.3)'] | numbers.json ['19.2 (+10.7)', '16.4 (+6.8)', '21.7 (-17.3)', '19.2 (-11.7)', '6.5 (-5.3)'] | committed {'cyc_mean': '19.2 (+10.7)', 't': '16.4 (+6.8)', 'jr_g': '6.5 (-5.3)'} | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
133 PASS | ROW E206 arm B / F2 | README ['-', '-', '79.2 (+37.1)', '78.6 (+36.4)', '16.4 (+7.6)'] | numbers.json ['-', '-', '79.2 (+37.1)', '78.6 (+36.4)', '16.4 (+7.6)'] | committed {'cyc_mean': '-', 't': '-', 'jr_g': '16.4 (+7.6)'} (agree) | numbers.json and docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab (time and rest cells; energy over idle at >= 3 W is desk)
134 PASS | ROW E207 / MM1-v1 | README ['5.9 (-2.4)', '5.7 (-2.6)', '5.4 (-2.1)', '5.8 (-2.4)', '2.1 (-0.7)'] | numbers.json ['5.9 (-2.4)', '5.7 (-2.6)', '5.4 (-2.1)', '5.8 (-2.4)', '2.1 (-0.7)'] | committed {'cyc_mean': ('5.93', '-2.37'), 't': ('5.66', '-2.62'), 'jo_g3': ('5.42', '-2.11'),  | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
135 PASS | ROW E207 / MM1-v2 | README ['5.0 (-0.9)', '4.8 (-1.1)', '4.8 (-0.7)', '5.2 (-0.9)', '1.9 (-0.2)'] | numbers.json ['5.0 (-0.9)', '4.8 (-1.1)', '4.8 (-0.7)', '5.2 (-0.9)', '1.9 (-0.2)'] | committed {'cyc_mean': ('5.01', '-0.86'), 't': ('4.81', '-1.12'), 'jo_g3': ('4.82', '-0.71'),  | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
136 PASS | ROW E207 / F1 | README ['21.1 (+18.5)', '18.0 (+13.9)', '25.3 (-24.4)', '16.4 (-13.8)', '9.2 (-8.6)'] | numbers.json ['21.1 (+18.5)', '18.0 (+13.9)', '25.3 (-24.4)', '16.4 (-13.8)', '9.2 (-8.6)'] | committed {'cyc_mean': ('21.10', '+18.51'), 't': ('17.97', '+13.89'), 'jo_g3': | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
137 PASS | ROW E207 / F2 | README ['-', '18.0 (+13.9)', '52.7 (+25.8)', '52.7 (+25.7)', '17.5 (+8.4)'] | numbers.json ['-', '18.0 (+13.9)', '52.7 (+25.8)', '52.7 (+25.7)', '17.5 (+8.4)'] | committed {'cyc_mean': '-', 't': ('17.97', '+13.89'), 'jo_g3': ('52.74', '+25.84'), 'jo_f3': ('52. | numbers.json and tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
138 PASS | ROW E209 / MM1-v1 | README ['10.9 (-5.6)', '8.6 (-4.3)', '5.7 (+2.5)', '7.4 (-0.6)', '2.7 (+1.0)'] | numbers.json ['10.9 (-5.6)', '8.6 (-4.3)', '5.7 (+2.5)', '7.4 (-0.6)', '2.7 (+1.0)'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
139 PASS | ROW E209 / MM1-v2 | README ['7.6 (-3.7)', '6.8 (-2.6)', '5.5 (+2.6)', '6.9 (+1.0)', '2.8 (+1.3)'] | numbers.json ['7.6 (-3.7)', '6.8 (-2.6)', '5.5 (+2.6)', '6.9 (+1.0)', '2.8 (+1.3)'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
140 PASS | ROW E209 / F1@800 | README ['23.0 (+16.6)', '19.6 (+11.8)', '31.0 (-14.6)', '32.0 (-4.4)', '10.1 (-5.8)'] | numbers.json ['23.0 (+16.6)', '19.6 (+11.8)', '31.0 (-14.6)', '32.0 (-4.4)', '10.1 (-5.8)'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
141 PASS | ROW E209 / F2@800 | README ['-', '-', '-', '43.7 (-22.5)', '-'] | numbers.json ['-', '-', '-', '43.7 (-22.5)', '-'] | committed table: none (desk) | numbers.json (make_figures.py on scored-e209.json and f1f2_e209.csv)
142 PASS | ROW E211, rgm211's 12 points / MM1-v1 | README ['8.2 (+2.5)', '8.0 (+2.5)', '3.2 (-0.5)', '3.4 (-0.3)', '1.6 (-0.3)'] | numbers.json ['8.2 (+2.5)', '8.0 (+2.5)', '3.2 (-0.5)', '3.4 (-0.3)', '1.6 (-0.3)'] | committed {'cyc_mean': '8.2 (+2.5)', 't': '8.0 (+2.5)', 'jo_g3': '3.2 (-0.5)', 'jo_f3': '3.4 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
143 PASS | ROW E211, rgm211's 12 points / MM1-v2 | README ['8.9 (+4.0)', '8.8 (+4.0)', '3.2 (+0.6)', '3.6 (+1.0)', '1.5 (+0.2)'] | numbers.json ['8.9 (+4.0)', '8.8 (+4.0)', '3.2 (+0.6)', '3.6 (+1.0)', '1.5 (+0.2)'] | committed {'cyc_mean': '8.9 (+4.0)', 't': '8.8 (+4.0)', 'jo_g3': '3.2 (+0.6)', 'jo_f3': '3.6 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
144 PASS | ROW E211, rgm211's 12 points / F1 | README ['17.1 (+10.1)', '14.4 (+7.8)', '18.4 (-16.2)', '11.2 (-10.7)', '8.4 (-7.1)'] | numbers.json ['17.1 (+10.1)', '14.4 (+7.8)', '18.4 (-16.2)', '11.2 (-10.7)', '8.4 (-7.1)'] | committed {'cyc_mean': '17.1 (+10.1)', 't': '14.4 (+7.8)', 'jo_g3': '18.4 (-16.2 | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
145 PASS | ROW E211, rgm211's 12 points / F2 | README ['-', '-', '-', '30.8 (+21.6)', '-'] | numbers.json ['-', '-', '-', '30.8 (+21.6)', '-'] | committed {'cyc_mean': '-', 't': '-', 'jo_g3': '-', 'jo_f3': '30.8 (+21.6)', 'jr_g': '-'} (agree) | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
146 PASS | ROW E211, rgm211's 12 points / NC (the chip-lines null) | README ['24.7 (+18.2)', '23.4 (+16.0)', '-', '-', '-'] | numbers.json ['24.7 (+18.2)', '23.4 (+16.0)', '-', '-', '-'] | committed {'cyc_mean': '24.7 (+18.2)', 't': '23.4 (+16.0)', 'jo_g3': '-', 'jo_f3': '-', 'jr_g': '-'} (agree) | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
147 PASS | ROW E211, the 12 rgm136 twins / MM1-v1 | README ['3.5 (-0.0)', '3.7 (+0.8)', '2.5 (-0.1)', '2.7 (+0.0)', '1.2 (-0.1)'] | numbers.json ['3.5 (-0.0)', '3.7 (+0.8)', '2.5 (-0.1)', '2.7 (+0.0)', '1.2 (-0.1)'] | committed {'cyc_mean': '3.5 (-0.0)', 't': '3.7 (+0.8)', 'jo_g3': '2.5 (-0.1)', 'jo_f3': '2.7 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
148 PASS | ROW E211, the 12 rgm136 twins / MM1-v2 | README ['2.7 (+0.3)', '2.9 (+1.2)', '2.7 (+1.1)', '2.9 (+1.3)', '1.2 (+0.4)'] | numbers.json ['2.7 (+0.3)', '2.9 (+1.2)', '2.7 (+1.1)', '2.9 (+1.3)', '1.2 (+0.4)'] | committed {'cyc_mean': '2.7 (+0.3)', 't': '2.9 (+1.2)', 'jo_g3': '2.7 (+1.1)', 'jo_f3': '2.9 ( | numbers.json and tools/matmul/mm1/v2/score-e211.md @ d38f148c5
149 PASS | | the same schedule five hours apart (E208, aifoundry2 card 0) | 0.41 | 0.38 | 1.16 | | 0.41, 0.38, 1.16 | numbers.json: repeat.E208.cyc_op_mean.rms_pct, repeat.E208.T_op_us.rms_pct, repeat.E208.J_op.rms_pct
150 PASS | | the two runs of each point in one day (E206's arms, E207) | 0.04 to 0.19 | 0.04 to 0.16 | 1.0 to 1.8 | | 0.04, 0.19, 0.04, 0.16, 1.0, 1.8 | numbers.json repeat.within_day
151 PASS | time at every point (119 and 113) | 119, 113 | numbers.json: blind.E206A.models.v0.cyc_mean.n, blind.E206B.models.v1.cyc_mean.n
152 PASS | (101 for MM1-v0 on arm A, 98 for both MM1 versions on arm B) | 101, 98, 98 | numbers.json: blind.E206A.models.v0.jo_g3.n, blind.E206B.models.v1.jo_g3.n, blind.E206B.models.v0.jo_g3.n
153 PASS | arm B's MM1-v1 reads 14.3% (n 105) and arm A's MM1-v0 9.8% (n 109) | 14.3, 105, 9.8, 109 | numbers.json: blind.E206B.models.v1.jo_g.rms_pct, blind.E206B.models.v1.jo_g.n, blind.E206A.models.v0.jo_g.rms_pct, blind.E206A.models.v0.jo_g.n
154 PASS | XREF: 14.30% (n 105) committed | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab | arm B's committed all-points table
155 PASS | MM1-v1 reads 0.21 W rms on arm B's 7 and MM1-v0 0.31 W on arm A's 8 | 0.21, 7, 0.31, 8 | numbers.json: blind.E206B.under_3W.v1.rms_w, blind.E206B.under_3W.v1.n, blind.E206A.under_3W.v0.rms_w, blind.E206A.under_3W.v0.n
156 PASS | (46 for MM1-v2, 50 for MM1-v1, 47 for F1, 46 for F2) | 46, 50, 47, 46 | numbers.json: blind.E207.models.v2.jo_g3.n, blind.E207.models.v1.jo_g3.n, blind.E207.models.F1.jo_g3.n, blind.E207.models.F2.jo_g3.n
157 PASS | time per case over the 47 cases | 47 | numbers.json: blind.E207.n.cases_scored
158 PASS | time per case over the 41 cases | 41 | numbers.json: blind.E209.n_cases
159 PASS | (45 for MM1-v2, 39 for MM1-v1, 42 for F1@800 and F2@800; no E209 point read under 3 W) | 45, 39, 42, 42, no | numbers.json: blind.E209.models.v2.jo_g3.n, blind.E209.models.v1.jo_g3.n, blind.E209.models.F1.jo_g3.n, blind.E209.models.F2.jo_f3.n, blind.E209.n_points_under_3W_measured
160 PASS | on the scorer's own footing, the rms of ln, it reads 82.2% | 82.2 | numbers.json: blind.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct
161 PASS | every point above 3 W | 3 | numbers.json: blind.E211.W_min_measured
162 PASS | 24 of its 119 points are bridges from experiments in MM1-v0's own fit | 24, 119 | numbers.json: blind.E206A.subsets.ran_before_any_card.n, blind.E206A.n_points
163 PASS | (11 of them on aifoundry3 itself) | 11 | numbers.json (119 - the 108 never on aifoundry3)
164 PASS | On the 95 points never run on any card MM1-v0 read **10.2% (-2.9)** in cycles and **10.4%** in joules over idl | 95, 10.2, -2.9, 10.4, 8.8 | numbers.json: blind.E206A.subsets.never_any_card.n, blind.E206A.subsets.never_any_card.models.v0.cyc_mean.rms_pct, blind.E206A.subsets.never_any_card.models.v0.cyc_mean.bias_pct, blind.E206A.subsets.never_any_card.models.v0.jo_g.rms_pct, blind.E206A.subsets.never_any_card.models.v0.jo_g3.rms_pct
165 PASS | on the 24 bridges, 6.2% and 7.1% | 24, 6.2, 7.1 | numbers.json: blind.E206A.subsets.ran_before_any_card.n, blind.E206A.subsets.ran_before_any_card.models.v0.cyc_mean.rms_pct, blind.E206A.subsets.ran_before_any_card.models.v0.jo_g.rms_pct
166 PASS | On the 85 points never run on card 1, MM1-v1 read 4.7% in cycles and 15.5% in joules over idle (n 77) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
167 PASS | XREF: never on card 1 before arm B, rebuilt: 85 points, MM1-v1 4.7 in cycles, 15.5 (n 77) in J over idle on ev | 85, 4.7, 15.5, 77 | numbers.json: blind.E206B.subsets.never_card1_before_armB.n, blind.E206B.subsets.never_card1_before_armB.models.v1.cyc_mean.rms_pct, blind.E206B.subsets.never_card1_before_armB.models.v1.jo_g.rms_pct, blind.E206B.subsets.never_card1_before_armB.models.v1.jo_g.n | equals arm B's dated note 1 (the check above)
168 PASS | its joules over idle read 12.7% (n 71; desk) | 12.7, 71 | numbers.json: blind.E206B.subsets.never_card1_before_armB.models.v1.jo_g3.rms_pct, blind.E206B.subsets.never_card1_before_armB.models.v1.jo_g3.n
169 PASS | with the seconds forecast (F1's), it read 43.7% on E209 (82.2% as the scorer's rms of ln: it under-forecasts)  | 43.7, 82.2, 30.8 | numbers.json: blind.E209.models.F2.jo_f3.rms_pct, blind.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct, blind.E211.sets.rgm211_12.F2.jo_f3.rms_pct
170 PASS | (E209's data README, item 6) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3 | e30 (gemmL2x8x4 int8) = E206's p016 (points-e206.json)
171 PASS | leaves E206's 119 points out as one fold | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
172 PASS | MM1-v0 already carried an awake power of 3.660 W for it | found | tools/matmul/mm1/v0/README.md @ 2d1413f56
173 PASS | its 53 points never ran on any card before MM1-v1 and MM1-v2 were frozen | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
174 PASS | at 05:30 and 06:16 PST | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
175 PASS | at 45 points never run on that card | found | tools/claims-v3/e209/E209.md @ d7b574f5f
176 PASS | (4 of them in both models' fit, 3 run in E207 before the freeze, 5 never run) | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
177 PASS | its 12 rgm136 twins | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
178 PASS | at least 90% of its cases or points sit within twice MM1-v1's larger held-out error | found | tools/claims-v3/e207/E207.md @ 3649245b7
179 PASS | 13 to 16% per case in cycles and seconds | found | tools/claims-v3/e207/E207.md @ 3649245b7 | T1 and T3 at 13% (E207.md section 7 table)
180 PASS | 15 to 16% per point in joules over idle | found | tools/claims-v3/e207/E207.md @ 3649245b7
181 PASS | 5% and 13% with the card at rest | found | tools/claims-v3/e207/E207.md @ 3649245b7 | the E3 and E4 rows of E207.md section 7
182 PASS | T1 45/47, T2 44/47, T3 45/47 | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
183 PASS | E1 50/53, E2 48/53, E3 51/53, E4 50/53 | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
184 PASS | 39 to 8 (exact sign test p 5.5e-06 | 5.539621596994948e-06 -> 5.5e-06 | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
185 PASS | H2 on the counter's mean 45 to 2 | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
186 PASS | H3 and H4 against F2 on joules over idle 47 to 2 each | found | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.txt @ f5c531459
187 PASS | (7/0/0 against F1, 8/0/0 against F2) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
188 PASS | closer at 24 cases against 18, p 0.44 | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
189 PASS | (30 against 11, p 0.0043) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
190 PASS | but the family-level check does not confirm it (families 5 / 0 / 3: NOT DECIDED) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
191 PASS | 62 of 62 runs in 26.16 card-minutes | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
192 PASS | first card command 10:30:44 PST, 8 h 46 min after | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
193 PASS | 29 shapes, three formats, four data kinds, five shire counts | found | tools/claims-v3/e209/E209.md @ d7b574f5f
194 PASS | 15,675 of 15,675 samples carry it (600 MHz 11,545, 700 MHz 131, 800 MHz 3,999) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
195 PASS | it stepped inside every device process | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md @ ea3fa3ce3
196 PASS | 19% in cycles and seconds, 14% and 15% in joules over idle, 5% and 13% with the card at rest | found | tools/claims-v3/e209/E209.md @ d7b574f5f
197 PASS | pass when at least 90% of cases or points sit within twice MM1-v2's larger held-out error | found | tools/claims-v3/e209/E209.md @ d7b574f5f
198 PASS | T1m, T1c, T2m, T2c, T3m and T3c PASS at 39 of 41 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
199 PASS | E1 PASS 45/45, E2m 42/45, E2c 41/44, E3 43/45, E4m 42/45, E4c 41/44 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
200 PASS | K1 (the clock forecast) PASS 44/45 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
201 PASS | XREF: E209 rules in the scorer's output | all present | scored-e209.json rules and head_to_head | every count above equals scored-e209.json's rules
202 PASS | wall cycles **7.2%**, MM1-v1 9.3%, F1@800 18.1% | 7.2, 9.3, 18.1 | numbers.json: blind.E209.registered_summaries_ln.v2_m cycles wall.rms_ln_pct, blind.E209.registered_summaries_ln.v1_m cycles wall.rms_ln_pct, blind.E209.registered_summaries_ln.F1 cycles wall.rms_ln_pct
203 PASS | seconds **5.4%** (45 points), MM1-v1 5.6% (39) | 5.4, 45, 5.6, 39 | numbers.json: blind.E209.registered_summaries_ln.v2 J over idle given t.rms_ln_pct, blind.E209.registered_summaries_ln.v2 J over idle given t.n, blind.E209.registered_summaries_ln.v1 J over idle given t.rms_ln_pct, blind.E209.registered_summaries_ln.v1 J over idle given t.n
204 PASS | F2@800 with its seconds 82.2% | 82.2 | numbers.json: blind.E209.registered_summaries_ln.F2 J over idle.rms_ln_pct
205 PASS | (+0.0158, 95% [+0.0037, +0.0293] in ln) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
206 PASS | the sign test reads 17 against 11 (p 0.345: NOT DECIDED) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
207 PASS | the families split 2 against 2 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
208 PASS | The subsets carry 67% of the summed difference | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
209 PASS | (H5, 38 against 3, p 1.05e-08) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
210 PASS | (H6, 35 against 5, p 1.38e-06) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
211 PASS | (e39) ran 24% more cycles than MM1-v2 forecast | 23.96 -> 24 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
212 PASS | `gemmL3x1x5` fp32 (e15) 19% | 19.34 -> 19 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
213 PASS | failed T2's 19% band by 0.03 points | 19, 0.03 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/posthoc-note15-e209.json (T2m: e42 0.19034 against the band 0.19)
214 PASS | The stride step at NB 8 measured 1.297 against MM1-v2's 1.187 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
215 PASS | int8 at one K block (e07) ran 1.158 times MM1-v2's wall cycles | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
216 PASS | real int8 tiles saved 9.0% of the joules against MM1-v2's 2.7% | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
217 PASS | 38 of 38 runs and the smoke in 17.99 card-minutes | found | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/README.md @ 38aaf004e
218 PASS | (13%, 16% and 13% in cycles and seconds; 15%, 16%, 5% and 13% in joules), PASS at 90% of rgm211's 12 points | found | tools/claims-v3/e211/E211.md @ 1393a6493
219 PASS | **T1 11/12, T2 12/12, T3 11/12, E1 12/12, E2 12/12, E3 11/12, E4 12/12: PASS** | found | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt @ 8f44b3800 | E211's registered scorer output, committed beside its data
220 PASS | ran 2.9% and 5.8% fewer wall cycles on rgm211 | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
221 PASS | (tolerance 0.01 in ln) | found | tools/claims-v3/e211/E211.md @ 1393a6493
222 PASS | (the two controls differ by 0.031 in ln) | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
223 PASS | W1, the ratio rule, reads FAIL 5/10 | found | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt @ 8f44b3800 | E211's registered scorer output, committed beside its data
224 PASS | MM1 BETTER (10/1/1, p 0.0117) | 0.01171875 -> 0.0117 | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.txt @ 8f44b3800 | E211's registered scorer output, committed beside its data
225 PASS | W2 (the direction) PASS, with the same words, "the controls did not pass: not a model test" | all present | docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/scores-e211-A.json rules.W2 | scores-e211-A.json rules.W2: verdict and caveat
226 PASS | (frozen 5 h 8 min before the first card command; | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
227 PASS | its wall cycles read **8.9%** rms (+4.0), MM1-v1 8.1%, F1 14.5%, NC 23.5% | 8.9, 4.0, 8.1, 14.5, 23.5 | numbers.json: blind.E211.sets.rgm211_12.v2.cyc_wall.rms_pct, blind.E211.sets.rgm211_12.v2.cyc_wall.bias_pct, blind.E211.sets.rgm211_12.v1.cyc_wall.rms_pct, blind.E211.sets.rgm211_12.F1.cyc_wall.rms_pct, blind.E211.sets.rgm211_12.NC.cyc_wall.rms_pct
228 PASS | on the 12 rgm136 twins MM1-v2 read 2.9% and MM1-v1 3.7% | 2.9, 3.7 | numbers.json: blind.E211.sets.twins_12.v2.cyc_wall.rms_pct, blind.E211.sets.twins_12.v1.cyc_wall.rms_pct
229 PASS | (3.2% for both versions; F1 18.4%) | 3.2, 3.2, 18.4 | numbers.json: blind.E211.sets.rgm211_12.v2.jo_g3.rms_pct, blind.E211.sets.rgm211_12.v1.jo_g3.rms_pct, blind.E211.sets.rgm211_12.F1.jo_g3.rms_pct
230 PASS | The ratio rgm211 / rgm136 over 10 pairs, rms of ln: MM1-v2 0.074, MM1-v1 0.065, F1 0.128, NC 0.126, N0 (no wal | found | tools/matmul/mm1/v2/score-e211.md @ d38f148c5
231 PASS | but its cycles error rose from 3-4% to 8-9% | 3-4, 8-9 | numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)
232 PASS | MM1-v0 closer than F1 at **89 of 119** points in cycles | 89, 119 | numbers.json: blind.E206A.h2h.v0<F1:cyc_mean.closer, blind.E206A.h2h.v0<F1:cyc_mean.n
233 PASS | **96 of 109** in joules over idle; closer than F2 at **104 of 109** | 96, 109, 104, 109 | numbers.json: blind.E206A.h2h.v0<F1:jo_g.closer, blind.E206A.h2h.v0<F1:jo_g.n, blind.E206A.h2h.v0<F2:jo_g.closer, blind.E206A.h2h.v0<F2:jo_g.n
234 PASS | MM1-v1 closer than F1 at **87 of 113** in cycles and **85 of 105** in joules over idle; closer than F2 at **99 | 87, 113, 85, 105, 99, 105 | numbers.json: blind.E206B.h2h.v1<F1:cyc_mean.closer, blind.E206B.h2h.v1<F1:cyc_mean.n, blind.E206B.h2h.v1<F1:jo_g.closer, blind.E206B.h2h.v1<F1:jo_g.n, blind.E206B.h2h.v1<F2:jo_g.closer, blind.E206B.h2h.v1<F2:jo_g.n
235 PASS | XREF: 87 of 113 (committed) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab | arm B's committed head to head
236 PASS | XREF: 85 of 105 / 99 of 105 (committed) | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
237 PASS | MM1-v1 was closer than MM1-v0 at 69 of 113 in cycles | 69, 113 | numbers.json: blind.E206B.h2h.v1<v0:cyc_mean.closer, blind.E206B.h2h.v1<v0:cyc_mean.n
238 PASS | On E207's footing, the points of 3 W and above: closer than F1 at 91 of 101 and than F2 at 99 of 101 | 91, 101, 99, 101 | numbers.json: blind.E206A.h2h.v0<F1:jo_g3.closer, blind.E206A.h2h.v0<F1:jo_g3.n, blind.E206A.h2h.v0<F2:jo_g3.closer, blind.E206A.h2h.v0<F2:jo_g3.n
239 PASS | At the points of 3 W and above: closer than F1 at 81 of 98 and than F2 at 95 of 98 (desk) | 81, 98, 95, 98 | numbers.json: blind.E206B.h2h.v1<F1:jo_g3.closer, blind.E206B.h2h.v1<F1:jo_g3.n, blind.E206B.h2h.v1<F2:jo_g3.closer, blind.E206B.h2h.v1<F2:jo_g3.n
240 PASS | The same 85-run schedule | found | docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/README.md @ 5d99fe172
241 PASS | repeated to **0.41%** rms in cycles an op | 0.41 | numbers.json: repeat.E208.cyc_op_mean.rms_pct
242 PASS | 0.38% on the slowest minion | 0.38 | numbers.json: repeat.E208.cyc_op_max.rms_pct
243 PASS | 0.38% in seconds | 0.38 | numbers.json: repeat.E208.T_op_us.rms_pct
244 PASS | **1.19%** in watts over idle | 1.19 | numbers.json: repeat.E208.dP_w.rms_pct
245 PASS | **1.16%** in joules over idle | 1.16 | numbers.json: repeat.E208.J_op.rms_pct
246 PASS | (0.72% with the die corrected to 50 C, post hoc) | 0.72 | numbers.json: repeat.E208.J_op_c50.rms_pct
247 PASS | XREF: 0.409% committed | found | docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.md @ 5d99fe172 | E208's committed repeat table
248 PASS | XREF: 1.163% committed | found | docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/repeat-e208-a2c0-S1r.md @ 5d99fe172
249 PASS | differed by 0.04 to 0.19% rms in cycles and 1.0 to 1.8% in joules over idle | 0.04, 0.19, 1.0, 1.8 | numbers.json repeat.within_day
250 PASS | MM1's blind errors are 3 to 23 times the session repeat | 3, 23 | numbers.json: blind_summary.over_repeat_min, blind_summary.over_repeat_max
251 PASS | rgm136 unchanged, 74 arms on three cards | found | tools/claims-v3/e208/E208.md @ d005dc530
252 PASS | 221 arms and an anchor in 10 sessions | found | tools/claims-v3/e212/E212.md @ c83a29d13
253 PASS | is in progress: as of `724e8f39`, nine of its ten sessions are committed (`d2ece7e8`, `5601b6a7`, `7726e127`,  | nine, d2ece7e8, 5601b6a7, 7726e127, a90105da, 7dfba40b, ebe552fe, d8de38b0, 58f01105, 724e8f39 | git ls-tree 724e8f39 docs/reports/data/ (a1c1-S1 d2ece7e8, a1c0-S1 5601b6a7, a1c1-S4 7726e127, a1c0-S2 a90105da, a1c1-S2 7dfba40b, a2c0-S1 ebe552fe, a1c1-S3 d8de38b0, a2c0-S2 58f01105, a2c0-S4 724e8f39) | the E212 data folders in the tree of 724e8f39, each with the commit that added it
254 PASS | `8f2df483`, was sealed at 12:58:15 PST, 3 min 50 s before the first session it covers (a1c1-S2) made its first | found | docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S2/README.md @ 7dfba40bf
255 PASS | XREF: every sealed sha256 in its registration | all present | tools/claims-v3/sealed-e206/e206-freeze-lines.md, tools/claims-v3/sealed-e206/e206-freeze-lines-2.md, tools/claims-v3/sealed-e207/e207-freeze-lines.md, tools/claims-v3/e208/E208.md, tools/claims-v3/sealed-e209/e209-freeze-lines.md, tools/claims-v3/sealed-e210/e210-freeze-lines.md, tools/claims-v3/sealed-e211/e211-freeze-lines.md, tools/claims-v3/e212/E212.md, docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S2/README.md | each sha256 prefix of the table found in the file that registers it
256 PASS | nine fp32 operand patterns never run in a GEMM, at two shapes | found | tools/claims-v3/e210/E210.md @ 7b59f7191
257 PASS | random minus zeros: 29.78 W and 20.53 W | found | tools/claims-v3/e210/E210.md @ 7b59f7191
258 PASS | the time equality PASS in all 20 cases | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
259 PASS | B5 (R1 within 5% of D | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b | 0.05 D = 5% of D
260 PASS | PASS 13 of 13 | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
261 PASS | the nearest measured kind (H1, 10 to 1) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
262 PASS | the raw bit-flip price (H2, 12 to 0) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
263 PASS | the bit-flip price with one scale (H3, 10 to 0) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
264 PASS | UNDECIDED (4 to 0 with 1 tie; 5 cases, too few to decide, as registered) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
265 PASS | R1's error is **0.481 W rms, 1.87% of D** | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
266 PASS | against 3.849 W (16.19%) for the scaled bit flips, 5.128 W (19.71%) for the nearest kind, 5.575 W (21.22%, 5 c | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
267 PASS | sits within 0.8% of the calibrated one | 0.8 | numbers.json switch.kappa (scores-e210-A.json)
268 PASS | (S1 1.6767 × 10^16 switches a J against 1.6733 × 10^16; S2 1.6235 against 1.6367 × 10^16) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
269 PASS | H1 is UNDECIDED (6 to 1, 1 tie) | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
270 PASS | 142 of 171 runs, when the card-time rule stopped new runs at 85.01 card-minutes | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md @ 6689d68f6
271 PASS | the die gate made each run about 35 s, not the planned 26 | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
272 PASS | 9 of the 13 test cases are scored on 2 of 3 blocks | found | docs/reports/data/2026-11-17-e210-switch-test-aifoundry3/README.md.dated-note-1.md @ d203e577b
273 PASS | committed data put ones at about 0.31 of D where the count says about 0.05 | found | tools/claims-v3/e210/E210.md @ 7b59f7191
274 PASS | (M a multiple of 1,024, N of 512, K of a block) | found | tools/claims-v3/e209/E209.md @ d7b574f5f
275 PASS | E211 shows a recompiled kernel's cycles drift 8-9% | 8-9 | numbers.json (E211 wall cycles, MM1-v1 and MM1-v2, twins and rgm211)
276 PASS | MM1-v2's energy reads 10.13% against 9.15% for MM1-v1's form | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
277 PASS | and MM1-v1's 14.2-42.1% | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8
278 PASS | missed the int8 saving by 6 points | 6 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/posthoc-note15-e209.json (e35/e01: measured 0.910, MM1-v2 0.973)
279 PASS | E207's real and designed tiles b49-b52 were NOT FORECAST in energy by MM1-v2 | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
280 PASS | ("blind4: M6; blind3: M5" | found | tools/matmul/mm1/v1/README.md @ 25d2e74e8 | MM1-v1's rule for a kind with no ledger row
281 PASS | given the measured seconds read -5.4%, -6.0%, +4.2% and +7.1% at b49-b52, with E1 and E2 PASS at all four | -5.4, -6.0, +4.2, +7.1 | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.json points b49-b52 (mm1_v1.given.J_over / measured.j_over - 1; E1 and E2 cells PASS) | scores-e207-A.json points b49-b52: MM1-v1's given J over idle / measured - 1; rules E1, E2
282 PASS | On arm B's 14 all-zero points | 14 | numbers.json: blind.E206B.classes.data kind: zeros.n
283 PASS | joules over idle **27.8%** rms (**+25.7%** bias) | 27.8, 25.7 | numbers.json: blind.E206B.classes.data kind: zeros.jo_g.v1.rms_pct, blind.E206B.classes.data kind: zeros.jo_g.v1.bias_pct
284 PASS | MM1-v0 33.7% (+31.4%) | 33.7, 31.4 | numbers.json: blind.E206B.classes.data kind: zeros.jo_g.v0.rms_pct, blind.E206B.classes.data kind: zeros.jo_g.v0.bias_pct
285 PASS | where F1 read 13.5% | 13.5 | numbers.json: blind.E206B.classes.data kind: zeros.jo_g.F1.rms_pct
286 PASS | closer at 13 of the 14 | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
287 PASS | XREF: zeros committed | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab | arm B's committed class row
288 PASS | watts over idle +21.2% (42 runs | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
289 PASS | (2.406 W at 1,024 minions against MM1-v1's 3.257 W) | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179
290 PASS | the subset points of 3 W and above read 7.0% for MM1-v1 | 7.0 | numbers.json: blind.E206B.classes.subset (mask < 32 shires).jo_g3.v1.rms_pct
291 PASS | the 7 under 3 W (1, 4 or 8 shires, 0.31 to 2.78 W over idle) read -0.05 to +0.39 W off, MM1-v1 high at 6 of th | 7, 1, 4, 8, 0.31, 2.78, -0.05, +0.39, 6, +0.18, +0.22 | numbers.json blind.E206B.under_3W_detail
292 PASS | +62% and +43% at the two smallest | found | docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/README.md.dated-note-1.md @ f155c8cab
293 PASS | -14.0% (mask 0x3) and -10.2% (0xfff) in wall cycles; MM1-v2's contention on the DRAM stream alone moved them t | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
294 PASS | 3x6x4 fp32 on 12 shires (0xfff) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
295 PASS | +13.3%: on that mask | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
296 PASS | faster than on 2 or on 24 shires | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
297 PASS | On E209 the one shire 0x80000000 ran 24% over MM1-v2 | 23.96 -> 24 | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
298 PASS | MM1-v2 was closer than MM1-v1 at 6 of the 9 subset points | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
299 PASS | E209's step at NB 8 measured 1.297 against MM1-v2's 1.187 | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
300 PASS | int8 at one K block ran 1.158 times MM1-v2's wall cycles on E209 (e07) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
301 PASS | and -14.0% on E207 (n01) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
302 PASS | -18.4% (E207's n02, int8) and -13.6% (n03, fp32) | found | tools/matmul/mm1/v2/score-e207.md @ 030ffa42c
303 PASS | int8 inside the L3 ran 6.3 to 6.5% more cycles than fp32 | 6.3, 6.5 | docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/scores-e207-A.json cases (6.338, 6.348, 6.348, 6.547%) | scores-e207-A.json cases: measured wall cycles, int8 / fp32 - 1, at 1x3x2, 2x3x2, 3x2x2 and 1x4x3 (score-e207.md rounds the top to 6.6)
304 PASS | rgm211's controls ran 3-6% fast, and MM1's cycles error there was 8-9% | 3-6, 8-9 | tools/matmul/mm1/v2/score-e211.json
305 PASS | (e44, 788.9 MHz measured against 764.1 forecast) | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1
306 PASS | two of 55 runs whose capped state MM1-v2 read wrong | found | docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/README.md.dated-note-15.md @ b067742b1 | 55 - 53 = 2
307 PASS | about 16 minutes in all | found | tools/matmul/mm1/v2/README.md @ 3ca4b7179

CHECKS: 307 run, 0 FAIL
NUMBERS OF README.md NO CHECK COVERS (228: dates, times, ids, section numbers, counts named in the text; for a reader to judge):
  line 1: 1,
  line 3: 17 2026 47
  line 8: 3.12
  line 18: 1
  line 28: 2026 11 17 1
  line 34: 1
  line 35: 1
  line 41: 2
  line 44: 3
  line 49: 4
  line 51: 3
  line 52: 3
  line 58: 5
  line 63: 6
  line 67: 6 1, 8,
  line 70: 1
  line 72: 16 2026,
  line 83: 2
  line 86: 05
  line 91: 2
  line 95: 4
  line 104: 32
  line 107: 1 1
  line 109: 1 2
  line 110: 2
  line 112: 1
  line 113: 1 1
  line 115: 2
  line 118: 2
  line 119: 3
  line 124: 4
  line 125: 5
  line 129: 7
  line 130: 5
  line 133: 0 600
  line 134: 2026 11 17
  line 145: 4
  line 147: 4 7 16 2026
  line 150: 17 2026
  line 153: 5.1
  line 154: 0
  line 155: 4
  line 157: 3
  line 159: 2 2
  line 162: 11
  line 164: 7,
  line 165: 2
  line 174: 4
  line 185: 6
  line 192: 3
  line 195: 4
  line 196: 3
  line 198: 6,
  line 199: 4.1
  line 205: 4
  line 212: 7
  line 214: 0, 600
  line 215: 1, 600
  line 216: 0, 600
  line 217: 0, 800, 800
  line 218: 0, 600
  line 220: 3 3
  line 222: 3
  line 226: 3
  line 255: 1, 7
  line 257: 3
  line 259: 3
  line 260: 3
  line 263: 800
  line 264: -100
  line 272: 1
  line 273: 1
  line 274: 2
  line 275: 3
  line 279: 1
  line 282: 3
  line 291: 7
  line 292: 06,
  line 293: 2,
  line 305: 7
  line 306: 15,
  line 311: 15
  line 313: 0,
  line 314: 800 800
  line 316: 15
  line 323: 0
  line 327: 7
  line 329: 1,
  line 330: 3
  line 334: 12
  line 336: 3
  line 338: 3
  line 351: 0
  line 353: 600
  line 354: 3
  line 370: 8
  line 380: 5
  line 382: 4 4
  line 386: 0,
  line 399: 1 4
  line 404: 1
  line 407: 6
  line 409: 5 5
  line 419: 0
  line 420: 5
  line 423: 0
  line 425: 2
  line 432: 1
  line 433: 1
  line 434: 1 1
  line 435: 1 1
  line 441: 6,
  line 449: 15
  line 453: 7
  line 462: 2026 11 16 2026 11 17
  line 463: 2026 11 17
  line 464: 15 2026 11 17
  line 465: 2026 11 17
  line 466: 2026 11 17
  line 467: 2026 11 17
  line 468: 2026 11 02 2026 11 02 2026 11 03
  line 474: 9
  line 475: 10 9,
  line 476: 2026 11 16
  line 477: 2026 11 17
  line 478: 2026 11 17
  line 479: 2026 11 17
  line 480: 1
  line 481: 2026 11 17
  line 482: 2026 11 17
  line 484: 2026 11 17
  line 485: 2026 11 17
  line 486: 2026 11 17
  line 489: 4
  line 497: 1 5
  line 501: 2026 11 17
  line 505: 2026 11 17 47
  line 509: 6
  line 510: 3
  line 511: 1 3
  line 516: 7 7
  line 518: 5 2
  line 521: 2.0
interpreter: /usr/bin/python3 3.12.3
