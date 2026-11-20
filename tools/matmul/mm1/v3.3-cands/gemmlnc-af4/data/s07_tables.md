### Table 2. Every declared form: constants (all data), in sample, held out, the pooled guard, the placebo, the keep rule

| form | c1, c2 (pJ a line) | in sample rms (bias) | **LOEO** rms (bias) | LOCO rms (bias) | LOPO rms (bias) | pooled MM1 LOEO no twins | placebo wins / 100 | kept |
|---|---|---|---|---|---|---|---|---|
| F3r | 239.6, 396.2 | 8.34% (-0.12) | **8.69% (-0.22)** | 9.06% (+1.32) | 8.72% (-0.16) | 5.039% | 100 | comparator |
| F1r | 344.7 | 12.09% (-2.67) | **12.22% (-2.55)** | 12.14% (-2.40) | 12.55% (-2.52) | 5.178% | n/a | no |
| F2r | 263.2, 130.4 | 11.45% (-1.12) | **12.38% (+0.11)** | 11.89% (-0.34) | 12.01% (-1.01) | 5.186% | 41 | no |
| F4r | 393.9 | 15.19% (-3.46) | **15.45% (-3.11)** | 15.36% (-2.76) | 15.45% (-3.42) | 5.345% | 0 | no |
| STEPr | 259.4, 324.5 | 8.26% (-0.20) | **9.05% (-0.21)** | 9.19% (-0.16) | 8.62% (-0.19) | 5.051% | 100 | no |
| AF1 | 224.7, 676.0 | 5.54% (+0.54) | **6.78% (+0.41)** | 6.50% (+2.08) | 5.96% (+0.44) | 4.982% | 100 | **KEPT** |
| AF2 | 221.0, 600.4 | 4.23% (+0.59) | **5.58% (+0.23)** | 5.40% (+2.18) | 4.77% (+0.49) | 4.953% | 100 | **KEPT** |
| AF3 | 245.9, 661.2 | 5.16% (+0.20) | **5.65% (+0.25)** | 6.21% (+1.82) | 5.48% (+0.18) | 4.955% | 100 | **KEPT** |
| **AF4** | 236.3, 597.3 | 3.23% (+0.37) | **3.88% (+0.14)** | 4.65% (+2.03) | 3.71% (+0.33) | 4.921% | 100 | **KEPT** |

MM1-v3.2 as landed (F3 at c1 247.7, c2 448.6 pJ): pooled 5.048% (n 1851; its own record 4.976%, n 1829, plus the 22 E216 and E218 gemmLnc points at its frozen forecasts).

### Table 3. Held out by fold: rms (bias) over each fold's gemmLnc points, W over idle given the measured op time

