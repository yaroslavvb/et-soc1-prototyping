# Q139(m): M8, the power model on one footing - the C register's flips earn a term for the floats, a near-whole-byte discount for int8; no exponent-field, per-position or aifoundry2 term lowers the error; no cheap read predicts a card's scale within 1%; frozen before blind pool 6

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds" (items 15, 12 and 7 feed its candidate terms). It answers Q138's final critic's open
**rank 2** (M8: a refit with the terms Q138 measured as missing) and **rank 5**'s card-scale predictor (a scale for a card nobody
has measured, from cheap reads, tested leave one card out). The owner's goal for this work, in his words of 2 November 2026: to
predict the power requirement and heat generation of numeric computations as accurately as possible.*

*Tue 3 Nov 2026 (week 45), 04:34-05:05 PST, Q139(m), desk only, on the Intel (`nice -n 10`, at most 6 threads): no card was
opened and nothing was measured here. Every watt, MHz and degree comes from a committed experiment, named where it is used. It
starts from Q138(m)'s M7 ([`../2026-11-02-q138m-model/`](../2026-11-02-q138m-model/README.md)) on Q139(u)'s one reduction
footing ([`../2026-11-03-q139u-footing/`](../2026-11-03-q139u-footing/README.md), imported: `reduce_footing.K_FROZEN` 0.2056 /
0.3134 W/°C and E82 A2's dip rule once). **The registration, [`M8-REGISTRATION.md`](M8-REGISTRATION.md), was committed and
pushed (`f640fb7a`, 04:43:20 PST) before `fit_m8.py` existed and before any candidate feature was computed on any row.** This
lane never read `tools/claims-v3/kinds/blind6/` or the pool-6 designer's scratch; pool 6 does not exist in the tree when M8 is
committed. E153 (aifoundry3), E157 (aifoundry1 card 1) and E160 (aifoundry2) score it.*

*Corrected after verification (a dated note, Tue 3 Nov 2026, from about 05:30 PST; desk only: no card, no device command,
no frozen file changed). An independent verifier re-derived every power number from `rows-m8.json` with its own code, the
C-register and byte features with its own emulator, aifoundry2's selection, the peak excess from the raw traces and the
card-scale table, and found M8 sound: it holds, with ten minor faults. None changes a frozen, registered or measured number,
a kept term or a verdict. Each is corrected by a dated note beside the text it concerns, the text itself left as it was, and
set out in full in [§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers
they quote are printed by [`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt)
([`corrections-numbers.json`](corrections-numbers.json)), which imports M8's frozen code unchanged and first reproduces 35
committed numbers exactly. **The main ones.** aifoundry2's end-to-end score fits the cap on the bursts it scores; with the cap
held out per kind as well it reads **7.22 MHz / 1.87 W** rms, against the frozen figure's 7.16 / 1.86 (the frozen bands stay).
Most of the floats' gain "resolved against M7 and M6 as frozen" is **the refit on the one footing**: M7's own form refitted
gains −0.011 W on M7 as frozen, and the C term adds −0.005 W, not resolved. git records the registration at **04:43:16 PST**
(not "about 04:50", nor 04:43:20) and the freeze at 04:57:59, so this lane's window was 04:34-04:58 PST, not to 05:05.*

## Results

**What this does to prediction** (every "after" is nested leave-one-kind-out on the same folds: out of kind, not blind; W rms
of measured − predicted D on the one footing; intervals are a paired bootstrap over kinds, 2,000 draws):

| term | before | after (M8) | resolved? | source |
|---|---|---|---|---|
| power, floats (627 rows, 343 kinds) | M7's form refitted per fold **0.187 W**; M6's form 0.191; M7 as frozen 0.198; M6 as frozen 0.195 | **0.182 W** (`G13_cend`: M7's form + the C register's flips) | against M7's form **no** (−0.005 [−0.012, +0.002]); against M7 and M6 as frozen **yes** (−0.016 [−0.025, −0.007]; −0.014 [−0.026, −0.001]); against M5's form yes (−0.030) | `nested-m8.json` › `families.float.same_folds.all`, `paired_bootstrap_over_kinds_M8_minus` |
| power, int8 (140 rows, 66 kinds) | M7's form 0.256 W; M6's form 0.261; M7 as frozen 0.237 | **0.241 W** (`J13_bsat`: M7's form + a near-whole-byte discount on B) | no (−0.015 [−0.050, +0.025] against M7's form; +0.005 [−0.031, +0.044] against M7 as frozen) | `families.int8.same_folds.all` |
| power on blind pool 5's rows (E141 + E142, out of kind) | M7's form: floats 0.159 / 0.146, int8 0.374 / 0.309 W (aifoundry3 / card 1) | floats 0.158 / 0.155, **int8 0.411 / 0.397 W** | floats no (+0.004 [−0.017, +0.029]); **int8 worse, not resolved** (+0.061 [−0.065, +0.223]) | `same_folds.exp E141`, `exp E142`, `paired_bootstrap_pool5_rows_M8_minus` |
| power on the older blind pools' rows (out of kind) | M7's form: pool 3 floats 0.262, pool 4 floats 0.198, int8 0.225 W | pool 3 floats **0.195**, pool 4 floats **0.163**; pool 4 int8 0.265 | — (the C term's gain sits on pools 3 and 4) | `same_folds.exp E115`, `exp E140` |
| E147's single-bit steps (70, aifoundry3) | M7's form 0.228 W (bias −0.129); M7 as frozen 0.224 | 0.219 W (bias −0.121): the exponent items still read 0.5-0.6 W high | the exponent-field term does not lower the error (0.1882 against 0.1872 W) and is not carried | `same_folds.exp E147`; `plain_loko_by_form` |
| 95% bands | M7: k 3.18 floats / 2.48 int8 (pool rows set k) | **k 2.20 floats** (all rows set it; the pools' rows give 2.04) / **2.83 int8**: 595 of 627 and 138 of 140 inside; pool rows 78 of 79 and 29 of 31 (28 of 31 with each left out of k) | a calibration, not a test (pool 6 is the test) | `families.*.band` |
| card 1's scale | M7u's C0 0.9616 | **0.9616** (C0 chosen again; all-pairs alternatives level, 0.7735 / 0.7738 / 0.7736 W on 114 pairs) | — | `families.float.card_terms` |
| aifoundry2's burst clock and board (95 bursts, E80 + E83 + E143) | M7's frozen relation through M8's nested D: 7.27 MHz, **1.73 W**; governed 10.86 MHz, 2.03 W | **M7's form, cap refitted 65.58 → 65.20 W: 7.16 MHz, 1.86 W**; governed 10.68 MHz, 2.28 W (bias +1.16 W) | **no new term kept**: zeros level, D scale per format and the cap rising with overshoot each failed the registered "lowers both" rule | `aifoundry2.selection_steps`, `end_to_end_from_M8_nested_D`, `M7_frozen_relation_same_cells` |
| aifoundry2's peak board power (new) | none (the 82 W stop had only E136's admission estimate) | **P800(c) + 1.94 W expected, + 2.95 W at 95%** (117 E143 traces; the highest 87.95 W); in sample, 35 of 36 pool-5 tiles' highest sample at or under the 95% value | — | `aifoundry2.peak` |
| **card-scale predictor (rank 5)** | none | **FAIL**: no cheap read predicts every held-out card within 1% (the voltage at 600 MHz misses card 1 by −5.2%, fitted −8.5%) | — | `card_scale.loco` |
| heat | M7's law (0.1186 / 0.1151 °C per board W) | **carried unchanged** (E141/E142 passed H1-H4; E144 scored Q138(t)'s chain) | — | `m8.json` › `heat` |

*(Dated note, Tue 3 Nov 2026, after verification, C1, C4, C5 and C7.)* **Floats:** "resolved against M7 and M6 as frozen" is
mostly the refit on the one footing, not the new term. On the same folds, M7's own form refitted on M8's rows gains
**−0.0108 W [−0.0178, −0.0040]** on M7 as frozen (resolved) and −0.0082 [−0.0190, +0.0036] on M6 as frozen (not resolved);
the C term adds **−0.0054 [−0.0122, +0.0017]** (not resolved). M6 and M7 as frozen are also in sample, on the old footing, on
most rows. So 0.182 W is out of kind, not blind, against 0.187 W for M7's form refitted on the same footing. **Card 1's
scale:** C0 was chosen once, on all rows, before the fold loop, and its value refitted inside every fold (see § 2's note).
**aifoundry2's bursts:** the end-to-end figures and the frozen bands fit the cap on all 95 bursts, the scored ones included,
so the cap is in sample. With the cap held out per kind as well: **7.22 MHz / 1.87 W** rms, 95th percentiles 17.6 MHz /
3.54 W (frozen: 16.95 / 3.50), governed 10.77 MHz / 2.30 W with the same +1.16 W bias. The frozen bands stay as committed.
The "before", M7's frozen relation, is in sample on E80's and E83's 56 bursts (M7 fitted its cap on them) and blind on
E143's 36. On those 36 it reads 4.71 MHz / 1.45 W, and M8 with the cap held out reads 3.81 MHz / 1.64 W, both through M8's
nested D. The 92 are all the bursts under aifoundry2's own governor (41 governed below 795 MHz, 51 at 795-800 MHz), not
governed bursts only. **The peak's coverage** (35 of 36, 4 flags) is now computed, in sample (§ 4's note). Sources:
[`corrections-numbers.json`](corrections-numbers.json) › `K4_gain_decomposition`, `K7_card_term`,
`K1_aifoundry2_cap_held_out`, `K5_and_K2a_D5_peak_pool5`.

**In plain words.** On one footing, the lab's model gets a little better on new kinds of floats, from 0.187 to 0.182 W rms out of
kind, by one new term: **the bits the C register flips each op** (Q138(b)'s descriptor, now 6.4 ± 2.1 fJ a flip). That gain is
not resolved against M7's own form refitted the same way, but it is resolved against M7 and M6 as they were frozen. It sits on
the older blind pools: pool 3's floats 0.26 → 0.20 W, pool 4's 0.20 → 0.16 W. On pool 5's floats it gains nothing. **int8** gets a
discount for B bytes that flip seven or eight bits at once (−57 ± 29 fJ a bit), which lowers its error on the rows before pool 5
(0.240 → 0.207 W) and helps the power-law and W8A8 misses, but over-corrects the whole-line flip-flops (+0.66 and +0.78 W out of
kind), so on pool 5's int8 rows M8 is worse than M7's form (0.41 against 0.37 W on aifoundry3), unresolved. Neither the
exponent-field term E147 asked for, nor E145's per-position B prices, nor any of aifoundry2's three new terms lowered the error
they were registered to lower, so none is carried. **No cheap read predicts a card's scale to 1%**: card 1 runs at 0.960 of
aifoundry3's switching watts and aifoundry2 at 0.978, while the 600 MHz voltages say 0.910 and 1.010 (V²). A new card still
needs its own measured scale. **For pool 6**, the honest forecast is floats about 0.16-0.20 W rms on both 600 MHz cards and
int8 0.24-0.41 W.

*(Dated note, Tue 3 Nov 2026, after verification, C4 and C6.)* "The bits the C register flips each op" is `c_end`: the C
register's flips in one accumulate op at an emulated launch-end state (C = N_END × the op's increment), an estimate, not a
measured toggle count. It is a fitted correction worth about 0.039 W on an average float row (at most 0.51 W, on rows that
average 12.1 W), and reading it as the result path's toggles is a hypothesis. The gain over M7 and M6 as frozen is mostly
the footing refit (the note under the table). **int8, said fully:** `bsat` moves the power-law and W8A8 misses toward zero
(power-law −0.458 / −0.466 W against M7's form's −0.603 / −0.606 on aifoundry3 / card 1; W8A8 down +0.397 / +0.136 against
+0.471 / +0.207; up +0.141 / +0.072 against +0.217 / +0.145). It leaves the whole-line zero/one miss about 0.07 W worse
(−0.678 / −0.673 against −0.605 / −0.602) and the A-word flip-flop about 0.08 W worse (−0.406 / −0.292 against −0.321 /
−0.211), and it turns the ungated B-line flip-flop into a +0.66 / +0.78 W miss (against −0.21 / −0.06). All out of kind,
not blind. Sources: [`corrections-numbers.json`](corrections-numbers.json) › `K4_gain_decomposition.float.c_end_term_w`,
`K6_int8_pool5_misses`.

**1. Power, the same folds for M5's, M6's, M7's forms and M8** (rms of measured − predicted D, W; bias measured − M8;
[`nested-m8.json`](nested-m8.json) › `families.<family>.same_folds`):

| | rows | M6 frozen | M7 frozen | M5's form | M6's form | M7's form | **M8, nested** | M8 bias |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fp32 | 380 | 0.207 | 0.208 | 0.216 | 0.198 | 0.200 | **0.195** | −0.033 |
| fp16 | 247 | 0.176 | 0.181 | 0.205 | 0.179 | 0.166 | **0.160** | +0.011 |
| floats, aifoundry3 fp32 / fp16 | | 0.212 / 0.159 | 0.205 / 0.160 | 0.226 / 0.222 | 0.209 / 0.173 | 0.204 / 0.159 | **0.193 / 0.147** | |
| floats, card 1 fp32 / fp16 | | 0.200 / 0.189 | 0.213 / 0.197 | 0.201 / 0.189 | 0.180 / 0.183 | 0.192 / 0.173 | **0.198 / 0.170** | |
| floats, pool 3 (E115) | 19 | 0.312 | 0.273 | 0.371 | 0.318 | 0.262 | **0.195** | −0.100 |
| floats, pool 4 (E140) | 18 | 0.211 | 0.215 | 0.160 | 0.175 | 0.198 | **0.163** | +0.002 |
| floats, pool 5 aifoundry3 (E141) | 21 | 0.136 | 0.151 | 0.221 | 0.132 | 0.159 | 0.158 | −0.043 |
| floats, pool 5 card 1 (E142) | 21 | 0.188 | 0.186 | 0.216 | 0.145 | 0.146 | 0.155 | +0.004 |
| E147's single-bit steps | 70 | 0.229 | 0.224 | 0.227 | 0.229 | 0.228 | **0.219** | −0.121 |
| int8 | 140 | 0.244 | 0.237 | 0.265 | 0.261 | 0.256 | **0.241** | −0.031 |
| int8, pool 4 (E140) | 7 | 0.313 | 0.210 | 0.316 | 0.313 | 0.225 | 0.265 | +0.003 |
| int8, pool 5 aifoundry3 / card 1 | 9 / 9 | 0.361 / 0.326 | 0.353 / 0.317 | 0.382 / 0.310 | 0.373 / 0.303 | 0.374 / 0.309 | **0.411 / 0.397** | |
| int8, rows outside pool 5 | 122 | 0.226 | 0.218 | 0.251 | 0.247 | 0.240 | **0.207** | |

M6 and M7 as frozen are in sample on most of these rows (on the old footing), so those columns flatter them; the four refitted
columns are all out of kind on the same folds. Pool 5's rows were blind for M7 and M6 as frozen.

**2. M8, frozen.** [`m8.json`](m8.json), written by [`fit_m8.py`](fit_m8.py) (imports Q138(m)'s `fit_m7.py`, Q139(u)'s
`reduce_footing.py`, pool 5's `make_blind5.py` and E147's `posthoc_m7_e147.py`, unchanged). sha256s are in § Files.
- **Floats, form `G13_cend`** = M7's `G8_gtr_glive` + `c_end` (fJ per count, ± 1 s.e., jackknife by kind): mult 1.629 ± 0.018,
  add32 1.630 ± 0.033, add16 1.579 ± 0.044, bus 6.81 ± 0.41, rest 2.284 ± 0.062, clk 0.633 ± 0.068, gtr 140.7 ± 14.7, glive
  2.90 ± 0.47 nJ an op at every slot live, **c_end 6.44 ± 2.05 fJ per C-register bit flip**. Picked in all 343 folds. Dropping
  `c_end` gives 0.1872 W plain leave-one-kind-out (with it 0.1818). `c_start` (0.1850), `xfld` (0.1882), `a_exp` + `b_exp`
  (0.1882) and `xfld` + `c_end` (0.1831) did not do as well. `glive`'s reading stays a fitted correction, collinear with `clk`
  (M7's C3).
- **int8, form `J13_bsat`** = M7's `J8_b138` + `bsat`: nets_nobus 3.405 ± 0.155, bus 11.3 ± 2.9, clk 2.073 ± 0.179, b138 +5.1 ± 12.9,
  **bsat −56.8 ± 29.4 fJ per bit flipped in a B byte that flips seven or eight bits**. Picked in 63 of 66 folds (`J16_bpos_bsat`
  2, `J8_b138` 1). Without `bsat`, 0.2557 W (with it 0.2437). With `bsat` in, b138's −23 fJ correction (M7) falls to zero
  within its error (+5.1 ± 12.9): the correction M7 put on the bench's B count is carried by the whole-byte flips (a reading of
  the fit, not a measurement). `bpos` (E145's prices, 0.2565), `absat` (0.2567)
  and `c_end` (0.2607) did not lower the error.
- **Card term**: M5's C0 (E78's and E82's same tiles), chosen again inside every fold, **0.9616** floats and int8. Paired kinds
  read card 1 at a median 0.960 of aifoundry3 (104 float kinds with D ≥ 5 W; int8 0.962, 39 kinds).
- **Interval pools** (M8's nested rms, W): fp32 aifoundry3 0.193, card 1 0.198; fp16 0.147, 0.170; int8 0.244, 0.238.
- **Carried**: M7's heat law and band (dT = 0.1186 °C per board W on aifoundry3, 0.1151 on card 1, over the 4.5 s run;
  aifoundry2's burst law 0.140 °C per W), applied to M8's S; Q138(t)'s heat-over-minutes chain as E144 scored it; E139's
  memory-path term (zero for a kinds tile).

*(Dated note, Tue 3 Nov 2026, after verification, C7.)* The card term was not "chosen again inside every fold". The family
(C0) was chosen once, on every paired kind, before the fold loop (`fit_m8.py` `run_family`: `best_ct` at line 250, the fold
loop from line 259), and only its value, the C0 ratio, is refitted without the held-out kind inside every fold
(`fit_m7.Fam`). It is a small selection step that sees the held-out kinds, and it matters little: the three card terms score
level, 0.7735 / 0.7738 / 0.7736 W on the float pairs and 0.0975 / 0.1000 / 0.1000 W on int8's
([`corrections-numbers.json`](corrections-numbers.json) › `K7_card_term`).

**3. The band rule** (`m8.json` › `band_rule`; registered in `f640fb7a`). Power: half-width = k × √(pool² + s² xᵀCx), pool =
M8's nested rms for the tile's format and card, C the jackknife covariance, s the card scale; **k = the larger of the 95th
percentile of |nested residual| / pool over all M8 rows and over the rows of blind pools 3, 4 and 5 (E115, E140, E141, E142)**:
floats 2.196 (all rows; the pool rows give 2.04), int8 2.835 (the pool rows; all rows 2.31). On one footing the blind pools'
float rows are no longer outliers: in M7 they set k at 3.18. Coverage is calibration: floats 595 of 627 (E147's small steps 64
of 70), pool rows 78 of 79, and 78 of 79 with each pool row left out of k; int8 138 of 140, pool rows 29 of 31 (28 of 31 left
out). Heat: M7's k_h. aifoundry2: § 4.

**4. aifoundry2 under its own governor, in bursts.** M7's relation P(f) = B(f) + c × s(f) (E136's B and s, aifoundry2's own
voltages), E83's dither at an effective cap W* ± 2.75 W, c = c_zeros + D / 1.01865 from a tile's D at 600 MHz on aifoundry3. 95
bursts: E80's and E83's kinds cells, E143's 36 pool-5 cells and its 3 session-link cells (D1). **Footing: the meter's dips kept
in training and test alike** (the committed kspeed reductions; Q139(u) F4), so E160 is scored on its registered reduction with
dips kept. Leave one kind out, from the measured aifoundry3 D (`aifoundry2.configs`):

| configuration | clock rms, MHz | board rms, W | governed (43): MHz / W / bias | pinned (52): MHz / W / bias | kept? |
|---|---:|---:|---|---|---|
| M7's form, cap refitted (65.20 W) | **7.13** | **1.83** | 10.55 / 2.29 / +1.24 | 0.81 / 1.32 / −1.04 | the base |
| + zeros level per format | 7.25 | 1.98 | 10.74 / 2.36 / +1.18 | 0.87 / 1.61 / −1.40 | no (both worse) |
| + D scale per format | 7.13 (+0.002) | 1.77 | 10.56 / 2.26 / +1.28 | 0.80 / 1.23 / −0.88 | **no** (the clock rose by 0.002 MHz; the board fell by 0.055 W) |
| + cap rising with overshoot | 7.13 | 1.83 | identical: γ = 0 in every fold | | no |

*(Dated note, Tue 3 Nov 2026, after verification, C8.)* "The meter's dips" above is the wrong label. On aifoundry2, A2's
samples are the governor's real low-voltage phases (Q139(u)'s verification, its fault 1). Of E143's 480 A2 dips, 449 sit
between samples at 55 W or more, and 98% of those fall within ±2 samples of a minion clock change, against 52% of the other
3,518 samples at 55 W or more ([`corrections-numbers.json`](corrections-numbers.json) › `K8_a2_dips_vs_clock`). The choice
stands, and it is the right one: A2's samples are kept in training and test alike (the committed kspeed reductions).

End to end through M8's nested D (92 bursts whose kind has one): **7.16 MHz and 1.86 W rms** (95th percentiles 16.9 MHz and
3.50 W, the frozen bands); governed 10.68 MHz and 2.28 W, board bias +1.16 W (the model low); pinned 0.83 MHz and 1.44 W. M7's
frozen relation through the same D on the same bursts: 7.27 MHz and 1.73 W (governed 10.86 MHz, 2.03 W). So refitting M7's cap on
the clocks, as M7 did, trades 0.12 MHz of clock for 0.13 W of board. **What none of the three terms reaches is the governed
board bias**: under the governor the board reads about 1.2 W above P(f) at the measured clock, a power-at-the-dithered-clock
error, not the cap's. The D-scale term would have taken the board to 1.77 W; it fell to the registered rule by 0.002 MHz.
**Peak board power** (the stop of section 22): the highest board sample of each of E143's 117 traces exceeds the P800 its own
measured c gives by a median 1.94 W, 95th percentile 2.95 W, at most 5.32 W. `predict_blind6.py` gives each tile P800(c) +
1.94 W (expected) and P800(c at the top of D's band) + 2.95 W (the 95% upper value), and flags tiles whose upper value exceeds
82 W. On pool 5 (in sample) the upper value covers 35 of 36 tiles' highest sample (`fp32.lowrank2_w` 86.65 W against 86.19)
and flags 4 tiles (`fp32.wideexp48_dense` 88.2 W, `lowrank2_w`, `anchor_randn`, `sorted_k`).

*(Dated note, Tue 3 Nov 2026, after verification, C1, C5 and D5.)* The end-to-end figures and the frozen bands above use the
cap fitted on all 95 bursts, the scored ones included. With the cap held out per kind as well they read **7.22 MHz /
1.87 W** rms and 95th percentiles 17.6 MHz / 3.54 W (the cap moves 65.1-65.3 W over the folds); the bands stay frozen as
committed. "M7's frozen relation ... 7.27 MHz and 1.73 W" is on the same bursts, in sample on E80's and E83's. The 35-of-36
coverage and the 4 flags are now computed ([`corrections-numbers.json`](corrections-numbers.json) ›
`K5_and_K2a_D5_peak_pool5`). The flagged tiles' 95% values are 86.16 W (`anchor_randn`), 86.19 (`lowrank2_w`), 83.37
(`sorted_k`) and 88.22 (`wideexp48_dense`); their highest samples are 85.82, 86.65, 81.98 and 87.95 W. The expected peak
misses the highest sample by 1.60 W rms. All of it is in sample, from one session's bursts. The 95% value puts c at the top
of D's band before adding the q95 excess, which the registration did not say: departure D5.

**5. The card-scale predictor (rank 5): FAIL.** Measured scales (D on the card over aifoundry3's D, the same tiles, 600 MHz):
card 1 **0.960** floats, 0.962 int8 (the footing's paired kinds); aifoundry2 **0.978** floats, 0.959 int8 (its bursts, (c − c_zeros)
/ D600 with its own s(800) = 1.905). Each cheap read, as s = (read / read_a3)^β, leave one card out (`nested-m8.json` ›
`card_scale.loco`; floats; the held-out card's scale against the other two):

| read (aifoundry3 / card 1 / aifoundry2) | β physical: error on aifoundry3 / card 1 / aifoundry2 | β fitted on the other two | within 1% on all three? |
|---|---|---|---|
| voltage at 600 MHz (0.5219 / 0.4987 / 0.5180 V) | V²: +2.2% / **−5.2%** / +3.2% | −1.8% / −8.5% / +1.5% | **no** |
| idle board power (25.90 / 33.06 / 25.46 W) | −13% / +33% / −13% | −2.3% / +41% / +2.5% | no |
| zeros level, fp32 (1.99 / 1.66 / 1.44 W) | +25% / +1.1% / −21% | −6.3% / +2.9% / −5.0% | no |
| leakage slope (0.2056 / 0.3134 / 0.2936 W/°C) | −34% / +31% / +16% | +8.5% / +1.5% / −1.3% | no |

The voltage is the physical candidate (switching energy goes as CV²), and it fails worst on card 1: card 1's 600 MHz rail sits
4.4% below aifoundry3's, which V² makes 9% fewer watts, but card 1 draws only 4% fewer. Whatever sets a card's capacitance or
activity per volt differs between these cards by about 5%. **For an unmeasured card the error stays 2-5%** (0.4-1.0 W on a 20 W
float kind), more than M8's whole error. M8 keeps the measured C0 term for card 1; aifoundry2 keeps M7's 1/1.01865. A new card
needs one paired run of a few kinds (E82's design) to set its scale.

*(Dated note, Tue 3 Nov 2026, after verification, C3 and D6.)* aifoundry2's 0.978 uses all 53 float bursts with D ≥ 5 W,
governed ones included, where the registration says "its bursts pinned at 795-800 MHz". Pinned only, it is 0.976 (14 bursts;
int8 0.959 either way): departure D6. With it, V² leave one card out reads +2.1 / −5.3 / +3.5% (fitted −2.1 / −9.8 /
+1.7%), FAIL as before. The scale also rests on s(800) with V². At a board exponent of about 2.3 (Q139(s)'s corrections, lab
`c944ff99`) it would be about 4% lower (0.940 at n = 2.28, 0.938 at 2.3), and at 2.45 about 7% lower (0.914), by an
approximate re-reduction ([`corrections-numbers.json`](corrections-numbers.json) › `K3_aifoundry2_scale_by_exponent`). So
aifoundry2's measured scale carries a 4-7% systematic from the form of s(f), more than the 1% rule, and card 1, at 600 MHz
with no s(f), is the clean held-out card. The FAIL does not rest on aifoundry2: V² from aifoundry3 alone misses card 1 by
−4.9%, and with aifoundry2 at 0.940 or 0.914 the voltage still fails (`K2b_D6_aifoundry2_scale_and_loco`).

**6. The predictor for pool 6.** [`predict_blind6.py`](predict_blind6.py) `<pool_dir> <card>` (card `aifoundry3`,
`aifoundry1c1` or `aifoundry2`) reads a pool in blind pool 5's layout (`blind6.json` preferred) and the bench's counts for its
tiles (`--counts`, or the one `counts-*.json` in the pool; without counts it prints the bench command and exits 2). It writes
`predictions-<card>.json` and `.md`: per tile, M8's, M7's and M6's D with 95% bands and the die rise over 4.5 s on aifoundry3 or
card 1; on aifoundry2, the burst clock, board W, D in the burst and the die rise with bands, and M8's predicted peak board
power (expected and 95% upper, with a flag above 82 W). M7 and M6 go through their frozen files and M7's frozen clock term,
exactly as `predict_blind5.py` computed them. **Self-test** on pool 5 ([`selftest_predict_blind6.py`](selftest_predict_blind6.py)
→ [`selftest-predict-blind6.txt`](selftest-predict-blind6.txt)): M7 and M6 through it reproduce Q138(x)'s frozen pool-5
predictions field for field on all three cards (360, 360 and 504 fields, 0 differ). Pool 5 is in M8's fit, so M8's numbers
there test nothing. **For Q139(x):** reduce pool 6 on aifoundry3 and card 1 with `reduce_footing.K_FROZEN` and A2 once (M8's
footing); on aifoundry2 with the registered kspeed reduction, dips kept.

*(Dated note, Tue 3 Nov 2026, after verification, C9.)* `predict_blind6.py` records the sha256 of `m8.json`, `m7.json`,
`m6.json`, itself and `fit_m8.py`, but not of the other files it reads at run time, which set the features and the clock.
Run on pool 5 under an audit hook, it reads 47 code and model files in the tree besides the pool's own: `fit_m7.py`,
`fit_m6.py`, `m6_rows.py`, `fit_m5.py`, `reduce_footing.py` and `footing.json`, `make_kinds.py`, `make_blind5.py`,
`predict_blind5.py`, `posthoc_m7_e147.py`, E119's dither module and the modules it calls (`surface_hpl.py`,
`surface_hpl_t.py`, E83's `predict_e83.py`), `counts-v2.json`, `predictions-e145.json`, `predictions-e101.json`, and the
committed experiment files that M7's rows come from. At this note every one equals its version at `122da8b6`
([`corrections-numbers.json`](corrections-numbers.json) › `K9_predictor_inputs` lists them with their sha256, and gives the
`git diff --stat 122da8b6 -- …` command over them). **For Q139(x):** run that command before computing pool 6's predictions,
and record its empty output in the predictions note.

## What this does to predicting power and heat

**Terms measured or tested:** the C-register term (kept for floats: 6.44 ± 2.05 fJ a flip), a near-whole-byte discount on int8's
B side (kept: −57 ± 29 fJ a bit), the exponent-field term, E145's per-position B prices, A's whole-byte flips and the C term for
int8 (all tested, none lowered the error), aifoundry2's zeros level, D scale per format and cap rising with overshoot (tested,
none kept), aifoundry2's peak board power (new), and the card-scale predictor (tested, fails). **Out-of-sample error before →
after (nested leave one kind out, the same folds, one footing):** floats 0.187 W (M7's form) → **0.182 W** (not resolved;
resolved against M7 and M6 as frozen, 0.198 and 0.195 W); int8 0.256 → **0.241 W** (not resolved); on pool 5's rows floats
0.159 / 0.146 → 0.158 / 0.155 W and int8 0.374 / 0.309 → **0.411 / 0.397 W** (worse, not resolved); pool 3's floats 0.262 → 0.195
W, pool 4's 0.198 → 0.163 W. aifoundry2's governed bursts, end to end: 7.27 MHz / 1.73 W (M7's frozen relation) → 7.16 MHz /
1.86 W (M8). The peak board power is new: P800 + 1.94 W expected, + 2.95 W at 95%. **A card's scale from cheap reads: not
achievable to 1%** (the voltage misses card 1 by 5%). **Heat is not changed**: M7's law is carried, and the die rise follows
the board watts M8 predicts. The blind test is pool 6.

*(Dated note, Tue 3 Nov 2026, after verification, C1 and C4.)* Two labels above are corrected. The floats' "resolved against
M7 and M6 as frozen" is mostly the footing refit: M7's form refitted gains −0.011 W on M7 as frozen (resolved), and the C
term −0.005 W (not resolved). "aifoundry2's governed bursts, end to end: 7.27 MHz / 1.73 W → 7.16 MHz / 1.86 W" covers all 92
bursts under aifoundry2's own governor (41 governed, 51 pinned), on the same bursts, with M8's cap in sample and M7's
relation in sample on E80's and E83's. With M8's cap held out per kind it is 7.27 / 1.73 → **7.22 MHz / 1.87 W**; on E143's
36 bursts alone, where M7 is blind, 4.71 MHz / 1.45 W → 3.81 MHz / 1.64 W. No model term changes, and heat is unchanged.
aifoundry2's measured card scale carries a 4-7% systematic from s(f)'s form (§ 5's note).

## Registered against what happened

| registered (`f640fb7a`) | happened |
|---|---|
| rows: M7u's 637 + E141's 30 + E142's 30 + E147's 70 steps | 767 rows (627 float, 140 int8), 27 experiments, none missing |
| candidates `xfld`, `c_end` / `c_start`, `bpos`, `bsat` / `absat` | all computed; `c_end` and `c_start` reproduce pool 5's committed descriptors on all 36 tiles |
| floats: keep only terms that beat M7's form | `G13_cend` kept (nested 0.1818 < 0.1872) |
| int8: the same | `J13_bsat` kept (nested 0.2412 < 0.2557), though it is worse on pool 5's rows |
| band k = max(all rows, pools 3-5's rows) | floats 2.196, int8 2.835 |
| aifoundry2: three terms, each kept only if both LOKO rms fall | none kept; the cap refitted on the clocks (65.20 W) |
| peak = P800 + the q95 excess over E143's traces | 2.95 W (median 1.94 W) |
| card scale within 1% on each held-out card | **FAIL** for every read |
| `predict_blind6.py` with M7 and M6 as frozen | self-test PASS |

**Departures** (dated Tue 3 Nov 2026, each before the numbers it touches unless said):
- **D1.** E143's results hold three session-link cells (`k-fp32-randn`, `k-fp16-randn`, `k-int8-full`: E80's own tiles re-run in
  E143's session) that the registration did not name. Run 1 stopped on them, with the power families' numbers printed and no
  aifoundry2 number computed. They enter as their E80 kinds (D from E78's footing row), so 95 bursts, not 92.
- **D2.** M7's frozen aifoundry2 relation through the same nested D was added for the side-by-side after run 2 was read. It is
  reported only; no selection uses it, and run 3 (the freeze) reproduced run 2's numbers.
- **D3.** The leakage-slope read for aifoundry2 is E66's dedicated idle cycles (0.2936 W/°C), a different method from F1's
  idle brackets, because aifoundry2 has no 600 MHz kinds rests. The zeros level for aifoundry2 is its c_zeros (the zeros'
  watts over B(600) through s(f)), not a pinned 600 MHz run.
- **D4.** The PATH's python3 has no numpy; every run used the Intel's `/usr/bin/python3` 3.9.6 with numpy 1.26.4.
- **D5** *(declared after verification, Tue 3 Nov 2026; it came after the registration and after the numbers it touches)*.
  The registration's peak rule is "predicted peak = P800(c) + q, q the 95th percentile" of the excess. The frozen predictor
  gives instead an expected peak, P800(c) + the median excess (1.94 W), and a 95% upper value, P800(c at the top of D's 95%
  band) + q95 (`m8.json` › `aifoundry2.peak.rule`; `predict_blind6.py` line 190). The upper value is the stricter. On pool 5
  (in sample) it sits a median 0.81 W (0.60-2.34) above the registered value, covers 35 of 36 tiles' highest sample against
  the registered value's 32, and flags the same 4 tiles above 82 W ([`corrections-numbers.json`](corrections-numbers.json) ›
  `K5_and_K2a_D5_peak_pool5`). Verdict-neutral: no registered rule scores the peak; it feeds section 22's 82 W stop, where
  the stricter value is the safer one.
- **D6** *(declared after verification, Tue 3 Nov 2026; after the registration and the numbers it touches)*. The
  registration measures aifoundry2's scale "from its bursts pinned at 795-800 MHz"; `fit_m8.py` (`scale_vs_a3`) used every
  float burst with D ≥ 5 W, governed ones included: 0.978 over 53 bursts, against 0.976 pinned only (14); int8 0.959 over 24,
  against 0.959 pinned only (21). Verdict-neutral: V² leave one card out fails either way (+2.2 / −5.2 / +3.2%, against +2.1
  / −5.3 / +3.5%), and M8's aifoundry2 predictions do not use this scale: they carry M7's 1/1.01865
  (`K2b_D6_aifoundry2_scale_and_loco`).

## Order (PST, Tue 3 Nov 2026)

1. 04:34 brief read; 04:35-04:42 Q138's final critic, M7's README and code, Q139(u)'s footing, E141-E148's READMEs and files,
   pool 5's manifest and C emulation read. Pool 6 and its designer's scratch were never read or listed.
2. 04:43:20 **the registration committed and pushed** (`f640fb7a`), before `fit_m8.py` existed.
3. 04:44-04:49 `fit_m8.py` written; the C descriptors checked against pool 5's committed values (36 of 36 equal).
4. 04:49:50 run 1 (the power families complete; stopped at D1); 04:51-04:52:30 run 2, read; D2 added; 04:53-04:54 **run 3, the
   freeze** ([`fit-output.txt`](fit-output.txt)); then the self-test (PASS) and this README.

*(Dated note, Tue 3 Nov 2026, after verification, C10.)* git records the registration `f640fb7a` at **04:43:16 PST** and the
freeze `122da8b6` at **04:57:59 PST**, author and committer alike ([`corrections-numbers.json`](corrections-numbers.json) ›
`K10_git_times`). The 04:43:20 in item 2 (and in this lane's result) is 4 s later, probably the push. The registration's own
header says "about 04:50 PST"; that is wrong, and its text stays as committed. The window at the top, 04:34-05:05 PST, ends
after this README's own commit: the lane's work ran 04:34-04:58 PST.

## What this cannot say

- **Nothing here is blind.** Pool 5 is now training data; the candidate terms were named from Q138's misses (E141, E145, E147)
  and Q138(b)'s post hoc C correlation, and the nested procedure, not a blind pool, chose among them. Pool 6 is the test.
- **The C-register term's gain is small and not resolved against M7's form** (−0.005 W [−0.012, +0.002]). It is a fitted term
  on an emulated descriptor (`c_end`: the launch-end state, estimated, not measured), and its physical reading (the result
  path's toggles) is a hypothesis.
- **int8's new term may be wrong in kind.** `bsat` lowers the error on the rows before pool 5 and raises it on pool 5's
  whole-line flip-flops, out of kind. It is a discount on near-whole-byte flips with a ±52% s.e.; the registered rule kept it.
  On pool 6's int8 tiles M8 may do worse than M7.
- **E147's exponent items still read 0.5-0.6 W high** (B bits 28-29, A bit 19), and no registered exponent term lowered the
  overall error; their fix is not in M8.
- **aifoundry2's governed board power is about 1.2 W low** where the governor acts, and none of the registered terms reaches
  it. Its scale (0.978) depends on s(800) = (V800/V600)² × 4/3; at Q139(s)'s board exponent 2.45 it would be about 4% lower.
- *(Dated note, Tue 3 Nov 2026, after verification, C3.)* The figure in the bullet above is low. At a board exponent of about
  2.3, where Q139(s)'s corrections (`c944ff99`) put it, aifoundry2's scale would be about 4% lower (0.940 at 2.28), and at 2.45
  about 7% lower (0.914), against 0.978. This is an approximate re-reduction
  ([`corrections-numbers.json`](corrections-numbers.json) › `K3_aifoundry2_scale_by_exponent`). So that scale carries a
  4-7% systematic from s(f)'s form, and card 1 is the clean held-out card for the card-scale test.
- *(Dated note, Tue 3 Nov 2026, after verification, C4.)* The figures here are out of kind, not blind, and the candidate terms
  were named post hoc from Q138's misses. "Resolved against M7 and M6 as frozen" mostly measures the footing refit; the peak
  margin rests on one session's bursts, in sample.
- **The card-scale test has three cards**, so a fitted exponent rests on one pair each time; none of the reads came within 1%.
- One lane wrote the model and its scoring code; pool 6's designer is independent, and E153, E157 and E160 are the test.

## Files

| file | what |
|---|---|
| [`M8-REGISTRATION.md`](M8-REGISTRATION.md) | the registration, committed first (`f640fb7a`, 04:43:20 PST) |
| [`fit_m8.py`](fit_m8.py) | the fit: rows on the footing, the candidate features, forms, card term, nested leave-one-kind-out with M6's and M7's forms and both as frozen on the same folds, the bootstrap, the band rule, aifoundry2's terms and peak, the card-scale test, the freeze |
| [`m8.json`](m8.json) | **the freeze**: per family the form, constants (J), jackknife covariance, card term and scales, interval pools, band k; aifoundry2's relation, kept configuration, parameters, bands and peak rule; the card-scale test; heat carried from M7; the band rule in words |
| [`nested-m8.json`](nested-m8.json), [`fit-output.txt`](fit-output.txt) | every form's plain and nested errors by format, card and experiment, paired bootstraps, the largest misses, pool 5's rows, aifoundry2 per configuration and per burst, the peaks, the card scale |
| [`rows-m8.json`](rows-m8.json) | the 767 assembled rows with their features |
| [`predict_blind6.py`](predict_blind6.py) | the frozen predictor for pool 6 (M8, M7, M6; three cards; aifoundry2's peak) |
| [`selftest_predict_blind6.py`](selftest_predict_blind6.py), [`selftest-predict-blind6.txt`](selftest-predict-blind6.txt) | the predictor on pool 5 against Q138(x)'s frozen predictions |
| *(added after verification, Tue 3 Nov 2026)* [`corrections-numbers.py`](corrections-numbers.py), [`corrections-numbers.json`](corrections-numbers.json), [`corrections-numbers.txt`](corrections-numbers.txt) | every number the corrections quote (K1-K10), post hoc, from committed inputs, with M8's frozen code imported unchanged; it first reproduces 35 committed numbers |

sha256 at the freeze: `m8.json` **`8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd`**; `fit_m8.py`
`3764bc4c345412ae71d66f18f114d0fe395d8db90988d699988513a590b6bad7`; `predict_blind6.py`
`6bc447eb5c5d88de6f084265908191cbbe372ce3a46b669babbce50a374fbbf1`; `nested-m8.json`
`f284b5407a98641ec33a57410be925a4c64199e0033b6c94ef893702de0f4905`; `rows-m8.json`
`6e3383ef10e2f8a3102755695c4ba95fe6367bd8ff17498a00382420349681d9`. Imported unchanged: Q138(m)'s `fit_m7.py` `cb01d826…c55c0`,
`m7.json` `bfeea822…d8b2`, `predict_blind5.py` `0d114d5b…c369`; Q139(u)'s `reduce_footing.py`, `footing.json`, `rows-m7u.json`
and `reduced/`.

Rerun from the tree's root, with a python that has numpy:

```
python3 -u docs/reports/data/2026-11-03-q139m-model/fit_m8.py <scratch dir> > docs/reports/data/2026-11-03-q139m-model/fit-output.txt   # ~2 min
python3 docs/reports/data/2026-11-03-q139m-model/selftest_predict_blind6.py <scratch dir> > docs/reports/data/2026-11-03-q139m-model/selftest-predict-blind6.txt
# pool 6: count its tiles with the bench (Q133(b)'s README, run_kinds.py --only __none__ --extra-tiles ...), then for each card
python3 docs/reports/data/2026-11-03-q139m-model/predict_blind6.py tools/claims-v3/kinds/blind6 aifoundry3 --counts <counts.json>
```

*(Added after verification, Tue 3 Nov 2026.)* The corrections' numbers: `python3 -B
docs/reports/data/2026-11-03-q139m-model/corrections-numbers.py <scratch dir>` (about half a minute). It writes
`corrections-numbers.json` and `.txt` beside it and nothing else in the tree; pool 5's predictions and the trace go to the
scratch dir.

## Corrections after verification (Tue 3 Nov 2026)

An independent verifier of this lane (Q139's, written up at 05:27 PST) re-derived M8 from the committed files, with this
lane's code and with its own: every power number from `rows-m8.json` (its own least squares and nested code), the bootstraps
with an independent seed, the C-register and byte features with its own emulator on all 414 distinct tiles, aifoundry2's 95
bursts and selection, the peak excess from E143's raw traces, the card-scale table, the self-test (0 of 1,224 fields
differ), the blind order and a privacy scan. It found M8 sound, with ten minor faults. None changes a frozen, registered or
measured number, a kept term or a verdict, and none involves a device command. [`corrections-numbers.py`](corrections-numbers.py)
(committed inputs only, M8's frozen code imported unchanged) reproduces 35 committed numbers before it prints anything new,
and prints every number below to [`corrections-numbers.txt`](corrections-numbers.txt) and
[`corrections-numbers.json`](corrections-numbers.json) (keys K1-K10). No frozen file was edited: `M8-REGISTRATION.md`,
`m8.json`, `fit_m8.py`, `predict_blind6.py`, `nested-m8.json`, `rows-m8.json` and the self-test are as committed in
`f640fb7a` and `122da8b6`, and this README gains lines only.

- **C1. aifoundry2's end to end and its bands fit the cap in sample.** § 4 and § "What this does" give the end-to-end figures
  (7.16 MHz / 1.86 W) and the frozen bands (95th percentiles 16.95 MHz / 3.50 W) as if out of sample, but `fit_m8.py` fits
  the cap W0 on all 95 bursts, the scored ones included (`a2_fit`: `par = fit_params(list(range(len(cells))), cfg_kept)`
  feeds both). With the cap held out per kind as well: **7.22 MHz / 1.87 W** rms (7.215 / 1.871), 95th percentiles 17.57 MHz
  / 3.54 W; governed (41 bursts below 795 MHz) 10.77 MHz / 2.30 W with a board bias of +1.16 W; pinned (51) 0.83 MHz /
  1.44 W; W0 65.1-65.3 W over the folds. The frozen bands stay as committed, about 3-4% narrower in clock than the held-out
  version, and Q139(x) uses them as committed. The "before", M7's frozen relation through M8's nested D (7.27 MHz / 1.73 W),
  is in sample on E80's and E83's 56 bursts, where M7 fitted its cap, and blind on E143's 36: there it reads 4.71 MHz /
  1.45 W, against M8's 3.81 / 1.64 with the cap held out (3.76 / 1.63 as frozen). The 92 are all the bursts under
  aifoundry2's own governor, 41 governed and 51 at 795-800 MHz, not governed bursts only (`K1_aifoundry2_cap_held_out`).
- **C2. Two departures were undeclared; they are D5 and D6 now** (§ Departures). D5: the peak's 95% value puts c at the top of
  D's band before adding q95, and an expected value with the median excess is added; the registration said P800(c) + q95.
  D6: aifoundry2's scale uses all 53 float bursts, where the registration said its bursts pinned at 795-800 MHz (0.976 over
  14). Both came after the registration and change no verdict (`K5_and_K2a_D5_peak_pool5`, `K2b_D6_aifoundry2_scale_and_loco`).
- **C3. aifoundry2's scale under a steeper s(f) was understated.** "At Q139(s)'s board exponent 2.45 it would be about 4%
  lower" is about 3 points low at 2.45. Re-reduced approximately (each burst's c_w rescaled by s(f)/s'(f) at its mean clock,
  the zeros' c at 800 MHz; the kspeed dither weighting not re-run): 0.978 at n = 2, **0.940 at 2.28 (−3.9%)**, 0.938 at 2.3
  (−4.2%), **0.914 at 2.45 (−6.6%)**; at 800 MHz alone the factor is 0.951 at 2.28 and 0.923 at 2.45. Q139(s)'s corrections
  (`c944ff99`) put the board exponent at about 2.3 (2.26-2.31). So aifoundry2's measured scale carries a 4-7% systematic from
  s(f)'s form, and card 1 is the clean held-out card. The FAIL holds every way: V² from aifoundry3 alone misses card 1 by
  −4.9%, and with aifoundry2 at 0.940 V² leave one card out reads +0.2 / −7.1 / +7.4% (at 0.914, −1.2 / −8.4 / +10.5%)
  (`K3_aifoundry2_scale_by_exponent`, `K2b_D6_aifoundry2_scale_and_loco`).
- **C4. The framing of the floats' gain overstated the new term.** On the same folds: M8 − M7's form −0.0054 W [−0.0122,
  +0.0017], not resolved; M7's form − M7 as frozen **−0.0108 [−0.0178, −0.0040], resolved**; M7's form − M6 as frozen −0.0082
  [−0.0190, +0.0036], not resolved. So M8 − M7 as frozen (−0.0162 [−0.0251, −0.0069]) and M8 − M6 as frozen (−0.0135 [−0.0256,
  −0.0010]) are mostly the footing refit, and the frozen models are in sample, on the old footing, on most rows. For int8,
  M7's form refitted is worse than M7 as frozen, +0.0190 [+0.0091, +0.0289]. The C term is worth 0.0385 W on average over
  the 627 float rows (at most 0.505 W; the rows average 12.1 W of D). `c_end` is an emulated launch-end descriptor: reading
  its price as the result path's toggles is a hypothesis. The peak margin rests on one session's 117 traces, in sample. The
  wording for the records and the blog: *out of kind, not blind: 0.182 W against 0.187 for M7's form refitted on the same
  footing (not resolved); most of the gap to M7 and M6 as frozen is the footing refit* (`K4_gain_decomposition`).
- **C5. The peak's coverage had no committed computation; it has one now.** `predict_blind6.py`, run unchanged on pool 5 for
  aifoundry2 and set against E143's traces: the frozen 95% value covers **35 of 36** tiles' highest sample (the one over,
  `fp32.lowrank2_w`, 86.65 W against 86.19) and flags 4 tiles above 82 W: `anchor_randn` 86.16, `lowrank2_w` 86.19,
  `sorted_k` 83.37 and `wideexp48_dense` 88.22 W, whose highest samples were 85.82, 86.65, 81.98 and 87.95 W. The three
  tiles whose highest sample exceeded 82 W are all among them. The expected peak misses the highest sample by 1.60 W rms. In
  sample: pool 5 is in M8's fit, and E143's traces set the excess. The README's figures hold; the verification's write-up
  lists three of the four flags with their highest samples in place of their 95% values, and its own JSON agrees with the
  figures here (`K5_and_K2a_D5_peak_pool5`).
- **C6. int8's summary left out two misses that got worse.** `bsat` moves the power-law and W8A8 misses toward zero, leaves
  the whole-line zero/one miss about 0.07 W worse (−0.678 / −0.673 W against M7's form's −0.605 / −0.602 on aifoundry3 / card
  1) and the A-word flip-flop about 0.08 W worse (−0.406 / −0.292 against −0.321 / −0.211), and turns the ungated B-line
  flip-flop into a +0.66 / +0.78 W miss (`K6_int8_pool5_misses`).
- **C7. The card term was chosen once, not in every fold.** `run_family` picks C0 among the three card terms on every paired
  kind before the fold loop (line 250, before line 259); only the C0 ratio is refitted without the held-out kind. The three
  score level (floats 0.7735 / 0.7738 / 0.7736 W; int8 0.0975 / 0.1000 / 0.1000 W), so the choice moves nothing measurable
  (`K7_card_term`). The wording: *C0, chosen once on all rows (the three card terms level within 0.0003 W) and refitted inside
  every fold*.
- **C8. aifoundry2's A2 dips are not the meter's.** On aifoundry2 they are the governor's real low-voltage phases (Q139(u)'s
  verification, fault 1): 98% of E143's 449 dips between samples at 55 W or more fall within ±2 samples of a minion clock
  change, against 52% of the other 3,518 samples at 55 W or more. M8's footing, A2's samples kept in training and test alike
  (the committed kspeed reductions), is unchanged and right (`K8_a2_dips_vs_clock`).
- **C9. The predictor did not hash the files it imports.** Besides the five files it hashes, `predict_blind6.py` reads 47
  code and model files at run time (traced on pool 5); all 47 equal their versions at `122da8b6`. Q139(x) runs
  `git diff --stat 122da8b6 -- <the 47 paths>` (the full command is `K9_predictor_inputs.check_command`) before computing
  pool 6's predictions, and records its empty output in the predictions note (`K9_predictor_inputs`).
- **C10. Times.** git records `f640fb7a` at 04:43:16 PST and `122da8b6` at 04:57:59 PST, author and committer alike. The
  registration's header ("about 04:50 PST") and this README's 04:43:20 are corrected by dated notes, the registration's text
  left as committed; the lane's work ran 04:34-04:58 PST (`K10_git_times`).

**What the corrections do to predicting power and heat.** No model term is measured, added or changed, and nothing frozen
moves. One out-of-sample figure is corrected: aifoundry2's bursts end to end, with M8's cap held out per kind, read **7.22
MHz / 1.87 W** rms (95th percentiles 17.6 MHz / 3.54 W), not the cap-in-sample 7.16 / 1.86; M7's frozen relation on the same
bursts reads 7.27 / 1.73 (in sample on E80/E83), and on E143's 36 bursts alone, where M7 is blind, M7 reads 4.71 MHz / 1.45 W
against M8's 3.81 / 1.64. The floats' out-of-kind error stays 0.187 → 0.182 W, not resolved; of the 0.016 W gap to M7 as
frozen, 0.011 W is the footing refit and 0.005 W the C term. int8 stays 0.256 → 0.241 W, not resolved, and worse on pool 5's
rows. The card-scale predictor still fails: the voltage misses card 1 by 4.9% from aifoundry3 alone, and aifoundry2's
measured scale carries a 4-7% systematic from s(f)'s form. The peak rule covers 35 of 36 pool-5 tiles in sample (the
registered form would cover 32). Heat is unchanged: M7's law is carried. The blind before → after is pool 6's, from E153,
E157 and E160.
