# E143: blind pool 5 under aifoundry2's own governor - M7 predicts the burst clock of 36 new kinds to 6.6 MHz rms where the governor acts and the board power at that clock to 1.6 W, inside every registered line

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 6, "a power model across kinds"**, the first of its next steps after Q137 (a refit "tested on a fifth pool written by someone else, on a second card"). E141 (aifoundry3) and E142 (aifoundry1 card 1) score the same pool at 600 MHz; E143 is the one card where the governor sets the clock, so it is the only blind test of M7's clock-and-voltage term. Q138's goal, in the owner's words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as possible.*

*Mon 2 Nov 2026 (week 45), Q138, aifoundry2 card 0 under its own governor. Pre-registered in `38cd9099` ([`tools/claims-v3/e143/E143.md`](../../../../tools/claims-v3/e143/E143.md): the frozen numbers, the rules, the stops, a self-test, a toy-card dry run of the whole queue and the device-command audit), committed at 20:54:09 PST and pushed before the claim (20:55:03) and the first launch (20:56). Every number it scores is Q138(x)'s, committed in `dac39d97` at 20:24 PST (`git merge-base --is-ancestor dac39d97 38cd9099` holds), from M7 (`3a210f2b`, 19:21 PST, before pool 5 entered the tree); nothing was fitted or refitted. `ettelem config` read 65 W / 65 °C, low_power, 600 MHz, 519 mV at the queue's start (20:55:36) and end (21:23:39). Nothing was set on the card. 28.1 card-minutes (20:55:36-21:23:39), every command a read.*

*Corrected after verification (a dated note, Mon 2 Nov 2026, about 22:30 PST). An independent verifier re-derived every registered number
and verdict from the raw telemetry, and all of them stand. It found seven faults, six in the text and one in the result's table cells,
and none of them changes a number, rule or verdict; the fix pass found one more of C3's kind (H1's printed reference). They are corrected in [§ Corrections after verification](#corrections-after-verification-mon-2-nov-2026) at the end. The text
between is as first committed; where it disagrees with those notes, the notes hold. The main one is C1: what M7 leaves on this card is
not an offset. The board error rises with the power M7 predicts, and the zeros level is −1.20 W (−0.80 W is the mean of all 17 pinned
tiles). So the next terms are a zeros level, a cap term and a D scale that depends on the format, all found post hoc and all to be scored
blind. Where the governor acts, and for the heat, the blind scores are consistent with the reference, not better than it (C3). And the
pool is 30 new kinds and 6 anchors (C5).*

## The answer

**M7's clock-and-voltage term holds on 36 kinds it never saw.** On the 19 tiles M7 put below 795 MHz, where aifoundry2's governor acts, the measured burst clock (three passes each) came within **6.63 MHz rms** of the frozen prediction, against 7.59 MHz on the reference rows the rules drew from; all 36 tiles fell inside the frozen ±21.3 MHz band, and the 17 tiles predicted at 800 MHz stayed there (1.01 MHz rms). **The board power at that clock** came within **1.60 W rms** on the governed tiles and **1.18 W** on the pinned ones (35 of 36 inside ±3.37 W), and **the die's rise** over a burst within **0.58 °C** (36 of 36 inside ±1.41 °C). Every registered rule passes, and the drift check against E80's and E83's own tiles passes (−5 to −8 MHz, −1.1 to +0.7 W). M7, M6 and M5 cannot be told apart on this card: they share M7's clock term and heat law and differ only through their D, by at most 0.3 MHz and 0.09 W of rms here.

**The registered rules** (`results.json` › `score.rules`, `replicate`):

| rule | set | n | measured | reference line (2.5% – 97.5%) or coverage line | verdict |
|---|---|---:|---|---|---|
| **E143-F1** | burst clock, governed | 19 | rms 6.63 MHz (mean error -4.96) | 4.66 – 10.23 MHz (reference rms 7.59) | **PASS** |
| **E143-F2** | burst clock, pinned | 17 | rms 1.01 MHz (mean error -0.15) | 0.36 – 15.47 MHz (reference rms 8.87) | **PASS** |
| **E143-F3** | burst clock, all: inside ±21.3 MHz | 36 | 36 of 36 inside | at least 31 | **PASS** |
| **E143-W1** | board W, governed | 19 | rms 1.60 W (mean error 1.17) | 1.41 – 2.43 W (reference rms 1.95) | **PASS** |
| **E143-W2** | board W, pinned | 17 | rms 1.18 W (mean error -0.80) | 1.25 – 2.44 W (reference rms 1.83) | **PASS (better than the reference says)** |
| **E143-W3** | board W, all: inside ±3.37 W | 36 | 35 of 36 inside | at least 31 | **PASS** |
| **E143-H1** | die rise, all | 36 | rms 0.58 °C (mean error -0.10) | 0.52 – 0.84 °C (reference rms 0.69) | **PASS** |
| **E143-H3** | die rise, all: inside ±1.41 °C | 36 | 36 of 36 inside | at least 31 | **PASS** |
| **E143-R0** | E80's replicate tiles | 3 | fp32-randn 705.3 MHz (-8.0), 67.93 W (-1.05); fp16-randn 720.1 MHz (-7.6), 67.33 W (+0.74); int8-full 794.7 MHz (-5.3), 49.47 W (-0.33) | within 25 MHz and 3.37 W of E80's and E83's cells | **PASS** |

**Before and after** (rms of measured − predicted, M7; before = the reference rows the rules drew from, after = E143, blind):

| set | n | clock: reference (before) → E143 blind (after) | board W: before → after | die rise: before → after |
|---|---:|---|---|---|
| governed (M7 < 795 MHz) | 19 | 7.59 → **6.63** MHz | 1.94 → **1.60** W | 0.68 → **0.46** °C |
| pinned (M7 795–800 MHz) | 17 | 8.87 → **1.01** MHz | 1.83 → **1.18** W | 0.68 → **0.70** °C |
| all 36 | 36 | 8.50 → **4.87** MHz | 1.86 → **1.42** W | 0.68 → **0.58** °C |

**What this does to predicting power and heat.** The term tested is aifoundry2's clock-and-voltage term (E136's relation P(f) = B(f) + c·s(f) with s(f) = (V_f/0.517 V)²·f/600, c from M7's D, E83's dither about the effective cap W* = 65.58 W), with M7's burst heat law (0.140 °C per board W over a 21.5 W idle). **Before**, its error was known only in sample to the cap: the reference rows, split by the group M7 predicts, 7.59 MHz and 1.94 W rms governed, 8.87 MHz and 1.83 W pinned, 8.50 MHz and 1.86 W over all 56 kinds bursts; heat 0.68 °C leave-one-kind-out (Q138(m)'s measured split, 13.9 MHz and 2.35 W where the governor acts, is the same rows cut by the outcome). **After**, blind, on a pool written by a designer who never saw the model: **governed 6.63 MHz and 1.60 W, pinned 1.01 MHz and 1.18 W, all 36 tiles 4.87 MHz and 1.42 W; heat 0.58 °C** (0.45 °C when the heat law is given the measured board power). So the quoted error of a burst's clock and power on this card can stand at the reference's size (about 7 MHz and 2 W where the governor acts); the frozen bands held on 36, 35 and 36 of 36 tiles. **What it does not fix:** the governed tiles read the board **1.17 W high on average** (the cap itself: 62.6-69.2 W measured where M7 puts 64.0-65.6 W) and the pinned ones **0.80 W low** (the zeros anchors 35.2-36.3 W against 36.3-37.7), the same two signs Q138(m)'s verification found on the reference bursts; and the burst D (a tile's board W over its zeros') reads 2.3 W high on the governed tiles because both errors add there. A cap and a zeros level refitted per card would remove most of it; neither is changed here.

