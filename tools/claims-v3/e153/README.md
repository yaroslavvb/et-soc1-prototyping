# E153: blind pool 6 on aifoundry3 card 0 - M8's power and heat, frozen before the claim, scored on Q139(u)'s one footing, every launch's C checked, with the C-checked re-run of 6 pool-5 tiles first (Q139, 600 MHz)

*Pre-registered Tue 3 Nov 2026 (week 45), PST, on the Intel, in Q139 (lane `a3-e153-blind6`), before the claim of aifoundry3 and before any
launch of blind pool 6 on any 600 MHz card. The owner's mandate of Mon 2 Nov 2026, about 18:40 PST, carried: "settle any unanswered
questions regarding horace's power model", with Q137's goal, "to predict the power requirement and heat generation of various kinds of
numeric computations as accurately as possible". **It answers item 6 of the kinds page's section 11**, "a power model across kinds"
([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), and three ranks of
Q138's final critic: **rank 2** (M8, "scored on a sixth blind pool on all three cards"; this is the aifoundry3 card), **rank 5** (the card
scale, as predicted) and **rank 14** ("no file tile's results are checked": the re-run of 6 pool-5 tiles with C checked, sub-rule K1, and the
check of C on every pool-6 launch), with **rank 8**'s real-tile sub-rule carried by the pool. An earlier attempt of this lane prepared most of
these files in the morning and died at about 07:46 PST on a usage limit before it registered, claimed or launched anything; every file here was
re-read, re-run and re-checked against git and the box tonight (16:00-16:40 PST), and the time gates are tonight's.
**Every prediction E153 scores is frozen elsewhere, before this was written**: the model M8
([`m8.json`](../../../docs/reports/data/2026-11-03-q139m-model/m8.json), Q139(m), `122da8b6`, 04:57:59 PST), blind pool 6
([`../kinds/blind6/`](../kinds/blind6/README.md), Q139(b)'s independent designer, copied unchanged into the tree with M8's, M7's and M6's
predictions by Q139(x), `d98d2e34`, 05:39:23 PST) and its aifoundry3 predictions
[`predictions-blind6-aifoundry3.json`](../kinds/blind6/predictions-blind6-aifoundry3.json) (`97247642…`). E153 adds no prediction. What it adds
is frozen in [`predictions-e153.json`](predictions-e153.json), written by [`make_predictions_e153.py`](make_predictions_e153.py) from the
committed files it names (each checked by sha256): the plan, the stops, the rules, the reference errors behind them and the hash of every
file the box runs. Any change after this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry3 card 0 only** (no
`V3_DEVICE`, `/run/lock/etsoc-shire0.lock`), 600 MHz as its boot-time TDP of 0 latches it, TDP 0 W and threshold 65 °C as read, never set.
**E153 sends no write command of any kind** (§ Device commands sent).*

## What it does to predicting power and heat

