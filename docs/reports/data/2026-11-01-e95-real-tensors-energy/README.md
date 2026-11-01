# E95: more real tensors' energy, and exact zeros letting the gate act (aifoundry3 card 0, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132, item 3 of the kinds page's section 11. **Every tile's prediction and the claims C1–C12 are Q132(r)'s, frozen in
[`real2/predictions-real2.json`](../../../../tools/claims-v3/kinds/real2/predictions-real2.json) (commit `6ae4c3d5`, sha256 `0957e0c2…`) before any card ran these tiles.**
E95's own pre-registration is `89bd34cb` (committed 00:49:44, pushed 00:49:49 PDT by origin/main's reflog, before the claim and the first launch):
[`tools/claims-v3/kinds/E95.md`](../../../../tools/claims-v3/kinds/E95.md), `predictions-e95.json` (sha256 `0f7da535…`), scorer `score_e95.py`. One amendment, A1, `df2cc512` (pushed
01:48:04 PDT, before the pass it added). aifoundry3 card 0 at 600 MHz in every sample, 521.6 mV mean, TDP 0 / threshold 65 °C read at the session's start and end, never set: no governor move,
no reset, no `--reset-ms`. Claim 1566370154114322443 in #community-lab, posted 01:35:46 PDT, released by editing it at about 01:22:55 PST (the clocks went back at 02:00 PDT): held 47.2 min, device access 46.8 min
(01:35:49 PDT to 01:22:36 PST), over the registered 45 and inside A1's 48 ([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

**What ran.** Q132(r)'s thirty real tiles: ReLU networks with exact zeros (ResNet-18, VGG-16, T5-small), more layers and models with none (GPT-2 small's layers 3 and 9, BERT, ViT-B/16), an fp16 and a bf16
forward pass of GPT-2, other int8 calibrations, T5's bf16-grid weights, ViT's −0.0 layer. Beside them, three of E86's tiles (C7's and C11's partners, and a second forward-pass partner) and, in every pass, E78's six anchors three times and the
tie twice: 53 runs a pass, E78's runner and reduction unchanged and sha256-checked. Five passes ran (9510–9514). Each tile is one 16 × 16 window of one layer: these are tiles, not models.
**D** is a tile's board power over its own type's all-zeros level, **S** over idle, **whole board** the window's leakage-corrected power (idle plus S); **r** is D over the same pass's random kind of that format (`fp32.randn`, `fp16.randn`, `int8.full`).
Every interval is 95% over kept passes, t(0.975, n − 1) × SE, a difference paired within the pass. Numbers come from [`scored.json`](scored.json) and [`results.md`](results.md), the labelled arm from [`dips-arm/`](dips-arm/), the derived ones from [`readme-numbers.txt`](readme-numbers.txt) and [`bench-check.txt`](bench-check.txt).

## Results

**Four passes kept of five (9510, 9511, 9512, 9514), 207 of 260 runs: of the 13 frozen claims, 9 PASS, 1 FAIL (C1), 2 INCONCLUSIVE (C2, C5), 1 UNDER-RESOLVED (C7).**
The registered dips-removed arm, which moves no verdict, keeps all five passes and reads 10 PASS, 1 FAIL (C1), 2 INCONCLUSIVE (C5, C7). The session tie to E78 and E86 passes. No verdict moves between scored readings at the three leakage arms.

| claim | says | PASS if | happened | verdict | dips-removed arm (five passes), labelled |
|---|---|---|---|---|---|
| **C1** | no-zero fp32, fp16 within 2% of random in every model | every cell's r interval inside [0.98, 1.02] | gpt2/fp32 0.9835 ± 0.0369 INCONCLUSIVE; gpt2/fp16 0.9568 ± 0.0110 FAIL; bert/fp32 0.9994 ± 0.0067 PASS; bert/fp16 0.9924 ± 0.0127 INCONCLUSIVE; vit/fp32 1.0040 ± 0.0114 PASS; vit/fp16 0.9859 ± 0.0091 INCONCLUSIVE | **FAIL** | FAIL |
| **C2** | they sit below random on average | each format's upper bound < 1 | fp32 0.9915 ± 0.0204 INCONCLUSIVE; fp16 0.9778 ± 0.0143 PASS | **INCONCLUSIVE** | PASS |
| **C3a** | a ReLU tile's power follows its live share | all 7 inside the gate law's interval | 7 of 7 inside | **PASS** | PASS |
| **C3b** | D's slope on live share is about L | slope / L in [0.85, 1.25] | fp32 0.955; fp16 0.933 | **PASS** | PASS |
| **C4** | the same numbers cost more in fp16 than fp32 | r(fp16) − r(fp32) lower bound > 0, all three | vgg16_fc2 +0.140 ± 0.011; resnet18_l3c1 +0.059 ± 0.004; t5small_l0_down +0.094 ± 0.004 | **PASS** | PASS |
| **C5** | int8 ReLU tiles follow bits more than live share | (a) nearer than (c) on both | `resnet18_l3c1` D 4.350 ± 0.231 W, nearer (a); `vgg16_fc2` D 3.912 ± 0.170 W, nearer (c) | **INCONCLUSIVE** | INCONCLUSIVE |
| **C6** | p99.9 clip − max-abs on a layer with an outlier | lower bound ≥ 2.0 W | +3.163 ± 0.147 W (predicted +3.994) | **PASS** | PASS |
| **C7** | E86's window ranks committed < per-token < p99.9, p99.99 beside committed | lower bounds > 0, p99.99 inside ±0.40 W | p9999 -0.057 ± 0.637 W (n 3); per_token -0.232 ± 1.516 W (n 3); p999 +0.054 ± 0.371 W (n 2) | **UNDER-RESOLVED** | INCONCLUSIVE |
| **C8** | asymmetric activations show the gate nothing | asym − symmetric lower bound > 0.5 W | +0.820 ± 0.119 W (predicted +1.396) | **PASS** | PASS |
| **C9** | −0.0 passes the gate | D's lower bound > 11.909 W | D 19.959 ± 0.851 W | **PASS** | PASS |
| **C10** | bf16-grid weights cost clearly less | r's upper bound < 0.97 | r 0.8903 ± 0.0138 (predicted 0.9082) | **PASS** | PASS |
| **C11** | an fp16 forward pass costs what rounding costs | paired interval inside ±0.50 W | -0.005 ± 0.032 W (predicted -0.104) | **PASS** | PASS |
| **C12** | the (a) intervals hold | ≥ 20 of 25 | 23 of 25; tier 2 apart 3 of 5 | **PASS** | PASS |

