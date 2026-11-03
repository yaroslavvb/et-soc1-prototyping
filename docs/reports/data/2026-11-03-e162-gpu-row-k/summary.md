## The L40S smoke (bf16, one 5 s window each)

Board `6aceaa9c621a`, enforced 350 W, NVML maximum 2520 MHz; held clock: None (none: bf16 zeros at 1024^3 did not hold the NVML maximum and carried a reason bit); verdict: cap-bound or clock-bound: the L40S arm stops.

| size | random W | random MHz | random TFLOPS | zeros W | zeros MHz | zeros TFLOPS | reason bits |
|---|---:|---:|---:|---:|---:|---:|---|
| 1024³ | 345.8 | 2190–2310 | 150.9 | 227.2 | 2475–2490 | 154.1 | 0x4 / 0x4 in 100% / 100% of samples |
| 1536³ | 340.1 | 2145–2160 | 146.1 | 223.7 | 2385–2400 | 143.3 | 0x4 / 0x4 in 100% / 100% of samples |
| 2048³ | 349.6 | 1875–1905 | 222.7 | 226.5 | 2235–2235 | 261.0 | 0x4 / 0x4 in 100% / 100% of samples |
| 3072³ | 321.4 | 2235–2235 | 191.8 | 209.7 | 2445–2445 | 185.1 | 0x4 / 0x4 in 100% / 100% of samples |
| 4096³ | 349.5 | 1740–1770 | 220.0 | 240.3 | 2175–2190 | 272.2 | 0x4 / 0x4 in 100% / 100% of samples |

## A100 stage 1: y (W over zeros, this session's boards), ± SE over 2 boards × 2 passes

