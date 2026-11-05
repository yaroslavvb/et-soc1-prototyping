# Blind pool 8: the design (Q142(d))

*Written Wed 4 Nov 2026, 23:20-23:35 PST, by the round's independent pool-8 designer, before any tile of the pool
exists. Committed together with its generator, [`make_blind8.py`](make_blind8.py), the code this file describes.
The pool is made only after this commit, by the committed file: `build` refuses to run when the file differs from
its committed blob. A later change is a dated amendment, a new file committed before the tiles it governs.*

## 0. The aim, and what the designer read

**The aim** (the round's subsection for this lane): a blind pool on which M10 and M9 are both predicted before any
card measures it, drawn by someone who has never seen any model's errors. Pool 8 must exercise, by name only, what
M10 adds to M9 (a float scale per session read from that session's own random anchors; the single high B bits
counted at launch points by a convergence rule; heat per board watt and card 0's burst coefficient; the heat chain's
gain over minutes; card 0's die-start footing) and what M9 prices (operand bit toggles by format and field: the fp32
exponent field, int8 whole lines and held B among them).

**Read:** the committed pools' `MANIFEST`, `SHA256SUMS`, `tiles/`, `real/` and `fetch_real*.py` (blind3 to blind7),
`make_kinds.py`, the public models' config, tokenizer and weights, and the round's notes on compute and on this
lane. **Not read:** any pool's README, `blindN.json`, `make_blindN.py`, `provenance-blindN.json`, corrections,
card-scale, predictions, counts, crosscheck, admission or a2-input files, the M10 directory, anything under
`docs/reports/data/`, any critic's directory.

**One exposure, disclosed.** At 23:19 PST, after the generator was written and dry-run on a test seed, a
`git log` call made to copy the lab's commit-message convention printed the first 200 characters of each paragraph
of the two latest lab commits. One of them, a records commit, quotes one aggregate held-out error figure of one model
over the float formats (no figure per kind or class). Nothing was changed after it: the generator's sha256 was recorded at that moment
(`fee9a4f01d32795e526c0b8ec06657b04024e8413351302080422643a76d14ea`, last modified 23:18:32), and the committed
`make_blind8.py` is that file, byte for byte. Every choice in it was fixed before the exposure; this file only
describes them.

## 1. The seed

```
SEED_COMMIT = "c996d1357609c10009c80e59dd8e85bcc652343f"
SEED = int(sha256(SEED_COMMIT.encode("ascii")).hexdigest()[:16], 16)
     = 0x1da1fde559d92805 = 2135266859847067653
```

The round named the commit and suggested this rule; the value follows from it and cannot be chosen.
Every random draw comes from one stream per tag, `rng(seed, *tag) = numpy.random.default_rng([seed, t])` with `t` the
first 8 bytes (little-endian) of `sha256("blind8/" + "/".join(tag))`, which is `make_kinds.rng_for`'s scheme. Every
choice made "by the seed" is a draw on a named stream or an order by `rank(seed, *tag) = sha256(f"{seed}/" +
"/".join(tag))`. The tags are listed with each rule below. Before this commit, the only seed ever run was
`TEST_SEED` (the first 16 hex digits of sha256 of `blind8 dry run, never the pool`), whose tiles went only to a
directory named TEST in the lane's scratch.

## 2. The tile format and the pool's files (pool 7's form)

Every tile is 2,048 bytes: the A tile, then the B tile, 1,024 bytes each, in `make_kinds.py`'s layout (16 lines
of 64 bytes; a 32-bit word is one lane operand; fp32 K=16, fp16 K=32, int8 K=64). The card runs it with
`sparsity_host --test fma --type <fmt> --values file:<tile>`.

The pool directory holds:

