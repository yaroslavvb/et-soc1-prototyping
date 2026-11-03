# Blind pool 6 in the tree, and M8's, M7's and M6's frozen predictions for it on three cards (Q139(x))

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 6**, "a power model across kinds" (with items 7, 13 and 15 folded into pool 6 as tiles). Q138's final critic: **rank 2** (M8, scored on a sixth blind pool on all three cards) and **rank 5** (a card's scale from cheap reads), with ranks 8, 14 and 16 carried by the pool. The goal, in the owner's words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as possible.*

*Tue 3 Nov 2026 (week 45), Q139(x), desk only, on the Intel: no card was opened and nothing was measured. This directory is Q139(b)'s blind pool 6 ([`README.md`](README.md), every file unchanged), copied into the tree at 05:05:27 PST, after M8 was committed and pushed (`122da8b6`, 04:57:59 PST; its registration `f640fb7a`, 04:43:16 PST; [Q139(m)'s README](../../../../docs/reports/data/2026-11-03-q139m-model/README.md)). Added beside it: the bench's counts for its 50 tiles, the frozen predictions of M8, M7 and M6 for the three cards that score the pool, E153 (aifoundry3), E157 (aifoundry1 card 1) and E160 (aifoundry2), and M8's card scale per card from its cheap-read predictor. Nothing was refitted, tuned or patched: every number below comes from Q139(m)'s `predict_blind6.py`, run unchanged at `122da8b6` on the committed `m8.json`, `m7.json` and `m6.json`, and from `fit_m8.py`'s own `loco()` on `m8.json`'s frozen inputs. This commit precedes every claim and launch of E153, E157 and E160; a card lane checks that it does.*

## Results

**What this does to predicting power and heat.** Nothing is scored here. This commit fixes, before any card runs, what each model says each of pool 6's 50 tiles will draw over the same kernel on zeros (D), how far the die will warm over the kinds harness's 4.5 s run, and, on aifoundry2, what clock its own governor will settle at in a 6 s burst and how high the board's highest sample will go. The terms under test are M8's two new ones (the C register's flips for the floats, 6.44 ± 2.05 fJ a flip; a discount on int8 B bytes that flip 7 or 8 bits, -56.8 ± 29.4 fJ a bit), its constants refitted on Q139(u)'s one footing, its aifoundry2 cap (65.20 W) and its new peak rule (P800 + 1.94 W expected, + 2.95 W at 95%), M7's heat law (carried unchanged), and the card scale (M8's measured card-1 term, 0.9616, against what cheap reads predict). **The error before**: M8 out of kind (nested leave one kind out over 767 rows): floats 0.182 W and int8 0.241 W, against M7's form refitted 0.187 / 0.256 W and M7 as frozen 0.198 / 0.237 W (M6 as frozen 0.195 W on the floats); aifoundry2 end to end 7.16 MHz and 1.86 W board over 92 bursts (`m8.json`, `nested-m8.json`). Pool 5's blind error for M7: aifoundry3 0.325 / 0.317 / 0.356 W (fp32 / fp16 / int8), card 1 0.169 / 0.149 / 0.251 W, aifoundry2 6.63 MHz and 1.60 W where the governor acts, heat over 4.5 s 0.13-0.17 °C (E141, E142, E143 `scored.json` / `results.json`). A card nobody has measured: no cheap read predicted a training card's scale to 1% (the 600 MHz voltage, V², missed card 1 by -5.2%). **The error after**, pool 6's blind error by format, card and term, is what E153, E157 and E160 measure, under the critic's rule (M8 minus M6 rms resolved below zero by a paired bootstrap over tiles on both 600 MHz cards; bias inside B1/B2; at least 26 of 30 inside the bands).

| card (scored by) | file | sha256 | tiles predicted | failures |
|---|---|---|---:|---|
| aifoundry3 card 0, 600 MHz pinned (E153) | [`predictions-blind6-aifoundry3.json`](predictions-blind6-aifoundry3.json), [`.md`](predictions-blind6-aifoundry3.md) | `972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f` | 50 of 50 | none |
| aifoundry1 card 1, 600 MHz (E157) | [`predictions-blind6-aifoundry1c1.json`](predictions-blind6-aifoundry1c1.json), [`.md`](predictions-blind6-aifoundry1c1.md) | `267565abe1b06466ea44ed123755c16ad6d091fb20f26fd710853526912c3276` | 50 of 50 | none |
| aifoundry2 card 0 under its own governor, 6 s kspeed bursts (E160) | [`predictions-blind6-aifoundry2.json`](predictions-blind6-aifoundry2.json), [`.md`](predictions-blind6-aifoundry2.md) | `6b9a5e6ee5f3c4761855d8cedc486c546fecc2d855d0e706919c2a21302e3125` | 50 of 50 | none |
| the card scale per card, cheap reads (E153, E157, E160; rank 5) | [`card-scale-blind6.json`](card-scale-blind6.json) | `6b04079139e05d168517779fbc97c6c9a720c69226585ee6c5e67d6857ff9312` | 3 cards; 50 tiles on card 1 | none |

Each predictions file gives, per tile, M8's, M7's and M6's prediction with its 95% band:

- **aifoundry3 and aifoundry1 card 1** (600 MHz): `D_w`, W over the type's own zeros on that card (card 1 through each model's measured card scale), `D_95`; `S_w`, board W over idle (D plus the zeros' mean S on that card, `zeros_S_w`); `dT_win_c`, the die rise over the kinds harness's 4.5 s run, `dT_win_95`. `D600_a3_footing_w` is the model's D on aifoundry3's footing.
- **aifoundry2** (its own governor, a 6 s burst of the kinds harness, E80's harness, the meter's dips kept): `burst_mhz` (the mean clock), `burst_board_w`, `burst_D_w` (board W less zeros' board W in their own burst) and `burst_die_rise_c` (die max less die start), each with a 95% band; for M8 also `P800_w`, `peak_board_w` (the expected highest board sample) and `peak_board_hi95_w` (its 95% upper value, from c at the top of D's band), and `peak_over_82w`. M7 and M6 go through M7's frozen clock term and burst heat law; only M8 predicts the peak.
- Bands, as frozen: power k x sqrt(pool^2 + s^2 x'Cx), **M8 k 2.196 on the floats and 2.835 on int8**, M7 3.179 / 2.483, M6 1.96; heat over 4.5 s k_h 1.95 x the card's pool for M8 and M7 (M8 carries M7's law), 1.96 x its own pool for M6; aifoundry2 M8 ±16.9 MHz and ±3.50 W, M7 and M6 ±21.3 MHz and ±3.37 W, the burst die ±1.41 °C. Each file copies M8's `band_rule` from `m8.json`.

**Every tile, as frozen** (W and °C; H marks Q139(b)'s four hold candidates for E154/E161; the files hold every model on every card):

| tile | prio | H | aifoundry3: M8 D (W) [95%] | M7 D | M6 D | M8 dT (°C) [95%] | card 1: M8 D (W) [95%] | M8 dT (°C) | aifoundry2: M8 MHz [95%] | M8 board W | M8 peak W, expected / 95% | > 82 W |
|---|---|---|---|---:|---:|---|---|---:|---|---:|---|---|
| `fp32.a_onebit_b16_half` | 2 |  | 9.680 [9.25, 10.11] | 9.650 | 9.626 | 1.38 [1.03, 1.74] | 9.308 [8.87, 9.75] | 1.28 | 800.0 [783, 800] | 54.46 | 56.40 / 58.21 | no |
| `fp32.a_onebit_b5_third` | 1 | H | 9.447 [9.02, 9.87] | 9.393 | 9.336 | 1.35 [1.00, 1.71] | 9.084 [8.64, 9.52] | 1.25 | 800.0 [783, 800] | 54.02 | 55.96 / 57.77 | no |
| `fp32.a_zeros_b_complement` | 1 |  | 1.536 [1.09, 1.98] | 1.535 | 1.779 | 0.42 [0.06, 0.77] | 1.477 [1.02, 1.93] | 0.38 | 800.0 [783, 800] | 39.23 | 41.17 / 43.01 | no |
| `fp32.anchor6_randn` | 2 |  | 24.728 [24.30, 25.16] | 24.597 | 24.636 | 3.17 [2.81, 3.52] | 23.778 [23.34, 24.22] | 2.94 | 702.6 [686, 720] | 64.92 | 84.54 / 86.36 | **YES** |
| `fp32.anchor6_zeros` | 2 |  | 0.000 [-0.42, 0.42] | 0.000 | 0.000 | 0.23 [-0.12, 0.59] | 0.000 [-0.43, 0.43] | 0.21 | 800.0 [783, 800] | 36.35 | 38.29 / 40.10 | no |
| `fp32.b_onebit_b12_third` | 1 |  | 9.853 [9.43, 10.28] | 9.823 | 9.796 | 1.40 [1.05, 1.76] | 9.475 [9.04, 9.91] | 1.30 | 800.0 [783, 800] | 54.78 | 56.72 / 58.53 | no |
| `fp32.b_onebit_b20_third` | 1 |  | 13.749 [13.32, 14.18] | 13.737 | 13.645 | 1.86 [1.51, 2.22] | 13.221 [12.78, 13.66] | 1.73 | 798.7 [782, 800] | 61.90 | 64.01 / 65.82 | no |
| `fp32.bf16_wideexp` | 1 |  | 19.420 [18.98, 19.86] | 19.457 | 19.512 | 2.54 [2.18, 2.89] | 18.674 [18.22, 19.13] | 2.36 | 752.0 [735, 769] | 65.20 | 74.61 / 76.46 | no |
| `fp32.c_absorbed` | 2 |  | 19.963 [19.53, 20.40] | 19.893 | 20.012 | 2.60 [2.25, 2.96] | 19.196 [18.75, 19.64] | 2.42 | 746.3 [729, 763] | 65.20 | 75.63 / 77.46 | no |
| `fp32.exp_a_pow2wide_b_randn` | 2 |  | 19.164 [18.72, 19.60] | 19.194 | 19.494 | 2.51 [2.15, 2.86] | 18.428 [17.98, 18.88] | 2.33 | 754.7 [738, 772] | 65.20 | 74.14 / 75.97 | no |
| `fp32.exp_a_walk_fixedmant` | 1 |  | 12.623 [12.19, 13.05] | 12.649 | 12.666 | 1.73 [1.38, 2.08] | 12.138 [11.70, 12.58] | 1.60 | 799.8 [783, 800] | 59.94 | 61.90 / 63.72 | no |
| `fp32.exp_b_alt_shift` | 1 |  | 16.047 [15.61, 16.49] | 16.092 | 16.029 | 2.14 [1.78, 2.49] | 15.431 [14.98, 15.88] | 1.98 | 787.3 [770, 800] | 64.60 | 68.31 / 70.14 | no |
| `fp32.exp_only_narrow2` | 1 |  | 14.991 [14.56, 15.43] | 14.974 | 14.961 | 2.01 [1.66, 2.37] | 14.416 [13.97, 14.86] | 1.87 | 794.5 [778, 800] | 63.66 | 66.33 / 68.16 | no |
| `fp32.negzero_a_b_complement` | 1 |  | 16.670 [16.22, 17.12] | 16.738 | 17.262 | 2.21 [1.86, 2.56] | 16.029 [15.57, 16.49] | 2.05 | 781.5 [765, 798] | 64.90 | 69.47 / 71.33 | no |
| `fp32.real_qwen_dequant_q` | 1 |  | 20.292 [19.86, 20.72] | 20.212 | 20.097 | 2.64 [2.29, 2.99] | 19.513 [19.07, 19.95] | 2.45 | 743.0 [726, 760] | 65.20 | 76.24 / 78.06 | no |
| `fp32.real_qwen_softmax_v` | 2 |  | 24.256 [23.82, 24.69] | 24.122 | 24.080 | 3.11 [2.76, 3.46] | 23.324 [22.88, 23.77] | 2.89 | 706.7 [690, 724] | 65.00 | 83.66 / 85.48 | **YES** |
| `fp32.real_smol_softmax_v_causal` | 1 | H | 13.693 [13.27, 14.12] | 13.625 | 13.548 | 1.86 [1.50, 2.21] | 13.167 [12.73, 13.61] | 1.72 | 798.8 [782, 800] | 61.81 | 63.90 / 65.72 | no |
| `fp32.signexp_invert_b` | 1 |  | 17.076 [16.62, 17.53] | 17.141 | 16.948 | 2.26 [1.91, 2.61] | 16.420 [15.96, 16.88] | 2.10 | 777.4 [760, 794] | 65.03 | 70.23 / 72.09 | no |
| `fp16.a_zeros_b_complement` | 2 |  | 1.520 [1.17, 1.87] | 1.519 | 1.599 | 0.41 [0.10, 0.72] | 1.462 [1.07, 1.86] | 0.37 | 800.0 [783, 800] | 39.11 | 41.05 / 42.72 | no |
| `fp16.anchor6_randn` | 2 |  | 22.075 [21.74, 22.41] | 21.975 | 22.038 | 2.85 [2.54, 3.16] | 21.227 [20.85, 21.61] | 2.65 | 726.5 [710, 743] | 65.18 | 79.49 / 81.12 | no |
| `fp16.anchor6_zeros` | 2 |  | 0.000 [-0.32, 0.32] | 0.000 | 0.000 | 0.23 [-0.08, 0.54] | 0.000 [-0.37, 0.37] | 0.20 | 800.0 [783, 800] | 36.27 | 38.21 / 39.82 | no |
| `fp16.b_onebit_b6_third` | 2 |  | 12.726 [12.40, 13.06] | 12.693 | 12.586 | 1.74 [1.43, 2.05] | 12.238 [11.86, 12.62] | 1.61 | 799.8 [783, 800] | 60.04 | 62.01 / 63.64 | no |
| `fp16.c_absorbed` | 2 |  | 19.863 [19.53, 20.20] | 19.836 | 19.905 | 2.59 [2.28, 2.90] | 19.100 [18.72, 19.48] | 2.40 | 747.8 [731, 765] | 65.20 | 75.36 / 76.99 | no |
| `fp16.e5m2grid_wide` | 1 |  | 17.923 [17.58, 18.26] | 17.937 | 17.969 | 2.36 [2.05, 2.67] | 17.235 [16.85, 17.62] | 2.19 | 768.7 [752, 786] | 65.15 | 71.73 / 73.37 | no |
| `fp16.exp_a_walk_fixedmant` | 2 |  | 12.504 [12.18, 12.83] | 12.504 | 12.524 | 1.72 [1.41, 2.02] | 12.024 [11.65, 12.40] | 1.59 | 799.8 [783, 800] | 59.63 | 61.59 / 63.22 | no |
| `fp16.exp_b_alt_shift` | 1 |  | 15.528 [15.19, 15.86] | 15.534 | 15.399 | 2.07 [1.76, 2.38] | 14.932 [14.55, 15.31] | 1.92 | 791.6 [775, 800] | 64.16 | 67.25 / 68.88 | no |
| `fp16.exp_only_narrow2` | 1 |  | 15.910 [15.57, 16.25] | 15.868 | 15.854 | 2.12 [1.81, 2.43] | 15.299 [14.92, 15.68] | 1.97 | 788.8 [772, 800] | 64.47 | 67.96 / 69.60 | no |
| `fp16.real_qwen_dequant_v` | 2 |  | 21.877 [21.54, 22.21] | 21.786 | 21.848 | 2.83 [2.52, 3.14] | 21.037 [20.66, 21.42] | 2.63 | 728.3 [711, 745] | 65.18 | 79.12 / 80.75 | no |
| `fp16.real_qwen_qk` | 1 |  | 19.011 [18.68, 19.34] | 18.947 | 18.911 | 2.49 [2.18, 2.80] | 18.281 [17.90, 18.66] | 2.31 | 756.8 [740, 774] | 65.20 | 73.76 / 75.39 | no |
| `fp16.real_smol_qk` | 1 |  | 21.564 [21.23, 21.90] | 21.474 | 21.480 | 2.79 [2.48, 3.10] | 20.736 [20.36, 21.11] | 2.59 | 731.2 [714, 748] | 65.19 | 78.54 / 80.17 | no |
| `fp16.real_smol_softmax_v` | 1 |  | 17.551 [17.22, 17.88] | 17.480 | 17.391 | 2.31 [2.00, 2.62] | 16.877 [16.50, 17.25] | 2.15 | 772.8 [756, 790] | 65.11 | 71.03 / 72.66 | no |
| `int8.a_word_zero_one` | 1 |  | 2.857 [2.14, 3.58] | 2.777 | 2.689 | 0.64 [0.24, 1.04] | 2.747 [2.05, 3.45] | 0.58 | 800.0 [783, 800] | 43.00 | 44.94 / 47.30 | no |
| `int8.a_zeros_b_lineflip` | 1 |  | -0.339 [-1.73, 1.05] | 0.049 | 0.505 | 0.26 [-0.14, 0.66] | -0.326 [-1.67, 1.01] | 0.23 | 800.0 [783, 800] | 37.02 | 38.96 / 42.57 | no |
| `int8.anchor6_full` | 2 |  | 7.026 [6.31, 7.74] | 7.014 | 6.975 | 1.14 [0.74, 1.53] | 6.756 [6.06, 7.45] | 1.05 | 800.0 [783, 800] | 50.80 | 52.74 / 55.09 | no |
| `int8.anchor6_zeros` | 2 |  | 0.000 [-0.69, 0.69] | 0.000 | 0.000 | 0.30 [-0.10, 0.70] | 0.000 [-0.67, 0.67] | 0.27 | 800.0 [783, 800] | 37.65 | 39.59 / 41.90 | no |
| `int8.b_line_55_aa` | 2 |  | 6.100 [4.84, 7.36] | 6.586 | 6.846 | 1.02 [0.63, 1.42] | 5.866 [4.65, 7.08] | 0.94 | 800.0 [783, 800] | 49.06 | 51.00 / 54.37 | no |
| `int8.b_line_zero_ff` | 1 | H | 3.388 [2.17, 4.61] | 3.703 | 4.101 | 0.70 [0.30, 1.10] | 3.258 [2.08, 4.44] | 0.64 | 800.0 [783, 800] | 43.99 | 45.93 / 49.23 | no |
| `int8.b_line_zero_full` | 1 |  | 4.237 [3.52, 4.96] | 4.075 | 4.178 | 0.80 [0.41, 1.20] | 4.074 [3.37, 4.78] | 0.74 | 800.0 [783, 800] | 45.58 | 47.52 / 49.88 | no |
| `int8.bflip_bit2_w` | 2 |  | 2.162 [1.40, 2.92] | 2.212 | 2.132 | 0.56 [0.16, 0.96] | 2.079 [1.34, 2.81] | 0.51 | 800.0 [783, 800] | 41.70 | 43.64 / 46.07 | no |
| `int8.bflip_bit5_w` | 2 |  | 2.163 [1.41, 2.92] | 2.166 | 2.126 | 0.56 [0.16, 0.96] | 2.080 [1.35, 2.81] | 0.51 | 800.0 [783, 800] | 41.70 | 43.64 / 46.07 | no |
| `int8.bheld_bit1` | 1 |  | 6.185 [5.38, 6.99] | 6.212 | 6.055 | 1.03 [0.64, 1.43] | 5.947 [5.17, 6.73] | 0.95 | 800.0 [783, 800] | 49.22 | 51.16 / 53.68 | no |
| `int8.bheld_bit4` | 1 |  | 5.855 [5.06, 6.65] | 5.880 | 5.730 | 1.00 [0.60, 1.40] | 5.630 [4.86, 6.40] | 0.92 | 800.0 [783, 800] | 48.61 | 50.55 / 53.04 | no |
| `int8.bheld_bit7` | 1 |  | 5.514 [4.74, 6.29] | 5.545 | 5.398 | 0.96 [0.56, 1.35] | 5.302 [4.55, 6.05] | 0.88 | 800.0 [783, 800] | 47.97 | 49.91 / 52.37 | no |
| `int8.powerlaw_df15_pt` | 2 |  | 2.668 [1.95, 3.39] | 2.647 | 2.626 | 0.62 [0.22, 1.02] | 2.566 [1.87, 3.27] | 0.56 | 800.0 [783, 800] | 42.65 | 44.59 / 46.95 | no |
| `int8.powerlaw_df4_pc` | 1 |  | 6.759 [6.05, 7.47] | 6.745 | 6.750 | 1.10 [0.70, 1.50] | 6.500 [5.81, 7.19] | 1.02 | 800.0 [783, 800] | 50.30 | 52.24 / 54.58 | no |
| `int8.real_qwen_w8a8_down` | 2 |  | 6.146 [5.43, 6.86] | 6.029 | 6.069 | 1.03 [0.63, 1.43] | 5.910 [5.21, 6.61] | 0.95 | 800.0 [783, 800] | 49.15 | 51.09 / 53.44 | no |
| `int8.real_qwen_w8a8_gate` | 1 |  | 6.728 [6.02, 7.44] | 6.687 | 6.691 | 1.10 [0.70, 1.50] | 6.469 [5.78, 7.16] | 1.01 | 800.0 [783, 800] | 50.24 | 52.18 / 54.52 | no |
| `int8.real_qwen_w8a8_v` | 1 | H | 6.694 [5.98, 7.41] | 6.692 | 6.703 | 1.10 [0.70, 1.49] | 6.437 [5.75, 7.13] | 1.01 | 800.0 [783, 800] | 50.17 | 52.11 / 54.46 | no |
| `int8.real_smol_w8a8_down` | 1 |  | 5.437 [4.73, 6.14] | 5.336 | 5.308 | 0.95 [0.55, 1.34] | 5.228 [4.54, 5.92] | 0.87 | 800.0 [783, 800] | 47.82 | 49.76 / 52.10 | no |
| `int8.real_smol_w8a8_q` | 1 |  | 6.545 [5.83, 7.26] | 6.469 | 6.492 | 1.08 [0.68, 1.48] | 6.294 [5.60, 6.99] | 0.99 | 800.0 [783, 800] | 49.90 | 51.84 / 54.18 | no |

**aifoundry2 and section 22's 82 W stop.** M8's 95% upper peak (`peak_board_hi95_w`, the value Q139(m) says the stop should use) exceeds 82 W on **2 of 50 tiles**: `fp32.anchor6_randn` 86.36 W (expected 84.54, P800 82.60; priority 2); `fp32.real_qwen_softmax_v` 85.48 W (expected 83.66, P800 81.72; priority 2). Their expected peak exceeds 82 W on 2 (`fp32.anchor6_randn`, `fp32.real_qwen_softmax_v`); 3 more are within 2 W of it at 95% (`fp16.anchor6_randn` 81.12 W, `fp16.real_qwen_dequant_v` 80.75 W, `fp16.real_smol_qk` 80.17 W). Below the line, the highest 95% upper value is 81.12 W (`fp16.anchor6_randn`). A flagged tile does not run on aifoundry2 as designed: E160 duty-cycles it or drops it, and every registered board stop stays at most 85 W on live samples (section 22). On pool 5, in sample, the same upper value covered 35 of 36 tiles' highest sample and flagged 4 tiles (Q139(m)'s README).

**M8's card scale per card from its cheap-read predictor** (rank 5; [`card-scale-blind6.json`](card-scale-blind6.json), computed by [`card_scale_blind6.py`](card_scale_blind6.py) with `fit_m8.py`'s `loco()` unchanged on `m8.json`'s frozen reads and measured scales; the recomputed table equals `m8.json`'s exactly). s = D on the card over D on aifoundry3 at 600 MHz on the same tiles. For a held-out card, ln s = the mean over the two other cards of [ln s_other + β ln(read / read_other)], β physical (the voltage: 2; the rest: 1) or fitted on the two other cards. No read and form met its 1% rule on all three training cards (2 came within 1% on one card only: the zeros level, physical, on aifoundry1c1's int8, -0.1% and the leakage slope, fitted, on aifoundry2's int8, +0.9%), so M8 applies measured scales (first column); the cheap-read columns are what M8 would say for a card nobody had measured:

| card, format family | scale M8 applies (M7) | measured in training | V600², physical | V600, β fitted | zeros level, physical | zeros level, fitted | idle power, physical | leakage slope, fitted |
|---|---|---|---:|---:|---:|---:|---:|---:|
| aifoundry3, floats | 1.0000 (1.0000) | 1.0000 | 1.0220 (+2.2%) | 0.9822 (-1.8%) | 1.2470 (+24.7%) | 0.9373 (-6.3%) | 0.8655 (-13.4%) | 1.0849 (+8.5%) |
| aifoundry3, int8 | 1.0000 (1.0000) | 1.0000 | 1.0128 (+1.3%) | 0.9583 (-4.2%) | 1.2359 (+23.6%) | 0.9662 (-3.4%) | 0.8578 (-14.2%) | 0.9415 (-5.8%) |
| aifoundry1 card 1, floats | 0.9616 (0.9711) | 0.9600 | 0.9102 (-5.2%) | 0.8780 (-8.5%) | 0.9707 (+1.1%) | 0.9879 (+2.9%) | 1.2733 (+32.6%) | 0.9745 (+1.5%) |
| aifoundry1 card 1, int8 | 0.9616 (0.9735) | 0.9621 | 0.9011 (-6.3%) | 0.7788 (-19.1%) | 0.9610 (-0.1%) | 0.9769 (+1.5%) | 1.2605 (+31.0%) | 0.9516 (-1.1%) |
| aifoundry2, floats | 0.9817 (0.9817) | 0.9784 | 1.0098 (+3.2%) | 0.9932 (+1.5%) | 0.7760 (-20.7%) | 0.9296 (-5.0%) | 0.8524 (-12.9%) | 0.9661 (-1.3%) |
| aifoundry2, int8 | 0.9817 (0.9817) | 0.9589 | 1.0109 (+5.4%) | 0.9935 (+3.6%) | 0.7769 (-19.0%) | 0.9332 (-2.7%) | 0.8533 (-11.0%) | 0.9679 (+0.9%) |

In brackets, each prediction's error against the scale measured in training (frozen in `m8.json`). On aifoundry2, M8's scale is the D scale g of its burst relation (M7's 1/1.01865, kept). The file also holds the idle-power fitted and leakage-slope physical forms, and, per tile on card 1, D600 x each predicted scale (`tiles_aifoundry1c1`, no band: M8 registered none for an unmeasured card). On aifoundry3 the scale is 1 by definition (M8's units); on aifoundry2 it enters the burst relation as g, and a burst computed with another g would be a changed parameter, so aifoundry2's predicted scale is scored as a scale only. What pool 6 measures for the 1% rule: card 1's median D ratio to aifoundry3 on the same tiles (E157 over E153; floats with D >= 5 W, int8 with D >= 1 W, as `m8.json`'s measured scale), and aifoundry2's (c - c_zeros) / D600 from its bursts pinned at 795-800 MHz (E160).

**Where the models disagree most** (D at 600 MHz on aifoundry3 and card 1, burst D on aifoundry2; descriptive, nothing fitted): aifoundry3 fp32: largest |M8 - M7| 0.134 W (`fp32.real_qwen_softmax_v`), |M8 - M6| 0.592 W (`fp32.negzero_a_b_complement`); aifoundry3 fp16: largest |M8 - M7| 0.100 W (`fp16.anchor6_randn`), |M8 - M6| 0.160 W (`fp16.real_smol_softmax_v`); aifoundry3 int8: largest |M8 - M7| 0.486 W (`int8.b_line_55_aa`), |M8 - M6| 0.844 W (`int8.a_zeros_b_lineflip`); aifoundry1c1 fp32: largest |M8 - M7| 0.226 W (`fp32.signexp_invert_b`), |M8 - M6| 0.734 W (`fp32.negzero_a_b_complement`); aifoundry1c1 fp16: largest |M8 - M7| 0.184 W (`fp16.e5m2grid_wide`), |M8 - M6| 0.230 W (`fp16.c_absorbed`); aifoundry1c1 int8: largest |M8 - M7| 0.545 W (`int8.b_line_55_aa`), |M8 - M6| 0.818 W (`int8.a_zeros_b_lineflip`); aifoundry2 fp32: largest |M8 - M7| 0.450 W (`fp32.anchor6_randn`), |M8 - M6| 0.500 W (`fp32.negzero_a_b_complement`); aifoundry2 fp16: largest |M8 - M7| 0.390 W (`fp16.anchor6_randn`), |M8 - M6| 0.390 W (`fp16.anchor6_randn`); aifoundry2 int8: largest |M8 - M7| 0.910 W (`int8.b_line_55_aa`), |M8 - M6| 1.580 W (`int8.a_zeros_b_lineflip`).

**A tile M8 puts below its zeros.** `int8.a_zeros_b_lineflip` (case Z, item 13's zeros' transport; its rule: "A every byte 0x00 (every micro-op gated); B lines alternate all 0x7F and all 0x80: all 512 B bits flip at every line boundary behind the closed gate (int8's zeros' transport)"): M8 -0.339 W on aifoundry3 (95% [-1.73, +1.05]) and -0.326 W on card 1, where M7 says +0.049 and M6 +0.505 W on aifoundry3. M8's near-whole-byte discount (`bsat`, -56.8 fJ a bit, 8,192 such bits an op here) alone contributes -0.90 W; Q139(m)'s README says the term over-corrects whole-line flip-flops. The frozen value stands, and this tile tests that term most directly.

**aifoundry2 (E160): governed against 800 MHz.** M8 puts 19 of the 50 tiles below 795 MHz in a 6 s burst (702.6 to 794.5 MHz; 12 of them priority 1) and 31 at 795-800 MHz, where a burst does not test the clock term. M7's verifier asked E143 to report the two sets apart with the frozen bands unchanged; the same split applies to E160.

## Checks

1. **M8 is committed and unchanged.** `122da8b6` and its registration `f640fb7a` are on `origin/main`. When the predictions ran, other lanes' commits had moved the tree's HEAD on (to `d8badb73`), touching nothing the predictor reads: `git diff 122da8b6` over M8's, M7's, M6's and M5's directories, Q139(u)'s footing and the tools they import was empty (and check 2 below). Its ten files hash the same in the working tree as in the commit, and the five its README lists at the freeze match (`m8.json` `8c23aba2...6abd`, `fit_m8.py` `3764bc4c...bad7`, `predict_blind6.py` `6bc447eb...bbf1`, `nested-m8.json` `f284b540...4905`, `rows-m8.json` `6e3383ef...81d9`). Its self-test, rerun here, passes with output identical to the committed `selftest-predict-blind6.txt` (M7 and M6 through `predict_blind6.py` reproduce Q138(x)'s frozen pool-5 predictions field for field: 360, 360 and 504 fields, 0 differ).
2. **Everything the predictor read is named.** Run under an audit hook (the same run, byte-identical output), it imported 14 modules and read 85 data files in the tree ([`provenance-blind6.json`](provenance-blind6.json): path, sha256, last commit). Every one outside this directory is tracked and identical to `122da8b6`; the 52 inside it are the pool's tiles and manifest and these counts. That closes for pool 6 what Q138(m)'s C9 note found for pool 5 (the files hash their direct inputs only).
3. **The pool is the designer's, byte for byte.** Copied from a snapshot verified first: 81 of 81 files identical; `SHA256SUMS` 80 of 80 OK (its sha256 `8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509`); `MANIFEST` `a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0`, 50 of 50 lines; the manifest `blind6.json` `4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03`, every tile 50 of 50 matching its `sha256.whole`, `a` (first 1,024 B) and `b` (last 1,024 B), 2,048 B each. `make_blind6.py --check`, run before anything was added: "check: 52 built files, 0 problems".
4. **After the additions** the pool's 81 files are still identical (81 of 81; `SHA256SUMS` 80 of 80). `make_blind6.py --check` in the tree then reports "MISMATCH SHA256SUMS"; "check: 52 built files, 1 problems": the designer's check compares `SHA256SUMS` with every file now in the directory, this lane's additions included (the pool verifier's minor fault 2; pool 5's check does the same since Q138(x)). Run on a copy holding the pool's 81 files only, taken from the tree after the additions, it prints "check: 52 built files, 0 problems". Later lanes check the pool with `shasum -c SHA256SUMS`, the `MANIFEST` hash and a count of 81.
5. **The predictions are the frozen model's.** Each file records the sha256 of the frozen files it read, and they are the committed ones (Files, below). Run again into a scratch directory, the predictor writes all six files byte for byte, and so does the traced run. An independent recompute from each tile's recorded features with the frozen constants of `m8.json`, `m7.json` and `m6.json` (D, the card scale, the band, S, the die rise and its band; on aifoundry2 M8's c, P800, peak, 95% peak and the 82 W flag, and every band's half-width; the burst clock is the predictor's own) agrees to the files' rounding: 3850 fields, 0 beyond it. The card-scale script, run again, writes its file byte for byte.
6. **The bench counted every tile cleanly**: 50 rows for the 50 tiles, `check_mismatch` 0 at every launch point (the bench's functional check, C against software at all 256 words).

## The pool's verifier, and what this copy is

Pool 6's independent verifier (04:56 PST) found the pool **holds, with fixes**: one major fault and nine minor. **The major one**: `blind6.json`'s fp16 `c_check` emulates C under PRM 9.4's literal rule (a two-term update dropped unless all four halves are nonzero), which the card does not use (E36; pool 5's [CORRECTIONS.md](../blind5/CORRECTIONS.md) C1), so for `fp16.real_smol_softmax_v` and `fp16.real_qwen_dequant_v` the C it describes, and its `c_op1_sha256`, are not the card's. Its fix changes `blind6.json`, the README and `SHA256SUMS`, and no tile or `MANIFEST` line; for a pool already copied it asks for a dated `CORRECTIONS.md` beside the frozen pool. This copy is the pool as Q139(b) returned it and as the verifier hashed it (the three hashes above), taken at 05:05:27 PST, when its fix pass had changed nothing in the pool. That pass's staged files, read at 05:16, keep every tile, the `MANIFEST` and every field the predictor and the harnesses read (name, file, type, case, priority, anchor, hold flag, sha256) identical, so **these predictions hold for the corrected pool too**; only the manifest hash recorded in each file would differ. At 05:25 the fix pass's draft of those corrections was a dated `CORRECTIONS.md` for this directory, changing no frozen file, as the verifier asked for a pool already copied. A launch's C is checked against Q139(k)'s `tools/claims-v3/ccheck/` reference, not against `blind6.json`'s fp16 `c_op1_sha256`.

**The same rule inside M8.** M8's C-register feature (`c_end`) comes from `make_blind5.py`'s emulation, the same PRM-literal rule, by its frozen definition, in training and here alike; the predictions keep it. As a sensitivity only (post hoc, in this lane's scratch, nothing committed changes), computing that descriptor with every update applied moves M8's D on `fp16.real_qwen_dequant_v` (priority 2) by +0.0074 W (9,920 to 10,948 flips an op); `fp16.real_smol_softmax_v` (priority 1) by +0.0023 W (7,882 to 8,199 flips an op); the other 11 fp16 tiles are unchanged. Both moves are far inside M8's float error (0.18 W).

Two of the verifier's minor faults bear on the card lanes: priority 1 holds 9 real tiles where the critic's rank 8 asks for 10, so a real-tile sub-rule is best registered over all 12 (the 3 priority-2 ones run); and `fp32.a_onebit_b5_third`'s rule text says bit 5 is set in the odd rows where the generator clears it (the bytes are right; the predictions read the bytes).

## The bench's counts

[`counts-blind6.json`](counts-blind6.json) (sha256 `6f321736d1a5edd5e0965c83c1e3154d91807fe0b841ac622f8b3866da847190`): 50 rows for the 50 tiles, keyed `type.name` as the manifest names them, from rtl-sim/fma_toggle_v2's `run_kinds.py` at the three launch points of a 0.5 s launch, with the same build and maps that counted M5's to M8's rows and pools 3-5 (Q133(b)'s build; its seven files hash as when Q138(x) counted pool 5). Run 05:06:06-05:34:20 PST, 6 jobs at nice 20 (this session's background commands run at nice 20, gentler than the brief's nice 10; the script's own `nice -n 10` could not lower it).

| bench file | sha256 |
|---|---|
| `obj_vpu/Vtb` | `9096e64586b561818ae64af9830ccdf1c6f08e0fab123bf0e7807516af6527e5` |
| `accum` | `9e47d24311e70f37868428605bc5f48310dbd5c670b489aea44148994ea4e5a1` |
| `settle_count` | `2a79d1320df29fc76d4c0d25a018059ade3a41ed43f2ea0ff1a9881b01d81363` |
| `maps/unit_float.map` | `1372705868cec52e47bd631db4850d63beaa3f21cc9891160da3941926ad9a51` |
| `maps/unit_int8.map` | `211be19daef07652dec3a160ed4024c58d20c50fc42cd7ffdfb46947fca5068e` |
| `maps/vpu.map` | `d5f925f204bc701e4746e616efe1962ab209d2ec5a91273214eccab0e30502d9` |
| `run_kinds.py` | `fa8112e9ff953f714f3a2161990a581c37617884a44cc6dddfb6bbe5e6133110` |

## Commands, exactly

From the top of the tree unless said. The bench runs in a build of `rtl-sim/fma_toggle_v2` (Q133(b)'s README, section Rerun: `make ... obj_vpu/Vtb accum settle_count`, then `train_maps.py ... --out maps`); `<repo>` is this tree's absolute path. `run_kinds.py` needs no numpy; the predictor and the card-scale script need numpy (here macOS's `/usr/bin/python3` 3.9.6 with numpy 1.26.4, as Q139(m) used).

```
# 1. the pool, from Q139(b)'s scratch, unchanged (through a snapshot verified first)
cp -Rp <Q139(b) pool dir>/. tools/claims-v3/kinds/blind6/
(cd tools/claims-v3/kinds/blind6 && shasum -a 256 -c SHA256SUMS)          # 80 OK
python3 tools/claims-v3/kinds/blind6/make_blind6.py --check               # before the additions: 52 built files, 0 problems
# 2. the bench, in its build dir; EXTRA = for each tile of blind6.json in order, <type>:<name after 'type.'>:<repo>/tools/claims-v3/kinds/blind6/<file>, comma-joined
nice -n 10 python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds <repo>/tools/claims-v3/kinds \
  --out counts-blind6.json --only __none__ --extra-tiles "$EXTRA" --jobs 6 --tmp <tmp dir> --keep-going
cp counts-blind6.json <repo>/tools/claims-v3/kinds/blind6/counts-blind6.json
# 3. the predictions: predict_blind6.py writes predictions-<card>.json/.md; this lane renames them predictions-blind6-<card>.*
for card in aifoundry3 aifoundry1c1 aifoundry2; do
  python3 docs/reports/data/2026-11-03-q139m-model/predict_blind6.py tools/claims-v3/kinds/blind6 $card --counts tools/claims-v3/kinds/blind6/counts-blind6.json
  mv tools/claims-v3/kinds/blind6/predictions-$card.json tools/claims-v3/kinds/blind6/predictions-blind6-$card.json
  mv tools/claims-v3/kinds/blind6/predictions-$card.md tools/claims-v3/kinds/blind6/predictions-blind6-$card.md
done
# 4. M8's card scale per card from its cheap-read predictor (needs step 3's card-1 file)
python3 tools/claims-v3/kinds/blind6/card_scale_blind6.py tools/claims-v3/kinds/blind6 tools/claims-v3/kinds/blind6/card-scale-blind6.json
```

Rerunning steps 3 and 4 on these files reproduces the predictions and the card scale byte for byte.

## Order (PST, Tue 3 Nov 2026)

1. 04:43:16 Q139(m) commits M8's registration (`f640fb7a`); 04:57:59 it commits and pushes M8 (`122da8b6`). Pool 6 is not in the tree.
2. 05:00-05:05 This lane reads the brief, Q138's critic, Q139(m)'s and Q139(b)'s results and the pool's verifier (holds with fixes; its fix pass had started at 04:59), and checks M8: on `origin/main`, its ten files unchanged, the README's freeze list matching.
3. 05:04:13 The pool in Q139(b)'s scratch still hashes as returned (`MANIFEST`, `blind6.json`, `SHA256SUMS`).
4. 05:05:26 A snapshot of it is taken into this lane's scratch and verified: 81 files, `SHA256SUMS` 80 of 80, `MANIFEST` 50 of 50, tiles 50 of 50.
5. 05:05:27 The pool is copied from the snapshot into this directory: 81 of 81 files identical.
6. 05:05:28-05:05:35 `make_blind6.py --check` in the tree, before any addition: 52 built files, 0 problems.
7. 05:06:06 The bench starts on the 50 tiles (150 jobs).
8. 05:06:35-05:06:41 M8's self-test rerun here: PASS, its output identical to the committed `selftest-predict-blind6.txt`.
9. 05:16 The pool's fix pass's staged files read: every tile, the `MANIFEST` and the fields the predictor reads identical to v1.
10. 05:34:20 The bench ends: 50 rows, `check_mismatch` 0 at every point.
11. 05:34:42-05:34:47 The predictions for the three cards, renamed `predictions-blind6-<card>.*`, and the card scale.
12. 05:34:47-05:35:13 The reruns into scratch (byte-identical), the traced runs and the provenance list, the independent recompute, the pool checked again beside the additions, `--check` in the tree and on the pool alone.
13. 05:38 This README and the public-text scan (clean, after one variable in the card-scale script was renamed for the scan; its output byte-identical); the pool checked once more beside the 11 additions.
14. Then: committed and pushed through the lab's commit script, before any E153, E157 or E160 claim. That commit is the gate each card lane checks.

## What this cannot say

- **Nothing here is a measurement or a score.** The predictions are frozen; E153, E157 and E160 measure the tiles and score them by their own registered rules.
- **No cheap read met the card-scale predictor's 1% rule** on all three training cards, so the cheap-read scales are quoted for a card nobody has measured, not used: M8 predicts card 1 with its measured term (0.9616) and aifoundry2 with its burst relation's g (0.9817). The predicted scales use the committed reads frozen in `m8.json` (Q139(s)'s 600 MHz voltages; E141's and E142's idle levels and aifoundry2's B(600) from E136; pool 5's fp32 zeros anchors; Q139(u)'s leakage slopes and E66's for aifoundry2), not pool 6's sessions' own reads; a lane that re-reads them applies the same formula. aifoundry2's measured scale rests on its own s(800) with V² (Q139(m)'s README: at Q139(s)'s board exponent 2.45 it would be about 4% lower).
- **On aifoundry2 the models share one clock form**: M7 and M6 go through M7's frozen relation (its cap 65.58 W), M8 through the same form with its cap refitted to 65.20 W and the same zeros levels and D scale (none of its three registered aifoundry2 terms was kept). Where a burst reaches the effective cap, every model's board power is the cap and the models differ in clock alone. Only M8 predicts the peak, and its 95% value rests on E143's 117 traces of one session.
- **The three zero anchors are byte-identical** (one tile under three type names, as in pool 5), each predicted under its own type; their D is near zero by construction (the counts are taken relative to the zeros' counts).
- **M8's C-register feature follows `make_blind5.py`'s PRM-literal fp16 emulation** (above): consistent with its training rows, not with the card's arithmetic, on the two fp16 tiles with half-zero words (a sensitivity of at most 0.01 W).
- The counts are the public RTL bench's (int8's multiply is behavioural there, and int8 bits per op stay provisional, `../README.md` 1.2).

## Files

| file | what | sha256 |
|---|---|---|
| [`README.md`](README.md), [`MANIFEST`](MANIFEST), [`blind6.json`](blind6.json), [`SHA256SUMS`](SHA256SUMS), [`make_blind6.py`](make_blind6.py), [`fetch_real6.py`](fetch_real6.py), `real/`, `tiles/` | Q139(b)'s pool, unchanged (81 files) | `MANIFEST` `a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0`; `blind6.json` `4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03`; `SHA256SUMS` `8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509` |
| [`counts-blind6.json`](counts-blind6.json) | the bench's counts for the 50 tiles | `6f321736d1a5edd5e0965c83c1e3154d91807fe0b841ac622f8b3866da847190` |
| [`predictions-blind6-aifoundry3.json`](predictions-blind6-aifoundry3.json), [`.md`](predictions-blind6-aifoundry3.md) | M8, M7, M6 on aifoundry3 | `972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f`, `cf3b57db3b5312226b44aab0e8dba283b1c74de8901a8ef49d0ea0167ebb5226` |
| [`predictions-blind6-aifoundry1c1.json`](predictions-blind6-aifoundry1c1.json), [`.md`](predictions-blind6-aifoundry1c1.md) | M8, M7, M6 on aifoundry1c1 | `267565abe1b06466ea44ed123755c16ad6d091fb20f26fd710853526912c3276`, `ab3dc0295caf4c39dac15721c7a3ad9592c404490968e5c36ae65b71da7160eb` |
| [`predictions-blind6-aifoundry2.json`](predictions-blind6-aifoundry2.json), [`.md`](predictions-blind6-aifoundry2.md) | M8, M7, M6 on aifoundry2 | `6b9a5e6ee5f3c4761855d8cedc486c546fecc2d855d0e706919c2a21302e3125`, `d1c4e0d8686ef176af6b212f1fa0d8d0b955817dd061434ea7a200bee272c260` |
| [`card-scale-blind6.json`](card-scale-blind6.json), [`card_scale_blind6.py`](card_scale_blind6.py) | M8's card scale per card from its cheap-read predictor, and the script that computes it | `6b04079139e05d168517779fbc97c6c9a720c69226585ee6c5e67d6857ff9312`, `4a9da8a083cf6b555acfb1f0f2192407e1fcbac2f5ca6ee9a270547cd753cba6` |
| [`provenance-blind6.json`](provenance-blind6.json) | every module and data file the predictor read, with sha256 and last commit | `d50f77e963847cd44ac3a7ac1c0d6a4a9532a4fd2b08b3ccb7fbe2f49bbf012d` |

Every predictions file records the hashes of what it read: `m8.json` `8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd`, `m7.json` `bfeea822b87e0a1f8c315809192faf0a437b72bcadd1459c027cd857c8b3d8b2`, `m6.json` `87c17e086ee36699d7bb96609c02c471b5ba6b7bcdc20ead576d26f89e136e82`, the manifest `4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03`, the counts `6f321736d1a5edd5e0965c83c1e3154d91807fe0b841ac622f8b3866da847190`, `predict_blind6.py` `6bc447eb5c5d88de6f084265908191cbbe372ce3a46b669babbce50a374fbbf1`, `fit_m8.py` `3764bc4c345412ae71d66f18f114d0fe395d8db90988d699988513a590b6bad7`; [`provenance-blind6.json`](provenance-blind6.json) names the rest.

*Commits: M6 `6a713a9f` (Q137(m)), M7 `3a210f2b` (Q138(m)), M8, `predict_blind6.py` and its self-test `122da8b6` (Q139(m), registered at `f640fb7a`); this directory, the counts, the predictions and the card scale: the commit that adds this README (Q139(x)).*