**M7, M6 and M5 on the same tiles** (rms; the paired difference's 95% interval over tiles; reported, never a verdict):

| set | n | clock M7 / M6 / M5 (MHz) | M7 − M6 | M7 − M5 | board M7 / M6 / M5 (W) | M7 − M6 | M7 − M5 | burst D M7 / M6 / M5 (W) |
|---|---:|---|---|---|---|---|---|---|
| governed | 19 | 6.63 / 6.57 / 6.60 | [-0.162, 0.287] | [-0.508, 0.468] | 1.60 / 1.60 / 1.57 | [-0.011, 0.002] | [-0.0, 0.089] | 2.57 / 2.57 / 2.56 |
| pinned | 17 | 1.01 / 1.00 / 1.00 | [-0.017, 0.036] | [-0.032, 0.127] | 1.18 / 1.17 / 1.26 | [-0.069, 0.084] | [-0.176, 0.007] | 1.04 / 1.01 / 1.15 |
| all | 36 | 4.87 / 4.82 / 4.84 | [-0.118, 0.206] | [-0.356, 0.332] | 1.42 / 1.42 / 1.43 | [-0.029, 0.034] | [-0.062, 0.036] | 2.06 / 2.06 / 2.08 |
| priority1 | 24 | 5.38 / 5.36 / 5.47 | [-0.188, 0.23] | [-0.56, 0.301] | 1.37 / 1.36 / 1.39 | [-0.039, 0.055] | [-0.093, 0.061] | 2.00 / 1.98 / 2.03 |
| fp32 | 14 | 6.68 / 6.76 / 6.69 | [-0.333, 0.155] | [-0.683, 0.588] | 1.61 / 1.62 / 1.57 | [-0.018, 0.002] | [-0.001, 0.136] | 2.52 / 2.55 / 2.50 |
| fp16 | 11 | 4.37 / 4.05 / 4.29 | [0.135, 0.489] | [-0.056, 0.265] | 1.20 / 1.18 / 1.25 | [-0.003, 0.088] | [-0.18, 0.007] | 2.25 / 2.21 / 2.33 |
| int8 | 11 | 1.23 / 1.23 / 1.23 | [0.0, 0.0] | [0.0, 0.0] | 1.36 / 1.36 / 1.41 | [-0.111, 0.077] | [-0.148, 0.029] | 0.85 / 0.82 / 0.85 |
| measured_governed | 19 | 6.63 / 6.57 / 6.60 | [-0.162, 0.287] | [-0.508, 0.468] | 1.60 / 1.60 / 1.57 | [-0.011, 0.002] | [-0.0, 0.089] | 2.57 / 2.57 / 2.56 |
| measured_pinned | 17 | 1.01 / 1.00 / 1.00 | [-0.017, 0.036] | [-0.032, 0.127] | 1.18 / 1.17 / 1.26 | [-0.069, 0.084] | [-0.176, 0.007] | 1.04 / 1.01 / 1.15 |

The heat law on the measured board W (the rise less 0.140 °C/W × (measured W − 21.5 W)): rms 0.453 °C, mean -0.135 °C over 36 tiles.

## Every tile

*Mean over the tile's three passes; the clock's three passes in brackets; M7's frozen value and 95% band beside each; ✗ marks a value outside M7's band. Governed: M7 predicts the burst below 795 MHz.*

| tile | group | prio | passes | clock MHz (runs) | M7 MHz [95%] | board W | M7 W [95%] | rise °C | M7 rise [95%] | burst D W | M7 D |
|---|---|---:|---:|---|---|---:|---|---:|---|---:|---:|
| `fp16.exp_only` | governed | 2 | 3 | **782.2** (783, 783, 780) | 786.4 [765, 800] | **65.43** | 65.04 [61.7, 68.4] | **6.67** | 6.10 [4.69, 7.50] | 30.27 | 28.78 |
| `fp16.pair_cancel_asign` | governed | 1 | 3 | **780.5** (780, 782, 780) | 782.6 [761, 800] | **66.00** | 65.25 [61.9, 68.6] | **6.00** | 6.13 [4.72, 7.53] | 30.84 | 28.98 |
| `fp16.real_pythia_softmax_v` | governed | 1 | 3 | **778.5** (778, 780, 778) | 777.2 [756, 798] | **66.06** | 65.41 [62.0, 68.8] | **6.33** | 6.15 [4.74, 7.56] | 30.90 | 29.15 |
| `fp16.real_pythia_qk` | governed | 1 | 3 | **731.0** (725, 736, 732) | 737.9 [717, 759] | **67.12** | 65.58 [62.2, 69.0] | **6.33** | 6.17 [4.77, 7.58] | 31.96 | 29.31 |
| `fp16.sparse24_straddled` | governed | 1 | 3 | **726.5** (725, 724, 730) | 732.3 [711, 754] | **66.94** | 65.57 [62.2, 68.9] | **6.67** | 6.17 [4.77, 7.58] | 31.78 | 29.31 |
| `fp16.pair_nearcancel` | governed | 1 | 3 | **724.8** (722, 728, 724) | 731.3 [710, 753] | **67.53** | 65.57 [62.2, 68.9] | **6.33** | 6.17 [4.77, 7.58] | 32.37 | 29.30 |
| `fp16.anchor_randn` | governed | 2 | 3 | **731.4** (751, 720, 723) | 730.6 [709, 752] | **67.22** | 65.57 [62.2, 68.9] | **7.33** | 6.17 [4.77, 7.58] | 32.06 | 29.30 |
| `fp16.real_pythia_ln2_up` | governed | 1 | 3 | **720.8** (722, 720, 720) | 728.7 [707, 750] | **66.93** | 65.57 [62.2, 68.9] | **6.67** | 6.17 [4.77, 7.58] | 31.77 | 29.30 |
| `fp32.wideexp48_bgate_alt` | governed | 1 | 3 | **781.9** (754, 796, 796) | 794.9 [774, 800] | **62.62** | 63.96 [60.6, 67.3] | **5.67** | 5.95 [4.54, 7.35] | 27.45 | 27.60 |
| `fp32.b_exp_busy_a_const` | governed | 2 | 3 | **791.3** (792, 792, 790) | 792.3 [771, 800] | **65.06** | 64.45 [61.1, 67.8] | **6.00** | 6.02 [4.61, 7.42] | 29.89 | 28.10 |
| `fp32.exp_only_both` | governed | 1 | 3 | **791.8** (800, 788, 788) | 790.9 [770, 800] | **64.64** | 64.64 [61.3, 68.0] | **6.33** | 6.04 [4.64, 7.45] | 29.48 | 28.29 |
| `fp32.gray_stream` | governed | 1 | 3 | **784.6** (788, 784, 782) | 783.6 [762, 800] | **65.84** | 65.20 [61.8, 68.6] | **6.00** | 6.12 [4.71, 7.53] | 30.68 | 28.85 |
| `fp32.e4m3grid_gelu_w` | governed | 1 | 3 | **779.2** (778, 780, 780) | 783.0 [762, 800] | **66.19** | 65.23 [61.9, 68.6] | **6.00** | 6.12 [4.72, 7.53] | 31.03 | 28.88 |
| `fp32.real_pythia_ln1_q` | governed | 1 | 3 | **724.1** (732, 720, 720) | 728.3 [707, 750] | **66.66** | 65.56 [62.2, 68.9] | **6.33** | 6.17 [4.76, 7.58] | 31.49 | 29.21 |
| `fp32.real_pythia_gelu_down` | governed | 1 | 3 | **715.5** (712, 720, 714) | 726.4 [705, 748] | **66.82** | 65.56 [62.2, 68.9] | **6.33** | 6.17 [4.76, 7.58] | 31.66 | 29.21 |
| `fp32.sorted_k` | governed | 1 | 3 | **707.3** (706, 708, 708) | 719.8 [698, 741] | **65.88** | 65.53 [62.2, 68.9] | **6.67** | 6.17 [4.76, 7.57] | 30.72 | 29.18 |
| `fp32.anchor_randn` | governed | 2 | 3 | **699.3** (700, 706, 692) | 707.0 [686, 728] | **67.74** | 65.39 [62.0, 68.8] | **7.00** | 6.15 [4.74, 7.55] | 32.57 | 29.04 |
| `fp32.lowrank2_w` | governed | 2 | 3 | **698.0** (700, 694, 700) | 706.9 [686, 728] | **68.26** | 65.39 [62.0, 68.8] | **6.67** | 6.15 [4.74, 7.55] | 33.09 | 29.04 |
| `fp32.wideexp48_dense` | governed | 1 | 3 | **693.8** (692, 692, 698) | 696.9 [676, 718] | **69.15** ✗ | 65.31 [61.9, 68.7] | **6.67** | 6.14 [4.73, 7.54] | 33.99 | 28.96 |
| `fp16.anchor_zeros` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **35.16** | 36.27 [32.9, 39.6] | **1.67** | 2.07 [0.66, 3.47] | 0.00 | 0.00 |
| `fp16.sparse24_aligned` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 799.8 [778, 800] | **61.08** | 60.16 [56.8, 63.5] | **5.33** | 5.41 [4.01, 6.82] | 25.92 | 23.89 |
| `fp16.wideexp_bgate_alt` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 799.4 [778, 800] | **61.49** | 61.36 [58.0, 64.7] | **6.00** | 5.58 [4.18, 6.99] | 26.33 | 25.10 |
| `fp32.anchor_zeros` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **35.17** | 36.35 [33.0, 39.7] | **1.67** | 2.08 [0.67, 3.49] | 0.00 | 0.00 |
| `fp32.block_sparse_k4` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 799.8 [778, 800] | **60.02** | 60.24 [56.9, 63.6] | **5.00** | 5.43 [4.02, 6.83] | 24.85 | 23.89 |
| `fp32.wideexp48_bgate_kblk` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 799.5 [778, 800] | **61.24** | 61.22 [57.9, 64.6] | **5.67** | 5.56 [4.16, 6.97] | 26.07 | 24.87 |
| `int8.a_word_flipflop` | pinned | 1 | 3 | **795.9** (800, 788, 800) | 800.0 [779, 800] | **42.23** | 44.24 [40.9, 47.6] | **2.00** | 3.18 [1.78, 4.59] | 5.90 | 6.59 |
| `int8.anchor_full` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **50.48** | 50.74 [47.4, 54.1] | **3.67** | 4.10 [2.69, 5.50] | 14.15 | 13.09 |
| `int8.anchor_zeros` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **36.33** | 37.65 [34.3, 41.0] | **1.33** | 2.26 [0.86, 3.67] | 0.00 | 0.00 |
| `int8.b_line_flipflop_nogate` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **48.69** | 49.52 [46.1, 52.9] | **3.00** | 3.92 [2.52, 5.33] | 12.36 | 11.87 |
| `int8.b_line_zero_one` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **43.41** | 45.06 [41.7, 48.4] | **2.00** | 3.30 [1.89, 4.71] | 7.08 | 7.40 |
| `int8.block_sparse_a` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **44.64** | 45.73 [42.4, 49.1] | **3.00** | 3.39 [1.99, 4.80] | 8.31 | 8.07 |
| `int8.gray_a` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **44.00** | 45.82 [42.5, 49.2] | **2.67** | 3.41 [2.00, 4.81] | 7.67 | 8.17 |
| `int8.powerlaw_w` | pinned | 2 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **47.39** | 49.58 [46.2, 53.0] | **3.00** | 3.93 [2.53, 5.34] | 11.05 | 11.92 |
| `int8.real_pythia_w8a8_down` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **49.56** | 49.23 [45.9, 52.6] | **3.67** | 3.88 [2.48, 5.29] | 13.22 | 11.58 |
| `int8.real_pythia_w8a8_up` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **49.05** | 49.14 [45.8, 52.5] | **3.33** | 3.87 [2.47, 5.28] | 12.72 | 11.49 |
| `int8.sorted_k` | pinned | 1 | 3 | **800.0** (800, 800, 800) | 800.0 [779, 800] | **47.61** | 48.90 [45.5, 52.3] | **3.00** | 3.84 [2.43, 5.24] | 11.28 | 11.25 |

**Each pass scored alone** (reported):

| pass | E143-F1 | E143-F2 | E143-F3 | E143-W1 | E143-W2 | E143-W3 | E143-H1 | E143-H3 |
|---|---|---|---|---|---|---|---|---|
| 1 | 12.76 FAIL | 0.20 PASS | 35 PASS | 2.03 PASS | 1.56 PASS | 34 PASS | 0.79 PASS | 35 PASS |
| 2 | 6.19 PASS | 2.97 PASS | 36 PASS | 1.63 PASS | 1.26 PASS | 36 PASS | 0.63 PASS | 36 PASS |
| 3 | 6.97 PASS | 0.20 PASS | 36 PASS | 1.81 PASS | 1.01 PASS | 35 PASS | 0.66 PASS | 36 PASS |

## Registered against what happened

| registered | what happened |
|---|---|
| smoke: the rest reading, one 2 s launch of each type's zeros anchor, cycles per op within 10% of 546 / 546 / 318, the config 65 W / 65 °C | passed at 20:56:28 PST; rest reading 21.87 W board, die 46.0 °C (`posthoc.txt` (1)) |
| two stop-path tests on live samples before the session | both passed (below) |
| block BURST: 3 passes × (36 pool tiles + 3 replicates), 117 bursts, cap 38 card-minutes | all 117 ran and all 117 counted (every launch passed its check of C); session `s1` exit 0 "done", 27.1 card-minutes; nothing refused by the admission rule, nothing cut by the cap |
| the rules F1-F3, W1-W3, H1, H3, R0 | all PASS (W2 "better than the reference says") |
| reported: M6 and M5, the burst D, the heat law on the measured W, per pass, the kernel's clock | in `results.json` › `score.reported`, `per_pass`; `posthoc.txt` |

**One pass alone.** Pass 1 alone fails F1 (12.76 MHz rms): `fp32.wideexp48_bgate_alt` ran its first pass at 754.2 MHz and 58.2 W with no power-down event and its other two at 795.8 MHz (the bistable behaviour four of the reference's cells showed), and `fp16.anchor_randn` ran pass 1 at 751.0 MHz against 720-723 in the others. Passes 2 and 3 pass F1 alone (6.19, 6.97 MHz). A tile's three passes spread by a median 2.2 MHz and 0.84 W (largest 41.6 MHz and 6.71 W, that tile; `posthoc.txt` (4)), so the pass, not the sample, is the unit, as registered.

**The sampled clock against the kernel's own.** The registered clock is the telemetry's sampled clock, the quantity M7 was fitted on. The kernel's own clock (its cycles over its wall time from 1.5 s on) reads 12-18 MHz lower on the governed tiles and about 1 MHz lower on the pinned ones (`posthoc.txt` (3): mean −7.0 MHz over 39 cells): the 100 ms sampler sees the governor's steps between 600, 700 and 800 MHz, and the kernel's count includes the time it spends in them. A model of the kernel's speed should use the kernel's clock; nothing registered reads it.

## The stops, and their test on live samples

E136's registered stops, under the keys `run_hpl.py`'s watcher reads (`abs_stop_c` 80 °C on one sample, `board_cap_w` 93 W on three in a row), with E146's two tests before the session (`aifoundry2/queue.jsonl` › `stoptest_detail`): **the board stop**, lowered to 30 W, **tripped 62 ms after the third live sampler line over 30 W, while the launch ran, and the launch ended 209 ms later** (exit 4, "safety:board 47.0 W > 30 W on 3 samples"); **the die stop**, lowered to 30 °C, **tripped 65 ms after the first live line, before any launch** (exit 4, "safety:die 69 C >= 30 C"). Neither registered stop fired in the session.

## Device commands sent

*Q136's rule ("take more care for writing commands"), kept in Q138: the classified list is [`E143.md`](../../../../tools/claims-v3/e143/E143.md) "Device commands sent", frozen in `38cd9099`, from et-platform `836a4ab` (aifoundry2's BL2 0.22.0), checked by Q136(w)'s `dmcmd_audit.py` before the claim ([`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e143/logs/dmcmd-audit.txt): 19 send sites, every one READ, GO; one reviewed exception, the residency query `run_e119.py` rewrites to raw states 1-3, which this `ettelem` refuses before it opens the device). **E143 sent no WRITE.** From the session's records (`posthoc.txt` (1)): 16,679 sampler samples (each `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`: all READ; 11 PMIC voltage-register reads each, the owner's allowed read-only PMIC voltage reads of 2 November 2026); an `ettelem config` (three RAM getters, the ASIC voltage and PLL reads) after each of the 121 recorded runs (the smoke's 4 and the session's 117; the stop tests end on their stop before a run is recorded), at the sessions' starts (four) and ends (two: the stop tests end on their stop) and in the queue's two snapshots; `ettelem sptrace` (an MMIO copy, nothing sent to the SP) after each run; no statistics reset, no firmware-revisions query, no residency read, no set. `sparsity_host` (E80's binary, sha256 checked before the session) opens the ops node only: the kernel load, the DMA of the tiles and C and the launches, no management command.*

## Safety

The session's highest board reading was **87.95 W**, in `fp32.wideexp48_dense`'s third pass (`results.json` › `peaks`); its three passes held 85-88 W for 1.6-1.8 s (16-18 samples) each before the governor stepped down, with a first-second median of 86.0-86.2 W. Nine runs touched 85 W, all fp32 random-like tiles (`wideexp48_dense`, `lowrank2_w`, `anchor_randn`). That is 5 W under the 93 W stop, and inside what this card has run before without incident (E105 96.25 W, E101 90.07 W from a cool start), but it is **1.7-3.6 W over the tile's frozen admission estimate** (84.34 W) and its first-second median is 2.1-2.3 W over the highest first-second median of any kinds burst on this card before tonight (83.93 W, E83's `fp32/randn_small`): the estimate from M7's D at aifoundry3's footing reads the high-power random-like kinds low here, as E105 found for its high-power cells (3.2-8.4 W). E80's own fp32 random tile read 81.9-83.6 W in its first second tonight, as in E80 and E83 (82.5-83.1 W), so the card had not moved. The die's mean peaked at 63 °C; the hottest sensor read 69 °C throughout, the SP's running maximum carried from before the session (E146's note). Nothing came near a PMIC over-power or over-temperature reset. No other user was logged in: E111's rule decided before every launch process, 493 times, and counted no other user (`aifoundry2/idle_logins.jsonl`, counts only).

