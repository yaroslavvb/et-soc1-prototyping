# E95: numbers the README quotes (readme-numbers.py)

## Kept passes per reduction
primary: k 0.2959 W/C over 167 runs; kept [9510, 9511, 9512, 9514]; runs kept 207/260; set aside [(9513, ['fp16.randn spans 1.776 W'])]
leak 0.1994: k 0.1994 W/C over -1 runs; kept [9511, 9512, 9514]; runs kept 157/260; set aside [(9510, ['fp32.randn spans 1.049 W']), (9513, ['fp16.randn spans 1.776 W'])]
leak 0.3803: k 0.3803 W/C over -1 runs; kept [9510, 9511, 9512]; runs kept 154/260; set aside [(9513, ['fp16.randn spans 1.776 W']), (9514, ['int8.zeros departs -0.279 W from its straight line'])]
leak 0: k 0.0000 W/C over -1 runs; kept [9511, 9512, 9514]; runs kept 157/260; set aside [(9510, ['fp32.randn spans 1.218 W']), (9513, ['fp16.randn spans 1.776 W'])]
dips removed: k 0.2989 W/C over 167 runs; kept [9510, 9511, 9512, 9513, 9514]; runs kept 260/260; set aside []
no A1: k 0.2938 W/C over 135 runs; kept [9510, 9511, 9512]; runs kept 154/207; set aside [(9513, ['fp16.randn spans 1.776 W'])]

## Runs per pass and the launch rule's skips
p9510: 50 runs; skipped [('fp16.randn', 4), ('int8.r2_gpt2_l6_down_p999', 24), ('fp32.r2_gpt2_l3_mlp_down', 38)]; block 1793522200133..1793522708895
   before #4 ran int8.r2_gpt2_l11_down_p999
   before #24 ran int8.r2_resnet18_l3c1
   before #38 ran fp32.r2_t5small_l0_down
p9511: 52 runs; skipped [('fp16.r2_gpt2_l9_attn_qk', 36)]; block 1793522724035..1793523248959
   before #36 ran int8.r2_t5small_l0_down
p9512: 52 runs; skipped [('int8.real_l6_mlp_down', 21)]; block 1793523264098..1793523795430
   before #21 ran int8.r2_vit_l11_down
p9513: 53 runs; skipped []; block 1793523810569..1793524341929
p9514: 53 runs; skipped []; block 1793524373246..1793524910074

## Tiles with fewer than the kept passes, primary
fp16.r2_gpt2_l9_attn_qk: n 3, values [20.8472, 21.0539, 20.9868]
fp32.r2_gpt2_l3_mlp_down: n 3, values [24.4087, 24.3512, 24.3353]
int8.r2_gpt2_l6_down_p999: n 3, values [5.7201, 5.8244, 5.8314]
int8.real_l6_mlp_down: n 3, values [5.5624, 5.6368, 5.8066]

## Primary against the 0.1994 arm (E78's slope), D in W
| tile | primary | 0.1994 arm (three passes) | difference |
|---|---|---|---|
| fp32.randn | 24.321 | 24.669 | -0.348 |
| fp16.randn | 21.906 | 22.160 | -0.254 |
| int8.full | 7.095 | 7.140 | -0.044 |
| fp32.r2_vit_l5_down | 24.416 | 24.701 | -0.285 |
| fp32.r2_vit_l11_down | 19.959 | 20.101 | -0.141 |
| fp32.r2_vgg16_fc2 | 7.806 | 7.870 | -0.064 |
| fp16.r2_vgg16_fc2 | 10.101 | 10.163 | -0.062 |
| int8.r2_vgg16_fc2 | 3.912 | 3.958 | -0.046 |
| fp32.r2_t5small_l0_up | 21.651 | 21.862 | -0.210 |

