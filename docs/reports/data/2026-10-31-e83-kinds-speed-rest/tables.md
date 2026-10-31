### The registered rules

| rule | verdict | numbers |
|---|---|---|
| E83-R1 | **PASS** | `{"population": 33, "rms_mhz": 11.78, "bar": 25.0, "beside_a1_reset_free_rms_mhz": 10.3, "beside_b_q130c_4_12s_rms_mhz": 12.59, "beside_gov_arm_rms_mhz": 12.36, "beside_rms_over_kinds_a_puts_below_799_mhz": 19.83}` |
| E83-R2 | **PASS** | `{"population": 33, "right": 29, "share": 0.879, "bar": 0.8, "beside_b_q130c_binary_right": 27}` |
| E83-R3 | **PASS** | `{"population": 33, "rms_mhz": 14.26, "bar": 25.0, "beside_t1_e80line_arm_rms_mhz": 14.69, "beside_rms_over_kinds_a_puts_below_799_mhz": 18.34}` |
| E83-R4 | **PASS** | `{"population": 33, "sus_rms_a_mhz": 14.26, "sus_rms_b_mhz": 23.43, "beside_burst_rms_a_mhz": 11.78, "beside_burst_rms_b_mhz": 12.59}` |
| E83-R5 | **PASS** | `{"bar": 25.0}` |
| E83-S1 | **PASS** | `{"population_burst": 33, "population_sus": 33, "burst_rms_mhz": 7.89, "sus_rms_mhz": 7.52, "bar": 15.0, "beside_burst_a1_reset_free_rms_mhz": 5.48}` |
| E83-S2 | **FAIL** | `{"population": 32, "inside_ci95": 22, "bar": 0.7}` |
| E83-S3 | **FAIL** | `{}` |

### Each kind, measured (the 33, then E80's five anchors as re-run here)

