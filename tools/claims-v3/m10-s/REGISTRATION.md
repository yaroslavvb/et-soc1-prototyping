# Q145(b): term S, a per-position single-high-B-bit term for M10, by format and clock, fitted nested on the committed single-bit price lists, with its uncertainty and the rule by which it enters M10 for the next blind pool; and the exact one-footing test "M10 on the law" (registration, written before any fit output)

*Fri 6 Nov 2026 (week 45), written about 02:25-03:00 PST on the Intel, desk only (no card, no lab box, no device command, no bench
sweep, no Discord, no Modal), by the lane classs-q145b of Q145(b), round B of the stock-take's first steps (MAP step 2).
It answers the card day critic's rank 6 ("the next power term, registered first: single high B bits per position, by format and
clock ... fitted nested") and the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) **item 6** (a power model across
kinds). The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of numeric
computations as accurately as possible; and his words of 5 November: "I want to build up on previous things as much as possible
before building new stuff." No new E or Q number.*

**Written and committed before any output it governs exists:** no fit of the term, no M10 prediction or residual on any price-list
item, no re-reduction at the footing law, no refit of M10 or M9. Everything below is fixed now. A departure is a dated amendment
file beside this one, written before the numbers it touches. No new card time and no bench sweep: every count used is committed.

**What it is, in one paragraph.** On pool 8 the single-high-B-bit tiles (class S) were both models' largest blind miss: M10 read
0.273 / 0.238 W rms (bias +0.195 / +0.138 W) on aifoundry3 / card 1 at 600 MHz, and +1.06 / +0.71 W above both models on
aifoundry2 / card 0 at the 800 MHz cap. The lab has measured the price of exactly that stimulus (one B bit alternating every cycle
in every lane, A held) at most bit positions, in seven committed price lists, and none of those rows taught M10 a separate term:
two of the lists (E102's and E147's) are among M10's 959 rows as ordinary rows, the rest were checks. Term S is the part of a
measured single-B-bit step that M10's bench-count prices miss, as a function of format and bit position, fitted on those lists with
one run left out at a time, and added to M10's prediction for any tile with that structure.

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Fri 6 Nov 2026 about 02:05-02:20 PST: public rows
   L23, H20, P15, P12, H09, H07, H16, H19, H21, H22, H24 and H15 (opaque pointers), and the map's rows 3 and 18 and its section 4 step 2.
