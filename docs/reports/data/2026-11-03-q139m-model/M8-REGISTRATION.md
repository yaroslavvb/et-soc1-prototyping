# Q139(m): M8's registration - rows, candidate terms (the C-register candidate among them), selection, band rule, aifoundry2's terms and the card-scale test, written before any M8 fit runs

*Tue 3 Nov 2026 (week 45), about 04:50 PST, on the Intel, desk only. Written and committed before `fit_m8.py` exists and
before any candidate feature is computed on any row. It answers Q138's final critic's open **rank 2** (M8) and **rank 5**'s
card-scale predictor, for the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 6** (a power model across kinds; items 15, 12 and 7 feed its terms). Blind pool 6 does not exist in the tree, and this
lane never reads `tools/claims-v3/kinds/blind6/` or the pool designer's scratch. Everything below is fixed now; a departure is a
dated amendment written before the numbers it touches.*

## 1. Footing

- **aifoundry3 card 0 and aifoundry1 card 1 (600 MHz):** Q139(u)'s footing, imported from
  [`../2026-11-03-q139u-footing/reduce_footing.py`](../2026-11-03-q139u-footing/reduce_footing.py): `K_FROZEN` (0.2056 /
  0.3134 W/°C) and E82 A2's dip rule once. M7's 637 rows come from `rows-m7u.json`; E141's and E142's from
  `reduced/e141-footing.json` and `reduced/e142-footing.json`.
