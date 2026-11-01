# Q130(n): real GPT-2 tensors as kinds tiles, with frozen predictions

Sat 31 Oct 2026 (week 44). **Nine 2,048-byte operand tiles cut from GPT-2 small's real layers and the activations it
produces on a public-domain text**: three matrix products × fp32, fp16 and int8, each in its type's exact layout and
stream order, written by [`make_kinds.py`](../make_kinds.py)'s own `encode()` and measured by its own `tile_stats()`.
This answers the Q130 critic's item 3 ("all 51 kinds are synthetic"). **Frozen here, before any card runs them:**
each tile's predicted switching power at 600 MHz on aifoundry3 (for E86), on aifoundry1 card 1 (for E91), and its
burst and sustained clock under aifoundry2's own governor (for E87), in
[`predictions-real.json`](predictions-real.json), sha256
**`bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941`**. Nothing here touches a card.

## Results

**1. On every statistic the gate and the operand bus see, real fp32 and fp16 data looks like random data.** No real
tile has a single zero word, so no lane is ever gated (`gated_lane_frac` 0.000 in all nine). The fp32 tiles flip
81,588–83,948 operand bits an op against `randn`'s 82,214; the fp16 tiles 81,324–84,748 against 84,416. Their
mantissas are full and their signs mixed. The GELU output's skew (most values small and negative) shows up only in the
A-side sign flips: 0.09 a step against `randn`'s 0.27 in fp32, 0.16 against 0.46 in fp16
([`real.json`](real.json) `tiles.<type>.<name>.stats`; `kinds.json` `kinds.fp32.randn.stats`).

**2. Real int8 data is not uniform random int8, and it is not sparse either.** Quantised as a deployment does it
(weights per output channel, activations per tensor), the values are small integers: over the whole matrices the
activations' standard deviation is 5–19 steps (of ±127) and the weights' 28–33 (`whole_matrix.A.sd`, `.B.sd`). 1–9%
of a tile's bytes are zero, but never four in one word, so nothing gates. The bus flips 45,684–59,716 bits an op
against `full`'s 69,312. GELU's small negatives become −1 to −5, so `l6_mlp_down`'s A half is 78.5% negative bytes
with a mean popcount of 5.6 (its B half 49%, 4.0; `stats.int8_twos_complement` gives 64% and 4.8 over both halves).

**3. The frozen predictions** (95% intervals; D = switching W over the type's own zeros, the quantity E78 measured):

| tile | window (rows, k, cols) | bus bits/op | (a) D, aifoundry3 600 MHz | nearest E78 kind (its D) | (E91) D, aifoundry1 card 1 | (b) burst MHz, aifoundry2 | (b) sustained MHz, limit |
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
every int8 kind: they rest on the reconstructed TIMA stream, `kinds.json` `facts.stream_order.int8`.)

In words: **real fp32 and fp16 numbers should cost what random numbers cost**, about 1% below `randn` (fp32 24.4–24.5
W against 24.73; fp16 21.4–21.7 against 22.16). Both lie well inside each prediction's ±2.2 / ±1.8 W. **Real int8
numbers should cost 0.73–0.83× of uniform random int8** (5.2–5.9 W against `full`'s 7.06). The saving comes from small
values and fewer flipped bits, not from the zero gate. So the speed predictions follow the power: fp32 and fp16 real
tiles burst like `randn` (≈711 / ≈737 MHz) and fall to the sustained floor (≈602 / ≈616 MHz, the thermal test), and
int8 stays at 800 MHz.

The windows were chosen to be typical, and the prediction barely depends on which window: over the 20 candidate
windows of one product the predicted D spans 0.24–0.75 W (fp32), 0.36–1.00 W (fp16) and 0.30–0.48 W (int8), at most
28% of the 95% interval's width (`a_aifoundry3_600mhz.D_band_over_20_windows_w`).

## What is frozen, and how

**(a) D on aifoundry3 at 600 MHz: a predictor fitted on E78's 51 measured kinds only** (`e78.json`
`items.<type>.<kind>.D.mean`, with E78's committed tiles; sha256 checked). The predictor is set per type:

- `D = Σ βᵢ xᵢ`, with every β ≥ 0 (exact non-negative least squares) and no intercept, so zeros predict 0.
- The x are read from the tile's own issue stream and gate (`make_real.py` `features()`):
  - `u`: the ungated share of column-slot-cycles.
  - `A`, `B`: operand-bus bit flips that land on ungated slots.
  - `N`: ungated slot-cycles whose operand pair changed.
  - `Vs`, `Vp`: the same slot-cycles weighted by the operands' element widths (significant mantissa bits, or the
    popcount of |x| in int8), summed or multiplied.