| format | kind | burst MHz (2 passes) | burst rate | p800 W | burst die °C | burst limit | sustained MHz | sustained rate (kernel / wall) | sustained board W | sustained die °C | sustained limit | c W | board pJ/op |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 | zeros | 800.0 (800.0/800.0) | 12.28 TFLOPS | 34.1 | 52→53, 54→55 | none | 789.3 | 12.10 / 11.76 TFLOPS | 35.2 | 57.9 | none | 1.72 | 2.91 |
| fp32 | ones | 800.0 (800.0/800.0) | 12.27 TFLOPS | 51.5 | 56→60, 56→59 | none | 782.4 (771.7/793.1) | 11.94 / 11.58 TFLOPS | 53.3 | 65.0 | thermal/none | 9.60 | 4.47 |
| fp32 | neg_ones | 800.0 (800.0/800.0) | 12.27 TFLOPS | 51.4 | 56→60, 55→59 | none | 767.3 | 11.65 / 11.28 TFLOPS | 52.0 | 65.1 | thermal | 9.63 | 4.46 |
| fp32 | pi | 800.0 (800.0/800.0) | 12.28 TFLOPS | 51.6 | 55→60, 56→60 | none | 780.1 | 11.90 / 11.58 TFLOPS | 53.3 | 64.9 | thermal | 9.82 | 4.47 |
| fp32 | randn_small | 706.0 (704.2/707.8) | 10.64 TFLOPS | 83.4 | 56→63, 55→62 | power | 600.5 | 9.21 / 8.94 TFLOPS | 54.0 | 66.3 | thermal | 25.75 | 5.86 |
| fp32 | randn_large | 703.0 (694.2/711.8) | 10.58 TFLOPS | 83.1 | 56→62, 55→62 | power | 608.2 | 9.32 / 9.09 TFLOPS | 54.8 | 66.0 | thermal | 25.55 | 5.88 |
| fp32 | uniform01 | 722.1 (732.0/712.2) | 10.90 TFLOPS | 78.6 | 53→60, 55→62 | power | 627.6 | 9.56 / 9.24 TFLOPS | 55.2 | 65.8 | thermal | 23.50 | 5.77 |
| fp32 | sparse50 | 800.0 (800.0/800.0) | 12.28 TFLOPS | 48.6 | 56→60, 54→58 | none | 793.6 (800.0/787.2) | 12.16 / 11.81 TFLOPS | 51.8 | 64.4 | none/thermal | 8.52 | 4.26 |
| fp32 | pow2 | 800.0 (800.0/800.0) | 12.28 TFLOPS | 62.0 | 56→62, 54→61 | none | 684.6 | 10.32 / 10.07 TFLOPS | 51.9 | 65.6 | thermal | 15.06 | 5.03 |
| fp32 | fp16grid | 757.5 (766.0/749.0) | 11.45 TFLOPS | 72.3 | 51→58, 56→62 | power | 648.7 | 9.84 / 9.47 TFLOPS | 54.6 | 65.6 | thermal | 20.65 | 5.55 |
| fp32 | a_randn_b_zeros | 800.0 (800.0/800.0) | 12.28 TFLOPS | 36.3 | 55→57, 55→56 | none | 800.0 | 12.28 / 11.96 TFLOPS | 37.2 | 58.3 | none | 2.20 | 3.03 |
| fp32 | a_zeros_b_randn | 800.0 (800.0/800.0) | 12.28 TFLOPS | 35.3 | 50→51, 55→56 | none | 795.4 | 12.20 / 11.86 TFLOPS | 36.7 | 57.0 | none | 2.41 | 3.01 |
| fp32 | randn_sorted | 712.9 (717.6/708.2) | 10.75 TFLOPS | 80.3 | 56→63, 54→61 | power | 603.1 | 9.25 / 8.91 TFLOPS | 52.8 | 66.0 | thermal | 24.32 | 5.71 |
| fp16 | neg_ones | 800.0 (800.0/800.0) | 24.55 TFLOPS | 51.4 | 55→59, 56→60 | none | 789.8 | 24.17 / 23.52 TFLOPS | 54.1 | 64.7 | none | 9.66 | 2.24 |
| fp16 | randn_small | 709.2 (720.4/698.0) | 21.51 TFLOPS | 77.9 | 54→61, 56→62 | power | 614.3 | 18.79 / 18.21 TFLOPS | 52.8 | 65.9 | thermal | 23.10 | 2.81 |
| fp16 | uniform01 | 769.2 (776.0/762.5) | 23.35 TFLOPS | 71.0 | 48→55, 55→61 | power | 632.0 | 19.24 / 18.69 TFLOPS | 52.5 | 65.8 | thermal | 20.39 | 2.73 |
| fp16 | sparse90 | 800.0 (800.0/800.0) | 24.55 TFLOPS | 36.3 | 47→49, 55→57 | none | 800.0 | 24.56 / 23.81 TFLOPS | 39.0 | 59.1 | none | 3.12 | 1.59 |
| fp16 | wsparse50 | 800.0 (800.0/800.0) | 24.55 TFLOPS | 48.2 | 56→59, 54→58 | none | 793.9 (792.9/794.9) | 24.34 / 23.71 TFLOPS | 51.1 | 63.6 | none | 8.32 | 2.10 |
| fp16 | wsparse90 | 800.0 (800.0/800.0) | 24.55 TFLOPS | 35.3 | 50→52, 55→57 | none | 789.8 | 24.22 / 23.61 TFLOPS | 36.6 | 58.1 | none | 2.39 | 1.51 |
| fp16 | a_randn_b_zeros | 800.0 (800.0/800.0) | 24.55 TFLOPS | 35.9 | 54→55, 55→57 | none | 794.9 | 24.39 / 23.73 TFLOPS | 36.9 | 58.3 | none | 2.20 | 1.51 |
| fp16 | a_zeros_b_randn | 800.0 (800.0/800.0) | 24.55 TFLOPS | 35.4 | 50→51, 55→57 | none | 794.4 | 24.38 / 23.66 TFLOPS | 36.7 | 57.0 | none | 2.53 | 1.50 |
| fp16 | pair_half_zero | 737.7 (740.0/735.4) | 22.38 TFLOPS | 74.8 | 56→62, 55→62 | power | 619.2 | 18.92 / 18.28 TFLOPS | 51.6 | 65.8 | thermal | 21.31 | 2.73 |
| fp16 | randn_sorted | 734.0 (730.6/737.5) | 22.12 TFLOPS | 75.4 | 56→62, 55→62 | power | 620.8 | 18.97 / 18.52 TFLOPS | 52.5 | 65.8 | thermal | 21.82 | 2.77 |
| int8 | ones | 800.0 (800.0/800.0) | 84.30 TOPS | 39.2 | 55→57, 56→57 | none | 800.0 | 84.32 / 82.04 TOPS | 40.5 | 59.0 | none | 3.75 | 0.48 |
| int8 | pos | 800.0 (800.0/800.0) | 84.30 TOPS | 48.2 | 56→59, 56→59 | none | 791.8 | 83.31 / 80.62 TOPS | 51.4 | 64.8 | none | 8.03 | 0.62 |
| int8 | ternary | 800.0 (800.0/800.0) | 84.30 TOPS | 46.2 | 56→59, 56→59 | none | 797.2 (794.4/800.0) | 84.01 / 81.38 TOPS | 48.5 | 62.6 | none | 7.06 | 0.58 |
| int8 | sparse90 | 800.0 (800.0/800.0) | 84.31 TOPS | 38.5 | 56→57, 55→56 | none | 794.9 | 83.76 / 80.77 TOPS | 39.6 | 59.3 | none | 3.27 | 0.47 |
| int8 | wsparse50 | 798.0 (796.1/800.0) | 84.31 TOPS | 42.2 | 56→58, 54→57 | none | 789.7 | 83.16 / 80.88 TOPS | 43.7 | 61.4 | none | 4.67 | 0.53 |
| int8 | wsparse90 | 779.1 (800.0/758.3) | 82.10 TOPS | 36.6 | 52→54, 55→57 | none | 800.0 | 84.33 / 81.55 TOPS | 37.8 | 57.0 | none | 2.77 | 0.45 |
| int8 | highbit | 800.0 (800.0/800.0) | 84.31 TOPS | 41.4 | 50→52, 55→58 | none | 789.8 | 83.08 / 80.52 TOPS | 44.0 | 61.9 | none | 5.51 | 0.53 |
| int8 | a_full_b_zeros | 800.0 (800.0/800.0) | 84.32 TOPS | 37.2 | 55→57, 55→57 | none | 794.4 | 83.70 / 80.87 TOPS | 37.9 | 58.8 | none | 2.48 | 0.45 |
| int8 | a_zeros_b_full | 800.0 (800.0/800.0) | 84.30 TOPS | 36.2 | 53→54, 54→56 | none | 794.9 | 83.74 / 81.37 TOPS | 37.1 | 57.2 | none | 2.58 | 0.44 |
| int8 | sorted | 775.5 (800.0/751.0) | 81.52 TOPS | 47.8 | 50→54, 56→59 | none | 789.3 | 82.97 / 80.71 TOPS | 51.8 | 65.0 | none | 8.53 | 0.62 |
| fp32 | randn (anchor) | 714.7 (711.8/717.6) | 10.75 TFLOPS | 82.8 | 55→62, 54→61 | power | 612.0 | 9.36 / 9.05 TFLOPS | 55.3 | 66.0 | thermal | 25.59 | 5.90 |
| fp16 | zeros (anchor) | 800.0 (800.0/800.0) | 24.55 TFLOPS | 33.9 | 51→52, 54→55 | none | 800.0 | 24.56 / 23.88 TFLOPS | 35.8 | 58.0 | none | 1.74 | 1.46 |
| fp16 | randn (anchor) | 724.8 (729.2/720.4) | 21.75 TFLOPS | 77.0 | 52→60, 56→62 | power | 609.0 | 18.65 / 18.21 TFLOPS | 52.1 | 66.0 | thermal | 23.05 | 2.80 |
| int8 | zeros (anchor) | 800.0 (800.0/800.0) | 84.31 TOPS | 35.2 | 51→53, 54→56 | none | 788.8 | 83.09 / 80.42 TOPS | 36.0 | 56.9 | none | 2.36 | 0.43 |
| int8 | full (anchor) | 800.0 (800.0/800.0) | 84.31 TOPS | 49.3 | 55→59, 53→58 | none | 786.5 | 82.27 / 80.11 TOPS | 52.3 | 65.0 | thermal | 8.98 | 0.64 |

