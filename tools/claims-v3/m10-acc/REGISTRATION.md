# Q153(m10acc): M10's per-tile accumulator-toggle term - the accumulator register's toggles per micro-op over the launch, from the exact C trace at each kit's launch size, plus, for floats, A's non-zero Booth rows beyond A = 1.0's times B's toggled significand bits; fitted leave one run out on committed rows (the kinds pools E78-E172, the single-bit lists, E178's 40 kinds), with its uncertainty and the rule by which it enters M10 for the next blind pool; it replaces the failed term S (registration, written before any fit output)

*Sat 7 Nov 2026 (week 45), written about 10:55-11:25 PST on the Intel, desk only (no card, no lab box, no device command, no
Discord, no Modal), by the lane m10acc of Q153, the round of follow-up registrations. It serves the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (a power model across
kinds), and it is the term Q145(b)'s README names as next: "a lane-uniform (one-word) term, registered first and tested on data
with one word in every lane". The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat
generation of numeric computations as accurately as possible; and of 5 November: "I want to build up on previous things as much as
possible before building new stuff." Numbers: Q153 is this round; E182 (the one-number TensorFMA's round 2, registered by another
lane after this one) is the run whose planned kinds § 6 freezes forecasts for. No other number is taken.*

**Written and committed before any output it governs exists:** no feature of § 2 computed on any row of § 3 beyond the
development checks § 0 lists, no residual set beside any feature, no fit, no held-out error, no forecast. Everything below is fixed
now. A departure is a dated amendment file beside this one, written before the numbers it touches.

**What it is, in one paragraph.** M10 prices the toggles the open-RTL bench counts at three launch points (or 9-243 for a case-S
tile), and for the accumulator it carries one estimate, `c_end`, the register flips of one op at 2^19 from a reconstructed start.
The term adds to M10, for every tile, a price per **toggle of the accumulator's register over the whole launch**, counted exactly
by stepping the lab's committed accumulator arithmetic (`accum.c`) through every op of a launch of the kit's own size, and, for the
floats, a price per **partial-product row of A beyond A = 1.0's, times each toggled significand bit of B**, from the open RTL's
radix-4 recoder (which recodes A, the operand the PRM's order broadcasts to the lanes). The two prices are fitted per family on
M10's committed held-out errors and the other committed rows of § 3, one run left out at a time. Term S (a per-position price,
`tools/claims-v3/m10-s/`) failed its entry rule; this term takes its place as M10's candidate for the single-high-bit class, but it
is a per-tile term on every tile, with no class or position in it.

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sat 7 Nov 2026 about 10:40-10:50 PST: public rows
   P11, P12, P15, P29, H06, H07, H08, H09, H15, H16, H19, H20, H21, H24, H27 and L23 (opaque pointers).
