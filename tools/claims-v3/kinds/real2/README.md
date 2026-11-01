# Q132(r): more real tensors as kinds tiles, with frozen predictions (for E95 and E96)

Sun 1 Nov 2026 (week 44). **Thirty new 2,048-byte operand tiles, cut from six public models run on public-domain inputs:**
ReLU networks with exact zeros (ResNet-18, VGG-16, T5-small), more layers and models with none (GPT-2 small, BERT,
ViT-B/16), an fp16 and a bf16 forward pass of GPT-2, and other int8 calibrations. Each is written by
[`make_kinds.py`](../make_kinds.py)'s own `encode()` and measured by its own `tile_stats()`, so it is the same kind of
object as E78's 51 kinds and Q130(n)'s nine. This is the desk half of item 3 of the kinds page's section 11 ("more real
tensors"). **Frozen here, before any card runs them:** each tile's predicted switching power at 600 MHz on aifoundry3
(for E95), its burst and sustained clock under aifoundry2's own governor (for E96), the gate law's prediction for each
gated tile, and thirteen energy and six speed claims, in [`predictions-real2.json`](predictions-real2.json), sha256
**`0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a`**. Nothing here touches a card, so nothing here closes
item 3: E95 and E96 do or do not.

## Results

**1. A ReLU network hands the gate exact zeros in fp32, and the word grouping takes most of them away in fp16 and int8.**
The gate tests a whole 32-bit word (fact 3 in `make_kinds.py`). That word is one fp32 element, two fp16 elements or four
int8 bytes, so the share of A's words that are zero falls with the format. No weight is exactly zero, so this share is
also the share of lanes the gate closes on the whole matrix:

| layer | exact zeros in A | fp32 zero words | fp16 zero words | int8 zero words (max-abs) | int8 zero bytes (max-abs) |
|---|---|---|---|---|---|
| ResNet-18 `layer1.0.conv2` | 0.470 | 0.470 | 0.366 | 0.275 | 0.485 |
| ResNet-18 `layer1.1.conv1` | 0.216 | 0.216 | 0.134 | 0.072 | 0.226 |
| ResNet-18 `layer2.0.conv1` | 0.263 | 0.263 | 0.146 | 0.065 | 0.275 |
| ResNet-18 `layer2.1.conv2` | 0.768 | 0.768 | 0.633 | 0.471 | 0.780 |
| ResNet-18 `layer3.0.conv1` | 0.530 | 0.530 | 0.357 | 0.206 | 0.550 |
| ResNet-18 `layer3.1.conv1` | 0.588 | 0.588 | 0.436 | 0.293 | 0.607 |
| ResNet-18 `layer4.0.conv1` | 0.618 | 0.618 | 0.479 | 0.348 | 0.639 |
| ResNet-18 `layer4.1.conv2` | 0.838 | 0.838 | 0.750 | 0.633 | 0.843 |
| VGG-16 `fc2` input | 0.758 | 0.758 | 0.575 | 0.347 | 0.765 |
| VGG-16 `fc3` input | 0.773 | 0.773 | 0.599 | 0.374 | 0.779 |
| T5-small block 0 feed-forward | 0.917 | 0.917 | 0.841 | 0.749 | 0.929 |
| T5-small block 2 feed-forward | 0.971 | 0.971 | 0.944 | 0.903 | 0.975 |
| T5-small block 5 feed-forward | 0.955 | 0.955 | 0.911 | 0.927 | 0.981 |

([`real2.json`](real2.json) `desk_gate_by_format.<product>`, whole matrices; `capture.json` `products.<product>.stats`.)
VGG's zeros fall as independent zeros would: 0.758² = 0.575 in fp16, and 0.758⁴ = 0.330 against 0.347 in int8, where
rounding adds some. A conv layer keeps more, because consecutive k are neighbouring pixels of one channel and its zeros
cluster: `layer3.0.conv1`'s 0.530 falls to 0.357 and 0.206, against independence's 0.281 and 0.079. Twelve of the thirteen
layers fall in that order. In T5's block 5 max-abs rounds so many bytes to zero (0.981) that int8's words (0.927) overtake
fp16's (0.911).

**2. In int8 the calibration decides whether the gate acts at all.** E86's three windows have no zero word, and the page
says real int8 tiles save through small values, not the gate. That holds for those windows, not as a rule. In four of the
fourteen GELU layers here one activation is 31–60× the 99th percentile. Max-abs scaling then rounds 79–97% of A's bytes
to zero and 39–88% of its words, so the gate closes on a layer with no exact zeros at all. A 99.9th percentile clip
brings those words back to 0.0–0.6%:

| GELU layer | max \|A\| / 99th percentile | int8 max-abs: zero bytes, zero words | int8 99.9th percentile: zero bytes, zero words |
|---|---|---|---|
| GPT-2 layer 0 | 11.2 / 0.57 | 0.188, 0.004 | 0.032, 0.000 |
| GPT-2 layer 3 | 10.7 / 0.63 | 0.244, 0.004 | 0.056, 0.000 |
| GPT-2 layer 6 | 4.6 / 0.76 | 0.074, 0.000 | 0.028, 0.000 |
| GPT-2 layer 9 | 6.0 / 1.03 | 0.090, 0.000 | 0.040, 0.000 |
| **GPT-2 layer 11** | **44.1 / 1.40** | **0.888, 0.624** | 0.046, 0.000 |
| **BERT layer 2** | **49.2 / 0.82** | **0.967, 0.876** | 0.268, 0.006 |
| BERT layer 6 | 7.1 / 0.82 | 0.331, 0.016 | 0.181, 0.002 |
| BERT layer 11 | 7.7 / 0.80 | 0.179, 0.001 | 0.062, 0.000 |
| **DistilBERT layer 1** | **36.3 / 0.85** | **0.791, 0.394** | 0.181, 0.001 |
| DistilBERT layer 3 | 5.2 / 0.74 | 0.146, 0.005 | 0.070, 0.003 |
| DistilBERT layer 5 | 6.8 / 0.45 | 0.069, 0.000 | 0.013, 0.000 |
| ViT-B/16 layer 2 | 4.4 / 0.70 | 0.202, 0.003 | 0.111, 0.000 |
| **ViT-B/16 layer 5** | **42.4 / 0.91** | **0.887, 0.624** | 0.188, 0.002 |
| ViT-B/16 layer 11 (result 3) | 11.8 / 1.85 | 0.884, 0.612 | 0.861, 0.553 |

