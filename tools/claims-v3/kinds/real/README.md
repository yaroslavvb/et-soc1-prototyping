# Q130(n): real GPT-2 tensors as kinds tiles, with frozen predictions

Sat 31 Oct 2026 (week 44). **Nine 2,048-byte operand tiles cut from GPT-2 small's real layers and the activations it
produces on a public-domain text**: three matrix products × fp32, fp16 and int8, each in its type's exact layout and
stream order, written by [`make_kinds.py`](../make_kinds.py)'s own `encode()` and measured by its own `tile_stats()`.
This answers the Q130 critic's item 3 ("all 51 kinds are synthetic"). **Frozen here, before any card runs them:**
each tile's predicted switching power at 600 MHz on aifoundry3 (for E86), on aifoundry1 card 1 (for E91), and its
burst and sustained clock under aifoundry2's own governor (for E87), in
[`predictions-real.json`](predictions-real.json), sha256
**`bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941`**. Nothing here touches a card.

**Amended the same evening, after verification and before any card ran a real tile** (§ Amendment 1). The frozen
file and its points are unchanged. Its intervals were too narrow, so E86, E87 and E91 score against the wider ones in
[`amendment-1.json`](amendment-1.json), sha256 **`f32e8a9087a9cf3bf60f29ff623c1a375537b43696df0dca24972ba220bc0d9e`**.

## Results

**1. On the gate and the total operand-bus count, real fp32 and fp16 data looks like random data.** No real tile has
a single zero word, so no lane is ever gated (`gated_lane_frac` 0.000 in all nine). The fp32 tiles flip 81,588–83,948
operand bits an op against `randn`'s 82,214 (−0.8% to +2.1%); the fp16 tiles 81,324–84,748 against 84,416 (−3.7% to
+0.4%). The mantissas, which carry most of the flips, flip as `randn`'s do, and the signs are mixed. The sign and
exponent fields do not match `randn`:
- the A side's sign flips are 0.09–0.21 a step against `randn`'s 0.27 in fp32, and 0.16–0.35 against 0.46 in fp16
  (lowest for the GELU output, whose values are mostly small and negative);
- the A side's exponent flips are 0.70–0.86 against 0.92 in fp32;
- the B side's exponent flips are 1.46–1.99 against 1.61 in fp32 (`l6_attn_qk` highest), and 2.50–3.01 against 2.80
  in fp16.

([`real.json`](real.json) `tiles.<type>.<name>.stats.<side>.hamming`; `kinds.json` `kinds.<type>.randn.stats`.)

**2. Real int8 data is not uniform random int8, and it is not sparse either.** Quantised with one simple calibration
(weights per output channel; activations per tensor, max-abs over this text), the values are small integers: over the
whole matrices the activations' standard deviation is 5–19 steps (of ±127) and the weights' 28–33
(`whole_matrix.A.sd`, `.B.sd`). 1–9% of a tile's bytes are zero, but never four in one word, so nothing gates. The bus
flips 45,684–59,716 bits an op against `full`'s 69,312. GELU's small negatives become −1 to −5, so `l6_mlp_down`'s A
half is 78.5% negative bytes with a mean popcount of 5.6 (its B half 49%, 4.0; `stats.int8_twos_complement` gives 64%
and 4.8 over both halves). The result does not rest on the calibration: four other common ones on the same windows
(per token, 99.99th and 99.9th percentile clips, token 0 left out) put D at 0.735–0.869× of `full`'s measured D
([`amendment-1.json`](amendment-1.json) `calibration_sensitivity`).

**3. The frozen predictions.** D is board switching power over the type's own zeros, at E78's primary leakage slope:
the quantity E78 measured (§ What D is). The intervals in this table are the frozen ones, which Amendment 1 found too
narrow. The (b) brackets are D-propagated ranges, not prediction intervals. E86, E87 and E91 score against the table
in § Amendment 1.