| b | 1 | 2 | 4 | 8 | 16 | 32 | 64 |
|---|---:|---:|---:|---:|---:|---:|---:|
| K wave, shared phase (`kS`) | 28.9 ± 0.8 | 28.1 ± 0.9 | 24.3 ± 1.9 | 51.1 ± 0.8 | 52.4 ± 1.1 | 36.5 ± 1.3 | 35.6 ± 2.7 |
| K wave, phase per row (E149's `sq`) | 72.9 ± 1.5 | — | — | — | 90.9 ± 2.0 | — | 83.6 ± 3.0 |
| row wave, shared phase (`rS`) | 97.5 ± 2.5 | 61.3 ± 1.6 | 67.7 ± 1.2 | 48.5 ± 0.9 | 47.1 ± 0.6 | 38.4 ± 1.9 | 37.1 ± 0.6 |

| kind | y |
|---|---:|
| `bf16.rC16` | 70.5 ± 1.1 |
| `bf16.rowc` | 128.8 ± 2.9 |
| `bf16.colc` | 69.9 ± 1.3 |
| `bf16.rowcA_colcB` | 134.8 ± 4.3 |
| `bf16.colcA_rowcB` | 75.2 ± 1.9 |
| `bf16.rollM` | 116.1 ± 2.6 |
| `bf16.drollK` | 143.9 ± 3.8 |
| `bf16.dsortK` | 99.6 ± 2.0 |
| `bf16.dshufK` | 155.1 ± 3.3 |
| `bf16.dsortM` | 93.4 ± 2.1 |
| `bf16.kS1A` | 25.1 ± 2.0 |
| `bf16.kS1B` | 24.1 ± 1.2 |
| `bf16.rS1A` | 88.1 ± 1.9 |
| `bf16.rS1B` | 20.9 ± 1.3 |
| `bf16.randn` | 154.7 ± 3.9 |
| `bf16.mk3` | 100.2 ± 1.5 |
| `fp16.kS1` | 27.9 ± 0.7 |
| `fp16.kS16` | 39.5 ± 1.8 |
| `fp16.rS1` | 78.8 ± 2.5 |
| `fp16.rS16` | 44.6 ± 1.6 |
| `fp16.rowc` | 108.1 ± 3.3 |
| `fp16.colc` | 63.5 ± 2.1 |
| `fp16.randn` | 123.4 ± 4.2 |
| `fp16.mk5` | 91.8 ± 3.0 |
| `int8.kS1` | 27.1 ± 1.3 |
| `int8.kS16` | 33.8 ± 2.2 |
| `int8.rS1` | 51.1 ± 2.4 |
| `int8.rS16` | 31.9 ± 2.6 |
| `int8.rowc` | 71.9 ± 2.7 |
| `int8.colc` | 50.6 ± 2.7 |
| `int8.rand` | 83.8 ± 2.7 |
| `int8.k3` | 75.4 ± 3.0 |

## The fit (A100, pooled rows on E149's stage-1 footing)

Rows: {'bf16': 75, 'fp16': 26, 'int8': 24}; session scale c (E162 y over E149 y on the bridge kinds): bf16 0.9950 (n 9, rms diff 1.5 W), fp16 0.9858 (n 2, rms diff 1.6 W), int8 0.9893 (n 2, rms diff 1.1 W); E149 rows left out: none.

RK chose K-lag s = 8, row-lag r = 1. Scan (pooled LOKO rms, W), the best 8:

| (s, r) | pooled | bf16 | fp16 | int8 |
|---|---:|---:|---:|---:|
| (8,1) | 12.40 | 12.36 | 13.09 | 11.71 |
| (4,1) | 13.15 | 13.99 | 11.87 | 11.68 |
| (32,1) | 13.34 | 13.93 | 12.38 | 12.43 |
| (2,1) | 13.47 | 14.36 | 12.09 | 11.94 |
| (16,1) | 13.74 | 12.83 | 16.67 | 12.94 |
| (1,1) | 15.66 | 15.12 | 18.42 | 13.98 |
| (8,4) | 16.06 | 16.83 | 16.37 | 12.91 |
| (8,2) | 16.15 | 16.95 | 16.46 | 12.96 |

| model | bf16 in · nested | fp16 in · nested | int8 in · nested |
|---|---|---|---|
| RK (ridge; nested = fully nested) | 10.13 · 13.94 | 8.70 · 15.40 | 9.65 · 12.66 |
| RK form by OLS at (s, r) | 10.01 · 12.87 | 6.51 · 112.30 | 6.87 · 37.48 |
| G1p (G1's form, OLS) | 29.33 · 33.49 | 28.80 · 132.84 | 19.64 · 30.98 |
| G4p (G4's form, lag 2, OLS) | 14.06 · 18.04 | 7.14 · 37.13 | 7.80 · 13.89 |

STABLE: **HOLDS** — bf16: nested 13.94 / in 10.13 = 1.38; fp16: nested 15.40 / in 8.70 = 1.77; int8: nested 12.66 / in 9.65 = 1.31; pooled nested 14.03 against G1's form 67.29 W.

E149's frozen G1 on E162's 36 new stage-1 kinds (never in its fit): 58.5 W rms, bias -4.6 W.

RK's coefficients (W per unit of each feature, E149's footing):

- bf16 (λ 0.03): nzprod +28.3, gtr -16.8, gtrR -7.1, flip_sign +4.3, flip_exp +3.9, flip_mant +2.9, pos_exp -3.2, pos_mant -22.4, asym -0.6, psgn +20.6, rflip_sign +19.5, rflip_exp +5.9, rflip_mant +6.0, rasym +4.7
- fp16 (λ 0.1): nzprod +18.3, gtr +2.1, gtrR +3.5, flip_sign -1.3, flip_exp +1.6, flip_mant +3.3, pos_mant -1.3, asym +0.6, psgn +2.8, rflip_sign +22.1, rflip_exp +5.7, rflip_mant +3.4, rasym +0.0
- int8 (λ 0.3): nzprod +10.8, gtr +0.6, gtrR +12.5, flip_sign +4.8, flip_high +4.1, flip_low +3.4, asym -1.0, psgn +9.4, rflip_sign +12.1, rflip_high +3.9, rflip_low +3.8, rasym -1.0

## Which pairing (stage 1 rules)

- **W1** HOLDS: a phase per row costs more than one shared phase (square waves along K, b = 1, 16, 64): bf16.sq1 − bf16.kS1 = +44.0 ± 1.7 W; bf16.sq16 − bf16.kS16 = +38.5 ± 2.2 W; bf16.sq64 − bf16.kS64 = +48.0 ± 4.0 W
- **W2** FAILS: with no row flips, neighbours along K are a pairing (b = 1 costs more than b = 64): bf16.kS1 − bf16.kS64 = -6.7 ± 2.8 W
- **W3** HOLDS: with no K flips, neighbouring rows are a pairing (b = 1 costs more than b = 64): bf16.rS1 − bf16.rS64 = +60.4 ± 2.6 W
- **W5** ROW>K: rows random with K smooth (drollK) against K random with rows smooth (rollM): bf16.drollK − bf16.rollM = +27.9 ± 4.6 W
- **R4b** FAILS: E149's R4b again: with a phase per row, period 2 along K costs more than period 128: bf16.sq1 − bf16.sq64 = -10.8 ± 3.3 W
- **W4** bf16: ROW>K (rowc − colc = +58.9 ± 3.2 W)
- **W4** fp16: ROW>K (rowc − colc = +44.6 ± 3.9 W)
- **W4** int8: ROW>K (rowc − colc = +21.3 ± 3.8 W)
- W6 kS1: UNRESOLVED (A only − B only = +0.9 ± 2.3 W)
- W6 rS1: A>B (A only − B only = +67.2 ± 2.2 W)

## Stage 2, blind: the held-out kinds on new boards

Boards: A d31f897269bd (NVIDIA A100-SXM4-40GB), B 80d5c1565177 (NVIDIA A100-SXM4-40GB); refused: none.

| kind | measured y ± SE | RK | G1 (E149) | G1p | G4p | E149 G4 | RK band | inside |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `bf16.cdup8` | 148.2 ± 4.4 | 159.5 | 50.6 | 55.3 | 123.0 | 158.2 | ±22.9 | yes |
| `bf16.checkv` | 94.3 ± 2.0 | 112.4 | 135.7 | 84.6 | 119.8 | 137.8 | ±22.9 | yes |
| `bf16.kB8_4` | 49.5 ± 1.0 | 33.3 | 60.4 | 54.5 | 48.9 | 33.8 | ±22.9 | yes |
| `bf16.rdup8` | 85.2 ± 2.6 | 88.9 | 158.6 | 132.1 | 87.1 | 80.3 | ±22.9 | yes |
| `bf16.rollM_A` | 113.6 ± 2.0 | 104.7 | 158.7 | 132.3 | 124.7 | 122.3 | ±22.9 | yes |
| `bf16.sinpos` | 113.6 ± 3.4 | 93.8 | 134.0 | 106.5 | 91.1 | 90.7 | ±22.9 | yes |
| `bf16.stripeK0` | 104.7 ± 2.4 | 79.8 | 207.1 | 233.7 | 79.1 | 79.1 | ±22.9 | no |
| `bf16.stripeR0` | 109.1 ± 2.4 | 156.8 | 75.7 | 62.4 | 166.3 | 149.3 | ±22.9 | no |
| `bf16.t16x16` | 56.0 ± 1.3 | 58.6 | 43.0 | 49.9 | 41.0 | 75.2 | ±22.9 | yes |
| `bf16.t32x4` | 78.4 ± 1.6 | 81.2 | 66.0 | 66.3 | 56.0 | 72.0 | ±22.9 | yes |
| `bf16.t4x32` | 67.1 ± 1.4 | 60.9 | 39.1 | 47.1 | 53.2 | 70.3 | ±22.9 | yes |
| `bf16.walk2` | 118.2 ± 2.8 | 99.7 | 122.9 | 106.9 | 94.2 | 102.6 | ±22.9 | yes |
| `bf16.walkK` | 159.8 ± 3.3 | 159.1 | 119.9 | 109.5 | 160.5 | 155.7 | ±22.9 | yes |
| `bf16.walkR` | 130.9 ± 2.9 | 125.3 | 195.9 | 173.8 | 131.2 | 140.5 | ±22.9 | yes |
| `fp16.cdup8` | 121.7 ± 3.8 | 127.6 | 28.7 | 41.7 | 107.6 | 130.1 | ±25.3 | yes |
| `fp16.rdup8` | 75.8 ± 2.7 | 64.7 | 132.8 | 89.7 | 63.1 | -1174.4 | ±25.3 | yes |
| `fp16.t16x16` | 51.3 ± 1.7 | 41.3 | 21.3 | 38.3 | 29.0 | -1263.0 | ±25.3 | yes |
| `fp16.walkK` | 123.7 ± 3.9 | 130.0 | 89.5 | 61.7 | 147.6 | 1729.2 | ±25.3 | yes |
| `int8.cdup8` | 83.0 ± 3.6 | 85.0 | 14.5 | 31.3 | 57.2 | 90.8 | ±20.8 | yes |
| `int8.rdup8` | 59.7 ± 4.9 | 50.8 | 92.7 | 70.0 | 62.3 | 40.1 | ±20.8 | yes |
| `int8.t16x16` | 50.9 ± 3.6 | 30.6 | 8.9 | 28.5 | 21.9 | 43.3 | ±20.8 | yes |
| `int8.walkK` | 77.8 ± 4.2 | 69.9 | 45.5 | 38.6 | -749.0 | -806.1 | ±20.8 | yes |

| model | rms W | bias W | worst W | bf16 rms | fp16 rms | int8 rms | board-scaled rms |
|---|---:|---:|---:|---:|---:|---:|---:|
| RK | 15.65 | +2.68 | 47.7 | 17.98 | 8.64 | 11.84 | 15.82 |
| e149_S1 | 36.07 | -12.08 | 79.8 | 41.26 | 32.16 | 12.80 | 36.64 |
| e149_G0 | 45.72 | +30.74 | 89.3 | 47.78 | 54.66 | 22.77 | 45.37 |
| G1p | 47.98 | +11.72 | 129.0 | 50.17 | 51.47 | 34.70 | 48.26 |
| e149_G1s | 49.98 | -21.56 | 97.5 | 55.47 | 47.88 | 26.07 | 50.85 |
| G1 | 52.35 | +3.24 | 102.4 | 51.92 | 59.11 | 46.35 | 52.89 |
| G4p | 177.59 | +43.49 | 826.8 | 22.90 | 18.91 | 413.84 | 179.77 |
| e149_G4 | 550.04 | +82.49 | 1605.5 | 20.53 | 1211.23 | 442.09 | 556.20 |
| e149_G3 | 2035.36 | -523.53 | 7880.5 | 27.88 | 2693.67 | 3940.34 | 2057.55 |

- **BEAT** HOLDS: rms RK 15.65 against 52.35 W (ratio 0.299, bar 0.8); difference +36.71 W, paired bootstrap 95% [+22.11, +50.08] over 22 kinds
- **BEAT_p** HOLDS: rms RK 15.65 against 47.98 W (ratio 0.326, bar 0.8); difference +32.33 W, paired bootstrap 95% [+14.81, +48.46] over 22 kinds
- **STABLE** HOLDS (stage 1)
- **HT1** HOLDS: cell die rise over its references, rms RK 1.276 °C, G1 3.334 °C, measured power 0.694 °C
- RK's band: 20 of 22 inside
- board scales (y(bf16 randn) over the fit's span): {'A': 0.9642587521648126, 'B': 1.0576751796676214}
- seen-kinds arm (E149's 17 held-out kinds, E149's stage-2 y; not blind to the designer): RK 12.78 W (bias -8.95), G1p 29.26 W (bias -7.31), G4p 15.61 W (bias -10.94), G1 24.66 W (bias -12.95)

