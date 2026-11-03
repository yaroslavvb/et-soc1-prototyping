# Blind pool 5: corrections after verification

*A dated note: Mon 2 Nov 2026 (week 45), Q138(b)'s fix pass after the pool's independent verification, which found that
the pool holds, with fixes (one major fault, three minor). **No frozen file changed.** The 56 files Q138(x) copied in at
19:27 PST are byte-identical: [`README.md`](README.md), [`blind5.json`](blind5.json) (sha256 `946f8493…`), the tiles,
`real/`, both scripts and [`SHA256SUMS`](SHA256SUMS) (sha256 `ccfab045…`). So the tiles, their hashes, the bench's
counts and the frozen predictions all stand. Where the README disagrees with this note, this note governs. Like the
pool, it answers item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "A power model across
kinds". The checks are in [`corrections-check.py`](corrections-check.py), which writes
[`corrections-check.json`](corrections-check.json) and [`corrections-check.txt`](corrections-check.txt).*

## Results

| | the frozen README says | corrected |
|---|---|---|
| **C1** (major) | fp16's C is emulated with PRM 9.4's pseudo-code: a two-term update is dropped unless all four halves are nonzero. So `fp16.sparse24_straddled` drops all 4,096 updates an op, and its C never moves (0 → 0 flips) | The card adds the plain sum (E36). Under that rule straddled's C flips **48,600 → 10,350** bits an op, with nothing dropped. `fp16.real_pythia_softmax_v` reads **36,847 → 7,280**, not 35,340 → 7,099. The other nine fp16 tiles are unchanged. **Pool 5 does not test the PRM-literal drop** |
| **C2** | the post-hoc C-flip correlation on blind pool 4 is r 0.53 (primary arm) and 0.63 (dips removed) | Those are the launch-end descriptor's values, chosen after both descriptors were computed. The start descriptor gives 0.455 and 0.565. The 95% intervals are wide: [0.168, 0.764] for the primary arm's 0.528 |
| **C3** | the Independence list ends "and nothing else" | It left out some reads. None is of M7, Q138(m)'s lane or M6's model code, so independence holds. They are listed below |
| **C4** | `run_checks.decodes_back: true` on all 36 tiles | It is n/a for the four tiles built from words |

## C1. fp16's two-term update: the card adds the plain sum

**The fault.** The pool's C check emulates PRM 9.4's pseudo-code: the update a1·b1 + a2·b2 applies only when a1, a2, b1
and b2 are all nonzero. This is the README's § "The C check", step 2, and `make_blind5.py` lines 486 and 500-501. The lab
already knew that the chip does not follow that rule.

**The evidence.** E36's LAT-S1 registered *fp16 pair result "math" at 50% and 100%*. It passed on aifoundry1 card 1,
aifoundry2 and aifoundry3, three kept passes each. Every pass reads `fp16_pair_result {"0.0": "both", "0.5": "math",
"1.0": "math"}`. Sources:
- [`lat.json`](../../../../docs/reports/data/2026-09-25-claims-v3/results/lat.json) `items[7]`;
- [05-claims](../../../../docs/findings/05-claims.md), the row "Tensor cycles per op in the sparsity kernels";
- the [Q130 RTL-formats README](../../../../docs/reports/data/2026-10-31-q130-rtl-formats/README.md) § 2: "The fp16
  two-term rule, as the PRM writes it, is not what the chip computes".

E36's host zeroes one element of a fraction of A's (2k, 2k+1) pairs (`workloads/sparsity/host/main.cpp`, the `pair`
pattern), so the rule was tested on A's half-zero words. `sparse24_straddled` puts its zeros on B. That the rule holds
there too follows from the update's symmetry; it was not tested directly. A `--values file:` run checks no arithmetic
(`../README.md` 1.5), so E141-E143 will not test it either.

**The corrected descriptors.** `corrections-check.py` reruns `make_blind5.c_check` unchanged on all 36 tiles, and every
one is identical to `blind5.json`. It then reruns the check with every fp16 update applied. The two rules can differ
only where an update is dropped although its sum is nonzero, which takes a word with exactly one zero half. Two
tiles have such words:

| tile | half-zero words (A / B) | as frozen (PRM-literal) | under the card's rule (E36) |
|---|---:|---|---|
| `fp16.sparse24_straddled` | 0 / 256 | 4,096 updates dropped an op; C flips 0 → 0; 0% of updates change C | 0 dropped; C flips **48,600 → 10,350**; 100% of updates change C (85.4% at the launch end) |
| `fp16.real_pythia_softmax_v` | 8 / 0 | 1,024 dropped (128 of them with a nonzero sum); 35,340 → 7,099; 75.0% | 0 dropped; **36,847 → 7,280**; 78.1% (66.7% at the end) |

