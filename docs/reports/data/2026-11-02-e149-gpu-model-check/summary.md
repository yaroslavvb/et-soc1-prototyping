### Stage 1, watts over the same GEMM on zeros (y ± SE over the valid replicates)

| bf16 zeros | 0% | 25% | 50% | 75% | 90% | 100% |
|---|---:|---:|---:|---:|---:|---:|
| scattered | 154.7 ± 3.6 | 153.2 ± 3.8 | 127.6 ± 2.0 | 95.4 ± 2.3 | 68.2 ± 1.6 | 0.0 ± 0.6 |
| blocks of 64 along K | 154.7 ± 3.6 | 145.1 ± 4.0 | 119.7 ± 3.4 | 79.3 ± 2.6 | 29.2 ± 1.2 | 0.0 ± 0.6 |

One-sided 50% scattered: A only 149.4 ± 3.9, B only 136.9 ± 3.5. int8 scattered 0/25/50/75/90%: 84.0 ± 3.5, 78.0 ± 3.5, 67.3 ± 4.0, 47.7 ± 3.0, 33.5 ± 1.8; blocks 50%: 62.6 ± 2.3. fp16 50%/75% scattered 97.8 ± 0.9 / 67.2 ± 0.9, 50% blocks 89.1 ± 1.2.

| Hamming ladder from the base 1.0 (k flips per element) | base | rungs |
|---|---:|---|
| bf16 mantissa (7 bits), k = 1, 2, 3, 5, 7 | 18.7 ± 2.0 | 68.8 ± 1.8, 90.3 ± 2.6, 100.2 ± 2.4, 99.0 ± 2.3, 25.7 ± 0.5 |
| bf16 exponent (low 5 bits), k = 1, 2, 3, 5 | 18.7 ± 2.0 | 66.1 ± 1.2, 72.7 ± 2.8, 70.6 ± 1.2, 14.7 ± 1.4 |
| bf16 sign, p = 0.10, 0.25, 0.50 | 18.7 ± 2.0 | 36.0 ± 1.1, 49.5 ± 1.3, 60.3 ± 2.1 |
| fp16 mantissa (10 bits), k = 1, 3, 5, 7, 10 | 12.0 ± 0.9 | 51.4 ± 0.8, 82.2 ± 1.1, 93.7 ± 1.1, 85.0 ± 0.8, 18.8 ± 1.4 |
| fp16 exponent (low 3 bits), k = 1, 2, 3 | 12.0 ± 0.9 | 35.1 ± 1.2, 32.8 ± 0.4, 7.5 ± 1.3 |
| fp16 sign, p = 0.25, 0.50; A only 0.50 | 12.0 ± 0.9 | 29.4 ± 1.3, 35.1 ± 0.6, 33.0 ± 1.2 |
| int8 bits 1–7 from 1, k = 1, 2, 3, 5, 7 | 3.6 ± 1.0 | 47.9 ± 2.1, 69.5 ± 3.4, 76.9 ± 3.1, 79.6 ± 3.8, 9.4 ± 0.8 |
| int8 p = 0.5 in bits 1–3, 4–6, 7; bit 7 on A only | 3.6 ± 1.0 | 39.3 ± 2.0, 39.8 ± 2.9, 21.1 ± 1.8, 15.4 ± 0.5 |

Single positions (p = 0.5), bf16 mantissa bits 0, 3, 6: 44.7 ± 2.0, 40.7 ± 0.4, 38.5 ± 1.2; exponent bits 0, 4: 37.1 ± 1.1, 45.0 ± 1.3; fp16 mantissa bits 0, 5, 9: 23.6 ± 1.2, 28.0 ± 1.1, 23.0 ± 0.5. One-sided bf16 mantissa k = 3 A / B: 65.8 ± 1.5 / 42.7 ± 2.1; exponent k = 2 A / B: 62.9 ± 1.7 / 40.2 ± 1.7; fp16 mantissa k = 5 on A: 55.6 ± 1.0; int8 random on A / B: 40.8 ± 1.3 / 58.9 ± 3.3.

