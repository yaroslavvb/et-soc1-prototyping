# Q142(m): M10's registration - five candidate terms, the rows each reads, the held-out refit, the entry rule for each term as numbers, and what is reported, written before any M10 fit output exists

*Wed 4 Nov 2026 (week 45), about 19:30-20:05 PST, on the Intel, desk only: no card, no device command, no card step on a lab box,
no post in the lab's channel, no Modal, no archive. It answers the card half's final critic's `next` **rank 2** (M10's registration, then its nested
refit, before any more card time on the power model), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** (a power model across
kinds), with items 8 and 9 (heat) for terms (c) and (d). The owner's goal, in his words of 2 November 2026: to predict the power
requirement and heat generation of numeric computations as accurately as possible.*

**Written and committed before any M10 fit output exists:** no `fit_m10.py`, no candidate term computed on any row, no held-out
error, no bench count beyond those already committed (§ 3.2 lists them). Everything below is fixed now. A departure is a dated
amendment file beside this one, written before the numbers it touches. [`SHA256SUMS`](SHA256SUMS) holds the sha256 of every
committed input this file names, as read at this commit; the refit checks them before it reads anything.

**This refit is held out, not blind.** Every candidate term below was named from misses already seen on pool 7 (E163, E164, E165,
E170) and the heat replicates (E166, E167). Its held-out errors are leave-one-kind-out (§ 5): no row is predicted by a fit that read
that row's kind, but the terms were chosen knowing where the misses were. **The blind test is pool 8, drawn by an independent
designer in a later round, after M10 is frozen and read by a critic.** This round makes no pool, and no prediction for any tile
that has not run.

## 0. What was already seen (disclosed, all post hoc)

The terms come from these readings. None is a registered result, and none is re-scored as one here.
- **The card-half critic's post hoc readings** (its desk checks, not committed): (i) scaling M9 as frozen by each 600 MHz
  session's own random float anchors (1.0082 of M9 on aifoundry3, 1.0095 on card 1; the median of measured D / M9's D over pool 7's
  random anchors) takes the float bias on pool 7's 48 priority-1 kinds from +0.151 / +0.164 W to +0.013 / +0.010 W and the 48-kind
  rms from 0.278 / 0.273 W to 0.259 / 0.245 W; the same with int8's anchors (1.0025, 0.9766) over-corrects int8 on card 1 (bias
  −0.076 → +0.061 W). (ii) E164-U1's FAIL is M6's float card term, 1.0099 times M9's on card 1 (0.9711 against 0.9616), absorbing
  that float excess; M9 × 1.0099 takes its 8 float unaimed tiles from 0.171 to 0.077 W rms. (iii) E170's leave-one-tile-out session
  scale per family (E170's README, reported) puts card 0's burst D at 0.425 W rms against 0.791 W as registered.
- **Single high bits (term b):** Q141(t)'s 27-point arm cut the S class's rms by 41% on card 1, 31% on aifoundry3, 36% pooled
  (E164's README, reported); Q141(t2)'s 243-point readings G4/G5 (pool 6's `fp32.b_onebit_b20_third`, M9's in-sample error −0.718 /
  −0.996 W → +0.331 / +0.013 W at 243 points); the calibration tiles' e(N) in
  [`../../../docs/reports/data/2026-11-04-q141t-s7-recount/step243/recount-rule.txt`](../../../docs/reports/data/2026-11-04-q141t-s7-recount/step243/recount-rule.txt);
  E165's class S, 57% of the pinned board's squared error (post hoc, `7830a9cb`); E170's class S +0.72 W mean at 800 MHz.
- **Heat (terms c, d):** E164's die rose 0.131 °C per board W over its 4.5 s runs against the 0.1151 carried, E163's 0.1237 against
  0.1186 (`scored.json` › `reported_rise_per_board_w`, reported); E170's burst rise 0.24 °C/W against the burst law's 0.1400
  (E170's posthoc readings); RK3-c given the watts: E166's large rises 1.83 / 2.15 / 3.23% low, E167's G1Q 5.42% low, E154's
  3.1-4.6% low (registered readings, each a FAIL of RK3-c).
- **Card 0's footing (term e):** E170-X0 reads 0.9766 as registered (board less the pass's zeros anchor) and 0.9312 referred to each
  tile's own die start (post hoc, E170's `posthoc/readings_e170.txt` § 5), against κ0 = 0.9463.
- **E163's float excess:** post hoc, a level or a gain in D, not separated (floats −0.100 ± 0.118 W + 1.09 ± 0.59% of D; `3b102b85`).
- **What this lane read before writing:** the committed per-tile rows of E163, E164 (power, heat, pool anchors), E170 (tiles, cells,
  anchors), E165's notes, E166/E167/E154/E161/E144's per-hold readings, the critic's three post hoc outputs, M9's registration,
  README and fit code, Q139(u)'s footing rule, the recount rule and Q141(t)/(t2)'s counts; and it listed each footing session's
  random-anchor D values (fp32.randn, fp16.randn, int8.full) without setting them against any model.

## 1. The footing, the sessions, the families

- **Footing:** Q139(u)'s, unchanged: `reduce_footing.K_FROZEN` (0.2056 W/°C aifoundry3, 0.3134 W/°C card 1) and E82 A2's dip
  rule once. Every row and anchor below is read from a reduction on that footing.
- **A session** σ is one experiment on one card: a row's `exp` with its `card` (31 sessions: M9's 29 and E163, E164).
- **Families:** floats (fp32 and fp16 fitted together) and int8, as M5-M9.

