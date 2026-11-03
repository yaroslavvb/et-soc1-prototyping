# Blind pool 5 in the tree, and M7's, M6's and M5's frozen predictions for it on three cards (Q138(x))

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 6**, "a power model across kinds", and the first of its "After Q137, the next steps in order": a refit "tested on a fifth pool written by someone else, on a second card". Q138's goal, in the owner's words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as possible.*

*Mon 2 Nov 2026 (week 45), Q138(x), desk only, on the Intel: no card was opened and nothing was measured. This directory is Q138(b)'s blind pool 5 ([`README.md`](README.md), every file unchanged), copied into the tree at 19:27:43 PST, after M7 was committed and pushed (`3a210f2b`, 19:21 PST; [Q138(m)'s README](../../../../docs/reports/data/2026-11-02-q138m-model/README.md)). Added beside it: the bench's counts for its 36 tiles and the frozen predictions of M7, M6 and M5 for the three cards that score the pool, E141 (aifoundry3), E142 (aifoundry1 card 1) and E143 (aifoundry2). Nothing was refitted, tuned or patched: every number below comes from Q138(m)'s `predict_blind5.py`, run unchanged at `3a210f2b` on the committed `m7.json`, `m6.json` and `m5.json`. This commit precedes every claim and launch of E141-E143; a card lane checks that it does.*

## Results

**What this does to predicting power and heat.** Nothing is scored here. This commit fixes, before any card runs, what each model says every one of pool 5's 36 tiles will draw over the same kernel on zeros, how far the die will warm, and, on aifoundry2, what clock its own governor will settle at in a burst. The error before is M7's out of kind (nested leave-one-kind-out: 0.209 W on the floats, 0.240 W on int8; heat 0.275 / 0.280 / 0.180 C for fp32 / fp16 / int8; aifoundry2 8.5 MHz and 1.86 W board end to end over 56 kinds bursts, most of them at 800 MHz where the clock is not tested; `m7.json`, `loko-m7.json`) and M6's and M5's blind error on pool 4 (E140, priority-1 tiles: M6 0.406 W rms on the floats and 0.384 W on int8, M5 0.337 and 0.379 W; all 25 tiles M6 0.406 W, M5 0.358 W; M6's die rise 0.204 / 0.164 C; `../../../../docs/reports/data/2026-11-02-e140-blind4/README.md`). The error after, the blind error on pool 5 by format, by card and by term, is what E141-E143 measure.

| card (scored by) | file | sha256 | tiles predicted | failures |
|---|---|---|---:|---|
| aifoundry3 card 0, 600 MHz pinned (E141) | [`predictions-blind5-aifoundry3.json`](predictions-blind5-aifoundry3.json), [`.md`](predictions-blind5-aifoundry3.md) | `396d336015664c46f6d181440059023d980df57e07f6e47206b3700283ab9bf1` | 36 of 36 | none |
| aifoundry1 card 1, 600 MHz (E142) | [`predictions-blind5-aifoundry1c1.json`](predictions-blind5-aifoundry1c1.json), [`.md`](predictions-blind5-aifoundry1c1.md) | `87d0ffd2299b29d52a361cff02da563aea3ebcab507784fc678c09f992d36515` | 36 of 36 | none |
| aifoundry2 card 0 under its own governor, 6 s kspeed bursts (E143) | [`predictions-blind5-aifoundry2.json`](predictions-blind5-aifoundry2.json), [`.md`](predictions-blind5-aifoundry2.md) | `596ec0754fb2abd95ac85604b497338fd3a7c8759078470a023a1b0c0726632b` | 36 of 36 | none |

Each file gives, per tile, M7's, M6's and M5's prediction with its 95% band:

- **aifoundry3 and aifoundry1 card 1** (600 MHz): `D_w`, W over the type's own zeros on that card (card 1 through each model's card scale), `D_95`; `S_w`, board W over idle (D plus the zeros' mean S on that card's training runs, `zeros_S_w`); `dT_win_c`, the die rise over the kinds harness's 4.5 s run, `dT_win_95` (M5 has no heat term: null). `D600_a3_footing_w` is the model's D on aifoundry3's footing.
- **aifoundry2** (its own governor, a 6 s burst of the kinds harness, E80's harness): `burst_mhz` (the mean clock), `burst_board_w`, `burst_D_w` (board W less zeros' board W in their own burst) and `burst_die_rise_c` (die max less die start), each with a 95% band. M6 and M5 go through M7's clock-and-voltage term and burst heat law (they have none of their own).
- Bands, as frozen in `m7.json`: M7's power band k x sqrt(pool^2 + s^2 x'Cx) with **k 3.179 on the floats and 2.483 on int8**, heat k_h 1.95 x the card's pool; M6 and M5 1.96 x their own pools; aifoundry2 +-21.3 MHz, +-3.37 W and +-1.41 C. The `band_rule` string that the predictor copies from `m7.json` into each file describes rule A's second term (the blind residuals of M5 and M6 against their own pools), but the k it applies are rule B's (Q138(m)'s README section 3; `fit_m7.py` sets `band_k` to rule B's k and the string from an older text). The numbers follow rule B; the string was left as frozen.

