# Q130(s): the kinds of numbers — the spec, the generator and the tiles

Sat 31 Oct 2026 (week 44). **51 operand tile pairs** — 18 fp32, 17 fp16, 16 int8 — one per *kind of number*,
each 2,048 bytes of raw operands ready for the card and for the RTL, with every tile's bit statistics measured
and frozen in [`kinds.json`](kinds.json).

> **Revision 2, the same day.** The first version of this spec assumed one issue stream and one gate rule for
> all three types. That is right for fp32 and fp16 and **wrong for int8**, which runs on a different unit with
> half as many micro-ops and a gate twice as wide. Every int8 figure here was re-derived; the two value-sort
> baselines of section 4 and a sampling band for every random kind are now committed as well, and the tier
> counts are corrected. Section 6 lists every correction, with its source. **int8 figures from revision 1 must
> not be quoted.**

This is the input the rest of Q130 runs on: **E78** (the energy matrix, aifoundry3, 600 MHz pinned), **E80**
(speed under the governor, aifoundry2), **Q130(b)** (RTL toggle counts) and **Q130(c)** (the empirical model).
Nothing here touches a card. Reproduce it with

```bash
python3 tools/claims-v3/kinds/make_kinds.py tools/claims-v3/kinds --check   # ~1 min, numpy only
python3 tools/claims-v3/kinds/make_kinds.py tools/claims-v3/kinds --replicates 0   # tiles only, 4 s
python3 tools/claims-v3/kinds/make_kinds.py --list                          # the kinds and their rules
```

and run one on a card, or in the RTL bench, with

```bash
sparsity_host --test fma --type fp32 --values file:tools/claims-v3/kinds/tiles/fp32/randn_sorted.bin
python3 rtl-sim/fma_toggle/tiles.py x out.hex --from-bin tools/claims-v3/kinds/tiles/fp32/randn_sorted.bin
```

`--check` passes: every tile decodes back to its intended element values through an independently written
decoder, every `*_sorted` tile is a verified permutation of its base kind's operand multiset, the vectorised
stream used for the replicate draws reproduces the explicit loop stream exactly in all three types, and the
fp32 kinds that share a name with one of the host's own `--values` patterns have per-bit one-probabilities
that agree with the host's distribution within 5 sigma (`checks.fp32_vs_host_builtin_p1` in `kinds.json`; the
deterministic `zeros`, `ones` and `pi` agree bit-exactly).

---

## 1. Five facts the other lanes must not get wrong

All five are quoted with their sources in `kinds.json` under `facts`, and all were confirmed from more than
one place. **Facts 2 and 3 are per type**: fp32 and fp16 share a stream and a gate, int8 has its own.

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

### 1.2 The stream order — and it is not the same stream in all three types

**fp32 and fp16 (txfma).** PRM 9.4, `external/core-et/rtl/shire/minion/vpu/vpu_tensorfma.v` (the pointer loop
at lines 717-752), and the bench's own `one_op` (`rtl-sim/fma_toggle/tb.sv` lines 92-110 and 144-149):

```
for k in 0..15:                 # the k-group: B line k, A word k
  for i in 0..15:               # A row
    for h in 0, 1:              # C columns 0-7, then 8-15
      A operand = Aword[i][k], BROADCAST to all eight lanes
      B operand of lane l = Bword[k][8*h + l]
```

512 micro-ops, one a cycle, then a gap: 546 cycles an op. Therefore

- the **A** word is held for two consecutive micro-ops and then walks **down a word-column of A**: 256 of the
  512 transitions are free, and the other 256 are steps down a column;
- lane `l`'s **B** word **alternates every cycle** between column `l` and column `l+8` of the *same* B line,
  sixteen times, before the next k-group: 31 of each lane's 32 transitions in a k-group cost exactly
  `d(Bword[k][l], Bword[k][l+8])`.

**int8 (TIMA) is a different stream.** `fma_exec_last_b_col` is forced true by `req_int8`
(`vpu_tensorfma.v:412`) and `fma_exec_b_col_next` never advances — `// First go to next B col block (for
INT8, we do all B cols at once)` (`:717-718`) — so there is no `h` half-pass loop:

```
for p in 0..15:                 # the k-group: B line p, A word p
  for i in 0..15:               # A row            -- NO h loop
    A operand = Aword[i][p], BROADCAST to all SIXTEEN column slots
    B operand of column slot j = Bword[p][j]
```

