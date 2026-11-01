# M4 and I3: frozen for E95

Written by `predict_m4.py`; D in W over the type's own zeros, on aifoundry3 card 0 at 600 MHz; no scale. The commit holding this file is the freeze. E94 is not a test of this form: it was read before the form was chosen.

**float:** core nets 1.624 ± 0.033 fJ, lane operand bus nets 7.533 ± 0.420 fJ, other nets 2.222 ± 0.099 fJ, clocked bits 1.066 ± 0.009 fJ; E78 fit rms 0.136 W, leave-one-out 0.155 W, over 33 kinds. Out-of-sample rms already read: e86 0.145, e90 0.220, e92 0.242, e82 after scale 0.159, e88 with e82's scale 0.214, e94 with e82's scale 0.178. Interval pool on this card: rms 0.202 W over 87.

**int8:** nets other than the lane operand bus 3.092 ± 0.292 fJ, lane operand bus nets 16.737 ± 4.743 fJ, clocked bits 1.795 ± 0.293 fJ; E78 fit rms 0.181 W, leave-one-out 0.248 W, over 15 kinds. Out-of-sample rms already read: e86 0.256, e90 0.237, e82 after scale 0.169, e88 with e82's scale 0.361, e94 with e82's scale 0.286. Interval pool on this card: rms 0.249 W over 19.

| tile | group | g | **D, W [95%]** | core | bus | other nets | clocks |
|---|---|---:|---:|---:|---:|---:|---:|
| `fp16.r2_bert_l6_up` | N | 0.000 | **22.13** [21.72, 22.55] | 8.26 | 1.04 | 4.63 | 8.20 |
| `fp16.real_l6_mlp_down` (E86 read) | E86 partner | 0.000 | **22.06** [21.65, 22.48] | 8.23 | 1.04 | 4.59 | 8.20 |
| `fp16.r2_gpt2_l6_mlp_down_fp16fwd` | F | 0.000 | **22.06** [21.65, 22.47] | 8.22 | 1.04 | 4.60 | 8.20 |
| `fp16.r2_vit_l5_down` | N | 0.000 | **21.88** [21.47, 22.29] | 8.06 | 1.03 | 4.58 | 8.21 |
| `fp16.real_l6_attn_qk` (E86 read) | E86 partner | 0.000 | **21.35** [20.94, 21.76] | 7.93 | 0.99 | 4.23 | 8.20 |
| `fp16.r2_gpt2_l6_attn_qk_fp16fwd` | F | 0.000 | **21.32** [20.91, 21.74] | 7.89 | 0.99 | 4.24 | 8.20 |
| `fp16.r2_gpt2_l9_attn_qk` | N | 0.000 | **21.10** [20.68, 21.51] | 7.83 | 0.99 | 4.07 | 8.20 |
| `fp16.r2_resnet18_l3c1` | Z | 0.367 | **14.04** [13.63, 14.44] | 4.59 | 1.04 | 3.31 | 5.09 |
| `fp16.r2_vgg16_fc2` | Z | 0.551 | **10.20** [9.79, 10.61] | 2.97 | 1.08 | 2.60 | 3.54 |
| `fp16.r2_t5small_l0_down` | Z | 0.871 | **3.48** [3.07, 3.89] | 0.77 | 0.91 | 0.95 | 0.84 |
| `fp32.r2_vit_l5_down` | N | 0.000 | **24.45** [23.99, 24.90] | 10.82 | 1.02 | 4.39 | 8.21 |
| `fp32.r2_gpt2_l3_mlp_down` | N | 0.000 | **24.43** [23.98, 24.88] | 10.93 | 1.01 | 4.28 | 8.21 |
| `fp32.r2_bert_l6_up` | N | 0.000 | **24.34** [23.90, 24.79] | 10.81 | 1.01 | 4.31 | 8.21 |
| `fp32.r2_gpt2_l9_attn_qk` | N | 0.000 | **23.87** [23.41, 24.33] | 10.71 | 1.01 | 3.94 | 8.21 |
| `fp32.r2_t5small_l0_up` | T | 0.000 | **21.84** [21.38, 22.29] | 8.88 | 0.70 | 4.04 | 8.21 |
| `fp32.r2_vit_l11_down` | M | 0.000 | **19.97** [19.56, 20.38] | 6.26 | 1.03 | 4.47 | 8.21 |
| `fp32.r2_resnet18_l2c1` | Z | 0.191 | **19.82** [19.39, 20.25] | 8.65 | 1.00 | 3.57 | 6.59 |
| `fp32.r2_gpt2_l6_mlp_down_bf16fwd` | B | 0.000 | **17.92** [17.52, 18.33] | 5.50 | 0.68 | 3.53 | 8.21 |
| `fp32.r2_resnet18_l3c1` | Z | 0.445 | **14.13** [13.71, 14.55] | 5.96 | 1.02 | 2.72 | 4.44 |
| `fp32.r2_vgg16_fc2` | Z | 0.723 | **7.82** [7.41, 8.23] | 3.00 | 1.03 | 1.70 | 2.09 |
| `fp32.r2_t5small_l0_down` | Z | 0.949 | **1.64** [1.24, 2.05] | 0.44 | 0.57 | 0.44 | 0.20 |
| `int8.r2_gpt2_l6_down_p999` | C | 0.000 | **5.54** [4.99, 6.09] | (all nets 2.93) | 1.32 | | 1.29 |
| `int8.r2_gpt2_l6_down_per_token` | C | 0.000 | **5.49** [4.94, 6.04] | (all nets 2.92) | 1.28 | | 1.29 |
| `int8.r2_gpt2_l6_down_p9999` | C | 0.000 | **5.42** [4.87, 5.97] | (all nets 2.87) | 1.27 | | 1.29 |
| `int8.r2_gpt2_l11_down_p999` | C | 0.000 | **5.38** [4.82, 5.93] | (all nets 2.81) | 1.27 | | 1.29 |
| `int8.real_l6_mlp_down` (E86 read) | E86 partner | 0.000 | **5.37** [4.82, 5.91] | (all nets 2.85) | 1.22 | | 1.29 |
| `int8.r2_vgg16_fc2_asym` | C | 0.000 | **4.67** [4.04, 5.30] | (all nets 1.97) | 1.41 | | 1.29 |
| `int8.r2_resnet18_l3c1` | Z | 0.176 | **4.52** [3.97, 5.07] | (all nets 2.32) | 1.14 | | 1.06 |
| `int8.r2_gpt2_l11_down_asym` | C | 0.000 | **4.35** [3.66, 5.04] | (all nets 1.60) | 1.46 | | 1.29 |
| `int8.r2_vgg16_fc2` | Z | 0.336 | **3.97** [3.41, 4.53] | (all nets 2.04) | 1.07 | | 0.86 |
| `int8.r2_vit_l11_down` | M | 0.547 | **2.87** [2.32, 3.42] | (all nets 1.45) | 0.84 | | 0.58 |
| `int8.r2_gpt2_l11_down_maxabs` | C | 0.637 | **2.53** [1.98, 3.08] | (all nets 1.29) | 0.77 | | 0.47 |
| `int8.r2_t5small_l0_down` | Z | 0.766 | **2.25** [1.70, 2.81] | (all nets 1.24) | 0.71 | | 0.30 |
