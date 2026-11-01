# E112b results (score_e112b.py; registration tools/claims-v3/e112/E112.md): E95's pass on aifoundry1 card 1

The tables below are score_e95.py's own (write_md), on the card-1 view of the frozen file; C7 and C8 by the ports with the scaled thresholds. 'at the arms' lists the arms' verdicts; a claim's verdict at the frozen thresholds unscaled is in scored.json (claims.<C>.at_frozen_thresholds_unscaled_labelled).

## Cross-card rules (E112b-X1, X4, X5)

Primary pairing: E112b primary (dips removed, auto) against E95's dips-removed arm (auto).

| rule | verdict | at the arms | detail |
|---|---|---|---|
| E112b-X1 rank | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | fp32 rho — (n 0 of 12) NOT SCORED; fp16 rho — (n 0 of 11) NOT SCORED; int8 rho — (n 0 of 13) NOT SCORED |
| E112b-X4 scale | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | median D(aifoundry3)/D(card 1) — over 0 of 24 eligible tiles, band [1.0008, 1.0608]; per type fp32 —, fp16 —, int8 — |
| E112b-X5 tile ratios | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | 0 of 0 resolved agree (of 33); disagree: none |

| tile | D card 1 W | D aifoundry3 W | ratio a3/c1 | r card 1 | r aifoundry3 | r diff | ± (quadrature) | band | agrees |
|---|---|---|---|---|---|---|---|---|---|
| fp16.r2_bert_l6_up | 20.834 ± 0.335 | 21.823 ± 0.066 | — | 0.9904 ± 0.0200 | 0.9964 ± 0.0020 | — | — | 0.03 | False |
| fp16.r2_gpt2_l6_attn_qk_fp16fwd | 20.336 ± 0.704 | 21.158 ± 0.098 | — | 0.9667 ± 0.0375 | 0.9660 ± 0.0037 | — | — | 0.03 | False |
| fp16.r2_gpt2_l6_mlp_down_fp16fwd | 20.843 ± 1.087 | 21.787 ± 0.061 | — | 0.9908 ± 0.0476 | 0.9947 ± 0.0028 | — | — | 0.03 | False |
| fp16.r2_gpt2_l9_attn_qk | 20.056 ± 0.740 | 20.947 ± 0.139 | — | 0.9534 ± 0.0391 | 0.9562 ± 0.0060 | — | — | 0.03 | False |
| fp16.r2_resnet18_l3c1 | 13.286 ± 0.296 | 13.927 ± 0.103 | — | 0.6316 ± 0.0115 | 0.6359 ± 0.0044 | — | — | 0.03 | False |
| fp16.r2_t5small_l0_down | 3.374 ± 0.840 | 3.544 ± 0.100 | — | 0.1604 ± 0.0393 | 0.1618 ± 0.0043 | — | — | 0.03 | False |
| fp16.r2_vgg16_fc2 | 9.748 ± 2.099 | 10.105 ± 0.142 | — | 0.4634 ± 0.0978 | 0.4614 ± 0.0073 | — | — | 0.03 | False |
| fp16.r2_vit_l5_down | 20.696 ± 1.014 | 21.600 ± 0.083 | — | 0.9838 ± 0.0441 | 0.9862 ± 0.0063 | — | — | 0.03 | False |
| fp16.randn | 21.036 ± 0.087 | 21.902 ± 0.063 | — | — | — | — | — | — | — |
| fp16.real_l6_attn_qk | 20.218 ± 0.136 | 21.185 ± 0.101 | — | 0.9611 ± 0.0105 | 0.9672 ± 0.0038 | — | — | 0.03 | False |
| fp16.real_l6_mlp_down | 20.851 ± 0.674 | 21.796 ± 0.063 | — | 0.9912 ± 0.0361 | 0.9951 ± 0.0032 | — | — | 0.03 | False |
| fp32.r2_bert_l6_up | 23.309 ± 2.049 | 24.292 ± 0.053 | — | 0.9955 ± 0.0606 | 0.9942 ± 0.0029 | — | — | 0.03 | False |
| fp32.r2_gpt2_l3_mlp_down | 23.440 ± 0.145 | 24.337 ± 0.077 | — | 1.0011 ± 0.0209 | 0.9957 ± 0.0046 | — | — | 0.03 | False |
| fp32.r2_gpt2_l6_mlp_down_bf16fwd | 17.000 ± 0.060 | 17.831 ± 0.056 | — | 0.7260 ± 0.0222 | 0.7297 ± 0.0019 | — | — | 0.03 | False |
| fp32.r2_gpt2_l9_attn_qk | 22.987 ± 1.183 | 23.943 ± 0.055 | — | 0.9817 ± 0.0240 | 0.9799 ± 0.0030 | — | — | 0.03 | False |
| fp32.r2_resnet18_l2c1 | 18.836 ± 0.430 | 19.676 ± 0.073 | — | 0.8044 ± 0.0034 | 0.8052 ± 0.0022 | — | — | 0.03 | False |
| fp32.r2_resnet18_l3c1 | 13.461 ± 0.230 | 14.050 ± 0.050 | — | 0.5749 ± 0.0254 | 0.5750 ± 0.0027 | — | — | 0.03 | False |
| fp32.r2_t5small_l0_down | 1.772 ± 2.417 | 1.633 ± 0.103 | — | 0.0757 ± 0.1053 | 0.0668 ± 0.0042 | — | — | 0.03 | False |
| fp32.r2_t5small_l0_up | 20.711 ± 0.950 | 21.643 ± 0.142 | — | 0.8845 ± 0.0645 | 0.8857 ± 0.0066 | — | — | 0.03 | False |
| fp32.r2_vgg16_fc2 | 7.539 ± 2.006 | 7.874 ± 0.058 | — | 0.3220 ± 0.0944 | 0.3222 ± 0.0024 | — | — | 0.03 | False |
| fp32.r2_vit_l11_down | 19.386 ± 0.588 | 20.180 ± 0.081 | — | 0.8280 ± 0.0475 | 0.8259 ± 0.0042 | — | — | 0.03 | False |
| fp32.r2_vit_l5_down | 23.278 ± 0.497 | 24.398 ± 0.104 | — | 0.9942 ± 0.0057 | 0.9985 ± 0.0043 | — | — | 0.03 | False |
| fp32.randn | 23.415 ± 0.633 | 24.435 ± 0.041 | — | — | — | — | — | — | — |
| int8.full | 6.719 ± 0.790 | 7.097 ± 0.045 | — | — | — | — | — | — | — |
| int8.r2_gpt2_l11_down_asym | 3.989 ± 0.788 | 4.159 ± 0.077 | — | 0.5939 ± 0.1872 | 0.5860 ± 0.0088 | — | — | 0.06 | False |
| int8.r2_gpt2_l11_down_maxabs | 2.348 ± 0.339 | 2.382 ± 0.155 | — | 0.3495 ± 0.0094 | 0.3356 ± 0.0210 | — | — | 0.06 | False |
| int8.r2_gpt2_l11_down_p999 | 5.236 ± 0.051 | 5.510 ± 0.154 | — | 0.7794 ± 0.0840 | 0.7764 ± 0.0181 | — | — | 0.06 | False |
| int8.r2_gpt2_l6_down_p999 | 5.428 ± 0.562 | 5.772 ± 0.099 | — | 0.8080 ± 0.1786 | 0.8142 ± 0.0176 | — | — | 0.06 | False |
| int8.r2_gpt2_l6_down_p9999 | 5.339 ± 0.138 | 5.659 ± 0.144 | — | 0.7947 ± 0.0729 | 0.7973 ± 0.0155 | — | — | 0.06 | False |
| int8.r2_gpt2_l6_down_per_token | 5.432 ± 1.592 | 5.715 ± 0.140 | — | 0.8084 ± 0.1420 | 0.8052 ± 0.0188 | — | — | 0.06 | False |
| int8.r2_resnet18_l3c1 | 4.064 ± 0.319 | 4.356 ± 0.158 | — | 0.6049 ± 0.0236 | 0.6137 ± 0.0200 | — | — | 0.06 | False |
| int8.r2_t5small_l0_down | 2.107 ± 1.407 | 2.153 ± 0.102 | — | 0.3134 ± 0.1726 | 0.3034 ± 0.0136 | — | — | 0.06 | False |
| int8.r2_vgg16_fc2 | 3.572 ± 0.577 | 3.884 ± 0.136 | — | 0.5317 ± 0.0233 | 0.5473 ± 0.0173 | — | — | 0.06 | False |
| int8.r2_vgg16_fc2_asym | 4.388 ± 0.973 | 4.717 ± 0.091 | — | 0.6533 ± 0.2217 | 0.6646 ± 0.0101 | — | — | 0.06 | False |
| int8.r2_vit_l11_down | 2.643 ± 1.144 | 2.886 ± 0.092 | — | 0.3933 ± 0.1240 | 0.4066 ± 0.0116 | — | — | 0.06 | False |
| int8.real_l6_mlp_down | 5.487 ± 0.164 | 5.696 ± 0.186 | — | 0.8168 ± 0.1204 | 0.8032 ± 0.0315 | — | — | 0.06 | False |