**256 micro-ops, and that is the only count that fits the measurement.** int8 takes **318** cycles an op
against fp32's and fp16's 546, measured on every card and registered PASS
(`docs/findings/05-claims.md:463`, E36 318.02-318.04; `:480`, E39 318.00). 512 micro-ops at one a cycle cannot
retire in 318 cycles; 256 can. The MAC count works out either way (16x16x64 = 16,384 = 256 micro-ops x 16
column slots x 4 bytes), so the cycle count is what discriminates. int8 also runs on another unit entirely:
`clock_en_txfma = (enabled_int & ~req_int8) | …`, `clock_en_tima = (enabled_int & req_int8) | …`
(`:157-166`), and `fma_en` is only clocked when `~req_int8` (`:626-628`). So in int8

- the **A** word changes **every** micro-op, walking down a word-column of A — none of the 256 transitions is
  free, which is the opposite of the fp32 picture;
- the **B** line is **held for all sixteen micro-ops** of its k-group, so the only B cost is the sixteen line
  boundaries, where all sixteen words change at once.

**int8's operand bus is therefore A-dominated**: for `full`, dA 15.93 bits against dB 0.99, and the A side
carries 94% of `bus_bits_per_op`.

**Sorting the rows of the matrix is not the same thing as ordering the stream.** For the A side the right
object is a path down each word-column, in all three types; for the B side it is a *pairing* of column `l`
with column `l+8` inside each line (fp32, fp16) or an *assignment* across the sixteen line boundaries (int8).
Section 4 measures what that distinction is worth.