2. **Used.**
   - **The single-bit price lists**, each as its registered primary gives the step of an item over its own registered zero, at
     600 MHz:
     - E65 (Q126, aifoundry3, 26 Oct), `85f52e08` `docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json` ›
       `cards.aifoundry3.bits.<k>` and `.bits_pi.<k>` (`dW`, `se`, `zero`), its reduction's leak 0.18238 W/°C (`gates`);
     - E70 (Q129, aifoundry3, 27 Oct), `7da0318d` `…/2026-10-27-e70-saturation-ladder/hl.json` › `cards.aifoundry3.items.lq_h1`
       (`d_p80`, `d_p80_se`; zero `lq_h0`), leak 0.1975 W/°C;
     - E79 (Q130, aifoundry3, 31 Oct), `8d2fe956` `…/2026-10-31-e79-fp16-int8-bit-prices/hlp.json` › `cards.aifoundry3.prices.fp16_b.<k>`
       (`dW`, `dW_se`, `zero`, `rate_ops_s`) and `order_probe.fp32.jg` (`b32_22` over `h32q`), leak 0.08336 W/°C;
     - E102 (Q132, aifoundry1 card 1, 1 Nov), `1e76be87` `…/2026-11-01-e102-balanced-bit-prices/scored.json` › `primary.prices`
       (`<type>.<item>@<block>` › `board.W`, the block the item is listed in), leak 0.2414 W/°C;
     - E134 (Q136, aifoundry3, 2 Nov), `6ae1019c` `…/2026-11-02-e134-bit-prices-more/scored.json` › `primary.prices.<item>.W`, leak
       0.04505 W/°C (`e134.json` › `leak`);
     - E147 (Q138, aifoundry3, 2 Nov), `b2348e11` `…/2026-11-02-e147-bit-prices-rest/scored.json` › `arms.dips_4w.prices.<item>.W`
       (A2's 4 W dip line, the arm M8, M9 and M10 read), leak 0.04512 W/°C (`e147-dips4.json` › `leak`);
     - each list's own zero for each item, read from the same file (`zero`), or `hq` for E102, E134 and E147's B items (their
       registered `predictions-e1xx.json` › `items.<item>.zero`).
     *Check against the same quantity at the same operating point:* where two lists measured the same bit position with A = 1.0 on
     aifoundry3 at 600 MHz (bits 0-5, 16-19, 21, 24-26, 28-29 in E65 and E147; 6-16 in E65 and E134; 22 in E65 and E79), the
     measured steps are set side by side (reported, `agreement` in the output); they differ in base words, so this is a check on the
     lists, not a test.
   - **The bench's committed three-point counts** of every item and zero (`rtl-sim/fma_toggle_v2`, `-fno-dfg`, Q132(b)'s bench, H09):
     `e57e65a3` `docs/reports/data/2026-11-01-q132-rtl-bench/counts-hl.json` (E65, E70) and `counts-hlp.json` (E79); `47060961`
     `…/2026-11-01-e102-balanced-bit-prices/bench/counts-e102.json`; `af56740a` `…/2026-11-02-e134-bit-prices-more/bench/counts-e134.json`;
     `c41c3905` `…/2026-11-02-e147-bit-prices-rest/bench/counts-e147.json` (with E134's for the three tiles E147 reused, as
     `posthoc_m7_e147.build_pool` merges them). *Check:* this lane's step features for E147's 70 rows equal M9's committed step
     features (`rows-m9.json`, `1f244140`) to 1e-9 in every feature M10 prices, before any residual is computed (else it stops).
   - **M10 as frozen** (`e9367b66` registration, `6829c9ba` `docs/reports/data/2026-11-04-q142m-m10/m10.json`): the float form
     `G8+c_end+xstage`, `coef_J`, card 1's term 0.9616, the sessions' float scales (`session_scales_training`), the 4.5 s heat law's
     per-card coefficients (0.1198 / 0.1194 °C per board W, H22); its feature chain `fit_m10.chain_feats` (M7's, M8's and M9's code,
     unchanged); its held-out errors per row (`rows-m10.json` › `err_w["B+a+b"]`); and **term b** (H20, H21): the single high bits
     counted at 9-243 launch points by RECOUNT-RULE.md (`b4444dd4`) with Q141(t)'s 27-, 81- and 243-point counts
     (`67d5e44f` `docs/reports/data/2026-11-04-q141t-s7-recount/` and its `step81/`, `step243/`), which M10 already uses for every
     case-S tile. *Check:* `predict_m10.py selftest` passes before any residual (pool 7's 104 rows within 1e-9 W).
   - **Q141(t)'s recount as the price of counting at three points:** the committed `three_point_minus_N_w` of M10's 13 recounted
     S tiles (`m10.json`'s fit output, `heldout-m10.json` › the S table, M10 README § 4) and RECOUNT-RULE's estimator e(N)
     (`recount_rule.err` at M9's prices), computed here at N = 3 for every training item and zero (§ 3.4).
   - **Pool 8's structure and its frozen predictions** (H21, H24): the byte test `single_bit_b` of `make_blind8.py` (`153b720f`), whose
     tiles are this term's target structure (§ 2); the frozen predictions `4576fb90` `tools/claims-v3/kinds/blind8/predictions-pool8-*.json`
     (M10's D at 600 MHz and its carried 800 MHz board); the measured class-S rows of E171 (`91f8ae40`), E172 (`b3255af1`), E173
     (`ed8b5761`) and E174 (`e5206b5b`), as their registered scorers wrote them. They are used only post hoc (§ 7).
   - **E151's Booth-on-B verdict and its transfer reading** (H16; `2f70b5ff`
     `docs/reports/data/2026-11-03-e151-int8-b-aifoundry3/README.md`, results ¶ 1): on int8 the B side is recoded in Booth digits on
     silicon, and per-position B prices carry across days and cards to 9-10% rms against 36-37% for one price. Taken as the precedent
     that a per-position B price is a stable property worth a term, and as the reason int8 is left out (Not used).
   - **Ditzel's "Esperanto Retrospective"** (P15; Cool Chips Hot Takes, 25 Aug 2026; slide 12, as AI Foundry's blog publishes it,
     and as E178 `48171930` § 4 and § 11 already cite it): the ET-SoC-1 silicon's register file is full custom, and the open RTL does
     not carry it ("too tricky trying to integrate full custom register file, so this won't affect open sourced RTL"). That is why
     the bench may be blind here (§ 1). The open RTL itself (P12: core-et, Erbium branch, `b38a1a3`) is what the bench simulates.
   - **The footings:** Q139(u)'s (H15; `f47669d1` `docs/reports/data/2026-11-03-q139u-footing/reduce_footing.py` and `footing.json`:
     aifoundry3 0.2056, card 1 0.3134 W/°C, E82 A2's dip rule once), M10's registered footing; and **the footing law** FL1-FL6
     (`c14e5f35` `tools/claims-v3/footing-law/FOOTING-LAW.md` with dated note 1 `65a93fbb`; `footing_law.py k`, `footing-law.json`),
     with FL7's law reductions of E171 and E172 (`0f4204e9`
     `docs/reports/data/2026-11-05-q145a-footing-law/fl7/e171-law.json`, `e172-law.json`; k_s 0.36007 / 0.49300). *Check:* before
     any law reduction is used, the route reproduces every committed footing reduction it re-runs at Q139(u)'s frozen k exactly
     (largest |ΔD| 0, as this lane's route check already read for E102: 35 items, 0.0 W).
   - **M8's form for a step's footing** (`docs/reports/data/2026-11-03-q139m-model/fit_m8.py` line 54, `E147_FOOTING_FACTOR`): a
     step's own heating carries leakage k × c1 × step, so a step reduced at a list's own slope k_list is put on slope k by
     step × (1 − (k − k_list) × c1).
3. **Not used.**
   - **E67's A side** (`abit_*`, `abp_*`) and every A-side single bit (E102's and E134's and E147's `aj_*`, `ap_*`, `a67j_*`, E79's
     `a16_*`): the class is B's; no E67 item passes § 2's test (its `lq_h0` and `lb_h0` are E65's ties). Not applicable.
   - **E70's other rungs** (`lq_h2`-`lq_h23`, the spread `ls_*`): several bits at once, whose deficit E70 explains by shared wires;
     not single bits. Not applicable.
   - **The balanced layouts** (`bp_*` in E102, E134, E147; E79's `b16p_9`, `b32p_22`): they fail § 2's test (the flipped word moves
     between the two halves line by line, so the two accumulators of a lane stay equal); pool 8's S tiles are all-in. Not
     applicable; reported beside as a contrast only if time allows (no rule reads them).
   - **int8's single bits** (E79's `b8_*`, E102's `bk_*`, E151's B tiles): pool 8's class S holds no int8 tile, M10's int8 family has
     no S class, and E151 reads int8's B prices as Booth digits (odd against even), a different structure from a float mantissa bit.
     Not applicable now.
   - **A new recount of the price lists at 27-243 points:** a bench sweep, which this registration comes before; owed (§ 10).
   - **An 800 MHz price list:** none is committed; the term is carried to 800 MHz by M10's rule E, not fitted there (§ 5). Owed, with
     card time on his word.
   - **E151's per-position int8 prices as a fit row:** not applicable (above). **E65's hart ladder** and block D: not single-bit steps.
   - None of Q124's counts.
4. **Tiers.** Public tier only: every piece above is the lab's committed data or code, or a public talk. No NDA-tier check is used,
   so there is no sha256 line; no NDA-tier piece, name, verdict, ratio, direction or figure is cited.

## 0. What was read before this was written (disclosed)

- The card day critic's class-S and B1 figures (as quoted above; B1 FAIL LOW +0.092 / +0.105 W, +0.018 W on aifoundry3 without the
  8 class-S tiles, +0.082 W on card 1), and **E171's 13 case-S rows of `scored.json` › `primary.rows`, printed by this lane**
  (`e_primary` per tile). So pool 8 is post hoc for term S, never a test of it.
- M10's README and registration, including M10's own held-out S class (0.234 W, bias +0.065 W, 13 tiles) and its term-b table.
- The structure of every price-list tile (§ 2's test applied to their bytes; whether each has a counts row), E65's and E102's
  READMEs (the two regimes of E65's B list, the all-in and balanced layouts). **No M10 prediction, residual or error was computed on
  any price-list row before this commit.**

## 1. Why the bench may be blind here (public sources only)

M10 prices toggles that the RTL bench counts in core-et's open `vpu_top` (H09, P12). Ditzel's 2026 retrospective (slide 12) says
the silicon's register file is full custom and that the open-sourced RTL does not carry it. The bench's register-file blocks
(`vpu_64x32_3r2w_vpurf`, `vpu_tensorb_rf`, `rf_latch_1r_1w` among its counted blocks) are the open RTL's models, so whatever the
silicon's full-custom cells spend per toggled bit, beyond the model's toggle count times M10's price for it, is invisible to the
bench. A single high B bit is the stimulus that toggles one operand bit in every lane on every cycle (4,096 flips an op in fp32,
8,192 in fp16), and the accumulators of a lane alternate between two sums that differ in the bits above it, so the read and write
paths of the operand and accumulator state run at their busiest while the arithmetic barely moves. That is a reason to expect a
miss the bench cannot see; it is not a measurement of one. Nothing from a non-public source enters this registration.

## 2. The structure the term applies to (a byte test)

**T_S(x):** a float tile x (fp32 or fp16; 2,048 bytes, A then B in make_kinds' layout) passes when:
- A holds one word everywhere;
- for each lane j = 0-7, B's column j holds one word u_j in all 16 lines, and B's column j + 8 holds one word in all 16 lines,
  equal to u_j XOR m;
- m is the same for every lane and is one bit (fp32) or the same one bit in both halves (fp16); its position is p.

Pool 8's `single_bit_b` is the case u_0 = … = u_7 (one base word). A tile that passes with m = 0 is a **zero** of the structure. The
code is `tools/claims-v3/m10-s/term_s.py` (`t_s`), committed after this file and before any fit (§ 9). Applied to the committed price
lists' tiles (structure only), T_S passes: E65's `bit_0`-`bit_31` (A = 1.0) and `bpi_0`, `_8`, `_11`, `_16`, `_22` (A = π); E70's `lq_h1`
(bit 0); E79's `b16_0`-`b16_15` (fp16) and `b32_22`; E102's fp32 `bj_0`, `_6`, `_11`, `_16`, `_20`, `_22`, `_23`, `_27`, `_30`, `_31` and
fp16 `bj_0`, `_9`, `_12`, `_15` (card 1); E134's `bj_6`-`bj_16`; E147's `bj_1`-`_5`, `_16`-`_19`, `_21`, `_24`-`_26`, `_28`, `_29`: **95
steps in six runs, 75 fp32 and 20 fp16, 81 on aifoundry3 and 14 on card 1**, each zero passing as a zero. Every one has a counts row.
These are all-in single bits with eight base words per tile (one per lane), the lists' construction; pool 8's have one.

## 3. The rows and the response

### 3.1 The training steps

Every price-list item that passes T_S with a registered zero that passes T_S as a zero, with a measured step (§ Builds on, Used),
fp32 or fp16, at 600 MHz: the 95 steps of § 2. A **run** is one list (E65, E70, E79, E102, E134, E147). No other row is a training
step.

### 3.2 The measured step on a footing

The list's step ΔW_list (W, its registered primary, over its own zero), at the list's own leak k_list, put on footing slope k by
M8's form: **ΔW(k) = ΔW_list × (1 − (k − k_list) × c1_card)**, c1 = M10's 4.5 s law (0.1198 aifoundry3, 0.1194 card 1). Its SE is
the list's SE times the same factor.
- **F-reg** (M10's registered footing): k = Q139(u)'s frozen slope of the list's card (0.2056 / 0.3134 W/°C).
- **F-law** (FL1-FL6): k = k_s = k_c(T_mid) by FL3, with T_mid from the list's committed `runs.csv` by `footing_law.py k` (the
  median over the runs with an empty `fail` of (launch reading + window reading) / 2), and k_c the card's FL1 law (aifoundry3 or
  aifoundry1 card 1).
- A2's dip rule is not re-applied to E65, E70, E79 or E134 (their registered primaries are used as committed; E102's applies A2
  built in; E147's arm is A2's 4 W line). Stated as a limit (§ 10).
- E147's steps here differ from M10's rows of the same items by M8's choice of k_list = 0 there (factor 0.9756 against this rule's
  0.9808 at k_list 0.0451): the difference is reported, never refitted.

### 3.3 M10's predicted step

**ΔD_M10 = s × c × rate × Σ_q coef_J[q] × (f_q(item) − f_q(zero))**, M10's frozen float prices and terms (`m10.json` › `families.float`),
the features from the item's and the zero's committed three-point counts through `fit_m10.chain_feats` (and, for E147, M9's step
construction exactly), c = 0.9616 on card 1 else 1, the item's measured rate from its list (else make_kinds' nominal rate), and s =
the session's M10 float scale where M10 has one (E102: 1.00507; E147: 1, as `m10.json` records), else 1 (M10's rule for a session
with no anchor of the family). On F-law, the base is **M10 on the law** (§ 6) if it exists when the fit runs, else M10's first-order
one-footing companion (ΔD_M10 × (1 − c1 × (k_s − k_frozen)), FL7's form), named in the output.

**The residual:** r = ΔW(k) − ΔD_M10, in W, and **ρ = r / (s × c × rate)** in J per op (the unit the term is priced in).

### 3.4 The count error of each step

e3 = √(e(3)_item² + e(3)_zero²), RECOUNT-RULE's estimator at N = 3 (`recount_rule.err` over the three launch points priced at M9's
frozen prices). Reported per step; it is not a weight (§ 4 uses plain means).

