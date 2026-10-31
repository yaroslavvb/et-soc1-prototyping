# Q130(s) — the kinds of numbers: spec, generator and tiles (data record)

Sat 31 Oct 2026 (week 44). Desk compute only: **no card was opened, nothing was measured in watts.** Every
number from this lane is a design-time count or a design-time expectation derived from committed operand
tiles.

**The artefact lives in the tool tree, not here:** [`tools/claims-v3/kinds/`](../../../../tools/claims-v3/kinds/)
— `README.md` (the spec and the kinds tables), `make_kinds.py` (the generator and the statistics, in one
file), `kinds.json` (the frozen spec and per-tile statistics, 51 kinds) and `tiles/<type>/<kind>.bin` (51
files of 2,048 bytes: the A tile then the B tile, 1,024 each, in that type's layout). This directory exists so
the work has a row in the lab's own data records; it holds no raw data of its own, because there is none.

## What it is

51 operand tile pairs — 18 fp32, 17 fp16, 16 int8 — one per *kind of number*, generated, characterised
bit by bit and checked. They are the input E78 (the energy matrix, aifoundry3), E80 (speed under the governor,
aifoundry2), Q130(b) (RTL toggle counts) and Q130(c) (the empirical model) run on.

Run one on a card or in the bench:

```bash
sparsity_host --test fma --type fp32 --values file:tools/claims-v3/kinds/tiles/fp32/randn_sorted.bin
python3 rtl-sim/fma_toggle/tiles.py x out.hex --from-bin tools/claims-v3/kinds/tiles/fp32/randn_sorted.bin
```

Reproduce the whole set (numpy only, about a minute; `--replicates 0` gives the tiles alone in 4 s):

```bash
python3 tools/claims-v3/kinds/make_kinds.py tools/claims-v3/kinds --check
```

## What it says, before any card runs

- **The zero gate is at least a whole 32-bit word wide, and in int8 two words wide** (the column pair `l`,
  `l+8` — eight bytes). So the same 50%-element-sparsity rule gates an expected 75.0% of column-slot-cycles
  in fp32, 43.7% in fp16 and only 6.7% in int8. The narrower the format, the less of your sparsity the
  hardware can see.
- **int8 does not use the same operand stream as fp32 and fp16.** It runs on TIMA, does all sixteen B columns
  in one micro-op, and takes 256 micro-ops an op, not 512 — which is what its measured 318 cycles an op
  (E36/E39) requires. Its A word changes every cycle and its B line is held sixteen, the opposite of fp32.
- **Ordering for the hardware's stream is cheaper; sorting the numbers is not.** The same operand multiset,
  permuted into the stream order of least change, flips 0.74 / 0.73 / 0.77 of the base count. A naive value
  sort of the same data gets 1.025 in fp32 — *worse* than not sorting.
- **Narrowing integer range buys nothing.** int4-range values in int8 bytes flip the same number of operand
  bits as full-range int8 (ratio 1.000 over 400 draws of each rule), because two's-complement sign extension
  turns one sign change into five bit flips. Narrowing *precision* inside a wide format does work: bf16
  precision in an fp32 word cuts operand flips 2.35x.

Each of those is sourced to a file and a key in `tools/claims-v3/kinds/README.md`.

## Revisions

- **Revision 1** — the first commit of the spec, generator and tiles.
- **Revision 2**, the same day, after a verification pass: int8's stream and gate re-derived from the RTL
  (every int8 figure changed, and the A/B asymmetry inverted), the int8 ordered tile regenerated against the
  corrected stream, the two value-sort baselines committed, a sampling band added for every random kind, and
  the tier counts corrected to 30 tier 1 / 21 tier 2. `tools/claims-v3/kinds/README.md` section 6 lists all
  eight corrections with their sources. **int8 figures from revision 1 must not be quoted.** 50 of the 51
  tiles are byte-identical across the two revisions.

## What is still open

- Nothing here is a watt. E78 and E80 must confirm that operand bit flips predict switching power before any
  of this is quoted as energy.
- The int8 `hamming` and `bus_bits_per_op` figures rest on a reconstruction of the TIMA stream (256
  micro-ops, 16 column slots) and on the convention that the broadcast A word is counted once per column
  slot. Both are flagged `provisional` per kind in `kinds.json`. The int8 **gated** figures are not
  provisional: they follow from the gate rule alone.
- int8 has no pair-granular sparsity kind, so no committed int8 kind gates half of its lanes.
- An int8 tile must not be replayed in `rtl-sim/fma_toggle` for gate or bus counts: that bench is the txfma
  unit, which is neither int8's stream nor int8's gate.
