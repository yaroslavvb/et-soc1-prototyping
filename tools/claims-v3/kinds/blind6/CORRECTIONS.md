# Blind pool 6: corrections after verification

*A dated note: Tue 3 Nov 2026 (week 45), PST. This is Q139(b)'s fix pass, after the pool's independent verification
found that the pool holds, with fixes: one major fault and nine minor ones. **No frozen file changed.** The 81 files
Q139(x) copied in (commit `d98d2e34`) are byte-identical to the pool as verified:
- [`README.md`](README.md) and [`blind6.json`](blind6.json) (sha256 `4c4cee7b…`);
- [`MANIFEST`](MANIFEST) (sha256 `a0e91556…`) and the 50 tiles;
- `real/`, both scripts, and [`SHA256SUMS`](SHA256SUMS) (sha256 `8ab25920…`).

So the tiles, their hashes and every model's frozen predictions stand. **Where the README or `blind6.json` disagrees
with this note, this note governs.** Like the pool, it answers the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) items 6, 7, 13 and 15
(Q138's final critic, ranks 2, 8 and 16). The checks are in [`corrections-check.py`](corrections-check.py). At the desk
it writes [`corrections-check.json`](corrections-check.json) and [`corrections-check.txt`](corrections-check.txt). With
`--network` (huggingface.co) it writes [`corrections-network.json`](corrections-network.json).*

## Results

| | the frozen pool says | corrected |
|---|---|---|
| **C1** (major) | fp16's C follows PRM 9.4's pseudo-code: a two-term update is dropped unless all four halves are nonzero (README § The C check, step 2) | **The card adds the plain sum (E36).** Two tiles change. `fp16.real_smol_softmax_v` (priority 1): C flips an op, start → end, **37,702 → 8,065**, not 35,944 → 7,882. `fp16.real_qwen_dequant_v` (priority 2): **47,517 → 10,800**, not 43,416 → 9,920. `c_op1_sha256` is a desk emulation's, not the card's bytes. The subnormal departure stays, but keeping that value would move C by 9.1e-5 of max \|C\|, not 3% |
| **C2** | C flips at a launch's end: one op from exactly 2^19 (floats) or 2^20 (int8) increments | That count is a power of two, which biases the flips. The mean over eight other counts near a 0.5 s launch moves **10 of 43 tiles by more than 25%** (0.52x to 2.02x), the hold candidate `int8.b_line_zero_ff` among them (14,064 → 9,927) |
| **C3** | `make_blind6.py --check` checks the pool | It sums every file in the directory, so any file beside the pool (this note, a predictions file) makes it report one problem. The pool's check is `shasum -a 256 -c SHA256SUMS` (80 of 80), the MANIFEST hash, and `corrections-check.py` § 6 |
| **C4** | blog: "in a real W8A8 model … a quarter of the int8 words all zero" | One 16×64 cut has 25.0%. Over SmolLM-135M's whole first layer it is **19.65%**; Qwen2.5-0.5B's is 5.44% (2.73% in its cut) |
| **C5** | `exp_only_narrow2`: "every step across 1.0/2.0 flips all eight exponent bits" | The field rolls over between 1 and 2. A step from 1 to 2 flips all eight; every step across 2 flips six to eight (fp16: all five; three to five). The 87% stands |
| **C6** | licence: "see the model card" | Both checkpoints are **Apache-2.0**. Their bases are `HuggingFaceTB/SmolLM-135M-Instruct` and `Qwen/Qwen2.5-0.5B` |
| **C7** | `fp32.a_onebit_b5_third`: "bit 5 set in the odd rows"; one A bit "walking" | Bit 5 is already set in 0x3EAAAAAB, so the odd rows clear it: **0x3EAAAA8B**. The bit flips at each step down a column; it does not walk. The bytes are right |
| **C8** | `--check` passes under numpy 2.5.3 | That evidence was a build from an earlier generator. On the final files it gives 0 problems under numpy 1.26.4, 2.5.3 and 2.5.4, and `fetch_real6.py` reproduces every cut byte for byte |
| **C9** | real tiles: 9 in priority 1 (the critic's rank 8 asks at least 10) | **Score the real-tile sub-rule over all 12 real tiles**, priority 2's three included |
| **C10** | E83: `ones` and `pi` "held 767-782 MHz" over minutes | They held 782.4 and 780.1 MHz. 767.3 MHz is `neg_ones` |

## C1. fp16's two-term update: the card adds the plain sum

**The fault.** The pool's C check emulates PRM 9.4's pseudo-code: the update a1·b1 + a2·b2 applies only when a1, a2,
b1 and b2 are all nonzero. This is in the README's § "The C check" (step 2), in `make_blind6.py`'s `steps_of` and
`run_op`, and in the rule text of `fp16.real_smol_softmax_v`. The chip does not follow that rule. Blind pool 5's
[`CORRECTIONS.md`](../blind5/CORRECTIONS.md) C1 found the same fault there, and the designer's reading list did not
include it.

**The evidence.** E36's LAT-S1 registered *fp16 pair result "math" at 50% and 100%*. Every kept pass on aifoundry1 card
1, aifoundry2 and aifoundry3 (three each) read `fp16_pair_result {"0.0": "both", "0.5": "math", "1.0": "math"}`
([`lat.json`](../../../../docs/reports/data/2026-09-25-claims-v3/results/lat.json) `items[7]`). The test zeroed halves
of A's words; that the rule holds for B's half-zero words follows from the update's symmetry. Q139(k)'s reference
([`../../ccheck/`](../../ccheck/README.md), which reproduces all 110 of E104's card reads) gates only a word pair whose
raw 32-bit A or B word is zero. So a word with one zero half is summed, not dropped.

**The two tiles that change.** The two rules can differ only where an update is dropped although its sum is nonzero,
which takes a word with exactly one zero half (`corrections-check.json` › `c1_fp16_rule`):

| tile | prio | half-zero words (A / B) | updates an op the literal rule drops (with a nonzero sum) | first op's C moves | C flips an op, start → end: frozen | under the card's rule |
|---|---|---:|---:|---:|---|---|
| `fp16.real_smol_softmax_v` | 1 | 8 / 1 | 1,040 (144) | 22.0% of max \|C\| | 35,944 → 7,882 | **37,702 → 8,065** |
| `fp16.real_qwen_dequant_v` | 2 | 0 / 23 | 368 (368) | 19.2% | 43,416 → 9,920 | **47,517 → 10,800** |

In the last column the end figure is C2's corrected descriptor. In the frozen column it is v1's power-of-two figure,
which under the card's rule would read 8,199 and 10,948. Two more tiles drop updates under the literal rule:
`fp16.anchor6_zeros` and `fp16.a_zeros_b_complement` (4,096 an op each). Every update they drop is a whole zero word
summing to zero, so their C is the same under both rules. The other nine fp16 tiles drop nothing. Under the card's
rule every fp16 tile still passes the C check: the operands are finite, C stays finite, and the first op's C is within
1.8e-07 of the exactly rounded sum of every product. For the two tiles above, the frozen "exact reference" left out
the dropped products. Section 0 first reruns `make_blind6.c_check`, unchanged, on all 50 tiles: every one equals
`blind6.json`, under numpy 1.26.4 and 2.5.3. So the corrected numbers come from the designer's own code, with one rule
changed.

**`c_op1_sha256` is not the card's bytes.** It hashes this desk emulation's first-op C: float64, then rounded to fp32
nearest even, starting from +0. Q139(k)'s reference differs in two ways:
- **fp16:** it truncates each aligned product in the RTL's fixed-point window;
- **op 0:** it starts with a multiply rather than an add to +0, and it skips gated word pairs.

Against `ccheck.py ref` at n = 1 (§ 4):

| format | the first op's C equals the reference | the rest |
|---|---|---|
| fp32 | 17 of 18 | `fp32.a_zeros_b_complement` differs in the sign of 128 zero words. A is all +0, so op 0's multiply leaves −0 wherever B is negative, and every later product is gated |
| int8 | 19 of 19, by value | `c_op1_sha256` hashes int64 values (2,048 bytes), so it can never equal the card's 1,024-byte C |
| fp16 | 3 of 13, under either rule (`anchor6_zeros`, `exp_only_narrow2`, `b_onebit_b6_third`) | 9 differ by 1 to 813 ulp in 119 to 256 words (the RTL's truncation); `a_zeros_b_complement` differs only in zero signs. Under the literal rule the two tiles above are off by up to 22% of max \|C\| |

So no pool-6 hash checks a card's C. **E153's, E157's and E160's C check is `ccheck.py`**, as Q139(k)'s README says.
`corrections-check.json` › `c4_first_op_against_ccheck` gives each tile's reference hash at n = 1.

**The subnormal departure stays; its reason changes.** One SmolLM value, −4.81e-05 at k 9, column 0 of B, rounds to an
fp16 subnormal, and the tile writes it as +0.0. The README says that keeping it would move the first op's C by 3% of its
largest element. That is the literal rule's figure (3.04%): there, a zero half drops the whole update. Under the card's
rule it is **9.07e-05** (`c3_subnormal_departure`). The departure is kept because every operand stays normal or zero.
That keeps the tile inside the domain Q139(k)'s reference was checked on (`ccheck.py domain` flags denormal operands),
and C does not depend on whether the unit flushes subnormals. The frozen tile equals the cut with that one value zeroed
(checked).

**What it changes.** Any C-term arm, and any model input that describes C, takes fp16's C under the card's rule:
`corrections-check.json` › `corrected_c_descriptors` (all 50 tiles, start and end), or › `c1_fp16_rule.tiles.<name>.card_c_check`
for the full check. Untouched: the tiles, their hashes, the counts, the hold candidates, and the frozen predictions.
The verification found that M8's `predict_blind6.py` does not read `c_check`. A launch of `fp16.real_qwen_dequant_v`
(23 half-zero B words) or `fp16.real_smol_softmax_v` (one) with C checked by `ccheck.py` tests the card's rule on B's
half-zero words on silicon (E36 tested A's). A card that dropped those updates would FAIL there.

## C2. The launch-end C descriptor: not from a power of two

`c_launch_end_est` runs one op from C = n × the op's exact increment, with n = 2^19 = 524,288 (floats) or
2^20 = 1,048,576 (int8). At a power of two, C is the increment with only its exponent moved, so C's low bits are not
those of a typical count. The corrected descriptor is the mean over 32 consecutive ops from each of eight starting counts, and none of them is a power
of two. The counts are spread over ±17.5% of a 0.5 s launch at 600 MHz (549,451 ops at 546 cycles; 943,396 int8 ops at
318); fp16 is taken under the card's rule (`c2_launch_end`). Over the 43 tiles whose C moves, the corrected figure runs
0.52x to 2.02x the frozen one (median 0.98x). Ten tiles move by more than 25%:

| tile | frozen (one op from 2^19 or 2^20) | corrected, mean [range of the 8 starts] | ratio |
|---|---:|---:|---:|
| `fp32.c_absorbed` | 256 | 516 [504-552] | 2.02 |
| `fp16.c_absorbed` | 256 | 516 [504-552] | 2.02 |
| `fp32.exp_only_narrow2` | 11,296 | 6,465 [6,288-6,667] | 0.57 |
| `fp16.exp_only_narrow2` | 14,004 | 9,043 [8,733-9,386] | 0.65 |
| `int8.bheld_bit4` | 28,656 | 19,941 [19,856-20,032] | 0.70 |
| `int8.b_line_zero_ff` (hold candidate) | 14,064 | 9,927 [9,841-10,003] | 0.71 |
| `int8.a_word_zero_one` | 14,480 | 10,175 [10,141-10,257] | 0.70 |
| `int8.powerlaw_df15_pt` | 5,984 | 3,137 [3,131-3,142] | 0.52 |
| `int8.real_smol_w8a8_down` | 20,158 | 15,694 [15,682-15,708] | 0.78 |
| `int8.real_qwen_w8a8_down` | 23,841 | 17,519 [17,484-17,552] | 0.74 |

The other hold candidates: `int8.real_qwen_w8a8_v` 29,125 → 23,967; `fp32.a_onebit_b5_third` 7,936 → 8,190;
`fp32.real_smol_softmax_v_causal` 5,645 → 5,654. The README's column "C flips/op, start → end" is replaced by
`corrected_c_descriptors`. Both figures are desk descriptors of the emulation, not measurements. The pool offers them
as descriptions, not as a model input.

## C3. `make_blind6.py --check` and files beside the pool

`--check` compares SHA256SUMS against every file in its directory (`disk_files_for_sums`, lines 910-920). So once any
file sits beside the pool it reports one problem, `MISMATCH SHA256SUMS`, even though the 52 files it builds still compare
equal. That covers this note, and predictions placed here as Q138(x) placed pool 5's: Q139(x)'s commit put eleven files
here (its predictions, counts and card-scale files, listed by name in `corrections-check.json` › `c6_files`). Pool 5's
committed `--check` fails the same way today. The pool's check, which passes with any file beside it, is:

```bash
cd tools/claims-v3/kinds/blind6 && shasum -a 256 -c SHA256SUMS      # 80 of 80 OK
shasum -a 256 MANIFEST                                              # a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0
python3 -B corrections-check.py --ccheck                            # § 6: the 52 built files equal, every other file listed
```

The pool itself is 81 files: the 80 that SHA256SUMS lists, plus SHA256SUMS. Anything else here (this note's five files,
predictions) sits beside it.

## C4. Blog point 1: a cut, not the model

The pool's result said: *"In a real W8A8 model, quantising the down projection's input per token leaves a quarter of the
int8 words all zero."* That 25% is one 16×64 cut: tokens 16-31 and hidden units 0-63 of SmolLM-135M's layer 0.
`fetch_real6.py`, unchanged, was re-run with the layer kept (`corrections-network.json` ›
`models.<m>.down_input_int8_zero_word_frac`):

| model | whole layer (32 tokens) | tokens 16-31 | the pool's cut |
|---|---:|---:|---:|
| SmolLM-135M-Instruct W8A8 (1,536 hidden units) | **19.65%** | 21.55% | 25.00% |
| Qwen2.5-0.5B W8A8 (4,864 hidden units) | **5.44%** | 5.53% | 2.73% |

A word is 4 consecutive hidden units, the gate's unit. Corrected: *In SmolLM-135M's first layer, quantising the down
projection's input per token, as its W8A8 checkpoint does, leaves 19.7% of the int8 words all zero (25% in the pool's
16×64 cut). So the chip's zero gate would close on about a fifth of that matmul's multiplier slots. Qwen2.5-0.5B's
first layer leaves 5.4%.*

## C5. `exp_only_narrow2`: where the exponent field rolls over

fp32's exponent field reads 0x7F for [1, 2) and 0x80 for [2, 4), so the rollover is between 1 and 2, across 2.0, not
1.0. The tile's fields are 125-129 (1/4 to 4). A step from 1 to 2 flips all eight exponent bits
(0x7F ^ 0x80 = 0xFF), and every step across 2 flips six to eight (0x7D ^ 0x81 = 0xFC has six). fp16's tile (fields
13-17) rolls over from 01111 to 10000 between 1 and 2. A step from 1 to 2 flips all five, and every step across 2
flips three to five (`c5_rule_texts`). The exponent share of the bus flips stands: 0.87 for fp32 and 0.83 for fp16.
The README's case E line, "powers of two across 1.0", should read *across 2*. Blog point 2, corrected: *Powers of two between
1/4 and 4 look like easy numbers, but fp32's exponent field rolls over from 0x7F to 0x80 between 1 and 2. A step from 1
to 2 flips all eight exponent bits, and every step across 2 flips six to eight. So 87% of such a tile's operand flips
are exponent flips.*

## C6. The real tiles' licences

`real/provenance.json` says `"license_note": "see the model card"`. Each model card was read at the pinned revision
from huggingface.co's model API: `cardData.license`, the `license:` tag and `cardData.base_model`, in
`corrections-network.json`.

| repo | revision | licence | base model |
|---|---|---|---|
| `RedHatAI/SmolLM-135M-Instruct-quantized.w8a8` | `203f247e5fdd358199df1cecd839a5b8fe5c9473` | Apache-2.0 | `HuggingFaceTB/SmolLM-135M-Instruct` |
| `RedHatAI/Qwen2.5-0.5B-quantized.w8a8` | `0d1951533baeec89dd257df86d4d10c3bd5429f5` | Apache-2.0 (the card links the base model's LICENSE) | `Qwen/Qwen2.5-0.5B` |

The text, the opening of *Pride and Prejudice* (1813), is public domain.

## C7. Rule texts of the single-bit tiles

- **`fp32.a_onebit_b5_third`:** 1/3 is 0x3EAAAAAB, whose low byte 0xAB already has bit 5 set. So the tile's odd rows
  clear it: **0x3EAAAA8B**; the even rows hold 0x3EAAAAAB (checked on the bytes). The rule should read *bit 5 cleared
  in the odd rows*. The hold candidate's description should read *one A bit flipping* (at every step down a column),
  not *walking*.
- **`fp32.a_onebit_b16_half`:** its odd rows are 0x3F010000 (bit 16 set; 0.5 has none). It is the same pattern:
  one bit flipping, not walking.

## C8. Reproducibility, re-run on the final files

The README's numpy-2 claim rested on a build from an earlier generator, one with a different `fp16.real_smol_softmax_v`.
The fix pass re-ran it on a clean copy of these 81 files:
- **`make_blind6.py --check`: 0 problems** under numpy 1.26.4 (Python 3.9.6), 2.5.3 (3.12.12) and 2.5.4 (3.15.2);
- `shasum -c`: 80 of 80;
- no `__pycache__` left behind.

The frozen `fetch_real6.py`, run again into a temporary directory under numpy 2.5.3, reproduces from huggingface.co
**all 24 cuts and `real/provenance.json` byte for byte** (`corrections-network.json`). `corrections-check.py` gives the
same JSON under numpy 1.26.4 and 2.5.3.

## C9. Rank 8's real-tile sub-rule: all 12 tiles

The critic's rank 8 asks for at least 10 real tiles. Priority 1 holds 9: SmolLM 5 and Qwen 4. A session that runs
priority 1 alone therefore under-fills it. **E153 and E157 (and E160) register the real-tile sub-rule over all 12 real
tiles.** That takes priority 2's three with it: `fp32.real_qwen_softmax_v`, `fp16.real_qwen_dequant_v` and
`int8.real_qwen_w8a8_down`.

## C10. E83's clocks over minutes

The README's § "Below the stops" gives E83's 76 s runs of fp32 `ones` and `pi` as holding 767-782 MHz at about 53 W.
E83's table (§ 2) gives `ones` 782.4 MHz and `pi` 780.1 MHz, both at 53.3 W. 767.3 MHz is `neg_ones`, at 52.0 W. It
should read *780-782 MHz (`neg_ones` 767)*.

## For E160 (not a fault of the pool)

Section 22 of the round's brief allows no tile on aifoundry2 whose predicted peak board power exceeds 82 W, unless it
is duty-cycled. **`fp32.anchor6_randn`'s relative, E143's fp32 random anchor, read 83.37-83.79 W** in its first second
at 800 MHz. `fp32.wideexp48_dense` read 86.01-86.18 W
([E143 `results.json`](../../../../docs/reports/data/2026-11-02-e143-blind5-aifoundry2/results.json) ›
`score.reported.tiles.<name>.p800_w_runs`). So E160 duty-cycles or drops `fp32.anchor6_randn`. It applies the rule to
every other tile with the frozen predictions; the pool names none. The four hold candidates' relatives drew 43-61 W, as
the README says.

## What this does to predicting power and heat

It measures nothing, and item 6's test set is unchanged: the same 50 tiles, hashes and frozen predictions. It
corrects **the inputs of the C-register candidate** (rank 2).
- Two fp16 tiles' C under the card's rule: 37,702 and 47,517 flips an op at the start, not 35,944 and 43,416.
- The launch-end descriptor: by more than 25% on 10 of 43 tiles.

A C-term arm registered on pool 6 must take `corrected_c_descriptors`. The note also widens rank 8's sub-rule to all
12 real tiles, and it flags the random fp32 anchor for E160's 82 W rule.
- **Before (pool 5, registered primaries):**
  - power of a new kind on aifoundry3: 0.325 / 0.317 / 0.356 W rms on fp32 / fp16 / int8, and on aifoundry1 card 1
    0.169 / 0.149 / 0.251 W;
  - heat over 4.5 s: 0.13 °C rms;
  - single exponent flips: M6 0.307 W rms, bias −0.259 W (E147);
  - int8's steady misses: −0.61 / −0.60 / +0.50 W (E141).
- **After:** E153, E157 and E160 measure M8 against M6 and M7 on these tiles. No out-of-sample error changes until then.

## Independence of the fix pass

The fix pass read the verification's result and work files and the reads listed in this note:
- blind pool 5's `CORRECTIONS.md`, `corrections-check.py` and `corrections-check.json`;
- `lat.json` › `items[7]`;
- Q139(k)'s `ccheck/README.md` and `ccheck.py`;
- E83's README § 2;
- a grep of E143's README (its peaks paragraph among the hits) and three `p800_w_runs` fields of its `results.json`;
- the two model cards, by API.

At 04:59 PST, `git log` showed it the subject line of M8's freeze commit (`122da8b6`, 04:57:59). By then the pool's
tiles had been fixed for over half an hour: the designer's last file is from 04:23. In Q139(x)'s scratch it listed the
file names and opened one file, a wait script, to rule out the two lanes waiting on each other (Q139(x) was waiting on
its own bench run). It read no file of M8 or of Q139(m)'s data directory or scratch, and no predictions. No tile,
MANIFEST line, count or hold candidate changed.

## Files

| file | what |
|---|---|
| `CORRECTIONS.md` | this note |
| `corrections-check.py` | the checks. Numpy only by default; it reads this pool and `make_kinds.py`. `--ccheck` adds § 4 (cc and `../../ccheck/ccheck.py`); `--network` reruns `fetch_real6.py` (huggingface.co, about 28 MB) |
| `corrections-check.json` | § 0-6, and `corrected_c_descriptors` (the C descriptors a C-term arm takes) |
| `corrections-check.txt` | its printout |
| `corrections-network.json` | § 7: every cut and `provenance.json` reproduced, the zero-word shares, the licences |

```bash
python3 -B tools/claims-v3/kinds/blind6/corrections-check.py --ccheck    # about 50 s on the Intel; exit 0 = every check holds
python3 -B tools/claims-v3/kinds/blind6/corrections-check.py --network   # about 25 s; exit 0 = cuts and provenance reproduced
```

These five files sit beside the frozen pool, as pool 5's do.
