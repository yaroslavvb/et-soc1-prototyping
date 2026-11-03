# Q138(b) blind pool 5

Mon 2 Nov 2026 (week 45). **Q138(b) blind pool 5, written by an independent designer who never saw M7** (Q138(m)'s
fit) nor anything of its lane. It answers the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "A power model
across kinds", whose power half [E140](../../../../docs/reports/data/2026-11-02-e140-blind4/README.md) left open. The
pool targets E140's six misses, all over-predictions: spread exponents beside gated zeros, exponent-only activity,
fp16 pairs that cancel, and int8's whole-line flip-flop.

**36 operand tile pairs: 14 fp32, 11 fp16, 11 int8.** 24 are priority 1, 6 are priority-2 tests and 6 are anchors.
Each tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), in the type's layout. Tiles are packed with
`make_kinds.encode` (or `make_kinds.from_words` for the four tiles defined on bit patterns) and described by
`make_kinds.tile_stats` in `blind5.json`. Each tile also carries a `c_check`: the accumulator C the card builds from
it, emulated on the desk (below). Layout, stream order and gate rule are those of `../README.md`; nothing here
changes them.

```bash
python3 tools/claims-v3/kinds/blind5/make_blind5.py            # writes tiles/, blind5.json, SHA256SUMS (numpy only)
python3 tools/claims-v3/kinds/blind5/make_blind5.py --check    # rebuilds in memory and compares with disk
python3 tools/claims-v3/kinds/blind5/fetch_real.py             # optional: re-fetches real/ from huggingface.co
sparsity_host --test fma --type fp16 --values file:tools/claims-v3/kinds/blind5/tiles/fp16/fp16.pair_nearcancel.bin
```

## Tiles

`gated`: the share of the 4,096 column-slot-cycles of one accumulate op that are gated. `bits/op`: operand bits the
input bus flips in one op, under `make_kinds`' stream and convention (int8's figure is provisional, as
`../README.md` 1.2 says). `C flips/op`: C-register bits that flip in one op, summed over its 16 updates of each of the 256
C elements, from this pool's C emulation. "Start" is the second op of a launch. "End" is an estimate of one op at the end of a 0.5 s launch at
600 MHz (2^19 ops for fp32 and fp16, 2^20 for int8). Read it as a descriptor, not a measurement. `sha12`: the first
12 hex digits of the whole file's sha256.

Cases: 0 an anchor, for footing; 1 fp16 pairs that cancel; 2 spread exponents beside gated zeros; 3 exponent-only
activity; 5 a real model; 6 whole-line or whole-word flip-flops; 7 few mantissa bits; 8 seeded realistic weights;
9 a structured stream. Cases 1, 2, 3 and 6 are E140's misses.