## Departures and notes

- **No departure from the registration.** No amendment was written; every run, rule and reading is as frozen in `38cd9099`.
- **The harness is E80's, not E140's.** As registered (E143.md, What runs): M7's aifoundry2 term was fitted on E80's and E83's 6 s kinds bursts and Q138(x)'s file says its predictions are for that shape, so E143 ran E80's chain; E140's share is the blind scoring's form and the tile check.
- **The rules split by the group M7 predicts**, so the reference rows were split the same way (17 governed, 39 pinned); Q138(m)'s split by the clock measured (21 and 35) is quoted where it is used.
- **The day's one post**, message `1566837317765963987`, was rewritten twice with `EXPECT_TEXT` under the discord lock: the claim at 20:55:03 PST added `using aifoundry2 for 1 h, until ~21:55 PST` beside the aifoundry3 and aifoundry1 card 1 clauses (the first attempt refused with exit 7 because another lane had rewritten the post; re-read and rebuilt); the release at 21:24:29 PST dropped it, the other two clauses kept word for word (again after one exit 7 and a re-read).

## What E143 says about the page and the model

- **For the kinds table, on aifoundry2 under its own governor:** what kind of number a matmul multiplies sets the clock its governor settles at, and the model predicts that clock from the bytes: random-like fp32 694-724 MHz, random-like fp16 721-731 MHz, the other floats (gated, sparse, exponent-only, grid-valued, Gray-coded, the softmax outputs) 778-800 MHz, every int8 tile 796-800 MHz (`results.json` › `score.reported.tiles`).
- **Section 11 item 6:** the clock-and-voltage term now has a blind score. With E141's and E142's 600 MHz scores it says whether M7's whole chain, from a tile's bytes to watts, clock and degrees, holds on new kinds.
- **The model's next term on this card** is not the clock: it is the cap's and the zeros' levels (+1.2 W and −0.8 W), which bias the board power and double in the burst D.

