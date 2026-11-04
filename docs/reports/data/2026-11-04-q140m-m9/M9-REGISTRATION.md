# Q140(m): M9's registration - rows, candidate features, folds, the selection rule, bands, the bench check at four base words, and what is scored, written before any M9 fit or prediction

*Wed 4 Nov 2026 (week 45), about 00:45 PST, on the Intel, desk only. Written and committed before `fit_m9.py` exists, before any
candidate feature below is computed on any row, before any fit, and before the bench check of § 8 runs. It answers the Q139 final
critic's open **rank 1** (M9: a power model more accurate than M6 on new kinds at 600 MHz, from pool 6's named misses), for the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** (a power
model across kinds; items 15, 12 and 7 feed its terms). Blind pool 7 is being written by an independent designer at the same time;
this lane never reads that designer's scratch, and pool 7 is not in the tree. Everything below is fixed now; a departure is a dated
amendment written before the numbers it touches.*

**Read before writing this** (all committed, plus the critic's own scratch): the Q139 final critic's result (rank 1, the six named-miss
tiles, the bound of 0.17-0.19 W without them); Q139(m)'s M8 (registration, README, `fit_m8.py`, `predict_blind6.py`, `m8.json`'s
structure); Q138(m)'s `fit_m7.py`, Q137(m)'s `fit_m6.py` and `m6_rows.py`, Q133(b)'s `fit_m5.py`; Q139(u)'s footing rule; pool 6's
README and predictions note; E153's and E157's READMEs and their `power_rows` (measured D, M8/M7/M6 errors per tile); E147's README
(single-bit steps); `make_kinds.py`'s issue streams; core-et's `tima_top.v` (int8's multiply is written `$signed(a)*$signed(b)`, so the
bench sees the product, not a partial-product array); and the bench's committed per-point stage counts of pool 6's S tiles and of five
E147 tiles. **Not done before this commit:** no candidate feature computed on any row, no regression of anything on board watts, no
nested or plain fit. One bench point-run was timed on pool 6's fp32 zeros anchor (19 s), which carries no information about § 8.

## 1. Footing and rows

- **Footing:** Q139(u)'s, unchanged: `reduce_footing.K_FROZEN` (0.2056 W/°C aifoundry3, 0.3134 W/°C card 1) and E82 A2's dip rule
  once. M8's rows carry it already.
- **Rows:** M8's 767 rows exactly as committed (`../2026-11-03-q139m-model/rows-m8.json`: D, card, kind and every M8 feature
  unchanged) **plus pool 6's 44 new kinds on both 600 MHz cards**: E153's registered primary reduction on aifoundry3
  (`../2026-11-03-e153-blind6-aifoundry3/e153.json` › `items.<tile>.D.mean`) and E157's on aifoundry1 card 1
  (`../2026-11-03-e157-blind6-card1/e157.json`), both on the footing (frozen slope, A2 once). Their corrections changed no measured
  number. 855 rows if every tile has a D.
- **Left out, as M5-M8 leave them out:** pool 6's six anchors (`*.anchor6_*`), E78's anchors and zeros re-run in those sessions, and
  the six pool-5 tiles E153 and E157 re-ran as K1 (they repeat pool-5 kinds already in M8's rows; they were a check).
- **Kinds:** each pool-6 tile is its own kind on both cards (no pool-6 tile shares bytes with an earlier tile), labelled
  `<type>.blind6:<name>`; every other row keeps M8's kind. A held-out kind is all its rows on both cards.
- **Pool 6's M8 features** are the frozen ones Q139(x) computed (`tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json` ›
  `tiles.<t>.features`); its bench counts are `counts-blind6.json`.

## 2. Candidate features (each from the tile bytes or the committed bench counts; registered before any is computed)

**Floats (fp32 and fp16 fitted together, as M5-M8).** The base is M7's `G8_gtr_glive` (M5's bench terms `mult`, `add32`, `add16`,
`bus`, `rest`, `clk`, plus `gtr` and `glive`).

1. `c_end`: M8's C-register term (its launch-end descriptor), a candidate again.
2. `xfld32` (**the exponent-field term for fp32, from the bytes**): `a_exp + b_exp` (M6's per-field flip counts) on fp32 rows, 0 on
   fp16 rows.
3. `xstage32` (**the exponent-field term for fp32, from the bench**): the bench's exponent-stage count per op (`vpu.by_stage.exponent`,
   the mean of the tile's three launch points, minus fp32 zeros'), on fp32 rows, 0 on fp16. Today that count is priced inside `rest`;
   this prices the exponent datapath apart. Its alternative **`xstage`**: the same on both float formats (fp16's minus fp16 zeros').
   A form holds at most one of the two.
