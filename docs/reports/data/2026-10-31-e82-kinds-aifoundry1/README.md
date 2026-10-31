# E82: the kinds-of-numbers energy matrix on a second card — aifoundry1 card 1, 600 MHz (Q130)

*Sat 31 Oct 2026 (week 44). E78's design (aifoundry3) replicated on **aifoundry1 card 1**, with E78's harness and
reduction unchanged. Pre-registered in [`tools/claims-v3/kinds/E82.md`](../../../../tools/claims-v3/kinds/E82.md) and
[`predictions-e82.json`](../../../../tools/claims-v3/kinds/predictions-e82.json), commit `06bc042e` (pushed 13:44:00
PDT); amendment A1 `249055ff` (13:47, a record correction) and A2 `0117ee1c` (14:00:50, one pass added and a labelled
post-hoc view), both before the data they touch. Card claimed in #community-lab at 13:44:56 (message
1566191265333125222, "for 2 h, until ~15:45 PDT"), released by editing that post at 15:03 PDT. Card session 13:45:23–
15:03:15 PDT, 78 card-minutes of the 90 registered. Seven passes ran; **the registered gates kept five** (8211–8215).*

## Results

1. **Card 1's matrix is aifoundry3's to within about 1%, at one card scale — but not at the scale September
   predicted.** Over the 32 kinds that switch ≥ 5 W, D(aifoundry3) / D(card 1) has a **median of 1.031** (IQR
   1.025–1.034; per format 1.030 fp32, 1.033 fp16, 1.027 int8; extremes 1.006 fp16 `sparse50` and 1.080 fp32
   `sparse50`, the two widest intervals), so card 1 switches about **0.970×** aifoundry3 across kinds and formats; ranks agree to Spearman
   **0.995 / 0.997 / 1.000** (X1 **PASS** in each type). The registered band, aifoundry3 = 0.88–0.99× card 1 from the
   September cards, is missed: **X2a FAIL** (0 of 32 point ratios inside), **X2b FAIL** (6 of 32 intervals overlap
   it), **X3 FAIL** (median 1.031). No verdict moves at any registered leakage arm (medians 1.053, 1.028, 1.021).
   [`scored.json` › `cross_card.primary`, `.arms`]
2. **Card 1 itself switches about 10% less than in September.** E78-R4 replicates E38's card-1 anchors of 26 Sep:
   D(fp32 `randn`) **23.99 ± 0.11 W** against 26.66 ± 1.5 W (**FAIL**), D(fp32 `ones`) **7.92 ± 0.43 W** against
   9.00 ± 1.0 W (**FAIL**, by 0.08 W; PASS with the meter dips removed, post hoc). aifoundry3 did not move: E78
   replicated E67 there (24.725 W against 24.659). The idle at a 58 °C reading is unchanged (33.10 W against E44's 33.0
   W), and so is the minion voltage (498.7 mV against 497.9). The card's firmware is no longer the one on record
   (1.4.0 / BL2 0.22.0 / minions 0.25.1, not 1.2.0: A1). Firmware is the leading suspect for the shift; nothing here
   tests it. [`scored.json` › `rules.E78-R4`; `e82.json` › `items.fp32.randn.D`, `idle_level`, `v_mean`]
3. **Every mechanism E78 tested holds on the second card** (E78-R3a–i, all 18 registered verdicts **PASS**): one-sided
   zeros cost **0.026–0.053×** random data; `sparse90` 0.026 / 0.063 / 0.165×; magnitude is free (`randn_small`,
   `randn_large` 1.003 and 0.999× `randn`); fewer mantissa bits cost less (`bf16trunc` 17.62 < `fp16grid` 19.22 <
   `randn` 23.99 W); order alone saves 1.43 / 1.21 / 0.45 W (fp32 / fp16 / int8); static bits are free in int8
   (`neg_ones` − `ones` 0.17 [0.06, 0.28] W); one zero in an fp16 pair gates nothing (`pair_half_zero` 0.923×); a
   zero is worth most in fp32 (`sparse50` 0.28 / 0.61 / 0.77× random) and the gate sees words (`sparse50` −
   `wsparse50` 6.29 W fp16, 2.37 W int8). [`scored.json` › `rules.E78-R3*`]
4. **E78's verdicts reproduce.** Of the 33 rule cells scored on both cards, 31 agree; the two that differ are R4's
   card-specific targets. E78's tally on aifoundry3 was 28 pass, 2 fail; card 1's is **23 pass, 4 fail** — the same
   two R2 accuracy failures (Q130(c) rms 2.47 W fp32, 1.07 W int8; E78 2.27 and 1.05) plus R4's two. Q130(c)'s own
   rules: 20 of 22 verdicts as on aifoundry3 (C-R1 fp32 FAIL, fp16 / int8 PASS; C-R2 fp32 / fp16 PASS, int8 FAIL at
   ρ 0.867; C-R3 PASS, int8 favouring the frozen 2.79 W; C-R4 PASS at 1.56 W; C-R6 PASS; C-R9 selects the **gate**
   arm, fp32 `a_randn_b_zeros` 0.63 W); the two that differ are C-R1 fp32's R1-A1 readings. [`scored.json` ›
   `tally`, `cross_card.e78_rule_verdict_agreement`, `q130c`]