## The same-session tie: E86's three tiles in (b) against (a) (reported)

| tile | (b) D W | (a) D W | diff W | band | verdict |
|---|---|---|---|---|---|
| fp16.real_l6_mlp_down | 20.851 ± 0.674 | 20.851 ± 0.056 | — | ±0.5 | NOT SCORED |
| int8.real_l6_mlp_down | 5.487 ± 0.164 | 5.325 ± 0.229 | — | ±0.5 | NOT SCORED |
| fp16.real_l6_attn_qk | 20.218 ± 0.136 | 20.270 ± 0.060 | — | ±0.5 | NOT SCORED |

Claims tally: {'NOT SCORED': 13}; cross-card tally: {'NOT SCORED': 3}

Passes kept: [11250, 11251] (2); leak {'mode': 'auto', 'k_w_per_c': 0.4172138255135273, 'n_runs': 98}; clock 600 MHz; mean minion voltage 498.6 mV; runs kept 106/159.

## The frozen claims (real2/predictions-real2.json claims.E95)

| claim | verdict | at the arms | detail |
|---|---|---|---|
| C1 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | gpt2/fp32 0.9914 ± 0.0015 UNDER-RESOLVED; gpt2/fp16 0.9534 ± 0.0391 UNDER-RESOLVED; bert/fp32 0.9955 ± 0.0606 UNDER-RESOLVED; bert/fp16 0.9904 ± 0.0200 UNDER-RESOLVED; vit/fp32 0.9942 ± 0.0057 UNDER-RESOLVED; vit/fp16 0.9838 ± 0.0441 UNDER-RESOLVED |
| C2 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | fp32 0.9931 ± 0.0145 UNDER-RESOLVED; fp16 0.9759 ± 0.0050 UNDER-RESOLVED |
| C3a | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | 0 of 7 inside the gate law's interval |
| C3b | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | fp32 slope/L — UNDER-RESOLVED; fp16 slope/L — UNDER-RESOLVED |
| C4 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | vgg16_fc2 0.1414 ± 0.0035 UNDER-RESOLVED; resnet18_l3c1 0.0567 ± 0.0139 UNDER-RESOLVED; t5small_l0_down 0.0847 ± 0.0660 UNDER-RESOLVED |
| C5 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | int8/resnet18_l3c1 D 4.064 ± 0.319, nearer None; int8/vgg16_fc2 D 3.572 ± 0.577, nearer None |
| C6 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | p99.9 - max-abs 2.888 ± 0.288 W (threshold 1.9473) |
| C7 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | p9999 -0.148 ± 0.302 W; per_token -0.055 ± 1.756 W; p999 -0.059 ± 0.398 W; Spearman — |
| C8 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | asym - symmetric 0.816 ± 1.550 W |
| C9 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | D 19.386 ± 0.588 W, threshold 11.5619; lands on: gate blind to -0.0; r 0.8280 ± 0.0475 |
| C10 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | r 0.8845 ± 0.0645 (threshold 0.97) |
| C11 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | fp16 pass - rounded -0.009 ± 1.761 W (band ±0.4839) |
| C12 | **NOT SCORED** | dips_kept NOT SCORED, leak0.1994 NOT SCORED, leak0.545 NOT SCORED, leak0.3803 NOT SCORED, leak0 NOT SCORED | 0 of 25 inside (a); E86-only arm 0; tier 2 apart 0 of 5 |