| fold | n | MM1-v3.2 as landed | F3r (F3 refitted) | AF1 | AF2 | AF3 | **AF4** |
|---|---|---|---|---|---|---|---|
| LOEO E211 | 2 | 10.15 (-1.44) | 10.44 (-2.75) | 11.06 (-3.35) | 9.19 (+8.93) | 13.80 (-8.54) | **8.45 (+6.96)** |
| LOEO E213 | 7 | 8.68 (-4.90) | 8.92 (-5.55) | 11.43 (-8.48) | 8.99 (-5.76) | 8.62 (-5.31) | **5.79 (-3.37)** |
| LOEO E215 | 5 | 7.23 (+4.62) | 5.58 (+0.90) | 2.13 (-0.05) | 3.23 (-1.81) | 2.47 (+0.95) | **2.96 (-0.97)** |
| LOEO E216 | 10 | 5.52 (+4.47) | 5.08 (+3.85) | 3.71 (+3.22) | 3.10 (+2.31) | 2.30 (+2.25) | **1.54 (+1.37)** |
| LOEO E218 | 12 | 11.48 (+0.54) | 11.29 (-0.56) | 5.28 (+4.08) | 4.46 (+1.40) | 3.70 (+2.99) | **2.84 (+0.50)** |
| LOEO E212 | 0 | no gemmLnc point: the term is 0 at every point of the fold, so the fold equals MM1-v3.2 there | | | | | |
| LOEO E214 | 0 | no gemmLnc point: the term is 0 at every point of the fold, so the fold equals MM1-v3.2 there | | | | | |
| LOEO E217 | 0 | no gemmLnc point: the term is 0 at every point of the fold, so the fold equals MM1-v3.2 there | | | | | |
| LOEO E219 | 0 | no gemmLnc point: the term is 0 at every point of the fold, so the fold equals MM1-v3.2 there | | | | | |
| **LOEO, all 36** | 36 | 8.95 (+1.03) | 8.69 (-0.22) | 6.78 (+0.41) | 5.58 (+0.23) | 5.65 (+0.25) | **3.88 (+0.14)** |
| LOCO aifoundry3 card 0 | 23 | 9.67 (+1.13) | 9.75 (+2.07) | 6.07 (+3.46) | 5.18 (+3.69) | 6.36 (+3.26) | **4.74 (+3.70)** |
| LOCO aifoundry1 card 1 | 3 | 11.91 (-11.22) | 13.02 (-12.88) | 13.37 (-12.24) | 10.58 (-9.82) | 11.67 (-10.62) | **8.93 (-8.53)** |
| LOCO aifoundry2 card 0 | 10 | 5.52 (+4.47) | 5.08 (+3.85) | 3.71 (+3.22) | 3.10 (+2.31) | 2.30 (+2.25) | **1.54 (+1.37)** |

MM1-v3.2 as landed: its own LOEO fold forecasts at the 14 points in its fit (E211, E213, E215), and its frozen forecasts at the measured op time at E216's and E218's 22 points (outside its fit).

### Table 4. Every gemmLnc point: the features, the measured W over idle, and the held-out errors (forecast / measured - 1, %)