5. **Energy per multiply-add on card 1** (switching over idle, at the measured op rate): fp32 `randn` **5.62 ± 0.04
   pJ** (2.81 pJ per flop), fp16 `randn` **2.54 ± 0.03 pJ**, int8 `full` **0.295 ± 0.004 pJ**; each format's zeros
   0.40 / 0.20 / 0.076 pJ. aifoundry3 pays 1.034–1.038× these. [`e82.json` › `items.<kind>.pj_mac_S`]
6. **Card 1's board meter sometimes reads a launch gap.** 85 one-pass dips (a reading more than 4 W below its
   neighbours) in seven passes, 62 inside runs and 35 inside power windows, every in-run dip 12–150 ms after the
   1–2 ms gap between two of a run's launches; the minion rail shows none. They set aside two of seven passes by
   E78's registered random-anchor gate (8210: `fp16.randn` spans 1.246 W; 8216: `fp32.randn` 1.072 W and `int8.full`
   1.034 W). With the dips removed (A2's labelled post-hoc view) all seven passes are kept, three verdicts move (R4
   fp32 `ones` FAIL → PASS, R3f's reported fp32 cell INCONCLUSIVE → PASS, C-R1 fp32's all-kinds R1-A1 FAIL → PASS) and
   no cross-card verdict moves (median 1.030). [`posthoc/dips.json`, `posthoc/scored-nodips.json`]
7. **The clock held.** 600 MHz in every sample of every run window (0 of 450 runs failed a run gate), 498.7 mV, TDP
   65 W and threshold 65 °C at both ends of every pass, cycles per op 546.001 / 546.001 / 318.000, duty 0.9958–0.9965.
   [`e82.json` › `failed`, `clock_mhz`, `cycles_per_op`, `checks.duty`; `aifoundry1-c1/kinds/p82*/config_*.json`]

**What it means for the blog.** The kinds table is a property of the chip, not of one card: two cards rank the 48
non-zero kinds almost identically (Spearman 0.995–1.000) and price the middle half of them at one ratio to within 1%. A
card-to-card figure, though, is a few percent and can move: September put aifoundry3 4–11% below card 1 (0.887–0.965),
today it reads 3% above. Quote a kind's watts with the card, and quote ratios between kinds, which travel.

## The matrix on card 1

D is switching power over the type's own zero-data level (each type's three zeros runs interpolated in time inside
the pass), S over the idle bracket in front of the run; pJ from S at the measured op rate; 95% intervals from the
scatter of the five kept passes. "Q130(c) pred" is the frozen aifoundry3 prediction (`switching_w_600mhz_a3`). The
last column is A2's post-hoc view (all seven passes, dips removed), not a registered result. Source: `e82.json` ›
`items`, `posthoc/e82-nodips.json` › `items`.

### fp32