## 2. Rows

**Power at 600 MHz (terms a, b):**
- **M9's 855 rows exactly as committed** (`docs/reports/data/2026-11-04-q140m-m9/rows-m9.json`: D, card, kind, rate and every
  feature unchanged; 681 float, 174 int8);
- **plus pool 7's 52 new kinds on both 600 MHz cards** (104 rows: 19 fp32, 9 fp16, 24 int8 tiles; 48 priority 1, 4 priority 2):
  E163's registered primary reduction on aifoundry3 (`docs/reports/data/2026-11-04-e163-blind7-aifoundry3/e163.json` ›
  `items.<tile>.D.mean`, `rate.mean`) and E164's on card 1 (`…/2026-11-04-e164-blind7-card1/e164.json`), both on the footing.
  Features: the frozen ones Q140(x) computed with M9's code on the bench's three-point counts
  (`tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry3.json` › `tiles.<t>.features`). Each pool-7 tile is its own kind on
  both cards, labelled `<type>.blind7:<name>`.
- **Left out, as M5-M9 leave them out:** pool 7's nine anchors (they enter term a only), E78's anchors and zeros re-run in E163 and
  E164, E163's K14 re-runs and E164's K7 repeats of earlier kinds, and E151's block. 959 rows if every tile has a D (each has one
  on both cards at this commit).