(`real2.json` `desk_gate_by_format.<product>`.) So the predicted power of one window of GPT-2's layer 11 moves 4.4× with
the calibration: 1.16 W under max-abs (gate 0.637) against 5.15 W under the 99.9th percentile clip (gate 0.000). The
other direction exists too. The TFLite convention for activations maps a ReLU zero to −128 (0x80), so the gate sees
nothing: VGG's int8 tile goes from gate 0.336 to 0.000, predicted 2.71 W to 4.10 W, with the same numbers and the same
weights. On E86's own window the calibrations Q130(n) predicted are close together: 5.18 W (committed), 5.22 W (99.99th),
5.35 W (per token), 5.43 W (99.9th), 0.74–0.77× of `full`'s measured D, as `amendment-1.json`'s `calibration_sensitivity`
said. Those steps sit at the size of E86's paired noise.

**3. Two things nobody asked for turned up, and each is now a tile.**
- **T5-small's weights sit on the bf16 grid.** In all six feed-forward weights captured (blocks 0, 2, 5; `wi` and `wo`)
  every low 16 mantissa bits are zero (`capture.json` `products.t5small_l*_ff_*.stats.B.low_mantissa_bits_zero_frac` = 1.0),
  which no other model's are (under 0.001). So `t5small_l0_up`, with no zero word and a full-mantissa A, moves 49,830 bus
  bits an op against `randn`'s 82,214: a real tile whose B bits barely move, predicted at 0.91 of random. It is what
  fp32's B-side price looks like in real data, and the predictor prices B at 0.
- **ViT-B/16's last block is 55% −0.0.** Its pre-activations have a median of −5.91 and 61% lie below −5. torch's float32
  GELU behaves as x·½(1 + erf(x/√2)): its 1 + erf rounds to exactly 0 between x = −5 and −6, so the output is −0.0, the word
  0x80000000 ([`check_negzero.txt`](check_negzero.txt)). An erfc-form GELU would give tiny negatives instead. The gate's test is
  `word == 0`, so it stays open on numbers that are arithmetically zero. Predicted 20.4 W if the gate is blind to them,
  against 9.3 W [6.8, 11.9] by the gate law if it were not. In int8 the same layer's −0.0 becomes a zero byte and the gate closes on 0.547
  of the tile. E93 tests −0.0 on synthetic tiles on another card; this is the real case.

**4. An fp16 forward pass is real, works, and barely moves the bits.** GPT-2 small computed in fp16 (every stored value
binary16, dot products with an fp32 accumulator, as TensorFMA16A32 does) reaches a next-token loss of **3.0461 nats**
against fp32's 3.0462, top-1 38.58% in both (`capture.json` `checks.gpt2_fp16_forward`, `gpt2_fp32`). Its activations against
rounding the fp32 ones: 12–19% of elements identical, the median element 2–3 fp16 ulps away (99th percentile 90–469), 2.0–2.5
bits differing per element, sign differing in 0.03–0.07%, relative rms 0.10–0.31% against rounding's 0.02%, and −0.0
rising from 0.006–0.04% to 0.2–0.8% in the GELU outputs (`checks.gpt2_fp16_forward.vs_rounding_fp32`). torch's own `.half()` on
CPU lands in the same place (loss 3.0469, median 1–2 ulps; `checks.gpt2_torch_half`). On E86's window the tile moves 82,986
bus bits against the rounded tile's 83,370, predicted −0.10 W. A bf16 pass came free: loss 3.0508, one tile (tier 2)
beside E78's synthetic `bf16trunc`.

**5. The frozen predictions, tile by tile.** D is board switching power over the type's own zeros, the quantity E78 and E86
measured. (a) is Q130(n)'s predictor, unchanged, with an interval fitted on its known out-of-sample misses (below), not on
E78. (c) is the gate law, stated separately. (b) is E83's relation applied to (a), its interval built as Amendment 1 built
it. `gate closes` is `tile_stats()`'s `gated_lane_frac`; it equals the zero-word column because no tile's B has a zero word.

