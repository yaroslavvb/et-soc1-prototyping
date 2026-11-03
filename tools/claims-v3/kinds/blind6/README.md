# Q139(b) blind pool 6

Tue 3 Nov 2026 (week 45). **Q139(b) blind pool 6, written by an independent designer who never saw M8** (Q139(m)'s
fit), its data directory or its scratch. It answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** ("a power
model across kinds", the blind test of M8), **item 7** (real tensors), **item 13** (zeros' transport) and **item 15**
(single bits on other base words), as Q138's final critic ranked them: **rank 2** (a refit with the terms Q138 measured
as missing, scored on a sixth blind pool on all three cards), **rank 8** (real tiles from two or more public models,
W8A8 projections and attention matmuls) and **rank 16** (items 13 and 15 folded into the pool as tiles). It also names
the four **hold candidates** for E154 and E161 (rank 4, heat end to end).

**50 operand tile pairs: 18 fp32, 13 fp16, 19 int8. 44 are new kinds and 6 are anchors, two per format.** 30 of the new
kinds are priority 1 and 14 are priority-2 tests. Every count the brief asks for is met inside priority 1 alone, so a
session that runs only priority 1 still tests every term:

| asked for | in the pool | priority 1 |
|---|---:|---:|
| new kinds (at least 30) | 44 | 30 |
| anchors, two per format (zeros, random normal; int8's random anchor is `full`) | 6 | (run in every pass) |
| exponent-heavy kinds (at least 8) | 10 | 8 |
| int8 B-position or whole-line kinds (at least 6) | 9 | 6 |
| real tiles from at least two public models (at least 8; the critic's rank 8 asks 10) | 12, from 2 models | 9 |
| item 13, zeros' transport | 4 | 3 |
| item 15, other base words | 5 | 3 |
| hold candidates for E154/E161 | 4 | 4 |

Each tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), in the type's layout. Tiles are packed with
`make_kinds.encode` (or `make_kinds.from_words` for the tiles defined on bit patterns) and described by
`make_kinds.tile_stats` in `blind6.json`. Layout, stream order and gate rule are those of `../README.md`; nothing here
changes them. Each tile also carries `bus_by_field` (its operand-bus flips split into sign, exponent and mantissa, or
int8's sign and magnitude, under the same stream and convention as `tile_stats`, which the generator asserts) and a
`c_check` (blind pool 5's, extended: below).

```bash
python3 tools/claims-v3/kinds/blind6/make_blind6.py            # writes tiles/, blind6.json, MANIFEST, SHA256SUMS (numpy only)
python3 tools/claims-v3/kinds/blind6/make_blind6.py --check    # rebuilds in memory and compares with disk
python3 tools/claims-v3/kinds/blind6/fetch_real6.py            # optional: re-fetches real/ from huggingface.co
sparsity_host --test fma --type int8 --values file:tools/claims-v3/kinds/blind6/tiles/int8/int8.real_qwen_w8a8_v.bin
```

**Names.** No pool-6 name equals any name in `kinds.json`, `real/`, `real2/` or blind pools 3-5, so a session can load
pool 6 beside E78's items and beside the pool-5 tiles E153 and E157 re-run first. The anchors are `*.anchor6_*` for
that reason. The three zero anchors are byte-identical to each other and to every earlier zero tile (2,048 zero bytes
are the same tile in every type); no other pool-6 tile shares its bytes with any earlier tile.

**`MANIFEST`** has one line per kind: the tile's sha256, its file, name, type, case, priority, `anchor` or `kind`, and
`hold` or `-`. `SHA256SUMS` covers every file here except itself (`sha256sum -c SHA256SUMS` from this directory).

## Tiles

`gated`: the share of the 4,096 column-slot-cycles of one accumulate op that are gated. `bits/op`: operand bits the
input bus flips in one op, under `make_kinds`' stream and convention (int8's figure is provisional, as `../README.md`
1.2 says). `exp`: the exponent field's share of those flips (floats). `C flips/op`: C-register bits that flip in one
op, from this pool's C emulation, at a launch's start and estimated at the end of a 0.5 s launch at 600 MHz (a
descriptor, not a measurement). `H`: a hold candidate. `sha12`: the first 12 hex digits of the whole file's sha256.

Cases: **0** an anchor; **E** exponent-heavy; **B** int8 B-position; **L** int8 whole-line or whole-word flip-flops;
**W** seeded power-law weights; **R** real model tiles; **Z** zeros' transport (item 13); **S** single bits on other
base words (item 15); **C** the C-register candidate.

| tile | case | rule | gated | bits/op | exp | C flips/op, start → end | prio | H | sha12 |
|---|---|---|---|---:|---:|---|---|---|---|
| `fp32.anchor6_zeros` | 0 | every element +0.0 (footing: the zero reference, as fp32.zeros) | 100.0% | 0 | 0.00 | 0 → 0 | anchor |  | `e5a00aa9991a` |
| `fp32.anchor6_randn` | 0 | standard normal both sides, a fresh draw (footing: as fp32.randn) | 0.0% | 85,608 | 0.13 | 49,089 → 10,300 | anchor |  | `36d9320b43de` |
| `fp32.exp_only_narrow2` | E | both sides random sign × 2^U{-2..2}, mantissa field 0: values within 1/4..4, but the exponent field runs 125..129, so every step across 1.0/2.0 (0x7F/0x80) flips all eight exponent bits; products are exact powers of two | 0.0% | 24,518 | 0.87 | 11,572 → 11,296 | 1 |  | `14ce8cc730ee` |
| `fp32.exp_b_alt_shift` | E | A every element 1.5 (never changes); B columns 0-7 random sign, random mantissa, exponent 2^U{-8..8}; column l+8 is column l times 2^d (d in +-1..12, per word): each lane's every-cycle alternation flips exponent bits only | 0.0% | 14,568 | 0.90 | 29,616 → 3,456 | 1 |  | `f6c08d00938b` |
| `fp32.exp_a_walk_fixedmant` | E | A[i][k] = (1 + m_k) × 2^e_ik, positive, one random mantissa per column k and exponent U{-20..20} per element: A's walk down each column flips exponent bits only; B random normal with columns l and l+8 equal, so the lanes never alternate and B changes only at the 16 line boundaries | 0.0% | 11,216 | 0.73 | 21,168 → 2,654 | 1 |  | `8ddb845a688d` |
| `fp32.bf16_wideexp` | E | bf16 values with spread exponents, both sides: random sign, exponent 2^U{-40..40}, 7 random mantissa bits, the low 16 bits zero: about as many exponent flips as mantissa flips | 0.0% | 49,138 | 0.50 | 5,638 → 1,323 | 1 |  | `0535bb7277cf` |
| `fp32.signexp_invert_b` | E | A every element 1.25; B columns 0-7 random sign, exponent field U{87..167}, random mantissa; column l+8 is column l with its sign and all eight exponent bits inverted (XOR 0xFF800000): every lane flips exactly 9 bits a cycle, all in sign and exponent, the mantissa held | 0.0% | 37,792 | 0.85 | 12,048 → 1,488 | 1 |  | `503400abe6da` |
| `fp32.exp_a_pow2wide_b_randn` | E | A random sign × 2^U{-30..30} (mantissa 0: only A's sign and exponent move); B standard normal (its mantissas busy): every product is one of B's mantissas, rescaled | 0.0% | 64,464 | 0.23 | 14,685 → 2,322 | 2 |  | `a88bc2c40e61` |
| `fp32.real_smol_softmax_v_causal` | R | SmolLM-135M (W8A8 checkpoint) layer 0, head 1: A = causal softmax of query tokens 0-15 x key tokens 0-15 (the diagonal block: exact zeros above the diagonal, 120 of 256 words); B = values of key tokens 0-15, head dims 0-15 | 46.9% | 73,550 | 0.14 | 25,898 → 5,645 | 1 | H | `21337776084c` |
| `fp32.real_qwen_dequant_q` | R | Qwen2.5-0.5B (W8A8 checkpoint) layer 0: A = input_layernorm output (tokens 16-31, dims 0-15, fp32); B = q_proj weights dequantised (int8 x its channel's bf16 scale, exact in fp32) rows 0-15 x dims 0-15, transposed (30 zero words) | 11.7% | 58,452 | 0.24 | 42,473 → 8,734 | 1 |  | `f33904e5a459` |
| `fp32.real_qwen_softmax_v` | R | Qwen2.5-0.5B layer 0, head 3: A = softmax of query tokens 16-31 x key tokens 0-15 (every key precedes: no masked zeros); B = values of key tokens 0-15, head dims 0-15 | 0.0% | 80,812 | 0.11 | 48,171 → 10,446 | 2 |  | `0a2e98ab65f1` |
| `fp32.a_zeros_b_complement` | Z | A every element +0.0 (every micro-op gated); B columns 0-7 random words (sign random, exponent field U{64..191}, random mantissa), column l+8 their bitwise complement: each lane's B flips all 32 bits every cycle, the most B traffic a tile can carry, all of it behind a closed gate | 100.0% | 129,036 | 0.25 | 0 → 0 | 1 |  | `6f3b15348b1f` |
| `fp32.negzero_a_b_complement` | Z | A every element -0.0 (0x80000000: a nonzero word, so no lane gates, yet every product is a zero); B as a_zeros_b_complement's rule (fresh draw): the same B traffic in live lanes that multiply zeros | 0.0% | 129,008 | 0.25 | 0 → 0 | 1 |  | `9166093f3fa7` |
| `fp32.b_onebit_b12_third` | S | A every element 1.0; B every word 1/3 (0x3EAAAAAB) with bit 12 flipped in columns 8-15: each lane flips that one mantissa bit every cycle (4,096 flips an op), on a base word no single-bit run has used | 0.0% | 4,096 | 0.00 | 58,880 → 7,936 | 1 |  | `29489c0fbc82` |
| `fp32.b_onebit_b20_third` | S | as b_onebit_b12_third with bit 20 (a high mantissa bit) flipping on every lane every cycle | 0.0% | 4,096 | 0.00 | 59,008 → 7,936 | 1 |  | `85505a89777d` |
| `fp32.a_onebit_b5_third` | S | A every word 1/3 (0x3EAAAAAB) with bit 5 set in the odd rows: each step down an A column flips that one bit (the recoded operand, a new base word); B every element 1.0 | 0.0% | 2,048 | 0.00 | 59,392 → 7,936 | 1 | H | `6d07fe951904` |
| `fp32.a_onebit_b16_half` | S | A every word 0.5 (0x3F000000, zero mantissa) with bit 16 set in the odd rows: one A bit walks on a base word with no other mantissa bit; B every element 1.0 | 0.0% | 2,048 | 0.00 | 11,776 → 7,936 | 2 |  | `872b9ba11af3` |
| `fp32.c_absorbed` | C | standard normal both sides except A's column 0 and B's line 0, every element 2^50: each op first adds 2^100 to every C element, which then absorbs the other fifteen products (ulp 2^77): operands nearly as busy as randn, C changing once an op in its low bits | 0.0% | 79,586 | 0.12 | 768 → 256 | 2 |  | `c6792446c044` |
| `fp16.anchor6_zeros` | 0 | every element +0.0 (footing: as fp16.zeros) | 100.0% | 0 | 0.00 | 0 → 0 | anchor |  | `e5a00aa9991a` |
| `fp16.anchor6_randn` | 0 | standard normal both sides, a fresh draw (footing: as fp16.randn) | 0.0% | 84,978 | 0.21 | 49,131 → 10,936 | anchor |  | `05ae2dc691e1` |
| `fp16.exp_only_narrow2` | E | fp16 random sign × 2^(e-15), exponent field e in 13..17 (1/4..4), mantissa 0, both sides: steps across 1.0/2.0 (01111/10000) flip all five exponent bits; every product a power of two | 0.0% | 36,754 | 0.83 | 14,845 → 14,004 | 1 |  | `6bfb16e16a74` |
| `fp16.exp_b_alt_shift` | E | A every element 1.5 (0x3E00); B columns 0-7 random sign, random mantissa, exponent field U{8..22}; column l+8 the same halves with the exponent field moved by d in +-1..6 (per half): each lane's alternation flips exponent bits only | 0.0% | 20,034 | 0.93 | 39,376 → 6,608 | 1 |  | `8e326bf126a9` |
| `fp16.e5m2grid_wide` | E | fp8 e5m2 values held in fp16 (the low 8 mantissa bits zero, round to nearest even), from randn × 2^U{-6..6}, both sides: 2 mantissa bits against 5 exponent bits | 0.0% | 48,556 | 0.61 | 28,080 → 4,247 | 1 |  | `c0568909bd65` |
| `fp16.exp_a_walk_fixedmant` | E | A halves (1 + m) × 2^(e-15), positive, one random mantissa per (word column, half) and exponent field U{5..25} per element: A's walk flips exponent bits only; B random normal with columns l and l+8 equal (the lanes never alternate) | 0.0% | 13,050 | 0.81 | 40,178 → 5,686 | 2 |  | `b91bcf1c5f03` |
| `fp16.real_smol_qk` | R | SmolLM-135M (W8A8 checkpoint) layer 0, head 1: A = rotary queries (tokens 16-31, head dims 0-31), B = rotary keys of KV head 0, tokens 0-15, transposed: the attention scores' matmul; fp32 values rounded to fp16 | 0.0% | 80,476 | 0.21 | 47,625 → 9,369 | 1 |  | `a144008e568f` |
| `fp16.real_smol_softmax_v` | R | SmolLM-135M layer 0, head 1: A = causal softmax (query tokens 16-31 x key tokens 0-31: exact zeros above the diagonal, 120 of 512 elements); B = values (keys 0-31, head dims 0-15); the one B value that rounds to an fp16 subnormal is written as +0.0, so C does not depend on whether the unit flushes subnormals before PRM 9.4's nonzero test | 21.9% | 80,770 | 0.24 | 35,944 → 7,882 | 1 |  | `b07a344a9047` |
| `fp16.real_qwen_qk` | R | Qwen2.5-0.5B (W8A8 checkpoint) layer 0, head 3: A = rotary queries with q_proj's bias (tokens 16-31, dims 0-31), B = rotary keys with k_proj's bias (KV head 0, tokens 0-15), transposed (keys up to 121.6) | 0.0% | 66,502 | 0.15 | 40,937 → 4,577 | 1 |  | `da9a13426327` |
| `fp16.real_qwen_dequant_v` | R | Qwen2.5-0.5B layer 0: A = input_layernorm output (tokens 16-31, dims 0-31) in fp16; B = v_proj weights dequantised (int8 x channel scale) rows 0-15 x dims 0-31, transposed, in fp16 (a W8A16 matmul) | 0.0% | 81,586 | 0.22 | 43,416 → 9,920 | 2 |  | `c1ac6a45560f` |
| `fp16.a_zeros_b_complement` | Z | A every word zero (every micro-op gated); B columns 0-7 random fp16 halves (sign random, exponent field U{1..30}, random mantissa), column l+8 their 16-bit complements: every lane's B flips all 32 bits every cycle behind the gate | 100.0% | 129,020 | 0.31 | 0 → 0 | 2 |  | `07c6f08cc915` |
| `fp16.b_onebit_b6_third` | S | A every element 1.0 (0x3C00); B every half 1/3 (0x3555) with bit 6 of each half flipped in columns 8-15: each lane flips two bits (one per half) every cycle, on a base word no fp16 single-bit run has used | 0.0% | 8,192 | 0.00 | 35,072 → 7,936 | 2 |  | `89453d7ee5e9` |
| `fp16.c_absorbed` | C | standard normal both sides (fp16) except A's columns 0-1 and B's lines 0-1, every element 2^15: each op first adds 2^31 to every C element, which then absorbs the other fifteen two-term sums (ulp 2^8 and up) | 0.0% | 78,830 | 0.20 | 256 → 256 | 2 |  | `f4b41ed786ca` |
| `int8.anchor6_zeros` | 0 | every byte 0x00 (footing: as int8.zeros) | 100.0% | 0 | — | 0 → 0 | anchor |  | `e5a00aa9991a` |
| `int8.anchor6_full` | 0 | uniform -128..127 both sides, a fresh draw (footing: as int8.full, the lab's int8 random anchor) | 0.0% | 68,600 | — | 34,932 → 34,665 | anchor |  | `df06eb01a286` |
| `int8.bheld_bit1` | B | A uniform -128..127; B every byte 0x02 (one bit set, at position 1, never changing): A's every-micro-op changes meet a B that holds one bit at one position | 0.0% | 65,376 | — | 27,312 → 25,264 | 1 |  | `c93ea4422c6c` |
| `int8.bheld_bit4` | B | as bheld_bit1 with B every byte 0x10 (bit 4) | 0.0% | 65,728 | — | 22,000 → 28,656 | 1 |  | `5449f302af2e` |
| `int8.bheld_bit7` | B | as bheld_bit1 with B every byte 0x80 (bit 7 alone: -128) | 0.0% | 65,920 | — | 24,352 → 23,808 | 1 |  | `18151e6e7d6c` |
| `int8.b_line_zero_ff` | L | A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0xFF (-1): the gate of blind 5's b_line_zero_one with all 512 B bits flipping at each boundary instead of 64 | 50.0% | 75,200 | — | 15,328 → 14,064 | 1 | H | `6a50d22072df` |
| `int8.b_line_zero_full` | L | A uniform -128..127; B lines alternate all 0x00 (even k-groups, gated) and uniform random bytes (odd) | 50.0% | 67,764 | — | 17,761 → 18,354 | 1 |  | `ee46e3c1cefc` |
| `int8.a_word_zero_one` | L | A rows alternate all 0x00 (even i, gated) and all 0x01 (+1, odd i): the A-side zero/one flip-flop, 4 bits a word changing every micro-op (blind 5's a_word_flipflop changed all 32); B uniform | 50.0% | 20,446 | — | 12,464 → 14,480 | 1 |  | `a332b69b890f` |
| `int8.b_line_55_aa` | L | A uniform -128..127; B lines alternate all 0x55 (+85) and all 0xAA (-86): every boundary flips all 512 B bits, no byte zero (blind 5's b_line_flipflop_nogate flipped 0x7F/0x80, the same count on other values) | 0.0% | 73,632 | — | 36,112 → 35,568 | 2 |  | `19d2d9fd0be5` |
| `int8.bflip_bit2_w` | B | E130's line-parity layout on a new base word: A every byte +1; B every word 0x4E3B6A19, with bit 2 of every byte flipped on the odd lines (1,024 B flips an op at one position) | 0.0% | 1,024 | — | 19,968 → 19,456 | 2 |  | `00429415886e` |
| `int8.bflip_bit5_w` | B | as bflip_bit2_w with bit 5 of every byte flipping on the odd lines | 0.0% | 1,024 | — | 19,968 → 19,712 | 2 |  | `fe60fd299320` |
| `int8.powerlaw_df4_pc` | W | power-law weights with a per-channel scale: B = W[0:64, 0:16] of a 1024x16 Student-t (df 4) tensor, int8 per output channel (max abs over its 1024 inputs / 127); A = Laplace activations quantised per token | 0.0% | 69,066 | — | 28,515 → 29,594 | 1 |  | `6567a038effa` |
| `int8.powerlaw_df15_pt` | W | heavier tails: B = W[0:64, 0:16] of a 1024x64 Student-t (df 1.5) tensor, symmetric per-tensor int8 (most bytes 0 or +-1); A = Laplace activations quantised per token | 61.7% | 64,138 | — | 4,128 → 5,984 | 2 |  | `f234359946f4` |
| `int8.real_smol_w8a8_q` | R | SmolLM-135M W8A8 layer 0, q_proj: A = input_layernorm output (tokens 16-31, dims 0-63) quantised per token (the token's max abs over all 576 dims / 127); B = the checkpoint's int8 q_proj rows 0-15 x dims 0-63, transposed | 0.0% | 65,374 | — | 23,431 → 26,856 | 1 |  | `fbea3ed0b033` |
| `int8.real_smol_w8a8_down` | R | SmolLM-135M W8A8 layer 0, down_proj: A = SiLU(gate) × up (tokens 16-31, hidden 0-63) quantised per token (max abs over all 1536 / 127); B = the checkpoint's int8 down_proj rows 0-15 x hidden 0-63, transposed | 25.0% | 59,298 | — | 17,806 → 20,158 | 1 |  | `24fe46efcb1b` |
| `int8.real_qwen_w8a8_v` | R | Qwen2.5-0.5B W8A8 layer 0, v_proj: A = input_layernorm output (tokens 16-31, dims 0-63) quantised per token (max abs over all 896 / 127); B = the checkpoint's int8 v_proj rows 0-15 x dims 0-63, transposed | 0.0% | 70,232 | — | 26,276 → 29,125 | 1 | H | `b253206379b2` |
| `int8.real_qwen_w8a8_gate` | R | Qwen2.5-0.5B W8A8 layer 0, gate_proj: A = post_attention_layernorm output after attention and the residual (tokens 16-31, dims 64-127) quantised per token; B = the checkpoint's int8 gate_proj rows 0-15 x dims 64-127, transposed | 0.0% | 68,396 | — | 28,045 → 29,917 | 1 |  | `3a31a0b62d83` |
| `int8.real_qwen_w8a8_down` | R | Qwen2.5-0.5B W8A8 layer 0, down_proj: A = SiLU(gate) × up (tokens 16-31, hidden 0-63) quantised per token (max abs over all 4864 / 127: most bytes small); B = the checkpoint's int8 down_proj rows 0-15 x hidden 0-63, transposed | 2.7% | 57,804 | — | 20,052 → 23,841 | 2 |  | `de54c13f933c` |
| `int8.a_zeros_b_lineflip` | Z | A every byte 0x00 (every micro-op gated); B lines alternate all 0x7F and all 0x80: all 512 B bits flip at every line boundary behind the closed gate (int8's zeros' transport) | 100.0% | 8,192 | — | 0 → 0 | 1 |  | `e3ae621ac9f9` |

### What each case is probing, and the pairs built in

Most new tiles have a partner in this pool, in an earlier pool or in E78's kinds that differs in one property, so a
session can score differences, which cancel the footing, as well as levels.

- **E: exponent-heavy (10; E147, rank 2's "exponent-field term").** E147 found the card paying 0.82-0.84 of the
  models' watts on single exponent flips. These tiles put most of the operand flips in the exponent field (`exp`
  0.50-0.93 on the eight priority-1 tiles, against 0.13 and 0.21 for the random anchors) in five ways:
  - **lane alternation on B alone, exponent bits only**: `fp32.exp_b_alt_shift` and `fp16.exp_b_alt_shift` (B's columns
    l and l+8 differ only by a power of two; A constant), and `fp32.signexp_invert_b` (exactly nine bits a cycle, the
    sign and the whole exponent field, the mantissa held);
  - **A's walk, exponent bits only**: `fp32.exp_a_walk_fixedmant`, `fp16.exp_a_walk_fixedmant` (one mantissa per
    column; B's lanes never alternate);
  - **powers of two across 1.0**: `fp32.exp_only_narrow2` and `fp16.exp_only_narrow2`. The values stay within 1/4..4,
    but the exponent field crosses 0x7F/0x80 (fp16: 01111/10000), so a small range of values flips the whole field.
    Against blind pool 5's `exp_only_both` (2^-40..2^40) they test whether the price follows the bits or the range;
  - **narrow mantissas, spread exponents**: `fp32.bf16_wideexp` (bf16 values at 2^-40..2^40) and `fp16.e5m2grid_wide`
    (fp8 e5m2 values held in fp16);
  - **exponent activity on A with B's mantissas busy**: `fp32.exp_a_pow2wide_b_randn` (priority 2; `exp` 0.23 on the
    bus, since B's random mantissas dominate the count; every A flip is a sign or exponent flip).
- **B: int8 B-position (5; E138, E145, rank 2's per-position B prices).** Two designs:
  - **a held B with one bit set**: `int8.bheld_bit1`, `bheld_bit4`, `bheld_bit7` (every B byte 0x02, 0x10 or 0x80;
    A uniform). B never changes, so these test which B bit position prices A's every-micro-op changes in the product
    path;
  - **E130's line-parity layout on a new base word**: `int8.bflip_bit2_w`, `bflip_bit5_w` (priority 2; A = +1, B's
    word 0x4E3B6A19 with one bit of every byte flipping on the odd lines, 1,024 flips an op at one position). Their
    signal is small on the board (E130 priced such flips in tens of fJ on the minion rail), so they are tests of a
    model's per-position B term at a level a kinds-loop session may not resolve.
- **L: int8 whole-line or whole-word flip-flops (4; E141's steady misses).** With blind 5's `b_line_zero_one` (the gate
  with 64 bits a boundary) and `b_line_flipflop_nogate` (512 bits, no gate), `int8.b_line_zero_ff` completes the
  two-by-two: the same gate with all 512 bits a boundary. `int8.b_line_zero_full` keeps the gate with random bytes in
  the live lines. `int8.a_word_zero_one` is the A-side zero/one flip-flop (blind 5's `a_word_flipflop` moved all 32
  bits). `int8.b_line_55_aa` (priority 2) flips all 512 bits with no gate on other values than 0x7F/0x80.
- **W: power-law weights (2; E141's steady miss).** `int8.powerlaw_df4_pc` (Student-t, df 4, a per-channel scale, so
  bytes are larger than blind 5's per-tensor `powerlaw_w`) and `int8.powerlaw_df15_pt` (priority 2; df 1.5 per tensor:
  most bytes 0 or +-1, so 61.7% of the slots gate).
- **R: real tiles (12; item 7, rank 8).** Layer 0 of two public **W8A8 checkpoints** run on a public-domain text
  (provenance below). Their linear layers are W8A8 matmuls by construction: int8 weights with one scale per output
  channel, activations quantised to int8 per token at run time. So the int8 tiles hold **the checkpoints' own int8
  weight rows**, not weights rounded here:
  - int8 W8A8 projections: SmolLM-135M `q_proj` and `down_proj`, Qwen2.5-0.5B `v_proj`, `gate_proj` (after attention
    and the residual) and `down_proj` (priority 2). The down projections' SiLU-gated inputs leave whole A words zero
    after per-token quantisation (`int8.real_smol_w8a8_down` gates 25% of its slots, Qwen's 2.7%);
  - attention matmuls: Q times K^T in fp16 from both models (Qwen's with its large k_proj bias, keys up to 121.6);
    the causal softmax times V in fp16 (SmolLM, the shape of blind 5's `real_pythia_softmax_v`, which E141 read 0.60 W
    off) and in fp32 (SmolLM's diagonal block, exact zeros above the diagonal: 47% of A's words, hold candidate; Qwen's
    off-diagonal block, priority 2, no zeros);
  - dequantised weights in a float matmul (W8A16): `fp32.real_qwen_dequant_q` (int8 times its bf16 channel scale,
    exact in fp32; the int8 zeros make 11.7% of B's words zero) and `fp16.real_qwen_dequant_v` (priority 2).
- **Z: zeros' transport (4; item 13).** Item 13 asks what moving zeros costs. These tiles carry the most B traffic a
  tile can (B's columns l and l+8 bitwise complements, so each lane's B flips all 32 bits every cycle):
  `fp32.a_zeros_b_complement` behind a closed gate (A = +0.0), `fp32.negzero_a_b_complement` in live lanes that multiply
  zeros (A = -0.0, a nonzero word, so nothing gates; E93 read `-0.0 x -0.0` at a constant's cost), `fp16.a_zeros_b_complement`
  (priority 2), and int8's `int8.a_zeros_b_lineflip` (A zero, B lines 0x7F/0x80). Against E78's `a_zeros_b_randn` and
  the zeros anchors they split B's transport under the gate from the live lanes' cost.
- **S: single bits on other base words (5; item 15).** One bit flipping on every lane every cycle (B; 4,096 flips an
  op) or down every A column (A; 2,048), on words no single-bit run has used: 1/3 (0x3EAAAAAB, alternating mantissa
  bits, the case the bench's Booth recoder makes dear) and 0.5 (0x3F000000, an empty mantissa), against E67's, E79's
  and E134's words (0x3fbbc9e4, 0x3fbd207c). `fp32.b_onebit_b12_third`, `b_onebit_b20_third`, `fp32.a_onebit_b5_third`
  (hold candidate), `fp32.a_onebit_b16_half` and `fp16.b_onebit_b6_third` (priority 2 both). Each sits on a constant
  partner (1.0), so its level is a constant's (E78's fp32 `ones`, `pi`) plus the bit.
- **C: the C-register candidate (2, priority 2; rank 2's "registered first").** `fp32.c_absorbed` and `fp16.c_absorbed`
  have operands nearly as busy as random data (79,586 and 78,830 bits an op against the anchors' 85,608 and 84,978) but
  one huge product per element absorbs every other: C flips 768 and 256 bits an op at a launch's start, against the
  anchors' 49,089 and 49,131. A model with a C term and one without should disagree most here.
- **0: anchors.** Zeros and a fresh random draw in each type: randn for the floats and `full` (uniform -128..127) for
  int8. They are `anchor: true`, priority 2, and run in every pass for footing.

## Hold candidates for E154 and E161 (rank 4)

Four kinds, each chosen from a different power tier and each below section 22's stops. They are described here by what
they are and by the measured levels of their nearest relatives in committed sessions, never by a model's prediction
(Q139(e) freezes those).

| tile | what it is | measured relatives (committed) |
|---|---|---|
| `int8.b_line_zero_ff` | an int8 whole-line kind: B lines alternate all 0x00 (gated) and all 0xFF, A uniform | blind 5's `int8.b_line_zero_one`: 3.30-3.41 W over zeros on aifoundry3 (E141 README § 3); 43.41 W board at 800 MHz on aifoundry2 (E143 `results.json` › `score.reported.tiles`) |
| `int8.real_qwen_w8a8_v` | an int8 real W8A8 projection, ungated: per-token int8 activations against a public checkpoint's own int8 `v_proj` rows | E78's int8 `full` 7.056 W (aifoundry3, `results.md`); blind 5's W8A8 tiles 49.05-49.56 W board on aifoundry2 (E143) |
| `fp32.a_onebit_b5_third` | an fp32 constant-word kind with one A bit walking: A on the word of 1/3 with bit 5 flipping down each column, B = 1.0 | E78's fp32 `ones` 8.257 W and `pi` 8.470 W (aifoundry3, `results.md`), plus one low A bit (E134); `ones` and `pi` 51.5 and 51.6 W board at 800 MHz on aifoundry2 (E83 README, column `p800 W`) |
| `fp32.real_smol_softmax_v_causal` | an fp32 real attention block: a causal softmax's diagonal block (exact zeros above the diagonal, 47% of A's words) times V | E78's fp32 `nn_like` (50.8% gated) 13.036 W (aifoundry3); half-gated fp32 tiles at 60.02-61.24 W board on aifoundry2 with the clock left at 800 MHz (E143: `fp32.block_sparse_k4`, `fp32.wideexp48_bgate_kblk`) |

**Below the stops.** On aifoundry3 the tiers run from about 3 to about 13 W over zeros, against fp32 random's 24.7 W,
whose 13-minute hold E144 had to duty-cycle. On aifoundry2 every relative ran its 6 s bursts at 800 MHz, the governor not acting
(boards 43-61 W in E143 and E83, against section 22's 82 W design limit and 85 W stop; E143's highest sample, 87.95 W,
came from a dense random-exponent fp32 tile, a kind none of the four resembles). Over minutes aifoundry2's governor
acts on temperature instead: E83's 76 s runs of fp32 `ones` and `pi` reached the 65 °C threshold and held 767-782 MHz
at about 53 W. That is what E161's governed holds measure, not a stop. So no candidate needs a duty cycle as designed;
Q139(e) still checks each against its own frozen prediction and the stops before E154 and E161.

## The C check (what a `--values file:` run cannot do, done on the desk)

A `--values file:` run verifies no arithmetic (`../README.md` 1.5), so the pool checks each tile's C before any card
sees it. This is blind pool 5's `c_check`, with four additions (marked +):

1. **Operands.** No NaN or Inf encoding (fp32 exponent field 0xFF, fp16 0x1F). -0.0 words counted: only
   `fp32.negzero_a_b_complement` has them, by design (its A, 256 words). + Subnormal operands counted: **none in any
   tile**. One SmolLM value rounds to an fp16 subnormal in `fp16.real_smol_softmax_v`'s B. Flushing it would zero that
   half, and PRM 9.4's two-term rule would then drop the update for all 16 rows, moving the first op's C by 3% of its
   largest element. So that value is written as +0.0, and C is the same whether or not the unit flushes subnormals
   before the nonzero test. The rule text says so.
2. **C emulated in PRM 9.4's order.** fp32: one rounded add per k. fp16: the two-term update per k-pair, dropped
   unless all four halves are nonzero, then rounded to fp32. int8: int32 with wraparound. This is a float64-then-round
   emulation; the unit's internal rounding of the two-term sum is not modelled. + **Subnormal products: none**, and +
   flushing every subnormal operand and product changes no tile's C.
3. **C stays finite.** The first 64 ops are run exactly. A bound over the absolute products shows C cannot reach Inf or
   NaN in 2^21 accumulate ops (with an 8x rounding margin). **All 50 pass.** The largest bound is 2.1e+37, from
   `fp32.c_absorbed` (its one product of 2^100 a step), against 3.4e38.
4. **C described.** The share of updates that change C, the C-register flips an op and the share of C still moving, at
   a launch's start and estimated at its end. + `c_op1_sha256`: the sha256 of the emulated first op's C, so a host-side
   check (Q139(k)'s `tools/claims-v3/ccheck/`) can compare the bytes. + The first op's C against an exact reference (the
   exactly rounded sum of every applied product, `math.fsum`): **every int8 tile exact**, and the floats within
   1.8e-07 of the largest C element, so each format's rounding is the only gap a check must allow.

**Reproducible.** `--check` passes with numpy 1.26.4 (Python 3.9.6, the lab collectors') and with numpy 2.5.3 (Python
3.12): every tile, `blind6.json`, `MANIFEST` and `SHA256SUMS` byte-identical.

## What the pool does to predicting power and heat

It measures nothing itself. **It is the out-of-sample test set** for M8 (rank 2) against M6 and M7 on three cards:
**E153** aifoundry3 card 0 at 600 MHz, **E157** aifoundry1 card 1 at 600 MHz, and **E160** aifoundry2 under its own
governor in bursts. It is also the source of the four kinds whose heat **E154** and **E161** predict end to end from
the bits (Q139(e)). Q139(x) copies the pool unchanged after M8's commit and commits every model's predictions before
any claim.

**Before** (pool 5, registered primaries): M7's blind power error on aifoundry3 was 0.325 / 0.317 / 0.356 W rms on
fp32 / fp16 / int8 and 0.365 W over all 30 new kinds, with M6 as good (0.367 W). On aifoundry1 card 1 it was
0.169 / 0.149 / 0.251 W. Heat over a 4.5 s run was 0.13 °C rms (E141, E142). On single exponent flips M6 read 0.307 W
rms with a bias of -0.259 W (E147). int8's steady misses were -0.61 W (whole-line zero/one), -0.60 W (power-law
weights) and +0.50 W (a W8A8 down projection) (E141).

**After:** these 44 kinds' blind error, per format and per term, with M8 scored against M6 and M7 on the same tiles.
Rank 2's rules (M8 minus M6 rms resolved below zero by a paired bootstrap over tiles on both 600 MHz cards; bias
inside B1/B2; at least 26 of 30 inside) can be applied to the 30 priority-1 kinds. The terms each case tests:

| term (M8's candidates, rank 2) | tiles that test it |
|---|---|
| an exponent-field price (E147) | case E: 10 tiles, exponent shares 0.23-0.93 |
| int8's per-position B prices (E138, E145) | case B: held single bits at positions 1, 4 and 7; line-parity flips at 2 and 5 |
| int8's steady misses: whole-line, power-law, W8A8 (E141) | cases L, W and the five int8 real tiles |
| the C-register candidate | case C (quiet C at random-data operand activity), and case Z's C-free tiles |
| zeros' transport (item 13) | case Z against E78's `a_zeros_b_randn` and the zeros anchors |
| the base word's effect on a bit's price (item 15) | case S, on two new words |
| real tensors (item 7) | case R: 12 tiles, two models, as a registered sub-rule (rank 8) |
| heat end to end (rank 4) | the four hold candidates |

Heat rides on power through the die's rise per board W, so every tile tests heat over a run too.

## Provenance of the real tiles

`real/` holds 24 float32 cuts, written by `fetch_real6.py`, which ran **layer 0 of two public W8A8 checkpoints** on a
public-domain text. Only the safetensors header, layer 0's tensors and the embedding rows of the text's tokens were
fetched, by HTTP range requests at pinned commits. `real/provenance.json` gives each tensor's offsets and sha256, and
each cut's slice, shape, range and zero count.

| model | repo | revision (commit) | weights | fetched |
|---|---|---|---|---|
| SmolLM-135M-Instruct, W8A8 | `RedHatAI/SmolLM-135M-Instruct-quantized.w8a8` | `203f247e5fdd358199df1cecd839a5b8fe5c9473` | int8, one bf16 scale per output channel | 3,581,568 bytes, 42 requests |
| Qwen2.5-0.5B, W8A8 | `RedHatAI/Qwen2.5-0.5B-quantized.w8a8` | `0d1951533baeec89dd257df86d4d10c3bd5429f5` | int8, one bf16 scale per output channel | 14,987,264 bytes, 45 requests |

Both declare `quant_method: compressed-tensors`, `format: int-quantized`: weights int8 symmetric per channel (static),
input activations int8 symmetric per token (dynamic). Embeddings and norms are bf16.

**Text.** The opening of Jane Austen, *Pride and Prejudice* (1813), public domain. The first 32 tokens are used, looked
up word by word in each model's `tokenizer.json` vocabulary (greedy longest match, not the BPE merges; both
tokenizers split the text into the same 32 pieces, from "It" to "or").

**Forward pass.** Layer 0 in float32: RMSNorm with the checkpoint's weight; W8A8 q, k and v projections (int8 times
int8 summed exactly, times the token's scale and the channel's scale, plus Qwen's biases); rotary over the whole
64-dim head (rotate_half; base 1e4 for SmolLM, 1e6 for Qwen); scores q.k/8 with grouped KV heads (SmolLM 9 heads on 3,
Qwen 14 on 2); a causal softmax; P times V; the W8A8 o_proj and the residual; RMSNorm; W8A8 gate and up projections;
SiLU(gate) times up. SmolLM's head 1 and Qwen's head 3 (KV head 0 in both) are used for Q, K, P and V.

**Rounding and quantisation.** fp32 tiles: activations as computed, weights dequantised (int8 times a bf16 scale is
exact in fp32). fp16 tiles: values rounded to fp16, nearest even (one SmolLM value that rounds to a subnormal written
as +0.0, above). int8 tiles: activations per token, scale = the token's max abs over its whole row (576 or 896 dims, or
1,536 or 4,864 hidden units) / 127, `q = clip(round_half_even(x / scale), -127, 127)` (the maxima are in
`provenance.json` › `scales`); weights are the checkpoints' int8 values, unchanged.

## Independence

The designer read the workflow's brief, the kinds page's source (section 11, items 6, 7, 13 and 15, and "How well power
and heat can be predicted now"), Q138's final critic (its open list and prediction table), and these files of this
repository, and nothing else:

- **Repository docs and code.** `tools/claims-v3/kinds/README.md` (sections 1-3); `blind5/README.md`,
  `blind5/make_blind5.py` (whose C check and build this generator extends) and `blind5/fetch_real.py`; the heads of
  `real/README.md` and `real2/README.md`; `make_kinds.py` (imported, not modified).
- **Measured results.** E78's `results.md` (the kinds matrix); E141's README (results, misses, stops); E143's
  `results.json` (board, clock and rise per pool-5 tile; the file also carries M5-M7's pool-5 predictions beside them,
  which were printed with it); the lines of E144's two READMEs (aifoundry3, aifoundry2) on holds and stops; E83's README table (aifoundry2's bursts and sustained runs); the heads of E145's, E147's,
  E134's and E93's READMEs and E130's tools README (base words and layouts).
- **E141's harness.** The pool-json keys `tools/claims-v3/e141/e141_common.py` and `score_e141.py` read (`name`,
  `file`, `type`, `case`, `priority`, `anchor`, `sha256`), so `blind6.json` keeps them.

**Never read:** M8, Q139(m)'s data directory (`docs/reports/data/2026-11-03-q139m-*`) or scratch, or any file of that
lane. No model code was opened (`m6_inputs.py`, `predict_blind*.py`, `make_predictions_*`, `fit_*`). The hold
candidates were chosen from tile descriptors and the committed measurements above, not from any model's prediction.

## Files

| path | what |
|---|---|
| `make_blind6.py` | the generator, the design asserts and the C check, with `--check` (numpy only; `--kinds-dir` points at `make_kinds.py`) |
| `fetch_real6.py` | fetches the real cuts and runs layer 0 of both checkpoints (numpy and network; not needed to rebuild) |
| `blind6.json` | per tile: file, type, case, rule (one line), seed, sha256 of the whole file and each half, priority, anchor, hold candidate, run checks, `tile_stats`, `bus_by_field`, `c_check`; plus the counts and the brief check |
| `MANIFEST` | one line per kind: sha256, file, name, type, case, priority, anchor or kind, hold or not |
| `tiles/<type>/<name>.bin` | the 50 tiles |
| `real/*.npy`, `real/provenance.json` | the 24 cuts the real tiles use, and where they came from |
| `SHA256SUMS` | sha256 of every file here except itself |