**1. C1 FAILS, on one fp16 cell: with no exact zeros, real fp32 costs what random fp32 costs, within 2%, and real fp16 does too except in attention.** Only three of the six models have such a tile (GPT-2, BERT, ViT): ResNet's and VGG's activations hold exact zeros (result 2), T5's weights sit on the bf16 grid (result 6), and ViT's last layer is 64% −0.0 (result 5).
GPT-2's fp16 attention cell reads **0.9568 ± 0.0110**, its whole interval below 0.98, as E86's and E91's fp16 attention tiles warned (0.971, 0.966). In the primary the other five cells read PASS or INCONCLUSIVE: a single dip-hit run (result 9) widens fp32's GPT-2 cell, and two fp16 cells' lower bounds touch 0.977–0.980. With the dips removed every fp32 cell PASSES (0.987–0.999) and fp16 BERT PASSES; fp16 ViT (0.986) stays INCONCLUSIVE and GPT-2's fp16 attention still FAILS.
The three fp16 attention windows here read 0.957–0.968 and the fp16 MLP-side windows 0.986–0.996, so **attention, with an activation on both sides, sits 3–4% below random in fp16 and about 2% in fp32** (`fp32.r2_gpt2_l9_attn_qk` 0.9799 ± 0.0030 with the dips removed; E95 has one such fp32 tile). C2 reads INCONCLUSIVE on fp32 (0.9915 ± 0.0204, PASS at 0.9916 ± 0.0038 with the dips removed) and PASS on fp16 (0.9778 ± 0.0143). The RTL bench, frozen before this data commit, saw the attention dip: 21.09 W (M2) and 21.10 W (M4) against 20.963 ± 0.262 W, from fewer net toggles than BERT's tile (result 7).