| tile | window (rows, k, cols) | bus bits/op | (a) D, aifoundry3 600 MHz [frozen 95%] | nearest E78 kind (its D) | (E91) D, aifoundry1 card 1 [frozen] | (b) burst MHz, aifoundry2 [D-propagated] | (b) sustained MHz [D-propagated], limit |
|---|---|---|---|---|---|---|---|
| fp32 `l0_mlp_up` | 96–112, 272–288, 928–944 | 82,508 | **24.46** [22.27, 26.66] | randn_small (24.76) | 23.75 [21.62, 25.88] | **710.7** [692, 730] | **602.5** [600, 611], thermal |
| fp32 `l6_mlp_down` | 112–128, 896–912, 576–592 | 81,588 | **24.37** [22.18, 26.57] | uniform01 (22.65) | 23.66 [21.53, 25.79] | **711.5** [693, 731] | **602.7** [600, 612], thermal |
| fp32 `l6_attn_qk` | 48–64, 48–64, 0–16 | 83,948 | **24.46** [22.27, 26.66] | randn_small (24.76) | 23.75 [21.62, 25.88] | **710.7** [692, 730] | **602.5** [600, 611], thermal |
| fp16 `l0_mlp_up` | 0–16, 0–32, 2032–2048 | 84,748 | **21.71** [19.91, 23.52] | randn (22.16) | 21.02 [19.27, 22.76] | **735.6** [719, 753] | **615.0** [605, 630], thermal |
| fp16 `l6_mlp_down` | 16–32, 1088–1120, 336–352 | 83,370 | **21.36** [19.55, 23.16] | uniform01 (19.43) | 20.67 [18.92, 22.42] | **738.9** [722, 757] | **617.6** [607, 633], thermal |
| fp16 `l6_attn_qk` | 64–80, 288–320, 32–48 | 81,324 | **21.54** [19.73, 23.34] | randn (22.16) | 20.84 [19.10, 22.59] | **737.2** [721, 755] | **616.2** [606, 632], thermal |
| int8 `l0_mlp_up` | 0–16, 512–576, 1088–1104 | 59,716 | **5.89** [5.00, 6.78] | gauss_q (6.60) | 5.74 [4.87, 6.60] | **800.0** [800, 800] | **796.2** [789, 799], none |
| int8 `l6_mlp_down` | 112–128, 2816–2880, 112–128 | 45,684 | **5.18** [4.30, 6.07] | sparse50 (5.46) | 5.05 [4.18, 5.91] | **800.0** [800, 800] | **798.9** [795, 800], none |
| int8 `l6_attn_qk` | 48–64, 640–704, 80–96 | 57,300 | **5.75** [4.86, 6.64] | sparse50 (5.46) | 5.60 [4.73, 6.46] | **800.0** [800, 800] | **797.0** [790, 799], none |

([`predictions-real.json`](predictions-real.json) `tiles.<type>/<name>`. The int8 bus counts are provisional, as for
every int8 kind: they rest on the reconstructed TIMA stream, `kinds.json` `facts.stream_order.int8`. The nearest-kind
label z-scores the terms with β > 0 over E78's kinds of the type. With every model column, B included, as the first
run did, four labels differ (Departure 8): the label depends on the metric.)

In words: **real fp32 and fp16 numbers should cost what random numbers cost.** Compared like with like, the predictor
puts them 0.7–1.1% (fp32) and 0.15–1.8% (fp16) below its own fit for `randn`, which is 24.64 and 21.75 W. That fit
is 0.08 W below measured `randn` in fp32 and 0.42 W below in fp16. Anchored on measured `randn`, the real tiles
would draw 24.45–24.54 W (fp32) and 21.77–22.13 W (fp16), against `randn`'s 24.73 and 22.16 W
(`amendment-1.json` `tiles.<key>.like_with_like`). **Real int8 numbers should cost 0.74–0.84× of uniform random
int8**: 5.2–5.9 W, against `full`'s 7.06 W measured and 7.04 W fitted. The saving comes from small values and fewer
flipped bits, not from the zero gate. So the speed predictions follow the power. The fp32 and fp16 real tiles burst
like `randn` (≈711 / ≈737 MHz) and fall close to the 600 MHz floor when sustained (≈602 / ≈616 MHz, thermal). int8
bursts at 800 MHz and holds 796–799 MHz sustained.

The windows were chosen to be typical, and the prediction barely depends on which window. Over the 20 candidate
windows of one product, the predicted D spans 0.24–0.75 W (fp32), 0.36–1.00 W (fp16) and 0.30–0.48 W (int8). That
is at most 28% of the frozen interval's width and 21% of the amended one's
(`a_aifoundry3_600mhz.D_band_over_20_windows_w`; `amendment-1.json` `band_share_of_width`).

## Amendment 1 (Sat 31 Oct 2026, ~19:15 PDT, before any card ran a real tile)

