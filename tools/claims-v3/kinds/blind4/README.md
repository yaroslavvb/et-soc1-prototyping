# Q137(m) blind pool 4

Mon 2 Nov 2026 (week 45). **Q137(m) blind pool 4, written by an independent designer who never saw the model.**

25 operand tile pairs: 11 fp32, 7 fp16, 7 int8; 20 priority 1 and 5 priority 2. Each is 2,048 bytes, raw A
(1,024 B) then raw B (1,024 B) in the type's layout, packed with `make_kinds.encode` (or `make_kinds.from_words`
for `fp16.wideexp_gate30`, which is defined on bit patterns), and described by `make_kinds.tile_stats` in
`blind4.json`. Layout, stream order and gate rule are those of `../README.md`; nothing here changes them.

```bash
python3 tools/claims-v3/kinds/blind4/make_blind4.py            # writes tiles/, blind4.json, SHA256SUMS
python3 tools/claims-v3/kinds/blind4/make_blind4.py --check    # rebuilds in memory and compares with disk
sparsity_host --test fma --type fp32 --values file:tools/claims-v3/kinds/blind4/tiles/fp32/fp32.cancel_pairs.bin
```

numpy only. The real-model tiles read the small cuts in `real/`; no model file is needed to rebuild.

## Tiles

`gated` = share of the 4,096 column-slot-cycles of one accumulate op that are gated. `bits/op` = operand bits
the input bus flips in one op under `make_kinds`' stream and convention (for int8 that figure is provisional,
as `../README.md` 1.2 says). `sha12` = first 12 hex digits of the whole file's sha256. Case numbers: 1 signs on
moving sums, 2 spread exponents under a gate, 3 A with a busy partner, 4 partial sparsity, 5 real model,
own = the designer's own choice, picked to surprise a model of bit flips and gating.