## Every tile

| tile | tier | gate closes | bus bits/op | D W ± 95% | D ÷ random | S ÷ random | whole board ÷ random | (a) W [interval] | in | (c) W [interval] | in | S W | pJ/MAC (S) | pJ/MAC (D) | ΔT °C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp16.r2_bert_l6_up | 1 | 0.000 | 84270 | 20.834 ± 0.335 | 0.9904 ± 0.0200 | 0.9884 ± 0.0352 | 0.9968 ± 0.0068 | 20.8162 [17.7627, 23.8698] | no | — | — | 22.606 | 2.462 | 2.269 | 2.43 |
| fp16.r2_gpt2_l6_attn_qk_fp16fwd | 2 | 0.000 | 80964 | 20.336 ± 0.704 | 0.9667 ± 0.0375 | 0.9703 ± 0.0465 | 0.9873 ± 0.0146 | 20.6672 [17.6137, 23.7207] | no | — | — | 22.192 | 2.417 | 2.214 | 2.37 |
| fp16.r2_gpt2_l6_mlp_down_fp16fwd | 1 | 0.000 | 82986 | 20.843 ± 1.087 | 0.9908 ± 0.0476 | 0.9931 ± 0.1008 | 0.9970 ± 0.0169 | 20.5694 [17.5159, 23.623] | no | — | — | 22.713 | 2.472 | 2.269 | 2.70 |
| fp16.r2_gpt2_l9_attn_qk | 1 | 0.000 | 83322 | 20.056 ± 0.740 | 0.9534 ± 0.0391 | 0.9561 ± 0.0883 | 0.9827 ± 0.0153 | 20.8162 [17.7627, 23.8698] | no | — | — | 21.868 | 2.381 | 2.184 | 2.32 |
| fp16.r2_resnet18_l3c1 | 1 | 0.367 | 78572 | 13.286 ± 0.296 | 0.6316 ± 0.0115 | 0.6614 ± 0.0087 | 0.8615 ± 0.0065 | 12.7658 [9.7229, 15.8086] | no | 13.8294 [12.7038, 14.955] | no | 15.127 | 1.648 | 1.447 | 1.68 |
| fp16.r2_t5small_l0_down | 1 | 0.871 | 48432 | 3.374 ± 0.840 | 0.1604 ± 0.0393 | 0.2249 ± 0.0427 | 0.6842 ± 0.0140 | 2.2831 [0.0, 5.326] | no | 3.3719 [2.2463, 4.4975] | no | 5.143 | 0.560 | 0.367 | 0.50 |
| fp16.r2_vgg16_fc2 | 1 | 0.551 | 74852 | 9.748 ± 2.099 | 0.4634 ± 0.0978 | 0.5021 ± 0.0469 | 0.7981 ± 0.0394 | 8.545 [5.5022, 11.5879] | no | 10.02 [8.8944, 11.1456] | no | 11.484 | 1.250 | 1.061 | 1.00 |
| fp16.r2_vit_l5_down | 1 | 0.000 | 83684 | 20.696 ± 1.014 | 0.9838 ± 0.0441 | 0.9830 ± 0.0237 | 0.9934 ± 0.0119 | 20.9401 [17.8866, 23.9936] | no | — | — | 22.482 | 2.448 | 2.253 | 2.40 |
| fp16.real_l6_attn_qk | 1 | 0.000 | 81324 | 20.218 ± 0.136 | 0.9611 ± 0.0105 | 0.9676 ± 0.0498 | 0.9857 ± 0.0024 | — | — | — | — | 22.130 | 2.410 | 2.202 | 1.93 |
| fp16.real_l6_mlp_down | 1 | 0.000 | 83370 | 20.851 ± 0.674 | 0.9912 ± 0.0361 | 0.9938 ± 0.0468 | 0.9968 ± 0.0115 | — | — | — | — | 22.730 | 2.475 | 2.270 | 2.68 |
| fp32.r2_bert_l6_up | 1 | 0.000 | 82334 | 23.309 ± 2.049 | 0.9955 ± 0.0606 | 0.9979 ± 0.0205 | 0.9975 ± 0.0111 | 23.6899 [21.3006, 26.0792] | no | — | — | 25.173 | 5.485 | 5.079 | 2.72 |
| fp32.r2_gpt2_l3_mlp_down | 1 | 0.000 | 82110 | 23.440 ± 0.145 | 1.0011 ± 0.0209 | 1.0057 ± 0.0450 | 1.0005 ± 0.0000 | 23.6588 [21.2696, 26.0481] | no | — | — | 25.370 | 5.524 | 5.104 | 3.20 |
| fp32.r2_gpt2_l6_mlp_down_bf16fwd | 2 | 0.000 | 32384 | 17.000 ± 0.060 | 0.7260 ± 0.0222 | 0.7437 ± 0.0755 | 0.8896 ± 0.0213 | 16.7745 [14.3852, 19.1638] | no | — | — | 18.759 | 4.083 | 3.701 | 1.90 |
| fp32.r2_gpt2_l9_attn_qk | 1 | 0.000 | 84644 | 22.987 ± 1.183 | 0.9817 ± 0.0240 | 0.9827 ± 0.0045 | 0.9924 ± 0.0094 | 23.7705 [21.3812, 26.1598] | no | — | — | 24.789 | 5.400 | 5.007 | 2.73 |
| fp32.r2_resnet18_l2c1 | 1 | 0.191 | 80128 | 18.836 ± 0.430 | 0.8044 ± 0.0034 | 0.8179 ± 0.0067 | 0.9221 ± 0.0059 | 19.089 [16.0366, 22.1414] | no | 19.5424 [17.0502, 22.0346] | no | 20.632 | 4.493 | 4.102 | 1.98 |
| fp32.r2_resnet18_l3c1 | 1 | 0.445 | 78630 | 13.461 ± 0.230 | 0.5749 ± 0.0254 | 0.6081 ± 0.0314 | 0.8294 ± 0.0084 | 13.2542 [10.2018, 16.3065] | no | 13.6231 [11.1309, 16.1153] | no | 15.339 | 3.342 | 2.933 | 1.50 |
| fp32.r2_t5small_l0_down | 1 | 0.949 | 25680 | 1.772 ± 2.417 | 0.0757 ± 0.1053 | 0.1404 ± 0.1197 | 0.6281 ± 0.0382 | 1.1437 [0.0, 4.196] | no | 1.8767 [0.0, 4.3689] | no | 3.542 | 0.771 | 0.386 | 0.02 |
| fp32.r2_t5small_l0_up | 1 | 0.000 | 49830 | 20.711 ± 0.950 | 0.8845 ± 0.0645 | 0.8918 ± 0.0484 | 0.9543 ± 0.0227 | 21.8016 [19.4123, 24.1909] | no | — | — | 22.496 | 4.901 | 4.512 | 2.30 |
| fp32.r2_vgg16_fc2 | 1 | 0.723 | 71262 | 7.539 ± 2.006 | 0.3220 ± 0.0944 | 0.3727 ± 0.0883 | 0.7278 ± 0.0338 | 6.8193 [3.7669, 9.8717] | no | 7.1581 [4.6659, 9.6503] | no | 9.401 | 2.048 | 1.642 | 1.00 |
| fp32.r2_vit_l11_down | 1 | 0.000 | 70024 | 19.386 ± 0.588 | 0.8280 ± 0.0475 | 0.8402 ± 0.0245 | 0.9311 ± 0.0070 | 19.8278 [17.4385, 22.2171] | no | — | — | 21.195 | 4.616 | 4.222 | 2.38 |
| fp32.r2_vit_l5_down | 1 | 0.000 | 82206 | 23.278 ± 0.497 | 0.9942 ± 0.0057 | 0.9961 ± 0.0168 | 0.9981 ± 0.0098 | 23.6957 [21.3064, 26.085] | no | — | — | 25.126 | 5.476 | 5.074 | 2.58 |
| int8.r2_gpt2_l11_down_asym | 2 | 0.000 | 14114 | 3.989 ± 0.788 | 0.5939 ± 0.1872 | 0.6945 ± 0.1023 | 0.9319 ± 0.0138 | 3.8703 [2.8752, 4.8653] | no | — | — | 6.336 | 0.201 | 0.127 | 0.50 |
| int8.r2_gpt2_l11_down_maxabs | 1 | 0.637 | 7330 | 2.348 ± 0.339 | 0.3495 ± 0.0094 | 0.5303 ± 0.0175 | 0.8973 ± 0.0044 | 1.1294 [0.0487, 2.2102] | no | 2.7447 [1.7146, 3.7748] | no | 4.837 | 0.153 | 0.074 | 0.02 |
| int8.r2_gpt2_l11_down_p999 | 1 | 0.000 | 42146 | 5.236 ± 0.051 | 0.7794 ± 0.0840 | 0.8335 ± 0.1285 | 0.9645 ± 0.0006 | 5.0182 [4.0231, 6.0133] | no | — | — | 7.603 | 0.241 | 0.166 | 0.50 |
| int8.r2_gpt2_l6_down_p999 | 1 | 0.000 | 47092 | 5.428 ± 0.562 | 0.8080 ± 0.1786 | 0.8594 ± 0.1431 | 0.9695 ± 0.0146 | 5.284 [4.2889, 6.2791] | no | — | — | 7.840 | 0.249 | 0.172 | 0.68 |
| int8.r2_gpt2_l6_down_p9999 | 1 | 0.000 | 44500 | 5.339 ± 0.138 | 0.7947 ± 0.0729 | 0.8487 ± 0.1634 | 0.9677 ± 0.0197 | 5.0864 [4.0913, 6.0814] | no | — | — | 7.742 | 0.246 | 0.169 | 0.50 |
| int8.r2_gpt2_l6_down_per_token | 1 | 0.000 | 46996 | 5.432 ± 1.592 | 0.8084 ± 0.1420 | 0.8739 ± 0.0824 | 0.9695 ± 0.0058 | 5.2129 [4.2179, 6.208] | no | — | — | 7.972 | 0.253 | 0.172 | 1.00 |
| int8.r2_resnet18_l3c1 | 1 | 0.176 | 26958 | 4.064 ± 0.319 | 0.6049 ± 0.0236 | 0.7109 ± 0.1375 | 0.9361 ± 0.0214 | 3.5207 [2.44, 4.6015] | no | 5.7319 [4.7018, 6.762] | no | 6.485 | 0.206 | 0.129 | 1.00 |
| int8.r2_t5small_l0_down | 2 | 0.766 | 6752 | 2.107 ± 1.407 | 0.3134 ± 0.1726 | 0.4961 ± 0.1642 | 0.8916 ± 0.0152 | 0.7721 [0.0, 1.8529] | no | 1.9093 [0.8792, 2.9395] | no | 4.526 | 0.144 | 0.067 | 0.00 |
| int8.r2_vgg16_fc2 | 1 | 0.336 | 19732 | 3.572 ± 0.577 | 0.5317 ± 0.0233 | 0.6601 ± 0.0723 | 0.9256 ± 0.0036 | 2.6337 [1.553, 3.7145] | no | 4.694 [3.6638, 5.7241] | no | 6.021 | 0.191 | 0.113 | 0.50 |
| int8.r2_vgg16_fc2_asym | 1 | 0.000 | 22836 | 4.388 ± 0.973 | 0.6533 ± 0.2217 | 0.7553 ± 0.1541 | 0.9460 ± 0.0388 | 3.9929 [2.9979, 4.988] | no | — | — | 6.890 | 0.218 | 0.139 | 0.50 |
| int8.r2_vit_l11_down | 2 | 0.547 | 16434 | 2.643 ± 1.144 | 0.3933 ± 0.1240 | 0.5419 ± 0.1254 | 0.9003 ± 0.0217 | 1.7204 [0.6397, 2.8012] | no | 3.327 [2.2968, 4.3571] | no | 4.943 | 0.157 | 0.084 | 0.50 |
| int8.real_l6_mlp_down | 1 | 0.000 | 45684 | 5.487 ± 0.164 | 0.8168 ± 0.1204 | 0.8617 ± 0.0333 | 0.9680 ± 0.0175 | — | — | — | — | 7.861 | 0.249 | 0.174 | 1.00 |
| fp32.zeros | 1 | 1.000 | 0 | 0.000 ± 0.000 | 0.0000 ± 0.0000 | 0.0706 ± 0.0001 | 0.5978 ± 0.0051 | — | — | — | — | 1.782 | 0.388 | 0.000 | -0.45 |
| fp32.randn | 1 | 0.000 | 82214 | 23.415 ± 0.633 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | — | — | — | — | 25.225 | 5.496 | 5.102 | 2.78 |
| fp16.zeros | 1 | 1.000 | 0 | 0.000 ± 0.000 | 0.0000 ± 0.0000 | 0.0823 ± 0.0257 | 0.6235 ± 0.0033 | — | — | — | — | 1.883 | 0.205 | 0.000 | -0.21 |
| fp16.randn | 1 | 0.000 | 84416 | 21.036 ± 0.087 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | — | — | — | — | 22.871 | 2.491 | 2.291 | 2.68 |
| int8.zeros | 1 | 1.000 | 0 | 0.000 ± 0.000 | 0.0000 ± 0.0000 | 0.2641 ± 0.0366 | 0.8398 ± 0.0098 | — | — | — | — | 2.409 | 0.076 | 0.000 | -0.31 |
| int8.full | 1 | 0.000 | 69312 | 6.719 ± 0.790 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | — | — | — | — | 9.122 | 0.289 | 0.213 | 0.38 |
| anchor_pi | 1 | 0.000 | 0 | 7.846 ± 0.480 | — | — | — | — | — | — | — | 9.632 | 2.098 | 1.709 | 1.00 |