M8 predicts, from the bytes a matmul multiplies, its **power** D (board W over the type's own zeros at 600 MHz) and its **heat** (the die's
rise over a 4.5 s kinds run). On aifoundry3 M8's power has no card scale (its units are this card on Q139(u)'s footing) and its heat is M7's
law, carried (0.1186 °C per board W on this card). **The terms under test** are M8's two new ones (the C register's flips for the floats,
6.44 ± 2.05 fJ a flip; a discount on int8 B bytes that flip 7 or 8 bits, −56.8 ± 29.4 fJ a bit), its constants refitted on the one footing,
and the card scale (1 on this card by definition; card 1's 0.9616 is scored jointly with E157). **Before** (the error M8 claims for a new kind,
nested leave one kind out, `nested-m8.json`, reproduced row by row by [`ref_errors_e153.py`](ref_errors_e153.py)): on aifoundry3's rows fp32
**0.193 W** (225 rows), fp16 **0.147 W** (113), int8 **0.244 W** (73); over both cards floats 0.182 W and int8 0.241 W. Heat on aifoundry3
0.181 / 0.159 / 0.205 °C (fp32 / fp16 / int8; M7's pools, `m8.json` › `heat`). The last blind test on this card, M7 on pool 5 (E141), read
0.325 / 0.317 / 0.356 W at its own session footing with the floats 0.23 W too high (B1 FAIL HIGH), and post hoc on Q139(u)'s footing 0.146 /
0.149 / 0.336 W (`docs/reports/data/2026-11-03-q139u-footing/scores-m7u.json`); heat 0.128 / 0.129 / 0.135 °C. **After**: pool 6's blind
error on this card by format, for power and heat, its bias, the share inside M8's frozen 95% bands, M8 against M6 and M7 on the same tiles,
and whether every launch's C is right. E153's reduction also gives E157 and E160 the aifoundry3 D that their card-scale rules divide by.

## The question

1. **Is every C right?** On the 6 pool-5 tiles re-run first (K1, rank 14) and on every pool-6 launch (KC): bit-exact against Q139(k)'s
   reference. And does a C-logging host reproduce E141's D on the same tiles (K1-D, K1-W)?
2. **Is M8's power on a blind pool, on the card its units are, as accurate as its nested score says?** Per format: P1 fp32, P2 fp16, P3 int8.
3. **Is it unbiased?** Floats (B1), int8 (B2): the critic's "bias inside B1/B2".
4. **Do its frozen 95% bands cover?** Power (C1: the critic's "at least 26 of 30 new kinds inside M8's bands"), heat (H4).
5. **Is M8 better than M6, resolved?** (M1: the critic's "M8 minus M6 rms resolved below zero by a paired bootstrap over tiles"), and than M7 (M2).
6. **Is its heat as accurate?** Per format (H1-H3), the die rise over each run's window.
7. **Real tiles** (rank 8's sub-rule, all 12, pool 6's `CORRECTIONS.md` C9): rms within the pool's own (R1), no tile outside its band (R2).
8. **The card scale as predicted** (rank 5): this card's measured scale against M8's 1 (CS0); card 1's against M8's 0.9616 and the cheap reads
   (CS1, scored where E157's registered reduction exists).

## The models, the pool and the check, frozen elsewhere

| what | file | sha256 | frozen in |
|---|---|---|---|
| blind pool 6: 50 tiles (18 fp32, 13 fp16, 19 int8; 30 priority 1, 14 priority-2 tests, 6 anchors of its own), by an independent designer | [`blind6.json`](../kinds/blind6/blind6.json), `MANIFEST`, `SHA256SUMS`, `tiles/` | `4c4cee7b…`, `a0e91556…`, `8ab25920…` | `d98d2e34` (Q139(x); designed by Q139(b); its fix pass `e9d20985` changed no frozen file) |
| M8 (floats, int8, heat carried from M7) and its nested scores | [`m8.json`](../../../docs/reports/data/2026-11-03-q139m-model/m8.json), `nested-m8.json`, `rows-m8.json`, `fit_m8.py` | `8c23aba2…`, `f284b540…`, `6e3383ef…`, `3764bc4c…` | `122da8b6` (registration `f640fb7a`) |
| M8's, M7's and M6's predictions for pool 6 on aifoundry3: D and the die rise with 95% bands | [`predictions-blind6-aifoundry3.json`](../kinds/blind6/predictions-blind6-aifoundry3.json) | `972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f` | `d98d2e34` |
| the card scale per card from cheap reads (rank 5) | [`card-scale-blind6.json`](../kinds/blind6/card-scale-blind6.json) | `6b040791…` | `d98d2e34` |
| the one footing: aifoundry3's leakage slope **0.20563713796102187 W/°C** and E82 A2's dip rule; E141 re-reduced on it | [`footing.json`](../../../docs/reports/data/2026-11-03-q139u-footing/footing.json), [`reduce_footing.py`](../../../docs/reports/data/2026-11-03-q139u-footing/reduce_footing.py), `reduced/e141-footing.json` | `f589efaa…`, `8b2ef4ec…`, `74b36e68…` | rule `d4c36bfe` (04:02:21), slopes `f47669d1` |
| E141's committed reduction (its session's own footing) | [`e141.json`](../../../docs/reports/data/2026-11-02-e141-blind5-aifoundry3/e141.json) | `31b5d319…` | E141 |
| the check of C | [`../ccheck/`](../ccheck/README.md): `sparsity_ccheck.sh`, `patch_host_ccheck.py`, `build_host_ccheck.sh`, `ccheck.py`, `pick6.py` | `d00158d4…`, `05a8c867…`, `35537915…`, `2f806fe6…`, `b4b92dc1…` | `4946a992` (05:46:15, Q139(k) after its verification) |

`git merge-base --is-ancestor` holds for `d98d2e34`, `122da8b6` and `4946a992` against this commit, and this commit precedes the claim and the
first launch. **The band rule** is M8's (`m8.json` › `band_rule`, copied into the predictions file): power half-width k × √(pool² + s² xᵀCx),
**k 2.196 on the floats and 2.835 on int8**; heat k_h 1.95 × the card's pool. **M7 and M6 are scored beside M8 on the same tiles**, each with its
own frozen band (M7 k 3.179 / 2.483, M6 1.96). The predictions file's `D600_a3_footing_w` equals `D_w` on this card.

## K1 first: the C-checked re-run of 6 pool-5 tiles (rank 14)

**The tiles** are Q139(k)'s [`pick6.py`](../ccheck/pick6.py) picks, per format the two pool-5 tiles measured most tightly on both cards:
`fp32.b_exp_busy_a_const`, `fp32.real_pythia_ln1_q`, `fp16.sparse24_aligned`, `fp16.exp_only`, `int8.gray_a`, `int8.b_line_zero_one`, their
files and sha256 unchanged from `../kinds/blind5/` (byte-identical on the box, checked tonight). **They run inside every pool-6 pass**, in
E141's frame (E78's protocol, E78's six anchors three times a pass, the tie first and last), so their D stands on the same zeros and the same
passes as pool 6's; "first" is the order of the rules: K1 is scored first, and its verdict decides whether pool 5's rows (and so every model's
file-tile training rows) stand as measured. **The comparison values**, from E141's committed reductions (copied into `predictions-e153.json` ›
`k1`):

| K1 tile (pool 5) | E141 D, its own session footing (passes) | E141 D on Q139(u)'s footing (passes) | se on the footing |
|---|---|---|---|
| `fp32.b_exp_busy_a_const` | 15.393 ± 0.080 (3) | 15.498 ± 0.057 (4) | 0.0180 |
| `fp32.real_pythia_ln1_q` | 21.964 ± 0.153 (3) | 22.118 ± 0.078 (4) | 0.0245 |
| `fp16.sparse24_aligned` | 12.716 ± 0.120 (3) | 12.830 ± 0.068 (4) | 0.0213 |
| `fp16.exp_only` | 16.247 ± 0.172 (2) | 16.341 ± 0.082 (3) | 0.0189 |
| `int8.gray_a` | 4.034 ± 0.094 (3) | 4.100 ± 0.059 (4) | 0.0184 |
| `int8.b_line_zero_one` | 3.351 ± 0.137 (3) | 3.380 ± 0.060 (4) | 0.0189 |

**The rule as the critic wrote it** (`E153-K1`): every C "exact or within the format's rounding" **and** D within **±0.05 W** of E141's on each
of the 6 tiles, the same footing on both sides (primary: Q139(u)'s footing, against E141 as Q139(u) re-reduced it; beside: this session's own
footing against E141's own). **The check that decides "exact"** is Q139(k)'s registered verdict table, as its README's "exact use" says:
`K1-C` PASS only if every launch of the 6 tiles in a kept pass has a C record that `ccheck.py check` judges **PASS** (bit-exact against the
RTL's arithmetic; ROUNDING, UNMODELLED, FAIL and a missing record count as not checked, because at launch lengths fp16's rounding envelope
admits all-zero C, Q139(k) finding 1). The critic's looser reading, every launch PASS or ROUNDING, is reported beside. `K1-D` is the flat
±0.05 W on each tile. `K1-W` is Q139(k)'s same-card rule, |D_new − D_old| ≤ t₀.₉₇₅(ν)·√(se_new² + se_old²) with Welch's ν (`pick6.welch`), on
each tile; **K1′ = K1-C and K1-W** is registered beside K1. Q139(k)'s finding 2 says ±0.05 W is narrower than a same-card repeat's noise on 5
of the 6 picks, so K1-D can fail on noise alone; that is why K1′ is registered too, and why K1 and K1′ are both reported whatever they say.

**What a K1 failure does.** A C that is not PASS on a K1 tile says a pool-5 launch on that tile may have computed the wrong C: every pool-5 row
on that tile (or that format, if the failures are systematic) is named as suspect for the integration lanes, and the diagnostics say what
the C equals. K1-D or K1-W failing with K1-C passing says the C-logging host or the day moved D: it is reported per tile with the K1 tiles'
duty and the launch gaps, never "corrected".

## The frozen predictions

D in W over the type's own zeros, and the die rise over the run in °C, aifoundry3 card 0, 600 MHz; M8 with its 95% band (scored), M7 and M6
beside (reported), copied from `predictions-blind6-aifoundry3.json` into `predictions-e153.json` › `tiles` (checked field by field: 0
differ). Cases: 0 anchor, E exponent-heavy, B int8 B-position, L int8 whole-line / whole-word, W power-law weights, R real model tiles, Z zeros'
transport, S single bits on other base words, C the C-register candidate; H the four hold candidates for E154.

| tile | case | prio | H | M8 D, W [95%] | M7 D | M6 D | M8 die rise, °C [95%] |
|---|---|---|---|---|---:|---:|---|
| `fp32.a_onebit_b5_third` | S | 1 | H | **9.45** [9.02, 9.87] | 9.39 | 9.34 | **1.35** [1.00, 1.71] |
| `fp32.a_zeros_b_complement` | Z | 1 |  | **1.54** [1.09, 1.98] | 1.54 | 1.78 | **0.42** [0.06, 0.77] |
| `fp32.b_onebit_b12_third` | S | 1 |  | **9.85** [9.43, 10.28] | 9.82 | 9.80 | **1.40** [1.05, 1.76] |
| `fp32.b_onebit_b20_third` | S | 1 |  | **13.75** [13.32, 14.18] | 13.74 | 13.64 | **1.86** [1.51, 2.22] |
| `fp32.bf16_wideexp` | E | 1 |  | **19.42** [18.98, 19.86] | 19.46 | 19.51 | **2.54** [2.18, 2.89] |
| `fp32.exp_a_walk_fixedmant` | E | 1 |  | **12.62** [12.19, 13.05] | 12.65 | 12.67 | **1.73** [1.38, 2.08] |
| `fp32.exp_b_alt_shift` | E | 1 |  | **16.05** [15.61, 16.49] | 16.09 | 16.03 | **2.14** [1.78, 2.49] |
| `fp32.exp_only_narrow2` | E | 1 |  | **14.99** [14.56, 15.43] | 14.97 | 14.96 | **2.01** [1.66, 2.37] |
| `fp32.negzero_a_b_complement` | Z | 1 |  | **16.67** [16.22, 17.12] | 16.74 | 17.26 | **2.21** [1.86, 2.56] |
| `fp32.real_qwen_dequant_q` | R | 1 |  | **20.29** [19.86, 20.72] | 20.21 | 20.10 | **2.64** [2.29, 2.99] |
| `fp32.real_smol_softmax_v_causal` | R | 1 | H | **13.69** [13.27, 14.12] | 13.63 | 13.55 | **1.86** [1.50, 2.21] |
| `fp32.signexp_invert_b` | E | 1 |  | **17.08** [16.62, 17.53] | 17.14 | 16.95 | **2.26** [1.91, 2.61] |
| `fp32.a_onebit_b16_half` | S | 2 |  | **9.68** [9.25, 10.11] | 9.65 | 9.63 | **1.38** [1.03, 1.74] |
| `fp32.c_absorbed` | C | 2 |  | **19.96** [19.53, 20.40] | 19.89 | 20.01 | **2.60** [2.25, 2.96] |
| `fp32.exp_a_pow2wide_b_randn` | E | 2 |  | **19.16** [18.72, 19.60] | 19.19 | 19.49 | **2.51** [2.15, 2.86] |
| `fp32.real_qwen_softmax_v` | R | 2 |  | **24.26** [23.82, 24.69] | 24.12 | 24.08 | **3.11** [2.76, 3.46] |
| `fp32.anchor6_randn` | 0 | anchor |  | **24.73** [24.30, 25.16] | 24.60 | 24.64 | **3.17** [2.81, 3.52] |
| `fp32.anchor6_zeros` | 0 | anchor |  | **0.00** [-0.42, 0.42] | 0.00 | 0.00 | **0.23** [-0.12, 0.59] |
| `fp16.e5m2grid_wide` | E | 1 |  | **17.92** [17.58, 18.26] | 17.94 | 17.97 | **2.36** [2.05, 2.67] |
| `fp16.exp_b_alt_shift` | E | 1 |  | **15.53** [15.19, 15.86] | 15.53 | 15.40 | **2.07** [1.76, 2.38] |
| `fp16.exp_only_narrow2` | E | 1 |  | **15.91** [15.57, 16.25] | 15.87 | 15.85 | **2.12** [1.81, 2.43] |
| `fp16.real_qwen_qk` | R | 1 |  | **19.01** [18.68, 19.34] | 18.95 | 18.91 | **2.49** [2.18, 2.80] |
| `fp16.real_smol_qk` | R | 1 |  | **21.56** [21.23, 21.90] | 21.47 | 21.48 | **2.79** [2.48, 3.10] |
| `fp16.real_smol_softmax_v` | R | 1 |  | **17.55** [17.22, 17.88] | 17.48 | 17.39 | **2.31** [2.00, 2.62] |
| `fp16.a_zeros_b_complement` | Z | 2 |  | **1.52** [1.17, 1.87] | 1.52 | 1.60 | **0.41** [0.10, 0.72] |
| `fp16.b_onebit_b6_third` | S | 2 |  | **12.73** [12.40, 13.06] | 12.69 | 12.59 | **1.74** [1.43, 2.05] |
| `fp16.c_absorbed` | C | 2 |  | **19.86** [19.53, 20.20] | 19.84 | 19.91 | **2.59** [2.28, 2.90] |
| `fp16.exp_a_walk_fixedmant` | E | 2 |  | **12.50** [12.18, 12.83] | 12.50 | 12.52 | **1.72** [1.41, 2.02] |
| `fp16.real_qwen_dequant_v` | R | 2 |  | **21.88** [21.54, 22.21] | 21.79 | 21.85 | **2.83** [2.52, 3.14] |
| `fp16.anchor6_randn` | 0 | anchor |  | **22.07** [21.74, 22.41] | 21.97 | 22.04 | **2.85** [2.54, 3.16] |
| `fp16.anchor6_zeros` | 0 | anchor |  | **0.00** [-0.32, 0.32] | 0.00 | 0.00 | **0.23** [-0.08, 0.54] |
| `int8.a_word_zero_one` | L | 1 |  | **2.86** [2.14, 3.58] | 2.78 | 2.69 | **0.64** [0.24, 1.04] |
| `int8.a_zeros_b_lineflip` | Z | 1 |  | **-0.34** [-1.73, 1.05] | 0.05 | 0.51 | **0.26** [-0.14, 0.66] |
| `int8.b_line_zero_ff` | L | 1 | H | **3.39** [2.17, 4.61] | 3.70 | 4.10 | **0.70** [0.30, 1.10] |
| `int8.b_line_zero_full` | L | 1 |  | **4.24** [3.52, 4.96] | 4.07 | 4.18 | **0.80** [0.41, 1.20] |
| `int8.bheld_bit1` | B | 1 |  | **6.18** [5.38, 6.99] | 6.21 | 6.05 | **1.03** [0.64, 1.43] |
| `int8.bheld_bit4` | B | 1 |  | **5.86** [5.06, 6.65] | 5.88 | 5.73 | **1.00** [0.60, 1.40] |
| `int8.bheld_bit7` | B | 1 |  | **5.51** [4.74, 6.29] | 5.54 | 5.40 | **0.96** [0.56, 1.35] |
| `int8.powerlaw_df4_pc` | W | 1 |  | **6.76** [6.05, 7.47] | 6.75 | 6.75 | **1.10** [0.70, 1.50] |
| `int8.real_qwen_w8a8_gate` | R | 1 |  | **6.73** [6.02, 7.44] | 6.69 | 6.69 | **1.10** [0.70, 1.50] |
| `int8.real_qwen_w8a8_v` | R | 1 | H | **6.69** [5.98, 7.41] | 6.69 | 6.70 | **1.10** [0.70, 1.49] |
| `int8.real_smol_w8a8_down` | R | 1 |  | **5.44** [4.73, 6.14] | 5.34 | 5.31 | **0.95** [0.55, 1.34] |
| `int8.real_smol_w8a8_q` | R | 1 |  | **6.55** [5.83, 7.26] | 6.47 | 6.49 | **1.08** [0.68, 1.48] |
| `int8.b_line_55_aa` | L | 2 |  | **6.10** [4.84, 7.36] | 6.59 | 6.85 | **1.02** [0.63, 1.42] |
| `int8.bflip_bit2_w` | B | 2 |  | **2.16** [1.40, 2.92] | 2.21 | 2.13 | **0.56** [0.16, 0.96] |
| `int8.bflip_bit5_w` | B | 2 |  | **2.16** [1.41, 2.92] | 2.17 | 2.13 | **0.56** [0.16, 0.96] |
| `int8.powerlaw_df15_pt` | W | 2 |  | **2.67** [1.95, 3.39] | 2.65 | 2.63 | **0.62** [0.22, 1.02] |
| `int8.real_qwen_w8a8_down` | R | 2 |  | **6.15** [5.43, 6.86] | 6.03 | 6.07 | **1.03** [0.63, 1.43] |
| `int8.anchor6_full` | 0 | anchor |  | **7.03** [6.31, 7.74] | 7.01 | 6.97 | **1.14** [0.74, 1.53] |
| `int8.anchor6_zeros` | 0 | anchor |  | **0.00** [-0.69, 0.69] | 0.00 | 0.00 | **0.30** [-0.10, 0.70] |

## Decision rules

**The registered primary reduction is Q139(u)'s one footing** ([`FOOTING-RULE.md`](../../../docs/reports/data/2026-11-03-q139u-footing/FOOTING-RULE.md)
F1-F3, for E141's wrapper type, as `reduce_footing.reduce` runs E141): E78's `reduce_e78.py` unchanged through [`reduce_e153.py`](reduce_e153.py)
`--leak 0.20563713796102187 --no-refit --drop-dips` (aifoundry3's frozen slope, read through `reduce_footing.K_FROZEN["a3"]` by the collector,
which refuses on any other value; E82 A2's dip rule applied once), E78's run and pass gates and its aifoundry3 config gate. That is M8's own
footing. **E141's session-own footing** (leakage `auto`, fitted on this session; dips kept: E141's registered primary) **is reduced and scored
with every rule beside it, never the verdict.** A tile's measured value is its mean over the kept passes it ran in; a tile with fewer than 2
is left out and named. **Fewer than 2 kept passes: every rule NOT SCORED.** Reference errors: M8's nested leave-one-kind-out error of every
**aifoundry3** row of the format (`ref_errors_e153.py` → [`ref-errors-m8.json`](ref-errors-m8.json): Q139(m)'s own `fit_m8.run_family`,
unchanged, on the committed `rows-m8.json`; every pool's n and rms equal `nested-m8.json`'s to 1e-9 W; 225 fp32, 113 fp16, 73 int8 rows),
copied into `predictions-e153.json` › `reference_errors.power_a3`; heat: a deterministic normal sample of 2,000 points with M8's (M7's) nested
aifoundry3 heat rms of the format (0.181, 0.159, 0.205 °C), as E141 did. Bootstrap: 20,000 draws, seed 15300 plus the rule's characters
([`score_e153.py`](score_e153.py)).

| rule | quantity | set | verdict |
|---|---|---|---|
| **E153-K1** | the C-checked re-run (rank 14) | the 6 K1 tiles | **PASS** if K1-C (every launch PASS) and K1-D (\|D − D_E141\| ≤ 0.05 W on each tile, same footing both sides); else FAIL; NOT SCORED if a K1 tile has fewer than 2 kept passes or no C check |
| E153-K1′ | the same, Q139(k)'s interval | the 6 K1 tiles | K1-C and K1-W (inside Welch's same-card 95% interval on each tile) |
| **E153-KC** | the C check | every pool-6 tile | **PASS** if every measured launch of every pool-6 tile in a kept pass has a C record (same `t_start_ms`, `t_end_ms`) that `ccheck.py check` judges PASS; a tile with any launch not PASS **leaves the scored set of every rule below** (named; the rules are also given over all tiles beside) |
| **E153-P1** | power D | priority-1 fp32 (12), at least 6 | rms(D − M8) against the 2.5–97.5% range of the rms of 12 draws with replacement from M8's aifoundry3 fp32 reference errors: **PASS** at or below the 97.5% point, **FAIL** above; below the 2.5% point is reported as "better than the nested score says" |
| **E153-P2** | power D | priority-1 fp16 (6), at least 4 | as P1, fp16's |
| **E153-P3** | power D | priority-1 int8 (12), at least 6 | as P1, int8's |
| **E153-B1** | bias | priority-1 floats (18), at least 8 | mean(D − M8) against the 2.5–97.5% range of the mean of as many draws (the same format mix): **PASS** inside; **FAIL HIGH** below it (M8 predicts too much), **FAIL LOW** above it |
| **E153-B2** | bias | priority-1 int8 (12), at least 6 | as B1 |
| **E153-C1** | power coverage | the 30 priority-1 new kinds | **PASS** if the number inside M8's frozen 95% band is at least the 2.5% point of Binomial(n, 0.95) (**26 of 30**), **FAIL** if fewer; NOT SCORED under 10 |
| **E153-M1** | M8 against M6 | the 30 priority-1 new kinds | d = rms(M8's errors) − rms(M6's), 95% interval by a paired bootstrap over tiles: **BETTER** (the critic's PASS) if its upper bound < 0, **WORSE** if its lower bound > 0, else **NOT RESOLVED** |
| **E153-M2** | M8 against M7 | the same 30 | as M1 |
| **E153-H1** | die rise `dT_win` | priority-1 fp32 (12), at least 6 | rms(dT − M8) against the 2.5–97.5% range of the rms of 12 draws from the normal reference (0.181 °C): PASS / FAIL as P1 |
| **E153-H2** | die rise | priority-1 fp16 (6), at least 4 | as H1 (0.159 °C) |
| **E153-H3** | die rise | priority-1 int8 (12), at least 6 | as H1 (0.205 °C) |
| **E153-H4** | heat coverage | the 30 priority-1 new kinds | as C1, M8's frozen dT band (26 of 30) |
| **E153-R1** | real tiles (rank 8) | all 12 real tiles (priority 1 and 2; `CORRECTIONS.md` C9), at least 8 | rms(D − M8) at or below the 97.5% point of the rms of 12 draws (the same format mix) from the errors of the pool's own non-real new kinds in this session: **PASS**, else **FAIL** |
| **E153-R2** | real tiles | all 12 | **PASS** if every measured real tile is inside M8's frozen 95% band, else **FAIL** (if the bands are exact, all 12 inside has probability 0.54) |
| **E153-CS0** | card scale, this card (rank 5) | pool-6 tiles with D ≥ 5 W (floats) or ≥ 1 W (int8), measured and predicted | the median of D / M8's D over them (a bootstrap 95% interval beside), per format family, within **1%** of M8's applied 1.0: **PASS**, else **FAIL**; the cheap-read predictions for aifoundry3 held out (`card-scale-blind6.json`) reported beside |
| **E153-CS1** | card scale, card 1 (rank 5, with E157) | the same tiles, D ≥ 5 W / 1 W on both cards | median of D_card1 / D_E153 within 1% of M8's 0.9616 (floats and int8): PASS, else FAIL; each cheap read within 1% of the measured scale, reported; **NOT SCORED here unless E157's registered-primary reduction exists at collection** (E157 or the integration scores it then) |

**Reported, never a verdict** (`scored.json`, `results.md`): every rule on E141's session-own footing and at every arm (leakage auto with dips
removed; the frozen slope with dips kept; leakage 0.1994, 0.3803 and 0 W/°C with dips removed; the pass gates opened); M7's and M6's rms,
bias and coverage beside M8's on every set, per format and by case; the 14 priority-2 tests and all 44 new kinds together (rms, coverage,
paired M8 − M6); every rule over all tiles if the C check removes any; each K1 tile on both footings with the flat 0.05 W and Welch's
interval, and every launch's C verdict; `int8.a_zeros_b_lineflip`, which M8 puts below its zeros (−0.339 W [−1.73, +1.05]; M7 +0.049, M6
+0.505): the int8 near-whole-byte discount's most direct test; heat at the measured run length (M7's ST term, −0.0490 °C/W/s); the die rise
per board W against 0.1186 °C/W; P1-P3 against both cards' reference rows; E78's anchors and the tie against E141's on this card; the C
log's extra DMA (each run's duty and the launch gaps against E141's).