- **E147's single-bit steps** (aifoundry3, E134's frame: each item between reads of its own zero, no temperature term) enter
  from `scored.json` › `arms.dips_4w` (A2's 4 W line), each step multiplied by (1 − 0.2056 × 0.1186): the footing's leakage on a
  step whose die rise is M7's frozen 0.1186 °C per board W. The row is the step; its features are the item's minus its own
  zero's (`predictions-e147.json` › `items.<item>.zero`).
- **aifoundry2 (its own governor, bursts):** dips kept in training and test alike (Q139(u) F4: "remove A2's dips from training
  and test alike, or from neither"): E80's, E83's and E143's committed kspeed reductions as they are. So E160 is scored on
  the same footing: its registered kspeed reduction, dips kept.

## 2. Rows

M8's power rows: M7u's 637 + E141's 30 non-anchor pool-5 tiles (aifoundry3) + E142's same 30 (card 1) + E147's 70 steps
(68 new items and E134's two link items, aifoundry3). Pool 5's six anchors are left out as M5-M7 leave out anchors and
later sessions' `randn`/`full`. Pool-5 features are the frozen ones Q138(x) computed (`tools/claims-v3/kinds/blind5/
predictions-blind5-aifoundry3.json` › `tiles.<t>.features`, from `counts-blind5.json`). A kind is every row of one tile rule
on both cards (M7's rule); each E147 item is its own kind.

The other public experiments enter as follows, none as kinds rows: **E143** fits and scores aifoundry2's terms (§ 5); **E144**
scores Q138(t)'s heat-over-minutes chain, which M8 carries unchanged (one session per card, nothing to refit); **E145** gives
the int8 B per-position prices (§ 3, `bpos`); **E148** measures int8's no-issue floor, which every D subtracts through the
zeros, so it adds no D row.

## 3. Candidate features (all from the tile bytes, written before any is computed)

- `xfld` = `a_exp` + `b_exp` (M6's per-field flip counts, `fit_m6.flip_feats`): one exponent-field term (E147: the card pays
  0.82-0.84 of M6's and M7's watts on exponent flips).
- `c_end`, `c_start`: **the C-register candidate** (Q138(b)'s C2, `tools/claims-v3/kinds/blind5/CORRECTIONS.md` § C2): the
  C-register bit flips in one accumulate op, from pool 5's C emulation (`make_blind5.steps_of` / `run_op`, unchanged): `c_start`
  = the second op of a launch, from the first op's C; `c_end` = one op from C = N_END × the op's exact increment (N_END 2^19
  floats, 2^20 int8), the launch-end descriptor Q138(b) correlated (r 0.53). `c_end` is the registered candidate and
  `c_start` its named alternative; the nested procedure chooses between them with every other form.
- `bpos` (int8): B's bit flips (make_kinds' issue stream, consecutive micro-ops, as `b_odd`/`b_even`) weighted per bit position
  by card 0's frozen rail prices (`tools/claims-v3/e145/predictions-e145.json` › `card0_prices_rail_fJ.B`, positions 0-6; bit 7
  takes the mean of positions 1, 3 and 5), the weights divided by their mean. E145: these prices carry to card 1 to 7-20%.
- `bsat` (int8): B's bit flips in byte transitions where at least 7 of the byte's 8 bits flip (E141's whole-line flip-flops and
  the sign-swinging small values of power-law weights). `absat`: the same over A and B.

## 4. Forms, selection and bands

Floats (M7's `G8_gtr_glive` = M5's bench terms + `gtr` + `glive`, the base): `G8` (M7's form), `G11` (+ `a_exp`, `b_exp`,
M7's own candidate), `G12_xfld` (+ `xfld`), `G13_cend` (+ `c_end`), `G14_cstart` (+ `c_start`), `G15_xfld_cend` (+ `xfld`,
`c_end`). int8 (M7's `J8_b138` the base): `J8`, `J12_bpos` (BASE_I + `bpos`), `J13_bsat` (J8 + `bsat`), `J14_absat` (J8 +
`absat`), `J15_cend` (J8 + `c_end`), `J16_bpos_bsat` (BASE_I + `bpos` + `bsat`).

**Nested leave-one-kind-out exactly as M7** (`fit_m7.Fam`, its batched normal equations, the card term chosen first among
M7's C0 / C1 / C2 by leave-one-kind-out on the paired kinds, card-1 rows divided by it inside every fold): for each held-out
kind every M8 form is scored by leave-one-kind-out on the rest, the best refitted on the rest predicts the held-out kind.
**On the same folds**: M6's form (`G6_M6`, `J1_M6`) and M7's form refitted per fold, and M6 and M7 as frozen (no refit).
**Keep only terms that lower the error:** the frozen form is the plain leave-one-kind-out best, kept only if the procedure's
nested error is below M7's form's leave-one-kind-out error on the same folds; else M7's form is frozen (refitted on M8's rows).
Each added term is dropped in turn and reported. Gains are tested by a bootstrap over kinds (2,000 draws, seed 139).

**Band rule (M8's, frozen with it):** power half-width = k × √(pool² + s² xᵀCx), pool = M8's nested rms for the tile's
format and card, C the jackknife covariance by kind, s the card scale; **k = the larger of (i) the 95th percentile of |nested
residual| / pool over all M8 rows and (ii) the same over the rows of blind pools 3, 4 and 5 (E115, E140, E141, E142)**, which
the nested procedure holds out kind by kind. Coverage is also reported with each pool row left out of k's calculation.
Heat: M7's frozen law and band (dT = g_card × S, k_h × pool_h), with M8's D giving S. aifoundry2: § 5.

## 5. aifoundry2 under its own governor (bursts)

M7's relation, P(f) = B(f) + c × s(f) with E136's B and s, the burst clock from E83's dither at an effective cap W* ± 2.75 W
(E119's module), and c from a tile's D at 600 MHz on aifoundry3. Bursts: E80's and E83's kinds cells and E143's 36 cells. The
D used to fit each term is the cell's measured aifoundry3 D on the footing (E78's footing rows, E141's); the score is end to
end through M8's nested D. Three terms, added in this order, each kept only if it lowers the leave-one-kind-out rms of both the
burst clock and the burst board power over all bursts (else dropped and reported):
1. **the zeros level per format**: c_zeros[t] refitted on the zeros cells (E80/E83 zeros, E143 anchors' zeros);
2. **a D scale per format**: c = c_zeros[t] + g[t] × D600, g[t] by least squares of (c_w − c_zeros[t]) on D600 (M7: one 1/1.01865);
3. **a cap rising with overshoot**: W*(c) = W0 + γ × max(0, P800(c) − W0), W0 and γ fitted on the burst clocks.
**Peak board power** (the 82 W stop of section 22): predicted peak = P800(c) + q, q the 95th percentile of (the burst's highest
board sample − its predicted P800 from its measured c_w) over E143's 117 committed traces (E80's and E83's traces are not in the
tree). Bands: the 95th percentiles of |measured − predicted| end to end, leave one kind out, as M7.

## 6. The card-scale predictor (rank 5)

A card's scale s = D_card / D_aifoundry3 at 600 MHz on the same tiles. Measured: card 1 from every paired float kind with D ≥ 5 W
on the footing (median ratio; int8 apart); aifoundry2 from its bursts pinned at 795-800 MHz, D_800 / (D600_a3 × s(800)) with
aifoundry2's own s(800). Cheap reads per card: the voltage at 600 MHz (Q139(s) `clock-voltage.json` › `cross_card_v2_at_600`),
the idle board power, the zeros level per format, the leakage slope. Predictors: s = (read / read_a3)^β, with β (a) the
physical exponent, no fit (V: 2; idle, zeros level, slope: 1) and (b) fitted on the other two cards. **Leave one card out** over
aifoundry3, card 1 and aifoundry2: each held-out card's scale relative to the other two is predicted from the other two alone.
**Rule (the critic's): within 1% on each held-out card.** A predictor that fails is reported as failed; M8 keeps the measured
card-1 term for card 1 either way, and the predictor is quoted only for an unmeasured card.

## 7. Frozen outputs

`m8.json` (forms, constants, covariance, card term, pools, k, heat carried, aifoundry2's terms and bands, the card-scale
predictor's verdicts), `fit_m8.py`, the nested scores, and `predict_blind6.py <pool_dir> <card>` (card aifoundry3 |
aifoundry1c1 | aifoundry2; M8, and M7 and M6 through the same interface as frozen; for aifoundry2 the burst clock and the
predicted peak board power), with a self-test that reproduces M7's and M6's frozen pool-5 predictions.