2. **Used.**
   - **M10 as frozen** (H21; registration `e9367b66`, `tools/claims-v3/m10/REGISTRATION.md`; fit `6829c9ba`,
     `docs/reports/data/2026-11-04-q142m-m10/`): `m10.json` (the float family `G8+c_end+xstage`, variant B+a+b; the int8 family
     `J8+bsat+bpp_r4`, variant B; `card1_scale` 0.9616 per family; `session_scales_training`), `rows-m10.json` (every row's
     committed held-out error `err_w`, leave one kind out), and the rows' tile paths, tile sha256 and measured rates as `fit_m10.py`'s
     `assemble` reads them: `docs/reports/data/2026-11-04-q140m-m9/rows-m9.json` (`1f244140`) for M9's 855 rows, and pool 7's 104 from
     `tools/claims-v3/kinds/blind7/blind7.json` (`75802201`) with E163's and E164's footing reductions (`e163.json`, `e164.json`).
     *Check:* each M10 row is matched to its source row by experiment, card and key, and its tile hashes as the source says, else stop.
   - **The accumulator arithmetic** (H09): `rtl-sim/fma_toggle_v2/accum.c` (`528fbe09`), included unchanged: fp32 FMADD with
     round-to-nearest-even, denormal operands read as zero and denormal results flushed (40,000 of 40,000 exact against the RTL in
     `fcheck_unit.py`); fp16's fixed-point window (`fp16_model.py`, ported); int8's exact int32 sum; the RTL's order and zero gate.
     **E178's exact flip model** (H27; `48171930`, `tools/claims-v3/e178/flipmodel_e178.c`), which steps the same arithmetic for a
     one-number kind and counts `c_store`, the 256 accumulator entries' Hamming distance at every step. *Check against an earlier
     computation of the same quantity at the same operating point:* for E178's 40 kinds, this term's x_acc at forecast_e178's
     `N_LAUNCH` must equal `forecast-e178.json` › `kinds.<k>.flips_i.launch_mean.c_store` to 0.001 a op (the file prints 4 decimals),
     else stop.
   - **The open RTL** (P12: core-et, Erbium branch, `b38a1a3`, under `external/core-et`, the RTL the bench simulates):
     `rtl/shire/minion/vpu/txfma_7s/txfma_booth_ppg_32r4.v` (radix-4 Booth, 17 digits from `ext_mplr = {2'b0, mplr, 1'b0}`; lines
     57-67), `txfma_f1.v` lines 109-114 (`mplr = fa_f1a_h`, `mpcnd = fb_f1a_h`), `txfma_f0.v` lines 388-399 (fa from opa: fp32
     `{hidden, mantissa[22:0], 8'b0}`, fp16 `{hidden_hi, mant_hi, 9'b0, hidden_lo, mant_lo, 1'b0}`), and `vpu_bypass.v` lines 95-104
     (operand source 0 is TenA's read data, source 1 TenB's). So the multiplier recodes A.
   - **The PRM's order** (P11; the TensorFMA pseudo-code, PRM 9.4, as `accum.c`'s header and the kinds spec state it, H06): for each
     B row k, for each A row i, two micro-ops of 8 lanes, lane l taking A[i][k] (broadcast) and B[k][8h + l]; int8 one micro-op of 16
     slots. 512 float micro-ops and 256 int8 micro-ops an op.
   - **Where the accumulator lives in the open RTL, and what the silicon has:** C is held in each lane's register file
     (`vpu_64x32_3r2w_vpurf`; the bench writes C there by back door, `rtl-sim/fma_toggle_v2/tb_vpu.sv` lines 80-83) and int8's in TenC
     (`vpu_tensorc_rf`); the bench's dated note 1 (`1c43f5cb`, `rtl-sim/fma_toggle_v2/README.md.dated-note-1.md`) and Ditzel's
     "Esperanto Retrospective" (P15; Cool Chips Hot Takes, 25 Aug 2026, slide 12): the silicon's register file is full custom and not
     in the open RTL.
   - **M10's term b** (H20, H21; RECOUNT-RULE.md `b4444dd4`, Q141(t)'s recount `67d5e44f`): counting a case-S tile at 9-243 launch
     points instead of 3 moved its features by -0.57 to +1.05 W and cut the S class's held-out error from 0.50 to 0.26 W (M10 README
     § 4): the accumulator's state over the launch carries that class's cost, and three points average it poorly.
   - **Term S** (H20; `dfc005bf`, `23e23210`, `6f9ae408`, notes `1c43f5cb`, `f8c3c9be`, `aab4a5f9`; `tools/claims-v3/m10-s/`,
     `docs/reports/data/2026-11-06-q145b-m10-s/`): its 99 single-B-bit steps in seven lists, each the list's registered step over its
     own zero on M10's footing, with M10 as frozen's step from the committed three-point counts and their difference, as committed in
     `note2-term-s-reg-99.json` › `steps` (`run`, `card`, `fmt`, `meas_w`, `pred_w`, `r_w`, `s`, `c`, `rate`, `tile`, `zero_tile`,
     their sha256); its failure (E2 on card 1, E3 on pool 6's and 7's case-S kinds) and its structure reading by A word (its dated note
     2 § 2: M10's step error with A = π −0.438 W against A = 1.0's −0.066 W, five and 70 steps): the reason for the Booth feature.
   - **Pool 8 at 600 MHz** (H24; design `153b720f`, frozen predictions `4576fb90`; E171 `91f8ae40` on aifoundry3, E172 `b3255af1` on
     aifoundry1 card 1): `tools/claims-v3/kinds/blind8/blind8.json` (tile files and sha256), `sets-blind8.json` (sets N1 and
     `other_priorities`), and each run's `scored.json` › `primary.rows.<tile>` (`e_primary` = D − M10's primary, `rate_per_s`, `case`) and
     `primary.scale.s_float`.
   - **E178** (H27; registration `48171930`, data `f7820e70` with notes `f68f0380` and `52f53c16`,
     `docs/reports/data/2026-11-06-e178-one-number-aifoundry3/`): `scored.json` › `primary.reported.kinds.<k>` (`D_minus_P_w`, `P_w`
     at the session's float scale and measured rate, `rate_per_s`, `c_kept`, `n`), `primary.scale.s_float`, and `primary.rules`
     › `E178-H-int8` (his pair, int8 5s - 4s); `tools/claims-v3/e178/kinds-e178.json` and `tiles/`.
   - **Q148(c)'s constant-lane term** (`c71fbc7f`, `413d252b`, `6b5ad913`, `d62d0c8f`, `tools/claims-v3/m10-c/`) and its reading on
     E178 (`52f53c16`, `arm-m10c-termc-e178.json`): NOT RESOLVED, worse in fp16, so it does not enter M10. Its registration is this
     file's template (rows, responses, the leave-one-run-out fit, the jackknife), and its fate is why this term carries no level.
   - **The kits' launch sizes:** every experiment's committed `runs.jsonl` files under its data directory (each run's `iters` per
     launch; § 2.3).
3. **Not used.**
   - **The single-bit lists already among M10's rows** (E102's and E147's steps): their measurements enter once, as M10's rows.
   - **int8 single-bit lists** (E79's `b8_*`, E102's `bk_*`, E151's B tiles): no committed M10 step error exists for them; and int8's
     unit recodes B, not A (H16), so § 2.2's feature is a float one. Not applicable now.
   - **800 MHz** (E165, E170, E173, E174, E175): the term is fitted at 600 MHz only and is not carried to the cap here.
   - **Pool 8's anchors, check anchors and re-runs** (sets KA, scale and zeros anchors, RR): the anchors set the session scale; the
     re-runs' kinds are in M10's own fit, so M10's error there is not held out.
   - **E178's F arm** (the accumulator's launch mean at M10's own `c_end` price): reported beside in § 7 only; the term is added to P.
   - **Term S's per-position values and Q148(c)'s levels:** not stacked; reported beside where § 7 says.
   - **A recount of any tile on the bench:** not needed; the trace is exact by construction and the bench's counts stay as committed.
   - None of Q124's counts.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code, the open RTL or a public talk. No NDA-tier
   piece is used, so there is no sha256 line, and no NDA-tier name, verdict, ratio, direction or figure is cited.
5. **Readiness:** this block is the registration's own.

## 0. What was read before this was written (disclosed)

- **The misses this term is aimed at, as committed:** pool 8's class S (M10 0.273 / 0.238 W rms, bias +0.195 / +0.138 W on aifoundry3 /
  card 1); M10's own S class (0.234 W held out, bias +0.065 W) and its term b table; term S's README and dated notes, including its
  by-field and by-A-word S0 figures, and one step's S0 residual printed while reading the 99-step file's layout (E65's `bit_0`);
  Q148(c)'s README and its E178 reading; E178's results (his int8 pair +0.053 W [+0.022, +0.085] against P's +0.186 W; the int8 price
  per flip 2.78 fJ against 7.48; the levels above zeros: fp32 +0.081 W, fp16 +0.017, int8 -0.177 W bias against M10; the ranking
  rho +0.643) and the day critic's readings of them.
- **The term's two features were named in this lane's brief** (Q153, lane 1).
- **Development checks, structure only, no residual:** the trace program of § 2 was built and run on five of E178's kinds (int8 5s
  and 4s, fp32 1s and 5s, fp16 5s), where it reproduced `forecast-e178.json`'s `c_store` launch means to the printed 4 decimals, and
  timed on three random tiles (`fp32/randn`, `fp16/randn`, `int8/full`) at launches of 27,000 and 54,000 ops; and each experiment's
  timed launch sizes were tabulated from its `runs.jsonl` files (§ 2.3). No feature was set beside any error.

## 1. Why this term (public reasons)

- **The accumulator's walk is where a one-word tile's energy goes.** A tile whose lanes hold constant words feeds the same operand
  bits every cycle; what moves is the accumulator, rewritten at every step of every op (nearly all of a one-number kind's flips in
  E178 § 3's model come from it: its register entries, `c_store`, and the write-back and bypass buses that carry each new value,
  `wb_rz` and `byp`). M10 sees it through the bench's three launch points and one `c_end` estimate; its own term b showed that how
  the launch is sampled moves a single-high-bit tile's price by up to 1 W.
- **The silicon's accumulator store is not the bench's.** In the open RTL C lives in the lane's register file and in TenC; the
  silicon's register file is full custom and absent from the open RTL (P15, the bench's dated note 1). So M10's price for the bench's
  register-file toggles need not be the silicon's price for the accumulator's toggles.
