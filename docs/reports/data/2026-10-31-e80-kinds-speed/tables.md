### The registered rules

| rule | verdict | numbers |
|---|---|---|
| E80-R1 | **PASS** | `{"population": 18, "rms_mhz": 21.74, "bar": 25.0, "t1_rms_mhz": 28.05, "q130c_4_12s_rms_mhz": 27.0}` |
| E80-R2 | **FAIL** | `{"population": 18, "right": 13, "share": 0.722, "bar": 0.8}` |
| E80-R3 | **FAIL** | `{"measured_mhz": 781.6, "runs": [792.9, 770.3], "pred_t1_mhz": 745.2, "miss_mhz": 36.4, "bar": 15.0, "e64_measured_mhz": 737.1, "e64_t1_oos_gamma3_trip66_mhz": 754.5}` |
| E80-R4 | **FAIL** | `{"bar": 25.0}` |
| R7 | **FAIL** | `{"population": 18, "within_25": 13, "predicted_800": 9, "predicted_800_below_790": ["int8/neg_ones"]}` |
| R8 | **FAIL** | `{"population": 18, "limit_right": 13, "within_40": 13, "limit_wrong": ["fp16/ones", "int8/full", "int8/smallint", "int8/gauss_q", "int8/sparse50"]}` |
| E80-S1 | **FAIL** | `{"population": 12, "inside_ci95": 8}` |
| E80-S2 | **FAIL** | `{"population": 34, "rms_mhz": 15.72, "bar": 10.0}` |
| E80-S3 | **FAIL** | `{"population": 18, "rms_mhz": 35.84, "bar": 15.0}` |

### Each kind, measured

| format | kind | burst MHz (2 passes) | burst rate | p800 W | burst die °C | burst limit | sustained MHz | sustained rate (kernel / wall) | sustained board W | sustained die °C | sustained limit | board pJ/op |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp16 | zeros | 800.0 (800.0/800.0) | 24.55 TFLOPS | 34.6 | 54→54, 55→56 | none | 789.8 | 24.23 / 23.57 TFLOPS | 35.1 | 57.7 | none | 1.45 |
| fp16 | ones | 800.0 (800.0/800.0) | 24.55 TFLOPS | 50.7 | 53→57, 55→59 | none | 781.6 (792.9/770.3) | 23.83 / 23.10 TFLOPS | 53.2 | 64.8 | none/thermal | 2.23 |
| fp16 | randn | 730.6 (746.9/714.3) | 21.95 TFLOPS | 76.1 | 48→55, 56→62 | power | 609.5 | 18.68 / 18.12 TFLOPS | 52.3 | 66.0 | thermal | 2.80 |
| fp16 | sparse50 | 800.0 (800.0/800.0) | 24.55 TFLOPS | 59.9 | 50→56, 56→61 | none | 717.1 | 21.62 / 20.99 TFLOPS | 54.9 | 65.5 | thermal | 2.54 |
| fp16 | smallint | 782.7 (787.8/777.6) | 23.82 TFLOPS | 66.9 | 52→58, 55→62 | power | 650.6 | 19.71 / 19.09 TFLOPS | 51.9 | 65.6 | thermal | 2.63 |
| fp16 | fp8grid | 773.2 (776.5/770.0) | 23.37 TFLOPS | 69.8 | 55→61, 56→62 | power | 661.5 | 19.98 / 19.23 TFLOPS | 54.2 | 65.6 | thermal | 2.71 |
| fp16 | nn_like | 780.0 (784.0/776.0) | 23.70 TFLOPS | 68.0 | 52→59, 54→61 | power | 665.2 | 20.12 / 19.52 TFLOPS | 54.7 | 65.6 | thermal | 2.72 |
| int8 | zeros | 800.0 (800.0/800.0) | 84.30 TOPS | 34.8 | 47→49, 55→57 | none | 800.0 | 84.33 / 81.96 TOPS | 37.0 | 58.0 | none | 0.44 |
| int8 | neg_ones | 777.5 (755.1/800.0) | 81.68 TOPS | 39.4 | 55→56, 55→57 | none | 796.9 | 83.98 / 81.47 TOPS | 41.0 | 60.0 | none | 0.49 |
| int8 | full | 800.0 (800.0/800.0) | 84.30 TOPS | 48.9 | 51→55, 56→59 | none | 793.4 (796.7/790.0) | 83.54 / 81.11 TOPS | 53.2 | 64.9 | none | 0.64 |
| int8 | smallint | 798.0 (800.0/796.0) | 84.31 TOPS | 46.2 | 50→53, 54→58 | none | 795.4 | 83.80 / 81.08 TOPS | 51.0 | 64.4 | none | 0.61 |
| int8 | gauss_q | 800.0 (800.0/800.0) | 84.31 TOPS | 48.0 | 53→56, 54→58 | none | 794.4 | 83.70 / 80.87 TOPS | 52.1 | 64.6 | none | 0.62 |
| int8 | sparse50 | 800.0 (800.0/800.0) | 84.30 TOPS | 46.8 | 56→58, 56→59 | none | 789.3 | 83.15 / 80.88 TOPS | 49.0 | 63.6 | none | 0.59 |
| fp32 | randn | 711.9 (715.7/708.0) | 10.69 TFLOPS | 82.7 | 55→62, 55→62 | power | 604.3 (608.4/600.3) | 9.27 / 9.02 TFLOPS | 54.2 | 66.0 | thermal | 5.85 |
| fp32 | bf16trunc | 774.0 (776.5/771.4) | 11.71 TFLOPS | 69.5 | 54→60, 54→61 | power | 639.1 | 9.70 / 9.37 TFLOPS | 51.7 | 65.7 | thermal | 5.33 |
| fp32 | sparse90 | 800.0 (800.0/800.0) | 12.28 TFLOPS | 35.5 | 52→54, 55→56 | none | 800.0 | 12.28 / 11.94 TFLOPS | 36.8 | 58.0 | none | 3.00 |
| fp32 | smallint | 800.0 (800.0/800.0) | 12.28 TFLOPS | 61.3 | 53→59, 55→61 | none | 690.8 | 10.44 / 10.15 TFLOPS | 52.5 | 65.5 | thermal | 5.03 |
| fp32 | nn_like | 760.8 (721.6/800.0) | 11.65 TFLOPS | 59.8 | 54→58, 55→61 | none | 700.0 | 10.56 / 10.28 TFLOPS | 52.5 | 65.5 | thermal | 4.97 |