| tile | format | group | window (rows, k, cols) | zero words in A | gate closes | bus bits/op | (a) D, W [95%] | (c) gate law, W [95%] | (b) burst MHz [95%] | (b) sustained MHz [95%], limit |
|---|---|---|---|---|---|---|---|---|---|---|
| `resnet18_l2c1` | fp32 | exact zeros (ReLU) | 2816–2832, 320–336, 112–128 | 0.191 | 0.191 | 80,128 | **19.66** [16.52, 22.81] | 20.13 [17.56, 22.70] | 756 [719, 794] | 632 [603, 670], thermal |
| `resnet18_l3c1` | fp32 | exact zeros (ReLU) | 1248–1264, 192–208, 48–64 | 0.445 | 0.445 | 78,630 | **13.65** [10.51, 16.80] | 14.03 [11.46, 16.60] | 800 [774, 800] | 703 [660, 747], thermal |
| `resnet18_l3c1` | fp16 | exact zeros (ReLU) | 1248–1264, 192–224, 48–64 | 0.367 | 0.367 | 78,572 | **13.19** [10.05, 16.33] | 14.29 [13.13, 15.45] | 800 [777, 800] | 710 [666, 755], thermal |
| `resnet18_l3c1` | int8 | exact zeros (ReLU) | 1248–1264, 192–256, 48–64 | 0.176 | 0.176 | 26,958 | **3.62** [2.51, 4.73] | 5.89 [4.83, 6.95] | 800 [800, 800] | 800 [784, 800], none |
| `vgg16_fc2` | fp32 | exact zeros (ReLU) | 0–16, 3840–3856, 3696–3712 | 0.723 | 0.723 | 71,262 | **7.02** [3.88, 10.17] | 7.37 [4.81, 9.94] | 800 [800, 800] | 793 [746, 800], none |
| `vgg16_fc2` | fp16 | exact zeros (ReLU) | 0–16, 3840–3872, 3696–3712 | 0.551 | 0.551 | 74,852 | **8.83** [5.68, 11.97] | 10.35 [9.19, 11.52] | 800 [800, 800] | 770 [722, 800], thermal |
| `vgg16_fc2` | int8 | exact zeros (ReLU) | 0–16, 3840–3904, 3696–3712 | 0.336 | 0.336 | 19,732 | **2.71** [1.59, 3.81] | 4.82 [3.76, 5.88] | 800 [800, 800] | 800 [800, 800], none |
| `t5small_l0_down` | fp32 | exact zeros (ReLU) | 48–64, 576–592, 352–368 | 0.949 | 0.949 | 25,680 | **1.18** [0.00, 4.32] | 1.93 [0.00, 4.50] | 800 [800, 800] | 800 [800, 800], none |
| `t5small_l0_down` | fp16 | exact zeros (ReLU) | 48–64, 576–608, 352–368 | 0.871 | 0.871 | 48,432 | **2.36** [0.00, 5.50] | 3.48 [2.32, 4.65] | 800 [800, 800] | 800 [784, 800], none |
| `gpt2_l3_mlp_down` | fp32 | no exact zeros | 32–48, 752–768, 240–256 | 0.000 | 0.000 | 82,110 | **24.37** [21.91, 26.83] | — | 712 [682, 742] | 603 [600, 622], thermal |
| `gpt2_l9_attn_qk` | fp32 | no exact zeros | 64–80, 192–208, 64–80 | 0.000 | 0.000 | 84,644 | **24.48** [22.02, 26.95] | — | 710 [681, 741] | 602 [600, 622], thermal |
| `gpt2_l9_attn_qk` | fp16 | no exact zeros | 112–128, 640–672, 0–16 | 0.000 | 0.000 | 83,322 | **21.51** [18.35, 24.66] | — | 738 [703, 776] | 616 [600, 650], thermal |
| `bert_l6_up` | fp32 | no exact zeros | 96–112, 128–144, 1920–1936 | 0.000 | 0.000 | 82,334 | **24.40** [21.94, 26.86] | — | 711 [682, 741] | 603 [600, 622], thermal |
| `bert_l6_up` | fp16 | no exact zeros | 32–48, 608–640, 1536–1552 | 0.000 | 0.000 | 84,270 | **21.51** [18.35, 24.66] | — | 738 [703, 776] | 616 [600, 650], thermal |
| `vit_l5_down` | fp32 | no exact zeros | 240–256, 64–80, 320–336 | 0.000 | 0.000 | 82,206 | **24.41** [21.95, 26.87] | — | 711 [682, 741] | 603 [600, 622], thermal |
| `vit_l5_down` | fp16 | no exact zeros | 48–64, 2496–2528, 160–176 | 0.000 | 0.000 | 83,684 | **21.64** [18.48, 24.79] | — | 736 [701, 775] | 616 [600, 649], thermal |
| `t5small_l0_up` | fp32 | bf16-grid weights | 112–128, 0–16, 816–832 | 0.000 | 0.000 | 49,830 | **22.46** [20.00, 24.92] | — | 728 [698, 760] | 610 [600, 635], thermal |
| `vit_l11_down` | fp32 | −0.0 | 560–576, 1488–1504, 656–672 | 0.000 | 0.000 | 70,024 | **20.42** [17.96, 22.88] | — (9.34 if the gate took −0.0) | 748 [716, 781] | 625 [601, 654], thermal |
| `gpt2_l6_mlp_down_fp16fwd` | fp16 | fp16 forward | 16–32, 1088–1120, 336–352 | 0.000 | 0.000 | 82,986 | **21.25** [18.10, 24.41] | — | 740 [705, 779] | 618 [600, 653], thermal |
| `gpt2_l6_down_per_token` | int8 | int8 calibration | 112–128, 2816–2880, 112–128 | 0.000 | 0.000 | 46,996 | **5.35** [4.33, 6.38] | — | 800 [800, 800] | 798 [781, 800], none |
| `gpt2_l6_down_p9999` | int8 | int8 calibration | 112–128, 2816–2880, 112–128 | 0.000 | 0.000 | 44,500 | **5.22** [4.20, 6.25] | — | 800 [800, 800] | 799 [782, 800], none |
| `gpt2_l6_down_p999` | int8 | int8 calibration | 112–128, 2816–2880, 112–128 | 0.000 | 0.000 | 47,092 | **5.43** [4.41, 6.45] | — | 800 [800, 800] | 798 [781, 800], none |
| `gpt2_l11_down_maxabs` | int8 | int8 calibration | 32–48, 1856–1920, 0–16 | 0.637 | 0.637 | 7,330 | **1.16** [0.05, 2.27] | 2.82 [1.76, 3.88] | 800 [800, 800] | 800 [800, 800], none |
| `gpt2_l11_down_p999` | int8 | int8 calibration | 32–48, 1856–1920, 0–16 | 0.000 | 0.000 | 42,146 | **5.15** [4.13, 6.18] | — | 800 [800, 800] | 799 [782, 800], none |
| `vgg16_fc2_asym` | int8 | int8 calibration | 0–16, 3840–3904, 3696–3712 | 0.000 | 0.000 | 22,836 | **4.10** [3.08, 5.12] | — | 800 [800, 800] | 800 [783, 800], none |
| `t5small_l0_down` (tier 2) | int8 | exact zeros (ReLU) | 48–64, 576–640, 352–368 | 0.766 | 0.766 | 6,752 | **0.79** [0.00, 1.90] | 1.96 [0.90, 3.02] | 800 [800, 800] | 800 [800, 800], none |
| `vit_l11_down` (tier 2) | int8 | −0.0 | 1504–1520, 2432–2496, 32–48 | 0.547 | 0.547 | 16,434 | **1.77** [0.66, 2.88] | 3.42 [2.36, 4.47] | 800 [800, 800] | 800 [800, 800], none |
| `gpt2_l6_attn_qk_fp16fwd` (tier 2) | fp16 | fp16 forward | 64–80, 288–320, 32–48 | 0.000 | 0.000 | 80,964 | **21.35** [18.20, 24.51] | — | 739 [704, 778] | 618 [600, 652], thermal |
| `gpt2_l6_mlp_down_bf16fwd` (tier 2) | fp32 | bf16 forward | 48–64, 720–736, 560–576 | 0.000 | 0.000 | 32,384 | **17.28** [14.82, 19.74] | — | 781 [747, 800] | 657 [626, 692], thermal |
| `gpt2_l11_down_asym` (tier 2) | int8 | int8 calibration | 32–48, 1856–1920, 0–16 | 0.000 | 0.000 | 14,114 | **3.98** [2.95, 5.00] | — | 800 [800, 800] | 800 [784, 800], none |