**Every tile, as frozen** (W and C; aifoundry3's M7, M6 and M5 D, M7's die rise; card 1's M7 D and rise; aifoundry2's M7 burst; the files hold every model on every card):

| tile | prio | aifoundry3: M7 D (W) [95%] | M6 D | M5 D | M7 dT (C) [95%] | card 1: M7 D (W) [95%] | M7 dT (C) | aifoundry2: M7 MHz [95%] | M7 burst board W | M7 burst D (W) | M7 burst die rise (C) |
|---|---|---|---:|---:|---|---|---:|---|---:|---:|---:|
| `fp32.anchor_randn` | 2 | 24.487 [23.68, 25.29] | 24.538 | 24.570 | 3.14 [2.78, 3.49] | 23.779 [23.08, 24.48] | 2.94 | 707.0 [686, 728] | 65.39 | 29.04 | 6.15 |
| `fp32.anchor_zeros` | 2 | 0.000 [-0.79, 0.79] | 0.000 | 0.000 | 0.23 [-0.12, 0.59] | 0.000 [-0.68, 0.68] | 0.21 | 800.0 [779, 800] | 36.35 | 0.00 | 2.08 |
| `fp32.b_exp_busy_a_const` | 2 | 15.586 [14.78, 16.40] | 15.504 | 15.745 | 2.08 [1.73, 2.44] | 15.136 [14.43, 15.84] | 1.95 | 792.3 [771, 800] | 64.45 | 28.10 | 6.02 |
| `fp32.block_sparse_k4` | 2 | 12.786 [11.99, 13.58] | 12.614 | 12.814 | 1.75 [1.40, 2.10] | 12.416 [11.73, 13.10] | 1.64 | 799.8 [778, 800] | 60.24 | 23.89 | 5.43 |
| `fp32.e4m3grid_gelu_w` | 1 | 16.733 [15.93, 17.54] | 16.726 | 16.886 | 2.22 [1.86, 2.57] | 16.249 [15.55, 16.95] | 2.08 | 783.0 [762, 800] | 65.23 | 28.88 | 6.12 |
| `fp32.exp_only_both` | 1 | 15.794 [14.97, 16.62] | 15.851 | 15.976 | 2.11 [1.75, 2.46] | 15.338 [14.62, 16.06] | 1.97 | 790.9 [770, 800] | 64.64 | 28.29 | 6.04 |
| `fp32.gray_stream` | 1 | 16.675 [15.88, 17.47] | 16.541 | 16.687 | 2.21 [1.86, 2.56] | 16.193 [15.50, 16.88] | 2.07 | 783.6 [762, 800] | 65.20 | 28.85 | 6.12 |
| `fp32.lowrank2_w` | 2 | 24.505 [23.70, 25.31] | 24.555 | 24.596 | 3.14 [2.79, 3.49] | 23.797 [23.10, 24.50] | 2.95 | 706.9 [686, 728] | 65.39 | 29.04 | 6.15 |
| `fp32.real_pythia_gelu_down` | 1 | 22.290 [21.49, 23.09] | 22.185 | 22.370 | 2.88 [2.52, 3.23] | 21.646 [20.95, 22.34] | 2.70 | 726.4 [705, 748] | 65.56 | 29.21 | 6.17 |
| `fp32.real_pythia_ln1_q` | 1 | 22.079 [21.28, 22.88] | 21.999 | 22.154 | 2.85 [2.50, 3.21] | 21.442 [20.75, 22.14] | 2.67 | 728.3 [707, 750] | 65.56 | 29.21 | 6.17 |
| `fp32.sorted_k` | 1 | 23.023 [22.22, 23.83] | 23.010 | 23.053 | 2.96 [2.61, 3.32] | 22.358 [21.66, 23.06] | 2.78 | 719.8 [698, 741] | 65.53 | 29.18 | 6.17 |
| `fp32.wideexp48_bgate_alt` | 1 | 15.125 [14.30, 15.95] | 15.134 | 14.580 | 2.03 [1.68, 2.38] | 14.688 [13.97, 15.41] | 1.90 | 794.9 [774, 800] | 63.96 | 27.60 | 5.95 |
| `fp32.wideexp48_bgate_kblk` | 1 | 13.332 [12.54, 14.13] | 13.181 | 13.395 | 1.81 [1.46, 2.17] | 12.947 [12.26, 13.64] | 1.70 | 799.5 [778, 800] | 61.22 | 24.87 | 5.56 |
| `fp32.wideexp48_dense` | 1 | 25.657 [24.84, 26.47] | 25.729 | 25.813 | 3.28 [2.92, 3.63] | 24.916 [24.20, 25.63] | 3.08 | 696.9 [676, 718] | 65.31 | 28.96 | 6.14 |
| `fp16.anchor_randn` | 2 | 21.872 [21.34, 22.40] | 21.946 | 21.869 | 2.83 [2.52, 3.14] | 21.240 [20.63, 21.85] | 2.65 | 730.6 [709, 752] | 65.57 | 29.30 | 6.17 |
| `fp16.anchor_zeros` | 2 | 0.000 [-0.52, 0.52] | 0.000 | 0.000 | 0.23 [-0.08, 0.54] | 0.000 [-0.60, 0.60] | 0.20 | 800.0 [779, 800] | 36.27 | 0.00 | 2.07 |
| `fp16.exp_only` | 2 | 16.409 [15.86, 16.96] | 16.416 | 16.497 | 2.18 [1.87, 2.49] | 15.935 [15.31, 16.56] | 2.04 | 786.4 [765, 800] | 65.04 | 28.78 | 6.10 |
| `fp16.pair_cancel_asign` | 1 | 16.825 [16.30, 17.35] | 16.949 | 16.770 | 2.23 [1.92, 2.54] | 16.339 [15.73, 16.95] | 2.09 | 782.6 [761, 800] | 65.25 | 28.98 | 6.13 |
| `fp16.pair_nearcancel` | 1 | 21.797 [21.27, 22.33] | 21.877 | 21.788 | 2.82 [2.51, 3.13] | 21.167 [20.56, 21.78] | 2.64 | 731.3 [710, 753] | 65.57 | 29.30 | 6.17 |
| `fp16.real_pythia_ln2_up` | 1 | 22.088 [21.56, 22.62] | 22.155 | 22.090 | 2.85 [2.54, 3.16] | 21.450 [20.84, 22.06] | 2.67 | 728.7 [707, 750] | 65.57 | 29.30 | 6.17 |
| `fp16.real_pythia_qk` | 1 | 21.101 [20.57, 21.63] | 21.125 | 21.100 | 2.73 [2.42, 3.04] | 20.491 [19.88, 21.10] | 2.56 | 737.9 [717, 759] | 65.58 | 29.31 | 6.17 |
| `fp16.real_pythia_softmax_v` | 1 | 17.352 [16.83, 17.88] | 17.282 | 17.346 | 2.29 [1.98, 2.60] | 16.851 [16.25, 17.46] | 2.15 | 777.2 [756, 798] | 65.41 | 29.15 | 6.15 |
| `fp16.sparse24_aligned` | 1 | 12.786 [12.25, 13.32] | 13.045 | 12.805 | 1.75 [1.44, 2.06] | 12.417 [11.80, 13.03] | 1.63 | 799.8 [778, 800] | 60.16 | 23.89 | 5.41 |
| `fp16.sparse24_straddled` | 1 | 21.692 [21.16, 22.22] | 21.722 | 21.724 | 2.81 [2.50, 3.12] | 21.065 [20.45, 21.68] | 2.63 | 732.3 [711, 754] | 65.57 | 29.31 | 6.17 |
| `fp16.wideexp_bgate_alt` | 1 | 13.458 [12.89, 14.03] | 13.474 | 12.864 | 1.83 [1.52, 2.14] | 13.069 [12.43, 13.71] | 1.71 | 799.4 [778, 800] | 61.36 | 25.10 | 5.58 |
| `int8.a_word_flipflop` | 1 | 3.522 [2.95, 4.09] | 3.432 | 3.613 | 0.72 [0.32, 1.12] | 3.429 [2.79, 4.07] | 0.66 | 800.0 [779, 800] | 44.24 | 6.59 | 3.18 |
| `int8.anchor_full` | 2 | 6.997 [6.41, 7.58] | 6.961 | 6.951 | 1.13 [0.73, 1.53] | 6.811 [6.16, 7.46] | 1.05 | 800.0 [779, 800] | 50.74 | 13.09 | 4.10 |
| `int8.anchor_zeros` | 2 | 0.000 [-0.56, 0.56] | 0.000 | 0.000 | 0.30 [-0.10, 0.70] | 0.000 [-0.63, 0.63] | 0.27 | 800.0 [779, 800] | 37.65 | 0.00 | 2.26 |
| `int8.b_line_flipflop_nogate` | 1 | 6.346 [5.72, 6.98] | 6.618 | 6.607 | 1.05 [0.66, 1.45] | 6.177 [5.49, 6.87] | 0.98 | 800.0 [779, 800] | 49.52 | 11.87 | 3.92 |
| `int8.b_line_zero_one` | 1 | 3.959 [3.35, 4.57] | 3.902 | 3.884 | 0.77 [0.37, 1.17] | 3.854 [3.18, 4.53] | 0.71 | 800.0 [779, 800] | 45.06 | 7.40 | 3.30 |
| `int8.block_sparse_a` | 2 | 4.316 [3.75, 4.88] | 4.334 | 4.364 | 0.81 [0.41, 1.21] | 4.202 [3.56, 4.84] | 0.75 | 800.0 [779, 800] | 45.73 | 8.07 | 3.39 |
| `int8.gray_a` | 1 | 4.367 [3.73, 5.00] | 4.363 | 4.404 | 0.82 [0.42, 1.22] | 4.251 [3.55, 4.95] | 0.76 | 800.0 [779, 800] | 45.82 | 8.17 | 3.41 |
| `int8.powerlaw_w` | 2 | 6.376 [5.79, 6.96] | 6.402 | 6.387 | 1.06 [0.66, 1.46] | 6.207 [5.55, 6.86] | 0.98 | 800.0 [779, 800] | 49.58 | 11.92 | 3.93 |
| `int8.real_pythia_w8a8_down` | 1 | 6.189 [5.61, 6.77] | 6.223 | 6.215 | 1.04 [0.64, 1.44] | 6.025 [5.38, 6.67] | 0.96 | 800.0 [779, 800] | 49.23 | 11.58 | 3.88 |
| `int8.real_pythia_w8a8_up` | 1 | 6.143 [5.57, 6.72] | 6.148 | 6.162 | 1.03 [0.63, 1.43] | 5.980 [5.33, 6.63] | 0.96 | 800.0 [779, 800] | 49.14 | 11.49 | 3.87 |
| `int8.sorted_k` | 1 | 6.015 [5.42, 6.61] | 5.955 | 5.965 | 1.01 [0.62, 1.41] | 5.855 [5.19, 6.52] | 0.94 | 800.0 [779, 800] | 48.90 | 11.25 | 3.84 |