## 4. The candidate forms, the nested fit and the uncertainty

τ_φ(p) is the term's value for format φ and bit position p, in J per op. Each value is the **plain mean of ρ** over the training
steps in its cell (in the fold).

| form | cells |
|---|---|
| **S0** | none: τ = 0 (M10 as frozen) |
| **S1** | one per format: fp32, fp16 |
| **S2** | one per field: fp32 mantissa 0-22, exponent 23-30, sign 31; fp16 mantissa 0-9, exponent 10-14, sign 15 |
| **S3** | one per (format, position) where the fold holds a step at that position; else S2's value for the position's field in the fold; else S1's |

**Nested: leave one run out.** For each run R, every value is fitted on the other five runs' steps only, and R's steps are predicted
as ΔD_M10 + s × c × rate × τ_φ(p). Their errors (measured − predicted) are each form's held-out errors. There is no inner choice: each
form's structure is fixed. The selection below reads the same held-out errors it reports, so the chosen form's held-out figure keeps
that optimism (at most three candidates).

**The selection and the entry rule (the term enters M10 as its class-S term for the next blind pool if ALL hold, on F-reg):**
- **E1.** The best of S1-S3 (lowest held-out rms over the 95 steps), B*, beats S0: held-out rms(B*) − rms(S0) ≤ −0.010 W, with its
  95% paired-bootstrap interval below 0 (over the 95 steps, 2,000 draws, seed 145; resampling steps, both forms on the same draw).