## Nested windows of one layer in three formats (r = D over the same pass's random kind of that format)
| layer | format | gate closes | live share | r primary | r dips-removed | D W | r ÷ live share | a live lane's cost ÷ random's | pJ/MAC (D) | pJ/MAC (S) |
|---|---|---|---|---|---|---|---|---|---|---|
| vgg16_fc2 | fp32 | 0.723 | 0.277 | 0.3210 ± 0.0118 | 0.3222 ± 0.0024 | 7.806 ± 0.230 | 1.157 | 1.063 | 1.700 | 2.139 |
| vgg16_fc2 | fp16 | 0.551 | 0.449 | 0.4611 ± 0.0107 | 0.4614 ± 0.0073 | 10.101 ± 0.208 | 1.026 | 0.975 | 1.100 | 1.310 |
| vgg16_fc2 | int8 | 0.336 | 0.664 | 0.5513 ± 0.0199 | 0.5473 ± 0.0173 | 3.912 ± 0.170 | 0.830 | 0.806 | 0.124 | 0.205 |
| resnet18_l3c1 | fp32 | 0.445 | 0.555 | 0.5781 ± 0.0040 | 0.5750 ± 0.0027 | 14.060 ± 0.072 | 1.042 | 1.002 | 3.061 | 3.501 |
| resnet18_l3c1 | fp16 | 0.367 | 0.633 | 0.6371 ± 0.0042 | 0.6359 ± 0.0044 | 13.956 ± 0.118 | 1.007 | 0.976 | 1.520 | 1.740 |
| resnet18_l3c1 | int8 | 0.176 | 0.824 | 0.6130 ± 0.0292 | 0.6137 ± 0.0200 | 4.350 ± 0.231 | 0.744 | 0.736 | 0.138 | 0.219 |
| t5small_l0_down | fp32 | 0.949 | 0.051 | 0.0671 ± 0.0058 | 0.0668 ± 0.0042 | 1.633 ± 0.152 | 1.322 | 0.761 | 0.356 | 0.792 |
| t5small_l0_down | fp16 | 0.871 | 0.129 | 0.1610 ± 0.0053 | 0.1618 ± 0.0043 | 3.526 ± 0.121 | 1.249 | 1.015 | 0.384 | 0.610 |
| t5small_l0_down | int8 | 0.766 | 0.234 | 0.3061 ± 0.0172 | 0.3034 ± 0.0136 | 2.172 ± 0.132 | 1.306 | 1.128 | 0.069 | 0.149 |
| resnet18_l2c1 | fp32 | 0.191 | 0.809 | 0.8087 ± 0.0097 | 0.8052 ± 0.0022 | 19.667 ± 0.085 | 1.000 | 0.977 | 4.284 | 4.718 |
| gpt2_l11_down_maxabs | int8 | 0.637 | 0.363 | 0.3321 ± 0.0271 | 0.3356 ± 0.0210 | 2.357 ± 0.201 | 0.914 | 0.820 | 0.075 | 0.154 |
| vit_l11_down | int8 | 0.547 | 0.453 | 0.4072 ± 0.0170 | 0.4066 ± 0.0116 | 2.889 ± 0.136 | 0.899 | 0.835 | 0.092 | 0.173 |

## D ÷ (c), range per format, primary
fp32: D/(c) 0.845..1.059; D-(c) -0.462..+0.433 W, rms 0.351; D-(a) +0.005..+0.782 W, rms 0.496; tiles 4
fp16: D/(c) 0.976..1.012; D-(c) -0.333..+0.042 W, rms 0.242; D-(a) +0.766..+1.272 W, rms 1.090; tiles 3
int8: D/(c) 0.739..1.108; D-(c) -1.537..+0.211 W, rms 0.863; D-(a) +0.734..+1.379 W, rms 1.148; tiles 5