### Predicted against measured (the 33)

| format | kind | burst meas | (a) | (b) 4–12 s | gov arm | sustained meas | (a) | (b) | T1 + E80 line | (a-adj) | limit meas / (a) | c meas (W) | c pred [95%] | relation on c meas: burst / sustained |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 | zeros | 800.0 | 800.0 | 800 | 800.0 | 789.3 | 800.0 | 800 | 800.0 | 800.0 | none / none | 1.72 | 1.44 [1.44, 1.74] | 800.0 / 800.0 |
| fp32 | ones | 800.0 | 800.0 | 800 | 800.0 | 782.4 | 773.8 | 745 | 776.6 | 773.6 | thermal/none / thermal | 9.60 | 9.84 [9.28, 10.39] | 800.0 / 777.6 |
| fp32 | neg_ones | 800.0 | 800.0 | 800 | 800.0 | 767.3 | 773.8 | 745 | 776.6 | 773.6 | thermal / thermal | 9.63 | 9.84 [9.28, 10.39] | 800.0 / 777.0 |
| fp32 | pi | 800.0 | 800.0 | 800 | 800.0 | 780.1 | 773.8 | 745 | 776.6 | 773.6 | thermal / thermal | 9.82 | 9.84 [9.28, 10.39] | 800.0 / 774.2 |
| fp32 | randn_small | 706.0 | 710.8 | 700 | 704.8 | 600.5 | 602.5 | 600 | 606.0 | 602.4 | thermal / thermal | 25.75 | 25.44 [21.59, 29.30] | 708.2 / 601.9 |
| fp32 | randn_large | 703.0 | 710.5 | 700 | 704.8 | 608.2 | 602.4 | 600 | 605.4 | 602.4 | thermal / thermal | 25.55 | 25.48 [21.62, 29.34] | 709.9 / 602.3 |
| fp32 | uniform01 | 722.1 | 748.2 | 736 | 742.9 | 627.6 | 625.3 | 612 | 637.7 | 625.1 | thermal / thermal | 23.50 | 21.43 [18.54, 24.32] | 728.1 / 610.0 |
| fp32 | sparse50 | 800.0 | 800.0 | 800 | 800.0 | 793.6 | 759.2 | 728 | 761.7 | 758.9 | none/thermal / thermal | 8.52 | 10.77 [8.88, 12.65] | 800.0 / 791.5 |
| fp32 | pow2 | 800.0 | 799.8 | 800 | 800.0 | 684.6 | 708.8 | 681 | 710.2 | 708.6 | thermal / thermal | 15.06 | 14.39 [13.15, 15.64] | 799.3 / 700.2 |
| fp32 | fp16grid | 757.5 | 715.1 | 700 | 704.8 | 648.7 | 603.8 | 600 | 609.0 | 603.7 | thermal / thermal | 20.65 | 24.95 [21.21, 28.69] | 756.5 / 632.7 |
| fp32 | a_randn_b_zeros | 800.0 | 800.0 | 800 | 800.0 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.20 | 1.44 [1.44, 1.74] | 800.0 / 800.0 |
| fp32 | a_zeros_b_randn | 800.0 | 800.0 | 800 | 800.0 | 795.4 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.41 | 1.44 [1.44, 1.74] | 800.0 / 800.0 |
| fp32 | randn_sorted | 712.9 | 725.5 | 706 | 723.8 | 603.1 | 608.4 | 600 | 618.6 | 608.3 | thermal / thermal | 24.32 | 23.79 [20.33, 27.25] | 720.8 / 606.0 |
| fp16 | neg_ones | 800.0 | 800.0 | 800 | 800.0 | 789.8 | 776.0 | 745 | 779.6 | 775.7 | none / thermal | 9.66 | 9.70 [7.33, 12.07] | 800.0 / 776.6 |
| fp16 | randn_small | 709.2 | 731.1 | 718 | 728.6 | 614.3 | 611.9 | 600 | 622.8 | 611.7 | thermal / thermal | 23.10 | 23.18 [14.44, 31.92] | 731.9 / 612.4 |
| fp16 | uniform01 | 769.2 | 786.4 | 776 | 785.7 | 632.0 | 664.3 | 646 | 670.7 | 664.0 | thermal / thermal | 20.39 | 17.82 [12.23, 23.41] | 759.2 / 635.2 |
| fp16 | sparse90 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | none / none | 3.12 | 2.56 [1.94, 3.19] | 800.0 / 800.0 |
| fp16 | wsparse50 | 800.0 | 800.0 | 800 | 800.0 | 793.9 | 767.0 | 735 | 768.9 | 766.8 | none / thermal | 8.32 | 10.27 [5.91, 14.63] | 800.0 / 793.3 |
| fp16 | wsparse90 | 800.0 | 800.0 | 800 | 800.0 | 789.8 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.39 | 1.84 [1.47, 2.22] | 800.0 / 800.0 |
| fp16 | a_randn_b_zeros | 800.0 | 800.0 | 800 | 800.0 | 794.9 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.20 | 1.39 [1.39, 1.69] | 800.0 / 800.0 |
| fp16 | a_zeros_b_randn | 800.0 | 800.0 | 800 | 800.0 | 794.4 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.53 | 1.39 [1.39, 1.69] | 800.0 / 800.0 |
| fp16 | pair_half_zero | 737.7 | 743.0 | 727 | 733.3 | 619.2 | 620.9 | 608 | 633.5 | 620.7 | thermal / thermal | 21.31 | 21.95 [13.95, 29.95] | 749.5 / 626.4 |
| fp16 | randn_sorted | 734.0 | 738.1 | 715 | 733.3 | 620.8 | 616.9 | 604 | 629.3 | 616.8 | thermal / thermal | 21.82 | 22.44 [14.15, 30.74] | 744.3 / 622.0 |
| int8 | ones | 800.0 | 800.0 | 800 | 800.0 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | none / none | 3.75 | 2.68 [2.12, 5.04] | 800.0 / 800.0 |
| int8 | pos | 800.0 | 800.0 | 800 | 800.0 | 791.8 | 800.0 | 800 | 800.0 | 800.0 | none / none | 8.03 | 5.51 [2.43, 8.58] | 800.0 / 795.5 |
| int8 | ternary | 800.0 | 800.0 | 800 | 800.0 | 797.2 | 792.4 | 768 | 800.0 | 792.3 | none / none | 7.06 | 8.42 [3.77, 13.08] | 800.0 / 799.2 |
| int8 | sparse90 | 800.0 | 800.0 | 800 | 800.0 | 794.9 | 800.0 | 800 | 800.0 | 800.0 | none / none | 3.27 | 2.90 [2.20, 3.60] | 800.0 / 800.0 |
| int8 | wsparse50 | 798.0 | 800.0 | 800 | 800.0 | 789.7 | 800.0 | 800 | 800.0 | 800.0 | none / none | 4.67 | 5.33 [3.04, 7.62] | 800.0 / 800.0 |
| int8 | wsparse90 | 779.1 | 800.0 | 800 | 800.0 | 800.0 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.77 | 2.39 [2.12, 2.73] | 800.0 / 800.0 |
| int8 | highbit | 800.0 | 800.0 | 800 | 800.0 | 789.8 | 799.8 | 800 | 800.0 | 799.8 | none / none | 5.51 | 6.53 [2.95, 10.12] | 800.0 / 800.0 |
| int8 | a_full_b_zeros | 800.0 | 800.0 | 800 | 800.0 | 794.4 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.48 | 2.12 [2.12, 2.42] | 800.0 / 800.0 |
| int8 | a_zeros_b_full | 800.0 | 800.0 | 800 | 800.0 | 794.9 | 800.0 | 800 | 800.0 | 800.0 | none / none | 2.58 | 2.12 [2.12, 2.42] | 800.0 / 800.0 |
| int8 | sorted | 775.5 | 800.0 | 800 | 800.0 | 789.3 | 795.7 | 776 | 800.0 | 795.6 | none / none | 8.53 | 8.00 [3.59, 12.40] | 800.0 / 791.3 |