4. `lq1` (**the base-word term for single bits, from the bench's per-point counts**): the bench's whole-VPU `nets_map` at the first
   launch point (n at 1/6 of a 0.5 s launch) minus the mean of the other two (1/2 and 5/6), the tile's minus its type's zeros'.
   *Why:* a single bit's cost depends on where the accumulator's rounding position sits relative to the flipping bit. That position
   moves as C grows over a launch, at a rate set by the base word, so a base word decides how much of the launch a single bit spends
   in its dear regime. The bench averages a launch as three equal thirds; a regime that fills less than the first third is
   over-weighted, and one that fills more than the last third is under-weighted. Seen in the committed counts before this was
   written: `fp32.b_onebit_b20_third` (every model 0.8-1.1 W high) counts 3.53 M nets at the first point against 2.21 M and
   2.09 M; E147's `aj_19` (read 0.5-0.6 W high in M8) 2.17 M against 1.27 M and 1.24 M; E147's `bj_21` (the card's swing 9%
   above the bench's) 2.05 M, 1.90 M, then 2.50 M at the last point. The term is identified on single-bit rows at **more than three
   base words**: E147's two A words (W79 `0x3FBD207C`, which E102's card-1 rows also use, and W67 `0x3FBBC9E4`) and E79's eight B
   words, and pool 6's 1/3 and 0.5. E147's rows are steps, so their `lq1` is the item's minus its own zero's, as every E147 feature
   is.

**int8.** The base is M7's `J8_b138` (`nets_nobus`, `bus`, `clk`, `b138`).

5. **M8's near-whole-byte discount, kept, bounded or dropped:** `bsat` (M8's feature, refitted with its sign free: kept);
   `bsat_cap` = min(`bsat`, 1,024) bits an op (bounded: one eighth of the 8,192 a whole-line flip-flop reaches, so a tile can take no
   more discount than the W8A8 and power-law tiles it was learned on, whose `bsat` E153 read at 1,064 or less); or neither (dropped).
   A form holds at most one of the two.
6. `bpp_r4` (**the held-B term, structural**): the radix-4 Booth partial-product bits that flip per op with **B recoded** (E151's
   registered verdict), from the tile bytes. For each of the 16 column slots j and byte lanes e (64 multipliers) over the 256
   micro-ops of `make_kinds`' int8 stream (A byte e of `Aword[i][p]` broadcast, B byte e of `Bword[p][j]` held over a k-group): the
   operands a multiplier sees are its F2 registers, which load only on a valid micro-op (`tima_top.v` `EN_FF(..., f1_mul_en, ...)`;
   `make_kinds.gate_mask`, gate bit j mod 8), and hold otherwise; a = the 9-bit signed A byte, digits d_m = -2 b(2m+1) + b(2m) +
   b(2m-1) (m = 0..3, b(-1) = 0) of the signed B byte; row m's partial product is the 10-bit (|d| = 2 ? 2a : |d| = 1 ? a : 0),
   inverted when d < 0, with its negate bit (11 bits; 0 when d = 0). `bpp_r4` = the bits of all four rows of all 64 multipliers that
   differ between consecutive micro-ops, cyclic over the op (the convention of every flip feature here). *Why:* int8's multiply is
   behavioural in the RTL, so the bench never sees the array a synthesised multiplier has; a held B with one bit set drives one or
   two rows where random B drives three on average, and 0x55/0xAA lines drive all four.
7. `bnz_a` (**the held-B term, simplest**): the A-byte bits that flip between consecutive valid micro-ops, each weighted by the number
   of non-zero radix-4 digits of the B byte it meets (0 to 4), summed over the 64 multipliers, cyclic.

## 3. Forms

- **Floats, 24 forms:** `G8_gtr_glive` plus every combination of {`c_end`} × {`xfld32`} × {none, `xstage32`, `xstage`} × {`lq1`}.
  `G8_gtr_glive` is M7's form; `G8_gtr_glive` + `c_end` is M8's (`G13_cend`).
- **int8, 12 forms:** `J8_b138` plus every combination of {none, `bsat`, `bsat_cap`} × {`bpp_r4`} × {`bnz_a`}. `J8_b138` is M7's form;
  `J8_b138` + `bsat` is M8's (`J13_bsat`).
- Fitting as M7 and M8: `fit_m7.Fam` (per-kind normal equations, batched, 1e-9 relative ridge on column-scaled features), D =
  rate × Σ price × feature, card-1 rows divided by the card term inside every fold.
- **The card term is M8's, kept:** C0 (E78's and E82's same tiles), its family fixed, not chosen again (so the selection never
  sees a held-out kind through it); its value refitted without the held-out kind in every fold, as `fit_m7.Fam` does.

## 4. Folds, and the models scored on them

Leave one kind out over every kind of the family (floats: M8's 343 kinds plus pool 6's float kinds; int8: M8's 66 plus pool 6's
int8 kinds). **On the same folds:** M9's nested procedure (§ 5); M8's, M7's and M6's forms refitted per fold (plain leave-one-kind-
out); and M8, M7 and M6 as frozen (no refit: in sample on most of M8's rows, **blind on pool 6's**). M5's form is reported beside.

## 5. The selection rule: a feature stays only if it lowers the nested error

