# E116 results (score_e116.py; registered rules from predictions-e116.json)

**E116-R0 (read-back): PASS** — 22 of 22 reads equal accum.c on every word of all 1,024 minions; 22 reads ran. Card 1 (E104) cross-check: 7 of 7 tiles the same words.

| tile | n | equal accum.c | distinct C | C[0][0] card / accum | C[0][8] card / accum | what it does |
|---|---:|---|---:|---|---|---|
| fp32.c_abs | 199874 | True | 1 | 7a433080 / 7a433080 | 7a433080 / 7a433080 | holds: a 2^100 product at k = 0 absorbs every later product (C = n x 2^100) |
| fp32.r_walk | 199874 | True | 1 | 49f9890a / 49f9890a | 4a299930 / 4a299930 | walks: the same operands as r_abs, k = 0 slice 1.0 |
| fp32.r_abs | 199874 | True | 1 | 7a433080 / 7a433080 | 7a433080 / 7a433080 | holds: absorbed, random positive operands (C = n x 2^100) |
| fp32.r_het | 199874 | True | 1 | 7a532d3f / 7a532d3f | 7a4eaad2 / 7a4eaad2 | holds per accumulator, the accumulators differ (k = 0 B row 2^50 m_j) |
| fp32.s_walk | 199874 | True | 1 | 49c33080 / 49c33080 | c9433080 / c9433080 | walks: +-1 operands |
| fp32.s_abs | 199874 | True | 1 | 7a433080 / 7a433080 | 7a433080 / 7a433080 | holds: absorbed, +-1 operands (C = n x 2^100) |
| fp16.c_cancel | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0: each micro-op's dot product cancels exactly |
| fp16.r_walk | 199874 | True | 1 | c9c7b3b6 / c9c7b3b6 | c77e6a3f / c77e6a3f | walks |
| fp16.r_cancel | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0: paired values cancel exactly |
| fp16.r_abs | 199874 | True | 1 | 57aaebf1 / 57aaebf1 | 57aaebf1 / 57aaebf1 | walks one unit a micro-op (E104 on card 1: fp16 truncates each aligned product separately) |
| int8.c_cancel | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0: each micro-op's dot product cancels exactly |
| int8.r_walk | 199874 | True | 1 | 9b2784bc / 9b2784bc | 625987de / 625987de | walks (int32, wraps) |
| int8.r_cancel | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0: paired bytes cancel exactly |
| fp32.zeros | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0 (every lane gated) |
| fp32.randn | 199874 | True | 1 | c8099fe8 / c8099fe8 | 47e02600 / 47e02600 | walks (anchor) |
| fp32.ones | 199874 | True | 1 | 4a433080 / 4a433080 | 4a433080 / 4a433080 | walks (anchor) |
| fp16.zeros | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0 (every lane gated) |
| fp16.randn | 199874 | True | 1 | 466fd174 / 466fd174 | c8a9d21c / c8a9d21c | walks (anchor) |
| fp16.ones | 199874 | True | 1 | 4ac33080 / 4ac33080 | 4ac33080 / 4ac33080 | walks (anchor) |
| int8.zeros | 199874 | True | 1 | 00000000 / 00000000 | 00000000 / 00000000 | holds at 0 (every lane gated) |
| int8.full | 199874 | True | 1 | 862deba0 / 862deba0 | 25513998 / 25513998 | walks (anchor) |
| int8.ones | 199874 | True | 1 | 00c33080 / 00c33080 | 00c33080 / 00c33080 | walks (anchor) |

Kept passes: 4 ['11611', '11612', '11613', '11614']; set aside: [{'pass': 11610, 'why': ['int8.zeros departs -0.316 W from its straight line']}]

**fp32** total D(r_walk) 22.273 ± 0.129 W
- i_clocked_lane: 8.386 ± 0.116 W, share 0.377 ± 0.004, of the anchor 0.339 ± 0.004
- iii_operand_multiplier: 8.855 ± 0.112 W, share 0.398 ± 0.006, of the anchor 0.358 ± 0.004
- ii_result_path: 5.032 ± 0.147 W, share 0.226 ± 0.006, of the anchor 0.203 ± 0.006
- unplaced of the anchor 0.100 ± 0.004
**fp16** total D(r_walk) 21.244 ± 0.154 W
- i_clocked_lane: 8.376 ± 0.065 W, share 0.394 ± 0.003, of the anchor 0.378 ± 0.002
- iii_operand_multiplier: 6.361 ± 0.145 W, share 0.299 ± 0.009, of the anchor 0.287 ± 0.008
- ii_result_path: 6.508 ± 0.242 W, share 0.306 ± 0.009, of the anchor 0.294 ± 0.010
- unplaced of the anchor 0.041 ± 0.004
**int8** total D(r_walk) 7.046 ± 0.212 W
- i_clocked_lane: 1.685 ± 0.334 W, share 0.239 ± 0.045, of the anchor 0.235 ± 0.044
- iii_operand_multiplier: 3.397 ± 0.287 W, share 0.482 ± 0.053, of the anchor 0.474 ± 0.044
- ii_result_path: 1.964 ± 0.326 W, share 0.279 ± 0.039, of the anchor 0.274 ± 0.048
- unplaced of the anchor 0.017 ± 0.035

**E116-S**
- fp32: **PASS** i_clocked_lane 0.377 vs 0.367 (band 0.040) PASS; iii_operand_multiplier 0.398 vs 0.399 (band 0.040) PASS; ii_result_path 0.226 vs 0.234 (band 0.040) PASS
- fp16: **PASS** i_clocked_lane 0.394 vs 0.389 (band 0.040) PASS; iii_operand_multiplier 0.299 vs 0.303 (band 0.040) PASS; ii_result_path 0.306 vs 0.308 (band 0.040) PASS
- int8: **PASS** i_clocked_lane 0.239 vs 0.257 (band 0.080) PASS; iii_operand_multiplier 0.482 vs 0.472 (band 0.080) PASS; ii_result_path 0.279 vs 0.271 (band 0.080) PASS