| bf16 signs, magnitude 1.5 | fixed + | A −, B + | random both | random A | random B | abs(randn), fixed + | same, random signs |
|---|---:|---:|---:|---:|---:|---:|---:|
| y | 22.0 ± 0.4 | 22.8 ± 1.9 | 65.1 ± 1.8 | 58.3 ± 1.6 | 32.7 ± 1.0 | 128.4 ± 4.6 | 157.1 ± 3.2 |

| bf16 order | sorted along K | the same values shuffled | magnitudes sorted, random signs | sorted along M/N | sorted along K, rolled |
|---|---:|---:|---:|---:|---:|
| y | 103.2 ± 2.5 | 156.2 ± 4.0 | 128.7 ± 3.9 | 94.4 ± 2.4 | 143.0 ± 2.9 |

| square wave along K, block b | 1 | 2 | 4 | 8 | 16 | 64 |
|---|---:|---:|---:|---:|---:|---:|
| y | 72.2 ± 3.0 | 80.0 ± 2.4 | 82.7 ± 1.9 | 88.4 ± 3.2 | 90.6 ± 1.8 | 85.6 ± 2.8 |

### The models on stage 1 (rms W; nested = leave-one-kind-out)

| model | bf16 in · nested | fp16 in · nested | int8 in · nested |
|---|---|---|---|
| G0 | 53.65 · 54.33 | 41.58 · 42.93 | 33.76 · 35.16 |
| G1 | 22.90 · 28.61 | 5.55 · 56.30 | 6.44 · 13.64 |
| G1s (lag 32) | 17.73 · 20.03 | 3.71 · 22.96 | 5.76 · 11.95 |
| G2 | 18.58 · 23.54 | 5.27 · 54.09 | 6.37 · 14.28 |
| G3 | 9.34 · 30.58 | 3.26 · 768.00 | 4.59 · 1536.41 |
| G4 (lag 16) | 8.39 · 94.46 | 3.42 · 321.35 | 5.60 · 315.25 |
| S1 | 35.84 · 45.16 | 29.31 · 188.91 | 12.09 · 28.29 |