| kind | gated | D over fp32 zeros (W) | ±95% | S over idle (W) | ±95% | pJ/MAC (S) | ±95% | pJ/flop (S) | ΔT window (°C) | Q130(c) pred (W) | passes | D, dips removed (post hoc) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 0.000 | 24.06 | 0.28 | 25.87 | 0.27 | 5.636 | 0.059 | 2.818 | 3.40 | 24.45 | 5 | 24.17 |
| randn | 0.000 | 23.99 | 0.11 | 25.82 | 0.17 | 5.623 | 0.036 | 2.812 | 3.41 | 24.21 | 5 | 24.00 |
| randn_large | 0.000 | 23.97 | 0.36 | 25.76 | 0.18 | 5.612 | 0.039 | 2.806 | 3.35 | 24.49 | 5 | 23.96 |
| randn_sorted | 0.000 | 22.56 | 0.82 | 24.48 | 0.83 | 5.331 | 0.182 | 2.665 | 3.14 | 22.77 | 5 | 22.79 |
| uniform01 | 0.000 | 22.03 | 0.09 | 23.85 | 0.14 | 5.195 | 0.029 | 2.597 | 3.08 | 20.36 | 5 | 21.95 |
| fp16grid | 0.000 | 19.22 | 0.18 | 21.02 | 0.16 | 4.578 | 0.032 | 2.289 | 2.74 | 23.95 | 4 | 19.16 |
| bf16trunc | 0.000 | 17.62 | 0.11 | 19.46 | 0.14 | 4.238 | 0.030 | 2.119 | 2.53 | 23.26 | 5 | 17.61 |
| pow2 | 0.000 | 13.71 | 0.04 | 15.52 | 0.28 | 3.380 | 0.062 | 1.690 | 2.05 | 13.19 | 5 | 13.66 |
| smallint | 0.118 | 13.66 | 0.10 | 15.51 | 0.05 | 3.380 | 0.009 | 1.690 | 2.03 | 17.39 | 5 | 13.66 |
| nn_like | 0.508 | 12.73 | 0.18 | 14.58 | 0.22 | 3.175 | 0.048 | 1.588 | 1.99 | 16.00 | 5 | 12.72 |
| pi | 0.000 | 8.21 | 0.20 | 9.94 | 0.11 | 2.166 | 0.023 | 1.083 | 1.44 | 8.55 | 5 | 8.18 |
| neg_ones | 0.000 | 7.98 | 0.19 | 9.91 | 0.07 | 2.159 | 0.015 | 1.080 | 1.29 | 8.55 | 5 | 7.94 |
| ones | 0.000 | 7.92 | 0.43 | 9.70 | 0.55 | 2.112 | 0.120 | 1.056 | 1.37 | 8.55 | 5 | 8.05 |
| sparse50 | 0.774 | 6.76 | 0.46 | 8.62 | 0.47 | 1.878 | 0.101 | 0.939 | 1.11 | 9.50 | 5 | 7.03 |
| a_zeros_b_randn | 1.000 | 0.72 | 0.09 | 2.68 | 0.06 | 0.585 | 0.013 | 0.292 | 0.37 | 0.00 | 5 | 0.72 |
| a_randn_b_zeros | 1.000 | 0.63 | 0.05 | 2.49 | 0.18 | 0.543 | 0.039 | 0.272 | 0.35 | 0.00 | 5 | 0.64 |
| sparse90 | 0.992 | 0.62 | 0.16 | 2.46 | 0.13 | 0.535 | 0.028 | 0.268 | 0.34 | 0.46 | 4 | 0.60 |
| zeros | 1.000 | 0.00 | 0.00 | 1.84 | 0.11 | 0.401 | 0.025 | 0.201 | 0.00 | 0.00 | 5 | 0.00 |
| *anchor_pi (built-in pi, the tie)* | 0 | 8.10 | 0.29 | 9.92 | 0.21 | 2.160 | 0.045 | 1.080 | 1.31 | — | 5 | |

### fp16

| kind | gated | D over fp16 zeros (W) | ±95% | S over idle (W) | ±95% | pJ/MAC (S) | ±95% | pJ/flop (S) | ΔT window (°C) | Q130(c) pred (W) | passes | D, dips removed (post hoc) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 0.000 | 21.62 | 0.16 | 23.50 | 0.11 | 2.559 | 0.012 | 1.279 | 2.98 | 22.19 | 5 | 21.60 |
| randn | 0.000 | 21.44 | 0.18 | 23.30 | 0.23 | 2.538 | 0.025 | 1.269 | 2.95 | 22.30 | 5 | 21.49 |
| randn_sorted | 0.000 | 20.24 | 0.14 | 22.07 | 0.15 | 2.403 | 0.017 | 1.201 | 2.72 | 21.44 | 5 | 20.22 |
| pair_half_zero | 0.000 | 19.78 | 0.11 | 21.67 | 0.19 | 2.360 | 0.021 | 1.180 | 2.84 | 20.94 | 5 | 19.78 |
| uniform01 | 0.000 | 18.82 | 0.16 | 20.69 | 0.18 | 2.253 | 0.020 | 1.126 | 2.79 | 16.73 | 5 | 18.85 |
| fp8grid | 0.000 | 17.48 | 0.11 | 19.43 | 0.16 | 2.116 | 0.018 | 1.058 | 2.56 | 21.44 | 5 | 17.44 |
| nn_like | 0.195 | 16.90 | 0.44 | 18.78 | 0.32 | 2.046 | 0.034 | 1.023 | 2.39 | 19.38 | 5 | 17.01 |
| smallint | 0.004 | 16.36 | 0.33 | 18.15 | 0.37 | 1.976 | 0.040 | 0.988 | 2.28 | 20.11 | 5 | 16.44 |
| sparse50 | 0.414 | 13.11 | 0.03 | 15.04 | 0.13 | 1.637 | 0.014 | 0.819 | 2.00 | 15.51 | 5 | 13.08 |
| neg_ones | 0.000 | 8.08 | 0.06 | 9.91 | 0.12 | 1.079 | 0.013 | 0.540 | 1.41 | 8.46 | 5 | 8.09 |
| ones | 0.000 | 8.06 | 0.03 | 9.84 | 0.06 | 1.072 | 0.007 | 0.536 | 1.64 | 8.46 | 5 | 8.02 |
| wsparse50 | 0.760 | 6.83 | 0.14 | 8.74 | 0.09 | 0.952 | 0.010 | 0.476 | 1.18 | 9.04 | 5 | 6.83 |
| sparse90 | 0.961 | 1.35 | 0.08 | 3.22 | 0.06 | 0.350 | 0.007 | 0.175 | 0.63 | 1.19 | 5 | 1.35 |
| a_zeros_b_randn | 1.000 | 0.76 | 0.10 | 2.58 | 0.13 | 0.281 | 0.014 | 0.141 | 0.00 | 0.00 | 5 | 0.80 |
| wsparse90 | 0.990 | 0.65 | 0.11 | 2.50 | 0.15 | 0.273 | 0.017 | 0.136 | 0.12 | 0.46 | 5 | 0.64 |
| a_randn_b_zeros | 1.000 | 0.62 | 0.15 | 2.43 | 0.18 | 0.265 | 0.019 | 0.132 | 0.15 | 0.00 | 5 | 0.65 |
| zeros | 1.000 | 0.00 | 0.00 | 1.87 | 0.07 | 0.204 | 0.007 | 0.102 | 0.03 | 0.00 | 5 | 0.00 |

