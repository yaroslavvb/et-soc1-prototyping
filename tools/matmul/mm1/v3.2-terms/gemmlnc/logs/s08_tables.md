### Table 1. The 9 committed gemmLnc points and their rgm136 gemmL twins (measured; MM1-v3.1 in sample, given the measured op time)

| point | shape, format, card | measured W over idle: gemmLnc / twin | MM1-v3.1: gemmLnc / twin | measured / MM1-v3.1: gemmLnc / twin | wall cycles an op: gemmLnc / twin | excess over MM1-v3.1, nJ a minion-op |
|---|---|---|---|---|---|---|
| c01c (w01m) | gemmLnc2x3x2 fp32, aifoundry3 card 0 | 36.09 / 25.07 | 24.95 / 24.23 | 1.446 / 1.034 | 876.6 / 904.7 | 15.89 |
| c02c (w06m) | gemmLnc3x5x7 fp32, aifoundry3 card 0 | 25.15 / 19.14 | 22.22 / 19.65 | 1.132 / 0.974 | 1030.5 / 1173.6 | 4.91 |
| a087 (a088) | gemmLnc1x1x1 int8, aifoundry3 card 0 | 26.27 / 14.65 | 16.05 / 14.88 | 1.637 / 0.985 | 358.7 / 389.8 | 5.97 |
| a086 (a083) | gemmLnc1x1x44 fp32, aifoundry3 card 0 | 21.72 / 14.58 | 14.78 / 15.00 | 1.470 / 0.972 | 1666.7 / 1633.8 | 18.83 |
| a079 (a076) | gemmLnc1x6x5 fp32, aifoundry3 card 0 | 26.23 / 20.14 | 22.78 / 20.60 | 1.151 / 0.978 | 982.5 / 1092.6 | 5.51 |
| a075 (a006) | gemmLnc3x1x3 fp32, aifoundry3 card 0 | 39.18 / 24.77 | 24.70 / 23.93 | 1.586 / 1.035 | 880.3 / 910.6 | 20.75 |
| a082 (a030) | gemmLnc4x1x6 fp32, aifoundry3 card 0 | 23.08 / 15.97 | 16.77 / 16.31 | 1.376 / 0.979 | 1375.9 / 1416.0 | 14.12 |
| k40 (k41) | gemmLnc1x1x1 int8, aifoundry1 card 1 | 29.31 / 15.15 | 16.28 / 15.02 | 1.801 / 1.009 | 358.8 / 389.8 | 7.61 |
| k37 (k06) | gemmLnc3x1x3 fp32, aifoundry1 card 1 | 41.96 / 24.93 | 24.90 / 24.11 | 1.685 / 1.034 | 880.2 / 910.3 | 24.44 |

### Table 2. Where the excess goes: W over idle by rail, gemmLnc minus its twin (measured, post hoc; medians in the reducers' windows)

| point | shape | board | minion rail | SRAM rail | NoC rail | NoC rail, nJ a minion-op | SRAM rail, nJ a minion-op |
|---|---|---|---|---|---|---|---|
| c01c | 2x3x2 | +11.03 | +0.53 | +3.75 | +2.28 | +3.15 | +5.23 |
| c02c | 3x5x7 | +6.01 | +1.77 | +2.42 | +0.56 | +0.50 | +3.57 |
| a087 | 1x1x1 | +11.61 | +1.53 | +8.25 | +0.29 | +0.14 | +4.65 |
| a086 | 1x1x44 | +7.14 | -0.15 | +2.24 | +1.88 | +5.18 | +6.17 |
| a079 | 1x6x5 | +6.08 | +1.51 | +2.51 | +0.53 | +0.49 | +3.61 |
| a075 | 3x1x3 | +14.41 | +0.76 | +4.97 | +3.80 | +5.33 | +6.99 |
| a082 | 4x1x6 | +7.11 | +0.35 | +2.70 | +2.04 | +4.47 | +5.93 |
| k40 | 1x1x1 | +14.16 | +1.63 | +6.55 | +0.38 | +0.18 | +3.69 |
| k37 | 3x1x3 | +17.03 | +0.84 | +3.96 | +4.53 | +6.37 | +5.58 |

### Table 3. The walk (desk, exact streams; full mask): what the branch changes a shire-op

| shape | what | footprint MB | reads a shire-op, gemmL / gemmLnc (lines) | duplicates (lines) | desk L2 hits, gemmL / gemmLnc (lines) | duplicates hitting the desk L2 | chip L3 strict 32 MB, A / B in-L3 share (both kernels) |
|---|---|---|---|---|---|---|---|
| 2x3x2 | E211 c01c | 26 | 192 / 1,024 | 832 (A 448, B 384) | 16 / 848 | 1.000 | 1.000 / 1.000 |
| 3x5x7 | E211 c02c | 107 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.800 / 0.500 |
| 1x1x1 | E213 a087/k40 | 5 | 192 / 1,024 | 832 (A 448, B 384) | 192 / 1024 | 1.000 | 1.000 / 1.000 |
| 1x1x44 | E213 a086 | 134 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 0.000 |
| 1x6x5 | E213 a079 | 52 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 0.500 |
| 3x1x3 | E213 a075/k37 | 27 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 1.000 |
| 4x1x6 | E213 a082 | 62 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 1.000 |
| 2x2x2 | E213/E215 smoke s03/s14 | 20 | 192 / 1,024 | 832 (A 448, B 384) | 16 / 848 | 1.000 | 1.000 / 1.000 |
| 1x15x3 | E215 a024 (shape only) | 81 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 0.500 |
| 1x12x4 | E215 a026 (shape only) | 80 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 1.000 / 0.500 |
| 8x1x5 | E215 a031 (shape only) | 101 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 1.000 |
| 5x1x10 | E215 a032 (shape only) | 120 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 1.000 |
| 2x1x37 | E215 b013 (shape only) | 189 | 192 / 1,024 | 832 (A 448, B 384) | 0 / 832 | 1.000 | 0.000 / 0.000 |

