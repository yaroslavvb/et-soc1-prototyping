# E142: blind pool 5 on aifoundry1 card 1 - M7's power and heat, frozen before the claim, scored on the second card with M6 and M5 beside it (Q138, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, in Q138 (lane `a1c1-e142-blind5`), before the claim of aifoundry1 card 1 and before any
card has run a tile of blind pool 5 on this card. The owner's words that evening: "feel free to settle any unanswered questions regarding
horace's power model", with Q137's goal, "to predict the power requirement and heat generation of various kinds of numeric computations as
accurately as possible". **It answers item 6 of the kinds page's section 11**, "a power model across kinds"
([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)), and the first
of its "After Q137, the next steps in order": a refit "tested on a fifth pool written by someone else, on a second card". **Every prediction
E142 scores is frozen elsewhere, before this was written**: the model M7 ([`m7.json`](../../../docs/reports/data/2026-11-02-q138m-model/m7.json),
Q138(m), `3a210f2b`, 19:21 PST), the pool ([`../kinds/blind5/`](../kinds/blind5/README.md), Q138(b)'s 36 tiles by an independent designer,
copied unchanged into the tree with M7's, M6's and M5's predictions by Q138(x), `dac39d97`, 20:24 PST), and the card-1 predictions
[`predictions-blind5-aifoundry1c1.json`](../kinds/blind5/predictions-blind5-aifoundry1c1.json) (`87d0ffd2…`). E142 adds no prediction. What it
adds is frozen in [`predictions-e142.json`](predictions-e142.json), written by [`make_predictions_e142.py`](make_predictions_e142.py) from the
committed files it names (each checked by sha256): the plan, the stops, the rules, the reference errors behind them and the hash of every file
the box runs. Any change after this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry1 card 1 only**
(`V3_DEVICE=1`, `aifoundry1-c1`, `/run/lock/etsoc-shire1.lock`), 600 MHz, TDP 65 W and threshold 65 °C as read, never set. **E142 sends no
write command of any kind** (§ Device commands sent).*

## What it does to predicting power and heat

M7 predicts, from the bytes a matmul multiplies, its **power** D (board W over the type's own zeros at 600 MHz) and its **heat** (the die's
rise over a 4.5 s kinds run). On this card both go through **the card term**, one model-free scale per family (D on card 1 = 0.9711 × D on
aifoundry3 for the floats, 0.9735 for int8) and card 1's own die rise per board W (0.1151 °C/W). **Before** (the error M7 claims for new
kinds, nested leave-one-kind-out on its 637 rows): power 0.209 W rms on the floats and 0.240 W on int8 (on card 1's rows: fp32 0.214, fp16
0.188, int8 0.255 W); heat on card 1 0.352 / 0.355 / 0.141 °C (fp32 / fp16 / int8); the card term itself predicts card 1's D at 0.175 W rms
on 92 paired float kinds. The blind record of the models it replaces, on pool 4 (E140, aifoundry3): M6 0.406 W rms on the floats and 0.384 W
on int8, M5 0.337 and 0.379 W, M6's bands covering 19 of 25. **After**: the blind error on pool 5 on this card, by format, for power and for
heat, with the bias and the share inside M7's frozen 95% bands, and M7 against M6 and M5 on the same tiles. With E141 (the same pool on
aifoundry3), the per-tile ratio between the cards tests the card term directly (X1, X2).

## The question