## Gated tiles: distance from the predictor (a) and the gate law (c)

| tile | g | live share | D W | D − (a) W | D − (c) W | nearer | D ÷ (c) | a live lane's cost ÷ random's (D − gG) / ((1 − g)L) |
|---|---|---|---|---|---|---|---|---|
| fp16.r2_resnet18_l3c1 | 0.367 | 0.633 | 13.286 ± 0.296 | — | — | None | — | — |
| fp16.r2_t5small_l0_down | 0.871 | 0.129 | 3.374 ± 0.840 | — | — | None | — | — |
| fp16.r2_vgg16_fc2 | 0.551 | 0.449 | 9.748 ± 2.099 | — | — | None | — | — |
| fp32.r2_resnet18_l2c1 | 0.191 | 0.809 | 18.836 ± 0.430 | — | — | None | — | — |
| fp32.r2_resnet18_l3c1 | 0.445 | 0.555 | 13.461 ± 0.230 | — | — | None | — | — |
| fp32.r2_t5small_l0_down | 0.949 | 0.051 | 1.772 ± 2.417 | — | — | None | — | — |
| fp32.r2_vgg16_fc2 | 0.723 | 0.277 | 7.539 ± 2.006 | — | — | None | — | — |
| int8.r2_gpt2_l11_down_maxabs | 0.637 | 0.363 | 2.348 ± 0.339 | — | — | None | — | — |
| int8.r2_resnet18_l3c1 | 0.176 | 0.824 | 4.064 ± 0.319 | — | — | None | — | — |
| int8.r2_t5small_l0_down | 0.766 | 0.234 | 2.107 ± 1.407 | — | — | None | — | — |
| int8.r2_vgg16_fc2 | 0.336 | 0.664 | 3.572 ± 0.577 | — | — | None | — | — |
| int8.r2_vit_l11_down | 0.547 | 0.453 | 2.643 ± 1.144 | — | — | None | — | — |