**Heat over a 4.5 s run (term c1):** M7's heat rows exactly as `fit_m7.heat_rows` assembles them (M6's rule: a row is a kinds item
with a window rise `dT_win` and a switching-plus-zeros power `S` in its session's reduction, and a median run length of at most
5.0 s from `runs.csv`), with the same rule applied to E141, E142, E153, E157, E163 and E164; kinds as the power rows' kinds
(anchors and items outside the power rows keep their key as the kind, as M6's rule does).

**Card 0's bursts (terms c2, e):** E170's 39 scored tiles (`docs/reports/data/2026-11-04-e170-blind7-card0/results.json` ›
`score.reported.tiles`, `cells`): per tile the measured burst board `burst_w`, the burst die rise `rise_c`, the die starts, and
the primary's `zeros_level_w` (the session's zeros level at the tile's own die start) and `a2_burst_D_w` (M9's D carried to the
800 MHz cap by M9's aifoundry2 part, as frozen).

**Heat over minutes (term d):** every committed long hold scored with arm A, Q138(t)'s frozen chain on the hold's measured board
power. Per hold: R, the measured plateau rise over the hold's anchor or rest, and e, arm A's plateau error (measured − the chain), as
each run's scorer committed them; the chain's rise is P = R − e.

| run | card kind | file (under `docs/reports/data/`) | e | R |
|---|---|---|---|---|
| E144 | aifoundry3 | `2026-11-02-e144-heat-minutes/scored.json` | `holds[].a.plateau_err_C` | `holds[].b.measured.plateau_rise_C` |
| E144b | aifoundry2 | `2026-11-02-e144-heat-minutes-aifoundry2/results.json` | `score.holds[].a.plateau_err_C` | `score.holds[].b.plateau_rise_C` |
| E154 | aifoundry3 | `2026-11-03-e154-heat-e2e-aifoundry3/scored.json` | `holds.<h>.A_given_watts.plateau_err_C` | `holds.<h>.measured.plateau_rise_C` |
| E161 | aifoundry2 | `2026-11-03-e161-heat-e2e-aifoundry2/results.json` | `holds.<h>.A_given_watts.plateau_err_C` | `holds.<h>.E_end_to_end.plateau_rise_measured_C` |
| E166 | aifoundry3 | `2026-11-04-e166-heat-replicate-aifoundry3/scored.json` | `readings.<h>.A_plateau_err_C` | `readings.<h>.measured_rise_C` |
| E167 | aifoundry2 | `2026-11-04-e167-heat-replicate-aifoundry2/scored.json` | `holds.<h>.A_plateau_err_C` | `holds.<h>.measured_rise_C` |

**Left out of the fit and reported:** the aifoundry2 holds in the governor's trip regime (E144b's G2, E161's and E167's G2Q), whose
plateau the trip sets, not the chain; and E166's `K_OL_long`, a second window of the hold `K_O_window` reads (one reading per hold).
E161's holds are read from E161's own results, not the copy carried in E167's.

## 3. The candidate terms (each written before it is computed on any row)

### (a) A scale per session and per family, read from the session's own random anchors

- **The anchors** A(σ): the items of σ's own footing reduction named exactly `fp32.randn`, `fp16.randn`, `int8.full` (E78's random
  tiles, which every footing session ran), `fp32.anchor6_randn`, `fp16.anchor6_randn`, `int8.anchor6_full` (pool 6's, where σ ran
  them), and `fp32.anchor7_randn_a`, `…_b`, `fp16.anchor7_randn_a`, `…_b`, `int8.anchor7_full_a`, `…_b` (pool 7's, where σ ran them),
  each with a D. Measured D_σ(a) and rate: `docs/reports/data/2026-11-03-q139u-footing/reduced/<exp>-footing.json` for E78-E142,
  and `e153.json`, `e157.json`, `e163.json`, `e164.json` for the pool sessions. **E147 has no random anchor: its scale is 1.**
- **The anchors' features:** E78's three from their E78 rows in `rows-m9.json`; pool 6's from Q139(x)'s frozen features
  (`tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json` › `tiles.<t>.features`) completed with M9's terms by
  `fit_m9.m9_extra` on the tile's row of `blind6/counts-blind6.json` (the chain `predict_blind7.py` runs); pool 7's from
  `predictions-blind7-aifoundry3.json` › `tiles.<t>.features`.
- **The scale:** s(σ, φ) = the median, over σ's anchors of family φ (floats: its fp32 and fp16 anchors together; int8: its int8
  anchors), of D_σ(a) / D̂_σ(a), where D̂_σ(a) = the anchor's rate × Σ price × feature at the fold's pass-1 prices, times the fold's
  card term when σ is on card 1. A session with no anchor of φ left in the fold takes s = 1.
- **Without the held-out kind:** in the fold that holds out kind k, no anchor whose tile is of kind k is read in any session. Only
  `fp32.randn`, `fp16.randn` and `int8.full` are both anchors and rows (in E78, E82 and E94); pool 6's and pool 7's anchors are never
  rows, so never held out.