An adversarial check of `7d5b99af`, finished at ~19:05 PDT, reproduced every tile, hash, β and D. It found the frozen
intervals too narrow in two ways, and wording that claimed more than the data. No real tile had been run, and no E86,
E87 or E91 pre-registration existed. The points and `predictions-real.json`'s bytes are unchanged.
[`amend_real.py`](amend_real.py) computes the amendment from committed files only, and refuses to run unless the
frozen files have their committed sha256.

- **(a) The selection made the frozen intervals optimistic.** The ±2.19 / ±1.80 / ±0.89 W came from the LOO rms of
  the feature set that was chosen for having the lowest LOO rms of 11 candidates. Before drawing up the 11, the lane
  had also fitted five OLS models to E78 in its scratch. A nested LOO redoes the choice inside each fold, with
  make_real's own NNLS and tie rule. It gives **1.125 / 1.089 / 0.606 W** (fp32 / fp16 / int8) against
  1.023 / 0.835 / 0.407 W, so 95% half-widths of **±2.41 / ±2.35 / ±1.32 W**, 10% / 30% / 49% wider
  (`nested_loo`). int8's choice is unstable: `u,N_pop,A,B,Vp_pop` and `u,A,B,Vs_sig` each win 7 of the 16 folds (full
  LOO 0.4073 against 0.4086). The runner-up's int8 points, 5.94 / 4.97 / 5.72 W against 5.89 / 5.18 / 5.75, lie
  inside every interval (`runner_up_informational`). The nested rms still leaves out the five earlier OLS models.
- **(b) The stored clock brackets are not prediction intervals.** `burst_mhz_pi95` and `sus_mhz_pi95` are
  D-propagated ranges: the clock at the two ends of (a)'s frozen interval through E83's relation. They leave out the
  relation's own error, which E83 measured. On each kind's measured power it is 7.9 / 7.5 MHz rms (burst /
  sustained) over its 33 kinds, and **10.6 / 8.4 MHz** over the kinds below 800 MHz, post hoc (E83 README,
  Results 1 and rule S1). The scoring interval is built in three steps:
  1. take the clock at the two ends of the amended (a) interval;
  2. widen each side, in quadrature, by 1.96 × 10.6 MHz (burst) or 8.4 MHz (sustained);
  3. clamp to the relation's [600, 800] MHz.

  A burst whose whole range sits at the 800 MHz cap stays [800, 800], since E83's cells at the cap read 800.0. The
  interval leaves out the step from aifoundry3's D to aifoundry2's power, beyond E83's conversion.
- **(E91)** is the amended (a) interval divided by E82's per-type scale. It still leaves out the card-scale spread:
  E82's per-kind ratios have an IQR of 1.025–1.034 over 32 kinds, and X3 failed.

**The intervals to score against** (`amendment-1.json` `tiles.<key>`; the frozen ones beside them):