## ViT's −0.0 tile

D 19.386 ± 0.588 W against 19.8278 W (gate blind to −0.0) and 9.0698 W (gate took it): D − blind -0.441 W, D − gated 10.317 W. **gate blind to -0.0**. D ÷ random 0.8280 ± 0.0475.

## Offsets from a partner, (a′)

| tile | partner | predicted offset W [interval] | measured W ± 95% | in |
|---|---|---|---|---|
| fp16.r2_gpt2_l6_attn_qk_fp16fwd | fp16.real_l6_attn_qk | -0.1771 [-0.783, 0.4288] | 0.118 ± 0.568 | no |
| fp16.r2_gpt2_l6_mlp_down_fp16fwd | fp16.real_l6_mlp_down | -0.1007 [-0.7065, 0.5052] | -0.009 ± 1.761 | no |
| int8.r2_gpt2_l11_down_asym | int8.r2_gpt2_l11_down_maxabs | 2.7408 [2.1313, 3.3503] | 1.641 ± 1.128 | no |
| int8.r2_gpt2_l11_down_p999 | int8.r2_gpt2_l11_down_maxabs | 3.8888 [3.2793, 4.4983] | 2.888 ± 0.288 | no |
| int8.r2_gpt2_l6_down_p999 | int8.real_l6_mlp_down | 0.2376 [-0.3719, 0.8471] | -0.059 ± 0.398 | no |
| int8.r2_gpt2_l6_down_p9999 | int8.real_l6_mlp_down | 0.0399 [-0.5696, 0.6494] | -0.148 ± 0.302 | no |
| int8.r2_gpt2_l6_down_per_token | int8.real_l6_mlp_down | 0.1665 [-0.443, 0.776] | -0.055 ± 1.756 | no |
| int8.r2_vgg16_fc2_asym | int8.r2_vgg16_fc2 | 1.3592 [0.7497, 1.9687] | 0.816 ± 1.550 | no |