- **Two passes in every fold:** pass 1 fits the prices with every s = 1 and reads the card term (M9's C0: E78's and E82's same
  tiles, its value refitted without the held-out kind, as `fit_m7.Fam` does); s(σ, φ) is read from pass 1's prices; pass 2 refits
  the prices with each row's D divided by its session's s (and card-1 rows by pass 1's card term, which pass 2 keeps unchanged); the
  held-out kind's rows are predicted as s(σ, φ) × card term × rate × Σ price × feature at pass 2's prices. Without term a, pass 1 alone
  is the fit (M9's form refitted).

### (b) The single-high-bit counts at 27 / 81 / 243 points

- **The S class:** the tiles pool 6's and pool 7's manifests label case S: pool 6's `fp32.b_onebit_b12_third`,
  `fp32.b_onebit_b20_third`, `fp32.a_onebit_b5_third`, `fp32.a_onebit_b16_half`, `fp16.b_onebit_b6_third`; pool 7's
  `fp32.b_onebit_b20_one`, `…_b20_full`, `…_b20_pi`, `…_b20_seventh`, `…_b22_third`, `fp16.b_onebit_b9_one`, `fp16.b_onebit_b8_pi`,
  `fp32.b_onebit_b20_third_a1p5`: 13 tiles, 26 rows. E147's single-bit steps keep their three-point counts in this round (their 70
  tiles are not recounted: about 8.8 bench-hours at 243 points), and so does every other row.
- **N per tile, by the convergence rule** (`docs/reports/data/2026-11-04-q140m-m9/recount-rule/RECOUNT-RULE.md` §§ 1-4, `b4444dd4`;
  `recount_rule.py`'s estimator e(N) at M9's frozen float prices, bound 0.10 W): from the most points already counted, a tile is
  counted at 3N while e(N) > 0.10 W, up to N = 243; a tile above the bound at 243 is carried at 243 with its e(243) stated.
- **Counts already committed and used as they are:** pool 7's eight at 27 points (`…/2026-11-04-q141t-s7-recount/counts-s7-27.json`);
  the byte twins `fp32.cal_third_b12` (pool 6's `b12_third`, met at 27), `fp32.cal_third_b20` (pool 6's `b20_third`, met at 243) and
  `fp32.cal_pi_b20` (pool 7's `b20_pi`, met at 243), from `…/q140m-m9/bench-check/counts-cal.json`,
  `…/recount-rule/counts-pilot27.json`, `…/q141t-s7-recount/step81/counts-cal81-*.json` and `…/step243/counts-cal243-*.json`
  (a twin's bytes are checked equal to the pool tile's before its counts are used). **To count now:** pool 7's other seven from 27
  points, and pool 6's `a_onebit_b5_third`, `a_onebit_b16_half` and `fp16.b_onebit_b6_third` from 3 points.
- **The bench:** the mini's build of `rtl-sim/fma_toggle_v2` that Q141(t2) recorded (`…/step243/build-record-mini.json`: Verilator
  5.052, `-fno-dfg`, its inputs as `…/bench-check/bench-sha256.txt`); its three binaries are hashed against that record before any
  count. At most 4 jobs. **One new point is counted on both the mini's build and the Intel's hashed build and must agree in every
  field before any mini count is used**, as Q141(t2)'s B3 did. C is checked against software at every point (`check_mismatch` 0,
  else stop). The driver is a new file committed before its first count.
- **How the counts enter:** a tile's N-point counts row is run_kinds.py's `mean_rows` over its N points (its `points` the bench's
  three standard ones, as Q141(t)'s arm built it), and every feature M9's code derives from a counts row is recomputed from it
  through the chain `predict_blind7.py` runs (`fit_m7.feats_from_counts`, `fit_m8.m8_extra`, `fit_m8.finish`, `fit_m9.m9_extra`),
  unchanged; byte-derived features do not change. With term b, the S rows carry those features in every fold.

### (c) The 4.5 s rise per board W, per card (and per session)

- **(c1) at 600 MHz:** the base is M7's form `H2_per_card_runlength` (dT = g_card S + h_card S (T_run − 4.5)) refitted leave one kind
  out on § 2's heat rows. **The candidate:** a heat scale per session, h(σ) = the median over σ's random anchors (§ 3a's set, both
  families together) of the anchor's measured `dT_win` / the fold's law at its measured S and run length; the held-out kind's rows
  are predicted as h(σ) × the law. The anchor kinds are left out of every session's h in their own fold, as in (a). Given the
  measured S (a test of the heat term alone); the end-to-end figure, with the fold's predicted D, is reported beside.
- **(c2) card 0's 6 s bursts:** the base is the frozen burst law, die rise = k (P_board − 21.5 W) with k = 0.14004 °C/W (M9's
  aifoundry2 part, `m9_a2.json` › `burst_heat`). **The candidate:** k for card 0 fitted leave one tile out on E170 (least squares
  through the knee over the other 38 tiles, at their measured boards), the held-out tile predicted at its measured board.