1. **Is M7's power on a blind pool, on the second card, as accurate as its nested score says?** Per format: fp32 (P1), fp16 (P2), int8 (P3).
2. **Is it unbiased?** Floats (B1), int8 (B2). E140 found M6 too high by 0.28 W on pool 4.
3. **Do its frozen 95% bands cover?** Power (C1), heat (H4). M7's bands are rule B's (k 3.179 floats, 2.483 int8), calibrated, not yet tested.
4. **Is M7 better than M6 and M5 on the same new tiles?** (M1, M2.)
5. **Is its heat as accurate?** Per format (H1-H3), the die rise over each run's window.
6. **Does the card term hold?** (X1, X2: scored only with E141's committed reduction; else handed on.)

## The models and the pool, frozen elsewhere

| what | file | sha256 | frozen in |
|---|---|---|---|
| the pool: 36 tiles (14 fp32, 11 fp16, 11 int8; 24 priority 1, 6 priority-2 tests, 6 anchors of its own), by an independent designer | [`blind5.json`](../kinds/blind5/blind5.json), `SHA256SUMS`, `tiles/` | `946f8493…`, `ccfab045…` | `dac39d97` (Q138(x); designed by Q138(b)) |
| M7 (floats `G8_gtr_glive`, int8 `J8_b138`, card term `C0_M5_E78E82_family`, heat `H2_per_card_runlength`) | [`m7.json`](../../../docs/reports/data/2026-11-02-q138m-model/m7.json) | `bfeea822…` | `3a210f2b` |
| its nested scores, every row's error | [`loko-m7.json`](../../../docs/reports/data/2026-11-02-q138m-model/loko-m7.json) | `c30320b7…` | `3a210f2b` |
| M7's, M6's and M5's predictions for the pool on card 1, D and die rise, with 95% bands | [`predictions-blind5-aifoundry1c1.json`](../kinds/blind5/predictions-blind5-aifoundry1c1.json) | `87d0ffd2…` | `dac39d97` |

`dac39d97` precedes this commit (`git merge-base --is-ancestor dac39d97 <this commit>`), and this commit precedes the claim and the first
launch. **The band rule** is Q138(m)'s README § 3 (rule B): power half-width k × √(pool² + s² xᵀCx), k 3.179 floats and 2.483 int8; heat k_h
1.95 × pool_h. The `band_rule` string inside the predictions file is run 1's wording (Q138(m)'s C4/C5 note); the numbers are rule B's.
**Heat at the measured run length** (Q138(m)'s C8 note, "For E142"): the frozen dT is H2 at 4.5 s; card 1's runs are about 4.46 s, where H2's
own run-length term adds about +0.0057 °C per board W. The registered prediction stays the frozen one; H2 at each tile's measured run length
(the ST term, −0.1548 °C/W/s on card 1, at the median T_run of the session, read from `runs.csv` as `fit_m6.heat_rows` reads it) is reported
beside it, never a verdict.

**The footing.** D as E78's reduction reads it on this card, with card 1's frame: E131's reduction (`reduce_e131.py`) ported, card 1's 65/65
config read accepted, the board meter's launch-gap dips removed (E82 A2), leakage frozen at E82's 0.2414 W/°C. That is the frame of M7's
card-1 training rows (E82, E131 and the rest: `m6_rows.py` reads each experiment's registered primary, `e131.json` among them).

## The frozen predictions

D in W over the type's own zeros, and the die rise over the run in °C, aifoundry1 card 1, 600 MHz; M7 with its 95% band (scored), M6 and
M5 beside (reported), copied from `predictions-blind5-aifoundry1c1.json` into `predictions-e142.json` › `tiles`.

| tile | case | prio | M7 D, W [95%] | M6 D | M5 D | M7 die rise, °C [95%] |
|---|---|---:|---|---:|---:|---|
| `fp32.e4m3grid_gelu_w` | 7 few mantissa bits | 1 | **16.25** [15.55, 16.95] | 16.24 | 16.40 | **2.08** [1.39, 2.76] |
| `fp32.exp_only_both` | 3 exponent-only activity | 1 | **15.34** [14.62, 16.06] | 15.39 | 15.51 | **1.97** [1.29, 2.66] |
| `fp32.gray_stream` | 9 structured stream | 1 | **16.19** [15.50, 16.88] | 16.06 | 16.21 | **2.07** [1.39, 2.76] |
| `fp32.real_pythia_gelu_down` | 5 real model | 1 | **21.65** [20.95, 22.34] | 21.54 | 21.72 | **2.70** [2.01, 3.38] |
| `fp32.real_pythia_ln1_q` | 5 real model | 1 | **21.44** [20.75, 22.14] | 21.36 | 21.51 | **2.67** [1.99, 3.36] |
| `fp32.sorted_k` | 9 structured stream | 1 | **22.36** [21.66, 23.06] | 22.34 | 22.39 | **2.78** [2.09, 3.47] |
| `fp32.wideexp48_bgate_alt` | 2 spread exponents beside gated zeros | 1 | **14.69** [13.97, 15.41] | 14.70 | 14.16 | **1.90** [1.21, 2.58] |
| `fp32.wideexp48_bgate_kblk` | 2 spread exponents beside gated zeros | 1 | **12.95** [12.26, 13.64] | 12.80 | 13.01 | **1.70** [1.01, 2.38] |
| `fp32.wideexp48_dense` | 2 spread exponents beside gated zeros | 1 | **24.92** [24.20, 25.63] | 24.99 | 25.07 | **3.08** [2.39, 3.76] |
| `fp32.anchor_randn` | 0 anchor | 2 (anchor) | **23.78** [23.08, 24.48] | 23.83 | 23.86 | **2.94** [2.26, 3.63] |
| `fp32.anchor_zeros` | 0 anchor | 2 (anchor) | **0.00** [-0.68, 0.68] | 0.00 | 0.00 | **0.21** [-0.48, 0.89] |
| `fp32.b_exp_busy_a_const` | 3 exponent-only activity | 2 | **15.14** [14.43, 15.84] | 15.06 | 15.29 | **1.95** [1.26, 2.63] |
| `fp32.block_sparse_k4` | 9 structured stream | 2 | **12.42** [11.73, 13.10] | 12.25 | 12.44 | **1.64** [0.95, 2.32] |
| `fp32.lowrank2_w` | 8 seeded realistic weights | 2 | **23.80** [23.10, 24.50] | 23.85 | 23.89 | **2.95** [2.26, 3.63] |
| `fp16.pair_cancel_asign` | 1 fp16 pairs that cancel | 1 | **16.34** [15.73, 16.95] | 16.46 | 16.29 | **2.09** [1.39, 2.78] |
| `fp16.pair_nearcancel` | 1 fp16 pairs that cancel | 1 | **21.17** [20.56, 21.78] | 21.25 | 21.16 | **2.64** [1.95, 3.33] |
| `fp16.real_pythia_ln2_up` | 5 real model | 1 | **21.45** [20.84, 22.06] | 21.52 | 21.45 | **2.67** [1.98, 3.37] |
| `fp16.real_pythia_qk` | 5 real model | 1 | **20.49** [19.88, 21.10] | 20.51 | 20.49 | **2.56** [1.87, 3.25] |
| `fp16.real_pythia_softmax_v` | 5 real model | 1 | **16.85** [16.25, 17.46] | 16.78 | 16.85 | **2.15** [1.45, 2.84] |
| `fp16.sparse24_aligned` | 9 structured stream | 1 | **12.42** [11.80, 13.03] | 12.67 | 12.43 | **1.63** [0.94, 2.33] |
| `fp16.sparse24_straddled` | 9 structured stream | 1 | **21.07** [20.45, 21.68] | 21.09 | 21.10 | **2.63** [1.94, 3.32] |
| `fp16.wideexp_bgate_alt` | 2 spread exponents beside gated zeros | 1 | **13.07** [12.43, 13.71] | 13.09 | 12.49 | **1.71** [1.02, 2.40] |
| `fp16.anchor_randn` | 0 anchor | 2 (anchor) | **21.24** [20.63, 21.85] | 21.31 | 21.24 | **2.65** [1.96, 3.34] |
| `fp16.anchor_zeros` | 0 anchor | 2 (anchor) | **0.00** [-0.60, 0.60] | 0.00 | 0.00 | **0.20** [-0.49, 0.90] |
| `fp16.exp_only` | 3 exponent-only activity | 2 | **15.94** [15.31, 16.56] | 15.94 | 16.02 | **2.04** [1.35, 2.73] |
| `int8.a_word_flipflop` | 6 whole-line / whole-word flip-flops | 1 | **3.43** [2.79, 4.07] | 3.34 | 3.52 | **0.66** [0.39, 0.94] |
| `int8.b_line_flipflop_nogate` | 6 whole-line / whole-word flip-flops | 1 | **6.18** [5.49, 6.87] | 6.44 | 6.43 | **0.98** [0.70, 1.25] |
| `int8.b_line_zero_one` | 6 whole-line / whole-word flip-flops | 1 | **3.85** [3.18, 4.53] | 3.80 | 3.78 | **0.71** [0.44, 0.99] |
| `int8.gray_a` | 9 structured stream | 1 | **4.25** [3.55, 4.95] | 4.25 | 4.29 | **0.76** [0.48, 1.03] |
| `int8.real_pythia_w8a8_down` | 5 real model | 1 | **6.02** [5.38, 6.67] | 6.06 | 6.05 | **0.96** [0.69, 1.24] |
| `int8.real_pythia_w8a8_up` | 5 real model | 1 | **5.98** [5.33, 6.63] | 5.99 | 6.00 | **0.96** [0.68, 1.23] |
| `int8.sorted_k` | 9 structured stream | 1 | **5.85** [5.19, 6.52] | 5.80 | 5.81 | **0.94** [0.67, 1.22] |
| `int8.anchor_full` | 0 anchor | 2 (anchor) | **6.81** [6.16, 7.46] | 6.78 | 6.77 | **1.05** [0.78, 1.33] |
| `int8.anchor_zeros` | 0 anchor | 2 (anchor) | **0.00** [-0.63, 0.63] | 0.00 | 0.00 | **0.27** [-0.01, 0.54] |
| `int8.block_sparse_a` | 9 structured stream | 2 | **4.20** [3.56, 4.84] | 4.22 | 4.25 | **0.75** [0.48, 1.03] |
| `int8.powerlaw_w` | 8 seeded realistic weights | 2 | **6.21** [5.55, 6.86] | 6.23 | 6.22 | **0.98** [0.71, 1.26] |

## Decision rules

On the primary reduction (E78's `reduce_e78.py` unchanged through `reduce_e142.py`: leakage 0.2414 W/°C, dips removed, E78's run and pass
gates, card 1's config gate), over kept passes. A tile's measured value is its mean over the passes it ran in; a tile with fewer than 2 kept
passes is left out and named. **Fewer than 2 kept passes: every rule NOT SCORED** (E140's). Reference errors: M7's nested leave-one-kind-out
errors of every **card-1** power row of the format (`loko-m7.json` › `families.<family>.row_errors`, card `c1`: 143 fp32, 125 fp16, 58 int8
rows), copied into `predictions-e142.json` › `reference_errors.power_card1`; heat: a deterministic normal sample of 2,000 points with M7's
nested card-1 heat rms of the format (`m7.json` › `heat.interval_pool_by_format_card_c`), as E140 did for M6 (no per-row heat error is
committed). Bootstrap: 20,000 draws, seed 14200 plus the rule's characters (`score_e142.py`).

| rule | quantity | set | verdict |
|---|---|---|---|
| **E142-P1** | power D | priority-1 fp32 (9), at least 5 | rms(D − M7) against the 2.5–97.5% range of the rms of 9 draws with replacement from the card-1 fp32 reference errors: **PASS** at or below the 97.5% point, **FAIL** above; below the 2.5% point is reported as "better than the nested score says" |
| **E142-P2** | power D | priority-1 fp16 (8), at least 5 | as P1, fp16's |
| **E142-P3** | power D | priority-1 int8 (7), at least 4 | as P1, int8's |
| **E142-B1** | bias | priority-1 floats (17), at least 5 | mean(D − M7) against the 2.5–97.5% range of the mean of as many draws (the same format mix): **PASS** inside; **FAIL HIGH** below it (M7 predicts too much), **FAIL LOW** above it |
| **E142-B2** | bias | priority-1 int8 (7), at least 4 | as B1 |
| **E142-C1** | power coverage | the 30 non-anchor tiles | **PASS** if the number inside M7's frozen 95% band is at least the 2.5% point of Binomial(n, 0.95) (26 of 30), **FAIL** if fewer; NOT SCORED under 10 |
| **E142-M1** | M7 against M6 | the 24 priority-1 tiles | d = rms(M7's errors) − rms(M6's), 95% interval by a bootstrap over tiles: **BETTER** if its upper bound < 0, **WORSE** if its lower bound > 0, else **NOT RESOLVED** |
| **E142-M2** | M7 against M5 | the 24 priority-1 tiles | as M1 |
| **E142-H1** | die rise `dT_win` | priority-1 fp32 (9), at least 5 | rms(dT − M7) against the 2.5–97.5% range of the rms of 9 draws from the normal reference (0.352 °C): PASS / FAIL as P1 |
| **E142-H2** | die rise | priority-1 fp16 (8), at least 5 | as H1 (0.355 °C) |
| **E142-H3** | die rise | priority-1 int8 (7), at least 4 | as H1 (0.141 °C) |
| **E142-H4** | heat coverage | the 30 non-anchor tiles | as C1, M7's frozen dT band (26 of 30) |
| **E142-X1** | the card term, floats | non-anchor float tiles with D ≥ 5 W on both cards | **scored only if E141's committed reduction of pool 5 on aifoundry3 exists when this lane reduces** (else NOT SCORED, handed on with the code): the median of D(card 1) / D(aifoundry3), 95% interval by a bootstrap over tiles: **PASS** if it holds M7's 0.9711, **FAIL** if not |
| **E142-X2** | the card term, int8 | non-anchor int8 tiles with D ≥ 1 W on both | as X1, with 0.9735 |

**Reported, never a verdict** (`scored.json`, `results.md`): every tile's measured D and rise with its passes; M6's and M5's rms, bias and
coverage beside M7's on every set and per format; each verdict at every arm (leakage `auto`, 0.1994, 0.3803 and 0 W/°C; dips kept; the
anchor and tie gates relaxed; `collect_e142.sh`) and P1–P3 against both cards' reference rows; the priority-2 tests; the pool's six anchors
(its zeros tiles against E78's built-in zeros, its random tiles against M7); E78's anchors against E131's on this card; the errors by case;
heat at the measured run length; the die rise per board W against M7's 0.1151 °C/W.

**Why these lines, before the data.** They are E140's (themselves E115's), so the blind tests read alike, with M7 as the scored model and
three additions the owner's goal asks for: the error per format (M7's pools and bands are per format and card), the bias (E140's main
finding was a one-sided −0.28 W), and the comparison with the models M7 replaced on the same tiles (E140 found M5 better than M6 blind). The
reference is card 1's rows because M7's bands are per card and this lane tests the card term too.

## Precision, before the data

[`planned-intervals.txt`](planned-intervals.txt), at the registered draws: **P1** 0.093–0.366 W (median 0.197) over 9 fp32 tiles; **P2**
0.085–0.294 W (median 0.178) over 8 fp16; **P3** 0.115–0.416 W (median 0.227) over 7 int8; **B1** −0.090 to +0.105 W; **B2** −0.161 to
+0.214 W; **H1** 0.195–0.509 °C; **H2** 0.181–0.524 °C; **H3** 0.067–0.211 °C; C1 and H4 need 26 of 30 inside.
[`selftest.txt`](selftest.txt) ([`selftest_e142.py`](selftest_e142.py), 60 simulated sessions a world on the frozen registration, three
passes, 0.05 W / 0.05 °C pass noise, bootstrap draws cut to 2,000 for speed; nothing there is a measurement): when M7 is as good as its
nested score (errors drawn from its own card-1 errors), P1 PASS 60, P2 59, P3 58, B1 57, B2 55, C1 60, H1–H2 60, H3 58, H4 58 of 60; **twice
as bad**, P1–P3 FAIL in 38–43, C1 in 17, H1–H4 in 47–59; three times as bad, every rms and coverage rule FAILS in 56–60; with a −0.3 W bias on
the floats at 1×, **B1 FAILS HIGH in 60 of 60** while P1 fails in 26 and C1 in 1, so the bias rule is the sharp test of E140's kind of
miss. M1 and M2 can only say BETTER where the models' predictions differ (they differ by at most 0.6 W on this pool): in the as-good world,
where M7 is right by construction, M1 says BETTER in 13 of 60 and M2 in 27, NOT RESOLVED otherwise.

**What I expect, frozen so it can be wrong:** P1–P3 PASS; B1 PASS or FAIL HIGH (M7 still over-predicted pool 4's floats by 0.22 W out of
kind, Q138(m) § 1); B2 PASS; C1 PASS (rule B's wider bands); M1 and M2 NOT RESOLVED; H1–H4 PASS. The likeliest misses, named now: the
wide-exponent gate tiles (`fp32.wideexp48_bgate_alt`, `fp32.wideexp48_bgate_kblk`, `fp16.wideexp_bgate_alt`; M6's and M7's steady-gate
over-prediction), the fp16 pairs that cancel (`fp16.pair_cancel_asign`, `fp16.pair_nearcancel`), int8's whole-line flip-flops
(`int8.b_line_flipflop_nogate`, `int8.b_line_zero_one`).

**The statement the page gets, decided now.** All PASS: "on 36 tiles written by a designer who never saw the model, on a second card, M7
predicted power within X W rms (fp32), Y (fp16) and Z (int8) with no resolved bias, its 95% bands covering K of 30, and the die's rise within
… °C, as its nested score said". A FAIL is stated with the rms or bias, its interval and the tiles that carry it, by case. **No tile,
prediction, band, rule or reference error changes after this commit; only tiles that ran are scored.**

## What the rules cannot say

One card, one clock, one session. The heat scored is the 4.5 s window only. The heat reference is a normal model of the nested rms, not the
rows. A PASS fails to find a miss at this many tiles; it does not bound M7's error on kinds unlike these 36. Without E141 the card term and
M7's own error on aifoundry3's footing cannot be separated (X1/X2 then hand on).

## What runs

| | E140 (blind pool 4, aifoundry3, today) | E131 (E95's pass, this card, today) | E142 | why |
|---|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet | the same | **the same** | the protocol M7's rows were measured with |
| the tiles | blind pool 4's 25 | E95's 33 | **blind pool 5's 36** (`tools/claims-v3/kinds/blind5/tiles/<type>/<name>.bin`, items `<type>.<name>`) | the pool |
| anchors | E78's six (each type's zeros and random) three times a pass, the tie `anchor_pi` first and last | the same | the same; the pool's six anchors are ordinary tiles | drift, the zeros D is measured over |
| a pass | 45 runs | 53 runs | **56 runs**: the tie, three segments of the six anchors and 12 tiles, the tie; `Random("E142\|aifoundry1-c1\|<pass>")` | |
| passes | 14010–14013 | 13110–13113 (652, 620, 547, 567 s) | **14210–14213, 14214 if it fits** (the budget rule decides), at least two kept | 50 card-minutes |
| stop-path test | none | none | **14202**, before the smoke, no launch: the guard's die stop (at 1.0 °C), its board stop (at 1.0 W) and the in-run watcher's board stop (at 1.0 W) must each end `run_e142.py` with EXIT_HOT on a live sample read at most 2.0 s after it was taken (`smoke_gate_e142.py`) | E139's stop watched a file written at pass end; E145's test, plus the watcher |
| smoke | 14001 | 13101 | **14201**: the tie, `fp32.zeros`, `fp32.randn`, `fp32.wideexp48_dense` (the hottest predicted tile), `fp32.anchor_zeros`, `fp16.pair_cancel_asign`, `fp16.zeros`, `int8.b_line_flipflop_nogate`, `int8.zeros`, 2 s each, no preheat; gated by `smoke_gate_e142.py` (records ok, cycles per op within 0.5%, 600 MHz, config 65 W / 65 °C / 600 MHz, dumped pool tiles equal their sha256, `since_reset_ms` −1, board below the stop) | |
| stops | die 70 °C, board 65 W, read between runs only | board 68 W, die 72 °C, between runs | **board ≥ 66 W or any minion-shire field ≥ 72 °C**, read by the main path between runs and by the in-run watcher every 0.1 s during runs (the host program checks STOP before each ~0.5 s launch); `run_e78`'s `--max-c 72` | E131's passes here peaked at 59.9–60.6 W board, the pool's hottest tile is predicted 1.1 W above `fp32.randn`; the shire field's high-water latch reads 65 °C on this card |
| config reads | both ends of every pass, the session's | the same | **the same**: session start, both ends of the stop test, the smoke and every pass, session end | |
| data | `build/claims-v3/aifoundry3/kinds/p140<nn>/` | `…/aifoundry1-c1/e131/p131<nn>/` | `build/claims-v3/aifoundry1-c1/e142/p142<nn>/` in `~/nekko`; results `docs/reports/data/2026-11-02-e142-blind5-card1/` | |

**Stops (registered, and why they read live samples).** The block's sampler (`ettelem sample --seconds --every-ms 100` through E128's guard)
writes one JSON line a sample into `<pass>/telemetry.jsonl.raw` while it runs. (1) The main path (E145's guard, copied): `run_e78.py` reads the
newest line through `last_sample()` before every launch and every 0.1 s while it waits; a line with `board_w` ≥ 66 W or any
`temp_c.minshire` field ≥ 72 °C writes STOP (with the line's `t_ms` and its age) and ends the pass with EXIT_HOT. (2) **New in E142, the
in-run watcher**: `run_e78.py` blocks on the host program for the 4 s of a run, so a reading between runs cannot see a run's own peak; a
daemon thread reads the same file every 0.1 s for the whole pass and on the same two stops writes STOP; the host program ends its launch loop
at the next launch (`main.cpp` `repeatFor`), and the main path then ends the pass. Both read only the sampler's file. The stop-path test
proves both on live samples before any launch.

**What is E78's, byte for byte.** `check_e142.py` (before any device opens), `run_e142.py` (before every pass) and `reduce_e142.py` (before
every reduction) refuse on any difference from `predictions-e142.json` › `harness`: E78's card code (`lib.sh` `033d0776…`, `e78_common.py`
`c58923a5…`, `run_e78.py` `f3efd783…`, `reduce_e78.py` `6a158cee…`, `kinds.json` `9586568f…`), E128's guard `c2c4ab76…`, Q136(w)'s checker
`f29e91ca…` and table `50168632…`, the workload's host source `0f53a7d5…`, E142's card files, the pool (manifest, SHA256SUMS, the predictions
file, all 36 tiles) and, on the box, the two binaries (`sparsity_host` `e0fbecce…`, `ettelem` `8008f96f…`, the ones E131 and E145 ran on this
card today). Ported with marked changes: `e142_common.py` (from `e140_common.py`), `run_e142.py` (from `run_e140.py` and `run_e145.py`, plus the
watcher), `block_e142.sh` (from `block_e140.sh` and `block_e145.sh`), `queue_e142.sh` (from `queue_e131.sh`), `session_e142.sh`,
`check_e142.py`, `preflight_e142.sh` and `smoke_gate_e142.py` (from E145's), `reduce_e142.py` (from `reduce_e131.py`), `collect_e142.sh`
(from `collect_e131.sh`). New: `score_e142.py` (from `score_e140.py`, with M7's rules), `selftest_e142.py`, `make_predictions_e142.py`.

## Device commands sent

*The owner's rules of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send, classified
READ or WRITE from the firmware source of the running build; only read-only PMIC voltage reads and the statistics reset are allowed, and
**E142 does not send the reset**.* The sending code is E145's and E131's on this card (`lib.sh` unchanged, the same `ettelem` binary through
E128's guard, the block's config reads and its one `start_sampler` call), classified from et-platform `836a4ab` (BL2 0.22.0), the handlers
read again for this lane:

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
| SET_STATS_RUN_CONTROL (`--reset-ms`, the statistics reset) | **never sent** | WRITE (allowed, not used) | `lib.sh:154` forwards `start_sampler`'s extra arguments; `block_e142.sh`'s only call passes the file and the duration, and the guard refuses `--reset-ms` before the device opens |
| `dev_mngt_service` GET_MODULE_POWER (`lib.sh` `drain_mgmt`) | **never sent** | READ | replaced by a refusal in `block_e142.sh` |
| the host program `sparsity_host` (ops node: DMA, launches), the heater (the same binary), `et-who`, `et-holders`, `et-lab-manifest` | — | no device-management command | the ops node only; host-side tools |

Never sent: any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset. **The
checker** `tools/claims-v3/dmcmd_audit.py` (unchanged), from the repository root on every file the session runs (`preflight_e142.sh`):
**NO-GO** without an exception, at the one conditional site E140's, E145's and E131's lanes reviewed (`lib.sh:154`), and with the reviewed
exception **GO, 32 send sites, 0 disallowed** ([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt)).
The session runs the same preflight on the box before any device opens and stops on anything but GO. **Verdict before the first launch: GO.**

## Card budget

**At most 50 card-minutes**, from the session's first device access (`E142_T0`, before its first config read) to the session-end config
read. Expected about 45–49: the stop-path test and the smoke about 2 min, then four passes of about 10.5–11.5 min (E131's 53-run passes here
took 547–652 s, the first from a cool die) with 10 s between. `queue_e142.sh` starts a pass only if its projected end (720 s until the first
pass ends, then the longest measured) is inside **2,940 s** of `E142_T0` (3,000 less a 60 s reserve for the closing read) and before
**23:40 PST**; a pass in flight is never cut. No session starts after 23:00 PST; every run ends by 23:50 PST. It starts only after E145 has
released card 1 (20:10:39 PST), with `et-who` clean, never beside another of our sessions on aifoundry1, and with the day's post in
`#community-lab` rewritten to carry this reservation.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__ tools/claims-v3/e142/` and `tools/claims-v3/kinds/blind5/`
to the same paths under `aifoundry1:nekko/`. On aifoundry1, from `~/nekko`: `python3 tools/claims-v3/e142/check_e142.py`, `bash
tools/claims-v3/e142/preflight_e142.sh`, `V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e142/block_e142.sh 14210` and the smoke's dry run (no device
access), the day's post rewritten, then `E142_T0=$(date +%s) setsid nohup bash tools/claims-v3/e142/session_e142.sh > build/e142/session.out
2>&1 < /dev/null &` from a script file. Collect on the Intel: `PY=<python with numpy> nice -n 10 bash tools/claims-v3/e142/collect_e142.sh <copy>
[<E141 reduction>]`.

## Files

All in `tools/claims-v3/e142/`: `README.md` (this); `make_predictions_e142.py` → `predictions-e142.json` (the freeze, with every file's
sha256); `e142_common.py`, `run_e142.py`, `block_e142.sh`, `queue_e142.sh`, `session_e142.sh`, `check_e142.py`, `preflight_e142.sh`,
`smoke_gate_e142.py` (the box); `reduce_e142.py`, `collect_e142.sh`, `score_e142.py` (the desk); `selftest_e142.py`, `selftest.txt`,
`planned-intervals.txt`; `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`. The pool: `tools/claims-v3/kinds/blind5/`. Data:
`docs/reports/data/2026-11-02-e142-blind5-card1/`.

## Amendments

*(none)*
