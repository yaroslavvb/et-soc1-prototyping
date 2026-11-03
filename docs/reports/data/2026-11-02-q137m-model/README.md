# Q137(m): M6, a power model with per-flip terms and a heat term, scored by nested leave-one-kind-out, frozen, with a blind pool from an independent designer

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): item 6, "the power model's open cases". Q137's goal, in the owner's words of Mon 2 Nov 2026: to predict the power and heat of numeric computations as accurately as possible.*

*Mon 2 Nov 2026 (week 45), Q137(m), desk only: no card was opened and nothing was measured here. Every watt and degree comes from a committed experiment, named where it is used. It builds on Q133(b)'s M5 ([`../2026-11-01-q133b-power-model/`](../2026-11-01-q133b-power-model/README.md)) and Q132(b)'s bench ([`../2026-11-01-q132-rtl-bench/`](../2026-11-01-q132-rtl-bench/README.md)). The pool it predicts, [`tools/claims-v3/kinds/blind4/`](../../../../tools/claims-v3/kinds/blind4/README.md), was written by a separate agent that saw only the tile format, and was committed in `67fe20a9` before any M6 fit ran. **E140** scores it on aifoundry3.*

## Results

**What this does to prediction.** Power, floats: the nested out-of-kind error falls from 0.226 W (M5 as frozen) to **0.207 W** over 489 rows from 22 experiments, and on the 206 rows of the nine experiments M5 never saw, from 0.270 to **0.230 W**. The gain is resolved in fp16 and not in fp32. Power, int8: **M6 is worse than M5**, 0.260 against 0.222 W, a resolved loss. Heat: over the kinds harness's 4.5 s run, the die rises **0.118 °C per board W on aifoundry3 and 0.116 on aifoundry1 card 1**. That is the lab's prior rule (S × 0.118), so the heat term buys nothing out of kind: its nested error is 0.304 / 0.283 / 0.175 °C (fp32 / fp16 / int8) against the prior rule's 0.277 / 0.288 / 0.190 °C. What M6 adds for heat is the long-time response: a frozen step response from E73's and E97's time constants and the steady coefficients of E97, E111 and E133. No experiment here scores that response out of sample.

**1. Power, nested leave-one-kind-out, rms of D − prediction (W)** ([`loko-m6.json`](loko-m6.json); 95% bootstrap over kinds, post hoc, [`bootstrap-m6.json`](bootstrap-m6.json)):

| format | rows | M5 as frozen (before) | M6 nested (after) | after − before, 95% | on the 9 new experiments only: before → after (n) |
|---|---:|---:|---:|---|---|
| fp32 | 275 | 0.239 | **0.227** | −0.037 to +0.008 (not resolved) | 0.282 → 0.258 (125), diff −0.063 to +0.005 |
| fp16 | 214 | 0.207 | **0.179** | −0.062 to +0.001 (3% of resamples ≥ 0) | 0.250 → **0.178** (81), diff **−0.135 to −0.011** |
| int8 | 115 | 0.222 | 0.260 | **+0.014 to +0.061 (worse)** | 0.211 → 0.243 (37), diff +0.002 to +0.066 |

M5 as frozen is in-sample on its thirteen experiments' rows (fitted on them), so the "before" column flatters it there. On the nine experiments it never saw (E102, E108, E115, E121, E122, E123, E127, E128, E131), it is out of sample, as M6's nested errors are everywhere. M5's own form refitted on all 22 experiments reads 0.230 W for the floats and 0.245 W for int8 (plain leave-one-kind-out), so for floats the new terms, not the extra rows, carry the gain.

**Which term did it.** The gate's switching, `gtr`, takes plain leave-one-kind-out from 0.230 to 0.211 W. On M5's thirteen experiments it added nothing (Q133(b) § 5). E115's and E127's gate-switching tiles are what resolve it: E127's error falls from 0.564 to 0.286 W, and E108's from 0.187 to 0.147 W. The per-field flips add 0.004 W more (`G6`, 0.207 W). The product-sign term alone adds nothing (`G2` 0.231 W), and neither does the A side's small-mask term (`G5` = `G4`, 0.213 W). The nested procedure picks `G6_gtr_psgn_fields` in 129 folds and `G7_all` in 106, and the freeze is `G6`. For int8 every extension is level with or worse than I3 refitted, and I3 refitted (0.245 W) is itself worse than M5's frozen constants out of sample. Refitting int8 on more experiments makes it worse out of kind. M5's int8 constants stay the better int8 predictor, and the blind predictions carry both.

