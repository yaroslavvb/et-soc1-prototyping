# E141: blind pool 5 on aifoundry3 card 0 - M7's power and heat, frozen before the claim, scored on the card its predictions are written for, with M6 and M5 beside it (Q138, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, in Q138 (lane `a3-e141-blind5`), before the claim of aifoundry3 and before any card
has run a tile of blind pool 5 on aifoundry3. The owner's words that evening: "feel free to settle any unanswered questions regarding
horace's power model", with Q137's goal, "to predict the power requirement and heat generation of various kinds of numeric computations as
accurately as possible". **It answers item 6 of the kinds page's section 11**, "a power model across kinds"
([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)): the blind test of
Q138(m)'s M7 on a fifth pool written by someone else, on the card where M7's power has no card term and where E140 tested M6 on pool 4.
**Every prediction E141 scores is frozen elsewhere, before this was written**: the model M7
([`m7.json`](../../../docs/reports/data/2026-11-02-q138m-model/m7.json), Q138(m), `3a210f2b`, 19:21 PST), the pool
([`../kinds/blind5/`](../kinds/blind5/README.md), Q138(b)'s 36 tiles by an independent designer, copied unchanged into the tree with M7's, M6's
and M5's predictions by Q138(x), `dac39d97`, 20:24 PST), and the aifoundry3 predictions
[`predictions-blind5-aifoundry3.json`](../kinds/blind5/predictions-blind5-aifoundry3.json) (`396d3366…`). E141 adds no prediction. What it
adds is frozen in [`predictions-e141.json`](predictions-e141.json), written by [`make_predictions_e141.py`](make_predictions_e141.py) from the
committed files it names (each checked by sha256): the plan, the stops, the rules, the reference errors behind them and the hash of every
file the box runs. Any change after this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry3 card 0 only** (no
`V3_DEVICE`, `/run/lock/etsoc-shire0.lock`), 600 MHz as its boot-time TDP of 0 latches it, TDP 0 W and threshold 65 °C as read, never set.
**E141 sends no write command of any kind** (§ Device commands sent).*

## What it does to predicting power and heat

M7 predicts, from the bytes a matmul multiplies, its **power** D (board W over the type's own zeros at 600 MHz) and its **heat** (the die's
rise over a 4.5 s kinds run). On aifoundry3 both are M7's own footing: no card scale, and the die rise per board W is aifoundry3's 0.1186 °C/W.
**Before** (the error M7 claims for new kinds, nested leave-one-kind-out): power 0.209 W rms on the floats and 0.240 W on int8 over both
cards; **on aifoundry3's rows** fp32 0.247 W, fp16 0.162 W, int8 0.226 W (`loko-m7.json` › `families.*.band_calibration.pools`, `<fmt>|a3`);
heat on aifoundry3 0.181 / 0.159 / 0.205 °C (fp32 / fp16 / int8; `m7.json` › `heat.interval_pool_by_format_card_c`). The blind record of the
models it replaces, on pool 4 on this card (E140): M6 0.406 W rms on the priority-1 floats and 0.384 W on int8, M5 0.337 and 0.379 W, M6
biased 0.28 W high, its bands covering 19 of 25; M6's heat 0.204 / 0.164 °C (floats / int8). **After**: the blind error on pool 5 on this
card, by format, for power and for heat, with the bias and the share inside M7's frozen 95% bands, and M7 against M6 and M5 on the same
tiles. E141's reduction also feeds E142's card-term rules (X1, X2: the per-tile ratio between aifoundry1 card 1 and this card).

## The question

1. **Is M7's power on a blind pool, on the card its predictions are written for, as accurate as its nested score says?** Per format: fp32
   (P1), fp16 (P2), int8 (P3).
2. **Is it unbiased?** Floats (B1), int8 (B2). E140 found M6 too high by 0.28 W on pool 4 on this card.
3. **Do its frozen 95% bands cover?** Power (C1), heat (H4). M7's bands are rule B's (k 3.179 floats, 2.483 int8), calibrated, not yet tested.
4. **Is M7 better than M6 and M5 on the same new tiles?** (M1, M2.)
5. **Is its heat as accurate?** Per format (H1-H3), the die rise over each run's window.

## The models and the pool, frozen elsewhere

| what | file | sha256 | frozen in |
|---|---|---|---|
| the pool: 36 tiles (14 fp32, 11 fp16, 11 int8; 24 priority 1, 6 priority-2 tests, 6 anchors of its own), by an independent designer | [`blind5.json`](../kinds/blind5/blind5.json), `SHA256SUMS`, `tiles/` | `946f8493…`, `ccfab045…` | `dac39d97` (Q138(x); designed by Q138(b)) |
| M7 (floats `G8_gtr_glive`, int8 `J8_b138`, heat `H2_per_card_runlength`) | [`m7.json`](../../../docs/reports/data/2026-11-02-q138m-model/m7.json) | `bfeea822…` | `3a210f2b` |
| its nested scores, every row's error | [`loko-m7.json`](../../../docs/reports/data/2026-11-02-q138m-model/loko-m7.json) | `c30320b7…` | `3a210f2b` |
| M7's, M6's and M5's predictions for the pool on aifoundry3, D and die rise, with 95% bands | [`predictions-blind5-aifoundry3.json`](../kinds/blind5/predictions-blind5-aifoundry3.json) | `396d3366…` | `dac39d97` |

`dac39d97` precedes this commit (`git merge-base --is-ancestor dac39d97 <this commit>`), and this commit precedes the claim and the first
launch. **The band rule** is Q138(m)'s README § 3 (rule B): power half-width k × √(pool² + s² xᵀCx), k 3.179 floats and 2.483 int8; heat k_h
1.95 × pool_h. The `band_rule` string inside the predictions file is run 1's wording (Q138(m)'s C4/C5 note); the numbers are rule B's.
**Heat at the measured run length** (Q138(m)'s C8 note): the frozen dT is H2 at 4.5 s; H2 at each tile's measured run length (its ST term,
−0.0490 °C/W/s on aifoundry3, at the median T_run of the session from `runs.csv`) is reported beside it, never a verdict.

**The footing.** D as E78's reduction reads it on this card, E140's primary unchanged: `reduce_e78.py` through `reduce_e141.py`, leakage
`auto`, the board meter's dips kept, E78's run and pass gates and its aifoundry3 config gate (TDP 0 / 65 °C). That is the frame of M7's
aifoundry3 training rows (E78, E95, E115, E140 and the rest: `m6_rows.py` reads each experiment's registered primary). **The dips-removed arm
(E82 A2's definition) is reported, never the verdict** (E140 found P3's verdict arm-sensitive to it).

## The frozen predictions

D in W over the type's own zeros, and the die rise over the run in °C, aifoundry3 card 0, 600 MHz; M7 with its 95% band (scored), M6 and M5
beside (reported), copied from `predictions-blind5-aifoundry3.json` into `predictions-e141.json` › `tiles`.

| tile | case | prio | M7 D, W [95%] | M6 D | M5 D | M7 die rise, °C [95%] | M6 rise |
|---|---|---:|---|---:|---:|---|---:|
| `fp32.e4m3grid_gelu_w` | 7 few mantissa bits (E140 suspicion) | 1 | **16.73** [15.93, 17.54] | 16.73 | 16.89 | **2.22** [1.86, 2.57] | 2.21 |
| `fp32.exp_only_both` | 3 exponent-only activity (E140 miss) | 1 | **15.79** [14.97, 16.62] | 15.85 | 15.98 | **2.11** [1.75, 2.46] | 2.11 |
| `fp32.gray_stream` | 9 structured stream | 1 | **16.68** [15.88, 17.47] | 16.54 | 16.69 | **2.21** [1.86, 2.56] | 2.19 |
| `fp32.real_pythia_gelu_down` | 5 real model (pythia-70m layer 0 forward) | 1 | **22.29** [21.49, 23.09] | 22.19 | 22.37 | **2.88** [2.52, 3.23] | 2.86 |
| `fp32.real_pythia_ln1_q` | 5 real model (pythia-70m layer 0 forward) | 1 | **22.08** [21.28, 22.88] | 22.00 | 22.15 | **2.85** [2.50, 3.21] | 2.84 |
| `fp32.sorted_k` | 9 structured stream | 1 | **23.02** [22.22, 23.83] | 23.01 | 23.05 | **2.96** [2.61, 3.32] | 2.96 |
| `fp32.wideexp48_bgate_alt` | 2 spread exponents beside gated zeros (E140 miss) | 1 | **15.13** [14.30, 15.95] | 15.13 | 14.58 | **2.03** [1.68, 2.38] | 2.03 |
| `fp32.wideexp48_bgate_kblk` | 2 spread exponents beside gated zeros (E140 miss) | 1 | **13.33** [12.54, 14.13] | 13.18 | 13.39 | **1.81** [1.46, 2.17] | 1.79 |
| `fp32.wideexp48_dense` | 2 spread exponents beside gated zeros (E140 miss) | 1 | **25.66** [24.84, 26.47] | 25.73 | 25.81 | **3.28** [2.92, 3.63] | 3.28 |
| `fp32.b_exp_busy_a_const` | 3 exponent-only activity (E140 miss) | 2 | **15.59** [14.78, 16.40] | 15.50 | 15.74 | **2.08** [1.73, 2.44] | 2.07 |
| `fp32.block_sparse_k4` | 9 structured stream | 2 | **12.79** [11.99, 13.58] | 12.61 | 12.81 | **1.75** [1.40, 2.10] | 1.73 |
| `fp32.lowrank2_w` | 8 seeded realistic weights | 2 | **24.51** [23.70, 25.31] | 24.55 | 24.60 | **3.14** [2.79, 3.49] | 3.14 |
| `fp32.anchor_randn` | 0 anchor (footing) | 2 (anchor) | **24.49** [23.68, 25.29] | 24.54 | 24.57 | **3.14** [2.78, 3.49] | 3.14 |
| `fp32.anchor_zeros` | 0 anchor (footing) | 2 (anchor) | **0.00** [-0.79, 0.79] | 0.00 | 0.00 | **0.23** [-0.12, 0.59] | 0.23 |
| `fp16.pair_cancel_asign` | 1 fp16 pairs that cancel (E140 miss) | 1 | **16.83** [16.30, 17.35] | 16.95 | 16.77 | **2.23** [1.92, 2.54] | 2.24 |
| `fp16.pair_nearcancel` | 1 fp16 pairs that cancel (E140 miss) | 1 | **21.80** [21.27, 22.33] | 21.88 | 21.79 | **2.82** [2.51, 3.13] | 2.82 |
| `fp16.real_pythia_ln2_up` | 5 real model (pythia-70m layer 0 forward) | 1 | **22.09** [21.56, 22.62] | 22.16 | 22.09 | **2.85** [2.54, 3.16] | 2.85 |
| `fp16.real_pythia_qk` | 5 real model (pythia-70m layer 0 forward) | 1 | **21.10** [20.57, 21.63] | 21.12 | 21.10 | **2.73** [2.42, 3.04] | 2.73 |
| `fp16.real_pythia_softmax_v` | 5 real model (pythia-70m layer 0 forward) | 1 | **17.35** [16.83, 17.88] | 17.28 | 17.35 | **2.29** [1.98, 2.60] | 2.28 |
| `fp16.sparse24_aligned` | 9 structured stream | 1 | **12.79** [12.25, 13.32] | 13.04 | 12.80 | **1.75** [1.44, 2.06] | 1.78 |
| `fp16.sparse24_straddled` | 9 structured stream | 1 | **21.69** [21.16, 22.22] | 21.72 | 21.72 | **2.81** [2.50, 3.12] | 2.80 |
| `fp16.wideexp_bgate_alt` | 2 spread exponents beside gated zeros (E140 miss) | 1 | **13.46** [12.89, 14.03] | 13.47 | 12.86 | **1.83** [1.52, 2.14] | 1.83 |
| `fp16.exp_only` | 3 exponent-only activity (E140 miss) | 2 | **16.41** [15.86, 16.96] | 16.42 | 16.50 | **2.18** [1.87, 2.49] | 2.18 |
| `fp16.anchor_randn` | 0 anchor (footing) | 2 (anchor) | **21.87** [21.34, 22.40] | 21.95 | 21.87 | **2.83** [2.52, 3.14] | 2.83 |
| `fp16.anchor_zeros` | 0 anchor (footing) | 2 (anchor) | **0.00** [-0.52, 0.52] | 0.00 | 0.00 | **0.23** [-0.08, 0.54] | 0.23 |
| `int8.a_word_flipflop` | 6 whole-line / whole-word flip-flops (E140 miss) | 1 | **3.52** [2.95, 4.09] | 3.43 | 3.61 | **0.72** [0.32, 1.12] | 0.71 |
| `int8.b_line_flipflop_nogate` | 6 whole-line / whole-word flip-flops (E140 miss) | 1 | **6.35** [5.72, 6.98] | 6.62 | 6.61 | **1.05** [0.66, 1.45] | 1.08 |
| `int8.b_line_zero_one` | 6 whole-line / whole-word flip-flops (E140 miss) | 1 | **3.96** [3.35, 4.57] | 3.90 | 3.88 | **0.77** [0.37, 1.17] | 0.76 |
| `int8.gray_a` | 9 structured stream | 1 | **4.37** [3.73, 5.00] | 4.36 | 4.40 | **0.82** [0.42, 1.22] | 0.82 |
| `int8.real_pythia_w8a8_down` | 5 real model (pythia-70m layer 0 forward) | 1 | **6.19** [5.61, 6.77] | 6.22 | 6.22 | **1.04** [0.64, 1.44] | 1.04 |
| `int8.real_pythia_w8a8_up` | 5 real model (pythia-70m layer 0 forward) | 1 | **6.14** [5.57, 6.72] | 6.15 | 6.16 | **1.03** [0.63, 1.43] | 1.03 |
| `int8.sorted_k` | 9 structured stream | 1 | **6.01** [5.42, 6.61] | 5.95 | 5.96 | **1.01** [0.62, 1.41] | 1.01 |
| `int8.block_sparse_a` | 9 structured stream | 2 | **4.32** [3.75, 4.88] | 4.33 | 4.36 | **0.81** [0.41, 1.21] | 0.81 |
| `int8.powerlaw_w` | 8 seeded realistic weights | 2 | **6.38** [5.79, 6.96] | 6.40 | 6.39 | **1.06** [0.66, 1.46] | 1.06 |
| `int8.anchor_full` | 0 anchor (footing) | 2 (anchor) | **7.00** [6.41, 7.58] | 6.96 | 6.95 | **1.13** [0.73, 1.53] | 1.12 |
| `int8.anchor_zeros` | 0 anchor (footing) | 2 (anchor) | **0.00** [-0.56, 0.56] | 0.00 | 0.00 | **0.30** [-0.10, 0.70] | 0.30 |

## Decision rules

On the primary reduction (E140's: E78's `reduce_e78.py` unchanged through `reduce_e141.py`, leakage `auto`, dips kept, E78's run and pass
gates), over kept passes. A tile's measured value is its mean over the passes it ran in; a tile with fewer than 2 kept passes is left out and
named. **Fewer than 2 kept passes: every rule NOT SCORED** (E140's). Reference errors: M7's nested leave-one-kind-out errors of every
**aifoundry3** power row of the format (`loko-m7.json` › `families.<family>.row_errors`, card `a3`: 143 fp32, 104 fp16, 64 int8 rows), copied
into `predictions-e141.json` › `reference_errors.power_a3`; heat: a deterministic normal sample of 2,000 points with M7's nested aifoundry3
heat rms of the format (`m7.json` › `heat.interval_pool_by_format_card_c`: 0.181, 0.159, 0.205 °C), as E140 and E142 do (no per-row heat error
is committed). Bootstrap: 20,000 draws, seed 14100 plus the rule's characters (`score_e141.py`).

| rule | quantity | set | verdict |
|---|---|---|---|
| **E141-P1** | power D | priority-1 fp32 (9), at least 5 | rms(D − M7) against the 2.5–97.5% range of the rms of 9 draws with replacement from the aifoundry3 fp32 reference errors: **PASS** at or below the 97.5% point, **FAIL** above; below the 2.5% point is reported as "better than the nested score says" |
| **E141-P2** | power D | priority-1 fp16 (8), at least 5 | as P1, fp16's |
| **E141-P3** | power D | priority-1 int8 (7), at least 4 | as P1, int8's |
| **E141-B1** | bias | priority-1 floats (17), at least 5 | mean(D − M7) against the 2.5–97.5% range of the mean of as many draws (the same format mix): **PASS** inside; **FAIL HIGH** below it (M7 predicts too much), **FAIL LOW** above it |
| **E141-B2** | bias | priority-1 int8 (7), at least 4 | as B1 |
| **E141-C1** | power coverage | the 30 non-anchor tiles | **PASS** if the number inside M7's frozen 95% band is at least the 2.5% point of Binomial(n, 0.95) (26 of 30), **FAIL** if fewer; NOT SCORED under 10 |
| **E141-M1** | M7 against M6 | the 24 priority-1 tiles | d = rms(M7's errors) − rms(M6's), 95% interval by a bootstrap over tiles: **BETTER** if its upper bound < 0, **WORSE** if its lower bound > 0, else **NOT RESOLVED** |
| **E141-M2** | M7 against M5 | the 24 priority-1 tiles | as M1 |
| **E141-H1** | die rise `dT_win` | priority-1 fp32 (9), at least 5 | rms(dT − M7) against the 2.5–97.5% range of the rms of 9 draws from the normal reference (0.181 °C): PASS / FAIL as P1 |
| **E141-H2** | die rise | priority-1 fp16 (8), at least 5 | as H1 (0.159 °C) |
| **E141-H3** | die rise | priority-1 int8 (7), at least 4 | as H1 (0.205 °C) |
| **E141-H4** | heat coverage | the 30 non-anchor tiles | as C1, M7's frozen dT band (26 of 30) |

**Reported, never a verdict** (`scored.json`, `results.md`): every rule on **the dips-removed arm** (E82 A2), scored alone too
(`scored-nodips.json`); every tile's measured D and rise with its passes; M6's and M5's rms, bias and coverage beside M7's on every set and
per format; each verdict at every arm (leakage 0.1994, 0.3803 and 0 W/°C; dips removed; pass gates opened: E140's arms, `collect_e141.sh`) and
P1–P3 against both cards' reference rows; the priority-2 tests; the pool's six anchors (its zeros tiles against E78's built-in zeros, its
random tiles against M7); E78's anchors against E140's on this card; the errors by case; heat at the measured run length; the die rise per
board W against M7's 0.1186 °C/W.

**Why these lines, before the data.** They are E142's (themselves E140's and E115's), so the three blind tests of pool 5 and the two of
this card read alike, with aifoundry3's reference rows because M7's bands are per card. The bias rule is the sharp test of E140's kind of
miss (a one-sided −0.28 W); the comparison with the models M7 replaced is what E140 found decisive (M5 better than M6 blind).

## Precision, before the data

[`planned-intervals.txt`](planned-intervals.txt), at the registered draws: **P1** 0.087–0.545 W (median 0.194) over 9 fp32 tiles (aifoundry3's
fp32 reference errors have heavy tails); **P2** 0.071–0.247 W (median 0.156) over 8 fp16; **P3** 0.093–0.361 W (median 0.210) over 7 int8;
**B1** −0.117 to +0.085 W; **B2** −0.225 to +0.103 W; **H1** 0.102–0.261 °C; **H2** 0.083–0.235 °C; **H3** 0.095–0.309 °C; C1 and H4 need 26 of
30 inside. [`selftest.txt`](selftest.txt) ([`selftest_e141.py`](selftest_e141.py), 60 simulated sessions a world on the frozen registration,
three passes, 0.05 W / 0.05 °C pass noise, bootstrap draws cut to 2,000 for speed; nothing there is a measurement): when M7 is as good as its
nested score, P1–P3 PASS in 58 of 60, B1 54, B2 60, C1 60, H1–H4 59; **twice as bad**, P1 FAILS in 13, P2 in 46, P3 in 40, C1 in 23, H1–H4 in
50–59; three times as bad, P1 in 35, P2–P3 in 53–58, C1 57, heat 58–60; with a −0.3 W bias on the floats at 1×, **B1 FAILS HIGH in 60 of 60**
while P1 fails in 4 and C1 in 1, so the bias rule is the sharp test of E140's kind of miss and P1 the weakest (fp32's wide reference). M1 and
M2 can only say BETTER where the models' predictions differ (by at most 0.6 W on this pool): in the as-good world, where M7 is right by
construction, M1 says BETTER in 10 of 60 and M2 in 45, NOT RESOLVED otherwise.

**What I expect, frozen so it can be wrong:** P1–P3 PASS; B1 PASS or FAIL HIGH (M7 still over-predicted pool 4's floats by 0.22 W out of
kind, Q138(m) § 1); B2 PASS; C1 PASS (rule B's wider bands); M1 NOT RESOLVED and M2 NOT RESOLVED or BETTER; H1–H4 PASS. The likeliest misses,
named now: the wide-exponent gate tiles (`fp32.wideexp48_bgate_alt`, `fp32.wideexp48_bgate_kblk`, `fp16.wideexp_bgate_alt`; M6's and M7's
steady-gate over-prediction), the fp16 pairs that cancel (`fp16.pair_cancel_asign`, `fp16.pair_nearcancel`), int8's whole-line flip-flops
(`int8.b_line_flipflop_nogate`, `int8.b_line_zero_one`), and on heat the small int8 rises the die's whole-degree readings floor.

**The statement the page gets, decided now.** All PASS: "on 36 tiles written by a designer who never saw the model, M7 predicted power on
aifoundry3 within X W rms (fp32), Y (fp16) and Z (int8) with no resolved bias, its 95% bands covering K of 30, and the die's rise within … °C,
as its nested score said". A FAIL is stated with the rms or bias, its interval and the tiles that carry it, by case. **No tile, prediction,
band, rule or reference error changes after this commit; only tiles that ran are scored.**

## What the rules cannot say

One card, one clock, one session. The heat scored is the 4.5 s window only. The heat reference is a normal model of the nested rms, not the
rows. A PASS fails to find a miss at this many tiles; it does not bound M7's error on kinds unlike these 36.

## What runs

| | E140 (blind pool 4, this card, today) | E142 (pool 5, aifoundry1 card 1, tonight) | E141 | why |
|---|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet | the same | **the same** | the protocol M7's rows were measured with |
| the tiles | blind pool 4's 25 | blind pool 5's 36 | **blind pool 5's 36** (`tools/claims-v3/kinds/blind5/tiles/<type>/<name>.bin`, items `<type>.<name>`) | the pool |
| anchors | E78's six three times a pass, the tie `anchor_pi` first and last | the same | the same; the pool's six anchors are ordinary tiles | drift, the zeros D is measured over |
| a pass | 45 runs | 56 runs | **56 runs**: the tie, three segments of the six anchors and 12 tiles, the tie; `Random("E141\|aifoundry3\|<pass>")` | |
| passes | 14010–14013 (438–469 s) | 14210–14214 | **14110–14113, 14114 if it fits** (the budget rule decides), at least two kept | 50 card-minutes |
| stop-path test | none | 14202 | **14102**, before the smoke, no launch: the guard's die stop (at 1.0 °C), its board stop (at 1.0 W) and the in-run watcher's board stop (at 1.0 W) must each end `run_e141.py` with EXIT_HOT on a live sample read at most 2.0 s after it was taken (`smoke_gate_e141.py`) | E139's stop watched a file written at pass end |
| smoke | 14001 | 14201 | **14101**: the tie, `fp32.zeros`, `fp32.randn`, `fp32.wideexp48_dense` (the hottest predicted tile), `fp32.anchor_zeros`, `fp16.pair_cancel_asign`, `fp16.zeros`, `int8.b_line_flipflop_nogate`, `int8.zeros`, 2 s each, no preheat; gated by `smoke_gate_e141.py` (records ok, cycles per op within 0.5%, 600 MHz, config 0 W / 65 °C / 600 MHz, dumped pool tiles equal their sha256, `since_reset_ms` −1, at least 100 live samples, board below the stop) | E142's smoke, on this card's config |
| stops | die 70 °C (`run_e78 --max-c`), board 65 W (E130's guard) | board 66 W, hottest shire field 72 °C, live, plus the in-run watcher | **board ≥ 65 W or `temp_c.minshire[0]` ≥ 70 °C** (E140's values), read by the main path between runs and by the in-run watcher every 0.1 s during runs (the host program checks STOP before each ~0.5 s launch); `run_e78`'s `--max-c 70` | E140's passes here peaked at 54.17 W and 62 °C; the pool's hottest tile is predicted 1.2 W above `fp32.anchor_randn` |
| config reads | both ends of every pass, the session's | the same | **the same**: session start, both ends of the stop test, the smoke and every pass, session end | |
| data | `build/claims-v3/aifoundry3/kinds/p140<nn>/` | `…/aifoundry1-c1/e142/p142<nn>/` | `build/claims-v3/aifoundry3/e141/p141<nn>/` in `~/aifoundry`; results `docs/reports/data/2026-11-02-e141-blind5-aifoundry3/` | |

**Stops (registered, and why they read live samples).** The block's sampler (`ettelem sample --seconds --every-ms 100` through E128's guard)
writes one JSON line a sample into `<pass>/telemetry.jsonl.raw` while it runs. (1) The main path (E145's guard, as E142 copied it):
`run_e78.py` reads the newest line through `last_sample()` before every launch and every 0.1 s while it waits; a line with `board_w` ≥ 65 W or
`temp_c.minshire[0]` ≥ 70 °C writes STOP (with the line's `t_ms` and its age) and ends the pass with EXIT_HOT. (2) **The in-run watcher**
(E142's): `run_e78.py` blocks on the host program for the 4 s of a run, so a daemon thread reads the same file every 0.1 s for the whole pass
and on the same two stops writes STOP; the host program ends its launch loop at the next launch (`main.cpp` `repeatFor`), and the main path
then ends the pass. Both read only the sampler's file. **E141's one change to E142's stop code**: the die stop reads `minshire[0]`, not the
largest of the three `minshire` fields, because on aifoundry3 `minshire[2]` is a high-water latch that read a constant 87 °C in every sample
of E140's passes (`docs/reports/data/2026-11-02-e140-blind4/aifoundry3/kinds/p14012/telemetry.jsonl.gz`: `minshire` [56–62, 46, 87]); the
maximum would stop every pass at once. `minshire[0]` is the field `run_e78.py`'s own `--max-c` reads. The stop-path test proves both paths on
live samples before any launch.

**What is E78's, byte for byte.** `check_e141.py` (before any device opens), `run_e141.py` (before every pass) and `reduce_e141.py` (before
every reduction) refuse on any difference from `predictions-e141.json` › `harness`: E78's card code (`lib.sh` `033d0776…`, `e78_common.py`
`c58923a5…`, `run_e78.py` `f3efd783…`, `reduce_e78.py` `6a158cee…`, `kinds.json` `9586568f…`), E128's guard `c2c4ab76…`, Q136(w)'s checker
`f29e91ca…` and table `50168632…`, the workload's host source `0f53a7d5…` (the box's copy is the same), E141's card files, the pool (manifest,
SHA256SUMS, the predictions file, all 36 tiles) and, on the box, the two binaries (`sparsity_host` `20e760c2…`, `ettelem` `16037641…`, the ones
E140 and E147 ran on this card today; read at 21:13 PST). The box files are E142's with the card, the seed tag, the pass numbers, the stop
values and the die field changed (each change marked); `reduce_e141.py` and `collect_e141.sh` are E140's on this card (pool 5's items, its
registration file); `score_e141.py` is E142's with aifoundry3's references and no card-term rules; `selftest_e141.py` and
`make_predictions_e141.py` are E142's, ported. **A no-device dry run** of this commit's files, byte-identical on the box (`check_e141.py`
HARNESS OK, 59 files), ran before this commit at 21:16 PST: one pass (58 launches, 36 on pool-5 tiles; `V3_DRY=1`), the smoke (9 launches) and
the queue's budget rule on stub blocks; `preflight_e141.sh` GO and `e141_common.py --verify` 0 problems on the box.

## Device commands sent

*The owner's rules of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send, classified
READ or WRITE from the firmware source of the running build; only read-only PMIC voltage reads and the statistics reset are allowed, and
**E141 does not send the reset**.* The sending code is E142's and E140's (`lib.sh` unchanged, the same `ettelem` binary E140 and E147 ran on
this card today, through E128's guard; the block's config reads and its one `start_sampler` call), classified from et-platform `836a4ab`
(BL2 0.22.0; Q136(w)'s table `dmcmd_table.json`, its handlers read again for E142 tonight):

| command (id) | sent by | class | firmware source (et-platform `836a4ab`, `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| GET_MODULE_STATIC_TDP_LEVEL (25) | `ettelem config` (session ends, block ends) | READ | `services/thermal_power_monitor.c:339` → `services/thermal_pwr_mgmt.c:613-617`, a RAM copy |
| GET_MODULE_TEMPERATURE_THRESHOLDS (21) | `ettelem config` | READ | `thermal_power_monitor.c:438` → `thermal_pwr_mgmt.c:665-669`, RAM |
| GET_MODULE_POWER_STATE (23) | `ettelem config` | READ | `thermal_power_monitor.c:48` → `thermal_pwr_mgmt.c:551-555`, RAM |
| GET_ASIC_FREQUENCIES (53) | `ettelem config`, `ettelem sample` | READ | `services/performance.c:41` → `perf_mgmt.c:276` → `driver/io_pll.c:907-960`, PLL register reads |
| GET_ASIC_VOLTAGE (32) | `ettelem config`, `ettelem sample` | READ (two PMIC voltage-register reads, allowed) | `thermal_power_monitor.c:192` → `thermal_pwr_mgmt.c:1142-1222`, PVT reads and `pmic_get_voltage` → `driver/pmic_controller.c:1473-1500` (an I2C register read) |
| GET_MODULE_POWER (33) | `ettelem sample` at 10 Hz | READ | `thermal_power_monitor.c:142` → `thermal_pwr_mgmt.c:984-988`, the RAM copy the SP keeps |
| GET_SP_STATS (60) | `ettelem sample` | READ | `performance.c:404-466` → `thermal_pwr_mgmt.c:2780-2784`, RAM |
| GET_MODULE_CURRENT_TEMPERATURE (27) | `ettelem sample` | READ | `thermal_power_monitor.c:545` → `thermal_pwr_mgmt.c:732-773`, PVT register reads |
| GET_MODULE_VOLTAGE (31) | `ettelem sample` | READ (nine PMIC voltage-register reads, allowed) | `thermal_power_monitor.c:243` → `thermal_pwr_mgmt.c:1010-1140` → `pmic_get_voltage` |
| SET_STATS_RUN_CONTROL (`--reset-ms`, the statistics reset) | **never sent** | WRITE (allowed, not used) | `lib.sh:154` forwards `start_sampler`'s extra arguments; `block_e141.sh`'s only call passes the file and the duration, and the guard refuses `--reset-ms` before the device opens |
| `dev_mngt_service` GET_MODULE_POWER (`lib.sh` `drain_mgmt`) | **never sent** | READ | replaced by a refusal in `block_e141.sh` |
| the host program `sparsity_host` (ops node: DMA, launches), the heater (the same binary), `et-who`, `et-holders`, `et-lab-manifest` | — | no device-management command | the ops node only; host-side tools |

Never sent: any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset. **The
checker** `tools/claims-v3/dmcmd_audit.py` (unchanged), from the repository root on every file the session runs (`preflight_e141.sh`):
**NO-GO** without an exception, at the one conditional site E140's, E142's and E145's lanes reviewed (`lib.sh:154`), and with the reviewed
exception **GO, 32 send sites, 0 disallowed** ([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt));
the desk files (`reduce_e141.py`, `score_e141.py`, `collect_e141.sh`, `make_predictions_e141.py`, `selftest_e141.py`) send nothing (GO, 0
sites). The session runs the same preflight on the box before any device opens and stops on anything but GO. **Residual (Q136(w)'s table
caveat, E130's A1):** aifoundry3 runs a non-public thermal firmware build first flashed on 7 Oct 2026, so these classes rest on `836a4ab`'s
handlers and on these reads' unchanged behaviour on this card; if the session-start `ettelem config` or the smoke's telemetry comes back in
another form than E147's session read tonight (the same fields, TDP 0 W / 65 °C / 600 MHz, `since_reset_ms` −1), the smoke gate fails and no
pass runs. **Verdict before the first launch: GO.**

## Card budget

**At most 50 card-minutes**, from the session's first device access (`E141_T0`, before its first config read) to the session-end config
read. Expected about 43–47: the stop-path test and the smoke about 2 min, then four passes of about 9.5–10 min (E140's 45-run passes here took
438–469 s; 56 runs scale that to 545–584 s) with 10 s between. `queue_e141.sh` starts a pass only if its projected end (620 s until the first
pass ends, then the longest measured) is inside **2,940 s** of `E141_T0` (3,000 less a 60 s reserve for the closing read) and before
**23:40 PST**; a pass in flight is never cut. No session starts after 23:00 PST; every run ends by 23:50 PST. It starts only after E147 has
released card 0 (20:57:44 PST), with `et-who` clean, and with the day's post in `#community-lab` rewritten to carry this reservation.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__ tools/claims-v3/e141/`, `tools/claims-v3/kinds/blind5/`,
`tools/claims-v3/e128/ettelem_guard.sh`, `tools/claims-v3/dmcmd_audit.py` and `dmcmd_table.json` to the same paths under `aifoundry3:aifoundry/`.
On aifoundry3, from `~/aifoundry`: `python3 tools/claims-v3/e141/check_e141.py`, `bash tools/claims-v3/e141/preflight_e141.sh`, the day's post
rewritten, then `E141_T0=$(date +%s) setsid nohup bash tools/claims-v3/e141/session_e141.sh > build/e141/session.out 2>&1 < /dev/null &` from a
script file. Collect on the Intel: `PY=<python with numpy> nice -n 10 bash tools/claims-v3/e141/collect_e141.sh <copy>`.

## Files

All in `tools/claims-v3/e141/`: `README.md` (this); `make_predictions_e141.py` → `predictions-e141.json` (the freeze, with every file's
sha256); `e141_common.py`, `run_e141.py`, `block_e141.sh`, `queue_e141.sh`, `session_e141.sh`, `check_e141.py`, `preflight_e141.sh`,
`smoke_gate_e141.py` (the box); `reduce_e141.py`, `collect_e141.sh`, `score_e141.py` (the desk); `selftest_e141.py`, `selftest.txt`,
`planned-intervals.txt`; `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`. The pool: `tools/claims-v3/kinds/blind5/`. Data:
`docs/reports/data/2026-11-02-e141-blind5-aifoundry3/`.

## Amendments

*(none)*