| tile | case | rule | gated | bits/op | C flips/op, start → end | prio | sha12 |
|---|---|---|---|---|---|---|---|
| `fp32.anchor_zeros` | 0 | every element +0.0 (footing: the zero reference, as fp32.zeros) | 100.0% | 0 | 0 → 0 | anchor | `e5a00aa9991a` |
| `fp32.anchor_randn` | 0 | standard normal both sides, a fresh draw (footing: as fp32.randn) | 0.0% | 81,950 | 49,208 → 10,650 | anchor | `195494806e1c` |
| `fp32.wideexp48_dense` | 2 | random sign, exponent uniform 2^-48..2^48, random mantissa, both sides, no zero anywhere: the spread exponents alone (products stay finite: C cannot overflow) | 0.0% | 97,624 | 4,782 → 1,161 | 1 | `080e7444feea` |
| `fp32.wideexp48_bgate_alt` | 2 | wideexp48_dense's rule (fresh draw) with B columns 8-15 all +0.0: every lane alternates a wide-exponent word with zero each cycle (half the slots gated); C finite, unlike blind 4's 2^+-120 version | 50.0% | 97,792 | 2,673 → 614 | 1 | `7f3b87aba38a` |
| `fp32.wideexp48_bgate_kblk` | 2 | wideexp48_dense's rule (fresh draw) with B lines (k-groups) 4-7 and 12-15 all +0.0: every lane gated for whole k-groups, the gate changing only 4 times an op (steady, beside the wide words) | 50.0% | 65,640 | 3,841 → 1,156 | 1 | `1a258f260c2e` |
| `fp32.exp_only_both` | 3 | both sides random sign * 2^U{-40..40}, mantissa field 0: only sign and exponent fields move, every product an exact power of two (the multiplier's mantissa array multiplies 1.0 by 1.0) | 0.0% | 26,996 | 2,787 → 1,336 | 1 | `e018de39a2a2` |
| `fp32.b_exp_busy_a_const` | 3 | A every element 1.25 (0x3FA00000, never changes); B random sign * 2^U{-40..40}, mantissa 0: exponent-only activity on the side that alternates every cycle (blind 4's version had it on A) | 0.0% | 18,512 | 7,232 → 1,488 | 2 | `8dda40560f6c` |
| `fp32.e4m3grid_gelu_w` | 7 | A = GELU(randn)*4 and B = 2*randn, each rounded to the OCP e4m3 grid (3 mantissa bits, so the low 20 mantissa bits of every word are zero); -0.0 written as +0.0 | 0.0% | 31,804 | 23,092 → 10,412 | 1 | `599d216da00d` |
| `fp32.real_pythia_ln1_q` | 5 | pythia-70m layer 0 on Dickens' opening: A = input_layernorm output (tokens 16-31, dims 0-15, computed in fp32: full mantissas); B = query_key_value rows 576-591 (head 3's query) x input dims 0-15, transposed (fp16 values) | 0.0% | 57,240 | 45,590 → 7,845 | 1 | `8c476c6a17c0` |
| `fp32.real_pythia_gelu_down` | 5 | pythia-70m layer 0: A = post-GELU of dense_h_to_4h (tokens 16-31, hidden units 1024-1039, fp32); B = dense_4h_to_h rows 0-15 x hidden 1024-1039, transposed (fp16 values) | 0.0% | 57,354 | 47,009 → 9,145 | 1 | `2fdf440fe446` |
| `fp32.lowrank2_w` | 8 | A standard normal; B = 0.1 * U V^T, rank 2 (U, V 16x2 standard normal): low-rank weights | 0.0% | 83,114 | 48,159 → 10,926 | 2 | `ceb49238386d` |
| `fp32.sorted_k` | 9 | standard normal; every A row sorted ascending along k and every B column sorted ascending along k: A's column walk and each lane's (l, l+8) alternation both meet near-equal values | 0.0% | 80,092 | 42,279 → 5,205 | 1 | `4a5a119cb3af` |
| `fp32.gray_stream` | 9 | random-valued words in a Gray-coded stream: A[i][k] = base_k XOR gray(i) << s_k (4 mantissa bits, s_k in 0..19), so each step down an A column flips one bit; B[k][l+8] = B[k][l] XOR one random mantissa bit, so every lane's alternation flips exactly one bit (bases standard normal) | 0.0% | 9,398 | 48,833 → 10,990 | 1 | `dd301a028766` |
| `fp32.block_sparse_k4` | 9 | standard normal; B lines (k-groups) 4-7 and 12-15 all +0.0 (blocks of four along k, 50%): the same steady gate as wideexp48_bgate_kblk with ordinary exponents, its matched control | 50.0% | 57,976 | 25,326 → 5,686 | 2 | `2462c61af644` |
| `fp16.anchor_zeros` | 0 | every element +0.0 (footing: as fp16.zeros) | 100.0% | 0 | 0 → 0 | anchor | `e5a00aa9991a` |
| `fp16.anchor_randn` | 0 | standard normal both sides, a fresh draw (footing: as fp16.randn) | 0.0% | 82,386 | 50,179 → 11,487 | anchor | `1d5e328c68a8` |
| `fp16.pair_cancel_asign` | 1 | randn; A's two halves are a and -a (each A word differs from its own other half only in a sign bit) and B's two halves are equal: every two-term update a*b + (-a)*b is exactly zero; nothing gates, nothing is dropped | 0.0% | 84,000 | 0 → 0 | 1 | `f5a1a7e39204` |
| `fp16.pair_nearcancel` | 1 | randn; A's halves equal (a1 = a2) and b2 = fp16(-b1*(1 - 2^-8)): every two-term update cancels to about 2^-8 of one product, so C creeps and every sum normalises across about 8 leading zeros | 0.0% | 83,202 | 35,516 → 10,740 | 1 | `e1ddce2d8bdc` |
| `fp16.wideexp_bgate_alt` | 2 | fp16 bit patterns: random sign, exponent field uniform 1..30 (2^-14..2^15), random nonzero mantissa, both sides; B columns 8-15 all zero words: every lane alternates a wide word with zero each cycle | 50.0% | 99,696 | 11,688 → 1,119 | 1 | `24560b605bcb` |
| `fp16.exp_only` | 3 | fp16 random sign * 2^(e-15), exponent field e uniform 1..30, mantissa 0, both sides: only sign and exponent bits move, every product a power of two | 0.0% | 36,962 | 11,163 → 1,532 | 2 | `f5f3f403d9bc` |
| `fp16.real_pythia_qk` | 5 | pythia-70m layer 0, head 2: A = rotary queries (tokens 16-31, head dims 0-31), B = rotary keys of tokens 0-15, transposed: the attention scores' matmul; fp32 values rounded to fp16 | 0.0% | 83,632 | 46,661 → 8,143 | 1 | `cd93edf425b3` |
| `fp16.real_pythia_softmax_v` | 5 | pythia-70m layer 0, head 2: A = causal softmax (query tokens 16-31 x key tokens 0-31: exact zeros above the diagonal, tiny probabilities rounding to fp16 subnormals or zero); B = values (keys 0-31, head dims 0-15) | 21.9% | 78,052 | 35,340 → 7,099 | 1 | `6acd49c4a5db` |
| `fp16.real_pythia_ln2_up` | 5 | pythia-70m layer 0: A = post_attention_layernorm output (tokens 16-31, dims 32-63), B = dense_h_to_4h rows 512-527 x input dims 32-63, transposed | 0.0% | 88,450 | 47,891 → 10,517 | 1 | `57d767ebfe46` |
| `fp16.sparse24_aligned` | 9 | randn; B 2:4 along k with the two zeros of every group of four k in ONE word (k 4m,4m+1 or 4m+2,4m+3, at random per group and column): half of B's words zero, so half the lane-slots gate | 50.0% | 77,946 | 25,965 → 6,136 | 1 | `294d92f7f1c8` |
| `fp16.sparse24_straddled` | 9 | randn; B 2:4 along k with one zero in EACH word of every group of four (k 4m or 4m+1, and 4m+2 or 4m+3): the same element sparsity as sparse24_aligned, but no word is zero (nothing gates) and every two-term update is dropped by PRM 9.4's rule | 0.0% | 78,786 | 0 → 0 | 1 | `606a7542a562` |
| `int8.anchor_zeros` | 0 | every byte 0x00 (footing: as int8.zeros) | 100.0% | 0 | 0 → 0 | anchor | `e5a00aa9991a` |
| `int8.anchor_full` | 0 | uniform -128..127 both sides, a fresh draw (footing: as int8.full, the lab's int8 random anchor, E64's int8 --values randn) | 0.0% | 69,384 | 34,333 → 34,935 | anchor | `c88be4f2f858` |
| `int8.b_line_flipflop_nogate` | 6 | A uniform -128..127; B lines alternate all 0x7F (+127, even k-groups) and all 0x80 (-128, odd): every line boundary flips all 512 B bits at once, and no B byte is ever zero (nothing gates) | 0.0% | 73,760 | 28,720 → 30,352 | 1 | `f3ef528fd509` |
| `int8.b_line_zero_one` | 6 | A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0x01 (+1): blind 4's b_line_flipflop gate exactly, with 64 of the 512 B bits flipping at each boundary instead of all 512 | 50.0% | 67,680 | 12,272 → 13,904 | 1 | `379921747d16` |
| `int8.a_word_flipflop` | 6 | A rows alternate all 0x00 (even i) and all 0xFF (-1, odd i): in int8's stream A changes every micro-op, so every micro-op flips all 32 A bits on the 16-slot broadcast and every other micro-op is gated; B uniform | 50.0% | 135,196 | 12,192 → 14,872 | 1 | `d57d3948ac7f` |
| `int8.real_pythia_w8a8_up` | 5 | pythia-70m layer 0, W8A8: A = post_attention_layernorm output (tokens 16-31, dims 64-127) quantised per token (scale = the token's max abs over all 512 dims / 127); B = dense_h_to_4h rows 768-783 x dims 64-127, transposed, quantised per output channel (max abs over its 512 inputs / 127) | 7.4% | 63,012 | 25,270 → 27,147 | 1 | `93a85e4e5667` |
| `int8.real_pythia_w8a8_down` | 5 | pythia-70m layer 0, W8A8: A = post-GELU (tokens 16-31, hidden 1536-1599) quantised per token (max abs over all 2048 hidden / 127: most bytes small); B = dense_4h_to_h rows 128-143 x hidden 1536-1599, transposed, per output channel | 0.8% | 68,062 | 24,027 → 26,999 | 1 | `403f65365f85` |
| `int8.powerlaw_w` | 8 | power-law weights: B = W[0:64, 0:16] of a 1024x64 Student-t (df 2.5) tensor, symmetric per-tensor int8 (scale = its max abs / 127, so most bytes are within +-4); A = Laplace activations quantised per token | 0.0% | 69,962 | 22,166 → 25,331 | 2 | `0a8e4447b21a` |
| `int8.sorted_k` | 9 | uniform -128..127; every A row sorted ascending along k and every B column sorted ascending along k: A's column walk meets near-equal order statistics, B's line boundaries change little | 0.0% | 54,530 | 33,840 → 33,585 | 1 | `fcf22eedbe90` |
| `int8.gray_a` | 9 | random bytes in a Gray-coded A stream: A word (i, p) = base_p XOR the 4-bit gray(i) spread one bit to each byte's LSB, so each micro-op (one step down a word-column) flips exactly one A bit; B uniform | 0.0% | 11,768 | 35,330 → 36,309 | 1 | `733b528ebda4` |
| `int8.block_sparse_a` | 9 | uniform -128..127; A words (i, w) zero in a checkerboard of 4-row x 2-word (8 k) blocks, (i//4 + w//2) odd: half of A zero, so int8's micro-ops gate in runs of four; B dense | 50.0% | 43,834 | 17,663 → 17,941 | 2 | `d54cd57a4c76` |

The three zero anchors are byte-identical (2,048 zero bytes are the same tile in every type). The harness keys each
item by name and type, so that is harmless.

### What each case is probing, and the pairs built in

Most new tiles come with a partner in the pool that differs in one property. The pairs let a session score
differences, which cancel the footing, as well as absolute levels.

- **2: spread exponents beside gated zeros.** Blind 4's two fp32 wide-exponent tiles spanned 2^-120..2^120 on both
  sides, so many products overflowed. The C check finds **C at +-Inf from the first op in 109 and 133 of the 256
  elements** (`fp32.wideexp_bgate_alt`, `fp32.wideexp_agate_rows`; computed here on the committed blind 4 tiles). An
  accumulator held at Inf is a confound for that miss. Pool 5 keeps every product finite: 2^-48..2^48 on each side,
  bounded over 2^21 ops. It separates the parts as a triplet: `wideexp48_dense` (no gate), `wideexp48_bgate_alt`
  (lanes gated every other cycle) and `wideexp48_bgate_kblk` (lanes gated for whole k-groups, steady). The steady one
  has an ordinary-exponent twin under the same gate, `fp32.block_sparse_k4`. `fp16.wideexp_bgate_alt` carries the
  alternating gate to fp16's whole exponent field.
- **3: exponent-only activity.** Both fp32 sides are powers of two (`exp_only_both`, where every product is a power of
  two). Exponent-only activity sits on B, the side that alternates every cycle, against a constant A
  (`b_exp_busy_a_const`; blind 4 had it on A). `fp16.exp_only` is the fp16 version.
- **1: fp16 pairs that cancel.** In `pair_cancel_asign` the sign moves to A: each A word is (a, -a) and each B
  word (b, b), so every two-term update is exactly zero and C never moves. `pair_nearcancel` has the same operand
  activity, but every update leaves about 2^-8 of a product, so C keeps moving. Its C register flips 35,516 bits
  an op; the exact cancel's flips none.
- **6: whole-line flip-flops.** `int8.b_line_flipflop_nogate` alternates B lines between +127 and -128, so every
  boundary flips all 512 bits and nothing gates. `int8.b_line_zero_one` keeps blind 4's flip-flop gate exactly (even
  lines zero) but flips 64 bits a boundary, not 512. Against blind 4's `int8.b_line_flipflop`, these two split the
  flips from the gate. `int8.a_word_flipflop` is the A-side version: A alternates 0x00000000 and 0xFFFFFFFF every
  micro-op, every other micro-op gated, the highest operand activity in the pool (135,196 bits an op).
- **7: few mantissa bits.** `fp32.e4m3grid_gelu_w` has every word on the e4m3 grid, so the low 20 mantissa bits are
  zero. Blind 4's real bf16-sourced tile read low; E140 put that down to the meter's dips.
- **5: real tensors, new kinds of them.** These are activations computed by running pythia-70m's layer 0, not raw
  weights:
  - LayerNorm outputs against query and MLP weights (fp32, fp16);
  - post-GELU against the down projection (fp32);
  - the attention scores' matmul, Q times K^T (fp16);
  - the causal softmax times V (fp16). That tile has exact zeros above the diagonal, and probabilities that round to
    fp16 subnormals or zero: 21.9% of A's words are zero;
  - W8A8 int8: per-token activations against per-channel weights. The post-LayerNorm one gates 7.4% of slots,
    because a token's outlier dimension sets its scale.
- **8: seeded realistic weights.** Rank-2 weights (`fp32.lowrank2_w`) and heavy-tailed Student-t weights under a
  per-tensor int8 scale (`int8.powerlaw_w`, most bytes within +-4).
- **9: structured streams.**
  - Sorted along K (`fp32.sorted_k`, `int8.sorted_k`).
  - Gray-coded streams (`fp32.gray_stream`, `int8.gray_a`). Their values are random, but each step flips one bit,
    so their operand bus reads 9,398 and 11,768 bits an op against randn's 81,950 and full's 69,384. Their C still
    flips as much as random data's.
  - Blocked sparsity (`fp32.block_sparse_k4`, `int8.block_sparse_a`).
  - 2:4 sparsity as a pair. `fp16.sparse24_aligned` puts both zeros of each group of four in one word, so half the
    slots gate. `fp16.sparse24_straddled` puts one zero in each word, so nothing gates and PRM 9.4 drops all 4,096
    two-term updates.
- **0: anchors.** Zeros and a fresh random draw in each type: randn for the floats, and for int8 `full`, uniform
  -128..127, the lab's int8 random anchor (E64's `--values randn`). They are marked `anchor: true` and priority 2,
  so they stay out of priority-1 rule sets unless a registration puts them in.

### The C check (what E140's run checks need, done on the desk)

A `--values file:` run verifies no arithmetic (`../README.md` 1.5), so the pool checks each tile's C before any card
sees it. `c_check` decodes the tile and then:

1. **Operands.** No NaN or Inf encoding (fp32 exponent field 0xFF, fp16 0x1F); -0.0 words counted. There are none:
   -0.0 is written as +0.0 where rounding could make it.
2. **C emulated in PRM 9.4's order.**
   - fp32: one rounded add per k.
   - fp16: the two-term update per k-pair, dropped unless all four halves are nonzero, then rounded to fp32.
   - int8: int32 with wraparound.

   This is a float64-then-round emulation. The unit's internal rounding of the two-term sum is not modelled.
3. **C stays finite.** The first 64 ops are run exactly. A bound over the absolute products shows C cannot reach Inf
   or NaN in 2^21 accumulate ops (with an 8x rounding margin), more than any 0.5 s launch runs: about 0.55 M ops at
   600 MHz, 1.6 M for int8 at 1 GHz. **All 36 pass.** The largest bound is 2.1e36, against 3.4e38 for fp32.
4. **C described.** The share of updates that change C, the C-register bit flips per op, and the share of C still
   moving, at a launch's start and estimated at its end.

The card-side checks are E140's, applied by the harness at run time:
- the tile file against `blind5.json`'s sha256 before the card opens (exit 9);
- each launch's record `ok` (the results read back, no tensor errors);
- cycles per op within E78's band;
- the dumped tile equal to the registered sha256.

### A post-hoc observation the pool can test (not registered, not a fit)

The C emulation was run on blind 4's committed tiles and set beside E140's published M6 residuals (`scored.json`,
`scored-nodips.json` › `primary.power.rows`). The residuals rise with the C-register flips:

| arm | r, all 25 | r, fp32 / fp16 / int8 | within-format r² |
|---|---:|---:|---:|
| primary | 0.53 | 0.61 / 0.46 / 0.66 | 0.34 |
| dips removed | 0.63 | 0.80 / 0.52 / 0.64 | 0.41 |

The tiles M6 over-predicted have a quiet C: fp16 `pair_cancel` (0 flips), the wide-exponent tiles, and int8's flip-flop
(half the k-groups gated). The tiles it under-predicted have a busy C: fp32 `cancel_pairs` (63k flips) and int8
`a_full_b_const`. That points at a result-path term M6 lacks.

It is **post hoc, on one session's 25 tiles**, with a derived descriptor, and it decides nothing. Pool 5 holds
contrasts that test it at matched operand activity:
- exact cancel against near-cancel (fp16);
- straddled against aligned 2:4 (fp16);
- Gray-coded streams against their random twins (fp32, int8);
- the wide-exponent triplet.

A model with a C term and one without should disagree most on those tiles.

## What the pool does to predicting power and heat

It measures nothing itself. **It is the out-of-sample test set** for item 6's power and heat models on three cards
(E141 aifoundry3, E142 aifoundry1 card 1, E143 aifoundry2 under its governor). Q138(x) freezes M5's, M6's and M7's
predictions for it before any claim.

**Before:** M6 on blind pool 4 (E140) read power 0.41 W rms on the floats and 0.38 W on int8, biased -0.28 W, with
19 of 25 tiles inside its 95% band. Its heat error was 0.20 °C on the floats and 0.16 °C on int8, with 24 of 25
inside. M5 read 0.36 W over all 25.

**After:** these 36 tiles' blind error, per format and per term. The terms tested:

| term | tiles that test it |
|---|---|
| the gate-state term | alternating against steady gates at matched spread exponents, and the 2:4 pair |
| per-field operand flips | exponent-only, the e4m3 grid, the Gray-coded streams |
| fp16's two-term rule | the cancel pair, the straddled 2:4 tile |
| int8's B-boundary and A terms | the flip-flops, `gray_a`, `sorted_k` |
| real tensors | W8A8 and attention tensors, untested before |
| a possible result-path term | the C contrasts above |

Heat rides on power through the die rise per board W, so the same tiles test it.

## Provenance of the real tiles

`real/` holds 14 float32 cuts, written by `fetch_real.py`. It ran pythia-70m's layer 0 on public-domain text. The
tensors were fetched by HTTP range requests on `model.safetensors` at a pinned commit: the header, the nine layer-0
tensors used, and the 13 distinct embedding rows of the tokens, 5,791,744 bytes in 22 requests (plus the header and
`tokenizer.json`). `real/provenance.json` gives
for each tensor its data offsets and sha256, and for each cut its slice, shape, range and zero count.

| model | repo | revision (commit) | source dtype |
|---|---|---|---|
| pythia-70m | `EleutherAI/pythia-70m` | `a39f36b100fe8a5377810d56c3f4789b9c53ac42` (blind 4's pin) | F16 |

**Text.** The opening of Charles Dickens, *A Tale of Two Cities* (1859), public domain. The first 32 tokens are used,
looked up word by word in the model's `tokenizer.json` vocabulary (greedy longest match, not the BPE merges): one
word, "foolishness", splits as `Ġfoolish` + `ness`.

**Forward pass.** GPT-NeoX layer 0 as pythia-70m configures it, in float32 from the fp16 weights:
- `input_layernorm`, then `query_key_value` with its bias, then rotary on dims 0-15 of each head (base 10000), then
  scores q·k/8, then a causal softmax;
- `post_attention_layernorm` of the same input (parallel residual), then `dense_h_to_4h` with its bias, then the
  exact GELU.

Head 2 is used for Q, K, P and V. Every A cut is tokens 16-31.

Rounding and quantisation:
- **fp32 tiles:** activations as computed in fp32, with full mantissas; weights are the fp16 values, exact in fp32.
- **fp16 tiles:** values rounded to fp16, nearest even.
- **int8 (W8A8):** activations per token, scale = the token's max abs over its whole row (512 dims, or 2,048 hidden
  units) / 127; weights per output channel, scale = the channel's max abs over all its inputs / 127. In both,
  `q = clip(round_half_even(x / scale), -127, 127)`. The maxima are in `provenance.json` › `scales`.

## Independence

The designer read the workflow's brief, the kinds page's source, and these files of this repository, and nothing else:

- **Repository docs.** `tools/claims-v3/kinds/README.md`. `blind4/README.md` and `blind4/make_blind4.py`. The tile
  table of `blind3/README.md`, through a grep that also printed blind 3's M5/M4 prediction rows.
- **Repository code.** `make_kinds.py`: the constants and the encode, decode, words, stream, gate and statistics
  functions, imported and not modified.
- **E78's harness.** The launch command and run gates of `run_e78.py` and `reduce_e78.py`; `e78_common.py`'s anchors.
- **E140.** The data README, `scored.json` and `scored-nodips.json` (the published residuals); lines 52-125 of
  `e140/e140_common.py`; a grep of `e140/README.md` that printed four rows of M6's frozen predictions for blind 4.
- **E115.** The first 60 lines of its data README.
- **The sparsity workload.** Fragments of the host (`repeatFor`, `Summary`, `checkC`) and of the kernel (`run_fma`,
  the result write).
- **Real-tile READMEs.** The heads and tables of `real/README.md` and `real2/README.md`.
- **The kinds page.** Section 11's item 6 and its subsection "How well power and heat can be predicted now".

**Never read:** M7, Q138(m)'s data directory or scratch, or any file of that lane. No M6 model code was opened either
(`m6_inputs.py`, `make_predictions_*`, `predictions-*.json`). Directory listings showed file names only.

## Files

| path | what |
|---|---|
| `make_blind5.py` | the generator and the C check, with `--check` (numpy only; `--kinds-dir` points at `make_kinds.py`) |
| `fetch_real.py` | fetches the real cuts and runs pythia-70m's layer 0 (numpy and network; not needed to rebuild) |
| `blind5.json` | per tile: file, type, case, rule (one line), seed, sha256 of the whole file and each half, priority, anchor, run checks, `tile_stats`, `c_check` |
| `tiles/<type>/<name>.bin` | the 36 tiles |
| `real/*.npy`, `real/provenance.json` | the 14 cuts the real tiles use, and where they came from |
| `SHA256SUMS` | sha256 of every file here except itself (`sha256sum -c SHA256SUMS` from this directory) |