### (d) The heat chain's gain on large rises

The chain's rise times (1 + γ): a held-out hold's predicted rise is (1 + γ) P, its error e − γ P. **Two variants:** one γ for both
card kinds, and one γ per card kind (aifoundry3; aifoundry2). γ = Σ e P / Σ P² over the fitted holds (§ 2) of the **other sessions**
(leave one session out: the holds of one session share its room and its board).

### (e) κ0's die-start footing (card 0)

Card 0's burst board = the session's zeros level at the tile's die start + κ × M9's carried burst D (E170's primary, unchanged but
for κ). The base is κ0 = 0.9463 as frozen. **The candidate:** κ per family read on the die-start-referred footing, leave one tile
out: the median over E170's other tiles of the family with `a2_burst_D_w` > 1 W of (burst_w − zeros_level_w) / a2_burst_D_w. M10's
own D is not carried to card 0 in this round (M9's aifoundry2 part would have to run on it); that is named as remaining.

## 4. Which form, and the card term

- **The forms stay M9's frozen ones:** floats `G8+c_end+xstage`, int8 `J8+bsat+bpp_r4` (`m9.json`), with M9's card term C0 (family
  fixed, value refitted in every fold). No other feature is a candidate here; M9's feature selection is not re-run.
- **The variants scored on the same folds:** B (M9's form refitted on the 959 rows: pass 1 alone), B+a, B+b, B+a+b (floats), and B,
  B+a (int8). Also on the same rows: **M9 as frozen** (`m9.json`, no refit: in sample on M9's 855 rows, blind on pool 7's 104).
- **Fitting:** as `fit_m7.Fam`: per-kind normal equations on column-scaled features, a 1e-9 relative ridge, D = rate × Σ price ×
  feature, card-1 rows divided by the card term.
- **Self-test before any candidate runs:** B's machinery on M9's own 855 rows must reproduce `nested-m9.json`'s leave-one-kind-out
  errors of M9's frozen form (`M9_frozen_form_loko`) within 1e-6 W on every row, else the refit stops.

## 5. The held-out procedure

- **Leave one kind out** over every kind of the family (floats 398 kinds: M9's 370 and pool 7's 28; int8 107: 83 and 24). A held-out kind is all its rows on
  both cards. Inside each fold everything fitted is re-derived without that kind: the prices, the card term, every session's
  scale (a) and heat scale (c1).
- **There is no inner choice of form:** each variant's structure is fixed, so its leave-one-kind-out errors are its held-out errors.
  The entry decision (§ 6) reads those same errors once, so the frozen M10's held-out figures keep that selection's optimism (at most
  four variants per family). That is one more reason pool 8 is the test.
- **Paired bootstrap:** over kinds (for c2 and e, over tiles; for d, over holds), 2,000 draws, seed 142, the rms of one variant minus
  the other on the same rows, 95% interval; "resolved" when it excludes 0.

## 6. The entry rules, as numbers (each term against the base on the same folds)

| term | it enters if ALL of these hold | rows it is judged on |
|---|---|---|
| (a) floats | held-out rms(B+a) − rms(B) ≤ −0.005 W pooled, with the 95% interval below 0; and the difference < 0 on each 600 MHz card's rows | every float row (both cards) |
| (a) int8 | the same, on the int8 rows | every int8 row |
| (b) | held-out rms(B+b) − rms(B) ≤ −0.050 W on the 26 S rows, with the 95% interval (over the 13 S kinds) below 0; the difference < 0 on each card's 13 S rows; and the pooled float rms does not rise by more than 0.001 W | the S class; every float row |
| (c1) | held-out heat rms with the session heat scale − without ≤ −0.010 °C pooled, the 95% interval below 0, and < 0 on each card | every heat row |
| (c2) | the leave-one-tile-out burst rise rms − the frozen law's ≤ −0.25 °C, the 95% interval below 0 | E170's 39 tiles |
| (d) | on the large-rise holds (R ≥ 10 °C, fitted set), held-out plateau-error rms with γ − without ≤ −0.10 °C, the 95% interval below 0, and < 0 on each card kind's large-rise holds; if both variants pass, the one with the lower held-out rms is frozen (a tie keeps the common γ) | the large-rise holds; every fitted hold reported |
| (e) | E170's board rms with the leave-one-tile-out κ − with κ0 ≤ −0.05 W, the 95% interval below 0 | E170's 39 tiles |

**M10's frozen form holds every term that enters**, refitted on all rows; its own held-out figures (the variant holding exactly those
terms) are reported. A term that does not enter is reported with its numbers, never dropped from the record.

## 7. What would show a term is not wanted (beyond failing its rule)

- **(a):** the sessions' scales agree within their own noise (the spread of s over a card's sessions no larger than the spread the
  anchors' measurement errors give); or pool 7's held-out bias does not move toward 0 on both cards; or a family's scale
  over-corrects (its bias changes sign on a card and grows in size), as int8's did post hoc on card 1.
- **(b):** the S rows' held-out errors move the wrong way on either card; or for most S tiles the three-point count's error
  (3pt − N) lies within ±e(N), so counting is not what misses.
- **(c1):** the session heat scales agree within the window rise's resolution; or the gain is not resolved. **(c2):** the fitted
  card-0 coefficients' leave-one-tile-out spread includes 0.14004.
- **(d):** γ's sign differs between the card kinds; or a held-out session's large rises read worse with γ.
- **(e):** the leave-one-tile-out κ values straddle κ0 within their spread; or the board error is not resolved.

## 8. What is reported (no verdict on M9 or on any earlier run)

- **Power:** held-out rms and bias (measured − predicted, W of D) of every variant and of the frozen M10, per card (aifoundry3, card
  1), per family and per format (fp32, fp16, int8), on (i) all rows, (ii) pool 7's rows (its 48 priority-1 kinds and all 52), (iii)
  the S class, (iv) M9's 855 rows; **M9 beside on the same rows** as frozen (in sample on M9's rows, blind on pool 7's) and as its form
  refitted (B). The paired bootstrap for every comparison of § 6, and M10 − M9-as-frozen on pool 7's rows (where M9 is blind and M10
  held out; a reading, not a test). The sessions' scales s(σ, φ) with their anchors. The S tiles' e(N), N and 3pt − N.
