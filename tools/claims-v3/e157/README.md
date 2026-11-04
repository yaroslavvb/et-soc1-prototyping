# E157: blind pool 6 on aifoundry1 card 1 - M8's power and heat, frozen before the claim, scored on the second card with M7 and M6 beside it, every launch's C checked (Q139, 600 MHz)

*Pre-registered Tue 3 Nov 2026 (week 45), evening, PST, on the Intel, in Q139 resumed (lane `a1c1-e157-blind6`), before the claim of
aifoundry1 card 1 and before any card has run a tile of blind pool 6 on this card. The owner's mandate is his of Mon 2 Nov, about 18:40 PST,
"feel free to settle any unanswered questions regarding horace's power model", with the goal "to predict the power requirement and heat
generation of various kinds of numeric computations as accurately as possible", and Q139 continues on his words of Tue 3 Nov, about 15:47 PST,
"approved both aifoundry and mordast, continue". **It answers item 6 of the kinds page's section 11**, "a power model across kinds"
([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), and three ranks of
Q138's final critic: **rank 2** (M8 scored on a sixth blind pool on both 600 MHz cards: "M8 minus M6 rms resolved below zero by a paired
bootstrap over tiles on both 600 MHz cards; bias inside B1/B2; at least 26 of 30 inside"), **rank 5** (the card term: E142's X1/X2 on pool 6,
and card 1's scale predicted from its cheap reads, "within 1% of the measured one") and **rank 14** (no file tile's C was ever checked:
"re-run 6 pool-5 tiles with C checked; every C exact or within the format's rounding, and D within ±0.05 W of E141's and E142's"). The
complaint behind rank 14 was first written in E78's README, § Joins and traps
([`docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md`](../../../docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md)).
**Every prediction E157 scores is frozen elsewhere, before this was written**: M8 ([`m8.json`](../../../docs/reports/data/2026-11-03-q139m-model/m8.json),
Q139(m), `122da8b6`, 04:57:59 PST), the pool ([`../kinds/blind6/`](../kinds/blind6/README.md), Q139(b)'s 50 tiles by an independent designer,
copied unchanged into the tree with M8's, M7's and M6's predictions by Q139(x), **`d98d2e34`**, 05:39:23 PST) and the card-1 predictions
[`predictions-blind6-aifoundry1c1.json`](../kinds/blind6/predictions-blind6-aifoundry1c1.json) (`267565ab…`). E157 adds no prediction. What it
adds is frozen in [`predictions-e157.json`](predictions-e157.json), written by [`make_predictions_e157.py`](make_predictions_e157.py) from the
committed files it names (each checked by sha256): the plan, the stops, the rules, the reference errors behind them and the hash of every file
the box runs. Any change after this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry1 card 1 only**
(`V3_DEVICE=1`, `aifoundry1-c1`, `/run/lock/etsoc-shire1.lock`), 600 MHz, TDP 65 W and threshold 65 °C as read, never set. **E157 sends no
write command of any kind** (§ Device commands sent).*

*An earlier attempt of this lane (Tue 3 Nov, about 06:35-06:55 PST) wrote most of these files and stopped on a usage limit before any
registration, claim or launch: nothing was committed, nothing was copied to the box (no `tools/claims-v3/e157/` or `kinds/blind6/` there,
checked 15:56 PST), and no card was touched. This lane re-checked every file it left (§ What was re-checked) and corrected what did not hold:
the scorer read a reference key the freeze no longer wrote, the time gates were the morning's, and the rules now follow E153's draft for the
same pool on aifoundry3 where the brief says "rules as E153's".*

## What it does to predicting power and heat

M8 predicts, from the bytes a matmul multiplies, its **power** D (board W over the type's own zeros at 600 MHz) and its **heat** (the die's rise
over a 4.5 s kinds run). On this card both go through **the card term**, M8's one measured scale (D on card 1 = 0.9616 × D on aifoundry3, floats
and int8) and card 1's die rise per board W (0.1151 °C/W, M7's heat law, carried). **Before** (the error M8 claims for new kinds, nested leave
one kind out on its 767 rows, card 1's rows): power **0.198 W rms fp32, 0.170 W fp16, 0.238 W int8**; heat 0.352 / 0.355 / 0.141 °C. The
blind record of the models it replaces on this card, pool 5 (E142): M7 0.169 / 0.149 / 0.251 W, M6 as good (0.211 W over the 30, 29 of 30
inside); on aifoundry3 (E141) M7 0.325 / 0.317 / 0.356 W with the floats biased −0.23 W. The card term: E142's X1 fails post hoc (card 1's
float D over aifoundry3's 0.982 against M7's 0.9711), and no cheap read predicted a training card's scale to 1% (the zeros level, physical,
missed card 1 by +1.1% floats and −0.1% int8; the 600 MHz voltage squared by −5.2%). **After**: pool 6's blind error on this card, by format,
for power and for heat, with the bias, the share inside M8's frozen 95% bands and M8 against M6 and M7 on the same tiles; with E153 (the same
pool on aifoundry3) the per-tile ratio between the cards tests the card term (X1, X2) and the cheap-read scale (S1, S2). **And the rows'
validity**: K1 re-runs six of pool 5's tiles with every launch's C checked, and every pool-6 launch carries its C, so a silent kernel error
would show as a FAIL rather than as a biased row in the next fit.

## The question