- **A's word sets how many partial-product rows a B toggle moves.** The multiplier recodes A (radix 4), so a B bit that toggles moves
  one partial product per non-zero Booth digit of A: two digits for A = 1.0 (the fewest any normal word has), up to 13 for an fp32
  word and 7 for an fp16 half. M10
  over-prices the lists' B steps with A = π far more than with A = 1.0 (term S's note 2 § 2).
- **The term is empirical.** Which cells carry either price is not resolved here.

## 2. The features (exact, per tile)

### 2.1 x_acc, the accumulator's register toggles

For a tile of format φ and a launch of N ops: every element C[i][j] follows its own sequence c ← step(A[i][k], B[k][j], c), k = 0..15
an op, with `accum.c`'s arithmetic and zero gate; op 0's first step is a multiply. **x_acc(tile, N)** = the mean over ops 1..N−1 of
the sum, over the 256 elements and the 16 steps of the op, of the Hamming distance between the 32-bit accumulator word before and
after the step: toggles per op. Op 0 is left out, as `flipmodel_e178.c` leaves it out (its launch events are reported apart there and
are at most 0.009 flips an op). **Per micro-op** it is x_acc / 512 (fp32, fp16: 8 lanes a micro-op) or / 256 (int8: 16 slots), each
micro-op's lanes summed; the fit uses x_acc per op, the unit of M10's features. Floats also give it by field (sign, exponent,
mantissa), reported.