### int8

| kind | gated | D over int8 zeros (W) | ±95% | S over idle (W) | ±95% | pJ/MAC (S) | ±95% | pJ/MAC (D) | ΔT window (°C) | Q130(c) pred (W) | passes | D, dips removed (post hoc) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 0.000 | 6.87 | 0.10 | 9.29 | 0.13 | 0.295 | 0.004 | 0.218 | 1.25 | 7.11 | 5 | 6.84 |
| gauss_q | 0.000 | 6.50 | 0.04 | 8.95 | 0.09 | 0.284 | 0.003 | 0.206 | 1.14 | 7.10 | 4 | 6.48 |
| sorted | 0.000 | 6.42 | 0.11 | 8.81 | 0.16 | 0.279 | 0.005 | 0.203 | 1.29 | 5.98 | 5 | 6.40 |
| pos | 0.000 | 5.99 | 0.13 | 8.41 | 0.16 | 0.267 | 0.005 | 0.190 | 1.05 | 3.45 | 5 | 5.97 |
| smallint | 0.000 | 5.89 | 0.14 | 8.30 | 0.12 | 0.263 | 0.004 | 0.187 | 1.01 | 7.13 | 5 | 5.88 |
| sparse50 | 0.070 | 5.29 | 0.17 | 7.76 | 0.21 | 0.246 | 0.007 | 0.168 | 1.01 | 6.06 | 5 | 5.24 |
| ternary | 0.008 | 5.01 | 0.19 | 7.40 | 0.18 | 0.235 | 0.006 | 0.159 | 1.00 | 6.42 | 5 | 4.99 |
| highbit | 0.000 | 3.09 | 0.14 | 5.54 | 0.20 | 0.176 | 0.006 | 0.098 | 0.84 | 4.49 | 5 | 3.15 |
| wsparse50 | 0.644 | 2.92 | 0.29 | 5.36 | 0.26 | 0.170 | 0.008 | 0.093 | 0.94 | 3.27 | 5 | 3.04 |
| neg_ones | 0.000 | 1.73 | 0.08 | 4.17 | 0.09 | 0.132 | 0.003 | 0.055 | 1.00 | 0.57 | 5 | 1.68 |
| ones | 0.000 | 1.56 | 0.09 | 3.95 | 0.13 | 0.125 | 0.004 | 0.049 | 0.79 | 0.57 | 5 | 1.56 |
| sparse90 | 0.822 | 1.13 | 0.06 | 3.49 | 0.10 | 0.111 | 0.003 | 0.036 | 0.83 | 0.79 | 5 | 1.13 |
| wsparse90 | 0.980 | 0.46 | 0.08 | 2.86 | 0.09 | 0.091 | 0.003 | 0.015 | 0.88 | 0.27 | 5 | 0.49 |
| a_full_b_zeros | 1.000 | 0.36 | 0.16 | 2.83 | 0.10 | 0.090 | 0.003 | 0.011 | 0.42 | 0.00 | 5 | 0.38 |
| a_zeros_b_full | 1.000 | 0.34 | 0.09 | 2.79 | 0.08 | 0.088 | 0.003 | 0.011 | 0.51 | 0.00 | 5 | 0.34 |
| zeros | 1.000 | 0.00 | 0.00 | 2.40 | 0.06 | 0.076 | 0.002 | 0.000 | 0.21 | 0.00 | 5 | 0.00 |

## E78's registered rules, scored on card 1