## Files

| file | what |
|---|---|
| [`README.md`](README.md) | this page |
| [`results.json`](results.json), [`reduce.txt`](reduce.txt) | the registered reduction (`tools/claims-v3/e143/reduce_e143.py` on `aifoundry2/s1`): every rule, every reported set, every tile and run |
| [`tables.md`](tables.md), [`tables_e143.py`](tables_e143.py) | this page's tables, printed from `results.json` |
| [`posthoc.txt`](posthoc.txt), [`posthoc.json`](posthoc.json), [`posthoc_e143.py`](posthoc_e143.py) | post hoc, never a verdict: card time and command counts, the stop-path records, the kernel's clock, the passes' spread, the config |
| `aifoundry2/` | the queue's records (`queue.jsonl`, `status.json`, the snapshots and config reads at its start and end, the box's 5 s history for 40 min before), and the four sessions (`smoke`, `stoptest-board`, `stoptest-die`, `s1`): `runs.jsonl`, `launches.jsonl.gz`, the sampler's `tel/*.jsonl.gz`, the trace ring, the queries |
| `logs/` | the queue's stdout and the script that started it |

To reproduce from the tree's root: `python3 tools/claims-v3/e143/reduce_e143.py docs/reports/data/2026-11-02-e143-blind5-aifoundry2/aifoundry2/s1 --out results.json > reduce.txt`, then `python3 docs/reports/data/2026-11-02-e143-blind5-aifoundry2/tables_e143.py > tables.md` and `posthoc_e143.py > posthoc.txt`.