**Where the models disagree most** (D at 600 MHz on aifoundry3 and card 1, burst D on aifoundry2; descriptive, nothing fitted): aifoundry3 fp16: largest |M7 - M6| 0.258 W (`fp16.sparse24_aligned`), |M7 - M5| 0.594 W (`fp16.wideexp_bgate_alt`); aifoundry3 fp32: largest |M7 - M6| 0.172 W (`fp32.block_sparse_k4`), |M7 - M5| 0.545 W (`fp32.wideexp48_bgate_alt`); aifoundry3 int8: largest |M7 - M6| 0.273 W (`int8.b_line_flipflop_nogate`), |M7 - M5| 0.261 W (`int8.b_line_flipflop_nogate`); aifoundry1c1 fp16: largest |M7 - M6| 0.251 W (`fp16.sparse24_aligned`), |M7 - M5| 0.577 W (`fp16.wideexp_bgate_alt`); aifoundry1c1 fp32: largest |M7 - M6| 0.167 W (`fp32.block_sparse_k4`), |M7 - M5| 0.530 W (`fp32.wideexp48_bgate_alt`); aifoundry1c1 int8: largest |M7 - M6| 0.265 W (`int8.b_line_flipflop_nogate`), |M7 - M5| 0.254 W (`int8.b_line_flipflop_nogate`); aifoundry2 fp16: largest |M7 - M6| 0.470 W (`fp16.sparse24_aligned`), |M7 - M5| 1.070 W (`fp16.wideexp_bgate_alt`); aifoundry2 fp32: largest |M7 - M6| 0.310 W (`fp32.block_sparse_k4`), |M7 - M5| 0.710 W (`fp32.wideexp48_bgate_alt`); aifoundry2 int8: largest |M7 - M6| 0.510 W (`int8.b_line_flipflop_nogate`), |M7 - M5| 0.490 W (`int8.b_line_flipflop_nogate`).

