# Q130(s): the kinds of numbers — the spec, the generator and the tiles

Sat 31 Oct 2026 (week 44). **51 operand tile pairs** — 18 fp32, 17 fp16, 16 int8 — one per *kind of number*,
each 2,048 bytes of raw operands ready for the card and for the RTL, with every tile's bit statistics measured
and frozen in [`kinds.json`](kinds.json).

This is the input the rest of Q130 runs on: **E78** (the energy matrix, aifoundry3, 600 MHz pinned), **E80**
(speed under the governor, aifoundry2), **Q130(b)** (RTL toggle counts) and **Q130(c)** (the empirical model).
Nothing here touches a card. Reproduce it with

```bash
python3 tools/claims-v3/kinds/make_kinds.py tools/claims-v3/kinds --check   # 4 s, numpy only
python3 tools/claims-v3/kinds/make_kinds.py --list                          # the kinds and their rules
```

and run one on a card, or in the RTL bench, with

```bash
sparsity_host --test fma --type fp32 --values file:tools/claims-v3/kinds/tiles/fp32/randn_sorted.bin
python3 rtl-sim/fma_toggle/tiles.py x out.hex --from-bin tools/claims-v3/kinds/tiles/fp32/randn_sorted.bin
```

`--check` passes: every tile decodes back to its intended element values through an independently written
decoder, every `*_sorted` tile is a verified permutation of its base kind's operand multiset, and the fp32
kinds that share a name with one of the host's own `--values` patterns have per-bit one-probabilities that
agree with the host's distribution within 5 sigma (`checks.fp32_vs_host_builtin_p1` in `kinds.json`; the
deterministic `zeros`, `ones` and `pi` agree bit-exactly).

---

## 1. Three facts the other lanes must not get wrong

All three are quoted with their sources in `kinds.json` under `facts`, and all three were confirmed from more
than one place.

### 1.1 A 32-bit word of a tile line is one lane operand, whatever the type

Both tiles are **16 lines of 64 bytes**. Element `k` of A row `i` sits at byte `i*64 + k*size`; element `k` of
B column `j` sits at byte `p*64 + (j*E + e)*size` with `k = p*E + e`
(`workloads/sparsity/host/main.cpp`, `makeTiles`). Because `E*size = 4` bytes in all three types, this means:

| type | `E` elements a word | `size` | `K` | word `w` of A line `i` | word `j` of B line `p` |
|---|---|---|---|---|---|
| fp32 | 1 | 4 | 16 | `A[i][w]` | `B[p][j]` |
| fp16 | 2 | 2 | 32 | `A[i][2w .. 2w+1]` | `B[2p .. 2p+1][j]` |
| int8 | 4 | 1 | 64 | `A[i][4w .. 4w+3]` | `B[4p .. 4p+3][j]` |

So **every tile is a 16x16 grid of 32-bit lane operand words**, element `e` at byte `e*size` inside the word
(little-endian: element 0 is the low bits). And **the A word index equals the B line index** — both are the
k-group. Demonstrated directly on a counting pattern: A word 3 of line 5 reads back as elements k = 12..15 of
row 5, and B word 7 of line 2 as `B[8..11][7]`.

### 1.2 The stream order: A changes every second cycle, B alternates every cycle

PRM 9.4, `external/core-et/rtl/shire/minion/vpu/vpu_tensorfma.v`, and the bench's own `one_op`
(`rtl-sim/fma_toggle/tb.sv` lines 92-110 and 144-149):

```
for k in 0..15:                 # the k-group: B line k, A word k
  for i in 0..15:               # A row
    for h in 0, 1:              # C columns 0-7, then 8-15
      A operand = Aword[i][k], BROADCAST to all eight lanes
      B operand of lane l = Bword[k][8*h + l]
```

512 micro-ops, one a cycle, then a gap: 546 cycles an op for fp32 and fp16, 318 for int8
(`tools/claims-v3/hpl/surface_hpl.py`). Therefore

- the **A** word is held for two consecutive micro-ops and then walks **down a word-column of A**: 256 of the
  512 transitions are free, and the other 256 are steps down a column;