| tile | (a) D [frozen] | **(a) scoring 95%** | **(E91) scoring** | (b) burst [D-propagated, frozen] | **(b) burst scoring** | (b) sustained [D-propagated, frozen] | **(b) sustained scoring** | real ÷ ref, model vs model |
|---|---|---|---|---|---|---|---|---|
| fp32 `l0_mlp_up` | 24.462 [22.27, 26.66] | **[22.05, 26.88]** | [21.41, 26.09] | 710.7 [691.8, 730.0] | **[681.3, 740.5]** | 602.5 [600.2, 611.1] | **[600.0, 621.7]** | 0.993 of randn |
| fp32 `l6_mlp_down` | 24.373 [22.18, 26.57] | **[21.96, 26.79]** | [21.32, 26.01] | 711.5 [692.6, 730.8] | **[682.1, 741.3]** | 602.7 [600.3, 611.7] | **[600.0, 622.1]** | 0.989 |
| fp32 `l6_attn_qk` | 24.461 [22.27, 26.66] | **[22.05, 26.87]** | [21.41, 26.09] | 710.7 [691.8, 730.0] | **[681.3, 740.5]** | 602.5 [600.2, 611.1] | **[600.0, 621.7]** | 0.993 |
| fp16 `l0_mlp_up` | 21.714 [19.91, 23.52] | **[19.36, 24.07]** | [18.74, 23.29] | 735.6 [719.3, 753.4] | **[706.0, 767.0]** | 615.0 [605.3, 629.9] | **[600.0, 641.0]** | 0.999 of randn |
| fp16 `l6_mlp_down` | 21.357 [19.55, 23.16] | **[19.01, 23.71]** | [18.39, 22.95] | 738.9 [722.4, 757.1] | **[709.2, 770.7]** | 617.6 [606.8, 633.3] | **[600.0, 644.4]** | 0.982 |
| fp16 `l6_attn_qk` | 21.537 [19.73, 23.34] | **[19.19, 23.89]** | [18.57, 23.12] | 737.2 [720.8, 755.2] | **[707.6, 768.8]** | 616.2 [606.0, 631.5] | **[600.0, 642.7]** | 0.990 |
| int8 `l0_mlp_up` | 5.890 [5.00, 6.78] | **[4.57, 7.21]** | [4.45, 7.02] | 800.0 [800, 800] | **[800, 800]** | 796.2 [788.7, 799.2] | **[775.3, 800.0]** | 0.837 of full |
| int8 `l6_mlp_down` | 5.183 [4.30, 6.07] | **[3.86, 6.50]** | [3.76, 6.33] | 800.0 [800, 800] | **[800, 800]** | 798.9 [795.1, 799.9] | **[780.9, 800.0]** | 0.736 |
| int8 `l6_attn_qk` | 5.749 [4.86, 6.64] | **[4.43, 7.07]** | [4.31, 6.88] | 800.0 [800, 800] | **[800, 800]** | 797.0 [790.3, 799.4] | **[776.7, 800.0]** | 0.817 |

**How E86, E87 and E91 use it:**
- cite both files by sha256 in their pre-registrations;
- score against the bold intervals, and report beside them where their data fall against the frozen ones;
- set their own decision rules.

Absolute D carries E78's session, and the model's own fp16 `randn` fit is 0.42 W low. So the verification also
recommends running E78's `randn` (fp32, fp16), `full` (int8) and `ones` in the same session as anchors, with a ratio
arm: measured real ÷ measured reference against the last column.

**What else changed in this README** (every change is listed here):
- Results 1 said "on every statistic the gate and the operand bus see". It now says the gate and the total bus count,
  and names the sign and exponent fields that differ.
- Results 2 and the int8 bullet said "as a deployment does it". They now say one simple calibration, with the range
  over four others.
- "In words" compared predictions with measured `randn` ("about 1% below", wrong for fp16). It now compares like with
  like.
- § (a) said `N` "is why" sorting saves only 5–7%. It now calls the model a post-hoc fit, gives its terms, notes that
  it prices B flips at 0 against E65, and states E78-R3e's model-free result.
- D's scope is stated, and the (b) brackets are named D-propagated ranges.
- "The windows' zero-word fractions equal the whole matrices'" was false for int8. Corrected.
- The int8 `l6_attn_qk` window's place in the causal mask is disclosed.
- Caveat 2 called the LOO rms "the honest measure". Struck.
- Caveat 5 said token 0 is not an outlier. It is one.
- Departure 8 (a flag and a metric narrowed after the first run) and Departure 9 (the build that made the files) are
  new.
- `make_real.py`'s PEP 723 header now pins `numpy==1.26.4` and Python < 3.13. No line of code changed.

## What is frozen, and how

**What D is:** board power, as E78 measured it with the board meter. E78's rail D, the minion rail deconvolved, is
0.80–0.87× of it. D is taken over the type's own zeros, at E78's primary leakage slope (auto, 0.1994 W/°C). E78's
registered leakage arms move random data's D by about ±0.6 W: fp32 `randn` is 25.344 / 24.725 / 24.163 W at k = 0 /
0.199 / 0.380 (E78 README, Results 1 and C5). E86 must compute D the same way.

**(a) D on aifoundry3 at 600 MHz: a predictor fitted on E78's 51 measured kinds only** (`e78.json`
`items.<type>.<kind>.D.mean`, with E78's committed tiles; sha256 checked). The predictor is set per type:

- `D = Σ βᵢ xᵢ`, with every β ≥ 0 (exact non-negative least squares) and no intercept, so zeros predict 0.
- The x are read from the tile's own issue stream and gate (`make_real.py` `features()`):
  - `u`: the ungated share of column-slot-cycles.
  - `A`, `B`: operand-bus bit flips that land on ungated slots.
  - `N`: ungated slot-cycles whose operand pair changed.
  - `Vs`, `Vp`: the same slot-cycles weighted by the operands' element widths (significant mantissa bits, or the
    popcount of |x| in int8), summed or multiplied.
