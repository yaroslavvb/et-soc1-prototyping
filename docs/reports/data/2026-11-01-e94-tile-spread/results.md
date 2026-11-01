# E94 scored (primary: dips removed, leak 0.2414)

Kept passes [9410, 9411, 9412], set aside [], leak {'mode': '0.2414', 'k_w_per_c': 0.2414, 'n_runs': -1}. Tally: {'PASS': 19, 'CORRECTION': 2, 'INCONCLUSIVE': 3, 'NO CORRECTION': 5, 'UNRESOLVED': 1}.

## What a kind costs (D over the type's zeros; the draw is the unit)

| rule | k | kind's mean, W | ± (draws) | between-draw SD τ, W [95%] | one tile's between-pass SD, W | τ / that | committed tile, W | offset, W | ± | R1 inside spread | R2 correction | share of random |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `fp32.sparse50` | 9 | 7.645 | 0.382 | 0.493 [0.329, 0.950] | 0.114 | 4.3 | 7.022 | -0.623 | 0.397 | PASS | CORRECTION | 0.317 |
| `fp16.nn_like` | 9 | 15.914 | 0.435 | 0.565 [0.381, 1.085] | 0.056 | 10.1 | 17.055 | +1.141 | 0.442 | PASS | CORRECTION | 0.738 |
| `fp16.uniform01` | 9 | 18.722 | 0.058 | 0.061 [0.024, 0.137] | 0.078 | 0.8 | 18.910 | +0.188 | 0.106 | INCONCLUSIVE | NO CORRECTION | 0.868 |
| `fp32.nn_like` | 6 | 12.351 | 0.582 | 0.552 [0.341, 1.360] | 0.105 | 5.2 | 12.804 | +0.452 | 0.603 | PASS | UNRESOLVED | 0.513 |
| `int8.sparse50` | 6 | 5.434 | 0.093 | 0.067 [0.000, 0.210] | 0.101 | 0.7 | 5.348 | -0.087 | 0.146 | PASS | NO CORRECTION | 0.784 |
| `fp32.randn` | 4 | 24.180 | 0.130 | 0.060 [0.000, 0.300] | 0.097 | 0.6 | 24.099 | -0.081 | 0.155 | PASS | NO CORRECTION | 1.003 |
| `fp16.randn` | 4 | 21.431 | 0.093 | 0.029 [0.000, 0.211] | 0.087 | 0.3 | 21.559 | +0.128 | 0.130 | INCONCLUSIVE | NO CORRECTION | 0.994 |
| `int8.full` | 4 | 6.962 | 0.019 | 0.000 [0.000, 0.037] | 0.042 | 0.0 | 6.928 | -0.034 | 0.057 | INCONCLUSIVE | NO CORRECTION | 1.005 |

## Rules