| point | token | card | NB | R4 | first | measured W | MM1-v3.2 as landed | F3r LOEO | **AF4 LOEO** | AF4 LOCO | AF4 in sample |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E211|c01c | gemmLnc2x3x2 | aifoundry3 card 0 | 3 | 25.0 | 8.34 | 36.09 | -11.5 | -12.8 | **+11.7** | +14.7 | +10.2 |
| E211|c02c | gemmLnc3x5x7 | aifoundry3 card 0 | 5 | 0.0 | 5.20 | 25.15 | +8.6 | +7.3 | **+2.2** | +3.9 | +2.2 |
| E213|a3|a087 | gemmLnc1x1x1 | aifoundry3 card 0 | 1 | 0.0 | 0.00 | 26.27 | -4.6 | -1.3 | **-3.7** | +5.1 | +0.6 |
| E213|a3|a086 | gemmLnc1x1x44 | aifoundry3 card 0 | 1 | 21.7 | 26.00 | 21.72 | -3.9 | -7.3 | **-1.4** | +2.5 | -1.1 |
| E213|a3|a079 | gemmLnc1x6x5 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 26.23 | +4.0 | +4.3 | **-0.4** | +2.8 | +1.2 |
| E213|a3|a075 | gemmLnc3x1x3 | aifoundry3 card 0 | 1 | 26.0 | 26.00 | 39.18 | -7.2 | -9.8 | **+1.3** | +5.7 | +1.4 |
| E213|a3|a082 | gemmLnc4x1x6 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 23.08 | +5.4 | +2.5 | **-0.0** | +3.8 | +0.7 |
| E213|c1|k40 | gemmLnc1x1x1 | aifoundry1 card 1 | 1 | 0.0 | 0.00 | 29.31 | -14.5 | -11.5 | **-13.6** | -12.3 | -9.8 |
| E213|c1|k37 | gemmLnc3x1x3 | aifoundry1 card 1 | 1 | 26.0 | 26.00 | 41.96 | -13.6 | -15.8 | **-5.7** | -6.4 | -5.5 |
| E215|a3|a026 | gemmLnc1x12x4 | aifoundry3 card 0 | 12 | 0.0 | 2.17 | 25.77 | +5.5 | +3.6 | **+1.2** | +2.8 | +1.2 |
| E215|a3|a024 | gemmLnc1x15x3 | aifoundry3 card 0 | 15 | 0.0 | 1.73 | 26.30 | +4.1 | +2.4 | **+0.4** | +1.9 | +0.3 |
| E215|a3|a032 | gemmLnc5x1x10 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 22.86 | +10.2 | +4.8 | **+0.5** | +4.0 | +0.8 |
| E215|a3|a031 | gemmLnc8x1x5 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 23.23 | +8.9 | +3.7 | **-0.6** | +2.8 | -0.3 |
| E215|c1|b013 | gemmLnc2x1x37 | aifoundry1 card 1 | 1 | 21.6 | 26.00 | 24.80 | -5.6 | -10.0 | **-6.4** | -6.9 | -6.0 |
| E216|a2c0|g01 | gemmLnc1x2x12 | aifoundry2 card 0 | 2 | 0.0 | 13.00 | 36.24 | +12.4 | +11.5 | **+2.7** | +2.7 | +2.5 |
| E216|a2c0|g02 | gemmLnc2x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.81 | +1.6 | +0.8 | **+0.5** | +0.5 | +0.4 |
| E216|a2c0|g03 | gemmLnc4x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.41 | +2.4 | +1.6 | **+1.4** | +1.4 | +1.3 |
| E216|a2c0|g04 | gemmLnc5x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.55 | +2.1 | +1.2 | **+1.0** | +1.0 | +0.9 |
| E216|a2c0|g05 | gemmLnc6x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.91 | +1.5 | +0.7 | **+0.5** | +0.5 | +0.4 |
| E216|a2c0|g06 | gemmLnc7x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.80 | +1.6 | +0.8 | **+0.6** | +0.6 | +0.5 |
| E216|a2c0|g07 | gemmLnc3x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 37.77 | +5.1 | +4.8 | **+1.1** | +1.1 | +0.9 |
| E216|a2c0|g08 | gemmLnc4x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 37.95 | +5.7 | +5.4 | **+1.7** | +1.7 | +1.5 |
| E216|a2c0|g09 | gemmLnc5x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 38.05 | +5.9 | +5.6 | **+1.9** | +1.9 | +1.7 |
| E216|a2c0|g10 | gemmLnc6x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 37.83 | +6.3 | +6.0 | **+2.2** | +2.2 | +2.0 |
| E218|a3|g01 | gemmLnc2x6x8 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 25.12 | +5.9 | +4.8 | **+1.0** | +2.1 | +0.5 |
| E218|a3|g02 | gemmLnc2x6x7 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 25.54 | +5.6 | +4.6 | **+0.8** | +1.9 | +0.3 |
| E218|a3|g03 | gemmLnc2x5x8 | aifoundry3 card 0 | 5 | 0.0 | 5.20 | 24.02 | +11.2 | +10.1 | **+5.2** | +6.4 | +4.7 |
| E218|a3|g04 | gemmLnc7x5x14 | aifoundry3 card 0 | 5 | 20.1 | 5.20 | 21.89 | -19.4 | -20.2 | **-4.0** | -0.2 | -3.6 |
| E218|a3|g05 | gemmLnc8x6x3 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 26.81 | +7.9 | +6.8 | **+3.0** | +4.1 | +2.5 |
| E218|a3|g06 | gemmLnc1x14x4 | aifoundry3 card 0 | 14 | 0.0 | 1.86 | 25.98 | +3.7 | +2.8 | **+1.6** | +2.7 | +1.0 |
| E218|a3|g07 | gemmLnc1x13x4 | aifoundry3 card 0 | 13 | 0.0 | 2.00 | 26.11 | +3.6 | +2.6 | **+1.3** | +2.4 | +0.7 |
| E218|a3|g08 | gemmLnc2x14x16 | aifoundry3 card 0 | 14 | 20.5 | 1.86 | 22.57 | -23.7 | -24.4 | **-5.8** | -2.0 | -5.3 |
| E218|a3|g09 | gemmLnc5x1x3 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 22.78 | +9.1 | +7.6 | **+1.7** | +5.1 | +2.0 |
| E218|a3|g10 | gemmLnc2x1x12 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 22.79 | +8.2 | +6.7 | **+0.9** | +4.3 | +1.1 |
| E218|a3|g11 | gemmLnc6x2x48 | aifoundry3 card 0 | 2 | 24.1 | 13.00 | 19.64 | -12.7 | -13.6 | **+0.5** | +4.9 | +1.1 |
| E218|a3|g12 | gemmLnc5x1x8 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 23.04 | +7.1 | +5.6 | **-0.2** | +3.2 | +0.1 |