**aifoundry2 (E143): governed against 800 MHz.** M7 puts 19 of the 36 tiles below 795 MHz in a 6 s burst (696.9 MHz, `fp32.wideexp48_dense`, up to 794.9, `fp32.wideexp48_bgate_alt`; 14 of them priority 1) and 17 at 795-800 MHz (all 11 int8 tiles and `fp16.wideexp_bgate_alt`, `fp32.wideexp48_bgate_kblk`, `fp16.sparse24_aligned`, `fp32.block_sparse_k4`, `fp16.anchor_zeros`, `fp32.anchor_zeros`). At 800 MHz a burst does not test the clock term. M7's verifier asks that E143 report the governed tiles and the 800 MHz ones separately, with the frozen bands unchanged.

## Checks

1. **M7 is committed and unchanged.** `3a210f2b` is on `origin/main` (19:21:05 PST). Each of its 14 files hashes the same in the working tree as in the commit when checked (twelve of them at 19:25, all 14 again at 20:19), and the six listed in its README's Files (`m7.json` `bfeea822...b8b2`, `fit_m7.py` `cb01d826...55c0`, `predict_blind5.py` `0d114d5b...c369`, `loko-m7.json`, `rows-m7.json`, `heat-rows-m7.json`) match that list. What it imports is unchanged since: Q137(m)'s `fit_m6.py`, `m6_rows.py`, `m6.json` (frozen at `6a713a9f`), Q133(b)'s `fit_m5.py`, `m5.json` (`64b4124e`), `tools/claims-v3/e119/make_predictions_e119.py`, Q137(m)'s `counts-blind4.json`. M7's self-test, rerun here (`selftest_predict_blind5.py`), passes with output identical to the committed `selftest-predict-blind5.txt`: the predictor runs on all three cards and reproduces M6's and M5's frozen pool-4 predictions exactly.
2. **The pool is the designer's, byte for byte.** 56 of 56 files identical to Q138(b)'s (sha256 each, and `diff -r`); `SHA256SUMS` 55 of 55 OK (its sha256 `ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6`); the manifest `blind5.json` `946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d`, every tile 36 of 36 matching its `sha256.whole`, `a` (first 1,024 B) and `b` (last 1,024 B), 2,048 B each. `make_blind5.py --check`, run before anything was added: "check: 37 built files, 0 problems".
3. **After the additions** the pool's 56 files are still identical (36 of 36 tiles, `SHA256SUMS` 55 of 55). `make_blind5.py --check` then prints: "MISMATCH SHA256SUMS"; "check: 37 built files, 1 problems". That is the designer's check comparing `SHA256SUMS` with every file now in the directory, this lane's additions included (pool 4's `make_blind4.py` does the same since its predictions were added beside it). Run on a copy holding the pool's 56 files only, taken from the tree after the additions, it prints "check: 37 built files, 0 problems".
4. **The predictions are the frozen model's.** Every predictions file records the sha256 of the frozen files it read, and they are the committed ones (Files, below). Run again into a scratch directory, the predictor writes all six files byte for byte. An independent recompute of M7's D, its band, the die rise and its band from each tile's recorded features with `m7.json`'s constants (k x sqrt(pool^2 + s^2 x'Cx); k_h x pool_h; aifoundry2's half-widths), written by M7's verifier, agrees to the files' rounding on all three cards (largest difference 0.0005).

## The bench's counts

[`counts-blind5.json`](counts-blind5.json) (sha256 `f1d42e6ca8f6b78154d43f82271474000c22960bd1d6924b75d4de1a300ce96c`): 36 rows for the 36 tiles, keyed `type.name` as the manifest names them, from rtl-sim/fma_toggle_v2's `run_kinds.py` at the three launch points of a 0.5 s launch, with the same build and maps that counted M5's, M6's and M7's rows and pool 4 (Q133(b)'s build; Q137(m) counted pool 4 with it the same way). Every row passed the bench's functional check (C against software at all 256 words) at every point. Run 19:28:48-20:18:01 PST, 5 jobs at nice 10.

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

From the top of the tree unless said. The bench runs in a build of `rtl-sim/fma_toggle_v2` (Q133(b)'s README, section Rerun: `make ... obj_vpu/Vtb accum settle_count`, then `train_maps.py ... --out maps`); `<repo>` is this tree's absolute path. The python for `run_kinds.py` needs no numpy (here macOS's `/usr/bin/python3`, 3.9); the one for the predictor has numpy (here Python 3.15.2, numpy 2.5.4).

```
# 1. the pool, from Q138(b)'s scratch, unchanged
cp -Rp <Q138(b) pool dir>/. tools/claims-v3/kinds/blind5/
(cd tools/claims-v3/kinds/blind5 && shasum -a 256 -c SHA256SUMS)          # 55 OK
python3 tools/claims-v3/kinds/blind5/make_blind5.py --check               # before the additions: 37 built files, 0 problems
# 2. the bench, in its build dir; EXTRA = for each tile of blind5.json in order, <type>:<name after 'type.'>:<repo>/tools/claims-v3/kinds/blind5/<file>, comma-joined
nice -n 10 python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds <repo>/tools/claims-v3/kinds \
  --out counts-blind5.json --only __none__ --extra-tiles "$EXTRA" --jobs 5 --tmp <tmp dir> --keep-going
cp counts-blind5.json <repo>/tools/claims-v3/kinds/blind5/counts-blind5.json
# 3. the predictions: predict_blind5.py writes predictions-<card>.json/.md; this lane renames them predictions-blind5-<card>.*
for card in aifoundry3 aifoundry1c1 aifoundry2; do
  python3 docs/reports/data/2026-11-02-q138m-model/predict_blind5.py tools/claims-v3/kinds/blind5 $card --counts tools/claims-v3/kinds/blind5/counts-blind5.json
  mv tools/claims-v3/kinds/blind5/predictions-$card.json tools/claims-v3/kinds/blind5/predictions-blind5-$card.json
  mv tools/claims-v3/kinds/blind5/predictions-$card.md tools/claims-v3/kinds/blind5/predictions-blind5-$card.md
done
```

Rerunning step 3 on these files reproduces the predictions byte for byte (the predictor run again after the first run, with `--out` to a scratch directory: all six files byte-identical).

## Order (PST, Mon 2 Nov 2026)

1. 19:21:05 Q138(m) commits and pushes M7 (`3a210f2b`). Pool 5 is not in the tree.
2. 19:25 This lane checks M7: on `origin/main`; its files unchanged (twelve hashed then, all 14 again at 20:19); what it imports unchanged.
3. 19:27:43 Pool 5 copied from Q138(b)'s scratch into this directory: 56 of 56 files identical, `SHA256SUMS` 55 of 55, manifest 36 of 36.
4. 19:28:48 The bench starts on the 36 tiles.
5. 19:29:00-19:29:10 `make_blind5.py --check` in the tree, before any addition: 37 built files, 0 problems.
6. 19:31:31-19:31:40 M7's self-test rerun here: PASS, its output identical to the committed one.
7. 20:18:01 The bench ends: 36 rows, no failure, `check_mismatch` 0 at every point.
8. 20:18:24-20:18:30 The predictions for the three cards, renamed `predictions-blind5-<card>.*`.
9. 20:19-20:25 The rerun into scratch (byte-identical), the pool checked again beside the additions, `--check` on the pool alone, the independent recompute, this README.
10. Then: committed and pushed through the lab's commit script, before any E141-E143 claim. That commit is the gate each card lane checks.

## What this cannot say

- **Nothing here is a measurement or a score.** The predictions are frozen; E141, E142 and E143 measure the tiles and score them by their own registered rules.
- **The band text in each file is stale** (rule A's words, rule B's numbers): see Results. A reader should take the bands as the numbers in the file, and the rule as Q138(m)'s README section 3 states it.
- **M5 has no heat term**, and M5 and M6 have no clock term: on aifoundry2 all three models go through M7's governor relation, so their clocks differ only through their D. Where the predicted burst reaches aifoundry2's effective cap, the board power is the cap for every model and the models differ in clock alone.
- **The three zeros anchors are byte-identical** (one tile under three type names, the designer's note); each is predicted under its own type. The anchors' D is near zero by construction (the bench counts are taken relative to the zeros' counts).
- The counts are the public RTL bench's (int8's multiply is behavioural there, and int8 bits/op stay provisional, `../README.md` 1.2).

## Files

| file | what | sha256 |
|---|---|---|
| [`README.md`](README.md), [`blind5.json`](blind5.json), [`SHA256SUMS`](SHA256SUMS), [`make_blind5.py`](make_blind5.py), [`fetch_real.py`](fetch_real.py), `real/`, `tiles/` | Q138(b)'s pool, unchanged (56 files) | manifest `946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d`; `SHA256SUMS` `ccfab045912309fbdf19ba8f0d0b13b56f364e10ce4ffeb757fe365e1fc748a6` |
| [`counts-blind5.json`](counts-blind5.json) | the bench's counts for the 36 tiles | `f1d42e6ca8f6b78154d43f82271474000c22960bd1d6924b75d4de1a300ce96c` |
| [`predictions-blind5-aifoundry3.json`](predictions-blind5-aifoundry3.json), [`.md`](predictions-blind5-aifoundry3.md) | M7, M6, M5 on aifoundry3 (E141) | `396d336015664c46f6d181440059023d980df57e07f6e47206b3700283ab9bf1`, `5e3caa1798639ae947c79749243885be0b9ba1a5a3536acc658a12006e160ac1` |
| [`predictions-blind5-aifoundry1c1.json`](predictions-blind5-aifoundry1c1.json), [`.md`](predictions-blind5-aifoundry1c1.md) | M7, M6, M5 on aifoundry1c1 (E142) | `87d0ffd2299b29d52a361cff02da563aea3ebcab507784fc678c09f992d36515`, `4f4d10fafd37e16cbf8b72b1c1f1d529099589f576df0e6d2a1acaabe2073225` |
| [`predictions-blind5-aifoundry2.json`](predictions-blind5-aifoundry2.json), [`.md`](predictions-blind5-aifoundry2.md) | M7, M6, M5 on aifoundry2 (E143) | `596ec0754fb2abd95ac85604b497338fd3a7c8759078470a023a1b0c0726632b`, `6ea7f8dd7bd94e3de7c31dcc41f4ea8562c6dabbcbb18aa56aaa32f15e6e591f` |

Every predictions file records the hashes of what it read: `m7.json` `bfeea822b87e0a1f8c315809192faf0a437b72bcadd1459c027cd857c8b3d8b2`, `m6.json` `87c17e086ee36699d7bb96609c02c471b5ba6b7bcdc20ead576d26f89e136e82`, `m5.json` `c19f2c7bc098b5a8969694b6563784d57bf88e7336fe97ac2afe769b0c63e2da`, the manifest `946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d`, the counts `f1d42e6ca8f6b78154d43f82271474000c22960bd1d6924b75d4de1a300ce96c`, `predict_blind5.py` `0d114d5bc01e317de2b5d1adef3cb71f01d0ecfc3ebad0ff7abe342f06bac369`, `fit_m7.py` `cb01d82684be3aa49e4e00b5a9a453c27603cd0612a2993af7775835f5bc55c0`.

*Commits: M5 `64b4124e` (Q133(b)), M6 `6a713a9f` (Q137(m)), M7 and `predict_blind5.py` `3a210f2b` (Q138(m)); this directory, the counts and the predictions: the commit that adds this README (Q138(x)).*