### 2.2 x_bth, A's non-zero Booth rows beyond A = 1.0's (floats only; 0 for int8)

- **The rows of an A word:** mplr as `txfma_f0.v` forms it (fp32 `{hidden, mantissa[22:0], 8'b0}`; fp16 the two halves at
  `{hidden_hi, mant_hi[9:0], 9'b0, hidden_lo, mant_lo[9:0], 1'b0}`), `ext = {2'b0, mplr, 1'b0}`, 17 digits from its bit triples, a
  digit non-zero unless its three bits are 000 or 111. **The excess rows** e(A) = the non-zero digits less 2 for each normal product
  (fp32 one, fp16 two halves); a zero or denormal half has none and contributes 0. e(1.0) = 0, and e ≥ 0 for every word.
- **B's toggled significand bits:** the hidden bit and the mantissa of the B word a lane holds (fp16 per half; a zero or denormal half
  reads 0), against the B word the same lane held at its last active slot.
- **x_bth(tile)** = the sum over the 8 lanes and over the 512 micro-op transitions of one op, in the PRM's issue order (the op's last
  micro-op followed by the next op's first), of e(A_new) × the toggled significand bits of B (fp16: each half of A with the same half
  of B), per op. A lane at a gated slot (an A or B word of 0) keeps its operands: no toggle and no contribution. x_bth does not depend
  on the launch: the stream is the same every op.