By `score_e78.py`'s own `score_all` (sha256 `5f41917f…`, checked) with `predictions-e82.json`'s thresholds, which are
E78's copied; R4's targets are card 1's (E38, September). Primary leakage slope `auto` = 0.2414 W/°C over 313 runs
(E78 on aifoundry3: 0.199). Arms: card 1's E44 idle slope 0.545 → 21 pass, 5 fail, 1 inconclusive; 0.3803 → the
same; none → 23 pass, 3 fail, 1 inconclusive. Source: `scored.json` › `rules`, `q130c`, `tally`, `arms`.

| rule | cell | statistic | verdict |
|---|---|---|---|
| E78-R1 | Q130(c) fp32 (15 kinds) | rho 0.934 | **PASS** |
| E78-R1 | Q130(c) fp16 (14 kinds) | rho 0.948 | **PASS** |
| E78-R1 | Q130(c) int8 (13 kinds) | rho 0.867 | **PASS** |
| E78-R2 | Q130(c) fp32 (15 kinds) | rms 2.470 W (bound 2.0) | **FAIL** |
| E78-R2 | Q130(c) fp16 (14 kinds) | rms 1.987 W (bound 2.0) | **PASS** |
| E78-R2 | Q130(c) int8 (13 kinds) | rms 1.071 W (bound 1.0) | **FAIL** |
| E78-R3a | fp32.a_randn_b_zeros/randn | 0.026 [0.024, 0.029] | **PASS** |
| E78-R3a | fp32.a_zeros_b_randn/randn | 0.030 [0.026, 0.034] | **PASS** |
| E78-R3a | fp16.a_randn_b_zeros/randn | 0.029 [0.022, 0.036] | **PASS** |
| E78-R3a | fp16.a_zeros_b_randn/randn | 0.035 [0.031, 0.040] | **PASS** |
| E78-R3a | int8.a_full_b_zeros/full | 0.053 [0.029, 0.076] | **PASS** |
| E78-R3a | int8.a_zeros_b_full/full | 0.049 [0.035, 0.062] | **PASS** |
| E78-R3b | fp32.sparse90/randn | 0.026 [0.019, 0.033] | **PASS** |
| E78-R3b | fp16.sparse90/randn | 0.063 [0.059, 0.068] | **PASS** |
| E78-R3b | int8.sparse90/full | 0.165 [0.157, 0.173] | **PASS** |
| E78-R3c | fp32.randn_small/randn | 1.003 [0.993, 1.013] | **PASS** |
| E78-R3c | fp32.randn_large/randn | 0.999 [0.982, 1.017] | **PASS** |
| E78-R3e | fp32.randn - fp32.randn_sorted | 1.426 [0.578, 2.274] | **PASS** |
| E78-R3e | fp16.randn - fp16.randn_sorted | 1.206 [1.003, 1.409] | **PASS** |
| E78-R3e | int8.full - int8.sorted | 0.452 [0.298, 0.607] | **PASS** |
| E78-R3f | int8.neg_ones - int8.ones | 0.168 [0.055, 0.282] | **PASS** |
| E78-R3f (reported) | fp32.neg_ones - fp32.ones | 0.062 [-0.403, 0.527] | **INCONCLUSIVE** |
| E78-R3f (reported) | fp16.neg_ones - fp16.ones | 0.023 [-0.029, 0.075] | **PASS** |
| E78-R3i | fp16.sparse50 - fp16.wsparse50 | 6.285 [6.132, 6.438] | **PASS** |
| E78-R3i | int8.sparse50 - int8.wsparse50 | 2.368 [1.957, 2.778] | **PASS** |
| E78-R3d | fp16grid−bf16trunc; randn−fp16grid | 1.625 [1.449, 1.801]; 4.755 [4.528, 4.981] W | **PASS** |
| E78-R3g | fp16 pair_half_zero/randn | 0.923 [0.911, 0.935] | **PASS** |
| E78-R3h | sparse50/random, fp32 < fp16 < int8 | fp32 0.282, fp16 0.612, int8 0.771; d1 0.330 [0.308, 0.351], d2 0.159 [0.120, 0.198] | **PASS** |
| E78-R4 | fp32.ones | 7.918 ± 0.427 vs 8.996 ± 1.0 | **FAIL** |
| E78-R4 | fp32.randn | 23.987 ± 0.106 vs 26.662 ± 1.5 | **FAIL** |
| E78-R4 | pi_builtin_vs_file | -0.099 ± 0.317 vs 0 ± 0.25 | **PASS** |
| Q130(c) C-R1 | fp32 | 0.400 inside the frozen 95% of 15 (need 0.7); R1-A1 0.600 (FAIL); overlap 0.533 | **FAIL** |
| Q130(c) C-R1 | fp16 | 0.857 inside the frozen 95% of 14 (need 0.5); R1-A1 0.857 (PASS); overlap 0.857 | **PASS** |
| Q130(c) C-R1 | int8 | 0.846 inside the frozen 95% of 13 (need 0.5); R1-A1 0.846 (PASS); overlap 1.000 | **PASS** |
| Q130(c) C-R2 | fp32 | rho 0.934 over 15 | **PASS** |
| Q130(c) C-R2 | fp16 | rho 0.948 over 14 | **PASS** |
| Q130(c) C-R2 | int8 | rho 0.867 over 13 | **FAIL** |
| Q130(c) C-R3 | fp16 sparse50 − wsparse50 | 6.285 W | **PASS** |
| Q130(c) C-R3 | int8 sparse50 − wsparse50 | 2.368 W (favours frozen) | **PASS** |
| Q130(c) C-R4 | int8 ones − zeros | 1.559 W (≤ 2.0) | **PASS** |
| Q130(c) C-R6 | fp32 neg_ones−ones 0.062; int8 ternary−ones 3.454; highbit−ones 1.535 W | | **PASS** |
| Q130(c) C-R9 | fp32 a_randn_b_zeros | 0.631 W | selects **gate** |