([`predictions-real2.json`](predictions-real2.json) `tiles.<type>/<name>`: `a_aifoundry3_600mhz`, `c_gate_law`,
`b_aifoundry2_governor`, and for a tile with a partner `a_prime_offset`. The int8 bus counts are provisional, as for every
int8 kind.)

In words. **No-zero real fp32 and fp16 should cost what random numbers cost**: 0.986–0.990 of E78's measured random fp32,
and 0.971–0.976 of its random fp16, which is 0.989–0.995 of the predictor's own random fit
(`claims.E95.C1_within_2pct`). **A ReLU tile in fp32 or fp16 should cost about its live share of random**: the two
predictions agree within 1.6 W. **In int8 they do not agree** (2.7–3.6 W against 4.8–5.9 W), which C5 decides.
**The gate should buy clock:** every float tile under 15 W is predicted to burst at about 800 MHz against random's 708–731
(E83's relation on E78's measured random kinds, `relation_e83.random_kind_from_relation_mhz`), and to sustain 703–800 MHz
against 602–612.

**6. The claims, frozen** (`claims.E95`, `claims.E96`; each has its tiles, thresholds and rule there; r is a tile's D over the
same pass's random kind of its format):

| claim | says | PASS if | FAIL if | predicted |
|---|---|---|---|---|
| **C1** | no-zero fp32, fp16 within 2% of random in every model | every (model, format) cell's r interval lies in [0.98, 1.02] | any lies entirely outside | fp32 0.987–0.988; fp16 0.971–0.976 of E78's random, 0.989–0.995 of the fit. E86's fp16 attention tile read 0.971, so this can fail |
| **C2** | they sit below random on average | format mean r's upper bound < 1, both formats | a lower bound > 1 | 0.988, 0.972 |
| **C3a** | a ReLU tile's power follows its live share | all 7 fp32, fp16 ReLU tiles inside the gate law's interval | two or more outside | table |
| **C3b** | D's slope on live share is about L | slope / L in [0.85, 1.25], both formats | either outside | 0.984, 0.963 from (a); 1.039, 0.937 on E78's and E90's gated tiles |
| **C4** | same numbers cost more in fp16 than fp32 | r(fp16) − r(fp32) lower bound > 0 on all three pairs | any upper bound < 0 | VGG 0.28 → 0.40; ResNet 0.55 → 0.60; T5 0.05 → 0.11 |
| **C5** | int8 ReLU follows bits more than live share | (a) nearer than (c) on both tiles | (c) nearer on both | (a) 3.62, 2.71; (c) 5.89, 4.82 W |
| **C6** | calibration lever on a GELU layer with an outlier | p99.9 − max-abs lower bound ≥ 2.0 W | upper bound < 2.0 W | +3.99 W |
| **C7** | E86's window ranks committed < per-token < p99.9, p99.99 beside committed | per-token's, p99.9's lower bounds > 0 and p99.99 inside ±0.40 W | either upper bound < 0, or p99.99 entirely outside | +0.17, +0.24, +0.04 W; INCONCLUSIVE is the likely outcome |
| **C8** | asymmetric activations turn the gate off | asym − symmetric lower bound > 0.5 W | upper bound < 0 | +1.40 W |
| **C9** | −0.0 passes the gate | D's lower bound > 11.91 W | D's upper bound ≤ 11.91 W | 20.42 W |
| **C10** | bf16-grid weights cost clearly less | r's upper bound < 0.97 | lower bound ≥ 0.97 | 0.908 |
| **C11** | an fp16 forward pass costs what rounding costs | paired difference inside ±0.50 W | entirely outside | −0.10 W |
| **C12** | the (a) intervals hold | ≥ 20 of 25 new tier-1 tiles inside | < 18 | |
| **S1** | E83's relation fed (a) holds the clocks | ≥ 80% of bursts and of sustained inside | < 60% | table |
| **S2** | a gated float tile under 15 W bursts well above randn | every tile ≥ +40 MHz | any < +15 MHz | 800 against 708–731 |
| **S2b** | and sustains above it | every tile ≥ +50 MHz | any < +15 MHz | 703–800 against 602–612 |
| **S3** | no-zero real tiles burst at random's speed | mean within ±15 MHz, both formats | otherwise | |
| **S4** | the sustained limit is called right | ≥ 80% | < 60% | table |
| **S5** | the relation on measured c | burst and sustained rms ≤ 15 MHz | either > 25 MHz | |

Between PASS and FAIL a claim reads INCONCLUSIVE. Intervals are t(0.975, n − 1) × SE over kept passes, paired where a
difference is named; fewer than 3 kept passes is NOT SCORED; a claim short of its population is UNDER-RESOLVED, never
PASS. The lanes may add rules of their own and cite this file by sha256; they do not move these.

## What E95 and E96 need

**Both.** Tiles are `tools/claims-v3/kinds/real2/tiles/<type>/<name>.bin`, 2,048 bytes, A then B. `real2.json`
(`6e259fd2…`) has the shape of Q130(n)'s `real.json`: `tiles.<type>.<name>` with `file` (relative to `real2/`), `bytes`,
`sha256`, `sha256_a`, `sha256_b`, `stats`, `what`. `predictions-real2.json` has the shape of `predictions-real.json`:
`tiles.<type>/<name>` with `tile`, `tile_sha256`. A box needs `tools/claims-v3/kinds/real2/tiles/` (rsync or a pull). Run
one with `sparsity_host --test fma --type <t> --values file:<tile>`. As for every kind, a `file:` run checks no arithmetic.

**E95 (aifoundry3, 600 MHz).** Port `e86_common.py`: its `real_items()` works with `real2.json`, `REAL_REL =
tools/claims-v3/kinds/real2`, item names `<type>.r2_<name>`. Tier 1 is 25 new tiles plus E86's `fp16.real_l6_mlp_down` and
`int8.real_l6_mlp_down` from `real/` (C7's and C11's partners), 27 in all; `tier` in `real2.json` marks them. With E78's six
anchors three times a pass and the tie twice that is 47 runs and 2 burn-ins a pass. E86 took about 12 s a run, so about
10 min a pass and 40 card-minutes for four passes with the smoke. Tier 2's five tiles add about 1 min a pass.
A smoke of `fp32.r2_vgg16_fc2`, `fp16.r2_t5small_l0_down` and `int8.r2_gpt2_l11_down_maxabs` covers all three gating levels.
E78's reduction applies unchanged; zero-bearing tiles are nothing new to it (`sparse90`). Score `claims.E95` on `D` at the
primary leakage slope, and report D's distance from (a) and from (c) for every gated tile.

**E96 (aifoundry2, own governor).** Port `kspeed/e87/run_e87.py`: `REAL_DIR`, `REAL_PRED`, `REAL_JSON` and `FROZEN_SHA` point
here, and the path check's prefix becomes `tools/claims-v3/kinds/real2/`; its `--dry` reads `b_aifoundry2_governor.c_w`, which is here.
Scoring intervals are in the same file (Amendment 1 kept them apart; this file holds them beside the points). All 27 in
E87's full shape is about 75 card-minutes (E87: 13 s a burst, 100 s a sustained run). `e96_suggested` gives a shorter plan:
bursts of every tier-1 tile and E87's six anchors, two passes (about 14 min), and sustained runs of the 15 tiles in
`sustained_first` (the gated float tiles, T5's and ViT's special cases, one no-zero tile per format, four int8 tiles) with the
anchors and randn twice (about 38 min). The fp16 and int8 `real_l6_mlp_down` tiles already ran in E87. Item 3's "several sustained
runs per kind for real int8" is about E87's three int8 tiles against `full`, at the edge of the 65 °C trip; real2's gated int8 tiles are
predicted far under that power, so they do not test it. That lane needs its own repeats of those tiles.

## How the intervals were built

**(a), known misses.** E90's correction: the predictor "tracks a re-draw's offset from a measured tile (0.28 W rms), not what a
tile costs, which it misses by 0.6–2.0 W". So the half-width is t(0.975, n) × the rms about zero of its misses, measured − frozen
point, on tiles it was not fitted on, per class, and a bias widens it (`known_misses.classes`):

| class | tiles and misses (W) | n | rms (W) | mean (W) | half-width (W) |
|---|---|---|---|---|---|
| float, ungated, fp32 | E86 −0.11, +0.16, −0.18; E90 ±1 +1.14, \|randn\| −1.59, −\|randn\| −1.75, ±π −0.80 | 7 | 1.041 | −0.447 | **±2.46** |
| float, ungated, fp16 | E86 +0.25, +0.63, −0.10; E90 ±1 −0.33, \|randn\| −1.70, −\|randn\| −1.69, `uniform01` −2.05, −1.92, −1.82 | 9 | 1.395 | −0.970 | **±3.15** |
| float, gated | E90 `sparse50` +1.71, +1.59, +1.73; `nn_like` +0.77, +0.67, +0.64 | 6 | 1.285 | +1.185 | **±3.14** |
| int8, ungated | E86 +0.40, +0.56, −0.21; E90 ±1 −0.14 | 4 | 0.368 | +0.155 | **±1.02** |
| int8, gated | **no E86 or E90 tile gates in int8**, so E78's nested-LOO residuals on its gated kinds: `sparse50` +0.27, `sparse90` +0.44, `wsparse50` +0.68, `wsparse90` +0.40, one-sided +0.50, +0.30 | 6 | 0.454 | +0.433 | **±1.11** |

Against Amendment 1's ±2.41 / ±2.35 / ±1.32 W, fp32 barely moves, fp16 widens by a third and int8 narrows. Beside each tile, labelled and never a verdict: the
E86-only arm (±0.49 / ±1.25 / ±1.33 W, what a tile that behaves like E86's would need), and the class's mean miss as a bias
arm (`a_aifoundry3_600mhz.e86_only_arm_w`, `bias_arm_w`). **(a′), offsets:** a tile with a partner also gets the predictor's
difference from that partner, where E90-R5 earned its trust: ±0.63 W, t(0.975, 9) × 0.2765 W (`a_prime_offset`).

**(c), the gate law.** D = g·G + (1 − g)·L, with g the tile's own `gated_lane_frac`, L E78's measured D of the format's random kind
and G the mean of E78's two one-sided kinds (every lane gated, one operand's bus moving). No parameter is fitted. Its interval
comes from its misses on E78's gated random-magnitude kinds and E90's gated re-draws (`gate_law.per_type`):

| format | L (W) | G (W) | known misses: n, rms, mean (W) | half-width (W) | measured ÷ law on them | slope of D on live share ÷ L, on them |
|---|---|---|---|---|---|---|
| fp32 | 24.725 | 0.713 | 6, 1.049, +0.859 | ±2.57 | 0.632–1.198 | 1.039 |
| fp16 | 22.162 | 0.720 | 8, 0.504, −0.086 | ±1.16 | 0.799–1.203 | 0.937 |
| int8 | 7.056 | 0.401 | 3, 0.332, −0.024 | ±1.06 | 0.721–1.133 | 1.107 |

Beside it, `D_w_with_L_from_e86_real_tiles` uses E86's three-tile mean as L (fp32 24.39, fp16 21.80, int8 5.86 W): int8's real numbers
cost less than `full` on a live lane too, which is why C5 is a real question.

**(b), the clock.** `make_real.py`'s conversion and `amend_real.py`'s rule, unchanged: E83's relation (burst W* 66.15 W, σ 2.75 W;
sustained W* 49.75 W, σ 1.95 W) on c = c_E64(type, zeros) + D / 1.01865; the clock at the two ends of (a)'s interval, widened in
quadrature by 1.96 × 10.6 MHz (burst) or 8.4 MHz (sustained); clamped to [600, 800]; a range wholly at the cap stays [800, 800]. It
leaves out the step from aifoundry3's D to aifoundry2's power beyond E83's conversion and the session's heat path (E87's ran 0.5 °C
warmer than E80's).

## How the tiles were made

| model | Hugging Face repo at revision, or torchvision | file | bytes | sha256 | licence |
|---|---|---|---|---|---|
| GPT-2 small | `openai-community/gpt2` at `607a30d783dfa663caf39e06633721c8d4cfcd7e` | `model.safetensors` | 548,105,171 | `248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707` | MIT |
| T5-small | `google-t5/t5-small` at `df1b051c49625cf57a3d0d8d3863ed4d13564fe4` | `model.safetensors` | 242,043,056 | `bd944e5f1b3ad9b70dd9d00010a517059e19265671076b8b0a4a58d9491842bc` | Apache-2.0 |
| BERT | `google-bert/bert-base-uncased` at `86b5e0934494bd15c9632b12f734a8a67f723594` | `model.safetensors` | 440,449,768 | `68d45e234eb4a928074dfd868cead0219ab85354cc53d20e772753c6bb9169d3` | Apache-2.0 |
| DistilBERT (desk table only) | `distilbert/distilbert-base-uncased` at `12040accade4e8a0f71eabdb258fecc2e7e948be` | `model.safetensors` | 267,954,768 | `5e3f1108e3cb34ee048634875d8482665b65ac713291a7e32396fb18f6ff0063` | Apache-2.0 |
| ViT-B/16 | `google/vit-base-patch16-224` at `3f49326eb077187dfe1c2a2bb15fbd74e6ab91e3` | `model.safetensors` | 346,293,852 | `1cea07110a4a47edc51420b2dda6f3b8b58e7256e8f44b4ea6aa9696162ccb5d` | Apache-2.0 |
| ResNet-18 | torchvision IMAGENET1K_V1 | `resnet18-f37072fd.pth` | 46,830,571 | `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec` | BSD-3-Clause (torchvision) |
| VGG-16 | torchvision IMAGENET1K_V1 | `vgg16-397923af.pth` | 553,433,881 | `397923af8e79cdbb6a7127f12361acd7a2f83e06b05044ddf496e83de57a5bf0` | BSD-3-Clause (torchvision) |

No model file is committed. Each large file was checked against the Hub's own LFS oid, or torchvision's hash prefix in its name
([`dl_models.py`](dl_models.py); every file's URL and sha256 in `real2.json` `models`).

**Inputs.** Text: the opening of Jane Austen's *Pride and Prejudice* (1813, public domain), the characters of `real/real.json`
`text`; 128 tokens per model's own tokenizer (T5 with its `summarize: ` prefix). Images: 32 pictures from NASA's image library,
which NASA does not copyright under US law, shuffled with a fixed seed: wildlife at Kennedy Space Center, shuttles, aircraft, vehicles, a
volcano ([`dl_images.py`](dl_images.py); URLs and sha256 in `real2.json` `images.files`; not committed). They were picked from a keyword search
([`nasa_search.py`](nasa_search.py)) that skips any picture whose credit or description names another source. ResNet-18 and ViT used the
first 8, VGG-16 all 32, with torchvision's and ViT's standard preprocessing.

**The products** (`capture.json` `products.<product>.what`, `.source`, `.stats`, with the bytes' sha256). Each window's rows, in words: `real2.json`
`tiles.<type>.<name>.window.rows_are`.

| tile | product | A (rows × k) | B (k × columns) | input |
|---|---|---|---|---|
| `resnet18_l2c1` | `resnet18_layer2_0_conv1` | `layer2.0.conv1`'s post-ReLU input, unfolded into 3×3 patches (6,272 × 576): rows (image, patch in scan order), k (channel, height, width) in `F.unfold`'s order | the conv weight flattened the same way (576 × 128) | 8 images |
| `resnet18_l3c1` | `resnet18_layer3_0_conv1` | the same for `layer3.0.conv1` (1,568 × 1,152) | (1,152 × 256) | 8 images |
| `vgg16_fc2`, `vgg16_fc2_asym` | `vgg16_fc2` | `classifier[3]`'s input, fc1's ReLU output (32 × 4,096) | its weight transposed (4,096 × 4,096) | 32 images |
| `t5small_l0_down` | `t5small_l0_ff_down` | encoder block 0's feed-forward ReLU output (128 × 2,048) | `wo.weight` transposed (2,048 × 512) | text |
| `t5small_l0_up` | `t5small_l0_ff_up` | that block's LayerNorm output (128 × 512) | `wi.weight` transposed (512 × 2,048) | text |
| `gpt2_l3_mlp_down` | same | layer 3's GELU output (128 × 3,072) | `h.3.mlp.c_proj.weight` (3,072 × 768) | text |
| `gpt2_l9_attn_qk` | same | layer 9's queries (128 × 768) | keys transposed (768 × 128) | text |
| `bert_l6_up` | `bert_l6_ff_up` | layer 6's attention block output after LayerNorm (128 × 768) | `intermediate.dense` transposed (768 × 3,072) | text |
| `vit_l5_down`, `vit_l11_down` | `vit_l5_ff_down`, `vit_l11_ff_down` | that block's GELU output (1,576 × 3,072): rows (image, token) | `output.dense` transposed (3,072 × 768) | 8 images |
| `gpt2_l6_mlp_down_fp16fwd`, `gpt2_l6_attn_qk_fp16fwd` | same | as `l6_mlp_down`, `l6_attn_qk`, from the fp16 pass, at E86's fp16 windows | the rounded weight, the same as E86's tile's; keys from the fp16 pass | text |
| `gpt2_l6_mlp_down_bf16fwd` | same | from the bf16 pass, in fp32 bytes (low 16 bits zero) | on the bf16 grid | text |
| `gpt2_l6_down_*` | `gpt2_l6_mlp_down` | re-quantised, at E86's int8 window | per output channel, the same as E86's tile's | text |
| `gpt2_l11_down_*` | `gpt2_l11_mlp_down` | layer 11's GELU output (one activation of 44.1) | `h.11.mlp.c_proj.weight`, per output channel | text |

**Checks that these are the real computation.** A conv's unfolded A × B reproduces the conv's own output, and VGG's fc the layer's, to at most
3e-7 relative, or the capture refuses (`products.*.matmul_vs_*_max_rel_err`). GPT-2's numpy pass equals `make_real.forward`, next-token
loss 3.0462 nats. T5 translates *The house is wonderful.* to *Das Haus ist wunderbar.* BERT's top fill-mask for *The capital of France is
[MASK].* is *paris* (DistilBERT's top five hold it, fourth). ResNet-18, VGG-16 and ViT read the images as, among others, American
alligator, bald eagle, pelican, space shuttle (`capture.json` `checks`). The committed int8 `l6_mlp_down` tile came back byte for byte
from this capture, and the three calibration tiles reproduce `amendment-1.json`'s D and bus counts ([`check_real2.txt`](check_real2.txt)).

**Types.** fp32 as computed. fp16: IEEE round-to-nearest-even of the fp32 values, except the forward-pass tiles. int8, as
`make_real2.py`'s docstring gives: `default` is Q130(n)'s (activations per tensor, max-abs; weights per output channel; attention's q and k per tensor);
`per_token`, `p9999`, `p999` are `amend_real.py`'s; `asym` is the TFLite int8 convention for activations (s = (hi − lo) / 255, z = round(−128 −
lo / s), code = clip(round(x / s) + z, −128, 127)), with B the same per-channel int8 as `default`, so a pair differs in A alone. Honest about
the signed format: the kernel multiplies the raw codes, so what the card computes is the true integer product plus z·Σ B per output column,
which a deployed kernel subtracts afterwards.

**Windows.** As Q130(n): the one of 20 seeded aligned windows nearest their median (`window_choice`). The three ReLU products cut in
several formats share one window, the same rows and columns with nested k blocks (fp32's 16 k are the first of fp16's 32, the first of int8's
64), with the distances summed over the formats, so "the same numbers in another format" means what it says. A calibration or forward-pass
tile takes its partner's window. `check_real2.py` checks the nesting and the pairs on the bytes.

## Departures and caveats

1. **The first fp16 forward pass was wrong, and the loss caught it.** It squared in fp16 before averaging. Some |d| reached 256, so d·d
   overflowed to inf, and one inf wipes a token: loss 4.44 nats, median 229 ulps from rounding at layer 6 ([`rebuild-check.txt`](rebuild-check.txt)). The variance is a dot product, so its
   accumulator is now fp32, as every other sum: loss 3.0461. Numbers above are the corrected pass's. No committed tile came from the first one.
2. **The asymmetric scheme differs from the brief's example.** It offered symmetric per-tensor weights with asymmetric activations. Weights here stay
   per output channel, the modern default, so an `asym` tile differs from its partner in A alone and the comparison is about the gate.
3. **The tile list was chosen after looking** at predicted D and the gate across all 57 captured products ([`explore-products.txt`](explore-products.txt),
   [`explore-calibrations.txt`](explore-calibrations.txt)). No card data informed it, and the predictor was not refitted. ResNet-50 was not needed: ResNet-18 gave the range.
4. **The predictor is Q130(n)'s post-hoc fit**, not a mechanism. It prices B flips at 0, which E65 contradicts, and T5's tile leans on that; a miss there is
   a finding. `gpt2_l9_attn_qk` fp32's B column lies 1.2% past E78's maximum (5.704 against 5.637), harmless at β = 0, and no other model column on any tile lies outside E78's
   range (`features_outside_e78_range`). `vit_l11_down` is out of family: nothing in E78 is 64% −0.0.
5. **int8's intervals rest on little.** Gated int8 has no out-of-sample miss to fit on, so that class uses E78's nested-LOO residuals, the one place E78 enters. Ungated int8's ±1.02 W, on four
   tiles, is narrower than Amendment 1's ±1.32 W, and no calibration tile is among the four; if those tiles miss, that is why.
6. **One tile a cell is a draw, and on a conv layer the draw matters**: over 20 windows `resnet18_l2c1`'s gate spans 0.00–0.71 and its predicted D 7.2–24.0 W
   (`window_choice.gated_band`, `D_pred_band_w`). The tile's gate is 0.191 where the layer's is 0.263; `resnet18_l3c1`'s 0.445 where the layer's is 0.530. C3 uses each tile's own g.
7. **The rows are real but the batch is ours**: 16 adjacent patches of one image, 16 tokens of one text, or 16 images. T5 and BERT read a novel, ResNet and VGG NASA's pictures; none of this is a benchmark's data.
8. **The law's L is a full-mantissa random kind.** T5's tiles have bf16-grid weights, so its L is too high for them; at live shares of 0.05–0.13 that is worth a few tenths of a watt, inside the interval.
9. **−0.0 and GELU's implementation:** result 3's share comes from torch's float32 formula; an erfc-form GELU gives tiny negatives. Neither is a zero word.
10. **Rebuilds:** two full builds on arm64 macOS, capture to predictions, gave byte-identical files, and the predictions script gave byte-identical output on x86_64 macOS
    ([`rebuild-check.txt`](rebuild-check.txt)). The capture was not re-run on another machine. On another BLAS or torch build expect the fp32 and fp16 tiles' low-order bits to move, as Q130(n)'s
    did; the committed sha256s are authoritative. Q130(n)'s committed int8 `l6_mlp_down` tile, made on x86_64, did come back byte for byte from this arm64 capture.

## Reproduce

```bash
# on a machine with room: CPython 3.11, numpy==1.26.4 torch==2.5.1 torchvision==0.20.1 transformers==4.46.3
# safetensors==0.4.5 sentencepiece==0.2.0 pillow==11.0.0 protobuf==5.28.3; about 2.5 GB of downloads, a minute of CPU a build
python3 dl_models.py <dl> && python3 dl_images.py <dl>/images
python3 capture_real2.py --dl <dl> --out <cap> --repo <lab repo>
python3 make_real2.py --cap <cap> --dl <dl> --out <dir> --repo <lab repo>
# from the committed files alone, numpy only
uv run --python 3.11 --with numpy==1.26.4 --no-project tools/claims-v3/kinds/real2/make_predictions_real2.py --out <dir> --real2 tools/claims-v3/kinds/real2
uv run --python 3.11 --with numpy==1.26.4 --no-project tools/claims-v3/kinds/real2/check_real2.py
```

## Files

| path | what |
|---|---|
| `predictions-real2.json` | **the freeze**: per tile (a), (a′), (b), (c); the known misses; the gate law; E83's relation; `claims`; `e95_suggested`, `e96_suggested`. `predictions-real2.txt` is its one-line-a-tile print |
| `real2.json` | provenance (models, images, checks, build), `desk_gate_by_format`, per tile its file, sha256, window, quantisation, `make_kinds` statistics, zero statistics, window choice, features |
| `capture.json` | every captured product: what A and B are, their source, their bytes' sha256, zero and low-bit statistics; the forward checks and the fp16 comparison |
| `capture_real2.py`, `make_real2.py`, `make_predictions_real2.py` | the three stages; `dl_models.py`, `dl_images.py`, `nasa_search.py` fetch and check the inputs |
| `check_real2.py`, `check_real2.txt` | desk checks on the committed bytes, the gate recomputed with plain loops; `check_negzero.py`, `check_negzero.txt` where ViT's −0.0 comes from; `rebuild-check.txt` |
| `explore_real2.py`, `explore_calib.py`, `explore-products.txt`, `explore-calibrations.txt` | the survey the tile list was chosen from: all captured products, gate and predicted D over windows, five calibrations on thirteen products (its `asym` rows use per-tensor weights, the brief's example; the tiles use per-channel) |
| `tiles/<type>/<name>.bin` | 2,048 bytes: the A tile then the B tile, 1,024 bytes each, in that type's layout |

| tile | sha256 |
|---|---|
| `tiles/fp32/resnet18_l2c1.bin` | `a27b4f483651824a733fa9ccfca80d221c820173b7806890f1dd5cd5e35014db` |
| `tiles/fp32/resnet18_l3c1.bin` | `6d759159247cf20745b92d8d0bf55f94fd7c3595c2d9d00c7973f0b8164f0ac7` |
| `tiles/fp16/resnet18_l3c1.bin` | `4206d172ad36b81a6d9e3f6f184786d322d3e69f7c0985eca6fb11f28b90ec97` |
| `tiles/int8/resnet18_l3c1.bin` | `27b8c649aab95813ae586537d2cff74fec8cf5ad2f59dd170b06729b95d925fc` |
| `tiles/fp32/vgg16_fc2.bin` | `26a2afc5740e01c31267e29cd253296b76a1384bd2679632c32a9c160056ff6f` |
| `tiles/fp16/vgg16_fc2.bin` | `0a3341897afc614968a11820600dd1760dbf7f9a4d672c0258037f35f329be91` |
| `tiles/int8/vgg16_fc2.bin` | `3b055155a98be6361146f84a1bdc017d2d408a6ad1f8811e74e497c4130e89fd` |
| `tiles/fp32/t5small_l0_down.bin` | `4c9e6d10f05808075953000601be1cf80a338fe2298df0b5cfacc15fc378f5a7` |
| `tiles/fp16/t5small_l0_down.bin` | `7c1496680ccf1d69f640c15fc86daa65d0be4b88672711b5338a2397fdeb09bd` |
| `tiles/fp32/gpt2_l3_mlp_down.bin` | `08bef955e7e835a9d934a07b60c5ad1c50b77e2dae69adf157b8875aa7bc9cb1` |
| `tiles/fp32/gpt2_l9_attn_qk.bin` | `a7a67f4aa8d9835e44ccacca0c9c49345c4fa15e527196651ff5097e44e87d2e` |
| `tiles/fp16/gpt2_l9_attn_qk.bin` | `6cfef807543dba6c3aa26caf37a0a6b72d3fd309bd579d7330742d0c7e4b7b86` |
| `tiles/fp32/bert_l6_up.bin` | `312c34d32261d6519992fb1fff797a31bee0e92c72f95f2f2913bea629783b91` |
| `tiles/fp16/bert_l6_up.bin` | `a8c708293b5c8cd369ccefd8c4374f1a2aee907d971b7f6494731dd674a6aac0` |
| `tiles/fp32/vit_l5_down.bin` | `4f77d357a4d97a7f6e2326e0314dfd0e9343ea13be188489609037d4707105ce` |
| `tiles/fp16/vit_l5_down.bin` | `64985e6c2bd5457c70d050daa0bdcde6a3c1e8f5a48ad9f958c15801f8ea617b` |
| `tiles/fp32/t5small_l0_up.bin` | `845dc5180fb0109a02fdcda2f04381874a1a2af37b1d676737fd4929919de7f7` |
| `tiles/fp32/vit_l11_down.bin` | `af7da866a3db13878e84ccb352d35e006b71578dd0d90af03ef3b7d28dbd4143` |
| `tiles/fp16/gpt2_l6_mlp_down_fp16fwd.bin` | `8d75f3fdee196fe9d4e099927488c1b4d421d8a7275a8926bb788b02ab9a7f87` |
| `tiles/int8/gpt2_l6_down_per_token.bin` | `9f7daf2842262797dc1c9ed41dd882a324c7645eb41377e143a6c02990e60da7` |
| `tiles/int8/gpt2_l6_down_p9999.bin` | `deefd9cab63f5be939c3bb0093205cd977dcc398dc77941d8619339fcbd608f6` |
| `tiles/int8/gpt2_l6_down_p999.bin` | `fda41dd9f32e7d439a9d765cfd5cdf223684b45d05178ce06efef4337be9e799` |
| `tiles/int8/gpt2_l11_down_maxabs.bin` | `0ac8783bbffab8ecf7c4001b5c5a7a4014d955577a708f937865cd6658a9ef4d` |
| `tiles/int8/gpt2_l11_down_p999.bin` | `eea7ce0a6f183100f9fd4781e34e368b6e795b21e4bb601d32075d8c64e3224e` |
| `tiles/int8/vgg16_fc2_asym.bin` | `b3d85b914f99477c98c0b92e7148e3014c01c4155fa7422a791b0ef8fa5275c5` |
| `tiles/int8/t5small_l0_down.bin` (tier 2) | `8e0ede7d4c04cca32b76cb0ebd251d8f3d51396ff60174a07f8ff4a04fb43e21` |
| `tiles/int8/vit_l11_down.bin` (tier 2) | `ddc28d6e9818434ca17d4694aa7abdf8ad7247f7ed572f52714cefc52ddbb65d` |
| `tiles/fp16/gpt2_l6_attn_qk_fp16fwd.bin` (tier 2) | `3da8b91fa51bf64800117d44bdf0d64a31add3a2dd3197c9a455768e5d2dedb0` |
| `tiles/fp32/gpt2_l6_mlp_down_bf16fwd.bin` (tier 2) | `da68af705b310b3599a8d629e9daead0d379309adcdbe0140c343042dc843cf2` |
| `tiles/int8/gpt2_l11_down_asym.bin` (tier 2) | `efd2503511345055f9f876e2e03945858e0d475547de8f3f2eb72a6d2a8c5587` |