### 2.3 The launch size N

N(experiment, type) = the median, rounded half up, of `iters` over the experiment's timed launches of that type (launch ≥ 0, `ok`
true) in every committed `runs.jsonl` under its data directory, smoke and stop-test passes left out. The tabulation (§ 0) found one
for every experiment of § 3 (E65 fp32 538,866; E67 fp32 456,502; E78 fp32 538,543, fp16 539,155, int8 911,863; E178 fp32 539,132,
fp16 538,872, int8 913,813; the rest 534,446-539,278 for the floats and 901,883-913,579 for int8). A tile that ran in several
experiments has x_acc at each one's N, from one trace (cumulative sums). Reported beside, not used: x_acc at the experiment's smallest
and largest launch, for E67 (whose launches ran 269,962-543,669 ops under another user's host load).

### 2.4 The code

`tools/claims-v3/m10-acc/acctrace_m10acc.c` (it includes `accum.c` unchanged and prints both features for one tile and a list of N),
committed after this file and before its first run on any row of § 3; built with `cc -O2 -std=gnu11 -ffp-contract=off`.

## 3. The rows and the response

Every row is at 600 MHz on M10's registered footing. For each: the response e (W, measured − M10's prediction), the session's float
scale s (1 for int8), the card term c (M10's `card1_scale` on card 1, else 1), the measured rate (ops a second), the tile (and for a
step its zero), and the experiment whose N applies.

- **(a) M10's 959 rows** (31 sessions, E78-E164): e = `rows-m10.json` › `err_w["B+a+b"]` for floats and `err_w["B"]` for int8, M10's
  committed held-out errors (leave one kind out); s = `m10.json` › `families.float.session_scales_training.<exp|card>`; rate the row's
  measured rate. E147's 70 rows are steps over each item's own zero (`rows-m9.json` › `zero`; the zero's tile from E147's pool,
  `tools/claims-v3/e147/e147/tiles/fp32/`): their features are the item's less the zero's.