**2. M6, frozen.** [`m6.json`](m6.json), sha256 **`87c17e086ee36699d7bb96609c02c471b5ba6b7bcdc20ead576d26f89e136e82`**, written by [`fit_m6.py`](fit_m6.py) (sha256 `010f2cf1b05e84906c697e5b9945adc903a45acd6f3b7348cc42d82de59092c7`) with [`m6_rows.py`](m6_rows.py) (`6a0e0458948683b07974b153917631b2e38d4b579985f9db5bae9f5e2ca6756a`), M5's [`fit_m5.py`](../2026-11-01-q133b-power-model/fit_m5.py) (imported, unchanged, `e02116913042291bac41a4431bf880f00a4249bddf50c649c66feb267d77decb`) and [`counts-e123.json`](counts-e123.json) (`3253a36540c016dc1753276112b1a70b2f51b1ff01e9678b3614a17686c98058`). Committed and pushed in `6a713a9f` at 15:56:19 PST, before the pool's predictions.

- **Floats, form `G6_gtr_psgn_fields`** (fJ per count, ± 1 s.e., jackknife by kind): mult 1.544 ± 0.038, add32 1.661 ± 0.038, add16 1.592 ± 0.050, bus 3.22 ± 1.25, rest 2.462 ± 0.080, clk 1.054 ± 0.004, gtr 157.8 ± 18.4, psgn −36.8 ± 45.0, a_sign 47.0 ± 23.2, a_exp 3.2 ± 8.8, a_mant −3.9 ± 5.3, b_sign 27.6 ± 44.3, b_exp −1.3 ± 4.5, b_mant 8.67 ± 2.26. Card-1 scale 0.9711. The flip terms share variance with the bench's lane-bus count (bus falls from M5's 7.57 to 3.22 fJ), and several of them are unresolved or negative. They are a predictor, not a physical price list. The one physical reading that holds is that a gate's state change costs about 158 fJ, against about 1.5 fJ for a multiplier net toggle.
- **int8, form `J1_gtr`**: nets_nobus 3.326 ± 0.180, bus 13.66 ± 2.98, clk 1.892 ± 0.182, gtr −46.2 ± 28.2 fJ. Card-1 scale 0.9735. The negative gate term is not physical (see 1).
- **Interval pools** (nested rms, W): fp32 a3 0.245, fp32 c1 0.208, fp16 a3 0.166, fp16 c1 0.190, int8 a3 0.249, int8 c1 0.271.
- **Heat, form `H2_per_card_runlength`**: 0.1184 °C per board W on aifoundry3 and 0.1155 on aifoundry1 card 1, over a run of 4.5 s from launch. The run-length slopes (−0.062 and −0.159 °C/W per s) were fitted on runs of 4.4–5.0 s only and are not to be extrapolated. Interval pools (nested rms): fp32 0.304, fp16 0.283, int8 0.175 °C. Step response, F(t) = 1 − Σ wᵢ e^(−t/τᵢ), with τ = 1.005, 15.98, 138.2 and 1500 s and w = 0.148, 0.010, 0.832, 0.010. It reproduces E97's six fractions within 0.002 rms, and the 1500 s pole sits at the grid's edge, so the tail beyond 10 min is not determined. Steady coefficients: aifoundry3 about 0.9 °C per board W (E97's settled plateau, below 12 W of switching), aifoundry2 0.65–0.70 (E111 and E133), aifoundry1 card 1 none.

**3. Heat, by format** (die rise over the kinds window, °C; rms of measured − predicted):

| format | rows | prior rule S × 0.118 (before) | one constant, plain | M6 nested (after) | heat with S predicted: before → after | readout floor (rms s.e. of an item) |
|---|---:|---:|---:|---:|---|---:|
| fp32 | 278 | 0.277 | 0.278 | 0.304 | 0.273 → 0.300 | 0.133 |
| fp16 | 196 | 0.288 | 0.286 | 0.283 | 0.288 → 0.280 | 0.122 |
| int8 | 96 | 0.190 | 0.184 | 0.175 | 0.188 → 0.163 | 0.095 |

By card, the prior rule reads 0.174 °C on aifoundry3 and 0.338 °C on aifoundry1 card 1. The die's whole-degree readings put about 0.1–0.13 °C of noise on an item. The rest of the error is between sessions: E108 reads 0.092 and E127 0.101 °C/W against the pool's 0.118, and nothing in these rows (run length, launch offset, format) predicts which sessions do that. "With S predicted" is end to end, from the tile's bytes to degrees: the nested heat error plus the card's coefficient times the nested power error, on 496 rows that have both. The heat rows hold only runs of 5.0 s or less. E106 (7.2 s), E128 (11–14 s) and E131 (7.2 s) are left out, because their launch reading is not comparable: E128 reads 0.0 °C of rise at 11.8 W. That rule was written after the first fit's heat results had been read (§ Order).

**4. The largest nested misses** (W): `fp32.a_colconst_b_randn` (E115) −1.70 (M5 −1.59); `fp32.g_blanes_steady` (E115) −0.76 (M5 −0.80) and (E127) −0.59 (−0.63); `fp32.x_logu_bsteady` (E115) −0.75 (−0.80); `fp32.c_near_rand` (E103) +0.74 (+0.71); `int8.r_cancel` (E88) +0.86 (+0.62); `int8.a_colconst_b_full` (E115) −0.75 (−0.71). E115's A held down a column and its steady B gate stay M6's worst. M6 over-predicts both by as much as M5 does: an A side held constant down a column is cheaper than any counted term says, and so is a lane gated steadily.

**5. The open cases of item 6, as M6 leaves them.**
- *Gated lanes and the B-lane gate* (E93, E121, E127): **narrowed**. `gtr` is now priced, at about 158 fJ a state change, and it is what moves the floats. A steadily gated B lane is still over-predicted, by 0.6–0.8 W.
- *Signs on moving sums* (E88, E92, E104, E106, E108, E122, E128): a product-sign term does not help out of kind (`G2`). The bench's adder and result counts carry what can be carried, and E108's sign tiles improve with `gtr` and the field flips (0.187 → 0.147 W). E103's `c_near_rand` and `s_bhalf_alt` stay +0.6–0.7 W low. **Open for fp32.**
- *The A side's two thirds and its small-mask exception* (E113, E125): designed as `a_small`, which adds nothing. No fitted row runs a small A mask with a busy partner (E113's and E125's `hl` rows are not in the fit), so the term is **untested, not refuted**.
- *The card scale* (E82): unchanged, 0.9711 floats and 0.9735 int8.
- *Heat*: the kinds window is predicted by S alone, at the prior 0.118 °C/W, on both cards. Long holds rest on quoted coefficients and are **not scored out of sample here**.

**6. The blind pool and its frozen predictions.** [`tools/claims-v3/kinds/blind4/`](../../../../tools/claims-v3/kinds/blind4/README.md): 25 tiles (11 fp32, 7 fp16, 7 int8; 20 priority 1), on signs on moving sums, spread exponents under a gate, A with a busy partner, partial sparsity, real-model tiles from pythia-70m and Qwen2.5-0.5B, and two of the designer's own (all-subnormal fp32, int8 B lines that flip between all 0x00 and all 0xFF). `blind4.json` sha256 `0bf9526f2049f6b0914050a297603416a953f2d38b5a30f4e98d93d50cb46b28`, `SHA256SUMS` `cd067da736f20cf8786d4bfe91ad1d3db5f540a0400828af60c51a428378bc9c`. Its counts ([`counts-blind4.json`](counts-blind4.json), sha256 `91d7a97f91bdf0f10a93859cdfab0c83047ea8143baab8934531def8aa1758ec`) come from the same bench, with 0 accumulator mismatches against software on all 25. The predictions are in [`predictions-blind4.json`](../../../../tools/claims-v3/kinds/blind4/predictions-blind4.json) and [`.md`](../../../../tools/claims-v3/kinds/blind4/predictions-blind4.md), from [`predict_blind4.py`](predict_blind4.py). For each tile they give M6's D on aifoundry3 at 600 MHz (W over the type's own zeros) with a 95% interval, M5's D beside it, the die rise over the kinds harness's 4.5 s run with a 95% interval, and the rise the same S would reach in a long hold (60 s, 300 s, plateau). M5 and M6 differ by at most 0.69 W on any tile (`fp32.wideexp_bgate_alt`), so E140 can tell them apart on the gated tiles and on little else. The long-hold plateaus (up to 23.7 °C over idle at 0.9 °C/W) extrapolate E97's low-power plateau, and a hold that long is not part of E140.

## How it was done

**Power rows.** M5's 361 rows (thirteen experiments, `fit_m5.assemble`, unchanged) plus every kinds experiment committed since whose tiles the bench has counted: E102, E108, E115, E121, E122, E123, E127, E128 and E131 ([`m6_rows.py`](m6_rows.py)). Twenty-two experiments, two cards. A row's counts are found by the sha256 of the tile it ran, across every committed counts file of `rtl-sim/fma_toggle_v2` (Q132(b)'s, Q133(b)'s, and E102's, E104's, E106's, E108's, E127's, E128's, E134's desk counts). E123's 36 re-draws had none; this lane counted them with Q133(b)'s Intel build of the same bench ([`counts-e123.json`](counts-e123.json): 36 tiles, 0 accumulator mismatches against software). Left out, as in M5: anchors (`anchor_pi`, zeros) and later sessions' `randn`/`full`; and E124, E129, E130 and E134, whose items are not kinds tiles (zeros modes, netlist arms, bit ladders on another harness) or have no per-tile D; E113 and E125 (the `hl` harness) inform the `a_small` term's design but their rows are not in the fit.

**New power features, from the tile bytes alone** (`flip_feats` in [`fit_m6.py`](fit_m6.py), through `make_kinds`' issue stream, the stream every earlier model used):
- `a_sign`, `a_exp`, `a_mant`, `b_sign`, `b_exp`, `b_mant`: operand bits that change between consecutive micro-ops, by field and side (A broadcast to every column slot, as M5's `abits`); int8 has sign and magnitude only;
- `psgn`: product-sign changes, a lane's sign(a) xor sign(b) changing between consecutive micro-ops (the sign term: E88, E92, E104, E106, E108, E122, E128);
- `a_small`: the A side's flips, when every A flip of the tile lies in its four low mantissa bits (E113, E125: A pays about two thirds of B's price per flip, but a mask of 2-4 low bits pays nearly the full price);
- `gtr` (M5's): gate-state changes between consecutive micro-ops (E127's B-lane gate, which costs per lane and on a short time scale, and E93's and E121's gated lanes).

**Power forms**, written at 15:30:44 PST, before any fit ran: M5's own form `G0_M5` (`F10_add_by_format`) and seven extensions `G1`-`G7` for the floats; I3 (`J0_M5`) and five for int8. No form was added or removed after a fit was read.

**Card scale** (E82): as M5, one model-free scale per family, E82's kinds against E78's same tiles, recomputed inside every fold without the held-out kind.

**Nested leave-one-kind-out** (Q130(n)'s lesson): for each held-out kind, every form is scored by leave-one-kind-out on the rest, the best is refitted on the rest and predicts the held-out kind; the outer errors score the whole procedure, the choice of form included. A kind is every row of one tile rule, on both cards and in every experiment (byte-identical tiles share a kind; re-draws join their rule). The same inner step on all rows chose the frozen form, fitted on all rows.

**Heat rows.** Every item of the same experiments with a die rise over its run (`dT_win`: the die reading at the window less the launch reading) and S (board W over idle). The run length comes from each experiment's `runs.csv`.

**Heat forms**: `H0` one constant per board W; `H1` one per card; `H2` adds a run-length slope; `H3` adds the launch reading's offset from its pass; `H4` adds an int8 term (E89/E97 put int8 4-11% above fp32 random per board W). Nested leave-one-kind-out as for power. **Before** is the lab's prior rule, S x 0.118 C per board W (E97 § What this is), unfitted.

**Time constants** (quoted, not refitted on card data here): E73's poles, 15.98 s with a 1.009 s delay or 15.57 s and 1.005 s; E97's step response on aifoundry3 (21% of the plateau by 10 s, 32% by 30 s, 45% by 60 s, 64% by 2 min, 90% by 5 min, ~98% by 10 min) and its settled plateau of about 0.9 C per board W; E111's and E133's 0.65-0.70 C per board W on aifoundry2 (four holds, two sessions). M6 freezes a four-pole step response F(t) = 1 - sum w_i exp(-t/tau_i), E73's two fast poles fixed, two slow poles fitted to E97's six fractions. The long-hold rises in the predictions are S x 0.9 x F(t) on aifoundry3; aifoundry1 card 1 has no hold, so no long-hold figure is given for it.

## Order (PST, Mon 2 Nov 2026)

1. 15:23 brief read. 15:24 Q133(b)'s README and `fit_m5.py` read (M5, its forms and rows). 15:2x the independent designer started, with only the kinds README, `make_kinds.py`, the tile layout and the list of open case types. It was never given a model, a prediction or a data README, and its own README lists what it read.
2. 15:28 the bench (Q133(b)'s Intel build of `rtl-sim/fma_toggle_v2`, unchanged) started counting E123's 36 re-draws. It ended 15:45:49 with 0 mismatches.
3. **15:30:44 the power forms `G0`–`G7` and `J0`–`J5`, and the heat forms `H0`–`H4`, written** (`fit_m6.py`), before any fit.
4. **15:33:03 the pool committed and pushed alone, `67fe20a9`**, before any M6 fit ran.
5. 15:33:23–15:41:38 fit run 1, without E123's re-draws (not yet counted). 15:41:59 its results read: floats nested 0.213 W, int8 0.261 W, heat fp16 nested 0.538 °C against one constant's 0.366 °C. **After reading them (post hoc):** the heat rows were restricted to runs of 5.0 s or less, and "before" for heat was set to the prior S × 0.118 rule. The cause was E128's long runs, which read no rise at 11.8 W. Both changes went into `fit_m6.py` at 15:42:30. No power form, power row rule or heat form was changed.
6. 15:49:17–15:55:30 fit run 2, on every row, which is **the freeze**. 15:56:19 `m6.json` and its code committed and pushed, `6a713a9f`.
7. 15:49–16:03 the pool's 25 tiles counted (0 mismatches). 15:58–16:02 `bootstrap_m6.py` (post hoc: row errors and intervals; nothing frozen changes). 16:05 the frozen predictions written. This README and the predictions follow in one commit, before E140's claim.

## What this cannot say

- The flip coefficients are not prices: they share variance with the bench's bus count, and several are unresolved. Read a gate's state change (158 ± 18 fJ) and the bench terms physically, not the field terms.
- The heat term is scored over the kinds harness's short run only. The long-hold figures are quoted from E97 (aifoundry3, below 12 W of switching, a plateau that failed E97's own steadiness test), E111 and E133 (aifoundry2). Nothing here scores them out of sample.
- The nested procedure for int8 chose a form that predicts worse than M5's frozen constants. That is reported as found: the freeze is the procedure's choice, and the predictions carry M5's beside it.
- One lane wrote both the model and the scoring code. The pool's designer was independent, and E140 is the test.

## Files

| file | what |
|---|---|
| [`fit_m6.py`](fit_m6.py), [`m6_rows.py`](m6_rows.py) | the fit: rows, flip features, forms, nested leave-one-kind-out, heat, freeze |
| [`m6.json`](m6.json) | **the freeze**: per family the form, constants (J), jackknife covariance, card-1 scale, interval pools; the heat form, coefficients, step response, steady coefficients |
| [`loko-m6.json`](loko-m6.json), [`fit-output.txt`](fit-output.txt) | every form's plain and nested errors, by format, card and experiment; the largest misses; heat by form |
| [`rows-m6.json`](rows-m6.json), [`heat-rows.json`](heat-rows.json) | the assembled power and heat rows |
| [`counts-e123.json`](counts-e123.json), [`counts-blind4.json`](counts-blind4.json) | the bench's counts for E123's re-draws and the pool's tiles |
| [`bootstrap_m6.py`](bootstrap_m6.py), [`bootstrap-m6.json`](bootstrap-m6.json), [`bootstrap-m6.txt`](bootstrap-m6.txt) | post hoc: per-row nested errors, bootstrap intervals over kinds, the heat readout floor |
| [`predict_blind4.py`](predict_blind4.py) | the pool's frozen predictions, M6 and M5 |
| `../../../../tools/claims-v3/kinds/blind4/` | the pool (`67fe20a9`), and its `predictions-blind4.json` / `.md` |

Rerun from the tree's root, with a python that has numpy:

```
python3 docs/reports/data/2026-11-02-q137m-model/fit_m6.py > docs/reports/data/2026-11-02-q137m-model/fit-output.txt   # ~8 min
python3 docs/reports/data/2026-11-02-q137m-model/predict_blind4.py
python3 docs/reports/data/2026-11-02-q137m-model/bootstrap_m6.py > docs/reports/data/2026-11-02-q137m-model/bootstrap-m6.txt
# the bench, as Q133(b)'s README says, with --extra-tiles for E123's re-draws and the pool's 25 tiles
```