- lane `l`'s **B** word **alternates every cycle** between column `l` and column `l+8` of the *same* B line,
  sixteen times, before the next k-group: 31 of each lane's 32 transitions in a k-group cost exactly
  `d(Bword[k][l], Bword[k][l+8])`.

**Sorting the rows of the matrix is not the same thing as ordering the stream.** For the A side the right
object is a path down each word-column; for the B side it is a *pairing* of column `l` with column `l+8`
inside each line. Section 4 measures what that distinction is worth: 0.740 of the base flip count instead of
0.935.

This implementation was cross-checked against the committed flip counter the Hamming-ladder experiments
(E60, E65, E67, E70) were built with: for all 18 fp32 kinds, `bus_bits_per_op` here equals
`tools/claims-v3/hl/make_hl.py`'s `fma_flips(A, B)["total"]` exactly. The two agree on the order and on the
convention (cyclic over the 512 micro-ops, the last against the next op's first), so these numbers are
directly comparable with the E60/E65/E67/E70 per-bit price lists.

### 1.3 Zero gating is word-wide, not element-wide — the biggest trap in the matrix

`external/core-et/rtl/shire/minion/vpu/vpu_ctrl.v` lines 1230-1233 compute the flags on a full
`VPU_DATA_S_SZ` = 32-bit word:

```verilog
f3_zero_data_a   = {`VPU_LANE_NUM{(f3_tena_regfile_wdata_l == `VPU_DATA_S_SZ'b0)}};
f3_zero_data_b[i] = (f3_tenb_regfile_wdata_l[`VPU_DATA_S_SZ * i +: `VPU_DATA_S_SZ] == `VPU_DATA_S_SZ'b0);
```

and lines 817 and 837-839 turn them into `ex_fma_gate_mask`, which clears `ex_txfma_valid`. The bench states
the same rule in one line (`tb.sv` line 56):

```systemverilog
assign lane_valid[l] = uop_valid & (uop_mul | ((uop_a != 32'b0) & (uop_b[l] != 32'b0)));
```

Two consequences:

- **the A-side flag is one bit broadcast to all eight lanes**, so a zero A word gates the whole micro-op,
  while a zero B word gates one lane;
- **a lane gates only when the whole 32-bit word is zero** — in fp16 *both* halves, in int8 *all four* bytes.

So the same 50% element sparsity gates **77.4% of lane-cycles in fp32, 41.4% in fp16 and 10.8% in int8**
(`sparse50`, measured below). That is why this spec carries both families: `sparse50`/`sparse90` zero
**elements** (the data property, what a user means by sparsity) and `wsparse50`/`wsparse90` zero whole
**words** (the gate's property). Quoting one for the other would wreck E78's sparsity row.

Also: the first op of a launch is a multiply pass and is never gated, so `gated_lane_cycles` below describes
an accumulate op, which is all but one of them.

### 1.4 fp16's two-term rule is arithmetic, not gating

PRM 9.4's pseudo-code applies the two-term update `c += a1*b1 + a2*b2` only when **all four** of `a1, a2, b1,
b2` are nonzero (host `expectC(..., literal=true)`). That is separate from the gate: a word with one nonzero
half is **not** gated, but its update is dropped. The kind `pair_half_zero` isolates exactly that — 0% of
lane-cycles gated, **4,096 of 4,096** updates dropped, and 72,796 operand bits still flipped per op. The
hardware pays 86% of `randn`'s operand switching to compute nothing.

---

## 2. The kinds

`tier 1` is the spine of the kinds table: run those first. `tier 2` is for a window that allows it.
31 kinds are tier 1, 20 are tier 2.

`gated` = of the 4,096 lane-cycles of one accumulate op, how many are gated. `bits/op` = operand bits the
input bus flips in one TensorFMA (`8*dA + sum over the eight lanes of dB`, summed over the 512 transitions).
`dA`, `dB` = mean bits that differ between consecutive operands in the stream order of 1.2 — `dA` for the one
broadcast word, `dB` the mean over the eight lanes.

### fp32 (18 kinds)

| kind | tier | rule | zero words A / B | gated | bits/op | dA | dB |
|---|---|---|---|---|---|---|---|
| `zeros` | 1 | every element +0.0 | 1.000 / 1.000 | 100.0% | 0 | 0.00 | 0.00 |
| `ones` | 1 | every element 1.0 | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `neg_ones` | 2 | every element -1.0: `ones` with the sign bit set | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `pi` | 2 | every element 3.14159274f, the host's `pi` | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `randn` | 1 | standard normal, sigma 1 | 0.000 / 0.000 | 0.0% | 82,214 | 6.88 | 13.19 |
| `randn_small` | 2 | normal, sigma 2^-10 | 0.000 / 0.000 | 0.0% | 82,244 | 6.71 | 13.37 |
| `randn_large` | 2 | normal, sigma 2^10 | 0.000 / 0.000 | 0.0% | 84,896 | 6.96 | 13.76 |
| `uniform01` | 2 | uniform [0, 1): sign 0, exponent below 127 | 0.000 / 0.000 | 0.0% | 77,842 | 6.33 | 12.68 |
| `sparse50` | 1 | randn, half the elements (= words) zero | 0.512 / 0.539 | 77.4% | 74,550 | 6.34 | 11.86 |
| `sparse90` | 1 | randn, 90% of the elements zero | 0.922 / 0.898 | 99.2% | 17,780 | 1.21 | 3.13 |
| `smallint` | 1 | integers -8..7 as floats (the int4 range; 1/16 are zero) | 0.062 / 0.062 | 11.8% | 19,806 | 1.78 | 3.05 |
| `pow2` | 1 | 2^(U{0..16} - 8), the host's `pow2` | 0.000 / 0.000 | 0.0% | 25,414 | 2.11 | 4.10 |
| `bf16trunc` | 1 | randn with the low 16 mantissa bits zeroed | 0.000 / 0.000 | 0.0% | 34,980 | 2.67 | 5.87 |
| `fp16grid` | 2 | randn rounded to the nearest fp16 value | 0.000 / 0.000 | 0.0% | 43,136 | 3.51 | 7.02 |
| `a_randn_b_zeros` | 1 | A randn, B all zero | 0.000 / 1.000 | 100.0% | 27,920 | 6.82 | 0.00 |
| `a_zeros_b_randn` | 2 | A all zero, B randn | 1.000 / 0.000 | 100.0% | 55,798 | 0.00 | 13.62 |
| `randn_sorted` | 1 | `randn`'s own 512 words, in the stream order of least change | 0.000 / 0.000 | 0.0% | 60,856 | 5.07 | 9.78 |
| `nn_like` | 1 | A = relu(randn), B = 0.02*randn | 0.508 / 0.000 | 50.8% | 80,426 | 6.07 | 13.56 |

### fp16 (17 kinds)

| kind | tier | rule | zero words A / B | gated | bits/op | dA | dB | updates dropped |
|---|---|---|---|---|---|---|---|---|
| `zeros` | 1 | every element +0.0 | 1.000 / 1.000 | 100.0% | 0 | 0.00 | 0.00 | 4,096 |
| `ones` | 1 | every element 1.0 (0x3C00) | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 | 0 |
| `neg_ones` | 2 | every element -1.0 (0xBC00) | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 | 0 |
| `randn` | 1 | standard normal, sigma 1 | 0.000 / 0.000 | 0.0% | 84,416 | 6.74 | 13.87 | 0 |
| `randn_small` | 2 | normal, sigma 2^-6 (fp16's exponent is 5 bits) | 0.000 / 0.000 | 0.0% | 91,126 | 7.28 | 14.97 | 0 |
| `uniform01` | 2 | uniform [0, 1) | 0.000 / 0.000 | 0.0% | 77,948 | 6.20 | 12.83 | 0 |
| `sparse50` | 1 | randn, half the **elements** zero | 0.199 / 0.270 | 41.4% | 71,590 | 6.16 | 11.32 | 3,751 |
| `sparse90` | 2 | randn, 90% of the elements zero | 0.793 / 0.805 | 96.1% | 18,412 | 1.56 | 2.94 | 4,096 |
| `wsparse50` | 1 | randn, half the **words** zero | 0.562 / 0.453 | 76.0% | 73,444 | 5.47 | 12.46 | 3,113 |
| `wsparse90` | 2 | randn, 90% of the words zero | 0.855 / 0.930 | 99.0% | 18,192 | 2.36 | 2.09 | 4,056 |
| `smallint` | 2 | integers -8..7 as fp16 | 0.000 / 0.004 | 0.4% | 35,980 | 2.84 | 5.94 | 870 |
| `fp8grid` | 2 | randn rounded to the nearest e4m3 value | 0.000 / 0.000 | 0.0% | 42,486 | 3.29 | 7.08 | 0 |
| `a_randn_b_zeros` | 2 | A randn, B all zero | 0.000 / 1.000 | 100.0% | 28,096 | 6.86 | 0.00 | 4,096 |
| `a_zeros_b_randn` | 2 | A all zero, B randn | 1.000 / 0.000 | 100.0% | 55,806 | 0.00 | 13.62 | 4,096 |
| `pair_half_zero` | 1 | exactly one half of every pair zero: never gated, every update dropped | 0.000 / 0.000 | 0.0% | 72,796 | 5.86 | 11.91 | 4,096 |
| `randn_sorted` | 1 | `randn`'s own words, in the stream order of least change | 0.000 / 0.000 | 0.0% | 61,846 | 5.15 | 9.95 | 0 |
| `nn_like` | 1 | A = relu(randn), B = 0.02*randn | 0.195 / 0.000 | 19.5% | 84,348 | 6.02 | 14.57 | 2,848 |

"updates dropped" = of the 4,096 two-term updates of one op, how many PRM 9.4's rule drops (1.4).

### int8 (16 kinds)

| kind | tier | rule | zero words A / B | gated | bits/op | dA | dB |
|---|---|---|---|---|---|---|---|
| `zeros` | 1 | every byte 0x00 | 1.000 / 1.000 | 100.0% | 0 | 0.00 | 0.00 |
| `ones` | 1 | every byte +1, word 0x01010101 | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `neg_ones` | 1 | every byte -1, word 0xFFFFFFFF: every bit set | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `full` | 1 | uniform -128..127 (**E64's int8 `randn`**) | 0.000 / 0.000 | 0.0% | 100,056 | 7.96 | 16.46 |
| `pos` | 1 | uniform 0..127, sign bit always 0 (**E64's int8 `uniform`**) | 0.000 / 0.000 | 0.0% | 85,642 | 7.02 | 13.89 |
| `smallint` | 1 | uniform -8..7: the int4 range in an int8 byte | 0.000 / 0.000 | 0.0% | 96,552 | 8.10 | 15.47 |
| `ternary` | 1 | -1, 0, +1 equally likely | 0.008 / 0.012 | 2.0% | 86,334 | 6.72 | 14.36 |
| `sparse50` | 1 | `full` with half the **bytes** zero | 0.070 / 0.039 | 10.8% | 76,534 | 6.14 | 12.55 |
| `sparse90` | 2 | `full` with 90% of the bytes zero | 0.672 / 0.668 | 89.7% | 18,184 | 1.39 | 3.05 |
| `wsparse50` | 1 | `full` with half the **words** zero | 0.539 / 0.469 | 74.9% | 73,426 | 5.55 | 12.38 |
| `wsparse90` | 2 | `full` with 90% of the words zero | 0.879 / 0.926 | 98.9% | 16,552 | 1.92 | 2.12 |
| `highbit` | 2 | +64 or -64 (0x40 / 0xC0): one bit apart | 0.000 / 0.000 | 0.0% | 12,148 | 1.00 | 1.97 |
| `gauss_q` | 1 | round(16*randn) clipped to +-127 | 0.000 / 0.000 | 0.0% | 99,352 | 8.00 | 16.26 |
| `a_full_b_zeros` | 2 | A uniform -128..127, B all zero | 0.000 / 1.000 | 100.0% | 32,624 | 7.96 | 0.00 |
| `a_zeros_b_full` | 2 | A all zero, B uniform -128..127 | 1.000 / 0.000 | 100.0% | 64,854 | 0.00 | 15.83 |
| `sorted` | 1 | `full`'s own words, in the stream order of least change | 0.000 / 0.000 | 0.0% | 73,902 | 6.14 | 11.91 |

---

## 3. What the tile statistics already say, before any card runs

Each of these is a prediction E78, E80 and Q130(b) can confirm or refute. Source for every number:
`kinds.json`, key `kinds.<type>.<kind>.stats`.

1. **Magnitude is free; mantissa randomness is not.** fp32 `randn_small` (sigma 2^-10), `randn` (sigma 1) and
   `randn_large` (sigma 2^10) flip 13.37, 13.19 and 13.76 B-side bits a transition. Scaling the data by a
   million changes nothing: the mantissa field carries 11.4, 11.1 and 11.3 of those bits and the exponent
   field only 1.45, 1.61 and 1.93. A blog claim that "big numbers cost more" is wrong on this chip.
2. **Narrowing precision inside a wide format works; narrowing the integer range does not.** Zeroing fp32's
   low 16 mantissa bits (`bf16trunc`) cuts operand flips 2.35x, from 82,214 to 34,980 bits an op. Narrowing
   int8 data to the int4 range (`smallint`, -8..7) cuts them only 1.04x, from 100,056 to 96,552 — because
   two's-complement sign extension makes every sign change flip five bits at once. `smallint`'s per-bit
   statistics show it: bits 3 to 7 all sit at P(1) = 0.4946, the same number, because they are copies of the
   sign. **int4 weights packed in int8 bytes buy almost no switching energy.**
3. **One field at a time.** `pow2` puts every flip in the exponent (4.10 exponent bits, 0.00 mantissa, 0.00
   sign) and `neg_ones` in none at all. These are the single-field anchors E79's price lists are read against.
4. **The two sides are not symmetric, 2:1.** `a_randn_b_zeros` and `a_zeros_b_randn` are both 100% gated, yet
   they flip 27,920 and 55,798 operand bits an op. The A side is one broadcast word changing every second
   cycle; the B side is eight words changing every cycle. Any model that treats "operand entropy" as one
   number will mis-fit these two cells.
5. **Element sparsity is not lane sparsity in the narrow types.** At 50% element sparsity the gated fraction
   is 77.4% (fp32), 41.4% (fp16), 10.8% (int8); at 50% *word* sparsity it is 77.4%, 76.0%, 74.9%. If int8
   `sparse50` does not save power on the card while `wsparse50` does, that is the gate, not the data.
6. **A matmul can do nothing and still pay.** fp16 `pair_half_zero` drops all 4,096 two-term updates to
   PRM 9.4's rule, gates not one lane, and flips 72,796 operand bits — 86% of `randn`'s. It separates "the
   arithmetic is trivial" from "the hardware is idle" completely.
7. **A floor for non-zero data.** int8 `highbit` (+-64) flips 12,148 bits an op, one bit a byte: the cheapest
   non-gated int8 kind here, 8.2x below `full`. `ones`, `neg_ones` and `pi` flip nothing at all.

## 4. The ordered kinds: the same numbers, 26% fewer flips

`randn_sorted` (fp32, fp16) and `sorted` (int8) hold **exactly the same operand multiset** as `randn` / `full`
— verified word by word, `multiset_identical_to_base: true` — permuted into the stream order of least change.
They are the direct test of the "predictable data is faster" claim at the operand-stream level: identical
arithmetic population, identical gating (none), only the order differs.

| type | base | plain value sort | stream-aware minimiser |
|---|---|---|---|
| fp32 | 82,214 | 76,872 (0.935) | **60,856 (0.740)** |
| fp16 | 84,416 | 78,222 (0.927) | **61,846 (0.733)** |
| int8 | 100,056 | 92,290 (0.922) | **73,902 (0.739)** |

A plain sort of each A column and sorted-adjacent B pairing recovers only 7-8% of the flips. Using the actual
stream of 1.2 recovers 26-27%, because:

- the **A** side's cost is a Hamiltonian **path** through the sixteen words of a word-column (each word held
  two micro-ops) — minimised by greedy nearest neighbour from all sixteen starts plus 2-opt;
- the **B** side's cost is the sum of **eight pair distances** per line, because lane `l` alternates between
  columns `l` and `l+8` for 31 of its 32 micro-ops in a k-group — minimised **exactly**, by dynamic
  programming over the minimum-weight perfect matching of the sixteen words.

The A-side path is a local optimum, not a proved one; the B-side matching is exact. The 16 group-boundary
transitions (one in 32) are not optimised. So 0.740 is an upper bound on the achievable flip count, not a
lower bound on what ordering can do.

## 5. Departures from the kinds list as first drafted

Six, all made before any tile was written.

1. **Added `wsparse50` and `wsparse90` to fp16 and int8.** The draft list said only "sparse50, sparse90" for
   those two types without naming a granularity. Because the gate is 32-bit-word-wide (1.3), element-granular
   sparsity gates a quarter of fp16 lanes and a sixteenth of int8 lanes at 50%: without the word-granular
   pair, E78 and E80 cannot separate "the values are sparse" from "the lanes are off", which is the headline
   question of the whole run. `sparse*` is element-granular and `wsparse*` word-granular, stated in each
   kind's `rule`.
2. **Added `a_zeros_b_randn` (fp16) and `a_zeros_b_full` (int8).** The fp32 list already carried both
   orientations; the narrow lists carried only one. The two are not equivalent — the measured split is 2:1
   (section 3.4) — and E65/E67 ran separate B-side and A-side price lists for the same reason.
3. **`randn_sorted` / `sorted` use a stream-aware minimiser, not a value sort.** The draft said "ordered to
   minimise the Hamming distance between consecutive operands in the unit's stream order"; a value sort does
   that badly (0.935 against 0.740, section 4). Both keep the operand multiset identical.
4. **Added a tier to every kind** (31 tier 1, 20 tier 2), so a card lane whose window closes has a defined
   subset rather than an arbitrary truncation.
5. **The int8 names.** E64 ran int8 under `--values randn` (uniform -128..127) and `--values uniform`
   (uniform 0..127); the draft named them `full` and `pos`. Kept, because the draft's names say what the data
   is — but **E64's three int8 cells join this matrix as `full`, `pos` and `zeros`/`ones`**, and E78 must say
   so or the comparison with 23 Oct is lost.
6. **fp32 `smallint` is not a zero-free kind.** The range -8..7 contains 0, so 1/16 of its words are zero and
   11.8% of lane-cycles gate. It is still the right kind (it is the int4 range as floats, matching int8's
   `smallint`), but it may not be used as a "dense small values" control. `pow2` and `bf16trunc` are the
   zero-free low-entropy fp32 kinds.

## 6. Files

| path | what |
|---|---|
| `make_kinds.py` | the generator, the spec and the statistics, in one file. `--check` re-decodes everything |
| `kinds.json` | the spec: `facts` (layout, stream order, gating, the fp16 rule, each with its source), `types`, and per kind the rule, tier, sha256 of the file and of each tile half, and the statistics |
| `tiles/<type>/<kind>.bin` | 2,048 bytes: the A tile then the B tile, 1,024 each, in that type's layout |

Per tile, `kinds.json` records: `zero_word_frac` and `zero_elem_frac` per side; `p1_word[32]` and
`p1_elem[W]` (W = 32/16/8, two's complement for int8, bit 7 the sign); `hamming` per side, total and per
field (sign / exponent / mantissa, or sign / magnitude for int8); `bus_bits_per_op`; `gated_lane_cycles`;
for fp16 `pair_any_zero`; for int8 `int8_twos_complement` (per-bit P(1), P(negative), mean value, mean
popcount).

Seed 20261031, derived per (type, kind) by sha256 of the name, so any one kind can be regenerated alone and
adding a kind never moves another.

**Replaying an fp16 or int8 tile in `rtl-sim/fma_toggle`** gives the right operand words and the right gating
— `txfma_top` is the fp32 unit, so quote its bus and gate counts for those two types, not its
multiplier-tree counts.