- `MANIFEST`: one line a tile, pool 7's eight fields: `sha256  file  label  format  case=<class>  p<priority>
  role  flag`. Roles: `anchor` (random anchors a and b, and the floor), `check` (the check anchor), `kind` (a new
  tile), `rerun` (an earlier tile under its own label, scored apart). Flag: `-`, or `rerun:<pool>` for every tile
  whose bytes are an earlier pool's.
- `tiles/<fmt>/<label>.bin`;
- `RERUNS`: every `rerun:` tile, with its source pool, its statistic and why it was picked;
- `provenance-blind8.json`: every tile's rule, stream, parameters, byte signature, statistics (`make_kinds.tile_stats`:
  bus bits per op, gated fraction, per-field toggles), half-twins, the inputs read (with hashes), and the generator's
  own sha256, git blob and commit;
- `real/`: the real cuts as float32 `.npy` arrays and `real/provenance.json` (models, revisions, licences, text,
  tokens, every fetched byte range with its sha256, the seeded plan, the outlier picks);
- `README.md` (what each class aims at, the quota table) and `SHA256SUMS`.

## 3. Quotas and this pool's plan

| Class | The round's quota | Planned | How |
|---|---|---|---|
| 0, anchors | two random anchors per format plus a check anchor per format | 9 + 3 floor | a, b and check per format; plus the all-zero floor under pool 7's label |
| S, single high B bits | at least 8, new bit positions and base words, fp32 and fp16 | 10 (6 fp32, 4 fp16) | §5.2 |
| U, no named class | at least 12 kinds from the generator | 13 (5 fp32, 4 fp16, 4 int8) | §5.3 |
| L + H, int8 whole lines and held B | at least 6 | 7 (4 L, 3 H) | §5.4 |
| R, real | at least 8, from 2 or more public models no earlier pool used, int8 W8A8 outlier activations among them | 10 (4 int8 W8A8, 3 fp16, 3 fp32) from 2 models | §5.5 |
| rerun | about 12 pool 6/7 float tiles, own labels, scored apart, spanning the data term | 12 (8 fp32, 4 fp16) | §5.6 |
| all | | 64 | |

`build` exits non-zero if a quota is not met, and `README.md` gives the counts it made.

## 4. How each label is computed from the bytes

Every new tile's label is `<fmt>.<slot>_<sig>`. The **slot** names the committed rule that drew the tile (fixed
here, before any tile). The **sig** is computed from the 2,048 bytes by `byte_sig`. The **class** the tile is filed
under must be borne out by its bytes (`class_check`), or the tile is refused:

| Class | slot(s) | sig, from the bytes |
|---|---|---|
| 0 | `anchor8_randn_a`, `anchor8_randn_b`, `anchor8_check_randn` (fp32, fp16); `anchor8_full_a`, `anchor8_full_b`, `anchor8_check_full` (int8) | 6 hex of the tile's sha256 |
| S | `s8_onebit` | `b<bit>_<base word hex>`, plus `_A<A word hex>` when A is not 1.0 |
| U | `u8_<family>` | 6 hex of the tile's sha256 |
| L | `l8_flip`, `l8_period2`, `l8_cycle3`, `l8_halfword` | `d<distinct B lines>p<period>c<changing boundaries>_<4 hex of sha256>` |
| H | `h8_held` | `v<byte hex>` when every B byte is one value, else `line<4 hex of sha256 of B line 0>` |
| R | `r8_<model>_l<layer>_<cut>` | 6 hex of the tile's sha256 |

The re-runs and the floor keep their earlier labels, read from blind6's and blind7's `MANIFEST`, and are listed
in `RERUNS`. The code (from `make_blind8.py`):

```python
def single_bit_b(raw, fmt, mk):
    """A single-high-B-bit tile: A one word everywhere; B columns 0-7 one word and columns 8-15 another, in every
    line, the two differing in one bit (per element).  Each lane then alternates between the two every cycle."""
    if fmt not in ONE:
        return None
    aw, bw = mk.words_of(raw)
    a = {int(x) for x in aw.ravel()}
    lo = {int(x) for x in bw[:, :8].ravel()}
    hi = {int(x) for x in bw[:, 8:].ravel()}
    if len(a) != 1 or len(lo) != 1 or len(hi) != 1:
        return None
    w0, w1 = lo.pop(), hi.pop()
    bit = one_bit(w0 ^ w1, fmt)          # one bit (fp32), or the same one bit in both halves (fp16)
    if bit is None:
        return None
    return {"side": "B", "bit": bit, "base": w0, "flipped": w1, "a_word": a.pop()}

