# From matmul speed to one transistor switch (Q128, 27 October 2026)

The page [`docs/reports/2026-10-27-matmul-to-transistor.html`](../../2026-10-27-matmul-to-transistor.html),
which joins nine steps — TFLOPS, the governor, board watts, picojoules per multiply-add, femtojoules per
flipped operand bit, net toggles, gate and wire capacitance, one transistor's gate, electrons and Landauer's
floor — into one chain, and shows what the chain does **not** account for.

## This directory produces nothing of its own

Every number on the page is read at build time out of a data directory that a scored experiment wrote. No
value is typed into the page, the script or this directory, so the page cannot drift from the record: if a
later correction changes a committed JSON, a rebuild changes the page.

    scripts/build-report.py matmul-to-transistor \
      docs/reports/data/2026-10-27-matmul-to-transistor/data.json \
      docs/reports/2026-10-27-matmul-to-transistor.html

`build_data.py <repo root> <out.json>` regenerates `data.json`. Its inputs:

| Block | Read from |
|---|---|
| `speed` `governor` `board` `closure` | [`2026-10-27-chain-closure/chain.json`](../2026-10-27-chain-closure/README.md) — itself built from E64, E60, E65 and E67 |
| `permac` | the same, whose E38 figures are read at run time from the sparsity page's own registered data block |
| `perbit` | `chain.json`'s price lists (E65's B side, E67's A side) and `saturation` rungs (E60) |
| `rail` `toggles` `gates` `transistor` `floor` `waterfall` | [`2026-10-27-transistor-ledger/transistor-ledger.json`](../2026-10-27-transistor-ledger/README.md) |

Two figures on the page are not in either JSON and are written in `build_data.py` as literals with their
source named in the code: E68's price band `117.5–135.9 fJ`
([`2026-10-27-e68-stage-map/leak-sensitivity.txt`](../2026-10-27-e68-stage-map/leak-sensitivity.txt), the
`sm_lo12` row at the registered 1.508 W/°C slope and at E66's measured 0.296 W/°C), and the bottom-up burst
range `1.06–1.19` (chain-closure's own open item). If either moves, change it here.

## Two deliberate choices

- **The sustained gap is quoted in clocks, not TFLOPS.** Zeros holds 800 MHz and random data sits on the
  governor's 600 MHz floor, so the ratio is exactly 4/3. E64's published 9.2 TFLOPS is 12.3 × 600/800 =
  9.225 rounded, and 12.3/9.2 would read 34%. The page says 33% and says why.
- **The floor's rungs are renamed to short keys here** (`mac_board`, `bit_netlist`, `transistor`, …), each
  carrying its long name as a `label`. A wording change upstream then breaks the build loudly instead of
  silently emptying a number on the page.

## The optional `vault` block

The page's script renders an extra set of boxes when its data carries a `vault` key, and nothing at all when
it does not. **Nothing in this repository writes that key**, `build_data.py` cannot produce it, and the
`data.json` committed here has none. It exists so that a private build of the same page, from the same source
files, can carry a cross-check that is not public.

## What the page says is still open

In the order that closing them would most change it: the governor's cap has never actually been moved (the
knob test); the single-bit price list over-predicts a whole random word by about 2×, and the ladder in the
*number* of simultaneously flipping positions that would settle it is built and unrun; the leakage slope used
to correct each run moves every per-bit price by 15%, which is why the page quotes a band; detailed routing
never closed in the open flow, so the wire share is a floor and the transistor share a ceiling; and half the
design's capacitance is unpriced.