## Baselines of the no-zero and special tiles, D ÷, S ÷, whole board ÷ random (primary, then dips removed)
| tile | D ÷ random | S ÷ random | board ÷ random | D ÷ random, dips removed |
|---|---|---|---|---|
| fp32.r2_gpt2_l3_mlp_down | 0.9999 ± 0.0093 | 0.9985 ± 0.0048 | 0.9995 ± 0.0053 | 0.9957 ± 0.0046 |
| fp32.r2_gpt2_l9_attn_qk | 0.9736 ± 0.0418 | 0.9721 ± 0.0371 | 0.9869 ± 0.0200 | 0.9799 ± 0.0030 |
| fp32.r2_bert_l6_up | 0.9994 ± 0.0067 | 0.9961 ± 0.0132 | 1.0000 ± 0.0048 | 0.9942 ± 0.0029 |
| fp32.r2_vit_l5_down | 1.0040 ± 0.0114 | 1.0028 ± 0.0099 | 1.0017 ± 0.0059 | 0.9985 ± 0.0043 |
| fp32.r2_t5small_l0_up | 0.8903 ± 0.0138 | 0.8983 ± 0.0144 | 0.9487 ± 0.0053 | 0.8857 ± 0.0066 |
| fp32.r2_vit_l11_down | 0.8208 ± 0.0397 | 0.8319 ± 0.0431 | 0.9162 ± 0.0174 | 0.8259 ± 0.0042 |
| fp32.r2_gpt2_l6_mlp_down_bf16fwd | 0.7331 ± 0.0080 | 0.7515 ± 0.0078 | 0.8750 ± 0.0044 | 0.7297 ± 0.0019 |
| fp16.r2_gpt2_l9_attn_qk | 0.9568 ± 0.0110 | 0.9633 ± 0.0193 | 0.9807 ± 0.0037 | 0.9562 ± 0.0060 |
| fp16.r2_bert_l6_up | 0.9924 ± 0.0127 | 0.9933 ± 0.0092 | 0.9962 ± 0.0057 | 0.9964 ± 0.0020 |
| fp16.r2_vit_l5_down | 0.9859 ± 0.0091 | 0.9887 ± 0.0100 | 0.9937 ± 0.0026 | 0.9862 ± 0.0063 |
| fp16.real_l6_attn_qk | 0.9675 ± 0.0055 | 0.9690 ± 0.0124 | 0.9854 ± 0.0013 | 0.9672 ± 0.0038 |
| fp16.r2_gpt2_l6_attn_qk_fp16fwd | 0.9665 ± 0.0050 | 0.9717 ± 0.0092 | 0.9855 ± 0.0015 | 0.9660 ± 0.0037 |
| fp16.real_l6_mlp_down | 0.9958 ± 0.0040 | 0.9986 ± 0.0055 | 0.9983 ± 0.0012 | 0.9951 ± 0.0032 |
| fp16.r2_gpt2_l6_mlp_down_fp16fwd | 0.9955 ± 0.0026 | 0.9959 ± 0.0081 | 0.9973 ± 0.0014 | 0.9947 ± 0.0028 |

## ΔT against the same pass's random kind (firmware's whole-degree reading, primary)
fp32.r2_vit_l5_down: dT 3.12 C, minus random 0.07 ± 0.74 C
fp32.r2_vgg16_fc2: dT 1.13 C, minus random -1.92 ± 0.24 C
fp32.r2_t5small_l0_down: dT 1.00 C, minus random -2.05 ± 0.36 C
fp16.r2_vgg16_fc2: dT 1.14 C, minus random -1.66 ± 0.36 C
fp16.r2_t5small_l0_down: dT 0.75 C, minus random -2.04 ± 0.81 C
int8.r2_vgg16_fc2: dT 1.00 C, minus random 0.00 ± 0.00 C
int8.r2_gpt2_l11_down_maxabs: dT 0.82 C, minus random -0.18 ± 0.56 C