def int8_lines(raw):
    B = raw[1024:]
    lines = [B[64 * p:64 * (p + 1)] for p in range(16)]
    period = next(p for p in range(1, 17) if all(lines[i] == lines[i + p] for i in range(16 - p)))
    vals = set(B)
    return {"distinct": len(set(lines)), "period": period,
            "changes": sum(1 for p in range(16) if lines[p] != lines[(p + 1) % 16]),
            "byte": next(iter(vals)) if len(vals) == 1 else None, "lines": lines}

def structure(raw, fmt, mk):
    if fmt in ONE:
        return "S" if single_bit_b(raw, fmt, mk) else "G"
    info = int8_lines(raw)
    if info["distinct"] == 1:
        return "H"
    if 2 <= info["distinct"] <= 4:
        return "L"
    return "G"

def byte_sig(raw, fmt, cls, mk):
    if cls == "S":
        s = single_bit_b(raw, fmt, mk)
        sig = f"b{s['bit']}_{s['base']:08x}"
        if s["a_word"] != ONE[fmt]:
            sig += f"_A{s['a_word']:08x}"
        return sig
    if cls == "H":
        i = int8_lines(raw)
        return f"v{i['byte']:02x}" if i["byte"] is not None else f"line{sha(i['lines'][0])[:4]}"
    if cls == "L":
        i = int8_lines(raw)
        return f"d{i['distinct']}p{i['period']}c{i['changes']}_{sha(raw)[:4]}"
    return sha(raw)[:6]

def class_check(raw, fmt, cls, role, mk):
    st = structure(raw, fmt, mk)
    want = {"S": "S", "H": "H", "L": "L"}.get(cls, "G")
    if st != want:
        return False, f"bytes read as {st}, class {cls} needs {want}"
    if role in ("anchor", "check"):            # the anchors' rule's moments, per side
        ...                                    # int8: sd 65-85, min <= -120, max >= 120; floats: |mean| < 0.3, sd 0.8-1.2
    return True, "ok"