C flips are bits an op: the start (a launch's second op) → the README's launch-end estimate. They are the desk's
emulation, a descriptor, not a measurement.

Three more tiles drop updates under the PRM-literal rule: `fp16.anchor_zeros` (4,096 an op), `fp16.wideexp_bgate_alt`
and `fp16.sparse24_aligned` (2,048 each). Every update they drop sums to zero (a whole zero word), so their C is the
same under both rules. The other six fp16 tiles drop nothing. Under the card's rule every fp16 tile still passes the C
check: the operands are finite, and C stays finite over the first 64 exact ops and at the launch-end estimate. The
bound over 2^21 ops sums every update's |products|, so it is the same under both rules.

**What it changes.**
- **`fp16.sparse24_straddled` is 2:4 at 50% element sparsity with nothing gated.** No B word is zero, and on the card
  each update adds its one nonzero product (PRM's pseudo-code would drop it). It is not a quiet-C tile.
- **With `fp16.sparse24_aligned` it tests ungated against gated 2:4 at equal element sparsity**, the gate-state term.
  Its C is busier too: 48,600 flips an op at the start, against aligned's 25,965. So this pair alone cannot separate a C
  term from the gate term.
- **The README's terms table.** The row "fp16's two-term rule | the cancel pair, the straddled 2:4 tile" now reads
  "fp16 exact against near cancel, C quiet against C busy at matched operand activity | `pair_cancel_asign`,
  `pair_nearcancel`". The 2:4 pair belongs to the gate-state row.
- **§ "A post-hoc observation".** The contrast "straddled against aligned 2:4" is a gate-state contrast with the busier C
  on the ungated tile, not a C-only contrast.
- **A C-term arm.** Any C-term arm that E141-E143 register must take fp16's C under the card's rule. The full record is
  `corrections-check.json` › `fp16_rule.tiles.<name>.math_c_check`, and its summary is `math_the_card`.
- **Untouched:** the tiles, their hashes, the bench's counts, and M5's, M6's and M7's frozen predictions. No model reads
  `c_check`: the verification found that M7's `predict_blind5.py` reads only the name, type, file, sha256, priority and
  case. Blind pool 4's seven fp16 tiles keep the same C flips under the card's rule, so C2's numbers are unchanged.

## C2. The post-hoc correlation: both descriptors, with intervals

The README's table (§ "A post-hoc observation the pool can test") shows only the launch-end descriptor. The designer
computed both descriptors in one script, and the end one went into the README after both were seen. Here are both,
recomputed by `corrections-check.py`:
- from blind pool 4's committed tiles;
- against E140's published residuals ([`scored.json`](../../../../docs/reports/data/2026-11-02-e140-blind4/scored.json),
  [`scored-nodips.json`](../../../../docs/reports/data/2026-11-02-e140-blind4/scored-nodips.json), `primary.power.rows`,
  error = measured − predicted, W);
- with Fisher-z 95% intervals (n 25).

| arm | C flips an op | r [95%] | Spearman ρ | r fp32 / fp16 / int8 | within-format r² | r without the two Inf tiles [95%] (n 23) |
|---|---|---|---:|---|---:|---|
| primary | launch end (the README's) | 0.528 [0.168, 0.764] | 0.493 | 0.609 / 0.456 / 0.656 | 0.337 | 0.503 [0.114, 0.758] |
| primary | start | 0.455 [0.073, 0.720] | 0.578 | 0.584 / 0.413 / 0.715 | 0.260 | 0.407 [−0.007, 0.701] |
| dips removed | launch end (the README's) | 0.632 [0.315, 0.822] | 0.525 | 0.797 / 0.522 / 0.644 | 0.412 | 0.608 [0.261, 0.816] |
| dips removed | start | 0.565 [0.219, 0.785] | 0.648 | 0.820 / 0.479 / 0.719 | 0.360 | 0.503 [0.114, 0.758] |

The two Inf tiles are blind 4's `fp32.wideexp_bgate_alt` and `fp32.wideexp_agate_rows`. Their C sits at ±Inf from the
first op in 109 and 133 of the 256 elements, with no NaN (reproduced here). Every number is the same under the card's fp16
rule. The correlation stays **post hoc, on one session's 25 tiles, with a derived descriptor, and it decides nothing**. A
C-term arm on pool 5 must be registered before any of E141-E143's data, must name its descriptor, and must take fp16's
C as C1 says.

## C3. Independence: the reads the list left out

The README's § "Independence" ends "and nothing else". The designer's tool-call record, checked in the verification,
shows reads that the list leaves out. None is of M7, Q138(m)'s lane or M6's model code, so the pool's independence
holds; the list was incomplete. The missing reads:
- **Greps of three files:** `tools/claims-v3/lib.sh` and `kinds/block_e78.sh`, for the launch's iteration count, and
  `workloads/sparsity/sparsity_args.h`.
- **Blind 4's files:** its `SHA256SUMS` (the first 40 lines), `blind4.json` and all 25 of its tiles. They were read for
  the C check of blind 4 (the Inf finding and C2).
- **E140's tool directory, `tools/claims-v3/e140/`:**
  - a listing;
  - a grep of its `.md`, `.py` and `.sh` files for NaN, Inf and read-back words. Among the rest it searched M6's
    `m6_inputs.py` and `make_predictions_e140.py`, and it printed one line, from `score_e140.py`;
  - a grep of `run_e140.py` and `e140_common.py` for definitions and hash checks;
  - a `grep -l` over E140's data directory, and a grep of its `logs/`, which printed only file names.
- **A `git grep`** for NaN and read-back words over `tools/claims-v3` and `docs/reports/data/2026-11-0*`. Its pathspec
  excluded Q138(m)'s directories. It printed 20 lines, from other experiments' data files (E97, E104, E116, E118 and
  Q132's RTL bench) and from three tool files, none of them a model's.
- **A `grep -l`** for `tensor_error` over `external/core-et/rtl`, which printed four file names.
- **A HEAD request** to huggingface.co, a reachability probe that fetched no data.

So the README's "No M6 model code was opened either" should read: *no line of M6's model code was read; one grep
searched `m6_inputs.py` and `make_predictions_e140.py` and printed nothing from them.*

**Public text.** The designer's own check was one pattern grep over four of the six text files. The verification ran
three checks over all six: the FORBIDDEN list of the lab's `tools/timeline/sanitize_extracts.py`, extra patterns, and a
proper-noun pass. All six were clean. The only hits were a loop variable's name in the generator's directory walk.

## C4. `run_checks.decodes_back` on the four tiles built from words

`make_blind5.py` (line 621) writes `decodes_back: true` for every tile. But `build_one` decodes and compares (lines
593-595) only the 32 tiles built from elements with `make_kinds.encode`. Four tiles are built from bit patterns with
`make_kinds.from_words` and return at line 589, before that check: `fp32.gray_stream`, `fp16.wideexp_bgate_alt`,
`fp16.exp_only` and `int8.gray_a`. They have no element list to decode back to, so read `decodes_back` as **n/a
(defined on words)** for them. Their sha256 fixes their bytes, and the verification checked each one's rule on its
bits.

## What this does to predicting power and heat

It measures nothing, and item 6's test set is unchanged: the same 36 tiles, hashes and frozen predictions.
- **Before**, M6 on blind pool 4 (E140):
  - power 0.41 W rms on the floats and 0.38 W on int8, biased −0.28 W, with 19 of 25 tiles inside its band;
  - heat 0.20 / 0.16 °C, with 24 of 25 inside;
  - M5 0.36 W over all 25.
- **After:** the blind error E141-E143 measure on pool 5.

What changes is which terms the pool tests, and one input a result-path term would use:
- **The fp16 PRM-literal drop is not tested**: E36 settled it. In its place the pool tests ungated against gated 2:4 at
  equal element sparsity (the gate-state term), and exact against near cancel (C quiet against C busy at matched
  operand activity).
- **A C-register term, if one is registered, takes fp16's C under the card's rule.** For straddled that is 48,600 flips an
  op at the start, not 0.
- **The term's post-hoc support is weak, and it is to be tested, not assumed.** On the primary arm it is r 0.528 [0.168,
  0.764] with the end descriptor and 0.455 [0.073, 0.720] with the start descriptor.

## Files

| file | what |
|---|---|
| `CORRECTIONS.md` | this note |
| `corrections-check.py` | the checks (numpy only; reads this pool, `../blind4/` and E140's scored files, and writes the two files below) |
| `corrections-check.json` | for each fp16 tile, its C check under both rules (`math_c_check` is the card's); blind 4's C flips under both rules; every correlation; the tiles built from words |
| `corrections-check.txt` | its printout |

```bash
python3 -B tools/claims-v3/kinds/blind5/corrections-check.py     # numpy; about 15 s on the Intel; exit 0 = every check holds
```

These four files sit beside the frozen pool, as Q138(x)'s counts and predictions do. `shasum -a 256 -c SHA256SUMS`, run
from this directory, still passes 55 of 55. `make_blind5.py --check` sums every file in this directory, so since Q138(x)'s
additions it reports one mismatch, on `SHA256SUMS`. The 37 files it builds still compare equal.