- **Heat:** (c1) held-out heat rms and bias per card and format with M7's law as frozen and B's refit beside, the refitted per-card
  coefficients beside M7's 0.1186 / 0.1151, the session heat scales; (c2) the leave-one-tile-out rms and k against 0.14004; (d) γ per
  variant, the held-out plateau errors per hold and session against arm A's; (e) the κ values and E170's board rms against κ0's.
- **Bands:** M9's rule (half-width k √(pool² + s² xᵀCx)), pools = M10's held-out rms per format and card, k = the larger of the 95th
  percentile of |held-out residual| / pool over all rows and over the rows of blind pools 3-7 (E115, E140-E142, E153, E157, E163,
  E164). A calibration on held-out rows, not a test.
- **The frozen form:** `m10.json` (prices, covariance, card term, the entered terms' rules and constants, the bands), the fit code
  and a hash list over code and parameters, in `docs/reports/data/2026-11-04-q142m-m10/`. The prediction code takes a tile's
  features (and, for term a, its session's anchors' measured D) and is self-tested on committed rows only.

## 9. What does not change

M9 (`1f244140`, `8dfafae3`), its aifoundry2 part, every earlier frozen file and every registered verdict stay as committed. After
this lane the four hash lists must still pass: `tools/claims-v3/kinds/blind7/SHA256SUMS` (91),
`docs/reports/data/2026-11-04-q140q-gemm-g4-stride/frozen-sha256-e168.json` (9) and `frozen-sha256-e168-scorer.txt` (18), and
`predict_q140e.py`'s 26 frozen inputs (read by parsing, never by importing it).

## 10. Compute

Bench counts on the mini (at most 4 jobs, each call capped in memory and time); the Python fits on a lab host, capped likewise; local
work on the Intel only for git, checks under a minute and one bench point on one core.