### Each kind's switching term as a share of random data's (derived)

Derived, not measured on its own: (c_kind − c_zeros) / (c_random − c_zeros), with this session's own zeros and random cells of the same format (fp32 zeros and randn, fp16 zeros and randn, int8 zeros and full), all from `results.json` `cells.*.c_w`. 0 = as cheap as zeros, 1 = as costly as random data.

| format | kind | c W | share of random's switching over zeros |
|---|---|---|---|
| fp32 | zeros | 1.72 | 0.000 |
| fp32 | ones | 9.60 | 0.330 |
| fp32 | neg_ones | 9.63 | 0.332 |
| fp32 | pi | 9.82 | 0.339 |
| fp32 | randn_small | 25.75 | 1.007 |
| fp32 | randn_large | 25.55 | 0.998 |
| fp32 | uniform01 | 23.50 | 0.913 |
| fp32 | sparse50 | 8.52 | 0.285 |
| fp32 | pow2 | 15.06 | 0.559 |
| fp32 | fp16grid | 20.65 | 0.793 |
| fp32 | a_randn_b_zeros | 2.20 | 0.020 |
| fp32 | a_zeros_b_randn | 2.41 | 0.029 |
| fp32 | randn_sorted | 24.32 | 0.947 |
| fp16 | neg_ones | 9.66 | 0.372 |
| fp16 | randn_small | 23.10 | 1.002 |
| fp16 | uniform01 | 20.39 | 0.875 |
| fp16 | sparse90 | 3.12 | 0.065 |
| fp16 | wsparse50 | 8.32 | 0.309 |
| fp16 | wsparse90 | 2.39 | 0.031 |
| fp16 | a_randn_b_zeros | 2.20 | 0.022 |
| fp16 | a_zeros_b_randn | 2.53 | 0.037 |
| fp16 | pair_half_zero | 21.31 | 0.918 |
| fp16 | randn_sorted | 21.82 | 0.942 |
| int8 | ones | 3.75 | 0.211 |
| int8 | pos | 8.03 | 0.856 |
| int8 | ternary | 7.06 | 0.710 |
| int8 | sparse90 | 3.27 | 0.138 |
| int8 | wsparse50 | 4.67 | 0.350 |
| int8 | wsparse90 | 2.77 | 0.063 |
| int8 | highbit | 5.51 | 0.476 |
| int8 | a_full_b_zeros | 2.48 | 0.019 |
| int8 | a_zeros_b_full | 2.58 | 0.034 |
| int8 | sorted | 8.53 | 0.932 |
| fp32 | randn | 25.59 | 1.000 |
| fp16 | zeros | 1.74 | 0.000 |
| fp16 | randn | 23.05 | 1.000 |
| int8 | zeros | 2.36 | 0.000 |
| int8 | full | 8.98 | 1.000 |

