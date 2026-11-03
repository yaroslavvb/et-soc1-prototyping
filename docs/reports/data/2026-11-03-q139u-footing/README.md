# Q139(u): one reduction footing for M7's training rows and every blind test, M7u refitted on it, E140-E142 re-scored (post hoc)

*Tue 3 Nov 2026 (week 45), 03:55-04:50 PST, on the Intel. Desk only: no card, no ssh, no Modal. It answers Q138's final
critic's open **rank 1** (the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 6**, the power model) and the desk part of **rank 5** (E142's registered X1/X2 card-term rules scored on one footing).
The footing rule, [`FOOTING-RULE.md`](FOOTING-RULE.md), was committed and pushed (`d4c36bfe`, 04:02 PST) before any row,
pass or reduced value was read. Everything after it is **post hoc**: no frozen model, prediction, band or verdict of any
earlier lane changes, and no number here is a blind result.*

## Results

| | before (each session's own footing) | after (one footing, post hoc) | source |
|---|---|---|---|
| leakage slope, aifoundry3 card 0 | 0.140-0.296 W/°C, one per session (E141: 0.2634) | **0.2056 W/°C** [0.1916, 0.2204], 2,334 idle rests in 49 passes | `footing.json` › `slopes.a3` |
| leakage slope, aifoundry1 card 1 | 0.2414 frozen, or the session's own (E88 0.315, E91 0.422) | **0.3134 W/°C** [0.2955, 0.3320], 2,700 rests in 74 passes | `footing.json` › `slopes.c1` |
| the board meter's dips | kept in 154 of M7's 247 aifoundry3 float rows, removed in 93 | removed everywhere (E82 A2) | `checks-footing.json` › `passes` |
| **pool 5 on aifoundry3 (E141), float bias, measured − M7** | −0.230 W, **B1 FAIL HIGH** (band −0.117 to +0.085) | frozen M7: +0.012 W, B1 PASS; **M7u: −0.072 W, B1 PASS** | `scores-m7u.json` › `scores.E141_*.B1` |
| pool 5 on aifoundry3, rms fp32 / fp16 / int8 | 0.325 / 0.317 / 0.356 W | frozen M7: 0.146 / 0.149 / 0.336; M7u: 0.161 / 0.148 / 0.342 | `scores.E141_*.reported.M7.power` |
| pool 5 on aifoundry3, 30 kinds rms; inside 95% | 0.365 W; 28 of 30 | frozen M7: 0.231 W, 30 of 30; M7u: 0.241 W, 29 of 30 | `scores.E141_*.reported.M7` |
| **pool 5 on card 1 (E142), float bias** | +0.050 W, B1 PASS | frozen M7: −0.125 W, **B1 FAIL HIGH**; **M7u: −0.027 W, B1 PASS** | `scores.E142_*.B1` |
| pool 5 on card 1, rms fp32 / fp16 / int8 | 0.169 / 0.149 / 0.251 W | frozen M7: 0.165 / 0.197 / 0.261; M7u: 0.130 / 0.147 / 0.256 (30 of 30) | `scores.E142_*.reported.M7.power` |
| **card term X1 (floats): card 1 / aifoundry3, measured median ratio** | 0.9821 [0.9796, 0.9955] against M7's 0.9711: **FAIL** | 0.9635 [0.9626, 0.9667] against M7u's 0.9616: **FAIL by 0.0010** (against M7's 0.9711: FAIL) | `scores.E142_*.X1` |
| card term X2 (int8) | 0.9809 [0.9688, 1.0050] against 0.9735: PASS | 0.9646 [0.9510, 0.9913] against M7u's 0.9616: PASS | `scores.E142_*.X2` |
| pool 4 (E140), M6 frozen, floats rms; bias | 0.419 W; −0.306 W | 0.212 W; −0.024 W | `score/scored-E140_*_frozen.json` › `primary.power.rows` |
| pool 4, M6 frozen, int8 rms; bias | 0.370 W; −0.197 W | 0.314 W; −0.044 W | same |
| pool 4, M6 frozen, all 25 tiles inside 95% | 19 of 25 (E140-P3 FAIL) | 23 of 25 (P3 PASS) | same, `primary.power.rules.E140-P3` |
| pool 4 out of sample, M7's form (M7 nested / M7u fitted without E140's rows) | floats 0.370 W, 0.22 W high (Q138(m) README) | M7u: floats 0.201 W (fp32 0.240, fp16 0.116), bias +0.007; int8 0.233, −0.048; 25 of 25 | `scores-m7u.json` › `families.*.pool4_out_of_sample` |
| M7's form, leave one kind out on the 637 rows, floats / int8 | 0.209 / 0.240 W | 0.184 / 0.244 W (M6's form 0.190 / 0.251; M5's 0.209 / 0.253) | `families.*.loko_old_rows`, `loko_footing_rows` |
| aifoundry2 (E143), F4: A2's dips in its bursts | not looked for | 480 of 16,679 samples (69 of 123 traces); removed: clock rules unchanged (F1 6.58 MHz PASS), board W1 1.60 → **4.11 W FAIL**, W3 FAIL | `e143-nodips.json` |

**The critic's decisive reading, reported either way: half of it holds.** On one footing, the blind float bias falls inside
B1's band on both 600 MHz cards with M7u (aifoundry3 −0.072 W, card 1 −0.027 W). **X1 still fails**, narrowly: the
measured float ratio is 0.9635 [0.9626, 0.9667] and M7u's card term is 0.9616, 0.0010 below the interval's low end. The
card term's miss shrinks from 1.1% (0.9711 against 0.982) to 0.2%, but at 1-in-500 precision the C0 term (fitted on E78's
and E82's pairs only) is still off. The nested procedure on the new rows re-chooses the all-pairs term C1 for floats, and its
scale, 0.9596, is further out (`scores-m7u.json` › `nested_procedure_footing_rows`).

**In plain words.** Most of aifoundry3's blind float error was the reduction's footing, not the model. When
every row and every test is reduced the same way (one leakage slope per card, the meter's dips removed), the frozen M7 reads
pool 5's floats on aifoundry3 to 0.15 W (from 0.32 W), and pool 4's float bias under M6 falls from −0.31 W to −0.02 W.
Card 1's slope is higher (0.31 against the 0.24 it used), so card 1's measured watts fall by about 0.1 W per float kind. The
frozen M7, trained on the old footing, then reads card 1 high (B1 FAIL); refitted on the one footing (M7u), it reads both
cards without a float bias. int8 does not move: its 0.25-0.34 W is in the model, not the footing. M7 is still not resolved
better than M6 on any card (M1 NOT RESOLVED in every arm). On card 1 at the footing it is resolved better than M5
(M2: −0.076 W [−0.142, −0.021] for M7u; `scores.E142_footing_m7u.M2`).

## What this does to predicting power and heat

**The term corrected is the reduction, not the model:** the leakage correction (one slope per card, from idle rests
pooled over all sessions, instead of each session's in-run fit) and the meter's dips (E82 A2's rule everywhere). It moves
the measured D of every training row and every test row. **Out-of-sample error, before → after (post hoc):** blind pool 5
on aifoundry3, floats 0.325 / 0.317 W → 0.161 / 0.148 W (M7u) or 0.146 / 0.149 W (the frozen M7 on the re-reduced
measurements), with the float bias −0.230 W → −0.072 W (B1 FAIL → PASS); int8 0.356 → 0.342 W (unchanged within its spread).
Card 1: floats 0.169 / 0.149 → 0.130 / 0.147 W (M7u), bias +0.050 → −0.027 W; int8 0.251 → 0.256 W. Pool 4 floats (M6 frozen)
0.419 → 0.212 W. Leave one kind out on the training rows: floats 0.209 → 0.184 W, int8 0.240 → 0.244 W. The card term: the
measured float ratio moves from 0.982 to 0.9635 and M7u's term from 0.9711 to 0.9616; X1 still fails by 0.001. **Heat is
not changed**: the window's die rise does not depend on the slope (only which passes are kept moves it), and no heat term
was refitted. **aifoundry2 is not yet on one footing**: its sampler shows A2's dips too, in E143 and in the E80/E83 bursts
M7's aifoundry2 term was fitted on, so removing them from E143 alone raises its measured burst watts by 1.43 W on average
(0 to 4.02 W) and fails W1. M8 (Q139(m)) needs E80/E83 re-reduced with A2 and the aifoundry2 relation refitted. Pool 6
(E153, E157) is the first blind test of the footing.

## The rule and what it gave

The rule ([`FOOTING-RULE.md`](FOOTING-RULE.md), `d4c36bfe`) chose **(a) one leakage slope per card from its idle rests**
over (b) the die temperature as a model input. In a kinds run the window's rise is set by the run's own power, so a jointly
fitted temperature term trades against every price. Idle rests carry no switching.

- **F1.** Each rest is the reducer's own 1 s idle bracket before a run, valid by its idle test, the run passing every
  per-run gate. The fit is ordinary least squares of the bracket's board W on its die reading, one intercept per pass, one
  slope per card, with a bootstrap over passes. aifoundry3 **0.2056 W/°C** [0.1916, 0.2204] (49 passes, 12 experiments,
  rests at 58.0-58.9 °C, within-pass spread 0.33 °C, residual 0.074 W). Card 1 **0.3134 W/°C** [0.2955, 0.3320] (74 passes,
  14 experiments, 55-59 °C, 0.36 °C, 0.090 W). Per experiment the within-pass slopes run 0.152-0.284 on aifoundry3 and
  0.242-0.626 on card 1 (`footing.json` › `slopes.*.by_experiment`).
- **F2.** E82 A2's rule on every pass, applied exactly once. The registered wrappers of 20 experiments (18 wrapper files,
  each with A2's 4.0 W and i ± 2) already apply it: built in for 16, as `--drop-dips` for E115, E127, E140 and E141. The six
  reducers with no dip handling (E78, E82, E86, E90, E92, E95) ran on A2-filtered copies (`reduce_footing.EXPS`,
  column 4).
- **F3.** Each experiment's registered reducer ran unchanged with `--leak k_c --no-refit`. With the dips gone, passes the
  registered reductions had set aside are kept by the same gates: E82 (+8210, 8216), E86 (+8614), E92 (+9211), E95 (+9513),
  E115 (+11510, 11511), E140 (+14010, 14011), E141 (+14110). E88, E91, E104 and E137 set aside the same pass as before; no
  experiment lost a pass, and none of the 637 rows was lost (`checks-footing.json` › `passes`; `scores-m7u.json` ›
  `rows_lost` = []).
- **D moved** (footing − M7's rows): aifoundry3 fp32 +0.063 W on average (−0.21 to +1.20), fp16 +0.040, int8 +0.037;
  card 1 fp32 −0.103, fp16 −0.113, int8 −0.040 (`scores-m7u.json` › `D_shift_footing_minus_m7_w`).
- **F4.** See the last row of the Results table and the paragraph above.

**M7u** keeps M7's forms (floats `G8_gtr_glive`, int8 `J8_b138`) and its card term (C0, E78/E82 pairs). Refitted on the 637
re-reduced rows: floats mult 1.62, add32 1.64, add16 1.57, bus 6.58, rest 2.35, clk 0.62, gtr 136 ± 19 fJ (M7: 145.5);
int8 nets 3.39, bus 16.2, clk 1.89, b138 −21.3 ± 10.1 fJ (M7: −23.4). The card-1 scale is 0.9616 floats and 0.9616 int8,
against M7's 0.9711 and 0.9735 (`m7u.json`). M7's whole nested procedure on the new rows picks the same forms; for floats it
picks the all-pairs card term (nested 0.185 W floats, 0.244 W int8).

**How pool 5 was scored**: the registered scorers (`tools/claims-v3/e141/score_e141.py`, `e142/score_e142.py`) ran
unchanged. Their inputs: (i) the committed reductions and frozen predictions, which reproduce the committed and critic's
numbers exactly (B1 −0.2303 FAIL HIGH; X1 0.9821 [0.9796, 0.9955] FAIL); (ii) the re-reduced measurements with the frozen
predictions; (iii) the re-reduced measurements with M7u's predictions in a copy of each registration (`score/reg-e14x-m7u.json`:
M7's power entries replaced, M7's frozen band half-widths kept, heat entries M7's; for E142, `model.card1_scale` set to
M7u's). B1's band is the registered interval drawn from M7's reference errors, unchanged.

## What this cannot say

- **Nothing here is blind.** The rule was fixed first, but the slope was fitted on sessions that include E140-E142's idle
  rests, and M7u was fitted knowing the critic's reading. Pool 6 on the frozen k_c is the test.
- **The slope's value is not settled physics.** The rests sit within about ±0.3 °C of each pass's launch target, and the
  die reading's noise in a 1 s mean can attenuate a slope fitted on that spread. E71's dedicated idle cycles read
  aifoundry3 at 0.3200 W/°C (52-58 °C) and 0.3803 (58-62 °C), above F1's 0.2056. One footing removes the inconsistency
  between rows. A common error in k is absorbed into the prices on a card. But the card term depends on both cards' slopes,
  so X1's 0.001 miss is inside what a slope error could move. The sensitivity of X1 to k_a3 and k_c1 was not run here.
- **X1's interval is narrow** (±0.002: 21 tiles whose ratios agree closely on one footing), and the rule tests a point card
  term with no interval of its own.
- **int8 is not explained by the footing.** Its 0.24-0.34 W blind error stays, and is M8's job (E141's whole-line,
  power-law and W8A8 misses; E138/E145's per-position B prices).
- **aifoundry2 is not on one footing** (F4): its training bursts carry A2's dips at 6.8% (E80) and 3.9% (E83) of samples.
- The pool-4 out-of-sample band is k × the pool rms (M7's frozen k and pools; no parameter term), because pool 4 has no
  frozen M7 prediction. Heat rules were not re-scored. Rates and features are M7's rows' own; only D, its se and dT_win
  were replaced.
- No launch's C is checked on file tiles (rank 14), here as in every earlier pool.

## Files

| file | what |
|---|---|
| [`FOOTING-RULE.md`](FOOTING-RULE.md) | the rule and the analysis plan, committed first (`d4c36bfe`, 04:02 PST) |
| [`reduce_footing.py`](reduce_footing.py) | **for later lanes to import**: `drop_dips` (A2), `filtered_copy`, `reduce(exp, k, …)` (each experiment's registered reducer at slope k, A2 once), `rests_from_csv`, `fit_slope`, `EXPS` (26 experiments: data dir, card, wrapper, dip class), `K_FROZEN` (from `footing.json`) |
| [`footing.json`](footing.json) | **the frozen footing**: per card k, its bootstrap interval, rests, passes, temperature range, residual and per-experiment slopes; the dip rule; the k = 0 stage's reductions |
| [`reduced/`](reduced/) | the 26 experiments re-reduced at the footing (`<exp>-footing.json`, each reducer's own output format) |
| [`rows-m7u.json`](rows-m7u.json) | M7's 637 rows with D, D_se and dT_win at the footing (`D_m7`, `dT_win_m7` keep M7's) |
| [`fit_m7u.py`](fit_m7u.py), [`m7u.json`](m7u.json), [`scores-m7u.json`](scores-m7u.json), [`fit-m7u-output.txt`](fit-m7u-output.txt) | M7u, its leave-one-kind-out scores beside M5's and M6's forms on the old and new rows, pool 4 out of sample, the scorer arms, the nested procedure on the new rows |
| [`score/`](score/) | the registered scorers' outputs for every arm, and the two registration copies carrying M7u's predictions |
| [`checks_footing.py`](checks_footing.py), [`checks-footing.json`](checks-footing.json) | E140's registered scorer on both footings, A2's dips on aifoundry2 (E143, E80, E83), the passes kept per experiment |
| [`e143_dips.py`](e143_dips.py), [`e143-nodips.json`](e143-nodips.json) | F4: E143's registered reduction on its traces with A2's dips removed, beside the committed results |

Rerun from the tree's root, with a python that has numpy (each step takes seconds):

```
python3 docs/reports/data/2026-11-03-q139u-footing/reduce_footing.py rests  <scratch>   # stage A: k = 0, rests, footing.json
python3 docs/reports/data/2026-11-03-q139u-footing/reduce_footing.py reduce <scratch>   # stage B: reduced/<exp>-footing.json
python3 docs/reports/data/2026-11-03-q139u-footing/fit_m7u.py <scratch> > docs/reports/data/2026-11-03-q139u-footing/fit-m7u-output.txt
python3 docs/reports/data/2026-11-03-q139u-footing/checks_footing.py
python3 docs/reports/data/2026-11-03-q139u-footing/e143_dips.py <scratch>
```

The committed JSONs have the Intel's absolute paths replaced by tree-relative ones (the reducers record their input
directories; the A2-filtered copies are named `<A2-filtered copy (reduce_footing.filtered_copy)>/…`).

**For later lanes (pool 6 on aifoundry3 and card 1):** `import reduce_footing as RF`, then reduce each pass with A2
applied once and `--leak RF.K_FROZEN[card]` (0.2056 aifoundry3, 0.3134 card 1). Never refit k on a new session. For
aifoundry2's governed bursts, F4's finding stands: remove A2's dips from training and test alike, or from neither.