| rule | verdict | numbers | moved at the arms |
|---|---|---|---|
| E94-R1:fp32.sparse50 | **PASS** |  | none |
| E94-R2:fp32.sparse50 | **CORRECTION** |  | leak0.545 UNRESOLVED |
| E94-R1:fp16.nn_like | **PASS** |  | dips_kept INCONCLUSIVE |
| E94-R2:fp16.nn_like | **CORRECTION** |  | none |
| E94-R1:fp16.uniform01 | **INCONCLUSIVE** |  | none |
| E94-R2:fp16.uniform01 | **NO CORRECTION** |  | dips_kept UNRESOLVED |
| E94-R1:fp32.nn_like | **PASS** |  | none |
| E94-R2:fp32.nn_like | **UNRESOLVED** |  | none |
| E94-R1:int8.sparse50 | **PASS** |  | leak0 INCONCLUSIVE |
| E94-R2:int8.sparse50 | **NO CORRECTION** |  | leak0.545 UNRESOLVED; leak0 UNRESOLVED |
| E94-R1:fp32.randn | **PASS** |  | none |
| E94-R2:fp32.randn | **NO CORRECTION** |  | none |
| E94-R1:fp16.randn | **INCONCLUSIVE** |  | dips_kept PASS; leak0 PASS |
| E94-R2:fp16.randn | **NO CORRECTION** |  | none |
| E94-R1:int8.full | **INCONCLUSIVE** |  | none |
| E94-R2:int8.full | **NO CORRECTION** |  | leak0.545 UNRESOLVED |
| E94-R3:fp32.sparse50 | **PASS** | τ 0.493 [0.329, 0.950], expected 0.685 | none |
| E94-R3:fp16.nn_like | **PASS** | τ 0.565 [0.381, 1.085], expected 0.599 | none |
| E94-R3:fp32.nn_like | **PASS** | τ 0.552 [0.341, 1.360], expected 0.853 | none |
| E94-R3:int8.sparse50 | **PASS** | τ 0.067 [0.000, 0.210], expected 0.086 | none |
| E94-R4a | **PASS** | τ 0.055 [0.022, 0.105] against 0.3 | none |
| E94-R4b | **PASS** | τ 0.052 [0.000, 0.127] against 0.25 | none |
| E94-R5 | **PASS** | rms 0.243 W (no offset 0.682) | none |
| E94-R6 | **PASS** | rms 0.140 W (no offset 0.894) | none |
| E94-R7:gate_law | **PASS** | residual 0.109 of centred SD 0.585 W, ratio 0.19 | none |
| E94-R7:q130n | **PASS** | residual 0.103 of centred SD 0.585 W, ratio 0.18 | none |
| E94-R8 | **PASS** | rms 0.131 W (noise alone 0.113) | none |
| E94-R9:gate_law | **PASS** | rms 0.322 W | none |
| E94-R9:q130n | **PASS** | rms 0.382 W | dips_kept INCONCLUSIVE |
| E94-S1 | **PASS** |  | leak0.545 FAIL; leak0 FAIL |

## Every draw against the committed tile (W; frozen deltas beside)