| tile | format | D (W) | D ÷ random | S ÷ random | whole board ÷ random | D ÷ random, dips removed | pJ/MAC (S) |
|---|---|---|---|---|---|---|---|
| GPT-2 layer 3, GELU output × weight | fp32 | 24.365 ± 0.096 | 0.9999 ± 0.0093 | 0.9985 ± 0.0048 | 0.9995 ± 0.0053 | 0.9957 ± 0.0046 | 5.743 |
| GPT-2 layer 9, queries × keys | fp32 | 23.677 ± 0.871 | 0.9736 ± 0.0418 | 0.9721 ± 0.0371 | 0.9869 ± 0.0200 | 0.9799 ± 0.0030 | 5.580 |
| BERT layer 6, LayerNorm × weight | fp32 | 24.305 ± 0.078 | 0.9994 ± 0.0067 | 0.9961 ± 0.0132 | 1.0000 ± 0.0048 | 0.9942 ± 0.0029 | 5.717 |
| ViT-B/16 layer 5, GELU output × weight | fp32 | 24.416 ± 0.151 | 1.0040 ± 0.0114 | 1.0028 ± 0.0099 | 1.0017 ± 0.0059 | 0.9985 ± 0.0043 | 5.755 |
| GPT-2 layer 9, queries × keys | fp16 | 20.963 ± 0.262 | 0.9568 ± 0.0110 | 0.9633 ± 0.0193 | 0.9807 ± 0.0037 | 0.9562 ± 0.0060 | 2.503 |
| BERT layer 6, LayerNorm × weight | fp16 | 21.738 ± 0.191 | 0.9924 ± 0.0127 | 0.9933 ± 0.0092 | 0.9962 ± 0.0057 | 0.9964 ± 0.0020 | 2.583 |
| ViT-B/16 layer 5, GELU output × weight | fp16 | 21.596 ± 0.114 | 0.9859 ± 0.0091 | 0.9887 ± 0.0100 | 0.9937 ± 0.0026 | 0.9862 ± 0.0063 | 2.571 |
| GPT-2 layer 6, GELU output × weight (E86's window) | fp16 | 21.813 ± 0.086 | 0.9958 ± 0.0040 | 0.9986 ± 0.0055 | 0.9983 ± 0.0012 | 0.9951 ± 0.0032 | 2.597 |
| GPT-2 layer 6, queries × keys (E86's window) | fp16 | 21.194 ± 0.149 | 0.9675 ± 0.0055 | 0.9690 ± 0.0124 | 0.9854 ± 0.0013 | 0.9672 ± 0.0038 | 2.520 |

**2. A ReLU tile's power follows its live share in fp32 and fp16 (C3a, C3b PASS), and the word grouping costs what was predicted (C4 PASS); in int8 neither frozen prediction holds (C5 INCONCLUSIVE).** All seven float tiles lie inside the gate law's interval, D ÷ law 0.845–1.059, the law nearer than (a) on six of them, and D's slope on live share is **0.955** of random's cost in fp32 and **0.933** in fp16. The same numbers cost more in fp16 than in fp32 because a zero must fill the whole 32-bit word: the r gap is +0.140 ± 0.011 on VGG, +0.059 ± 0.004 on ResNet and +0.094 ± 0.004 on T5, against a predicted +0.114, +0.043, +0.059.
In int8 D lies **between** the two predictions on both C5 tiles: ResNet 4.350 ± 0.231 W (bits predictor (a) 3.62, gate law (c) 5.89), VGG 3.912 ± 0.170 W ((a) 2.71, (c) 4.82). (a) is nearer on ResNet and (c) on VGG, so C5 reads INCONCLUSIVE. The frozen file's third column, (c′), the law with L taken from E86's real int8 tiles (5.86 W) instead of uniform random's 7.06 W, lands closer on these two, and in rms over all five gated int8 tiles (below; it is not a registered claim): **a live int8 lane on real numbers costs less than a lane on uniform random bytes, and the gate takes the rest.** Over five gated int8 tiles D's slope on live share is only 0.568 of `full`'s cost (known on E78's synthetic gated kinds: 1.107). Over the zeros level, energy per MAC falls with format on VGG and ResNet, and not from fp32 to fp16 on T5: VGG goes 1.70 → 1.10 → 0.124 pJ/MAC, ResNet 3.06 → 1.52 → 0.138, and T5, gated 95% and 87%, 0.356 → 0.384 → 0.069, where the gate share fp16 loses eats what its narrower multiplier saves.

| layer | format | gate closes g | live share | r = D ÷ random | D (W) | (a) | (c) gate law | (c′) law with E86's real L | bench M4 | pJ/MAC (D) | pJ/MAC (S) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VGG-16 fc2 | fp32 | 0.723 | 0.277 | 0.3210 ± 0.0118 | 7.806 ± 0.230 | 7.02 | 7.37 | 7.28 | 7.82 | 1.700 | 2.139 |
| VGG-16 fc2 | fp16 | 0.551 | 0.449 | 0.4611 ± 0.0107 | 10.101 ± 0.208 | 8.83 | 10.35 | 10.19 | 10.20 | 1.100 | 1.310 |
| VGG-16 fc2 | int8 | 0.336 | 0.664 | 0.5513 ± 0.0199 | 3.912 ± 0.170 | 2.71 | 4.82 | 4.03 | 3.97 | 0.124 | 0.205 |
| ResNet-18 layer3.0.conv1 | fp32 | 0.445 | 0.555 | 0.5781 ± 0.0040 | 14.060 ± 0.072 | 13.65 | 14.03 | 13.85 | 14.13 | 3.061 | 3.501 |
| ResNet-18 layer3.0.conv1 | fp16 | 0.367 | 0.633 | 0.6371 ± 0.0042 | 13.956 ± 0.118 | 13.19 | 14.29 | 14.06 | 14.04 | 1.520 | 1.740 |
| ResNet-18 layer3.0.conv1 | int8 | 0.176 | 0.824 | 0.6130 ± 0.0292 | 4.350 ± 0.231 | 3.62 | 5.89 | 4.90 | 4.52 | 0.138 | 0.219 |
| T5-small block 0 ff | fp32 | 0.949 | 0.051 | 0.0671 ± 0.0058 | 1.633 ± 0.152 | 1.18 | 1.93 | 1.92 | 1.64 | 0.356 | 0.792 |
| T5-small block 0 ff | fp16 | 0.871 | 0.129 | 0.1610 ± 0.0053 | 3.526 ± 0.121 | 2.36 | 3.48 | 3.44 | 3.48 | 0.384 | 0.610 |
| T5-small block 0 ff | int8 | 0.766 | 0.234 | 0.3061 ± 0.0172 | 2.172 ± 0.132 | 0.79 | 1.96 | 1.68 | 2.25 | 0.069 | 0.149 |
| ResNet-18 layer2.0.conv1 | fp32 | 0.191 | 0.809 | 0.8087 ± 0.0097 | 19.667 ± 0.085 | 19.66 | 20.13 | 19.86 | 19.82 | 4.284 | 4.718 |
| GPT-2 layer 11 (max-abs, no exact zero) | int8 | 0.637 | 0.363 | 0.3321 ± 0.0271 | 2.357 ± 0.201 | 1.16 | 2.82 | 2.38 | 2.53 | 0.075 | 0.154 |
| ViT layer 11 (−0.0 rounds to zero bytes) | int8 | 0.547 | 0.453 | 0.4072 ± 0.0170 | 2.889 ± 0.136 | 1.77 | 3.42 | 2.88 | 2.87 | 0.092 | 0.173 |

| format | gated tiles | (a) rms W | (c) rms W | (c′) rms W | bench M2 rms W | bench M4 rms W | slope of D on live share ÷ L, per-pass ± 95% | known on E78's and E90's gated tiles |
|---|---|---|---|---|---|---|---|---|
| fp32 | 4 | 0.496 | 0.351 | 0.331 | 0.372 | 0.083 | 0.955 (0.955 ± 0.005) | 1.039 |
| fp16 | 3 | 1.090 | 0.242 | 0.093 | 0.598 | 0.079 | 0.933 (0.933 ± 0.007) | 0.937 |
| int8 | 5 | 1.148 | 0.863 | 0.334 | 0.163 | 0.117 | 0.568 (0.568 ± 0.026) | 1.107 |

**3. A true fp16 forward pass costs the same as rounding the fp32 activations (C11 PASS): -0.005 ± 0.032 W on GPT-2's MLP tile, -0.021 ± 0.149 W on its attention tile.** D ÷ random 0.9955 ± 0.0026 against 0.9958 ± 0.0040, and 0.9665 ± 0.0050 against 0.9675 ± 0.0055. The pass moved the numbers by 2–3 fp16 ulps at the median (real2 README, result 4), and the power does not move. So on these two windows E86's fp16 row, cut from rounded fp32, stands for an fp16 forward pass. A **bf16** forward pass held in fp32 bytes is a different kind: 17.830 ± 0.075 W, r 0.7331 ± 0.0080 (whole board 0.8750 ± 0.0044), beside E78's synthetic `bf16trunc`, 18.14 W at E78's slope (18.06 W at that slope here).

**4. The int8 calibration is a lever only where the tile holds an outlier or a ReLU zero.** On GPT-2's layer 11, with one activation of 44.1, max-abs rounds 64% of A's words to zero in this window and the gate closes on them: p99.9 clip − max-abs is **+3.163 ± 0.147 W** (C6 PASS, predicted +3.99), 2.34× in D, 1.65× in S, and 8.9 points of the whole board. The TFLite asymmetric scheme maps zero to −128, so no word is zero: on VGG's ReLU tile it costs **+0.820 ± 0.119 W** more than symmetric with the same numbers (C8 PASS, predicted +1.40; 4.73 against 3.91 W), and on layer 11 +1.688 ± 0.452 W over max-abs (tier 2), still below the clip. On E86's own window, with no outlier, **no rank resolves**: C7 is UNDER-RESOLVED in the primary, because two launch-rule skips and the set-aside pass leave the p99.9 pair with two passes, and INCONCLUSIVE with the dips removed, where the offsets are +0.000 ± 0.273, +0.014 ± 0.183 and -0.058 ± 0.335 W for per-token, p99.9 and p99.99 against committed. Its four tiles sit within 0.12 W of each other there. So: max-abs ≪ asymmetric < p99.9 on layer 11 (p99.9 − asymmetric +1.48 ± 0.30 W, `readme-numbers.txt`); symmetric < asymmetric on VGG; indistinguishable on layer 6.

| layer | calibration | gate closes | bus bits/op | D (W) | D ÷ random | S (W) | whole board ÷ random | D (W), dips removed |
|---|---|---|---|---|---|---|---|---|
| GPT-2 layer 11, GELU output (one activation of 44.1) | max-abs | 0.637 | 7,330 | 2.357 ± 0.201 | 0.3321 ± 0.0271 | 4.859 ± 0.323 | 0.8668 ± 0.0068 | 2.382 ± 0.155 |
|  | TFLite asymmetric (tier 2) | 0.000 | 14,114 | 4.044 ± 0.467 | 0.5698 ± 0.0613 | 6.553 ± 0.581 | 0.9130 ± 0.0120 | 4.159 ± 0.077 |
|  | p99.9 clip | 0.000 | 42,146 | 5.520 ± 0.224 | 0.7779 ± 0.0259 | 8.025 ± 0.238 | 0.9560 ± 0.0024 | 5.510 ± 0.154 |
| VGG-16 fc2 input, ReLU output | symmetric max-abs | 0.336 | 19,732 | 3.912 ± 0.170 | 0.5513 ± 0.0199 | 6.476 ± 0.066 | 0.9105 ± 0.0008 | 3.884 ± 0.136 |
|  | TFLite asymmetric | 0.000 | 22,836 | 4.732 ± 0.121 | 0.6669 ± 0.0116 | 7.272 ± 0.177 | 0.9330 ± 0.0017 | 4.717 ± 0.091 |
| GPT-2 layer 6, GELU output (E86's window) | committed (max-abs) | 0.000 | 45,684 | 5.669 ± 0.311 | 0.7999 ± 0.0565 | 8.141 ± 0.468 | 0.9591 ± 0.0063 | 5.696 ± 0.186 |
|  | p99.99 clip | 0.000 | 44,500 | 5.644 ± 0.202 | 0.7954 ± 0.0214 | 8.154 ± 0.265 | 0.9596 ± 0.0036 | 5.659 ± 0.144 |
|  | per token | 0.000 | 46,996 | 5.525 ± 0.708 | 0.7785 ± 0.0946 | 8.105 ± 0.702 | 0.9565 ± 0.0171 | 5.715 ± 0.140 |
|  | p99.9 clip | 0.000 | 47,092 | 5.792 ± 0.155 | 0.8177 ± 0.0267 | 8.302 ± 0.651 | 0.9628 ± 0.0063 | 5.772 ± 0.099 |

**5. A real layer's −0.0 passes the gate (C9 PASS).** ViT-B/16's last block holds 64% −0.0 words in this tile. It reads **19.959 ± 0.851 W** (dips removed 20.180 ± 0.081 W), 0.46 W from the gate-blind prediction of 20.42 W and 10.6 W above the 9.34 W the law gives if the gate took numeric zeros. This is the real-network instance of E93's result 1 (`-0.0 × -0.0` costs 7.94 W on aifoundry1 card 1). D ÷ random is 0.8208 ± 0.0397 (0.8259 ± 0.0042 with the dips removed): read with the law's two-part split, and assuming the other 36% of lanes cost random's, a −0.0 lane costs about 0.72 of a random one (an estimate, not a measurement). In int8 the same layer's −0.0 rounds to a zero byte and the gate does act: `int8.r2_vit_l11_down` closes 0.547 of its lanes and reads 2.889 ± 0.136 W, r 0.4072 ± 0.0170.

**6. T5's bf16-grid weights cost clearly less (C10 PASS):** `fp32.r2_t5small_l0_up`, no zero word, a full-mantissa A, weights with all low 16 mantissa bits zero, reads r 0.8903 ± 0.0138 (predicted 0.908), 21.651 ± 0.212 W. The bits predictor misses it by -0.80 W, since it prices B at 0; the frozen file flagged this tile for that reason.

**7. The frozen predictions against the measurement, the RTL bench's beside them.** (a) holds: C12 reads 23 of 25 inside (outside: `vgg16_fc2` int8, `gpt2_l11_down_maxabs` int8, each measured above the interval), with tier 2's 3 of 5 apart (`t5small_l0_down` int8, `vit_l11_down` int8 also above). Its class rms beats its known misses except on int8 (gated 1.07 W against 0.45 known, ungated 0.42 against 0.37). Labelled beside: 21 of 25 inside the E86-only arm; on ungated float tier-1 tiles the no-model baseline "each tile costs E78's random kind" scores 2.37 W rms in fp32 and 0.72 W in fp16, against the predictor's 0.50 and 0.41 W.

| class | tier-1 tiles | rms W | known rms W | mean miss W | known mean W |
|---|---|---|---|---|---|
| float_ungated/fp32 | 6 | 0.504 | 1.0406 | -0.361 | -0.4466 |
| float_ungated/fp16 | 4 | 0.406 | 1.3947 | +0.050 | -0.9699 |
| float_gated | 7 | 0.806 | 1.2848 | +0.694 | 1.1851 |
| int8_ungated | 5 | 0.417 | 0.368 | +0.391 | 0.1551 |
| int8_gated | 3 | 1.069 | 0.4536 | +1.046 | 0.4332 |

**The RTL bench (Q132(b)) was frozen before this data commit, by the commit times, and it does better than (a).** M2, `2b7ece4a`, committed 01:03:01 PST: 1.871 fJ per net toggle and 1.092 fJ per clocked bit in floats, 3.735 and 2.133 fJ in int8, fitted on E78 alone. M4, `b995463e`, committed 01:08:31 PST: the lane operand bus priced apart (float: core 1.62, bus 7.53, other 2.22 fJ per net toggle, 1.07 fJ per clocked bit), fitted on E78 alone, its form chosen after E94 was read, so E95 is its first blind test. **This data commit comes after both.** At the first, passes 9510 and 9511 and nearly all of 9512 had run on the card (9512 ended 14 s later); at the second, 9513 was running and 9514 had not begun. No E95 value had been committed; the two scripts (`predict_e94_e95.py`, `predict_m4.py`) open no E95 data directory, and their commits say none was read. The bench's 30 tiles of `real2/` were blind; E86's three were not. No verdict rests on them: they are not among E95's claims. Byte-for-byte copies: `bench-prediction-2b7ece4a.json`, `bench-prediction-m4-b995463e.json`.

**M4 lands all 30 blind tiles inside its 95% interval with 0.161 W rms, M2 all 30 with 0.373 W, against (a)'s 0.696 W** (M2's half-width is 0.76–0.86 W and M4's 0.41–0.69 W, so "inside" says less than the rms). Largest misses: M4 `fp16.r2_bert_l6_up` -0.40 W; M2 `fp16.r2_t5small_l0_down` +0.75 W. On the ten ReLU tiles M4's rms is 0.092 W, and on the five gated int8 tiles 0.117 W, against (a)'s 1.15 and (c)'s 0.86 W. E95's primary slope (0.2959 W/°C) is its own and the bench's fit is on E78's (0.1994), so the like-with-like reading at the 0.1994 arm is in [`bench-check.txt`](bench-check.txt): M2 0.367 W, M4 0.154 W, (a) 0.741 W rms, on three kept passes.

| set | tiles | M2 rms W (mean error) | M2 inside its 95% | M4 rms W (mean error) | M4 inside its 95% | (a) rms W (mean error) |
|---|---|---|---|---|---|---|
| all 30 blind tiles | 30 | 0.373 (+0.066) | 30 | 0.161 (-0.075) | 30 | 0.696 (+0.364) |
| fp32 | 11 | 0.424 (-0.138) | 11 | 0.102 (-0.078) | 11 | 0.506 (+0.003) |
| fp16 | 8 | 0.403 (+0.093) | 8 | 0.212 (-0.169) | 8 | 0.730 (+0.403) |
| int8 | 11 | 0.285 (+0.249) | 11 | 0.166 (-0.004) | 11 | 0.824 (+0.697) |
| ReLU tiles | 10 | 0.411 (+0.286) | 10 | 0.092 (-0.068) | 10 | 0.919 (+0.818) |
| no exact zeros | 7 | 0.408 (-0.376) | 7 | 0.206 (-0.163) | 7 | 0.380 (-0.179) |
| int8 calibrations | 7 | 0.331 (+0.301) | 7 | 0.194 (+0.035) | 7 | 0.574 (+0.460) |

| tile | D (W), primary | M2 frozen `2b7ece4a` [95%] | D − M2 | M4 frozen `b995463e` [95%] | D − M4 | (a) frozen `6ae4c3d5` | D − (a) |
|---|---|---|---:|---|---:|---|---:|
| `fp32.r2_vit_l5_down` | 24.416 ± 0.151 | 24.83 [23.97, 25.68] | -0.41 | 24.45 [23.99, 24.90] | -0.03 | 24.41 | +0.01 |
| `fp32.r2_gpt2_l3_mlp_down` | 24.365 ± 0.096 | 24.85 [24.00, 25.71] | -0.49 | 24.43 [23.98, 24.88] | -0.06 | 24.37 | -0.00 |
| `fp32.r2_bert_l6_up` | 24.305 ± 0.078 | 24.74 [23.89, 25.59] | -0.43 | 24.34 [23.90, 24.79] | -0.04 | 24.40 | -0.10 |
| `fp32.r2_gpt2_l9_attn_qk` | 23.677 ± 0.871 | 24.31 [23.46, 25.16] | -0.63 | 23.87 [23.41, 24.33] | -0.19 | 24.48 | -0.81 |
| `fp32.r2_t5small_l0_up` | 21.651 ± 0.212 | 22.22 [21.37, 23.07] | -0.57 | 21.84 [21.38, 22.29] | -0.18 | 22.46 | -0.80 |
| `fp32.r2_vit_l11_down` | 19.959 ± 0.851 | 19.64 [18.80, 20.47] | +0.32 | 19.97 [19.56, 20.38] | -0.01 | 20.42 | -0.46 |
| `fp32.r2_resnet18_l2c1` | 19.667 ± 0.085 | 19.97 [19.13, 20.81] | -0.30 | 19.82 [19.39, 20.25] | -0.15 | 19.66 | +0.00 |
| `fp32.r2_gpt2_l6_mlp_down_bf16fwd` | 17.830 ± 0.075 | 17.89 [17.06, 18.72] | -0.06 | 17.92 [17.52, 18.33] | -0.09 | 17.28 | +0.55 |
| `fp32.r2_resnet18_l3c1` | 14.060 ± 0.072 | 13.95 [13.12, 14.78] | +0.11 | 14.13 [13.71, 14.55] | -0.07 | 13.65 | +0.41 |
| `fp32.r2_vgg16_fc2` | 7.806 ± 0.230 | 7.28 [6.46, 8.10] | +0.53 | 7.82 [7.41, 8.23] | -0.01 | 7.02 | +0.78 |
| `fp32.r2_t5small_l0_down` | 1.633 ± 0.152 | 1.22 [0.40, 2.03] | +0.42 | 1.64 [1.24, 2.05] | -0.01 | 1.18 | +0.45 |
| `fp16.real_l6_mlp_down` | 21.813 ± 0.086 | 22.01 [21.17, 22.85] | -0.20 | 22.06 [21.65, 22.48] | -0.25 | E86 read | — |
| `fp16.r2_gpt2_l6_mlp_down_fp16fwd` | 21.808 ± 0.073 | 22.00 [21.16, 22.84] | -0.19 | 22.06 [21.65, 22.47] | -0.26 | 21.25 | +0.55 |
| `fp16.r2_bert_l6_up` | 21.738 ± 0.191 | 22.07 [21.23, 22.92] | -0.33 | 22.13 [21.72, 22.55] | -0.40 | 21.51 | +0.23 |
| `fp16.r2_vit_l5_down` | 21.596 ± 0.114 | 21.80 [20.96, 22.64] | -0.21 | 21.88 [21.47, 22.29] | -0.28 | 21.64 | -0.04 |
| `fp16.real_l6_attn_qk` | 21.194 ± 0.149 | 21.34 [20.51, 22.18] | -0.15 | 21.35 [20.94, 21.76] | -0.16 | E86 read | — |
| `fp16.r2_gpt2_l6_attn_qk_fp16fwd` | 21.173 ± 0.142 | 21.31 [20.47, 22.14] | -0.13 | 21.32 [20.91, 21.74] | -0.15 | 21.35 | -0.18 |
| `fp16.r2_gpt2_l9_attn_qk` | 20.963 ± 0.262 | 21.09 [20.26, 21.93] | -0.13 | 21.10 [20.68, 21.51] | -0.13 | 21.51 | -0.55 |
| `fp16.r2_resnet18_l3c1` | 13.956 ± 0.118 | 13.55 [12.73, 14.38] | +0.40 | 14.04 [13.63, 14.44] | -0.08 | 13.19 | +0.77 |
| `fp16.r2_vgg16_fc2` | 10.101 ± 0.208 | 9.51 [8.69, 10.33] | +0.59 | 10.20 [9.79, 10.61] | -0.10 | 8.83 | +1.27 |
| `fp16.r2_t5small_l0_down` | 3.526 ± 0.121 | 2.78 [1.96, 3.60] | +0.75 | 3.48 [3.07, 3.89] | +0.05 | 2.36 | +1.17 |
| `int8.r2_gpt2_l6_down_p999` | 5.792 ± 0.155 | 5.37 [4.57, 6.17] | +0.42 | 5.54 [4.99, 6.09] | +0.25 | 5.43 | +0.36 |
| `int8.real_l6_mlp_down` | 5.669 ± 0.311 | 5.25 [4.45, 6.05] | +0.42 | 5.37 [4.82, 5.91] | +0.30 | E86 read | — |
| `int8.r2_gpt2_l6_down_p9999` | 5.644 ± 0.202 | 5.28 [4.48, 6.07] | +0.37 | 5.42 [4.87, 5.97] | +0.23 | 5.22 | +0.42 |
| `int8.r2_gpt2_l6_down_per_token` | 5.525 ± 0.708 | 5.34 [4.54, 6.14] | +0.18 | 5.49 [4.94, 6.04] | +0.04 | 5.35 | +0.17 |
| `int8.r2_gpt2_l11_down_p999` | 5.520 ± 0.224 | 5.21 [4.42, 6.01] | +0.31 | 5.38 [4.82, 5.93] | +0.14 | 5.15 | +0.37 |
| `int8.r2_vgg16_fc2_asym` | 4.732 ± 0.121 | 4.23 [3.45, 5.00] | +0.51 | 4.67 [4.04, 5.30] | +0.06 | 4.10 | +0.63 |
| `int8.r2_resnet18_l3c1` | 4.350 ± 0.231 | 4.32 [3.54, 5.10] | +0.03 | 4.52 [3.97, 5.07] | -0.17 | 3.62 | +0.73 |
| `int8.r2_gpt2_l11_down_asym` | 4.044 ± 0.467 | 3.79 [3.02, 4.56] | +0.25 | 4.35 [3.66, 5.04] | -0.30 | 3.98 | +0.07 |
| `int8.r2_vgg16_fc2` | 3.912 ± 0.170 | 3.73 [2.95, 4.50] | +0.19 | 3.97 [3.41, 4.53] | -0.06 | 2.71 | +1.21 |
| `int8.r2_vit_l11_down` | 2.889 ± 0.136 | 2.63 [1.87, 3.39] | +0.26 | 2.87 [2.32, 3.42] | +0.02 | 1.77 | +1.12 |
| `int8.r2_gpt2_l11_down_maxabs` | 2.357 ± 0.201 | 2.29 [1.53, 3.05] | +0.07 | 2.53 [1.98, 3.08] | -0.17 | 1.16 | +1.20 |
| `int8.r2_t5small_l0_down` | 2.172 ± 0.132 | 2.02 [1.26, 2.78] | +0.16 | 2.25 [1.70, 2.81] | -0.08 | 0.79 | +1.38 |

**(a′), offsets from a partner** (reported; the bench's offsets are in [`bench-check.txt`](bench-check.txt)):

| tile | partner | (a′) predicted, W [interval] | measured, W (n) | in | dips removed, W (n) |
|---|---|---|---|---|---|
| `fp16.r2_gpt2_l6_attn_qk_fp16fwd` | `fp16.real_l6_attn_qk` | -0.183 [-0.809, +0.443] | -0.021 ± 0.149 (4) | yes | -0.027 ± 0.102 (5) |
| `fp16.r2_gpt2_l6_mlp_down_fp16fwd` | `fp16.real_l6_mlp_down` | -0.104 [-0.730, +0.522] | -0.005 ± 0.032 (4) | yes | -0.009 ± 0.024 (5) |
| `int8.r2_gpt2_l11_down_asym` | `int8.r2_gpt2_l11_down_maxabs` | +2.815 [+2.189, +3.441] | +1.688 ± 0.452 (4) | no | +1.777 ± 0.196 (5) |
| `int8.r2_gpt2_l11_down_p999` | `int8.r2_gpt2_l11_down_maxabs` | +3.994 [+3.368, +4.620] | +3.163 ± 0.147 (4) | no | +3.128 ± 0.137 (5) |
| `int8.r2_gpt2_l6_down_p999` | `int8.real_l6_mlp_down` | +0.244 [-0.382, +0.870] | +0.054 ± 0.371 (2) | unresolved, n 2 | +0.014 ± 0.183 (3) |
| `int8.r2_gpt2_l6_down_p9999` | `int8.real_l6_mlp_down` | +0.041 [-0.585, +0.667] | -0.057 ± 0.637 (3) | yes | -0.058 ± 0.335 (4) |
| `int8.r2_gpt2_l6_down_per_token` | `int8.real_l6_mlp_down` | +0.171 [-0.455, +0.797] | -0.232 ± 1.516 (3) | yes | +0.000 ± 0.273 (4) |
| `int8.r2_vgg16_fc2_asym` | `int8.r2_vgg16_fc2` | +1.396 [+0.770, +2.022] | +0.820 ± 0.119 (4) | yes | +0.832 ± 0.087 (5) |

**8. Heat follows D.** On the firmware's whole-degree reading (E89 found it truncated) gated float tiles warm the die 0.75–2.55 °C in 2 s against random's 2.79–3.05 (fp32 VGG 1.13 °C, -1.92 ± 0.24 °C against random; T5 1.00 °C, -2.05 ± 0.36), no-zero tiles as much as random. int8 tiles all read 0.75–1.0 °C. E95 adds no finer reading.

**9. Instrument: the dips and a launch-rule skip, not the data.** With E82's definition the five passes hold 60 board-reading dips, 17 inside power windows (`dips-arm/dips.json`). Two samples in `fp16.randn`'s window read 33.28 W against 50.2–50.4 W and set pass 9513 aside by the registered range gate (1.776 W against 1.0). Dip-hit runs make the wide intervals: `fp32.r2_gpt2_l9_attn_qk` ±0.871 W, `fp32.r2_vit_l11_down` ±0.851, `int8.r2_gpt2_l6_down_per_token` ±0.708, `int8.r2_gpt2_l11_down_asym` ±0.467; removed, they read ±0.055, ±0.081, ±0.140, ±0.077. **New here:** E78's launch rule skipped 5 of the 265 planned runs (3, 1, 1, 0, 0 by pass), each straight after an int8 or other low-power tile: the whole-degree reading reached 58 °C and flicked back to 59 °C inside the 2 s quiet gap (`aifoundry3/kinds/p95*/run.log`, read with `run_e78.py`'s `approach`). E86, E90 and E92 never hit it; E95 has more low-power tiles, and the runner does not retry. It cost C7 its population.

## What a blog reader can now be told

Each sentence is scoped to these tiles, one 16 × 16 window of a layer each, on one card at 600 MHz, over the format's all-zeros level unless it says otherwise.

- Real fp32 numbers with no exact zeros cost what random fp32 costs, within 2%, in GPT-2, BERT and ViT, once the instrument's dips are removed; the registered reading is short of that on one GPT-2 cell (`scored.json` › `claims.C1`; `dips-arm/scored-nodips.json`).
- Real fp16 does the same except in attention, where both operands are activations: GPT-2's windows cost 3–4% less than random fp16 (`claims.C1`, `tiles`).
- A ReLU network's exact zeros buy almost exactly their share: in fp32 and fp16, power follows the live share at 0.93–0.96 of random's cost (`claims.C3b`).
- Fewer bits hand the gate fewer zeros: the same VGG numbers cost 32% of random in fp32, 46% in fp16 and 55% in int8, because a zero must fill a whole 32-bit word (`claims.C4`; `tiles`).
- In int8 a real ReLU tile costs less than its live share of uniform random bytes, and more than its bits alone suggest (`claims.C5`; `readme-numbers.txt`).
- Computing GPT-2 in fp16 instead of rounding fp32 changes the power by 0.005 ± 0.032 W on the MLP tile and 0.02 ± 0.15 W on the attention tile: nothing (`claims.C11`).
- A bf16 forward pass held in fp32 words costs 73% of random fp32 (`tiles.fp32.r2_gpt2_l6_mlp_down_bf16fwd`).
- One huge activation makes the int8 calibration a 2.3× lever on power over the zeros level, 3.2 W: max-abs rounds most words to zero and the gate takes them (`claims.C6`). Without an outlier the calibrations cannot be told apart (`dips-arm/scored-nodips.json` › `claims.C7`).
- TFLite's asymmetric scheme turns the gate off on a ReLU layer: 0.82 W more for the same numbers (`claims.C8`).
- A real layer's −0.0 stays on: ViT's last block, 64% −0.0, costs 20 W where the gate would have left 9 W (`claims.C9`).
- T5's weights, on the bf16 grid, cost 11% less than random fp32 with no zero anywhere (`claims.C10`).
- RTL counts through the real `vpu_top`, fitted only on E78's synthetic kinds, predicted these thirty real tiles to 0.16 W rms before this data was committed (`bench-check.txt`, M4).

## Registered against happened

- **Before the card.** Registration pushed 00:49:49 PDT. `run_e95.sh setup` (no device access), 01:01:55–01:02:04 PDT on the idle box between other lanes' claims, found the reused E78 files and E95's files identical to the freeze, every tile matching its sha256, and a dry pass of 55 launches, 30 on real2 tiles (`logs/box-setup.txt`). E99's claim read released and `et-who` was clean at 01:35:20 PDT; the claim went up at 01:35:46.
- **Card state, read only.** TDP 0, threshold 65 °C, 600 MHz, 523 mV at 01:35:49 PDT and 01:22:36 PST (`logs/config-session-*.json`), and each pass's two reads (`aifoundry3/kinds/p95*/config_*.json`). Binary hashes in `logs/binaries.sha256`.
- **Smoke, pass 9501** (01:35:50–01:36:34 PDT): seven 2 s runs across all three gating levels, every record ok, cycles per op 546 / 546 / 318.
- **Passes.** 9510 01:36:41–01:45:08 PDT, 9511 01:45:23–01:54:08, 9512 01:54:23 PDT–01:03:15 PST, 9513 01:03:30–01:12:21 PST, 9514 01:12:54–01:21:50 PST: 260 runs, 5 skipped by the launch rule, no run-gate failure. The queue log's clock goes back an hour inside 9512; the reduction uses epoch times.
- **Amendment A1 and its premise.** At 01:47 PDT a desk reduction of pass 9510 **alone**, whose own leakage slope was 0.2286 W/°C, set it aside (`fp32.randn` spans 1.024 W), so A1 added pass 9514, inside 48 card-minutes, before any tile's value entered a decision (`logs/a1-pass-9510-alone.txt`). **On the registered reduction of all five passes the premise does not hold:** the slope is 0.2959 W/°C, `fp32.randn` spans 0.967 W in 9510 and the pass is kept, while the dip in `fp16.randn` sets 9513 aside. 9510's fate is slope-sensitive (1.049 W at 0.1994, 1.218 W at 0: aside). A1 still earned its place: without 9514 the kept passes are 9510–9512 and C1, C2, C7 and C12 read UNDER-RESOLVED (labelled, `no-a1-arm/`). A1's second clause (9515 if fewer than 3 are kept) did not fire: the gates-only look read four kept.
- **Leakage.** Primary `auto` 0.2959 W/°C over 167 runs (E78's 0.1994, E86's 0.2290): it lowers a random fp32 tile by about 0.35 W against the 0.1994 arm, which is most of the session-tie difference below. At each fixed arm (0.1994, 0.3803, 0) the gates keep three passes, and C1, C2, C7 and C12 read UNDER-RESOLVED because a skipped tile falls to two; the other nine verdicts hold at every arm, so no verdict is slope-sensitive (`scored-leak*.json`, `results-leak*.md`).
- **The session tie, E95-S1** (reported):

| cell | E95 D (W) | reference | its D (W) | diff (W) | band | verdict | the 0.1994 arm's diff (W) |
|---|---|---|---|---|---|---|---|
| `fp32.randn` | 24.321 ± 0.202 | E78 | 24.7249 | -0.404 | ±0.5 | PASS | -0.056 |
| `fp16.randn` | 21.906 ± 0.091 | E78 | 22.1624 | -0.257 | ±0.5 | PASS | -0.003 |
| `anchor_pi` | 8.292 ± 0.071 | E78 | 8.3603 | -0.068 | ±0.5 | PASS | +0.001 |
| `int8.full` | 7.095 ± 0.065 | E78 | 7.0565 | +0.039 | ±0.25 | PASS | +0.083 |
| `fp16.real_l6_mlp_down` | 21.813 ± 0.086 | E86 | 21.9821 | -0.169 | ±0.5 | PASS | +0.112 |
| `fp16.real_l6_attn_qk` | 21.194 ± 0.149 | E86 | 21.4378 | -0.243 | ±0.5 | PASS | -0.031 |
| `int8.real_l6_mlp_down` | 5.669 ± 0.311 | E86 | 5.7476 | -0.079 | ±0.5 | PASS | -0.008 |

- **Checks (E78-R5's, reported):** idle consistency median |S − S0 − D| 0.078 W (≤ 0.15); rail lag re-fit median 0.95 s (in [0.80, 1.15]); duty 0.9959–0.9968 (in [0.990, 1.000]); carry-over 0.0021 ± 0.0012 W/W (≤ 0.01); every dumped tile equals its registered sha256 (a run gate, no failure); idle level 25.864 ± 0.009 W; pi tie drift 0.10–0.21 W (`e95.json` › `tie_drift_w`).
- **Departures, each dated.** (1) A1 above: a fifth pass, and the card budget from 45 to 48 min; the card took 46.8. (2) In pass 9510 `fp16.randn` has two runs, not three, so the conventions' "three runs' mean" is two there. (3) Two scratch reads between passes: pass 9510 alone at 01:47 PDT, for A1 (it kept no run and printed no tile's D), and pass 9511 alone at 01:54 PDT, after A1 was pushed, as a sanity read; neither entered a decision. (4) The first collection ran over a scratch path and recorded it, so it was re-run over a copy inside the ignored `build/` tree: same verdicts, relative paths. (5) The comparison with Q132(b)'s bench is not in E95's registration: it was added after the run, and the predictions are the bench lane's.

## What it changes

- **Item 3 of the kinds page's section 11 ("more real tensors"):** the energy half is closed for this card: more layers and models, a layer with exact zeros, other int8 calibrations, an fp16 forward pass. Open: their speed under the governor (E96), several sustained runs for real int8 (E87's question), and another card. C7's rank on E86's window stays unresolved, at a size that no longer matters (under 0.12 W).
- **Item 4 (the zero gate on silicon):** E93 settled −0.0 on synthetic tiles; this is the same on a real layer, at 19.96 W against 9.34 W.
- **Item 6 (a power model that predicts every kind):** narrowed. M4 predicted 30 blind real tiles to 0.16 W rms; (a) misses gated int8 by 1.1 W. E95 scores them; it does not decide which stage spends what.
- **Item 11 (tile-to-tile spread):** one tile a cell remains a draw, and on a conv layer the draw matters (real2 README, departure 6). E95 does not measure that spread.
- **For the kinds table:** rows for ReLU tiles at their own live share, an attention row 3–4% under random in fp16, and an int8 calibration note that names the outlier.
- **For the instrument record:** the launch rule's skip is new; a retry for a run whose launch reading flicks needs a registration of its own, as does a run gate on in-window dips.

## Files

| file | what |
|---|---|
| `e95.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered reduction (reduce_e78.py unchanged, via reduce_e95.py), primary leakage slope |
| `scored.json`, `results.md`, `score.log` | every claim, verdicts at the arms beside (score_e95.py), every tile's table, the gated tiles' distances, (a′), the session tie, the checks |
| `e95-leak{0.1994,0.3803,0}.json`, `runs-leak*.csv`, `reduce-leak*.{txt,log}`, `scored-leak*.json`, `results-leak*.md` | the registered leakage arms |
| `dips-arm/` | the registered dips-removed arm: `dips.json`, `e95-nodips.{json,txt}`, `runs-nodips.csv`, `scored-nodips.json`, `results-nodips.md` |
| `no-a1-arm/` | labelled sensitivity: the four passes registered before A1, without 9514 |
| `bench-check.py`, `bench-check.txt`, `bench-prediction-2b7ece4a.json`, `bench-prediction-m4-b995463e.json` | Q132(b)'s frozen predictions, byte for byte as of their commits, beside the measurement |
| `readme-numbers.py`, `readme-numbers.txt` | every derived number this README quotes that `results.md` does not print |
| `aifoundry3/kinds/p9510…p9514`, `aifoundry3/kinds/kinds-smoke-p9501` | raw passes as the box wrote them (telemetry at 10 Hz, launch records, marks, dumped tiles, config reads, manifests) |
| `logs/` | the queue and chain logs, the dry pass, the box's setup, the smoke, the session's config reads, binary hashes, `a1-pass-9510-alone.txt`, `push-and-claim-times.txt` |
| `code.sha256` | every harness file, the freeze and the tiles, as reduced |

Code: `tools/claims-v3/kinds/` (`E95.md`, `e95_common.py`, `run_e95.py`, `block_e95.sh`, `queue_e95.sh`, `run_e95.sh`, `chain_e95_a1.sh`, `reduce_e95.py`, `score_e95.py`, `collect_e95.sh`, `posthoc_dips_e95.py`, `selftest_e95.py`, `make_predictions_e95.py`, `predictions-e95.json`). Reproduce from a copy of the raw passes at `build/e95-raw/kinds/`: `PY=/usr/bin/python3 bash tools/claims-v3/kinds/collect_e95.sh 'p95[1-9][0-9]' build/e95-raw`.