- Eleven candidate feature sets (`CANDIDATES`) were drawn up on E78's data alone, before any real tile existed. Before
  them, the lane fitted five OLS models to E78 in its scratch, so the search was wider than the list. The set with the
  lowest leave-one-kind-out (LOO) rms on E78 is used.
- The frozen interval is point ± t(0.975, n − p) × LOO rms, with p the number of non-zero terms. That LOO rms belongs
  to the set chosen for having the lowest one, so it is biased low. Amendment 1 scores with the nested LOO rms
  instead.

| type | selected terms | β (W per unit) | rms in sample | LOO rms (worst) | frozen 95% half-width | nested LOO rms → scoring half-width |
|---|---|---|---|---|---|---|
| fp32 (18 kinds) | u, N, A, Vs (B dropped at 0) | 8.287, 1.382, 1.816, 0.310 | 0.757 W | 1.023 W (2.57, `pow2`) | ±2.19 W | **1.125 W → ±2.41 W** |
| fp16 (17 kinds) | u, N, A, Vs (B dropped at 0) | 8.415, 1.386, 2.687, 0.016 | 0.704 W | 0.835 W (2.26, `uniform01`) | ±1.80 W | **1.089 W → ±2.35 W** |
| int8 (16 kinds) | u, N, A, Vp (B dropped at 0) | 1.591, 0.289, 0.452, 0.397 | 0.328 W | 0.407 W (0.79, `pos`) | ±0.89 W | **0.606 W → ±1.32 W** |

([`predictions-real.json`](predictions-real.json) `predictor.per_type.<type>`, with every candidate's LOO residuals;
the nested column from [`amendment-1.json`](amendment-1.json) `nested_loo`.) Flips alone (u, A, B) give LOO
1.55 / 1.41 / 0.61 W.

**This is a post-hoc fit, not a mechanism.** It was chosen on the same 16–18 points per type that it is scored on. It
splits the cost above a constant lane level (`u`) into three terms: a per-change term (`N`), a per-flipped-A-bit term
(`A`) and a width term (`Vs` or `Vp`). On `randn` they are:
- fp32: 8.29 + 5.66 + 5.12 + 5.58 W;
- fp16: 8.42 + 5.68 + 7.42 + 0.23 W, where the A-side flips weigh more than `N`

(`amendment-1.json` `model_terms_on_reference_kinds`). The fit prices B-side flips at exactly 0 in all three types.
E65 contradicts that: it measured each flipped B bit on silicon at 83–1,008 fJ
([`05-claims.md`](../../../../docs/findings/05-claims.md), the E65 section). The model-free fact is E78-R3e's: the same
words, sorted to change least, move 23–27% fewer operand bits but cost only 5.4% / 6.4% / 6.6% less (E78 README,
Results 2). `u`'s coefficient lands near the constant's level: 8.3 / 8.4 / 1.6 W against E78's `ones` at
8.26 / 8.45 / 1.56 W.

**Extrapolation:** every real tile's features with β > 0 lie inside E78's range for its type, except one: fp32
`l6_mlp_down`'s `Vs` is 18.078 against E78's maximum of 18.062, 0.09% outside (flagged in
`features_outside_e78_range`). B, priced at 0, also lies outside on two tiles:
- fp32 `l6_attn_qk`: 5.670 against E78's maximum of 5.637 (+0.59%);
- int8 `l6_attn_qk`: 0.418 against 0.4158 (+0.53%).

(`amendment-1.json` `model_columns_outside_e78_range`.) With β_B = 0, B cannot move these predictions, but β_B = 0 is
the very extrapolation E65 argues against. The first run with real tiles checked every model column; the check was
narrowed before the committed run (Departure 8).