| draw | gate share | bus bits/op | D(draw) − D(committed) | ±95% over passes | Q130(n) | gate law |
|---|---|---|---|---|---|---|
| `fp32.sparse50_e94d1` | 0.7119 | 80758 | +1.683 | 0.598 | +1.679 | +1.938 |
| `fp32.sparse50_e94d2` | 0.7476 | 75092 | +0.731 | 0.413 | +0.645 | +0.828 |
| `fp32.sparse50_e94d3` | 0.7590 | 74842 | +0.473 | 0.250 | +0.252 | +0.471 |
| `fp32.sparse50_e94d4` | 0.7532 | 78210 | +0.642 | 0.422 | +0.398 | +0.653 |
| `fp32.sparse50_e94d5` | 0.7612 | 76614 | +0.366 | 0.573 | +0.523 | +0.403 |
| `fp32.sparse50_e94d6` | 0.7837 | 75332 | -0.118 | 0.510 | -0.251 | -0.296 |
| `fp32.sparse50_e90d1` | 0.7449 | 80246 | +0.745 | 0.265 | +0.756 | +0.912 |
| `fp32.sparse50_e90d2` | 0.7407 | 72546 | +0.840 | 0.420 | +0.858 | +1.041 |
| `fp32.sparse50_e90d3` | 0.7634 | 73696 | +0.246 | 0.591 | +0.185 | +0.334 |
| `fp16.nn_like_e94d1` | 0.3086 | 79324 | -2.191 | 0.306 | -2.787 | -2.395 |
| `fp16.nn_like_e94d2` | 0.2656 | 80624 | -1.269 | 0.149 | -1.756 | -1.486 |
| `fp16.nn_like_e94d3` | 0.2266 | 83274 | -0.481 | 0.345 | -1.054 | -0.661 |
| `fp16.nn_like_e94d4` | 0.2812 | 81548 | -1.618 | 0.045 | -2.131 | -1.817 |
| `fp16.nn_like_e94d5` | 0.2773 | 82462 | -1.491 | 0.141 | -2.008 | -1.734 |
| `fp16.nn_like_e94d6` | 0.2422 | 82240 | -0.831 | 0.203 | -1.296 | -0.991 |
| `fp16.nn_like_e90d1` | 0.2305 | 81966 | -0.525 | 0.397 | -1.038 | -0.743 |
| `fp16.nn_like_e90d2` | 0.2344 | 81590 | -0.709 | 0.231 | -1.150 | -0.826 |
| `fp16.nn_like_e90d3` | 0.2500 | 80024 | -1.157 | 0.258 | -1.476 | -1.156 |
| `fp16.uniform01_e94d1` | 0.0000 | 76764 | -0.084 | 0.357 | -0.128 | +0.000 |
| `fp16.uniform01_e94d2` | 0.0000 | 75360 | -0.211 | 0.220 | +0.036 | +0.000 |
| `fp16.uniform01_e94d3` | 0.0000 | 75126 | -0.197 | 0.161 | -0.049 | +0.000 |
| `fp16.uniform01_e94d4` | 0.0000 | 75118 | -0.304 | 0.162 | -0.107 | +0.000 |
| `fp16.uniform01_e94d5` | 0.0000 | 75990 | -0.125 | 0.181 | +0.063 | +0.000 |
| `fp16.uniform01_e94d6` | 0.0000 | 74772 | -0.238 | 0.068 | -0.091 | +0.000 |
| `fp16.uniform01_e90d1` | 0.0000 | 74882 | -0.110 | 0.226 | -0.107 | +0.000 |
| `fp16.uniform01_e90d2` | 0.0000 | 76294 | -0.272 | 0.325 | -0.034 | +0.000 |
| `fp16.uniform01_e90d3` | 0.0000 | 74492 | -0.152 | 0.160 | -0.033 | +0.000 |
| `fp32.nn_like_e94d1` | 0.5508 | 79690 | -1.118 | 0.144 | -0.951 | -1.110 |
| `fp32.nn_like_e94d2` | 0.5273 | 80728 | -0.524 | 0.106 | -0.468 | -0.505 |
| `fp32.nn_like_e94d3` | 0.5469 | 79810 | -0.999 | 0.275 | -0.887 | -1.010 |
| `fp32.nn_like_e94d4` | 0.4883 | 81244 | +0.304 | 0.461 | +0.419 | +0.505 |
| `fp32.nn_like_e94d5` | 0.5273 | 82364 | -0.391 | 0.175 | -0.438 | -0.505 |
| `fp32.nn_like_e94d6` | 0.5000 | 79338 | +0.014 | 0.383 | +0.198 | +0.202 |
| `int8.sparse50_e94d1` | 0.0469 | 55280 | +0.192 | 0.034 | +0.197 | +0.132 |
| `int8.sparse50_e94d2` | 0.0547 | 51910 | +0.144 | 0.352 | +0.053 | +0.088 |
| `int8.sparse50_e94d3` | 0.0430 | 52352 | +0.096 | 0.312 | +0.067 | +0.154 |
| `int8.sparse50_e94d4` | 0.0815 | 50204 | -0.049 | 0.613 | -0.171 | -0.063 |
| `int8.sparse50_e94d5` | 0.0625 | 53378 | +0.123 | 0.402 | +0.076 | +0.044 |
| `int8.sparse50_e94d6` | 0.0469 | 53484 | +0.013 | 0.386 | +0.101 | +0.132 |
| `fp32.randn_e94d1` | 0.0000 | 82364 | +0.010 | 0.095 | -0.201 | +0.000 |
| `fp32.randn_e94d2` | 0.0000 | 82402 | +0.075 | 0.475 | -0.003 | +0.000 |
| `fp32.randn_e94d3` | 0.0000 | 81662 | +0.043 | 0.271 | -0.107 | +0.000 |
| `fp32.randn_e94d4` | 0.0000 | 85576 | +0.197 | 0.202 | +0.004 | +0.000 |
| `fp16.randn_e94d1` | 0.0000 | 83280 | -0.215 | 0.433 | +0.082 | +0.000 |
| `fp16.randn_e94d2` | 0.0000 | 83676 | -0.098 | 0.197 | +0.130 | +0.000 |
| `fp16.randn_e94d3` | 0.0000 | 84604 | -0.103 | 0.222 | +0.165 | +0.000 |
| `fp16.randn_e94d4` | 0.0000 | 84796 | -0.096 | 0.191 | +0.047 | +0.000 |
| `int8.full_e94d1` | 0.0000 | 69188 | +0.042 | 0.084 | -0.038 | +0.000 |
| `int8.full_e94d2` | 0.0000 | 70780 | +0.045 | 0.152 | +0.076 | +0.000 |
| `int8.full_e94d3` | 0.0000 | 70068 | +0.021 | 0.274 | +0.039 | +0.000 |
| `int8.full_e94d4` | 0.0000 | 69850 | +0.027 | 0.102 | +0.024 | +0.000 |