- Eleven candidate feature sets (`CANDIDATES`) were drawn up on E78's data alone, before any real tile existed. The one
  with the lowest leave-one-kind-out (LOO) rms on E78 is used.
- The interval is point ± t(0.975, n − p) × LOO rms, with p the number of non-zero terms.

| type | selected terms | β (W per unit) | rms in sample | **LOO rms** (worst) | 95% half-width |
|---|---|---|---|---|---|
| fp32 (18 kinds) | u, N, A, Vs (B dropped at 0) | 8.287, 1.382, 1.816, 0.310 | 0.757 W | **1.023 W** (2.57, `pow2`) | ±2.19 W |
| fp16 (17 kinds) | u, N, A, Vs (B dropped at 0) | 8.415, 1.386, 2.687, 0.016 | 0.704 W | **0.835 W** (2.26, `uniform01`) | ±1.80 W |
| int8 (16 kinds) | u, N, A, Vp (B dropped at 0) | 1.591, 0.289, 0.452, 0.397 | 0.328 W | **0.407 W** (0.79, `pos`) | ±0.89 W |

(`predictions-real.json` `predictor.per_type.<type>`, with every candidate's LOO residuals.) Flips alone (u, A, B)
give LOO 1.55 / 1.41 / 0.61 W. The term that helps is `N`, a cost per change whatever the number of bits. It is why
E78's sorted kinds, which flip 23–27% fewer bits, cost only 5–7% less. `u`'s coefficient is the constant's level:
8.3 / 8.4 / 1.6 W against E78's `ones` at 8.26 / 8.45 / 1.56 W.

**Extrapolation:** every real tile's used features lie inside E78's range for its type except one.
fp32 `l6_mlp_down`'s `Vs` is 18.078 against E78's maximum of 18.062, 0.09% outside (flagged in
`features_outside_e78_range`).

**(b) The clock on aifoundry2: E83's registered relation**
([`../../kspeed/e83/predictions.json`](../../kspeed/e83/predictions.json), sha256 `97f58c89…`). It is the dither at
an effective cap on E64's registered power curve, fitted on E80's 18 kinds: burst W* 66.15 W, σ 2.75 W; sustained
W* 49.75 W, σ 1.95 W. It is applied to (a) through the conversion E83 used: `c = c_E64(type, zeros) + D / (0.5218 /
0.517)²` (c_E64 zeros 1.440 / 1.394 / 2.123 W, from Q130(c)'s `predictions.json`). Its interval is the clock at the
two ends of (a)'s 95% interval. The limit labels and the rates (TFLOPS / TOPS) come from E83's own code.

**(E91) aifoundry1 card 1:** (a) divided by E82's per-type card scale, D(aifoundry3) / D(card 1) = 1.0300 / 1.0332
/ 1.0271 (E82 `scored.json` `cross_card.primary.x3.per_type_median`). This is a labelled arm: E82 found the one scale
approximate (χ² p ≈ 0.002), so a few kinds sit 1–2% off it.

E86, E87 and E91 should cite `predictions-real.json` by its sha256 in their own pre-registrations, and set their own
decision rules.

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
- **Types:**
  - fp32: as computed.
  - fp16: IEEE round-to-nearest-even of the fp32 values (an fp16 deployment would compute its activations in fp16;
    this is the approximation).
  - int8: symmetric with zero point 0. Weights are scaled per output channel, scale_j = max|W[:, j]| / 127.
    Activations are scaled per tensor, scale = max|x| / 127 over this text's 128 tokens. Rounding is half to even,
    clipped to ±127. The scales are in `tiles.int8.<name>.quantisation`: activation scales 0.0211 (ln_2), 0.0364
    (GELU), 0.0759 (q) and 0.1233 (k).
- **Cutting:** A is 16 rows × K and B is K × 16 columns, with K = 16 / 32 / 64 for fp32 / fp16 / int8 (int8's K = 64
  is the TIMA path). The same k range is used for A and B, in aligned blocks, as a blocked GEMM feeds them. The tiles
  are written by `make_kinds.encode()`, and each is checked to decode back to its intended elements through
  `make_kinds.decode()`.
- **Choosing windows:** for each product and type, 20 distinct aligned windows are drawn with a seed. For each,
  `tile_stats()` gives the gated fraction, the zero-word fraction per side, the stream-order Hamming distance per field
  per side, and bus bits per op. The window nearest the 20-window median (Σ |x − median| / MAD) is taken.
  - All 20 are recorded with their statistics and predicted D (`window_choice`), together with each window's
    per-bit one-probability against the whole matrix's (`p1_elem_mad_vs_whole`).
  - The chosen windows' zero-word fractions equal the whole matrices' (0 on both sides, in every tile).
  - Their per-bit one-probabilities lie within 0.005–0.040 (mean absolute deviation) of the whole matrix's.

## Departures and caveats

1. **The E78 data directory** named in this lane's brief, `2026-10-31-e78-kinds-of-numbers`, does not exist. E78's
   data is [`docs/reports/data/2026-10-31-e78-kinds-energy-matrix/`](../../../../docs/reports/data/2026-10-31-e78-kinds-energy-matrix/README.md),
   used here by sha256.
2. **The predictor's candidate list was drawn up by this lane** on E78's data before any real tile was cut. No real
   tile informed it. It is a post-hoc model of E78, offered as a prediction for new tiles. Its LOO rms is the honest
   measure of how it does on kinds it was not fitted to, and the real tiles look like E78's random-like kinds in every
   used feature.
3. **fp16 activations are rounded from fp32**, not computed by an fp16 forward pass.
4. **The int8 activation scale is max-abs over this text.** A deployment calibrated on more text, or by a
   percentile, would choose a different scale and so different integers. A larger scale gives smaller integers and
   more zeros.
5. **One window starts at token 0** (fp16 and int8 `l0_mlp_up`). The median rule picked it; layer 0's ln_2 output at
   token 0 is not an outlier.
6. **(b) inherits E83's caveats.** E83 measured its heat path moving within the day (its arm a-adj). (b) uses E83's
   registered W* without that adjustment, as E83's own prediction (a) did.
7. **As for every kind**, a `--values file:` run prints the discarded random fill's metadata and checks no
   arithmetic (`../README.md` § 1.5). The critic also suggested a ResNet-50 conv layer after ReLU (exact zeros); it
   is not in this lane's brief and is not here.

## Run one on a card, or reproduce

```bash
sparsity_host --test fma --type int8 --values file:tools/claims-v3/kinds/real/tiles/int8/l6_mlp_down.bin
# fetch the three files by the URLs in real.json (model, tokenizer), check their sha256, then (~15 s, numpy only):
python3 tools/claims-v3/kinds/real/make_real.py --hf-dir <dir with model.safetensors, vocab.json, merges.txt>
```

Two runs give byte-identical `real.json`, `predictions-real.json` and tiles.

## Files

| path | what |
|---|---|
| `make_real.py` | the whole pipeline: safetensors, tokenizer, forward pass, quantisation, windows, tiles, predictor, predictions |
| `real.json` | provenance (model, tokenizer, text, forward check, frozen inputs by sha256), per matrix its fp32 statistics, per tile its file, sha256 (whole, A, B), window, quantisation, `make_kinds` statistics, the whole matrix's statistics, the 20 candidate windows, the predictor features; and the predictions |
| `predictions-real.json` | the frozen predictions alone: the predictor (every candidate and its LOO residuals), E83's relation and conversion, E82's scales, per tile (a), (E91) and (b) |
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