1. **Nested procedure P(Φ)** over a set of forms Φ: for each held-out kind, every form in Φ is scored by plain leave-one-kind-out on
   the remaining kinds; the best is refitted on them and predicts the held-out kind. nested(Φ) = the rms of those outer errors over
   all the family's rows.
2. **M9's nested error** (its out-of-kind score, the "after") is nested(Φ) with Φ = all the family's registered forms (§ 3).
3. **A candidate feature q stays only if it lowers the nested error:** nested(Φ) < nested(Φ without the forms that hold q). For
   `bsat` and `bsat_cap`, and for `xstage32` and `xstage`, each is tested alone, the other left in Φ. Q = the features that stay.
4. **The frozen form** = the form with the lowest plain leave-one-kind-out rms on all rows among the forms whose added features all
   lie in Q (the base form if Q is empty). Each feature of it is dropped in turn and the plain leave-one-kind-out rms reported.
5. **Bootstrap:** paired over kinds, 2,000 draws, seed 140: M9's nested error minus each other model's on the same rows, on (a) all
   rows, (b) pool 6's rows, (c) pool 6's rows without the six named-miss tiles (§ 6), with 95% intervals; "resolved" when the interval
   excludes 0.

## 6. What is scored (reported per format, fp32 / fp16 / int8, and per card, aifoundry3 / card 1; no verdict here)

For every model of § 4: the rms and bias (measured − predicted) on (a) all rows; (b) pool 6's rows, all 44 kinds and the 30
priority-1 kinds; (c) the same without the critic's **six named-miss tiles**: `fp32.b_onebit_b20_third`, `int8.a_zeros_b_lineflip`,
`int8.b_line_zero_ff`, `int8.bheld_bit1`, `int8.bheld_bit4`, `int8.bheld_bit7`; (d) M8's rows (outside pool 6); and by experiment.
**The check before anything is read:** M8, M7 and M6 as frozen, on pool 6's rows, must reproduce E153's and E157's registered errors
(`power_rows`) within 0.002 W, else the run stops. Pool 6's rows are out of kind for M9, not blind: its features were named from
pool 6's misses. Pool 7 is the blind test.

## 7. Bands, heat, aifoundry2

- **Power band (M8's rule, pools 3-6):** half-width = k × √(pool² + s² xᵀCx); pool = M9's nested rms for the tile's format and card
  (§ 5.2's outer errors); C = the frozen form's jackknife covariance by kind; s = the card scale; **k = the larger of the 95th
  percentile of |nested residual| / pool over all M9 rows and the same over the rows of blind pools 3, 4, 5 and 6 (E115, E140, E141,
  E142, E153, E157)**. Coverage reported on all rows, on the pool rows, and with each pool row left out of k.
- **Heat:** M7's frozen law and band carried unchanged, as M8 did (die rise over the 4.5 s run = g_card × S, S = D + the card's
  zeros' S).
- **aifoundry2: nothing is fitted here.** `predict_blind7.py` hands M9's D at 600 MHz (aifoundry3's footing, with its band) to
  (a) M8's frozen aifoundry2 relation and peak rule (`m8.json` › `aifoundry2`) by default, or (b) Q140(l)'s part with
  `--a2-terms <m9_a2.json>` (and its session reads with `--a2-session <json>`), as Q140(x) applies it. The interface is in the
  README; whatever Q140(l) freezes, M9's D is the input.

## 8. The bench check at four base words (bench only; reported; it never changes M9)

16 fp32 tiles, A every element 1.0, B every word w with bit k flipped in columns 8-15 (pool 6's single-bit design), for w in {1/3
`0x3EAAAAAB`, E79's and E102's word `0x3FBD207C`, E67's `0x3FBBC9E4`, π `0x40490FDB`} and k in {12, 17, 20, 21}, counted by the
same bench build (Q133(b)'s, the seven files Q139(x) hashed) at the nine midpoints of ninths of a 0.5 s launch, which include the
bench's three points. Per tile: m3 (the three points' mean whole-VPU nets), m9 (the nine's) and `lq1`; α = Σ (m3 − m9) lq1 / Σ lq1².
**Expected: α > 0** (the three-point average over-counts when the first point is high). If M9 keeps `lq1`, its fitted price is set
beside the bench's own −α × the frozen form's mean price per VPU net on the 16 tiles, as a ratio, to say whether the term reads as
the launch average or only as a fitted correction.

## 9. Frozen outputs

`m9.json` (forms, kept features, constants, covariance, card term, pools, k, heat carried, the aifoundry2 default, the band rule),
`fit_m9.py`, `nested-m9.json` (every model's errors on the same folds), `rows-m9.json`, `predict_blind7.py <pool_dir> <card>` (card
aifoundry3 | aifoundry1c1 | aifoundry2; M9, and M8, M7 and M6 as frozen through the same interface; for aifoundry2 `--a2-terms`),
and a self-test: M8, M7 and M6 through `predict_blind7.py` reproduce Q139(x)'s committed pool-6 predictions field for field on all
three cards.