## The session tie

| cell | D, W | E82 dips removed, W | difference | band |
|---|---|---|---|---|
| `fp32.randn` | 24.099 ± 0.168 | 24.002 | 0.097 | ±0.5 |
| `fp16.randn` | 21.559 ± 0.125 | 21.490 | 0.069 | ±0.5 |
| `anchor_pi` | 8.118 ± 0.317 | 8.135 | -0.018 | ±0.5 |
| `int8.full` | 6.928 ± 0.064 | 6.839 | 0.089 | ±0.25 |
| `fp32.sparse50` | 7.022 ± 0.604 | 7.029 | -0.008 | ±0.5 |
| `fp16.nn_like` | 17.055 ± 0.305 | 17.010 | 0.045 | ±0.5 |
| `fp16.uniform01` | 18.910 ± 0.086 | 18.846 | 0.063 | ±0.5 |
| `fp32.nn_like` | 12.804 ± 0.205 | 12.720 | 0.084 | ±0.5 |
| `int8.sparse50` | 5.348 ± 0.177 | 5.235 | 0.112 | ±0.25 |

## The correction, row by row

| row | verdict | card 1: committed → kind's mean, W | aifoundry3: E78 → kind's mean, W | why |
|---|---|---|---|---|
| `fp32.sparse50` | CORRECTION | 7.022 → 7.645 ± 0.382 | 7.302 → 7.944 | E94-R8 PASS: the same draws moved alike on both cards |
| `fp16.nn_like` | CORRECTION | 17.055 → 15.914 ± 0.435 | 17.602 → 16.423 | E94-R8 PASS: the same draws moved alike on both cards |
| `fp16.uniform01` | NO CORRECTION | 18.910 → 18.722 ± 0.058 | 19.426 → 19.231 | E94-R8 PASS: the same draws moved alike on both cards |
| `fp32.nn_like` | UNRESOLVED | 12.804 → 12.351 ± 0.582 | 13.036, not translated | no draw of this rule was read on both cards |
| `int8.sparse50` | NO CORRECTION | 5.348 → 5.434 ± 0.093 | 5.463, not translated | no draw of this rule was read on both cards |
| `fp32.randn` | NO CORRECTION | 24.099 → 24.180 ± 0.130 | 24.725, not translated | no draw of this rule was read on both cards |
| `fp16.randn` | NO CORRECTION | 21.559 → 21.431 ± 0.093 | 22.162, not translated | no draw of this rule was read on both cards |
| `int8.full` | NO CORRECTION | 6.928 → 6.962 ± 0.019 | 7.056, not translated | no draw of this rule was read on both cards |