```

`make_blind8.py check --out <pool>` re-reads every tile and re-derives its label from the bytes, as here.

## 5. The rules, class by class

### 5.1 Anchors (class 0)

Per format, on streams `anchor/<fmt>/a`, `anchor/<fmt>/b` and `anchor/<fmt>/check`. The rules are pool 7's: A and
B standard normal for fp32 and fp16 (fp16 rounded to nearest), and uniform over -128..127 for int8.

- **a** and **b** are the two random anchors (role `anchor`).
- **check** is a third draw of the same rule, held out (role `check`). M10 reads its session scale from a and b;
  the check anchor is predicted with that scale and measured, which checks it.
- **The floor**: the all-zero tile of each format (role `anchor`, flag `rerun:blind7`), kept under pool 7's own
  label `<fmt>.anchor7_zeros`. Its bytes are pool 6's and pool 7's zeros, so a new label would be a byte twin.

All anchors are p2, as pool 7's were.

### 5.2 Single high B bits (class S)

The structure of pools 6 and 7: A is one constant word. B columns 0-7 hold a base word and columns 8-15 hold the
base with one bit flipped (in fp16, the same bit in both halves), in every line. Each lane's B operand therefore
toggles that one bit every cycle, and nothing else moves.

- **Bit positions.** First, every earlier single-bit tile of blind3-blind7 is found from its bytes
  (`single_bit_any`: the B structure above, or its A-side mirror). The positions they used are removed: fp32 5, 12,
  16, 20 and 22; fp16 6, 8 and 9 (blind3-5 hold none of either structure). Then, per stratum, the seed draws
  without replacement on stream `S/<fmt>/bits/<stratum>`:
  - fp32: two from the high mantissa (16-22), two from the middle mantissa (8-15), one from the low mantissa (0-7),
    and one from the exponent's bits 23-28 or the sign bit 31;
  - fp16: one from 7-9, two from 0-6, and one from exponent bits 10-12 or the sign bit 15.
- **Base words.** Drawn on stream `S/<fmt>/base/<bit>`: a random sign, a biased exponent uniform in 124-130 (fp32)
  or 13-17 (fp16), and random mantissa bits. A draw is redrawn unless both the base and the flipped word are normal,
  finite and of magnitude 2^-40..2^40 (fp32) or 2^-10..2^10 (fp16), and neither equals an earlier single-bit tile's
  word or a word already drawn.
- **A.** The word 1.0, except one tile: the second fp32 middle-mantissa pick holds A at a seeded positive constant
  (exponent 126-128, random mantissa, stream `S/fp32/a/<bit>`), as pool 7 held one tile at A = 1.5.

### 5.3 Kinds aimed at no named class (class U)

The seed draws the families from a fixed menu, on stream `U/<fmt>/families` (a permutation; the first n are
taken), and then each family's parameters, on `U/<fmt>/<family>`:

| Menu | Families (n drawn) |
|---|---|
| fp32 (5), fp16 (4) | `tdist` (Student t, df 2.5-8, scale 2^-4..2^4, clipped at 64 scales); `lognorm` (exp(N(mu, sigma)) magnitudes, mu -2..2, sigma 0.5-2.5, random sign); `mixture` (normal with a 1-10% wide component 8-128x wider); `uniform` (half-width 2^-6..2^6, log-uniform); `expo` (A exponential, B normal, separate scales); `grid` (normal on a grid of 2^-q, q 1-6, clipped at 4 sigma); `rowscale` (log-normal per-row A and per-column B scales); `sparse` (each side's elements zero with p 0.1-0.8); `ar_i` (AR(1), rho 0.8-0.99, along A's rows and B's columns, the stream directions); `ar_k` (AR(1) along k); `bimodal` (±m plus noise); `cauchy` (clipped at 1,000 scales). fp16 is clipped at ±60,000. |
| int8 (4) | `tq` (round(s·t(df))); `geom` (two-sided geometric); `urange` (uniform over ±2, 4, 16, 32 or 64); `biased` (normal with mean -80..80); `sparseq` (rounded normal with p 0.2-0.7 zeros); `pm` (±m only); `ar_k` (AR(1) along k, rounded); `relu_tq` (A rounded ReLU(normal), B rounded t) |

### 5.4 int8 whole lines (class L) and held B (class H)

A is uniform over -128..127 in every one of these. The held values that earlier pools used are read from the bytes
(an int8 tile whose B is one byte value): 0x00, 0x01, 0x02, 0x10, 0x33, 0x55, 0x5a, 0x80, 0xfd and 0xff.

- **H, `h8_held`** (streams `H/v1`, `H/v2`, `H/line`):
  - one byte value with popcount 3;
  - one negative byte value with popcount 5 or 6;
  - in both, the value is drawn from the values no earlier pool held;
  - and one line of round(12·N(0,1)) bytes, held for all 16 k-groups.
- **L** (streams `L/flip`, `L/period2`, `L/cycle3`, `L/halfword`):
  - `flip`: lines alternate X and X xor M, where M sets k bits in every byte (k drawn from 2-5);
  - `period2`: X, X, Y, Y, ..., a change at every second boundary;
  - `cycle3`: X, Y, Z, X, ...;
  - `halfword`: X and Y alternate, where Y is X with words 8-15 (columns 8-15) complemented, so half of each line
    changes at every boundary.
  - X, Y and Z are random lines.

### 5.5 Real tiles (class R)

**Models.** Two public W8A8 checkpoints that no earlier pool used. Earlier pools used pythia-70m, Qwen2.5-0.5B
(plain and W8A8), SmolLM-135M and SmolLM-360M. Both checkpoints are safetensors only, compressed-tensors
"int-quantized": int8 weights symmetric per output channel, and int8 activations symmetric, dynamic, per token.

| Key | Repo | Revision | Licence (model card) | Base |
|---|---|---|---|---|
| `granite` | RedHatAI/granite-3.1-2b-instruct-quantized.w8a8 | `ba87c9abf4e5ccd3e1255925eb490991809a89ab` | apache-2.0 | ibm-granite/granite-3.1-2b-instruct |
| `dsqwen` | RedHatAI/DeepSeek-R1-Distill-Qwen-1.5B-quantized.w8a8 | `eb5a917a789bcf9f76eee7b3f61a12d647e2d37a` | mit | deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B |

`build` asserts each config's geometry and quantisation scheme (the values are in `REAL_MODELS` and
`QUANT_EXPECT`) and each tokenizer's pre-tokenizer.

**Text.** Mary Shelley, *Frankenstein* (1818), the opening of Letter 1, public domain: ASCII, with no digits. Each
model's own byte-level BPE gives the tokens (its tokenizer.json split, merges by rank, no special token), and the
first 32 are kept.

**Forward pass.** Layers 0-5, in float32, with W8A8 linears. Activations are quantised per token: scale = the
token's max |x| over its whole row / 127, rounding half to even, clipped to ±127, which is pool 7's reading of the
scheme. The products are int8 × int8, exact in float64, then times the token's scale and the channel's scale. The
steps:

1. Granite only: the embeddings are multiplied by `embedding_multiplier`.
2. RMSNorm.
3. q, k and v projections, with a bias where the checkpoint has one (dsqwen).
4. Rotary over the whole head.
5. Scores q·k × `attention_multiplier` (Granite) or × 1/sqrt(head dim) (dsqwen), with grouped KV heads.
6. Causal softmax, then P V.
7. o_proj, then the residual (Granite: × `residual_multiplier`).
8. RMSNorm, then the gate and up projections, then SiLU(gate) × up.
9. down_proj, then the residual.

**The cuts.** Each model gives five. Every choice is drawn on stream `real/<model>`, in the order `real_plan`
draws them:

1. the int8 layer L8 and the float layer Lf, each in 1-5;
2. for each cut, a token window (tokens 0-15 or 16-31);
3. the q/k/v projection;
4. the weight rows (aligned blocks of 16 output channels);
5. the heads and the 16-dim head blocks;
6. gate or up;
7. the dequantised cut's dim block.

The windows, rows and blocks of different cuts are interleaved in that order.

The outlier blocks are chosen by a rule on the data, never by hand:

- **int8 `x1<proj>`**: A is the input_layernorm output at L8, quantised per token over all dims, cut to the
  aligned 64-dim block that holds the commonest per-token argmax of |x| (the outlier dim). B is that projection's
  own int8 weight rows × the block, transposed.
- **int8 `actdown`**: A is SiLU(gate)·up at L8 (down_proj's input), quantised per token, cut to the 64-unit block
  that holds the top unit of the window's most outlying token (its largest max/median of |x|). B is down_proj's
  int8 rows × the block, transposed.
- **fp16 `pv`**: A is the causal softmax of a seeded head at Lf (queries of the window × keys 0-31). B is that KV
  head's values (tokens 0-31 × a 16-dim block).
- **fp32 `qk`**: A is the rotary queries (window × 16 dims). B is the rotary keys of tokens 0-15, transposed.
- **`x2<gate|up>`**: A is the post_attention_layernorm output (window × a seeded K-block). B is the dequantised
  gate or up weights (int8 × the channel's bf16 scale, exact in float32), transposed. It is fp16 for one model and
  fp32 for the other; stream `real/dequant-format` decides which.

`real/provenance.json` records every cut's rows, dims, heads, windows and outlier statistics (per-row max/median
and the share of int8 codes in {-1, 0, 1}).

### 5.6 Re-runs (role `rerun`) and the data term

The candidates are pool 6's and pool 7's MANIFEST lines with role `kind` in fp32 or fp16, one for each distinct
sha256. The statistic is `make_kinds.tile_stats(raw)["bus_bits_per_op"]`: the operand bits that the unit's input
bus flips in one op, which is the sum of every field's toggles that M9 prices. It is computed from the bytes,
because this design never sees a model's terms.

The rule, per format, with 8 picks in fp32 and 4 in fp16:

1. Sort the candidates by (statistic, `rank(seed, "rerun", label)`).
2. Take the minimum and the maximum.
3. Split the rest into n-2 contiguous equal-count strata, and from each take the tile with the smallest
   `rank(seed, "rerun", label)`.

The picks therefore span the statistic's whole range, and the seed chooses within each stratum. A re-run is copied
byte for byte from its pool's committed file and keeps that pool's label and class (`case=` as in its MANIFEST).
Its role is `rerun` and its flag is `rerun:<pool>`, and it is scored apart from the new tiles.

## 6. Admission and the byte-twin check

Every tile passes `tile_refusal` and `class_check` (§4), or `build` refuses it and records why. `tile_refusal`
requires exactly 2,048 bytes and no NaN or Inf, and requires that `make_kinds.encode` accepts the decoded elements
and gives back exactly these bytes.

**Byte twins.** Every tile's 2,048 bytes are hashed against every tile file of blind3-blind7 (197 files). Each
pool's `SHA256SUMS` is compared with its files on the way, and the agreement is recorded (197 of 197 agreed in the
dry run).

- A new tile whose sha256 is an earlier tile's is refused: an earlier tile's bytes never appear under a new label.
- A re-run or floor tile must match its own earlier tile, under that tile's own label, or `build` stops.
- No two tiles of the pool share bytes, except the floor's zeros across the three formats, as in pool 7.
- Half-twins (an A or B half equal to an earlier tile's half, such as the constant 1.0 A of every S tile) are
  recorded in the provenance and not refused.

Power admission (the tiles predicted over 82 W) belongs to the next round's (x) lane.

## 7. Priorities

The anchors and the check anchor are p2, as pool 7's anchors were. Every other group (S, U, L+H, R, re-runs) is
sorted by `rank(seed, "prio", label)`, the last round(n/4) of each group (at least one) are p2, and the rest are p1.

## 8. Downloads

`fetch` puts each model's bytes into three new empty directories, `<dl>/<key>-config`, `<key>-tokenizer` and
`<key>-safetensors`, and refuses one that exists. It uses HTTP range requests at the pinned revisions: the
safetensors header, the embedding rows of the text's tokens, and every tensor of layers 0-5. It downloads under a
byte cap. `build` reads only those directories and never the network.

The scripts run under `python3 -I`, and parse only JSON and raw little-endian arrays: no pickle, and safetensors
only.

The lane's downloads in all:

| Download | When | Size |
|---|---|---|
| Model API, config, tokenizer and header probes | before this commit | about 11 MB |
| Test fetch at depth 2, for the dry run | before this commit | 226 MB |
| The pool's fetch at depth 6 | after this commit | about 0.66 GB |

This is under the round's 2 GB.

## 9. After this commit

The lane runs, with this committed file:

1. `fetch --dl <new dir> --depth 6`;
2. `build --dl <that dir> --out <the lane's pool directory>`;
3. `check --out <the lane's pool directory>`.

Nothing of the pool is committed by this lane. The next round's (x) lane copies it, runs the recount, computes M9's
and M10's predictions with Q142(p)'s frozen predictor, marks the tiles predicted over 82 W, and commits all of it in
one commit before any claim.

## 10. Amendments

None yet. A change to the generator or to a rule here goes in a new dated file in this directory, committed before
the tiles it governs. The file names what it changes and why.