## E78's cells beside (predictions-e95.json e78_beside)
fp32.randn: 24.7249 ± 0.0823
fp16.randn: 22.1624 ± 0.0545
int8.full: 7.0565 ± 0.0595
fp32.zeros: 0.0 ± 0.0
fp16.zeros: 0.0 ± 0.0
int8.zeros: 0.0 ± 0.0
anchor_pi: 8.3603 ± 0.0716
fp32.bf16trunc: 18.1359 ± 0.0465
fp32.fp16grid: 19.6238 ± 0.0647
fp32.nn_like: 13.0356 ± 0.0662
fp16.nn_like: 17.602 ± 0.1185
int8.gauss_q: 6.598 ± 0.0692
fp32.sparse50: 7.3019 ± 0.0626
fp16.sparse50: 13.196 ± 0.5399
int8.sparse50: 5.4634 ± 0.1458
fp32.a_randn_b_zeros: 0.6162 ± 0.1218
fp32.a_zeros_b_randn: 0.8104 ± 0.0645
fp16.a_randn_b_zeros: 0.6586 ± 0.08
fp16.a_zeros_b_randn: 0.7822 ± 0.0633

## Calibration tiles, primary and dips removed
| layer | calibration | gate | bus bits/op | D W | r | S W | whole board ÷ random | D W, dips removed |
|---|---|---|---|---|---|---|---|---|
| GPT-2 l11 | max-abs | 0.637 | 7330 | 2.357 ± 0.201 | 0.3321 ± 0.0271 | 4.859 ± 0.323 | 0.8668 ± 0.0068 | 2.382 ± 0.155 |
| GPT-2 l11 | asymmetric | 0.000 | 14114 | 4.044 ± 0.467 | 0.5698 ± 0.0613 | 6.553 ± 0.581 | 0.9130 ± 0.0120 | 4.159 ± 0.077 |
| GPT-2 l11 | p99.9 clip | 0.000 | 42146 | 5.520 ± 0.224 | 0.7779 ± 0.0259 | 8.025 ± 0.238 | 0.9560 ± 0.0024 | 5.510 ± 0.154 |
| VGG fc2 | symmetric | 0.336 | 19732 | 3.912 ± 0.170 | 0.5513 ± 0.0199 | 6.476 ± 0.066 | 0.9105 ± 0.0008 | 3.884 ± 0.136 |
| VGG fc2 | asymmetric | 0.000 | 22836 | 4.732 ± 0.121 | 0.6669 ± 0.0116 | 7.272 ± 0.177 | 0.9330 ± 0.0017 | 4.717 ± 0.091 |
| GPT-2 l6 | committed (max-abs) | 0.000 | 45684 | 5.669 ± 0.311 | 0.7999 ± 0.0565 | 8.141 ± 0.468 | 0.9591 ± 0.0063 | 5.696 ± 0.186 |
| GPT-2 l6 | p99.99 clip | 0.000 | 44500 | 5.644 ± 0.202 | 0.7954 ± 0.0214 | 8.154 ± 0.265 | 0.9596 ± 0.0036 | 5.659 ± 0.144 |
| GPT-2 l6 | per token | 0.000 | 46996 | 5.525 ± 0.708 | 0.7785 ± 0.0946 | 8.105 ± 0.702 | 0.9565 ± 0.0171 | 5.715 ± 0.140 |
| GPT-2 l6 | p99.9 clip | 0.000 | 47092 | 5.792 ± 0.155 | 0.8177 ± 0.0267 | 8.302 ± 0.651 | 0.9628 ± 0.0063 | 5.772 ± 0.099 |

## The E78 reference: S and pJ per MAC of random, primary
fp32.randn: D 24.321 ± 0.202, S 26.354 ± 0.247, pJ/MAC (S) 5.739, (D) 5.297
fp16.randn: D 21.906 ± 0.091, S 23.880 ± 0.123, pJ/MAC (S) 2.601, (D) 2.386
int8.full: D 7.095 ± 0.065, S 9.637 ± 0.140, pJ/MAC (S) 0.305, (D) 0.225

GPT-2 layer 11, p99.9 - asymmetric, paired per pass (primary): +1.475 +- 0.305 W over 4 passes

idle level 25.864 ± 0.009 W