## Live share and bits, per format (reported)

| format | tiles | R² of D on live share | R² of D on bus bits | slope on live share ÷ L |
|---|---|---|---|---|

Gated tiles only:

| format | tiles | slope ÷ L | per-pass ± 95% | known slope ÷ L |
|---|---|---|---|---|

## C12 beside: rms per class, and the no-model baseline

| class | tier-1 tiles | rms W | known rms W | mean miss W | known mean W |
|---|---|---|---|---|---|
| float_ungated/fp32 | 0 | — | 1.0406 | — | -0.4466 |
| float_ungated/fp16 | 0 | — | 1.3947 | — | -0.9699 |
| float_gated | 0 | — | 1.2848 | — | 1.1851 |
| int8_ungated | 0 | — | 0.368 | — | 0.1551 |
| int8_gated | 0 | — | 0.4536 | — | 0.4332 |

| format (ungated float tier 1) | tiles | rms of 'costs E78's random kind' W | rms of the predictor W |
|---|---|---|---|

## The session tie (reported; a failure means the session moved, not a model)

| cell | E95 D W ± 95% | reference W | which | diff W | band | verdict |
|---|---|---|---|---|---|---|
| fp32.randn | 23.415 ± 0.633 | 23.986936105256 | E82 (card 1) | — | ±0.5 | NOT SCORED |
| fp16.randn | 21.036 ± 0.087 | 21.441512616301118 | E82 (card 1) | — | ±0.5 | NOT SCORED |
| anchor_pi | 7.846 ± 0.480 | 8.095381203007511 | E82 (card 1) | — | ±0.5 | NOT SCORED |
| int8.full | 6.719 ± 0.790 | 6.868848968010575 | E82 (card 1) | — | ±0.25 | NOT SCORED |

## Checks (reported, never a verdict)

- idle consistency median |S − S0 − D| 0.074 W (≤ 0.15: True)
- rail lag re-fit median 0.975 s (in [0.80, 1.15]: True)
- duty 0.9955–0.9967 (in [0.990, 1.000]: True)
- carry-over {'slope_w_per_w': 0.003800739169192093, 'se': 0.0008155628781380529, 'n': 104} (ok: True)
- passes set aside [{'pass': 11252, 'why': ['fp32.zeros departs -0.253 W from its straight line']}]; config flags []; config unread []
- failed runs []; idle-invalid runs 0

Tally: {'NOT SCORED': 13}