### All 51 kinds: the speed column (E80's 18 at 12:22–13:02 PDT, E83's 33 later the same afternoon)

| format | kind | session | burst MHz | burst rate | sustained MHz | sustained rate | sustained board W | sustained die °C | sustained limit |
|---|---|---|---|---|---|---|---|---|---|
| fp32 | randn | E80 (E83 re-run: 714.7 / 612.0) | 711.9 | 10.69 TFLOPS | 604.3 | 9.27 TFLOPS | 54.2 | 66.0 | thermal |
| fp32 | bf16trunc | E80 | 774.0 | 11.71 TFLOPS | 639.1 | 9.70 TFLOPS | 51.7 | 65.7 | thermal |
| fp32 | sparse90 | E80 | 800.0 | 12.28 TFLOPS | 800.0 | 12.28 TFLOPS | 36.8 | 58.0 | none |
| fp32 | smallint | E80 | 800.0 | 12.28 TFLOPS | 690.8 | 10.44 TFLOPS | 52.5 | 65.5 | thermal |
| fp32 | nn_like | E80 | 760.8 | 11.65 TFLOPS | 700.0 | 10.56 TFLOPS | 52.5 | 65.5 | thermal |
| fp32 | zeros | E83 | 800.0 | 12.28 TFLOPS | 789.3 | 12.10 TFLOPS | 35.2 | 57.9 | none |
| fp32 | ones | E83 | 800.0 | 12.27 TFLOPS | 782.4 | 11.94 TFLOPS | 53.3 | 65.0 | thermal/none |
| fp32 | neg_ones | E83 | 800.0 | 12.27 TFLOPS | 767.3 | 11.65 TFLOPS | 52.0 | 65.1 | thermal |
| fp32 | pi | E83 | 800.0 | 12.28 TFLOPS | 780.1 | 11.90 TFLOPS | 53.3 | 64.9 | thermal |
| fp32 | randn_small | E83 | 706.0 | 10.64 TFLOPS | 600.5 | 9.21 TFLOPS | 54.0 | 66.3 | thermal |
| fp32 | randn_large | E83 | 703.0 | 10.58 TFLOPS | 608.2 | 9.32 TFLOPS | 54.8 | 66.0 | thermal |
| fp32 | uniform01 | E83 | 722.1 | 10.90 TFLOPS | 627.6 | 9.56 TFLOPS | 55.2 | 65.8 | thermal |
| fp32 | sparse50 | E83 | 800.0 | 12.28 TFLOPS | 793.6 | 12.16 TFLOPS | 51.8 | 64.4 | none/thermal |
| fp32 | pow2 | E83 | 800.0 | 12.28 TFLOPS | 684.6 | 10.32 TFLOPS | 51.9 | 65.6 | thermal |
| fp32 | fp16grid | E83 | 757.5 | 11.45 TFLOPS | 648.7 | 9.84 TFLOPS | 54.6 | 65.6 | thermal |
| fp32 | a_randn_b_zeros | E83 | 800.0 | 12.28 TFLOPS | 800.0 | 12.28 TFLOPS | 37.2 | 58.3 | none |
| fp32 | a_zeros_b_randn | E83 | 800.0 | 12.28 TFLOPS | 795.4 | 12.20 TFLOPS | 36.7 | 57.0 | none |
| fp32 | randn_sorted | E83 | 712.9 | 10.75 TFLOPS | 603.1 | 9.25 TFLOPS | 52.8 | 66.0 | thermal |
| fp16 | zeros | E80 (E83 re-run: 800.0 / 800.0) | 800.0 | 24.55 TFLOPS | 789.8 | 24.23 TFLOPS | 35.1 | 57.7 | none |
| fp16 | ones | E80 | 800.0 | 24.55 TFLOPS | 781.6 | 23.83 TFLOPS | 53.2 | 64.8 | none/thermal |
| fp16 | randn | E80 (E83 re-run: 724.8 / 609.0) | 730.6 | 21.95 TFLOPS | 609.5 | 18.68 TFLOPS | 52.3 | 66.0 | thermal |
| fp16 | sparse50 | E80 | 800.0 | 24.55 TFLOPS | 717.1 | 21.62 TFLOPS | 54.9 | 65.5 | thermal |
| fp16 | smallint | E80 | 782.7 | 23.82 TFLOPS | 650.6 | 19.71 TFLOPS | 51.9 | 65.6 | thermal |
| fp16 | fp8grid | E80 | 773.2 | 23.37 TFLOPS | 661.5 | 19.98 TFLOPS | 54.2 | 65.6 | thermal |
| fp16 | nn_like | E80 | 780.0 | 23.70 TFLOPS | 665.2 | 20.12 TFLOPS | 54.7 | 65.6 | thermal |
| fp16 | neg_ones | E83 | 800.0 | 24.55 TFLOPS | 789.8 | 24.17 TFLOPS | 54.1 | 64.7 | none |
| fp16 | randn_small | E83 | 709.2 | 21.51 TFLOPS | 614.3 | 18.79 TFLOPS | 52.8 | 65.9 | thermal |
| fp16 | uniform01 | E83 | 769.2 | 23.35 TFLOPS | 632.0 | 19.24 TFLOPS | 52.5 | 65.8 | thermal |
| fp16 | sparse90 | E83 | 800.0 | 24.55 TFLOPS | 800.0 | 24.56 TFLOPS | 39.0 | 59.1 | none |
| fp16 | wsparse50 | E83 | 800.0 | 24.55 TFLOPS | 793.9 | 24.34 TFLOPS | 51.1 | 63.6 | none |
| fp16 | wsparse90 | E83 | 800.0 | 24.55 TFLOPS | 789.8 | 24.22 TFLOPS | 36.6 | 58.1 | none |
| fp16 | a_randn_b_zeros | E83 | 800.0 | 24.55 TFLOPS | 794.9 | 24.39 TFLOPS | 36.9 | 58.3 | none |
| fp16 | a_zeros_b_randn | E83 | 800.0 | 24.55 TFLOPS | 794.4 | 24.38 TFLOPS | 36.7 | 57.0 | none |
| fp16 | pair_half_zero | E83 | 737.7 | 22.38 TFLOPS | 619.2 | 18.92 TFLOPS | 51.6 | 65.8 | thermal |
| fp16 | randn_sorted | E83 | 734.0 | 22.12 TFLOPS | 620.8 | 18.97 TFLOPS | 52.5 | 65.8 | thermal |
| int8 | zeros | E80 (E83 re-run: 800.0 / 788.8) | 800.0 | 84.30 TOPS | 800.0 | 84.33 TOPS | 37.0 | 58.0 | none |
| int8 | neg_ones | E80 | 777.5 | 81.68 TOPS | 796.9 | 83.98 TOPS | 41.0 | 60.0 | none |
| int8 | full | E80 (E83 re-run: 800.0 / 786.5) | 800.0 | 84.30 TOPS | 793.4 | 83.54 TOPS | 53.2 | 64.9 | none |
| int8 | smallint | E80 | 798.0 | 84.31 TOPS | 795.4 | 83.80 TOPS | 51.0 | 64.4 | none |
| int8 | gauss_q | E80 | 800.0 | 84.31 TOPS | 794.4 | 83.70 TOPS | 52.1 | 64.6 | none |
| int8 | sparse50 | E80 | 800.0 | 84.30 TOPS | 789.3 | 83.15 TOPS | 49.0 | 63.6 | none |
| int8 | ones | E83 | 800.0 | 84.30 TOPS | 800.0 | 84.32 TOPS | 40.5 | 59.0 | none |
| int8 | pos | E83 | 800.0 | 84.30 TOPS | 791.8 | 83.31 TOPS | 51.4 | 64.8 | none |
| int8 | ternary | E83 | 800.0 | 84.30 TOPS | 797.2 | 84.01 TOPS | 48.5 | 62.6 | none |
| int8 | sparse90 | E83 | 800.0 | 84.31 TOPS | 794.9 | 83.76 TOPS | 39.6 | 59.3 | none |
| int8 | wsparse50 | E83 | 798.0 | 84.31 TOPS | 789.7 | 83.16 TOPS | 43.7 | 61.4 | none |
| int8 | wsparse90 | E83 | 779.1 | 82.10 TOPS | 800.0 | 84.33 TOPS | 37.8 | 57.0 | none |
| int8 | highbit | E83 | 800.0 | 84.31 TOPS | 789.8 | 83.08 TOPS | 44.0 | 61.9 | none |
| int8 | a_full_b_zeros | E83 | 800.0 | 84.32 TOPS | 794.4 | 83.70 TOPS | 37.9 | 58.8 | none |
| int8 | a_zeros_b_full | E83 | 800.0 | 84.30 TOPS | 794.9 | 83.74 TOPS | 37.1 | 57.2 | none |
| int8 | sorted | E83 | 775.5 | 81.52 TOPS | 789.3 | 82.97 TOPS | 51.8 | 65.0 | none |

51 kinds.