- **(b) Pool 8 at 600 MHz** (E171 on aifoundry3, E172 on card 1): the 40 kinds of sets N1 (31) and `other_priorities` (9), on each card:
  e = `primary.rows.<tile>.e_primary` (D − M10's primary, blind); s = `primary.scale.s_float`; rate = `rate_per_s`.
- **(c) The single-bit lists outside M10's rows** (E65 37 steps, E67 4, E70 1, E79 17, E134 11: 70 steps, aifoundry3): their steps in
  `note2-term-s-reg-99.json`:
  e = `r_w` (the list's step on M10's footing less M10 as frozen's step); s, c and rate as the step carries them; features the item's
  less the zero's.
- **(d) E178's 40 kinds** (aifoundry3): e = `D_minus_P_w` for each kind with `c_kept` true and n ≥ 2; s = `primary.scale.s_float`; rate
  = `rate_per_s`.
- **A run** is one session (an experiment on a card) for (a), (b) and (d), and one list for (c): 31 + 2 + 5 + 1 = 39 runs.
- **The S class** (named for R3 and § 7): M10's 26 S-class rows (pool 6's and 7's case S) and pool 8's 8 case-S tiles of set N1 on
  each card (16 rows).
- **The regressors:** z_acc = s × c × rate × x_acc and, for floats, z_bth = s × c × rate × x_bth (W per J a toggle). A step's z is its
  item's less its zero's.
- **Checks before any fit** (else stop): the row counts by source, family and card are printed; every tile hashes as its source says;
  (a)'s e equal `rows-m10.json`; (b)'s e_primary equal D_w − M10_primary_w to 1e-9 W; (d)'s D_minus_P equal D − P to 1e-9 W.

## 4. The form, the fit, the held-out errors and the uncertainty

- **The term.** **M10-ACC's D = M10's D + s × c × rate × (τ_acc,φ × x_acc + τ_bth × x_bth)**, φ the family (float: fp32 and fp16
  together, one accumulator price, since C is an fp32 word in the same register file in both; int8 its own, TenC), τ in J a toggle;
  x_bth is 0 for int8. The term is 0 on the zeros tile and at any tile whose accumulator never moves.
- **The estimator.** Per family, ordinary least squares through the origin of e on the regressors (floats z_acc and z_bth; int8
  z_acc), every row weighing the same, in W.
- **Leave one run out (nested).** For each run R, τ is fitted on the other 38 runs' rows, and R's rows are predicted:
  **e' = e − τ_(−R) · z**, the term's held-out errors. There is no inner choice: one form per family.
- **The frozen term:** τ fitted on every row. **Its uncertainty:**
  - (i) **the jackknife over runs:** se_J = √((n − 1)/n × Σ_R (τ_(−R) − mean)²), n the runs holding the family's rows; **the 95%
    interval τ ± t(0.975, n − 1) × se_J**, the registered interval;
  - (ii) beside, a cluster bootstrap over runs (runs resampled with replacement, 2,000 draws, numpy `default_rng(1531)`), percentile 95%;
  - (iii) the OLS standard errors, reported only;
  - (iv) **σ_ACC**, the rms of e' by family, format and card: one new row's scatter around M10-ACC.
- **Reported arms (frozen beside, never in the entry rule):**
  - **ACC1:** floats with x_acc alone (no Booth feature).
  - **strict:** the same form fitted on rows (a) and (c) only, leaving pool 8 and E178 out of the fit altogether; its leave-one-run-out
    errors on (a) and (c), and its predictions for (b) and (d) from the fit on all of (a) and (c).

## 5. The rule by which the term enters M10 for the next blind pool (read on § 4's held-out errors, per family)

- **R1:** pooled d = rms(e') − rms(e) over the family's rows ≤ −0.005 W, and the 95% interval of d by a cluster bootstrap over runs
  (2,000 draws, `default_rng(1532)`; runs resampled, e and e' kept paired) has its upper end below 0.
- **R2:** d < 0 on aifoundry3's rows and on card 1's rows separately.
- **R3 (floats):** on the S class (§ 3, 42 rows), d_S = rms(e') − rms(e) ≤ 0.
- **The family's term enters if R1-R3 hold** (int8: R1 and R2). The next blind pool's frozen predictor (its own registration,
  committed before its designer draws a tile) then computes **M10-ACC** for that family with this file's frozen τ, unchanged, with M10
  beside it as an arm, and scores **P9-ACC**: rms(D − M10-ACC) against rms(D − M10) over its tiles on each 600 MHz card, paired, in
  P8-M1's form, BETTER / WORSE / NOT RESOLVED. **Otherwise** M10 stays as frozen for that family, and M10-ACC is a reported arm in that
  pool and in E182.
- **Readings that would show the term is not wanted, beside the rule (reported, never a verdict):** τ's jackknife interval includes
  0; τ_(−R) changes sign between runs; the S class or E178's int8 kinds read worse with it; the strict arm's τ lies outside the
  primary's interval.

## 6. What is frozen, and the forecasts

- **The term:** τ per family with § 4's intervals, σ_ACC, and the rule's readings, in `m10acc.json`, by the fit code; a predictor,
  `predict_m10acc.py`, computes the term's watts for any tile (or for a one-number kind from its A and B words) at a given format, N,
  rate, card and s, from `m10acc.json` and the trace program alone, self-tested on committed rows.
- **Forecasts for the next blind pool's rule (F-P9):** from § 4's held-out errors on pool 8's 40 kinds per card (rows (b)): the
  forecast P9-ACC difference d = rms(e') − rms(e) per card and family for a pool drawn like pool 8, with a bootstrap over kinds (2,000
  draws, `default_rng(1533)`); and the same on pool 8's class S. They are forecasts from held-out errors, not a test.
- **Forecasts for E182's planned kinds:** E182's kinds are not drawn when this file is written (its brief: one-number kinds whose A and
  B words have unequal popcounts, and E178's int8 5s and 4s as an A B B A train). So this lane freezes, for a grid of one-number kinds,
  the term's watts on aifoundry3 and card 1 at E178's launch sizes and measured rates with s = 1: **int8**, A and B words each of the
  bytes 1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 31, 63, 85, 127, −1, −2, −85 and −128 repeated four times (324 kinds); **fp32 and fp16**, A and
  B each of E178's eleven values 0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8 and −1 (121 kinds a format). For a one-number kind x_bth is 0, so the
  term is τ_acc × x_acc. E182's lane adds it to its own M10 forecast (P) for each kind it draws; a kind outside the grid runs through
  `predict_m10acc.py` unchanged.

## 7. What is reported, and how each figure is labelled

- **Held out (leave one run out):** every figure of § 4 and § 5, by family, format, card, source (a)-(d) and run; the arms beside.
- **Post hoc** (pool 8 and E178 were measured, and their misses read, before this file; labelled post hoc everywhere):
  - **pool 8's class S**, 8 N1 tiles per card: rms and bias of e and of e' (primary and strict), against M10's 0.273 / 0.238 W and term
    S's 0.357 / 0.323 W;
  - **E178's int8 levels**, its 13 int8 kinds: rms and bias of D − P and of D − (P + the term) (primary and strict), with E178's F
    beside (`D_minus_F_w`);
  - **his int8 pair, 5s − 4s:** P's +0.1857 W, P + the term's difference, and E178-H-int8's measured +0.0532 W [+0.0217, +0.0848];
  - E178's float levels by format; the S-class's and E178's x_acc per micro-op.
- **Blind:** nothing here. The first blind tests are the next blind pool (§ 5) and E182 (§ 6).

## 8. The code and the order

1. This file, and nothing else, is committed first.
2. Then `acctrace_m10acc.c`, `fit_m10acc.py` (the rows, checks, fit, held-out errors, uncertainty, rule, forecasts and post hoc
   readings) and `predict_m10acc.py` with their self-tests, before the first full trace run on the rows of § 3.
3. Then the outputs in `docs/reports/data/2026-11-07-q153-m10acc/`, with a README and a hash list: the features of every tile
   (`features-m10acc.json`), the fit (`fit-m10acc.json`, `m10acc.json`), the forecasts and the post hoc readings. New files only; no
   committed file changes.
4. **Compute:** the traces are batch work and run on the mini through `run_remote --host mini` (the C program only; at most 6
   workers); the fit runs on the Intel through the round's local slot, one job at a time. No card, no lab box.

## 9. What this cannot say

- **The features are the open RTL's structure,** not the silicon's: the term prices them empirically, and which cells carry the
  prices is not resolved.
- **x_bth's gate rule is an assumption** (a gated lane keeps its operands); it touches only tiles with zero words.
- **One N per experiment and type:** a run's own launch differs from the median by up to about 1.5% (E67 more); x_acc's dependence on
  N is reported for E67 and the launch-size sensitivity of the frozen term is stated.
- **M10's held-out errors are leave one kind out with M10's fold scales;** this term is fitted on them with the frozen session scale
  in z, so a fold scale δ away from the frozen one moves z by δ × z (under 1% of the term).
- **Pool 8 and E178 are post hoc here**, as § 7 labels them; the strict arm reads them without fitting on them, but this file was
  written after their misses were read.

SPDX-License-Identifier: Apache-2.0