### Table 4. The candidate terms (post hoc; W over idle errors in %, on the 9 points; MM1-v3.1 alone: rms 32.56%, mean -30.66%)

| form | x | constants, pJ a line | in sample | LOPO | LORO (12 runs) | LOEO E211 out | LOEO E213 out | E213 arm A out | card 1 out | aifoundry3 out |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | dup | 360.3 | 16.16 | 19.37 | 17.56 | 11.67 | 19.67 | 17.82 | 19.01 | 16.10 |
| F2 | dup + beyond | 261.4, 324.2 | 13.45 | 16.51 | 16.29 | 21.37 | 961.80 (NOT IDENTIFIED) | 13.34 | 15.40 | 27.95 |
| F3 | dup + first | 254.4, 552.1 | 7.99 | 9.81 | 9.63 | 10.05 | 100.71 (NOT IDENTIFIED) | 12.82 | 9.86 | 12.76 |
| F4 | beyond | 587.5 | 23.72 | 25.17 | 23.17 | 21.35 | 25.79 | 21.31 | 34.21 | 31.22 |

per-point errors, chosen form F3, in sample: [-8.649, 11.286, 4.645, 3.638, 8.536, 0.746, 13.632, -6.374, -6.14]; LOPO: [-9.284, 11.803, 8.547, 4.034, 8.962, 1.163, 15.979, -11.279, -9.373]

### Table 5. The frozen forecasts (MM1-v3.1 + gemmLnc term, form F3)

| id | arm, card | shape | NB | MM1-v3.1 W over idle | term W | **W over idle** | A, B (W, W us) for given() | J over idle a GEMM | J at rest a GEMM (rest law, T0) | planning peak W | stop | margin W | within 3 W |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a024 | A, aifoundry3 card 0 | gemmLnc1x15x3 | 15 | 19.554 | 3.978 | **23.531** | 0.9293, 44.2701 | 0.13274 | 0.27230 (24.74 W, 54.4 C) | 50.27 | 70 W x3 | 19.73 | no |
| a026 | A, aifoundry3 card 0 | gemmLnc1x12x4 | 12 | 19.456 | 4.112 | **23.568** | 0.9293, 44.2470 | 0.14151 | 0.29006 (24.74 W, 54.4 C) | 50.31 | 70 W x3 | 19.69 | no |
| a031 | A, aifoundry3 card 0 | gemmLnc8x1x5 | 1 | 16.582 | 9.314 | **25.896** | 0.9293, 57.8332 | 0.15356 | 0.30028 (24.74 W, 54.4 C) | 52.64 | 70 W x3 | 17.36 | no |
| a032 | A, aifoundry3 card 0 | gemmLnc5x1x10 | 1 | 16.446 | 9.308 | **25.754** | 0.9293, 57.5436 | 0.19103 | 0.37455 (24.74 W, 54.4 C) | 52.49 | 70 W x3 | 17.51 | no |
| b013 | B, aifoundry1 card 1 | gemmLnc2x1x37 | 1 | 16.577 | 8.461 | **25.038** | 1.4067, 59.9726 | 0.30094 | 0.68262 (31.76 W, 55.0 C) | 58.80 | 72 W x3 | 13.20 | no |
| s03 (smoke) | A, aifoundry3 card 0 | gemmLnc2x2x2 | 2 | 24.700 | 9.569 | **34.269** | 0.9118, 48.5198 | 0.02552 | 0.04395 (24.74 W, 54.4 C) | 61.01 | 70 W x3 | 8.99 | no |
| s14 (smoke) | B, aifoundry1 card 1 | gemmLnc2x2x2 | 2 | 25.278 | 9.523 | **34.802** | 1.3892, 48.5996 | 0.02592 | 0.04957 (31.76 W, 55.0 C) | 68.56 | 72 W x3 | 3.44 | no |

other forms beside (REPORTED): a024: F1 24.48, F2 27.55, F4 27.58 W (max-form peak 54.32 W); a026: F1 24.39, F2 27.47, F4 27.50 W (max-form peak 54.24 W); a031: F1 20.74, F2 23.35, F4 23.37 W (max-form peak 52.64 W); a032: F1 20.60, F2 23.20, F4 23.23 W (max-form peak 52.49 W); b013: F1 20.36, F2 22.72, F4 22.74 W (max-form peak 58.80 W); s03: F1 31.33, F2 35.25, F4 35.11 W (max-form peak 61.99 W); s14: F1 31.87, F2 35.78, F4 35.64 W (max-form peak 69.54 W, within 3 W)

held-out smokes (REPORTED): E213 A s03: est 34.90 W, v3.1 -29.4%, F3 -2.1%, analog E215 planning peak 61.64 W (margin 8.36 W); E213 B s14: est 36.66 W, v3.1 -31.9%, F3 -6.3%, analog E215 planning peak 70.42 W (margin 1.58 W)