## Corrections after verification (Mon 2 Nov 2026)

*A dated note, written at about 22:30 PST on the Intel. Desk only: no card, no device command, nothing re-run. An independent verifier
re-derived F1–F3, W1–W3, H1, H3 and R0 from the raw telemetry with its own code (per-run differences from `results.json` at most
0.049 MHz, 0.005 W and 0 °C). It also reran Q138(x)'s predictor, which reproduced the frozen predictions byte for byte, and it confirmed
that every command sent was a read. The numbers below come from [`posthoc_corrections_e143.py`](posthoc_corrections_e143.py), which
writes [`posthoc-corrections.json`](posthoc-corrections.json) and prints [`posthoc-corrections.txt`](posthoc-corrections.txt). They are
post hoc and never a verdict, and every interval is a percentile bootstrap over tiles (20,000 draws). The text above is as first committed
in `f8783f05`. `results.json`, `reduce.txt`, `posthoc.txt` and the registration (`tools/claims-v3/e143/`, `38cd9099`) are unchanged.
`tables_e143.py` now prints two reference values correctly, so two cells of `tables.md` change (C3).*

- **C1 (major; "What this does to predicting power and heat" and What E143 says): what M7 leaves on this card is not an offset.** The
  text says the governed tiles read 1.17 W high and the pinned 0.80 W low, and that a cap and a zeros level refitted per card "would remove
  most of it". Its last bullet calls the next term "the cap's and the zeros' levels (+1.2 W and −0.8 W)". Both are corrected
  (`posthoc-corrections.json` › `3_board_error_offset_or_scale`):
  - **The board error rises with the power M7 predicts**: 0.107 W per predicted W [0.081, 0.141] over the 36 tiles; 0.110 [0.066, 0.166]
    over the 14 pinned tiles that are not zeros, where no cap acts; 0.214 [0.022, 0.367] inside int8's 10.
  - **The zeros level is −1.20 W**: the three zeros anchors read −1.11 (fp16), −1.18 (fp32) and −1.32 W (int8). −0.80 W is the mean of
    all 17 pinned tiles. The four pinned floats that are not zeros (gated or sparse, 60.0–61.5 W) read +0.21 W, the ten pinned int8
    tiles −1.09 W and the 19 governed tiles +1.17 W.
  - **Inside the governed tiles the error rises too.** The 11 random-like ones (M7 below 760 MHz) read +1.79 W [1.29, 2.34] and the 8
    lightly governed +0.33 W [−0.20, 0.71]. Against each tile's frozen unthrottled estimate (`predictions-e143.json` › `admission` ›
    `fixed_p800_w`, 64.6–84.3 W) the slope is 0.138 W per W [0.075, 0.188], so the cap term is not one level either. One candidate, not
    tested here: the burst window opens 1.5 s after the first launch, and the hottest tile, `fp32.wideexp48_dense`, held 85–88 W for
    1.6–1.8 s in each pass before the governor stepped down (§ Safety).
  - **Where no cap acts, the burst D reads high by a share.** It reads +1.35 W on the four gated or sparse pinned floats (measured D
    over M7's, through zero: 1.055) and +0.23 W on the ten int8 tiles (1.031). The governed tiles' +2.33 W is where the cap's error and
    the zeros' add, as the text says.
  - **In sample, on these same tiles**, a cap level and a zeros level take the board's rms from 1.42 to 1.03 W, but the pinned tiles
    that are not zeros only from 1.18 to 1.05 W. A D gain per kind of format as well (floats 1.058, int8 1.020) takes the pinned tiles
    to 0.65 W and all 36 to 0.91 W.
  - **So the next aifoundry2 terms** are a zeros level (about −1.2 W), a cap term (about +1.2 W on average, rising with the tile's
    overshoot of the cap) and a D scale that depends on the format (floats 1.055–1.058, int8 1.020–1.031 by the two estimates above). All three were found post hoc
    on E143's own tiles, and each must be scored blind on a new pool or session before it is quoted.
- **C2 (the same paragraph): where the governor acts, the clock reads about 5 MHz low.** "What it does not fix" leaves out the governed
  clock's bias: −4.96 MHz [−6.97, −3.01], with 15 of the 19 tiles below their prediction. It is −6.68 MHz [−8.71, −4.52] on the 11
  random-like tiles and −2.61 MHz on the 8 lightly governed (`4_clock_bias_and_drift`). That is about the size of the card's drift
  since E80 and E83 on identical tiles, which R0 measured tonight. E80's fp32 randn tile ran at 705.3 MHz against E80's and E83's mean
  of 713.3 (−8.0), and its fp16 randn tile at 720.1 against 727.7 (−7.6); all six of their passes read low. The pool's fresh fp32 randn
  anchor read 7.7 MHz below M7. (R0's int8 −5.3 MHz is one pass at 784 MHz, not a drift.) R0 passed its 25 MHz bar, and as registered
  it "qualifies the verdicts above": F1 passes with a bias the size of the drift inside it. So a burst clock quoted for this card needs
  an anchor in the same session, or a drift allowance of about −5 to −8 MHz (kinds page section 11 item 8, the drift between sessions).
- **C3 (The answer, the rules table, Before and after, and What this does): the blind scores carry intervals. Where the governor acts,
  and for the heat, they are consistent with the reference, not better than it; the pinned scores reflect what the pool holds.** With
  95% intervals over tiles (`1_blind_rms_intervals`):

  | rule | blind rms [95%] | in-sample reference | reading |
  |---|---|---|---|
  | F1, governed clock | 6.63 [4.77, 8.27] MHz | 7.59 | inside: consistent |
  | F2, pinned clock | 1.01 [0.08, 1.73] MHz | 8.87; 0.61 without its 4 large-error cells | the pool's composition |
  | W1, governed board | 1.60 [1.11, 2.08] W | 1.94 | inside: consistent |
  | W2, pinned board | 1.18 [0.87, 1.46] W | 1.83; 1.50 without those cells | below the reference, as W2's verdict says |
  | H1, die rise | 0.585 [0.46, 0.70] °C | 0.68 | inside: consistent |

  The pinned clock's drop from 8.87 to 1.01 MHz does not come from a better model. Four of the reference's 39 pinned cells, which M7 put
  at 800 MHz, read 21–39 MHz lower: E80's int8 neg_ones and fp32 nn_like, and E83's int8 wsparse90 and int8 sorted. Without them the
  reference reads 0.61 MHz, and pool 5's pinned tiles held none like them (the largest pinned error is −4.1 MHz, `int8.a_word_flipflop`'s
  one pass at 788 MHz). So the line "pinned 8.87 → 1.01 MHz" reflects what the pool holds. W2 is the one score below its reference
  (1.18 W against 1.83, or 1.50 without the four cells), as its registered verdict says. Read Before and after, and the "before" and
  "after" of What this does, as the text's own conclusion puts it: the quoted error "can stand at the reference's size". On the 30 new
  kinds alone (`2_new_kinds_only`; C5) the scores are much the same: governed 6.75 MHz [4.76, 8.52] and 1.54 W [0.98, 2.09], pinned
  1.15 MHz and 1.22 W, die rise 0.544 °C [0.40, 0.68]. **The rules table prints W1's reference rms as 1.95 and H1's as 0.69.** They are
  1.94 (1.9447) and 0.68 (0.6845), as Before and after has them. `results.json` stores them rounded to three places (1.945, 0.685), and
  `tables_e143.py` rounded those again. It now prints the frozen reference's own values, and in `tables.md` those two cells change and
  nothing else.
- **C4 (Registered against what happened, and Departures): no launch's C was checked.** "All 117 counted (every launch passed its check
  of C)" is not so, and E143.md's smoke and counting rule (lines 81 and 105) and `queue_e143.py`'s step 5 say the same. For a file tile
  the host checks no arithmetic: `rawValues` is true for any `--values` but `small` (`workloads/sparsity/host/main.cpp:589`), so the
  result is `unchecked` (`:614`). All 1,983 kernel launches of the session and all 19 of the smoke read `unchecked`, with `ok` true and
  no tensor error (`5_check_of_C`), as in E80 (4,148 and 21). So "counted" means that every launch completed, every hart wrote its result
  record and no tensor error was raised (`ok`, `:615`, with `summarize`'s `bad`), which is what `reduce_e143.py`'s `launch_ok ==
  launch_n` tests. **This is a departure**, recorded after the data: the registered smoke's "check of C" could not run, so "No departure
  from the registration" is corrected to this one. No rule or score depends on C.
- **C5 (the title, The answer and What E143 says): 30 new kinds and 6 anchors.** "36 kinds it never saw" overstates it. Six of the 36
  tiles are anchors (`6_anchors`). The three zeros tiles are byte-identical to the zeros tiles of E80, E83 and M7's reference rows
  (sha256 `e5a00aa9…`, as `tools/claims-v3/kinds/tiles/<format>/zeros.bin`). The fp32 and fp16 randn anchors and the int8 full anchor
  are fresh tiles of kinds M7 was fitted on. So the pool is 30 new kinds and 6 anchors. And "the other floats (gated, sparse, …)
  778–800 MHz" is wrong for one sparse float. `fp16.sparse24_straddled` is a 2:4 tile whose zeros straddle the fp16 pairs, so no update
  is gated (pool 5's [CORRECTIONS](../../../../tools/claims-v3/kinds/blind5/CORRECTIONS.md) C1). It ran at 726.5 MHz (725, 724, 730),
  with the random-like ones. Read: the gated and block-sparse floats, and the 2:4 tile aligned to the pairs, stayed at 778–800 MHz.
- **C6 (E143.md's first line): the registration did not precede every card's run of the pool.** E143.md says it was registered "before
  any card has run a tile of the pool". E142 had begun the pool on aifoundry1 card 1 at 20:52:47 PST (`fp32.gray_stream`), 82 s before
  `38cd9099` was committed at 20:54:09, and 57 of E142's records, of 6 pool tiles, started before the commit (`7_registration_vs_e142`).
  Nothing flowed. E143's numbers are Q138(x)'s, frozen in `dac39d97` at 20:24 PST, before any card ran the pool. And the E143 lane read
  no E141 or E142 file: its 163 tool calls name them only in its own prose (checked from the lane's record on 2 Nov). The registration
  did precede E143's own claim and every launch of E143, as it says.
- **C7 (the kinds table): the cells.** The 36 tiles' burst clock, burst board W, burst D and die rise on aifoundry2 under its own
  governor are cells of the kinds table. All 141 of them (D is 0 by definition for the 3 zeros tiles) are in `posthoc-corrections.json` ›
  `8_table_cells`, each with its passes' spread and its source key in `results.json`.

**What the corrections do to predicting power and heat.** Nothing is refitted, and every registered verdict stands. Where the governor
acts, the blind clock (6.63 [4.77, 8.27] MHz) and board (1.60 [1.11, 2.08] W) scores, and the heat (0.585 [0.46, 0.70] °C), are
consistent with the in-sample reference (7.59 MHz, 1.94 W, 0.68 °C). So M7's clock-and-voltage term holds blind at the size it was
quoted, and no better. What changes is the model's next term on this card. It is not two levels: it is a zeros level (−1.20 W), a cap
term that rises with the tile's overshoot (+1.17 W on average) and a D scale that depends on the format (floats 1.055–1.058), plus a drift
allowance for the clock (about −5 to −8 MHz) or an anchor in the same session. All of these are post hoc, to be scored blind.
