# Blind pool 7 in the tree, M9's, M8's, M7's and M6's frozen predictions for it on three cards, and rank 4's paired-anchor rule (Q140(x))

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 6**, "a power model across kinds". Q139's final critic: **rank 1** (M9, a power model more accurate than M6 on new kinds at 600 MHz, scored on a seventh blind pool), **rank 4** (a card nobody has measured: the paired-anchor scale, registered here), **rank 9** (real tensors beyond pool 6, carried by the pool) and the aifoundry2 half of **rank 2** (Q140(l)'s session terms, scored blind by E165). The goal, in the owner's words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as possible.*

*Wed 4 Nov 2026 (week 45), Q140(x), desk only, on the Intel: no card was opened, no device command was sent and nothing was measured. This directory is Q140(b)'s blind pool 7 as its fix pass left it after verification ([`README.md`](README.md), every one of its 92 files unchanged), copied into the tree at 02:50:39 PST, after both of M9's parts were committed and pushed: Q140(m)'s 600 MHz part (`1f244140`, 01:12:04 PST; its registration `8dfafae3`, 00:45:51 PST; [README](../../../../docs/reports/data/2026-11-04-q140m-m9/README.md)) and Q140(l)'s aifoundry2 part (`5b98bd5c`, 01:04:31 PST; its registration `245caffe`, 00:43:45 PST; [README](../../../../docs/reports/data/2026-11-04-q140l-a2-session-terms/README.md)). Both lanes' corrections after verification (Q140(m) through `e95c3f89`, 02:39:36 PST; Q140(l) `5c98c0c5`, 01:58:09 PST) changed no frozen file. Added beside the pool: the bench's counts for its 61 tiles; the frozen predictions of M9, M8, M7 and M6 for the three cards that score it, E163 (aifoundry3), E164 (aifoundry1 card 1) and E165 (aifoundry2); the tiles left out on aifoundry2 by the 82 W stop; and rank 4's paired-anchor rule with its scorer. Nothing was refitted, tuned or patched: every prediction comes from Q140(m)'s `predict_blind7.py`, run unchanged on the committed `m9.json`, `m8.json`, `m7.json` and `m6.json`, and on aifoundry2 through Q140(l)'s committed `predict_m9_a2.py` and `m9_a2.json`. This commit precedes every claim and launch of E163, E164 and E165; a card lane checks that it does.*

*Independence (the pool's README, Independence): `int8.bheld_fd` was designed and built after M9's freeze commit, by Q140(b)'s fix pass, which never read M9, its commit or its data; it replaced `int8.bheld_7f`, E103's training kind. Every other tile was final before M9 was frozen. M9's and Q140(l)'s lanes never read pool 7.*

## Results

**What this does to predicting power and heat.** Nothing is scored here. This commit fixes, before any card runs, what each model says each of pool 7's 61 tiles will draw over the same kernel on zeros (D) at 600 MHz on aifoundry3 and card 1, how far the die will warm over the kinds harness's 4.5 s run, and on aifoundry2 what clock its own governor will settle at in a 6 s burst, the board power there, and how high the board's highest sample will go. **The terms under test** are M9's: for int8, a radix-4 Booth partial-product count with B recoded (`bpp_r4`, +2.205 fJ a flip) beside M8's near-whole-byte discount at half size (`bsat`, -29.3 fJ a bit); for the floats the bench's exponent stage (`xstage`, +0.648 fJ a count) beside M8's C-register term (`c_end`, +6.186 fJ a flip); M9's recalibrated bands (k 1.996 floats, 1.864 int8); M8's card term, kept (card 1 0.9616); M7's heat law, carried; and on aifoundry2 Q140(l)'s three session terms (the cap's plateau, 2.52 W over an effective cap of 64.60 W; the session's zeros level, beta 0.648; the die at a burst's start, 0.395 W/C from 54.38 C) with s(f) at n = 2, on M9's D, and M8's peak rule unchanged for the 82 W stop. Pool 7 aims at every miss pool 6 named (single high B bits on new base words, exponent-heavy fp32, whole-line and near-whole-byte int8, int8 with B held), with 12 kinds aimed at none of them, 10 real tiles at priority 1, and two random anchors per format for rank 4.