**(b) The clock on aifoundry2: E83's registered relation**
([`../../kspeed/e83/predictions.json`](../../kspeed/e83/predictions.json), sha256 `97f58c89…`). It is the dither at
an effective cap on E64's registered power curve, fitted on E80's 18 kinds: burst W* 66.15 W, σ 2.75 W; sustained
W* 49.75 W, σ 1.95 W. It is applied to (a) through the conversion E83 used: `c = c_E64(type, zeros) + D / (0.5218 /
0.517)²` (c_E64 zeros 1.440 / 1.394 / 2.123 W, from Q130(c)'s `predictions.json`). **The stored `burst_mhz_pi95` and
`sus_mhz_pi95` are D-propagated ranges, not 95% prediction intervals**: the clock at the two ends of (a)'s frozen
interval. They leave out the relation's own error, which E83 measured. Amendment 1's scoring intervals add it. The
limit labels and the rates (TFLOPS / TOPS) come from E83's own code.

**(E91) aifoundry1 card 1:** (a) divided by E82's per-type card scale, D(aifoundry3) / D(card 1) = 1.0300 / 1.0332
/ 1.0271 (E82 `scored.json` `cross_card.primary.x3.per_type_median`). This is a labelled arm. E82 found the one scale
approximate (χ² p ≈ 0.002), so a few kinds sit 1–2% off it. Its interval leaves out the card-scale spread: E82's
per-kind ratios have an IQR of 1.025–1.034 over 32 kinds.

E86, E87 and E91 should cite `predictions-real.json` and `amendment-1.json` by their sha256 in their own
pre-registrations. They score against Amendment 1's intervals, report the frozen ones' outcome beside them, and set
their own decision rules.

## How the tiles were made

- **Model:** GPT-2 small, Hugging Face `openai-community/gpt2` at revision
  `607a30d783dfa663caf39e06633721c8d4cfcd7e` (MIT licence).
  - File: `model.safetensors`, 548,105,171 bytes, sha256 `248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707`,
    which is the Hub's own LFS oid for the file.
  - `vocab.json` and `merges.txt` come from the same revision (sha256 and git blob ids in `real.json` `tokenizer`).
  - The model file is not committed.
- **Parsing and forward pass:** the safetensors file is parsed with numpy alone. The forward pass is float32 numpy:
  wte + wpe, then per block ln_1, causal attention, residual, ln_2, c_fc, GELU (GPT-2's tanh form), c_proj and
  residual; then ln_f and the tied unembedding.
- **Forward check:** on the text's first 128 tokens the next-token loss is **3.046 nats** (perplexity 21.0, top-1
  38.6%), the loss of a working language model (`forward_check`).
- **Text:** the opening paragraphs of Jane Austen's *Pride and Prejudice* (1813, public domain), ASCII straight
  quotes. The exact characters and their sha256 are in `real.json` `text`, with the token ids. It gives 205 tokens, of
  which the first 128 are used.
- **The three products:**
  - `l0_mlp_up`: layer 0's MLP up-projection. A is ln_2's output (128 × 768); B is `h.0.mlp.c_fc.weight`
    (768 × 3072).
  - `l6_mlp_down`: layer 6's MLP down-projection. A is the GELU output (128 × 3072); B is `h.6.mlp.c_proj.weight`
    (3072 × 768).
  - `l6_attn_qk`: layer 6's attention scores. A is the queries (128 × 768); B is the keys transposed (768 × 128).
    The 1/√64 scale is applied after the product, and an aligned K block always lies inside one head.
    - **The int8 window lies wholly in the causally masked triangle.** It pairs query rows 48–63 with key columns
      80–95, so every key comes after every query. A causal attention kernel never computes this block, though a
      dense QK^T GEMM does. Its operands are still real q and k.
    - The fp32 window (keys 0–15 against queries 48–63) and the fp16 one (keys 32–47 against queries 64–79) lie
      below the diagonal.
- **Types:**
  - fp32: as computed.
  - fp16: IEEE round-to-nearest-even of the fp32 values (an fp16 deployment would compute its activations in fp16;
    this is the approximation).
  - int8: symmetric with zero point 0, one simple calibration (Results 2 gives the spread over four others). Weights
    are scaled per output channel, scale_j = max|W[:, j]| / 127. Activations are scaled per tensor, scale = max|x| / 127
    over this text's 128 tokens. Rounding is half to even, clipped to ±127. The scales are in
    `tiles.int8.<name>.quantisation`: activation scales 0.0211 (ln_2), 0.0364 (GELU), 0.0759 (q) and 0.1233 (k).
- **Cutting:** A is 16 rows × K and B is K × 16 columns, with K = 16 / 32 / 64 for fp32 / fp16 / int8 (int8's K = 64
  is the TIMA path). The same k range is used for A and B, in aligned blocks, as a blocked GEMM feeds them. The tiles
  are written by `make_kinds.encode()`, and each is checked to decode back to its intended elements through
  `make_kinds.decode()`.
- **Choosing windows:** for each product and type, 20 distinct aligned windows are drawn with a seed. For each,
  `tile_stats()` gives the gated fraction, the zero-word fraction per side, the stream-order Hamming distance per field
  per side, and bus bits per op. The window nearest the 20-window median (Σ |x − median| / MAD) is taken.
  - All 20 are recorded with their statistics and predicted D (`window_choice`), together with each window's
    per-bit one-probability against the whole matrix's (`p1_elem_mad_vs_whole`).
  - No chosen window has a zero word on either side. The whole matrices have none in fp32 and fp16, and at most 6e-5
    in int8: `l0_mlp_up` B 8e-6; `l6_mlp_down` A 3.1e-5, B 5.8e-5; `l6_attn_qk` B 4.1e-5
    (`whole_matrix.<side>.zero_word_frac`). A 256-word tile side would hold about 0.01 of them.
  - Their per-bit one-probabilities lie within 0.005–0.040 (mean absolute deviation) of the whole matrix's.

## Departures and caveats

1. **The E78 data directory** named in this lane's brief, `2026-10-31-e78-kinds-of-numbers`, does not exist. E78's
   data is [`docs/reports/data/2026-10-31-e78-kinds-energy-matrix/`](../../../../docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md),
   used here by sha256.
2. **The predictor's candidate list was drawn up by this lane** on E78's data before any real tile was cut, after five
   OLS models tried in its scratch. No real tile informed it. It is a post-hoc model of E78, offered as a prediction
   for new tiles. Its LOO rms is biased low, because the set was chosen by it. The nested LOO rms (Amendment 1) is the
   fairer measure of how it does on kinds it was not fitted to, though it still leaves out the five earlier models.
   The real tiles look like E78's random-like kinds in every feature with β > 0.
3. **fp16 activations are rounded from fp32**, not computed by an fp16 forward pass.
4. **The int8 activation scale is max-abs over this text.** A deployment calibrated on more text, or by a
   percentile, would choose a different scale and so different integers. A larger scale gives smaller integers and
   more zeros. Four other common calibrations give D at 0.735–0.869× of `full` (`amendment-1.json`
   `calibration_sensitivity`).
5. **One window starts at token 0** (fp16 and int8 `l0_mlp_up`), and the median rule picked it. **Token 0 is an
   outlier** in layer 0's ln_2 output.
   - It holds the whole tensor's largest |x|, 2.681 (dimension 674), against at most 1.961 over tokens 1–127.
   - So it sets the per-tensor int8 activation scale (0.0211 = 2.681 / 127) for all 128 tokens, not only for this
     window.
   - With token 0 left out of the calibration, int8 `l0_mlp_up` is predicted at 6.02 W, not 5.89 W.

   (`amendment-1.json` `calibration_sensitivity.activation_max_abs` and `.products.l0_mlp_up`. Corrected after
   verification: `7d5b99af` said token 0 was not an outlier.)
6. **(b) inherits E83's caveats.** E83 measured its heat path moving within the day (its arm a-adj). (b) uses E83's
   registered W* without that adjustment, as E83's own prediction (a) did.
7. **As for every kind**, a `--values file:` run prints the discarded random fill's metadata and checks no
   arithmetic (`../README.md` § 1.5). The critic also suggested a ResNet-50 conv layer after ReLU (exact zeros); it
   is not in this lane's brief and is not here.
8. **The extrapolation flag and the nearest-kind metric were narrowed after the first run with real tiles** (changed
   at 18:36 PDT, disclosed at ~19:15).
   - The first run (18:35:06) checked every column of the model and z-scored every column for the nearest kind. The
     committed run (18:36:40) uses only the terms with β > 0 for both.
   - That dropped the two B flags (§ Extrapolation) and moved four labels: fp32 `l6_mlp_down` randn_small →
     uniform01, fp16 `l6_mlp_down` randn → uniform01, int8 `l6_mlp_down` ternary → sparse50, int8 `l6_attn_qk`
     gauss_q → sparse50.
   - No D, interval or clock changed. `amendment-1.json` `tiles.<key>.nearest_e78_kind` gives both labels per tile,
     and the all-column metric reproduces the first run's labels.
9. **The build that made the files** (disclosed at ~19:15). They were made with numpy 1.26.4, using its bundled
   OpenBLAS 0.3.23.dev, on CPython 3.11.13 (x86_64 macOS). § Reproduce gives what another build changes.

## Run one on a card, or reproduce

```bash
sparsity_host --test fma --type int8 --values file:tools/claims-v3/kinds/real/tiles/int8/l6_mlp_down.bin
# fetch the three files by the URLs in real.json (model, tokenizer), check their sha256, then (~15 s each, numpy only):
uv run --python 3.11 tools/claims-v3/kinds/real/make_real.py --hf-dir <dir with model.safetensors, vocab.json, merges.txt> --out <dir>
uv run --python 3.11 tools/claims-v3/kinds/real/amend_real.py --hf-dir <same dir> --out <dir>
```

On the build that made them, a re-run reproduces all eleven committed files byte for byte; `make_real.py`'s header
pins that numpy. On another BLAS, the three int8 tiles still reproduce byte for byte, but the six fp32/fp16 tiles
differ in low-order mantissa bits, and D moves by at most 0.035 W. A window choice can flip:
- fp16 `l0_mlp_up` flips on both other builds tried, because its best and second-best distances are 3.336 and 3.353;
- fp32 `l6_mlp_down` flips on Accelerate.

([`rebuild-check.txt`](rebuild-check.txt).) The committed sha256s are authoritative.

## Files

| path | what |
|---|---|
| `make_real.py` | the whole pipeline: safetensors, tokenizer, forward pass, quantisation, windows, tiles, predictor, predictions |
| `real.json` | provenance (model, tokenizer, text, forward check, frozen inputs by sha256), per matrix its fp32 statistics, per tile its file, sha256 (whole, A, B), window, quantisation, `make_kinds` statistics, the whole matrix's statistics, the 20 candidate windows, the predictor features; and the predictions |
| `predictions-real.json` | the frozen predictions alone: the predictor (every candidate and its LOO residuals), E83's relation and conversion, E82's scales, per tile (a), (E91) and (b) |
| `amend_real.py` | Amendment 1's computation, from committed files only (the nested LOO, the scoring intervals, like-with-like ratios, the column checks, and the int8 calibration sensitivity when given `--hf-dir`) |
| `amendment-1.json` | Amendment 1: per type the nested LOO; per tile the scoring intervals for (a), (E91) and (b) beside the frozen ones, the like-with-like ratios, the runner-up model's points, both nearest-kind labels; the model's terms on the reference kinds; the int8 calibration sensitivity |
| `rebuild-check.txt` | `make_real.py` re-run on three numpy builds against the committed files |
| `tiles/<type>/<name>.bin` | 2,048 bytes: the A tile then the B tile, 1,024 bytes each, in that type's layout |

| tile | sha256 |
|---|---|
| `tiles/fp32/l0_mlp_up.bin` | `6d592ffe2d7854bb4e26dd28d61f80d734152acfd12b9e64df2ef10884bfdfb6` |
| `tiles/fp32/l6_mlp_down.bin` | `fa0270cb9480245c16fd3ebd1826fd98826face2f4db0f991697aa04a3914acd` |
| `tiles/fp32/l6_attn_qk.bin` | `3bfdf870e6f96347f111ad6cf921486dc72fee880c7fc1b1a9db0088cbab171c` |
| `tiles/fp16/l0_mlp_up.bin` | `521996390983cb6e52c62de7d2b3c2584956dc216867cbe373df4a67459f3e28` |
| `tiles/fp16/l6_mlp_down.bin` | `193c36e9ef5b3bedae7ffc9f9cf30ad84743306a7bd1a1b7dd753dc1bf65b90a` |
| `tiles/fp16/l6_attn_qk.bin` | `b3b4644304f0870637a4e4a5515e35d46f4c008a7f536a773152150fc5974596` |
| `tiles/int8/l0_mlp_up.bin` | `2734a6f44f485d6b129801effa750dba5678822690eade70f51562df3dd7f52f` |
| `tiles/int8/l6_mlp_down.bin` | `3af027ef38e00cce862b16e79f7778bd5384da93164539621790fef1d1a03558` |
| `tiles/int8/l6_attn_qk.bin` | `50879e493c403d90bf8d9fc42e70e8e653eb4d789dadb3f40a5c2342438ff4fe` |