- **E2.** The difference is negative on aifoundry3's 81 steps and on card 1's 14 steps separately.
- **E3.** On pool 6's and pool 7's 13 case-S kinds (26 rows of `rows-m10.json`: M10's held-out errors `err_w["B+a+b"]`, N-point
  counts; the term never reads them), M10 + B* frozen (fitted on all 95 steps) does not read worse: rms(e − s c rate τ) − rms(e) ≤ 0
  over the 26 rows (its 95% interval over the 13 kinds, 2,000 draws, seed 1452, reported). These tiles have one base word, the
  target structure; this is the term's held-out test on kinds.

**The frozen term:** B* refitted on all 95 steps (on F-reg; on F-law beside). **Its uncertainty:**
- each value's 95% interval by a bootstrap over steps within its cell (2,000 draws, seed 145) and, beside, over runs (resampling the
  six runs, 2,000 draws, seed 146);
- σ_S,φ: the held-out rms of B*'s errors over the format's training steps, the term's prediction error for a new step;
- **the band for a T_S tile:** M10's band with σ_S added in quadrature to its pool term: half-width k_M10 √(pool² + σ_S² + s² xᵀCx),
  k_M10 and pool as `m10.json` gives them for the format and card.
- **δ, the count bias:** the mean of `three_point_minus_N_w` over M10's 13 recounted S tiles by format, with its t-interval. The
  training residuals use three-point counts, an N-point prediction does not: if δ's 95% interval excludes 0, the term used with
  N-point counts is τ + δ / rate (the three-point counts' mean excess removed); else τ as fitted. Reported either way.

## 5. By clock

All seven lists ran at 600 MHz, so the term is **fitted at 600 MHz only**. At the 800 MHz cap (aifoundry2's governed bursts, card 0)
it is **carried, not fitted**: by POOL8-REGISTRATION § 5's rule E, M10-S's D at 600 MHz on aifoundry3's footing (card term 1, nominal
rate, s = 1) is the input to M9's aifoundry2 part and to E170's relation, exactly as M10's is. For pool 8's frozen files the carry is
linear in D at each tile's fixed inputs (`a2_fallback.burst_D_w` / `D600_a3_footing_w` on aifoundry2; the card-0 file's equivalent on
card 0), so the carried term is that ratio times the term's 600 MHz watts (read from the frozen files; checked to be the same ratio
for D and D + 1 W on three tiles by calling the frozen part, if the part is importable, else stated as an assumption). An 800 MHz
price list is owed.