**The error before.** Out of kind, not blind (Q140(m), nested leave one kind out, every model's form on the same folds): int8 over every committed row 0.251 / 0.256 / 0.261 W (M6's / M7's / M8's forms) against M9's 0.177 W; floats 0.194-0.198 against 0.193 W. Pool 6's blind error, as registered: M8 / M7 / M6 0.286 / 0.252 / 0.243 W on aifoundry3 and 0.323 / 0.314 / 0.283 W on card 1 over 30 new kinds (E153, E157). aifoundry2, held out over four sessions with the terms chosen on the same folds: governed clock 6.25 -> 5.00 MHz, governed board 1.62 -> 0.89 W, pinned board 1.52 -> 0.75 W rms (M7 as frozen -> M9's part; 5.1-6.9 MHz, 0.89-0.93 W and 0.88-0.92 W with the selection nested). The 4.5 s heat: 0.13 C rms on pool 6's int8 kinds, unchanged by M9. The card scale: no cheap read lands within 1% held out; post hoc, pool 6's random anchors gave card 1's float scale to -0.15% and int8's to -1.04% of the pool's median. **The error after** is what E163, E164 and E165 measure on these frozen predictions, under the critic's rank-1 rule (M9 - M6 resolved below zero by a paired bootstrap over tiles on both 600 MHz cards; M9 no worse than M6 on the unaimed subset; bias inside B1/B2; at least 26 of 30 inside) and rank 4's rule below. Q140(m)'s honest forecast: int8 better than M6, floats level with it.

| card (scored by) | file | sha256 | tiles predicted | failures |
|---|---|---|---:|---|
| aifoundry3 card 0, 600 MHz pinned (E163) | [`predictions-blind7-aifoundry3.json`](predictions-blind7-aifoundry3.json), [`.md`](predictions-blind7-aifoundry3.md) | `303dc5b94b35dbd772a9d405934406b4f3fa23551efeba63d85e064839b3d750` | 61 of 61 | none |
| aifoundry1 card 1, 600 MHz (E164) | [`predictions-blind7-aifoundry1c1.json`](predictions-blind7-aifoundry1c1.json), [`.md`](predictions-blind7-aifoundry1c1.md) | `22fe64be1b648f1aac222490c2548e5c4f920932c93ff470f5bb34ab9d9b27c0` | 61 of 61 | none |
| aifoundry2 card 0 under its own governor, 6 s bursts (E165) | [`predictions-blind7-aifoundry2.json`](predictions-blind7-aifoundry2.json), [`.md`](predictions-blind7-aifoundry2.md) | `e2c467c4a60d6409fb9139e8b109ad5f5e758cc1747367984e164ce397c57c01` | 61 of 61 | none |
| aifoundry2: M9's and M8's D at 600 MHz per tile, the input of any aifoundry2 relation | [`a2-inputs-aifoundry2.json`](a2-inputs-aifoundry2.json) | `ff4f4eaa49dfdcc5aeb59c86ad8225889d737f5d41eb02908e0dc8c1545c3933` | 61 of 61 | none |
| aifoundry2: the tiles the 82 W stop leaves out | [`admission-aifoundry2-82w.json`](admission-aifoundry2-82w.json), by [`admission_aifoundry2.py`](admission_aifoundry2.py) | `c330806ae93b86ac83e835f50b66398688a002071c817cf77e0d4e0a11caa384` | 61 | none |
| rank 4's paired-anchor rule (E163 with E164) | [`RANK4-RULE.md`](RANK4-RULE.md), [`rank4_rule.json`](rank4_rule.json), [`score_rank4.py`](score_rank4.py), [`selftest-rank4.txt`](selftest-rank4.txt) | `4b9ccaf006fff9bc92041bf470fe8520e7443f790c02dd1ba3e1ee62293f2507` (the rule) | registered | none |

Each predictions file gives, per tile, M9's, M8's, M7's and M6's prediction with its 95% band:

- **aifoundry3 and aifoundry1 card 1** (600 MHz): `D_w`, W over the type's own zeros on that card (card 1 through each model's card scale), `D_95`; `S_w`, board W over idle (D plus the zeros' mean S on that card, `zeros_S_w`); `dT_win_c`, the die rise over the kinds harness's 4.5 s run, `dT_win_95`. `D600_a3_footing_w` is the model's D on aifoundry3's footing; `features` holds every term's value.
- **aifoundry2** (its own governor, a 6 s burst of the kinds harness, E80's harness, the meter's dips kept): `burst_mhz`, `burst_board_w`, `burst_D_w` and `burst_die_rise_c`, each with a 95% band. **M9's primary is its `a2_q140l` block** (`a2_part.primary` = `a2_q140l`): Q140(l)'s `burst()` on M9's D and half-band, with no session read yet, so it takes `m9_a2.json`'s fallback zeros offset (-1.51 to -1.54 W per format) and the reference die start (54.38 C), and gives the sensitivities per W of the session's anchor offset and per C of die start. M9's other aifoundry2 fields are M9's D through M8's frozen relation, kept beside it. M8 goes through its own frozen relation; M7 and M6 through M7's. M9 and M8 give `P800_w`, `peak_board_w` (the expected highest board sample) and `peak_board_hi95_w` (its 95% upper value), with `peak_over_82w`.
- Bands, as frozen: power k x sqrt(pool^2 + s^2 x'Cx), **M9 k 1.996 on the floats and 1.864 on int8**, M8 2.196 / 2.835, M7 3.179 / 2.483, M6 1.96; heat over 4.5 s M7's law for M9, M8 and M7 (k_h x the card's pool), 1.96 x its own pool for M6; aifoundry2, M9's part: ±9.65 MHz and ±1.85 W governed, ±15.35 MHz and ±1.26 W pinned (by the predicted group: governed below 795 MHz); M8 ±16.9 MHz and ±3.50 W; M7 and M6 ±21.3 MHz and ±3.37 W.

**Every tile, as frozen** (W and C; H marks the pool's hold candidates; case is the pool's class: S single high B bits, E exponent-heavy fp32, L whole-line and near-whole-byte int8, H int8 with B held, U aimed at none, R real, 0 the anchors; the files hold every model on every card):

| tile | prio | case | aifoundry3: M9 D (W) [95%] | M8 D | M7 D | M6 D | M9 dT (C) [95%] | card 1: M9 D (W) [95%] | aifoundry2: M9 MHz [95%] | M9 board W | M9 peak W, expected / 95% | M8 MHz / board W / 95% peak | left out (82 W) |
|---|---|---|---|---:|---:|---:|---|---|---|---:|---|---|---|
| `fp32.anchor7_randn_a` | 2 | 0 | 24.702 [24.30, 25.11] | 24.709 | 24.578 | 24.638 | 3.16 [2.81, 3.52] | 23.754 [23.33, 24.18] | 705.3 [696, 715] | 66.90 | 84.49 / 86.27 | 702.7 / 64.93 / 86.33 | **YES** (M9_a2_q140l, M9_m8_relation, M8) |
| `fp32.anchor7_randn_b` | 2 | 0 | 24.613 [24.21, 25.02] | 24.620 | 24.490 | 24.543 | 3.15 [2.80, 3.51] | 23.668 [23.24, 24.09] | 706.0 [696, 716] | 66.92 | 84.33 / 86.10 | 703.5 / 64.94 / 86.16 | **YES** (M9_a2_q140l, M9_m8_relation, M8) |
| `fp32.anchor7_zeros` | 2 | 0 | 0.000 [-0.40, 0.40] | 0.000 | 0.000 | 0.000 | 0.23 [-0.12, 0.59] | 0.000 [-0.42, 0.42] | 800.0 [785, 800] | 35.36 | 38.29 / 40.05 | 800.0 / 36.35 / 40.10 | no |
| `fp32.b_onebit_b20_full` | 1 | S | 12.219 [11.81, 12.63] | 12.282 | 12.232 | 12.154 | 1.68 [1.33, 2.04] | 11.750 [11.32, 12.18] | 799.9 [785, 800] | 58.24 | 61.15 / 62.93 | 799.9 / 59.31 / 63.08 | no |
| `fp32.b_onebit_b20_one` | 1 | S | 13.177 [12.77, 13.58] | 13.187 | 13.173 | 13.112 | 1.80 [1.44, 2.15] | 12.671 [12.24, 13.10] | 799.6 [784, 800] | 60.09 | 62.94 / 64.71 | 799.4 / 60.95 / 64.77 | no |
| `fp32.b_onebit_b20_pi` | 1 | S | 12.093 [11.67, 12.51] | 12.188 | 12.166 | 12.074 | 1.67 [1.31, 2.02] | 11.628 [11.19, 12.07] | 800.0 [785, 800] | 58.00 | 60.91 / 62.71 | 799.9 / 59.14 / 62.90 | no |
| `fp32.b_onebit_b20_seventh` | 1 | S | 11.975 [11.56, 12.39] | 12.069 | 12.046 | 11.953 | 1.65 [1.30, 2.01] | 11.515 [11.08, 11.95] | 800.0 [785, 800] | 57.78 | 60.69 / 62.48 | 799.9 / 58.92 / 62.67 | no |
| `fp32.b_onebit_b20_third_a1p5` | 2 | S | 13.217 [12.79, 13.64] | 13.333 | 13.315 | 13.193 | 1.80 [1.45, 2.15] | 12.710 [12.26, 13.16] | 799.6 [784, 800] | 60.17 | 63.01 / 64.83 | 799.3 / 61.20 / 65.04 | no |
| `fp32.b_onebit_b22_third` | 1 | S | 12.914 [12.50, 13.33] | 12.977 | 12.962 | 12.895 | 1.77 [1.41, 2.12] | 12.418 [11.99, 12.85] | 799.8 [784, 800] | 59.58 | 62.45 / 64.23 | 799.6 / 60.57 / 64.38 | no |
| `fp32.dropout30_both` | 1 | U | 14.699 [14.30, 15.10] | 14.714 | 14.648 | 14.721 | 1.98 [1.62, 2.33] | 14.135 [13.71, 14.56] | 796.7 [781, 800] | 63.10 | 65.78 / 67.55 | 795.8 / 63.32 / 67.62 | no |
| `fp32.exp_a_gray_walk` | 1 | E | 9.261 [8.86, 9.66] | 9.219 | 9.185 | 9.182 | 1.33 [0.98, 1.69] | 8.905 [8.48, 9.33] | 800.0 [785, 800] | 52.69 | 55.61 / 57.38 | 800.0 / 53.59 / 57.35 | no |
| `fp32.exp_b_alt_b26` | 1 | E | 9.810 [9.40, 10.22] | 9.697 | 9.687 | 9.664 | 1.40 [1.04, 1.75] | 9.434 [9.00, 9.87] | 800.0 [785, 800] | 53.72 | 56.64 / 58.42 | 800.0 / 54.49 / 58.25 | no |
| `fp32.exp_b_alt_lsb` | 1 | E | 9.695 [9.29, 10.10] | 9.600 | 9.604 | 9.568 | 1.38 [1.03, 1.74] | 9.323 [8.89, 9.75] | 800.0 [785, 800] | 53.50 | 56.43 / 58.20 | 800.0 / 54.31 / 58.06 | no |
| `fp32.exp_b_alt_nib` | 1 | E | 15.877 [15.47, 16.29] | 15.759 | 15.807 | 15.706 | 2.12 [1.76, 2.47] | 15.267 [14.84, 15.70] | 790.3 [781, 800] | 65.16 | 67.99 / 69.76 | 789.6 / 64.39 / 69.60 | no |
| `fp32.exp_only_pos12` | 1 | E | 14.370 [13.95, 14.79] | 14.224 | 14.278 | 14.229 | 1.94 [1.58, 2.29] | 13.819 [13.38, 14.25] | 797.8 [782, 800] | 62.45 | 65.17 / 66.96 | 797.6 / 62.64 / 66.75 | no |
| `fp32.laplace_both` | 1 | U | 24.698 [24.29, 25.10] | 24.693 | 24.575 | 24.609 | 3.16 [2.81, 3.52] | 23.749 [23.32, 24.18] | 705.3 [696, 715] | 66.90 | 84.48 / 86.26 | 702.9 / 64.93 / 86.29 | **YES** (M9_a2_q140l, M9_m8_relation, M8) |
| `fp32.mant2_spreadexp` | 1 | E | 17.109 [16.70, 17.52] | 17.007 | 17.046 | 17.047 | 2.26 [1.91, 2.62] | 16.452 [16.02, 16.88] | 779.3 [770, 789] | 66.51 | 70.29 / 72.07 | 778.1 / 65.01 / 71.94 | no |
| `fp32.randn_a24k` | 1 | U | 13.342 [12.94, 13.74] | 13.362 | 13.299 | 13.288 | 1.82 [1.46, 2.17] | 12.830 [12.41, 13.25] | 799.5 [784, 800] | 60.41 | 63.25 / 65.01 | 799.2 / 61.25 / 65.09 | no |
| `fp32.real_qwen_l3_softmax_v_sink` | 1 | R | 23.947 [23.54, 24.36] | 23.947 | 23.879 | 23.870 | 3.07 [2.72, 3.43] | 23.027 [22.60, 23.46] | 711.8 [702, 721] | 67.00 | 83.08 / 84.86 | 709.4 / 65.05 / 84.91 | **YES** (M9_a2_q140l, M9_m8_relation, M8) |
| `fp32.real_s360_l1_qk` | 2 | R | 24.575 [24.17, 24.98] | 24.573 | 24.450 | 24.471 | 3.15 [2.79, 3.50] | 23.632 [23.20, 24.06] | 706.4 [697, 716] | 66.92 | 84.26 / 86.03 | 703.9 / 64.95 / 86.07 | **YES** (M9_a2_q140l, M9_m8_relation, M8) |
| `fp32.real_smol_l3_w8a16_q_outlier` | 1 | R | 22.016 [21.61, 22.42] | 21.981 | 21.920 | 21.844 | 2.85 [2.49, 3.20] | 21.170 [20.74, 21.60] | 728.9 [719, 739] | 67.11 | 79.47 / 81.24 | 726.9 / 65.18 / 81.22 | no |
| `fp32.uniform_pm1` | 1 | U | 24.719 [24.31, 25.12] | 24.715 | 24.580 | 24.628 | 3.17 [2.81, 3.52] | 23.769 [23.34, 24.20] | 705.1 [695, 715] | 66.90 | 84.52 / 86.29 | 702.7 / 64.93 / 86.34 | **YES** (M9_a2_q140l, M9_m8_relation, M8) |
| `fp16.anchor7_randn_a` | 2 | 0 | 22.040 [21.70, 22.38] | 22.040 | 21.938 | 22.017 | 2.85 [2.54, 3.16] | 21.194 [20.83, 21.55] | 729.0 [719, 739] | 67.11 | 79.43 / 81.07 | 726.8 / 65.18 / 81.06 | no |
| `fp16.anchor7_randn_b` | 2 | 0 | 21.992 [21.65, 22.33] | 21.988 | 21.888 | 21.974 | 2.84 [2.53, 3.15] | 21.148 [20.79, 21.51] | 729.5 [720, 739] | 67.11 | 79.34 / 80.98 | 727.3 / 65.18 / 80.96 | no |
| `fp16.anchor7_zeros` | 2 | 0 | 0.000 [-0.33, 0.33] | 0.000 | 0.000 | 0.000 | 0.23 [-0.08, 0.54] | 0.000 [-0.36, 0.36] | 800.0 [785, 800] | 35.29 | 38.21 / 39.84 | 800.0 / 36.27 / 39.82 | no |
| `fp16.b_onebit_b8_pi` | 1 | S | 12.124 [11.77, 12.48] | 12.221 | 12.190 | 12.108 | 1.67 [1.36, 1.98] | 11.658 [11.29, 12.03] | 800.0 [785, 800] | 57.99 | 60.88 / 62.55 | 799.9 / 59.11 / 62.69 | no |
| `fp16.b_onebit_b9_one` | 1 | S | 13.580 [13.24, 13.92] | 13.562 | 13.539 | 13.504 | 1.84 [1.53, 2.15] | 13.058 [12.70, 13.42] | 799.3 [784, 800] | 60.80 | 63.60 / 65.25 | 799.0 / 61.51 / 65.20 | no |
| `fp16.laplace_both` | 1 | U | 22.302 [21.96, 22.64] | 22.277 | 22.189 | 22.273 | 2.88 [2.57, 3.19] | 21.446 [21.09, 21.81] | 726.7 [717, 736] | 67.11 | 79.92 / 81.56 | 724.6 / 65.17 / 81.50 | no |
| `fp16.randn_x8` | 1 | U | 22.350 [22.01, 22.69] | 22.328 | 22.229 | 22.299 | 2.88 [2.57, 3.19] | 21.492 [21.13, 21.85] | 726.2 [717, 736] | 67.10 | 80.01 / 81.65 | 724.2 / 65.17 / 81.60 | no |
| `fp16.real_qwen_l3_softmax_v_h1` | 1 | R | 17.417 [17.08, 17.75] | 17.416 | 17.366 | 17.293 | 2.30 [1.99, 2.61] | 16.748 [16.39, 17.11] | 776.5 [767, 786] | 66.68 | 70.78 / 72.42 | 774.2 / 65.09 / 72.41 | no |
| `fp16.real_s360_l3_qk` | 1 | R | 21.839 [21.50, 22.18] | 21.834 | 21.742 | 21.782 | 2.82 [2.51, 3.13] | 21.001 [20.64, 21.36] | 730.9 [721, 741] | 67.11 | 79.05 / 80.70 | 728.7 / 65.18 / 80.67 | no |
| `fp16.real_s360_l3_w8a16_gate` | 1 | R | 21.677 [21.34, 22.02] | 21.675 | 21.584 | 21.648 | 2.80 [2.49, 3.11] | 20.844 [20.48, 21.20] | 732.4 [723, 742] | 67.12 | 78.75 / 80.39 | 730.2 / 65.19 / 80.38 | no |
| `fp16.sorted_k` | 1 | U | 19.808 [19.47, 20.15] | 19.829 | 19.758 | 19.747 | 2.58 [2.27, 2.89] | 19.047 [18.69, 19.41] | 750.7 [741, 760] | 67.12 | 75.25 / 76.90 | 748.2 / 65.20 / 76.92 | no |
| `fp16.uniform_pm1` | 1 | U | 21.983 [21.64, 22.32] | 21.986 | 21.880 | 21.948 | 2.84 [2.53, 3.15] | 21.139 [20.78, 21.50] | 729.6 [720, 739] | 67.11 | 79.32 / 80.97 | 727.3 / 65.18 / 80.96 | no |
| `int8.a_full_b_pos` | 1 | U | 7.128 [6.80, 7.46] | 6.963 | 6.973 | 6.900 | 1.15 [0.75, 1.55] | 6.854 [6.50, 7.21] | 800.0 [785, 800] | 50.00 | 52.93 / 54.55 | 800.0 / 50.68 / 54.98 | no |
| `int8.anchor7_full_a` | 2 | 0 | 7.272 [6.94, 7.60] | 7.062 | 7.056 | 7.018 | 1.16 [0.77, 1.56] | 6.993 [6.64, 7.35] | 800.0 [785, 800] | 50.27 | 53.20 / 54.83 | 800.0 / 50.86 / 55.15 | no |
| `int8.anchor7_full_b` | 2 | 0 | 7.216 [6.89, 7.55] | 7.016 | 6.999 | 6.964 | 1.16 [0.76, 1.56] | 6.939 [6.58, 7.30] | 800.0 [785, 800] | 50.16 | 53.09 / 54.72 | 800.0 / 50.78 / 55.06 | no |
| `int8.anchor7_zeros` | 2 | 0 | 0.000 [-0.32, 0.32] | 0.000 | 0.000 | 0.000 | 0.30 [-0.10, 0.70] | 0.000 [-0.34, 0.34] | 800.0 [785, 800] | 36.66 | 39.59 / 41.20 | 800.0 / 37.65 / 41.90 | no |
| `int8.b_line_0f_f0` | 1 | L | 6.278 [5.94, 6.61] | 5.857 | 6.272 | 6.572 | 1.05 [0.65, 1.45] | 6.037 [5.68, 6.40] | 800.0 [785, 800] | 48.41 | 51.34 / 52.98 | 800.0 / 48.61 / 53.84 | no |
| `int8.b_line_6bit_rand` | 1 | L | 7.379 [7.04, 7.72] | 7.032 | 6.784 | 6.909 | 1.18 [0.78, 1.58] | 7.096 [6.73, 7.46] | 800.0 [785, 800] | 50.47 | 53.40 / 55.05 | 800.0 / 50.81 / 55.16 | no |
| `int8.b_line_7f_80_aconst` | 1 | L | 2.577 [2.20, 2.96] | 1.915 | 2.341 | 2.703 | 0.61 [0.21, 1.01] | 2.478 [2.08, 2.88] | 800.0 [785, 800] | 41.48 | 44.41 / 46.13 | 800.0 / 41.24 / 46.80 | no |
| `int8.b_line_compl_rand` | 1 | L | 7.047 [6.68, 7.42] | 6.194 | 6.678 | 6.937 | 1.14 [0.74, 1.54] | 6.777 [6.39, 7.17] | 800.0 [785, 800] | 49.85 | 52.77 / 54.48 | 800.0 / 49.24 / 54.53 | no |
| `int8.b_line_near7_rand` | 1 | L | 6.962 [6.60, 7.32] | 6.233 | 6.659 | 6.874 | 1.13 [0.73, 1.53] | 6.695 [6.31, 7.08] | 800.0 [785, 800] | 49.69 | 52.62 / 54.30 | 800.0 / 49.31 / 54.40 | no |
| `int8.b_line_zero_55` | 1 | L | 4.434 [4.11, 4.76] | 4.190 | 4.060 | 4.096 | 0.83 [0.43, 1.23] | 4.263 [3.91, 4.62] | 800.0 [785, 800] | 44.96 | 47.89 / 49.51 | 800.0 / 45.49 / 49.80 | no |
| `int8.b_line_zero_7f` | 1 | L | 3.901 [3.57, 4.23] | 3.516 | 3.884 | 4.165 | 0.76 [0.37, 1.16] | 3.751 [3.39, 4.11] | 800.0 [785, 800] | 43.96 | 46.89 / 48.52 | 800.0 / 44.23 / 49.32 | no |
| `int8.bheld_01` | 1 | H | 5.820 [5.47, 6.17] | 6.277 | 6.295 | 6.141 | 0.99 [0.59, 1.39] | 5.597 [5.22, 5.97] | 800.0 [785, 800] | 47.55 | 50.48 / 52.15 | 800.0 / 49.39 / 53.87 | no |
| `int8.bheld_33` | 1 | H | 7.148 [6.77, 7.52] | 6.647 | 6.815 | 6.580 | 1.15 [0.75, 1.55] | 6.874 [6.48, 7.27] | 800.0 [785, 800] | 50.04 | 52.96 / 54.68 | 800.0 / 50.09 / 54.55 | no |
| `int8.bheld_55` | 1 | H | 7.100 [6.73, 7.47] | 6.637 | 6.811 | 6.573 | 1.14 [0.74, 1.54] | 6.827 [6.43, 7.22] | 800.0 [785, 800] | 49.95 | 52.87 / 54.58 | 800.0 / 50.07 / 54.53 | no |
| `int8.bheld_55_asmall` | 2 | H | 7.032 [6.66, 7.41] | 6.475 | 6.561 | 6.370 | 1.14 [0.74, 1.53] | 6.761 [6.36, 7.16] | 800.0 [785, 800] | 49.82 | 52.74 / 54.46 | 800.0 / 49.76 / 54.22 | no |
| `int8.bheld_fd` | 1 | H | 6.392 [6.05, 6.74] | 6.567 | 6.672 | 6.470 | 1.06 [0.66, 1.46] | 6.147 [5.78, 6.51] | 800.0 [785, 800] | 48.62 | 51.55 / 53.20 | 800.0 / 49.94 / 54.39 | no |
| `int8.bheld_ff` | 1 | H | 5.978 [5.62, 6.33] | 6.500 | 6.594 | 6.399 | 1.01 [0.61, 1.41] | 5.748 [5.37, 6.13] | 800.0 [785, 800] | 47.85 | 50.77 / 52.45 | 800.0 / 49.81 / 54.27 | no |
| `int8.bheld_rand` | 1 | H | 6.873 [6.51, 7.23] | 6.818 | 7.071 | 6.791 | 1.12 [0.72, 1.52] | 6.609 [6.23, 6.99] | 800.0 [785, 800] | 49.52 | 52.45 / 54.13 | 800.0 / 50.41 / 54.92 | no |
| `int8.pos_small` | 1 | U | 4.346 [4.02, 4.67] | 4.465 | 4.441 | 4.393 | 0.82 [0.42, 1.22] | 4.179 [3.83, 4.53] | 800.0 [785, 800] | 44.79 | 47.72 / 49.34 | 800.0 / 46.00 / 50.29 | no |
| `int8.real_qwen_l3_w8a8_down_massive` | 1 | R | 6.346 [6.02, 6.67] | 6.255 | 6.163 | 6.184 | 1.05 [0.66, 1.45] | 6.102 [5.75, 6.45] | 800.0 [785, 800] | 48.53 | 51.46 / 53.08 | 800.0 / 49.35 / 53.64 | no |
| `int8.real_qwen_l3_w8a8_k_sink` | 1 | R | 6.619 [6.30, 6.94] | 6.616 | 6.595 | 6.606 | 1.09 [0.69, 1.49] | 6.365 [6.01, 6.72] | 800.0 [785, 800] | 49.05 | 51.97 / 53.59 | 800.0 / 50.03 / 54.31 | no |
| `int8.real_s360_l2_w8a8_o` | 1 | R | 6.235 [5.91, 6.56] | 6.165 | 6.112 | 6.124 | 1.04 [0.64, 1.44] | 5.995 [5.64, 6.35] | 800.0 [785, 800] | 48.33 | 51.26 / 52.87 | 800.0 / 49.18 / 53.45 | no |
| `int8.real_s360_l3_w8a8_q_outlier` | 1 | R | 6.711 [6.38, 7.04] | 6.552 | 6.448 | 6.474 | 1.10 [0.70, 1.50] | 6.453 [6.10, 6.81] | 800.0 [785, 800] | 49.22 | 52.15 / 53.77 | 800.0 / 49.91 / 54.20 | no |
| `int8.real_smol_l2_w8a8_up_outlier` | 1 | R | 6.816 [6.49, 7.14] | 6.673 | 6.599 | 6.612 | 1.11 [0.71, 1.51] | 6.554 [6.20, 6.91] | 800.0 [785, 800] | 49.41 | 52.34 / 53.96 | 800.0 / 50.14 / 54.42 | no |
| `int8.real_smol_l3_w8a8_down` | 2 | R | 6.881 [6.56, 7.21] | 6.741 | 6.669 | 6.680 | 1.12 [0.72, 1.52] | 6.617 [6.26, 6.97] | 800.0 [785, 800] | 49.54 | 52.47 / 54.09 | 800.0 / 50.26 / 54.55 | no |
| `int8.relu_q_a` | 1 | U | 5.722 [5.40, 6.05] | 5.771 | 5.744 | 5.729 | 0.98 [0.58, 1.38] | 5.503 [5.15, 5.85] | 800.0 [785, 800] | 47.37 | 50.30 / 51.91 | 800.0 / 48.45 / 52.72 | no |
| `int8.sparse_rows_a` | 1 | U | 6.029 [5.70, 6.35] | 5.940 | 5.904 | 5.820 | 1.02 [0.62, 1.42] | 5.797 [5.44, 6.15] | 800.0 [785, 800] | 47.94 | 50.87 / 52.49 | 800.0 / 48.76 / 53.04 | no |

**aifoundry2 and section 22's 82 W stop: 6 of 61 tiles are left out there.** The rule, registered here: a tile is left out (it does not run on aifoundry2 as designed) if its predicted 95% upper peak board power exceeds 82 W under M9's primary aifoundry2 prediction (Q140(l)'s part, whose peak is M8's peak rule unchanged on M9's D at its band top), under M9 through M8's relation (the same rule on the same D; the two agree on every tile) or under M8 as frozen: the union, because 82 W is a safety stop and aifoundry2's PMIC over-power configuration is unknown. Left out: `fp32.anchor7_randn_a` (p2, case 0): 95% M8 86.33 W, M9_a2_q140l 86.27 W, M9_m8_relation 86.27 W; expected M8 84.51, M9_a2_q140l 84.49, M9_m8_relation 84.49; `fp32.anchor7_randn_b` (p2, case 0): 95% M8 86.16 W, M9_a2_q140l 86.10 W, M9_m8_relation 86.10 W; expected M8 84.34, M9_a2_q140l 84.33, M9_m8_relation 84.33; `fp32.laplace_both` (p1, case U): 95% M8 86.29 W, M9_a2_q140l 86.26 W, M9_m8_relation 86.26 W; expected M8 84.48, M9_a2_q140l 84.48, M9_m8_relation 84.48; `fp32.real_qwen_l3_softmax_v_sink` (p1, case R): 95% M8 84.91 W, M9_a2_q140l 84.86 W, M9_m8_relation 84.86 W; expected M8 83.08, M9_a2_q140l 83.08, M9_m8_relation 83.08; `fp32.real_s360_l1_qk` (p2, case R): 95% M8 86.07 W, M9_a2_q140l 86.03 W, M9_m8_relation 86.03 W; expected M8 84.25, M9_a2_q140l 84.26, M9_m8_relation 84.26; `fp32.uniform_pm1` (p1, case U): 95% M8 86.34 W, M9_a2_q140l 86.29 W, M9_m8_relation 86.29 W; expected M8 84.52, M9_a2_q140l 84.52, M9_m8_relation 84.52. Expected peaks over 82 W: `fp32.anchor7_randn_a`, `fp32.anchor7_randn_b`, `fp32.laplace_both`, `fp32.real_qwen_l3_softmax_v_sink`, `fp32.real_s360_l1_qk`, `fp32.uniform_pm1`. Kept but within 2 W of the line at 95%: `fp16.randn_x8` 81.65 W, `fp16.laplace_both` 81.56 W, `fp32.real_smol_l3_w8a16_q_outlier` 81.24 W, `fp16.anchor7_randn_a` 81.07 W, `fp16.anchor7_randn_b` 80.98 W, `fp16.uniform_pm1` 80.97 W, `fp16.real_s360_l3_qk` 80.70 W, `fp16.real_s360_l3_w8a16_gate` 80.39 W. The highest 95% value kept is 81.65 W (`fp16.randn_x8`). Priority-1 coverage left on aifoundry2 per class: E 6 of 6, H 6 of 6, L 7 of 7, R 9 of 10, S 7 of 7, U 10 of 12. E165 drops or duty-cycles the left-out tiles, and every registered board stop stays at most 85 W on live samples (section 22).

**aifoundry2 (E165): governed against 800 MHz.** M9's part puts 18 of the 61 tiles below 795 MHz in a 6 s burst (705.1 to 790.3 MHz; 13 of them priority 1), M8 18. Report the two sets apart, as E143 and E160 did. With no session read, M9's aifoundry2 predictions use the fallback offset and the reference die; after E165's zeros anchors run, the same frozen code recomputes them mechanically from the session's own reads (`--a2-session`, `--a2-die-start`; Commands, below). Which of the two E165 scores as primary is E165's to register before its claim.

**Rank 4's paired-anchor rule, registered here** ([`RANK4-RULE.md`](RANK4-RULE.md), [`rank4_rule.json`](rank4_rule.json)): a card's scale is the median of its anchors' ratios to aifoundry3's; it must land within 1% of the pool's median ratio for floats, and within 2% for int8, in each session pair. The anchors are pool 7's four float random anchors and two int8 ones; the pool's median is E157's X1 / X2 selection on pool 7 (non-anchor tiles measured on both cards, floats at D >= 5 W, int8 at D >= 1 W); each card's D is its registered primary on Q139(u)'s footing. [`score_rank4.py`](score_rank4.py) applies it; its self-test on pool 6 (E153, E157, with the critic's anchors) reproduces Q140(c)'s check 3 and E157's X1 / X2 exactly (16 checks, 0 differ; [`selftest-rank4.txt`](selftest-rank4.txt)). Forecast, registered: floats PASS (about -0.15%); int8 PASS more likely than not (about -1%, 69-75% inside ±2%).

**Where M9 departs from the frozen models** (D at 600 MHz on aifoundry3; descriptive, nothing fitted), per pool class at priority 1, the mean and the largest of M9 - M8 and M9 - M6:

| class | tiles | M9 - M8: mean, largest (tile) | M9 - M6: mean, largest (tile) |
|---|---:|---|---|
| S | 7 | -0.058 W, -0.097 (`fp16.b_onebit_b8_pi`) | +0.040 W, +0.075 (`fp16.b_onebit_b9_one`) |
| E | 6 | +0.103 W, +0.146 (`fp32.exp_only_pos12`) | +0.121 W, +0.171 (`fp32.exp_b_alt_nib`) |
| L | 7 | +0.520 W, +0.853 (`int8.b_line_compl_rand`) | +0.046 W, +0.470 (`int8.b_line_6bit_rand`) |
| H | 6 | -0.022 W, -0.522 (`int8.bheld_ff`) | +0.060 W, +0.568 (`int8.bheld_33`) |
| U | 12 | +0.007 W, +0.165 (`int8.a_full_b_pos`) | +0.064 W, +0.228 (`int8.a_full_b_pos`) |
| R | 10 | +0.051 W, +0.159 (`int8.real_s360_l3_w8a8_q_outlier`) | +0.118 W, +0.236 (`int8.real_s360_l3_w8a8_q_outlier`) |

## Checks

1. **M9 is committed and unchanged.** Q140(m)'s `8dfafae3` and `1f244140` and Q140(l)'s `245caffe`, `5b98bd5c` and `5c98c0c5` are on `origin/main`; when the predictions ran the tree's HEAD was `e39d06da` (= `origin/main`). `git diff --name-only --diff-filter=MDRT 1f244140 -- <M9's dir> ':!<M9's dir>/README.md'` prints nothing (Q140(m)'s corrected check, C5); `git diff 8dfafae3` over M8's, M7's, M6's and M5's directories, Q139(u)'s footing, E147's and E119's code, blind pool 5 and the counts files `fit_m9.COUNTS_FILES` names is empty; `git diff 5b98bd5c` over `m9_a2.json` and `predict_m9_a2.py` is empty; the working tree is clean in all of them. `m9.json` `322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835`, `predict_blind7.py` `32b5cdac865945e88e4616a30de78ce93eaf97381fe38f3d62aab5cbf158c2d1`, `m9_a2.json` `cc6fbccc4b63fa80575e91abb02c6296a24ac97984fd52a232dbea04a6c6fec8`, `predict_m9_a2.py` `420b887ea57cfdfec7da6a1f4f3f2017a92da9c9cf86d71cefe8c17ec1fcf284`, as both lanes handed them over. M9's self-test, rerun here, passes with output identical to the committed `selftest-predict-blind7.txt` (SELFTEST PASS: 5072 fields, 0 differ).
2. **Everything the predictor read is named.** Run under an audit hook (the same runs, byte-identical output), it imported 15 modules and read 99 data files in the tree ([`provenance-blind7.json`](provenance-blind7.json): path, sha256, its state at M9's freeze `1f244140`). Every one outside this directory is tracked and identical to `1f244140`; those not tracked there (63) are this directory's pool files and counts.
3. **The pool is the designer's, byte for byte.** Copied from a snapshot verified first: 92 of 92 files identical; `SHA256SUMS` 91 of 91 OK (its sha256 `df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239`); `MANIFEST` `92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a`, 61 of 61 lines; `blind7.json` `24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552`, every tile 61 of 61 matching its `sha256.whole`, `a` and `b`, 2,048 B each. `make_blind7.py --check`, before anything was added: "check: 63 built files, 92 pool files, 0 problems".
4. **After the additions** the pool's 92 files are still identical (92 of 92; `SHA256SUMS` 91 of 91). `make_blind7.py --check` in the tree lists the 17 files beside the pool and passes ("check: 63 built files, 92 pool files, 0 problems"; the pool's fix K4), and so does a copy holding the pool's 92 files only.
5. **The predictions are the frozen models'.** Each file records the sha256 of the frozen files it read, and they are the committed ones. Run again into a scratch directory, the predictor writes all seven files byte for byte, and so does the traced run. An independent recompute from each tile's recorded features with the frozen constants of `m9.json`, `m8.json`, `m7.json`, `m6.json` and `m9_a2.json` (D, the card scale, the band, S, the die rise and its band; on aifoundry2 M9's and M8's c, P800, peak, 95% peak and the 82 W flag, M9's a2_q140l peak, flag and band half-widths, and every other band's half-width; the burst clocks are the predictors' own) agrees to the files' rounding: 7076 fields, 0 beyond it.
6. **M8, M7 and M6 equal Q139(m)'s `predict_blind6.py`.** Run unchanged on this pool and these counts (into scratch), its predictions equal `predict_blind7.py`'s field for field on all three cards: 13,810 fields (every M8, M7 and M6 field, the features it records, each tile's hash and check fields, and the headers), 0 differ.
7. **The bench counted every tile cleanly:** 61 rows for the 61 tiles, `check_mismatch` 0 at all 183 launch points (the bench's functional check, C against software at all 256 words), at its default three launch points, which is what M9's features were fitted on (Q140(m): `predict_blind7.py` stops on a float tile with another number of points).
8. **Rank 4's scorer** reproduces Q140(c)'s committed check 3 and E157's registered X1 / X2 on pool 6 (above).

## What the predictor reads of the pool, and the C-register descriptor

`predict_blind7.py` reads from `blind7.json` only each tile's name, type, file, `sha256.whole`, priority and case; it never reads `c_check`. M9's and M8's C-register feature (`c_end`) comes from the tile's bytes through `fit_m8.c_feats`, that is `make_blind5.py`'s code: PRM 9.4's literal fp16 rule (a two-term update dropped unless all four halves are nonzero) and make_blind5's launch-end count. That is the frozen definition, in training and here alike. Pool 7's own `c_check` follows the card's plain fp16 sum and pool 6's C2 launch end (away from powers of two). As a sensitivity only (post hoc, in this lane's scratch; nothing committed changes), taking pool 7's descriptor instead moves M9's D at its c_end price (6.186 fJ a flip; M8's 6.438) most on `fp32.b_onebit_b20_full` (-0.0284 W; c_end 12288 -> 8192), `fp32.anchor7_randn_a` (-0.0023 W; c_end 10707 -> 10377), `fp32.exp_b_alt_lsb` (+0.0020 W; c_end 3936 -> 4225), `fp32.exp_b_alt_b26` (-0.0018 W; c_end 6048 -> 5784). Over the 34 float tiles, 1 move by more than 0.01 W. The two fp16 tiles with half-zero words are `fp16.real_qwen_l3_softmax_v_h1` and `fp16.real_s360_l3_w8a16_gate`. The card lanes check C with Q139(k)'s `tools/claims-v3/ccheck/`, never with `c_op1_sha256` (it differs from ccheck's `accum.c` on the 9 fp16 tiles, the RTL's fixed-point window; the pool's README).

## The bench's counts

[`counts-blind7.json`](counts-blind7.json) (sha256 `0749922588daf81f684d5e7804d337cf38d6b3c8519a99903b535118492caa57`): 61 rows for the 61 tiles, keyed `type.name` as the manifest names them, from rtl-sim/fma_toggle_v2's `run_kinds.py` at its default three launch points of a 0.5 s launch, with the same build and maps that counted M5's to M9's rows and pools 3-6 (Q133(b)'s build; its seven files hash as when Q139(x) counted pool 6). Run 02:51:30-03:21:41 PST, 4 jobs (section 24: at most 4 cores a lane), at nice 20: the script asks `nice -n 10`, and this session's background commands start at nice 10, so the bench ran gentler than the brief's nice 10 (as Q139(x)'s did).

| bench file | sha256 |
|---|---|
| `obj_vpu/Vtb` | `9096e64586b561818ae64af9830ccdf1c6f08e0fab123bf0e7807516af6527e5` |
| `accum` | `9e47d24311e70f37868428605bc5f48310dbd5c670b489aea44148994ea4e5a1` |
| `settle_count` | `2a79d1320df29fc76d4c0d25a018059ade3a41ed43f2ea0ff1a9881b01d81363` |
| `maps/unit_float.map` | `1372705868cec52e47bd631db4850d63beaa3f21cc9891160da3941926ad9a51` |
| `maps/unit_int8.map` | `211be19daef07652dec3a160ed4024c58d20c50fc42cd7ffdfb46947fca5068e` |
| `maps/vpu.map` | `d5f925f204bc701e4746e616efe1962ab209d2ec5a91273214eccab0e30502d9` |
| `run_kinds.py` | `fa8112e9ff953f714f3a2161990a581c37617884a44cc6dddfb6bbe5e6133110` |

## For the card lanes (E163, E164, E165)

- **The gate.** This commit must precede each lane's registration, claim and first launch (`git merge-base --is-ancestor <this commit> <the lane's registration>`). Check the pool with `shasum -a 256 -c SHA256SUMS` (91 OK), the `MANIFEST` hash above and `make_blind7.py --check` ("63 built files, 92 pool files, 0 problems", the additions listed beside).
- **Counting.** M9's features were fitted on the bench's three-point counts; these predictions use them. The recount rule in Q140(m)'s `recount-rule/` is for the next model, never for M9's predictions.
- **Duty (Q140(m) D1).** The predictor works at the nominal op rate (duty 0.9963). Pool 6's sessions ran at 0.9932 because the C log's DMA widened the gap between launches, so a pool-7 session that logs C reads about 0.3% low against M9, M8, M7 and M6 alike. A factor common to a session cancels in rank 4's ratio of ratios.
- **aifoundry2.** The left-out tiles above do not run as designed. The zeros anchors run first (E165's design), and M9's part can be recomputed from them mechanically.
- **The anchors.** All nine run in every session: they are rank 4's inputs and the footing. They are marked priority 2 in the `MANIFEST`, but they are not among the four priority-2 tests a session may drop first to save time (`blind7.json` `subsets.priority2_tests`).
- **Not registered here** (the card lanes' to register before their claims): the critic's rank-1 coverage share (26 of 30 inside) on pool 7's 48 priority-1 kinds is 42 of 48 at the same rate; the unaimed subset for "no worse than M6" is the 12 U tiles (`unaimed_synthetic`), or 17 with the five float real tiles (`unaimed_with_float_real`), and never the int8 real tiles (they carry near-whole-byte flips); the real-tile sub-rule (rank 9) is over the 10 priority-1 real tiles, or all 12.

## Commands, exactly

From the top of the tree unless said. `run_kinds.py` needs no numpy; the predictors need numpy (here macOS's `/usr/bin/python3` 3.9.6 with numpy 1.26.4, as Q140(m) used); the rank-4 scorer and the admission script use the standard library only.

```
# 1. the pool, from Q140(b)'s scratch, unchanged (through a snapshot verified first)
cp -Rp <Q140(b) pool dir>/. tools/claims-v3/kinds/blind7/
(cd tools/claims-v3/kinds/blind7 && shasum -a 256 -c SHA256SUMS)          # 91 OK
python3 -B tools/claims-v3/kinds/blind7/make_blind7.py --check            # 63 built files, 92 pool files, 0 problems
# 2. the bench, in its build dir; EXTRA = for each tile of blind7.json in order, <type>:<name after 'type.'>:<repo>/tools/claims-v3/kinds/blind7/<file>, comma-joined
nice -n 10 python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds <repo>/tools/claims-v3/kinds \
  --out counts-blind7.json --only __none__ --extra-tiles "$EXTRA" --points launch --jobs 4 --tmp <tmp dir> --keep-going
cp counts-blind7.json <repo>/tools/claims-v3/kinds/blind7/counts-blind7.json
# 3. the predictions: predict_blind7.py writes predictions-<card>.json/.md (and a2-inputs-aifoundry2.json); this lane renames them predictions-blind7-<card>.*
for card in aifoundry3 aifoundry1c1; do
  python3 -B docs/reports/data/2026-11-04-q140m-m9/predict_blind7.py tools/claims-v3/kinds/blind7 $card --counts tools/claims-v3/kinds/blind7/counts-blind7.json
done
python3 -B docs/reports/data/2026-11-04-q140m-m9/predict_blind7.py tools/claims-v3/kinds/blind7 aifoundry2 --counts tools/claims-v3/kinds/blind7/counts-blind7.json \
  --a2-terms docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json
for card in aifoundry3 aifoundry1c1 aifoundry2; do
  mv tools/claims-v3/kinds/blind7/predictions-$card.json tools/claims-v3/kinds/blind7/predictions-blind7-$card.json
  mv tools/claims-v3/kinds/blind7/predictions-$card.md tools/claims-v3/kinds/blind7/predictions-blind7-$card.md
done
# 4. the 82 W stop on aifoundry2, and rank 4's scorer's self-test
python3 -B tools/claims-v3/kinds/blind7/admission_aifoundry2.py
python3 -B tools/claims-v3/kinds/blind7/score_rank4.py --selftest . > tools/claims-v3/kinds/blind7/selftest-rank4.txt
# after E165's zeros anchors run: M9's aifoundry2 part recomputed from the session's own reads ({format: [{burst_w, burst_mhz, die_start}]})
python3 -B docs/reports/data/2026-11-04-q140m-m9/predict_blind7.py tools/claims-v3/kinds/blind7 aifoundry2 --counts tools/claims-v3/kinds/blind7/counts-blind7.json \
  --a2-terms docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json --a2-session <anchors.json> [--a2-die-start <C>] --out <dir>
# after E163 and E164: rank 4
python3 -B tools/claims-v3/kinds/blind7/score_rank4.py --a3 <E163 scored.json or D table> --c1 <E164 scored.json or D table> --pair E163/E164 --out <rank4.json>
```

Rerunning steps 3 and 4 on these files reproduces the predictions, the admission file and the self-test byte for byte.

## Order (PST, Wed 4 Nov 2026)

1. 02:50:38 brief read (CONTEXT.md sections 24, 3, 5, 6, 7, 17, 20, 21, 22); Q139 critic result.json/.md; Q140(m), Q140(l), Q140(b) finals (attached)
2. 02:50:38 M9 check: 8dfafae3, 1f244140 (Q140(m)) and 245caffe, 5b98bd5c, 5c98c0c5 (Q140(l)) on origin/main (HEAD = origin/main = c9aaf179); C5 diff empty; m9.json 322dd739, predict_blind7.py 32b5cdac, m9_a2.json cc6fbccc, predict_m9_a2.py 420b887e as handed over
3. 02:50:39 snapshot of Q140(b)'s fixed pool taken (cp -Rp) into scratch work/snapshot-pool7
4. 02:50:39 pool copied (cp -Rp) from the verified snapshot into tools/claims-v3/kinds/blind7
5. 02:50:55 make_blind7.py --check in the tree before any addition: check: 63 built files, 92 pool files, 0 problems 
6. 02:51:29 bench starting on the 61 tiles (Q133(b)'s build, default three launch points, --jobs 4; nice -n 10 asked, and it ran at nice 20 because this session's background commands start at nice 10)
7. 02:59:47 rank 4's rule written (rank4_rule.json, RANK4-RULE.md, score_rank4.py); its self-test on pool 6 PASS (16 checks, 0 differ against Q140(c)'s check 3 and E157's X1/X2); no pool-7 data exists
8. 03:20:27 one variable in score_rank4.py renamed for the public-text scan (the lab's fixed list flags its name); its self-test output byte-identical; admission_aifoundry2.py's nested f-string quotes fixed for python 3.9 (syntax check)
9. 03:21:41 the bench ends: 61 rows at the three launch points, check_mismatch 0 at all 183 points
10. 03:21:53 frozen inputs checked unchanged (8dfafae3 / 1f244140 / 5b98bd5c; working tree clean there); HEAD e39d06da, origin/main e39d06da
11. 03:22:39 the first prediction attempt stopped on a shell error (an empty array under set -u in macOS's bash 3.2) before any prediction was written; fixed and rerun from the counts gate
12. 03:22:40 frozen inputs checked unchanged (8dfafae3 / 1f244140 / 5b98bd5c; working tree clean there); HEAD e39d06da, origin/main e39d06da
13. 03:22:47 predictions written for the three cards (predict_blind7.py; aifoundry2 with Q140(l)'s m9_a2.json), renamed predictions-blind7-<card>.*; predict_blind6.py run on the same pool and counts into scratch
14. 03:22:50 M9's self-test rerun (SELFTEST PASS: 5072 fields, 0 differ, identical to the committed output); the 82 W list written; the c_end sensitivity (scratch, post hoc) did not run: python -I hid the user site that holds numpy (corrected below)
15. 03:23:40 post-checks: reruns and traced runs byte-identical, provenance, predict_blind6.py cross-check, independent recompute, the pool beside the additions, --check in the tree and pool-only, rank 4's self-test again
16. 03:25:44 the c_end sensitivity (scratch, post hoc) rerun with python -B: done
17. 03:26:02 README-predictions.md written from the files and the checks; the pool and --check checked again with all 17 additions beside it
18. Then: the public-text scan over every text file here, the pool checked once more beside the 17 additions, and one commit through the lab's commit script, before any E163, E164 or E165 claim. That commit is the gate each card lane checks.

## What this cannot say

- **Nothing here is a measurement or a score.** The predictions are frozen; E163, E164 and E165 measure the tiles and score them by their own registered rules.
- **M9 is out of kind, not blind, until pool 7 runs.** Its candidates were named from pool 6's misses, and pool 6 is in its training rows. Pool 7 is the first blind test of M9 and of Q140(l)'s part.
- **M9 keeps the bench's three-point launch average** on single high bits: at 27 launch points pool 6's bit-20 tile's over-count was 0.78 ± 0.27 W (Q140(m) C9), so on pool 7's S tiles M9 may carry an error of that size from the counts alone.
- **On aifoundry2 the frozen predictions have no session read yet**: M9's part takes the fallback zeros offset and the reference die start; its clock moves about -3.9 MHz per W of the session's anchor offset under the cap and about -2.4 MHz per C of die start (Q140(l)).
- **The three zeros anchors are byte-identical** (one tile under three type names, as in pools 5 and 6), each predicted under its own type; their D is near zero by construction.
- **The C-register descriptor** is make_blind5's, as frozen (above); pool 7's own `c_check` uses the card's rule.
- The counts are the public RTL bench's (int8's multiply is behavioural there; `bpp_r4` counts a modelled radix-4 Booth array, a fitted price on a count nobody has seen in silicon).

## Files

| file | what | sha256 |
|---|---|---|
| [`README.md`](README.md), [`MANIFEST`](MANIFEST), [`blind7.json`](blind7.json), [`SHA256SUMS`](SHA256SUMS), [`make_blind7.py`](make_blind7.py), [`fetch_real7.py`](fetch_real7.py), `real/`, `tiles/` | Q140(b)'s pool, unchanged (92 files) | `MANIFEST` `92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a`; `blind7.json` `24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552`; `SHA256SUMS` `df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239` |
| [`counts-blind7.json`](counts-blind7.json) | the bench's counts for the 61 tiles | `0749922588daf81f684d5e7804d337cf38d6b3c8519a99903b535118492caa57` |
| [`predictions-blind7-aifoundry3.json`](predictions-blind7-aifoundry3.json) | M9, M8, M7, M6 on aifoundry3 | `303dc5b94b35dbd772a9d405934406b4f3fa23551efeba63d85e064839b3d750` |
| [`predictions-blind7-aifoundry3.md`](predictions-blind7-aifoundry3.md) | the same, as a table | `e90356e0feaa9fea7b2c60eb782e30efa9cef9a7f0f4f47a9c3294f05073976c` |
| [`predictions-blind7-aifoundry1c1.json`](predictions-blind7-aifoundry1c1.json) | M9, M8, M7, M6 on aifoundry1 card 1 | `22fe64be1b648f1aac222490c2548e5c4f920932c93ff470f5bb34ab9d9b27c0` |
| [`predictions-blind7-aifoundry1c1.md`](predictions-blind7-aifoundry1c1.md) | the same, as a table | `83e97f5c72c860ee06a8b5f5eb588b74e55944e72e5177cbc33d7f50ebe7e385` |
| [`predictions-blind7-aifoundry2.json`](predictions-blind7-aifoundry2.json) | M9 (Q140(l)'s part, and through M8's relation), M8, M7, M6 on aifoundry2 | `e2c467c4a60d6409fb9139e8b109ad5f5e758cc1747367984e164ce397c57c01` |
| [`predictions-blind7-aifoundry2.md`](predictions-blind7-aifoundry2.md) | the same, as a table | `d08d5c9b9afb3ed764a7d9a34ea35162cba7fcc17c4c11252f96207bd08a70dd` |
| [`a2-inputs-aifoundry2.json`](a2-inputs-aifoundry2.json) | M9's and M8's D at 600 MHz per tile (any aifoundry2 relation's input) | `ff4f4eaa49dfdcc5aeb59c86ad8225889d737f5d41eb02908e0dc8c1545c3933` |
| [`admission_aifoundry2.py`](admission_aifoundry2.py) | the 82 W stop's rule, applied | `437f85f5fdfaa426a51ebcde5bf0937f1eb181ea8fd024b08b925b9cbe65ac94` |
| [`admission-aifoundry2-82w.json`](admission-aifoundry2-82w.json) | its output: the tiles left out on aifoundry2 | `c330806ae93b86ac83e835f50b66398688a002071c817cf77e0d4e0a11caa384` |
| [`RANK4-RULE.md`](RANK4-RULE.md) | rank 4's rule in words | `852b7db73b933e93d7316bc8f80ddd1e894efce93b4e35fa7becc8c5b9c4747b` |
| [`rank4_rule.json`](rank4_rule.json) | rank 4's rule, machine-readable | `4b9ccaf006fff9bc92041bf470fe8520e7443f790c02dd1ba3e1ee62293f2507` |
| [`score_rank4.py`](score_rank4.py) | rank 4's scorer | `2aba0a82898c96521f35fa402a376cb303588791775da2c7d4b8004bb8998897` |
| [`selftest-rank4.txt`](selftest-rank4.txt) | the scorer's self-test on pool 6 | `b35d4dfea830549c69d8d5369aabb9daf146fbdf1838104226241052593f427b` |
| [`provenance-blind7.json`](provenance-blind7.json) | every module and data file the predictor read | `1d4a540c6f455a0ae359fe0115cffc23559d7c3d98e6b1dd44394622a9f6e516` |
| [`crosscheck-blind6.json`](crosscheck-blind6.json) | M8, M7, M6 against Q139(m)'s predict_blind6.py, field for field | `7204bcc9bd4d9ef2733c98b6e8abd450b11ab549210bec798fb99167c536c2ae` |

Every predictions file records the hashes of what it read: `m9.json` `322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835`, `m8.json` `8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd`, `m7.json` `bfeea822b87e0a1f8c315809192faf0a437b72bcadd1459c027cd857c8b3d8b2`, `m6.json` `87c17e086ee36699d7bb96609c02c471b5ba6b7bcdc20ead576d26f89e136e82`, the manifest `24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552`, the counts `0749922588daf81f684d5e7804d337cf38d6b3c8519a99903b535118492caa57`, `predict_blind7.py` `32b5cdac865945e88e4616a30de78ce93eaf97381fe38f3d62aab5cbf158c2d1`, `fit_m9.py` `0b3f1074c4a84865dd2f6e6e4e018a56ce28e016b22b6fbfd66b74a1520752f5`; on aifoundry2 also `m9_a2.json` `cc6fbccc4b63fa80575e91abb02c6296a24ac97984fd52a232dbea04a6c6fec8` and `predict_m9_a2.py` `420b887ea57cfdfec7da6a1f4f3f2017a92da9c9cf86d71cefe8c17ec1fcf284`. [`provenance-blind7.json`](provenance-blind7.json) names the rest.

*Commits: M6 `6a713a9f` (Q137(m)), M7 `3a210f2b` (Q138(m)), M8 `122da8b6` (Q139(m)); M9's 600 MHz part `1f244140` (Q140(m), registered at `8dfafae3`), its aifoundry2 part `5b98bd5c` (Q140(l), registered at `245caffe`); this directory, the counts, the predictions, the 82 W list and rank 4's rule: the commit that adds this README (Q140(x)).*

SPDX-License-Identifier: Apache-2.0