**E116-W**
- fp32: **PASS** i_clocked_lane 8.386 vs 8.160 (band 0.979) PASS; iii_operand_multiplier 8.855 vs 8.873 (band 1.065) PASS; ii_result_path 5.032 vs 5.193 (band 0.623) PASS
- fp16: **PASS** i_clocked_lane 8.376 vs 8.219 (band 0.986) PASS; iii_operand_multiplier 6.361 vs 6.396 (band 0.767) PASS; ii_result_path 6.508 vs 6.497 (band 0.780) PASS
- int8: **PASS** i_clocked_lane 1.685 vs 1.757 (band 0.600) PASS; iii_operand_multiplier 3.397 vs 3.230 (band 0.600) PASS; ii_result_path 1.964 vs 1.858 (band 0.600) PASS

**E116-T (session tie): PASS** fp32.randn 24.744 ± 0.098 vs E78 24.725 PASS; fp16.randn 22.149 ± 0.085 vs E78 22.162 PASS; int8.full 7.160 ± 0.062 vs E78 7.056 PASS

**E116-H (E88's 13 mechanism rules): INCONCLUSIVE** — 12 of 13 the same; differ: {'H4-signs-result': ['PASS', 'INCONCLUSIVE']}

**E116-P (E88's 19 bands, reported):** 17 of 19 PASS; tally of all 32: {'PASS': 28, 'FAIL': 3, 'INCONCLUSIVE': 1, 'not scored': 0}
- P-F32: card 1 PASS, aifoundry3 PASS
- P-W32: card 1 PASS, aifoundry3 PASS
- P-M32: card 1 PASS, aifoundry3 PASS
- P-R32: card 1 PASS, aifoundry3 PASS
- P-R32bus: card 1 PASS, aifoundry3 PASS
- P-R32sum: card 1 PASS, aifoundry3 PASS
- P-M32s: card 1 FAIL, aifoundry3 FAIL
- P-R32s: card 1 FAIL, aifoundry3 FAIL
- P-X32: card 1 PASS, aifoundry3 PASS
- P-F16: card 1 PASS, aifoundry3 PASS
- P-W16: card 1 PASS, aifoundry3 PASS
- P-M16: card 1 PASS, aifoundry3 PASS
- P-R16: card 1 PASS, aifoundry3 PASS
- P-A16: card 1 PASS, aifoundry3 PASS
- P-R16abs: card 1 PASS, aifoundry3 PASS
- P-F8: card 1 PASS, aifoundry3 PASS
- P-W8: card 1 PASS, aifoundry3 PASS
- P-M8: card 1 PASS, aifoundry3 PASS
- P-R8: card 1 PASS, aifoundry3 PASS

| contrast | a − b | D (W) ±95% | E88 card 1 | ratio |
|---|---|---|---|---|
| F32 | fp32.c_abs − fp32.zeros | 8.386 ± 0.116 | 7.922 | 1.059 |
| W32 | fp32.ones − fp32.c_abs | 0.026 ± 0.020 | 0.100 | 0.259 |
| M32 | fp32.r_abs − fp32.c_abs | 8.855 ± 0.112 | 8.614 | 1.028 |
| R32 | fp32.r_walk − fp32.r_abs | 5.032 ± 0.147 | 5.042 | 0.998 |
| R32bus | fp32.r_het − fp32.r_abs | 3.889 ± 0.106 | 3.801 | 1.023 |
| R32sum | fp32.r_walk − fp32.r_het | 1.143 ± 0.150 | 1.241 | 0.921 |
| M32s | fp32.s_abs − fp32.c_abs | 2.627 ± 0.218 | 2.524 | 1.041 |
| R32s | fp32.s_walk − fp32.s_abs | 2.134 ± 0.153 | 2.259 | 0.944 |
| X32 | fp32.randn − fp32.r_walk | 2.471 ± 0.113 | 2.241 | 1.103 |
| F16 | fp16.c_cancel − fp16.zeros | 8.376 ± 0.065 | 7.955 | 1.053 |
| W16 | fp16.ones − fp16.c_cancel | 0.018 ± 0.072 | 0.014 | 1.263 |
| M16 | fp16.r_cancel − fp16.c_cancel | 6.361 ± 0.145 | 6.190 | 1.028 |
| R16 | fp16.r_walk − fp16.r_cancel | 6.508 ± 0.242 | 6.289 | 1.035 |
| A16 | fp16.r_abs − fp16.r_cancel | 0.410 ± 0.133 | 0.388 | 1.058 |
| R16abs | fp16.r_walk − fp16.r_abs | 6.097 ± 0.173 | 5.901 | 1.033 |
| F8 | int8.c_cancel − int8.zeros | 1.678 ± 0.176 | 1.710 | 0.981 |
| W8 | int8.ones − int8.c_cancel | -0.104 ± 0.113 | -0.231 | 0.452 |
| M8 | int8.r_cancel − int8.c_cancel | 3.402 ± 0.151 | 3.145 | 1.082 |
| R8 | int8.r_walk − int8.r_cancel | 1.964 ± 0.326 | 1.809 | 1.086 |

Arm dips-kept: kept 2; S not scored; W not scored; T not scored

Arm leak0.545: kept 3; S not scored; W not scored; T not scored

Arm leak0.3803: kept 3; S not scored; W not scored; T not scored

Arm leak0: kept 5; S fp32 PASS, fp16 PASS, int8 PASS; W fp32 PASS, fp16 PASS, int8 PASS; T PASS