1. **Is M8's power on a blind pool, on the second card, as accurate as its nested score says?** Per format: fp32 (P1), fp16 (P2), int8 (P3).
2. **Is it unbiased?** Floats (B1), int8 (B2).
3. **Do its frozen 95% bands cover?** Power (C1: at least 26 of 30), heat (H4).
4. **Is M8 better than M6 (and M7) on the same new tiles?** (M1: the critic's rule, a paired bootstrap; M2.)
5. **Is its heat as accurate?** Per format (H1-H3), the die rise over each run's window.
6. **Real tiles** (critic rank 8, all 12 real tiles, pool 6's CORRECTIONS C9): as accurate as the pool's own non-real tiles (R1), none outside
   its band (R2).
7. **Does the card term hold on pool 6, and do cheap reads predict it?** (X1, X2; S1, S2: scored only with E153's committed reduction.)
8. **Are the launches' results right?** K1 (six pool-5 tiles: C, and D against E142's), PC (every pool-6 launch's C), PCa (E78's anchors).

## The models, the pool and K1, frozen elsewhere

| what | file | sha256 | frozen in |
|---|---|---|---|
| the pool: 50 tiles (18 fp32, 13 fp16, 19 int8; 30 priority 1, 14 priority-2 tests, 6 anchors of its own; 12 real tiles cut from two public models), by an independent designer | [`blind6.json`](../kinds/blind6/blind6.json), `MANIFEST`, `SHA256SUMS`, `tiles/` | `4c4cee7b…`, `a0e91556…`, `8ab25920…` | `d98d2e34` (Q139(x); designed by Q139(b)) |
| M8 (floats with the C register's flips, int8 with a near-whole-byte discount; card term 0.9616; heat M7's, carried) | [`m8.json`](../../../docs/reports/data/2026-11-03-q139m-model/m8.json), [`nested-m8.json`](../../../docs/reports/data/2026-11-03-q139m-model/nested-m8.json) | `8c23aba2…`, `f284b540…` | `122da8b6` (registration `f640fb7a`) |
| M8's, M7's and M6's predictions for the pool on card 1, D and die rise, with 95% bands | [`predictions-blind6-aifoundry1c1.json`](../kinds/blind6/predictions-blind6-aifoundry1c1.json) | `267565ab…` | `d98d2e34` |
| card 1's scale from cheap reads, every read and form | [`card-scale-blind6.json`](../kinds/blind6/card-scale-blind6.json) | `6b040791…` | `d98d2e34` |
| the one footing (card 1's leakage slope 0.3134 W/°C, E82 A2's dips removed once) and E142 re-reduced on it | [`footing.json`](../../../docs/reports/data/2026-11-03-q139u-footing/footing.json), [`reduced/e142-footing.json`](../../../docs/reports/data/2026-11-03-q139u-footing/reduced/e142-footing.json) | `f589efaa…`, `d117d83b…` | Q139(u) (rule `d4c36bfe`, data `f47669d1`) |
| K1's six pool-5 tiles (`pick6.py`: per format the two measured most tightly on both cards) and E142's D on its own footing | [`../ccheck/pick6.py`](../ccheck/pick6.py), [`e142.json`](../../../docs/reports/data/2026-11-02-e142-blind5-card1/e142.json), [`../kinds/blind5/`](../kinds/blind5/README.md) | `b4b92dc1…`, `f9976328…`, `946f8493…` | Q139(k) `4946a992`; E142 `e677dddc`; pool 5 `dac39d97` |
| the C reference and the C-logging host | [`../ccheck/`](../ccheck/README.md) (`ccheck.py`, `patch_host_ccheck.py`, `sparsity_ccheck.sh`, `build_host_ccheck.sh`) | `2f806fe6…` (ccheck.py) | Q139(k) `60b91395`, corrected `4946a992` |

`d98d2e34` precedes this commit (`git merge-base --is-ancestor d98d2e34 <this commit>`), and this commit precedes the claim and the first
launch. **The band rule** is M8's (`band_rule_M8` in the predictions file): power half-width k × √(pool² + s² xᵀCx), heat M7's carried.

**The footing.** The registered primary is **Q139(u)'s one footing**: E78's reduction (`reduce_e78.py`, unchanged, through `reduce_e157.py`)
with card 1's frozen leakage slope **0.3134 W/°C** (`footing.json` › `slopes.c1`, never refitted on this session), `--no-refit`, the board
meter's dips removed once (E82 A2) and card 1's 65/65 config read accepted. That is the frame of M8's training rows and of its predictions.
**Beside it, E142's own footing**: the same reduction at 0.2414 W/°C (E82's frozen slope, dips removed), the footing E142's session was reduced
on (the frame of `e142.json`); every rule is scored and reported on it too. (The brief's "E142's session-own footing" is read as that one,
since E142 registered a frozen slope; the session's own fitted slope, `auto`, is an arm.)

**K1** (the critic's rank-14 sub-rule). Six pool-5 tiles run in every pass of this session, in the first third of each pass, with C logged, on
E78's frame like every other tile. E142's D for them, on both footings:

| K1 tile | E142 D, its own footing (0.2414 W/°C), W ± se (passes) | E142 D, Q139(u)'s footing (0.3134 W/°C) ± se | Welch half-width of a same-card repeat, Q139(u)'s footing |
|---|---|---|---|
| `fp32.b_exp_busy_a_const` | 15.114 ± 0.061 (5) | 14.967 ± 0.055 | ±0.179 |
| `fp32.real_pythia_ln1_q` | 21.500 ± 0.049 (5) | 21.311 ± 0.047 | ±0.152 |
| `fp16.sparse24_aligned` | 12.459 ± 0.031 (5) | 12.316 ± 0.031 | ±0.100 |
| `fp16.exp_only` | 15.822 ± 0.034 (5) | 15.662 ± 0.028 | ±0.090 |
| `int8.gray_a` | 4.261 ± 0.061 (5) | 4.211 ± 0.055 | ±0.181 |
| `int8.b_line_zero_one` | 3.287 ± 0.082 (5) | 3.227 ± 0.085 | ±0.278 |

The brief puts K1 "first". The C check runs at the desk only (Q139(k): never on a lab host), so no C verdict exists on the box during the
session; K1's six therefore run first in every pass (segment 0), and K1 is scored and reported first.

## The frozen predictions

D in W over the type's own zeros, and the die rise over the run in °C, aifoundry1 card 1, 600 MHz; M8 with its 95% band (scored), M7 and M6
beside (reported), copied from `predictions-blind6-aifoundry1c1.json` into `predictions-e157.json` › `tiles`. Cases are the pool's: E
exponent-heavy, S single-bit, Z zeros' transport, R real (12), C the C-register candidate, L whole-line flip-flops, B int8 B positions, W
seeded weights, 0 anchors; "hold" marks the four hold candidates for E154/E161.

| tile | case | prio | M8 D, W [95%] | M7 D | M6 D | M8 die rise, °C [95%] |
|---|---|---:|---|---:|---:|---|
| `fp32.a_onebit_b5_third` | S hold | 1 | **9.08** [8.64, 9.52] | 9.12 | 9.07 | **1.25** [0.57, 1.94] |
| `fp32.a_zeros_b_complement` | Z | 1 | **1.48** [1.02, 1.93] | 1.49 | 1.73 | **0.38** [-0.31, 1.06] |
| `fp32.b_onebit_b12_third` | S | 1 | **9.47** [9.04, 9.91] | 9.54 | 9.51 | **1.30** [0.61, 1.98] |
| `fp32.b_onebit_b20_third` | S | 1 | **13.22** [12.78, 13.66] | 13.34 | 13.25 | **1.73** [1.04, 2.42] |
| `fp32.bf16_wideexp` | E | 1 | **18.67** [18.22, 19.13] | 18.89 | 18.95 | **2.36** [1.67, 3.04] |
| `fp32.exp_a_walk_fixedmant` | E | 1 | **12.14** [11.70, 12.58] | 12.28 | 12.30 | **1.60** [0.92, 2.29] |
| `fp32.exp_b_alt_shift` | E | 1 | **15.43** [14.98, 15.88] | 15.63 | 15.57 | **1.98** [1.30, 2.67] |
| `fp32.exp_only_narrow2` | E | 1 | **14.42** [13.97, 14.86] | 14.54 | 14.53 | **1.87** [1.18, 2.55] |
| `fp32.negzero_a_b_complement` | Z | 1 | **16.03** [15.57, 16.49] | 16.25 | 16.76 | **2.05** [1.37, 2.74] |
| `fp32.real_qwen_dequant_q` | R real | 1 | **19.51** [19.07, 19.95] | 19.63 | 19.52 | **2.45** [1.77, 3.14] |
| `fp32.real_smol_softmax_v_causal` | R real, hold | 1 | **13.17** [12.73, 13.61] | 13.23 | 13.16 | **1.72** [1.04, 2.41] |
| `fp32.signexp_invert_b` | E | 1 | **16.42** [15.96, 16.88] | 16.65 | 16.46 | **2.10** [1.41, 2.78] |
| `fp32.a_onebit_b16_half` | S | 2 | **9.31** [8.87, 9.75] | 9.37 | 9.35 | **1.28** [0.59, 1.96] |
| `fp32.c_absorbed` | C | 2 | **19.20** [18.75, 19.64] | 19.32 | 19.43 | **2.42** [1.73, 3.10] |
| `fp32.exp_a_pow2wide_b_randn` | E | 2 | **18.43** [17.98, 18.88] | 18.64 | 18.93 | **2.33** [1.64, 3.01] |
| `fp32.real_qwen_softmax_v` | R real | 2 | **23.32** [22.88, 23.77] | 23.43 | 23.38 | **2.89** [2.21, 3.58] |
| `fp32.anchor6_randn` | 0 | 2 (anchor) | **23.78** [23.34, 24.22] | 23.89 | 23.92 | **2.94** [2.26, 3.63] |
| `fp32.anchor6_zeros` | 0 | 2 (anchor) | **0.00** [-0.43, 0.43] | 0.00 | 0.00 | **0.21** [-0.48, 0.89] |
| `fp16.e5m2grid_wide` | E | 1 | **17.23** [16.85, 17.62] | 17.42 | 17.45 | **2.19** [1.50, 2.88] |
| `fp16.exp_b_alt_shift` | E | 1 | **14.93** [14.55, 15.31] | 15.09 | 14.95 | **1.92** [1.23, 2.62] |
| `fp16.exp_only_narrow2` | E | 1 | **15.30** [14.92, 15.68] | 15.41 | 15.40 | **1.97** [1.27, 2.66] |
| `fp16.real_qwen_qk` | R real | 1 | **18.28** [17.90, 18.66] | 18.40 | 18.36 | **2.31** [1.62, 3.00] |
| `fp16.real_smol_qk` | R real | 1 | **20.74** [20.36, 21.11] | 20.85 | 20.86 | **2.59** [1.90, 3.28] |
| `fp16.real_smol_softmax_v` | R real | 1 | **16.88** [16.50, 17.25] | 16.98 | 16.89 | **2.15** [1.46, 2.84] |
| `fp16.a_zeros_b_complement` | Z | 2 | **1.46** [1.07, 1.86] | 1.48 | 1.55 | **0.37** [-0.32, 1.06] |
| `fp16.b_onebit_b6_third` | S | 2 | **12.24** [11.86, 12.62] | 12.33 | 12.22 | **1.61** [0.92, 2.31] |
| `fp16.c_absorbed` | C | 2 | **19.10** [18.72, 19.48] | 19.26 | 19.33 | **2.40** [1.71, 3.10] |
| `fp16.exp_a_walk_fixedmant` | E | 2 | **12.02** [11.65, 12.40] | 12.14 | 12.16 | **1.59** [0.90, 2.28] |
| `fp16.real_qwen_dequant_v` | R real | 2 | **21.04** [20.66, 21.42] | 21.16 | 21.22 | **2.63** [1.94, 3.32] |
| `fp16.anchor6_randn` | 0 | 2 (anchor) | **21.23** [20.85, 21.61] | 21.34 | 21.40 | **2.65** [1.96, 3.34] |
| `fp16.anchor6_zeros` | 0 | 2 (anchor) | **0.00** [-0.37, 0.37] | 0.00 | 0.00 | **0.20** [-0.49, 0.90] |
| `int8.a_word_zero_one` | L | 1 | **2.75** [2.05, 3.45] | 2.70 | 2.62 | **0.58** [0.31, 0.86] |
| `int8.a_zeros_b_lineflip` | Z | 1 | **-0.33** [-1.67, 1.01] | 0.05 | 0.49 | **0.23** [-0.04, 0.51] |
| `int8.b_line_zero_ff` | L hold | 1 | **3.26** [2.08, 4.44] | 3.60 | 3.99 | **0.64** [0.37, 0.92] |
| `int8.b_line_zero_full` | L | 1 | **4.07** [3.37, 4.78] | 3.97 | 4.07 | **0.74** [0.46, 1.01] |
| `int8.bheld_bit1` | B | 1 | **5.95** [5.17, 6.73] | 6.05 | 5.89 | **0.95** [0.68, 1.23] |
| `int8.bheld_bit4` | B | 1 | **5.63** [4.86, 6.40] | 5.72 | 5.58 | **0.92** [0.64, 1.19] |
| `int8.bheld_bit7` | B | 1 | **5.30** [4.55, 6.05] | 5.40 | 5.25 | **0.88** [0.60, 1.15] |
| `int8.powerlaw_df4_pc` | W | 1 | **6.50** [5.81, 7.19] | 6.57 | 6.57 | **1.02** [0.74, 1.29] |
| `int8.real_qwen_w8a8_gate` | R real | 1 | **6.47** [5.78, 7.16] | 6.51 | 6.51 | **1.01** [0.74, 1.29] |
| `int8.real_qwen_w8a8_v` | R real, hold | 1 | **6.44** [5.75, 7.13] | 6.51 | 6.53 | **1.01** [0.73, 1.28] |
| `int8.real_smol_w8a8_down` | R real | 1 | **5.23** [4.54, 5.92] | 5.19 | 5.17 | **0.87** [0.60, 1.15] |
| `int8.real_smol_w8a8_q` | R real | 1 | **6.29** [5.60, 6.99] | 6.30 | 6.32 | **0.99** [0.72, 1.27] |
| `int8.b_line_55_aa` | L | 2 | **5.87** [4.65, 7.08] | 6.41 | 6.66 | **0.94** [0.67, 1.22] |
| `int8.bflip_bit2_w` | B | 2 | **2.08** [1.34, 2.81] | 2.15 | 2.08 | **0.51** [0.23, 0.78] |
| `int8.bflip_bit5_w` | B | 2 | **2.08** [1.35, 2.81] | 2.11 | 2.07 | **0.51** [0.23, 0.78] |
| `int8.powerlaw_df15_pt` | W | 2 | **2.57** [1.87, 3.27] | 2.58 | 2.56 | **0.56** [0.29, 0.84] |
| `int8.real_qwen_w8a8_down` | R real | 2 | **5.91** [5.21, 6.61] | 5.87 | 5.91 | **0.95** [0.67, 1.22] |
| `int8.anchor6_full` | 0 | 2 (anchor) | **6.76** [6.06, 7.45] | 6.83 | 6.79 | **1.05** [0.77, 1.32] |
| `int8.anchor6_zeros` | 0 | 2 (anchor) | **0.00** [-0.67, 0.67] | 0.00 | 0.00 | **0.27** [-0.01, 0.54] |

**Card 1's scale from cheap reads** (`card-scale-blind6.json`, frozen; s = D on card 1 over D on aifoundry3, same tiles): the registered form
is **the zeros level with the physical exponent: 0.9707 floats, 0.9610 int8**. The critic's rank 5 asks for each card's scale "predicted from
its own zeros and idle reads only"; of those two reads the zeros level is the one whose leave-one-card-out error on card 1 was smallest in
training (+1.1% / −0.1%; idle power +32.6% / +31.0%), chosen from M8's training table before any pool-6 data exists. Reported beside, every
other read and form: V600² (M8's physical candidate) 0.9102 / 0.9011, V600 fitted 0.8780 / 0.7788, the zeros level fitted 0.9879 / 0.9769, the
leakage slope fitted 0.9745 / 0.9516, physical 1.2617 / 1.2490, idle power 1.2733 / 1.2605 (physical) and 1.3555 / 1.7942 (fitted); and the
registered form with card 1's zeros level re-read in this session (pool 6's own fp32 zeros tile's S).

## Decision rules

On the primary reduction (Q139(u)'s footing: E78's `reduce_e78.py` unchanged through `reduce_e157.py`, leakage 0.3134 W/°C, `--no-refit`, dips
removed once, E78's run and pass gates, card 1's config gate), over kept passes. A tile's measured value is its mean over the passes it ran in;
a tile with fewer than 2 kept passes is left out and named. **Fewer than 2 kept passes: every rule but the C rules NOT SCORED.** The scored set
is the tiles whose every launch passed the C check (PC); every rule is also given over all tiles, beside. Power reference: M8's nested leave
one kind out errors of every **card-1** row of the format (155 fp32, 134 fp16, 67 int8; `ref-errors-m8.json`, recomputed with Q139(m)'s own
`fit_m8.run_family`, unchanged, every pool's rms equal to `nested-m8.json`'s to 1e-9 W; this lane re-ran it and matched to 4.5e-13 W), copied
into `predictions-e157.json` › `reference_errors.power_card1`. Heat: a deterministic normal sample of 2,000 points with M8's carried card-1 heat
rms (0.352 / 0.355 / 0.141 °C). Bootstrap: 20,000 draws, seed 15700 plus the rule's characters (`score_e157.py`); paired comparisons 5,000.

| rule | quantity | set | verdict |
|---|---|---|---|
| **E157-PC** | C, pool 6 | every launch of a pool-6 tile in a kept pass | **PASS** if each has its C record (same `t_start_ms`, `t_end_ms`) and `ccheck.py check` judges it PASS (bit-exact; ROUNDING, UNMODELLED, FAIL, unrecorded = not checked), else **FAIL** naming the tiles; **a tile with any launch not PASS leaves the scored set of every rule below**, named (E153-KC's rule) |
| **E157-P1** | power D | priority-1 fp32 (12), at least 6 | rms(D − M8) against the 2.5–97.5% range of the rms of as many draws with replacement from the card-1 fp32 reference errors: **PASS** at or below the 97.5% point, **FAIL** above; below the 2.5% point is reported as "better than the nested score says" |
| **E157-P2** | power D | priority-1 fp16 (6), at least 4 | as P1, fp16's |
| **E157-P3** | power D | priority-1 int8 (12), at least 6 | as P1, int8's |
| **E157-B1** | bias | priority-1 floats (18), at least 8 | mean(D − M8) against the 2.5–97.5% range of the mean of as many draws (the same format mix): **PASS** inside; **FAIL HIGH** below it (M8 predicts too much), **FAIL LOW** above it |
| **E157-B2** | bias | priority-1 int8 (12), at least 6 | as B1 |
| **E157-C1** | power coverage | the priority-1 tiles (30) | **PASS** if the number inside M8's frozen 95% band is at least the 2.5% point of Binomial(n, 0.95) (26 of 30), **FAIL** if fewer; NOT SCORED under 10 |
| **E157-M1** | M8 against M6 (the critic's) | the priority-1 tiles | d = rms(M8's errors) − rms(M6's), 95% interval by a paired bootstrap over tiles: **BETTER** ("resolved below zero") if its upper bound < 0, **WORSE** if its lower bound > 0, else **NOT RESOLVED**. Card 1's half of the critic's "on both 600 MHz cards"; E153 has aifoundry3's |
| **E157-M2** | M8 against M7 | the priority-1 tiles | as M1 |
| **E157-H1** | die rise `dT_win` | priority-1 fp32, at least 6 | rms(dT − M8) against the 2.5–97.5% range of the rms of as many draws from the normal reference (0.352 °C): PASS / FAIL as P1 |
| **E157-H2** | die rise | priority-1 fp16, at least 4 | as H1 (0.355 °C) |
| **E157-H3** | die rise | priority-1 int8, at least 6 | as H1 (0.141 °C) |
| **E157-H4** | heat coverage | the priority-1 tiles | as C1, M8's frozen dT band (26 of 30) |
| **E157-R1** | real tiles (rank 8) | all 12 real tiles, at least 8 | rms(D − M8) at or below the 97.5% point of the rms of as many draws (same format mix) from the errors of the pool's own non-real non-anchor tiles: **PASS**, else **FAIL** (E153-R1's form) |
| **E157-R2** | real tiles | all 12 | every measured real tile inside M8's frozen 95% band: **PASS**, else **FAIL** naming them |
| **E157-X1** | the card term, floats (E142's X1 on pool 6) | non-anchor float tiles with D ≥ 5 W on both cards, in both cards' scored sets | **scored only if E153's committed primary reduction of pool 6 exists when this lane reduces** (else NOT SCORED, handed on with the code): the median of D(card 1) / D(aifoundry3), each card's primary (Q139(u)'s footing on both), 95% interval by a bootstrap over tiles: **PASS** if it holds M8's 0.9616, **FAIL** if not; M7's 0.9711 and E153-CS1's reading (the median within 1% of 0.9616) reported |
| **E157-X2** | the card term, int8 | non-anchor int8 tiles with D ≥ 1 W on both | as X1 (M7's 0.9735 reported) |
| **E157-S1** | card 1's scale from cheap reads, floats (rank 5) | X1's tiles | the zeros level, physical, frozen reads (0.9707) against X1's measured median: **PASS** if within 1%, **FAIL** if not; NOT SCORED when X1 is; every other read and form reported |
| **E157-S2** | the same, int8 | X2's tiles | 0.9610 against X2's median, as S1 |
| **E157-K1C** | K1, C (rank 14) | every launch of K1's six tiles in the session, the smoke's included | **PASS** if each has its C record and is PASS (bit-exact, int8 mod 2^32), **FAIL** if any is ROUNDING, UNMODELLED, FAIL or unrecorded (Q139(k): only PASS counts as checked); the critic's literal "every C exact or within the format's rounding" (PASS or ROUNDING) reported beside |
| **E157-K1D** | K1, D (the critic's literal) | the six tiles, at least 2 passes each | \|D_E157 − D_E142\| ≤ 0.05 W on each, **Q139(u)'s footing on both sides** (this session's primary against `e142-footing.json`): **PASS** if all six, else **FAIL** naming them |
| **E157-K1W** | K1, D (Q139(k)'s same-card rule) | the same | Welch's 95% interval, \|D_E157 − D_E142\| ≤ t₀.₉₇₅(ν) √(se_new² + se_old²) (`pick6.py`'s `welch()`), the same frame: **PASS** if all six inside, else **FAIL** |
| **E157-K1** | K1 = K1C AND K1D; K1′ = K1C AND K1W | | both also read on E142's own footing (the reduction at 0.2414 against `e142.json`), reported |
| **E157-PCa** | C, E78's frame | every launch of E78's six anchors and the tie in the session | PASS if all PASS and recorded, else FAIL naming them |

**Reported, never a verdict** (`scored.json`, `results.md`): every tile's measured D and rise with its passes; M7's and M6's rms, bias and
coverage beside M8's on every set and per format, every model on all 44 non-anchor tiles; every rule on E142's own footing and at every arm
(the session's own slope, dips kept, k 0.2955 and 0.3320, the anchor gates relaxed) and over all tiles with the C check's exclusions put back;
the priority-2 tests; the pool's six anchors (its zeros tiles against E78's built-in zeros, its random tiles against M8); the four hold
candidates; the errors by case; the below-zeros tile `int8.a_zeros_b_lineflip` against M8's −0.326 W (M7 +0.048, M6 +0.492: M8's `bsat` term's
most direct test); heat at the measured run length (H2's ST term, −0.1548 °C/W/s, at each tile's median run length); the die rise per board
W against M8's 0.1151 °C/W; the C check's per-tile counts in every pass and the smoke, the launch gaps with the C log, `ccheck.py domain`'s
first-read notes; card 1's cheap reads in this session and the scale they give; E78's anchors and the tie against E142's.

**Why these lines, before the data.** They are E153's for the same pool on aifoundry3 (its draft rules: the critic's rank-2 rules, heat, the
real-tile sub-rule, the C check as the scored set's filter, K1 with the critic's 0.05 W on Q139(u)'s footing and Welch's beside), in E142's
form on this card (card-1 reference errors, E142's X1/X2 for the card term), so the two cards' blind tests read alike. A FAIL on any rule is
stated as a FAIL.

## Precision, before the data

[`planned-intervals.txt`](planned-intervals.txt), at the registered reference and draws: **P1** 0.097–0.302 W (median 0.188) over 12 fp32
tiles; **P2** 0.066–0.291 W (median 0.149) over 6 fp16; **P3** 0.121–0.363 W (median 0.227) over 12 int8; **B1** −0.097 to +0.079 W; **B2**
−0.133 to +0.133 W; **H1** 0.214–0.501 °C; **H2** 0.160–0.557 °C; **H3** 0.086–0.200 °C; C1 and H4 need 26 of 30 inside. **K1-D's ±0.05 W is
narrower than every K1 tile's same-card repeat interval** (Welch half-widths ±0.090 to ±0.278 W on Q139(u)'s footing, ±0.102 to ±0.266 W on
E142's own), so K1-D can fail by noise alone (Q139(k)'s finding 2); K1-W is the statistical reading. [`selftest.txt`](selftest.txt)
([`selftest_e157.py`](selftest_e157.py), 30 simulated sessions a world on the frozen registration, three passes, 0.05 W / 0.05 °C pass noise,
2,000 draws; nothing there is a measurement): when M8 is as good as its nested score (each tile's error drawn from its own card-1 errors), P1
and P2 PASS 30 of 30, P3 29, B1 and B2 28, C1 30, H1–H4 29–30, R1 26, **R2 18** (every one of 12 tiles inside a 95% band happens
0.95¹² = 54% of the time, so R2 FAILS by chance in about 4 sessions of 10); twice as bad, P1–P3 FAIL in 16–23, C1 in 21; with a −0.3 W bias on
the floats, **B1 FAILS HIGH in 30 of 30**; with M6 right, **M1 reads WORSE in 30 of 30** and B1 FAILS LOW in 30. M1 and M2 can only say BETTER
where the models' predictions differ (by under 0.2 W on most tiles here): in the as-good world, where M8 is right by construction, M1 says
BETTER in 25 of 30 and M2 in 18. The C paths: all PASS → PC, K1C, PCa PASS; one ROUNDING launch on a K1 tile → K1C FAIL (critic's literal
PASS); one unrecorded launch on a pool-6 tile → PC FAIL and that tile alone leaves the scored set; a FAIL on E78's zeros → PCa FAIL; a K1
tile moved 0.3 W → K1D and K1W FAIL; at M8's own card ratio X1, X2, S1 and S2 PASS (S1's 0.9707 is +0.94% from 0.9616).

**What I expect, frozen so it can be wrong:** P1–P3 PASS; B1 PASS; B2 PASS or FAIL; C1 PASS; **M1 and M2 NOT RESOLVED** (M8 and M6 differ by
under 0.2 W on most tiles, at most 0.73 W); H1–H4 PASS; R1 PASS, R2 PASS or FAIL on one tile; PC PASS unless a first-read tile shows the
reference's limit; K1C PASS (E104 read this arithmetic on this card); **K1D FAIL by noise on at least one tile, K1W PASS**; PCa PASS; X1 PASS or
FAIL (pool 5's ratio was 0.982 against M7's 0.9711); S1 and S2 FAIL by about 1% (the zeros level missed card 1's floats by +1.1% in
training); X and S handed on if E153's reduction is not committed when this lane reduces. The likeliest misses, named now:
`int8.a_zeros_b_lineflip` and `int8.b_line_55_aa` (M8's `bsat` discount), the whole-line int8 flip-flops (`int8.b_line_zero_ff`,
`int8.a_word_zero_one`), the zeros' transport tiles (`fp32.negzero_a_b_complement`, M6 0.73 W above M8).

**The statement the page gets, decided now.** All PASS: "on 50 tiles written by a designer who never saw the model, on a second card, M8
predicted power within X W rms (fp32), Y (fp16) and Z (int8) with no resolved bias, its 95% bands covering K of 30, and the die's rise within
… °C, as its nested score said; every launch's C was checked". A FAIL is stated with the rms or bias, its interval and the tiles that carry it,
by case. **No tile, prediction, band, rule or reference error changes after this commit; only tiles that ran are scored.**

## What the rules cannot say

One card, one clock, one session. The heat scored is the 4.5 s window only. The heat reference is a normal model of the nested rms, not the
rows. A PASS fails to find a miss at this many tiles; it does not bound M8's error on kinds unlike these 50. M1's paired bootstrap can resolve
M8 against M6 only where they differ. Without E153's reduction the card term and the cheap-read scale are not tested here (handed on with the
code). The C check proves the arithmetic of the launches whose C equals the reference bit for bit; a ROUNDING launch is "the right size", not
checked (Q139(k)'s finding 1).

## What runs

| | E142 (pool 5, this card, 2 Nov) | E157 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet | **the same, through Q139(k)'s wrapper**: the patched host `build/ccheck/b/host/sparsity_host` with `--c-log <pass>/c-log.jsonl --c-poison` and the power passes' kernel `build/sparsity/kernel/sparsity.elf`; the heater unchanged (E78's host) | the protocol M8's rows were measured with; C read after every launch |
| the tiles | pool 5's 36 | **pool 6's 50 and K1's six pool-5 tiles** (`tools/claims-v3/kinds/blind6/tiles/<type>/<name>.bin`, `…/blind5/tiles/…`) | |
| anchors | E78's six three times a pass, the tie `anchor_pi` first and last | the same; the pool's six anchors are ordinary tiles | drift, the zeros D is measured over |
| a pass | 56 runs | **76 runs**: the tie, segment 0 (K1's six, 13 pool-6 tiles, E78's six anchors), segment 1 (19 + 6), segment 2 (18 + 6), the tie; `Random("E157\|aifoundry1-c1\|<pass>")` | |
| passes | 14210–14214 (507–525 s each) | **15710–15714**, as many as the budget rule allows (expected 4), at least two kept | 55 card-minutes |
| stop-path test | 14202 | **15702**, before the smoke, no launch: the guard's die stop (at 1.0 °C), its board stop (at 1.0 W) and the in-run watcher's board stop (at 1.0 W) must each end `run_e157.py` with EXIT_HOT on a live sample (`smoke_gate_e157.py`) | the stops read live samples, tested |
| smoke | 14201 | **15701**: the tie, `fp32.zeros`, `fp32.randn`, `fp32.real_qwen_softmax_v` (the hottest predicted pool-6 tile on this card, S 25.1 W), `fp32.anchor6_zeros`, `fp32.real_pythia_ln1_q` (K1), `fp16.real_smol_qk`, `fp16.zeros`, `int8.b_line_zero_ff`, `int8.zeros`, 2 s each, no preheat, C logged; gated by `smoke_gate_e157.py` (E142's gate: records ok, cycles per op within 0.5%, 600 MHz, config 65 W / 65 °C / 600 MHz, dumped tiles equal their sha256, `since_reset_ms` −1, board below the stop; plus the C log: a host record naming the pinned patched host and kernel, a C record for every launch, ok, poison on, mask 0, stream 0, 1,024 participants) | |
| stops | board ≥ 66 W or a minion-shire field ≥ 72 °C (main path and in-run watcher); `--max-c 72` | **the same** | E142 peaked at 62.09 W board on this card; pool 6's hottest predicted tile is 1.6 W above E142's |
| config reads | both ends of every pass, the session's | **the same** | |
| data | `build/claims-v3/aifoundry1-c1/e142/p142<nn>/` | `build/claims-v3/aifoundry1-c1/e157/p157<nn>/` in `~/nekko`; results `docs/reports/data/2026-11-03-e157-blind6-card1/` | |

**Stops (registered, and why they read live samples).** E142's, unchanged: the block's sampler (`ettelem sample --seconds --every-ms 100`
through E128's guard) writes one JSON line a sample into `<pass>/telemetry.jsonl.raw`; `run_e157.py` reads the newest line before every
launch and every 0.1 s while it waits, and an in-run watcher thread reads it every 0.1 s for the whole pass; a line with `board_w` ≥ 66 W or
any `temp_c.minshire` field ≥ 72 °C writes STOP and ends the pass with EXIT_HOT (the host program checks the STOP file before every ~0.5 s
launch). The stop-path test proves all three on live samples before any launch. No run drives the card near a PMIC over-power or
over-temperature limit: the stops sit about 4 W and 7 °C above E142's peaks on this card.

**What is E78's, byte for byte.** `check_e157.py` (before any device opens), `run_e157.py` (before every pass) and `reduce_e157.py` (before
every reduction) refuse on any difference from `predictions-e157.json` › `harness`: E78's card code (`lib.sh`, `e78_common.py`, `run_e78.py`,
`reduce_e78.py`, `kinds.json`), E128's guard, Q136(w)'s checker and table, the workload's host source (`0f53a7d5…`), Q139(k)'s wrapper, patch,
build script, `ccheck.py`, `pick6.py` and the reference engine `accum.c`, E157's card files, the pools (manifests, SHA256SUMS, the predictions
file, all 56 tiles) and, on the box, the binaries: `sparsity_host` `e0fbecce…` and `ettelem` `8008f96f…` (the ones E142, E155 and E156 ran on
this card), the kernel `990807f4…`, and Q139(k)'s patched host `4f0956ce…` (built on aifoundry1 by `build_host_ccheck.sh` on Tue 3 Nov at
06:37 PST from `main.cpp` `0f53a7d5…`, its patched source `5bd029ca…`; re-read on the box at 15:56 PST, unchanged). Ported with marked changes
from E142's: `e157_common.py`, `run_e157.py`, `block_e157.sh`, `queue_e157.sh`, `session_e157.sh`, `check_e157.py`, `preflight_e157.sh`,
`smoke_gate_e157.py`, `reduce_e157.py`, `collect_e157.sh`; new: `score_e157.py` (from `score_e142.py`, with E153's rules), `selftest_e157.py`,
`make_predictions_e157.py`, `ref_errors_e157.py`.

## Device commands sent

*The owner's rules of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send, classified
READ or WRITE from the firmware source of the running build; only read-only PMIC voltage reads and the statistics reset are allowed, and
**E157 does not send the reset**.* The sending code is E142's on this card (`lib.sh` unchanged, the same `ettelem` binary through E128's guard,
the block's config reads and its one `start_sampler` call). Card 1 runs release 1.4.0 (BL2 0.22.0; E156's session read it this morning), so
the classification is et-platform `836a4ab` (BL2 0.22.0), Q136(w)'s table (`tools/claims-v3/dmcmd_table.json`):

| command (id) | sent by | class | firmware source (et-platform `836a4ab`, `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| GET_MODULE_STATIC_TDP_LEVEL (25) | `ettelem config` (session ends, block ends) | READ | `services/thermal_power_monitor.c:339` → `services/thermal_pwr_mgmt.c:613-617`, a RAM copy |
| GET_MODULE_TEMPERATURE_THRESHOLDS (21) | `ettelem config` | READ | `thermal_power_monitor.c:438` → `thermal_pwr_mgmt.c:665-669`, RAM |
| GET_MODULE_POWER_STATE (23) | `ettelem config` | READ | `thermal_power_monitor.c:48` → `thermal_pwr_mgmt.c:551-555`, RAM |
| GET_ASIC_FREQUENCIES (53) | `ettelem config`, `ettelem sample` | READ | `services/performance.c:41` → `driver/io_pll.c:907-960`, PLL register reads |
| GET_ASIC_VOLTAGE (32) | `ettelem config`, `ettelem sample` | READ (two PMIC voltage-register reads, allowed) | `thermal_pwr_mgmt.c:1142-1222`, PVT reads and `pmic_get_voltage` → `driver/pmic_controller.c:1473-1500` → `get_pmic_reg` (an I2C register read) |
| GET_MODULE_POWER (33) | `ettelem sample` at 10 Hz | READ | `thermal_pwr_mgmt.c:984-988`, the RAM copy the SP keeps |
| GET_SP_STATS (60) | `ettelem sample` | READ | `performance.c:404-466` → `thermal_pwr_mgmt.c:2780-2784`, RAM |
| GET_MODULE_CURRENT_TEMPERATURE (27) | `ettelem sample` | READ | `thermal_pwr_mgmt.c:732-773`, PVT register reads |
| GET_MODULE_VOLTAGE (31) | `ettelem sample` | READ (nine PMIC voltage-register reads, allowed) | `thermal_pwr_mgmt.c:1010-1140` → `pmic_get_voltage` |
| SET_STATS_RUN_CONTROL (`--reset-ms`, the statistics reset) | **never sent** | WRITE (allowed, not used) | `lib.sh:154` forwards `start_sampler`'s extra arguments; `block_e157.sh`'s only call passes the file and the duration, and the guard refuses `--reset-ms` before the device opens |
| `dev_mngt_service` GET_MODULE_POWER (`lib.sh` `drain_mgmt`) | **never sent** | READ | replaced by a refusal in `block_e157.sh` |
| the host program (E78's `sparsity_host`, the heater; Q139(k)'s patched host for every measured launch: ops node only, DMA and launches; `--c-log` reads C back with one more 1 MiB `memcpyDeviceToHost`, `--c-poison` writes the host's own C buffer with one more 1 MiB `memcpyHostToDevice` before each launch), `et-who`, `et-holders`, `et-lab-manifest` | — | no device-management command | the ops node only (`createPcieDeviceLayer(true, false)`: the management node is never opened); host-side tools |

Never sent: any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset, any PMIC command
beyond the two voltage reads. **The checker** `tools/claims-v3/dmcmd_audit.py` (unchanged), from the repository root on every file the session
runs (`preflight_e157.sh`: the session's scripts, `lib.sh`, E128's guard, E78's runner and module, the host source, Q139(k)'s wrapper, patch
and build script, and on the box the patched source the build compiled): **NO-GO** without an exception, at the one conditional site E140's,
E142's and E145's lanes reviewed (`lib.sh:154`), and with the reviewed exception **GO, 32 send sites, 0 disallowed**
([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt)); the desk files (freeze, reducer, scorer,
collector, self-test, reference script, `ccheck.py`, `pick6.py`): GO, 0 send sites. The session runs the same preflight on the box before any
device opens and stops on anything but GO. **Verdict before the first launch: GO.**

## Card budget

**At most 55 card-minutes**, from the session's first device access (`E157_T0`, before its first config read) to the session-end config read.
Expected about 50: the stop-path test and the smoke about 2-3 min, then four passes of about 12-13 min (E142's 56-run passes here took
507–525 s; 76 runs scale to about 712 s, plus the C log's DMA) with 10 s between. `queue_e157.sh` starts a pass only if its projected end
(780 s until the first pass ends, then the longest measured) is inside **3,240 s** of `E157_T0` (3,300 less a 60 s reserve for the closing read)
and before **21:50 PST**; a pass in flight is never cut. Section 23 of the round's brief: no card session starts after 21:00 PST, every run ends
by 22:00 PST. It starts only with `et-who` clean on card 1, never beside another of our sessions on aifoundry1 (card 0 is not used), and with
the day's one post in `#community-lab` carrying this reservation (`using aifoundry1 card 1 for <N> h, until ~HH:MM PST`).

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__` `tools/claims-v3/e157/`, `tools/claims-v3/kinds/blind6/`
and `tools/claims-v3/ccheck/` to the same paths under `aifoundry1:nekko/`. On aifoundry1, from `~/nekko`: `python3
tools/claims-v3/e157/check_e157.py`, `bash tools/claims-v3/e157/preflight_e157.sh`, `V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e157/block_e157.sh
15710` and the smoke's dry run (no device access), the day's post carrying the reservation, then `E157_T0=$(date +%s) setsid nohup bash
tools/claims-v3/e157/session_e157.sh > build/e157/session.out 2>&1 < /dev/null &` from a script file. Collect on the Intel: `PY=<python with
numpy> nice -n 10 bash tools/claims-v3/e157/collect_e157.sh <copy> [<E153's primary reduction>]`.

## What was re-checked from the earlier attempt (before this commit)

- **Git and the box**: no E157 commit, registration or claim exists; on aifoundry1 (15:56 PST) no `tools/claims-v3/e157/`, no
  `kinds/blind6/`, no E157 data; `et-who`: no process holds a device node or card lock; the binaries and Q139(k)'s patched host hash as pinned.
- **The frozen inputs**: `d98d2e34` is an ancestor of origin/main; `blind6.json`, `MANIFEST`, `SHA256SUMS`, the card-1 predictions and the card
  scale equal their bytes at `d98d2e34`; every source in `make_predictions_e157.py` › `SOURCES` matches its sha256.
- **The reference errors**: `ref_errors_e157.py` re-run on the Intel reproduces `ref-errors-m8.json` to 4.5e-13 W on every row, with the same
  input hashes.
- **Corrected**: the scorer read `reference_errors.power_normal_card1`, which the freeze script no longer wrote (it writes the per-row errors as
  `power_card1`); the queue's deadline and the plan's gates were the morning's (11:20 / 10:30 / 11:30 PST), now 21:50 / 21:00 / 22:00 PST; the
  rules now follow E153's draft (the C check as the scored set's filter, the real-tile sub-rule, E153's minimum tile counts, K1-D as the critic's
  0.05 W on Q139(u)'s footing with Welch's beside; the card scale's registered form is the zeros level, the critic's "its own zeros ... reads").
- **The C reference's domain** (`ccheck.py domain`, n = 750,000, every one of the 56 tiles; [`ccheck-domain.txt`](ccheck-domain.txt)): re-run
  on the Intel, equal line for line to the earlier attempt's: **56 of 56 inside** (finite normal or zero operands, no Inf, overflow, clamp or
  flushed sum at any op up to n), **36 with first-read notes**: those launches are the first silicon read of their value range (exponent
  spreads wider than E104's, more distinct magnitudes, full-range int8, 14 int8 tiles whose words wrap at 32 bits by n), so a FAIL there can
  be the reference's rather than the launch's (Q139(k)'s § What this does not establish); PC still counts it as not checked.
- **On the box** (16:15 PST, no device opened): `check_e157.py` HARNESS OK on 90 files (the 86 above and the 4 binaries); `preflight_e157.sh`
  GO, 32 send sites, 0 disallowed (the reviewed `lib.sh:154` exception); the 56 tiles against their sha256; the dry runs of a pass (76 runs,
  every measured launch through `tools/claims-v3/ccheck/sparsity_ccheck.sh`) and of the smoke exit 0; the stop-path test's dry run ends as a dry
  run must (its watcher needs live samples).

## Files

All in `tools/claims-v3/e157/`: `README.md` (this); `make_predictions_e157.py` → `predictions-e157.json` (the freeze, with every file's
sha256); `ref_errors_e157.py` → `ref-errors-m8.json` (M8's nested per-row errors); `e157_common.py`, `run_e157.py`, `block_e157.sh`,
`queue_e157.sh`, `session_e157.sh`, `check_e157.py`, `preflight_e157.sh`, `smoke_gate_e157.py` (the box); `reduce_e157.py`, `collect_e157.sh`,
`score_e157.py` (the desk); `selftest_e157.py`, `selftest.txt`, `planned-intervals.txt`; `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`; `ccheck-domain.txt`. The
pools: `tools/claims-v3/kinds/blind6/`, `tools/claims-v3/kinds/blind5/`. Data: `docs/reports/data/2026-11-03-e157-blind6-card1/`.

## Amendments

*(none)*