The cooperative twins (term 0 for every form; MM1-v3.2 at the measured op time): n 30, rms 2.69%, bias +1.27%.

### Table 6. The frozen E220 forecasts at its gemmLnc points (arm A at 600 MHz, arm B at 799 MHz; every cooperative point equals MM1-v3.2)

| arm | id | token | R4 regime | MM1-v3.2 W over idle | F3 in it | AF4 term | **MM1-v3.2 + AF4 W over idle** | J over idle a GEMM, t forecast | J at rest a GEMM | planning peak, plain / E220 form | stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | xg01 | gemmLnc2x6x8 | none (R4 0), R4 0.0 | 24.16 | 4.40 | 3.23 | **22.98** | 0.2754 | 0.6558 | 56.7 / 60.6 | 72 |
| A | xg02 | gemmLnc2x6x7 | none (R4 0), R4 0.0 | 24.45 | 4.46 | 3.27 | **23.26** | 0.2406 | 0.5691 | 57.0 / 60.9 | 72 |
| A | xg03 | gemmLnc2x5x8 | none (R4 0), R4 0.0 | 24.19 | 4.57 | 3.20 | **22.82** | 0.2298 | 0.5496 | 56.6 / 60.4 | 72 |
| A | xg04 | gemmLnc7x5x14 | near reuse misses the L3, R4 20.1 | 20.38 | 3.66 | 7.57 | **24.29** | 1.871 | 4.318 | 58.1 / 62.1 | 72 |
| A | xg05 | gemmLnc8x6x3 | none (R4 0), R4 0.0 | 25.90 | 4.72 | 3.46 | **24.64** | 0.4131 | 0.9455 | 58.4 / 62.6 | 72 |
| A | xg06 | gemmLnc1x14x4 | none (R4 0), R4 0.0 | 25.15 | 4.09 | 3.46 | **24.51** | 0.16 | 0.3672 | 58.3 / 62.4 | 72 |
| A | xg07 | gemmLnc1x13x4 | none (R4 0), R4 0.0 | 25.22 | 4.13 | 3.46 | **24.54** | 0.1485 | 0.3406 | 58.3 / 62.4 | 72 |
| A | xg08 | gemmLnc2x14x16 | near reuse misses the L3, R4 20.5 | 19.71 | 3.02 | 7.64 | **24.33** | 1.722 | 3.97 | 58.1 / 62.2 | 72 |
| A | xg09 | gemmLnc5x1x3 | A fresh into the row, R4 14.0 | 25.97 | 8.27 | 6.63 | **24.32** | 0.05233 | 0.1207 | 58.1 / 62.2 | 72 |
| A | xg10 | gemmLnc2x1x12 | A fresh into the row, R4 14.0 | 24.78 | 7.95 | 6.38 | **23.21** | 0.08314 | 0.1969 | 57.0 / 60.9 | 72 |
| A | xg11 | gemmLnc6x2x48 | near reuse misses the L3, R4 24.1 | 21.53 | 4.94 | 8.27 | **24.86** | 2.333 | 5.313 | 58.6 / 62.8 | 72 |
| A | xg12 | gemmLnc5x1x8 | A fresh into the row, R4 14.0 | 24.84 | 7.95 | 6.37 | **23.26** | 0.1388 | 0.3283 | 57.0 / 60.9 | 72 |
| A | n01 | gemmLnc1x6x48 | near reuse misses the L3, R4 24.1 | 19.96 | 3.37 | 8.27 | **24.86** | 1.166 | 2.656 | 58.6 / 62.8 | 72 |
| A | n02 | gemmLnc2x6x24 | near reuse misses the L3, R4 23.8 | 20.00 | 3.38 | 8.21 | **24.83** | 1.162 | 2.647 | 58.6 / 62.8 | 72 |
| A | n03 | gemmLnc2x6x28 | near reuse misses the L3, R4 23.8 | 19.99 | 3.38 | 8.22 | **24.83** | 1.355 | 3.089 | 58.6 / 62.8 | 72 |
| A | n04 | gemmLnc2x6x32 | near reuse misses the L3, R4 23.8 | 19.99 | 3.38 | 8.22 | **24.82** | 1.549 | 3.53 | 58.6 / 62.8 | 72 |
| A | n05 | gemmLnc1x6x40 | near reuse misses the L3, R4 23.8 | 19.98 | 3.38 | 8.22 | **24.82** | 0.9677 | 2.206 | 58.6 / 62.8 | 72 |
| A | n06 | gemmLnc2x6x20 | near reuse misses the L3, R4 23.1 | 20.04 | 3.40 | 8.10 | **24.74** | 0.9592 | 2.191 | 58.5 / 62.7 | 72 |
| A | n07 | gemmLnc4x6x16 | near reuse misses the L3, R4 20.5 | 20.17 | 3.48 | 7.64 | **24.33** | 1.476 | 3.403 | 58.1 / 62.2 | 72 |
| B | xg04 | gemmLnc7x5x14 | near reuse misses the L3, R4 20.1 | 34.83 | 4.39 | 9.08 | **39.52** | 2.857 | 4.534 | 64.7 / 71.4 | 70 |
| B | xg08 | gemmLnc2x14x16 | near reuse misses the L3, R4 20.5 | 33.99 | 3.62 | 9.17 | **39.54** | 2.627 | 4.168 | 64.7 / 71.4 | 70 |
| B | n01 | gemmLnc1x6x48 | near reuse misses the L3, R4 24.1 | 34.15 | 4.05 | 9.93 | **40.03** | 1.763 | 2.785 | 65.2 / 72.0 | 70 |
| B | n02 | gemmLnc2x6x24 | near reuse misses the L3, R4 23.8 | 34.21 | 4.06 | 9.86 | **40.01** | 1.757 | 2.776 | 65.2 / 71.9 | 70 |
| B | n03 | gemmLnc2x6x28 | near reuse misses the L3, R4 23.8 | 34.20 | 4.06 | 9.86 | **40.00** | 2.05 | 3.239 | 65.2 / 71.9 | 70 |
| B | n04 | gemmLnc2x6x32 | near reuse misses the L3, R4 23.8 | 34.19 | 4.06 | 9.86 | **40.00** | 2.343 | 3.701 | 65.2 / 71.9 | 70 |
| B | n05 | gemmLnc1x6x40 | near reuse misses the L3, R4 23.8 | 34.18 | 4.06 | 9.86 | **39.99** | 1.464 | 2.313 | 65.2 / 71.9 | 70 |
| B | n06 | gemmLnc2x6x20 | near reuse misses the L3, R4 23.1 | 34.28 | 4.08 | 9.72 | **39.92** | 1.453 | 2.297 | 65.1 / 71.8 | 70 |
| B | n07 | gemmLnc4x6x16 | near reuse misses the L3, R4 20.5 | 34.54 | 4.17 | 9.17 | **39.54** | 2.252 | 3.573 | 64.7 / 71.4 | 70 |