**Why these lines, before the data.** They are E141's on this card (themselves E142's, E140's and E115's), with M8 in M7's place and the
critic's rank-2 rules (paired M8 − M6, bias inside B1/B2, 26 of 30) and rank 8's and rank 5's added, so the blind tests of pools 5 and 6 on this
card read alike. The reference rows are this card's because M8's bands are per card.

## Precision, before the data

[`planned-intervals.txt`](planned-intervals.txt), at the registered draws: **P1** 0.094–0.285 W (median 0.185) over 12 fp32 kinds; **P2**
0.048–0.253 W (median 0.129) over 6 fp16; **P3** 0.135–0.356 W (median 0.235) over 12 int8; **B1** −0.108 to +0.053 W; **B2** −0.192 to
+0.079 W; **H1** 0.110–0.251 °C; **H2** 0.073–0.246 °C; **H3** 0.123–0.286 °C; C1 and H4 need 26 of 30 inside; R2 needs all 12. M8's frozen
95% power half-widths on the priority-1 kinds: fp32 0.43–0.45 W, fp16 0.33–0.34 W, int8 0.71–1.39 W; |M8 − M6| on them: median 0.110 W, max
0.844 W, so **M1 can resolve only where the two models differ**. [`selftest.txt`](selftest.txt) ([`selftest_e153.py`](selftest_e153.py), 40
simulated sessions a world on the frozen registration, three passes, 0.05 W / 0.05 °C pass noise, the bootstrap cut to 2,000 draws; nothing
there is a measurement): when M8 is as good as its nested score, P1–P3 PASS in 38–39 of 40, B1 36, B2 40, C1 40, H1–H3 38, H4 40, R1 37, **R2
25**, **CS0-int8 19** (int8's median ratio carries 1–7 W of D, so its 1% line fails half the time even then: a CS0-int8 FAIL says little), M1
BETTER in 29 and NOT RESOLVED in 11 (M8 right by construction); **twice as bad**, P1 FAILS in 31, P2 21, P3 33, C1 25, H1–H4 29–39; with a
−0.3 W bias on the floats, **B1 FAILS HIGH in 40 of 40** while P1 fails in 40 and C1 in 23. The C-check plumbing on stub files: every launch
PASS keeps every tile; one ROUNDING launch, or one launch with no C record, removes its tile from the scored set and fails KC.

**What I expect, frozen so it can be wrong:** KC and K1-C PASS (the kernel is unchanged and the reference reproduced all 110 of E104's card
reads); K1-D FAIL on at least one tile and K1-W PASS (the flat 0.05 W is narrower than a same-card repeat's noise, Q139(k) finding 2); P1–P3
PASS; B1 and B2 PASS (one footing for training and test); C1 PASS; M1 NOT RESOLVED and M2 NOT RESOLVED (M8's nested gain over M6 as frozen was
small, and the models differ by a median 0.11 W here); H1–H4 PASS; R1 PASS and R2 PASS or FAIL; CS0 PASS for the floats and PASS or FAIL
for int8. **The likeliest misses, named now:** the exponent-heavy kinds (case E: E147 found the card paying 0.82–0.84 of the models' watts on
single exponent flips, and M8 kept no exponent term), `int8.a_zeros_b_lineflip` (M8's near-whole-byte discount alone is −0.90 W there),
int8's whole-line kinds (case L) and the W8A8 real tiles (E141's steady misses), and fp16's two-term tiles (`fp16.real_smol_softmax_v`,
`fp16.real_qwen_dequant_v`: pool 6's `CORRECTIONS.md` C1); on heat, int8's small rises that the die's whole-degree readings floor.

**The statement the page gets, decided now.** All PASS: "on 44 new kinds written by a designer who never saw the model, every launch's C
checked bit for bit, M8 predicted power on aifoundry3 within X W rms (fp32), Y (fp16) and Z (int8) with no resolved bias, its 95% bands
covering K of 30, and the die's rise within … °C, as its nested score said; it was [not] resolved better than M6". A FAIL is stated with the
rms or bias, its interval and the tiles that carry it, by case. **No tile, prediction, band, rule or reference error changes after this
commit; only tiles that ran and passed the C check are scored.**

## What the rules cannot say

One card, one clock, one session. The heat scored is the 4.5 s window only. The heat reference is a normal model of the nested rms, not the
rows. A PASS fails to find a miss at this many tiles; it does not bound M8's error on kinds unlike these 50. A C PASS says the arithmetic
matched the RTL's model at every word of every participating minion; 36 of the 56 tiles carry first-read notes (below), so their launches
are those value ranges' first silicon reads and a FAIL there could be the model's.

## What runs

| | E141 (pool 5, this card, 2 Nov) | E153 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet | **the same**, every measured launch through Q139(k)'s wrapper `tools/claims-v3/ccheck/sparsity_ccheck.sh` (`--sparsity`), which runs the C-logging host `build/ccheck/b/host/sparsity_host` with **the power passes' kernel** `build/sparsity/kernel/sparsity.elf` and appends `--c-log <pass>/c-log.jsonl --c-poison`; the heater stays on E78's host | the protocol M8's aifoundry3 rows were measured with; rank 14's check |
| the tiles | pool 5's 36 | **pool 6's 50 and the 6 K1 tiles** (`tools/claims-v3/kinds/blind6/tiles/<type>/<name>.bin`, `…/blind5/tiles/…`) | |
| anchors | E78's six three times a pass, the tie `anchor_pi` first and last; the pool's anchors ordinary tiles | the same | drift, the zeros D is measured over |
| a pass | 56 runs | **76 runs**: the tie, three segments of the six anchors and 19, 19 and 18 of the 56 tiles, the tie; `Random("E153\|aifoundry3\|<pass>")` | |
| passes | 14110–14113 (574–623 s each), 3 kept | **15310–15312, 15313 if it fits** (the budget rule decides; 3 expected), at least 2 kept; **the registered subset is the first two passes** | 55 card-minutes |
| stop-path test | 14102 | **15302**, before the smoke, no launch: the guard's die stop (at 1.0 °C), its board stop (at 1.0 W) and the in-run watcher's board stop (at 1.0 W) must each end `run_e153.py` with EXIT_HOT on a live sample read at most 2.0 s after it was taken | registered stops read live samples |
| smoke | 14101 | **15301**: the tie, `fp32.zeros`, `fp32.randn`, `fp32.real_qwen_softmax_v` (pool 6's hottest non-anchor, M8 24.26 W), `fp32.anchor6_zeros`, `fp16.real_smol_softmax_v`, `fp16.zeros`, `int8.a_zeros_b_lineflip`, `int8.zeros`, `fp32.b_exp_busy_a_const` (a K1 tile), 2 s each, no preheat; gated by [`smoke_gate_e153.py`](smoke_gate_e153.py): E141's checks (records ok, cycles per op within 0.5%, 600 MHz, config 0 W / 65 °C / 600 MHz, dumped pool tiles equal their sha256, `since_reset_ms` −1, at least 100 live samples, board below the stop) plus **the C log** (a host record naming the registered C-logging host and kernel by sha256; a C record for every launch record, ok, poison on, mask and B stream off, at least one group) and **the C log's DMA** (the median gap between consecutive launches of a run at most 10 ms: E141's was 1 ms, E78's duty gate 0.97 binds near 14 ms; E160's C-logged launches on aifoundry2 had 2–3 ms) | E141's smoke on pool 6's items |
| stops | board ≥ 65 W or `temp_c.minshire[0]` ≥ 70 °C, live, main path and in-run watcher; `run_e78 --max-c 70` | **the same** | E141's passes here peaked at 55.33 W board and 63 °C `minshire[0]`, no stop fired (its data README); pool 6's hottest tile is predicted 0.9 W below pool 5's (`fp32.wideexp48_dense`) |
| config reads | session start, both ends of the stop test, the smoke and every pass, session end | the same | |
| data | `build/claims-v3/aifoundry3/e141/p141<nn>/` | `build/claims-v3/aifoundry3/e153/p153<nn>/` in `~/aifoundry`; results `docs/reports/data/2026-11-03-e153-blind6-aifoundry3/` | |

**Stops (registered, and why they read live samples)** are E141's code and values unchanged: the block's sampler (`ettelem sample --seconds
--every-ms 100` through E128's guard) writes one JSON line a sample into `<pass>/telemetry.jsonl.raw`; (1) the main path, `run_e78.py` through
`run_e153.py`, reads the newest line before every launch and every 0.1 s while it waits, and a line with `board_w` ≥ 65 W or
`temp_c.minshire[0]` ≥ 70 °C writes STOP (with the line's `t_ms` and its age) and ends the pass with EXIT_HOT; (2) the in-run watcher, a
daemon thread, reads the same file every 0.1 s for the whole pass, runs included, and on the same two stops writes STOP; the host program
(the C-logging host keeps `main.cpp`'s `repeatFor` loop unchanged) ends its launch loop at the next launch, and the main path then ends the
pass. The die stop reads `minshire[0]` because `minshire[2]` is a high-water latch on this card (87 °C in every sample of E140's passes). The
stop-path test proves both paths on live samples before any launch.

**What is E78's and E141's, byte for byte.** `check_e153.py` (before any device opens), `run_e153.py` (before every pass) and `reduce_e153.py`
(before every reduction) refuse on any difference from `predictions-e153.json` › `harness`: E78's card code (`lib.sh` `033d0776…`,
`e78_common.py` `c58923a5…`, `run_e78.py` `f3efd783…`, `reduce_e78.py` `6a158cee…`, `kinds.json` `9586568f…`), E128's guard `c2c4ab76…`,
Q136(w)'s checker `f29e91ca…` and table `50168632…`, the workload's host source `0f53a7d5…`, Q139(k)'s five files, E153's nine card files,
both pools (manifests, `SHA256SUMS`, the predictions file, the 56 tiles) and, on the box, four binaries: E78's host, the heater
(`sparsity_host` `20e760c2…`, E141's), the kernel every launch runs (`sparsity.elf` `d521e432…`), the C-logging host (`99ed75fb…`, built on
aifoundry3 at 06:40 PST today by `build_host_ccheck.sh` from `main.cpp` `0f53a7d5…` with Q139(k)'s patch, giving `5bd029ca…` exactly as the
patch gives it on the Intel; no device opened; its build log is clean) and `ettelem` `16037641…` (E141's). The box files are E141's with the
items, the pass numbers, the C log, the smoke's C checks, tonight's time gates and the seed tag changed (each change marked); `reduce_e153.py`
is E141's with pool 6's items; `score_e153.py` is E141's scorer with M8 scored and the K1, KC, R and CS rules added. **A no-device dry run** of
this commit's files, byte-identical on the box,
ran at 16:03 PST, and the check (HARNESS OK, 89 files), the preflight (GO), the verify and a dry pass again at 16:16 PST on this commit's files: one pass (`V3_DRY=1`: 76 runs of 63 items plus 2 burn-ins, all 78 through the wrapper), the smoke (10 launches through the
wrapper), the queue's budget rule on stub blocks (two 3 s stubs, then "budget: stopping"), the queue's deadline rule (stops before the first
pass when the deadline has passed) and the session's start gate (exit 8, no device opened); `preflight_e153.sh` GO and
`e153_common.py --verify` 0 problems on the box.

**The check of C at the desk** (Q139(k)'s README, "The exact use", steps 3-5): after collection, on the Intel, never on the box, `ccheck.py check`
on every pass's `c-log.jsonl` and the smoke's, in one call, `--jobs 6` ([`collect_e153.sh`](collect_e153.sh)). **`ccheck.py domain`** on pool 6's
50 tiles and the 6 K1 tiles at n = 750,000 (about 16:10-16:14 PST, before this commit; [`logs/ccheck-domain.txt`](logs/ccheck-domain.txt),
`ccheck-domain.json`): **56 of 56 inside** what silicon has read; **36 carry first-read notes** (a wider exponent spread or more distinct
magnitudes than E104's tiles, int8 operands beyond the [−3, 3] the host read in September, or words that wrap by n).

## Device commands sent

*The owner's rules of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send, classified
READ or WRITE from the firmware source of the running build; only read-only PMIC voltage reads and the statistics reset are allowed, and
**E153 does not send the reset**.* The sending code is E141's (`lib.sh` unchanged, the same `ettelem` binary, through E128's guard; the block's
config reads and its one `start_sampler` call), classified from et-platform `836a4ab` (BL2 0.22.0; Q136(w)'s table `dmcmd_table.json`); each
cited handler and getter was read again at `836a4ab` tonight:

| command (id) | sent by | class | firmware source (et-platform `836a4ab`, `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| GET_MODULE_STATIC_TDP_LEVEL (25) | `ettelem config` (session ends, block ends) | READ | `services/thermal_power_monitor.c:339` → `services/thermal_pwr_mgmt.c:613-617`, a RAM copy |
| GET_MODULE_TEMPERATURE_THRESHOLDS (21) | `ettelem config` | READ | `thermal_power_monitor.c:438` → `thermal_pwr_mgmt.c:665-669`, RAM |
| GET_MODULE_POWER_STATE (23) | `ettelem config` | READ | `thermal_power_monitor.c:48` → `thermal_pwr_mgmt.c:551-555`, RAM |
| GET_ASIC_FREQUENCIES (53) | `ettelem config`, `ettelem sample` | READ | `services/performance.c:41` → `perf_mgmt.c:276` → `driver/io_pll.c:907-960`, PLL register reads |
| GET_ASIC_VOLTAGE (32) | `ettelem config`, `ettelem sample` | READ (two PMIC voltage-register reads, allowed) | `thermal_power_monitor.c:192` → `thermal_pwr_mgmt.c:1142-1222`, PVT reads and `pmic_get_voltage` → `driver/pmic_controller.c:1473-1500` (`get_pmic_reg`, an I2C register read) |
| GET_MODULE_POWER (33) | `ettelem sample` at 10 Hz | READ | `thermal_power_monitor.c:142` → `thermal_pwr_mgmt.c:984-988`, the RAM copy the SP keeps |
| GET_SP_STATS (60) | `ettelem sample` | READ | `performance.c:404-466` → `thermal_pwr_mgmt.c:2780-2784`, RAM |
| GET_MODULE_CURRENT_TEMPERATURE (27) | `ettelem sample` | READ | `thermal_power_monitor.c:545` → `thermal_pwr_mgmt.c:732-773`, PVT register reads |
| GET_MODULE_VOLTAGE (31) | `ettelem sample` | READ (nine PMIC voltage-register reads, allowed) | `thermal_power_monitor.c:243` → `thermal_pwr_mgmt.c:1010-1140` → `pmic_get_voltage` |
| SET_STATS_RUN_CONTROL (`--reset-ms`, the statistics reset) | **never sent** | WRITE (allowed, not used) | `lib.sh:154` forwards `start_sampler`'s extra arguments; `block_e153.sh`'s only call passes the file and the duration, and the guard refuses `--reset-ms` before the device opens |
| `dev_mngt_service` GET_MODULE_POWER (`lib.sh` `drain_mgmt`) | **never sent** | READ | replaced by a refusal in `block_e153.sh` |
| the C-logging host `build/ccheck/b/host/sparsity_host` through `sparsity_ccheck.sh` (every measured launch), the heater (E78's host), `et-who`, `et-holders`, `et-lab-manifest` | — | **no device-management command** | the ops node only (`createPcieDeviceLayer(true, false)`; the management node is never opened). The C log adds two runtime DMA calls the harness already makes every launch: `dev.put("out", …)` 1 MiB of the poison before the launch and `dev.get("out", …)` 1 MiB of C after it (Q139(k) § Device commands sent); the wrapper's sha256 of the two binaries is host-side |

Never sent: any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset. **The
checker** `tools/claims-v3/dmcmd_audit.py` (unchanged), from the repository root on every file the session runs or sources
(`preflight_e153.sh`; on the box also the patched host source `build/ccheck/src/host/main.cpp`): **NO-GO** without an exception, at the one
conditional site E140's, E141's and E142's lanes reviewed (`lib.sh:154`), and with the reviewed exception **GO, 32 send sites, 0 disallowed**
([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt)); the desk files (`reduce_e153.py`,
`score_e153.py`, `collect_e153.sh`, `make_predictions_e153.py`, `selftest_e153.py`, `ref_errors_e153.py`, `ccheck.py`) and the patched host
source (`5bd029ca…`, made on the Intel as `build_host_ccheck.sh` makes it) send nothing (GO, 0 sites; [`dmcmd-audit-desk.txt`](dmcmd-audit-desk.txt)).
The session runs the same preflight on the box before any device opens and stops on anything but GO. **Residual (Q136(w)'s table caveat, E130's
A1):** aifoundry3 runs a non-public thermal firmware build first flashed on 7 Oct 2026, so these classes rest on `836a4ab`'s handlers and on
these reads' unchanged behaviour on this card; if the session-start `ettelem config` or the smoke's telemetry comes back in another form than
E141's (the same fields, TDP 0 W / 65 °C / 600 MHz, `since_reset_ms` −1), the smoke gate fails and no pass runs. **Verdict before the first
launch: GO.**

## Card budget and time gates

**At most 55 card-minutes**, from the session's first device access (`E153_T0`, before its first config read) to the session-end config read.
Expected about 45–47: the stop-path test and the smoke about 2 min, then three passes of about 13–14 min (E141's 56-run passes took 574–623 s;
76 runs scale that to 779–846 s) with 10 s between. [`queue_e153.sh`](queue_e153.sh) starts a pass only if its projected end (880 s until the
first pass ends, then the longest measured) is inside **3,240 s** of `E153_T0` (3,300 less a 60 s reserve for the closing read) and before
**21:50 PST**; a pass in flight is never cut, so a fourth pass will not start. **No card session starts after 21:00 PST** (`session_e153.sh`
refuses with exit 8 before any device opens); **every run ends by 22:00 PST**. It starts only with `et-who` clean and with the day's post in
`#community-lab` carrying this reservation.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a -c --exclude __pycache__` `tools/claims-v3/e153/`, `tools/claims-v3/kinds/blind6/`,
`tools/claims-v3/ccheck/`, `tools/claims-v3/dmcmd_audit.py` and `dmcmd_table.json` to the same paths under `aifoundry3:aifoundry/` (pool 5's tiles
are there unchanged). On aifoundry3, from `~/aifoundry`: `python3 tools/claims-v3/e153/check_e153.py`, `bash tools/claims-v3/e153/preflight_e153.sh`,
the day's post written, then `E153_T0=$(date +%s) setsid nohup bash tools/claims-v3/e153/session_e153.sh > build/e153/session.out 2>&1 < /dev/null &`
from a script file. Collect on the Intel: `PY=<python with numpy> nice -n 10 bash tools/claims-v3/e153/collect_e153.sh <copy> [<E157 reduction>]`.

## Files

All in `tools/claims-v3/e153/`: `README.md` (this); `make_predictions_e153.py` → `predictions-e153.json` (the freeze, with every file's
sha256) and `planned-intervals.txt`; `ref_errors_e153.py` → `ref-errors-m8.json`; `e153_common.py`, `run_e153.py`, `block_e153.sh`,
`queue_e153.sh`, `session_e153.sh`, `check_e153.py`, `preflight_e153.sh`, `smoke_gate_e153.py` (the box); `reduce_e153.py`,
`collect_e153.sh`, `score_e153.py` (the desk); `selftest_e153.py`, `selftest.txt`; `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`,
`dmcmd-audit-desk.txt`; `logs/ccheck-domain.txt`, `logs/ccheck-domain.json`. The pools: `tools/claims-v3/kinds/blind6/`,
`tools/claims-v3/kinds/blind5/`. Data: `docs/reports/data/2026-11-03-e153-blind6-aifoundry3/`.

## Amendments

**A1 (Tue 3 Nov 2026, about 16:40 PST, during the session and before its registered reduction and scoring): a tile that never ran is
not a C failure.** The session started at 16:21:44 PST. After its first pass (15310) ended at 16:35:07, the collector, the C check and the
scorer were run once on that pass alone as a pipeline test (a scratch copy, outputs overwritten; one pass is below every rule's two-pass
minimum, so no verdict exists and its numbers are not results and are reported nowhere). It found a fault in `score_e153.py`'s C status:
E78's runner had skipped one run by its own rule ("launch reading not reached", `int8.b_line_zero_full`, as E141's D2), and the scorer
counted a tile with **no launch** in the kept passes as a C failure (`all_pass` required at least one launch), so KC read FAIL and the tile
was put in the C-excluded set. The registered rule says "every measured launch" (E153-KC above and `predictions-e153.json` › `rules`): a tile
with no measured launch has nothing to check, and with no D it is outside every rule anyway. **The change** (code only, `score_e153.py`
`score` and `k1_rules`): a tile with no launch in any kept pass is named in `c_not_measured` and is neither C-excluded nor a KC failure;
K1-C reads FAIL on any launch not PASS, NOT SCORED if a K1 tile has no launch, else PASS. A kept pass with no `runs.jsonl` still fails every
tile, as registered. Nothing else changes: no tile, prediction, band, reference error, rule threshold, footing or arm; the self-test's C
plumbing cases (one ROUNDING launch, one launch with no C record) still fail their tile. A tile that runs in some kept passes and not others
is judged on the launches it has, as before.

*Dated note on A1 (Tue 3 Nov 2026, written about 18:25 PST and committed 18:29 PST, after verification; A1's text above is left as committed in `e6ca949d`). A1's account
of the pipeline test is incomplete, and its words "so no verdict exists and its numbers are not results and are reported nowhere" are
withdrawn. The test ran in two steps (times from the lane's working files). First, to 16:39:47 PST, the collector ran on pass 15310 alone:
the C check, the reduction and its arms. With one pass the scorer scored nothing. Then the lane listed that pass twice in a copy of the
primary reduction (`passes` [15310, 15310]) and ran this registration's scorer on it, with the C check, at 16:40:11. The scorer counted
two passes and printed every rule's verdict on that one pass's data: P1 FAIL (0.286 W); P2, P3, B1 (−0.029 W), B2, C1 (28 of 29),
H1–H4, R1, R2 and CS0-floats PASS; M1 NOT RESOLVED; M2 WORSE (+0.036 W); CS0-int8 FAIL; K1 and CS1 NOT SCORED; KC FAIL. KC's FAIL was the
fault this amendment fixes. The scorer was changed and re-run on the same copy at 16:41:35 (KC PASS, every other verdict and number as
before). The amendment was written at 16:41:53 and committed at 16:42:11. **So A1 was written after an interim scoring of data it
touches.** It moved no verdict. This registration's scorer (`359c96b2`, before A1), run on the session's final reduction, gives its
`scored.json` and `results.md` exactly, bar A1's new, empty `c_not_measured` keys, because every tile ran in at least three kept passes.
An independent verifier found the same. Nothing registered changed after the look: `predictions-e153.json` is unchanged since this
registration, and the queue on the box ran its passes by the registered budget rule. The two printouts are committed, unchanged and
labelled, in [`docs/reports/data/2026-11-03-e153-blind6-aifoundry3/interim/`](../../../docs/reports/data/2026-11-03-e153-blind6-aifoundry3/interim/README.md),
with the re-score in that directory's `corrections.txt` (C1). They are not results.*