**Q130(b) r2** (watts above fp32 zeros, both variants; provisional by its own statement): variant A rms 1.46 W fp32,
1.49 W fp16, **8.11 W int8** (mean error +6.34 W: it predicts int8 far above what either card measures); variant B
1.46 / 1.12 / 8.74 W. [`scored.json` › `q130b`]. **Secondary, not a rule:** Q130(c)'s aifoundry3 predictions divided
by 0.935 (the registered band's middle) fit card 1 *worse* (rms 3.32 / 2.84 / 1.22 W), as they must once card 1 reads
below aifoundry3 rather than above it [`secondary_r2_scaled`]. **E78-R5 checks, reported:** idle consistency median
0.069 W (≤ 0.15), rail lag re-fitted 1.00 s (E58 measured 1.08 s on this card's minion rail), duty 0.9958–0.9965,
carry-over 0.0018 ± 0.0011 W/W, the built-in pi tile dumped equal to kinds.json's in every pass. [`rules.E78-R5`]

## Card 1 against aifoundry3 (E82's cross-card rules)

D on each card, E82's five kept passes against E78's six (`docs/reports/data/2026-10-31-e78-kinds-energy-matrix/
e78.json`, read after this lane's freeze was pushed). The ratio is D(aifoundry3) / D(card 1); its interval is the
delta-method combination of the two cards' 95% intervals. Source: `scored.json` › `cross_card.primary.kinds`.

| kind | D card 1 (W) | ±95% | D aifoundry3 (W) | ±95% | ratio a3/c1 | ±95% | inside |
|---|---|---|---|---|---|---|---|
| fp16.fp8grid | 17.477 | 0.106 | 18.052 | 0.126 | 1.033 | 0.010 | False |
| fp16.neg_ones | 8.085 | 0.061 | 8.382 | 0.133 | 1.037 | 0.018 | False |
| fp16.nn_like | 16.899 | 0.442 | 17.602 | 0.118 | 1.042 | 0.028 | False |
| fp16.ones | 8.062 | 0.029 | 8.448 | 0.082 | 1.048 | 0.011 | False |
| fp16.pair_half_zero | 19.785 | 0.108 | 20.122 | 0.569 | 1.017 | 0.029 | False |
| fp16.randn | 21.442 | 0.185 | 22.162 | 0.054 | 1.034 | 0.009 | False |
| fp16.randn_small | 21.621 | 0.157 | 22.209 | 0.086 | 1.027 | 0.008 | False |
| fp16.randn_sorted | 20.236 | 0.142 | 20.748 | 0.426 | 1.025 | 0.022 | False |
| fp16.smallint | 16.359 | 0.333 | 17.000 | 0.302 | 1.039 | 0.028 | False |
| fp16.sparse50 | 13.113 | 0.029 | 13.196 | 0.540 | 1.006 | 0.041 | False |
| fp16.uniform01 | 18.818 | 0.163 | 19.426 | 0.086 | 1.032 | 0.010 | False |
| fp16.wsparse50 | 6.828 | 0.144 | 7.058 | 0.035 | 1.034 | 0.022 | False |
| fp32.bf16trunc | 17.623 | 0.112 | 18.136 | 0.046 | 1.029 | 0.007 | False |
| fp32.fp16grid | 19.223 | 0.177 | 19.624 | 0.065 | 1.021 | 0.010 | False |
| fp32.neg_ones | 7.980 | 0.195 | 8.143 | 0.408 | 1.021 | 0.057 | False |
| fp32.nn_like | 12.735 | 0.185 | 13.036 | 0.066 | 1.024 | 0.016 | False |
| fp32.ones | 7.918 | 0.427 | 8.257 | 0.221 | 1.043 | 0.063 | False |
| fp32.pi | 8.209 | 0.203 | 8.470 | 0.113 | 1.032 | 0.029 | False |
| fp32.pow2 | 13.708 | 0.044 | 13.985 | 0.159 | 1.020 | 0.012 | False |
| fp32.randn | 23.987 | 0.106 | 24.725 | 0.082 | 1.031 | 0.006 | False |
| fp32.randn_large | 23.974 | 0.356 | 24.711 | 0.084 | 1.031 | 0.016 | False |
| fp32.randn_small | 24.059 | 0.279 | 24.764 | 0.463 | 1.029 | 0.023 | False |
| fp32.randn_sorted | 22.561 | 0.818 | 23.384 | 0.376 | 1.036 | 0.041 | False |
| fp32.smallint | 13.659 | 0.103 | 14.079 | 0.058 | 1.031 | 0.009 | False |
| fp32.sparse50 | 6.760 | 0.464 | 7.302 | 0.063 | 1.080 | 0.075 | False |
| fp32.uniform01 | 22.031 | 0.088 | 22.646 | 0.093 | 1.028 | 0.006 | False |
| int8.full | 6.869 | 0.099 | 7.056 | 0.059 | 1.027 | 0.017 | False |
| int8.gauss_q | 6.499 | 0.045 | 6.598 | 0.069 | 1.015 | 0.013 | False |
| int8.smallint | 5.885 | 0.136 | 6.003 | 0.142 | 1.020 | 0.034 | False |
| int8.sorted | 6.416 | 0.112 | 6.588 | 0.073 | 1.027 | 0.021 | False |
| int8.sparse50 | 5.293 | 0.170 | 5.463 | 0.146 | 1.032 | 0.043 | False |
| int8.ternary | 5.013 | 0.190 | 5.186 | 0.051 | 1.035 | 0.041 | False |

**Reported beside the rules:** each format's zero-data level S(zeros) is 1.84 / 1.87 / 2.40 W on card 1 against 1.99
/ 1.99 / 2.61 W on aifoundry3 (0.93×, 0.94×, 0.92×); the idle at the launch reading 33.10 W against 25.91 W; the
minion voltage 498.7 mV against 521.7 mV, so a C·V² reading of the 1.031 would put card 1's switched capacitance
1.06× aifoundry3's ((521.7 / 498.7)² = 1.094; 1.094 / 1.031 = 1.061), *if* the two boards' meters read alike —
which nothing here establishes. [`cross_card.primary.reported`]

## Card 1's board meter and the launch gaps (amendment A2)

`posthoc_dips_e82.py` (the A2 definition: `board_w[i] < min(board_w[i−2], board_w[i+2]) − 4.0 W`) finds, per pass,
14 / 12 / 16 / 7 / 7 / 18 / 11 dips (8210–8216), of them 9 / 11 / 13 / 3 / 6 / 13 / 7 inside runs and 6 / 7 / 7 / 2 / 3 /
8 / 2 inside a run's power window. Every in-run dip comes 12–150 ms (median 74) after a launch boundary, i.e. inside
one service-processor pass (~158 ms on this card under ettelem) of the 1–2 ms gap between two of a run's ~490 ms
launches, and the minion rail does not move with it. So card 1's `board_w` is a near-instantaneous reading that
sometimes lands in that gap and is then held for one pass. One dip pair in a 20-sample window lowers that run's mean
by 0.4–1.2 W. aifoundry3 (E78) kept every pass under the same gates. [`posthoc/dips.json`]

The registered reduction keeps the five passes the gates keep; nothing is chosen after the fact. The labelled
post-hoc view (`posthoc/e82-nodips.json`, `posthoc/scored-nodips.json`, `posthoc/results-nodips.md`) re-runs the
same reduction on copies of all seven passes with the dip samples removed: all seven pass every gate, the tally is 24
pass / 3 fail, and the cross-card median is 1.030 (per format 1.028 / 1.032 / 1.031). **It moves no registered
verdict**; it shows the artifact moves single kinds by up to 0.3 W (fp32 `sparse50` 6.76 → 7.03 W) and nothing
systematic.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | before the claim and any E78 data | `06bc042e` pushed 13:44:00; claim 13:44:56; E78's data (`410c56f6`, 14:15) first read at 14:38 |
| config read | `ettelem config` once, read only, under card 1's lock | 13:45:23: TDP 65, threshold 65, `managed_power`, 600 MHz, 499 mV (`ident/config_pre.json`) |
| firmware | only if card 0's lock is free | read 13:45:24 with both locks held non-blocking: **1.4.0 / BL1–BL2 0.22.0 / PMIC 1.3.0 / minions 0.25.1** (`ident/firmware_pre.txt`) — not the 1.2.0 on record (A1) |
| smoke | six 2 s runs, cycles per op, coverage | 13:46: 600 MHz in all 375 samples, 546.0 / 546.0 / 318.0, ok, coverage 0.9975–0.9979 (`ident/smoke.out`, `aifoundry1-c1/kinds/kinds-smoke-p8201`) |
| passes | 8210–8215, at least four, by the budget rule | 8210–8215 (13:47:21–14:52:10, ~10 min each) and, by A2, 8216 (14:52:30–15:02:37, budget 19 card-min); **8210 and 8216 set aside** by the random-anchor gate; five kept |
| skipped runs | a run whose launch reading is not reached is skipped, never launched off protocol | 5 of 455: 8211 `fp32.sparse90`, `fp32.fp16grid`; 8212 `fp16.zeros`; 8213 `fp32.zeros`; 8215 `int8.gauss_q` — each time the reading went back from 58 to 59 °C inside the 2.0 s quiet wait. Two were zeros anchors, so those passes interpolated that format's zeros through two runs and its mid-run line test was not computable; both passes are kept by the registered code |
| budget | ≤ 90 card-minutes, end by 19:30 | 78 card-minutes (13:45:23–15:03:15) |
| config at the end | — | every pass's start and end read, and the closing read at 15:03:15: TDP 65, threshold 65, 600 MHz, 499 mV (`ident/config_post.json`, `ident/final_box.out`) |
| departures | dated amendments before the data they touch | A1 (13:47, `249055ff`): the firmware record; no rule changed. A2 (`0117ee1c`, committed 14:00:50; its text says "~14:04"): pass 8216 added and the post-hoc view defined after pass 8210 was peeked at, before any of 8211–8215 was reduced; no rule, gate or analysis changed. The pass peeks (8210, 8211, 8212 reduced alone on the Intel) chose nothing |

Card 1's launch reading: the die idles at 52 °C on this card (aifoundry3 55–57 °C), so every run was heated into the
band; a pass took ~10 min all the same (E78's plan assumed ~10.7 min on aifoundry3).

## What this changes for the hub

- **Levels / Status:** the kinds matrix now has a second card; the claim "the kinds table is a property of the chip"
  is measured (X1, and per-kind ratios 1.025–1.034 for the middle half), and "a card-to-card scale is a few percent and
  moves" too (X2/X3 fail against September's band).
- **Records to correct:** `docs/findings/14-card-behaviour.md`'s card table gives aifoundry1 card 1 firmware 1.2.0
  (0.18.0 / 1.3.0 / 0.22.0); it reads 1.4.0 / 0.22.0 / 1.3.0 / 0.25.1 (A1). The BL2 0.18.0 flash-writing NoC voltage
  path the records warn about is therefore not this card's build any more; E82 set nothing either way. Card 1's
  `board_w` dips at launch gaps (A2) belong in its telemetry traps.
- **Open:** why card 1 switches ~10% less than on 26 Sep (firmware change, the September 80 °C protocol, or the
  meter): a same-protocol re-run of E38's anchors on card 1, or E64-style fp32 `randn` on aifoundry2 before and after
  its own 10 Oct update, would separate them.

## Files

`e82.json` (the registered reduction, `reduce_e82.py` = `reduce_e78.py` unchanged with card 1's config values),
`runs.csv`, `reduce.txt`, `reduce.log`; the leakage arms `e82-leak0.545.json`, `e82-leak0.3803.json`, `e82-leak0.json`
(+ csv, txt, log); the rail-lag arms `e82-tau0.80.json`, `e82-tau1.10.json`; `scored.json` and `results.md`
(`score_e82.py`: E78's rules by `score_e78.score_all`, Q130(c), Q130(b) r2, the secondary, the cross-card rules);
`posthoc/` (A2's labelled view: `dips.json`, `e82-nodips.json` + txt + csv, `scored-nodips.json`,
`results-nodips.md`); `code.sha256`; `logs/` (`e82-queue-8210-8215.log`, `e82-queue.log` = the 8216 queue,
`e82-dry.log`); `ident/` (setup, config and firmware reads, smoke, closing read); `aifoundry1-c1/kinds/p8210`–`p8216`
(every pass's raw telemetry, marks, launch records, tile dumps, configs, manifest; 8210 and 8216 set aside) and
`kinds-smoke-p8201`. Code: `tools/claims-v3/kinds/` — `E82.md`, `predictions-e82.json`, `reduce_e82.py`,
`score_e82.py`, `collect_e82.sh`, `run_e82.sh`, `posthoc_dips_e82.py`, and E78's harness, unchanged. Reproduce:
`PY=/usr/bin/python3 E78DIR=docs/reports/data/2026-10-31-e78-kinds-energy-matrix bash tools/claims-v3/kinds/collect_e82.sh
'p82[1-9][0-9]' build/claims-v3/aifoundry1-c1` over a copy of `aifoundry1-c1/` at that path.