| tile | case | rule | gated | bits/op | prio | sha12 |
|---|---|---|---|---|---|---|
| `fp32.cancel_pairs` | 1 | randn; A[i][2m+1] = A[i][2m] and B[2m+1][j] = -B[2m][j], so every k-pair adds exactly zero to C | 0.0% | 84,098 | 1 | `38905a312c3c` |
| `fp32.sign_drift` | 1 | abs(randn) with one random sign s_k per k shared by A column k and B line k: every product positive, C only grows | 0.0% | 83,806 | 1 | `a9c610d263ad` |
| `fp32.wideexp_bgate_alt` | 2 | random sign, exponent 2^-120..2^120, random mantissa; B columns 8-15 all +0.0, so every lane alternates a wide-exponent word with zero each cycle (half the slots gated) | 50.0% | 99,072 | 1 | `7e6c0df7fd94` |
| `fp32.wideexp_agate_rows` | 2 | wide-exponent words (2^-120..2^120) both sides; A rows 2,5,8,11,14 all zero (whole micro-ops gated) and 20% of B words zero at random | 45.5% | 96,254 | 2 | `32802fd28115` |
| `fp32.denormals_only` | own | every word an fp32 subnormal: exponent field 0, random nonzero 23-bit mantissa, random sign; no word is zero so nothing gates, but a flush-to-zero datapath sees only zeros | 0.0% | 73,832 | 1 | `180d6dcbfe85` |
| `fp32.a_const_b_busy` | 3 | A every element 1.5 (0x3FC00000, A never changes), B standard normal | 0.0% | 55,654 | 1 | `135c07a4ba6d` |
| `fp32.a_exp_busy_b_const` | 3 | A = random sign * 2^U{-60..60}, mantissa 0 (only sign and exponent fields move); B every element 0.75 | 0.0% | 9,216 | 2 | `8f1e8d18c620` |
| `fp32.b_3of8_k` | 4 | A randn dense; B randn with N:M sparsity 3:8 along k: in each column, 3 of every 8 k-lines nonzero (62.5% of B words zero) | 62.5% | 71,752 | 1 | `382bf54aec89` |
| `fp32.rowcol_sparse` | 4 | randn; A rows 1,4,7,10,13 zero (31.25%); B columns 2 and 10 zero (lane 2 gated on both half-passes) and column 5 zero (its partner 13 is not) | 44.1% | 84,424 | 2 | `be6c635b1887` |
| `fp32.real_pythia_embed_qkv` | 5 | pythia-70m: A = token embeddings (rows 100-115, dims 0-15), B = layer-2 query_key_value weight W[0:16, 0:16] transposed (head 0's query rows); fp16 source values, exact in fp32 | 0.0% | 43,432 | 1 | `964235353646` |
| `fp32.real_qwen_q_down` | 5 | Qwen2.5-0.5B: A = layer-12 q_proj weight rows 128-143, cols 0-15; B = layer-0 mlp.down_proj W[0:16, 2048:2064] transposed; bf16 source values, exact in fp32 (low 16 mantissa bits zero) | 0.0% | 35,784 | 1 | `67cb6ae7071a` |
| `fp16.pair_cancel` | 1 | randn; both halves of every A word equal (a1 = a2) and B[2w+1][j] = -B[2w][j]: every two-term update a1*b1 + a2*b2 is exactly zero, yet no lane gates and no update is dropped | 0.0% | 83,260 | 1 | `91f083767c5d` |
| `fp16.wideexp_gate30` | 2 | fp16 bit patterns: random sign, exponent field uniform 1..30 (2^-14..2^15) with 10% subnormals, random mantissa; 30% of the 32-bit words zeroed on each side | 51.1% | 88,088 | 1 | `2725d137d967` |
| `fp16.a_hi_busy_lo_const` | 3 | A: even k (the low half of each word) = 1.0, odd k (the high half) randn; B randn | 0.0% | 70,660 | 1 | `bfed38b292a3` |
| `fp16.block_sparse_37` | 4 | randn; the 16x16 word grid in 4x4-word blocks: 6 of B's 16 blocks zero (37.5%), 3 of A's (18.75%) | 50.0% | 80,054 | 1 | `940a43740f64` |
| `fp16.band_local` | 4 | randn; A word (i, w) nonzero only where abs(i - w) <= 1 (46 of 256), B word (p, j) only where abs(p - j) <= 3 (100 of 256): local-attention bands on both sides | 92.9% | 60,016 | 2 | `c64ec8524f7e` |
| `fp16.real_pythia_embed_qkv` | 5 | pythia-70m: A = token embeddings rows 200-215, dims 64-95; B = layer-2 query_key_value W[512:528, 64:96] transposed (GPT-NeoX interleaves q,k,v per head: these are head 2's value rows); fp16 source values, stored exactly | 0.0% | 88,394 | 1 | `ea1bcc457b9e` |
| `fp16.real_qwen_ln_down` | 5 | Qwen2.5-0.5B: A = layer-12 input_layernorm gains 0-511 laid out 16x32 (values near 1, a few up to 6.7); B = layer-0 mlp.down_proj W[400:416, 300:332] transposed; bf16 rounded to fp16 (nearest-even) | 0.0% | 69,474 | 1 | `ad684a5b644e` |
| `int8.sign_runs_i` | 1 | magnitudes 1..20 (abs(round(6*randn)), zeros bumped to 1); A sign constant down each A column for runs of 8 rows (i 0-7, 8-15), random per run and k; B uniform -128..127 | 0.0% | 37,782 | 1 | `45bd65fd4ffe` |
| `int8.a_full_b_const` | 3 | A uniform -128..127; B every byte 0x5A (+90): B nonzero and never changing | 0.0% | 65,760 | 1 | `c473960fef0c` |
| `int8.pair_gate_37` | 4 | A uniform -128..127 dense; B uniform with column pairs (1,9), (4,12), (6,14) all zero (exactly 3/8 of int8's gate decisions off) and column 3 zero alone (its partner 11 live, so it never gates) | 37.5% | 69,254 | 1 | `cd58e75e0bd1` |
| `int8.band_a` | 4 | A uniform -128..127 only in words (i, w) with abs(i - w) <= 2 (74 of 256), else zero; B 2:4 byte sparsity (two random bytes of every 4-byte word zero), which never gates in int8 | 71.1% | 25,550 | 2 | `3560b8d907c3` |
| `int8.b_line_flipflop` | own | A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0xFF = -1 (odd k-groups): at every line boundary all 512 B bits flip at once | 50.0% | 73,760 | 1 | `0f0a7429de02` |
| `int8.real_pythia_embed_mlpout` | 5 | pythia-70m: A = token embeddings rows 40-55, dims 128-191, symmetric int8 with a per-cut scale max(abs(cut))/127; B = layer-4 mlp.dense_4h_to_h W[32:48, 1000:1064] transposed, symmetric per-tensor (scale max(abs(W))/127 over the whole tensor) | 0.0% | 67,094 | 1 | `a95314aa8da3` |
| `int8.real_qwen_q_down` | 5 | Qwen2.5-0.5B: A = layer-12 q_proj rows 700-715, cols 64-127; B = layer-0 mlp.down_proj W[100:116, 4000:4064] transposed; each symmetric per-tensor int8 (scale max(abs(W))/127 over its whole tensor) | 0.0% | 65,752 | 1 | `9d3841187aa9` |

### What each case is probing

1. **Signs on moving sums.** `fp32.cancel_pairs` and `fp16.pair_cancel` have randn-like operand bits but an
   accumulator that returns to the same value every k-pair (fp16: every two-term update is exactly zero, yet
   nothing gates and nothing is dropped). `fp32.sign_drift` has the same magnitudes with every product positive,
   so C grows all op long and the sign field barely moves. `int8.sign_runs_i` holds the sign down each A column
   for eight rows, which in int8's A-every-cycle stream removes most sign-extension flips.
2. **Spread exponents under a gate.** fp32 words with exponents over 2^-120..2^120 next to zeros: `wideexp_bgate_alt`
   makes every lane alternate between a wide word and zero each cycle; `wideexp_agate_rows` gates whole
   micro-ops by A rows plus 20% random B words. `fp16.wideexp_gate30` covers fp16's whole exponent field,
   subnormals included, with 30% word gating on each side.
3. **A with a busy partner.** A quiet against B busy (`fp32.a_const_b_busy`), A busy only in sign and exponent
   against a constant B (`fp32.a_exp_busy_b_const`), only the high half of each fp16 A word busy
   (`fp16.a_hi_busy_lo_const`), and int8 A full range against a constant nonzero B (`int8.a_full_b_const`).
4. **Partial sparsity.** 3:8 N:M along k (fp32), row and column zeros with one unpaired column (fp32), 4x4-word
   blocks at 37.5% / 18.75% (fp16), local bands on both sides (fp16), int8 column-pair zeros at exactly 3/8 with
   one unpaired zero column, and an int8 A band with 2:4 byte sparsity on B (which never gates in int8).
5. **Real models other than GPT-2**: pythia-70m and Qwen2.5-0.5B, below.

Own choice: `fp32.denormals_only` (every word a nonzero subnormal: nothing gates and the bits are as busy as
randn's mantissa, but a flush-to-zero datapath multiplies zeros) and `int8.b_line_flipflop` (B lines alternate
all 0x00 and all 0xFF, so half the k-groups are fully gated and every line boundary flips all 512 B bits at once).

## Provenance of the real tiles

Two public models, fetched from huggingface.co by HTTP range requests on `model.safetensors` at a pinned
commit (only the safetensors header and the bytes of the tensors used; about 15 MB in all, never the whole file):

| model | repo | revision (commit) | source dtype |
|---|---|---|---|
| pythia-70m | `EleutherAI/pythia-70m` | `a39f36b100fe8a5377810d56c3f4789b9c53ac42` | F16 |
| Qwen2.5-0.5B | `Qwen/Qwen2.5-0.5B` | `060db6499f32faf8b98477b0a26969ef7d8b9987` | BF16 |

The cuts are committed in `real/` as float32 `.npy` (an exact copy of each fp16 or bf16 value), with
`real/provenance.json` giving per tensor the dtype, shape, `data_offsets` (relative to the start of the data
section, as safetensors states them), the bytes fetched, their sha256 and max abs value; and per cut the tensor,
row and column ranges and whether it was transposed. Weights are torch `Linear` `[out, in]`, so a B operand
(K x 16) is `W[j0:j0+16, k0:k0+K].T`, i.e. `B[k][j] = W[j0+j][k0+k]`. A operands are token-embedding rows
(the real layer-0 input of pythia-70m), weight rows, or one LayerNorm gain vector. No activations were computed
by running a model.

| cut (`real/<cut>.npy`) | tensor | rows | cols | transposed | used by |
|---|---|---|---|---|---|
| `pythia_embed_r100_c0_16x16` | `pythia:gpt_neox.embed_in.weight` | 100-115 | 0-15 | no | `fp32.real_pythia_embed_qkv` |
| `pythia_embed_r200_c64_16x32` | `pythia:gpt_neox.embed_in.weight` | 200-215 | 64-95 | no | `fp16.real_pythia_embed_qkv` |
| `pythia_embed_r40_c128_16x64` | `pythia:gpt_neox.embed_in.weight` | 40-55 | 128-191 | no | `int8.real_pythia_embed_mlpout` |
| `pythia_mlpout_r32_c1000_16x64T` | `pythia:gpt_neox.layers.4.mlp.dense_4h_to_h.weight` | 32-47 | 1000-1063 | yes | `int8.real_pythia_embed_mlpout` |
| `pythia_qkv_r0_c0_16x16T` | `pythia:gpt_neox.layers.2.attention.query_key_value.weight` | 0-15 | 0-15 | yes | `fp32.real_pythia_embed_qkv` |
| `pythia_qkv_r512_c64_16x32T` | `pythia:gpt_neox.layers.2.attention.query_key_value.weight` | 512-527 | 64-95 | yes | `fp16.real_pythia_embed_qkv` |
| `qwen_down_r0_c2048_16x16T` | `qwen:model.layers.0.mlp.down_proj.weight` | 0-15 | 2048-2063 | yes | `fp32.real_qwen_q_down` |
| `qwen_down_r100_c4000_16x64T` | `qwen:model.layers.0.mlp.down_proj.weight` | 100-115 | 4000-4063 | yes | `int8.real_qwen_q_down` |
| `qwen_down_r400_c300_16x32T` | `qwen:model.layers.0.mlp.down_proj.weight` | 400-415 | 300-331 | yes | `fp16.real_qwen_ln_down` |
| `qwen_ln12_0_512_as16x32` | `qwen:model.layers.12.input_layernorm.weight` | 0-0 | 0-511 | no | `fp16.real_qwen_ln_down` |
| `qwen_qproj_r128_c0_16x16` | `qwen:model.layers.12.self_attn.q_proj.weight` | 128-143 | 0-15 | no | `fp32.real_qwen_q_down` |
| `qwen_qproj_r700_c64_16x64` | `qwen:model.layers.12.self_attn.q_proj.weight` | 700-715 | 64-127 | no | `int8.real_qwen_q_down` |

Rounding and quantisation:

- fp32 tiles: the source values unchanged (fp16 and bf16 both embed exactly in fp32; so pythia's fp32 words have
  their low 13 mantissa bits zero and Qwen's their low 16).
- fp16 tiles: pythia's values unchanged; Qwen's bf16 values rounded to fp16 by numpy (round to nearest even).
- int8 tiles: symmetric, `scale = max_abs / 127`, `q = clip(round_half_even(x / scale), -127, 127)`. For every
  weight cut `max_abs` is over the **whole tensor** (each weight tensor was fetched in full): pythia layer-4
  `mlp.dense_4h_to_h` 0.8583984375, Qwen layer-12 `q_proj` 0.26171875, Qwen layer-0 `down_proj` 0.310546875. The
  pythia embedding A operand uses a **per-cut** scale (max abs over its own 16x64 cut), the way activations are
  quantised dynamically; only the first 256 embedding rows were fetched, so a per-tensor scale was not available.

## Independence

The designer read only these files of this repository:

- `tools/claims-v3/kinds/README.md`
- `tools/claims-v3/kinds/make_kinds.py` (lines 1-851 of 1,158; imported, not modified)

and no other file in it: not `workloads/sparsity/host/main.cpp` (the layout was taken from the README), nothing
under `docs/`, no earlier blind pool, no `rtl-sim/` file, and no file with fit, predict, model, m4, m5, m6,
counts or loko in its name. One directory listing of `tools/claims-v3/kinds/` was taken to check that `blind4/`
was new; it showed file **names** (among them `predictions-*.json` and `fit`-like names) but no file was opened.
No model or prediction was seen.

## Files

| path | what |
|---|---|
| `make_blind4.py` | the generator, with `--check` |
| `blind4.json` | per tile: file, type, case, rule, seed, sha256 of the whole file and of each half, priority, and the full `tile_stats` |
| `tiles/<type>/<name>.bin` | the 25 tiles |
| `real/*.npy`, `real/provenance.json` | the 12 cuts the real tiles use, and where they came from |
| `SHA256SUMS` | sha256 of every file here except itself (`sha256sum -c SHA256SUMS` from this directory) |