### Predicted against measured

| format | kind | burst meas | burst pred (registered) | T1 | Q130(c) 4–12 s | sustained meas | T1 γ3 pred | Q130(c) | limit meas / pred | c meas (W) | c pred [95%] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp16 | zeros | 800.0 | 800.0 | 800.0 | 800 | 789.8 | 800.0 | 800 | none / none | 1.61 | 1.39 [1.39, 1.69] |
| fp16 | ones | 800.0 | 800.0 | 800.0 | 800 | 781.6 | 745.2 | 745 | none/thermal / thermal | 9.70 | 9.70 [7.33, 12.07] |
| fp16 | randn | 730.6 | 728.6 | 714.3 | 715 | 609.5 | 600.0 | 600 | thermal / thermal | 23.07 | 23.28 [19.96, 26.61] |
| fp16 | sparse50 | 800.0 | 800.0 | 792.9 | 794 | 717.1 | 654.5 | 656 | thermal / thermal | 14.72 | 16.62 [9.99, 23.26] |
| fp16 | smallint | 782.7 | 752.4 | 740.5 | 739 | 650.6 | 614.4 | 614 | thermal / thermal | 18.05 | 21.14 [13.60, 28.68] |
| fp16 | fp8grid | 773.2 | 733.3 | 719.0 | 715 | 661.5 | 604.2 | 604 | thermal / thermal | 19.05 | 22.44 [14.15, 30.74] |
| fp16 | nn_like | 780.0 | 761.9 | 750.0 | 752 | 665.2 | 620.4 | 621 | thermal / thermal | 18.59 | 20.42 [12.47, 28.37] |
| int8 | zeros | 800.0 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | 800 | none / none | 2.49 | 2.12 [2.12, 2.42] |
| int8 | neg_ones | 777.5 | 800.0 | 800.0 | 800 | 796.9 | 800.0 | 800 | none / none | 3.54 | 2.68 [2.12, 5.04] |
| int8 | full | 800.0 | 800.0 | 800.0 | 800 | 793.4 | 757.5 | 758 | none / thermal | 8.98 | 9.10 [5.79, 12.41] |
| int8 | smallint | 798.0 | 800.0 | 800.0 | 800 | 795.4 | 756.9 | 757 | none / thermal | 7.99 | 9.12 [4.03, 14.21] |
| int8 | gauss_q | 800.0 | 800.0 | 800.0 | 800 | 794.4 | 757.5 | 758 | none / thermal | 7.79 | 9.10 [4.02, 14.17] |
| int8 | sparse50 | 800.0 | 800.0 | 800.0 | 800 | 789.3 | 774.3 | 774 | none / thermal | 7.36 | 8.07 [3.68, 12.47] |
| fp32 | randn | 711.9 | 704.8 | 700.0 | 700 | 604.3 | 600.0 | 600 | thermal / thermal | 25.55 | 25.21 [21.41, 29.01] |
| fp32 | bf16trunc | 774.0 | 714.3 | 695.2 | 706 | 639.1 | 600.0 | 600 | thermal / thermal | 19.11 | 24.27 [20.70, 27.85] |
| fp32 | sparse90 | 800.0 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | 800 | none / none | 2.23 | 1.89 [1.57, 2.20] |
| fp32 | smallint | 800.0 | 781.0 | 769.0 | 770 | 690.8 | 638.3 | 639 | thermal / thermal | 15.18 | 18.52 [16.07, 20.96] |
| fp32 | nn_like | 760.8 | 795.2 | 781.0 | 785 | 700.0 | 650.9 | 649 | thermal / thermal | 14.04 | 17.15 [14.24, 20.06] |
