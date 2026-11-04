# Q140(b) blind pool 7

Wed 4 Nov 2026 (week 45). **Q140(b) blind pool 7, written by an independent designer who never saw M9** (Q140(m)'s fit),
Q140(l)'s aifoundry2 terms, their data directories or their scratch, **and corrected before the commit by its fix pass**,
under the same rule (§ Corrections before the commit). It answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** ("a power
model across kinds", the blind test of M9) and **item 7** (real tensors), as Q139's final critic ranked them: **rank 1**
(M9 scored on a seventh pool aimed at the misses every model shares, with a subset aimed at none of them), **rank 4** (two
random anchors per format, for the paired-anchor card scale) and **rank 9** (real tiles from two or more public models,
int8 activations with outliers among them).

**61 operand tile pairs: 22 fp32, 12 fp16, 27 int8. 52 are new kinds and 9 are anchors, three per format: the zeros the
footing needs and two fresh random draws.** 48 of the new kinds are priority 1 and 4 are priority-2 tests. Every count
the brief asks for is met inside priority 1 alone, the whole-line and near-whole-byte class strictly, so a session that
runs only priority 1 still tests every class:

| asked for | in the pool | priority 1 |
|---|---:|---:|
| single high B bits on three or more base words (at least 6) | 8, on 7 base words | 7: four new fp32 base words, pool 6's 1/3 at a new bit (22), two fp16 words |
| exponent-heavy fp32 (at least 6) | 6 | 6 |
| whole-line and near-whole-byte int8 (at least 6) | 7: six, and the 6-bit control | 7: six, and the control |
| int8 with B held (at least 6) | 7 | 6 |
| kinds aimed at none of the four (at least 12) | 12 | 12 |
| real tiles from two or more public models (at least 10) | 12, from 3 models | 10 |
| among them, int8 tiles whose activations carry outliers | 4 | 4 |
| random anchors, two per format | 6 | (run in every pass) |
| zeros anchors, one per format | 3 | (run in every pass) |

Each tile is 2,048 bytes: raw A (1,024 B) then raw B (1,024 B), in the type's layout, ready for `sparsity_host --values
file:`. Tiles are packed with `make_kinds.encode` (or `make_kinds.from_words` for the tiles defined on bit patterns) and
described by `make_kinds.tile_stats` in `blind7.json`. Layout, stream order and gate rule are those of `../README.md`;
nothing here changes them. Every tile carries pool 6's `bus_by_field` unchanged, and pool 6's `c_check` with pool 6's two
committed C corrections applied: fp16's C under the card's plain sum, and the launch-end descriptor read away from powers
of two (`../blind6/CORRECTIONS.md` C1 and C2; § The C check). Two keys are new: `aim` (S, E, L, H, `none` or `anchor`) and
`class_descriptors`, model-free counts of how much of each named class the tile holds (below). `blind7.json` keeps every
key pool 6's harnesses read (`name`, `file`, `type`, `case`, `priority`, `anchor`, `sha256`, `hold_candidate`, all false
here). It adds `subsets` (the aimed tiles by class and L's strict six, the unaimed ones alone and with the five float real
tiles, the real ones, the priority-2 tests, and the anchors: zeros, random, random float, random int8) and
`corrected_before_commit`.

```bash
python3 tools/claims-v3/kinds/blind7/make_blind7.py --check            # the 63 built files and SHA256SUMS against disk (files beside the pool are listed, not checked)
python3 tools/claims-v3/kinds/blind7/make_blind7.py --check --uniq .   # also: no tile, name or held-B kind repeats an earlier tile in the tree
(cd tools/claims-v3/kinds/blind7 && shasum -a 256 -c SHA256SUMS && shasum -a 256 MANIFEST)   # 91 files OK; MANIFEST `92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a`
python3 tools/claims-v3/kinds/blind7/make_blind7.py                    # writes tiles/, blind7.json, MANIFEST, SHA256SUMS (numpy only)
python3 tools/claims-v3/kinds/blind7/fetch_real7.py                    # optional: re-fetches real/ from huggingface.co
sparsity_host --test fma --type int8 --values file:tools/claims-v3/kinds/blind7/tiles/int8/int8.bheld_55.bin
```

**Names and bytes.** No pool-7 tile repeats an earlier one. `--uniq` scanned every 2,048-byte `.bin` file in the lab
tree, 20,959 of them (E78's kinds, `real/`, `real2/`, blind pools 3-6, every experiment's tiles and every run's dumped
copies). It found no tile with the same bytes and no tile with the same name. Since the fix pass it also checks the
held-B class by kind, where a fresh A draw hides a repeat from the whole-tile hash: no tile whose B is one held byte under
a full-range A meets an earlier tile with the same B half under a full-range A. The verified version's `int8.bheld_7f`
did. Its rule was E103's `int8.i_afull_b127` (A uniform, B every byte 0x7F; `../make_e103_pool.py`), measured on
aifoundry1 card 1 and one of M8's 767 training rows (`docs/reports/data/2026-11-03-q139m-model/rows-m8.json`). So the fix
pass replaced it with `int8.bheld_fd` (K1). A byte scan of the tree and of M8's training rows finds 0xFD held nowhere,
and none of this pool's other held bytes (0x55, 0xFF, 0x01, 0x33) under a full-range A: elsewhere they are held only
against a constant A or a single-bit A, at most two A values. The three zero anchors are the one byte-level exception, by
necessity: 2,048 zero bytes are the same tile in every type and every pool. The two random anchors of a format are
different draws. `fp32.b_onebit_b20_third_a1p5` holds pool 6's `fp32.b_onebit_b20_third` B half byte for byte, by
design, under a different A.

**`MANIFEST`** has one line per kind, in pool 6's form: the tile's sha256, its file, name, type, case, priority, `anchor`
or `kind`, and `hold` or `-` (no hold candidates are asked of this pool, so every line ends `-`). **`SHA256SUMS`** covers
the pool's own files and nothing else, 91 in all: the 63 the generator builds (61 tiles, `blind7.json`, `MANIFEST`), this
README, both scripts and `real/`'s 25 files. Files placed beside the pool later (predictions, notes) are not part of it,
and `--check` lists them without failing (pool 6's C3; K4).

## Tiles

`gated`: the share of the 4,096 column-slot-cycles of one accumulate op that are gated. `bits/op`: operand bits the input
bus flips in one op, under `make_kinds`' stream and convention (int8's figure is provisional, as `../README.md` 1.2 says).
`class`: for floats the exponent field's share of those flips; for int8 the share of B's line-boundary flips that sit in
bytes flipping seven or eight bits at once (`nwb`, M8's near-whole-byte rule), and `held` when every B line is the same.
`C flips/op`: C-register bits that flip in one op, from the C emulation (fp16 under the card's plain sum), at a launch's
start (the second op) and near the end of a 0.5 s launch at 600 MHz (the mean over 32 ops from each of eight starting
counts, none a power of two; pool 6's C2): a descriptor, not a measurement. `sha12`: the first 12 hex digits of the whole
file's sha256.

Cases: **0** an anchor; **S** single high B bits on other base words; **E** exponent-heavy fp32; **L** int8 whole-line and
near-whole-byte B flips; **H** int8 with B held; **U** aimed at none of the four; **R** real model tiles.

| tile | case | rule | gated | bits/op | class | C flips/op, start → end | prio | sha12 |
|---|---|---|---|---:|---|---|---|---|
| `fp32.anchor7_zeros` | 0 | every element +0.0 (footing: the zero reference, as fp32.zeros) | 100.0% | 0 | exp 0.00 | 0 → 0 | anchor | `e5a00aa9991a` |
| `fp32.anchor7_randn_a` | 0 | standard normal both sides, a fresh draw (the first random anchor: as fp32.randn) | 0.0% | 83,460 | exp 0.11 | 49,263 → 10,377 | anchor | `d2f651f6a027` |
| `fp32.anchor7_randn_b` | 0 | standard normal both sides, a second fresh draw (the second random anchor) | 0.0% | 83,966 | exp 0.12 | 49,187 → 10,293 | anchor | `9a8b732ca349` |
| `fp16.anchor7_zeros` | 0 | every element +0.0 (footing: as fp16.zeros) | 100.0% | 0 | exp 0.00 | 0 → 0 | anchor | `e5a00aa9991a` |
| `fp16.anchor7_randn_a` | 0 | standard normal both sides, a fresh draw (the first random anchor: as fp16.randn) | 0.0% | 84,320 | exp 0.20 | 50,075 → 10,975 | anchor | `194ac8a5fd59` |
| `fp16.anchor7_randn_b` | 0 | standard normal both sides, a second fresh draw (the second random anchor) | 0.0% | 83,308 | exp 0.20 | 50,043 → 11,174 | anchor | `9653eccefc44` |
| `int8.anchor7_zeros` | 0 | every byte 0x00 (footing: as int8.zeros) | 100.0% | 0 | nwb 0.00, held | 0 → 0 | anchor | `e5a00aa9991a` |
| `int8.anchor7_full_a` | 0 | uniform -128..127 both sides, a fresh draw (the first random anchor: as int8.full, the lab's int8 random anchor) | 0.0% | 69,798 | nwb 0.06 | 35,094 → 32,552 | anchor | `6329c4e38b1a` |
| `int8.anchor7_full_b` | 0 | uniform -128..127 both sides, a second fresh draw (the second random anchor) | 0.0% | 69,134 | nwb 0.04 | 35,500 → 32,650 | anchor | `1db39476eb13` |
| `fp32.b_onebit_b20_one` | S | A every element 1.0; B every word 1.0 (0x3F800000, an empty mantissa) with bit 20 flipped in columns 8-15: each lane alternates 1.0 / 1.125 every cycle (4,096 flips an op); pool 6's b20 on 1/3, moved to the emptiest base word | 0.0% | 4,096 | exp 0.00, bit 20 | 12,288 → 8,195 | 1 | `17c55f8c3c67` |
| `fp32.b_onebit_b20_full` | S | as b_onebit_b20_one on the base word 0x3FFFFFFF (1.99999988, every mantissa bit set): the fullest base word | 0.0% | 4,096 | exp 0.00, bit 20 | 11,776 → 8,192 | 1 | `296441f3c6df` |
| `fp32.b_onebit_b20_pi` | S | as b_onebit_b20_one on pi (0x40490FDB, mantissa 0x490FDB, bit 20 clear): a base word with an irregular mantissa and exponent field 128 | 0.0% | 4,096 | exp 0.00, bit 20 | 41,472 → 8,188 | 1 | `af4296a239e2` |
| `fp32.b_onebit_b20_seventh` | S | as b_onebit_b20_one on 1/7 (0x3E124925, mantissa 0x124925: the period-3 pattern 001, bit 20 set): a periodic base word other than 1/3's alternation | 0.0% | 4,096 | exp 0.00, bit 20 | 47,360 → 8,192 | 1 | `7ccb5d8572eb` |
| `fp32.b_onebit_b22_third` | S | as b_onebit_b20_one on pool 6's base word 1/3 (0x3EAAAAAB) at bit 22, the mantissa's top bit (clear in 1/3: 1/3 / 0.4583): the third position on 1/3, beside pool 6's bits 12 and 20 | 0.0% | 4,096 | exp 0.00, bit 22 | 59,520 → 8,192 | 1 | `1d67b2a7d341` |
| `fp16.b_onebit_b9_one` | S | A every element 1.0 (0x3C00); B every half 1.0 with bit 9 (the fp16 mantissa's top bit) of each half flipped in columns 8-15: each lane alternates 1.0 / 1.5 in both halves every cycle (8,192 flips an op) | 0.0% | 8,192 | exp 0.00, bit 9 | 9,984 → 8,198 | 1 | `42a2043fc737` |
| `fp16.b_onebit_b8_pi` | S | A every element 1.0; B every half pi in fp16 (0x4248, 3.140625) with bit 8 of each half flipped in columns 8-15 (3.140625 / 3.640625): a second fp16 base word and position | 0.0% | 8,192 | exp 0.00, bit 8 | 25,600 → 8,189 | 1 | `4ead4e02db33` |
| `fp32.b_onebit_b20_third_a1p5` | S | pool 6's fp32.b_onebit_b20_third B half byte for byte (1/3 with bit 20 flipped in columns 8-15), with A every element 1.5 (0x3FC00000, two radix-4 digits) instead of 1.0: whether the b20 miss scales with A's digits (the multiplier) or with the products' difference (the accumulators) | 0.0% | 4,096 | exp 0.00, bit 20 | 13,568 → 8,194 | 2 | `19bda61eb9d1` |
| `fp32.exp_b_alt_lsb` | E | A every element 1.25; B columns 0-7 random sign and mantissa, exponent field an even number in 118..136; column l+8 the same word with exponent bit 0 (word bit 23) set: each lane flips exactly one exponent bit a cycle (x / 2x), fresh words on every line | 0.0% | 6,100 | exp 0.75 | 36,992 → 4,225 | 1 | `e807e536a466` |
| `fp32.exp_b_alt_b26` | E | as exp_b_alt_lsb with the exponent field in 112..143 and its bit 3 (word bit 26) clear in columns 0-7 and set in 8-15: one exponent bit a cycle, but the two words 256 times apart | 0.0% | 6,132 | exp 0.75 | 32,672 → 5,784 | 1 | `fae3e9c1af14` |
| `fp32.exp_b_alt_nib` | E | as exp_b_alt_lsb with the exponent field in 112..143 and column l+8's field = column l's XOR 0x0F: four exponent bits (word bits 23-26) a cycle, the two words up to 2^15 apart | 0.0% | 17,866 | exp 0.92 | 23,024 → 2,629 | 1 | `2619f45c4aa1` |
| `fp32.exp_a_gray_walk` | E | A[i][k] = (1 + m_k) * 2^(gray(i) - 15), positive, one random mantissa per column k and the exponent field 0x70 with its low four bits a Gray code down the rows: each step down an A column flips exactly one exponent bit, the value jumping 2x, 4x, 16x or 256x; B every line the same, eight random normal words per lane and columns l and l+8 equal, so B never changes | 0.0% | 3,504 | exp 0.58 | 45,568 → 8,229 | 1 | `39f249e61da8` |
| `fp32.mant2_spreadexp` | E | both sides randn * 2^U{-6..6}, rounded to two mantissa bits (the low 21 mantissa bits zero, round to nearest even): an e5m2-like significand with a spread exponent, in fp32 words | 0.0% | 34,090 | exp 0.72 | 18,639 → 2,966 | 1 | `821b0b7c2ca2` |
| `fp32.exp_only_pos12` | E | both sides +2^U{-12..12}: sign 0 and mantissa 0, so only exponent bits move, every product an exact power of two (between pool 6's narrow 1/4..4 and pool 5's 2^-40..2^40, and positive) | 0.0% | 24,426 | exp 1.00 | 8,219 → 1,155 | 1 | `37f59cdc8246` |
| `int8.b_line_0f_f0` | L | A uniform -128..127; B lines alternate all 0x0F (+15) and all 0xF0 (-16): every boundary flips all 512 B bits, no byte zero, two values pool 5 (0x7F/0x80) and pool 6 (0x55/0xAA, 0x00/0xFF) did not use | 0.0% | 73,344 | nwb 1.00, whole-line | 27,712 → 24,340 | 1 | `e65c065af07a` |
| `int8.b_line_zero_7f` | L | A uniform -128..127; B lines alternate all 0x00 (even k-groups: every slot gated) and all 0x7F (+127): seven of eight bits a byte at every boundary, under the gate (pool 5's 0x00/0x01 flipped one, pool 6's 0x00/0xFF eight) | 50.0% | 72,320 | nwb 1.00, whole-line | 22,128 → 16,925 | 1 | `3ed0a93e121c` |
| `int8.b_line_near7_rand` | L | A uniform -128..127; B one random line pattern r (random bytes), line p = r XOR 0xFE in every byte when p is odd: every boundary flips exactly seven bits (all but bit 0) in every B byte, the values random, no line constant | 0.0% | 71,424 | nwb 1.00 | 33,673 → 32,065 | 1 | `433e096abf9b` |
| `int8.b_line_compl_rand` | L | as b_line_near7_rand with line p = r XOR 0xFF on odd p: all eight bits of every B byte flip at every boundary, the values random (whole bytes, not whole lines) | 0.0% | 74,144 | nwb 1.00 | 35,347 → 32,460 | 1 | `9611430257f0` |
| `int8.b_line_6bit_rand` | L | as b_line_near7_rand with line p = r XOR 0x7E on odd p: six bits (1-6) of every B byte flip at every boundary, one bit under M8's near-whole-byte line (seven or eight): the control just below the threshold | 0.0% | 71,808 | nwb 0.00 | 35,298 → 32,303 | 1 | `3d22931ec503` |
| `int8.b_line_7f_80_aconst` | L | A every byte +3 (A never changes, so no slot gates and no A bit moves); B lines alternate all 0x7F and all 0x80: pool 5's b_line_flipflop_nogate B with a quiet A, so the line boundaries' 512 flipped bits are the operand bus's only activity (C still moves: its register flips 96,000 bits an op at a launch's start) | 0.0% | 8,192 | nwb 1.00, whole-line | 96,000 → 18,229 | 1 | `f55ced450161` |
| `int8.b_line_zero_55` | L | A uniform -128..127; B lines alternate all 0x00 (gated) and all 0x55 (+85, four bits a byte): the gated ladder's missing rung between pool 5's one bit and this pool's seven and pool 6's eight | 50.0% | 70,208 | nwb 0.00, whole-line | 19,008 → 16,321 | 1 | `72db46f3cc83` |
| `int8.bheld_55` | H | A uniform -128..127; B every byte 0x55 (+85, never changing): four bits set, four nonzero radix-4 digits (+1 each) | 0.0% | 65,632 | nwb 0.00, held | 37,600 → 33,521 | 1 | `3178d79b1168` |
| `int8.bheld_fd` | H | as bheld_55 with B every byte 0xFD (-3): seven bits set, two nonzero radix-4 digits (+1 and -1). It takes the cell of the verified pool's bheld_7f (0x7F, +127), which repeated E103's int8.i_afull_b127, a kind M8 trained on; no committed tile holds B at 0xFD | 0.0% | 66,464 | nwb 0.00, held | 25,680 → 22,896 | 1 | `469ef8d6d24c` |
| `int8.bheld_ff` | H | as bheld_55 with B every byte 0xFF (-1): all eight bits set, one nonzero radix-4 digit (-1) | 0.0% | 65,536 | nwb 0.00, held | 19,536 → 20,102 | 1 | `e299dc1612ea` |
| `int8.bheld_01` | H | as bheld_55 with B every byte 0x01 (+1): one bit set at position 0, one radix-4 digit (pool 6 held bits 1, 4 and 7) | 0.0% | 64,896 | nwb 0.00, held | 23,920 → 20,112 | 1 | `3ca9392c2424` |
| `int8.bheld_33` | H | as bheld_55 with B every byte 0x33 (+51): four bits set, four nonzero radix-4 digits of alternating sign (-1, +1, -1, +1) | 0.0% | 66,752 | nwb 0.00, held | 35,168 → 32,364 | 1 | `ddae40987dd1` |
| `int8.bheld_rand` | H | A uniform -128..127; B held but not constant: every line the same 16 words of four random bytes, so each column slot holds its own random word for the whole op | 0.0% | 65,728 | nwb 0.00, held | 35,750 → 32,980 | 1 | `d90103683d75` |
| `int8.bheld_55_asmall` | H | as bheld_55 with A uniform -8..7 (small values, signs changing): the held B against a quieter A | 0.0% | 66,720 | nwb 0.00, held | 28,208 → 24,048 | 2 | `6bda30a3d13b` |
| `fp32.uniform_pm1` | U | uniform (-1, 1) both sides | 0.0% | 80,746 | exp 0.09 | 50,048 → 11,064 | 1 | `de5c5683ce9d` |
| `fp32.laplace_both` | U | Laplace (0, 1) both sides: heavier tails than randn | 0.0% | 88,360 | exp 0.17 | 47,073 → 8,756 | 1 | `73e9b56e8a2d` |
| `fp32.randn_a24k` | U | standard normal both sides; A 2:4 sparse along k (in every row, two random k of each four are +0.0): half of A's words zero, so half the micro-ops gate, in a pattern that changes every row | 50.0% | 81,158 | exp 0.16 | 26,004 → 6,120 | 1 | `a8bfdbfe1956` |
| `fp32.dropout30_both` | U | standard normal both sides with each element +0.0 with probability 0.3 | 46.1% | 87,102 | exp 0.22 | 27,097 → 6,205 | 1 | `1eb7969c858e` |
| `fp16.uniform_pm1` | U | uniform (-1, 1) both sides, rounded to fp16 | 0.0% | 82,488 | exp 0.18 | 50,124 → 11,599 | 1 | `87d9081d81fb` |
| `fp16.laplace_both` | U | Laplace (0, 1) both sides, rounded to fp16 | 0.0% | 91,640 | exp 0.26 | 48,090 → 9,562 | 1 | `094cfe3ded00` |
| `fp16.randn_x8` | U | normal with sigma 8 both sides, rounded to fp16: randn's mantissas three exponent steps up (E78's randn_small went six down) | 0.0% | 92,700 | exp 0.27 | 48,655 → 11,147 | 1 | `199b1f981dcd` |
| `fp16.sorted_k` | U | standard normal; every A row sorted ascending along k and every B column sorted ascending along k (pool 5's sorted_k rule, in fp16) | 0.0% | 75,864 | exp 0.19 | 42,758 → 5,275 | 1 | `5ad9f10050b3` |
| `int8.pos_small` | U | uniform 0..15 both sides: no sign, the low four bits only | 0.0% | 34,846 | nwb 0.00 | 22,518 → 22,589 | 1 | `c18feb62f969` |
| `int8.relu_q_a` | U | A = ReLU(standard normal) quantised per token to 0..127 (half the bytes zero, about 6% of A's words); B uniform -128..127 | 5.1% | 44,464 | nwb 0.07 | 30,514 → 28,113 | 1 | `ad6026a10af7` |
| `int8.a_full_b_pos` | U | A uniform -128..127; B uniform 0..127 (no sign in B) | 0.0% | 68,072 | nwb 0.01 | 34,753 → 32,628 | 1 | `92e3de99979d` |
| `int8.sparse_rows_a` | U | uniform -128..127; A rows 3, 7, 11 and 15 all zero: a quarter of the micro-ops gate, in a fixed rhythm down every A column | 25.0% | 70,124 | nwb 0.06 | 26,774 → 24,449 | 1 | `83a6e9c31b27` |
| `int8.real_s360_l3_w8a8_q_outlier` | R | SmolLM-360M-Instruct W8A8 layer 3, q_proj: A = input_layernorm output (tokens 16-31, the 64 dims holding the residual's outlier dim 463, the argmax of every token) quantised per token (max abs over all 960 dims / 127); B = the checkpoint's int8 q_proj rows 0-15 x those dims, transposed | 0.0% | 66,130 | nwb 0.09 | 23,114 → 21,127 | 1 | `9e0c742569cc` |
| `int8.real_qwen_l3_w8a8_down_massive` | R | Qwen2.5-0.5B W8A8 layer 3, down_proj: A = SiLU(gate) * up (tokens 0-15, the 64 hidden units holding token 0's massive unit 2247, 8,073 times the row's median) quantised per token (max abs over all 4864 / 127: in the cut, token 0's row is one byte of -127 and zeros; over its whole row, a -105 at unit 3016 and six codes of +-1 besides); B = the checkpoint's int8 down_proj rows 0-15 x those units, transposed | 5.9% | 65,862 | nwb 0.15 | 21,940 → 19,141 | 1 | `f1217c0eb2fa` |
| `int8.real_smol_l2_w8a8_up_outlier` | R | SmolLM-135M-Instruct W8A8 layer 2, up_proj: A = post_attention_layernorm output (tokens 16-31, dims 256-319, holding the outlier dim 285) quantised per token (over all 576); B = the checkpoint's int8 up_proj rows 0-15 x dims 256-319, transposed | 0.0% | 67,772 | nwb 0.09 | 26,997 → 24,146 | 1 | `1ddb4d9301e8` |
| `int8.real_qwen_l3_w8a8_k_sink` | R | Qwen2.5-0.5B W8A8 layer 3, k_proj: A = input_layernorm output (tokens 0-15, token 0 the attention sink at 110 times its median; dims 512-575, holding the outlier dim 570) quantised per token (over all 896); B = the checkpoint's int8 k_proj rows 0-15 x dims 512-575, transposed | 0.0% | 69,092 | nwb 0.23 | 24,860 → 23,281 | 1 | `e1380e9cace5` |
| `int8.real_s360_l2_w8a8_o` | R | SmolLM-360M-Instruct W8A8 layer 2, o_proj: A = the attention output (tokens 16-31, dims 0-63, head 0's) quantised per token (over all 960); B = the checkpoint's int8 o_proj rows 0-15 x dims 0-63, transposed | 0.0% | 60,676 | nwb 0.10 | 28,653 → 25,370 | 1 | `8d7186c11693` |
| `int8.real_smol_l3_w8a8_down` | R | SmolLM-135M-Instruct W8A8 layer 3, down_proj: A = SiLU(gate) * up (tokens 16-31, hidden units 0-63) quantised per token (over all 1536); B = the checkpoint's int8 down_proj rows 0-15 x hidden 0-63, transposed | 0.0% | 69,132 | nwb 0.10 | 26,923 → 24,017 | 2 | `47bb503b9efd` |
| `fp16.real_qwen_l3_softmax_v_h1` | R | Qwen2.5-0.5B layer 3, head 1 (the head that puts least weight on token 0, 0.13 of it, in a layer whose other heads sink 0.24-0.99 there): A = causal softmax, query tokens 16-31 x key tokens 0-31 (exact zeros above the diagonal; a probability that rounds to an fp16 subnormal is written as +0.0); B = values of KV head 0, keys 0-31, head dims 0-15 | 21.9% | 77,480 | exp 0.21 | 34,455 → 5,167 | 1 | `8a7a682facc1` |
| `fp16.real_s360_l3_qk` | R | SmolLM-360M-Instruct W8A8 layer 3, head 1: A = rotary queries (tokens 16-31, head dims 0-31), B = rotary keys of KV head 0, tokens 0-15, transposed: the attention scores' matmul; fp32 values rounded to fp16 | 0.0% | 83,928 | exp 0.21 | 48,121 → 9,326 | 1 | `86fa979e9792` |
| `fp16.real_s360_l3_w8a16_gate` | R | SmolLM-360M-Instruct layer 3: A = post_attention_layernorm output (tokens 16-31, dims 64-95, holding its outlier dim 87) in fp16; B = gate_proj weights dequantised (int8 x channel scale) rows 0-15 x dims 64-95, transposed, in fp16 (a W8A16 matmul) | 0.0% | 84,918 | exp 0.21 | 46,979 → 9,382 | 1 | `14ace11e9d5b` |
| `fp32.real_qwen_l3_softmax_v_sink` | R | Qwen2.5-0.5B layer 3, head 5: A = softmax, query tokens 16-31 x key tokens 0-15 (key 0 the sink, 0.99 of the weight; no masked zeros, the smallest weight 2.3e-14); B = values of KV head 0, keys 0-15, head dims 16-31 | 0.0% | 83,824 | exp 0.12 | 12,081 → 1,019 | 1 | `eb074b9c66c3` |
| `fp32.real_smol_l3_w8a16_q_outlier` | R | SmolLM-135M-Instruct layer 3: A = input_layernorm output (tokens 16-31, dims 272-287, holding the outlier dim 285) in fp32; B = q_proj weights dequantised (int8 x its channel's bf16 scale, exact in fp32) rows 0-15 x dims 272-287, transposed | 0.8% | 56,866 | exp 0.16 | 43,085 → 4,465 | 1 | `17941c8ac17f` |
| `fp32.real_s360_l1_qk` | R | SmolLM-360M-Instruct layer 1, head 2: A = rotary queries (tokens 16-31, head dims 0-15), B = rotary keys of KV head 0, tokens 0-15, head dims 0-15, transposed | 0.0% | 82,866 | exp 0.12 | 48,883 → 9,526 | 2 | `63844d7459ba` |

## What each case aims at, and why

Q139's final critic (rank 1) named the misses every model shares on pool 6's 30 priority-1 kinds. Without the six tiles
that carry them, every model reads the other 24 at 0.17-0.19 W rms on both 600 MHz cards (its post hoc check, confirmed
by Q140(c)'s committed `check2-pool6-named-misses`), so the named classes are where M9's new terms can gain. Each class
here takes pool 6's miss and varies it along the property a term would price, so a term fitted to pool 6's one tile meets
new cases. The measured misses, from E153 (aifoundry3) and E157 (aifoundry1 card 1), `scored.json` › power rows, error =
measured − model:

- **S: single high B bits on other base words (8; the base-word term).** Pool 6's `fp32.b_onebit_b20_third` (B on 1/3 with
  bit 20 flipping every cycle on every lane) read 12.94 W on aifoundry3 and 12.13 W on card 1: every model over-predicts it
  by 0.70-0.81 W and 1.09-1.21 W, and bits 12 and 20 on 1/3 read 2.92 W apart where every model said 3.85-3.91 W (E153
  README § 3). This pool keeps pool 6's construction (A every element 1.0; B one base word, bit `j` flipped in columns 8-15,
  every line the same: 4,096 flips an op and nothing else moving) and moves it:
  - **bit 20 onto four new base words** spanning what a mantissa can hold: 1.0 (`0x3F800000`, an empty mantissa),
    `0x3FFFFFFF` (every mantissa bit set), pi (`0x40490FDB`, an irregular mantissa, exponent field 128) and 1/7
    (`0x3E124925`, the period-3 pattern 001, against 1/3's alternation);
  - **bit 22 on 1/3**, the mantissa's top bit, a third position on pool 6's word beside its bits 12 and 20;
  - **fp16 bit 9 on 1.0 and bit 8 on pi** (`0x3C00`, `0x4248`), each in both halves of the word: pool 6's
    `fp16.b_onebit_b6_third` read 0.48 W under M8 on aifoundry3;
  - and, priority 2, **pool 6's own b20-on-1/3 B half under A = 1.5** (two radix-4 digits where 1.0 has one): if the miss
    is the multiplier's it should scale with A's digits, if it is the accumulators' with the products' difference.

  The emulated C register tells these words apart only at a launch's start. On the second op its flips read 9,984 and
  25,600 an op on fp16's 1.0 and pi, 11,776-13,568 on fp32's `0x3FFFFFFF` and 1.0 (and 1/3 under A = 1.5), and
  41,472-59,520 on pi, 1/7 and 1/3 at bit 22. Near a launch's end every S tile reads 8,188-8,198 an op (K3). So a
  C-register term that reads C's end state cannot tell these base words apart; one that reads the start can.
- **E: exponent-heavy fp32 (6; the exponent-field term).** On pool 6 the card paid more than M8 on 7 of its 10
  exponent-heavy kinds, by +0.17 to +0.18 W on average for each model (E153 README § 3; +0.17 to +0.20 W in the critic's
  words), while E147 found the models too high on single exponent flips. These six put 58-100% of the operand flips in
  the exponent field, and separate how many exponent bits flip from how far the values jump:
  - **one exponent bit a cycle on B's lane alternation**, at the field's bit 0 (`exp_b_alt_lsb`: the two words a factor 2
    apart) and at its bit 3 (`exp_b_alt_b26`: one bit, a factor 256), each with random signs and mantissas held across the
    alternation and fresh words on every line;
  - **four exponent bits a cycle** (`exp_b_alt_nib`: the field's low nibble inverted, the words up to 2^15 apart);
  - **one exponent bit a step down A** (`exp_a_gray_walk`: the field's low four bits a Gray code down the rows, so each
    step flips one bit while the value jumps 2x to 256x; B never changes);
  - **a two-bit mantissa under a spread exponent** (`mant2_spreadexp`, randn × 2^U{-6..6}, an e5m2-like significand in
    fp32 words);
  - **exponent alone, positive** (`exp_only_pos12`, 2^U{-12..12} both sides: between pool 6's 1/4..4 and pool 5's
    2^-40..2^40, with no sign flips).
- **L: int8 whole-line and near-whole-byte B flips (7; M8's near-whole-byte discount).** M8 prices every bit flipped in a
  B byte that flips seven or eight bits at a line boundary at −56.8 fJ (Q139(m) README § 2). On pool 6 the card drew more
  than M8 on all three tiles where it acts most: +0.36 W (`b_line_zero_ff`), +0.62 W (`a_zeros_b_lineflip`) and +1.31 W
  (`b_line_55_aa`) on aifoundry3 (E153 README § 3). These seven separate the threshold, the gate, the values and A's part.
  Six are whole-line or near-whole-byte by M8's line (`subsets.aimed_L_strict`); `b_line_6bit_rand` is the control just
  under it:
  - **the threshold, on random bytes**: every B byte flips exactly 6 (`b_line_6bit_rand`, one under the rule's line), 7
    (`b_line_near7_rand`) or 8 bits (`b_line_compl_rand`) at every boundary, from one random line pattern XORed on odd
    lines, so the values are random and no line is constant;
  - **whole-line flips on new values**: `b_line_0f_f0` (`0x0F`/`0xF0`, all eight bits, no zero byte);
  - **under the gate**: `b_line_zero_7f` (`0x00`/`0x7F`, seven bits) and `b_line_zero_55` (four bits; priority 1 since K5),
    rungs between pool 5's `0x00`/`0x01` (one bit) and pool 6's `0x00`/`0xFF` (eight);
  - **with A quiet**: `b_line_7f_80_aconst` (A every byte +3, so no A bit moves and no slot gates; B pool 5's
    `0x7F`/`0x80` lines): the boundaries' 512 flipped bits are the operand bus's only activity. C still moves: its
    register flips 96,000 bits an op at a launch's start and 18,229 near the end.
- **H: int8 with B held (7; the held-B term).** Pool 6's three held single bits read 5.91 W (`0x02`), 5.31 W (`0x10`) and
  5.27 W (`0x80`) on aifoundry3 against the random anchor's 7.14 W, and every model over-predicted all three, by 0.24-0.54 W
  for M8 (E153 README § 3). B is Booth-recoded in int8 (a registered verdict, the critic's rank 16), and `0x02` holds two
  nonzero radix-4 digits where `0x10` and `0x80` hold one. So these six vary the digits and the set bits apart, A uniform:
  `0x55` (four bits, four digits), `0xFD` (−3: seven bits, two digits, +1 and −1), `0xFF` (eight bits, one digit), `0x01`
  (one bit, one digit), `0x33` (four bits, four digits of alternating sign), and `bheld_rand` (each column slot its own
  random held word). Priority 2: `0x55` held under a small A (−8..7). `0xFD` takes the cell of the verified version's
  `0x7F` (+127: seven bits, two digits, +2 and −1), which was a kind M8 trained on (K1). It keeps the cell's set bits and
  digit count, and moves the digits to the two low groups and the product from 127·A to −3·A. The generator checks each
  held byte's set bits and digits on the bytes, and that none is a byte a committed set held under a full-range A (0x00,
  0x5A, 0x7F, 0x02, 0x10, 0x80).
- **U: aimed at none of the four (12; the unaimed subset).** M8 showed that a term can make a model worse where it was
  not aimed. These twelve are ordinary distributions, sparsity and order, four per format, and the generator asserts that
  each holds none of the four classes: floats with an exponent share under 0.35 (they read 0.09-0.27) and no single-bit
  design; int8 with B neither held nor whole-line, and at most 10% of B's or A's flipped bits in near-whole-byte bytes
  (they read 0.00-0.09; uniform random bytes read about 0.06). fp32: uniform (−1, 1), Laplace, a 2:4-sparse A, dropout
  30%; fp16: uniform (−1, 1), Laplace, sigma 8, both sides sorted along k; int8: 0..15, a per-token-quantised ReLU A,
  a positive B, every fourth A row zero.
- **R: real tiles (12; rank 9).** Below.
- **0: anchors (9).** Zeros, once per format, for the footing (the harness's zero reference), and **two fresh random draws
  per format** for rank 4's paired-anchor card scale: fp32 and fp16 standard normal, int8 uniform −128..127, the lab's
  random anchors since E78. Q140(c)'s committed check (`docs/reports/data/2026-11-04-q140c-critic-checks/`
  `check3-anchor-card-scale.txt`, post hoc) reads card 1's float scale from E78's and pool 6's four float random anchors
  as their median, 0.9618, −0.15% from pool 6's median ratio (0.9632), and int8's from its two at −1.04% (0.9580 against
  0.9681; ± 1.50% from their passes). Two draws per format in one pool let a session pair test rank 4's rule on anchors it
  ran itself. The rule is per format: the float scale from the median of the four float random anchors' ratios
  (`subsets.anchors.random_float`), int8's from the median of its two (`random_int8`). The anchors are `anchor: true`,
  priority 2, and run in every pass.

## Inside the stops pool 6 used

The pool's tiles are chosen from descriptors and committed measurements, never from a model's prediction. On aifoundry3
the stops are E141's, which E153 kept: board ≥ 65 W or `minshire[0]` ≥ 70 °C. The hottest tile ever measured there is
pool 5's `fp32.wideexp48_dense`: 25.82 W of switching (E141 `scored.json` › `primary.power_rows`), with 97,624 operand
bits an op on the bus (`../blind5/blind5.json` › its `stats.bus_bits_per_op`). E141's passes peaked at 55.33 W board (E141
README, the "stops" row). **Every pool-7 tile flips fewer operand bits an op than that tile** (`stats.bus_bits_per_op`).
The most are fp16's `randn_x8` and `laplace_both` (92,700 and 91,640), and fp16 draws less per bit than fp32: on
aifoundry3 pool 6's random anchors read 22.0 W at 85.0 k bits for fp16 against 24.9 W at 85.6 k for fp32 (E153
`scored.json`; `../blind6/blind6.json`). Then fp32's `laplace_both` (88,360) and `dropout30_both` (87,102, with 46% of its
lane-cycles gated). Every other tile flips at most 84,918 (`fp16.real_s360_l3_w8a16_gate`), inside the float random
anchors' own range across pools 6 and 7 (83,308-85,608), or is a bounded design (S, E, L and H flip 3,504-74,144). On
aifoundry2 the limit is section 22's: Q140(x) marks any tile whose predicted peak exceeds 82 W, to be left out there
(pool 6 left two dense fp32 tiles out; this pool's dense fp32 tiles, the random anchors among them, may be marked the
same way).

## The C check

A `--values file:` run verifies no arithmetic (`../README.md` 1.5), so the pool checks each tile's C before any card sees
it, three ways.

1. **Pool 6's `c_check`, with pool 6's two committed corrections applied** (`../blind6/CORRECTIONS.md` C1 and C2; K2,
   K3). No NaN or Inf encoding. **No subnormal operand in any tile** (fp16 values that round to a subnormal are written
   as +0.0: two in all, both in `fp16.real_qwen_l3_softmax_v_h1`). C is emulated in PRM 9.4's order, with **fp16's
   two-term update as the card adds it: the plain sum a1·b1 + a2·b2 for every k pair**. E36's LAT-S1 read "math" at 50%
   and 100% on three cards; PRM 9.4's pseudo-code, taken literally, drops the update unless all four halves are nonzero,
   and the card does not. C is shown finite over 2^21 accumulate ops (the first 64 run exactly, then a bound with an 8x
   rounding margin). **No product is subnormal**, so flushing changes no tile's C. C is described at a launch's start and
   near its end (the mean over 32 ops from each of eight starting counts, none a power of two), and `c_op1_sha256` is
   recorded. **All 61 pass.**

   Two fp16 real tiles hold words with one zero half, where the two rules differ (`c_check` ›
   `prm_literal_rule_would_drop`). `fp16.real_qwen_l3_softmax_v_h1` has 9 such A words and 1 B word: the literal rule
   would drop 1,056 updates an op, 160 of them with a nonzero sum. `fp16.real_s360_l3_w8a16_gate` has 6 B words: it would
   drop 96, all with a nonzero sum. Under the card's rule their first op's C is within 7.0e-08 and 8.6e-08 of the exactly
   rounded sum of every product. The literal rule would move it by 24.5% and 12.0% of max |C| (`c_op1_moves_rel_to_max_c`). A launch of either with C
   checked by `ccheck.py` tests the card's rule on half-zero words on silicon, as pool 6's two such tiles did: E153 and
   E157 read every pool-6 launch's C bit-exact against `ccheck.py`.
2. **Q139(k)'s domain screen** (`tools/claims-v3/ccheck/ccheck.py domain`, the pre-claim step E153 ran, at its n =
   750,000): **all 61 tiles are inside** the operand and result classes silicon has read, at every op up to n (no NaN, Inf
   or denormal operand; no overflow; no fp32 flush). **41 of them are first reads** of their value range against E104's 44
   tiles: int8 operands past the ±3 the host read in September, float tiles with more distinct magnitudes. Pool 6's were
   too, and E153, E157 and E160 have since read such tiles bit-exact.
3. **The first op's C against Q139(k)'s reference** (`ccheck.py ref <type> <tile> 1`, the RTL's arithmetic in
   `accum.c`): `c_op1_sha256` equals it on **52 of 61 tiles**, every fp32 and int8 tile among them (`int8.bheld_fd` too).
   The nine that differ are fp16 tiles with many distinct magnitudes, by 10 to 768 ulp in 162 to 256 of the 256 C words:
   the RTL truncates each aligned product in its fixed-point window, where this emulation rounds the exact sum once. The
   two half-zero tiles are among the nine, at 64 ulp at most; under the literal rule they would be 24.5% and 12.0% of
   max |C| away. Pool 6's tiles match on 39 of 50: nine fp16 tiles
   apart for the RTL's fixed-point window, and `fp16.a_zeros_b_complement` and `fp32.a_zeros_b_complement` for the signs
   of zero words (`../blind6/CORRECTIONS.md` C1). The card lanes check C against `accum.c`, not against this hash.

**Reproducible.** `--check` passes with numpy 1.26.4 (Python 3.9.6, the lab collectors'), 1.24.2 (3.10.10), 2.5.3
(3.12.12) and 2.5.4 (3.15.2): every tile, `blind7.json`, `MANIFEST` and `SHA256SUMS` byte-identical.

## Real tiles: three public W8A8 checkpoints, layers 1-3

`real/` holds 24 float32 cuts, written by `fetch_real7.py`, which ran **layers 0-3 of three public W8A8 checkpoints** on a
public-domain text. Their linear layers are W8A8 matmuls by construction (compressed-tensors `int-quantized`: int8 weights,
one scale per output channel; activations quantised to int8 per token at run time), so the int8 tiles hold **the
checkpoints' own int8 weight rows** against activations quantised the way the scheme says. Pool 6 cut layer 0 of the first
two; this pool goes past layer 0, where the outliers are, and adds a third model.

| model | repository | revision (commit) | licence | layers run | fetched |
|---|---|---|---|---|---|
| Qwen2.5-0.5B, W8A8 | `RedHatAI/Qwen2.5-0.5B-quantized.w8a8` | `0d1951533baeec89dd257df86d4d10c3bd5429f5` | apache-2.0 | 0-3 | 59,816,448 bytes, 106 requests |
| SmolLM-135M-Instruct, W8A8 | `RedHatAI/SmolLM-135M-Instruct-quantized.w8a8` | `203f247e5fdd358199df1cecd839a5b8fe5c9473` | apache-2.0 | 0-3 | 14,241,024 bytes, 94 requests |
| SmolLM-360M-Instruct, W8A8 | `RedHatAI/SmolLM-360M-Instruct-quantized.w8a8` | `4477e7ff83e89ab2310ebfb589af52b356dec848` | apache-2.0 | 0-3 | 39,463,680 bytes, 94 requests |

The licence is each card's `license` field (all three Apache-2.0, as their base models). Only the safetensors header, the
tensors of layers 0-3 and the embedding rows of the text's tokens were fetched, by HTTP range requests at pinned commits.
`real/provenance.json` gives each fetched range's sha256, each cut's slice, shape, range and zero count, the per-token
scales, and the rule that picked each outlier. The int8 sums are exact, but the forward pass's float32 parts (RMSNorm,
rotary, softmax, P·V) can round differently under another numpy or BLAS, so a re-run of `fetch_real7.py` may not
reproduce the cuts bit for bit: `make_blind7.py` builds the tiles from the committed cuts, never from a re-fetch (the
cuts here came from numpy 2.5.4; the pool's verifier re-ran `fetch_real7.py` under it and reproduced all 24 cuts and
`provenance.json` bit for bit).

**Text.** The opening of Lewis Carroll, *Alice's Adventures in Wonderland* (1865), public domain, 32 tokens, from "Alice"
to "into". **Tokenised by each model's own byte-level BPE** (its `tokenizer.json`: the pre-tokenizer's split, GPT-2's
byte-to-unicode map, the merges applied by rank; exact on this ASCII text), where pool 6 used greedy longest match. No
special token is added.

**Forward pass.** Layers 0-3 in float32: RMSNorm; W8A8 q, k and v (int8 × int8 summed exactly, times the token's and the
channel's scales, plus Qwen's biases); rotary over the 64-dim head; causal softmax attention with grouped KV heads; the
W8A8 o_proj and the residual; RMSNorm; W8A8 gate and up; SiLU(gate) × up; the W8A8 down_proj and the residual.

**Where the outliers are** (an `--explore 4` pass printed every layer's statistics before any cut was chosen; each cut is
then picked by a rule on the data, written in `fetch_real7.py`): **Qwen2.5-0.5B** grows a massive activation at layer 2-3:
token 0's down_proj input reaches 8,073 times its row's median at layer 3 (unit 2247), and layer 3's heads put 0.13-0.99
of their weight on token 0 (an attention sink; head 5 the most). Quantised per token, that row is almost all zeros. In the
tile's 64-unit cut it is a single −127 and 63 zeros. Over its whole 4,864-unit row it is 4,856 zeros, six codes of ±1,
the −127 and a −105 at unit 3016 (`provenance.json` › `scales` gives the row's share within ±1, 0.9996; the codes are
from `fetch_real7.forward`, re-run by the fix pass). **SmolLM-135M** carries one residual outlier dim, 285, the largest
value of every token from layer 0. **SmolLM-360M** carries dim 463 the same way, up to 579 times a token's median at
layer 3's attention input.

| tile | p | model, layer | A | B | outliers in A |
|---|---|---|---|---|---|
| `int8.real_s360_l3_w8a8_q_outlier` | 1 | SmolLM-360M, 3, q_proj | attention input, tokens 16-31, dims 448-511 (outlier dim 463) | int8 q_proj rows 0-15 | rows' max/median 36-90; 33% of A's bytes within ±1, 16 at ±127 |
| `int8.real_qwen_l3_w8a8_down_massive` | 1 | Qwen2.5-0.5B, 3, down_proj | SiLU(gate) × up, tokens 0-15, units 2240-2303 (token 0's massive unit 2247) | int8 down_proj rows 0-15 | rows' max/median 32-8,073; 44% of A's bytes within ±1, 2 at ±127 |
| `int8.real_smol_l2_w8a8_up_outlier` | 1 | SmolLM-135M, 2, up_proj | MLP input, tokens 16-31, dims 256-319 (outlier dim 285) | int8 up_proj rows 0-15 | rows' max/median 12-33; 13% of A's bytes within ±1, 16 at ±127 |
| `int8.real_qwen_l3_w8a8_k_sink` | 1 | Qwen2.5-0.5B, 3, k_proj | attention input, tokens 0-15 (token 0 the sink), dims 512-575 (outlier dim 570) | int8 k_proj rows 0-15 | rows' max/median 8-110; 8% of A's bytes within ±1, 14 at ±127 |
| `int8.real_s360_l2_w8a8_o` | 1 | SmolLM-360M, 2, o_proj | attention output, tokens 16-31, dims 0-63 | int8 o_proj rows 0-15 | rows' max/median 9-44; 8% of A's bytes within ±1, 0 at ±127 |
| `int8.real_smol_l3_w8a8_down` | 2 | SmolLM-135M, 3, down_proj | SiLU(gate) × up, tokens 16-31, units 0-63 | int8 down_proj rows 0-15 | rows' max/median 13-73; 24% of A's bytes within ±1, 0 at ±127 |
| `fp16.real_qwen_l3_softmax_v_h1` | 1 | Qwen2.5-0.5B, 3, P·V head 1 | causal softmax, queries 16-31 × keys 0-31 (head 1, the least sink: 0.13 on token 0) | values, keys 0-31, dims 0-15 | - |
| `fp16.real_s360_l3_qk` | 1 | SmolLM-360M, 3, Q·Kᵀ head 1 | rotary queries, tokens 16-31, dims 0-31 | rotary keys, tokens 0-15, transposed | - |
| `fp16.real_s360_l3_w8a16_gate` | 1 | SmolLM-360M, 3, gate_proj (W8A16) | MLP input in fp16, tokens 16-31, dims 64-95 (outlier dim 87) | gate_proj dequantised, rows 0-15 | the outlier dim inside the cut |
| `fp32.real_qwen_l3_softmax_v_sink` | 1 | Qwen2.5-0.5B, 3, P·V head 5 | softmax, queries 16-31 × keys 0-15 (head 5, the sink: 0.99 on token 0) | values, keys 0-15, dims 16-31 | - |
| `fp32.real_smol_l3_w8a16_q_outlier` | 1 | SmolLM-135M, 3, q_proj (W8A16) | attention input in fp32, tokens 16-31, dims 272-287 (outlier dim 285) | q_proj dequantised, rows 0-15 | the outlier dim inside the cut |
| `fp32.real_s360_l1_qk` | 2 | SmolLM-360M, 1, Q·Kᵀ head 2 | rotary queries, tokens 16-31, dims 0-15 | rotary keys, tokens 0-15, transposed | - |

**Rounding and quantisation.** fp32 tiles: activations as computed, weights dequantised (int8 × a bf16 scale, exact in
fp32). fp16 tiles: values rounded to fp16, nearest even; a value that rounds to an fp16 subnormal is written as +0.0 (two
values, both in the fp16 attention tile), so C does not depend on whether the unit flushes subnormals. The sink head's
probabilities stay in the fp32 tile, where they are normal numbers down to 2.3e-14; in fp16 a third of them would be
subnormal, so the fp16 attention tile takes the layer's least-sink head (head 1). int8 tiles: activations per token,
scale = the token's max abs over its whole row (896, 960 or 576 dims, or 4,864 or 1,536 hidden units) / 127,
`q = clip(round_half_even(x / scale), -127, 127)` (the maxima are in `provenance.json` › `scales`); weights are the
checkpoints' int8 values, unchanged. The int8 real tiles carry near-whole-byte flips: by the pool's own descriptor, A's
share runs 0.16-0.53 on all five priority-1 int8 real tiles, and B's is 0.105, 0.146 and 0.227 on three of them
(`o`, `down_massive`, `k_sink`), against the cap of 0.10 the generator asserts for U's int8 tiles.

## What the pool does to predicting power and heat

It measures nothing itself. **It is the out-of-sample test set** for M9 (Q140(m), rank 1) against M6, M7 and M8 on the two
600 MHz cards (E163 aifoundry3 card 0, E164 aifoundry1 card 1) and, in governed bursts, aifoundry2 (E165, with Q140(l)'s
part), and the anchor set for rank 4's paired-anchor card scale. Q140(x) copies it unchanged after M9's commits and
commits every model's predictions before any claim.

**Before** (pool 6, registered primaries, Q139(u)'s footing): a new kind's power was read blind to **0.286 / 0.252 / 0.243 W
rms** by M8 / M7 / M6 on aifoundry3 and **0.323 / 0.314 / 0.283 W** on card 1 (30 priority-1 kinds; M8 bootstrap 95%
[0.20, 0.37] and [0.20, 0.45] W). The named misses: a high B bit on 1/3, −0.81 / −1.09 W in every model; exponent-heavy
fp32, +0.17 to +0.20 W; a held one-bit B, −0.24 to −0.54 W; M8's near-whole-byte discount, +0.36 to +1.36 W. Without the
six tiles that carry them every model reads 0.17-0.19 W (the critic's post hoc check). Real tiles: 0.155 / 0.146 W rms, 12 of
12 inside (R1, R2). Card 1's scale from paired random anchors: −0.15% for floats (the median of four) and −1.04% ± 1.50%
for int8 (Q140(c), committed, post hoc). Heat over a 4.5 s run: 0.10-0.13 °C rms on aifoundry3, a skill on the floats.

**After:** these 52 kinds' blind error per class and per model, on the same tiles and footing. The subsets let each of
rank 1's rules be scored on what it asks:

| what | tiles (priority 1) | the term or rule it tests |
|---|---|---|
| S | 7 | a base-word term for single bits (bench counts at three or more base words) |
| E | 6 | an exponent-field term for fp32 |
| L | 7: six strict and the 6-bit control | bounding or dropping M8's near-whole-byte discount |
| H | 6 | a held-B int8 term |
| unaimed | 12 (17 with the five float real tiles) | "M9 no worse than M6 on the unaimed subset" |
| real | 10 | rank 9's real-tile sub-rule (rms within the pool's own, no tile outside its band) |
| all priority 1 | 48 | M9 − M6 resolved below zero by a paired bootstrap on both cards; bias inside B1/B2; coverage |
| random anchors | 4 float, 2 int8 | rank 4: the card's scale as the median of its anchors' ratios, per format, within 1% floats / 2% int8 |

Heat rides on power through the die's rise per board W, so every tile tests heat over a run too. Dropping the four
priority-2 tests first, to save card time, leaves every class at six or more.

**For Q140(x), not registered here.**
- The critic's coverage rule was written for 30 priority-1 kinds ("at least 26 of 30", 86.7%). This pool has 48, so the
  same share is 42 of 48.
- The unaimed subset as the brief defines it is the 12 U tiles. The five float real tiles of priority 1 hold none of the
  four either (exponent shares 0.12-0.21, under U's 0.35), so U and those five (17, `subsets.unaimed_with_float_real`)
  give the no-harm rule more power if Q140(x) wants it. The int8 real tiles do not qualify: they carry near-whole-byte
  flips (§ Real tiles).
- Rank 4's rule is per format: a float median over the four float random anchors, an int8 median over the two int8 ones.
  E78's anchors may join.
- The pool's check, once predictions sit beside it: `shasum -a 256 -c SHA256SUMS` (91 OK), the MANIFEST hash above, and
  `make_blind7.py --check` (0 problems; it lists the files beside the pool).
- M8's `predict_blind6.py` builds its C descriptors itself from the tile bytes, through `make_blind5`'s code
  (`fit_m8.py` › `c_feats`: pool 5's literal fp16 rule and power-of-two end); it never reads `c_check`. A C-register term in
  any model should be read the same way, and Q140(x) can confirm whether `predict_blind7.py` reads this file's `c_check`.

## Corrections before the commit

*Wed 4 Nov 2026 (week 45), PST, before Q140(x) copied the pool. The pool's independent verification (verdict: holds with
fixes) found two major faults and six minor ones. Nothing had been committed, so the fix pass corrected them in place,
and this section records how. The verified version's hashes: MANIFEST `00ceddd3…`, `blind7.json` `d982f61b…`,
SHA256SUMS `1c3f5477…` (in full in `blind7.json` › `corrected_before_commit`). 60 of the 61 tiles are byte-identical to
that version; one was replaced. Now: MANIFEST `92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a`, `blind7.json` `24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552`.*

| | the verified version said | corrected |
|---|---|---|
| **K1** (major) | `int8.bheld_7f` (A uniform, B every byte 0x7F) a new kind: 52 new kinds, 47 at priority 1 | Its rule is E103's `int8.i_afull_b127` (`../make_e103_pool.py`), measured on aifoundry1 card 1 and one of M8's training rows; a fresh A draw hid it from the whole-tile hash. **Replaced by `int8.bheld_fd`**: B every byte 0xFD (−3), the same cell (seven bits set, two radix-4 digits), held by no committed tile. So 52 new kinds still, and six new held-B kinds at priority 1. `--uniq` now checks the held-B class by kind |
| **K2** (major) | fp16's C under PRM 9.4's literal rule, the check copied from `make_blind6.py` with pool 6's C1 fault in it | the card's plain sum. Two tiles change. `fp16.real_qwen_l3_softmax_v_h1`: C flips an op at the start 32,852 → **34,455**. `fp16.real_s360_l3_w8a16_gate`: 45,986 → **46,979**. Both tiles' `c_op1_sha256` changes. Every tile still passes. The tiles and MANIFEST do not change for this |
| **K3** | the launch-end C descriptor one op from exactly 2^19 or 2^20 (pool 6's C2) | the mean over 32 ops from each of eight counts that are not powers of two. Of the 57 tiles both versions hold whose C moves at the end, 2 move by more than 25% (the median ratio 0.97): `fp32.b_onebit_b20_full` 12,288 → **8,192** and `int8.b_line_7f_80_aconst` 68,096 → **18,229**; twelve int8 tiles move by 10-24%. Every S tile now reads 8,188-8,198 at the end, so the S paragraph's claim that C's end state tells the base words apart is withdrawn |
| **K4** | `--check` sums every file in the directory (pool 6's C3), so any file beside the pool fails it | it checks the files it builds and SHA256SUMS over the pool's own files; files beside the pool are listed, not checked. SHA256SUMS covers the pool's own 91 files only |
| **K5** | L at priority 1: five whole-line or near-whole-byte tiles and the 6-bit control; `int8.b_line_zero_55` at priority 2 | `b_line_zero_55` at priority 1: six strict L tiles and the control. 48 priority-1 kinds and 4 priority-2 tests, so dropping the priority-2 tests keeps every class at six or more |
| **K6** | wording | Blog point 3's "its int8 row is a single −127 and zeros" holds for the cut, not the whole row (pool 6's C4; § Real tiles). "The only activity" on `b_line_7f_80_aconst` means the operand bus. "At most 84,918 bits an op in live lanes" had no recorded statistic behind it: by `bus_bits_per_op`, `fp32.dropout30_both` flips 87,102. 97,624 is `blind5.json`'s figure, not E141's `scored.json`. One of pool 6's 11 tiles apart from the reference at n = 1 is fp32 (`a_zeros_b_complement`). Rank 4's rule is per format. The anchors' "before" is Q140(c)'s committed −0.15% / −1.04% ± 1.50%. 41 tiles are first reads of their value range |

**For later pools.** Read `../blind5/CORRECTIONS.md` and `../blind6/CORRECTIONS.md` before copying a C check or a
`--check`. Pool 6's C1, C2 and C3 recurred here because this pool's reading list left them out, and pool 6's C1 itself
recurred from pool 5's.

## Independence

The designer read the workflow's brief (all of it; sections 3, 5-7, 17 and 20-24 bind this lane), Q139's final critic
(`result.md` and `result.json`: its prediction table, open list and checks), and these files of this repository, and
nothing else:

- **Repository docs and code.** `tools/claims-v3/kinds/README.md` (sections 1-3); blind pool 6's `README.md`,
  `make_blind6.py` (whose C check this generator copied and whose build it extends) and `fetch_real6.py`; blind pool 5's
  tile list; the tile lists of E78's kinds and pools 3-4; `make_kinds.py` (imported, not modified); E147's and E134's
  README heads and `make_e147.py`'s header (the single-bit layouts and base words); `tools/claims-v3/ccheck/` (`README.md`
  and `ccheck.py`, run read-only for the domain screen and the reference at n = 1).
- **Committed models and results.** M8's README (`docs/reports/data/2026-11-03-q139m-model/README.md`, sections 1-6: its
  terms, `bsat` among them), the brief's permission to read M6, M7 and M8 being how the named classes are aimed; E153's
  README and the power rows of E153's and E157's `scored.json` (pool 6's measured D and every model's error per tile);
  E141's `scored.json` (pool 5's hottest tile); E153's registered stops.

**Never read:** M9, Q140(m)'s or Q140(l)'s scratch, or `docs/reports/data/2026-11-04-q140m-*` / `-q140l-*`. No model code
was run, and no model's prediction chose a tile. Two disclosures: a `git status --short` of the lab tree, run to confirm
the tree was clean, listed the names of five untracked files in Q140(l)'s data directory (names only; none was opened);
and the first `--uniq` scan walked the whole tree, so it hashed any 2,048-byte `.bin` file there (it reported no match and
printed nothing from those directories). `--uniq` now never enters them, and its re-run scanned the same 20,959 files.

**The fix pass** read the verification's result and work files; `../blind6/CORRECTIONS.md` and its
`corrections-check.py`; `../make_e103_pool.py` and `../e103/e103.json`'s tile list; M8's `rows-m8.json` (its rows' kinds
and tile files, to find the held-B kinds M8 trained on), and `predict_blind6.py`'s head and `fit_m8.py` › `c_feats` (what
M8 reads of a pool); Q140(c)'s committed `check3-anchor-card-scale.txt`; E141's `scored.json` and README (the stops row);
`blind5.json`'s and `blind6.json`'s anchor and single-bit tiles. It ran `ccheck.py` and a byte scan of the lab tree. It
read nothing of M9, Q140(l)'s part, their scratch or their data directories, and its scans pruned those directories
before entering them. **One disclosure:** the replacement tile (`int8.bheld_fd`, K1) was designed and built after M9's
freeze commit, where the designer's tiles were final before it. The fix pass never read that commit or any file of M9,
so the timing gives M9 no sight of the tile, and M9, frozen first, cannot have been fitted to it.

## Files

| path | what |
|---|---|
| `make_blind7.py` | the generator, the class and design asserts, the C check (pool 6's, corrected), `--check` and `--uniq` (numpy only; `--kinds-dir` points at `make_kinds.py`) |
| `fetch_real7.py` | fetches the real cuts and runs layers 0-3 of the three checkpoints (numpy and network; `--explore N` prints the outliers; not needed to rebuild) |
| `blind7.json` | per tile: file, type, case, aim, rule (one line), seed, sha256 of the whole file and each half, priority, anchor, run checks, `tile_stats`, `bus_by_field`, `c_check`, `class_descriptors`; plus the counts, the brief check, the subsets and `corrected_before_commit` |
| `MANIFEST` | one line per kind: sha256, file, name, type, case, priority, anchor or kind, hold or not |
| `tiles/<type>/<name>.bin` | the 61 tiles |
| `real/*.npy`, `real/provenance.json` | the 24 cuts the real tiles use, and where they came from |
| `SHA256SUMS` | sha256 of the pool's own 91 files (not itself, and not files placed beside the pool) |