## 6. M10 on the law: the exact one-footing test (round A's owed test)

**The question:** does M10's lead over M9 (P8-M1 BETTER on E171 and E172 on the registered footing) survive when the training rows
and the tests share one footing, the footing law, and both models are refitted on it?
- **Rows:** M10's 959 rows (M9's 855 among them), each experiment re-reduced by FL3 at its own k_s = k_c(T_mid): the 26 experiments of
  Q139(u) through `reduce_footing.reduce(exp, k_s, …)` unchanged (A2 once), the pool sessions E153, E157, E163, E164 through their own
  registered wrappers with `--leak k_s --no-refit`, E147's steps by M8's form with k_s in place of the frozen slope. T_mid by
  `footing_law.py k` on each re-reduction's `runs.csv` (its columns do not depend on k). The anchors (term a) are read from the same
  law reductions. A row whose item has no D at the law (a gate moved) is dropped from both models' fits and listed.
- **The refit:** `fit_m10.py`'s machinery unchanged (its `Fit10`, two passes, card term C0): M10's frozen variant (floats B+a+b with
  term b's N-point features; int8 B) on the 959 law rows; **M9 on the law** = M9's frozen forms (floats `G8+c_end+xstage`, int8
  `J8+bsat+bpp_r4`, card term C0, no session scale) refitted on M9's 855 law rows.
- **The test (post hoc: pool 8 is measured):** E171's and E172's N1, F1 and I1 tiles at FL7's law reductions (k_s 0.36007 / 0.49300),
  measured − predicted for each refitted model at each tile's measured rate, M10's float scale read on the law-reduced anchors by
  M10's rule; P8-M1, P8-M1f and P8-M1i by `score_p8_600.paired` with the pool-8 registration's draws and seeds; verdict words BETTER /
  WORSE / NOT RESOLVED. P8-A1 and the KA reading reported beside.
- **Checks first:** the route reproduces each committed footing reduction at Q139(u)'s frozen slope exactly; the machinery refitted on
  the F-reg rows reproduces `m10.json`'s float and int8 prices (relative 1e-9) and M9's `m9.json` prices (the same); FL7's committed law
  reductions are used as committed (their sha256 recorded).
- **What each outcome means:** M1 BETTER on the law on both cards: the lead was never the footing's. NOT RESOLVED on the law: the lead
  holds on the registered footing only, as the critic read. WORSE: the footing carried it.
- **If time runs short,** the test is named owed in the output with exactly what is done and what it still needs; no partial figure
  is quoted as its answer.

## 7. What is reported, and how each figure is labelled

- **Held out (leave one run out), F-reg and F-law:** every form's rms and bias over the 95 steps, by format, card, run and field; the
  paired differences of E1 and E2; E3's reading; the frozen τ table with both intervals; σ_S; δ; e3 per step; the agreement table.
- **Post hoc (pool 8 already measured; labelled post hoc everywhere):**
  - pool 8's 8 class-S N1 tiles per 600 MHz card (E171, E172): rms and bias of D − M10 against D − (M10 + term), both footings (the
    F-law reading on FL7's law reductions with M10 on the law, or its first-order companion if § 6 is owed); the 13 case-S rows beside;
  - B1's float excess (the F1 set's mean, as P8-B1 computes it) with and without the term, against +0.092 / +0.105 W, and the
    critic's split (+0.018 W on aifoundry3 without class S; +0.082 W on card 1);
  - at 800 MHz: E173's and E174's class-S tiles, M10 carried against M10-S carried (§ 5), against +1.06 / +0.71 W;
  - § 6's M1 on the law.