This implementation was cross-checked against the committed flip counter the Hamming-ladder experiments
(E60, E65, E67, E70) were built with: for all 18 fp32 kinds, `bus_bits_per_op` here equals
`tools/claims-v3/hl/make_hl.py`'s `fma_flips(A, B)["total"]` exactly. The two agree on the order and on the
convention (cyclic over the 512 micro-ops, the last against the next op's first), so **the fp32 numbers** are
directly comparable with the E60/E65/E67/E70 per-bit price lists. The int8 numbers are not: `make_hl.py` is a
txfma counter. The sibling lane E79 sidesteps this by counting only quantities invariant to the grouping
width (`tools/claims-v3/hlp/README.md:64-66`); the word-transition counts here are not invariant, which is
why int8's `hamming` and `bus_bits_per_op` carry a `provisional` flag in `kinds.json` and the gated figures
do not.

**What is provisional, and what is not.** The 256 micro-ops and the sixteen-slot bus follow from the loop RTL
and the measured cycle count, but there is no int8 bench and no cycle-accurate simulation here, so they are a
reconstruction. The **gated** figures do not depend on it: they depend only on the set of (A word, B
column-pair) combinations, which is the same 2,048 whether or not the `h` loop exists, and on the gate rule of
1.3. The **hamming** and **bus** figures do depend on it, and every int8 kind in `kinds.json` says so.

### 1.3 Zero gating is word-wide, not element-wide — and in int8 it is two words wide

`external/core-et/rtl/shire/minion/vpu/vpu_ctrl.v` lines 1229-1234 compute the flags on a full
`VPU_DATA_S_SZ` = 32-bit word:

```verilog
f3_zero_data_a   = {`VPU_LANE_NUM{(f3_tena_regfile_wdata_l == `VPU_DATA_S_SZ'b0)}};
f3_zero_data_b[i] = (f3_tenb_regfile_wdata_l[`VPU_DATA_S_SZ * i +: `VPU_DATA_S_SZ] == `VPU_DATA_S_SZ'b0);
```

and lines 802-818 combine them into the eight-bit `ex_tensor_zero_mask`, which clears `ex_txfma_valid`
(`:834-840`) or `ex_tima_valid` (`:824-832`), only for `VPU_FCMD_MADD`:

```verilog
ex_tensor_zero_mask = ex_tensora_zero_mask_mux                                  // TENA
                    | ex_tensorb_zero_mask_tima0 & ex_tensorb_zero_mask_tima1;  // TENB
```

**That AND is the part the first version of this spec missed.** `ex_tensorb_zero_mask_tima0` reads TenB row
`raddr` and `tima1` reads `raddr | 1`.

- For **fp32 and fp16**, `ex_tima_valid_unqual` is 0, so both terms address the same row (`ex_ra2_ten`) and
  the AND is a no-op. The gate is one 32-bit word per lane, exactly as the bench says (`tb.sv:56`):
  `lane_valid[l] = uop_valid & (uop_mul | ((uop_a != 32'b0) & (uop_b[l] != 32'b0)))`.
- For **int8**, `s1_tima_tenb_raddr = {fma_exec_b_rd_ptr, 1'b0}` (`vpu_tensorfma.v:863`), so `raddr` and
  `raddr | 1` are the **two halves of one 64-byte B line** — a TenB row is
  `VPU_DATA_SZ = VPU_LANE_NUM * VPU_DATA_S_SZ` = 256 b = 8 words = half a line
  (`minion_defines.vh:189-192`). Gate bit `l` therefore covers **columns `l` and `l+8` together**, and
  `ex_tensorb_zero_mask_tima1[l]` is only forced to 1 when `~ex_tima_mask[l][1]`, which at `cols_b = 3` is
  never (`ex_tima_mask[l][t] = ex_fma_mask[(l>>1)+(t<<2)]`, all ones; `vpu_tensorfma.v:654-663, 899`). Both
  TIMAs are live and the AND is real.

**There is one zero test and it is 32 bits wide in every type** (`:1229-1234`, taken when the tensor operand
register is written). What differs per type is *how many of those tests one gate decision needs*. So the
word-zero rate is `p^E` in all three types — but the *gated* rate in int8 is not: it needs both words.

| type | zero test | tests a gate decision needs | B elements that must be zero | word-zero vs gate rate |
|---|---|---|---|---|
| fp32 | 32 bits | 1 | 1 | `p` / `p` |
| fp16 | 32 bits | 1 | 2 (both halves) | `p²` / `p²` |
| int8 | 32 bits | **2, ANDed** | **8 bytes** (the column pair) | `p⁴` / **`p⁸`** |

Quoting int8's word-zero rate as its gated rate is the same mistake in a different place: at `p = 0.5` that
is 6.25% of words against a 6.7% gated fraction — close by coincidence — but at `p = 0.9` it is 65.6% of
words against an 82.2% gated fraction, because the A side gates too.

*Which pair?* The RTL says columns (`l`, `l+8`), twice over: `ex_tensor_zero_mask_ext[l][t]` uses the same
bit `l` for both TIMAs while `tima0` reads TenB row `raddr` (columns 0-7) and `tima1` row `raddr|1` (columns
8-15); and the enable mapping `ex_tima_mask[l][t] = ex_fma_mask[(l>>1)+(t<<2)]` puts unit (`l`, `t`) on column
`2*((l>>1)+4t) + (l&1)`, which is column `l` at `t = 0` and column `l+8` at `t = 1`. **E79's amendment A4
instead states the grouping as the eight contiguous bytes of columns (`2l`, `2l+1`).** Both readings are
"eight bytes must be zero", so every int8 kind here also carries `stats.gated_lane_frac_alt_grouping` under
A4's reading: the largest disagreement over the 16 kinds is 0.007 (`sparse50`, 0.070 against 0.078), well
inside that kind's single-tile sd of 0.015. **No claim in this spec depends on which grouping is right**, and
the question is left open for Q130(b). A4's *load-bearing* fact — 256 micro-ops, no half-pass alternation in
int8 — is a card measurement (pass 7910: int8's half-boundary ladder reads 0.003 ± 0.02 W where fp16 reads
4.73 W) and agrees with 1.2 exactly.

Two further consequences, the same in all three types:

- **the A-side flag is one bit broadcast to all eight gate bits**, so a zero A word gates the whole micro-op,
  while a zero B word gates one bit;
- **a lane gates only when the whole gate unit is zero** — never when some of its elements are zero.

So the same 50%-element-sparsity *rule* gates **75.0% of column-slot-cycles in fp32, 43.7% in fp16 and only
6.7% in int8** (design-time expectation over 400 draws of the rule; the committed `sparse50` tiles realise
77.4%, 41.4% and 7.0%, see section 2 and `replicates` in `kinds.json`). At 50% **word** sparsity it is 75.0%
(fp32, where word and element sparsity are the same thing), 74.9% (fp16) and — because int8's gate wants
*both* words of the pair — still only 62.4%. That is why this spec
carries both families: `sparse50`/`sparse90` zero **elements** (the data property, what a user means by
sparsity) and `wsparse50`/`wsparse90` zero whole **words** (the gate's property in fp32 and fp16). Quoting
one for the other would wreck E78's sparsity row.

Also: the first op of a launch is a multiply pass and is never gated, so `gated_lane_cycles` below describes
an accumulate op, which is all but one of them. In int8 the gate additionally needs
`ex_tima_ren3 && ~ex_tima_last_pass` (`vpu_ctrl.v:827`).

### 1.4 fp16's two-term rule is arithmetic, not gating

PRM 9.4's pseudo-code applies the two-term update `c += a1*b1 + a2*b2` only when **all four** of `a1, a2, b1,
b2` are nonzero (host `expectC(..., literal=true)`). That is separate from the gate: a word with one nonzero
half is **not** gated, but its update is dropped. The kind `pair_half_zero` isolates exactly that — 0% of
lane-cycles gated, **4,096 of 4,096** updates dropped, and 72,796 operand bits still flipped per op. The
hardware pays 86% of `randn`'s operand switching to compute nothing.

### 1.5 A `--values file:` run prints the WRONG metadata and does no math check

`workloads/sparsity/host/main.cpp:587-591`: `makeTiles()` runs first, fills `t.A` / `t.B` with the pattern's
own random values and computes `nnzA` and `zeroPairsOneSided` from them; `fillValues()` then overwrites only
the raw bytes `t.a` / `t.b` from the file and returns. So on every kind run:

- the `SPARSITY {...}` line's `nnz_a`, `a_elems` and `fp16_one_sided_pairs` describe the **discarded** random
  fill, not the tile. **Ignore them.** Use `zero_elem_frac`, `zero_word_frac` and `pair_any_zero` from
  `kinds.json` instead;
- `rawValues` is true, so `check` is forced to `"unchecked"` (`:614`) and `checkC` never runs. **A kind run
  verifies no arithmetic at all.** In particular the fp16 two-term rule that fact 1.4 cites
  `expectC(..., literal=true)` for is *not* evaluated on a kind run. To confirm that rule on the card, run
  `--pattern pair` **without** `--values file:`.

---

## 2. The kinds

`tier 1` is the spine of the kinds table: run those first. `tier 2` is for a window that allows it.
**30 kinds are tier 1, 21 are tier 2** (`kinds.json` `counts.tier1_total` / `counts.tier2_total`, which the
generator asserts sum to 51 — revision 1's prose said 31 and 20, which its own `counts` already contradicted).

`gated` = of the 4,096 **column-slot-cycles** of one accumulate op, how many are gated. There are eight gate
bits a micro-op in every type, so that is 4,096 decisions in fp32 and fp16 and 2,048 in int8, each covering
two column slots; the fraction is the same either way. `bits/op` = operand bits the input bus flips in one
TensorFMA (`slots*dA + sum over the slots of dB`, summed over the transitions, `slots` = 8 / 8 / 16 — and see
section 3.4 on what that A-side multiplier is and is not). `dA`, `dB` = mean bits that differ between
consecutive operands in that type's stream order (1.2) — `dA` for the one broadcast word, `dB` the mean over
the column slots.

Every figure below is **one tile**. For every kind whose rule is random, `kinds.json` also carries
`replicates`: the same rule re-drawn with 400 independent seeds, giving the design-time expectation and the
band a single tile lands in. E78 and E80 run one tile a cell, so **the tile's count is itself a draw** —
quote the expectation for the rule and the tile's figure for the run.

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

**Under the TIMA stream and the column-pair gate of 1.2 and 1.3** — 256 micro-ops of 16 column slots, A
changing every cycle, the B line held sixteen. `gated` is a count, not provisional. `bits/op` and `dA`/`dB`
depend on the reconstructed stream and on the 16-slot A convention: they are a design-time model, flagged
`provisional` per kind in `kinds.json`, and must not be quoted as a measurement.

| kind | tier | rule | zero words A / B | gated | bits/op | dA | dB |
|---|---|---|---|---|---|---|---|
| `zeros` | 1 | every byte 0x00 | 1.000 / 1.000 | 100.0% | 0 | 0.00 | 0.00 |
| `ones` | 1 | every byte +1, word 0x01010101 | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `neg_ones` | 1 | every byte -1, word 0xFFFFFFFF: every bit set | 0.000 / 0.000 | 0.0% | 0 | 0.00 | 0.00 |
| `full` | 1 | uniform -128..127 (**E64's int8 `randn`**) | 0.000 / 0.000 | 0.0% | 69,312 | 15.93 | 0.99 |
| `pos` | 1 | uniform 0..127, sign bit always 0 (**E64's int8 `uniform`**) | 0.000 / 0.000 | 0.0% | 61,096 | 14.04 | 0.88 |
| `smallint` | 1 | uniform -8..7: the int4 range in an int8 byte | 0.000 / 0.000 | 0.0% | 70,526 | 16.20 | 1.02 |
| `ternary` | 1 | -1, 0, +1 equally likely | 0.008 / 0.012 | 0.8% | 58,798 | 13.45 | 0.91 |
| `sparse50` | 1 | `full` with half the **bytes** zero | 0.070 / 0.039 | 7.0% | 53,480 | 12.27 | 0.78 |
| `sparse90` | 2 | `full` with 90% of the bytes zero | 0.672 / 0.668 | 82.2% | 12,144 | 2.77 | 0.19 |
| `wsparse50` | 1 | `full` with half the **words** zero | 0.539 / 0.469 | 64.4% | 48,766 | 11.09 | 0.81 |
| `wsparse90` | 2 | `full` with 90% of the words zero | 0.879 / 0.926 | 98.0% | 16,316 | 3.84 | 0.14 |
| `highbit` | 2 | +64 or -64 (0x40 / 0xC0): one bit apart | 0.000 / 0.000 | 0.0% | 8,664 | 1.99 | 0.12 |
| `gauss_q` | 1 | round(16*randn) clipped to +-127 | 0.000 / 0.000 | 0.0% | 69,544 | 15.99 | 0.99 |
| `a_full_b_zeros` | 2 | A uniform -128..127, B all zero | 0.000 / 1.000 | 100.0% | 65,248 | 15.93 | 0.00 |
| `a_zeros_b_full` | 2 | A all zero, B uniform -128..127 | 1.000 / 0.000 | 100.0% | 4,140 | 0.00 | 1.01 |
| `sorted` | 1 | `full`'s own words, in the stream order of least change | 0.000 / 0.000 | 0.0% | 53,346 | 12.27 | 0.75 |

The int8 column that moved most between revisions is the A/B pair: under the txfma stream the two came out
32,624 and 64,854 (B-heavy, like fp32); under the TIMA stream they are 65,248 and 4,140 — **A-heavy, and by
nearly 16:1**, because the A word changes every cycle while the B line is held sixteen. The direction of the
asymmetry is a property of the stream, not of the data.

---

## 3. What the tile statistics already say, before any card runs

Each of these is a prediction E78, E80 and Q130(b) can confirm or refute. Source for every number:
`kinds.json`, key `kinds.<type>.<kind>.stats`.

1. **Magnitude is free; mantissa randomness is not.** fp32 `randn_small` (sigma 2^-10), `randn` (sigma 1) and
   `randn_large` (sigma 2^10) flip 13.37, 13.19 and 13.76 bits **per lane per step on the B operand** —
   82,244, 82,214 and 84,896 operand bits per op. Scaling the data by a million changes nothing: the mantissa
   field carries 11.4, 11.1 and 11.3 of those per-step bits and the exponent field only 1.45, 1.61 and 1.93.
   A blog claim that "big numbers cost more" is wrong on this chip.
2. **Narrowing precision inside a wide format works; narrowing the integer range buys nothing at all.**
   Zeroing fp32's low 16 mantissa bits (`bf16trunc`) cuts operand flips **2.35x**, from 82,214 to 34,980 bits
   an op. Narrowing int8 data to the int4 range (`smallint`, -8..7) cuts them by **nothing**: 70,526 against
   `full`'s 69,312, and over 400 draws of each rule the two means are 69,617 and 69,586 — a ratio of
   **1.000**, with a single-tile sd of 1,315 and 730. Two's-complement sign extension is why: every sign
   change flips five bits at once, so the five high bits of a `smallint` byte all sit at P(1) = 0.4946, the
   same number, because they are copies of the sign. **int4 weights packed in int8 bytes buy no switching
   energy whatsoever.** (Revision 1 reported 1.04x from the txfma stream; the corrected stream makes the point
   stronger, not weaker.)
3. **One field at a time.** `pow2` puts every flip in the exponent (4.10 exponent bits, 0.00 mantissa, 0.00
   sign) and `neg_ones` in none at all. These are the single-field anchors E79's price lists are read against.
4. **The two sides are not symmetric, and the reason is the hold, not the broadcast.** fp32
   `a_randn_b_zeros` and `a_zeros_b_randn` are both 100% gated, yet they flip 27,920 and 55,798 operand bits
   an op. The reason is that **the A word only changes every second micro-op, so it toggles half as often as
   B**: the ratio is exactly mean dB / mean dA = 13.62 / 6.82 = 1.9985, and `bus_bits_per_op` applies the
   same x8 broadcast multiplier to both sides, so the broadcast contributes *nothing* to the ratio. In int8,
   where A changes every cycle and B is held sixteen, the same pair inverts to 65,248 against 4,140. Any
   model that treats "operand entropy" as one number will mis-fit these cells — and any model that reads the
   2:1 as "one word against eight" has the mechanism wrong. **The x8 A-side multiplier is a counting
   convention inherited from `tb.sv` and `make_hl.py`, not a measurement; E78 must validate it before any of
   this is quoted as energy** (`kinds.json` `facts.hamming_convention`; E70 measured shared-wire carry-over
   at 1.246).
5. **Element sparsity is not lane sparsity in the narrow types.** For the 50%-element-sparsity *rule* the
   expected gated fraction is **75.0%** (fp32), **43.7%** (fp16), **6.7%** (int8); for the 50%-*word* rule it
   is 75.0%, 74.9%, 62.4%. Those are expectations over 400 draws; one tile has an sd of about 0.022, 0.029
   and 0.015, so the committed tiles' 77.4 / 41.4 / 7.0% and 75.0(=`sparse50`) / 76.0 / 64.4% all sit inside
   their bands. If int8 `sparse50` does not save power on the card while `wsparse50` does, that is the gate,
   not the data — and note that in int8 even `wsparse50` leaves a third of the lanes live, because the gate
   wants both words of the column pair.
6. **A matmul can do nothing and still pay.** fp16 `pair_half_zero` drops all 4,096 two-term updates to
   PRM 9.4's rule, gates not one lane, and flips 72,796 operand bits — 86% of `randn`'s. It separates "the
   arithmetic is trivial" from "the hardware is idle" completely.
7. **A floor for non-zero data.** int8 `highbit` (+-64) flips 8,664 bits an op, one bit a byte: the cheapest
   non-gated int8 kind here, 8.0x below `full`. `ones`, `neg_ones` and `pi` flip nothing at all.

## 4. The ordered kinds: the same numbers, 23-27% fewer flips

`randn_sorted` (fp32, fp16) and `sorted` (int8) hold **exactly the same operand multiset** as `randn` / `full`
— verified word by word, `multiset_identical_to_base: true` — permuted into the stream order of least change.
They are the direct test of the "predictable data is faster" claim at the operand-stream level: identical
arithmetic population, identical gating (none), only the order differs.

All five columns below are computed by `make_kinds.py` on every build and written to `kinds.json` under
`sort_baselines`, each under its own type's stream, so `--check` reproduces every one of them. (In revision 1
the two sort baselines lived only in this table and in a scratch script, so nothing could reproduce them.)

| type | base | naive value sort | value sort that knows the pairing | stream-aware minimiser |
|---|---|---|---|---|
| fp32 | 82,214 | 84,248 (**1.025**) | 76,872 (0.935) | **60,856 (0.740)** |
| fp16 | 84,416 | 83,412 (0.988) | 78,222 (0.927) | **61,846 (0.733)** |
| int8 | 69,312 | 67,426 (0.973) | — (the pair has no meaning) | **53,346 (0.770)** |

Read that first column carefully. **A naive value sort — sort each A word-column, sort each B line, in
place — makes fp32 WORSE than not sorting at all** (1.025), and buys 1-3% in the other two types. It is only
when the sort is told about the stream that anything happens: dealing each sorted B line into the (`l`,
`l+8`) pairs the fp32/fp16 lane alternates between already recovers 6-7% (0.935 / 0.927), and minimising
against the real stream recovers 23-27%. The honest version of "sorted data is cheaper" is therefore
**"ordering for the hardware's stream is cheaper; sorting the numbers is not"**. Because:

- the **A** side's cost is a Hamiltonian **path** through the sixteen words of a word-column (held two
  micro-ops in fp32/fp16, one in int8 — the same objective) — minimised by greedy nearest neighbour from all
  sixteen starts plus 2-opt;
- the **B** side's cost in fp32 and fp16 is the sum of **eight pair distances** per line, because lane `l`
  alternates between columns `l` and `l+8` for 31 of its 32 micro-ops in a k-group — minimised **exactly**,
  by dynamic programming over the minimum-weight perfect matching of the sixteen words;
- the **B** side's cost in int8 is **only the sixteen line boundaries**, because the line is held for its
  whole k-group — a chain of assignment problems down the lines, solved greedily with 2-swap over three
  sweeps. int8's bus is A-dominated anyway (the B side is 1.4% of it), so this part moves little.

The A-side path is a local optimum, not a proved one; the fp32/fp16 B-side matching is exact and the int8
B-side assignment is not. The 16 group-boundary transitions (one in 32) are not optimised in fp32 or fp16. So
0.740 is an upper bound on the achievable flip count, not a lower bound on what ordering can do.

Each ratio is also one draw: over 12 re-draws of the whole pipeline the minimiser's own figure has a
single-tile sd of about 590 (fp32), 580 (fp16) and 450 (int8) bits an op — about 1% — so quote 0.74 / 0.73 /
0.77, not four digits.

## 5. Departures from the kinds list as first drafted

Six. The drafted list is the orchestrator's brief for this lane, which is not a committed file, so there is
nothing in git to diff these against: read them as what this spec does differently from that brief, not as a
dated amendment trail. (Revision 1 said "all made before any tile was written"; the spec, the generator, the
tiles and the statistics all landed in one commit, so that ordering was not verifiable and the claim is
withdrawn. Nothing here needs it: no card ran, so no pre-registration clock was running. **For E78 and E80
the clock starts at this spec's commit** — their frozen predictions must cite it and be pushed before the
Discord claim and the first launch.)

1. **Added `wsparse50` and `wsparse90` to fp16 and int8.** The draft list said only "sparse50, sparse90" for
   those two types without naming a granularity. Because the gate is at least a whole 32-bit word wide (1.3),
   50% element sparsity gates an expected 43.7% of fp16 lanes and 6.7% of int8's: without the word-granular
   pair, E78 and E80 cannot separate "the values are sparse" from "the lanes are off", which is the headline
   question of the whole run. `sparse*` is element-granular and `wsparse*` word-granular, stated in each
   kind's `rule`. **int8 needs a third rule and does not yet have one**: because its gate wants both words of
   the column pair, even `wsparse50` leaves 36% of the lanes live, so a pair-granular kind is the only one
   that would gate half of int8's lanes. Recorded as an open issue rather than added here, because adding a
   kind changes the matrix other lanes have already read.
2. **Added `a_zeros_b_randn` (fp16) and `a_zeros_b_full` (int8).** The fp32 list already carried both
   orientations; the narrow lists carried only one. The two are not equivalent — the split is 2:1 B-heavy in
   fp32 and fp16 and nearly 16:1 A-heavy in int8 (section 3.4) — and E65/E67 ran separate B-side and A-side
   price lists for the same reason.
3. **`randn_sorted` / `sorted` use a stream-aware minimiser, not a value sort.** The draft said "ordered to
   minimise the Hamming distance between consecutive operands in the unit's stream order"; a value sort does
   that badly, and a naive one makes fp32 worse than no sort at all (1.025 and 0.935 against 0.740,
   section 4). Both keep the operand multiset identical.
4. **Added a tier to every kind** (30 tier 1, 21 tier 2), so a card lane whose window closes has a defined
   subset rather than an arbitrary truncation.
5. **The int8 names.** E64 ran int8 under `--values randn` (uniform -128..127) and `--values uniform`
   (uniform 0..127); the draft named them `full` and `pos`. Kept, because the draft's names say what the data
   is — but **E64's three int8 cells join this matrix as `full`, `pos` and `zeros`/`ones`**, and E78 must say
   so or the comparison with 23 Oct is lost.
6. **fp32 `smallint` is not a zero-free kind.** The range -8..7 contains 0, so 1/16 of its words are zero and
   11.8% of lane-cycles gate. It is still the right kind (it is the int4 range as floats, matching int8's
   `smallint`), but it may not be used as a "dense small values" control. `pow2` and `bf16trunc` are the
   zero-free low-entropy fp32 kinds.

## 6. Corrections made in revision 2 (same day, after verification)

A verification pass over revision 1 re-derived every statistic from the committed tiles and read the int8 path
out of the RTL. Eight corrections followed. The tiles themselves survived: **50 of the 51 are byte-identical
to revision 1**, and the fp32 cross-check against `make_hl.py fma_flips` still holds exactly for all 18 fp32
kinds.

1. **int8's stream was wrong (critical).** Revision 1 asserted the txfma stream — 512 micro-ops, the `h`
   half-pass loop, eight lanes — for all three types, while recording int8's measured 318 cycles an op in the
   same object. The two cannot both be true. int8 runs on TIMA with all sixteen B columns in one micro-op
   (`vpu_tensorfma.v:412`, `:717-718`), 256 micro-ops, and with the txfma clock off (`:157-166`). Every int8
   `hamming` and `bus_bits_per_op` figure changed; the A/B asymmetry inverted. Section 1.2 now gives both
   streams, and `facts.stream_order` is per type.
2. **int8's gate was wrong (critical).** `ex_tensor_zero_mask` ANDs **two** TenB rows, which for int8 are the
   two halves of one B line, so the gate unit is the column pair (`l`, `l+8`) = **eight bytes**, not four
   (`vpu_ctrl.v:802-818`, `vpu_tensorfma.v:863, 899`). int8's gated fractions moved: `sparse50` 10.8% ->
   **7.0%**, `wsparse50` 74.9% -> **64.4%**, `sparse90` 89.7% -> 82.2%, `wsparse90` 98.9% -> 98.0%. The
   headline gets *stronger*: the gate is even coarser in int8 than revision 1 claimed. (The zero *test* is
   still 32 bits wide in every type, as the sibling lane Q130(g) says — what needs two of them, ANDed, is an
   int8 *gate decision*. Q130(g)'s int8 row quotes the word-zero rate `~p⁴` as the gating rate; for a lane it
   is `p⁸`, and that row is worth a second look before E78 reads it.)
3. **`microops_per_op` and the denominators are per type**, not 512/4,096 for all three.
4. **The claim that an int8 tile replays correctly in `rtl-sim/fma_toggle` is withdrawn.** That bench is
   txfma with the `h` loop and the 32-bit gate — it has no int8 path, so it would report the operand words
   right and the gate and bus wrong.
5. **int8 `sorted` was ordered for the wrong stream** and has been regenerated against the TIMA stream (the
   one tile of the 51 whose bytes changed; its sha256 in `kinds.json` is the new one). It reaches 0.770 of
   `full`; the old ordering, scored under the correct stream, reached only 0.784.
6. **The tier counts were wrong in prose:** 30 tier 1 and 21 tier 2, not 31 and 20. `kinds.json` `counts`
   now carries `tier1_total` and `tier2_total`, and the generator asserts they sum to 51.
7. **The two value-sort baselines are committed** (`sort_baselines` in `kinds.json`, computed on every
   build). Revision 1's table gave one of them, 0.935, as "plain value sort"; it is a sort that already knows
   the (`l`, `l+8`) pairing. A genuinely naive value sort is 1.025 in fp32 — worse than no sort. Section 4.
8. **Every random kind carries a sampling band** (`replicates`, 400 draws of the rule), because E78 and E80
   run one tile a cell and revision 1 quoted single-tile counts as the law of the format. Two further
   wording fixes: the magnitude ladder's 13.37 / 13.19 / 13.76 are **per-lane per-step B-side** bits, not
   per-op totals; and "the same 50%-sparse data" was three independent draws of the same *rule*, since the
   seed is per (type, kind). Section 1.5 is new: it says what a `--values file:` run does to the host's own
   metadata and math check.

## 7. Files

| path | what |
|---|---|
| `make_kinds.py` | the generator, the spec and the statistics, in one file. `--check` re-decodes everything and re-derives the vectorised stream against the explicit one |
| `kinds.json` | the spec: `facts` (layout, the per-type stream order, the per-type gate, the fp16 rule, the Hamming convention, the replay caveat — each with its source), `types`, `sort_baselines`, `counts`, and per kind the rule, tier, sha256 of the file and of each tile half, the statistics and the replicate bands |
| `tiles/<type>/<kind>.bin` | 2,048 bytes: the A tile then the B tile, 1,024 each, in that type's layout |

Per tile, `kinds.json` records: `zero_word_frac` and `zero_elem_frac` per side; `p1_word[32]` and
`p1_elem[W]` (W = 32/16/8, two's complement for int8, bit 7 the sign); `hamming` per side, total and per
field (sign / exponent / mantissa, or sign / magnitude for int8); `bus_bits_per_op`; `microops_per_op`,
`gate_decisions_per_op`, `column_slot_cycles_per_op`, `gated_lane_cycles` and `gated_lane_frac`; for fp16
`pair_any_zero`; for int8 `int8_twos_complement` (per-bit P(1), P(negative), mean value, mean popcount) and a
`provisional` block saying which of its figures depend on the reconstructed stream; and, for every random
kind, `replicates` with the expectation and the single-tile band.

Seed 20261031, derived per (type, kind) by sha256 of the name, so any one kind can be regenerated alone and
adding a kind never moves another. Each kind's replicate draws are seeded per (type, kind, replicate) the
same way.

**Replaying a tile in `rtl-sim/fma_toggle`:** fp32 is exact. fp16 gives the right operand words, the right
stream and the right gate, but fp32 arithmetic inside the unit, so quote its bus and gate counts, not its
multiplier-tree counts. **int8 must not be replayed there at all** — the bench is the txfma unit with the `h`
loop and the 32-bit-word gate, which is neither int8's stream nor int8's gate.