Lag scan (G1's form at K-lag s; pooled nested rms over the three formats, W): s = 1: 34.91, s = 2: 33.13, s = 4: 32.65, s = 8: 30.51, s = 16: 27.82, s = 32: 19.43.

### Frozen coefficients, G1 and G1s (W per flip per multiply-add; fJ per flip at the measured rate)

- G1 bf16 (MAC rate 78.6 T/s): nzprod 35.27; gtr -32.67; flip_sign 18.20 (232 fJ); flip_exp 10.83 (138 fJ); flip_mant 7.18 (91 fJ); pos_exp 2.98; pos_mant -71.95; asym 4.25; psgn 41.29
- G1 fp16 (MAC rate 54.4 T/s): nzprod 13.91; gtr -34.25; flip_sign -22.18 (-408 fJ); flip_exp 7.56 (139 fJ); flip_mant 8.32 (153 fJ); pos_mant 0.03; asym -0.11; psgn 75.05
- G1 int8 (MAC rate 74.1 T/s): nzprod 3.43; gtr -13.06; flip_sign -3.45 (-47 fJ); flip_high 11.27 (152 fJ); flip_low 10.46 (141 fJ); asym -2.31; psgn 34.60
- G1s bf16 (MAC rate 78.6 T/s): nzprod 39.82; gtr -28.75; flip_sign 28.56 (364 fJ); flip_exp 13.81 (176 fJ); flip_mant 9.06 (115 fJ); pos_exp 27.76; pos_mant -5.82; asym 4.23; psgn -6.35
- G1s fp16 (MAC rate 54.4 T/s): nzprod 15.53; gtr -4.64; flip_sign -9.18 (-169 fJ); flip_exp 6.71 (123 fJ); flip_mant 8.02 (148 fJ); pos_mant -0.22; asym -0.05; psgn 48.47
- G1s int8 (MAC rate 74.1 T/s): nzprod 4.78; gtr -5.84; flip_sign -1.32 (-18 fJ); flip_high 11.07 (149 fJ); flip_low 10.06 (136 fJ); asym -2.31; psgn 29.34

### Heat

Pooled two-pole fit: τ₁ 0.20 s, τ₂ 31.8 s, r₁ 0.0597, r₂ 0.0562 °C/W, **die rise per board W 0.1159 °C/W**, 81% of it in 30 s (0.0940 °C/W), rms 1.77 °C over 39024 samples; grid edge {'tau1': True, 'tau2': False}.
- unit A: τ₁ 0.20 s, τ₂ 12.7 s, R 0.0944 °C/W, 30 s share 96%, rms 0.71 °C; leakage 2.61 W/°C over [54.0, 60.0] °C
- unit B: τ₁ 0.20 s, τ₂ 40.0 s, R 0.1425 °C/W, 30 s share 72%, rms 2.25 °C; leakage 1.78 W/°C over [47.0, 58.0] °C
- out-of-board 30 s rises (fit on one board, scored on the other): A→B 1.19 °C (n 186); B→A 1.01 °C (n 187)

### Stage 1's rules

- B1: **HOLDS**
- R1a_bf16: **HOLDS**
- R1a_int8: **HOLDS**
- R1b: **HOLDS**
- R2_bf16.exp: **HOLDS**
- R2_bf16.mant: **HOLDS**
- R2_fp16.mant: **HOLDS**
- R2_int8.bits: **HOLDS**
- R3a: **HOLDS**
- R3b: **HOLDS**
- R4a: **HOLDS**
- R4b: **FAILS**
- V0: **HOLDS**

### Stage 2, blind (measured − predicted, W)

| kind | measured y ± SE | G1 | G1s | G0 | S1 | G2 | G3 | G4 | G1 band | inside |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| bf16.checker | 135.9 ± 2.4 | 214.6 | 65.9 | 19.8 | 67.9 | 122.4 | 216.1 | 149.3 | ±47.1 | no |
| bf16.gelu_w | 146.4 ± 3.9 | 160.0 | 146.8 | 79.1 | 130.7 | 162.9 | 158.4 | 157.9 | ±47.1 | yes |
| bf16.lowrank | 151.0 ± 2.6 | 159.4 | 153.9 | 79.1 | 135.4 | 165.0 | 158.8 | 159.0 | ±47.1 | yes |
| bf16.onebit | 30.8 ± 1.0 | 18.6 | 30.6 | 19.0 | 4.9 | 2.8 | 16.6 | 16.5 | ±47.1 | yes |
| bf16.pi | 17.0 ± 1.2 | 35.3 | 39.8 | 79.1 | 44.8 | 63.3 | 27.2 | 27.3 | ±47.1 | yes |
| bf16.powerlaw | 161.4 ± 3.1 | 189.5 | 201.1 | 79.1 | 131.2 | 162.5 | 189.4 | 190.4 | ±47.1 | yes |
| bf16.rand | 118.0 ± 1.4 | 107.8 | 110.8 | 78.7 | 77.5 | 107.7 | 114.1 | 116.8 | ±47.1 | yes |
| bf16.randn (seen) | 151.3 ± 3.6 | 158.7 | 153.3 | 79.1 | 135.6 | 165.1 | 158.2 | 158.3 | ±47.1 | yes |
| bf16.sortrand | 86.4 ± 2.6 | 67.1 | 95.5 | 78.9 | 77.4 | 89.3 | 83.2 | 95.7 | ±47.1 | yes |
| bf16.sparse75 | 89.4 ± 1.8 | 94.6 | 96.6 | 4.9 | 34.0 | 100.1 | 93.2 | 94.0 | ±47.1 | yes |
| bf16.sparse_neg | 105.2 ± 1.8 | 109.3 | 130.0 | 19.7 | 38.2 | 91.2 | 115.5 | 117.5 | ±47.1 | yes |
| bf16.ternary | 77.1 ± 1.8 | 102.2 | 99.4 | 35.1 | 64.3 | 49.9 | 91.7 | 89.0 | ±47.1 | yes |
| bf16.twos | 10.2 ± 1.0 | 35.3 | 39.8 | 79.1 | 4.0 | 10.3 | 27.2 | 27.3 | ±47.1 | yes |
| fp16.gelu_w | 117.7 ± 0.7 | 136.9 | 132.4 | 48.0 | 101.3 | 136.2 | 138.3 | 132.1 | ±92.6 | yes |
| fp16.rand | 98.4 ± 1.1 | 114.5 | 111.2 | 48.0 | 54.0 | 110.6 | 114.0 | 109.2 | ±92.6 | yes |
| int8.q_gelu_w | 80.4 ± 1.7 | 90.0 | 89.4 | 46.6 | 77.2 | 87.9 | 88.4 | 88.6 | ±22.4 | yes |
| int8.ternary | 65.2 ± 2.0 | 76.3 | 77.8 | 22.0 | 78.6 | 71.8 | 80.5 | 77.8 | ±22.4 | yes |
| int8.twos | 4.1 ± 1.3 | 3.4 | 4.8 | 49.5 | -4.0 | 2.3 | 1.8 | 5.6 | ±22.4 | yes |

| model | rms | bias | worst | n |
|---|---:|---:|---:|---:|
| G0 | 63.71 | 37.01 | 116.18 | 17 |
| G1 | 24.66 | -12.95 | 78.69 | 17 |
| G1s | 24.03 | -7.72 | 70.08 | 17 |
| G2 | 17.74 | -2.44 | 46.38 | 17 |
| G3 | 23.43 | -12.93 | 80.15 | 17 |
| G4 | 12.76 | -9.36 | 28.94 | 17 |
| S1 | 33.82 | 22.19 | 68.00 | 17 |

| hold (30 s after 15 s of zeros) | measured rise °C | blind | with measured power | band |
|---|---:|---:|---:|---:|
| bf16.checker | 12.95 | 23.11 | 11.63 | ±4.78 |
| bf16.gelu_w | 11.85 | 15.75 | 11.72 | ±4.78 |
| bf16.lowrank | 12.50 | 15.93 | 12.31 | ±4.78 |
| bf16.onebit | 3.00 | 1.08 | 1.97 | ±4.78 |
| bf16.pi | 2.45 | 3.18 | 0.92 | ±4.78 |
| bf16.powerlaw | 13.00 | 19.10 | 13.01 | ±4.78 |
| bf16.rand | 11.50 | 10.29 | 9.51 | ±4.78 |
| bf16.sortrand | 8.50 | 5.10 | 5.78 | ±4.78 |
| bf16.sparse75 | 6.50 | 8.98 | 6.52 | ±4.78 |
| bf16.sparse_neg | 9.05 | 10.64 | 7.98 | ±4.78 |
| bf16.ternary | 5.50 | 10.57 | 6.04 | ±4.78 |
| bf16.twos | -0.20 | 2.30 | -0.61 | ±4.78 |
| fp16.gelu_w | 11.40 | 13.73 | 9.43 | ±8.90 |
| fp16.rand | 8.00 | 10.70 | 6.82 | ±8.90 |
| int8.q_gelu_w | 8.50 | 9.71 | 6.12 | ±2.78 |
| int8.ternary | 7.00 | 8.58 | 5.31 | ±2.78 |
| int8.twos | 0.00 | -0.51 | -0.90 | ±2.78 |

Rules: H1 **FAILS**; H2 **FAILS**; H3 **HOLDS**; H4 **FAILS**; P1 **FAILS**; P2 **FAILS**; P3 **HOLDS**; P4 **HOLDS**; P5 **HOLDS**

A2's board-scaled arm (no verdict): power scale {"A": 0.9392, "B": 1.0168}; G0 rms 64.19 bias 38.13 inside 6/17; G1 rms 22.93 bias -10.73 inside 16/17; G1s rms 23.19 bias -5.61 inside 16/17; G2 rms 17.22 bias -0.45 inside 17/17; G3 rms 21.57 bias -10.71 inside 16/17; G4 rms 10.86 bias -7.22 inside 17/17; S1 rms 34.77 bias 23.64 inside 14/17; heat scale {"A": 0.724, "B": 0.93}, rms 2.35 °C, inside 16/17