- **Blind:** nothing here. The first blind test is the next blind pool (§ 8).

## 8. How the term enters M10 for the next blind pool

- **If E1-E3 hold:** the next blind pool's frozen predictor (its own registration, before its designer's first tile) computes
  **M10-S**: M10 plus B*'s frozen values (the τ table committed by this lane, with δ applied by § 4's rule) for every tile that passes
  T_S, carried to 800 MHz by § 5; M10 without the term beside it as an arm. The pool's registration scores **P9-S**: rms(D − M10-S)
  against rms(D − M10) over its T_S tiles on each 600 MHz card, paired (P8-M1's form), BETTER / WORSE / NOT RESOLVED, with the band of
  § 4. The footing follows the M10 it amends: F-reg with M10 as frozen; F-law with M10 on the law, if that pool's registration makes
  FL3 primary.
- **If any of E1-E3 fails:** M10 stays as frozen for T_S tiles, and the term is a reported arm in the next pool's predictor.
- **Either way:** the pool's designer draws its S tiles without reading this lane's figures (their positions and base words by its own
  seed, as pool 8's were), and the next pool should hold at least 8 T_S tiles per float format at positions this lane's runs cover.

## 9. The code and the order

1. This file (and nothing else) is committed first.
2. Then `tools/claims-v3/m10-s/term_s.py` (T_S, the steps, the residuals, the forms, the nested fit, E1-E3, the uncertainty, the post
   hoc readings) and `tools/claims-v3/m10-s/law_m10.py` (§ 6), with their self-tests, before their first full run; then their outputs in
   `docs/reports/data/2026-11-06-q145b-m10-s/` with a README and a hash list. New files only; no committed file changes.
3. Compute: Python on the Intel through the round's local slot (one job at a time, nice 10); no bench, no card, no lab box.

## 10. What this cannot say

- **Counting:** the lists' counts are three-point launch averages; their residuals carry the bench's launch-average error (e3), which
  the recount (§ 4's δ) can only test for a mean, not remove per step. A recount of the 95 steps' tiles at 27-243 points is owed: about
  95 × 2 tiles, a bench sweep on the mini, a later step.
- **Coverage:** card 1 is one run (E102, 14 steps); 800 MHz has no list; base words are exponent-127 positive words in every list but
  pool 8's are exponents 124-130 of either sign, and each list tile has eight base words where pool 8's have one.
- **Dips:** A2's rule is not re-applied to four lists (§ 3.2).
- **Mechanism:** § 1 is a public-source reason the bench may be blind; the term is empirical. Which register file, or which path, carries
  the miss is not resolved here.
- **Selection:** the entry reads the held-out errors it reports (at most three forms).

SPDX-License-Identifier: Apache-2.0
